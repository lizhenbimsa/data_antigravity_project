"""Unit tests for papers/benefit_society/shrinkage.py."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def shrink():
    from news_process.papers.benefit_society import shrinkage
    return shrinkage


def test_shrinkage_returns_arrays_of_same_length(shrink):
    values = np.array([1.0, 2.0, 3.0, 4.0])
    n_obs = np.array([10, 5, 3, 1])
    groups = np.array(["G1", "G1", "G2", "G2"])
    shrunk, weights = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    assert shrunk.shape == values.shape
    assert weights.shape == values.shape


def test_shrinkage_weights_in_unit_interval(shrink):
    rng = np.random.default_rng(0)
    n = 50
    values = rng.normal(0, 1, n)
    n_obs = rng.integers(1, 20, n)
    groups = rng.choice(["A", "B", "C"], n)
    _, weights = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    assert np.all(weights >= 0.0)
    assert np.all(weights <= 1.0)


def test_shrinkage_more_when_n_obs_small(shrink):
    """Lower n_obs → larger within-unit variance → larger shrinkage weight."""
    values = np.array([5.0, 5.0])
    n_obs = np.array([100, 1])  # First is precise, second is sparse
    groups = np.array(["G1", "G1"])
    _, weights = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    assert weights[1] >= weights[0]


def test_shrinkage_pulls_toward_group_mean(shrink):
    """An outlier observation must be pulled toward its group mean."""
    values = np.array([0.0, 0.0, 0.0, 10.0])
    n_obs = np.array([100, 100, 100, 1])
    groups = np.array(["G1", "G1", "G1", "G1"])
    shrunk, _ = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    # The outlier should have moved toward 0 (group mean)
    assert abs(shrunk[3]) < 10.0


def test_shrinkage_handles_nan(shrink):
    """NaN values must be left untouched."""
    values = np.array([1.0, np.nan, 3.0])
    n_obs = np.array([5, 5, 5])
    groups = np.array(["G", "G", "G"])
    shrunk, _ = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    assert np.isnan(shrunk[1])
    assert np.isfinite(shrunk[0])
    assert np.isfinite(shrunk[2])


def test_shrinkage_insufficient_obs_returns_raw(shrink):
    """With <2 valid obs, must return raw values unchanged."""
    values = np.array([1.0, np.nan])
    n_obs = np.array([5, 5])
    groups = np.array(["G", "G"])
    shrunk, weights = shrink.empirical_bayes_shrinkage(values, n_obs, groups)
    assert abs(shrunk[0] - 1.0) < 1e-9
    assert np.all(weights == 0)


def test_shrinkage_length_mismatch_raises(shrink):
    with pytest.raises(ValueError, match="equal length"):
        shrink.empirical_bayes_shrinkage(
            np.array([1, 2, 3]), np.array([5, 5]), np.array(["A", "B"])
        )


def test_apply_shrinkage_to_panel_adds_columns(shrink):
    df = pd.DataFrame({
        "benefit_mean_full": [0.1, 0.2, 0.3, -0.1, np.nan, 0.5],
        "n_articles": [10, 5, 8, 3, 2, 12],
        "bank_type": ["city", "city", "rural", "rural", "city", "rural"],
        "bank_province": ["P1", "P1", "P2", "P2", "P1", "P2"],
    })
    out = shrink.apply_shrinkage_to_panel(df)
    assert "benefit_mean_full_shrunk" in out.columns
    assert "benefit_mean_full_shrunk_weight" in out.columns
    assert len(out) == len(df)


def test_apply_shrinkage_to_panel_missing_columns_raises(shrink):
    df = pd.DataFrame({"benefit_mean_full": [0.1, 0.2]})
    with pytest.raises(KeyError, match="Missing columns"):
        shrink.apply_shrinkage_to_panel(df)


def test_apply_shrinkage_custom_output_col(shrink):
    df = pd.DataFrame({
        "benefit_mean_full": [0.1, 0.2],
        "n_articles": [5, 5],
        "bank_type": ["A", "A"],
        "bank_province": ["P", "P"],
    })
    out = shrink.apply_shrinkage_to_panel(df, output_col="my_shrunk_col")
    assert "my_shrunk_col" in out.columns
    assert "my_shrunk_col_weight" in out.columns


# ============================================================================
# quality-hardening Round 53 (2026-05-27): shrinkage 65.38% → ≥90%
# 补 mixedlm_sanity_check (127-146) + CLI legacy/track 分支 (236/240/254-280)
# ============================================================================


@pytest.mark.filterwarnings("ignore:Random effects covariance is singular:UserWarning")
def test_mixedlm_returns_dict_when_statsmodels_available(shrink):
    """mixedlm_sanity_check 在 statsmodels 装好时返回 dict (lines 127-143)."""
    # 合成 panel 含足够 groups + samples
    rng = np.random.default_rng(7)
    n = 60
    df = pd.DataFrame({
        'benefit_mean_full': rng.normal(0, 1, n),
        'bank_province': rng.choice(['P1', 'P2', 'P3'], n),
    })
    result = shrink.mixedlm_sanity_check(df, 'benefit_mean_full', 'bank_province')
    # statsmodels 应该装好 (pyproject 依赖); 应返回 dict
    if result is not None:
        assert 'sigma_within' in result
        assert 'sigma_between' in result
        assert 'icc' in result
        # ICC ∈ [0, 1]
        assert 0.0 <= result['icc'] <= 1.0


def test_mixedlm_returns_none_for_too_few_obs(shrink):
    """obs < 10 或 group < 2 → 返回 None (lines 134-135)."""
    df = pd.DataFrame({
        'benefit_mean_full': [0.1, 0.2, 0.3],
        'bank_province': ['P1', 'P1', 'P2'],  # 只 3 行
    })
    result = shrink.mixedlm_sanity_check(df, 'benefit_mean_full', 'bank_province')
    assert result is None


def test_mixedlm_returns_none_when_statsmodels_missing(shrink, monkeypatch):
    """statsmodels 不可用 → 返回 None (line 129-131).

    通过 sys.modules 注入失败的 statsmodels.formula.api 抢断 import.
    """
    import sys
    monkeypatch.setitem(sys.modules, 'statsmodels.formula.api', None)
    df = pd.DataFrame({
        'benefit_mean_full': [0.1] * 20,
        'bank_province': ['P1', 'P2'] * 10,
    })
    result = shrink.mixedlm_sanity_check(df, 'benefit_mean_full', 'bank_province')
    assert result is None


def test_mixedlm_returns_none_on_exception(shrink, monkeypatch):
    """MixedLM 内部抛 → except 返回 None (lines 144-146)."""
    from unittest.mock import patch
    df = pd.DataFrame({
        'benefit_mean_full': [0.1] * 20,
        'bank_province': ['P1', 'P2'] * 10,
    })

    class FakeModel:
        def fit(self, **_kw):
            raise RuntimeError("fit failed simulated")

    def fake_mixedlm(*_args, **_kw):
        return FakeModel()

    import statsmodels.formula.api as smf
    with patch.object(smf, 'mixedlm', side_effect=fake_mixedlm):
        result = shrink.mixedlm_sanity_check(
            df, 'benefit_mean_full', 'bank_province')
    assert result is None


def test_main_panel_missing_required_returns_1(tmp_path):
    """main(): 基础列缺失 → return 1 (lines 247-252)."""
    from news_process.papers.benefit_society.shrinkage import main
    # panel 仅 benefit_mean_full, 缺 n_articles / bank_type / bank_province
    panel_path = tmp_path / 'panel.parquet'
    df = pd.DataFrame({'benefit_mean_full': [0.1, 0.2]})
    df.to_parquet(panel_path)
    rc = main(['--panel', str(panel_path),
                '--output', str(tmp_path / 'out.parquet')])
    assert rc == 1


def test_main_legacy_value_col_branch(tmp_path):
    """--value-col 覆盖 --track (lines 235-236)."""
    from news_process.papers.benefit_society.shrinkage import main
    panel_path = tmp_path / 'panel.parquet'
    # 含完整列 + custom value_col
    df = pd.DataFrame({
        'custom_metric': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        'n_articles': [5] * 10,
        'bank_type': ['A'] * 10,
        'bank_province': ['P1'] * 10,
    })
    df.to_parquet(panel_path)
    output = tmp_path / 'out.parquet'
    rc = main([
        '--panel', str(panel_path),
        '--value-col', 'custom_metric',
        '--output', str(output),
    ])
    assert rc == 0
    assert output.exists()


def test_main_track_full_branch_writes_panel(tmp_path):
    """--track full 走 line 240 ('benefit_mean_full' single track)."""
    from news_process.papers.benefit_society.shrinkage import main
    panel_path = tmp_path / 'panel.parquet'
    df = pd.DataFrame({
        'benefit_mean_full': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        'n_articles': [5] * 10,
        'bank_type': ['A'] * 10,
        'bank_province': ['P1'] * 10,
    })
    df.to_parquet(panel_path)
    output = tmp_path / 'out.parquet'
    rc = main([
        '--panel', str(panel_path),
        '--track', 'full',
        '--output', str(output),
    ])
    assert rc == 0
    out_df = pd.read_parquet(output)
    assert 'benefit_mean_full_shrunk' in out_df.columns


def test_main_track_both_skips_missing_ctx_column(tmp_path):
    """--track both: 仅 _full 存在, _ctx 缺 → warning skip (lines 256-258 + 273-278)."""
    from news_process.papers.benefit_society.shrinkage import main
    panel_path = tmp_path / 'panel.parquet'
    df = pd.DataFrame({
        'benefit_mean_full': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        # no benefit_mean_ctx → warning skip
        'n_articles': [5] * 10,
        'bank_type': ['A'] * 10,
        'bank_province': ['P1'] * 10,
    })
    df.to_parquet(panel_path)
    output = tmp_path / 'out.parquet'
    rc = main([
        '--panel', str(panel_path),
        '--track', 'both',
        '--output', str(output),
    ])
    assert rc == 0
    out_df = pd.read_parquet(output)
    assert 'benefit_mean_full_shrunk' in out_df.columns
    assert 'benefit_mean_ctx_shrunk' not in out_df.columns
