# LLM 三模型平局/无效响应处理政策

**状态**：事实政策 (2026-05-13 锁定为 Wave 1 T1.5 落地)
**作用域**：[pipeline/sentiment/tone_llms.py](../pipeline/sentiment/tone_llms.py) 输出 → [pipeline/panel/runner.py](../pipeline/panel/runner.py) 消费链路
**适用方法学**：v6/F2 三模型多数投票 + 反向验证 (verification track)

---

## 1. 政策（一句话）

**NaN-as-not-positive**：`llm_undefined=1` 的样本在 `is_positive` / `is_negative` /
逐 LLM `_score` 等 nullable Int8 字段中表示为 NaN，所有下游消费点都用
`fillna(0) == 1`（或 `> 0` / `< 0`）的严格比较，使 NaN 行**在每种二值标记中均为 False**——既不算正面，也不算负面，也不算中性。

## 2. 实现链路

| 阶段 | 位置 | 行为 |
|---|---|---|
| 产生 None | [pipeline/sentiment/tone_llms.py:648](../pipeline/sentiment/tone_llms.py#L648) | `majority_vote_sentiment()` 平局时返回 `None` 而非默认"中性" 0（2026-05-14 重构：内部委托给 `majority_vote_categorical` at [L585](../pipeline/sentiment/tone_llms.py#L585)，行为不变） |
| 同上 | [pipeline/sentiment/tone_llms.py:783](../pipeline/sentiment/tone_llms.py#L783) | 文档化：标记 `llm_undefined=1`；下游 panel 层把 None 映射为 NaN |
| 写出标记列 | [pipeline/sentiment/tone_llms.py:1091-1092](../pipeline/sentiment/tone_llms.py#L1091) | 全样本初始化 `llm_undefined_full = 0` / `llm_undefined_ctx = 0` |
| 同上 | [pipeline/sentiment/tone_llms.py:1310-1311](../pipeline/sentiment/tone_llms.py#L1310) | 实际填入 `undefined_full_arr` / `undefined_ctx_arr` |
| panel 消费 | [pipeline/panel/runner.py:354-359](../pipeline/panel/runner.py#L354) | NaN 视为非正面：`(df[pos_col].fillna(0) == 1) & _is_symb` |
| 同上 (各方法) | [pipeline/panel/runner.py:361-440](../pipeline/panel/runner.py#L361) | 方法 A/A2/B/D/D2/E/E2/F 全部沿用 `fillna(0) == 1` 或 `> 0`/`< 0` 模式 |

## 3. 为什么不用 "neutral = 0" 或 "drop"

- **"neutral"**：会让平局样本在"中性"统计中堆积，扭曲 Hassan (2019) 风格的 tone 指标分布
- **"drop"**：每篇文章在 4 个轨道（full/ctx/title × 验证/未验证）上独立判定 undefined；
  drop 会导致不同轨道样本量不同，破坏面板对齐
- **"NaN-as-not-positive"**：使 undefined 样本对所有二值标记零贡献，对连续 tone 平均通过
  `mean(skipna=True)` 自然剔除——既保留样本观测又不引入伪信号

## 4. 变更政策的影响范围（**至少 6 处消费点**）

若未来需切换策略，须同步修改以下文件中所有 `fillna(0) ==` / `fillna(0) >` /
`fillna(0) <` 模式：

- [pipeline/panel/runner.py](../pipeline/panel/runner.py)（约 20+ 处洗稿率前置标记）
- [pipeline/panel/aggregation.py](../pipeline/panel/aggregation.py)（bank-year 聚合）
- [pipeline/audit/stata_audit.py:305](../pipeline/audit/stata_audit.py#L305), [:320-321](../pipeline/audit/stata_audit.py#L320)
- [pipeline/falsification/controls.py:600](../pipeline/falsification/controls.py#L600)

变更必须配套：
1. **Bump** [scripts/migrate/generate_golden_snapshot.py](../scripts/migrate/generate_golden_snapshot.py) 的 schema_version
2. **重生成** [tests/fixtures/golden_panel_v0.json](../tests/fixtures/golden_panel_v0.json)
3. **更新本文档**的 §1 政策声明
4. **PR description** 注明合作者评审

## 5. 验证

[tests/integration/test_panel_reproducibility.py](../tests/integration/test_panel_reproducibility.py) 通过比对
`column_hashes` 保证 panel 输出与 golden 一致；任何对 undefined 处理的偏离都会触发
该测试红——是政策不变性的护栏。
