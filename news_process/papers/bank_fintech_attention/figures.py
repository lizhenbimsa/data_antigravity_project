"""news_process.papers.bank_fintech_attention.figures — P2 论文图表.

Figure layout (per plan §5.8.2):
    Figure 1: attention intensity bank-year distribution
    Figure 2: event study coefplot (E1/E2/E4/E5a/E5b)
    Figure 3: time trend by 4 bank types × fintech wave segments

缺列防护 (metric-audit 2026-06-02 attention_media-01):
    plan §5.8.2 起草时假设面板含 ``attention_index_full`` 处理列, 但该列
    **从未在任何 stage 物化** (全仓零产出)。直接 ``load_panel(columns=[...])``
    会触发 pyarrow ``ArrowInvalid`` (而非 ``FileNotFoundError``), analysis.py
    的 ``except FileNotFoundError`` 接不住 → CLI 退出码 1 + traceback。
    本模块改为: 先探测面板实际列, 缺 ``attention_index_*`` 时回退到真实存在、
    语义最接近 Hassan 2019 QJE attention intensity 的 ``avg_ft_intensity_*``
    (stage 14_fintech_intensity → panel aggregate), 并在图标题/轴标签注明
    "(proxied by avg_ft_intensity)"; 候选列全缺时 logger.warning + 优雅返回
    ``None`` (不抛)。
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

_LOGGER = logging.getLogger('papers.bank_fintech_attention.figures')

# 注意力强度处理列优先级 (从理想 → 可得 fallback)。
# attention_index_* 是 plan §5.8.2 设计列但从未物化; avg_ft_intensity_* 为
# stage 14 fintech_intensity 的 bank-year 均值, 是当前面板真实可得、最贴近
# Hassan 2019 QJE attention intensity 的代理 (实测 full/ctx 各 119 非空)。
_ATTENTION_COL_PREFERENCE: list[str] = [
    'attention_index_full',
    'attention_index_ctx',
    'avg_ft_intensity_full',
    'avg_ft_intensity_ctx',
]

# 回退列 (非设计列) 在图上标注代理来源, 避免读者误判为已物化的 attention_index。
_PROXY_COLS: frozenset[str] = frozenset({
    'avg_ft_intensity_full', 'avg_ft_intensity_ctx',
})


def _panel_path(pc: PaperConfig) -> Path:
    """返回 40_panel_yearly.parquet 绝对路径 (与 load_panel 同源解析)."""
    return pc.panel_path('40_panel_yearly.parquet')


def _resolve_attention_column(pc: PaperConfig) -> str | None:
    """探测面板列, 按偏好顺序选出第一个真实存在的注意力强度列.

    缺文件或候选列全缺 → 返回 None (调用方负责 graceful skip)。
    """
    path = _panel_path(pc)
    if not path.exists():
        _LOGGER.warning("面板文件不存在 (%s); 跳过注意力分布图", path)
        return None
    try:
        available = set(pq.read_schema(path).names)
    except Exception as exc:  # noqa: BLE001 — 读 schema 失败一律降级为优雅 skip
        _LOGGER.warning("读取面板 schema 失败 (%s): %s; 跳过注意力分布图", path, exc)
        return None
    for col in _ATTENTION_COL_PREFERENCE:
        if col in available:
            if col in _PROXY_COLS:
                _LOGGER.warning(
                    "attention_index_* 列未物化; 回退到代理列 '%s' "
                    "(图上标注 'proxied by avg_ft_intensity')", col)
            return col
    _LOGGER.warning(
        "面板缺所有注意力强度候选列 %s; 跳过注意力分布图",
        _ATTENTION_COL_PREFERENCE)
    return None


def plot_attention_distribution(paper_config: PaperConfig | None = None,
                                *, filename: str = 'fig1_attention_distribution.pdf'
                                ) -> Path | None:
    """绘制 fintech 注意力强度在 Bank-Year 维度的分布.

    优先用设计列 ``attention_index_full/ctx``; 未物化时回退到代理列
    ``avg_ft_intensity_full/ctx`` (Hassan 2019 QJE attention intensity 近似)。
    候选列全缺或面板缺失 → logger.warning + 返回 None (不抛)。
    """
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('bank_fintech_attention')

    col = _resolve_attention_column(pc)
    if col is None:
        return None

    is_proxy = col in _PROXY_COLS
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=[col])
    series = panel[col].dropna()
    if series.empty:
        _LOGGER.warning("注意力强度列 '%s' 全为空; 跳过分布图", col)
        return None

    # 标题/轴标签: 代理列显式注明来源, 设计列照常。
    track = 'Full' if col.endswith('_full') else 'Context'
    if is_proxy:
        xlabel = f'Fintech Attention Intensity ({track}, proxied by avg_ft_intensity)'
        title = ('P2 Bank Fintech Attention — distribution '
                 '(proxied by avg_ft_intensity)')
    else:
        xlabel = f'Fintech Attention Index ({track})'
        title = 'P2 Bank Fintech Attention — distribution'

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title(title)
    fig.tight_layout()

    out_path = pc.output_dir / filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
