"""Statistical helpers for paper-level robustness analysis.

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 (P1.4 + P1.5):

- `within_unit_sd`: Within-group standard deviation for economic significance
  reporting per J-L-M 2026 RFS §2.1 convention:
    "A 1 within-bank SD increase in benefit_mean ≈ X bp change in ROA"

- `block_subsampling_ci`: Block-subsampling 95% CI (Politis-Romano 1994
  *Annals of Statistics*) replicating J-L-M 2026 Figure 2 CI methodology.
  Uses non-overlapping blocks to preserve within-block dependence.

Both helpers are pure NumPy/pandas; no external API dependencies, no
sentence_transformers, no Stata. CI-safe across all 5 matrix jobs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def within_unit_sd(
    series: pd.Series | np.ndarray | list[float],
    unit_id: pd.Series | np.ndarray | list,
) -> float:
    """Compute within-unit standard deviation (group-demeaned SD, ddof=1).

    Group-demean values by `unit_id`, then return SD of demeaned residuals.
    Following J-L-M 2026 RFS §2.1 convention where within-country SD is
    reported to gauge economic significance after country fixed effects.

    Parameters
    ----------
    series
        Numeric values (e.g., benefit_mean_full at bank-year level).
    unit_id
        Grouping variable (e.g., target_bank or bank_id).

    Returns
    -------
    float
        Within-unit SD. Returns ``float('nan')`` when fewer than 2 valid
        (non-NaN) observations remain after dropping NaN rows.

    Notes
    -----
    - NaN values in `series` are dropped before demeaning.
    - Single-observation groups contribute 0 to the demeaned residual
      (their group mean equals their value).
    - Uses sample SD (``ddof=1``).
    """
    df = pd.DataFrame({"y": pd.Series(series), "unit": pd.Series(unit_id)})
    df = df.dropna(subset=["y", "unit"])
    if len(df) < 2:
        return float("nan")
    df["y_demeaned"] = df["y"] - df.groupby("unit")["y"].transform("mean")
    sd = df["y_demeaned"].std(ddof=1)
    return float(sd) if pd.notna(sd) else float("nan")


def block_subsampling_ci(
    values: np.ndarray | pd.Series | list[float],
    block_size: int = 2,
    n_subsamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Block-subsampling confidence interval for the sample mean.

    Implements Politis-Romano (1994) non-overlapping block subsampling.
    Aligns with J-L-M 2026 RFS Figure 2 caption: "Bands represent 95%
    confidence intervals produced by subsampling."

    Parameters
    ----------
    values
        Numeric values (e.g., article-level benefit_score within a year).
    block_size
        Number of consecutive observations per block. Default 2 reflects
        short-T panel context; rule of thumb ``floor(n ** (1/3))``.
    n_subsamples
        Number of block-resamples drawn with replacement.
    alpha
        Significance level. Default 0.05 → 95% CI.
    seed
        RNG seed for reproducibility.

    Returns
    -------
    tuple[float, float, float]
        ``(point_estimate, lower_bound, upper_bound)`` where the bounds
        are the empirical ``alpha/2`` and ``1 - alpha/2`` quantiles of
        the block-resampled means.

    Raises
    ------
    ValueError
        If fewer than ``block_size * 2`` non-NaN observations are
        available (insufficient for at least 2 blocks).
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float).ravel()
    arr = arr[~np.isnan(arr)]
    n = arr.size
    if n < block_size * 2:
        raise ValueError(
            f"Need at least block_size * 2 = {block_size * 2} non-NaN "
            f"observations; got {n}."
        )
    n_blocks = n // block_size
    block_starts = np.arange(n_blocks) * block_size

    point = float(arr.mean())
    subsample_means = np.empty(n_subsamples, dtype=float)
    for i in range(n_subsamples):
        chosen = rng.choice(block_starts, size=n_blocks, replace=True)
        # Vectorized block gather: shape (n_blocks, block_size) → flatten
        idx = chosen[:, None] + np.arange(block_size)[None, :]
        subsample_means[i] = arr[idx.ravel()].mean()

    lower = float(np.quantile(subsample_means, alpha / 2.0))
    upper = float(np.quantile(subsample_means, 1.0 - alpha / 2.0))
    return point, lower, upper


__all__ = ["within_unit_sd", "block_subsampling_ci"]
