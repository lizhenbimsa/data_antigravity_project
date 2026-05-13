"""news_process.papers.llm_peer.tables — LLM-Peer 论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # LLM 同业 IV 主变量 (cutoff=0.80 标准)
    'llm_peer_tone_iv_full',
    'llm_peer_coverage_iv',
    'llm_peer_count',
    'peer_compete_idx',
    # 多阈值敏感性 (主要 cutoff)
    'llm_peer_tone_iv_full_70',
    'llm_peer_tone_iv_full_75',
    'llm_peer_tone_iv_full_80',
    'llm_peer_tone_iv_full_85',
    'llm_peer_tone_iv_full_90',
    # 对照基线
    'n_articles',
    'llm_vote_tone_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('llm_peer', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('llm_peer', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


__all__ = ['build_table1', 'write_table1']
