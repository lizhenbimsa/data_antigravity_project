---
family_id: F412
columns:
- loughran_advonly_tone_ctx
- loughran_advonly_tone_full
- loughran_advonly_tone_ss
- loughran_degadv_tone_ctx
- loughran_degadv_tone_full
- loughran_degadv_tone_ss
- loughran_degonly_tone_ctx
- loughran_degonly_tone_full
- loughran_degonly_tone_ss
- loughran_negadv_tone_ctx
- loughran_negadv_tone_full
- loughran_negadv_tone_ss
- loughran_negdeg_tone_ctx
- loughran_negdeg_tone_full
- loughran_negdeg_tone_ss
- loughran_negonly_tone_ctx
- loughran_negonly_tone_full
- loughran_negonly_tone_ss
- loughran_raw_tone_ctx
- loughran_raw_tone_full
- loughran_raw_tone_ss
unit: 语调得分 (连续, 约 [-1,1]; 聚合后 bank-year 均值)
formula: 状态机 Σ|final| 自归一化词典语调 (指定语言学规则子集) → bank-year 均值
producer: pipeline\sentiment\tone_words.py ; pipeline\panel\export.py
upstream: []
citations: []
new_dois: []
---

## CORE

【构念与来源】
骨架占位 — 本节为家族核心长文, 待 WP4 写手按写手输入包三件套 (build/codebook_inputs/F412/ 下 columns.json、source_excerpt.md、citations_pool.md) 撰写。本骨架由 build_codebook_family_map 机械生成, 家族 status=draft, 字数闸与引文闸在 draft 态降级为告警计数。单位初判: 语调得分 (连续, 约 [-1,1]; 聚合后 bank-year 均值)。公式初判见 frontmatter formula 字段, 写手须对 producer 源码逐条校对后改写。

## VAR: loughran_advonly_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_advonly_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_advonly_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degadv_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degadv_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degadv_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degonly_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degonly_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_degonly_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negadv_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negadv_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negadv_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negdeg_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negdeg_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negdeg_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negonly_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negonly_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_negonly_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_raw_tone_ctx

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_raw_tone_full

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

## VAR: loughran_raw_tone_ss

【变体差分】
骨架占位 — 本列 tier=standard, 待写手写清该列区别于家族 canonical 的精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
