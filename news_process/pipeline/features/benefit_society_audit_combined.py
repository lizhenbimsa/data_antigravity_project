"""benefit_society — Combined audit-only pipeline (P1.6).

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
Orchestrates ``benefit_society_alt_anchor`` (J-L-M canonical 5-pair) +
``benefit_society_placebo`` (4 business-line + 1 neutral) into a single
audit-only output:

    data/processed/27c_alt_anchor_and_placebo_panel.parquet

Schema (key = target_bank + year):
    - benefit_jlm_zh_mean / std / pos_frac / neg_frac  (+ ``_ctx`` twin 列,
      当提供 ctx 轨嵌入时; fix(omni-g-benefit-01, 2026-06-11) 补 ctx 轨)
    - benefit_placebo_housing_loans_mean
    - benefit_placebo_credit_cards_mean
    - benefit_placebo_intermediate_business_mean
    - benefit_placebo_branch_channel_mean
    - benefit_placebo_general_corporate_mean   (neutral baseline)
      (placebo 列同样有 ``_ctx`` twin)

Sidecar JSON: ``...sidecar.json`` with yaml SHA-256 anchors + match counts.

**Critical**: does not touch main panel; this is audit-only path.

fix(omni-g-benefit-01, 2026-06-11) 链路重接线 (2026-05-29 主轨换模后失效):
- 锚点嵌入不再硬编码 SentenceTransformer("shibing624/...") — 经统一引擎
  ``embedding_engine.embed_texts``, spec 由文章嵌入 .npy 的 sidecar
  ``model_id`` 反查 → 锚点与文章同嵌入空间 (维度错配根因消除);
- 输入 .npy 必须带 stage 27 落盘的 ``.sidecar.json`` (fail-loud on stale);
  ``--main-direction-npy`` 的产出方 = stage 27 ``27_benefit_direction.npy``;
- 显式 seed (np.random.seed + sidecar 记录): 当前链路确定性, seed 守卫
  未来抽样步; 嵌入真重算 deferred 到下次生产 run (锚点 ~10 句, $≈0)。
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
    load_article_embeddings,
    load_jlm_zh_anchors,
    make_anchor_embedding_fn,
    resolve_embedding_spec,
)
from news_process.pipeline.features.benefit_society_alt_anchor import (
    project_texts as _alt_project,
)
from news_process.pipeline.features.benefit_society_placebo import (
    compute_placebo_projection,
    load_placebo_keywords,
)

#: 默认随机种子 — 与 Stata 模板族 RANDOM_SEED 占位符 (20260516) 同值。
DEFAULT_SEED = 20260516

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
    text_embeddings_ctx: np.ndarray | None = None,
    anchor_embedding_fn=None,
    embedding_model_id: str | None = None,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Build the combined audit panel.

    Parameters
    ----------
    df_exploded
        Article-bank DataFrame (must have target_bank, year, 标题, 内容).
    text_embeddings
        Pre-computed article embeddings, shape ``(n_articles, d)`` — full track
        (stage 27 ``27_benefit_embeddings_full.npy``; 行序对齐 df_exploded,
        空文本行=NaN)。fix(omni-g-benefit-01, 2026-06-11): 不再假设
        shibing624/768 — 维度由数组自描述, 模型由 ``embedding_model_id`` 声明。
    main_direction
        Main 10-anchor fintech direction vector (used for placebo subset
        projection); stage 27 ``27_benefit_direction.npy`` (未归一, 本函数
        消费端归一)。
    text_embeddings_ctx
        Optional ctx-track embeddings (同 model / 同行序) → ``_ctx`` twin 列。
    anchor_embedding_fn
        Injectable anchor-embedding closure (tests). ``None`` → 经
        ``make_anchor_embedding_fn(resolve_embedding_spec(model_id))`` 构造
        (统一引擎, 与文章同空间)。
    embedding_model_id
        文章嵌入的 model_id (来自 .npy sidecar)。``None`` → 取 config MAIN spec。
    seed
        显式随机种子 (fix(omni-g-benefit-01, 2026-06-11)): 当前链路无随机步
        (确定性), seed 守卫未来抽样步并记录进 sidecar metadata。

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
    if text_embeddings.ndim == 2 and main_direction.shape[0] != text_embeddings.shape[1]:
        raise ValueError(
            f"Dimension mismatch: main_direction d={main_direction.shape[0]} vs "
            f"text_embeddings d={text_embeddings.shape[1]} — 方向向量与文章嵌入"
            "不同空间 (2026-05-29 换模错配根因), 重跑 stage 27 产出配对产物"
        )
    if text_embeddings_ctx is not None and len(df_exploded) != len(text_embeddings_ctx):
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and text_embeddings_ctx "
            f"({len(text_embeddings_ctx)}) length mismatch"
        )

    np.random.seed(seed)  # 显式 seed (确定性披露见 docstring)

    # ---- 1) Alt anchor (J-L-M 5-pair) — anchors embedded via unified engine
    if embedding_model_id is None:
        from news_process.core.config import load_config

        embedding_model_id = str(
            (load_config().get("embedding_api") or {}).get("model")
            or "text-embedding-3-small"
        )
    if anchor_embedding_fn is None:
        anchor_embedding_fn = make_anchor_embedding_fn(
            resolve_embedding_spec(embedding_model_id)
        )

    pos, neg, alt_meta = load_jlm_zh_anchors()
    alt_dir = _alt_direction(pos, neg, anchor_embedding_fn)
    alt_scores = _alt_project(text_embeddings, alt_dir)
    alt_panel = _alt_aggregate(
        df_exploded, alt_scores, bank_col=bank_col, year_col=year_col
    )
    if text_embeddings_ctx is not None:
        alt_scores_ctx = _alt_project(text_embeddings_ctx, alt_dir)
        alt_panel_ctx = _alt_aggregate(
            df_exploded, alt_scores_ctx,
            bank_col=bank_col, year_col=year_col, col_suffix="_ctx",
        )
        alt_panel = alt_panel.merge(
            alt_panel_ctx, on=[bank_col, year_col], how="outer"
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
    if text_embeddings_ctx is not None:
        # ctx twin: 同关键词掩码 (track-agnostic 文本过滤) + ctx 嵌入投影
        placebo_panel_ctx, _ = compute_placebo_projection(
            df_exploded,
            text_embeddings_ctx,
            main_direction,
            keyword_sets,
            bank_col=bank_col,
            year_col=year_col,
            col_suffix="_ctx",
        )
        placebo_panel = placebo_panel.merge(
            placebo_panel_ctx, on=[bank_col, year_col], how="outer"
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
        "schema_version": "1.1",
        "plan_version": "v2.0 (J-L-M 2026 robustness alignment)",
        "task_id": "P1.6 audit-only combined panel",
        "embedding_model": embedding_model_id,
        "embedding_dim": int(text_embeddings.shape[1]) if text_embeddings.ndim == 2 else None,
        "tracks": ["full", "ctx"] if text_embeddings_ctx is not None else ["full"],
        "random_seed": int(seed),
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
        help=(
            "Path to stage 27 article embeddings .npy (full track; requires "
            "sibling .sidecar.json — 27_benefit_embeddings_full.npy)"
        ),
    )
    parser.add_argument(
        "--text-embeddings-ctx",
        type=str,
        default=None,
        help=(
            "Optional ctx-track embeddings .npy (+ sidecar) → *_ctx twin 列 "
            "(fix(omni-g-benefit-01, 2026-06-11): 补 ctx 轨)"
        ),
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
        help=(
            "Path to MAIN 10-anchor fintech direction .npy (stage 27 落盘的 "
            "27_benefit_direction.npy; used for placebo projection)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=(
            "显式随机种子 (记录进 sidecar; 当前链路确定性, 守卫未来抽样步; "
            "fix(omni-g-benefit-01, 2026-06-11))"
        ),
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

    # fix(omni-g-benefit-01, 2026-06-11): sidecar 强制 (fail-loud on stale npy)
    # + model_id 反查 spec → 锚点与文章同嵌入空间。
    text_embeddings, emb_meta = load_article_embeddings(args.text_embeddings_full)
    model_id = str(emb_meta["model_id"])
    df_exploded = pd.read_parquet(args.df_exploded)
    if len(df_exploded) != text_embeddings.shape[0]:
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and embeddings "
            f"({text_embeddings.shape[0]}) length mismatch — 不同代产物, 重跑 stage 27"
        )
    main_direction = np.load(args.main_direction_npy)
    direction_sidecar = Path(f"{args.main_direction_npy}.sidecar.json")
    if direction_sidecar.exists():
        dir_meta = json.loads(direction_sidecar.read_text(encoding="utf-8"))
        if str(dir_meta.get("model_id") or model_id) != model_id:
            raise ValueError(
                f"direction model={dir_meta.get('model_id')!r} != article "
                f"embeddings model={model_id!r} — 方向向量与文章不同空间"
            )

    text_embeddings_ctx = None
    if args.text_embeddings_ctx is not None:
        text_embeddings_ctx, ctx_meta = load_article_embeddings(
            args.text_embeddings_ctx
        )
        if str(ctx_meta["model_id"]) != model_id:
            raise ValueError(
                f"ctx embeddings model={ctx_meta['model_id']!r} != full track "
                f"model={model_id!r} — 双轨必须同嵌入空间"
            )

    logger.info(
        "Loaded embeddings shape=%s (model=%s) / df len=%d / direction shape=%s / ctx=%s",
        text_embeddings.shape,
        model_id,
        len(df_exploded),
        main_direction.shape,
        "yes" if text_embeddings_ctx is not None else "no",
    )

    combined, meta = build_audit_panel(
        df_exploded,
        text_embeddings,
        main_direction,
        text_embeddings_ctx=text_embeddings_ctx,
        embedding_model_id=model_id,
        seed=args.seed,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, index=False)
    logger.info("Wrote audit panel: %s (%d bank-year obs)", output_path, len(combined))

    sidecar_path = write_sidecar_json(output_path, meta)
    logger.info("Wrote sidecar JSON: %s", sidecar_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
