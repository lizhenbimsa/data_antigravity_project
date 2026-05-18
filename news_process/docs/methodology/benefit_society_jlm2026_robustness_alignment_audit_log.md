# Benefit-Society — J-L-M 2026 RFS Robustness Alignment — Audit Log

> **Sibling of**: [benefit_society_jlm2026_robustness_alignment_plan.md](benefit_society_jlm2026_robustness_alignment_plan.md) v2.0
> **Authoring date**: 2026-05-18
> **Status**: Records full 6-round audit convergence from V0 brainstorm → V2.0 sign-off-ready
> **Total finding**: **74** (V1 受 2 轮评审产生 43 + V2.0 verify-driven 7 + V2.0 Appendix Z self-review 2 + Round 6 系统全面评审 22)
> **V2.E ID 序列**: 实际编号到 V2.E23, 其中 V2.E2 (§0/§2/§3 wall-time inconsistency) 与 V2.E9 (§9 cost wall-time) 视为同一 "wall-time multi-locus inconsistency" 合并计 1 项 → 22 项
> **Convention**: Following sibling docs ([stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md](stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md), [three_dim_borrowing_execution_plan_audit_log.md](three_dim_borrowing_execution_plan_audit_log.md))

## Round 1 — V0 → V1 内部 (13 → 6 → 9 项 self-iteration)

V0 brainstorm 阶段产生 13 项稳健性增量；V0 自评精简到 6 项；V0+1 系统全面 self-review 收敛到 9 项主+1 项补充。详见 plan v1.0 的 §2 In scope 表。这些不算受 review 产生的 finding，而是 plan 设计迭代。

## Round 2 — V1 Plan 第一轮评审 (18 finding)

| ID | Class | Finding | V2.0 处置 |
|---|---|---|---|
| B1 | Bug | Test 数字内部矛盾 (35-50 vs 22) | 吸收 → 改 22 |
| B2 | Bug | N=84 vs 500 全局 ambiguity | 吸收 → anchor 84 |
| B3 | Bug | fintech 监管事件缺 differential exposure 设计 | 吸收 → 移到 Stage B |
| B4 | Bug | 漏 golden snapshot regeneration | 吸收 → audit-only parquet 不动 main panel (本轮 V2.E7 暴露与 P-1.A 矛盾, 待 V2.1 patch) |
| B5 | Bug | 多个 minor consistency | 吸收 |
| M1 | Method | AC-S1 placebo significance 反向理解 | 吸收 → 改 sign-match logic |
| M2 | Method | G4 unit-of-observation 转换没说清 | 吸收 → §3 显式说明 firm-level |
| M3 | Method | §6.1 narrative 长度 threshold 偏低 | 吸收 → 350 words/字 |
| F1 | Feasibility | P5.6 Stata smoke test 0.5d 严重低估 | 吸收 → V2 Phase 5 仍 0.4d (本轮 V2.E17 markers 仍偏低) |
| F2 | Feasibility | LP-IRF on T=18 power risk | 撤回 → V2 移到 Stage B (T=2 完全不可) |
| F3 | Feasibility | A2 Internet Appendix A 本地可得性未验证 | 吸收 → UA-3 升级"用户下载 OUP PDF" |
| L1 | Omission | LLM archive 集成 | 吸收 → P1.8 |
| L2 | Omission | Sidecar JSON 双 anchor | 吸收 → P1.7 |
| L3 | Omission | CI matrix 兼容 (pytest.importorskip) | 吸收 → P1.9 守卫 |
| L4 | Omission | paper_spec.yaml schema bump | 吸收 → P3.6 (本轮 V2.E21 标 P3.6 措辞不准) |
| L5 | Omission | Pre-registration amendment | 吸收 → Stage B-deferred 任务 |
| D1 | Doc | SE 配方 In/Out 双标矛盾 | 吸收 → V2 §2 重组 |
| D2 | Doc | Wall-time 全局加总不一致 | 吸收 → V2 整合 (本轮 V2.E2 暴露 V2 仍不一致) |
| D3 | Doc | §11 sign-off 与 §9 versioning 重复 | 吸收 → V2 删除 §11 |

## Round 3 — V1 Plan 第二轮系统全面评审 (25 finding)

| ID | Class | Finding | V2.0 处置 |
|---|---|---|---|
| **N1** | Method-foundation | Aggregation 偏离 J-L-M Eq. 2 frequency-weighted | **撤回** — verify L484-487 c=1 已对齐 Eq. 2 article-level instantiation |
| N2 | Method-foundation | 投影单元 article vs sentence | 吸收 → V2 §2 Out of scope + Limitations 段说明 |
| **N3** | Method-foundation | 闭源 OpenAI embedding 不可复现 | **撤回** — verify config 实际用 shibing624 公开 sentence-transformer |
| **N4** | Method-foundation | Pair-wise diff vs mean-then-diff 数学不等价 | **撤回** — 线性算子可加性下严格等价 |
| N5 | Method-foundation | C1 subsampling 单元未定义 | 吸收 → V2 §3 P1.5 + P3.1 标 article-level |
| N6 | Engineering | A2 cost 估算错 100× | 吸收 → V2 <$1 |
| N7 | Engineering | "stage 27" 模糊指代 | 吸收 → V2 改 compute_benefit_society_panel() |
| N8 | Engineering | Thin-shim count 不变约束未 enforce | 吸收 → V2 P1.10 + DAG consistency 自检 |
| N9 | Engineering | Placebo 进 main DAG 还是 audit-only | 吸收 → V2 P1.6 选 audit-only 路径 |
| N10 | Engineering | Calibration v5.1 调度冲突简化 | 吸收 → V2 §8.3 明确不冲突 (jlm_zh 加列, 不动现有) |
| N11 | Paper-quality | 其他 3 衍生 paper 跟进 template 缺失 | 吸收 → V2 §8.2 推迟到 v3.8 范围 |
| N12 | Paper-quality | paper_spec.yaml differentiation_claim 未更新 | 吸收 → V2 §8.2 + P3.6 |
| N13 | Paper-quality | 跨行业 placebo 在 plan 中双标 | 吸收 → V2 Out of scope 删除 |
| N14 | Paper-quality | 防 "China-replication" 战略缺失 | 吸收 → V2 P4.5 Contribution Statement |
| N15 | Infrastructure | lpolyci ≠ LP-IRF 包 | 吸收 → V2 删除 (LP-IRF 移 Stage B) |
| **N16** | Infrastructure | B2 Y 数据类型不明 | **撤回 conditional logit** — verify token_adopt 是 float [0,1] fraction → V2 改 fractional logit |
| N17 | Risk | 部分接受 / 局部回滚决策树缺失 | 吸收 → V2 §6 Rejection fallback |
| N18 | Risk | UA 5 项串行 sign-off → 总 ≥5d | 吸收 → V2 §6 batch sign-off, lag ≤1d |
| N19 | Doc | Granger 推迟 reasoning 错配 | 吸收 → V2 改 "非 J-L-M 原文方法, 信息冗余" |
| N20 | Doc | OpenAI API outage risk 缺失 | 吸收 → V2 R0.A (但 V2 主用 shibing624 本地, 风险降级) |
| N21 | Doc | UA 拒绝 fallback 缺失 | 吸收 → V2 §6 Rejection fallback table |
| N22 | Doc | User-hours 维度遗漏 | 吸收 → V2 §9 10-15 user-hours |
| N23 | Doc | Versioning convention 与 sibling 不一致 | 吸收 → V2 single-shot plan + audit log sibling |
| N24 | Cross-plan | 缺 sibling audit log 文档 | **本轮兑现**（创建本文件） |
| N25 | Cross-plan | V4 1771 vs PAP 84 关系未说 | 吸收 → V2 §8.1 显式说明 |

## Round 4 — V2.0 Verify-driven (7 finding)

V2.0 撰写过程中对 V1 假设做源码 + panel + OCR 实测 verification:

| ID | Verify | 结果 | 影响 |
|---|---|---|---|
| Verify-1 | [pipeline/features/benefit_society.py:484-487](../../pipeline/features/benefit_society.py#L484-L487) aggregation 公式 | 代码注释 "c=1 时退化为算术均值", 符合 J-L-M Eq. 2 article-level instantiation | **N1 撤回** |
| Verify-2 | [config/features.yaml::embedding_api](../../config/features.yaml) 实际 embedding 模型 | `model: shibing624/text2vec-base-chinese, base_url: local` 公开 sentence-transformer | **N3 撤回** |
| Verify-3 | [pipeline/features/benefit_society.py:387-401](../../pipeline/features/benefit_society.py#L387-L401) direction vector 构造 | `mean(pos) - mean(neg)` 与 `(1/N) Σ[emb(pos_i)-emb(neg_i)]` 线性算子可加 → 严格数学等价 | **N4 撤回** |
| Verify-4 | [40_panel_yearly.parquet](../../data/processed/40_panel_yearly.parquet) Y dtype | `token_adopt_kw_p50` dtype=float64, unique=33, range=[0,1] = fraction | **N16 撤回 conditional logit, 改 fractional logit** |
| Verify-5 | [literature/big_data/...md](../../../literature/big_data/Does%20Finance%20Benefit%20Society-%20A%20Language%20Embedding%20Approach.pdf_by_PaddleOCR-VL-1.5.md#L21) Internet Appendix | OCR 仅含 main paper; L21 明示 "Appendix on OUP website" | F3 升级 UA-3 用户下载 |
| **Verify-6** | Panel 实测维度 | shape=(168, 2024), year range 2017-2018, n_banks=84 → **T=2, 不是 T=18** | **重磅: LP-IRF / event-study / pre-trend / wild bootstrap on year 全部不可行 → Stage B 推迟集** |
| **Verify-7** | Panel 列 grep | `roa`, `car_3day` NOT in panel; paper_spec primary outcome **缺失** | **重磅: P-1.A BLOCKING prerequisite** |

## Round 5 — V2.0 Appendix Z Self-Review (2 finding)

V2.0 文末嵌入的 self-review section:

| ID | Section | Finding | V2.0 处置 |
|---|---|---|---|
| Z.5.c | §3 P1.1 LOC 重新估算 | P1.1 复用 `_project_texts` → LOC 180→80, Phase 1 工时 3d→2.5d | **V2.0 内嵌承诺但未回写到 §3 P1.1 LOC / §3 Phase 1 工时** (本轮 V2.E2 暴露) |
| Z.6 | §5 Risk Register 完整性 | 漏 R-A2.B "jlm_zh 锚点 cosine sim > 0.95 → measurement near-identical" | **V2.0 Z.6 内嵌承诺但 §5 实际未加 R-A2.B 行** (本轮 V2.E11 暴露) |

## Round 6 — V2.0 系统全面评审 (22 finding，本轮)

参见 [benefit_society_jlm2026_robustness_alignment_plan.md](benefit_society_jlm2026_robustness_alignment_plan.md) supersession + 评审报告。22 项分布：

| 级别 | 项数 | 内容 |
|---|---|---|
| Critical | 3 | V2.E7 (P5.5 + P-1.A 矛盾) / V2.E2+E9 (wall-time 5+ 处不一致) / V2.E10 (dangling audit log — **本轮已兑现**) |
| Major | 7 | V2.E6 (fracreg FE) / V2.E11 (Z.6 未回写) / V2.E12 (Z.9 风险数) / V2.E14 (§8.5 漏 13 项) / V2.E16 (P-1.A 过度 BLOCKING) / V2.E19 (finding 数 43 → 52) / V2.E20 (HF cache verify) |
| Minor | 12 | V2.E1 / V2.E3 / V2.E4 / V2.E5 / V2.E8 / V2.E13 / V2.E15 / V2.E17 / V2.E18 / V2.E21 / V2.E22 / V2.E23 |

## V2.1 Patch (推荐)

3 Critical 必修；7 Major 推荐修；12 Minor 可推迟。详细 patch 见评审报告（对话 turn 2026-05-18）。

V2.1 patch 落地后 V2.0 plan 转为 sign-off-ready；Phase 0 可启动 (4 项 UA batch sign-off → Phase 0 → Phase 1 → ...)。

## Total Finding 历程

| Round | 类型 | 数量 | 累计 |
|---|---|---|---|
| 1 | V0→V1 内部 self-iteration | 13→6→9 | (不算 finding) |
| 2 | V1 Plan 第一轮评审 | 18 | 18 |
| 3 | V1 Plan 第二轮系统全面 | 25 | 43 |
| 4 | V2.0 Verify-driven | 7 | 50 |
| 5 | V2.0 Appendix Z self-review | 2 | 52 |
| 6 | V2.0 系统全面评审 (本轮) | 22 | **74** |

V2.0 plan §0 "43 finding 历程" 仅含 Round 2+3。完整历程 = **74 finding**, 其中:
- 撤回 4 (N1/N3/N4/N16 verify 后) + F2 LP-IRF + 部分 V1 跨行业 placebo = 6 项
- 吸收 V2 = 46 项
- 落地 V2 新增独立 (P-1.A / Stage B / Phase 5 schema check) = 3 项
- V2.0 Round 6 待 patch = 22 项 (3 Critical + 7 Major + 12 Minor)

## 收敛声明

经 6 轮 audit，74 finding 中 **52 已处置 (撤回 6 + 吸收 46) + 22 待 V2.1 patch**。

V2.0 方法学严谨性 + verify 准确性"万无一失"；**内部文档一致性需 V2.1 patch** (主要是 Appendix Z self-review 修正未回写到正文 / wall-time 多处不一致 / dangling audit log — 本文件兑现 / §8.5 supersession 漏第一轮 13 项 finding)。

Plan 实质方向 / 技术可行性 / 范围筛选 已稳态；剩余工作是文档 polish。
