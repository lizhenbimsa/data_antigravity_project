"""news_process.papers.llm_peer.figures — LLM-Peer 论文图表."""

from __future__ import annotations

from pathlib import Path

from news_process.papers._common import (
    PaperConfig,
    get_paper_config,
    load_panel,
    apply_publication_style,
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
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
    ax.set_xlabel('TNIC similarity cutoff $c$')
    ax.set_ylabel(r'$\overline{\mathrm{LLM\ Peer\ Tone\ IV}}\ \pm\ \mathrm{SD}$')
    ax.set_title('LLM-Peer IV mean $\\pm$ SD by cutoff')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


__all__ = ['plot_cutoff_sensitivity']
