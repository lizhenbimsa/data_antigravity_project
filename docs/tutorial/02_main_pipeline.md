# 跑主流水线

本教程指导你用 22 GB 真实数据跑通主流水线（`STAGES_MAIN` 11 阶段），从
原始 XLSX → Bank-Year 平衡面板 + 伪造检验对照变量。

```{warning}
**资源要求**：~16 GB RAM 峰值，~50 GB 磁盘，~6-12 小时跑时（取决于
LLM API 配额与并发数），需要可用的 GPT5/Gemini/Claude API 密钥。
```

## 1. 前置条件检查

```bash
# 1. 已完成 [快速上手](01_quickstart.md) 全部 5 步
# 2. 原始数据落盘到 news_process/data_excel/<group>/<year>.xlsx
ls news_process/data_excel/ | head

# 3. .env 已填入 4 个 LLM API 密钥（GPT5NANO / GEMINI3 / CLAUDE4H / EMBEDDING）
grep -c "^[A-Z_]*_API_KEY=." news_process/.env  # 期望: 4

# 4. config/ 中 7 个域 YAML 都齐全
ls news_process/config/*.yaml
```

## 2. 主流水线 DAG（11 阶段）

```{mermaid}
graph LR
    S00[阶段 00<br/>preprocess<br/>10000s 超时]
    S11[阶段 11<br/>news_bank<br/>3600s]
    S12[阶段 12<br/>news_fintech<br/>3600s]
    S14[阶段 14<br/>fintech_intensity<br/>3600s]
    S15[阶段 15<br/>policy_alignment<br/>7200s]
    S21[阶段 21<br/>tone_llms<br/>3600s]
    S22[阶段 22<br/>tone_words<br/>3600s]
    S23[阶段 23<br/>tone_berts<br/>3600s]
    S24[阶段 24<br/>herd_decay<br/>3600s]
    S45[阶段 40-45<br/>panel build<br/>7200s]
    S51[阶段 51<br/>falsification<br/>3600s]

    S00 --> S11 --> S12 --> S14 --> S15
    S15 --> S21
    S15 -.->|enabled_methods| S22
    S15 -.->|enabled_methods| S23
    S21 --> S24
    S24 --> S45
    S45 --> S51
```

**config-conditional 启用**（`sentiment_analysis.enabled_methods`）：
* `tone_llms`: 控制 21 启用
* `tone_words`: 控制 22 启用
* `tone_berts`: 控制 23 启用

默认配置全启用三种方法以做三角验证。

## 3. 启动

```bash
# 在 repo root：
.venv/Scripts/python.exe news_process/run_pipeline_function.py
```

或等价：

```bash
.venv/Scripts/python.exe -m news_process.run_pipeline_function
```

```{tip}
**断点续跑**：每阶段输出独立 parquet 文件到 `data/processed/NN_xxx.parquet`，
若中途失败，**修复问题后重跑** — orchestrator 会预清理失败阶段输出，但
不会重做已成功的前置阶段（增量跑由文件存在性自动判断）。

如果想强制全量重跑，删 `data/processed/*.parquet` 即可。
```

## 4. 实时监控

主流水线分两个通道输出：

* **控制台**：实时日志 + 阶段开始/结束时间戳 + 内存占用
* **文件日志**：`logs/runs/<run_id>/<stage>.log`（每个 stage 一个文件）

`run_id` 由 `run_pipeline_function.py:_generate_run_id()` 生成，格式：
`YYYYMMDDTHHMMSSZ-<hostname>-<pid>`，例如 `20260504T080000Z-DESKTOP-1234`。

子进程通过 `NEWS_PROCESS_RUN_ID` 环境变量继承同一个 run_id，所有 stage
日志聚合到同一个 `logs/runs/<run_id>/` 目录。

```bash
# 实时 tail 当前 stage 日志（Linux/macOS）
tail -f news_process/logs/runs/$(ls -t news_process/logs/runs/ | head -1)/*.log

# Windows PowerShell
Get-Content news_process/logs/runs/$(ls news_process/logs/runs/ | sort -Descending | select -First 1)/*.log -Wait
```

## 5. 输出 inventory

完成后 `data/processed/` 应包含：

| 阶段 | 输出文件 | 大小（参考） |
|---|---|---|
| 00 | `00_preprocessing.parquet` + `.csv` | ~6.9 GB + ~17 MB |
| 11 | `11_bank_news.parquet` + `.csv` | ~2.4 GB + ~20 MB |
| 12 | `12_fintech_news.parquet` + `.csv` | ~674 MB + ~37 MB |
| 12 | `12_fintech_news_full.parquet` + `.csv` | ~2.4 GB + ~21 MB |
| 14 | `14_fintech_intensity.parquet` + `.csv` | ~676 MB + ~37 MB |
| 15 | `15_article_alignment.parquet` | varies |
| 21 | `21_tone_llms.parquet` + `_full.parquet` | ~3 MB + ~4 MB |
| 22 | `22_words_tone.parquet` + `22_idf_weights.json` | ~3 MB + ~700 KB |
| 23 | `23_bert_tone.parquet` | ~3 MB |
| 24 | `24_herd_decay.parquet` | ~3 MB |
| 40-45 | `40_panel_yearly.{parquet,csv,dta}` | ~1.5 MB |
| 40-45 | `40_article_bank_level.{parquet,csv}` | ~4 MB |
| 40-45 | `40_attn_index_{year,province_year,city_year}.parquet` | varies |
| 51 | `51_panel_with_controls.{parquet,csv,dta}` | ~1.5 MB |
| 51 | `51_falsification_diagnostics.csv` | < 5 KB |

**注**：parquet 是主要存储格式；csv 是 LLM/人工抽样可读副本；dta 是
Stata 输入格式。

## 6. 验证可复现性

跑完后用 golden snapshot 测试：

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/integration/test_panel_reproducibility.py -v
```

如果有 hash drift，输出会精确指出哪个 stage 的哪些列不匹配，可对照
[Rollback 锚点指南](../reference/rollback_anchors.md) 回到稳定版本。

## 7. 故障排查

| 症状 | 可能原因 | 处理 |
|---|---|---|
| 阶段 00 OOM | 内存不足，~10 GB peak | 关闭其他大型应用，或切到 32 GB+ 机器 |
| 阶段 21 大量 timeout | LLM API 限流 | 调低 `tone_llm_processing.max_concurrency`（默认 300）|
| 阶段 21 缓存失效 | `data/processed/_llm_cache.db` 损坏 | 删除该文件，会自动重建（损失已缓存请求 vs LLM 重跑成本） |
| 阶段 23 BERT OOM | 模型显存不足 | 切到 CPU 推理：set `tone_bert_processing.device: cpu` |
| `PipelineLock` 提示并发 | 上次 crash 留下 lock | 删 `data/processed/.pipeline.lock` 或参 [PipelineLock 文档](../api/core.md) |

## 8. 下一步

* 跑了主流水线后，做 [验证矩阵](03_validation.md)（稳健性检验）
* 进入 [多论文工作流](04_multi_paper.md)（生成 5 篇论文的表/图）
* 用面板做 [Stata 计量分析](05_stata_integration.md)
