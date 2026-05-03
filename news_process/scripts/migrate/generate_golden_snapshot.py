"""
generate_golden_snapshot.py — Phase 0 deliverable

Computes column-level value hashes for every existing parquet artifact in
``data_processed/`` and writes the result to ``tests/fixtures/golden_panel_v0.json``.

This is the **degraded-path** Phase 0 snapshot (per the restructuring plan):
we do NOT re-run the main pipeline. We hash whatever artifacts exist on disk
right now. If any expected stage output is missing, the JSON is marked with
``"incomplete": true``; Phase 2's ``test_panel_reproducibility.py`` will then
only verify the columns of stages we have a baseline for.

Hash semantics:
- Per column: hex(int(pd.util.hash_pandas_object(df[col], index=False).sum()))
- Row count + column count + dtype dict captured for cheap structural diff.
- Bytes hash of the parquet file is deliberately NOT captured (pyarrow
  metadata / snappy block boundaries / timestamps are not stable across
  re-writes).

Usage:
    python scripts/migrate/generate_golden_snapshot.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# Stages declared in run_pipeline_function.STAGES (per plan §1).
# A subset of these may already exist on disk; missing ones flip "incomplete" to true.
EXPECTED_STAGES = [
    "00_preprocessing.parquet",
    "11_bank_news.parquet",
    "12_fintech_news.parquet",
    "12_fintech_news_full.parquet",
    "14_fintech_intensity.parquet",
    "15_article_alignment.parquet",
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
]


def column_hash(s: pd.Series) -> str:
    """Hex digest of pandas hash of a single column's values (index ignored)."""
    h = int(pd.util.hash_pandas_object(s, index=False).sum())
    h_unsigned = h & ((1 << 64) - 1)
    return f"{h_unsigned:016x}"


def hash_parquet(path: Path) -> dict:
    """Hash one parquet file column-by-column."""
    df = pd.read_parquet(path)
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns_order": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "column_hashes": {c: column_hash(df[c]) for c in df.columns},
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data_processed"
    fixture_path = project_root / "tests" / "fixtures" / "golden_panel_v0.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    if not data_dir.is_dir():
        print(f"ERROR: data_processed/ not found at {data_dir}", file=sys.stderr)
        return 2

    snapshot: dict = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_tag": "baseline-pre-restructure",
        "data_dir": str(data_dir.relative_to(project_root)),
        "hash_method": "pd.util.hash_pandas_object(s, index=False).sum() -> u64 hex",
        "stages": {},
    }

    present = []
    missing = []
    for filename in EXPECTED_STAGES:
        path = data_dir / filename
        if not path.is_file():
            missing.append(filename)
            continue
        try:
            snapshot["stages"][filename] = hash_parquet(path)
            present.append(filename)
        except Exception as exc:  # noqa: BLE001 — diagnostic capture
            snapshot["stages"][filename] = {
                "file": filename,
                "error": f"{type(exc).__name__}: {exc}",
            }
            missing.append(filename)

    snapshot["incomplete"] = len(missing) > 0
    snapshot["counts"] = {
        "expected": len(EXPECTED_STAGES),
        "present": len(present),
        "missing": len(missing),
    }
    snapshot["missing_stages"] = missing

    with fixture_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {fixture_path.relative_to(project_root)}")
    print(f"  present: {len(present)} / {len(EXPECTED_STAGES)}")
    if missing:
        print(f"  missing: {missing}")
        print(f"  incomplete = true (Phase 2 repro test will skip missing stages)")
    else:
        print(f"  incomplete = false (full coverage)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
