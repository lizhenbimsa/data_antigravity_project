"""news_process.papers.strategic_diff.dag — 衍生论文 DAG."""

from __future__ import annotations

from news_process.core.dag import STAGES_MAIN, StageSpec

# 战略差异度列由 stage 25 (pipeline.features.strategic_diff) 经 stage 45 panel
# runner 集成入主面板 — DAG 复用整套主管线 (identity-preserved subset)。
STAGES: list[StageSpec] = list(STAGES_MAIN)


__all__ = ['STAGES']
