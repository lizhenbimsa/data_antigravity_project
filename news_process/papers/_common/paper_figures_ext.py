"""news_process.papers._common.paper_figures_ext — Figure 2-4 通用 helper。

P3.1 (plan-r3 derivative-paper extension, 2026-05-15)

消费 Stata esttab CSV 输出 (经 ``stata_postprocess.parse_esttab_csv``
解析) 的通用发表级 matplotlib 图。

为什么独立成文件 (而不是扩展 _common/figures.py)
-------------------------------------------------------
既有 ``_common/figures.py`` 只设置 matplotlib rcParams 和暴露色盲友好
调色板。在那里加绘图*函数*会混淆职责, 且对一个测试已稳定的文件侵入
更大。P3.1 刻意放在兄弟模块, 让既有 106 行的 `figures.py` 原封不动。

提供的图
--------------
1. ``coefplot_from_esttab_df(df, vars, models)``
   — 系数 ± 1.96·SE 图。Cao-2025 cutoff 灵敏度图 +
   strategic_diff N 灵敏度图都可归约为它。

2. ``forest_plot_from_esttab_df(df, var, models)``
   — 异质性森林图 (每行 = 一个子组 / spec, 带 SE 误差棒)。
   用于 SOE × paper 异质性图。

3. ``event_study_plot(periods, coefficients, ...)``
   — TWFE 动态事件研究图 (Sun-Abraham 2021)。bank_fintech_tone 在用;
   衍生论文可按需复用。

所有图:
- 默认后端: matplotlib 的 Agg (经 savefig.format 设置), 保证 headless
  CI 下测试可过。
- 默认风格: ``apply_publication_style`` (Times Roman, 9pt, 色盲友好)。
- 文件扩展名: .pdf (符合期刊惯例)。
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from news_process.papers._common.figures import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    FIGSIZE_WIDE,
    apply_publication_style,
)
from news_process.papers._common.stata_postprocess import Coefficient

# ============================================================================
# Helpers
# ============================================================================

def _ensure_matplotlib_agg():
    """headless 运行 (无 DISPLAY) 时强制 Agg 后端。"""
    import os

    import matplotlib
    if os.environ.get('DISPLAY') is None and os.name != 'nt':
        matplotlib.use('Agg', force=False)


def _to_value_se(cell) -> tuple[float, float | None]:
    """从 Coefficient 对象或数值标量中提取 (value, SE); None → (nan, None)。"""
    if cell is None:
        return float('nan'), None
    if isinstance(cell, Coefficient):
        return float(cell.value), (None if cell.se is None else float(cell.se))
    try:
        return float(cell), None
    except (TypeError, ValueError):
        return float('nan'), None


# ============================================================================
# 1. 系数图 Coefplot (输入 = esttab 解析后的 DataFrame)
# ============================================================================

def coefplot_from_esttab_df(df: pd.DataFrame,
                            variables: Sequence[str],
                            models: Sequence[str] | None = None,
                            *,
                            output_path: str | Path,
                            title: str = '',
                            xlabel: str = 'Coefficient',
                            ci_multiplier: float = 1.96,
                            figsize: tuple[float, float] = FIGSIZE_WIDE,
                            ) -> Path:
    """绘制系数图: 每个 (model, variable) 组合画一个点 + 95% 置信区间。

    布局: y 轴 = 变量 (自上而下), x 轴 = 系数值。
    多个模型以不同颜色并排展示。

    Args:
        df:              parse_esttab_csv 的输出。
        variables:       要绘制的变量行 (须在 df.index 中)。
        models:          列名; 默认取 df 的全部模型列。
        output_path:     .pdf 输出路径。
        title:           图标题。
        xlabel:          x 轴标签。
        ci_multiplier:   95% CI = 1.96·SE; 传 1.645 得 90% CI。
        figsize:         (宽, 高), 单位英寸。

    Returns:
        解析后的输出路径 (Path)。
    """
    _ensure_matplotlib_agg()
    import matplotlib.pyplot as plt

    apply_publication_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if models is None:
        models = list(df.columns)
    vars_present = [v for v in variables if v in df.index]
    if not vars_present:
        raise KeyError(f"None of variables {list(variables)} are in df.index "
                       f"(have: {list(df.index)[:10]}...)")

    fig, ax = plt.subplots(figsize=figsize)

    n_models = len(models)
    y_positions = list(range(len(vars_present)))
    offset_step = 0.18

    for m_idx, model in enumerate(models):
        offset = (m_idx - (n_models - 1) / 2) * offset_step
        coefs = []
        errs = []
        for v in vars_present:
            cell = df.loc[v, model]
            val, se = _to_value_se(cell)
            coefs.append(val)
            errs.append(0.0 if se is None else ci_multiplier * se)
        color = COLORBLIND_PALETTE[m_idx % len(COLORBLIND_PALETTE)]
        ys = [y + offset for y in y_positions]
        ax.errorbar(coefs, ys, xerr=errs, fmt='o', color=color,
                    label=model, capsize=2, markersize=4)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(vars_present)
    ax.invert_yaxis()
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    ax.legend(loc='best', frameon=False, fontsize=8)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return output_path


# ============================================================================
# 2. 森林图 Forest plot — 同一变量跨多个回归设定 (异质性分析)
# ============================================================================

def forest_plot_from_esttab_df(df: pd.DataFrame,
                               variable: str,
                               models: Sequence[str] | None = None,
                               *,
                               output_path: str | Path,
                               title: str = '',
                               xlabel: str = 'Effect size',
                               ci_multiplier: float = 1.96,
                               figsize: tuple[float, float] = FIGSIZE_SINGLE,
                               ) -> Path:
    """绘制森林图: 每个模型设定一行, 展示单一变量的系数 ± 置信区间。

    典型用途: 异质性表 (SOE / 非 SOE / OLS+交互 / 2SLS+交互 各行),
    比较同一 MAIN_DV-对-TONE_VAR 系数在不同设定下的大小。
    """
    _ensure_matplotlib_agg()
    import matplotlib.pyplot as plt

    apply_publication_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if models is None:
        models = list(df.columns)
    if variable not in df.index:
        raise KeyError(f"variable {variable!r} not in df.index")

    fig, ax = plt.subplots(figsize=figsize)
    coefs = []
    errs = []
    valid_models = []
    for m in models:
        cell = df.loc[variable, m]
        val, se = _to_value_se(cell)
        if val == val:  # not nan
            coefs.append(val)
            errs.append(0.0 if se is None else ci_multiplier * se)
            valid_models.append(m)

    y_positions = list(range(len(valid_models)))
    ax.errorbar(coefs, y_positions, xerr=errs, fmt='s',
                color=COLORBLIND_PALETTE[0], capsize=3, markersize=5)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(valid_models)
    ax.invert_yaxis()
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return output_path


# ============================================================================
# 3. 事件研究图 Event study (TWFE 动态系数)
# ============================================================================

def event_study_plot(periods: Sequence[int],
                     coefficients: Sequence[float],
                     standard_errors: Sequence[float] | None,
                     *,
                     output_path: str | Path,
                     title: str = '',
                     xlabel: str = 'Event time',
                     ylabel: str = 'Coefficient',
                     ci_multiplier: float = 1.96,
                     reference_period: int = -1,
                     figsize: tuple[float, float] = FIGSIZE_WIDE,
                     ) -> Path:
    """TWFE 动态事件研究图 (Sun-Abraham 2021 风格)。

    Args:
        periods:           事件时间整数序列, 如 [-3,-2,-1,0,1,2,3]。
        coefficients:      与 periods 一一对应的估计系数。
        standard_errors:   可选的对应标准误 (用于画 95% CI 误差条)。
        output_path:       PDF 输出路径。
        reference_period:  标记为省略基期的期数 (不画 CI), 默认 -1。
    """
    _ensure_matplotlib_agg()
    import matplotlib.pyplot as plt

    apply_publication_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if standard_errors is None:
        standard_errors = [0.0] * len(periods)

    fig, ax = plt.subplots(figsize=figsize)
    color = COLORBLIND_PALETTE[0]
    errs = [ci_multiplier * se if se else 0.0 for se in standard_errors]
    ax.errorbar(list(periods), list(coefficients), yerr=errs,
                fmt='o-', color=color, capsize=3, markersize=4)
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
    if reference_period in periods:
        ax.axvline(reference_period, color='red', linewidth=0.5,
                   linestyle=':', alpha=0.5, label=f'Reference t={reference_period}')
        ax.legend(loc='best', frameon=False, fontsize=8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return output_path


__all__ = [
    'coefplot_from_esttab_df',
    'forest_plot_from_esttab_df',
    'event_study_plot',
]
