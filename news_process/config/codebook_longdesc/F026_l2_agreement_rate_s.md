---
family_id: F026
columns:
- avg_agreement_rate_s_ctx
- avg_agreement_rate_s_full
- avg_agreement_rate_s_ss
unit: 比率/占比 (proportion, [0,1] 或百分比; 待写手按 frontmatter 校准)
formula: '(WP0 初判占位 — 以家族 md frontmatter formula: 为准, 写手对源码校对)'
producer: pipeline\sentiment\tone_llms.py ; pipeline\panel\codebook.py
upstream: []
citations: []
new_dois: []
---

## CORE

【构念与来源】
骨架占位 — 本节为家族核心长文, 待 WP4 写手按写手输入包三件套 (build/codebook_inputs/F026/ 下 columns.json、source_excerpt.md、citations_pool.md) 撰写。本骨架由 build_codebook_family_map 机械生成, 家族 status=draft, 字数闸与引文闸在 draft 态降级为告警计数。单位初判: 比率/占比 (proportion, [0,1] 或百分比; 待写手按 frontmatter 校准)。公式初判见 frontmatter formula 字段, 写手须对 producer 源码逐条校对后改写。

## VAR: avg_agreement_rate_s_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: avg_agreement_rate_s_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: avg_agreement_rate_s_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
