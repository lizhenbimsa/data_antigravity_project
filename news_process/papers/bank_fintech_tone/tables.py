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

import pandas as pd

from news_process.papers._common import (
    PaperConfig,
    get_paper_config,
    load_panel,
    summary_stats,
)


# Bank-FinTech-Tone 主线论文的 Table 1 核心变量集.
# 与 50_robustness_text2vec_stata.do 中 ``ds`` 命令选定的核心变量保持一致。
_TABLE1_VARIABLES: list[str] = [
    # 主关键解释变量 — 媒体语调
    'llm_vote_tone_full',
    'llm_vote_tone_ctx',
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
    # IV (LOO + Bartik)
    'prov_leave1out_tone_full',
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
    pc = paper_config or get_paper_config('bank_fintech_tone')
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config)

    available = [v for v in _TABLE1_VARIABLES if v in panel.columns]
    return summary_stats(panel, variables=available)


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
    pc = paper_config or get_paper_config('bank_fintech_tone')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    table = build_table1(pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')

    if dta_filename:
        from news_process.papers._common import export_dta
        export_dta(table.reset_index(), pc.output_dir / dta_filename)

    return csv_path


__all__ = ['build_table1', 'write_table1']
