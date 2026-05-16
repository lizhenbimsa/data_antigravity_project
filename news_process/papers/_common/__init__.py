"""news_process.papers._common — 跨论文共享内核.

Phase 3b 交付物 + Phase 9b 扩展。提供 6 个支柱:

    paper_config   — PaperConfig dataclass + 路径解析             (无副作用)
    panel_loader   — 按 paper_id 加载 data/processed/*.parquet     (只读 IO)
    tables         — Stata-safe 列名清洗 + 通用 .dta 导出           (无副作用)
    figures        — matplotlib rcParams + 色盲友好调色板          (无副作用)
    stata_runner   — 调用本地 Stata 执行 .do 文件的 subprocess 包装 (子进程)
    pipeline_runner— Phase 9b 桥接: 调用 run_pipeline_function.run_pipeline()
                     ⚠ 唯一有副作用的 export — 触发整套 pipeline 写
                     ``data/processed/*.parquet`` + 改全局状态
                     (NEWS_PROCESS_RUN_ID env / setup_logging 文件 handler /
                     PipelineLock 互斥). 不可在测试 fixture 中无前置 mock 调用.

设计约束 (Phase 3 设计原则, 经 Phase 9b 修订)
-----------------------------------------
1. 不重复实现 ``pipeline/panel/export.py`` 的 ``export_panel()``。
   后者是 bank-fintech-tone 主线论文的专属导出器（含 940+ 行 STATA_LABELS
   字典和 32-字符列名碰撞防护），属于 ``papers/bank_fintech_tone`` 范畴。
   ``_common/tables.py`` 仅提供 *通用、参数化* 的 Stata 导出小工具，
   供衍生论文使用。
2. 所有 Path 解析统一通过 ``core.config.load_config()``，不另起 IO 子系统。
3. 除 ``pipeline_runner.run_main_pipeline`` (Phase 9b 加入) 外, 所有公开
   API 都是 *无副作用* 的纯函数 / 数据类, 方便
   ``tests/test_papers_common.py`` 单元测试隔离。
"""

from news_process.papers._common.figures import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    FIGSIZE_SQUARE,
    FIGSIZE_WIDE,
    apply_publication_style,
)
from news_process.papers._common.panel_loader import (
    list_available_panels,
    load_panel,
)
from news_process.papers._common.paper_config import (
    PaperConfig,
    get_paper_config,
    get_papers_assets_root,
)
from news_process.papers._common.paper_registry import (
    PAPER_IDS_ALL,
    PAPER_IDS_EXISTING,
    PAPER_IDS_NEW,
    PaperSpec,
    get_spec,
    list_paper_ids,
    load_all_specs,
)
from news_process.papers._common.pipeline_runner import (
    run_main_pipeline,
)
from news_process.papers._common.stata_runner import (
    StataNotFoundError,
    run_do,
)
from news_process.papers._common.tables import (
    export_dta,
    sanitize_stata_columns,
    summary_stats,
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
    "run_main_pipeline",
    # M0.2 paper_registry (8 paper spec.yaml 统一入口):
    "PAPER_IDS_ALL",
    "PAPER_IDS_EXISTING",
    "PAPER_IDS_NEW",
    "PaperSpec",
    "get_spec",
    "list_paper_ids",
    "load_all_specs",
]
