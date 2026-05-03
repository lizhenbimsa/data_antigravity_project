"""news_process.papers.bank_fintech_tone.figures — 主线论文图表生成.

Phase 3c 交付物 (最小可用集)
---------------------------
- ``Figure 1: News Coverage Distribution`` — 银行年度新闻覆盖量分布。

后续 Phase 3 / 论文修订过程中按需扩展。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from news_process.papers._common import (
    PaperConfig,
    get_paper_config,
    load_panel,
    apply_publication_style,
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
)


def plot_news_coverage_distribution(paper_config: PaperConfig | None = None,
                                    *,
                                    filename: str = 'fig1_news_coverage.pdf'
                                    ) -> Path:
    """绘制银行年度新闻覆盖量直方图 (Bank-Year level).

    Args:
        paper_config:  可选 — 已实例化的 PaperConfig。
        filename:      输出文件名 (默认 PDF)。

    Returns:
        实际写入的图片绝对路径。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_tone')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel(
        '40_panel_yearly.parquet',
        paper_id=pc.paper_id,
        project_config=pc.config,
        columns=['n_articles'],
    )

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    coverage = panel['n_articles'].dropna()
    coverage = coverage[coverage > 0]

    ax.hist(np.log1p(coverage), bins=40, color=COLORBLIND_PALETTE[0],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(r'$\log(1 + \mathrm{news\ count})$')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank-year news coverage')

    out_path = pc.output_dir / filename
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


__all__ = ['plot_news_coverage_distribution']
