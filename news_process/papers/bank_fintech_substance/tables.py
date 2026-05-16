"""news_process.papers.bank_fintech_substance.tables — P3 论文表格生成.

P3 = Bank Fintech Substance (W&Z 1994 ASQ substantive vs symbolic).

Table layout (per plan §5.5.2 + R11-m02 注: P3 16_mechanism 用 dual outcome 而非 mediation):
    Table 1: descriptive (substantiveness / dual outcome / controls)
    Table 2: main regression (M1→M6 progressive; long_panel within-bank within-year)
    Table 3: dual outcome (短期 CAR + 长期 ROA 反转, W&Z 1994 实证机制)
    Table 4: heterogeneity (4 bank types × SOE × fintech wave × capital quartile)
    Table 5: advanced robustness (含 alternative substantiveness track full vs ctx)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # P3 treatment (per paper_spec.yaml R35-M01: pipeline v3.2.0 实测列名)
    'innovation_substantiveness_full',
    'innovation_substantiveness_ctx',
    'substantive_minus_symbolic_gap',
    # P3 dual outcome
    'long_run_roa_change_3yr',
    'car_3day_window_fintech_announcement',
    # P3 secondary outcomes
    'ceo_turnover_2yr',
    'executive_pay_change',
    'board_change',
    # Bank-level standard controls
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_substance', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_substance', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 progressive main regression (long_panel within-bank within-year)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table2_main.csv', paper_config)


def build_table3_dual_outcome(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Dual outcome (CAR + long-run ROA reversal) — W&Z 1994 实证机制.

    NB: P3 不用经典 Baron-Kenny mediation, 而用 dual outcome regression (R11-m02)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table3_dual_outcome.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 4 bank types × SOE × wave × capital_ratio quartile heterogeneity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: Advanced robustness + alternative substantiveness track (full vs ctx)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table5_robustness.csv', paper_config)
