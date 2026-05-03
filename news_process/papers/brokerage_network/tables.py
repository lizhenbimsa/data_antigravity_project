"""news_process.papers.brokerage_network.tables — 信息经纪网络论文表格生成."""

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
    # 经纪网络中心性 (Han et al. 2024)
    'brokerage_eigen_cent',
    'industry_neg_shock',
    'brokerage_fire_sale',
    'peer_fintech_exposure_lag1',
    # 共现网络补充 (节点级)
    'bank_degree_cent',
    'bank_strength_cent',
    'bank_eigen_cent',
    'bank_clustering',
    'bank_constraint',
    'bank_ego_density',
    'bank_effective_size',
    # 一/二阶溢出
    'peer_tone_lag1_full',
    'peer_tone_2nd_lag1_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    pc = paper_config or get_paper_config('brokerage_network')
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)
    available = [v for v in _TABLE1_VARIABLES if v in panel.columns]
    return summary_stats(panel, variables=available)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    pc = paper_config or get_paper_config('brokerage_network')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    table = build_table1(pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')
    if dta_filename:
        export_dta(table.reset_index(), pc.output_dir / dta_filename)
    return csv_path


__all__ = ['build_table1', 'write_table1']
