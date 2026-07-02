# 稳健性缺口补齐执行计划 (ROBUSTNESS GAP BACKFILL)

- **日期**: 2026-07-02
- **状态**: **v3 定稿** (两轮对抗评审: 第一轮 8 视角 37→36 确认; 终审 12 agent 组 20→19 确认, 全部落地; 记录见 §12) → **实施中**
- **目标**: 把全仓"银行金融科技"各子维度测度族的稳健性检验补到"每个核心测度沿每条**适用**的梯子各走一遍"的满配状态; 同时把刻意不做的项显式归档 (含两句话依据), 使覆盖矩阵无未解释空白格。
- **总原则** (继承既有铁律, 全 WP 通用):
  1. 所有新变体轨**互为稳健性、不分主次** (镜像三轨 / co-primary 嵌入 / LLM 三家 / 政治词权重先例); 各变体 just-identified 并排, **禁混进同一 over-identified Hansen J**。
  2. 梯子之间**正交、不交叉** (不做 per-model × polw × 消融 之类的笛卡尔积, 防列爆炸)。
  3. **$0 约束**: 本计划全部 WP 在本机零 API 付费; 任何触发付费的路径一律 DEFER 生产机 + M0 审批门。
  4. **golden 纪律 + 本机不动 parquet**: 本机不重生 golden、**不重放/重跑任何产 parquet 的 stage** (评审 blocker #31: 单独重放 stage 21 会造成 22→23→24→40 级联新鲜度失配); 一切列物化 DEFER 生产机级联重跑。本机验证 = mock/合成 fixture + baseline-stash A/B 差分证 "0 新增失败"。
  5. **提交纪律**: by-name `git add` (排除 `*constants.json` / `eval_reports` / `data/processed` 等并发产物); 绝不 amend / `--no-verify`。

---

## 0. 事实基线 (2026-07-02 三路核查 + 对抗评审补正)

| # | 事实 | 落点 |
|---|---|---|
| F1 | stage 21 每家 LLM 单次响应含全部 4 个 CoT 维度; per-model 分类结果在 `_aggregate_track` (tone_llms.py:1524) 内已解析进 `per_model_parsed` (L1695/1708/1719), 但写 parquet 的 `per_model_cols` 只留 verified/sentiment/conf/prob — **分类维度被丢弃**。⚠ 发列块是 full/ctx/ss **三份手抄副本** (:2515/:2554/:2591), 改列须三块成对改 (镜像留篇门控 2 副本教训) | `pipeline/sentiment/tone_llms.py` |
| F2 | `_llm_cache.db` 三轨 0 miss → `NEWS_PROCESS_LLM_OFFLINE=1` 重放 stage 21 = $0 字节级确定 (**生产机回填用**, 本机不重放, 见总原则 4) | `verify_stage21_cache_coverage` |
| F3 | `_stage21_skip_is_compatible` 只比对窄指纹白名单列。**两面性** (评审补正, 勿只当好消息): ① 回填后的机器 skip 不受新列扰动 (便利); ② **未回填的机器旧 schema 也能通过安检** — 须把新代表列加入 `_STAGE21_REQUIRED_OUTPUT_COLUMNS` (run_pipeline_function.py:343-348, v3.2.0 先例) 堵静默空转漏洞, 否则生产机 `--skip-21-if-exists` 会接受缺 27 列的旧 parquet, 下游 encode `valid_agg` 静默跳过 → 面板列无声缺席 | `run_pipeline_function.py:316-366,466-485` |
| F4 | panel innovation frac 列 (`sub_frac`/`tech_frac`/`collab_frac`…) 全依赖**共识列**, 在 `encode.py::aggregate_panel` (L1277 起) 分组算; per-model tone 聚合范式在 `build_aggregation_dict` L702-707; **per-model tone 在 encode 层按该模型自身 verified=False 置 NA** (encode.py:294-298, 门控先例); `n_articles_llm_valid` = 非空 `llm_vote_score` 计数 (encode.py:849-857) | `pipeline/panel/encode.py` |
| F5 | codebook `_infer_source_stage` 宽前缀已覆盖新 per-model 列 (L2013-2016); 但 `_LLM_MODEL_RE` metric 组 (codebook.py:262-264) 硬编码 tone 族, 且 `_infer_label` per-model 分支 (L1946) 与 `_infer_description` (L1988) **硬编码「语调」文案** — matcher/标签/文案三处须按 metric 分流扩展; 现测试断言 `_llm_model_match('gpt54nano_tone_sub_full') is None` (test_llm_model_robustness.py:78) | `pipeline/panel/codebook.py` |
| F6 | benefit 4 维度只算 full/ctx 是 **plan 层 DEFER 非代码约束**: stage 27 主体循环 `track∈{full,ctx,ss} × suffix∈{'','_lg'}` (benefit_society.py:715-744) 有能力产全部 `.npy`, 盘上已有独立 `27_benefit_direction_lg.npy` 佐证 per-spec 方向向量先例; 锚点嵌入走 LLMCache miss→raise 不调 API; `_benefit_center_sidecar.json` 与维度分解正交不挡路。⚠ dimension_analysis 内**硬编码 full/ctx 共六处**: `_DEFAULT_EMBEDDINGS` L307-311 / merge 校验 L391-394 / argparse choices L519-524 / **CLI main tracks L620 / 方向向量单次 MAIN-only 调用 L625 / track_paths L629-632** (后三处为评审补充, 漏改则 `_lg` 3072 维文本嵌入投影到 4096 维 Qwen 方向直接崩 shape) | `papers/benefit_society/dimension_analysis.py` |
| F7 | 维度列落**孤儿 parquet** `27_benefit_dimensions_panel.parquet`, 不在 OUTPUT_REGISTRY、不碰主 golden; `merge_dimensions_to_panel` fail-loud 拒绝覆盖主面板; ⚠ 其 `track` 参数语义 `'both'`=full/ctx 被 `test_omni_fix_gapfill.py` 4 个用例锁定 (:174/:208-211/:219-221), main() L720 有 `len(tracks)==2 → 'both'` 启发式; **`_lg` 列现无任何桥接路径进 `.dta` 副本** | dimension_analysis.py:359,391-440,720 |
| F8 | parity 测试 `_EMB_FAMILY_PREFIXES` 不含 `benefit_{dim}` 且只扫主面板两 parquet → 维度列现状静默逃逸 parity; dimension_analysis 无 both-or-neither 守卫 | `tests/test_embedding_coprimary_parity.py:33-45,227-239` |
| F9 | boilerplate 单轨 full-only 是语义 DEFER 非数据缺失 (`content_ctx/ss` 已物化); char n-gram DF 统计非嵌入族, 无 `_lg` 需求; 纯 CPU 确定 | `pipeline/sentiment/boilerplate.py:13-14,163,184-186` |
| F10 | herd 的 τ 阈值梯子已物化为面板列 (`herd_sensitivity_grid` τ∈{0.25,0.30,0.40,0.45} → `llm_vote_tone_hw_thr{XX}{track}`); herd 权重公式是计数式 `1/(1+n)` 无半衰期参数; stage 69 刻意固定 3 种衰减函数形式 | `core/config.py:435-458` / `herd_decay.py` / `decay_sensitivity.py:238-255` |
| F11 | num_intensity 句级/词级双分母 × 3 轨已对称满配 | `numerical_intensity.py:431-542` / `encode_collab.py:1048-1164` |
| F12 | lexical_complexity: 文章级列基名 = **`rare_word_ratio{track}`** (lexical_complexity.py:280,427), 面板聚合 = **`avg_rare_word{track}`** (encode.py:779, 两级基名本就不同); `RARE_WORD_PERCENTILE=20` 实测 cutoff=3.0。⚠ **jieba 0.42.1 冻结词典 tie 结构** (代码注释实测): freq=2 约 4 万词、freq=3 约 16 万词, cutoff=3 覆盖分位 P∈(11.6%, 57.25%] 整段 → **分位梯子 {10,20,30} 必然退化** (p30 与 p20 同 cutoff, 列逐字节恒等), 梯子必须在**频次 cutoff 空间**定义 (`_rare_word_cutoff` 排序取索引无去重, L230-234)。forward_looking 双门 (future∧time) 词表外置; news_salience 是二值/解析旗标无阈值 | `pipeline/sentiment/{lexical_complexity,forward_looking}.py` |
| F13 | 根级模板 20 / 总 146。**计数断言实为五处 + 两份 expected 子 .do 清单** (评审补正, 原"三处"漏项): ① `test_papers_b_route.py:176` (146); ② `stata_runner.py:681 _EXPECTED_ROOT_DO=20` (+:676 注释); ③ `test_stata_replication_matrix.py:48` (20) + **:99-110 expected_subdo 硬编码名单**; ④ **`test_stata_templates.py:297` 字面断言 `'20/20 完整'` + :298 `'19/19 子 .do'`**; ⑤ **`stata_runner.py:733-746` verify [5/5] 段 expected 子 .do 硬编码名单 (19 项, +:725 注释)**。master 手工接线 `capture noisily do` + `[WARN]` 对 (00_master:33-77); 残留 `{{FOO}}` → build 崩 (stata_runner.py:392-397); rwolf p 提取 = `e(RW_<iv>)[1,3]` 逐族紧邻提取 (18_substance:60-104 范式)。⚠ **占位符判据 = "⊆ P1 实际绑定集"而非 "∈ _KNOWN_PLACEHOLDERS"**: 根级模板由 bank_fintech_tone 的 effective_choices 实例化, 可替换键仅 `_PAPER_DEFAULTS['bank_fintech_tone']` 7 键 (PAPER_ID/MAIN_DV/CONTROLS/CLUSTER_VAR/HET_VAR/MAIN_TREAT/RANDOM_SEED) ∪ 用户必传 (MAIN_SENT_TRACK 等); `_KNOWN_PLACEHOLDERS` 是全 11 篇并集, 含 TONE_VAR/BARTIK_IV 等 P1 永不绑定键, 用了即 build 全红。⚠ `27_tableA12` 结果矩阵硬编码 **`J(6,1,.)` 容量上限** (:58, 注释"至多 6 模型"), 赋值行无 capture (:80,:106) | `papers/_common/stata_runner.py` / 模板 |
| F14 | policy 列族无根级回归稳健性模板 (23_tableA4 是 radius-κ 非回归); 现覆盖只在 3 个 derivative anchor_robustness 模板 | 核查 §6 |
| F15 | 梯子 gate 测试范式 = 8 类不变量; 范例 `test_political_weight_ladder.py` (含 `test_rule_ablation_ladder.py` 第 4 范例) | `tests/test_*_ladder.py` |
| F16 | **共识列 ≠ per-model 存档标签的裸多数投票** (评审 blocker): ① 共识票池只纳入该模型自身 verified=True 的标签 (`if v:` 门控, tone_llms.py:1691/1704/1717), 而 per-model 存档刻意不门控 (L1684 注释"审计保留原始输出"); ② `final_v_{track}=False` 时共识票池整体清空 → 共识=None 而 per-model 标签保留 (L1773-1777; ctx/ss 轨 conditional-on-full 下大量此类行); ③ locus 共识经 `_resolve_locus_track` (L1196-1216) 混入 canonicalize_topic 关键词交叉验证与回退, LLM 零票时可由关键词证据产标签 — **非纯多数投票** | `tone_llms.py` |
| F17 | 盘面陈旧预存: `75_cross_media_alpha` 产物 mtime 已早于 21_tone_llms.parquet (与本次无关, 防实施时误判为本次回归); stage 21 是**双输出阶段** (`21_tone_llms.parquet` + `21_tone_llms_full.parquet`), 任何备份/还原须**成对** (半对还原 → main/full 代际错配) | 盘面 |
| F18 | (终审补) **D2 聚合点**: `frac_fls` 面板聚合 = `encode_collab.py::apply_v3_5_2` L1486-1494, 契约 dst=src **同名 mean** (非 encode.py:779 的 avg_ 前缀范式); 文章级接线 = `forward_looking.compute_fls_for_text` 返回键 + `tone_words.py:1755-1757` merge 三行 + `:1852-1854` 预分配清单; 满产阈值 L1530-1538。**policy 面板列命名**: full 轨**无 `_full` 后缀** (runner.py:1838-1889 实名: `article_sim_mean` / `_ctx` / `_ss`), 中缀次序 = 基名 + `[_lg]` + `[_allv]` + `[轨]` (如 `article_sim_mean_lg_allv_ss`; **禁**拼成 `*_allv_lg_*` 或 `*_full`) | `encode_collab.py` / `runner.py` |
| F19 | (终审补) boilerplate 的 codebook 条目现在 **`_SINGLE_TEXT_SPECS`** (codebook.py:1313, 键 `avg_boilerplate_full`) 单轨块; stata_export 标签在 :357; `enrich_with_boilerplate` 的调用点 = `tone_words.py:2330-2340` (签名改动须同步)。WP-B 的 CLI 锁定测试面 = `test_omni_fix_gapfill.py` 4 用例 + **`test_papers_benefit_society_cli.py:12-23`** (legacy `--text-embeddings` 别名, F-V2-H2 契约) + **`test_benefit_society_dual_track.py:271-283`** (对 `inspect.getsource(main)` 的 `"--track"`/`"full"`/`"ctx"`/`"both"` 字面断言); 18_table9 模板 L78-81 有硬编码 esttab 候选名单 `cand_models`/`cand_titles` (10 个 full/ctx 估计名) | dimension_analysis 周边 |

---

## 1. 工作包总览与优先级

| WP | 内容 | 成本 | 新列 (面板) | 本机物化? | 优先级 |
|---|---|---|---|---|---|
| A | LLM 分类维度 per-model 梯子 (P3/P4/P5 treatment 的跨厂商稳健) + 27_tableA12 扩 Panel C (A5) | $0 (生产机离线重放) | 文章级 +27, 面板 +27 | **否** — 仅代码+gate mock; 列物化随生产机级联 (§8) | ★★★ |
| B | benefit 4 维度补 `_ss` 轨 + `_lg` 孪生 | $0 矩阵后处理 | 孤儿 parquet +16 (不入主面板) | 视盘上 `.npy` 而定 (缺则优雅 skip, 回填 DEFER) | ★★ |
| C | boilerplate 补 ctx/ss 稳健轨 | $0 纯 CPU | 文章级 +2, 面板 +2 | 否 (随生产机重跑) | ★★ |
| D | D1 罕见词**频次 cutoff 梯子** + D2 forward_looking 单/双门变体 | $0 纯 CPU | D1 +6, D2 +3 | 否 (随生产机重跑) | ★ |
| E | 根级 policy 列族回归稳健性模板 (+1; Panel C 扩展本体在 WP-A A5 / Phase 1, 不在此) | $0 (模板) | 0 | 是 (纯模板/测试) | ★★ |
| F | 文档/铁律/测试/不做清单归档 | $0 | 0 | 是 | ★★★ (随各 WP) |

**明确刻意不做** (§7): herd 半衰期公式族、news_salience 阈值梯子、num_intensity cn2arab 开关、surface_staleness `_lg`、梯子间交叉、per-model 分类的 verified 门控**孪生列**。

---

## 2. WP-A: LLM 分类维度 per-model 互为稳健性梯子

**动机**: `sub_frac` (P3) / `locus_layer` (P4) / `collab_frac` (P5) 三篇论文的 treatment 均出自 LLM 分类共识, 但目前只有共识列; tone 已有三家 per-model 梯子而分类维度没有。补齐后: 共识 = canonical headline, 三家 per-model = co-equal 互为稳健性。

### A1. 文章级: tone_llms.py 补 per-model 分类列

- 在 `per_model_cols` 每家追加 3 维度 × 3 轨 = 9 列/家, 共 27 列; **三份逐轨发列块 (:2515/:2554/:2591) 成对改** (F1):
  - `{short}_subst_{track}` / `{short}_locus_{track}` / `{short}_collab_{track}`
  - 最长 `deepseekv4_collab_full` = **22** 字符 ✓ (≤32; gate 用逐列 `len<=32` 遍历断言, 不做 max==N 单点断言)。
  - 解析源 = `per_model_parsed[f"{short}_innovation_*"]` 已现成, 零新解析算法。
- **口径决策 (评审后钉死)**: 文章级 per-model 列 = **不门控审计存档** (镜像既有 `{short}_sentiment` 先例, L1684 语义; 严禁为凑不变量加 verified 门控)。**门控延迟到 encode 层** (A2, 镜像 encode.py:294-298 tone 先例)。「per-model 存档 ≠ 共识门控票池」口径差写进代码注释 + codebook + manuscript 各一句话 (F16)。
- 缺失哨兵 = None/NaN (勿用 `-1` 类与标签冲突的哨兵)。
- **命名域 SSOT (终审钉死, 消除文章级/面板级两套 token 错配)**: 文章级维度基名 (`subst`/`locus`/`collab`) 与面板 metric 基名 (`sub_frac`/`tech_frac`/`collab_frac`) **无字符串变换可达** — 须在 `encode.py` 立三元映射 SSOT `LLM_CLASS_SPEC = {'subst': ('sub_frac', '实质性'), 'locus': ('tech_frac', '底层技术'), 'collab': ('collab_frac', '外部协同')}` (键=文章级基名, 值=(面板 metric, frac 分子目标类)), `tone_llms.py` 模块级 import 复用 (镜像 codebook import 先例); A1 发列/守卫代表列由**键**派生, A2 面板列与 A4 codebook 正则由**值[0]** 派生, A2 分子目标类由**值[1]** 派生。
- **skip 守卫联动** (评审 major, 与本子项同一提交): 新列代表集由 `LLM_CLASS_SPEC` **键**派生 (钉死为 `gpt54nano_subst_full` / `gemini31_locus_ctx` / `deepseekv4_collab_ss`, 覆盖三模型×三维度×三轨) 追加进 `run_pipeline_function.py::_STAGE21_REQUIRED_OUTPUT_COLUMNS` (:343-348), 更新 v3.2.0 注释块与 reject 消息措辞; `tests/test_run_pipeline_function.py:55` fixture 迭代该常量自动适配 (⚠ fixture 从常量自身造 mock 列, 错名也绿 — 真防线在 A6-② 的跨常量交叉断言)。生产机 DEFER 清单载明: "守卫已收紧, `--skip-21-if-exists` 首跑被 reject → 触发 $0 离线重放回填, 属预期行为非故障"。
- **本机不重放** (总原则 4)。文章级正确性验证 = mock `results_map` 喂 `_aggregate_track`→发列路径的合成 fixture (A6-②); 生产机重放后的验证脚本 (留档 scratch): 对**成对双 parquet** (F17) 旧列逐列 sha256 不变 + 27 新列逐列非空计数 > 0 且与该模型该轨 `{short}_verified{track}` 非空计数同数量级。

### A2. 面板级: encode.py per-model frac 聚合

- `aggregate_panel` 内镜像共识 frac 分组逻辑, 逐模型逐轨产 27 列: `{short}_sub_frac{track}` / `{short}_tech_frac{track}` / `{short}_collab_frac{track}` (最长 `deepseekv4_collab_frac_full` = 27 ✓)。metric 名与分子目标类均由 `LLM_CLASS_SPEC` 派生 (A1), 源列 = 文章级 `{short}_{dim}_{track}`。
- **分子/分母口径 (评审后统一, 消除 v1 的 L69/L74 分歧)**:
  - 分子 = 该模型 `{short}_verified{track}=True` **且**该维度标签为目标类的篇数;
  - 分母 = 该模型 `{short}_verified{track}=True` 的篇数 (per-model 版 `n_articles_llm_valid`, 镜像 encode.py:849-857 判定语义 + encode.py:294-298 门控先例);
  - 允许 sub+symb ≤ 1 的缺标残差, 与共识 frac 结构同构 (可比);
  - codebook/manuscript 披露: "per-model frac 分母是该模型自身 verified 篇数, 而非共识 `n_articles_llm_valid`"。
- **不做** per-model 的互补 frac (`symb/app/indep`)、`_vw/_mw/_hw` 加权变体、ctx 对角变体 (`_sc`/`_cm`) — 防列爆炸 (总原则 2; 面板层不产加权列, 但 stata_export 标签块按全积生成多余键无害, 见 A4)。

### A3. 跨模型一致性统计 (镜像 tone 先例)

- `validation/tone_validation.py` (stage 64) 扩展: 三分类维度逐轨 Krippendorff α (复用 `compute_krippendorffs_alpha`, 名义+缺标感知) + 两两 Cohen κ (中文标签先因子化为非负整数码, 避开 `-1` 哨兵冲突)。输出进 stage 64 eval_report, 不入面板。
- **A3 gate** (终审补, 上一轮同型扩展有 gate 先例, 不得裸奔): 新增/扩展 `tests/test_cross_model_kappa.py` — ① 中文标签因子化后码值全非负; ② 三维×轨 α/κ 产出存在; ③ 缺标 (None) 行为与 2-vs-3 类容错; ④ eval_report 输出键结构锁契约; ⑤ 既有 tone 版测试零扰动。纳入 Phase 1 "A6 gate 绿" 同一闸。

### A4. codebook / stata_export 联动

- `codebook.py::_LLM_MODEL_RE` metric 组扩为 `(cont_mean|cont_sum|tone_sum|tone_std|tone|sub_frac|tech_frac|collab_frac)`; `_PER_MODEL_METRIC_ZH` 补 3 条中文。
- **文案分流** (评审补): `_infer_label` per-model LLM 分支 (L1946) 与 `_infer_description` (L1988, 经 `_LLM_MODEL_NOTE`) 按 metric 族分流 — tone/cont 族保留「LLM 逐模型语调」原文; frac 族改「LLM 逐模型分类占比」+ frac 专用 NOTE。gate 断言: frac 列 label/description **不含「语调」字样**。
- `stata_export.py::build_variable_labels`: 3 个 frac metric 直接加入 `_PM_LLM_METRIC_EN`, **沿用既有 metric×weight×track 全积循环, 不加 per-metric weight 特判** (多余加权键按 L626 口径无害, 仅列存在时被查; 与 `_LLM_MODEL_RE` 可选 weight 组保持同一覆盖域)。英文标签前缀按 metric 分流 (tone 族 'per-model tone…' / frac 族 'per-model share…'); 标签 ≤80 字节。
- 负例保持: `_llm_model_match('gpt54nano_tone_sub_full') is None` 扩正则后实跑复核 (TDD: 先写测试再改正则)。

### A5. FWER: 27_tableA12 扩 Panel C (计数零变动)

- 加 "Panel C: 分类维度跨模型族" — 三模型 `{short}_sub_frac_full` 一族 rwolf, `e(RW_<iv>)[1,3]` 紧邻提取, 占位符沿用 `{{MAIN_DV}}`/`{{RANDOM_SEED}}`/`{{CLUSTER_VAR}}` (禁新占位符)。
- **矩阵扩容 (评审 major, 漏改则生产机整表崩)**: 模板 :58 `J(6, 1, .)` → **`J(9, 1, .)`**, 注释同步 "至多 9 模型 (3 LLM tone + 3 BERT net_tone + 3 LLM sub_frac)" (rownames/切片 L120-121 按 ri 动态裁剪, 扩容无其它联动); 加固 (可选): 赋值前 `if `ri' <= rowsof(`RES')` 守卫使未来扩族 fail-soft。
- Panel C 行名用独立族前缀 `CLS:` (与 `LLM:`/`BERT:` 区分); esttab note 补 "三族各自 rwolf、禁并族" 铁律句。
- gate (入 A6 或模板文本断言测试): 模板含 `J(9, 1` 且 Panel C 块存在。
- 继承性问题沿用: rwolf(reghdfe) 部分版本 rc=111 优雅降级 (capture 防护); 本机 DV wire-ahead 休眠 [SKIP] 属预期。
- paper_spec: P3/P4/P5 补 `cross_model` 声明式条目 (注释写明运行时无消费者, 真检验在根级模板)。

### A6. gate 测试 `tests/test_llm_classification_robustness.py` (镜像 F15 八类)

1. SSOT: `encode.LLM_CLASS_SPEC` 三元映射 (A1) 为唯一源; `LLM_CLASS_METRICS` 若单独存在须 == 映射值[0] 元组 byte-sync; codebook 正则/文案覆盖与映射值[0] byte-sync; `_STAGE21_REQUIRED_OUTPUT_COLUMNS` 新代表列由映射**键** × 代表 (model,track) 派生 (⚠ 禁用面板 metric 名派生文章级守卫列 — 两命名域无字符串变换可达, 错配 → 生产机永久 reject skip 且本机 fixture 自洽全绿抓不到)。
2. 文章级列存在: mock `results_map` 走**真实发列路径** (stage 21 主循环或将三份逐轨发列块重构为 track 参数化 helper — 后者顺带消灭手抄副本风险且不动列序; 若怕漂移则保持三块+mock 主循环), per-track 断言 27 列且非全 None; 共识列不受扰动; **跨常量交叉断言**: 真实发列路径产出的列名集 ⊇ `_STAGE21_REQUIRED_OUTPUT_COLUMNS` 新增代表列 (把"守卫要求的列 stage 21 真会发"固化为本机可红不变量, 堵 test_run_pipeline_function fixture 迭代常量自身的自洽盲区)。
3. 面板聚合: `aggregate_panel` 产 27 列 + 全列 `len<=32` 遍历; 分母=per-model verified 篇数断言; **verified=False 但标签非空的 mock 行零贡献** (不入分子也不入分母)。
4. **一致性锚 (评审 blocker 后重写为条件式, F16)**:
   - (a) `final_v_{track}=True` 行: 对 `{short}_verified_{track}=True` 的模型子集标签做 `majority_vote_categorical(tie_strategy='conservative', empty_fallback=None)` (tie_default 逐维: subst='象征性' / collab='自主研发' / locus='应用场景'), **subst/collab 两维**断言 == 共识列 (含门控票池空→共识 None 情形; 注意空票走 empty_fallback 非 tie_default);
   - (b) `final_v_{track}=False` 行: 反向断言共识列恒 None 而 per-model 标签可非空 (把门控不对称固化为断言, 镜像 L1773-1777);
   - (c) **locus 维排除出严格 reproduction 断言** (共识经 `_resolve_locus_track` 关键词回退, 不可由 per-model 票复现); 改为 import 级单测完整复刻 `_resolve_locus_track(门控票集, topics)` 含关键词回退与空票 (None,0.0) 分支;
   - fixture 必须覆盖两类反例: verified=[T,T,F] + 两 verified 标 null + unverified 标'实质性' → 共识 None; final_v=False 且 per-model 有标签。三点口径差写进测试 docstring。
5. Stata 标签非 fallback ≤80B + frac 列不含「语调」。
6. codebook matcher/label/source-stage + SSOT 全覆盖。
7. 四方 matcher 正交 + `gpt54nano_tone_sub_full` 负例保持。
8. geography 负例: 跨模型 rollup 不吸收分类 frac 列。

---

## 3. WP-B: benefit 4 维度补 `_ss` 轨 + `_lg` 孪生

**动机**: benefit 主测度三轨 × 双嵌入满配, 4 维度分解只有 full/ctx 单嵌入。F6 证实是滞后 plan DEFER, 补齐 = $0。

### B1. dimension_analysis.py 扩轨 (六处硬编码全改, F6)

- **列名 SSOT** (评审补): 新增模块级函数 `_dim_col(dim, suffix, track) -> f"benefit_{dim}{suffix}_{track}"` (suffix ∈ {'', '_lg'}, **lg 中置**, 对齐 `benefit_mean_lg_full` 先例); 生成端 (suffix, track) 双循环 (镜像 benefit_society.py:847-852)、rename map、merge wanted 白名单、B2 守卫、B4 模板变量名**全部经 `_dim_col` 生成** (三方同源防漂移)。
- `_DEFAULT_EMBEDDINGS` (L307-311) 扩六键 `{full,ctx,ss}×{'','_lg'}` 作唯一路径 SSOT (`27_benefit_embeddings{suffix}_{track}.npy`); merge 校验 (L391-394) 与 argparse choices (L519-524) 同步; **CLI main 三处** (L620 tracks / L625 方向向量 / L629-632 track_paths) 改为从 SSOT 派生; `_log_environment_and_config` (L472-473) 遍历派生后 track_paths。
- **CLI 向后兼容硬约束** (终审, 锁定测试面见 F19): ① `--embeddings-dir`/模式串**只能新增**便捷入口, 既有 `--text-embeddings-full`/`--text-embeddings-ctx` 与 legacy 别名 `--text-embeddings` (L526-532, F-V2-H2 契约) 原样保留, 显式传入优先于 dir 派生 (否则 `test_papers_benefit_society_cli.py` argparse SystemExit(2) 顶替 RuntimeError 断言必红); ② argparse `--track` choices 保持**字面列表**形式, 在 `["full","ctx","both"]` 上追加 `"ss"`/`"all"` 字面量, 禁改为纯 SSOT 表达式 (`test_benefit_society_dual_track.py:271-283` 对 `inspect.getsource(main)` 做双引号字面断言); ③ 这两个测试与 test_omni_fix_gapfill 4 用例并列入锁定清单, Phase 5 A/B 差分必含。
- **两轴分工钉死** (终审): `track` 参数只控**文本轨集** (`'all'` = {full,ctx,ss}; `'both'` 保持 = {full,ctx} 向后兼容), `_lg` 后缀由独立 `include_lg` 参数控制; 六轨 = `track='all'` AND `include_lg=True`。
- **空 `_lg` spec 门控** (终审): main() 构造 specs 集时镜像 benefit_society.py:715-717 契约 — `CONFIG.get('embedding_large')` 为空/falsy 时整个 `'_lg'` suffix 从 specs 集剔除 + logger.warning 退化单 MAIN (`_lg` 12 列由 B2 守卫同置 NaN); **禁**把空 dict 传入 `spec_model` 走 Qwen 默认回退 (否则 `_lg` 方向向量以错键查缓存 → RuntimeError 崩整个 CLI 含 MAIN 轨)。
- **陈旧豁免清理** (终审, 同一提交): 删除 dimension_analysis.py 全部 4 处 `# no-ss-track` 标记与 L299-307 两轨说明块, 刷新 banner/docstring/argparse help 的 "ss 延后" 措辞 (其 "无 _ss.npy" 陈述已被盘面/stage 27 能力证伪)。
- **per-spec 方向向量 (评审 blocker #27)**: main() 对每 spec 各调一次 `compute_direction_vectors` — `''` 用 MAIN model/prompt_version; `'_lg'` 用 `spec = CONFIG.get('embedding_large', {})` (普通 **dict**, 禁 `.model` 属性访问) 经 `embedding_engine.spec_model(spec)` / `spec_version(spec)` 取键, 期望二元组 = **('text-embedding-3-large', 'v1-2026-06-27-emb3large')** (字段名 `text_pipeline_version`; **禁沿用 `_resolve_prompt_version()`** — 它硬绑 MAIN 版本号, 传错则 _lg 锚点 100% miss→RuntimeError)。`compute_direction_vectors`/`_get_anchor_embeddings` 已有 `model_id`/`prompt_version` kwargs 并透传, **无需改签名, 只改调用点**。
- 投影配对按 (track, spec) 槽位: `compute_dual_track_dimensions` 保证投影永远用同空间方向向量; **投影入口加显式断言 `text_embeddings.shape[1] == direction.shape[0]`**, 不匹配 raise 带 spec 名的 ValueError (fail-loud, 禁被优雅 skip 吞成静默 NaN)。
- 保留 `.npy` 缺失优雅 skip: 本机缺则该轨跳过, 回填 DEFER 生产机。实施时先 `ls data/processed/27_benefit_embeddings*` 实探盘面。
- **merge 桥接 (评审 major #29)**: `merge_dimensions_to_panel` 的 `'both'` **保持 = full/ctx 向后兼容** (test_omni_fix_gapfill.py 4 个用例零改动); 新增 `track='all'` 承载全六轨 + `include_lg` 参数 (或 wanted 按 dimensions 实有 `benefit_*` 列取交集), 使 `_lg` 列有真实桥接路径 — 否则 B4 Panel D 是结构性死路而非 DEFER。main() L720 的 `len(tracks)==2 → 'both'` 启发式改为直接透传实跑 tracks 并处理剪枝边界。

### B2. both-or-neither 守卫 + parity 纳管决策

- dimension_analysis 内新增族级守卫 (镜像 benefit_society.py:876-894): 每 track 对 `_dim_col(dim,'',t)` vs `_dim_col(dim,'_lg',t)` 恰一侧有效 → 两侧同置 NaN。
- **不**改 `_EMB_FAMILY_PREFIXES` (主面板扫描器扫不到孤儿 parquet, 加了是假保险); 双射断言放 B3 gate。决策写进测试 docstring。

### B3. gate 测试 `tests/test_benefit_dimension_tracks.py`

1. `DIMENSION_INDICES` 10 锚点全覆盖不重不漏;
2. 24 列名 (4 dim × 2 suffix × 3 track) 三方同源 byte-sync: 生成端实际列名 == 守卫端检查集 == `_dim_col` 输出集;
3. both-or-neither 守卫行为 (mock 单边缺失);
4. full/ctx 既有数值与旧版逐字节一致 (canonical 锚, 合成嵌入 fixture 不依赖盘上 `.npy`); **fixture 的 MAIN 与 `_lg` 用不同维度 (如 8 vs 6)**, 使配对错误必炸而非同维静默通过 (评审 blocker 加固);
5. `_get_anchor_embeddings` 对 `_lg` 的**完整缓存键二元组** ('text-embedding-3-large', 'v1-2026-06-27-emb3large') mock 断言; 另加 main()-级接线断言 (mock 到 `compute_direction_vectors`, 断言 `_lg` 轨收到 `_lg` model_id 而非默认 None) — 防"函数能收 spec 但 main 不传"复发;
6. CLI 冒烟: `main(argv=['--track','ss',...])` 配 tmp `.npy` 不 KeyError、缺 `.npy` 优雅 skip 返回 0; `--track all` 实跑轨集覆盖 ss; 可选加 `--merge-panel-output` 走通端到端 (merge 仅在该参数给出时执行, L716);
7. **merge 桥接** (终审补): (i) `track='all'` + `include_lg=True` 时输出恰含全部 24 个 `_dim_col` 派生列 (merge wanted 白名单纳入 B3-2 同源断言方); (ii) `track='both'` 输出与旧版逐列一致的显式回归锚 (既有 test_omni_fix_gapfill 4 用例零改动为 de facto gate, 此为补强); (iii) main() 级: mock 到 `merge_dimensions_to_panel`, 构造剪枝后 tracks={full,ss} 场景, 断言透传实跑轨列表而非 `'both'` (锁 L720 边界);
8. **空 `embedding_large` 降级** (终审补): mock load_config 使 embedding_large 缺失, 断言 main() 返回 0、MAIN 轨列照常产出、无 RuntimeError 且无 ('Qwen/…','v0') 错键缓存查询。

### B4. Stata 模板

- `benefit_society/18_table9_dimension_decomposition.do.tmpl` 扩 Panel C (ss) + Panel D (`_lg` 全轨, **前提 = B1 的 include_lg 桥接已落地**); derivative 子目录模板不动根级计数; 列缺失 `capture confirm variable` 优雅跳过 (wire-ahead)。
- **第四同步点 (终审 major, 漏则新估计静默不出表)**: 模板 L78-81 的 esttab 硬编码候选名单 `cand_models`/`cand_titles` (现 10 个 full/ctx 估计名) 必须**原子成对**追加 ss 与 `_lg` 系估计名/标题 (命名经 `_dim_col` SSOT 派生, lg 中置), 两 local 词数恒等; 修正 L72 "动态化" 注释注明候选侧是硬编码白名单。加模板文本 gate (镜像 A5 J(9,1) 断言): `cand_models` 行含 `_ss` 与 `_lg` 子串, 且 cand_models 词数 == cand_titles 引号组数。
- **README 同步** (终审): `papers/_common/stata_templates/benefit_society/README.md:24` 的 Panel 结构描述行同步 (该 README 经 derivative_replication.py:388 原样进 derivative 复现包, 无测试兜底); Phase 4 grep 残留检查追加 `grep -n 'Panel A full + Panel B ctx' …/benefit_society/README.md` 确认 0 残留。

---

## 4. WP-C: boilerplate 补 ctx/ss 稳健轨

- `boilerplate.py`: 单列改三轨 `boilerplate_phrase_ratio_{full,ctx,ss}` (track 循环取 `content_{track}`, ctx/ss 缺列优雅跳过)。docstring/banner 改写: full = headline, ctx/ss = 稳健性轨; 原语义警示 ("套话集口径在子窗口意义弱") 转为 codebook 解释性限定。
- **调用点联动** (终审): `tone_words.py:2330-2340` 的 `enrich_with_boilerplate` 调用形参适配三轨 + L2330-2333 注释与 L2338 "单轨" 日志散文反转 (签名改动不同步 → TypeError)。
- 面板聚合: encode.py `build_aggregation_dict` :790-791 既有 `boilerplate_phrase_ratio_full` 聚合点, 镜像补 ctx/ss mean。
- **codebook/stata 标签联动** (终审, grep 判据用 `avg_boilerplate` 而非 `boilerplate_phrase_ratio_full`): codebook 的 `avg_boilerplate_full` 条目从 `_SINGLE_TEXT_SPECS` (codebook.py:1313) **迁入** `_DUAL_TEXT_SPECS` 以 base=`avg_boilerplate` 自动发三轨; 迁移不变量 = full 条目发射结果六字段逐字节等价 (⚠ `_DUAL_TEXT_SPECS` 发射 label 为 `f'{_label} ({_tn})'`, base label 须去掉原 '(full)' 后缀); stata_export.py:357 旁镜像补 `avg_boilerplate_ctx/ss` 标签 (≤80B); 可选 `_infer_source_stage` 加 'boilerplate' 子串兜底 (与显式 metadata 二择一写进 gate)。
- `_ss` 回退语义自动继承; 非嵌入族无 `_lg` (CLAUDE.md carve-out 句补 boilerplate)。
- T=18 OOM: docstring 警示 + 生产 DEFER 清单载明, 非本次阻断。
- gate: 既有 boilerplate 测试扩三轨断言 + full 数值不变 (canonical 锚)。列物化随生产机重跑 (本机不动 parquet)。

---

## 5. WP-D: 词典外围测度参数梯子

### D1. 罕见词**频次 cutoff 梯子** (评审后从分位空间改为 cutoff 空间, F12)

- ⚠ v1 的分位梯子 {10,20,30} **不可用**: jieba 冻结词典 tie 结构使 p30 与 p20 同 cutoff=3.0, 变体列与 canonical 逐字节恒等 → 假稳健臂。
- **SSOT**: `lexical_complexity.RARE_WORD_FREQ_CUTOFFS = (2.0, 3.0, 5.0)` — 中值 3.0 ≡ canonical 实测 cutoff (对应现 `RARE_WORD_PERCENTILE=20`; `_rare_word_cutoff` 保留为 canonical 派生, 测试断言其值==3.0 锚死词典漂移); 2.0 ≈ 实测 p10, 5.0 ≈ 实测 p63, 三臂真互异。
- **列名对齐既有族基名** (评审 major: 仓内不存在 `rare_word_frac`): 文章级变体 `rare_word_ratio_c2{track}` / `rare_word_ratio_c5{track}` (canonical 沿用无后缀 `rare_word_ratio{track}`, 不另发重复列); 面板 `avg_rare_word_c2{track}` / `avg_rare_word_c5{track}` (镜像 encode.py:779 契约 `agg[f'avg_rare_word_c{K}{track}'] = (f'rare_word_ratio_c{K}{track}', 'mean')`)。面板 +6 (§1 表已改)。
- 两句话依据 (SSOT 常量, comments/codebook/stata 同源): ① 罕见词频次阈值 3 为研究者选择 (≡ 分位 20 实测值); ② 令 cutoff ∈ {2,3,5} 三者互为稳健性、不分主次, 并披露"冻结词典低频巨量并列使分位→cutoff 映射成段, 故梯子按频次参数化而非等距分位" (与模块 docstring "非高频词率" 定性同源)。
- codebook/export 联动: `_DUAL_TEXT_SPECS` (codebook.py:1228 邻近) 为 `avg_rare_word_c{2,5}` 补显式 metadata (同既有 avg_rare_word 的 source_stage), 或 `_infer_source_stage` 加 'rare_word' 子串兜底 (二择一写进 gate); export.py:673-674 标签块补条目。
- **Phase 0 preflight**: 用 `_get_pristine_tokenizer()` 冻结词典实算三臂 cutoff, 断言两两互异, 任一并列 fail-loud。
- gate `tests/test_rare_word_cutoff_ladder.py` (镜像 polw 八类, canonical 锚 = "以 cutoff=3 重算逐行 ≡ 既有 `rare_word_ratio` 列") **另加两条判别性断言**: 三臂 cutoff 两两互异 (锚死 = {2,3,5}); 合成语料上非 canonical 两臂各自与 canonical 至少一行不同 (防谓词层退化)。

### D2. forward_looking 单/双门变体

- 双门 (future∧time) = canonical `frac_fls{track}`; 新增单门稳健轨 `frac_fls_fonly{track}` (仅 future 词)。面板 +3, **同名直聚合** (F18 契约, 非 avg_ 前缀)。
- **接线点清单** (终审补齐, ⚠ 面板聚合在 encode_collab.py **非** encode.py): ① `forward_looking.compute_fls_for_text` 返回 dict 加 `'frac_fls_fonly'` 键 (复用 `_is_fls_sentence` 拆出 future-only 谓词) + `get_panel_columns` 契约扩为双基名; ② `tone_words.py:1755-1757` merge 块镜像三行 + `:1852-1854` 预分配清单; ③ `encode_collab.py:1486-1494` FLS 聚合环扩为 (`frac_fls`, `frac_fls_fonly`) 双基名循环 (:1526 'fls' 子串判读自动吸收, gate 断言 fls_added 计数 3→6); ④ 满产阈值 L1530-1538 (21→24) 与 :1431/:1408 docstring "21 列/3 列" 文案同步。
- **标签落点** (终审二择一, 取补全族): 为 `frac_fls` 全族 (含既有 3 列) 一并补 codebook curated 条目 + export/stata_export 标签, 顺手偿还既有欠账 (符合 §8 验收 "每条新梯子有标签")。
- 依据: 双门是防弱前瞻句误报的研究者选择; 单门变体证明 FLS 结论不被该门控驱动。
- gate: 既有测试 (test_lm_and_fls / get_panel_columns 契约) 扩断言 (双门列不变 + 单门 ≥ 双门逐行成立 — 超集天然不变量 + fls_added 3→6)。

### D3. Stata 侧

- D1/D2 只做面板列 + codebook 披露, 不进 Table A5 (语义不合); 回归模板留给 paper 层按需 (clarity 是 provisional, wire-ahead 不实例化)。决策记入 §7。

---

## 6. WP-E: 根级 policy 列族回归稳健性模板

- 新建根级 `28_tableA13_policy_family_robustness.do.tmpl`: `article_sim_mean` 为代表的 [vintage vs `_allv`] × [MAIN vs `_lg`] × [full/ctx/ss] 并列回归 (每列一臂 just-identified, 表尾注禁 Hansen J 混用), 列缺失 `capture confirm variable` 优雅降级。
- **列名规格 (终审 blocker: policy 面板列 full 轨无 `_full` 后缀, F18)**: 轨循环用空后缀模式 `foreach sfx in "" "_ctx" "_ss"` (镜像 29_tableA16 无后缀=full 约定); 12 臂实名按 runner.py:1838-1889 拼: `article_sim_mean\`sfx'` / `article_sim_mean_allv\`sfx'` / `article_sim_mean_lg\`sfx'` / `article_sim_mean_lg_allv\`sfx'` (中缀次序 **lg 先、allv 后**; ⚠ 禁 `foreach sent in full ctx ss` 拼出不存在的 `article_sim_mean_full`, 禁拼 `*_allv_lg_*` — 错拼会被 capture confirm 静默吞掉且本机 wire-ahead 休眠不可见)。
- **模板文本 gate** (挂 test_stata_templates 或新 gate): 断言模板文本含裸字面 `article_sim_mean` 与 `article_sim_mean_lg_allv_ss` 两个代表列名, 且 **0 命中** `article_sim_mean_full` / `article_sim_mean_allv_lg` 任一错拼。
- **统一头部** (终审): `version 19` + `set maxvar 32767` + `set linesize 120` 必备; `clear all` 按根级先例 — 若消费 `$bank_controls` 全局 (由 01_data_prep 设置) 则**刻意省略**并加注释 (镜像 27_tableA12/26_tableA7/34_tableA11), 否则保留。写入 Phase 4 验收。
- **占位符判据 (评审修正)**: 只能 ⊆ P1 实际绑定集 (F13: `_PAPER_DEFAULTS['bank_fintech_tone']` 7 键 ∪ 用户必传), 实际建议只用 27_tableA12 先例同款 `{{MAIN_DV}}`/`{{RANDOM_SEED}}`/`{{CLUSTER_VAR}}`; 轨道/列名循环直接硬编码 `foreach sent in full ctx ss`, 不走占位符。⚠ "∈ `_KNOWN_PLACEHOLDERS`" 不是判据 — 它含 TONE_VAR/BARTIK_IV 等 P1 永不绑定键, 用了 build 全红 (stata_runner.py:392-397)。
- **计数联动 = 七联动 + 三文档** (评审 blocker/major 补正, 对齐 tableA12 先例 commit 6805475a 实际改动面):
  1. `tests/test_papers_b_route.py:176` 146 → **147**;
  2. `stata_runner.py:681` `_EXPECTED_ROOT_DO` 20 → **21** (+:676 注释);
  3. `stata_runner.py:733-746` verify [5/5] expected 名单按排序插入 `'28_tableA13_policy_family_robustness.do'` (27_tableA12 与 32_tableA8 之间; +:725 注释 19→20);
  4. `tests/integration/test_stata_replication_matrix.py:48` 20 → **21** (+:42-46 注释);
  5. 同文件 :99-110 `expected_subdo` 名单 + 新 .do;
  6. `tests/test_stata_templates.py:297` `'20/20 完整'` → `'21/21 完整'`; :298 `'19/19 子 .do'` → `'20/20 子 .do'` (:299 'Summary: 8 OK' 不变; 3/5/6 三处必须原子同步);
  7. `00_master.do.tmpl` 加 `capture noisily do "code/28_tableA13_policy_family_robustness.do"` + `[WARN]` 对。
  - 三文档: ① CLAUDE.md CLI 段 "20 个根级" → 21; ② CLAUDE.md Stata Environment 段 "146 个 .do.tmpl" → 147、"主线 20 (含 27_tableA12)" → "主线 21 (含 27_tableA12 / 28_tableA13)"; ③ `papers/_common/stata_templates/README.md` 清单表 + 新行、"20/20 模板完整交付" → "21/21" (该 README 被 build_replication_package 原样复制进复现包, 必须同步)。Phase 4 冒烟后 `grep -n '20/20\|146'` 双文件确认 0 残留。
- `build-replication` 非递归 glob 自动拾取, 无需注册。

---

## 7. 刻意不做清单 (归档 + CLAUDE.md 覆盖矩阵注记, 每项两句话依据)

| 项 | 依据 |
|---|---|
| herd 半衰期 `hl{X}` 变体 | ① herd 权重是计数式 `1/(1+n)` 无时间参数, 引入 exp 衰减是公式族变更(新构念)而非参数变体; ② τ 阈值梯子已物化为面板列 (F10), stage 69 已刻意固定 3 种函数形式避免研究者自由度。 |
| news_salience 阈值梯子 | ① 三信号是二值/解析旗标, 无连续阈值可扫 (F12); ② 覆盖靠 stage 68 媒体多样性审计兜底。 |
| num_intensity cn2arab 开关变体 | ① 双分母 × 3 轨已满配 (F11); ② 分子端守卫是数据清洗正确性而非研究者自由度, 做成开关等于把 bug 口径当稳健臂。 |
| surface_staleness `_lg` | 既有 carve-out: MinHash 非嵌入派生 (CLAUDE.md 铁律已载)。 |
| 梯子交叉 (per-model×polw×消融×N…) | 总原则 2, 防组合爆炸 (polw×消融 3×8 先例)。 |
| WP-A per-model 加权/对角变体 | §2 A2: 保持与共识列单一对应, 加权归共识 headline 族。 |
| **WP-A per-model 分类的 verified 门控孪生列** (评审新增) | ① 文章级存档保持原始输出审计语义 (F16), 门控在 encode 层一次完成 (A2), 面板构念已同构可比; ② 再发一套"写时门控"文章列 = 同信息双份, 防列爆炸; 若审稿要求可后补。 |
| P3/P4/P5 spec 的 fwer 字段接真消费者 | 声明式文档定位不变; 真检验在根级模板 (27_tableA12 Panel C)。 |
| D1 分位命名梯子 | 冻结词典 tie 结构使 {10,20,30} 数学上退化 (F12), 频次 cutoff 参数化是唯一不产假臂的定义域; 若坚持分位命名唯一可行形如 {10,20,60}, 反而更晦涩。 |

---

## 8. 实施顺序与验证闸

**Phase 0 (preflight, 只读)**: ① `ls data/processed/27_benefit_embeddings*` 探盘 (B 组轨道范围); ② D1 三臂 cutoff 实算互异断言 (fail-loud); ③ baseline-stash 全量 pytest 留 A 侧基线 (churn 隔离; F17 的 75 陈旧预存记入基线); ④ (文档性) 生产机回填前提 = `verify_stage21_cache_coverage` 0 miss, 记入 DEFER 清单。

**Phase 1 (WP-A)**: A1 (发列 + skip 守卫 + `LLM_CLASS_SPEC` SSOT) → A2/A4 → A3 (+κ gate) → A6 gate 绿 (全 mock, 本机不动 parquet) → A5 模板 (+J(9,1) 扩容)。预期改动文件: tone_llms.py / encode.py / codebook.py / stata_export.py / run_pipeline_function.py / tone_validation.py / 27_tableA12 模板 / paper_spec×3 / tests×3。
**Phase 2 (WP-B)**: B1 (六处 + per-spec 方向 + merge 桥接 + CLI 兼容) / B2 → B3 gate 绿 (含 `python news_process/scripts/audit/check_static_enums.py` exit 0) → B4 模板 (+cand_models 同步 + README)。预期改动文件: dimension_analysis.py / 18_table9 模板 / benefit_society/README.md / tests×1。
**Phase 3 (WP-C + WP-D)**: 逐 WP 实现 + gate 绿。⚠ **同文件交叠须串行** (终审): WP-C 与 WP-D2 都改 tone_words.py (C=:2330 调用点, D2=:1755/:1852), WP-C 与 WP-D1 都改 encode.py::build_aggregation_dict (C=:790-791, D1 镜像 :779, 同函数相邻); 按文件 ownership 切分或整段串行, **禁双 agent 并行改同文件**。预期改动文件: boilerplate.py / tone_words.py / lexical_complexity.py / forward_looking.py / encode.py / encode_collab.py / codebook.py / export.py / stata_export.py / tests×3。
**Phase 4 (WP-E)**: 模板 + **七联动 + 三文档** → 定向冒烟 `pytest -k "papers_b_route or replication_matrix or stata_templates"` (评审修正: 必含 stata_templates) → `build-replication` 三个代表 paper 实例化 + `verify-replication` 5 段绿 → grep 计数残留。
**Phase 5 (收尾)**: ① 全量 pytest B 侧 → A/B 差分证 0 新增失败; ② ruff; ③ CLAUDE.md 铁律段 + 覆盖矩阵注记 + §7 清单; ④ by-name 提交; ⑤ memory 归档。

**统一验收标准**:
- 全部新 gate 绿; 既有测试 0 新增失败 (A/B 差分口径);
- 每条新梯子有: SSOT 常量 + canonical 复现不变量 (条件式, 见 A6-④) + codebook/stata 标签 + 铁律注记;
- $0 实证: 本机全程不触 API (不重放不重跑产 parquet 阶段);
- **生产机 DEFER 清单** (随提交信息归档): 离线重放 stage 21 (先 verify 0 miss) → **完整级联 21→22→23→24→(26/75 validation)→40→46** (stage 23 前提: `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`, `_local_model_cache.db` 生产机未播种、首跑为全量推理成本) → benefit `.npy` 补产 + dimension_analysis 六轨回填 → boilerplate/D1/D2 列物化 → golden 重生 (PYTHONHASHSEED=0 + BLAS 钉 1) → manuscript prose (per-model 分类口径两句披露 + D1 频次参数化披露)。
- 生产机备份纪律: stage 21 是双输出阶段, 备份/还原必**成对** (`21_tone_llms.parquet` + `21_tone_llms_full.parquet`, F17), 且还原须连 mtime (os.utime), 防半对还原代际错配。

**回滚**: 各 Phase 独立 git revert (本机纯代码+测试+模板, 无 parquet 变更, 回滚零数据风险)。

---

## 9. 风险清单

| # | 风险 | 缓解 |
|---|---|---|
| R1 | 生产机重放意外改旧列 (浮点/顺序漂移) | 重放前后对**成对双 parquet** 旧列逐列 sha256 (排除新列); 漂移即停排查 |
| R2 | per-model frac 分母口径与共识 frac 混淆 → 审稿质疑 | A2 双分母显式披露 + gate 断言 verified 门控与零贡献反例 |
| R3 | `_LLM_MODEL_RE` 扩 metric 撞四方 matcher 正交 | A4/A6 TDD 先写正交测试再改正则 |
| R4 | 27_tableA12 Panel C 撞 `J(6,1)` 容量 → 生产机 rwolf 成功时**整表**中止 (本机 wire-ahead 休眠抓不到) | A5 扩 `J(9,1)` + 注释 + gate 模板文本断言 + (可选) rowsof 守卫 fail-soft |
| R5 | dimension_analysis `_lg` 锚点缓存键传错 → 100% miss RuntimeError | B1 精确二元组规格 + B3-⑤ mock 断言完整键 + 禁用 `_resolve_prompt_version` 于 `_lg` |
| R6 | 计数七联动漏项 → Phase 5 才红 | Phase 4 定向冒烟 -k 含 stata_templates + grep 计数残留双保险 |
| R7 | boilerplate 三轨内存×3 生产 T=18 才炸 | docstring 警示 + DEFER 清单载明, 非本次阻断 |
| R8 | 全量 pytest disk-state flakiness 误判回归 | Phase 0/5 baseline-stash A/B 差分 |
| R9 | D1 未来 jieba 词典变更使 cutoff 梯子并列退化 | gate 锚死 `_rare_word_cutoff()==3.0` + 三臂互异断言, 词典漂移即红 |
| R10 | 生产机 skip 守卫收紧后首跑被 reject 误判故障 | DEFER 清单载明"reject → $0 离线重放回填属预期" |
| R11 | WP-E/B4 模板列名错拼被 `capture confirm` 静默吞掉, 本机 wire-ahead 休眠不可见 | 模板文本 gate 双字面量断言 (§6 与 B4) + 生产机首次出表核对臂数齐全 |
| R12 | A1/A6 两命名域 (文章级 subst/locus/collab vs 面板 sub_frac/tech_frac/collab_frac) 错配 → 守卫列 stage 21 永不发 → 生产机永久 reject skip | `LLM_CLASS_SPEC` 三元映射单源 + A6-② 跨常量交叉断言 (发列集 ⊇ 守卫代表列) |

---

## 10. 多智能体编排安排 (实施期)

- **计划评审**: 已完成 (§12)。
- **实施**: 按 Phase 串行, Phase 内独立文件改动可并行 agent; 每 Phase 结束跑定向 gate。
- **终审**: 实现结果 break-it 评审 (镜像 strat_diff top-k 先例的 ok_to_commit 门) → A/B 差分 → 提交。

## §11 实施记录 (2026-07-03 回填)

- [x] **Phase 0**: 六个 benefit `.npy` 全在盘 (1005×4096 / 1005×3072); D1 三臂 cutoff 实测互异 (2.0→11.6% / 3.0→57.2% / 5.0→63.4%, canonical==_rare_word_cutoff()==3.0); A 侧基线 = 27 个既有失败 (golden 分叉 + cohort CSV + locus/substance output 目录 + val_mask/_TABLE1 契约债 + jieba isolation, 全部与 memory 记载一致)。
- [x] **Phase 1 (WP-A)**: A1 发列 (三份逐轨块+init, `_LLM_CLASS_SPEC` try-import encode + fallback) / A2 **实现偏差 (更优)**: 门控指示列在 `encode_sentiment` (`{short}_{metric}_src{track}`, 镜像 per-model tone 门控先例) + `build_aggregation_dict` mean, 语义 ≡ 计划的分子/分母口径 / A3 tone_validation 扩展 + `test_cross_model_kappa` +14 用例 (agent 实施) / A4 codebook 正则+文案分流+`_LLM_CLASS_NOTE`, stata_export `share` 措辞 / A5 Panel C + `J(9,1)` + `CLS:` 前缀 + note 三族句 / A6 `test_llm_classification_robustness` 26 用例 (含条件式一致性锚两类反例 fixture、跨常量交叉断言、三副本文本锁、A12 文本 gate)。skip 守卫 +3 代表列。paper_spec P3/P4/P5 +cross_model 声明。**本机未重放 stage 21** (级联纪律)。
- [x] **Phase 2 (WP-B)**: B1 六处硬编码 + `_dim_col` SSOT + per-spec 方向向量 (`_spec_cache_keys`) + 空 `_lg` spec 剔除降级 + CLI 兼容 (legacy 别名/字面 choices 保留, +`--track ss/all` +`--include-lg` +`--text-embeddings-ss` +`--embeddings-dir`) + `# no-ss-track` 豁免全清 / B2 `_apply_both_or_neither` / B3 `test_benefit_dimension_tracks` 17 用例 (MAIN=8 维 vs _lg=6 维 fixture) / B4 18_table9 Panel C/D + cand_models/titles 30/30 + benefit README (gitignored 本地文件)。**超计划**: 本机真实回填孤儿 parquet (24 列 × 143 bank-year, `_lg` 锚点离线全命中 $0)。check_static_enums 本文件 0 命中 (其它文件既有命中非本次)。
- [x] **Phase 3 (WP-C/D, 串行)**: C boilerplate 三轨 (canonical 形参对回兼 + ctx/ss 固定槽) + tone_words 调用点 + encode 三轨聚合 + codebook 迁 `_DUAL_TEXT_SPECS` (full label 逐字节同) + stata 标签; D1 `RARE_WORD_FREQ_CUTOFFS=(2,3,5)` + 变体列/聚合/codebook/标签 + `test_rare_word_cutoff_ladder` 12 用例 (真实词典判别性断言); D2 `_fls_gates` 拆分 (canonical 语义逐字节保持) + 四接线点 + 阈值 21→24 + FLS 全族标签补录 + 超集不变量测试。
- [x] **Phase 4 (WP-E)**: 28_tableA13 (空后缀轨循环, 12 臂实名, `$bank_controls` 省略 clear all, 无终端 exit) + **七联动** (papers_b_route 147 / _EXPECTED_ROOT_DO 21 / verify expected 名单 / matrix 21+expected_subdo / test_stata_templates '21/21'+'20/20' / 00_master 接线) + **三文档** (CLAUDE.md CLI 段+Stata 段 / templates README 21/21) + 两个模板文本 gate。冒烟: build-replication P1 (21 .do) + benefit derivative (27 .do, Panel D 列实例化) + verify-replication 8 OK + 占位符/计数 0 残留。
- [x] **Phase 5**: 全部改动 py 文件 ruff 干净; **A/B 差分 = 27↔27 逐条相同, 0 新增失败 0 转绿**; CLAUDE.md 铁律段 +"稳健性缺口补齐"块; 终审 break-it 工作流 (6 视角 + 对抗核实) 见 §12c。
- **生产机 DEFER 清单最终版**: ① `verify_stage21_cache_coverage` 0 miss → `NEWS_PROCESS_LLM_OFFLINE=1` 重放 stage 21 (双 parquet 成对备份+还原含 mtime; 守卫收紧后 `--skip-21-if-exists` 首跑 reject 属预期) → 完整级联 21→22→23→24→(26/75 validation)→40→46 (stage 23 前提 HF_HUB_OFFLINE=1/TRANSFORMERS_OFFLINE=1; `_local_model_cache.db` 未播种首跑为全量推理); ② boilerplate ctx/ss + D1 c2/c5 + D2 fonly 列随级联物化 (boilerplate T=18 前须分块改造, 见模块 P1 TODO); ③ golden 重生 (PYTHONHASHSEED=0 + BLAS 钉 1, 排除 3 网络列); ④ manuscript prose: per-model 分类分母口径两句披露 + D1 频次参数化披露 + FLS 单/双门披露; ⑤ Table A12 Panel C / A13 12 臂在 T=18 财务数据到位后首跑核对臂数齐全 (R4/R11)。

## §12b 终审记录 (2026-07-03, v2→v3)

- 工作流: 4 忠实性核查 (36 条前轮意见逐条落地对照) + 8 全新视角干跑 (逐 WP 打开每个点名位置模拟实施 / 事实复核 / 内部一致性 / 跨 WP 冲突 / 完备性) + 逐条对抗核实 (32 agents)。
- 结果: 20 findings → **19 确认 / 1 驳回**, 全部落地 v3。最重要修正:
  1. **[blocker] WP-E 列名**: policy 面板列 full 轨无 `_full` 后缀 — 轨循环改空后缀模式, 加模板文本 gate 防 capture 静默吞臂 (R11);
  2. **A1/A6 命名域错配**: 文章级 (subst/locus/collab) 与面板 (sub_frac/tech_frac/collab_frac) 两套 token 无字符串变换可达 — 立 `LLM_CLASS_SPEC` 三元映射 SSOT + 跨常量交叉断言 (R12);
  3. **D2 聚合点纠正**: frac_fls 在 encode_collab.py::apply_v3_5_2 同名 mean (非 encode.py avg_ 范式), 补 4 处接线点与阈值/文案联动 (F18);
  4. **B1 CLI 兼容**: legacy `--text-embeddings` 别名与 `--track` 字面 choices 被两个既有测试锁定, 禁替换/派生化; 空 `embedding_large` spec 须剔除 `_lg` 而非默认回退; 补 merge 桥接三断言 + `# no-ss-track` 陈旧豁免清理;
  5. **B4 第四同步点**: 18_table9 的 esttab 硬编码 cand_models/cand_titles 名单 + benefit README; **WP-C**: codebook 条目从 `_SINGLE_TEXT_SPECS` 迁 `_DUAL_TEXT_SPECS` + tone_words 调用点;
  6. A3 补 κ gate; Phase 3 同文件交叠串行纪律 + 各 Phase by-name 预期文件清单; 28_tableA13 统一头部条款; §1 归属唯一化 (Panel C 属 WP-A)。

## §12 计划评审记录 (2026-07-02)

- 工作流: 8 视角 (计数/缓存/命名/计量/测试/encode 链路/benefit/break-it) 并行找茬 → 每条 finding 独立对抗核实 (45 agents)。
- 结果: 37 findings → **36 确认 / 1 驳回** (驳回项: WP-C/D 既有测试硬冲突 — 核实为不成立)。
- 确认项全部落地本版, 最重要的方向性改动:
  1. **本机不重放 stage 21** (v1 计划的本机重放会引发 22→40 级联失配, 改为生产机级联 DEFER);
  2. **A6 一致性锚从"裸多数投票==共识"改为条件式** (verified 门控 + final_v 清空 + locus 关键词回退三重语义, F16);
  3. **A2 分母口径钉死** = per-model verified 篇数 (镜像 tone encode 门控先例);
  4. **D1 从分位梯子改为频次 cutoff 梯子** (分位空间在冻结词典上数学退化);
  5. **B1 补 per-spec 方向向量与 CLI main 三处硬编码** (防 4096×3072 维度崩) + merge 桥接 (`'both'` 向后兼容 + `include_lg`);
  6. **WP-E 计数从"四联动"扩为七联动 + 三文档** (含 test_stata_templates 字面断言与两份 expected 名单);
  7. 27_tableA12 `J(6,1)` 扩容 `J(9,1)`; skip 守卫 `_STAGE21_REQUIRED_OUTPUT_COLUMNS` 收紧; 列名基名对齐 (`rare_word_ratio`/`avg_rare_word`)。
