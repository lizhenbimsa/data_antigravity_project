"""news_process.papers.bank_fintech_locus.tables — P4 论文表格生成.

P4 = Bank Fintech Locus (Gomber 2018 JMIS + Kogan 2017 QJE).

Table layout (per plan §5.8.2 / §B.4):
    Table 1: descriptive (locus_layer / locus_scenario / outcomes / controls)
    Table 2: main regression (M1→M6 progressive; layer × event study)
    Table 3: mechanism (locus → R&D / IT capex → patent + stock return; Baron-Kenny)
    Table 4: heterogeneity (三波 fintech 浪潮 wave_1/2/3 + consolidation + SOE)
    Table 5: advanced robustness (含 alternative locus classifier + Borusyak DiD)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # P4 primary_pair treatment (R35-M02 derived)
    'locus_layer_full',
    'locus_scenario_full',
    'locus_gap',
    # P4 primary outcome
    'car_5day_window',
    'patent_fintech_count',
    'citation_weighted_patent',
    # P4 mediator (R7-M04)
    'capex_it',
    'r_and_d_intensity',
    # Bank-level standard controls
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_locus', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_locus', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 progressive main regression (layer × event study baseline)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_locus', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Mediation (locus → capex_it / r_and_d_intensity → patent / car).

    Baron-Kenny 1986 + Imai-Keele-Tingley 2010 sensitivity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_locus', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 三波 fintech 浪潮 (wave_1/2/3) + consolidation + SOE heterogeneity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_locus', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: Advanced robustness + alternative locus classifier (full vs ctx) + Borusyak DiD."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_locus', 'table5_robustness.csv', paper_config)
