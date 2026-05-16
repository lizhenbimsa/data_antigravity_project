"""news_process.papers.bank_fintech_attention.tables — P2 论文表格生成.

P2 = Bank Fintech Attention (Hassan 2019 QJE style firm-level attention intensity).

Table layout (per plan §5.8.2 / §B.2):
    Table 1: descriptive statistics (attention / outcomes / controls)
    Table 2: main regression (M1→M6 progressive; staggered DiD baseline + IV)
    Table 3: mechanism (attention → ln_fintech_mdna_length → ln_fintech_investment)
    Table 4: heterogeneity (4 bank types × fintech wave + SOE)
    Table 5: advanced robustness (Oster δ + rwolf + Honest DiD + ...)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


# Attention treatments (stage 14_fintech_intensity derivatives) + outcome enrichment
_TABLE1_VARIABLES: list[str] = [
    # P2 treatment (per paper_spec.yaml R36-m01)
    'attention_index_full',
    'attention_index_ctx',
    'attention_disp_full',
    'attention_pct_full',
    # P2 outcome (M0.5.11 financial enrichment)
    'ln_fintech_investment',
    'm_and_a_fintech',
    'patent_fintech_count',
    'employee_growth_it',
    # P2 mediator
    'ln_fintech_mdna_length',
    # Bank-level standard controls
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_attention', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_attention', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# Tables 2-5 from Stata esttab CSV output (filled at M5/M6)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 progressive main regression (staggered DiD baseline + IV)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Mediation (attention → ln_fintech_mdna_length → ln_fintech_investment).

    Baron-Kenny 1986 + Imai-Keele-Tingley 2010 sensitivity (per §5.5.2 R7-M01/M02)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 4 bank types × fintech wave + SOE × non-SOE heterogeneity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: Advanced robustness (Oster δ / rwolf / Honest DiD / wild bootstrap / ritest /
    spillover / sample cuts + paper-specific alternative attention measures)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table5_robustness.csv', paper_config)
