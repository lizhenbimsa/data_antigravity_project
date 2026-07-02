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
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4

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
    model_id: str | None = None,
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
    model_id : optional
        None (默认) 时动态解析为 config/features.yaml::embedding_api.model
        (v3.15.0 = Qwen/Qwen3-Embedding-8B), 与 Stage 27 锚点缓存键同源 (SSOT);
        显式传入则按传入值。
    """
    if model_id is None:
        from news_process.core.config import load_config

        model_id = str(
            (load_config().get("embedding_api") or {}).get("model")
            or "Qwen/Qwen3-Embedding-8B"
        )
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
    model_id: str | None = None,
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
        # 📊 方向向量预归一化范数 = ‖pos_mean − neg_mean‖ = 正/负锚点均值的欧氏距离
        # (语义轴锐利度诊断)。白话: 范数越大 = 该维正面锚点与负面锚点在 embedding
        # 空间分得越开 = 语义轴越锐利 → 直接印证 banner 前提"4 维各载独立信息、
        # 分解有意义"; 范数 ≈ 0 才是上面的退化分支。纯日志、值已算好 (复用既有
        # `norm`)、仅喂 logger 后丢弃, golden-safe (镜像 geometry-of-culture 反义
        # 锚点对均值差的轴有效性诊断, 该构念出处 Kozlowski et al. 2019 ASR 已于
        # _log_environment_and_config 的 📖 块 emit)。
        logger.info(
            f"  [{dim_name}] direction norm (pre-normalize, ‖pos_mean − neg_mean‖) "
            f"= {sig4(norm)}"
        )
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
# 7. 多轨辅助函数 (plan v2.12, F-B2 / F-M3 / F-V2-B2 — 回写到
#    pipeline/features 层, 而非共享的 panel runner)
#
# 2026-07-03 (ROBUSTNESS_GAP_BACKFILL 计划 §3 B1): 维度分解扩到六轨 =
# {full, ctx, ss} × {MAIN Qwen, '_lg' text-embedding-3-large}。旧版 "ss 切片
# v1 延后 / 暂无 _ss.npy" 的豁免声明已被盘面证伪 (stage 27 主循环
# track×suffix 双循环全量产 .npy, 见 benefit_society.py:715-744), 故删除。
# ⚠ 两轴分工: `--track` 只控文本轨集 ('both'={full,ctx} 向后兼容,
# 'all'={full,ctx,ss}); `_lg` 后缀由独立 `--include-lg` 控制; 六轨 =
# track='all' AND include_lg。⚠ 铁律: MAIN 与 _lg co-primary 互为稳健性,
# both-or-neither (单边缺失 → 同族两列同置 NaN); 各轨 just-identified 并排,
# 禁混同一 over-identified Hansen J。
# ---------------------------------------------------------------------------

# 六键路径 SSOT: (suffix, track) → stage 27 落盘 .npy 路径 (文件名 = base{suffix}_{track},
# 与 benefit_society._persist_article_embeddings 拼接规则一致; suffix ∈ {'', '_lg'})。
_EMB_SUFFIXES = ("", "_lg")
_EMB_TRACKS = ("full", "ctx", "ss")
_DEFAULT_EMBEDDINGS = {
    (sfx, trk): f"news_process/data/processed/27_benefit_embeddings{sfx}_{trk}.npy"
    for sfx in _EMB_SUFFIXES for trk in _EMB_TRACKS
}


def _dim_col(dim: str, suffix: str, track: str) -> str:
    """维度列名 SSOT: benefit_{dim}{suffix}_{track} (**lg 中置**, 对齐 benefit_mean_lg_full).

    生成端 / both-or-neither 守卫 / merge wanted 白名单 / Table 9 模板变量名
    四方一律经本函数 (或其字面输出) 派生, 防任一侧手写漂移
    (gate = tests/test_benefit_dimension_tracks.py 三方同源断言)。
    """
    return f"benefit_{dim}{suffix}_{track}"


def _resolve_large_spec() -> dict:
    """取 config/features.yaml::embedding_large spec (dict; 缺失/空 → {})。

    ⚠ 空 spec 时调用方必须把整个 '_lg' suffix 从 specs 集剔除 (镜像
    benefit_society.py `if _LARGE_SPEC:` 优雅降级), **禁**把空 dict 传入
    spec_model 走 Qwen 默认回退 — 那会让 _lg 方向向量以错键
    ('Qwen/…', 'v0') 查缓存 → miss → RuntimeError 崩整个 CLI 含 MAIN 轨。
    """
    from news_process.core.config import load_config
    return load_config().get("embedding_large") or {}


def _spec_cache_keys(spec: dict) -> tuple[str, str]:
    """spec → (model_id, prompt_version) 缓存键二元组 (经 embedding_engine 取键 SSOT).

    _lg 期望值 = ('text-embedding-3-large', 'v1-2026-06-27-emb3large')。
    ⚠ 禁沿用 _resolve_prompt_version() — 它硬绑 MAIN 的 text_pipeline_version
    ('v4-2026-06-28-qwen3-8b'), 用在 _lg 锚点上 100% miss → RuntimeError。
    """
    from news_process.pipeline.text.embedding_engine import spec_model, spec_version
    return spec_model(spec, default="text-embedding-3-large"), spec_version(spec)


def compute_dual_track_dimensions(
    df_exploded: pd.DataFrame,
    track_to_embedding: dict,
    directions: dict[str, np.ndarray],
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
    directions_by_suffix: dict[str, dict[str, np.ndarray]] | None = None,
) -> pd.DataFrame:
    """把各轨子指数得分聚合进同一张 bank-year 面板.

    ``track_to_embedding`` 键两种形式 (向后兼容):
      - str 轨名 (``'full'``/``'ctx'``/``'ss'``) → MAIN spec (suffix ''), 用 ``directions``;
      - (track, suffix) 元组 → suffix ∈ {'', '_lg'}, ``'_lg'`` 用
        ``directions_by_suffix['_lg']`` (per-spec 方向向量, 2026-07-03 §3 B1)。

    ⚠ 投影配对铁律: 每 (track, suffix) 槽位的文本嵌入必须与**同 spec** 的方向
    向量配对 — MAIN Qwen 4096 维 vs _lg 3072 维, 跨 spec 混投影必崩 shape;
    此处显式断言 fail-loud (带 spec 名), 禁被优雅 skip 吞成静默 NaN。

    产出列名经 :func:`_dim_col` (``benefit_<dim><suffix>_<track>``, lg 中置)。
    """
    merged: pd.DataFrame | None = None
    for key, text_emb in track_to_embedding.items():
        track, suffix = (key, "") if isinstance(key, str) else key
        dirs = directions if suffix == "" else (directions_by_suffix or {}).get(suffix)
        if dirs is None:
            raise ValueError(
                f"track_to_embedding[{key!r}] 要求 suffix={suffix!r} 的方向向量, "
                f"但 directions_by_suffix 未提供该 spec (per-spec 配对铁律)"
            )
        if len(df_exploded) != len(text_emb):
            raise ValueError(
                f"df_exploded ({len(df_exploded)}) and text_embeddings[{key!r}] "
                f"({len(text_emb)}) length mismatch"
            )
        _dir_dim = len(next(iter(dirs.values())))
        if text_emb.ndim != 2 or text_emb.shape[1] != _dir_dim:
            raise ValueError(
                f"[{key!r}] embedding dim {text_emb.shape[1] if text_emb.ndim == 2 else text_emb.shape} "
                f"!= direction dim {_dir_dim} (spec={suffix or 'MAIN'}); "
                f"跨 spec 混投影禁止 — 检查 .npy 与方向向量是否同一嵌入空间"
            )
        track_panel = aggregate_to_bank_year(
            df_exploded, text_emb, dirs, bank_col=bank_col, year_col=year_col,
        )
        track_panel = track_panel.rename(columns={
            f"benefit_{dim}": _dim_col(dim, suffix, track) for dim in dirs
        })
        merged = (
            track_panel if merged is None
            else merged.merge(track_panel, on=[bank_col, year_col], how="outer")
        )
    assert merged is not None
    return merged


def _apply_both_or_neither(panel: pd.DataFrame, tracks: list[str]) -> pd.DataFrame:
    """co-primary both-or-neither 族级守卫 (2026-07-03 §3 B2, 镜像 benefit_society.py §6.5b).

    对每 (dim, track): ``benefit_{dim}_{track}`` 与 ``benefit_{dim}_lg_{track}``
    恰一侧有效 (另一侧缺列或全 NaN) → 两侧同置 NaN (缺列则补全-NaN 列),
    保证无单边孤儿。仅在 _lg spec 激活 (调用方判断) 时调用。
    """
    for dim in _DIMENSION_NAMES:
        for trk in tracks:
            main_c, lg_c = _dim_col(dim, "", trk), _dim_col(dim, "_lg", trk)
            main_ok = main_c in panel.columns and panel[main_c].notna().any()
            lg_ok = lg_c in panel.columns and panel[lg_c].notna().any()
            if main_ok != lg_ok:  # 恰一侧有效 → 同族两列同置 NaN
                logger.warning(
                    f"  ⚠ both-or-neither: ({dim}, {trk}) 单边有效 "
                    f"(MAIN={main_ok}, _lg={lg_ok}) → 两侧同置 NaN (无单边孤儿)")
                for c in (main_c, lg_c):
                    panel[c] = float("nan")
    return panel


_DIMENSION_NAMES = tuple(DIMENSION_INDICES)  # core_op / growth / resource / compliance


def merge_dimensions_to_panel(
    panel: pd.DataFrame | None = None,
    dimensions: pd.DataFrame | None = None,
    *,
    track: str = "both",
    tracks: list[str] | None = None,
    include_lg: bool = False,
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
        track:       'full' | 'ctx' | 'ss' | 'both' (={full,ctx} 向后兼容) |
                     'all' (={full,ctx,ss}, 2026-07-03 §3 B1)。
        tracks:      可选显式轨列表, 覆盖 ``track`` (承载缺 .npy 剪枝后的
                     任意轨组合, 如 ['full','ss']; main() 直接透传实跑轨)。
        include_lg:  并入 ``benefit_{dim}_lg_{track}`` 孪生列 (2026-07-03;
                     _lg 列缺失时按既有 fail-loud 契约报 lacks columns)。
        output_path: 可选 parquet 落盘路径 (副本, 禁与 panel_path 同路径)。

    Returns:
        合并后的面板副本 (含 4 × track × suffix 个 ``benefit_<dim>[<_lg>]_<track>`` 列)。

    Raises:
        ValueError: track 非法 / 维度列缺失 / output_path 指向主面板。
        FileNotFoundError: panel/dimensions parquet 缺失。
    """
    if tracks is None:
        if track not in ("full", "ctx", "ss", "both", "all"):
            raise ValueError(
                f"track must be 'full' | 'ctx' | 'ss' | 'both' | 'all', got {track!r}")
        tracks = (["full", "ctx"] if track == "both"
                  else ["full", "ctx", "ss"] if track == "all"
                  else [track])
    else:
        _bad = [t for t in tracks if t not in _EMB_TRACKS]
        if _bad:
            raise ValueError(f"tracks 含非法轨 {_bad}; 合法 = {_EMB_TRACKS}")

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

    _suffixes = ("", "_lg") if include_lg else ("",)
    wanted = [_dim_col(dim, sfx, t)
              for sfx in _suffixes for t in tracks for dim in _DIMENSION_NAMES]
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
def _log_environment_and_config(args, *, n_pos: int, n_neg: int, tracks: list[str]) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (Jha, Liu & Manela
    2026 RFS https://doi.org/10.1093/rfs/hhaf012; Kozlowski, Taddy & Evans 2019 ASR
    https://doi.org/10.1177/0003122419877135), 绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform

        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 模块: benefit_society.dimension_analysis "
                    "(普惠/CSR 4 维度子指数; 六轨 = full/ctx/ss × MAIN/_lg, 2026-07-03 §3 B1)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "锚点/文本 embedding 全经 Stage 27 缓存命中 ($0, 无新 API 调用) → 确定性投影")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 轨次: track={args.track} → 实跑 {tracks} ({len(tracks):,d} 轨)")
        logger.info(f"     · full embeddings: {args.text_embeddings_full or '(dir/SSOT 派生)'}")
        logger.info(f"     · ctx  embeddings: {args.text_embeddings_ctx or '(dir/SSOT 派生)'}")
        logger.info(f"     · ss   embeddings: {getattr(args, 'text_embeddings_ss', None) or '(dir/SSOT 派生)'}")
        logger.info(f"     · _lg 孪生: include_lg={getattr(args, 'include_lg', False)} | "
                    f"embeddings-dir={getattr(args, 'embeddings_dir', None) or '(SSOT 默认)'}")
        logger.info(f"     · df_exploded:     {args.df_exploded or '(未提供 → anchors-only 模式, 不落面板)'}")
        logger.info(f"     · LLM cache DB:    {args.cache_db or '(默认 Stage 27 路径)'}")
        logger.info(f"     · 维度面板输出:    {args.output}")
        logger.info(f"     · 面板桥接副本:    {args.merge_panel_output or '(未启用 Table 9 桥接)'}")

        logger.info("  ⚙ 运行配置")
        logger.info(f"     · 锚点: 正面={n_pos:,d} 句 / 负面={n_neg:,d} 句 (Stage 27 POSITIVE/NEGATIVE_ANCHORS)")
        logger.info(f"     · 维度划分 (DIMENSION_INDICES, {len(DIMENSION_INDICES):,d} 维, 与锚点 ①-⑩ 对齐):")
        for _dim, _idx in DIMENSION_INDICES.items():
            logger.info(f"        - {_dim:<10} 锚点索引 {_idx} → {DIMENSION_LABELS.get(_dim, _dim)}")
        logger.info("     · 投影: pos_mean − neg_mean → L2 归一化方向向量; 文本 embedding L2 归一 后 余弦投影")
        logger.info(f"     · 退化护栏: 方向向量范数 < {sig4(1e-10)} 判为退化 (degenerate) → 跳过该维度")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info("     · 双极锚点投影框架 (本模块直接构念出处): "
                    "Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? "
                    "A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. "
                    "https://doi.org/10.1093/rfs/hhaf012")
        logger.info("       → 正/负锚点句 embedding 均值之差定义语义方向, 文本投影到该方向衡量构念态度")
        logger.info("     · 嵌入空间语义维度 (方向向量 = 反义锚点对均值差, 规范出处): "
                    "Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture: "
                    "Analyzing the meanings of class through word embeddings. American Sociological "
                    "Review, 84(5), 905-949. https://doi.org/10.1177/0003122419877135")
        logger.info("       → 文化/构念维度可表示为 embedding 空间中由对立锚点张成的方向, 投影即得连续度量")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 计算 4 维度子指数, 并可选聚合到 bank-year 面板.

    Plan v2.12: ``--track {full,ctx,both}`` (默认 both) 产出 benefit 嵌入轴
    (2026-07-03 §3 B1 扩 'ss'/'all') 产出 ``benefit_{core_op,growth,resource,compliance}``
    的 full/ctx/ss 轨输出; ``--include-lg`` 并算 ``benefit_<dim>_lg_<track>`` co-primary
    孪生 (both-or-neither 守卫, 无单边孤儿)。

    成功或优雅跳过 (可选输入缺失) 时返回 0; 硬错误直接 raise。
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.dimension_analysis",
        description="4 维度子指数计算 (core_op / growth / resource / compliance; "
                    "六轨 full/ctx/ss × MAIN/_lg, 2026-07-03)",
        # F-V2-H2 向后兼容: 关闭前缀缩写匹配, 使旧版 --text-embeddings
        # (Phase 0) 与新版 --text-embeddings-full (v2.12) 不产生歧义。
        allow_abbrev=False,
    )
    parser.add_argument(
        "--track",
        # ⚠ 字面列表锁定 (test_benefit_society_dual_track 对 main 源码做双引号字面断言),
        # 禁改为纯 SSOT 表达式派生; 'both'={full,ctx} 向后兼容, 'all'={full,ctx,ss} (2026-07-03)
        choices=["full", "ctx", "ss", "both", "all"],
        default="both",
        help="Sentiment track(s) to compute (plan v2.12; 'all' = full+ctx+ss, 2026-07-03 §3 B1)",
    )
    parser.add_argument(
        "--include-lg",
        action="store_true",
        help="并算 _lg (text-embedding-3-large) co-primary 孪生 (2026-07-03 §3 B1; "
             "六轨 = --track all + --include-lg; embedding_large spec 缺失时优雅降级单 MAIN)",
    )
    # ⚠ 三参数 default=None 哨兵 (终审 #1, 2026-07-03): argparse 无法区分"用户显式传入"
    # 与"默认回填", 若带 SSOT 默认值则 --embeddings-dir 对 MAIN 三槽永不生效 →
    # 可静默产出 MAIN/_lg 跨目录混源面板。三级优先见 _slot_path: 真显式 > dir 派生 > SSOT 默认。
    parser.add_argument(
        "--text-embeddings-full",
        "--text-embeddings",  # legacy 别名 (Phase 0 脚手架时期的默认参数名; F-V2-H2 契约, 勿删)
        type=str,
        default=None,
        dest="text_embeddings_full",
        help="Path to Stage 27 full-track text embeddings (.npy). "
             "Legacy alias: --text-embeddings. 缺省时按 --embeddings-dir/SSOT 派生",
    )
    parser.add_argument(
        "--text-embeddings-ctx",
        type=str,
        default=None,
        help="Path to Stage 27 ctx-track text embeddings (.npy); 缺省时按 --embeddings-dir/SSOT 派生",
    )
    parser.add_argument(
        "--text-embeddings-ss",
        type=str,
        default=None,
        help="Path to Stage 27 ss-track text embeddings (.npy; 2026-07-03 §3 B1); 缺省时按 --embeddings-dir/SSOT 派生",
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        default=None,
        help="可选: stage 27 嵌入 .npy 所在目录 — _lg 系与未显式覆盖的路径按 "
             "27_benefit_embeddings{suffix}_{track}.npy 模式从此目录派生 "
             "(显式 --text-embeddings-* 优先; 2026-07-03 §3 B1)",
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

    start_time = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # ── 【功能】banner (黄金范式, 对齐 herd_decay main() / 已富集的 63 模块) ──
    logger.info("=" * 72)
    logger.info("benefit_society 维度分析: 普惠/CSR 4 维度子指数 "
                "(双极锚点投影; Jha-Liu-Manela 2026 RFS / Kozlowski et al. 2019 ASR)")
    logger.info("=" * 72)
    logger.info(
        "【功能】把 Stage 27 的普惠/社会效益单维锚点拆成 4 个子维度 "
        "(core_op 核心经营 / growth 成长 / resource 资源 / compliance 合规),"
    )
    logger.info(
        "        分别给每篇新闻一个'该维度态度有多正面'的连续投影分, 再聚合成 bank-year 面板,"
    )
    logger.info(
        "        供论文 Table 9 / H4 机制分解使用 (并入面板副本, 不改主 40_panel_yearly)。"
    )
    logger.info(
        "【方法】每维取若干正面锚点句与负面锚点句的 embedding 均值, 两均值之差 (再 L2 归一) = 该维语义方向;"
    )
    logger.info(
        "        把文本 embedding (Stage 27 缓存, full/ctx/ss × MAIN/_lg) L2 归一后对同 spec 方向向量做余弦投影 → 维度得分;"
    )
    logger.info(
        "        按 (target_bank, year) 等权均值聚合为 benefit_<dim>_<track> 列 (Jha 2026 Eq. 2)。"
    )
    logger.info(
        "【判读】投影分越大 = 该维度态度越正面; 4 维分散度高 = 单维锚点确含多面信息(分解有意义)。"
    )
    logger.info(
        "        某维方向向量范数 ≈ 0 (退化) = 该维正负锚点几乎同向, 该维被跳过(需检查锚点设计)。"
    )
    logger.info(
        "【确定性】锚点与文本 embedding 全经 Stage 27 缓存命中 ($0, 无新 API/网络); "
        "固定均值差 + L2 归一 + 余弦投影 → 确定性可复现。"
    )

    pos, neg = _import_anchors()
    logger.info(f"Loaded {len(pos)} positive + {len(neg)} negative anchors")

    # 轨集派生 (2026-07-03 §3 B1): 'both'={full,ctx} 向后兼容; 'all'={full,ctx,ss}
    tracks = (["full", "ctx"] if args.track == "both"
              else ["full", "ctx", "ss"] if args.track == "all"
              else [args.track])
    # _lg spec 门控: 空/缺失 → 整个 '_lg' suffix 剔除 + WARNING 退化单 MAIN
    # (禁把空 dict 传 spec_model 走 Qwen 默认回退 → 错键 miss → RuntimeError 崩 MAIN 轨)
    suffixes = [""]
    _lg_spec = _resolve_large_spec() if args.include_lg else {}
    if args.include_lg:
        if _lg_spec:
            suffixes.append("_lg")
        else:
            logger.warning(
                "--include-lg 已指定但 config embedding_large spec 缺失/空 → "
                "剔除 _lg suffix, 退化单 MAIN (both-or-neither: _lg 列不产出)")
    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24, 参数解析后打印)
    _log_environment_and_config(args, n_pos=len(pos), n_neg=len(neg), tracks=tracks)

    # per-spec 方向向量 (2026-07-03 §3 B1 铁律): MAIN 与 _lg 各算一遍 —
    # _lg 用 embedding_large 的缓存键二元组 (text-embedding-3-large, v1-2026-06-27-emb3large);
    # 跨 spec 混投影 (4096 vs 3072 维) 必崩, compute_dual_track_dimensions 内亦有 shape 守卫。
    _t = time.time()
    directions = compute_direction_vectors(pos, neg, cache_db_path=args.cache_db)
    directions_by_suffix: dict[str, dict] = {}
    if "_lg" in suffixes:
        _lg_model, _lg_ver = _spec_cache_keys(_lg_spec)
        directions_by_suffix["_lg"] = compute_direction_vectors(
            pos, neg, cache_db_path=args.cache_db,
            model_id=_lg_model, prompt_version=_lg_ver,
        )
    phase_durations['①方向向量计算'] = time.time() - _t
    logger.info(f"Computed {len(directions)} dimensional direction vectors: {list(directions)}"
                + (" (+_lg spec 同维数)" if "_lg" in suffixes else ""))
    # 六槽路径三级优先 (终审 #1 修正): ① 用户真显式 --text-embeddings-* (default=None 哨兵,
    # 非 None 即显式) → ② --embeddings-dir 按 27_benefit_embeddings{suffix}_{track}.npy 模式
    # 派生 (MAIN 与 _lg 六槽**同源**, 防跨目录混源) → ③ _DEFAULT_EMBEDDINGS SSOT 默认。
    _explicit = {
        ("", "full"): args.text_embeddings_full,
        ("", "ctx"): args.text_embeddings_ctx,
        ("", "ss"): args.text_embeddings_ss,
    }
    def _slot_path(sfx: str, trk: str) -> Path:
        _v = _explicit.get((sfx, trk))
        if _v is not None:
            return Path(_v)
        if args.embeddings_dir:
            return Path(args.embeddings_dir) / f"27_benefit_embeddings{sfx}_{trk}.npy"
        return Path(_DEFAULT_EMBEDDINGS[(sfx, trk)])
    track_paths = {(sfx, trk): _slot_path(sfx, trk)
                   for sfx in suffixes for trk in tracks}

    if args.df_exploded is None:
        logger.warning("Skipping panel aggregation (df_exploded not provided)")
        _log_phase_timing(phase_durations, start_time)
        return 0

    missing_slots = [k for k, p in track_paths.items() if not p.exists()]
    if missing_slots:
        logger.warning(f"Skipping slots (embedding files missing): {missing_slots}")
        for k in missing_slots:
            track_paths.pop(k)
    # 文本轨集按 MAIN 侧存活剪枝 (与旧语义一致: MAIN 轨缺 .npy → 该轨整体跳过)
    tracks = [t for t in tracks if ("", t) in track_paths]
    if not tracks:
        logger.warning("No tracks available; aborting panel aggregation")
        _log_phase_timing(phase_durations, start_time)
        return 0

    _t = time.time()
    # ⚠ 键序契约: compute_dual_track_dimensions 解包 (track, suffix); 路径 SSOT 键是 (suffix, track)
    track_emb = {(trk, sfx): np.load(str(p))
                 for (sfx, trk), p in track_paths.items() if trk in tracks}
    for k, emb in track_emb.items():
        logger.info(f"  [{k}] embeddings shape: {emb.shape}")

    df_exploded = pd.read_parquet(args.df_exploded)
    # 📂 df_exploded 来源信息 (article-bank 展开表, 驱动 bank-year 聚合的逐文章观测)。
    # 其行数须与各轨文本 embedding 行数严格相等 (见 aggregate_to_bank_year L266-269 /
    # compute_dual_track_dimensions L320-324 的长度匹配断言) —— 该不变量此前被断言却
    # 从未落日志, 此处补 provenance。纯日志、try/except 守卫、结果仅喂 logger 后丢弃,
    # golden-safe。
    try:
        _de_rows, _de_cols = df_exploded.shape
        logger.info(f"  📂 df_exploded 来源: {args.df_exploded}")
        logger.info(f"     · 形状: {_de_rows:,d} 行 × {_de_cols:,d} 列 "
                    "(行数须 == 各轨 embedding 行数, 否则聚合断言 fail-loud)")
        if 'target_bank' in df_exploded.columns:
            logger.info(f"     · 目标银行数 (target_bank.nunique): "
                        f"{df_exploded['target_bank'].nunique():,d}")
        if 'year' in df_exploded.columns:
            _yr = df_exploded['year'].dropna()
            if len(_yr):
                logger.info(f"     · 年份覆盖: {df_exploded['year'].nunique():,d} 个年度 "
                            f"(范围 {int(_yr.min())}–{int(_yr.max())})")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (df_exploded 来源信息打印失败, 忽略): {_e}")
    phase_durations['②加载 embeddings+df_exploded'] = time.time() - _t

    _t = time.time()
    panel = compute_dual_track_dimensions(
        df_exploded, track_emb, directions,
        directions_by_suffix=directions_by_suffix or None,
    )
    if "_lg" in suffixes:
        panel = _apply_both_or_neither(panel, tracks)
    phase_durations['③多轨投影+bank-year聚合'] = time.time() - _t

    # 📊 维度子指数横截面分布 (本模块的存在理由 = benefit_<dim>_<track> 这组测度;
    # 此前仅 log panel.shape + 列名, 零分布信息)。给审稿人维度分解测度的分布画像:
    # 逐列非空计数 + 均值/中位数/标准差/极值/四分位。纯日志、try/except 守卫、
    # describe/quantile 结果仅喂 logger 后丢弃, golden-safe (镜像 geography.py
    # fintech_exposure 的 mean/std/非空 范式)。
    try:
        _bcols = [c for c in panel.columns if c.startswith('benefit_')]
        _n_rows = len(panel)
        logger.info(f"  📊 维度子指数分布 ({len(_bcols):,d} 列, bank-year 行 n={_n_rows:,d})")
        for _c in _bcols:
            _s = panel[_c].dropna()
            if len(_s) == 0:
                logger.info(f"     · {_c}: 全空 (无非空观测)")
                continue
            _q = _s.quantile([0.25, 0.5, 0.75])
            logger.info(
                f"     · {_c}: 非空={len(_s):,d} "
                f"({pct4(len(_s) / _n_rows) if _n_rows else 'n/a'}), "
                f"mean={sig4(_s.mean())}, median={sig4(_q.loc[0.5])}, "
                f"std={sig4(_s.std())}, min={sig4(_s.min())}, "
                f"Q1={sig4(_q.loc[0.25])}, Q3={sig4(_q.loc[0.75])}, "
                f"max={sig4(_s.max())}"
            )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (维度子指数分布打印失败, 忽略): {_e}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _t = time.time()
    panel.to_parquet(output_path, index=False)
    phase_durations['④写维度面板parquet'] = time.time() - _t
    logger.info(f"Wrote dual-track dimensional panel to {output_path}: {panel.shape}")
    logger.info(f"  Columns: {sorted(panel.columns)}")

    # fix(omni-gapfill-10, 2026-06-12): 可选 Table 9 桥接 (面板副本, 不动主面板)。
    # 2026-07-03 §3 B1: 直接透传实跑轨列表 (剪枝安全, 取代 len(tracks)==2 → 'both'
    # 启发式 — 剪枝后剩 {full,ss} 组合时旧启发式会误判 'both' 致 merge 崩);
    # include_lg 跟随 _lg spec 实跑状态, 使 _lg 孪生列有真实桥接路径 (B4 Panel D 前置)。
    if args.merge_panel_output:
        _t = time.time()
        merge_dimensions_to_panel(
            dimensions=panel,
            tracks=tracks,
            include_lg=("_lg" in suffixes),
            panel_path=args.panel,
            output_path=args.merge_panel_output,
        )
        phase_durations['⑤Table9面板桥接副本'] = time.time() - _t

    _log_phase_timing(phase_durations, start_time)
    return 0


def _log_phase_timing(phase_durations: dict[str, float], start_time: float) -> None:
    """打印 ⏱ 各子阶段墙钟耗时汇总 (秒, sig4; 纯日志, golden-safe)。"""
    try:
        logger.info("  ⏱ 阶段计时 (墙钟秒)")
        for _name, _sec in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_sec)} s")
        logger.info(f"     · 总计 (含日志/导入): {sig4(time.time() - start_time)} s")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  计时汇总打印失败 (不影响处理): {e}")


if __name__ == "__main__":
    sys.exit(main())
