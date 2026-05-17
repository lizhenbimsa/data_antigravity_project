"""news_process.papers.bank_fintech_collab.figures — P5 论文图表 (v3.4.0 占位).

M5/M6 阶段填实主回归 event study / coefplot / time trend. 本 PR 仅占位.

学术锚点: Chesbrough (2003) Open Innovation; Laursen & Salter (2006 SMJ 27:131-150).
"""

from __future__ import annotations

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)

PAPER_ID = 'bank_fintech_collab'


def main() -> None:
    """P5 figures entry-point (M5/M6 阶段实现; 本 PR 仅占位骨架)."""
    cfg: PaperConfig = get_paper_config(PAPER_ID)
    apply_publication_style()
    # 占位: M5 阶段填实 event study (E1/E3/E4 collab_mode treatment) +
    # coefplot (M1-M6 主回归系数) + collab_mode time trend (2007-2024).
    _ = (cfg, COLORBLIND_PALETTE, FIGSIZE_SINGLE, load_panel)
    print(f'[{PAPER_ID}] figures.py placeholder — 实施延后到 M5/M6.')


if __name__ == '__main__':
    main()
