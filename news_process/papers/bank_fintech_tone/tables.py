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
# fix(omni-g-papers-misc-06, 2026-06-11): paper_spec.yaml 主回归 = ctx 轨
# (treatment.primary=llm_vote_tone_ctx), 但连续分与 IV 原仅列 full 轨 —
# 增补 llm_vote_cont_ctx / prov_leave1out_tone_ctx / bartik_type_iv_ctx
# (盘上已存在且非空), main-ctx 在前排序。outcome (2026-06-13 重定位后主因变量 =
# funding_cost 资金成本; car_3day_window_tone_shock 降级上市行扩展) 与金融
# controls 仍待 M0.5.11 enrichment 落盘后增补 (届时在此列表加 funding_cost)。
_TABLE1_VARIABLES: list[str] = [
    # 主关键解释变量 — 媒体语调 (main = ctx 轨, per spec v3.6.0)
    'llm_vote_tone_ctx',
    'llm_vote_tone_full',
    'llm_vote_cont_ctx',
    'llm_vote_cont_full',
    # 信息环境
    'n_articles',
    'ln_news_coverage',
    'media_breadth_z',
    # 异质性变量
    'fin_media_frac',
    'central_media_frac',
    # 注意力指数
    'ft_attn_yr',
    'ft_attn_prov',
    # 战略响应
    'auth_sim_emb_full',
    'auth_sim_emb_ctx',
    # 经营效益态度投影
    'benefit_mean_full',
    'benefit_mean_ctx',
    # IV (LOO + Bartik; main-ctx 在前, fix(omni-g-papers-misc-06))
    'prov_leave1out_tone_ctx',
    'prov_leave1out_tone_full',
    'bartik_type_iv_ctx',
    'bartik_type_iv_full',
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
    return write_summary_table('bank_fintech_tone', _TABLE1_VARIABLES,
                               paper_config=paper_config,
                               filename=filename, dta_filename=dta_filename)


__all__ = ['build_table1', 'write_table1']
