"""tests/integration/test_panel_reproducibility.py — Phase 2g acceptance gate.

Verifies that every parquet currently present in ``data/processed/`` produces
the same per-column value hashes as the Phase 0 ``golden_panel_v0.json``
baseline.  Any column-level mismatch indicates a refactor accidentally altered
downstream data — a reason to roll back to ``phase-1-baseline`` (or the
relevant earlier baseline).

Phase 8 (2026-05-04): the on-disk layout migrated from ``data_processed/`` to
``data/processed/``; ``data_dir`` fixture now points at the new location.

The check is **column-level hash-only** (per the restructuring plan's Phase 2g
spec).  Reasons hash-only is the right choice over ``assert_frame_equal``:
  - Phase 0 fixture stores hashes only (no full DataFrame), so equality cannot
    be asserted structurally.
  - Hash-only is forward-compatible: when Phase 2e migrates the on-disk
    layout to ``data/processed/<group>/``, this test only needs to look up the
    new location, not re-snapshot.

Behaviour:
  - For each stage in ``OUTPUT_REGISTRY`` whose parquet currently exists,
    recompute column-level value hashes and compare against the golden.
  - Any column hash mismatch -> test FAIL with diagnostic delta.
  - Any expected stage that's missing from the golden snapshot is skipped
    with a note (Phase 0 marked ``incomplete=true`` because stage 15 had no
    output at the time of snapshot).
  - Stages currently present on disk but absent from the golden snapshot
    likewise yield a SKIP (legitimate when a stage was re-run after Phase 0).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import pytest


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _column_hash(s: pd.Series) -> str:
    """64-bit unsigned hex digest of pandas value hash."""
    h = int(pd.util.hash_pandas_object(s, index=False).sum())
    return f"{h & ((1 << 64) - 1):016x}"


@pytest.fixture(scope="module")
def golden() -> dict:
    """Load the Phase 0 baseline snapshot."""
    fixture_path = (_project_root() / "tests" / "fixtures"
                    / "golden_panel_v0.json")
    if not fixture_path.exists():
        pytest.skip(
            f"Phase 0 fixture not found at {fixture_path}; "
            "run `python scripts/migrate/generate_golden_snapshot.py` first."
        )
    with fixture_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def data_dir() -> Path:
    """Resolve the parquet directory (Phase 8: ``data_processed`` → ``data/processed``)."""
    return _project_root() / "data" / "processed"


def _stages_present(golden: dict, data_dir: Path) -> list[str]:
    """Stages that exist both in the golden snapshot and on disk."""
    return [
        name for name in golden.get("stages", {})
        if (data_dir / name).is_file()
        and "error" not in golden["stages"][name]
        and "column_hashes" in golden["stages"][name]
    ]


def test_golden_snapshot_has_content(golden):
    """Sanity: the snapshot must have at least one indexed stage."""
    stages = golden.get("stages", {})
    assert stages, "golden_panel_v0.json contains no stages"
    indexed = sum(1 for s in stages.values() if "column_hashes" in s)
    assert indexed > 0, "no stage in the golden snapshot has column_hashes"


@pytest.mark.parametrize("stage_filename", [
    "00_preprocessing.parquet",
    "11_bank_news.parquet",
    "12_fintech_news.parquet",
    "12_fintech_news_full.parquet",
    "14_fintech_intensity.parquet",
    "21_tone_llms.parquet",
    "21_tone_llms_full.parquet",
    "22_words_tone.parquet",
    "23_bert_tone.parquet",
    "24_herd_decay.parquet",
    "40_panel_yearly.parquet",
    "40_article_bank_level.parquet",
    "40_attn_index_year.parquet",
    "40_attn_index_province_year.parquet",
    "40_attn_index_city_year.parquet",
    "41_panel_with_controls.parquet",
    "51_panel_with_controls.parquet",
])
def test_column_hashes_match_golden(stage_filename, golden, data_dir):
    """Per-column value hashes must equal the Phase 0 baseline.

    Skipped if either the stage is absent from disk (Phase 0 was incomplete)
    or absent from the golden snapshot (legit if stage was re-snapshotted
    after Phase 0).
    """
    parquet_path = data_dir / stage_filename
    if not parquet_path.is_file():
        pytest.skip(f"Stage parquet not on disk: {stage_filename}")

    stage_record = golden.get("stages", {}).get(stage_filename)
    if not stage_record or "column_hashes" not in stage_record:
        pytest.skip(
            f"Stage {stage_filename} missing from golden snapshot "
            "(generate_golden_snapshot.py was run before this stage existed)"
        )

    expected_hashes: dict = stage_record["column_hashes"]
    expected_columns: list = stage_record.get("columns_order", list(expected_hashes.keys()))

    df = pd.read_parquet(parquet_path)

    # Column set match
    df_cols = set(df.columns)
    expected_cols = set(expected_columns)
    extra = df_cols - expected_cols
    missing = expected_cols - df_cols
    assert not extra and not missing, (
        f"{stage_filename}: column-set drift\n"
        f"  added (in disk, not in golden):   {sorted(extra)[:10]}\n"
        f"  removed (in golden, not in disk): {sorted(missing)[:10]}"
    )

    # Per-column hash match
    mismatches = []
    for col in expected_columns:
        actual = _column_hash(df[col])
        expected = expected_hashes[col]
        if actual != expected:
            mismatches.append((col, expected, actual))

    if mismatches:
        details = "\n".join(
            f"  {col!r}: golden={exp}  current={act}"
            for col, exp, act in mismatches[:10]
        )
        n_more = len(mismatches) - 10
        suffix = f"\n  ... and {n_more} more" if n_more > 0 else ""
        pytest.fail(
            f"{stage_filename}: {len(mismatches)} column hash mismatches\n"
            f"{details}{suffix}\n"
            f"  Phase 2 refactor may have altered downstream data; "
            f"consider rolling back to phase-1-baseline."
        )
