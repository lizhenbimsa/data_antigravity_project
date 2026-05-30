# B Route Master Plan v2 — 五篇独立 Bank-FinTech 论文 (v3.4.0 P5 epoch 5)

> **Status**: v2.56 **EPOCH 4 IN-PROGRESS** (streak 3/3 pending; F-211 起编; 触发原因: user 2026-05-17 决策 P5 `bank_fintech_collab` 立项 per plan v3.4.0 §I)
> **Previous Status**: v2.55 EPOCH 3 AUDIT-STABILIZED (post 84-round self-audit; **207 plan-doc cumulative findings + 3 audit-log meta findings = 210 total**; epoch 2 streak 3/3 ACHIEVED at R70-R72; epoch 3 streak 3/3 ACHIEVED at R82-R83-R84; see [audit log](B_route_master_plan_v2_audit_log.md))
> **Authoring date**: 2026-05-16
> **Revision date**: 2026-05-17 (v2.56 epoch 5 launch)
> **Author**: Claude Opus 4.7 (1M context), authored per user directive
> **Baseline**: news_process v3.4.0 (BREAKING upgrade from v3.3.0 `e815237`; v3.4.0 (2026-05-17) Stage 3 第三维度对称扩张 — 新增 `innovation_collab_mode_{full,ctx}` (Chesbrough 2003 + Laursen & Salter 2006 SMJ); prompt v7→v8 additive supplementation per Nosek 2018 PNAS; v8 字节级锚定 = sidecar JSON `prompt_v8_sha256` (PROJECT_DESCRIPTION.md L3888;无 git tag); **61 Stata templates** (= 55 v3.3.0 + 6 bank_fintech_collab/ P5 子目录) + **12 双语 manuscripts** (v3.3.0 10 + P5 zh/en); LLM cost cap 4200 → 5000)
> **Test baseline**: 1718 passed / 5 baseline-existing failures (v3.3.0 main 即 fail, 非 v3.4.0 引入) / 2 skipped
> **Decision context**:
> - 用户在 A/B/C 三条路线评审后明确选定 **B 路线**（v2.55 4 paper, **v2.56 epoch 5 加 P5 → 5 paper**）；
> - 用户报告 raw 数据规模 = 400,000 篇媒体报道 × 500 家中国商业银行 × 2007-2024 (18 年)；
> - **当前 pipeline ingested 仅为 9,427 → 168 obs 子集**（v1 plan 误以为这是全量）；
> - v2 修正核心：M-1 数据现状审计 + M0.5 Pipeline 全量重跑两项前置工作；
> - **v2.56 epoch 5 触发**: 2026-05-17 P5 `bank_fintech_collab` 立项 (Chesbrough 2003 Open Innovation 第三维度); paper portfolio 11 接收 → 12 接收; LLM cap 4200 → 5000 (Q-B); 人工 calibration v5.2 9 strata × 450 obs × 3 raters (Q-C).
> **Anchor commits**:
> - v3.3.0 closing: `e815237` (2026-05-16)
> - v3.4.0 BREAKING: (pending PR-A commit, 2026-05-17)
> - benefit_society v2.12: prior anchor for "14 rounds / 59 findings" rigor benchmark
> - three_dim_borrowing v1.37: prior anchor for plan-doc format standard
> - 关联文档: [innovation_collab_mode_framework.md](../methodology/innovation_collab_mode_framework.md) / [stage3_third_dim_plan_v3.4.0.md](../methodology/stage3_third_dim_plan_v3.4.0.md) / [calibration_plan_v5.2_delta.md](../methodology/calibration_plan_v5.2_delta.md) / [wz_framework_boundary_justification.md](../methodology/wz_framework_boundary_justification.md) §4

---

## 0. Document Purpose

本文档是 B 路线（v2.55 4 篇 + v2.56 P5 = 5 篇独立 Bank-FinTech 论文）的端到端**项目执行计划**，不是方法学
设计文档。它定义：

1. **四篇论文的最终学术定位**（包括投稿目标期刊与现实顶板）；
2. **从当前 v3.4.0 状态到 5 篇 submission-ready manuscript 的完整工程路径** (v2.55 4 + v2.56 P5)；
3. **关键决策点 D1-D6** 与 **应急方案 C1-C4**；
4. **风险登记表 R1-R12** 与 **acceptance gates G-1 → G8**；
5. **资源预算**（LLM cost / GPU / 人时 / 数据成本）；
6. **法律合规清单**。

它**不**重复 [`papers/bank_fintech_tone/README.md`](../../papers_assets/bank_fintech_tone/README.md) 等论文级 README 已经记录的方法学细节，
也**不**重复 CLAUDE.md 已经定义的工程约定。下游 plan 文档（如各 paper-spec.yaml）
派生自本文档。

---

## 1. Context Anchors

- Project root: `f:\WiseSearch\data_antigravity_project\`
- Python interpreter: `F:\Anaconda3\python.exe` (memory `python_interpreter`)
- Package: `news_process/`; CLAUDE.md governs conventions
- Stata env: StataNow/MP 19.5 (64-core, 128GB RAM, Rev 2026-01-14)
- Sibling plan & methodology docs:
  - [`docs/methodology/three_dim_borrowing_execution_plan.md`](../methodology/three_dim_borrowing_execution_plan.md) — v1.37, P0/P1/P2 三维补对称
  - [`docs/methodology/calibration_plan_v5.1.md`](../methodology/calibration_plan_v5.1.md) — frozen 2026-05-14 (git tag `calibration-plan-v5.1-frozen`)
  - [`docs/methodology/stage3_dual_track_plan_v3.2.0.md`](../methodology/stage3_dual_track_plan_v3.2.0.md) — v3.2.0 双轨设计依据
  - [`docs/methodology/wz_framework_boundary_justification.md`](../methodology/wz_framework_boundary_justification.md) — W&Z 框架边界条件
  - [`docs/methodology/paper_methodology_section_draft.md`](../methodology/paper_methodology_section_draft.md) — 方法学章草稿
  - [`papers_assets/bank_fintech_tone/README.md`](../../papers_assets/bank_fintech_tone/README.md) — 主线论文 README (R8-m03 visible name 校正)
  - [`papers/_common/stata_templates/`](../../papers/_common/stata_templates/) — 14 共享 + 41 paper-specific Stata templates = 55 total

- Existing git tags relevant to this plan:
  - `prompt-v7-released` — prompt v7 pre-registration anchor
  - `calibration-plan-v5.1-frozen` — manual validation plan freeze
  - (planned) `B-route-v2-frozen` — M0 完成时打标

---

## 2. Scope

### 2.1 In scope

| 工作项 | 含义 |
|---|---|
| **M-1** | 数据现状审计：从 raw (40 万条 / 500 银行 / 18 年) 推算实际 N_eff × T_eff，决定 Go/No-go |
| **M0** | 设计契约冻结：v2.55 8 份 paper_spec.yaml (3 新 + 5 retrofit; R2-M08) **+ v2.56 epoch 5 第 9 份 P5 bank_fintech_collab** = 9 份 + paper_registry 扩到 9 paper |
| **M0.5** | Pipeline 全量重跑：把 raw 推到 `46_panel_yearly_v34.dta` |
| **M1** | 目录骨架镜像：在 `papers/` 和 `papers_assets/` 下新增 3 个 paper 子模块 |
| **M2** | Stata 模板差异化：3 个新 paper 各自的"主回归+机制+异质性+稳健性"四件套 |
| **M3** | Manuscript 骨架冻结：3 篇新 paper × en/zh × 8 section = 48 sections (5 existing manuscript 不在 M3 scope, 但 M3 G3 含 5 existing regression test) |
| **M4** | 外生冲击 DiD 设计 (R2-M10 + R3-M07 修订; v2.56 epoch 5 +P5): 6 events (E1-E5b) × applicable papers (per §5.7.2) = v2.55 **17** + v2.56 epoch 5 P5 (E1/E3/E4 applicable) **+3** = **20 DiD spec** 设计 + 平行趋势检验 + treatment 定义 |
| **M5** | 主回归 + 机制 + 异质性章实证内容 |
| **M6** | 稳健性 + Devil's Advocate 审稿模拟 |
| **M7** | 内审 + 互引校准 + 投稿包 |
| **M8** | 投稿 + post-submission monitor (持续到首次 decision; revision cycle 不在本 plan scope) |

### 2.2 Out of scope (with reason)

| 工作项 | 排除理由 |
|---|---|
| 跨国 fintech 媒体数据（v1 plan 的 B2 路径）| N×T = 500 × 18 = 9,000 obs 已足够进入 top 5 银行实证下沿；跨国扩展边际收益不抵成本（3-6 月、$5K+ 数据采购）|
| 新增 BERT 模型 fine-tune | 现有 3 BERT (FinBERT-CN, FinSent-ZH, FinBERT2, 加上 prompt v7 三 LLM) 三角验证足够；扩展属 future work |
| LLM 同业竞争网络 IV (`llm_peer/`) 重新设计 | 已在 v3.3.0 落地，M0 仅做 9 paper registry 注册 (v2.56 epoch 5 含 P5)，不重新设计 |
| 新建 stage（如 stage 17/27/47）| 4 个新 paper 全部消费 `46_panel_yearly_v34.dta`，不向 DAG 注入新 stage |
| Manual annotation 等级扩展 | 由 [calibration_plan_v5.1](../methodology/calibration_plan_v5.1.md) 单独跟踪 |
| Manuscript 实质内容生成 | 工程基线 plan，paper 实质内容由 academic-paper skill 在 M5/M6 阶段产出 |
| 直投顶刊概率优化（如换 outlet）| D5 决策点处理，不在本 plan 默认范围内 |

### 2.3 Academic anchors invoked

- **Hassan, Hollander, van Lent, Tahoun (2019)** QJE 134(4), 2135–2202 — firm-level political risk text-based exposure 方法学锚
- **Westphal & Zajac (1994)** ASQ 39(3); **(1998)** ASQ 43(1) — substance vs symbolism 框架
- **Westphal & Zajac (2001)** ASQ 46(2) — decoupling policy from practice
- **Fiss & Zajac (2006)** AMJ 49(6), 1173–1193 — symbolic management of strategic change (P3 SMJ-style exemplar)
- **Gomber, Kauffman, Parker, Weber (2018)** JMIS 35(1), 220–265 — fintech taxonomy (locus: technology vs business function)
- **Kogan, Papanikolaou, Seru, Stoffman (2017)** QJE 132(2), 665–712 — innovation 度量 anchor
- **Goldsmith-Pinkham, Sorkin, Swift (2020)** AER 110(8), 2586–2624 — Bartik IV identification
- **Sautner, van Lent, Vilkov, Zhang (2023)** JF 78(3), 1449–1498 — climate exposure 文本度量延伸
- **Callaway & Sant'Anna (2021)** J. Econometrics 225(2), 200–230 — staggered DiD baseline
- **Borusyak, Jaravel, Spiess (2024)** RES 91(6), 3253–3285 — robust DiD estimator (imputation)
- **Cengiz, Dube, Lindner, Zipperer (2019)** QJE 134(3), 1405–1454 — event study with proper pre-trends
- **Sun & Abraham (2021)** J. Econometrics 225(2), 175–199 — heterogeneous-effect event study estimator (eventstudyinteract Stata command; R30-M01 增引)
- **Oster (2019)** JBES 37(2), 187–204 — δ coefficient stability with omitted variables
- **Romano & Wolf (2005)** Econometrica 73(4), 1237–1282 — stepwise multiple hypothesis testing (rwolf)
- **Roodman, Nielsen, MacKinnon, Webb (2019)** Stata Journal 19(1), 4–60 — wild cluster bootstrap inference (boottest Stata command; R31-M01 增引)
- **Roth (2022)** AER:Insights 4(3), 305–322 — "Pretest with Caution" (pre-trend testing pitfalls)
- **Rambachan & Roth (2023)** RES 90(5), 2555–2591 — honest DiD / robust confidence sets under smoothness restrictions
- **Loughran & McDonald (2011)** JF 66(1), 35–65 — financial dictionary (P1 对照基准)
- **Tetlock (2007)** JF 62(3), 1139–1168 — media tone → returns (P1 对照基准)
- **Engelberg, Reed, Ringgenberg (2018)** JFE 130(3), 532–555 — banking text exemplar (P1/P2 JCF-style exemplar)
- **Goldstein, Jiang, Karolyi (2019)** RFS 32(5), 1647–1661 — fintech special issue (P4 对照 / RFS-style exemplar)
- **Florackis, Louca, Michaely, Weber (2023)** RFS 36(1), 351–407 — cybersecurity exposure (P2 对照)
- **Cong & He (2019)** RFS 32(5), 1754–1797 — blockchain disruption (P4 对照; R1-M03 替换 v2.0 中的 unverifiable Cong-Xie-Zhang 2024 引文)
- **Cong, Li, Wang (2021)** RFS 34(3), 1105–1155 — tokenomics (P4 备选对照)
- **Goldstein, Spatt, Ye (2021)** RFS 34(7), 3213–3225 — big data in finance editorial (P4 对照)
- **Hsieh & Klenow (2009)** QJE 124(4), 1403–1448 — 中国单国上 top journal 的范本 (R1-M04 替换 v2.0 中错误的 Hau-Huang-Shan-Sheng 2019 RFS 引文; 实际 Hau et al. 论文为 JF 2024 79(2), 与本 plan identification 设计不直接相关)
- **Allen, Qian, Qian (2005)** JFE 77(1), 57–116 — 中国 law-finance-growth (中国单国上 top journal 的另一范本)
- **Bromiley & Rau (2014)** SMJ 35(8), 1249–1256 — practice-based view of strategy (P3 SMJ-style exemplar)
- **Baron & Kenny (1986)** Journal of Personality and Social Psychology 51(6), 1173–1182 — canonical mediation analysis framework (P2/P4 16_mechanism, R32-M01 增引)
- **Imai, Keele, Tingley (2010)** Psychological Methods 15(4), 309–334 — causal mediation analysis sensitivity (P2/P4 16_mechanism, R32-M01 增引)
- **Chesbrough (2003)** *Open Innovation: The New Imperative for Creating and Profiting from Technology* HBS Press — P5 主框架 (v3.4.0 epoch 5 增引; closed vs open innovation paradigm)
- **Laursen & Salter (2006)** SMJ 27(2), 131–150 — "Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms" (P5 search breadth & depth canonical, v3.4.0 epoch 5 增引)
- **Hagedoorn (2002)** Research Policy 31(4), 477–492 — inter-firm R&D partnerships 1960-1990 (P5 secondary anchor, v3.4.0 epoch 5 增引)
- **Cohen & Levinthal (1990)** ASQ 35(1), 128–152 — absorptive capacity (P5 salvage path anchor: Research Policy submission; v3.4.0 epoch 5 增引)
- **Nosek, Ebersole, DeHaven, Mellor (2018)** PNAS 115(11), 2600–2606 — "The preregistration revolution" (additive vs revisionary adjustment; v3.4.0 β supplementation 锚定 per wz_framework §4 增引)

### 2.4 Citations explicitly NOT invoked (避免与现有 paper 冲突)

- **Han et al. (2024)** RFS — 已锚定 `brokerage_network/` paper，不在 B 路线 5 paper 内重用 (v2.56 epoch 5 含 P5)
- **Cao, Li, Wang, Zhao (2025)** RAS — 已锚定 `llm_peer/`
- **Jha, Liu & Manela (2026)** RFS §1.3.2 — 已锚定 `benefit_society/`
- **Guzman & Li (2023)** MS — 已锚定 `strategic_diff/`

---

## 3. 四篇论文最终定位

### 3.1 论文标识与差异化

| ID | Paper module | 核心维度 | Anchor 文献 | 投稿 outlet 主推 | Backup outlet |
|---|---|---|---|---|---|
| **P1** | `bank_fintech_tone` | 媒体语调（情感）| Tetlock 2007 + Loughran-McDonald 2011 + 自有 llm_peer disagreement | **JFQA** | JCF / JBF |
| **P2** | `bank_fintech_attention` (新建) | 关注度 / fintech exposure | Hassan 2019 QJE + Florackis 2023 RFS | **JCF** | JBF / JFI |
| **P3** | `bank_fintech_substance` (新建) | 实质性 vs 象征性 | W&Z 1994/1998/2001 ASQ + Fiss-Zajac 2006 AMJ | **SMJ** | AMJ → ASQ (cascade resubmission); JFE corp finance (改写 salvage path, R3-M02) |
| **P4** | `bank_fintech_locus` (新建) | 底层技术 vs 应用场景 | Gomber 2018 JMIS + Kogan 2017 QJE + Goldstein-Jiang-Karolyi 2019 RFS | **RFS** | JFE (per §B.4 backup_outlet; JF 是 §B.4 ambitious_outlet, 见 §3.2 P4 v2 ambitious "JF (顶配)", 不重复列入 backup; R76-m01) |

### 3.2 v1 → v2 顶刊预期对照

| Paper | v1 现实顶板 | v1 ambitious | v2 现实顶板 | v2 ambitious | 修正驱动 |
|---|---|---|---|---|---|
| P1 tone | JBF / IRFA | RFS | **JFQA / JCF** | **RFS / JFE** | T=18 解锁 long-horizon return predictability |
| P2 attention | JFI / JBF | JFE / RFS | **JCF / JBF** | **JFE** | 18 年含 5 个外生冲击，可做 Hassan 风格 within-firm time variation |
| P3 substance | SMJ / AMJ | ASQ | **SMJ / AMJ** | **ASQ (cascade 终点); JFE 重写稿 (salvage path)** (顺序投稿, 见下注; R3-M02 同步) | T=18 让"长期 ROA 反转"故事成立 |
| P4 locus | JFQA | RFS / JFE | **RFS / JFE** | **JF** (顶配) | 18 年涵盖三波 fintech 浪潮 + consolidation: pre_period (2007-2012) + wave_1 (2013-2015 互联网金融) + wave_2 (2016-2018 区块链/早期 AI) + consolidation (2019-2021 蚂蚁叫停后) + wave_3 (2022-2024 大模型); R4-M03 重定义 |

**注 1 (G-1 条件)**：上调均**条件于** M-1 数据审计 G-1 pass。如果 G-1 yellow band 或
C1-C4 触发, 顶刊预期降一档 (见 §11); 如果实际 N_eff × T_eff < 1,500, 本表回退到 v1
估计 (R3-m02)。

**注 2 (P3 投稿路径; R3-M02 统一)**: P3 走双轨 cascade:
- **Primary cascade (理论纯化)**: SMJ (main) → AMJ (if SMJ reject) → ASQ (cascade 终点)
  — 完整 W&Z 实质性 vs 象征性框架, 顺序投稿不并行
- **Salvage path (任一阶段 reject 后)**: 改写为 disclosure quality 框架的**独立论文** (研究问题
  重新表述、理论 anchor 切换、outcome 仅保留 long-run ROA 反转、删除组织学叙事), 投
  JFE corp finance track
- 任何时刻仅 1 outlet 在审; 共享 panel 数据但研究问题 / 理论 / outcome 独立, 是两篇
  论文不是 dual submission, 不违反 simultaneous submission ethics。

### 3.3 与现有 4 衍生 paper 的区分原则

| 现有 paper (v3.3.0) | 核心方法 | 与 B 路线 5 paper 是否冲突 (v2.56 epoch 5 含 P5) |
|---|---|---|
| `benefit_society` | LLM-Embedding 双极锚点投影 | ✗ 不冲突，方法学完全不同 |
| `brokerage_network` | 共现网络中心性 + 二阶语调 IV | ✗ 不冲突 |
| `llm_peer` | LLM 同业竞争网络 IV | ✗ 不冲突；P1 可调用其 disagreement 框架 |
| `strategic_diff` | 多文本表征 + Bartik IV | ✗ 不冲突 |

9 paper 共用底层 `46_panel_yearly_v34.dta` (v2.56 epoch 5 含 P5 bank_fintech_collab)，但 outcome / 识别 / 度量完全异质。
M0 设计契约时强制每 paper 在 spec.yaml 声明"差异化主张"。

### 3.4 v3.3.0 panel → v34 panel 迁移路径 (R1-M05 补)

5 existing paper (P1 + 4 衍生) 已针对 v3.3.0 panel (168 obs / 2024 cols) 完成 P0-P4。
v34 panel (M0.5 输出) 是 **superset**: 行数 168 → 3000-9000, 列只增不减 (现有 2024 列
保留 + 新增稳健性 / 跨期变体列 ≤ 5000 总数)。迁移规则:

1. **列名向后兼容**: stage 46 输出强制保留 v3.3.0 全部 2024 列名 (即便部分列在新样本
   下为 NaN); 新增列以 `_v34_*` 或扩展段命名 (如 `tone_2007_2012_*`)。
2. **Stata template 验证 (R3-M05 时序修订)**: M0 G0 acceptance 仅包含 "5 existing
   paper 的 build-replication CLI 在 **v3.3.0 panel 上跑通 (regression baseline)**"
   (因为 v34 panel 在 M0.5 后才产生, M0 时不存在)。v34 panel 上的兼容验证延后到 M0.5
   G0.5 acceptance — 即 `papers/_common/stata_templates/<paper>/` 中 41 个 paper-specific
   template 全部对 v34 panel 列名 resolve 成功。
3. **Python tables.py / figures.py**: 现有 5 paper 的 Table 1 / Figure 1 输入为 v3.3.0
   schema, M0.5 后需要适配 long-panel (T=18 vs T=2) — 但由于 v34 panel 是 superset, 仅
   读取 (target_bank ∈ v3.3.0 已知 84 银行, year ∈ {2017, 2018}) 子集就能复现 v3.3.0
   baseline (R4-M06 修订: 必须同时满足 bank 子集 AND year 子集; 不仅 year)。M0.5 G0.5
   acceptance 包含 "5 existing paper 的 tables/figures 在 v34 panel 上输出 byte-identical
   或 panel-hash identical (subset to bank ∈ 84 + year ∈ {2017, 2018})"。
4. **Backward compatibility lock**: `tests/integration/test_v34_v33_subset_invariance.py`
   (新增) — 锁定 v34 panel 子集 (target_bank ∈ v3.3.0 84 银行 AND year ∈ {2017, 2018})
   与 v3.3.0 panel 在共同列上的数值一致性 (差异 ≤ 1e-9 for floats, exact for categoricals)。
   84 banks 列表来源 (R5-m02): `data/processed/40_panel_yearly.parquet::target_bank.unique()`
   (M0 G0 通过时冻结写入 `tests/fixtures/v33_banks_84.json`)。

---

## 4. 总体时间线 & Milestone Map

```
2026-05-19 ─── M-1   数据现状审计 (10 d)                              ←  G-1
2026-06-02 ─── M0    设计契约冻结  (5 d)                              ←  G0
2026-06-09 ─── M0.5  Pipeline 全量重跑 (12 wk, $4.2K, 64-core GPU)    ←  G0.5 (R3-M03: 起始日 6/9 next workday after M0 ends 6/8)
2026-09-01 ─── M1    目录骨架镜像 (8 d)                               ←  G1
2026-09-15 ─── M2    Stata 模板差异化 (8 d)                           ←  G2
2026-09-29 ─── M3    Manuscript 骨架冻结 (10 d)                       ←  G3
2026-10-19 ─── M4    外生冲击 DiD 设计 (4 wk)                         ←  G4
2026-11-16 ─── M5    主回归 / 机制 / 异质性 (8 wk)                    ←  G5
2027-01-11 ─── M6    稳健性 + Devil's Advocate (6 wk)                ←  G6
2027-02-22 ─── M7    内审 + 投稿包 (3 wk)                             ←  G7
2027-03-15 ─── M8    投稿 + post-submission monitor (持续到首次 decision) ←  G8

总周期：M-1 起 → M8 投稿 ≈ 9.5 个月 (R2-M09 修订: 与 §10.2 40.5 wk = 9.45 月对账)
对照 v1 plan：13-19 月 → v2 净缩短 3.5-9.5 个月
```

### 4.1 关键依赖

- M-1 G-1 **不通过则触发 C1-C4 应急方案**（见 §11）
- M0.5 G0.5 失败则 M1 起所有下游 milestone 暂停
- M2/M3 并行（M2 不依赖 M3，且共享 M1 输出）
- M5/M6 强耦合（M6 反馈可能触发 M5 局部重做）
- M7 内审失败可循环回 M5/M6 任意次（multi-round audit per memory `prefers_rigorous_multi_round_audits`）

### 4.2 关键路径 (critical path)

```
M-1 → M0 → M0.5 → M2 → M4 → M5 → M6 → M7 → M8
```

M0.5（12 周 Pipeline 重跑）是**单点最长依赖**。M1/M3 在 M0.5 期间可部分提前启动
（写"骨架"不依赖最终 panel；Table 1 留 placeholder）。

---

## 5. 详细 Milestone 说明

### 5.1 M-1 数据现状审计 (2026-05-19 → 2026-05-30, 10 working days 含两端)

#### 5.1.1 目标

把"40 万条 / 500 银行 / 18 年"从一个数字变成可信的 N_eff × T_eff 估计；
确认 raw → panel 转化率；识别覆盖空洞；锁定 Go/No-go 决策。

#### 5.1.1.bis 前置 prerequisite (R1-M21 补)

M-1 启动前必须由用户 (经 D1) 明确提供:

1. **Raw 40 万条语料的物理位置 / 访问方式**: 磁盘绝对路径 / 数据库连接串 / API endpoint
2. **访问凭证**: 数据库 read 用户 / API key / 商业授权号
3. **数据元信息**: 原始 schema 文档 (字段含义) + 来源 (CNRDS / Wind / 巨灵 / 自建爬虫
   / 多源拼接) + 时间戳 + 抓取 cutoff date
4. **法律授权链初稿**: 数据采集合规来源声明 (即使初稿, 可在 M-1.7 补充)
5. **CSMAR/Wind 银行模块访问凭证** (M-1.2 / M-1.6 银行实体匹配率审计需要)

**无此前置 M-1 不启动**。如缺凭证则 M-1 进入 hold, 同步触发 D1 决策点 (用户提供 / 替换数据源 / 启动 C1 fallback)。

#### 5.1.2 子任务

| ID | 任务 | 交付 |
|---|---|---|
| M-1.1 | Raw 语料盘点 | 物理位置、schema、字段、时间分布、银行覆盖统计 |
| M-1.2 | 银行实体匹配率审计 | 500 银行 ID → CSMAR/Wind 财务库匹配率（按 4 类银行：国有 6 + 股份制 12 + 城商行 ~130 + 农商行 ~350）|
| M-1.3 | 覆盖热力图 | bank × year 报道数热力图（500 × 18 = 9000 cells）|
| M-1.4 | Fintech 关键词跨期演化 | 2-year 窗口 lexicon 聚类，识别"金融科技"概念何时进入 |
| M-1.5 | Pipeline scale test | 抽 1% raw (~4000 条) 全程跑 pipeline，估计 raw → 21_tone → 40_panel 转化率 |
| M-1.6 | Financial controls 可得性 | CSMAR/Wind 银行模块 × 500 家 ID 交叉表 |
| M-1.7 | 数据来源 & 法律合规清单 | 数据采集方式、授权链、ToS 风险评估 |

#### 5.1.3 交付

- `docs/audit/M-1_data_reality_check.md`（待创建; 文件尚未存在, 链接为 placeholder）
  - 7 张数据表
  - 5 张图（含 bank × year 覆盖热力图、年度报道量趋势、银行类型分布等）
  - N_eff × T_eff **95% 置信区间**（如 "3,200 ± 1,500 obs"）
  - Pareto 曲线："去掉哪 N 家最薄的银行后剩余 panel 健康度最高"
  - Go / No-go decision matrix
- `scripts/audit/data_reality_check.py` — 一键复现整份审计
- `data/audit/M-1/` — 中间产物（热力图原始数据、匹配表）

#### 5.1.4 Acceptance gate G-1

| 检查项 | 通过条件 | 失败 → 应急 |
|---|---|---|
| Raw 语料完整性 | 400K ± 5% 可访问 (yellow band [50%, 95%) → C1-c 软 fallback per R59-M01) | C1-a (raw <50%) / C1-c (raw 50-95%) |
| 时间覆盖完整性 (R60-m01 新增) | 无 > 2 年系统性时间断层 (per M-1.3 覆盖热力图 bank × year) | C1-b (时间断层 > 2 年) |
| 银行实体匹配率 | 财务数据匹配 ≥ 60% (yellow band [40%, 60%) → C2-lite) | C2 (< 40%) |
| Pipeline scale test | 1% 样本能完整跑通 21→46 stage | C3 (pipeline 失稳) |
| LLM 跨期一致性预估 | 2007-2010 段抽 100 样本 prompt v7 输出 valid_response_rate ≥ 80% | C4 (LLM 跨期失效) |
| 法律合规 | 数据来源 + 授权链可披露 | 暂停 M0，先解决合规 |

#### 5.1.5 Audit 轮次：8 轮 (R1-M24 上调; 与 plan v14 9 轮均值 / benefit_society v2.12 14 轮 对齐)

| 轮 | 焦点 | 工具 |
|---|---|---|
| A-1.1 | 覆盖率盘点正确性 | 手算对照 5 家银行 |
| A-1.2 | 匹配率算法公平性 | bank ID normalize 规则审查 |
| A-1.3 | 时间漂移分析（fintech 概念演化）| 跨期 lexicon Jaccard |
| A-1.4 | 数据来源合规性 | 法律语言抽查 |
| A-1.5 | Pareto 曲线收敛性 | 不同 cut-off 敏感性 |
| A-1.6 | 财务匹配率边界 audit (yellow band [40%, 60%) 行为) | 触发 G-1 conditional pass / C2-lite 分支 |
| A-1.7 | 数据来源 + 法律合规交叉 audit | ToS 摘录 × 商业授权链 × 投稿期刊 replication policy |
| A-1.8 | C1-C4 应急触发条件可执行性 audit | 每条 trigger 用 1% 抽样模拟验证 |

### 5.2 M0 设计契约冻结 (2026-06-02 → 2026-06-08, 5 working days 含两端)

#### 5.2.1 目标

基于 G-1 通过的 N_eff × T_eff 区间，冻结 v2.55 8 paper (3 新 + 5 现有 retrofit) + v2.56 epoch 5 第 9 paper P5 = 9 paper 的工程契约。

#### 5.2.2 子任务 (R1-M10 修订)

| ID | 任务 | 交付 |
|---|---|---|
| M0.1a | 起草 3 新 paper 的 `paper_spec.yaml` | `papers/bank_fintech_{attention,substance,locus}/paper_spec.yaml` |
| M0.1b | Retrofit 5 现有 paper 的 `paper_spec.yaml` | `papers/{bank_fintech_tone,benefit_society,brokerage_network,llm_peer,strategic_diff}/paper_spec.yaml` (从 README + 现有代码反推 spec) |
| M0.2 | 扩展 `paper_registry.py` | 9 paper 注册（v2.55: 5 paper auto-registered + 3 new + v2.56 epoch 5: P5 bank_fintech_collab）|
| M0.3 | 9 paper 列名冲突扫描 | `tests/integration/test_paper_namespace_isolation.py` |
| M0.4 | 锁定外生冲击事件库 | `config/exogenous_shocks.yaml`（含 5 个事件 + 时间窗 + identification strategy per event, 见 §5.7.2）|
| M0.5 | M0.5 Pipeline 重跑配置 | `config/pipeline_v34_rerun.yaml` |
| M0.6 | Git tag `B-route-v2-frozen` | 锁定本 plan v2.x + 8 spec |

#### 5.2.3 `paper_spec.yaml` 模板

**注 (R16-m01)**: 下方 example 为 schema demonstration template; 最终 9 paper (v2.56 epoch 5 含 P5) 各自 spec
见 Appendix B; status `skeleton` 仅用于 schema 演示, 实际 spec status 为 `existing`
(5 现有 paper) 或 `new` (3 新 paper)。

```yaml
paper_id: bank_fintech_attention
spec_version: 2.0.0  # R13-M01 同步 §B specs naming (spec_version not version)
status: skeleton  # demonstration only; actual P2 spec status = "new" (见 §B.2)
# authors field 可选 (R13-m01: §B specs 默认无 author 字段)

# R13-M01 flatten: differentiation_claim 在顶层, theory.anchors 仅 optional metadata
differentiation_claim: |
  P2 与 P1 (tone) 的差异：P2 度量"曝光强度"而非"情感方向"；
  与现有 brokerage_network 的差异：P2 不构造网络中心性，仅用 firm-level attention。

theory:  # optional metadata
  primary_anchors:
    - Hassan-Hollander-van Lent-Tahoun 2019 QJE
    - Florackis-Louca-Michaely-Weber 2023 RFS
  secondary_anchors:
    - Gomber 2018 JMIS

# R46-M01 修订: outcome / mediator / treatment / controls 提升到顶层 (与 §B specs + §5.2.3.bis schema 一致, 删除原 variables: wrapper); R64-M01: mediator 移到 outcome 后 treatment 前 (与 §B.4 + schema R63-M01 顺序一致)
outcome:
  primary: ln_fintech_investment
  secondary: [m_and_a_fintech, patent_fintech_count, employee_growth_it]  # R47-M05 同步 §B.2 命名 (patent_fintech → patent_fintech_count)
  enrichment_source: M0.5.11 (CSMAR 年报 ln_fintech_investment / Tonghuashun M&A / IncoPat patent / CSMAR employee)  # R47-M02 增 enrichment_source 字段 (schema required, R8-M04)
mediator:  # R8-M01 + R64-M01: mediator 紧跟 outcome (causal chain proximity; 与 schema + §B.2 + §B.4 一致)
  primary: ln_fintech_mdna_length
  source: 银行年报 MD&A 章节文本长度 (enrichment M0.5.11)
treatment:
  primary: attention_index_full
  secondary: [attention_index_ctx, attention_disp_full, attention_pct_full]  # R3-m04 同步 §B.2
  source: stage 14_fintech_intensity 衍生 (R36-m01: 4 attention 度量: index_full / index_ctx / disp = dispersion, pct = percentile; M0 G0 时按 14_fintech_intensity.parquet schema 对齐 actual column names)
controls:
  bank_level: [ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth]  # R1-M13: roa 移除避免与 outcome.secondary 重复
  year_level: [gdp_growth, m2_growth]
  fixed_effects: [bank_fe, year_fe]

identification:
  baseline: staggered_did_callaway_santanna_2021
  iv:
    # R1-M22 修订: Bartik IV 需 shift-share 结构; 默认 fall back 到 leave-one-out peer IV
    primary: leave_one_out_peer_attention_iv  # Cao 2025 RAS 风格, firm-level 兼容
    fallback: bartik_attention_iv  # 仅当 pre-2007 bank fintech-lending share (CSMAR) 可得时启用; shift = national fintech regulatory event density × share

event_studies:  # R2-M05 + R45-m03 + R66-M01 修订: top-level (去缩进, 与 schema + §B specs 4 处一致); 引用 Appendix C events by id
  - E1   # 2013-06-13 yuebao_launch — post dummy × bank pre-2012 fintech-exposure (Hassan-style)
  - E2   # 2016-08-24 p2p_regulation — bank-level continuous exposure
  - E4   # 2020-11-03 ant_ipo_pause — bank-level continuous exposure
  - E5a  # 2022-09-01 data_export_assessment_rules — binary treated (跨境业务 dummy)
  - E5b  # 2023-09-30 data_export_management_rules — binary treated (复合 E5a)
  # 注: P2 不适用 E3 (资管新规对所有银行同时生效, 对 attention 度量无 cross-sectional intensity)

# R47-M04 删除: stata_templates block 不在 schema, 也不在 §B specs; Stata template association 由 M2 build-replication CLI 自动处理, 不需在 spec.yaml

targets:
  primary_outlet: JCF
  secondary_outlet: [JBF, JFI]
  ambitious_outlet: JFE
  submission_window: 2027-03-15

sample:
  n_bank_min: 200  # 数据审计 G-1 确认后填
  t_year: 18
  obs_target_min: 3000

audit_rounds_target_min: 8  # R1-m06 + R24-m01: M5 阶段每 paper ≥ 8 轮 (§5.8.4); M6 阶段每 paper ≥ 5 轮 (§5.9.5)
```

#### 5.2.3.bis paper_spec.yaml schema reference (R12-M01 显式 schema)

完整 allowed fields 与 optionality 参考 (每 paper spec 必须 conform):

```yaml
# Required fields (all 9 papers; v2.56 epoch 5 含 P5 bank_fintech_collab)
paper_id: str
spec_version: semver (e.g. 2.0.0)
status: enum [existing, new, skeleton]
authors: list[str]                # optional (R13-m01: §B specs 默认无 authors)
differentiation_claim: multiline str  # 必含 vs 其他 7 paper 差异声明 (R13-M01 flatten 到顶层)
theory:                           # optional metadata
  primary_anchors: list[str]
  secondary_anchors: list[str]
outcome:
  primary: str
  short_run: str             # optional (P3 dual outcome)
  secondary: list[str]
  construction: multiline str  # optional (long_run_roa_change_3yr 公式)
  enrichment_source: str       # 必须指向 M0.5.11
  patent_quality_measure: str  # optional (P4-specific)
mediator:                      # R63-M01 移到此处 (与 §B.4 P4 spec 顺序一致): mediator 紧跟 outcome (causal chain proximity); optional (P2, P4 有; P1/P3 无)
  primary: str
  secondary: str               # optional
  source: str
treatment:                     # R15-m01 多态结构: 选一
  # (a) primary + alternative (P1, P3 style)
  # (b) primary + secondary (P2 style)
  # (c) primary_pair + secondary (P4 style)
  primary: str                 # or primary_pair: list[str] (P4)
  primary_pair_construction: dict[str, str]  # P4-specific, optional (R35-M02 formula for derived primary_pair from existing pipeline column)
  alternative: list[str]       # P1, P3 only
  alternative_construction: dict[str, str]  # P3-specific, optional (formula for derived alternatives)
  secondary: list[str]         # P2, P4 only
  secondary_construction: dict[str, str]    # P4-specific, optional (formula for derived secondaries)
  source: str                  # optional (R37-M01), metadata 标注 treatment 数据来源 (pipeline stage / file)
controls:                      # R9-M01 强制
  bank_level: list[str]
  year_level: list[str]
  fixed_effects: list[str]
identification:
  baseline: str
  iv:                          # R15-M01 标 optional (P1/P2/P4 有; P3 不需 IV)
    primary: str
    fallback: str              # optional
event_studies: list[str]       # R65-M01: 去缩进, top-level (与 §B.1/B.2/B.3/B.4 specs 4 处一致); 每 entry = 事件 ID, per §5.7.2
heterogeneity_wave: dict                   # optional, P4-specific (R57-m01 移到 event_studies 后 targets 前; R49-m01 explicit; R4-M03 schema)
targets:
  primary_outlet: str
  secondary_outlet: list | str  # optional
  ambitious_outlet: list | str             # R75-m01: list 形式与 backup_outlet (R50-M01) schema parallel, 容纳 multi-tier ambitious (如 P1 [RFS, JFE]); 单 outlet 可继续用 str
  backup_outlet: list | str                # optional (R50-M01: 支持 list 与 secondary_outlet schema 一致, 容纳 cascade alternatives)
  sequential_resubmission: multiline str   # optional, P3-specific (R49-m01 explicit)
  submission_window: date
sample:
  n_bank_min: int              # 数据审计 G-1 后填
  t_year: int
  obs_target_min: int
tables:                        # v3.5.0 新增 (per stage3_v3_5_0_augmentation_plan §5 B-NEW-4 + F2): 显式声明各 paper Table 渲染配置, 防 schema test fail
  t1: dict | null              # optional, Table 1 descriptives (复用 10_table1_descriptives.do.tmpl 默认; spec 可 override)
  t6:                          # v3.5.0 D2 cell decomposition Table 6 字段 (P3/P4/P5 主用; 其余 6 paper 必须 explicit null)
    template: str | null       # 模板名 (e.g., '19_table6_cell_decomposition'); null 表示该 paper 不渲染 Table 6
  # v3.5.1 A1 + A3 appendix tables (per stage3_v3_5_1_a1_a3_supplementation_plan §1.3 + R6-C1 schema 授权)
  tA7:                         # v3.5.1 A1 Lexical Clarity Robustness (P3/P4/P5 主用; 其余 6 paper explicit null)
    template: str | null       # e.g., '21_substance_clarity_robustness'; null = 该 paper 不渲染
    clarity_robustness: dict | null  # optional clarity_robustness 配置 (spec 可 override)
  tA8:                         # v3.5.1 A3 Numerical Intensity (benefit_society 主用; 其余 8 paper explicit null)
    template: str | null       # e.g., '19_bs_num_intensity_robustness'; null = 该 paper 不渲染
    num_intensity_robustness: dict | null
  tA9:                         # v3.5.1 A3 Numerical Intensity (P1 bank_fintech_tone 主用; 其余 8 paper explicit null)
    template: str | null       # e.g., '27_tableA9_num_intensity'; null = 该 paper 不渲染
    num_intensity_robustness: dict | null
  # 其它 t* / tA* 字段保留未来扩展, schema 不强制
audit_rounds_target_min: int   # ≥ 8 per memory `prefers_rigorous_multi_round_audits`
```

M0 G0 acceptance 包含 "9 paper × spec.yaml 全部 conform 此 schema" 检查 (v2.56 epoch 5 含 P5; v3.5.0 新增 `tests/integration/test_paper_spec_schema.py` 覆盖 9 paper × `tables.t6` 字段 — P3/P4/P5 模板存在性 + 其余 6 paper null 显式声明; **v3.5.1 扩展覆盖 `tables.tA7/tA8/tA9`** — A1 clarity (tA7: P3/P4/P5 主用) + A3 num_intensity (tA8: benefit_society 主用; tA9: P1 主用) + 其余 paper explicit null)。

#### 5.2.4 Acceptance gate G0

| 检查项 | 通过条件 |
|---|---|
| 9 份 spec.yaml (3 新 + 5 retrofit + v2.56 epoch 5 P5) | schema 校验 pass + 字段完整 + differentiation_claim 互不冲突 |
| `paper_registry.py` | 9 paper 注册 + 唯一性约束 (v2.56 epoch 5 含 P5) |
| 列名冲突 | 0 冲突 (跨 9 paper) |
| 5 existing paper 兼容性 | 5 existing 的 build-replication CLI 在 v3.3.0 panel 上跑通 (M0.5 重跑前的 regression test) |
| LLM cost cap | **$5,000 锁定** per §10.1 budget + §8 R10 mitigation (v3.4.0 Q-B 2026-05-17: 4200→5000; R19-m01 + R78-m01 + F-211 epoch 5 同步 §6 G0 row) |
| Git tag | `B-route-v2-frozen` 已打 |

#### 5.2.5 Audit 轮次：3 轮 (R46-m01 列举)

| 轮 | 焦点 |
|---|---|
| A0.1 | 8 spec.yaml schema conformance + differentiation_claim 7-paper 对称 |
| A0.2 | paper_registry 8 paper 唯一性 + 列名冲突扫描 |
| A0.3 | 5 existing build-replication 在 v3.3.0 panel pass + git tag |

### 5.3 M0.5 Pipeline 全量重跑 (2026-06-09 → 2026-08-31, 12 weeks; R3-M03 修订起始日; R9-M02 解释 critical path)

**Critical path 说明**: M0.5 子任务 wall-time (per §5.3.2) sub-task sequential 总和 = 1+1+1+**4**+1+2+1+2+1 = 14 wk; M0.5.10 (1 wk 跨期 prompt 测试, 并行) + M0.5.11 (2 wk financial enrichment, 并行) 同时 running during M0.5.4 (4 wk LLM API wait) → critical path 缩短为 **14 - 2 = 12 wk**。如 M0.5.4 LLM API 延期, M0.5.10/M0.5.11 并行节省可能不足, total 可达 13-14 wk (R11 trigger 14 wk threshold)。

#### 5.3.1 目标

把 40 万 raw 推到 `46_panel_yearly_v34.dta`，列数预算 ≤ 5,000，行数预算 3,000 - 9,000。

#### 5.3.2 子任务

| ID | 任务 | wall-time | 资源 |
|---|---|---|---|
| M0.5.1 | Raw 入库 + 00_preprocessing 全量 | 1 wk | CPU |
| M0.5.2 | 11_bank_news / 12_fintech_news 过滤 | 1 wk | CPU |
| M0.5.3 | 14_fintech_intensity / 15_article_alignment | 1 wk | CPU + embedding API |
| M0.5.4 | **21_tone_llms 全量** | 4 wk | LLM API ($2,400) |
| M0.5.5 | 22_words_tone | 1 wk | CPU |
| M0.5.6 | **23_bert_tone 全量** | 2 wk | GPU 64-core |
| M0.5.7 | 24_herd_decay | 1 wk | CPU |
| M0.5.8 | 32a / 33-39 sentiment + innovation tracks | 2 wk | LLM API + GPU |
| M0.5.9 | 40-46 panel + Stata export | 1 wk | CPU |
| M0.5.10 | 跨期 prompt 稳健性测试 | 1 wk（并行）| LLM API |
| M0.5.11 (R4-M05 + R5-M01 + R11-m01 修订) | Financial / market / patent data enrichment: 从 CSMAR (上市银行年报 ROA / loan_growth / 资本充足率 / NPL + **daily stock returns 模块**) + Wind (非上市银行季报合并到年报 + 日行情) + IncoPat / 国家专利局 (fintech 专利 + Kogan 2017 market value 算法) + Tonghuashun 财讯 (M&A 事件 + 历史日行情备份); 输出 `data/processed/v34/47_financial_outcomes_panel.parquet`; **daily stock returns 单独存 `data/processed/v34/48_daily_returns_panel.parquet`**; **并衍生 event-window CAR variables (R11-m01)**: (a) `car_3day_window_tone_shock` for P1 (基于 tone shock 事件 timing × 3-day daily returns + market-adjusted abnormal returns); (b) `car_3day_window_fintech_announcement` for P3 (基于 fintech 公告事件 timing × 3-day daily returns); (c) `car_5day_window` for P4 (基于 fintech-related events × 5-day daily returns); CAR construction 用 market-adjusted model (中证银行指数 as benchmark) | 2 wk (并行) | CPU + database query |

#### 5.3.3 关键风险缓解

- **R4 应对**（fintech 概念跨期演化）：抽 2007-2010 / 2011-2014 / 2015-2018 / 2019-2024 四段各 500 样本，分段验证 prompt v7 标注一致性 ≥ 0.7 (Cohen's κ)
- **R5 应对**（LLM 跨期稳定性）：每段固定 seed + temperature=0 + 三家族 LLM 投票
- **R6 应对**（unbalanced panel）：保留 `46_panel_yearly_v34_unbalanced.dta` 与 `..._balanced.dta` 两版

#### 5.3.4 交付

- `data/processed/v34/46_panel_yearly_full.parquet` + `.dta`
- `data/processed/v34/46_panel_yearly_core.dta` + `_aux.dta`（IC 兼容）
- `data/processed/v34/46_codebook_v34.xlsx`
- `data/processed/v34/46_panel_yearly_v34_balanced.dta` (R5-M03: only banks with 全 18 年观测; 用于 R6 缓解 + Sample cuts 稳健性)
- `data/processed/v34/46_panel_yearly_v34_unbalanced.dta` (R5-M03: 含所有有 ≥ 1 年观测的银行; 主 spec)
- `data/processed/v34/47_financial_outcomes_panel.parquet` (R4-M05: financial / market / patent enrichment, M0.5.11 产出)
- `data/processed/v34/48_daily_returns_panel.parquet` (R5-M01: daily stock returns, P4 car_5day_window 依赖)
- `data/processed/v34/21_tone_llms_lineage_v34_<timestamp>.json` (≥ 3 family × 全 sample)
- `tests/fixtures/golden_panel_v34.json` — 新 golden baseline
- `scripts/migrate/v3_3_to_v3_4_panel_upgrade.py`（参考现有 v3_1_to_v3_2 migrator）
- 跨期 κ 报告 `eval_reports/cross_era_kappa_v34.json` + `.tex`

#### 5.3.5 Acceptance gate G0.5

| 检查项 | 通过条件 |
|---|---|
| `tests/integration/test_panel_reproducibility_v34.py` | pass |
| 跨期 LLM κ | ≥ 0.7 (按 4 段分别) |
| 4 类银行 × 18 年覆盖热力图 | 无系统空洞（每 cell 至少 1 报道或显式标注 0）|
| LLM cost | **≤ $5,000** (v3.4.0 Q-B: 4200→5000; v3.4.0 estimate $2,400 21_tone × (1 + 15%) collab_mode + $380 M0.5.8 + $50 M-1.5 + $500 M5/M6 + 25% buffer ≈ $4,480, cap $5,000 留 ~$520 裕度; v2.55 baseline $4,062 → v2.56 $4,480) |
| Pipeline 健壮性 | LLM cache HOT 时: panel content hash identical (排除 parquet metadata 时间戳); LLM cache COLD (重抓全量) 时: panel content hash 差异 ≤ 0.1% rows (温和 stochasticity 容差) |
| v3.3.0 兼容 (R1-M05 + R4-M06 完整化) | `tests/integration/test_v34_v33_subset_invariance.py` pass (v34 panel subset to **target_bank ∈ v3.3.0 84 银行 AND year ∈ {2017, 2018}** 与 v3.3.0 panel 在共同列上数值一致: float 差异 ≤ 1e-9, categoricals exact) |

#### 5.3.6 Audit 轮次：6 轮

| 轮 | 焦点 |
|---|---|
| A0.5.1 | 覆盖率 vs M-1 预测一致性 |
| A0.5.2 | 列对齐 (与 v3.3.0 panel 的 schema diff) |
| A0.5.3 | 时间错配（年度切分规则）|
| A0.5.4 | 缺失模式 (MCAR / MAR / MNAR 诊断) |
| A0.5.5 | Outlier (winsorize 1% / 5% 敏感性) |
| A0.5.6 | 跨期 LLM 一致性 |

### 5.4 M1 目录骨架镜像 (2026-09-01 → 2026-09-12, 8 working days)

#### 5.4.1 目标

3 个新 paper（bank_fintech_attention / substance / locus）在 `papers/` 和
`papers_assets/` 下落地，与 benefit_society / brokerage_network / strategic_diff /
llm_peer 完全对称。

#### 5.4.2 逐 paper 交付 (×3)

```
news_process/papers/<name>/
├── __init__.py
├── analysis.py        # CLI: --stage pipeline|tables|figures|all
├── tables.py          # Table 1 long-panel descriptive (镜像 benefit_society/tables.py 但支持 T=18)
└── figures.py         # Figure 1 核心变量分布 + 时间趋势

news_process/papers_assets/<name>/
├── README.md          # 镜像 bank_fintech_tone/README.md 结构
├── do/                # paper-specific override .do (M2 阶段填)
├── drafts/
│   ├── en/manuscript.tex + refs.bib   # 12 TODO 占位
│   └── zh/manuscript.tex + refs.bib
└── output/            # gitignored
```

#### 5.4.3 共享 vs paper-specific 划分

| 资产 | 共享位置 | Paper-specific 位置 |
|---|---|---|
| Long-panel descriptive 通用模板 | `papers/_common/tables.py::long_panel_table1` (新增, 与现有 `tables.py` 函数共存) | 各 paper `tables.py` 调用 |
| Time-trend figure 通用 | `papers/_common/figures.py::time_trend_figure` (新增, 与现有 `figures.py` 函数共存) | 各 paper `figures.py` 调用 |
| 14 共享 Stata templates | `papers/_common/stata_templates/*.do.tmpl` | 不复制 |
| 主回归 / 机制 / 异质性 / 稳健性 .do (R1-M26 修订) | – | `papers/_common/stata_templates/<paper_id>/<NN>_<name>.do.tmpl` (与现有 4 衍生 paper 同位置约定) |
| Ad-hoc paper-only override .do (非模板) | – | `papers_assets/<name>/do/` (现有约定: bank_fintech_tone 2 个 / benefit_society 1 个 / brokerage_network 1 个 / strategic_diff 2 个; llm_peer 0 个) |
| Manuscript | – | `papers_assets/<name>/drafts/{en,zh}/` |

#### 5.4.4 Acceptance gate G1 (R2-M06 修订)

| 检查项 | 通过条件 |
|---|---|
| `python -m news_process.papers._common.stata_runner list-templates --verbose` | 列出 8 paper × N templates |
| `python -m news_process.papers.bank_fintech_attention.analysis --stage tables` | 跑通 Table 1 |
| Manuscript 数 | **6 new manuscript skeleton created** (3 new × en/zh) + **10 existing manuscript regression test pass** (compile state 未被 panel 升级或 M1 改动 break); 总 16 manuscript visible 但 M1 实际产出 6 |
| `pytest tests/test_papers_b_route.py` | pass |

#### 5.4.5 Audit 轮次：5 轮

| 轮 | 焦点 |
|---|---|
| A1.1 | bank_fintech_attention 单独 audit |
| A1.2 | bank_fintech_substance 单独 audit |
| A1.3 | bank_fintech_locus 单独 audit |
| A1.4 | 8 paper 资产对称性交叉 audit (重要) |
| A1.5 | 与 benefit_society v2.12 14-round audit 标准对照 |

### 5.5 M2 Stata 模板差异化 (2026-09-15 → 2026-09-26, 8 working days)

#### 5.5.1 目标

3 个新 paper 各自的 "主回归 + 机制 + 异质性 + 稳健性" 四件套，必要时叠加 paper-specific 第 5 件。

#### 5.5.2 每 paper 必产模板 (R1-M26 修订位置约定)

位置约定: 全部新增 paper-specific 模板放在 `papers/_common/stata_templates/<paper_id>/`, 与
现有 benefit_society (17) / brokerage_network (8) / llm_peer (8) / strategic_diff (8) 同。

通用 orchestrator 对 (RR7-2 补; 与 4 existing 衍生 paper 同模式):

| 模板 (位于 `papers/_common/stata_templates/<paper_id>/`) | 作用 |
|---|---|
| `00_master.do.tmpl` | replication 入口; 设置 `$repl_root` / `$data_dir` / `$tables_dir` / `$figures_dir` globals + 链式 do 01-19 (per benefit_society/00_master.do.tmpl L26 pattern) |
| `01_data_prep.do.tmpl` | load panel.dta + `xtset bank_id year` + 设置 `$controls` global + required-variable existence check + winsor2 |

通用四件套：

| 模板 (位于 `papers/_common/stata_templates/<paper_id>/`) | P2 attention | P3 substance | P4 locus |
|---|---|---|---|
| `15_<paper>_main_regression.do.tmpl` | staggered DiD baseline | within-bank within-year FE | layer × time event study |
| `16_<paper>_mechanism.do.tmpl` (R6-M01 + R7-M01/M02/M03 + R11-m02 修订: 真正的中介或 dual outcome 测试) | attention → fintech 战略披露文本长度 (`ln_fintech_mdna_length`, observable proxy from 年报 MD&A) → fintech investment (Baron-Kenny 1986 mediation + Imai-Keele 2010 sensitivity) | **dual outcome regression** (短期 CAR + 长期 ROA 反转, 二者反向预期, 共同检验 W&Z 1994 实证机制; 不是经典 mediation; template naming `16_substance_mechanism` 仅维持 M2 stata templates 命名一致性, Stata 文件内部头部注释明确 "此 paper 用 dual outcome regression 而非 mediation analysis", R11-m02) | locus → R&D / IT capex (mediator, observable from CSMAR) → patent + stock return (Baron-Kenny + Imai-Keele) |
| `17_<paper>_heterogeneity.do.tmpl` (R6-M03/M04 修订: 各 paper 丰富异质性切分; R7-m01 small-cell 警告) | 4 银行类型 × fintech wave (per §B.4) + SOE × non-SOE | 4 银行类型 × SOE × non-SOE + fintech wave 分段 + 资本充足率 quartile + pre-2013 fintech 暴露度 | 三波 fintech 浪潮 (wave_1/2/3 + consolidation per §B.4 R4-M03) + SOE × non-SOE |
| `18_<paper>_robustness.do.tmpl` (R6-M02 修订: 对齐 §5.9.2 全 7 维度) | §5.9.2 通用 7 维 (Oster δ + rwolf + Honest DiD + wild bootstrap + ritest + spillover + sample cuts) + paper-specific alternative measure | 同上 + alternative substantiveness track | 同上 + alternative locus classifier + Borusyak DiD (额外) |

**Small-cell warning (R7-m01)** (R46-M02 移到表格后): 异质性切分按全笛卡尔积过细 (例 P3 = 4 类型 × 2 SOE × 5 wave × 4 quartile = 160 cells; N≈3600 → 平均 22 obs/cell, 部分 cell < 10)。
实际实施: 每次仅切 1-2 dim, **不**用全笛卡尔积; 任何 cell N < 10 obs 不报告或加 caveat。

**Wave segment 使用方式 (R10-m03)** (R46-M02 移到表格后): 5 segments (pre_period / wave_1 / wave_2 / consolidation / wave_3) 实施方式:
- (a) **主**: treatment × wave_dummies interaction (4 个 dummy + reference = pre_period) → wave-specific marginal effect on outcome
- (b) **Robustness**: sample cut by wave → wave-by-wave separate regression
不直接用 5 wave 与其他维度全笛卡尔积。

Paper-specific 第 5 件:

| Paper | 额外模板 | 目的 |
|---|---|---|
| P2 attention | `19_attention_iv_first_stage.do.tmpl` | leave-one-out peer / Bartik IV first stage (按 spec.yaml IV 选择) |
| P3 substance | `19_substance_lr_reversal.do.tmpl` + `20_substance_disclosure_quality.do.tmpl` | 长短期 ROA 反转 + 与 disclosure 协方差 |
| P4 locus | `19_locus_event_study.do.tmpl` | layer-specific event study (5 个外生冲击) |

#### 5.5.3 Stata templates 总数预测 (R1-M01 + R1-M27 + RR6-1 修订; v2.56 epoch 5: +P5 7)

```
v3.3.0 实测:  55 templates = 14 root shared + 41 paper-specific
              (benefit_society 17 + brokerage_network 8 + llm_peer 8 + strategic_diff 8)
M2 新增:      3 paper × 4 common templates (15-18) = 12
            + P2 extras (1: 19_iv_first_stage) + P3 extras (2: 19_lr_reversal + 20_disclosure) + P4 extras (1: 19_event_study) = 4
            + 3 paper × 2 orchestrator (00_master + 01_data_prep, RR6-1: 与 4 existing 衍生 paper 同模式) = 6
            合计新增 22
M2 v2.55 完成预测: 55 + 22 = 77 templates
v3.4.0 (v2.56 epoch 5): + P5 bank_fintech_collab/ 子目录 7 个 (00_master + 01_data_prep + 15-19_collab_*) = 7
M2 v2.56 完成实测: 77 + 7 = 84 templates (本机 Stata MP 19.5 maxvar 120,000 余量充足; v2.56 实测验证 pytest test_total_template_count_77 已升级到 84)
```

#### 5.5.4 Acceptance gate G2 (R1-M20 修订)

| 检查项 | 通过条件 |
|---|---|
| 每 paper `build-replication` 命令 | 产出完整 replication 包 |
| 本机 Stata 19.5 跑通 | **22 个新模板** (4 common × 3 papers + 4 paper-specific extras: P2 1 + P3 2 + P4 1 + 6 orchestrator pairs RR6-1) 全 pass |
| `pytest tests/test_stata_templates.py` | pass（已有，需 extend）|
| Macro/var 截断 | 无 `set maxvar` 触顶（panel 新列数 ≤ 5000 vs MP 上限 120,000）|
| SSC 包齐全 (R1-M06) | `csdid`, `csdid_plot`, `did_imputation`, `eventstudyinteract`, `boottest`, `rwolf`, `ritest`, `honestdid` 已 installed (见 §5.7.3 SSC prerequisites) |

#### 5.5.5 Audit 轮次：4 轮 (R46-m01 列举)

| 轮 | 焦点 |
|---|---|
| A2.1 | 16 新模板 Stata 19.5 跑通 + SSC 包齐全 |
| A2.2 | 模板位置约定 (`papers/_common/stata_templates/<paper_id>/`) 与现有 4 衍生 paper 一致 |
| A2.3 | 16_mechanism / 17_heterogeneity / 18_robustness 设计与 §5.9.2 / §B.X spec 对齐 |
| A2.4 | DRY check: 新模板与 14 共享 templates 无重复 |

### 5.6 M3 Manuscript 骨架冻结 (2026-09-29 → 2026-10-10, 10 working days)

#### 5.6.1 目标

3 篇新 paper × en/zh × {abstract, intro, lit, methodology, data, results, conclusion, references} = 48 sections 骨架。

#### 5.6.2 每篇必填项

- **Abstract**: 200 英文词 / 300 中文字
- **Intro**: 5 段（research question / contribution / preview of results / theoretical contributions / roadmap）
- **Lit review**: ≥ 30 anchor (含 §2.3 中适用于本 paper 的 10-15 anchor + paper-specific 衍生 15-20: banking text 类 / W&Z 类 / fintech innovation 类, R8-m01 修订, R2-m05)
- **Methodology + Data**: 完整可复现（指向 paper_spec.yaml + M0.5 panel 路径）
- **Results / Conclusion**: 仅 `\NoteThis{...}` 占位（M5/M6 填）

#### 5.6.3 风格 calibration (R1-M16 修订: 指定 exemplar paper 而非期刊名)

- 调用 academic-paper skill 的 Style Calibration mode, 每个 paper 用具体 **exemplar paper** 作为风格参照:
  - **P4 (RFS-style)**: Cong & He (2019) RFS 32(5) "Blockchain Disruption and Smart Contracts" + Goldstein-Jiang-Karolyi (2019) RFS 32(5) editorial
  - **P3 (SMJ-style)**: Bromiley & Rau (2014) SMJ 35(8) "Towards a practice-based view of strategy" + Fiss & Zajac (2006) AMJ 49(6) (W&Z 衍生 exemplar)
  - **P1 + P2 (JCF/JFQA-style)**: Engelberg, Reed, Ringgenberg (2018) JFE 130(3) "Short-selling risk" (text-in-finance exemplar) + Florackis et al. (2023) RFS 36(1) "Cybersecurity Risk" (exposure-style exemplar)
- IRON RULE 反 anti-pattern check：
  - 禁止 "novel"、"unprecedented"、"groundbreaking" 等空泛形容词
  - 禁止 "we believe"、"we feel" 类主观语
  - 强制数据来源 + 法律合规披露

#### 5.6.4 Acceptance gate G3 (R2-M01 修订)

| 检查项 | 通过条件 |
|---|---|
| pdflatex 编译 | **6 new manuscript pdflatex pass** (3 new paper × en/zh, M3 实际产出) + **10 existing manuscript regression test pass** (compile state 在 M0.5 panel 升级后未被 break) |
| `tests/test_manuscript_compilation.py` | pass (新增, 覆盖 8 paper × en/zh = 16 manuscript) |
| BibTeX coverage | ≥ 30 unique entries / paper (含 §2.3 共用 anchor ≥ 15 + paper-specific 衍生 ≥ 15, 见 R2-m05) |
| IRON RULE | 0 violations per paper |
| Bilingual abstract | 完整 |

#### 5.6.5 Audit 轮次：4 轮 (R46-m01 列举)

| 轮 | 焦点 |
|---|---|
| A3.1 | pdflatex 编译完整性 (6 new + 10 existing regression) |
| A3.2 | bibtex coverage ≥ 30 / paper + APA-finance 格式 |
| A3.3 | IRON RULE 反 anti-pattern 0 violations (banned terms scan) |
| A3.4 | 风格 calibration: exemplar paper 引用一致性 |

### 5.7 M4 外生冲击 DiD 设计 (2026-10-19 → 2026-11-15, 4 weeks)

#### 5.7.1 目标 (R2-M02 修订)

6 外生冲击事件 (E1-E5b, 见 §5.7.2) × applicable papers (per §5.7.2 applicable_papers 列) = v2.55 **17** + v2.56 epoch 5 P5 (E1/E3/E4 applicable per [P5 paper_spec.yaml](../../papers/bank_fintech_collab/paper_spec.yaml)) **+3** = **20 DiD spec** 设计 + 平行趋势检验 + treatment 定义。

实际 spec 计数 (R2-M04 + R3-M07 修订后):
- E1: P1, P2, P3, P4, **P5** (5 papers; R2-M04: P3 加 E1; v2.56 epoch 5: P5 加 E1 per P5 paper_spec event_studies)
- E2: P1, P2, P3 (3)
- E3: P1, P3 (2)
- E4: P1, P2, P3, P4 (4)
- E5a: P2, P4 (2; R3-M07: P2 适用)
- E5b: P2, P4 (2; R3-M07)
- 合计 4+3+2+4+2+2 = **17 spec**

#### 5.7.2 外生冲击事件库（详见 Appendix C）

R1-M11 + R1-m02 修订: 事件按 identification strategy 标注, 拆分原 E5。

| 事件 ID | 日期 | 内容 | 适用 paper | Identification 策略 |
|---|---|---|---|---|
| E1 | 2013-06-13 | 余额宝上线（互联网金融元年）| **P1, P2, P3, P4** (R2-M04 加 P3) | post dummy × bank pre-2012 fintech-exposure (Hassan-style); P3 用于测试 substantive-symbolic gap 时间动态 (post-E1 累积 year, R4-m02 改 quarter → year, panel 是 bank-year) |
| E2 | 2016-08-24 | 网络借贷整顿（P2P 暂行办法）| P1, P2, P3 | bank-level continuous exposure (与 P2P 业务 pre-2016 媒体共现强度) |
| E3 | 2017-04-27 | 资管新规《指导意见》征求稿 | P1, P3 | **cross-sectional intensity DiD** (基于 pre-2017 银行理财业务占比 × post dummy; 不是 staggered DiD, 因为对所有银行同时生效) |
| E4 | 2020-11-03 | 蚂蚁集团 IPO 暂停 | P1, P2, P3, P4 | bank-level continuous exposure (与蚂蚁 / 网商银行 / 余额宝 pre-2020 关联强度) |
| E5a | 2022-09-01 | 数据出境安全评估办法 (实施) | **P2, P4** (R3-M07: P2 适用 — 跨境业务 attention intensity 有 cross-sectional 变异) | binary treated (跨境业务 dummy) |
| E5b | 2023-09-30 | 数据出境管理办法 (网信办 11 号公告) | **P2, P4** (R3-M07) | binary treated (跨境业务 dummy); 与 E5a 复合 treatment |

**G4 平行趋势检验适用性 (R8-M03 修订: 所有 6 events 都是 intensity-based DiD)**:

所有 E1-E5b 都是政策事件, 对所有银行同步生效, **无银行级 staggered timing variation**。treatment 是基于
pre-event exposure intensity (bank-level cross-sectional heterogeneity) × post-event dummy。

- 平行趋势检验统一为 **intensity slope ≈ 0** (pre-event 期间 intensity × event_time interaction 在 90% CI 不显著)
- 所有 events 通用此检验; G4 acceptance "≥ 80% pass" 指 6 events 中至少 5 个 events 的 intensity pre-trend 通过
- 不存在 standard staggered DiD with different treatment timings (因为政策事件对所有银行同步生效)

#### 5.7.3 DiD spec 模板 (R1-M06 + R1-M18 修订)

**SSC / GitHub prerequisites** (M2 起一次性 install):

```stata
* DiD estimators
ssc install csdid, replace          // Rios-Avila, Sant'Anna, Callaway
ssc install csdid_plot, replace     // 配套绘图命令
ssc install did_imputation, replace // Borusyak-Jaravel-Spiess robust DiD
ssc install eventstudyinteract, replace  // Sun-Abraham 2021 event study

* Inference
ssc install boottest, replace       // wild cluster bootstrap (Roodman et al.)
ssc install rwolf, replace          // Romano-Wolf stepdown (Clarke 2021)
ssc install ritest, replace         // randomization inference (Heß)

* Honest DiD (R6-m01: SSC 优先, GitHub fallback)
capture ssc install honestdid, replace
if _rc != 0 {  // 若 SSC 未收录, fallback github
    net install honestdid, ///
        from(https://raw.githubusercontent.com/mcaceresb/stata-honestdid/main/) replace
}
```

**Estimator 模板 (R8-M03 修订: main spec = intensity DiD; csdid 仅 sub-cohort scenarios)**:

```stata
// === MAIN SPEC: Cross-sectional intensity DiD (适用所有 E1-E5b) ===
// 政策事件同步生效 → treatment intensity 来自 bank-level pre-event exposure
gen exposure_x_post = pre_event_exposure_intensity * (year >= event_year)
reghdfe <outcome> exposure_x_post <controls>, absorb(bank_id year) cluster(bank_id)

// Event study with intensity × event_time interactions (Sun-Abraham 2021 风格)
eventstudyinteract <outcome> lead_3-lead_1 lag_0-lag_3, ///
    cohort(treat_year) control_cohort(never_treated) absorb(bank_id year) ///
    vce(cluster bank_id)

// === ROBUSTNESS: Callaway-Sant'Anna staggered DiD ===
// CAVEAT: csdid 适用于 staggered timing scenarios; B-route 实际事件多为 simultaneous
// treatment, intensity DiD 是 main spec; csdid 仅在 sub-cohort 场景使用
// (如 P2P 暂行办法对城商行 / 农商行可能 staggered 实施, 用作 robustness)
csdid <outcome> <controls>, ivar(bank_id) time(year) gvar(treat_year) ///
    method(dripw) wboot rseed(20260516)
estat all
csdid_plot, group(...) title("...")

// === ROBUSTNESS: Borusyak-Jaravel-Spiess imputation DiD ===
did_imputation <outcome> bank_id year treat_year, ///
    fe(bank_id year) controls(<controls>) autosample
```

#### 5.7.4 Acceptance gate G4

| 检查项 | 通过条件 |
|---|---|
| SSC 包齐全 (R1-M06) | csdid + csdid_plot + did_imputation + eventstudyinteract + boottest + rwolf + ritest + honestdid 全部 installed |
| **20 DiD spec** (v2.55 17 = 4+3+2+4+2+2; v2.56 epoch 5 P5 +3 = E1/E3/E4 applicable per P5 paper_spec; R2-M02 + R2-M04 + R3-M07 + F-211) | 全部本机 Stata 19.5 跑通 |
| 平行趋势 (R1-M11 + R8-M03 重写: 所有 events 统一 intensity slope 检验) | 所有 6 events 适用 intensity × event_time pre-trend slope ≈ 0 (90% CI 不显著); 6 events 中 ≥ 5 events pass 即满足 G4 |
| Cluster-robust SE | 全部 bank-level cluster |
| `config/exogenous_shocks.yaml` | 6 events (E1-E5b) 完整定义 + identification 策略 + 文献依据 |

#### 5.7.5 Audit 轮次：4 轮 (R46-m01 列举)

| 轮 | 焦点 |
|---|---|
| A4.1 | 20 DiD spec (v2.55 17 + v2.56 P5 +3) 全部 Stata 跑通 + SSC 包齐全 (§5.7.4 G4 一致) |
| A4.2 | 平行趋势 intensity slope ≈ 0 (6 events ≥ 5 pass) |
| A4.3 | Cluster-robust SE 全部 bank-level cluster |
| A4.4 | `config/exogenous_shocks.yaml` 6 events 完整 (id + date + name + treatment_logic + identification + applicable_papers + reference) |

### 5.8 M5 主回归 / 机制 / 异质性 (2026-11-16 → 2027-01-10, 8 weeks)

#### 5.8.1 目标

每 paper 产出 Table 2 (M1→M6 progressive) + Table 3 (机制) + Table 4 (异质性) 三大表 + Figure 2-4。

#### 5.8.2 每 paper 节奏（2 weeks each, 并行可压缩）

- Week 1: Table 2 主回归 (M1 base → M6 full FE + cluster + **IV per paper_spec.yaml** identification.iv (P1/P2/P4 有 IV); P3 无 IV (per §B.3 + §5.7.2 E3 identification, baseline 即 cross-sectional intensity DiD 替代 IV); R2-M13 + R54-m01 修订: P2 用 leave-one-out peer attention 或 Bartik fallback, P1 用 leave-one-out industry tone, P4 用 leave-one-out peer locus)
- Week 1: Table 3 机制（含中介效应 / KHB 分解）
- Week 2: Table 4 异质性 (4 银行类型 + fintech wave 分段 per §B.4 heterogeneity_wave: wave_1 / wave_2 / consolidation / wave_3 + SOE × non-SOE, R4-M02 修订)
- Week 2: Figure 2-4（event study / coefplot / time trend by group）

#### 5.8.3 Acceptance gate G5 (R2-M07 修订)

| 检查项 | 通过条件 |
|---|---|
| 每 paper 4 张表 + 3 图 | 完整 .tex / .png |
| 主回归系数符号 | 与 paper_spec.yaml 预设一致（或显式记录方向 puzzle）|
| Stata log | 每 paper 实际运行的 paper-specific templates (4-5 个, per §5.5.2) + shared templates 调用全部归档到 `output/<paper>/logs/`; 4 paper 累计 ≥ 40 log 文件 (per-paper 范围 8-13 含 IV first stage + 主回归 progressive + 机制 + 异质性) |
| Pre-registration deviation | 任何偏离 paper_spec.yaml 的设计必须文档化 (触发 D5 决策点) |

#### 5.8.4 Audit 轮次：每 paper ≥ 8 轮（per memory `prefers_rigorous_multi_round_audits`）

| 轮（每 paper）| 焦点 |
|---|---|
| A5.1 | 主回归识别策略 |
| A5.2 | FE 选择正确性 |
| A5.3 | Cluster level 正确性 |
| A5.4 | 控制变量内生性 |
| A5.5 | 机制章因果链完整 |
| A5.6 | 异质性切分非任意 |
| A5.7 | Pre-registration 一致 |
| A5.8 | 与现有 5 paper 互不重复 |

> v2.55: 4 paper × 8 轮 = 32 轮 audit. v2.56 epoch 5: 5 paper × 8 轮 = 40 轮 audit 总计，对标 benefit_society v2.12 (14 轮 / 59 finding) × 5 paper ≈ 70 轮规模 (epoch 5 含 P5)

### 5.9 M6 稳健性 + Devil's Advocate (2027-01-11 → 2027-02-21, 6 weeks)

#### 5.9.1 目标

每 paper 产出 Table A1-A5 (稳健性) + Table 5 (advanced robustness) + Devil's Advocate
模拟报告。

#### 5.9.2 稳健性矩阵 (R1-M12 修订: per-paper specific)

**通用维度** (4 paper 全适用):

| 维度 | 工具 |
|---|---|
| 系数稳定性 | Oster (2019) δ (target δ ≥ 0.5) |
| 多重假设 | rwolf (Romano-Wolf stepdown, Clarke 2021) |
| Honest DiD | Rambachan-Roth (2023) RES, smoothness M ∈ {0, 0.5, 1, 2}×∆̂ (R1-M02 修订引文) |
| Wild bootstrap | boottest (Roodman et al.) |
| Placebo (银行-年随机化) | ritest (Heß) |
| Spillover (SUTVA) | 邻接矩阵 placebo / 同业网络遗漏检验 |
| Sample cuts | excl. 国有 6 / excl. 农商行 / excl. 上市子样本 / excl. pre_period (2007-2012, R8-m02 同步 §B.4 wave 重定义) |

**Paper-specific alternative measure** (R1-M12: 不同 paper 度量替代源不同):

| Paper | Alternative treatment measure 维度 |
|---|---|
| P1 (tone) | text2vec / dictionary-only / BERT-only / single-family LLM (gpt54nano / gemini31111 / deepseekv4 单独) vs vote |
| P2 (attention) | attention_index_full vs ctx vs disp vs pct (4 个独立度量) |
| P3 (substance) | substantiveness_full vs ctx; substantive-symbolic gap; 单独 W&Z full-track vs ctx-track |
| P4 (locus) | locus_layer_full vs ctx; locus_scenario_full vs ctx; layer-scenario gap |

#### 5.9.3 Devil's Advocate

- 调用 academic-paper-reviewer skill 的 Devil's Advocate mode
- 模拟 EIC + 3 reviewer + Devil's Advocate 共 5 视角审稿
- 每 paper 产出 `output/devils_advocate_round_<n>.md`

**Fatal flaw 定义 (R2-M14 显式标准, G6 验收依据)**:

| Fatal 类型 | 触发条件 |
|---|---|
| **Identification fatal** | 主回归 treatment 显示明确 endogeneity (reverse causality 证据 / pre-trend slope ≠ 0 在 90% CI 外 / Hausman 拒绝外生性 p < 0.01) |
| **Data fatal** | Selection bias 不可救 (outcome 系统性 missing for treated 子样本 / measurement error 与 treatment 系统相关) |
| **Theory fatal** | 理论框架 boundary 不满足 (如 W&Z 1994 要求 "管理层向 stakeholder 沟通" — 见 [wz_framework_boundary_justification.md](../methodology/wz_framework_boundary_justification.md) 但本研究是 fintech 业务声明, 需边界 justification 通过) |
| **Replication fatal** | Replication 包不能复现 Table 2 主回归系数 (差异 > 1% 或 sign change) |

#### 5.9.4 Acceptance gate G6

| 检查项 | 通过条件 |
|---|---|
| 每 paper 5 张稳健性表 | 完整 |
| Oster δ | ≥ 0.5 (Oster 2019 threshold) |
| Wild bootstrap p | < 0.10 for main coef |
| Devil's Advocate fatal flaw | = 0 (unresolved) |
| Honest DiD (R1-M08 修订) | Rambachan-Roth (2023) robust CI 在 smoothness restriction M = 1× max\|∆̂_pre\| 下 95% CI 不跨 0; sensitivity 表展示 M ∈ {0, 0.5, 1, 2}× 各档 CI |

#### 5.9.5 Audit 轮次：每 paper ≥ 5 轮 (R2-m06 枚举)

| 轮 (每 paper) | 焦点 |
|---|---|
| A6.1 | 系数稳定性 (Oster δ) 解读 + 给定 max R² 的 δ 选择 justification |
| A6.2 | Multiple hypothesis (rwolf) 中 hypothesis family 选取规则 |
| A6.3 | Honest DiD smoothness M 选择 justification (M ∈ {0, 0.5, 1, 2}×∆̂ 哪档作为 main spec) |
| A6.4 | Placebo / SUTVA 邻接图 reasonableness (邻接矩阵定义 + spillover threshold) |
| A6.5 | Sample cuts heterogeneity 解读 + Devil's Advocate fatal flaw 收敛性 |

### 5.10 M7 内审 + 投稿包 (2027-02-22 → 2027-03-14, 3 weeks)

#### 5.10.1 目标

- 4 paper 互引校准（避免自我重复）
- bibliography 去重 + 统一 APA-finance 格式
- Pre-submission rigor check

#### 5.10.2 子任务

| ID | 任务 |
|---|---|
| M7.1 | 互引矩阵：4 paper × 4 = 16 cell，标注每对 paper 是否互引、如何区分 |
| M7.2 | bibliography 去重 (4 paper × ~30 ref/paper, 含 §2.3 共用 anchor ≥ 15 适用 + paper-specific 衍生 ≥ 15; 去重后总数 80-100 视 paper 主题广度, R2-m03) |
| M7.3 | 期刊格式适配（JCF / SMJ / RFS 各自模板）|
| M7.4 | 5-视角 pre-submission 模拟 (R5-M02 同步 §5.9.3 + G7): EIC + 3 reviewer + Devil's Advocate; 用 academic-paper-reviewer skill |
| M7.5 | Cover letter 起草（4 份）|
| M7.6 | Replication 包打包（4 份 .zip）|

#### 5.10.3 Acceptance gate G7 (R1-M19 + R1-M28 修订)

| 检查项 | 通过条件 |
|---|---|
| 互引矩阵 | 16 cell 完整填写 |
| Salami slicing 检查 (R1-M19 显式标准) | (1) differentiation_claim 在 spec.yaml 与 manuscript intro 中表述一致; (2) 每 paper 至少 1 unique outcome variable (不在其他 3 paper 中作为 outcome 使用); (3) 每 paper 至少 1 unique identification strategy / IV / event; (4) 4 paper Methods Section paragraph-level Jaccard similarity ≤ 0.3 |
| Pre-submission rigor check (R1-M28 修订) | 5 视角模拟统一: EIC + 3 reviewer + Devil's Advocate (与 §5.9.3 M6 一致), fatal flag 0 unresolved |
| Replication 包 | 4 paper × `verify-replication` pass |
| Cover letter | 强调 differentiation_claim |

#### 5.10.4 Audit 轮次：3 轮（per paper × 4 = 12 total; R46-m01 列举）

| 轮 (每 paper) | 焦点 |
|---|---|
| A7.1 | 互引矩阵 16 cell 填写完整 + Salami slicing 4 criteria pass |
| A7.2 | 5-视角 pre-submission (EIC + 3 reviewer + Devil's Advocate) fatal flag = 0 |
| A7.3 | Replication 包 `verify-replication` pass + cover letter 强调 differentiation_claim |

### 5.11 M8 投稿 + post-submission monitor (2027-03-15 onwards)

#### 5.11.1 投稿计划

| Paper | 主推 | 投稿 window | Backup cascade (R73-m01 完整化) |
|---|---|---|---|
| P1 tone | JFQA | 2027-03-15 | JCF → JBF (per §B.1 backup_outlet=[JCF, JBF]; 2027-09 first cascade / 2028-03+ if successive reject) |
| P2 attention | JCF | 2027-03-15 | JBF → JFI (per §B.2 backup_outlet=[JBF, JFI]; 2027-09 / 2028-03+) |
| P3 substance | SMJ | 2027-03-15 | AMJ → ASQ → JFE salvage (per §B.3 sequential_resubmission cascade; 2027-09+ for AMJ, 后续 cascade 按 §3.2 / §3.1 注 2) |
| P4 locus | RFS | 2027-03-15 | JFE (per §B.4 backup_outlet=JFE; 2027-09 if reject) |

**Backup 列含义说明 (R73-m01 + R1-m11 同步)**: 上表 Backup 列展示首次 decision reject 后的完整 cascade outlet sequence (与 §3.1 / §B specs backup_outlet / sequential_resubmission 一致)。注 §5.11.2 R1-m11 scope: B-route v2 plan 持续到**首次 decision** (accept / R&R / desk reject / reject); cascade 第二段及以后实际投稿 (2027-09+) 由 academic-paper skill 的 revision mode 独立处理, 超出本 plan scope, 上表 cascade timeline 仅作 forward visibility。

#### 5.11.2 Post-submission (R1-m11 scope boundary)

- **Scope**: 持续到首次 decision (accept / R&R / desk reject / reject); 之后 (revision cycle / resubmission) 由 academic-paper skill 的 revision mode 独立处理, **不在 B-route v2 scope**
- 平均首次 referee report 周期 18-24 月
- 每季度更新 `docs/papers/<paper>/submission_status.md` (持续到首次 decision)

---

## 6. Acceptance Gates Matrix (汇总)

| Gate | 时点 | 关键指标 | 失败后果 |
|---|---|---|---|
| G-1 | M-1 完 | N_eff × T_eff 区间 + raw 完整性 ≥ 95% (Yellow band [50%, 95%) → C1-c 软 fallback, R59-M01) + **时间覆盖完整性: 无 > 2 年系统性时间断层** (R60-m01 新增, per M-1.3 覆盖热力图) + 财务匹配率 ≥ 60% (Yellow band [40%, 60%) → C2-lite) + **Pipeline scale test 1% 样本完整跑通 21→46 stage** (R77-m01 同步 §5.1.4 row 4, 对应 C3 fail-consequence trigger) + 跨期 LLM valid_rate ≥ 80% + 法律合规 | raw < 50%: C1-a (hard); raw [50%, 95%): C1-c (软); **时间断层 > 2 年: C1-b**; 财务 < 40%: C2; scale test 失稳: C3; LLM 跨期失效: C4; **法律合规失败: 暂停 M0 直至 cleared** (R79-m01 同步 §5.1.4 row 6) |
| G0 | M0 完 | **9 份 spec.yaml** (v2.55: 3 new + 5 retrofit + v2.56 epoch 5: P5 = 9; R1-M10 修订) + paper_registry 9 paper + 0 列名冲突 + 5 existing paper build-replication 在 v3.3.0 panel pass + **LLM cost cap = $5,000 锁定** (v3.4.0 Q-B 2026-05-17, 4200→5000; R19-m01 per §8 R10 mitigation + §10.1) + git tag | M0.5 暂停 |
| G0.5 | M0.5 完 | panel v34 reproducibility (panel-hash identical with LLM cache HOT; cache COLD 差异 ≤ 0.1% rows) + 跨期 κ ≥ 0.7 (按 4 段分别) + 4 类银行 × 18 年覆盖热力图无空洞 + LLM cost ≤ $5,000 (v3.4.0 Q-B, R46-M03 同步 §10.1 budget cap) + v3.3.0 兼容 (R46-M04 完整化): subset to **target_bank ∈ v3.3.0 84 银行 AND year ∈ {2017, 2018}** 与 v3.3.0 panel float 差异 ≤ 1e-9, categoricals exact | M1 暂停 |
| G1 | M1 完 | **8 new manuscript skeleton** (v2.55 3 new × en/zh + v2.56 epoch 5 P5 × en/zh = 8, M1 实际产出) + **10 existing manuscript regression test pass** (compile state 未被 panel 升级或 M1 改动 break; v2.55 总 16 visible, v2.56 总 18 visible) + 9 paper analysis CLI 跑通 + **pytest tests/test_papers_b_route.py pass** (R53-M01 同步 §5.4.4) | M2 暂停 |
| G2 | M2 完 | **84 Stata templates 实际总数** (v2.55 77 + v2.56 epoch 5 P5 7 = 84; RR6-1 加 6 orchestrator) + SSC 包齐全 + 22 + 7 = 29 个新模板 Stata 19.5 跑通 + 5 paper replication 包齐 (v2.56 含 P5) + **Macro/var 截断: 无 `set maxvar` 触顶 (panel 列数 ≤ 5000 < MP 上限 120,000)** (R49-m02) + **pytest tests/test_stata_templates.py pass** (R53-M02 同步 §5.5.4) | M3 暂停 |
| G3 | M3 完 | **8 new manuscript pdflatex pass** (v2.55 3 new × en/zh + v2.56 epoch 5 P5 × en/zh, M3 实际产出) + **10 existing manuscript regression test pass** (R46-M06 同步 §5.6.4) + `tests/test_manuscript_compilation.py` pass + bibtex ≥30/paper + IRON RULE 0 violations + Bilingual abstract 完整 | M4 暂停 |
| G4 | M4 完 | **20 DiD spec** pass (v2.55: 17 = 4+3+2+4+2+2; v2.56 epoch 5: +3 P5 applicable E1/E3/E4 = 20; R3-M01/M07) + 平行趋势检验统一为 intensity slope ≈ 0 (R8-M03: 6 events intensity-based); 6 events 中 ≥ 5 通过 + **SSC 包齐全** (csdid/csdid_plot/did_imputation/eventstudyinteract/boottest/rwolf/ritest/honestdid) + **Cluster-robust SE 全部 bank-level cluster** + **`config/exogenous_shocks.yaml` 6 events 完整定义 + identification 策略 + 文献依据** (R53-M03 同步 §5.7.4) | M5 暂停 |
| G5 | M5 完 | 5 paper × 主+机制+异质 + 8 轮 audit/paper (v2.56 epoch 5 含 P5) + **每 paper 4 张表 (Table 2 主回归 + Table 3 机制 + Table 4 异质 + Table 5 advanced)** + **3 图 (event study + coefplot + time trend) 完整 .tex / .png** + **主回归系数符号与 paper_spec.yaml 预设一致** (或方向 puzzle 文档化) + **Stata log 累计 ≥ 50 文件归档 `output/<paper>/logs/`** (v2.55 40 + P5 10) + **Pre-registration deviation 文档化** (触发 D5; **v3.4.0 β supplementation 已记录 prompt-v7→v8 additive** per wz_framework §4) | M6 暂停 |
| G6 | M6 完 | 5 稳健性表/paper + Oster δ ≥ 0.5 + **Wild bootstrap p < 0.10 for main coef (boottest)** (R53-M05 同步 §5.9.4) + Devil's Advocate fatal flaw = 0 (unresolved) + Honest DiD: 主 spec M = 1× max\|∆̂_pre\| robust CI 不跨 0; sensitivity 表展示 M ∈ {0, 0.5, 1, 2}× 全部 4 档 (R5-m06) | M7 暂停 |
| G7 | M7 完 | 互引矩阵 16 cell + **Salami slicing 4 条 criteria pass** (per §5.10.3 R1-M19: (1) differentiation_claim 一致; (2) 每 paper ≥ 1 unique outcome; (3) 每 paper ≥ 1 unique identification; (4) Methods Jaccard ≤ 0.3) + 5-视角 pre-submission (EIC+3 reviewer+Devil's Advocate) fatal = 0 + replication 包 + cover letter (R49-m03 同步 §5.10.3) | M8 暂停 |
| G8 | M8 投稿 | 5 paper submitted (v2.56 epoch 5 含 P5; submission window 2027-03-15 → 2027-04-09 per R6-13 timeline shift) | – |

---

## 7. Audit Matrix (R1-M24 修订: M-1 从 5 → 8)

| Milestone | Audit 轮数 | 总 finding 估计 | 累计审计轮数 |
|---|---:|---:|---:|
| M-1 | 8 | ~22 | 8 |
| M0 | 3 | ~8 | 11 |
| M0.5 | 6 | ~20 | 17 |
| M1 | 5 | ~12 | 22 |
| M2 | 4 | ~10 | 26 |
| M3 | 4 | ~10 | 30 |
| M4 | 4 | ~12 | 34 |
| M5 | 4 paper × 8 = 32 | ~80 | 66 |
| M6 | 4 paper × 5 = 20 | ~40 | 86 |
| M7 | 3 paper × 4 = 12 | ~20 | 98 |
| **Total** | **98 轮** | **~234 findings** | – |

注: 此处的 audit 是 milestone 实施阶段的 audit (M-1 数据/M0 设计/M5 实证 …), 与本 plan
文档的 multi-round audit (B_route_master_plan_v2_audit_log.md) 是两个独立 audit campaign。

对照 plan v14 (62 轮 / 68 finding) 与 benefit_society v2.12 (14 轮 / 59 finding)，
B 路线 4 paper 总 audit 规模 ≈ 1.5× plan v14。

---

## 8. Risk Register

| ID | 风险 | 严重度 | 概率 | 缓解 | 应急 |
|---|---|---|---|---|---|
| R1 | 40 万 raw → 有效 panel 转化率未知 | 致命 | 中 | M-1 scale test | C1 |
| R2 | 银行覆盖不均匀，有效 N 远低于 500 | 高 | 高 | M-1 Pareto 曲线 + 上市银行子样本 fallback | C2 |
| R3 | 财务变量匹配率 < 60% | 高 | 中 | M-1 CSMAR/Wind 交叉 | C2 |
| R4 | "Fintech" 概念跨期演化 (2007-2012 vs 2013+) | 高 | 高 | M0.5.10 跨期 prompt 稳健性测试 + κ ≥ 0.7 gate | C4 |
| R5 | LLM 度量跨 18 年时序稳定性 | 中-高 | 中 | 三家族投票 + temperature=0 + 段内 κ 检验 | C4 |
| R6 | 银行存活 / 合并造成 unbalanced panel | 中 | 高 | 保留 balanced + unbalanced 双版 panel | – |
| R7 | 媒体源结构变化 (传统 → 门户 → 自媒体) detrend 困难 | 中 | 高 | 媒体来源虚拟变量 + 按报道密度归一化 (Implementation R12-m02: M-1.1 raw 盘点识别 media_source 字段 `pubcode` from CNRDS/Wind/巨灵 metadata; M0.5.X 生成 media_source × bank 共现 panel; 归一化公式 `log(1 + raw_count) - log(1 + yearly_total_media_count_by_source)`) | – |
| R8 | 4 paper 内容雷同 / salami slicing | 高 | 中 | M0 differentiation_claim 强制 + M7 互引校准 | – |
| R9 | Stata 模板膨胀到 70+ 维护失控 | 中 | 中 | M2 反 DRY audit + 严守 shared/override 划分 | – |
| R10 | LLM cost 超 budget | 中 | 中 | M-1.5 dry-run 估算 → M0 G0 时 LLM cost 上限 lock | 砍 BERT 变体 |
| R11 | M0.5 12 周关键路径延期 | 高 | 中 | M1/M3 部分并行（写骨架不依赖最终 panel）+ Trigger: M0.5 wall-time > 14 wk (12 wk + 2 wk 缓冲) → 触发 next v2.x revision (e.g., v2.3 重排, R3-M04); > 18 wk → 触发 v3 plan 重写 (含 scope 缩减) | 重排 M4-M8 |
| R12 | 法律合规：raw 数据来源 ToS 风险 | 致命 | 中 | M-1.7 合规清单 + 优先用 CNRDS/Wind 商业授权 | 替换数据源 |

---

## 9. Decision Points

| ID | 决策点 | 时点 | 触发条件 | 由谁决定 |
|---|---|---|---|---|
| **D1** | 数据来源最终确认 | M-1 起 | 立即 | 用户 |
| **D2** | G-1 失败后选择哪个 C 应急 | M-1 完 | G-1 fail | 用户 + Claude |
| **D3** | 投稿 outlet 是否调整（如 P4 从 RFS 降为 JFE）| M6 完 | M6 audit 发现致命缺陷 | 用户 |
| **D4** (R46-M07 修订) | 修订投稿 strategy: P3 cascade SMJ → AMJ → ASQ 任一阶段后 JFE salvage 时点 / 资源分配 (NB: 不是"双投"; cascade 顺序投稿 + salvage rewrite 是 sequential not simultaneous, 见 §3.2 注 2) | M7 完 | 资源允许 / cascade 进度需调整 | 用户 |
| **D5** | M5/M6 偏离 paper_spec.yaml 多大幅度需触发 v3 plan | M5/M6 进行中 | 任意 | 用户 |
| **D6** (R5-m01 重表述) | 数据来源是否含未发表 working paper / 内部数据 / 第三方授权数据 (影响投稿期刊 replication policy 接受度: RFS / JFE 要求公开 replication; SMJ 较宽容) | M-1 期 | 数据来源含 working paper / 内部数据 / 受限授权 | 用户 + IRB / 期刊 policy 对照 |

---

## 10. Resource Budget

### 10.1 直接成本

| 项 | 估计 | 备注 |
|---|---|---|
| LLM API M0.5.4 (21_tone_llms 全量) | $2,400 | 400K × 3 family × $0.002/call |
| LLM API M0.5.8 (32a / 33-39 验证 + audit, R2-M17 补) | $300 | validation 子样本 ~10% × 3 family + audit 抽样, cache hit 较高 |
| LLM API M-1.5 (pipeline scale test 1% sample, per §5.1.2 canonical) | $50 | R73-M01 修订: 此 LLM cost 来自 M-1.5 Pipeline scale test (抽 1% raw 全程跑 pipeline 含 21_tone_llms LLM API), 不是 M-1.4 (后者是 lexicon clustering 无 LLM cost) |
| LLM API M5/M6 (ad hoc 稳健性变体) | $500 | – |
| 缓冲 25% | $812 | 25% × ($2,400 + $300 + $50 + $500) |
| **小计 LLM cost (v2.55)** | **~$4,062** | budget cap $4,200 (历史 v2.55 数字) |
| **小计 LLM cost (v2.56 epoch 5)** | **~$4,480** | budget cap **$5,000** (v3.4.0 Q-B 上调; collab_mode 第三维度 +$418 ≈ +10% 总成本) |
| Stata MP 19.5 license | $0 | 本机 lab perpetual 64-core 已覆盖 4 paper × 16 templates × 5 events × all robustness (R2-m02) |
| GPU (M0.5.6 BERT 全量推理) | $0 | 本机 |
| 数据库订阅 (CSMAR / Wind) | $0 | 已有 |
| 投稿 submission fees (M8, **由用户承担, 非 Claude budget**, R2-m07) | ~$1,000 | 4 paper × ~$250 (RFS $250 / SMJ $300 / JFE $300 / JCF $100 / JFQA $150) |
| **总 Claude operation 成本** | **~$4,062** | (不含 $1,000 submission fees, 由用户在 M8 阶段承担) |

### 10.2 时间成本（wall-time）

**Wall-time** = 真实日历周, 含 LLM API 等待 / GPU 推理 / 工具运行 idle (R1-m03 澄清)。

| 阶段 | wall-time | working days |
|---|---|---|
| M-1 → M0 | 2.5 wk | 15 |
| M0.5 | 12 wk | 60 (含并行)|
| M1 → M3 | 5 wk | 26 |
| M4 → M6 | 18 wk | 90 |
| M7 | 3 wk | 15 |
| **总** | **~40.5 wk** | **~206 working days** |

### 10.3 人时（Claude 协作时长，rough; R1-M25 + R1-m13 修订）

**Claude time** = Claude 主动操作时间 (audit + edit + reason), 不含 idle wait。

"1 audit round/day" 是 best-case 估计; 实际包含 plan-doc 修改 + cross-reference 检查 +
report 起草开销 + cross-paper context switch (在 M5/M6 显著)。range ≈ ±25% (R33-m01 修订:
各 milestone 实际 ±15-33% asymmetric, upper bound 倾向更宽以反映 cross-paper context-switch
overhead 在 M5/M6/M7 显著)。

| 阶段 | audit 轮数 | best-case Claude days | range (±25%) |
|---|---:|---:|---|
| M-1 (R1-M24 上调) | 8 | 8 | 6 - 10 |
| M0 | 3 | 3 | 2 - 4 |
| M0.5 (跨 12 wk wall-time, audit 占用) | 6 | 6 | 5 - 8 |
| M1-M3 | 13 | 13 | 10 - 17 |
| M4 | 4 | 4 | 3 - 5 |
| M5 (4 paper cross-switch overhead 显著) | 32 | 32 | 24 - 40 (±25%; or 28-42 if cross-paper context-switch overhead 在 upper bound 显著, R10-m05) |
| M6 (跨 paper) | 20 | 20 | 16 - 26 |
| M7 (跨 paper internal review) | 12 | 12 | 10 - 16 |
| **总 Claude time** | **98** | **98 d** | **76 - 126 d** (R69-m01: 各 milestone individual range 之和, low 6+2+5+10+3+24+16+10=76, high 10+4+8+17+5+40+26+16=126) |

---

## 11. Contingency Plans

### 11.1 C1 — Raw 数据不足 (G-1 fail on raw 完整性) (R2-M19 拆 sub-cases)

**触发条件 sub-cases**:

**C1-a (raw 完全不足; R5-m05 优先级注: C1-a 优先于 C1-b)**: M-1.1 发现 raw < 200K 条 或 < 300 银行 (覆盖严重不足); raw 同时不足且时间断层 > 2 年时, 仍触发 C1-a (raw 完全不足是更严重的 fail mode)
**应急 (R3-m05 + R9-m01 + R45-m02 修订)**:
- 限制到 v3.3.0 baseline (168 obs, T=2) **或** raw 实际可用子集 (取 N_eff × T_eff 较大者; 但 W&Z 长期反转故事仍要求 T ≥ 5, 否则 P3 退化为 cross-sectional)
- **C1-a 输出 = 2 paper** (R45-m02 措辞校正):
  - **P1 (tone) 主战 paper** (full spec, 在 168 obs 上跑全部 outcome / treatment / identification)
  - **P3 (substance) 退化稿** (cross-sectional only; T=2 不支持 long-run reversal):
    - 保留 outcome.short_run = car_3day_window_fintech_announcement (single event 2018 可算)
    - **删除** outcome.primary long_run_roa_change_3yr (T=2 不够 t+3 forward change)
    - 退化为 "象征性 vs 实质性 short-run market reaction cross-sectional comparison (single t=2018)"
    - 顶刊预期 SMJ → JMS / SMJ Special Issue
- 放弃 P2 / P4 (T=2 下 attention 时序变异 / locus 三波浪潮 不成立)
- 顶刊预期回到 v1 估计: P1 → JBF; P3 (退化稿) → JMS / SMJ Special Issue
- 总周期压缩到 5-6 月

**C1-c (R59-M01 新增: raw 完整性 yellow band [50%, 95%) = [200K, 380K] 可访问, 其他 OK)**:
- raw 200K-380K accessible 但 ≥ 300 银行 (覆盖宽度足够, 仅深度减少); 时间无大断层
**应急 (软 fallback)**:
- 用 raw 实际可用子集 ~200-380K, 4 paper 保留 (P1+P2+P3+P4)
- N_eff × T_eff ≈ 2000-5000 obs (R61-m01 精确化: baseline 3000-9000 缩减约 40-70%; raw 200-380K subset 的实际 N_eff 取决于覆盖热力图)
- 顶刊预期降 0.5 档: P4 RFS-realistic → JFE-realistic; P3 SMJ-realistic → SMJ + AMJ; P1 JFQA → JCF; P2 JCF → JBF
- 与 C2-lite 类似的 "soft fallback" 风格, 区别在于 C1-c 是 raw 不足, C2-lite 是财务匹配不足

**C1-b (时间断层 > 2 年, 但其他 OK)**: raw 200K-400K, 银行覆盖 ≥ 300, 但某段时间 (如 2007-2010 或 2012-2014) 系统性缺失 > 2 年

**应急 (R10-m01 sub-classification)**:

| Sub-case | 断层位置 | P3 long_run_roa 影响 | 整体应对 |
|---|---|---|---|
| C1-b1 | panel 早期 (2007-2010) | 可算 from t ∈ {2011+, ...}; outcome 保留 | 用 available T 段 (2011-2024 = 14 年), N_eff × T_eff ≈ 3000-6000; 4 paper 保留 |
| C1-b2 | panel 中期 (2015-2019) | 部分行 NaN (t 在断层 → t+3 不可算); sample 缩水 | 顶刊预期降一档: P4 RFS → JFE; P3 SMJ → SMJ + AMJ; P1 JFQA → JCF; P2 JCF → JBF |
| C1-b3 | panel 后期 (2022-2024) | t=2021 之前可算 (t+3 ≤ 2024); 接近完整 | 4 paper 保留, 顶刊预期降 0.5 档 |

- §11.4 C4 与 C1-b 高度重叠 (LLM 跨期失效也会导致放弃早段); C1-b 是 raw 早段缺失, C4 是 raw 在但 LLM 度量不可靠

### 11.2 C2 — 财务变量匹配率 < 40% (R1-m04 措辞修订)

**触发条件**：M-1.2 / M-1.6 显示 < 200 家银行有完整 2007-2024 ROA + 资本充足率。

**应急**：
- 缩减 sample 到 ~40-60 家上市银行 (R6-m03: A 股上市 ≈ 42 家 + 港股 H 股 ≈ 15 家 + 美股 ADR ≈ 1 家; 取 ≈ 50 家 × 18 yr ≈ 900 obs)
- 各 paper 保留 spec.yaml 原 outcome (含 stock return / patent / capex), 仅缩窗到上市子样本
- 顶刊预期：P4 仍可冲 RFS，但 referee 会挑样本代表性 → 需 robustness 解释上市 vs 非上市 banking sector 异质性
- **C2-lite** (匹配率 ∈ [40%, 60%) yellow band): 不缩到 60 家, 保留 200-300 家有部分财务数据的银行, 用 multiple imputation (R4-m03 方法: MICE / multivariate imputation by chained equations, m=20 imputations, 用 Stata `mi impute chained` 或 R `mice` 包) 填补缺失年; robustness 用 listwise deletion 子样本; 顶刊预期降一档

### 11.3 C3 — Pipeline scale test 失稳

**触发条件**：M-1.5 抽 1% 样本 pipeline 跑挂或转化率 < 0.5%。

**应急 (R2-M18 重命名)**：
- 暂停 M0.5 全量重跑
- 触发 **M-1.bis Pipeline Robustness Sprint** (4-6 周), 放在 M-1 fail 后 M0 启动前
- 修复后 G-1 重做 → 回到主流程

### 11.4 C4 — LLM 跨期失效

**触发条件**：M-1 抽 100 样本或 M0.5.10 测试 2007-2010 段 valid_rate < 80% 或 κ < 0.5。

**应急 (R1-m10 + R3-M08 + R4-M03 修订)**：
- 放弃 2007-2012 段 = 失去 pre-fintech baseline (2007-2012 中文媒体几乎无 "金融科技" 一词, 以 "网上银行/电子银行" 为主)
- 仅做 2013-2024 (12 年) → N×T ≈ 6,000 obs（仍够 top 5 下沿）
- **P4 三波 fintech 浪潮叙事保持完整** (R4-M03 重定义对称三波 + consolidation): wave_1 (2013-2015) + wave_2 (2016-2018) + consolidation (2019-2021) + wave_3 (2022-2024), 全部在 2013-2024 段内
- 顶刊预期：P4 维持 RFS / JFE 现实 (失去 pre-period baseline 仅影响 robustness 而非 main identification)
- 注: 此 C4 与 §11.1 C1 不同; C1 是 raw 整体不足, C4 是早期段质量问题

---

## 12. Legal / Compliance Checklist

| 项 | 状态 | M-1.7 处理 |
|---|---|---|
| Raw 媒体语料来源 | 待 D1 确认 | 列出 5 个候选来源 + ToS 摘录 |
| 商业授权链 | 待 M-1.7 | CNRDS / Wind / 巨灵财经 license 副本 |
| 数据脱敏 (PII) | 银行新闻无个人 PII | 仅需检查记者署名是否需要脱敏 |
| 出境数据合规 | 仅中文 + 中国境内媒体 | 默认无需 |
| Replication 包数据披露 | 学术 fair use + 元数据 + 派生统计 | 不分发 raw 全文 |
| IRB (如有 manual annotation) | 已在 [calibration_plan_v5.1](../methodology/calibration_plan_v5.1.md) 覆盖 | – |
| 投稿期刊数据政策 | RFS / JFE / JCF / SMJ 各自要求 replication 包 | M7 阶段适配 |

---

## 13. Document Maintenance

- **版本递进**：每次重大修改 v2.0 → v2.1 → v2.2 ...；breaking 变更触发 v3.0
- **修订记录**：见 Appendix E
- **关联更新**：
  - 每完成一个 milestone，更新 [`docs/INDEX.md`](../INDEX.md)
  - 每完成一个 G-gate，更新本文档 §6 Acceptance Gates Matrix
  - 任何 spec.yaml 变更触发 paper_registry 测试
- **Plan / spec semver 关系 (R1-m07 + R6-m02)**: 每个 `paper_spec.yaml` 含 `spec_version: <major>.<minor>.<patch>` 字段; spec_version 主版本号 ≤ plan major (例: plan v2.x → spec ≤ 2.x; plan v3.0 breaking 触发所有 spec major bump)
- **freeze 时点**：M0 完成时 git tag `B-route-v2-frozen`
- **plan-doc 与 commit 关系**：每次 commit 在 message footer 引用本 plan 的 milestone 编号 (M-1.3 / G-1 / R4 etc.)

---

## 14. RACI Matrix (R1-M14 新增)

| Milestone | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| M-1 数据现状审计 | **Claude (audit ops) + 用户 (prerequisite delivery per §5.1.1.bis)** (R3-m03) | Claude | 用户 (D1 数据来源决策 + D6 数据来源类型决策 per §9 R5-m01: 含 working paper / 内部数据 / 第三方授权 影响投稿 replication policy; R73-m02 补 D6; + D2 G-1 失败后 C-fallback 选择 per §9: conditional trigger 仅 G-1 fail 时, 用户 + Claude 共同决策; R80-m01 补 D2) | 用户 (G-1 报告) |
| M0 设计契约 | Claude | Claude | 用户 (4 paper 边界确认) | 用户 (G0 报告) |
| M0.5 Pipeline 重跑 | Claude (LLM 调用 + 监控) | Claude | – | 用户 (LLM cost / wall-time 周报) |
| M1 目录骨架 | Claude | Claude | – | 用户 (G1 报告) |
| M2 Stata 模板 | Claude | Claude | – | 用户 (G2 报告) |
| M3 Manuscript 骨架 | Claude (academic-paper skill) | Claude | – | 用户 (G3 报告) |
| M4 DiD 设计 | Claude | Claude | 用户 (E1-E5b identification 策略确认) | 用户 (G4 报告) |
| M5 主回归 | Claude (per-paper × 4) | Claude | 用户 (D5 偏离 spec 触发) | 用户 (G5 报告) |
| M6 稳健性 + DA | Claude (per-paper × 4) | Claude | 用户 (D3 outlet 调整) | 用户 (G6 报告) |
| M7 内审 + 投稿包 | Claude | Claude | 用户 (D4 投稿策略调整) | 用户 (G7 报告) |
| M8 投稿 | **用户** (实际提交是用户操作) | 用户 + Claude | Claude (cover letter / replication 包) | – |
| Post-submission | 用户 (与期刊对接) | 用户 | Claude (revision mode 协助) | – |
| Decision points D1-D6 | 用户 | 用户 | Claude (option analysis) | – |
| Risk register R1-R12 monitor | Claude | Claude | 用户 (R12 法律合规 / R10 budget) | 用户 (R 触发时) |

注: M0-M7 默认 Claude 自主操作 (per 用户 "无人工参与" 指令); M8 投稿 + post-submission
是与外部期刊的 IO, 必须由用户操作。Decision points 仍是用户保留权。

---

## Appendix A: v1 → v2 完整 Diff

| 项 | v1 conversation draft | v2 修正 |
|---|---|---|
| 起点假设 | N×T = 168 (v3.3.0 ingested baseline) | N_raw = 400K, N×T_target = 9000 (待 M-1 验证) |
| 顶刊预期 | 4 paper 几乎都难进 top 5 | P4 RFS / JFE 现实, P3 SMJ / AMJ + JFE 现实, P1/P2 JCF / JFQA 现实 |
| Track B 路径 | B1/B2/B3 三选二（含跨国扩展）| 仅 B3 + pipeline 重跑（B1 数据已有，B2 不必要）|
| 数据扩展周期 | 5 个月（含数据采购）| 12 周 Pipeline 重跑（数据在手）|
| 起始 milestone | M0 设计契约 | **M-1 数据现状审计**（v2 新增）|
| 关键路径瓶颈 | 数据获取 | Pipeline 健壮性 + 财务数据匹配率 |
| 总周期 | 13-19 月 | **9.5 月**（M-1 起 → M8 投稿; R2-M09 与 §10.2 40.5 wk 对账）|
| 直接成本 | $5-15K (数据采购) | **~$4.062K** (LLM API + 25% buffer; 不含 ~$1K submission fees 由用户在 M8 阶段承担; R3-M09 同步 §10.1) |
| 风险等级 | R1-R7 | **R1-R12**（v2 新增 R8-R12）|
| 应急方案 | 无明确 fallback | **C1-C4** |
| 决策点 | 2 个 | **6 个** |
| 总 audit 轮数 | 模糊（"≥3 轮 / milestone"）| **98 轮 / ~234 findings** 精确预测 (R46-M09 同步 §7 Audit Matrix R1-M24 修订后 M-1 5→8) |

---

## Appendix B: 4-Paper Spec Drafts

### B.1 P1 — `bank_fintech_tone`

```yaml
paper_id: bank_fintech_tone
spec_version: 2.0.0  # R1-m07: 与 plan v2.x 一致
status: existing  # v3.2.0 已存在, M0 retrofit spec
differentiation_claim: |
  P1 度量媒体对银行的语调情感方向 (积极 / 消极, 连续情感得分 llm_vote_tone_full)。
  R20-m01 跨 paper 区分 (B-route 3 + existing 4 paper, 共 7 对照):
  - 与 P2 (attention): P1 度量情感方向 (sign + magnitude); P2 度量曝光强度 (cumulative attention without sign); 二者独立 channel
  - 与 P3 (substance): P1 度量连续 tone 情感; P3 度量银行 fintech 公告的 W&Z 二元 substantive vs symbolic; outcome 事件窗口也不同 — P1 用 car_3day_window_tone_shock (tone shock 触发), P3 用 car_3day_window_fintech_announcement (fintech 公告触发)
  - 与 P4 (locus): P1 度量连续 tone; P4 区分公告的 locus 二元属性 (底层/应用); 完全不同 dimension
  - 与现有 llm_peer: P1 不构造同业网络 IV, 仅用 firm-level tone; llm_peer 用 LLM-determined semantic peer 网络
  - 与现有 brokerage_network: P1 不用网络中心性, 仅 firm-level; brokerage 用 betweenness/constraint/eigenvector
  - 与现有 benefit_society: P1 用 LLM-vote tone (情感方向); benefit_society 用 LLM-Embedding 双极锚点投影 (态度强度, 不是情感)
  - 与现有 strategic_diff: P1 度量 firm 自身 tone; strategic_diff 度量 firm 在 N-邻群中的差异度 (distinctness, not tone)
outcome:
  primary: car_3day_window_tone_shock  # R10-M01: 重命名差异化 (tone shock 事件窗口, 与 P3 fintech announcement 窗口区分)
  secondary: [loan_growth, ln_market_cap, roa]  # R1-M13: roa 仅作 outcome.secondary, 不在 controls 中复用
  enrichment_source: M0.5.11 (CSMAR/Wind daily returns + 年报 ROA + Wind 季报 ln_market_cap; derived event-window CAR construction per §5.3.2 M0.5.11, R12-m01)  # R8-M04
treatment:
  primary: llm_vote_tone_full  # 现有列
  alternative: [gpt54nano_tone_full, gemini31111_tone_full, deepseekv4_tone_full]
controls:
  bank_level: [ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth]  # R1-M13: 不含 roa
  year_level: [gdp_growth, m2_growth]
  fixed_effects: [bank_fe, year_fe]  # R51-M01: schema required, R1-M13 时遗漏, R51 补; 与 §B.2/B.3/B.4 一致
identification:
  baseline: long_panel_within_bank_within_year
  iv:  # R14-M01: 改为 dict 形式 与 schema + §B.2/B.4 一致
    primary: leave_one_out_industry_tone  # Cao et al. 2025 RAS 风格但 firm-level
event_studies:  # R2-M11 + R45-m03 修订: 引用 Appendix C events by id (与 yaml 文件 `id` 字段一致)
  - E1  # 2013-06-13 yuebao_launch
  - E2  # 2016-08-24 p2p_regulation
  - E3  # 2017-04-27 asset_management_rules
  - E4  # 2020-11-03 ant_ipo_pause
targets:
  primary_outlet: JFQA
  ambitious_outlet: [RFS, JFE]  # R75-m01: 2-tier ambitious list 与 §3.2 P1 v2 ambitious "RFS / JFE" 一致; schema R75-m01 允许 list 形式
  backup_outlet: [JCF, JBF]  # R48-M01 + R50-M01: list 形式与 §3.1 P1 backup 列 "JCF / JBF" 完整对齐
  submission_window: 2027-03-15  # R47-M03 增 (per §5.11.1 投稿计划)
sample:  # R14-M02 增 sample section per schema
  n_bank_min: 200  # M-1 G-1 确认后 update
  t_year: 18
  obs_target_min: 3000
audit_rounds_target_min: 8
```

### B.2 P2 — `bank_fintech_attention` (新建)

```yaml
paper_id: bank_fintech_attention
spec_version: 2.0.0
status: new
differentiation_claim: |
  P2 度量银行被 fintech 媒体话题"曝光"的强度，独立于情感方向。
  方法对标 Hassan et al. 2019 QJE 的 firm-level political risk exposure。
  R17-m01 + R21-m01 跨 paper 区分 (B-route 3 + existing 4 paper, 共 7 对照):
  - 与 P1 (tone): P2 度量曝光强度 (cumulative attention without sign); P1 度量情感方向 (sign + magnitude); 二者独立 channel
  - 与 P3 (substance): P2 度量媒体对银行的曝光强度 (cumulative attention from media); P3 度量银行 fintech 公告的 W&Z 实质性 vs 象征性
  - 与 P4 (locus): P2 度量曝光强度 (1D scalar); P4 区分底层 vs 应用场景 (2D treatment pair)
  - 与现有 llm_peer: P2 不构造 LLM-determined peer 网络 IV; llm_peer 用 leave-one-out semantic peer; 二者 IV 机制不同 (P2 fallback Bartik shift-share; llm_peer 语义同业)
  - 与现有 brokerage_network: P2 不构造网络中心性, 仅用 firm-level attention; brokerage 用 betweenness/constraint/eigenvector + 二阶语调 IV
  - 与现有 benefit_society: P2 度量曝光强度 (count); benefit_society 度量态度 (LLM-Embedding 投影强度), 性质不同
  - 与现有 strategic_diff: P2 度量 firm 自身 attention 量; strategic_diff 度量 firm 在 N-邻群中的战略差异度 (distinctness)
outcome:
  primary: ln_fintech_investment  # 银行年报 fintech 投入披露
  secondary: [m_and_a_fintech, patent_fintech_count, employee_growth_it]
  enrichment_source: M0.5.11 (CSMAR 年报 ln_fintech_investment / Tonghuashun M&A / IncoPat patent / CSMAR employee)  # R8-M04
mediator:  # R8-M01 + R47-M01 + R63-M01: mediator 紧跟 outcome (与 §B.4 + schema 顺序一致)
  primary: ln_fintech_mdna_length
  source: 银行年报 MD&A 章节文本长度 (enrichment M0.5.11; observable proxy 对应 §5.5.2 P2 16_mechanism)
treatment:
  primary: attention_index_full
  secondary: [attention_index_ctx, attention_disp_full, attention_pct_full]
  source: stage 14_fintech_intensity 衍生 (R36-m01 + R47-M01: 4 attention 度量 index_full/index_ctx/disp/pct; M0 G0 时按 14_fintech_intensity.parquet schema 对齐 actual column names)
controls:  # R9-M01 + R47-M01: 之前 fix 仅 §B.3/B.4, 未到 §B.2, R47 正确补加
  bank_level: [ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth]
  year_level: [gdp_growth, m2_growth]
  fixed_effects: [bank_fe, year_fe]
identification:
  baseline: cross_sectional_intensity_did  # RR15-1 (Review-only audit): R8-M03 同步 — all 6 events intensity-based (政策同步生效, treatment = pre-event exposure × post). 历史 label `staggered_did_callaway_santanna` 在 §5.7.3 csdid 仅 robustness sub-cohort 使用
  iv:
    primary: leave_one_out_peer_attention_iv  # firm-level 兼容
    fallback: bartik_attention_iv             # 需要 pre-2007 bank fintech-lending share
    # R5-m03 与 llm_peer paper 区别: P2 leave-one-out peer = 银行类型 (国有 / 股份制 / 城商 / 农商)
    # 子样本内同类银行 attention 均值, 不依赖 LLM 语义判定; llm_peer paper 用 LLM-determined
    # semantic peer (Cao 2025 RAS 风格的语义相似度), 与 P2 的 4 类银行分类完全不同。
event_studies:  # R2-M11 + R45-m03 修订: P2 applicable events 引用 Appendix C event id
  - E1   # 2013-06-13 yuebao_launch
  - E2   # 2016-08-24 p2p_regulation
  - E4   # 2020-11-03 ant_ipo_pause
  - E5a  # 2022-09-01 data_export_assessment_rules
  - E5b  # 2023-09-30 data_export_management_rules
targets:
  primary_outlet: JCF
  ambitious_outlet: JFE
  backup_outlet: [JBF, JFI]  # R48-M01 + R50-M01: list 形式与 §3.1 P2 backup 列 "JBF / JFI" 完整对齐
  submission_window: 2027-03-15  # R47-M03 增 (per §5.11.1)
sample:  # R14-M02 增 sample section per schema
  n_bank_min: 200
  t_year: 18
  obs_target_min: 3000
audit_rounds_target_min: 8
```

### B.3 P3 — `bank_fintech_substance` (新建)

```yaml
paper_id: bank_fintech_substance
spec_version: 2.0.0
status: new
differentiation_claim: |
  P3 度量银行 fintech 战略宣告的"实质性 vs 象征性"差异 (W&Z 1994/1998 ASQ)。
  R17-m01 + R21-m02 跨 paper 区分 (B-route 3 + existing 4 paper, 共 7 对照):
  - 与 P1 (tone): P3 度量 W&Z 二元 substantiveness; P1 度量连续 tone — 性质不同 (实质 vs 情感)
  - 与 P2 (attention): P3 关注公告的 substantive vs symbolic 属性; P2 关注媒体对银行的 attention exposure 量
  - 与 P4 (locus): P3 度量公告的 W&Z 二元属性 (实质/象征); P4 区分公告的 locus 二元属性 (底层/应用); 二维交叉但独立
  - 与现有 llm_peer: P3 不构造 LLM peer 网络 IV, 仅 firm-level substantiveness; llm_peer 用语义同业网络
  - 与现有 brokerage_network: P3 不用网络中心性, 仅 firm-level W&Z 二元标签; brokerage 用网络位置异质性
  - 与现有 benefit_society: P3 不做态度投影 (LLM-Embedding 双极锚点), 仅用 W&Z substantiveness 二元标签
  - 与现有 strategic_diff: P3 度量 firm 自身 公告属性 (binary); strategic_diff 度量 firm 在 N-邻群中的战略差异度 (distinctness, distance)
outcome:
  primary: long_run_roa_change_3yr  # 长期 ROA 反转检验
  construction: |  # R2-M15 补: 公式
    long_run_roa_change_3yr[bank_b, year_t] = ROA[bank_b, year_t+3] - ROA[bank_b, year_t]
    (within-bank 3-year forward change; 用于检验 W&Z 1994 框架下
    象征性 fintech 宣告 → 短期股价正反应 → 长期 ROA 反转 (negative);
    在 T=18 panel 上, t ∈ {2007, ..., 2021} 各有对应 t+3 outcome)
  short_run: car_3day_window_fintech_announcement  # R7-M03 + R10-M01: dual outcome (fintech 公告事件窗口, 与 P1 tone shock 窗口区分)
  secondary: [ceo_turnover_2yr, executive_pay_change, board_change]
  enrichment_source: M0.5.11 (CSMAR 年报 ROA + 高管离职 + 高管薪酬 + CSMAR daily returns; derived event-window CAR construction per §5.3.2 M0.5.11, R12-m01)  # R8-M04
treatment:
  primary: innovation_substantiveness_full  # R35-M01 同步 CLAUDE.md v3.2.0 pipeline 实际列名
  alternative: [innovation_substantiveness_ctx, substantive_minus_symbolic_gap]
  alternative_construction:  # R29-m01 + R35-M01 derived 字段说明
    substantive_minus_symbolic_gap: innovation_substantiveness_full - (1 - innovation_substantiveness_full)  # M0.5.X / stage 24-40 panel construct 阶段衍生 (简单 algebraic; ∈ {-1, +1})
controls:  # R9-M01 增 controls 字段 (与 §B.1/B.2 schema 一致)
  bank_level: [ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth]
  year_level: [gdp_growth, m2_growth]
  fixed_effects: [bank_fe, year_fe]
identification:
  baseline: long_panel_within_bank_within_year
event_studies:  # R2-M11 + R2-M04 + R45-m03 修订: P3 applicable events 引用 Appendix C event id
  - E1  # 2013-06-13 yuebao_launch — substantive-symbolic gap 时间动态起点
  - E2  # 2016-08-24 p2p_regulation
  - E3  # 2017-04-27 asset_management_rules — cross-sectional intensity DiD (pre-2017 理财占比)
  - E4  # 2020-11-03 ant_ipo_pause
targets:
  primary_outlet: SMJ
  secondary_outlet: AMJ  # R3-M06 修订: cascade intermediate (SMJ → AMJ → ASQ); 与 §3.1 Backup 列保持一致
  ambitious_outlet: ASQ  # cascade 终点
  sequential_resubmission: |  # R1-M07 + R3-M02 顺序投稿 (不是 dual submission)
    SMJ → AMJ → ASQ cascade (Primary path, 完整 W&Z 框架); 任一阶段 reject 后:
    改写为 disclosure quality 框架的独立论文投 JFE corp finance track (Salvage path)
    (重新表述研究问题 / 切换理论 anchor / 仅保留 long_run_roa_change_3yr outcome /
    删除组织学叙事 — 是两篇论文, 不是 dual submission)
  submission_window: 2027-03-15  # R47-M03 增 (per §5.11.1)
sample:  # R14-M02 增 sample section per schema
  n_bank_min: 200
  t_year: 18
  obs_target_min: 3000
audit_rounds_target_min: 8
```

### B.4 P4 — `bank_fintech_locus` (新建)

```yaml
paper_id: bank_fintech_locus
spec_version: 2.0.0
status: new
differentiation_claim: |
  P4 区分银行 fintech 媒体话语中的"底层技术 (区块链 / AI / 云)"与"应用场景 (支付 / 信贷 / 理财)"，
  检验差异化的市场反应与创新产出 (Gomber 2018 JMIS + Goldstein-Jiang-Karolyi 2019 RFS)。
  R17-m01 + R21 跨 paper 区分 (B-route 3 + existing 4 paper, 共 7 对照):
  - 与 P1 (tone): P4 区分公告的 locus 二元属性 (底层/应用); P1 度量连续 tone
  - 与 P2 (attention): P4 度量 locus 二元对照 (1 paper 2 treatment indicators); P2 度量曝光强度 (单一 scalar)
  - 与 P3 (substance): P4 关注 locus (技术维度); P3 关注 substantiveness (实质 vs 象征维度) — 二维交叉但独立
  - 与现有 llm_peer: P4 用 leave-one-out peer locus IV (4 银行类型分类同业), llm_peer 用 LLM-determined 语义同业; 命名 surface-相似但 peer 定义机制完全不同
  - 与现有 brokerage_network: P4 不构造网络中心性 / 二阶语调 IV, 仅 firm-level locus 二元对照
  - 与现有 benefit_society: P4 度量 locus (二元层属性), benefit_society 度量态度 (LLM-Embedding 投影强度), 维度完全不同
  - 与现有 strategic_diff: P4 度量 locus 自身属性, strategic_diff 度量 firm 在 N-邻群中的战略差异度
outcome:
  primary: car_5day_window
  secondary: [patent_fintech_count, citation_weighted_patent]  # R7-M04/M05: capex_it 移到 mediator 角色, 不再列为 outcome
  enrichment_source: M0.5.11 (CSMAR/Wind daily returns for car_5day + IncoPat / 国家专利局 patent count + Kogan 2017 algorithm for citation_weighted; derived event-window CAR construction per §5.3.2 M0.5.11, R12-m01)  # R8-M04
  patent_quality_measure: kogan_2017_market_value  # R2-M12 修订: Kogan 2017 是 outcome 度量, 不是 IV. 依赖 M0.5.11 patent enrichment 输出 (patent_fintech_count + 个股市值 + Kogan 2017 算法), R4-m01
mediator:  # R7-M04 新增 mediator 字段; R9-m02/m04: 增 secondary + 统一 source field schema
  primary: capex_it
  secondary: r_and_d_intensity  # R9-m02: 与 R7-M04 提到的 "R&D / IT capex" 二者对应
  source: M0.5.11 CSMAR (capex_it) + 国家专利局衍生 R&D investment intensity (r_and_d_intensity); 用于 16_mechanism.do.tmpl 的 Baron-Kenny mediation
treatment:
  primary_pair: [locus_layer_full, locus_scenario_full]  # R35-M02 derived from `innovation_locus_full` (CLAUDE.md v3.2.0: 二元 indicator 0=应用 / 1=底层)
  primary_pair_construction:  # R35-M02 explicit derivation
    locus_layer_full: 1 if innovation_locus_full == 1 else 0  # 底层 (区块链/AI/云) indicator
    locus_scenario_full: 1 if innovation_locus_full == 0 else 0  # 应用 (支付/信贷/理财) indicator
  secondary: [locus_gap]  # R29-M01 schema-conform list 形式; column name only
  secondary_construction:  # R29-M01 公式分离: derived 在 M0.5.X / stage 24-40 panel construct 阶段
    locus_gap: locus_layer_full - locus_scenario_full  # ∈ {-1, +1}
controls:  # R9-M01 增 controls 字段
  bank_level: [ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth]
  year_level: [gdp_growth, m2_growth]
  fixed_effects: [bank_fe, year_fe]
identification:
  baseline: layer_x_event_study  # E1/E4 events × 2 locus class
  iv:  # R2-M12 修订: Kogan 2017 不是 IV; locus IV 用 peer-based
    primary: leave_one_out_peer_locus_iv  # Cao 2025 RAS 风格
    fallback: layer_scenario_industry_event_iv  # E1/E4 events 作为 instrument for locus
    # R5-m04 与 llm_peer paper 区别: P4 leave-one-out peer locus = 银行类型 (国有 / 股份制 /
    # 城商 / 农商) 子样本内同类银行 locus 均值; llm_peer paper 用 LLM-determined 语义同业。
    # 二者 IV 命名 surface-相似但底层 peer 定义机制完全不同 (P4 用分类同业, llm_peer 用语义)。
event_studies:  # R2-M11 + R45-m03 修订: P4 applicable events 引用 Appendix C event id
  - E1   # 2013-06-13 yuebao_launch
  - E4   # 2020-11-03 ant_ipo_pause
  - E5a  # 2022-09-01 data_export_assessment_rules
  - E5b  # 2023-09-30 data_export_management_rules
heterogeneity_wave:  # R4-M03 重定义: 三波严格对称 (各 3 年) + consolidation 独立段
  pre_period:   2007_2012  # pre-fintech baseline (中文媒体几乎无 "金融科技" 一词)
  wave_1:       2013_2015  # 互联网金融 wave (余额宝)
  wave_2:       2016_2018  # 区块链 / 早期 AI wave
  consolidation: 2019_2021 # 蚂蚁叫停后期 monetary tightening + 监管收紧 transition period (不计入 "三波" narrative)
  wave_3:       2022_2024  # 大模型 wave
  # 注: "三波 fintech 浪潮" 严格指 wave_1 / wave_2 / wave_3 各 3 年; consolidation 是
  # 2018 → 2022 之间的 transition, 在 P4 异质性章作为对照组
targets:
  primary_outlet: RFS
  ambitious_outlet: JF
  backup_outlet: JFE
  submission_window: 2027-03-15  # R47-M03 增 (per §5.11.1)
sample:  # R14-M02 增 sample section per schema
  n_bank_min: 200
  t_year: 18
  obs_target_min: 3000
audit_rounds_target_min: 8
```

---

## Appendix C: Exogenous Shock Event Library

(M0.4 阶段写入 `config/exogenous_shocks.yaml`)

```yaml
events:
  - id: E1
    date: 2013-06-13
    name: yuebao_launch
    name_zh: 余额宝上线
    description: |
      支付宝余额宝产品上线，标志中国互联网金融元年。
      首日规模 1 亿，1 年达 5,000 亿；触发银行业整体 fintech 战略响应。
    treatment_logic: post dummy × bank pre-2012 fintech-exposure (Hassan-style intensity)
    identification: cross-sectional intensity DiD (基于 pre-2012 fintech 暴露度 × post-event dummy + bank FE); R46-M08 同步 §5.7.2 表
    applicable_papers: [P1, P2, P3, P4]  # R28-M01 同步 §5.7.2 表 (R2-M04 加 P3)
    reference: 谢平 (2014) 经济研究, 49(2)

  - id: E2
    date: 2016-08-24
    name: p2p_regulation
    name_zh: 网络借贷整顿
    description: |
      银监会等四部委发布《网络借贷信息中介机构业务活动管理暂行办法》，
      P2P 平台密集出清；银行 fintech 战略由对抗转为合作。
    treatment_logic: 与 P2P 业务有交集的银行 = treated
    identification: bank-level continuous exposure (与 P2P 业务 pre-2016 媒体共现强度 × post-event dummy); R46-M08 同步 §5.7.2 表
    applicable_papers: [P1, P2, P3]
    reference: 银保监会 (2016) 〔2016〕1 号文

  - id: E3
    date: 2017-04-27
    name: asset_management_rules
    name_zh: 资管新规
    description: |
      央行等四部委《关于规范金融机构资产管理业务的指导意见》征求意见稿；
      正式稿 2018-04-27 发布；银行理财业务彻底变革。
    treatment_logic: 理财业务占比高的银行 = treated (连续 treatment)
    identification: **cross-sectional intensity DiD** (基于 pre-2017 银行理财业务占比 × post 2017 dummy; 不是 staggered DiD, 因为政策对所有银行同时生效); R46-M08 同步 §5.7.2 表
    applicable_papers: [P1, P3]
    reference: 央行 (2018) 银发〔2018〕106 号

  - id: E4
    date: 2020-11-03
    name: ant_ipo_pause
    name_zh: 蚂蚁集团 IPO 暂停
    description: |
      上交所、港交所同日暂停蚂蚁集团 IPO；标志监管对 fintech 巨头态度反转。
      触发银行 fintech 战略从"拥抱 BigTech"转向"自建"。
    treatment_logic: 与蚂蚁有股权 / 合作关系的银行 = treated
    identification: bank-level continuous exposure (与蚂蚁 / 网商银行 / 余额宝 pre-2020 关联强度 × post-event dummy); R46-M08 同步 §5.7.2 表
    applicable_papers: [P1, P2, P3, P4]
    reference: 经济研究多篇 2021-2022

  - id: E5a
    date: 2022-09-01
    name: data_export_assessment_rules
    name_zh: 数据出境安全评估办法 (实施)
    description: |
      国家网信办《数据出境安全评估办法》正式实施 (2022-07-07 公布, 2022-09-01 实施);
      银行跨境 fintech 业务首批受限。
    treatment_logic: 跨境业务银行 = treated (binary)
    identification: binary treated × post-event dummy + bank FE
    applicable_papers: [P2, P4]  # R28-M01 同步 §5.7.2 表 (R3-M07 加 P2: 跨境 attention intensity)
    reference: 网信办 (2022) 第 11 号令

  - id: E5b
    date: 2023-09-30
    name: data_export_management_rules
    name_zh: 数据出境管理办法 (规范促进)
    description: |
      国家网信办《促进和规范数据跨境流动规定》;
      底层技术（云 / 数据中心）跨境合规要求进一步明确, 与 E5a 复合 treatment。
    treatment_logic: 跨境业务银行 = treated (binary); 可与 E5a 联合 DiD
    identification: binary treated × post-event dummy; 或与 E5a 复合 (双 event)
    applicable_papers: [P2, P4]  # R28-M01 同步 §5.7.2 表 (R3-M07 加 P2)
    reference: 网信办 (2023) 第 16 号令
```

---

## Appendix D: Current Asset Inventory (Pre-M-1 状态)

### D.1 Papers (5)

| Paper | Status | Stata templates (含 shared) |
|---|---|---|
| `bank_fintech_tone` | v3.2.0 完整 | 14 shared + 1016-line falsification |
| `benefit_society` | v2.12 完整 | 14 shared + 187-line token_hidden_regression |
| `brokerage_network` | v3.3.0 | 14 shared + 345-line network_causal |
| `llm_peer` | v3.3.0 | 14 shared + paper-specific |
| `strategic_diff` | v3.3.0 | 14 shared + 268+119 line override |

### D.2 Stata templates (55 total — R1-M01 修订计数)

实测 `find news_process/papers/_common/stata_templates/ -name '*.do.tmpl' | wc -l` = 55:

```
papers/_common/stata_templates/
├── 14 root shared templates:
│   ├── 00_master.do.tmpl
│   ├── 01_data_prep.do.tmpl
│   ├── 10_table1_descriptives.do.tmpl
│   ├── 11_table2_main_m1m6.do.tmpl
│   ├── 12_table3_mechanism.do.tmpl
│   ├── 13_table4_heterogeneity.do.tmpl
│   ├── 14_table5_advanced_robustness.do.tmpl
│   ├── 20_tableA1_inter_track_kappa.do.tmpl
│   ├── 21_tableA2_main_spec_switch.do.tmpl
│   ├── 22_tableA3_bartik_iv.do.tmpl
│   ├── 23_tableA4_radius_sensitivity.do.tmpl
│   ├── 24_tableA5_dictionary_method.do.tmpl
│   ├── 30_figure1_event_study.do.tmpl
│   └── 31_figure_coefplot_dual.do.tmpl
├── benefit_society/    (17 templates) — W&Z token/hidden + 9 衍生
├── brokerage_network/  (8 templates)
├── llm_peer/           (8 templates)
└── strategic_diff/     (8 templates)

合计: 14 root + 17 + 8 + 8 + 8 = 55 templates
```

注: bank_fintech_tone paper 没有 `_common/stata_templates/<paper>/` 子目录, 因为其
paper-specific 资产在 `papers_assets/bank_fintech_tone/do/` (2 files: 50_robustness +
falsification_template) — 这是 P1 / 主线 paper 的历史性约定, 新增 P2/P3/P4 按 M2
统一约定走 `_common/stata_templates/<paper_id>/`。

### D.3 Pipeline parquet (v3.3.0 baseline)

```
00_preprocessing.parquet:        9,427 × 13
11_bank_news.parquet:            4,054 × 22
12_fintech_news.parquet:         1,170 × 29
14_fintech_intensity.parquet:    1,170 × 31
15_article_alignment.parquet:    1,170 × 32
21_tone_llms.parquet:              865 × 115
22_words_tone.parquet:             865 × 256
23_bert_tone.parquet:              865 × 313
24_herd_decay.parquet:             865 × 315
40_panel_yearly.parquet:           168 × 2024
51_panel_with_controls.parquet:    168 × 2033
```

### D.4 Manuscripts (v3.3.0: 10 双语)

```
papers_assets/<paper>/drafts/{en,zh}/manuscript.tex (各 paper × 2 lang = 10)
```

M1 完成后扩展到 **16 双语** (8 paper × 2)。

---

## Appendix E: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| v2.0 | 2026-05-16 | Claude Opus 4.7 | Initial v2 plan; superseded v1 unconfirmed conversation draft post-data-reality-check |
| v2.1 | 2026-05-16 | Claude Opus 4.7 | Round 1 self-audit fixes (41 findings: 28 MAJOR + 13 MINOR). 主要修订: §2.3 citations (Roth 2022, Rambachan-Roth 2023, Cong-He 2019, Hsieh-Klenow 2009 替换 unverifiable / 错误引文); §3.2 P3 顺序投稿伦理澄清; §3.4 v3.3.0→v34 panel 迁移规范; §5.1.1.bis 前置 prerequisite; §5.1.5 audit 5→8 轮; §5.2 8 paper retrofit; §5.4.3+§5.5 模板位置约定与现有 4 衍生 paper 一致 (`_common/stata_templates/<paper_id>/`); §5.5.3 模板数学 (55→71 修订); §5.6.3 exemplar paper 指定; §5.7.2 events identification 策略差异化, E5 拆 E5a+E5b; §5.7.3 SSC prerequisites + csdid_plot 正确 syntax; §5.9.2 per-paper robustness matrix; §5.9.4 Rambachan-Roth honest DiD CI 规范; §5.10.3 G7 salami 检查 4 条 + 5 视角与 M6 一致; §6 G-1 yellow band + G2 71 templates + G4 24 spec; §7 audit matrix 95→98; §8 R10/R11 修订; §10.2/10.3 wall-time vs Claude time 区分 + range; §11.1 C1 P3 退化处理; §11.2 C2-lite yellow band; §14 RACI matrix 新增; Appendix B P1 spec roa 重复修复; Appendix C E5 拆分; Appendix D template 计数修订 |
| v2.2 | 2026-05-16 | Claude Opus 4.7 | Round 2 self-audit fixes (26 findings: 19 MAJOR + 7 MINOR). 主要修订: §2.1 in-scope M0/M3/M4 同步 R1 修订 (M0 8 spec / M3 6 new + 10 existing / M4 14 spec); §4 总周期 10→9.5 月 (与 §10.2 对账); §5.2.3 spec.yaml event_studies 列全 5 events; §5.6.4 G3 拆分 6 new + 10 existing regression; §5.7.1 14 spec count; §5.7.2 P3 加 E1; §5.7.4 G4 15 spec; §5.8.2 IV per paper_spec.yaml; §5.8.3 G5 log 数修订; §5.9.3 fatal flaw 4 类型定义; §5.9.5 M6 audit 5 轮枚举; §10.1 LLM cost 拆开 M0.5.4/M0.5.8 (~$4,062 含 buffer) + submission fee 注; §11.1 C1 sub-cases (C1-a 完全不足 / C1-b 时间断层); §11.3 C3 命名 M-1.bis; Appendix B P1/P2/P3/P4 spec event_studies 列全 + P3 outcome 公式 + P4 IV 修正 (Kogan 2017 不是 IV) + P4 heterogeneity_wave 含 pre_period + consolidation; §3.2 P4 修正驱动同步 wave 定义 |
| v2.3 | 2026-05-16 | Claude Opus 4.7 | Round 3 self-audit fixes (14 findings: 9 MAJOR + 5 MINOR). 主要修订: §6 G4 row 24→17 spec (同步 R2 fix); §3.1/§3.2/§B.3 P3 投稿 cascade (SMJ→AMJ→ASQ + JFE salvage) 三处统一; §4 timeline M0.5 起 6/8→6/9 (避免 M0 overlap); §8 R11 "plan v2.1" → "next v2.x revision"; §3.4 #2 时序修订 (M0 G0 检查 v3.3.0 panel, v34 验证延后到 M0.5 G0.5); §B.3 增 secondary_outlet AMJ; §5.7.2 表 E5a/E5b applicable_papers 加 P2 (R3-M07 双向对账); §5.7.1/§5.7.4 spec count 15→17; §11.4 wave 描述同步 §B.4; Appendix A 直接成本 $3.7K → $4.062K; §14 RACI M-1 R 列加 用户 (prerequisite delivery); §5.2.3 spec.yaml secondary 同步 §B.2; §11.1 C1-a 表述放宽 |
| v2.4 | 2026-05-16 | Claude Opus 4.7 | Round 4 self-audit fixes (9 findings: 6 MAJOR + 3 MINOR). 主要修订: §5.5.2 P4 17_heterogeneity wave 描述同步 §B.4; §5.8.2 异质性 wave 描述同步; §B.4 wave 重定义为对称三波 + consolidation (R4-M03: pre/wave_1/wave_2/consolidation/wave_3); §B 各 paper outcome 类变量明确 M0.5.11 financial enrichment 依赖 (R4-M04); §5.3.2 新增 M0.5.11 financial / patent enrichment step + §5.3.4 输出 47_financial_outcomes_panel; §3.4 + §5.3.5 v34 subset 描述增 bank 过滤 (R4-M06); §B.4 patent_quality_measure data source 注; §5.7.2 P3 E1 "quarter" → "year"; §11.2 C2-lite MICE imputation 方法; §3.2 / §11.4 wave 描述全部同步 R4-M03 |
| v2.5 | 2026-05-16 | Claude Opus 4.7 | Round 5 self-audit fixes (9 findings: 3 MAJOR + 6 MINOR). 主要修订: §5.3.2 M0.5.11 enrichment 补 daily stock returns (P4 car_5day 依赖); §5.3.4 增 balanced/unbalanced panel 双版 + 48_daily_returns_panel; §5.10.2 M7.4 sub-task 改为 5-视角 (含 Devil's Advocate); §9 D6 重表述 (working paper / 内部 / 第三方授权 + 期刊 replication policy); §3.4 #4 84 banks 来源 frozen 路径; §B.2 / §B.4 IV 与 llm_peer 区别注; §11.1 C1-a/b tie-break (C1-a 优先); §6 G6 Honest DiD M 全 4 档 |
| v2.6 | 2026-05-16 | Claude Opus 4.7 | Round 6 self-audit fixes (7 findings: 4 MAJOR + 3 MINOR). 主要修订: §5.5.2 16_mechanism column 修正 (真正 mediator 测试不是 main regression); §5.5.2 17_heterogeneity 各 paper 丰富切分 (4 银行类型 × wave × SOE × capital quartile); §5.5.2 18_robustness 对齐 §5.9.2 全 7 维度; §5.7.3 honestdid SSC 优先 GitHub fallback; §13 spec semver 语法澄清; §11.2 C2 上市银行数 ~40-60 (实测) |
| v2.7 | 2026-05-16 | Claude Opus 4.7 | Round 7 self-audit fixes (6 findings: 5 MAJOR + 1 MINOR). 主要修订: §5.5.2 16_mechanism KHB→Baron-Kenny (R7-M01); P2 mediator 改为 observable proxy `ln_fintech_mdna_length` (R7-M02); P3 mechanism 改为 dual outcome regression 非 mediation (R7-M03); §B.4 outcome.secondary 去掉 capex_it; §B.4 新增 mediator 字段 (R7-M04/M05); §B.3 outcome 新增 short_run CAR field; §5.5.2 17_heterogeneity small-cell warning |
| v2.8 | 2026-05-16 | Claude Opus 4.7 | Round 8 self-audit fixes (7 findings: 4 MAJOR + 3 MINOR). 主要修订: §B.2 P2 增 mediator 字段 (R8-M01); §B.1 P1 outcome ar_3day → car_3day 命名统一 (R8-M02); §5.7.2 G4 + §5.7.3 模板 + G4 acceptance 统一: 所有 6 events 是 intensity-based DiD 不是 staggered (R8-M03); §B.1/B.2/B.3 outcome 增 enrichment_source 字段 (R8-M04); §5.6.2 lit review 数据估计校正; §5.9.2 sample cuts 2007-2010 → pre_period 2007-2012; §1 sibling doc link visible name 校正 |
| v2.9 | 2026-05-16 | Claude Opus 4.7 | Round 9 self-audit fixes (5 findings: 2 MAJOR + 3 MINOR). 主要修订: §B.3/B.4 spec 增 controls 字段 (R9-M01 schema 统一); §5.3 critical path 12 wk 解释 (sub-task sequential 14 wk - parallel 2 wk = 12 wk, R9-M02); §B.4 mediator 增 r_and_d_intensity secondary + 统一 source field schema (R9-m02/m04); §11.1 C1-a P3 退化处理具体化 (保留 car_3day, 删除 long_run_roa, R9-m01/m05) |
| v2.10 | 2026-05-16 | Claude Opus 4.7 | Round 10 self-audit fixes (6 findings: 1 MAJOR + 5 MINOR). 主要修订: P1/P3 outcome 命名差异化 (car_3day_window_tone_shock vs car_3day_window_fintech_announcement, R10-M01 避免 salami slicing); §1 anchor commits "14 rounds/59 findings"; §B.1 differentiation_claim 增 P1 vs P3 区分 (R10-m04); §5.5.2 17_heterogeneity wave 5 segments 使用方式 (interaction 主 + sample cut robustness); §11.1 C1-b sub-cases (b1/b2/b3 按断层位置); §10.3 M5 range 24-40 标准 ±25% |
| v2.11 | 2026-05-16 | Claude Opus 4.7 | Round 11 self-audit fixes (2 findings: 0 MAJOR + 2 MINOR; **首次 MAJOR=0**). 主要修订: §5.3.2 M0.5.11 enrichment 显式衍生 event-window CAR variables (R11-m01); §5.5.2 P3 16_mechanism template naming 与 dual outcome 概念冲突 footnote (R11-m02) |
| v2.12 | 2026-05-16 | Claude Opus 4.7 | Round 12 self-audit fixes (3 findings: 1 MAJOR + 2 MINOR). 主要修订: §5.2.3.bis paper_spec.yaml schema reference (R12-M01 显式 schema + 新 test test_paper_spec_schema.py); §B.1/B.3/B.4 enrichment_source 增 derived CAR construction reference (R12-m01); §11 R7 media source detrend implementation 具体化 (R12-m02 pubcode 字段 + 归一化公式) |
| v2.13 | 2026-05-16 | Claude Opus 4.7 | Round 13 self-audit fixes (2 findings: 1 MAJOR + 1 MINOR). 主要修订: §5.2.3 + §5.2.3.bis schema flatten — differentiation_claim 移到顶层 (与 §B specs 实际结构一致), theory 仅 optional metadata; authors 字段 mark optional (R13-M01/m01); §5.2.3 example version → spec_version |
| v2.14 | 2026-05-16 | Claude Opus 4.7 | Round 14 self-audit fixes (2 findings: 2 MAJOR). 主要修订: §B.1 P1 iv scalar → dict 形式 (R14-M01 与 schema 一致); §B.1/B.2/B.3/B.4 都增 sample section (R14-M02 per schema required) |
| v2.15 | 2026-05-16 | Claude Opus 4.7 | Round 15 self-audit fixes (2 findings: 1 MAJOR + 1 MINOR). 主要修订: §5.2.3.bis schema iv 标 optional (R15-M01 P3 不需 IV); treatment 字段多态结构明确 (R15-m01 P1/P3 vs P2 vs P4 三种字段组合) |
| v2.16 | 2026-05-16 | Claude Opus 4.7 | Round 16 self-audit fixes (1 finding: 0 MAJOR + 1 MINOR). §5.2.3 example 前增 demonstration 说明区分 example vs §B.2 actual spec (R16-m01) |
| v2.17 | 2026-05-16 | Claude Opus 4.7 | Round 17 self-audit fixes (1 finding: 0 MAJOR + 1 MINOR). §B.2/B.3/B.4 differentiation_claim 增 vs 另 3 paper + vs 现有 paper 区分 (R17-m01 跨 spec 对称) |
| v2.18 | 2026-05-16 | Claude Opus 4.7 | Round 18 = 0 finding (streak 1/7 reached); Round 19 self-audit fixes (1 finding: 0 MAJOR + 1 MINOR; streak reset). 主要修订: §6 G0 acceptance 增 LLM cost cap $4,200 lock (R19-m01 per §8 R10 mitigation 显式) |
| v2.19 | 2026-05-16 | Claude Opus 4.7 | Round 20 self-audit fixes (1 finding: 0 MAJOR + 1 MINOR). §B.1 P1 differentiation_claim 扩成 7 对照 (vs B-route 3 + vs existing 4 paper) — 同 §B.2/B.3/B.4 R17-m01 完成对称 (R20-m01) |
| v2.20 | 2026-05-16 | Claude Opus 4.7 | Round 21 self-audit fixes (2 findings: 0 MAJOR + 2 MINOR). §B.2/B.3/B.4 differentiation_claim 全部扩展到 7-paper 对称 (R21-m01/m02 同 R20-m01 §B.1); 4 §B specs differentiation_claim 现完全对称 |
| v2.21 | 2026-05-16 | Claude Opus 4.7 | Round 22-23 = 0 finding (streak 2/7); Round 24 self-audit fixes (1 finding: 0 MAJOR + 1 MINOR; streak reset). §5.2.3 spec.yaml audit_rounds_target_min comment 更新 (R24-m01: M5 ≥ 8 § M6 ≥ 5 区分) |
| v2.22 | 2026-05-16 | Claude Opus 4.7 | Round 25-27 = 0 finding (streak 3/7); Round 28 self-audit fixes (1 finding: 1 MAJOR; streak reset). Appendix C E1/E5a/E5b applicable_papers 同步 §5.7.2 表 (R28-M01: E1 加 P3 per R2-M04; E5a/E5b 加 P2 per R3-M07) |
| v2.23 | 2026-05-16 | Claude Opus 4.7 | Round 29 self-audit fixes (2 findings: 1 MAJOR + 1 MINOR). §B.4 treatment.secondary scalar → list + secondary_construction 字段 (R29-M01 schema-conform); §B.3 treatment.alternative_construction 字段 (R29-m01 derived 公式分离); §5.2.3.bis schema 增 alternative_construction / secondary_construction 字段 |
| v2.24 | 2026-05-16 | Claude Opus 4.7 | Round 30 self-audit fixes (1 finding: 1 MAJOR). §2.3 增 Sun & Abraham (2021) J. Econometrics anchor (R30-M01: §5.7.3 eventstudyinteract 命令的 canonical reference) |
| v2.25 | 2026-05-16 | Claude Opus 4.7 | Round 31 self-audit fixes (1 finding: 1 MAJOR). §2.3 增 Roodman et al. (2019) Stata Journal anchor (R31-M01: boottest 命令 canonical reference) |
| v2.26 | 2026-05-16 | Claude Opus 4.7 | Round 32 self-audit fixes (1 finding: 1 MAJOR). §2.3 增 Baron-Kenny (1986) + Imai-Keele-Tingley (2010) mediation anchors (R32-M01: §5.5.2 P2/P4 16_mechanism canonical refs) |
| v2.27 | 2026-05-16 | Claude Opus 4.7 | Round 33 self-audit fixes (1 finding: 1 MINOR). §10.3 preamble range "±25%" 改为 "≈ ±25% (各 milestone 实际 ±15-33% asymmetric, M5/M6/M7 上界更宽)" (R33-m01 与实际 range table 对账) |
| v2.28 | 2026-05-16 | Claude Opus 4.7 | Round 34 = 0 finding (streak 1/7); Round 35 self-audit fixes (2 findings: 2 MAJOR; streak reset). §B.3 P3 treatment 名 substantiveness_index_full → innovation_substantiveness_full 同步 CLAUDE.md v3.2.0 pipeline 实际列名 (R35-M01); §B.4 P4 treatment.primary_pair derived from innovation_locus_full 显式 construction step + schema 增 primary_pair_construction 字段 (R35-M02) |
| v2.29 | 2026-05-16 | Claude Opus 4.7 | Round 36 self-audit fixes (1 finding: 1 MINOR). §B.2 P2 treatment 增 source 注 (R36-m01: pipeline stage 14_fintech_intensity 衍生; M0 G0 时按实际列名对齐) |
| v2.30 | 2026-05-16 | Claude Opus 4.7 | Round 37 self-audit fixes (1 finding: 1 MAJOR). §5.2.3.bis schema treatment 增 source 字段 optional (R37-M01: 与 R36-m01 §B.2 source 字段对齐) |
| v2.31 FINAL-revised | 2026-05-16 | Claude Opus 4.7 | Round 38-R44 = 0 finding (streak 7/7 主张, 后由 R46 推翻); Round 45 用户请求"最后一次审核"补充 (3 finding: 0 MAJOR + 3 MINOR cosmetic). §1 Baseline 描述 e815237 / 8d33c46 厘清 (R45-m01); §11.1 C1-a "P1 主战 + P3 退化稿 2 paper" 措辞校正 (R45-m02); §B.1-B.4 event_studies entries 引用 Appendix C event id 一致格式 (R45-m03) |
| v2.32 FINAL-truly-revised | 2026-05-16 | Claude Opus 4.7 | Round 46 用户再请求"最后一次全面系统地审核" — R38-R44 streak 主张作废 (实际 stamp-clean 漏审); 发现 10 真实 finding (9 MAJOR + 1 MINOR): §5.2.3 example `variables:` wrapper 删除与 §B specs / schema 对齐 (R46-M01); §5.5.2 表格被 narrative text 打断修复 (R46-M02); §6 G0.5 LLM cost $3000 → $4,200 (R46-M03) + v3.3.0 兼容描述补 bank subset + categoricals (R46-M04); §6 G1 row 同步 6 new + 10 existing (R46-M05); §6 G3 row 同步 §5.6.4 完整版 (R46-M06); §9 D4 "P3 双投" → cascade 顺序 (R46-M07); Appendix C E1-E4 增 identification 字段 (R46-M08); Appendix A 总 audit 95 → 98 轮 (R46-M09); §5.2.5/§5.5.5/§5.6.5/§5.7.5/§5.10.4 audit list 补焦点 (R46-m01) |
| v2.33 FINAL-deeply-revised | 2026-05-16 | Claude Opus 4.7 | Round 47 用户再请求"最后一次以最高标准全面系统地审核" — 揭示 R8-M01 / R9-M01 / R36-m01 / R8-M04 等 "§B.X 增字段" fix 实际只 edit §5.2.3 example 内嵌 variables wrapper, 没 propagate 到 §B.2 P2 actual spec; R46-M01 删除 wrapper 后暴露. 5 MAJOR findings: §B.2 P2 spec 真正增 mediator + controls + treatment.source (R47-M01); §5.2.3 example outcome 增 enrichment_source (R47-M02); §B.1-B.4 都增 submission_window: 2027-03-15 (R47-M03); §5.2.3 example 删除 stata_templates block 不在 schema / §B specs (R47-M04); §5.2.3 example outcome.secondary patent_fintech → patent_fintech_count 与 §B.2 一致 (R47-M05) |
| v2.34 | 2026-05-16 | Claude Opus 4.7 | Round 48 用户请求"对本轮 plan 修改最高标准 / 连续 3 次独立交叉对账". 第 1 轮独立交叉对账 (cross-validation, not stamp-clean): R47/R46 各 fix 在 plan 中已实际 propagate ✓; 但发现 1 新 MAJOR (R48-M01): §B.1 / §B.2 spec targets 缺 backup_outlet (per §5.11.1 P1 backup=JCF, P2 backup=JBF). Fix: §B.1 增 backup_outlet=JCF; §B.2 增 backup_outlet=JBF |
| v2.35 | 2026-05-16 | Claude Opus 4.7 | Round 49 第 2 轮独立交叉对账 — 3 MINOR findings. R49-m01: schema sequential_resubmission / heterogeneity_wave 加 "optional, P3/P4-specific" 一致 (并删除原 duplicate heterogeneity_wave line in schema); R49-m02: §6 G2 row 增 Macro/var 截断检查项 (同步 §5.5.4); R49-m03: §6 G7 row 增 Salami slicing 4 条 explicit criteria (同步 §5.10.3) |
| v2.36 | 2026-05-16 | Claude Opus 4.7 | Round 50 第 3 轮独立交叉对账 — 1 MAJOR finding. R50-M01: §3.1 backup 列 (2 outlets list) 与 §B.X spec backup_outlet (单 string) 不一致. Fix: schema backup_outlet 改为 `list | str` (与 secondary_outlet 一致); §B.1 backup_outlet: [JCF, JBF]; §B.2 backup_outlet: [JBF, JFI]. §B.4 已用 ambitious + backup 分别表达 OK |
| v2.37 | 2026-05-16 | Claude Opus 4.7 | Round 51 streak 第 1 次 attempt — 1 MAJOR finding. R51-M01: §B.1 P1 spec controls 缺 fixed_effects 字段 (schema required; §B.2/B.3/B.4 都有; R1-M13 修订时遗漏). Fix: §B.1 controls 增 `fixed_effects: [bank_fe, year_fe]` |
| v2.38 | 2026-05-16 | Claude Opus 4.7 | Round 52 = 0 finding (streak 1/3 reached). Round 53 fresh-eye 切换维度 (§6 vs §5.x G row item-by-item) — 5 MAJOR findings. R53-M01: §6 G1 增 pytest test_papers_b_route; R53-M02: §6 G2 增 pytest test_stata_templates; R53-M03: §6 G4 增 SSC 包齐全 + Cluster-robust SE + exogenous_shocks.yaml 完整定义; R53-M04: §6 G5 增 4 表 + 3 图 + 主回归系数符号 + Stata log + Pre-registration deviation; R53-M05: §6 G6 增 Wild bootstrap p < 0.10 |
| v2.39 | 2026-05-16 | Claude Opus 4.7 | Round 54 fresh-eye — 1 MINOR. R54-m01: §5.8.2 Week 1 描述把 P3 cross-sectional intensity 列在 IV 范畴, 但 §B.3 P3 无 IV (per R15-M01); P3 cross-sectional intensity 是 baseline 而非 IV. Fix: 澄清 "P3 无 IV; baseline 即 cross-sectional intensity DiD 替代 IV" |
| v2.40 | 2026-05-16 | Claude Opus 4.7 | Round 55-56 = 0 finding (streak 2/3 reached). Round 57 fresh-eye — 1 MINOR. R57-m01: schema 字段顺序 (event_studies → targets → heterogeneity_wave → sample) 与 §B.4 spec (event_studies → heterogeneity_wave → targets → sample) 不一致. Fix: schema heterogeneity_wave 移到 event_studies 后 targets 前 (与 §B.4 一致) |
| v2.41 | 2026-05-16 | Claude Opus 4.7 | Round 58 = 0 finding (streak 1/3). Round 59 fresh-eye — 1 MAJOR. R59-M01: §5.1.4 G-1 raw 完整性 阈值 (< 95% = < 380K) 与 §11.1 C1-a (< 200K) 不一致; [200K, 380K) yellow band 未明. Fix: §6 G-1 row 增 raw yellow band [50%, 95%) → C1-c (软 fallback); §11.1 新增 C1-c sub-case (raw 200-380K + 银行覆盖 ≥ 300, 4 paper 保留 N_eff 缩小 30-50%, 顶刊预期降 0.5 档) |
| v2.42 | 2026-05-16 | Claude Opus 4.7 | Round 60 fresh-eye — 1 MINOR. R60-m01: §5.1.4 G-1 + §6 G-1 缺 "时间断层" 检查项, 但 §11.1 C1-b 触发条件是时间断层 > 2 年. Fix: §5.1.4 G-1 增 6th row "时间覆盖完整性 | 无 > 2 年系统性时间断层 (per M-1.3 覆盖热力图) | C1-b"; §6 G-1 row 同步增 "时间断层 > 2 年: C1-b" |
| v2.43 | 2026-05-16 | Claude Opus 4.7 | Round 61 fresh-eye — 1 MINOR. R61-m01: §11.1 C1-c "缩小 30-50%, 约 2000-5000 obs" 数学不严格 (baseline 3000-9000, 实际缩减 40-70%). Fix: 改为 "N_eff × T_eff ≈ 2000-5000 obs (baseline 3000-9000 缩减约 40-70%)" |
| v2.44 | 2026-05-16 | Claude Opus 4.7 | Round 62 = 0 finding (streak 1/3). Round 63 fresh-eye — 1 MAJOR. R63-M01: mediator 字段顺序 schema (controls 后) / §B.2 (treatment 后) / §B.4 (outcome 后) 三处不一致. Fix: 统一为 §B.4 顺序 (mediator 紧跟 outcome, causal chain proximity): schema 移到 outcome 后 treatment 前; §B.2 同样移到 outcome 后 treatment 前 |
| v2.45 | 2026-05-16 | Claude Opus 4.7 | Round 64 fresh-eye — 1 MAJOR. R64-M01: R63-M01 fix 未传播到 §5.2.3 example (example mediator 仍在 treatment 后). Fix: §5.2.3 example mediator 移到 outcome 后 treatment 前 (与 schema/§B.2/§B.4 一致) |
| v2.46 | 2026-05-16 | Claude Opus 4.7 | Round 65 fresh-eye — 1 MAJOR. R65-M01: schema event_studies 缩进 (嵌套在 identification 块内) vs 4 §B specs top-level event_studies. Fix: schema event_studies 去缩进, 提升到 top level (与 4 §B specs 一致) |
| v2.47 | 2026-05-16 | Claude Opus 4.7 | Round 66 fresh-eye — 1 MAJOR. R66-M01: R65-M01 fix 未传播到 §5.2.3 example (example event_studies 仍 nested under identification). Fix: §5.2.3 example event_studies 去缩进, 提升到 top level (与 schema/4 §B specs 一致) |
| v2.48 | 2026-05-16 | Claude Opus 4.7 | Round 67-68 = 0 finding (streak 2/3). Round 69 fresh-eye — 1 MINOR. R69-m01: §10.3 总 Claude time range "80-128 d" 与 individual milestone ranges sum (76-126) 不对齐. Fix: 改为 "76-126 d" 显示具体加法 |
| v2.49 | 2026-05-17 | Claude Opus 4.7 | Round 70-72 = 0 finding (streak 3/3 closed at R72); 用户再次发起 "自动化执行 / 连续 3 次每轮独立交叉对账完美" 指令 → streak reset, R73 启动. Round 73 self-audit fixes (3 findings: 1 MAJOR + 2 MINOR). R73-M01: §10.1 + §5.3.5 LLM cost breakdown "$50 M-1.4 (scale test)" 子任务 ID 错位 — §5.1.2 canonical M-1.4 是 lexicon clustering (无 LLM cost), M-1.5 才是 Pipeline scale test (含 LLM API); §8 R10 mitigation 正确 reference M-1.5, §10.1/§5.3.5 错位. Fix: §10.1 + §5.3.5 改 M-1.4 → M-1.5; R73-m01: §5.11.1 投稿计划 Backup 列每 paper 仅单 outlet, 与 §3.1 / §B specs backup_outlet 列 list/cascade 不完整对账. Fix: §5.11.1 Backup 列扩展显示完整 cascade (P1 JCF→JBF / P2 JBF→JFI / P3 AMJ→ASQ→JFE salvage / P4 JFE) + 加 §5.11.2 scope 注; R73-m02: §14 RACI matrix M-1 行 Consulted 列只列 D1, 缺 D6 (D6 trigger 时点 = M-1 期 per §9). Fix: §14 M-1 Consulted 增 "+ D6 数据来源类型决策 per §9 R5-m01" |
| (no plan bump) | 2026-05-17 | Claude Opus 4.7 | Round 74 audit-log-only fixes (2 MINOR; 不涉及 plan-doc, 无 version bump). R74-m01: audit log top-level Stop condition (line 4) 仍 epoch 1 "连续 7 轮", 与 epoch 2/3 当前 target "连续 3 轮" 不同步. Fix: line 4-5 epoch 1/2/3 boundary 显式; R74-m02: line 2487 Final Cross-Validation Campaign Summary 状态 "达成 / audit-frozen" 在 R73 重启后失效, 缺 epoch boundary 注. Fix: section heading 改 "Epoch 2 Final ... frozen at R72; superseded by R73" + section 内 epoch boundary 注 |
| v2.50 | 2026-05-17 | Claude Opus 4.7 | Round 75 self-audit fixes (1 MINOR). R75-m01: §3.2 P1 v2 ambitious "RFS / JFE" 2-outlet vs §B.1 ambitious_outlet=RFS (单) + schema ambitious_outlet=str (单) 三向不一致 — JFE 在 §B.1 spec 任何 outlet 字段 (primary/backup/ambitious) 都不存在. Fix (与 R50-M01 backup_outlet 处理一致): schema line 452 ambitious_outlet 改为 "list \| str"; §B.1 ambitious_outlet 改为 [RFS, JFE]. P2/P3/P4 现有 single ambitious 保持 str 形式 |
| v2.51 | 2026-05-17 | Claude Opus 4.7 | Round 76 self-audit fixes (1 MINOR). R76-m01: §3.1 P4 backup 列 "JFE / JF" 把 §B.4 ambitious_outlet JF 错误列入 backup 列 — JF 在 §B.4 是 ambitious_outlet ("顶配", §3.2 P4 v2 ambitious), 不是 backup. R50-M01 时漏 fan-out P4. Fix: §3.1 P4 backup 改为 "JFE (per §B.4 backup_outlet)" 单 outlet; JF 仍在 §3.2 P4 ambitious 表达 |
| v2.52 | 2026-05-17 | Claude Opus 4.7 | Round 77 self-audit fixes (1 MINOR). R77-m01: §6 G-1 row 关键指标 column 缺 "Pipeline scale test 跑通", 与 §5.1.4 G-1 row 4 不对账; §6 fail-consequence column 含 "scale test 失稳: C3" 但 关键指标 column 无对应 entry — table asymmetric. Fix: §6 G-1 关键指标 column 增 "Pipeline scale test 1% 样本完整跑通 21→46 stage (R77-m01 同步 §5.1.4 row 4, 对应 C3 fail-consequence trigger)" |
| v2.53 | 2026-05-17 | Claude Opus 4.7 | Round 78 self-audit fixes (1 MINOR). R78-m01: §5.2.4 G0 acceptance 表 5 rows 缺 "LLM cost cap = $4,200 锁定" 检查项, 与 §6 G0 row 含 LLM cost cap 不对账. R19-m01 (plan v2.18→v2.19) 添加该 item 仅 fan-out 到 §6 G0 row, 未 propagate 到 §5.2.4 G0 subsection. Fix: §5.2.4 G0 表加新 row "LLM cost cap | $4,200 锁定 per §10.1 + §8 R10 (R78-m01 fan-out)" |
| v2.54 | 2026-05-17 | Claude Opus 4.7 | Round 79 self-audit fixes (1 MINOR). R79-m01: §6 G-1 fail-consequence column 6 triggers (C1-a/c/b + C2/C3/C4) 全是 C-fallback, 缺 "法律合规失败 → 暂停 M0" trigger, 与 §5.1.4 G-1 row 6 fail-consequence "暂停 M0, 先解决合规" 不对账; §6 G-1 关键指标 column 含 "法律合规" 但 fail-consequence column 无对应 entry. Fix: §6 G-1 fail-consequence column 增 "; 法律合规失败: 暂停 M0 直至 cleared (R79-m01 同步 §5.1.4 row 6)" 作为第 7 trigger |
| v2.55 | 2026-05-17 | Claude Opus 4.7 | Round 80 self-audit fixes (1 MINOR). R80-m01: §14 RACI matrix M-1 行 Consulted 列缺 D2 (G-1 fail 后 C-fallback 选择 conditional trigger), 与 §9 D2 trigger "M-1 完" 不对账. R73-m02 补 D6 时遗漏 D2; §14 已含 D3/D4/D5/D6 conditional triggers, 仅 D2 缺. Fix: §14 M-1 Consulted 增 "+ D2 G-1 失败后 C-fallback 选择 per §9: conditional trigger 仅 G-1 fail 时, 用户 + Claude 共同决策; R80-m01" |
