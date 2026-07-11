---
family_id: F303
columns:
- fin_sent_zh_tone_entropy_ctx
- fin_sent_zh_tone_entropy_full
- fin_sent_zh_tone_entropy_ss
- finbert2_tone_entropy_ctx
- finbert2_tone_entropy_full
- finbert2_tone_entropy_ss
- finbert_cn_tone_entropy_ctx
- finbert_cn_tone_entropy_full
- finbert_cn_tone_entropy_ss
unit: 语调得分 (连续, 约 [-1,1]; 聚合后 bank-year 均值)
formula: BERT 概率列 $0 后处理分布形状测度 (熵/极端占比/偏度/跨模型/年内动态)
producer: pipeline\sentiment\tone_berts.py ; pipeline\panel\codebook.py
upstream: []
citations: []
new_dois: []
---

## CORE

【构念与来源】
骨架占位 — 本节为家族核心长文, 待 WP4 写手按写手输入包三件套 (build/codebook_inputs/F303/ 下 columns.json、source_excerpt.md、citations_pool.md) 撰写。本骨架由 build_codebook_family_map 机械生成, 家族 status=draft, 字数闸与引文闸在 draft 态降级为告警计数。单位初判: 语调得分 (连续, 约 [-1,1]; 聚合后 bank-year 均值)。公式初判见 frontmatter formula 字段, 写手须对 producer 源码逐条校对后改写。

## VAR: fin_sent_zh_tone_entropy_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: fin_sent_zh_tone_entropy_full

【变体差分】
骨架占位 — 本列 tier=core, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: fin_sent_zh_tone_entropy_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert2_tone_entropy_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert2_tone_entropy_full

【变体差分】
骨架占位 — 本列 tier=core, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert2_tone_entropy_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert_cn_tone_entropy_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert_cn_tone_entropy_full

【变体差分】
骨架占位 — 本列 tier=core, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: finbert_cn_tone_entropy_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
