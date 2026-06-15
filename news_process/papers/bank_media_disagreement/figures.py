"""news_process.papers.bank_media_disagreement.figures — 第10篇图表 (provisional 2026-06-01).

Figure 1 (treatment 分布) 走 _common 通用绘图样式, 即开即用 (依赖 pipeline 产出 panel)。
event study / coefplot 待 M5 填实 (Cookson-Niessner 2020 JF media disagreement;
勘误: 旧注释误标 RFS, 实为 JF)。
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

# 三轨 full-parity (v3.9.0 三轨 ss): treatment 轨后缀 → 轴标签;
# 绘图按此顺序遍历, skip-if-missing — ss (银行+金科同句轨) 在 P4 付费 run 前
# 盘上无列, 自动跳过, 不再硬编码 _full 单轨。
_TREATMENT_BASE = 'cross_outlet_tone_variance'
_TRACKS: list[tuple[str, str]] = [
    ('_full', 'Full'),
    ('_ctx', 'Ctx'),
    ('_ss', 'SS (bank+fintech same-sentence)'),
]


def plot_disagreement_distribution(paper_config: PaperConfig | None = None,
                                   *, filename: str = 'fig1_disagreement_distribution.pdf'
                                   ) -> Path:
    """绘制 ``cross_outlet_tone_variance_{full,ctx,ss}`` 在 Bank-Year 维度的分布.

    三轨 (full/ctx/ss) 取**首个在面板中存在且非空**的轨道绘图; 各轨缺列或全 NaN
    则跳过 (skip-if-missing), 不再硬编码 _full 单轨。ss 轨在 P4 付费 run 前盘上缺,
    会被自动略过, 退回 ctx 或 full。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    # 不传 columns= 过滤: pd.read_parquet 对缺列会 raise, 而 ss 轨在 P4 付费 run 前
    # 盘上必缺 — 整盘加载后用 `col in panel.columns` 做 skip-if-missing 才安全。
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)

    series = None
    track_label = None
    for (suffix, label) in _TRACKS:
        col = f'{_TREATMENT_BASE}{suffix}'
        if col not in panel.columns:
            continue
        candidate = panel[col].dropna()
        if candidate.empty:
            continue
        series, track_label = candidate, label
        break

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    if series is None:
        # 三轨全缺/全 NaN (P4 付费 run 前可能如此): 出空图占位, 不崩 CLI
        ax.text(0.5, 0.5, 'No treatment track available\n(full / ctx / ss all missing)',
                ha='center', va='center', transform=ax.transAxes)
        track_label = 'N/A'
    else:
        ax.hist(series, bins=40, color=COLORBLIND_PALETTE[3],
                alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(f'Cross-Outlet Tone Variance ({track_label})')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Paper 10 Bank Media Disagreement — treatment distribution')
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
