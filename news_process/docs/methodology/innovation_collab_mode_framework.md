> **[D1 恢复注记, 2026-07-14]**：本文档服务 v8 历史复现包（`unified_cot.txt:84` 引注目标），由计划 D1 于 2026-07-14 从 commit `1698bda5^` 恢复；§11 v9 将删除 prompt 内该引注，本文档与之双轨不冲突。原文档随 `1698bda5`（"删除整个 docs/ 目录"）一并删除，此处按原始内容原样恢复，未做实质性改写；恢复时核查确认 §2 已含 W&Z substantiveness / Gomber locus 正交性 cross-tab 框架（8-cell 表 + §2.bis 稀疏 cell 合并决策树），无需另补。

---

# Innovation Collaboration Mode Framework (v3.4.0)

> **版本**: v1.0 (2026-05-17, 与 prompt v8 同步发布;v8 字节级锚定 = sidecar JSON `prompt_v8_sha256` per PROJECT_DESCRIPTION.md L3888;无 git tag)
> **关联**: [wz_framework_boundary_justification.md](wz_framework_boundary_justification.md) §4 / [stage3_dual_track_plan_v3.2.0.md](stage3_dual_track_plan_v3.2.0.md) / [stage3_third_dim_plan_v3.4.0.md](stage3_third_dim_plan_v3.4.0.md)

---

## §1. 文献基础

### 1.1 Chesbrough (2003) Open Innovation
Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* Harvard Business School Press.

核心论点: 企业不应仅依赖内部 R&D (closed innovation paradigm)，而应主动**通过外部知识源 / 外部商业化路径**获取技术。开放式创新强调：
- **inbound**: 引入外部 ideas / IP / 技术 (technology in-sourcing, licensing-in, M&A)
- **outbound**: 向外输出未用 IP (licensing-out, spin-off)
- **混合模式**: 与外部组织 (fintech 公司 / 科技巨头 / 大学 / 研究所) 的 joint R&D / 战略联盟 / 开放 API

### 1.2 Laursen & Salter (2006) Search Breadth & Depth
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms. *Strategic Management Journal*, 27(2), 131-150.

操作化两个连续维度:
- **Search breadth** (0-16 外部 sources): 企业从多少不同类型的外部 source 获取 ideas
- **Search depth** (0-7 intensity): 与每个 source 的合作深度

实证发现: 适度 openness 提升创新产出，过度 openness (over-search) 反而损害绩效 (inverted-U)。

### 1.3 Hagedoorn (2002) R&D Partnerships
Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492.

实证证据: 1960-1990 年代 inter-firm R&D 联盟从 80 个/年增长到 600+ 个/年，**主要由 high-tech 行业驱动** (信息技术、生物技术、新材料)。本研究的 fintech 银行场景对应此 high-tech 趋势在中国 2007-2024 期间的延伸。

### 1.4 Cohen & Levinthal (1990) Absorptive Capacity
Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.

补充论点: 即使采用 open innovation，企业仍需**内部 R&D 投入维持 absorptive capacity** 才能消化外部知识。这为本研究的 **自主研发 vs 外部协同 trade-off** 提供理论 baseline (二者并非互斥，但 reporting layer 上的主导事件呈现二元性)。

---

## §2. 与 W&Z substantiveness / Gomber locus 的正交性论证

新增 collab_mode 后，三维度 (substantiveness × locus × collab_mode) 构成 **2³ = 8 cross-tab cells**:

| Substantiveness | Locus | Collab Mode | 概念解释 | 真实案例 |
|---|---|---|---|---|
| 实质性 | 底层技术 | 自主研发 | 真实内部技术能力建设 | 工行自建 AI 实验室 + 自研专利 |
| 实质性 | 底层技术 | 外部协同 | 协作建底层技术能力 | 招行 × 蚂蚁链联合开发区块链平台 |
| 实质性 | 应用场景 | 自主研发 | 内部团队开发业务应用 | 建行内部团队上线"惠懂你"APP |
| 实质性 | 应用场景 | 外部协同 | Ecosystem play (业务 + 外部) | 微众银行 × 腾讯开放支付 API |
| 象征性 | 底层技术 | 自主研发 | 技术口号但无投入 | 银行声称"全面 AI 化"但 IT 预算未升 |
| 象征性 | 底层技术 | 外部协同 | 战略联盟签约但未执行 | 战略协议 PR 后无后续 |
| 象征性 | 应用场景 | 自主研发 | 业务公关包装 | 仪式性产品发布会 |
| 象征性 | 应用场景 | 外部协同 | 战略合作 PR-only | 跨界合作签约但无产品落地 |

**正交性的理论支撑**:
- **collab_mode × substantiveness**: 自主研发可以是象征性 (Westphal & Zajac 2001 decoupling 框架延伸; Fiss & Zajac 2006 AMJ symbolic management) — 内部声明但无实际行动。外部协同也可以是实质性 — 真实并购 fintech / 落地 joint R&D。
- **collab_mode × locus**: Chesbrough open innovation 不限于技术层或业务层 (Hagedoorn 1993 SMJ "Understanding the rationale of strategic technology partnering" 区分 technology vs business 跨域合作)。自主研发亦同。

**实证可分离性**: 在 400k 文章语料中，每个 cell 在概念上独立可识别 (M5 阶段需验证 cell 计数 ≥ 50 obs，否则 power 不足)。若某 cell 实证为空 (e.g., 实质性 × 底层技术 × 外部协同 0 obs)，则需在 limitations 中说明 trade-off 决策。

### §2.bis Sparse cell pre-registered merge decision tree (v3.5.0 升级, per [stage3_v3_5_0_augmentation_plan.md §2.1.4](stage3_v3_5_0_augmentation_plan.md#L196))

v3.4.0 版仅说"在 limitations 中说明"。**v3.5.0 升级**: 引入 article-level 8-cell decomposition (D2) 后, panel 输出 8 个 `n_articles_cell_{1..8}_full` 列**不变**, cell 合并发生在 **Stata pre-regression decision 层**——单 paper Table 6 跑回归前由 .do 模板判定。

**主回归阶段 单 paper 决策树** (pre-registered, 每 paper Table 6 启动前 frozen; per Nosek 2018 PNAS additive supplementation):

| 条件 | 行动 |
|---|---|
| cell n ≥ 50 obs (rule of thumb for OLS cell-level fixed-effect estimation, NOT Cohen 1988) | 独立 estimate, 入 Table 6 |
| cell 30 ≤ n < 50 | **Priority A**: 与同 collab + 同 locus、相反 substantiveness 的 cell 合并 |
| 合并后仍 n < 50 | **Priority B**: 与同 collab、相反 locus 的合并 |
| 仍 n < 50 | **Priority C**: 该 cell 标 `merged_into_other`, 主回归 omit, Appendix 报描述统计 |

**合并记录义务**: 每次合并发生前后**必须**记录到 [stage3_v3_5_0_augmentation_plan_audit_log.md §B.cell_merge_history](stage3_v3_5_0_augmentation_plan_audit_log.md)。审稿人 replication 重现需引用 stage 21 输出 + 该 audit log row。

**Cross-paper 一致性**: 若 P3/P4/P5 中两个或以上 paper 都触发 cell merge, 不同 paper 的 merge 决策 (Priority A/B/C) 必须独立基于该 paper 的样本统计; **不要求** cross-paper merge 决策一致。但 audit log §B.cell_merge_history 必须每 paper 单独记录 (含 cell, n_obs, priority used, paper_id) 以让 cross-paper Table 6 比较时审稿人能看见每 paper 的 merge structure 差异。Paper-level Table 6 主结果**禁止**跨 paper 直接合并 cell, 仅允许 within-paper merge。

---

## §3. fintech 银行场景的边界规则

### 3.1 "外部协同" 的判定边界

✅ **算外部协同**:
- 与 fintech 公司 / 大学 / 研究所的 joint R&D (e.g., 工行 × 清华联合实验室)
- 收购 fintech 子公司 / 战略投资 / 合资公司 (e.g., 平安并购金融壹账通)
- 开放银行 API + 第三方接入 / SDK (e.g., 浦发开放银行 2018)
- 行业联盟 / 产业链协作 (e.g., 区块链金融服务联盟)
- 引入外部供应商技术栈 / licensing-in / 技术转让 (e.g., 工行采购 Murex 风控系统)

❌ **不算外部协同**:
- 单纯采购通用 IT 设备 (服务器、办公软件) — 不构成 fintech 实质创新合作
- 雇佣外部顾问做培训 — 顾问不构成创新主体 (per Cohen & Levinthal 1990 absorptive capacity)
- 文章主体不是该银行的合作 (e.g., 报道行业 fintech 趋势但未具体涉及目标银行)

### 3.2 "自主研发" 的判定边界

✅ **算自主研发**:
- 自建技术团队 / 自有 R&D lab / 自有专利
- 内部 IT 部门主导的系统建设
- "自研" / "自建" / "自主开发" / "in-house" 措辞

❌ **不算自主研发**:
- 与外部协同并列报道 → 按报道主导事件判定 (首段主语 / 标题指向)
- 单纯公关宣告无具体实施 → 倾向于象征性而非自主研发

### 3.3 Multi-class 扩展的未来方向 (R6-3 Construct Validity Mitigation)

当前 v3.4.0 采用单字段二元 collab_mode 作为 Chesbrough/L&S spectrum 的离散 proxy，损失了:
- 多伙伴协作 vs 单一伙伴 (breadth)
- 深度长期合作 vs 浅度试探 (depth)
- 协作类型异质性 (M&A / 投资 / API / 联盟)

未来研究可拓展为 multi-class:
- `independent` (自主研发)
- `strategic_investment` (战略投资)
- `m_and_a` (M&A)
- `api_open` (开放 API)
- `industry_alliance` (行业联盟)
- `joint_rd` (joint R&D)

但当前二元设计的优点: 与 substantiveness / locus 形成对称 2×2×2 cross-tab，便于 Stata 主回归 single-treatment specification。

---

## §4. 与 v3.2.0 dual-track 架构的兼容性

`innovation_collab_mode_full` / `innovation_collab_mode_ctx` 双轨结构与 v3.2.0 BREAKING 后的 substantiveness/locus 双轨完全对称:

- **full 轨**: 全文 (article-level) 多模型 LLM 投票, anchor frame: Chesbrough 2003 + L&S 2006
- **ctx 轨**: entity-context (Hassan 2019 QJE) 实体邻近窗口判定, 避免与目标银行无关的 fintech 行业背景干扰

**dual gate 语义保持不变**: `llm_verified_dual_full_only` / `llm_verified_dual_ctx_only` / `llm_verified_dual_both` 仍基于 `llm_verified_*` 与 `innovation_locus_*` 闸门 (v3.2.0 BREAKING 设定，per [tone_llms.py:1554-1555](../../pipeline/sentiment/tone_llms.py#L1554))，**不引入 collab_mode 作为第三闸门**。理由: dual gate 设计目的是判断"该篇报道是否构成有效 fintech 关联文章"，与 collab_mode 的"内部 vs 外部"语义无关。

**Inter-track κ 阈值**: 与 substantiveness 同标准 κ ≥ 0.45 (fair-to-moderate per Landis & Koch 1977)，详见 [inter_track_agreement_interpretation.md](inter_track_agreement_interpretation.md)。

---

## §5. Stata 编码与 paper-level usage

### 5.1 Stata byte 编码

`pipeline/panel/stata_export.py::COLLAB_MODE_ENCODING`:
```python
COLLAB_MODE_ENCODING = {
    '自主研发': 0,  # 0 = baseline (closed innovation, Chesbrough 2003)
    '外部协同': 1,  # 1 = 对照 (open innovation; paper 主回归 treatment 焦点)
}
```

与 substantiveness/locus 同模式 (`0=baseline, 1=对照`)，方便 Stata 主回归 single-treatment specification。

### 5.2 panel 列后缀约定

- `_indep` (自主研发) / `_collab` (外部协同) — 平行于 substantiveness `_sub`/`_symb` 与 locus `_tech`/`_app`
- `_indep_cm_ctx` / `_collab_cm_ctx` — ctx 轨对角线 (Hassan 2019 entity-context)
- `n_articles_indep` / `n_articles_collab` — 计数列
- `indep_frac` / `collab_frac` — 比例列
- `tone_gap_indep_collab` — 情感纯度差距 (类似 `tone_gap_sub_symb`)

### 5.3 paper-level usage

- **P5 (bank_fintech_collab)**: 主回归 treatment = `collab_open_full` / `collab_closed_full` (binary pair from `innovation_collab_mode_full`)
- **P3 (bank_fintech_substance) / P4 (bank_fintech_locus)**: collab_mode 仅作 Table 5 robustness control (alternative spec)
- **P1/P2/4-retrofit paper**: 按 Q-D user 决策 "全部 9 paper 完全传播"，加入 `paper_spec.yaml::controls.bank_level` 作 control variable

---

## 参考文献

- Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* HBS Press.
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms. *Strategic Management Journal*, 27(2), 131-150.
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492.
- Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *PNAS*, 115(11), 2600-2606.
- Westphal, J. D., & Zajac, E. J. (2001). Decoupling policy from practice: The case of stock repurchase programs. *Administrative Science Quarterly*, 46(2), 202-228.
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change. *Academy of Management Journal*, 49(6), 1173-1193.
