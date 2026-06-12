"""news_process.papers.bank_fintech_collab.figures — P5 论文图表 (provisional 2026-06-01).

Figure 1 (treatment 分布) 走 _common 通用绘图样式 (依赖 pipeline 产出 panel)。
event study / coefplot / time trend 待 M5/M6 填实
(Chesbrough 2003 Open Innovation; Laursen & Salter 2006 SMJ 27:131-150)。

缺列防护 (fix(omni-g-papers-misc-02, 2026-06-11), 扩散 attention-01 修复):
    旧版直接 ``load_panel(columns=['innovation_collab_mode_full'])`` — 该列是
    **文章级**中文分类字符串 (自主研发/外部协同), 永远不会以该名出现在
    bank-year panel, pyarrow 抛 ``ArrowInvalid`` 逃逸窄 except → CLI 崩溃。
    现 (a) 改读 panel 真实物化的 bank-year 编码 ``collab_frac`` (full 轨) /
    ``collab_frac_cm`` (ctx 轨); (b) ``pq.read_schema`` 先探测列存在性,
    候选列全缺时出占位图 + logger.warning (优雅降级, 不抛)。
"""

from __future__ import annotations

import logging
from pathlib import Path

import pyarrow.parquet as pq

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)

PAPER_ID = 'bank_fintech_collab'

_LOGGER = logging.getLogger('papers.bank_fintech_collab.figures')

# 外部协同占比列优先级: collab_frac (full 轨, panel 真实物化) → collab_frac_cm (ctx 轨)。
# 注意: 旧设计列 innovation_collab_mode_full 是文章级字符串, 不入候选。
_COLLAB_COL_PREFERENCE: list[str] = ['collab_frac', 'collab_frac_cm']


def _placeholder_figure(out_path: Path, title: str, missing: list[str]) -> Path:
    """候选列全缺时的占位图 (优雅降级, 扩散 attention-01 模式)."""
    import matplotlib.pyplot as plt

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.text(0.5, 0.5,
            f'PLACEHOLDER — panel columns not materialized:\n{missing}',
            ha='center', va='center', fontsize=8, color='dimgray', wrap=True)
    ax.set_axis_off()
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def plot_collab_mode_distribution(paper_config: PaperConfig | None = None,
                                  *, filename: str = 'fig1_collab_mode_distribution.pdf'
                                  ) -> Path | None:
    """绘制外部协同新闻占比 ``collab_frac`` 在 Bank-Year 维度的分布.

    fix(omni-g-papers-misc-02/-11, 2026-06-11): 读 panel 真实列 collab_frac/
    collab_frac_cm (旧 innovation_collab_mode_full 为面板幻影列); 缺列时
    出占位图 + WARN, 面板文件缺失时返回 None。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config(PAPER_ID)
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = pc.output_dir / filename

    panel_path = pc.panel_path('40_panel_yearly.parquet')
    if not panel_path.exists():
        _LOGGER.warning("面板文件不存在 (%s); 跳过 P5 分布图", panel_path)
        return None
    try:
        available = set(pq.read_schema(panel_path).names)
    except Exception as exc:  # noqa: BLE001 — 读 schema 失败一律降级
        _LOGGER.warning("读取面板 schema 失败 (%s): %s; 跳过 P5 分布图",
                        panel_path, exc)
        return None
    col = next((c for c in _COLLAB_COL_PREFERENCE if c in available), None)
    if col is None:
        _LOGGER.warning("面板缺外部协同占比候选列 %s; 出占位图 (优雅降级)",
                        _COLLAB_COL_PREFERENCE)
        return _placeholder_figure(
            out_path, 'P5 Bank Fintech Collab — treatment distribution (placeholder)',
            _COLLAB_COL_PREFERENCE)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config, columns=[col])
    series = panel[col].dropna()
    if series.empty:
        _LOGGER.warning("外部协同占比列 '%s' 全为空; 出占位图", col)
        return _placeholder_figure(
            out_path, 'P5 Bank Fintech Collab — treatment distribution (placeholder)',
            [col])

    track = 'Full track' if col == 'collab_frac' else 'Context track'
    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[2],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(f'Frac of External-Collab Fintech News ({track}, {col}; '
                  '自主研发 0 ← → 1 外部协同)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('P5 Bank Fintech Collab — treatment distribution')
    fig.tight_layout()

    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
