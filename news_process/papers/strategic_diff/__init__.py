"""news_process.papers.strategic_diff — 衍生论文 4.

研究主题
--------
Strategic-Diff — 银行金融科技战略差异度 (Strategic Differentiation).
衍生自 ``pipeline/features/strategic_diff.py`` (原 25_panel_strategic_diff.py),
学术依据 Guzman & Li 2023 (Strategic Differentiation), Hoberg & Phillips 2016
(TNIC industry classification), 谢佳松 2025 (行业重心法).

核心被解释变量
--------------
- ``strat_diff_n3..n7``    : N-邻 TF-IDF 字符差异度
- ``strat_sim_max``         : 最大同业相似度
- ``strat_fluidity``        : 产品市场流动性 (Hoberg-Phillips fluidity)
- ``strat_diff_n5_lda``     : LDA + JSD 主题差异度
- ``strat_diff_n5_emb``     : Embedding 差异度
- ``centroid_diff_*``       : 全行业重心距离 (谢佳松 2025)

非代码资产
----------
- ``papers_assets/strategic_diff/{do,output,drafts}/``
- Phase 4a 已迁入:
  - ``strategic_differentiation.do`` (Guzman-Li 2023 + Hoberg-Phillips 2016 战略差异度回归)
  - ``text_coherence.do`` (欧阳-胡 2024 + Hoberg-Phillips 2016 相邻期文本连贯性)
"""

PAPER_ID = 'strategic_diff'
__all__ = ['PAPER_ID']
