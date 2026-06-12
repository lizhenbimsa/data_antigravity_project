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
# P2.2 — Tables 2-5 读取 Stata esttab CSV 输出
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 主回归 (Jha-Liu-Manela 2026)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Token/Hidden/Subst 机制 (Distel 2026 + Westphal-Zajac 2001)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 国企 (SOE) × 态度异质性."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: 稳健性组合 (P25/P75/INT/Ctx/Pos-Neg)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table5_robustness.csv', paper_config)


# ============================================================================
# Plan v2.12 — Tier-A 双轨表 (PAP v1.0-final §2 H3 证据)
# ============================================================================


def build_table_a1_inter_track_kappa(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A1: 轨间一致性 (文章级 rho + bank-year 级 rho)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'tableA1_inter_track_kappa.csv', paper_config)


def build_table_a2_attitude_track_switch(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A2: 双轨切换敏感性 (6 specs: 2 轨 x 3 维度)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'tableA2_attitude_track_switch.csv', paper_config)


def build_table_8b_shrinkage_dual(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 8b: 贝叶斯收缩 (Bayesian shrinkage) 的 ctx 轨伴随表."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('benefit_society', 'table8b_shrinkage_dual.csv', paper_config)


# ============================================================================
# V2.0 J-L-M 2026 稳健性对齐 (Round 9 落地)
# ============================================================================


def build_table_a9_external_validation(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A9: 对 firm-level 第三方指标的外部效度验证 (G4)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(
        'benefit_society', 'tableA9_external_validation.csv', paper_config
    )


def build_table_a10_placebo(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A10: Placebo 业务线稳健性 (S1, J-L-M §4.2 移植)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(
        'benefit_society', 'tableA10_placebo_business_lines.csv', paper_config
    )


def build_table_a11_anchor_alt(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table A11: 替代锚词族 (A2, J-L-M canonical 5-pair vs main 10-pair)."""
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
    # V2.0 J-L-M 2026 对齐 (Round 9)
    'build_table_a9_external_validation',
    'build_table_a10_placebo',
    'build_table_a11_anchor_alt',
]
