"""news_process.papers.brokerage_network.tables — 信息经纪网络论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


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
    return build_summary_table('brokerage_network', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('brokerage_network', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


__all__ = ['build_table1', 'write_table1']
