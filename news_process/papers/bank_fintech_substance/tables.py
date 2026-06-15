"""news_process.papers.bank_fintech_substance.tables — P3 论文表格生成.

P3 = Bank Fintech Substance (W&Z 1994 ASQ substantive vs symbolic).

表格布局 (per plan §5.5.2 + R11-m02 注: P3 16_mechanism 用 dual outcome 而非 mediation):
    Table 1: 描述统计 (substantiveness / dual outcome / controls)
    Table 2: 主回归 (M1→M6 递进控制; long_panel within-bank within-year)
    Table 3: dual outcome (短期 CAR + 长期 ROA 反转, W&Z 1994 实证机制)
    Table 4: 异质性 (4 bank types × SOE × fintech wave × capital quartile)
    Table 5: 高阶稳健性 (含 alternative substantiveness track full vs ctx)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


# fix(omni-g-papers-misc-03/-11, 2026-06-11): treatment 行改 panel 真实物化的
# bank-year 编码 (sub_frac/symb_frac + ctx 轨 *_sc) — 旧清单的
# innovation_substantiveness_full/_ctx 是文章级中文字符串, 永远不会以该名出现在
# bank-year panel (结构性错名 → Table 1 全 NaN)。金融 enrichment 列 (待 M0.5.11)
# 保留为可见 NaN 占位行 (F16 政策) 并经 CSV 脚注披露。
# 三轨 (full/ctx/ss) 平价 (third-track-ss 2026-06-14): _ss = 银行+金科同句共现轨
# (encode.py 镜像 _sc×_ctx 块产 sub_frac_ss/symb_frac_ss, 分母 = n_articles_llm_valid_ss);
# ss 列 stage 21 三轨产出后落盘, 落盘前 build_summary_table(strict=False) 以 NaN 占位行
# 可见保留 (golden-safe)。⚠ ss 是同句共现情感/属性轨, 与 full/ctx 互为稳健性。
_TABLE1_VARIABLES: list[str] = [
    # P3 treatment — panel 真实列 (实质性/象征性新闻占比, full 轨 + ctx 轨 *_sc + ss 轨 *_ss)
    'sub_frac',
    'symb_frac',
    'sub_frac_sc',
    'symb_frac_sc',
    'sub_frac_ss',
    'symb_frac_ss',
    # P3 outcome 族 (M0.5.11 enrichment 待落盘; 2026-06-13 重定位: 主因变量 =
    # cost_income_ratio_change_3yr 效率试金石, long_run_roa 降级 secondary,
    # CAR 降级上市行扩展)
    'cost_income_ratio_change_3yr',
    'misconduct_penalty_count',
    'long_run_roa_change_3yr',
    'car_3day_window_fintech_announcement',
    # P3 secondary outcomes (M0.5.11 enrichment 待落盘)
    'ceo_turnover_2yr',
    'executive_pay_change',
    'board_change',
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
    "(sub_frac/symb_frac, full track; *_sc = ctx track; "
    "*_ss = bank+fintech same-sentence co-occurrence track). "
    "Outcome/control rows pending M0.5.11 financial enrichment appear as "
    "NaN placeholder rows until materialized (existence-checked at build time)."
)


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_substance', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_substance', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename,
                               footnote=_TABLE1_FOOTNOTE)


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 递进式主回归 (long_panel within-bank within-year)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table2_main.csv', paper_config)


def build_table3_dual_outcome(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: Dual outcome (CAR + long-run ROA reversal) — W&Z 1994 实证机制.

    NB: P3 不用经典 Baron-Kenny mediation, 而用 dual outcome regression (R11-m02)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table3_dual_outcome.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 4 bank types × SOE × wave × capital_ratio 四分位异质性."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: 高阶稳健性 + 替代 substantiveness 轨 (full / ctx / ss 三轨)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_substance', 'table5_robustness.csv', paper_config)
