# news_process 文档索引（v3.7.0 + v2.3 / 最近 git tag v3.6.0, 2026-05-18）

## 项目说明（三层）

- [项目说明_顶刊版.md](项目说明_顶刊版.md) — 顶刊投稿版（722 行；面向 editor / referee，20-90 分钟阅读）
- [项目说明书_简明版.md](项目说明书_简明版.md) — 简明导览（面向合作者 / 复现协作者）
- [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) — 综合白皮书（6,543 行 / ≥ 50,000 字；面向内部博士生 / co-author / 长期维护者）

## 项目级执行计划

- [plan/B_route_master_plan_v2.md](plan/B_route_master_plan_v2.md) — 主线 Bank-FinTech 论文端到端执行计划 v2.56（含 M-1 数据现状审计 → M8 投稿；G-1..G8 acceptance gates；R1-R12 风险登记表；C1-C4 应急方案）。注：v3.4 之后多论文 portfolio 已扩展至 9 paper，本 master plan 锚定 epoch 4，9 paper 完整分布详见 CLAUDE.md §Multi-Paper Support。

## 设计与实施指南

- [配置文件拆分实施指南.md](配置文件拆分实施指南.md) — Phase 4d 七域 YAML split 设计
- [错误处理和重试机制实施指南.md](错误处理和重试机制实施指南.md) — LLM retry / backoff 设计
- [数据版本控制和血缘追踪实施指南.md](数据版本控制和血缘追踪实施指南.md) — caching SCHEMA_VERSION + prompt_version 设计
- [policy_llm_undefined.md](policy_llm_undefined.md) — LLM 三模型平局/无效响应处理事实政策（NaN-as-not-positive）

## 数据与产物

- [PANEL_DATA_INFO.md](PANEL_DATA_INFO.md) — 银行年度面板数据说明
- [所有parquet保存点汇总.md](所有parquet保存点汇总.md) — 各 stage parquet 产物对照
- [CODEBOOK_AUDIT_REPORT.md](CODEBOOK_AUDIT_REPORT.md) — 变量字典审计

## Stata 集成

- [STATA_INDICATORS_CATALOG.md](STATA_INDICATORS_CATALOG.md) — Stata 列指标完整分类说明（v1.5 / 3,085 行 / 5 轮评审终版，2026-05-19 起为当前权威）
- [STATA_INTEGRATION_SUMMARY.md](STATA_INTEGRATION_SUMMARY.md) — Stata 集成总览

## 测试

- [测试覆盖率指南.md](测试覆盖率指南.md) — pytest --cov 本地与 CI 使用指南

## 运维

- [bash_tool_audit.md](bash_tool_audit.md) — Windows / PowerShell 适配记录

## 历史归档

- v2.1.0 及更早的审计与计划报告已不再维护; 如需溯源, 请通过 git log / git show 在历史 commit 中查找 (相关目录已在重构中删除)。
