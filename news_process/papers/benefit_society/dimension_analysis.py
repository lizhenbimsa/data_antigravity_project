"""news_process.papers.benefit_society.dimension_analysis
=========================================================
4 维度子指数分析 — 拆分 Stage 27 锚点为 core_op / growth / resource / compliance

【学术依据】
- Jha, Liu & Manela (2026, RFS §1.3.2): 双极锚点投影框架
- 维度划分依据 Stage 27 [POSITIVE_ANCHORS] 注释中的 4 维度结构

【设计原则】
- **不修改** [news_process/pipeline/features/benefit_society.py] 主流程
- 通过 `news_process.core.caching.LLMCache` 公共接口
- 直接 import [POSITIVE_ANCHORS] / [NEGATIVE_ANCHORS] 大写公开常量
- try/except ImportError 容错（应对未来 v4 接口变化）

【输出】
- 4 个子方向向量 (numpy.ndarray)
- 4 个子指数对原 panel 的合并表 (DataFrame)

CLI:
    python -m news_process.papers.benefit_society.dimension_analysis [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. 锚点维度切片 (与 Stage 27 [POSITIVE_ANCHORS] 注释 ①-⑩ 对齐)
# ---------------------------------------------------------------------------
# 4 维度索引 (0-based)，对应 Stage 27 锚点列表
DIMENSION_INDICES: dict[str, tuple[int, ...]] = {
    "core_op": (0, 1, 2),          # ①盈利效率 ③风险管控 ⑨信贷质量
    "growth":  (3, 4, 5),          # ②业务转型 ④客户基础 ⑤市场竞争力
    "resource": (6, 7),            # ⑦经济效益 ⑩人才队伍
    "compliance": (8, 9),          # ⑥合规成本 ⑧信息安全
}

DIMENSION_LABELS = {
    "core_op": "Core Operations (盈利/风险/信贷)",
    "growth": "Growth Capacity (转型/客户/竞争)",
    "resource": "Resource Investment (效益/人才)",
    "compliance": "Compliance & Security (合规/安全)",
}

# ---------------------------------------------------------------------------
# 2. 锚点导入 (容错)
# ---------------------------------------------------------------------------
def _import_anchors() -> tuple[list[str], list[str]]:
    """Import POSITIVE/NEGATIVE anchors from Stage 27, with version-tolerant fallback."""
    try:
        from news_process.pipeline.features.benefit_society import (
            NEGATIVE_ANCHORS,
            POSITIVE_ANCHORS,
        )
        return list(POSITIVE_ANCHORS), list(NEGATIVE_ANCHORS)
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import anchors from Stage 27: {e}. "
            "If running outside the news_process package, ensure PYTHONPATH includes project root."
        ) from e


# ---------------------------------------------------------------------------
# 3. Embedding 获取 (通过 LLMCache 公共接口)
# ---------------------------------------------------------------------------
def _resolve_prompt_version() -> str:
    """Resolve the prompt_version used by Stage 27 (F7 fix).

    Stage 27 stores anchor embeddings keyed by ``EMBEDDING_CONFIG['text_pipeline_version']``
    (see news_process.pipeline.features.benefit_society). If we use a different
    value, we silently miss the cache and try to call the API. Resolve dynamically
    with a safe fallback.
    """
    try:
        from news_process.pipeline.features.benefit_society import EMBEDDING_CONFIG
        return str(EMBEDDING_CONFIG.get("text_pipeline_version", "v0"))
    except ImportError:
        return "v0"


def _get_anchor_embeddings(
    anchors: Sequence[str],
    *,
    cache_db_path: str | None = None,
    model_id: str = "text-embedding-3-small",
    prompt_version: str | None = None,
) -> np.ndarray:
    """Retrieve embeddings for anchor sentences via LLMCache.

    If the anchors were already embedded by Stage 27, this is a cache hit and no
    new API calls are made. Otherwise, raises RuntimeError instructing the caller
    to run Stage 27 first.

    Parameters
    ----------
    prompt_version : optional
        If None (default), auto-resolves to Stage 27's value via
        [_resolve_prompt_version]. Explicit override is honored.
    """
    if prompt_version is None:
        prompt_version = _resolve_prompt_version()
    try:
        from news_process.core.caching import LLMCache
    except ImportError as e:
        raise RuntimeError(f"news_process.core.caching unavailable: {e}") from e

    if cache_db_path is None:
        # Default cache path consistent with Stage 27
        try:
            from news_process.pipeline.panel.encode import CONFIG, OUTPUT_DIR
            cache_db_path = CONFIG.get("paths", {}).get(
                "llm_cache_db",
                os.path.join(OUTPUT_DIR, "_llm_cache.db"),
            )
        except ImportError:
            raise RuntimeError(
                "Cannot resolve default LLM cache path; pass cache_db_path explicitly."
            )

    if not os.path.exists(cache_db_path):
        raise RuntimeError(
            f"LLM cache not found at {cache_db_path}. "
            "Run Stage 27 first to populate anchor embeddings."
        )

    embeddings: list[np.ndarray] = []
    with LLMCache(cache_db_path) as cache:
        for anchor in anchors:
            raw = cache.get(model_id, anchor, prompt_version=prompt_version)
            if raw is None:
                raise RuntimeError(
                    f"Anchor not cached: {anchor[:30]}... "
                    "Run Stage 27 to populate, or pass a different model_id."
                )
            vec = np.asarray(json.loads(raw), dtype=np.float32)
            embeddings.append(vec)

    return np.vstack(embeddings)


# ---------------------------------------------------------------------------
# 4. 子方向向量计算
# ---------------------------------------------------------------------------
def compute_direction_vectors(
    pos_anchors: Sequence[str],
    neg_anchors: Sequence[str],
    *,
    cache_db_path: str | None = None,
    model_id: str = "text-embedding-3-small",
    prompt_version: str | None = None,  # F7: auto-resolved from Stage 27 when None
) -> dict[str, np.ndarray]:
    """Compute 4 dimensional direction vectors.

    Returns
    -------
    dict
        {"core_op": ndarray, "growth": ndarray, "resource": ndarray, "compliance": ndarray}
    """
    if len(pos_anchors) != len(neg_anchors):
        raise ValueError(
            f"Anchor count mismatch: pos={len(pos_anchors)}, neg={len(neg_anchors)}"
        )

    all_anchors = list(pos_anchors) + list(neg_anchors)
    emb = _get_anchor_embeddings(
        all_anchors,
        cache_db_path=cache_db_path,
        model_id=model_id,
        prompt_version=prompt_version,
    )
    n_pos = len(pos_anchors)

    directions: dict[str, np.ndarray] = {}
    for dim_name, indices in DIMENSION_INDICES.items():
        valid_indices = tuple(i for i in indices if i < n_pos)
        if not valid_indices:
            logger.warning(f"No valid anchors for dimension {dim_name}; skipping")
            continue
        pos_idx = list(valid_indices)
        neg_idx = [n_pos + i for i in valid_indices]
        pos_mean = emb[pos_idx].mean(axis=0)
        neg_mean = emb[neg_idx].mean(axis=0)
        direction = pos_mean - neg_mean
        norm = np.linalg.norm(direction)
        if norm < 1e-10:
            logger.error(f"Dimension {dim_name}: direction vector norm < 1e-10; degenerate")
            continue
        directions[dim_name] = direction / norm

    return directions


# ---------------------------------------------------------------------------
# 5. 文本投影
# ---------------------------------------------------------------------------
def project_texts_by_dimension(
    text_embeddings: np.ndarray,
    directions: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Project text embeddings onto each dimensional direction vector.

    Parameters
    ----------
    text_embeddings : np.ndarray, shape (n_texts, dim)
        Pre-computed text embeddings (e.g., from Stage 27 [27_benefit_embeddings_full.npy])
    directions : dict
        Output of [compute_direction_vectors].

    Returns
    -------
    dict
        {dim_name: ndarray of shape (n_texts,)} cosine projections
    """
    if text_embeddings.ndim != 2:
        raise ValueError(f"text_embeddings must be 2D, got shape {text_embeddings.shape}")

    norms = np.linalg.norm(text_embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normalized = text_embeddings / norms

    scores: dict[str, np.ndarray] = {}
    for dim_name, direction in directions.items():
        scores[dim_name] = normalized @ direction
    return scores


# ---------------------------------------------------------------------------
# 6. Bank-Year 聚合
# ---------------------------------------------------------------------------
def aggregate_to_bank_year(
    df_exploded: pd.DataFrame,
    text_embeddings: np.ndarray,
    directions: dict[str, np.ndarray],
    *,
    bank_col: str = "target_bank",  # F6: align with 40_panel_yearly.parquet schema
    year_col: str = "year",
) -> pd.DataFrame:
    """Aggregate dimensional scores to bank-year panel (equal-weighted mean per Jha 2026 Eq. 2)."""
    if len(df_exploded) != len(text_embeddings):
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and text_embeddings ({len(text_embeddings)}) length mismatch"
        )

    scores_by_dim = project_texts_by_dimension(text_embeddings, directions)

    df_work = df_exploded[[bank_col, year_col]].copy()
    for dim_name, scores in scores_by_dim.items():
        df_work[f"benefit_{dim_name}"] = scores

    agg = df_work.groupby([bank_col, year_col]).agg(
        {f"benefit_{dim_name}": "mean" for dim_name in scores_by_dim}
    ).reset_index()

    return agg


# ---------------------------------------------------------------------------
# 7. Dual-track helpers (plan v2.12, F-B2 / F-M3 / F-V2-B2 — write back to
#    pipeline/features layer rather than the shared panel runner)
# ---------------------------------------------------------------------------

_DEFAULT_EMBEDDINGS = {
    "full": "news_process/data/processed/27_benefit_embeddings_full.npy",
    "ctx":  "news_process/data/processed/27_benefit_embeddings_ctx.npy",
}


def compute_dual_track_dimensions(
    df_exploded: pd.DataFrame,
    track_to_embedding: dict[str, np.ndarray],
    directions: dict[str, np.ndarray],
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
) -> pd.DataFrame:
    """Aggregate sub-index scores into a single bank-year panel covering all tracks.

    For each track key in ``track_to_embedding`` (typically ``{'full', 'ctx'}``),
    produces columns ``benefit_<dim>_<track>`` keyed on (bank_col, year_col).

    Returns a merged bank-year DataFrame.
    """
    merged: pd.DataFrame | None = None
    for track, text_emb in track_to_embedding.items():
        if len(df_exploded) != len(text_emb):
            raise ValueError(
                f"df_exploded ({len(df_exploded)}) and text_embeddings[{track!r}] "
                f"({len(text_emb)}) length mismatch"
            )
        track_panel = aggregate_to_bank_year(
            df_exploded, text_emb, directions, bank_col=bank_col, year_col=year_col,
        )
        track_panel = track_panel.rename(columns={
            f"benefit_{dim}": f"benefit_{dim}_{track}" for dim in directions
        })
        merged = (
            track_panel if merged is None
            else merged.merge(track_panel, on=[bank_col, year_col], how="outer")
        )
    assert merged is not None
    return merged


# ---------------------------------------------------------------------------
# 8. CLI 入口
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """CLI entry: compute 4-dimensional sub-indices and optionally aggregate to bank-year panel.

    Plan v2.12: ``--track {full,ctx,both}`` (default both) produces dual-track
    output ``benefit_{core_op,growth,resource,compliance}_{full,ctx}``.

    Returns 0 on success or graceful skip (missing optional inputs); raises on hard errors.
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.dimension_analysis",
        description="4 维度子指数计算 (core_op / growth / resource / compliance, 双轨)",
        # F-V2-H2 backwards-compat: disable abbrev so legacy --text-embeddings
        # (Phase 0) and new --text-embeddings-full (v2.12) are unambiguous.
        allow_abbrev=False,
    )
    parser.add_argument(
        "--track",
        choices=["full", "ctx", "both"],
        default="both",
        help="Sentiment track(s) to compute (plan v2.12)",
    )
    parser.add_argument(
        "--text-embeddings-full",
        "--text-embeddings",  # legacy alias (Phase 0 scaffolding default)
        type=str,
        default=_DEFAULT_EMBEDDINGS["full"],
        dest="text_embeddings_full",
        help="Path to Stage 27 full-track text embeddings (.npy). "
             "Legacy alias: --text-embeddings",
    )
    parser.add_argument(
        "--text-embeddings-ctx",
        type=str,
        default=_DEFAULT_EMBEDDINGS["ctx"],
        help="Path to Stage 27 ctx-track text embeddings (.npy)",
    )
    parser.add_argument(
        "--df-exploded",
        type=str,
        default=None,
        help="Path to exploded article-bank DataFrame parquet (optional; if missing, anchors-only mode)",
    )
    parser.add_argument(
        "--cache-db",
        type=str,
        default=None,
        help="Override LLM cache DB path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/27_benefit_dimensions_panel.parquet",
        help="Output path for bank-year dimensional panel",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    pos, neg = _import_anchors()
    logger.info(f"Loaded {len(pos)} positive + {len(neg)} negative anchors")

    directions = compute_direction_vectors(pos, neg, cache_db_path=args.cache_db)
    logger.info(f"Computed {len(directions)} dimensional direction vectors: {list(directions)}")

    tracks = ["full", "ctx"] if args.track == "both" else [args.track]
    track_paths = {
        "full": Path(args.text_embeddings_full),
        "ctx":  Path(args.text_embeddings_ctx),
    }

    if args.df_exploded is None:
        logger.warning("Skipping panel aggregation (df_exploded not provided)")
        return 0

    missing = [t for t in tracks if not track_paths[t].exists()]
    if missing:
        logger.warning(f"Skipping tracks (embedding files missing): {missing}")
        tracks = [t for t in tracks if t not in missing]
    if not tracks:
        logger.warning("No tracks available; aborting panel aggregation")
        return 0

    track_emb = {t: np.load(str(track_paths[t])) for t in tracks}
    for t, emb in track_emb.items():
        logger.info(f"  [{t}] embeddings shape: {emb.shape}")

    df_exploded = pd.read_parquet(args.df_exploded)
    panel = compute_dual_track_dimensions(df_exploded, track_emb, directions)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info(f"Wrote dual-track dimensional panel to {output_path}: {panel.shape}")
    logger.info(f"  Columns: {sorted(panel.columns)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
