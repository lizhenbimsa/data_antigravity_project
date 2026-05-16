"""news_process.papers.bank_fintech_locus.figures — P4 论文图表."""

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


def plot_locus_distribution(paper_config: PaperConfig | None = None,
                            *, filename: str = 'fig1_locus_distribution.pdf'
                            ) -> Path:
    """绘制 ``locus_layer_full`` / ``locus_scenario_full`` 双柱分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_locus')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['locus_layer_full', 'locus_scenario_full'])

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    counts = [int(panel['locus_layer_full'].sum()),
              int(panel['locus_scenario_full'].sum())]
    ax.bar(['Layer (底层)', 'Scenario (应用)'], counts,
           color=[COLORBLIND_PALETTE[0], COLORBLIND_PALETTE[3]],
           alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_ylabel('Bank-Year count')
    ax.set_title('P4 Bank Fintech Locus — layer vs scenario')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
