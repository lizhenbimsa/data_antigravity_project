# 论文边界协调 — benefit_society vs bank_fintech_tone

**D8 自动决策**：方案 (b) — Y 变量切分

---

## 1. 边界冲突源

`news_process/papers/` 下 5 篇论文模块共用同一 pipeline 产出（[40_panel_yearly.parquet](../../../data/processed/40_panel_yearly.parquet)）。

主要冲突在 [bank_fintech_tone](../../../papers/bank_fintech_tone/)（主论文）与 [benefit_society](../../../papers/benefit_society/)（本论文）之间。

---

## 2. 两套划分方案

### 方案 (a)：样本切分
- 主论文：上市银行子样本（17 家 × 2 年 = 34 obs）
- 本论文：非上市子样本（64 家 × 2 年 = 128 obs）
- **问题**：主论文样本过小（34 obs）→ 不可行

### 方案 (b)：Y 变量切分 ✅ **采用**
- 主论文：sentiment → bank tone/intensity 综合反应（既有 Y）
- 本论文：sentiment → **NCD 利差 / 资产增速 / 不良率**（非上市经营 Y）
- 两论文**共用 84 银行样本**，X 重叠但 Y 独立

---

## 3. 方案 (b) 实施细节

### 3.1 X 维度分工
- **共同 X**：`benefit_mean_{full,ctx}`（Stage 27 产出）
- **本论文额外 X**：`benefit_{core_op, growth, resource, compliance}` 4 维度子指数（dimension_analysis.py 产出）

### 3.2 Y 维度分工

| Y 类别 | 主论文 (bank_fintech_tone) | 本论文 (benefit_society) |
|---|---|---|
| 媒体反应 | ✅ tone / intensity 综合 | ❌ |
| NCD 利差 | ❌ | ✅ 首要 Y |
| NCD 规模 | ❌ | ✅ |
| 资产增速 | 控制变量 | ✅ Y |
| 不良率 | 控制变量 | ✅ Y |
| 信息科技投入 | ❌ | ✅ 机制 |
| 同业合作事件 | ❌ | ✅ Robustness |

### 3.3 引用关系
- 本论文 **应**引用主论文方法（"Following bank_fintech_tone (Anonymous 2026)..."）
- 本论文 **应**明确声明 X 测度共用，Y 应用不同
- 主论文 **可选**引用本论文作 robustness（待主论文发表时再补）

---

## 4. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 双盲审稿时审稿人识别同作者 | 两论文以不同 first author 投稿 |
| Y 变量定义重叠 | 明确章节"与既有研究的区别"段落 |
| 数据共用合规 | 两 paper 共用 Stage 27 产出，符合 replication 透明原则 |

---

## 5. 待用户确认

- ☐ 用户最终确认方案 (b) 而非 (a)
- ☐ 用户确认两论文投稿先后顺序
- ☐ 用户确认 first author 分配

**默认推进**（无人工参与下）：按方案 (b) 推进所有代码与文档；用户确认后无需修改技术内容。
