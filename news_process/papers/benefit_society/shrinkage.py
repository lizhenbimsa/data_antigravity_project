"""news_process.papers.benefit_society.shrinkage
=================================================
Hierarchical empirical Bayes shrinkage for benefit_mean in sparse-coverage settings.

【目的】
- 当某些 bank-year 单元仅有 1-3 篇新闻时, benefit_mean 标准误大
- 用 hierarchical model 将稀疏单元向"同省同类型均值"收缩
- Bias-variance tradeoff: 引入小 bias 换取大幅降 variance

【方法】
- James-Stein-style empirical Bayes (closed-form, no MCMC)
- Group-wise pooling on (bank_type, province) 群组均值
- Shrinkage weight = σ²_within / (σ²_within + n_i × σ²_between)

【为什么用 closed-form 而非 PyMC/Stan】
- 避免重依赖 (PyMC ~ 100MB)
- closed-form James-Stein 在 group-level shrinkage 上已是最优 (Efron-Morris 1973)
- statsmodels.regression.mixed_linear_model 作 sanity check

【输入/输出】
- 输入: bank-year panel with [benefit_mean_full, n_articles, bank_type, province]
- 输出: panel + [benefit_mean_full_shrunk, shrinkage_weight]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. James-Stein closed-form shrinkage
# ---------------------------------------------------------------------------
def empirical_bayes_shrinkage(
    values: np.ndarray,
    n_obs: np.ndarray,
    group_labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Shrink ``values`` toward group means weighted by within-unit precision.

    Parameters
    ----------
    values : np.ndarray, shape (N,)
        Raw bank-year measurements (e.g., benefit_mean_full)
    n_obs : np.ndarray, shape (N,)
        Number of articles backing each measurement
    group_labels : np.ndarray, shape (N,)
        Group identifier (e.g., bank_type×province combo)

    Returns
    -------
    shrunk : np.ndarray, shape (N,)
        Shrunk measurements
    weights : np.ndarray, shape (N,)
        Shrinkage weights ∈ [0, 1], where 1 = full pooling toward group mean,
        0 = no shrinkage (keep raw)
    """
    if not (len(values) == len(n_obs) == len(group_labels)):
        raise ValueError("values, n_obs, group_labels must have equal length")

    values = np.asarray(values, dtype=np.float64)
    n_obs = np.asarray(n_obs, dtype=np.float64)
    group_labels = np.asarray(group_labels)

    valid_mask = np.isfinite(values) & (n_obs > 0)
    if valid_mask.sum() < 2:
        logger.warning("Insufficient valid observations for shrinkage; returning raw values")
        return values.copy(), np.zeros_like(values)

    # Compute group means
    unique_groups, inverse = np.unique(group_labels[valid_mask], return_inverse=True)
    group_means = np.array(
        [values[valid_mask][inverse == g].mean() for g in range(len(unique_groups))]
    )

    # Map back to all rows
    group_mean_per_row = np.full(len(values), np.nan, dtype=np.float64)
    group_lookup = dict(zip(unique_groups, group_means))
    for i, g in enumerate(group_labels):
        if g in group_lookup:
            group_mean_per_row[i] = group_lookup[g]

    # Within-unit variance (proxy: 1/n_obs scaled by grand variance)
    grand_var = np.var(values[valid_mask], ddof=1) if valid_mask.sum() > 1 else 1.0
    within_var = grand_var / np.maximum(n_obs, 1.0)

    # Between-group variance (residual after group means)
    deviations = values[valid_mask] - group_mean_per_row[valid_mask]
    between_var = max(np.var(deviations, ddof=1), 1e-8) if len(deviations) > 1 else 1e-8

    # James-Stein weight: w = within_var / (within_var + between_var)
    # When n_obs is large → within_var small → w small → less shrinkage
    weights = within_var / (within_var + between_var)
    weights = np.clip(weights, 0.0, 1.0)
    weights = np.where(valid_mask, weights, 0.0)

    shrunk = np.where(
        valid_mask & np.isfinite(group_mean_per_row),
        weights * group_mean_per_row + (1.0 - weights) * values,
        values,
    )

    return shrunk, weights


# ---------------------------------------------------------------------------
# 2. Sanity check via statsmodels MixedLM (optional, slow)
# ---------------------------------------------------------------------------
def mixedlm_sanity_check(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
) -> dict | None:
    """Run a random-intercept MixedLM as cross-validation of closed-form shrinkage.

    Returns
    -------
    dict with {sigma_within, sigma_between, icc} or None if statsmodels unavailable
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
# 3. Panel-level shrinkage wrapper
# ---------------------------------------------------------------------------
def apply_shrinkage_to_panel(
    panel: pd.DataFrame,
    *,
    value_col: str = "benefit_mean_full",
    n_obs_col: str = "n_articles",
    group_cols: tuple[str, ...] = ("bank_type", "bank_province"),  # F8 fix: align with existing panel
    output_col: str | None = None,
) -> pd.DataFrame:
    """Apply empirical Bayes shrinkage to a bank-year panel column.

    Adds two columns:
    - {output_col}: shrunk values
    - {output_col}_weight: shrinkage weight per row
    """
    if output_col is None:
        output_col = f"{value_col}_shrunk"

    df = panel.copy()
    missing = [c for c in (value_col, n_obs_col, *group_cols) if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    # Build composite group label
    group_label = df[list(group_cols)].astype(str).agg("|".join, axis=1).values

    shrunk, weights = empirical_bayes_shrinkage(
        df[value_col].values,
        df[n_obs_col].values,
        group_label,
    )

    df[output_col] = shrunk
    df[f"{output_col}_weight"] = weights
    return df


# ---------------------------------------------------------------------------
# 4. CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """CLI entry: apply empirical Bayes shrinkage to benefit_mean on a panel parquet.

    Returns 0 on success, 1 if required panel columns are missing.
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.shrinkage",
        description="Hierarchical empirical Bayes shrinkage for benefit_mean",
    )
    parser.add_argument(
        "--panel",
        type=str,
        default="news_process/data/processed/40_panel_yearly.parquet",
    )
    parser.add_argument("--value-col", type=str, default="benefit_mean_full")
    parser.add_argument("--n-obs-col", type=str, default="n_articles")
    parser.add_argument(
        "--group-cols",
        type=str,
        default="bank_type,bank_province",  # F8 fix
        help="Comma-separated grouping columns (must exist in panel)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/40_panel_yearly_shrunk.parquet",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    panel = pd.read_parquet(args.panel)
    logger.info(f"Loaded panel: {panel.shape}")

    group_cols = tuple(c.strip() for c in args.group_cols.split(","))
    missing = [c for c in (args.value_col, args.n_obs_col, *group_cols) if c not in panel.columns]
    if missing:
        logger.error(
            f"Required columns missing: {missing}. "
            "Build the auxiliary panel with bank_type, province, n_articles first."
        )
        return 1

    result = apply_shrinkage_to_panel(
        panel,
        value_col=args.value_col,
        n_obs_col=args.n_obs_col,
        group_cols=group_cols,
    )

    sanity = mixedlm_sanity_check(panel, args.value_col, group_cols[0])
    if sanity:
        logger.info(f"MixedLM sanity: ICC={sanity['icc']:.3f}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    logger.info(
        f"Wrote shrunk panel to {output_path}: "
        f"mean shrinkage weight = {result[f'{args.value_col}_shrunk_weight'].mean():.3f}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
