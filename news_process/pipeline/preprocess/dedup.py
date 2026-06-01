"""news_process.pipeline.preprocess.dedup — 去重层 (精确 + MinHash LSH 近似).

Phase 4b 从 ``runner.py`` 提取。包含:
- ``ArticleDeduplicator`` — 精确去重 + MinHash LSH 近似去重的封装类

依赖: 仅 ``_constants.py`` (logger / nb_workers); 类自身通过 ``config`` /
``logger_instance`` 构造参数注入运行期上下文, 无 sibling 模块依赖。
"""

from __future__ import annotations

import json
import multiprocessing
import string
import sys
from functools import partial
from typing import Any, Callable, Dict, Set

import numpy as np
import pandas as pd
from datasketch import MinHash, MinHashLSH

from news_process.pipeline.preprocess._constants import logger, nb_workers

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from news_process.core.logging import log_and_time


class ArticleDeduplicator:
    """文章去重器: 精确去重 + 近似去重 (MinHash LSH + 时间窗口).

    算法说明:
      ① 精确去重: 基于 (标题 + 内容) 字符串完全匹配。
         在重复组内, 按媒体权重降序、docid 升序保留首条。

      ② 近似去重:
         - 对每篇文章计算 MinHash 签名(128 个置换), 使用字符级 3-gram 作为特征。
         - 构建 LSH 索引(阈值 = Jaccard ≥ 0.8), O(1) 查询近似重复簇。
           注: Jaccard ≥ 0.8 具备双重文献支持:
           1) English Lit: 相似度 > 0.8 常用作剔除冗余信息的安全学术门槛。
           2) Chinese Lit: 胡俊 (2021) 验证了 0.8 作为金融文本极高相似度的基准,
                            有效过滤通稿 / 转载。
         - 在每个重复簇内, 按日期排序, 5 个工作日内的后发文章标记为重复。

    复杂度分析:
      - 精确去重: O(n log n) (排序) + O(n) (去重) = O(n log n)
      - 近似去重: O(n) (MinHash 生成, 并行化) + O(n) (LSH 插入+查询)
      - 总体空间: O(n) (MinHash 签名 + LSH 索引)

    Attributes:
        COL_WEIGHT:   媒体权重临时列名。
        COL_LENGTH:   内容长度临时列名。
        COL_COMBINED: 标题+内容合并临时列名。
    """

    COL_WEIGHT = 'temp_media_weight'
    COL_LENGTH = 'temp_content_length'
    COL_COMBINED = 'temp_title_content'
    SORT_BY_COLS = [COL_WEIGHT, 'docid', COL_LENGTH]
    SORT_ASCENDING = [False, True, False]

    # 标点和空白字符清洗表: 用于 MinHash 分词前的文本规范化
    PUNCTUATION = (
        string.punctuation
        + "＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～"
        + "｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—''‛"
        + "\"\"„‟…‧﹏."
    )
    WHITESPACE = " \n\t\r\u3000"
    CLEANING_TABLE = str.maketrans('', '', PUNCTUATION + WHITESPACE)

    def __init__(self, config: Dict[str, Any], logger_instance):
        """初始化去重器.

        Args:
            config:          已解析的配置字典。
            logger_instance: 日志记录器实例。
        """
        self.params = config['deduplication']
        self.paths = config['paths']
        self.logger = logger_instance

        self.media_weights = self._load_media_weights()
        self.default_weight = self.media_weights.get("其他媒体", 10)

        self.num_perm = self.params.get('minhash_permutations', 128)
        # 生产默认阈值 = 0.8 (config/preprocessing.yaml: jaccard_similarity_threshold);
        # 下方 0.85 仅是 config 缺失时的保守 fallback, 非生产默认。
        # 文献支持: 相似度 ≥ 0.8/0.85 是学术界 (胡俊 2021 等) 公认的去重与信息冗余剔除标准。
        self.threshold = self.params.get('jaccard_similarity_threshold', 0.85)
        self.ngram_size = self.params.get('ngram_size', 3)

        # 参数边界校验
        if not (0 < self.threshold < 1):
            self.logger.warning(
                f"jaccard_similarity_threshold={self.threshold} 超出合理范围 (0, 1), "
                f"已回退到默认值 0.85。"
                f"(threshold=0 会将所有文档视为重复, threshold=1 不去除任何重复)"
            )
            self.threshold = 0.85

    def _load_media_weights(self) -> Dict[str, int]:
        """从 JSON 文件加载媒体权重评分表."""
        filepath = self.paths['media_weights_file']
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"媒体权重文件未找到: {filepath}")
        except json.JSONDecodeError as e:
            self.logger.error(f"媒体权重文件格式错误: {e}")
        return {}

    def _clean_and_tokenize(self, text: str) -> Set[str]:
        """清洗文本并生成字符级 n-gram 集合作为 MinHash 特征."""
        if not isinstance(text, str) or not text:
            return set()
        cleaned_text = text.translate(self.CLEANING_TABLE)
        n = self.ngram_size
        if len(cleaned_text) < n:
            return {cleaned_text} if cleaned_text else set()
        return {cleaned_text[i:i + n] for i in range(len(cleaned_text) - n + 1)}

    @staticmethod
    def _create_minhash(args, num_perm: int = 128,
                        tokenizer_func: Callable[[str], Set[str]] = None):
        """为单条文本创建 MinHash 签名 (供 multiprocessing.Pool 调用的工作函数)。"""
        idx, text = args
        from datasketch import MinHash as _MinHash
        m = _MinHash(num_perm=num_perm)
        tokens = tokenizer_func(str(text))
        if not tokens:
            return (idx, None)
        # 批量更新替代逐 token 循环, 减少 Python 函数调用开销 (2-3x 加速)
        m.update_batch([t.encode('utf8') for t in tokens])
        return (idx, m)

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加去重所需的辅助列 (媒体权重、内容长度、合并文本、日期)."""
        self.logger.info("添加辅助列...")
        media_weight = pd.to_numeric(
            df['媒体(中文)'].map(self.media_weights),
            errors='coerce',
        )
        df[self.COL_WEIGHT] = media_weight.fillna(self.default_weight).astype(int)
        df[self.COL_LENGTH] = df['内容'].str.len().fillna(0).astype(int)
        df[self.COL_COMBINED] = df['标题'].fillna('') + " " + df['内容'].fillna('')

        # 日期解析(coerce 模式: 无法解析的值设为 NaT)
        df['temp_datetime'] = pd.to_datetime(df['日期'], errors='coerce')
        valid_dates = df['temp_datetime'].notna().sum()
        total_rows = len(df)
        self.logger.info(
            f"日期解析: {valid_dates:,}/{total_rows:,} 有效({valid_dates/total_rows:.1%})"
        )
        if valid_dates < total_rows:
            self.logger.warning(
                f"{total_rows - valid_dates:,} 条日期解析失败, 去重时默认保留"
            )
        return df

    def _perform_exact_deduplication(self, df: pd.DataFrame) -> pd.DataFrame:
        """精确去重: 基于标题+内容完全匹配, 保留媒体权重最高者."""
        self.logger.info("执行精确去重...")
        pre_count = len(df)
        df_sorted = df.sort_values(by=self.SORT_BY_COLS, ascending=self.SORT_ASCENDING)
        df_deduped = df_sorted.drop_duplicates(subset=[self.COL_COMBINED], keep='first')
        removed = pre_count - len(df_deduped)
        self.logger.info(
            f"精确去重完成: 移除 {removed:,} 条, 剩余 {len(df_deduped):,}"
        )
        return df_deduped

    def _perform_near_deduplication(self, df: pd.DataFrame) -> pd.DataFrame:
        """近似去重: MinHash LSH + 5 个工作日时间窗口."""
        self.logger.info("执行近似去重(LSH + 时间窗口)...")

        # ── Step 1: 标准进程池分块并行生成 MinHash 签名 ──
        self.logger.info(
            f"生成 MinHash 签名({self.num_perm} 个置换, "
            f"{nb_workers} 个工作进程)..."
        )
        create_minhash_with_params = partial(
            self._create_minhash,
            num_perm=self.num_perm,
            tokenizer_func=self._clean_and_tokenize
        )

        texts = df[self.COL_COMBINED].tolist()
        indices = df.index.tolist()
        tasks = list(zip(indices, texts))  # (index, text) 元组
        total_count = len(tasks)
        progress_step = max(1, total_count // 10)  # 每 10% 输出一次进度

        minhash_results = {}  # {index: MinHash}
        with multiprocessing.Pool(processes=nb_workers) as pool:
            for i, (idx, mh) in enumerate(pool.imap_unordered(
                create_minhash_with_params,
                tasks,
                chunksize=max(1, total_count // (nb_workers * 4))
            )):
                if mh is not None:
                    minhash_results[idx] = mh
                if (i + 1) % progress_step == 0 or (i + 1) == total_count:
                    pct = (i + 1) / total_count * 100
                    self.logger.info(
                        f"  MinHash 进度: {i + 1:,}/{total_count:,} ({pct:.0f}%)"
                    )

        minhashes = pd.Series(minhash_results)

        if minhashes.empty:
            self.logger.warning("无有效 MinHash, 跳过近似去重")
            return df

        # ── Step 2: 构建 LSH 索引 ──
        self.logger.info(f"构建 LSH 索引({len(minhashes):,} 个文档)...")
        lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        lsh_data = list(minhashes.items())
        insert_errors = 0

        lsh_iterator = (
            tqdm(lsh_data, desc="构建LSH索引", file=sys.stdout)
            if TQDM_AVAILABLE else lsh_data
        )
        for index, m_hash in lsh_iterator:
            try:
                lsh.insert(index, m_hash)
            except ValueError:
                insert_errors += 1
        if insert_errors > 0:
            self.logger.warning(f"LSH 插入跳过 {insert_errors:,} 个重复键")

        # ── Step 3: 查询 LSH 并应用时间窗口规则 ──
        self.logger.info("查询 LSH 索引, 应用时间窗口去重...")
        processed_indices = set()
        all_indices_to_drop = set()
        index_to_minhash = dict(lsh_data)

        iterator = (
            tqdm(df.index, total=len(df), desc="查找重复簇", file=sys.stdout)
            if TQDM_AVAILABLE else df.index
        )

        for idx in iterator:
            if idx in processed_indices:
                continue
            if idx not in index_to_minhash:
                continue

            result_cluster = lsh.query(index_to_minhash[idx])
            processed_indices.update(result_cluster)

            if len(result_cluster) <= 1:
                continue

            # 簇内排序: 日期升序 → 权重降序 → docid 升序
            cluster_df = df.loc[result_cluster]
            sorted_cluster = cluster_df.sort_values(
                by=['temp_datetime', self.COL_WEIGHT, 'docid'],
                ascending=[True, False, True],
                na_position='last'
            )

            # 时间窗口去重: 5 个工作日内的后发相似文章视为重复
            kept_articles = []
            for row in sorted_cluster.itertuples():
                current_idx = row.Index
                current_date = row.temp_datetime
                is_redundant = False

                if pd.isna(current_date):
                    # 日期无效的文章默认保留
                    kept_articles.append((current_idx, current_date))
                    continue

                for kept_idx, kept_date in kept_articles:
                    if pd.isna(kept_date):
                        continue
                    try:
                        d1 = np.datetime64(kept_date, 'D')
                        d2 = np.datetime64(current_date, 'D')
                        if 0 <= np.busday_count(d1, d2) <= 5:
                            is_redundant = True
                            break
                    except Exception:
                        pass

                if is_redundant:
                    all_indices_to_drop.add(current_idx)
                else:
                    kept_articles.append((current_idx, current_date))

        self.logger.info(
            f"近似去重完成: 找到 {len(all_indices_to_drop):,} 条近似重复"
        )
        return df.drop(index=list(all_indices_to_drop)) if all_indices_to_drop else df

    @log_and_time(logger)
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行完整去重流程 (精确 + 近似)."""
        if df.empty:
            self.logger.warning("输入为空, 跳过去重")
            return df

        df_prepared = self._prepare_dataframe(df)
        df_exact = self._perform_exact_deduplication(df_prepared)
        df_near = self._perform_near_deduplication(df_exact)

        # 清理辅助列
        cols_to_drop = [
            self.COL_WEIGHT, self.COL_LENGTH, self.COL_COMBINED, 'temp_datetime'
        ]
        return df_near.drop(
            columns=[c for c in cols_to_drop if c in df_near.columns],
            errors='ignore'
        )


# Re-export MinHash for any caller that does `from .dedup import MinHash, MinHashLSH`.
# (Defensive backwards-compat — the legacy runner.py exposed these top-level.)
_ = MinHash, MinHashLSH


__all__ = ['ArticleDeduplicator']
