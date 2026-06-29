"""news_process.papers.benefit_society.shrinkage
=================================================
Hierarchical empirical Bayes shrinkage for benefit_mean in sparse-coverage settings.

【目的】
- 当某些 bank-year 单元仅有 1-3 篇新闻时, benefit_mean 标准误大
- 用 hierarchical model 将稀疏单元向"同年同省同类型均值"收缩
- Bias-variance tradeoff: 引入小 bias 换取大幅降 variance

【方法】
- Empirical Bayes (closed-form Morris 矩估计, no MCMC)
- Group-wise pooling on (bank_type, province, **year**) 同年截面群组均值
  (fix(omni-g-benefit-06, 2026-06-11): group 加 year — 此前 pooled 全年份组均值
   使 t 期 shrunk 值嵌入未来年份信息, 而 shrunk 列是 Table 8/8b 回归 RHS)
- Shrinkage weight: w_i = σ̂²ᵢ / (σ̂²ᵢ + τ̂²)
  σ̂²ᵢ = 单元均值的抽样方差 (优先 文章级 std²/nᵢ, 即面板自带 benefit_std_*;
        缺失回退 grand_var/nᵢ 代理 — 有偏, 见下方披露)
  τ̂²  = 组内真实均值的先验方差, Morris 矩估计:
        max(SS_dev/(N−k) − mean(σ̂²ᵢ), 1e-8)
  (fix(omni-g-benefit-03/07/09, 2026-06-11): 此前 between_var=var(value−groupmean,
   ddof=1) 是含抽样噪声的组内残差方差 (=τ²+E[σ̂²ᵢ], 未做 Efron-Morris 噪声扣除),
   且单成员组贡献恒 0 离差、分母 N−1 而非 N−k — 三项偏误致权重系统性失真
   (独立模拟: 旧实现权重均值 0.13 vs 正确 EB 0.64)。现: 单成员组从 τ̂² 估计中
   排除 + N−k 自由度 + 减 mean(σ̂²ᵢ) 噪声扣除。)

【披露 (g-benefit-03)】
- 回退代理 grand_var/nᵢ 用 bank-year 均值的截面总方差 (≈τ²+E[σ²/n]) 冒充文章级
  σ², 系统性低估; 仅在 std_col 不可用时使用。
- n_obs 默认列 n_articles 是 cell 内全部文章数, 非支撑 benefit_mean 的
  valid-scored 文章数 (ctx 轨差异更大) → 精度有高估; 上游无 per-track valid
  计数列, 可经 n_obs_col 覆写。

【为什么用 closed-form 而非 PyMC/Stan】
- 避免重依赖 (PyMC ~ 100MB)
- closed-form Morris (1983, JASA) 矩估计在等方差近似下与 EB 后验均值一致;
  statsmodels.regression.mixed_linear_model 作 sanity check
  (注: 旧 docstring "James-Stein 已是最优 (Efron-Morris 1973)" 声称已撤 —
   旧实现未做噪声扣除, 并不构成 Efron-Morris 估计量)

【输入/输出】
- 输入: bank-year panel with [benefit_mean_full(+benefit_std_full), n_articles,
        bank_type, bank_province, year]
- 输出: panel + [benefit_mean_full_shrunk, benefit_mean_full_shrunk_weight]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Empirical Bayes 闭式收缩 (Morris 矩估计法 MoM)
# ---------------------------------------------------------------------------
def empirical_bayes_shrinkage(
    values: np.ndarray,
    n_obs: np.ndarray,
    group_labels: np.ndarray,
    sampling_var: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """按单元内精度加权, 把 ``values`` 向组均值收缩.

    白话: 新闻很少的银行-年份算出的均值很"飘", 这里让它向同组 (同年同省
    同类型) 的平均值靠拢——新闻越少靠得越多, 新闻越多越保留原值。

    fix(omni-g-benefit-03/07/09, 2026-06-11) — 方差分量修正 (公式与代码统一):

    - ``w_i = σ̂²ᵢ / (σ̂²ᵢ + τ̂²)``;  ``shrunk_i = w_i·groupmean + (1−w_i)·value_i``
    - ``σ̂²ᵢ`` (单元抽样方差): 优先 ``sampling_var`` (= 文章级 std²/nᵢ, 调用方
      从面板 benefit_std_* 构造); 缺失元素回退 ``grand_var/nᵢ`` 代理 (有偏,
      模块头已披露)。
    - ``τ̂²`` (组内真实均值先验方差, Morris 矩估计):
      ``max(SS_dev/(N−k) − mean(σ̂²ᵢ), 1e-8)``, 其中 SS_dev 只累计 **≥2 成员组**
      (单成员组离差恒 0, 纳入会双重低估 τ̂²), N/k = 非单成员组的行数/组数,
      减 mean(σ̂²ᵢ) 是 Efron-Morris 噪声扣除 (残差方差 = τ² + E[σ̂²ᵢ])。
    - 全部组均为单成员时 τ̂² 取 1e-8 (此时组均值≡自身, 收缩为恒等, 权重无影响)。

    Parameters
    ----------
    values : np.ndarray, shape (N,)
        原始 bank-year 度量值 (如 benefit_mean_full)
    n_obs : np.ndarray, shape (N,)
        支撑每个度量值的文章数
    group_labels : np.ndarray, shape (N,)
        组标识 (如 bank_type×province×year 组合)
    sampling_var : np.ndarray | None, shape (N,)
        可选的单元抽样方差 σ̂²ᵢ (如 benefit_std²/nᵢ);
        non-finite / non-positive 元素逐位回退 grand_var/nᵢ 代理。

    Returns
    -------
    shrunk : np.ndarray, shape (N,)
        收缩后的度量值
    weights : np.ndarray, shape (N,)
        收缩权重 ∈ [0, 1]; 1 = 完全收缩到组均值, 0 = 不收缩 (保留原值)
    """
    if not (len(values) == len(n_obs) == len(group_labels)):
        raise ValueError("values, n_obs, group_labels must have equal length")
    if sampling_var is not None and len(sampling_var) != len(values):
        raise ValueError("sampling_var must have equal length with values")

    values = np.asarray(values, dtype=np.float64)
    n_obs = np.asarray(n_obs, dtype=np.float64)
    group_labels = np.asarray(group_labels)

    valid_mask = np.isfinite(values) & (n_obs > 0)
    if valid_mask.sum() < 2:
        logger.warning("Insufficient valid observations for shrinkage; returning raw values")
        return values.copy(), np.zeros_like(values)

    # 计算组均值
    unique_groups, inverse = np.unique(group_labels[valid_mask], return_inverse=True)
    group_means = np.array(
        [values[valid_mask][inverse == g].mean() for g in range(len(unique_groups))]
    )
    group_sizes = np.bincount(inverse, minlength=len(unique_groups))

    # 映射回全部行
    group_mean_per_row = np.full(len(values), np.nan, dtype=np.float64)
    group_lookup = dict(zip(unique_groups, group_means))
    for i, g in enumerate(group_labels):
        if g in group_lookup:
            group_mean_per_row[i] = group_lookup[g]

    # σ̂²ᵢ — 组内 (单元内) 抽样方差 within-unit sampling variance:
    # 优先文章级 sampling_var; 缺失元素回退 grand_var/nᵢ 代理 (有偏, 已披露)
    grand_var = np.var(values[valid_mask], ddof=1) if valid_mask.sum() > 1 else 1.0
    proxy_var = grand_var / np.maximum(n_obs, 1.0)
    if sampling_var is not None:
        sv = np.asarray(sampling_var, dtype=np.float64)
        within_var = np.where(np.isfinite(sv) & (sv > 0), sv, proxy_var)
    else:
        within_var = proxy_var

    # τ̂² — Morris MoM: 排除单成员组 + N−k 自由度 + 噪声扣除 (见 docstring)
    sizes_per_valid_row = group_sizes[inverse]          # 各 valid 行所属组的成员数
    multi = sizes_per_valid_row >= 2
    n_multi = int(multi.sum())
    k_multi = int(np.unique(inverse[multi]).size) if n_multi else 0
    if n_multi - k_multi >= 1:
        deviations = values[valid_mask][multi] - group_mean_per_row[valid_mask][multi]
        resid_var = float((deviations ** 2).sum()) / float(n_multi - k_multi)
        mean_sampling = float(within_var[valid_mask][multi].mean())
        between_var = max(resid_var - mean_sampling, 1e-8)
    else:
        between_var = 1e-8  # 无可识别的组内对比 → 收缩恒等 (单成员组均值=自身)

    # EB 后验中先验 (组) 均值的权重: w = σ̂²ᵢ / (σ̂²ᵢ + τ̂²)
    # n_obs 越大 → σ̂²ᵢ 越小 → w 越小 → 收缩越少
    weights = within_var / (within_var + between_var)
    weights = np.clip(weights, 0.0, 1.0)  # 防御性 (两项非负时数学上已 ∈[0,1])
    weights = np.where(valid_mask, weights, 0.0)

    shrunk = np.where(
        valid_mask & np.isfinite(group_mean_per_row),
        weights * group_mean_per_row + (1.0 - weights) * values,
        values,
    )

    # ── 📊 EB 方差分解 + 组结构 + 权重分布 (纯日志, try/except; golden-safe, 不回流下游) ──
    # 白话: 把"组间真实差异 τ̂²、单元内抽样噪声 σ̄²ᵢ、二者隐含的全局合并比"以及收缩权重
    # 的整张分布落进日志。此前本函数除"观测不足"告警外不打任何日志, 而 main() 虽命名了
    # 闭式 ICC≈τ̂²/(τ̂²+σ̄²ᵢ) 却从未 emit → 跨方法 (闭式 vs MixedLM ICC) 一致性无法从 .log
    # 核对。全部取已算好的 locals (between_var/within_var/grand_var/valid_mask/unique_groups/
    # n_multi/k_multi/weights), 结果仅喂 logger、用后即弃, 绝不改任何返回值/计算 (golden-safe)。
    try:
        _mean_samp = float(np.mean(within_var[valid_mask]))
        _pool_ratio = (
            between_var / (between_var + _mean_samp)
            if (between_var + _mean_samp) > 0 else float("nan")
        )
        _w_valid = weights[valid_mask]
        logger.info(
            f"  📊 EB 方差分解: τ̂²(组间先验 between_var)={sig4(between_var)} | "
            f"grand_var(截面总方差)={sig4(grand_var)} | "
            f"σ̄²ᵢ(单元内抽样方差均值)={sig4(_mean_samp)} | "
            f"全局合并比 τ̂²/(τ̂²+σ̄²ᵢ)={sig4(_pool_ratio)} "
            "(=闭式 ICC, 与 MixedLM ICC 跨方法应一致)"
        )
        logger.info(
            f"  📊 组结构: valid 观测={int(valid_mask.sum()):,d} 行 | "
            f"组数={len(unique_groups):,d} | "
            f"≥2 成员行 n_multi={n_multi:,d} / 组 k_multi={k_multi:,d} "
            "(仅多成员组以 N−k 离差贡献 τ̂²; 单成员组离差恒 0 已排除)"
        )
        logger.info(
            f"  📊 收缩权重 w 分布 (valid 行): 均值={sig4(float(_w_valid.mean()))} | "
            f"中位={sig4(float(np.median(_w_valid)))} | "
            f"min={sig4(float(_w_valid.min()))} | max={sig4(float(_w_valid.max()))} "
            "(w→1 强收缩至组均值 / w→0 保留原值)"
        )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不让收缩计算崩 (golden-safe)
        logger.warning(f"  (EB 方差分解日志失败, 忽略不影响收缩结果): {_e}")

    return shrunk, weights


# ---------------------------------------------------------------------------
# 2. 用 statsmodels MixedLM 做交叉合理性校验 (可选, 慢)
# ---------------------------------------------------------------------------
def mixedlm_sanity_check(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
) -> dict | None:
    """跑随机截距 MixedLM, 作为 closed-form 收缩的交叉校验.

    Returns
    -------
    含 {sigma_within, sigma_between, icc} 的 dict; statsmodels 不可用时返回 None
    """
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        logger.info("statsmodels unavailable; skipping MixedLM sanity check")
        return None

    df_clean = df[[value_col, group_col]].dropna().copy()
    if len(df_clean) < 10 or df_clean[group_col].nunique() < 2:
        return None

    try:
        model = smf.mixedlm(f"{value_col} ~ 1", df_clean, groups=df_clean[group_col])
        result = model.fit(method="lbfgs", reml=True)
        sigma_within = float(result.scale)
        sigma_between = float(result.cov_re.iloc[0, 0]) if hasattr(result.cov_re, "iloc") else float(result.cov_re[0, 0])
        icc = sigma_between / (sigma_between + sigma_within) if (sigma_between + sigma_within) > 0 else 0.0
        return dict(sigma_within=sigma_within, sigma_between=sigma_between, icc=icc)
    except Exception as e:
        logger.warning(f"MixedLM failed: {e}")
        return None


# ---------------------------------------------------------------------------
# 3. 面板级收缩封装 wrapper
# ---------------------------------------------------------------------------
def apply_shrinkage_to_panel(
    panel: pd.DataFrame,
    *,
    value_col: str = "benefit_mean_full",
    n_obs_col: str = "n_articles",
    # fix(omni-g-benefit-06, 2026-06-11): 默认 group 加 year — 收缩目标改为同年
    # 截面组均值, 消除"t 期 shrunk 值嵌入未来年份信息"的跨年泄漏 (shrunk 列是
    # Table 8/8b reghdfe RHS 主解释变量)。
    group_cols: tuple[str, ...] = ("bank_type", "bank_province", "year"),
    std_col: str | None = "auto",
    output_col: str | None = None,
) -> pd.DataFrame:
    """对 bank-year 面板的一列应用 empirical Bayes 收缩.

    新增两列:
    - {output_col}: 收缩后的值
    - {output_col}_weight: 每行的收缩权重

    Parameters (新增, fix(omni-g-benefit-03/09, 2026-06-11))
    ----------
    std_col
        文章级离散度列, 用于 σ̂²ᵢ = std²/nᵢ (替代 grand_var/nᵢ 有偏代理)。
        ``"auto"`` (默认) → 由 value_col 推导 (benefit_mean_* → benefit_std_*,
        面板自带), 不存在时回退代理; ``None`` → 强制代理 (legacy 行为)。
        注意: 单观测 bank-year 的 std 为 NaN (fix(omni-g-benefit-05)) → 该行
        逐位回退代理, 不影响其余行。
    """
    if output_col is None:
        output_col = f"{value_col}_shrunk"

    df = panel.copy()
    missing = [c for c in (value_col, n_obs_col, *group_cols) if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    if std_col == "auto":
        candidate = value_col.replace("benefit_mean", "benefit_std")
        std_col = candidate if (candidate != value_col and candidate in df.columns) else None
    elif std_col is not None and std_col not in df.columns:
        raise KeyError(f"Missing columns: ['{std_col}']")

    sampling_var = None
    if std_col is not None:
        n_arr = pd.to_numeric(df[n_obs_col], errors="coerce").astype(float).values
        std_arr = pd.to_numeric(df[std_col], errors="coerce").astype(float).values
        with np.errstate(divide="ignore", invalid="ignore"):
            sampling_var = (std_arr ** 2) / np.maximum(n_arr, 1.0)
        _n_finite = int(np.isfinite(sampling_var).sum())
        _n_total = int(len(sampling_var))
        logger.info(
            f"  [{value_col}] σ̂²ᵢ 来源: {std_col}²/{n_obs_col} "
            f"(可用 {_n_finite:,d}/{_n_total:,d} 行 = "
            f"{pct4(_n_finite / _n_total) if _n_total else 'n/a'}, "
            "其余回退 grand_var/n 代理)"
        )

    # 构造复合组标签
    group_label = df[list(group_cols)].astype(str).agg("|".join, axis=1).values

    shrunk, weights = empirical_bayes_shrinkage(
        df[value_col].values,
        df[n_obs_col].values,
        group_label,
        sampling_var=sampling_var,
    )

    df[output_col] = shrunk
    df[f"{output_col}_weight"] = weights
    return df


# ---------------------------------------------------------------------------
# 4. CLI
# ---------------------------------------------------------------------------
def _log_environment_and_config(args, value_cols, group_cols) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接
    (Morris 1983 JASA https://doi.org/10.1080/01621459.1983.10477920;
     Efron & Morris 1975 JASA https://doi.org/10.1080/01621459.1975.10479864),
    James & Stein 1961 为 Berkeley Symposium 论文 (无 DOI, 仅作者-年-出处), 绝不伪造 DOI。
    """
    try:
        import platform

        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 模块: benefit_society.shrinkage (经验贝叶斯分层收缩, benefit_mean 稀疏单元降噪)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {Path(__file__).resolve()}")
        logger.info(f"     · 工作目录: {Path.cwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 CPU NumPy 闭式矩估计 / 无 LLM·Embedding·网络·API ($0) → 逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入 panel:  {Path(args.panel).resolve()}")
        logger.info(f"     · 输出 panel:  {Path(args.output).resolve()}")

        logger.info("  ⚙ 运行配置 (CLI 实参)")
        logger.info(f"     · 待收缩列 value_cols={value_cols} (--track={args.track}"
                    f"{', --value-col=' + args.value_col if args.value_col else ''})")
        logger.info(f"     · 分组列 group_cols={list(group_cols)} (同年截面收缩目标, 含 year 防跨年泄漏)")
        logger.info(f"     · n_obs_col={args.n_obs_col} (支撑度量值的文章数) | "
                    f"std_col={args.std_col} ('auto'=由 value_col 推导 benefit_std_*; 'none'=强制 grand_var/n 代理)")
        logger.info(f"     · τ̂² 下界=1e-8 (=sig4 {sig4(1e-8)}); 权重夹断区间 ∈[{sig4(0.0)}, {sig4(1.0)}]; "
                    "Morris MoM 噪声扣除 (残差方差 = τ² + E[σ̂²ᵢ]) + 排除单成员组 + N−k 自由度")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info("     · 闭式参数经验贝叶斯 (矩估计 MoM, 本模块 τ̂² 来源): "
                    "Morris, C. N. (1983). Parametric empirical Bayes inference: Theory and "
                    "applications. Journal of the American Statistical Association, 78(381), 47-55. "
                    "https://doi.org/10.1080/01621459.1983.10477920")
        logger.info("     · Stein/经验贝叶斯收缩的偏差-方差权衡基础: "
                    "Efron, B., & Morris, C. (1975). Data analysis using Stein's estimator and its "
                    "generalizations. Journal of the American Statistical Association, 70(350), 311-319. "
                    "https://doi.org/10.1080/01621459.1975.10479864")
        logger.info("     · 收缩估计量的原始统计动因 (二次损失下样本均值不可容许): "
                    "James, W., & Stein, C. (1961). Estimation with quadratic loss. In Proceedings of "
                    "the Fourth Berkeley Symposium on Mathematical Statistics and Probability "
                    "(Vol. 1, pp. 361-379). University of California Press. (无 DOI, 仅作者-年-出处)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 对面板 parquet 的 benefit_mean 应用 empirical Bayes 收缩.

    成功返回 0; 面板缺必需列时返回 1。
    """
    import time
    start_time = time.time()
    phase_durations: dict[str, float] = {}
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.shrinkage",
        description="Hierarchical empirical Bayes shrinkage for benefit_mean (dual-track)",
    )
    parser.add_argument(
        "--panel",
        type=str,
        default="news_process/data/processed/40_panel_yearly.parquet",
    )
    # no-ss-track: benefit_mean 源自 SBERT 嵌入轴 (Stage 27) 现已三轨化
    # (full/ctx/ss + _t2v twins, features/benefit_society.py 已产出 benefit_mean_ss,
    # 下游 derivative_replication.py(ATTITUDE_SS)/tables.py/paper_spec.yaml/iv_extensions.py
    # 均活跃消费); 但本收缩 CLI 刻意仅对 full/ctx 两轨应用经验贝叶斯收缩 —
    # ss 轨收缩超出本 CLI 范围 (out of scope), 故 --track 仅 full/ctx/both。
    # Plan v2.12 (F-H3): 默认 'both' 同时产出 benefit_mean_full 与
    # benefit_mean_ctx 的 shrunk 列。旧版 --value-col 仍支持单列向后兼容。
    parser.add_argument(
        "--track",
        choices=["full", "ctx", "both"],
        default="both",
        help="full/ctx track selection (plan v2.12); overrides --value-col when set to non-legacy values",
    )
    parser.add_argument("--value-col", type=str, default=None,
                        help="Legacy single-column override (e.g., benefit_mean_full)")
    parser.add_argument("--n-obs-col", type=str, default="n_articles")
    parser.add_argument(
        "--group-cols",
        type=str,
        # fix(omni-g-benefit-06, 2026-06-11): 默认加 year (同年截面收缩目标,
        # 消除跨年泄漏; shrunk 列进 Table 8/8b 回归 RHS)
        default="bank_type,bank_province,year",
        help="Comma-separated grouping columns (must exist in panel)",
    )
    parser.add_argument(
        "--std-col",
        type=str,
        default="auto",
        help=(
            "文章级离散度列 (σ̂²ᵢ=std²/n; fix(omni-g-benefit-03/09, 2026-06-11)); "
            "'auto'=由 value_col 推导 benefit_std_*, 'none'=强制 grand_var/n 代理"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/40_panel_yearly_shrunk.parquet",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    # ── 【功能】banner (黄金范式, 对齐 herd_decay main()) ──
    logger.info("=" * 72)
    logger.info("benefit_society 收缩: benefit_mean 稀疏单元经验贝叶斯分层降噪 (Morris 1983 JASA)")
    logger.info("=" * 72)
    logger.info(
        "【功能】有些'银行-年份'单元只有 1-3 篇新闻, 算出的 benefit_mean (新闻有益于社会程度)"
    )
    logger.info(
        "        噪声很大、很'飘'。本模块把这些稀疏单元向'同年同省同类型'的组均值收缩——"
    )
    logger.info(
        "        新闻越少越往组均值靠, 越多越保留原值; 输出 _shrunk 列供 Table 8/8b 回归当 RHS。"
    )
    logger.info(
        "【方法】闭式经验贝叶斯 (Morris 矩估计, 无 MCMC): w_i = σ̂²ᵢ/(σ̂²ᵢ+τ̂²);"
    )
    logger.info(
        "        shrunk_i = w_i·组均值 + (1−w_i)·原值。σ̂²ᵢ=单元抽样方差 (优先 文章级 std²/nᵢ,"
    )
    logger.info(
        "        缺失回退 grand_var/nᵢ 代理); τ̂²=组内真实均值先验方差 (排除单成员组 + N−k 自由度"
    )
    logger.info(
        "        + Efron-Morris 噪声扣除)。可选 statsmodels MixedLM 交叉校验 (ICC)。"
    )
    logger.info(
        "【判读】平均收缩权重 w̄: 越接近 0 = 几乎不收缩 (单元自身证据足); 越接近 1 = 强烈拉向组均值"
    )
    logger.info(
        "        (单元稀疏/噪声大)。MixedLM ICC 与闭式 τ̂²/(τ̂²+σ̄²ᵢ) 应大致一致 (跨方法 sanity)。"
    )
    logger.info(
        "【确定性】纯 CPU NumPy 闭式矩估计, $0, 无 LLM/Embedding/网络 → 逐位可复现。"
    )

    _t = time.time()
    panel = pd.read_parquet(args.panel)
    phase_durations['①加载panel'] = time.time() - _t
    logger.info(f"  加载面板 panel: 形状 {panel.shape[0]:,d} 行 × {panel.shape[1]:,d} 列 (来源: {args.panel})")

    # 由 --track / --value-col 解析待处理列 (--value-col 显式给出时优先)
    if args.value_col is not None:
        value_cols = [args.value_col]
    elif args.track == "both":
        value_cols = ["benefit_mean_full", "benefit_mean_ctx"]
    else:
        value_cols = [f"benefit_mean_{args.track}"]

    group_cols = tuple(c.strip() for c in args.group_cols.split(","))

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24)
    _log_environment_and_config(args, value_cols, group_cols)

    # 一次性校验必需列
    base_required = [args.n_obs_col, *group_cols]
    missing_base = [c for c in base_required if c not in panel.columns]
    if missing_base:
        logger.error(
            f"Required base columns missing: {missing_base}. "
            "Build the auxiliary panel with bank_type, province, n_articles first."
        )
        return 1

    _t = time.time()
    result = panel.copy()
    for value_col in value_cols:
        if value_col not in panel.columns:
            logger.warning(f"  [skip] track value column missing: {value_col}")
            continue
        result = apply_shrinkage_to_panel(
            result,
            value_col=value_col,
            n_obs_col=args.n_obs_col,
            group_cols=group_cols,
            std_col=None if args.std_col == "none" else args.std_col,
        )
        sanity = mixedlm_sanity_check(panel, value_col, group_cols[0])
        if sanity:
            logger.info(
                f"  [{value_col}] MixedLM 交叉校验: ICC={sig4(sanity['icc'])} "
                f"(σ_within={sig4(sanity['sigma_within'])} / σ_between={sig4(sanity['sigma_between'])}; "
                "ICC≈τ̂²/(τ̂²+σ̄²ᵢ), 与闭式 between_var 一致性参照)"
            )
        weight_col = f"{value_col}_shrunk_weight"
        _mean_w = float(result[weight_col].mean())
        logger.info(
            f"  [{value_col}] 平均收缩权重 w̄ = {sig4(_mean_w)} "
            "(→0 几乎不收缩/保留原值; →1 强烈拉向同年同省同类型组均值)"
        )
        # ── 📊 收缩权重全分布 + 偏差-方差位移影响 (纯日志, try/except; golden-safe) ──
        # 白话: 不只看平均权重, 还看权重的中位/分位/极值, 以及"部分合并 (partial pooling)
        # 究竟把 benefit_mean 推动了多远" (|shrunk−原值| 的均值/最大值 + 被实质移动的行占比)。
        # 这正是审稿人衡量"引入的 bias 是否值回 variance 下降"所需的量级证据。仅用既有列
        # (output_col / value_col / weight_col), 结果用后即弃, 不改任何产物 (golden-safe)。
        try:
            _w = pd.to_numeric(result[weight_col], errors="coerce")
            _out_col = f"{value_col}_shrunk"
            _disp = (
                pd.to_numeric(result[_out_col], errors="coerce")
                - pd.to_numeric(result[value_col], errors="coerce")
            ).abs()
            _moved_frac = float((_w > 0.5).mean())
            logger.info(
                f"  [{value_col}] 收缩权重 w 分布: 中位={sig4(float(_w.median()))} | "
                f"std={sig4(float(_w.std()))} | min={sig4(float(_w.min()))} | "
                f"max={sig4(float(_w.max()))} | Q25={sig4(float(_w.quantile(0.25)))} | "
                f"Q75={sig4(float(_w.quantile(0.75)))}"
            )
            logger.info(
                f"  [{value_col}] 偏差-方差位移: |shrunk−原值| 均值={sig4(float(_disp.mean()))} | "
                f"最大={sig4(float(_disp.max()))} | 被实质移动 (w>0.5) 行占比={pct4(_moved_frac)} "
                "(量化部分合并对 benefit_mean 的实际推动幅度, 供 bias↔variance 权衡核对)"
            )
        except Exception as _e:  # noqa: BLE001 — 日志块绝不让阶段崩 (golden-safe)
            logger.warning(f"  ({value_col} 权重分布/位移日志失败, 忽略): {_e}")
    phase_durations['②逐轨经验贝叶斯收缩+MixedLM校验'] = time.time() - _t

    _t = time.time()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    phase_durations['③写出parquet'] = time.time() - _t
    logger.info(
        f"  写出收缩后面板 → {output_path} (tracks={value_cols})"
    )
    # ── 📤 输出维度血缘 (闭合 输入→输出; 纯日志, try/except; golden-safe) ──
    # 白话: 此前只记了"加载面板"的形状, 没记写出的形状 → 血缘在阶段边界断开。这里补上
    # 输出面板的行×列, 以及相对输入新增了几列 (每处理一轨 +2 列: 收缩值 + 收缩权重),
    # 把 输入→输出 的维度对账落进日志。仅读 result/panel 已有形状, 不改任何产物。
    try:
        _cols_added = int(result.shape[1] - panel.shape[1])
        logger.info(
            f"     输出面板形状: {result.shape[0]:,d} 行 × {result.shape[1]:,d} 列 "
            f"(输入 {panel.shape[0]:,d} 行 × {panel.shape[1]:,d} 列; 新增 {_cols_added:,d} 列 "
            "= 每处理轨 +2 列: 收缩值 _shrunk + 收缩权重 _shrunk_weight) → 闭合 输入→输出 血缘"
        )
    except Exception as _e:  # noqa: BLE001 — 维度日志失败不影响已写出的产物
        logger.warning(f"  (输出维度血缘日志失败, 忽略): {_e}")

    # ── ⏱ 阶段计时摘要 (墙钟秒, sig4; 纯日志, golden-safe) ──
    _total = time.time() - start_time
    logger.info("  ⏱ 阶段计时 (墙钟秒)")
    for _name, _dur in phase_durations.items():
        _share = _dur / _total if _total > 0 else 0.0
        logger.info(f"     · {_name}: {sig4(_dur)} s ({pct4(_share)})")
    logger.info(f"     · 合计: {sig4(_total)} s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
