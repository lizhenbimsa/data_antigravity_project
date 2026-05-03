"""news_process.papers.strategic_diff.tables — 战略差异度论文表格生成."""

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
    # N-最近邻 (Guzman & Li 2023)
    'strat_diff_n3',
    'strat_diff_n4',
    'strat_diff_n5',
    'strat_diff_n6',
    'strat_diff_n7',
    # 最大同业相似度
    'strat_sim_max',
    'strat_sim_max_w',
    # 产品市场流动性 (Hoberg-Phillips 2016)
    'strat_fluidity',
    'strat_fluidity_w',
    # 多方法稳健性
    'strat_diff_n5_lda',
    'strat_diff_n5_emb',
    # 全行业重心 (谢佳松 2025)
    'centroid_diff_tfidf_c',
    'centroid_diff_lda',
    'centroid_diff_emb',
    # 文本连贯性 (Time-coherence)
    'coh_tfidf_c_full',
    'coh_lda_full',
    'coh_emb_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    pc = paper_config or get_paper_config('strategic_diff')
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)
    available = [v for v in _TABLE1_VARIABLES if v in panel.columns]
    return summary_stats(panel, variables=available)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    pc = paper_config or get_paper_config('strategic_diff')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    table = build_table1(pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')
    if dta_filename:
        export_dta(table.reset_index(), pc.output_dir / dta_filename)
    return csv_path


__all__ = ['build_table1', 'write_table1']
