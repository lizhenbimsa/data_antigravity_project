# CLAUDE.md

Claude Code (claude.ai/code) 在本仓工作的指引。

# Communication
- 一律用简体中文回复, 用中文解释代码改动。
- 代码注释: 技术术语英文, 解释中文 (沿用 `core/`/`pipeline/`/`papers/` 既有中英混排惯例)。

## Project Overview
**news_process**: 把中文银行/金科新闻转成银行-年面板 (计量用): preprocessing → classification → sentiment (LLM/词典/BERT) → 面板构建。

**Current version**: v3.16.0 (2026-07-17)。逐版 changelog 见 git history (CHANGELOG.md 未维护); 本文件 + git history 是版本权威源, 每次大改的权威执行计划在 `scripts/audit/*_EXECUTION_PLAN_*.md`。⚠ 2026-07-21 生产词典换血: `config/fintech_dict.json` 1506→**607 词** (main=b7b70b08, sha16=9c731b78379401e9); 全链缓存/产物已随 2026-07-21/22 九入口审计在线回填重算 (见 `scripts/audit/NINE_ENTRYPOINT_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-21.md`); locus_split/S13 placebo/benefit sidecar 三事项待研究决策 (同计划 §4)。

## 当前状态铁律 (load-bearing, 改动前必读)

**计数不变量**: STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16。注册=32 (16+16); 3 个不注册 shim: 80 (audit-only) / 81、82 (user-CLI, `schemas.py` 显式排除)。阶段增删必同步 `core/dag.py` + `core/schemas.py::OUTPUT_REGISTRY`, 跑 `test_dag_consistency.py`。

**全局稳健性铁律** (下方所有梯子/轨/权重/判据通用, 不再逐处重复): 各变体各自 **just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J**; 梯子间正交不交叉。

**嵌入架构 (co-primary 双轨, 零本地模型)**: canonical 无后缀槽 = `Qwen/Qwen3-Embedding-8B` (硅基流动 `https://api.siliconflow.cn/v1`, 4096 维); `_lg` 槽 = `text-embedding-3-large` (OpenAI/yunwu, 3072 维)。两轨严格 parity (列名双射 both-or-neither; 任一 embed None → 同族两列同置 NaN)。引擎 `embed_texts` 纯 API、维度无关 (由 `emb.shape[1]` 驱动), token 切块 cl100k/8191。stage 15/25/26 产双轨嵌入列。**carve-out**: `surface_staleness`/`surface_highstale` 是 MinHash (非嵌入), 无 `_lg` 孪生。
- **换嵌入模型入口**: config 键 `config/features.yaml::embedding_api` + 散落硬编码回退 (核心 4 处 `embedding_engine.spec_model` / `article_sbert._SBERT_MODEL_ID` / `strategic_diff._emb_main` / `stata_export._QWEN_ANNOT`; 另有 producer 内兜底) — 以 `grep 'Qwen/Qwen3-Embedding-8B'` 全仓非测试文件逐处改, 否则 config 改了回退仍指旧模型。完整清单见 `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN`。`spec_uses_local` 恒 False 纯谓词守卫 (勿删)。
- ⚠ 换嵌入前必先删盘上冻结阈值文件 (如 `data/processed/_benefit_center_sidecar.json`), 否则跨嵌入空间阈值守卫 fail-loud → stage 40 benefit 崩。
- **零 instruct 前缀 (刻意, 绝不加)**: 嵌入用于对称相似度任务, 加官方非对称检索前缀会任务失配, 且无前缀文本已冻结播种为缓存键 → 加前缀 = 全部嵌入缓存作废 + golden 全漂移。
- 🚫 **嵌入 ≠ LLM**: stage 21 情感 LLM 是三家投票 (`gpt-5.4-nano`/gpt54nano · `gemini-3.1-flash-lite`/gemini31 走 yunwu · `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com), 与嵌入模型无关 — 换嵌入时全仓零误改。
- gate: `test_embedding_coprimary_parity` + `test_qwen_semantic_validity` (ρ≥0.80 / ≥500 对)。⚠ 生产首次播种须验硅基流动 >256 批是否限流 (探针仅验到 n≤256)。

**三轨 `_full`/`_ctx`/`_ss`**: full=标题+正文; ctx=标题+实体窗口; ss=标题+银行∧金科同句±N 窗 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认1; ≠ `cooccurrence_filter.sentence_radius`)。三轨文本 (`content_{full,ctx,ss}` + `*_is_fallback`) 在 stage 14 `ctx_materializer` 物化 (`prepend_title`, 原始`内容`列不动); 情感 21/22/23/24 均跑三轨。判定不对称: 银行侧=否定+短名过滤, 金科侧=裸 AC 607 词 (2026-07-21 词典换血 1506→607, main=b7b70b08)。
- **回退语义** (`_ss` 镜像 `_ctx`): 无同句共现 → `content_ss`=全文 body + `ss_is_fallback`=True; `FINTECH_AC=None` → `*_is_fallback` 全 True 优雅降级。
- 无 `_title` 独立轨 (v3.8.0 删, 标题改 prepend); 保留非情感信号 `target_bank_in_title` / `fintech_in_title`+`in_title` / `headline_frac` — 勿连带删。
- 🔒 **留篇门控 = full-only** (2026-06-29): stage 21 是否判为「一篇银行金科报道」只看 `llm_verified_full == True`; ctx/ss 降为 conditional-on-full 稳健性轨。**2 处门控副本必须同步翻** (不同改 → 永久 reject skip → 每跑付费 stage 21): ① `tone_llms.py::df_filtered`; ② `run_pipeline_function.py::_stage21_skip_is_compatible`。skip 上游指纹含三轨文本+回退列, 改物化参数后指纹自动 reject。
- P1 `bank_fintech_tone` + prov `bank_news_clarity` 主轨已切 `_full`; `llm_vote_tone_full` 由 P1 与 llm_peer 刻意共享 (`test_paper_namespace_isolation.py::SHARED_CONTROLS` 白名单)。

**stage 13 共现硬过滤** (`13_cooccurrence_filter.py`): 硬过滤丢行, 只留「目标银行与 ≥1 金科词邻近共现」的文章。生产口径 = `sentence_radius=1` + `match_in_title=true` (`config/filtering.yaml::cooccurrence_filter`; 路径键仍 `output_12b_cooccurrence`)。判据原语 `entity_context.has_bank_fintech_cooccurrence_within_radius` (与 `_ss` 严格同句的 `extract_bank_fintech_cooccurrence` 不同口径, 禁互相复用)。**安全**: `FINTECH_AC=None` → 保留全部行 + loud WARNING (绝不静默清空); keep 率 < `min_keep_frac` 或 0 行 → `SystemExit(1)`。

**always-on**: 情感 21/22/23/24 + 全部 14 验证阶段无条件启用。谓词函数/`filter_enabled`/`get_script_for_method` 保留为纯函数供测试 (勿删)。⚠ stage 26 staleness 须装 `faiss-cpu`/`datasketch` (缺则真崩)。

**列族扩展** (详见各 SSOT + 执行计划; 均遵全局稳健性铁律):
- **IV 扩展** (`pipeline/panel/iv_extensions.py`, runner 步骤 8z): 三引擎 → `leave_one_out_peer_*_iv`/`bartik_*_iv`/`outlet_*_iv` + 7 paper_spec + 7 个 2SLS 模板。
- **词典消融梯度**: 三语言学规则 powerset → `{dict}_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}` × 6 词典 × 3 轨。SSOT=`_RULE_ABLATION_VARIANTS`; 高度共线 (corr≈0.99) 报 corr 不并入同式。
- **LLM 三家/BERT 三模型互稳**: canonical headline=`llm_vote_tone` (多数投票, P1 treatment); per-model `{gpt54nano,gemini31,deepseekv4}_tone` / `{finbert_cn,fin_sent_zh,finbert2}` co-equal (**per-model 独立降级, 非 both-or-neither**); BERT signed `{short}_net_tone` (golden 重生 DEFERRED)。SSOT=`encode.LLM_MODELS`/`BERT_MODELS`; 真 FWER=`27_tableA12_cross_model_fwer` (paper_spec `cross_model` 仅声明式文档); 一致性 κ/α 见 `tone_validation.py` (⚠ Cohen κ 须先重映射非负码)。gate=`test_{llm,bert}_model_robustness`。
- **稳健性缺口补齐 (5 梯子)**: ① LLM 分类 per-model — SSOT=`encode.LLM_CLASS_SPEC` (两命名域唯一互锁点, 无字符串变换可达); FWER=27_tableA12 Panel C。② benefit 4 维度六轨 {full,ctx,ss}×{MAIN,_lg} — SSOT=`dimension_analysis._dim_col` (lg 中置), both-or-neither。③ boilerplate 三轨 (非嵌入无 `_lg`)。④ 罕见词 cutoff `RARE_WORD_FREQ_CUTOFFS=(2,3,5)` (canonical=3≡无后缀; 分位梯子在冻结词典上数学退化, 禁用)。⑤ FLS 单/双门二臂 (`frac_fls`=双门 canonical / `frac_fls_fonly`=单门稳健)。根级 +1 = `28_tableA13_policy_family_robustness`。gate=`test_llm_classification_robustness`/`test_benefit_dimension_tracks`/`test_rare_word_cutoff_ladder`。
- **政治词权重敏感性** (du_2022 独有): `political_positive`(1,434 词) 生产口径权重 0.5; 敏感性 ∈ {0.0,0.5,1.0} (`du_2022_polw{00,05,10}`, polw05≡canonical)。依据 Du et al. (2022, RoF, doi:10.1093/rof/rfab036) + 研究者选择。SSOT=`tone_words.POLITICAL_WEIGHT_VARIANTS` (byte-sync `encode.POLITICAL_WEIGHT_SUFFIXES`); ⚠ 与规则消融梯度正交不交叉。gate=`test_political_weight_ladder`。
- **网络三轨 + 构造判据**: shock 三轨 (分子分母严格逐轨) + W-轨 (`bank_cogn_mean`/`bank_emb_sim`/diag `emb_peer_tone_diag`, **per-W-轨独立降级**) + 33 结构指标 × 判据 {同篇/±1句 `_win1`/严格同句 `_sent`}(+66 列, 判据主体=银行∧银行)。SSOT=`network_spillover.NETWORK_METRIC_BASES`; ⚠ codebook 三推断函数入口须剥判据后缀 (`_CRITERIA_SFX_RE`)。gate=`test_network_tritrack_expansion`。生产 T=19 播种 DEFERRED。
- **BERT 分布形状五族**: stage 23 概率列纯后处理 +69 列 (entropy/xneg_frac/skew/跨模型双轨/年内 iyvol+iytrend)。SSOT=`pipeline/panel/bert_distribution.py` 叶模块 (**禁反向 import encode** 成环); ⚠ finbert2=Bernoulli 熵与三分类不可比、阈值语义 model-specific (只比标准化 β); 无 `_lg`; 51 个文章级中间列 runner 步骤 9 前单点 drop。gate=`test_bert_distribution_metrics` (15 项)。
- **boilerplate OOM 硬化**: stage 22 单遍 `fit_transform` → 分块 exact two-pass (字节等价, golden 零漂移)。默认 `memory_tier='in_memory'` (tier1); `'single_pass'`=字节等价参照臂 (禁删); `'disk'/'auto'` (tier2) → `raise SystemExit` (**非** NotImplementedError, 会被 `tone_words except Exception` 吞成静默丢列)。SSOT=`boilerplate._make_vectorizer`。⚠ **生产 T=19 铁律**: tier1 只消 CSR (非-binding), vocab-binding 仍驻 RAM → **T=19 OOM 未解决, 须补 tier2 (DEFERRED)**; `df_dict_budget_hard=40M` 是未校准占位, 生产 global_df 极可能超之 → Pass1 内 `SystemExit` 连坐 nuke 整批 stage-22 → **T=19 首播前必先跑计划 §3-P0 按 128GB 反推校准硬闸** (受 M0 审批门约束)。gate=`test_boilerplate_chunked` (17) + `test_boilerplate` (9)。

**已移除阶段** (勿引用, 详见 git history): EPU(原16)/BERTopic(17)/高管 NER(19)/risk_taking_outcomes(49)/llm_contamination_test(39h)/temporal_mask(38a)/track_discriminant(39g)/独立 text2vec(30)+bge 本地嵌入轨。⚠ 勿误删仍活跃的 staleness/`article_sbert`/`news_salience`/`ceo_turnover_2yr`; prov `.do` 模板里 `z_score`/NPL/RWA 是占位变量名 (保留); `config/bank_list.yaml`/`fetch_llm_archive.py` 刻意保留。

## 确定性 / golden (铁律)
- **勿删 `data/processed/_llm_cache.db`** (~2.1GB) — golden 跨-run 复现锚。三轨缓存 0 miss 即可 `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 字节级复现 (miss → raise `LLMCacheMissError`, 不调 API)。缓存键=`prompt_version='v8-2026-05-17'`/`temperature=0.0`; prompt SSOT=`tone_llms.iter_article_track_prompts`。验证: `python -m news_process.scripts.audit.verify_stage21_cache_coverage`。⚠ 嵌入族**亦受** `NEWS_PROCESS_LLM_OFFLINE` 守卫 (`embedding_engine.py` miss→raise `RuntimeError`); 仅在线 miss 才付费。
- **冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1`。
- **golden 重生 DEFERRED 到生产语料机** (本机 data/raw 空、T=2、付费不可逆); 完整付费 LLM 重处理须先过 **M0 审批门**。重生须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1 (`MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1`)。BLAS-FP 非确定网络列 (9 个): `bank_clustering`/`bank_cfbetween_cent`/`bank_harmonic_cent` × {无后缀,_win1,_sent} → 验零漂移须按全名 drop 排除 (`diff_golden.py` 的 `_KNOWN_BLAS_RE` 子串匹配自动覆盖)。换模/改测度类改动 golden 零字节安全须受控全量重生; manuscript 须披露 Google→Qwen 与 full-only 数值副作用 (`n_articles`/`fintech_share`/`attention_pct` 收缩, 非 bug)。
- **本机验证套路**: 改测度类改动本机不动 parquet → 用 baseline-stash A/B 差分证「0 新增失败」(committed golden 本就陈旧, T=2 dev 不新增红灯)。
- **Disk 状态**: ~220 行 (110 banks × 2 years 2017–2018, T=2 dev); 最宽 dta≈3453 列 (随重生漂移, 以实读为准, 勿「旧基数+增量」心算)。真实全量 (目标语料) = **18,198,978 条 / 2007–2025 / T=19** (2026-07-16 裁定: 目标语料=普查全量)。
- **原始语料普查** (stage 00 `raw_census`, 过滤·去重前全量): 183 去重源文件 / 18,198,978 条 / 2007–2025 / 3,740 家媒体; 报纸占 92.93% (16,912,361 行) 保留、其余按行剔除; 精确唯一 18,177,370。该口径即目标语料口径, 但 ≠ stage 00 非递归 `data_excel/*.xlsx` 实处理量。全表见 `build/manual_facts/key_stats.md`。

## CLI 子命令 (`python -m news_process.papers._common.stata_runner <cmd>`)
- `build-replication`: instantiate 21 个根级 `.do` 模板 + spec 替换 (复现包规范入口)。
- `list-templates [--verbose]` / `doctor [--verbose]` (7 段诊断) / `verify-replication <path>` (5 段)。
- panel 迁移: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`。

## Architecture

声明式 DAG 在 `core/dag.py` (`STAGES_MAIN` 生产 / `STAGES_VALIDATION` 评估)。orchestrator `run_pipeline_function.py` 把每阶段当独立子进程跑。

**Stage flow** (authoritative set in `core/dag.py`):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 13_cooccurrence_filter
→ 14_materialize_ctx → 15_fintech_intensity → 16_article_policy_alignment
→ 21_tone_llms / 22_tone_words / 23_tone_berts → 24_herd_decay_processor
→ 40_panel_export_main → 46_stata_export → 51_falsification_test
```
`14_materialize_ctx` 物化 `content_ctx`/`content_ss` 供下游 15/16 真三轨。`25_article_sbert` 仍活跃 (产 co-primary `_lg` 双轨嵌入喂 stage 26; `_t2v`/`_bge` 本地轨 v3.14.0 移除)。

**Directory**:
```
news_process/
├── core/       # config, logging, caching, DAG, stage runner
├── pipeline/   # 阶段实现
├── papers/     # 11 paper 模块 (8 fully-coded + 3 provisional)
├── validation/ # 稳健性测试
├── config/     # 拆分 YAML + prompt 模板 (config.yaml 是 legacy stub)
├── data/       # raw/ 输入 + processed/*.parquet 输出
├── tests/      # 全量 sweep ≈2581 passed / 3 skipped
└── NN_*.py     # 35 thin shims (≤30 行); 32 注册 (16+16); 3 不注册: 80/81/82
```
**Key invariant**: `NN_*.py` 是 thin shim, 逻辑全在 `pipeline.*`/`validation.*`。**绝不**往 shim 加业务逻辑。

**Single Sources of Truth**:
1. DAG: `core/dag.py::STAGES_MAIN`/`STAGES_VALIDATION`
2. Output registry: `core/schemas.py::OUTPUT_REGISTRY`
3. Config: `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. Dependencies: `pyproject.toml::[project].dependencies` (requirements.txt 是 fallback)

**Data Flow**: `data/raw/*.xlsx` → `data/processed/NN_*.parquet` (每阶段一个) → `40_panel_yearly.parquet` (银行-年面板); 日志 `logs/<stage>.log` (扁平, 每阶段一文件, 每次运行覆盖)。

## Development Commands
```bash
# 环境 (Windows PowerShell venv; 解释器走 conda base python 3.13)
python -m venv venv && venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp news_process/.env.example news_process/.env   # 填 YUNWU_API_KEY / DEEPSEEK_API_KEY / SILICONFLOW_API_KEY
pre-commit install

# 跑 pipeline (从 repo 根 f:\WiseSearch\data_antigravity_project\)
python run_pipeline_function.py     # 全主线
python run_pipeline_validation.py   # 验证 pipeline
python 21_tone_llms.py              # 单阶段调试

# 测试 (必须从 repo 根跑, 否则绕过 pyproject testpaths)
pytest                    # 全量
pytest -m fast            # 快测 (~30s, commit 前)
pytest -m integration     # 集成 (~5min)
pytest -k "test_golden"

ruff check . ; ruff check --fix .

# Golden 重生 (列 schema 变更后)
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol
1. **绝不 amend** (除非显式要求); pre-commit hook 失败后创建**新** commit。
2. **按文件名 stage** (`git add <file>`), 避免 `git add .`/`-A` (防误提 secrets); 共享树并发会话尤须 by-name (排除 `*constants.json`/`eval_reports` 等并发产物)。
3. Commit message: HEREDOC + `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer。
4. **绝不 `--no-verify`** (除非显式要求)。

### Code Modification Rules
1. **Shim 冻结**: 35 个 `NN_*.py` ≤30 行, 逻辑归 `pipeline.*`/`validation.*`。
2. **DAG consistency**: 阶段增删同步 `STAGES_MAIN`/`STAGES_VALIDATION` + `OUTPUT_REGISTRY` (产 parquet 时), 跑 `test_dag_consistency.py`。
3. **Config split active**: `load_config()` 优先 7-domain 拆分 YAML, 全缺才回退 legacy; 拆分文件须语义等价 legacy 契约。
4. **Golden**: 列 schema 变更后经 `generate_golden_snapshot.py` 重生 `tests/fixtures/golden_panel_v0.json`。

### Testing Requirements
- **Integration gate**: `tests/integration/test_panel_reproducibility.py` 必过 (列哈希对 golden)。
- **DAG consistency** (2026-07-18 收紧): `test_dag_consistency.py` 强制双向集合恒等 (OUTPUT_REGISTRY==STAGES_MAIN scripts 且 EXPECTED_NO_OUTPUT_STAGES==STAGES_VALIDATION scripts, 各 len==16, orchestrator import 与 `core/dag.py` identity 一致)。`test_pipeline_shims.py` 锁 32 注册 script 盘上存在+thin ≤30 与 35 普查集合恒等。
- **Mock 外部 API**: 测试必 mock LLM/embedding API (范例 `tests/test_25_audit.py`)。

## Common Patterns
- **加阶段**: 实现 `pipeline/<module>/<stage>.py` → thin shim `NN_<stage>.py` → 注册 `STAGES_MAIN`(/`STAGES_VALIDATION`) → 产 parquet 加 `OUTPUT_REGISTRY`, 否则加 `EXPECTED_NO_OUTPUT_STAGES` → 测试 → 跑 `test_dag_consistency.py`。⚠ 该 gate 现为双向恒等, 若加「MAIN 无输出阶段」须按失败消息放宽恒等式并同步计数不变量。
- **改 config schema**: 改拆分 YAML → 仅 loader 语义变时改 `load_config()` → 列 schema 变则重生 golden → 全量测试。
- **调试失败阶段**: 看 `logs/<stage>.log` → 单跑 `python news_process/NN_<stage>.py` → `pytest tests/test_XX_<stage>.py -v` → 查 `data/processed/`。

## Environment Variables (`.env`)
- `YUNWU_API_KEY`: stage 21 (gpt54nano/gemini31) + 若干 LLM 验证阶段 (66/70) + `_lg`/yunwu 嵌入。
- `DEEPSEEK_API_KEY`: stage 21 第三家 `deepseek-v4-flash` (直连 api.deepseek.com)。离线命中不需; 生产首跑/播种须填。
- `SILICONFLOW_API_KEY`: canonical Qwen 嵌入轨。
- `EMBEDDING_API_KEY`: 默认 `${YUNWU_API_KEY}` (可覆盖独立端点)。
- `FINBERT2_MODEL_DIR`: 可选本地 BERT (stage 23 缺失时优雅跳过)。
- ⚠ `LLMs_for_FinTech_dic/` 独立管道用**独立开关 `LLMS_DIC_OFFLINE`** (`NEWS_PROCESS_LLM_OFFLINE` 对其无效)。
- ⚠ 裸环境嵌入 SSL 报错 → 设 `SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")`; 重跑 stage 23 BERT 设 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`。

## Multi-Paper Support
`papers/` 含 11 个模块 (8 fully-coded + 3 provisional), 全部具备 `analysis.py`/`figures.py`/`tables.py`, 纳入 `paper_registry.PAPER_IDS_ALL`。
- **P1–P5 主线** (`bank_fintech_*`): tone (P1) / attention (P2) / substance (P3) / locus (P4) / collab (P5, prov)。
- **衍生/prov**: `benefit_society` · `brokerage_network` · `llm_peer` · `strategic_diff` · `bank_media_disagreement` (prov) · `bank_news_clarity` (prov)。
- **treatment vs outcome 是两套**: 主轨 treatment 多为 `*_full` (P1=`llm_vote_tone_full`); outcome/DV 另定 (P1 `funding_cost` / P2 `ln_fintech_investment` / P3 `cost_income_ratio_change_3yr` / P4 `citation_weighted_patent` / P5 `m_and_a_fintech` / benefit&brokerage `roa` / llm_peer `avg_ft_intensity_full` / strategic_diff `tobin_q` / prov `z_score`), 多为外部财务哨兵列。详见 memory `outcome-redesign-2026-06-13`。
- 公用工具 `papers/_common/` (含 `AI_DISCLOSURE_TEMPLATES.md` 6 系列)。
> 注: paper ID `P1..P5` 是 portfolio 本地编号, 与其它文档/计划的 `P1/P2/..` 步骤编号是两个独立空间。

## Stata Environment
**本机 StataNow/MP 19.5** (`C:\Program Files\StataNow19\StataMP-64.exe`, 64-core, 128GB)。**策略: Stata 19+ only, 无需向下兼容**。

### 启动约定 (防「已完成」弹框)
- **一律 `/b` 批处理** (Windows 用斜杠 `/b` 不是 `-b`); **禁** `/e` 与裸 GUI/双击。
- ⚠ `/b` 不弹框前提是 do-file 干净收尾。两层防御: ① 走 `/b` 或封装 `stata_runner.py::run_do`/`scripts/run_stata.ps1` (硬编码 `/b`); ② ad-hoc/probe `.do` 末尾加 `exit, clear`。⚠ 终端 `exit` 只加在 standalone/`00_master.do` 末尾, **绝不**加进被 master 调用的子 `.do`。
- `StataMP-64.exe` 是 GUI 子系统 → PowerShell `&` 立即返回, 必须 `Start-Process -Wait`:
```powershell
$exe = "C:\Program Files\StataNow19\StataMP-64.exe"
Start-Process -FilePath $exe -ArgumentList '/b','do','"<绝对路径\x.do>"' `
  -WorkingDirectory "<.do 所在目录>" -Wait -PassThru | ForEach-Object { "退出码=$($_.ExitCode)" }
# 退出码不完全可信 → 跑完扫同名 .log 的 r(###) 取真实结果
```

### 容量 / 模板
- MP 硬上限远未触顶 (maxvar 120,000)。**core/aux IC 双切分已退役** (单一全列 `.dta`) — **勿**在模板硬编码「前 N 列」截断。行数瓶颈在面板深度 (T=2)。
- 稳健性 battery (`bootstrap`/`rwolf`/`ritest`/`csdid`) 本机自动拉满 (`set processors 64`); `matsize` Stata 19 自动管理。
- **147 个 `.do.tmpl`** (`papers/_common/stata_templates/` rglob) = 主线 21 (含 `27_tableA12`/`28_tableA13`) + 8 个 paper 子目录 123 + 归档 3; prov 两篇另 15 不计入。统一头部 `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120` (消费 `$bank_controls` 的根级模板刻意省略 `clear all`)。
- pyreadstat 写 `.dta` 用 **format version 118** (文件格式 spec 编号, ≠ Stata 应用版本; 勿与 `version 19` 混淆)。

## Known Issues & Workarounds
1. **Windows line endings**: Git 可能 warn CRLF (预期无害)。repo 根 `.gitattributes` 标 `*.parquet`/`*.xlsx`/`*.db` 为 binary; 源文件保持磁盘 EOL。
2. **FinBERT2 model**: stage 23 需私有微调模型; `FINBERT2_MODEL_DIR` 未设/无效时优雅跳过 (其余 BERT 照跑)。

## Phase History
项目历经 9 次重构 (v1.x → v2.1.0): package skeleton + DAG 单源 → 拆巨石 + OUTPUT_REGISTRY + acceptance gate → 多论文产品化 + 7-domain config 拆分 → 数据布局规范化 → 清理。v3.x 演进见 git history; 当前 HEAD baseline 见顶部 "Current version" + "当前状态铁律"。
