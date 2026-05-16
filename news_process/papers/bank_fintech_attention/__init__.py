"""news_process.papers.bank_fintech_attention — P2 B-route paper.

研究主题
--------
Bank Fintech Attention — 银行 fintech 媒体话题曝光强度 (firm-level attention intensity)
对银行 fintech 战略响应的因果识别.

锚定文献:
    - Hassan, Hollander, van Lent, Tahoun (2019) QJE 134(4) — firm-level political risk exposure
    - Florackis, Louca, Michaely, Weber (2023) RFS 36(1) — cybersecurity exposure
    - Gomber, Kauffman, Parker, Weber (2018) JMIS 35(1) — fintech taxonomy (secondary anchor)

核心被解释变量
--------------
- ``ln_fintech_investment``  : 银行年报 fintech 投入披露 (M0.5.11 CSMAR 衍生)
- ``m_and_a_fintech``        : Tonghuashun M&A 事件
- ``patent_fintech_count``   : IncoPat fintech 专利计数
- ``employee_growth_it``     : CSMAR 员工增长 (IT 板块)

核心处理变量 (stage 14_fintech_intensity 衍生):
- ``attention_index_full`` / ``attention_index_ctx`` /
  ``attention_disp_full`` / ``attention_pct_full``

Identification: staggered DiD (Callaway-Sant'Anna 2021) + leave-one-out peer attention IV /
Bartik IV fallback (per paper_spec.yaml identification.iv).

Spec: ``papers/bank_fintech_attention/paper_spec.yaml`` (M0 G0 frozen).
"""

PAPER_ID = 'bank_fintech_attention'
__all__ = ['PAPER_ID']
