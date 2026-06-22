# news_process 流水线编号 .py 文件参考 (2026-06-15)

本文档汇编 `news_process/` 根目录下全部 35 个编号 `NN_*.py` 脚本的权威参考。这 35 个文件都是 **thin shim** (极薄转发脚本, 每个 ≤30 行): 真正的业务逻辑全部位于 `news_process.pipeline.*` 与 `news_process.validation.*` 子包中, shim 只做 `sys.path` 注入后导入并调用对应实现模块的入口函数。

其中 **32 个已在 DAG 注册** = 16 个 `STAGES_MAIN` (生产主链) + 16 个 `STAGES_VALIDATION` (验证支线); 另有 **3 个设计上未注册** (`27c_placebo_and_alt_anchor.py` / `52_stata_data_audit.py` / `53_export_stats_excel.py`): 它们刻意游离于编排器之外 —— `27c` 是 benefit_society 论文的 audit-only 旁支, `52`/`53` 是用户按需手动调用的 CLI 工具, `core/schemas.py:156-158` 显式注释排除 52/53。

每个文件小节给出: 一行元信息 (注册 / 底层模块 / 产出 / 三轨), 然后逐字引用定稿的 **详细功能说明** (技术细节) 与 **白话说明** (非技术解释)。

> ⚠ **行号说明 (post-12b)**: stage 12b StageSpec 块 (core/dag.py:187-191) 后续插入在 stage 12 与 stage 13 之间, 故本文档中 stage 13 及之后各小节引用的 `core/dag.py` / `pipeline/panel/runner.py` 源行号统一向后漂移 (dag.py 约 +8 行 / runner.py 约 +38 行), 与现行源码偏移。stage 00/11/12 (12b 之前) 行号不受影响。各小节的 StageSpec 名称、script 文件名、语义描述均仍正确, 仅行号待重生; 以现行源码实读为准。

---

## 总览表

| 文件 | 注册 | 底层模块 | 产出 | 三轨 |
|---|---|---|---|---|
| 00_preprocessing.py | STAGES_MAIN (阶段00) | pipeline/preprocess/runner.py | 00_preprocessing.parquet + 旁路对账 json/csv | 不适用 (三轨在 stage 13 物化) |
| 11_news_bank.py | STAGES_MAIN (阶段11) | pipeline/filtering/news_bank.py | 11_bank_news.parquet + .csv | 不适用 (firm-level 公共上游) |
| 12_news_fintech.py | STAGES_MAIN (阶段12) | pipeline/filtering/news_fintech.py | 12_fintech_news.parquet + 12_fintech_news_full.parquet | 不适用 (金科词典是 ss 轨金科侧词源) |
| 12b_cooccurrence_filter.py | STAGES_MAIN (阶段12b) | pipeline/filtering/cooccurrence_filter.py | 12b_cooccurrence_filtered.parquet | 不适用 (硬过滤丢行, 三轨天然继承) |
| 13_materialize_ctx.py | STAGES_MAIN (阶段13) | pipeline/text/ctx_materializer.py | 13_news_with_ctx.parquet (五列文本/旗标) | **三轨源头** (full/ctx/ss) |
| 14_fintech_intensity.py | STAGES_MAIN (阶段14) | pipeline/filtering/fintech_intensity.py | 14_fintech_intensity.parquet | 真三轨 |
| 15_article_policy_alignment.py | STAGES_MAIN (阶段15) | pipeline/filtering/policy_alignment.py | 15_article_alignment.parquet | 真三轨 + 双模型 twin |
| 18_article_staleness.py | STAGES_MAIN (阶段18) | pipeline/text/article_staleness.py | 18_article_staleness.parquet + 18_staleness_panel.parquet | surface 三轨 / semantic 两轨 (ss DEFER) |
| 21_tone_llms.py | STAGES_MAIN (阶段21) | pipeline/sentiment/tone_llms.py | 21_tone_llms.parquet + 21_tone_llms_full.parquet + _llm_cache.db | 真三轨 |
| 22_tone_words.py | STAGES_MAIN (阶段22) | pipeline/sentiment/tone_words.py | 22_words_tone.parquet + 22_idf_weights.json | 三轨 |
| 23_tone_berts.py | STAGES_MAIN (阶段23) | pipeline/sentiment/tone_berts.py | 23_bert_tone.parquet | 三轨 (优雅降级) |
| 24_herd_decay_processor.py | STAGES_MAIN (阶段24) | pipeline/sentiment/herd_decay.py | 24_herd_decay.parquet + 阈值敏感性 csv | 三轨 |
| 27c_placebo_and_alt_anchor.py | 未注册 (audit-only) | pipeline/features/benefit_society_audit_combined.py | 27c_alt_anchor_and_placebo_panel.parquet + sidecar.json | 三轨 (twin 列扩展) |
| 30a_article_sbert.py | STAGES_MAIN (阶段30a) | pipeline/text/article_sbert.py | 30a_article_embeddings.parquet (无 config key) | 嵌入轴 full/ctx 两路 (ss DEFER) |
| 31_bank_fintech_threshold.py | STAGES_VALIDATION (阶段31) | validation/threshold.py | eval_reports 下 5 个 csv/png/tex | 不适用 |
| 32_news_llms_human.py | STAGES_VALIDATION (阶段32) | validation/llms_human.py | 32_human_samples.xlsx (+ _merged) | 不适用 (track-agnostic) |
| 32a_dedup_threshold_sensitivity.py | STAGES_VALIDATION (阶段32a) | validation/dedup_threshold.py | dedup_sensitivity_report.csv | 不适用 |
| 33_news_llms_evaluation.py | STAGES_VALIDATION (阶段33) | validation/llms_evaluation.py | eval_reports 下 json/tex/csv/png | 三轨全覆盖 |
| 34_tone_validation.py | STAGES_VALIDATION (阶段34) | validation/tone_validation.py | 每轨 json/tex/csv/xlsx + 回读 csv | 三轨全覆盖 (主控制流) |
| 35_radius_sensitivity.py | STAGES_VALIDATION (阶段35) | validation/radius_sensitivity.py | 35_radius_sensitivity.json/tex/png | 半成品多轨 (track-agnostic) |
| 36_entity_masking_test.py | STAGES_VALIDATION (阶段36) | validation/entity_masking.py | eval_reports 下 json/csv/tex/png | 完整三轨 |
| 37_dict_coverage_audit.py | STAGES_VALIDATION (阶段37) | validation/dict_coverage.py | eval_reports 下 4 个 csv | 不适用 |
| 38_media_diversity.py | STAGES_VALIDATION (阶段38) | validation/media_diversity.py | 38_media_diversity.xlsx (12 Sheet) | 不适用 |
| 38b_decay_sensitivity.py | STAGES_VALIDATION (阶段38b) | validation/decay_sensitivity.py | 38b_decay_sensitivity.csv | 半成品多轨 (track-agnostic) |
| 39_prompt_sensitivity.py | STAGES_VALIDATION (阶段39) | validation/prompt_sensitivity.py | validation/eval_reports 下 json/csv/tex/png | 完整三轨 |
| 39a_inter_track_kappa.py | STAGES_VALIDATION (阶段39a) | pipeline/audit/inter_track_kappa.py | inter_track_kappa_table.csv/.tex | 三轨核心阶段 |
| 39c_construct_orthogonality.py | STAGES_VALIDATION (阶段39c) | pipeline/audit/construct_orthogonality.py | 7 件 parquet/json | 三轨各出 NMI 矩阵 |
| 39d_lexical_discriminant_validity.py | STAGES_VALIDATION (阶段39d) | pipeline/audit/lexical_discriminant_validity.py | 39d_*.parquet + 39d_htmt_matrix.json | 三轨各跑判别效度 |
| 39e_lm_discriminant_validity.py | STAGES_VALIDATION (阶段39e) | pipeline/audit/lm_discriminant_validity.py | eval_reports 下 csv (无 parquet) | 三轨各跑一次 |
| 39f_cross_media_alpha.py | STAGES_VALIDATION (阶段39f) | pipeline/audit/cross_media_alpha.py | 39f_cross_media_alpha.parquet | 三轨各算一次 (panel +9 列) |
| 45_panel_export_main.py | STAGES_MAIN (阶段45) | pipeline/panel/runner.py | 40_panel_yearly + 40_article_bank_level + 三级 attn + .dta/.csv | 三轨核心承载阶段 |
| 46_stata_export.py | STAGES_MAIN (阶段46) | pipeline/panel/stata_export.py | 46_panel_yearly_full.dta + labels.do + codebook.xlsx | 三轨透传 |
| 51_falsification_test.py | STAGES_MAIN (阶段51) | pipeline/falsification/controls.py | 51_panel_with_controls.parquet + .dta + 诊断 csv | 三轨在诊断层体现 |
| 52_stata_data_audit.py | 未注册 (user-CLI) | pipeline/audit/stata_audit.py | 52_stata_data_audit.csv + log | 三轨体现于检查项 |
| 53_export_stats_excel.py | 未注册 (user-CLI) | pipeline/audit/stats_excel.py | 各阶段_媒体_地区_城市_统计.xlsx | 不适用 |

---

### 00_preprocessing.py

- **注册**: STAGES_MAIN(阶段00: 数据预处理)。core/dag.py:166-171 注册 StageSpec(name="阶段00: 数据预处理", script="00_preprocessing.py", group="main", kind="preprocess", timeout=10000); core/schemas.py:45 在 OUTPUT_REGISTRY 声明产出 00_preprocessing.parquet。非 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: pipeline/preprocess/runner.py (入口 main; 核心编排 load_and_process_data; 真正处理逻辑分散在 sibling 子模块 _constants/load/normalize/filter/dedup)
- **产出**: 主产物 data/processed/00_preprocessing.parquet (Snappy 压缩, row_group_size=100_000, use_dictionary=True, write_statistics=True — main() 末次写盘参数)。旁路产物: ① data/processed/source_reconciliation.json (degradation F7 源对账, 字段含 n_found / n_contributed / n_zero_contribution / total_rows / failed_files / zero_contribution_files / per_source_rows); ② 同名 .csv 预览 (safe_save_preview_csv, 前 5000 行, core/reporting.py:33); ③ data/processed/_cache/<源名>.parquet 逐源增量缓存 (schema metadata 内嵌 config_hash); ④ data/processed/media_weight_coverage.json (仅当存在未匹配媒体时由 dedup 写出, fail-soft 旁路)。
- **三轨**: 不适用 — 三轨文本列 (content_full/ctx/ss) 在 stage 13 才物化。本阶段只产出统一清洗后的原始 '内容'/'标题' 等列, 是三轨共同的语料底座。

**详细功能说明**

**输入**: `config paths.raw_data_dir` 目录下全部 `*.xlsx` (生产规模 ~176 文件 / ~37GB / ~1700 万条媒体报道; 数字取自 runner.py 模块 docstring 与 main() 日志)。无上游 parquet, 是 DAG 的根阶段。

**处理步骤** (`runner.main` → `load_and_process_data` → 媒体名兜底映射 → `ArticleDeduplicator.run`):
1. `glob` 扫描 XLSX 列表; 对每个源文件检查增量缓存 (`_cache/*.parquet`): 缓存有效需同时满足 缓存文件存在 ∧ 缓存 mtime 晚于源 XLSX ∧ schema metadata 的 `config_hash` 与当前一致 (runner.py:208-214); 任一不满足则入待处理列表。
2. 未命中文件经 `ProcessPoolExecutor` 并行调用 `load._process_single_file` (worker 数 `num_workers = PARAMS.get('num_workers', min(cpu_count, 32))` — 配置缺省时取 min(cpu_count, 32), 配置存在时直接用配置值)。单文件内: calamine 加载 → `filter._clean_and_filter_dataframe` 的 **8 步初步过滤** (地域 / 媒体类型 / 媒体名称黑名单 / 缺失值 / 广告 / 银行关键词保留 / Schema 统一 / 媒体名清理) → 文本标准化 (`normalize.clean_text_batch`: 编码修复/OpenCC 繁简/全角半角/HTML 清洗/噪声去除) → 长度过滤 (标题汉字数 ≥2, 内容汉字数 100~10000)。worker 内异常 catch→return None (整源丢失, 但落入零贡献对账)。
3. 处理结果以 `pq.ParquetWriter` 流式追加写主 parquet, 同时写逐源缓存 (缓存 schema metadata 写入 config_hash)。
4. 全量读回后做媒体名全局映射兜底 (`MEDIA_NAME_OVERRIDES`), 再执行去重。

**关键算法/公式**:
- **Aho-Corasick 自动机** (load.py): O(n) 一次线性扫描多模式匹配, 用于第 6 步银行关键词保留过滤 (复杂度从 O(文本×词数) 降到 O(文本)); 自动机注入繁体 (OpenCC s2t) + 全角括号变体以兼容规范化前原文 (fix omni-g-preprocess-07)。
- **精确去重** (dedup.py): 基于 标题+内容 字符串完全匹配, 排序键 [日期↑, 媒体权重↓, docid↑, 内容长度↓], 保留首发 (日期为第一排序键, 媒体权重仅同日 tiebreak; fix omni-g-preprocess-06)。
- **近似去重 (MinHash LSH, Broder 1997)**: 默认 128 个置换函数 (Jaccard 估计 std ≈ 1/√128 ≈ 8.8%), 字符级 3-gram 作特征, `datasketch.MinHashLSH(threshold, num_perm)` banding 分桶; 簇内按 [日期↑, 权重↓, docid↑] 排序, **5 工作日时间窗** (`np.busday_count`) 内的后发相似稿 (Jaccard ≥ 0.8) 判为转载删除。生产阈值 0.8 来自 config; 0.85 仅 config 缺失时的保守 fallback (有效阈值实测略偏保守 ~0.82, 见 memory dedup-banding-n4)。

**输出列**: 不新增分析列, 产出统一 schema 的清洗后语料 (含 内容/标题/媒体/版面/页号/作者/日期 等)。写 `00_preprocessing.parquet`。

**外部依赖/缓存/确定性**: 纯 CPU (calamine/pyarrow/multiprocessing/datasketch/ahocorasick), 不调任何 LLM/Embedding/BERT, 无网络。`timeout=10000` 秒 (dag.py:170, 高于 StageSpec 默认 7200, 因全量加载 37GB)。**增量缓存键 (`compute_preprocess_cache_key`) = SHA-256(preprocessing 段 + normalization 段 + noise_patterns.json 内容 sha256 + bank_keywords.json 内容 sha256 + PREPROCESS_CODE_VERSION)** (omni-g-preprocess-04: 资源文件内容入哈希, 改词典后缓存自动失效; 资源缺失以 `missing:<文件名>` 哨兵入哈希)。`NEWS_PROCESS_STRICT_SOURCES=1` 可在有失败/零贡献源时 fail-loud。

**DAG 位置**: STAGES_MAIN 首阶段, 下游 11/12/13… 全部依赖其 parquet。

**白话说明**

**这一步在做什么**: 把上百个原始 Excel 表格 (上千万条新闻) 倒进一台'洗衣机+分拣机', 统一格式、修乱码、繁体转简体、去掉广告和网页噪声, 再把'同一篇新闻被多家媒体转载'的重复稿件删到只剩最早那一份。打个比方: 原始数据像一堆来自不同报社、字体大小不一、还夹着传单的剪报, 这步把它们裁齐、去重、装订成一本干净的剪报册。

**为什么需要它**: 后面所有分析都建立在这本'干净剪报册'上。如果不去重, 同一条新闻被 50 家媒体转载就会被当成 50 条独立证据, 银行的'媒体关注度'会被严重虚高; 如果不规范化, 繁简体和乱码会让后面的关键词匹配漏判。它是整条流水线的地基。

**做得好不好的影响**: 去重门槛 (5 个工作日内、相似度 0.8) 直接决定每家银行每年被算成'多少篇独立报道'——这是银行-年度面板里注意力、情感等核心指标的分母。删多了会丢掉真实报道、删少了会把转载灌水进面板, 两种都会让回归系数偏掉, 影响论文结论的可信度。它还会输出一份'源文件对账单', 万一某个 Excel 整个读取失败、悄悄从面板里消失, 审稿人能查得到。

---

### 11_news_bank.py

- **注册**: STAGES_MAIN(阶段11: 银行新闻判断)。core/dag.py:174-178 注册 StageSpec(name="阶段11: 银行新闻判断", script="11_news_bank.py", group="main", kind="filter"); core/schemas.py:47 声明产出 11_bank_news.parquet。非 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: pipeline/filtering/news_bank.py (入口 main; 单篇判定/AC 匹配/假阳性排除委托至 core/text/ahocorasick.py::analyze_bank_matches + load_bank_names + load_exclusion_patterns)
- **产出**: data/processed/11_bank_news.parquet (paths.yaml::filenames.output_11_bank_news = 11_bank_news.parquet) + 同名 .csv 预览。写盘经 save_parquet_with_metadata, 血缘 input_files = [00_preprocessing.parquet, bank_names.json, bank_name_exclusions.json] (S10/B 修复: 词典内容纳入 input_hashes)。
- **三轨**: 不适用于 full/ctx/ss 情感三轨 (那在 stage 13/21+ 才分轨)。但本阶段产出 target_bank_in_title 与 mention_density 等 firm-level 暴露信号, 是三轨情感的公共上游 (决定哪些 firm-document 行进入后续轨)。

**详细功能说明**

**输入**: `00_preprocessing.parquet` (config 键 output_00_preprocessing) 的 内容/标题/版面/页号/作者 等列。

**处理步骤** (`main` → joblib `Parallel` 分批 → `classify_batch` → 委托 `core.text.ahocorasick.analyze_bank_matches`):
1. 按 `parallel.batch_size` (默认 5000) 切批, `n_jobs` 默认满核-1 (psutil), joblib 并行。
2. 每篇文章按 `split_ratio` (默认 0.5) 把'内容'按字符数等分上下两半; 用全局 Aho-Corasick 自动机一次线性扫描所有银行别名 (`load_bank_names` → BANKS/BANK_AC_AUTOMATON/VARIANT_TO_BANK)。
3. **firm-document 展开**: 一篇可同时命中多家银行 → 每家合格银行生成一条独立物理行 (故输出行数可多于输入)。

**关键算法/判定公式** (`analyze_bank_matches`, 每家银行; classify_batch:209-214 复用同一阈值):
- 前置: 任一别名 总计 (含标题, `total_with_title`) ≥ `MIN_NAME_OCCURRENCES` (默认 2);
- 分布条件 (满足其一): (a) 上半 ≥ `MIN_UPPER` (默认 1) ∧ 下半 ≥ `MIN_LOWER` (默认 1); 或 (b) 别名出现在标题 ∧ 全文合计 `total_count` ≥ `MIN_UPPER`。
- **不对称口径的假阳性排除**: ① 否定模式排除 ('务农行列''交通行业'命中'农行' → 排除, NEGATION_AC); ② 短名歧义消解 (≤2 字简称如'工行''中行', 检查前后 context_window 字符, 命中排除词则剔除该次匹配)。这套排除规则与 stage 13 ctx/ss 锚定共用同一事实源 (core/text/ahocorasick)。

**输出列** (合格行追加 9 列): `is_bank_news`, `target_bank`, `co_mentioned_banks`, `target_bank_in_title` (int 0/1, 显著性/β 信号, 刻意保留非情感轨), `matched_banks_info` (json), `matched_bank_names`, `doc_length`, `target_bank_mention_count`, `mention_density` (= total_count / max(len(str(内容)),1), 即 提及次数/文档字符数, value-weighted exposure)。另经 `compute_news_salience` 追加 NEWS_SALIENCE_KEYS (版位/导语命中 target_in_lead/署名 has_byline 等, 用全部别名 + 同款否定/短名排除)。
注: classify_batch 内某批次无任何银行新闻时, 空回退 DataFrame 仍含全部 9 列 + NEWS_SALIENCE_KEYS (news_bank.py:270-274); 仅当**全部批次**均无银行新闻时, main() 最终回退到只含 is_bank_news/matched_banks_info 两列的空 DataFrame (news_bank.py:461-463)。

**外部依赖/确定性**: 纯 CPU (ahocorasick / joblib / psutil), 无 LLM/Embedding/网络。确定性: 给定语料+词典逐位可复现。词典文件纳入 parquet 血缘 input_hashes (防词典内容篡改而路径不变导致完整性校验失明)。

**DAG 位置**: 上游 stage 00, 下游 stage 12 (金科判定) 读其输出。学术依据 Hassan 2019 QJE (firm-level exposure) + Gentzkow-Kelly-Taddy 2019 JEL (Text as Data; 见模块 docstring)。

**白话说明**

**这一步在做什么**: 从全部新闻里挑出'真的在讲某家银行'的那些, 并标注是哪家银行。打个比方: 像图书管理员把一摞剪报里凡是讲'工商银行''建设银行'的挑出来, 还在每篇上贴标签写明主角是谁; 如果一篇同时认真讲了工行和建行, 就复印成两份各自归档 (这就是'按银行展开成独立行')。

**为什么需要它**: 后面研究的是'每家银行每年的媒体形象', 所以必须先确定每篇新闻属于哪家银行。难点在于中文简称会误伤——'农行'可能其实是'务农行列', '中行'可能是'居中行驶'。这步特意加了两道'防误判'闸门 (否定短语排除 + 短名前后文检查), 还要求银行名在文章上半段和下半段都出现 (说明是主角而非一笔带过), 才算数。

**做得好不好的影响**: 这步决定了每家银行'有多少篇新闻'——这是整个银行-年度面板的样本来源。挑太松会把不相关的稿件算进某家银行 (污染情感、注意力指标, 系数失真); 挑太严会漏掉真实报道 (样本变小、估计不稳)。它顺手算的'提及密度''是否上标题'还会被后面用作加权和稳健性信号, 影响主回归与显著性。

---

### 12_news_fintech.py

- **注册**: STAGES_MAIN(阶段12: 金融科技新闻判断 + 全量分类结果)。core/dag.py:179-183 注册 StageSpec(name="阶段12: 金融科技新闻判断 + 全量分类结果", script="12_news_fintech.py", group="main", kind="filter"); core/schemas.py:48-51 声明双产出 12_fintech_news.parquet + 12_fintech_news_full.parquet。非 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: pipeline/filtering/news_fintech.py (入口 main; 单篇判定委托至 core/text/ahocorasick.py::analyze_fintech_matches + load_fintech_dict)
- **产出**: 两个 parquet: ① data/processed/12_fintech_news.parquet (config 键 output_12_fintech_news, 仅 is_fintech_news==True 的子集); ② data/processed/12_fintech_news_full.parquet (键 output_12_fintech_full, 过滤前全量 = 全部 stage 11 银行新闻 + 金科分类列)。各配 .csv 预览。两者写盘均经 save_parquet_with_metadata, 血缘含 fintech_dict.json (1506 词)。注: 模块 docstring (line 32/35) 仍写旧名 '11_news_fintech.parquet'/'12_news_fintech_full.parquet', 与实际不符, 但写盘路径走 config 键 → 以 paths.yaml 实名为准 (input=11_bank_news.parquet / full=12_fintech_news_full.parquet)。
- **三轨**: 不适用情感三轨。但本阶段的金科判定与金科词典 (fintech_dict.json, 实测 1506 词) 是 stage 13 ss 轨 (银行+金科同句共现) 的同款金科侧词源 (stage 13 经 load_fintech_dict 复用); fintech_in_title 信号刻意保留供下游。

**详细功能说明**

**输入**: `11_bank_news.parquet` (config 键 output_11_bank_news) 全列 + 内容/标题。

**处理步骤** (`main` → joblib `Parallel` 分批 → `classify_batch` → 委托 `analyze_fintech_matches`):
1. 同 stage 11 的分批/并行框架 (batch_size 默认 5000, n_jobs 满核-1)。
2. 每篇按 split_ratio (默认 0.5) 按字符数等分上下半; 用全局 Aho-Corasick (`load_fintech_dict`, 1506 词金科词典) 一次线性扫描。

**关键判定公式** (`analyze_fintech_matches`, 整篇判定——stage 12 **不再** firm-document 展开, 沿用 stage 11 已展开的行):
- 前置 (多样性): 标题或全文出现 ≥ `MIN_DISTINCT_KEYWORDS` (默认 2) 个**不同**金科词;
- 分布条件 (其一): (a) 全部词上半合计 ≥ `MIN_UPPER` (默认 1) ∧ 下半合计 ≥ `MIN_LOWER` (默认 1); 或 (b) 任一词在标题 ∧ 全文合计 ≥ `MIN_UPPER`。
- 金科侧为**裸 AC 匹配** (不做否定/短名排除), 与 stage 13 ss 轨'不对称口径'的金科侧一致 (单一事实源 core/text/ahocorasick)。

**输出列** (对每行追加 7 列): `is_fintech_news` (bool), `fintech_total_count`, `fintech_upper_count`, `fintech_lower_count`, `fintech_in_title` (供下游显著性, 刻意保留), `fintech_distinct_keywords`, `fintech_keyword_details` (json)。

**双产出语义**:
- `12_fintech_news_full.parquet`: 写在过滤**之前** (news_fintech.py:295-321), 含全部 stage 11 银行新闻行 (含非金科) + 上述 7 列, 与 stage 11 输出 1:1 行对应 (供人工验证抽样)。注: 任务简述'_full=过滤前全量银行新闻(与 11 1:1)'成立——它就是'银行新闻全集 + 金科分类标记', 未做金科过滤。下游 controls.py 用其'减面板后去重'部分作 fintech_share 分母的一块 (见 memory fintech-share-denominator)。
- `12_fintech_news.parquet`: 对 full 做 `is_fintech_news==True` 过滤后的子集 (news_fintech.py:325), 即'既是银行新闻又是金科新闻'的稿件, 供 stage 13+ 三轨/强度/情感消费。

**外部依赖/确定性**: 纯 CPU (ahocorasick/joblib/psutil), 无 LLM/网络, 逐位可复现。fintech_dict.json 纳入两个 parquet 的 input_hashes 血缘 (防词典内容篡改失明)。

**DAG 位置**: 上游 stage 11, 下游 stage 13 (ctx_materializer) 读 12_fintech_news.parquet。学术依据 胡俊等 2024 中国管理科学 + Loughran-McDonald 2011 JF (见模块 docstring)。

**白话说明**

**这一步在做什么**: 在'已经是银行新闻'的稿件里, 再判断哪几篇是真的在谈'金融科技'(手机银行、移动支付、大数据风控、区块链这类)。它会输出两份: 一份是'银行新闻全集, 每篇都打上是不是金科的标记'(供抽查核对), 另一份是'确实是金科的那个子集'(交给后面用)。打个比方: 先有一摞银行剪报, 这步给每篇盖个章——'涉金融科技'或'不涉', 然后把盖章'涉'的单独抽出来一叠。

**为什么需要它**: 整个项目研究的是'媒体怎么报道银行与金融科技的关系', 所以必须先框定'银行×金科'这个话题范围。判定要求一篇里出现至少 2 个不同的金科词 (而不是偶然蹦一个), 避免把只顺嘴提一句'扫码支付'的普通银行新闻误算进来。

**做得好不好的影响**: 这步圈定的金科新闻子集, 是后面所有'银行金融科技注意力/态度/实质性'指标的原料。框太宽会把噪声稿件灌进来, 框太窄会漏掉真实的金科报道, 都会让银行-年度面板里的核心解释变量偏移。它保留的那份'全量+标记'还充当 fintech_share (银行新闻里金科占比) 指标的分母来源之一, 直接影响该比例型变量的口径; 同时它的金科词典就是后面'银行和金科出现在同一句'(第三条文本轨) 用来认定共现的金科词源。

---

### 12b_cooccurrence_filter.py

- **注册**: STAGES_MAIN(阶段12b: 银行×金科邻近共现预过滤 (Andreou et al. 2026))。core/dag.py:187-191 注册 StageSpec(name="阶段12b: 银行×金科邻近共现预过滤 (Andreou et al. 2026)", script="12b_cooccurrence_filter.py", group="main", kind="filter"); core/schemas.py:53 在 OUTPUT_REGISTRY 声明产出 12b_cooccurrence_filtered.parquet (config 键 output_12b_cooccurrence, 见 schemas.py:118)。v3.10.0 (2026-06-15) 引入。非 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: pipeline/filtering/cooccurrence_filter.py (入口 main → filter_cooccurrence; 判据原语 core/text/entity_context.py::has_bank_fintech_cooccurrence_within_radius)
- **产出**: data/processed/12b_cooccurrence_filtered.parquet (config 键 output_12b_cooccurrence) = stage 12 子集的【近邻相关】子集 (硬过滤丢行); 另落 .meta.json provenance sidecar (判据 + criterion_sha256 + 行数对账)。经 core/reporting.py::save_dataset 写盘 (版本元数据; input_files 含 12_fintech_news.parquet + fintech_dict.json + 排除配置)。
- **三轨**: 不适用情感三轨。它在 stage 12 与 stage 13 之间硬过滤丢行, 三轨情感/强度链在下游天然继承过滤结果 (下游 controls.py/encode.py 零改动, 路线 A 纯接受-披露)。注: 判据口径与 stage 13 _ss 轨【不同】—— 12b 是窗口邻近 (银行锚句 ±sentence_radius 句), 严格同句 (_ss, radius=0) 是其子集, **禁互相复用**。

**详细功能说明**

**输入**: `12_fintech_news.parquet` (config 键 output_12_fintech_news, stage 12 的 is_fintech_news==True 关键词金科子集)。

**处理步骤** (`main` → `filter_cooccurrence` → 逐行判定窗口邻近共现):
1. 模块级加载金科 AC 自动机 (load_fintech_dict, 1506 词) + 银行否定/短名排除配置 (load_exclusion_patterns, 与 stage 11/13 同口径)。
2. 对每个 (文章, target_bank) 行, 调 `has_bank_fintech_cooccurrence_within_radius(body, aliases, FINTECH_AC, sentence_radius, ...)` 判定 "目标银行锚句 ∧ ≥1 金科词在 ±sentence_radius 句窗口内" 是否成立, 命中则保留。
3. 性能 (CF-01): 先 `tolist` 取 target_bank/内容两列再纯 Python zip 循环 (避开 df.iterrows() 逐行 Series 开销), 语义与逐行等价 (同序、同 mask); 稳定布尔掩码保留 stage 12 原序, 不 sort_values。

**保留判据** (`has_bank_fintech_cooccurrence_within_radius`, 与 _ss 轨严格同句口径不同):
- 窗口邻近: 银行锚句 i ∧ 金科∈[i±radius] 邻句 (默认 sentence_radius=1); 严格同句 (radius=0) 是其子集。
- 不对称匹配: 银行侧做否定/短名排除 (has_unexcluded_occurrence); 金科侧裸 AC (1506 词), 与 stage 12/13 ss 轨金科侧一致 (单一事实源 core/text/ahocorasick)。

**安全铁律**:
- SAFE-1: FINTECH_AC=None (词典加载失败) → **保留全部行 + loud WARNING** (绝不静默清空整库)。
- min-N 守卫: 仅当 FINTECH_AC 实际生效 (非 SAFE-1) 时校验, keep 率低于 `cooccurrence_filter.min_keep_frac` (默认 0.001) 或 0 行 → `SystemExit(1)` + loud (防真实零共现把整库清空)。

**路线 A (纯接受-披露)**: 12b 仅丢行, 下游 controls.py/encode.py 零改动; n_articles/fintech_share(分子)/attention 族①/NF 对照组的统计宇宙统一平移为 "近邻相关金科" 口径, 在 manuscript/codebook 如实披露。fintech_share 分母经 "望远镜式坍缩" 恒不变 (12b 只把中间集从 ft 端移到 nf 端, 代数和守恒)。⚠ 地理 attention 族 (ft_attn_*/ft_vol_*) 直读 12_fintech_news_full、不经 12b → 仍原始关键词口径, 与 12b 正交。

**外部依赖/确定性**: 纯 CPU (ahocorasick), 无 LLM/网络, 逐位可复现。fintech_dict.json + 排除配置纳入 input_hashes 血缘。provenance sidecar 刻意不含 wall-clock 时间戳 (保确定性)。

**DAG 位置**: 上游 stage 12 (news_fintech), 下游 stage 13 (ctx_materializer) 改读 12b 输出 (唯一 load-bearing 重指针)。学术依据 Andreou et al. 2026 Research Policy (core-contextual word-pairing 的句级窗口操作化) + Hassan et al. 2019 QJE §III.B proximity-based attribution (见模块 docstring)。

**白话说明**

**这一步在做什么**: 在'已经被判为金科新闻'的稿件里, 再卡一道更严的关: 只留下'目标银行和金融科技词出现得足够近'(在同一句或相邻一句里) 的文章, 其余直接丢掉。打个比方: stage 12 只要一篇里凑够几个金科词就盖章'涉金科', 但这篇可能前半段讲某银行、后半段才单独讲金融科技, 两者其实没在谈一回事; 这步就把'银行和金科隔得太远、各说各的'那种稿子剔出去。

**为什么需要它**: 光靠关键词命中容易把'顺带提了金科、但主题根本不是银行×金科'的稿件误算进来 (虚假相关)。要求银行和金科词在相邻句窗口内同时出现, 等于要求它们'谈的是同一件事', 大幅降低误判, 让后面所有银行×金科指标更干净。

**做得好不好的影响**: 这一刀决定了进入下游所有情感/强度/注意力指标的文章总集。它有两道保险: 词典万一加载失败就原样全保留 (绝不误删整库), 真过滤时如果剩下的太少 (疑似全删) 就直接中止报警。它只删行不改下游计算口径, 被删与保留的代数和守恒, 所以 fintech_share 这类比例变量的分母保持不变; 但分子 (近邻相关金科篇数) 会因这道过滤变小, 这一点在论文和码本里如实披露。

---

### 13_materialize_ctx.py

- **注册**: STAGES_MAIN(阶段13: 实体特异性上下文物化 content_ctx / content_ss 三轨)。core/dag.py:189-193 注册 StageSpec(name="阶段13: 实体特异性上下文物化 (content_ctx / content_ss 三轨)", script="13_materialize_ctx.py", group="main", kind="filter"); core/schemas.py:53 声明产出 13_news_with_ctx.parquet。v3.6.0 引入 (Plan E P4 A1), v3.9.0 (2026-06-14) 扩出第三轨 _ss。非 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: pipeline/text/ctx_materializer.py (入口 main → materialize_content_ctx; 提取原语在 core/text/entity_context.py)
- **产出**: data/processed/13_news_with_ctx.parquet (config 键 output_13_news_with_ctx) = stage 12 子集 + 五列文本/旗标 (content_full, content_ctx, content_ss, ctx_is_fallback, ss_is_fallback)。经 core/reporting.py::save_dataset 写盘 (版本元数据 + .csv 预览; input_files=[12_fintech_news.parquet])。
- **三轨**: **本阶段就是三轨的源头**: 同时物化 content_full(标题+全文)/content_ctx(标题+银行实体窗口)/content_ss(标题+银行∧金科同句窗口) 三条文本列, 各配回退旗标 (ctx_is_fallback/ss_is_fallback)。下游 14/15/21/22/23 统一以 ['_full','_ctx','_ss'] 循环消费; stage 21 仅作消费者, content_ss 单一事实源即本阶段。ss/ctx 短文本(<3 句)退化走字符级窗口回退。

**详细功能说明**

**输入**: `12_fintech_news.parquet` (config 键 output_12_fintech_news) 的 '内容'/'标题'/'target_bank' 等列。模块导入时全局加载: 银行否定/短名排除配置 (`load_exclusion_patterns` → NEGATION_AC/SHORT_NAME_EXCLUSIONS/CONTEXT_WINDOW) 与金科 AC 自动机 (`load_fintech_dict` → FINTECH_AC; 加载失败 try/except 兜底为 None → content_ss 全回退)。

**处理步骤** (`main` → `materialize_content_ctx`, idempotent):
1. 幂等短路: 若五列俱全直接返回; 旧 schema (仅有 content_ctx) 走兼容回填路径——补 content_full/ctx_is_fallback, 并以**哨兵**填 content_ss=content_full、ss_is_fallback=True (保幂等, 不重算 ss; 删 content_ctx 可触发全量重算)。
2. 全量路径逐行: 取 body_full='内容', title (缺失显式 pd.isna→空, 不注入字面 'nan'), target_bank。
3. **ctx 轨** = `extract_entity_context(body, 别名, sentence_radius=配置 context_window.sentence_radius 默认1, fallback_char_radius=150, +否定/短名排除)`: 分句→定位银行别名命中句 (经否定/短名排除, has_unexcluded_occurrence)→前后各 radius 句扩窗→O(N log N) 区间合并→' [...] ' 拼接; 无命中回退全文 body (回退公理)。
4. **ss 轨** = `extract_bank_fintech_cooccurrence(body, 别名, FINTECH_AC, sentence_radius=配置 ss_sentence_radius 默认同ctx, fallback_char_radius=150, +否定/短名排除)`: 命中句 = (该句银行别名经排除后仍在) ∧ (含 ≥1 金科词); **不对称口径**——银行侧套否定/短名排除, 金科侧裸 AC (1506 词); 无共现回退全文 body (镜像 ctx); FINTECH_AC=None 时直接全回退。
5. 三轨文本均经 `prepend_title` 注入标题 (body 已以标题开头则不重复; 标题非句末标点则插中文句号)。

**关键公式/算法** (core/text/entity_context.py): 分句 `_split_sentences` 硬边界正则 `[。！？!?；;]` (逗号/顿号不切); 窗口 `_merge_intervals` O(N log N) 区间合并; 短文本(<3 句)退化为字符级窗口 (`_char_level_fallback`, radius=150, ss 路径额外传 fintech_ac 要求同窗共现)。

**输出列** (5 列): `content_full`, `content_ctx`, `content_ss` (三轨文本); `ctx_is_fallback` = (ctx_body == 全文 body) bool; `ss_is_fallback` = (ss_body == 全文 body) bool。两旗标判定都比较'去标题后的 body' (标题前缀对三轨相同, 不影响 entity-miss 语义), 并有 assert 校验列计数与 batch 统计一致。原始 '内容' 列原样保留 (供 doc_length/去重/上下半切分/强度分母/staleness 复用)。

**三轨体现**: 这是 full/ctx/ss 三条文本轨的唯一物化点; v3.6.0 前置 ctx 物化让 stage 14/15 在 stage 21 前即可三轨化, stage 21 直接消费已物化的 content_ctx/ss (tone_llms._materialize_content_ctx 仍存, 保留为幂等向后兼容)。

**外部依赖/确定性**: 纯 CPU (pandas + ahocorasick + 正则分句), **不调 LLM/Embedding/BERT**, 无网络, 逐位可复现。ss 词典加载失败优雅降级 (FINTECH_AC=None → ss 全回退, 不崩管道)。

**DAG 位置**: 上游 stage 12, 下游 stage 14 (fintech_intensity 三轨)/15 (policy_alignment 三轨)/21 (tone_llms 三轨) 全部消费三列文本。实测 (disk 1170 篇): ss 零共现回退 ~14.27%, 主题漂移 65.76% (银行句仅 34% 同时提金科 → ss 与 ctx 是独立信号)。

**白话说明**

**这一步在做什么**: 给每篇新闻额外造三段文本, 供后面不同口径地'读'同一篇文章。第一段 content_full = 标题+整篇正文 (全文视角); 第二段 content_ctx = 标题+只跟这家银行有关的那几句话 (聚焦视角); 第三段 content_ss = 标题+'银行和金融科技出现在同一句'的那几句话 (银行×金科共现视角)。打个比方: 同一篇报道, 一份是整页复印, 一份是只把提到'工行'的段落剪下来, 第三份是只把'工行同时谈到移动支付'的句子剪下来——截不到就退回整篇。原始正文一字不动地保留着。

**为什么需要它**: 同一篇文章, '从全文看的态度'和'只看跟这家银行直接相关那几句的态度'可能不同; 而'银行专门在谈金融科技时的态度'又是另一回事 (很多银行新闻其实在讲罚款、坏账, 跟金科无关)。三条轨道让后面的情感/强度分析能从三个角度各算一遍, 互相印证 (这叫'互为稳健性'——结论不依赖某一种截取方式才靠得住)。

**做得好不好的影响**: 这三段文本是后面情感打分、金科强度、政策契合度等核心变量的**直接输入**。如果上下文窗口截得太碎或截错句子, 后面算出来的'银行对金科的态度'就会失真; 实测显示同句共现轨 (ss) 和聚焦轨 (ctx) 有六成多的差异, 说明它确实带来一条独立的新信息, 能支撑论文的稳健性检验。回退旗标 (ctx_is_fallback/ss_is_fallback) 还会告诉后面'这篇有没有截到相关内容', 是判断信号质量的依据, 间接影响银行-年度面板里这些变量的可信度。

---

### 14_fintech_intensity.py

- **注册**: STAGES_MAIN(阶段14)。core/dag.py:194-198 StageSpec(name="阶段14: 金融科技技术重度评分 (TF-IDF, 三轨 full/ctx/ss)", script="14_fintech_intensity.py", group="main", kind="filter"), 无 enabled_when (随主管道 always-on); core/schemas.py:54 OUTPUT_REGISTRY 映射到 14_fintech_intensity.parquet, schemas.py:117 _OUTPUT_FILENAME_KEYS 复合键 = output_14_fintech_intensity。与任务给定事实一致。
- **底层模块**: pipeline/filtering/fintech_intensity.py
- **产出**: 14_fintech_intensity.parquet (经 core.reporting.save_dataset 写出, 受数据版本控制)。列 = 上游金科子集全列 + fintech_intensity_score(_full/_ctx/_ss) + intensity_verified(_full/_ctx/_ss), 无后缀列 fintech_intensity_score / intensity_verified = _full 向后兼容别名。⚠ 上游来源: 主路径读 stage 13 输出 13_news_with_ctx.parquet (含 content_ctx/content_ss, 按 is_fintech_news==True 筛子集); stage 13 缺失时回退读 12_fintech_news.parquet (无 ctx/ss, 触发 ctx/ss 轨回退 = full)。故输出基底列 = 13 子集全列 (主路径) 或 12_fintech_news 全列 (回退)。
- **三轨**: 真三轨。同一核函数 _compute_intensity_scores 以 text_col 参数分别对 content_full / content_ctx / content_ss 各跑一次; full 轨实际读 content_full (缺列回退 '内容'), 非裸 '内容'。doc_length 按各轨实际文本长度推算 (text_col != '内容' 时取 str.len, 避免用全文长度归一化短文本)。缺 content_ctx/content_ss 列时该轨优雅回退 = _full (即 fintech_intensity_score_ctx/_ss ≡ _full, stage 13 ctx/ss 未物化时)。

**详细功能说明**

**在 DAG 中的位置**: STAGES_MAIN 阶段14, kind=filter, 无显式 timeout (取 StageSpec 默认)。上游 = stage 12 (news_fintech) + stage 13 (materialize_ctx), 下游 = stage 15 (policy_alignment, 直接读 14 的 parquet)。

**输入**:
- `12_fintech_news_full.parquet` — 全量(含非金科)新闻, 仅用作全局 IDF 参考语料(Gentzkow-Kelly-Taddy 2019 JEL §2.2 "full reference corpus" 语义)。⚠ 注释明确警告勿改用 13_news_with_ctx(它只含 is_fintech_news=True 子集会塌缩 IDF 区分度)。
- 逐篇打分语料: 优先 `13_news_with_ctx.parquet`(含 content_ctx/content_ss, 读后按 `is_fintech_news==True` 筛金科子集), 缺失则回退 `12_fintech_news.parquet`。
- 金科词典经 `core.text.ahocorasick.load_fintech_dict` 加载(与 stage 12 共享同一份)。

**处理步骤**:
1. **全局 DF (Module A)** `_compute_global_df_jieba`: 把词典全部关键词 `jieba.add_word` 注入, `_ensure_keywords_injected` 划分 matchable / unmatchable(代码注释记 6/1506 含空格顿号的词 jieba 整词永不可命中, 实际剔除数由 `len(unmatchable)` 运行期计算 → 从权重宇宙剔除并 WARNING 披露)。在全量参考语料上按 **(标题,日期) 去重的唯一文档** 用 jieba 整词统计每个关键词的文档频率 DF 与 N_total(joblib `prefer='threads'` 并行, 分批 2000)。DF 语料列经 `_materialize_df_corpus_column` 在线物化 content_full(prepend_title) 与 TF 端同口径。
2. **综合权重 (Module B)** `_build_intensity_weights`:
   - 步骤A IDF: `raw_idf = log10(N_total/(1+df))` → 均值归一化 → Winsorize(默认 [1,99] 分位)。
   - 步骤B 语义纯度: 用 SentenceTransformer(默认 shibing624/text2vec-base-chinese) 编码每个关键词 → IDF 加权普通质心 `np.average(embeddings, axis=0, weights=idf)`(代码注释明确订正: 名为 "SIF" 实非 SIF, 无 a/(a+p(w)) 平滑与首主成分去除) → 各关键词对质心余弦 → min-max + floor(anisotropy_floor 默认 0.1) 重标定。
   - 步骤C: `W_i = IDF_i × CosSim_scaled_i` 预乘。
   - 多处降级守卫(DF 空 / IDF 均值≤0 / CosSim 全相同 / sentence_transformers ImportError 或运行期 Exception)统一 logger.error 披露口径降级为纯词频或纯 IDF, 防同名列静默漂移。
3. **逐文档打分 (Module C)** `_compute_intensity_scores`, 双重对数核公式:
   `Score_d = Σ_{i:TF>0} [(1 + ln(TF_{d,i})) / (1 + ln(L_d))] × W_i`
   - 防长文偏差(分母 1+ln(L_d))、防复读机刷分(对 TF 取对数)。
   - **二次熔断**: distinct 关键词数 < min_distinct_keywords_jieba(默认 2) → score=NaN, verified=False(NaN 在下游 bank-year 均值中自动剔除, 避免把未验证文章当零强度系统性拉低均值)。

**输出列**: `fintech_intensity_score_{full,ctx,ss}` + `intensity_verified_{full,ctx,ss}`, 加无后缀 `fintech_intensity_score` / `intensity_verified`(= _full 别名)。

**外部依赖/确定性**: jieba(整词分词, 注入态单源, 锁 jieba==0.42.1)、joblib 线程并行、sentence-transformers + text2vec 本地模型(仅用于关键词级语义权重, 非文章嵌入, 不调任何 API, 不进 _llm_cache.db)。**无 LLM/Embedding API、无网络付费**, 本阶段 $0, 确定性取决于 jieba 版本与本地词向量模型。配置节 = config/filtering.yaml::fintech_intensity (代码 CONFIG.get('fintech_intensity'))。

**白话说明**

这一步给每篇'金融科技'新闻打一个连续的'技术含金量分数'。

打个比方: stage 12 只是判断一篇新闻'是不是'谈金融科技(是/否的开关); 这一步则进一步衡量它谈得'有多硬核'。它给每个金科关键词配一个'权重': 越稀有的词(很多文章不提的, 比如'联邦学习')权重越高, 越泛泛的词(篇篇都有的)权重越低; 同时还看这个词在语义上'是不是真的很金科'。然后把一篇文章里出现的关键词按权重加起来, 还特意做两件事: 长文章不会因为字多就自动得高分, 同一个词重复刷十遍也不会线性加分(防'复读机刷分')。如果一篇文章翻来覆去只提一两个孤立的金科词(很可能是顺带一提), 就判定为'没通过验证', 分数记为空缺而不是0, 免得把它当成'零强度'拖累整体平均。

为什么需要它: 后面要研究'银行对金融科技的关注/实质投入'到底强不强, 光数关键词容易被注水的稿件骗到。这个连续分数让'真干事'和'喊口号'能被区分开。

对最终面板/论文的影响: 这个分数(三条轨道的版本)会被聚合成银行-年度的平均金科强度, 直接进入 P2(注意力强度)等论文的核心解释变量。如果权重算偏了或验证门槛没把住, 银行的'金科活跃度'就会被高估或低估, 回归系数随之失真; 反过来, 做扎实了, 论文里'媒体对某银行金科报道越强 → 后续某结果'这类结论才站得住。

---

### 15_article_policy_alignment.py

- **注册**: STAGES_MAIN(阶段15)。core/dag.py:199-204 StageSpec(name="阶段15: 文章级政策语义对齐度", script="15_article_policy_alignment.py", group="main", kind="filter", timeout=7200, 代码注释 '阶段内含 Embedding API 调用'); core/schemas.py:55 映射到 15_article_alignment.parquet (filename_key=output_15_article_alignment)。与任务给定事实一致(产出文件名为 15_article_alignment.parquet, 注意非 15_article_policy_alignment.parquet)。
- **底层模块**: pipeline/filtering/policy_alignment.py
- **产出**: 15_article_alignment.parquet (save_dataset 写出, 受数据版本控制; 列 = 14 全列 + policy_cosine_sim 族, content_ss 物化时 7 列 / 缺失时退回 5 列)。
- **三轨**: 真三轨 + 双模型 twin。content_full / content_ctx / content_ss 各算一遍政策对齐余弦, 每轨再用 MAIN(API)与 ROBUSTNESS(text2vec)两个嵌入模型各算一份(_t2v 后缀)。full 轨优先读 content_full, 缺列回退 prepend_title('标题','内容')内联构建; 缺 content_ctx → ctx 轨回退 = full(policy_cosine_sim_ctx ≡ _full); 缺 content_ss → ss_texts=None, 不产 _ss/_t2v_ss 列(优雅跳过, 避免 _ss≡_full 伪列污染面板)。

**详细功能说明**

**在 DAG 中的位置**: STAGES_MAIN 阶段15, kind=filter, timeout=7200(因含 Embedding API)。上游 = stage 14(直接读 14_fintech_intensity.parquet), 下游被 stage 45 panel runner 的四象限分类(Token/Hidden/Substantive/Irrelevant)消费。

**输入**:
- `14_fintech_intensity.parquet`(含 标题/内容/content_full/content_ctx/content_ss/year/日期 等)。
- `config/authoritative_corpus.txt`(权威政策语料, 经 CONFIG['paths']['authoritative_corpus_file'] 读取, 与 stage 26 共享同一份)。

**核心度量**: `policy_cosine_sim_i = cos(emb(article_i), emb(auth_anchor))`, 理论值域 [-1,1], 实务多落 0~1。

**处理步骤**:
1. **语料加载** `load_policy_corpus_docs`: 按 `# [VINTAGE YYYY]` 标注行 / 落款日期行(YYYY年M月)/ 文号〔YYYY〕N号 解析各政策文档发布年份(vintage); 经 `_strip_leader_names` 镜像新闻侧 normalize 步骤2.5 做敏感词('习近平')对称清洗; 无 VINTAGE 标注时按 ≥3 连续空行切文档。
2. **Vintage-aware 前视守卫**(默认开, config: article_alignment.vintage_aware, 函数 vintage_aware_enabled): 年度 t 的文章只与 **发布年份 ≤ t** 的政策文档段拼成锚点算余弦(消除'2017年新闻比2022年才发布的政策'前视构造)。文章年份从 year 列或 日期 列派生; 年份未知或早于全部政策文档 → 该篇置 NaN。无年份信息或 opt-out 时降级为静态全语料锚点并 WARNING 披露。
3. **嵌入与池化** `_cosine_for_spec`: 政策语料按文档朴素分段 (naive chunking)(_split_into_chunks, token 上限切不重叠段)→ 各段独立嵌入 → 对该年度允许的段做 mean pooling + L2 归一化 = 年度锚点; 文章侧无预截断(2026-06-12 选项 B 移除 8191-token 预截断), 超长文章由引擎 chunk+pool。文章与锚点算 cosine_similarity。每个 spec 用自己的模型独立嵌(API 1536维 vs text2vec 768维, 严禁混算)。
4. **双模型**: MAIN = text-embedding-3-small(config embedding_api, yunwu OpenAI-compat API)→ canonical `policy_cosine_sim_{full,ctx,ss}` + 无后缀别名; ROBUSTNESS = shibing624/text2vec-base-chinese(本地, config embedding_robustness)→ `policy_cosine_sim_t2v_{full,ctx,ss}`。_t2v 失败(try/except 守卫)仅置 NaN 不破坏 canonical。
5. 统计/断言全部 NaN-安全(nanmin/nanmax/nanmean); full↔ctx Spearman ρ 轨间独立性诊断。

**外部依赖/缓存**: 生产嵌入统一走 `pipeline/text/embedding_engine.embed_texts`(LLMCache 穿透 + 动态分批 + chunk-pool); 缓存键含逐字文本(故三轨 content_full/ctx/ss 文本不同字节天然隔离缓存项), 缓存库 = _llm_cache.db。content_full 与 stage 27(benefit_society)逐篇嵌入同源, 同篇文章 API 向量只付费一次。模块内 `_get_embeddings_api_dynamic` 是 legacy(仅 tests/test_pipeline_robustness.py 引用, 生产0调用)。**API 离线守卫**: 嵌入 miss 即付费调 API(不受 NEWS_PROCESS_LLM_OFFLINE 的 stage 21 守卫保护; 裸环境须设 SSL_CERT_FILE=certifi 修 yunwu.ai 证书)。timeout=7200。

**白话说明**

这一步给每篇金科新闻打一个'政策对齐分'——衡量这篇新闻跟国家金融科技政策'像不像'。

打个比方: 先把国家发布的一摞重磅金科政策文件读进来, 浓缩成一份'标准答案'; 再把每篇新闻也变成一串数字(向量), 算它跟'标准答案'的夹角余弦——越接近1说明这篇新闻越贴政策方向, 越低说明越不沾边。这里有个很讲究的细节: 算2017年的新闻时, 只拿'2017年(含)之前已经发布'的政策当标准答案, 绝不拿几年后才出台的政策来比——否则就成了'用未来的信息预测过去', 是学术大忌(叫前视偏误)。

它还同时用两套不同的'翻译机'(一套联网的大模型 API, 一套本地小模型)各算一遍, 互为稳健性对照: 如果两套都给出类似结论, 结果就更可信。

为什么需要它: 后面要把每篇新闻分到四个格子里——'关键词刷得多但其实不贴政策'(洗科技/喊口号)、'关键词不多但很贴政策'(闷声干事)、'又多又贴'(言行一致)、'又少又不贴'(无关)。要分格子, 就必须先有这个'贴不贴政策'的对齐分(配合 stage 14 的'关键词强度')。

对最终面板/论文的影响: 这是把'象征性 vs 实质性采纳'这个核心构念落地的关键一步。若政策语料选错、前视守卫没做、或嵌入算偏, 银行被错分进'洗科技'还是'真干事'就会反转, 直接动摇 P1/P3 等论文关于'媒体语调/政策实质'的主结论。它的输出还会经年度内分位阈值定四象限, 所以哪怕单篇分数小变动, 也可能让整年阈值移动、连带多篇文章翻类, 需要谨慎重生面板。

---

### 18_article_staleness.py

- **注册**: STAGES_MAIN(阶段18)。core/dag.py:278-283 StageSpec(name="阶段18: Article-level staleness 双指标 (surface MinHash + semantic Faiss)", script="18_article_staleness.py", group="main", kind="robustness", timeout=21600); 2026-06-13 起无条件 always-on, 历史 opt-in flag article_staleness.enabled 仅作记录(谓词函数保留供测试)。core/schemas.py:57-60 映射到 18_article_staleness.parquet + 18_staleness_panel.parquet (filename_key 分别为 output_18_article_staleness / output_18_staleness_panel)。与任务给定事实一致。
- **底层模块**: pipeline/text/article_staleness.py
- **产出**: 18_article_staleness.parquet (article 级, 列 = docid(透传, 旧 schema 缺则跳过)/target_bank/year + 所有含 'staleness' 的列) 与 18_staleness_panel.parquet (bank-year 聚合 = 各 staleness 列 mean + 同名 highstale 列(>0.9 占比, 列名 *_highstale_*))。均 to_parquet(index=False)。
- **三轨**: 分两步平价。surface(MinHash)三轨齐全: full/ctx/ss 各算一次(ss 在 v3.9.0 免费补上, 仅依赖 content_ss 文本)。semantic(SBERT+Faiss)暂 full/ctx 两轨; semantic_staleness_ss 延后(DEFER), 因需 stage 30a 为 content_ss 产出 emb_ss, 该 ss 嵌入轨尚未上线 → 该列缺列, 下游 aggregate_to_bank_year 按 `if stale_col in df.columns` 守卫'缺列即跳过'优雅降级。

**详细功能说明**

**在 DAG 中的位置**: STAGES_MAIN 阶段18, kind=robustness, timeout=21600(6h)。上游 = stage 13(13_news_with_ctx.parquet) + stage 30a(30a_article_embeddings.parquet, semantic 轨依赖, 缺则仅 surface 轨) + stage 21/24(聚合域门控, _restrict_to_panel_domain 内连)。产出供下游 panel/稳健性消费。学术锚点 Tetlock 2011 RFS(陈旧信息 return reversal)。

**输入**: `13_news_with_ctx.parquet`(article 级; 缺 year 则从 日期 派生); `30a_article_embeddings.parquet`(可选, 缺则只输出 surface 轨)。

**双指标算法**(对每篇文章求'过去7天内最相似旧文章'的最大相似度):
1. **surface_staleness** `compute_surface_staleness`: 字符级 3-gram shingle(_char_shingles, 中文友好不依赖分词)→ MinHash(num_perm=128) → MinHashLSHForest。按 unique-day 分组的滚动 LSH(每个'天'重建一次 forest, 窗口 = [d-7d, d) **严格排除同日行**), 把原 O(N²) 降到约 7N。返回前按 stable argsort 的逆置换还原原始行序(P0 修复, 防整列错位)。第一周/空窗口 → NaN; 有窗口但 LSH 查询无命中 → 0.0。
2. **semantic_staleness** `compute_semantic_staleness`: Faiss IndexFlatIP(归一化内积 = cosine), 复用 stage 30a 的 SBERT 768维嵌入, 同样日粒度7天滚动窗口、严格排除同日行(修同 docid 跨 bank 复制行 cosine=1.0 的 artifact), 取窗内 top-1 相似度。stable argsort 保证可复现。

**嵌入对齐** `_load_aligned_embeddings`: 按 article_id 显式 join(非裸位置对齐), 行数不等/键缺失/键重复/辅键(target_bank/日期)逐行不一致时 fail-loud sys.exit(1) 提示重跑 30a(防 30a 陈旧静默错位)。

**聚合** `aggregate_to_bank_year`: 每轨 staleness 列 → bank-year mean + highstale(>0.9 占比) 列, `if col in df.columns` 守卫(缺列即跳过, 故 semantic_staleness_ss 在 30a ss 未上线时不会误产空列)。聚合前 `_restrict_to_panel_domain` 把 **平均域** 收缩到 verified 面板语料((docid,target_bank) 内连 24_herd_decay, 缺则 21_tone_llms; 都缺则 ERROR 披露并退回全集)——与面板兄弟列(tone/herd/intensity 聚合自 verified-union ~857篇)口径一致; 但 **参照窗口**(过去7天信息环境)刻意保留全集。

**外部依赖**: faiss-cpu + datasketch(always-on 后缺包会真崩, ImportError raise)。无 LLM/Embedding API、$0。**构念保真披露**: 与 Tetlock 2011 两点刻意偏离——匹配域是 corpus-level 全银行混池7天窗(非同公司72h最近10篇), semantic 轨 SBERT cosine 是扩展(2011年无 SBERT)。G-D2.1 诊断: surface vs semantic corr 期望 [0.3,0.7](互补≠冗余)。

**白话说明**

这一步给每篇新闻打一个'陈旧度'分: 这篇新闻在过去7天里, 有没有和某篇更早的旧新闻高度雷同?

打个比方: 报社里经常有'新瓶装旧酒'——同一件事换个说法又发一遍, 或者通稿被多家媒体转载。这一步就是给每篇新闻查'查重': 翻出它发表前7天内最像它的那篇旧文, 雷同度越高, 这篇就越'陈旧'(信息含量越低)。它用两把尺子量: 一把看'字面像不像'(用一种叫 MinHash 的快速指纹技术, 哪怕几十万篇也能很快两两比对), 另一把看'意思像不像'(用 stage 30a 算好的语义向量, 字面不同但说的是一回事也能抓到)。两把尺子互补, 一篇真正的旧闻重印通常两边都高。

为什么需要它: 投资者对'炒冷饭'的新闻反应较弱(Tetlock 2011 的经典发现), 所以衡量'媒体到底是在传递新信息还是重复旧信息'对解读银行相关报道很重要。

对最终面板/论文的影响: 陈旧度会聚合成银行-年度指标, 主要用作稳健性检验——验证主结论不是被'重复报道的噪音'驱动的。这里有个关键讲究: 算'最近7天有没有旧闻'时用的是全部新闻当背景, 但最后求银行年度平均时, 只把'经过严格验证、确实是关于这家银行'的文章算进去, 跟面板里别的指标口径一致, 否则会混进约26.8%其实不是真讲这家银行的文章, 把平均值带偏。做不好会让稳健性表里的陈旧度指标失真, 削弱论文'结果不是旧闻噪音造成的'这一辩护。

---

### 21_tone_llms.py

- **注册**: STAGES_MAIN(阶段21: 统一 LLM 语义精筛与情感分析, 三轨 full/ctx/ss)。core/dag.py:212-222 StageSpec, timeout=21600 (6 小时硬超时); core/schemas.py:64-67 OUTPUT_REGISTRY 登记两产物 + 122-123 _OUTPUT_FILENAME_KEYS。已逐行核实与题面一致。
- **底层模块**: pipeline/sentiment/tone_llms.py
- **产出**: 21_tone_llms.parquet (verified 并集子集, 下游主消费; config 键 output_21_tone_llms) + 21_tone_llms_full.parquet (含 verified=True/False 全量, 供验证模块; config 键 output_21_tone_llms_full)。另跨 run/跨 stage 读写 data/processed/_llm_cache.db (SQLite LLM 请求缓存, 确定性锚点, 不在 OUTPUT_REGISTRY)。
- **三轨**: 真三轨。full=content_full(标题+全文) / ctx=content_ctx(标题+含目标银行句±窗) / ss=content_ss(标题+银行∧金科同句±窗)。iter_article_track_prompts 逐 (行×轨) yield (full/ctx/ss) prompt, 三轨各跑同一冻结 prompt v8(仅 content 实参不同)、各自 majority-vote、各自产出 _full/_ctx/_ss 列; verified 过滤用三轨并集 (verified_full | verified_ctx | verified_ss, 任一轨 verified 即保留, 非交集), 三轨各自 just-identified 不混 Hansen J。

**详细功能说明**

**输入**: 读 stage 14 输出 `14_fintech_intensity.parquet` (硬依赖, 缺失即报错终止, 不再静默回退 stage 12; main() Step 4(a) 硬化; 因 LLM 需 stage 14 的 `fintech_intensity_score`/`intensity_verified` 列)。关键输入列: `内容`(全文)、`标题`、`content_ctx`(stage 13 物化, 缺则 main() 调 `_materialize_content_ctx` 兜底)、`content_ss`(stage 13 单一事实源物化, 缺则 `iter_article_track_prompts` 优雅回退 content_full)、`target_bank`、`co_mentioned_banks`。

**处理步骤**: ①`main()` 加载 parquet + schema 守护; ②`LLMCache(_llm_cache.db)` 打开 SQLite 缓存; ③`asyncio.run(run_all_llms(...))` 对每篇文章 × 三轨 × 三个 LLM 家族异步并发请求 (信号量 MAX_CONCURRENCY 控并发); ④`_aggregate_track` 对每轨返回 18 元组聚合 (verified 三角验证投票 + sentiment 投票 + locus/substantiveness/collab_mode 三维分类投票 + logit-to-score 概率分数); ⑤逐模型存档列 + 轨级聚合列写回 DataFrame; ⑥verified 并集过滤后写 `21_tone_llms.parquet`, 全量写 `21_tone_llms_full.parquet`。

**关键算法/公式**: 三模型 ensemble 多数决 (`majority_vote_bool` 严格多数 >50%; `majority_vote_sentiment`/`majority_vote_categorical` 分类决); 平局策略可配 (sentiment 平局 tie_strategy='undefined'→None 防中性污染; substantiveness 平局 tie_default='象征性'; locus 平局 tie_default='应用场景'; collab_mode 平局 tie_default='自主研发', 均 conservative=uniform-prior MAP 保守降级); `compute_prob_score(label, confidence)` 把 3 类情感标签+置信度映射到 [-1,+1] 连续分 (logit-to-score, config `logit_to_score.enabled=true`; NaN/越界 confidence→P3_INV 拒绝); `compute_prob_score_binary` 对三维创新标签产 [0,1] 二分类分 (P2_BIN/P3_BIN)。verified gate 用并集 `verified_full | verified_ctx | verified_ss` (非交集), 并产 triple-gate 7 互斥态诊断列 (`llm_verified_triple_*`)。

**输出列** (每轨 _full/_ctx/_ss 各一套): `llm_verified_*`、`llm_sentiment_*`、`llm_agreement_rate_v/s_*`、`n_valid_votes_*`/`n_verifying_votes_*`、`innovation_locus_*`(Gomber 2018 JMIS)、`innovation_substantiveness_*`(W&Z 1994/1998 ASQ)、`innovation_collab_mode_*`(Chesbrough 2003 + L&S 2006 SMJ)、各维度 `*_confidence_*`、`llm_prob_score`(avg_prob_score, 轨级聚合主列)、per-model `{short}_prob_score_*`、`avg_subst/locus/collab_prob_score_*`、逐模型 `{short}_verified/sentiment_*` 存档列; 另产 `llm_verified_dual_*`(3 态) / `llm_verified_triple_*`(7 态) 互斥指示列。

**外部依赖**: 三个 LLM 家族经 config/sentiment.yaml 锁定 = gpt-5.4-nano(short_name gpt54nano) / gemini-3.1-flash-lite(gemini31111) / deepseek-v4-flash(deepseekv4, 走 api.deepseek.com 直连, 其余两家走 yunwu.ai/v1); 需 YUNWU_API_KEY / DEEPSEEK_API_KEY。**Prompt v8 字节级冻结** (`iter_article_track_prompts` 为生产与缓存覆盖审计共用单一事实源; 缓存键 = 模型名+prompt 文本+prompt_version+temperature+seed)。**确定性锚点 = _llm_cache.db** (~407MB/13.3 万条): 命中即 $0 字节级复现; `NEWS_PROCESS_LLM_OFFLINE=1` 离线守卫下缓存 miss 抛 `LLMCacheMissError` 而非调 API + 跳 preflight 探针。**超时**: 父端子进程硬超时 21600s (3x 安全余量覆盖冷缓存/雪崩退避)。

**DAG 位置**: 上游 stage 14 (fintech_intensity) + stage 13 (content_ctx/content_ss 物化); 下游 stage 22 (词典法读 21 输出 `21_tone_llms.parquet`)、最终经 stage 24/45 进面板。本阶段是全流水线唯一核心付费阶段。

**白话说明**

这一步是整条流水线里最贵、最关键的一环: 让三个大语言模型 (相当于三位独立的金融分析员) 各自读同一篇新闻, 先判断这篇报道是不是真的在讲'某家银行和金融科技的关系'(精筛/把关), 再判断它的语气是正面、负面还是中性, 顺带给出这条创新是'实质性还是象征性'、'底层技术还是应用场景'、'自己研发还是对外合作'等标签。三位分析员投票, 少数服从多数, 谁都说不准的就标成'未定'而不是硬塞成'中性'。为什么需要它: 后面要算每家银行每年被媒体报道的整体情绪, 必须先有一个可靠、可复盘的逐篇打分, 而大模型比关键词词典更懂上下文 (比如能分清'不看好'是负面)。它做得好不好直接决定面板里'媒体语调'这个主变量的质量, 也就是论文最核心的结论靠不靠得住。为保证'同一篇文章每次跑出来分数都一样'(论文复现的命脉), 项目把每次问大模型的结果都存进一个叫 _llm_cache.db 的账本, 之后离线照查账本就能零成本、一字不差地重跑——所以这个账本千万不能删。它还把同一篇文章按三种取材范围 (全文 / 只看跟银行相关的句子 / 只看银行和金科同句出现的片段) 各算一遍, 互为稳健性印证; 三种范围里只要有一种判定'确实在讲银行-金科'就把这篇保留下来。

---

### 22_tone_words.py

- **注册**: STAGES_MAIN(阶段22: 词典法情感分析)。core/dag.py:223-227 StageSpec; core/schemas.py:68 OUTPUT_REGISTRY + 124 _OUTPUT_FILENAME_KEYS 登记产物。注: config/paths.yaml::output_22_words_tone = 22_words_tone.parquet (与 schemas 一致), 代码字面量 '22_tone_words.parquet' 仅是 config 缺失时的兜底默认 (main():1681 / 输入侧 1679), 实际产物名 = 22_words_tone.parquet。
- **底层模块**: pipeline/sentiment/tone_words.py
- **产出**: 22_words_tone.parquet (config 驱动名; 代码默认兜底字符串为 22_tone_words.parquet)。另写 22_idf_weights.json (IDF 权重存档, 可复现性) + 同名 .csv 预览。
- **三轨**: 三轨。classify_batch 对 content_full / content_ctx / content_ss 各扫一遍 (内部多处 `for track in ['_full','_ctx','_ss']` 循环), 每部词典产 {dict}_score_{track}、{dict}_zscore_{track}、IDF 加权 {dict}_idf_score/zscore_{track}; content_ss/ctx 缺列时回退全文优雅跳过。

**详细功能说明**

**输入**: 读 stage 21 输出 `21_tone_llms.parquet` (config 键 output_21_tone_llms; 取其 `content_full`/`content_ctx`/`content_ss`/`内容`/`标题` 等列)。

**处理步骤**: ①`load_all_dictionaries()` 延迟加载五部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018) + 跨类重叠词双侧剔除 + `_inject_custom_dicts_to_jieba` 注入 jieba 自定义词; ②可选 `build_idf_weights` 在与 TF 同一语料 (caller 传 content_full, 缺则回退 '内容') 上算 IDF 文档频率 (Gentzkow-Kelly-Taddy 2019 JEL §2.2), 公式 `log10(N/(1+df(w)))`, 均值归一(mean→1) 后 P1/P99 Winsorize, 文档级去重统计 N/df, 存 22_idf_weights.json; ③joblib 线程并行分批 `classify_batch`, 每批对每篇文章三轨调用打分; ④对每部词典每轨的 score 列做 Z-score 标准化 (`_zscore_or_nan`, σ 退化→整列 NaN); ⑤调 `enrich_with_num_intensity_dual_track` (外部模块导入) 三轨派生 `num_intensity_{full,ctx,ss}` (数值披露强度, Davis & Tama-Sweet 2012 CAR); ⑥写 parquet + 预览 CSV + 三轨分类报告。

**关键算法/公式**: 核心是 `_compute_sentiment_with_rules(tokens, dict, apply_degree, apply_adversative)` —— 逐 token 状态机施加语言学规则: 否定词翻转极性 (窗口 NEGATION_WINDOW=2 个分词单元)、程度副词六级权重缩放 (HowNet 六级体系 + Liu 2012, DEGREE_WORDS 由 config 注入)、转折连词后权重 ×ADVERSATIVE_BOOST(默认 1.5)、句末标点重置作用域 (Ding 2008 从句级)。最终分 = self-normalized Σ(final)/Σ|final| ∈ [-1,+1]。**negonly 消融变体**: `apply_degree=False & apply_adversative=False` 只保留否定翻转, 产 `{dict}_score_negonly`/`msent_negonly`, 用作'主结果对去掉程度/转折两条规则是否敏感'的稳健性 (实测 corr(full,negonly)≈0.998-0.999 高度共线, 是稳健性对照非独立信号)。另产 `pos_ratio`/`neg_ratio` (固定 union 词典计数 / word-token 数)、`msent_score`=(raw_neg−raw_pos)/(raw_pos+raw_neg) 原始极性计数 (零规则; framing ≈ Tetlock 2007/Garcia 2013/Henry 2008; 代码注 He et al. 2024 IRFA Eq.1)、clarity/可读性/词汇复杂度等 $0 测度族。

**输出列**: 每部词典 × 三轨的 `{dict}_score/zscore/idf_score/idf_zscore`、`{dict}_score_negonly`、跨词典 `pos_ratio/neg_ratio/msent_score/msent_negonly`、`num_intensity_{full,ctx,ss}`、可读性/复杂度列。

**外部依赖**: jieba (`==0.42.1` 冻结); 纯 CPU, 无 LLM/网络/API, $0; 无缓存锚点 (确定性来自 jieba 版本 + 词典文件)。

**DAG 位置**: 上游 stage 21 (`21_tone_llms.parquet`); 下游 stage 23 (BERT 读 `22_words_tone.parquet`)。STAGES_MAIN 阶段22。

**白话说明**

这一步是'查字典版'的情绪打分: 准备好五本专门的中文金融情绪词典 (里面标好哪些词是褒义、哪些是贬义), 然后逐字逐词扫每篇新闻, 数褒义词、贬义词, 还会按中文语法做修正——遇到'不'就把后面词的好坏反过来 (不乐观=负面), 遇到'非常'就把强度放大, 遇到'但是/然而'就更看重转折后那半句话 (因为作者真实立场常在转折之后)。为什么需要它: 大模型那一步虽然聪明但也可能有偏差或'幻觉', 用一套透明、可解释、谁来跑都一样的词典法另算一遍, 等于给大模型的结论找了个独立的旁证 (论文里叫'稳健性检验')。如果两种方法算出的银行情绪走势一致, 结论就更可信; 如果只用一种, 审稿人会质疑是不是方法本身的偏差。它还专门留了一个'只做否定、不做程度和转折'的简化版本, 用来回答'我的主结果是不是过度依赖那两条修饰规则'——实测发现两者几乎一模一样, 正好证明结论稳。这一步不花钱、不联网, 同样按全文/银行相关段落/银行金科同句段落三种范围各算一遍。

---

### 23_tone_berts.py

- **注册**: STAGES_MAIN(阶段23: BERT模型情感分析)。core/dag.py:232-236 StageSpec (2026-06-12 起无条件 always-on, 不再受 enabled_methods 控制); core/schemas.py:69 OUTPUT_REGISTRY + 125 _OUTPUT_FILENAME_KEYS 登记产物。已核实与题面一致。
- **底层模块**: pipeline/sentiment/tone_berts.py
- **产出**: 23_bert_tone.parquet。另写同名 .csv 预览。
- **三轨**: 三轨 (优雅降级)。Step 1 用 prepend_title 构 content_full_list / content_ctx_list / content_ss_list; ctx、full 先推理, content_ss 列存在才推 ss (缺列日志告警、仅产 full/ctx 两路)。每模型产 {sn}_label / {sn}_{标签} 概率列 + bert_num_windows_{track}, 三轨后缀由 main() 追加。

**详细功能说明**

**输入**: 读 stage 22 输出 `22_words_tone.parquet` (config 键 output_22_words_tone; 取 `标题`/`内容`/`content_ctx`/`content_ss` 列)。

**处理步骤**: ①`_build_model_configs()` 从 config/sentiment.yaml::sentiment_analysis.tone_berts.models 读 3 个 BERT 模型配置; ②`MultiModelSentimentEngine.load_all()` 一次性加载到 GPU (FP32 权重 + AMP autocast 动态混合精度推理); ③Step 1 用 `prepend_title` 拼三轨文本列表 (full=标题+内容, ctx=标题+content_ctx, ss=标题+content_ss); ④`process_all_models` 对 ctx/full/(ss) 各跑批量推理 (物理隔离防 OOM); ⑤超长文本滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5` 50% 重叠, 单窗 ≤max_length 512 含特殊 token, 有效正文 ≤510 token) + 置信度加权池化聚合各窗 logits (logits*=Σ(conf_k·logits_k)/Σconf_k); ⑥三轨结果带后缀写回 DataFrame; ⑦写 `bert_num_windows_{track}` (≥1 正常 / 0 空文本 / -1 推理失败哨兵); ⑧保存 parquet, 释放显存, 打三轨分类报告。

**关键算法**: 各模型按自身 tokenizer 分窗 (fix g-berts-01 后词表不同模型不共享分词); argmax 分类 + 置信度加权窗口池化 (高置信窗口更大权重)。批级异常 → 逐篇重试一次 → 仍失败才写失败哨兵 (label=None/概率 NaN/num_windows=-1, 与空文本 num_windows=0 严格区分)。

**输出列**: 每模型 (finbert_cn/fin_sent_zh/finbert2) × 三轨的 `{sn}_label` + 各标签概率列 (含 2-class 模型补 `{sn}_中性`=NaN)、`{sn}_infer_failed_{track}` 哨兵、`bert_num_windows_{full/ctx/ss}`。

**外部依赖与降级**: 3 模型 = (1) yiyanghkust/finbert-tone-chinese (finbert_cn, HF, 3-class 中性/正面/负面), (2) bardsai/finance-sentiment-zh-base (fin_sent_zh, HF, 基于 Financial PhraseBank 微调, 3-class), (3) FinBERT2 (finbert2, 本地私有, 2-class 负面/正面, 经 .env `FINBERT2_MODEL_DIR` 解析; 留空或路径不存在则**优雅跳过该模型**, 另两个 HF 模型照跑)。`strict_models=true` 默认下两个 HF 模型非预期加载失败会 fail-loud raise; FINBERT2_MODEL_DIR 未配是预期 graceful skip。**须 HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1** 本地重跑 (两 HF 模型连不上 hf.co 但有本地缓存; 见 memory)。依赖 torch/transformers + GPU; 无 LLM API、无 _llm_cache.db (确定性来自模型权重 + AMP argmax 对分类结果无影响)。

**DAG 位置**: 上游 stage 22 (`22_words_tone.parquet`); 下游 stage 24 (herd_decay 硬依赖 23_bert_tone.parquet)。STAGES_MAIN 阶段23, always-on。

**白话说明**

这一步是'AI 神经网络版'的情绪打分: 用三个已经在大量金融文本上训练过的小型语言模型 (BERT 系列, 可以理解为'专门读金融新闻的情绪识别器') 给每篇新闻判正面/负面/中性。它和前两步 (大模型、查字典) 是三条独立路线, 各有所长——BERT 不靠关键词硬数, 而是整体理解一段话的语气。新闻太长超出模型一次能读的长度时, 它像翻书一样用滑动窗口分段读, 每段都有 50% 重叠不漏信息, 最后按'读得有多确定'加权合并。为什么需要它: 同样是给媒体语调找旁证, 三种方法 (大模型 + 词典 + BERT) 互相印证, 结论越稳越能上顶刊。其中一个叫 FinBERT2 的模型是项目自己训练的私货, 别人机器上没有也没关系, 程序会自动跳过它、用另外两个公开模型继续跑, 不会卡死。一个实操坑: 本地重跑要先把'离线模式'开关打开, 否则它会去外网下模型结果连不上而失败。这一步同样按全文/银行相关段/银行金科同句段三种范围各推理一遍 (同句段那一路如果上游没准备好就自动只跑前两路)。

---

### 24_herd_decay_processor.py

- **注册**: STAGES_MAIN(阶段24: 跟风衰减权重)。core/dag.py:249-253 StageSpec (与 stage 23 构成结构性 always-on 链); core/schemas.py:70 OUTPUT_REGISTRY + 126 _OUTPUT_FILENAME_KEYS 登记产物。已核实与题面一致。
- **底层模块**: pipeline/sentiment/herd_decay.py
- **产出**: 24_herd_decay.parquet (追加三轨衰减列后整表写出)。另写 eval_reports/24_herd_threshold_sensitivity.csv (阈值敏感性诊断, 生产路径专属, 单测直调 compute_herd_weights 不落盘)。
- **三轨**: 三轨。compute_herd_weights 对 content_full / content_ctx / content_ss 各跑一次 TF-IDF+余弦, 产 herd_weight_{full/ctx/ss} + n_similar_articles_{full/ctx/ss} (各轨独立打折, 解决原单列权重错施到不同轨的 measurement-treatment 错配, Edwards 2001 ORM); ctx 缺列回退 full, ss 缺列回退 full。另每轨×敏感性 τ 网格各 2 列。

**详细功能说明**

**输入**: **硬依赖** stage 23 输出 `23_bert_tone.parquet` (代码显式禁止回退读 22/21 防磁盘残留污染, 见 main():639; 缺失即 `raise SystemExit(1)` (main():654) 让编排器感知 DAG 契约违规; 取 `target_bank`/`日期`/`content_full`(或 '内容')/`content_ctx`/`content_ss`/`ss_is_fallback` 列)。

**处理步骤**: ①`compute_herd_weights(df)`: 按 `target_bank` 分组; ②对每组三轨各做 TF-IDF 向量化 (`max_features=MAX_FEATURES`=10000 按原始词频截断, `min_df` 比例化 min(MIN_DF, max(2, ceil(0.01·n))) 防套话词污染, as-of yearly vocab fit——年 t 文章的前驱计数只用 year≤t 文档拟合的向量空间保证历史不变); ③≤2000 篇/前缀 dense pairwise 余弦 / >2000 篇 7 天窗双指针分桶 O(N·window) 算余弦; ④时间窗 (`TIME_WINDOW_DAYS` 默认 7 天) 内文章 j 与更早文章 i 相似度 ≥ `SIMILARITY_THRESHOLD`(0.35, 闭边界 >=) 记为跟风前驱; ⑤生产路径输出阈值敏感性诊断 CSV (预注册 τ 网格默认 {0.25,0.30,0.40,0.45}, 逐 τ flag 率/权重分布/Spearman ρ vs 基线); ⑥保存。

**关键公式**: 衰减权重 `weight_j = 1 / (1 + n_similar_predecessors)` —— 原创首篇权重 1, 第 10 篇抄稿约 1/10, 防同一消息被各家转抄重复计数给情感指标注水。

**输出列**: `herd_weight_{full/ctx/ss}` + `n_similar_articles_{full/ctx/ss}` (6 列) + `herd_weight`/`n_similar_articles` (full 轨 NON-BREAKING 别名 2 列, v3.6.0 兼容) + 敏感性网格 `herd_weight_{track}_{tag}`/`n_similar_articles_{track}_{tag}` (默认 4 τ × 3 轨 × 2 = 24 列)。

**verified-universe 域门控**: 本阶段对**全部**文章 (含 stage 21 verified=False 的) 算 herd 权重——域门控不在此发生; 真正的'只保留 stage 21 verified 集'的 (docid, target_bank) semi-join 在下游 stage 45 panel runner 里完成 (见 memory panel-universe-consistency-audit: attention 族曾因分子绕过该 semi-join 泄漏 26.8% 伪文章)。本阶段产出是面板聚合情感时的逐文章降权乘子。

**外部依赖**: scikit-learn TfidfVectorizer + scipy (余弦/spearman); 纯 CPU, $0, 无 LLM/网络。确定性来自固定 TF-IDF 参数 + as-of vocab fit。

**DAG 位置**: 上游 stage 23 (硬依赖); 下游 **stage 45 panel runner 硬依赖** `24_herd_decay.parquet` (pipeline/panel/runner.py:460 读, 缺文件则 sys.exit(1) 于 463-465; 关键列缺失另在 476 退出)——23→24→45 是结构性 always-on 链, 这正是把 23/24 提为 always-on 要消除的脆弱耦合。STAGES_MAIN 阶段24。

**白话说明**

这一步在解决'同一条新闻被各家媒体抄来抄去导致情绪被重复计算'的问题。同一家银行的一条消息, 往往当天被几十家媒体转载、改写, 内容大同小异。如果把这几十篇都当成独立的'情绪表态'加起来, 这家银行那段时间的情绪就被严重注水了。这一步给每篇新闻数一数'它发出来之前 7 天内, 有几篇内容长得很像的旧文', 然后按这个数量打折: 头一篇原创算满分权重 1, 第十篇抄稿只算约 1/10。打比方就像开会发言, 同一个观点被十个人复述, 只能算一票多一点, 不能算十票。为什么需要它: 没有这个降权, 越是被疯狂转载的大事件 (往往情绪也越极端) 越会主导面板, 让结论被'转载量'而不是'真实信息量'带偏, 这是审稿人会盯的硬伤。它的产出 (每篇的折扣系数) 是后面把逐篇情绪汇总成'银行-年度'面板时必须乘上去的, 所以后续的面板构建那一步硬性依赖它——它一旦缺失或算错, 整张面板和论文里几乎所有回归都会受影响。注意: 这一步对所有文章都算折扣, 而'只统计真正讲银行-金科关系的那批文章'这道筛选是放在更下游的面板汇总环节做的。它同样按全文/银行相关段/银行金科同句段三种范围各算一套折扣, 各算各的不混用。

---

### 27c_placebo_and_alt_anchor.py

- **注册**: 未注册 (设计如此: audit-only sibling)。已核实 27c / benefit_society_audit_combined / 27_alt_anchor 在 core/dag.py 与 core/schemas.py 中均无任何匹配 (Grep 零命中) — 既不在 STAGES_MAIN/STAGES_VALIDATION, 也不在 OUTPUT_REGISTRY/EXPECTED_NO_OUTPUT_STAGES。它是手动/审计专用入口, 刻意游离于编排器之外以保证绝不污染主面板与 golden snapshot。
- **底层模块**: pipeline/features/benefit_society_audit_combined.py (入口 main(argv); 核心 build_audit_panel())
- **产出**: 产出 data/processed/27c_alt_anchor_and_placebo_panel.parquet (bank-year 审计面板, 默认 --output 路径) + 同名 .sidecar.json (锚点 yaml SHA-256 + direction SHA + placebo_keyword yaml SHA + 逐 placebo 命中数 + embedding_model + embedding_dim + tracks 列表 + seed + schema_version 1.1)。注意: 该 parquet **刻意不进** OUTPUT_REGISTRY, 不并入 40_panel_yearly, 不影响 golden; 供下游 benefit_society 论文 Stata 模板 (P2.S1/P2.A2) 消费。--validate-only 仅校验 yaml schema 返回 0; 三个必需输入 (full嵌入/df/main-direction) 任缺时也只校验 yaml 后 return 0 (不产出)。
- **三轨**: 三轨全支持 (作为 twin 列扩展)。full 轨必跑 (--text-embeddings-full); --text-embeddings-ctx 提供时加 `_ctx` twin 列; --text-embeddings-ss 提供时加 `_ss` twin 列 (银行+金科同句共现 content_ss 嵌入)。三轨必须同一 embedding model_id (经各 .npy 的 sidecar model_id 校验, 不同则 raise)。锚点方向向量 track-agnostic, 三轨仅切换文章嵌入子集投影。

**详细功能说明**

**职责**: benefit_society (银行普惠/服务社会) 论文的 audit-only 稳健性管线, 把两项检验合成单一产物 —— ① **替代锚点** (J-L-M canonical 5 对正/负锚点, 换一组定义"惠及社会"的锚句, 测主测度对锚点选择的敏感性); ② **安慰剂** (4 条业务线 housing_loans/credit_cards/intermediate_business/branch_channel + 1 中性基线 general_corporate, 测主信号是否"在不该出现的地方也出现"=伪相关)。

**输入** (CLI 参数, `main(argv)`): `--text-embeddings-full` (stage 27 `27_benefit_embeddings_full.npy`, 必带 .sidecar.json 否则 fail-loud) + `--df-exploded` (文章-银行级 parquet, 含 target_bank/year/标题/内容) + `--main-direction-npy` (stage 27 `27_benefit_direction.npy`, 主 10 锚点金科方向向量); 可选 `--text-embeddings-ctx/ss` + `--seed` (默认 DEFAULT_SEED=20260516) + `--output` + `--validate-only`。

**处理步骤** (`build_audit_panel`):
1. 长度/维度守卫: df 行数 == 嵌入行数; main_direction 维度 == 文章嵌入维度 (防 2026-05-29 换模后方向向量与文章不同空间的根因错配); ctx/ss 同步长度校验。
2. 显式 `np.random.seed(seed)` (当前链路确定性, seed 守卫未来抽样步)。
3. **替代锚点**: `load_jlm_zh_anchors` 读 5 对锚句 → 经统一引擎 `make_anchor_embedding_fn(resolve_embedding_spec(model_id))` 嵌入 (与文章同空间) → `compute_direction_vector` 算锚点方向 → `project_texts` 投影文章嵌入 → `aggregate_to_bank_year` 聚合为 `benefit_jlm_zh_mean/std/pos_frac/neg_frac` (+ ctx/ss twin)。
4. **安慰剂**: `load_placebo_keywords` 读 4 业务线 + 1 中性的关键词集 → `compute_placebo_projection` (关键词掩码 track-agnostic + 文章嵌入投影到**主**方向向量) → `benefit_placebo_{业务线}_mean` (+ ctx/ss twin)。
5. 按 (target_bank, year) outer-merge 合并 alt + placebo → 写 parquet + sidecar。

**关键算法**: 句嵌入余弦/方向投影 (锚点对方向向量 + 文章嵌入点积投影) + bank-year 聚合 (mean/std/正负分数比例, pos/neg_frac 默认以 in-sample median 为 center)。

**外部依赖**: 统一 embedding 引擎 (`embedding_engine.embed_texts`, 经 make_anchor_embedding_fn 闭包穿透 LLMCache; 锚点仅 ~10 句, 嵌入成本 ≈$0, 真重算 deferred 到生产 run); 文章嵌入须 stage 27 预先落盘 (本脚本不调嵌入 API 跑全量文章, 只嵌锚点)。读 yaml (锚点/placebo 关键词)。

**DAG 位置**: stage 27 (benefit 嵌入) 的审计旁支, 上游 = stage 27 的 .npy + sidecar; 下游 = benefit_society 论文 Stata 模板 (P2.S1/P2.A2)。shim 仅 `from ...benefit_society_audit_combined import main; sys.exit(main())`, 零逻辑。

**白话说明**

这一步是"给银行普惠测度做两项打假实验", 而且是专门为 benefit_society 这篇论文服务的、独立于主流水线的旁支 (它故意不接进主面板, 保证万一出错也不会污染正式数据)。

两项实验打个比方: 主测度是用一组"标准锚句"(比如"服务实体经济"算正、"过度逐利"算负) 来给每家银行的新闻打"惠及社会"的分。实验一 (替代锚点) = 换一组同义但措辞不同的锚句重打分, 看结论变不变 —— 如果换了锚句分数就翻盘, 说明主测度太脆弱、是"挑词凑出来的"。实验二 (安慰剂) = 故意拿"住房贷款""信用卡""中间业务"这些跟"惠及社会"无关的普通业务线去打同样的分, 还放一条纯中性基线 —— 如果这些不该有信号的地方也冒出强信号, 说明主测度在乱抓相关性 (伪相关), 不可信。

为什么需要它: 顶刊审稿人会追问"你这个'银行惠及社会'的分数是真有内容, 还是你锚句选得巧/纯属噪声"。这两项检验就是正面回应。

对最终结果的影响: 它本身不进主银行-年度面板、不动任何主回归数字; 它产出一张独立的审计面板, 喂给 benefit_society 论文的稳健性表格。做得好, 就能证明"惠及社会"测度经得起换锚句、扛得住安慰剂, 主结论站得稳; 做得不好 (实验暴露脆弱), 就提示这篇论文的核心测度需要重新设计。

---

### 30a_article_sbert.py

- **注册**: STAGES_MAIN(阶段30a)。core/dag.py:267-272 StageSpec(name="阶段30a: Article-level SBERT 持久化 (D 组前置)", script="30a_article_sbert.py", group="main", kind="robustness", timeout=21600), 无 enabled_when(always-on)。core/schemas.py:62 OUTPUT_REGISTRY 列出 30a_article_embeddings.parquet, 但 schemas.py:129 _OUTPUT_FILENAME_KEYS 映射为 None(无 config filename key)→ 即任务所述'内部副产物, 无 config key'。与任务给定事实一致。
- **底层模块**: pipeline/text/article_sbert.py
- **产出**: 30a_article_embeddings.parquet (内部副产物, 无 config filename key, 硬编码路径 to_parquet; 列 = article_id(=stage 13 的 df.index, 缺 article_id 列时用之)/docid(存在时透传)/target_bank/year/日期 + emb_full[768] + emb_ctx[768](list-of-1D-array)+ model_id/model_revision/text_pipeline_version provenance; docstring 预估 400k 文章约 2.5GB)。
- **三轨**: 嵌入轴仅 full/ctx 两路(content_full / content_ctx 各编码一遍 768维; 缺 content_full 回退裸 '内容'+'标题', 缺 content_ctx → emb_ctx 全 NaN)。ss 嵌入(emb_ss)在 v1 明确延后(plan §④/§7.5, 最贵收益低): 即便 content_ss 已由 stage 13 物化, 本阶段也只 logger.info 记录跳过决策、不编码 emb_ss → 下游 stage 18 的 semantic_staleness_ss 恒 NaN 直到 30a ss 上线。情感三轨(full/ctx/ss)在 stage 21/22/23 已平价, 此处嵌入轴不在三轨范围。

**详细功能说明**

**在 DAG 中的位置**: STAGES_MAIN 阶段30a, kind=robustness, timeout=21600(GPU 4-6h / CPU 12-24h)。D 组前置阶段, 上游 = stage 13(13_news_with_ctx.parquet), 下游被 stage 18(D2 staleness 的 semantic 轨)及模块 docstring 提及的 D3(Krippendorff α, 39c/39d/39f 族)复用——核心动机是把 article-level SBERT 嵌入持久化一次, 避免多处重复编码(节省约12-15h)。

**输入**: `13_news_with_ctx.parquet`(article 级; 优先用 content_full / content_ctx, 缺则回退 内容 + 标题)。

**处理步骤**:
1. `_resolve_sbert_model` 从 `config/features.yaml::embedding_robustness.model`(默认 shibing624/text2vec-base-chinese, 与 stage 15/25 t2v 轨真单源) 解析 model_id + 可选 revision(钉死 HF commit 防权重漂移)。
2. `encode_articles`: 推理前 `ensure_torch_determinism()`(seed 四源 + deterministic algorithms + cuDNN 策略, 对齐 stage 23)。文本构造 = Bybee 2024 风格'标题(≤100字, TITLE_CHARS) + 首段(≤300字, FIRST_PARA_CHARS)'(避免 SBERT 512-token 截断丢尾段)。**关键对称性**: content_full/content_ctx 已由 stage 13 prepend 标题恰好一次, 故 `title_col=None` 关闭二次前置(否则 ctx 轨标题被注入两次, 与 full 轨不对称)。`model.encode(normalize_embeddings=True, convert_to_numpy=True)` → (N,768) float32; show_progress_bar 仅交互式 TTY 显示。
3. emb_full 读 content_full(缺则裸 内容+标题, title_col='标题'), emb_ctx 读 content_ctx(缺则 np.full_like NaN)。
4. `_build_output_frame`: 组装 article_id(= stage 13 的 df.index, 供 stage 18 显式 join 对齐键)+ docid 透传 + target_bank/year/日期 + emb_full/emb_ctx(parquet 兼容的 list-of-1D-array)+ 三列 provenance(model_id / model_revision / text_pipeline_version='v2-2026-06-08-dualtrack-prepend')。

**外部依赖/确定性**: sentence-transformers + 本地 SBERT 模型(shibing624/text2vec, 与 stage 15 _t2v 同源)。**无 LLM/Embedding API、$0**(本地模型); 本地重跑须设 HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1(连不上 hf.co 但有本地缓存)。确定性由 ensure_torch_determinism + revision 钉死保证。无 _llm_cache.db 参与(本地编码每跑重算)。timeout=21600。

**白话说明**

这一步把每篇新闻'翻译'成一串数字(768个数的向量), 让计算机能比较'两篇新闻意思像不像', 然后把这些向量存成文件备用。

打个比方: 它像一个一次性的'语义指纹采集站'——把40万篇新闻挨个扫一遍, 给每篇生成一个'意思指纹', 存进一个大文件。为了省时间和保证一致, 它只读每篇的'标题 + 开头300字'(中文新闻中位数约800字, 模型一次读不完整篇, 而开头通常已含核心信息), 而且特意保证标题只被算进去一次(否则带标题的窗口会把标题权重算重)。

为什么需要它: 后面好几个步骤都要用'语义像不像'——比如 stage 18 判断一篇新闻是不是'旧闻重印'、还有评估多个评分者一致性的步骤(D3)。如果每个步骤各自重新算一遍这些指纹, 要多花十几个小时。这一步算一次、存下来、大家共用, 是个纯粹的'性能/复用'前置, 本身不产出面板里的最终变量。

对最终面板/论文的影响: 它是间接的'地基'——它算出的语义向量喂给 stage 18 的'语义陈旧度', 进而进入稳健性检验。如果这里模型选错、标题被算重、或不同步(比如上游新闻重生了它却没重算导致向量和文章对不上号), 下游的语义相似度就会变成噪音; 代码因此特意用 article_id 严格配对并在对不上时直接报错停下, 强制重算, 防止论文用到错位的语义信号。注意它目前只算'全文'和'银行局部窗口'两条轨, 第三条'银行+金科同句'轨的语义向量暂未上线(成本高收益低), 所以面板里对应的'同句语义陈旧度'暂为空缺, 不影响其它指标。

---

### 31_bank_fintech_threshold.py

- **注册**: STAGES_VALIDATION(阶段31)。core/dag.py:332-336 注册为 StageSpec(name="阶段31: 阈值敏感性分析", script="31_bank_fintech_threshold.py", group="validation", kind="sensitivity"), 默认 always_enabled (省略 enabled_when)。同时列入 core/schemas.py:164 的 EXPECTED_NO_OUTPUT_STAGES (不进 OUTPUT_REGISTRY, 不产 parquet)。
- **底层模块**: validation/threshold.py (入口 main())
- **产出**: 无 parquet 产出 (设计为 validation 诊断阶段)。写入 data/processed/eval_reports/ 下 5 个文件: threshold_sensitivity_bank.csv / threshold_sensitivity_fintech.csv / sensitivity_bank_threshold.png / sensitivity_fintech_threshold.png / threshold_sensitivity_table.tex (PR 曲线图仅当结果含 precision/recall 时才出, 当前无人工验证数据→不出)。
- **三轨**: 不适用 (三轨指 LLM 情感文本轨 full/ctx/ss; 本阶段是分类阶段 11/12 的阈值模拟, 直接读 stage 00 原始 `内容`/`标题`, 早于 LLM 三轨, 不涉及任何轨道循环)。

**详细功能说明**

**位置与角色**: 验证流水线诊断阶段, 不修改任何主链中间数据。shim (31_bank_fintech_threshold.py) 仅 `sys.path` 注入后 `from news_process.validation.threshold import main; main()`。

**输入**: `data/processed/00_preprocessing.parquet` (CONFIG['filenames']['output_00_preprocessing']; 人民日报+Wisers 全量预处理语料), 取 `内容`/`标题` 两列。为提速做抽样: `sample_n = min(sample_max=10000, max(1000, int(总行数×sample_fraction=0.10)))`, `random_state=42`; 抽样量 ≥ 总行数时改全量。

**处理步骤**:
1. 银行分类阈值扫描 — 复用与 stage 11 完全一致的匹配逻辑 (`core/text/ahocorasick.analyze_bank_matches`, 含否定模式 `negation_ac` + 短名歧义消解 `short_name_exclusions` + `context_window`)。先 `_precompute_bank_matches` 一次遍历预计算每篇 upper/lower/title 命中计数, 再对 `min_name_occurrences ∈ threshold_range (默认 1..10)` 网格用 `simulate_bank_classification_from_precomputed` 快速过滤。
2. 金融科技分类阈值扫描 — `_precompute_fintech_matches` (Aho-Corasick `fintech_ac.iter` 上/下半区+标题命中) + `simulate_fintech_classification_vectorized` 对 `min_distinct_keywords ∈ 1..10` 网格过滤。

**关键算法/公式**: 银行判正 = `total (=total_with_title) >= threshold` 且 (`cond_a`: upper>=min_upper 且 lower>=min_lower; 或 `cond_b`: 标题命中 且 正文 (upper+lower)>=min_upper)。注意 fix(omni-extra-threshold-condb, 2026-06-11): cond_b 比较基数从含标题的 total_with_title 改为正文 (upper+lower), 对齐生产 analyze_bank_matches; 前置 `total>=threshold` 仍用 total_with_title (与生产 meets_occurrence 一致, 勿改)。每个阈值算 count / ratio(%) / estimated_total (=int(count/sample_n×total_rows) 按抽样比例外推全量) / is_current。'拐点'建议 = `np.argmin(相邻 count 差分 diffs)` 找样本量下降最剧烈点 (报告 diffs argmin 的右侧阈值)。

**输出列/产物**: CSV 列 = threshold / count / ratio / estimated_total / is_current; 另出双面板 (Panel A 银行 / Panel B 金科, 含 Δ Count) LaTeX 表 + 双子图 PNG (左=样本量柱状, 右=保留率曲线)。

**外部依赖**: 无 LLM/Embedding/BERT; 仅 matplotlib (缺失则 ImportError 捕获后跳图)、pyahocorasick (经 core/text/ahocorasick)。无超时配置 (StageSpec 未设 timeout), 无 _llm_cache.db 锚点。确定性: 抽样 seed 固定=42, 算法纯计数, 完全确定。

**学术依据 (模块 docstring)**: Loughran & McDonald (2011, JF) 阈值稳健性范式; Gentzkow, Kelly & Taddy (2019, JEL) 文本分析人为选择须报告稳健性。

**白话说明**

**这一步在做什么**: 想象你用'文章里出现某银行名字几次'来判定'这是不是这家银行的新闻'。'几次'这个门槛是人为定的 (现在银行用2次、金融科技新闻用2个不同关键词)。这一步就是把门槛从1一直试到10, 每个门槛下数一数还剩多少篇新闻被判为'是', 画成曲线。

**为什么需要它**: 审稿人会问'你为什么挑2而不是1或3? 是不是凑出来的好看结果?'。这一步用证据回答: 如果门槛在2附近上下挪一点, 入选新闻数几乎不变 (处在平坦区), 就说明结论稳, 不是挑出来的; 如果一挪就剧烈变化, 就得谨慎。

**对面板和论文的影响**: 它本身不改任何数据, 只生成附录里的稳健性表格和图。它影响的是'可信度'而非数字 — 让最终银行-年度面板里'哪些新闻算数'这个最底层的过滤决策站得住脚。门槛选得稳, 后续所有情感、注意力指标的样本基础就稳; 选得不稳, 整篇论文的样本都可能被质疑。

---

### 32_news_llms_human.py

- **注册**: STAGES_VALIDATION(阶段32: 人工抽样验证样本生成); 同时列入 schemas.py::EXPECTED_NO_OUTPUT_STAGES → 不进 OUTPUT_REGISTRY (无 parquet 产出)。已读代码核实: dag.py:337-342 StageSpec(group='validation', kind='human'), schemas.py:165。
- **底层模块**: validation/llms_human.py (入口 main(); 另含模块级函数 merge_annotations() / set_excel_data_validation())
- **产出**: 无 parquet 产出 (设计如此, 列入 EXPECTED_NO_OUTPUT_STAGES)。产出 = Excel 标注工作台 **data/processed/32_human_samples.xlsx** (文件名取自 config/paths.yaml::filenames.output_32_human_sample = `32_human_samples.xlsx`; 代码内硬编码默认 `32_news_llms_human_samples.xlsx` 仅在该 config 键缺失时回退, 当前配置存在故实际落 `32_human_samples.xlsx`)。merge 子命令额外产出 `32_human_samples_merged.xlsx` (同名 + `_merged` 后缀)。
- **三轨**: 不适用 (track-agnostic)。本阶段只做随机抽样 + 加标注列, 不区分 full/ctx/ss; 抽中的文章行原样携带其全部列, 但生成逻辑本身不按轨循环。

**详细功能说明**

**职责**: stage 21 LLM 投票结果的人工"金标准"采样器 —— 抽一批文章给人类编码员复核, 产出可直接填写的 Excel 工作台, 是 stage 33/34 效标效度评估的上游。

**输入 (三级回退, 取第一个存在者)**: ① `21_tone_llms_full.parquet` (config.filenames.output_21_tone_llms_full) → ② `23_bert_tone.parquet` (output_23_bert_tone) → ③ `21_tone_llms.parquet` (output_21_tone_llms)。三者皆缺则 logger.error 并 return (不抛异常)。

**处理步骤** (`main()`):
- `load_config()` 读 `human_validation.sample_size` (默认 500) / `random_seed` (默认 42)。
- 简单随机抽样 `df.sample(n=min(SAMPLE_SIZE,len(df)), random_state=RANDOM_SEED)`; 行数 ≤ 目标量则全选 (`df.copy()`)。确定性由固定 seed 保证。
- 追加 4 个空标注列: `编码者A_验证`/`编码者B_验证` (取值 1/0 = 真/伪) + `编码者A_情感`/`编码者B_情感` (正面/中性/负面)。初值均为空字符串 `''`。
- 列重排: 把 4 个标注列 + 关键展示列 (日期/媒体类型(中文)/标题/内容/target_bank/co_mentioned_banks/fintech_keyword_details, 取存在者) 提到最前。
- 用 `xlsxwriter` 写 Excel (sheet 名 `验证数据`), 并经 `set_excel_data_validation()` 对验证列下拉锁定为 {'1','0'}、情感列锁定为 {正面,中性,负面} (动态范围 行2:行10000); 引擎不可用/写盘异常时回退普通 `to_excel`。

**合并函数 `merge_annotations()`** (编码完成后手动调用): 读回填好的 xlsx, 逐行比对两编码者 —— 验证/情感各自: 两人皆有效且一致 → 写共识 `最终_验证`/`最终_情感`; 分歧 → 写哨兵 (`最终_验证`=-1, `最终_情感`='待仲裁'); 另加空 `裁定备注` 列; 输出 `*_merged.xlsx` + 一致率/分歧数/待仲裁数日志。这些哨兵正是 stage 33 评估时要剔除的 attrition。⚠ **该 merge 子命令仅经模块入口可达** —— `python -m news_process.validation.llms_human merge [in.xlsx] [out.xlsx]` (模块 `__main__` 解析 argv[1]=='merge'); 根 shim `32_news_llms_human.py` 的 `__main__` 只调 `main()` 且不透传 argv, 故 `python 32_news_llms_human.py merge` **不会** 触发合并 (只会跑抽样)。

**关键算法/公式**: 无统计计算, 核心是确定性随机抽样 (pandas `df.sample` + 固定 random_state) + Excel 数据校验下拉规则。

**外部依赖**: pandas / numpy / xlsxwriter (写校验下拉) / openpyxl (回退路径与 merge 读 xlsx)。无 LLM/Embedding API 调用, 无 _llm_cache.db, 无网络, $0。

**DAG 位置**: 验证支线 stage 32, 上游 = stage 21 (LLM) / 23 (BERT) 的文章级产出; 下游 = stage 33 (`llms_evaluation.main` 读 32 产出的填好 Excel 算 precision/recall/κ)。shim 仅 `sys.path` 注入后 `from ...llms_human import main; main()`, 零业务逻辑。

**白话说明**

这一步是"出考卷": 从全部新闻里随机抽 500 篇 (固定随机种子, 每次抽的都一样), 做成一张 Excel 表 (默认文件名 32_human_samples.xlsx) 发给两位人工编码员, 让他们逐篇判断 ①这条新闻是不是真的银行金融科技新闻 ②它的语气是正面/中性/负面。表格里的判断列被锁成下拉菜单, 防止有人手滑填错格式。

为什么需要它: 流水线主要靠 AI 大模型 (LLM) 给每篇新闻打标签, 但我们必须证明"机器打的标签跟人判断的一致", 否则审稿人不信。这张人工答卷就是后面给机器打分用的"标准答案"。编码员填完后, 还有个合并环节把两人的答案对齐 (一致就采纳, 吵架就标"待仲裁")—— 注意这个合并要用模块入口 `python -m news_process.validation.llms_human merge` 触发, 直接跑根脚本带 merge 参数是无效的。

对最终结果的影响: 它本身不直接进银行-年度面板, 也不改任何论文数字。但它的抽样质量决定了 stage 33/34 算出的"机器准确率/κ 一致性"可不可信 —— 抽得有代表性, 验证结论才站得住; 抽偏了 (比如全抽到容易判的), 会高估机器水平。

---

### 32a_dedup_threshold_sensitivity.py

- **注册**: STAGES_VALIDATION(阶段32a)。core/dag.py:343-347 注册为 StageSpec(name="阶段32a: 去重阈值敏感性分析", script="32a_dedup_threshold_sensitivity.py", group="validation", kind="sensitivity"), always_enabled (历史 runner 无专属 flag)。列入 schemas.py:166 EXPECTED_NO_OUTPUT_STAGES。流水线编排上在 stage 32 (人工抽样) 之后执行。
- **底层模块**: validation/dedup_threshold.py (入口 main())
- **产出**: 无 parquet 产出 (validation 诊断)。写 data/processed/eval_reports/dedup_sensitivity_report.csv, 列 = Threshold / Retained / Dropped / Retained_Ratio / Is_Production / Input_Mode / Mechanically_Censored。
- **三轨**: 不适用。去重发生在文章级、远早于 LLM 情感三轨; 本阶段只对原始去重前语料做 MinHash 相似度阈值扫描, 不涉及 full/ctx/ss。

**详细功能说明**

**⚠ 与任务描述的偏差订正**: 任务要点写的 'attention_*_jXXwY 20列演示' 实际属于另一个模块 `pipeline/panel/dedup_sensitivity.py` (runner 步骤 6b-3, 在面板上派生 20 个 `attention_*_jXXwY` 列)。本 shim (32a) 转发的是 `validation/dedup_threshold.py`, 它产出的是 `dedup_sensitivity_report.csv` (4 阈值×7 列), 与 jXXwY 列无关, 不要混淆。

**输入 (双口径, 关键)**: 优先 `data/processed/_cache/*.parquet` — 这是 stage 00 在去重**之前**写的 per-file 增量快照 (normalize+filter 后), 经 `_load_pre_dedup_corpus` 仅读 5 列 ['docid','标题','内容','日期','媒体(中文)']。缓存目录缺失/为空/任一文件缺列或读取失败时回退 `21_tone_llms.parquet` (CONFIG['filenames']['output_21_tone_llms']; 已按生产阈值去过重的下游产物)。

**处理步骤**: 
1. 读生产阈值 `deduplication.jaccard_similarity_threshold` (默认 0.80) 作基准标注。
2. 实例化 `ArticleDeduplicator(config, logger)` (canonical path = `news_process.pipeline.preprocess.dedup`, 与生产 stage 00 同一类), 先 `_prepare_dataframe` + `_perform_exact_deduplication` 做一次精确去重 (作近似去重基数)。
3. 对 thresholds=[0.75, 0.80, 0.85, 0.90] 逐个覆写 `dedup.threshold` 并 `_perform_near_deduplication`, 记录 Retained/Dropped/Retained_Ratio, 每轮 `del df_near; gc.collect()` 防 OOM。

**关键算法**: Jaccard MinHash LSH 近似去重 (Broder 1997 IEEE SEQUENCES, DOI:10.1109/SEQUEN.1997.666900)。`_annotate_censoring` 追加披露列: pre_dedup_cache 口径双向有效 (Mechanically_Censored 全 False); post_dedup_fallback 口径下 `Threshold >= 生产阈值` 的行 Dropped≈0 是'机械截尾'而非稳健性 (逐行标 Mechanically_Censored=True) — 这是 fix(omni-g-val-robust-01, 2026-06-11) 的核心: 旧实现读已去重数据扫更高阈值必然 Retained≈100%, 是数据被剪过的假象, 现改读去重前快照真实重去重。

**外部依赖**: 无 LLM; ArticleDeduplicator 内部用 MinHash (datasketch)、pyarrow.parquet (读 schema/列子集)。无显式 timeout。确定性: MinHash 用固定 permutation, 结果确定。

**上下游**: 纯诊断, 不写回主链, golden 不受影响。

**白话说明**

**这一步在做什么**: 同一条新闻常被多家媒体转载, 流水线会把高度相似的稿子合并成一条 (去重)。'相似到什么程度算重复' 是个门槛 (现在用 0.80, 即 80% 相似)。这一步把门槛换成 0.75/0.80/0.85/0.90 各跑一遍, 看每个门槛下还剩多少篇文章。

**为什么需要它**: 防止有人质疑'你定 0.80 是为了凑数据'。如果门槛上下挪保留的文章数变化不大, 就说明去重不会人为操纵样本。这里有个大坑模块特意防住了: 如果拿'已经去过重的数据'去测更严的门槛, 肯定测不出新重复 — 不是因为门槛好, 而是数据早被剪过了。所以它优先去读'去重之前的原始快照'来真测, 实在拿不到才退而求其次并在报告里逐行老实标明'这个数字是机械结果, 别当证据'。

**对面板和论文的影响**: 去重直接决定每条新闻只数一次还是被重复计入。去重门槛若不稳, 银行某一年的'新闻热度/情感'就会被转载量人为放大或缩小, 进而扭曲银行-年度面板的核心变量。这一步给出的就是'去重门槛不影响结论'的书面证据。

---

### 33_news_llms_evaluation.py

- **注册**: STAGES_VALIDATION(阶段33: 分类有效性评估); schemas.py::EXPECTED_NO_OUTPUT_STAGES (schemas.py:167), 不进 OUTPUT_REGISTRY。已核实 dag.py:348-352 StageSpec(group='validation', kind='evaluation')。
- **底层模块**: validation/llms_evaluation.py (入口 main())
- **产出**: 无 parquet 产出 (设计如此)。产出落 data/processed/eval_reports/: classification_eval_results.json / classification_eval_table.tex (含 Panel A-F) / classification_eval_summary.csv / per_model_verification_comparison.csv / per_model_innovation_{substantiveness,locus}_comparison.csv / 混淆矩阵 PNG (cm_verification_llm{track}.png · cm_sentiment_llm{track}.png · cm_innovation_*_llm{track}.png, 三轨各一)。demo 模式 (人工文件全缺) 下 JSON/TeX/CSV/PNG 一律加 _DEMO 后缀防误用。
- **三轨**: 三轨全覆盖。验证任务对 `llm_verified_{full,ctx,ss}` 三列各算指标并做 McNemar 三轨两两 pairwise (full↔ctx/full↔ss/ctx↔ss, 经 itertools.combinations(['_full','_ctx','_ss'],2)); 创新维度 (substantiveness/locus) 对 `innovation_*{_full,_ctx,_ss}` 三轨各评; ss 列缺席时该轨自然跳过 (pred col 不在 join 帧即 continue)。关键披露 GOLD_CONSTRUCT_DISCLOSURE (经 construct_disclosure_for 子串匹配落盘): 人工金标准基于整篇阅读 (全文构念), 用它评 ctx/ss 窗口轨时, 准确率含"窗口-全文构念差", 只能解读为 [模型误差 + 窗口-全文构念差] 的混合下界。

**详细功能说明**

**职责**: 把 stage 32 的人工金标准当"标准答案", 全面评估 LLM 分类器的精度 (真伪验证 + 三分类情感 + 创新二元属性), 产出可直接嵌论文的 LaTeX 表。

**输入**: ① stage 32 的人工标注 Excel (优先 `*_merged.xlsx` 双编码者共识, 回退原始人工样本 xlsx; sheet 名 `验证数据`); ② `21_tone_llms.parquet` (机器预测列); ③ 创新维度另读 `manual_validation_samples.xlsx` (3 编码者 R1/R2/R3, 经 manual_validation_schema.R_COLUMNS_BY_RATER)。人工文件全缺时用 `_generate_demo_data(n=200)` 合成数据走通框架 (demo_mode=True, 全部产物加 _DEMO 标记, 严禁引用)。

**处理步骤** (`main()`, 多职责耦合): 加载 + schema 守护 → 提取金标准 (排除验证哨兵 -1 / 情感哨兵 '待仲裁', 待仲裁数作 attrition 报告; 记录 gold_source ∈ {two_coder_consensus, single_coder_A, demo_synthetic, none}) → 编码者间一致性 (ICR) → 分类器性能 → 误分类系统偏倚诊断 (Carlson & Burbano 2026) → 多格式导出。

**关键算法/公式**:
- **Cohen's κ** `compute_cohens_kappa`: (p_o - p_e)/(1 - p_e), p_o=混淆矩阵对角和/N, p_e=Σ(行和×列和)/N², 自动适配多分类。
- **Krippendorff's α** `compute_krippendorffs_alpha` (名义尺度, 支持 ≥3 编码者 + 缺标): α=1 - D_o/D_e; D_e 仅基于可配对单元 (m_u≥2), 单编码者单元对 α 零贡献 (2026-06-13 修正)。
- **Precision/Recall/F1** `compute_classification_metrics` 经 sklearn, 取 macro + weighted + per-class; accuracy 附 **Wilson score 95% CI** (acc_ci 键, 不改既有键)。sklearn 缺失则 raise ImportError。
- **McNemar** `compute_mcnemar_test`: 分歧数 b+c < EXACT_CUTOFF(=25) 用精确二项检验 (min(b,c)~Binom(b+c,0.5), scipy.binomtest, 无 scipy 时 math.comb 手算), 否则连续性校正卡方 (chi2.sf)。返回 test_type 字段。
- **误分类偏倚** (Panel D): 对 FP-vs-TP / FN-vs-TN 的下游情感分数做 Welch t-test (`_safe_ttest`, ttest_ind equal_var=False) + KS 检验 (`_safe_kstest`, ks_2samp), 检测一阶误差方向是否与二阶 DV 相关 (Carlson-Burbano Fig 1 警告)。
- **创新维度** (Panel E/F, `_evaluate_innovation_panels`): 3 编码者多数票 (`merge_three_rater_majority`) 合成 gold, 与 `innovation_{substantiveness,locus}{track}` 经 docid join (去重 keep=first), 算分类指标; 同时对 3 编码者原始标注算 Krippendorff α (折叠前信度, results 独立键 innovation_inter_coder_reliability); 工作簿带 `population_weight` 时附总体后分层加权 accuracy (Manski-Lerman 选择性样本修正, 仅权重全有限非负时计)。

**外部依赖**: sklearn (必需, 缺则 raise) / scipy (binomtest/chi2/ttest_ind/ks_2samp, 多处有手算回退) / matplotlib (Agg, 中文字体 configure_matplotlib_chinese_fonts)。无 LLM/Embedding API, 无缓存, $0。

**DAG 位置**: 验证支线 stage 33, 上游 = stage 32 (人工 Excel) + stage 21 (机器预测); 纯诊断终点, 无下游消费 (只供论文)。shim 仅 `from ...llms_evaluation import main; main()`。

**白话说明**

这一步是"批改 + 出成绩单": 拿 stage 32 那张人工填好的答卷当标准答案, 给 AI 大模型 (LLM) 的判断逐项打分 —— 它判断"是不是金融科技新闻"准不准 (precision/recall, 即"它说是的里有多少真是"和"真该挑出的它挑出了多少"), 它判断情感正负准不准, 它判断创新是"实质性还是象征性""底层技术还是应用场景"准不准。还会算两位人工编码员之间的一致度 (κ 系数、α 系数, 越接近 1 说明答案越靠谱、不是随便填的)。

为什么需要它: 顶级期刊审稿人一定会问"你怎么知道机器打的标签是对的"。这一步就是用人工答案给机器开"体检报告", 还特别贴心地提醒一个陷阱 —— 人是读整篇文章判断的, 而 ctx/ss 两个版本的机器只看了银行名附近几句话, 所以拿"整篇答案"给"只看片段的机器"打分, 它答错不一定是笨, 可能是片段和整篇本来就传达了不同意思, 因此这两轨的分数只能算保守下限。

对最终结果的影响: 不进面板、不改回归数字, 但它产出的精度表和一致性系数是论文"测量效度"章节的命脉。如果机器精度低或编码员一致度差, 整个用 AI 标签做的实证就失去可信度; 这一步做扎实, 主结果才经得起审稿人推敲。

---


### 34_tone_validation.py

- **注册**: STAGES_VALIDATION(阶段34: 情感三角验证); schemas.py::EXPECTED_NO_OUTPUT_STAGES (schemas.py:168), 不进 OUTPUT_REGISTRY。已核实 dag.py:353-357 StageSpec(group='validation', kind='evaluation')。
- **底层模块**: validation/tone_validation.py (入口 main(); 单轨主入口 _run_validation_for_track())
- **产出**: 无 parquet 产出 (设计如此)。每轨产出落 eval_reports/: sentiment_validation_results{track}.json / sentiment_validation_table{track}.tex / sentiment_cross_method{track}.csv / cronbachs_alpha_summary{track}.csv / 热力图 PNG + 人工验证工作台 09_sentiment_verify{track}.xlsx; 回读后产 human_verify_metrics{track}.csv (track ∈ {_full,_ctx,_ss})。
- **三轨**: 三轨全覆盖且为主控制流: main() 对 ['_full','_ctx','_ss'] 各调一次 `_run_validation_for_track`, 每轨独立跑完整 6 步并写带 {track} 后缀的全套报告。人工验证工作台按轨独立抽样 (编码指南随轨切换文本口径: full=标题+正文 / ctx=标题+实体窗口 / ss=标题+银行+金科同句片段; 机器输入文本列 content_full/ctx/ss), 让 ctx/ss 获得真正的窗口级金标准 (区别于 stage 33 的全文构念 gold)。

**详细功能说明**

**职责**: 对三种情感方法 (词典法/BERT/LLM) 做系统交叉验证, 提供"方法间趋同"的**收敛效度** (convergent validity) 证据 —— 代码明确声明这不等于"效标效度"(vs 人工金标准), 后者靠人工回读 (evaluate_human_verification) 和 stage 33。

**输入**: `23_bert_tone.parquet` (含逐级累积的全部词典/BERT/LLM 列, config 键 output_23_bert_tone), 回退 `22_words_tone.parquet` (output_22_words_tone); 两者皆缺则 logger.error 并 return。

**处理步骤** (每轨 `_run_validation_for_track`):
1. `discover_sentiment_columns(df, track_suffix)` 按列名后缀自动识别词典 (`*_score{track}`/`*_label{track}`, IDF 词典单独分 words_idf 组防虚高)、BERT (`*_label{track}` + 正面/中性/负面概率列)、LLM (`*_sentiment{track}` + confidence) 三族列。聚合投票列 short_name=='llm' 被剔除出跨方法统计 (否则把成员模型合成票当第 4 个独立模型, 机械抬高一致性)。
2. **内部一致性**: 各族算 Cronbach's α `(k/(k-1))(1-Σσ²ᵢ/σ²ₜ)` + Spearman 相关矩阵 + 热力图。
3. **跨方法一致性**: 词典综合 vs BERT vs LLM 的 Spearman/Pearson; 标签一致率 (完全一致 = nunique==1; 多数一致 = 众数票数 > 方法数/2 的严格多数)。
4. **分层稳健性** `stratified_analysis`: 按新闻长度 (33/66 分位)、年度、词典覆盖率分层, 每层算 α + 观测一致率; 年度 α 序列 ≥5 年做 Spearman 趋势检验 (预警 temporal drift)。
5. **LLM 概率诊断**: 类别偏向 (chi-square + Jensen-Shannon) + 置信度校准 ECE。
6. **人工验证样本生成** `generate_validation_sample`: 一致样本随机抽 n_agree=100 + 分歧样本随机抽 n_disagree=200 (对分歧案例 2:1 过采样, 经 RandomState(seed) 简单 choice — **非几何/邻域加密**, 只是对存在分歧的文章集做无放回随机抽样并放大配额), 附"机器输入文本"列 (content_full/ctx/ss) 与轨道专属编码指南, 写 `09_sentiment_verify{track}.xlsx`。配套 `evaluate_human_verification` 回读端: 对工作台内全部 11 方法列 (词典 5 / BERT 3 / LLM 逐模型+多数投票) vs 人工判定算 accuracy/macro-P/R/F1 + Cohen κ (复用 stage 33 的 compute_classification_metrics / compute_cohens_kappa, 这是全项目唯一能给词典/BERT 族产出人工指标的路径); 空表 pending 绝不合成, `count_human_annotations` 做 fail-closed 防覆盖守卫 (pending 时清陈旧 CSV, error 时保留)。

**关键公式**: Cronbach α / Spearman ρ / Krippendorff (复用) / Jensen-Shannon 散度 / ECE / Cohen κ。标签数值化: 正面=+1/中性=0/负面=-1, 缺失保 NaN (不 fillna(0) 伪造中性)。

**外部依赖**: pandas/numpy/scipy (spearmanr 等, 有回退) / matplotlib / openpyxl。无 LLM/Embedding API, $0。

**DAG 位置**: 验证支线 stage 34, 上游 = stage 21/22/23 三方法文章级产出; 下游 = 人工回读 (跨阶段闭环到 stage 33 口径)。

**白话说明**

这一步是"三个裁判交叉验票": 我们用三种完全不同的方法给每篇新闻判情感 —— 一是查情感词典 (数好词坏词), 二是 BERT 神经网络模型, 三是 LLM 大模型。这一步检查三者打分一致不一致。如果三种风马牛不相及的方法都说"这篇是负面", 那这个结论就非常可信; 如果它们经常吵架, 说明情感测量本身不稳。

用到的指标都很直观: Cronbach's α 衡量"几个测量是否在量同一件事"(≥0.7 算可接受), Spearman ρ 衡量两种方法排序是否一致, 还会按新闻长短、按年份分组看一致性稳不稳 (防止 AI 模型"随年代越用越漂")。它还会出一张人工抽查表, 专门多抽"三裁判吵架"的疑难篇 (分歧篇配额是一致篇的两倍) 让人裁决。

关键诚实声明: 三种机器方法互相一致, 只能说"它们彼此趋同"(收敛效度), 不能直接等于"它们都对"(那要跟人工答案比, 叫效标效度) —— 代码里反复强调这一点, 防止论文夸大。对最终面板的影响: 不直接改情感数据, 但它给"我们的情感测量可靠"提供了证据链; 三轨各出一份报告, 让 full/ctx/ss 三个版本的情感测度都各自有可信度背书, 主回归用哪一轨都有据可依。

---

### 35_radius_sensitivity.py

- **注册**: STAGES_VALIDATION(阶段35)。core/dag.py:358-362 注册为 StageSpec(name="阶段35: 窗口半径敏感性检验", script="35_radius_sensitivity.py", group="validation", kind="sensitivity"), always_enabled。列入 schemas.py:169 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: validation/radius_sensitivity.py (入口 main())
- **产出**: 无 parquet (任务说的 'EXPECTED_NO_OUTPUT' 成立; 严格说本模块产物是 JSON/TEX/PNG 而非 CSV)。4 个产物全写在 output_dir 根 (= data/processed/, 不在 eval_reports/): 35_radius_sensitivity.json + 35_radius_sensitivity.tex + 35_radius_label_distribution.png + 35_radius_correlation_heatmap.png。
- **三轨**: 半成品多轨。当前实现是 track-agnostic 的窗口半径扫描 — 只动 ctx 提取的句级半径 (`sentence_radius`), 读原始 `内容` 全文用词典法重提情感, 不切换 LLM 情感轨。`RUN_MULTI_TRACK=False` 占位开关未接线 (main() 未分支于此, 翻 True 暂不生效); full/ctx/ss 各跑一遍 RADII grid (输出 35_radius_sensitivity_{full,ctx,ss}.json) 仍是 TODO。可理解为隐式覆盖了 ctx 的提取参数。

**详细功能说明**

**核心问题**: ctx 轨提取'银行名前后几句'时, 半径 (`sentence_radius`, 生产=1) 是人为参数。本阶段在 radius ∈ {0,1,2,3} (`RADII`) 上扫描, 验证词典情感结论对窗口大小是否稳健。

**输入 (订正)**: 优先 `21_tone_llms.parquet` (CONFIG['filenames']['output_21_tone_llms'] — 经 LLM 精筛、仅 llm_verified=True 的下游产物, 含 `target_bank` 列), 回退 `12_fintech_news.parquet`。⚠ 注意是 `21_tone_llms.parquet` 而非 `_full` 版本。必需列 `target_bank` + `内容`。

**处理步骤**:
1. 加载 5 套中文金融情感词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018; 正面+1/负面-1/政治正面+0.5), 注入 jieba (词典词+银行名+金科词+否定/程度/转折词)。
2. 对每篇文章, `analyze_single_article_multi_radius`: 每个 radius 调 `core.text.entity_context.extract_entity_context(sentence_radius=r, fallback_char_radius=150)` 提上下文 (未命中回退原文), jieba 分词, 对 5 词典各算 `_compute_sentiment_with_rules` (否定窗口翻转/程度副词缩放/转折增强/句末标点重置状态机, 与 22_tone_words 逐行对齐) → 归一化得分 + 三分类标签 (正/中/负, 阈值 ±0.1)。
3. 跨半径对比 (基准 r=1): 对每词典算标签一致率、Cohen's κ、Pearson/Spearman 相关、配对 t 检验 (ttest_1samp 得分差)。

**关键算法/公式**: 归一化得分 = total_score / (pos_count+neg_count)。Cohen's κ = (p_o−p_e)/(1−p_e)。零方差守卫 (radius-zerovar-guard, 2026-06-10): 常量分数 (词典零命中/空窗口/样本退化) 或 n≤2 下 pearsonr/spearmanr 置 NaN (语义=相关无定义), 下游裁决用 np.nanmin/np.nanmean (`_compute_pairwise_radius_corr` 热力图同款守卫, NaN 渲染为 'n/a')。'Kappa 悖论' 检测: 主导标签占比 ≥90% 时 κ 被数学压低, 此时一致率/Pearson 更可靠。判定: 邻近窗口 (r=1 vs 2/3) min κ≥0.80 = 强稳健; r=0 (仅实体所在句) 是故意极端压力测试, 偏差大属预期。

**外部依赖**: jieba (必需, 缺则 raise ImportError); scipy.stats; matplotlib (经 HAS_MATPLOTLIB 守卫, 缺则跳图)。无 LLM/缓存。无显式 timeout。确定性: 纯词典+确定提取, 无随机性 (不抽样, 全量处理)。

**学术依据**: Hassan et al. (2019, QJE) proximity-based attribution 参数敏感性。

**白话说明**

**这一步在做什么**: 判断一篇长新闻对某银行是褒是贬时, 流水线不读整篇, 只截取'银行名字出现的那句话, 加上下各 N 句'这一小段来打分 (现在 N=1, 即前后各 1 句)。这个'前后几句'的窗口大小是人定的。这一步把窗口改成 0/1/2/3 句各算一遍情感分, 看分数变不变。

**为什么需要它**: 防审稿人质疑'你只截前后 1 句, 换 2 句结果会不会完全不同?'。如果 1 句和 2/3 句算出来高度一致 (相关 ≥0.8、标签几乎不变), 就证明窗口怎么选都不影响结论。其中 0 句 (只留银行名那一句、上下文全砍掉) 是故意做的极端压力测试, 它偏差大是正常的, 不能拿它否定默认设置。

**对面板和论文的影响**: ctx 轨 (实体上下文情感) 是 P1 主线论文的主变量来源。窗口若选得不稳, 银行情感打分就会随'截多少句'飘忽, 银行-年度面板里的语调变量就不可信。这一步给出的是'情感测量对截取范围稳健'的附录证据, 是 ctx 主结果可信度的支柱之一。

---

### 36_entity_masking_test.py

- **注册**: STAGES_VALIDATION(阶段36)。core/dag.py:363-371 注册为 StageSpec(name="阶段36: Entity Masking 稳健性测试", script="36_entity_masking_test.py", group="validation", kind="robustness", timeout=21600), always_enabled (2026-06-13 移除 entity_masking_test.enabled 早退门)。列入 schemas.py:170 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: validation/entity_masking.py (入口 main())
- **产出**: 无 parquet。写 data/processed/eval_reports/: entity_masking_results.json (三轨四维指标+判定) / entity_masking_detail.csv (逐条对比) / entity_masking_table.tex (三轨 Panel LaTeX) / entity_masking_confusion.png (full/ctx/ss 三轨混淆矩阵并排)。
- **三轨**: 完整三轨。TRACKS=['full','ctx','ss'], 每条新闻同时以全文/实体上下文/银行+金科同句三种输入做掩码替换并重判 LLM。ctx/ss 轨掩码前先经 `build_ctx_masking_input`→`_strip_prepended_title` 剥离 stage13 prepend 的标题前缀 (与生产 prompt 构造对齐, 防标题双重注入污染)。content_ctx/content_ss 缺列时优雅回退全文 `内容` (镜像 ss_is_fallback 公理)。

**详细功能说明**

**核心问题**: 验证 LLM 是否靠'读懂文本'而非'看到银行名的刻板印象' (如'工商银行→国有大行→稳健') 下判定。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full']; 全量含 verified=True/False, 三轨 full/ctx/ss 列)。随机抽样 N=1000 (EM_CFG sample_size, seed=42)。

**处理步骤**:
1. `extract_baseline` 取样本已有的 full/ctx/ss 三轨 LLM 判定 (整体投票 llm_verified/llm_sentiment + 逐模型)。
2. `mask_entity` 三轨各做掩码: 目标银行别名→'目标银行A' (PLACEHOLDER, EM_CFG 可配); 共提银行→'同业银行B/C/D...'; 别名按长度降序替换防短名先匹配; 正文+标题双覆盖; `verify_masking_completeness` 扫正文+标题残留 (残留则 warning)。
3. `run_masked_llms` 异步对掩码文本调 3 模型 × 3 轨 LLM 重判 (PROMPT_TEMPLATE 字节级冻结, 只换 title/content/target_bank/co_mentioned_banks 实参), 走 `fetch_llm_async`。
4. `_aggregate_track` 把三模型应答聚合为 masked_verified/sentiment 等 (18-tuple, v3.4.0 BREAKING)。
5. `compute_masking_consistency` 算四维指标 × 三轨: ①验证一致率 ②情感一致率 (双方均判真子集) ③Cohen's κ ④逐模型一致率。

**关键算法/分母双口径**: 主口径 per-protocol (valid 分母, `_call_failure_mask` 剔除掩码重判或 baseline 调用全失败行 — 空票被默认判 False 属测量缺失非翻转); ITT (physical 分母, 含失败行) 以 `*_itt` 键并行披露。混淆矩阵与主口径对齐 (失败行不进图)。`compute_cohens_kappa` 复用 `news_process.validation.llms_evaluation` (返回含 'kappa' 键的 dict)。判定: 三轨各须 验证一致率≥0.90 + 情感一致率≥0.85 + κ≥0.80, 整体 = full/ctx/ss AND; sentiment_consistency is None (n_both_true==0 子集空) 视为'不可判定'不计通过 (degradation F24 修复, 防伪装通过)。三轨两两 pairwise (combinations) 验证一致率/κ 差异 >5pp 则提示文本粒度敏感。

**外部依赖**: LLM API (yunwu, 经 tone_llms.fetch_llm_async), 3 模型 × 3 轨 × 1000 = 最多 9000 请求; aiohttp 异步, ENTITY_MASKING_MAX_CONCURRENCY 限流。确定性锚点 = `_llm_cache.db` (用 LLMCache 命中缓存; 但掩码文本 prompt 与生产不同 → 这些是增量 LLM 请求, 冷缓存需付费跑)。timeout=21600s (6h) 因冷缓存+限流。matplotlib 三轨混淆矩阵。

**学术依据**: SSRN-4558295 §7.2 entity substitution; Landis & Koch (1977, Biometrics) κ 解释阈值。

**白话说明**

**这一步在做什么**: 把每篇新闻里的银行名字全部涂掉换成匿名代号 ('目标银行A'、'同业银行B'), 再让同一批 AI 模型重新判一遍这篇新闻的真伪和褒贬。然后对比涂名前后 AI 的答案变没变。

**为什么需要它**: 用 AI (大语言模型) 给新闻打情感分, 最怕 AI 不是真读懂文章, 而是一看到'工商银行'就条件反射地觉得'国有大行肯定稳健'。这就好比考试时学生不解题、光看题目里的名字猜答案。涂掉名字后如果 AI 给出的判定还基本一致 (一致率≥90%、扣掉碰巧一致后的 κ≥0.8), 就证明 AI 靠的是文章内容而非对银行的成见。

**对面板和论文的影响**: 整篇论文的情感/注意力指标都建立在'AI 判定可信'之上。如果 AI 其实在凭银行名字下结论, 那银行-年度面板里所有情感变量都掺了'银行身份偏见', 因果推断会被严重质疑。这一步是核心方法论防线之一: 三条文本轨道 (整篇/上下文/同句) 都通过, 才能在论文里宣称'AI 标注稳健、不受银行身份干扰'。它要真跑会花钱 (调 AI 接口), 所以放在最长的 6 小时超时阶段。

---


### 37_dict_coverage_audit.py

- **注册**: STAGES_VALIDATION(阶段37: 金融科技词典覆盖率审计); schemas.py::EXPECTED_NO_OUTPUT_STAGES (schemas.py:171), 不进 OUTPUT_REGISTRY。已核实 dag.py:372-376 StageSpec(group='validation', kind='audit')。
- **底层模块**: validation/dict_coverage.py (入口 main(); CLI flag --run-llm-check)
- **产出**: 无 parquet 产出 (设计如此)。产出落 eval_reports/: 37_coverage_distribution.csv (分析1+2, group_df 非空时, 否则 dist_df) / 37_keyword_frequency.csv (分析3a) / 37_zero_hit_keywords.csv (分析3c) / 37_temporal_drift.csv (分析4)。注: 37_false_negative_estimate.csv (分析5b) 从未生成 (死功能已披露移除)。
- **三轨**: 不适用。审计的是金融科技分类用的关键词词典 (AC 词袋匹配), 与情感三轨 (full/ctx/ss) 无关。LLM 验证率单调性检验固定读 `llm_verified_full` 列 (full 轨), 但这是分类门控信号, 非情感轨。

**详细功能说明**

**职责**: 量化诊断静态金融科技词典 (`fintech_dict.json`, ~1500 词) 是否够用 —— 从 Precision (踩线噪声)、Coverage (词典遗漏/死词)、Stability (时间老化) 三维全自动审计, 零人工零 LLM 付费。

**输入 (两文件)**: ① `21_tone_llms_full.parquet` (分析 1/2/3, 已过 distinct≥T 阈值的金科文章, 选择后样本; config 键 output_21_tone_llms_full) → 列 `fintech_distinct_keywords` / `llm_verified_full` / `fintech_keyword_details`; ② `12_fintech_news_full.parquet` (分析 4/5, 全量银行新闻含被拒行; output_12_fintech_full) → `is_fintech_news` / `日期`。任一缺则 `sys.exit(1)`。阈值 T = `fintech_news_classification.min_distinct_keywords` (默认 2, 实读自 config/filtering.yaml:20)。

**处理步骤 + 算法**:
1. **边际通过率分布** (analysis_1): `fintech_distinct_keywords` 频次分布; 边际率 = 恰好命中 T 个 (刚踩线) 占比, >15% 报警 (词典覆盖勉强)。
2. **LLM 验证率单调性** (analysis_2): 按命中数分组 (=T/=T+1/=T+2/≥T+3) 算 LLM 二次验证通过率 + Wilson CI; 边际组 vs 高命中组差值 (Wald CI); **Cochran-Armitage 趋势检验** (cochran_armitage_trend_test, z 统计量 + p 值) + Fisher 精确检验辅助。
3. **关键词集中度** (analysis_3): 解析 `fintech_keyword_details` JSON 算 article-level 词频; **HHI** = Σ(份额²) (compute_hhi), **有效关键词数 ENK** = 1/HHI (<50 报警, 词典靠少数高频词撑场); 零命中词清单 (口径披露: 选择后样本, 系统性高估死词数, 删词前须在全量语料 12_fintech_news_full 复核)。
4. **时间稳定性** (analysis_4): 逐年总体通过率/边际率/平均命中词; `np.polyfit` 一阶斜率判老化 (边际率↑ + 总体率↓ = 词典老化, 阈值各 ±0.005)。
5a. **灰色地带统计** (analysis_5a): 被拒文章中 1≤distinct<T 的篇数占比 (可能是被漏掉的真金科新闻); 5b (analysis_5b, 仅 --run-llm-check 触发) = 从未实装的死功能 (历史依赖不存在的 utils.llm_clients 模块), 2026-06-11 移除死分支, 仅输出诚实披露, 不产 CSV。

**关键公式**: Wilson score CI / Cochran-Armitage z 统计量 / HHI + ENK (Laakso-Taagepera 等效数)。

**外部依赖**: pandas/numpy/scipy (norm.cdf/fisher_exact, 缺则跳趋势/Fisher 检验)。**无 LLM/Embedding API** (5b 死功能除外), $0。

**DAG 位置**: 验证支线 stage 37, 上游 = stage 21 (full LLM) + stage 12 (全量金科分类); 纯诊断终点, 不修改任何管道数据。

**白话说明**

这一步是"给词典做体检": 判断一篇新闻是不是"金融科技新闻", 靠的是一本人工编的关键词词典 (约 1500 个词)。这一步回答三个问题 —— ① 有多少文章是"刚好踩线"通过的 (比如规定至少命中 3 个词, 很多文章正好只命中 3 个, 说明词典对这批文章覆盖很勉强); ② 这 1500 个词里是不是只有几十个在真正干活、其余都是"摆设死词"(用 HHI 集中度和"有效关键词数"衡量); ③ 词典会不会过时 (金融科技每年冒新词如"数字人民币", 词典没跟上就会表现为踩线率逐年升高)。

为什么需要它: 整个研究的样本边界 (哪些新闻算金融科技新闻) 由这本词典划定。如果词典有系统性漏洞, 样本就会偏 —— 要么放进太多噪声 (伪金科新闻), 要么漏掉大量真金科新闻, 两者都会污染下游的银行-年度面板。

对最终结果的影响: 它不改任何数据, 但它的结论决定"样本可不可信"。如果体检发现词典老化或覆盖不足, 就要扩词典或调阈值后重跑 —— 这会直接影响哪些新闻进入面板、每家银行每年有多少篇金科新闻, 进而影响所有以"金科关注度"为变量的回归。全程纯统计、零付费。

---

### 38_media_diversity.py

- **注册**: STAGES_VALIDATION(阶段38: 媒体名称与地域多样性审计); schemas.py::EXPECTED_NO_OUTPUT_STAGES (schemas.py:172), 不进 OUTPUT_REGISTRY。已核实 dag.py:377-381 StageSpec(group='validation', kind='audit')。
- **底层模块**: validation/media_diversity.py (入口 main())
- **产出**: 无 parquet 产出 (设计如此)。产出 = 单一多 Sheet Excel: data/processed/eval_reports/38_media_diversity.xlsx (12 个 Sheet: 跨阶段总览/全部媒体/媒体名称_Top20/媒体层级分布/长尾分析/地域分布/城市分布/银行媒体覆盖/未覆盖省份/时序稳定性/权重覆盖诊断/跨阶段差异)。
- **三轨**: 不适用。审计的是媒体来源与地域元数据的分布, 与情感三轨 (full/ctx/ss) 无关; 跨 6 个流水线阶段遍历分析, 但维度是"流水线阶段"而非"文本轨道"。

**详细功能说明**

**职责**: 量化每道流水线筛子后"媒体来源"和"地域覆盖"的多样性, 回答审稿人"你的新闻是不是都来自一两家媒体/一两个省", 为论文"数据来源客观性"辩护。

**输入 (跨 6 阶段遍历)**: `00_preprocessing` / `11_bank_news` / `12_fintech_news` / `21_tone_llms` / `23_bert_tone` / `40_article_bank_level` 的 parquet; 列 `媒体(中文)` / `国家地区/省份` / `城市` / `target_bank` / `日期`。另读 config/media_weights.json (媒体权威权重, 经 load_media_weights) + config 的 mainland_china_regions。文件缺则跳过该阶段。

**处理步骤 + 算法** (每阶段):
- **媒体名称多样性** `analyze_media_names`: HHI = Σ份额²; 等效媒体数 ENM = 1/HHI (Laakso-Taagepera); **Shannon 熵** H = -Σpᵢlog₂pᵢ; **Pielou 均匀度** J' = H/log₂(N) (compute_pielou_evenness; S=1 单一媒体返回 NaN 而非误导性 1.0); **Gini 系数** (compute_gini); 加权 HHI (compute_weighted_hhi, 按权威权重); 集中率 CR1/CR3/CR5/CR10/CR20; 长尾 (仅 1 篇/≤5/≤10 的媒体数); 6 层 Tier 分布。
- **地域多样性** `analyze_regions`: 省份级 HHI/Shannon/Gini/Pielou + 东中西部分组 (国统局标准) + 城市分布 + 未覆盖省份识别 + 省份覆盖率。
- **按银行** `analyze_bank_media` (仅 40_ 阶段): 每行 media breadth (唯一媒体数, Bushee2010) + Shannon 熵 + 层级加权得分 + `Tier1-3覆盖率(%)` (权重 w≥80 视为 Tier 1-3 高权威覆盖)。
- **时序稳定性** `analyze_temporal_stability`: 逐年唯一媒体数/HHI/熵 + 新进/退出媒体 + **年际 Jaccard 相似度** (|交|/|并|, 媒体名单跨年重叠度, 平均 ≥0.7 稳定)。
- **权重覆盖诊断**: 识别高频但未评级媒体 (不在 media_weights 且非 default/其他媒体/未知), 供权重表维护。
- **跨阶段差异** `compute_cross_stage_delta`: 相邻阶段 HHI 变化率 + 媒体存留率 + Jaccard。
- **综合结论** `log_comprehensive_summary`: 对最终阶段指标自动判阈值 (HHI≥0.10 / J'<0.70 / Gini≥0.80 / 已评级报道占比<40% / 省份覆盖<80% / 地域HHI≥0.15 报警; J' 为 NaN 时不触发均匀度判定)。

所有结果汇入 12 Sheet Excel (`export_to_excel`, openpyxl)。

**外部依赖**: pandas/numpy/openpyxl。无 LLM/Embedding API, $0。

**DAG 位置**: 验证支线 stage 38, 上游 = 6 个主线阶段产出; 纯诊断终点, 不改任何管道数据。

**白话说明**

这一步是"查新闻来源的家底": 审稿人最爱挑刺的一句话是"你的新闻是不是都来自《人民日报》一家、都报道北京一个省"。这一步就用一整套经典的"分散度"指标量化回答 —— HHI 越小说明来源越分散 (好), "等效媒体数"告诉你实际上相当于几家媒体在干活, Shannon 熵和 Pielou 均匀度衡量报道量在各家媒体间摊得匀不匀, Gini 系数衡量"贫富差距式"的不均, 还按东中西部看地域覆盖全不全。再逐年看媒体名单变没变 (Jaccard 重叠度), 以及流水线每过一道筛子、媒体多样性掉了多少。

为什么需要它: 如果数据高度集中在少数媒体或少数地区, 那"媒体关注度""媒体语调"这些核心变量就可能只反映个别媒体的口味, 而非真实舆论, 实证结论的外部有效性 (能不能推广) 就成问题。

对最终结果的影响: 它不改面板数字, 但它出的这份多样性体检报告是论文"样本代表性"段落的证据。指标健康 (来源够分散、地域够广) 就能挡住"样本有偏"的质疑; 如果发现某道筛子把多样性砍得太狠, 就提示需要回头检查那个环节是不是过度过滤了。全部自动判阈值、出一个 12 页的 Excel 报告。

---

### 38b_decay_sensitivity.py

- **注册**: STAGES_VALIDATION(阶段38b)。core/dag.py:382-387 注册为 StageSpec(name="阶段38b: 距离衰减权重敏感性检验", script="38b_decay_sensitivity.py", group="validation", kind="sensitivity"), always_enabled (历史 runner 无专属 flag)。列入 schemas.py:173 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: validation/decay_sensitivity.py (入口 main())
- **产出**: 无 parquet。写 data/processed/eval_reports/38b_decay_sensitivity.csv (得分矩阵, 列名 = '{dict_name}_{decay_name}', 即 5 词典×3 衰减=15 列)。
- **三轨**: 半成品多轨 (track-agnostic 衰减族扫描)。当前单轨实现: 只动句级距离权重函数, 读原始 `内容` 全文, 不切换 LLM 情感轨。多轨化 (full/ctx/ss 各跑 3 decay → 9×9 相关矩阵) 推迟到 P7.b 单独 PR (TODO), 本轮三轨化不改本模块。

**详细功能说明**

**核心问题**: 计算情感时, 离银行名越远的句子是否该按距离'打折'计权? 本阶段比较 3 种距离衰减权重方案下词典情感得分的相关性。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full'], 回退 glob `21_*.parquet` 取字典序末位)。过滤 `llm_verified_full == True` 仅保留已验证的金科新闻。

**处理步骤**:
1. 加载 5 套词典 (jiang/yao/bian/du/you; 正面+1/负面-1/政治正面+0.5) + 注入 jieba (与 22_tone_words/35 一致)。
2. `run_analysis` 逐文: `core.text.entity_context.extract_entity_context_with_distances(content, aliases, sentence_radius=2)` 提取 [(句文本, 句级距离 d), ...] (radius=2 大于生产 ctx 的 1, 给衰减留空间); 每句 jieba 分词一次 (3 衰减函数共享预分词)。
3. 对 5 词典 × 3 衰减函数 = 15 组合调 `compute_decay_sentiment`。

**关键算法/公式**: 衰减函数 (3 种固定形式, 不做超参搜索以避免研究者自由度, DECAY_FUNCTIONS): uniform w(d)=1 / inverse w(d)=1/(1+d) / exponential w(d)=exp(−0.5d)。距离加权得分 = Σ w(d_s)·tone(s) / Σ w(d_s), 其中 tone(s)=单句归一化得分 (`_sentence_tone`, 否定/转折/程度三规则状态机, 与 22_tone_words 对齐)。`log_correlation_report` 算 uniform vs inverse/exponential 的 Pearson/Spearman + 均值差; 零方差/有效样本<10 守卫置 0.0 (注: 与 35 选 NaN 路线不同, 这里是 0.0 sentinel)。判定: min Pearson≥0.95 高度不敏感 / ≥0.90 基本不敏感 / <0.90 正文讨论。

**重要口径披露 (fix omni-g-val-robust-04)**: uniform 列**不是**生产 ctx 测度的数值锚点 — 三重差异: ①半径 2 vs 生产 1 ②估计量 mean-of-ratios vs 生产 ratio-of-sums ③读原始 `内容` vs 生产读 prepend_title 文本。故结论只能表述为'词典得分在 radius=2 衰减权重族内稳健', 不可说'主结果对权重不敏感'。

**外部依赖**: jieba (必需, 缺则 raise); scipy.stats。无 LLM/缓存/timeout。确定性: 纯词典+确定提取, 全确定。

**学术依据**: Sautner et al. (2023, JF §2.2) 倒数距离衰减; Hassan et al. (2019, QJE) proximity attribution; Loughran & McDonald (2016, JAR) 加权方案稳健性; Simmons et al. (2011) 研究者自由度。

**白话说明**

**这一步在做什么**: 给一篇新闻算银行情感分时, 银行名字所在那句话和离它三句远的句子, 该不该一视同仁? 直觉上越近越相关。这一步用三种打折方式各算一遍: '不打折'(远近句子一样重)、'按距离倒数打折'、'按指数打折', 再看三套分数的相关性高不高。

**为什么需要它**: '远的句子要不要打折、打多少折'又是一个人为选择, 审稿人会问。如果三种打折方式算出的分数高度相关 (≥0.9), 说明怎么打折都不影响结论, 论文附录交代一句即可。模块特别老实地标注了一点: 这里的'不打折'版本和论文真正用的主指标在窗口大小、算法、是否含标题上都有差别, 所以只能说'打折方式不敏感', 不能偷换成'主结果不敏感'。

**对面板和论文的影响**: 它是情感测量的又一道稳健性检查, 确保银行-年度面板里的语调变量不是靠某种'巧妙的加权技巧'凑出来的。做得好, 论文能多一条'我们对句子加权方案做了敏感性分析'的方法论背书; 做得草率或夸大口径, 反而会被审稿人抓住'过度声称'的把柄。

---


### 39_prompt_sensitivity.py

- **注册**: STAGES_VALIDATION(阶段39)。core/dag.py:388-396 注册为 StageSpec(name="阶段39: Prompt措辞敏感度测试", script="39_prompt_sensitivity.py", group="validation", kind="robustness", timeout=43200), always_enabled (2026-06-13 移除 prompt_sensitivity_test.enabled 早退门)。列入 schemas.py:174 EXPECTED_NO_OUTPUT_STAGES。
- **底层模块**: validation/prompt_sensitivity.py (入口 main())
- **产出**: 无 parquet。⚠ report_dir = 模块文件同级目录 `news_process/validation/eval_reports/` (main() line 1548: os.path.dirname(__file__)/eval_reports, **非** data/processed/eval_reports/, 与模块 docstring 写的 'eval_reports/' 相对路径实际落点不同): prompt_sensitivity_results.json / prompt_sensitivity_detail.csv / prompt_sensitivity_table.tex / prompt_sensitivity_heatmap.png (κ 热力图)。
- **三轨**: 完整三轨。run_variant_llms 对 full/ctx/ss 三轨各发请求 (任务数 ×3); ctx/ss 轨在 prompt 构造前 `_strip_prepended_title` 剥离 stage13 标题前缀 (镜像生产 iter_article_track_prompts, 防标题双重注入)。content_ss 缺列回退全文。最终 gate = full/ctx/ss 三轨 AND (active_tracks: full/ctx 必含, ss 仅当变体真产出 _ss 列时纳入, 对旧 parquet 优雅降级)。

**详细功能说明**

**核心问题**: 量化 LLM 标注对 prompt 措辞选择的敏感度 — 同一任务用不同说法重写, 答案变不变。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full']; 含三轨 LLM 判定列, 必需列 llm_verified_full/ctx + llm_sentiment_full/ctx)。随机抽样 N=1000 (PS_CFG sample_size, seed=42)。

**处理步骤**:
1. `extract_baseline` 取 V0 (= 生产 prompt v8, PROMPT_TEMPLATE) 的三轨判定 + 三创新维度 (substantiveness/locus/collab_mode) baseline。
2. 4 个硬编码变体 VARIANT_PROMPTS: V1_role (角色改写) / V2_structure (调换前两阶段顺序+Markdown) / V3_concise (精简) / V4_paraphrase (整句改写+XML `<role>` 标签)。每变体仅改表述, 保持任务语义 + 输出 JSON schema 不变 (v8 已补齐第三维度 innovation_collab_mode 三字段, 消除 baseline v8 vs 变体 v7 的 schema 不一致)。
3. 对每变体 `run_variant_llms` 异步发三轨 × 3 模型请求; `aggregate_variant_results` 用 `_aggregate_track` 聚合 (locus 直接复用生产模块级 `_resolve_locus_track` 保证规则同源; substantiveness/collab 用 majority_vote_categorical conservative); call_failure/undefined 旗标保留。
4. 分轨算: pairwise (变体 vs V0 的验证一致率/情感一致率/Cohen's κ + 三创新维度 κ) + 多变体 (5 编码者 = V0+4 变体的 Krippendorff's α + Fleiss' κ, `compute_fleiss_kappa` 内联实现 line 472) + 跨变体方差。

**关键算法/公式**: Fleiss' κ = (P̄−P_e)/(1−P_e) 推广到 5 编码者。compute_cohens_kappa / compute_krippendorffs_alpha 复用 `validation.llms_evaluation`。失败行掩码 (fix omni-g-val-prompt-05): 变体 API 全失败行剔除, 不计为'措辞不一致'; 全失败→指标 NaN (fail-loud)。阈值: 验证一致率≥0.85 / 情感≥0.80 / κ≥0.70 / α≥0.667 / substantiveness≥0.75 / locus≥0.80 / collab≥0.70。gate = full/ctx/ss 三轨各自全 criteria AND (fix omni-g-val-prompt-03: 此前仅 full 进 gate, 而 P1 主 spec=ctx 轨, 会误报)。

**外部依赖**: LLM API, 4 变体 × 1000 × 3 模型 × 3 轨 = 最多 36000 请求; aiohttp 异步限流。确定性锚点 = `_llm_cache.db` (LLMCache; 变体 prompt 与生产不同 → 增量付费请求, 冷缓存需线上跑)。PROMPT_MAX_RETRIES 缺省已对齐生产 MAX_RETRIES (validation.yaml 可显式取 1 防长尾卡死, 已披露)。timeout=43200s (12h)。matplotlib κ 热力图 (5 编码者 panel)。

**学术依据**: Carlson & Burbano (2026, SMJ §3.5) generating families of related prompts; 框架引 Westphal & Zajac 1994/1998 ASQ + Gomber 2018 JMIS + Chesbrough 2003 + Laursen & Salter 2006 SMJ。

**白话说明**

**这一步在做什么**: 同一道判断题, 用 5 种不同的问法去问 AI — 原版问法, 加上换个口吻、换段落顺序、大幅精简、整句重写这 4 个变体, 意思一字不差。然后看 AI 对同一批新闻给出的 5 套答案一不一致。

**为什么需要它**: 用 AI 做研究有个隐忧: 结果会不会只是'指令 (prompt) 碰巧那么写'才出来的? 换个说法就翻盘? 这就像同一道题, 老师换个措辞问, 学生答案就全变了, 那这答案就不可靠。如果 5 个版本的答案高度一致 (各项一致率、κ、α 都过线, 而且整篇/上下文/同句三条文本轨道都要过), 就证明结果反映的是新闻本身, 不是问法的偶然产物。

**对面板和论文的影响**: 这是 AI 标注可信度的另一根支柱 (和涂名检验互补: 涂名查'是否看名字', 这里查'是否看问法')。如果 AI 判定随 prompt 措辞飘忽, 那银行-年度面板里所有 AI 派生的情感、创新属性变量都成了'问法的产物', 论文核心结论会崩。通过这一关, 才能在论文里写'我们的 LLM 标注对 prompt 措辞稳健'。它是全流水线最贵的检验 (要跑约 3.6 万次 AI 调用), 因此配了 12 小时的超长超时。

---

### 39a_inter_track_kappa.py

- **注册**: STAGES_VALIDATION(阶段39a)。core/dag.py:397-402 注册 StageSpec(group="validation", kind="audit"), 无显式 timeout(取 StageSpec 默认), 无 enabled_when 挂载 → 取默认 always_enabled(谓词 inter_track_kappa 仍登记在 core/dag.py:116 的 _VALIDATION_PREDS, 但自 2026-06-13 起不再挂到任何 StageSpec.enabled_when, 仅作纯函数供测试)。core/schemas.py:175 列入 EXPECTED_NO_OUTPUT_STAGES, 不进 OUTPUT_REGISTRY(只写 eval_reports/ 下的 CSV/TeX, 无 parquet)。
- **底层模块**: pipeline/audit/inter_track_kappa.py(入口 run_stage; shim 39a_inter_track_kappa.py 调 run_stage())
- **产出**: 无 parquet 产出(走 validation 约定, 列入 EXPECTED_NO_OUTPUT_STAGES)。实际写两文件到 output_dir/eval_reports/: inter_track_kappa_table.csv(9 行机器可读表)+ inter_track_kappa_table.tex(booktabs 论文表)。与 Stata 模板 20_tableA1_inter_track_kappa.do.tmpl 互为镜像。
- **三轨**: 三轨核心阶段: 对 full/ctx/ss 两两配对(_TRACK_PAIRS = full_ctx / full_ss / ctx_ss 共 3 个 pair)× 3 个创新维度(_THRESHOLDS: locus / substantiveness / collab_mode)= 9 行 κ。某轨列(如 _ss 后缀尚未物化)缺失时该 pair 行优雅退化为 NaN κ(col_l/col_r in df.columns 缺列守卫, n_obs=0)。

**详细功能说明**

**输入**: 从 config['paths']['output_dir'] 读 `21_tone_llms.parquet`(文章级 LLM 标注), 按 `llm_verified_dual_both == True` 过滤到"双向验证 both"子集。读三个创新维度的三轨列: `innovation_locus_{full,ctx,ss}` / `innovation_substantiveness_{full,ctx,ss}` / `innovation_collab_mode_{full,ctx,ss}`。输入缺失 / 缺 llm_verified_dual_both 列 / dual_both 子集为空 → 发空占位表(全 NaN / n_obs=0 行)而非崩溃。

**处理步骤**(`run_stage` → `compute_inter_track_kappa`):
- 对每个维度 × 每个轨道 pair, 取两列 dropna() 后调 `_compute_kappa_with_bootstrap(return_pvalue=True)`(返回 5 元组 kp/lo/hi/n/pv)。
- 点估计 κ 经 `validation.radius_sensitivity_llm.cohens_kappa_2cat(y1,y2)['kappa']`。
- Bootstrap: `np.random.default_rng(seed=42)`, n_boot=1000 次有放回重抽, 每次重算 κ; 取 2.5%/97.5% nanpercentile 为 95% CI; 守卫: n_obs<3 或点估计常量列 NaN → 直接 NaN 元组; 有限重抽 <50% → CI 报 NaN + RuntimeWarning。
- 单侧 bootstrap p 值: H0 κ=0 vs κ>0, = 有限重抽中 κ≤0 的占比。
- 同维度内对 3 个 pair 的 raw p 值做 Holm(1979) step-down FWER 校正(`_holm_correct`, family=3; NaN 不参与排序, clip 到 [0,1] 并强制单调非降)。

**关键算法/公式**: Cohen(1960) κ=(p_o−p_e)/(1−p_e); Landis&Koch(1977) 解释阈值; 预期 κ∈[0.50,0.70](非越高越好, >0.70 提示轨间冗余、<0.30 提示某轨噪声); Holm step-down(第 k 小 p 值 ×(m−rank) 并强制单调非降)。阈值 _THRESHOLDS: locus 0.50 / substantiveness 0.45 / collab_mode 0.45。

**输出列**(9 行表): field, pair, kappa_point, ci_95_low, ci_95_high, n_obs, threshold, passes_threshold, p_value, p_value_holm。κ 落在 [0.30,0.70] 之外时 warnings.warn(RuntimeWarning)+ logger.warning。

**外部依赖/确定性**: 纯 numpy/pandas, 无 LLM/Embedding API、无 BERT/faiss; seed=42 + NaN-aware 守卫保证确定性可复现; 不触 _llm_cache.db(只读上游已落盘的 stage 21 parquet)。

**DAG 位置**: 验证阶段 39a(STAGES_VALIDATION), 上游=stage 21 tone_llms, 下游=Stata 表 20_tableA1(诊断披露用, 不进主面板)。

**白话说明**

**这一步在做什么**: 同一篇新闻, 我们用三种不同"取景方式"读它——full(读全文)、ctx(只读目标银行附近那一小段)、ss(只读"银行和金融科技出现在同一句"的那几句)——然后各自给它打三个创新标签(这家银行报道讲的是真创新还是装样子、是底层技术还是表层应用、是自己研发还是找外人合作)。这一步像"让三位评委独立打分, 再两两比对他们的吻合程度"。这个吻合程度叫 Cohen's κ(一个一致性分数)。

**为什么需要它**: 如果三种取景方式打出来的标签几乎一模一样(κ>0.70), 说明它们其实在量同一个东西、白白多算了一遍; 如果差得离谱(κ<0.30), 说明至少有一种取景方式在乱打、是噪声。落在中间才说明三种口径各有各的信息、互相补充。bootstrap 和 Holm 校正是为了说"这个吻合程度不是碰巧得来的", 让审稿人信服。

**对最终面板/论文的影响**: 它本身不改银行-年度面板里的任何数字, 只产一张诊断表放进论文附录。它的价值是为论文"三轨互为稳健性"这个核心主张背书——证明三种文本口径既不是冗余重复, 也不是某一轨在添乱, 从而让主回归结论更可信。

---

### 39c_construct_orthogonality.py

- **注册**: STAGES_VALIDATION(阶段39c)。core/dag.py:403-411 注册 StageSpec(group="validation", kind="audit", timeout=10800), 无 enabled_when 挂载 → 取 StageSpec 默认 always_enabled(谓词 construct_orthogonality 仍在 core/dag.py:117 的 _VALIDATION_PREDS, 但不挂到任何 StageSpec, 仅作纯函数供测试)。core/schemas.py:176 列入 EXPECTED_NO_OUTPUT_STAGES——它确实写多个 39c_*.parquet/json 到 data/processed/, 但按 validation 约定不登记进 OUTPUT_REGISTRY。
- **底层模块**: pipeline/audit/construct_orthogonality.py(入口 run_stage; shim 39c_construct_orthogonality.py 调 run_stage())
- **产出**: 写 7 件产物到 out_dir(默认 data/processed/, 可经 OUT_DIR 环境变量覆盖), 走 validation 约定不进 OUTPUT_REGISTRY: 39c_nmi_matrix_full.parquet / 39c_nmi_matrix_ctx.parquet / 39c_nmi_matrix_ss.parquet(各 3×3 NMI+CI+n_pair 长表, 列 d1/d2/nmi/ci_low/ci_high/n_pair)/ 39c_nmi_matrix_cross.parquet(6×6 full∪ctx, 不含 ss)/ 39c_nmi_null_p95.parquet / 39c_nmi_null_p99.parquet(置换 null 分位参照矩阵, 落盘的是 ALL_DIMS 6×6 版)/ 39c_nmi_summary.json(max_off_diag_nmi、classify_full_3x3、interpretation、classify_threshold_scale、reproducibility 锚点)。
- **三轨**: 三轨各出一份 3×3 NMI 诊断矩阵(DIMS_FULL/CTX/SS, 由 _full→_ctx/_ss 机械 swap, 继承同三维度非新维度)。有意不对称: 正交性三档分类(classify_orthogonality)只对 full 3×3 做; ctx/ss 仅产 NMI 矩阵作诊断、不进分类与解读。ss 列未物化时 compute_nmi_matrix 缺列守卫返回全 NaN 矩阵优雅跳过。

**详细功能说明**

**输入**: 读 `21_tone_llms.parquet`(文章级, 可经 STAGE_21_PARQUET 环境变量覆盖; 可复现锚点=v3.4.0 commit 450c1aa7, 见 docstring/summary.json)。用三个创新构念列的三轨版: substantiveness / locus / collab_mode 的 _full/_ctx/_ss。

**处理步骤**(`run_stage`):
- 用 `np.random.SeedSequence(seed=42)` 派生根序列, `.spawn(2)` 取 bootstrap 与 permutation 两个独立子种子状态(避免 seed+1 耦合; 实际 compute_nmi_matrix 内部又各自 SeedSequence.spawn(bootstrap_n) 派生整行 resample 种子)。
- `compute_nmi_matrix` 对 full/ctx/ss 各算 3×3、对 ALL_DIMS(=DIMS_FULL+DIMS_CTX, 6 维)算 6×6 cross: 默认 sample_strategy='listwise_complete'(全 dims 同时非缺整行剔除, 保证所有格子同样本可比); 对角线 NMI=1.0 直接填(跳 bootstrap); 非对角格用 sklearn `normalized_mutual_info_score(average_method='arithmetic')` 算点估计, 再对该 pair 的两列 [d1,d2] 做 1000 次有放回 row resample(SeedSequence.spawn 跨 numpy 版本可复现)取 2.5%/97.5% 为 CI; 守卫: 缺列→全 NaN 矩阵 + warning、样本<100 跳过、退化常量列(nunique<2)跳过并 logger.error、bootstrap 退化>5% warning。
- `compute_permutation_null` 对 ALL_DIMS(落盘 null_p95/p99)与(另单独对 DIMS_FULL 同域, 仅供分类)各算 1000 次置换: 打乱 d2 标签算 null NMI, 取 95%/99% 分位(默认 seed=43, run_stage 传 perm_seed_state)。
- `classify_orthogonality` 只对 full 3×3, 且与 DIMS_FULL 同 listwise 域的 null 比: obs≤null_p95→'strong'、≤p99→'moderate'、>p99→'weak'(关键修复 omni-g-audit-family-04: 观测 point_f 与 null 必须同 DIMS_FULL 3 列 listwise 域, 否则 NMI 有限样本偏差随 N 错配)。

**关键算法/公式**: Vinh-Epps-Bailey(2010 JMLR) 算术平均归一化互信息 NMI=MI(X,Y)/mean(H(X),H(Y)); 阈值口径=置换 null 的**单侧** 95%/99% 分位(≈单侧 Z 1.645/2.326, 非旧注释宣称的双侧 1.96/2.58, 旧未引用常量已删)。

**输出**: 上列 7 件; summary.json 含 max_off_diag_nmi、classify_full_3x3、interpretation(strong/moderate/mixed/undefined; 修复了 classify 全 undefined 时"空真"错报 strong 的 bug, CR-15)、classify_threshold_scale 口径披露、reproducibility 锚点。

**外部依赖/超时/性能**: 依赖 sklearn(1.5–1.8 已验证, lazy import); 无 LLM/Embedding/_llm_cache.db。docstring 估算 N≈40 万标签单线程约 77 分钟(bootstrap 1000 + permutation 1000), 故 DAG timeout=10800(3 小时上限); 64 核 MP 上 n_jobs=16 约 5 分钟(注: 当前实现为 single-thread 串行, n_jobs 并行为 docstring 给出的可选加速路径, 代码默认不并行)。

**DAG 位置**: 验证阶段 39c(STAGES_VALIDATION, 紧跟 39a/39 序列, 避开 40 panel_export), 上游=stage 21, 产物供论文 Appendix A.2 "Construct Validity Evidence"。

**白话说明**

**这一步在做什么**: 我们造了三把"创新尺子"——一把量这家银行的创新是真干实事还是喊口号(实质性)、一把量是底层技术还是表面应用(落点)、一把量是自研还是合作(协同模式)。这一步像质检员检查"这三把尺子是不是真的在量三件不同的事, 还是其实有两把量的是同一个东西"。它用一个叫 NMI(归一化互信息)的指标衡量"知道一把尺子的读数, 能猜出另一把多少", 再把标签随机打乱一千遍看"纯属巧合时能有多像", 只有比巧合明显更像才算"真有重叠"。

**为什么需要它**: 顶刊审稿人会质疑"你这三个新指标会不会是换汤不换药、在重复计量同一件事"。这一步用统计证据回答: 如果三把尺子两两的关联都只跟随机打乱差不多(正交), 就能在论文附录理直气壮地写"三个构念各自独立、没有重复造轮子"。

**对最终面板/论文的影响**: 它不往银行-年度面板里加任何主回归用的列(产物只是诊断矩阵和一份小结), 但它直接决定论文"我们的三维创新测度是有效、可区分的构念"这一方法学主张能不能站住。做得好, 三个指标可以放心分别进各自的回归; 做得不好(发现高度重叠), 论文就得暂缓那部分构念效度声明、请专家复核。

---


### 39d_lexical_discriminant_validity.py

- **注册**: STAGES_VALIDATION(阶段39d)。core/dag.py:412-420 注册 StageSpec(group="validation", kind="audit", timeout=900), 无 enabled_when 挂载 → 取 StageSpec 默认 always_enabled(谓词 lexical_discriminant_validity 仍在 core/dag.py:118 的 _VALIDATION_PREDS, 不挂到任何 StageSpec, 仅作纯函数供测试)。core/schemas.py:177 列入 EXPECTED_NO_OUTPUT_STAGES——确实写 39d_*.parquet + 39d_htmt_matrix.json, 但按 validation 约定不进 OUTPUT_REGISTRY。
- **底层模块**: pipeline/audit/lexical_discriminant_validity.py(入口 main; shim 39d_lexical_discriminant_validity.py 调 main())
- **产出**: 走 validation 约定不进 OUTPUT_REGISTRY。写到 config['paths']['output_dir']。full 轨写 canonical 名: 39d_lexical_discriminant.parquet(metric/value 两列摘要表, value 统一 str 化)+ 39d_htmt_matrix.json(完整报告); ctx/ss 轨写 track-suffixed 名(39d_lexical_discriminant_{ctx,ss}.parquet / 39d_htmt_matrix_{ctx,ss}.json)。某轨列未物化或样本不足时该轨不写文件(run_discriminant_validity 返回 status=missing_columns / insufficient_obs, 仅日志, main 中 continue)。
- **三轨**: 三轨 full/ctx/ss 各跑一次完整判别效度。INDICATORS_FULL 三列经 _full→_ctx/_ss 机械 swap 得 CTX/SS; full 为主 spec(run_discriminant_validity 默认参数, canonical 输出名向后兼容)。ss=银行+金科同句共现轨, 列尚未物化时 run_discriminant_validity 返回 status=missing_columns → 该轨优雅跳过(不写文件)。

**详细功能说明**

**输入**: 读 `40_panel_yearly.parquet`(银行-年度面板)。每轨用 3 个指标列(单 indicator 构念): T1=LLM 实质性概率 `avg_subst_prob_score_{full,ctx,ss}`、T2=词典清晰度 `mean_clarity_score_*`、T3=数字密集度 `mean_num_intensity_*`。

**处理步骤**(`main` → 三轨循环 `run_discriminant_validity`):
- 样本 mask: 优先 `n_articles_llm_valid ≥ 2`(该列缺失时回退 n_articles_col, 默认 'n_articles'), 与 39e 同口径(修 R8-H2); mask 后 <10 obs → status=insufficient_obs 跳过。
- `compute_htmt`: 单 indicator 退化为 HTMT_ij=|corr(T_i,T_j)|(`_safe_corrcoef` Pearson r, 缺值/方差 0 → NaN)。
- `compute_ave_and_phi_squared`: 单 item AVE=1.0, φ²_ij=r²(Fornell-Larcker 1981)。
- `compute_cronbach_alpha_across_indicators`: 跨 3 个 item α=(k/(k−1))(1−Σσ²_i/σ²_total)(跨全部 indicator 而非 within track, 避单 item 退化)。
- `compute_cohen_kappa_substance_vs_clarity`: 二分化(substance≥0.5→象征性 1; clarity<median→含糊 1), 方向锁定预期正 κ; mask.sum()<4 或常量轴守卫(任一二分轴无变异 → 显式 NaN, 避 vacuous κ=0)。
- `compute_spearman_substance_clarity`: 同报 Spearman ρ 避二分化丢信息。
- `compute_permutation_null`: 每对 indicator 打乱 1000 次(seed=42, np.random.default_rng)取 |corr| 的 p95/p99/mean/std。

**关键算法/公式**: Henseler-Ringle-Sarstedt(2015) HTMT 双 cutoff(strict<0.85 / lenient<0.90, 三档 verdict strict_pass/lenient_pass/fail/nan); Cohen(1960) κ; Cronbach(1951) α; Fornell-Larcker(1981) √AVE>max(φ)。注: docstring 标 "算法路径 pairwise on-disk"(为 R7-H3/R8-H3 OOM 设计), 实际 main 一次性 read_parquet 全表入内存逐对计算(面板仅约 9000 bank-year, 内存无压力)。

**输出**: report dict 落两份: parquet(每个非 dict 标量一行 metric/value, 统一 str 化避 pyarrow ArrowTypeError)+ JSON(全报告含 htmt/htmt_verdict/ave_phi_squared/cronbach_alpha_across/cohen_kappa_substance_clarity/spearman/permutation_null/permutation_seed)。

**外部依赖/超时/确定性**: 纯 numpy/pandas, 无 sklearn/LLM/Embedding/_llm_cache.db; permutation seed=42 保证确定性; DAG timeout=900(15 分钟, 实际 N≈9000 bank-year 单线程<1 分钟)。

**DAG 位置**: 验证阶段 39d(STAGES_VALIDATION), 上游=stage 40 panel(及上游 14/15 物化的 clarity/num_intensity 列), 与 39e(LM 子词典 6 维 HTMT)互补, 服务论文 §3.4 判别效度披露。注: R8-H1 ctx-fallback HTMT mask 文档锁定但本 stage 推迟实施(validation-only ROI 低), 论文层若需可在 Stata 用 frac_ctx_fallback<0.30 等价处理。

**白话说明**

**这一步在做什么**: 我们有三把不同的"尺子"量同一批银行新闻——LLM 判的"实质性"(讲的是真创新还是装样子)、词典算的"表述清晰度"(话说得清不清楚)、"数字密集度"(文章里堆了多少数据)。这一步像检查"这三把尺子量的是不是三件不同的事": 它算任意两把尺子读数的相关高不高(低于 0.85/0.90 才算各量各的), 还专门检查理论预期——"装样子"的报道是不是真的更"含糊"。

**为什么需要它**: 一篇严谨的论文不能让人觉得"你这几个文本指标其实在重复量同一个东西"。这一步用判别效度检验给出统计证据: 三把尺子相关都够低、且能合成一个内部一致的量表, 就证明它们是独立有效的测度, 论文可以放心分别使用。

**对最终面板/论文的影响**: 它不改主回归用的面板列(只产摘要表和 JSON), 但它支撑论文方法学部分"我们的清晰度、数字密集度指标和 LLM 实质性判断是可区分的有效构念"这一关键声明。如果检验发现两把尺子高度重叠, 论文就要重新考虑是否同时用、或在稳健性里披露这个重叠。

---

### 39e_lm_discriminant_validity.py

- **注册**: STAGES_VALIDATION(阶段39e)。core/dag.py:423-428 注册 StageSpec(group="validation", kind="audit", timeout=900), 无 enabled_when 挂载 → 取 StageSpec 默认 always_enabled(谓词 lm_discriminant_validity 仍在 core/dag.py:119 的 _VALIDATION_PREDS, 不挂到任何 StageSpec, 仅作纯函数供测试)。core/schemas.py:178 列入 EXPECTED_NO_OUTPUT_STAGES——仅写 eval_reports/*.csv, 无 parquet, 不进 OUTPUT_REGISTRY。
- **底层模块**: pipeline/audit/lm_discriminant_validity.py(入口 main; shim 39e_lm_discriminant_validity.py 调 main())
- **产出**: 仅 eval_reports/*.csv(无 parquet; EXPECTED_NO_OUTPUT)。三轨各写: eval_reports/39e_lm_htmt_matrix_{ctx,full,ss}.csv(6×6 HTMT 矩阵)+ eval_reports/39e_lm_permutation_{ctx,full,ss}.csv(permutation null 单行汇总: obs_htmt_max / perm_htmt_max_mean / perm_htmt_max_p95 / p_empirical / n_perm / n_listwise / note)。注意 eval_dir=output_dir/../eval_reports。不单独落 Cohen κ CSV(本 stage 不算 κ), Cronbach α 仅写日志。ss 或某轨列缺失时该轨不写。
- **三轨**: 三轨各跑一次(循环顺序 ctx→full→ss)。INDICATORS_FULL 6 列经 _full→_ss swap 得 INDICATORS_SS; main spec 用 _ctx(与 P1 v3.6.0 G3 对齐)。compute_htmt_matrix 内 present<2 列时返回空矩阵 → 该轮 continue 优雅跳过(镜像 full/ctx 缺列守卫)。

**详细功能说明**

**输入**: 读 `40_panel_yearly.parquet`(银行-年度面板)。每轨 6 个 indicator: LM 4 子词典频率 uncert_frac / litig_frac / constr_frac / modal_strong_frac, 加 v3.5.1 的 mean_clarity_score、mean_num_intensity(各带 _ctx/_full/_ss 后缀)。panel 缺失时 sys.exit(0) 优雅跳过。

**处理步骤**(`main`):
- `_apply_llm_valid_mask`: 与 39d 统一, 优先 `n_articles_llm_valid ≥ 2`(缺该列回退 n_articles, 两列均缺则不过滤)以保证 HTMT/α/permutation 同样本可比(修 omni-g-audit-family-05)。
- 三轨循环, 每轨: `compute_htmt_matrix` 取 present 列(<2 列跳过)算 `panel[present].corr().abs()`(单 item HTMT 退化为 |Pearson r|); `compute_cronbach_alpha` 跨 6 item α=(k/(k−1))(1−Σσ²_i/σ²_total); `permutation_null` 在 listwise-complete 子样本(观测与 null 同域; len(sub)<4 则跳过)上对每列洗牌 1000 次(seed=42)算 HTMT 上限 null 分布, 报 obs_htmt_max、perm_htmt_max_p95、p_empirical、n_listwise、note(披露行置换未处理 bank 聚类); `_offdiag_max` 用 to_numpy(copy=True) 取非对角最大值(pandas 3.0 Copy-on-Write 下只读数组守卫, 修 P0 崩溃)。
- G-A1.2 准入门控: max off-diagonal HTMT < 0.85 → PASS, 否则 FAIL(need expert audit), 仅写日志。

**关键算法/公式**: Henseler-Ringle-Sarstedt(2015) HTMT 双 cutoff 0.85/0.90; Cronbach(1951) α; 1000-rep permutation(与 39d 基线对齐, Henseler 建议≥500)。预期 6×6 中 LM 4 子集互相及与 clarity/num_intensity 的 HTMT 均<0.85。

**输出**: 上列 CSV; α 与 G-A1.2 判定仅入日志。

**外部依赖/超时/确定性**: 纯 numpy/pandas, 无 sklearn/LLM/Embedding/_llm_cache.db; seed=42; DAG timeout=900(15 分钟, 仿 39d)。

**DAG 位置**: 验证阶段 39e(STAGES_VALIDATION), 上游=stage 40 panel(及上游 LM 子词典/clarity/num_intensity 列), 与 39d 测同一对 clarity/num_intensity 构念但扩到 LM 6 维, 互补不冲突; 服务 G-A1.2 准入门控与论文判别效度披露。

**白话说明**

**这一步在做什么**: Loughran-McDonald(LM)金融词典会给文本贴四类标签——不确定性、诉讼、约束、强语气情态; 我们又加了"表述清晰度"和"数字密集度"两把尺子, 一共 6 个测度。这一步像检查"这 6 个测度是不是各管各的、有没有谁跟谁其实在量同一件事": 它把 6 个测度两两的相关排成一张 6×6 表, 看是不是都低于 0.85; 再用随机打乱一千次确认"这个判断不是碰巧"。

**为什么需要它**: 这 6 个词典/文本指标如果彼此高度相关, 同时塞进回归就是重复计量、会误导结论。这一步设了一个"准入门"(G-A1.2): 只有最大相关低于 0.85 才算通过, 否则要请专家人工复核。它和 39d 测的是同一对清晰度/数字密集度, 用同一套样本过滤, 保证两份报告互相可比。

**对最终面板/论文的影响**: 它不改主回归面板(只产几张 CSV 诊断表和日志), 但它是这些文本指标能否进论文的"安检"。安检通过, 论文可以放心声称这些词典测度各自独立有效; 不通过, 就得砍掉或合并冗余指标, 直接影响论文用哪些自变量、结论的可信度。

---

### 39f_cross_media_alpha.py

- **注册**: STAGES_VALIDATION(阶段39f)。core/dag.py:432-437 注册 StageSpec(group="validation", kind="audit", timeout=3600), 无 enabled_when 挂载 → 取 StageSpec 默认 always_enabled(谓词 cross_media_alpha 仍在 core/dag.py:120 的 _VALIDATION_PREDS, 不挂到任何 StageSpec, 仅作纯函数供测试)。core/schemas.py:179 列入 EXPECTED_NO_OUTPUT_STAGES——确实写 39f_cross_media_alpha.parquet 到 output_dir, 但 validation 类不进 OUTPUT_REGISTRY(与 39c/39d 约定一致)。已核实仅此一件 parquet。
- **底层模块**: pipeline/audit/cross_media_alpha.py(入口 main; shim 39f_cross_media_alpha.py 调 main())
- **产出**: 写 39f_cross_media_alpha.parquet 到 output_dir(三轨 outer-merge 后的 bank-year 面板, 每轨 3 列), 走 validation 约定不进 OUTPUT_REGISTRY。源 parquet(21_tone_llms_full/21_tone_llms)均不存在时 sys.exit(1); 存在但三轨均无有效输出(article 级 tone 列全缺、panels 为空)时不写文件, return 优雅跳过。
- **三轨**: 三轨 full/ctx/ss 各算一次, panel 新增 9 列: cross_outlet_tone_variance_{full,ctx,ss} / cross_media_alpha_{full,ctx,ss} / n_events_{full,ctx,ss}。tone 列由 llm_sentiment_{trk}(正面+1/中性0/负面−1)映射派生(仅当 llm_vote_tone_{trk} 缺且 llm_sentiment_{trk} 存在时); ss=银行+金科同句共现轨, 其 llm_sentiment_ss 缺失时不派生 → 该轨循环优雅跳过。

**详细功能说明**

**输入**: 优先读 `21_tone_llms_full.parquet`, 回退 `21_tone_llms.parquet`(文章级); 两者均缺 → sys.exit(1)。用列: target_bank、日期、媒体(中文)、llm_vote_tone_{full,ctx,ss}(若该列无但 llm_sentiment_{trk} 存在, 则按 `_SENT_TO_TONE`={'正面':1.0,'中性':0.0,'负面':-1.0}(与 encode.py SENTIMENT_MAP 一致)派生数值 tone, 这是 panel 聚合才有的列在 article 级的补派生; 其它标签 → NaN)。

**处理步骤**(`main`):
- `detect_bank_events`: 按 bank-day 计文章数, 取该 bank 的 p90(N_ARTICLE_PERCENTILE=0.90)峰值日(n_per_day≥p90 且 p90>pmin 排除常量分布), 经 `_merge_overlapping_events` 把相邻 gap≤2×window 的传递重叠 ±3d 窗合并为单一 episode(防同文章跨事件重复计入、防 n_events 高估; 修 omni-g-audit-family-01)。
- 三轨循环: `compute_outlet_tone_aggregates` 对每个 (bank,event_date) 在 episode 并集窗内收集 outlet×day 结构(outlet_tones 1D 供方差、daily_matrix 2D 供 α、n_articles 供加权; 要求 outlet 数≥2)。
- `compute_variance_and_alpha`: variance=np.var(outlet_tones, ddof=1)(事件窗条件 outlet 间方差); Krippendorff α(interval scale, reliability_data=outlet×day matrix, NaN 作 missing, 需至少 1 个 item 有≥2 outlets)。
- `aggregate_to_bank_year`: 按 episode 内 n_articles 加权均值聚到 bank-year(修: 旧版误按 n_outlets, 缺 n_articles 列回退 n_outlets+warning), 三轨 panel outer-merge。
- G-D3.1 诊断: valid bank 覆盖 ≥60% → PASS 否则 WARN(仅日志)。

**关键算法/公式**: Krippendorff(2004) α(多评分员、任意尺度, 比 Cohen κ 稳健); Tetlock(2007) 跨源 tone 一致性作信号质量代理; 事件窗 ±3d、min 2 outlets、p90 峰值。

**输出**: 9 列(见三轨段)。⚠ 同名异构披露: cross_outlet_tone_variance_{full,ctx}(注: 披露仅列 full/ctx 两轨)与第 10 篇 bank_media_disagreement paper_spec 冻结的 main treatment **同名但不同构**(本模块=事件窗条件子样本逐 episode 方差再加权; spec=全年无条件截面 outlet 均值的跨 outlet var)——第 10 篇采用前必须对齐 spec 或重命名释放保留名。

**外部依赖/超时**: 依赖 `krippendorff>=0.5.0`(默认在 requirements.txt 注释化, 未装时 α 输出 NaN、仅 variance 可用); 无 LLM/Embedding/_llm_cache.db(只读已落盘 stage 21 + 确定性 _SENT_TO_TONE 派生); DAG timeout=3600(60 分钟, 含事件检测+媒体源聚合)。

**DAG 位置**: 验证阶段 39f(STAGES_VALIDATION), 上游=stage 21 tone_llms, 下游与第 10 篇 bank_media_disagreement 论文重叠(启用前须对齐 spec, 当前仅 validation)。

**白话说明**

**这一步在做什么**: 同一家银行出大新闻的那几天, 不同媒体打出来的语调一致吗? 这一步先找出每家银行"上头条"的高峰日(某天报道数特别多), 把相邻的高峰并成一个"事件", 然后看这个事件窗口里各家媒体的语调差多远。它算两个东西: 方差(各家媒体说法分歧有多大)和 Krippendorff α(把媒体当评分员、看它们打分有多吻合的一个一致性分数)。

**为什么需要它**: 媒体说法越一致, 说明这条情感信号越可靠(不是某一家媒体的偏见); 反过来, 媒体之间的分歧本身也是有价值的信息("媒体分歧度"恰好是第 10 篇论文的核心变量)。这一步既给主线情感测度提供"信号质量"的稳健性证据, 又为媒体分歧那篇论文铺路。

**对最终面板/论文的影响**: 它给银行-年度面板加了 9 列(语调方差、媒体一致性 α、事件数, 三种文本口径各一份)。一个重要警示: 它产的"跨媒体语调方差"列和第 10 篇论文承诺的主变量"名字一样但算法不一样"(这里是"事件窗口内"算的, 论文要的是"全年"算的)——所以第 10 篇真正动用前, 必须先把口径对齐或改名, 否则会张冠李戴、影响那篇论文的核心识别。

---


### 45_panel_export_main.py

- **注册**: STAGES_MAIN(阶段45)。core/dag.py:291-301 StageSpec.name="阶段45 (内含 41+42+43+44+46+47): Bank-Year 面板编排器 — 41 编码聚合 → 42 媒体注意力 → 43 地理缓冲 → 44 Bartik IV/DID → 46 网络溢出 → 47 经纪网络 → 45 诊断与多格式导出", script=45_panel_export_main.py, group=main, kind=panel, timeout=7200。OUTPUT_REGISTRY["45_panel_export_main.py"] 登记 5 个 parquet (schemas.py:74-80)。
- **底层模块**: pipeline/panel/runner.py (入口 main(); shim 17-19 行 import 并调用)
- **产出**: 5 个 parquet 全在 OUTPUT_REGISTRY 登记: 40_panel_yearly.parquet (bank-year 主面板, export.py::export_panel 经 save_dataset 写) + 40_article_bank_level.parquet (article×bank 级, export.py 写 df_exploded) + 40_attn_index_year.parquet / 40_attn_index_province_year.parquet / 40_attn_index_city_year.parquet (三级地理注意力副表, 由 attention_media.py::compute_fintech_attention_index 内 _save_attn_index 落盘; ⚠ year 表无条件写, province/city 两表仅当 df_unique 含 '国家地区/省份' / '城市' 列时才写, 否则该档跳过)。另写 .dta 孪生 (40_panel_yearly.dta / 40_article_bank_level.dta) + .csv (save_dataset 同步产出, 非 OUTPUT_REGISTRY 登记项)。注意: 给外部 Stata 用的全列 .dta 由独立的 stage 46 产出 (46_panel_yearly_full.dta), 不是本阶段。
- **三轨**: 三轨核心承载阶段: 主流程内多处循环 ['_full','_ctx','_ss'] (ss=银行+金科同句轨), VW/MW/HW 加权列、洗稿率、J-F/disag/concern/algo_cater/交互项/四象限/Bartik 基期变体全部三轨产出; ss 缺列 (首跑前) 优雅跳过 (列在则进, 不在则不计入硬警告); export.py::REQUIRED_PANEL_COLUMNS 刻意不含 _ss 列。

**详细功能说明**

**输入**: 主读 `24_herd_decay.parquet` (df_exploded, stage 21 语义精筛后 article×bank 级 verified 集; 缺则 sys.exit(1)); 步骤 7h-token 段硬读 `15_article_alignment.parquet` (policy_cosine_sim; 缺则 raise RuntimeError, 非静默 skip); 步骤 6b `compute_fintech_attention_index` 内读 `12_fintech_news_full.parquet` (全量银行新闻, 注意力分母); 步骤 8c `_merge_optin_feature_panels` 条件 merge `18_staleness_panel.parquet` / `39f_cross_media_alpha.parquet` (含新鲜度 mtime 守卫 + 重复键 fail-loud)。入口处校验关键列 `target_bank` / `llm_sentiment_full` / `日期` / `llm_agreement_rate_full` (runner.py:472, 缺则 sys.exit(1))。

**处理步骤 (runner.main(), 串行子步, StageSpec.name 对应 41→42→43→44→46→47→45)**:
- 步骤2 `encode_sentiment` 篇章级情感数值编码。
- 步骤3 多银行特征 (bank_count/is_multi_bank/in_title); 步骤3b/3c/3d 预计算加权列 — VW(mention_density)/MW(media_authority, +tier 并行列)/HW(herd_weight 三轨独立, 缺则 legacy 单轨退化) × 全测度族, 含 `_build_llm_valid_masked_weights` 的 valid-mask 分母列 (`_wd_*`, 修 encode-01 向零衰减); 步骤3d-2 阈值敏感性 HW (`herd_sensitivity_grid`, 仅施于 LLM 投票主测度)。
- 洗稿率前置: 多方法 (A LLM投票/A2 单LLM/B 反向/D/D2 词典/E/E2 BERT argmax/F 高置信) × 三轨篇章级 `_is_*` 标记 + `_svd_*` subst-valid 分母指示 (+ M2 P3 的 sentiment×subst_ctx `_sc` 4-way)。
- 步骤5 `aggregate_panel` → bank-year panel + `_pool_svd_substvalid_counts` 同域分母聚合; 步骤6 `balance_panel` 笛卡尔积补全 + 6a has_coverage。
- 步骤6b `compute_fintech_attention_index` (比值 ft_attn + 总量 ft_vol, 三级地理, 落 3 parquet); 6b-2 `compute_attention_treatments` (verified 域门控); 6b-3 `compute_dedup_sensitivity_treatments`; 6c `compute_media_heterogeneity`。
- 步骤7 综合指标/7b 截面标准化/7c 地理 merge/7d LOO 情感 IV/7d-geo 地理距离缓冲 (`_m43.compute_geo_proximity_buffers`)/7d-imit 区域模仿渗透 (`compute_regional_imitation_pressure`)。
- 步骤7e Bartik shift-share IV (6 类核心: type/scale/fintech_lf+lc/media/mauth/geoprox; GPSS 2020 pre-treatment 基期 T0=max(year.min,2010), cutoff≤T0 强制 raise; _t0/_t1/_t01 基期敏感性带外生性守卫)。7f 经济圈 LOO (`compute_zone_leave1out`); 7g DID 政策冲击 (`merge_policy_shocks`, DCEP+Sandbox)。
- 步骤7g-het 异质性交互 (Tone×SOE/Scale/HighCov, `_base_year_median_split` pre-period 固定切分, DDD 三重差, stress/depins 断点, lag/reversal/rolling SD 波动率, abnormal_tone 残差 dormant 仅当面板含财务基本面列时产出)。
- 步骤7h 网络族: `compute_network_spillovers`/`compute_bank_network_centrality`(22 中心度)/`compute_cognitive_proximity`/`compute_strategic_differentiation`/`compute_authoritative_similarity`/`compute_benefit_society_panel`/四象限政策对齐(`_classify_policy_quadrants` NaN 掩码 + `_filter_to_verified_universe` semi-join)/`compute_brokerage_centrality`/`compute_industry_neg_shock`/`compute_fire_sale_interaction`/`compute_embedding_peer_network`/`compute_llm_peer_iv`。
- 步骤7h 洗稿率 `_safe_ratio`(分子 pos_symb / 分母 `_svd_denom` substvalid 同域); 7i Janis-Fadner; 8b disag; 8c log_sent(`_gated_log_sent` 零覆盖→NaN); 8d algo_cater; 8e 内联 t2v 双模型存在性诊断 (不读外部 parquet)。
- 步骤8z `compute_iv_extensions`(LOO/广义 Bartik/outlet 构成三引擎 IV 族, 须在全部 merge 之后)。
- `log_diagnostics`(只读) → `export_panel`(REQUIRED_PANEL_COLUMNS 缺列 raise; 物化 low_conf_flag; 写 parquet/csv + sanitize 列名后的 .dta + 启发式标签)。

**关键公式**: J-F: P>N → (P²−PN)/t², N>P → (PN−N²)/t², P=N → 0 (t = n_articles_llm_valid = 正+负+中性有效投票数, 旧 schema 缺该列时回退 t=P+N); disag=√(1−((P−N)/(P+N))²); concern_score=ln_news_coverage×(senti_ratio+1)/2, 其中 senti_ratio=(neg−pos)/(neg+pos); Bartik=Σ_k(base-period share × year-shift)。

**外部依赖**: 本阶段不直接调 LLM (消费 stage 21 缓存产物); 7h-emb/llmpeer + 内联 stage 25/27 含 Sentence-Embedding 相似度 (可能触发 embedding API, 故 timeout=7200 留 buffer)。无 NEWS_PROCESS_LLM_OFFLINE 守卫 (那是 stage 21 的)。

**DAG 位置**: 上游 24_herd_decay(主)+15(硬)+12_full+18/39f(条件); 下游 46_stata_export (读 40_panel_yearly) + 51_falsification (读 40_panel_yearly + 40_article_bank_level + 12_fintech_news_full)。是流水线的扇入汇聚点 (fan-in)。

**白话说明**

**这一步是什么**: 这是整条流水线的"总装车间"。前面各阶段把每一篇新闻都打好了分 (语调、是不是金融科技、跟政策像不像、谁和谁一起被提到), 这一步把成千上万条 article 级的记录按"哪家银行、哪一年"归拢压缩成一张规整的银行-年度表格 (panel), 每家银行每一年一行, 一行里有上千列指标。可以理解为把一大筐零散单据汇总成一张年度报表。

**为什么需要它**: 经济学论文跑回归必须是"银行×年"这种结构化面板, 不能直接喂原始新闻。所有论文最终用的那张数据表就是这里生出来的; 它还顺手算了几十种稳健性指标 (换语调算法、换聚合权重、换工具变量), 让论文能证明结论不是靠某一个口径碰巧。

**做得好不好的影响**: 这一步是承上启下的咽喉——上游任何阶段缺数据它就报错停下 (故意不让它带病生成残缺面板), 避免论文用错误数据跑出假结论。它把"按比例/计数"的分子分母口径对齐、把没报道的银行年份标成"缺失"而不是"零", 这些细节直接决定回归系数是否可信; 一旦这里口径错了, 后面所有表格和结论都会跟着错。

---

### 46_stata_export.py

- **注册**: STAGES_MAIN(阶段46)。core/dag.py:306-311 StageSpec.name="阶段46: Stata 数据导出 (pyreadstat .dta + labels)", script=46_stata_export.py, group=main, kind=export, timeout=600。OUTPUT_REGISTRY 登记 3 个产物 (schemas.py:83-87, filename_key 在 _OUTPUT_FILENAME_KEYS 中均为 None — 即均为 stage 内部副输出, 永用默认文件名, 不可经 paths.yaml 改名)。
- **底层模块**: pipeline/panel/stata_export.py (入口 main() → export_panel_to_stata())
- **产出**: 46_panel_yearly_full.dta (单一全列 .dta, pyreadstat 默认 format version 118; 2026-06-12 起取消 core/aux 双切分) + 46_panel_yearly_labels.do (variable/value labels 的 Stata apply 脚本, 头部带 backend 指纹) + 46_panel_yearly_codebook.xlsx (人类可读变量字典, 含 is_core/original_name 反查列)。三者均在 OUTPUT_REGISTRY 登记。无 parquet 产出 (本阶段是 parquet→Stata 的格式转换层)。
- **三轨**: 三轨在此为透传: 不区分 full/ctx/ss 逻辑分支, 把 stage 45 面板里已有的三轨列原样编码导出; HEURISTIC_LABELS / core_patterns / 类别编码均含 _full/_ctx/_ss 三套键, 但靠 `if col in df.columns` 守卫——实际落盘哪列就给哪列贴标签 (含 _ss), 缺列跳过。另有 `_assert_track_triplet_unique` 写前断言: full/ctx/ss 三轨同一 base 列缩短后不可坍缩到同名。

**详细功能说明**

**输入**: `40_panel_yearly.parquet` (stage 45 产出的 bank-year 全列面板; main() 经 CONFIG['filenames']['output_45_panel_main'] 解析路径, 缺失则 FileNotFoundError)。

**处理步骤 (export_panel_to_stata)**:
1. `_select_dta_backend`: 优先 pyreadstat (嵌入 value labels + 中文 column labels), 缺失则 fallback pandas `to_stata` 并 WARN (两后端 .dta 二进制不等价: pandas 路径不嵌 value label, 须手动 run labels.do; nullable Int 存储宽度也可能不同)。
2. `encode_categorical_columns`: 三套中文类别 str → byte 0/1 + value label —— LOCUS (底层技术=0/应用场景=1)、SUBSTANTIVENESS (实质性=0/象征性=1)、COLLAB_MODE (自主研发=0/外部协同=1), 各覆盖 full/ctx/ss 三轨列名。`_map_categorical_failloud` 对未登记类别值 raise (不静默 NaN 化)。当前 bank-year 面板不含这些文章级 str 列 → encoder 为 no-op (value_labels={}, 诚实披露 fix(omni-g-stata-export-14))。
3. `upcast_unsafe_int8_columns`: 非 value-labeled int8/Int8 计数列升 Int16 (Stata byte 合法值域 [-127,100], 101..127 是缺失码位 `.`/.a-.z, 防 pyreadstat 直写损值)。
4. `shorten_long_column_names`(>32 字符缩写→截断→md5 后缀去重) + `asciify_non_ascii_columns`(中文情感标签 正面/负面/中性 → pos/neg/neu, 残留非 ASCII 移除), 全程同步 value_labels 键 + `rename_map` 链式压平 (`_chase_original` 反查最初原名); 写前跑 `_assert_track_triplet_unique` 三轨唯一性断言。
5. `build_variable_labels`(改名列经 rename_map 反查原名命中 codebook meta / HEURISTIC_LABELS / 列名兜底, 按 UTF-8 字节边界截断 ≤80 字节) → `validate_stata_compat` (列名 ≤32 + 合法 Stata 标识符 + label ≤80 字节)。
6. `assign_core_columns`(STATA_IC_MAX_VARS=2048 守卫分析核心列别膨胀; 2026-06-12 起仅供 codebook is_core 标注, 不再驱动文件切分; 声明却缺席的 pattern 记 WARN 监测 schema 漂移)。
7. `write_dta` 写单一 `*_full.dta`; `write_labels_do_file` 写 labels.do (compound double quotes 安全转义); `_write_codebook_xlsx` 写 codebook (engine='xlsxwriter', 非阻塞, 失败仅 WARN)。

**关键转换规则**: NaN→. (统一 sysmiss, extended missing .a/.b 未实现 — 两后端均不传 missing_user_values); .dta format version=118 (文件格式编号, 非 Stata 应用版本); 列名≤32 + 变量标签≤80 字节。

**外部依赖**: pyreadstat (可选, 推荐) 或 pandas 原生 to_stata; xlsxwriter (codebook)。无 LLM/Embedding/网络。timeout=600 (小面板 ~168 行 < 1 分钟)。确定性: 纯函数转换, 输入 parquet 固定则输出值稳定 (二进制随 backend 选择漂移)。

**DAG 位置**: 上游 stage 45 (40_panel_yearly.parquet); 下游为外部 Stata 研究者 / 11 篇论文的 .do 模板消费 (本机 StataNow/MP 19.5 maxvar≤120,000 直读全列 full.dta)。

**白话说明**

**这一步是什么**: 这是数据的"出关口岸"。Python 算出来的那张大表格 (parquet 格式) 经济学家的 Stata 软件读不了, 这一步负责把它翻译成 Stata 能直接打开的 .dta 文件, 并且给每一列贴上看得懂的英文标签 (比如把 llm_vote_tone_full 标注成媒体乐观度), 再附一份 Excel 字典告诉人每列是什么意思。打个比方: Python 给数据起了很长的名字, 但古老的 Stata 只认 32 个字母的短名, 这一步就是严格的护照审查员, 把长名字安全剪短、防止两列剪短后撞名、再盖上学术标签。

**为什么需要它**: 全世界经济金融论文几乎都用 Stata 跑回归出表。如果没有这一步, 研究者拿到的就是一堆 Python 才认识的文件, 没法直接做实证。它还把缺失值、中文类别、整数溢出这些水土不服的细节统一处理好, 保证 Stata 一打开就能跑。

**做得好不好的影响**: 标签贴得全不全、列名剪得对不对, 直接决定研究者能不能看懂数据、会不会跑错变量。如果两列名字剪短后撞名 (碰撞) 或某列因整数溢出被 Stata 误读成缺失, 回归结果就会悄悄出错却很难发现。它本身不改数据数值, 但它是最终封印——交付给人手里的那份数据干不干净, 全看这一步。

---

### 51_falsification_test.py

- **注册**: STAGES_MAIN(阶段51)。core/dag.py:314-317 StageSpec.name="阶段51: 伪造检验对照变量构建", script=51_falsification_test.py, group=main, kind=falsification, 取默认 timeout=7200。OUTPUT_REGISTRY 登记 51_panel_with_controls.parquet (schemas.py:89, filename_key=output_51_panel_controls)。
- **底层模块**: pipeline/falsification/controls.py (入口 main())
- **产出**: 51_panel_with_controls.parquet (OUTPUT_REGISTRY 登记, filename_key=output_51_panel_controls)。另写未登记孪生: 51_panel_with_controls.dta (sanitize_stata_columns 列名 + build_stage51_variable_labels 共享标签) + 51_falsification_diagnostics.csv (Pearson 相关矩阵, 仅当 run_diagnostics 返回非 None 时写)。
- **三轨**: 三轨在诊断层体现: run_diagnostics 的相关矩阵核心列含 llm_vote_tone_full/_ctx/_ss (ss=银行+金科同句, 缺列优雅跳过, 自动解读循环同样三轨); STATA_LABELS_41 给三轨 prov/city LOO 工具变量列贴标签 (_ss 标签 = 'Bank+FinTech same-sentence')。对照变量本身 (nf_*) 是 track-agnostic 计数指标, 不分三轨。

**详细功能说明**

**输入 (load_data, 三个文件硬读, 缺则 sys.exit(1))**: (a) `12_fintech_news_full.parquet` (stage 12 过滤前全量银行新闻, 与 11_bank_news 逐行 1:1, 含 is_fintech_news 标注; 命名带 fintech 但是全量底库); (b) `40_article_bank_level.parquet` (已进面板的金融科技文章); (c) `40_panel_yearly.parquet` (待挂控制变量的 bank-year 面板)。

**处理步骤 (main)**:
1. `build_non_fintech`(anti-join): Non-Fintech = 全量银行新闻 MINUS 面板文章, 复合键 (target_bank, 标题, _date_str) 双侧 drop_duplicates 后集合差集 (Hassan 2019 QJE Table 7 互补划分); 经 attrs 暴露 `nf_media_breadth_physical`(去重前物理口径 distinct-outlet 媒体广度, 转载计入广度) 与 `ft_dedup_agg`(去重 fintech 计数, fintech_share 同基分子)。
2. `aggregate_non_fintech`: 按 (target_bank, year) 聚合 — nf_n_articles(=count, 去重'同稿件'基) / nf_ln_coverage=ln(1+count)(Fang-Peress 2009) / nf_media_breadth(优先 attrs 物理口径 nunique, 缺则去重基回退) / nf_headline_frac=mean(target_bank_in_title)。
3. `merge_to_panel`: left join 挂面板 + 总量变量 — all_n_articles=ft_dedup+nf(同基, 缺 ft_dedup 时回退物理 n_articles+nf 混合基) / all_ln_coverage / fintech_share=ft_dedup/all_n_articles(分母0→NaN, zero_coverage 指示) / ln_ft_articles & ln_nf_articles(挤出弹性对, 两端同基) + 跨源一致性校验(去重 fintech 计数 ≤ 物理 n_articles 逐行)。
4. `run_diagnostics`: Pearson/Spearman 相关矩阵 (情感三轨 × nf_coverage; |r|<0.3 弱相关支持 H1) + 挤出弹性 r(ln_ft,ln_nf) 机械关联检测; 可用诊断列 <2 时返回 None。
5. `export_results`: save_dataset 写 parquet (input_files 记全 3 个 fan-in 源) + sanitize 列名写 .dta (失败 raise 不 swallow, 先删旧 .dta) + 诊断 CSV。
6. `print_stata_template` (读 papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl) + `print_references`。

**注**: 模块还含三个 main() **未调用**的辅助函数 (供下游/测试): `generate_placebo_did_variables`(G-13 安慰剂时点 DID, 窗口截断于真处理年 [ty-k, ty), Callaway-Sant'Anna 2021) / `diagnose_fintech_classification_consistency`(G-09 收敛效度) / `diagnose_alias_matching_quality`(G-11 别名匹配质量)。

**假设框架**: H0 fintech tone 解释力全来自一般媒体关注度 vs H1 含金融科技特异性增量信息 (Hassan 2019 PRisk/NPRisk 范式)。

**外部依赖**: 无 LLM/Embedding/网络; 纯 pandas/numpy。确定性强。默认 timeout=7200。

**DAG 位置**: 上游 stage 12_full + stage 45 (40_panel_yearly + 40_article_bank_level), 三方 fan-in; 是主链末端阶段, 下游为 bank_fintech_tone 论文的 falsification_template.do 消费。

**白话说明**

**这一步是什么**: 这是给核心结论做打假对照实验的一步。论文想说金融科技新闻的语调对银行有独特影响, 但有人会质疑: 是不是只要新闻多 (不管什么内容) 都有这个效果? 这一步就专门造一个对照组——把所有不是金融科技的银行新闻挑出来 (用减法: 全部银行新闻减掉已算进面板的金融科技新闻), 数一数每家银行每年有多少这种普通新闻、多少家媒体报道过, 当作安慰剂变量挂回面板。

**为什么需要它**: 做对比赛马: 把金融科技语调和普通新闻数量一起放进回归。如果控制了普通新闻量之后, 金融科技语调依然显著, 就证明它确实带了金融科技这一维度的独特信息, 而不只是新闻多的副产品。这是顶刊审稿人必问的稳健性检验。

**做得好不好的影响**: 这一步直接关系到论文核心论点站不站得住。它特别讲究数新闻要用同一把尺子——分子分母如果一个按物理篇数、一个按去重后的稿件数, 算出来的份额就会系统性偏大, 对比就失真。它还把全年没有任何新闻的银行年份标成未定义而不是零份额, 避免污染回归。做得好, 审稿人信服你的指标有独立价值; 做得粗糙, 这道防线一破, 整篇文章的因果解释都会被打问号。

---


### 52_stata_data_audit.py

- **注册**: 未注册 (设计如此): 不在 STAGES_MAIN/STAGES_VALIDATION 中, 编排器永不触发。schemas.py:156-158 注释显式说明排除原因 (orchestrator 不会调 _get_stage_output_files 查它, 故也不列入 EXPECTED_NO_OUTPUT_STAGES)。是 user-CLI wrapper, 由用户在 Stata 导出后按需手动调用。
- **底层模块**: pipeline/audit/stata_audit.py (入口 main(), 返回退出码 1 if 有 FAIL else 0)
- **产出**: 无 OUTPUT_REGISTRY 产出 (审计 CLI, 不进 DAG)。审计运行写 data/processed/eval_reports/52_stata_data_audit.csv (审核摘要表, utf-8-sig) + logs/.../52_stata_data_audit.log (详细日志, 路径由 setup_logging 决定)。
- **三轨**: 三轨体现于审计检查项: 缺失率/值域/情感计数恒等式/加权恒等式均循环 ['_full','_ctx','_ss'], 跨轨道相关做 full-ctx/full-ss/ctx-ss 三对 pairwise; ss 列缺失时该检查项自动跳过。审计本身是只读校验, 不产生轨道分支数据。

**详细功能说明**

**输入**: 读最终交付 Stata 的面板数据 — 40_panel_yearly.parquet 与同名 .dta、51_panel_with_controls.parquet 与同名 .dta (按存在性消费; 40 缺则 error, 51 缺则 warning 跳过该半套审核)。40_article_bank_level 在本模块 docstring 提及但 main() 实际只加载 40/51 两套面板。

**处理步骤 (main, 顶刊级面板审核)**: 对 40 / 51 各跑 9 个 per-file 只读审核函数, 再加 1 个跨文件函数, 共 **10 类**检查 (草稿原列 7 类有遗漏)。经 `record(category, check_name, status, detail, severity='INFO')` 收集 PASS/WARN/FAIL —
1. 面板结构完整性 (`audit_panel_structure`): (target_bank, year) 唯一键 (Wooldridge 2010) + 平衡率 (实际行/理论行 n_banks×年跨度, Baltagi 2021) + 银行名/年份合理性 + 列数。
2. 变量质量 (`audit_variable_quality`): 缺失率/异常值(5σ)/值域合规/哑变量0-1/Inf。
3. 情感指标一致性 (`audit_sentiment_consistency`): pos+neg+neutral frac 恒等、全 *_frac∈[0,1]、情感计数≤物理篇数、三轨 pairwise 相关、LLM 模型间相关、VW/MW/HW 加权恒等式、fintech 分类恒等式。
4. IV 有效性预检 (`audit_iv_variables`): Bartik 份额和≤1(排除 other 类, GPSS 2020)、LOO 排除自身、Bartik IV 变异性。
5. DID 变量合规 (`audit_did_variables`): treated/post 0-1 编码、treated-post 时间逻辑、event-study lead/lag 互斥。
6. Stata 兼容性 (`audit_stata_compatibility`): 列名合规、.dta 可读性/行数一致/数值精度(含 NaN 对齐对称校验)、nullable dtype。
7. 网络变量 (`audit_network_variables`): 中心度列存在性/值域/年度常量校验。
8. 地理变量 (`audit_geography_variables`): bank_province/city 跨年一致性、bank_zone 覆盖率。
9. 描述性统计 (`audit_descriptive_stats`): 核心变量 describe + 零新闻占比。
10. 跨文件一致性 (`audit_cross_file_consistency`, 仅 40+51 均存在时): 行数/键集/核心变量值/51 含 nf_ 列。
汇总 audit_results → DataFrame → to_csv (eval_reports/52_stata_data_audit.csv)。

**外部依赖**: 纯 pandas/numpy 只读; 无 LLM/Embedding/网络。无 timeout 约束 (不在 DAG)。确定性强 (只读校验)。规范调用: `python -m news_process.pipeline.audit.stata_audit` 或 `python news_process/52_stata_data_audit.py`。

**DAG 位置**: 不在 DAG。逻辑上是 stage 45/46/51 的下游质检关卡, 但作为 user-CLI 手动触发, 与流水线主链解耦。

**白话说明**

**这一步是什么**: 这是数据交付前的质检员。当面板表格和 .dta 文件都做好、准备交给经济学家跑回归之前, 这个工具会把它们从头到脚体检一遍: 有没有同一家银行同一年出现两行 (重复)、面板缺了多少格、各种情感指标算得自不自洽、工具变量的份额加起来是不是 ≤1、DID 的处理前后标记有没有搞反、列名符不符合 Stata 规矩、网络/地理变量稳不稳、两张表 (主面板和加了对照变量的面板) 对得上对不上。最后出一张体检报告 (CSV) 列出每一项是通过、警告还是失败。

**为什么需要它**: 流水线自动跑出来的数据可能藏着不易察觉的毛病, 一旦带病进了回归, 论文结果就不可信。这个工具相当于交付前的安检, 把问题拦在送进 Stata 之前, 省得跑出一堆表才发现数据有坑。它是用户想用的时候手动跑的, 不是流水线自动环节。

**做得好不好的影响**: 它不改数据、只挑毛病, 所以不会直接影响面板数值。但它是最后一道人工眼睛: 如果它能抓出重复键、缺失异常、变量不自洽这些问题, 研究者就能在写论文前修好; 如果跳过这一步, 一些隐蔽错误可能一路带到发表。可以理解为买保险——平时用不上, 出事时能救命。

---

### 53_export_stats_excel.py

- **注册**: 未注册 (设计如此): 不在 STAGES_MAIN/STAGES_VALIDATION 中, 编排器不触发。schemas.py:156-158 与 shim docstring 均显式说明排除。是 user-CLI wrapper (描述统计 Excel 导出), 用户按需手动调用; Phase 1.4b 迁移试点 (pilot) 文件。
- **底层模块**: pipeline/audit/stats_excel.py (入口 main())
- **产出**: 无 OUTPUT_REGISTRY 产出 (导出 CLI, 不进 DAG)。运行写 data/processed/各阶段_媒体_地区_城市_统计.xlsx (多 sheet, 每阶段×每字段一个频次分布 sheet)。
- **三轨**: 不适用 (本阶段只对原始元数据字段做频次统计, 与 full/ctx/ss 情感三轨无关)。

**详细功能说明**

**输入**: 按 4 个阶段读对应 parquet 的 3 个元数据列 (columns 限定读, 省内存) — 00_preprocessing / 11_bank_news / 12_fintech_news / 21_tone_llms (文件名经 config['filenames'] 的 output_00_preprocessing / output_11_bank_news / output_12_fintech_news / output_21_tone_llms 解析); 缺文件则 print 跳过该阶段。

**处理步骤 (main)**:
1. Windows 控制台 utf-8 重配 (失败静默 pass)。
2. 对每个阶段 × 每个统计字段 (媒体(中文) / 国家地区/省份 / 城市) 做 `df[col].fillna('(空值)').value_counts().reset_index()`, 列名命名为 [原字段名, 数量]; 字段列不存在则 print 警告跳过。
3. 经 openpyxl ExcelWriter 各写一个 sheet (sheet 名 `{label}_{中文后缀}` 截断 31 字符, Excel 上限), 输出单一 Excel `各阶段_媒体_地区_城市_统计.xlsx`。

**关键算法**: 纯 value_counts 频次分布, 无回归/聚合公式。

**外部依赖**: pandas + openpyxl; 无 LLM/Embedding/网络。无 timeout (不在 DAG)。确定性强。规范调用: `python -m news_process.pipeline.audit.stats_excel` 或 `python news_process/53_export_stats_excel.py`。

**DAG 位置**: 不在 DAG。是横切多阶段的描述性统计便利工具, 由用户手动触发, 与主链解耦。

**白话说明**

**这一步是什么**: 这是个统计小帮手。它把流水线四个关键阶段 (原始预处理、银行新闻、金融科技新闻、LLM 打分后) 的新闻, 按哪家媒体发的、来自哪个省、哪个城市分别数一数各有多少条, 然后整理成一个多页的 Excel 表格, 每一页是一个阶段、一个维度的分布清单。打个比方: 就是把一大堆新闻按媒体/地区/城市分类点名, 做成一份花名册。

**为什么需要它**: 研究者想快速了解我的新闻数据都来自哪些媒体、覆盖哪些地区、各阶段筛选后样本怎么变化, 不用自己写代码, 跑一下就能拿到一份现成的 Excel 概览。论文的样本描述、数据来源说明、附录里的覆盖范围表常常要用到这些数字。

**做得好不好的影响**: 它不参与任何回归计算, 也不改面板数据, 纯粹是给人看的描述性统计。所以它好不好不会影响论文的核心结果, 但它能帮研究者快速发现样本是否偏向某几家媒体或某个地区 (代表性问题), 以及各阶段筛选掉了多少数据。属于了解自己数据家底的辅助工具, 想用就用、不用也不影响主流程。

---

## 核查与计数

本文档经过 **文档 → 对抗核查 → 终审** 三层核对。终审环节亲自 Read `core/dag.py` 与 `core/schemas.py` 后逐条点数, 现将终审的 `count_check` 与 `verdict` 原样附上。

### count_check (终审逐条点数核对)

亲自 Read core/dag.py + core/schemas.py 后逐条点数核对，全部吻合：

STAGES_MAIN (dag.py:164-319) = 15 条：00_preprocessing / 11_news_bank / 12_news_fintech / 13_materialize_ctx / 14_fintech_intensity / 15_article_policy_alignment / 21_tone_llms / 22_tone_words / 23_tone_berts / 24_herd_decay_processor / 30a_article_sbert / 18_article_staleness / 45_panel_export_main / 46_stata_export / 51_falsification_test。= 15 ✓

STAGES_VALIDATION (dag.py:331-438) = 16 条：31 / 32 / 32a / 33 / 34 / 35 / 36 / 37 / 38 / 38b / 39 / 39a / 39c / 39d / 39e / 39f。= 16 ✓ (注：dag.py 文件头注释多处写"全部 14 个验证阶段"指的是历史上挂 _VALIDATION_PREDS 谓词的 14 个，另 32 / 38b 本就无 flag，14+2=16，与 StageSpec 实际条目数 16 不矛盾)。

注册阶段 = 15 (MAIN) + 16 (VALIDATION) = 31 ✓
未注册 = 27c / 52 / 53 = 3 ✓ (Grep 旁证：dag.py 与 schemas.py 中无 27c/52/53 任何 StageSpec 条目；schemas.py:156-158 显式注释排除 52/53)
合计 = 31 + 3 = 34 ✓

旁证一致性：
- OUTPUT_REGISTRY (schemas.py:43-90) = 15 keys，与 15 个 MAIN 阶段一一对应 ✓
- EXPECTED_NO_OUTPUT_STAGES (schemas.py:159-180) = 16 个，恰为全部 16 个 VALIDATION 阶段 ✓
- _OUTPUT_FILENAME_KEYS 与 OUTPUT_REGISTRY 双向覆盖 (import-time 不变式校验 1)，文档逐文件的 filename_key (含 None) 声明与 schemas.py:110-141 全部对得上 ✓

结论：15 / 16 / 31 / 3 / 34 全部=任务给定值，零偏差。

### verdict (终审裁决)

**PASS** — 亲读 core/dag.py 与 core/schemas.py 核对，计数链 15(MAIN)+16(VALIDATION)+3(未注册:27c/52/53)=34、注册阶段=31 全部精确成立；逐文件的注册事实、行号引用、三轨声明、OUTPUT_REGISTRY/EXPECTED_NO_OUTPUT_STAGES 归属与术语跨文件完全自洽，零矛盾零遗漏，无需订正 (file_patches 为空)。

