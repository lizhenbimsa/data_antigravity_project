"""news_process.papers.strategic_diff.figures — 战略差异度论文图表."""

from __future__ import annotations

from pathlib import Path

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)


def plot_strategic_diff_n5_distribution(paper_config: PaperConfig | None = None,
                                        *, filename: str = 'fig1_strat_diff_n5.pdf'
                                        ) -> Path:
    """绘制 N=5 战略差异度的 Bank-Year 分布。"""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('strategic_diff')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['strat_diff_n5'])
    series = panel['strat_diff_n5'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[5],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Strategic Differentiation (N=5, TF-IDF char)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank strategic differentiation')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_main_coefplot(paper_config: PaperConfig | None = None,
                       *, filename: str = 'fig2_main_coefplot.pdf') -> Path:
    """Figure 2: 战略差异度主效应系数图 (读 Table 2 esttab CSV)."""
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.strategic_diff.tables import build_table2_main

    pc = paper_config or get_paper_config('strategic_diff')
    df = build_table2_main(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return coefplot_from_esttab_df(
        df,
        variables=[v for v in ['strat_diff_n5', 'strat_fluidity', 'strat_sim_max',
                               'llm_vote_tone_full', 'coh_tfidf_c_full']
                   if v in df.index],
        output_path=out,
        title='Main Effects --- strategic_diff',
        xlabel='Coefficient (95% CI)',
    )


def plot_n_sensitivity_coefplot(paper_config: PaperConfig | None = None,
                                *, filename: str = 'fig3_n_sensitivity_coefplot.pdf') -> Path:
    """Figure 3: 邻居数敏感性系数图 N∈{3,4,5,6,7,10,20,30,40,50} (读 Table 5a esttab CSV).

    fix(topk-n-expansion, 2026-07-02): 纳入大邻域 N∈{10,20,30,40,50} (与 n3..n7 互为稳健性)。
    """
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.strategic_diff.tables import build_table5_robustness

    pc = paper_config or get_paper_config('strategic_diff')
    df = build_table5_robustness(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    _n_grid = [3, 4, 5, 6, 7, 10, 20, 30, 40, 50]
    vars_present = [f'strat_diff_n{n}' for n in _n_grid
                    if f'strat_diff_n{n}' in df.index]
    if not vars_present:
        raise KeyError("No strat_diff_n{3..7,10,20,30,40,50} found in df.index")
    return coefplot_from_esttab_df(
        df, variables=vars_present, output_path=out,
        title='N-Neighbor Sensitivity --- strategic_diff (Bresnahan-Reiss 1991)',
        xlabel='Coefficient (95% CI)',
    )


__all__ = [
    'plot_strategic_diff_n5_distribution',
    'plot_main_coefplot',
    'plot_n_sensitivity_coefplot',
]
