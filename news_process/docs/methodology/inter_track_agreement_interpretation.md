# Inter-track Agreement κ 解读指南 (v3.2.0)

> Plan v14 §3.5 P5.1 + §5.2 R5-B 阈值论证。

## 1. 两类 κ 不要混淆

| κ 类型 | 度量什么 | 期望值 | Plan ref |
|---|---|---|---|
| **Inter-track κ** | 同一篇文章 / bank-year 下, full 轨 vs ctx 轨标签一致性 | **0.50-0.70**（fair-to-moderate, **预期有信号差异**） | §5.2 R5-B |
| **Radius κ** | 同一 ctx 轨内 radius=1 vs radius=2 标签一致性 | **≥ 0.70**（substantial, 应稳健） | §3.5 P5.2 |
| **Prompt sensitivity κ** | 同一 prompt v0 vs v1 重写后标签一致性 | **≥ 0.70**（substantial） | validation.yaml |
| **Cross-rater κ** | LLM 标签 vs 人工标签一致性 (stage 33) | **≥ 0.80**（almost perfect） | stage 33 |

## 2. 为什么 Inter-track κ 阈值低 (0.50/0.45)

直觉是"κ 越高越好"。但 inter-track κ 在 v3.2.0 双轨设计下**不应过高**：
- κ > 0.70 → 双轨结果几乎相同 → 双轨设计**冗余**（无信息增量）
- κ < 0.30 → 双轨结果几乎无关 → 一方是噪音（措施学失败）
- **0.50-0.70 区间**（fair-to-moderate per Landis & Koch 1977）→ 存在**显著但非主导的实体邻近效应**，正是双轨设计**应当呈现**的状态

这一区间与 Hassan 2019 QJE 的 entity-proximity vs full-text 设计差异同源。

## 3. 篇章级 vs Bank-year 级 κ

### 3.1 篇章级 κ

直接比较 `innovation_locus_full[i]` vs `innovation_locus_ctx[i]`，对每篇 i ∈ verified_dual_both 子集。

```stata
* Stata 篇章级 κ (kapci2 包)
kapci2 innovation_locus_full innovation_locus_ctx if llm_verified_dual_both == 1
kapci2 innovation_substantiveness_full innovation_substantiveness_ctx if llm_verified_dual_both == 1
```

或 Python：
```python
from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat
mask = df['llm_verified_dual_both']
k_locus = cohens_kappa_2cat(
    df.loc[mask, 'innovation_locus_full'].values,
    df.loc[mask, 'innovation_locus_ctx'].values,
)
```

### 3.2 Bank-year 级 κ

`tech_frac_lf` vs `tech_frac_lc`（同一 bank-year 下两套子集占比的相关性）。这是论文 Robustness Appendix Table A1 的典型呈现：

| Field | Article-level κ | Bank-year-level κ |
|---|---|---|
| innovation_locus | 0.62 (期望 0.50-0.70) | 0.71 (聚合后稳定) |
| innovation_substantiveness | 0.48 (期望 0.45-0.65) | 0.55 |

聚合后 κ 通常高于篇章级（噪音 averaging out）。

## 4. 论文 Methods §4 模板

> Following Hassan et al. (2019, QJE), we measure innovation locus and innovation substantiveness on two text windows per article-bank pair: a full-text window (`_full`) and an entity-proximate window of ±1 sentence around the target bank's mentions (`_ctx`). Inter-track Cohen's κ between the two classifications is X (locus) and Y (substantiveness) at the article level, indicating fair-to-moderate agreement (Landis & Koch 1977) — consistent with the entity-proximity vs full-text distinction motivating our dual-track design. We report main results using {locus_choice} and {subst_choice}; results using the alternative track are presented in Robustness Appendix Table A2.

## 5. Robustness Appendix 表 A1 输出

`tableA1_inter_track_kappa.do` 模板（plan v14 §9.2，待 M6 后续 commit）生成：

```
Field                                 | Article-level κ | Bank-year κ | n_obs
--------------------------------------|-----------------|-------------|------
innovation_locus_full vs _ctx         | 0.62 (κ̂ ± 0.04) | 0.71        | 1170
innovation_substantiveness_full vs _ctx | 0.48 (κ̂ ± 0.05) | 0.55      | 1170
```

## 6. 阈值参考

| 阶段 | κ 类型 | 阈值 | 来源 |
|---|---|---|---|
| stage 21 篇章级 inter-track | locus | ≥ 0.50 | Landis & Koch 1977 moderate 下限 |
| stage 21 篇章级 inter-track | subst | ≥ 0.45 | fair-to-moderate 边界 |
| stage 39 prompt sensitivity | 双维度 | ≥ 0.65-0.70 | validation.yaml; 项目内部 audit |
| stage 33 LLM vs human | 双维度 | ≥ 0.80 | almost perfect (Landis & Koch) |
| stage 35 radius sensitivity (LLM 法) | 三维度 | ≥ 0.70 | radius 稳健性应 substantial |

## 7. 注意事项

- **不要用 inter-track κ 论证 main spec 选择**: 高/低 κ 都不直接支持选 `_full` 或 `_ctx`。Main spec 选择是**方法学论证**问题，与 κ 值无关（参考 stage3_dual_track_plan_v3.2.0.md §5）。
- **篇章级 κ 计算前 dual gate 筛选必须**: 只在 `llm_verified_dual_both == 1` 子集计算（两轨都判 verified=True 的样本），避免 stage 1 拒绝率污染。
- **小样本 κ 不稳**: n < 50 时 κ 置信区间宽阔，不要单点报告，需 bootstrap CI。
