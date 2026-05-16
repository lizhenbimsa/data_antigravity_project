# Pre-Analysis Plan (PAP) — Benefit-Society 论文 v1 草案

> **状态**: 草案 v1，待 D8/D10 用户确认后定稿并 OSF 注册
> **依据**: Olken (2015) JEP "Promises and Perils of Pre-Analysis Plans"
> **MVP 范围**: 84 银行 × 2017-2018 = 116 有效 obs

---

## 1. Research Question

中国非上市中小商业银行的媒体语调（金融科技/数字化转型经营效益态度）是否预测同期及次期的经营结果？

---

## 2. Hypotheses (Pre-Registered)

**H1 (主假设)**: 正向 benefit_mean → 更低 NCD 利差
- β < 0，p < 0.10（双尾，由 power 限制放宽至 0.10）

**H2**: 正向 benefit_mean → 更高资产增速
- β > 0，p < 0.10

**H3**: Full 与 Ctx 双轨系数同号
- |β_full − β_ctx| / mean(|β|) < 0.50

**H4 (机制)**: 4 维度子指数中至少 2 个 (core_op / growth) 显著
- 同号 p < 0.10

---

## 3. Sample (Pre-Registered)

- **总体**: 84 家银行（来源：[40_panel_yearly.parquet](../../../data/processed/40_panel_yearly.parquet)）
- **筛选**: benefit_mean_full notna；2017-2018 完整覆盖
- **最终 n**: 预计 ≈ 116 obs（取决于其他变量 notna）

---

## 4. Main Specification (Pre-Registered)

$$Y_{i,t} = \beta \cdot \text{benefit\_mean\_full}_{i,t} + \gamma X_{i,t} + \alpha_{\text{type}(i)} + \delta_t + \varepsilon_{i,t}$$

**控制变量** $X$（顺序固定）:
1. ln(总资产_t)
2. CAR 资本充足率
3. 贷存比
4. ln(成立年限)
5. ln(年度文章数+1) 媒体覆盖度

**FE**:
- 银行类型 FE（国有 / 股份制 / 城商 / 农商 / 外资 = 5 类）
- 年 FE（2017 / 2018）
- ❌ **不**加银行 FE（与类型 FE 共线 + 仅 2 年无识别力）
- 总部省份 FE（如自由度允许）

**标准误**: bank 单向聚类（年仅 2 个，双向聚类不稳定）

---

## 5. Robustness Battery (Pre-Registered)

11 项 robustness（按 reviewer_response_map 对应）:

| # | 内容 | 接受标准 |
|---|---|---|
| R1 | Leave-one-pair-out 锚点（10×重做）| 主 β 95% CI 重叠 |
| R2 | Embedding 替换（text2vec/BGE/OpenAI）| β 同号 |
| R3 | 媒体来源切分（官方 vs 市场化）| β 同号 |
| R4 | 报道密度门槛（≥1 / ≥3 / ≥5）| β 同号 |
| R5 | Bayesian shrinkage 测度 | β 同号 |
| R6 | Ctx 轨主回归 | β 同号 |
| R7 | 控制 ln(文章数) | β 同号 |
| R8 | 1-year-change 设计 (Δbenefit → ΔY) | β 同号 |
| R9 | 弃用控制变量稳健性（minimal control set）| β 同号 |
| R10 | 极端值（1% winsorize vs 不处理）| β 同号 |
| R11 | 评级数据 vs 年报 vs 监管三角 | 不一致率 < 5% |

**收敛标准**: 任 ≥7 项 robustness 与主回归 β 同号同显著（α=0.10）

---

## 6. Heterogeneity (Pre-Registered)

仅 2 个维度（power 不允许更多）:
- (a) 银行类型: 城商 vs 农商
- (b) 总部地区: 东 vs 中西

---

## 7. Mechanism (Pre-Registered)

- 4 维度子指数: core_op / growth / resource / compliance（dimension_analysis.py）
- 报告每个子指数对 NCD 利差的边际效应

---

## 8. Stopping Rules

- 若主回归 β 在 α=0.10 下不显著 → **不放弃**, 报告效应大小 + 95% CI 作"null result"
- 若 11 项 robustness 中 < 5 项同号 → 重新检视测度有效性, 不强推

---

## 9. Deviations from PAP

任何偏离本 PAP 的分析必须在论文 §"Deviations from Pre-Analysis Plan" 中明确披露:
- 偏离原因
- 偏离前后的结果对比
- 是否影响主结论

---

## 10. Pre-Registration

- 预计提交平台: OSF (Open Science Framework)
- 预计 DOI 获取时间: Phase 0 完成后 Week 5
- 注册版本号 v1.0，后续修订均通过 OSF 版本追溯系统

---

## 11. Authorship & Conflicts

- Authors: [待填]
- Funding: [待填]
- Conflicts of Interest: 无
- Data Access: 内部研究使用慧科 + 公开 NCD 数据，符合数据订阅条款

---

**PAP 终态**: 待 Phase 0 D8（边界）+ D10（资金）用户确认后，本草案可升级为 v1.0 正式版并提交 OSF。
