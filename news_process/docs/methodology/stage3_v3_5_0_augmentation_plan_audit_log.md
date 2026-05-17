# Stage 3 v3.5.0 Augmentation Plan — Audit Log

> **状态**: SKELETON (2026-05-17 created, populated incrementally as v3.5.0 implementation proceeds)
> **关联 plan**: [stage3_v3_5_0_augmentation_plan.md](stage3_v3_5_0_augmentation_plan.md) (v0.2 → v11; SHA256 anchor 见 §H)
> **关联 master plan v2 audit log**: [B_route_master_plan_v2_audit_log.md](../plan/B_route_master_plan_v2_audit_log.md) R93+ epoch 6 entries

---

## §A. D0 day scan reports

### §A.production_lineage_gap (F-50 — 最高标准 final audit 发现, 2026-05-17)

**Issue**: Production [21_tone_llms.parquet](../../data/processed/21_tone_llms.parquet) (May 16 02:06) **早于 v3.4.0 commit `450c1aa7` (May 17)**, 仅含 v3.3.0 schema:
- `innovation_locus_full / _ctx / _confidence_full / _confidence_ctx`
- `innovation_substantiveness_full / _ctx / _confidence_full / _confidence_ctx`
- **缺失** `innovation_collab_mode_full / _ctx` (v3.4.0 第三维度)

**后果 (production validation 实测 2026-05-17)**:
- `apply_v3_5_0` → cell_id_full = all-NA (865/865 articles)
- D2 panel aggregation 整段 `cell_aggregation_skipped=True / skip_reason=all_na_cell_id`
- D2 主 deliverable (8-cell decomposition) **当前不可用**
- D3 NMI 仅 2 dim 可计算 (collab_mode 是常数 / 缺失)
- D4 collab_*_residual 派生跳过 (subst + locus 派生正常)

**Plan §9 prereq 漏列**: plan §9.11 仅声明 PII scrubbing prereq, **未声明** stage 21 必须 post-v3.4.0 重跑产出 collab_mode 列。

**解决方案 (user-side)**:
- D0 day 重跑 stage 21 with prompt v8 (M0.5 step, ~12 wk wall-time, ~$2000+ LLM 增量, 在 v3.4.0 epoch 5 launch budget cap $5000 内)
- 重跑后 v3.5.0 cell_id 自动 materialize, 不需要改 v3.5.0 代码

**v3.5.0 代码行为 (已验证 robust)**:
- 当 collab_mode 列缺失时 graceful skip + logger.warning (升级 2026-05-17 final audit)
- 不破坏现有 v3.4.0 baseline tests
- D4 subst/locus 维度继续正常工作
- Stage 21 重跑后**无需修改任何 v3.5.0 代码**, 自动生效

### §A.plan_implementation_discrepancy_log (F-53)

| Plan §section | Plan 写法 | 实际 implementation | 原因 |
|---|---|---|---|
| §2.1.2 code example | `df.groupby(['bank', 'year'])` | `df.groupby(['target_bank', 'year'])` | Production encode.py:221+666 用 `target_bank` 是 v3.4.0 baseline; plan code example 是 stylized 简化 |
| §2.3.3 code example | 同上 | 同上 | 同上 |

用户 2026-05-17 明确指令 "不要再修改计划了" (post-G5 audit 后)。Plan v12 stale references 文档化在此, 不修订 plan 文档 (per user 决定)。Implementation 是 correct production-aligned reference, 测试 fixtures 也已更新 (test_cell_id_panel + test_residual_signals 用 `target_bank`).

---

### §A.1 11-paper / 11-portfolio hardcode scan (per plan §9.9, 修 G-NEW-3)

| Pattern | hits in plan v11 | 结论 |
|---|---|---|
| `11 paper` | 0 | ✓ clean |
| `11-portfolio` | 0 | ✓ clean |
| `12 paper` | 0 | ✓ clean |
| `9 paper` | 4 | ✓ 动态 count (实测 papers/ 目录 9 个 paper_spec.yaml), 与 §2.1.6 + §5 + §12 一致 |
| `P1-P5` | 1 (§2.2.5 paper-level 用法) | ✓ enumeration of main analytical papers, acceptable |
| `5 paper` | 0 | ✓ M6 修订已替换为 9 paper |
| `8 paper` | 0 | ✓ R89 v2.55→v2.56 epoch 5 launch 已修硬编码 |

**Scan command**: `grep -rn "11 paper\|11-portfolio\|11 接收\|12 paper\|12-portfolio\|5 paper\|9 paper\|8 paper" plan-v11.md`

**Verdict**: plan v11 全文使用动态 paper count (基于 papers/ 实测 9 paper_spec.yaml), 无 R89 修订前的硬编码 regression。

### §A.2 PII scrubbing lineage 验证 (per plan §9.11, 修 F38)

待 D0 day 执行: `python -c "import pyarrow.parquet as pq; m = pq.read_metadata('news_process/data/processed/21_tone_llms.parquet'); print(m.schema, m.metadata)"`

预期: stage 21 parquet header 含 Stage 10.5 scrubbed lineage 标识 (e.g., `pii_scrubbed=true` 元数据 or schema 无 raw text column)。

**当前状态**: ⏳ 待 D0 day 执行验证脚本。

### §A.3 constant_dim_warning (per plan §2.2.4 F30 / F40)

NMI compute 若发现 dim 接近常数 (nunique == 1 或 mode_frac > 0.99) 触发，记录在此节。当前: 空（D4 day 实测后填充）。

### §A.4 degenerate_dim_pair (per plan §2.2.4 (d) F40)

NMI both-constant 对 (H(X)=H(Y)=0) 跳过的 (d1, d2) pair 记录。当前: 空（D4 day 实测后填充）。

---

## §B. cell_merge_history (per plan §2.1.4 + F26)

每次 Stata pre-regression cell merge 决策记录。Schema:

| paper_id | cell_id_original | n_obs | priority_used (A/B/C) | merged_into | timestamp | reviewer_signoff |
|---|---|---|---|---|---|---|

**当前状态**: 空（M5 阶段 P3/P4/P5 主回归启动后填充）。

**Cross-paper invariant**: 不同 paper 的 merge 决策可不一致 (per framework §2.bis); 但每 paper 必须 独立 record。

---

## §C. golden_snapshot_diff (per plan §4.3 + F9)

| Stage | v3.4.0 golden hash | v3.5.0 golden hash | Diff summary | Commit |
|---|---|---|---|---|

**当前状态**: 空（D7 day golden baseline regen 后填充）。

**备份策略 anchor**: `tests/fixtures/golden_panel_v0_v3_4_0.json` (git-tagged `v3.4.0-golden-frozen`) + `tests/fixtures/golden_panel_v0.json` (v3.5.0 overwrite default entry).

---

## §D. rollback_log (per plan §7 R8 + F9)

任何 v3.5.0 ship 后的回滚事件 (NMI > null_p99 触发 paper_spec.yaml revert / R0 refactor regression rollback / etc) 记录。

| timestamp | rollback target | trigger | git commit reverted | downstream impact |
|---|---|---|---|---|

**当前状态**: 空（无回滚事件）。

---

## §E. parallel_actual / thread_race_event (per plan §2.2.2 F31 + F43)

### §E.1 parallel_actual NMI compute wall-time

| run_id | n_jobs | wall-time | NMI matrix hash | notes |
|---|---|---|---|---|

**当前状态**: 空（D4 day NMI compute 后填充）。

### §E.2 thread_race_event

若 production parallel 触发 race condition fallback `n_jobs=1`, 记录在此节。

| timestamp | n_jobs attempted | error trace | fallback wall-time |
|---|---|---|---|

**当前状态**: 空（无 race event）。

---

## §F. runtime_observability (per plan §2.2.1 F13)

stage 39c logger.* 输出归档 + audit replay。每次 stage 39c run 的 log file 路径:

| run_id | log path | duration | exit status |
|---|---|---|---|

**当前状态**: 空（stage 39c D4 day 首次 run 后填充）。

---

## §G. signoff_record (per plan §5 PR Reviewer & Sign-off Matrix + F19)

v3.5.0 PR 各类 stakeholder sign-off 记录。

| stakeholder role | identity | signoff timestamp | review focus area | PR comment link |
|---|---|---|---|---|
| Methodology Lead | TBD | ⏳ | framework §2 + §2.2 NMI + §2.3 D4 | |
| Code Owner pipeline/panel/ | TBD | ⏳ | encode.py refactor + encode_collab.py + stata_export.py | |
| Paper Author P3 (bank_fintech_substance) | TBD | ⏳ | paper_spec.yaml tables.t6 + treatment.alternative | |
| Paper Author P4 (bank_fintech_locus) | TBD | ⏳ | 同 | |
| Paper Author P5 (bank_fintech_collab) | TBD | ⏳ | 同 + R9 audit budget confirm | |
| DAG Owner | TBD | ⏳ | stage 39c + OUTPUT_REGISTRY entry | |

**当前状态**: ⏳ 待 v3.5.0 PR 提交后填充。

---

## §H. plan_version_anchor

每个 audit round 必须显式引用所审 plan SHA256:

| audit round | plan version | SHA256 | finding count |
|---|---|---|---|
| epoch 5 R89 (launch) | v3.4.0 baseline | (commit 450c1aa7) | F-211 same-PR fixes (per [master plan v2 audit log R89](../plan/B_route_master_plan_v2_audit_log.md)) |
| epoch 5 R90-R92 (streak 1/2/3) | v3.4.0 baseline | (commit 450c1aa7) | ⏳ pending (user-side action; epoch 5 close 是 v3.5.0 D0 hard prereq) |
| epoch 6 R93 (launch, master plan §5.2.3.bis schema 扩展) | v3.5.0 plan v12 | `ef917f973b6f475184398a4e07f73756dcf4326fb7d6dbe7756933327f0bb978` | 0 (master plan 视角; schema-additive 不 breaking) — 详见 [master plan v2 audit log R93](../plan/B_route_master_plan_v2_audit_log.md) |
| epoch 6 R94 (streak 2/3) | v3.5.0 plan v12 | (same) | ⏳ pending |
| epoch 6 R95 (streak 3/3 close) | v3.5.0 plan v12 | (same) | ⏳ pending |

**Plan-level audit 详细历程** (49 finding 跨 5 组 35 轮): 详见本 plan §11 audit trail (V0 → V12 演进 mapping)。Plan-level 与 master plan v2 audit log 不重复记录 finding 详情, 仅 master plan log 记录 epoch tracker 与 schema-level changes.

**当前 plan v11 anchor**: SHA256 = `ea7eb3ba914df8fbb0a31e730638194400dad50dfc6f268900a857ac727e5271` (post G4 R1, plan §11 audit trail trace 43 historical findings closed).

**Pre-experimental freeze tag**: `v3.5.0-plan-frozen` (D0 day 创建, anchor 此 SHA256, per plan §0 + §9.5).

---

## §I. v3.4.0 anchor commits + tags

| anchor | commit hash | tag (若有) | 用途 |
|---|---|---|---|
| v3.4.0 baseline | 450c1aa7 | ⏳ `v3.4.0-baseline-frozen` (D0 day 第一动作, per §9.12 F33) | NMI reproducibility lock + paper SSRN lock |
| prompt v8 release | (待 git log 查) | ⏳ `prompt-v8-supplementation-released` (CLAUDE.md/memory 声明但 git tag 实测缺失, 独立 hotfix PR 补打) | prompt v8 pre-registration anchor |
| ctx coverage baseline | 待 D0 测定 | ⏳ `v3_4_0_ctx_coverage_baseline.json` (git-tagged) | F8 ctx coverage 自适应警告阈值 |
| golden v3.4.0 | 待 D7 day backup | ⏳ `v3.4.0-golden-frozen` | rollback path per §5 F9 |

**当前状态**: 全部 ⏳ 待 D0 day 创建。

---

## 索引导航

- §A: D0 day scan reports + lineage 验证
- §B: cell_merge_history (per-paper)
- §C: golden_snapshot_diff
- §D: rollback_log
- §E: parallel_actual + thread_race_event
- §F: runtime_observability
- §G: signoff_record (PR reviewer matrix)
- §H: plan_version_anchor (epoch 6 streak)
- §I: v3.4.0 anchor commits + tags
