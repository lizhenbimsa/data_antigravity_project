"""news_process.papers.bank_fintech_collab.tables — P5 论文表格 (provisional 2026-06-01).

Table 1 (descriptive stats) 走 _common 通用 summary builder, 与其它 paper 对称。
fix(omni-g-papers-misc-03, 2026-06-11): 撤回旧 "即开即用" 声称 — treatment 行已改
panel 真实物化列 (collab_frac/indep_frac), 但金融 enrichment 列 (M&A/R&D/CAR/controls)
待 M0.5.11 落盘前为可见 NaN 占位行 (非即开即用), 已经 CSV 脚注披露。
Tables 2-5 (主回归 M1→M6 / 机制 / 异质性 / 稳健性) 为 esttab reader 占位, 待 M5/M6
跑通 Stata 后填实 (Chesbrough 2003 Open Innovation; Laursen & Salter 2006 SMJ 27:131-150)。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd

PAPER_ID = 'bank_fintech_collab'

# fix(omni-g-papers-misc-03/-11, 2026-06-11): treatment 行改 panel 真实物化的
# bank-year 编码 (collab_frac/indep_frac + ctx 轨 *_cm) — 旧清单的
# innovation_collab_mode_full/_ctx 是文章级中文字符串 (自主研发/外部协同), 永远
# 不会以该名出现在 bank-year panel (结构性错名 → Table 1 全 NaN)。金融
# enrichment 列 (待 M0.5.11) 保留为可见 NaN 占位行 (F16 政策) 并经 CSV 脚注披露。
_TABLE1_VARIABLES: list[str] = [
    'collab_frac',                     # treatment — 外部协同新闻占比 (full 轨, Chesbrough 2003)
    'indep_frac',                      # 自主研发新闻占比 (full 轨)
    'collab_frac_cm',                  # ctx 轨 (entity-context 分类)
    'indep_frac_cm',                   # ctx 轨
    'm_and_a_fintech',                 # outcome.primary (外部协同直接 outcome; M0.5.11 待落盘)
    'r_and_d_intensity',               # secondary (自主研发强度; M0.5.11 待落盘)
    'car_5day_window',                 # short-run 市场反应 (M0.5.11 待落盘)
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]

# Table 1 CSV 脚注 (存在性披露; fix(omni-g-papers-misc-03))
_TABLE1_FOOTNOTE = (
    "Treatment rows use panel-materialized bank-year shares "
    "(collab_frac/indep_frac, full track; *_cm = ctx track). "
    "Outcome/control rows pending M0.5.11 financial enrichment appear as "
    "NaN placeholder rows until materialized (existence-checked at build time)."
)


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table(PAPER_ID, _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table(PAPER_ID, _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename,
                               footnote=_TABLE1_FOOTNOTE)


# ============================================================================
# Tables 2-5 读取 Stata esttab CSV 输出 (M5/M6 阶段填实)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 递进式主回归 (collab_mode → M&A / R&D).

    白话: M1→M6 指主回归表的 6 列从左到右逐列加控制变量/固定效应,
    让读者看到系数随控制加严是否稳定; 本函数只负责把 Stata esttab
    导出的 CSV 读回 DataFrame, 回归本身在 .do 模板里跑。
    """
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab(PAPER_ID, 'table2_main.csv', paper_config)
