"""news_process.pipeline.preprocess.dedup — 去重层 (精确 + MinHash LSH 近似).

Phase 4b 从 ``runner.py`` 提取。包含:
- ``ArticleDeduplicator`` — 精确去重 + MinHash LSH 近似去重的封装类

依赖: 仅 ``_constants.py`` (logger / nb_workers); 类自身通过 ``config`` /
``logger_instance`` 构造参数注入运行期上下文, 无 sibling 模块依赖。
"""

from __future__ import annotations

import json
import multiprocessing
import os
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
         在重复组内, 按日期升序 (保留首发)、媒体权重降序 (同日 tiebreak)、
         docid 升序保留首条 (fix omni-g-preprocess-06, 与近似去重口径对齐)。

      ② 近似去重:
         - 对每篇文章计算 MinHash 签名(128 个置换), 使用字符级 3-gram 作为特征。
         - 构建 LSH 索引(阈值 = Jaccard ≥ 0.8), O(1) 查询近似重复簇。
           注: Jaccard ≥ 0.8 具备双重文献支持:
           1) English Lit: 相似度 > 0.8 常用作剔除冗余信息的安全学术门槛。
           2) Chinese Lit: 中文金融文本去重文献普遍以相似度 ≥ 0.8 作为极高相似度基准,
                            有效过滤通稿 / 转载。
           ⚠ LSH banding 有效阈值披露 (datasketch==1.10.0, MinHashLSH 默认 FP/FN 权重
              (0.5,0.5), num_perm=128, threshold=0.8): datasketch 自动分带为 b=9 带 ×
              r=13 行 (仅用 117/128 个排列), 故 "0.8" 是【概率性近似阈值】非硬阈值 ——
              有效 50%-检出阈值 ≈ 0.819, 对真 Jaccard=0.80 单对检出概率仅 ≈ 0.40, 检出
              10%→90% 散布在真 Jaccard∈[0.71, 0.89]。含义: 去重偏保守 (偏向漏删轻度改写
              的转载, 而非误删独立文章); 换 datasketch 版本/权重会使上述数字漂移。
         - 在每个重复簇内, 按日期排序, 5 个工作日 (busday) 内的后发文章标记为重复。
           注: "5 个工作日" 按发文星期不同, 实际覆盖发文日起 7~9 个自然日 (工作日发文最多
           7 天; 周末发文跨两个完整周末最多 9 天, numpy 默认周一至周五 weekmask)。
         - ⚠ 删除前做 pairwise 真 Jaccard 复核 (fix N4, 见 find_near_duplicate_indices):
           LSH 簇仅作【候选】, 簇内成员仅当其与触发它的已保留文的真实 char-3gram Jaccard
           ≥ threshold 时才删 —— 防止 banding 传递连边把真 J<threshold 的成员误删 (该误删
           亦是去重对输入集合非幂等的根源)。

    复杂度分析:
      - 精确去重: O(n log n) (排序) + O(n) (去重) = O(n log n)
      - 近似去重: O(n) (MinHash 生成, 并行化) + O(n) (LSH 插入+查询)
      - 总体空间: O(n) (MinHash 签名 + LSH 索引)

    Attributes:
        COL_WEIGHT:   媒体权重临时列名。
        COL_LENGTH:   内容长度临时列名。
        COL_COMBINED: 标题+内容合并临时列名。

    白话:
        先删一字不差的完全重复 (保留最早发的那篇); 再给每篇文章算一个
        "文本指纹" (MinHash), 哪怕改了几个字指纹也几乎一样, 借此快速找出
        转载/通稿簇 — 簇内 5 个工作日内后发的相似稿被判为重复删除,
        间隔更久的 (如周年回顾) 保留。

    下游口径注意 (对银行关注度指标的影响, 顶刊依据见
    panel/attention_media.py::compute_attention_treatments docstring):
        去重基适配 "信息到达" 构念 (Tetlock 2011 RFS; Hassan et al. 2019 QJE) —
        attention_index/pct/density 等关注度指标消费本层输出 ✓; "保留首发" 排序键
        防止跨期转载错配 bank-year 年度归属。
        ⚠ 更正 (2026-06-13 审核): 此前注释称 "传播广度" 构念由
        falsification/controls.py::nf_media_breadth 用【去重前物理行集】另算 —— 该函数
        【不存在】; 现行 media_breadth (panel/encode.py, groupby nunique '媒体(中文)') 实际
        算在【去重后】面板上 (controls.py 的 _df_full_physical 仅是该模块自身复合键折叠前,
        非 stage-00 去重前)。如需真正 "去重前" 口径的传播广度/outlet 构成对照 (Bushee 2010
        JAR; Fang & Peress 2009 JF), 去重前语料经 validation/dedup_threshold.py::
        _load_pre_dedup_corpus 从 _cache/*.parquet 重建 (normalize+filter 后、去重前; 含全部
        非银行新闻, 用前须重放银行/长度过滤)。
    """

    COL_WEIGHT = 'temp_media_weight'
    COL_LENGTH = 'temp_content_length'
    COL_COMBINED = 'temp_title_content'
    COL_DATETIME = 'temp_datetime'
    # fix(omni-g-preprocess-06, 2026-06-11): 精确去重排序键加日期为第一键
    # (升序, NaT 排末) — 与近似去重 '保留首发源' 原则对齐; 媒体权重降级为
    # 同日 tiebreak。旧序 [权重↓, docid↑, 长度↓] 完全不看日期, 跨年转载时
    # 保留高权重副本的日期 → bank-year 面板年度归属错位。
    SORT_BY_COLS = [COL_DATETIME, COL_WEIGHT, 'docid', COL_LENGTH]
    SORT_ASCENDING = [True, False, True, False]

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
        # 生产默认阈值 = 0.8 (config/preprocessing.yaml: jaccard_similarity_threshold)。
        # fix(N4-audit, 2026-06-13): 下方 fallback 默认值由 0.85 统一为 0.80 = 生产值。
        # 仅 config 缺 'jaccard_similarity_threshold' 键时命中; 当前 5 个构造点传入的 config
        # 均含该键, 故 fallback 不可达, 改此值对所有现有产物零影响 —— 目的是消除 "代码默认值 (0.85) ≠
        # 生产值 (0.80)" 的复现性陷阱 (他人无 config 复现时不再静默用更松的 0.85)。
        # 文献支持: 相似度 ≥ 0.8 是中文金融文本去重文献普遍采用的去重门槛。
        self.threshold = self.params.get('jaccard_similarity_threshold', 0.80)
        self.ngram_size = self.params.get('ngram_size', 3)

        # 参数边界校验
        if not (0 < self.threshold < 1):
            self.logger.warning(
                f"jaccard_similarity_threshold={self.threshold} 超出合理范围 (0, 1), "
                f"已回退到默认值 0.80。"
                f"(threshold=0 会将所有文档视为重复, threshold=1 不去除任何重复)"
            )
            self.threshold = 0.80

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

    def _log_media_weight_coverage(self, media_names: pd.Series,
                                   mapped_weight: pd.Series) -> None:
        """媒体权重覆盖率日志 (匹配行占比 + 高频未匹配名单).

        fix(omni-g-preprocess-06, 2026-06-11): 旧实现未匹配媒体静默回退默认权重
        (盘上实测 ~24% 行无覆盖率日志), 未覆盖媒体间的精确去重保留退化为 docid
        序而无任何可见性。覆盖率 payload 暂存于 ``self.weight_coverage_``,
        sidecar 落盘由 ``_write_weight_coverage_sidecar()`` 在 ``run()`` 中执行
        (validation 阶段直接调本方法复用时不会覆写 stage 00 的 sidecar)。
        """
        self.weight_coverage_ = None
        total = len(media_names)
        if total == 0:
            return
        unmatched_mask = mapped_weight.isna()
        n_matched = int((~unmatched_mask).sum())
        coverage = n_matched / total
        self.logger.info(
            f"媒体权重覆盖率: {n_matched:,}/{total:,} 行 ({coverage:.1%}) 命中 "
            f"media_weights.json; 未匹配行回退默认权重 {self.default_weight}"
        )
        if not bool(unmatched_mask.any()):
            return
        unmatched_counts = media_names[unmatched_mask].astype(str).value_counts()
        self.logger.warning(
            f"未匹配媒体 {len(unmatched_counts)} 个 "
            f"({int(unmatched_mask.sum()):,} 行回退默认权重), "
            f"高频未匹配: {unmatched_counts.head(10).to_dict()}"
        )
        self.weight_coverage_ = {
            'total_rows': int(total),
            'matched_rows': n_matched,
            'coverage': round(coverage, 4),
            'default_weight': int(self.default_weight),
            'unmatched_media': {
                str(k): int(v) for k, v in unmatched_counts.items()
            },
        }

    def _write_weight_coverage_sidecar(self) -> None:
        """把未匹配媒体清单落 sidecar (``<output_dir>/media_weight_coverage.json``).

        fix(omni-g-preprocess-06, 2026-06-11): 仅在存在未匹配媒体时写盘;
        写盘失败仅 warning (fail-soft, 不阻断去重主流程)。
        """
        payload = getattr(self, 'weight_coverage_', None)
        if not payload:
            return
        try:
            out_dir = self.paths.get('output_dir', '')
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
                sidecar = os.path.join(out_dir, 'media_weight_coverage.json')
                with open(sidecar, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                self.logger.info(f"未匹配媒体清单已落盘: {sidecar}")
        except Exception as e:
            self.logger.warning(f"media_weight_coverage.json 写入失败: {e}")

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加去重所需的辅助列 (媒体权重、内容长度、合并文本、日期)."""
        self.logger.info("添加辅助列...")
        media_weight = pd.to_numeric(
            df['媒体(中文)'].map(self.media_weights),
            errors='coerce',
        )
        # fix(omni-g-preprocess-06, 2026-06-11): 权重覆盖率显式化 (日志 + sidecar)
        self._log_media_weight_coverage(df['媒体(中文)'], media_weight)
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
        """精确去重: 基于标题+内容完全匹配, 保留首发 (最早日期) 副本.

        fix(omni-g-preprocess-06, 2026-06-11): 排序键改为 [日期↑, 权重↓, docid↑,
        长度↓] (NaT 日期排末) — 媒体权重仅作同日 tiebreak, 与近似去重 '保留
        首发源' 口径一致; 旧实现保留最高权重副本, 跨年转载导致年度归属错位。
        """
        self.logger.info("执行精确去重...")
        pre_count = len(df)
        df_sorted = df.sort_values(
            by=self.SORT_BY_COLS, ascending=self.SORT_ASCENDING,
            na_position='last',  # NaT 日期副本排末: 有效日期副本优先保留
        )
        df_deduped = df_sorted.drop_duplicates(subset=[self.COL_COMBINED], keep='first')
        removed = pre_count - len(df_deduped)
        self.logger.info(
            f"精确去重完成: 移除 {removed:,} 条, 剩余 {len(df_deduped):,}"
        )
        return df_deduped

    def compute_minhashes(self, df: pd.DataFrame) -> pd.Series:
        """Step 1: 并行生成 MinHash 签名 (索引 → MinHash 的 Series).

        签名只依赖文本与 (num_perm, ngram_size), **不依赖** Jaccard 阈值/时间窗口
        — 因此去重敏感性检验 (panel/dedup_sensitivity.py) 可对同一批签名按
        多组 (threshold, window) 反复判重而无需重算签名。
        前置: df 须已经 ``_prepare_dataframe`` (依赖 COL_COMBINED 列)。
        """
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

        return pd.Series(minhash_results)

    def find_near_duplicate_indices(
        self, df: pd.DataFrame, minhashes: pd.Series,
        threshold: float = None, window_busdays: int = 5,
    ) -> Set:
        """Steps 2-3: 按 (threshold, window_busdays) 判近似重复, 返回应剔除的索引集.

        生产默认 = (self.threshold, 5 工作日); 去重敏感性检验传入备选参数网格。
        前置: df 须已经 ``_prepare_dataframe`` (依赖 temp_datetime / COL_WEIGHT /
        docid 列做簇内排序)。

        fix(N4, 2026-06-13): 簇内删除前加 pairwise 真 Jaccard 复核 —— LSH 簇仅作
        【候选】(banding 在 J=0.80 处召回率仅 ~0.40 且可经传递连边把真 J<threshold 的
        成员拉进同簇), 某成员仅当其与触发它的已保留文的真实 char-3gram Jaccard ≥ threshold
        时才删。消除 sub-threshold 过删 (及由此引发的去重对输入集合非幂等); 不影响真转载
        (真 J≥threshold) 的正常剔除。
        """
        if threshold is None:
            threshold = self.threshold
        if minhashes.empty:
            self.logger.warning("无有效 MinHash, 跳过近似去重")
            return set()

        # fix(N4): pairwise 真 Jaccard 复核所需的 token 缓存 (按 index 惰性物化, 复用)
        _tok_cache: Dict[Any, Set[str]] = {}

        def _toks(i):
            t = _tok_cache.get(i)
            if t is None:
                t = self._clean_and_tokenize(str(df.loc[i, self.COL_COMBINED]))
                _tok_cache[i] = t
            return t

        def _true_jaccard(i: Any, j: Any) -> float:
            a, b = _toks(i), _toks(j)
            u = a | b
            return (len(a & b) / len(u)) if u else 0.0

        # ── Step 2: 构建 LSH 索引 ──
        self.logger.info(
            f"构建 LSH 索引({len(minhashes):,} 个文档, "
            f"threshold={threshold}, window={window_busdays} 工作日)..."
        )
        lsh = MinHashLSH(threshold=threshold, num_perm=self.num_perm)
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

            # 时间窗口去重: window_busdays 个工作日内的后发相似文章视为重复
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
                        within_window = 0 <= np.busday_count(d1, d2) <= window_busdays
                    except Exception:
                        within_window = False
                    if not within_window:
                        continue
                    # fix(N4, 2026-06-13): LSH 簇是【候选】非等价类; 删除前复核被删文与触发
                    # 它的已保留文的【真实 char-3gram Jaccard】≥ threshold 才删, 否则继续看
                    # 其它已保留文。防止 banding 传递连边把真 J<threshold 的成员误删。
                    if _true_jaccard(current_idx, kept_idx) >= threshold:
                        is_redundant = True
                        break

                if is_redundant:
                    all_indices_to_drop.add(current_idx)
                else:
                    kept_articles.append((current_idx, current_date))

        self.logger.info(
            f"近似去重完成: 找到 {len(all_indices_to_drop):,} 条近似重复"
        )
        return all_indices_to_drop

    def _perform_near_deduplication(self, df: pd.DataFrame) -> pd.DataFrame:
        """近似去重: MinHash LSH + 5 个工作日时间窗口 (生产口径).

        重构 (2026-06-13, 去重敏感性): 拆为 compute_minhashes (签名, 参数无关) +
        find_near_duplicate_indices (判重, 参数化) 两个可复用方法, 本方法以生产
        默认参数 (self.threshold, window=5) 串联二者。⚠ 注: find_near_duplicate_indices
        已含 N4 pairwise 真 Jaccard 复核 (2026-06-13), 故对 sub-threshold 边界簇成员的
        行为与该复核引入前【不再逐位一致】(刻意的正确性修复, 仅影响真 J<threshold 的罕见
        传递误删); 真转载 (真 J≥threshold) 剔除不变。
        """
        self.logger.info("执行近似去重(LSH + 时间窗口)...")
        minhashes = self.compute_minhashes(df)
        drop = self.find_near_duplicate_indices(df, minhashes)
        return df.drop(index=list(drop)) if drop else df

    @log_and_time(logger)
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行完整去重流程 (精确 + 近似)."""
        if df.empty:
            self.logger.warning("输入为空, 跳过去重")
            return df

        df_prepared = self._prepare_dataframe(df)
        # fix(omni-g-preprocess-06, 2026-06-11): 未匹配媒体清单 sidecar 仅在
        # 主流程 run() 落盘 (validation 复用内部方法时不覆写 stage 00 产物)
        self._write_weight_coverage_sidecar()
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


# 重导出 MinHash, 兼容 `from .dedup import MinHash, MinHashLSH` 的调用方。
# (防御性向后兼容 — 旧版 runner.py 曾在顶层暴露这两个名字。)
_ = MinHash, MinHashLSH


__all__ = ['ArticleDeduplicator']
