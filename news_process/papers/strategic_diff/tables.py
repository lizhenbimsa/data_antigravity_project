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
    # outcome (2026-06-13 重定位: 主因变量 = 特许权价值, 外部财务待落盘 → NaN 占位行)
    'tobin_q',
    # 全行业重心 (谢佳松 2025; full 轨, ss 同句共现孪生作三轨稳健性)
    'centroid_diff_tfidf_c',
    'centroid_diff_lda',
    'centroid_diff_emb',
    'centroid_diff_tfidf_c_ss',
    'centroid_diff_lda_ss',
    'centroid_diff_emb_ss',
    # 文本连贯性 (Time-coherence; full 轨 + ss 同句共现轨)
    # 三轨 (full/ctx/ss) 平价 (third-track-ss 2026-06-14): coh_*_ss / centroid_diff_*_ss
    # = 银行+金科同句共现轨 (strategic_diff.py 镜像 ctx 轨产出, 标签 "(银行+金科同句)");
    # ss 列 stage 15 三轨产出后落盘, 落盘前 build_summary_table(strict=False) NaN 占位。
    'coh_tfidf_c_full',
    'coh_lda_full',
    'coh_emb_full',
    'coh_tfidf_c_ss',
    'coh_lda_ss',
    'coh_emb_ss',
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
# P2.2 — Tables 2-5 读取 Stata esttab CSV 输出
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 主回归 (Guzman-Li 2023 + Hoberg-Phillips 2016)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Bartik IV + 多方法对照."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 国企 (SOE) 分样本异质性."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: N 邻敏感性 / 行业重心 / Ctx 轨 + Ss 轨 (银行+金科同句共现) 稳健性
    (读 table5a_n_sensitivity.csv).

    third-track-ss 2026-06-14: 加 ss 轨 (strat_diff_n5_ss / coh_*_ss / centroid_diff_*_ss)
    作同句共现稳健性, 与 full/ctx 三轨互为稳健性; ss 列缺失时 Stata capture confirm 守卫。"""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('strategic_diff', 'table5a_n_sensitivity.csv', paper_config)


__all__ = [
    'build_table1', 'write_table1',
    'build_table2_main', 'build_table3_mechanism',
    'build_table4_heterogeneity', 'build_table5_robustness',
]
