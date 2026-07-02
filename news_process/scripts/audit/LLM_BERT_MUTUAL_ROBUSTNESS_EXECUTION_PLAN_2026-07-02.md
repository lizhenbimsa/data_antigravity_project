# LLM 三家(含投票共识) / BERT 三模型「互为稳健性」形式化落地 — 执行计划 **v3 (二轮评审后定稿)**

> 日期: 2026-07-02 · 状态: 计划已定稿, 未实施 · 权威范式镜像 = `du_2022` 政治词权重梯度 + `18_substance_robustness` rwolf
>
> **版本沿革**: v1 → 15-agent 评审 (9 major) → v2 → **24-agent 最终评审 (2 blocker + 11 major, 多条实跑)** → **v3 (本版)**。
> **用户已定决策**: BERT signed `_net_tone` (+9); 补模型间 κ; **FWER = 现建真 rwolf (option B, 根级 + 全联动 wire-ahead)**。
>
> ⚠ **二轮评审两大教训 (v2 的致命短板, v3 已修)**:
> 1. **rwolf 落地远比 v2 想的复杂**: tone 无模板子目录 → **必须根级**放置 (子目录永不实例化); 占位符 `{{OUTCOME}}/{{T}}` 不存在会**崩整个复现包 build**; 根级放置牵动 ~8 处联动 (计数/00_master/多测试)。
> 2. **per-model 覆盖范围被严重低估**: 盘上 per-model 列 **≈465 个** (含 81 个加权变体 `_vw/_mw/_hw`), 非 v2 假设的 5-metric 口径; 窄正则修完仍剩 ~129 列落「未知」→ 改**宽前缀**。

---

## §0. 关键已核验事实 (含二轮实跑)

| 层 | 现状 (实读/实跑确认) | 含义 |
|---|---|---|
| LLM per-model | `encode.py:692-697` signed `{short}_tone{track}`(+_tone_sum/_cont_mean/_cont_sum/_tone_std)。SSOT `encode.py:57-58`。**另有** 27 个加权变体 `{short}_tone_{vw,mw,hw}` (`encode.py:2082+`)。 | 0 新列; 覆盖须含加权臂。 |
| LLM 投票共识 | `encode.py:700-702` `llm_vote_tone{track}` = canonical headline (`primary`)。 | 0 新列。 |
| LLM 均值-ensemble | `geography.py:220` `llm_models_avg_tone{track}` (第二个 ensemble, 均值)。 | §1(e) 调和。 |
| BERT per-model | `encode.py:748-756` 仅 `{short}_pos/_neg/_pos_std{track}`(3 分类另 `_neu/_neu_sum`, +`_sum`)。SSOT `:83-84`。**另有** 54 个加权变体 `{short}_{pos,neg}_{vw,mw,hw}`。**无 signed net-tone**。 | **P2 补 +9 net_tone**; 覆盖须含 8 metric + 加权臂。 |
| BERT rollup | `geography.py:253-259` `bert_avg_*` **仅 `_BERT3`** (finbert2 排除)。 | net_tone 不自动入 rollup (显式列名清单)。 |
| 分类数 | finbert_cn/fin_sent_zh = 3 分类 (`sentiment.yaml:314/319`); **finbert2 = 2 分类** (`:328`)。LLM 三家共享 `{−1,0,+1}` (`encode.py:102`)。 | Phase 3 用 **Krippendorff α** (缺标感知, 天然容 2-vs-3 分类)。 |
| κ 现状 | `validation/llms_evaluation.py:138/275/338` **已有** `compute_cohens_kappa`/`_weighted`/**`compute_krippendorffs_alpha`** (名义+缺标感知)。`manuscript.tex:55-56` **已承诺 Cohen κ + Krippendorff α**。 | Phase 3 **复用既有 Krippendorff**, 不另造 Fleiss。 |
| tone 复现路径 | `stata_runner.py:446-447` tone→**根级** `template_dir=base` + `:482` **非递归 glob**; `derivative_replication.py:344` 对 tone raise。tone **无模板子目录**。`_EXPECTED_ROOT_DO=19`(`:680`)。 | rwolf **必须根级** + 联动改动。 |
| 占位符 | tone `_PAPER_DEFAULTS['MAIN_DV']='ROA'`(`stata_runner.py:318`); `{{MAIN_SENT_TRACK}}` 裸值 full/ctx/ss; **`{{RANDOM_SEED}}/{{CLUSTER_VAR}}` 根级不可用**; `_substitute_placeholders` 对残留 `{{X}}` **fail-fast raise**。 | rwolf 用 `{{MAIN_DV}}`(=ROA)/`{{MAIN_SENT_TRACK}}`, seed/cluster **硬编码**。 |

---

## §1. 设计决策

### (a) 对称性: canonical headline + per-model co-equal 稳健梯度 【已定】
LLM: `llm_vote_tone`=headline; 三 `{short}_tone` co-equal 不分主次。BERT: 三 per-model co-equal, 无 ensemble headline。

### (b) finbert2 parity: per-model 独立降级, 非 both-or-neither 【已定】
缺席仅掉自身族 (`valid_agg` 过滤); gate 用 DEFERRED skip。

### (c) BERT signed net-tone: `{short}_net_tone{track}` (+9) 【已定, v2 修尺度, v3 补加权孪生取舍】
- `net_tone{track} = panel[{short}_pos{track}] − panel[{short}_neg{track}] ∈ [−1,1]`, post-agg 派生, 不重跑 stage 23。
- 2 分类 finbert2: `net=2·pos−1` 满幅; 3 分类: 中性质量压缩向 0 → **方差不同, 原始 β 机械不可比** → **β 对照须 z-score 标准化** (仅用于 Table A5, §F4; rwolf 用原始量, 见 §1f)。
- **只产 mean (9 列)**: 不产 `_net_tone_std`(非 post-agg 可派生)、`_net_tone_sum`(保持 +9)、**`_net_tone_{vw,mw,hw}` 加权孪生**。⚠ **v3 明记该不对称** (评审 completeness): LLM `tone` 与 BERT `pos/neg` 均有 `_vw/_mw/_hw`, net_tone 刻意不产加权孪生 —— 理由: net_tone 是为 β 可比派生的 signed 便利列, 加权稳健性已由底层 `pos/neg` 的 `_vw/_mw/_hw` 覆盖; 全套加权 net_tone (+27) 列爆炸, 收益低, 列为 optional 后续。

### (d) 模型间 κ: **Krippendorff α (主) + pairwise Cohen κ** 【v3 改用既有 canonical 函数】
- ⚠ **v3 关键修 (评审 confirmed)**: **不**自造 Fleiss (会撞 2-vs-3 分类失配)。**复用 `validation/llms_evaluation.py:338 compute_krippendorffs_alpha`** (名义尺度 + **缺标感知** → finbert2 无「中性」= 缺标, Krippendorff 原生容纳, 无需二值化/丢信息) + `:138 compute_cohens_kappa` pairwise。
  - **LLM 组**: 三家 `{−1,0,+1}` → Krippendorff α + pairwise Cohen。
  - **BERT 组**: 三模型 → Krippendorff α (finbert2 的「中性」作缺标, 天然处理); pairwise Cohen (finbert2 对须共享 {正,负} 类空间, 或标注为缺标)。
- **对齐手稿**: `manuscript.tex:55-56` 已承诺「Cohen κ + Krippendorff α」→ 产物须**同时含** Cohen κ 与 Krippendorff α。出 `eval_reports/sentiment_model_kappa_{track}.{csv,tex}`。锚 Krippendorff (2004)/Hayes-Krippendorff (2007)/Landis-Koch (1977)。golden-safe。

### (e) 两个 LLM ensemble 调和 【v2 新增】
`llm_vote_tone`(投票, headline, `primary`) 与 `llm_models_avg_tone`(均值, 次级复合) 并存; 三 per-model 是 co-equal 稳健臂。§1(a) 措辞不再称「vote 是唯一/第 4 个 ensemble」。

### (f) FWER 实现 = 真 rwolf 根级模板 (option B) 【已定, v3 全重写落地】
- ⚠ spec 的 `fwer.*` 是**声明式文档、运行时无人消费** (评审 confirmed); 真 FWER 由 §F5 **根级** rwolf 模板产 (family 硬编码, 与全仓一致)。
- ⚠ **rwolf 报校正后 p, 对 indepvar 单调缩放不变** → **rwolf 用原始量, 不标准化** (标准化只用于 §F4 Table A5 的 β 幅度并排)。§1(c)/§7 措辞据此收紧, 删「统一 β/统计量尺度无关」。
- ⚠ **wire-ahead 休眠**: rwolf DV = `{{MAIN_DV}}`=**ROA** (tone 默认; ROA/funding_cost 盘上均缺席) → **当前数据恒 capture-confirm 跳过, T=18 财务数据到位才运行** (与仓库 wire-ahead 惯例一致)。

---

## §2. 分阶段范围

| Phase | 内容 | golden | 列增量 | 模板计数 |
|---|---|---|---|---|
| **1 核心** | paper_spec(doc) + **stata_export 标签层(8 metric+加权臂)** + codebook(matcher/_infer_label/_desc/**_infer_source_stage 宽前缀**) + encode 铁律注释 + **根级 rwolf 模板(option B)+全联动** + Table A5 补列+标准化 + CLAUDE.md + gate | 0 新 panel 列 | 0 | **+1 (19→20 根级; 145→146 总)** |
| **2 BERT signed** | encode post-agg +9 net_tone + codebook metadata + stata 标签 + gate 恒等 + CLAUDE.md 列数。(rwolf 的 BERT 族由 capture-confirm 在此自动激活, **无独立"切 signed"步**) | +9 → DEFERRED+A/B | +9 | 不变 |
| **3 κ** | `tone_validation.py` **Krippendorff α + Cohen κ** (复用 llms_evaluation) + eval_reports | golden-safe | 0 | 不变 |

提交序: **Phase 1 → Phase 3 → Phase 2**。

---

## §3. 确切改动清单 (v3)

### 层 A — article/stage: 不动。

### 层 B — encode (`pipeline/panel/encode.py`)
- **B1/B2 (P1)** `:54-58`/`:82-93` SSOT 注释补铁律 (headline+co-equal; per-model 独立降级; ⚠ 禁混同一 over-identified Hansen J)。
- **B3 (P2)** `aggregate_panel` groupby `.agg()` 后加 net_tone post-agg (守卫 `if pos in cols and neg in cols`), 见 §1(c) 代码。

### 层 C — import
- **C1 (P1)** `codebook.py` 补 `from ...encode import BERT_MODELS` (现仅 `LLM_MODELS`@`:679`)。

### 层 D — codebook (`pipeline/panel/codebook.py`)
- **D1 (P1)** `:247` 后新增 matcher + NOTE (镜像 `_POLITICAL_WEIGHT_*`@`:223-247`):
  - `_LLM_MODEL_RE` / `_BERT_MODEL_RE` **须覆盖全 metric + 加权臂**: metric ∈ {tone,tone_sum,tone_std,cont_mean,cont_sum} (LLM) / {net_tone,pos,neg,neu,pos_sum,neg_sum,neu_sum,pos_std} (BERT), 各带**可选** `(_vw|_mw|_hw)?` + `(_full|_ctx|_ss)?`。排除 `llm_vote_*`/`{short}_tone_sub/_symb`。用 `enc.LLM_MODELS`/`enc.BERT_MODELS` 拼装。
  - `_llm_model_match`/`_bert_model_match` + `_LLM/_BERT_MODEL_NOTE`(含「co-equal 不分主次」+「⚠ 禁混同一 over-identified Hansen J」)+`_*_CITATION`。
- **D2/D3 (P1)** `_infer_label`(`:1885-1887` 后、`:1888` 泛型前)/`_infer_description`(`:1918-1921` 后) 插 per-model 分支。
- **D4 (P1) `_infer_source_stage` (`:1937-1960`) — ⚠ v3 改宽前缀 (评审实跑: 窄正则修完仍剩 ~129 列「未知」)**: 在 `:1937` 前插:
  ```python
  if any(var_name.startswith(m + '_') for m in LLM_MODELS):
      return 'Stage 21'
  if any(var_name.startswith(m + '_') for m in BERT_MODELS):
      return 'Stage 23'
  ```
  宽前缀覆盖全部 per-model 列 (tone/pos/neg/net_tone + 加权/计数/和变体), 实跑残留 0。⚠ 须在 `'llm'/'gpt'/'gemini'` 子串块**前** (顺序无害但语义清晰); `llm_vote_*` 不以模型名开头故不误命中。
- **D5 (P2, 可选)** BERT `_net_tone` 显式 `VariableMetadata` (镜像 `:691-708`)。

### 层 E — paper_spec (documentation-only, 评审 confirmed 无运行时消费)
> ⚠ E1-E5 是文档 (记录 battery + 可复现意图), **不触发** FWER; 真校正见 §F5。
- **E1** `bank_fintech_tone/paper_spec.yaml:100` 加 `cross_bert_model` + 铁律注释 + 「实际 FWER 由 `<根级 rwolf 模板>` 计算」。
- **E2** `:105` `apply_to` 追加 `cross_model,cross_bert_model` — 注释标「记录受校正族; 实现见 Stata rwolf」。
- **E3 (可选)** `:52-54` 补 `_ss` 三家。**⚠ caveat (评审)**: full-only 门控下 `_ss` 是 conditional-on-full, 注释须标明; 且须确认 `{short}_tone_ss` 三列在盘 (在, encode 三轨无条件产)。
- **E4/E5** `bank_fintech_attention/paper_spec.yaml:120`/`:124-125` 加 `cross_model`/`cross_bert_model` + `fwer.families` 追加 (同 documentation 注释)。

### 层 F — Stata
- **F1 (P1)** `24_tableA5...tmpl:48` 后补 3 个 per-LLM `eststo` (`foreach lm in ...`, capture confirm)。
- **F2 (P1→P2)** `:102` `local berts`: P1 追加 `finbert_cn_pos`; P2 切 signed `finbert_cn_net_tone fin_sent_zh_net_tone finbert2_net_tone`。
- **F3 (P1)** `:120-121` `cand_models`/`cand_titles` **成对同位**扩 (⚠ r(111))。
- **F4 (P1, 标准化 — 仅 Table A5)** 对情感 DV `egen std_*=std(...)` 出标准化 β 列 (镜像 `benefit_society/15_table6:30-34`); 脚注标「跨模型 β 标准化后可比 (2/3 分类 net_tone 原始方差不同)」。头部注释补铁律。
- **F5 (P1, option B 真 rwolf) — ⚠ v3 全重写: 根级 + 全联动**:
  - **放置**: **根级新模板** (非 tone 子目录; 子目录永不实例化——评审 blocker)。编号实施时择根级空号 (如 `25_tableA6_cross_model_fwer.do.tmpl`, 确认不与现有根级碰撞)。
  - **占位符**: DV=`{{MAIN_DV}}` (tone→**ROA**, wire-ahead 哨兵, capture confirm 守卫); 轨=`{{MAIN_SENT_TRACK}}` (裸 full/ctx/ss, **无前导下划线**, 故写 `_{{MAIN_SENT_TRACK}}` 补下划线或写 `{{MAIN_SENT_TRACK}}` 视上下文)。**seed/cluster 硬编码** (`seed(90210)`/`cluster(bank_id)`, 因根级无 `{{RANDOM_SEED}}/{{CLUSTER_VAR}}`)。⚠ **禁用** `{{OUTCOME}}/{{T}}` (未注册 → fail-fast 崩包)。
  - **两族**: `capture which rwolf` 守卫 → ① LLM 族 `rwolf {{MAIN_DV}}, indepvar(gpt54nano_tone_{{MAIN_SENT_TRACK}} gemini31_tone_{{MAIN_SENT_TRACK}} deepseekv4_tone_{{MAIN_SENT_TRACK}}) controls($controls) reps(1000) seed(90210) method(reghdfe) abs(bank_id year) cluster(bank_id)`; ② BERT 族同款 indepvar=三 `_net_tone` (**capture confirm 每列 → Phase 1 因 net_tone 未产自动休眠, Phase 2 自动激活**, 镜像 F2 分期)。
  - **⚠ 镜像深度到 `:104` (评审 confirmed)**: 抄 `18_substance_robustness.do.tmpl:53-104` 的**多-indepvar 校正 p 抽取** (矩阵 `e(RW_<iv>)[1,3]` + 32 字符名回退); **两族顺序跑 → 各族 rwolf 后立即抽 p** (后一 rwolf 覆盖 `e()`)。
  - **DV 名**: `{{MAIN_DV}}`=ROA (非 funding_cost; 二者盘上均缺席, 均 capture-confirm 休眠; 若确需 funding_cost 须单独决策改 tone MAIN_DV 默认, 波及全部根级表, **本计划不改**)。
- **F6 (P1, 根级放置全联动 — v3 新增, 评审 confirmed)**:
  - `stata_runner.py:680 _EXPECTED_ROOT_DO 19→20`。
  - `00_master.do.tmpl:33-74` 增 `capture noisily do` 行 (否则新表永不执行)。
  - `test_stata_templates.py` roundtrip 断言: `'19/19'→'20/20'` / `'Summary: 8 OK'` (核对是否连动) / `EXPECTED_TEMPLATES_V14` 硬列表加项 (`:219/291/297-299`)。
  - `test_stata_replication_matrix.py:47` `==19→20`。
  - `test_build_replication_package.py` (fast, 6 例) — 复跑确认新模板占位符全解析 (`{{MAIN_DV}}/{{MAIN_SENT_TRACK}}` 均注册; 无残留 → 不 raise)。
  - `test_papers_b_route.py:176 145→146` + `:164-184` docstring 加项。

### 层 G — stata_export (`pipeline/panel/stata_export.py`) 【v2 新增层】
- **G1 (P1)** per-model 标签机械块 (镜像 polw `:606-620`, 插 `:583-620` 同区、**`for col` 循环 `:622` 前**): 用 `enc.LLM_MODELS`/`BERT_MODELS` 循环, **覆盖全 metric + 加权臂** (评审: BERT 须 8 metric 非 4, 且含 `_vw/_mw/_hw`), 生成 `HEURISTIC_LABELS[裸列名]` (≤80 byte)。
- **G2 (P1)** 补 `llm_vote_tone_ss` 标签 (`_full/_ctx`@`codebook.py:561/578` 已注册, `_ss` 现 fallback)。

### 层 H — gate (镜像 `test_political_weight_ladder.py` 全 6 类)
- **H1/H2 (P1)** `test_llm_model_robustness.py`/`test_bert_model_robustness.py`: (a) `enc.LLM/BERT_MODELS==config==codebook` 三方一致; (b) agg 含 `{short}_tone/pos/neg{track}`; (c) **StataLabels 非 fallback** (依赖 G1; **断言列集须 = G1 覆盖集**, 勿断言未覆盖的加权臂非 fallback → 否则自红); (d) **`_infer_source_stage`→正确 stage** (宽前缀; 断言含 `deepseekv4_*`/`fin_sent_zh_*` **及加权变体** `deepseekv4_tone_vw_full`/`fin_sent_zh_pos_vw_full` 均不「未知」); (e) matcher 不吞 `llm_vote_tone`/`_sub`/`_symb`; (f) 四方 matcher 互斥; (g) NOTE 含铁律。P2 追加 net_tone 存在+≤32+恒等。
- **H3 (P1)** geography no-rollup gate (镜像 `:239-264`): per-model/net_tone 不误入非预期跨模型均值。

### 层 I — CLAUDE.md
- **I1 (P1)** 新增「LLM/BERT 互为稳健性」铁律段 (headline+co-equal; 两 ensemble; 独立降级; 禁混 Hansen J; SSOT; 真 FWER=根级 rwolf; gate)。
- **I2 (P2/根级)** 最宽列数 (~L53/L199) +9; **模板计数「142」→「146」** (CLAUDE.md 模板段) + 根级 `.do` 19→20 若有述及处。

### 层 J — validation (Phase 3)
- **J1 (P3)** `tone_validation.py` 新增「模型间一致性」段: **复用** `llms_evaluation.compute_krippendorffs_alpha` (LLM 三家一组、BERT 三家一组各算 α, finbert2 缺「中性」作缺标) + `compute_cohens_kappa` pairwise; 出 `eval_reports/sentiment_model_kappa_{track}.{csv,tex}` (含 **Cohen κ + Krippendorff α**, 对齐 `manuscript.tex:55-56`)。
- **J2 (P3)** gate 验 κ/α 路径 + 缺标处理 + 产物键。

---

## §4. 列增量
| Phase | 新增 panel 列 | 数量 |
|---|---|---|
| 1 | 无 panel 列 (Stata 模板 +1: 根级 19→20, 总 145→146) | 0 |
| 2 | `{finbert_cn,fin_sent_zh,finbert2}_net_tone{_full,_ctx,_ss}` | +9 |
| 2 明记不产 | `_net_tone_{std,sum,vw,mw,hw}` (§1c 取舍) / `bert_avg_net_tone` (geography, optional) | 0 |
| 3 | 无 panel 列 | 0 |
最长 `fin_sent_zh_net_tone_full`=25 ≤32 ✓。

---

## §5. Golden 策略
- **Phase 1 = 0 新 panel 列 → golden 字节不变**。根级 rwolf 模板只加 `.do.tmpl` + 改测试计数/master/stata_runner 常量, **不产 panel 列** → `test_panel_reproducibility` 不受影响; `test_papers_b_route`(145→146)/`_EXPECTED_ROOT_DO`(19→20)/`test_stata_templates`/`test_stata_replication_matrix`/`test_build_replication_package` 须同步 (§F6)。
- **Phase 2 = +9 (encode post-agg, 不重跑 stage 23)** → strategic_diff 先例: `test_panel_reproducibility` (已陈旧红) → **DEFERRED 重生 + A/B**; `test_v3_2_panel_columns`(presence+下界)/`test_dag_consistency`/`OUTPUT_REGISTRY` 安全。STAGES 计数不变。
- **Phase 3 = validation/eval_reports, golden-safe**。

---

## §6. 铁律写入清单
1. `encode.py:54-58` 2. `:82-93` 3. B3 派生块 4. `bank_fintech_tone/paper_spec.yaml:100` 5. `attention/paper_spec.yaml:124-125` 6. `24_tableA5` 头部+per-LLM 块(F4) + **根级 rwolf 模板注释**(F5) 7. `codebook.py` `_LLM/_BERT_MODEL_NOTE`(D1) 8. CLAUDE.md 新段(I1) 9. gate 断 NOTE 含短语 (H1/H2, 镜像 `test_political_weight_ladder.py:42-45` 对 **RATIONALE** 常量的短语断言模式)。

---

## §7. 风险 / 易错点 (v3, ⚠ = 评审确认的真实陷阱)
- ⚠ **rwolf 必须根级** (子目录永不实例化 → 伪完成); 禁 `{{OUTCOME}}/{{T}}` (fail-fast 崩包); seed/cluster 硬编码。
- ⚠ **根级放置全联动** (§F6): `_EXPECTED_ROOT_DO`/`00_master`/`test_stata_templates`/`test_stata_replication_matrix`/`test_build_replication_package`/`test_papers_b_route` 一处不改即红。
- ⚠ **rwolf 镜像须到 :104**: 只抄调用 (:53-55) 会「跑得动但取不到校正 p」(substance/18 反复修的 bug); 两族顺序跑各族即时抽 p。
- ⚠ **DV=ROA 非 funding_cost**; 二者盘上缺席 → rwolf wire-ahead 休眠至财务数据到位。
- ⚠ **`_infer_source_stage` 用宽前缀** (窄正则漏 ~129 列); **stata 标签/gate 断言列集须与 G1 覆盖集一致** (勿断言未覆盖列非 fallback)。
- ⚠ **加权变体 `_vw/_mw/_hw`** (81 列) 须纳入 D1 regex/D4/G1/gate 覆盖; net_tone **不产**加权孪生 (§1c 明记)。
- ⚠ **κ 用 Krippendorff α (缺标感知)** 非自造 Fleiss (避 2-vs-3 分类失配); 产物含 Cohen κ + Krippendorff α 对齐手稿。
- ⚠ **标准化仅用于 Table A5 β** (F4); **rwolf 用原始量** (p 对缩放不变); §1(c)/§7 删「同尺度可比」。
- ⚠ **净列恒等/mask**: net_tone := pos−neg panel 后处理恒真; 解读为 article-mean signed net 依赖 pos/neg 原子失败掩码一致 (已披露)。
- ⚠ 成对必改 `cand_models`/`cand_titles` (r(111)); 标题/note 禁英文单引号 (r(109)); `_infer_label` 分支在泛型 `'tone'` 前; regex 排除 `llm_vote`/`_sub`/`_symb`; BERT parity≠嵌入 both-or-neither; 共享树 by-name 提交排除并发产物 (`v3_5_1_constants.json`/`eval_reports/*`)。
- ⚠ E3 `_ss` full-only caveat; 两 ensemble 调和 (§1e)。

---

## §8. 落地顺序
**Phase 1 (golden-safe, 一次提交)**
1. **1a** codebook (D1 全 metric+加权 matcher / D2 / D3 / **D4 宽前缀** / C1) + encode 注释 (B1/B2) + **stata_export 标签层 (G1 全 metric+加权 / G2)**。验: `pytest tests/test_political_weight_ladder.py` + 新 `test_llm/bert_model_robustness.py` + `ruff`。
2. **1b** paper_spec (doc, E1-E5)。验: `pytest -k paper_spec test_paper_namespace_isolation`。
3. **1c** Stata: Table A5 (F1/F3/F4 补列+标准化) + **根级 rwolf 模板 (F5)** + **全联动 (F6)**。验: `pytest tests/test_papers_b_route.py tests/test_stata_templates.py tests/test_build_replication_package.py` + (integration) `test_stata_replication_matrix.py` + `stata_runner build-replication` 冒烟 + (可选) `run_stata.ps1` 跑无 r(111)/r(109)/rwolf 守卫。
4. **1d** CLAUDE.md (I1)。
5. **1 全局门**: `pytest -m fast` + `test_dag_consistency`/`test_v3_2_panel_columns` + **baseline-stash A/B**。

**Phase 3** 6. `tone_validation.py` (J1 Krippendorff+Cohen) + eval_reports + gate (J2)。验: `pytest tests/test_64_tone_validation.py`(或新建) + `ruff`。

**Phase 2 (DEFERRED)** 7. encode +9 (B3) + codebook metadata (D5) + stata net_tone 标签 (G1) + Stata berts 切 signed (F2, rwolf BERT 族自动激活) + gate 恒等 (H2) + CLAUDE.md 列数/计数 (I2)。验: `pytest test_bert_model_robustness test_v3_2_panel_columns` + A/B; golden 重生 DEFERRED 生产机。

---

## §9. 实施时须现场确认 (残余不确定)
- 根级 rwolf 模板**编号**择空号 (查现有根级 `NN_*.do.tmpl` 序列)。
- `test_stata_templates.py` 的 `'Summary: 8 OK'`/`'18/18 子'` 等断言是否随 +1 根级模板连动 (实跑 roundtrip 定)。
- `00_master.do.tmpl` 新 do 行的确切位置 (`:33-74` 枚举区)。
- `encode.py::aggregate_panel` post-agg (B3) 精确插入行。
- rwolf 多-indepvar ereturn 在本机 Stata 19 的 `e(RW_*)` 命名 (镜像 substance/18:60-104 实测口径)。

---

## §10. 实施记录 (执行时填写)
- [x] P1-1a codebook (C1 模块级 import 两名 / D1 matcher+加权 / D2 D3 label / D4 宽前缀) + encode B1/B2 + stata_export G1/G2 — 实跑: 宽前缀 13/13 + 四方互斥 + 249 列非-fallback + polw 28/28 无回归
- [x] P1-1b paper_spec E1/E2/E4/E5 (doc) — namespace/forward_compat 8 通过
- [x] P1-1c Table A5 (F1 per-LLM+F2 三BERT+F3 cand_models+F4 z-score) + 根级 rwolf 27_tableA12 (F5) + 全联动 (F6) — 实跑: 计数 146 + build/verify roundtrip 20/20+19/19 全通过 (无 {{OUTCOME}}/{{T}} 崩)
- [x] P1-1d CLAUDE.md I1
- [x] P1 gate test_llm/bert_model_robustness 26/26 + geography no-rollup + ruff 全清 + 回归 155 绿 (仅既有 locus/substance 缺 output/ 红, 非本次)
- [x] P3 tone_validation `compute_cross_model_kappa` (复用 llms_evaluation Krippendorff α + Cohen κ; **非负重映射** 负=0/中=1/正=2 避 -1 哨兵; 矩阵 n_coders×n_items) + 钩入 _run_validation_for_track + eval_reports — 实跑 8 行, LLM α=-0.035 (随机≈0 证 -1 修复), finbert2 2-vs-3 原生处理, 'llm' 剔除; golden-safe
- [x] P2 encode B3 +9 net_tone (post-agg, per-model 守卫独立降级, 仅 mean) — 实跑 net_tone==pos−neg 恒等 + finbert2 缺席跳过; ⚠ 真面板 +9 须生产机 aggregate_panel 重生 (golden DEFERRED + A/B)
- [x] 全局门 + A/B: fast baseline-stash A/B **证 0 新增失败** (4 红灯 baseline≡A = 既有 disk-state, 非本次); DAG + 面板列 presence 26/26 绿
- [ ] 提交 (by-name, 排除并发 v3_5_1_constants.json/bank_list.yaml) + 推送 — 待用户确认 (outward)
- [ ] 生产机: aggregate_panel 重生 (+9 net_tone) + golden 重生 + manuscript FWER/κ prose

---

## §附. 二轮评审处置台账 (2 blocker + 11 major, 全 confirmed/partial)
| # | 发现 | 处置 (v3) |
|---|---|---|
| B1 | tone 子目录 rwolf 永不实例化 | F5 强制**根级** |
| B2 | `{{OUTCOME}}/{{T}}` 崩包 | F5 用 `{{MAIN_DV}}/{{MAIN_SENT_TRACK}}` + 硬编码 seed/cluster |
| M1 | DV=ROA 非 funding_cost | §1(f)/F5 明记 ROA wire-ahead 休眠 |
| M2 | 根级联动全漏 | **F6 新增** (EXPECTED_ROOT_DO/00_master/4 测试/计数) |
| M3 | 镜像太浅漏 ereturn 抽取 | F5 镜像到 `:104` + 两族即时抽 p |
| M4 | BERT 族 net_tone Phase 门控 | F5 capture-confirm 分期 (P1 休眠/P2 激活) |
| M5 | `_infer_source_stage` 窄正则剩 129 列 | **D4 改宽前缀** (残留 0) |
| M6 | 加权变体 81 列全漏 | D1/D4/G1/gate 覆盖 `_vw/_mw/_hw` |
| M7 | G1 BERT 仅 4/8 metric | G1 补全 8 metric |
| M8 | κ 脱节 (漏 Krippendorff/手稿) | **§1(d)/J1 改用既有 Krippendorff α + Cohen**, 对齐手稿 |
| M9 | net_tone 加权孪生不对称未记 | §1(c) 明记取舍 |
| M10 | §2/§8 Phase 归属自相矛盾 | net_tone=P2; rwolf BERT 族 capture-confirm 自动激活 (无独立"切"步) |
| M11 | 标准化误及 rwolf | §1(f)/§7 明确标准化仅 Table A5, rwolf 用原始量 |

---

## §11. v4 最终审核修正 (三轮评审收口 · **以本节为准, 覆盖前文任何冲突**)

> 第三轮 12-agent sign-off 审核 (全 go-with-fixes, 无架构 blocker; 7 serious 全 confirmed, 多条实跑)。以下 11 条为**实施必依**的精确修正; 前文 §0-§附 若与本节冲突, **一律以本节为准**。

### 🔴 照字面做会崩/静默算错 (必修)
1. **C1 import (NameError 崩 codebook)**: codebook.py 模块作用域 **既无 `LLM_MODELS` 也无 `BERT_MODELS`** (`:679` 那处是 `get_variable_metadata_dict` **函数内局部导入 + 别名 `_ISS_LLM_MODELS`**, 对模块级 `_LLM_MODEL_RE`(D1)/`_infer_source_stage`(D4) **不可见**)。→ **C1 改为**: codebook.py **模块顶部** 加 `from news_process.pipeline.panel.encode import LLM_MODELS, BERT_MODELS` (**两名都加**), 且 D1/D4 引用统一 (裸名或统一 `as enc`, 二选一)。删 v3「现仅 LLM_MODELS@:679」的错误前提。
2. **Krippendorff -1 哨兵撞负面标签 (静默算错, α 虚高至 1.0)**: `compute_krippendorffs_alpha` 用 **`valid_mask = ratings_matrix >= 0`** (`llms_evaluation.py:355`), 而 `SENTIMENT_MAP` 负面 = **−1** (`encode.py:102`) → 直接喂 `{−1,0,+1}` 会把**所有负面标签当缺失丢弃**。→ **§1(d)/J1 改为**: 调 Krippendorff/Cohen 前**必须**把三值重映射到**非负码** (`{负面:0, 中性:1, 正面:2}`, 镜像 `llms_evaluation.py:1954` / `tone_validation.py:913`); `−1` 仅留给**真正缺失** (整模型 graceful-skip)。BERT 组同理 (负面不得编 −1)。(注: Cohen κ 用 `sorted(set)` 自动发现类别, 不受 −1 影响, 但为一致仍统一重映射。)
3. **F5 `$controls` → `$bank_controls`**: 根级复现包只定义 `$bank_controls` (`根/01_data_prep.do.tmpl:53`); `$controls` 是 substance 子目录特有 (F5 从 `substance/18:53` 直抄未改)。ROA 守卫下当前不崩, 但**财务数据到位后会以空 controls 跑 → 结果错**。→ F5 rwolf 用 **`controls($bank_controls)`**。
4. **finbert2 「缺标」表述概念错 (依据错, 结论对)**: finbert2 是 2 分类, 每篇必输出确定 pos/neg, **不产生可标缺失的单元**; Krippendorff 的 −1 缺标指「某编码者未评某 item」, 与「类别词表少一类」是两回事。→ **§0/§1(d)/J1 改写依据**: finbert2 以**真实 pos/neg 作 present (非负) 标签**参与; 名义 Krippendorff α **天然允许编码者只用类别子集**, 会把 finbert2 的 pos/neg 与 3 分类模型的中性**正确计为真实不一致** — **无需也不能**标缺失。(用 Krippendorff、不二值化的**结论不变**, 仅纠正理由。)

### 🟠 会让测试红 (必修)
5. **F6 补 test 本地白名单 (否则 `test_template_no_unknown_placeholders_full` 红)**: `test_stata_templates.py:24-29` 的**本地** `KNOWN_PLACEHOLDERS` frozenset 仅 4 项 (`MAIN_LOCUS_TRACK/MAIN_SUBST_TRACK/MAIN_SENT_TRACK/PROJECT_ROOT`), **与 `stata_runner._KNOWN_PLACEHOLDERS`(含 MAIN_DV) 是两套**。新模板用 `{{MAIN_DV}}` → 加进 `EXPECTED_TEMPLATES_V14` 后该断言 (`:169-174`) 会红。→ F6 补: **同步在 `test_stata_templates.py:24` 本地 frozenset 加 `'MAIN_DV'`** (MAIN_SENT_TRACK 已在)。§7 加风险条「测试本地 frozenset ≠ stata_runner 运行时注册表, 两处分别维护」。
6. **F6 联动断言精确化**: 加新根级模板 (进 00_master) 后, 须改 **两处**: `test_stata_templates.py:297 '19/19'→'20/20'` **且** `:298 '18/18 子 .do'→'19/19 子 .do'` (master 现引用 18 个子 do, +1→19)。`:299 'Summary: 8 OK'` **不变** (段数固定 8)。`stata_runner.py:732-747` 子-do 期望清单**不动**。`test_build_replication_package.py` 实为 **12 个 test** (非 6; `len>=3` 无计数耦合, 无害)。

### 🟠 号码/展示/文档 (必修)
7. **F5 模板编号改真空号**: `25_tableA6_cross_model_fwer` **双撞车** (号 25 + 标签 A6 均被 `25_tableA6_tone_iv_2sls` 占用)。实测根级空号 = {15-19, 27, 28-29, 35-40}, 空 A 标签 = {A10, A12}。→ **用 `27_tableA12_cross_model_fwer.do.tmpl`** (27 空 · A12 空 · 已核验无碰撞)。
8. **F3 必须把 BERT 列加进 `cand_models`/`cand_titles`**: `24_tableA5:102-110` 现 `eststo BERT_`b'` 被算但 **`:120 cand_models` 无任何 BERT_* 项** → BERT 列算而不展示; F2 改 `local berts` 若不配 F3 加 cand_models 则**对输出无效**。→ F3 明确成对加入 `BERT_finbert_cn_pos`(P1) / `BERT_*_net_tone`(P2) 到 `cand_models`+`cand_titles` (位置对齐, ⚠ r(111))。
9. **§I2 计数基数 142→145**: v3 §I2 误用 CLAUDE.md 陈旧值「142→146」; 实际现值 **145** (`test_papers_b_route.py:176`)。→ §I2 改 **145→146**, 并把 CLAUDE.md 分解同步为 **主线20(19+1新rwolf)+paper120+归档3+_allv3 = 146** (原「142=主线19+120+3」已陈旧, 一并订正)。

### 🟢 可用占位符 (措辞订正, 二选一)
10. **`{{RANDOM_SEED}}/{{CLUSTER_VAR}}` 根级其实可用**: 二者均在 tone `_PAPER_DEFAULTS` (`CLUSTER_VAR=bank_id`@`:320` / `RANDOM_SEED=20260516`@`:328`), `_substitute_placeholders` 正常填充。v3 §0/F5「根级不可用故硬编码」**前提为假**。→ **优先改用 `{{RANDOM_SEED}}`/`{{CLUSTER_VAR}}`** (对齐全仓 seed 20260516); 若仍硬编码则订正理由为「惯例硬编码」而非「不可用」。

### 🟢 命名/接线 (可接受, 明确即可)
11. **Phase 3 κ 产物命名 + 接线**: eval_reports 既有约定 `f'name{track}'` (track 自带前导下划线, 如 `cronbachs_alpha_summary_full`)。→ J1 产物写 **`sentiment_model_kappa{track}`** (track = `_full/_ctx/_ss`)。κ 只落 eval_reports/`.{csv,tex}`, **manuscript 手工引用**填数 (与既有 llms_evaluation κ 一致, `manuscript.tex:55-56` 承诺 Cohen κ + Krippendorff α) — **可接受, 不强制接 Stata 表**; `20_tableA1` 是跨**轨** κ 非跨**模型** κ, 勿混。J1 import 用现有 lazy 模式 (`tone_validation.py:908` 已复用二函数, 无循环依赖); 注意 Krippendorff 返裸 float、Cohen 返 dict 取 `['kappa']`。

### ✅ 审核确认可直接照做 (无需改)
- 宽前缀 D4 路由**完全正确**: 实跑并集 3153 列, per-model 残留「未知」= **0**, **0 误路由** (llm_vote_* 不以模型名开头), **不破坏既有路由**, 插入位置安全。
- rwolf 核心语法/结构 (indepvar 多变量族 / method(reghdfe) abs cluster) 与 `substance/18:53-104` 逐字一致; 镜像深度 :53-104 正确。
- `_EXPECTED_ROOT_DO=19`(`:680`) / 根级非递归 glob(`:482`) / `matrix:47==19` / `b_route:176==145` / 18_substance 多-indepvar `e(RW_<iv>)` 抽取范围 — 全部实况一致。
- Cohen κ 对 2-vs-3 分类 pairwise 可行 (`sorted(set)` auto-union, 不崩)。
- gate 新测试无 collection 冲突; paper_spec schema 无严格未知键校验 (E1-E5 安全); papers/*.py 零 per-model 消费 (无需接线); net_tone 不被 geography 误 rollup (显式列名清单)。
- 层字母 A-J 唯一连续无冲突; 三类 overclaim 已清除; §附 台账 13 条正文全落实。

---

## §12. 结果审核修正 (已实现代码的最终审核, 2026-07-02, 已全部应用)

> 实现完成后又跑 **12-agent 结果审核 (真跑 3144 列面板 / 真 aggregate_panel / 真 build-replication / 真 Krippendorff)**。codebook/encode/stata_export/validation-kappa 四层**真跑零缺陷**; 抓出 4 confirmed major + 若干 minor, **均已修复并验证**:

1. **[major, 真 bug] 27_tableA12 路径**: 原 `$data_dir="../data"` (抄自子目录) → master 下 `use` r(601), wire-ahead 表**永产不出**。→ 全文重写为根级约定: `capture confirm file "data/processed/_prepared_panel.dta"` + 回退 `46_panel_yearly_full.dta` + `$tables_dir="output/tables"` (镜像 26/34/21)。附带修 tempname 非短路 (嵌套 if 防 `&` 不短路致 rowsof 作用于不存在矩阵 r(111)) + header `{{MAIN_DV}}` 双替换。
2. **[major] 7 处陈旧文档计数**同步为 根级 20 / 子-do 19 / 总 146: `CLAUDE.md`(build-replication 19→20 · 142→146 分解) / `stata_runner.py`(docstring "19 .do"→20 自相矛盾修 · 注释 "18 子"→19) / `stata_templates/README.md`(19/19→20/20 + 加 A12 行) / `papers_assets/bank_fintech_tone/README.md`(19→20) / `build/manual_facts/key_stats.md`(142→146)。
3. **[major] `compute_cross_model_kappa` 无 gate** → 新建 `tests/test_cross_model_kappa.py` (5 测试: 非负码 / 两组产出 / 'llm' 剔除 / finbert2 参与 / **-1 哨兵回归断言**)。
4. **[minor] `test_stata_replication_matrix` master-ref** 漏 27_tableA12 → 加入 expected_subdo + docstring。

**最终验证**: κ gate 5/5 · stata roundtrip (27_tableA12 路径修复后仍干净实例化 20/20+19/19) · 计数 146 · ruff 全清 · **定向 A/B (10 既有测试文件) 决定性证 0 新增失败** (A≡baseline 各 8 既有红灯; A-only 差集空)。

