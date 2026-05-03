"""news_process.papers._common.panel_loader — pipeline 输出面板加载.

提供两个轻量级 helper:
    - ``load_panel(filename, paper_id=None)``: 加载单个 parquet 面板。
    - ``list_available_panels()``: 罗列 ``OUTPUT_REGISTRY`` 中已经在磁盘
       存在的面板, 便于诊断 "我现在能跑哪些下游分析"。

设计原则
--------
- 默认从 ``cfg['paths']['output_dir']`` 解析面板目录, 不引入新的路径源。
- ``OUTPUT_REGISTRY`` 是 schemas 单源, 不在此重复硬编码文件名清单。
- 失败时给出明确诊断信息, 引导用户回到对应 pipeline 阶段。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from news_process.core.config import load_config
from news_process.core.schemas import OUTPUT_REGISTRY
from news_process.papers._common.paper_config import (
    PaperConfig,
    get_paper_config,
)


def _resolve_panel_dir(project_config: dict[str, Any] | None) -> Path:
    cfg = project_config if project_config is not None else load_config()
    panel_dir = cfg.get('paths', {}).get('output_dir')
    if not panel_dir:
        raise KeyError(
            "cfg['paths']['output_dir'] 未配置; 无法定位 pipeline 输出目录"
        )
    return Path(panel_dir)


def load_panel(filename: str = '40_panel_yearly.parquet',
               *,
               paper_id: str | None = None,
               project_config: dict[str, Any] | None = None,
               columns: list[str] | None = None) -> pd.DataFrame:
    """从 pipeline 输出目录加载一个 parquet 面板.

    Args:
        filename:        面板 parquet 文件名 (e.g. ``'40_panel_yearly.parquet'``)。
        paper_id:        可选 — 给定 paper_id 时使用其 ``panel_dir``;
                         否则从 ``cfg['paths']['output_dir']`` 解析。
        project_config:  可选 — 复用已加载的项目 cfg, 避免 YAML I/O。
        columns:         可选 — pyarrow.read_parquet 列过滤
                         (大面板加载时显著提速)。

    Returns:
        ``pd.DataFrame``。

    Raises:
        FileNotFoundError: 文件不存在 — 错误信息会指出对应的 pipeline 阶段。
    """
    if paper_id is not None:
        pc: PaperConfig = get_paper_config(paper_id, project_config)
        panel_dir = pc.panel_dir
    else:
        panel_dir = _resolve_panel_dir(project_config)

    panel_path = panel_dir / filename
    if not panel_path.exists():
        producer = _find_producer_stage(filename)
        hint = (
            f" 该文件由 pipeline 阶段 {producer!r} 产生; "
            f"请先运行 ``python news_process/{producer}`` "
            f"或整条 pipeline (run_pipeline_function.py)。"
        ) if producer else ""
        raise FileNotFoundError(
            f"面板文件不存在: {panel_path}.{hint}"
        )

    return pd.read_parquet(panel_path, columns=columns)


def list_available_panels(project_config: dict[str, Any] | None = None,
                          panel_dir: Path | str | None = None
                          ) -> dict[str, list[str]]:
    """罗列 OUTPUT_REGISTRY 中已经在磁盘存在的面板.

    Returns:
        ``{stage_script: [filename, ...]}`` — 仅包含确实存在的文件,
        缺失的 entry 不出现; 整阶段都缺则 stage_script 整体不出现。
    """
    if panel_dir is None:
        panel_dir = _resolve_panel_dir(project_config)
    else:
        panel_dir = Path(panel_dir)

    available: dict[str, list[str]] = {}
    for stage_script, parquets in OUTPUT_REGISTRY.items():
        present = [p for p in parquets if (panel_dir / p).exists()]
        if present:
            available[stage_script] = present
    return available


def _find_producer_stage(filename: str) -> str | None:
    """在 ``OUTPUT_REGISTRY`` 中反查产生 ``filename`` 的 stage 脚本名."""
    for stage_script, parquets in OUTPUT_REGISTRY.items():
        if filename in parquets:
            return stage_script
    return None


__all__ = ['load_panel', 'list_available_panels']
