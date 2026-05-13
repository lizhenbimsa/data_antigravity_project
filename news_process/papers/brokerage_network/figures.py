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


__all__ = ['plot_brokerage_centrality_distribution']
