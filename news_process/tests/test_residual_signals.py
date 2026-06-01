"""v3.5.0 D4 dual-track residual signals unit tests.

Per v3.5.0 D4 dual-track residual signals §2.3 / §4.1 (文档已随 docs/ 删除):
    12 tests covering:
        - 9 article-level boolean cols (3 dim × 3 signal: disagree/freerider/quietworker)
        - Invariants (i)(ii)(iii) per plan §2.3.2:
            (i)  freerider + quietworker ≤ 1 (mutually exclusive)
            (ii) freerider + quietworker == disagree (definitionally)
            (iii) NaN on either track → all three False (not NaN)
        - 18 panel-level cols (3 dim × 3 signal × 2 metric [frac, count])
        - Small-sample restriction: panel n_articles < 5 → *_frac forced NA
        - ctx coverage 自适应警告 + d4_data_quality_flag str column (F6 + C-NEW-3)
        - Missing track column graceful skip
        - cross-dim independence (subst/locus/collab 派生独立)

依赖: synthetic small fixture.
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
    """Each row dict can override any dim/track values.

    Production convention: target_bank (NOT 'bank') per encode.py:221.
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
# Test 1: 9 article-level columns added
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
# Test 2: Invariant (i) — freerider + quietworker ≤ 1 (mutually exclusive)
# ----------------------------------------------------------------------------

def test_invariant_i_freerider_quietworker_mutually_exclusive():
    """∀ article a, ∀ dim d: freerider[a,d] + quietworker[a,d] ≤ 1."""
    # Build diverse df covering 4 cases per dim
    df = _make_dual_track_df([
        {},  # all baseline = baseline matching, disagree=False, both=False
        {'innovation_substantiveness_full': '象征性'},  # full=contrast, ctx=baseline → quietworker
        {'innovation_substantiveness_ctx': '象征性'},   # full=baseline, ctx=contrast → freerider
        {'innovation_substantiveness_full': '象征性',
         'innovation_substantiveness_ctx': '象征性'},  # full=contrast=contrast, both=False
    ])
    derive_residual_signals(df)
    for dim_short, _, _, _ in DIMS_D4:
        violations = ((df[f'{dim_short}_freerider'].astype(int) +
                       df[f'{dim_short}_quietworker'].astype(int)) > 1).sum()
        assert violations == 0, (
            f"Invariant (i) failed for dim={dim_short}: {violations} rows with both True"
        )


# ----------------------------------------------------------------------------
# Test 3: Invariant (ii) — freerider + quietworker == disagree
# ----------------------------------------------------------------------------

def test_invariant_ii_freerider_plus_quietworker_equals_disagree():
    """∀ article: freerider + quietworker == disagree (when both tracks valid)."""
    df = _make_dual_track_df([
        {},  # match: all False
        {'innovation_substantiveness_full': '象征性'},  # quietworker (disagree)
        {'innovation_substantiveness_ctx':  '象征性'},  # freerider (disagree)
        {'innovation_locus_full': '应用场景'},  # quietworker (locus dim)
    ])
    derive_residual_signals(df)
    for dim_short, _, _, _ in DIMS_D4:
        lhs = df[f'{dim_short}_freerider'].astype(int) + df[f'{dim_short}_quietworker'].astype(int)
        rhs = df[f'{dim_short}_disagree'].astype(int)
        assert (lhs == rhs).all(), (
            f"Invariant (ii) failed for dim={dim_short}: free+quiet != disagree"
        )


# ----------------------------------------------------------------------------
# Test 4: Invariant (iii) — NaN propagation → all 3 indicators False
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
    """If full or ctx is NaN on any dim → 3 indicators all False (not NaN).

    CR-21: parametrized to cover NaN on each of 6 track-dim combinations.
    Strengthens earlier single-row test which missed track-specific bugs.
    """
    df = _make_dual_track_df([{nan_field: None}])
    derive_residual_signals(df)

    # Find which dim the NaN was on (e.g., 'innovation_substantiveness_full' → 'subst')
    dim_short = {
        'innovation_substantiveness': 'subst',
        'innovation_locus': 'locus',
        'innovation_collab_mode': 'collab',
    }[nan_field.rsplit('_', 1)[0]]

    # That dim's 3 indicators must all be False (not NaN, not True)
    assert df[f'{dim_short}_disagree'].iloc[0] == False, \
        f"{dim_short}_disagree should be False when {nan_field} is NaN"
    assert df[f'{dim_short}_freerider'].iloc[0] == False, \
        f"{dim_short}_freerider should be False when {nan_field} is NaN"
    assert df[f'{dim_short}_quietworker'].iloc[0] == False, \
        f"{dim_short}_quietworker should be False when {nan_field} is NaN"


def test_invariant_iii_both_tracks_nan_all_false():
    """When both full and ctx are NaN, all 3 indicators must still be False (not NaN)."""
    df = _make_dual_track_df([{
        'innovation_substantiveness_full': None,
        'innovation_substantiveness_ctx': None,
    }])
    derive_residual_signals(df)
    assert df['subst_disagree'].iloc[0] == False
    assert df['subst_freerider'].iloc[0] == False
    assert df['subst_quietworker'].iloc[0] == False


# ----------------------------------------------------------------------------
# Test 5: Disagree definition — full != ctx with both valid
# ----------------------------------------------------------------------------

def test_disagree_definition():
    df = _make_dual_track_df([
        {},  # match
        {'innovation_locus_ctx': '应用场景'},  # full=baseline, ctx=contrast → disagree
        {'innovation_locus_full': '应用场景'},  # full=contrast, ctx=baseline → disagree
    ])
    derive_residual_signals(df)
    assert df['locus_disagree'].tolist() == [False, True, True]


# ----------------------------------------------------------------------------
# Test 6: Cross-dim independence (subst != locus != collab derivations)
# ----------------------------------------------------------------------------

def test_cross_dim_independence():
    """Modifying subst track shouldn't affect locus/collab indicators."""
    df = _make_dual_track_df([{'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    # Only subst dim should show signal; locus/collab should all be False
    assert df['subst_quietworker'].iloc[0] == True
    assert df['locus_disagree'].iloc[0] == False
    assert df['locus_freerider'].iloc[0] == False
    assert df['locus_quietworker'].iloc[0] == False
    assert df['collab_disagree'].iloc[0] == False


# ----------------------------------------------------------------------------
# Test 7-8: Panel aggregation — 18 cols (3 dim × 3 signal × 2 metric)
# ----------------------------------------------------------------------------

def test_panel_18_columns_added():
    """aggregate_d4_panel adds 9 *_frac + 9 n_articles_* = 18 cols."""
    df = _make_dual_track_df([{}, {}, {'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    for dim_short, _, _, _ in DIMS_D4:
        for signal in ('disagree', 'freerider', 'quietworker'):
            assert f'{dim_short}_{signal}_frac' in panel.columns
            assert f'n_articles_{dim_short}_{signal}' in panel.columns


def test_panel_count_equals_sum_per_bank_year():
    """n_articles_subst_disagree == sum of subst_disagree per bank-year.

    Note: needs ≥ 5 articles per bank-year to avoid small-sample restriction
    (panel n_articles < 5 → *_frac forced to NA, see test_small_sample_restriction_forces_frac_nan).
    """
    df = _make_dual_track_df([
        {},  # match
        {'innovation_substantiveness_full': '象征性'},  # quietworker → disagree
        {'innovation_substantiveness_ctx':  '象征性'},  # freerider → disagree
        {},  # match (padding for ≥5 articles)
        {},  # match (padding)
        {},  # match (padding)
    ])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    # 6 articles in B1 2020, 2 disagree → frac = 2/6
    row = panel[(panel['target_bank'] == 'B1') & (panel['year'] == 2020)].iloc[0]
    assert row['n_articles_subst_disagree'] == 2
    assert row['subst_disagree_frac'] == pytest.approx(2 / 6)


# ----------------------------------------------------------------------------
# Test 9: Small-sample restriction — n_articles < 5 → *_frac forced NA
# ----------------------------------------------------------------------------

def test_small_sample_restriction_forces_frac_nan():
    """Panel n_articles < 5 → *_frac columns forced to pd.NA."""
    # Build df with 2 articles for B1 (small sample)
    df = _make_dual_track_df([{}, {'innovation_substantiveness_full': '象征性'}])
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    aggregate_d4_panel(df, panel)
    # B1 2020 has 2 articles < 5 → frac forced NA
    row = panel[(panel['target_bank'] == 'B1') & (panel['year'] == 2020)].iloc[0]
    assert pd.isna(row['subst_freerider_frac'])
    assert pd.isna(row['subst_quietworker_frac'])


# ----------------------------------------------------------------------------
# Test 10: d4_data_quality_flag str column (F6)
# ----------------------------------------------------------------------------

def test_d4_data_quality_flag_col_present():
    """aggregate_d4_panel always adds d4_data_quality_flag str column."""
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
    """ctx coverage < (baseline mean - 2σ) → quality_flag='insufficient'."""
    # Build df with most ctx NaN (low coverage)
    rows = [{}] * 2 + [{'innovation_collab_mode_ctx': None}] * 18
    df = _make_dual_track_df(rows)
    derive_residual_signals(df)
    panel = df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')

    # Baseline: mean=0.74, std=0.05 → threshold = 0.64
    # Actual coverage = 2/20 = 0.1 → far below threshold → 'insufficient'
    baseline_path = tmp_path / 'v3_4_0_ctx_coverage_baseline.json'
    baseline_path.write_text(json.dumps({'mean': 0.74, 'std': 0.05}), encoding='utf-8')

    aggregate_d4_panel(df, panel, ctx_baseline_path=str(baseline_path))
    assert panel['d4_data_quality_flag'].iloc[0] == 'insufficient'


# ----------------------------------------------------------------------------
# Test 12: Missing track columns → graceful skip
# ----------------------------------------------------------------------------

def test_missing_track_column_graceful_skip():
    """If e.g. innovation_locus_ctx column missing, only that dim's residuals skipped."""
    df = _make_dual_track_df([{}])
    df = df.drop(columns=['innovation_locus_ctx'])
    cols_added = derive_residual_signals(df)
    # subst + collab indicators added; locus_* not added (missing column skip)
    assert 'subst_disagree' in cols_added
    assert 'collab_disagree' in cols_added
    assert 'locus_disagree' not in cols_added
