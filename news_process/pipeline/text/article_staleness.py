"""news_process.pipeline.text.article_staleness — stage 18 article-level staleness.

v3.7.0 PR #11 + #11.5 (D2 双指标) — Article staleness 连续 score, 与 v3.6.x
dedup.py:94 的 jaccard 布尔决策互补.

两种 staleness 计算方式
-----------------------
**surface_staleness** (D2.a, PR #11):
    MinHash + datasketch LSHForest, char-shingle 3-gram jaccard.
    与现有 dedup.py jaccard_similarity_threshold=0.85 同源, 升级为连续 score.

**semantic_staleness** (D2.b, PR #11.5):
    Faiss IVFFlat + SBERT cosine (stage 30a article embeddings).
    捕捉语义相似度 (词面不同但含义近似), 与 surface 互补.

双指标 panel 列 (G-S7 设计):
    ``surface_staleness_{full,ctx}``     (与 MinHash jaccard 相关性 ≥ 80%)
    ``semantic_staleness_{full,ctx}``    (Tetlock 2011 JF 原文 cosine 范式)
    ``staleness_corr``                  panel-level surface vs semantic 相关性

学术依据
--------
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors
react to stale information? Review of Financial Studies, 24(5), 1481-1512.
→ 主指标用 cosine staleness, return reversal 实证证据

Gentzkow, M., Shapiro, J. M., & Taddy, M. (2019). Text as data. Journal of
Economic Literature, 57(3), 535-574.

设计
----
- 滚动窗口 7d 内 pairwise 相似度 → max
- N²: 400k 文章 × 7d 窗口典型 ~5000 candidates = 2×10^9 pair 不可行
  → 必须 LSH (MinHashLSHForest for jaccard) + Faiss (HNSW for cosine)
- 双轨独立 (full + ctx 各算一次), 与 v3.5.1 真双轨对齐

D-0 实测项 (v2.3 G-D2.1)
------------------------
surface 与 semantic staleness 相关性 ∈ [0.3, 0.7] (互补 ≠ 冗余).
"""

from __future__ import annotations

import os
import sys
import time
from datetime import timedelta

import numpy as np
import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "18_article_staleness"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

WINDOW_DAYS = 7
SHINGLE_SIZE = 3  # char-shingle 3-gram for MinHash


# ── D2.a Surface staleness (MinHash + datasketch) ────────────────────
def _char_shingles(text: str, n: int = SHINGLE_SIZE) -> set[str]:
    """字符级 n-gram shingle set (中文友好, 不依赖分词)."""
    text = text or ''
    if len(text) < n:
        return {text}
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def compute_surface_staleness(
    df: pd.DataFrame,
    content_col: str,
    date_col: str = '日期',
    num_perm: int = 128,
) -> np.ndarray:
    """每篇文章 surface staleness = max jaccard in past 7d (LSH-accelerated).

    Args:
        df: article-level DataFrame (按 date_col 升序).
        content_col: '内容' or 'content_ctx'.
        date_col: 日期列名.
        num_perm: MinHash permutation 数 (越大越精确, 128 是经验值).

    Returns:
        np.ndarray of shape (N,); 第 1 周内文章为 NaN (无前 7d 邻居).
    """
    try:
        from datasketch import MinHash, MinHashLSHForest
    except ImportError:
        logger.error("datasketch 未装 (requirements.txt:36 应有)")
        raise

    df = df.sort_values(date_col).reset_index(drop=True)
    dates = pd.to_datetime(df[date_col], errors='coerce')

    # ── 预计算 MinHash for each article ──
    logger.info(f"  surface: 预计算 {len(df)} 篇 MinHash (num_perm={num_perm})")
    t0 = time.time()
    hashes = []
    for txt in df[content_col].fillna(''):
        m = MinHash(num_perm=num_perm)
        for s in _char_shingles(txt):
            m.update(s.encode('utf-8'))
        hashes.append(m)
    logger.info(f"  MinHash 完成: {time.time() - t0:.1f}s")

    # ── 按 unique-day 分组 flush 的滚动 LSH (修 S1.3 O(N²) 灾难, v3.7.1) ──
    # 算法 (核心: 按"今天"分组遍历, forest 仅重建 unique_days 次):
    #   1. 按 day 分组 articles;
    #   2. 对每个 day d:
    #        window = [j : cutoff = d - 7d ≤ day_j < d]  # 不含今天
    #        重建 forest with window articles
    #        对所有 articles_on_day_d 查询
    #   3. 复杂度: forest 重建次数 = |unique_days| ≈ 2555 (7y), 每次成本 ~|window|
    #      → 总 ≈ unique_days × (N / unique_days × 7) = 7N
    # 性能: 400k × 7 = 2.8M ops vs 原 O(N²)=1.6e11 → ~50000× speedup
    # 实测预估: 单线程 5-15 min (原 10+ 天)
    stale = np.full(len(df), np.nan)
    if dates.isna().all():
        return stale

    # day-level 索引 (剥离时分秒)
    day = pd.to_datetime(dates.dt.date)
    day_idx = day.groupby(day).groups  # {timestamp: [int indices]}
    unique_days_sorted = sorted([d for d in day_idx.keys() if pd.notna(d)])

    n = len(df)
    t0 = time.time()
    window_start_pos = 0  # day_arr 上的指针 (升序天数列表里的 cursor)
    # 先按 day 升序生成 day_arr (每文章一个 day, day 已 sorted)
    day_arr = day.values  # already aligned with sorted df

    for d in unique_days_sorted:
        cutoff = d - timedelta(days=WINDOW_DAYS)
        # 把 window_start_pos 推进到首个 day_j >= cutoff 的位置
        while window_start_pos < n and (
            pd.isna(day_arr[window_start_pos]) or day_arr[window_start_pos] < cutoff
        ):
            window_start_pos += 1
        # window_end_pos = 首个 day_j >= d 的位置 (即"今天之前最后一篇 + 1")
        window_end_pos = window_start_pos
        while window_end_pos < n and (
            pd.notna(day_arr[window_end_pos]) and day_arr[window_end_pos] < d
        ):
            window_end_pos += 1

        if window_end_pos <= window_start_pos:
            # 窗口空; 该天所有 articles 标 NaN
            for i in day_idx[d]:
                stale[i] = np.nan
            continue

        # 重建 forest (每 day 1 次)
        forest = MinHashLSHForest(num_perm=num_perm)
        for j in range(window_start_pos, window_end_pos):
            forest.add(j, hashes[j])
        forest.index()

        # 查询该天所有 articles
        for i in day_idx[d]:
            results = forest.query(hashes[i], 10)
            if not results:
                stale[i] = 0.0
                continue
            stale[i] = max(hashes[i].jaccard(hashes[j]) for j in results)

    logger.info(f"  surface staleness 完成: {time.time() - t0:.1f}s "
                f"({len(unique_days_sorted)} day-buckets)")
    return stale


# ── D2.b Semantic staleness (Faiss + SBERT cosine) ───────────────────
def compute_semantic_staleness(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    date_col: str = '日期',
) -> np.ndarray:
    """每篇文章 semantic staleness = max cosine sim in past 7d (Faiss-accelerated).

    Args:
        df: article-level DataFrame (按 date_col 升序对齐 embeddings 行).
        embeddings: (N, 768) SBERT embeddings (normalize_embeddings=True 假设).
        date_col: 日期列名.

    Returns:
        np.ndarray of shape (N,); 第 1 周内文章为 NaN.
    """
    try:
        import faiss
    except ImportError:
        logger.error(
            "faiss-cpu 未装; v3.7.0 启用步骤: 取消 requirements.txt 中 "
            "faiss-cpu>=1.7.4 行注释后 pip install"
        )
        raise

    sort_idx = pd.to_datetime(df[date_col], errors='coerce').argsort().values
    df_sorted = df.iloc[sort_idx].reset_index(drop=True)
    embs_sorted = embeddings[sort_idx]
    dates = pd.to_datetime(df_sorted[date_col], errors='coerce')

    N, dim = embs_sorted.shape
    stale = np.full(N, np.nan)

    # 用 IndexFlatIP (inner product on normalized = cosine) 简化实现;
    # 大样本可换 IVFFlat with nprobe=10.
    index = faiss.IndexFlatIP(dim)

    t0 = time.time()
    window_start_idx = 0
    for i in range(N):
        if pd.isna(dates.iloc[i]):
            continue
        cutoff = dates.iloc[i] - timedelta(days=WINDOW_DAYS)
        # 移除窗外
        while window_start_idx < i and dates.iloc[window_start_idx] < cutoff:
            window_start_idx += 1
        # 重建 index (滚动重建; FlatIP 重建成本与 size 线性)
        index.reset()
        if window_start_idx >= i:
            continue
        index.add(embs_sorted[window_start_idx:i].astype(np.float32))
        # 查询 top-1 (除自己)
        D_sim, I_idx = index.search(embs_sorted[i:i + 1].astype(np.float32), 1)
        stale[i] = float(D_sim[0, 0]) if D_sim.shape[1] > 0 else 0.0

    logger.info(f"  semantic staleness 完成: {time.time() - t0:.1f}s")

    # 还原原始顺序
    inv_idx = np.argsort(sort_idx)
    return stale[inv_idx]


# ── bank-year 聚合 ───────────────────────────────────────────────────
def aggregate_to_bank_year(article_df: pd.DataFrame) -> pd.DataFrame:
    """article-level staleness → bank-year mean + frac_high (>0.9)."""
    agg_cols = {}
    for col in ['surface_staleness_full', 'surface_staleness_ctx',
                'semantic_staleness_full', 'semantic_staleness_ctx']:
        if col in article_df.columns:
            agg_cols[col] = lambda s: s.dropna().mean() if len(s.dropna()) else np.nan
            agg_cols[col.replace('staleness', 'highstale')] = (
                lambda s, c=col: (article_df[c] > 0.9).mean()
            )

    panel = (
        article_df.groupby(['target_bank', 'year'], as_index=False)
        .agg({col: 'mean' for col in agg_cols})
    )
    # frac_high_stale 列重命名 (待 v3.7.1 集成时启用)
    # rename = {c: c.replace('staleness', 'highstale')
    #           for c in panel.columns if 'staleness' in c}
    return panel


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 18: Article-level staleness 双指标 (v3.7.0 PR #11+#11.5, D2)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['data_processed_dir']
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  stage 13 未跑: {src_path}")
        sys.exit(1)

    art_df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(art_df)} 行")

    # ── D2.a Surface staleness (双轨) ──
    art_df['surface_staleness_full'] = compute_surface_staleness(
        art_df, content_col='内容',
    )
    if 'content_ctx' in art_df.columns:
        art_df['surface_staleness_ctx'] = compute_surface_staleness(
            art_df, content_col='content_ctx',
        )

    # ── D2.b Semantic staleness (双轨, 依赖 stage 30a) ──
    emb_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    if os.path.exists(emb_path):
        emb_df = pd.read_parquet(emb_path)
        embs_full = np.stack(emb_df['emb_full'].tolist())
        embs_ctx = np.stack(emb_df['emb_ctx'].tolist())
        art_df['semantic_staleness_full'] = compute_semantic_staleness(
            art_df, embs_full,
        )
        art_df['semantic_staleness_ctx'] = compute_semantic_staleness(
            art_df, embs_ctx,
        )
    else:
        logger.warning(
            f"  stage 30a 未跑: {emb_path}; D2.b semantic 跳过 (仅 D2.a surface 输出)"
        )

    # ── article-level 持久化 ──
    out_path = os.path.join(output_dir, '18_article_staleness.parquet')
    keep_cols = (
        ['target_bank', 'year']
        + [c for c in art_df.columns if 'staleness' in c]
    )
    art_df[keep_cols].to_parquet(out_path, index=False)
    logger.info(f"  article-level → {out_path}")

    # ── bank-year 聚合 ──
    panel = aggregate_to_bank_year(art_df)
    panel_path = os.path.join(output_dir, '18_staleness_panel.parquet')
    panel.to_parquet(panel_path, index=False)
    logger.info(f"  bank-year → {panel_path} ({len(panel)} 行)")

    # ── G-D2.1 双指标相关性诊断 ──
    if all(c in art_df.columns for c in ['surface_staleness_full', 'semantic_staleness_full']):
        corr = art_df[['surface_staleness_full', 'semantic_staleness_full']].corr().iloc[0, 1]
        logger.info(
            f"  G-D2.1: surface vs semantic corr = {corr:.4f} "
            f"({'PASS' if 0.3 <= corr <= 0.7 else 'WARN (互补性偏离区间)'})"
        )

    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
