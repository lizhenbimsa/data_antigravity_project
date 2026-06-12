"""test_omni_fix_risk — omni 2026-06-11 g-risk 组修复的回归锁.

锁定 pipeline/panel/risk_taking_outcomes.py (stage 49) 的 6 项修复行为:
- g-risk-01: σ(ROA) rolling 与 npl/loan lag-1 的日历语义 (连续年网格 reindex,
  缺年 → NaN, 不再把多年前的值当 "上一年" / "5 年窗" 跨更长日历区间)
- g-risk-02: stock 类季度聚合改单一参考季度快照 (分子分母同测量日)
  + stock_quarter_used 指示列
- g-risk-03: flow 类 YTD-aware 聚合 (data_source 区分 PDF 全年值
  + de-cumulation 单调启发式, 不再无条件 sum 高估 ~2x)
- g-risk-04: rolling-window 与 min_periods 耦合校验 (--rolling-window 3
  不再 pandas ValueError, 3y robustness 路径可运行)
- g-risk-05: LLP discretion 分母改 Loans_{t-1} (与 BW2012 Eq.(2) LHS 一致)
- g-risk-06: σ(ROA)≈0 → z_score 置 NaN 时输出 zero_var_flag 指示列
  (零方差剔除显式披露, 区分数据缺失)

全部为纯内存合成 DataFrame, 无 LLM/IO/网络, 确定性。
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel.risk_taking_outcomes import (
    OUTPUT_OUTCOME_COLS,
    aggregate_quarterly_to_yearly,
    build_risk_taking_outcomes,
    compute_llp_discretion,
    compute_npl_formation,
    compute_sigma_roa_rolling,
    compute_z_score,
    summarize_outcomes,
)

# ─────────────────────────────────────────────────────────────────────────────
# g-risk-01: 日历语义 (连续年网格 reindex)
# ─────────────────────────────────────────────────────────────────────────────

class TestCalendarSemanticsSigma:
    """σ(ROA) rolling: gap year 下窗口按日历计, 不按行位置."""

    def test_gap_years_all_nan(self):
        # 审计复现场景: 年份 [2007,2008,2012,2013,2014] — 任何 5 年日历窗内
        # 非 NaN 观测都 < min_periods=4 → 全 NaN (旧位置窗在第 4/5 行即出值,
        # "5y" 实跨 7 个日历年)
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2007, 2008, 2012, 2013, 2014],
            'roa': [1.0, 1.5, 1.2, 0.9, 1.1],
        })
        out = compute_sigma_roa_rolling(df, window=5, min_periods=4)
        assert out.isna().all(), (
            "gap year 下日历窗内观测不足, σ 必须为 NaN (旧位置窗错误出值)"
        )

    def test_gap_year_counts_as_nan_observation(self):
        # 年份 [2014..2017, 2019] (缺 2018): 2019 的日历窗 [2015..2019] 内
        # 非 NaN = {2015,2016,2017,2019} 恰 4 个 ≥ min_periods → 出值,
        # 且值 = 这 4 个观测的 ddof=1 std (缺年作为 NaN 不贡献数值)
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2014, 2015, 2016, 2017, 2019],
            'roa': [9.0, 1.0, 2.0, 3.0, 4.0],
        })
        out = compute_sigma_roa_rolling(df, window=5, min_periods=4)
        expected = np.std([1.0, 2.0, 3.0, 4.0], ddof=1)
        assert out.iloc[-1] == pytest.approx(expected)
        # 2014 起首的窗口均不足 4 个非 NaN
        assert out.iloc[:3].isna().all()

    def test_continuous_years_unchanged_golden(self):
        # 连续年份下与修复前行为一致 (回归守卫)
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2015, 2016, 2017, 2018, 2019],
            'roa': [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        out = compute_sigma_roa_rolling(df)
        assert out.iloc[3] == pytest.approx(np.std([1, 2, 3, 4], ddof=1))
        assert out.iloc[4] == pytest.approx(np.std([1, 2, 3, 4, 5], ddof=1))

    def test_unsorted_input_index_alignment(self):
        # 乱序输入: 返回 Series 按 (bank, year) 映射回原行, 不依赖输入顺序
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2019, 2015, 2017, 2016, 2018],
            'roa': [5.0, 1.0, 3.0, 2.0, 4.0],
        })
        out = compute_sigma_roa_rolling(df)
        # 行 0 是 year=2019 → 完整 5 年窗 [1..5]
        assert out.iloc[0] == pytest.approx(np.std([1, 2, 3, 4, 5], ddof=1))
        # 行 4 是 year=2018 → 4 obs [1..4]
        assert out.iloc[4] == pytest.approx(np.std([1, 2, 3, 4], ddof=1))


class TestCalendarSemanticsNplFormation:
    """NPL formation lag-1: 缺年 → lag = NaN → formation = NaN."""

    def test_gap_year_lag_is_nan(self):
        # 审计复现场景: 2012 的日历 lag (2011) 缺失 → NaN
        # (旧位置 shift 误用 2008 作 lag → 0.16364)
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2007, 2008, 2012, 2013, 2014],
            'npl_balance': [10.0, 12.0, 30.0, 32.0, 33.0],
            'total_loans': [100.0, 110.0, 200.0, 210.0, 220.0],
        })
        npl, _ = compute_npl_formation(df)
        npl = npl.sort_index()
        assert np.isnan(npl.iloc[0])               # 2007: 无 lag
        assert npl.iloc[1] == pytest.approx(0.02)  # 2008: (12-10)/100
        assert np.isnan(npl.iloc[2]), (
            "2012 的日历 t-1 (2011) 缺失, formation 必须为 NaN "
            "(旧位置 shift 误用 2008 → 0.16364)"
        )
        assert npl.iloc[3] == pytest.approx((32.0 - 30.0) / 200.0)  # 2013
        assert npl.iloc[4] == pytest.approx((33.0 - 32.0) / 210.0)  # 2014

    def test_duplicate_bank_year_raises(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2017],
            'npl_balance': [10.0, 11.0],
            'total_loans': [100.0, 100.0],
        })
        with pytest.raises(ValueError, match='重复键'):
            compute_npl_formation(df)

    def test_nan_year_raises(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017.0, np.nan],
            'npl_balance': [10.0, 11.0],
            'total_loans': [100.0, 100.0],
        })
        with pytest.raises(ValueError, match='year'):
            compute_npl_formation(df)


# ─────────────────────────────────────────────────────────────────────────────
# g-risk-02: stock 单一参考季度快照
# ─────────────────────────────────────────────────────────────────────────────

class TestStockSingleReferenceQuarter:

    def test_numerator_denominator_same_quarter(self):
        # 审计复现场景: rwa 仅 Q1-Q2, TA 全年 → 共同最后季度 Q2 →
        # rwa=52 / TA=104 = 0.5 (旧逐列独立: 52/112 = 0.4643 系统性向下偏)
        df = pd.DataFrame({
            'target_bank': ['A'] * 4,
            'year': [2017] * 4,
            'quarter': [1, 2, 3, 4],
            'rwa': [50.0, 52.0, np.nan, np.nan],
            'total_assets': [100.0, 104.0, 108.0, 112.0],
        })
        out = aggregate_quarterly_to_yearly(df)
        row = out.iloc[0]
        assert row['rwa'] == pytest.approx(52.0)
        assert row['total_assets'] == pytest.approx(104.0), (
            "分母必须与分子取同一参考季度 (Q2), 不得逐列独立取 Q4"
        )
        assert row['stock_quarter_used'] == pytest.approx(2)

    def test_all_nan_column_does_not_poison_snapshot(self):
        # 该 bank-year 完全不披露 rwa → rwa 不参与共同季度判定,
        # 其余 stock 列仍取最后可得季度
        df = pd.DataFrame({
            'target_bank': ['A'] * 4,
            'year': [2017] * 4,
            'quarter': [1, 2, 3, 4],
            'rwa': [np.nan] * 4,
            'total_assets': [100.0, 104.0, 108.0, 112.0],
        })
        out = aggregate_quarterly_to_yearly(df)
        row = out.iloc[0]
        assert np.isnan(row['rwa'])
        assert row['total_assets'] == pytest.approx(112.0)
        assert row['stock_quarter_used'] == pytest.approx(4)

    def test_no_common_quarter_yields_nan(self):
        # rwa 仅 Q1 / TA 仅 Q3 → 无共同季度 → 全 NaN + quarter_used NaN
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            'quarter': [1, 2, 3],
            'rwa': [50.0, np.nan, np.nan],
            'total_assets': [np.nan, np.nan, 108.0],
        })
        out = aggregate_quarterly_to_yearly(df)
        row = out.iloc[0]
        assert np.isnan(row['rwa'])
        assert np.isnan(row['total_assets'])
        assert np.isnan(row['stock_quarter_used'])


# ─────────────────────────────────────────────────────────────────────────────
# g-risk-03: flow YTD-aware 聚合
# ─────────────────────────────────────────────────────────────────────────────

class TestFlowYtdAware:

    @staticmethod
    def _frame(writeoffs, data_source=None):
        n = len(writeoffs)
        d = {
            'target_bank': ['A'] * n,
            'year': [2017] * n,
            'quarter': list(range(1, n + 1)),
            'loan_writeoffs': writeoffs,
        }
        if data_source is not None:
            d['data_source'] = data_source
        return pd.DataFrame(d)

    def test_monotonic_ytd_takes_last_not_sum(self):
        # YTD 累计 [10,20,30,40] → 全年 = 40 (旧 sum = 100, 高估 2.5x)
        out = aggregate_quarterly_to_yearly(self._frame([10.0, 20.0, 30.0, 40.0]))
        assert out['loan_writeoffs'].iloc[0] == pytest.approx(40.0)

    def test_non_monotonic_single_quarter_flows_summed(self):
        # 非单调 → 视为真单季流量 → 求和 (保留旧语义)
        out = aggregate_quarterly_to_yearly(self._frame([30.0, 20.0, 10.0]))
        assert out['loan_writeoffs'].iloc[0] == pytest.approx(60.0)

    def test_pdf_annual_record_preferred_over_heuristic(self):
        # Wind YTD Q1-Q3 + PDF 年报 Q4=28 (重述, 非单调): 必须直接用 PDF 全年值,
        # 不得 sum (旧 sum = 88)
        out = aggregate_quarterly_to_yearly(self._frame(
            [10.0, 20.0, 30.0, 28.0],
            data_source=['wind', 'wind', 'wind', 'annual_report_pdf'],
        ))
        assert out['loan_writeoffs'].iloc[0] == pytest.approx(28.0)

    def test_single_observation_used_directly(self):
        out = aggregate_quarterly_to_yearly(
            self._frame([np.nan, 15.0, np.nan, np.nan])
        )
        assert out['loan_writeoffs'].iloc[0] == pytest.approx(15.0)

    def test_all_nan_returns_nan_min_count_semantic(self):
        out = aggregate_quarterly_to_yearly(
            self._frame([np.nan, np.nan, np.nan, np.nan])
        )
        assert np.isnan(out['loan_writeoffs'].iloc[0])


# ─────────────────────────────────────────────────────────────────────────────
# g-risk-04: rolling-window / min_periods 耦合校验
# ─────────────────────────────────────────────────────────────────────────────

class TestWindowMinPeriodsCoupling:

    def test_window3_with_default_minperiods_does_not_crash(self):
        # 修复前: rolling(window=3, min_periods=4) → pandas ValueError,
        # 文档承诺的 3y robustness 路径无法运行
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017, 2018, 2019],
            'roa': [1.0, 2.0, 3.0],
        })
        out = compute_sigma_roa_rolling(df, window=3, min_periods=4)
        # 自动收缩 min_periods=3 → 第 3 行出值
        assert out.iloc[2] == pytest.approx(np.std([1, 2, 3], ddof=1))

    def test_clamp_equals_explicit_minperiods(self):
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': list(range(2015, 2020)),
            'roa': [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        clamped = compute_sigma_roa_rolling(df, window=3, min_periods=4)
        explicit = compute_sigma_roa_rolling(df, window=3, min_periods=3)
        pd.testing.assert_series_equal(clamped, explicit)


# ─────────────────────────────────────────────────────────────────────────────
# g-risk-05: LLP discretion 分母 = Loans_{t-1}
# ─────────────────────────────────────────────────────────────────────────────

class TestLlpLaggedDenominator:

    def test_denominator_is_lagged_loans(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'A'],
            'year': [2017, 2018, 2019],
            'loan_loss_provision': [15.0, 20.0, 24.0],
            'total_loans': [1000.0, 1100.0, 1200.0],
        })
        out = compute_llp_discretion(df)
        assert np.isnan(out.iloc[0])                      # 无 Loans_{t-1}
        assert out.iloc[1] == pytest.approx(20.0 / 1000.0)  # 非 20/1100
        assert out.iloc[2] == pytest.approx(24.0 / 1100.0)

    def test_gap_year_lag_nan(self):
        # 继承 g-risk-01 日历语义: 2019 的 Loans_{t-1} (2018) 缺失 → NaN
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2019],
            'loan_loss_provision': [15.0, 24.0],
            'total_loans': [1000.0, 1200.0],
        })
        out = compute_llp_discretion(df)
        assert out.isna().all()


# ─────────────────────────────────────────────────────────────────────────────
# g-risk-06: zero_var_flag 零方差剔除披露
# ─────────────────────────────────────────────────────────────────────────────

class TestZeroVarFlag:

    def test_flag_marks_zero_sigma_only(self):
        df = pd.DataFrame({
            'roa': [1.0, 1.0, 1.0],
            'capital_adequacy_ratio': [10.0, 10.0, 10.0],
            'sigma_roa_5y_rolling': [2.0, 0.0, np.nan],
        })
        z, flag = compute_z_score(df)
        assert z.iloc[0] == pytest.approx(5.5)
        assert np.isnan(z.iloc[1]) and np.isnan(z.iloc[2])
        # 仅 σ≈0 (零方差剔除) 标 1; σ=NaN (数据缺失) 标 0
        assert list(flag.astype(int)) == [0, 1, 0]

    def test_summarize_counts_zero_var_censored(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'z_score': [np.nan, np.nan],
            'zero_var_flag': [1, 0],
            'npl_formation_rate': [np.nan, np.nan],
            'rwa_to_ta_ratio': [np.nan, np.nan],
            'sigma_roa_5y_rolling': [0.0, np.nan],
            'loan_loss_provision_discretion': [np.nan, np.nan],
            'is_soe': [np.nan, np.nan],
            'implicit_guarantee_tier': [np.nan, np.nan],
        })
        summary = summarize_outcomes(df)
        assert summary['n_zero_var_censored'] == 1


# ─────────────────────────────────────────────────────────────────────────────
# build 级集成: 全链路 + 输出 schema
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildIntegration:

    @staticmethod
    def _quarterly_two_years() -> pd.DataFrame:
        rows = []
        # 2017: rwa 仅 Q1-Q2 → 参考季度 Q2
        for q, (ta, rwa, npl, loans, wo, llp) in enumerate([
            (100.0, 50.0, 10.0, 80.0, 1.0, 2.0),
            (104.0, 52.0, 10.0, 82.0, 2.0, 2.0),
            (108.0, np.nan, 11.0, 84.0, 3.0, 2.0),
            (112.0, np.nan, 11.0, 86.0, 4.0, 2.0),
        ], start=1):
            rows.append({
                'target_bank': 'A', 'year': 2017, 'quarter': q,
                'roa': 1.0, 'capital_adequacy_ratio': 10.0,
                'total_assets': ta, 'rwa': rwa, 'npl_balance': npl,
                'npl_ratio': 1.5, 'total_loans': loans,
                'loan_writeoffs': wo, 'loan_loss_provision': llp,
            })
        # 2018: rwa Q1 + Q4 → 参考季度 Q4
        for q, (ta, rwa, npl, loans, wo, llp) in enumerate([
            (120.0, 60.0, 11.0, 90.0, 2.0, 3.0),
            (124.0, np.nan, 11.0, 92.0, 4.0, 3.0),
            (128.0, np.nan, 12.0, 94.0, 6.0, 3.0),
            (132.0, 66.0, 12.0, 96.0, 8.0, 3.0),
        ], start=1):
            rows.append({
                'target_bank': 'A', 'year': 2018, 'quarter': q,
                'roa': 1.2, 'capital_adequacy_ratio': 10.0,
                'total_assets': ta, 'rwa': rwa, 'npl_balance': npl,
                'npl_ratio': 1.5, 'total_loans': loans,
                'loan_writeoffs': wo, 'loan_loss_provision': llp,
            })
        return pd.DataFrame(rows)

    def test_end_to_end_consistent_quarters_and_schema(self, tmp_path):
        df_q = self._quarterly_two_years()
        out = build_risk_taking_outcomes(
            df_q, bank_list_path=tmp_path / 'nonexistent_bank_list.yaml'
        )
        # 输出 schema = OUTPUT_OUTCOME_COLS (含新增 zero_var_flag /
        # stock_quarter_used)
        assert list(out.columns) == OUTPUT_OUTCOME_COLS
        assert 'zero_var_flag' in out.columns
        assert 'stock_quarter_used' in out.columns

        r17 = out[out['year'] == 2017].iloc[0]
        r18 = out[out['year'] == 2018].iloc[0]
        # g-risk-02: rwa/TA 同参考季度 → 两年比率均 = 0.5
        assert r17['stock_quarter_used'] == pytest.approx(2)
        assert r18['stock_quarter_used'] == pytest.approx(4)
        assert r17['rwa_to_ta_ratio'] == pytest.approx(52.0 / 104.0)
        assert r18['rwa_to_ta_ratio'] == pytest.approx(66.0 / 132.0)
        # g-risk-03: writeoffs YTD 单调 → 取末值 (2018 = 8, 非 sum=20)
        # g-risk-01/02: npl formation = (npl18(Q4) - npl17(Q2) + wo18) / loans17(Q2)
        assert r18['npl_formation_rate'] == pytest.approx((12.0 - 10.0 + 8.0) / 82.0)
        assert np.isnan(r17['npl_formation_rate'])  # 2017 无 lag
        # g-risk-05: llp discretion 2018 = LLP18 / Loans17
        assert r18['loan_loss_provision_discretion'] == pytest.approx(3.0 / 82.0)
        assert np.isnan(r17['loan_loss_provision_discretion'])
        # 仅 2 年 → σ 不足 min_periods → z NaN 且非零方差剔除
        assert np.isnan(r17['z_score']) and np.isnan(r18['z_score'])
        assert int(r17['zero_var_flag']) == 0 and int(r18['zero_var_flag']) == 0

    def test_constant_roa_sets_zero_var_flag(self, tmp_path):
        # 年度输入 (无 quarter 列): 5 年常数 ROA → σ=0 → z NaN + flag=1
        df_y = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': list(range(2015, 2020)),
            'roa': [1.0] * 5,
            'capital_adequacy_ratio': [10.0] * 5,
            'npl_balance': [10.0] * 5,
            'npl_ratio': [1.5] * 5,
            'total_loans': [100.0] * 5,
            'total_assets': [200.0] * 5,
            'rwa': [80.0] * 5,
            'loan_loss_provision': [2.0] * 5,
        })
        out = build_risk_taking_outcomes(
            df_y, bank_list_path=tmp_path / 'nonexistent_bank_list.yaml'
        )
        out = out.sort_values('year').reset_index(drop=True)
        # 2018 (4 obs) / 2019 (5 obs) 的 σ=0 → 零方差剔除
        assert np.isnan(out.loc[3, 'z_score']) and np.isnan(out.loc[4, 'z_score'])
        assert int(out.loc[3, 'zero_var_flag']) == 1
        assert int(out.loc[4, 'zero_var_flag']) == 1
        assert int(out.loc[0, 'zero_var_flag']) == 0  # σ=NaN: 数据不足, 非剔除
        # 年度输入无 quarter → stock_quarter_used 全 NaN (Step 8 补列)
        assert out['stock_quarter_used'].isna().all()


# ─────────────────────────────────────────────────────────────────────────────
# 守卫: 业务模块路径存在 (防文件被移动后测试空转)
# ─────────────────────────────────────────────────────────────────────────────

def test_module_under_pipeline_panel():
    import news_process.pipeline.panel.risk_taking_outcomes as m
    parts = Path(m.__file__).parts
    assert parts[-3:] == ('pipeline', 'panel', 'risk_taking_outcomes.py')
