"""news_process.papers.bank_fintech_collab.tables — P5 论文表格 (provisional 2026-06-01).

Table 1 (descriptive stats) 走 _common 通用 summary builder, 与其它 paper 对称, 即开即用。
Tables 2-5 (主回归 M1→M6 / 机制 / 异质性 / 稳健性) 为 esttab CSV reader 占位, 待 M5/M6
跑通 Stata 后填实 (Chesbrough 2003 Open Innovation; Laursen & Salter 2006 SMJ 27:131-150)。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd

PAPER_ID = 'bank_fintech_collab'

# P5 treatment (innovation_collab_mode) + outcome (M&A / R&D / CAR) + 标准控制
_TABLE1_VARIABLES: list[str] = [
    'innovation_collab_mode_full',     # treatment.primary (Chesbrough 2003)
    'innovation_collab_mode_ctx',      # context-conditional 轨 (Hassan 2019 QJE)
    'm_and_a_fintech',                 # outcome.primary (外部协同直接 outcome)
    'r_and_d_intensity',               # secondary (自主研发强度)
    'car_5day_window',                 # short-run 市场反应
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table(PAPER_ID, _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table(PAPER_ID, _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# Tables 2-5 from Stata esttab CSV output (filled at M5/M6)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 progressive main regression (collab_mode → M&A / R&D)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(PAPER_ID, 'table2_main.csv', paper_config)
