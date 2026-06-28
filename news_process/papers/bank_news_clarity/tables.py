"""news_process.papers.bank_news_clarity.tables — 第11篇表格 (provisional 2026-06-01).

Table 1 (descriptive stats) 走 _common 通用 summary builder, 与其它 paper 对称, 即开即用。
Tables 2-5 (主回归 / LLP ratio 替代 outcome / 异质性 / 稳健性) 为 esttab CSV reader 占位,
待 M7 跑通 Stata 后填实 (Bushman-Williams 2012 JAE external info environment 仅作 framework
anchor — 当前 loan_loss_provision_discretion 列实为裸 LLP/贷款比率, 非 BW2012 残差式
discretion; outcome 为 CAR-based Z-score 变体, cf. Laeven-Levine 2009 — 见 paper_spec
outcome 更正)。fix(omni-g-zscore-papers-01, 2026-06-11)。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd

PAPER_ID = 'bank_news_clarity'

# treatment (三轨 news clarity full/ctx/ss, 全 parity) + outcome (Z-score 稳定性) + 标准控制
# 三轨互为稳健性 (full=正文全文 / ctx=实体窗口 / ss=银行+金科同句共现, v3.9.0);
# summary builder 对缺列优雅跳过 → ss 值在 P4 付费 run 落盘前为 NaN 不影响表生成。
_TABLE1_VARIABLES: list[str] = [
    'mean_clarity_score_full', # treatment.primary (full 轨, full-only gating 2026-06-29)
    'mean_clarity_score_ctx',  # treatment _ctx 轨 (entity-context; 降为首要 robustness 孪生)
    'mean_clarity_score_ss',   # treatment ss 轨 (银行+金科同句共现; P4 前 NaN, 防御保留)
    'z_score',                 # outcome.primary (CAR-based Z-score 变体, cf. Laeven-Levine 2009; 与第10篇共享)
    'sigma_roa_5y_rolling',
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table(PAPER_ID, _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table(PAPER_ID, _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# Tables 2-5 读取 Stata esttab CSV 输出 (M7 阶段填实)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 主回归 (news clarity 作为 external info environment quality
    proxy → 银行风险承担; 原英文注释把 proxy 误写成回归右端→左端方向, 已更正)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(PAPER_ID, 'table2_main.csv', paper_config)
