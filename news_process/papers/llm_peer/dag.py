"""news_process.papers.llm_peer.dag — 衍生论文 DAG."""

from __future__ import annotations

from news_process.core.dag import STAGES_MAIN, StageSpec

# LLM-Peer IV 列由 stage 48 (pipeline.panel.llm_peer_iv) 经 stage 45 panel
# runner 集成入主面板 — DAG 复用整套主管线 (identity-preserved subset)。
STAGES: list[StageSpec] = list(STAGES_MAIN)


__all__ = ['STAGES']
