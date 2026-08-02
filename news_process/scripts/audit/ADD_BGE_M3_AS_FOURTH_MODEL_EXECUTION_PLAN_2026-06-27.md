# 执行计划: 本地部署 BGE-M3 作为第四嵌入模型 (`_bge`)

> ⚠ **2026-08-02 状态订正 (聚合中转平台迁移 yunwu.ai → OpenLux)**: 本文成文时,
> 本项目的 OpenAI / Google 两家 LLM 与 `_lg` 嵌入孪生轨经 **yunwu.ai 聚合代理**
> (`https://yunwu.ai/v1`; 环境变量 `YUNWU_API_KEY` / `YUNWU_FULL_KEY`) 路由。
> **2026-08-02 起全项目已迁移至 OpenLux 聚合代理** (`https://api.openlux.ai/v1`;
> 变量更名为 `OPENLUX_API_KEY` / `OPENLUX_FULL_KEY`)。DeepSeek 直连
> (`api.deepseek.com`) 与硅基流动嵌入主轨 (`api.siliconflow.cn`) **不受影响**。
> 下文一切 `yunwu` / `YUNWU_*` 表述均为**成文当时**的事实记录 (含当时对该端点的
> 实测探针结果与授权清单), **不代表当前状态**; 保留原文以维持取证链完整。
> ⚠ 迁移**不改变任何既有数值**: LLM/嵌入缓存键 = (模型名, prompt 文本,
> prompt 版本, temperature), **不含端点地址** (`core/caching.py::_make_key`),
> 故 `_llm_cache.db` 既有条目在迁移后仍逐位命中, 离线 `$0` 复现不受影响。


**日期**: 2026-06-27
**版本**: v3.13.0 (quad-model-embedding)
**前序**: v3.12.0 (tri-model-embedding, `_lg` = text-embedding-3-large) — main=84fd845f
**用户决策 (2026-06-27 拍板)**:
- **D-1 = 加法式新增** (非替换): BGE-M3 作并列第四模型, 保留 text2vec(`_t2v`)/large(`_lg`)。
- **D-2 = config-gated 休眠** (镜像 `_lg`): 无活动 `embedding_bge` 配置 → 不产 `_bge` 列 → golden 字节级不变。

---

## 0. 一句话设计

在既有"三模型并列嵌入"(small 主 / text2vec `_t2v` / large `_lg`)之上, **加第四个本地模型 `BAAI/bge-m3`(`_bge` 后缀)** 作为 small 的强跨架构稳健轨。
**`_bge` 完全镜像 `_t2v`(本地模型), 不是 `_lg`(API 模型)** —— 这是本计划的核心简化:

| 维度 | `_t2v` (text2vec) | `_lg` (large) | **`_bge` (BGE-M3, 新)** |
|---|---|---|---|
| 部署 | 本地 sentence-transformers | API (yunwu) | **本地 sentence-transformers** |
| `base_url` | `local` | `https://yunwu.ai/v1` | **`local`** |
| 维度 | 768 | 3072 | **1024** |
| 路由 | `encode_local` | `get_embeddings_api` | **`encode_local`** |
| 失败语义 | fail-fast (local) | 软降级 NaN (仅 `_lg` twin) | **fail-fast (local), 同 `_t2v`** |
| 稳健性角色 | 弱跨架构 (旧/小中文模型) | 同族容量对照 | **强跨架构 (SOTA 多语言, 1024 维)** |

因 `_bge` 是 **本地** spec, 它天然落入既有 `spec_uses_local()` 的 fail-fast 分支, **不需要 `_lg` 那套 MAIN-fail-fast / API 降级守卫**。引擎 `encode_local` 用 `SentenceTransformer(model_id)` 加载任意 model_id, 按 model_id 隔离 `_LOCAL_MODELS` 缓存与穿透 LLMCache 命名空间 (text2vec 与 bge-m3 各持其模型/各自缓存域), 分块逻辑自适应 `model.max_seq_length`(BGE-M3=8192, 长新闻几乎不切块) —— **引擎层零改动**。

## 1. BGE-M3 技术核对 (落地前已验证)

1. **加载**: `SentenceTransformer('BAAI/bge-m3')` → dense 1024 维。走 `encode_local` 既有路径 (line 322-326), 与 text2vec 同代码路径。✓
2. **无 query instruction**: BGE-M3 dense retrieval **不需要** 指令前缀 (区别于 bge-large-zh-v1.5 的 "为这个句子生成表示…")。镜像 text2vec 的"无前缀"即正确。**铁律: 勿给 `_bge` 加任何指令前缀。**
3. **归一化**: cosine producer 维度/归一无关 (下游算 cosine); chunk-pool 路径逐块 L2 归一 (line 376-385), 与 text2vec 同口径。stage27 投影按 spec 自洽归一。**无需特殊处理。**
4. **维度敏感落盘**: 唯一 = stage27 `27_benefit_embeddings_bge_*.npy` / `27_benefit_direction_bge.npy` (1024 维, sidecar dim 由 `emb.shape[1]` 动态自愈)。其余 `_bge` 列全是 cosine 标量 (维度无关)。
5. **设备/确定性**: cuda:0 (RTX 3090, ~2.3GB 权重轻松放下); `ensure_torch_determinism()` 已覆盖。`_bge` 的 GPU-FP 非确定性同 `_t2v` 既有先例 (休眠态不入 golden, 见 §6)。
6. **首次激活需联网下载** `BAAI/bge-m3` (~2.3GB) 一次, 之后 `HF_HUB_OFFLINE=1` 离线 (引擎 line 70 已 setdefault)。

## 2. 改动清单 (12 文件, 全部 `if _BGE_SPEC:` 休眠门包裹)

| # | 文件 | 改动 | 镜像源 |
|---|---|---|---|
| 1 | `config/features.yaml` | 加**注释模板** `embedding_bge`(不激活) + 休眠门说明 | `embedding_robustness` |
| 2 | `pipeline/filtering/policy_alignment.py` | `_BGE_SPEC` 声明 + `_ALIGN_NAN_COLS` 块 + `_bge` 计算块 (try/except, 同 `_t2v`) | `_t2v` 块 (1077-1124) |
| 3 | `pipeline/panel/runner.py` | `_bge_src` 聚合块 (6 列白名单) | `_lg_src` (1887-1903) |
| 4 | `pipeline/features/benefit_society.py` | `_BGE_SPEC` 声明 + `_specs.append(('_bge', _BGE_SPEC))` | `_specs` `_lg` append |
| 5 | `pipeline/features/strategic_diff.py` | `_BGE_SPEC` 声明 + `_bge` 计算块 | `_lg` 块 (1545-1591) |
| 6 | `pipeline/features/policy_similarity.py` | `_BGE_SPEC` 声明 + `_bge` 链 (a)(b)(c)(d) | `_lg` 链 (117-164,412-424) |
| 7 | `pipeline/panel/network_spillover.py` | `_BGE_SPEC` 声明 + `_bge` 块 (**早退前**) | `_lg` 块 (1749-1781) |
| 8 | `pipeline/panel/stata_export.py` | `_bge` 标签机械派生循环 | `_lg` 派生 (458-467) |
| 9 | `pipeline/features/benefit_society_alt_anchor.py` | section 元组加 `"embedding_bge"` | — |
| 10 | `tests/test_dual_compute_coverage.py` | `_enable_bge` + 休眠锁 + 四族断言 | `_enable_large` |
| 11 | `CLAUDE.md` | Current version → v3.13.0 quad-model | — |
| 12 | (本文件) | 执行计划 | — |

**关键: benefit_society / strategic_diff 的 try/except 守卫无需改动** —— `_bge` 是 local, `spec_uses_local(_BGE_SPEC)=True` → 自动走既有 fail-fast 分支 (与 `_t2v` 同), 不进 `_lg` 软降级分支。仅 `_specs` append 处加 `if _BGE_SPEC:` 门。

## 3. 休眠门铁律 (golden 安全)

- 各 producer 模块级 `_BGE_SPEC = CONFIG.get('embedding_bge', {})`; 所有 `_bge` 计算/落列被 `if _BGE_SPEC:` 包裹。
- `config/features.yaml` **刻意不加任何活动 `embedding_bge` 块** → `_BGE_SPEC={}` → 完全不产 `_bge` 列 → 既有列/行为/golden **字节级不变**。
- `_t2v` 与 `_lg` 与 MAIN(无后缀) 任何逻辑/列 **严禁改动**。

## 4. 缓存命名空间

- `embedding_bge.model = BAAI/bge-m3` (model_id 不同) + `text_pipeline_version: "v1-2026-06-27-bge"` → 穿透 LLMCache 键 `(SCHEMA_VERSION, model_id, chunk文本, version)` 双重隔离, 与 small/`_t2v`/`_lg` 互不串。

## 5. 论文定位 (manuscript framing)

稳健性谱系升级为 **四模型**:
- **MAIN** = text-embedding-3-small (API, 1536) — 主测度。
- `_t2v` = text2vec-base-chinese (本地, 768) — **弱**跨架构独立 (中文专训但旧/小)。
- **`_bge` = BGE-M3 (本地, 1024) — 强跨架构独立** (SOTA 多语言, BAAI, 独立于 OpenAI; 8192 token 上窗)。⇒ 把 `_t2v` 承担的"跨架构独立性"稳健性**显著加强**: 现有两个本地独立模型 (弱 text2vec + 强 BGE-M3) 共同支撑"结论非 OpenAI 单一模型偶然产物"。
- `_lg` = text-embedding-3-large (API, 3072) — 同族容量对照 (休眠)。

论文如启用须报**实测 corr** (休眠态从未真跑); BGE-M3 vs small 是**跨架构** → 预期相关性低于 `_lg`(同族), 是更有力的独立性证据。**铁律**: 四轨各自 just-identified 并排, **禁混进同一 over-identified Hansen J** (重申既有红线)。

## 6. 计数与 golden

- **计数不变** (纯休眠列内扩展, 无阶段增删): STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16 全不变。
- **golden 加法安全**: 休眠态零 `_bge` 列 → `test_panel_reproducibility` 字节级不变 (= baseline, 零新增失败)。

## 7. DEFERRED (生产激活, 本机无生产语料)

1. yunwu 无关 (本地模型); 但需**首次联网下载** `BAAI/bge-m3` (~2.3GB)。
2. 在 `config/features.yaml` 填活动 `embedding_bge` 块 (model/base_url=local/version/batch_size/device) → 解除休眠。
3. 全量重跑 stage 15/25/26/27/46 产 `_bge` 列 (本地 GPU, $0)。
4. golden **加法重生** (新增 `_bge` 列; 受控环境 `PYTHONHASHSEED=0` + BLAS 钉死; GPU-FP 列同 `_t2v`/3 网络列处理)。
5. export.py `_bge` 标签镜像 (40-path 走 fallback 兜底不崩, 同 `_lg` DEFERRED) + codebook `_bge` 条目 (自动随 `_t2v` 发射)。

---
**权威记录**: 本文件 = `_bge` 落地的单一事实源。审计/复审以此为准。
