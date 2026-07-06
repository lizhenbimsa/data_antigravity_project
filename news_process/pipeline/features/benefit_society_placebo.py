"""benefit_society — 业务线 placebo (安慰剂) 投影 (S1 稳健性).

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 P1.1 + P1.2:

依 J-L-M 2026 §4.2 的 placebo industries 方法论, 把**同一个**金融科技主
10 锚点对方向向量, 施加到经关键词**过滤**后的文章子集 (非金融科技业务线 +
中性基线) 上。预期行为: 过滤后的投影**不应**预测 ROA (验收标准:
≥4/5 个 placebo spec 满足 |β_placebo / β_fintech| < 0.3, 见 AC-S1)。

**Audit-only / library-only 路径**: 本模块自身的 CLI (main) **不写任何 parquet**
(只做 validation + 提供库函数, 见 main 末尾日志); 经编排的 placebo 面板由
`benefit_society_audit_combined.py` 写出为 `data/processed/80_alt_anchor_and_placebo_panel.parquet`;
**不**修改主面板 `40_panel_yearly.parquet` 及其 golden snapshot。

白话: 这是一个"反向对照实验"。我们的主指标声称量出了"金融科技利好经营"
的态度; 为了证明它量的真是金融科技而不是随便什么新闻都能量出效果,
把同一把尺子拿去量"住房贷款/信用卡/中间业务/网点渠道"这类与金融科技无关的新闻 —
如果在这些无关新闻上也能"预测"银行业绩, 说明尺子本身有问题。
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import platform
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# ── 经核验参考文献 (VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 + DOI; 仅日志用) ──
# emit 进运行期日志的方法学锚点。关键: 生产路径 compute_placebo_projection 由
# benefit_society_audit_combined.py 三轨各调一次 (full/ctx/ss), 绕过 main() /
# _log_environment_and_config (那里才有引文) → 编排 .log 此前 0 条方法学依据。
# 把 placebo industries 设计本体的引文搬到模块级, 让编排路径入口 banner 也自证依据。
_REFERENCES = {
    # 白话: placebo industries (安慰剂行业) 设计 —— 把"金科利好经营"方向向量施加到与
    # 金科无关的业务线新闻 (住房贷款/信用卡/中间业务/网点渠道) 上; 若无关新闻也量出强
    # 信号, 说明尺子量的是普遍语气而非金科 (本模块的 S1 反向对照实验直接操作化此法)。
    "jlm_placebo_industries": (
        "Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit "
        "society? A language embedding approach. The Review of Financial "
        "Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012"
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_placebo_keywords(
    yaml_path: Path | str | None = None,
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, object]]:
    """加载业务线 + 中性基线的 placebo 关键词集.

    Returns
    -------
    tuple
        ``(business_lines, neutral_baseline, metadata)``, 其中:
        - ``business_lines``: ``{line_id: keyword_list}`` (4 条业务线)
        - ``neutral_baseline``: ``{neutral_id: keyword_list}`` (1 套中性基线)
        - ``metadata``: yaml 文件 SHA-256 + schema_version
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
    """返回布尔掩码: 任一关键词出现在标题**或**正文中的行为 True.

    Parameters
    ----------
    df_articles
        文章级 DataFrame (须含 title_col + content_col 列).
    keywords
        待匹配的中文关键词列表 (大小写敏感的子串匹配;
        中文文本天然无大小写之分).
    title_col, content_col
        列名. 默认值沿用 v3.7.0 管道的 标题/内容 约定.

    Returns
    -------
    pd.Series
        布尔掩码, 长度 == len(df_articles).
    """
    if not keywords:
        return pd.Series(False, index=df_articles.index)

    # 转义关键词中的正则元字符 (防御性; 中文关键词很少需要)
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
    """对多个业务线过滤器分别计算 placebo 投影.

    对 ``keyword_sets`` 中的每个过滤器:
        1. 按关键词匹配过滤文章 (标题 + 正文)
        2. 把 ``direction`` 施加到 ``text_embeddings`` 的过滤子集上
        3. 聚合为 bank-year 级余弦投影均值

    确定性披露 (fix(omni-g-benefit-01, 2026-06-11)): 本函数链路 (关键词过滤 +
    余弦投影 + groupby mean) 无任何随机步; 编排器 (audit_combined) 仍显式
    np.random.seed 并把 seed 写入 sidecar, 守卫未来引入的抽样步。

    Parameters
    ----------
    df_articles
        文章级 DataFrame; 须满足 len == len(text_embeddings).
    text_embeddings
        预计算好的嵌入向量, 形状 ``(n_articles, d)``.
    direction
        单位范数方向向量 (典型为金融科技主 10 锚点对方向).
    keyword_sets
        ``{placebo_id: [keyword, ...]}`` 映射 (4 业务线 + 1 中性 = 5).
    col_suffix
        输出列后缀, track-agnostic (ctx 轨传 ``"_ctx"`` / ss 轨传 ``"_ss"``;
        fix(omni-g-benefit-01, 2026-06-11) 补 ctx 轨, 三轨补 ss 轨)。
        默认 ``""`` 维持既有列名。

    Returns
    -------
    pd.DataFrame
        Bank-year 面板, 每个 placebo 一列:
        ``benefit_placebo_{placebo_id}_mean{col_suffix}``.
    dict[str, int]
        逐 placebo 命中文章数 (``{placebo_id: n_matched_articles}``),
        供下游 R1.A 风险监控使用.
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

    # ── 入口 banner (日志富集 Round 8, 2026-06-29; guarded 纯日志, golden-safe) ──
    # 生产/编排路径 (本函数由 benefit_society_audit_combined.py 三轨各调一次) 绕过
    # main()/_log_environment_and_config → 此前 .log 仅有 0-match warning, 无任何
    # I/O provenance / 运行期参数 / 方法学引文。补一条入口块自证: 输入规模、嵌入维度、
    # 方向向量 L2 范数 (= 上面单位化分母)、placebo 规格数、活动轨与聚合键 (唯一可调旋钮)。
    try:
        _emb_dim = int(text_embeddings.shape[1]) if text_embeddings.ndim == 2 else -1
        _dir_norm = float(np.linalg.norm(direction))  # 已在 direction_unit 单位化处算过
        _track = col_suffix or "(canonical/full)"
        logger.info("  🧭 placebo 投影入口 (业务线安慰剂, S1 稳健性; 生产/编排路径)")
        logger.info(
            f"     · 输入: 文章 n={len(text_embeddings):,d} 篇 | 嵌入维 d={_emb_dim:,d} | "
            f"方向向量 L2 范数={sig4(_dir_norm)} (>0 即可单位化, 余弦投影成立)"
        )
        logger.info(
            f"     · placebo 规格数={len(keyword_sets):,d}/5 (4 业务线 + 1 中性基线) | "
            f"活动轨 col_suffix='{col_suffix}' → {_track} | "
            f"聚合键 bank_col='{bank_col}' year_col='{year_col}'"
        )
        logger.info(f"  📖 {_REFERENCES['jlm_placebo_industries']}")
        logger.info(
            "     → placebo industries: 同一金科方向向量施于非金科业务线新闻; 无关新闻"
            f"不应预测 ROA (AC-S1: ≥4/5 规格 |β_placebo/β_fintech| < {sig4(0.3)} → 主"
            "测度非『报道总体语气』驱动, 构念效度成立)"
        )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不让计算崩 (golden-safe)
        logger.warning(f"  (placebo 入口 banner 日志失败, 忽略不影响计算): {_e}")

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

        # ── 逐 placebo 结果分布 (日志富集 Round 8, 2026-06-29; guarded 纯日志, 弃用) ──
        # 这是 S1 核心安慰剂测度。审稿人核 AC-S1 (|β_placebo/β_fintech| < 0.3) 时, 期望
        # 日志逐条给出: 命中保留率 + 文章级余弦投影分布 + bank-year 聚合分布 (从已算好
        # 的 sub/agg 局部量直接读, 只喂 logger 不回流)。镜像 geography.py L358-372 的
        # sig4 fintech_exposure 分布日志。同时把 _log_environment_and_config(L319-322)
        # 仅"描述"、却从不在测量处实检的 R1.A 风险阈值 (单业务线命中 < 500 篇 → warning)
        # 在此对真实 n_matched 落地检查 (描述 → 实测)。
        try:
            _n_art = len(df_articles)
            _retain = (n_matched / _n_art) if _n_art else float("nan")
            logger.info(
                f"  📊 placebo '{placebo_id}'{col_suffix}: 命中 n={n_matched:,d} 篇 | "
                f"关键词保留率={pct4(_retain)} (占文章宇宙 {_n_art:,d} 篇)"
            )
            if n_matched > 0:
                _sc = sub["_score"]
                _col = f"benefit_placebo_{placebo_id}_mean{col_suffix}"
                _ag = agg[_col]
                logger.info(
                    f"     · 文章级余弦投影 (matched): mean={sig4(_sc.mean())} "
                    f"median={sig4(_sc.median())} std={sig4(_sc.std())} "
                    f"[min={sig4(_sc.min())}, max={sig4(_sc.max())}]"
                )
                logger.info(
                    f"     · bank-year 聚合 ({len(_ag):,d} 行): "
                    f"mean={sig4(_ag.mean())} std={sig4(_ag.std())}"
                )
            # R1.A 风险监控 (计划 §5): 单业务线命中 < 500 篇记 warning (此前仅描述未实检)
            if 0 < n_matched < 500:
                logger.warning(
                    f"     · ⚠ R1.A 风险监控: placebo '{placebo_id}'{col_suffix} 命中 "
                    f"{n_matched:,d} < 500 篇 → 投影统计功效弱 "
                    "(≥2 条不达标须回退 ≤3 业务线 + 中性基线)"
                )
        except Exception as _e:  # noqa: BLE001 — 日志块绝不让计算崩 (golden-safe)
            logger.warning(
                f"  (placebo '{placebo_id}' 结果分布日志失败, 忽略不影响计算): {_e}"
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


def _log_environment_and_config(
    meta: dict[str, object],
    business_lines: dict[str, list[str]],
    neutral_baseline: dict[str, list[str]],
    *,
    validate_only: bool,
) -> None:
    """打印项目/环境信息 + 运行配置 + 方法论依据 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读哪些配置、用了哪些可调参数、依据哪篇文献"一次性落进日志,
    便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / schema / 控制流 (golden-safe)。
    """
    try:
        _run_id = os.environ.get("NEWS_PROCESS_RUN_ID")

        logger.info("  🧭 项目 / 环境信息")
        logger.info(
            "     · 阶段: benefit_society placebo (业务线安慰剂投影, S1 稳健性; "
            "audit/library-only, 不写主面板/golden)"
        )
        logger.info(
            "     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); "
            "版本 v3.15.0"
        )
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(
            f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}"
        )
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            "纯 CPU / 无 LLM·网络·API ($0); 链路无随机步 → 确定性可复现"
        )

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 关键词 yaml: {meta.get('yaml_path')}")
        logger.info(
            f"     · yaml SHA-256: {str(meta.get('yaml_sha256', ''))[:16]}… | "
            f"schema_version={meta.get('schema_version')}"
        )
        logger.info(
            "     · 本 CLI 不写 parquet (audit/library-only); 编排器 "
            "benefit_society_audit_combined.py 写 80_alt_anchor_and_placebo_panel.parquet"
        )

        _bl_sizes = {k: len(v) for k, v in business_lines.items()}
        _nb_sizes = {k: len(v) for k, v in neutral_baseline.items()}
        logger.info("  ⚙ 运行配置 (config/benefit_society_placebo_keywords.yaml)")
        logger.info(
            f"     · 业务线 placebo: {len(business_lines):,d} 条 (非金科) | "
            f"中性基线: {len(neutral_baseline):,d} 条 | 合计 placebo 规格="
            f"{len(business_lines) + len(neutral_baseline):,d}/5"
        )
        logger.info(f"     · 业务线词数: {_bl_sizes}")
        logger.info(f"     · 中性基线词数: {_nb_sizes}")
        logger.info(
            "     · 匹配口径: 任一关键词命中 标题 或 内容 即判命中 (子串匹配, 大小写不敏感)"
        )
        logger.info(
            "     · 投影方向: 复用主分析金科 10 锚点对方向向量 (track-agnostic, "
            "col_suffix∈{'','_ctx','_ss'})"
        )
        logger.info(
            f"     · 验收标准 AC-S1: ≥4/5 规格满足 |β_placebo/β_fintech| < {sig4(0.3)} "
            "→ 主信号非『报道总体语气』驱动 (主测度稳健)"
        )
        logger.info(
            "     · 命中率校验 (计划 §5 R1.A): 单业务线命中 < 500 篇记 warning; "
            "≥2 条不达标则回退 ≤3 业务线 + 中性基线"
        )
        logger.info(f"     · 运行模式: {'validate-only (仅校验 schema)' if validate_only else '完整 (含投影库函数说明)'}")

        logger.info("  📖 方法论依据")
        logger.info(
            "     · placebo industries (安慰剂行业) 设计: "
            "Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit "
            "society? A language embedding approach. The Review of Financial "
            "Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012"
        )
        logger.info(
            "       → 把『金科利好经营』方向向量施加到与金科无关的业务线新闻上; "
            "若无关新闻也量出强信号, 说明尺子量的是普遍语气而非金科 (证伪用对照)"
        )
        logger.info(
            "     · 文本测度构念效度的证伪/中性化范式 (同源 Manela, 方法论近邻):"
        )
        logger.info(
            "       Engelberg, J., Manela, A., Mullins, W., & Vulicevic, L. (2025). "
            "Entity neutering [Working paper]. SSRN. https://doi.org/10.2139/ssrn.5182756"
        )
        logger.info(
            "       → entity neutering 测实体特异性, 本安慰剂测主题(金科)特异性 — 二者同属"
            "『嵌入测度是否真捕捉声称构念而非普遍语气/实体泄漏』的证伪检验 (不同特异性维度, 同一证伪哲学)"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


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

    stage_start = time.time()
    phase_durations: dict[str, float] = {}

    logger.info("--- 开始执行: benefit_society placebo (业务线安慰剂投影, S1 稳健性) ---")

    _t = time.time()
    business_lines, neutral_baseline, meta = load_placebo_keywords(args.keywords_yaml)
    phase_durations["①加载并校验关键词 yaml"] = time.time() - _t

    # 项目/环境信息 + 运行配置 + 方法论依据 (日志富集 2026-06-24)
    _log_environment_and_config(
        meta,
        business_lines,
        neutral_baseline,
        validate_only=args.validate_only,
    )

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

    # 📊 关键指标解读 (运行结果信息): 关键词集规模/均衡度对照预期阈值
    try:
        _bl_counts = [len(v) for v in business_lines.values()]
        _nb_counts = [len(v) for v in neutral_baseline.values()]
        _all_counts = _bl_counts + _nb_counts
        _total_kw = sum(_all_counts)
        _n_specs = len(business_lines) + len(neutral_baseline)
        _min_kw = min(_all_counts) if _all_counts else 0
        _mean_kw = (_total_kw / _n_specs) if _n_specs else 0.0
        # placebo 规格间词表均衡度: 越接近 1 → 各 placebo 过滤力度越可比
        _balance = (_min_kw / max(_bl_counts + _nb_counts)) if _all_counts else 0.0

        logger.info("  📊 关键指标解读 (placebo 关键词集就绪度)")
        logger.info(
            f"     · placebo 规格数: {_n_specs:,d}/5 "
            f"{'✅ 完整' if _n_specs == 5 else '⚠ 不足 (预期 4 业务线 + 1 中性)'}"
        )
        _max_kw = max(_all_counts) if _all_counts else 0
        logger.info(
            f"     · 关键词总量: {_total_kw:,d} 词 | 每规格均值={sig4(_mean_kw)} 词 | "
            f"规格词数 [min, max]=[{_min_kw:,d}, {_max_kw:,d}]"
        )
        logger.info(
            f"     · 规格间词表均衡度 (min/max)={sig4(_balance)} "
            f"({pct4(_balance)}) "
            + (
                "✅ 较均衡 (各 placebo 过滤力度可比)"
                if _balance >= 0.5
                else "⚠ 不均衡 (词表偏少的 placebo 命中率可能不足)"
            )
        )
        if _min_kw < 3:
            logger.warning(
                "     · ⚠ 存在词表 < 3 词的 placebo, 命中文章可能过稀 → 投影列易全 NaN"
            )
        logger.info(
            "     · 提示: 真正的命中率/投影区分度判读须在编排 (audit_combined) 携 "
            "text_embeddings 时给出; 本 CLI 仅校验 schema + 提供库函数"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  关键指标解读打印失败 (不影响处理): {e}")

    if args.validate_only:
        logger.info("[validate-only] yaml schema OK; exiting.")
        _log_timing(phase_durations, stage_start)
        return 0

    logger.warning(
        "Full projection requires text_embeddings + df_exploded (see plan §3 P1.6); "
        "this CLI provides validation + library functions only."
    )
    _log_timing(phase_durations, stage_start)
    return 0


def _log_timing(phase_durations: dict[str, float], stage_start: float) -> None:
    """⏱ 阶段计时汇总 (墙钟耗时, 4 位有效数字; golden-safe 纯日志)。"""
    try:
        logger.info("  ⏱ 阶段计时 (墙钟)")
        for name, dur in phase_durations.items():
            logger.info(f"     · {name}: {sig4(dur)} 秒")
        logger.info(f"     · 总计: {sig4(time.time() - stage_start)} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  计时汇总打印失败 (不影响处理): {e}")


if __name__ == "__main__":
    sys.exit(main())
