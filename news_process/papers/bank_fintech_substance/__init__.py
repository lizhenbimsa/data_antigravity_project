"""news_process.papers.bank_fintech_substance — P3 B-route paper.

研究主题
--------
Bank Fintech Substance — 银行 fintech 战略宣告的"实质性 vs 象征性"差异
(W&Z 1994/1998 ASQ + Fiss-Zajac 2006 AMJ + Westphal-Zajac 2001).

核心被解释变量 (2026-06-13 重定位, dual outcome per spec):
- ``cost_income_ratio_change_3yr`` : 主因变量 — 3 年前向成本收入比变化 (W&Z 效率试金石)
- ``long_run_roa_change_3yr``      : secondary (long-run ROA reversal)
- ``car_3day_window_fintech_announcement`` : short-run market reaction (上市行扩展)

核心处理变量 (fix(omni-g-papers-misc-11): 改指 bank-year panel 真实物化列 — 旧 innovation_substantiveness_full 是文章级中文字符串, 在 panel 0 命中):
- ``sub_frac``         : 实质性新闻占比 (full 轨, W&Z substantive share; spec.treatment.primary)
- ``sub_frac_sc``      : context-conditional 轨 (ctx)
- ``substantive_minus_symbolic_gap`` : derived (Stata 01_data_prep)

Identification: long_panel within-bank within-year (无 IV; cross-sectional intensity DiD
替代 IV for E3 资管新规事件).

Investment outlet cascade (per spec sequential_resubmission):
    SMJ (main) → AMJ → ASQ (cascade 终点); 任一阶段 reject 后可改写为
    JFE corp finance disclosure quality 框架的独立论文 (salvage path).

Spec: ``papers/bank_fintech_substance/paper_spec.yaml`` (M0 G0 frozen).
"""

PAPER_ID = 'bank_fintech_substance'
__all__ = ['PAPER_ID']
