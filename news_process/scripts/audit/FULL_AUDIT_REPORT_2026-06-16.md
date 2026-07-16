# 顶刊审计合并报告 — Stata / 文档 / 注释三轨缺陷清单

> 范围：本项目 Stata do-file 模板、文档(CLAUDE.md / manuscript / README / 审计报告)、代码注释。
> 已对抗验证(误报已剔除)。下文已**按根因去重**：同一根错误在多 unit 重复出现的，合并为一条并列出全部受影响文件。

---

## 一、执行摘要 (Executive Summary)

### 严重度 × 轨道计数

| 严重度 | Stata | 文档(doc) | 注释(comment) | 合计(去重后条目) |
|--------|------:|---------:|--------------:|------:|
| **P0** | 3 | 1 | 0 | **4** |
| **P1** | 6 | 13 | 6 | **25** |
| **P2** | 14 | 13 | 13 | **40** |
| **P3** | 17 | 4 | 9 | **30** |
| **合计** | **40** | **31** | **28** | **99** |

> 说明：去重前 verified findings 共 130 条。本报告把"stage 49 已删却仍被引用""digital_frontier 被 bank FE 吸收""三轨 _ss 未落 Stata/文档""模板计数过期""ivreghdfe r301 回退缺失""标准头部缺失""Stock-Yogo maximal-bias 误用""模板文件不自加载/无 set maxvar""replication 包 .do 计数"等同根因簇各合并为一条。99 条去重项中，纯 P3 共 30 条系 cosmetic（行号漂移/计数过期/标准头部），verifier 已 pass-through 未逐条复核。

### 总体裁决 (Overall Verdict)

**当前文档/注释/Stata 层尚未达到"可投稿洁净"，须先修复 4 个 P0 + 优先处理 P1 簇。** 核心问题不是大面积错误，而是**两类系统性"声明-实现/文档漂移"**：

1. **`stage 49` 已删但被多处硬引用**（P0 簇）——两篇 provisional 论文的 replication 包 + README 仍把已删除的 `49_risk_taking_outcomes.dta` 作为**首行无守卫 `use`** 的基础数据集，且 README 把它列为复现硬前置。外部复现者一跑就 r(601) 崩溃 + /b 卡"Done"框。
2. **`digital_frontier` 被 bank FE 吸收却仍报头条系数**（P1，主线 9 模板）——主回归的 headline 变量是 base-year 固定的银行级 0/1 分组，与 `absorb(bank_id)` 完全共线被 reghdfe 静默丢弃，M2-M6 整行空白却无任何披露。
3. **第三轨 `_ss`（v3.9.0 全平价）未落到 Stata IV 模板与多处文档**——主线 IV 表、coefplot、benefit/substance IV 表、llm_peer 主 IV 表均只覆盖 full/ctx 两轨；并触发一个 P0 标签 bug：`gemini311_*`(三个1) 在 `stata/` 标签文件里硬引用，但生产列名是 `gemini31111`(五个1)，跑真面板 r(111)。
4. **Stata 启动守卫缺失**（P0/P1/P2）——`stata/99_master.do` 无终端 `exit, clear`、`15_label_supplementary.do` 引用不存在的文件 → label 链 r(601) 崩溃 + /b 卡框。
5. **Stock-Yogo "maximal bias" 在 just-identified 列被系统性误用**（P2 簇）——多个 just-ID 单工具 2SLS 列把 16.38 标为"5% maximal bias"，而该判据数学上只对 over-id(≥3 工具)定义。

最高优先级的 5 项：**P0-簇-1(stage49)、P0-A(gemini 标签)、P0-B(99_master 启动守卫)、P1-A(digital_frontier 吸收)、P1-B(_ss 三轨缺口)**。

---

## 二、P0 — 阻断级（必须先修）

### P0-簇-1 ｜`stage 49` 已删除但被 replication 包/README 硬引用为基础数据集
**轨道：Stata + doc** ｜ 合并自 **S10-01, S10-02, S12-001, S12-002, D5-01, D5-02**（同一根因，跨两篇 provisional 论文）

- **受影响文件**（共 6 个 .do + 2 个 README + 2 个源模板）：
  - `papers/bank_news_clarity/stata_templates/01_data_prep.do.tmpl:9`（源模板）
  - `papers/bank_news_clarity/replication/code/01_data_prep.do:9` / `11_table2_main_clarity_risk.do:29` / `13_table4_heterogeneity.do:14`
  - `papers/bank_media_disagreement/stata_templates/01_data_prep.do.tmpl:18`（源模板）
  - `papers/bank_media_disagreement/replication/code/01_data_prep.do:18` / `11_table2_main_disagreement_risk.do:26` / `13_table4_heterogeneity.do:13`
  - `papers/bank_news_clarity/replication/README.md:L8-13,L47`
  - `papers/bank_media_disagreement/replication/README.md:L10-13,L47`
- **错误**：上述文件以**无 `capture` 守卫**的 `use "data/processed/49_risk_taking_outcomes.dta", clear` 作为首个数据加载行；README 把"stage 49 已跑且 .dta 已生成"列为复现硬前置；注释称"risk_taking_outcomes.py main 已 pyreadstat 导出"。
- **真相**：stage 49 (risk_taking_outcomes) 于 2026-06-12 **整体移除**——`pipeline/panel/risk_taking_outcomes.py`、shim `49_*.py`、`49_risk_taking_outcomes.dta` 均不存在；`core/dag.py` / `core/schemas.py` 零 49 注册；`z_score` 等无任何生产者，仅作占位变量名保留。该文件**永远不会再生成**（非"财务数据待补"的 wire-ahead）。首行无守卫 `use` 即 r(601) 崩溃；master 用裸 `do` 调 01_data_prep → 整链中止，未到终端 `exit, clear` → /b 卡"Done"框。
- **修复**：
  1. 将所有 6 个 .do（含 2 个源 `.tmpl`，改后重新实例化）的基础加载从 `49_risk_taking_outcomes.dta` 改为 **`data/processed/46_panel_yearly_full.dta`**（OUTPUT_REGISTRY 唯一 .dta 产物；注意**不是** `40_panel_yearly.dta`——那是 parquet）；表级 .do 改读 `_paperNN_working.dta`（01_data_prep 已保存的工作集）。
  2. 给基础 `use` 加 `capture` + fail-loud 提示；`z_score`/`npl_formation`/`rwa_to_ta` 改为 `capture confirm variable` 守卫（保留为占位名，符合 CLAUDE.md 保留规则）。
  3. 删除 README/注释中所有"stage 49 输出 / 已跑 / risk_taking_outcomes.py 已导出"措辞，改述真实数据源 + 财务面板待接入。

> ⚠ 注意：仅改 README 文案**不足以**修复——包仍会在首行崩溃；必须同改 `.do.tmpl` 基础 `use`。

### P0-A ｜`stata/` 标签文件硬引用不存在的 `gemini311_*` 列名（少两个"1"）
**轨道：Stata** ｜ **S11-01**

- **受影响文件**（6 个，共 47 条 `label variable`）：`stata/01_label_variables.do:25-29`、`03_label_features.do`、`11_label_washing_disag.do`、`12_label_cater_misc.do:35`、`14_label_jf_exc.do:42`、`15_label_complete.do`。（finding 误列 `05_label_advanced.do`，该文件实际 0 处。）
- **错误**：47 条无 `capture` 守卫的 `label variable gemini311_...`（三个"1"）。
- **真相**：LLM 权威 short_name 是 **`gemini31111`（五个"1"）**（`config/sentiment.yaml:35`；`encode.py:55-57` LLM_MODELS；`export.py:740/892/...`；golden snapshot 列名 `gemini31111_tone_full`）。grep `gemini311[^1]` 在 `pipeline/` 零命中——无任何生产者创建 `gemini311_*` 列。`99_master.do` 以裸 `do` 调这些文件 → 首条 `label variable gemini311_...` 对真面板 r(111) 崩溃。
- **修复**：把 6 个文件中全部 `gemini311_` token 改为 `gemini31111_`。**优选**：弃用此手维护标签集，改用 stage 46 自动生成的 `46_panel_yearly_labels.do`（已用正确名）。至少给 label 语句加 `capture`。

### P0-B ｜`stata/99_master.do` 引用不存在的 `15_label_supplementary.do` + 缺终端 `exit, clear`
**轨道：Stata** ｜ 合并自 **S11-03, S11-06**

- **受影响文件**：`stata/99_master.do:130-131`（broken ref）+ 文件末尾（无 exit）。
- **错误 1**（broken-ref，S11-03）：line 130-131 `do "stata/15_label_supplementary.do"`，但磁盘上只有 `15_label_complete.do`（无 `_supplementary`）。无守卫 `do` → r(601) 文件未找到，整 master 在 final save 前中止。
- **错误 2**（启动守卫，S11-06）：`99_master.do` 是顶层 master（直接调用，非被上层 master 调），保存 `40_panel_yearly_labeled.dta`，但文件末尾无终端 `exit, clear`。/b 批处理跑到末尾后卡"Done"模态框。
- **修复**：
  1. line 130-131 改为引用 `15_label_complete.do`（display 字符串 + do 语句同改）。
  2. 文件末尾追加 `exit, clear`（**只加在 99_master，绝不加进被调子脚本 01..15**）。

---

## 三、P1 — 高优先级

### —— Stata 轨 ——

### P1-A ｜`digital_frontier` 被 bank FE 吸收却仍报为头条系数（未披露）
**轨道：Stata** ｜ **S1-01**（受影响 9 个主线模板）

- **受影响文件**：`papers/_common/stata_templates/11_table2_main_m1m6.do.tmpl:100-135`（M2-M6），同型 pattern 见 `13_table4`(HET1/HET3)、`14_table5`、`21_tableA2`、`24_tableA5`、`26_tableA7`、`32_tableA8`、`33_tableA9`、`34_tableA11`(Panel A)。
- **错误**：M2-M6 跑 `reghdfe DV digital_frontier ..., absorb(bank_id year)`，全表报 `digital_frontier` 为 headline。
- **真相**：`digital_frontier` 是 base-year 中位数分割、**组员资格跨年固定**的银行级 0/1（`runner.py:1138 _base_year_median_split`），故在银行内时不变，与 `absorb(bank_id)` 完全共线，被 reghdfe 在每个 bank-FE 列静默丢弃。只有 M1（noabsorb）能识别其系数。从未披露。内部矛盾：`13_table4` HET2 (lines 46-49) 在按它分样本时**主动从 RHS 删掉** `digital_frontier`，证明团队知道它是 bank-constant。referee 复跑会发现 M2-M6 headline 行空白/被删。`32_tableA8`（"FE 阶梯上 β 稳定性"）按现写法完全空洞——每级都吸收 `digital_frontier`。
- **修复**（两者都做）：
  - (a) 在 `11_table2` 及全部下游 FE 表加表注：β(digital_frontier) 仅在 no-FE 列(M1)识别，bank FE 列被吸收，那些列只识别 within-bank 时变的 LOCUS/SUBST 控制；
  - (b) 横截面处理效应为真正目标处，重构为 within-bank 时变形式 `c.digital_frontier##i.year`（或 `##i.era`，如 `34_tableA11` Panel B line 158 已正确做），或对 headline 列去 bank FE。同步修 `34_tableA11` Panel A (lines 115-116)。

### P1-B ｜第三轨 `_ss`（v3.9.0 全平价）未落到主线/各论文 IV 表与 coefplot
**轨道：Stata** ｜ 合并自 **S1-02, BS-07, S4-03, S6-collab(uniform), LP-S8-02, S5-locus(uniform)** 的 _ss 缺口簇

- **受影响文件**：
  - `papers/_common/stata_templates/31_figure_coefplot_dual.do.tmpl`（S1-02：loop 仍 `full ctx`，缺 4 个 ss spec；header 仍 v3.2.0；注释"8 specs"应为 12）
  - `papers/_common/stata_templates/llm_peer/11_table2_main_iv_2sls.do.tmpl`（LP-S8-02：M3/M4/M5 仅 full+ctx，无 M6 ss；paper_spec ss_mirror 声明却未实现；`derivative_replication.py:197` 注释称的 `foreach sent in full ctx ss` 不存在）
  - `papers/_common/stata_templates/benefit_society/25_tableA12_iv_2sls.do.tmpl`（BS-07）
  - `papers/_common/stata_templates/bank_fintech_substance/22_substance_iv_2sls.do.tmpl`（S4-03）
  - locus/20 与 collab/21 IV 模板同样 full+ctx-only（系统性遗漏）
- **错误**：`_ss`（银行+金科同句）已是 v3.9.0 全平价第三主轨且其工具列(`lpeer_*_iv_ss`)与处理列(`*_frac_ss`)真实生产，但上述 IV/coefplot 模板只覆盖两轨。referee 看到 Table A2 有 12 列、coefplot 只有 8 点；IV 表声称三轨平价却只 instrument 两轨。
- **修复**（按表类型选）：
  - **coefplot(31)**：loop `full ctx` → `full ctx ss`（含 estimate loop line 20 + gather loop line 55），"8 specs"→"12 specs"，header bump；已有 `capture confirm`/动态过滤会自动优雅降级。
  - **IV 表**：优选最小披露——加 header 注说明 ss 轨 IV 在主同句/spec-switch 表(21_tableA2)报告、本表刻意不重复；或加 capture-guarded ss just-ID 列镜像 ctx 块。**铁律：full×ctx×ss 严禁拼进同一 over-id Hansen J，各 just-identified 并排。**
  - llm_peer/11 加 M6 ss 列（`ivreghdfe ... (TONE_VAR_SS = llm_peer_tone_iv_ss)`）或降级 spec/tables/CLAUDE 声明。

### P1-C ｜FE 标注 stale：表注/注释写 `bank_type FE`，代码实为 `absorb(bank_id year)`（SPEC IV-1 遗留）
**轨道：Stata + comment** ｜ 合并自 **BS-01, BS-02, BS-03, BS-04**（benefit_society SPEC IV-1 迁移遗留簇）

- **受影响文件**：
  - `benefit_society/26_tableA13_fe_robust_oster.do.tmpl:95-101,292`（comment+addnotes，称"主表用 bank_type FE / M0 是 over-baseline"）
  - `benefit_society/18_table9_dimension_decomposition.do.tmpl:102`（addnotes "bank_type/year FE"）
  - `benefit_society/22_tableA9_external_validation.do.tmpl:81`（addnotes "Bank-type/year FE"）
  - `benefit_society/15_table6_effect_size.do.tmpl:24`（inline comment "bank-type FE 规格"）
- **错误**：上述表注/注释声称用 `bank_type FE`，但代码全部 `absorb(bank_id year)`（bank+year FE）。
- **真相**：SPEC IV-1（2026-06-14/15）已把主表/稳健性/附录 FE 升级为 `absorb(bank_id year)`（`paper_spec.yaml:52`；`11_table2_main:17-23`；`14_table5:12-15`）；**仅 `13_table4_heterogeneity` 刻意保留 bank_type FE**。代码改了但表注/注释漏更。published 表注误导 referee 对识别策略的理解。26_tableA13 的"M0 是 over-baseline"框架也作废（M0 即等于主表 FE）。
- **修复**：把这些 FE 标签全部改为 `bank (bank_id) + year FE`；26_tableA13 改述为"M0 复现主 FE，后续列在其上饱和 province/type/zone×year + bank trends"，删 over-baseline 框架与对 `11_table2` 的错误交叉引用。

### P1-D ｜esttab 硬点名缺名 → r(111) 丢整表（个别模板未做动态名单化）
**轨道：Stata** ｜ 合并自 **S1-03(24_tableA5), S5-locus-04(19_locus_clarity), S6-collab-03(20_collab_clarity)**

- **受影响文件**：
  - `24_tableA5_dictionary_method.do.tmpl:62-71`（自披露"仍硬点名 6 个估计，尚未动态化"）
  - `bank_fintech_locus/19_locus_clarity_robustness.do.tmpl:39`
  - `bank_fintech_collab/20_collab_clarity_robustness.do.tmpl:39-42`
- **错误**：eststo 全部在 `capture confirm variable ...` 守卫下条件存储，但最后 `esttab name1 name2 ...` 硬点名。若任一列缺失→该 estimate 未存储→esttab 引用不存在的估计名 r(111)，丢整表（master `capture noisily` 下静默丢表而非崩链）。
- **真相**：列对应的产生者（dict 列、`mean_clarity_score_full`）在生产面板真实存在，故生产不触发；但与目录内已确立的动态名单化 idiom（`12_table3:78-92`、`13_table4:67-81`、`21_tableA2:98-115` 的 `qui estimates dir`→`list m in stored`）不一致，T=2/部分构建时静默丢表。
- **修复**：套用同目录的动态名单化模式——`qui estimates dir` → `local stored r(names)` → 仅对 stored 的估计 build models/mtitles，空时 [WARN] 跳过。（注意 collab/20 由 `capture do`(无 noisily)调用，须用 in-file `display` 而非依赖 master 回显。）

### P1-E ｜brokerage 13/14 缺 `ivreghdfe→ivreg2` 回退，外部机器上两表静默消失
**轨道：Stata** ｜ **BRK-02**

- **受影响文件**：`brokerage_network/13_table4_heterogeneity.do.tmpl:21-25`、`14_table5_robustness.do.tmpl:22-26`。
- **错误**：两表 `capture which ivreghdfe / if _rc { exit 199 }` 后无 ivreg2 替代路径，而兄弟表 11/17/18/19/24 都有 IV-6 `ivreghdfe→ivreg2+i.bank_id i.year` 运行期回退。
- **真相**（verifier 修正措辞）：本机经 2026-06-15 `require` 安装后 ivreghdfe r301 已修、13/14 现能产出；但**任何 ivreghdfe 损坏的机器（如未装 `require` 的外部复现者）**上，11/17/18/19/24 优雅降级而 13/14 hard-`exit 199` → Table 4/5 静默消失（master `capture noisily` 保链但跳表）。是**条件性 portability/resilience 缺口**，非"必然丢失"。
- **修复**：把 IV-6 回退扩展到 13/14（用 `ivreg2 ... i.bank_id i.year, cluster() first` + 动态 esttab + 保 widstat/ffirst），如 `11_table2:33-52`/`17_table8:31-56`；或在 master/表注披露两表需可用 ivreghdfe。

### P1-F ｜`test` 未守卫且跑在错误模型上 → 主结果表(Table 2)整表不产出
**轨道：Stata** ｜ **S5-locus-01**

- **受影响文件**：`bank_fintech_locus/15_locus_main_regression.do.tmpl:74`（+ 镜像 `bank_fintech_collab/15_collab_main_regression.do.tmpl:73`）。
- **错误**：line 74 `test locus_layer_full = locus_scenario_full`（无 `capture`）跑在内存中最后一个估计 M6_gap 上，而 M6_gap 的 RHS 只有 `locus_gap`（+控制），不含被测两系数 → r(111)。无 `capture` 故 do-file 在 esttab(lines 94-106)前中止 → **Table 2(主结果表)永不写出**。M6_gap 因 `01_data_prep:67` 无条件 gen `locus_gap` 而**每次生产运行必触发**（StataNow 19.5 /b probe 已实测中止）。
- **修复**：line 74 前插 `capture estimates restore M5`（fallback M4），并改 `capture noisily test locus_layer_full = locus_scenario_full`（noisily 保日志可见、capture 防中止）；或把 test 移到 M5 reghdfe 后、M6_gap 块前。collab/15:73 同步修。

### P1-G ｜事件研究遗漏全部 lead 项 → 无平行趋势检验（名实不符）
**轨道：Stata** ｜ **S6-collab-01**

- **受影响文件**：`bank_fintech_collab/19_collab_event_study.do.tmpl:40-65`。
- **错误**：生成 `event_t_*_0.._6`(t=-3..+3)，但回归(lines 51-54)只交互 `_3/_4/_5/_6`(t≥0)；三个 lead 哑变量 `_0/_1/_2`(t=-3/-2/-1)生成后**从未进 reghdfe**=死代码。header 自称"event study / lead/lag(-3~+3)"，实为 post-only dynamic-DiD，无前趋检验、无 omitted base period。
- **真相**：显式命名的镜像模板 `locus/19_locus_event_study.do.tmpl` **正确**做了 lead 交互(lines 61-66)+omit 事件年 base+前趋联合 F(lines 72-82)。collab/19 是缺陷的那个。
- **修复**：采纳选项(a)，对齐 locus/19——加 `c.collab_open_full#i.event_t_*_0/_1/_2` lead 交互、omit `_3`(t=0)为 base、加前趋联合 F 检验并 estadd。$0/golden-safe，纯模板改。

### P1-H ｜`mechanism` 表 outcome header 标错（CAR 主 vs citation_weighted_patent 主）
**轨道：comment** ｜ **S5-locus-02**

- **受影响文件**：`bank_fintech_locus/16_locus_mechanism.do.tmpl:8`。
- **错误**：header line 8 `Y = {{MAIN_DV}} (car_5day_window 主) + patent_fintech_count (secondary)`。
- **真相**：`{{MAIN_DV}}` 解析为 `citation_weighted_patent`（`derivative_replication.py:255`；`paper_spec.yaml:30 primary`）；2026-06-13 outcome 重定位把 CAR 降为 listed-subsample 扩展。兄弟模板 15/20 已正确标注，唯 16 是 pre-redesign 残留。
- **修复**：line 8 改为 `Y = {{MAIN_DV}} (= citation_weighted_patent, Kogan 2017; car_5day_window 降级上市行扩展) + patent_fintech_count (secondary)`。

### P1-I ｜wave 异质性维度被文档/表注承诺却永不执行（无生产者，可内联派生）
**轨道：Stata** ｜ **S5-locus-03**

- **受影响文件**：`bank_fintech_locus/17_locus_heterogeneity.do.tmpl:6-8,29-55,107`（兄弟 `substance/17`、`attention/17` 同型）。
- **错误**：header 把 fintech-wave 异质性列为第一异质性维度，Panel(a) loop 与 wave×layer 交互消费 `pre_period wave_1 wave_2 consolidation wave_3`，addnotes 描述如已产出。
- **真相**：无任何生产者创建这些 wave 列（grep `pipeline/*.py` + 全部 `01_data_prep.do.tmpl` 零命中）；spec 只定义年份区间映射(`paper_spec.yaml:160-165`)。故 Panel(a)+layer×wave 在每次运行(含生产 T=19)永久静默跳过，却被文档/addnotes 当 live 呈现。可内联派生（同 `25_locus_era_stability:90-94` 从 year 派生 era）。
- **修复**（优选内联派生）：`use ... clear` 后插 `gen byte wave_1=inrange(year,2013,2015)` 等（年份区间见 spec），使 Panel(a)+交互真正运行；或在 header/addnotes 明确披露 wave 异质性为 inert wire-ahead。同步修 substance/17、attention/17。

### —— 文档轨 ——

### P1-J ｜CLAUDE.md `doctor` 段数过期（5→6）
**轨道：doc** ｜ **D1-01**

- **受影响文件**：`CLAUDE.md:70`。
- **错误**："`doctor`: 5 段诊断 (deps + pipeline + LLM + Stata bin)"。
- **真相**：`stata_runner.py` doctor 实有 6 段：[1/6]Python依赖、[2/6]Pipeline、[3/6]LLM cache、[4/6]LLM API、[5/6]Stata bin、[6/6]Stata ado 包(2026-06-15 加)。
- **修复**：改为"6 段诊断 (Python 依赖 + pipeline 数据 + LLM cache + LLM API + Stata bin + Stata ado 包)"。

### P1-K ｜CLAUDE.md P2 attention 引文已被项目主动walk-back却仍当事实
**轨道：doc** ｜ **D1-02**

- **受影响文件**：`CLAUDE.md:248`。
- **错误**："bank_fintech_attention (P2): firm-level fintech attention intensity (Hassan 2019 QJE)"。
- **真相**：主处理 `attention_index_full` 锚 Fang & Peress (2009 JF) extensive 覆盖，**明确"不是 Hassan intensive 归一化份额"**（`paper_spec.yaml:12-17`；`attention_media.py:262-264`；`figures.py:40-41` fix omni-g-papers-misc-09）。Hassan 2019 QJE 仅用于归一化稳健度量(attention_pct/density)与 outcome 范式。
- **修复**：改为"firm-level fintech attention; main = attention_index_full (Fang-Peress 2009 JF extensive coverage; Hassan 2019 QJE 仅用于归一化稳健度量与 outcome 范式)"。

### P1-L ｜论文 README 主因变量/主处理列标错（与 spec+模板矛盾）
**轨道：doc** ｜ 合并自 **D3-02, D3-03, D5-04, D5-05**（outcome/treatment 重定位遗留簇）+ **D3-01**(attention 列状态错)

- **受影响文件**：
  - `papers_assets/bank_fintech_locus/README.md:49-50`（D3-02：MAIN_DV 标 car_5day_window，应为 citation_weighted_patent）
  - `papers/_common/stata_templates/bank_fintech_locus/README.md:31`（D5-05：同上）
  - `papers_assets/bank_fintech_substance/README.md:56-57`（D3-03：MAIN_TREAT 标 article-level `innovation_substantiveness_full`，应为 panel `sub_frac`）
  - `papers/_common/stata_templates/bank_fintech_substance/README.md:32`（D5-04：MAIN_DV 标 long_run_roa_change_3yr，应为 cost_income_ratio_change_3yr）
  - `papers_assets/bank_fintech_attention/README.md:19`（D3-01：称 attention_index_full"尚未物化"，与同文 L55 称其为 MAIN_TREAT 自相矛盾；实已由 `attention_media.py:450-452` 物化）
- **错误/真相**：README 标注的主因变量/主处理列与权威 spec + `derivative_replication.py` 默认值 + 模板 header 全部矛盾，多为 2026-06-13 outcome/treatment 重定位的遗留 stale。复现者按 README 会 reghdfe 不存在/错粒度的列。
- **修复**：逐文件对齐 `paper_spec.yaml::outcome.primary`/`treatment.primary` 与 `derivative_replication.py`：locus MAIN_DV→`citation_weighted_patent`(car 移 listed_subsample_extension)；substance MAIN_TREAT→`sub_frac`、MAIN_DV→`cost_income_ratio_change_3yr`；attention README 删"尚未物化"、区分 firm-level(attention_media.py)与 geographic ratio 族。

### P1-M ｜论文 README brokerage 引文捏造作者 + 模板计数过期
**轨道：doc** ｜ 合并自 **D3-04, D5-03(主线14→19), D5-06/07/08/09**(子目录模板计数)

- **D3-04（引文，受影响 `papers_assets/brokerage_network/README.md:61` + `drafts/en|zh/refs.bib:61` + `do/network_causal.do:208,316`）**：标 "Han, Kim, Nanda, **& Ramadorai** (2024) RFS 37(9)"，捏造第 4 作者。权威源 `network_brokerage.py:24` 为三作者 "Han, Kim & Nanda (2024). RFS 37(9), 2903-2935, DOI 10.1093/rfs/hhae026"。**修复**：删 Ramadorai。
- **D5-03（主线复现包 .do 计数）`papers/_common/stata_templates/README.md:L77,L92,L102`**：称"14/14 模板"，实 19（CLI/包输出会打印 19，矛盾）。漏 25/26/32/33/34 五个新模板。**修复**：14→19 并补 5 行。
- **D5-06/07/08/09（子目录 Template inventory 计数）**：attention `README.md:L8` 7→10、locus 8→14、substance 9→14、brokerage 8→18（均漏 IV 补全/顶刊稳健性扩充新增模板）。**修复**：按 `CLAUDE.md:308` 权威计数刷新并补缺行。

### —— 注释轨 ——

### P1-N ｜`core/dag.py` 引文作者名错(Shapiro→Kelly)
**轨道：comment** ｜ **C1-001**

- **受影响文件**：`core/dag.py:282`（+ copy-paste 孪生 `config/sentiment.yaml:320`）。
- **错误**："Gentzkow-Shapiro-Taddy (2019) JEL"。
- **真相**：2019 JEL "Text as Data" 作者是 **Gentzkow, Kelly, Taddy**（非 Shapiro；后者是 G&S 2010 ECMA 另一篇）。全库其余处均正确(news_bank.py:30-31 等)，有专门回归锁测试守卫，唯 dag.py/yaml 漏改。
- **修复**：两处 "Gentzkow-Shapiro-Taddy" → "Gentzkow-Kelly-Taddy"。Tetlock(2011)同行部分正确不动。

### P1-O ｜`token_utils.py` 编造术语 "Early Chunking" + 反向归因 arXiv:2409.04701
**轨道：comment** ｜ **C1-002**

- **受影响文件**：`core/text/token_utils.py:57`（+ 孪生 `pipeline/filtering/policy_alignment.py:91`、`scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md:270`）。
- **错误**：docstring 称 "Early Chunking (Günther et al., 2024, arXiv:2409.04701)"，描述为"先固定切分→各段独立嵌入→均值池化"。
- **真相**：arXiv:2409.04701 标题是 **"Late Chunking"**（"Early Chunking" 是编造术语）；且该论文**批判**的正是这种 naive 独立分块基线，Late Chunking 是先嵌全文再切。代码(token_utils.py:61-67)实现的就是 naive 独立分块。
- **修复**：改标为 naive/independent fixed-window chunking，**删除** Late Chunking 引文（或换通用 long-text pooling 引用）。三处同步。

### P1-P ｜benefit `shrinkage.py` 注释声称 `benefit_mean_ss` 不存在（已三轨化）
**轨道：comment** ｜ **C6-03**

- **受影响文件**：`papers/benefit_society/shrinkage.py:294-296`。
- **错误**：注释"无 benefit_mean_ss → 收缩仍 full/ctx 两轨"，断言 ss 切片延后。
- **真相**：`pipeline/features/benefit_society.py:751` 现 `for track in ['full','ctx','ss']`，确实产出 `benefit_mean_ss`(+_t2v 孪生)；live 消费者 `derivative_replication.py:98`、`tables.py:24`、`paper_spec.yaml:78,110`、`iv_extensions.py:597-616` 均引用之。CLI 仅跑 full/ctx 本身没问题，但**理由错**。
- **修复**：注释改为"benefit_mean_ss 现已三轨产出；本收缩 CLI 刻意仅 full/ctx（ss 收缩超本 CLI 范围）"。

### P1-Q ｜benefit/disagreement README Status 自称"已刷新至当前态"却报旧计数
**轨道：doc** ｜ 合并自 **D3-05**（self-contradicting）

- **受影响文件**：`papers_assets/benefit_society/README.md:3,35`。
- **错误**：Status header 写"计数已刷新至当前态…Stata 22 模板"，但目录实 26 .do.tmpl（漏 25/26/27/28_tableA12-A15）。因 header 显式断言 current，是**当前态事实错**而非历史快照。
- **修复**：22→26 并补 4 行，或去掉"已刷新至当前态"声明。

### —— 注释/文档轨（其余 P1）——

### P1-R ｜D4 审计报告 `PIPELINE_NUMBERED_PY_REFERENCE` 计数 pre-12b（被 MEMORY 引为权威却 stale）
**轨道：doc** ｜ **D4-01**

- **受影响文件**：`scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md:3,5` + overview 表 15-48。
- **错误**：称"34 个 NN_*.py…31 注册=15 STAGES_MAIN+16 VALIDATION"，overview 表 34 行整体遗漏 `12b_cooccurrence_filter.py`。
- **真相**：v3.10.0(同日 12b)后实为 **35 shim / 32 注册 = 16 MAIN + 16 VALIDATION**；12b 已在 dag.py:187 + OUTPUT_REGISTRY 注册。代码一致，仅文档滞后；该文档被 MEMORY.md 引为"权威参考"。
- **修复**：header 改 35/32/16+16，补 12b overview 行 + 完整 section；或加 pre-12b 快照注。

### P1-S ｜V6_METHODOLOGY_CHANGES.md "single account" 数据基建表述已失实（写论文必读 boilerplate）
**轨道：doc** ｜ **D2-01**

- **受影响文件**：`papers_assets/V6_METHODOLOGY_CHANGES.md:23-30`。
- **错误**：建议方法章节措辞"All three routed through yunwu.ai aggregator (single account, identical schema)"。
- **真相**：现 config 只 OpenAI+Google 经 yunwu；**DeepSeek 经自有直连 `api.deepseek.com` + 独立 `DEEPSEEK_API_KEY`**（`sentiment.yaml:25-27,39-43`；`.env.example:23`）——非"single account"。该文档是"写论文必读"逐字 boilerplate，会把错误基建表述带进投稿。
- **修复**：改为 OpenAI/Google 经 yunwu(YUNWU_API_KEY)、DeepSeek 经 api.deepseek.com(独立 key)，删"single account, identical schema"。

### P1-T ｜manuscript 引用不存在的 .dta 文件名
**轨道：doc** ｜ **D2-02**

- **受影响文件**：`papers_assets/bank_fintech_collab/manuscript_en.md:50`。
- **错误**："pipeline produces 46_panel_yearly_v34.dta"。
- **真相**：stage 46 产单一 `46_panel_yearly_full.dta`（`core/schemas.py:86`；`stata_export.py`）；无 `_v34.dta` 生产者。复现者找不到。zh 孪生(:50)只描述形状、正确。
- **修复**：`46_panel_yearly_v34.dta` → `46_panel_yearly_full.dta`（或同 zh 只述形状）。

### P1-U ｜`stata/14_label_jf_exc.do` 把 Janis-Fadner 误标 "Jaffe-Feldman"
**轨道：Stata** ｜ **S11-05**

- **受影响文件**：`stata/14_label_jf_exc.do:9`。
- **错误**：section header "42. JF系数 (Jaffe-Feldman Coefficient)"。
- **真相**：JF = **Janis-Fadner** 不平衡系数（`runner.py:2013-2014` 引 Janis & Fadner 1965 + Deephouse 2000；`export.py:854` 中性标 "JF Coefficient"，且含 2026-06-05 erratum 纠正过同类错）。"Jaffe-Feldman" 是捏造作者对。
- **修复**：改为 "JF系数 (Janis-Fadner imbalance coefficient; Janis and Fadner 1965; Deephouse 2000, J. of Management 26(6):1091-1112)"。

### P1-V ｜`stata/` 标签集残留已删 `_title` 轨空 section
**轨道：comment** ｜ **S11-08**

- **受影响文件**：`stata/01_label_variables.do:54`、`stata/05_label_advanced.do:61-64`。
- **错误**："2.3 标题轨道 (_title)" / "14. 标题-全文情感差异" 空 section header。
- **真相**：独立 `_title` 情感轨 v3.8.0 BREAKING 删除（`encode.py:699,1976` "remove-title-track…已取消"）。空 header 在 active label 流水线中是 reader-facing 死注释。
- **修复**：删两个 header，或改注 "remove-title-track: 标题情感轨已停产 (v3.8.0)"。

### P1-W ｜provisional 论文模板/注释残留 stage-49 / FE / 引文错（非 P0 的 spec/disclosure 层）
**轨道：Stata + comment** ｜ 合并自 **S10-03, S10-04, C6-02**

- **S10-03（同名异构 DV，`bank_media_disagreement/11_table2:37` + 12_table3:50 + 13_table4:19）**：TX=`cross_outlet_tone_variance_full` 当 paper spec 主处理，但唯一生产者是 stage 39f `cross_media_alpha.py`，其 docstring 明示"同名异构"（事件窗条件 vs spec 全年无条件）、"采用前必须对齐或重命名"。模板逐字消费无披露。**修复**：加表注披露是 39f 事件窗构造非 spec 全年构造，或新建 spec 构造换名。
- **S10-04（few-cluster 推断，clarity+disagreement `11_table2`）**：主 Table 2 全用 `vce(cluster bank_id year)` 双向聚类、addnotes 无 few-cluster 警示、无 wild bootstrap；但 G_year=13(生产)/2(盘面) 远低阈值，spec `small_g_inference` 与稳健性表 14/15 都已披露并建议 boottest，唯主表漏。**修复**：主 Table 2 加 few-cluster 披露 + headline M5/M6 报 boottest wild-cluster p（disagreement 篇须新增 boottest）。
- **C6-02（`papers/brokerage_network/__init__.py:7`）**：标 "Han, Jiang, Zhang & Zhu 2024"，捏造作者；权威 = Han, Kim & Nanda 2024（同 D3-04）。**修复**：改 "Han, Kim & Nanda 2024 (RFS)"；`run_paper.py:74` 同型同步。

### P1-X ｜llm_peer B2 滞后列偷换工具(co-mention vs LLM-semantic peer)
**轨道：Stata** ｜ **LP-S8-01**

- **受影响文件**：`papers/_common/stata_templates/llm_peer/17_tableA8_subsample_timing.do.tmpl:350-371,442`。
- **错误**：B2 注释称 `peer_tone_lag1_full` 为滞后"peer-IV"，用它 instrument 自身滞后 tone；表注框架为"LLM-peer IV timing"。
- **真相**：`peer_tone_lag1_full` 由 co-mention 网络 spillover(`network_spillover.py:383`)产生，与 headline 的 LLM-语义-peer 工具 `llm_peer_tone_iv_full`(`llm_peer_iv.py`)是**不同 peer 构造**。B2 的 fallback 分支(line 386)反而正确用 `L.IV`——同列两分支用两种构造。表标题 "LLM-peer IV" 对 B2 失实。
- **修复**：B2 preferred 分支改 `(L.TONE = L.IV)`（镜像 B1/B3 与 fallback）；若刻意保留 co-mention 工具，须在注释+表标题明确披露 B2 用 co-mention 网络 peer 而非 LLM-语义-peer。

---

## 四、P2 — 中优先级

> 多为内部不一致/披露缺口/引文期刊错/启动守卫/计数过期，不阻断但顶刊 referee 会注意。以下按根因簇合并。

### —— Stata 轨 ——

### P2-1 ｜Stock-Yogo "maximal bias" 在 just-identified 列被系统性误用
**轨道：Stata/comment** ｜ 合并自 **S6-collab-04, S9-ATT-03, S10-09, BRK-05**（项目已自承待订正）

- **受影响文件**：`bank_fintech_collab/21_collab_iv_2sls.do.tmpl:138,227`、`bank_fintech_attention/19_attention_iv_first_stage.do.tmpl:163`、两 provisional `12_table3_iv_2sls`(clarity:185/disagreement:199)、主线 `25_tableA6_tone_iv_2sls:266`、`benefit_society/25:199`。`brokerage_network/14_table5:89-90` 已用正确"maximal-size 16.38"且**自承"主线 25_tableA6 的 5% maximal bias 措辞待订正"**。
- **错误**：just-ID 单工具列把 16.38 标为"Stock-Yogo 5% maximal bias"。
- **真相**：16.38 是 just-ID(1 endog,1 IV)的 **10% maximal-IV-size** 临界值；maximal-relative-bias 临界值数学上只对 over-id(L≥K+1，实际≥3 工具)定义。ATT-03 的 over-id 列(2 工具)正确阈值是 ~19.93。
- **修复**：just-ID 列改标 "Stock-Yogo 10% maximal-IV-size (1 instrument) = 16.38"，删"maximal bias"；over-id 列用对应工具数阈值。AR-CI 推荐(已有)保留为主推断。

### P2-2 ｜模板不自加载(继承内存)/`$data_dir` 不对称/缺 `set maxvar` 标准头部
**轨道：Stata** ｜ 合并自 **S1-05(22_tableA3), S1-06($data_dir), BS-09, BRK-03, S4-05, S7-06, D5-13(行号)** 等头部/加载簇

- **S1-05**：`22_tableA3_bartik_iv.do.tmpl` 无 `use`，继承 21_tableA2 内存状态（23/24 同），独立跑无数据。**修复**：套用 26/32/33/34 的 `capture confirm file _prepared_panel.dta→use, else 46_panel_yearly_full.dta` 自加载 idiom。
- **S1-06**：`01_data_prep.do.tmpl` save 走 `$data_dir` 但 input `use`(line 22)硬编码 `data/processed/`，且 `11_table2:40-42` 读硬编码——非对称。root 家族实际从不设 `$data_dir` 故现为 dead branch。**修复**：删 save 的 `$data_dir` else 分支统一硬编码，或端到端honor `$data_dir`。
- **头部缺 `set maxvar 32767`/`set linesize 120`**（BS-09 / BRK-03 / S4-05 / S7-06 / S5-locus-05 / S9-att/strategic 各 master+轻量子 do）：CLAUDE.md 称"全部统一头部含 set maxvar"，但 8 个 paper-specific master + 多数轻量子 do 实为 `version 19/clear all/set more off`（缺 maxvar/linesize）。当前 ~1569 列<5000 不崩。**修复**：优选**改 CLAUDE.md:308** 限定为"仅 root standalone master 带完整 4 行头"，或给子 do 补 `set maxvar 32767`。

### P2-3 ｜inference/识别 spec 缺陷（sureg 丢 FE / mgroups 静态 pattern / rwolf e() 名错）
**轨道：Stata** ｜ 合并自 **S4-01, S4-02, S4-04, S7-01**

- **S4-01（`substance/16:63-68`）**：W&Z reversal `sureg` 无 FE（sureg 不支持 absorb），与同文 FE-identified 单 outcome 列(absorb bank_id year)不一致且未披露。**修复**：FWL 残差化后 sureg，或 addnote 披露 sureg 是 pooled(no FE)定向检验。
- **S4-02（`substance/24:278-279`）**：esttab mgroups 硬编码 `pattern(0 0 0 0 0 1 0 0 1)` 与动态 models 列表脱钩，T<3/guard 触发时 panel banner 错位。**修复**：按 realized 列动态构 pattern（镜像 benefit_society/21:219-234）。
- **S4-04（`substance/18:62-64`）**：rwolf 多-indepvar 调用，e() 名应为 `e(rw_<dep>_<indep>)`/`e(RW_<indep>)`，代码读单-indepvar 名 `e(rw_sub_frac)` → Romano-Wolf p 行系统性空白。**修复**：改读多-indepvar 名 + 失败时可见提示。
- **S7-01（`strategic_diff/12_table3:33-35`）**：paper 唯一因果 IV 列(just-ID 单工具)仅报 `ffirst`，缺 KP rk F/AR CI/Stock-Yogo/排他性论证。**修复**：`estadd scalar KPF=e(widstat)` + AR CI(weakiv/ivreg2 ar) + 排他性一句话。

### P2-4 ｜标准独立性/启动守卫（standalone 缺 exit、$controls fallback、exit 199 不一致）
**轨道：Stata** ｜ 合并自 **S7-02, S8-LP-S8-03, S12-006, S12-007, S11-07**

- **S7-02（`strategic_diff/15_table6:83-132`）**：支持 standalone 加载但缺 `if "$controls"==""` fallback（兄弟 16/17/18 都有），standalone 跑时 $controls 空、Panel B/C 静默无控制变量。**修复**：load 后加 `if "$controls"=="" global controls "{{CONTROLS}}"`。
- **LP-S8-03（llm_peer 12/13/14/30）**：缺估计器时 `exit 199`(非零)经裸 `do` 上抛中止 master，与 15-18 的 `exit 0` 优雅跳过不一致。**修复**：`exit 199`→`exit 0`（含 finder 漏列的 13_table4）。
- **S12-006/007（papers_assets/*/do）**：`50_robustness_text2vec.do` 裸 `DV` 占位 → r(111)；5 个 standalone assets do 缺 `version 19`/`set maxvar`/终端 `exit, clear`，/b 卡框。**修复**：占位 DV 加 capture 守卫 + 标准头部 + 终端 exit。
- **S11-07（`stata/00_load_panel_data.do`）**：standalone loader 无终端 exit。**修复**：末尾加 `exit, clear`（无人 `do` 它，安全）。

### —— 文档轨 ——

### P2-5 ｜CLAUDE.md/注释中 stage 引用与缓存数字过期
**轨道：doc/comment** ｜ 合并自 **D1-03, D1-04, C1-003, C1-004, C1-006**

- **D1-03（`CLAUDE.md:61`）**：`_llm_cache.db` 标 "407MB/133,687 条"，实 ~453MB/~140,614 条(ss 部分播种后增长)。`tone_llms.py:67` 同步 stale（`llm_archive/__init__.py:82` 是固定历史基线，**勿改**）。**修复**：改 "~453MB/~140.6k 条(随 _ss 播种增长)"。
- **D1-04（`CLAUDE.md:238`）**：YUNWU_API_KEY 阶段列 "32a"，但 32a=dedup_threshold_sensitivity(无 LLM)。**修复**：**删 32a**（verifier 修正：勿换 32——stage 32 也无 LLM API；严格列应为 21/36/39 + embedding 15/27）。
- **C1-003/004/006**：`dag.py:247-248` herd_decay 行号漂移(实 :667)；`stata_export.py:43,1211` 引用不存在的 config key `output_45_panel_main`(应 `output_40_panel_yearly`，现靠默认值兜底)；`config.py:329-341` `return config` 后的重复死代码块。**修复**：分别更新行号引用/改 config key 名/删死代码块。

### P2-6 ｜README/文档模块行数 stale + 内部计数矛盾
**轨道：doc** ｜ 合并自 **D3-06, D3-08, D3-09, D3-10, D3-11, D3-12, D3-14, D3-15, D3-16, D5-10, D5-11, D5-12, D5-14, D2-03, D2-04**

- 这是**最大的 stale 簇**（15 项），覆盖 README 模板/模块行数计数过期与内部矛盾。代表项：
  - `papers_assets/llm_peer/README.md`：L3 "14 模板" vs L34 "8" 互相矛盾，实 12（D3-06）；L13 `llm_peer_iv 763 行` 实 1025（D3-12）。
  - `papers_assets/bank_fintech_tone/README.md`：falsification 模板 "1677 行" 实 1874（D3-09，4 处）；"14 主模板" 实 19（D3-10）。
  - `papers_assets/bank_fintech_collab/README.md`：L19 "innovation_collab_mode 为关键变量" 实应 collab_frac(D3-08/D5-14)；L65 "8 模板" 实 14(D5-12)。
  - `V6_METHODOLOGY_CHANGES.md`：F2 "10 列元数据×2 轨" 实 15 列×3 轨(D2-03)；F4 `bartik_fintech_iv_*` 陈旧键(应 `_lf_/_lc_`)(D2-04)。
  - 子目录 inventory 计数(D5-10 benefit 22→26、D5-11 llm_peer 14↔8→12 等)。
- **修复**：按 `CLAUDE.md:308` 与各 spec 逐一刷新计数/行数/列名；优选去掉脆性精确行数或改近似标记。**安全可批量直接改。**

### —— 注释轨 ——

### P2-7 ｜引文期刊/作者错（comment 层，非 manuscript load-bearing）
**轨道：comment** ｜ 合并自 **BS-08, C3-04, C3-05, C7-V-002, C8-002, C8-005, C6-07, D4-03**

- **BS-08（`benefit_society/11b:7,13`）**：MacKinnon-Webb 2017 标 "(J. Econometrics)"，应 **Econometrics Journal**（2018, 21(2)）。
- **C3-04（`tone_words.py:1522`）**：MSENT 列锚 "He et al. (2024, IRFA)"(无 DOI、项目自审标 phantom)，与同文 :1314-1325 的 Henry 2008/Tetlock 2007(有 DOI)矛盾。**修复**：改锚 Henry 2008 JBC/Tetlock 2007 JF。
- **C3-05（`tone_llms.py` 6 处 innovation_locus）**：底层/应用二元框架锚 "Gomber 2018 JMIS"，直接出处应为 **Gomber, Koch & Siering (2017) Digital Finance Cube**（项目 LITERATURE_ANCHORS 已指出）。
- **C7-V-002（`validation/threshold.py:476-477`）**：阈值稳健性 main() docstring 标 "Tetlock (2007, JF)"，同模块其余三处均为 Gentzkow-Kelly-Taddy (2019, JEL)。**修复**:统一为 GKT 2019。
- **C8-002（`scripts/audit/att_drift_simulation.py:11`）**：Andrews-Stock-Sun 2019 标 "AER"，应 **Annual Review of Economics (ARE)**（全库其余正确）。
- **C8-005（`scripts/fintech_rating_example.py:15`）**：Li et al. (2021) 标 "Management Science"，应 **RFS 34(7)**（`config/filtering.yaml:28-29`）。
- **C6-07（`bank_media_disagreement/__init__.py:16`）**：Acharya-Anginer-Warburton 标 "(2016 RFS)"，实为 SSRN working paper（spec 已用 "(2016 RFS, working)"）。
- **D4-03（`LITERATURE_ANCHORS_2026-06-13.md:219,225`）**：Bingler 2022 FRL 与 2024 JBF 两条 copy-paste 同文，2024 误标"首篇"且自引循环。
- **修复**：逐条改正期刊/作者/年份至权威源。**安全直接改。**

### P2-8 ｜注释行号漂移 / 缓存键描述不精确 / stale feature ref
**轨道：comment** ｜ 合并自 **C1-004(已并 P2-5), C3-01, C3-02, C2-01, C2-02, C2-04, C4-001, C4-002, C4-003, C5-01, C5-02, C5-03, C5-04**

- **C3-01（`herd_decay.py:622`）**："缺 ss_is_fallback→全 False" 与下行 `_ss_real=pd.Series(True)` 矛盾。**修复**：改 "_ss_real 全 True (ss_is_fallback 视作全 False)"。
- **C3-02（`tone_llms.py:67`）**："缓存键=...+temperature+seed" 无条件列 seed，但 `caching.py:255-259` 仅 temperature≠0 时入键；生产 temp=0 下 seed 不入键(决定 $0 字节级确定性)。**修复**：改 "...+temperature (+seed 仅当 temperature>0)"。
- **C2-01/02/04**：`cn_text_utils.py:97`(geography 行号 132→141-148)、:95-97(SSOT 称三原语"统一引用"实仅 is_cjk 被调)、:20-21(1000 句人工分句一致率≥95% 无 fixture 入库、是设计目标非已实现门控)。
- **C4-001/002/003**：`encode_collab.py:287`(encode.py 行号+列名 n_articles 'size' vs n_articles_llm_valid 'count' 混淆)、`export.py:324`(runner.py:1077→1598)、`codebook.py:358`(encode.py:579-588→661-684)。
- **C5-01（`ctx_materializer.py:164`）**：'内容' 消费者列表含 'topic'，但 stage 17 已于 2026-06-09 移除（同文 :60 权威列表已删 topic）。**修复**：删 'topic'。
- **C5-02/03/04**：`lexical_discriminant_validity.py:18`(inter_track_kappa 行号 41→118)、:16-17(称 "pairwise on-disk/<1GB" 实为一次性全表入内存，同文 :58 已自承)、`news_salience.py:26`(署名安全理由 stage 顺序倒置——stage 11 实**晚于**stage 00 预处理)。
- **修复**：行号改指函数名/更新行号；缓存键描述加条件；is_cjk SSOT 措辞软化；contradiction 注释改正；stale feature 删除。**多为安全直接改。**

---

## 五、P3 — 低优先级（cosmetic，verifier pass-through）

> 30 条，纯行号漂移/计数过期/标准头部/illustrative 措辞，无行为影响。可在改 P0-P2 时顺手清理，无须单独验证。代表簇：

- **行号漂移**（多为审计/注释交叉引用）：S1-07/08/09、BRK-04/05/06、S4-06/07/08、S5-locus-05/06、S7-05/06/08/09、D3-18/19/20、D4-02/04/05、C2-03/05、C4-005/006、C5-05/06/07/08、C6-05/06/08、C7-V-003/004/007、C8-003/004/006/007、D1-05、D5-13、C1-007/009。
- **标准头部缺 set maxvar**（已在 P2-2 提及的低 sev 残项）：S5-locus-05、S7-06、S9-att 等。
- **illustrative/version 措辞过期**：C3-03(`tone_llms.py:520` prompt 例 v6→v8)、C7-V-005(`radius_sensitivity_llm.py:8` v7→v8)、C7-V-001(`tone_validation.py:45` "邻域加密"编造术语→应"过采样随机抽取")、C7-V-003/004(filename/placeholder 例)、C8-006/007(stale one-off 工具)。
- **披露/精度 nit**：S1-04(event study framing)、S3-BRK-06(descriptive sample universe)、S4-07/08、S7-08/09、C3-06/07、C5-05/07/08、C6-08。

**建议**：P3 全部"安全可立即改或留待顺手清理"，无 econometric/spec 决策成分。其中 **C7-V-001 的"邻域加密"编造术语**虽 P3 但建议优先清（同文已自承非几何/邻域加密，只是过采样随机抽样），避免误导读者。

---

## 六、建议处置 (建议处置)

### A. 可立即安全应用（typos / stale 计数 / 错 DOI / stale 注释 / 行号）— 无需用户决策

这些是纯文档/注释/计数订正，零 econometric/行为影响，可直接批量改：

1. **全部 P1 引文错**：C1-001(Shapiro→Kelly, dag.py+yaml)、C1-002(删 Late Chunking 误引, 3 处)、S11-05(Janis-Fadner)、D3-04/C6-02(Han 三作者, 删 Ramadorai/Jiang-Zhang-Zhu)、D1-02(attention 锚 Fang-Peress)。
2. **全部 P2-7 引文错**（BS-08/C3-04/C3-05/C7-V-002/C8-002/C8-005/C6-07/D4-03）。
3. **全部计数/行数 stale**：D1-01(doctor 5→6)、D1-03(缓存 MB/条)、D1-04(删 32a)、D5-03(14→19)、D5-06/07/08/09/10/11/12/14、D3-05/06/09/10/11/12/14/15/16、D4-01(35/32/16+16)、D4-02、D2-03/04、P1-Q。
3. **stale 注释/行号/feature ref**：C5-01(删 topic)、S11-08(_title 空 section)、P1-P(shrinkage ss 理由)、C3-01/02、C2-01/02/04、C4-001/002/003、C5-02/03/04、C1-003/004/006、全部 P3 行号簇。
4. **启动守卫(纯机械)**：P0-B(99_master `exit, clear`+15_complete 引用)、S11-07、S12-007 终端 exit。

### B. 需用户决策（econometric / spec / 数据-契约改动）— 不可径改

这些涉及识别策略、回归 spec、数据列契约或下游 golden 重生，须用户拍板：

1. **P0-簇-1（stage 49 重锚）**：把 6 个 .do 基础 `use` 改指 `46_panel_yearly_full.dta` + z_score 占位守卫——是**数据契约改动**，须确认 provisional 论文是否就此接 live 面板 / 还是标记包暂不可跑。
2. **P1-A（digital_frontier 吸收）**：选 (a) 仅披露 还是 (b) 重构为 `##i.year/i.era` 交互——是**主回归 spec 决策**。
3. **P1-B（_ss 三轨 IV）**：选 加 ss just-ID 列(全平价) 还是 仅 header 披露 deferred——影响多个 IV 模板与 golden。**铁律：禁混 Hansen J。**
4. **P1-F/P1-G（locus/15 test 中止、collab/19 event study）**：改 Stata 逻辑(restore M5 / 加 lead 项)——是 spec 改动，须确认与 locus 镜像一致。
5. **P1-W（few-cluster boottest、同名异构 DV、sureg FE）/ P2-1(Stock-Yogo)/P2-3(rwolf/mgroups)**：涉及推断方法/工具识别，须确认是否动 spec + 是否要 golden/付费重跑。
6. **P0-A（gemini 标签）/P1-E(ivreghdfe 回退)**：虽是修复但触及 Stata 行为，建议确认是改名 vs 弃用手维护标签集、是否扩 IV-6 回退到 13/14。

> **关键护栏**：任何触及 panel 列/回归值的改动须经 golden 受控重生（排除 3 个 BLAS-FP 网络列），且**勿删 `_llm_cache.db`**（删则 stage 21 须付费重跑、golden 不可复现）。文档/注释/计数订正全部 golden-safe。