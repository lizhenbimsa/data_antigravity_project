"""v3.5.0 D4 双轨残差信号 (dual-track residual signals) 单元测试。

依据 v3.5.0 D4 dual-track residual signals §2.3 / §4.1 (文档已随 docs/ 删除):
    12 个测试覆盖:
        - 9 个文章级布尔列 (3 维度 × 3 信号: disagree/freerider/quietworker)
        - plan §2.3.2 的不变量 (i)(ii)(iii):
            (i)  freerider + quietworker ≤ 1 (互斥)
            (ii) freerider + quietworker == disagree (定义恒等)
            (iii) 任一轨为 NaN → 三个指示列全 False (而非 NaN)
        - 18 个面板级列 (3 维度 × 3 信号 × 2 度量 [frac, count])
        - 小样本限制: panel n_articles < 5 → *_frac 强制 NA
        - ctx coverage 自适应警告 + d4_data_quality_flag str 列 (F6 + C-NEW-3)
        - 缺失轨列时优雅跳过
        - 跨维度独立性 (subst/locus/collab 派生互不影响)

依赖: 合成小型 fixture.
"""
from __future__ import annotations

import json

import pandas as pd
import pytest

from news_process.pipeline.panel.encode_collab import (
    DIMS_D4,
    aggregate_d4_panel,
    derive_residual_signals,
)


def _make_dual_track_df(rows: list[dict]) -> pd.DataFrame:
    """每个 row dict 可覆盖任意维度/轨道的值。

    生产约定: 列名用 target_bank (而非 'bank'), 见 encode.py:221。
    """
    base = {
        'innovation_substantiveness_full': '实质性',
        'innovation_substantiveness_ctx':  '实质性',
        'innovation_locus_full':           '底层技术',
        'innovation_locus_ctx':            '底层技术',
        'innovation_collab_mode_full':     '自主研发',
        'innovation_collab_mode_ctx':      '自主研发',
        'target_bank': 'B1',
        'year': 2020,
    }
    return pd.DataFrame([{**base, **r} for r in rows])


# ----------------------------------------------------------------------------
# Test 1: 新增 9 个文章级列
# ----------------------------------------------------------------------------

def test_derive_residual_adds_9_article_columns():
    df = _make_dual_track_df([{}, {}])
    cols = derive_residual_signals(df)
    expected = [f'{d}_{s}' for d, _, _, _ in DIMS_D4
                for s in ('disagree', 'freerider', 'quietworker')]
    assert sorted(cols) == sorted(expected)
    for col in expected:
        assert col in df.columns


# ----------------------------------------------------------------------------
# Test 2: 不变量 (i) — freerider + quietworker ≤ 1 (互斥)
# ----------------------------------------------------------------------------

def test_invariant_i_freerider_quietworker_mutually_exclusive():
    """对任意文章 a、任意维度 d: freerider[a,d] + quietworker[a,d] ≤ 1 (互斥)。"""
    # 构造多样化 df, 每个维度覆盖 4 种情形
    df = _make_dual_track_df([
        {},  # 全 baseline = 两轨一致, disagree=False, 两信号均 False
        {'innovation_substantiveness_full': '象征性'},  # full=对照值, ctx=baseline → quietworker
        {'innovation_substantiveness_ctx': '象征性'},   # full=baseline, ctx=对照值 → freerider
        {'innovation_substantiveness_full': '象征性',
         'innovation_substantiveness_ctx': '象征性'},  # full=ctx=对照值, 两信号均 False
    ])
    derive_residual_signals(df)
    for dim_short, _, _, _ in DIMS_D4:
        violations = ((df[f'{dim_short}_freerider'].astype(int) +
                       df[f'{dim_short}_quietworker'].astype(int)) > 1).sum()
        assert violations == 0, (
            f"Invariant (i) failed for dim={dim_short}: {violations} rows with both True"
        )


# ----------------------------------------------------------------------------
# Test 3: 不变量 (ii) — freerider + quietworker == disagree
# ----------------------------------------------------------------------------

def test_invariant_ii_freerider_plus_quietworker_equals_disagree():
    """∀ article: freerider + quietworker == disagree (两轨均有效时)。"""
    df = _make_dual_track_df([
        {},  # 两轨一致: 全 False
        {'innovation_substantiveness_full': '象征性'},  # quietworker (disagree)
        {'innovation_substantiveness_ctx':  '象征性'},  # freerider (disagree)
        {'innovation_locus_full': '应用场景'},  # quietworker (locus 维度)
    ])
    derive_residual_signals(df)
    for dim_short, _, _, _ in DIMS_D4:
        lhs = df[f'{dim_short}_freerider'].astype(int) + df[f'{dim_short}_quietworker'].astype(int)
        rhs = df[f'{dim_short}_disagree'].astype(int)
        assert (lhs == rhs).all(), (
            f"Invariant (ii) failed for dim={dim_short}: free+quiet != disagree"
        )


# ----------------------------------------------------------------------------
# Test 4: 不变量 (iii) — NaN 传播 → 3 个指示列全 False
# ----------------------------------------------------------------------------

@pytest.mark.parametrize('nan_field', [
    'innovation_substantiveness_full',
    'innovation_substantiveness_ctx',
    'innovation_locus_full',
    'innovation_locus_ctx',
    'innovation_collab_mode_full',
    'innovation_collab_mode_ctx',
])
def test_invariant_iii_nan_track_yields_false_indicators(nan_field):
    """任一维度的 full 或 ctx 为 NaN → 该维度 3 个指示列全 False (而非 NaN)。

    CR-21: 参数化覆盖 6 个 轨道×维度 组合各自的 NaN 情形。
    强化早期单行测试 (旧版漏掉轨道特定的 bug)。
    """
    df = _make_dual_track_df([{nan_field: None}])
    derive_residual_signals(df)

    # 找出 NaN 落在哪个维度 (如 'innovation_substantiveness_full' → 'subst')
    dim_short = {
        'innovation_substantiveness': 'subst',
        'innovation_locus': 'locus',
        'innovation_collab_mode': 'collab',
    }[nan_field.rsplit('_', 1)[0]]

    # 该维度的 3 个指示列必须全 False (不能是 NaN, 也不能是 True)
    assert df[f'{dim_short}_disagree'].iloc[0] == False, \
        f"{dim_short}_disagree should be False when {nan_field} is NaN"
    assert df[f'{dim_short}_freerider'].iloc[0] == False, \
        f"{dim_short}_freerider should be False when {nan_field} is NaN"
    assert df[f'{dim_short}_quietworker'].iloc[0] == False, \
        f"{dim_short}_quietworker should be False when {nan_field} is NaN"


def test_invariant_iii_both_tracks_nan_all_false():
    """full 与 ctx 同时为 NaN 时, 3 个指示列仍须全 False (而非 NaN)。"""
    df = _make_dual_track_df([{
        'innovation_substantiveness_full': None,
        'innovation_substantiveness_ctx': None,
    }])
    derive_residual_signals(df)
    assert df['subst_disagree'].iloc[0] == False
    assert df['subst_freerider'].iloc[0] == False
    assert df['subst_quietworker'].iloc[0] == False


# ----------------------------------------------------------------------------
# Test 5: disagree 定义 — 两轨均有效且 full != ctx
# ----------------------------------------------------------------------------

def test_disagree_definition():
    df = _make_dual_track_df([
        {},  # 两轨一致
        {'innovation_locus_ctx': '应用场景'},  # full=baseline, ctx=对照值 → disagree
        {'innovation_locus_full': '应用场景'},  # full=对照值, ctx=baseline → disagree
    ])
    derive_residual_signals(df)
    assert df['locus_disagree'].tolist() == [False, True, True]


# ----------------------------------------------------------------------------
# Test 6: 跨维度独立性 (subst / locus / collab 各自独立派生)
# ----------------------------------------------------------------------------

def test_cross_dim_independence():
    """改动 subst 轨不应影响 locus/collab 的指示列。"""
    df = _make_dual_track_df([{'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    # 只有 subst 维度应出信号; locus/collab 应全 False
    assert df['subst_quietworker'].iloc[0] == True
    assert df['locus_disagree'].iloc[0] == False
    assert df['locus_freerider'].iloc[0] == False
    assert df['locus_quietworker'].iloc[0] == False
    assert df['collab_disagree'].iloc[0] == False


# ----------------------------------------------------------------------------
# Test 7-8: 面板聚合 — 18 列 (3 维度 × 3 信号 × 2 度量)
# ----------------------------------------------------------------------------

def test_panel_18_columns_added():
    """aggregate_d4_panel 新增 9 个 *_frac + 9 个 n_articles_* = 18 列。"""
    df = _make_dual_track_df([{}, {}, {'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    for dim_short, _, _, _ in DIMS_D4:
        for signal in ('disagree', 'freerider', 'quietworker'):
            assert f'{dim_short}_{signal}_frac' in panel.columns
            assert f'n_articles_{dim_short}_{signal}' in panel.columns


def test_panel_count_equals_sum_per_bank_year():
    """n_articles_subst_disagree == 每个 bank-year 内 subst_disagree 之和。

    注意: 每个 bank-year 需 ≥ 5 篇文章以避开小样本限制
    (panel n_articles < 5 → *_frac 强制 NA, 见 test_small_sample_restriction_forces_frac_nan)。
    """
    df = _make_dual_track_df([
        {},  # 两轨一致
        {'innovation_substantiveness_full': '象征性'},  # quietworker → disagree
        {'innovation_substantiveness_ctx':  '象征性'},  # freerider → disagree
        {},  # 两轨一致 (凑满 ≥5 篇的填充行)
        {},  # 填充行
        {},  # 填充行
    ])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    # B1 2020 共 6 篇文章, 2 篇 disagree → frac = 2/6
    row = panel[(panel['target_bank'] == 'B1') & (panel['year'] == 2020)].iloc[0]
    assert row['n_articles_subst_disagree'] == 2
    assert row['subst_disagree_frac'] == pytest.approx(2 / 6)


# ----------------------------------------------------------------------------
# Test 9: 小样本限制 — n_articles < 5 → *_frac 强制 NA
# ----------------------------------------------------------------------------

def test_small_sample_restriction_forces_frac_nan():
    """panel n_articles < 5 → *_frac 列强制置 pd.NA。"""
    # 构造 B1 仅 2 篇文章的 df (小样本)
    df = _make_dual_track_df([{}, {'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    # B1 2020 仅 2 篇 < 5 → frac 强制 NA
    row = panel[(panel['target_bank'] == 'B1') & (panel['year'] == 2020)].iloc[0]
    assert pd.isna(row['subst_freerider_frac'])
    assert pd.isna(row['subst_quietworker_frac'])


# ----------------------------------------------------------------------------
# Test 10: d4_data_quality_flag str 列 (F6)
# ----------------------------------------------------------------------------

def test_d4_data_quality_flag_col_present():
    """aggregate_d4_panel 必定新增 d4_data_quality_flag str 列。"""
    df = _make_dual_track_df([{}, {}])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    assert 'd4_data_quality_flag' in panel.columns
    assert panel['d4_data_quality_flag'].iloc[0] in ('ok', 'insufficient')


# ----------------------------------------------------------------------------
# Test 11: ctx coverage 自适应 — baseline 文件加载 + threshold 触发
# ----------------------------------------------------------------------------

def test_ctx_coverage_baseline_adaptive_threshold(tmp_path):
    """ctx coverage < (baseline 均值 - 2σ) → quality_flag='insufficient'。"""
    # 构造大部分 ctx 为 NaN 的 df (低覆盖率)
    rows = [{}] * 2 + [{'innovation_collab_mode_ctx': None}] * 18
    df = _make_dual_track_df(rows)
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')

    # Baseline: mean=0.74, std=0.05 → 阈值 = 0.64
    # 实际 coverage = 2/20 = 0.1 → 远低于阈值 → 'insufficient'
    baseline_path = tmp_path / 'v3_4_0_ctx_coverage_baseline.json'
    baseline_path.write_text(json.dumps({'mean': 0.74, 'std': 0.05}), encoding='utf-8')

    aggregate_d4_panel(df, panel, ctx_baseline_path=str(baseline_path))
    assert panel['d4_data_quality_flag'].iloc[0] == 'insufficient'


# ----------------------------------------------------------------------------
# Test 12: 缺失轨列 → 优雅跳过
# ----------------------------------------------------------------------------

def test_missing_track_column_graceful_skip():
    """如 innovation_locus_ctx 列缺失, 仅该维度的残差信号被跳过。"""
    df = _make_dual_track_df([{}])
    df = df.drop(columns=['innovation_locus_ctx'])
    cols_added = derive_residual_signals(df)
    # subst + collab 指示列照常新增; locus_* 不新增 (缺列跳过)
    assert 'subst_disagree' in cols_added
    assert 'collab_disagree' in cols_added
    assert 'locus_disagree' not in cols_added
