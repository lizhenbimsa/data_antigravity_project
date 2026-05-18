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


# ============================================================================
# P2.2 — Tables 2-5 from Stata esttab CSV output
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: Main regression (Jha-Liu-Manela 2026)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Token/Hidden/Subst mechanism (Distel 2026 + Westphal-Zajac 2001)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: SOE × attitude heterogeneity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: Robustness battery (P25/P75/INT/Ctx/Pos-Neg)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table5_robustness.csv', paper_config)


# ============================================================================
# Plan v2.12 — Tier-A dual-track tables (PAP v1.0-final §2 H3 evidence)
# ============================================================================


def build_table_a1_inter_track_kappa(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A1: Inter-track agreement (article-level rho + bank-year rho)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'tableA1_inter_track_kappa.csv', paper_config)


def build_table_a2_attitude_track_switch(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A2: Dual-track switch sensitivity (6 specs: 2 tracks x 3 dimensions)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'tableA2_attitude_track_switch.csv', paper_config)


def build_table_8b_shrinkage_dual(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 8b: Bayesian shrinkage ctx-track companion."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table8b_shrinkage_dual.csv', paper_config)


# ============================================================================
# V2.0 J-L-M 2026 robustness alignment (Round 9 implementation)
# ============================================================================


def build_table_a9_external_validation(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A9: External validation against firm-level third-party indicators (G4)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(
        'benefit_society', 'tableA9_external_validation.csv', paper_config
    )


def build_table_a10_placebo(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A10: Placebo business-line robustness (S1, J-L-M §4.2 transposed)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(
        'benefit_society', 'tableA10_placebo_business_lines.csv', paper_config
    )


def build_table_a11_anchor_alt(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A11: Alternative anchor family (A2, J-L-M canonical 5-pair vs main 10-pair)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(
        'benefit_society', 'tableA11_anchor_family_alternative.csv', paper_config
    )


__all__ = [
    'build_table1', 'write_table1',
    'build_table2_main', 'build_table3_mechanism',
    'build_table4_heterogeneity', 'build_table5_robustness',
    'build_table_a1_inter_track_kappa',
    'build_table_a2_attitude_track_switch',
    'build_table_8b_shrinkage_dual',
    # V2.0 J-L-M 2026 alignment (Round 9)
    'build_table_a9_external_validation',
    'build_table_a10_placebo',
    'build_table_a11_anchor_alt',
]
