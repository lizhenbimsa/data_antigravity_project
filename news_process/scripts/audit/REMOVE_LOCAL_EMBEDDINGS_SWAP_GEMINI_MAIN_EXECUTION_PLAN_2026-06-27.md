# 执行计划：移除本地嵌入模型（text2vec / bge-m3）+ MAIN 槽切换到 `gemini-embedding-2-preview` + 激活 `text-embedding-3-large`(`_lg`) 作 **co-primary 对等双轨**

> 版本目标：**v3.14.0 · BREAKING · all-API-embedding**
> 状态：**计划定稿，待批准实施**（撰写计划阶段；尚未改任何代码）
> 撰写日期：2026-06-27 ｜ 作者：Claude（基于 8-agent inventory workflow + yunwu 实测探针）
> 前置基线：HEAD = `7b7cf3a1`（v3.13.0 quad-model-embedding）

---

## 0. 决策表（2026-06-27 用户锁定，四问拍板）

| 代号 | 决策 | 终值 |
|---|---|---|
| **D-1** | `_t2v`/`_bge` 处置方式 | **硬删除（代码 + 列 + config + golden + npy + 文档）**，非 config-gated 休眠（直接兑现"删除及其实现"指令） |
| **D-2** | text2vec 删除**范围** | **彻底移除 text2vec 模型** —— 连 stage 25 语义陈旧度 + stage 15 金科强度的 text2vec **功能骨干**一起改造；**项目此后不加载任何本地嵌入模型** |
| **D-2a** | stage 25/15 功能测度替代方案 | **选项 (i) 改 API 嵌入**（保真），且用 **gemini + `text-embedding-3-large`(`_lg`) co-primary 双轨"互为稳健性检验"** —— 把全管线 co-primary 双轨**统一扩展到 staleness 与 intensity**（此前二者是 text2vec 单模型、无 twin）|
| **D-3** | MAIN 槽（无后缀 canonical 列）| `text-embedding-3-small`(1536) → **`gemini-embedding-2-preview`(3072)**，base_url 仍 `https://yunwu.ai/v1` |
| **D-4** | 嵌入主轨架构 | 删两本地轨 + **gemini 与 large 并列 CO-PRIMARY**：`gemini-embedding-2-preview` 与 `text-embedding-3-large` **同为主测度、互为稳健性**（跨厂商 Google⟂OpenAI），**地位对等**；`_lg` 后缀仅为列命名机制（同名冲突回避），**无层级含义**（非"主轨 + 稳健检验"）|
| **D-5** | 预览版复现风险 | **纯按指示**用 `-2-preview`，**不加**应急回退/复现保险机制；计划仅**如实披露**风险（顶刊诚信） |

> ✅ **D-4a（2026-06-27 用户补充拍板）**：gemini 与 large **严格 parity（双射）** —— **任何**产 gemini（无后缀）嵌入列的地方**必同时**产 large（`_lg`）孪生列，反之亦然，**无一例外**（5 cosine producer × 3 轨 + `_allv` + staleness + intensity）。两者 co-primary、互为稳健性、地位对等（**非"主 + 稳健检验"**）。新增 **parity 不变量测试**（§11/§13）强制 bijection（每个无后缀嵌入列 ⟺ 恰一个 `_lg` 孪生）。**铁律不变**：两 co-primary 各自 just-identified 并排报告（互证一致性），**禁混进同一 over-identified Hansen J**。
> 🔧 **命名澄清（防churn）**：保留项目既有"无后缀 = canonical 列槽 + 后缀 = 孪生"约定 —— gemini 占无后缀槽、large 占 `_lg` 槽，**纯为列命名机制**（panel 不能两列同名），**后缀不表达任何主次/优劣**；下游所有 no-suffix 列名零改动（避免全列改后缀的巨churn）。manuscript/codebook/stata 标签须以"co-primary 对等互证"表述，**不得**称 large 为"robustness check / 稳健性附录"。

> ⚠ **D-2 是本计划体量的决定因素**：它把任务从"列内缩减"升级为"测度变更 + 架构转向"。staleness 与 fintech_intensity 是**功能性测度**（非稳健轨），改造它们必然**改变这两个测度的数值**，并触发 golden 大改。
> ✅ **D-2a（2026-06-27 用户补充拍板）**：staleness 与 intensity 不仅迁 API，还各获 **gemini(MAIN) + large(`_lg`) 双轨**——使**全管线所有嵌入派生测度统一为 MAIN+`_lg` 跨厂商双轨**，无任何单模型测度。这强化了稳健性论证（连 staleness/intensity 也有跨厂商对照），但**生产嵌入成本 ×2**（每篇文章嵌两个 API 模型）。

---

## 1. 目标架构（变更前 → 变更后）

### 变更前（v3.13.0，四模型）
| 轨 | 模型 | 后缀 | 路径 | 维度 |
|---|---|---|---|---|
| MAIN | text-embedding-3-small | 无 | API/yunwu | 1536 |
| ROBUSTNESS-A | shibing624/text2vec-base-chinese | `_t2v` | **本地** | 768 |
| ROBUSTNESS-B | text-embedding-3-large | `_lg` | API/yunwu（休眠） | 3072 |
| ROBUSTNESS-C | BAAI/bge-m3 | `_bge` | **本地** | 1024 |
| 功能骨干① | text2vec（stage 25 SBERT → 陈旧度） | — | **本地** | 768 |
| 功能骨干② | text2vec（stage 15 金科质心） | — | **本地** | 768 |

### 变更后（v3.14.0，双 API 模型 · 零本地模型 · **co-primary 对等双轨**）
| 角色 | 模型 | 列后缀（仅命名机制）| 路径 | 维度 |
|---|---|---|---|---|
| **CO-PRIMARY ①** | **gemini-embedding-2-preview**（Google）| 无（canonical 列槽）| API/yunwu | **3072** |
| **CO-PRIMARY ②** | **text-embedding-3-large**（OpenAI，激活）| `_lg`（孪生列槽）| API/yunwu | 3072 |
| 功能骨干① staleness（stage 25→26）| **gemini + large co-primary 双轨** API 嵌入（D-2a 选项 i）| 无 / `_lg` | API/无本地 | 3072 |
| 功能骨干② intensity（stage 15）| **gemini + large co-primary 双轨** API 嵌入词表质心 | 无 / `_lg` | API/无本地 | 3072 |

> 变更后**全管线统一 gemini ⟂ large 跨厂商 co-primary 双轨**：5 个 cosine producer、staleness、intensity 全部双轨，**严格 parity（每个无后缀嵌入列 ⟺ 恰一 `_lg` 孪生）**，无任何单模型嵌入测度。后缀 `_lg` **仅为列命名机制、无主次含义**（D-4 命名澄清）。

### 稳健性论证的**诚实转变**（manuscript 必须披露）
- **丢失维度**：`_t2v`（中文专训）/`_bge`（本地多语言）提供的"**本地 / 中文专训 / 跨架构独立性**"——审稿人质疑"结论是否只是某 OpenAI 模型的偶然产物"时，原有本地独立轨作答。**此维度被删除后不复存在。**
- **保留 / 新增维度**：gemini（Google）⟂ text-embedding-3-large（OpenAI）= **跨厂商 / 跨训练数据独立性**，二者 **co-primary 对等互证**（非"主 + 稳健检验"）。
- ⚠ **纠正 inventory 综合稿口误**：8-agent inventory workflow（task `wth0fmrzl`）综合稿 §4-(c) 称 "_lg 与 gemini 同 OpenAI-family、同维度→近重复"。**这是错的**——`gemini-embedding-2-preview` 是 **Google**，`text-embedding-3-large` 是 **OpenAI**，二者**跨厂商**；维度同为 3072 与稳健性无关（余弦本就维度无关）。故 D-4 激活 `_lg` 是**有效的跨厂商稳健性**，并非冗余。**但**它无法替代被删的"本地 / 中文专训"独立性维度——论文须如实定位为"跨厂商"而非"跨架构 / 跨语言专训"稳健性。

---

## 2. 关键技术事实（2026-06-27 yunwu 实测探针，非推断）

| 事实 | 实测结果 | 对计划的含义 |
|---|---|---|
| gemini 经 yunwu 可达 | ✅ `https://yunwu.ai/v1/embeddings`，OpenAI-compat `{"model","input"}` 格式，**返回 3072 维单位归一向量** | base_url / auth / 引擎 API 路径**零改动**，仅换 model 名 |
| gemini token 限制 | ✅ **0–8191 cl100k token 全区间无报错**（8191 cl100k ≈ 4707 gemini-token） | 引擎 `EMB_MAX_TOKENS=8191` + cl100k 切块**保留不动**（cl100k 对 gemini 是**保守高估** → 批次偏小、永不超限；超长文走既有 mean-pool 分块，每块 gemini 均接受） |
| GA 版 gemini-embedding-001 | ❌ **yunwu 上不存在**（只有 `-2-preview`） | 无稳定 GA 替代 → D-5 预览版复现风险**无法用 GA 规避**（已锁定纯按指示） |
| task_type / dimensions 字段 | ❌ OpenAI-compat 路径**不透传** | gemini 原生 `SEMANTIC_SIMILARITY` task_type 无法指定 → 见 §6 方法论 caveat（须实测 corr 验证余弦有效性） |
| `text-embedding-3-large`（`_lg`） | ✅ 3072 维可用，model echo 正确 | D-4 激活可行 |

> 探针脚本留存：`scratchpad/probe_gemini.py` / `probe_embed.py` / `probe_limits.py`（一次性，不入库）。

---

## 3. 影响面 A：移除 `_t2v` + `_bge`（精确锚点，已对源码核验）

> 模式：每个 producer 有模块级 `_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})` + `_BGE_SPEC = CONFIG.get('embedding_bge', {})`，后接 `if _SPEC:` 门控的列计算。删除 = 删两个 spec 声明 + 其全部计算/赋值/落盘/校验，**保留 MAIN 与 `_LARGE_SPEC`（`_lg`）**。

### 3A. Producer（删 `_t2v`/`_bge` 分支，留 MAIN + `_lg`）
| 文件 | 锚点（实测，BGE 落地后可能微移，实施时复核） | 动作 |
|---|---|---|
| `pipeline/features/benefit_society.py` | `_ROBUSTNESS_SPEC`~L122 / `_BGE_SPEC`~L130 / **留 `_LARGE_SPEC` L126**；`_specs=[('',EMBEDDING_CONFIG),('_t2v',_ROBUSTNESS_SPEC)]`~L713 + `if _BGE_SPEC:` append；`.npy` 落盘 `_t2v`/`_bge` | 删两 spec；`_specs` 收为 `[('', EMBEDDING_CONFIG)]` + 留 `if _LARGE_SPEC: _specs.append(('_lg',...))`；删 `_t2v`/`_bge` npy save/load |
| `pipeline/features/strategic_diff.py` | `_ROBUSTNESS_SPEC`/`_BGE_SPEC`~L281/283 / **留 `_LARGE_SPEC` L282**；`_build_embedding_sim_matrix(spec=…)` + `_compute_emb_coherence` 的 `_t2v`/`_bge` 调用；列 `strat_diff_n5_emb_t2v`/`strat_sim_max_emb_t2v`/`centroid_diff_emb_t2v`/`coh_emb_t2v_*`/别名 `strat_diff_t2v_*` | 删 `_t2v`/`_bge` spec + 全部 sim-matrix/coherence 调用 + 列赋值（含 full/ctx/ss 三处 `_sub_tracks`）|
| `pipeline/features/policy_similarity.py`（stage 26）| `_ROBUSTNESS_SPEC`/`_BGE_SPEC`~L82/88 / **留 `_LARGE_SPEC` L85**；`_build_indicators` 的 `emb_t2v` 键 + try/except；`auth_sim_emb_t2v_*`/`_bge_*` + `_allv` | 删 `emb_t2v`/`emb_bge` 键、try/except、全部 `auth_sim_*_t2v/_bge` 赋值 |
| `pipeline/filtering/policy_alignment.py`（stage 15 政策对齐）| `_ROBUSTNESS_SPEC` L147 / `_BGE_SPEC` L155 / **留 `_LARGE_SPEC` L151**；`_cosine_for_spec(spec=_ROBUSTNESS_SPEC/_BGE_SPEC)`；`policy_cosine_sim_t2v_*`/`_bge_*` + `_allv` | 删两 spec + 全部 `_t2v`/`_bge` cosine 调用 + 列赋值 |
| `pipeline/panel/network_spillover.py`（stage 46）| `_ROBUSTNESS_SPEC`/`_BGE_SPEC`~L1440/1447 / **留 `_LARGE_SPEC` L1444**；`emb_peer_tone_lag1_t2v_*`/`bank_emb_sim_mean_lag1_t2v` + `_bge`；⚠ `if not _ROBUSTNESS_SPEC: return` 早退守卫 | 删 `_t2v`/`_bge` 块；⚠ **死代码陷阱**：删 `_t2v` 块及其早退守卫后，确保 `_lg` 块仍**无条件可达**（勿留在被删守卫之后）|
| `pipeline/features/benefit_society_alt_anchor.py`（stage 27c，**consumer/validator，非 producer**）| `_check_anchor_model_consistency` 迭代 `("embedding_api","embedding_robustness","embedding_large","embedding_bge")`；消费 `27_benefit_embeddings_t2v_*.npy` | 迭代元组删 `embedding_robustness`/`embedding_bge`；删 `_t2v` npy 载入；**先删码后删文件**（防 FileNotFoundError）|

> 注：上表 7 行中，**producer 计 6**（5 cosine producer + `fintech_intensity`，Phase 3 "6 个"）；`benefit_society_alt_anchor`（stage 27c）是 **consumer/validator**（消费 `_t2v` npy + 校验锚点一致性），非 producer，不计入 6。
| `pipeline/filtering/fintech_intensity.py`（stage 15，**D-2/D-2a 功能骨干**，非 `_t2v` 列）| `EMBEDDING_MODEL` 硬编码 text2vec **~L152**（`INTENSITY_CONFIG.get('embedding_model','shibing624/text2vec-base-chinese')`）+ `SentenceTransformer(EMBEDDING_MODEL)` 调用 **~L370-377**（import L372 / `SentenceTransformer` L374 / `model.encode(kw_list)` L377，`kw_list=idf_weights.keys()`，**词表级一次性**嵌 ~1506 金科词，非逐文档）| 改统一引擎**双轨** `embed_texts(spec=…)`：MAIN=gemini→`fintech_intensity_score`（无后缀，三轨）+ `intensity_verified`；`_lg`=large→`fintech_intensity_score_lg`（镜像三轨）；删 `config/filtering.yaml::fintech_intensity.embedding_model` 键；详见 §5A |

### 3B. 聚合 + 导出（panel 层）
| 文件 | 锚点（实测 CONFIRMED）| 动作 |
|---|---|---|
| `pipeline/panel/runner.py` | `_t2v_src` **L1871-1885** / `_bge_src` **L1910-1921** / **留 `_lg_src` L1892-1903** | 删 `_t2v_src` + `_bge_src` 块；**留 `_lg_src` 逐字**；更新注释 L1864-1869 |
| `pipeline/panel/export.py` | 🔴 `REQUIRED_PANEL_COLUMNS` **L373-374** 硬要求 `strat_diff_t2v_full/ctx`、`policy_cosine_sim_t2v_full/ctx`；`STATA_LABELS` fallback **L798-822** ~25 条 `_t2v` | 🔴 删 L373-374 两行 + 全部 `_t2v` STATA_LABELS；**必须与 producer/runner 原子同删**（见 §4 陷阱①）|
| `pipeline/panel/stata_export.py` | `_t2v` 手写标签~L338-362,429-447；`_bge` 派生循环~L476-482；**`_lg` 派生循环~L458-467**；`_allv` 循环~L484-499 | 删 `_t2v` 手写标签 + `_bge` 派生循环；**留 `_lg` 循环 + `_allv` 循环**；⚠ **`_lg` 标签派生 re-base**（见 §4 陷阱②）|

### 3C. Config（`config/features.yaml`，实测行号 CONFIRMED）
- **删 `embedding_robustness` 块 L31-47**（`_t2v` spec）。
- **删 `embedding_bge` 块 L61-68**（`_bge` spec —— ⚠ 当前工作树中**已取消注释处于激活态**，是 R4 遗留未提交改动，本次随删）。
- **改 `embedding_api` L17**：`text-embedding-3-small` → `gemini-embedding-2-preview`（§6）。
- **bump 版本 L29**：`v2-2026-05-29-api` → `v3-2026-06-27-gemini`（§6 BLOCKING）。
- **新增 `embedding_large` 块**（激活 `_lg`，§7）。
- 更新头部 docstring L5-15（四模型叙事 → 双 API 模型）；更新 `benefit_society.max_tokens_per_input:8191` 注释 L85（"text-embedding-3-small 硬性上限"陈旧）。
- 跨 config 复核（低概率）：grep `config/{panel,validation,sentiment,paths}.yaml` 的 `embedding_robustness`/`embedding_bge`。

### 3D. 测试
| 文件 | 动作 |
|---|---|
| `tests/test_t2v_batch_version_lock.py` | **整文件删**（纯 `_t2v` batch_size 版本锁；读已删的 `embedding_robustness.batch_size` → collect 即崩）|
| `tests/test_dual_compute_coverage.py` | 删 `_FAKE_BGE_SPEC`/`_enable_bge`/`_fake_embed_raise_bge`/`test_bge_local_*`、全部 `_t2v`/`_bge` 列断言；`_track_of` 四分 → 留 `''`+`_lg`；MAIN mock dim 1536→3072；休眠锁改测 `_LARGE_SPEC`（现已激活则改测"激活产 `_lg` 列"）；config-shape 锁删 `embedding_robustness`/`embedding_bge` |
| `tests/test_16_policy_alignment_dual.py` | mock dim `[1.0]+[0.0]*1535`→`*3071`；删 `policy_cosine_sim_t2v_*` 断言；强制 `_ROBUSTNESS_SPEC` 存在的测试 → 删/改 MAIN+`_lg` |
| `tests/test_omni_fix_{strategic,embed,policy,benefit,panel_export,net_spill,runner}.py`、`tests/test_25_audit.py` | 删 `_t2v`/`_bge` 列 + npy 断言；硬编码 `1536`/`8191` 字面量按需改（多数 mock dim，安全）；**⚠ `test_omni_fix_runner.py:328` `assert "policy_cosine_sim_t2v_allv_full" in src` 必删**（runner `_t2v_src` 删后该字面量消失），保留 `_lg`/`article_sim_mean_allv` 孪生断言 |
| `tests/integration/test_panel_reproducibility.py` | **不改码**；golden 重生前**按设计 fail**（§8）|
| `tests/fixtures/golden_panel_v0.json` | **重生**（非手改）|
| `scripts/audit/_dual_embedding_validation.py` | 一次性审计，断言 1536/768 形状 → 删或改 MAIN-only |

### 3E. 二进制产物 + Stata/papers/docs
- **npy 删**（producer 码删后）：`data/processed/27_benefit_embeddings_t2v_{full,ctx,ss}.npy` + `.sidecar.json`；`27_benefit_direction_t2v.npy` + sidecar；及 `data/_processed_backup_run20260619/` 镜像。
- **Stata `.do`**：`stata/09_label_strategic.do` L71-73,91-93（`strat_diff_t2v_*`/`policy_cosine_sim_t2v_*` 标签）+ 注释 L9 删；`papers_assets/bank_fintech_tone/do/50_robustness_text2vec_stata.do` —— **整文件是 `_t2v` 稳健性脚本 → 删**（⚠ 删前跑 `find papers_assets -name 50_robustness_text2vec_stata.do` 确认它在 `papers_assets/` 下而非 `papers/_common/stata_templates/`，否则触 `test_papers_b_route::test_total_template_count_142`；实测它在 `papers_assets/` → **不计入 142**，安全）；`data/processed/46_panel_yearly_labels.do` 自动重生（源修好即可）。
- **文档（非 load-bearing）**：`CLAUDE.md` 版本头；`pipeline/text/__init__.py` docstring；`core/dag.py` 注释 L273-280；`core/schemas.py` 注释 L74；`core/caching.py` docstring §5-C；`scripts/audit/ADD_BGE_M3_*.md`/`ADD_EMB3LARGE_*.md`（标注 superseded）；`config/v2_3_implementation_constants.json::v3_7_0_pr_9_sbert_persist.sbert_model`（冻结历史 sidecar，append-only 代码不改，加弃用注记/标 superseded，stage 26 现走 features.yaml→引擎 spec）；`pipeline/.../article_staleness.py` docstring 中 "768维" → "N维（由嵌入模型决定；gemini/large=3072）"（纯文档，代码 `faiss.IndexFlatIP(dim)` 已维度无关）；`core/text/token_utils.py` 的 cl100k docstring（"text-embedding-3-small 编码器"）补一句"cl100k 对 gemini 是保守高估、亦服务 gemini 切块"（§6/§2，刻意保留 cl100k）。
- ⚠ **manuscript 失效（最高 stakes 非技术项）**：`papers_assets/benefit_society/drafts/{zh,en}/manuscript.tex` 把 `shibing624/text2vec-base-chinese` 列为**稳健性方法学**（zh L120）。若该稿在投/在审，删 `_t2v` **使已陈述的稳健性主张失效** → 须改稿/披露。**Phase 6 必须处理**（见 §12 披露）。

---

## 4. 四大硬陷阱（必须原子处理，排名按危险度）

**① export ↔ producer ↔ runner 原子性（最危险）**
`export.py::REQUIRED_PANEL_COLUMNS` L373-374 把 `_t2v` 列列为**硬契约**，缺失即 `RuntimeError`（`_missing` 检查 L376-382）。
- 只删 producer 不删 L373-374 → `export_panel` 崩。
- 只删 L373-374 不删 runner `_t2v_src` 合并 → panel 出现伪 NaN `_t2v` 列。
- **铁律：producer（3A）→ runner（3B）→ export（3B）三步必须同一 commit 落地。**

**② 🔴 `stata_export.py` 的 `_lg` / `_allv` 标签派生在删 `_t2v` 后输入归零（最易漏，已升 P0）**
现状（实测 CONFIRMED）：`_lg`/`_bge` 标签是**从 `_t2v` 手写模板机械派生** —— `_lg` 派生循环 **L458** `for _k,_v in [(k,v) for k,v in HEURISTIC_LABELS.items() if '_t2v' in k]`（`'_t2v'→'_lg'`、`'T2V robust'→'Large robust'`）。**关键发现**：anchor-dependent 嵌入族（`policy_cosine_sim_*`/`strat_diff_*`/`auth_sim_emb_*`/`benefit_*`/`emb_peer_tone_lag1_*`）在 `HEURISTIC_LABELS` 里**只有 `_t2v` 键、没有 MAIN（无后缀）键**（仅 `bank_emb_sim_mean_lag1` 例外）。删 `_t2v` 块后 L458 循环 **0 次迭代** → `_lg` 标签**全失**；`_allv` 派生循环（**L489-499**）依赖同一集 → `policy_cosine_sim_allv_*` 等标签**也静默消失**（这些列确实进 panel）。故"re-base 到 MAIN 模板"**当前不可执行（MAIN 模板根本不存在）**。
- **修复（具体化，见 §9 Phase 6）**：① 在删 `_t2v` 块前，**手写新增 MAIN（无后缀）`HEURISTIC_LABELS` 条目**覆盖全部 anchor-dependent 嵌入族；② 把 L458 循环判据从 `if '_t2v' in k` 改为基于这批 MAIN 键集（`if k in _MAIN_ANCHOR_KEYS`）派生 `_lg`；③ 删 L469-482 `_bge` 派生循环；④ 测试断言 `_lg`/`_allv` 标签非空。这是全任务最易错的一处。

**③ `ensure_torch_determinism` / 本地推理机器的删除时机**
`embedding_engine.py::ensure_torch_determinism` 当前被 `article_sbert.py:161` import。**D-2a 锁定 stage 25 = 选项 (i) 全 API**（§5B）→ article_sbert 不再本地 torch 推理 → 该函数 + 全部本地机器（§5C）**孤儿可删**。
- **铁律：先完成 §5B 的 article_sbert 双轨 API 改造（删其 `ensure_torch_determinism` import），再删引擎里的该函数**；删前 grep 全仓确认零 import（tone_berts 有自有确定性块，不依赖此函数）。⚠ 若 article_sbert 改造留有任何 import 而引擎已删 → stage 25 import 崩。

**④ network_spillover 早退死代码陷阱**（§3A 已述）：删 `_t2v` 块 + `if not _ROBUSTNESS_SPEC: return` 守卫后，确保 `_lg` 块无条件可达。

---

## 5. 影响面 B：text2vec **彻底移除** + stage 15/25 改 **MAIN+`_lg` 双轨 API 嵌入**（D-2 + D-2a 核心）

> 这两处**不是稳健轨**，是产出 load-bearing 测度的功能嵌入。删 text2vec 后，二者**统一改走 API 双轨**：gemini(MAIN) + text-embedding-3-large(`_lg`)，互为稳健性检验。任一测度**数值必变** → golden 改、须 manuscript 披露。**铁律**：MAIN 与 `_lg` 各自 just-identified 并排，**禁混进同一 over-identified Hansen J**（沿用全管线既有红线）。

### 5A. stage 15 `fintech_intensity`（金科强度 `fintech_intensity_score`）
- **现状**：硬编码 `EMBEDDING_MODEL='shibing624/text2vec-base-chinese'`（~L36/152），用于关键词的"语义纯粹度权重" `CosSim_scaled_i`（IDF×CosSim 双权）。
- **改造**：把该处 `SentenceTransformer` 调用改为经统一引擎 `embed_texts(..., spec=…)`，**双轨**：
  - MAIN = gemini → `fintech_intensity_score`（无后缀，三轨 `_full/_ctx/_ss`）+ `intensity_verified`。
  - `_lg` = text-embedding-3-large → `fintech_intensity_score_lg`（镜像三轨）作互为稳健性检验。
- ⚠ 实施前**必须确认嵌入对象**：据 docstring 公式 `W_i=IDF_i×CosSim_scaled_i` 的 CosSim 是**词级语义纯粹度**（金科词 vs 质心），应为**词表级一次性**（~1506 词 × 2 模型，成本极低）。若实现里还嵌**逐文档**，须在 Phase-0 量化（双轨 ×2）。
- **后果**：`fintech_intensity_score` 三轨**数值变**（不同嵌入 → 不同纯粹度权重）+ 新增 `_lg` 镜像列。属**测度变更**，须披露。stage 15 always-on，**阶段计数不变**（列内扩展）。

### 5B. stage 25 `article_sbert` → stage 26 语义陈旧度（staleness）—— **选项 (i) 双轨 API 嵌入**（D-2a 锁定）
- **现状**：读 `embedding_robustness.model` → text2vec 单模型编码 title+300char → **768 维**向量 → stage 26 语义陈旧度（近重复检测 + 余弦）。**当前是单模型、无 robustness twin。**
- **改造（D-2a 锁定 = 选项 i + 双轨）**：
  1. `article_sbert.py` **弃本地 `SentenceTransformer`**，改走统一引擎 `embed_texts(..., spec=…)`，对 title+300char 文本用**两个 API spec 各嵌一遍**：
     - MAIN = gemini（3072 维）→ 既有 staleness 列（无后缀）。
     - `_lg` = text-embedding-3-large（3072 维）→ 新增 `_lg` 镜像 staleness 列。
  2. `_resolve_sbert_model`（读 `embedding_robustness.model`）**删除/替换**为引擎 spec 路由（不再有"单一事实源 = embedding_robustness"概念）。
  3. stage 26（`article_staleness`）对**两套嵌入各算一遍**陈旧度 → **`semantic_staleness_{full,ctx,ss}`**（MAIN）+ **`semantic_staleness_{full,ctx,ss}_lg`**（`_lg`），互为稳健性检验。⚠ **仅嵌入派生的 `semantic_staleness` 双轨化**；同模块的 **`surface_staleness_{full,ctx,ss}` / `surface_highstale` 是 MinHash/datasketch 字符 shingle 派生（无嵌入）→ 不产 `_lg` 孪生、行为不变**（归入 §11 parity carve-out）。
- **成本**：⚠ **每篇文章嵌两个 API 模型**（gemini + large）。title+300char 短（~100-150 token/篇），但生产 17M 文 × 2 模型 = **本计划最大可量化成本**（text2vec 原本地 GPU $0）。Phase-0 须用 T=2 小样实测单价、外推生产、单独批准（§10）。
- **下游契约核查（实施前必做）**：`semantic_staleness` 改 768→3072 维 + 改 API + 加 `_lg` 列 → 须确认 stage 26 的 FAISS（`IndexFlatIP(dim)`，已维度无关）对 3072 维无硬编码维度假设；确认 `semantic_staleness`（嵌入派生）下游消费者（always-on，进 panel）不因新增 `_lg` 列或值变而断；`surface_staleness`/`surface_highstale`（MinHash，非嵌入）**完全不动**。
- ⚠ stage 25/26 是 always-on，**阶段计数不变**（纯列内：MAIN 值变 + 新增 `_lg` 列；无阶段增删）。
- **维度脚注**：原 text2vec staleness 是 768 维、SBERT title+300char 截断（512 token 内）；改 gemini/large 后维度升 3072，但 staleness 是**相对近重复**测度（余弦排序/阈值），维度无关；截断策略（title+300char）**保留不变**以维持 Bybee 风格构念。

#### §5B.1 — `article_sbert.py` dual-emit 实现规范（P0-2：Phase 1 必须先落地，当前 0 重构）
> 现状（实测 CONFIRMED）：`article_sbert.py` 100% 单模型本地——`_load_sbert_model`（L155-170）裸 `SentenceTransformer`、`model.encode` L210、单套 provenance（`_build_output_frame` L223-256 仅一组 `model_id/model_revision/text_pipeline_version`）、`ensure_torch_determinism` import L161、零 `embed_texts` 引用。这是整个 D-2a 架构的 load-bearing 前置门，必须给出实现规范（非仅叙事）。
1. **`main()` 每轨调引擎两次**：`emb_main = embed_texts(texts, CONFIG['embedding_api'])`（gemini）+ `emb_lg = embed_texts(texts, CONFIG['embedding_large'])`（large）。删 `_load_sbert_model` / `_resolve_sbert_model`。
2. **删 L161 `from ...embedding_engine import ensure_torch_determinism` import**（API-only 后无本地 torch；Phase 7 删引擎函数前 grep 全仓零 import，tone_berts 自有确定性块）。
3. **输出 schema 扩展**：`emb_{full,ctx,ss}`（MAIN/gemini）+ `emb_{full,ctx,ss}_lg`（large）；**双套 provenance**：`model_id/model_revision/text_pipeline_version` + `_lg` 镜像三元组（供 stage 26 双套独立校验）。
4. **下游 stage 26（`article_staleness`）** `_load_aligned_embeddings`：对 MAIN 与 `_lg` 两套各自做 provenance fail-loud 校验 + 各算一遍陈旧度（产 MAIN 列 + `_lg` 镜像列）。
5. `26_staleness_panel.parquet` 带 **spec-origin 元数据列**（供 manuscript 透明归因 + 双轨 corr 报告）。
6. ⚠ 文本切块走引擎现有 cl100k/8191 机制（gemini 安全，§2/§6），但 article_sbert 的 title+300char 远未触限 → 不分块、直送。
7. **明确接口契约（防实现漂移）**：
   - `_build_output_frame` 签名由 3 嵌入参数（`embs_full/ctx/ss`）扩为 **6 参数**（+ `embs_full_lg/ctx_lg/ss_lg`）。
   - parquet 列：`emb_{full,ctx,ss}`（MAIN）+ `emb_{full,ctx,ss}_lg`；provenance **两套三元组** MAIN `(model_id, model_revision, text_pipeline_version)` + `_lg` 镜像 `(model_id_lg, model_revision_lg, text_pipeline_version_lg)`。
   - 下游 stage 26 `_load_aligned_embeddings` 须 **unpack 6 个矩阵**、对两套各自 provenance fail-loud 校验；`compute_semantic_staleness()` 加 **track/spec 后缀参数** → 发射 `..._lg` 镜像列。
   - 向后兼容：旧 parquet 无 `_lg` 列时 → `_lg` 陈旧度优雅 `None` 降级（不崩，与既有 NaN 守卫一致）。

### 5C. 引擎本地机器拆除（`embedding_engine.py`，D-2 下全删）
全部 spec 均为 API 后，本地推理机器**全孤儿**：
| 符号 | 行 | 动作 |
|---|---|---|
| `encode_local` | 310-393 | **删** |
| `_encode_local_cached` | 639-733 | **删** |
| `_LOCAL_MODELS` | 117 | **删** |
| `_LOCAL_BASE_URLS` | 119-124 | **删** |
| `spec_uses_local` + `embed_texts` 本地分支 | 256-259 / 784-789 | **删**（`embed_texts` 收为纯 API 路径）|
| `_select_torch_device` | 295-307 | **删** |
| `ensure_torch_determinism` | 217-253 | **删**（D-2a 选 (i) 全 API → article_sbert 不再本地 torch 推理 → 此函数全仓零 import；§4 陷阱③：删前 grep 全仓确认，tone_berts 有自有确定性块不依赖此函数）|
| `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE` env | 77-78 | 删（引擎全 API，不再加载任何本地模型）|
| `spec_model`/`spec_version` | 262-269 | **留**（API 路径仍用）|
| `split_text_for_embedding`/`_EMB_ENCODING`/`EMB_MAX_TOKENS` | 272-292/85-86 | **留**（API 切块用，gemini 安全，§2）|

---

## 6. 影响面 C：MAIN 切换 `gemini-embedding-2-preview`

- `config/features.yaml` **L17**：`model: gemini-embedding-2-preview`。
- `config/features.yaml` **L29**：`text_pipeline_version: "v3-2026-06-27-gemini"`（🔴 BLOCKING：model_id 已变缓存自然 miss，但版本 bump 是 `caching.py §5-C` 强制的防御层，同 diff 必做）。
- `config/features.yaml` **L18**：`base_url` 保留 `https://yunwu.ai/v1`（实测 gemini 走此端点 OK）。
- `embedding_engine.py` **L262**：`spec_model` 默认 `'text-embedding-3-small'` → `'gemini-embedding-2-preview'`（**强制，非 cosmetic**：签名允许 `spec=None`，留旧默认会让缺失/None spec 把已删的旧主模型悄悄塞回缓存键/日志）。
- API payload（L508）`{"model","input"}`：**不动**（gemini 经 yunwu 用同格式，无需 `dimensions`/`task_type`）。引擎 `emb.shape[1]` 驱动（L823 维度无关）→ 3072 自然流过，**数学层零改动**。
- **tokenizer / token 限制：保留现状**（§2 实测：cl100k 8191 对 gemini 保守安全）。`EMB_MAX_TOKENS=8191`、`core/text/token_utils.py` 的 cl100k 不改。

### 方法论 caveat（manuscript 须报）
gemini 原生 `SEMANTIC_SIMILARITY` task_type 在 OpenAI-compat 路径**无法指定**；实测返回**单位归一向量**（norm=1.0），余弦=点积，形式上可用。但激活后**须用人工/已知对实测 corr** 验证 gemini 余弦的语义有效性（不能假设 = text-embedding-3-small 的语义行为）。**铁律重申**：gemini 与 large 两 co-primary 各自 just-identified 并排，**禁混进同一 over-identified Hansen J**。

---

## 7. 影响面 D：激活 `_lg`（text-embedding-3-large）作 **co-primary ②**

新增 `config/features.yaml::embedding_large`（参照已退役计划 `ADD_EMB3LARGE_*` §Phase1）：
```yaml
embedding_large:                          # CO-PRIMARY ② — text-embedding-3-large (OpenAI); 与 gemini(co-primary ①) 对等互证, 跨厂商
  model: text-embedding-3-large
  base_url: https://yunwu.ai/v1
  api_key: ${EMBEDDING_API_KEY}
  text_pipeline_version: "v1-2026-06-27-emb3large"
```
- 5 producer 的 `if _LARGE_SPEC:` 分支**本就存在**（v3.12.0 已落码、休眠）→ 加 config 即激活，产 `_lg_{full,ctx,ss}`(+`_allv`) 列。
- ⚠ **co-primary parity 强制语义（精确定义，避免与 API 软降级冲突）**：parity = **schema 层列名双射，非值非空**。
  - **测试门强制（非 export 运行期 raise）**：`test_embedding_coprimary_parity`（§11）post-export 校验"每个无后缀嵌入列 ⟺ 恰一同名 `_lg` 列"，**值可 NaN**（与既有 `embed_texts` 返回 None→列置 NaN 的软降级守卫不冲突）。
  - **`export.py::REQUIRED_PANEL_COLUMNS` 删 L373-374 `_t2v` 后不新增 `_lg` 硬契约**（避免运行期 raise 与 API 软降级打架）；parity 由测试门保证，不由 export raise。
  - **producer 侧 both-or-neither**：在 producer 内，若 gemini 或 large 任一 `embed_texts` 返回 None，则**两列同置 NaN**（不产单边孤儿列），从源头保证列名双射成立。v3.12.0 既有 `_lg` 分支的"软诊断/NaN 不崩"行为**保留**（不改为崩），仅由测试门 + producer both-or-neither 保证 parity。
- `runner._lg_src`、`stata_export` `_lg` 派生循环**保留**（§4 陷阱② / §9.6 re-base 后，co-primary 标签文案）。
- **付费**：激活即须播种 `_lg` 缓存（§10 成本）；gemini 与 `_lg` 同批播种、同等对待（parity）。

---

## 8. golden & 复现性（**无任何字节安全**，须受控全量重生）

**为何零字节安全**：MAIN 换模 + 1536→3072 → **每一个 MAIN 派生值都变**（不同模型 + 不同维度的余弦标量）；叠加删 **37 个唯一 `_t2v` 列名**（golden 跨 stage 共 **77 条列哈希**：40_panel_yearly 37 + 51_panel_with_controls 37 + 16_article_alignment 3）+ **0 个 `_bge` 列**（当前休眠未计）（schema 缩）+ 激活 `_lg`（schema 增）+ stage 15 intensity 双轨化（值变 + 新 `_lg` 列）+ stage 25/26 staleness 双轨化（768→3072 值变 + 新 `_lg` 列，§5B）。golden 在**多轴**齐变：列集 + 数值 + 维度。

**必须重生**：`tests/fixtures/golden_panel_v0.json`（`generate_golden_snapshot.py`）；panel parquet/.dta/.csv；MAIN `.npy`（`27_benefit_embeddings.npy` 1045×1536→1045×3072、`27_benefit_direction.npy`）+ sidecar 的 model_id/version；**stage 25 嵌入持久化产物**（768→3072 维 + 新增 `_lg` 套）。⚠ staleness/intensity 列既改值又增 `_lg` 列，golden 列哈希全部刷新。

**受控重生环境**（memory `golden-regen-omp-determinism`）：`PYTHONHASHSEED=0` **且** 全 BLAS 线程钉死 1（`MKL_NUM_THREADS=1`+`OPENBLAS_NUM_THREADS=1`+`NUMEXPR_NUM_THREADS=1`+`OMP_NUM_THREADS=1`；numpy=MKL 故 OMP 单独不够）。3 个网络中心度列（`bank_clustering` / `bank_cfbetween_cent` / `bank_harmonic_cent`）保持 BLAS-FP 非确定 → 字节等值检查须排除。

**⚠ 预览版复现 caveat（D-5 披露，新增于现状）**：`gemini-embedding-2-preview` 是**预览端点** + yunwu 代理双层非钉死。与 text-embedding-3-small（稳定、`_llm_cache.db` 已 0-miss 全缓存）不同，gemini 在本播种周期前 `_llm_cache.db` **零命中**（新 model_id 缓存为空） → 首次 golden 重生**付费全量重嵌**，且重生后 golden 仅"在预览端点持续返回相同向量期间"可复现；**预览模型被静默更新 → golden 无码变即破**。缓解（仅披露非机制）：播种后 `_llm_cache.db`（新 model_id+version 键）成为复现锚点，前提是维持 0-miss（同 stage21 纪律）。**勿删 `_llm_cache.db`**（[[stage21-determinism-anchor-2026-06-06]]）。

---

## 9. 分阶段执行步骤（强制顺序）

| Phase | 内容 | Gate |
|---|---|---|
| **0** | 前置 gate：① gemini 可用性 ✅（已验）② token 限制 ✅（已验）③ stage 25 = 选项 (i) 双轨 ✅（D-2a 锁定）④ 盘上 T=2 小样估 gemini MAIN + `_lg` + **staleness/intensity 双轨**重嵌成本（含 staleness 逐文档 ×2 模型）| 成本确认 |
| **1** | article_sbert 双轨 API 改造（§5B：弃本地 ST、删 `ensure_torch_determinism` import、走引擎 gemini+large 双 spec），再动 config（§4 陷阱③）| stage 25 import 不崩 |
| **2** | `config/features.yaml`：删 `embedding_robustness`+`embedding_bge`、换 MAIN model + bump 版本、**新增 `embedding_large` 配置块（参照 §7：model/base_url/api_key/text_pipeline_version 四行，与删两块同一 diff）**；+ 删 `config/filtering.yaml::fintech_intensity.embedding_model`（~L36） | — |
| **3** | Producer（**6 个，含 fintech_intensity**）删 `_t2v`/`_bge` 分支（§3A）+ stage 15 fintech_intensity 双轨 API 改造（§5A）+ stage 25 article_sbert 双轨 API 改造（§5B）+ stage 26 双轨 staleness | — |
| **4** | `runner.py` 删 `_t2v_src`/`_bge_src`（留 `_lg_src`）| 🔴 与 3、5 原子 |
| **5** | `export.py` 删 L373-374 + `_t2v` STATA_LABELS | 🔴 同上 |
| **6** | `stata_export.py` `_lg` 标签 re-base（**具体化**，见下 §9.6）| 测试 `_lg`/`_allv` 标签非空 |
| **7** | 引擎本地机器拆除（§5C）| 确认零 import |
| **8** | 测试删/改（§3D）| ruff + pytest |
| **9** | npy + Stata `.do` 删（§3E）| — |
| **10** | 文档 + manuscript 披露（§3E + §12）| — |
| **11** | 播种缓存（gemini MAIN + `_lg` + stage15/25）→ golden 受控重生（§8）| M0 付费 gate |
| **12** | 验收门（§13）→ by-name 提交 → CLAUDE.md v3.14.0 | — |

### §9.6 — Phase 6 `stata_export.py` `_lg` 标签 re-base（P0-1 具体化）
> 背景：anchor-dependent 嵌入族在 `HEURISTIC_LABELS` 里**只有 `_t2v` 键、无 MAIN 键**；删 `_t2v` 后 `_lg` 派生循环（L458 `if '_t2v' in k`）与 `_allv` 循环（L489-499）输入归零（§4 陷阱②）。
1. **先手写新增 MAIN（无后缀）`HEURISTIC_LABELS` 条目**（在 `_t2v` 字面 dict 之后、`_lg` 派生循环 L458 **之前**），覆盖**这 10 个** stata-label anchor 嵌入族：`policy_cosine_sim_{full,ctx,ss}`、`strat_diff_{full,ctx,ss}`、`strat_diff_n5_emb_{full,ctx,ss}`、`strat_sim_max_emb_{full,ctx,ss}`、`centroid_diff_emb_{full,ctx,ss}`、`coh_emb_{full,ctx,ss}`、`auth_sim_emb_{full,ctx,ss}`、`benefit_{mean,std,pos_frac,neg_frac}_{full,ctx,ss}`、`emb_peer_tone_lag1_{full,ctx,ss}`、`bank_emb_sim_mean_lag1`。**MAIN base 文案各带恰一个 "(co-primary: gemini-embedding-2-preview)" 标注**。
2. **在 L458 之上显式定义** `_MAIN_ANCHOR_KEYS = frozenset({上述步骤 1 全部手写键}）`；把 **L458** 派生循环判据由 `if '_t2v' in k` 改为 `if k in _MAIN_ANCHOR_KEYS`，派生 `_lg` 标签 = **以 step-1 MAIN base 文案、把 "(co-primary: gemini-embedding-2-preview)" 整体 _replace_ 为 "(co-primary: text-embedding-3-large)"**（**replacive 非 append**，确保 MAIN 与 `_lg` 各带恰一个对称 co-primary 标注、无双标记视觉层级；**禁用 "robust/robustness check"**，D-4）。
3. **删 L469-482 `_bge` 派生循环**（随 `_bge` 删除）。
4. `_allv` 循环（L489-499）现可在 MAIN + `_lg` 两套键上正确派生 `policy_cosine_sim_allv_*` 等。
5. **测试断言（强化，防部分 re-base 静默漏族）**：遍历**上述 10 个 stata-label anchor 根族 × 3 轨**（外加单列 `bank_emb_sim_mean_lag1`），逐一断言 (a) MAIN base 键在 `HEURISTIC_LABELS`、(b) 派生 `_lg` 键存在且标签非空、(c) 对应 `_allv` 键标签非空 —— 而非弱 `any(...)` 单族抽检（弱断言会让 9/10 族部分失败仍通过）。
   - ⚠ **范围澄清**：这 10 族是 **stata-label re-base** 的 parity（标签层）。`fintech_intensity_score`（stage 15）/ `semantic_staleness`（stage 26）是**计算测度**，其 co-primary parity 由 **producer 代码** both-or-neither 强制（§5A/§5B）+ panel 列双射测试（§11 `test_embedding_coprimary_parity`）保证，**不入此标签 re-base 循环**，故**不计入这 10 族**。

---

## 10. 成本估算（生产 T=18，本机无生产语料，须 Phase-0 实测）

| 项 | 量级 | 估算 |
|---|---|---|
| MAIN gemini 全量重嵌（5 cosine producer × 三轨唯一文本）| ~944k×3 唯一文本 ≈ 1.5–1.8B token | gemini 计价待 Phase-0 实测（yunwu 报价）；**MAIN 是全量、非增量**，是主成本 |
| `_lg` 激活播种（5 cosine producer，同上规模）| 同量级 | @ ~$0.13/1M ≈ **$200–240**（沿用 ADD_EMB3LARGE 估）|
| **stage 25→26 staleness 双轨（25 嵌入生产 + 26 计算，D-2a 选项 i）** | ⚠ **每篇文章 title+300char × 2 模型（gemini+large）**（远多于 cosine producer 的去重文本集；逐文章非去重）| **本计划最大可量化成本**；title+300char 短(~100-150 token/篇) 但 17M 文 ×2 模型 → 须 Phase-0 实测外推 |
| **stage 15 金科质心双轨** | ~1506 词 × 2 模型一次性（若仅词表级）| 极低（若逐文档则 Phase-0 重估）|
| 存储 | benefit `_lg`/MAIN `.npy` + stage 25 嵌入 3072 维 ×2 套 | 中 |
| 离线复现 | 播种后 `NEWS_PROCESS_LLM_OFFLINE=1` | $0 |

> ⚠ 与之前 `_lg`/`_bge` 的"加法休眠 $0"**根本不同**：本次 MAIN 槽换模 + staleness/intensity 双轨化 = **付费全量重嵌（gemini + large 两 co-primary）+ 逐文章双模型嵌入**，不可避免。D-2a 的双轨化使嵌入成本约 **×2**（每测度两个 API 模型）。

---

## 11. 计数不变量 + parity 不变量

- **STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16 全不变**（列内扩展 + 测度替换 + staleness/intensity 双轨化，**无阶段增删**；D-2a 选项 (i) 不动阶段，只在 stage 15/25/26 内部加 `_lg` 列）。
- 🔴 **gemini⟂large parity 不变量（D-4a，新增强制门）**：panel + 各 producer 产物中，**每一个无后缀嵌入派生列 ⟺ 恰存在一个 `_lg` 孪生列，反之亦然**（双射）。
  - **嵌入派生族（须有 `_lg` 孪生）**：`policy_cosine_sim_{full,ctx,ss}`(+`_allv`)、`strat_diff_*`/`strat_sim_max_emb_*`/`centroid_diff_emb_*`/`coh_emb_*`、`auth_sim_emb_*`(+`_allv`)、`benefit_{mean,std,pos_frac,neg_frac}_*`、`emb_peer_tone_lag1_*`/`bank_emb_sim_mean_lag1`、`fintech_intensity_score`(三轨)、**`semantic_staleness_{full,ctx,ss}`**。
  - **carve-out（非嵌入派生，禁止 `_lg` 孪生）**：`surface_staleness_*`/`surface_highstale`（MinHash 字符 shingle）、`ss_is_fallback`/`ctx_is_fallback`/`headline_frac` 等 track-agnostic 元数据 —— 这些列**无 `_lg` 概念**。
  - 新增测试 `test_embedding_coprimary_parity`：扫 panel 列名集，断言 (a) 每个嵌入派生无后缀列恰有一 `_lg` 孪生（无孤儿）、(b) 每个 `_lg` 列恰有一无后缀本体、(c) **carve-out 列不得出现 `_lg` 变体**（防 surface_staleness_lg 误产）、(d) **覆盖率 parity**：因 producer both-or-neither（§7，任一 spec 返回 None→两列同 NaN），同族 `N(non-null 无后缀) == N(non-null _lg)` **精确相等**（非 ±tol），断言之以防单边播种漂移。
- `core/dag.py`/`core/schemas.py` 的 `_t2v` 引用**仅注释**（无 `enabled_when` 谓词、无 OUTPUT_REGISTRY 枚举）→ `dag_consistency` 不受影响。
- ⚠ 测试断言计数复核：`test_dual_compute_coverage`（列名集缩）、`test_16_policy_alignment_dual`、`test_omni_fix_panel_export`（`REQUIRED_PANEL_COLUMNS` 长度 −4）、`test_papers_b_route::test_total_template_count_142`（确认 `50_robustness_text2vec_stata.do` 在 `papers_assets/` 不计入 → 142 不变）。

---

## 12. 风险 / 回滚 / 披露

- **🔴 不可逆成本**：MAIN 换模的生产重嵌是真金白银（不像加法休眠可净空回滚）。回滚代码易（git revert + 恢复 config），但**已花的重嵌费用沉没**。
- **回滚**：删 `embedding_large`、恢复 `embedding_api` model=small、恢复 `embedding_robustness`/`embedding_bge`、`git revert` 代码 → 旧四模型架构回归（但 golden 需再切回旧版）。
- **manuscript 披露（必做）**：① 删 `_t2v`/`_bge` → 原"本地/中文专训跨架构稳健性"主张失效，须改稿；② MAIN 改 gemini → 主测度全部换嵌入空间，须重报所有嵌入派生结果 + gemini 余弦实测有效性；③ gemini 与 large **co-primary 对等互证**须如实定位（**跨厂商 Google⟂OpenAI 两个对等主测度，互证一致性**；**不得**称 large 为"稳健性附录/robustness check"——D-4）；④ 预览模型复现性局限须 limitations 段披露；⑤ stage 15 intensity + stage 25→26 staleness 改 gemini+large **co-primary 双轨**（测度数值变 + 对等互证），须披露测度变更并报双轨 corr；⑥ 两 co-primary 各自 just-identified 并排报告，**禁混进同一 over-identified Hansen J**（co-primary 不改此铁律）；⑦ **co-primary 分歧裁定规则**（manuscript 须明文）：两轨结果**并排报告、绝不平均/池化**；约定"互证一致 = 符号一致 且 |β| 同量级"，**符号翻转 或 |β_gemini|/|β_large| > 2×** 标为**实质分歧**须正文讨论（非藏附录）；**多重比较立场**：co-primary 定位为"互证稳健性"（**非两个独立假设**）→ 默认不做 Bonferroni/FDR 校正，但若审稿要求按独立检验，则**校正后 + 未校正 p 值并列**报告。
- **预览版风险**（D-5）：见 §8 caveat。

---

## 13. 验收门

`ruff clean` · 全量 `pytest`（co-primary → gemini+`_lg` dual coverage，含 staleness/intensity 新双轨）· `dag_consistency` · 🔴 **`test_embedding_coprimary_parity` 过**（gemini⟂large 列双射，无孤儿列，§11/D-4a）· **`test_panel_reproducibility` 受控重生后过**（既有 `_t2v`/`_bge` 列消失、gemini 列 3072 新值、`_lg` 列新增、staleness/intensity 双轨列就位）· **`corr(gemini, large)` 实测报告**（跨厂商 co-primary 互证一致性，覆盖 cosine producer + semantic_staleness + intensity）· **`test_gemini_semantic_validity` 绑定阈值**（gemini 无 task_type 路径，§6 caveat）：预设 **Spearman ρ(gemini, large 余弦) ≥ 0.80**、样本 **≥500 对**，低于阈值则 gate 失败（替代原"抽检"的不可证伪表述）。

---

## TL;DR

把项目从"四模型（small 主 + 本地 t2v/bge + 休眠 large）"**转向"双 API 模型、零本地模型、gemini ⟂ large 跨厂商 co-primary 对等双轨"**。**gemini 与 large 同为主测度、互为稳健性、严格 parity（有 gemini 处必有 large，反之亦然；`_lg` 后缀仅命名机制无层级，D-4/D-4a）**。删 `_t2v`/`_bge` 旧稳健轨（代码+列+config+golden+npy+文档，硬删非休眠）；**彻底拔掉 text2vec**——stage 25→26 陈旧度 + stage 15 金科强度的本地骨干**改走 gemini+large co-primary 双轨 API 嵌入**（D-2a，逐文章 ×2 模型）；MAIN 换 `gemini-embedding-2-preview`（3072，引擎数学层零改、token 机制保留，纯 config + 版本 bump）；激活 `_lg`（加 `embedding_large` config，并纳入 **parity 强制 = schema 列名双射 + producer both-or-neither**，软诊断 NaN 行为保留，§7/§11）。**四大陷阱**：① export↔producer↔runner 原子同删、② `stata_export` `_lg`/`_allv` 标签删 `_t2v` 后输入归零须先手写 10 个 MAIN 键再 replacive re-base（co-primary 对称标签）、③ `ensure_torch_determinism` 删除时机（全 API 后孤儿，先改 article_sbert 再删）、④ `network_spillover` 早退守卫（删 `_t2v` 块后保 `_lg` 块无条件可达）。**golden 零字节安全**（换模+缩列+增列+双轨测度变，多轴齐变），须受控全量重生 + **付费重嵌 + 逐文章双模型嵌入**（不可逆成本，约 ×2）。计数 16/16/35/16 不变（纯列内）+ **新增 gemini⟂large parity 不变量门**。预览模型复现风险纯披露不加机制（D-5）。manuscript 须改稿：稳健性维度从"本地/中文专训独立性"→"跨厂商 co-primary 对等互证"，**不得**称 large 为"稳健性附录"。

---

### 附：本计划权威信息源
- yunwu 实测探针（2026-06-27）：gemini-embedding-2-preview 3072 维 / 0–8191 cl100k 安全 / text-embedding-3-large 3072 可用 / 无 GA gemini-001。
- 8-agent inventory workflow（765k token，221 tool-use）master impact map（行号已对源码核验）。
- 既有计划参照：`ADD_EMB3LARGE_AS_THIRD_MODEL_EXECUTION_PLAN_2026-06-27.md`（`_lg` 激活模板）、`ADD_BGE_M3_AS_FOURTH_MODEL_EXECUTION_PLAN_2026-06-27.md`（`_bge` 镜像，反向删除）。
- memory：[[golden-regen-omp-determinism-2026-06-18]] / [[stage21-determinism-anchor-2026-06-06]] / [[three-track-text-architecture]] / [[dualtrack-is-mutual-robustness]] / [[machine-has-rtx3090-local-embeds-on-gpu-2026-06-23]]（注：本计划移除本地嵌入后，RTX3090 本地嵌入条目对嵌入轨失效，仅 stage 23 BERT 仍用 GPU）。
