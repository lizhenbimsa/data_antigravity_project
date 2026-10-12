# CLAUDE.md

Claude Code (claude.ai/code) 在本仓工作的指引。

# Communication
- 一律用简体中文回复, 用中文解释代码改动。
- 代码注释: 技术术语英文, 解释中文 (沿用 `core/`/`pipeline/`/`papers/` 既有中英混排惯例)。

## Project Overview
**news_process**: 把中文银行/金科新闻转成银行-年面板 (计量用): preprocessing → classification → sentiment (LLM/词典/BERT) → 面板构建。

**Current version**: v3.16.0 (2026-07-17)。逐版 changelog 见 git history (CHANGELOG.md 未维护); 本文件 + git history 是版本权威源, 每次大改的权威执行计划在 `scripts/audit/*_EXECUTION_PLAN_*.md`。⚠ 2026-07-21 生产词典换血: `config/fintech_dict.json` 1506→**607 词** (main=b7b70b08, sha16=9c731b78379401e9); 全链缓存/产物已随 2026-07-21/22 九入口审计在线回填重算 (见 `scripts/audit/NINE_ENTRYPOINT_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-21.md`)。2026-07-22 用户裁定**全项目 607 化、严禁 1506 残留**, 三决策项已落地: S13-v2 placebo 白名单换血 {自助银行}; locus_split v2 增量双编码 (289 新词 κ=0.8418, 三桶 215/307/85, v1 双编码表冻结存档); benefit sidecar 补第 4 指纹 `dict_sha256` + 删旧重冻结 (607 语料 median), 27 号/80 号/两侧线同批重生。

**⚠ 2026-08-02 聚合中转平台迁移 (yunwu.ai → OpenLux)**: OpenAI/Google 两家 LLM 与 `_lg` 嵌入孪生轨的 base_url 全部由 `https://yunwu.ai/v1` 换为 **`https://api.openlux.ai/v1`**; 环境变量 `YUNWU_API_KEY`→**`OPENLUX_API_KEY`**、`YUNWU_FULL_KEY`→**`OPENLUX_FULL_KEY`** (密钥值沿用同一串, 实测 OpenLux 认此 key)。DeepSeek 直连 (`api.deepseek.com`) 与硅基流动 Qwen 嵌入主轨 (`api.siliconflow.cn`) **零改动**。
- 🔑 **缓存零失效 (本次迁移最重要的不变量)**: 缓存键 = `(model_id, prompt, prompt_version, temperature[, seed])`, **不含 base_url/端点/密钥** (`core/caching.py::_make_key`); 且 stage 21 的 `model_id = model_cfg['model_name']`、嵌入侧 = spec 的 `model` + `text_pipeline_version` —— 这三个字段本次 diff **一个都没动**。故 137 GB `_llm_cache.db` 全部条目迁移后仍逐位命中, **零付费重播种、golden 零漂移**。改端点时切勿顺手改 `model_name`/`model`/`text_pipeline_version`, 那才会炸缓存。
- ✅ 迁移实测 (2026-08-02): `GET /v1/models` HTTP 200 / 481 个授权模型; `gpt-5.4-nano`、`gemini-3.1-flash-lite`、`text-embedding-3-large` 三个生产依赖模型全部可用; 端到端冒烟 (force_json chat ×2 + embeddings ×1, 绕缓存直连) schema 全兼容, `_lg` 返回 3072 维与契约一致。
- 📜 **历史取证刻意保留 yunwu 字面量** (勿再"清残留"): 22 份历史审计/执行计划文档已加 `2026-08-02 状态订正` 横幅但**保留原文**; `scripts/audit/_replan_v5_evidence/*.json`(原始探针响应)、`data/llm_archive/**/*.jsonl`(原始 API 响应存档, 内含真实 `api_endpoint`)、`21_tone_llms_lineage.json`、历次运行日志、`LLMs_for_dic/保存20260214/` 归档快照**一律不改** —— 它们记录的是当时对 yunwu.ai 的真实调用, 改写即伪造取证链。11 篇论文手稿已切 OpenLux 并加 provenance 脚注 (说明本文数据的推理发生在迁移前、经确定性缓存逐位复现)。

## 当前状态铁律 (load-bearing, 改动前必读)

**计数不变量**: STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16。注册=32 (16+16); 3 个不注册 shim: 80 (audit-only) / 81、82 (user-CLI, `schemas.py` 显式排除)。阶段增删必同步 `core/dag.py` + `core/schemas.py::OUTPUT_REGISTRY`, 跑 `test_dag_consistency.py`。

**全局稳健性铁律** (下方所有梯子/轨/权重/判据通用, 不再逐处重复): 各变体各自 **just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J**; 梯子间正交不交叉。

**嵌入架构 (co-primary 双轨, 零本地模型)**: canonical 无后缀槽 = `Qwen/Qwen3-Embedding-8B` (硅基流动 `https://api.siliconflow.cn/v1`, 4096 维); `_lg` 槽 = `text-embedding-3-large` (OpenAI/OpenLux, 3072 维)。两轨严格 parity (列名双射 both-or-neither; 任一 embed None → 同族两列同置 NaN)。引擎 `embed_texts` 纯 API、维度无关 (由 `emb.shape[1]` 驱动), token 切块 cl100k/8191。stage 15/25/26 产双轨嵌入列。**carve-out**: `surface_staleness`/`surface_highstale` 是 MinHash (非嵌入), 无 `_lg` 孪生。
- **换嵌入模型入口**: config 键 `config/features.yaml::embedding_api` + 散落硬编码回退 (核心 4 处 `embedding_engine.spec_model` / `article_sbert._SBERT_MODEL_ID` / `strategic_diff._emb_main` / `stata_export._QWEN_ANNOT`; 另有 producer 内兜底) — 以 `grep 'Qwen/Qwen3-Embedding-8B'` 全仓非测试文件逐处改, 否则 config 改了回退仍指旧模型。完整清单见 `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN`。`spec_uses_local` 恒 False 纯谓词守卫 (勿删)。
- ⚠ 换嵌入前必先删盘上冻结阈值文件 (如 `data/processed/_benefit_center_sidecar.json`), 否则跨嵌入空间阈值守卫 fail-loud → stage 40 benefit 崩。
- **零 instruct 前缀 (刻意, 绝不加)**: 嵌入用于对称相似度任务, 加官方非对称检索前缀会任务失配, 且无前缀文本已冻结播种为缓存键 → 加前缀 = 全部嵌入缓存作废 + golden 全漂移。
- 🚫 **嵌入 ≠ LLM**: stage 21 情感 LLM 是三家投票 (`gpt-5.4-nano`/gpt54nano · `gemini-3.1-flash-lite`/gemini31 走 OpenLux · `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com), 与嵌入模型无关 — 换嵌入时全仓零误改。
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
- **boilerplate OOM 硬化**: stage 22 单遍 `fit_transform` → 分块 exact two-pass (字节等价, golden 零漂移)。默认 `memory_tier='in_memory'` (tier1); `'single_pass'`=字节等价参照臂 (禁删); `'disk'/'auto'` (tier2) → `raise SystemExit` (**非** NotImplementedError, 会被 `tone_words except Exception` 吞成静默丢列)。SSOT=`boilerplate._make_vectorizer`。⚠ **生产 T=19 现状 (2026-07-28 订正; 旧载「T=19 OOM 未解决 / T=19 首播前必先跑 §3-P0 校准硬闸」已被生产实跑否证)**: stage 22 已在**生产 T=19 全量语料上跑通** (2026-07-26 ② 全链, 3,744s, EXIT=0, 日志载「boilerplate 三轨派生完成」), 预言的 Pass1 `SystemExit` 连坐**未发生**。同时订正一处**数量级笔误**: `df_dict_budget_hard` 的实际默认是 `_DEFAULT_BUDGET_HARD = **400_000_000` (400M)`, 不是旧载的 40M —— 差 10 倍。⚠ 但**余量仍未测**: `boilerplate.py` 用 `logging.getLogger(__name__)`, 在 F29 (main=e94bf57f) 之前该 logger 链上无 handler, 故那行 `Pass1 完成 (global_df N entry)` **从未落盘**, 实际 global_df 对 400M 的余量至今无证据 (F29 之后即可见)。tier2 (`memory_tier='disk'/'auto'`) 仍 `raise SystemExit` 未实现, 但已不构成 T=19 阻塞项。gate=`test_boilerplate_chunked` (17) + `test_boilerplate` (9)。

**已移除阶段** (勿引用, 详见 git history): EPU(原16)/BERTopic(17)/高管 NER(19)/risk_taking_outcomes(49)/llm_contamination_test(39h)/temporal_mask(38a)/track_discriminant(39g)/独立 text2vec(30)+bge 本地嵌入轨。⚠ 勿误删仍活跃的 staleness/`article_sbert`/`news_salience`/`ceo_turnover_2yr`; prov `.do` 模板里 `z_score`/NPL/RWA 是占位变量名 (保留); `config/bank_list.yaml`/`fetch_llm_archive.py` 刻意保留。

## 确定性 / golden (铁律)
- **勿删 `data/processed/_llm_cache.db`** (**137.15 GB / 3,596,160 条**, 2026-07-28 实测; 旧载「98.9 GB / 3,037,107 条」为 07-25 数, 一趟 stage 40 又长了 38 GB) — golden 跨-run 复现锚。⚠ 它是**混合库**: stage21 三家 LLM + llm_peer + **嵌入**(stage 15/25/26/27) 共库靠 key 内 model_id 区分, 体积主体是嵌入向量 (单条 63–92 KB, 而 stage21 响应仅 0.8–1.1 KB) → ① 「N 条已缓存」**不是** stage21 的条数, 据此估覆盖率会高估; ② 删它会**同时**炸掉 stage21 确定性锚点与全部嵌入缓存 (后者重播种付费); ③ `freelist_count=0` (2026-07-28 复测, 07-25 为 3) 零碎片, **VACUUM 无收益**。三轨**真 miss = 0** 即可 `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 字节级复现。缓存键=`prompt_version='v8-2026-05-17'`/`temperature=0.0`; prompt SSOT=`tone_llms.iter_article_track_prompts`。验证: `python -m news_process.scripts.audit.verify_stage21_cache_coverage`。
- 🔑 **「真 miss」口径 (2026-08-02 用户裁定, D1「仅 permanent」弃票登记表落地后生效; 旧载「0 miss 即可离线复现」+「0 miss 概率上不可达 ⟹ 离线必 hard-fail 崩溃」两句**均已作废**)**: 主缓存 miss 分两类 —— ① **真 miss** (登记表也无据) → 照旧 `raise LLMCacheMissError` **hard-fail**; ② **已登记永久弃票** (`llm_dropped_votes` 表有据) → 返 None 票 + loud WARNING **放行**。理由: 这类格模型**永久拒绝出票**, 在线路径对它们本来就是"返 None 票、退化为 2 票多数决", 离线照此放行才是对在线跑的**忠实**复现, hard-fail 反而做不到。故判据 = 「真 miss=0 且全部 miss 在登记表有据可查 ⟺ 离线 $0 复现」。
- **登记从严 (勿放宽)**: 只登记已证实的**永久型**失败 —— `http_permanent` (不可重试 HTTP, 典型 DeepSeek 400 `Content Exists Risk` 内容风控) 与 `empty_response` (**每一次**尝试都返空/不可解析, 且尝试数 ≥ `tone_llms._PERMANENT_EMPTY_MIN_ATTEMPTS`=5)。超时/5xx/网络抖动等**瞬时**故障绝不登记 (掺一次即判瞬时), 离线遇之仍 hard-fail 提醒回填。地板值与 `max_retries` **刻意解耦** (否则把 max_retries 调到 1 就能把偶发失败洗成"永久")。SSOT=`core/caching.py::LLMCache.{get,put}_dropped_vote` + `tone_llms.fetch_llm_async`; gate=`test_llm_dropped_votes_registry.py` (11 项)。⚠ 只 `CREATE TABLE` 新表, **严禁**对 137 GB 的 `llm_cache` 主表 `ALTER`/`CREATE INDEX`。主缓存"只装通过 `_is_cacheable_llm_response` 的好响应"零妥协 —— 登记表**不是**缓存, 不参与任何在线命中路径。
- **缺口回填入口**: `python -m news_process.scripts.audit.backfill_stage21_cache_misses --execute` (只对 miss 格调 API, **一条既有条目都不覆写**; 已登记的永久弃票格默认跳过, `--rows` 可跳过 218 万次全量扫描定向重试)。⚠ **勿**用「在线跑整个 stage 21」来回填 —— 在线模式会启用平局重试 (`force_refresh=True` 绕缓存重调 + `INSERT OR REPLACE` **覆写**既有条目), 为补 0.005% 的缺口而让 99.99% 已冻结的确定性锚点面临覆写风险。
- 📌 **2026-08-02 生产实测基线**: 242,000 行 × 3 模型 × 3 轨 = 2,178,000 格, 首验 120 miss (hit_rate=0.999945; gemini31 117 / deepseekv4 3 / gpt54nano **0**) → 定向回填补齐 **116**, 余 **4 格物理不可回填**并登记: `deepseekv4 × 行 50816 × 三轨` (400 内容风控, 秒回) + `gemini31 × 行 109994 × full` (连续 30 次稳定返空)。miss 呈"随机散落单格、同一 (行,轨) 只一个模型"形态 —— 若见成片整行三家全 miss, 那是**语料/prompt 漂移**而非弃票, 别混判。⚠ 嵌入族**亦受** `NEWS_PROCESS_LLM_OFFLINE` 守卫 (`embedding_engine.py` miss→raise `RuntimeError`); 仅在线 miss 才付费。
- **冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1`。
- 🔒 **人工标注成果冻结 (2026-10-12 用户裁定, 严禁修改/删除/重生)**: 13 份专家盲表 + 6 份仲裁表 (任务一 61 / 三轨窗口情感 09_sentiment_verify / stage13 漏检审计 / 创新三维 manual_validation) 已回收, sha256 冻结清单 = `config/validation.yaml::human_annotation_frozen` (流水线原件 + `data/processed/human_samples_blind/` 回收副本同受保护); 校验 = `python news_process/scripts/audit/verify_human_annotation_frozen.py [--root 备份]`; 异盘备份 `D:/E:\人工标注备份_news_process\20261012`。⚠ 均在 gitignore 的 `data/processed/` 下, 不入库。守卫: stage 61/64 检出人工标注即跳过重生 (正常结束), 两个 migrate 抽样脚本拒绝覆写; **绝不**传 `--force-regenerate`。读取/合并/回读 (merge、readback、stage 63/64、`python -m news_process.validation.human_annotation_ci`) 只写派生文件, 允许。协议偏离与结果登记见 `scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md` §8。
- **golden 重生仍须过 M0 审批门** (付费不可逆), 但「DEFERRED 到生产语料机」的前提已消失 —— ⚠ 2026-08-01 订正: 旧载「本机 data/raw 空、T=2」**双重失实**: ① 原始语料就在本机 `news_process/data_excel/` (**183 个 xlsx**, 即 18,198,978 条普查全量的源文件; 路径不叫 `data/raw`, 该目录根本不存在); ② 本机盘上面板自 2026-07-27/28 起即 **T=19** (见下条 Disk 状态), 不是 T=2。本机**就是**生产语料机。重生须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1 (`MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1`)。BLAS-FP 非确定网络列 (9 个): `bank_clustering`/`bank_cfbetween_cent`/`bank_harmonic_cent` × {无后缀,_win1,_sent} → 验零漂移须按全名 drop 排除 (`diff_golden.py` 的 `_KNOWN_BLAS_RE` 子串匹配自动覆盖)。换模/改测度类改动 golden 零字节安全须受控全量重生; manuscript 须披露 Google→Qwen 与 full-only 数值副作用 (`n_articles`/`fintech_share`/`attention_pct` 收缩, 非 bug)。
- **本机验证套路**: 改测度类改动本机不动 parquet → 用 baseline-stash A/B 差分证「0 新增失败」(committed golden 本就陈旧, 差分口径下不新增红灯)。⚠ 该套路的旧理由「T=2 dev 盘小、红灯不敏感」已作废 —— 本机盘上是 T=19 生产面板, 陈旧的是 **golden 快照本身**而非盘面规模。
- **Disk 状态 (2026-07-28 实读订正; 此前载「172 行 / 86 banks × 2 years / T=2 dev / 最宽 dta≈3453 列 / bank_list 全量=110 家」**已全部作废**)**: 盘上 `40_panel_yearly.parquet` = **23,693 行 × 4,183 列**, 覆盖 **1,247 banks × 19 years (2007–2025)** —— 即 2026-07-27/28 那次 28.12h 生产全链跑通的产物, **不再是 T=2 试跑面板**。三个 dta: 40/46 号各 23,693×4,183, **51 号 23,693×4,194 (最宽)**。`config/bank_list.yaml::banks` = **1,767 家** (与 `config/bank_addresses.json` 同量级, 后者 1,767 家/99.89% 落真实 NFRA 类型组)。⚠ 列数随重生漂移, 一律**实读**, 勿「旧基数+增量」心算。⚠ 三个 dta 当前 `notes=0` (Stata notes 重放尚未执行)。🔴 **2026-08-01 起该重放被显式阻塞**: 待重放的载荷 `data/processed/apply_notes_part01..07.do` + 3 个 master + `apply_notes_manifest.json` 是**生成期快照**且已被本次清扫**就地半改**(2026-08-01 实测: 三类陈旧标记均仍大量残留 (数量级 10^3; 该目录被 gitignore、随清扫脚本再跑会漂, 具体值以重放前实测为准)) —— 该目录被 `.gitignore:113 news_process/data/processed/**` 覆盖故不入库, 但盘上确已处于**半改状态**: 既非原始快照、也非按新 SSOT 重生的产物。现在重放会把这份半改载荷灌进交付 `.dta`。解阻塞顺序: ① `config/codebook_longdesc/*.md` 残留已清 (本次已做) → ② 待当前生产全链跑完后重跑 `python -m news_process.scripts.generate_codebook` 重生 `build/codebook/variable_codebook.{md,json}` (⚠ 该入口曾被 F156 家族 final-lint 的「人工区禁 markdown 粗体」硬闸拦死 —— 2026-07-29 commit `0128984c` 的 S10b 订正在人工区写了 10 个 `**`, 使 `load_library` 直接 `SystemExit`; **2026-08-01 已去除粗体标记并实测 `load_library` 通过**。⚠ 该硬闸至今无测试覆盖, 建议补一条 fast gate: 对真实 `config/codebook_longdesc` 跑 `load_library` 断言不抛 SystemExit) → ③ 由 `pipeline/panel/stata_export.py` 重生 apply_notes 载荷 → ④ 才可重放。真实全量 (目标语料) = **18,198,978 条 / 2007–2025 / T=19** (2026-07-16 裁定: 目标语料=普查全量); 面板 23,693 格中仅 **6,224 格** `n_articles>0` (73.73% 为笛卡尔补全的零报道格)。
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
├── data_excel/ # 原始 Excel 输入 (SSOT: config/paths.yaml::paths.raw_data_dir)
├── data/       # processed/*.parquet 输出 (⚠ 无 raw/ 子目录, 见上文 golden 条订正)
├── tests/      # 全量 sweep ≈2581 passed / 3 skipped
└── NN_*.py     # 35 thin shims (≤30 行); 32 注册 (16+16); 3 不注册: 80/81/82
```
**Key invariant**: `NN_*.py` 是 thin shim, 逻辑全在 `pipeline.*`/`validation.*`。**绝不**往 shim 加业务逻辑。

**Single Sources of Truth**:
1. DAG: `core/dag.py::STAGES_MAIN`/`STAGES_VALIDATION`
2. Output registry: `core/schemas.py::OUTPUT_REGISTRY`
3. Config: `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. Dependencies: `pyproject.toml::[project].dependencies` (requirements.txt 是 fallback)

**Data Flow**: `data_excel/*.xlsx` (⚠ 不是 `data/raw/`, 该目录不存在) → `data/processed/NN_*.parquet` (每阶段一个) → `40_panel_yearly.parquet` (银行-年面板); 日志 `logs/<stage>.log` (扁平, 每阶段一文件, 每次运行覆盖)。
⚠ **该约定有且仅有 2 个例外** (32 个注册阶段普查, 2026-07-29 实测; gate=`test_stage_log_filename_mapping.py` 冻结): `40_panel_export_main.py` → **`logs/40_build_panel.log`**; `62_dedup_threshold_sensitivity.py` → **`logs/62_dedup_sensitivity.log`**。二者的 `STAGE_NAME` 是刻意保留的 (`encode.py:47` 明写「保留原名」; `test_subprocess_log_isolation.py` 有 6 处按 `40_build_panel` 做命名空间断言), **勿改名**。
🔴 **踩坑形态**: 按约定 `tail logs/40_panel_export_main.log` 得到的是**空**, 因为该文件根本不存在 —— 而「文件不存在」与「阶段一个字没写」在终端上**长得一模一样**, 极易误判成卡死 (2026-07-29 实弹, 差点把正常跑着的阶段 62 判成疑似挂起)。查日志前先 `ls logs/NN_*` 确认真实文件名。

## Development Commands
```bash
# 环境 (Windows PowerShell venv; 解释器走 conda base python 3.13)
python -m venv venv && venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp news_process/.env.example news_process/.env   # 填 OPENLUX_API_KEY / DEEPSEEK_API_KEY / SILICONFLOW_API_KEY
pre-commit install

# 跑 pipeline —— ⚠ 2026-07-28 订正: 旧载「从 repo 根 …\data_antigravity_project\ 跑
#   `python run_pipeline_function.py`」是**错的**: git 根 = f:\WiseSearch\data_antigravity_project,
#   而 9 个入口脚本**全部在 news_process\ 下**, 在根目录按裸文件名跑 = 文件不存在,
#   python 立刻退出; 若启动时没重定向 stderr 就**连报错都看不到**, 只表现为"跑了很久
#   什么也没发生"(2026-07-28 实弹, 白等一小时)。两种写法都对, 二选一:
cd news_process && python run_pipeline_validation.py     # ① 进目录跑 (推荐)
python news_process/run_pipeline_function.py             # ② 从 repo 根带包路径跑
#   (脚本自身 bootstrap sys.path — `_PROJECT_PARENT` 插入 sys.path — 故 cwd 任意,
#    唯一要求是**脚本路径本身正确**。)
python news_process/21_tone_llms.py                      # 单阶段调试 (同理)
# ⚠ 后台启动务必带 stdout/stderr 重定向, 否则路径错/import 错会静默消失:
#   Start-Process ... -RedirectStandardOutput a.out -RedirectStandardError a.err

# 测试 (必须从 repo 根跑, 否则绕过 pyproject testpaths)
pytest                    # 全量
pytest -m fast            # 快测 (~30s, commit 前)
pytest -m integration     # 集成 (~5min)
pytest -k "test_golden"

ruff check . ; ruff check --fix .

# Golden 重生 (列 schema 变更后) —— 路径同样相对 news_process/, 与上面的入口同理
cd news_process && python scripts/migrate/generate_golden_snapshot.py
pytest news_process/tests/integration/test_panel_reproducibility.py   # 从 repo 根跑
```

## Critical Constraints

### Git Commit Protocol
1. **绝不 amend** (除非显式要求); pre-commit hook 失败后创建**新** commit。
2. **按文件名 stage** (`git add <file>`), 避免 `git add .`/`-A` (防误提 secrets); 共享树并发会话尤须 by-name (排除 `*constants.json`/`eval_reports` 等并发产物)。
3. Commit message: HEREDOC + `Co-Authored-By: <当前实际模型> <noreply@anthropic.com>` trailer。⚠ 2026-07-28 订正: 原文把型号写死为 `Claude Opus 4.8 (1M context)` —— 那是写这行时的模型, 照抄会造成**错误署名**。trailer 必须写**本次真正执行的模型**(本轮为 `Claude Opus 5`), 历史 commit 里的 4.8 是当时的事实, 不追改。
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
- `OPENLUX_API_KEY`: stage 21 (gpt54nano/gemini31) + 若干 LLM 验证阶段 (66/70) + `_lg`/OpenLux 嵌入。
- `DEEPSEEK_API_KEY`: stage 21 第三家 `deepseek-v4-flash` (直连 api.deepseek.com)。离线命中不需; 生产首跑/播种须填。
- `SILICONFLOW_API_KEY`: canonical Qwen 嵌入轨。
- `EMBEDDING_API_KEY`: 默认 `${OPENLUX_API_KEY}` (可覆盖独立端点)。
- `OPENLUX_FULL_KEY`: **仅** `LLMs_for_FinTech_dic/` 独立管道读 (`config.py::API_KEY`); 端点由 `OPENLUX_BASE_URL` 覆盖, 默认 `https://api.openlux.ai/v1`。本机与 `OPENLUX_API_KEY` 同值但**是两个独立变量**, 改 key 须同改两处。
- `FINBERT2_MODEL_DIR`: 可选本地 BERT (stage 23 缺失时优雅跳过)。
- ⚠ `LLMs_for_FinTech_dic/` 独立管道用**独立开关 `LLMS_DIC_OFFLINE`** (`NEWS_PROCESS_LLM_OFFLINE` 对其无效)。
- ⚠ 裸环境嵌入 SSL 报错 → 设 `SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")`; 重跑 stage 23 BERT 设 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`。

## Multi-Paper Support
`papers/` 含 11 个模块 (8 fully-coded + 3 provisional), 全部具备 `analysis.py`/`figures.py`/`tables.py`, 纳入 `paper_registry.PAPER_IDS_ALL`。
- **P1–P5 主线** (`bank_fintech_*`): tone (P1) / attention (P2) / substance (P3) / locus (P4) / collab (P5, prov)。
- **衍生/prov**: `benefit_society` · `brokerage_network` · `llm_peer` · `strategic_diff` · `bank_media_disagreement` (prov) · `bank_news_clarity` (prov)。
- **treatment vs outcome 是两套**: 主轨 treatment 多为 `*_full` (P1=`llm_vote_tone_full`); outcome/DV 另定 (P1 `funding_cost` / P2 `ln_fintech_investment` / P3 `cost_income_ratio_change_3yr` / P4 `citation_weighted_patent` / P5 `m_and_a_fintech` / benefit&brokerage&llm_peer `roa` (llm_peer 2026-06-14 PORT SAL-3 起主 outcome=roa, `avg_ft_intensity_full` 降为 first-stage 机制佐证) / strategic_diff `tobin_q` / prov `z_score`), 多为外部财务哨兵列。详见 memory `outcome-redesign-2026-06-13`。
- 公用工具 `papers/_common/` (含 `AI_DISCLOSURE_TEMPLATES.md` 6 系列)。
> 注: paper ID `P1..P5` 是 portfolio 本地编号, 与其它文档/计划的 `P1/P2/..` 步骤编号是两个独立空间。

## Stata Environment
**本机 StataNow/MP 19.5** (`C:\Program Files\StataNow19\StataMP-64.exe`, **许可 64 核但机器只有 32 逻辑线程**, 128GB)。**策略: Stata 19+ only, 无需向下兼容**。
⚠ 2026-07-29 实测订正: 原文写「64-core」是把**许可数**当成了机器核数。CPU = i9-13900K = **24 物理核 (8 P + 16 E) / 32 逻辑线程**; `c(processors_lic)=64` 而 `c(processors)=32` (被物理线程数封顶)。`c(edition_real)=MP`/`c(MP)=1` 属实 (`c(flavor)` 回 `IC` 是 legacy 兼容常量, 别据此判版本)。

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
- MP 硬上限远未触顶 (maxvar 120,000 — 2026-07-29 实测确认: `set maxvar 120000` rc=0 且 `c(max_k_theory)` 随之变 120000)。**core/aux IC 双切分已退役** (单一全列 `.dta`) — **勿**在模板硬编码「前 N 列」截断。⚠ 2026-08-01 订正: 旧载「行数瓶颈在面板深度 (T=2)」已作废 —— 盘上面板 **23,693 行 = 1,247 家 × 19 年**, 行数早已不是瓶颈; 真正的紧迫项是**列数**距 paper master 默认 `maxvar 5000` 仅剩 ~806 列余量 (见下文「147 个 `.do.tmpl`」条的 `set maxvar` 待补)。
- 🔴 **绝不写 `set processors 64` —— 2026-07-29 实测 r(198) 报错**, 且在 `/b` 批处理 master 里会直接中断整条 battery。原文「本机自动拉满 (`set processors 64`)」双重失实: ① 本机上限是 **32** (许可 64 但物理只有 32 逻辑线程); ② 全仓 `.do`/`.tmpl`/`.py` **零处**写过 `set processors` (`grep` 计数 = 0), 所谓"自动拉满"从来不存在 —— Stata MP 本就默认吃满 `c(processors)=32`, 无需也不该显式设。若确需显式设, 上限写 `32` (实测 rc=0; 24 亦可)。`matsize` Stata 19 自动管理。
  ⚠ 关联教训: `72_construct_orthogonality.py` 旧 docstring 那句「n_jobs=16 → ~5 min on **64-core** MP machine」正是被同一处「64 核」误载带偏的, 而 DAG timeout=10800s 又照它设 —— 2026-07-29 阶段 72 被强杀、73/74/75 连坐跳过的根因链就从这里起头。凡涉及本机核数的估算, 一律实测 `c(processors)` / `NumberOfLogicalProcessors`, 勿引本文件旧数。
- **147 个 `.do.tmpl`** (`papers/_common/stata_templates/` rglob) = 主线 21 (含 `27_tableA12`/`28_tableA13`) + 8 个 paper 子目录 123 + 归档 3; prov 两篇另 15 不计入。头部分层 (2026-07-22 订正措辞): 完整四行头 (`version 19`+`clear all`+`set maxvar 32767`+`set linesize 120`) 仅根级 `00_master`; 8 个 paper master 为三行头 (`version 19`/`clear all`/`set more off`, 无 maxvar → 按默认 5000 跑, 而面板 **2026-07-28 实读已 4,183 列 / 51 号 4,194 列** (旧载 3453 作废) — 距默认 5000 仅剩 806 列余量, **补 `set maxvar` 已从「待决策」升为紧迫**); 子表仅 `version 19` (master 会话内共享状态, 刻意; 消费 `$bank_controls` 的根级模板刻意省略 `clear all`)。
- pyreadstat 写 `.dta` 用 **format version 118** (文件格式 spec 编号, ≠ Stata 应用版本; 勿与 `version 19` 混淆)。

## Known Issues & Workarounds
1. **Windows line endings**: Git 可能 warn CRLF (预期无害)。repo 根 `.gitattributes` 标 `*.parquet`/`*.xlsx`/`*.db` 为 binary; 源文件保持磁盘 EOL。
2. **FinBERT2 model**: stage 23 需私有微调模型; `FINBERT2_MODEL_DIR` 未设/无效时优雅跳过 (其余 BERT 照跑)。

## Phase History
项目历经 9 次重构 (v1.x → v2.1.0): package skeleton + DAG 单源 → 拆巨石 + OUTPUT_REGISTRY + acceptance gate → 多论文产品化 + 7-domain config 拆分 → 数据布局规范化 → 清理。v3.x 演进见 git history; 当前 HEAD baseline 见顶部 "Current version" + "当前状态铁律"。
