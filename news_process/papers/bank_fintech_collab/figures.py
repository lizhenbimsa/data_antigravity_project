"""news_process.papers.bank_fintech_collab.figures — P5 论文图表 (provisional 2026-06-01).

Figure 1 (treatment 分布) 走 _common 通用绘图样式, 即开即用 (依赖 pipeline 产出 panel)。
event study / coefplot / time trend 待 M5/M6 填实
(Chesbrough 2003 Open Innovation; Laursen & Salter 2006 SMJ 27:131-150)。
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

PAPER_ID = 'bank_fintech_collab'


def plot_collab_mode_distribution(paper_config: PaperConfig | None = None,
                                  *, filename: str = 'fig1_collab_mode_distribution.pdf'
                                  ) -> Path:
    """绘制 ``innovation_collab_mode_full`` 在 Bank-Year 维度的分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['innovation_collab_mode_full'])
    series = panel['innovation_collab_mode_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[2],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Fintech Collaboration Mode (Full; 外部协同 ← → 自主研发)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('P5 Bank Fintech Collab — treatment distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
