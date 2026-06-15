"""news_process.papers.llm_peer.tables — LLM-Peer 论文表格生成."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


_TABLE1_VARIABLES: list[str] = [
    # LLM 同业 IV 主变量 (cutoff=0.80 标准)
    'llm_peer_tone_iv_full',
    # ctx + ss 三轨稳健性镜像 (2026-06-13 ctx; third-track-ss 2026-06-14 加 ss):
    # Table 2 M5 列 (llm_vote_tone_ctx = llm_peer_tone_iv_ctx) 对应的描述统计, 与 full
    # 轨 IV 并列, 使 ctx/ss 规格自洽。ss = 银行+金科同句共现轨 (llm_peer_tone_iv_ss,
    # 标签 "(银行+金科同句)"; 三轨各自 just-identified 并排, 严禁合成 over-id Hansen J)。
    'llm_peer_tone_iv_ctx',
    'llm_peer_tone_iv_ss',
    'llm_peer_coverage_iv',
    'llm_peer_count',
    'peer_compete_idx',
    # 多阈值敏感性 (主要 cutoff)
    'llm_peer_tone_iv_full_70',
    'llm_peer_tone_iv_full_75',
    'llm_peer_tone_iv_full_80',
    'llm_peer_tone_iv_full_85',
    'llm_peer_tone_iv_full_90',
    # 对照基线 (内生变量三轨: full=主规格, ctx=M5 稳健性, ss=同句共现稳健性)
    'n_articles',
    'llm_vote_tone_full',
    'llm_vote_tone_ctx',
    'llm_vote_tone_ss',
    # ── 主 outcome (PORT SAL-3 修正 2026-06-14, 顶刊重审): real-economy 财务/创新结局。
    #    撤销 2026-06-13 的 avg_ft_intensity_full 文本量 outcome (与 P2 attention
    #    treatment 同源, 反映共同媒体覆盖因子而非真实公司行为)。这些是外部财务面板
    #    sentinel (M0.5.11 待接入); build_summary_table strict=False → 接入前以 NaN
    #    占位行可见保留 (golden-safe, 不静默剔除), 接入后自动填实。
    'roa',                          # spec.outcome.primary (银行盈利能力, headline)
    'ln_fintech_investment',        # spec.outcome.secondary (fintech 实际投入)
    'citation_weighted_patent',     # spec.outcome.secondary (创新产出, Kogan 2017)
    'tobin_q',                      # spec.outcome.secondary (市场估值; Wind 市值)
    # first-stage 机制佐证 (NON-headline, PORT SAL-3 降级): 原主 outcome 降于此,
    #    展示 LLM-peer IV → own tone → own fintech 报道强度的中间通道, 不作 headline。
    'avg_ft_intensity_full',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('llm_peer', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('llm_peer', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# P2.2 — Tables 2-5 读取 Stata esttab CSV 输出
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 主回归 IV 2SLS (Cao et al. 2025) — 读 esttab CSV."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('llm_peer', 'table2_main_iv_2sls.csv', paper_config)


def build_table3_cutoff(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: cutoff 阈值敏感性 (τ ∈ {0.70,...,0.90})."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('llm_peer', 'table3_cutoff_sensitivity.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 国企 (SOE) 异质性 (交互项 + 分样本 2SLS)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('llm_peer', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: 稳健性组合 (cov-IV / +compIdx / Ctx 轨 / ss 轨 (银行+金科同句共现) / 省级聚类).

    third-track-ss 2026-06-14: 加 ss 轨 (llm_peer_tone_iv_ss) 作同句共现稳健性, 与 full/ctx
    各自 just-identified 并排 (严禁三轨合成 over-id Hansen J); ss 列缺失时 Stata capture
    confirm 守卫优雅降级。"""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('llm_peer', 'table5_robustness.csv', paper_config)


__all__ = [
    'build_table1', 'write_table1',
    'build_table2_main', 'build_table3_cutoff',
    'build_table4_heterogeneity', 'build_table5_robustness',
]
