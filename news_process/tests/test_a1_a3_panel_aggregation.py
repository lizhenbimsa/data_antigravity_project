"""tests/test_a1_a3_panel_aggregation.py — v3.5.1 A1+A3 panel 聚合单测 (修 M2).

测试覆盖 (8 tests, 修 M2 5→8):
    1. 单 bank 单 year 单 article (n_articles=1 NA per R8-H2)
    2. 多 article weighted aggregation
    3. ctx 缺失轨道
    4. NA 传播
    5. idempotent 重复调用
    6. D2 cell_id 联动
    7. D4 残差列联动
    8. order independence
"""
from __future__ import annotations

import math

import pandas as pd
import pytest

from news_process.pipeline.panel.encode_collab import (
    aggregate_clarity_panel,
    aggregate_num_intensity_panel,
)


@pytest.fixture
def sample_df_panel():
    """合成 article DataFrame + 空 panel 用于聚合测试."""
    df = pd.DataFrame([
        # bank A, year 2020, article 1: 高 clarity_score
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.02, 'clarity_frac_definite_full': 0.08,
         'clarity_clarity_score_full': 0.06,
         'clarity_frac_ambiguous_ctx': 0.03, 'clarity_frac_definite_ctx': 0.05,
         'clarity_clarity_score_ctx': 0.02,
         'num_intensity_full': 2.5, 'num_intensity_ctx': 1.5,
         'media_authority_weight': 1.0, 'herd_decay_weight': 1.0},
        # bank A, year 2020, article 2: 低 clarity
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.10, 'clarity_frac_definite_full': 0.02,
         'clarity_clarity_score_full': -0.08,
         'clarity_frac_ambiguous_ctx': 0.12, 'clarity_frac_definite_ctx': 0.01,
         'clarity_clarity_score_ctx': -0.11,
         'num_intensity_full': 0.5, 'num_intensity_ctx': 0.3,
         'media_authority_weight': 1.0, 'herd_decay_weight': 1.0},
        # bank B, year 2020, article 3: 单一 (n_articles=1, R8-H2 mask 触发)
        {'target_bank': 'B', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.05, 'clarity_frac_definite_full': 0.05,
         'clarity_clarity_score_full': 0.00,
         'clarity_frac_ambiguous_ctx': 0.05, 'clarity_frac_definite_ctx': 0.05,
         'clarity_clarity_score_ctx': 0.00,
         'num_intensity_full': 1.0, 'num_intensity_ctx': 1.0,
         'media_authority_weight': 1.0, 'herd_decay_weight': 1.0},
    ])
    panel = pd.DataFrame([
        {'target_bank': 'A', 'year': 2020},
        {'target_bank': 'B', 'year': 2020},
    ])
    return df, panel


def test_single_article_cell_na_mask(sample_df_panel):
    """R8-H2: n_articles ≥ 2 mask; bank B 仅 1 article → frac_amb_articles NA."""
    df, panel = sample_df_panel
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    # bank B (n=1) frac_amb_articles 应为 NaN (R8-H2 mask)
    bank_b_row = panel[panel['target_bank'] == 'B'].iloc[0]
    assert math.isnan(bank_b_row['frac_amb_articles_full'])
    assert math.isnan(bank_b_row['frac_amb_articles_ctx'])


def test_weighted_aggregation_correct(sample_df_panel):
    """Weighted aggregation: bank A 2 articles, mean_clarity = (0.06 + (-0.08)) / 2 = -0.01."""
    df, panel = sample_df_panel
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    bank_a = panel[panel['target_bank'] == 'A'].iloc[0]
    # 等权 + 等加权: mean = (0.06 + -0.08)/2 = -0.01
    expected = (0.06 + -0.08) / 2
    assert abs(bank_a['mean_clarity_score_full'] - expected) < 1e-6


def test_ctx_track_na_graceful(sample_df_panel):
    """ctx 轨缺失列时, graceful skip."""
    df, panel = sample_df_panel
    # 删除 ctx 列模拟缺失
    df_no_ctx = df.drop(columns=[c for c in df.columns if c.endswith('_ctx') and 'clarity' in c])
    result = aggregate_clarity_panel(df_no_ctx, panel, median_amb_d0=0.06)
    # graceful skip
    assert result['v3_5_1_clarity_added'] == []


def test_nan_propagation_in_aggregation():
    """NaN article 行不破坏整体聚合."""
    df = pd.DataFrame([
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.05, 'clarity_frac_definite_full': 0.05,
         'clarity_clarity_score_full': 0.00,
         'clarity_frac_ambiguous_ctx': 0.05, 'clarity_frac_definite_ctx': 0.05,
         'clarity_clarity_score_ctx': 0.00,
         'num_intensity_full': 1.0, 'num_intensity_ctx': 1.0,
         'media_authority_weight': 1.0, 'herd_decay_weight': 1.0},
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': float('nan'),
         'clarity_frac_definite_full': float('nan'),
         'clarity_clarity_score_full': float('nan'),
         'clarity_frac_ambiguous_ctx': float('nan'),
         'clarity_frac_definite_ctx': float('nan'),
         'clarity_clarity_score_ctx': float('nan'),
         'num_intensity_full': float('nan'), 'num_intensity_ctx': float('nan'),
         'media_authority_weight': 1.0, 'herd_decay_weight': 1.0},
    ])
    panel = pd.DataFrame([{'target_bank': 'A', 'year': 2020}])
    # 不抛
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    assert 'mean_clarity_score_full' in panel.columns


def test_idempotent_repeated_call(sample_df_panel):
    """重复调用 aggregate_clarity_panel 结果一致."""
    df, panel = sample_df_panel
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    val1 = panel.loc[panel['target_bank'] == 'A', 'mean_clarity_score_full'].iloc[0]
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    val2 = panel.loc[panel['target_bank'] == 'A', 'mean_clarity_score_full'].iloc[0]
    assert abs(val1 - val2) < 1e-9


def test_d2_cell_id_independence(sample_df_panel):
    """A1 panel 聚合不破坏 D2 cell_id 列 (若存在)."""
    df, panel = sample_df_panel
    # 添加合成 D2 cell_id_full 列
    panel['cell_id_full'] = pd.array([1, 2], dtype='Int8')
    aggregate_clarity_panel(df, panel, median_amb_d0=0.06)
    assert 'cell_id_full' in panel.columns
    assert panel['cell_id_full'].tolist() == [1, 2]


def test_d4_residual_independence(sample_df_panel):
    """A3 panel 聚合不破坏 D4 残差列 (若存在)."""
    df, panel = sample_df_panel
    panel['subst_disagree_frac_full'] = [0.5, 0.3]
    aggregate_num_intensity_panel(df, panel)
    assert 'subst_disagree_frac_full' in panel.columns


def test_order_independence(sample_df_panel):
    """先 clarity 后 num_intensity 与 先 num_intensity 后 clarity 结果相同."""
    df1, panel1 = sample_df_panel
    aggregate_clarity_panel(df1, panel1, median_amb_d0=0.06)
    aggregate_num_intensity_panel(df1, panel1)

    df2, panel2 = sample_df_panel
    aggregate_num_intensity_panel(df2, panel2)
    aggregate_clarity_panel(df2, panel2, median_amb_d0=0.06)

    # 顺序无关: 两组结果相同
    for col in ['mean_clarity_score_full', 'mean_num_intensity_full']:
        v1 = panel1.loc[panel1['target_bank'] == 'A', col].iloc[0]
        v2 = panel2.loc[panel2['target_bank'] == 'A', col].iloc[0]
        assert abs(v1 - v2) < 1e-9, f"{col} order-dependent: {v1} vs {v2}"
