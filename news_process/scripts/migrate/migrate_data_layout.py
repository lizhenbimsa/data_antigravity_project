"""migrate_data_layout.py — Phase 2e migration helper (DEFERRED, partially obsoleted by Phase 8).

Phase 8 status (2026-05-04)
---------------------------
Phase 8 (delivered) performed the **single-level** rename
``data_processed/`` → ``data/processed/`` *without* the originally-planned
business-group sub-partitioning (``00_preprocess/``, ``10_filter/``, ...).
Rationale: cross-stage parquet reads (e.g. stage 21 reads stage 14 output,
stage 24 reads stage 23 output) would force ``CONFIG['filenames']`` to carry
group prefixes, *increasing* coupling rather than reducing it (DRY violation).
The flat layout under ``data/processed/`` keeps its original prefix discipline
(``NN_xxx.parquet``) which already encodes business group via the numeric
prefix, with zero duplication.

This script remains as **archival/optional helper** for any future scenario
where someone explicitly wants the deeper grouping (e.g. when storage tiering
or per-group cold-storage retention policies become a requirement). When
invoking, target paths now sit under ``data/processed/<group>/``.

Purpose (original)
------------------
The original Phase 2e blueprint mandated the move from the flat
``news_process/data_processed/`` directory to a stage-grouped layout::

    data/processed/00_preprocess/    # 00 outputs
    data/processed/10_filter/        # 11/12/14/15 outputs
    data/processed/20_sentiment/     # 21/22/23/24 outputs
    data/processed/30_features/      # 25/26/27/30 outputs
    data/processed/40_panel/         # 41-48 + 45 outputs
    data/processed/50_falsification/ # 51 outputs
    data/processed/validation/       # 31-39 outputs
    data/processed/reports/          # eval_reports/

Phase 2e in this commit is intentionally **non-destructive**: this script is
created as a future-execution helper, not invoked.  Reasons for deferral:

1. The current ``tests/fixtures/golden_panel_v0.json`` snapshot was indexed
   against ``data_processed/<file>.parquet`` paths.  Moving the parquets
   without simultaneously updating the snapshot would break Phase 2g's
   reproducibility test.
2. The existing 5 ``stata/*.do`` files reference paths like
   ``output/40_panel_data.dta`` which are already stale (the file does not
   exist), so the .do contract is loosely respected anyway.  A full migration
   wants a coordinated re-snapshot + .do-rewrite + Stata-user notification.
3. The orchestrator's ``OUTPUT_REGISTRY`` (Phase 2d) currently records
   filenames *only*; once it grows to include directory prefixes (Phase 2e
   coordinated change), this helper performs the on-disk relocation in one
   atomic ``mv`` pass.

Until then, runtime semantics are unchanged: stages continue to read/write
``data_processed/<flat>``, and ``CONFIG['paths']['output_dir']`` still
resolves to that flat directory.

Invocation (when Phase 2e is unfrozen):
    python news_process/scripts/migrate/migrate_data_layout.py [--apply]
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


# Stage filename → destination subdirectory under ``data/processed/``.
TARGET_LAYOUT = {
    "00_preprocessing.parquet":          "00_preprocess",
    "11_bank_news.parquet":              "10_filter",
    "12_fintech_news.parquet":           "10_filter",
    "12_fintech_news_full.parquet":      "10_filter",
    "14_fintech_intensity.parquet":      "10_filter",
    "15_article_alignment.parquet":      "10_filter",
    "21_tone_llms.parquet":              "20_sentiment",
    "21_tone_llms_full.parquet":         "20_sentiment",
    "22_words_tone.parquet":             "20_sentiment",
    "23_bert_tone.parquet":              "20_sentiment",
    "24_herd_decay.parquet":             "20_sentiment",
    "27_benefit_embeddings_anchors.npy": "30_features",
    "27_benefit_embeddings_ctx.npy":     "30_features",
    "27_benefit_embeddings_full.npy":    "30_features",
    "40_panel_yearly.parquet":           "40_panel",
    "40_panel_yearly.dta":               "40_panel",
    "40_article_bank_level.parquet":     "40_panel",
    "40_attn_index_year.parquet":        "40_panel",
    "40_attn_index_province_year.parquet": "40_panel",
    "40_attn_index_city_year.parquet":   "40_panel",
    "41_panel_with_controls.parquet":    "40_panel",
    "41_panel_with_controls.dta":        "40_panel",
    "51_panel_with_controls.parquet":    "50_falsification",
    "51_panel_with_controls.dta":        "50_falsification",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def plan_moves() -> list[tuple[Path, Path]]:
    """Return the list of (src, dst) pairs that would be moved.

    Phase 8 update: source root migrated from ``data_processed/`` to
    ``data/processed/`` (single-level rename). This helper, when invoked,
    would deepen that one level further into ``data/processed/<group>/``.
    """
    root = _project_root()
    # Phase 8 (2026-05-04): src_dir migrated from data_processed/ → data/processed/
    src_dir = root / "data" / "processed"
    dst_root = root / "data" / "processed"
    moves: list[tuple[Path, Path]] = []
    for fname, sub in TARGET_LAYOUT.items():
        src = src_dir / fname
        if src.exists():
            dst = dst_root / sub / fname
            moves.append((src, dst))
    return moves


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2e data-layout migration (DRY-RUN by default)"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually move files (default: print plan only).",
    )
    args = parser.parse_args()

    moves = plan_moves()
    if not moves:
        print("No files to move (data/processed/ is empty or layout already complete).")
        return 0

    print(f"Phase 2e plan: {len(moves)} moves")
    for src, dst in moves:
        print(f"  {src.name:<42s} -> data/processed/{dst.parent.name}/")

    if not args.apply:
        print("\n(dry-run) Re-run with --apply to perform the moves.")
        print("WARNING: re-snapshot tests/fixtures/golden_panel_v0.json afterwards,")
        print("         and audit stata/*.do paths.")
        return 0

    print("\nApplying moves...")
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"  moved: {src.name}")
    print(f"\nDone. {len(moves)} files relocated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
