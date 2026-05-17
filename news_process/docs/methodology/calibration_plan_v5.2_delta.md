# Calibration Plan v5.2 Delta (Incremental over v5.1 frozen)

> **状态**: 待启动 (v5.1 G1 fail 解封后一并落地; git tag `calibration-plan-v5.2-released` 在 v3.4.0 PR-A 合并后创建)
> **基线**: [calibration_plan_v5.1.md](calibration_plan_v5.1.md) git tag `calibration-plan-v5.1-frozen` 永不删除
> **触发**: v3.4.0 第三维度 `innovation_collab_mode` 加入, 分层抽样从 5 strata → 9 strata
> **决策来源**: User Q-C (2026-05-17 plan mode) 锁定 `n=450 / 3 raters / 9 strata`

---

## §1. 增量范围

### 1.1 v5.1 不变内容 (保留)

- 温度缩放 (Guo et al. 2017 ICML) + isotonic 回归 calibrator 数学框架
- OOF / Production 路由 (`StratifiedGroupKFold(5)`, bank-level stratification)
- 32 测试 invariant + golden snapshot 框架
- Logprob verification PoC (gpt54nano N=2000 Spearman ρ 决策规则)

### 1.2 v5.2 新增内容

- **分层抽样从 5 strata → 9 strata** (substantiveness × locus × collab_mode = 2³ + null + 边界 = ~9)
- **n_sample 从 248 → 450** (per Q-C user 锁定; 每层 ~50 obs ≈ 原 v5.1 power 水平)
- **3 raters × 450 = 1,350 标注总量** (≈ 原 744 的 1.8 倍)
- **κ / α 计算扩展到第 3 维度** (collab_mode 单独 / 三维联合)

---

## §2. 新分层抽样设计

### 2.1 9 strata 定义

| Stratum | substantiveness | locus | collab_mode | 目标 n |
|---|---|---|---|---|
| S1 | 实质性 | 底层技术 | 自主研发 | 50 |
| S2 | 实质性 | 底层技术 | 外部协同 | 50 |
| S3 | 实质性 | 应用场景 | 自主研发 | 50 |
| S4 | 实质性 | 应用场景 | 外部协同 | 50 |
| S5 | 象征性 | 底层技术 | 自主研发 | 50 |
| S6 | 象征性 | 底层技术 | 外部协同 | 50 |
| S7 | 象征性 | 应用场景 | 自主研发 | 50 |
| S8 | 象征性 | 应用场景 | 外部协同 | 50 |
| S9 | null/边界 (含跨 stratum 难判) | - | - | 50 |
| **合计** | - | - | - | **450** |

### 2.2 抽样脚本

`scripts/migrate/manual_validation_sampling.py` (Plan R3-8 列为需更新): 
- 第 54-80 行从 4 strata 改 8 strata 分层
- 第 150 行 column whitelist 加入 `'innovation_collab_mode'`
- backfill 逻辑保留 (各层不足 50 时从邻近层借)

---

## §3. Inter-rater Reliability Formula 重写

### 3.1 v5.1 (2 维度) → v5.2 (3 维度)

**单维度 κ / α 计算** (维持 v5.1 Cohen's κ + Krippendorff's α):
- `κ_substantiveness` (3 raters)
- `κ_locus` (3 raters)
- `κ_collab_mode` (3 raters, v3.4.0 新增)

**三维联合 κ** (新增): 
- 概念上将三维度视为复合标签 (e.g., "实质性-底层技术-自主研发"), 8 个可能值
- Fleiss' κ for 3+ raters with categorical multi-class labels
- 期望阈值: 三维联合 κ ≥ 0.40 (fair, accounting for chance agreement over 8 classes; per Landis & Koch 1977 conservative)

### 3.2 接受门槛

| Metric | Threshold | Reference |
|---|---|---|
| κ_substantiveness | ≥ 0.45 | Landis & Koch 1977 fair-to-moderate |
| κ_locus | ≥ 0.50 | Landis & Koch 1977 moderate |
| κ_collab_mode (v3.4.0) | ≥ 0.45 | mirrors substantiveness (Chesbrough framework 实务难判类似 W&Z) |
| α_substantiveness | ≥ 0.667 | Krippendorff conservative |
| α_locus | ≥ 0.667 | 同上 |
| α_collab_mode (v3.4.0) | ≥ 0.667 | 同上 |
| 联合 κ (3 dim, Fleiss') | ≥ 0.40 | conservative for 8-class |

---

## §4. v5.1 G1 fail 状态与 v5.2 衔接

v5.1 当前 G1 fail (标注列 `32_human_samples.xlsx` 为空，用户未完成人工标注)。v5.2 衔接策略:

1. **v5.1 frozen 永久保留**: `calibration-plan-v5.1-frozen` git tag 不删, 历史 baseline 可追溯
2. **v5.2 不重启 v5.1 标注**: 用户直接以 v5.2 设计 (9 strata × 50 obs × 3 raters = 1,350 标注) 开始
3. **v5.2 acceptance gate G1.5**: 标注完成后通过 9 strata 内部一致性 + κ 阈值检查

---

## §5. Power 计算重新审定

### 5.1 v5.1 设计 (5 strata × 50 obs × 3 raters)

- 总标注: 744 (原文档 248 obs × 3 raters)
- Per-stratum power: 50 obs 可检出 κ ≥ 0.45 (Sim & Wright 2005 sample size for κ)

### 5.2 v5.2 设计 (9 strata × 50 obs × 3 raters)

- 总标注: 1,350
- Per-stratum power: 维持 50 obs / stratum, power 等同 v5.1
- 新增 stratum (S5-S9) 因极端 base-rate skew (e.g., 97% substantive × 3% symbolic) 可能 oversample 困难; backfill 逻辑保留

### 5.3 v5.2 风险

- **极端 cell 不足**: S6 (象征性 × 底层技术 × 外部协同) 可能 < 30 obs (per base-rate prior); 若发生需在 limitations 中说明
- **rater fatigue**: 1,350 / 3 raters = 450 per rater (≈ 6h × 3 sessions); v5.1 是 248 / 3 ≈ 83 per rater. 需评估 inter-session fatigue 效应

---

## §6. 实施时间线

- **M5.2.4** (M0.5 stage 21 完成后): 抽样脚本生成 450 obs
- **M5.2.5**: 3 raters 平行标注 (≈ 2 周 wall-time)
- **M5.2.6**: κ / α 计算 + acceptance gate
- **M5.3** (本 PR 不阻塞): v5.1 calibrator 重新 fit 加入 collab_mode 第三维度

---

## §7. 与 v3.4.0 PR-A 的解耦

本 PR 仅落地 v5.2 delta **文档骨架**, 不强制启动 v5.2 标注。理由:
- v5.2 标注依赖 M0.5 stage 21 实跑 (LLM API 调用)
- M0.5 是独立 milestone (12 wk wall-time, $5,000 LLM cap)
- v3.4.0 工程契约 PR 不阻塞 M0.5

实际 v5.2 启动时机: M0.5 完成 + user 解封 v5.1 G1 fail 状态 + 同意 1,350 标注成本。
