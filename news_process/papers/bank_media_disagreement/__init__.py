"""news_process.papers.bank_media_disagreement — 第 10 篇 (M0 立项中).

研究主题
--------
Bank-Media-Disagreement: 媒体观点分歧 (cross-outlet tone variance) 对银行风险承担
(Z-score / NPL formation / RWA ratio) 的因果效应。
(注: stage 49 已删除, 三件套 outcome 目前仅为 Stata 模板中的变量名占位,
待银行财务面板数据接入后才可计算。)

锚定文献
--------
- Diether, Malloy & Scherbina (2002 JF) — disagreement → 横截面收益经典
- Cookson & Niessner (2020 JF)《Why Don't We Agree?》— 信息源分歧
  (本 paper outlet-level 类比; 勘误: 旧注释误标 RFS, 实为 JF)
- Bushman & Williams (2012 JAE) — bank info environment → risk-taking
- Acharya, Anginer & Warburton (2016 RFS) — implicit guarantee 框架 (V4 必加)

治理路径 (DC1 path B)
--------------------
SSRN preprint: true (影响力优先)
G3 治理解锁: false (放弃 _ctx main, 走 _full + SSRN 路线)
Main track: _full
Pre-registration: OSF required pre-M5
LLM response archive: required (DC3)

包结构
------
- ``paper_spec.yaml`` : 立项 spec
- ``stata_templates/`` + ``replication/`` : 已就位
- ``analysis.py``     : 已创建 (2026-06-01 provisional 接线; main CLI 入口 + STAGES 引用)
- ``tables.py``       : 已创建 (provisional 占位骨架, 主回归 esttab 待 onboarding 填实)
- ``figures.py``      : 已创建 (provisional 占位骨架)

Audit 历史
----------
V1 (58 finding) → V2 (90 finding) → V3 (5 DC) → V4 (白话回归) → DC1 决策 (2026-05-18)
"""

PAPER_ID = 'bank_media_disagreement'
__all__ = ['PAPER_ID']
