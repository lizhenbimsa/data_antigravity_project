"""news_process.papers.brokerage_network.dag — 衍生论文 DAG.

经纪网络指标 (stage 47, 集成在 ``pipeline.panel.runner``) 落于
``40_panel_yearly.parquet``, DAG 复用整套主管线 (identity-preserved subset)。
"""

from __future__ import annotations

from news_process.core.dag import STAGES_MAIN, StageSpec

STAGES: list[StageSpec] = list(STAGES_MAIN)


__all__ = ['STAGES']
