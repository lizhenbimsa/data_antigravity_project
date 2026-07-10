"""news_process.papers.bank_fintech_tone.tables — 主线论文表格生成.

Phase 3c 交付物 (最小可用集)
---------------------------
- ``Table 1: Summary Statistics`` 描述统计 — 银行年度面板核心变量。

设计原则
--------
- 复用 ``papers/_common/tables.py:summary_stats`` 与 ``export_dta``;
   不在此重复实现 Stata 列名清洗或描述统计逻辑。
- 输出固定到 ``PaperConfig.output_dir``;
   存在性由调用方提前 ``mkdir(parents=True, exist_ok=True)``。
- 变量列表是 *论文专属业务知识*, 因此放在论文包内 (而非 _common)。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from news_process.papers._common import PaperConfig
from news_process.papers._common.tables import build_summary_table, write_summary_table

if TYPE_CHECKING:
    import pandas as pd


# Bank-FinTech-Tone 主线论文的 Table 1 核心变量集.
# 历史上沿用 50_robustness_text2vec_stata.do ``ds`` 变量集 (v3.6.0 主轨切换前);
# fix(omni-g-papers-misc-06, 2026-06-11): 连续分与 IV 三轨 (full/ctx/ss) 全列出。
# full-only gating (2026-06-29): paper_spec.yaml 主回归由 _ctx 切 _full
# (treatment.primary=llm_vote_tone_full), main-full 在前排序; _ctx 降为首要
# robustness 孪生 (仍列出, 盘上已存在且非空)。outcome (2026-06-13 重定位后主因变量 =
# funding_cost 资金成本; car_3day_window_tone_shock 降级上市行扩展) 与金融
# controls 仍待 M0.5.11 enrichment 落盘后增补 (届时在此列表加 funding_cost)。
# 三轨 (full/ctx/ss) 平价 (third-track-ss 2026-06-14): _ss = 银行+金科同句共现轨
# (content_ss; 机械 _ctx→_ss 后缀 swap, 标签 "(银行+金科同句)"); ss 列 stage 21/15
# 三轨产出后落盘, 落盘前 build_summary_table(strict=False) 以 NaN 占位行可见保留
# (golden-safe, 同 funding_cost 待 enrichment 落盘惯例; F4 2026-07-10: 原"同 ft_vol_*"
# 类比已失效 — ft_vol_* 现已实算落值非占位)。⚠ full×ctx×ss 三轨各自 just-identified 并排,
# 严禁混进同一 over-id Hansen J (三轨互为稳健性, 非穷尽工具集)。
_TABLE1_VARIABLES: list[str] = [
    # 主关键解释变量 — 媒体语调 (main = full 轨, full-only gating 2026-06-29; +ss 同句共现轨)
    'llm_vote_tone_full',
    'llm_vote_tone_ctx',
    'llm_vote_tone_ss',
    'llm_vote_cont_full',
    'llm_vote_cont_ctx',
    'llm_vote_cont_ss',
    # 信息环境
    'n_articles',
    'ln_news_coverage',
    'media_breadth_z',
    # 异质性变量
    'fin_media_frac',
    'central_media_frac',
    # 注意力指数 — 比值 (议程份额) + 总量孪生 (extensive 覆盖量, 互为稳健性 2026-06-13;
    # ⚠ F4 据实校正 2026-07-10: ft_vol_yr/ft_vol_prov 已由 attention/volume 实算落真值
    # (盘上 N=220/194 非空, 非 NaN 占位); 原"待 stage 45/46 golden 重生"注释已删, 脚注同步)
    'ft_attn_yr',
    'ft_attn_prov',
    'ft_vol_yr',
    'ft_vol_prov',
    # 战略响应 (auth_sim 嵌入相似度三轨, ss 缺列时 NaN 占位)
    'auth_sim_emb_full',
    'auth_sim_emb_ctx',
    'auth_sim_emb_ss',
    # 经营效益态度投影 (三轨)
    'benefit_mean_full',
    'benefit_mean_ctx',
    'benefit_mean_ss',
    # IV (LOO + Bartik; main-full 在前, full-only gating 2026-06-29; ss 同句工具镜像)
    'prov_leave1out_tone_full',
    'prov_leave1out_tone_ctx',
    'prov_leave1out_tone_ss',
    'bartik_type_iv_full',
    'bartik_type_iv_ctx',
    'bartik_type_iv_ss',
]


def build_table1(paper_config: PaperConfig | None = None) -> pd.DataFrame:
    """生成 Table 1: 主关键变量描述统计.

    Args:
        paper_config:  可选 — 已实例化的 PaperConfig; 否则按 paper_id
                       'bank_fintech_tone' 默认构造。

    Returns:
        以 variable 为 index 的描述统计 DataFrame
        (参见 ``papers/_common/tables.py:summary_stats``)。
    """
    return build_summary_table('bank_fintech_tone', _TABLE1_VARIABLES, paper_config=paper_config)


def write_table1(paper_config: PaperConfig | None = None,
                 *,
                 filename: str = 'table1_summary_stats.csv',
                 dta_filename: str | None = 'table1_summary_stats.dta'
                 ) -> Path:
    """计算 Table 1 并写入 ``paper.output_dir``.

    Args:
        paper_config:  可选 — 已实例化的 PaperConfig。
        filename:      CSV 输出文件名。
        dta_filename:  可选 — 同时写一份 .dta (传 ``None`` 仅写 CSV)。

    Returns:
        CSV 文件路径。
    """
    # fix(toptier-audit D5-3, 2026-06-13): 年档 ft_attn_yr/ft_vol_yr 为 year-level 常量
    # (同年所有 bank 同值), summary_stats 报的是 POOLED SD (仅反映 between-year, T=2),
    # 易被审稿误读为截面离散 → 表尾脚注显式披露 (亦适用其在 year FE 下被吸收, 仅作描述)。
    _footnote = (
        'ft_attn_yr / ft_vol_yr are year-level constants (identical across banks within '
        'a year); their reported SD reflects between-year variation only, not '
        'cross-sectional dispersion (N counts bank-year cells; #distinct values = #years). '
        'These year-tier rows are descriptive; they are absorbed by year fixed effects '
        'and carry no within-estimator identifying variation.'
    )
    return write_summary_table('bank_fintech_tone', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename,
                               footnote=_footnote)


__all__ = ['build_table1', 'write_table1']
