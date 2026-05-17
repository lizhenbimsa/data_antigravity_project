"""news_process.papers.bank_fintech_collab — P5 B-route paper (v3.4.0 epoch 5).

研究主题
--------
Bank Fintech Collab Mode — 银行 fintech 创新的"自主研发 vs 外部协同"差异
(Chesbrough 2003 Open Innovation + Laursen & Salter 2006 SMJ search breadth & depth
+ Hagedoorn 2002 Research Policy inter-firm R&D partnerships).

核心被解释变量 (proposed primary; M5 阶段 user 校正):
- ``m_and_a_fintech``               : 外部协同的直接 outcome (M&A 事件计数)
- ``r_and_d_intensity``             : 自主研发的强度信号 (alternative outcome)
- ``car_5day_window``               : 短期市场反应 (与 P4 同窗口)

核心处理变量:
- ``innovation_collab_mode_full``   : pipeline v3.4.0 实测列名 (Chesbrough 2003)
- ``innovation_collab_mode_ctx``    : context-conditional 轨 (Hassan 2019 QJE 同构)
- ``independent_minus_collab_gap``  : derived = full - (1 - full) ∈ {-1, +1}

Identification: long_panel within-bank within-year; E1/E3/E4 events applicable
(per master plan §5.7.2 v2.56 epoch 5 audit 决策).

Investment outlet cascade (mirrors P3 sequential_resubmission):
    SMJ (main) → AMJ → ASQ (cascade 终点).

Pre-registration: prompt-v8-supplementation-released git tag (v8 = v7 严格超集,
additive supplementation per Nosek et al. 2018 PNAS).

Spec: ``papers/bank_fintech_collab/paper_spec.yaml`` (M0 G0 frozen post epoch 5 audit).
"""

PAPER_ID = 'bank_fintech_collab'
__all__ = ['PAPER_ID']
