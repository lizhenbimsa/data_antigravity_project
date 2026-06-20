# 执行计划：非极性文本维度的「整合—提升—披露」全面落地（管道 + 论文 + golden）

> **v2.5 · 2026-06-20**（v2.4 经 plan↔execution 复核审计 GO 后**订正 2 处状态措辞夸大**：WS-F ✅→⏳部分(OVER-1..7 未做, 仅复用 3 锚点)、WS-A 标注"仅 2 新列"；并将本文档提交入库(原 untracked, 补 git 可追溯锚)。下方"执行状态"段为权威实况，正文以下为原始 roadmap 保留备查。）
> v2.4：v2.3 GO 后已全面执行 + 回填执行状态。
> v2.3 收敛轨迹：v1=NO-GO(3×P0/5×P1) → v2 → v2.1 → v2.2(8-agent GO) → v2.3(第 5 轮收敛 GO)。
> 范围决策（用户 2026-06-20）：**全面落地（管道 + 论文 + golden）**。

---

## 执行状态（2026-06-20 全面执行后回填，权威实况）

分支 `exec/nonpolarity-dims-2026-06-20`（6 commit，工作树干净，main pristine `8adb3111`，**未推送**）。
执行经多轮多智能体审计：WS-B1 执行审计 GO → 全执行审计(4-agent) GO → 完整性/跳过审计(3-agent) GO。

| WS | 状态 | commit / 证据 |
|---|---|---|
| WS-0 前置硬门 | ✅ DONE | `080ca711` 快照提交 25 个并行会话在途工作（用户授权）腾净树 |
| WS-B1 named_entity_ratio（三轨）| ✅ DONE | `83f764cd`；lexical_complexity 3 处编辑 + encode 三轨 agg + test 子集断言；golden 外科注入双 gate 0 失配 |
| WS-B2 boilerplate_phrase_ratio（单轨）| ✅ DONE | `0ef3c1aa`；新模块 + tone_words.main() post-proc + encode 单轨 agg；确定性+覆盖 gate |
| WS-A/C 标签 + core 列 | ✅ DONE（**仅 2 新列**）| 含于 `83f764cd`/`0ef3c1aa`：仅为 named_entity/boilerplate 2 新列加 Stata 标签+core_pattern。⚠ WS-A 正文所列**既有列**(`avg_specificity`/`lazy_*`/`coh`/`centroid_diff`/`avg_within_doc_redund`)的 base 标签缺口**未补**，由下方 "broader Stata labels ⛔ 跳过(by-design, `_apply_label_fallback` 100% 兜底)" 覆盖 |
| WS-E spec 注册 | ✅ DONE | `04b78d0c`（named_entity）+ `0ef3c1aa`（boilerplate）；3 个 alternative + 共线披露 |
| WS-F 引用治理 | ⏳ 部分（锚点复用；OVER-1..7 未做）| 2 新列所需 3 锚点 (Hope-Hu-Lu 2016 / Lang-Stice-Lawrence 2015 / Dyer-LSL 2017) **本就在** LITERATURE_ANCHORS（前序 `4e35aba9` 加，本批仅复用 + codebook/spec 引用一致）。⚠ WS-F 正文的 **OVER-1..7 测度对齐治理**（Arena-Julio/Buehlmaier-Whited/LM2013-IPO/Bodnaruk/Hwang-Kim 的测度对齐+动词降级）**未执行** → 属 manuscript 起草阶段（T=18-blocked），无既有 manuscript 故无落点 |
| WS-G golden 受控注入 | ✅ DONE | 累计 **+24 clean delta**（named_entity 18 + boilerplate 6），既有列 0 漂移 0 删除，数据二次重建确定 |
| WS-D 正交性证据 | ✅ DONE（替代实现）| `209bf7f2` 独立可复现诊断（bank-year Pearson/Spearman，validation-only/golden-safe）；**未改 39c 内核**（NMI 引擎喂连续列无效，计划已定 open-redesign）|
| be6c9e07 审计修正 | ✅ DONE | named_entity×specificity 实测 corr≈0.81（非别名）回填四处披露 |
| B3 text_novelty | ⛔ 跳过（审计 GO）| 实测 `corr(1−strat_sim_max, strat_sim_max)=−1.0` 完全共线；横截面/时序 novelty 已各有专列 → 加=冗余 variable-farm |
| staleness-merge | ⛔ 跳过（审计 GO）| `18_staleness_panel`(06-17) 早于 `21/24`(06-20) → runner mtime 守卫正确拦截；强行注入=lineage 违规；已是独立 golden record |
| broader Stata labels | ⛔ 跳过（审计 GO）| `_apply_label_fallback` 100% 兜底 + fail-loud 断言（实测 2787/2787 全有标签）→ by-design 非缺陷 |
| manuscript | ⏳ T=18-blocked | 无 drafts + T=2(172 行) + spec 的 8 个 outcome 在 panel 全 ABSENT（财务面板未获取）→ 无真回归可写 |

**测试**：repro 19p/1s、dag、lexical(含子集)、boilerplate(4) 全绿；ruff clean；3 个 `test_dual_track` _ss-NaN + 2 个 `papers_b_route` output-dir 失败为 **pre-existing**（独立坐实未混入）。
**生产 T=18 待办**（受 M0 / golden 受控重生门控）：财务数据接入 → outcome 列就位 → 全链重跑(含 fresh stage18 解 staleness) → golden 受控重生 → manuscript 起草。

---

## 审计返工说明（v1→v2 关键修正，必读）

v1 经多智能体审计判 **NO-GO**，本版修正以下硬错误（每条都已直读代码复证）：

| # | v1 缺陷 | 严重度 | v2 修正 |
|---|---|---|---|
| 1 | 重生链写 `22→24→45→46→51` 跳过 stage 23（且括号自相矛盾） | **P0** | 改 `22→23→24→45→46→51`；**首选外科注入法**绕开整链（见 WS-G） |
| 2 | 工作树已被并行会话改脏（golden 2342 行 diff、encode.py/export.py 均 `M`），by-name add 无法隔离同文件 hunk | **P0** | 新增 **WS-0 前置硬门**：先 reconcile 并行 golden + 干净 worktree 逐 hunk 提交 |
| 3 | B2 corpus-DF 落点含糊 + 语料前提错（stage 22 是 gated 847 行子集非全量）+ 聚合路径错配 encode_collab | **P0** | B2 落点冻结在 `tone_words.main()` 两遍；聚合走 encode.py H2（与 B1 同）；语料口径如实披露（见 WS-B2） |
| 4 | WS-A 称 export.py 缺 `_ss` 标签 | P1 | export.py:1255-1261 已自动派生 `_ss` → **删除该编辑**；真缺口在 `stata_export.py::HEURISTIC_LABELS` base 标签 |
| 5 | WS-B1 只列 KEYS+_empty，漏 return dict SSOT 与 test 相等断言 | P1 | 列全 **3 处编辑**（return dict 414-436 / KEYS 272 / _empty 242）+ 同步 `test_lexical_complexity.py:28,36` |
| 6 | WS-D「扩 DIMS list」纳连续列进 39c | P1 | 39c 是**纯 NMI-on-categoricals**（无 Pearson/无离散化）+ 读 article 级（grain 不匹配）→ **WS-D 降级为开放重设计项，移出第 1 波** |
| 7 | WS-E 称 paper_spec_schema 校验=spec 完整；strategic_diff 承载；manuscript $0 | P1 | schema 是 no-op；strategic_diff 计入 142 锁；manuscript 从零建**非 $0**（独立写作任务）；填既有 tA7/tA8 占位槽 |
| 8 | BLAS 列名缺 `bank_` 前缀；herd_decay 误称 CountVectorizer(4,6)；SAFE 误引静默先例；litigious 块行号错 | P2 | 全部订正（见各处） |

---

## WS-0　前置硬门（提交/重生安全，**必须最先满足**）

**实测工作树状态（`git status --porcelain`，2026-06-20）**：
- `tests/fixtures/golden_panel_v0.json` = `M`，**2342 行 diff（+1207/-1135）** ← 并行 `loughran-exc-cols` 会话注入 12 个 `exc_loughran` 列，**尚未提交**。
- `pipeline/panel/encode.py` = `M`、`pipeline/panel/export.py` = `M`、`pipeline/panel/attention_media.py` = `M` ← 并行 attention/loughran 会话。**实际脏文件 ~28 个**（含 6 个 `stata/*.do`、`v3_5_1_constants.json`、~10 个 test、4 个 config）→ **以提交时实时 `git status` 为准，全量逐 hunk，勿假定仅 3 文件**。（注：`stata_export.py` 当前实测**干净**，但若 WS-A 改它，仍须确认提交时状态。）

**铁门（不满足不得进入 WS-B/WS-G）**：
1. **golden 重生前必须先 reconcile 并行 golden**：等并行会话提交其 12 列，或合并其改动。否则 `generate_golden_snapshot.py` 会**覆盖**并行未提交改动；先 `git stash` 又丢本计划新列（同一 JSON 物理冲突）。
2. **提交走干净 worktree + 逐 hunk 重贴**：本计划要动的 `encode.py`/`export.py`（及 WS-A 的 `stata_export.py`）若提交时已被并行会话改脏，`git add <file>` 是**整文件粒度**，会把外来 hunk 一并 staged。必须基于 `origin/main` 建 detached worktree、逐 hunk `Edit` 重贴本计划改动后再 add（memory `iv-dualtrack-gaps-filled` / `geo-attention-volume-twin` 先例）。**by-name add 对已混改文件无效**。
3. 备份 `_regen_backup_<date>/`（golden + 受影响 parquet）。

---

## 0. 关键再定位 + 对前次「功能审计」的勘误

前次审计称 3 个「遗漏的正交维度」（相似度/变化、跨公司可比性、特异性/套话）。**直读 golden 证明它们大多已实现并落 `40_panel`**：

| 维度 | golden `40_panel` 实测 | 学术锚点（WebSearch 已核验） |
|---|---|---|
| 相似度/年度变化 | **已有**：`lazy_{jaccard,overlap,minedit}_{full,ctx,ss}`(9)、`coh_*`(15)；staleness 在 `18_staleness_panel`（**未并入 40**） | Cohen-Malloy-Nguyen 2020 JF；Brown-Tucker 2011 JAR |
| 跨公司可比性 | **已有**：`strat_diff_*`/`strat_sim_max*`/`centroid_diff_*`(共 ~47+15)、`bank_cogn_mean` | Hoberg-Phillips 2016 JPE；De Franco-Kothari-Verdi 2011 JAR |
| 特异性/套话 | **部分**：`avg_specificity`×3、`avg_within_doc_redund(_han)`×6、`mean_num_intensity`×6；**缺** `named_entity_ratio`、真·跨文档 `boilerplate_phrase_ratio` | Hope-Hu-Lu 2016 RAS；Dyer-Lang-Stice-Lawrence 2017 JAE；Lang-Stice-Lawrence 2015 JAE |

**勘误**：「这 3 个维度是项目遗漏」被推翻——它们大多已落盘。真实缺口 = **论文层接线 + 部分三轨标签缺口 + 缺正交性证据 + 2 个精化新列（`named_entity_ratio`/`boilerplate_phrase_ratio`）+ 测度对齐/披露**，而非从零建维度。

---

## 1. 目标 / 非目标

**目标**：(G1) 补 `named_entity_ratio` / `boilerplate_phrase_ratio` 两精化新列；(G2) 补 `stata_export.py` 三轨 base 标签真缺口；(G3) 把已有非极性测度提升进承载论文 + 披露；(G4) 测度对齐/引用治理（OVER-1..7）；(G5) golden 受控重生 + 测试；(G6, 独立重设计) 非极性维度正交性证据。

**非目标**：不重造已存在的 lazy/coh/strat/centroid/cogn/specificity/within_doc 列；不触付费 stage 21 / 不改 prompt v8 / 不删 `_llm_cache.db`；不新增 DAG 阶段（列内扩展，STAGES 计数不变，thin shim 冻结）；不在本机宣称生产结论（T=2 仅验管道）。

---

## 2. 现状真值盘点（已在 `40_panel`，无需重建）

LM 6 frac×3轨(18)、`frac_fls`×3、`mean_clarity_score`×3、`avg_specificity`×3、`avg_within_doc_redund(_han)`×6、`mean_num_intensity`×6、`lazy_*`×9、`coh_*`×15、`strat_*`/`centroid_diff_*`、`bank_cogn_mean`。
**真实缺口**：`named_entity_ratio`(0)、`boilerplate_phrase_ratio`(0)、`*staleness*` 不在 40_panel（仅 `18_staleness_panel`，118 行）。
**三轨实测注意**：`lazy_*`/`coh_*`/`centroid_diff_lda`/`strat_diff_t2v`/`strat_diff_n5`/`strat_sim_max`/`strat_fluidity` 有 `_ss`；**`strat_diff_n3/n4/n6/n7`（及 `_w`）无 `_ss`**（补标签须逐列核对，勿按列族通配，否则造孤儿标签）。

---

## 3. 工作流（WS-A … WS-H）

### WS-A　三轨 base 标签真缺口（$0，golden-safe）
- **删除** v1 对 `export.py:549-554/691-702` 的 `_ss` 编辑——`export.py:1255-1261` 已有 `for k ... if k.endswith('_ctx')` 机械循环**自动派生所有 `_ss` 标签**（实测）。
- **真缺口在 `stata_export.py::HEURISTIC_LABELS`**：`lazy_*`/`coh`(主，非 t2v)/`centroid_diff`(主)/`avg_specificity`/`avg_within_doc_redund` 等**无 base 标签**（落 column-name 兜底），且此处**无** `_ctx→_ss` 派生。补三轨 base 标签。
- **范围加宽**：`export.py:545-569` 显示 `tone_volatility`/`abnormal_tone`/`fintech_exposure`/各 `_z` 列也仅 full/ctx → 一并审计。
- **逐列实测**：补标签前读 golden `column_hashes` 确认该列存在 `_ss`，避免 `strat_diff_n3_ss` 等孤儿键。
- golden-safe（标签非列值；`.dta` 须跑 stage 46 才落）。验收：`stata_export._assert_track_triplet_unique`（:49）通过。

### WS-B　精化新列（golden-regen，$0 计算）
- **B1 `named_entity_ratio_{full,ctx,ss}`**（specificity 纯实体面）
  - **3 处编辑**（全改，缺一即 test 红）：`lexical_complexity.py` 的 ① return dict（**:414-436，真 SSOT**）② `LEXICAL_COMPLEXITY_KEYS`（:272）③ `_empty_result`（:242）。复用同一 `_get_pristine_posseg` pass（:365）+ `_ENTITY_FLAGS`（:113），`n_entity_only=Σ(nr/ns/nt/nz)`，`named_entity_ratio=n_entity_only/n_real`。
  - **同步测试契约**：`test_lexical_complexity.py:28,36` 断言 `set(r.keys())==_ALL_KEYS`，不同步 KEYS 立即红。
  - 三轨由 `tone_words.py:1566` 的 `LEXICAL_COMPLEXITY_KEYS` 提取循环**物化（必需，非自动）**。
  - 聚合：`encode.py` H2 块（在 `:537` 起的 `for track` 循环内，:599-619）加 `agg[f'avg_named_entity{track}']=(f'named_entity_ratio{track}','mean')`。
  - **共线披露**：`named_entity_ratio` 是 `specificity_index`（实体+硬数词）真子集分子 → 实测 article+bank-year corr；**若 corr>0.95，按 `within_doc_redund_han`（实测 0.99）先例降级为「specificity 对数字扰动的敏感性诊断列」**，不作第二独立构念，写进 codebook + 论文。
  - codebook：**显式 curate** `VariableMetadata`（citation=Hope-Hu-Lu 2016 RAS），勿依赖 `_infer_*` 空引用兜底。
- **B2 `boilerplate_phrase_ratio_full`（先单轨，ctx/ss 延后，by-design 披露，镜像 `semantic_staleness_ss` DEFER 先例）**
  - **落点冻结**：必须在 `tone_words.main()`（read `:1726` 之后、save `:1874` 之前）做**全 df 两遍**——`_dual_analyze` 是逐行 `df.apply`（:1477），不能做语料级统计。**这会二次改 stage 22 列宽 → 同样触发 golden 重生 + 同样必经 23→24**。
  - **语料口径如实披露（测度效度 caveat）**：stage 22 读 `21_tone_llms.parquet` 是 **gated 子集（盘上 847/全量 ~4024）**，非真全量。两选一并写进计划与 codebook：
    - **(A) 默认**：在 stage 22 内联两遍，套话集建在「12b 后 fintech gated 子集」上，**显式 caveat** 非 Lang-Stice-Lawrence 真全量；
    - **(B) 若要真全量**：在 stage 45 读 `12_fintech_news_full.parquet`（~4024 行，镜像 `attention_media.py:534/584`）算 DF + per-article ratio，再按 `(docid,target_bank)` join 回——**独立 merge 步骤，远重于 groupby**。
  - **聚合路径（修 v1 错配）**：B2 article 列随 23→24 pass-through 到 stage 45，**走 `encode.py` H2 块聚合（与 B1 同），不进 `encode_collab`**（后者只聚合 24_herd_decay 已有列，错配会静默缺列）。
  - **聚合域（ATT-1 铁律）**：per-bank-year mean 必须在 `24_herd_decay` verified 集上做（随列流入再聚合），**禁在 pre-21 全量集直接 groupby**（否则重演 attention 族 26.8% 假阳泄漏）。
  - **DF 实现**：只借鉴 `herd_decay.py:190-197` 的 `char_wb` 向量器**惯用法**（注意该处是 `TfidfVectorizer`、`ngram=(2,4)`，用途不同）；**B2 自建 `CountVectorizer(analyzer='char_wb', ngram_range=(4,6))`**（套话是「短语级」→ 刻意取更长的 4–6gram，区别于 herd_decay 的 2–4）取 document-frequency，**vocabulary 用 `sorted` 固定序**防 HASHSEED 漂移。
  - **聚合短名 ≤32**：`avg_boilerplate_full` 等（`avg_boilerplate_phrase_ratio_full`=33>32 会触截断/撞名）。
  - **SAFE**：套话集为空 → `nan` + **loud WARNING**（镜像 `FINTECH_AC=None`（cooccurrence_filter）的真 loud 先例，**勿引** `lm_non_sentiment.py:112` 静默返回空集）。
  - **本机 T=2 退化披露**：1125 篇/2 年下高频 char_wb 4-6gram 几乎全跨两年共现 → ratio 近饱和/近空，**本机只验管道不验功效**。
- **B3（可选）`text_novelty`**：零成本派生自 `strategic_diff.py:460-784` 相似度矩阵。phase-2。
- **B-staleness-merge（可选，独立 WS）**：`18_staleness_panel`（118 行）left-merge 进 `40_panel`（172 行）→ **54 行 NaN**（无覆盖，须披露）；`semantic_staleness` 仅 full/ctx（**无 `_ss`，引入三轨平价漏洞须 by-design 披露**）；须 `runner.py` 新增 `(target_bank,year)` merge 步 + golden 重生。否则论文直接读 `18_staleness_panel`。

### WS-C　提升已有轨（$0，golden-safe）
- LM 6 frac / clarity / num_intensity / specificity / within_doc 均已在 `40_panel`。
- **`assign_core_columns` 核心列清单真缺口**（`stata_export.py:558-590` 是逐列名字面 list、非 regex；已含 clarity/num_intensity/6 LM frac → **删除这些**）：仅补 `avg_specificity`/`avg_within_doc`/`avg_rare_word`/`avg_hard_char`/`avg_nominalization`/`avg_function_word`/`avg_adversative`/`lazy`/`coh`(主)/`strat_diff_n`/`centroid`(主)。
- 注：`HEURISTIC_LABELS` 缺这些列的 base 标签是 **by-design**（仅 curate 每部词典 6 个 headline tone 列，衍生列走泛型推断 + `export.py:1265-1269 _apply_label_fallback` 100% 覆盖 fail-loud）；WS-A 补 base 标签是**增强**非修 bug，且只动标签字典、**不触** `_assert_track_triplet_unique`（:671，作用于列名缩短非标签）。

### WS-D　正交性证据（**降级为开放重设计项，移出第 1 波**）
- **模块路径**：`pipeline/audit/construct_orthogonality.py`（**不在 validation/**）；`DIMS_FULL`（:90）仅 3 个**离散**创新构念。validation-only：写 `data/processed/39c_*.parquet`（在 `schemas.py:180 EXPECTED_NO_OUTPUT_STAGES`，**不并入 40_panel、不进 OUTPUT_REGISTRY** → golden-safe）。
- **不可行点（v1 严重低估）**：39c 全文 `pearson|spearman|qcut|discretiz` **零命中**，只用 `normalized_mutual_info_score`（:110/204）；连续浮点（`lazy/specificity/named_entity`）直接喂 NMI 统计无效。且输入是 `21_tone_llms.parquet`（**article 级**，:343/397），而目标列是 **bank-year panel 列** → grain 不匹配。
- **重设计要求**：① 给 39c 新增**连续变量分支**（Pearson/Spearman 相关矩阵，或 qcut 五分位离散化后再 NMI）；② 新增/切换**输入源**（读 `40_panel_yearly` 或 join `22_words_tone`）；③ 同步 `compute_nmi_matrix`/`compute_permutation_null`/`classify_orthogonality`/bootstrap + 维度计数测试。**这是新功能开发，非「加几个列名」。** 排在 WS-B/G 之后。

### WS-E　论文层接线（**manuscript 部分非 $0**）
- **现状澄清**：8 篇正式 manuscript 对 clarity/uncert/litig/modal/complexity/fls/Fog/readability/boilerplate **零命中**；`bank_news_clarity` spec **已深度登记 clarity**（`treatment.alternative:111-119`/`composite_pca:121-124`/`inference.families:230-238`/`tables:387-393` 留 tA7/tA8 占位槽 `19_bnc_clarity_main_robustness`/`19_bnc_num_intensity_complementary`）→ **不是「零接线」**；真缺口 = **manuscript**（`papers_assets/bank_news_clarity/drafts` 不存在）。
- **承载与计数锁**：`strategic_diff` 在 `papers/_common/stata_templates/strategic_diff/`（**计入 142**）→ 给它加模板会让 `test_papers_b_route.py:170 expected_count=142` 立即红。**新模板放 `bank_news_clarity`（provisional 子目录，零 142 锁影响）**；若必须放 `_common`，同步上调 `:170` + CLAUDE.md + `stata_runner` verify-CLI 计数（3-4 处联动）。
- **填占位槽 = 建文件（非改一行）+ build-replication 约束（P1，实施必守）**：`paper_spec.yaml:387-393` 虽引用 `19_bnc_clarity_main_robustness`/`19_bnc_num_intensity_complementary` 两槽，但对应 `.do.tmpl` 在 `papers/bank_news_clarity/stata_templates/` **尚不存在**——「填槽」实为**从零建模板文件**。且 `bank_news_clarity` 在 `_VALID_PAPER_IDS_BUILD` 但**不在 `_PAPER_DEFAULTS`**（`.get(paper_id,{})` 返回空 dict）→ `_substitute_placeholders`（:327-332）遇任何残留 `{{KEY}}` 即 fail-fast `raise`。**铁律**：新 `19_bnc_*.do.tmpl` **必须零新占位符**（镜像现有 8 个 sibling 模板：全硬编码变量名，仅用 `PROJECT_ROOT`），否则须先建 `_PAPER_DEFAULTS['bank_news_clarity']` 条目 + 在 `_KNOWN_PLACEHOLDERS_PAPER_SPECIFIC`(:179) 登记。**勿造新名**（用既有两槽名）。
- **验收门诚实化**：`paper_spec_schema.validate_paper_spec` 是历史死字段 **no-op**；`REQUIRED_FIELDS` 只查 12 顶层 key；`test_b_route_paper_assets_structure` 只覆盖 attention/substance/locus 3 篇 → **manuscript 无自动验收门**。计划**不得**用「schema/build-replication 通过」暗示 spec/manuscript 完整。
- **manuscript 起草 = 独立非-$0 写作任务**（走 `academic-paper` skill；从 `papers_assets/strategic_diff|benefit_society/drafts/{en,zh}` 拷 `.tex/.bib` 骨架；refs.bib 沿用共享 foundational 块 + append）。或把可比性维度路由到**已有 drafts 的 strategic_diff**（更现实）。

### WS-F　引用治理 + 测度对齐（$0，OVER-1..7）
- 这些引用（Arena-Julio/Buehlmaier-Whited/LM2013 IPO…）**全 refs.bib 零命中** → 「引入即合规」，非「改现有错」。先进 `scripts/audit/LITERATURE_ANCHORS_2026-06-13.md`，**每条走 Crossref/WebSearch 四要素核验**（项目史踩坑：Hillert JF→RFS / Shapiro→Kelly / Bozanic RAS→JAE）后下沉 manuscript。
- 措辞铁律：**动词降级**（观察性研究用「相关/预测/反映」不用「致/导致」）；**测度对齐**（Arena-Julio=证券集体诉讼风险≠LM litigious 词频；Buehlmaier-Whited=Naïve Bayes/MD&A≠LM constraining 词典；Fog 加 LM2014 批评+file size 稳健性）；**范围限定**（LM2013=IPO 招股书语料；Bodnaruk「与 KZ/WW/SA 低相关、正交补充、特定事件预测力更强」**删裸「优于」**；Hwang-Kim=封闭式基金）。
- 词典 provenance（`config/tone_dicts.json`）：litigious 数组在 **:37583**（非 v1 误写的 :34743，该处是 loughran 块 `_description`）；FLS 块 ~:38919-38936。

### WS-G　golden 受控重生 + 测试（gate）
- **前置**：WS-0 铁门满足（并行 golden 已 reconcile）。
- **触发**：WS-B 任一新列 → golden 列集断言（`test_panel_reproducibility.py:163`）必红。WS-A/C/D/E/F 纯标签/诊断/spec → **不触发**。
- **重生范围（修 v2 终审 P1：实为 6 块，非 3 块）**：单个 **article 级**新列（B1 `named_entity_ratio`/B2 boilerplate）的 golden record 足迹经直读 golden 行号坐实为 **6 块**：
  - **article 级原始列（raw 三轨）4 块**：`22_words_tone.parquet`（@2479）、`23_bert_tone.parquet`（@3799，**stage 23 整表透传**）、`24_herd_decay.parquet`（@5263）、`40_article_bank_level.parquet`（@15184）。
  - **聚合 `avg_*` 列 2 块**：`40_panel_yearly.parquet`（@6545）、`51_panel_with_controls.parquet`（@18338）。
  - ⚠ 外科注入若只改 22/24/40 三块（v2 旧写法），漏掉 `23_bert_tone`/`40_article_bank_level`/`51_panel_with_controls` → `test_panel_reproducibility` 列集断言（:163）二次 gate **必红**。**6 块必须同步注入**（4 块注 raw 三轨列、2 块注 `avg_*`）。
  - ⚠ **第 5、6 块（avg_* 进 40_panel_yearly + 51）是条件性的**：仅当 WS-B1 在 `encode.py` H2 块**显式登记** `agg[f'avg_named_entity{track}']=(...,'mean')` 时才出现；若只产 raw 列不登记聚合，足迹**塌为 4 块**（真对照 = `redundancy_log_length`/`redundancy_han_log_length`：golden 实测有 raw 三轨但 `encode.py` H2 **未登记 avg** → 只占 4 块；⚠ 勿用 `type_token_ratio` 当对照，它在 `encode.py:596` 已登记 `avg_ttr` → 实为 6 块列）。即 6 块 = raw 产出（WS-B1 三处编辑）∧ avg 登记（WS-B1 encode.py）两步皆做。
  - 命名歧义：golden record key 是 `22_words_tone.parquet`（外科注入操作对象以此为准），而 `tone_words.py:1719` 默认输出名写作 `22_tone_words.parquet`（已知盘面 stale），勿混用。
- **首选：外科注入法**（memory `loughran-exc-cols-fix-regen`）：隔离算新列直接注入上述 **6 个 parquet record + golden**，**绕开 stage 23 BERT 重跑的不确定性**（见下）。
- **次选：全链重跑** `22 → 23 → 24 → 45 → 46 → 51`（**不可跳 23**：`herd_decay.py:705-720` `raise SystemExit(1)` 禁回退读 22/21；stage 23 整表透传 stage22 新列）。
  - ⚠ **stage 23 offline 模型预检（失败模式订正）**：canonical env 钉 `HF_HUB_OFFLINE=1`；若 hub-id 模型 `finbert_cn`/`fin_sent_zh` 未在本地缓存，**默认 `strict_models=True`（tone_berts.py:451）下 offline hub-miss 会 fail-loud `raise`（硬停 stage 23），不是静默丢列**（`_looks_local` 分支 :467-477 只对本地私有模型如 FINBERT2_MODEL_DIR 触发 graceful-skip）。无论哪种，结论一致：**重跑前先预检 HF cache，缺则首选外科注入绕开整条 23→24**。（利好：BERT `cpu_strict`+argmax 确定，不引入 BLAS-FP 漂移。）
- **canonical env（全程）**：`NEWS_PROCESS_LLM_OFFLINE=1 PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 KMP_DUPLICATE_LIB_OK=TRUE HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`（用 `F:/Anaconda3/python.exe`）。
- **BLAS-FP 非确定列（须排除/同 env 防漂，列名订正）**：`bank_eigen_cent`/`bank_harmonic_cent`/`bank_cfbetween_cent`/`bank_clustering`（PYTHONHASHSEED 源）+ ~45 LDA/嵌入列（`coh_lda_*`/`centroid_diff_lda*`/`strat_*`/`auth_sim_emb*`，BLAS 线程源）。
- 验收：二次重建 content-sha 字节一致；`test_panel_reproducibility` + `test_dag_consistency` 绿。

### WS-H　全程质量门
ruff clean；引用 forensics（WS-F 每条核验）；三轨平价命名锁单测（B2 单轨须 by-design 披露）；共线/正交实测披露；`test_lexical_complexity`/`test_22_tone_words`/`test_papers_b_route`/repro/dag 绿。

---

## 4. 排序与依赖（修 v1 矛盾：WS-D 不再在第 1 波）

```
WS-0(前置硬门: reconcile 并行 golden + 干净 worktree) ── 必须最先
   │
第1波($0/golden-safe, 并行): WS-A(stata_export 标签) · WS-C(core_patterns) · WS-F(引用治理)
   │
第2波(golden-regen): WS-B1(named_entity) → [WS-B2(boilerplate)] → WS-G(外科注入/全链重生)
   │
第3波: WS-E(论文 spec+Stata, 引 golden 列) ;  manuscript(独立非-$0 写作)
   │
开放重设计项(不排波次): WS-D(39c 连续分支+换输入源) · B3 novelty · staleness-merge
   ▼
WS-H 终审门
```

---

## 5. 验收门（全绿才算完成）
1. ruff clean。2. `test_panel_reproducibility` 绿（重生后 0 漂移 + 二次重建字节一致）。3. `test_dag_consistency` 绿（STAGES 计数不变）。4. `test_lexical_complexity`（含 `_ALL_KEYS` 相等断言）+ `test_22_tone_words` + `test_papers_b_route`（142 锁不破）绿。5. 新列 codebook 显式 curate（非空引用）。6. 新引用 Crossref/WebSearch 四要素 100% 通过 + OVER-1..7 措辞落地。7. `.dta` 三轨 base 标签齐；`stata_runner doctor` 6/6；承载论文 `build-replication` 可打包。8. 三轨平价/共线披露/构念保真披露/SAFE loud 降级到位。9. **manuscript 若交付，人工核对（无自动门）**。

---

## 6. 风险与回滚（含审计新增）
| 风险 | 缓解 |
|---|---|
| **golden/encode/export 已脏，提交污染** | WS-0：reconcile 并行 golden + 干净 worktree 逐 hunk 重贴（**禁 by-name add 隔离同文件混改**） |
| **重生链跳 23 致新列丢失/SystemExit** | 链固定 `22→23→24→45→46→51`；首选外科注入 |
| **offline stage23 模型缺失致 BERT 列消失误红** | 重生前预检 HF cache；缺则外科注入 |
| **B2 落点/语料/聚合错配** | 落点冻结 tone_words.main()；语料口径披露；聚合走 encode.py H2 + verified 集 |
| golden 重生误 bless 49 BLAS-FP 列 | canonical env 全钉死 + 外科注入只改新列 + 二次重建字节一致 gate |
| named_entity 与 specificity 高共线 | corr>0.95 降级为诊断列 |
| 142 模板锁破 | 模板放 provisional 子目录；动 _common 才同步计数 |
| manuscript 无自动门致过度声称 | 标「人工交付物」；或补 assets 结构断言 |
| T=2 误当生产 | 全程标注；功效 deferred T=18 |

回滚：每 WS 独立提交；外科注入前备份 `_regen_backup_<date>/`；新列纯 append 可单独 revert。

---

## 7. 铁律 checklist（提交前逐项）
- [ ] **WS-0 满足**（并行 golden reconcile + 干净 worktree）。
- [ ] thin shim 冻结；DAG/OUTPUT_REGISTRY 计数不变。
- [ ] 三轨平价（单轨 by-design 披露）；full×ctx×ss 禁混同一 Hansen J。
- [ ] 冻结 prompt v8；不触 stage 21；不删 `_llm_cache.db`。
- [ ] SAFE loud WARNING（引 FINTECH_AC=None 先例，非静默）。
- [ ] 列名 ≤32（`avg_boilerplate_full`）；`_assert_track_triplet_unique` 通过。
- [ ] golden 重生用 canonical env；**重生/外科注入范围含 6 块**（`22_words_tone`+`23_bert_tone`+`24_herd_decay`+`40_article_bank_level` 注 raw 三轨列；`40_panel_yearly`+`51_panel_with_controls` 注 `avg_*`）；用户批准。
- [ ] 引用四要素 Crossref/WebSearch 核验；OVER-1..7 措辞收敛。
- [ ] codebook 显式 curate 新列 provenance（非 `_infer_*` 空兜底）；共线/SAFE 派生关系披露走 `codebook.py:138-140` emission-loop 前缀注入（镜像 loughran union 先例），非仅单列 `VariableMetadata`。
- [ ] **新列无需登记** `PanelBuildingSchema`（`core/schemas_yaml.py:91-107` 仅校验 `compute_*` 配置 flag，本计划无新 flag）**或** `REQUIRED_PANEL_COLUMNS`（`export.py:287-298` 硬契约仅 target_bank/year+4 t2v，`_ss` 刻意排除，新 `avg_*` 非必填）——列内扩展，确认不动这两处。
- [ ] **建 memory 主题文件 + 更新 MEMORY.md 索引**（单行 <200 字符）。
- [ ] **CLAUDE.md Current version 段追加一行变更叙述**（列内扩展，不 bump 大版本）。

---

## 8. 生产 T=18 待办（deferred，本机 T=2 不可代替）
全量 17M/T=18 重跑（30a 4-6h；B2 corpus-DF 分块防 OOM + 真全量语料口径）；新列 T=18 功效 + 跨年构成漂移检验（HRS 2020）；FLS 词表过 G-A2.1 专家审定门（precision≥0.80）后方进主表；T=18 golden 受控重生 + 承载论文 esttab 出真表。

---

## 附：MVP 垂直切片（最小风险闭环，修订版）
1. **WS-0**：确认/等待并行 golden 提交；建干净 worktree。
2. WS-F：建引用锚点（Hope-Hu-Lu 2016 RAS / Lang-Stice-Lawrence 2015 JAE / Dyer-LSL 2017 JAE，逐条 Crossref 核验）。
3. WS-B1：`named_entity_ratio`（3 处编辑 + 同步 test `_ALL_KEYS`）。
4. WS-G：**外科注入**（6 块：22_words_tone/23_bert_tone/24_herd_decay/40_article_bank_level 注 raw 三轨列 + 40_panel_yearly/51_panel_with_controls 注 `avg_*`）+ repro gate 绿 + 二次重建字节一致。
5. WS-A/C：`stata_export.py` 补 `named_entity` 三轨标签 + core_pattern。
6. WS-E：在 `bank_news_clarity` spec 填既有 tA7 占位槽 + 1 个 provisional 子目录 Stata 模板（零 142 锁）。
跑通后再扩 B2（含落点/语料/聚合域三冻结）、WS-D 重设计、staleness-merge、manuscript 起草。
