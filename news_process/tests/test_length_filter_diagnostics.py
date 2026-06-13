"""tests/test_length_filter_diagnostics.py — 长度过滤诊断 (log-only) 单元测试.

对象: pipeline/preprocess/load.py::_length_filter_diagnostics / _log_length_filter_diagnostics
(2026-06-13 长度区间顶刊合规化, 详见 scripts/audit/LENGTH_FILTER_JUSTIFICATION_2026-06-13.md)。

核心不变量: 诊断是纯只读 — 不得改变长度过滤行为, 不得修改输入 Series。
导入策略: 与 test_omni_fix_preprocess.py 一致, 在测试体内懒导入生产模块。
"""

import pandas as pd
import pytest


def _diag(series):
    from news_process.pipeline.preprocess.load import _length_filter_diagnostics
    return _length_filter_diagnostics(pd.Series(series))


class TestLengthFilterDiagnostics:

    def test_empty_series_returns_n0_only(self):
        assert _diag([]) == {'n': 0}

    def test_kept_counts_at_production_cutoff(self):
        # 5 篇: 两篇低于下限 100, 一篇高于上限 10000, 两篇在区间内
        lens = [50, 99, 100, 10000, 10001]
        diag = _diag(lens)
        assert diag['n'] == 5
        assert diag['kept'][(100, 10000)] == 2          # 生产阈值组合
        assert diag['kept'][(50, 10000)] == 4           # 放宽下限到 TSM 等价 50
        assert diag['kept'][(100, None)] == 3           # 不设上限 (TSM 2008 路线)
        assert diag['kept'][(200, 5000)] == 0           # 双向收紧

    def test_alternative_cutoff_matrix_complete(self):
        # 矩阵覆盖 min{50,100,200} × max{5000,10000,20000,∞} 共 12 组合
        diag = _diag([100, 200, 300])
        assert len(diag['kept']) == 12
        assert all(lo in (50, 100, 200) and hi in (5000, 10000, 20000, None)
                   for lo, hi in diag['kept'])

    def test_percentiles_and_extremes(self):
        diag = _diag(list(range(1, 101)))  # 1..100
        assert diag['min'] == 1
        assert diag['max'] == 100
        assert diag['pctiles'][0.5] == 50  # 中位数 (int 截断后 50)
        assert set(diag['pctiles']) == {0.01, 0.05, 0.5, 0.95, 0.99}

    def test_input_series_not_mutated(self):
        s = pd.Series([10, 5000, 20000])
        before = s.copy()
        _ = _diag(s.tolist())
        from news_process.pipeline.preprocess.load import _log_length_filter_diagnostics
        _log_length_filter_diagnostics(s)
        pd.testing.assert_series_equal(s, before)

    def test_log_wrapper_handles_empty(self):
        from news_process.pipeline.preprocess.load import _log_length_filter_diagnostics
        _log_length_filter_diagnostics(pd.Series([], dtype='int64'))  # 不抛即过

    def test_all_nan_series_treated_as_empty(self):
        # 全 NaN 守卫: int(min())=int(NaN) 崩溃路径 (生产不可达, 防御性)。
        diag = _diag([float('nan'), float('nan'), float('nan')])
        assert diag == {'n': 0}
        from news_process.pipeline.preprocess.load import _log_length_filter_diagnostics
        _log_length_filter_diagnostics(pd.Series([float('nan')]))  # 不抛即过

    def test_partial_nan_excluded_like_filter(self):
        # 部分 NaN: 与生产过滤同口径 (NaN 比较为 False → 排除), 分位跳 NaN 不崩。
        diag = _diag([float('nan'), 100, 10000, float('nan'), 50])
        assert diag['n'] == 5                       # n = 总行数 (过滤分母, 含 NaN 行)
        assert diag['kept'][(100, 10000)] == 2      # 100, 10000 (NaN 与 50 排除)


class TestProductionCouplingGuards:
    """守卫: 防未来改动静默使 data appendix 供数失效 (audit 2026-06-13 P1)."""

    def test_production_cutoff_present_in_matrix(self):
        # 生产 (content_min_length, content_max_length) 必须落在诊断矩阵格子中,
        # 否则改阈值 (如 150) 后 appendix 缺生产格 → 供数静默失效。
        from news_process.pipeline.preprocess._constants import PARAMS
        from news_process.pipeline.preprocess.load import (
            _DIAG_MAX_CUTOFFS,
            _DIAG_MIN_CUTOFFS,
        )
        lo = PARAMS.get('content_min_length', 100)
        hi = PARAMS.get('content_max_length', 10000)
        assert lo in _DIAG_MIN_CUTOFFS, (
            f"生产下限 {lo} 不在诊断矩阵 {_DIAG_MIN_CUTOFFS}; "
            f"改阈值时须同步 _DIAG_MIN_CUTOFFS"
        )
        assert hi in _DIAG_MAX_CUTOFFS, (
            f"生产上限 {hi} 不在诊断矩阵 {_DIAG_MAX_CUTOFFS}; "
            f"改阈值时须同步 _DIAG_MAX_CUTOFFS"
        )

    def test_diagnostics_wired_into_process_single_file(self):
        # 调用点接线锁: 整个功能的存在意义就是 _process_single_file 里这行调用,
        # 误删不会有其他测试红。用 source 断言 (避免 opencc 依赖)。
        import inspect

        from news_process.pipeline.preprocess.load import _process_single_file
        src = inspect.getsource(_process_single_file)
        assert '_log_length_filter_diagnostics(content_chinese_len)' in src, (
            "内容长度诊断调用点从 _process_single_file 丢失 → data appendix 供数失效"
        )
        assert '_log_title_filter_diagnostics(title_chinese_len)' in src, (
            "标题长度诊断调用点从 _process_single_file 丢失 → 标题删除构成供数失效"
        )


class TestTitleFilterDiagnostics:
    """标题长度诊断 (支撑 '≥2 删的是损坏行而非真标题' 披露; 第三轮终审新增)."""

    @staticmethod
    def _tdiag(series):
        from news_process.pipeline.preprocess.load import _title_filter_diagnostics
        return _title_filter_diagnostics(pd.Series(series))

    def test_empty_and_all_nan_return_n0(self):
        assert self._tdiag([]) == {'n': 0}
        assert self._tdiag([float('nan'), float('nan')]) == {'n': 0}

    def test_typical_composition(self):
        # 标题汉字数: 两个 0 字(损坏), 一个 1 字, 其余 ≥2
        d = self._tdiag([0, 0, 1, 2, 5, 8])
        assert d['n'] == 6
        assert d['kept'] == {1: 4, 2: 3, 3: 2}   # ≥1:4(排2个0) ≥2:3(再排1字) ≥3:2(再排2字)
        assert d['removed_lt2'] == 3              # 6 - 3 = 被 ≥2 删除
        assert d['n_zero'] == 2
        assert d['n_one'] == 1

    def test_log_wrapper_does_not_raise(self):
        from news_process.pipeline.preprocess.load import _log_title_filter_diagnostics
        _log_title_filter_diagnostics(pd.Series([0, 1, 2, 5]))           # 不抛即过
        _log_title_filter_diagnostics(pd.Series([], dtype='int64'))      # 空: 早退不抛

    def test_log_title_wired_into_process_single_file(self):
        import inspect

        from news_process.pipeline.preprocess.load import _process_single_file
        src = inspect.getsource(_process_single_file)
        assert '_log_title_filter_diagnostics(title_chinese_len)' in src


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
