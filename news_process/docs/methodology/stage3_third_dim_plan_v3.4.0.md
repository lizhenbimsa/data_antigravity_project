# Stage 3 Third Dimension Plan v3.4.0 (Incremental over v3.2.0)

> **状态**: 已实施 (2026-05-17, prompt v8 + git tag `prompt-v8-supplementation-released`)
> **不动**: [stage3_dual_track_plan_v3.2.0.md](stage3_dual_track_plan_v3.2.0.md) 保持 frozen, 本文档为增量
> **关联**: [innovation_collab_mode_framework.md](innovation_collab_mode_framework.md) / [wz_framework_boundary_justification.md](wz_framework_boundary_justification.md) §4

---

## §1. 增量范围

v3.2.0 双轨设计 (innovation_locus + innovation_substantiveness 各 _full/_ctx 共 4 列) 之上，新增第 3 个对称维度:

| Dimension | Values | Tracks | Framework |
|---|---|---|---|
| substantiveness (v3.2.0 existing) | 实质性 / 象征性 | _full / _ctx | W&Z 1994/1998 ASQ |
| locus (v3.2.0 existing) | 底层技术 / 应用场景 | _full / _ctx | Gomber 2018 JMIS |
| **collab_mode (v3.4.0 NEW)** | **自主研发 / 外部协同** | **_full / _ctx** | **Chesbrough 2003 + L&S 2006 SMJ** |

新增 4 个 panel 列 + 4 个 confidence 列:
- `innovation_collab_mode_full` / `innovation_collab_mode_ctx`
- `innovation_collab_mode_confidence_full` / `innovation_collab_mode_confidence_ctx`

---

## §2. v7 → v8 Prompt Bump (Pre-registration β supplementation)

### 2.1 修改范围

[unified_cot.txt](../../config/prompts/unified_cot.txt):
- L1 version bump: `v7-2026-05-14` → `v8-2026-05-17`
- 加入 `### 维度 3：创新协作模式 (innovation_collab_mode)` 段落 (~25 行)
- JSON output_format 加入 3 字段 (`_reason` / `_value` / `_confidence`)

### 2.2 v7 不变性保证 (additive only)

- v7 的 `<step1_relevance>` / `<step2_sentiment>` / `<step3_innovation>` 中的维度 1/2 段落字符级保留
- v7 已 pre-registered 的 5 个 substantive features + 5 个 symbolic mechanisms (`wz_framework_boundary_justification.md` §3) 未修改
- v7 git tag `prompt-v7-released` 永不删除

### 2.3 测试 gate

`tests/integration/test_prompt_version_wired.py::test_production_prompts_have_version_header` 拦截 "未 bump 版本号" 退化。v3.4.0 PR 通过该 gate。

---

## §3. dual gate 语义约定 (v3.2.0 保持不变, plan §G)

`pipeline/sentiment/tone_llms.py:1554-1555` 的 `dual_gate_inputs` 元组仅用 `innovation_locus_*` 列作 "轨内有效性" 判定。本 PR **保持** 该语义不变 = "轨内有效 ⇔ locus 存在"，**不引入第三维度作为闸门**。

理由: dual gate 设计目的是判断"该篇报道是否构成有效 fintech 关联文章"，与 collab_mode 的"内部 vs 外部"语义无关。第三维度若加入 dual gate 会导致 over-restrictive 过滤 (例: 文章有 locus 但 collab_mode 不确定时被错判为无效)。

---

## §4. Tie strategy (与 substantiveness 对称)

`pipeline/sentiment/tone_llms.py` `_aggregate_track()` 内多模型投票:

| Dimension | Tie strategy | Empty fallback | Rationale |
|---|---|---|---|
| locus | conservative → `应用场景` | keyword fallback | 业务侧是 fintech 银行的默认场景 |
| substantiveness | conservative → `象征性` | None | W&Z framework 下实质性需充分证据 |
| **collab_mode (v3.4.0)** | **conservative → `自主研发`** | **None** | **Chesbrough 框架下外部协同需明确证据, 默认归因为自主研发 (MAP under uniform prior)** |

---

## §5. Stata 编码方向 (positive_class = 外部协同)

per `wz_framework_boundary_justification.md` §4 (R32-B encoding direction):

```python
COLLAB_MODE_ENCODING = {
    '自主研发': 0,  # baseline (closed innovation)
    '外部协同': 1,  # 对照 (open innovation; paper main treatment focus)
}
```

`compute_prob_score_binary(label, conf, positive_class="外部协同")` 与 substantiveness/locus 同模式。

---

## §6. 面板聚合 (encode.py)

`pipeline/panel/encode.py` 新增第三维度聚合 if-block (~120 行)，镜像 substantiveness pattern:

- 主 full 轨分组聚合: `_indep` (自主研发) / `_collab` (外部协同) 后缀，n_articles + tone_gap + cross-tab
- ctx 轨对角线: `_indep_cm_ctx` / `_collab_cm_ctx` (Hassan 2019 QJE entity-proximity)
- 恒等式校验: `n_articles == n_articles_indep + n_articles_collab`
- 0-fill: `n_articles_indep` / `n_articles_collab` 在 0 新闻行填 0
- confidence 聚合: `avg_icm_confidence_full` / `avg_icm_confidence_ctx` (i.c.m. 前缀)

---

## §7. 测试覆盖

- `tests/test_stage3_dual_track.py`: 元组解包从 16 → 18 维度 (2 测试更新)
- `tests/test_v3_3_to_v3_4_migration.py`: 11 新增测试 (idempotent / dtype / row count / column count)
- `tests/test_compute_prob_score_binary.py`: 复用现有 prob_score 测试 (VALID_BINARY_LABELS 扩展即可)
- `tests/test_majority_vote_categorical.py`: 复用 (collab_mode 走通用投票路径)
- `tests/integration/test_stata_replication_matrix.py`: 25 测试 (P5 6 模板 + 现有 P3/P4 测试)
- `tests/integration/test_paper_spec_schema.py`: P5 paper_spec.yaml 通过 schema 校验

测试总数: v3.3.0 baseline 1153 → v3.4.0 ≈ 1175-1195 passed (实际增量待 Step L 集成验收测定)。

---

## §8. M5/M6 阶段 follow-up

本 PR 仅做工程契约层 + 文档骨架; 后续 milestone:

- **M0.5 全量重跑 stage 21** (12 wk wall-time, $5,000 LLM cap): 实际产出 collab_mode 标注
- **M3 manuscript 8 section 填实**: P5 + 8 paper limitations 段标准声明
- **M5 主回归实证**: P5 Table 2 (M1-M6) + P3/P4 robustness Table 5 加 collab_mode control
- **M6 稳健性 + Devil's Advocate**: 三维度 cross-tab 8 cells 案例分析
- **Calibration v5.2**: n=450 / 9 strata / 3 raters 人工标注 (待 v5.1 G1 解封后启动, 详见 [calibration_plan_v5.2_delta.md](calibration_plan_v5.2_delta.md))
