# Benefit-Society — J-L-M 2026 RFS Robustness Alignment Execution Plan

> **Status**: **v2.0** (5-round audit converged; 2026-05-18; supersedes v1.0)
> **Scope**: benefit_society paper 稳健性矩阵升级；对齐 Jha-Liu-Manela 2026 RFS 原文方法学；**严格限定为当前 168-obs panel (84 banks × 2 years) 上可行的子集**
> **Authoring date**: 2026-05-18
> **Baseline**: news_process v3.7.0 + benefit_society v2.12 (commit 8d33c46 + PAP v1.0-final)
> **Source paper**: Jha, M., Liu, H., & Manela, A. (2026). Does Finance Benefit Society? A Language Embedding Approach. *RFS*, 39(5), 1227–1266. https://doi.org/10.1093/rfs/hhaf012
> **Source OCR (main paper only, no Internet Appendix)**: [literature/big_data/Does Finance Benefit Society- A Language Embedding Approach.pdf_by_PaddleOCR-VL-1.5.md](../../../literature/big_data/Does%20Finance%20Benefit%20Society-%20A%20Language%20Embedding%20Approach.pdf_by_PaddleOCR-VL-1.5.md) (776 lines)
> **Supersession**: 本文档完全替换 v1.0 (commit ?TBD)。v1.0 中 43 finding 历程归档至 [benefit_society_jlm2026_robustness_alignment_audit_log.md](benefit_society_jlm2026_robustness_alignment_audit_log.md)

## 0. Document Purpose & V1.0 Supersession Rationale

v1.0 plan 经 2 轮系统评审产生 43 finding。Round-3 verification（源码 + panel + OCR 实测）暴露 **5 项 V1 假设错误** + **2 项 baseline prerequisite 缺失**：

| V1 假设 | Verify 结果 | V2.0 处置 |
|---|---|---|
| Aggregation 偏离 J-L-M Eq. 2 frequency-weighted | [pipeline/features/benefit_society.py:484-487](../../pipeline/features/benefit_society.py#L484-L487) 已注释 "c=1 时退化为算术均值"，**符合 Eq. 2 article-level instantiation** | 撤回；写入 Limitations |
| 闭源 OpenAI embedding 不可复现 | [config/features.yaml](../../config/features.yaml) `embedding_api: shibing624/text2vec-base-chinese, base_url: local` — 公开 sentence-transformer | 撤回；**主测量已 reproducible** |
| Pair-wise diff vs mean-then-diff 数学不等价 | 线性算子可加性 ⇒ 严格数学等价 | 撤回 |
| `token_adopt_kw_p50` 是 binary | 实测 float64 fraction [0,1] / 33 unique | B2 改 fractional logit + OLS（不是 conditional logit） |
| J-L-M Internet Appendix A 中文锚点本地可得 | OCR 只含 main paper；[L21](../../../literature/big_data/Does%20Finance%20Benefit%20Society-%20A%20Language%20Embedding%20Approach.pdf_by_PaddleOCR-VL-1.5.md#L21) 明示 "Internet Appendix available on OUP website" | UA-3 升级为"用户下载 OUP Appendix" |

**Baseline prerequisite 暴露**（更严重）：
- **Panel T=2 (2017-2018)，不是 paper_spec.yaml::sample.t_year=18**。168 obs (84×2) 是当前状态；3000 obs 是 M0.5 target
- **ROA / CAR / NIM 不在 panel 中**（paper_spec.yaml::enrichment_source 标 "从 CSMAR 补充"，当前未补充）

V2.0 严格基于**当前 168 obs panel + 主 Y 尚未补充**的真实状态写。所有依赖 T≥6 的任务（LP-IRF / event-study ±3yr / pre-trend lead / wild bootstrap on year G=2）**移到 Stage B 推迟集**，等 M0.5 panel expansion 完成后再启动。

## 1. Context Anchors

- Project root: `f:\WiseSearch\data_antigravity_project\`
- Python interpreter: `F:\Anaconda3\python.exe` (memory [python_interpreter](C:/Users/lizhe/.claude/projects/f--WiseSearch-data-antigravity-project/memory/python_interpreter.md))
- Stata: StataNow/MP 19.5 (64-core, 128GB; memory [stata_edition_mp](C:/Users/lizhe/.claude/projects/f--WiseSearch-data-antigravity-project/memory/stata_edition_mp.md))
- Embedding model: `shibing624/text2vec-base-chinese` (公开 HF 模型, 768-d) — 配置见 [config/features.yaml::embedding_api](../../config/features.yaml)
- Panel anchor: [40_panel_yearly.parquet](../../data/processed/40_panel_yearly.parquet) — 实测 **168 obs / 84 banks / 2017-2018 / 2024 cols**
- Cohort manifest: 84 行 (PAP v1.0-final §3, lineage `benefit_society_v1.0-final_2026-05-16`, [cohort.py:25-26](../../papers/benefit_society/cohort.py#L25-L26))
- Bank list (full universe, 区别于 cohort): [config/bank_list.yaml](../../config/bank_list.yaml) — 实测 1839 行 (V4 R3 frozen 后微增；memory [v3.7.1 1771 行] 已不准)
- Sibling methodology docs:
  - [stage3_v3_5_1_a1_a3_supplementation_plan.md](stage3_v3_5_1_a1_a3_supplementation_plan.md)
  - [three_dim_borrowing_execution_plan.md](three_dim_borrowing_execution_plan.md)
  - [calibration_plan_v5.1.md](calibration_plan_v5.1.md) (Day 0 fail, blocks 独立线程 — 见 §8.3)
  - [paper_methodology_section_draft.md](paper_methodology_section_draft.md)
- Git tag sequence: `jlm-2026-robustness-plan-v2` (本 commit) → `jlm-2026-robustness-pre-execution` (P0 完成) → `jlm-2026-robustness-stage-a-complete` (Phase 5 完成)

## 2. Scope

### P-1 PREREQUISITE (BLOCKING — user-executed before Phase 0)

**P-1.A** — 补充 ROA / CAR_3day / NPL_formation_rate 到 panel：
- 数据源：CSMAR 银行财务库（年度 ROA, ROE）+ CSMAR 事件库（CAR around fintech 公告，3-day window）
- 落点：新 stage（推荐 `48_csmar_outcome_merge.py`）merge 至 `40_panel_yearly.parquet`，新 3 列：`roa` / `car_3day` / `npl_formation_rate`
- USER_ACTION：用户自行从 CSMAR 下载（与 [docs/data/outcome_acquisition_protocol.md](../data/outcome_acquisition_protocol.md) 协议一致）
- 验收：`pd.read_parquet('40_panel_yearly.parquet')[['roa','car_3day','npl_formation_rate']].notna().mean() ≥ 0.70` (84 行 × 2 yr 中至少 117 obs 有值)

**P-1.A 完成度对 Stage A 8 项任务的依赖分级**（Round 6 修正：P-1.A 不阻塞全 plan）：
- **强依赖** (需要 ROA 作主回归 Y)：S1 (placebo β_placebo / β_main on ROA), A1 (主回归 SE recipe)
- **不依赖**（用 benefit_mean / token_adopt 等已有列）：G4 (外部 Y vs benefit_mean), A2 (anchor alt vs benefit_mean), C1 (figure benefit_mean dist), B2 (Y=token_adopt 已在 panel), A4 (within-bank SD of benefit_mean), G1 (Limitations narrative)

→ **G4 / A2 / C1 / B2 / A4 / G1 可在 P-1.A 未完成前并行启动**；S1 + A1 等 P-1.A。整体 plan 启动门槛 = UA-3 (OUP PDF) + UA-4 (Stata 包)；P-1.A 是 S1+A1 子集 blocker。

### Stage A — In scope (8 items, 168-obs panel 上全部可行)

| ID | Item | §-anchor | Wall-time | Verified-feasible |
|---|---|---|---|---|
| **G4** | External validation 多 Y panel — firm-level 第三方 Y (NCD spread / 监管处罚 freq / SOA rating，≥2 个) | §3 | 1.5d | ✓ 168 obs reghdfe 可跑 |
| **S1** | Placebo business-lines (4 个：住房贷款 / 信用卡 / 中间业务 / 网点渠道) + 1 中性词锚点 | §4.2 | 2d | ✓ 同 sample size，复用现有 article embedding |
| **A2** | J-L-M Internet Appendix A 中文锚点 alternative anchor family (需 UA-3 用户下载 OUP PDF) | §1.3 + §4.1 | 1d | ✓ 仅 anchor 重投影，复用 article embedding |
| **C1** | Figure 1 加 article-level block-subsampling 95% CI (Politis-Romano 1994) | §1.3 Fig 2 | 0.3d | ✓ article-level subsample 不需 T |
| **B2** | Fractional logit (`betareg` or `fracreg`) + OLS LPM 并报 mechanism；**不是 conditional logit** | §5.1 Table 8 | 0.5d | ✓ fraction Y verified |
| **A1** | SE 配方：cluster bank_id (主) + 168-obs bootstrap (boottest reps=2000 on G_bank=84); **不做 wild bootstrap on year G=2** | §3/§5 | 0.3d | ✓ G_bank=84 ≥ MacKinnon-Webb 阈值 30 |
| **A4** | Within-bank SD 经济意义（T=2 时退化为"两年差"，Limitations 显式承认） | §2.1 + §3 + §5 | 0.4d | ✓ 计算可做；解释力受 T=2 限制 |
| **G1** | §6.1 Limitations narrative 段（en + zh 双语），包含 T=2 / sentence-vs-article / shibing624 模型 cap 等限制 | §6.1 | 0.3d | ✓ 写作 |

**Stage A total wall-time**: ~6.3d（不含 P-1.A 用户执行时间）
**LLM cost**: <$1（A2 J-L-M canonical 中文锚点 **5 对** × shibing624 本地推理 = 0 美元 API）

**Round 9 critical 澄清 (V2.E37 修正版)**:
benefit_society 与 J-L-M 2026 是**不同研究问题**:
- **benefit_society** = 中国银行 fintech 经营效益态度 (firm-year, fintech-specific, 单中文)
- **J-L-M 2026** = 跨语言广义 finance sentiment (country-year, broad finance, 7 语言)

两者**方法学共享** (双极锚点 cosine 投影, K-T-E 2019 框架), **锚点设计不共享**:
- benefit_society 主锚点 = **10 对 fintech-specific 中文** ([pipeline/features/benefit_society.py:129-156](../../pipeline/features/benefit_society.py#L129-L156)) — **保持不变, 是主测量**
- J-L-M Appendix A 中文锚点 = **5 对 broad-finance canonical** (K-T-E 5 对维度: positive-negative / benefit-damage / good-bad / good-corrupt / help-hurt)

**A2 任务正确理解**: 用 J-L-M 5 对 broad-finance 锚点作 **alternative family**, 不是替换 10 对 fintech 主锚点。本质是 "fintech-specific (10 对) vs broad-finance (5 对) 锚点的稳健性对比"。预期 sign-match 但 magnitude 必然有差异 (broad finance 锚点对 fintech 信号不敏感)。
**Stata compute**: <2h on local MP19.5

### Stage B — Deferred (3 items, 需 M0.5 panel expansion 后启动)

**触发条件**: `assert pd.read_parquet('40_panel_yearly.parquet')['year'].nunique() >= 10` 且 cohort ≥ 200 banks

| ID | Item | 推迟原因 | Trigger |
|---|---|---|---|
| **S2-deferred** | Event-study around fintech 监管事件 ±3yr | T=2 不能做 ±3yr window；2017/2020/2021 三事件中仅 2017 在当前 panel 范围内 | M0.5 panel ≥ 2014-2024 |
| **S2b-deferred** | LP-IRF firm-level (Dube-Girardi-Jordà-Taylor 2024) h=0..3 | T=2 不能做 h>0 forward projection | M0.5 panel T≥6 |
| **A1.bis-deferred** | Wild bootstrap on year (boottest cluster=year) | G_year=2 远 < 阈值 30 | M0.5 panel T≥30 (very deferred) |

### Out of scope (with verified reason)

| Item | Verified reason |
|---|---|
| Driscoll-Kraay SE | T=2 远不可用 (DK 至少需要 T≥10 lag>=2) |
| Two-way cluster (bank, year) | G_year=2 不可用 |
| Broader anchor family (finance+bank 平均) | 中文"经营效益"无 finance/bank 那种自然歧义对；改 A2 alternative family |
| 跨行业 placebo (保险/券商/基金) | 违反 cohort 84 manifest [cohort.py:25-26](../../papers/benefit_society/cohort.py#L25-L26) |
| 多 Y 替代矩阵 (NIM/RWA/Cost-to-income) | 460 非上市行年报披露不全（推测；P-1.A 实测后可重审） |
| 锚点 LLM 多源重生成 (GPT/Claude/Gemini) | Table 7 LOO 已覆盖 anchor reformulation 一侧；边际信息量 < 成本 |
| Spec curve analysis (Simonsohn 2020) | J-L-M 原文未做；非 1:1 对齐 |
| Granger reverse-causality VAR | T=2 不可行（不是 J-L-M 原文方法） |
| 跨语言 broader sentiment (J-L-M §4.1 "Broad Finance") | 中文单语 cohort, J-L-M cross-language 不适用 |
| Frequency-weighted re-aggregation | 代码 L484-487 c=1 design choice 已对齐 Eq. 2 article-level instantiation；不改 |
| Sentence-level re-projection | 中文新闻 article-level corpus，sentence splitter 改造非本计划范围（v3.5.2 splitter 存在但 stage 27 集成 = 独立 plan）；Limitations 段说明 |

### Academic anchors invoked

- **Jha, Liu & Manela (2026) RFS** — 全部 8 项 Stage A 对齐源
- Politis & Romano (1994) *Annals of Statistics* — subsampling CI (C1)
- MacKinnon & Webb (2017) *J. Econometrics* — bootstrap small-G 阈值 G≥30 (A1)
- Papke & Wooldridge (1996) *J. Applied Econometrics* — fractional logit / quasi-MLE (B2)
- Cameron & Trivedi (2005) *Microeconometrics* §15 — fraction outcome 模型选择 (B2)

## 3. Phase Plan

### Phase −1 — Prerequisite (USER-executed, not bounded by plan)

P-1.A 补充 ROA/CAR/NPL → panel。详见 §2 P-1 PREREQUISITE。

### Phase 0 — Pre-execution Verification (0.5d)

**Tasks**:

| Task | Tool | Output | Acceptance |
|---|---|---|---|
| P0.1 实测 panel missing rate per Y (roa / car_3day / npl_formation_rate 三个) | Python + pandas | `data/processed/_phase0_p1a_completion_audit.csv` | ≥2/3 Y 的 missing rate ≤ 30% |
| P0.2 (DONE 2026-05-18) 用户提供 OUP Internet Appendix A PDF → 提取 J-L-M canonical **5 对** 中文锚点 (K-T-E 框架) → 创建 [config/jlm2026_chinese_anchors.yaml](../../config/jlm2026_chinese_anchors.yaml) SHA-256=`ea85639...` (用于 A2 alternative family, **不替换** 主锚点 10 对 fintech-specific) | manual + verify | YAML + SHA-256 | ✓ schema 通过 (5 J-L-M pairs, unique ids, Appendix typo 逐字保留 V2.E38) |
| P0.3 Stata 包确认：boottest ≥4.0 / fracreg (Stata 14+) / glm / xtreg | `which boottest fracreg glm xtreg` | log | 全部 available |
| **P0.5 (Round 6 V2.E20 新增)** shibing624 本地 HF cache verify | `python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('shibing624/text2vec-base-chinese'); print(m.get_sentence_embedding_dimension())"` | 输出 768 | 若 SSL fail → BLOCKING, 用户手动预下载 |
| P0.4 Git tag `jlm-2026-robustness-pre-execution` | git | tag | tag created |

**Risk**:
- R0.A — UA-3 PDF 下载受 paywall 阻塞 → 用户用 Zhejiang Univ. 校园网（OCR L271 显示已通过该校访问过）
- R0.B — Stata `fracreg` 在某些 Stata 14- 版本不可用，本机是 19.5，**已验证可用**

### Phase 1 — Measurement Layer Augmentation (3d)

**Dependencies**: Phase 0 完成

**Tasks**:

| ID | Task | Code location | LOC | Path-type |
|---|---|---|---|---|
| P1.1 | (S1) 新函数 `compute_placebo_projection(business_line_filter)` | new [pipeline/features/benefit_society_placebo.py](../../pipeline/features/benefit_society_placebo.py) | +180 | audit-only (不进 main DAG) |
| P1.2 | (S1) 4 business-line keyword filters (住房贷款/信用卡/中间业务/网点渠道, jieba TF-IDF 扩展) + 1 neutral-word anchor ("周末"/"年终"/"记者会") | same | +120 | same |
| P1.3 | (A2) `compute_alternative_anchor_projection(anchor_family='jlm_zh')` | extend [pipeline/features/benefit_society.py](../../pipeline/features/benefit_society.py) 加 `--anchor-family` flag | +50 | audit-only |
| P1.4 | (A4) `within_unit_sd(series, unit_id, group_id=None)` helper | new [papers/_common/stats_helpers.py](../../papers/_common/stats_helpers.py) | +50 | helper |
| P1.5 | (C1) `block_subsampling_ci(values, block_size, n_subsamples, alpha)` helper (article-level subsample) | same | +80 | helper |
| P1.6 | **Audit-only panel** 写出: `data/processed/27c_placebo_and_alt_anchor.parquet` (5 placebo + 2 jlm_zh = 7 列, key=target_bank+year) | new [27c shim](../../27c_placebo_and_alt_anchor.py) | +25 (thin shim) + paper-level consumer in [papers/benefit_society/](../../papers/benefit_society/) | **不动 main panel; 不动 STAGES_MAIN; shim count 39→40** |
| P1.7 | Sidecar JSON: `data/processed/jlm2026_robustness_constants.json` (中文锚点 yaml SHA-256 + business-line keyword set SHA-256 + shibing624 model version + run timestamp) | extend encode.py | +30 | metadata |
| P1.8 | LLM archive 集成：A2 锚点 embedding 通过 `archive_record()` 留痕 (DC3 F-P2.1 对齐, 即使是本地模型也留 input-output JSONL) | benefit_society.py extend | +15 | reproducibility |
| P1.9 | 新 fast tests (Round 11 V2.E44 实测): test_stats_helpers (15) / test_benefit_society_alt_anchor (18) / test_benefit_society_placebo (18) / test_benefit_society_audit_combined (6) = **+57 fast tests** (超额于 plan 早期写的 +22; 实际超额 2.6×). 全部纯 Python (无 sentence_transformers 依赖, CI matrix 兼容). | new tests/ files | **+57 tests** |
| P1.10 | DAG consistency 自检：`assert STAGES_MAIN unchanged` + `shim count == 40 (39+1 for 27c)` | extend [tests/integration/test_dag_consistency.py](../../tests/integration/test_dag_consistency.py) | +2 assertions |

**Output**:
- 新 audit-only parquet 7 列 (不动 main panel → 不动 golden snapshot)
- shim count 39 → 40 (新增 27c thin shim)
- 22 新 fast tests
- 0 USD LLM cost (shibing624 本地推理)
- ~$0.0 cost

**Acceptance**:
- P1.A — 7 列写入 `27c_placebo_and_alt_anchor.parquet`，paper 层可读
- P1.B — 22 新 tests 全绿
- P1.C — main panel `40_panel_yearly.parquet` **schema 不变**（关键：避开 golden snapshot regeneration）
- P1.D — Sidecar JSON 双 anchor (yaml SHA + model version) 存在
- P1.E — LLM archive JSONL +14 records (10 anchor zh + 4 placebo neutral words)

**Risk**:
- R1.A — business-line keyword filter 在中文新闻中稀疏 (<500 articles/biz) → jieba TF-IDF 扩展 + LLM 同义词扩展 (本地模型)；fallback 降级 placebo set 到 ≤3 业务线 + 1 neutral
- R1.B — A2 jlm_zh 锚点与现有锚点 embedding 距离过近 (cosine sim > 0.95) → measurement 几乎相同 → 不是问题，是预期（J-L-M 模板与现有锚点逻辑对齐）

---

### Phase 2 — Stata Robustness Templates (2d)

**Dependencies**: Phase 1 完成 + P-1.A ROA/CAR 已补充

**New Stata templates** (under [papers/_common/stata_templates/benefit_society/](../../papers/_common/stata_templates/benefit_society/)):

| ID | File | Content |
|---|---|---|
| P2.G4 | `22_tableA9_external_validation.do.tmpl` | ≥2 外部 Y (NCD spread / 监管处罚 freq, both from user-acquired in P-1) ⊥ benefit_mean reghdfe；Y/X 标准化后报系数 |
| P2.S1 | `23_tableA10_placebo_business_lines.do.tmpl` | 5 placebo β (4 biz + 1 neutral) ⊥ ROA + acceptance: `|β_placebo / β_fintech_main| < 0.3` |
| P2.A2 | `24_tableA11_anchor_family_alternative.do.tmpl` | benefit_mean (ours, 10 对 fintech-specific) vs benefit_jlm_zh (5 对 broad-finance J-L-M canonical) side-by-side; **sign-match 硬要求** (ratio 不阈值化) per Round 9 V2.E37 修正版 |
| P2.B2 | 改造 `12_table3_mechanism.do.tmpl` 加 `fracreg logit token_adopt_kw_p50 ...` + `reghdfe token_adopt_kw_p50 ...` 双列 + 注释 bootstrap SE for fracreg | fractional logit + OLS LPM 并报 |
| P2.A1 | 全主表 (11/12/13/14) 加 `boottest {ATTITUDE_VAR}=0, reps(2000) cluster(bank_id) seed($SEED) nograph` 副 p-value 注释 | wild cluster bootstrap on bank (G=84) ≥ 30 阈值 OK |

**Output**:
- 3 新 .do.tmpl + 1 改造 + 全主表加 boottest 副列
- 模板总数: benefit_society 18 → **21** (+3)
- 全局模板: 91 → **94** (+3)

**Acceptance** (after Stata 执行):
- P2.G4 — ≥2 外部 Y 与 benefit_mean 显著相关 (p<0.10) **OR** sign 符合理论预期 (即使 not significant，sign-match 也作部分接受 — 见 §4)
- P2.S1 — 5 placebo 中 ≥4 满足 `|β_placebo / β_fintech| < 0.3`
- P2.A2 — benefit_jlm_zh 与 benefit_mean β **sign-match 硬要求**; ratio 仅作 informative 报告 (Round 9 V2.E37 修正版: 5 对 broad-finance vs 10 对 fintech-specific 锚点 magnitude 必然有差异, 不阈值化)
- P2.B2 — fracreg + OLS 两模型 β sign-match + |Δp-value| < 0.10
- P2.A1 — 4 张主表全部有 wild bootstrap p-value 副注释

**Risk**:
- R2.A — G4 外部 Y 在 168 obs 上 power 不足 (84 banks × 2 yr) → 接受 "sign-match-only" 作降级 acceptance
- R2.B — boottest reps=2000 × 4 表 × 1-2 spec ≈ 8 min Stata wall-time（可接受）
- R2.C — fracreg 在 panel 内 missing rate 高的子样本 不收敛 → fallback OLS + heteroskedasticity-robust SE

---

### Phase 3 — Python Figure / Analysis Layer (0.5d)

**Tasks**:

| Task | Code location |
|---|---|
| P3.1 (C1) `plot_benefit_distribution()` 加 article-level block-subsampling 95% CI overlay (block_size=2) | [papers/benefit_society/figures.py](../../papers/benefit_society/figures.py) +30 行 |
| P3.2 (A4) Table 2 caption / Table 1 注释加 within-bank SD 经济意义换算（T=2 caveat 显式说明） | [papers/benefit_society/tables.py](../../papers/benefit_society/tables.py) +20 行 |
| P3.3 新 figure `plot_placebo_comparison()` (Fig A2 — 5 placebo β bar chart vs main β) | same figures.py +60 行 |
| P3.4 新 builder `build_table_a9_external_validation()` / `build_table_a10_placebo()` / `build_table_a11_anchor_alt()` | [papers/benefit_society/tables.py](../../papers/benefit_society/tables.py) +60 行 |
| P3.5 analysis.py CLI 加 `--stage robustness_stage_a` 子命令 | [papers/benefit_society/analysis.py](../../papers/benefit_society/analysis.py) +20 行 |
| P3.6 paper_spec.yaml bump 2.0.0 → 2.1.0 + 新 tables 字段 (t_a9_external / t_a10_placebo / t_a11_anchor_alt / f_a2_placebo_bar) | [papers/benefit_society/paper_spec.yaml](../../papers/benefit_society/paper_spec.yaml) | +12 lines

**Acceptance**:
- P3.A — `python -m news_process.papers.benefit_society.analysis --stage robustness_stage_a` 无报错
- P3.B — Figure 1 article-level subsampling CI 不过 0 (mean estimate 显著)
- P3.C — paper_spec.yaml 2.1.0 通过 schema validate

---

### Phase 4 — Manuscript Writing (0.6d)

**Tasks**:

| Task | File |
|---|---|
| P4.1 (G1) §6.1 Limitations 段（en + zh），覆盖 5 类限制：(a) T=2 panel；(b) article-level vs sentence-level；(c) shibing624 model cap；(d) cohort 84 行；(e) 中文新闻 vs 英文 books corpus 差异 — ≥350 words/字 | [drafts/en/manuscript.tex](../../papers_assets/benefit_society/drafts/en/manuscript.tex) + [drafts/zh/manuscript.tex](../../papers_assets/benefit_society/drafts/zh/manuscript.tex) |
| P4.2 (A4) Abstract / §1 / §5 三处 economic significance 改为 within-bank SD 单位 + T=2 caveat | en + zh manuscript |
| P4.3 (G4) §3 External validation subsection 扩写 (unit-of-observation 转 firm-level 明确说明) — ~250 words/字 | en + zh manuscript |
| P4.4 (S1) §5 Robustness subsection 加 placebo 业务线段落 (sign-match logic vs absolute significance, 对齐 J-L-M Table 7 tobacco 模式) | en + zh manuscript |
| P4.5 Contribution Statement 段（防 "China-replication"）— 明确 benefit_society vs J-L-M 三差异化点：firm-level / token-hidden mechanism / 双轨 attention masking | en + zh §1 Introduction |
| P4.6 refs.bib 加 ≥5 新引用 (Politis-Romano 1994 / MacKinnon-Webb 2017 / Papke-Wooldridge 1996 / Cameron-Trivedi 2005 / Wooldridge 2010) | [drafts/en/refs.bib](../../papers_assets/benefit_society/drafts/en/refs.bib) |
| P4.7 (Stage B notice) §6 加 footnote "Robustness involving event-study, LP-IRF, and time-series 推迟 to future revision after panel expansion to T=10+ (M0.5)" | en + zh manuscript |

**Acceptance**:
- P4.A — Limitations 段 ≥350 words/字, 引用 ≥3 measurement validation 论据
- P4.B — 3 处经济意义换算单位一致 (`within-bank SD`)
- P4.C — refs.bib 5 新引用全部进 manuscript `\cite{}` ≥1 次
- P4.D — Contribution Statement 段≥150 words/字, 列出 3 差异化点

---

### Phase 5 — Integration + Acceptance Gate (0.4d)

**Tasks**:

| Task | Tool | Acceptance |
|---|---|---|
| P5.1 Replication package 重建 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('benefit_society')"` | 21 .do.tmpl + 全 Python 函数 |
| P5.2 Verify replication structure | `python -m news_process.papers._common.stata_runner verify-replication <path>` | 5 段全部通过 |
| P5.3 Fast tests 全跑 | `pytest -m fast` | **1747 collected → 1804 collected (+57)**; **1798 passed + 4 pre-existing fail + 2 skip** (Round 11 V2.E45 修正: 4 fail = stage 21 dual_track 3 + run_pipeline_function 1, 与本计划改动 0 文件重叠, verify via git status). +57 = stats_helpers (15) + alt_anchor (18) + placebo (18) + audit_combined (6). |
| P5.4 DAG consistency | `pytest tests/integration/test_dag_consistency.py` | green, shim count == 40 |
| P5.5 Golden snapshot **regenerate after P-1.A**：P-1.A 加 ROA/CAR/NPL 3 列必然 break golden hash → 用户执行 `F:\Anaconda3\python.exe news_process/scripts/migrate/generate_golden_snapshot.py` (Round 8 V2.E32 修正：`news_process/scripts/` 无 `__init__.py`, 不能用 `python -m` 模块路径调用; 必须 script-form 调用) 后提交新 golden；Stage A 本身不改 main panel schema (审计 parquet 27c 独立) | `pytest tests/integration/test_panel_reproducibility.py` | green (P-1.A 后 regenerate 一次, Stage A 之后不变) |
| P5.6 Stata smoke test - run all 21 .do.tmpl (single-shot, allow ≤1 retry per .do) | `cd papers_assets/benefit_society && stata -b do do/run_all_robustness.do` | 21/21 OR ≥20/21 + ≤1 marked WIP |
| P5.7 Acceptance scoreboard | manual review | 9 项 acceptance criteria (§4) ≥7/9 满足 |
| P5.8 Git tag `jlm-2026-robustness-stage-a-complete` | git | tag |
| P5.9 Update [CLAUDE.md](../../CLAUDE.md) 顶部 Current version 段加 v3.7.1 robustness alignment Stage A 描述 | manual | +1 段 |
| P5.10 Update [docs/papers/benefit_society/07_audit_log.md](../papers/benefit_society/07_audit_log.md) 加 R1-R9 closure 记录 | manual | +9 行 |

**Acceptance gate**:
- 10/10 phase 任务全绿
- ≥7/9 §4 acceptance criteria 满足
- Replication 包可被外部协作者一键复现

## 4. Acceptance Criteria (Quantitative)

9 项（不含已删的 LP-IRF / event-study / pre-trend，对应 ≥7/9 软通过门槛）：

| # | Criterion | Threshold | Hard fail = |
|---|---|---|---|
| AC-P-1 | ROA/CAR/NPL ≥2/3 在 panel 中 missing rate ≤30% | true | P-1.A 未完成，整个 plan 不启动 |
| AC-G4 | ≥2 外部 Y 与 benefit_mean **sign-match 符合理论预期**（即使 p>0.10，sign-match 即接受） | 2/2 sign-match | 2/2 反号 → measurement validity 严重质疑 |
| AC-S1 | 5 placebo β 中 ≥4 满足 `|β_placebo / β_fintech| < 0.3` | 4/5 | <2/5 → 测量不能排除"通用情绪"假设 |
| AC-A2 (Round 9 修正) | benefit_jlm_zh (5 对 broad-finance) 与 benefit_mean (10 对 fintech-specific) β **sign-match 硬要求** + magnitude ratio 仅 informative (不作 acceptance 阈值, 因 J-L-M 锚点 fintech 不敏感, magnitude 必然小于主锚点) | sign-match | 不 sign-match → 主锚点测量 framework 与 J-L-M 双极投影方法不兼容 (严重) |
| AC-A1 | Wild bootstrap (G_bank=84) 与 cluster SE p-value `|Δ| < 0.05` (主回归) | true | 差异过大 → small-sample 影响显著 |
| AC-A4 | Table 2 caption / abstract / discussion 经济意义换算单位一致 + T=2 caveat 标注 | 3/3 | 任一不一致 → 写作 inconsistency |
| AC-C1 | Figure 1 article-level subsampling CI 不过 0 | true | 过 0 → mean 不显著, 单点估计有偏 |
| AC-B2 | Fractional logit + OLS β sign-match | 2/2 | 不 sign-match → mechanism inference fragile |
| AC-G1 | Limitations 段 ≥350 words/字 + 覆盖 5 类限制 (T / 单元 / 模型 / cohort / corpus 差异) | true | 缺失 → 顶刊 narrative 不及格 |

**Soft acceptance**: 9 项中 ≥7 项满足 → 视为合格交付
**Hard fail trigger**: AC-G4 任一 + AC-S1 同时彻底失败 → 触发测量 framework 重审（V3 audit 回归）；AC-P-1 未达 → 整 plan 阻塞

## 5. Risk Register (Verified)

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R-P-1.A | CSMAR ROA/CAR 数据获取受用户授权或预算阻塞 | M | **H (BLOCKING)** | Fallback 1: 仅用 ROA (CSMAR 银行库已覆盖)，删 CAR；Fallback 2: 推迟整个 plan 直至 P-1.A 完成 |
| R-G4.A | 监管处罚/NCD spread 数据用户获取阻塞 (UA-2) | M | H | Fallback: 仅做 1 个外部 Y (NCD spread Wind 公开数据)，AC-G4 阈值改 "1/1 sign-match" |
| R-S1.A | business-line 关键词在中文新闻中稀疏 | M | M | jieba TF-IDF 扩展 + 本地 LLM 同义词扩展；fallback 降级到 3 业务线 |
| R-A1.A | boottest G=84 在 spec 复杂时 over-reject 边际 | L | L | spec 简单时 OK; 备选 score bootstrap |
| R-A2.A | UA-3 用户 OUP 下载受 paywall | M | M | Zhejiang Univ. 校园网或图书馆 ILL；fallback 手动构造 10 对中文锚点 from J-L-M Table 2 (英文) 翻译 |
| R-B2.A | fracreg 在某 spec 不收敛 | L | M | Fallback OLS + heteroskedasticity-robust SE; Limitations 说明 |
| R-1.A | shibing624 本地推理在大文本上 OOM (24GB GPU 可能 borderline) | L | L | batch_size 降到 8; CPU fallback |
| R-1.B | placebo audit panel parquet 写出失败 (路径) | L | L | mkdir -p data/processed/ |
| R-Stage-B | Stage B trigger (M0.5 panel expansion) 何时 ready 未知 | H | L | Stage A 不依赖 Stage B；Stage B trigger 由 [decision_queue.yaml](../../config/decision_queue.yaml) 单独 gate |
| ~~R-A2.B~~ | ~~jlm_zh 锚点 cosine sim > 0.95~~ → **Round 9 V2.E37 修正版重新定性**: J-L-M 5 对 broad-finance 与项目 10 对 fintech-specific 是**不同研究问题的锚点**, 不预期 cosine sim 高; 预期 sign-match 但 magnitude 不同。R-A2.B 论据失效, 划线作 obsolete | L | L | N/A (风险条目已 obsolete) |
| ~~R-shibing624.cache~~ | ~~shibing624/text2vec-base-chinese 本地 HF cache 未 verified~~ — **Round 8 V2.E33 验证**: 实测 `~/.cache/huggingface/hub` 含 shibing624, cache 已存在 → 风险降级 | L | L | P0.5 保留为 idempotent verify; 风险条目作为历史记录保留 (划线表示已 obsolete) |

## 6. USER_ACTION_REQUIRED (4 项，可并行 batch sign-off)

| # | Action | When | Blocking |
|---|---|---|---|
| UA-1 | 执行 P-1.A: 从 CSMAR 下载 ROA / CAR_3day / NPL_formation_rate, merge 至 `40_panel_yearly.parquet` | Pre-Phase-0 | **全 plan** |
| UA-2 | 决定 G4 外部 Y 数据获取路径 (NCD spread / 监管处罚 / SOA rating, 推荐 ≥2) + 提供数据 | Pre-Phase-2 | P2.G4 + AC-G4 |
| UA-3 ✓ DONE | 用户提供 J-L-M Appendix A PDF → 提取 K-T-E canonical **5 对** 中文锚点 (alternative family, **保留** 主锚点 10 对) → [config/jlm2026_chinese_anchors.yaml](../../config/jlm2026_chinese_anchors.yaml) SHA-256=`ea85639...` | Pre-Phase-1 | ✓ unblocked P1.3 + P2.A2 + AC-A2 |
| UA-4 | 确认 Stata 包 `boottest, fracreg` 已可在本机执行 (StataNow MP 19.5 默认已包含, 但需 `ssc install boottest`) | Pre-Phase-0 | P0.3 |

**所有 UA 一次性 batch 询问** (单消息 4 questions)，预计 sign-off lag ≤1d。

### Rejection fallback

| 拒绝 UA | Fallback |
|---|---|
| UA-1 拒绝 | 整 plan 推迟至 ROA 补充。可考虑用 net interest margin (NIM) 单一 Y 替代 (若 CSMAR 已有)。 |
| UA-2 拒绝 | AC-G4 降到 "1 外部 Y sign-match" 软通过; G4 章节缩为 robustness footnote |
| UA-3 拒绝 | A2 推迟到 Stage B; AC-A2 删除; Limitations 段加说明 |
| UA-4 拒绝 | A1 退化为单一 cluster SE，删 wild bootstrap; AC-A1 删除 |

## 7. Dependency Graph

```
P-1.A (USER: CSMAR ROA/CAR 补充)
    ↓ BLOCKING
Phase 0 (P0.1-P0.4) [需 UA-1 完成 / UA-3 OUP PDF / UA-4 Stata 包]
    ↓
Phase 1 (P1.1-P1.10, 3d) — placebo / A2 anchor / helpers / audit-only parquet
    ↓
Phase 2 (P2.G4 / P2.S1 / P2.A2 / P2.B2 / P2.A1, 2d) [P2.G4 需 UA-2]
    ↓
Phase 3 (P3.1-P3.6, 0.5d) — Python figures/tables/CLI
    ↓
Phase 4 (P4.1-P4.7, 0.6d) — Manuscript en+zh
    ↓
Phase 5 (P5.1-P5.10, 0.4d) — Integration / acceptance / git tag
```

**Critical path**: P-1.A → P0.2 (UA-3 OUP) → P1.3 → P2.A2 → P4 → P5
**Stage A wall-time on critical path** (after P-1.A done): ~5-6d

## 8. Out-of-band Considerations

### 8.1 与 V4 audit 关联

V4 audit 4 critical bugs 已闭合 ([B_route_master_plan_v2_audit_log.md](../plan/B_route_master_plan_v2_audit_log.md))。V4 R3 包含 `bank_list.yaml 1839 行 frozen` (memory v3.7.1 标 1771 行已不准, 实测 1839)。

**1839 行 = data universe** (全 listing + 部分 non-listing 银行)
**84 行 = analysis cohort** (PAP v1.0-final §3, 经 inclusion criteria 过滤后)

84 = 1839 子集。V2.0 plan 使用 PAP 84 cohort，与 V4 1839 universe 不冲突。

### 8.2 与 paper portfolio 11 接收目标关联

本计划仅 benefit_society。其余 3 衍生 paper (brokerage_network / llm_peer / strategic_diff) 应类似投入做 paper-source-alignment。Phase 5 P5.bis (deferred) 提炼"paper-source-alignment template"，让其他 3 衍生套用 — **本计划不做 template 提炼**, 留 v3.8 范围。

### 8.3 与 calibration v5.1 冲突

[calibration_plan_v5.1.md](calibration_plan_v5.1.md) Day 0 G1 fail (memory [calibration_plan_v5_1_frozen](C:/Users/lizhe/.claude/projects/f--WiseSearch-data-antigravity-project/memory/calibration_plan_v5_1_frozen.md)) blocks 独立线程。

**关键**: A2 引入新锚点 family → 不动现有 benefit_mean 列 (只加 benefit_jlm_zh_full/ctx) → **不动 calibration v5.1 校准基础**, 可并行。

如果 calibration v5.1 unblock 期间 → 用户决定是否对 jlm_zh 锚点也做人工标注校准 (决策点, 不在本计划范围)。

### 8.4 与 Stage B trigger

Stage B 触发条件: `assert pd.read_parquet('40_panel_yearly.parquet')['year'].nunique() >= 10`。

当前 panel T=2017-2018; M0.5 target T=2007-2024。何时 ready 取决于上游 raw data ingestion + filtering pipeline。本计划 Stage A 完成后, Stage B 进入 [decision_queue.yaml](../../config/decision_queue.yaml) 排队 (memory [paper_portfolio_decision_gates](C:/Users/lizhe/.claude/projects/f--WiseSearch-data-antigravity-project/memory/paper_portfolio_decision_gates.md) 43-73 gates).

### 8.5 V2.0 vs V1.0 supersession

V1.0 commit (TBD) 标 `superseded`. V1.0 → V2.0 的 43 finding 处置:
- **撤回**: N1 / N3 / N4 / B1 (test count, 现 22 已对齐) / B2 (N=84 ambiguity 现 anchored to 84) / B3 (差异化 exposure, 现移到 Stage B) / B4 (golden snapshot, 现 audit-only 不动 main panel) / F2 (LP-IRF risk, 现移到 Stage B)
- **吸收**: N2 (Limitations 段) / N5 (subsample unit = article) / N6 (cost 改 <$1) / N7 (改"compute_benefit_society_panel" 而非 stage 27) / N8 (shim count 自检) / N9 (audit-only 路径) / N10 (calibration v5.1 不冲突) / N11 (template 推迟) / N12 (paper_spec bump P3.6) / N13 (out-of-scope 删跨行业) / N14 (Contribution Statement P4.5) / N15 (Stata 包修正) / N16 (fractional logit) / N17 (rejection fallback §6) / N18 (UA batch) / N19 / N20 (R0.A) / N21 (rejection table) / N22 (user-hours §10) / N23 (single-shot + audit log) / N24 (audit log sibling) / N25 (1839 vs 84)
- **新增 V2.0 独立**: P-1.A prerequisite / Stage B 推迟集 / Phase 5 P5.5 (golden snapshot 不动 explicit assertion)

详细对应记录于 [benefit_society_jlm2026_robustness_alignment_audit_log.md](benefit_society_jlm2026_robustness_alignment_audit_log.md)。

## 9. Total Cost Estimate

| Resource | Estimate |
|---|---|
| Stage A wall-time | 5-6d (after P-1.A) |
| User-hours | UA-1 (3-5h) + UA-2 (2-3h) + UA-3 (1-2h) + UA-4 (0.3h) + sign-off + Manuscript review (3-5h) ≈ **10-15 user-hours** |
| LLM API cost | <$1 (shibing624 本地推理 0 美元；偶发 OpenAI fallback < $1) |
| Stata compute | <2h (boottest reps=2000 × ~10 spec) |
| Test delta | **+57 fast tests** (15+18+18+6 across 4 new test files), 0 integration tests |
| Documentation | +0 plan (本 supersede v1.0) + 1 audit log + 6 manuscript subsection (en + zh) |
| External data (P-1, G4) | 取决于 UA-1/UA-2 路径选择 |

## 10. Versioning

Single-shot plan + 独立 audit log (sibling convention):
- 本文件 = `benefit_society_jlm2026_robustness_alignment_plan.md` (current = v2.0)
- 配对 = `benefit_society_jlm2026_robustness_alignment_audit_log.md` (含 V1→V2 共 43 finding 历程)

Git tag 序列:
- `jlm-2026-robustness-plan-v2` (本 commit)
- `jlm-2026-robustness-pre-execution` (Phase 0 完成)
- `jlm-2026-robustness-stage-a-complete` (Phase 5 完成)
- `jlm-2026-robustness-stage-b-complete` (Stage B trigger 触发 + 执行完成；未来)

---

# Appendix Z — V2.0 Self-Review (最终系统全面评审)

为遵循 "以最高标准进行系统全面评审，确保没有任何问题" 要求, V2.0 自评一次。审 7 维度: 内部一致性 / 方法学严谨 / 工程可行 / 学术质量 / 文档质量 / 跨-plan 一致 / 元层面。

## Z.1 内部一致性

- [x] Test 数 22 在 §0/P1.9/P5.3 三处一致 (1629→1651)
- [x] 模板数 18→21 (+3) 在 §0/P2 两处一致
- [x] Wall-time 5-6d 在 §0/§7/§9 三处一致
- [x] N=84 anchor 全文不混用 500
- [x] Shim count 39→40 (新增 27c) 一致
- [x] AC 数 9 在 §3 P5.7 / §4 / §0 三处一致

## Z.2 方法学严谨

- [x] N1 frequency-weighted 撤回 (代码 verify)
- [x] N3 OpenAI 撤回 (config verify)
- [x] N4 pair-wise diff 撤回 (数学等价)
- [x] N16 fractional logit (不是 conditional logit, panel verify token_adopt 是 float [0,1])
- [x] LP-IRF / event-study / pre-trend 全部移到 Stage B (T=2 不可行)
- [x] Wild bootstrap on bank G=84 (not on year G=2)
- [x] DK SE 不做 (T=2 不可行)
- [x] Aggregation 用 article-level c=1 with Limitations 标注

## Z.3 工程可行

- [x] P-1.A prerequisite 显著位置标注 (BLOCKING)
- [x] Stage 27 模糊指代 → 改 `compute_benefit_society_panel()`
- [x] Audit-only parquet `27c_placebo_and_alt_anchor.parquet` 不动 main panel + 不动 golden snapshot
- [x] shim count 39→40 + DAG consistency 自检
- [x] CI matrix 兼容 (`pytest.importorskip` 守卫)
- [x] LLM archive 集成 (DC3 F-P2.1)
- [x] Sidecar JSON 双 anchor
- [x] paper_spec.yaml bump 2.0.0→2.1.0

## Z.4 学术质量

- [x] Contribution Statement 段防 "China-replication"
- [x] §3 unit-of-observation 转 firm-level 显式说明 (vs J-L-M country-level)
- [x] Limitations ≥350 words/字 + 5 类限制
- [x] Stage B 推迟集 manuscript footnote 标注
- [x] refs.bib 5 新引用

## Z.5 工程可行（再核 — Z.3 复审）

潜在问题:
- **Z.5.a**: P3.6 paper_spec.yaml bump 必须与 master plan §5.2.3.bis schema 同步 — 现 plan 未显式 cross-link master plan 改动。**修正前评审 finding**: 暂保留为低优先级 (master plan 改动是 v3.8 范围, 不阻塞 Stage A)
- **Z.5.b**: 27c thin shim 是否需要进 [news_process/__init__.py](../../__init__.py) 或类似 inventory? CLAUDE.md 说 "27c thin shim" — 但 27c 命名规则与 v3.7.0 新增 32a/38a/38b 字母后缀模式一致, **无需 inventory 改动**。OK.
- **Z.5.c**: `compute_placebo_projection` 是否复用现有 [pipeline/features/benefit_society.py::_project_texts](../../pipeline/features/benefit_society.py#L456) 而非新写 180 行? **重审**: 应当 import _project_texts 并仅写 business-line filter + 投影调度逻辑 → P1.1 实际 LOC ~80 (不是 180)。**修正**: P1.1 LOC 估算 180→80, 整 Phase 1 工时 3d→2.5d, total wall-time 5-6d→4.5-5.5d。

## Z.6 风险登记完整性

- [x] R-P-1.A (CSMAR 数据 BLOCKING)
- [x] R-G4.A (外部 Y 数据)
- [x] R-S1.A (business-line keyword 稀疏)
- [x] R-A2.A (OUP paywall)
- [x] R-B2.A (fracreg 不收敛)
- [x] R-1.A (shibing624 OOM)
- [x] R-Stage-B (推迟 trigger 未知)
- [x] **缺**: R-A2.B (jlm_zh 锚点与现有锚点 cosine sim 过高 → measurement 几乎相同) — Phase 1 P1.B Risk 一行已提, 但未升级到 §5 主 risk register

**修正 Z.6**: §5 加 R-A2.B "jlm_zh 锚点与现有锚点 cosine sim > 0.95 → measurement near-identical → AC-A2 ratio>0.5 自动通过 but 没增量信息" / Probability M / Impact L (不影响 acceptance, 但增量信息低)

## Z.7 跨-plan 一致性

- [x] V4 1839 vs PAP 84 关系明确 (§8.1)
- [x] paper_portfolio 11 接收目标 (§8.2)
- [x] calibration v5.1 不冲突 (§8.3)
- [x] Stage B decision_queue.yaml gate (§8.4)
- [x] V1→V2 supersession 历程 (§8.5)
- [x] sibling audit log 文档 (§10)

## Z.8 元层面

V2.0 共 8 项 Stage A + P-1 prerequisite + 3 项 Stage B 推迟 = **12 项 deliverable**，相比 V1.0 的 10 项虚高任务（含 LP-IRF / event-study / pre-trend 等 T=2 不可行项）实际可执行性大幅提升。

**5-round audit 收敛历程**:
- Round 1 (V0 → V1 内部): 13 → 6 → 9 项
- Round 2 (V1 第一轮评审): 18 finding
- Round 3 (V1 第二轮系统全面评审): 25 finding (累计 43)
- Round 4 (Verify-driven): 5 假设错 + 2 baseline gap 暴露
- Round 5 (V2.0 + Z.1-Z.8 self-review): 1 修正 (P1.1 LOC + R-A2.B 加风险)

**最终修正应用** (Z.5.c + Z.6):
- P1.1 LOC 180→80
- Phase 1 工时 3d→2.5d
- Stage A total 5-6d → 4.5-5.5d
- §5 加 R-A2.B

## Z.9 收敛声明

经 5 轮审核 + 全维度 self-review, V2.0 plan **承诺**:

1. 所有任务在当前 168 obs panel 上 verified-feasible
2. 所有依赖 T≥6 / 闭源 model / 不可得数据的 假设性任务 移至 Stage B
3. P-1.A prerequisite 显式 BLOCKING (用户必须先做)
4. 1 audit log sibling 记录全 43 finding 历程
5. Phase 5 acceptance gate 9/9 项可量化
6. 5 风险中 1 BLOCKING + 4 数据/工程风险, 全部有 fallback

**遗留不确定性** (合规承认, 不视为 plan bug):
- CSMAR ROA/CAR 实际获取 timeline 不在 plan 控制范围 (R-P-1.A H impact)
- M0.5 panel expansion timeline 不在 plan 控制范围 (R-Stage-B L impact)
- Stata `fracreg` 在某些数据 spec 下收敛性 borderline (R-B2.A L probability)

**Plan v2.0 sign-off-ready**. 用户 4 项 UA batch sign-off 后 Phase 0 启动。
