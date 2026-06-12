"""test_49_risk_taking_outcomes — Stage 49 金融结果指标的单元测试.

audit-fixes 2026-05-29 (M3): 此前 Stage 49
(pipeline/panel/risk_taking_outcomes.py, 9 函数, 455 LOC) 仅有 DAG 注册 / config
predicate 层测试, 核心金融数学 (Z-score / NPL formation / LLP raw ratio / 5y
rolling sigma) 零功能覆盖。本文件用手算黄金值断言这些纯 pandas 函数, 防止
符号 / 分子分母 / 滚动窗口 / lag 回归静默污染 P10/P11 论文的结果变量。

全部为纯内存 DataFrame, 无 LLM/IO/网络, 确定性。
"""
import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel.risk_taking_outcomes import (
    compute_llp_discretion,
    compute_npl_formation,
    compute_sigma_roa_rolling,
    compute_z_score,
)


class TestComputeZScore:
    """Z = (ROA + CAR) / sigma_roa_5y_rolling; sigma NaN/≈0 → NaN.

    fix(omni-g-risk-06, 2026-06-11): compute_z_score 现返回
    (z_score, zero_var_flag) 两元组, 断言已同步更新。
    """

    def test_basic_golden_value(self):
        df = pd.DataFrame({
            'roa': [1.0],
            'capital_adequacy_ratio': [10.0],
            'sigma_roa_5y_rolling': [2.0],
        })
        z, flag = compute_z_score(df)
        assert z.iloc[0] == pytest.approx((1.0 + 10.0) / 2.0)  # 5.5
        assert int(flag.iloc[0]) == 0

    def test_nan_sigma_yields_nan(self):
        df = pd.DataFrame({
            'roa': [1.0], 'capital_adequacy_ratio': [10.0],
            'sigma_roa_5y_rolling': [np.nan],
        })
        z, flag = compute_z_score(df)
        assert np.isnan(z.iloc[0])
        # 数据缺失 (σ=NaN) 不是零方差剔除 → flag=0
        assert int(flag.iloc[0]) == 0

    def test_zero_sigma_yields_nan(self):
        df = pd.DataFrame({
            'roa': [1.0], 'capital_adequacy_ratio': [10.0],
            'sigma_roa_5y_rolling': [0.0],
        })
        z, flag = compute_z_score(df)
        assert np.isnan(z.iloc[0])
        # fix(omni-g-risk-06): σ≈0 零方差剔除须被指示列标记
        assert int(flag.iloc[0]) == 1

    def test_sign_preserved(self):
        # 负 ROA + 小 CAR → 负 numerator → 负 Z (符号回归守卫)
        df = pd.DataFrame({
            'roa': [-5.0], 'capital_adequacy_ratio': [1.0],
            'sigma_roa_5y_rolling': [2.0],
        })
        z, _ = compute_z_score(df)
        assert z.iloc[0] == pytest.approx((-5.0 + 1.0) / 2.0)  # -2.0


class TestComputeNplFormation:
    """NPL formation = ((NPL_t - NPL_{t-1}) + writeoffs) / Loans_{t-1}."""

    def test_lag_and_writeoffs_golden(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'npl_balance': [100.0, 130.0],
            'total_loans': [1000.0, 1100.0],
            'loan_writeoffs': [np.nan, 10.0],
        })
        npl, imputed = compute_npl_formation(df)
        npl = npl.sort_index()
        imputed = imputed.sort_index()
        # 2017: lag1 NaN → NaN
        assert np.isnan(npl.iloc[0])
        # 2018: ((130-100)+10)/1000 = 0.04
        assert npl.iloc[1] == pytest.approx(0.04)
        # writeoffs_imputed: 2017 缺失→1, 2018 有值→0
        assert int(imputed.iloc[0]) == 1
        assert int(imputed.iloc[1]) == 0

    def test_missing_writeoffs_column_imputes_zero(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'npl_balance': [100.0, 130.0],
            'total_loans': [1000.0, 1100.0],
        })
        npl, imputed = compute_npl_formation(df)
        assert (imputed == 1).all()  # 整列 imputed
        # 2018: (130-100)/1000 = 0.03 (writeoffs imputed 0)
        assert npl.sort_index().iloc[1] == pytest.approx(0.03)

    def test_per_bank_lag_isolation(self):
        # 不同银行的 lag 不应串组
        df = pd.DataFrame({
            'target_bank': ['A', 'B', 'A', 'B'],
            'year': [2017, 2017, 2018, 2018],
            'npl_balance': [100.0, 200.0, 130.0, 260.0],
            'total_loans': [1000.0, 2000.0, 1100.0, 2200.0],
        })
        npl, _ = compute_npl_formation(df)
        df2 = df.sort_values(['target_bank', 'year']).reset_index(drop=True)
        npl = compute_npl_formation(df2)[0].reset_index(drop=True)
        # A 2018: (130-100)/1000 = 0.03 ; B 2018: (260-200)/2000 = 0.03
        assert npl.iloc[1] == pytest.approx(0.03)  # A/2018
        assert npl.iloc[3] == pytest.approx(0.03)  # B/2018
        assert np.isnan(npl.iloc[0]) and np.isnan(npl.iloc[2])  # 各组首年 NaN


class TestComputeLlpDiscretion:
    """LLP raw ratio = LLP_t / Loans_{t-1}; lag 缺失/≈0 → NaN.

    fix(omni-g-risk-05, 2026-06-11): 分母从当期 total_loans 改为日历 t-1 的
    Loans_{t-1} (与 docstring BW2012 Eq.(2) LHS 规格一致), 旧断言锁的是
    错误的当期分母行为, 已更新。
    """

    def test_basic_ratio_lagged_denominator(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'loan_loss_provision': [15.0, 20.0],
            'total_loans': [1000.0, 1100.0],
        })
        out = compute_llp_discretion(df)
        # 2017: 无 Loans_{t-1} → NaN
        assert np.isnan(out.iloc[0])
        # 2018: LLP_2018 / Loans_2017 = 20/1000 = 0.02 (非 20/1100)
        assert out.iloc[1] == pytest.approx(0.02)

    def test_zero_lag_loans_nan(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'loan_loss_provision': [15.0, 20.0],
            'total_loans': [0.0, 1100.0],
        })
        # 2018 的 Loans_{t-1}=0 → NaN
        assert np.isnan(compute_llp_discretion(df).iloc[1])

    def test_missing_llp_column_nan(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2018],
            'total_loans': [1000.0, 1100.0],
        })
        assert compute_llp_discretion(df).isna().all()


class TestComputeSigmaRoaRolling:
    """5y rolling std(ROA) per bank, window=5 min_periods=4."""

    def test_min_periods_guard(self):
        # 3 obs < min_periods=4 → 全 NaN
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'A'],
            'year': [2017, 2018, 2019],
            'roa': [1.0, 2.0, 3.0],
        })
        assert compute_sigma_roa_rolling(df).isna().all()

    def test_rolling_std_golden(self):
        df = pd.DataFrame({
            'target_bank': ['A'] * 5,
            'year': [2015, 2016, 2017, 2018, 2019],
            'roa': [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        out = compute_sigma_roa_rolling(df).sort_index()
        # 第 4 行 (4 obs [1,2,3,4]) 达 min_periods → ddof=1 std
        assert out.iloc[3] == pytest.approx(np.std([1, 2, 3, 4], ddof=1))
        # 第 5 行 (5 obs [1..5]) → ddof=1 std = sqrt(2.5)
        assert out.iloc[4] == pytest.approx(np.std([1, 2, 3, 4, 5], ddof=1))

    def test_per_bank_isolation(self):
        # 两家银行各自滚动, 不串组 (各 5 obs)
        df = pd.DataFrame({
            'target_bank': ['A'] * 5 + ['B'] * 5,
            'year': list(range(2015, 2020)) * 2,
            'roa': [1.0, 2.0, 3.0, 4.0, 5.0] + [10.0, 10.0, 10.0, 10.0, 10.0],
        })
        out = compute_sigma_roa_rolling(df)
        df_sorted = df.sort_values(['target_bank', 'year']).reset_index(drop=True)
        out = compute_sigma_roa_rolling(df_sorted).reset_index(drop=True)
        # B 全 10.0 → std == 0 (常数), 不被 A 的方差污染
        assert out.iloc[9] == pytest.approx(0.0)
