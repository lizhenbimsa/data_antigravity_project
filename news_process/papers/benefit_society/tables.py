"""news_process.papers.benefit_society.tables — 经营效益态度论文表格生成."""

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
    pc = paper_config or get_paper_config('benefit_society')
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)
    available = [v for v in _TABLE1_VARIABLES if v in panel.columns]
    return summary_stats(panel, variables=available)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    table = build_table1(pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')
    if dta_filename:
        export_dta(table.reset_index(), pc.output_dir / dta_filename)
    return csv_path


__all__ = ['build_table1', 'write_table1']
