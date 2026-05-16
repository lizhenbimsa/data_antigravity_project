# Pre-Analysis Plan (PAP) — Benefit-Society 论文 v1.0-final

> **状态**: v1.0-final OSF-locked draft (2026-05-16，经 14 轮 audit / 59 finding 收敛)
> **依据**: Olken (2015) JEP "Promises and Perils of Pre-Analysis Plans"
> **样本范围**: 84 中国商业银行 × 2017-2018 = 168 obs (benefit_mean notna ≈ 116)
> **理论锚**: Tetlock 2007 JF + Garcia 2013 JF (media sentiment → firm value) + Jha-Liu-Manela 2026 RFS (bipolar anchor projection) + Westphal & Zajac 2001 ASQ (Token/Hidden 解耦)
> **变更血统**: v1 草案 → v1.0.5 (audit-driven revision) → v1.0-final (OSF-locked)

---

## 1. Research Question

中国商业银行的媒体语调（金融科技/数字化转型经营效益态度）是否预测同期及次期的银行经营结果？

> **审计修订** (DP-7 / F-V2-B1): 原 v1 草案限定"非上市中小商业银行"；实测 panel 84 银行 cohort 包含 12 家上市国有大行（SOE）+ 22 家上市股份制（joint），与"非上市"定义直接冲突。v1.0-final 改为"中国商业银行"全样本叙事，并通过 `is_listed` 异质性分析挽救部分原创新性叙事（DP-9）。

---

## 2. Hypotheses (Pre-Registered)

**H1 (主假设)**: 正向 benefit_mean → 更高 ROA
- β > 0，p < 0.10（双尾，由 power 限制放宽至 0.10）
- 理论锚: Tetlock 2007 JF（媒体悲观 → 公司未来盈利下行）的逆向应用

**H2**: 正向 benefit_mean → 更高 CAR（资本充足率）
- β > 0，p < 0.10
- 解读: 经营效益态度正向反映稳健经营策略，间接预测资本充实

**H3 (双轨一致性)**: Full 与 Ctx 双轨系数同号且量级相当
- 接受标准 (审计修订，F-H5):
  - **符号一致**: `sign(β_full) == sign(β_ctx)` 必须通过
  - **量级一致**: `min(|β_full|, |β_ctx|) / max(|β_full|, |β_ctx|) > 0.5`
- 三维度同时检验 (F-H3):
  - `benefit_mean_{full,ctx}`
  - `benefit_pos_frac_{full,ctx}`
  - `benefit_neg_frac_{full,ctx}`
- 整体接受: 3 维度中 ≥ 2 维度同时满足上述两门
- 推断方法 (F-H4): wild cluster bootstrap (boottest, B=999 reps, cluster=bank_id) 替代 SUEST；理由：reghdfe FWL 估计与 suest 的 e-class 接口不兼容；同时 wild bootstrap 对小簇数 G=84 的偏差更稳健 (Cameron-Miller 2015)

**H4 (机制)**: 4 维度子指数 (core_op / growth / resource / compliance) 中至少 2 个与主回归同号显著
- 同号 p < 0.10
- Family-wise 校正: Romano-Wolf rwolf (F-R5-M2)，控制 H1-H4 + H3-three-tuple = 6 检验家族 FWER ≤ 0.10

---

## 3. Sample (Pre-Registered)

- **总体**: 84 中国商业银行（来源：[40_panel_yearly.parquet](../../../data/processed/40_panel_yearly.parquet)）
- **Cohort lock**: [data/raw/cohort/benefit_society_84banks.csv](../../../data/raw/cohort/benefit_society_84banks.csv) — git committed manifest (DP-8 / F-R6 lineage)
- **bank_type 分布** (6 类，非原 PAP 写的 4 类，F-V2-M2):
  - city: 68, rural: 48, joint: 22, soe: 12, private: 10, foreign: 8
- **筛选**: benefit_mean_full notna；2017-2018 完整覆盖
- **最终 n**: 实测 116 obs（取决于其他变量 notna）

---

## 4. Main Specification (Pre-Registered)

$$\text{ROA}_{i,t} = \beta \cdot \text{benefit\_mean\_full}_{i,t} + \gamma X_{i,t} + \alpha_{\text{type}(i)} + \delta_t + \varepsilon_{i,t}$$

**控制变量** $X$（顺序固定）:
1. ln(总资产_t)
2. CAR 资本充足率
3. 贷存比 (LDR)
4. ln(成立年限)
5. ln(年度文章数+1) 媒体覆盖度

**FE**:
- 银行类型 FE (6 类: soe / joint / city / rural / private / foreign)
- 年 FE (2017 / 2018)
- ❌ **不**加银行 FE（与类型 FE 共线 + 仅 2 年无识别力，F-R5-H2）
- 总部省份 FE（如自由度允许）

**标准误**: bank 单向聚类 + **wild cluster bootstrap (boottest)** for inference (F-R5-H1)
- 理由: G=84 处于小簇边界，asymptotic CRVE 偏差需 wild bootstrap 校正

---

## 5. Robustness Battery (Pre-Registered)

9 项 robustness（v1 草案的 11 项 → v1.0-final 删除 R8 + R11，F-R3-H1）:

| # | 内容 | 接受标准 |
|---|---|---|
| R1 | Leave-one-pair-out 锚点（10×重做）| 主 β 95% CI 重叠 |
| R2 | Embedding 替换（text2vec/BGE/OpenAI）| β 同号 |
| R3 | 媒体来源切分（官方 vs 市场化）| β 同号 |
| R4 | 报道密度门槛（≥1 / ≥3 / ≥5）| β 同号 |
| R5 | Bayesian shrinkage 测度（含 ctx 路径双轨，新加）| β 同号 |
| R6 | Ctx 轨主回归（dual-track 主对比，并入 Table A2） | β 同号 + 量级一致 |
| R7 | 控制 ln(文章数) | β 同号 |
| R9 | 弃用控制变量稳健性（minimal control set）| β 同号 |
| R10 | 极端值（1% winsorize vs 不处理）| β 同号 |

> **已删除** (审计修订):
> - ~~R8 (1-year-change 设计)~~: 2 年面板退化为单 diff (n=84)，power < 0.30 — F-R3-H1
> - ~~R11 (NCD 利差三角)~~: NCD 利差不在 panel，且 DV 已切到 ROA — F-B3 / F-R3-H1

**收敛标准**: 任 ≥6 项 robustness 与主回归 β 同号同显著（α=0.10）

---

## 6. Heterogeneity (Exploratory, F-R3-H2 / F-R5-M1)

> **审计修订**: het 检验标为 **exploratory**（不入 H 系列 hypothesis），限定 2 维度避免 3-way 8-cell n=14 问题。

- (a) `is_listed`: 上市 vs 非上市（含 SOE + 部分 joint 上市股份制）
- (b) `bank_type` 2-level 合并: 全国性大行 (SOE + joint) vs 地方性银行 (city + rural + private + foreign)

**het regression FE**: `absorb(bank_type year)` （**不**用 `absorb(bank_id year)`，F-R5-H2）

---

## 7. Mechanism (Pre-Registered)

- 4 维度子指数: core_op / growth / resource / compliance（[dimension_analysis.py](../../../papers/benefit_society/dimension_analysis.py)）
- 每个子指数同时报告 full + ctx 双轨系数（Panel A: full / Panel B: ctx）
- H4 接受标准：≥ 2/4 维度同号显著（α=0.10）

---

## 8. Stopping Rules

- 若主回归 β 在 α=0.10 下不显著 → **不放弃**, 报告效应大小 + 95% CI 作"null result"
- 若 9 项 robustness 中 < 5 项同号 → 重新检视测度有效性, 不强推
- 若 H3 失败率 > 50% (3 维度中 < 2 维度 sign + ratio 双门) → 回退 stage 21 ctx prompt review

---

## 9. Deviations from PAP

任何偏离本 PAP 的分析必须在论文 §"Deviations from Pre-Analysis Plan" 中明确披露。

### 已知 deviations (v1.0-final 锁定)

1. **Cohort 范围扩展** (DP-7): v1 草案 "非上市中小商业银行" → v1.0-final "中国商业银行 84 家"。理由: 实测 cohort 已含上市国有大行 (12) 与上市股份制 (22)，原叙事与数据不符。

2. **DV 切换** (DP-1.b / F-B3): v1 草案主 DV "NCD 利差" → v1.0-final 主 DV "ROA"。理由: NCD 利差数据需 Wind license，CBIRC + 年报覆盖的 ROA / CAR 是无 license 公开数据替代。

3. **R8 + R11 删除** (F-R3-H1): R8 (1-year-change) 在 2 年面板下退化无 power；R11 (NCD 利差三角) 数据源已不可用。

4. **Dual-track 冗余披露** (F-H2 / F-R4-M1): benefit_mean_full vs benefit_mean_ctx 实测 Pearson ρ = 0.761 (n=116)，接近 _common/20 注释的"双轨冗余阈值 ρ>0.70"。论证为何**仍保留** dual-track：
   - (a) frac 维度 ρ=0.46 < 0.50 — dual-track 真正信息量集中在 pos/neg frac 而非 mean；
   - (b) ctx 是 v3.2.0 R1-A 修复的 prompt-level 安全网，弃用会回退 stage 3 设计；
   - (c) mean 高 ρ 反而**支持** convergent validity — ctx 修复在 benefit 域是 conservative，不引入新偏差；
   - (d) anchor 端在 dual-track 下不变，dual-track 仅捕获 text embedding 端的 ctx 修复效果。

5. **Cluster G=84 小簇推断** (F-R5-H1): main inference via wild cluster bootstrap (boottest, B=999) due to small G.

6. **Heterogeneity → exploratory** (F-R3-H2 / F-R5-M1): het 不入 H 系列，标记 exploratory；2-way 限定。

7. **bank_type 6 类**（F-V2-M2）: panel 实际 6 类 (含 private + foreign)，FE 用全 6 类而非 v1 草案的 4 类。

---

## 10. Pre-Registration

- 提交平台: OSF (Open Science Framework)
- DOI 获取: Phase 0 完成后由用户手动触发 (DP-5)
- 注册版本: **v1.0-final OSF-locked** (F-R7-L1)
- 后续修订: 通过 OSF 版本追溯系统

---

## 11. Authorship & Conflicts & AI Disclosure

- Authors: [待填]
- Funding: [待填]
- Conflicts of Interest: 无
- Data Access:
  - 慧科 (Wisers) news data — 项目订阅协议
  - CBIRC + 年报 ROA/CAR — 公开数据
  - **同时 OSF 发布数据需 license 审查 (P7.0, F-V2-H4)**
- **AI Tooling Disclosure** (F-R9-M1):
  > "Stata template scaffolding, Python module structure, and audit-driven plan revision assisted by Claude Code (Anthropic, Opus 4.7). Substantive analytic decisions, theoretical anchoring, and hypothesis interpretation by the human authors. AI did not generate empirical results."

---

## 12. Audit lineage

本 PAP 经 14 轮独立审计 (R1-R14, 2026-05-16 当日完成) / 59 finding 收敛形成。完整 audit log 见 [07_audit_log.md](./07_audit_log.md)；执行计划见 [08_dual_track_plan_v2.12.md](./08_dual_track_plan_v2.12.md)。

**PAP 终态**: v1.0-final OSF-locked，待 §11 作者 + funding 字段填写后即可 OSF 注册。
