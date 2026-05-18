"""news_process.papers.bank_news_clarity — 第 11 篇 (M0 立项中).

研究主题
--------
Bank-News-Clarity: 媒体报道清晰度 (mean_clarity_score, You 2018 词典) 作为
external information environment quality proxy, 对银行风险承担 (Z-score /
NPL formation / RWA ratio) 的因果效应。

V4 reframe (致命修复)
--------------------
放弃 "clarity = 银行透明度" claim (genre mismatch fatal);
改为 "clarity = external information environment quality" (Bushee 2010 JAR 框架);
词表 validity 跟随 *外部感知者* (储户 / 监管 / 投资者), 非 *作者*.

锚定文献
--------
- Loughran & McDonald (2014 JF) — readability 测量经典
- Bonsall, Leone, Miller & Rennekamp (2017 JAE) — plain English readability
- Bushman & Williams (2012 JAE) — direct anchor: info discretion → bank risk-taking
- Bushee, Core, Guay & Hamm (2010 JAR) — business press as info intermediary (reframe 依据)
- You et al. (2018 hhx055) Panel C/D — 中文清晰度词典 (v3.5.1 已 frozen at D0)

治理路径 (DC1 path C)
--------------------
SSRN preprint: false (No-SSRN, 走 G3 严谨路线)
G3 治理解锁: true (单作者 + No SSRN + 数据授权 三条件解锁)
Main track: _ctx (entity-context, Tetlock 2007 JF + L&M 2016 JAR 现代标准)
Pre-registration: OSF required pre-M5
LLM response archive: required (DC3)

包结构 (M7+ 创建)
----------------
- ``paper_spec.yaml`` : 立项 spec (此模块当前唯一已存在文件)
- ``analysis.py``     : 待 M7 创建
- ``tables.py``       : 待 M7 创建
- ``figures.py``      : 待 M7 创建

Audit 历史
----------
V1 (58 finding) → V2 (90 finding) → V3 (5 DC) → V4 (白话回归 + reframe) → DC1 (2026-05-18)
"""

PAPER_ID = 'bank_news_clarity'
__all__ = ['PAPER_ID']
