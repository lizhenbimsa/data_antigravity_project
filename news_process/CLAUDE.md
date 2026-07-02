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
- 🚫 **嵌入 ≠ LLM**: stage 21 情感 LLM 是三家投票 (`gpt-5.4-nano`/gpt54nano · `gemini-3.1-flash-lite`/gemini31 两家走 yunwu · `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com; panel 列含 `*_gemini31_*`), 与嵌入模型**无关** — 换嵌入时全仓零误改。
- **换嵌入模型的入口**: config 键 `config/features.yaml::embedding_api` (model/base_url/api_key/text_pipeline_version) + **散落的硬编码默认回退须同步改** (核心 4 处 `embedding_engine.spec_model` / `article_sbert._SBERT_MODEL_ID` / `strategic_diff._emb_main` / `stata_export._QWEN_ANNOT`; 另有 `policy_alignment` / `benefit_society_audit_combined` / `dimension_analysis` 等 producer 内兜底 — 以 `grep 'Qwen/Qwen3-Embedding-8B'` 全仓非测试文件逐处改), 否则 config 改了回退仍指旧模型 → 静默不一致。`spec_uses_local` 保留为恒 False 纯谓词作 producer fail-fast 守卫 (勿删)。完整清单见 `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN`。
- ⚠ 换嵌入前必先删盘上冻结阈值文件 (如 `data/processed/_benefit_center_sidecar.json`): 跨嵌入空间的阈值守卫会 fail-loud, 否则 stage 40 benefit 崩。
- gate 测试: `test_embedding_coprimary_parity` (列双射+carve-out) + `test_qwen_semantic_validity` (Spearman ρ≥0.80 / ≥500 对)。⚠ 生产首次播种须验硅基流动 >256 的批是否限流 (探针仅验到 n≤256)。

**三轨 `_full` / `_ctx` / `_ss`**: full=标题+正文; ctx=标题+实体窗口; ss=标题+银行∧金科同句±N窗 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认1; 与下方 `cooccurrence_filter.sentence_radius` 是**两个不同键**)。三轨文本 (`content_full`/`content_ctx`/`content_ss` + `*_is_fallback`) 在 stage 14 `ctx_materializer` 物化 (`prepend_title`, 原始`内容`列不动; stage 13 是上游共现硬过滤, 不物化文本列); 情感 21/22/23/24 均跑三轨。判定不对称口径: 银行侧=否定+短名过滤, 金科侧=裸 AC 1506 词。
- **回退语义** (`_ss` 镜像 `_ctx`): 无银行∧金科同句共现 → `content_ss`=全文 body, `ss_is_fallback`=True (共享 `n_articles` 分母); `FINTECH_AC=None` → `*_is_fallback` 全 True 优雅降级。
- 无 `_title` 独立轨 (v3.8.0 删, 标题改 prepend); 保留非情感信号 `target_bank_in_title`(news_bank.py) / `fintech_in_title`+`in_title`(news_fintech.py) / `headline_frac`(controls.py) — 勿连带删。
- ⚠ 三轨禁混同一 over-identified Hansen J。
- **留篇门控 = full-only** (2026-06-29): stage 21 是否判为"一篇银行金科报道"只看 `llm_verified_full == True`。ctx/ss 降为 **conditional-on-full** 测度/稳健性轨 (行宇宙 = full 留篇集子集, per-track 列照算)。**2 处门控副本必须同步翻**: ① `tone_llms.py::df_filtered`; ② `run_pipeline_function.py::_stage21_skip_is_compatible` (不同改 → 永久 reject skip → 每跑付费 stage 21)。
- P1 `bank_fintech_tone` + provisional `bank_news_clarity` 主轨已切 `_ctx→_full`。`llm_vote_tone_full` 由 P1 与 llm_peer 刻意共享 (`test_paper_namespace_isolation.py::SHARED_CONTROLS` 白名单, 镜像 z_score 跨篇共享先例)。clarity 的 5 个 `.do` 模板仍以 `_ctx` 为 headline (M7-deferred)。

**stage 13 共现硬过滤** (`13_cooccurrence_filter.py`, 原 stage 12b): 硬过滤丢行, 只保留"目标银行与 ≥1 金科词邻近共现"的文章。生产口径 = `sentence_radius=1` (±1 句窗口) + `match_in_title=true` (标题+正文), 见 `config/filtering.yaml::cooccurrence_filter`; 输出路径键仍是 `config/paths.yaml::output_12b_cooccurrence` (重编号未改 config 键)。判据原语 `core/text/entity_context.py::has_bank_fintech_cooccurrence_within_radius` (与 `_ss` 严格同句的 `extract_bank_fintech_cooccurrence` 不同口径, **禁互相复用**)。**安全**: `FINTECH_AC=None` → 保留全部行 + loud WARNING (绝不静默清空); keep 率 < `min_keep_frac` 或 0 行 → `SystemExit(1)`。

**always-on**: 情感 21/22/23/24 + 全部 14 验证阶段无条件启用 (StageSpec 默认 `always_enabled`, 无 `enabled_when`; `METHOD_TO_PREDICATE={}`)。谓词函数 / `filter_enabled` / `get_script_for_method` 保留为纯函数供测试 (勿删)。⚠ stage 26 staleness always-on 后须装 `faiss-cpu`/`datasketch` (缺则真崩, 不再优雅跳过)。

**IV 扩展** (`pipeline/panel/iv_extensions.py`, runner 步骤 8z, `config/panel.yaml::compute_iv_extensions` 默认 true): 三引擎 (同组 LOO 均值 / 广义 Bartik / 媒体来源 house-style 暴露) → 面板 IV 列族 (`leave_one_out_peer_*_iv` / `bartik_*_iv` / `outlet_*_iv`) + 7 篇 paper_spec `identification.iv` + 7 个 2SLS 模板。

**词典消融梯度** (v3.11.1): tone_words 三语言学规则 (否定翻转 / 程度副词 / 转折) 全 powerset 物化为消融变体 `{dict}_score_{raw,degonly,advonly,negdeg,negadv,degadv}` × 6 词典 × 3 轨 + 同名 panel 聚合 + geography `dict_avg_{sfx}_tone{track}`。各变体自归一化、非可加分解 (audit MATH-1: 高度共线 corr≈0.99, 报 corr 而非并入同式)。SSOT = `_RULE_ABLATION_VARIANTS`。

**政治词权重敏感性** (du_2022 独有): `du_2022` 的 `political_positive`(1,434 词) 生产口径以 **0.5** 权重计入正侧。**两句话依据** (comments/logs/codebook/stata/tone_dicts.json 同源, SSOT=`tone_words.POLITICAL_WEIGHT_RATIONALE`): ① 依据 Du et al. (2022, *Review of Finance*, doi:10.1093/rof/rfab036) 政治正面词信号弱于普通正面词的发现, 对该类词赋予降低的权重; ② 权重取 0.5 为研究者选择, 并做敏感性检验: 令政治词权重 ∈ **{0.0, 0.5, 1.0}** 三者**互为稳健性、不分主次**, 证明主结论不被这一取值驱动。落地: `article: du_2022_score_polw{00,05,10}` / `panel: du_2022_polw{00,05,10}_tone{track}` (polw05 ≡ canonical `du_2022_score`/`du_2022_tone`, 无后缀为历史命名产物非"主"; 镜像 co-primary 嵌入双轨口径)。SSOT = `tone_words.POLITICAL_WEIGHT_VARIANTS` (byte-sync `encode.POLITICAL_WEIGHT_SUFFIXES`)。⚠ 与规则消融梯度**正交、不交叉** (三权重均在全语言学规则下算, 避免 3×8 列爆炸); ⚠ **铁律**: 三权重各自 just-identified 并排, **禁混进同一 over-identified Hansen J** (同三轨 / co-primary 嵌入铁律)。gate 测试 `tests/test_political_weight_ladder.py`。

**已移除阶段** (勿引用, 详见 git history): EPU 宏观控制(原16) / BERTopic 主题(17) / 高管 NER(19) / risk_taking_outcomes(49) / llm_contamination_test(39h) / temporal_mask(38a) / track_discriminant(39g) / 独立 text2vec(30)+bge 本地嵌入轨。⚠ 勿误删仍活跃的 staleness/`article_sbert`/`news_salience`/`ceo_turnover_2yr`; provisional `.do` 模板里的 `z_score`/NPL/RWA 是占位变量名 (保留); `config/bank_list.yaml`、`fetch_llm_archive.py` 刻意保留。

## 确定性 / golden (铁律)

- **勿删 `data/processed/_llm_cache.db`** (~2.1GB, 随缓存播种增长; ⚠ `data/processed/_cache/_llm_cache.db` 是 0 字节空壳, 勿认错) — golden 跨-run 可复现锚。三轨 (full/ctx/ss) 在缓存 **0 miss** 即可 `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 字节级复现 (miss → raise `LLMCacheMissError`, 不调 API, 跳过 preflight 探针)。缓存命中键 = `prompt_version='v8-2026-05-17'` / `temperature=0.0`; prompt 构造 SSOT = `tone_llms.iter_article_track_prompts` (生产/审计共用 → 缓存键一致)。验证: `python -m news_process.scripts.audit.verify_stage21_cache_coverage`。⚠ 嵌入族**亦受** `NEWS_PROCESS_LLM_OFFLINE` 守卫 (`embedding_engine.py` 内 miss→raise `RuntimeError`, 与 stage 21 `LLMCacheMissError` 对称但异常类型不同、live 逐次读非 import 快照); 仅在线 (env 未设或为非真值) miss 才付费。
- **冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1` (不重跑 stage 21, $0 LLM)。
- **golden 重生 DEFERRED 到生产语料机** (本机 data/raw 空、T=2、无生产语料、付费不可逆); 完整付费 LLM 重处理 (stage 21 全量重跑) 须先过 **M0 审批门**。重生须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1 (`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/`NUMEXPR`/`OMP_NUM_THREADS`=1)。3 个网络中心度列 (`bank_clustering` / `bank_cfbetween_cent` / `bank_harmonic_cent`) BLAS-FP 非确定 → 验零漂移须排除。换模/改测度类改动 golden **零字节安全**须受控全量重生; manuscript 须披露厂商维度 Google→阿里 Qwen 与 full-only 数值副作用 (`n_articles`/`fintech_share`/`attention_pct` 收缩, 均非 bug)。
- **本机验证套路**: 改测度类改动本机不动 parquet → 用 baseline-stash A/B 差分证"0 新增失败"(committed golden 本就陈旧, T=2 dev 不新增红灯)。
- **Disk 状态**: ~172 行 (86 banks × 2 years 2017–2018, T=2 dev); 最宽 dta ≈ 2782 列 (随重生漂移, 以实读为准)。真实全量 = 1700 万条 / 2007–2024 / T=18。

## CLI 子命令 (`python -m news_process.papers._common.stata_runner <cmd>`)

- `build-replication`: 一键 instantiate 19 个根级 `.do` 模板 + spec 替换 (构建复现包的规范入口)。
- `list-templates [--verbose]`: 模板清单 + 占位符 inventory。
- `doctor [--verbose]`: 6 段诊断 (Python 依赖 / pipeline 数据 / LLM cache / LLM API / Stata bin / Stata ado 包)。
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
- **142 个 `.do.tmpl`** (计数口径 = `papers/_common/stata_templates/` rglob, 见 `test_papers_b_route.py`) = 主线 19 + 8 个 paper 子目录 120 + 历史归档 3; provisional 两篇另 15 不计入。统一头部 `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120`。
- pyreadstat 写 `.dta` 用 **format version 118** (文件格式 spec 编号, 非 Stata 应用版本; Stata 19 读取无限制, 勿与 `version 19` 混淆)。

## Known Issues & Workarounds

1. **Windows line endings**: Git 可能 warn CRLF (Windows 预期)。repo 根 `.gitattributes` 标 `*.parquet`/`*.xlsx`/`*.db` 为 binary; 源文件保持磁盘上的 EOL (不强制 LF 归一, CRLF warning 无害)。
2. **FinBERT2 model**: stage 23 需私有微调模型; `FINBERT2_MODEL_DIR` 未设/无效时优雅跳过该模型 (其余 BERT 照跑)。

## Phase History

项目历经 9 次重构 (v1.x → v2.1.0): package skeleton + DAG 单源 → 拆分巨石 + OUTPUT_REGISTRY + acceptance gate → 多论文产品化 + 7-domain config 拆分 → 数据布局规范化 → 清理。后续版本演进 (v3.x) 见 git history; 当前 HEAD baseline 见顶部 "Current version" + "当前状态铁律"。
