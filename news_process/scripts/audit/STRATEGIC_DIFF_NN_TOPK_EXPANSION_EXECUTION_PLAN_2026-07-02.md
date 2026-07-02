# 战略差异度 N-最近邻 top-k 扩展执行计划 (top-10/20/30/40/50)

- **日期**: 2026-07-02
- **作者**: Claude Code (Opus 4.8, ultracode)
- **状态**: **已实施 (IMPLEMENTED 2026-07-02)** — 三轮计划核查 + 一轮实现结果终审 (第四轮 7-agent 对实际代码, `ok_to_commit=true`/break-it 0 真崩) 后按计划执行完成; **16 文件 (15 改 + 1 新计划 md)** + 净增 75 列; 单测/集成/e2e-smoke/parity/ruff 全绿 (详见文末 §9 实施记录)。golden 重生按 Q3 DEFERRED 到生产机; 手稿 FWER prose 按 §8 待写。
- **paper 模块**: `strategic_diff`
- **相关既有计划**: `INJECT_FINTECH_DICT_WORD_LDA_TRACKS_PLAN_2026-06-21.md` (word/LDA 轨口径), `METRIC_AUDIT_OMNI_2026-06-11.md` (omni-g-strategic-02/05 值域 + |peers|<N→NaN 语义)

---

## 1. 背景与目标

现状: 战略差异度 (distinctness) 主指标

```
strat_diff_n5 = 1 − mean( top-5 最近邻同业的 TF-IDF 余弦相似度 )
```

- 逐年独立建模 (per-year); 对角线排除自身 (`np.fill_diagonal(sim, np.nan)`);
- 严格映射 Guzman & Li (2023, MS §3) `Ŝ_i = (1/N) Σ_{j∈J_i^N} δ_ij`, δ_ij = 1 − cos_sim(TF-IDF_i, TF-IDF_j);
- 现有 N-邻敏感性梯度 = **N ∈ {3,4,5,6,7}** (基准 N=5), 仅落在 **TF-IDF char + word 两轨 · full 轨**。

**目标**: 在保留 N=5 及现有 {3,4,6,7} 的基础上, **新增 N ∈ {10, 20, 30, 40, 50}**, 与 N=5 **互为稳健性、不分主次** (即同族 N-邻敏感性梯度, 无 primary/secondary 划分)。

**用户口径 (原文锚定)**: 用户原文举例 "strat_diff_n5 = 1 − mean(top-5 最近邻同业的 TF-IDF 余弦相似度)" (以 TF-IDF 为例说明构念)。→ **范围见 §2.1 (Q1 已拍板 = 最大范围: TF-IDF char/word + LDA + Embedding Qwen + Embedding large `_lg`, 全 3 轨 full/ctx/ss)**。⚠ 本节仅陈述构念与目标; **不再限定 TF-IDF-only** (v1 minimal 表述已废)。

---

## 2. 范围决策 (SCOPE — 用户 2026-07-02 已拍板: 最大范围)

> **用户决策 (AskUserQuestion 2026-07-02)**: Q1=**再加 LDA + Embedding(含 `_lg`)** (最大范围) · Q2={10,20,30,40,50} · Q3=golden DEFERRED · Q4=**并入同一 `n_neighbor` FWER 族** · Q5=**同步更新**复现 .do + 40 侧标签。

### 2.1 采用范围 (MAXIMAL — 全方法 × 全轨)
新 N ∈ **{10,20,30,40,50}** (统一常量 `_TOPK_NN`), **追加到每个既有方法轨的现有 N 集之上** (保留既有列, 逐位不动):

| 方法 | 现有 N | 扩后 N | 轨 |
|---|---|---|---|
| TF-IDF char | 3,4,5,6,7 | **+10,20,30,40,50** | full / ctx / ss |
| TF-IDF word (`_w`) | 3,4,5,6,7 (full); 5 (ctx/ss) | **+10,20,30,40,50** | full / ctx / ss |
| LDA+JSD (`_lda`) | 5 | **+10,20,30,40,50** | full / ctx / ss |
| Embedding Qwen (`_emb`) | 5 | **+10,20,30,40,50** | full / ctx / ss |
| Embedding large (`_emb_lg`) | 5 | **+10,20,30,40,50** | full / ctx / ss |

→ **净增恰 75 列** (5 个新 N × 5 方法 × 3 轨; 新 N∈{10..50} 与各方法既有 N 集**无交集**, 故 75 即净增, **无重叠可扣**)。ctx/ss 现有 char/word 仅 n5 → 扩后为 {5,10,20,30,40,50}; full char/word 为 {3,4,5,6,7,10,20,30,40,50}。

**关键修正 (成本)**: 扩 emb/`_lg`/LDA 的 N **不增任何嵌入/API 成本** — `_compute_nn_scores` 是对**已算好的相似度矩阵** (`se_mat`/`jsd_mat`, 每轨每方法只算一次) 的纯后处理 (多取几个近邻)。嵌入调用面 = `_build_embedding_sim_matrix` 每轨一次, 与 N 无关 → 缓存覆盖不变 → **离线 $0 可复现**。(计划 v1 的"付费嵌入重算"表述作废。)

### 2.2 保持不变 (与 N 无关)
- **centroid / fluidity / coherence**: 与 N 无关, 不动。
- `strat_sim_max*` (每方法每轨一个, N-independent): 不动。
- LDA 的 `[5]` 若某轨无独立 sim_max 逻辑改动, 仅扩 N_list。

### 2.3 铁律合规 (CLAUDE.md) — ⚠ 最大范围**触发** co-primary parity 面
- ⚠ **co-primary both-or-neither parity (v3.14.0)**: 新 `strat_diff_n{10..50}_emb` **必须**与 `strat_diff_n{10..50}_emb_lg` 严格双射 (both-or-neither)。producer 的 matrix 级 `if se is None or se_lg is None → 两者同 None` 守卫**已覆盖** (同一 N_list 喂两侧); 但 **parity 测试的族识别 `_is_emb_family` 硬编码前缀 `strat_diff_n5_emb`, 不认 `strat_diff_n10_emb`** (`.startswith` = False) → 新 emb 列**静默逃逸 parity 强制**。→ **必须扩** `test_embedding_coprimary_parity._EMB_FAMILY_PREFIXES` (改 `strat_diff_n5_emb` → 正则 `strat_diff_n\d+_emb` 或枚举各 N)。见 §4.9。
- ⚠ **两 co-primary 各自 just-identified, 禁混同一 over-id Hansen J**: `n{k}_emb` (Qwen) 与 `n{k}_emb_lg` (large) 是同一邻域半径的 co-primary 对, **禁**并入同一 over-id GMM; 论文各自单跑。
- ⚠ **三轨禁混同一 over-id Hansen J**: `n{k}_*` 的 full/ctx/ss 各自 just-identified 并排。
- ✅ **确定性/golden-safe**: char/word (char_wb + jieba 冻结) 纯本地确定; LDA (n_jobs=1+seed=42) 确定; emb/`_lg` 走缓存命中确定 (值来自 `_llm_cache.db`, cosine+argsort 确定)。新列**全部逐位可复现** (非 3 网络中心度 BLAS 列)。
- ✅ **嵌入 ≠ LLM**: 不涉及 stage 21 情感 LLM。

---

## 3. 统计可行性 (feasibility)

**关键闸门** (`_compute_nn_scores`, omni-g-strategic-05): `|peers| < N → NaN` (不再静默降级)。故 N=k 仅在"年内可比银行数 ≥ k+1"时非空。

**实测 (盘上 T=2 dev, `40_panel_yearly.parquet`)**:
- 2017: 88 家银行有金科新闻 (peer set = 87) → N=50 需 ≥51 → **可测**。
- 2018: 55 家银行 (peer set = 54) → N=50 需 ≥51 → **可测** (54 ≥ 50, 勉强满足)。
- 全部 N ∈ {10,20,30,40,50} 在两年均**非空可测**。

**生产 (真实全量 T=18, n_bank 目标 ~200)**: 覆盖更充分, N=50 无压力。

**披露口径 (须写入 docstring + manuscript)**:
- 大 N 时 top-N 近邻趋近"与几乎全部同业的平均距离" (N→n_banks−1 时 ≡ 全 peer 均距), 与 centroid 构念趋同但仍为 N-NN 口径 — 这是**互为稳健性的连续谱**, 非冗余。
- 年内可比银行 < N+1 的 (bank, year) → 该 N 列 NaN (优雅降级); 小样本年份 (如个别历史早年) 大 N 列覆盖率会下降, 论文表脚注须标注。

---

## 4. 实现步骤 (touchpoints)

### 4.1 [SSOT · 核心] 生产者 `pipeline/features/strategic_diff.py` (最大范围)
**新增模块常量** (顶部, SSOT): `_TOPK_NN = [10, 20, 30, 40, 50]`。
1. **char/word full · L1497**: `N_LIST = [3, 4, 5, 6, 7]` → `N_LIST = [3, 4, 5, 6, 7] + _TOPK_NN`。emit 循环 (L1584-1588 `for N in N_LIST`) 自动产 `strat_diff_n{N}`/`_w`。
2. **LDA/emb/`_lg` full · L1548/1559/1570**: `[5]` → `[5] + _TOPK_NN`。⚠ **emit 循环必须改** — 现 L1592-1600 仅写单列 `row['strat_diff_n5_lda']=sl['n5']...`; 须改为 `for N in ([5]+_TOPK_NN): row[f'strat_diff_n{N}_lda']=sl[f'n{N}'].get(...)` (emb/`_lg` 同)。**both-or-neither**: emb 与 `_lg` 用同一 N 列表, 保证列名双射。
3. **ctx/ss 全方法 · L1771/1775/1780/1789/1801**: 各 `[5]` → `[5] + _TOPK_NN` (char/word/lda/emb/lg 五方法); emit 循环 L1814-1826 同理改为 `for N in (...)` 多列写出 (含 `_ctx`/`_ss` 后缀)。
4. **docstring/注释 (本节 = 生产者内所有文档触点的唯一 SSOT; §4.8 不再重复)**: 批改反映全方法扩 N + 大 N 语义披露 (§3)。**穷尽清单** (终审补全):
   - **计数块** (须改数字): L85 `输出列 (~50 列)` → **~125** (净增 ~75); L93 `Full 轨 (18 列)` → **43** (char5+word5+lda5+emb5+lg5=+25); **L102 `Ctx 轨 (8 列, N=5 only)` → ~48 且删 "N=5 only"**; **L109 `Ss 轨 (8 列, N=5 only)` → ~48 且删 "N=5 only"**。
   - **⚠⚠ 会与代码语义相悖的遗留注释 (必改, 比陈旧计数更危险)**: L1738 `# N-NN 仅跑 N=5 (不展开...)` / L1769 `# N-NN (N=5 only)...` / L1813 `# N-NN 本轨 (N=5)...` → 改为 "ctx/ss 亦展开 N∈{5}∪_TOPK_NN"。
   - **陈旧 N 文案**: L13 / L39 / L732 (`_compute_nn_scores` docstring `N=3,4,6,7 为敏感性`) / L1374 / L1389 (`N=3,4,5,6,7 for TF-IDF; N=5 for LDA/Embedding`) / L1495-1496 (`N_LIST=[3,4,5,6,7]` 白话) / L98/100/105/107/112/114/132/134/137 (各方法 "N=5" 列名清单) → 文案含 10,20,30,40,50。纯文档零数值影响, 但求穷尽。
5. **config 日志 L1512**: `N_LIST={N_LIST}` 动态引用自动反映; 建议补打 `_TOPK_NN` + 各方法轨 N 集。
6. **诊断/覆盖段 + `_log_robustness_diagnostics`**: 基准列仍 `strat_diff_n5`, 六方法 corr 固定列表不改; **值域断言 L1941-1953 自动正确** — 新 `_emb`/`_emb_lg` N 列命中 `_emb` 分支 [0,2] (距离 δ=1−cos), TF-IDF/LDA 新列命中 [0,1], 均与 `_compute_nn_scores` clip 一致。
7. **`_compute_nn_scores`**: 对非连续/大 N + `is_distance` (LDA) + `sim_bounds=(-1,1)` (emb) **已正确处理**, 无需改函数体。

> ⚠ **实施铁律 (二轮核查修正)**: 须做"单 n5 → for-N 多列"转换的 emit 语句 = **共 8 处** (非 5):
> - **full 3 处**: L1593 `strat_diff_n5_lda` / L1596 `strat_diff_n5_emb` / L1599 `strat_diff_n5_emb_lg`。(full 的 char/word emit L1584-1588 **已在** `for N in N_LIST` 循环内, 扩 N_LIST 自动产列, **不算**在这 8 处。)
> - **ctx/ss 5 处**: L1814 char / L1815 word / L1819 lda / L1822 emb / L1825 lg。
> - ⚠⚠ **陷阱**: ctx/ss 的 **char/word emit (L1814/1815) 是单 n5 硬写, 并未进任何 N_LIST 循环** (与 full char/word 不同!)。若只改 compute 调用 (L1771/1775) 为 `[5]+_TOPK_NN` 却漏改这两处 emit → 新 N **算出但不写出** → ctx/ss char/word 的 n10..n50 **静默缺列且不报错** (因 `sc['n5']` 键仍在)。compute 与 emit **必须成对改**。
> - 每处 emit 须保 `.get(bank, np.nan)` 缺失兜底; emb 与 `_lg` **严格同一 N 列表** (`[5]+_TOPK_NN`) 保 parity 双射。

### 4.2 [论文规格] `papers/strategic_diff/paper_spec.yaml`
- `differentiation_claim` (L10): "N-邻 (N=3..7)" → "N-邻 (N=3..7,10,20,30,40,50)"。
- `outcome.enrichment_source` (L30-31): `strat_diff_n{3..7}` → 含新 N 文案。
- `treatment.alternative` (L35): 追加 `strat_diff_n10, strat_diff_n20, strat_diff_n30, strat_diff_n40, strat_diff_n50`。
- `inference.exploratory` (L78): "N-邻敏感性 strat_diff_n{3,4,6,7}" → "...{3,4,6,7,10,20,30,40,50}"。
- `inference.families.n_neighbor` (L85, Q4=并入同族): 追加 char 的 `strat_diff_n{10,20,30,40,50}` → Romano-Wolf FWER 族 (headline **char-only**, 与既有 n_neighbor char-only 口径一致) 含全部 N (兑现"互为稳健性、不分主次" = 同族同权多重检验校正)。
- confirmatory 主规格 (L73-76) **不变** (仍 n5→tobin_q); 新 N 全归 exploratory。
- ⚠ **FWER 族口径自洽 (二轮核查)**: 最大范围产出 ~60 个非-char 新 N 列 (word/lda/emb/`_lg` × 3 轨 × 5 N), 须在 spec 显式声明其推断角色, 否则与 §2.1"全方法互为稳健性"叙述有张力。**口径**: 这些列仅作 **point-estimate 探索性稳健** (各自单跑, **不组建独立 FWER 族**; headline FWER 族保持 char-only)。"不分主次"指**同方法内 N 梯度**同权, **非跨方法合族** (跨方法是既有的 method-robustness 维度)。
- ⚠ **n5 双角色披露 (P2, 手稿 prose)**: n5 既是唯一 confirmatory 主规格 (未校正单假设 n5→tobin_q) 又是 n_neighbor 族成员 (Romano-Wolf 校正后 p)。手稿须落地统计正当性 prose (非仅断言"正交"): confirmatory 主张立于预设单一未校正检验; n_neighbor 族 (含 n5) 为独立标注的探索性 N-敏感性, 报族内校正后 p; 且披露族 5→10 使既有成员校正后 p **单调变严** (审稿可见), 说明 n5 双角色不构成 double-counting。

### 4.3 [论文代码] `papers/strategic_diff/`
- `figures.py` L76-79: `range(3, 8)` → `[3,4,5,6,7,10,20,30,40,50]`; `raise KeyError` 文案同步; 系数敏感性图纳入新 N。
- `tables.py` L17-21: 显式 N-邻列表追加新 5 列 (descriptives / 相关表纳入)。

### 4.4 [Stata 模板] `papers/_common/stata_templates/strategic_diff/`
连续 `forvalues n = 3/7` **无法**表达非连续 {10,20,30,40,50} → 全部改**显式 list 循环** `foreach n in 3 4 5 6 7 10 20 30 40 50`:
- `14_table5_robustness.do.tmpl` L20 + L35 (两处 forvalues; esttab 动态点名循环同步)。
- `30_figure1_n_sensitivity.do.tmpl` L15 (forvalues) + L26-27 (coefplot)。
  - ⚠ **P1 核查发现 + 三轮精修**: coefplot 现为**写死点名** `(N3,...)..(N7,...)`。**两层崩点须都堵** (三轮 break-it 指出计划旧处方只堵了下游命名):
    - **① 输出侧 (命名)**: coefplot/esttab 硬点名 N3..N7 → 若某 N 估计未建立则引用不存在估计崩 r(198)/r(111)。→ 仿 `14_table5` 用 `estimates dir`+`list posof` **动态构组**。
    - **② 上游 (估计建立)**: `reghdfe` (30_figure1 L18 / 14_table5 L23) **无 `capture` 包裹**; 若某 N 列**跨全 panel 皆 NaN** → reghdfe 抛 r(2000) 无观测**先崩**, 动态命名救不了。→ reghdfe 前加 `capture` + `if !_rc eststo N{n}`。
    - ⚠ **严重度校正**: 生产者对每 N **无条件 emit** (列恒存在) → `capture confirm variable` 恒过; 真实崩点是"列存在但全 NaN"。此仅当某 N 跨**全 panel** 皆 NaN — 而 N≤50 在生产 (T=18, 近年 >50 家银行) **不可达**, 故**实风险低** (非"极易触发"); 但 capture 是零成本防御, 仍建议加。`keep(strat_diff_n*)` 通配已自动含新 N, 无需改。
- `10_table1_descriptives.do.tmpl` L21: summary 变量清单追加新 5 列。
- 头部注释 "N=3..7" 文案同步。
- ✅ **核查确认 (三轮独立 grep)**: 全目录 N-sweep 仅存在于 **14/30/10** 三模板; **00_master/01_data_prep/11/12/13/15/16/17/18/19** 均仅用固定 `strat_diff_n5` (或多方法单-N 变体 `n5_w/_lda/_emb`, 如 12_table3) → **已核清无需改** (含同日新建的 19_table10_anchor_robustness, 用 `auth_sim_*` 与 N-邻正交)。`foreach n in 3 4 5 6 7 10 20 30 40 50` (或 `numlist 3/7 10(10)50`) Stata 语法正确。
- ⚠ **核查纠正 (§4.4c)**: 本计划所有模板编辑均为 **body-only, 头部保持磁盘现状不动**。实测 14_table5/30_figure1 头部仅 `version 19`+`clear all`+`set more off` (**无** `set maxvar`/`set linesize`); 10_table1 有 maxvar 无 linesize。**勿**为"兑现 CLAUDE.md 理想头部"而误注入 `set maxvar 32767`/`set linesize 120`。`.do.tmpl` **文件数不变** (仅改内容; 盘上实测 `rglob *.do.tmpl = 145`, CLAUDE.md 所述 142 基线已陈旧, 不影响"不改文件数"不变量)。

### 4.5 [Stata 标签] 标签处理
- `data/processed/46_panel_yearly_labels.do` = **stata_export.py 自动生成**; char/word N 列走**列名自兜底** (不在 `HEURISTIC_LABELS`)。→ 新 char/word n10..n50 自动获自兜底标签。
- ⚠ **最大范围新增** (精确计数, 防 partial-edit): 新 `strat_diff_n{10..50}_emb{,_ctx,_ss}` 是嵌入族, 须有 `_lg` 标签孪生。精确增量 =
  - **手写 `HEURISTIC_LABELS` +15 条** (emb × 3 轨 × 5 N; 各带 `(co-primary: Qwen/Qwen3-Embedding-8B)` 标注; 现 n5_emb 模板 ~60 字节 < 80 上限, 有余量);
  - **`_MAIN_ANCHOR_KEYS` +15 条** (同名);
  - **`_lg` 15 条自动派生** (L527-536 循环: track 后缀前插 `_lg` / 裸名 append `_lg` + Qwen→large replace), **无需手写**。
  - 🔒 **原子性铁律**: `_MAIN_ANCHOR_KEYS` 与 `HEURISTIC_LABELS` 两处**必须同一次编辑同增** — P2-D 守卫 (L522-526 `assert not _missing_annot`) 在 `build_variable_labels` 被调用时逐条校验 anchor key ∈ 带 Qwen 标注的 HEURISTIC_LABELS; 加了 anchor key 却漏手写 label (或漏 Qwen 标注) → **fail-loud 崩**。sim_max 系 N-independent, **不新增**。
- `stata/09_label_strategic.do` (根级手写中文标签, live — 核查✅ 经 `stata/99_master.do` L106-107 调用): 追加 n10..n50 中文标签。⚠ **三轮核查两点**:
  - **① 只补 full + ctx 轨** (与文件现状一致): 实读该文件**当前仅 full (L15-52) + ctx (L53-71) 两轨, 无任何 `_ss` 标签** (连既有 `strat_diff_n5_emb_ss` 都没有; `_ss` 标签由 46 侧 `stata_export.py` 自动兜底)。→ 新 N 标签**同样只补 full+ctx**, 勿引入 n5-无-ss / n10-有-ss 的不对称。
  - **② 用 `capture label variable`**: 该文件现用**无 capture** 的 `label variable`; 若被标变量在盘上 `.dta` 缺列 → `r(111)` 中止 `99_master.do`。新 N 标签须用 `capture label variable` (或确保标签与列同批落盘)。

### 4.6 [文档/手稿] (非代码, 数值零影响)
- `papers_assets/strategic_diff/README.md`: **逐行点名** L7 (`N-邻 (N=3..7)`) / L13 (`strat_diff_n{3..7}`) / L24 (`N-邻`) / L44 (`strat_diff_n5 默认`) → 含新 N。
- `papers_assets/strategic_diff/drafts/{en,zh}/manuscript.tex` (⚠ 终审纠正完整路径): 手稿摘要 L18 **无字面** `N=3..7` 亦**无** `strat_diff_n5` (仅泛化 "N-最近邻 / N-nearest-neighbor TF-IDF")。→ 应**新增大-N 稳健性披露 prose** (§3 语义 + §6 FWER 口径), **非字符串替换**。
- (`strategic_diff.py` 内 docstring/注释触点 → §4.1.4 SSOT; `__init__.py:12` → §4.8。`figures.py` 顶部 docstring 若含 "N=3..7 敏感性" 一并改。)
- 本 execution plan 归档 `scripts/audit/`。

### 4.7 [排除项确认] 无需改
- `core/schemas.py::OUTPUT_REGISTRY`: stage→file 映射, **不逐列枚举** strat_diff → 无需改 (核查✅)。
- `core/dag.py`: 无新增/删除 stage → 无需改 (核查✅)。
- `pipeline/panel/stata_export.py` `HEURISTIC_LABELS` (**stage-46 导出器**): char/word N 列从不入此 dict (走 `build_variable_labels` 列名自兜底) → 无需改 (核查✅)。
  - ⚠ **核查纠正**: 本条只对 `stata_export.py` (46 侧) 成立。**另有 stage-40 导出器 `pipeline/panel/export.py::STATA_LABELS`** 显式硬编码了 n3..n7(+`_w`) 学术标签 → **是触点, 见 §4.8**。原计划把两个导出器混同, 此处更正。
- `derivative_replication.py`: 仅用 `MAIN_DIFF_VAR/MAIN_TREAT = strat_diff_n5` (n5 不变) + 模板替换 → 无需改 (核查✅, 模板已在 §4.4 处理)。
- `pipeline/panel/codebook.py` (三轮新扫): L1957/L1977 用**泛型** `elif 'strat' in var_name:` 子串生成标签 → 新 `strat_diff_n{10..50}` 列**自动覆盖, 不硬编码 N** → 无需改 (核查✅)。
- `pipeline/panel/runner.py` 步骤 8e 嵌入 co-primary 诊断 (L2440-2463, 三轮新扫): 仅枚举 **N-independent 契约别名** (`strat_diff_full/ctx/ss`, `strat_diff_lg_*`), **不含** `strat_diff_n5_emb` 更不含新 N 列; 且为**软诊断** (缺列仅 WARNING 不 raise) → 新列零影响, 无需改 (核查✅)。

### 4.8 [核查新增触点] (verification workflow 2026-07-02 发现的遗漏)
- **P2 · `pipeline/panel/export.py::STATA_LABELS` (L1131-1160)**: 40_panel_yearly.dta 显式标签源, 逐条枚举 `strat_diff_n{3..7}`+`_w` (char/word) 及 `n5_lda`/`n5_emb`/ctx 变体。→ 追加 char/word 的 n{10..50}(+`_w`) 同款标签 (不触发 dup-key invariant `test_40_panel_export_main.py`, 新键唯一)。
  - ⚠ **emb/lda 的 n10..n50 跨文件依赖 (二/三轮核查修正)**: 40-path 的 emb/lda 新 N 列**不在** export.py 显式补录 → 走 `_apply_label_fallback` → `build_variable_labels`。**终审纠正**: 二者兜底路径**不同** — **emb** 命中 `stata_export.py::HEURISTIC_LABELS` (依赖 §4.5 落实, 得 Qwen/`_lg` 标签); **lda** 在 HEURISTIC_LABELS **无 `strat_diff_n*_lda` 键** → 走**列名自兜底** (`strat_diff_n10_lda`, 参 `46_panel_yearly_labels.do` 既有 `capture label var strat_diff_n5_lda "strat_diff_n5_lda"`)。均非破坏 (覆盖恒 100%)。→ **推荐 (a)** 接受此不对称 (与既有 40-path 仅显式 n5_emb / lda 自兜底的口径一致)。
- **P1 · `papers_assets/strategic_diff/do/strategic_differentiation.do` (L105/110/112/26-27, 74)**: RETAINED 手写复现分析 .do (README.md:36 标"保留"), 含**真实 N-sweep**: `foreach n of numlist 3/7` + `esttab n3 n4 n5 n6 n7` + `mtitles("N=3".."N=7")` + docstring。不改则其 N-敏感性表恒停 N=3..7, **直接违背本次目的**。→ `numlist 3/7` → `numlist 3 4 5 6 7 10 20 30 40 50`, esttab/mtitles/注释同步。⚠ L74 `sum strat_diff_n*` 通配会**静默多吞** 10 列 (见 §6 通配风险)。(同目录 `text_coherence.do:75` 仅用 n5, 不动。)
- **P2 · docstring 触点**: `strategic_diff.py` 内所有 docstring/注释触点 (含计数块与相悖注释) 的**穷尽清单 + 正确目标值** = **§4.1.4 (唯一 SSOT)**; 本处不再重复计数 (原 "~60/28" 为 minimal 残数误值, 已废)。另 `papers/strategic_diff/__init__.py:12` (`strat_diff_n3..n7` DV 清单文案) → 含新 N。纯文档零数值影响。

---

### 4.9 [co-primary parity] 最大范围新增触点 (emb/`_lg` N 列)
1. **producer both-or-neither** (已覆盖): `strategic_diff.py` full L1576-1578 + ctx/ss L1807-1809 的 `if se is None or se_lg is None → 两者同 None` 守卫在 matrix 级保证 emb↔emb_lg 同生共灭 (守卫在 `if _LARGE_SPEC:` 内, 生产态 `_LARGE_SPEC` 恒非空)。列名双射依赖两侧 emit 迭代**同一 N 列表** → 用统一 `_TOPK_NN` 常量强制字面相同。
2. **parity 测试族识别** (⚠ 必改, 有实现陷阱): `tests/test_embedding_coprimary_parity.py::_is_emb_family` (L65-69) 用 `base.startswith(p)` 对 `_EMB_FAMILY_PREFIXES` 元组做**前缀匹配** (非正则)。`_is_emb_family("strat_diff_n10_emb")` = **False** → 新 emb N 列**逃逸 parity 强制**。
   - ⚠⚠ **禁止字面 swap**: 若把元组里 `'strat_diff_n5_emb'` 直接换成字面串 `'strat_diff_n\d+_emb'`, `startswith` 会把 `\d+` 当**字面字符**永不匹配 → **不仅新列逃逸, 连既有 `strat_diff_n5_emb` 也从此逃逸 (静默回归, 丢既有覆盖)**。
   - ✅ **正确修法**: 改 `_is_emb_family` **函数体**, 加正则分支 `if re.match(r'^strat_diff_n\d+_emb', base): return True` (`^` 锚定起始)。**严禁**用裸前缀 `strat_diff_n` (会误吞 TF-IDF `strat_diff_n5`/`n3`/`n5_w`/`n5_lda` → 触发 `test_parity_non_embedding_strat_diff_not_required_lg` 红灯)。正则要求 digits 后紧跟 `_emb`, 故 `strat_diff_n10`/`_w`/`_lda` 均不匹配 (核查✅安全)。
   - **测试须补 4 项**: ① 正向单测 `strat_diff_n10_emb` ⟺ `strat_diff_n10_emb_lg` 双射 (full 轨) + 单边缺失即违例; ② **⚠ ctx/ss 双射 (三轮补: 最非平凡路径)** —— producer 产 `strat_diff_n10_emb_lg_ctx` (**lg 在 track 后缀之前**), 须靠 `_strip_lg` 位置无关剥离才与 base `strat_diff_n10_emb_ctx` 对齐; 追加 `check_coprimary_parity(['strat_diff_n10_emb_ctx','strat_diff_n10_emb_lg_ctx','strat_diff_n10_emb_ss','strat_diff_n10_emb_lg_ss'])==[]` 显式锁 (test 文件 L14-15 docstring 专门警告两种 lg 位置); ③ **回归锁** `strat_diff_n5_emb` ⟺ `strat_diff_n5_emb_lg` 仍被强制 (防字面 swap 静默丢覆盖); ④ 扩 `test_parity_non_embedding_strat_diff_not_required_lg` 的 `cols` 纳入 `strat_diff_n10`/`n10_w`/`n10_lda` 断言仍返 `[]` (证正则不误吞)。
   - **注释同步**: 更新 L26-27 / L41-42 硬编码的 "n5 前缀口径" 注释 → 反映正则族判 + TF-IDF/word/LDA 各 N 列一律无 `_lg`。
   - (可选清理: 加正则后元组内 `'strat_diff_n5_emb'` 条目被 `^strat_diff_n\d+_emb` 涵盖成冗余, 可删或加注; 不删无害。)
3. **stata_export `_lg` 标签派生** (见 §4.5): `_MAIN_ANCHOR_KEYS` 扩含新 emb N 列 (含精确计数 + P2-D 原子性铁律)。

## 5. 测试与 golden 处理

### 5.1 受影响测试 (核查结论)
- `tests/test_25_audit.py`: ✅ **无需改** — `test_output_columns` 断 `len(strat_cols)>=10` (前缀过滤, 加列只增不减); 值域断言遍历 `strat_` 前缀 (新 TF-IDF 列自满足)。
- `tests/test_paper_figures_ext.py`: ✅ **无需改** — 仅测 CSV 缺失 raise; `figures.py` `vars_present=[... if in df.index]` 按 index 成员过滤, `range→list` 改动对 fixture 结果不变。
- `tests/test_embedding_coprimary_parity.py`: ⚠ **必改** (最大范围) — `_EMB_FAMILY_PREFIXES` 族识别扩到 `strat_diff_n\d+_emb` (见 §4.9), 否则新 emb N 列逃逸 parity; 补双射合成单测。
- `tests/test_dual_compute_coverage.py`: 核查其是否枚举 emb/`_lg` 精确列集 (若是 → 追加新 emb N 列); 若仅前缀/存在性则无需改 (实施期确认)。
- `tests/test_omni_fix_strategic.py`: 若断言精确 N_LIST 值 → 更新; 其 `test_peers_lt_n_nan_*` (L162-178) 已用合成 sim 矩阵验 `|peers|<N→NaN`, 可直接镜像扩到 `[10,20,50]`。
- **新增单测**: 断言 `strat_diff_n{10,20,30,40,50}` (+`_w`) 存在且 ∈[0,1], 且 `|peers|<N→NaN` (mock 小 peer set)。可选: 大 N 覆盖率下限 fail-loud (见 §6)。

### 5.2 golden (列 schema 变更)
- `tests/integration/test_panel_reproducibility.py::test_column_hashes_match_golden` 对**磁盘上** `40_panel_yearly.parquet` 做 **exact column-set 比对** (`extra = df_cols − expected_cols` 非空即 FAIL; 磁盘无该文件则 skip)。
  - ⚠⚠ **终审实证纠正 (原"保持绿"表述为事实错误)**: 终审 agent **实跑 pytest** 证 —— 盘上 `40_panel_yearly.parquet` **已被重生为 v3.14.0** (3144 列, 含 `_emb_lg` 无 `_t2v`), 而 golden JSON **仍停在 2787 列** (含 `_t2v` 无 `_lg`) → 该测试**当前已是既存红灯 (~17 FAILED, 与本次改动无关)**, 是 "v3.14.0 重生 parquet 但未重生 golden" 的**已知分叉**。故本次改动**不改变** golden 测试状态 (本就红, 我们不动盘上 parquet → 不新增红灯亦不转绿)。原 v1/v2 "DEFERRED 则保持绿" 论断作废。
- **处理 (Q3 = DEFERRED, 遵循 stage13 radius 先例)**: golden 重生 DEFERRED 到生产语料机。**安全论证只靠 baseline-stash A/B 差分** (改动前后本机各产一次 panel, 证"仅新增 ~75 列 + 0 既有列 hash 漂移"), **不依赖 golden 测试转绿** (它本就是既存分叉红灯)。生产机受控重生 golden 后统一转绿。
- ⚠ **确定性分层披露 (二轮核查修正; 原 minimal-scope "纯 TF-IDF $0" 表述作废)**: 最大范围 ~75 新列的确定性**分三层**, 非全部纯 TF-IDF:
  - **char/word** (char_wb + jieba 冻结): 纯本地确定, 逐位可复现;
  - **LDA** (`_lda`): 本地确定 (`n_jobs=1` + `random_state=42`, AST + 逐位双锁);
  - **emb/`_lg`** (`_emb`/`_emb_lg`): **非纯 TF-IDF** — 值来自 `_llm_cache.db` 嵌入**缓存命中** + `cosine`/`argsort`; 逐位复现须**嵌入缓存 0-miss** + BLAS 线程钉 1 (与既有 `n5_emb` 同确定性类)。
  - 若本机重生 golden: 须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1 + **嵌入缓存 0-miss** + 排除 3 网络中心度 BLAS 列。因决策 = DEFERRED, 本机不重生, 上述仅生产机适用。

### 5.3 pipeline 重跑 (使新列落盘)
- 落列需重跑 strat_diff 特征 + panel 合并 (stage 40)。char/word/LDA 纯本地; emb/`_lg` 走 `_build_embedding_sim_matrix` (每轨一次, **与 N 无关**) — **不新增嵌入 API 调用** (新 N 是同一 `se_mat` 的后处理), 缓存 0-miss 即离线 $0 重跑。

---

## 6. 风险与缓解
| 风险 | 缓解 |
|---|---|
| 大 N 覆盖薄 (小样本年 NaN) | 已有 `|peers|<N→NaN` 优雅降级; 论文表脚注标注覆盖率 (§3 披露) |
| **coefplot 大 N 全 NaN → reghdfe 无观测 → 整图崩** (P1) | 30_figure1 补 `estimates dir`+`list posof` 动态构组 (§4.4); 非仅硬追加点名 |
| **Stata `strat_diff_n*` 通配符静默扩容** | `sum strat_diff_n*` (strategic_differentiation.do:74) / coefplot `keep(strat_diff_n*)` 会自动多吞 10 列 → summary/描述表/图变量集无声漂移。实施期清点所有 `strat_diff_n*` glob, 决定收窄点名 or 接受扩容并披露 |
| **Romano-Wolf FWER 族 5→10 稀释既有功效** | 扩族使族内校正**单调变严** → 拉高既有 n3..n7/n5 的 rwolf 校正后 p 值 (审稿可见)。决策见 §7 (披露 vs 大 N 单列独立展示) |
| 大 N 覆盖率断崖无 fail-loud | 生产早年 (2007–2010) 金科新闻稀疏, N=50 可能整年 NaN 却无告警 → 加覆盖率下限 WARNING (§5.1 可选单测) |
| 标签口径两 .dta 不对称 | export.py (40) + stata_export.py (46) 两导出器标签口径本就不一致; 决定是否两侧都补齐 n10..n50 显式标签 (§7) |
| golden 红灯误判为回归 | baseline-stash A/B 隔离 "对称 churn ≠ 回归" (近期日志富集教训) |
| forvalues→foreach 改写引入 Stata 语法错 | 模板改后 stata_runner `/b` smoke (末尾 `exit, clear`) |

---

## 7. 核查计划 (verification — 本计划的"进行核查"环节)
多 agent 对抗式审计, 校验本计划:
1. **touchpoint 完整性**: 全仓独立清点所有硬编码 N-邻枚举 (`n3..n7` / `3/7` / `range(3,8)` / `N_LIST` / `strat_diff_n\d+`), 交叉核对 §4 清单**是否有遗漏**。
2. **可行性/统计**: 复核 `_compute_nn_scores` 对非连续大 N 的正确性 + 是否有任何代码路径假设 N 为个位数/连续 (matrix/argsort/列命名)。
3. **测试/golden 影响**: 独立枚举断裂测试 + golden 处理正确性。
4. **合规**: co-primary parity / Hansen-J / 确定性铁律零破坏确认。
5. **completeness critic**: 计划遗漏了什么 (未列文件/未验断言/未披露口径)。

**用户决策 (2026-07-02 已拍板, 全部锁定)**:
- Q1 范围 = **最大范围** (TF-IDF char+word + LDA + Embedding + `_lg`, 全 3 轨) — 见 §2.1。
- Q2 N 集合 = **{10,20,30,40,50}** (不补 {8,9})。
- Q3 golden = **DEFERRED 到生产机** (本机 baseline-stash A/B) — 见 §5.2。
- Q4 FWER = **并入同一 `n_neighbor` 族** (char headline N 集全并入; 手稿须披露族 5→10 稀释 + n5 双角色正交) — 见 §4.2/§6。
- Q5 = **同步更新** `strategic_differentiation.do` + `export.py::STATA_LABELS` (+ §4.9 emb 标签)。

---

## 8. 核查结论 (verification closure, 2026-07-02)

**方法**: **三轮**对抗式 workflow — 初轮 (minimal, 8-agent) + 二轮增量 (maximal, 5-agent) + **终审** (maximal 从零重验, 10-agent: 6 域逐行重验+行号漂移 / 计划内部一致性 / 完整性新角度 / 对抗 break-it / 最终裁定; ~119 万 token)。

**终审总判定**: `ready_after_minor_edits` (`is_flawless=false` → **已按终审全部 defect 逐条修订至 v3**)。终审关键结论:
- ✅ **核心实现逻辑正确、行号零漂移**: 10 个 `_compute_nn_scores` 调用点 / 8 处 emit 块 / N_LIST / 值域断言 / both-or-neither 守卫 / parity 正则 / 标签链 / 可行性 —— 全部实读代码逐一证实, 无一行号漂移。
- ⚠ 全部 defect 均为**计划文档级** (无重设计): (P1) §1 残留 TF-IDF-only 自相矛盾 → 已改指 §2.1; (P2) §5.2 golden "保持绿" **事实错误** (终审实跑 pytest: 盘上 parquet 3144 列 vs golden 2787 列 → **已既存 ~17 FAILED**, 与本改动无关) → 已改为"既存分叉红灯, 安全靠 baseline-stash A/B"; (P2) docstring 计数 §4.1.4↔§4.8 互斥 → 已统一为 ~125/Full 43 且归 §4.1.4 单一 SSOT; (P2) reghdfe 无 capture 处方补全 (输出侧+上游双堵) + 严重度校正; (P2) parity 补 ctx/ss lg-before-track 双射测试; (P2) 09_label 用 capture + 只补 full/ctx; (P3×多) 相悖遗留注释 L1738/1769/1813、ctx/ss 计数块 L102/109、codebook.py/runner.py 8e 排除项、manuscript 路径等 → 全部折回。

**终审证实无误的关键面 (confirmed_solid)**: 见上"已证实的强项"。**无 P0/P1 遗留** (P1 §1 已修)。

---

**(以下为初/二轮结论, 保留存档)** 初轮 8-agent (5 维审计 + 2 路重扫 + 1 评审) + 二轮增量 5-agent, 两轮均 `ready_after_edits`。

**已证实的强项 (实读证据)**:
1. ✅ full char/word 扩列**确为改 `N_LIST` 一行** (emit 已在 `for N in N_LIST` 循环)。
2. ✅ `_compute_nn_scores` 对**非连续/大 N + is_distance(LDA) + sim_bounds(emb) 全无假设**: dict key `f'n{N}'` 动态, `idx[:N]` 整数切片, `len(valid)<N→NaN` 先判后切。
3. ✅ 值域断言对新列**自动正确** (`_emb`→[0,2], TF-IDF/LDA→[0,1])。
4. ⚠→✅ **co-primary parity (maximal 修正)**: 初轮"零影响"**仅 minimal 成立**; 最大范围下 `_is_emb_family("strat_diff_n10_emb")=False` → 新 emb 列**静默逃逸 parity** → **必改** `_is_emb_family` (§4.9)。producer matrix 级 both-or-neither 守卫仍保证 emb↔`_lg` 同生共灭 (同 N 列表)。
5. ✅ 确定性分层 (char/word 纯本地; LDA seed=42; emb/`_lg` 缓存命中确定) — 全非 3 网络中心度 BLAS 列。
6. ✅ Hansen-J just-identified 纪律不破 (IV=Bartik 不含 strat_diff_n*)。
7. ✅ 标签: `_MAIN_ANCHOR_KEYS`+`HEURISTIC_LABELS` +15/+15、`_lg` 15 条自动派生; P2-D 守卫要求原子同增 (§4.5)。
8. ✅ 测试: `test_dual_compute_coverage`/`test_25_audit`/`test_paper_figures_ext` 均**存在性/前缀/index 过滤, 不因 ~75 新列红灯**; `test_embedding_coprimary_parity` 必改 (§4.9)。

**修订后触点总数 (maximal)**: **约 16–18 个文件** (`strategic_diff.py` 核心+docstring / `paper_spec.yaml` / `figures.py` / `tables.py` / 3 Stata 模板 / `strategic_differentiation.do` / `export.py` / `stata_export.py` / `09_label_strategic.do` / `test_embedding_coprimary_parity.py` / 新增单测 / README + manuscript×2 + `__init__.py`)。数据列净增 **~75 列**; 核心逻辑改动 = `N_LIST` 一行 + **8 处 emit 块**"单 n5→for-N" + parity 函数体正则。

**剩余项 (均非阻塞, 无 P0/P1)**:
- **实施期二选一**: §4.8 40-path emb/lda 标签对称 (推荐接受不对称); §4.9 冗余元组条目清理 (可选)。
- **手稿 prose 待写** (§4.2/§6): FWER 族 5→10 稀释披露 + n5 confirmatory/robustness 双角色正当性。
- **实施后须跑**: baseline-stash A/B 差分证 "仅净增 ~75 列 + 0 既有列 hash 漂移" (golden 测试本就既存分叉红灯, 不作为绿灯依据); parity/新单测本机跑绿; 改动的 `.do.tmpl` 走 `stata_runner /b` smoke。
- **golden 正式转绿**: DEFERRED 到生产语料机受控重生 (Q3)。

---

## 9. 实施记录 (implementation closure, 2026-07-02)

**改动文件 (16 个 = 15 改 + 1 新计划 md, 均 by-name; ⚠ 提交须排除 `data/processed/v3_5_1_constants.json` 与 `CLAUDE.md` — 二者为并发/会话前既有改动, 与本任务无关)**:
- 生产者 `pipeline/features/strategic_diff.py`: `_TOPK_NN=[10,20,30,40,50]` 常量 + `N_LIST`(char/word full) + `LDA_EMB_N_LIST=[5]+_TOPK_NN` + 全方法 compute `[5]→LDA_EMB_N_LIST` + 8 处 emit 单→for-N (full lda/emb/lg + ctx/ss 五方法, 含 ctx/ss char/word 循环外硬写陷阱已堵) + docstring/注释穷尽同步。
- parity `tests/test_embedding_coprimary_parity.py`: `_is_emb_family` 函数体加 `^strat_diff_n\d+_emb` 正则 + 注释 + 4 组新测 (full/ctx-ss 双射 · 孤儿 · n5 回归锁 · 非嵌入负锁扩大 N)。
- 新单测 `tests/test_omni_fix_strategic.py::TestTopKNExpansion`: 常量 SSOT / |peers|<N→NaN / 大 N 可测 / 单调 / emb bounds。
- 标签: `export.py::STATA_LABELS` +char/word 10 条; `stata_export.py` `_MAIN_ANCHOR_KEYS`+`HEURISTIC_LABELS` 原子 +15/+15 (`_lg` 15 自动派生); `stata/09_label_strategic.do` capture+foreach (full/ctx)。
- 模板: `14_table5`/`30_figure1`/`10_table1` (forvalues→`foreach of numlist 3/7 10(10)50` + reghdfe capture + 30_figure1 coefplot 动态构建); `strategic_differentiation.do` (numlist+esttab 动态+注释)。
- paper: `paper_spec.yaml` (claim/enrichment/alternative/exploratory/families.n_neighbor +非char探索性口径+n5双角色注); `figures.py`/`tables.py`/`__init__.py`; `README.md`。

**验证 (全绿)**:
- `test_embedding_coprimary_parity` (含新 4 组): PASS; `test_omni_fix_strategic` (含 TestTopKNExpansion): PASS (50); `test_25_audit`/`test_dual_compute_coverage`/`test_paper_figures_ext`: PASS; `test_40_panel_export_main` (dup-key/coverage/P2-D): PASS; `test_dag_consistency`/`test_paper_spec_schema`: PASS。
- **e2e smoke** (12 银行合成 + emb mock): 净增**恰 75 列**; 全方法×全轨代表列齐备; N-logic (n10 finite@peers11 / n20 NaN@peers11); **parity 0 违例** (real output); 值域断言不抛; `build_variable_labels` `_lg` 派生 Qwen↔large 正确 (含 ctx/ss lg-before-track)。
- `ruff check` 8 改动 py: All checks passed。
- 已知**既存红灯 (非本次)**: `test_papers_b_route` 的 bank_fintech_locus/substance 缺 `output/` 空目录 (git 不跟空目录, 与 strategic_diff 无关); golden `test_column_hashes_match_golden` 既存分叉红灯 (盘 3144 vs golden 2787, DEFERRED)。

**未落盘/待后续**: golden 重生 (Q3 DEFERRED 生产机); 手稿 FWER 稀释+n5 双角色 prose (§8 待写, 非机械); 40 面板 parquet 重跑使 75 列落盘 (DEFERRED, char/word/LDA 本地 + emb 缓存命中 $0)。
