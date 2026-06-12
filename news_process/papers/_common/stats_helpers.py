"""论文级稳健性分析的统计 helper。

V2.0 J-L-M 2026 RFS robustness 对齐计划 §3 Phase 1 (P1.4 + P1.5):

- `within_unit_sd`: 组内标准差, 用于经济显著性报告,
  依 J-L-M 2026 RFS §2.1 惯例:
    "benefit_mean 提高 1 个 within-bank SD ≈ ROA 变动 X bp"

- `cluster_block_bootstrap_ci`: (cluster) block bootstrap percentile 95% CI。
  fix(omni-g-papers-misc-10, 2026-06-11) 方法标签更正: 本实现自始是
  Carlstein (1986) / Künsch (1989) 式**有放回块自助** (resample blocks with
  replacement to size n, percentile CI), **不是**旧文档宣称的 Politis-Romano
  (1994 Annals of Statistics) subsampling — 后者的定义特征是抽 b≪n 的无放回
  子样本并以 sqrt(b/n) 重标定统计量分布, 二者收敛条件与有效性论证不同。
  旧名 `block_subsampling_ci` 保留为 DeprecationWarning alias。
  新增 `cluster_id` 簇模式: 按真实依赖单元 (如 target_bank) 整簇重采样,
  替代位置切片块 (位置块在 dropna 移位 / T>2 不平衡面板下会跨银行)。

两个 helper 均为纯 NumPy/pandas; 不依赖外部 API、sentence_transformers
或 Stata。在全部 5 个 CI matrix job 上安全可跑。
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd


def within_unit_sd(
    series: pd.Series | np.ndarray | list[float],
    unit_id: pd.Series | np.ndarray | list,
) -> float:
    """计算组内标准差 (within-unit, 组内去均值后的 SD, ddof=1)。

    先按 `unit_id` 组内去均值, 再返回去均值残差的 SD。
    遵循 J-L-M 2026 RFS §2.1 惯例: 报告 within-country SD,
    用于衡量加入固定效应后的经济显著性。

    Parameters
    ----------
    series
        数值序列 (如 bank-year 级的 benefit_mean_full)。
    unit_id
        分组变量 (如 target_bank 或 bank_id)。

    Returns
    -------
    float
        组内 SD。剔除 NaN 行后有效观测不足 2 个时返回 ``float('nan')``。

    Notes
    -----
    - `series` 中的 NaN 在去均值前剔除。
    - 单观测组对去均值残差贡献为 0 (其组均值等于自身)。
    - 用样本 SD (``ddof=1``)。
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
    """样本均值的 (cluster) block bootstrap 百分位 CI。

    fix(omni-g-papers-misc-10, 2026-06-11) 方法标签更正: 本函数实现的是
    Carlstein (1986) / Künsch (1989) 式**有放回块自助百分位 CI** (抽满 n 的
    with-replacement 块重采样), 不是 Politis-Romano (1994) subsampling
    (b≪n 无放回 + sqrt(b/n) 重标定)。算法本体保持原状 (golden-safe), 仅命名/
    文档更正 + 新增 ``cluster_id`` 簇模式。

    两种重采样模式:

    - **cluster mode** (``cluster_id`` given, 推荐): 按真实依赖单元 (如
      ``target_bank``) 整簇有放回重采样 (cluster bootstrap over banks)。
      在 dropna 移位 / T>2 不平衡面板下仍保证块=同一银行的观测, 修复位置
      切片块跨银行错位的 latent 缺陷。
    - **positional mode** (``cluster_id=None``, 兼容旧行为): 相邻位置
      non-overlapping blocks of ``block_size``; 仅当输入已按依赖单元排序且
      无缺失移位时块与依赖结构对齐 (caller beware)。

    白话: 普通 bootstrap 假设观测彼此独立, 但同一家银行不同年份的数据
    是相关的; 所以重抽样时要"整块/整簇"地抽 — 推荐传 cluster_id 按银行
    整簇抽 (不怕缺失值错位), 不传则退回按相邻位置切块的旧行为 (要求
    调用方自己保证数据已按银行排好且无缺失)。

    Parameters
    ----------
    values
        数值序列 (如 bank-year 级 benefit_mean)。
    cluster_id
        可选 — 与 ``values`` 对齐的簇标签 (如 target_bank)。
        给定 → cluster mode; None → positional-block mode。
    block_size
        仅 positional mode 用 — 每块连续观测数。默认 2 对应短 T 面板
        语境; 经验法则 ``floor(n ** (1/3))``。
    n_resamples
        bootstrap 重采样次数 (有放回)。
    alpha
        显著性水平。默认 0.05 → 95% CI。
    seed
        RNG 种子 (可复现)。

    Returns
    -------
    tuple[float, float, float]
        ``(point_estimate, lower_bound, upper_bound)`` — 上下界为重采样
        均值的经验 ``alpha/2`` / ``1 - alpha/2`` 分位数。

    Raises
    ------
    ValueError
        positional mode: 非 NaN 观测少于 ``block_size * 2``。
        cluster mode: 含有效观测的不同簇少于 2 个。
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
        # 向量化取块: 形状 (n_blocks, block_size) → 拉平
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
    """已弃用的错误命名别名 (DEPRECATED misnomer) — 见 ``cluster_block_bootstrap_ci``。

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
