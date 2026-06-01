"""news_process.papers.bank_news_clarity.figures — 第11篇图表 (provisional 2026-06-01).

Figure 1 (treatment 分布) 走 _common 通用绘图样式, 即开即用 (依赖 pipeline 产出 panel)。
event study / coefplot 待 M7 填实 (Bushman-Williams 2012 JAE external info environment)。
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

PAPER_ID = 'bank_news_clarity'


def plot_clarity_distribution(paper_config: PaperConfig | None = None,
                              *, filename: str = 'fig1_clarity_distribution.pdf'
                              ) -> Path:
    """绘制 ``mean_clarity_score_ctx`` 在 Bank-Year 维度的分布."""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['mean_clarity_score_ctx'])
    series = panel['mean_clarity_score_ctx'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[4],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Mean News Clarity Score (Ctx)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Paper 11 Bank News Clarity — treatment distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
