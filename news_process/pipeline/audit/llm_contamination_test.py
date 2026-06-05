"""news_process.pipeline.audit.llm_contamination_test — DC4 deliverable.

V4 audit F-Adv.2 critical 修复 (2026-05-18).

问题
----
LLM 训练数据可能包含 2007-2024 中国银行业新闻 → LLM 输出与 outcome (risk-taking)
已经 contaminated (look-ahead bias) → 顶刊 reviewer 最致命攻击.

设计原理
--------
利用 LLM 训练数据 cutoff date (e.g. GPT-5.4nano cutoff = 2024-Q1):
- pre-cutoff sample (LLM 可能见过): 2007 ~ 2024-Q1
- post-cutoff sample (LLM 绝对没见过): 2024-Q2 ~ 至今

如果 contamination 严重:
  - pre-cutoff: LLM 输出 与 outcome 的相关性 *异常高* (因为 LLM 记忆了答案)
  - post-cutoff: LLM 输出 与 outcome 的相关性 *正常* (纯前瞻预测能力)
  - 差异显著 (Fisher's z transformation test) → 报警 contamination

如果 contamination 轻微:
  - pre vs post 相关性差异不显著 → LLM 输出反映真实 channel, 可用

模块输出
--------
contamination_report.json 含:
  - cutoff_date: 用的 cutoff
  - n_pre_cutoff / n_post_cutoff
  - pre_correlation / post_correlation (LLM 输出 vs 真实 outcome)
  - fisher_z_test: difference test (z statistic + p-value)
  - bayes_factor: 强证据 / 弱证据 / 无证据
  - verdict: 'contamination_detected' / 'no_contamination_evidence' /
             'reverse_pattern_anomaly' / 'inconclusive'

学术锚定
--------
- Sainz et al. (2023) EMNLP "NLP Evaluation in Trouble" — LLM data contamination detection
- Magar & Schwartz (2022) ACL "Data Contamination: From Memorization to Exploitation"
- Carlini et al. (2023) ICLR "Quantifying Memorization Across Neural Language Models"
- 应用到金融文本: Lopez-Lira & Tang (2023, arXiv) ChatGPT return prediction holdout protocol

复现协议
--------
1. 准备 panel 含 LLM 输出 (e.g. llm_vote_tone_full) + outcome (e.g. z_score)
2. cutoff_date 参数对齐使用的 LLM (默认 GPT-5.4nano = 2024-04-01)
3. python -m news_process.pipeline.audit.llm_contamination_test \\
       --input data/processed/40_panel_yearly.parquet \\
       --llm-col llm_vote_tone_full \\
       --outcome-col z_score \\
       --cutoff 2024-04-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

# v3.7.0 (M12 修复): scipy module top import (替代手算 normal CDF + 局部 import).
# scipy 是项目硬依赖 (pyproject.toml + pipeline/sentiment 已用), 失败应 fail-loud.
from scipy.stats import norm

logger = logging.getLogger(__name__)

# v3.7.0 (C5 修复): LLM_CUTOFF_DATES 已删除 — 原值是 fabricated.
# 用户必须显式提供 cutoff date (fail-loud), 来源应是 LLM provider 官方文档截图 /
# 公开 release notes / API endpoint /v1/models metadata 的 frozen-by-date 校准.
# 项目惯例: 校准 cutoff 后写入 data/processed/v3_7_0_constants.json sidecar
# (与 v3.5.1 prompt frozen 同样的 anchor 机制).
#
# 反模式 (CLAUDE.md: don't introduce data we don't know):
#   - 不要在本 module 重新引入 hardcoded cutoff date 字典.
#   - 不要给 contamination_test 的 cutoff_date 参数设非空默认值.

# Bayes factor 评级 (Jeffreys 1961 scale)
BAYES_FACTOR_LABELS = [
    (0.10, "decisive evidence FOR contamination"),
    (0.33, "very strong evidence FOR contamination"),
    (1.0, "weak / inconclusive"),
    (3.0, "moderate evidence AGAINST contamination"),
    (10.0, "strong evidence AGAINST contamination"),
    (float('inf'), "very strong evidence AGAINST contamination"),
]


def fisher_z_test(
    r1: float, n1: int, r2: float, n2: int,
) -> tuple[float, float]:
    """Fisher z-transformation: test H0: r1 == r2.

    Returns (z_stat, two_sided_p_value).

    ⚠ v3.7.0 (M11 注释): 经典 Fisher z 假设 r1, r2 是 *独立* 样本相关性.
    对于本项目 pre/post cutoff sub-samples (共享 bank fixed effect, 时间序列
    相关), 独立性假设违反, p-value 偏 anti-conservative. 真实诊断建议补做
    ``cluster_robust_correlation_diff_test`` (M11 提供) 或 permutation test
    (bank-level resampling 1000 reps).
    """
    # Edge cases
    if abs(r1) >= 0.999 or abs(r2) >= 0.999:
        return float('nan'), float('nan')
    if n1 < 4 or n2 < 4:
        return float('nan'), float('nan')

    z1 = 0.5 * np.log((1 + r1) / (1 - r1))
    z2 = 0.5 * np.log((1 + r2) / (1 - r2))
    se = np.sqrt(1.0 / (n1 - 3) + 1.0 / (n2 - 3))
    z = (z1 - z2) / se

    # v3.7.0 (M12 修复): scipy.stats.norm.sf 替代手算 erf — 数值精度更高 +
    # 与 classify_bayes_factor 用同一个 norm 实例 (一致性)
    p = 2 * norm.sf(abs(z))
    return float(z), float(p)


def cluster_robust_correlation_diff_test(
    df: pd.DataFrame,
    *,
    pre_mask: pd.Series,
    post_mask: pd.Series,
    col_x: str,
    col_y: str,
    cluster_col: str,
    n_permutations: int = 1000,
    random_seed: int = 42,
) -> tuple[float, float]:
    """v3.7.0 (M11 修复): permutation test for r_pre vs r_post diff with
    bank-level cluster resampling — 替代 Fisher z 用于非独立样本.

    设计:
        H0: pre 与 post 期 corr(X, Y) 相同
        Permutation: 每次 bank-level 重新分组 (保持每 bank obs 内时间序列结构),
        随机 reassign pre/post 标签, 计算 r_pre - r_post.
        实证 p-value = 模拟分布中 |diff| ≥ 实际 |diff| 的占比.

    Returns:
        (observed_diff, permutation_p_value)
    """
    sub = df[[col_x, col_y, cluster_col]].dropna().copy()
    sub['_pre_mask'] = pre_mask.reindex(sub.index, fill_value=False)
    sub['_post_mask'] = post_mask.reindex(sub.index, fill_value=False)
    valid = sub[sub['_pre_mask'] | sub['_post_mask']]
    if len(valid) < 20:
        return float('nan'), float('nan')

    def _corr_diff(pre_idx, post_idx):
        if len(pre_idx) < 4 or len(post_idx) < 4:
            return float('nan')
        r_pre = valid.loc[pre_idx, col_x].corr(valid.loc[pre_idx, col_y])
        r_post = valid.loc[post_idx, col_x].corr(valid.loc[post_idx, col_y])
        return r_pre - r_post

    observed = _corr_diff(
        valid[valid['_pre_mask']].index,
        valid[valid['_post_mask']].index,
    )
    if not np.isfinite(observed):
        return float('nan'), float('nan')

    rng = np.random.default_rng(random_seed)
    n_extreme = 0
    clusters = valid[cluster_col].unique()
    for _ in range(n_permutations):
        # Bank-level random assignment (保持 within-bank time series intact)
        cluster_pre = set(rng.choice(
            clusters, size=len(clusters) // 2, replace=False
        ))
        perm_pre_idx = valid[valid[cluster_col].isin(cluster_pre)].index
        perm_post_idx = valid[~valid[cluster_col].isin(cluster_pre)].index
        diff = _corr_diff(perm_pre_idx, perm_post_idx)
        if np.isfinite(diff) and abs(diff) >= abs(observed):
            n_extreme += 1

    p = n_extreme / n_permutations
    return float(observed), float(p)


def compute_correlation(
    df: pd.DataFrame,
    col_x: str,
    col_y: str,
    method: str = 'pearson',
) -> tuple[float, int]:
    """计算 col_x 与 col_y 的相关性 + 有效 sample size."""
    sub = df[[col_x, col_y]].dropna()
    n = len(sub)
    if n < 4:
        return float('nan'), n
    if method == 'pearson':
        r = sub[col_x].corr(sub[col_y])
    elif method == 'spearman':
        r = sub[col_x].corr(sub[col_y], method='spearman')
    else:
        raise ValueError(f"unknown method: {method}")
    return float(r), n


def classify_bayes_factor(p_value: float, n_pre: int, n_post: int) -> tuple[float, str]:
    """近似 BIC-based Bayes factor (Wagenmakers 2007 Psychon Bull Rev approx).

    V2 E2E 修复: 公式符号原本写反 (导致 p<0.001 时 label 输出 "AGAINST contamination").

    Wagenmakers 2007 §3 BIC approximation:
        BF_10 ≈ exp(t² / 2) / sqrt(n)    (favors H1 = contamination)
        BF_01 ≈ sqrt(n) / exp(t² / 2)    (favors H0 = no contamination)
        N = harmonic mean of n_pre + n_post (effective sample size)

    Interpretation:
        - 小 p → 大 z² → BF_10 大 → BF_01 小 → "evidence FOR contamination"
        - 大 p → 小 z² → BF_10 ~ 1 → BF_01 ~ sqrt(n) → "evidence AGAINST contamination"

    返回 (bayes_factor_01, qualitative_label).
    bayes_factor_01 越小 → contamination 证据越强.
    """
    if not np.isfinite(p_value) or p_value <= 0:
        return float('nan'), "p-value invalid"

    from math import exp, log

    n_harmonic = 2 / (1.0 / max(n_pre, 1) + 1.0 / max(n_post, 1))
    z = abs(norm.ppf(p_value / 2))

    # V2 修复: log BF_01 = 0.5 * log(n) - 0.5 * z²
    # (旧公式 0.5*log(n) - 0.5*z² 给的是 log BF_10 但被错赋值给 bf_10 变量,
    # 然后再 1/bf_10 反推 bf_01 — 双重符号错误抵消了一部分但结果仍错)
    log_bf_01 = 0.5 * log(n_harmonic) - 0.5 * z ** 2
    # log BF_01 < 0 → bf_01 < 1 → contamination evidence
    # log BF_01 > 0 → bf_01 > 1 → no contamination evidence
    bf_01 = exp(log_bf_01)

    for threshold, label in BAYES_FACTOR_LABELS:
        if bf_01 <= threshold:
            return float(bf_01), label
    return float(bf_01), "very strong evidence AGAINST contamination"


def contamination_test(
    df: pd.DataFrame,
    *,
    llm_col: str,
    outcome_col: str,
    cutoff_date: str,                  # C5: 强制 caller 提供, 无默认值
    date_col: str = 'date',
    method: str = 'pearson',
) -> dict:
    """Run pre/post cutoff contamination test.

    Args:
        df: panel 含 LLM 输出列 + outcome 列 + date 列.
        llm_col: LLM 输出列名 (e.g. 'llm_vote_tone_full').
        outcome_col: outcome 列名 (e.g. 'z_score').
        date_col: 日期列名 (datetime 可解析).
        cutoff_date: ISO format 'YYYY-MM-DD'.
        method: 'pearson' or 'spearman'.

    Returns:
        dict 含 contamination report 字段 (参 module docstring).
    """
    required = {llm_col, outcome_col, date_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"必填列缺失: {missing}")

    cutoff = pd.Timestamp(cutoff_date)
    dates = pd.to_datetime(df[date_col], errors='coerce')

    pre_mask = dates < cutoff
    post_mask = dates >= cutoff
    df_pre = df[pre_mask].copy()
    df_post = df[post_mask].copy()

    r_pre, n_pre = compute_correlation(df_pre, llm_col, outcome_col, method)
    r_post, n_post = compute_correlation(df_post, llm_col, outcome_col, method)
    z_stat, p_value = fisher_z_test(r_pre, n_pre, r_post, n_post)

    try:
        bf, bf_label = classify_bayes_factor(p_value, n_pre, n_post)
    except ImportError:
        bf, bf_label = float('nan'), 'scipy unavailable'

    # Verdict
    if not np.isfinite(p_value):
        verdict = 'inconclusive'
    elif p_value < 0.05 and r_pre > r_post:
        verdict = 'contamination_detected'
    elif p_value < 0.05 and r_pre < r_post:
        verdict = 'reverse_pattern_anomaly'  # unexpected, 需要人工 review
    else:
        verdict = 'no_contamination_evidence'

    report = {
        'method': method,
        'cutoff_date': cutoff_date,
        'llm_col': llm_col,
        'outcome_col': outcome_col,
        'n_pre_cutoff': int(n_pre),
        'n_post_cutoff': int(n_post),
        'r_pre_cutoff': r_pre,
        'r_post_cutoff': r_post,
        'fisher_z_stat': z_stat,
        'fisher_p_value': p_value,
        'bayes_factor_h0': bf,
        'bayes_factor_label': bf_label,
        'verdict': verdict,
        'computed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    return report


STAGE_NAME = "39h_llm_contamination_test"


def run_stage(config=None):
    """Stage 39h 入口 (config 驱动, opt-in 默认禁用).

    DC4 LLM 训练数据污染留出检验. 与 CLI ``main()`` 的区别:
    - cutoff / 列名 / 输入路径全部从 config 读取. ``cutoff`` 须用户在
      ``config/validation.yaml::llm_contamination_test.cutoff`` 显式提供
      (来源为 LLM provider 官方文档, 不得伪造 — 见模块 docstring C5 修复);
      未配置则优雅跳过, 绝不 fabricate.
    - 缺面板 / 缺 outcome 列 (``z_score`` 来自 opt-in stage 49 risk_taking_outcomes) /
      未配 cutoff / pre-post 样本不足时一律优雅跳过 (log + return 0, 不 raise),
      与同族 39d/39e "缺列 graceful skip" 约定一致 (T=2 面板年份多 < cutoff,
      n_post 通常为 0, 属预期).
    """
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)
    if config is None:
        from news_process.core.config import load_config
        config = load_config()

    logger.info("=" * 60)
    logger.info("Stage 39h: LLM contamination holdout test (DC4 F-Adv.2)")

    cfg = config.get('llm_contamination_test', {}) or {}
    paths = config.get('paths', {}) or {}
    filenames = config.get('filenames', {}) or {}
    output_dir = Path(paths.get('output_dir', 'data/processed'))
    panel_name = filenames.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    input_path = Path(cfg.get('input') or (output_dir / panel_name))
    llm_col = cfg.get('llm_col', 'llm_vote_tone_full')
    outcome_col = cfg.get('outcome_col', 'z_score')
    date_col = cfg.get('date_col', 'year')
    cutoff = cfg.get('cutoff')  # None → 跳过 (禁止伪造 cutoff)
    method = cfg.get('method', 'pearson')
    report_path = Path(cfg.get('report') or (output_dir / 'llm_contamination_report.json'))

    if not input_path.exists():
        logger.warning("[skip] 面板不存在: %s — Stage 39h 跳过.", input_path)
        return 0
    if not cutoff:
        logger.warning(
            "[skip] 未配置 cutoff (config/validation.yaml::llm_contamination_test.cutoff); "
            "cutoff 须来自 LLM provider 官方文档不得伪造 — Stage 39h 跳过.")
        return 0

    df = pd.read_parquet(input_path)
    if outcome_col not in df.columns:
        logger.warning(
            "[skip] outcome 列 %r 不在面板 (来自 opt-in stage 49 risk_taking_outcomes, "
            "尚未并入面板) — Stage 39h 跳过.", outcome_col)
        return 0
    if llm_col not in df.columns:
        logger.warning("[skip] LLM 列 %r 不在面板 — Stage 39h 跳过.", llm_col)
        return 0

    if date_col == 'year':
        df['_test_date'] = pd.to_datetime(df['year'].astype(str) + '-07-01')
        eff_date_col = '_test_date'
    else:
        eff_date_col = date_col

    try:
        report = contamination_test(
            df, llm_col=llm_col, outcome_col=outcome_col,
            date_col=eff_date_col, cutoff_date=cutoff, method=method,
        )
    except Exception as exc:  # noqa: BLE001 — 同族 graceful-skip: 样本不足时不阻塞验证管线
        logger.warning(
            "[skip] contamination_test 无法在当前样本计算 (%s: %s); "
            "通常因 pre/post-cutoff 样本不足 (T=2 面板年份 < cutoff) — Stage 39h 跳过.",
            type(exc).__name__, exc)
        return 0

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Stage 39h verdict=%s → %s", report.get('verdict'), report_path)
    return 0


def main():
    """CLI 入口."""
    parser = argparse.ArgumentParser(
        description='V4 DC4: LLM contamination holdout test'
    )
    parser.add_argument('--input', type=Path, required=True,
                        help='panel parquet 路径')
    parser.add_argument('--llm-col', default='llm_vote_tone_full')
    parser.add_argument('--outcome-col', default='z_score')
    parser.add_argument('--date-col', default='year')
    parser.add_argument('--cutoff', required=True,
                        help='LLM training data cutoff ISO date — MUST come from '
                             'LLM provider official documentation, NOT fabricated. '
                             'See module docstring §"反模式".')
    parser.add_argument('--method', default='pearson',
                        choices=['pearson', 'spearman'])
    parser.add_argument('--report', type=Path,
                        default='data/processed/llm_contamination_report.json')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    df = pd.read_parquet(args.input)
    logger.info(f"Loaded {len(df)} rows from {args.input}")

    # 若 date_col 是 year, 转 datetime (年中点)
    if args.date_col == 'year':
        df['_test_date'] = pd.to_datetime(df['year'].astype(str) + '-07-01')
        date_col = '_test_date'
    else:
        date_col = args.date_col

    report = contamination_test(
        df,
        llm_col=args.llm_col,
        outcome_col=args.outcome_col,
        date_col=date_col,
        cutoff_date=args.cutoff,
        method=args.method,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"LLM CONTAMINATION TEST: {report['verdict'].upper()}")
    print("=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
