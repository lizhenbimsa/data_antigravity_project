"""news_process.papers.bank_fintech_tone — 主线论文.

研究主题
--------
Bank-FinTech-Tone: 媒体对金融科技的情感倾向如何影响银行行为
(presented as the canonical "main pipeline" of the project — drives
the entire 00→11→12→14→15→21/22/23→24→45→51 stage chain).

包结构
------
- ``dag.py``      : 论文专属 DAG (Phase 3c: 等同 ``core.dag.STAGES_MAIN``)
- ``analysis.py`` : ``main()`` CLI 入口 — 调 ``run_pipeline()`` + 论文表/图
- ``tables.py``   : 论文 Table 1/2/... 生成器
- ``figures.py``  : 论文 Figure 1/2/... 生成器

非代码资产
----------
- ``papers_assets/bank_fintech_tone/do/``      : Stata .do 脚本
   (Phase 3 暂留 ``news_process/stata/`` 集中目录, 按文件归属逐步迁移;
    本论文目前确认归属: ``50_robustness_text2vec_stata.do``。其余
    .do 文件归属待 Phase 3d 衍生论文落地后定。)
- ``papers_assets/bank_fintech_tone/output/``  : 表/图最终成品
- ``papers_assets/bank_fintech_tone/drafts/``  : 手稿/送审稿
"""

from news_process.papers.bank_fintech_tone import dag

PAPER_ID = 'bank_fintech_tone'
__all__ = ['dag', 'PAPER_ID']
