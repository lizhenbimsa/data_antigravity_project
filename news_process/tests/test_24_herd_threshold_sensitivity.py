"""阈值敏感性守护测试 (2026-06-13): herd 相似度阈值网格的多阈值一遍式计数。

背景: similarity_threshold=0.35 是研究者自由参数 (构念锚 Tetlock 2011 RFS 用连续
staleness 不设硬阈值)。herd_decay 按 herd_detection.sensitivity_thresholds 网格
(默认 {0.25, 0.30, 0.40, 0.45}) 在同一 TF-IDF/余弦矩阵上一遍式复算前驱计数,
输出 herd_weight_{track}_thrNN, 经 runner 3d-2 + encode F5b 聚合为面板
llm_vote_tone_hw_thrNN_{track}, 供 Stata 稳健性表逐 τ 重估主回归。

守护点:
  1. herd_sensitivity_grid 单一事实源 (去重/剔基线/非法值过滤/tag 编码)
  2. thresholds=None 的 1D 兼容路径 ≡ 多阈值矩阵的基线列 (老调用方零回归)
  3. 计数对阈值的单调性 (τ↓ ⇒ count↑, weight↓)
  4. dense / bucketed 两分支多阈值下逐位等价
  5. compute_herd_weights 输出全部 thr 列且与基线列契约一致
  6. encode.build_aggregation_dict 注册 F5b 聚合键 (含 valid-mask 分母)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from news_process.core.config import herd_sensitivity_grid
from news_process.pipeline.sentiment.herd_decay import (
    SENS_TAGS,
    SENS_THRESHOLDS,
    SIMILARITY_THRESHOLD,
    _bucketed_similar_counts,
    _dense_similar_counts,
    compute_herd_weights,
)


# ---------------------------------------------------------------------------
# 1. 单一事实源: herd_sensitivity_grid
# ---------------------------------------------------------------------------
class TestHerdSensitivityGrid:
    def test_default_grid(self):
        thrs, tags = herd_sensitivity_grid(
            {'herd_detection': {'similarity_threshold': 0.35}})
        assert thrs == [0.25, 0.30, 0.40, 0.45]
        assert tags == ['thr25', 'thr30', 'thr40', 'thr45']

    def test_baseline_excluded_and_dedup_and_invalid_filtered(self):
        thrs, tags = herd_sensitivity_grid({'herd_detection': {
            'similarity_threshold': 0.35,
            # 0.35=基线剔除; 'x' 非数值; 1.5 越界; 0.275 非 0.01 粒度; 0.25 重复
            'sensitivity_thresholds': [0.45, 0.35, 0.25, 'x', 1.5, 0.275, 0.25],
        }})
        assert thrs == [0.25, 0.45]
        assert tags == ['thr25', 'thr45']

    def test_non_list_disables(self):
        assert herd_sensitivity_grid(
            {'herd_detection': {'sensitivity_thresholds': 'oops'}}) == ([], [])

    def test_sorted_ascending(self):
        thrs, _ = herd_sensitivity_grid({'herd_detection': {
            'sensitivity_thresholds': [0.45, 0.25, 0.40]}})
        assert thrs == sorted(thrs)

    def test_module_constants_consistent(self):
        # herd_decay 模块级常量须与生产 config 网格一致 (列名契约共享)
        assert len(SENS_THRESHOLDS) == len(SENS_TAGS)
        for thr, tag in zip(SENS_THRESHOLDS, SENS_TAGS):
            assert tag == f"thr{int(round(thr * 100)):02d}"
            assert abs(thr - SIMILARITY_THRESHOLD) > 1e-9


# ---------------------------------------------------------------------------
# 2-4. 计数核心: 1D 兼容 / 单调性 / 双分支等价
# ---------------------------------------------------------------------------
def _graded_matrix(n: int, seed: int = 7) -> np.ndarray:
    """构造行向量两两余弦连续散布的稠密矩阵 (覆盖各阈值两侧)。

    standard_normal 单位化后两两余弦围绕 0 散布 (6 维下 sd≈0.4), 在
    0.25-0.45 网格区间内两侧均有质量, 保证逐阈值计数真正分化。
    """
    rng = np.random.default_rng(seed)
    m = rng.standard_normal((n, 6))
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def _seq_dates(n: int) -> list:
    """非降序日期 (含同日并列) — 分桶分支前置要求升序 (镜像生产 sort_values)。"""
    base = pd.Timestamp('2017-03-01')
    return [base + pd.Timedelta(days=i // 3) for i in range(n)]


THR_GRID = [0.25, 0.30, 0.35, 0.40, 0.45]


class TestMultiThresholdCounts:
    def test_baseline_column_equals_legacy_1d(self):
        M, dates = _graded_matrix(60), _seq_dates(60)
        legacy = _dense_similar_counts(M, dates)            # 1D 兼容路径
        multi = _dense_similar_counts(M, dates, thresholds=[SIMILARITY_THRESHOLD, 0.25])
        assert legacy.ndim == 1 and multi.shape == (60, 2)
        assert np.array_equal(legacy, multi[:, 0])

    def test_monotonic_in_threshold(self):
        M, dates = _graded_matrix(80), _seq_dates(80)
        counts = _dense_similar_counts(M, dates, thresholds=THR_GRID)
        for k in range(len(THR_GRID) - 1):
            assert (counts[:, k] >= counts[:, k + 1]).all(), (
                f"τ={THR_GRID[k]} 计数应 ≥ τ={THR_GRID[k+1]}")
        # 非平凡性: 网格两端计数确实不同 (否则单调性测试空转)
        assert counts[:, 0].sum() > counts[:, -1].sum()

    def test_dense_bucket_equivalence_multithreshold(self):
        M, dates = _graded_matrix(120, seed=11), _seq_dates(120)
        dense = _dense_similar_counts(M, dates, thresholds=THR_GRID)
        bucket = _bucketed_similar_counts(M, dates, thresholds=THR_GRID)
        assert np.array_equal(dense, bucket)

    def test_bucket_1d_compat(self):
        M, dates = _graded_matrix(40, seed=3), _seq_dates(40)
        legacy = _bucketed_similar_counts(M, dates)
        multi = _bucketed_similar_counts(M, dates, thresholds=[SIMILARITY_THRESHOLD])
        assert legacy.ndim == 1 and multi.shape == (40, 1)
        assert np.array_equal(legacy, multi[:, 0])


# ---------------------------------------------------------------------------
# 5. compute_herd_weights 端到端列契约
# ---------------------------------------------------------------------------
def _article_frame(n: int = 24) -> pd.DataFrame:
    base = "央行发布金融科技发展规划银行积极推进数字化转型与普惠金融服务创新"
    rows = []
    for i in range(n):
        txt = base + "拓展" * (i % 4)
        rows.append({
            'target_bank': '测试银行',
            '日期': pd.Timestamp('2017-03-01') + pd.Timedelta(days=i % 9),
            '标题': f'新闻{i}',
            '内容': txt,
            'content_full': f'新闻{i}。' + txt,
            'content_ctx': f'新闻{i}。' + txt[:18],
        })
    return pd.DataFrame(rows)


class TestComputeHerdWeightsSensitivityColumns:
    def test_thr_columns_present_and_contract(self):
        out = compute_herd_weights(_article_frame())
        for tag in SENS_TAGS:
            for tr in ('full', 'ctx'):
                w = out[f'herd_weight_{tr}_{tag}']
                c = out[f'n_similar_articles_{tr}_{tag}']
                # 权重契约: w = 1/(1+n), ∈ (0, 1]
                assert ((w > 0) & (w <= 1.0)).all()
                assert np.allclose(w, 1.0 / (1.0 + c))

    def test_threshold_monotonicity_end_to_end(self):
        if len(SENS_TAGS) < 2:
            return  # 网格被缩水配置禁用时跳过
        out = compute_herd_weights(_article_frame())
        ordered = sorted(zip(SENS_THRESHOLDS, SENS_TAGS))
        for tr in ('full', 'ctx'):
            seq = [out[f'n_similar_articles_{tr}_{tag}'] for _, tag in ordered]
            for a, b in zip(seq, seq[1:]):
                assert (a >= b).all()

    def test_baseline_columns_unchanged_by_grid(self):
        # 基线列 (herd_weight_full/ctx) 不因网格存在而改变 — 与权重契约自洽
        out = compute_herd_weights(_article_frame())
        for tr in ('full', 'ctx'):
            assert np.allclose(
                out[f'herd_weight_{tr}'],
                1.0 / (1.0 + out[f'n_similar_articles_{tr}']))


# ---------------------------------------------------------------------------
# 6. encode 聚合注册 (F5b)
# ---------------------------------------------------------------------------
def test_encode_aggregation_registers_sensitivity_keys():
    from news_process.pipeline.panel.encode import CONFIG, build_aggregation_dict
    _, tags = herd_sensitivity_grid(CONFIG)
    if not tags:
        return  # 网格被禁用时无注册义务
    agg = build_aggregation_dict()
    for track in ('_full', '_ctx'):
        for tag in tags:
            assert agg[f'avg_herd_weight{track}_{tag}'] == (
                f'herd_weight{track}_{tag}', 'mean')
            assert agg[f'sum_herd_weight{track}_{tag}'] == (
                f'herd_weight{track}_{tag}', 'sum')
            assert agg[f'llm_vote_score_hw_{tag}_sum{track}'] == (
                f'llm_vote_score_hw_{tag}{track}', 'sum')
            assert agg[f'llm_vote_cont_hw_{tag}_sum{track}'] == (
                f'llm_vote_cont_hw_{tag}{track}', 'sum')
            # encode-01 同构: valid-mask 分母
            assert agg[f'sum_wd_hw_{tag}_llm{track}'] == (
                f'_wd_hw_{tag}_llm{track}', 'sum')


def test_stata_name_length_within_32():
    # Stata 变量名硬上限 32 字符 — 最长生成名是聚合中间列
    _, tags = herd_sensitivity_grid(
        {'herd_detection': {'similarity_threshold': 0.35}})
    for tag in tags:
        for track in ('_full', '_ctx'):
            for name in (
                f'llm_vote_tone_hw_{tag}{track}',
                f'llm_vote_cont_hw_{tag}{track}',
                f'llm_vote_score_hw_{tag}_sum{track}',
                f'avg_herd_weight{track}_{tag}',
                f'sum_herd_weight{track}_{tag}',
            ):
                assert len(name) <= 32, name
