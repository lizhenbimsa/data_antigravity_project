"""Orphan-panel merge fix (2026-05-30) — stage 17/18/19 feature panels into 40_panel_yearly.

Stages 17 (BERTopic), 18 (staleness), 19 (CEO NER) each
produce a bank-year FEATURE panel whose columns stata_export.py core_patterns already
declares, but nothing merged them into 40_panel_yearly. runner.py main() now has a
conditional left-merge loop that
brings their columns in when the (opt-in) stage has run, and is a graceful no-op when
the file is absent (the default, since 17/18/19 are disabled-by-default).

Stage 49 (risk_taking_outcomes) is deliberately EXCLUDED from the merge: it is the
DV/outcome master that papers 10/11 `use` directly, so merging it into the feature
panel would invert the DV→feature direction. This file pins both contracts.

`pytest.mark.fast` (pure source-inspection + in-memory pandas; no IO/LLM).
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

pytestmark = pytest.mark.fast

_RUNNER = (Path(__file__).resolve().parents[1]
           / "pipeline" / "panel" / "runner.py")


def _runner_src() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_runner_has_feature_merge_block():
    """The 8c merge loop must reference all four orphan feature panels (17/18/19 +
    39f cross_media_alpha, paper-10 main treatment)."""
    src = _runner_src()
    for fname in ("17_topic_panel.parquet",
                  "18_staleness_panel.parquet",
                  "19_executive_ner_panel.parquet",
                  "39f_cross_media_alpha.parquet"):
        assert fname in src, f"runner.py missing feature-merge for {fname}"


def test_runner_merge_is_key_safe_and_graceful():
    """The merge must drop_duplicates on keys, left-join, raise on row-count drift,
    and be guarded by os.path.exists (graceful when the opt-in stage didn't run)."""
    src = _runner_src()
    assert "drop_duplicates(['target_bank', 'year'])" in src
    assert "how='left'" in src
    # row-count integrity guard (raise, not assert — survives python -O)
    assert re.search(r"feature merge 改变面板行数", src)
    assert "os.path.exists(_opath)" in src


def test_runner_excludes_stage49_from_feature_merge():
    """Stage 49 risk-taking OUTCOMES must NOT be merged into 40_panel (DV master)."""
    src = _runner_src()
    # 49 outcomes parquet is never read into the feature-merge loop
    assert "49_risk_taking_outcomes.parquet" not in src, (
        "stage 49 (DV outcomes) must stay standalone, not merged into the panel")
    # and the rationale comment documents the exclusion
    assert "DV master" in src or "DV/feature" in src


# --- behavioral contract (mirrors the 8c loop semantics on fixtures) -----------

def _merge_feature(panel: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    """Replicate the runner.py 8c merge contract for a single feature panel."""
    feat = feat.drop_duplicates(['target_bank', 'year'])
    bring = ['target_bank', 'year'] + [
        c for c in feat.columns
        if c not in ('target_bank', 'year') and c not in panel.columns]
    n_before = len(panel)
    out = panel.merge(feat[bring], on=['target_bank', 'year'], how='left')
    if len(out) != n_before:
        raise RuntimeError("feature merge changed row count (key not 1:1)")
    return out


def _panel():
    return pd.DataFrame({
        'target_bank': ['工商', '建设', '农业'],
        'year': [2018, 2018, 2018],
        'llm_vote_tone_full': [0.1, -0.2, 0.0],
    })


def test_feature_merge_preserves_rowcount_and_adds_cols():
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '农业'],  # 建设 has no topic row
        'year': [2018, 2018],
        'topic_hhi_full': [0.5, 0.7],
    })
    out = _merge_feature(panel, feat)
    assert len(out) == 3                      # left-join preserves panel rows
    assert 'topic_hhi_full' in out.columns
    assert out.loc[out['target_bank'] == '工商', 'topic_hhi_full'].iloc[0] == 0.5
    assert pd.isna(out.loc[out['target_bank'] == '建设', 'topic_hhi_full'].iloc[0])


def test_feature_merge_raises_on_duplicate_after_dedup_is_safe():
    """Duplicate (bank,year) rows in the feature panel are de-duplicated, not exploded."""
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '工商'],   # duplicate key
        'year': [2018, 2018],
        'topic_hhi_full': [0.5, 0.9],
    })
    out = _merge_feature(panel, feat)          # must NOT raise / must NOT explode
    assert len(out) == 3


def test_feature_merge_does_not_overwrite_existing_panel_column():
    """A feature col that collides with an existing panel col is skipped (panel wins)."""
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '建设', '农业'],
        'year': [2018, 2018, 2018],
        'llm_vote_tone_full': [9.9, 9.9, 9.9],   # collides with panel
        'topic_hhi_full': [0.5, 0.6, 0.7],
    })
    out = _merge_feature(panel, feat)
    # existing panel value preserved, not overwritten by the feature panel's 9.9
    assert out.loc[out['target_bank'] == '工商', 'llm_vote_tone_full'].iloc[0] == 0.1
    assert 'topic_hhi_full' in out.columns
