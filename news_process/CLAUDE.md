# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** transforms raw Chinese bank/fintech news into bank-year panel datasets for econometrics: preprocessing → classification → sentiment (LLM/dictionary/BERT) → panel construction.

**Current version**: v3.15.0 (2026-06-28)。逐版 changelog 见 git history; 本段 + 下方"当前状态铁律"是版本变更的权威源 (CHANGELOG.md 未维护)。每次大改的权威执行计划在 `scripts/audit/*_EXECUTION_PLAN_*.md`。

## 当前状态铁律 (load-bearing, 改动前必读)

**计数不变量**: STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16。注册=32 (16+16); 3 个不注册 shim: 80 (audit-only, 原 27c) / 81、82 (user-CLI, 原 52/53; `schemas.py` 显式排除)。阶段增删必同步 `core/dag.py` + `core/schemas.py::OUTPUT_REGISTRY`，并跑 `tests/integration/test_dag_consistency.py`。

**嵌入架构 (co-primary 双轨, 零本地模型)**: canonical 无后缀槽 = `Qwen/Qwen3-Embedding-8B` (硅基流动 `https://api.siliconflow.cn/v1`, **4096 维**); `_lg` 槽 = `text-embedding-3-large` (OpenAI/yunwu, **3072 维**)。两轨**同为主测度、互为稳健性、严格 parity** (列名双射 both-or-neither; 任一 embed None → 同族两列同置 NaN, 无单边孤儿)。引擎 `embed_texts` 纯 API, 维度由 `emb.shape[1]` 驱动 (维度无关), token 切块 cl100k/8191。stage 15 (fintech_intensity) / 25 (`article_sbert`, dual-emit `emb_{full,ctx,ss}`+`_lg`) / 26 (`semantic_staleness_*`+`_lg`) 产 co-primary 双轨嵌入列。**carve-out**: `surface_staleness`/`surface_highstale` 是 MinHash (非嵌入), **无 `_lg` 孪生**, 不动。
- ⚠ **铁律**: 两 co-primary 各自 just-identified 并排, **禁混进同一 over-identified Hansen J**。
- **零 instruct 前缀 (刻意设计, D2 披露 2026-07-14, 绝不加前缀)**: 本项目嵌入用于**对称**相似度任务 (文档↔文档/文档↔锚点句), Qwen3-Embedding 官方 instruct 前缀面向**非对称检索** (query→document), 对称任务加前缀反而引入任务失配; 且无前缀文本已作为缓存键语料冻结播种——事后加前缀 = 全部嵌入缓存作废 + golden 全漂移。
- 🚫 **嵌入 ≠ LLM**: stage 21 情感 LLM 是三家投票 (`gpt-5.4-nano`/gpt54nano · `gemini-3.1-flash-lite`/gemini31 两家走 yunwu · `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com; panel 列含 `*_gemini31_*`), 与嵌入模型**无关** — 换嵌入时全仓零误改。
- **换嵌入模型的入口**: config 键 `config/features.yaml::embedding_api` (model/base_url/api_key/text_pipeline_version) + **散落的硬编码默认回退须同步改** (核心 4 处 `embedding_engine.spec_model` / `article_sbert._SBERT_MODEL_ID` / `strategic_diff._emb_main` / `stata_export._QWEN_ANNOT`; 另有 `policy_alignment` / `benefit_society_audit_combined` / `dimension_analysis` 等 producer 内兜底 — 以 `grep 'Qwen/Qwen3-Embedding-8B'` 全仓非测试文件逐处改), 否则 config 改了回退仍指旧模型 → 静默不一致。`spec_uses_local` 保留为恒 False 纯谓词作 producer fail-fast 守卫 (勿删)。完整清单见 `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN`。
- ⚠ 换嵌入前必先删盘上冻结阈值文件 (如 `data/processed/_benefit_center_sidecar.json`): 跨嵌入空间的阈值守卫会 fail-loud, 否则 stage 40 benefit 崩。
- gate 测试: `test_embedding_coprimary_parity` (列双射+carve-out) + `test_qwen_semantic_validity` (Spearman ρ≥0.80 / ≥500 对)。⚠ 生产首次播种须验硅基流动 >256 的批是否限流 (探针仅验到 n≤256)。

**三轨 `_full` / `_ctx` / `_ss`**: full=标题+正文; ctx=标题+实体窗口; ss=标题+银行∧金科同句±N窗 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认1; 与下方 `cooccurrence_filter.sentence_radius` 是**两个不同键**)。三轨文本 (`content_full`/`content_ctx`/`content_ss` + `*_is_fallback`) 在 stage 14 `ctx_materializer` 物化 (`prepend_title`, 原始`内容`列不动; stage 13 是上游共现硬过滤, 不物化文本列); 情感 21/22/23/24 均跑三轨。判定不对称口径: 银行侧=否定+短名过滤, 金科侧=裸 AC 1506 词。
- **回退语义** (`_ss` 镜像 `_ctx`): 无银行∧金科同句共现 → `content_ss`=全文 body, `ss_is_fallback`=True (共享 `n_articles` 分母); `FINTECH_AC=None` → `*_is_fallback` 全 True 优雅降级。
- 无 `_title` 独立轨 (v3.8.0 删, 标题改 prepend); 保留非情感信号 `target_bank_in_title`(news_bank.py) / `fintech_in_title`+`in_title`(news_fintech.py) / `headline_frac`(controls.py) — 勿连带删。
- ⚠ 三轨禁混同一 over-identified Hansen J。
- **留篇门控 = full-only** (2026-06-29): stage 21 是否判为"一篇银行金科报道"只看 `llm_verified_full == True`。ctx/ss 降为 **conditional-on-full** 测度/稳健性轨 (行宇宙 = full 留篇集子集, per-track 列照算)。**2 处门控副本必须同步翻**: ① `tone_llms.py::df_filtered`; ② `run_pipeline_function.py::_stage21_skip_is_compatible` (不同改 → 永久 reject skip → 每跑付费 stage 21)。skip 上游指纹含三轨文本+回退列 (`content_ctx/content_ss/ctx_is_fallback/ss_is_fallback`, F7 2026-07-16) — 改动轨道物化参数后指纹自动 reject, 无需手动强制重跑。
- P1 `bank_fintech_tone` + provisional `bank_news_clarity` 主轨已切 `_ctx→_full`。`llm_vote_tone_full` 由 P1 与 llm_peer 刻意共享 (`test_paper_namespace_isolation.py::SHARED_CONTROLS` 白名单, 镜像 z_score 跨篇共享先例)。clarity 的 5 个 `.do` 模板 (11–15) headline 已切 `_full` (2026-07-02, `_ctx` 留作首要 robustness; 12 号 IV primary=`outlet_style_clarity_iv_full`)。

**stage 13 共现硬过滤** (`13_cooccurrence_filter.py`, 原 stage 12b): 硬过滤丢行, 只保留"目标银行与 ≥1 金科词邻近共现"的文章。生产口径 = `sentence_radius=1` (±1 句窗口) + `match_in_title=true` (标题+正文), 见 `config/filtering.yaml::cooccurrence_filter`; 输出路径键仍是 `config/paths.yaml::output_12b_cooccurrence` (重编号未改 config 键)。判据原语 `core/text/entity_context.py::has_bank_fintech_cooccurrence_within_radius` (与 `_ss` 严格同句的 `extract_bank_fintech_cooccurrence` 不同口径, **禁互相复用**)。**安全**: `FINTECH_AC=None` → 保留全部行 + loud WARNING (绝不静默清空); keep 率 < `min_keep_frac` 或 0 行 → `SystemExit(1)`。

**always-on**: 情感 21/22/23/24 + 全部 14 验证阶段无条件启用 (StageSpec 默认 `always_enabled`, 无 `enabled_when`; `METHOD_TO_PREDICATE={}`)。谓词函数 / `filter_enabled` / `get_script_for_method` 保留为纯函数供测试 (勿删)。⚠ stage 26 staleness always-on 后须装 `faiss-cpu`/`datasketch` (缺则真崩, 不再优雅跳过)。

**IV 扩展** (`pipeline/panel/iv_extensions.py`, runner 步骤 8z, `config/panel.yaml::compute_iv_extensions` 默认 true): 三引擎 (同组 LOO 均值 / 广义 Bartik / 媒体来源 house-style 暴露) → 面板 IV 列族 (`leave_one_out_peer_*_iv` / `bartik_*_iv` / `outlet_*_iv`) + 7 篇 paper_spec `identification.iv` + 7 个 2SLS 模板。

**词典消融梯度** (v3.11.1): tone_words 三语言学规则 (否定翻转 / 程度副词 / 转折) 全 powerset 物化为消融变体 `{dict}_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}` (7 个非-full 变体) × 6 词典 × 3 轨 + 同名 panel 聚合 + geography `dict_avg_{sfx}_tone{track}`。各变体自归一化、非可加分解 (audit MATH-1: 高度共线 corr≈0.99, 报 corr 而非并入同式)。SSOT = `_RULE_ABLATION_VARIANTS`。

**LLM 三家 / BERT 三模型互为稳健性** (2026-07-02): 情感三法各自的 per-model 子测度并排为「互为稳健性、不分主次」轨 (镜像政治词权重梯度)。**LLM**: `llm_vote_tone` (三家多数投票共识) = canonical headline (P1 `treatment.primary`); 三 per-model `{gpt54nano,gemini31,deepseekv4}_tone{track}` = co-equal 跨厂商稳健 (另有均值-ensemble `llm_models_avg_tone`, `geography.py`)。**BERT**: 三 per-model `{finbert_cn,fin_sent_zh,finbert2}` co-equal, 无 ensemble headline; Phase 2 加 signed `{short}_net_tone{track}` = mean(pos)−mean(neg) ∈ [−1,1] (`encode.py` post-agg, +9 列, golden 重生 DEFERRED)。**per-model 独立降级** (finbert2 缺席仅掉自身族, **非** co-primary 嵌入的 both-or-neither)。SSOT = `encode.LLM_MODELS`/`BERT_MODELS` (codebook 模块级 import 复用防漂移); `_infer_source_stage` 用**宽前缀** (`deepseekv4_*`/`fin_sent_zh_*` 无 llm/bert 子串)。⚠ **铁律**: 各家/各模型各自 just-identified 并排, **禁混同一 over-identified Hansen J** (同三轨 / co-primary 嵌入 / 政治词权重)。真 FWER = 根级 rwolf 模板 `27_tableA12_cross_model_fwer` (paper_spec 的 `cross_model`/`cross_bert_model` 是**声明式文档**, 运行时无消费者); Table A5 跨模型 β 须 z-score 标准化 (2/3 分类 net_tone 原始方差不同)。模型间一致性 = `tone_validation.py` 复用 `llms_evaluation.compute_krippendorffs_alpha` (名义+缺标感知, 容 2-vs-3 分类) + Cohen κ (⚠ 须先重映射非负码, `-1` 缺标哨兵与负面标签冲突)。gate: `tests/test_{llm,bert}_model_robustness.py`。执行计划 = `scripts/audit/LLM_BERT_MUTUAL_ROBUSTNESS_EXECUTION_PLAN_2026-07-02.md`。

**稳健性缺口补齐** (2026-07-03, 计划=`scripts/audit/ROBUSTNESS_GAP_BACKFILL_EXECUTION_PLAN_2026-07-02.md`): 五条新梯子/轨, 全部「互为稳健性、不分主次」、各自 just-identified 并排、**禁混同一 over-identified Hansen J**、梯子间正交不交叉。① **LLM 分类维度 per-model** (P3/P4/P5 treatment 跨厂商稳健): SSOT=`encode.LLM_CLASS_SPEC` 三元映射 {文章级基名 subst/locus/collab → (面板 metric sub_frac/tech_frac/collab_frac, 分子目标类, 解析键)} — **两命名域无字符串变换可达, 该映射是唯一互锁点**; 文章级 `{short}_{dim}{track}` = 不门控审计存档 (三份逐轨发列块成对改), verified 门控在 encode 层 (`{short}_{metric}_src` 指示列, 分母=该模型自身 verified 篇数); skip 守卫 `_STAGE21_REQUIRED_OUTPUT_COLUMNS` 已收紧 (未回填机器 reject → $0 离线重放属预期); 共识≠存档裸多数票 (verified 门控/final_v 清票/locus 关键词回退); 真 FWER=27_tableA12 Panel C (`CLS:` 族, RES 矩阵已扩 `J(9,1)`); gate=`test_llm_classification_robustness`+`test_cross_model_kappa`。② **benefit 4 维度六轨** ({full,ctx,ss}×{MAIN,_lg}): 列名 SSOT=`dimension_analysis._dim_col` (**lg 中置**), per-spec 方向向量 (_lg 缓存键=('text-embedding-3-large','v1-2026-06-27-emb3large'), 禁 `_resolve_prompt_version`), both-or-neither 守卫; 孤儿 parquet 24 列已本机回填; merge `'both'`={full,ctx} 向后兼容+`'all'`/`include_lg`; gate=`test_benefit_dimension_tracks`。③ **boilerplate 三轨** (full=headline, ctx/ss=稳健轨; 非嵌入 carve-out 无 `_lg`; codebook 条目已迁 `_DUAL_TEXT_SPECS`)。④ **罕见词频次 cutoff 梯子** `RARE_WORD_FREQ_CUTOFFS=(2,3,5)` (canonical=3≡无后缀 `rare_word_ratio`; **分位梯子 {10,20,30} 在 jieba 冻结词典上数学退化, 禁用**; 列 `rare_word_ratio_c{2,5}`/`avg_rare_word_c{2,5}`; gate=`test_rare_word_cutoff_ladder` 锚死 cutoff==3.0)。⑤ **FLS 单/双门二臂** (`frac_fls`=双门 canonical / `frac_fls_fonly`=单门超集稳健臂; 聚合在 **encode_collab** 同名 mean 非 encode avg_ 范式)。根级模板 +1 = `28_tableA13_policy_family_robustness` (policy 12 臂; ⚠ policy 面板列 full 轨**无 _full 后缀**, 中缀序 lg 先 allv 后, 错拼被 capture confirm 静默吞 — 文本 gate 兜底)。刻意不做 (§7 归档): herd 半衰期/salience 阈值/num_intensity cn2arab/surface_staleness `_lg`/梯子交叉/per-model 门控孪生列。

**政治词权重敏感性** (du_2022 独有): `du_2022` 的 `political_positive`(1,434 词) 生产口径以 **0.5** 权重计入正侧。**两句话依据** (comments/logs/codebook/stata/tone_dicts.json 同源, SSOT=`tone_words.POLITICAL_WEIGHT_RATIONALE`): ① 依据 Du et al. (2022, *Review of Finance*, doi:10.1093/rof/rfab036) 政治正面词信号弱于普通正面词的发现, 对该类词赋予降低的权重; ② 权重取 0.5 为研究者选择, 并做敏感性检验: 令政治词权重 ∈ **{0.0, 0.5, 1.0}** 三者**互为稳健性、不分主次**, 证明主结论不被这一取值驱动。落地: `article: du_2022_score_polw{00,05,10}` / `panel: du_2022_polw{00,05,10}_tone{track}` (polw05 ≡ canonical `du_2022_score`/`du_2022_tone`, 无后缀为历史命名产物非"主"; 镜像 co-primary 嵌入双轨口径)。SSOT = `tone_words.POLITICAL_WEIGHT_VARIANTS` (byte-sync `encode.POLITICAL_WEIGHT_SUFFIXES`)。⚠ 与规则消融梯度**正交、不交叉** (三权重均在全语言学规则下算, 避免 3×8 列爆炸); ⚠ **铁律**: 三权重各自 just-identified 并排, **禁混进同一 over-identified Hansen J** (同三轨 / co-primary 嵌入铁律)。gate 测试 `tests/test_political_weight_ladder.py`。

**网络三轨 + 构造判据敏感性** (2026-07-03): ①-A `industry_neg_shock{,_ctx,_ss}` + lag1 三轨 (分子分母**严格逐轨**: `neg_count_{trk}/n_articles_llm_valid_{trk}`, ctx/ss 缺列跳轨不借 full 分母; dev T=2 上 ctx/ss 均零方差≡0 属预期退化)。①-B W-轨: `bank_cogn_mean_{ctx,ss}` (TF-IDF $0) + `bank_emb_sim_mean_lag1_{ctx,ss}`(+_lg) + **diag 对角轨** `emb_peer_tone_diag_lag1_{ctx,ss}`(+_lg) — legacy `emb_peer_tone_lag1_{ctx,ss}` 语义 = **W_full×tone_trk** (W 来源恒 full, 标签写明), diag = W 与 tone 同轨; ctx/ss 超级文档 = `content_{ctx,ss}` 原样拼接 (**剔 *_is_fallback 行 + 禁 title 通道** — prepend_title 已内嵌标题, 再拼即双标题污染付费缓存); **per-W-轨独立降级** (D8, 单元内 both-or-neither, 单元间不连坐; 非 full 族全家桶)。② 33 结构指标 × 判据 `{同篇(无后缀)/±1句窗 _win1/严格同句 _sent}` (+66 列) — **判据后缀 ≠ 三轨文本后缀**, 判据主体是银行∧银行 (原语 `entity_context.map_bank_sentence_positions`, 逐句 `has_unexcluded_occurrence`, 扫描文本=prepend_title 标题第 0 句, 镜像 stage 13 match_in_title); config 记录键 `panel.yaml::network_criteria` (与 stage 13 `cooccurrence_filter.sentence_radius` 是不同键)。SSOT = `network_spillover.NETWORK_METRIC_BASES` (33 基名, stata_export 标签机械块 import 复用)。⚠ codebook 三推断函数入口**剥判据后缀**再匹配 (`_CRITERIA_SFX_RE`, 否则 'sent' 子串误归情感 + net_yr endswith 破)。⚠ **铁律**: 三轨/W-轨/三判据各自 just-identified 并排, **禁混同一 over-identified Hansen J**; 判据/W轨/①-A 三轨属**规格稳健性并排** (镜像政治词权重/词典消融先例, 不设 FWER 模板 — 跨模型 rwolf 先例仅覆盖同构念替代 headline 测量, 本族不适用)。gate: `tests/test_network_tritrack_expansion.py`。**播种状态**: ctx/ss/diag 嵌入 (canonical+_lg) T=2 已本机在线播种、`NEWS_PROCESS_LLM_OFFLINE=1` 离线 0-miss 可 $0 复现; 生产 T=19 播种 DEFERRED (费用按生产语料实测重估)。执行计划 = `scripts/audit/NETWORK_TRITRACK_AND_CRITERIA_EXECUTION_PLAN_2026-07-02.md`。

**BERT 分布形状五族** (2026-07-04): stage 23 概率列 $0 纯后处理 → **+69 面板列** (盘上 3395): ①`{b}_tone_entropy` 归一化熵 (⚠ finbert2=Bernoulli 熵与三分类"模糊度"构念不可比且逐篇≡|net_tone| 单调**递减**变换 ρ≡−1, 禁跨模型比水平) ②`{b}_xneg_frac[_t80/_t95]` 极端负面占比 (τ∈{.80,.90,.95}, canonical=.90≡无后缀; ⚠ 阈值语义 model-specific 禁跨模型比占比水平, 只比标准化 β) ③`{b}_net_tone_skew` (raw skew **非 NCSKEW**; `SKEW_MIN_N=10` 掩码 n 口径=`_nt_n_` count 临时列 [agg 后即 drop], **禁用 pos_count**=argmax 判正数内生选择) ④跨模型双轨 `bert_xmodel_lblhet` (canonical, sign 两两不一致对占比, 0 vs ±1 记不一致) + `bert_xmodel_disp` (z-SD 稳健轨, 样本依赖) ⑤年内 `{b}_nt_iyvol` (噪声校正: 池化 σ̂² 双 ddof=1, 门槛 T≥3 且 ≥1 月 n_t≥2) + `{b}_nt_iytrend` (≥6 有效月, 闭式斜率**禁 lstsq/polyfit**)。SSOT = `pipeline/panel/bert_distribution.py` **叶模块** (BERT_MODELS/THREE_CLASS_MODELS 参数注入, encode/codebook/stata_export 模块级 import 安全, **禁反向 import encode** 成环)。文章级中间列 51 个 (非 `_is_` 前缀) 由 runner 步骤 9 前单点 drop, 绝不落文章级 parquet。⚠ 铁律: 阈值梯子/per-model/三轨/双轨各自 just-identified 并排, **禁混同一 over-identified Hansen J**; 无 `_lg` (非嵌入 carve-out); per-model 独立降级。dev T=2 上 skew 仅 n≥10 格出值、iyvol/iytrend 全 NaN 属预期退化 (生产 T=19 正常)。gate = `tests/test_bert_distribution_metrics.py` (15 项)。执行计划 (五轮评审史) = `scripts/audit/BERT_DISTRIBUTION_METRICS_EXECUTION_PLAN_2026-07-03.md`。

**boilerplate OOM 硬化** (2026-07-06, 计划 = `scripts/audit/BOILERPLATE_CHUNKED_TWOPASS_OOM_HARDENING_EXECUTION_PLAN_2026-07-06.md`): stage 22 套话比率 (`boilerplate.py`) 单遍 `fit_transform` → **分块 exact two-pass** (字节等价单遍, golden 零漂移; §9 三不变量 + fuzz 1800 + 真实 400 篇 + golden baseline-stash A/B 既存陈旧红灯 17↔17 零新增 四重证)。`memory_tier='in_memory'` (tier1, 默认) 消除 CSR 驱动; 旧单遍冻结为 `'single_pass'` 字节等价参照臂 (gate 存在即禁删); `'disk'/'auto'` (tier2) → `raise SystemExit` (**非** NotImplementedError, 后者⊂Exception 会被 `tone_words` `except Exception` 吞成静默丢列)。SSOT = `boilerplate._make_vectorizer` 工厂 (类型感知 assert 锁 min_df=int1/max_df=float1.0/max_features=None 无剪枝命门) + `_coerce_int` config 畸值兜底。⚠ **生产 T=19 铁律**: 只消 CSR (较小非-binding 项), 真正 binding 的 `global_df` 词表仍驻 RAM → **tier1 ≠ "T=19 OOM 已解决"**, vocab-binding 须补 **tier2 (DEFERRED)**; `df_dict_budget_hard=40M` 是**未校准占位**, 生产语料 global_df 极可能超之 → Pass1 循环内 `SystemExit` **连坐 nuke 整批 stage-22** (boilerplate 在 save 前, 词典 tone 先算完) → **T=19 首播前必先跑计划 §3-P0 实测 per-entry 字节按 128GB 反推校准硬闸** (受 M0 审批门约束)。gate = `tests/test_boilerplate_chunked.py` (17 项) + `test_boilerplate.py` (9 项) = 26 用例。

**已移除阶段** (勿引用, 详见 git history): EPU 宏观控制(原16) / BERTopic 主题(17) / 高管 NER(19) / risk_taking_outcomes(49) / llm_contamination_test(39h) / temporal_mask(38a) / track_discriminant(39g) / 独立 text2vec(30)+bge 本地嵌入轨。⚠ 勿误删仍活跃的 staleness/`article_sbert`/`news_salience`/`ceo_turnover_2yr`; provisional `.do` 模板里的 `z_score`/NPL/RWA 是占位变量名 (保留); `config/bank_list.yaml`、`fetch_llm_archive.py` 刻意保留。

## 确定性 / golden (铁律)

- **勿删 `data/processed/_llm_cache.db`** (~2.1GB, 随缓存播种增长) — golden 跨-run 可复现锚。三轨 (full/ctx/ss) 在缓存 **0 miss** 即可 `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 字节级复现 (miss → raise `LLMCacheMissError`, 不调 API, 跳过 preflight 探针)。缓存命中键 = `prompt_version='v8-2026-05-17'` / `temperature=0.0`; prompt 构造 SSOT = `tone_llms.iter_article_track_prompts` (生产/审计共用 → 缓存键一致)。验证: `python -m news_process.scripts.audit.verify_stage21_cache_coverage`。⚠ 嵌入族**亦受** `NEWS_PROCESS_LLM_OFFLINE` 守卫 (`embedding_engine.py` 内 miss→raise `RuntimeError`, 与 stage 21 `LLMCacheMissError` 对称但异常类型不同、live 逐次读非 import 快照); 仅在线 (env 未设或为非真值) miss 才付费。
- **冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1` (不重跑 stage 21, $0 LLM)。
- **golden 重生 DEFERRED 到生产语料机** (本机 data/raw 空、T=2、无生产语料、付费不可逆); 完整付费 LLM 重处理 (stage 21 全量重跑) 须先过 **M0 审批门**。重生须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1 (`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/`NUMEXPR`/`OMP_NUM_THREADS`=1)。BLAS-FP 非确定网络列 (2026-07-03 判据分轨后 3→**9**): `bank_clustering` / `bank_cfbetween_cent` / `bank_harmonic_cent` 各自的 无后缀/_win1/_sent 三判据变体 → 验零漂移须按全名 drop 排除这 9 列 (⚠ diff_golden.py 的 _KNOWN_BLAS_RE 子串匹配自动覆盖新后缀; 其宽清单含 eigen 与本处 3 基名清单不一致, 待生产机重生时实证统一)。换模/改测度类改动 golden **零字节安全**须受控全量重生; manuscript 须披露厂商维度 Google→阿里 Qwen 与 full-only 数值副作用 (`n_articles`/`fintech_share`/`attention_pct` 收缩, 均非 bug)。
- **本机验证套路**: 改测度类改动本机不动 parquet → 用 baseline-stash A/B 差分证"0 新增失败"(committed golden 本就陈旧, T=2 dev 不新增红灯)。
- **Disk 状态**: ~220 行 (110 banks × 2 years 2017–2018, T=2 dev); 最宽 dta = **3453** 列 (51_panel_with_controls.dta, 2026-07-15 实读; 40/46=3442; 随重生漂移, 以实读为准 — 勿再用"旧基数+增量"心算)。真实全量 (目标语料) = **18,198,978 条 (约 1,819 万条) / 2007–2025 / T=19** (2026-07-16 用户裁定: 目标语料 = 普查全量, 旧"约 1700 万 / 2007–2024 / T=18"口径作废)。
- **原始语料普查** (stage 00 `raw_census`, 2026-06-29, 过滤·去重**之前**全量): 183 去重源文件 / **18,198,978 条**媒体报道 / 2007-01-01 ~ 2025-12-31 / **3,740 家媒体来源** (outlet count, 全类型未过滤); 媒体类型=报纸的报道**占全部行 92.93%** (16,912,361 行) 保留、其余类型 (通讯社/杂志/政府/网页等) 按行剔除; 精确唯一 18,177,370 (重复率 0.12%)。⚠ 该递归全量口径 (供论文 data appendix) **即目标语料口径** (2026-07-16 用户裁定二者合一: 目标语料 = 普查全量 18,198,978 条 / 2007–2025 / T=19, 旧"普查 vs 目标语料"二分作废), 但仍 **≠** stage 00 非递归 `data_excel/*.xlsx` 实处理量 (这一区分保留)。全表见 `build/manual_facts/key_stats.md`。

## CLI 子命令 (`python -m news_process.papers._common.stata_runner <cmd>`)

- `build-replication`: 一键 instantiate 21 个根级 `.do` 模板 + spec 替换 (构建复现包的规范入口; 2026-07-02 +27_tableA12_cross_model_fwer; 2026-07-03 +28_tableA13_policy_family_robustness)。
- `list-templates [--verbose]`: 模板清单 + 占位符 inventory。
- `doctor [--verbose]`: 7 段诊断 (Python 依赖 / pipeline 数据 / LLM cache / LLM API / Stata bin / Stata ado 包 / Stata notes 指纹)。
- `verify-replication <path>`: 5 段验证 replication 包结构。
- panel 迁移: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`。

## Architecture

### Pipeline Structure

声明式 DAG 定义在 `core/dag.py`，阶段注册于 `STAGES_MAIN` (生产) / `STAGES_VALIDATION` (评估)。orchestrator `run_pipeline_function.py` 把每阶段当独立子进程跑。

**Stage flow** (illustrative; authoritative set in `core/dag.py`):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 13_cooccurrence_filter
→ 14_materialize_ctx → 15_fintech_intensity → 16_article_policy_alignment
→ 21_tone_llms / 22_tone_words / 23_tone_berts → 24_herd_decay_processor
→ 40_panel_export_main → 46_stata_export → 51_falsification_test
```
`14_materialize_ctx` 物化 `content_ctx`/`content_ss`, 让下游 15/16 在 stage 21 前即可消费 → fintech_intensity / policy_alignment 真三轨。`25_article_sbert` 仍活跃 (产 co-primary `_lg` 双轨嵌入喂 stage 26 `article_staleness`; `_t2v`/`_bge` 本地轨已于 v3.14.0 整体移除)。

### Directory Layout

```
news_process/
├── core/           # Kernel: config, logging, caching, DAG, stage runner
├── pipeline/       # Stage implementations (filtering, sentiment, panel, etc.)
├── papers/         # 11 paper module dirs (8 fully-coded + 3 provisional)
├── validation/     # Robustness tests (threshold sensitivity, entity masking, etc.)
├── config/         # Split YAML configs + prompt templates (config.yaml is a legacy stub)
├── data/           # Input (raw/) + output (processed/*.parquet)
├── tests/          # full sweep ≈2581 passed / 3 skipped (collect 数以 --collect-only 为准)
└── NN_*.py         # 35 thin shims (≤30 lines); 32 registered (16 MAIN + 16 VALIDATION);
                    # 3 unregistered by design: 80 / 81 / 82。shim 号已重编号反映执行先后。
```

**Key invariant**: `news_process/NN_*.py` 是 thin shim, 所有逻辑在 `news_process.pipeline.*` / `news_process.validation.*`。**绝不**往 shim 加业务逻辑。

### Single Sources of Truth

1. **DAG**: `core/dag.py::STAGES_MAIN` / `STAGES_VALIDATION`
2. **Output registry**: `core/schemas.py::OUTPUT_REGISTRY` (stage → parquet files)
3. **Config**: split YAMLs in `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. **Dependencies**: `pyproject.toml::[project].dependencies` (requirements.txt is a fallback)

### Data Flow

- **Input**: `data/raw/*.xlsx` (raw news articles)
- **Intermediate**: `data/processed/*.parquet` (one per stage, e.g. `21_tone_llms.parquet`)
- **Final**: `data/processed/40_panel_yearly.parquet` (bank-year panel for Stata)
- **Logs**: `logs/<stage>.log` (扁平布局, 每阶段一文件; 每次运行覆盖, 只留最新一次)

## Development Commands

```bash
# 环境 (本项目主环境 = Windows PowerShell venv; 解释器走 conda base python 3.13)
python -m venv venv && venv\Scripts\Activate.ps1
pip install -e ".[dev]"                                          # runtime + pytest/pre-commit/ruff
# 或精确锁定: pip install -r news_process/requirements.lock && pip install -e . --no-deps
cp news_process/.env.example news_process/.env                   # 然后填 YUNWU_API_KEY / DEEPSEEK_API_KEY / SILICONFLOW_API_KEY
pre-commit install                                               # 一次性: 提交自动跑 check-prompt-headers + ruff

# 跑 pipeline (从 repo 根 f:\WiseSearch\data_antigravity_project\)
python run_pipeline_function.py     # 全主线
python run_pipeline_validation.py   # 验证 pipeline
python 21_tone_llms.py              # 单阶段调试

# 测试 (必须从 repo 根跑, 否则绕过 pyproject testpaths)
pytest                              # 全量 sweep
pytest -m fast                      # 快测 (~30s, 每次 commit 前)
pytest -m integration               # 集成 (parquet IO + mocked LLM, ~5min)
pytest -k "test_golden"             # 按 pattern

# Lint
ruff check . ; ruff check --fix .

# Golden 重生 (列 schema 变更后)
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol
1. **绝不 amend** (除非显式要求); pre-commit hook 失败后创建**新** commit。
2. **按文件名 stage** (`git add <file>`); 避免 `git add .`/`-A` (防误提 `.env`/secrets)。共享树并发会话尤须 by-name (排除 `*constants.json`/`eval_reports` 等并发产物)。
3. **Commit message**: HEREDOC + `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer。
4. **绝不 `--no-verify`** (除非显式要求)。

### Code Modification Rules
1. **Shim 冻结**: 35 个 `NN_*.py` 是 thin shim (≤30 行), 逻辑归 `pipeline.*`/`validation.*`。
2. **DAG consistency**: 阶段增删同步 `STAGES_MAIN`/`STAGES_VALIDATION` + `OUTPUT_REGISTRY` (产 parquet 时), 跑 `test_dag_consistency.py`。
3. **Config split active**: `load_config()` 优先 7-domain 拆分 YAML, 全缺时才回退 legacy 单文件; 拆分文件须语义等价 legacy 契约。
4. **Golden**: 列 schema 变更后经 `generate_golden_snapshot.py` 重生 `tests/fixtures/golden_panel_v0.json`。

### Testing Requirements
- **Integration gate**: `tests/integration/test_panel_reproducibility.py` 必过 (列哈希对 golden)。
- **DAG consistency**: `test_dag_consistency.py` 强制 STAGES_MAIN ⊆ OUTPUT_REGISTRY ∪ EXPECTED_NO_OUTPUT_STAGES, 无重名, orchestrator import 与 `core/dag.py` identity (`is`) 一致。
- **Mock 外部 API**: 测试必 mock LLM/embedding API (范例 `tests/test_25_audit.py`)。

## Common Patterns

- **加阶段**: 实现 `pipeline/<module>/<stage>.py` → thin shim `NN_<stage>.py` (≤30 行) → 注册 `STAGES_MAIN` (验证阶段注册 `STAGES_VALIDATION`) → 产 parquet 则加 `OUTPUT_REGISTRY`, 不产则加 `EXPECTED_NO_OUTPUT_STAGES` (否则 `test_dag_consistency` 失败) → 测试 → 跑 `test_dag_consistency.py`。
- **改 config schema**: 改对应拆分 YAML → 仅 loader 语义变时改 `load_config()` → 列 schema 变则重生 golden → 全量测试。
- **调试失败阶段**: 看 `logs/<stage>.log` → 单跑 `python news_process/NN_<stage>.py` → `pytest tests/test_XX_<stage>.py -v` → 查 `data/processed/`。

## Environment Variables (`.env`)

- `YUNWU_API_KEY`: stage 21 情感 LLM (gpt54nano/gemini31 走 yunwu) + 若干 LLM 验证阶段 (如 66/70) + `_lg`/yunwu 嵌入。
- `DEEPSEEK_API_KEY`: stage 21 第三家 LLM `deepseek-v4-flash` (直连 `api.deepseek.com`, 与 yunwu 不同源)。离线缓存命中时不需; 生产首跑/播种须填。
- `SILICONFLOW_API_KEY`: canonical Qwen 嵌入轨 (硅基流动)。
- `EMBEDDING_API_KEY`: 默认 `${YUNWU_API_KEY}` (可覆盖独立端点)。
- `FINBERT2_MODEL_DIR`: 可选本地 BERT (stage 23 缺失时优雅跳过)。
- ⚠ `LLMs_for_FinTech_dic/` 独立管道使用**独立开关 `LLMS_DIC_OFFLINE`**; `NEWS_PROCESS_LLM_OFFLINE` 对该目录无效 ("设主项目离线变量即全仓 $0" 不成立)。
- ⚠ 裸环境嵌入 SSL 报错 → 设 `SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")`; 重跑 stage 23 BERT 设 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`。

## Multi-Paper Support

`papers/` 含 11 个 paper 模块 (8 fully-coded + 3 provisional); 全部具备 `analysis.py`/`figures.py`/`tables.py` 三件套, 纳入 `paper_registry.PAPER_IDS_ALL`。

- **P1–P5 主线** (`bank_fintech_*`): tone (P1) / attention (P2) / substance (P3, W&Z) / locus (P4, Gomber) / collab (P5, provisional, Chesbrough)。
- **衍生/provisional**: `benefit_society` · `brokerage_network` · `llm_peer` (方法学) · `strategic_diff` · `bank_media_disagreement` (prov) · `bank_news_clarity` (prov)。
- **处理变量 (treatment) vs outcome (DV) 是两套**: 各 paper 主轨 treatment 多为 `*_full` 情感/属性变量 (P1=`llm_vote_tone_full`); outcome/DV 另定 (P1 `funding_cost` / P2 `ln_fintech_investment` / P3 `cost_income_ratio_change_3yr` / P4 `citation_weighted_patent` / P5 `m_and_a_fintech` / benefit&brokerage `roa` / llm_peer `avg_ft_intensity_full` / strategic_diff `tobin_q` / prov `z_score`)。多为外部财务哨兵列, 财务面板接入时构造; 详见 memory `outcome-redesign-2026-06-13`。
- 公用工具 `papers/_common/` (含 `AI_DISCLOSURE_TEMPLATES.md` 6 系列: Nature/AER/JF/ASQ/RP/CSSCI)。
> 注: 本段 paper ID `P1..P5` 是 paper-portfolio 的本地编号, 与其它文档/计划里的 `P1/P2/..` 步骤编号是两个独立空间。

## Stata Environment

**本机 StataNow/MP 19.5** (`C:\Program Files\StataNow19\StataMP-64.exe`, 64-core perpetual, 128GB)。**项目策略: Stata 19+ only, 无需向下兼容**。

### 启动约定 (自动化必读 — 防「已完成」弹框)
- **一律 `/b` 批处理** (Windows 用斜杠 `/b` 不是 `-b`); **禁** `/e` 与裸 GUI/双击 (弹模态完成框卡死自动化)。
- ⚠ `/b` 的"不弹框"前提是 do-file 跑到干净收尾。**两层防御 (二选一, 都做最稳)**: ① 走 `/b` 或封装 `papers/_common/stata_runner.py::run_do` / `scripts/run_stata.ps1` (硬编码 `/b`); ② 任何 ad-hoc/probe `.do` 末尾加 `exit, clear` (直接终结进程绕过完成框)。⚠ 终端 `exit` **只**加在 standalone/`00_master.do` 末尾, **绝不**加进被 master 调用的子 `.do` (会让 master 提前退出)。
- `StataMP-64.exe` 是 GUI 子系统 → PowerShell `&` 会立即返回, 必须 `Start-Process -Wait`:
```powershell
$exe = "C:\Program Files\StataNow19\StataMP-64.exe"
Start-Process -FilePath $exe -ArgumentList '/b','do','"<绝对路径\x.do>"' `
  -WorkingDirectory "<.do 所在目录>" -Wait -PassThru | ForEach-Object { "退出码=$($_.ExitCode)" }
# 退出码不完全可信 → 跑完扫同名 .log 的 r(###) 取真实结果
```

### 容量 / 模板
- MP 硬上限远未触顶 (maxvar 120,000; 当前最宽 panel ≈2782 列)。**core/aux IC 双切分已整体退役** (2026-06-21: 单一全列 `.dta`, codebook 无 `is_core`) — **勿**在模板硬编码"前 N 列"截断。行数瓶颈在面板深度 (T=2), 不在 Stata 容量。
- 跑稳健性 battery (`bootstrap`/`rwolf`/`ritest`/`csdid` wild bootstrap) 本机按 license 自动拉满 (`set processors 64`); `matsize` 在 Stata 19 已自动管理 (`reghdfe`/`ivreg2` 走 Mata 不受约束)。
- **147 个 `.do.tmpl`** (计数口径 = `papers/_common/stata_templates/` rglob, 见 `test_papers_b_route.py`) = 主线 21 (含 2026-07-02 cross-model FWER `27_tableA12` / 2026-07-03 policy 列族 `28_tableA13`) + 8 个 paper 子目录 123 (含 _allv 3: benefit/strategic/substance) + 历史归档 3; provisional 两篇另 15 不计入。统一头部 `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120` (消费 `$bank_controls` 的根级模板刻意省略 `clear all`)。
- pyreadstat 写 `.dta` 用 **format version 118** (文件格式 spec 编号, 非 Stata 应用版本; Stata 19 读取无限制, 勿与 `version 19` 混淆)。

## Known Issues & Workarounds

1. **Windows line endings**: Git 可能 warn CRLF (Windows 预期)。repo 根 `.gitattributes` 标 `*.parquet`/`*.xlsx`/`*.db` 为 binary; 源文件保持磁盘上的 EOL (不强制 LF 归一, CRLF warning 无害)。
2. **FinBERT2 model**: stage 23 需私有微调模型; `FINBERT2_MODEL_DIR` 未设/无效时优雅跳过该模型 (其余 BERT 照跑)。

## Phase History

项目历经 9 次重构 (v1.x → v2.1.0): package skeleton + DAG 单源 → 拆分巨石 + OUTPUT_REGISTRY + acceptance gate → 多论文产品化 + 7-domain config 拆分 → 数据布局规范化 → 清理。后续版本演进 (v3.x) 见 git history; 当前 HEAD baseline 见顶部 "Current version" + "当前状态铁律"。
