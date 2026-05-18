"""news_process.papers.benefit_society.figures — 经营效益态度论文图表.

Phase 3d 最小可用集: 占位 ``plot_benefit_distribution()``。
具体图表方案在论文修订过程中扩展。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)


def plot_benefit_distribution(paper_config: PaperConfig | None = None,
                              *, filename: str = 'fig1_benefit_distribution.pdf'
                              ) -> Path:
    """绘制 ``benefit_mean_full`` 在 Bank-Year 维度的分布。"""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['benefit_mean_full'])
    series = panel['benefit_mean_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Benefit-Operations Attitude Mean (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank-year benefit attitude')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_main_coefplot(paper_config: PaperConfig | None = None,
                       *, filename: str = 'fig2_main_coefplot.pdf') -> Path:
    """Figure 2: main effects coefplot (Table 2 esttab)."""
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.benefit_society.tables import build_table2_main

    pc = paper_config or get_paper_config('benefit_society')
    df = build_table2_main(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return coefplot_from_esttab_df(
        df,
        variables=[v for v in ['benefit_mean_full', 'article_sim_mean',
                               'fintech_intensity_mean'] if v in df.index],
        output_path=out,
        title='Main Effects — benefit_society',
        xlabel='Coefficient (95% CI)',
    )


def plot_mechanism_forest(paper_config: PaperConfig | None = None,
                          *, filename: str = 'fig3_mechanism_forest.pdf') -> Path:
    """Figure 3: Token/Hidden/Subst mechanism forest (Table 3 esttab)."""
    from news_process.papers._common.paper_figures_ext import forest_plot_from_esttab_df
    from news_process.papers.benefit_society.tables import build_table3_mechanism

    pc = paper_config or get_paper_config('benefit_society')
    df = build_table3_mechanism(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    # Pick whichever mechanism variable is present in row index
    var = next((v for v in ['token_adopt_kw_p50', 'hidden_adopt_kw_p50',
                            'subst_adopt_kw_p50', 'benefit_mean_full']
                if v in df.index), None)
    if var is None:
        raise KeyError("No recognized mechanism variable in df.index")
    return forest_plot_from_esttab_df(
        df, variable=var, output_path=out,
        title='Mechanism: Token / Hidden / Subst — benefit_society',
    )


def plot_benefit_distribution_with_subsampling_ci(
    paper_config: PaperConfig | None = None,
    *,
    filename: str = 'fig1_benefit_distribution_with_ci.pdf',
    block_size: int = 2,
    n_subsamples: int = 1000,
    seed: int = 42,
) -> Path:
    """Figure 1 with Politis-Romano block-subsampling 95% CI overlay (C1).

    V2.0 J-L-M 2026 plan §3 P3.1: replicates J-L-M Figure 2 caption methodology
    ("Bands represent 95% confidence intervals produced by subsampling").
    Article-level block-subsampling preserves within-block dependence.
    """
    import matplotlib.pyplot as plt

    from news_process.papers._common.stats_helpers import block_subsampling_ci

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['benefit_mean_full'])
    series = panel['benefit_mean_full'].dropna().values
    mean, lo, hi = block_subsampling_ci(
        series, block_size=block_size, n_subsamples=n_subsamples, seed=seed,
    )

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.axvline(mean, color=COLORBLIND_PALETTE[3], linestyle='-', linewidth=1.5,
               label=f'Mean = {mean:.3f}')
    ax.axvspan(lo, hi, color=COLORBLIND_PALETTE[3], alpha=0.15,
               label=f'95% subsampling CI = [{lo:.3f}, {hi:.3f}]')
    ax.set_xlabel('Benefit-Operations Attitude Mean (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution with Politis-Romano subsampling 95% CI')
    ax.legend(loc='best', fontsize=8, frameon=False)

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_placebo_comparison(
    paper_config: PaperConfig | None = None,
    *,
    filename: str = 'figA2_placebo_comparison.pdf',
) -> Path:
    """Figure A2: Placebo β bar chart vs main β (S1 visual evidence).

    Per V2.0 plan §3 P3.3: 5 placebo β + 1 main β bar chart, each annotated
    with |β_placebo / β_main| ratio. Acceptance (AC-S1) visual check:
    placebo bars should be ≤30% of main bar height.
    """
    import matplotlib.pyplot as plt

    from news_process.papers.benefit_society.tables import build_table_a10_placebo

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = build_table_a10_placebo(pc)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Placebo table CSV missing (run Stata 23_tableA10_*.do first): {e}"
        ) from e

    # Pick first coefficient row (typically the projected mean variable)
    coef_row = df.iloc[0] if len(df) > 0 else None
    if coef_row is None:
        raise ValueError("Placebo CSV empty")

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    cols = list(coef_row.index)
    values = [float(coef_row[c]) if pd.notna(coef_row[c]) else 0.0 for c in cols]
    colors = [COLORBLIND_PALETTE[0]] + [COLORBLIND_PALETTE[2]] * (len(cols) - 1)

    ax.bar(range(len(cols)), values, color=colors, alpha=0.85,
           edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=30, ha='right', fontsize=8)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_ylabel('β coefficient')
    ax.set_title('Placebo vs Main: business-line robustness (S1, J-L-M §4.2)')

    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


__all__ = [
    'plot_benefit_distribution',
    'plot_main_coefplot',
    'plot_mechanism_forest',
    # V2.0 J-L-M alignment (Round 9)
    'plot_benefit_distribution_with_subsampling_ci',
    'plot_placebo_comparison',
]
