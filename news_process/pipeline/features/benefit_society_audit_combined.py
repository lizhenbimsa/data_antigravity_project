"""benefit_society — 合并 audit-only 管线 (P1.6).

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
把 ``benefit_society_alt_anchor`` (J-L-M canonical 5 对锚点) +
``benefit_society_placebo`` (4 业务线 + 1 中性基线) 编排为单一
audit-only 输出:

    data/processed/80_alt_anchor_and_placebo_panel.parquet

Schema (键 = target_bank + year):
    - benefit_jlm_zh_mean / std / pos_frac / neg_frac  (+ ``_ctx`` twin 列,
      当提供 ctx 轨嵌入时; + ``_ss`` twin 列, 当提供 ss 轨 [银行+金科同句]
      嵌入时; fix(omni-g-benefit-01, 2026-06-11) 补 ctx 轨, 三轨补 ss 轨)
    - benefit_placebo_housing_loans_mean
    - benefit_placebo_credit_cards_mean
    - benefit_placebo_intermediate_business_mean
    - benefit_placebo_branch_channel_mean
    - benefit_placebo_general_corporate_mean   (中性基线)
      (placebo 列同样有 ``_ctx`` / ``_ss`` twin)

Sidecar JSON: ``...sidecar.json``, 记录锚点 yaml SHA-256 + 逐 placebo 命中数。

**关键约束**: 不触碰主面板; 这是 audit-only 路径。

fix(omni-g-benefit-01, 2026-06-11) 链路重接线 (2026-05-29 主轨换模后失效):
- 锚点嵌入不再硬编码 SentenceTransformer("shibing624/...") — 经统一引擎
  ``embedding_engine.embed_texts``, spec 由文章嵌入 .npy 的 sidecar
  ``model_id`` 反查 → 锚点与文章同嵌入空间 (维度错配根因消除);
- 输入 .npy 必须带 stage 27 落盘的 ``.sidecar.json`` (fail-loud on stale);
  ``--main-direction-npy`` 的产出方 = stage 27 ``27_benefit_direction.npy``;
- 显式 seed (np.random.seed + sidecar 记录): 当前链路确定性, seed 守卫
  未来抽样步; 嵌入真重算 deferred 到下次生产 run (锚点 ~10 句, $≈0)。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 80_placebo_and_alt_anchor.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**职责**: benefit_society (银行普惠/服务社会) 论文的 audit-only 稳健性管线, 把两项检验合成单一产物 —— ① **替代锚点** (J-L-M canonical 5 对正/负锚点, 换一组定义"惠及社会"的锚句, 测主测度对锚点选择的敏感性); ② **安慰剂** (4 条业务线 housing_loans/credit_cards/intermediate_business/branch_channel + 1 中性基线 general_corporate, 测主信号是否"在不该出现的地方也出现"=伪相关)。

**输入** (CLI 参数, `main(argv)`): `--text-embeddings-full` (stage 27 `27_benefit_embeddings_full.npy`, 必带 .sidecar.json 否则 fail-loud) + `--df-exploded` (文章-银行级 parquet, 含 target_bank/year/标题/内容) + `--main-direction-npy` (stage 27 `27_benefit_direction.npy`, 主 10 锚点金科方向向量); 可选 `--text-embeddings-ctx/ss` + `--seed` (默认 DEFAULT_SEED=20260516) + `--output` + `--validate-only`。

**处理步骤** (`build_audit_panel`):
1. 长度/维度守卫: df 行数 == 嵌入行数; main_direction 维度 == 文章嵌入维度 (防 2026-05-29 换模后方向向量与文章不同空间的根因错配); ctx/ss 同步长度校验。
2. 显式 `np.random.seed(seed)` (当前链路确定性, seed 守卫未来抽样步)。
3. **替代锚点**: `load_jlm_zh_anchors` 读 5 对锚句 → 经统一引擎 `make_anchor_embedding_fn(resolve_embedding_spec(model_id))` 嵌入 (与文章同空间) → `compute_direction_vector` 算锚点方向 → `project_texts` 投影文章嵌入 → `aggregate_to_bank_year` 聚合为 `benefit_jlm_zh_mean/std/pos_frac/neg_frac` (+ ctx/ss twin)。
4. **安慰剂**: `load_placebo_keywords` 读 4 业务线 + 1 中性的关键词集 → `compute_placebo_projection` (关键词掩码 track-agnostic + 文章嵌入投影到**主**方向向量) → `benefit_placebo_{业务线}_mean` (+ ctx/ss twin)。
5. 按 (target_bank, year) outer-merge 合并 alt + placebo → 写 parquet + sidecar。

**关键算法**: 句嵌入余弦/方向投影 (锚点对方向向量 + 文章嵌入点积投影) + bank-year 聚合 (mean/std/正负分数比例, pos/neg_frac 默认以 in-sample median 为 center)。

**外部依赖**: 统一 embedding 引擎 (`embedding_engine.embed_texts`, 经 make_anchor_embedding_fn 闭包穿透 LLMCache; 锚点仅 ~10 句, **cache 命中时 ≈$0**; ⚠ 嵌入族**不受** `NEWS_PROCESS_LLM_OFFLINE` 离线闸的"miss→raise"豁免成本约束 —— 换嵌入模型后首跑锚点 cache miss 会真发一次极小付费嵌入调用 (~10 句, ≈分钱级), 命中后离线 $0); 文章嵌入须 stage 27 预先落盘 (本脚本不调嵌入 API 跑全量文章, 只嵌锚点)。读 yaml (锚点/placebo 关键词)。

**DAG 位置**: stage 27 (benefit 嵌入) 的审计旁支, 上游 = stage 27 的 .npy + sidecar; 下游 = benefit_society 论文 Stata 模板 (P2.S1/P2.A2)。shim 仅 `from ...benefit_society_audit_combined import main; sys.exit(main())`, 零逻辑。

■ 白话说明

这一步是"给银行普惠测度做两项打假实验", 而且是专门为 benefit_society 这篇论文服务的、独立于主流水线的旁支 (它故意不接进主面板, 保证万一出错也不会污染正式数据)。

两项实验打个比方: 主测度是用一组"标准锚句"(比如"服务实体经济"算正、"过度逐利"算负) 来给每家银行的新闻打"惠及社会"的分。实验一 (替代锚点) = 换一组同义但措辞不同的锚句重打分, 看结论变不变 —— 如果换了锚句分数就翻盘, 说明主测度太脆弱、是"挑词凑出来的"。实验二 (安慰剂) = 故意拿"住房贷款""信用卡""中间业务"这些跟"惠及社会"无关的普通业务线去打同样的分, 还放一条纯中性基线 —— 如果这些不该有信号的地方也冒出强信号, 说明主测度在乱抓相关性 (伪相关), 不可信。

为什么需要它: 顶刊审稿人会追问"你这个'银行惠及社会'的分数是真有内容, 还是你锚句选得巧/纯属噪声"。这两项检验就是正面回应。

对最终结果的影响: 它本身不进主银行-年度面板、不动任何主回归数字; 它产出一张独立的审计面板, 喂给 benefit_society 论文的稳健性表格。做得好, 就能证明"惠及社会"测度经得起换锚句、扛得住安慰剂, 主结论站得稳; 做得不好 (实验暴露脆弱), 就提示这篇论文的核心测度需要重新设计。
========================================================================
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

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4
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


def _resolve_default_inputs(args, config: dict) -> None:
    """把省略的输入路径自动接线到 stage 27/40 规范产物 (in-place 填充 args 的 None 槽)。

    fix(2026-06-29): audit-only stage 80 此前裸跑 (不带 5 个输入 CLI 路径) 仅校验 yaml
    即空转 warn 退出, 不产审计面板 (logs/80_placebo_and_alt_anchor.log 的根问题)。本
    helper 让省略的输入回退到 config 声明的上游规范产物 ——

    - ``--text-embeddings-full`` → ``<output_dir>/27_benefit_embeddings_full.npy``
      (镜像 benefit_society._persist_article_embeddings 的 ``cache_filename
      .replace('.npy', f'{suffix}_{track}.npy')``, MAIN suffix='');
    - ``--main-direction-npy``   → ``<output_dir>/27_benefit_direction.npy``
      (benefit_society._persist_direction_vector 硬编码 ``27_benefit_direction{suffix}.npy``);
    - ``--df-exploded``          → ``<output_dir>/40_article_bank_level.parquet``
      (stage 40 export_panel 落盘的同一 df_exploded; 行序与 .npy 1:1 对齐,
      benefit 投影(runner:1759)→export(runner:2694) 之间 df_exploded 不重排)。

    使裸跑在上游 (stage 27/40) 已落盘时即可消费、产出面板; 解析后文件仍缺 (CI/无数据机)
    则由 main() 的存在性检查 warn 回退 (原 no-op 语义)。

    必需三件套 (full/df/direction) 无条件填默认路径 (存在性由 main() 校验)。可选 ctx/ss
    twin **仅当默认路径文件实际存在时**才接线 —— 上游未产 ctx/ss 时不强填, 避免 main()
    把缺失的可选轨误当必需输入而错误 warn 回退。显式传入的 CLI 路径 (非 None) 一律保留不覆盖。
    """
    paths = config.get("paths") or {}
    filenames = config.get("filenames") or {}
    out_dir = paths.get("output_dir", "data/processed")
    emb_base = filenames.get("output_27_benefit_cache", "27_benefit_embeddings.npy")

    def _emb_track(track: str) -> str:
        return os.path.join(out_dir, emb_base.replace(".npy", f"_{track}.npy"))

    if args.text_embeddings_full is None:
        args.text_embeddings_full = _emb_track("full")
    if args.main_direction_npy is None:
        args.main_direction_npy = os.path.join(out_dir, "27_benefit_direction.npy")
    if args.df_exploded is None:
        args.df_exploded = os.path.join(
            out_dir,
            filenames.get("output_40_article_bank", "40_article_bank_level.parquet"),
        )
    # 可选 ctx/ss twin: 默认路径文件存在才接线 (上游未产则保持 None)
    if args.text_embeddings_ctx is None:
        _cand_ctx = _emb_track("ctx")
        if os.path.exists(_cand_ctx):
            args.text_embeddings_ctx = _cand_ctx
    if args.text_embeddings_ss is None:
        _cand_ss = _emb_track("ss")
        if os.path.exists(_cand_ss):
            args.text_embeddings_ss = _cand_ss


def build_audit_panel(
    df_exploded: pd.DataFrame,
    text_embeddings: np.ndarray,
    main_direction: np.ndarray,
    *,
    bank_col: str = "target_bank",
    year_col: str = "year",
    text_embeddings_ctx: np.ndarray | None = None,
    text_embeddings_ss: np.ndarray | None = None,
    anchor_embedding_fn=None,
    embedding_model_id: str | None = None,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """构建合并的 audit 面板.

    Parameters
    ----------
    df_exploded
        文章-银行级 DataFrame (须含 target_bank, year, 标题, 内容).
    text_embeddings
        预计算的文章嵌入, 形状 ``(n_articles, d)`` — full 轨
        (stage 27 ``27_benefit_embeddings_full.npy``; 行序对齐 df_exploded,
        空文本行=NaN)。fix(omni-g-benefit-01, 2026-06-11): 不再假设
        shibing624/768 — 维度由数组自描述, 模型由 ``embedding_model_id`` 声明。
    main_direction
        主 10 锚点对金融科技方向向量 (用于 placebo 子集投影);
        即 stage 27 ``27_benefit_direction.npy`` (未归一, 本函数
        消费端归一)。
    text_embeddings_ctx
        可选 ctx 轨嵌入 (同 model / 同行序) → ``_ctx`` twin 列。
    text_embeddings_ss
        可选 ss 轨嵌入 (银行+金科同句共现 content_ss; 同 model / 同行序)
        → ``_ss`` twin 列 (三轨第三轨, 与 ctx 并列)。
    anchor_embedding_fn
        可注入的锚点嵌入闭包 (测试用). ``None`` → 经
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
        ``(combined_panel, metadata)``. metadata 含锚点 yaml SHA +
        逐 placebo 命中数, 供下游 sidecar JSON 使用.
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
    if text_embeddings_ss is not None and len(df_exploded) != len(text_embeddings_ss):
        raise ValueError(
            f"df_exploded ({len(df_exploded)}) and text_embeddings_ss "
            f"({len(text_embeddings_ss)}) length mismatch"
        )

    np.random.seed(seed)  # 显式 seed (确定性披露见 docstring)

    # ---- 1) 替代锚点 (J-L-M 5 对) — 锚点经统一引擎嵌入
    if embedding_model_id is None:
        from news_process.core.config import load_config

        embedding_model_id = str(
            (load_config().get("embedding_api") or {}).get("model")
            or "Qwen/Qwen3-Embedding-8B"
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
    # ss 轨 (第三轨, 银行+金科同句): 同一 alt 方向向量 (锚点 track-agnostic),
    # 仅切换 ss 文章嵌入子集投影, 镜像 ctx 路径
    if text_embeddings_ss is not None:
        alt_scores_ss = _alt_project(text_embeddings_ss, alt_dir)
        alt_panel_ss = _alt_aggregate(
            df_exploded, alt_scores_ss,
            bank_col=bank_col, year_col=year_col, col_suffix="_ss",
        )
        alt_panel = alt_panel.merge(
            alt_panel_ss, on=[bank_col, year_col], how="outer"
        )

    # ---- 2) Placebo (4 业务线 + 1 中性) — 使用 MAIN 主方向向量
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
    if text_embeddings_ss is not None:
        # ss twin (第三轨): 同关键词掩码 (track-agnostic 文本过滤) + ss 嵌入投影
        placebo_panel_ss, _ = compute_placebo_projection(
            df_exploded,
            text_embeddings_ss,
            main_direction,
            keyword_sets,
            bank_col=bank_col,
            year_col=year_col,
            col_suffix="_ss",
        )
        placebo_panel = placebo_panel.merge(
            placebo_panel_ss, on=[bank_col, year_col], how="outer"
        )

    # ---- 3) 按 (bank, year) outer-merge 合并
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
        "tracks": (
            ["full"]
            + (["ctx"] if text_embeddings_ctx is not None else [])
            + (["ss"] if text_embeddings_ss is not None else [])
        ),
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
        prog="python news_process/80_placebo_and_alt_anchor.py",
        description=(
            "P1.6 — combined audit-only panel: J-L-M alt anchor + business-line placebo. "
            "Outputs `data/processed/80_alt_anchor_and_placebo_panel.parquet`."
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
        "--text-embeddings-ss",
        type=str,
        default=None,
        help=(
            "Optional ss-track embeddings .npy (+ sidecar; 银行+金科同句共现, "
            "content_ss) → *_ss twin 列 (三轨第三轨, 与 ctx 并列)"
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
        default=None,  # P2 fix (2026-06-26): 默认延后到 main() 经 config output_dir 解析 (cwd 无关)
        help="Output parquet path (默认: <output_dir>/80_alt_anchor_and_placebo_panel.parquet)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate yaml schemas only; do not load embeddings or run projection",
    )

    args = parser.parse_args(argv)

    # 接入项目统一日志: 写 <log_dir>/80_placebo_and_alt_anchor.log。此前本阶段仅
    # 模块级 getLogger(__name__) + 一次性 basicConfig, audit-only 旁支日志不落
    # <stage>.log; 现对齐 39c/39d 同族 audit 阶段的 setup_logging 约定 (替换而非
    # 叠加旧 basicConfig), 让日志自带阶段说明书。
    global logger
    from news_process.core.config import load_config
    from news_process.core.logging import setup_logging
    config = load_config()
    logger = setup_logging(
        "80_placebo_and_alt_anchor",
        config["paths"].get("log_dir", "logs"),
    )

    # P2 fix (2026-06-26): --output 默认延后到此经 config output_dir 解析 (cwd 无关; audit-only)。
    if args.output is None:
        args.output = os.path.join(
            config['paths']['output_dir'],
            '80_alt_anchor_and_placebo_panel.parquet',
        )

    # fix(2026-06-29): 省略的输入路径自动接线到 stage 27/40 规范产物 (见 _resolve_default_inputs)。
    # 让 audit-only stage 80 裸跑即可消费上游已落盘的 .npy/df, 不再因缺 5 个 CLI 路径而空转 warn;
    # 解析后文件仍缺 (CI/无数据机) 则由下方存在性检查 warn 回退 (保持原 no-op 语义)。须在输入/输出
    # 日志块 (下方 banner) 之前接线, 让日志打印的是真实解析后路径而非 "(未提供)"。
    _resolve_default_inputs(args, config)

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info(
        "阶段 80: benefit_society 替代锚点 + 安慰剂审计 "
        "(audit-only; V2.0 J-L-M 2026 §3 P1.6)"
    )
    logger.info("=" * 72)
    logger.info("【功能】给银行'惠及社会'测度做两项打假实验, 产出独立审计面板 (不进主面板/golden):")
    logger.info("        ① 替代锚点 = 换 J-L-M canonical 5 对锚句重打分, 测主测度对锚点选择的敏感性;")
    logger.info("        ② 安慰剂 = 拿 4 条无关业务线 + 1 中性基线打同样的分, 测主信号是否在不该出现处冒头 (伪相关)。")
    logger.info("【方法】句嵌入方向投影 (锚点对方向向量 ⊙ 文章嵌入点积) → bank-year 聚合 mean/std/pos_frac/neg_frac;")
    logger.info("        placebo 用 MAIN 主方向向量 + 关键词掩码子集投影; 锚点与文章须同嵌入空间 (model_id 反查校验)。")
    logger.info("【判读】替代锚点: 与主测度方向一致、量级相近=稳健(好); 翻盘/塌缩=锚点敏感(不利)。")
    logger.info("        安慰剂: 业务线信号量级 *远小于* 替代锚点 (|均值|占比 ratio<0.5)=干净(好); 接近/超过=主测度乱抓相关(伪相关,不利)。")
    logger.info("        注: RAW 余弦投影均值在各向异性嵌入空间 (sign-at-0 实测 ~97% 投影>0, 见 alt_anchor 饱和退化披露) 下系统性非零, 无绝对 ≈0 基线, 故只作 *相对* 量级判读。")
    logger.info("【确定性】不调 LLM; 仅嵌 ~10 句锚点 (cache 命中时 ≈$0; ⚠ 换模首跑锚点 miss 会发一次极小付费嵌入, 非 OFFLINE 闸豁免); 文章嵌入读 stage 27 预落盘 .npy; 显式 seed。")

    # ① 🧭 项目 / 环境信息 + ② 输入/输出 + ③ 运行配置 + ④ 方法论依据 (日志富集 2026-06-24, 纯增量 golden-safe)。
    # 全块 try/except 兜底: 纯日志诊断绝不让 audit 阶段返回非 0。emit 只在函数体内 (避免 import-time 截断)。
    _t_start = time.time()
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: 80 benefit_society 替代锚点 + 安慰剂审计 (audit-only 旁支, shim 80_placebo_and_alt_anchor)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            "确定性 (显式 seed + 锚点经 LLMCache); 不调 LLM, 仅嵌 ~10 句锚点 (≈$0); audit-only 不进主面板/golden"
        )

        logger.info("  📂 输入 / 输出文件")
        # full/df/direction 三槽已由 _resolve_default_inputs 无条件接线 (恒非 None), 直接打印解析后路径;
        # ctx/ss 是可选 twin (仅默认文件存在才接线) → 仍可能为 None, 保留 '(未提供)' 占位。
        logger.info(f"     · 文章嵌入 full: {args.text_embeddings_full}")
        logger.info(f"     · 文章嵌入 ctx:  {args.text_embeddings_ctx or '(未提供)'}")
        logger.info(f"     · 文章嵌入 ss:   {args.text_embeddings_ss or '(未提供)'}")
        logger.info(f"     · 文章-银行 df:  {args.df_exploded}")
        logger.info(f"     · 主方向 .npy:   {args.main_direction_npy} (stage 27 27_benefit_direction.npy)")
        logger.info(f"     · 输出 parquet:  {args.output}")

        logger.info("  ⚙ 运行配置 (CLI argv + 默认值)")
        logger.info(f"     · 随机种子 seed = {args.seed:,d} (默认 DEFAULT_SEED={DEFAULT_SEED:,d}; 当前链路无随机步, 守卫未来抽样)")
        logger.info(f"     · validate-only = {args.validate_only} (True=仅校验 yaml schema, 不加载嵌入/不投影)")
        logger.info("     · 锚点集 = J-L-M canonical 5 对正/负锚句 (config yaml SHA 见 sidecar)")
        logger.info("     · 安慰剂 = 4 业务线 (housing_loans/credit_cards/intermediate_business/branch_channel) + 1 中性基线 (general_corporate)")
        logger.info("     · pos/neg_frac center = 批内 in-sample median (聚合口径见 benefit_society_alt_anchor.aggregate_to_bank_year)")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info("     · 语言嵌入『惠及社会』方向投影 (本审计的替代锚点主方法):")
        logger.info("       Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? "
                    "A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. "
                    "https://doi.org/10.1093/rfs/hhaf012")
        logger.info("     · 锚点对方向向量 = 概念双极投影 (geometry of culture, 锚句对差向量定义语义轴):")
        logger.info("       Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture: "
                    "Analyzing the meanings of class through word embeddings. American Sociological Review, "
                    "84(5), 905-949. https://doi.org/10.1177/0003122419877135")
        logger.info("     · 句嵌入 (锚句/文章同空间余弦投影):")
        logger.info("       Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using "
                    "Siamese BERT-networks. In Proceedings of the 2019 Conference on Empirical Methods in "
                    "Natural Language Processing and the 9th International Joint Conference on Natural Language "
                    "Processing (EMNLP-IJCNLP) (pp. 3980-3990). Association for Computational Linguistics. "
                    "https://doi.org/10.18653/v1/D19-1410")
        logger.info("     · 白话: 用 J-L-M 的『语言嵌入测惠及社会』范式, 换一组锚句重打分 (替代锚点) "
                    "+ 拿无关业务线打同样的分 (安慰剂), 检验主测度是否锚点敏感/伪相关。")
    except Exception as _e:
        logger.warning(f"[环境/配置/方法块] 日志诊断异常, 跳过(不影响产物): {_e}")

    # 恒安全的 yaml schema 校验 (不加载嵌入)
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

    # fix(2026-06-29): 必需输入 (full/df/direction) 现已由 _resolve_default_inputs 自动接线到
    # stage 27/40 规范产物; 故 warn 回退判据由 "CLI 是否传参" 改为 "解析后文件是否实际存在"。
    # 三件套齐备 → 跑 full projection; 任一缺失 (上游未跑/CI 无数据) → warn 回退 (yaml 已校验, no-op)。
    _required = {
        "--text-embeddings-full": args.text_embeddings_full,
        "--df-exploded": args.df_exploded,
        "--main-direction-npy": args.main_direction_npy,
    }
    _missing = [f"{k}={v!r}" for k, v in _required.items() if not (v and os.path.exists(v))]
    if _missing:
        logger.warning(
            "Full projection 需要 stage 27/40 产物 (已尝试从 config 自动接线), 但以下缺失: %s. "
            "Yaml schemas validated; 先跑 stage 27 (config benefit_society.cache_embeddings=true) 产出 "
            "27_benefit_embeddings_full.npy + 27_benefit_direction.npy, 跑 stage 40 产出 "
            "40_article_bank_level.parquet, 或显式传 --text-embeddings-full/--df-exploded/"
            "--main-direction-npy 后重跑, 即可产出审计面板。",
            "; ".join(_missing),
        )
        return 0

    logger.info(
        "✓ 输入已就绪 (auto-wired from config 或显式 CLI): full=%s | df=%s | direction=%s | ctx=%s | ss=%s",
        args.text_embeddings_full, args.df_exploded, args.main_direction_npy,
        args.text_embeddings_ctx or "(无)", args.text_embeddings_ss or "(无)",
    )

    # fix(omni-g-benefit-01, 2026-06-11): sidecar 强制 (fail-loud on stale npy)
    # + model_id 反查 spec → 锚点与文章同嵌入空间。
    _t_load = time.time()
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
                f"model={model_id!r} — 三轨必须同嵌入空间"
            )

    text_embeddings_ss = None
    if args.text_embeddings_ss is not None:
        text_embeddings_ss, ss_meta = load_article_embeddings(
            args.text_embeddings_ss
        )
        if str(ss_meta["model_id"]) != model_id:
            raise ValueError(
                f"ss embeddings model={ss_meta['model_id']!r} != full track "
                f"model={model_id!r} — 三轨必须同嵌入空间"
            )

    _elapsed_load = time.time() - _t_load
    logger.info(
        "Loaded embeddings shape=%s (model=%s) / df len=%d / direction shape=%s / ctx=%s / ss=%s",
        text_embeddings.shape,
        model_id,
        len(df_exploded),
        main_direction.shape,
        "yes" if text_embeddings_ctx is not None else "no",
        "yes" if text_embeddings_ss is not None else "no",
    )
    logger.info("  ⏱ [phase] 嵌入/df/方向加载: %s 秒", sig4(_elapsed_load))

    _t_build = time.time()
    combined, meta = build_audit_panel(
        df_exploded,
        text_embeddings,
        main_direction,
        text_embeddings_ctx=text_embeddings_ctx,
        text_embeddings_ss=text_embeddings_ss,
        embedding_model_id=model_id,
        seed=args.seed,
    )
    _elapsed_build = time.time() - _t_build
    logger.info("  ⏱ [phase] 锚点投影 + 安慰剂 + bank-year 聚合 (build_audit_panel): %s 秒", sig4(_elapsed_build))

    _t_write = time.time()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, index=False)
    logger.info("Wrote audit panel: %s (%d bank-year obs)", output_path, len(combined))

    # io-provenance (golden-safe 纯日志): 写盘边界补面板"宽度"维度的来源溯源 —— 行数已由上方
    # "Wrote audit panel" 打出, 这里补 总列数 + 替代锚点 (benefit_jlm_zh_*) / 安慰剂 (benefit_placebo_*)
    # 列族计数, 让审计面板的 schema 宽度在阶段输出边界处可追溯。仅打印整数 (%d, 不引入 float), 不回写 combined/meta。
    # 白话: 除了"多少行 (bank-year)", 也记下"多少列、其中替代锚点几列/安慰剂几列", 方便复现时核对 schema 完整。
    try:
        _n_cols = len(combined.columns)
        _n_altanchor_cols = sum(1 for _c in combined.columns if str(_c).startswith("benefit_jlm_zh_"))
        _n_placebo_cols = sum(1 for _c in combined.columns if str(_c).startswith("benefit_placebo_"))
        logger.info(
            "  [schema] 审计面板宽度: 共 %d 列 (替代锚点 benefit_jlm_zh_* %d 列 + 安慰剂 benefit_placebo_* %d 列)",
            _n_cols, _n_altanchor_cols, _n_placebo_cols,
        )
    except Exception as _e:
        logger.warning(f"[schema 溯源] 日志诊断异常, 跳过(不影响产物): {_e}")

    sidecar_path = write_sidecar_json(output_path, meta)
    logger.info("Wrote sidecar JSON: %s", sidecar_path)
    logger.info("  ⏱ [phase] 写盘 (parquet + sidecar): %s 秒", sig4(time.time() - _t_write))

    # 结果分析 — 写入日志: 替代锚点信号强度 + 逐安慰剂命中数/均值, 对照"伪相关"方向判读。
    # 仅用于日志打印, 不回写 combined / meta (golden-safe 纯增量)。此块在产物 (parquet
    # + sidecar) 已落盘之后执行, 故即便抛异常也不影响产物; 仍整体 try/except 兜底
    # (crash-guard), 防止纯日志诊断意外让阶段返回非 0。
    try:
        logger.info("-" * 72)
        n_obs = meta.get("n_bank_year_obs", len(combined))
        n_art = meta.get("n_articles_total", len(combined))
        logger.info(
            "【结果分析】审计面板 %s bank-year obs (源自 %s 篇文章-银行行; embedding_dim=%s; tracks=%s):",
            n_obs,
            n_art,
            meta.get("embedding_dim", "?"),
            ",".join(meta.get("tracks", [])) or "?",
        )

        # ① 替代锚点 (J-L-M 5 对) — full 轨信号强度。pos_frac > 0.5 表示多数文章投影为"正向惠及"。
        # NaN-guard: 全 NaN (上游空文本/聚合无有效行) 时 alt_abs_mean 取 nan, 下游 ② 的
        # 占比判读会自动落进"基准不可比"分支, 不会打出 nan% 误导。
        alt_abs_mean = float("nan")
        if "benefit_jlm_zh_mean" in combined and combined["benefit_jlm_zh_mean"].notna().sum() == 0:
            logger.warning("  ① 替代锚点 full: benefit_jlm_zh_mean 全 NaN — 该轨无有效数据, 替代锚点信号无法评估")
        elif "benefit_jlm_zh_pos_frac" in combined:
            alt_mean = float(combined["benefit_jlm_zh_mean"].mean())
            alt_abs_mean = float(combined["benefit_jlm_zh_mean"].abs().mean())
            alt_pos = float(combined["benefit_jlm_zh_pos_frac"].mean())
            alt_neg = float(combined["benefit_jlm_zh_neg_frac"].mean())
            logger.info(
                "  ① 替代锚点 full: 均值=%s  |均值|=%s  pos_frac=%s  neg_frac=%s "
                "(pos_frac 以批内 median 为 center → ~0.5 属预期; 与主测度方向一致即稳健)",
                sig4(alt_mean), sig4(alt_abs_mean), sig4(alt_pos), sig4(alt_neg),
            )
        else:
            logger.warning("  ① 替代锚点列缺失 (benefit_jlm_zh_*) — 上游嵌入/锚点链路异常, 替代锚点检验未生效")

        # ①′ 替代锚点 ctx/ss 孪生轨 — 三轨 (full/ctx/ss) 稳健性报告补全。fix(omni-g-benefit-01) 后 ctx/ss
        # twin 列已由 aggregate_to_bank_year col_suffix='_ctx'/'_ss' 落进 combined, 但此前仅 full 轨打印
        # 信号强度; 此处对称补 ctx/ss, NaN-guard 镜像上方 full 轨。纯日志, 用 combined 既有列, 不回写产物。
        # 白话: full 轨看全文, ctx 轨只看银行实体邻近窗口, ss 轨只看银行+金科同句窗口 —— 三轨方向一致才算锚点稳健。
        for _trk, _trk_label in (("_ctx", "ctx(实体邻近)"), ("_ss", "ss(银行+金科同句)")):
            _mean_col = f"benefit_jlm_zh_mean{_trk}"
            _pos_col = f"benefit_jlm_zh_pos_frac{_trk}"
            _neg_col = f"benefit_jlm_zh_neg_frac{_trk}"
            if _mean_col not in combined or _pos_col not in combined or _neg_col not in combined:
                continue
            if combined[_mean_col].notna().sum() == 0:
                logger.warning("  ①′ 替代锚点 %s: %s 全 NaN — 该轨无有效数据, 替代锚点信号无法评估", _trk_label, _mean_col)
                continue
            _t_mean = float(combined[_mean_col].mean())
            _t_abs = float(combined[_mean_col].abs().mean())
            _t_pos = float(combined[_pos_col].mean())
            _t_neg = float(combined[_neg_col].mean())
            logger.info(
                "  ①′ 替代锚点 %s: 均值=%s  |均值|=%s  pos_frac=%s  neg_frac=%s "
                "(pos_frac 以批内 median 为 center → ~0.5 属预期; 与 full 轨方向一致即三轨稳健)",
                _trk_label, sig4(_t_mean), sig4(_t_abs), sig4(_t_pos), sig4(_t_neg),
            )

        # ② 安慰剂 (4 业务线 + 1 中性) — 命中数 + 均值; 期望"业务线信号量级 *远小于* 替代锚点 (相对判读, 非绝对 ≈0)"。
        # 各向异性嵌入空间下 RAW |均值| 系统性非零 (alt_anchor.py:317 实测 ~97% 投影>0), 故不存在绝对 ≈0 基线, 只看相对占比。
        logger.info("  ② 安慰剂 (期望: 命中数充足且均值 |·| 远小于替代锚点 |均值|=%s → 无伪相关, 好):", sig4(alt_abs_mean))
        # ⚠ 判读口径说明 (顶刊免责声明, 仅日志): 替代锚点与安慰剂均用 *未去中心* 的 RAW |余弦均值|,
        # 在各向异性嵌入空间 (sign-at-0 实测 ~97% 投影>0, 见 alt_anchor.py:317 饱和退化披露) 下二者各带
        # 固定方向的基线正偏移, 故下方 ratio 主要反映两条 direction 的偏移大小关系, 仅作 *量级参考*;
        # 正式伪相关检验须改用 median-center / 相对中性基线 (general_corporate) 口径。
        # ⚠ 阈值 0.5 / 1.0 是本块的 ad-hoc 日志启发式 (粗分干净/临界/泄漏三档), *不是* alt_anchor.py:10
        # 文档授权的正式判据 — 文档判据是『benefit_jlm_zh vs benefit_mean 的回归 β 符号一致 + β 比值 > 0.5』
        # (回归系数比), 与此处 placebo-vs-alt 的 |均值| 幅值比是语义无关的两个量, 仅恰好共用数字 0.5。
        logger.info(
            "  ⚠ 口径: 下方 ratio = 安慰剂 RAW|均值| / 替代锚点 RAW|均值| (均未去中心, 各向异性下二者带固定正偏移), 仅作量级参考; "
            "阈值 0.5/1.0 为 ad-hoc 日志启发式, 非 alt_anchor.py:10 文档的回归 β 比值判据。"
        )
        placebo_hits = meta.get("placebo_match_counts", {}) or {}
        # (命中率校验, 计划 §5 R1.A): 汇总 placebo 规格命中分布 (单业务线命中 < 500 篇为风险信号,
        # ≥2 条不达标则回退 ≤3 业务线 + 中性基线)。纯日志, 不改 combined/meta。
        _hit_vals = [int(_n) for _n in placebo_hits.values()]
        _n_ge500 = sum(1 for _n in _hit_vals if _n >= 500)
        _n_zero = sum(1 for _n in _hit_vals if _n == 0)
        _med_hit = float(np.median(_hit_vals)) if _hit_vals else float("nan")
        logger.info(
            "  (命中率校验 R1.A) placebo 规格 %d 个: 命中 ≥500 篇 %d 个 | 命中 0 篇 %d 个 | 命中数中位=%s 篇",
            len(_hit_vals), _n_ge500, _n_zero, sig4(_med_hit),
        )
        leak_lines: list[str] = []
        for pid, n_hit in placebo_hits.items():
            col = f"benefit_placebo_{pid}_mean"
            is_neutral = pid == "general_corporate"
            tag = " [中性基线]" if is_neutral else ""
            if n_hit == 0:
                logger.warning("    - %s%s: 命中 0 篇 → 该列全 NaN, 安慰剂在此业务线上无法评估 (优雅降级)", pid, tag)
                continue
            # column-guard: 命中非 0 但列缺失 (聚合异常); 命中且有列但全 NaN (NaN-guard) 也单独分支。
            if col not in combined:
                logger.warning("    - %s%s: 命中 %d 篇但列缺失 (%s) — 聚合异常", pid, tag, n_hit, col)
                continue
            if combined[col].notna().sum() == 0:
                logger.warning("    - %s%s: 命中 %d 篇但 %s 全 NaN — 该业务线无有效投影, 无法评估", pid, tag, n_hit, col)
                continue
            p_abs_mean = float(combined[col].abs().mean())
            # 判读 (ad-hoc 量级启发式, 见上方口径说明): 安慰剂 RAW|均值| 显著小于替代锚点 RAW|均值| = 干净;
            # 接近或超过 = 可能伪相关泄漏。两者均未去中心, 仅作量级参考, 非 alt_anchor.py:10 文档的回归 β 比值判据。
            if alt_abs_mean == alt_abs_mean and alt_abs_mean > 0:  # noqa: PLR0124 (NaN 自比过滤)
                ratio = p_abs_mean / alt_abs_mean
                verdict = "干净(好)" if ratio < 0.5 else ("临界" if ratio < 1.0 else "⚠ 疑似伪相关泄漏(不利)")
                if ratio >= 0.5:
                    leak_lines.append(pid)
                logger.info(
                    "    - %s%s: 命中 %d 篇  |均值|=%s  占替代锚点信号 %s  → %s",
                    pid, tag, n_hit, sig4(p_abs_mean), pct4(ratio), verdict,
                )
            else:
                logger.info("    - %s%s: 命中 %d 篇  |均值|=%s (替代锚点基准不可比)", pid, tag, n_hit, sig4(p_abs_mean))

        # 辅助判读 (更干净, 仅日志): 以中性基线 general_corporate |均值| 为分母, 算各业务线 |均值| 的相对偏离。
        # 中性基线与业务线安慰剂同走 MAIN 方向投影 → 共享同一各向异性正偏移, 相比 alt-anchor 分母能更多消去固定偏移,
        # 故"相对中性基线"的比值比"相对替代锚点"的量级比更接近真正的伪相关信号强度。仅打印, 不回写产物。
        neutral_col = "benefit_placebo_general_corporate_mean"
        if neutral_col in combined and combined[neutral_col].notna().sum() > 0:
            neutral_abs_mean = float(combined[neutral_col].abs().mean())
            if neutral_abs_mean > 0:
                logger.info(
                    "  (辅助) 相对中性基线 general_corporate |均值|=%s 的偏离 (更干净的伪相关参考量, 越接近 1 越无超额信号):",
                    sig4(neutral_abs_mean),
                )
                for pid, n_hit in placebo_hits.items():
                    if pid == "general_corporate" or n_hit == 0:
                        continue
                    col = f"benefit_placebo_{pid}_mean"
                    if col not in combined or combined[col].notna().sum() == 0:
                        continue
                    rel = float(combined[col].abs().mean()) / neutral_abs_mean
                    logger.info("    - %s: |均值| / 中性基线 |均值| = %s", pid, sig4(rel))
            else:
                logger.info("  (辅助) 中性基线 general_corporate |均值|=0, 无法作相对中性参考")

        if leak_lines:
            logger.info(
                "  ⚠ %d 条安慰剂信号量级 ≥ 替代锚点一半 (%s): 需在论文稳健性附录中正面回应是否伪相关",
                len(leak_lines), ", ".join(leak_lines),
            )
        else:
            logger.info("  ✓ 全部安慰剂信号均显著弱于替代锚点 → 主测度未在无关业务线乱抓相关 (支持构念效度)")

        # 小样本警告: 盘面 T=2 仅验证管道正确性, 全量结论以 17M/T=18 实测为准。
        logger.info(
            "  ⚠ 样本 = %s 篇文章 / %s bank-year (盘面 T=2 小样本时仅验证管道正确性, 全量结论以 17M/T=18 实测为准)",
            n_art, n_obs,
        )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    try:
        logger.info("  ⏱ [phase] 阶段 80 总墙钟 (加载→build→写盘→分析): %s 秒", sig4(time.time() - _t_start))
    except Exception as _e:
        logger.warning(f"[计时汇总] 日志诊断异常, 跳过(不影响产物): {_e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
