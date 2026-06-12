"""benefit_society — Business-line placebo projection (S1 robustness).

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 P1.1 + P1.2:

Per J-L-M 2026 §4.2 placebo industries methodology, applies the **same** main
fintech-specific 10-anchor direction vector to **filtered** article subsets
(non-fintech business lines + neutral baseline). Expected behavior: filtered
projections should NOT predict ROA (acceptance: |β_placebo / β_fintech| < 0.3
for ≥4/5 placebo specs, per AC-S1).

**Audit-only path**: writes to `data/processed/27c_alt_anchor_panel.parquet`
or a sibling file; does NOT modify the main panel `40_panel_yearly.parquet`
or its golden snapshot.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_placebo_keywords(
    yaml_path: Path | str | None = None,
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, object]]:
    """Load business-line + neutral placebo keyword sets.

    Returns
    -------
    tuple
        ``(business_lines, neutral_baseline, metadata)`` where:
        - ``business_lines``: ``{line_id: keyword_list}`` (4 lines)
        - ``neutral_baseline``: ``{neutral_id: keyword_list}`` (1 set)
        - ``metadata``: yaml SHA-256 + schema_version
    """
    if yaml_path is None:
        yaml_path = (
            _repo_root()
            / "news_process"
            / "config"
            / "benefit_society_placebo_keywords.yaml"
        )
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"benefit_society_placebo_keywords.yaml not found at {yaml_path}"
        )
    raw = yaml_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    cfg = yaml.safe_load(raw.decode("utf-8"))

    bl_raw = cfg.get("business_lines", {})
    if len(bl_raw) != 4:
        raise ValueError(
            f"Expected 4 business lines per plan §3 P1.2; got {len(bl_raw)}"
        )
    business_lines = {k: list(v.get("keywords", [])) for k, v in bl_raw.items()}
    for k, kws in business_lines.items():
        if not kws:
            raise ValueError(f"Business line '{k}' has no keywords")

    nb_raw = cfg.get("neutral_baseline", {})
    if len(nb_raw) != 1:
        raise ValueError(f"Expected 1 neutral baseline; got {len(nb_raw)}")
    neutral_baseline = {k: list(v.get("keywords", [])) for k, v in nb_raw.items()}
    for k, kws in neutral_baseline.items():
        if not kws:
            raise ValueError(f"Neutral baseline '{k}' has no keywords")

    metadata = {
        "yaml_path": str(yaml_path),
        "yaml_sha256": sha,
        "schema_version": cfg.get("schema_version"),
        "n_business_lines": len(business_lines),
        "n_neutral_baselines": len(neutral_baseline),
    }
    return business_lines, neutral_baseline, metadata


def filter_articles_by_keywords(
    df_articles: pd.DataFrame,
    keywords: list[str],
    *,
    title_col: str = "标题",
    content_col: str = "内容",
) -> pd.Series:
    """Return a boolean mask selecting rows where ANY keyword appears in
    title OR content.

    Parameters
    ----------
    df_articles
        Article DataFrame (must contain title_col + content_col).
    keywords
        List of Chinese keywords to match (case-sensitive substring match;
        Chinese text is case-invariant).
    title_col, content_col
        Column names. Defaults match v3.7.0 pipeline 标题/内容 convention.

    Returns
    -------
    pd.Series
        Boolean mask, length == len(df_articles).
    """
    if not keywords:
        return pd.Series(False, index=df_articles.index)

    # Escape regex meta chars in keywords (defensive; Chinese rarely needs it)
    escaped = [re.escape(kw) for kw in keywords]
    pattern = "|".join(escaped)

    title = (
        df_articles[title_col].fillna("").astype(str)
        if title_col in df_articles.columns
        else pd.Series("", index=df_articles.index)
    )
    content = (
        df_articles[content_col].fillna("").astype(str)
        if content_col in df_articles.columns
        else pd.Series("", index=df_articles.index)
    )
    combined = title + " " + content

    return combined.str.contains(pattern, regex=True, na=False)


def compute_placebo_projection(
    df_articles: pd.DataFrame,
    text_embeddings: np.ndarray,
    direction: np.ndarray,
    keyword_sets: dict[str, list[str]],
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
    title_col: str = "标题",
    content_col: str = "内容",
    col_suffix: str = "",
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Compute placebo projections for multiple business-line filters.

    For each filter in ``keyword_sets``:
        1. Filter articles by keyword match (title + content)
        2. Apply ``direction`` to filtered subset of ``text_embeddings``
        3. Aggregate to bank-year mean cosine projection

    确定性披露 (fix(omni-g-benefit-01, 2026-06-11)): 本函数链路 (关键词过滤 +
    余弦投影 + groupby mean) 无任何随机步; 编排器 (audit_combined) 仍显式
    np.random.seed 并把 seed 写入 sidecar, 守卫未来引入的抽样步。

    Parameters
    ----------
    df_articles
        Article DataFrame; must have len == len(text_embeddings).
    text_embeddings
        Pre-computed embeddings, shape ``(n_articles, d)``.
    direction
        Unit-norm direction vector (typically main 10-pair fintech direction).
    keyword_sets
        ``{placebo_id: [keyword, ...]}`` mapping (4 biz + 1 neutral = 5).
    col_suffix
        输出列后缀 (ctx 轨传 ``"_ctx"``; fix(omni-g-benefit-01, 2026-06-11)
        补 ctx 轨)。默认 ``""`` 维持既有列名。

    Returns
    -------
    pd.DataFrame
        Bank-year panel with one column per placebo:
        ``benefit_placebo_{placebo_id}_mean{col_suffix}``.
    dict[str, int]
        Per-placebo match counts (``{placebo_id: n_matched_articles}``)
        for downstream R1.A risk monitoring.
    """
    if len(df_articles) != len(text_embeddings):
        raise ValueError(
            f"df_articles ({len(df_articles)}) and text_embeddings "
            f"({len(text_embeddings)}) length mismatch"
        )

    direction_unit = direction / np.linalg.norm(direction)
    norms = np.linalg.norm(text_embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    all_scores = (text_embeddings / norms) @ direction_unit  # shape (n,)

    panel_pieces: list[pd.DataFrame] = []
    match_counts: dict[str, int] = {}
    base = df_articles[[bank_col, year_col]].reset_index(drop=True).copy()
    base["_score"] = all_scores

    for placebo_id, keywords in keyword_sets.items():
        mask = filter_articles_by_keywords(
            df_articles,
            keywords,
            title_col=title_col,
            content_col=content_col,
        ).reset_index(drop=True)
        n_matched = int(mask.sum())
        match_counts[placebo_id] = n_matched
        if n_matched == 0:
            logger.warning(
                "Placebo '%s' matched 0 articles; column will be all-NaN.",
                placebo_id,
            )
        sub = base.loc[mask].copy()
        agg = (
            sub.groupby([bank_col, year_col])["_score"]
            .mean()
            .reset_index()
            .rename(columns={
                "_score": f"benefit_placebo_{placebo_id}_mean{col_suffix}",
            })
        )
        panel_pieces.append(agg)

    if not panel_pieces:
        return pd.DataFrame(columns=[bank_col, year_col]), match_counts

    panel = panel_pieces[0]
    for piece in panel_pieces[1:]:
        panel = panel.merge(piece, on=[bank_col, year_col], how="outer")
    return panel, match_counts


# ============================================================================
# CLI
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m news_process.pipeline.features.benefit_society_placebo",
        description=(
            "Business-line + neutral placebo projection (V2.0 plan P1.1+P1.2). "
            "Uses MAIN 10-anchor fintech direction applied to filtered article subsets."
        ),
    )
    parser.add_argument(
        "--keywords-yaml",
        type=str,
        default=None,
        help="Override path to benefit_society_placebo_keywords.yaml",
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

    business_lines, neutral_baseline, meta = load_placebo_keywords(args.keywords_yaml)
    logger.info(
        "Loaded placebo keyword sets: %d business lines + %d neutral. yaml sha=%s",
        len(business_lines),
        len(neutral_baseline),
        meta["yaml_sha256"][:16],
    )
    for line_id, kws in business_lines.items():
        logger.info("  Business line '%s': %d keywords", line_id, len(kws))
    for nb_id, kws in neutral_baseline.items():
        logger.info("  Neutral baseline '%s': %d keywords", nb_id, len(kws))

    if args.validate_only:
        logger.info("[validate-only] yaml schema OK; exiting.")
        return 0

    logger.warning(
        "Full projection requires text_embeddings + df_exploded (see plan §3 P1.6); "
        "this CLI provides validation + library functions only."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
