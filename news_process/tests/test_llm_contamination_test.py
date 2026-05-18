"""tests/test_llm_contamination_test.py — DC4 单元测试 (V4 F-Adv.2 critical)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.audit.llm_contamination_test import (
    compute_correlation,
    contamination_test,
    fisher_z_test,
)


@pytest.fixture
def df_no_contamination():
    """合成 panel: pre 与 post cutoff 相关性接近 (无 contamination)."""
    rng = np.random.default_rng(42)
    n_pre = 200
    n_post = 200
    # 真实 channel: corr ≈ 0.4 两边都一样
    pre_outcome = rng.standard_normal(n_pre)
    pre_llm = 0.4 * pre_outcome + np.sqrt(1 - 0.16) * rng.standard_normal(n_pre)
    post_outcome = rng.standard_normal(n_post)
    post_llm = 0.4 * post_outcome + np.sqrt(1 - 0.16) * rng.standard_normal(n_post)

    dates_pre = pd.date_range('2010-01-01', periods=n_pre, freq='D')
    dates_post = pd.date_range('2025-01-01', periods=n_post, freq='D')
    return pd.DataFrame({
        'date': list(dates_pre) + list(dates_post),
        'llm_col': list(pre_llm) + list(post_llm),
        'outcome_col': list(pre_outcome) + list(post_outcome),
    })


@pytest.fixture
def df_strong_contamination():
    """合成 panel: pre cutoff corr 异常高 (LLM 记忆了答案), post 接近 0."""
    rng = np.random.default_rng(123)
    n_pre = 300
    n_post = 300
    # Pre: corr 0.85 (LLM memorized); Post: corr 0.05 (no real signal)
    pre_outcome = rng.standard_normal(n_pre)
    pre_llm = 0.85 * pre_outcome + np.sqrt(1 - 0.7225) * rng.standard_normal(n_pre)
    post_outcome = rng.standard_normal(n_post)
    post_llm = 0.05 * post_outcome + np.sqrt(1 - 0.0025) * rng.standard_normal(n_post)

    dates_pre = pd.date_range('2010-01-01', periods=n_pre, freq='D')
    dates_post = pd.date_range('2025-01-01', periods=n_post, freq='D')
    return pd.DataFrame({
        'date': list(dates_pre) + list(dates_post),
        'llm_col': list(pre_llm) + list(post_llm),
        'outcome_col': list(pre_outcome) + list(post_outcome),
    })


class TestFisherZTest:
    """Fisher z-transformation correctness."""

    def test_identical_corrs_p_high(self):
        z, p = fisher_z_test(r1=0.4, n1=200, r2=0.4, n2=200)
        assert abs(z) < 0.5
        assert p > 0.5

    def test_different_corrs_p_low(self):
        z, p = fisher_z_test(r1=0.8, n1=200, r2=0.1, n2=200)
        assert abs(z) > 5.0
        assert p < 0.01

    def test_small_n_returns_nan(self):
        z, p = fisher_z_test(r1=0.5, n1=3, r2=0.5, n2=3)
        assert np.isnan(z)
        assert np.isnan(p)

    def test_extreme_corr_returns_nan(self):
        z, p = fisher_z_test(r1=0.9999, n1=100, r2=0.5, n2=100)
        assert np.isnan(z)


class TestComputeCorrelation:
    """compute_correlation pearson + spearman."""

    def test_perfect_corr(self):
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': [2, 4, 6, 8, 10]})
        r, n = compute_correlation(df, 'a', 'b')
        assert abs(r - 1.0) < 1e-9
        assert n == 5

    def test_handles_missing(self):
        # rows 0 (1, 2), 1 (2, 4), 4 (5, 10) 完全可观测 → n=3
        # row 2 'a'=NaN → drop; row 3 'b'=NaN → drop
        df = pd.DataFrame({'a': [1, 2, None, 4, 5], 'b': [2, 4, 6, None, 10]})
        r, n = compute_correlation(df, 'a', 'b')
        assert n == 3

    def test_too_few_obs(self):
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        r, n = compute_correlation(df, 'a', 'b')
        assert np.isnan(r)


class TestContaminationDetection:
    """Detection logic on synthetic data."""

    def test_no_contamination_correctly_classified(self, df_no_contamination):
        report = contamination_test(
            df_no_contamination,
            llm_col='llm_col',
            outcome_col='outcome_col',
            date_col='date',
            cutoff_date='2024-01-01',  # test-frozen, NOT 来自 LLM provider
        )
        # 关键 invariant: NOT 'contamination_detected' (否则会误报)
        # reverse_pattern_anomaly 在随机 noise 下可能出现, 不是 contamination
        assert report['verdict'] != 'contamination_detected', (
            f"无 contamination 样本被误判: {report['verdict']}"
        )

    def test_strong_contamination_detected(self, df_strong_contamination):
        report = contamination_test(
            df_strong_contamination,
            llm_col='llm_col',
            outcome_col='outcome_col',
            date_col='date',
            cutoff_date='2024-01-01',  # test-frozen, NOT 来自 LLM provider
        )
        assert report['verdict'] == 'contamination_detected'
        # pre corr 应远大于 post corr
        assert report['r_pre_cutoff'] > report['r_post_cutoff'] + 0.3

    def test_report_schema_complete(self, df_no_contamination):
        report = contamination_test(
            df_no_contamination,
            llm_col='llm_col',
            outcome_col='outcome_col',
            date_col='date',
            cutoff_date='2024-01-01',  # test-frozen, NOT 来自 LLM provider
        )
        required_keys = {
            'method', 'cutoff_date', 'llm_col', 'outcome_col',
            'n_pre_cutoff', 'n_post_cutoff',
            'r_pre_cutoff', 'r_post_cutoff',
            'fisher_z_stat', 'fisher_p_value',
            'bayes_factor_h0', 'bayes_factor_label',
            'verdict', 'computed_at_utc',
        }
        assert required_keys.issubset(report.keys())

    def test_missing_col_raises(self):
        df = pd.DataFrame({'date': [], 'llm_col': []})
        with pytest.raises(ValueError, match='必填列缺失'):
            contamination_test(df, llm_col='llm_col',
                               outcome_col='missing_col', date_col='date',
                               cutoff_date='2024-01-01')


pytestmark = [pytest.mark.fast]
