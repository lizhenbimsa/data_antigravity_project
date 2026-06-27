# 执行计划：新增 `text-embedding-3-large` 作**第三嵌入模型**（保留 text2vec）

> 版本目标：**v3.12.0 · tri-model-embedding**（在既有 主轨 `text-embedding-3-small` + 稳健轨 `text2vec`(`_t2v`) 之上，**新增**第三轨 `text-embedding-3-large`(`_lg`)；三模型并列互为稳健性检验）
> **本文件 = v3（2026-06-27 第二次 98-agent 顶刊评审后，用户采纳评审 dominant 异议：D-A 由"替换"改为"保留 text2vec + 新增 large"）**
> 状态：**定稿待第三轮评审 → 批准实施**（D-D 已升级为：评审过后批准执行 + 执行后审核）

---

## 0. 决策（2026-06-27 终版）

| 代号 | 决策 | 终值 |
|---|---|---|
| **D-A** | 替换 vs 新增第三模型 | **新增 large 作第三模型，text2vec 保留不动**（评审 dominant 方案；跨架构独立性 + 容量对照兼得） |
| **D-B** | 本地消费者 | **不动**（article_sbert / fintech_intensity 继续用 text2vec；不迁 API，无测度变更） |
| **D-C** | 命名 | **`_t2v` 不改名**；新增列用新后缀 **`_lg`**（large，3 字符） |
| **D-D** | 执行 | **本轮评审过 → 批准执行 → 执行后审核 + 终审** |

> ✅ **本方案相对"替换"的优越性（评审认定）**：① 稳健性最强——`_t2v`(text2vec, 跨架构/中文专训独立) 检验模型独立性，`_lg`(large, 同族) 检验容量；② **加法式、零破坏**——既有所有列/缓存/golden/测试/manuscript **完全不变**，只新增 `_lg` 列；③ 无 `_t2v` 改名、无 article_sbert/fintech 测度变更、无归一契约风险；④ FinTextSim 中文专训构念依据保留有效。

---

## 1. 目标与口径
- **纯加法（additive column expansion）**：在 5 个 cosine producer 既有 `MAIN(无后缀=small) + _t2v(text2vec)` 双轨之上，**镜像新增 `_lg`(large) 第三轨**。
- text2vec(`_t2v`)、主轨 small、article_sbert、fintech_intensity **一字不动**。
- 维度：`_lg` = text-embedding-3-large **3072**；`_t2v`=768、small=1536 不变。
- `_lg` 走 `https://yunwu.ai/v1` + `${EMBEDDING_API_KEY}`（与主轨同端点同 key，仅 model 名不同）。
- **golden 加法安全**：既有列哈希不变（输入/引擎确定），仅新增 `_lg` 列；未播种时 `_lg` 优雅 NaN（embed_texts 失败/离线 → 列置 NaN，不破坏既有契约）→ 可**先落码（golden 既有列不动）、后播种重生只追加 `_lg` 列哈希**。

---

## 2. 三模型架构与命名

| 轨 | 模型 | 后缀 | 角色 | 维度 |
|---|---|---|---|---|
| MAIN（canonical） | text-embedding-3-small (API) | 无 | 主结果 | 1536 |
| ROBUSTNESS-A | shibing624/text2vec-base-chinese (本地) | `_t2v` | **跨架构/中文专训独立**稳健性 | 768 |
| ROBUSTNESS-B（新增） | text-embedding-3-large (API) | `_lg` | **同族容量**稳健性 | 3072 |

- 新增列（镜像每个 `_t2v` 列）：`policy_cosine_sim_lg_{full,ctx,ss}`(+`_allv`) · `strat_diff_n5_emb_lg`/`strat_sim_max_emb_lg`/`centroid_diff_emb_lg`/`coh_emb_lg_*`/`strat_diff_lg_*` · `auth_sim_emb_lg_{full,ctx,ss}`(+`_allv`) · `benefit_{mean,std,pos_frac,neg_frac}_lg_*` · `emb_peer_tone_lag1_lg_*`/`bank_emb_sim_mean_lag1_lg`。
- 新增 `.npy`（镜像 `_t2v`）：`27_benefit_embeddings_lg_*.npy`/`27_benefit_direction_lg.npy`（3072 维，sidecar dim 动态）+ benefit_society_alt_anchor 的 `_lg` 对标列。
- `_lg`(3 字符) 短于 `_t2v`(4 字符) → 无新增 Stata ≤32 字符截断风险。

---

## 3. 影响面（统一 `_ROBUSTNESS_SPEC` 镜像模式，5 producer 一致）

**实现范式**：每个 producer 已有 `_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})`；新增 `_LARGE_SPEC = CONFIG.get('embedding_large', {})` 并**镜像其每一处 `_t2v` 计算/赋值/落盘/校验为 `_lg`**。spec 缺失（`{}`）→ `spec_uses_local({})=False` 但无 base_url/api_key → 优雅 NaN（与 `_t2v` 失败同款守卫）。

| 文件 | 现有 `_t2v` 锚点（file:line） | 新增 `_lg` 镜像 |
|---|---|---|
| `policy_alignment.py` | `_ROBUSTNESS_SPEC`@[147](news_process/pipeline/filtering/policy_alignment.py#L147)；`_cosine_for_spec(...,_ROBUSTNESS_SPEC)`@[1061](news_process/pipeline/filtering/policy_alignment.py#L1061)；赋值 ~1086-1099 | 加 `_LARGE_SPEC` + 第三次 `_cosine_for_spec` + `_lg` 赋值 |
| `strategic_diff.py` | `_ROBUSTNESS_SPEC`@[281](news_process/pipeline/features/strategic_diff.py#L281)；[1518](news_process/pipeline/features/strategic_diff.py#L1518)/[1624](news_process/pipeline/features/strategic_diff.py#L1624)/[1721](news_process/pipeline/features/strategic_diff.py#L1721) | 镜像三处 spec 调用为 `_lg` |
| `policy_similarity.py` | `_ROBUSTNESS_SPEC`@[82](news_process/pipeline/features/policy_similarity.py#L82)；`_build_emb(...,spec=_ROBUSTNESS_SPEC)`@[137](news_process/pipeline/features/policy_similarity.py#L137) | 加 `_lg` ghost-anchor 列 |
| `benefit_society.py` | **干净循环** `for suffix, spec in [('', EMBEDDING_CONFIG), ('_t2v', _ROBUSTNESS_SPEC)]:`@[649](news_process/pipeline/features/benefit_society.py#L649) | **加一项 `('_lg', _LARGE_SPEC)`**（最小改动）；`.npy` 落盘随循环自动产 `_lg` |
| `benefit_society_alt_anchor.py` | `for section in ("embedding_api","embedding_robustness")`@[184](news_process/pipeline/features/benefit_society_alt_anchor.py#L184) | 加 `"embedding_large"` |
| `network_spillover.py` | `_ROBUSTNESS_SPEC`@[1440](news_process/pipeline/panel/network_spillover.py#L1440)；`_compute_emb_peer_metrics(...,spec=_ROBUSTNESS_SPEC,suffix="_t2v")`@[1747](news_process/pipeline/panel/network_spillover.py#L1747) | 加平行 `_LARGE_SPEC, suffix="_lg"` 调用 |
| `panel/runner.py` | `_t2v` 聚合 ~[1871-1882](news_process/pipeline/panel/runner.py#L1871) | 聚合列表加 `_lg` 同名列 |
| `panel/export.py` | REQUIRED_PANEL_COLUMNS [364-389](news_process/pipeline/panel/export.py#L364)（硬要求 `_t2v_full/ctx`） | `_lg` 列**软诊断**（未播种可全 NaN，不进硬契约，避免未播种即崩） |
| `panel/stata_export.py` | HEURISTIC_LABELS 35 条 `_t2v`（[338-439](news_process/pipeline/panel/stata_export.py#L338)） | 镜像加 `_lg` 标签（"Large robust=text-embedding-3-large"） |
| `panel/codebook.py` | `_DUAL_TEXT_SPECS`@[1146](news_process/pipeline/panel/codebook.py#L1146) 等 | 加 `_lg` codebook 条目（或确认通用循环自动发射） |

---

## 4. 分阶段执行步骤

### Phase 0 — 前置 Gate（M0，$≈0）
yunwu `text-embedding-3-large` 可用性探针：确认可用 + 同名透传 + 维度 3072（是否支持 `dimensions`）+ 限速 + 计价。❌ 不过 → `_lg` 列保持 NaN 占位、暂不接入（其余无影响）。

### Phase 1 — 配置层
新增 `config/features.yaml::embedding_large`：
```yaml
embedding_large:                          # 第三模型 — text-embedding-3-large
  model: text-embedding-3-large
  base_url: https://yunwu.ai/v1
  api_key: ${EMBEDDING_API_KEY}
  text_pipeline_version: "v1-2026-06-27-emb3large"
```
`embedding_api` / `embedding_robustness` / `fintech_intensity` **不动**。

### Phase 2 — 5 producer 加 `_lg`（§3 镜像模式）
逐 producer 加 `_LARGE_SPEC` + 镜像 `_t2v` 计算/赋值/落盘为 `_lg`；全部复用既有失败守卫（spec 缺/embed 失败 → NaN）。benefit_society 仅加循环一项。

### Phase 3 — panel 聚合 + 契约
runner 聚合加 `_lg`；export.py `_lg` 列入**软诊断**（非 REQUIRED_PANEL_COLUMNS 硬契约，未播种 NaN 不崩）。

### Phase 4 — 标签 / codebook
stata_export HEURISTIC_LABELS + 46_labels.do 镜像加 `_lg`（与 `_t2v` 同款标签文案，model 标注 large）；codebook 加 `_lg` 条目。

### Phase 5 — 测试
`test_dual_compute_coverage.py` → **三模型**：每个 producer 断言 canonical + `_t2v` + `_lg` 三族并存；`test_engine_namespaces_cache_by_model` 加 large model_id 隔离；`test_16_policy_alignment_dual` 加 `_lg` 断言。`_t2v` 既有断言**全部保留不变**。

### Phase 6 — 文档
CLAUDE.md 新增 v3.12.0 段（三模型）；embedding_engine.py docstring/banner 补 `_lg` 第三轨（FinTextSim text2vec 论证**保留**，加一句 large 容量对照）；AI_DISCLOSURE_TEMPLATES.md 6 处补 large；manuscript 稳健性叙述：text2vec=跨架构独立 + large=容量对照（见 §6）。

### Phase 7 — 播种 `_lg` 缓存（M0 Gate）
- 批 1 盘上小样（~1150 文 × cosine producer 三轨）在线播种验证（~$1-3）。
- 批 2 生产级单独批准（§5）。
- `NEWS_PROCESS_LLM_OFFLINE=1` 离线闸对 `_lg` 同样生效；播种后离线 $0 复现。
- ⚠ 若 yunwu 不可用：`_lg` 列保持 NaN，代码/golden 仍 OK（加法安全），择期播种。

### Phase 8 — golden 加法重生
播种后 `PYTHONHASHSEED=0` + BLAS 钉死跑 `generate_golden_snapshot.py`：**既有列哈希不变**，仅**追加** `_lg` 列哈希。过 `test_panel_reproducibility`。

### Phase 9 — 验收门 + 提交
ruff clean · 全量 pytest · dag_consistency · repro gate（既有列零漂移 + 新增 `_lg` 列）→ by-name 暂存提交 → v3.12.0 changelog。

---

## 5. 成本估算
- **仅新增 large cosine 嵌入**（text2vec/article_sbert/fintech 全不动 → 零新增）。
- cosine producer 三轨 `content_full/ctx/ss`：盘上小样 ~$1-3；生产 T=18 ~944k×3 唯一文本 ~1.5-1.8B token @$0.13/1M ≈ **~$200-240**（precise 待 Phase 0 + 去重计数）。
- `_allv` 复用 article embeddings → 零额外（[policy_alignment.py:562](news_process/pipeline/filtering/policy_alignment.py#L562)）；strategic_diff bank-year 聚合自成域；API 请求内不去重（首跑同批重复 content 各算）。
- 存储：benefit `_lg` `.npy` 新增 3072 维（小，仅 benefit 落盘原始向量）。

---

## 6. 方法论（本方案的强项）
- **双重稳健性**：`_t2v`(text2vec) 提供**跨架构 + 中文金融专训独立性**（FinTextSim 构念依据 [embedding_engine.py:160-169](news_process/pipeline/text/embedding_engine.py#L160-L169) **保留有效**）；`_lg`(large) 提供**同族容量上限对照**。审稿人两类质疑都有答案。
- **`_lg` 同族 caveat（仅限 `_lg`）**：large 与 small 同 OpenAI 同 Matryoshka，**预期高度相关**（先验工程预期，**非实测** — 休眠态从未真跑 `_lg`；激活后须报**实测 corr**，勿沿用先验阈值）。manuscript 须报实测 corr 并定位 `_lg` 为"容量稳健性"，**主独立性稳健性由 `_t2v` 承担**。
- **`_t2v` 既有红线不变**：三轨×多模型禁混同一 over-identified Hansen J；各模型各自 just-identified 并排。`_lg` 与 `_t2v` 同为稳健列，**禁同式并入**（沿用既有 corr 高度共线红线）。

---

## 7. golden / 风险 / 回滚
- **golden 加法安全**：既有列输入与引擎确定性不变 → 既有列哈希**逐位不变**；仅追加 `_lg` 列。未播种 → `_lg` 全 NaN（合法、可入 golden 或留 NaN）。**勿删 `_llm_cache.db`**。
- **缓存隔离**：large model_id 独立命名空间（键含 model_id 维度，[caching.py:287-291](news_process/core/caching.py#L287-L291)）；不撞 small/text2vec。
- **回滚极简**：删 `embedding_large` config + revert `_lg` 代码 → 既有一切不变（`_lg` 是纯增量）。**零不可逆**（除生产播种花费，但 `_lg` 列删除即净空）。
- **风险面极小**：无 `_t2v` 改名、无 article_sbert 归一契约、无 fintech 测度变更、无既有列值变 → 评审 6 P0 中**仅"成本透明"与"yunwu 探针"残留**，其余（归一/改名/测度/crash）**全部不适用本方案**。

---

## 8. 验收门
ruff clean · 全量 pytest（三模型 dual→triple coverage）· dag_consistency · **repro gate 既有列零漂移**（关键：证明加法未扰动既有列）+ `_lg` 列新增 · corr(small,`_lg`) 与 corr(small,`_t2v`) 对照报告（前者≈0.99 容量、后者更低=独立性，作 §6 实证）。

## TL;DR
新增 `embedding_large` config + 5 producer 镜像 `_ROBUSTNESS_SPEC` 加 `_lg` 第三轨 + panel/标签/codebook/测试加 `_lg` + 文档。**纯加法、既有列零变、golden 仅追加、回滚净空、风险面最小**。text2vec 保留=跨架构独立稳健性，large 新增=容量稳健性。生产成本 ~$200-240（仅新增轨）。M0-gate 下先探针+小样,再批生产播种与 golden 追加重生。
