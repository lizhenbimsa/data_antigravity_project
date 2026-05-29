"""S3 fix v2 (2026-05-30) regression guard — .dta column-name sanitizer consistency.

The S3 defect was: the same bank-year panel got DIFFERENT Stata variable names in
40_panel_yearly.dta (stage 45, via papers/_common/tables.py::sanitize_stata_columns)
vs 46_panel_yearly_full.dta (stage 46, via stata_export.shorten→asciify), because the
two paths used divergent length/abbreviation rules and the 40-path stripped Chinese
sentiment labels (正面/负面) to empty stems → pos/neg conflated into _1/_2 collisions.

The fix routes ALL .dta writers (40 via export.py, 51 via controls.py, derivative
papers via export_dta, scripts/convert_parquet_to_stata.py) through the SINGLE
canonical sanitizer (stata_export.shorten_long_column_names → asciify_non_ascii_columns).

These tests pin the contract:
  1. sanitize_stata_columns output == the canonical 46-path output (byte-identical).
  2. CN sentiment labels map to DISTINCT ascii stems (正面→pos, 负面→neg); no collision.
  3. On the real on-disk panel (if present): all names unique, ≤32 chars, valid Stata
     identifiers, and identical between the two paths.

A pre-existing test (test_papers_common.py::test_equivalence_with_pipeline_panel_export_
algorithm) only checked self-consistency (uniqueness/length), NOT cross-path equivalence,
so it passed while 125 names silently diverged. This file closes that gap.
"""
from __future__ import annotations

import os

import pandas as pd
import pytest

from news_process.papers._common.tables import sanitize_stata_columns
from news_process.pipeline.panel.stata_export import (
    asciify_non_ascii_columns,
    shorten_long_column_names,
)

_SAMPLE = [
    'finbert_cn_正面_w_sum_full', 'finbert_cn_负面_w_sum_full',
    'finbert_cn_正面_hw_sum_ctx', 'finbert_cn_负面_hw_sum_ctx',
    'jiang_2021_idf_score_w_sum_full', 'jiang_2021_idf_score_w_sum_ctx',
    'jiang_2021_idf_score_w_sum_title',
    'llm_vote_tone_full', 'mean_clarity_score_ctx', 'target_bank', 'year',
    'media_(中文)_breadth', '', '___',  # paren + empty + all-underscore edge cases
]


def _preprocess(columns):
    """Replicate the 40-path pre-processing the 46-path does not do (paren/empty)."""
    out = []
    for i, raw in enumerate(columns):
        c = str(raw).replace('(', '_').replace(')', '_')
        c = c.replace('（', '_').replace('）', '_')
        if not c or not c.strip('_'):
            c = f'col_{i}'
        out.append(c)
    return out


def _canonical_46(columns):
    """The canonical stage-46 sanitizer: shorten THEN asciify (stata_export order)."""
    df = pd.DataFrame(columns=_preprocess(columns))
    df, _ = shorten_long_column_names(df)
    df, _ = asciify_non_ascii_columns(df)
    return list(df.columns)


def test_tables_path_matches_canonical_46_path_on_sample():
    """40-path sanitize_stata_columns must equal the 46-path output, position-wise."""
    assert sanitize_stata_columns(_SAMPLE) == _canonical_46(_SAMPLE)


def test_pos_neg_labels_map_to_distinct_stems():
    """正面/负面 must NOT collapse to the same name (the core S3 corruption)."""
    out = sanitize_stata_columns(_SAMPLE)
    assert len(set(out)) == len(out), f"collision in sanitized names: {out}"
    pos_full, neg_full = out[0], out[1]
    assert pos_full != neg_full
    assert 'pos' in pos_full and 'neg' in neg_full
    # full vs ctx track suffix preserved (not truncated to ambiguous stem)
    assert out[0] != out[2] and out[1] != out[3]


def test_all_names_valid_stata_identifiers():
    import re
    ident = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,31}$')
    out = sanitize_stata_columns(_SAMPLE)
    for name in out:
        assert ident.match(name), f"invalid Stata identifier: {name!r}"


@pytest.mark.parametrize("parquet", ["40_panel_yearly.parquet"])
def test_real_panel_40_path_equals_46_path(parquet):
    """On the real on-disk panel: 40-path ≡ 46-path, all names unique & ≤32 chars."""
    path = os.path.join("news_process", "data", "processed", parquet)
    if not os.path.exists(path):
        pytest.skip(f"{parquet} not on disk")
    cols = list(pd.read_parquet(path).columns)
    out = sanitize_stata_columns(cols)
    assert len(set(out)) == len(out), "collisions on real panel columns"
    assert all(len(c) <= 32 for c in out), "name >32 chars on real panel"
    assert out == _canonical_46(cols), "40-path diverges from 46-path on real panel"
