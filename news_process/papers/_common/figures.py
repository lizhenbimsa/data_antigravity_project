"""news_process.papers._common.figures — 发表级 matplotlib 默认配置 + 调色板.

跨论文统一图风:
    - 字体大小 / 行宽 / 网格设置 (符合 JF / JFE / RFS 排版要求)
    - 色盲友好的 Paul Tol 调色板 (8 色)
    - 单/双栏图尺寸常量 (basic / wide)

本模块**不绘图**, 只设置 rcParams 和提供颜色常量。
具体每个论文的 figures.py 自己决定 plt.figure() 内容。
"""

from __future__ import annotations

from typing import Final


# ----------------------------------------------------------------------------
# 1. Paul Tol "muted" 8-色色盲友好调色板.
#    https://personal.sron.nl/~pault/   (Tol 2018, "Colour schemes")
# ----------------------------------------------------------------------------
COLORBLIND_PALETTE: Final[tuple[str, ...]] = (
    '#332288',  # indigo
    '#117733',  # green
    '#44AA99',  # teal
    '#88CCEE',  # cyan
    '#DDCC77',  # sand
    '#CC6677',  # rose
    '#AA4499',  # purple
    '#882255',  # wine
)


# ----------------------------------------------------------------------------
# 2. 期刊级图表尺寸 (英寸); 适配 single-column 与 double-column 排版.
# ----------------------------------------------------------------------------
FIGSIZE_SINGLE: Final[tuple[float, float]] = (3.5, 2.6)   # JF/JFE 单栏 ~3.5 in
FIGSIZE_WIDE: Final[tuple[float, float]] = (7.0, 4.0)     # 双栏跨页
FIGSIZE_SQUARE: Final[tuple[float, float]] = (4.0, 4.0)   # 散点/相关矩阵


# ----------------------------------------------------------------------------
# 3. apply_publication_style — 写入 matplotlib rcParams.
# ----------------------------------------------------------------------------


def apply_publication_style(font_size: int = 9,
                            line_width: float = 0.8,
                            *,
                            grid: bool = True) -> None:
    """覆盖 matplotlib rcParams 为发表级默认.

    设计目标:
    - 字体: Times New Roman / DejaVu Serif (跨平台 fallback)
    - 字体大小: 9 pt (期刊正文 + 0~1 pt)
    - 线宽: 0.8 (符合 NBER working paper 风格)
    - 颜色循环: COLORBLIND_PALETTE
    - 网格: 默认开启, 半透明 dashed

    幂等: 多次调用产生相同结果。

    Args:
        font_size:   全局字号 (默认 9 pt)。
        line_width:  axes/线条/tick 线宽 (默认 0.8 pt)。
        grid:        是否启用网格 (默认 True)。
    """
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
        'font.size': font_size,
        'axes.titlesize': font_size,
        'axes.labelsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 1,
        'figure.titlesize': font_size + 1,

        'axes.linewidth': line_width,
        'lines.linewidth': line_width * 1.5,
        'xtick.major.width': line_width,
        'ytick.major.width': line_width,
        'patch.linewidth': line_width,

        'axes.grid': grid,
        'grid.linestyle': '--',
        'grid.linewidth': line_width * 0.6,
        'grid.alpha': 0.4,

        'axes.prop_cycle': plt.cycler(color=list(COLORBLIND_PALETTE)),
        'axes.spines.top': False,
        'axes.spines.right': False,

        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.format': 'pdf',
    })


__all__ = [
    'COLORBLIND_PALETTE',
    'FIGSIZE_SINGLE',
    'FIGSIZE_WIDE',
    'FIGSIZE_SQUARE',
    'apply_publication_style',
]
