"""news_process.papers.bank_fintech_locus.figures — P4 论文图表.

缺列防护 (fix(omni-g-papers-misc-02, 2026-06-11), 扩散 attention-01 修复):
    旧版直接 ``load_panel(columns=['locus_layer_full', 'locus_scenario_full'])``
    — 这两列仅在 Stata ``01_data_prep.do`` 内由面板列 tech_frac/app_frac 临时
    gen, 从不落 parquet, pyarrow 抛 ``ArrowInvalid`` 逃逸窄 except → CLI 崩溃。
    现 (a) 改读 panel 真实物化列 ``tech_frac``/``app_frac``, 并按 01_data_prep
    同式 (主导类别二元化: tech_frac > app_frac → layer-focused) 在 pandas 侧
    复推 layer/scenario 计数; (b) ``pq.read_schema`` 探测 + 缺列占位图 + WARN。
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

_LOGGER = logging.getLogger('papers.bank_fintech_locus.figures')

# locus 占比源列 (panel 真实物化; 与 Stata 01_data_prep.do.tmpl:41-43 同源)
_LOCUS_SOURCE_COLS: list[str] = ['tech_frac', 'app_frac']


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


def plot_locus_distribution(paper_config: PaperConfig | None = None,
                            *, filename: str = 'fig1_locus_distribution.pdf'
                            ) -> Path | None:
    """绘制 layer-focused vs scenario-focused 的 bank-year 主导类别双柱分布.

    fix(omni-g-papers-misc-02/-11, 2026-06-11): 由 panel 真实列 tech_frac/
    app_frac 按 01_data_prep 同式推导 (tech_frac > app_frac → layer-focused;
    平票/缺失不计入任一柱); 缺列时出占位图 + WARN, 面板缺失时返回 None。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_locus')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = pc.output_dir / filename

    panel_path = pc.panel_path('40_panel_yearly.parquet')
    if not panel_path.exists():
        _LOGGER.warning("面板文件不存在 (%s); 跳过 P4 分布图", panel_path)
        return None
    try:
        available = set(pq.read_schema(panel_path).names)
    except Exception as exc:  # noqa: BLE001 — 读 schema 失败一律降级
        _LOGGER.warning("读取面板 schema 失败 (%s): %s; 跳过 P4 分布图",
                        panel_path, exc)
        return None
    missing = [c for c in _LOCUS_SOURCE_COLS if c not in available]
    if missing:
        _LOGGER.warning("面板缺 locus 占比源列 %s; 出占位图 (优雅降级)", missing)
        return _placeholder_figure(
            out_path, 'P4 Bank Fintech Locus — layer vs scenario (placeholder)',
            missing)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config, columns=_LOCUS_SOURCE_COLS)
    valid = panel.dropna(subset=_LOCUS_SOURCE_COLS)
    # 主导类别二元化 (镜像 Stata 01_data_prep.do.tmpl:41-43; 平票两者皆否)
    n_layer = int((valid['tech_frac'] > valid['app_frac']).sum())
    n_scenario = int((valid['app_frac'] > valid['tech_frac']).sum())
    if n_layer + n_scenario == 0:
        _LOGGER.warning("tech_frac/app_frac 无任何非平票有效观测; 出占位图")
        return _placeholder_figure(
            out_path, 'P4 Bank Fintech Locus — layer vs scenario (placeholder)',
            _LOCUS_SOURCE_COLS)

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.bar(['Layer (底层)', 'Scenario (应用)'], [n_layer, n_scenario],
           color=[COLORBLIND_PALETTE[0], COLORBLIND_PALETTE[3]],
           alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_ylabel('Bank-Year count (dominant category)')
    ax.set_title('P4 Bank Fintech Locus — layer vs scenario')
    fig.tight_layout()

    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
