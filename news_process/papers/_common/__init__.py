"""news_process.papers._common — 跨论文共享内核.

Phase 3b 交付物。提供 5 个互不耦合的支柱:

    paper_config   — PaperConfig dataclass + 路径解析
    panel_loader   — 按 paper_id 加载 data/processed/*.parquet (Phase 8 重命名)
    tables         — Stata-safe 列名清洗 + 通用 .dta 导出 + summary stats
    figures        — matplotlib rcParams + 色盲友好调色板
    stata_runner   — 调用本地 Stata 执行 .do 文件的 subprocess 包装

设计约束 (Phase 3 设计原则)
--------------------------
1. 不重复实现 ``pipeline/panel/export.py`` 的 ``export_panel()``。
   后者是 bank-fintech-tone 主线论文的专属导出器（含 940+ 行 STATA_LABELS
   字典和 32-字符列名碰撞防护），属于 ``papers/bank_fintech_tone`` 范畴。
   ``_common/tables.py`` 仅提供 *通用、参数化* 的 Stata 导出小工具，
   供衍生论文使用。
2. 所有 Path 解析统一通过 ``core.config.load_config()``，不另起 IO 子系统。
3. 所有公开 API 都是 *无副作用* 的纯函数 / 数据类，
   方便 ``tests/unit/test_papers_common.py`` 单元测试隔离。
"""

from news_process.papers._common.paper_config import (
    PaperConfig,
    get_paper_config,
    get_papers_assets_root,
)
from news_process.papers._common.panel_loader import (
    load_panel,
    list_available_panels,
)
from news_process.papers._common.tables import (
    sanitize_stata_columns,
    export_dta,
    summary_stats,
)
from news_process.papers._common.figures import (
    apply_publication_style,
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    FIGSIZE_WIDE,
    FIGSIZE_SQUARE,
)
from news_process.papers._common.stata_runner import (
    run_do,
    StataNotFoundError,
)

__all__ = [
    "PaperConfig",
    "get_paper_config",
    "get_papers_assets_root",
    "load_panel",
    "list_available_panels",
    "sanitize_stata_columns",
    "export_dta",
    "summary_stats",
    "apply_publication_style",
    "COLORBLIND_PALETTE",
    "FIGSIZE_SINGLE",
    "FIGSIZE_WIDE",
    "FIGSIZE_SQUARE",
    "run_do",
    "StataNotFoundError",
]
