# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** is a research data pipeline that transforms raw Chinese news articles into panel datasets for econometric analysis. It processes bank and fintech news through multiple stages: preprocessing, classification, sentiment analysis (LLM/dictionary/BERT), and panel construction.

**Current version**: v3.8.0 (2026-05-31, remove-title-track, 移除提交 `6382cc67`)。

**v3.8.0 BREAKING** — 删除独立 `_title` 情感轨及全部产物, 标题改 prepend 进 full/ctx 两轨：
- 删 stage 39g (`track_discriminant_validity`) → STAGES_VALIDATION 18→17, 注册阶段共 **36** (STAGES_MAIN 19 + STAGES_VALIDATION 17), thin shim 40→**39**。
- 删 9 个 title 稳健性 Stata 模板 (`25_tableA8` / `26_bs`) → Stata 模板 104→**95**, replication 包 .do 15→**14**。
- 删 `core/text/title_indicators.py` + stage 13 `_add_title_indicators` + title-only migrate/audit 脚本与测试。
- 删所有 `*_title` 情感 panel 列 (`tone_gap_title_full` / `frac_title_*` / `hw_title` / `llm_peer_tone_iv_title` 等) 及 LLM/BERT/词典 title 路径; 下游多轨循环 `['_full','_ctx','_title']` 收为 `['_full','_ctx']`。
- 新增 `core/text/entity_context.py::prepend_title()`; stage 13 `ctx_materializer` 物化 `content_full`(=标题+正文) / `content_ctx`(=标题+实体窗口), 原始 `内容` 列不动; tone_words/tone_berts 改读 prepend 后文本。
- **保留** (非情感轨, 分类/β 显著性信号, 仍活跃, 勿连带删除): `target_bank_in_title` (`news_bank.py`) / `fintech_in_title`+`in_title` (`news_fintech.py`) / `headline_frac` (`controls.py`)。

**2026-06-05 后续结构移除** (post-v3.8.0, 非 v3.8.0 内容):
- 整体移除 **stage 16 EPU 中国版宏观控制** (Baker-Bloom-Davis 2016 QJE): 删 `16_epu_merge.py` shim + `pipeline/external/` 子包 + `data/external/` 数据 + DAG/OUTPUT_REGISTRY 注册 + runner `8b` merge + `stata_export.py` 的 `epu_*` 标签/core_patterns; panel/.dta/.csv/codebook 去 4 列 `epu_*`, golden snapshot 同步重生。→ **STAGES_MAIN 19→18, 注册阶段 36→35 (18 + 17), thin shim 39→38** (Stata 模板数不变, 无模板引用 epu)。
- 清除已退役死代码 `validation/text2vec.py` (stage 30 早于 2026-05-29 退役, 无 shim、不在 DAG) + 其 2 处测试引用 (`test_stage_smoke` / `test_lineage_input_contract`); 已退役模块清理, 不改计数。⚠ 活跃的 `shibing624/text2vec-base-chinese` 稳健双轨 (`*_t2v` 列, stage 15/25 内联) 完好无损, 勿混淆。
- 接线 **stage 39h `llm_contamination_test`** (DC4 LLM 训练数据污染留出检验, V4 F-Adv.2): 此前 `pipeline/audit/llm_contamination_test.py` 是同族 6 个 audit 中唯一缺 shim+注册者, 但已是 bank_news_clarity / bank_media_disagreement 两篇 frozen spec 承诺的 DC4 必修项。补 `run_stage()` (config 驱动, 缺 stage 49 z_score / 未配官方 cutoff / 样本不足时优雅跳过) + 根 shim `39h_*.py` + `STAGES_VALIDATION` 注册 (opt-in `validation.llm_contamination=false`) + `EXPECTED_NO_OUTPUT_STAGES`。→ **STAGES_VALIDATION 17→18, 注册阶段 35→36 (18 + 18), thin shim 38→39**。配套修 `codebook.py` xlsx 列宽 nullable-dtype `len(float)` 崩溃 + 重生 variable_codebook (去 `*_title` 幻影行) + 守卫 `falsification_template.do.tmpl` 的 `prob_gap_title_full` 陈旧回归 (capture confirm 防 r(111))。
- 整体移除 **stage 17 (D1 BERTopic 叙事主题族) + stage 19 (D4 LLM CEO/Chairman NER 高管聚焦族)** (2026-06-09): 删两模块 (`pipeline/text/article_topic.py` / `pipeline/sentiment/executive_ner.py`) + 两 shim (`17_article_topic.py` / `19_executive_ner.py`) + DAG StageSpec/谓词 (`article_topic_enabled` / `executive_ner_enabled`) + OUTPUT_REGISTRY/_OUTPUT_FILENAME_KEYS 4 产物 + `config/sentiment.yaml` 两 opt-in 块 + runner `8c` merge 两元组 + `stata_export.py` core_patterns (`topic_hhi` / `n_ceo_mentions` / `n_unique_execs` / `exec_hhi`) + `export.py` `topic_entropy` 标签 + `requirements.txt` `bertopic`/`umap-learn`/`hdbscan`; 两族下游零回归消费 (variable-farm), golden `missing_stages` 去 4 项 (expected 27→23)。→ **STAGES_MAIN 18→16, 注册阶段 36→34 (16 + 18), thin shim 39→37** (Stata 模板数 95 不变, 无模板引用)。⚠ 刻意保留 stage 18 staleness / stage 30a SBERT (共享前置) / `news_salience` / `ceo_turnover_2yr` (不同功能, 勿混淆)。
- 整体移除 **stage 49 (`risk_taking_outcomes` 风险承担结果三件套: Z-score / NPL formation / RWA ratio) + stage 39h (`llm_contamination_test` DC4 LLM 训练数据污染留出检验)** (2026-06-12, 无财务数据无法计算): stage 49 的结果变量依赖银行财务面板 (ROA/CAR/NPL/RWA), 该数据始终未获取 → stage 49 长期只优雅跳过写空 panel; 三件套仅作为**变量名**残留在 `bank_news_clarity` / `bank_media_disagreement` 两篇 provisional 论文的 Stata `.do` 模板中 (刻意保留为指标占位, 不删)。stage 39h 唯一 outcome 源即 stage 49 的 `z_score` (audit-local join), 随之一并删除。删: 两 shim (`49_risk_taking_outcomes.py` / `39h_llm_contamination_test.py`) + 两实现 (`pipeline/panel/risk_taking_outcomes.py` / `pipeline/audit/llm_contamination_test.py`) + DAG StageSpec/谓词 (`risk_taking_outcomes_enabled` / `_VALIDATION_PREDS['llm_contamination']`) + `OUTPUT_REGISTRY`/`_OUTPUT_FILENAME_KEYS` (`49_*.parquet`) + `EXPECTED_NO_OUTPUT_STAGES` (`39h`) + `config/panel.yaml::risk_taking_outcomes` + `config/validation.yaml` 的 `llm_contamination` 开关与 `llm_contamination_test` 块 + 3 个唯一为 stage 49 供数的 DC2 抓取脚本 (`scripts/data_acquisition/banking_outcome_dry_run.py` / `outcome_schema_validator.py` / `fallback_decision.py`) + 配套测试 (`test_49_risk_taking_outcomes.py` / `test_omni_fix_risk.py` / `test_llm_contamination_test.py` 整文件, 及 `test_omni_fix_audit_family.py` 的 4 个 39h 类 / `test_metric_audit_p0_fixes.py::TestRiskBankListPath` / `test_panel_orphan_merges.py` 的 stage49 排除断言 / `test_dag_predicates.py` 谓词项, + `test_dag_consistency.py` / `test_39a_inter_track_kappa.py` 计数)。stage 49/39h 均**不并入** 40_panel → panel 列与下游 .dta/codebook 不受影响; golden snapshot 仅需去掉它单独追踪的 `49_risk_taking_outcomes.parquet` 空占位条目 (n_rows=0 / 全 0 哈希) + `counts` (expected 23→22, present 22→21), 已手工剪除 (无需重生全量哈希, 避免在本机裸环境误 bless stage 21 等无关漂移)。⚠ 刻意保留 `config/bank_list.yaml` (`network_spillover` + `strategic_diff` 共享) / `scripts/data_acquisition/fetch_llm_archive.py` (与 outcome 无关) / 两 provisional 论文 Stata 模板与 `paper_spec.yaml` (`z_score` 等仅作指标名)。→ **STAGES_MAIN 16→15, STAGES_VALIDATION 18→17, 注册阶段 34→32 (15 + 17), thin shim 37→35** (Stata 模板数 95 不变)。
- **11 论文 outcome 顶刊重定位** (2026-06-13, spec 层, 与同日 IV 补全协同): 全项目统一**年度 bank-year 面板** → 事件窗 CAR 族 (需日频) 降级各 spec `listed_subsample_extension`, ΔCoVaR 同。主因变量定稿: P1 `funding_cost` (储户纪律) / P2 `ln_fintech_investment` (不变) / P3 `cost_income_ratio_change_3yr` (W&Z 效率试金石, long_run_roa 降 secondary) / P4 `citation_weighted_patent` (Kogan) / P5 `m_and_a_fintech` (不变) / benefit `roa` (**PAP v1.0-final 锁定**) / brokerage `roa` / llm_peer `avg_ft_intensity_full` (**主规格重构**, panel 实存列 $0 可跑) / strategic_diff `tobin_q` (特许权价值) / 第 10/11 篇 `z_score` (测试锁死)。配套: `derivative_replication.py` 4 处 MAIN_DV 同步 + 测试锁拆分 (`ROA_SENTINEL_2`={benefit,brokerage} vs `SPEC_ALIGNED`=B-route 3+llm_peer+strategic) + `pipeline_v34_rerun.yaml` derived_columns 扩年度财务 outcome 族 + 7 个 IV 模板第二阶段 DV 与 4 篇 tables.py Table 1 清单同步。⚠ 新主因变量多为外部财务哨兵列 (capture confirm 优雅跳过), 财务面板接入时须构造列 + 重指剩余 ROA 哨兵 (注意 'ROA' 大写 vs 未来小写 roa 列) + 模板 LHS 接线 + golden 重生; 详见 memory `outcome-redesign-2026-06-13`。
- **11 论文 IV 补全** (2026-06-13, $0 纯既有数据): 新模块 `pipeline/panel/iv_extensions.py` (三引擎: 同组 LOO 均值 / 广义 Bartik 任意 shift / 媒体来源构成 house-style 暴露) + runner 步骤 8z 接线 (`config/panel.yaml::compute_iv_extensions`, 默认 true) → 面板新增 IV 列族: P2 `leave_one_out_peer_attention_iv(+_lag1)`+`bartik_attention_iv(_full/_ctx)`, P3 `leave_one_out_peer_subst_iv`+`bartik_subst_iv_*`, P4 `leave_one_out_peer_locus_iv`, P5 `leave_one_out_peer_collab_iv`+`bartik_collab_iv_*`, benefit_society `leave_one_out_peer_benefit_iv`+`zone_leave1out_benefit_iv`, P10 `outlet_disp_exposure_iv_*`, P11 `outlet_style_clarity_iv_*` (P1/llm_peer/brokerage/strategic_diff 沿用既有 IV)。配套: 7 篇 paper_spec `identification.iv` 落地 + 7 个 2SLS 模板 (主线 `25_tableA6_tone_iv_2sls` 双工具 Hansen J + substance/22 + locus/20 + collab/21 + benefit_society/25 + 两 provisional `12_table3_iv_2sls`; 全部 capture-confirm 守卫, KP rk F + Stock-Yogo + AR CI 脚注) + 各 00_master 挂接。→ **Stata 模板 95→100** (provisional 2 个不计数), replication 包 .do 14→15。引用锚点: Bartik 1991 / GPSS 2020 AER / BHJ 2022 REStud (仅对比) / Manski 1993 / Leary-Roberts 2014 JF / Bramoullé 2009 JoE / Gentzkow-Shapiro 2010 ECMA / Dougal et al. 2012 RFS / Gurun-Butler 2012 JF / KP 2006 JoE / Stock-Yogo 2005 / Andrews-Stock-Sun 2019 ARE。⚠ 新列落盘需重跑 stage 45/46 + golden 重生。
- 整体移除 **stage 38a (`temporal_mask_test` 时间掩码前视偏误检验, B2-1; Tetlock et al. 2008 JF)** (2026-06-12): validation-only 稳健性阶段, 仅写 `temporal_mask_diagnostics*.csv` 诊断表 (`EXPECTED_NO_OUTPUT_STAGES`, 不进 panel/OUTPUT_REGISTRY)。删: shim `38a_temporal_mask_test.py` + 实现 `validation/temporal_mask.py` + DAG `temporal_mask_enabled` 谓词与 StageSpec + `EXPECTED_NO_OUTPUT_STAGES` (`38a`) + `config/panel.yaml::temporal_mask_test` 块 + `config/{validation,config}.yaml` 注释 + `run_pipeline_validation.py` 阶段清单/计数 + `validation/__init__.py` 示例 + 测试 (`test_stage_smoke.py` UNTESTED_STAGES 项 / `test_dag_predicates.py` 谓词参数 / `test_dag_consistency.py` 谓词 identity 集 + 计数 / `test_39a_inter_track_kappa.py` 计数)。validation-only → golden snapshot 不受影响, 无需重生。⚠ 刻意保留 stage 38b decay_sensitivity (不同功能, 勿混淆)。→ **STAGES_VALIDATION 17→16, 注册阶段 32→31 (15 + 16), thin shim 35→34** (Stata 模板数 95 不变)。
- **全部 opt-in / 条件启用阶段 → 无条件 always-on** (2026-06-13, 用户决策"全部启用而非条件启用", 对齐 2026-06-12 的 stage 23/24 先例; **纯 DAG/配置/注释层重构, 行为不变, $0, 不重跑 stage 21, golden 不变** — 所有 flag 现值本就是启用值): `core/dag.py` 移除全部 **17** 个 `enabled_when` 谓词挂载 — 主线 21 (`llm_method_enabled`) / 22 (`words_method_enabled`) / 18 (`article_staleness_enabled`) + 全部 **14** 个验证阶段 (`_VALIDATION_PREDS`) 一律改取 StageSpec 默认 `always_enabled` (现 STAGES_MAIN/STAGES_VALIDATION 中已无任何 `enabled_when`); `METHOD_TO_PREDICATE` 清空为 `{}` (`get_script_for_method` 恒返回 None); `run_pipeline_function.py` 删"未启用 method 陈旧文件清理"循环 + 其 `METHOD_TO_PREDICATE`/`get_script_for_method` import。移除 3 个阶段内 `enabled` 二级门早退: stage 21 (`tone_llm_processing.enabled`, 删整个禁用透传块 ~104 行) / stage 36 (`entity_masking_test.enabled`) / stage 39 (`prompt_sensitivity_test.enabled`)。移除 `runner.py` 全部 **9** 个 `if PANEL_CFG.get('compute_*')` 运行期守卫 (展平为顶层无条件调用; 含 6b/6b-2/6b-3/6c/7e Bartik/7f/7g/8z IV/3c 媒体权威)。**配置 flag 全部保留为已启用值** (同 23/24 先例, 注释统一改标 "[已 always-on] 仅作记录, 改 false 不再停掉"): `enabled_methods` 三项 / `validation.*` 九项 / `article_staleness.enabled` / `tone_llm_processing.enabled` / `compute_*` 八项 / 两 `*_test.enabled`。**唯一删除的 config flag = `preprocessing.yaml::interaction_noise_patterns_enabled`** (本项目无网页语料, 它门控的纯网页互动计数清洗是死代码): 同步删 `_constants.py::INTERACTION_NOISE_ENABLED` + `filter_noise_patterns` 去 `interaction_enabled` 参数 (互动计数族 + pagination 裸分数支改无条件永久排除, 等价旧 `False` 路径 = 报纸语料清洗输出字节不变) + `__all__` + 测试 (`test_omni_fix_preprocess.py` 删 2 个绑定已删符号的用例)。测试同步: `test_dag_consistency.py::test_filter_enabled_respects_predicate` 4 个 filter_enabled 计数全改 **15** (全 always-on 后恒返回全集)。⚠ 谓词函数 (`llm_method_enabled` / `words_method_enabled` / `berts_method_enabled` / `article_staleness_enabled` / `_VALIDATION_PREDS`) + `filter_enabled` / `get_script_for_method` 机制**保留**为纯函数供测试/未来扩展 (勿删, 删则破多个测试)。⚠ stage 18 always-on 后若 faiss-cpu/datasketch 缺失会真崩 (不再优雅跳过), 运行环境须确保两包已装。**计数不变** (STAGES_MAIN 15 / STAGES_VALIDATION 16 / 模板 100); 详见 memory `optin-to-alwayson-2026-06-13`。

**Disk 状态** (2026-06-03 实测): panel/.dta 已重生为 v3.8.0 两轨 schema (full/ctx), 无任何 `*_title` 情感列, golden snapshot 同步重生; ~176 行 (banks × 2 years 2017–2018, T=2)。列数详见 Stata 段, 随每次 panel 重生漂移, 以实读 .dta 为准。完整 LLM 重处理 (stage 21 等付费阶段) 仍受 M0 gate (见 memory `paper_portfolio_decision_gates`)。

**冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1` (不重跑 stage 21, $0 LLM)。

**Stage 21 确定性锚点 = `data/processed/_llm_cache.db`** (2026-06-06 落地, 问题3): golden 的跨-run 可复现性取决于 stage 21 LLM 投票是否确定。唯一不确定源是 **缓存 miss → 重调付费 API → 同篇文章投票可能翻转** (实测曾致某边缘银行整行掉出, panel 176→174 行漂移)。
- **充要条件**: 当前语料 × 全部启用模型 × 双轨 在 `_llm_cache.db` 中 **0 miss**。已验证: 7020/7020 命中 (1170 文 × 3 模型 × 2 轨, `prompt_version='v8-2026-05-17'` / `temperature=0.0`); 离线真跑 stage 21 输出与原盘 **content-sha256 字节级一致**。
- **强制机制 (新)**: 设 `NEWS_PROCESS_LLM_OFFLINE=1` → stage 21 缓存 miss 时 **raise `LLMCacheMissError` 而非调 API** (`pipeline/sentiment/tone_llms.py`, 默认关闭, 不改生产首跑); 离线模式同时跳过 preflight 探针 → 零网络、$0。
- **验证工具**: `python -m news_process.scripts.audit.verify_stage21_cache_coverage` (纯缓存读, 报 hit/miss; misses=0 即可 $0 确定性复现)。
- **铁律**: **勿删 `_llm_cache.db`** (407MB / 133,687 条) — 删则 golden 不再可复现, 须重跑付费 stage 21。prompt 构造单一事实源 = `tone_llms.iter_article_track_prompts` (生产与审计共用 → 缓存键一致)。

**Test baseline** (v3.8.0 实测 2026-05-31): 全量 sweep **2581 passed / 3 skipped / 0 failed** (ruff clean)。精确 collect 数随 production run 漂移, 以 `pytest --collect-only` 为准; 历史逐版计数已失效, 不再维护。

> 历史版本 (v3.5.x–v3.7.5) 的完整 changelog 与 audit 记录见 git history。本文件顶部 "Current version" 段是版本变更的权威源 (CHANGELOG.md 暂未维护)。

**CLI 子命令** (`python -m news_process.papers._common.stata_runner <cmd>`):
- `build-replication`: 一键 instantiate 15 .do 模板 + spec 替换 (2026-06-13 +25_tableA6 语调 IV)
- `list-templates [--verbose]`: 模板清单 + 占位符 inventory
- `doctor [--verbose]`: 5 段诊断 (deps + pipeline + LLM + Stata bin)
- `verify-replication <path>`: 5 段验证 replication 包结构

**v3.1.1 → v3.2.0 panel 迁移**: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`

## Architecture

### Pipeline Structure

The pipeline is a **declarative DAG** defined in `news_process/core/dag.py`. All stages are registered in `STAGES_MAIN` (production) or `STAGES_VALIDATION` (evaluation). The orchestrator (`run_pipeline_function.py`) executes stages as isolated subprocesses.

**Stage flow** (illustrative; authoritative set in `core/dag.py`):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 13_materialize_ctx
→ 14_fintech_intensity → 15_article_policy_alignment
→ 21_tone_llms / 22_tone_words / 23_tone_berts → 24_herd_decay_processor
→ 45_panel_export_main → 46_stata_export → 51_falsification_test
```
`13_materialize_ctx` 物化 `content_ctx` 列, 让下游 14/15 在 stage 21 之前即可消费 ctx, 实现 fintech_intensity / policy_alignment 真双轨 (`*_full` / `*_ctx`)。stage 30 (`robustness_text2vec`) 已于 2026-05-29 退役 — `_t2v` 列改由 stage 15/25 inline 产出, 仅余 `30a_article_sbert`。

Sentiment methods **21 (LLM) / 22 (词典) / 23 (BERT) / 24 (跟风衰减) 自 2026-06-13 起全部为无条件 always-on** (用户决策"全部启用而非条件启用", 在 2026-06-12 的 23/24 先例基础上扩展到 21/22 + 全部 14 个验证阶段): 所有 StageSpec 均取默认 `enabled_when=always_enabled`, 不再随 `config/sentiment.yaml::sentiment_analysis.enabled_methods` / `config/validation.yaml::validation.*` 启停; `METHOD_TO_PREDICATE` 已清空 `{}`, 各方法/验证谓词函数保留供测试。决策动机: 把全部阶段提升为结构性 always-on 后, 无论配置如何, 下游输入 (如 `24_herd_decay.parquet`) 始终生成 → 消除了 stage 45 因缺输入而 `sys.exit(1)` 的脆弱耦合。详见顶部 "全部 opt-in / 条件启用阶段 → 无条件 always-on (2026-06-13)" 段。

### Directory Layout

```
news_process/
├── core/           # Kernel: config, logging, caching, DAG, stage runner
├── pipeline/       # Stage implementations (filtering, sentiment, panel, etc.)
├── papers/         # Multi-paper module dirs (11: 8 fully-coded + 3 provisional)
├── validation/     # Robustness tests (threshold sensitivity, entity masking, etc.)
├── config/         # Split YAML configs + prompt templates (config.yaml is a legacy stub)
├── data/           # Input (raw/) + output (processed/*.parquet)
├── tests/          # full sweep 2581 passed / 3 skipped / 0 failed (collect 数以 --collect-only 为准)
└── NN_*.py         # 34 thin shim scripts under news_process/ (≤30 lines each);
                    # 31 registered in core/dag.py (15 STAGES_MAIN + 16 STAGES_VALIDATION);
                    # 3 unregistered by design: 27c (audit-only sibling),
                    # 52/53 (user-CLI wrappers, schemas.py:159 显式排除).
                    # planned retirement Plan-r3 P3-18 (拆分约束见 pipeline/panel/runner.py:159).
```

**Key invariant**: `news_process/NN_*.py` scripts are thin shims. All logic lives in `news_process.pipeline.*`. Never add business logic to shims.

### Single Sources of Truth

1. **DAG**: `core/dag.py::STAGES_MAIN` / `STAGES_VALIDATION`
2. **Output registry**: `core/schemas.py::OUTPUT_REGISTRY` (stage → parquet files)
3. **Config**: split YAMLs in `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. **Dependencies**: `pyproject.toml::[project].dependencies` (requirements.txt is a fallback)

### Data Flow

- **Input**: `data/raw/*.xlsx` (raw news articles)
- **Intermediate**: `data/processed/*.parquet` (one per stage, e.g., `21_tone_llms.parquet`)
- **Final**: `data/processed/40_panel_yearly.parquet` (bank-year panel for Stata)
- **Logs**: `logs/runs/<run_id>/<stage>.log` (one run_id per pipeline execution)

## Development Commands

### Environment Setup

```bash
# From repository root — create + activate virtual environment
python -m venv venv
source venv/bin/activate            # Linux/macOS
venv\Scripts\Activate.ps1           # Windows PowerShell (本项目主环境)

# Install dependencies (choose one)
pip install -e .                                  # Runtime deps only
pip install -e ".[dev]"                           # + dev tools (pytest, pre-commit, pytest-cov)
pip install -r news_process/requirements.lock && pip install -e . --no-deps  # Exact deps + editable
pip install -r news_process/requirements.txt  && pip install -e . --no-deps  # Fallback for pip-only users

# Configure environment
cp news_process/.env.example news_process/.env    # then set YUNWU_API_KEY (required for LLM stages)

# Enable local pre-commit hooks (one-time per dev machine)
pre-commit install                  # git commit auto-runs check-prompt-headers + ruff check
pre-commit run --all-files          # manual run against full repo
```

### Running the Pipeline

```bash
python run_pipeline_function.py     # Full pipeline (all enabled stages)
python run_pipeline_validation.py   # Validation pipeline (robustness tests)
python 21_tone_llms.py              # Single stage (for debugging)
```

### Testing

> **Run pytest from the repository root** (`f:\WiseSearch\data_antigravity_project\`). Running from the
> `news_process/` subdir may bypass the parent `pyproject.toml::testpaths`; root-level invocation is consistent.

```bash
pytest                              # full sweep (2581 passed / 3 skipped / 0 failed)
pytest -m fast                      # fast tests (~30s, run before every commit)
pytest -m integration               # integration tests (parquet IO, mocked LLM, ~5min)
pytest news_process/tests/test_21_tone_llms.py            # specific file
pytest -k "test_golden"             # tests matching pattern
```

### Linting & Formatting

```bash
ruff check .                        # Lint (configured in pyproject.toml)
ruff check --fix .                  # Auto-fix
```

### Regenerating Golden Baseline

After schema changes that add/remove columns:

```bash
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol

1. **Never amend commits** unless explicitly requested. After pre-commit hook failures, create a NEW commit.
2. **Stage specific files** by name. Avoid `git add .` / `git add -A` (risk of committing `.env` or secrets).
3. **Commit message format**: HEREDOC with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.
4. **Never skip hooks** (`--no-verify`) unless explicitly requested.

### Code Modification Rules

1. **Stage shims are frozen**: The 37 `news_process/NN_*.py` scripts are thin shims (≤30 lines). All logic belongs in `news_process.pipeline.*` or `news_process.validation.*`.
2. **DAG consistency**: Any stage added/removed must update `core/dag.py::STAGES_MAIN`/`STAGES_VALIDATION` and `core/schemas.py::OUTPUT_REGISTRY` (if it produces parquet). Verify with `pytest tests/integration/test_dag_consistency.py`.
3. **Config split is active**: `core/config.py::load_config()` prefers the 7-domain YAML split and falls back to legacy single-file mode only when all split files are absent. Keep split files semantically equivalent to the legacy config contract.
4. **Golden baseline**: After column schema changes, regenerate `tests/fixtures/golden_panel_v0.json` via `scripts/migrate/generate_golden_snapshot.py`.

### Testing Requirements

- **Integration gate**: `tests/integration/test_panel_reproducibility.py` must pass (validates column hashes against golden baseline).
- **DAG consistency**: `tests/integration/test_dag_consistency.py` enforces STAGES_MAIN ⊆ OUTPUT_REGISTRY ∪ EXPECTED_NO_OUTPUT_STAGES, no duplicate stage names, and orchestrator imports matching `core/dag.py` (identity check via `is`).
- **Mock external APIs**: Tests must mock LLM/embedding APIs (see `tests/test_25_audit.py` for fixture examples).

## Common Patterns

### Adding a New Stage

1. Create implementation in `news_process/pipeline/<module>/<stage>.py`
2. Create thin shim `NN_<stage>.py` under `news_process/` (≤30 lines, imports and calls pipeline function)
3. Register in `core/dag.py::STAGES_MAIN` with `StageSpec(...)`
4. If it produces parquet, add to `core/schemas.py::OUTPUT_REGISTRY`
5. Add tests in `tests/test_XX_<stage>.py`
6. Run `pytest tests/integration/test_dag_consistency.py` to verify

### Modifying Config Schema

1. Edit the owning split YAML under `config/`
2. Update `core/config.py::load_config()` only if loader semantics change
3. Regenerate golden baseline if column schema changes
4. Run full test suite to catch downstream breakage

### Debugging Pipeline Failures

1. Check `logs/runs/<run_id>/<stage>.log` for the failed stage
2. Run the stage in isolation: `python news_process/NN_<stage>.py`
3. Use `pytest tests/test_XX_<stage>.py -v` to reproduce in test environment
4. Check `data/processed/` for intermediate outputs

## Environment Variables

Required in `.env`:

- `YUNWU_API_KEY`: Unified API key for LLM sentiment analysis (stages 21, 32a, 33, 34, 36, 39) and embedding (stage 15, 27)
- `EMBEDDING_API_KEY`: Defaults to `${YUNWU_API_KEY}` (can override for separate endpoint)
- `FINBERT2_MODEL_DIR`: Optional local BERT model path (stage 23 gracefully skips if missing)

## Multi-Paper Support

`papers/` contains 11 paper-specific module dirs (**8 fully-coded + 3 provisional**)。自 2026-06-01 全功能打开后, 全部 11 篇均具备 `analysis.py` (Stata runner, main+STAGES, --dry-run 可调度) + `figures.py` + `tables.py` 三件套, 并纳入 `paper_registry.PAPER_IDS_ALL` → `run_paper` 可调度全部 11 篇。provisional 三篇的表/图为 `build_table1`/`plot_*` 占位骨架 (主回归 esttab + manuscript/refs.bib 待 onboarding 填实)。

**P1–P5 Bank-FinTech 主线五篇** (统一 `bank_fintech_*` 命名):
- `bank_fintech_tone/` (P1, 主线): 媒体语调; 三轨化 spec, main = `llm_vote_tone_ctx`
- `bank_fintech_attention/` (P2): firm-level fintech attention intensity (Hassan 2019 QJE)
- `bank_fintech_substance/` (P3): W&Z 实质/象征二元属性
- `bank_fintech_locus/` (P4): Gomber 底层/应用二元属性
- `bank_fintech_collab/` (P5, provisional): Chesbrough 自主研发 vs 外部协同

**衍生 / provisional**: `benefit_society/` · `brokerage_network/` · `llm_peer/` (方法学) · `strategic_diff/` · `bank_media_disagreement/` (provisional) · `bank_news_clarity/` (provisional)。

Common utilities in `papers/_common/` (含 `AI_DISCLOSURE_TEMPLATES.md` 6 系列: Nature/AER/JF/ASQ/RP/CSSCI)。

> 注: 顶部 "Current version" 段中的 `P1/P2/P4/P7` 等指 **Plan E 内部步骤**, 与本段 paper-portfolio 的 `P1..P5` paper ID 是两个独立编号空间。

## Stata Environment

**本机 Stata：StataNow/MP 19.5** (2026-05-16 经 `about` 实测)。
- 路径 `C:\Program Files\StataNow19\StataMP-64.exe`; Build 14 Jan 2026; Windows 64-bit
- 许可 **64-core lab perpetual**; 物理内存 128 GB; 默认 `set maxvar = 5,000` (可上调到 MP 上限 120,000)
- **项目策略 (2026-05-16 起): Stata 19+ only, 无需向下兼容**

### 启动 Stata 的命令约定 (自动化必读 — 防「已完成」弹框)

**Windows 上跑 `.do` 一律用 `/b` 批处理 flag，禁用 `/e` 与裸 GUI 启动。** 弹「已完成」模态框需手动点确定的根因是启动模式不对：

- `StataMP-64.exe /b do x.do` — 真·批处理: 后台、跑完自动退出、不弹框 (本机实测退出码 0)。✅ 唯一推荐。
- `StataMP-64.exe /e do x.do` — 跑完弹模态完成框并阻塞等待点击, 卡死自动化。❌ 禁用。
- 无 flag / 双击 — GUI 交互模式, 同样卡。❌ 禁用。
- Windows 用斜杠 `/b` (不是 Unix 的 `-b`; `-b` 在 Windows 上不可靠)。Unix/Mac 才用 `stata-mp -b do x.do`。

推荐写法 (`StataMP-64.exe` 是 GUI 子系统程序, PowerShell `&` 调用会立即返回 → 必须 `Start-Process -Wait`):

```powershell
$exe = "C:\Program Files\StataNow19\StataMP-64.exe"
Start-Process -FilePath $exe -ArgumentList '/b','do','"<绝对路径\x.do>"' `
  -WorkingDirectory "<.do 所在目录>" -Wait -PassThru |
  ForEach-Object { "Stata 退出码=$($_.ExitCode)" }
# 跑完读同名 .log / .smcl 取结果
```

或用项目封装 `papers/_common/stata_runner.py::run_do(...)` (默认 `batch_mode=True` → 跨平台自动选 `/b`(Win) / `-b`(Unix), 从根上不弹框):

```python
from news_process.papers._common.stata_runner import run_do
cp = run_do(r"build\stata_verify\verify.do"); print(cp.returncode)
```

### 容量与列数 (MP 远未触顶)

MP 硬上限: max obs ≈ 1.1 兆 · maxvar 120,000 · RHS 65,532 · matsize 65,534 · macro 15,480,200 字符
(来源: https://www.stata.com/products/detailed-size-limits/)。当前 panel 最大 `51_panel_with_controls.dta` ≈ 1569 列 (2026-06-03 重生; 列数随每次重生漂移, 以实读为准), 距 MP 上限裕度 > 11.8 万列, 可放心继续加特征。

对本项目的含义:
- **core/aux IC 双切分已整体移除** (2026-06-12 stage 46 改单一全列 `46_panel_yearly_full.dta`; 2026-06-13 清除 `01_data_prep.do.tmpl` IC 回退分支等最后残留)。`stata_export.py::STATA_IC_MAX_VARS = 2048` 仅余一个用途: `assign_core_columns` 守卫"分析核心列"清单别膨胀超 2048 (该清单现在只供 codebook `is_core` 标注), 不再驱动任何文件切分。
- 不要在通用模板里硬编码 "前 2048 列" 之类的 IC 截断逻辑; IC 协作者如需运行, 自行 `keep` 变量子集或升级 SE/MP。
- **行数瓶颈在面板深度 (T=2, ~176 行 = banks × 2 years 2017–2018)**, 不在 Stata 容量; panel 扩展瓶颈在上游数据 / stage 41。
- **64 核并行**: 跑 `bootstrap`/`permute`/`rwolf`/`ritest`/`csdid` wild bootstrap 时按 license 上限自动拉满 (`set processors 64`)。
- **matsize 在 Stata 19 已自动管理** (16+ deprecated); `reghdfe`/`ivreg2` 走 Mata 不受约束。仅原生 `regress` + 极多 RHS 才需显式 `set matsize`。

### Stata 模板约定

- **100 个 `.do.tmpl`** (2026-06-13 IV 补全 +5) = 主线 15 (直接在 `stata_templates/` 下, 含新增 `25_tableA6_tone_iv_2sls`) + 8 个 paper-specific 子目录 82 (attention 7 / collab 9 / locus 9 / substance 10 / benefit_society 23 / brokerage_network 8 / llm_peer 8 / strategic_diff 8) + 历史归档 `v3_5_0/` 2 + `v3_5_1/` 1。另有 provisional 两篇 (`papers/bank_media_disagreement|bank_news_clarity/stata_templates/`) 各 6 个 (各含新增 `12_table3_iv_2sls`), **不计入** 100 (计数口径 = `papers/_common/stata_templates/` rglob, 见 `test_papers_b_route.py::test_total_template_count_77`)。全部统一头部 `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120` (见 `00_master.do.tmpl:13-16`)。新增模板复用此头部。
- `version 19` 锁定最低版本: Stata 18 及更老会报 "version 19 is not a valid version" 拒跑 (这正是 "19+ only" 的执行机制), 可放心使用 `xtdidregress`/`frames`/`pystata`/新版 `meta` 等无需 `version` 守卫。
- `set maxvar 32767` 是防御性保留 (SE 上限); 若未来列数突破 32,767 需上调到 `set maxvar 120000`。
- **pyreadstat 写出的 `.dta` 用 format version 118** (`stata_export.py::_write_dta_pyreadstat` 走 pyreadstat 默认 118; pandas fallback `_write_dta_pandas_fallback` / `tables.py::export_dta` 显式 `version=118`; 实读 4 个 .dta header 均 release=118) — 这是 **.dta 文件格式 spec 编号**, 不是 Stata 应用版本; Stata 19 读取无限制。勿与 `version 19` 混为一谈。

## Known Issues & Workarounds

1. **Windows line endings**: Git may warn about CRLF (expected on Windows). The repo-root `.gitattributes` marks `*.parquet`/`*.xlsx`/`*.db` as binary; source files keep their on-disk EOL.
2. **FinBERT2 model**: Stage 23 requires a private fine-tuned model. If `FINBERT2_MODEL_DIR` is unset or invalid, the stage gracefully skips that model (other BERT models still run).

## Phase History

The project underwent 9 restructuring phases (v1.x → v2.1.0): package skeleton + DAG single-source (0-1) → split monoliths + OUTPUT_REGISTRY + acceptance gate (2) → multi-paper productization + 7-domain config split (3-7) → data layout normalization `data_processed/` → `data/processed/` (8) → cleanup (9). 后续版本演进见 git history; 当前 HEAD baseline 见顶部 "Current version" 段。
