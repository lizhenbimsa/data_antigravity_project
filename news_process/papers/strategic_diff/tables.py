"""news_process.papers.strategic_diff.tables — 战略差异度论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # N-最近邻 (Guzman & Li 2023)
    'strat_diff_n3',
    'strat_diff_n4',
    'strat_diff_n5',
    'strat_diff_n6',
    'strat_diff_n7',
    # 最大同业相似度
    'strat_sim_max',
    'strat_sim_max_w',
    # 产品市场流动性 (Hoberg-Phillips 2016)
    'strat_fluidity',
    'strat_fluidity_w',
    # 多方法稳健性
    'strat_diff_n5_lda',
    'strat_diff_n5_emb',
    # 全行业重心 (谢佳松 2025)
    'centroid_diff_tfidf_c',
    'centroid_diff_lda',
    'centroid_diff_emb',
    # 文本连贯性 (Time-coherence)
    'coh_tfidf_c_full',
    'coh_lda_full',
    'coh_emb_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('strategic_diff', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('strategic_diff', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# P2.2 — Tables 2-5 from Stata esttab CSV output
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: Main regression (Guzman-Li 2023 + Hoberg-Phillips 2016)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Bartik IV + multi-method comparison."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: SOE split heterogeneity."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: N-sensitivity / Centroid / Ctx-track."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table5a_n_sensitivity.csv', paper_config)


__all__ = [
    'build_table1', 'write_table1',
    'build_table2_main', 'build_table3_mechanism',
    'build_table4_heterogeneity', 'build_table5_robustness',
]
