"""news_process.papers.brokerage_network.tables — 信息经纪网络论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # 经纪网络中心性 (Han et al. 2024)
    'brokerage_eigen_cent',
    'industry_neg_shock',
    'brokerage_fire_sale',
    'peer_fintech_exposure_lag1',
    # 共现网络补充 (节点级)
    'bank_degree_cent',
    'bank_strength_cent',
    # ⚠ NB-04 (network-metrics-reaudit 2026-06-13): bank_eigen_cent 自 P1-1 起按连通分量
    #   内 L2 归一 → 跨分量水平不可比; 此处池化 mean/sd 混合不同分量标尺, 仅作粗略描述,
    #   非回归 RHS (回归用 brokerage_eigen_cent)。表注宜注明"分量内归一"。
    'bank_eigen_cent',
    'bank_clustering',
    'bank_constraint',
    'bank_ego_density',
    'bank_effective_size',
    # 一/二阶溢出
    'peer_tone_lag1_full',
    'peer_tone_2nd_lag1_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('brokerage_network', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('brokerage_network', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# P2.2 — Tables 2-5 读取 Stata esttab CSV 输出
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 网络 2SLS 主回归 (Bramoulle 2009)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('brokerage_network', 'table2_main_iv_2sls.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: 机制 — 中心性 × DCEP/监管沙盒政策交互."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('brokerage_network', 'table3_mechanism_policy.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 国企 (SOE) 分样本 2SLS 异质性."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('brokerage_network', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: 稳健性 (Ctx 轨 / ss 轨 (银行+金科同句共现) / bank 聚类 / 二阶滞后 (L2.) 中心度).

    third-track-ss 2026-06-14: peer_tone_lag1_ss / peer_tone_2nd_lag1_ss 由
    network_spillover 三轨 (full/ctx/ss) 传播产出, 作 spillover IV 工具的同句共现稳健性轨
    (与 full/ctx 各自 just-identified 并排, 严禁三轨合成 over-id Hansen J); ss 列缺失时
    Stata capture confirm 守卫优雅降级。Table 1 仅列 full 轨 (peer_tone_lag1_full 作主 IV
    工具源), ctx/ss 稳健轨在本表展开。"""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('brokerage_network', 'table5_robustness.csv', paper_config)


__all__ = [
    'build_table1', 'write_table1',
    'build_table2_main', 'build_table3_mechanism',
    'build_table4_heterogeneity', 'build_table5_robustness',
]
