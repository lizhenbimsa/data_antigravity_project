"""news_process.papers.brokerage_network.figures — 信息经纪网络论文图表."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)


def plot_brokerage_centrality_distribution(paper_config: PaperConfig | None = None,
                                           *, filename: str = 'fig1_brokerage_centrality.pdf'
                                           ) -> Path:
    """绘制经纪中心性的 Bank-Year 分布。"""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('brokerage_network')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['brokerage_eigen_cent'])
    series = panel['brokerage_eigen_cent'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(np.log1p(series), bins=40, color=COLORBLIND_PALETTE[2],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(r'$\log(1 + \mathrm{brokerage\ eigenvector\ centrality})$')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank brokerage centrality')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_main_iv_coefplot(paper_config: PaperConfig | None = None,
                          *, filename: str = 'fig2_main_iv_coefplot.pdf') -> Path:
    """Figure 2: Network 2SLS main coefplot (Table 2 esttab)."""
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.brokerage_network.tables import build_table2_main

    pc = paper_config or get_paper_config('brokerage_network')
    df = build_table2_main(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return coefplot_from_esttab_df(
        df,
        variables=[v for v in ['peer_tone_lag1_full', 'L_btw', 'L_cons', 'L_broker']
                   if v in df.index],
        output_path=out,
        title='Network 2SLS Main Effects --- brokerage_network',
        xlabel='Coefficient (95% CI)',
    )


def plot_policy_centrality_forest(paper_config: PaperConfig | None = None,
                                  *, filename: str = 'fig3_policy_centrality_forest.pdf') -> Path:
    """Figure 3: DCEP/Sandbox × centrality forest (Table 3 esttab)."""
    from news_process.papers._common.paper_figures_ext import forest_plot_from_esttab_df
    from news_process.papers.brokerage_network.tables import build_table3_mechanism

    pc = paper_config or get_paper_config('brokerage_network')
    df = build_table3_mechanism(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    # Pick the first interaction variable present
    var = next((v for v in ['dcep_x_btw', 'dcep_x_cons', 'dcep_x_broker',
                            'sb_x_btw', 'sb_x_cons', 'sb_x_broker']
                if v in df.index), None)
    if var is None:
        raise KeyError("No recognized interaction variable in df.index")
    return forest_plot_from_esttab_df(
        df, variable=var, output_path=out,
        title=f'Policy × Centrality ({var}) --- brokerage_network',
    )


__all__ = [
    'plot_brokerage_centrality_distribution',
    'plot_main_iv_coefplot',
    'plot_policy_centrality_forest',
]
