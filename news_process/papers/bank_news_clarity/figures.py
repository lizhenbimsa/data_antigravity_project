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


# 三轨 clarity treatment (full=正文全文 / ctx=实体窗口 / ss=银行+金科同句共现, v3.9.0)。
# 互为稳健性; 逐轨叠画分布, 缺列 (如 ss 在 P4 付费 run 落盘前) skip-if-missing,
# 不再硬编码单一 _ctx 轨, 防 ss/full 列缺失时 KeyError 崩图。
_CLARITY_TRACKS: list[tuple[str, str]] = [
    ('mean_clarity_score_full', 'Full'),
    ('mean_clarity_score_ctx', 'Ctx'),
    ('mean_clarity_score_ss', 'SS'),
]


def plot_clarity_distribution(paper_config: PaperConfig | None = None,
                              *, filename: str = 'fig1_clarity_distribution.pdf'
                              ) -> Path:
    """绘制三轨 ``mean_clarity_score_{full,ctx,ss}`` 在 Bank-Year 维度的分布.

    逐轨遍历 ``_CLARITY_TRACKS``, 列不在面板 / 全 NaN 时跳过该轨 (skip-if-missing),
    保证 ss 列在 P4 付费 run 落盘前缺失时本图仍能生成 (退化为现存轨)。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=[col for col, _ in _CLARITY_TRACKS])

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    drawn = 0
    for idx, (col, label) in enumerate(_CLARITY_TRACKS):
        if col not in panel.columns:
            continue
        series = panel[col].dropna()
        if series.empty:
            continue
        ax.hist(series, bins=40,
                color=COLORBLIND_PALETTE[idx % len(COLORBLIND_PALETTE)],
                alpha=0.55, edgecolor='white', linewidth=0.4, label=label)
        drawn += 1
    if drawn > 1:
        ax.legend(title='Track', frameon=False)
    ax.set_xlabel('Mean News Clarity Score (full / ctx / ss)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Paper 11 Bank News Clarity — treatment distribution (三轨)')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
