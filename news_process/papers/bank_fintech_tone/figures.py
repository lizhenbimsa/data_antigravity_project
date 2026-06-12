"""news_process.papers.bank_fintech_tone.figures — 主线论文图表生成.

Phase 3c 交付物 (最小可用集)
---------------------------
- ``Figure 1: News Coverage Distribution`` — 银行年度新闻覆盖量分布。

后续 Phase 3 / 论文修订过程中按需扩展。
"""

from __future__ import annotations

import logging
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


def plot_news_coverage_distribution(paper_config: PaperConfig | None = None,
                                    *,
                                    filename: str = 'fig1_news_coverage.pdf'
                                    ) -> Path:
    """绘制银行年度新闻覆盖量直方图 (Bank-Year level).

    披露 (fix(omni-g-papers-misc-04, 2026-06-11)): 本图**有条件于 coverage>0**
    — 零覆盖 bank-year (盘上 ~32%) 被剔除后才取 log1p; 标题/图注现明示
    "conditional on >=1 article" 并报告被剔除的零覆盖行数 (旧版静默截除,
    且 log1p 变换本可原生保留 0, 读者会误以为分布含零覆盖行)。

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
    # fix(omni-g-papers-misc-04, 2026-06-11): 剔除零覆盖行的行为保留 (条件分布),
    # 但不再静默 — 计数并在标题/图注/日志中显式披露。
    n_zero = int((coverage == 0).sum())
    coverage = coverage[coverage > 0]
    if n_zero:
        logging.getLogger('papers.bank_fintech_tone.figures').warning(
            "Figure 1: %d 个零覆盖 bank-year 被剔除 (conditional on >=1 article; "
            "已在图注披露)", n_zero)

    ax.hist(np.log1p(coverage), bins=40, color=COLORBLIND_PALETTE[0],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(r'$\log(1 + \mathrm{news\ count})$, conditional on $\geq 1$ article')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank-year news coverage\n'
                 r'(conditional on $\geq$1 article)')
    ax.annotate(f'Excluded: {n_zero} zero-coverage bank-years',
                xy=(0.98, 0.95), xycoords='axes fraction',
                ha='right', va='top', fontsize=7, color='dimgray')

    out_path = pc.output_dir / filename
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


__all__ = ['plot_news_coverage_distribution']
