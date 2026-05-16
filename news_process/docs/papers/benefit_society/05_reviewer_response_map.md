# 审稿人挑战预判 + 稳健性映射

针对 MVP 版本（n=116，2017-2018）

---

## 10 类预期审稿挑战

| # | 审稿挑战 | 应对稳健性表 | 论文章节 |
|---|---|---|---|
| **1** | "Why bipolar embedding over Loughran-McDonald dictionary?" | T2 三角对照（Stage 21/22/23 vs 27） | §3 Measurement |
| **2** | "Anchor design is arbitrary — could you pick anchors to get the result you want?" | R1 leave-one-pair-out (10×) | §5 Robustness |
| **3** | "Sample size too small (n=116)" | Power analysis 透明披露 + 报告 95% CI + Bayesian shrinkage | §4 Identification + §6 |
| **4** | "Reverse causality — good banks get good media coverage" | 1-year-change 设计 + IV (lagged industry sentiment) | §4 Identification |
| **5** | "Only 2 years — no DID identification possible" | 公开承认；MVP 定位 + 未来扩展计划 | §6 Discussion |
| **6** | "Embedding model dependency" | R2 三模型替换（text2vec / BGE / OpenAI text-embedding-3） | §5 |
| **7** | "Chinese media is censored — sentiment may not reflect reality" | R3 媒体来源切分（官方 vs 市场化） | §5 |
| **8** | "Why focus on non-listed banks?" | §1 introduction motivation: 文献空白 + 中小银行系统性风险 | §1 |
| **9** | "NCD spread数据可信度（评级机构内生）" | R11 三角验证（评级报告 vs 年报 vs 监管） | §5 |
| **10** | "Full vs Ctx distinction not meaningful" | Phase 2 Full-Ctx placebo + 共线性诊断（ρ < 0.95） | §3.2 |

---

## 关键应对脚本

### 挑战 #3 (Power) 应对
```stata
// papers/_common/stata_templates/benefit_society/15_table6_effect_size.do.tmpl
// 报告 β + 95% CI + 标准化系数 + Bayesian posterior
```

### 挑战 #4 (Reverse causality) 应对
**Planned module (not yet built)**: `iv_construction` (path: papers/benefit\_society/iv\_construction.py)
- 待 Phase 0 D8 (主论文边界) + 数据范围扩展后构建
- 设计: lagged industry sentiment as IV, first-stage F report
- 当前替代: 1-year-change 设计 (在 PAP §5 R8 列入)

### 挑战 #5 (2 年限制) 应对
- 论文 §6 Discussion 明确声明 MVP 限制
- 附录 A "未来研究扩展版" 列出 raw news 扩展计划

---

## 元审稿挑战

| 元挑战 | 应对 |
|---|---|
| "Why publish this MVP instead of waiting for full sample?" | Working paper 优先权 + 方法论贡献独立 |
| "Are you cherry-picking specifications?" | PAP 注册（OSF） + 全部 robustness 公开 |
| "Replication" | Stage 27 输出 + 5 个新建脚本 + 26 单元测试 + Stata templates 全部开源 |
