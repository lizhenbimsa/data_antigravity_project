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
    """从 Stage 27 导入 POSITIVE/NEGATIVE 锚点, 带版本容错回退."""
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
    """解析 Stage 27 实际使用的 prompt_version (F7 fix).

    Stage 27 以 ``EMBEDDING_CONFIG['text_pipeline_version']`` 为键存储锚点
    embedding (见 news_process.pipeline.features.benefit_society)。若此处用了
    不同的值, 会静默 miss 缓存并尝试调付费 API。因此动态解析, 并带安全回退。
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
    """经 LLMCache 取锚点句子的 embedding.

    若锚点已被 Stage 27 嵌入过, 则全部缓存命中、不产生任何新 API 调用;
    否则抛 RuntimeError 提示调用方先跑 Stage 27。

    Parameters
    ----------
    prompt_version : optional
        None (默认) 时经 [_resolve_prompt_version] 自动解析为 Stage 27 的值;
        显式传入则按传入值。
    """
    if prompt_version is None:
        prompt_version = _resolve_prompt_version()
    try:
        from news_process.core.caching import LLMCache
    except ImportError as e:
        raise RuntimeError(f"news_process.core.caching unavailable: {e}") from e

    if cache_db_path is None:
        # 默认缓存路径与 Stage 27 保持一致
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
    prompt_version: str | None = None,  # F7: None 时自动解析为 Stage 27 的值
) -> dict[str, np.ndarray]:
    """计算 4 个维度的方向向量.

    白话: 每个维度取若干"正面锚点句"与"负面锚点句"的 embedding 均值,
    两均值之差就是该维度的语义方向; 之后把新闻文本投影到这个方向上,
    投影值越大表示该维度态度越正面。

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
    """把文本 embedding 投影到各维度方向向量上.

    Parameters
    ----------
    text_embeddings : np.ndarray, shape (n_texts, dim)
        预计算好的文本 embedding (如来自 Stage 27 [27_benefit_embeddings_full.npy])
    directions : dict
        [compute_direction_vectors] 的输出。

    Returns
    -------
    dict
        {dim_name: shape 为 (n_texts,) 的 ndarray} 余弦投影值
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
    bank_col: str = "target_bank",  # F6: 与 40_panel_yearly.parquet schema 对齐
    year_col: str = "year",
) -> pd.DataFrame:
    """把维度得分聚合到 bank-year 面板 (等权均值, per Jha 2026 Eq. 2)."""
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
# 7. 双轨辅助函数 (plan v2.12, F-B2 / F-M3 / F-V2-B2 — 回写到
#    pipeline/features 层, 而非共享的 panel runner)
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
    """把各轨子指数得分聚合进同一张 bank-year 面板.

    对 ``track_to_embedding`` 中的每个轨键 (通常为 ``{'full', 'ctx'}``),
    产出以 (bank_col, year_col) 为键的 ``benefit_<dim>_<track>`` 列。

    返回合并后的 bank-year DataFrame。
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


_DIMENSION_NAMES = tuple(DIMENSION_INDICES)  # core_op / growth / resource / compliance


def merge_dimensions_to_panel(
    panel: pd.DataFrame | None = None,
    dimensions: pd.DataFrame | None = None,
    *,
    track: str = "both",
    panel_path: str | Path = "news_process/data/processed/40_panel_yearly.parquet",
    dimensions_path: str | Path = "news_process/data/processed/27_benefit_dimensions_panel.parquet",
    bank_col: str = "target_bank",
    year_col: str = "year",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """把 4 维度子指数列并入 bank-year 面板副本 (Table 9 / H4 机制前置).

    fix(omni-gapfill-10, 2026-06-12): 18_table9_dimension_decomposition.do.tmpl
    自始声称前置 "pipeline/features/benefit_society.py merge_dimensions_to_panel"
    — 该函数全仓不存在 (幻影前置), dimension_analysis CLI 只写孤儿
    27_benefit_dimensions_panel.parquet, 无任何代码把 benefit_<dim>_<track>
    桥进面板 → Table 9 永远空守卫跳过。本函数补真实桥接:

    - 左连接 (bank_col, year_col), 面板行数不变;
    - 只并入所选 track 的 ``benefit_{core_op,growth,resource,compliance}_{track}``;
    - **不改写主 40_panel_yearly.parquet** (golden 锚定): ``output_path`` 显式
      指向主面板路径时 fail-loud; 默认仅返回 DataFrame, 由调用方导出 .dta 副本。

    Args:
        panel:       面板 DataFrame; None 时读 ``panel_path``。
        dimensions:  dimension_analysis CLI 产物 DataFrame; None 时读
                     ``dimensions_path``。
        track:       'full' | 'ctx' | 'both'。
        output_path: 可选 parquet 落盘路径 (副本, 禁与 panel_path 同路径)。

    Returns:
        合并后的面板副本 (含 4×track 个 ``benefit_<dim>_<track>`` 列)。

    Raises:
        ValueError: track 非法 / 维度列缺失 / output_path 指向主面板。
        FileNotFoundError: panel/dimensions parquet 缺失。
    """
    if track not in ("full", "ctx", "both"):
        raise ValueError(f"track must be 'full' | 'ctx' | 'both', got {track!r}")
    tracks = ["full", "ctx"] if track == "both" else [track]

    if panel is None:
        panel_p = Path(panel_path)
        if not panel_p.exists():
            raise FileNotFoundError(f"panel parquet not found: {panel_p}")
        panel = pd.read_parquet(panel_p)
    if dimensions is None:
        dim_p = Path(dimensions_path)
        if not dim_p.exists():
            raise FileNotFoundError(
                f"dimensions parquet not found: {dim_p}. "
                "Run: python -m news_process.papers.benefit_society.dimension_analysis "
                "--df-exploded <exploded.parquet> --track both"
            )
        dimensions = pd.read_parquet(dim_p)

    wanted = [f"benefit_{dim}_{t}" for t in tracks for dim in _DIMENSION_NAMES]
    missing = [c for c in wanted if c not in dimensions.columns]
    if missing:
        raise ValueError(
            f"dimensions panel lacks columns {missing}; "
            f"available: {sorted(c for c in dimensions.columns if c.startswith('benefit_'))}"
        )
    for key in (bank_col, year_col):
        if key not in panel.columns or key not in dimensions.columns:
            raise ValueError(f"merge key {key!r} missing in panel and/or dimensions")

    merged = panel.merge(
        dimensions[[bank_col, year_col, *wanted]],
        on=[bank_col, year_col],
        how="left",
        validate="one_to_one",
    )

    if output_path is not None:
        out_p = Path(output_path)
        if out_p.resolve() == Path(panel_path).resolve():
            raise ValueError(
                "refusing to overwrite the main panel parquet "
                f"({panel_path}); write a sidecar copy instead (golden anchor)."
            )
        out_p.parent.mkdir(parents=True, exist_ok=True)
        merged.to_parquet(out_p, index=False)
        logger.info(f"Wrote dimension-merged panel copy to {out_p}: {merged.shape}")

    return merged


# ---------------------------------------------------------------------------
# 8. CLI 入口
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 计算 4 维度子指数, 并可选聚合到 bank-year 面板.

    Plan v2.12: ``--track {full,ctx,both}`` (默认 both) 产出双轨输出
    ``benefit_{core_op,growth,resource,compliance}_{full,ctx}``。

    成功或优雅跳过 (可选输入缺失) 时返回 0; 硬错误直接 raise。
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.dimension_analysis",
        description="4 维度子指数计算 (core_op / growth / resource / compliance, 双轨)",
        # F-V2-H2 向后兼容: 关闭前缀缩写匹配, 使旧版 --text-embeddings
        # (Phase 0) 与新版 --text-embeddings-full (v2.12) 不产生歧义。
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
        "--text-embeddings",  # legacy 别名 (Phase 0 脚手架时期的默认参数名)
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
    # fix(omni-gapfill-10, 2026-06-12): Table 9 桥接 — 可选地把维度列并入面板
    # 副本 (merge_dimensions_to_panel; 禁写主 40_panel_yearly.parquet)。
    parser.add_argument(
        "--panel",
        type=str,
        default="news_process/data/processed/40_panel_yearly.parquet",
        help="Main bank-year panel parquet (read-only merge base)",
    )
    parser.add_argument(
        "--merge-panel-output",
        type=str,
        default=None,
        help="Optional: write dimension-merged panel COPY parquet here "
             "(refuses to overwrite --panel; Table 9 prerequisite)",
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

    # fix(omni-gapfill-10, 2026-06-12): 可选 Table 9 桥接 (面板副本, 不动主面板)。
    # `tracks` 已剔除嵌入缺失轨 — 只并入实际算出的轨, 防 merge 因列缺失 fail-loud。
    if args.merge_panel_output:
        merge_dimensions_to_panel(
            dimensions=panel,
            track="both" if len(tracks) == 2 else tracks[0],
            panel_path=args.panel,
            output_path=args.merge_panel_output,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
