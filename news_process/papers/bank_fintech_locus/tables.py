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


# fix(omni-g-papers-misc-03/-11, 2026-06-11): treatment 行改 panel 真实物化的
# bank-year 编码 (tech_frac/app_frac + ctx 轨 *_lc) — 旧清单的 locus_layer_full/
# locus_scenario_full/locus_gap 仅在 Stata 01_data_prep.do 内由 tech_frac/app_frac
# 临时 gen, 不落 parquet (结构性错名 → Table 1 全 NaN)。金融 enrichment 列
# (待 M0.5.11) 保留为可见 NaN 占位行 (F16 政策) 并经 CSV 脚注披露。
_TABLE1_VARIABLES: list[str] = [
    # P4 treatment 源列 — panel 真实列 (底层技术/应用场景占比, full 轨 + ctx 轨)
    'tech_frac',
    'app_frac',
    'tech_frac_lc',
    'app_frac_lc',
    # P4 primary outcome (M0.5.11 enrichment 待落盘)
    'car_5day_window',
    'patent_fintech_count',
    'citation_weighted_patent',
    # P4 mediator (R7-M04; M0.5.11 enrichment 待落盘)
    'capex_it',
    'r_and_d_intensity',
    # Bank-level standard controls (M0.5.11 enrichment 待落盘)
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]

# Table 1 CSV 脚注 (存在性披露; fix(omni-g-papers-misc-03))
_TABLE1_FOOTNOTE = (
    "Treatment rows use panel-materialized bank-year shares "
    "(tech_frac/app_frac, full track; *_lc = ctx track); the regression "
    "indicators locus_layer_full/locus_scenario_full/locus_gap are derived "
    "from these in Stata 01_data_prep.do (dominant-category binarization) "
    "and do not exist on the parquet panel. "
    "Outcome/mediator/control rows pending M0.5.11 financial enrichment "
    "appear as NaN placeholder rows until materialized."
)


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_locus', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_locus', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename,
                               footnote=_TABLE1_FOOTNOTE)


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
