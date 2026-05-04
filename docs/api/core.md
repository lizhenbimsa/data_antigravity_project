# `news_process.core` — 共享内核 API

`core` 是整个流水线的共享基础设施层，由 v2.0 重构期间从 `utils/` 演化而来，
现已成为所有 pipeline / validation / papers 模块的**唯一**依赖入口。

```{eval-rst}
.. autosummary::

   news_process.core.config
   news_process.core.logging
   news_process.core.parallel
   news_process.core.reporting
   news_process.core.stage
   news_process.core.dag
   news_process.core.locking
   news_process.core.caching
   news_process.core.quality
   news_process.core.schemas
   news_process.core.text.ahocorasick
   news_process.core.text.canonicalization
   news_process.core.text.entity_context
```

## 模块速查

| 模块 | 关键 API | 用途 |
|---|---|---|
| `core.config` | `load_config()` | YAML 7 域聚合 + .env 解析 + prompt 内联 |
| `core.logging` | `setup_logging()`, `log_stage_summary()`, `get_run_id()` | 多进程隔离日志，按 `NEWS_PROCESS_RUN_ID` 分目录 |
| `core.parallel` | `parallel_apply()` | joblib / ProcessPoolExecutor 包装 |
| `core.reporting` | `save_dataset()`, `safe_save_preview_csv()`, `generate_pipeline_summary()` | parquet / csv / dta 持久化 |
| `core.stage` | `run_stage()` | 子进程隔离的 stage 执行器 |
| `core.dag` | `StageSpec`, `STAGES_MAIN`, `STAGES_VALIDATION`, `filter_enabled()` | 声明式 DAG，单源真值 |
| `core.locking` | `PipelineLock` | 跨平台文件锁（Windows / POSIX） |
| `core.caching` | `LLMCache` | LLM 请求级 SQLite 缓存 |
| `core.quality` | 数据质量校验工具 | 列完整性 / 类型 / 范围检查 |
| `core.schemas` | `OUTPUT_REGISTRY`, `get_stage_outputs()` | stage → 输出 parquet 文件名映射 |
| `core.text.ahocorasick` | `load_bank_names()`, `analyze_bank_matches()` 等 | Aho-Corasick 多模式串匹配 |
| `core.text.canonicalization` | `canonicalize_topic()` | 文本规范化 |
| `core.text.entity_context` | `extract_entity_context()`, `get_target_aliases()` | 实体特异性上下文片段提取 |
