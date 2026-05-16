"""news_process.papers.bank_fintech_substance.figures — P3 论文图表."""

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


def plot_substantiveness_distribution(paper_config: PaperConfig | None = None,
                                      *, filename: str = 'fig1_substantiveness_distribution.pdf'
                                      ) -> Path:
    """绘制 ``innovation_substantiveness_full`` 在 Bank-Year 维度的分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_substance')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['innovation_substantiveness_full'])
    series = panel['innovation_substantiveness_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[2],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Innovation Substantiveness (Full track)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('P3 Bank Fintech Substance — distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
