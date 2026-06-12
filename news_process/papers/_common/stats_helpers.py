"""Statistical helpers for paper-level robustness analysis.

V2.0 J-L-M 2026 RFS robustness alignment plan §3 Phase 1 (P1.4 + P1.5):

- `within_unit_sd`: Within-group standard deviation for economic significance
  reporting per J-L-M 2026 RFS §2.1 convention:
    "A 1 within-bank SD increase in benefit_mean ≈ X bp change in ROA"

- `cluster_block_bootstrap_ci`: (cluster) block bootstrap percentile 95% CI。
  fix(omni-g-papers-misc-10, 2026-06-11) 方法标签更正: 本实现自始是
  Carlstein (1986) / Künsch (1989) 式**有放回块自助** (resample blocks with
  replacement to size n, percentile CI), **不是**旧文档宣称的 Politis-Romano
  (1994 Annals of Statistics) subsampling — 后者的定义特征是抽 b≪n 的无放回
  子样本并以 sqrt(b/n) 重标定统计量分布, 二者收敛条件与有效性论证不同。
  旧名 `block_subsampling_ci` 保留为 DeprecationWarning alias。
  新增 `cluster_id` 簇模式: 按真实依赖单元 (如 target_bank) 整簇重采样,
  替代位置切片块 (位置块在 dropna 移位 / T>2 不平衡面板下会跨银行)。

Both helpers are pure NumPy/pandas; no external API dependencies, no
sentence_transformers, no Stata. CI-safe across all 5 matrix jobs.
"""

from __future__ import annotations

import warnings

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


def cluster_block_bootstrap_ci(
    values: np.ndarray | pd.Series | list[float],
    cluster_id: np.ndarray | pd.Series | list | None = None,
    block_size: int = 2,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    """(Cluster) block bootstrap percentile CI for the sample mean.

    fix(omni-g-papers-misc-10, 2026-06-11) 方法标签更正: 本函数实现的是
    Carlstein (1986) / Künsch (1989) 式**有放回块自助百分位 CI** (抽满 n 的
    with-replacement 块重采样), 不是 Politis-Romano (1994) subsampling
    (b≪n 无放回 + sqrt(b/n) 重标定)。算法本体保持原状 (golden-safe), 仅命名/
    文档更正 + 新增 ``cluster_id`` 簇模式。

    Two resampling modes:

    - **cluster mode** (``cluster_id`` given, 推荐): 按真实依赖单元 (如
      ``target_bank``) 整簇有放回重采样 (cluster bootstrap over banks)。
      在 dropna 移位 / T>2 不平衡面板下仍保证块=同一银行的观测, 修复位置
      切片块跨银行错位的 latent 缺陷。
    - **positional mode** (``cluster_id=None``, 兼容旧行为): 相邻位置
      non-overlapping blocks of ``block_size``; 仅当输入已按依赖单元排序且
      无缺失移位时块与依赖结构对齐 (caller beware)。

    Parameters
    ----------
    values
        Numeric values (e.g., bank-year benefit_mean).
    cluster_id
        Optional cluster labels aligned with ``values`` (e.g., target_bank)。
        Given → cluster mode; None → positional-block mode.
    block_size
        Positional mode only — consecutive observations per block. Default 2
        reflects short-T panel context; rule of thumb ``floor(n ** (1/3))``.
    n_resamples
        Number of bootstrap resamples (with replacement).
    alpha
        Significance level. Default 0.05 → 95% CI.
    seed
        RNG seed for reproducibility.

    Returns
    -------
    tuple[float, float, float]
        ``(point_estimate, lower_bound, upper_bound)`` — bounds are the
        empirical ``alpha/2`` / ``1 - alpha/2`` percentile of resampled means.

    Raises
    ------
    ValueError
        Positional mode: fewer than ``block_size * 2`` non-NaN obs.
        Cluster mode: fewer than 2 distinct clusters with valid obs.
    """
    rng = np.random.default_rng(seed)

    if cluster_id is not None:
        vals = pd.Series(np.asarray(values, dtype=float).ravel())
        cl = pd.Series(list(cluster_id)).reset_index(drop=True)
        if len(cl) != len(vals):
            raise ValueError(
                f"cluster_id length {len(cl)} != values length {len(vals)}")
        ok = vals.notna() & cl.notna()
        vals, cl = vals[ok], cl[ok]
        groups = [g.to_numpy() for _, g in vals.groupby(cl.to_numpy())]
        if len(groups) < 2:
            raise ValueError(
                f"cluster mode needs >= 2 distinct clusters with valid obs; "
                f"got {len(groups)}.")
        point = float(vals.mean())
        n_clusters = len(groups)
        resample_means = np.empty(n_resamples, dtype=float)
        for i in range(n_resamples):
            chosen = rng.integers(0, n_clusters, size=n_clusters)
            resample_means[i] = float(
                np.concatenate([groups[j] for j in chosen]).mean())
        lower = float(np.quantile(resample_means, alpha / 2.0))
        upper = float(np.quantile(resample_means, 1.0 - alpha / 2.0))
        return point, lower, upper

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
    resample_means = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        chosen = rng.choice(block_starts, size=n_blocks, replace=True)
        # Vectorized block gather: shape (n_blocks, block_size) → flatten
        idx = chosen[:, None] + np.arange(block_size)[None, :]
        resample_means[i] = arr[idx.ravel()].mean()

    lower = float(np.quantile(resample_means, alpha / 2.0))
    upper = float(np.quantile(resample_means, 1.0 - alpha / 2.0))
    return point, lower, upper


def block_subsampling_ci(
    values: np.ndarray | pd.Series | list[float],
    block_size: int = 2,
    n_subsamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    """DEPRECATED misnomer alias — see ``cluster_block_bootstrap_ci``.

    fix(omni-g-papers-misc-10, 2026-06-11): 旧名宣称 Politis-Romano (1994)
    subsampling, 但实现是 with-replacement 块自助 (block bootstrap)。保留此
    alias 仅为向后兼容; 数值行为与旧实现逐位一致 (positional mode 同 RNG 序)。
    """
    warnings.warn(
        "block_subsampling_ci is a misnomer (the implementation is a "
        "with-replacement block bootstrap, NOT Politis-Romano 1994 "
        "subsampling); use cluster_block_bootstrap_ci instead",
        DeprecationWarning, stacklevel=2)
    return cluster_block_bootstrap_ci(
        values, cluster_id=None, block_size=block_size,
        n_resamples=n_subsamples, alpha=alpha, seed=seed)


__all__ = ["within_unit_sd", "cluster_block_bootstrap_ci", "block_subsampling_ci"]
