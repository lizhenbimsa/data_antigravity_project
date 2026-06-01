"""news_process.papers.bank_media_disagreement.figures — 第10篇图表 (provisional 2026-06-01).

Figure 1 (treatment 分布) 走 _common 通用绘图样式, 即开即用 (依赖 pipeline 产出 panel)。
event study / coefplot 待 M5 填实 (Cookson-Niessner 2020 RFS media disagreement)。
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

PAPER_ID = 'bank_media_disagreement'


def plot_disagreement_distribution(paper_config: PaperConfig | None = None,
                                   *, filename: str = 'fig1_disagreement_distribution.pdf'
                                   ) -> Path:
    """绘制 ``cross_outlet_tone_variance_full`` 在 Bank-Year 维度的分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['cross_outlet_tone_variance_full'])
    series = panel['cross_outlet_tone_variance_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[3],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Cross-Outlet Tone Variance (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Paper 10 Bank Media Disagreement — treatment distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
