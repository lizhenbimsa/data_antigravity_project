# Phase A — 数据状态盘点报告

> ⚠ **2026-08-02 状态订正 (聚合中转平台迁移 yunwu.ai → OpenLux)**: 本文成文时,
> 本项目的 OpenAI / Google 两家 LLM 与 `_lg` 嵌入孪生轨经 **yunwu.ai 聚合代理**
> (`https://yunwu.ai/v1`; 环境变量 `YUNWU_API_KEY` / `YUNWU_FULL_KEY`) 路由。
> **2026-08-02 起全项目已迁移至 OpenLux 聚合代理** (`https://api.openlux.ai/v1`;
> 变量更名为 `OPENLUX_API_KEY` / `OPENLUX_FULL_KEY`)。DeepSeek 直连
> (`api.deepseek.com`) 与硅基流动嵌入主轨 (`api.siliconflow.cn`) **不受影响**。
> 下文一切 `yunwu` / `YUNWU_*` 表述均为**成文当时**的事实记录 (含当时对该端点的
> 实测探针结果与授权清单), **不代表当前状态**; 保留原文以维持取证链完整。
> ⚠ 迁移**不改变任何既有数值**: LLM/嵌入缓存键 = (模型名, prompt 文本,
> prompt 版本, temperature), **不含端点地址** (`core/caching.py::_make_key`),
> 故 `_llm_cache.db` 既有条目在迁移后仍逐位命中, 离线 `$0` 复现不受影响。


**生成时间**：2026-05-05 ~01:05 (UTC+8)
**目的**：在任何修改之前确认数据/缓存当前状态，决定 [E1] 内部细节。

---

## A.1 关键时间戳对比

| 文件 | mtime | 说明 |
|---|---|---|
| `news_process/config/sentiment.yaml` | **2026-05-05 00:42:44** | 用户最近一次手动改 model_name |
| `news_process/data/processed/21_tone_llms.parquet` | **2026-03-28 21:01** | Stage 21 上次产出 |
| `news_process/data/processed/21_tone_llms_full.parquet` | **2026-03-28 21:01** | 同上 |
| `news_process/data/processed/22_words_tone.parquet` | 2026-04-29 16:51 | 词典法 (无 LLM 依赖) |
| `news_process/data/processed/23_bert_tone.parquet` | 2026-04-29 16:59 | BERT (无 LLM 依赖) |
| `news_process/data/processed/40_panel_yearly.parquet` | 2026-05-01 09:35 | 已用旧 21 输出生成 |

**结论**：`21_tone_llms*.parquet` 显著早于 `sentiment.yaml`（mtime 差 38 天） → **数据陈旧**，与 v5 锁定的「象限 ④（重跑+重命名）」假设一致。

---

## A.2 LLM 缓存盘点

```
sqlite3 _llm_cache.db "SELECT model_id, COUNT(*) FROM llm_cache GROUP BY model_id;"
text-embedding-3-small|10
```

**结论**：缓存中**仅含 embedding 条目**（10 条），没有任何 LLM 推理缓存条目。意味着：
- 历史 `gpt-5.4-nano` / `glm-4.5-flash` / `claude4h` 的旧响应**没有被持久化**（可能被早期清空过）
- v5 §C.3 的「DELETE WHERE model_id IN (...)」步骤在本环境**实际为空操作**（无遗留条目可删）
- 重跑 Stage 21 将从零生成全部 LLM 响应，token 成本最高路径

---

## A.3 21_tone_llms.parquet schema

```
=== 列前缀计数 (62 总列数) ===
gpt54nano: 8     # *_verified_full/ctx, *_sentiment_full/ctx, *_verification_confidence_full/ctx, *_sentiment_confidence_full/ctx
gemini3111: 8      # 同上
claude4h: 8     # 同上 ← v5 [E1] 必须重命名为 deepseek4f
fintech: 7
llm: 6
target: 3
其他元数据列若干 (docid/pubcode/co_mentioned_banks/content/category 等)
```

**结论**：当前 schema 尚未携带 v5 [E1] 引入的新元数据列：
- `n_valid_votes_*` / `n_verifying_votes_*`（缺）
- `llm_call_failure_*` / `llm_undefined_*`（缺）
- `{slot}_actual_model_name` / `{slot}_actual_model_call_time`（缺，N8）
- `agree_rate_v_*` / `agree_rate_s_*`（当前可能只有合并版 `agree_rate_*`）

---

## A.4 stage 21 历史日志

最近一次 stage 21 日志位于 `news_process/logs/runs/test_dag_consistency/21_tone_llms.log`，内容仅 2 行：

```
2026-05-05 00:08:52 - 21_tone_llms - PID:15964 - INFO - LLM 推理参数: temperature=0.0, seed=42, force_json=True, models=3, concurrency=300
2026-05-05 00:08:52 - 21_tone_llms - PID:15964 - INFO - Logit-to-Score 概率映射: enabled=True
```

由于 `21_tone_llms.parquet` 自 03-28 以来未变（mtime 一致），可推断该 dag_consistency 测试**仅完成前置初始化即提前退出**（很可能因为已有 cache/parquet 走增量路径未真正调用 LLM）。

---

## A.5 .env API key 状态

```
GPT5NANO_API_KEY=sk-djQ...C359
GEMINI3_API_KEY =sk-djQ...C359   ← 与 GPT5NANO_API_KEY 完全相同
CLAUDE4H_API_KEY=sk-djQ...C359   ← 同上
EMBEDDING_API_KEY=sk-djQ...C359  ← 同上
```

**结论**：4 个 var 实际是同一 yunwu key 复用 4 次。N7（统一 `YUNWU_API_KEY`）合理且零风险。

---

## A.6 决策影响

| 决策项 | 数据证据导出的结论 |
|---|---|
| 象限锁定 | **象限 ④（重跑 + 重命名）确认成立**：数据陈旧 + 命名清洁度优先 |
| LLM 重跑 token 成本 | **最高估算**（缓存无任何 LLM 响应可命中） |
| 缓存清理 | 实际为空操作（无 `gpt-5.4-nano` / `glm-4.5-flash` 条目） |
| 当前 schema 与 v5 [E1] 新增列差异 | 完全缺失 → 必须通过 [E1] 添加 |
| .env 兼容路径 | 添加 `YUNWU_API_KEY` + `DEEPSEEK4F_API_KEY` 别名 |

---

**Phase A 验收**：✓ 报告生成；不修改任何 .py / .yaml / .json / .parquet 文件。
