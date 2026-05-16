"""news_process.papers.bank_fintech_attention.figures — P2 论文图表.

Figure layout (per plan §5.8.2):
    Figure 1: attention_index_full bank-year distribution
    Figure 2: event study coefplot (E1/E2/E4/E5a/E5b)
    Figure 3: time trend by 4 bank types × fintech wave segments
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


def plot_attention_distribution(paper_config: PaperConfig | None = None,
                                *, filename: str = 'fig1_attention_distribution.pdf'
                                ) -> Path:
    """绘制 ``attention_index_full`` 在 Bank-Year 维度的分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_attention')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['attention_index_full'])
    series = panel['attention_index_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Fintech Attention Index (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('P2 Bank Fintech Attention — distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
