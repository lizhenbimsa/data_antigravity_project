# 自主研发与外部协同：中国银行金融科技战略中的开放式创新

**Paper ID**: `bank_fintech_collab` (P5)
**状态**: M3 骨架 (M0 G0 spec 已冻结 2026-05-17, manuscript 实施延后到 M5/M6)
**总规划**: B-route 主规划文档 (原 docs/plan/B_route_master_plan_v2.md) 已随 docs/ 目录整体删除 (commit 1698bda5); 当前版本/特性真值以仓库根 CLAUDE.md 顶部 "Current version" 段为准。

---

## 摘要

[M3 阶段填实 ~250 字]

银行的金融科技创新模式——自主研发（内部 R&D）与外部协同（与 fintech 公司 / 科技巨头 / 大学的 joint R&D、并购、战略投资、开放 API、行业联盟）——如何影响其长期能力建设、市场反应与下游 M&A 活动？本研究基于 2007-2024 年 500 家中国商业银行的 40 万条金融科技新闻语料，构造了一个**篇章级二元"创新协作模式"分类（聚合为银行-年外部协同新闻占比 `collab_frac`）**，锚定 Chesbrough (2003) 开放式创新框架与 Laursen & Salter (2006 SMJ) search breadth-depth 分类法。...

---

## 1. 导论

[M3 阶段填实 ~1500 字]

- 研究问题: 银行 fintech 创新的"自主 vs 协同"选择路径与传统制造业 R&D 路径异同
- 文献缺口: 既有文献多以单维度衡量 fintech 创新（量、质、locus），忽视组织来源（open vs closed）
- 本研究贡献: 篇章级二元分类（聚合为银行-年外部协同占比 `collab_frac`）+ 与 P3 (substantiveness) / P4 (locus) 形成 2³=8 cross-tab cells

---

## 2. 理论框架

[M3 阶段填实 ~2000 字]

### 2.1 开放式创新 (Chesbrough 2003)
### 2.2 搜索广度与深度 (Laursen & Salter 2006)
### 2.3 企业间 R&D 伙伴关系 (Hagedoorn 2002)
### 2.4 与 P3 (substantiveness) / P4 (locus) 的概念正交性

三维交叉 2³ = 8 cells（详见本节内联框架说明，M3 阶段补实）：
- 实质性 × 底层技术 × 自主研发 → 真实内部技术能力建设
- 实质性 × 应用场景 × 外部协同 → 生态系统协作（开放 API + 业务侧）
- 象征性 × 外部协同 → 战略合作签署但未执行 (decoupling, Fiss & Zajac 2006 延伸)
- ...（其余 cells 见 §2 内联说明）

---

## 3. 数据与方法

[M3 阶段填实 ~2500 字]

### 3.1 样本
- 40 万条新闻 × 500 家中国商业银行 × 2007-2024 (18 年)
- M0.5 全量重跑后 panel 形状: ~3000-9000 obs × ≤5000 cols

### 3.2 度量：创新协作模式
- LLM 三模型集成（gpt-5.4-nano + gemini-3.1-flash-lite + deepseek-v4-flash）多数投票
- Prompt v8（v7 的 additive supplementation；专属 git tag prompt-v8-supplementation-released 尚未打，当前唯一已打的 prompt tag 是 prompt-v7-released）
- 二元编码: 0 = 自主研发, 1 = 外部协同
- 双轨内 κ ≥ 0.45（与 P3 实质性同阈值，fair-to-moderate；阈值定义见 `pipeline/audit/inter_track_kappa.py::_THRESHOLDS`，依据 Landis & Koch 1977）

### 3.3 被解释变量
- 主: `m_and_a_fintech` (Tonghuashun 数据库金融科技 M&A 事件计数)
- 短期: `car_5day_window` (5 日市场调整 CAR, 中证银行指数 benchmark)
- 次: `r_and_d_intensity`, `patent_fintech_count`, `capex_it`

### 3.4 识别策略
- 基线: long-panel 银行-年双向 FE
- 事件研究: E1（余额宝 2013）/ E3（资管新规 2017）/ E4（蚂蚁 IPO 暂停 2020）

---

## 4. 实证结果

[M5 阶段填实 ~2500 字; 主回归 Table 2 (M1-M6) + 机制 Table 3 + 异质性 Table 4]

---

## 5. 稳健性

[M6 阶段填实 ~1500 字; Table 5 进阶稳健性 battery]

---

## 6. 讨论

[M6 阶段填实 ~1500 字]

- 机制解释: 开放式创新对 fintech 银行的边际收益取决于业务侧 vs 技术侧
- 管理实务启示
- 局限: 二元 proxy 的信息损失（Chesbrough/L&S spectrum nature；详见本稿末局限性声明）

---

## 7. 结论

[M6 阶段填实 ~500 字]

---

## 参考文献

[M3/M6 阶段累积, 共用 §2.3 anchor 15 + paper-specific 衍生 15-25]

- Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* HBS Press.
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms. *Strategic Management Journal*, 27(2), 131-150.
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492.
- Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.
- [...]

---

## 局限性声明 (Pre-registration β supplementation)

本研究采用二元分类（自主研发 vs 外部协同）作为 Chesbrough 开放式创新连续 spectrum 与 Laursen & Salter 连续搜索广度-深度的离散 proxy。二元度量压缩了关于伙伴强度、伙伴类型、合作范围的信息，未来研究可拓展为多类（如 M&A vs 战略投资 vs 开放 API vs 行业联盟）。

本研究使用的 LLM 分类 prompt 模板（prompt v8）是预注册的 v7 prompt（git tag `prompt-v7-released`）的**纯增量补充（additive supplementation）**；v7 中的验证、情感、实质性、位点判定规则完全保留（additive non-revisionary adjustment per Nosek et al. 2018 PNAS）。新增的创新协作模式维度计划在最终 production 重跑后通过 git tag `prompt-v8-supplementation-released` 锚定（该 tag 尚未创建）。
