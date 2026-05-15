"""v3.1.1: tone_gap_tech_app helper - hermetic 测试 (无 live parquet 依赖).

测试设计 (15 轮审核 R11/R12 修复):
- 直接调用 module-level helper _compute_tone_gap_tech_app
- 合成 panel-level fixture, 绕过 aggregate_panel 巨函数
- 覆盖 mutation kill: 阈值边界 / min vs max / 减法方向 / dtype / value range
"""
import pandas as pd
import pytest

from news_process.pipeline.panel.encode import _compute_tone_gap_tech_app


def _make_panel(rows):
    """构造最小 panel fixture.

    Args:
        rows: list of (n_tech, n_app, tone_tech, tone_app) tuples
    """
    return pd.DataFrame({
        'n_articles_tech': [r[0] for r in rows],
        'n_articles_app': [r[1] for r in rows],
        'llm_vote_tone_tech_full': pd.array([r[2] for r in rows], dtype='Float64'),
        'llm_vote_tone_app_full': pd.array([r[3] for r in rows], dtype='Float64'),
    })


def test_qualified_at_threshold_5():
    """mutation kill: >=5 vs >5 — n=5 必须 qualified."""
    panel = _make_panel([(5, 5, 0.6, -0.2)])
    result = _compute_tone_gap_tech_app(panel)
    assert result.iloc[0] == pytest.approx(0.8, rel=1e-6)


def test_unqualified_min_below_5():
    """mutation kill: min vs max — n_tech=4 必须 NaN."""
    panel = _make_panel([(4, 10, 0.5, 0.1)])  # min=4 < 5
    result = _compute_tone_gap_tech_app(panel)
    assert pd.isna(result.iloc[0])


def test_unqualified_other_side_below_5():
    """对称: n_app=2 必须 NaN (验证 max mutation 不通过)."""
    panel = _make_panel([(10, 2, 0.3, 0.4)])  # min=2 < 5
    result = _compute_tone_gap_tech_app(panel)
    assert pd.isna(result.iloc[0])


def test_subtraction_direction_tech_minus_app():
    """mutation kill: tech-app vs app-tech — tech 正 / app 负 → 正差."""
    panel = _make_panel([(5, 5, 0.6, -0.2)])
    result = _compute_tone_gap_tech_app(panel)
    assert result.iloc[0] > 0  # 0.6 - (-0.2) = +0.8


def test_dtype_float64_nullable():
    """dtype 必须 Float64 (与 tone_gap_sub_symb 对称)."""
    panel = _make_panel([(5, 5, 0.6, -0.2)])
    result = _compute_tone_gap_tech_app(panel)
    assert str(result.dtype) == 'Float64'


def test_value_range_within_minus_two_to_plus_two():
    """value range: tech - app, 两 mean ∈ [-1,+1] → gap ∈ [-2,+2]."""
    panel = _make_panel([(5, 5, 1.0, -1.0), (5, 5, -1.0, 1.0)])
    result = _compute_tone_gap_tech_app(panel)
    assert result.iloc[0] == pytest.approx(2.0, rel=1e-6)
    assert result.iloc[1] == pytest.approx(-2.0, rel=1e-6)
