"""benefit_society — Combined audit-only pipeline (P1.6).

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
Orchestrates ``benefit_society_alt_anchor`` (J-L-M canonical 5-pair) +
``benefit_society_placebo`` (4 business-line + 1 neutral) into a single
audit-only output:

    data/processed/27c_alt_anchor_and_placebo_panel.parquet

Schema (key = target_bank + year):
    - benefit_jlm_zh_mean / std / pos_frac / neg_frac
    - benefit_placebo_housing_loans_mean
    - benefit_placebo_credit_cards_mean
    - benefit_placebo_intermediate_business_mean
    - benefit_placebo_branch_channel_mean
    - benefit_placebo_general_corporate_mean   (neutral baseline)

Sidecar JSON: ``...sidecar.json`` with yaml SHA-256 anchors + match counts.

**Critical**: does not touch main panel; this is audit-only path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from news_process.pipeline.features.benefit_society_alt_anchor import (
    aggregate_to_bank_year as _alt_aggregate,
)
from news_process.pipeline.features.benefit_society_alt_anchor import (
    compute_direction_vector as _alt_direction,
)
from news_process.pipeline.features.benefit_society_alt_anchor import (
    load_jlm_zh_anchors,
)
from news_process.pipeline.features.benefit_society_alt_anchor import (
    project_texts as _alt_project,
)
from news_process.pipeline.features.benefit_society_placebo import (
    compute_placebo_projection,
    load_placebo_keywords,
)

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_audit_panel(
    df_exploded: pd.DataFrame,
    text_embeddings: np.ndarray,
    main_direction: np.ndarray,
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Build the combined audit panel.

    Parameters
    ----------
    df_exploded
        Article-bank DataFrame (must have target_bank, year, 标题, 内容).
    text_embeddings
        Pre-computed shibing624 embeddings, shape ``(n_articles, 768)``.
    main_direction
        Main 10-anchor fintech direction vector (used for placebo subset
        projection). Must be unit norm.

    Returns
    -------
    tuple[pd.DataFrame, dict]
        ``(combined_panel, metadata)``. Metadata contains anchor yaml SHAs +
        per-placebo match counts for downstream sidecar JSON.
    """
    if len(df_exploded) != len(text_embeddings):
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and text_embeddings "
            f"({len(text_embeddings)}) length mismatch"
        )

    # ---- 1) Alt anchor (J-L-M 5-pair) — needs its own embedding pass for anchors
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("shibing624/text2vec-base-chinese")
    embedding_fn = lambda texts: model.encode(list(texts), show_progress_bar=False)  # noqa: E731

    pos, neg, alt_meta = load_jlm_zh_anchors()
    alt_dir = _alt_direction(pos, neg, embedding_fn)
    alt_scores = _alt_project(text_embeddings, alt_dir)
    alt_panel = _alt_aggregate(
        df_exploded, alt_scores, bank_col=bank_col, year_col=year_col
    )

    # ---- 2) Placebo (4 business lines + 1 neutral) — uses MAIN direction
    business_lines, neutral_baseline, placebo_meta = load_placebo_keywords()
    keyword_sets: dict[str, list[str]] = {**business_lines, **neutral_baseline}
    placebo_panel, match_counts = compute_placebo_projection(
        df_exploded,
        text_embeddings,
        main_direction,
        keyword_sets,
        bank_col=bank_col,
        year_col=year_col,
    )

    # ---- 3) Outer-merge on (bank, year)
    combined = alt_panel.merge(
        placebo_panel, on=[bank_col, year_col], how="outer"
    )

    metadata = {
        "alt_anchor_yaml_sha256": alt_meta["yaml_sha256"],
        "alt_anchor_direction_sha256": hashlib.sha256(alt_dir.tobytes()).hexdigest(),
        "placebo_keyword_yaml_sha256": placebo_meta["yaml_sha256"],
        "placebo_match_counts": match_counts,
        "n_articles_total": int(len(df_exploded)),
        "n_bank_year_obs": int(len(combined)),
        "schema_version": "1.0",
        "plan_version": "v2.0 (J-L-M 2026 robustness alignment)",
        "task_id": "P1.6 audit-only combined panel",
        "embedding_model": "shibing624/text2vec-base-chinese",
        "embedding_dim": int(text_embeddings.shape[1]) if text_embeddings.ndim == 2 else None,
    }
    return combined, metadata


def write_sidecar_json(panel_path: Path, metadata: dict[str, object]) -> Path:
    sidecar_path = panel_path.with_suffix(".sidecar.json")
    sidecar_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return sidecar_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python news_process/27c_placebo_and_alt_anchor.py",
        description=(
            "P1.6 — combined audit-only panel: J-L-M alt anchor + business-line placebo. "
            "Outputs `data/processed/27c_alt_anchor_and_placebo_panel.parquet`."
        ),
    )
    parser.add_argument(
        "--text-embeddings-full",
        type=str,
        default=None,
        help="Path to main pipeline article embeddings .npy (full track)",
    )
    parser.add_argument(
        "--df-exploded",
        type=str,
        default=None,
        help="Path to exploded article-bank parquet (target_bank/year/标题/内容)",
    )
    parser.add_argument(
        "--main-direction-npy",
        type=str,
        default=None,
        help="Path to MAIN 10-anchor fintech direction .npy (used for placebo projection)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/27c_alt_anchor_and_placebo_panel.parquet",
        help="Output parquet path",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate yaml schemas only; do not load embeddings or run projection",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )

    # Always-safe yaml schema validation (no embedding load)
    pos, neg, alt_meta = load_jlm_zh_anchors()
    bl, nb, placebo_meta = load_placebo_keywords()
    logger.info(
        "Loaded anchors: J-L-M 5-pair (sha=%s) + placebo %d business lines + %d neutral (sha=%s)",
        alt_meta["yaml_sha256"][:16],
        len(bl),
        len(nb),
        placebo_meta["yaml_sha256"][:16],
    )

    if args.validate_only:
        logger.info("[validate-only] yaml schemas OK; exiting.")
        return 0

    if not all([args.text_embeddings_full, args.df_exploded, args.main_direction_npy]):
        logger.warning(
            "Full projection requires --text-embeddings-full + --df-exploded + "
            "--main-direction-npy. Yaml schemas validated; rerun with inputs to "
            "produce audit panel."
        )
        return 0

    text_embeddings = np.load(args.text_embeddings_full)
    df_exploded = pd.read_parquet(args.df_exploded)
    main_direction = np.load(args.main_direction_npy)
    logger.info(
        "Loaded embeddings shape=%s / df len=%d / direction shape=%s",
        text_embeddings.shape,
        len(df_exploded),
        main_direction.shape,
    )

    combined, meta = build_audit_panel(df_exploded, text_embeddings, main_direction)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, index=False)
    logger.info("Wrote audit panel: %s (%d bank-year obs)", output_path, len(combined))

    sidecar_path = write_sidecar_json(output_path, meta)
    logger.info("Wrote sidecar JSON: %s", sidecar_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
