"""news_process.papers.benefit_society.tables — 经营效益态度论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # 经营效益态度 (Jha, Liu & Manela 2026, RFS §1.3.2)
    'benefit_mean_full',
    'benefit_mean_ctx',
    'benefit_std_full',
    'benefit_std_ctx',
    'benefit_pos_frac_full',
    'benefit_pos_frac_ctx',
    'benefit_neg_frac_full',
    'benefit_neg_frac_ctx',
    # 信息环境对照
    'n_articles',
    'ln_news_coverage',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('benefit_society', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('benefit_society', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


__all__ = ['build_table1', 'write_table1']
