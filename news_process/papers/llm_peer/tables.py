"""news_process.papers.llm_peer.tables — LLM-Peer 论文表格生成."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from news_process.papers._common import (
    PaperConfig,
    get_paper_config,
    load_panel,
    summary_stats,
    export_dta,
)


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
    pc = paper_config or get_paper_config('llm_peer')
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)
    available = [v for v in _TABLE1_VARIABLES if v in panel.columns]
    return summary_stats(panel, variables=available)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    pc = paper_config or get_paper_config('llm_peer')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    table = build_table1(pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')
    if dta_filename:
        export_dta(table.reset_index(), pc.output_dir / dta_filename)
    return csv_path


__all__ = ['build_table1', 'write_table1']
