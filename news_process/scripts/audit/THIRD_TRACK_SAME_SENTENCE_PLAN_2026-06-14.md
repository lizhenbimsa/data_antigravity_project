# 第三轨"银行+金科同句"情感轨 · 执行计划（已锁定决策版）

> 2026-06-14 · 权威执行计划。基于 16 子系统映射工作流（20 agent / 2.4M tok）+ 3 路对抗批判 + 综合，
> 并经实测语料校准。本文件是后续实施的单一事实源；列数/计数以实读为准。

## 0. 已锁定的 4 个决策（用户 2026-06-14 拍板）

| 决策 | 选择 | 含义 |
|---|---|---|
| 回退语义 | **回退全文（镜像 ctx）** | 无"银行∧金科同句"时 `content_ss = 全文 body`，与 ctx 回退公理完全一致；`ss_is_fallback=True` |
| 覆盖范围 | **全平价** | ctx 在全部阶段/IV/校验/Stata 模板/11 篇 paper_spec 做的，cooc 全做一遍，作并列第三主轨 |
| LLM 成本 | **现在批准线上付费跑** | stage 21 cooc 首跑线上（缓存现 0 条 ss）；golden 随之重生 |
| 命名后缀 | **`_ss`**（同句，3 字符） | 内部/parquet/Stata 统一 `_ss`；文本列 `content_ss`；标签"(银行+金科同句)" |

### `_ss` 命名的连带简化
- `_ss`(3) **短于** `_ctx`(4) → 任何 ctx 能塞进 32 字符的列，ss 一定也能 → **无需新增缩写规则**（取消原 `_cooc`→`_co` 工作项）。
- 唯一保留：Stata 写前**三元组唯一性断言**（full / ctx / ss 截断后不撞名），扩 `test_dta_name_sanitizer_consistency`。

### 回退=镜像ctx 的连带简化
- 面板聚合**可共享 `n_articles` 分母**（不需独立 `n_articles_ss`），与 ctx 同口径 → 工作流⑥比"空串→NaN"路径更简单。
- 唯一例外：stage 24 Spearman 独立性诊断仍**门控 `ss_is_fallback==False`**（避免回退行 ss≡full 污染相关性判定）。

## 1. 第三轨定义

| 轨 | 文本列 | 取句规则 | 回退 |
|---|---|---|---|
| full | `content_full` | 标题+全文 | — |
| ctx | `content_ctx` | 标题+含**目标银行**句 ±1 句窗 | 无银行命中→全文 |
| **ss（新）** | **`content_ss`** | 标题+**同句内同时含 目标银行∧金科词** 的句 ±N 句窗 | 无共现→**全文**（镜像 ctx） |

判定逻辑复用 `scripts/audit/measure_bank_fintech_cooccurrence.py`（`sent_has_bank`=stage11/13 同款否定+短名排除；`sent_has_fintech`=`load_fintech_dict` AC 自动机 1506 词）。生产函数与审计脚本**同口径**。

### 实测覆盖（disk 1170 篇，`cooccurrence_measurement.json`）
- 零共现文章 **14.27%**（→回退全文，少数）；主题漂移率 **65.76%**（银行句仅 34% 提金科→ss≠ctx，独立信号成立）；每文均 2.75 句、中位 2 句；直方图 0:167 / 1:232 / 2:259 / ≥3:512。

## 2. 12 个工作流（依赖排序 · 零遗漏清单）

### ① 核心提取原语 — 免费 【阻塞性根依赖】
- `core/text/entity_context.py`：新增 `extract_bank_fintech_cooccurrence(text, target_aliases, fintech_ac, sentence_radius, fallback_char_radius, negation_ac, short_name_exclusions, context_window)`。复用 `_split_sentences`/`_merge_intervals`/`has_unexcluded_occurrence`。回退=空→由 stage 13 回退全文 body（镜像 ctx）。
- `_char_level_fallback` 加可选 `fintech_ac`（<3 句短文本，DRY）。
- ⚠ 不对称口径写进 docstring：银行侧过滤否定/短名；金科侧裸 AC。

### ② 配置接线 — 免费（可与①并行）
- `config/filtering.yaml`：`context_window.ss_sentence_radius: 1`（默认同 sentence_radius）+ 注释。
- `config/paths.yaml`：确认 `fintech_dict_file`；stage 13 加路径回退解析。
- `config/sentiment.yaml`/`panel.yaml`：注释 ss 结构性 always-on，无 compute 开关。

### ③ Stage 13 物化（content_ss 单一事实源）— 免费
- `pipeline/text/ctx_materializer.py::materialize_content_ctx`：content_ctx 之后，模块级 `load_fintech_dict`（try/except 优雅降级）；逐行产 `content_ss=prepend_title(title, ss_body)`（ss_body 空→全文 body）；新列 `content_ss`+`ss_is_fallback`（=ss_body==full body，镜像 ctx_is_fallback）；幂等守卫扩 content_full/ctx/ss + 2 flag 全在；读 `ss_sentence_radius`；加完成日志。
- `pipeline/text/__init__.py` docstring 更新；shim 不改。

### ④ 情感 21/22/23 + herd 24 + 其它文章级测度 — **21 付费**，余免费
- `tone_llms.py`(付费)：`iter_article_track_prompts` 加 `'ss'`；`per_model_cols` 预分配加 `_ss`；逐模型归档/ensemble(`llm_verified_ss`/`llm_sentiment_ss`/`innovation_*_ss`/`prob_score_ss`)/logit/日志加 ss；`_aggregate_track` 第三次调用；**冻结 prompt v8**（只换 content 实参）；缓存键已按轨分区；门控并集 `verified_full|ctx|ss`。
- `tone_words.py`(免费)：`_dual_analyze` 加第三路；~12 抽取循环+`merge_stats` 加 `_ss`；`_empty_article_result` 加 `_ss` 键；分类报告标签"银行+金科同句"；IDF 跨轨共用 content_full。
- `tone_berts.py`(免费/本地)：轨循环(~1109)加 `(output_ss,'_ss')`；建 `content_ss_list`、`bert_num_windows_ss`；缺列优雅跳过。
- `herd_decay.py`(免费)：**3 处循环**(441-447、491、601)加 `'ss'`；init+SENS 网格；Spearman 扩 3 路但门控 `ss_is_fallback==False`。
- `numerical_intensity/lexical_complexity/forward_looking/lm_non_sentiment`：泛型，由 tone_words 用 ss 文本调用。
- `article_staleness.py`：surface_staleness_ss 免费加；semantic_staleness_ss 依赖 ss SBERT（见⑫/可延后）。

### ⑤ 特征 14/15 — 14免费 / 15低成本付费
- `fintech_intensity.py`(免费)：泛型加 content_ss → `fintech_intensity_score_ss`/`intensity_verified_ss`；扩断言。
- `policy_alignment.py`(低付费·嵌入)：`_cosine_for_spec` 加 ss → `policy_cosine_sim_ss`+`policy_cosine_sim_t2v_ss`。

### ⑥ 面板聚合：参数化循环 + 静态枚举（81+ 处，最高静默漏列风险）— 免费
- 参数化：`encode.py`(~22)/`runner.py`(~23)/`geography.py`(~6,含 `_expand_track_templates`)/`attention_media.py`(~9) 每个 `['_full','_ctx']` 加 `'_ss'`+`if f'col{track}' in df.columns` 守卫。
- **静态枚举(grep 抓不到，必手改)**：`encode_collab.py` `cell_id_full`/`'full'` 字面量(95,166-204,227-241,267-273)；`runner.py:194` 元组；`verified_universe.py`(ss 同(docid,bank)子集自动继承 verified)；`dedup_sensitivity.py` attention_index_* 静态构建。
- `encode.py` 专项：`hw_by_track` 加 `_ss` 键(防 KeyError)；`_aggregate_ss_diagonal`；`tone_gap_*_ss`；ss_is_fallback 处理镜像 ctx_is_fallback。共享 n_articles 分母（回退=镜像 ctx）。
- balance_panel：ss 计数列进零填充，比率/语调列保持 NaN。
- **强制自动扫描**：每个双轨族 F 必有 F_ss 或显式 skip 注释。

### ⑦ 工具变量列 — 免费
- `iv_extensions.py`：9 轨循环加 `_ss`；静态 `shift_*_by_track` 加 `_ss` 键；ss LOO/zone/clarity/disp。
- `llm_peer_iv.py`：静态 `_ART_TONE_BY_TRACK`(831) 加 `'_ss':'llm_vote_score_ss'`；循环+`_primary_maps`。
- `iv_did.py`：循环 235/409/554 加 `_ss`。
- ⚠ 铁律：full×ctx×ss **禁混进同一 over-id Hansen J**；三轨各自 just-identified 并排。

### ⑧ 校验 + 审计 — 免费
- `inter_track_kappa.py`(39a)：双轨→**三轨**；推荐 pairwise Cohen κ 出 9 行(含 pair 列)。
- `construct_orthogonality.py`：`DIMS_CTX` 加 `DIMS_SS`；3×3 NMI + `39c_*_ss.parquet`。
- `lexical/lm_discriminant_validity.py`：`INDICATORS_CTX` 加 `INDICATORS_SS`；`39e_*_ss.csv`。
- `stata_audit.py`：233 加 `llm_vote_tone_ss`；309/353/413 循环；相关 376-379→3 路 pairwise。
- `entity_masking.py`：`TRACKS=['full','ctx']`(129) 加 `'ss'`(自动扩 7+ 下游)。
- `tone_validation.py`/`prompt_sensitivity.py`/`llms_evaluation.py`：循环+docstring 三轨化；McNemar→3 pairwise；词典/BERT 校验同步。

### ⑨ Stata 导出 + 标签 + codebook — 免费
- `stata_export.py`：~60 个 `_ss` HEURISTIC_LABELS、~12-25 个 core_patterns（核心 ≤2048 守卫）；`_ALLOWED_TRACKS` 加 `'ss'`（实在 codebook）；**无需新缩写规则**（_ss≤_ctx）；**加写前唯一性断言**(三元组)。
- `export.py`：~100 个 `_ss` STATA_LABELS；`REQUIRED_PANEL_COLUMNS` 防御 `.get()`。
- `codebook.py`：`_ALLOWED_TRACKS` frozenset 加 `'ss'`；VariableMetadata `_ss` 条目；6 个 `_FRAC_SPECS` ss 条目；**修 nullable-float `len()` xlsx 崩溃守卫**。
- `generate_all_labels.py`：`_ctx` 分支后加 `elif endswith('_ss'): track='(同句共现)'`。
- `papers/_common/tables.py`：`sanitize_stata_columns` 三元组碰撞核验。

### ⑩ Stata 模板 + paper_spec + 复现包（全平价）
- `stata_runner.py:208` `_VALID_SPEC_VALUES['MAIN_SENT_TRACK']` 加 `'ss'`。
- 模板：`20_tableA1_inter_track_kappa`(加 ss κ 行)；`21_tableA2_main_spec_switch` / benefit_society `21_tableA2_attitude_track_switch`(`foreach sent in full ctx`→`full ctx ss`，6→9 reghdfe，mgroups/mtitles 6→9)；`31_figure2_coefplot_dual`(6→9)。
- `derivative_replication.py`：加 ss 占位符(ATTITUDE_SS / MAIN_DV ss 孪生)。
- 11 篇 `paper_spec.yaml`：ss 进 `inference.families.sentiment_tracks` + `identification.iv` ss 镜像。
- 新增 `*_ss_*` 模板则同步 +N 计数锁。

### ⑪ DAG/schemas/orchestrator — 免费（无结构变更，仅核验）
- 不增删阶段；STAGES_MAIN=15 / **STAGES_VALIDATION=16**（实测; 计划初稿误写 17 — temporal_mask_test 已于 2026-06-12 移除 17→16）不变；OUTPUT_REGISTRY=15 keys 不变(列加在既有文件内; stage 39c/39d/39e 的 `*_ss` 诊断文件复用既有文件名/或 EXPECTED_NO_OUTPUT, 不新增 registry 项)。dag.py docstring 提 content_ss；`test_dag_consistency` 锁 **15/16**。

### ⑫ 测试 + golden + 盘面产物 — 测试免费 / golden 付费
- 50+ 测试硬编码 `['_full','_ctx']`：优先 `parametrize('track',['_full','_ctx','_ss'])`；fixture 加 content_ss(含 1 零共现行测回退)。
- `test_v3_2_panel_columns` 列数下界 1400→**据实测面板 1658 列 + ss 增量据实重算**(勿用估值)。
- **golden(付费·延后)**：①-⑨ 完成后线上跑 stage 13→21→…→46 播种 ss 缓存→`generate_golden_snapshot.py`；schema_version 2→3(版本感知 loader，单一 golden)；重生 codebook.{csv,json,md,xlsx}+`46_*_labels.do`；此后 `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 复现。

## 3. 免费 vs 付费
- 免费(~90%)：①②③核心+⑤-14+⑥81+循环+⑦IV+⑧校验+⑨标签/codebook+⑩⑪⑫测试代码。
- 付费：stage 21 ss LLM(主)；stage 15 ss 嵌入(低)；stage 30a SBERT ss(最贵收益低，可延后)；golden 重生那次线上跑(M0 gate)。
- 闸门：`NEWS_PROCESS_LLM_OFFLINE=1` 防偷跑；批准后线上；事后 `verify_stage21_cache_coverage`。

## 4. 计数锁 & golden 影响
- `_ALLOWED_TRACKS` 加 `'ss'`；`MAIN_SENT_TRACK` 加 `'ss'`；`test_v3_2_panel_columns` 1400→~1500；golden schema_version 2→3；模板 142 仅新增 ss 模板才 +N；STAGES 计数不变(显式核验)；`test_dual_track` 列数锁逐 bump。

## 5. Top 风险 + 缓解
1. 【阻塞】①全新实现，先建+单测+与审计脚本对齐再跑下游。
2. 【静默漏列】81+循环+~6静态枚举漏一=无报错缺列 → 强制自动扫描。
3. 【付费/确定性】stage21 ss 首跑必线上；冻结 prompt v8。
4. 【Stata 静默覆盖】三元组截断撞名 → 写前唯一性断言(_ss 短于_ctx，风险已最小)。
5. 【相关性/回退】实测零共现仅 14.27%、漂移 65.76% → ss 仍独立(已缓解)。
6. 【覆盖/功效】全量下 ss 非空率需关注 min-N 阈值；上线前 `measure_bank_fintech_cooccurrence` 量化每年覆盖。

## 6. 分阶段实施 + 检查点
- **P0 基础(免费)**：①②③ → 单测 stage 13 content_ss → **检查点 A**（盘面物化验证、覆盖率打印）。
- **P1 文章级三轨(21 付费/余免费)**：④⑤ → 检查点 B（缓存 miss 探针、ss 列非空）。
- **P2 面板/IV/校验(免费)**：⑥⑦⑧ → 自动 F_ss 扫描 → **检查点 C**（面板 ss 列齐全）。
- **P3 导出/模板/spec(免费)**：⑨⑩⑪ → 测试三轨化⑫(测试码) → ruff+定向 pytest 绿。
- **P4 付费收尾**：线上 stage 21 ss 跑 → golden 重生 → repro 绿 → 提交推送。

---

## 7. 平价完整性审计修订（22-agent, 2026-06-14）

> 16 子系统独立普查 + 5 路对抗遗漏猎手 + 综合裁决（`tasks/wge1n86za`）。
> **裁决 = GAPS_FOUND**：架构稳健、~82% spec 覆盖且多数声明经代码核实属实；但确证 **11 个缺口** 须补进计划方达"零遗漏"标准。另**澄清 6 个被误报的非缺口**。本节为修订增量，前 6 节工作流主体不变。

### 7.1 已核实属实的计划声明（无需改）
- ✅ **`_ss(3)≤_ctx(4)` 不溢出**：实测活面板 1658 列，最长 `_ctx`=`prov_leave1out_dict_avg_tone_ctx`(32)→`_ss`=31；最长 `_full`=33→`_ss`=31；**零 `_ss` 超 32、零三元组截断撞名**。无需新缩写规则；写前唯一性断言仅作前瞻护栏（sanitizer 用 md5 后缀非裸截断）。
- ✅ **verified_universe ss 自动继承**：`restrict_to_verified` 按 `(docid,target_bank)` join，track-agnostic（:48,:66），ss 列零改自动进 verified 门。
- ✅ **嵌入缓存键无碰撞**：`policy_alignment.py:367` 键于 (model, **text**, prompt_version)，content_ss 文本不同→独立缓存项，无需 track 标签。
- ✅ **DAG 无结构变更**：STAGES_MAIN=15 / OUTPUT_REGISTRY=15 keys / 列就地加在既有 parquet（仅 §⑪ 计数 digit 17→16 须订正）。
- ✅ **prompt v8 冻结可行**：`iter_article_track_prompts` 模板共享、content 是唯一变参；交换 content_ctx→content_ss 不触模板。
- ✅ **81 参数化循环非逐一缺口**：`for track in [...]` 自动扩；真正承重风险=6 处静态枚举（见 7.3-A1）。

### 7.2 BLOCKER（spec 须绑定到具体编辑 + 验收测试；本就是 P0/P1 首做项）
- **B1 §① 核心函数**：`extract_bank_fintech_cooccurrence()` 代码确不存在（grep 仅见于本 .md）。**新增验收门**：单测对 disk 1170 篇断言 ss 选句与 `measure_bank_fintech_cooccurrence.py` **逐字节一致**（同 `_split_sentences`/同 NEGATION_AC+SHORT_NAME_EXCLUSIONS/同 1506 词 fintech AC）；`_char_level_fallback` 加可选 `fintech_ac`，并把 `entity_context.py:188` 既有 `extract_entity_context` 调用补 `fintech_ac=None`（向后兼容）。= 检查点 A 的阻塞测试。
- **B2 §③ stage 13**：绑定具体编辑：(a) `:72` 后加 `load_fintech_dict` try/except（失败→`FINTECH_AC=None`）；(b) `fintech_dict_file` 路径回退**镜像 `:142` bank_names_file 模式**；(c) ctx 循环后(`:177`)加 ss 抽取循环→`content_ss=prepend_title(title, ss_body)`，ss_body 空→full body；(d) `ss_is_fallback=(ss_body==full body)` 镜像 `:187-190`；(e) **两处幂等守卫都改**：主守卫 `:102-103`(3→5 列) + **legacy-schema 回填分支 `:113-133`**(也回填 content_ss/ss_is_fallback)；(f) ss 计数一致性断言镜像 `:192-194`；(g) ss 完成日志镜像 `:198-202`；(h) 注明 **FINTECH_AC=None ⇒ ss_is_fallback 全 True**。
- **B3 §④ tone_llms**：补两项关键 spec：(1) `run_all_llms` 的 `results_map[i]` 初始化须含 `ss` 键 `{full:{},ctx:{},ss:{}}`（否则 KeyError）；(2) `_aggregate_track` 第三次调用（`:1837` ctx 后）+ 赋全部 ss 列。`iter_article_track_prompts` 读 `row.get('content_ss', content_full)`（缺列回退）。**门控决策**：verified 门保留并集 `v_full|v_ctx|v_ss`；诊断 breakdown **扩 7 互斥态**（full_only/ctx_only/ss_only/full_ctx/full_ss/ctx_ss/all_three）+ 7 行日志。加 **prompt-freeze 回归测试**（ss prompt ≡ ctx 模板换 content）。
- **B4 §④ stage 22/23/24**：(1) tone_words 明列全部 ~12 个 `['_full','_ctx']` 抽取循环(`:1417/1431/1437/1442/1450/1459/1466/1470/1477/1481/1491/1500`)+stats init(`:1346`)+merge_stats(`:1512-1535`)+`log_classification_report` track_label 三元(`:1544-1546`→加"银行+金科同句")全加 `_ss`；`_empty_article_result` 返回 `_ss` 键。(2) **herd_decay Spearman 改 3 路 pairwise**(full-ctx/full-ss/ctx-ss)，ss 腿额外门控 `ss_is_fallback==False`；**stage 24 须摄入 ss_is_fallback 列**（来自 stage 13）；`:491` 元组解包加 `('ss', ss_counts)`；诊断 CSV(`~:600-629`)加 ss 行。

### 7.3 HIGH（真·计划遗漏，须补 spec）
- **A1 §⑥ cell_id_ss 设计决策 + 自动护栏**（最高静默漏列风险）：
  - **决策（定）**：**ss 不做 D2/D4 collab-cell 分解**——`cell_id` 分类的是 substantiveness/locus/collab 这类 full/ctx 锚定的 LLM 属性，ss 是纯情感轨。`encode_collab.py:522-523`(cell_id)+`:936 TRACKS` 保持 2 轨；仅情感族得 `_ss`。加注释 `# cell_id_ss intentionally NOT produced` + 测试断言**无** `cell_id_ss`/`n_articles_cell_*_ss` 泄漏。
  - **"强制自动扫描"落地为真工具**：新建 `scripts/audit/check_static_enums.py`——grep 非参数化循环内的 `'full'`/`'_full'` 字面量，断言每个 base 有 `_ss` 兄弟**或** `# no-ss-track` skip 注释，**wire 进 pytest**（漏一个静态枚举 → 测试 FAIL，替代不可信的"人工 review"）。其它静态枚举：`runner.py:194` 元组→3 元；`llm_peer_iv.py:831 _ART_TONE_BY_TRACK` 加 `'_ss':'llm_vote_score_ss'`(先确认 stage21 真出此列名) + `:908 _primary_maps`；`dedup_sensitivity.py:174/229/240` 加 `fintech_intensity_score_ss`+`attention_index_ss_<v>`。
- **A2 §⑩ Stata/paper_spec 全平价缺口**：
  - **TONE_VAR_SS（破"全平价"的静默项）**：`derivative_replication.py` 加 `ATTITUDE_SS`(benefit=`benefit_mean_ss`)，并为用 `TONE_VAR` 的 2SLS 论文（strategic_diff / llm_peer）**定 `TONE_VAR_SS`**（原计划漏，会让这两篇 ss 不全平价）。
  - **提供一份样板**：给 `bank_fintech_tone/paper_spec.yaml` 写 BEFORE/AFTER（`inference.families.sentiment_tracks` 加 `llm_vote_tone_ss`；`identification.iv` ss 镜像=机械 `_ctx→_ss` 后缀swap，如 `prov_leave1out_tone_ctx→_ss`/`bartik_type_iv_ctx→_ss`），其余 10 篇照此机械化。
  - `stata_runner.py:208 _VALID_SPEC_VALUES['MAIN_SENT_TRACK']` 加 `'ss'`；4 个模板 `foreach sent in full ctx`→`full ctx ss`、mgroups/mtitles 6→9，且**第 3 列用 `capture confirm variable *_ss` 守卫**（ss 列运行期缺失则优雅降级，不崩表）。
- **A3 §⑧ 校验/审计 spec 未定义**：`DIMS_SS = copy(DIMS_CTX)` 做 `_ctx→_ss` swap（继承非新维度），`INDICATORS_SS` 同理；`inter_track_kappa` 出 **9 行**+`pair` 列(full_ctx/full_ss/ctx_ss × 3 维)，**FWER 用 Holm 跨 3 对**；记录**有意不对称**（construct_orthogonality 只对 full 做 3×3 分类、ss 仅出 NMI 诊断）；核验 `entity_masking` 7+ 下游循环(`:156/299/496/604/756/777/812/827`)确为 `for track in TRACKS` 参数化（`:129` 加 `'ss'` 自动级联）。`config/paths.yaml` 加 `fintech_dict_file`（确认实际路径，1506 词字典）。

### 7.4 MEDIUM / LOW
- **M1 §⑨ 标签 fail-loud**：`codebook._ALLOWED_TRACKS` = `frozenset({'','full','ctx','ss','dual'})`（**加性，保留 'dual'**）；机械规则=每个 `_ctx` 标签 `.replace('_ctx','_ss')`+后缀文案"(银行+金科同句)"；加 `test_stata_export_labels_completeness` 断言 `count(_ss labels)==count(_ctx labels)`（漏标签→FAIL 而非静默退泛型名）；写前三元组唯一性断言 + 扩 `test_dta_name_sanitizer_consistency` 到 3 元组。
- **M2 §⑫ 测试/golden 顺序**：grep 实列 50+ 测试清单（非估值），逐个分类 parametrize/手改/跳过；**单一 conftest `content_ss` fixture 含≥1 零共现回退行**供所有参数化测试继承；golden 顺序明确——**首次 ss stage-21 跑须 `NEWS_PROCESS_LLM_OFFLINE` 不设/=0** 以播种 ~3510 ss 缓存→再 `generate_golden_snapshot.py`→此后离线字节稳定；版本感知**单一 golden** loader（schema_version==2 时丢 `_ss` 列）；3 个非确定网络中心度列及其 ss 派生仍排除字节级 repro。
- **L1 §⑪ 事实订正**：STAGES_VALIDATION **16 非 17**（已订正于 §⑪/§4）。

### 7.5 残余风险（实施纪律层，非计划缺口）
1. **实施就绪度=0%**：所有"缺口"本质是"计划 vs 无代码"——本审计只能验 **spec 平价**，不能验**行为平价**。编码后**必须再跑一次 code-vs-code 平价审计**，再 golden 重生。
2. **静默漏列**仍是 #1 风险，直到 `check_static_enums.py` 落地并入 CI。
3. **付费顺序**：§0"现在批准" = 成本预批，**实际 ss stage-21 单次跑放在 P4**（播种缓存+重生 golden 一气呵成），避免误早跑/脏 golden 提交——已在 §6 P4 明确。
4. **全量外推**：14.27%/65.76% 来自 1170 篇 disk 小样；全量 17M/T=18 须**逐年重测** ss 非空率与 min-N，再断言 ss 识别可行。
5. **semantic_staleness_ss 延后**（stage 30a SBERT，低 ROI）：`article_staleness.py:491` 须优雅跳过（NaN）直到 30a ss 上线——**文档化**，勿被审稿读成平价漏洞。

### 7.6 平价矩阵（covered/partial/missing，各子系统）
text13:2/4/3 · llm21:4/3/3 · words22:3/12/9 · bert23:1/3/3 · herd24:3/5/3 · feat14-15:30/3/12 · article:12/13/15 · panel:36/3/7 · panel-feat:7/4/4 · IV:3/6/9 · geo-attn-net:16/5/2 · stata-export:2/8/8 · validation:1/11/22 · templates-spec:3/6/11 · dag-runner:20/4/6 · tests-golden:1/2/5。
（"missing/partial" 多为 spec 未绑定具体行号，非设计漏洞；7.2-7.4 已逐条补绑。）

---

## 8. 最终 GO 审计 + 注释/文档平价补订（18-agent, 2026-06-14, task w1g4aq05w）

> 第三轮（最后一轮）审计：5 修订核验 + 8 **注释平价**普查 + 4 终局对抗 + 裁决。
> **裁决 = GO_WITH_AMENDMENTS**：§0-6 架构稳健，§7 的 11 项修订经抽样核实**准确**（STAGES_VALIDATION=16 确锁于 `test_dag_consistency.py:120`；`_ALLOWED_TRACKS` 确无 'ss'；核心函数确不存在）——这些**不是阻断, 就是 P0-P4 路线图本身**。唯一**实质欠缺 = 注释/文档平价**（正是你本轮新增的维度）。条件：**新增 §⑬ 注释/文档平价工作流, 与 _ss 列同一 PR 落地**，即 GO。

### 8.1 新增工作流 §⑬ 注释/文档平价 — 免费，必须与 _ss 列同 PR
**(A) 新注释（镜像 ctx 孪生注释）**
- **学术锚点**（计划原缺）：ctx 在 `ctx_materializer.py:17-21` 引 Hassan et al. (2019) QJE §III.B proximity-based attribution。`extract_bank_fintech_cooccurrence()` 与 content_ss 物化 docstring 须配**同句共现**锚点。候选：**Gentzkow & Shapiro (2010) ECMA**（文本共现/co-mention 计量）+ **Dougal et al. (2012) RFS**（媒体共提及情感）；与既有 proximity 谱系 Sautner et al. (2023) JF / Hassan (2019) QJE 并列。⚠ **落地前须 Crossref 核验 DOI**（项目铁律, 见 [[literature-anchors-2026-06-13]]）。
- **不对称口径注释**：docstring 明示 银行侧=否定+短名过滤 / 金科侧=裸 AC(1506 词)（§① 已要求, 确保真落地为代码注释）。
- **回退公理镜像注释**：content_ss/ss_is_fallback 注释镜像 ctx_is_fallback——"空同句匹配→content_ss=全文 body, ss_is_fallback=True (镜像 ctx 回退公理)"；并把 **FINTECH_AC=None ⇒ ss_is_fallback 全 True** 写成**代码注释**（非仅计划文字）。
- **verified 并集注释**：tone_llms 三键 results_map + `v_full|v_ctx|v_ss` 并集门须内联注释说明**为何并集(任一轨过即过)而非 AND**。
- **标签文案**（用户可见, 属注释平价）：每个 `_ss` 标签带中文后缀 **"(银行+金科同句)"**（HEURISTIC_LABELS/STATA_LABELS `.replace('_ctx','_ss')`）；`generate_all_labels.py` 加 `elif endswith('_ss'): track='(同句共现)'`；tone_words `log_classification_report` track_label 加"银行+金科同句"。

**(B) 陈旧注释订正（双轨→三轨）—— 实测 733 处 / 106 .py 文件**（前轮低估为 85/142/625）
- tier-1（公共 docstring/标签, **本 PR 必改**）：`entity_context.py:49,67`；`tone_llms.py:2,16,18,679,698,710,741,752,1500,1650`（⚠ `:710 total_tasks ×2→×3` 是**功能性**改动非纯注释）；`herd_decay.py:2`+设计段；`tone_words.py` docstring+循环注释；`tone_berts.py` log+注释；`encode.py`(36 处)；`codebook.py:162,488` 框架措辞；**`iv_extensions.py:501-502,567-569`**（Hansen J: "full+ctx 两支"→"full/ctx/ss 任意两轨"；"双轨互为稳健性"→三轨）；`inter_track_kappa.py:1-23,12,21`；`stata_audit.py:346-411`；`construct_orthogonality.py:363`；`lm_discriminant_validity.py`；`entity_masking.py:2,14-23`；`tone_validation.py:1889-1956`；`prompt_sensitivity.py:12-568`；`llms_evaluation.py`；`stata_runner.py:162`+MAIN_SENT_TRACK doc。
- tier-2（测试模块名/docstring, 决定保留历史名 vs 改名）：`test_dual_track.py`/`test_24_herd_decay_dual.py`/`test_dual_track_parity_fixes.py`/`test_benefit_society_dual_track.py` —— 至少 docstring 中"仅两轨"断言须随 ss 列改为三轨。
- ⚠ 仅**注释/docstring 散文**改；被参数化的**代码字面量** `['_full','_ctx']` 保持代码（由 §⑥ 处理）；`encode_collab` cell_id 注释须明写 **"(cell_id 有意仅 full/ctx, ss 不分解)"** 而非泛"双轨"。

**(C) CLAUDE.md（版本权威源, 计划原零提及）**
- "Current version" 顶部加 **v3.9.0 三轨条目**：`_ss 银行+金科同句共现轨 (content_ss / suffix _ss / 标签 "(银行+金科同句)"); 回退=镜像 ctx→全文 body, flag ss_is_fallback; LLM prompt v8 字节冻结; 全平价并列第三主轨`，含 4 锁定决策 + M0 付费重跑 + golden schema 2→3。
- `:71` "真双轨 (*_full / *_ctx)" → 三轨 (+content_ss)；`:73` Sentiment methods 循环 `['_full','_ctx','_ss']`；`:41` stage21 确定性"充要条件…双轨"→三轨 + 缓存数 7020→7020+~3510 ss。
- 明确 **STAGES_MAIN=15 / STAGES_VALIDATION=16 不变**（"三轨为列内扩展, 无阶段增删"）；列数/标签/codebook 重生 note。

**(D) 强制**：扩 `scripts/audit/check_static_enums.py`（§7.3-A1）或加姊妹 lint——本 PR 触及文件若仍含裸 `双轨/两轨` 注释（无 `# legacy (full/ctx) 示例` 豁免标记）即 **测试 FAIL**。把"双轨→三轨 sweep"绑进**同一 PR**（不延后到"v3.10 注释审计"），因用户长期指令要求混合语言文件注释始终正确。

### 8.2 三项小型功能补订（并入既有工作流）
- **§7.4-M1 补**：显式把 `codebook.py:488 _ISS_TRACKS`（2 轨静态 dict, 驱动 :489-504 substantiveness-subset VariableMetadata）加进静态枚举编辑清单 → `{'_full':..,'_ctx':..,'_ss':('同句','Same-sentence')}`；check_static_enums 作兜底。
- **§⑦/§7.3 补**：Hansen J 铁律不止是"决策"——绑定 `iv_extensions.py:501-502,:567-569`（及 `llm_peer_iv.py` 镜像）的**注释文本**改写（防未来 coder 把"full+ctx"读成穷尽对 = 识别 footgun）。
- **§①/§③ 补**：把选定的同句学术锚点**写进计划本身**（现 §① 只引审计脚本作代码出处, 非文献锚点）。

### 8.3 B-项残余 under-spec（编码时补全, 非阻断）
- **§③ B2(e) legacy-schema 回填策略（原 NOT_CLOSED）定**：旧数据缺 ss 列时，stage 13 回填 **`ss_body=full_body` + `ss_is_fallback=True` + 警告日志**（**不**在回填路径重算 ss）——保幂等性（旧 schema 重跑行为不变）。
- B1/B2/B3/B4 的伪代码细节（results_map 三键初始化位置、`_aggregate_track` 第三调用点、tone_words 12 循环逐一行号、7 态诊断 schema）= **P0-P3 编码时按 §7.2 行号落实**；编码后**强制 code-vs-code 平价复审**（§7.5 #1）再 golden。

### 8.4 最终结论
**GO_WITH_AMENDMENTS** → 补入 §⑬（注释/文档平价）+ 8.2 三项 + 8.3 回填策略后，计划达"功能 + 注释 双重零遗漏" spec 标准，可按 §6 P0-P4 开工。**唯一 INFO 级保留**：本审计仍是 spec 平价（代码 0% 实现）；行为平价须编码后再审。全量 17M/T=18 ss 逐年覆盖在 P4 付费跑前用 `measure_bank_fintech_cooccurrence` 分年度实测把关。
