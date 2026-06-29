"""benefit_society — 替代锚点族 (A2 稳健性, audit-only).

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 P1.3:

用 **J-L-M 2026 RFS Internet Appendix A Table IA.1 (b) Chinese** 的 5 对
canonical 锚点集 (替代 ``pipeline/features/benefit_society.py`` 中扩充的
10 对锚点集), 复刻 benefit_society 的方向向量投影。

目的: 为计划验收标准 AC-A2 提供替代锚点族 —
"benefit_jlm_zh vs benefit_mean 的 β 符号一致 + 比值 > 0.5"。

**Audit-only 路径**: 本模块输出写入独立 parquet
(``data/processed/80_alt_anchor_panel.parquet``), **不**修改主面板
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
- 第三轨 ss 轨 (``--text-embeddings-ss`` → ``benefit_jlm_zh_*_ss`` 列; 银行+金科同句
  共现, content_ss; 与 full/ctx 并列, 投影机制 track-agnostic, 仅切换文章嵌入子集)。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import platform
import sys
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import yaml

from news_process.core.logging import pct4, sig4

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

    fix(omni-g-benefit-01, 2026-06-11): 历次主轨换模 (2026-05-29 text2vec 768 维 →
    text-embedding-3-small 1536 维; v3.15.0 起 Qwen/Qwen3-Embedding-8B 4096 维) 后, 盘上无 sidecar 的 .npy 一律视为陈旧
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
    ``embedding_api`` (MAIN, Qwen) / ``embedding_large`` (_lg, co-primary,
    text-embedding-3-large)。未知 model → fail-loud (无法保证同空间)。
    (v3.14.0 已整体移除本地稳健轨 embedding_robustness/_t2v 与 embedding_bge/_bge,
    故反查元组只剩双 API 模型。)
    """
    from news_process.core.config import load_config

    cfg = load_config()
    for section in ("embedding_api", "embedding_large"):
        spec = cfg.get(section) or {}
        if str(spec.get("model") or "") == str(model_id):
            return spec
    raise ValueError(
        f"未知嵌入模型 {model_id!r}: 不匹配 config/features.yaml 的 "
        "embedding_api / embedding_large — "
        "锚点与文章无法保证同嵌入空间"
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

    返回列 (``col_suffix`` track-agnostic: ctx 轨传 ``_ctx`` / ss 轨传 ``_ss``):
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
    embedding_model: str = "(unknown — pass actual model_id)",
    embedding_dim: int = -1,
    tracks: tuple[str, ...] = ("full",),
) -> Path:
    """在 parquet 输出旁写入可复现性 sidecar JSON.

    fix(omni-g-benefit-01, 2026-06-11): embedding_model / embedding_dim 改为
    参数 (main() 传入文章 .npy sidecar 实际值)。keyword 默认值仅为旧调用方兼容
    保留 (中性占位, 不再硬编码具体模型), 生产路径必须传实际值。
    (v3.14.0: 原默认 shibing624/text2vec-base-chinese / 768 维已随本地稳健轨整体移除。)
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


def _log_environment_config_method(args: argparse.Namespace) -> None:
    """打印 🧭 环境 / 📂 输入输出 / ⚙ 配置 / 📖 方法论依据 四块 banner.

    顶刊审计标准的运行期日志 (照搬 tone_words.py 范式)。纯日志, 不改任何
    产物 / schema / 控制流 (golden-safe)。失败用 try/except 包住, 绝不让日志
    块崩阶段。引文逐字取自经核验注册表 (status=match)。
    """
    try:
        _run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
        _offline = os.environ.get("NEWS_PROCESS_LLM_OFFLINE")
        logger.info("  🧭 项目 / 环境信息")
        logger.info(
            "     · 阶段: 80_alt_anchor (J-L-M 2026 替代锚点族, A2 稳健性, audit-only sibling)"
        )
        logger.info(
            "     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.11.1"
        )
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            f"LLM_OFFLINE={_offline or '(未设置)'}"
        )
        logger.info(
            "     · 确定性/成本: 投影/聚合纯 CPU·确定性 ($0); 锚点嵌入经统一引擎穿透 LLMCache "
            "(命中即 $0, miss 受离线守卫约束 deferred 到生产 run)"
        )

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 锚点 yaml:        {args.anchors_yaml or '(默认 config/jlm2026_chinese_anchors.yaml)'}")
        logger.info(f"     · full 轨嵌入:      {args.text_embeddings_full or '(未提供 → 仅校验 yaml)'}")
        logger.info(f"     · ctx 轨嵌入(可选): {args.text_embeddings_ctx or '(未提供)'}")
        logger.info(f"     · ss 轨嵌入(可选):  {args.text_embeddings_ss or '(未提供)'}")
        logger.info(f"     · df_exploded:      {args.df_exploded or '(未提供)'}")
        logger.info(f"     · 输出面板:         {args.output}")
        logger.info(
            "     · audit-only: 写独立 80_alt_anchor_panel.parquet, 不改主面板 "
            "40_panel_yearly.parquet 及其 golden-snapshot schema"
        )

        logger.info("  ⚙ 运行配置")
        logger.info(
            "     · 锚点集: J-L-M 2026 Appendix A Table IA.1(b) 中文 5 对 canonical 锚点 "
            "(替代主模块扩充的 10 对)"
        )
        logger.info(
            "     · 方向向量: p = mean(pos) − mean(neg) (单位范数); 文章投影 = 余弦相似度 ∈ [−1,1]"
        )
        logger.info(
            "     · 聚合: J-L-M Eq.(2) 文章级 c=1 → bank-year 均值; pos/neg_frac center=in-sample median "
            "(各向异性嵌入空间 sign-at-0 饱和退化, 故中位居中)"
        )
        logger.info(
            f"     · 轨道: full{' +ctx' if args.text_embeddings_ctx else ''}"
            f"{' +ss' if args.text_embeddings_ss else ''} (投影机制 track-agnostic, 仅切换文章嵌入子集)"
        )
        logger.info(
            f"     · validate_only={args.validate_only} (仅校验 yaml schema, 不跑投影)"
        )

        logger.info("  📖 方法论依据 (核心方法的学术出处, 经核验注册表逐字照抄)")
        logger.info(
            "     · 语言嵌入 benefit-society 方向投影: "
            "Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? "
            "A language embedding approach. The Review of Financial Studies, 39(5), "
            "1227-1266. https://doi.org/10.1093/rfs/hhaf012"
        )
        logger.info(
            "       → 本阶段直接复刻 J-L-M 官方 5 对锚点, 与自选 10 对互为稳健性对照"
        )
        logger.info(
            "     · 极性对锚点 → 方向向量 (geometry-of-culture): "
            "Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture: "
            "Analyzing the meanings of class through word embeddings. American Sociological "
            "Review, 84(5), 905-949. https://doi.org/10.1177/0003122419877135"
        )
        logger.info(
            "       → mean(pos) − mean(neg) 构造语义对立轴, 投影量化文本在该轴上的位置"
        )
        logger.info(
            "     · 句嵌入引擎: "
            "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using "
            "Siamese BERT-networks. In Proceedings of the 2019 Conference on Empirical Methods "
            "in Natural Language Processing and the 9th International Joint Conference on Natural "
            "Language Processing (EMNLP-IJCNLP) (pp. 3980-3990). Association for Computational "
            "Linguistics. https://doi.org/10.18653/v1/D19-1410"
        )
        logger.info(
            "       → 锚点句与文章在同一句嵌入空间 (model_id 由 stage 27 sidecar 反查), 保证可比"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def _log_result_analysis(
    panel: pd.DataFrame,
    scores: np.ndarray,
    tracks: Sequence[str],
    meta: dict,
) -> None:
    """打印 📊 关键指标解读 — 把真实算出的统计量对照阈值给 好/临界/坏 判读.

    纯日志, 只读已算出的真实值, 不改任何产物 (golden-safe)。所有非整数数字
    用 sig4/pct4 渲染 (4 位有效数字)。失败用 try/except 包住。
    """
    try:
        logger.info("  📊 关键指标解读 (替代锚点投影结果, 数字均 4 位有效数字)")
        n_obs = len(panel)
        # ① 面板深度 (T=2 小样本下退化警告)
        n_banks = panel["target_bank"].nunique() if "target_bank" in panel else 0
        n_years = panel["year"].nunique() if "year" in panel else 0
        logger.info(
            f"     ① 面板规模: {n_obs:,d} bank-year obs | 银行 {n_banks:,d} | 年份 {n_years:,d}"
        )
        if n_obs < 30:
            logger.info(
                "        ⚠ 小样本 (<30 obs): A2 β 符号/比值验收在生产规模 (T=18) 才有充分功效, "
                "本盘 T=2 试跑仅作链路自检 (优雅降级)"
            )

        # ② 文章级投影分布
        sc = np.asarray(scores, dtype=np.float64)
        sc = sc[np.isfinite(sc)]
        if sc.size:
            s_mean = float(sc.mean())
            s_std = float(sc.std(ddof=1)) if sc.size > 1 else float("nan")
            s_pos = float((sc > 0).mean())
            s_med = float(np.median(sc))
            s_min = float(sc.min())
            s_max = float(sc.max())
            logger.info(
                f"     ② 文章级投影 (n={sc.size:,d}): μ={sig4(s_mean)} | σ={sig4(s_std)} | "
                f"中位={sig4(s_med)} | [min, max]=[{sig4(s_min)}, {sig4(s_max)}] | "
                f"投影>0 占比={pct4(s_pos)} (理论范围 [−1,1])"
            )
            if s_pos > 0.95 or s_pos < 0.05:
                logger.info(
                    f"        ⚠ sign-at-0 饱和 (投影>0={pct4(s_pos)} 极端): 各向异性嵌入空间已知现象, "
                    "故 pos/neg_frac 改用 in-sample median 居中 (见聚合口径)"
                )
            else:
                logger.info("        ✓ 投影方向分布无明显饱和退化")

        # ③ 各轨 bank-year 均值列的有效率 (notna) + 量级
        for trk in tracks:
            suffix = "" if trk == "full" else f"_{trk}"
            mcol = f"benefit_jlm_zh_mean{suffix}"
            if mcol not in panel.columns:
                continue
            col = pd.to_numeric(panel[mcol], errors="coerce")
            notna = float(col.notna().mean()) if n_obs else 0.0
            m_mean = float(col.mean()) if col.notna().any() else float("nan")
            m_std = float(col.std(ddof=1)) if col.notna().sum() > 1 else float("nan")
            verdict = "✓ 良好" if notna >= 0.95 else ("⚠ 临界" if notna >= 0.80 else "❌ 偏低")
            logger.info(
                f"     ③ [{trk}] {mcol}: 有效率={pct4(notna)} {verdict} | "
                f"列均值={sig4(m_mean)} | 列内 σ={sig4(m_std)}"
            )

        # ④ 锚点族元信息
        logger.info(
            f"     ④ 锚点族: family={meta.get('anchor_family')} | n_pairs={meta.get('n_pairs')} | "
            f"source_doi={meta.get('source_doi') or '(yaml 未声明)'} | sha={str(meta.get('yaml_sha256', ''))[:16]}"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  结果分析打印失败 (不影响产物): {e}")


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
        "--text-embeddings-ss",
        type=str,
        default=None,
        help=(
            "Optional ss-track embeddings .npy (27_benefit_embeddings_ss.npy "
            "+ sidecar; 银行+金科同句共现, content_ss); produces "
            "benefit_jlm_zh_*_ss columns (三轨第三轨, 与 ctx 并列)"
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
        default="news_process/data/processed/80_alt_anchor_panel.parquet",
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

    stage_start = time.time()
    logger.info("--- 开始执行阶段: 80_alt_anchor (J-L-M 2026 替代锚点投影; audit-only) ---")
    _log_environment_config_method(args)

    _t0 = time.time()
    pos, neg, meta = load_jlm_zh_anchors(args.anchors_yaml)
    logger.info(
        "Loaded J-L-M Appendix A anchors: %d pairs, family=%s, sha=%s",
        len(pos),
        meta["anchor_family"],
        meta["yaml_sha256"][:16],
    )
    logger.info(f"  ⏱ [锚点加载/校验] 耗时 {sig4(time.time() - _t0)} 秒")

    if args.validate_only:
        logger.info("[validate-only] yaml schema OK; exiting.")
        logger.info(f"--- 阶段 80_alt_anchor (validate-only) 完成, 总耗时 {sig4(time.time() - stage_start)} 秒 ---")
        return 0

    if args.text_embeddings_full is None or args.df_exploded is None:
        logger.warning(
            "Skipping projection (missing --text-embeddings-full / --df-exploded). "
            "Yaml schema validated; rerun with embedding inputs to produce panel."
        )
        logger.info(f"--- 阶段 80_alt_anchor (跳过投影) 完成, 总耗时 {sig4(time.time() - stage_start)} 秒 ---")
        return 0

    # fix(omni-g-benefit-01, 2026-06-11): 文章嵌入须带 sidecar (fail-loud on
    # stale npy); 锚点经统一引擎用 sidecar model_id 反查的 spec 嵌入 → 同空间。
    _t0 = time.time()
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
    logger.info(f"  ⏱ [文章嵌入加载/对齐] 耗时 {sig4(time.time() - _t0)} 秒")

    _t0 = time.time()
    direction = compute_direction_vector(pos, neg, embedding_fn)
    dir_sha = hashlib.sha256(direction.tobytes()).hexdigest()
    logger.info("Direction vector computed: norm=1.0, sha=%s", dir_sha[:16])
    logger.info(f"  ⏱ [方向向量构建 (锚点嵌入)] 耗时 {sig4(time.time() - _t0)} 秒")

    _t0 = time.time()
    scores = project_texts(text_embeddings, direction)
    panel = aggregate_to_bank_year(df_exploded, scores)
    tracks: list[str] = ["full"]

    # ctx 轨 (optional): 同一方向向量 (锚点 track-agnostic), ctx 文章嵌入投影
    if args.text_embeddings_ctx is not None:
        emb_ctx, ctx_meta = load_article_embeddings(args.text_embeddings_ctx)
        if str(ctx_meta["model_id"]) != model_id:
            raise ValueError(
                f"ctx embeddings model={ctx_meta['model_id']!r} != full track "
                f"model={model_id!r} — 三轨必须同嵌入空间"
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

    # ss 轨 (optional, 第三轨): 银行+金科同句共现 (content_ss); 同一方向向量
    # (锚点 track-agnostic), 仅切换 ss 文章嵌入子集投影, 镜像 ctx 路径
    if args.text_embeddings_ss is not None:
        emb_ss, ss_meta = load_article_embeddings(args.text_embeddings_ss)
        if str(ss_meta["model_id"]) != model_id:
            raise ValueError(
                f"ss embeddings model={ss_meta['model_id']!r} != full track "
                f"model={model_id!r} — 三轨必须同嵌入空间"
            )
        if emb_ss.shape[0] != len(df_exploded):
            raise ValueError(
                f"ss embeddings rows ({emb_ss.shape[0]}) != df_exploded "
                f"({len(df_exploded)})"
            )
        scores_ss = project_texts(emb_ss, direction)
        panel_ss = aggregate_to_bank_year(df_exploded, scores_ss,
                                          col_suffix="_ss")
        panel = panel.merge(panel_ss, on=["target_bank", "year"], how="outer")
        tracks.append("ss")
    logger.info(f"  ⏱ [投影 + bank-year 聚合 ({len(tracks)} 轨)] 耗时 {sig4(time.time() - _t0)} 秒")

    # 📊 结果分析 (纯日志, 不改产物)
    _log_result_analysis(panel, scores, tracks, meta)

    _t0 = time.time()
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
    logger.info(f"  ⏱ [写盘 (parquet + sidecar)] 耗时 {sig4(time.time() - _t0)} 秒")
    logger.info(f"--- 阶段 80_alt_anchor 完成, 总耗时 {sig4(time.time() - stage_start)} 秒 ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
