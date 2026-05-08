"""news_process.papers.benefit_society — 衍生论文 1.

研究主题
--------
Benefit-Society — 经营效益态度投影 (Operating Benefit Sentiment Projection).
衍生自 ``pipeline/features/benefit_society.py`` (原 27_audit_benefit_society.py),
学术依据 Jha, Liu & Manela 2026 RFS §1.3.2 — *Does Finance Benefit Society?*

核心被解释变量
--------------
- ``benefit_mean_full``       : 银行年度对经营效益态度均值 (Full 轨)
- ``benefit_pos_frac_full``   : 正向态度占比
- ``benefit_neg_frac_full``   : 负向态度占比

非代码资产
----------
- ``papers_assets/benefit_society/{do,output,drafts}/``
- Phase 4a 已迁入: ``token_hidden_regression.do`` (Distel 2026 + Jha-Liu-Manela 2026 双层回归)
"""

PAPER_ID = 'benefit_society'
__all__ = ['PAPER_ID']
