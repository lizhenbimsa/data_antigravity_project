"""news_process.papers._common.paper_figures_ext — Figure 2-4 generic helpers.

P3.1 (plan-r3 derivative-paper extension, 2026-05-15)

Generic publication-grade matplotlib figures consuming Stata esttab CSV output
(parsed via ``stata_postprocess.parse_esttab_csv``).

Why a separate file (not extending _common/figures.py)
-------------------------------------------------------
The existing ``_common/figures.py`` only sets matplotlib rcParams and exposes
the colorblind palette. Adding plotting *functions* there would mix concerns
and is more invasive to a file with stable tests. P3.1 deliberately ships in
a sibling module so the existing 106-line `figures.py` is untouched.

Provided plots
--------------
1. ``coefplot_from_esttab_df(df, vars, models)``
   — coefficient ± 1.96·SE plot. The Cao-2025 cutoff-sensitivity figure +
   strategic_diff N-sensitivity both reduce to this.

2. ``forest_plot_from_esttab_df(df, var, models)``
   — heterogeneity forest plot (each row = a sub-group / spec, with SE bars).
   Used for SOE × paper heterogeneity figures.

3. ``event_study_from_esttab_df(df, lead_lags)``
   — TWFE dynamic event-study plot (Sun-Abraham 2021). Bank-fintech-tone uses
   this; derivative papers can reuse where applicable.

All plots:
- Default backend: matplotlib's Agg (set via setting savefig.format) so tests
  pass under headless CI.
- Default style: ``apply_publication_style`` (Times Roman, 9pt, color-blind).
- File extension: .pdf (matches journal convention).
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
    """Force Agg backend if running headless (no DISPLAY)."""
    import os

    import matplotlib
    if os.environ.get('DISPLAY') is None and os.name != 'nt':
        matplotlib.use('Agg', force=False)


def _to_value_se(cell) -> tuple[float, float | None]:
    """Extract (value, SE) from a Coefficient or numeric scalar; None → (nan, None)."""
    if cell is None:
        return float('nan'), None
    if isinstance(cell, Coefficient):
        return float(cell.value), (None if cell.se is None else float(cell.se))
    try:
        return float(cell), None
    except (TypeError, ValueError):
        return float('nan'), None


# ============================================================================
# 1. Coefplot from esttab DataFrame
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
    """Render a coefficient plot: one point + 95% CI per (model, variable).

    Layout: y-axis = variables (top to bottom), x-axis = coefficient value.
    Multiple models shown side by side with different colors.

    Args:
        df:              Output of parse_esttab_csv.
        variables:       Variable rows to plot (in index of df).
        models:          Column names; defaults to all model columns of df.
        output_path:     .pdf file path.
        title:           Figure title.
        xlabel:          X-axis label.
        ci_multiplier:   95% CI = 1.96·SE; pass 1.645 for 90% CI.
        figsize:         (width, height) in inches.

    Returns:
        Resolved output path (Path).
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
# 2. Forest plot — single variable across multiple specs (heterogeneity)
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
    """Render a forest plot: one row per model spec, single variable's coef ± CI.

    Typical use: heterogeneity table (SOE / non-SOE / OLS+Int / 2SLS+Int rows)
    with the same MAIN_DV-on-TONE_VAR coefficient.
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
# 3. Event study (TWFE dynamic) plot
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
    """TWFE dynamic event-study plot (Sun-Abraham 2021 style).

    Args:
        periods:           Event-time integers, e.g. [-3,-2,-1,0,1,2,3].
        coefficients:      Estimated coefficients matched to periods.
        standard_errors:   Optional matched SEs (for 95% CI bars).
        output_path:       PDF target.
        reference_period:  Period to mark as omitted (no CI). Default -1.
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
