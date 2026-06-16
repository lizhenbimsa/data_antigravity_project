"""news_process.papers.llm_peer.figures — LLM-Peer 论文图表."""

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


def plot_cutoff_sensitivity(paper_config: PaperConfig | None = None,
                            *, filename: str = 'fig1_cutoff_sensitivity.pdf'
                            ) -> Path:
    """绘制 LLM-Peer 多阈值 (cutoff∈{0.70, 0.75, 0.80, 0.85, 0.90}) 的均值-标准差敏感性曲线。"""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('llm_peer')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    cutoffs = (70, 75, 80, 85, 90)
    cols = [f'llm_peer_tone_iv_full_{c}' for c in cutoffs]
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config, columns=cols)

    means = [panel[c].mean() if c in panel.columns else float('nan')
             for c in cols]
    stds = [panel[c].std(ddof=1) if c in panel.columns else float('nan')
            for c in cols]

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    x = [c / 100 for c in cutoffs]
    ax.errorbar(x, means, yerr=stds, fmt='o-', color=COLORBLIND_PALETTE[3],
                ecolor=COLORBLIND_PALETTE[3], capsize=3, linewidth=1.0)
    # fix(omni-g-misc-02, 2026-06-11): 轴标签去 TNIC 误标 — 此 cutoff 是
    # difflib.get_close_matches 的字符串匹配严格度 (LLM 输出同行名 → 规范名归一),
    # 非 Hoberg-Phillips TNIC 同行语义相似度阈值 (口径勘误同 llm_peer_iv.py ~L912 命名勘误段);
    # 原标签直接印入出版图 fig1, 故须改。
    ax.set_xlabel('Peer name-matching cutoff $c$')
    ax.set_ylabel(r'$\overline{\mathrm{LLM\ Peer\ Tone\ IV}}\ \pm\ \mathrm{SD}$')
    ax.set_title('LLM-Peer IV mean $\\pm$ SD by cutoff')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_main_iv_coefplot(paper_config: PaperConfig | None = None,
                          *, filename: str = 'fig2_main_iv_coefplot.pdf'
                          ) -> Path:
    """Figure 2: 主回归 IV 2SLS 系数图 (读 Table 2 esttab CSV)."""
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.llm_peer.tables import build_table2_main

    pc = paper_config or get_paper_config('llm_peer')
    df = build_table2_main(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return coefplot_from_esttab_df(
        df,
        variables=[v for v in ['llm_vote_tone_full', 'peer_compete_idx',
                               'ln_news_coverage', 'media_hhi'] if v in df.index],
        output_path=out,
        title='Main IV 2SLS — llm_peer',
        xlabel='Coefficient (95% CI)',
    )


def plot_heterogeneity_forest(paper_config: PaperConfig | None = None,
                              *, filename: str = 'fig3_heterogeneity_forest.pdf'
                              ) -> Path:
    """Figure 3: 国企 (SOE) × LLM-Peer-IV 异质性森林图 (读 Table 4 esttab CSV)."""
    from news_process.papers._common.paper_figures_ext import forest_plot_from_esttab_df
    from news_process.papers.llm_peer.tables import build_table4_heterogeneity

    pc = paper_config or get_paper_config('llm_peer')
    df = build_table4_heterogeneity(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return forest_plot_from_esttab_df(
        df, variable='llm_vote_tone_full',
        output_path=out,
        title='Heterogeneity by SOE — llm_peer 2SLS',
        xlabel='Coefficient on llm_vote_tone_full (95% CI)',
    )


__all__ = [
    'plot_cutoff_sensitivity',
    'plot_main_iv_coefplot',
    'plot_heterogeneity_forest',
]
