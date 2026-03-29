"""
tests/test_37_dict_coverage_audit.py — 37_dict_coverage_audit.py 白盒测试
=========================================================================

覆盖维度：
  - wilson_ci: 标准比例、边界值 (n=0)、极端比例 (p=0/1)
  - cochran_armitage_trend_test: 正向趋势、无趋势、退化保护
  - compute_hhi: 均匀分布、完全集中、空数组
  - analysis_1_marginal_distribution: 正常输入、空DataFrame
"""

import pytest
import numpy as np
import pandas as pd


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def audit_module():
    """导入 37_dict_coverage_audit 模块。"""
    import importlib
    return importlib.import_module('37_dict_coverage_audit')


# ============================================================================
# 测试 wilson_ci
# ============================================================================

class TestWilsonCI:
    """Wilson score interval 白盒测试。"""

    def test_standard_proportion(self, audit_module):
        """p=0.5, n=100 → CI 应包含 0.5。"""
        lo, hi = audit_module.wilson_ci(0.5, 100)
        assert lo < 0.5 < hi
        assert hi - lo < 0.25  # 置信区间宽度合理

    def test_n_zero(self, audit_module):
        """n=0 → (0.0, 1.0)。"""
        lo, hi = audit_module.wilson_ci(0.5, 0)
        assert lo == 0.0
        assert hi == 1.0

    def test_p_zero(self, audit_module):
        """p=0.0 → CI 下界不应为负。"""
        lo, hi = audit_module.wilson_ci(0.0, 100)
        assert lo >= 0.0
        assert hi > 0.0

    def test_p_one(self, audit_module):
        """p=1.0 → CI 上界不应超过 1。"""
        lo, hi = audit_module.wilson_ci(1.0, 100)
        assert hi <= 1.0
        assert lo < 1.0

    def test_small_sample(self, audit_module):
        """小样本 (n=5) → CI 较宽。"""
        lo, hi = audit_module.wilson_ci(0.6, 5)
        assert lo >= 0.0
        assert hi <= 1.0
        assert hi - lo > 0.2

    def test_large_sample_narrow(self, audit_module):
        """大样本 (n=10000) → CI 很窄。"""
        lo, hi = audit_module.wilson_ci(0.5, 10000)
        assert hi - lo < 0.03

    def test_ci_is_tuple(self, audit_module):
        """返回值应为 tuple。"""
        result = audit_module.wilson_ci(0.5, 100)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_ci_monotonicity(self, audit_module):
        """lo <= hi 恒成立。"""
        for p in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            for n in [1, 10, 100, 1000]:
                lo, hi = audit_module.wilson_ci(p, n)
                assert lo <= hi, f"Invalid CI for p={p}, n={n}: [{lo}, {hi}]"


# ============================================================================
# 测试 cochran_armitage_trend_test
# ============================================================================

class TestCochranArmitageTrend:
    """Cochran-Armitage 趋势检验白盒测试。"""

    def test_positive_trend(self, audit_module):
        """完美正向趋势 → 正统计量。"""
        # 组1: 20% 通过, 组2: 50% 通过, 组3: 80% 通过
        counts = np.array([
            [20, 50, 80],   # successes
            [80, 50, 20],   # failures
        ])
        scores = np.array([1, 2, 3], dtype=float)
        result = audit_module.cochran_armitage_trend_test(counts, scores)
        assert result['statistic'] > 0
        assert result['p_value'] < 0.05
        assert result['slope_sign'] == 1

    def test_no_trend(self, audit_module):
        """无趋势 → p > 0.05（近似）。"""
        # 所有组相同比例
        counts = np.array([
            [50, 50, 50],
            [50, 50, 50],
        ])
        scores = np.array([1, 2, 3], dtype=float)
        result = audit_module.cochran_armitage_trend_test(counts, scores)
        assert result['p_value'] > 0.05  # 不显著

    def test_degenerate_all_zero(self, audit_module):
        """全0 → 退化保护。"""
        counts = np.array([
            [0, 0],
            [100, 100],
        ])
        scores = np.array([1, 2], dtype=float)
        result = audit_module.cochran_armitage_trend_test(counts, scores)
        # 不应崩溃
        assert 'p_value' in result

    def test_return_structure(self, audit_module):
        """返回字典应包含标准键。"""
        counts = np.array([[10, 20], [90, 80]])
        scores = np.array([1, 2], dtype=float)
        result = audit_module.cochran_armitage_trend_test(counts, scores)
        assert 'statistic' in result
        assert 'p_value' in result
        assert 'slope_sign' in result


# ============================================================================
# 测试 compute_hhi
# ============================================================================

class TestComputeHHI:
    """Herfindahl-Hirschman Index 白盒测试。"""

    def test_perfectly_uniform(self, audit_module):
        """完全均匀分布 → HHI = 1/K。"""
        freq = np.array([10, 10, 10, 10, 10])
        hhi = audit_module.compute_hhi(freq)
        assert abs(hhi - 1.0 / 5) < 1e-10

    def test_perfect_concentration(self, audit_module):
        """完全集中（单元素）→ HHI = 1.0。"""
        freq = np.array([100])
        hhi = audit_module.compute_hhi(freq)
        assert abs(hhi - 1.0) < 1e-10

    def test_empty_array(self, audit_module):
        """空数组 → 0.0。"""
        freq = np.array([])
        hhi = audit_module.compute_hhi(freq)
        assert hhi == 0.0

    def test_zero_sum(self, audit_module):
        """全0 → 0.0（除零保护）。"""
        freq = np.array([0, 0, 0])
        hhi = audit_module.compute_hhi(freq)
        assert hhi == 0.0

    def test_two_elements_unequal(self, audit_module):
        """不均匀双元素。"""
        freq = np.array([75, 25])
        hhi = audit_module.compute_hhi(freq)
        # HHI = (0.75)^2 + (0.25)^2 = 0.5625 + 0.0625 = 0.625
        assert abs(hhi - 0.625) < 1e-10

    def test_enk_inverse(self, audit_module):
        """ENK = 1/HHI 验证。"""
        freq = np.array([10, 10, 10, 10])
        hhi = audit_module.compute_hhi(freq)
        enk = 1.0 / hhi
        assert abs(enk - 4.0) < 1e-10


# ============================================================================
# 测试 analysis_1_marginal_distribution
# ============================================================================

class TestAnalysis1Marginal:
    """analysis_1_marginal_distribution 白盒测试。"""

    def test_normal_input(self, audit_module):
        """正常输入 → 返回分布 DataFrame。"""
        df = pd.DataFrame({
            'fintech_distinct_keywords': [3, 3, 4, 5, 5, 5, 6, 7, 3, 4],
        })
        result = audit_module.analysis_1_marginal_distribution(df)
        assert isinstance(result, pd.DataFrame)
        assert 'distinct_keywords' in result.columns
        assert 'n_articles' in result.columns
        assert 'pct' in result.columns

    def test_empty_dataframe(self, audit_module):
        """空 DataFrame → 不崩溃。"""
        df = pd.DataFrame({'fintech_distinct_keywords': pd.Series(dtype=int)})
        result = audit_module.analysis_1_marginal_distribution(df)
        assert isinstance(result, pd.DataFrame)

    def test_all_marginal(self, audit_module):
        """所有文章都是边际组 → 边际率=100%。"""
        T = audit_module.T
        df = pd.DataFrame({
            'fintech_distinct_keywords': [T] * 10,
        })
        result = audit_module.analysis_1_marginal_distribution(df)
        marginal_row = result[result['distinct_keywords'] == T]
        assert not marginal_row.empty
        assert marginal_row.iloc[0]['pct'] == 100.0
