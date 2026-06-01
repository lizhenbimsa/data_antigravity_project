"""
news_process.pipeline.sentiment.herd_decay — 跟风/抄袭新闻检测与衰减加权 (双轨版 v3.6.0)
=========================================================================

迁移说明 (Phase 7a-7)：
    本模块由原 root script ``24_herd_decay_processor.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.herd_decay``

v3.6.0 (Plan E P1 B3) 双轨化升级:
    原实现仅对 '内容' 全文做 TF-IDF 相似度判定, 算出单列 herd_weight,
    被下游同时施加到 _full / _ctx 两轨。这是 measurement-treatment
    错配 (Edwards 2001 ORM): 全文相似度 ≠ 对目标银行的报道相似度。
    本版本改为对 '内容' 和 'content_ctx' 分别做 TF-IDF, 输出双轨权重
    herd_weight_full + herd_weight_ctx, 下游按 track 各自施加。

功能:
  对同一 target_bank 在同一时间窗口内的多篇新闻进行文本相似度聚类,
  识别"跟风抄袭"新闻并施加衰减权重, 防止重复计数导致情感指标注水。
  v3.6.0 起按 full / ctx 双轨独立判定。

学术依据:
  - Tetlock (2011, JF): 媒体新闻的信息冗余与重复效应
  - Sautner et al. (2023, JF): 文本相似度驱动的曝光度度量
  - Edwards (2001, ORM): measurement-treatment matching (双轨化动因)

关键设计:
  - TF-IDF 向量化 + 维度封锁 (max_features=10000)
  - pairwise_distances_chunked 分块运算, 峰值内存 < 30GB
  - 相似度阈值 0.35: 高于此值视为"跟风"
  - 衰减公式: weight = 1 / (1 + n_similar_predecessors)
  - **双轨**: full 用 '内容', ctx 用 'content_ctx' (后者由 stage 21 物化)

输入: 23_bert_tone.parquet (含 content_ctx 列, 由 stage 21 物化后下传)
输出: 24_herd_decay.parquet (追加 6 列: 4 双轨列 herd_weight_full + herd_weight_ctx
      + n_similar_articles_full + n_similar_articles_ctx, 外加 herd_weight +
      n_similar_articles 两个单列 —— 后者作为 _full 轨的 NON-BREAKING 别名保留
      (v3.6.0 F-B 修, 见下方主路径), 供 v3.5.x 既有调用方继续读取, 不强制下游显式指定轨道)
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances, pairwise_distances_chunked

# Phase 7a-7: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/herd_decay.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "24_herd_decay_processor"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]

# 跟风检测参数
HERD_CFG = CONFIG.get('herd_detection', {})
SIMILARITY_THRESHOLD = HERD_CFG.get('similarity_threshold', 0.35)
TIME_WINDOW_DAYS = HERD_CFG.get('time_window_days', 7)
MAX_FEATURES = HERD_CFG.get('max_features', 10000)
MIN_DF = HERD_CFG.get('min_df', 5)
MAX_DF = HERD_CFG.get('max_df', 0.9)
CHUNK_SIZE = HERD_CFG.get('chunk_size', 1000)  # 仅用于日志显示; 实际内存分块由 pairwise_distances_chunked(working_memory=) 控制


# ============================================================================
# 2. 核心算法: 分块相似度计算
# ============================================================================

def _build_tfidf_vectorizer(n_docs: int, *, relaxed: bool = False) -> TfidfVectorizer:
    """Create a TF-IDF vectorizer whose df thresholds are valid for the group size."""
    if relaxed or n_docs <= MIN_DF:
        min_df = 1
        max_df = 1.0
    else:
        min_df = min(MIN_DF, n_docs)
        max_df = MAX_DF
        if isinstance(max_df, float) and 0 < max_df < 1.0:
            max_allowed_df = int(np.floor(max_df * n_docs))
            if max_allowed_df < min_df:
                min_df = max(1, max_allowed_df)

    return TfidfVectorizer(
        max_features=MAX_FEATURES,
        min_df=min_df,
        max_df=max_df,
        analyzer='char_wb',  # 中文友好: 字符级 n-gram
        ngram_range=(2, 4),
        dtype=np.float32,  # 节省内存
    )

def _compute_similar_counts_for_track(
    bank_df: pd.DataFrame, text_col: str, dates: list
) -> np.ndarray | None:
    """对单一文本列计算同银行 + 时间窗口内的"前驱跟风计数"向量。

    抽出 v3.5.0 单轨实现的核心算法以支持双轨复用 (Plan E P1 B3)。
    返回 None 表示无法向量化 (空文本 / TF-IDF 失败), 调用方应保留 weight=1.0。

    Args:
        bank_df: 单银行子集, 已按日期排序。
        text_col: 文本列名 ('内容' for full, 'content_ctx' for ctx)。
        dates:    与 bank_df 对齐的日期列表 (含 NaT)。

    Returns:
        np.ndarray[int] 长度 = len(bank_df), 每元素为 i 的"早于 i 且相似 ≥ 阈值"
        前驱数; 失败返回 None。
    """
    texts = bank_df[text_col].fillna('').astype(str).tolist()
    non_empty = [t for t in texts if len(t.strip()) > 0]
    if len(non_empty) < 2:
        return None

    try:
        tfidf_matrix = _build_tfidf_vectorizer(len(texts)).fit_transform(texts)
    except ValueError:
        try:
            tfidf_matrix = _build_tfidf_vectorizer(
                len(texts), relaxed=True
            ).fit_transform(texts)
        except ValueError:
            return None

    n_articles = len(texts)
    if n_articles <= 2000:
        _epoch = pd.Timestamp('1970-01-01')
        dates_num = np.array(
            [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
            dtype=np.float64)
        time_diff = np.abs(np.subtract.outer(dates_num, dates_num))
        time_diff = np.nan_to_num(time_diff, nan=float(TIME_WINDOW_DAYS + 1))
        valid_mask = (time_diff <= TIME_WINDOW_DAYS) & np.tril(
            np.ones((n_articles, n_articles), dtype=bool), k=-1)
        sim_matrix = 1.0 - pairwise_distances(tfidf_matrix, metric='cosine')
        herd_mask = (sim_matrix >= SIMILARITY_THRESHOLD) & valid_mask
        return herd_mask.sum(axis=1).astype(int)

    # ⚠ PERF / SCALABILITY (audit-fixes 2026-05-29, M5 — documented, deferred):
    # 下方 >2000 篇分支是 O(N²): pairwise_distances_chunked 计算全 N×N 余弦,
    # 内层 `for j in range(global_i)` 是纯 Python 双循环, 7 天窗在循环内判断而非
    # 用来缩候选集。在 400k-article 生产规模 (M0 gate 之后) 头部银行 ~20k 篇 →
    # ~2e8 次内循环 + 20k×20k 余弦, 是 stage 24 主 wall-clock cliff。
    # 修复配方 (须 byte 级数值等价, 不改 herd_weight): 先按日期排序并按 7 天滚动
    # 窗预分桶 (仿 article_staleness.compute_surface_staleness 的 day-bucketing,
    # ~50000× 提速 precedent), 仅对同窗候选算相似度, 把 per-bank 成本从 O(N²)
    # 降到 O(N·window)。等价要求: 保持"j 按 index < global_i 且
    # |date_i-date_j|<=window 且 sim>=threshold"的计数语义不变。
    # 暂不实施: dev panel (≤2000 篇/bank) 全走上方 dense 分支, 本分支无 >2000 篇
    # 测试夹具可验证数值等价, 贸然重写有 herd_weight 静默回归风险 → defer 到
    # M0 规模放大时连同 >2000 篇 fixture 一起做。
    similar_counts = np.zeros(n_articles, dtype=int)
    row_start = 0
    for chunk in pairwise_distances_chunked(
        tfidf_matrix, working_memory=128, metric='cosine'
    ):
        n_rows_in_chunk = chunk.shape[0]
        similarity_chunk = 1.0 - chunk
        for local_i in range(n_rows_in_chunk):
            global_i = row_start + local_i
            date_i = dates[global_i]
            for j in range(global_i):
                date_j = dates[j]
                if pd.isna(date_i) or pd.isna(date_j):
                    continue
                if abs((date_i - date_j).days) > TIME_WINDOW_DAYS:
                    continue
                if similarity_chunk[local_i, j] >= SIMILARITY_THRESHOLD:
                    similar_counts[global_i] += 1
        row_start += n_rows_in_chunk
    return similar_counts


def compute_herd_weights(df: pd.DataFrame) -> pd.DataFrame:
    """对同一银行在时间窗口内的新闻进行**双轨**跟风检测 (Plan E P1 B3, v3.6.0)。

    算法流程 (对 full / ctx 两轨各跑一次):
      1. 按 target_bank 分组
      2. 对每组新闻进行 TF-IDF 向量化 (轨 1 用 '内容', 轨 2 用 'content_ctx')
      3. 使用 pairwise_distances_chunked 分块计算余弦距离
      4. 在时间窗口内, 若文章 j 与更早的文章 i 的相似度 > 阈值,
         则 j 被标记为"跟风", 衰减权重递减
      5. 衰减公式: weight_j = 1 / (1 + n_similar_predecessors)

    v3.6.0 修复 (Edwards 2001 ORM measurement-treatment matching):
      原 v3.5.0 仅对全文计算 herd_weight 单列, 被下游同时施加到
      _full / _ctx 两轨, 造成 _ctx 路径被"全文相似度"惩罚。
      本版本输出 herd_weight_full + herd_weight_ctx 两列, 下游按轨匹配。

    Args:
        df: 篇章级 DataFrame, 须含 'target_bank', '日期', '内容' 列;
            'content_ctx' 可选 — 缺失时 ctx 轨回退到 '内容' (即与 full 同值)。

    Returns:
        df: 附加 'herd_weight_full' / 'herd_weight_ctx' /
            'n_similar_articles_full' / 'n_similar_articles_ctx' 四列。
    """
    logger.info("=" * 60)
    logger.info("步骤 1: 跟风/抄袭新闻检测与衰减加权 (双轨 v3.6.0)")
    logger.info("=" * 60)
    logger.info(f"  参数: similarity_threshold={SIMILARITY_THRESHOLD}, "
                f"time_window={TIME_WINDOW_DAYS}天, "
                f"max_features={MAX_FEATURES}, chunk_size={CHUNK_SIZE}")

    # 确保日期列为 datetime
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

    # 双轨文本列解析
    # full 轨: 优先 '内容', 兼容 '正文' / 'content'
    full_col = '内容' if '内容' in df.columns else (
        '正文' if '正文' in df.columns else 'content')
    has_full = full_col in df.columns
    # ctx 轨: 来自 stage 21 _materialize_content_ctx; 缺失则回退 full
    has_ctx = 'content_ctx' in df.columns

    if not has_full:
        logger.warning(f"  文本列 '{full_col}' 不存在, 所有 herd_weight 设为 1.0")
        df['herd_weight_full'] = 1.0
        df['herd_weight_ctx'] = 1.0
        df['n_similar_articles_full'] = 0
        df['n_similar_articles_ctx'] = 0
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = 1.0
        df['n_similar_articles'] = 0
        return df

    if not has_ctx:
        logger.warning(
            "  'content_ctx' 列不存在 (stage 21 _materialize_content_ctx 未跑?), "
            "ctx 轨回退至全文计算 — 此时 herd_weight_ctx ≡ herd_weight_full, "
            "不构成真双轨。建议先执行 stage 21 物化 content_ctx。"
        )

    # 初始化结果列
    df['herd_weight_full'] = 1.0
    df['herd_weight_ctx'] = 1.0
    df['n_similar_articles_full'] = 0
    df['n_similar_articles_ctx'] = 0

    if 'target_bank' not in df.columns:
        logger.warning("  'target_bank' 列不存在, 所有 herd_weight 设为 1.0")
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = df['herd_weight_full']
        df['n_similar_articles'] = df['n_similar_articles_full']
        return df

    bank_groups = df.groupby('target_bank')
    n_banks = len(bank_groups)
    logger.info(f"  共 {n_banks} 家银行待处理 (双轨)")

    total_herd_full = 0
    total_herd_ctx = 0

    for bank_idx, (bank_name, bank_df) in enumerate(bank_groups):
        if len(bank_df) < 2:
            continue

        bank_df = bank_df.sort_values('日期').copy()
        indices = bank_df.index.tolist()
        dates = bank_df['日期'].tolist()

        # full 轨计算
        full_counts = _compute_similar_counts_for_track(bank_df, full_col, dates)
        # ctx 轨计算 (缺失时回退 = full)
        if has_ctx:
            ctx_counts = _compute_similar_counts_for_track(bank_df, 'content_ctx', dates)
        else:
            ctx_counts = full_counts  # 回退: 与 full 同值, 由 has_ctx 警告告知用户

        for k, idx in enumerate(indices):
            if full_counts is not None:
                n_sim_f = int(full_counts[k])
                df.at[idx, 'n_similar_articles_full'] = n_sim_f
                df.at[idx, 'herd_weight_full'] = 1.0 / (1.0 + n_sim_f)
                if n_sim_f > 0:
                    total_herd_full += 1
            if ctx_counts is not None:
                n_sim_c = int(ctx_counts[k])
                df.at[idx, 'n_similar_articles_ctx'] = n_sim_c
                df.at[idx, 'herd_weight_ctx'] = 1.0 / (1.0 + n_sim_c)
                if n_sim_c > 0:
                    total_herd_ctx += 1

        if (bank_idx + 1) % 50 == 0:
            logger.info(f"  已处理 {bank_idx + 1}/{n_banks} 家银行")

    n_total = len(df)
    logger.info(f"  双轨跟风检测完成:")
    logger.info(f"    总新闻数: {n_total:,}")
    logger.info(f"    full 轨跟风: {total_herd_full:,} "
                f"({total_herd_full/max(n_total,1):.1%})")
    logger.info(f"    ctx  轨跟风: {total_herd_ctx:,} "
                f"({total_herd_ctx/max(n_total,1):.1%})")
    logger.info(f"    herd_weight_full mean={df['herd_weight_full'].mean():.4f}, "
                f"min={df['herd_weight_full'].min():.4f}")
    logger.info(f"    herd_weight_ctx  mean={df['herd_weight_ctx'].mean():.4f}, "
                f"min={df['herd_weight_ctx'].min():.4f}")

    # v3.6.0 NON-BREAKING 兼容层 (F-B 修): 保留 herd_weight / n_similar_articles
    # 单列 alias = _full 路径, 让 v3.5.x 既有调用方 (paper Stata 模板 / 测试套件 /
    # legacy panel reader) 不破坏. 下游若想用 ctx 路径必须显式引用 _ctx 后缀列.
    df['herd_weight'] = df['herd_weight_full']
    df['n_similar_articles'] = df['n_similar_articles_full']

    # 双轨独立性诊断 (Plan E P1 B3 验收门 #2):
    # 若 Spearman ρ(herd_weight_full, herd_weight_ctx) < 0.95, 视为"真双轨";
    # ≥ 0.95 提示 ctx 与 full 文本几乎相同 (可能 content_ctx fallback 比例过高)
    try:
        from scipy.stats import spearmanr
        valid = (df['herd_weight_full'].notna() &
                 df['herd_weight_ctx'].notna() &
                 (df['herd_weight_full'].nunique() > 1))
        if valid.sum() >= 50:
            rho, _ = spearmanr(
                df.loc[valid, 'herd_weight_full'],
                df.loc[valid, 'herd_weight_ctx'])
            logger.info(f"    双轨独立性诊断: Spearman ρ = {rho:.4f} "
                        f"({'真双轨' if abs(rho) < 0.95 else '⚠ 高度相关, 检查 content_ctx fallback 比例'})")
    except ImportError:
        pass

    return df


# ============================================================================
# 3. 主流程
# ============================================================================

def main():
    """主入口: 加载数据 → 跟风检测 → 保存。"""
    import time
    start_time = time.time()

    logger.info("=" * 60)
    logger.info(f"阶段 {STAGE_NAME} 启动")
    logger.info("=" * 60)

    # 加载篇章级数据: 固定读取阶段 23 (BERT情感分析) 的输出
    # 严禁回退读取 22/21 的输出，避免磁盘残留旧文件导致静默数据污染
    filenames = CONFIG.get('filenames', {})
    input_filename = filenames.get('output_23_bert_tone', '23_bert_tone.parquet')
    output_filename = filenames.get('output_24_herd_decay', '24_herd_decay.parquet')
    input_file = os.path.join(OUTPUT_DIR, input_filename)
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(input_file):
        logger.error(
            f"输入文件未找到: {input_file}。"
            f"请确保阶段 23 (tone_berts) 已在 enabled_methods 中启用并成功执行。"
        )
        # 显式以非零返回码退出, 让上游编排器能感知"DAG 24 依赖 23"契约违规,
        # 避免父进程把 'silent return' 误判为 stage 24 成功 (详见 plan c2)。
        raise SystemExit(1)

    # 记录输入文件修改时间，便于数据溯源审计
    import datetime as _dt
    _mtime = os.path.getmtime(input_file)
    logger.info(
        f"  📁 输入文件: {input_filename} "
        f"(修改时间: {_dt.datetime.fromtimestamp(_mtime).strftime('%Y-%m-%d %H:%M:%S')})"
    )

    df = pd.read_parquet(input_file)
    logger.info(f"  加载 {len(df):,} 条新闻 (来源: {input_filename})")

    # 执行跟风检测
    df = compute_herd_weights(df)

    # 保存 (追加 herd_weight 列后写入独立输出文件)
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    save_parquet_with_metadata(
        df=df,
        output_path=output_file,
        stage_name="24_herd_decay",
        config=CONFIG,
        input_files=[input_file],
    )
    logger.info(f"  已保存至 {output_file}")

    elapsed = time.time() - start_time
    logger.info(f"  耗时: {elapsed:.1f}秒")
    logger.info(f"阶段 {STAGE_NAME} 完成 ✓")


if __name__ == '__main__':
    main()
