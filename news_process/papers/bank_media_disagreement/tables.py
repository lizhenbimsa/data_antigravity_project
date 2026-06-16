"""news_process.papers.bank_media_disagreement.tables — 第10篇表格 (provisional 2026-06-01).

Table 1 (descriptive stats) 走 _common 通用 summary builder, 与其它 paper 对称, 即开即用。
Tables 2-5 (主回归 / 机制 / 异质性 / 稳健性) 为 esttab CSV reader 占位, 待 M5 跑通 Stata
后填实 (Cookson-Niessner 2020 JF media disagreement, 勘误: 旧注释误标 RFS;
outcome 为 CAR-based Z-score 变体,
cf. Laeven-Levine 2009 JFE — 资本项=监管 CAR 非账面 equity/assets, 见 paper_spec outcome
更正)。fix(omni-g-zscore-papers-01, 2026-06-11)。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd

PAPER_ID = 'bank_media_disagreement'

# treatment (cross-outlet tone variance) + outcome (Z-score 稳定性) + 标准控制
# 三轨 full-parity (v3.9.0 三轨 ss): full / ctx / ss 三个 treatment 变体并列入表;
# build_summary_table 对缺列/NaN 防御性跳过 — ss (银行+金科同句轨) 在 P4 付费 run
# 前盘上无列, ctx/ss 会被自动略过, 不致整表崩。
_TABLE1_VARIABLES: list[str] = [
    'cross_outlet_tone_variance_full',  # treatment.primary (main_track=_full, V4 R3, 待 M2-M3 新建)
    'cross_outlet_tone_variance_ctx',   # treatment ctx 轨 dual-track robustness (paper_spec alternative)
    'cross_outlet_tone_variance_ss',    # treatment ss 镜像轨 (银行+金科同句, P4 前盘上缺则跳)
    'z_score',                          # outcome.primary (CAR-based Z-score 变体, cf. Laeven-Levine 2009; 与第11篇共享)
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
# Tables 2-5 读取 Stata esttab CSV 输出 (M5 阶段填实)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: 主回归 (cross-outlet disagreement → risk-taking)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(PAPER_ID, 'table2_main.csv', paper_config)
