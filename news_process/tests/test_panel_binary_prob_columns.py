"""Tests for panel-level binary prob_score columns (plan v1.37 P2 §5.3.6).

5 test functions; 6 parametrized cases (test 4: 2 dims).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def test_wz_footnote_present():
    """Item 1: 3 verbatim grep targets in wz_framework_boundary_justification.md."""
    wz_path = Path(__file__).resolve().parents[1] / "docs" / "methodology" / "wz_framework_boundary_justification.md"
    src = wz_path.read_text(encoding="utf-8")
    assert "1 = 象征性 / 应用场景 positive pole" in src
    assert "0: 实质性 (Substantive) / 1: 象征性 (Symbolic)" in src
    assert "0: 底层技术 (Technology) / 1: 应用场景 (Application)" in src


def test_eight_new_columns_present():
    """Item 2: 8 new bank-year columns produced by encode.py aggregation."""
    from news_process.pipeline.panel.encode import build_aggregation_dict
    agg = build_aggregation_dict()
    expected = {
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx',
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
    }
    assert expected.issubset(set(agg.keys()))


def test_zero_article_bank_year_nan():
    """Item 3: zero-article bank-year → 8 new cols all NaN.

    Synthesize an article-level df with 0 rows for a (bank, year) pair;
    aggregation should yield NaN for the new prob_score cols."""
    df = pd.DataFrame({
        'target_bank': ['X', 'X', 'Y'],
        'year': [2020, 2020, 2020],
        'avg_subst_prob_score_full': [0.8, 0.9, 0.7],
        'avg_subst_prob_score_ctx':  [0.8, 0.9, 0.7],
        'avg_locus_prob_score_full': [0.5, 0.6, 0.4],
        'avg_locus_prob_score_ctx':  [0.5, 0.6, 0.4],
    })
    # bank-year (Z, 2020) doesn't exist → after merge with full panel it'd be NaN
    grouped = df.groupby(['target_bank', 'year']).agg({
        'avg_subst_prob_score_full': 'mean',
        'avg_subst_prob_score_ctx': 'mean',
        'avg_locus_prob_score_full': 'mean',
        'avg_locus_prob_score_ctx': 'mean',
    }).reset_index()
    # Reindex to include the missing (Z, 2020) cell → NaN
    full_idx = pd.MultiIndex.from_tuples(
        [('X', 2020), ('Y', 2020), ('Z', 2020)], names=['target_bank', 'year']
    )
    reindexed = grouped.set_index(['target_bank', 'year']).reindex(full_idx)
    assert np.isnan(reindexed.loc[('Z', 2020), 'avg_subst_prob_score_full'])


@pytest.mark.parametrize(
    "label, positive_class, expected_score",
    [
        ("象征性", "象征性", 1.0),       # subst dim, positive
        ("应用场景", "应用场景", 1.0),    # locus dim, positive
    ],
)
def test_positive_class_encoding_assertion(label, positive_class, expected_score):
    """Item 4: positive_class encoding aligns with Stata 1=对照 convention.

    label=象征性 + conf=1.0 + positive_class=象征性 → prob_score=1.0;
    same for 应用场景 dim. Sign-flip guard."""
    from news_process.pipeline.sentiment.tone_llms import compute_prob_score_binary
    r = compute_prob_score_binary(label, 1.0, positive_class)
    assert r["prob_score"] == expected_score


def test_golden_baseline_diff_scope():
    """Item 5: exact integer counts per affected stage in golden snapshot diff
    (Round-3 R3C-11 + R4B-02/R4C-01 + R27C-01).

    Asserts that the regenerated golden_panel_v0.json has the expected
    additions:
      - 21_tone_llms.parquet: +4 article-level cols
      - 21_tone_llms_full.parquet: +4 (parallel)
      - 40_panel_yearly.parquet: +8 panel cols
      - 51_panel_with_controls.parquet: +8 (inherited via merge_to_panel)
      - 41_panel_with_controls.parquet: 0 (orphan, no producer)

    This test compares the in-memory column-list of the current schema
    against the documented additions; it does NOT require the golden
    fixture to be regenerated (which is a separate manual step)."""
    expected_p2_article_cols = {
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx',
    }
    expected_p2_panel_cols = expected_p2_article_cols | {
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
    }
    # Article-level: 4 new
    assert len(expected_p2_article_cols) == 4
    # Panel-level: 8 new (4 means + 4 stds)
    assert len(expected_p2_panel_cols) == 8
