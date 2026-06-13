"""tests/test_iv_extensions.py — IV 扩展族引擎单元测试 (2026-06-13)

覆盖 pipeline/panel/iv_extensions.py 三引擎:
  1. compute_peer_loo_iv     — 同组×年 LOO 数学 / min_peers 门槛 / 'other' 拒绝 / _lag1
  2. compute_bartik_shift_iv — share 复用 / shift LOO 自我剔除 / value_map /
                               NaN 传播 / 前视掩码
  3. compute_outlet_composition_iv — 基期份额冻结 / outlet-year 银行级 LOO /
                               strict NaN 传播 / 基期无文章 → NaN

全部合成数据手算闭式值, 不触盘、不调外部 API。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.panel.iv_extensions import (  # noqa: E402
    compute_bartik_shift_iv,
    compute_outlet_composition_iv,
    compute_peer_loo_iv,
)

# ============================================================================
# helpers
# ============================================================================

def _mk_panel():
    """3 city 银行 + 1 other 银行 × 2 年 (2017/2018) 的最小面板。"""
    rows = []
    vals = {
        ('A', 2017): 1.0, ('B', 2017): 2.0, ('C', 2017): 3.0,
        ('A', 2018): 4.0, ('B', 2018): 5.0, ('C', 2018): 6.0,
        ('X', 2017): 9.0, ('X', 2018): 9.0,
    }
    for (bank, year), v in vals.items():
        rows.append({
            'target_bank': bank, 'year': year,
            'bank_type': 'other' if bank == 'X' else 'city',
            'x': v,
        })
    return pd.DataFrame(rows)


# ============================================================================
# 1. compute_peer_loo_iv
# ============================================================================

class TestPeerLooIV:
    def test_loo_math_exact(self):
        panel = compute_peer_loo_iv(_mk_panel(), 'x', 'iv', min_peers=2)
        got = panel.set_index(['target_bank', 'year'])['iv']
        # A@2017 = mean(B,C) = 2.5; B@2017 = mean(A,C) = 2.0; C = 1.5
        assert got[('A', 2017)] == pytest.approx(2.5)
        assert got[('B', 2017)] == pytest.approx(2.0)
        assert got[('C', 2017)] == pytest.approx(1.5)
        assert got[('A', 2018)] == pytest.approx(5.5)

    def test_other_group_rejected(self):
        panel = compute_peer_loo_iv(_mk_panel(), 'x', 'iv', min_peers=2)
        got = panel.set_index(['target_bank', 'year'])['iv']
        assert np.isnan(got[('X', 2017)])
        assert np.isnan(got[('X', 2018)])

    def test_min_peers_threshold(self):
        # 只剩 2 家同组: LOO 后剩 1 < min_peers=2 → NaN
        panel = _mk_panel()
        panel = panel[panel['target_bank'].isin(['A', 'B', 'X'])]
        out = compute_peer_loo_iv(panel, 'x', 'iv', min_peers=2)
        got = out.set_index(['target_bank', 'year'])['iv']
        assert np.isnan(got[('A', 2017)])
        # min_peers=1 时恢复: A 的 LOO = B 的值
        out1 = compute_peer_loo_iv(panel, 'x', 'iv', min_peers=1)
        got1 = out1.set_index(['target_bank', 'year'])['iv']
        assert got1[('A', 2017)] == pytest.approx(2.0)

    def test_own_missing_value_excluded_from_denominator(self):
        # A 自身 x 缺失: 不进分子分母, A 的 LOO 仍 = mean(B,C); B 的 LOO
        # 只剩 C (1 家 < min_peers=2) → NaN
        panel = _mk_panel()
        panel.loc[(panel['target_bank'] == 'A')
                  & (panel['year'] == 2017), 'x'] = np.nan
        out = compute_peer_loo_iv(panel, 'x', 'iv', min_peers=2)
        got = out.set_index(['target_bank', 'year'])['iv']
        assert got[('A', 2017)] == pytest.approx(2.5)
        assert np.isnan(got[('B', 2017)])

    def test_lag1_variant(self):
        panel = compute_peer_loo_iv(_mk_panel(), 'x', 'iv', min_peers=2)
        got = panel.set_index(['target_bank', 'year'])
        # lag1@2018 = LOO@2017; 面板首年 lag1 = NaN
        assert got.loc[('A', 2018), 'iv_lag1'] == pytest.approx(2.5)
        assert np.isnan(got.loc[('A', 2017), 'iv_lag1'])

    def test_missing_column_graceful(self):
        out = compute_peer_loo_iv(_mk_panel(), 'no_such_col', 'iv')
        assert out['iv'].isna().all()
        assert out['iv_lag1'].isna().all()


# ============================================================================
# 2. compute_bartik_shift_iv
# ============================================================================

def _mk_bartik_inputs():
    """2 组 (city/rural) × 2 年; share 列直接挂面板 (复用 7e 形态)。"""
    panel = pd.DataFrame([
        # A: share_city=1.0 share_rural=0.0
        {'target_bank': 'A', 'year': 2017,
         'bartik_type_share_city': 1.0, 'bartik_type_share_rural': 0.0},
        {'target_bank': 'A', 'year': 2018,
         'bartik_type_share_city': 1.0, 'bartik_type_share_rural': 0.0},
        # B: 50/50
        {'target_bank': 'B', 'year': 2017,
         'bartik_type_share_city': 0.5, 'bartik_type_share_rural': 0.5},
        {'target_bank': 'B', 'year': 2018,
         'bartik_type_share_city': 0.5, 'bartik_type_share_rural': 0.5},
        # C: 基期无文章 → share NaN
        {'target_bank': 'C', 'year': 2018,
         'bartik_type_share_city': np.nan, 'bartik_type_share_rural': np.nan},
    ])
    group_map = {'A': 'city', 'B': 'city', 'R1': 'rural', 'R2': 'rural'}
    # 文章级: city 组 2018 = A(0.2, 0.4) + B(0.6); rural 组 2018 = R1(1.0), R2(0.0)
    arts = pd.DataFrame([
        {'target_bank': 'A', 'year': 2018, 's': 0.2},
        {'target_bank': 'A', 'year': 2018, 's': 0.4},
        {'target_bank': 'B', 'year': 2018, 's': 0.6},
        {'target_bank': 'R1', 'year': 2018, 's': 1.0},
        {'target_bank': 'R2', 'year': 2018, 's': 0.0},
        # 2017 基期文章 (shift 同样可算)
        {'target_bank': 'A', 'year': 2017, 's': 0.0},
        {'target_bank': 'B', 'year': 2017, 's': 1.0},
        {'target_bank': 'R1', 'year': 2017, 's': 0.5},
        {'target_bank': 'R2', 'year': 2017, 's': 0.5},
    ])
    return panel, arts, group_map


class TestBartikShiftIV:
    def test_loo_shift_and_share_combination(self):
        panel, arts, gmap = _mk_bartik_inputs()
        out = compute_bartik_shift_iv(
            panel, arts, gmap, 'tst',
            {'_full': 's', '_ctx': None}, base_years=[2017])
        got = out.set_index(['target_bank', 'year'])['bartik_tst_iv_full']
        # A@2018: shift_city^LOO(A) = B 文章均值 = 0.6; share_city=1 → IV=0.6
        assert got[('A', 2018)] == pytest.approx(0.6)
        # B@2018: shift_city^LOO(B) = mean(0.2,0.4)=0.3;
        #          shift_rural^LOO(B) = mean(1.0,0.0)=0.5 → 0.5*0.3+0.5*0.5=0.4
        assert got[('B', 2018)] == pytest.approx(0.4)
        # C: share NaN → IV NaN
        assert np.isnan(got[('C', 2018)])
        # ctx 轨 shift 列为 None → 全 NaN
        assert out['bartik_tst_iv_ctx'].isna().all()

    def test_share_positive_nan_shift_propagates(self):
        panel, arts, gmap = _mk_bartik_inputs()
        # 删光 rural 组 2018 文章 → B (share_rural=0.5>0) 的 rural shift 缺 → IV NaN
        arts2 = arts[~((arts['target_bank'].isin(['R1', 'R2']))
                       & (arts['year'] == 2018))]
        out = compute_bartik_shift_iv(
            panel, arts2, gmap, 'tst', {'_full': 's', '_ctx': None},
            base_years=[2017])
        got = out.set_index(['target_bank', 'year'])['bartik_tst_iv_full']
        assert np.isnan(got[('B', 2018)])
        # A (share_rural=0) 不受 rural shift 缺失影响
        assert got[('A', 2018)] == pytest.approx(0.6)

    def test_pre_base_mask(self):
        panel, arts, gmap = _mk_bartik_inputs()
        out = compute_bartik_shift_iv(
            panel, arts, gmap, 'tst', {'_full': 's', '_ctx': None},
            base_years=[2018])
        got = out.set_index(['target_bank', 'year'])['bartik_tst_iv_full']
        # 2017 行早于基期末年 2018 → NaN
        assert np.isnan(got[('A', 2017)])
        assert np.isnan(got[('B', 2017)])

    def test_value_map_indicator(self):
        panel, _, gmap = _mk_bartik_inputs()
        arts = pd.DataFrame([
            {'target_bank': 'A', 'year': 2018, 'cat': '实质性'},
            {'target_bank': 'B', 'year': 2018, 'cat': '实质性'},
            {'target_bank': 'B', 'year': 2018, 'cat': '象征性'},
            {'target_bank': 'R1', 'year': 2018, 'cat': '实质性'},
            {'target_bank': 'R2', 'year': 2018, 'cat': '其他未映射'},  # → NaN, 不进分母
        ])
        out = compute_bartik_shift_iv(
            panel, arts, gmap, 'tst', {'_full': 'cat', '_ctx': None},
            base_years=[2017],
            value_map={'实质性': 1.0, '象征性': 0.0})
        got = out.set_index(['target_bank', 'year'])['bartik_tst_iv_full']
        # A@2018: city LOO(A) = B 的 (1+0)/2 = 0.5 → share_city=1 → 0.5
        assert got[('A', 2018)] == pytest.approx(0.5)
        # B@2018: city LOO(B) = A 的 1/1 = 1.0; rural LOO(B) = R1 的 1/1 = 1.0
        # (R2 未映射 → 剔除) → 0.5*1 + 0.5*1 = 1.0
        assert got[('B', 2018)] == pytest.approx(1.0)

    def test_missing_share_columns_graceful(self):
        panel = pd.DataFrame([
            {'target_bank': 'A', 'year': 2018},
        ])
        arts = pd.DataFrame([{'target_bank': 'A', 'year': 2018, 's': 1.0}])
        out = compute_bartik_shift_iv(
            panel, arts, {'A': 'city'}, 'tst', {'_full': 's', '_ctx': None},
            base_years=[2017])
        assert out['bartik_tst_iv_full'].isna().all()


# ============================================================================
# 3. compute_outlet_composition_iv
# ============================================================================

def _mk_outlet_inputs():
    panel = pd.DataFrame([
        {'target_bank': 'A', 'year': 2017},
        {'target_bank': 'A', 'year': 2018},
        {'target_bank': 'B', 'year': 2017},
        {'target_bank': 'B', 'year': 2018},
        {'target_bank': 'N', 'year': 2018},   # 基期无文章
    ])
    # 基期 2017: A 被 O1 报 2 篇 + O2 报 2 篇 (share 0.5/0.5); B 被 O1 报 1 篇
    # 2018: O1 报 A 1 篇(v=10) + B 1 篇(v=20); O2 报 B 2 篇(v=30,50)
    arts = pd.DataFrame([
        {'target_bank': 'A', 'year': 2017, 'outlet': 'O1', 'v': 1.0},
        {'target_bank': 'A', 'year': 2017, 'outlet': 'O1', 'v': 1.0},
        {'target_bank': 'A', 'year': 2017, 'outlet': 'O2', 'v': 1.0},
        {'target_bank': 'A', 'year': 2017, 'outlet': 'O2', 'v': 1.0},
        {'target_bank': 'B', 'year': 2017, 'outlet': 'O1', 'v': 5.0},
        {'target_bank': 'A', 'year': 2018, 'outlet': 'O1', 'v': 10.0},
        {'target_bank': 'B', 'year': 2018, 'outlet': 'O1', 'v': 20.0},
        {'target_bank': 'B', 'year': 2018, 'outlet': 'O2', 'v': 30.0},
        {'target_bank': 'B', 'year': 2018, 'outlet': 'O2', 'v': 50.0},
        {'target_bank': 'N', 'year': 2018, 'outlet': 'O1', 'v': 99.0},
    ])
    shift = {'_full': arts['v'], '_ctx': None}
    return panel, arts, shift


class TestOutletCompositionIV:
    def test_loo_excludes_focal_bank_articles(self):
        panel, arts, shift = _mk_outlet_inputs()
        out = compute_outlet_composition_iv(
            panel, arts, shift, 'oiv', base_years=[2017], outlet_col='outlet')
        got = out.set_index(['target_bank', 'year'])['oiv_full']
        # A@2018: O1 LOO(A) = mean(B 20, N 99) = 59.5; O2 LOO(A) = mean(30,50)=40
        #   → 0.5*59.5 + 0.5*40 = 49.75
        assert got[('A', 2018)] == pytest.approx(49.75)
        # B@2018: share = {O1: 1.0}; O1 LOO(B) = mean(A 10, N 99) = 54.5
        assert got[('B', 2018)] == pytest.approx(54.5)

    def test_no_base_articles_is_nan(self):
        panel, arts, shift = _mk_outlet_inputs()
        out = compute_outlet_composition_iv(
            panel, arts, shift, 'oiv', base_years=[2017], outlet_col='outlet')
        got = out.set_index(['target_bank', 'year'])['oiv_full']
        assert np.isnan(got[('N', 2018)])

    def test_strict_nan_propagation_when_outlet_silent(self):
        panel, arts, shift = _mk_outlet_inputs()
        # 删除 O2 的 2018 全部文章 → A 的 O2 项 style 缺 → A@2018 NaN
        keep = ~((arts['outlet'] == 'O2') & (arts['year'] == 2018))
        arts2 = arts[keep]
        shift2 = {'_full': arts2['v'], '_ctx': None}
        out = compute_outlet_composition_iv(
            panel, arts2, shift2, 'oiv', base_years=[2017], outlet_col='outlet')
        got = out.set_index(['target_bank', 'year'])['oiv_full']
        assert np.isnan(got[('A', 2018)])
        # B (share 全在 O1) 不受影响
        assert got[('B', 2018)] == pytest.approx(54.5)

    def test_pre_base_mask_and_ctx_none(self):
        panel, arts, shift = _mk_outlet_inputs()
        out = compute_outlet_composition_iv(
            panel, arts, shift, 'oiv', base_years=[2018], outlet_col='outlet')
        got = out.set_index(['target_bank', 'year'])['oiv_full']
        assert np.isnan(got[('A', 2017)])
        assert out['oiv_ctx'].isna().all()

    def test_missing_outlet_col_graceful(self):
        panel, arts, shift = _mk_outlet_inputs()
        out = compute_outlet_composition_iv(
            panel, arts, shift, 'oiv', base_years=[2017],
            outlet_col='不存在的列')
        assert out['oiv_full'].isna().all()


# ============================================================================
# 4. 编排入口烟雾测试 (列名契约)
# ============================================================================

class TestComputeIvExtensionsSmoke:
    def test_orchestrator_produces_contract_columns(self):
        from news_process.pipeline.panel.iv_extensions import compute_iv_extensions
        panel = _mk_panel().rename(columns={'x': 'attention_index_full'})
        panel['sub_frac'] = 0.5
        panel['tech_frac'] = 0.5
        panel['collab_frac'] = 0.5
        panel['benefit_mean_full'] = 0.1
        # ctx 轨内生孪生 (lpeer_* ctx LOO 工具的源列; 2026-06-13)
        panel['attention_index_ctx'] = 0.4
        panel['sub_frac_sc'] = 0.45
        panel['tech_frac_lc'] = 0.55
        panel['collab_frac_cm'] = 0.5
        panel['benefit_mean_ctx'] = 0.12
        panel['bank_zone'] = '长三角'
        # 7e share 列 (city 单组)
        panel['bartik_type_share_city'] = 1.0
        arts = pd.DataFrame([
            {'target_bank': 'A', 'year': 2017, '媒体(中文)': 'O1',
             'llm_vote_score_full': 0.5, 'llm_vote_score_ctx': 0.5,
             'fintech_intensity_score_full': 0.5,
             'fintech_intensity_score_ctx': 0.5,
             'innovation_substantiveness_full': '实质性',
             'innovation_substantiveness_ctx': '实质性',
             'innovation_collab_mode_full': '外部协同',
             'innovation_collab_mode_ctx': '自主研发',
             'clarity_clarity_score_full': 0.2,
             'clarity_clarity_score_ctx': 0.3},
            {'target_bank': 'B', 'year': 2018, '媒体(中文)': 'O1',
             'llm_vote_score_full': -0.5, 'llm_vote_score_ctx': -0.5,
             'fintech_intensity_score_full': 0.7,
             'fintech_intensity_score_ctx': 0.7,
             'innovation_substantiveness_full': '象征性',
             'innovation_substantiveness_ctx': '象征性',
             'innovation_collab_mode_full': '自主研发',
             'innovation_collab_mode_ctx': '外部协同',
             'clarity_clarity_score_full': -0.1,
             'clarity_clarity_score_ctx': 0.0},
        ])
        out = compute_iv_extensions(
            panel, arts, {'A': 'city', 'B': 'city', 'C': 'city'},
            base_years=[2017])
        expected_cols = [
            'leave_one_out_peer_attention_iv',
            'leave_one_out_peer_attention_iv_lag1',
            'bartik_attention_iv', 'bartik_attention_iv_full',
            'bartik_attention_iv_ctx',
            'leave_one_out_peer_subst_iv',
            'bartik_subst_iv_full', 'bartik_subst_iv_ctx',
            'leave_one_out_peer_locus_iv',
            'leave_one_out_peer_collab_iv',
            'bartik_collab_iv_full', 'bartik_collab_iv_ctx',
            'leave_one_out_peer_benefit_iv',
            'zone_leave1out_benefit_iv',
            'outlet_disp_exposure_iv_full', 'outlet_disp_exposure_iv_ctx',
            'outlet_style_clarity_iv_full', 'outlet_style_clarity_iv_ctx',
            # ctx 轨同业 LOO 工具镜像 (lpeer_* 前缀; 2026-06-13 终审落地) +
            # _lag1 滞后变体 (compute_peer_loo_iv add_lag1=True 默认产出)
            'lpeer_attention_iv_ctx', 'lpeer_attention_iv_ctx_lag1',
            'lpeer_subst_iv_ctx', 'lpeer_subst_iv_ctx_lag1',
            'lpeer_locus_iv_ctx', 'lpeer_locus_iv_ctx_lag1',
            'lpeer_collab_iv_ctx', 'lpeer_collab_iv_ctx_lag1',
            'lpeer_benefit_iv_ctx', 'lpeer_benefit_iv_ctx_lag1',
        ]
        missing = [c for c in expected_cols if c not in out.columns]
        assert not missing, f"编排入口缺契约列: {missing}"
        # 行数不变 (全程 merge-based)
        assert len(out) == len(panel)
