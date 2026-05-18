"""news_process.pipeline.audit.lm_discriminant_validity — stage 39e.

v3.5.2 PR #4 — LM 4 子词典与 v3.5.1 lexical clarity / numerical intensity
的 panel-level 判别效度 (Discriminant Validity) 测试.

学术依据
--------
Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for
assessing discriminant validity in variance-based structural equation
modeling. Journal of the Academy of Marketing Science, 43(1), 115-135.
→ HTMT (Heterotrait-Monotrait ratio) 双 cutoff: 0.85 strict / 0.90 lenient

Cohen, J. (1960). A coefficient of agreement for nominal scales.
Educational and Psychological Measurement, 20(1), 37-46.

Cronbach, L. J. (1951). Coefficient alpha and the internal structure of
tests. Psychometrika, 16(3), 297-334.

测试指标对
----------
本 stage 测试 6 维构念间的判别效度:
    1. uncert_frac (LM uncertainty)
    2. litig_frac (LM litigious)
    3. constr_frac (LM constraining)
    4. modal_strong_frac (LM modal_strong)
    5. clarity_score (v3.5.1 A1)
    6. num_intensity (v3.5.1 A3)

预期: 6×6 HTMT 矩阵中 LM 4 子集互相 HTMT < 0.85, 且与 clarity / num_intensity
HTMT < 0.85 (判别效度通过).

输入 / 输出
-----------
输入: ``data/processed/40_panel_yearly.parquet`` (含 v3.5.1 + v3.5.2 全部列)
输出:
    ``eval_reports/39e_lm_htmt_matrix.csv``     6×6 HTMT 矩阵
    ``eval_reports/39e_lm_kappa.csv``           pairwise Cohen κ
    ``eval_reports/39e_lm_cronbach_alpha.csv``  6 indicator Cronbach α
    ``eval_reports/39e_lm_permutation.csv``     1000-rep permutation null
    ``data/processed/39e_lm_htmt.parquet``      machine-readable HTMT

stub 说明
---------
当前是 PR #4 stub: ``main()`` 入口 + key 函数骨架, 实际 HTMT 计算依赖
v3.5.2 PR #3 (lm_non_sentiment) 输出 panel 列存在; G-A1.2 准入门控
(panel HTMT < 0.85 on 9000 bank-year) 验证由 PR #14 集成完成.
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "39e_lm_discriminant_validity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 6 个 indicator 列 (双轨各一组; main spec 用 _ctx 与 P1 v3.6.0 G3 对齐)
INDICATORS_CTX = [
    'uncert_frac_ctx',
    'litig_frac_ctx',
    'constr_frac_ctx',
    'modal_strong_frac_ctx',
    'mean_clarity_score_ctx',
    'mean_num_intensity_ctx',
]
INDICATORS_FULL = [
    'uncert_frac_full',
    'litig_frac_full',
    'constr_frac_full',
    'modal_strong_frac_full',
    'mean_clarity_score_full',
    'mean_num_intensity_full',
]

HTMT_STRICT = 0.85
HTMT_LENIENT = 0.90


def compute_htmt_matrix(panel: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    """k×k HTMT 矩阵 (Henseler et al. 2015 JAMS).

    HTMT(i, j) = corr(indicator_i, indicator_j) / sqrt(rel_i × rel_j),
    其中 rel_i 用 Cronbach α 估单维 reliability. 因 LM 子集 single-item,
    退化为 single-indicator HTMT = |corr(i, j)| / sqrt(1 × 1) = |corr|.

    Note:
        v3.5.1 stage 39d 已实现 multi-indicator HTMT 完整版; stage 39e 因
        LM 4 子集为 single-item, 用 abs(Pearson r) 作为 HTMT 简化估计.
        与 39d 互补不冲突.
    """
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        logger.warning(f"  indicators 列不足 2 列存在 ({present}); HTMT 跳过")
        return pd.DataFrame()
    corr = panel[present].corr().abs()
    return corr


def compute_cronbach_alpha(panel: pd.DataFrame, indicators: list[str]) -> float:
    """Cronbach α (Cronbach 1951) across 6 indicators."""
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return float('nan')
    sub = panel[present].dropna()
    k = len(present)
    if len(sub) < 2:
        return float('nan')
    var_items = sub.var(axis=0).sum()
    var_total = sub.sum(axis=1).var()
    if var_total == 0:
        return float('nan')
    return (k / (k - 1)) * (1 - var_items / var_total)


def permutation_null(panel: pd.DataFrame, indicators: list[str],
                     n_perm: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Permutation null distribution for HTMT (random column shuffles).

    Stub: 完整实现仿 stage 39c::permutation_null (n_jobs=16 on MP 64-core).
    """
    rng = np.random.default_rng(seed)
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return pd.DataFrame()
    # Stub: 仅返回观测 HTMT 上限均值 (实际跑由 PR #14 完整化).
    obs_htmt = compute_htmt_matrix(panel, present)
    if obs_htmt.empty:
        return pd.DataFrame()
    np.fill_diagonal(obs_htmt.values, np.nan)
    obs_max = obs_htmt.max().max()
    perm_max = []
    for _ in range(min(n_perm, 100)):  # stub: 100 reps 而非 1000
        shuffled = panel[present].apply(lambda c: rng.permutation(c.values))
        h = shuffled.corr().abs()
        np.fill_diagonal(h.values, np.nan)
        perm_max.append(h.max().max())
    p_emp = float((np.array(perm_max) >= obs_max).mean())
    return pd.DataFrame([{
        'obs_htmt_max': obs_htmt.max().max(),
        'perm_htmt_max_mean': float(np.mean(perm_max)),
        'perm_htmt_max_p95': float(np.percentile(perm_max, 95)),
        'p_empirical': p_emp,
        'n_perm': len(perm_max),
        'note': 'stub: 100 reps; 完整 1000 reps 由 PR #14 启用',
    }])


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 39e: LM Non-Sentiment 判别效度 (v3.5.2 PR #4)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['data_processed_dir']
    eval_dir = os.path.join(output_dir, '..', 'eval_reports')
    os.makedirs(eval_dir, exist_ok=True)

    panel_path = os.path.join(output_dir, '40_panel_yearly.parquet')
    if not os.path.exists(panel_path):
        logger.error(f"  panel 未找到: {panel_path}; 跳过 39e")
        sys.exit(0)

    panel = pd.read_parquet(panel_path)
    logger.info(f"  panel: {len(panel)} 行 × {len(panel.columns)} 列")

    # 双轨各跑一次 (与 v3.5.1 stage 39d 对齐)
    for suffix, indicators in (('ctx', INDICATORS_CTX), ('full', INDICATORS_FULL)):
        logger.info(f"  ── 轨道 {suffix} ──")
        htmt = compute_htmt_matrix(panel, indicators)
        if htmt.empty:
            logger.warning(f"  {suffix}: HTMT 跳过 (indicator 列缺失)")
            continue
        htmt_path = os.path.join(eval_dir, f'39e_lm_htmt_matrix_{suffix}.csv')
        htmt.to_csv(htmt_path)
        logger.info(f"    HTMT matrix → {htmt_path}")

        alpha = compute_cronbach_alpha(panel, indicators)
        logger.info(f"    Cronbach α = {alpha:.4f}")

        perm = permutation_null(panel, indicators)
        if not perm.empty:
            perm_path = os.path.join(eval_dir, f'39e_lm_permutation_{suffix}.csv')
            perm.to_csv(perm_path, index=False)
            logger.info(f"    Permutation → {perm_path}")

        # G-A1.2 准入门控判定
        np.fill_diagonal(htmt.values, np.nan)
        max_htmt = htmt.max().max()
        logger.info(
            f"    G-A1.2 判定: max HTMT = {max_htmt:.4f} "
            f"({'PASS' if max_htmt < HTMT_STRICT else 'FAIL (need expert audit)'})"
        )

    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
