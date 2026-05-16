"""news_process.papers.bank_fintech_substance — P3 B-route paper.

研究主题
--------
Bank Fintech Substance — 银行 fintech 战略宣告的"实质性 vs 象征性"差异
(W&Z 1994/1998 ASQ + Fiss-Zajac 2006 AMJ + Westphal-Zajac 2001).

核心被解释变量 (dual outcome per spec):
- ``long_run_roa_change_3yr``           : t+3 ROA forward change (long-run reversal)
- ``car_3day_window_fintech_announcement`` : short-run market reaction

核心处理变量:
- ``innovation_substantiveness_full``   : pipeline v3.2.0 实测列名
- ``innovation_substantiveness_ctx``    : context-conditional 轨
- ``substantive_minus_symbolic_gap``    : derived = full - (1 - full) ∈ {-1, +1}

Identification: long_panel within-bank within-year (无 IV; cross-sectional intensity DiD
替代 IV for E3 资管新规事件).

Investment outlet cascade (per spec sequential_resubmission):
    SMJ (main) → AMJ → ASQ (cascade 终点); 任一阶段 reject 后可改写为
    JFE corp finance disclosure quality 框架的独立论文 (salvage path).

Spec: ``papers/bank_fintech_substance/paper_spec.yaml`` (M0 G0 frozen).
"""

PAPER_ID = 'bank_fintech_substance'
__all__ = ['PAPER_ID']
