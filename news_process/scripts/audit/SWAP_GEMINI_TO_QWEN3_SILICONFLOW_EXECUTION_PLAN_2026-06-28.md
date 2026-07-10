# 执行计划：MAIN/canonical 嵌入槽 `gemini-embedding-2-preview`(云雾) → `Qwen/Qwen3-Embedding-8B`(硅基流动)

> 版本目标：**v3.15.0 · BREAKING · 嵌入主轨换厂商 (yunwu→SiliconFlow, gemini→Qwen3-8B)**
> 撰写日期：2026-06-28 ｜ 前置基线：HEAD = `3739979a` (v3.14.0 all-API co-primary)
> 用户指令：「在整个项目中，使用硅基流动中的嵌入模型 `Qwen/Qwen3-Embedding-8B`，替换来自云雾 API 的模型 `gemini-embedding-2-preview`」

---

## 0. 范围与不变量

| 项 | 变更前 (v3.14.0) | 变更后 (v3.15.0) |
|---|---|---|
| **CO-PRIMARY ①** (canonical, 无后缀) | gemini-embedding-2-preview (Google, yunwu, 3072 维) | **Qwen/Qwen3-Embedding-8B (阿里, 硅基流动, 4096 维)** |
| **CO-PRIMARY ②** (`_lg` 孪生) | text-embedding-3-large (OpenAI, yunwu, 3072 维) | **不变** (OpenAI, yunwu, 3072 维) |
| 跨厂商独立性论证 | Google ⟂ OpenAI | **阿里/硅基流动 ⟂ OpenAI** (中文专训 ⟂ 英文为主, 独立性更强) |
| API key | `${EMBEDDING_API_KEY}` (=yunwu) | **`${SILICONFLOW_API_KEY}`** (新 env var) |
| base_url | `https://yunwu.ai/v1` | **`https://api.siliconflow.cn/v1`** |
| text_pipeline_version | `v3-2026-06-27-gemini` | **`v4-2026-06-28-qwen3-8b`** |

**只换 ①, 不动 ②**（用户明确「替换 gemini」, 未提 large）。**列 schema 零改动**（canonical 仍无后缀, `_lg` 仍 text-embedding-3-large）→ 无任何列改名, 远比 v3.14.0 (换维度+删本地轨) 简单。

**计数不变**: STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16。

## 1. 实测探针 (2026-06-28, 非推断)

| 事实 | 实测 |
|---|---|
| 端点可达 | ✅ `POST https://api.siliconflow.cn/v1/embeddings`, OpenAI-compat `{"model","input"}`, Bearer auth |
| 模型名 | ✅ `Qwen/Qwen3-Embedding-8B` (model echo 一致) |
| 维度 | ✅ **4096** (gemini 是 3072 → 维度变, 但引擎 `emb.shape[1]` 驱动、维度无关) |
| 归一化 | ✅ **单位归一** (norm=1.0) → 余弦=点积, 与 gemini/large 同, 余弦语义形式可用 |
| `index` 字段 | ✅ 存在且有序 → 引擎 `sorted(data['data'], key=index)` 重组正确 |
| 批量 | ✅ n∈{2,16,64,256} 全 200 (引擎 ≤2000 动态分批; 生产播种须验更大批) |
| token 上限 | Qwen3-Embedding-8B 支持 32K → 引擎 cl100k 8191 切块对 Qwen **更保守安全** (不动) |

> 探针留存: `scratchpad/probe_siliconflow.py` (一次性, 不入库)。

## 2. 关键技术点：引擎数学层零改动

引擎 (`embedding_engine.py::get_embeddings_api` / `embed_texts`) 完全 `emb.shape[1]` 驱动, payload `{"model","input"}` 不带 `dimensions`/`task_type` → 4096 自然流过。token 切块 cl100k/8191 保留 (对 Qwen 32K 上限保守安全)。**唯一功能改动 = config + env + 代码内 4 处硬编码默认回退**。

## 3. 影响面（已对源码核验）

### 3A. 功能 SSOT (behavior-changing)
- `.env`: 加 `SILICONFLOW_API_KEY=sk-...` (gitignore, 不提交)。
- `.env.example`: 声明 `SILICONFLOW_API_KEY=` (空值, 满足 `_validate_env_placeholders` 契约)。
- `config/features.yaml::embedding_api`: model / base_url / api_key / text_pipeline_version bump + docstring。`embedding_large` 块不动。
- 4 处代码默认回退 `'gemini-embedding-2-preview'` → `'Qwen/Qwen3-Embedding-8B'`:
  1. `pipeline/text/embedding_engine.py::spec_model` default
  2. `pipeline/text/article_sbert.py::_SBERT_MODEL_ID`
  3. `pipeline/features/strategic_diff.py` `_emb_main` fallback (L1471, 2 处字面量)
  4. `pipeline/panel/stata_export.py::_GEMINI_ANNOT` (重命名 `_QWEN_ANNOT` + 值; `_LARGE_ANNOT` 不动)

### 3B. stata 标签 (~40 条)
`stata_export.py` 的 `(co-primary: gemini-embedding-2-preview)` → `(co-primary: Qwen/Qwen3-Embedding-8B)` (Qwen 标注 37 字符 < gemini 40 → ≤80 字节恒满足)。`_lg` 派生循环 (replacive) 结构不变。

### 3C. 注释/docstring 全仓清扫 (accuracy, 非 behavior)
pipeline/text/{article_staleness,__init__}, pipeline/panel/{runner,network_spillover,encode,export}, pipeline/features/{benefit_society,benefit_society_alt_anchor,__init__,policy_similarity}, pipeline/filtering/{fintech_intensity,policy_alignment}, core/{caching,text/token_utils}, config/{filtering,sentiment}。
- 维度: canonical 嵌入 3072→**4096**; `_lg`/text-embedding-3-large 仍 **3072** (勿改)。
- 厂商: "Google⟂OpenAI" → "阿里 Qwen(硅基流动)⟂OpenAI"。

### 3D. 测试
- mock `model='gemini-embedding-2-preview'` → `'Qwen/Qwen3-Embedding-8B'`; mock 维度 canonical 3072→4096 (含 `assert emb.shape==(.,4096)`), `_lg` mock 保持 3072; `text_pipeline_version` mock 同步; cache-key 测试 (`test_dual_compute_coverage.py:216`) 同步。
- `tests/test_gemini_semantic_validity.py` → 重命名 `tests/test_qwen_semantic_validity.py` + 内容 (函数名/docstring/断言文案)。
- 涉及文件: test_16_policy_alignment_dual / test_25_audit / test_benefit_society_embedding / test_benefit_society_alt_anchor / test_benefit_society_audit_combined / test_dual_compute_coverage / test_dual_track_parity_fixes / test_embedding_coprimary_parity(docstring) / test_network_spillover_embedding / test_omni_fix_{benefit,embed,fintech,net_spill,policy} / test_strategic_diff_embedding。

### 3E. Stata .do + 生成脚本
`stata/*.do` 嵌入标签 + `scripts/generate_{missing,all}_labels.py` 的 gemini 嵌入标注。

### 3F. 文档
CLAUDE.md 版本头 (v3.15.0) + memory。

## 4. 🚫 严禁误改（LLM gemini ≠ 嵌入 gemini）

stage 21 情感 LLM 三家族之一是 `gemini-3.1-flash-lite` (short_name `gemini31`)。**与嵌入模型完全无关, 一律不动**:
`gemini31` / `gemini-3.1-flash-lite[-preview]` / `gemini3` / `GEMINI3_API_KEY` / `avg_gemini31_conf_*` / `gemini31_score_` / `gemini31_sentiment` / `gemini31_prob_*` / `gemini31_verified` / `codebook.py:1859 'gemini' in var_name` / `config/sentiment.yaml` 的 LLM 块 / `config/pipeline_v34_rerun.yaml:58 families` / `pipeline/audit/stata_audit.py:435`。
**判别规则**: 字面 `gemini-embedding-2-preview` 一律是嵌入 (改); 含 `31`/`3.1`/`3`/`GEMINI3` 的一律是 LLM (不改); 裸 "gemini" 仅在嵌入语境 (MAIN/canonical/co-primary①/无后缀) 改。

## 5. golden / 生产 (DEFERRED, 本机无生产语料且付费不可逆)

换模 → 每个嵌入派生值变 (4096 维新空间 + 不同模型) → golden **零字节安全**, 须受控全量重生 + 付费全量重嵌 (Qwen 主轨 + staleness/intensity 逐文章 ×2)。本机无生产语料 → 全部 DEFERRED 到生产语料机 (同 v3.14.0 纪律)。`test_{gemini→qwen}_semantic_validity` / `test_real_panel_coprimary_parity` / `test_panel_reproducibility` 在重生前 DEFERRED-skip。⚠ **勿删 `_llm_cache.db`** (复现锚)。
⚠ 生产播种须验 SiliconFlow 更大批 (>256) 是否 429/400; 必要时下调引擎批上限 (当前 ≤2000, 与 `_lg` 共享)。

## 6. 验收门
ruff clean · 全量 pytest 零新增失败 (golden 类 DEFERRED-skip) · dag_consistency · 计数 16/16/35/16 · 探针实证 (§1) · 残留扫描: 全仓无 `gemini-embedding-2-preview` 字面 (除本计划/v3.14.0 历史计划) · LLM `gemini31` 零误改。

**换嵌入模型复核清单补遗 (2026-07-10 八入口审计 G7)**: benefit 负极锚点句 #3 ("金融科技降低银行信贷质量与资产安全性…") 在 Qwen 空间投影为正 (+0.1416 > 符号容差 0.03; 锚点轴整体仍判"锐利", 最小对间隔 0.06481>0.02) — 单句反号被 mean(pos)−mean(neg) 稀释非缺陷, 但**任何后续换嵌入模型时须复核该句措辞/投影符号** (stage 40 benefit 锚点自检日志段), 反号扩大则改写锚句。

## TL;DR
把 canonical 嵌入槽从「gemini-embedding-2-preview (云雾, 3072)」换成「Qwen/Qwen3-Embedding-8B (硅基流动, 4096)」, `_lg`=text-embedding-3-large 不动 → co-primary 变为「阿里 Qwen ⟂ OpenAI large」跨厂商对等双轨。引擎数学层零改 (维度无关), 改动 = config + 新 env key + 4 处默认回退 + 全仓 gemini→Qwen 注释/标签/测试清扫。列 schema 零改动, 计数不变。LLM `gemini31` 严禁误改。golden 重生 + 付费重嵌 DEFERRED 到生产语料机。
