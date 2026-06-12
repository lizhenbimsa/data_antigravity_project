"""validation 各绘图模块共享的 Matplotlib 辅助工具。"""

from __future__ import annotations

from functools import lru_cache

_CJK_FONT_CANDIDATES = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "WenQuanYi Micro Hei",
    "PingFang SC",
    "Heiti SC",
    "Arial Unicode MS",
]


@lru_cache(maxsize=1)
def _installed_font_names() -> set[str]:
    import matplotlib.font_manager as fm

    return {font.name for font in fm.fontManager.ttflist}


def configure_matplotlib_chinese_fonts() -> str | None:
    """配置 Matplotlib 中文字体, 使中文标签渲染不再报缺字形警告。"""
    import matplotlib.pyplot as plt

    installed = _installed_font_names()
    usable = [name for name in _CJK_FONT_CANDIDATES if name in installed]
    if usable:
        current = list(plt.rcParams.get("font.sans-serif", []))
        plt.rcParams["font.sans-serif"] = usable + [
            name for name in current if name not in usable
        ]
        plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    return usable[0] if usable else None
