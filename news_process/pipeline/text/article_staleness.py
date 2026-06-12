"""news_process.pipeline.text.article_staleness — stage 18 article-level staleness.

v3.7.0 PR #11 + #11.5 (D2 双指标) — Article staleness 连续 score, 与 v3.6.x
dedup.py:94 的 jaccard 布尔决策互补.

两种 staleness 计算方式
-----------------------
**surface_staleness** (D2.a, PR #11):
    MinHash + datasketch LSHForest, char-shingle 3-gram jaccard.
    与现有 dedup.py jaccard_similarity_threshold=0.85 同源, 升级为连续 score.

**semantic_staleness** (D2.b, PR #11.5):
    Faiss IndexFlatIP (normalized inner-product = cosine) + SBERT cosine
    (stage 30a article embeddings); 大样本可换 IVFFlat (见实现 _compute_semantic).
    捕捉语义相似度 (词面不同但含义近似), 与 surface 互补.

双指标 panel 列 (G-S7 设计):
    ``surface_staleness_{full,ctx}``     (与 MinHash jaccard 相关性 ≥ 80%)
    ``semantic_staleness_{full,ctx}``    (SBERT cosine 扩展轨, Tetlock 2011 RFS 启发)
    ``staleness_corr``                  panel-level surface vs semantic 相关性

学术依据
--------
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors
react to stale information? Review of Financial Studies, 24(5), 1481-1512.
→ staleness 构念锚点 (return reversal 实证证据)

构念保真披露 — fix(omni-g-embed-02, 2026-06-11)
------------------------------------------------
本实现与 Tetlock (2011) 原度量有两点刻意偏离, 论文/codebook 引用时须如实披露:
1. **匹配域**: Tetlock 原文按 *同一公司* 过去 72h 内最近 10 篇旧故事匹配; 本实现
   两轨均为 **corpus-level (全银行混池) 7d 日粒度窗口** — 度量"银行业信息环境"层面
   的 staleness, 非严格的同公司旧闻重印率 (银行 A 的文章与上周关于银行 B 的行业
   通稿相似亦计为 stale)。
2. **相似度函数**: Tetlock 原文是词重叠比率 (与本模块 surface jaccard 轨同族);
   semantic 轨的 SBERT 嵌入 cosine 是 *扩展* 而非"原文范式" (2011 年不存在 SBERT)。

聚合域披露 — fix(omni-g-embed-06/08, 2026-06-11)
------------------------------------------------
staleness 的 *参照窗口* (过去 7d 信息环境基准) 用 stage 13 预筛全集; bank-year
*平均域* 则收缩到 verified 面板语料 ((docid, target_bank) 内连 24_herd_decay /
21_tone_llms), 与面板兄弟列 (tone/herd/intensity, 聚合自 verified-union) 口径
一致。见 ``_restrict_to_panel_domain``。

Gentzkow, M., Shapiro, J. M., & Taddy, M. (2019). Text as data. Journal of
Economic Literature, 57(3), 535-574.

设计
----
- 滚动窗口 7d 内 pairwise 相似度 → max
- N²: 400k 文章 × 7d 窗口典型 ~5000 candidates = 2×10^9 pair 不可行
  → 必须 LSH (MinHashLSHForest for jaccard) + Faiss (rolling-window
    IndexFlatIP for cosine; 大样本升级路径为 IVFFlat / HNSW)
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

    # P0 修复 (metric-audit 2026-06-02): 此前 sort_values 后在"日期排序序"上计算
    # stale 并直接 return; 但 main() 用 `art_df['surface_*'] = compute_surface_*(...)`
    # 按位置赋回"未排序"的 art_df → 整列行错位 (盘上 99.8% 行错配, 且与已做逆置换的
    # semantic 轨不一致). 改为捕获排序置换 _sort_idx, 返回前逆置换还原原始行序
    # (与 compute_semantic_staleness:207-208,244-245 一致).
    _sort_idx = pd.to_datetime(df[date_col], errors='coerce').argsort(kind='stable').values
    df = df.iloc[_sort_idx].reset_index(drop=True)
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
        return stale[np.argsort(_sort_idx)]  # 逆置换还原原始行序 (P0 修复)

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
    # P0 修复 (metric-audit 2026-06-02): 逆置换还原原始行序, 与 main() 的位置赋值对齐.
    return stale[np.argsort(_sort_idx)]


# ── D2.b Semantic staleness (Faiss + SBERT cosine) ───────────────────
def compute_semantic_staleness(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    date_col: str = '日期',
) -> np.ndarray:
    """每篇文章 semantic staleness = max cosine sim in past 7d (Faiss-accelerated).

    fix(omni-g-embed-01, 2026-06-11): 窗口改为日粒度 [d-7d, d) 且**严格排除同日行**,
    与 surface 轨 (`day_arr[window_end_pos] < d`) 语义对齐。此前时间戳粒度窗口含
    同日更早行 — 流水线把同一篇文章 (同 docid) 按 matched bank 复制成多行后,
    dup 组内第 2+ 行与第 1 行 cosine=1.0, semantic staleness 机械=1.0 (盘上
    155/155 同日 dup 行全 =1.0, semantic_highstale 信号几乎纯由该 artifact 驱动),
    且哪一行得 1.0 取决于任意输入行序。修后两轨窗口/NaN 口径一致。

    Args:
        df: article-level DataFrame (按 date_col 升序对齐 embeddings 行).
        embeddings: (N, 768) SBERT embeddings (normalize_embeddings=True 假设).
        date_col: 日期列名.

    Returns:
        np.ndarray of shape (N,); 窗口空 (含首周/仅同日邻居) 的文章为 NaN.
    """
    try:
        import faiss
    except ImportError:
        logger.error(
            "faiss-cpu 未装; v3.7.0 启用步骤: 取消 requirements.txt 中 "
            "faiss-cpu>=1.7.4 行注释后 pip install"
        )
        raise

    # metric-audit 2026-06-02 final: kind='stable' 与 surface 轨 (L108) 对齐 — 大量
    # 同时间戳 ties 下非 stable argsort 的 tie 顺序依赖输入行序 → semantic staleness
    # 值随任意输入序漂移 (实测 27% 行/max 0.75), 破坏可复现性. stable 使其确定.
    sort_idx = pd.to_datetime(df[date_col], errors='coerce').argsort(kind='stable').values
    df_sorted = df.iloc[sort_idx].reset_index(drop=True)
    embs_sorted = embeddings[sort_idx]
    dates = pd.to_datetime(df_sorted[date_col], errors='coerce')
    # fix(omni-g-embed-01, 2026-06-11): day 粒度 (剥离时分秒), 与 surface 轨 L139 对齐
    day_vals = dates.dt.normalize().values  # datetime64[ns], NaT-aware

    N, dim = embs_sorted.shape
    stale = np.full(N, np.nan)

    # 用 IndexFlatIP (inner product on normalized = cosine) 简化实现;
    # 大样本可换 IVFFlat with nprobe=10.
    index = faiss.IndexFlatIP(dim)

    t0 = time.time()
    window_start_idx = 0
    window_end_idx = 0  # 首个 day_j >= 当前日 d 的位置 (同日行被排除在窗口外)
    for i in range(N):
        if pd.isna(day_vals[i]):
            continue
        d = day_vals[i]
        cutoff = d - np.timedelta64(WINDOW_DAYS, 'D')
        # 移除窗外 (P-013 修复: 镜像 compute_surface_staleness L144-147 的 NaT 守卫.
        # 不加 pd.isna 守卫时, NaT < cutoff 返 False, 窗口起点冻结在 NaT 行.)
        while window_start_idx < i and (
            pd.isna(day_vals[window_start_idx])
            or day_vals[window_start_idx] < cutoff
        ):
            window_start_idx += 1
        # fix(omni-g-embed-01, 2026-06-11): 窗口终点 = 首个 day_j >= d 的行 —
        # 严格排除同日行 (镜像 surface 轨 window_end_pos 的 `day < d` 推进条件)
        if window_end_idx < window_start_idx:
            window_end_idx = window_start_idx
        while window_end_idx < i and (
            pd.notna(day_vals[window_end_idx]) and day_vals[window_end_idx] < d
        ):
            window_end_idx += 1
        if window_end_idx <= window_start_idx:
            continue  # 窗口空 → NaN (与 surface 轨空窗口口径一致)
        # 重建 index (滚动重建; FlatIP 重建成本与 size 线性)
        index.reset()
        index.add(embs_sorted[window_start_idx:window_end_idx].astype(np.float32))
        # 查询 top-1 (除自己与同日行)
        D_sim, I_idx = index.search(embs_sorted[i:i + 1].astype(np.float32), 1)
        stale[i] = float(D_sim[0, 0]) if D_sim.shape[1] > 0 else 0.0

    logger.info(f"  semantic staleness 完成: {time.time() - t0:.1f}s")

    # 还原原始顺序
    inv_idx = np.argsort(sort_idx)
    return stale[inv_idx]


# ── bank-year 聚合 ───────────────────────────────────────────────────
def aggregate_to_bank_year(article_df: pd.DataFrame) -> pd.DataFrame:
    """article-level staleness → bank-year mean + frac_high (>0.9).

    P-012 修复 (v3.7.1): 旧实现两个 bug:
    1. lambda `c=col: (article_df[c] > 0.9).mean()` 引用外层 article_df
       而非 group slice → 永远是全局均值, 不是 bank-year mean.
    2. `.agg({col: 'mean' for col in agg_cols})` 丢弃 lambdas + 把
       'surface_highstale_full' 等 article_df 中不存在的 key 传给 groupby.agg
       → KeyError 崩溃, 函数 dead-on-arrival.

    新实现: 先在 article_df 添加 binary highstale 列 (vectorized), 再用
    标准 `.agg('mean')` 一次 groupby 算出 staleness 均值 + highstale 比例.
    """
    if article_df.empty:
        return pd.DataFrame(columns=['target_bank', 'year'])

    df = article_df.copy()
    agg_cols = {}
    for stale_col in ['surface_staleness_full', 'surface_staleness_ctx',
                      'semantic_staleness_full', 'semantic_staleness_ctx']:
        if stale_col in df.columns:
            agg_cols[stale_col] = (stale_col, 'mean')
            # 加 binary high-stale 列 (NaN propagates, mean 自动 skip NA)
            high_col = stale_col.replace('staleness', 'highstale')
            df[high_col] = (df[stale_col] > 0.9).astype('float64')
            df.loc[df[stale_col].isna(), high_col] = np.nan
            agg_cols[high_col] = (high_col, 'mean')

    if not agg_cols:
        return df.groupby(['target_bank', 'year'], as_index=False).size().drop(columns='size')

    panel = df.groupby(['target_bank', 'year'], as_index=False).agg(**agg_cols)
    return panel


def _load_aligned_embeddings(
    art_df: pd.DataFrame, emb_path: str,
) -> tuple[np.ndarray, np.ndarray]:
    """读取 stage 30a embeddings 并按 article_id 显式 join 对齐到 art_df 行序.

    fix(omni-g-embed-03/09, 2026-06-11): 此前 `np.stack(emb_df['emb_full'])` 纯位置
    对齐, 与 13_news_with_ctx 的对应完全靠隐式行序 — stage 13 重生而 30a (4-6h
    手动重负载 stage) 陈旧时, 行数恰相等会**静默整列错位** (semantic staleness 全为
    噪声且不可见)。现按 article_id 键 reindex (30a 写出 article_id = stage 13 的
    df.index, 见 article_sbert.py::_build_output_frame), 长度不等/键缺失/键重复或
    辅键 (target_bank/日期) 逐行不一致时 fail-loud 退出, 提示重跑 30a。

    Returns:
        (embs_full, embs_ctx): 均为 (N, dim) ndarray, 行序与 art_df 一致。
    """
    emb_df = pd.read_parquet(emb_path)

    if 'article_id' not in emb_df.columns:
        logger.error(f"  30a 缺 article_id 键列, 无法显式对齐: {emb_path}")
        sys.exit(1)
    if len(emb_df) != len(art_df):
        logger.error(
            f"  30a 行数 {len(emb_df)} != stage 13 行数 {len(art_df)} — "
            f"30a 陈旧 (stage 13 重生后未重跑 30a), 请先重跑 30a"
        )
        sys.exit(1)

    # 与 30a 产出端同构的键: art_df 有 article_id 列用之, 否则 = 行索引
    # (read_parquet 后为 RangeIndex, 与 30a 写出时的 df.index 同构)
    expected_ids = (
        art_df['article_id'] if 'article_id' in art_df.columns
        else pd.Series(art_df.index)
    ).to_numpy()

    emb_keyed = emb_df.set_index('article_id')
    if emb_keyed.index.duplicated().any():
        logger.error("  30a article_id 键重复, 无法 1:1 对齐, 请重跑 30a")
        sys.exit(1)
    missing = pd.Index(expected_ids).difference(emb_keyed.index)
    if len(missing) > 0:
        logger.error(
            f"  30a 缺 {len(missing)} 个 article_id (如 {list(missing[:5])}) — "
            f"30a 陈旧, 请重跑 30a"
        )
        sys.exit(1)
    emb_aligned = emb_keyed.reindex(expected_ids)

    # 辅键校验: target_bank / 日期 逐行一致 (仅当两 parquet 同源同一 stage-13 快照
    # 才成立; 不一致 = 30a 陈旧 → fail-loud, 防静默错配文章-向量对)
    for key in ('target_bank', '日期'):
        if key in emb_aligned.columns and key in art_df.columns:
            a = emb_aligned[key].reset_index(drop=True)
            b = art_df[key].reset_index(drop=True)
            if key == '日期':
                a = pd.to_datetime(a, errors='coerce')
                b = pd.to_datetime(b, errors='coerce')
            mism = ~((a == b) | (a.isna() & b.isna()))
            if bool(mism.any()):
                logger.error(
                    f"  30a 与 stage 13 的 {key} 不一致 {int(mism.sum())} 行 — "
                    f"两文件非同一 stage-13 快照, 请重跑 30a"
                )
                sys.exit(1)

    # 模型 provenance (g-embed-03 产出端新增列; 旧版 parquet 无 → 仅 WARN 不阻塞)
    if 'model_id' in emb_aligned.columns:
        logger.info(f"  30a 模型 provenance: {emb_aligned['model_id'].iloc[0]}")
    else:
        logger.warning(
            "  30a 无 model_id provenance 列 (旧版 parquet); 建议重跑 30a 落 provenance"
        )

    embs_full = np.stack(emb_aligned['emb_full'].tolist())
    embs_ctx = np.stack(emb_aligned['emb_ctx'].tolist())
    return embs_full, embs_ctx


def _restrict_to_panel_domain(art_df: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """bank-year 聚合前把 *平均域* 收缩到 verified 面板语料 (参照窗口仍用全集).

    fix(omni-g-embed-06/08, 2026-06-11): 此前聚合域 = stage 13 预筛全集 (盘上 1170
    篇), 而面板全部兄弟文章级测度 (tone/herd/intensity/salience) 聚合自 24_herd_decay
    (= stage 21 LLM 双轨验证并集, 盘上 857 篇): 26.8% 被 LLM 判定并非真正关于该银行
    的文章混入 staleness 均值 (27% bank-year 偏移 >0.01, 最大 ≈10.6% 量程), 并产生
    n_articles==0 却带非缺 staleness 的幻影 bank-year 行。staleness 的 *参照窗口*
    (过去 7d 信息环境) 刻意保留全集 — compute_* 已在全集上算完, 本函数仅过滤进入
    bank-year 均值的行: (docid, target_bank) 内连 24_herd_decay (缺则回退
    21_tone_llms)。两文件均缺时 ERROR 披露口径降级并退回全集 (不静默)。
    """
    if not {'docid', 'target_bank'}.issubset(art_df.columns):
        logger.error(
            "⚠ 口径降级[staleness]: art_df 缺 docid/target_bank 键, 聚合域无法收缩到 "
            "verified 语料 → 退回 stage-13 预筛全集 "
            "(与面板兄弟列聚合域不一致, 勿用于发表对比)"
        )
        return art_df
    for fname in ('24_herd_decay.parquet', '21_tone_llms.parquet'):
        vpath = os.path.join(output_dir, fname)
        if not os.path.exists(vpath):
            continue
        ver = pd.read_parquet(vpath, columns=['docid', 'target_bank'])
        vkeys = pd.MultiIndex.from_frame(ver[['docid', 'target_bank']].drop_duplicates())
        akeys = pd.MultiIndex.from_frame(art_df[['docid', 'target_bank']])
        mask = np.asarray(akeys.isin(vkeys))
        logger.info(
            f"  聚合域: {int(mask.sum())}/{len(art_df)} 行落在 verified 语料 ({fname}); "
            f"{int((~mask).sum())} 行仅参与参照窗口、不进 bank-year 均值"
        )
        return art_df[mask]
    logger.error(
        "⚠ 口径降级[staleness]: 24_herd_decay/21_tone_llms 均缺失, bank-year 聚合域"
        "退化为 stage-13 预筛全集 → 与面板兄弟列 (verified-union) 聚合域不一致, "
        "勿用于发表对比"
    )
    return art_df


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 18: Article-level staleness 双指标 (v3.7.0 PR #11+#11.5, D2)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  stage 13 未跑: {src_path}")
        sys.exit(1)

    art_df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(art_df)} 行")

    # P0 修复 (metric-audit 2026-06-02): 13_news_with_ctx 仅有 str 型 '日期', 无
    # 'year' 列; 此前 line ~331 (keep_cols 含 'year') 与 ~335 (groupby year) 必崩
    # KeyError: 'year' (stage 18 dead-on-arrival). 镜像 attention_media.py:255 派生.
    if 'year' not in art_df.columns:
        if '日期' not in art_df.columns:
            logger.error("  缺 'year' 与 '日期' 列, 无法做 bank-year 聚合")
            sys.exit(1)
        art_df['year'] = pd.to_datetime(art_df['日期'], errors='coerce').dt.year

    # ── D2.a Surface staleness (双轨) ──
    # P1 修复 (metric-audit 2026-06-02, 病根A): surface_full 改读 content_full (含标题),
    # 与 semantic_full (emb 含标题) / ctx 轨对称; 缺列回退 '内容'.
    _full_col = 'content_full' if 'content_full' in art_df.columns else '内容'
    art_df['surface_staleness_full'] = compute_surface_staleness(
        art_df, content_col=_full_col,
    )
    if 'content_ctx' in art_df.columns:
        art_df['surface_staleness_ctx'] = compute_surface_staleness(
            art_df, content_col='content_ctx',
        )

    # ── D2.b Semantic staleness (双轨, 依赖 stage 30a) ──
    emb_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    if os.path.exists(emb_path):
        # fix(omni-g-embed-03/09, 2026-06-11): article_id 显式 join 取代裸位置对齐
        embs_full, embs_ctx = _load_aligned_embeddings(art_df, emb_path)
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
        # docid 透传 (provenance 键, 供下游 join / 聚合域审计; 旧 schema 缺则跳过)
        [c for c in ('docid',) if c in art_df.columns]
        + ['target_bank', 'year']
        + [c for c in art_df.columns if 'staleness' in c]
    )
    art_df[keep_cols].to_parquet(out_path, index=False)
    logger.info(f"  article-level → {out_path}")

    # ── bank-year 聚合 ──
    # fix(omni-g-embed-06/08, 2026-06-11): 平均域收缩到 verified 面板语料
    panel = aggregate_to_bank_year(_restrict_to_panel_domain(art_df, output_dir))
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
