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
