"""benefit_society — 替代锚点族 (A2 稳健性, audit-only).

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 P1.3:

用 **J-L-M 2026 RFS Internet Appendix A Table IA.1 (b) Chinese** 的 5 对
canonical 锚点集 (替代 ``pipeline/features/benefit_society.py`` 中扩充的
10 对锚点集), 复刻 benefit_society 的方向向量投影。

目的: 为计划验收标准 AC-A2 提供替代锚点族 —
"benefit_jlm_zh vs benefit_mean 的 β 符号一致 + 比值 > 0.5"。

**Audit-only 路径**: 本模块输出写入独立 parquet
(``data/processed/27c_alt_anchor_panel.parquet``), **不**修改主面板
``40_panel_yearly.parquet`` 及其 golden-snapshot schema。

复用 (而非复制) ``benefit_society.py`` 的嵌入缓存 + 投影机制 —
锚点数量不同 (5 对 vs 10 对), 但方向向量数学 (``mean(pos) − mean(neg)``)
与余弦投影字节级一致。

白话: 主指标用的是我们自己扩充的 10 对"尺子句"; 这里换成原论文官方的
5 对句子再量一遍 —— 如果两把尺子量出来的结论方向一致, 说明结果不是
被我们自选的句子"凑"出来的。

fix(omni-g-benefit-01, 2026-06-11) 链路重接线 (2026-05-29 主轨换模后失效):
- 锚点嵌入不再硬编码 SentenceTransformer("shibing624/...") 直调 — 改经统一引擎
  ``embedding_engine.embed_texts`` (穿透 LLMCache), spec 由文章嵌入 .npy 的
  sidecar ``model_id`` 解析 → 锚点与文章保证同嵌入空间 (维度错配根因消除)。
- 文章嵌入 .npy 必须带 stage 27 落盘的 ``.sidecar.json`` (model_id/n_rows
  一致性断言); 2026-05-09 陈旧无 sidecar 文件 → fail-loud, 不静默消费。
- 新增 ctx 轨 (``--text-embeddings-ctx`` → ``benefit_jlm_zh_*_ctx`` 列)。
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
    """加载 J-L-M 2026 Appendix A 中文 5 对锚点集.

    Returns
    -------
    tuple[list[str], list[str], dict]
        ``(positive_sentences, negative_sentences, metadata)``, metadata
        含 schema_version / anchor_family / sha256 / n_pairs.

    Raises
    ------
    FileNotFoundError
        yaml 文件缺失时.
    ValueError
        yaml schema 校验失败时 (n_pairs != 5、字段缺失、
        id 重复、或句子为空).
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


# ============================================================================
# fix(omni-g-benefit-01, 2026-06-11): 嵌入空间一致性基础设施
# ============================================================================


def load_article_embeddings(npy_path: Path | str) -> tuple[np.ndarray, dict]:
    """加载 stage 27 落盘的文章嵌入 .npy, 强制 sidecar 一致性断言。

    fix(omni-g-benefit-01, 2026-06-11): 2026-05-29 主轨换模 (text2vec 768 维 →
    text-embedding-3-small 1536 维) 后, 盘上无 sidecar 的 .npy 一律视为陈旧
    产物 fail-loud, 不静默消费 (历史 2026-05-09 npy 曾以 584 行 / 1536 维与
    857 行 df_exploded 错配)。sidecar 由 benefit_society._persist_article_embeddings
    产出, 含 model_id / n_rows / dim。

    Returns
    -------
    tuple[np.ndarray, dict]
        ``(embeddings (n_rows, dim), sidecar_metadata)``
    """
    npy_path = Path(npy_path)
    if not npy_path.exists():
        raise FileNotFoundError(f"article embeddings .npy not found: {npy_path}")
    sidecar_path = Path(f"{npy_path}.sidecar.json")
    if not sidecar_path.exists():
        raise FileNotFoundError(
            f"article-embedding sidecar missing: {sidecar_path} — 无 sidecar 的 "
            ".npy 视为 2026-05-29 换模前陈旧产物, 拒绝静默消费; 重跑 stage 27 "
            "(config benefit_society.cache_embeddings=true) 生成对齐的 .npy + sidecar"
        )
    meta = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if not meta.get("model_id"):
        raise ValueError(f"sidecar {sidecar_path} 缺 model_id, 无法做嵌入空间断言")
    emb = np.load(npy_path)
    if emb.ndim != 2:
        raise ValueError(f"article embeddings must be 2D, got shape {emb.shape}")
    n_rows = int(meta.get("n_rows", -1))
    if n_rows != emb.shape[0]:
        raise ValueError(
            f"sidecar n_rows={n_rows} != npy rows={emb.shape[0]} ({npy_path}): "
            "嵌入与 sidecar 不同代产物, 重跑 stage 27"
        )
    dim = int(meta.get("dim", -1))
    if dim != emb.shape[1]:
        raise ValueError(
            f"sidecar dim={dim} != npy dim={emb.shape[1]} ({npy_path})"
        )
    return emb, meta


def resolve_embedding_spec(model_id: str) -> dict:
    """按 model_id 解析 config/features.yaml 的 embedding spec。

    fix(omni-g-benefit-01, 2026-06-11): 锚点嵌入必须与文章嵌入同空间 —
    spec 不再硬编码 shibing624, 而是由文章 .npy sidecar 的 model_id 反查
    ``embedding_api`` (MAIN) / ``embedding_robustness`` (_t2v)。未知 model
    → fail-loud (无法保证同空间)。
    """
    from news_process.core.config import load_config

    cfg = load_config()
    for section in ("embedding_api", "embedding_robustness"):
        spec = cfg.get(section) or {}
        if str(spec.get("model") or "") == str(model_id):
            return spec
    raise ValueError(
        f"未知嵌入模型 {model_id!r}: 不匹配 config/features.yaml 的 "
        "embedding_api / embedding_robustness — 锚点与文章无法保证同嵌入空间"
    )


def make_anchor_embedding_fn(spec: dict, *, cache_db_path: str | None = None):
    """构造经统一引擎 (embedding_engine.embed_texts) 的锚点嵌入闭包。

    fix(omni-g-benefit-01, 2026-06-11): 替代原 SentenceTransformer("shibing624/…")
    硬编码直调 — 统一引擎穿透 LLMCache (API spec) / 本地确定性硬化 (local spec),
    与主管线 stage 27 共用缓存键命名空间。注: 真实 API 重算 deferred 到下次
    生产 run (锚点句量级 ~10 条, 受 NEWS_PROCESS_LLM_OFFLINE 离线守卫约束)。
    """
    if cache_db_path is None:
        from news_process.core.config import load_config

        paths = load_config().get("paths") or {}
        cache_db_path = paths.get("llm_cache_db")
        if not cache_db_path and paths.get("output_dir"):
            cache_db_path = str(Path(paths["output_dir"]) / "_llm_cache.db")

    def _fn(texts: Sequence[str]) -> np.ndarray:
        from news_process.pipeline.text import embedding_engine as _eng

        emb = _eng.embed_texts(
            list(texts), spec,
            cache_db_path=cache_db_path,
            log_prefix="JLM anchor embedding",
        )
        if emb is None:
            raise RuntimeError(
                "anchor embedding failed (embedding_engine.embed_texts → None)"
            )
        return emb

    return _fn


def compute_direction_vector(
    pos_sentences: Sequence[str],
    neg_sentences: Sequence[str],
    embedding_fn,
) -> np.ndarray:
    """计算单位范数方向向量 p = mean(pos) − mean(neg).

    数学上等价于逐对差分再取平均 (均值算子的线性可加性)。

    Parameters
    ----------
    pos_sentences, neg_sentences
        锚点句, 两侧数量必须相等.
    embedding_fn
        可调用对象 ``texts -> np.ndarray, 形状 (n, d)``. 生产路径用
        ``make_anchor_embedding_fn(spec)`` (统一引擎, 与文章嵌入同空间;
        fix(omni-g-benefit-01, 2026-06-11)); 测试可注入 mock.

    Returns
    -------
    np.ndarray
        单位范数方向向量, 形状 (d,).
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
    """把预计算好的文本嵌入投影到方向向量上 (余弦相似度).

    Parameters
    ----------
    text_embeddings
        文本嵌入数组, 形状 ``(n, d)`` (每篇文章一行).
    direction
        单位范数方向向量, 形状 ``(d,)``.

    Returns
    -------
    np.ndarray
        余弦投影值 ∈ ``[-1, 1]``, 形状 ``(n,)``.
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
    center: float | None = None,
    col_suffix: str = "",
) -> pd.DataFrame:
    """把文章级余弦得分聚合为 bank-year 面板.

    遵循 J-L-M 2026 Eq. (2) 的文章级 c=1 实例化:
    ``f_it = mean(银行 i 年度 t 内全部文章 j 的 a_ji)``.

    返回列 (``col_suffix`` 用于 ctx 轨 ``_ctx`` 后缀):
        ``benefit_jlm_zh_mean``, ``benefit_jlm_zh_std``,
        ``benefit_jlm_zh_pos_frac``, ``benefit_jlm_zh_neg_frac``

    fix(omni-g-benefit-02, 2026-06-11): pos/neg_frac 阈值与主模块 (benefit_society
    .py median-center, fix(benefitfrac-01)) 对齐 — ``center=None`` 时取本批
    scores 的 pooled median (各向异性嵌入空间下 sign-at-0 实测 ~97% 投影>0,
    饱和退化; J-L-M 5 对锚点族不改变该根因)。披露: 默认 center 为 in-sample
    median; 若需与主面板同阈值口径, 经 ``center=`` 显式传入主模块冻结 sidecar
    值 (data/processed/_benefit_center_sidecar.json)。

    fix(omni-g-benefit-05, 2026-06-11): 单观测 bank-year 的 std (ddof=1 未定义)
    保持 NaN, 不再 fillna(0) — 与主模块及核心 tone std 族口径一致。
    """
    if len(df_articles) != len(scores):
        raise ValueError(
            f"df_articles ({len(df_articles)}) and scores ({len(scores)}) length mismatch"
        )
    work = df_articles[[bank_col, year_col]].copy()
    work[score_col] = scores
    work = work.dropna(subset=[score_col])

    if center is None:
        center = float(work[score_col].median()) if len(work) else 0.0
        if not np.isfinite(center):
            center = 0.0

    agg = (
        work.groupby([bank_col, year_col])[score_col]
        .agg(**{
            f"benefit_jlm_zh_mean{col_suffix}": "mean",
            f"benefit_jlm_zh_std{col_suffix}": "std",
            f"benefit_jlm_zh_pos_frac{col_suffix}":
                lambda x, c=center: float((x > c).mean()),
            f"benefit_jlm_zh_neg_frac{col_suffix}":
                lambda x, c=center: float((x < c).mean()),
        })
        .reset_index()
    )
    return agg


def write_sidecar_json(
    panel_path: Path,
    metadata: dict[str, object],
    direction_sha: str,
    n_articles: int,
    n_bank_years: int,
    *,
    embedding_model: str = "shibing624/text2vec-base-chinese",
    embedding_dim: int = 768,
    tracks: tuple[str, ...] = ("full",),
) -> Path:
    """在 parquet 输出旁写入可复现性 sidecar JSON.

    fix(omni-g-benefit-01, 2026-06-11): embedding_model / embedding_dim 改为
    参数 (main() 传入文章 .npy sidecar 实际值) — 此前硬编码 shibing624/768,
    与 CLI help 声称的主管线 API 嵌入 (1536 维) 自相矛盾。keyword 默认值仅为
    旧调用方兼容保留, 生产路径必须传实际值。
    """
    sidecar = {
        "schema_version": "1.1",
        "plan_version": "v2.0 (J-L-M 2026 robustness alignment)",
        "task_id": "P1.3 A2 alternative anchor projection",
        "anchor_metadata": metadata,
        "direction_vector_sha256": direction_sha,
        "n_articles_scored": int(n_articles),
        "n_bank_year_obs": int(n_bank_years),
        "embedding_model": embedding_model,
        "embedding_dim": int(embedding_dim),
        "tracks": list(tracks),
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
        help=(
            "Path to stage 27 article-level embeddings .npy (full track; "
            "requires sibling .sidecar.json with model_id/n_rows — "
            "27_benefit_embeddings_full.npy, rows aligned with df_exploded)"
        ),
    )
    parser.add_argument(
        "--text-embeddings-ctx",
        type=str,
        default=None,
        help=(
            "Optional ctx-track embeddings .npy (27_benefit_embeddings_ctx.npy "
            "+ sidecar); produces benefit_jlm_zh_*_ctx columns "
            "(fix(omni-g-benefit-01, 2026-06-11): 补 ctx 轨)"
        ),
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

    # fix(omni-g-benefit-01, 2026-06-11): 文章嵌入须带 sidecar (fail-loud on
    # stale npy); 锚点经统一引擎用 sidecar model_id 反查的 spec 嵌入 → 同空间。
    text_embeddings, emb_meta = load_article_embeddings(args.text_embeddings_full)
    df_exploded = pd.read_parquet(args.df_exploded)
    if len(df_exploded) != text_embeddings.shape[0]:
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and embeddings "
            f"({text_embeddings.shape[0]}) length mismatch — 不同代产物, 重跑 stage 27"
        )
    model_id = str(emb_meta["model_id"])
    spec = resolve_embedding_spec(model_id)
    embedding_fn = make_anchor_embedding_fn(spec)
    logger.info(
        "Loaded text_embeddings shape=%s (model=%s), df_exploded len=%d",
        text_embeddings.shape,
        model_id,
        len(df_exploded),
    )

    direction = compute_direction_vector(pos, neg, embedding_fn)
    dir_sha = hashlib.sha256(direction.tobytes()).hexdigest()
    logger.info("Direction vector computed: norm=1.0, sha=%s", dir_sha[:16])

    scores = project_texts(text_embeddings, direction)
    panel = aggregate_to_bank_year(df_exploded, scores)
    tracks: list[str] = ["full"]

    # ctx 轨 (optional): 同一方向向量 (锚点 track-agnostic), ctx 文章嵌入投影
    if args.text_embeddings_ctx is not None:
        emb_ctx, ctx_meta = load_article_embeddings(args.text_embeddings_ctx)
        if str(ctx_meta["model_id"]) != model_id:
            raise ValueError(
                f"ctx embeddings model={ctx_meta['model_id']!r} != full track "
                f"model={model_id!r} — 双轨必须同嵌入空间"
            )
        if emb_ctx.shape[0] != len(df_exploded):
            raise ValueError(
                f"ctx embeddings rows ({emb_ctx.shape[0]}) != df_exploded "
                f"({len(df_exploded)})"
            )
        scores_ctx = project_texts(emb_ctx, direction)
        panel_ctx = aggregate_to_bank_year(df_exploded, scores_ctx,
                                           col_suffix="_ctx")
        panel = panel.merge(panel_ctx, on=["target_bank", "year"], how="outer")
        tracks.append("ctx")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info("Wrote alt-anchor panel: %s (%d bank-year obs)", output_path, len(panel))

    sidecar_path = write_sidecar_json(
        output_path, meta, dir_sha,
        n_articles=len(scores), n_bank_years=len(panel),
        embedding_model=model_id,
        embedding_dim=int(text_embeddings.shape[1]),
        tracks=tuple(tracks),
    )
    logger.info("Wrote sidecar JSON: %s", sidecar_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
