"""Tests for news_process.papers._common.stats_helpers.

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.9 partial.
Covers within_unit_sd (A4) + cluster_block_bootstrap_ci (C1).

fix(omni-g-papers-misc-10, 2026-06-11): 主名由 block_subsampling_ci (方法标签
误称 Politis-Romano subsampling) 更正为 cluster_block_bootstrap_ci (实现自始是
with-replacement 块自助); 本文件断言改用新名 (positional 模式数值行为逐位不变),
旧名 alias 的 DeprecationWarning 行为在 tests/test_omni_fix_papers_misc.py 锁定。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from news_process.papers._common.stats_helpers import (
    cluster_block_bootstrap_ci,
    within_unit_sd,
)

# ============================================================================
# within_unit_sd
# ============================================================================


class TestWithinUnitSD:
    def test_constant_within_units_returns_zero(self) -> None:
        """每个 unit 内部值恒定 → within SD == 0."""
        series = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
        unit_id = ["a", "a", "b", "b", "c", "c"]
        assert within_unit_sd(series, unit_id) == pytest.approx(0.0, abs=1e-10)

    def test_two_unit_symmetric_variation(self) -> None:
        """两 unit, 每 unit 两观测对称偏离均值."""
        # a: [1, 3] mean=2, demeaned=[-1, 1]
        # b: [5, 7] mean=6, demeaned=[-1, 1]
        # combined demeaned: [-1, 1, -1, 1] → SD(ddof=1) = sqrt(4/3) ≈ 1.1547
        series = [1.0, 3.0, 5.0, 7.0]
        unit_id = ["a", "a", "b", "b"]
        assert within_unit_sd(series, unit_id) == pytest.approx(1.1547, abs=1e-3)

    def test_drops_nan_values(self) -> None:
        """NaN 行被 drop, 不参与 demean."""
        # After dropna: a=[1.0] (demeaned=0), b=[5.0, 7.0] (demeaned=[-1, 1])
        # combined demeaned: [0, -1, 1] → SD(ddof=1) = 1.0
        series = [1.0, np.nan, 5.0, 7.0]
        unit_id = ["a", "a", "b", "b"]
        assert within_unit_sd(series, unit_id) == pytest.approx(1.0, abs=1e-3)

    def test_all_nan_returns_nan(self) -> None:
        """全 NaN → 返回 NaN (insufficient obs)."""
        series = [np.nan, np.nan]
        unit_id = ["a", "b"]
        result = within_unit_sd(series, unit_id)
        assert np.isnan(result)

    def test_single_obs_per_unit_returns_zero(self) -> None:
        """每 unit 1 obs → 所有 demeaned = 0 → SD = 0."""
        series = [1.0, 5.0, 9.0]
        unit_id = ["a", "b", "c"]
        assert within_unit_sd(series, unit_id) == pytest.approx(0.0, abs=1e-10)

    def test_accepts_pandas_series_and_numpy(self) -> None:
        """接受 pd.Series 和 np.ndarray 输入."""
        s = pd.Series([1.0, 3.0, 5.0, 7.0])
        u = pd.Series(["a", "a", "b", "b"])
        sd_pd = within_unit_sd(s, u)
        sd_np = within_unit_sd(s.values, u.values)
        assert sd_pd == pytest.approx(sd_np, abs=1e-10)


# ============================================================================
# cluster_block_bootstrap_ci (fix(omni-g-papers-misc-10): 原名 block_subsampling_ci)
# ============================================================================


class TestClusterBlockBootstrapCI:
    def test_constant_values_give_degenerate_ci(self) -> None:
        """全相等输入 → CI = (val, val, val)."""
        values = np.full(20, 0.5)
        point, lo, hi = cluster_block_bootstrap_ci(
            values, block_size=2, n_resamples=100, seed=42
        )
        assert point == pytest.approx(0.5, abs=1e-12)
        assert lo == pytest.approx(0.5, abs=1e-12)
        assert hi == pytest.approx(0.5, abs=1e-12)

    def test_ordering_low_lt_point_lt_high(self) -> None:
        """CI 边界 lo ≤ point ≤ hi."""
        rng = np.random.default_rng(123)
        values = rng.standard_normal(200)
        point, lo, hi = cluster_block_bootstrap_ci(
            values, block_size=2, n_resamples=500, seed=42
        )
        assert lo <= point <= hi

    def test_reproducible_with_seed(self) -> None:
        """相同 seed → 相同结果."""
        rng = np.random.default_rng(123)
        values = rng.standard_normal(100)
        r1 = cluster_block_bootstrap_ci(values, block_size=2, n_resamples=200, seed=7)
        r2 = cluster_block_bootstrap_ci(values, block_size=2, n_resamples=200, seed=7)
        assert r1 == r2

    def test_different_seed_gives_different_ci(self) -> None:
        """不同 seed → CI 边界不同 (point 相同, 边界 stochastic)."""
        rng = np.random.default_rng(123)
        values = rng.standard_normal(100)
        r1 = cluster_block_bootstrap_ci(values, block_size=2, n_resamples=200, seed=1)
        r2 = cluster_block_bootstrap_ci(values, block_size=2, n_resamples=200, seed=2)
        assert r1[0] == pytest.approx(r2[0], abs=1e-10)  # point estimate
        # bounds should differ stochastically
        assert (r1[1], r1[2]) != (r2[1], r2[2])

    def test_drops_nan_values(self) -> None:
        """NaN 值被 drop, 不影响计算."""
        rng = np.random.default_rng(42)
        values = rng.standard_normal(100)
        values[::10] = np.nan
        point, lo, hi = cluster_block_bootstrap_ci(
            values, block_size=2, n_resamples=200, seed=42
        )
        assert not np.isnan(point)
        assert lo <= point <= hi

    def test_too_few_obs_raises(self) -> None:
        """obs 数 < block_size * 2 → ValueError."""
        values = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="block_size"):
            cluster_block_bootstrap_ci(values, block_size=2, n_resamples=100, seed=42)

    def test_alpha_param_affects_ci_width(self) -> None:
        """alpha=0.10 (90% CI) 应当窄于 alpha=0.05 (95% CI)."""
        rng = np.random.default_rng(42)
        values = rng.standard_normal(200)
        _, lo90, hi90 = cluster_block_bootstrap_ci(
            values, block_size=2, n_resamples=500, alpha=0.10, seed=42
        )
        _, lo95, hi95 = cluster_block_bootstrap_ci(
            values, block_size=2, n_resamples=500, alpha=0.05, seed=42
        )
        assert (hi90 - lo90) <= (hi95 - lo95)

    def test_block_size_one_equivalent_to_iid_bootstrap(self) -> None:
        """block_size=1 退化为标准 iid bootstrap on means."""
        rng = np.random.default_rng(42)
        values = rng.standard_normal(100)
        # Should run without error
        point, lo, hi = cluster_block_bootstrap_ci(
            values, block_size=1, n_resamples=500, seed=42
        )
        assert lo <= point <= hi

    def test_accepts_pandas_series_and_list(self) -> None:
        """接受 pd.Series / list / np.ndarray 输入."""
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        r_np = cluster_block_bootstrap_ci(arr, block_size=2, n_resamples=100, seed=42)
        r_pd = cluster_block_bootstrap_ci(
            pd.Series(arr), block_size=2, n_resamples=100, seed=42
        )
        r_lst = cluster_block_bootstrap_ci(
            list(arr), block_size=2, n_resamples=100, seed=42
        )
        assert r_np == r_pd == r_lst
