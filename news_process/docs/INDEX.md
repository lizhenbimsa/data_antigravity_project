# news_process 文档索引（v3.2.0）

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

- [STATA_INTEGRATION_SUMMARY.md](STATA_INTEGRATION_SUMMARY.md) — Stata 集成总览
- [STATA_REVIEW_REPORT.md](STATA_REVIEW_REPORT.md) — Stata 代码评审详情
- [STATA_REVIEW_SUMMARY.md](STATA_REVIEW_SUMMARY.md) — Stata 评审摘要

## 测试

- [测试覆盖率指南.md](测试覆盖率指南.md) — pytest --cov 本地与 CI 使用指南
- [测试验证报告.md](测试验证报告.md) — v2.2.0 数据版本控制 + DAG 一致性历史快照（2026-05-09，非最新；当前 baseline 1153 见 CLAUDE.md L16）

## 运维

- [bash_tool_audit.md](bash_tool_audit.md) — Windows / PowerShell 适配记录

## 历史归档

- [archive/](archive/) — v2.1.0 及更早的审计与计划报告，仅供溯源，**不再维护**
