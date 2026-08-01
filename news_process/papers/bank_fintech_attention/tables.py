"""news_process.papers.bank_fintech_attention.tables — P2 论文表格生成.

P2 = Bank Fintech Attention — firm-level attention intensity。
锚点更正 (fix(omni-g-papers-misc-09, 2026-06-11)): 主处理 attention_index 是
Fang & Peress (2009 JF) 式 extensive 覆盖加权曝光; Hassan et al. (2019 QJE)
对标仅限归一化度量 (attention_pct/density) 与 ctx 轨 proximity 归因。

Table layout (per plan §5.8.2 / §B.2; fix(omni-g-papers-misc-08, 2026-06-11):
Table 2 baseline 措辞与 frozen spec RR15-1/R8-M03 对齐 — cross-sectional
intensity DiD (TWFE 实现), 非旧称 staggered DiD; csdid 为 T≥3 robustness):
    Table 1: descriptive statistics (attention / outcomes / controls)
    Table 2: main regression (M1→M6 progressive; cross-sectional intensity DiD
             baseline (TWFE) + IV; csdid 仅 T≥3 robustness)
    Table 3: mechanism (attention → ln_fintech_mdna_length → ln_fintech_investment)
    Table 4: heterogeneity (4 bank types × fintech wave + SOE)
    Table 5: advanced robustness (Oster δ + rwolf + Honest DiD + ...)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


# Attention treatment 列 (stage 15_fintech_intensity 衍生) + outcome enrichment 列。
# 三轨 (full/ctx/ss) 平价 (third-track-ss 2026-06-14): attention_index_ss = 银行+金科
# 同句共现轨曝光强度 (content_ss; 标签 "(银行+金科同句)"; 配同句 IV lpeer_attention_iv_ss,
# 与 full/ctx 各自 just-identified 并排, 严禁三轨合成 over-id Hansen J)。ss 列 stage
# 14/21 三轨产出后落盘, 落盘前 build_summary_table(strict=False) 以 NaN 占位行可见保留。
_TABLE1_VARIABLES: list[str] = [
    # P2 处理变量 treatment (依 paper_spec.yaml R36-m01; +ss 同句共现轨)
    'attention_index_full',
    'attention_index_ctx',
    'attention_index_ss',
    'attention_disp_full',
    'attention_pct_full',
    # P2 结果变量 outcome (M0.5.11 财务数据扩充列)
    'ln_fintech_investment',
    'm_and_a_fintech',
    'patent_fintech_count',
    'employee_growth_it',
    # P2 mediator
    'ln_fintech_mdna_length',
    # 银行层面标准控制变量
    'ln_assets',
    'leverage',
    'capital_ratio',
    'npl_ratio',
    'deposit_growth',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    return build_summary_table('bank_fintech_attention', _TABLE1_VARIABLES,
                               paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *, filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    return write_summary_table('bank_fintech_attention', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


# ============================================================================
# Tables 2-5 读取 Stata esttab CSV 输出 (M5/M6 阶段填实)
# ============================================================================


def build_table2_main(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 2: M1→M6 progressive main regression — cross-sectional intensity DiD
    baseline (TWFE via reghdfe) + IV; csdid (Callaway-Sant'Anna) 仅作 T≥3 robustness.

    fix(omni-g-papers-misc-08, 2026-06-11): 旧 docstring 无保留宣称 'staggered DiD
    baseline', 与 frozen spec (RR15-1/R8-M03: baseline=cross_sectional_intensity_did)
    及模板实现 (15_attention_main_regression: M1-M6 全为 reghdfe TWFE, 无 csdid 调用,
    早期试跑 T=2 下 csdid 不可识别) 不符 — 现三层措辞对齐。"""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table2_main.csv', paper_config)


def build_table3_mechanism(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 3: 中介机制 (attention → ln_fintech_mdna_length → ln_fintech_investment).

    Baron-Kenny 1986 中介三步法 + Imai-Keele-Tingley 2010 敏感性分析
    (per §5.5.2 R7-M01/M02)."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table3_mechanism.csv', paper_config)


def build_table4_heterogeneity(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 4: 4 bank types × fintech wave + SOE × non-SOE 异质性."""
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table4_heterogeneity.csv', paper_config)


def build_table5_robustness(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """Table 5: 高阶稳健性 (Oster δ / rwolf / Honest DiD / wild bootstrap / ritest /
    spillover / 样本切割 + 本文专属替代 attention 度量).

    白话: rwolf = Romano-Wolf 多重检验校正 — 同时跑很多个稳健性回归时,
    总会有几个"碰巧"显著, rwolf 把 p 值整体调严, 防止挑出来的显著是运气;
    Oster δ 衡量"还要多大的遗漏变量才能推翻结论"。
    """
    from news_process.papers._common.stata_postprocess import read_paper_esttab
    return read_paper_esttab('bank_fintech_attention', 'table5_robustness.csv', paper_config)
