"""W1 守护测试: herd_decay 的 7 天窗分桶分支 (_bucketed_similar_counts) 与原稠密
参照分支 (_dense_similar_counts) 在 >2000 篇 fixture 上**数值逐位等价**。

背景: pipeline/sentiment/herd_decay.py 原 >2000 篇分支是 O(N^2) 纯 Python 双循环,
全量 17M/2007-2024 下头部银行 (工农中建招) 数十万篇会触发 wall-clock cliff + N×N
余弦 OOM。M0 规模修复改为 7 天窗双指针分桶 (O(N·window))。模块注释明确要求:
重写必须连同 >2000 篇 fixture 对拍, 防 herd_weight 静默回归。本文件即该守护。

等价语义 (两分支必须逐位一致): 对每篇 i (已按日期升序), 计
    {j : j<i, 0 <= date_i - date_j <= 7, cos_sim(i,j) >= SIMILARITY_THRESHOLD}
NaT 篇既不计数也不作候选。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from news_process.pipeline.sentiment.herd_decay import (
    _bucketed_similar_counts,
    _build_tfidf_vectorizer,
    _dense_similar_counts,
)


def _onehot(topics: np.ndarray, n_topics: int) -> np.ndarray:
    """构造 one-hot 矩阵 → cos_sim 恰为 0/1 (同主题=1, 异主题=0), 远离 0.35 阈值,
    使等价判定不受浮点边界干扰, 纯验"分桶+计数"逻辑。"""
    m = np.zeros((len(topics), n_topics), dtype=np.float64)
    m[np.arange(len(topics)), topics] = 1.0
    return m


# ---------------------------------------------------------------------------
# 1. 显式边界: 7 天 (计入) vs 8 天 (排除)
# ---------------------------------------------------------------------------
def test_window_boundary_7_vs_8_days():
    d0 = pd.Timestamp('2015-03-01')
    # 4 篇同主题, 升序: day0 / day7 / day8 / day16
    dates = [d0, d0 + pd.Timedelta(days=7), d0 + pd.Timedelta(days=8),
             d0 + pd.Timedelta(days=16)]
    M = _onehot(np.zeros(4, dtype=int), 1)  # 全同主题 → sim 恒 1
    dense = _dense_similar_counts(M, dates)
    bucket = _bucketed_similar_counts(M, dates)
    # day0: 无前驱 → 0
    # day7: day0 diff=7 (<=7) → 1
    # day8: day7 diff=1 ✓; day0 diff=8 (>7) ✗ → 1
    # day16: day8 diff=8 ✗, day7 diff=9 ✗, day0 diff=16 ✗ → 0
    assert list(dense) == [0, 1, 1, 0]
    assert np.array_equal(dense, bucket)


# ---------------------------------------------------------------------------
# 2. 显式 NaT: 不计数也不作候选
# ---------------------------------------------------------------------------
def test_nat_excluded():
    d0 = pd.Timestamp('2015-03-01')
    # 升序 (NaT 末尾): day0 / day1 / NaT, 全同主题
    dates = [d0, d0 + pd.Timedelta(days=1), pd.NaT]
    M = _onehot(np.zeros(3, dtype=int), 1)
    dense = _dense_similar_counts(M, dates)
    bucket = _bucketed_similar_counts(M, dates)
    # day0: 0; day1: day0 diff1 → 1; NaT: 跳过 → 0
    assert list(dense) == [0, 1, 0]
    assert np.array_equal(dense, bucket)


# ---------------------------------------------------------------------------
# 3. 同日并列: date_i == date_j (j<i) 必须计入
# ---------------------------------------------------------------------------
def test_same_day_ties():
    d0 = pd.Timestamp('2015-03-01')
    dates = [d0, d0, d0]  # 三篇同日同主题
    M = _onehot(np.zeros(3, dtype=int), 1)
    dense = _dense_similar_counts(M, dates)
    bucket = _bucketed_similar_counts(M, dates)
    # i=0:0; i=1: j=0 diff0 → 1; i=2: j=0,j=1 → 2
    assert list(dense) == [0, 1, 2]
    assert np.array_equal(dense, bucket)


# ---------------------------------------------------------------------------
# 4. 大规模 (>2000) 受控等价: one-hot 主题, 含同日/NaT/各种窗口距离
# ---------------------------------------------------------------------------
def test_large_controlled_equivalence():
    rng = np.random.default_rng(42)
    n = 2500  # >2000, 触发生产分派的分桶分支
    n_topics = 40
    base = pd.Timestamp('2015-03-01')

    topics = rng.integers(0, n_topics, size=n)
    day_off = rng.integers(0, 45, size=n).astype(float)  # 45 天跨度 → 大量同日/同窗
    nat_idx = rng.choice(n, size=35, replace=False)       # 注入 35 个 NaT
    day_off[nat_idx] = np.nan

    # 按日期升序排序 (NaT 末尾), 对齐 topics — 镜像生产 sort_values('日期')
    order = sorted(
        range(n),
        key=lambda k: (np.isnan(day_off[k]), 0.0 if np.isnan(day_off[k]) else day_off[k]),
    )
    topics_s = topics[order]
    dates_s = [
        pd.NaT if np.isnan(day_off[k]) else base + pd.Timedelta(days=int(day_off[k]))
        for k in order
    ]
    M = _onehot(topics_s, n_topics)

    dense = _dense_similar_counts(M, dates_s)
    bucket = _bucketed_similar_counts(M, dates_s)

    assert np.array_equal(dense, bucket), (
        f"分桶分支与稠密参照不一致: 首个差异 idx="
        f"{int(np.argmax(dense != bucket))}"
    )
    # 非平凡性: 必须真的命中过 herd, 否则测试空转
    assert dense.sum() > 0


# ---------------------------------------------------------------------------
# 5. 真实文本稀疏路径 (>2000) 烟雾: 用生产 TF-IDF 矢量器, 验稀疏行/切片索引正确
# ---------------------------------------------------------------------------
def test_real_text_sparse_equivalence():
    rng = np.random.default_rng(7)
    n = 2100
    n_clusters = 60
    base = pd.Timestamp('2015-03-01')

    bases = [
        f"金融科技创新与银行数字化转型专题报道第{c}组深度分析内容"
        for c in range(n_clusters)
    ]
    cl = rng.integers(0, n_clusters, size=n)
    texts = [bases[cl[k]] + f"补充材料编号{k}" for k in range(n)]
    day_off = rng.integers(0, 60, size=n).astype(float)

    # 升序排序对齐
    order = np.argsort(day_off, kind='stable')
    texts_s = [texts[k] for k in order]
    dates_s = [base + pd.Timedelta(days=int(day_off[k])) for k in order]

    tfidf = _build_tfidf_vectorizer(len(texts_s)).fit_transform(texts_s)

    dense = _dense_similar_counts(tfidf, dates_s)
    bucket = _bucketed_similar_counts(tfidf, dates_s)

    assert np.array_equal(dense, bucket)
    assert dense.sum() > 0  # 同簇近重复必产生 herd 命中
