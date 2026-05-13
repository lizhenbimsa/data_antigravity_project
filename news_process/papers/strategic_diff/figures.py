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


__all__ = ['plot_strategic_diff_n5_distribution']
