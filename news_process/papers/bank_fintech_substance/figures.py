"""news_process.papers.bank_fintech_substance.figures — P3 论文图表.

缺列防护 (fix(omni-g-papers-misc-02, 2026-06-11), 扩散 attention-01 修复):
    旧版直接 ``load_panel(columns=['innovation_substantiveness_full'])`` — 该列
    是**文章级**中文分类字符串 (实质性/象征性), 永远不会以该名出现在 bank-year
    panel, pyarrow 抛 ``ArrowInvalid`` 逃逸 analysis.py 的窄 except → CLI 整体
    崩溃。现 (a) 改读 panel 真实物化的 bank-year 编码 ``sub_frac`` (full 轨) /
    ``sub_frac_sc`` (ctx 轨); (b) ``pq.read_schema`` 先探测列存在性, 候选列
    全缺时出占位图 + logger.warning (优雅降级, 不抛)。
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

_LOGGER = logging.getLogger('papers.bank_fintech_substance.figures')

# 实质性占比列优先级: sub_frac (full 轨, panel 真实物化) → sub_frac_sc (ctx 轨)。
# 注意: 旧设计列 innovation_substantiveness_full 是文章级字符串, 不入候选。
_SUBST_COL_PREFERENCE: list[str] = ['sub_frac', 'sub_frac_sc']


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


def plot_substantiveness_distribution(paper_config: PaperConfig | None = None,
                                      *, filename: str = 'fig1_substantiveness_distribution.pdf'
                                      ) -> Path | None:
    """绘制实质性新闻占比 ``sub_frac`` 在 Bank-Year 维度的分布.

    fix(omni-g-papers-misc-02/-11, 2026-06-11): 读 panel 真实列 sub_frac/
    sub_frac_sc (旧 innovation_substantiveness_full 为面板幻影列); 缺列时
    出占位图 + WARN, 面板文件缺失时返回 None。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_substance')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = pc.output_dir / filename

    panel_path = pc.panel_path('40_panel_yearly.parquet')
    if not panel_path.exists():
        _LOGGER.warning("面板文件不存在 (%s); 跳过 P3 分布图", panel_path)
        return None
    try:
        available = set(pq.read_schema(panel_path).names)
    except Exception as exc:  # noqa: BLE001 — 读 schema 失败一律降级
        _LOGGER.warning("读取面板 schema 失败 (%s): %s; 跳过 P3 分布图",
                        panel_path, exc)
        return None
    col = next((c for c in _SUBST_COL_PREFERENCE if c in available), None)
    if col is None:
        _LOGGER.warning("面板缺实质性占比候选列 %s; 出占位图 (优雅降级)",
                        _SUBST_COL_PREFERENCE)
        return _placeholder_figure(
            out_path, 'P3 Bank Fintech Substance — distribution (placeholder)',
            _SUBST_COL_PREFERENCE)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config, columns=[col])
    series = panel[col].dropna()
    if series.empty:
        _LOGGER.warning("实质性占比列 '%s' 全为空; 出占位图", col)
        return _placeholder_figure(
            out_path, 'P3 Bank Fintech Substance — distribution (placeholder)',
            [col])

    track = 'Full track' if col == 'sub_frac' else 'Context track'
    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[2],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(f'Frac of Substantive Fintech News ({track}, {col})')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('P3 Bank Fintech Substance — distribution')
    fig.tight_layout()

    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
