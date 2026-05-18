"""benefit_society — Alternative Anchor Family (A2 robustness, audit-only).

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 P1.3:

Replicates the benefit_society direction-vector projection using the
**J-L-M 2026 RFS Internet Appendix A Table IA.1 (b) Chinese** 5-pair canonical
anchor set (instead of the 10-pair extended set in
``pipeline/features/benefit_society.py``).

Purpose: provide an alternative anchor family for plan Acceptance Criterion
AC-A2 — "benefit_jlm_zh vs benefit_mean β sign-match + ratio > 0.5".

**Audit-only path**: this module writes outputs to a separate parquet
(``data/processed/27c_alt_anchor_panel.parquet``) and does NOT modify the
main panel ``40_panel_yearly.parquet`` or its golden-snapshot schema.

Reuses (does not duplicate) the embedding cache + projection mechanics from
``benefit_society.py`` — anchor count differs (5 vs 10) but direction-vector
math (``mean(pos) − mean(neg)``) and cosine projection are byte-identical.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_jlm_zh_anchors(
    yaml_path: Path | str | None = None,
) -> tuple[list[str], list[str], dict[str, object]]:
    """Load the J-L-M 2026 Appendix A Chinese 5-pair anchor set.

    Returns
    -------
    tuple[list[str], list[str], dict]
        ``(positive_sentences, negative_sentences, metadata)`` where metadata
        contains schema_version / anchor_family / sha256 / n_pairs.

    Raises
    ------
    FileNotFoundError
        If the yaml file is missing.
    ValueError
        If the yaml fails schema validation (n_pairs != 5, missing fields,
        duplicate ids, or empty sentence).
    """
    if yaml_path is None:
        yaml_path = _repo_root() / "news_process" / "config" / "jlm2026_chinese_anchors.yaml"
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"jlm2026_chinese_anchors.yaml not found at {yaml_path}. "
            "This is UA-3 deliverable; user must provide before A2 runs."
        )

    raw = yaml_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    cfg = yaml.safe_load(raw.decode("utf-8"))

    if cfg.get("n_pairs") != 5:
        raise ValueError(
            f"J-L-M canonical methodology uses 5 anchor pairs; yaml declares "
            f"n_pairs={cfg.get('n_pairs')}. See Appendix A footnote."
        )
    pairs = cfg.get("pairs", [])
    if len(pairs) != 5:
        raise ValueError(f"Expected 5 pairs, got {len(pairs)}")
    ids = [p.get("id") for p in pairs]
    if len(set(ids)) != 5:
        raise ValueError(f"Duplicate pair ids: {ids}")
    pos: list[str] = []
    neg: list[str] = []
    for p in pairs:
        if not p.get("positive") or not p.get("negative"):
            raise ValueError(f"Empty sentence in pair id={p.get('id')}")
        pos.append(str(p["positive"]))
        neg.append(str(p["negative"]))

    metadata = {
        "yaml_path": str(yaml_path),
        "yaml_sha256": sha,
        "schema_version": cfg.get("schema_version"),
        "anchor_family": cfg.get("anchor_family"),
        "n_pairs": cfg["n_pairs"],
        "language": cfg.get("language"),
        "source_doi": cfg.get("source", {}).get("doi"),
    }
    return pos, neg, metadata


def compute_direction_vector(
    pos_sentences: Sequence[str],
    neg_sentences: Sequence[str],
    embedding_fn,
) -> np.ndarray:
    """Compute the unit-norm direction vector p = mean(pos) − mean(neg).

    Mathematically equivalent to per-pair difference average (linear
    additivity of the mean operator).

    Parameters
    ----------
    pos_sentences, neg_sentences
        Anchor sentences. Must have equal length.
    embedding_fn
        Callable ``texts -> np.ndarray of shape (n, d)``. Typically a closure
        around shibing624 sentence-transformer or a mock for testing.

    Returns
    -------
    np.ndarray
        Unit-norm direction vector of shape (d,).
    """
    if len(pos_sentences) != len(neg_sentences):
        raise ValueError(
            f"Anchor count mismatch: pos={len(pos_sentences)}, neg={len(neg_sentences)}"
        )
    all_anchors = list(pos_sentences) + list(neg_sentences)
    emb = embedding_fn(all_anchors)
    emb = np.asarray(emb, dtype=np.float32)
    if emb.ndim != 2 or emb.shape[0] != len(all_anchors):
        raise ValueError(
            f"embedding_fn returned shape {emb.shape}, expected ({len(all_anchors)}, d)"
        )
    n_pos = len(pos_sentences)
    direction = emb[:n_pos].mean(axis=0) - emb[n_pos:].mean(axis=0)
    norm = float(np.linalg.norm(direction))
    if norm < 1e-10:
        raise ValueError(f"Degenerate direction vector (norm={norm:.2e})")
    return direction / norm


def project_texts(
    text_embeddings: np.ndarray,
    direction: np.ndarray,
) -> np.ndarray:
    """Project pre-computed text embeddings onto direction (cosine similarity).

    Parameters
    ----------
    text_embeddings
        Shape ``(n, d)`` array of text embeddings (one per article).
    direction
        Unit-norm direction vector of shape ``(d,)``.

    Returns
    -------
    np.ndarray
        Cosine projections in ``[-1, 1]``, shape ``(n,)``.
    """
    if text_embeddings.ndim != 2:
        raise ValueError(
            f"text_embeddings must be 2D, got shape {text_embeddings.shape}"
        )
    if text_embeddings.shape[1] != direction.shape[0]:
        raise ValueError(
            f"Dimension mismatch: texts={text_embeddings.shape[1]} dir={direction.shape[0]}"
        )
    norms = np.linalg.norm(text_embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normalized = text_embeddings / norms
    return (normalized @ direction).astype(np.float32)


def aggregate_to_bank_year(
    df_articles: pd.DataFrame,
    scores: np.ndarray,
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
    score_col: str = "benefit_jlm_zh_score",
) -> pd.DataFrame:
    """Aggregate article-level cosine scores to bank-year panel.

    Follows J-L-M 2026 Eq. (2) with article-level c=1 instantiation:
    ``f_it = mean(a_ji over articles j in bank i, year t)``.

    Returns columns:
        ``benefit_jlm_zh_mean``, ``benefit_jlm_zh_std``,
        ``benefit_jlm_zh_pos_frac``, ``benefit_jlm_zh_neg_frac``
    """
    if len(df_articles) != len(scores):
        raise ValueError(
            f"df_articles ({len(df_articles)}) and scores ({len(scores)}) length mismatch"
        )
    work = df_articles[[bank_col, year_col]].copy()
    work[score_col] = scores
    work = work.dropna(subset=[score_col])

    agg = (
        work.groupby([bank_col, year_col])[score_col]
        .agg(
            benefit_jlm_zh_mean="mean",
            benefit_jlm_zh_std="std",
            benefit_jlm_zh_pos_frac=lambda x: float((x > 0).mean()),
            benefit_jlm_zh_neg_frac=lambda x: float((x < 0).mean()),
        )
        .reset_index()
    )
    agg["benefit_jlm_zh_std"] = agg["benefit_jlm_zh_std"].fillna(0.0)
    return agg


def write_sidecar_json(
    panel_path: Path,
    metadata: dict[str, object],
    direction_sha: str,
    n_articles: int,
    n_bank_years: int,
) -> Path:
    """Write reproducibility sidecar JSON next to the parquet output."""
    sidecar = {
        "schema_version": "1.0",
        "plan_version": "v2.0 (J-L-M 2026 robustness alignment)",
        "task_id": "P1.3 A2 alternative anchor projection",
        "anchor_metadata": metadata,
        "direction_vector_sha256": direction_sha,
        "n_articles_scored": int(n_articles),
        "n_bank_year_obs": int(n_bank_years),
        "embedding_model": "shibing624/text2vec-base-chinese",
        "embedding_dim": 768,
    }
    sidecar_path = panel_path.with_suffix(".sidecar.json")
    sidecar_path.write_text(
        json.dumps(sidecar, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return sidecar_path


# ============================================================================
# CLI entry
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m news_process.pipeline.features.benefit_society_alt_anchor",
        description=(
            "Compute J-L-M 2026 Appendix A alternative-anchor projections "
            "(audit-only; does not modify main panel)."
        ),
    )
    parser.add_argument(
        "--anchors-yaml",
        type=str,
        default=None,
        help="Path to jlm2026_chinese_anchors.yaml (default: news_process/config/...)",
    )
    parser.add_argument(
        "--text-embeddings-full",
        type=str,
        default=None,
        help="Path to stage 27 article-level embeddings .npy (full track)",
    )
    parser.add_argument(
        "--df-exploded",
        type=str,
        default=None,
        help="Path to exploded article-bank parquet (provides target_bank, year)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/27c_alt_anchor_panel.parquet",
        help="Output path for bank-year alt-anchor panel",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate yaml schema; do not load embeddings or run projection",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )

    pos, neg, meta = load_jlm_zh_anchors(args.anchors_yaml)
    logger.info(
        "Loaded J-L-M Appendix A anchors: %d pairs, family=%s, sha=%s",
        len(pos),
        meta["anchor_family"],
        meta["yaml_sha256"][:16],
    )

    if args.validate_only:
        logger.info("[validate-only] yaml schema OK; exiting.")
        return 0

    if args.text_embeddings_full is None or args.df_exploded is None:
        logger.warning(
            "Skipping projection (missing --text-embeddings-full / --df-exploded). "
            "Yaml schema validated; rerun with embedding inputs to produce panel."
        )
        return 0

    # Defer model import to here so --validate-only stays import-light
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("shibing624/text2vec-base-chinese")
    embedding_fn = lambda texts: model.encode(list(texts), show_progress_bar=False)  # noqa: E731

    direction = compute_direction_vector(pos, neg, embedding_fn)
    dir_sha = hashlib.sha256(direction.tobytes()).hexdigest()
    logger.info("Direction vector computed: norm=1.0, sha=%s", dir_sha[:16])

    text_embeddings = np.load(args.text_embeddings_full)
    df_exploded = pd.read_parquet(args.df_exploded)
    logger.info(
        "Loaded text_embeddings shape=%s, df_exploded len=%d",
        text_embeddings.shape,
        len(df_exploded),
    )

    scores = project_texts(text_embeddings, direction)
    panel = aggregate_to_bank_year(df_exploded, scores)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info("Wrote alt-anchor panel: %s (%d bank-year obs)", output_path, len(panel))

    sidecar_path = write_sidecar_json(
        output_path, meta, dir_sha, n_articles=len(scores), n_bank_years=len(panel)
    )
    logger.info("Wrote sidecar JSON: %s", sidecar_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
