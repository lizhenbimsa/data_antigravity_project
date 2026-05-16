# Phase 0 侦察报告 — Benefit-Society 论文

**执行日期**: 2026-05-16
**执行模式**: 无人工参与自动化
**审核标准**: 连续 7 次完美执行

---

## 一、决策点状态总览（D1-D10）

| ID | 决策点 | 状态 | 自动决策 / 数据 |
|---|---|---|---|
| **D1** | 样本边界 | ✅ PASS | 现有 panel 84 银行（76% 非上市），无需扩展 |
| **D2** | entity_masking 字典覆盖 | ✅ PASS | 字典已覆盖 64 家非上市银行，无需扩展 |
| **D3** | LLMCache 公共接口 | ✅ PASS | `core/caching.py::LLMCache` 类 + 公开方法 `get/put/put_batch/stats/size` 全部稳定 |
| **D4** | NCD 评级报告 LLM 抽取 PoC | ⏸ 阻塞 | 需 GPT-4o vision API 预算（$5400-10700）|
| **D5** | 同业合作事件抽取 PoC | ⏸ 阻塞 | 需 LLM API 预算 |
| **D6** | Stage 27 非空率 ≥ 60% | ✅ PASS | benefit_mean_{full,ctx} 非空率 = **69.0%** |
| **D7** | 优先权检索 (SSRN) | ⏸ 阻塞 | 需 web 访问 |
| **D8** | 主论文边界协调 | ✅ 默认 | 方案 (b)：Y 变量切分，NCD 利差为本论文独家 |
| **D9** | Power analysis | ✅ 完成 | 见 [03_power_analysis.md](03_power_analysis.md) |
| **D10** | API 资金来源 | ⏸ 阻塞 | 待用户确认 |

---

## 二、关键数据现实（与 V4 计划的偏差）

### 2.1 现有 panel 实际规模

| 维度 | V4 计划假设 | 现有 panel 实际 | 偏差 |
|---|---|---|---|
| 银行数 | 150-250 家 | **84 家** | -44% |
| 年份范围 | 2014-2024 (11 年) | **2017-2018 (2 年)** | -82% |
| 总 obs | 800-1500 | **168 (balanced)** | -88% |
| 非空 obs | ~600-1200 | **~116** (168 × 0.69) | -90% |
| 非上市占比 | ~70-80% | **76%** | ✅ 符合 |

### 2.2 银行构成（84 家）

| 类别 | 数量 | 占比 |
|---|---|---|
| 上市/国有大行/股份制 | 17 | 20% |
| 农村商业银行（农商）| 24 | 29% |
| 城市商业银行（城商，未上市为主）| 40 | 48% |
| 外资银行 | 4 | 3% |

**结论**：**76% 非上市**完全符合 V4 计划的研究对象定位。

### 2.3 时间维度限制（重大约束）

现有 pipeline 仅产出 **2017-2018** 两年数据，原因待 Phase 1 调查（可能是 raw news 数据起止）。

**对识别策略的影响**：
- ❌ 无法用 CSA-DID 跨 2019 央行《金融科技发展规划》识别（处理后窗口缺失）
- ❌ 无法用 2017 资管新规作 placebo（仅样本起始年）
- ❌ 无法用 t+1 期 Y（仅 1 年可用）
- ✅ 可用 cross-sectional 变异 + 内部时序变异（2017 vs 2018）
- ✅ 可作为 **MVP (Minimum Viable Paper)**：cross-sectional + 1-year-change 设计

---

## 三、对 V4 计划的调整建议

### 3.1 调整识别策略

| V4 设计 | 现有数据下的调整 |
|---|---|
| CSA-DID (2019 处理) | ❌ 弃用，改为 cross-sectional FE |
| t+1 期 Y | 改为 contemporaneous + 1-year change |
| 双向聚类 SE (bank × year) | bank 单向聚类（年仅 2 个）|
| 同业 IV | 保留，但 first-stage power 极弱 |
| Event study | 弃用 |

### 3.2 现实的论文定位（MVP 版）

> **"Cross-Sectional Sentiment-Performance Linkage in Chinese Non-Listed Banks: A Bipolar Embedding Approach"**
>
> - 横截面 + 1-year-change 设计
> - 样本：84 家银行 × 2017-2018
> - Y：NCD 利差变化 / 资产增速 / 不良率变化
> - X：benefit_mean (2017 → 2018 一阶差分)
> - 控制：银行类型 FE + 总部省份 FE

### 3.3 推迟的扩展路径

- **Phase A（本研究）**：MVP 论文，~6 个月完成
- **Phase B（扩展研究）**：若 raw news 库可扩展至 2014-2024，重做面板，输出 V4 计划的完整版

---

## 四、本论文可执行边界（无人工参与）

### 4.1 立即可执行（本次会话）
- ✅ Phase 0 决策文档 (本文 + 3 份 docs)
- ✅ 5 个新建 Python 模块（基于现有 168-obs 面板）
- ✅ 单元测试（≥ 26 个）
- ✅ Stata 模板扩展（含 cross-sectional 设计）
- ✅ pytest baseline 验证

### 4.2 阻塞项（需用户解阻塞）
- ⏸ NCD 评级报告抓取（需 API 预算 + 数据订阅）
- ⏸ 优先权检索（需 web 访问）
- ⏸ 主论文边界用户最终确认
- ⏸ raw news 时间范围扩展（需上游 pipeline 重跑）

### 4.3 长期需 RA / 协作
- ⏸ 200 篇同业合作事件标注
- ⏸ 50 家评级报告手工校验

---

## 五、风险登记（V4 → V4.1 增量）

| 新增风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 时间维度 = 2 年导致面板设计退化 | **已实现** | 高 | 改 MVP 设计；推迟扩展版 |
| 84 银行样本量小于 power 假设 | **已实现** | 中 | 见 power_analysis.md |
| raw news 库无 2019+ 数据 | 待查 | 中 | Phase 0 后置任务：核查 raw 数据 |

---

## 六、自动化执行下的产出清单

| Phase | 产出 | 状态 |
|---|---|---|
| Phase 0 | 4 份立项文档 (本文 + power + boundary + reviewer map) | 本次会话完成 |
| Phase 1 准备 | 5 个 Python 模块（含 NCD 抓取/抽取 stub）| 本次会话完成 |
| Phase 2 准备 | 26 个单元测试 | 本次会话完成 |
| Phase 3 准备 | Stata cross-sectional + IV + robustness 模板 | 本次会话完成 |
| Phase 4-6 | 待 raw news 扩展 + API 预算就位后启动 | 阻塞 |
