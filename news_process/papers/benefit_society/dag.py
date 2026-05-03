"""news_process.papers.benefit_society.dag — 衍生论文 DAG.

经营效益态度投影 (stage 27, 集成在 ``pipeline.panel.runner``) 的输出列
落在 ``40_panel_yearly.parquet`` 中, 因此 DAG 复用整套主管线
(identity-preserved subset)。
"""

from __future__ import annotations

from news_process.core.dag import STAGES_MAIN, StageSpec

# Phase 3d 最小可用集: 全集 — 因为 benefit_society 列由 stage 45 panel runner
# 集成产出, 上游每一步都是必须的。后续 stage 拆分到更小粒度后再行收紧。
STAGES: list[StageSpec] = list(STAGES_MAIN)


__all__ = ['STAGES']
