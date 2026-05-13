"""news_process.papers.benefit_society.figures — 经营效益态度论文图表.

Phase 3d 最小可用集: 占位 ``plot_benefit_distribution()``。
具体图表方案在论文修订过程中扩展。
"""

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


__all__ = ['plot_benefit_distribution']
