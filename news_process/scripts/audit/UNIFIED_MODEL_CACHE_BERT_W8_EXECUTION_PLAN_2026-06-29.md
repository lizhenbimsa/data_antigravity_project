# 全项目统一缓存策略 — 收口 BERT 模型推理缓存 (W8) 执行计划 (2026-06-29, v2 含 R1 评审修正)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> **本文件是本次实现的唯一权威来源 (single source of truth)。**
> 上游沿革: `CACHE_STRATEGY_SPEC_V2_2026-06-25.md` (13 项, 批1/2/3 = 10 safe 项已落地推送 main=3e5653f3 / W5 激活 main=93f9f2eb;
> 批4 = W7/W8/W10 needs-regen DEFERRED)。本计划只**收口三大模型族统一缓存中唯一未落地的 BERT 推理缓存 (W8)**,
> 把 LLM/嵌入/BERT 三族缓存的"物理库分治、逻辑接口统一"在代码层落实 + 文档定稿。
> **v2 修订**: 折入 R1 九智能体对抗评审 0 P0 / 0 P1 + 27 项 P2/P3 全部修正 (helper 化复合键 + label_map/batch 维 + 确定性 fail-fast + stats 落点 + 测试重构 + 验收改逐文件 A/B)。
>
> **本机现实铁律 (不可违背)**: 本机 `data/raw` 为空、面板 T=2 小样、无生产语料、付费/重生不可逆 →
> 任何"改测度→重生 golden / 付费播种"一律 **DEFERRED 到生产语料机**。本机只落地 **golden-safe (字节中性)** 改动。

---

## §0 现状总览 (三族缓存的真实落地状态 — 经本仓代码 ground-truth)

| 模型族 | 缓存抽象 | 物理库 | 落地状态 | 证据 (文件:行) |
|---|---|---|---|---|
| LLM (大模型) | `core/caching.py::LLMCache` | `_llm_cache.db` | ✅ 已落地 | `tone_llms.py:2382`, `llm_peer_iv.py:805`, `network_spillover.py:1501` |
| 嵌入 (Qwen/large) | 同 `LLMCache` (穿透) | `_llm_cache.db` | ✅ 已落地 (v3.14/3.15 全 API) | `embedding_engine.py:277-281/405-411`, `policy_alignment.py:621`, `article_sbert.py:485`, `fintech_intensity.py:169` |
| 验证变体 LLM | 同 `LLMCache` (隔离库) | `_llm_cache_validation.db` | ✅ 已落地 (W4) | `prompt_sensitivity.py:1656`, `entity_masking.py:991` |
| MinHash 签名 | sidecar (内容寻址) | `_minhash_cache/` | ✅ 已落地 (W9) | `tests/test_w9_minhash_cache.py` |
| 阶段级增量跳过 | config/产物哈希 | parquet metadata | ✅ 已落地 (W5) | `run_pipeline_function.py:163/207/598/696`, `tests/test_w5_skip_unchanged.py` |
| **BERT (finbert_cn / fin_sent_zh / finbert2)** | **无** | **无** | ❌ **未落地 (本计划收口)** | `tone_berts.py:85/1115/1151` 明示"无 _llm_cache.db" |

**结论**: 三大模型族中, **唯有 BERT 推理无任何缓存** —— 这是"统一缓存策略"的最后一块拼图。
本计划落地 **W8 (BERT 推理缓存)**, 复用同一 `LLMCache` 抽象 + 独立物理库 `_local_model_cache.db`,
完成 LLM / 嵌入 / BERT 三族缓存的统一收口。

### §0.1 已自然解决 / 刻意不做 (避免范围蔓延)

- **W7 (SBERT 穿透缓存) — 已被 v3.14.0 自然解决, 无需任何动作**: stage 25 `article_sbert` 自 v3.14.0
  弃本地 SentenceTransformer、改走 `embedding_engine.embed_texts` API 双轨 → 已天然经 `_llm_cache.db` 穿透缓存
  (`article_sbert.py:198/485`)。原 W7 的"本地模型穿透缓存"前提 (本地 t2v/bge) 已不存在 → **作废, 不再实现**。
- **W10 (词典 powerset 单次扫描重构) — 非缓存项, 本计划不含**: W10 是 `tone_words` 的**计算重构**, 与"模型推理缓存"无关;
  仍属既有 rule-ablation DEFERRED 批, 与本次缓存统一**正交**, 不纳入。
- **不重构既有 ~10 处 `os.path.join(output_dir,'_llm_cache.db')` 硬编码 callsite**: 工作正常, 批量迁移=纯 churn + 真实风险。
  本计划只新增**集中式 helper** 供 BERT 新缓存使用 + 文档登记, **不动**既有 callsite (R1 P2.9 确认: 迁移不在范围)。

---

## §1 实现纪律 (落地前必读)

1. **golden 铁律**: 勿删 `_llm_cache.db` / `_llm_cache_validation.db` / (启用后) `_local_model_cache.db`; 本机不跑生产语料、不重生 golden、不付费播种。
2. **W8 default-OFF 是 golden-safe 的全部依据** (R1 九评审一致确认字节中性): 新增 `inference_cache: false` 默认关 →
   `run_all_models` 走**逐字未改的旧路径** (`_run_all_models_uncached`) → stage 23 产物**字节级不变** → golden 零风险。
   缓存路径仅在显式 `inference_cache: true` (生产受控播种窗口) 时才被触发。
3. **共享 helper 强制复用** (禁造轮子): 缓存类一律 `core/caching.py::LLMCache` + `make_key`; 三库路径一律走新 helper
   `core/caching.py::resolve_cache_db_path(output_dir, kind)`。
4. **缓存值 JSON 安全性铁律 (W8 关键不变量, R1 P2.6/P3.5/P3.16 加固)**: 缓存包裹的是 `run_all_models` 输出, 其逐文章结果
   `{label, probabilities(已 round 4), num_windows}` **永不含 NaN/inf** —— 只可能是 `_empty_result` (label='中性', 概率 0.0, num_windows=0,
   `tone_berts.py:801-812`) 或真实结果 (round 4 位有限浮点 + num_windows≥1, `:789-795`)。
   **失败哨兵 `_failure_result` (NaN 概率 / num_windows=-1, `:814-830`) 仅由下游 `process_all_models` 异常兜底 (`:890/899/906`) 产生, 不在 `run_all_models` 内、绝不进缓存**。
   ⚠ 注意 `json.dumps(allow_nan=True)` 会无损往返 NaN → "JSON 往返无损"不足以证明哨兵不入缓存; 真正的锁是 **(a) `run_all_models` 输出全有限 (b) `cache.put` 永不以 NaN/哨兵形状值被调** (见 §2 W8-D 测试)。
5. **enabled 须确定性模式 (R1 P3-15 / R2 P3-5 fail-fast)**: `inference_cache: true` 时 `deterministic_mode` 必须 ∈ {`cpu_strict`,`gpu_strict`}, 否则 `load_all` 启用块 **raise**。两重理由: (a) 严格模式 `USE_AMP` 恒 False (`tone_berts.py:211-215`) → logits 有限 → 兑现 §1.4 no-NaN; (b) 缓存即跨机复现锚 (§1.7), 须 `use_deterministic_algorithms` 生效 (仅 strict 模式设, `:191`); `mode=off` 即便纯 CPU 无 AMP/NaN, 其非确定算法也破坏锚点忠实性 → 一并拦截。
6. **golden 安全的承重论证 = cold-seed 转发 (R2 P2.1-2.4/P3.1 重新定位; RR1 P3.4 精化)**: 真正使 enabled-path golden 安全的**不是** batch-不变性, 而是: **空缓存冷播种时 `_run_all_models_cached` 把 miss 文章 (冷启动即全部) 转发 `_run_all_models_uncached`, `process_all_models` 仍按 `ARTICLES_PER_BATCH` 同样分块**; cold==warm 仅需"命中即重放所存值"(平凡)。⚠ **精化 (RR1 P3.4)**: 多 chunk 单 run 中, 靠前 chunk 的 put 会让靠后 chunk 对**重复内容**命中 → 靠后 chunk 转发的子集比纯 uncached **更短** → mini-batch 组成变。故"冷播种 ≡ uncached 字节一致"的**充分条件 = 纯 CPU 单线程确定性 BLAS** (batch 组成字节不变, 跨 chunk 去重导致的子集收缩也不改任一文 logits); GPU 上由 §5.2② 实证硬门兜底 (半播种→全量 == from-scratch uncached, 恰覆盖跨 chunk 去重漂移)。生产**首选纯 CPU 播种** (§5.1)。**golden 永远在空缓存冷全量上重生/重验, 绝不在 partial-miss 已填充的缓存上**。
   - **batch-组成-不变性是二级 (非承重) 主张**: 仅 partial-miss 增量 (语料新增, 只前向 miss 子集) "== 全量重算" 依赖它; 该集合**不在 golden 内**, 故即便不变性不完美也不污染 golden, 只影响新增语料增量精度, 由 §5.2② 实证门把关。
   - 工程依据 (近似成立, 非无条件字节): masked transformer padding 位 `attention_mask=0` → softmax 前置加 `finfo.min` (HF 实现, **非** `-inf`) → 权重 ≈0; 线性层按行独立。**纯 CPU + 单线程确定性 BLAS** 下归约序固定 → 字节级成立; **GPU (cuBLAS 按形选 kernel) 不保证** → 此时 partial-miss==full 唯由 §5.2② 实证门保障 (硬门, 不过则该环境禁用 W8 增量、回退 uncached)。
7. **`_local_model_cache.db` = 复现锚 (R1 P3-2 freeze-anchor 语义)**: 复合键刻入**模型身份 (short_name) + config 定义的计算决定量** (maxlen/labels/labelmap 内容哈希/vocab/det/amp/stride/ibs/apb/ckpt, 共 11 维), **刻意不刻运行期 DEVICE** —— 与 `_llm_cache.db` 同纪律: 缓存即跨机复现锚, 任何机器读已播种缓存 → 字节级复现 golden (而非各自按本机设备重算)。`ibs`/`apb` 入键仅隔离**跨播种会话改 config 批宽**这一轴 (保守失效), **不**保护同一 run 内 partial-miss 的实际 batch 组成差异 (后者由 §1.6 纯 CPU 不变性 / §5.2② 实证承担)。
8. **计数不变**: 纯列内/谓词内改动, 无阶段/列增删 → STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16 全不变。

---

## §2 改动清单 (5 个文件 + 1 个新测试文件)

### W8-A · `core/caching.py` — 三库路径集中 helper + §5 治理文档定稿 (golden-safe, 纯新增)

- **新增模块级 helper** (放在 `LLMCache` 类定义之后):
  ```python
  _CACHE_DB_FILENAMES = {
      'production': '_llm_cache.db',            # LLM (stage 21/llm_peer) + 嵌入 (stage 15/25/26/27/network) 生产锚点
      'validation': '_llm_cache_validation.db', # 验证变体 LLM (W4: prompt_sensitivity / entity_masking)
      'local_model': '_local_model_cache.db',   # 本地深度模型推理 (W8: stage 23 BERT)
  }

  def resolve_cache_db_path(output_dir: str, kind: str = 'production') -> str:
      """解析三大缓存物理库的绝对路径 (统一接口, 物理库分治)。

      kind ∈ {'production','validation','local_model'}; 未知 kind → ValueError (fail-fast, 防静默落错库)。
      既有 callsite 多以字面量直拼 — 本 helper 是其集中化版本; 新缓存 (W8 BERT) 走此 helper, 既有 callsite 不迁 (纯 churn)。
      """
      import os as _os
      if kind not in _CACHE_DB_FILENAMES:
          raise ValueError(f"未知缓存库 kind={kind!r}; 合法值: {sorted(_CACHE_DB_FILENAMES)}")
      return _os.path.join(output_dir, _CACHE_DB_FILENAMES[kind])
  ```
- **§5 docstring 定稿**: 模块 docstring 末段"如 _local_model_cache.db"前瞻语气 → 已实现陈述: 三族缓存收口完成
  (LLM/嵌入 → `_llm_cache.db`; 验证 → `_llm_cache_validation.db`; BERT/本地模型 → `_local_model_cache.db`, W8 2026-06-29 落地 default-off)。`SCHEMA_VERSION='v1'` 不变量不碰。
- **golden**: safe (纯新增函数 + 文档)。

### W8-B · `pipeline/sentiment/tone_berts.py` — BERT 推理缓存 (核心; default-off dispatch)

**严格 "off 路径逐字未改" dispatch 模式**, 保证 default-off 字节中性。

1. **顶部 import 区** (与现有 `import hashlib`/`os` 同处) 加 `import json`, 并加模块级 `from news_process.core.caching import LLMCache, resolve_cache_db_path` (R2 P3-13; default-off 下仅 import 不实例化 → golden-safe)。
2. **⚠ 模块级常量必须放在 `BERT_PARAMS = ... (:157)` 之后** (R1 P2.1: `BERT_PARAMS` :157 才定义, 放 import 区会 NameError)。
   落点 = `ARTICLES_PER_BATCH` 块之后 (`:409` 后):
   ```python
   # W8 BERT 推理缓存版本门 (§5-D 内联常量): 改动任何影响 BERT 推理输出的数学层
   # (窗口切分/池化/argmax/label_map 推导/分窗 batch) 须 bump 此号, 让旧 _local_model_cache.db 静默失效。
   _BERT_CACHE_VERSION = "bert-v1-2026-06-29"
   _BERT_INFERENCE_CACHE = bool(BERT_PARAMS.get('inference_cache', False))  # default-off (见 config 注释)
   ```
3. **`_checkpoint_fingerprint(model_path)` helper** (模块级, 仅 enabled 时调用):
   - 本地目录: `sha256(config.json 内容字节 + sorted([(文件名, 文件大小) for *.safetensors/*.bin/*.pt]))` (cheap, 只 stat 不读权重)。
   - 非本地 (HF hub id): 退化 `f"no-ckpt:{model_path}"` (失去换版保护; 由 vocab 指纹 + label_map 内容 + 加载期 `_label_order_consistent` fail-loud 守卫部分补偿; **R1 P3-11/P3-14/P3-17 已披露**, §5 列 DEFERRED 增强)。
4. **`_compute_composite(...)` 纯 helper (模块级, R1 P2.5/P2.3/P2.7/P2.10 — 抽出供测试直接调, 含 label_map/batch 维)**:
   ```python
   def _compute_composite(*, short_name, max_length, num_labels, label_map,
                          vocab_fp, det_mode, amp, stride, inf_batch, art_batch, ckpt) -> str:
       """BERT 推理缓存复合身份串 (model_id 槽塞此, content 塞 prompt 槽)。
       刻入 config 定义的全部计算决定量; 刻意不刻 DEVICE (见 §1.7 freeze-anchor)。"""
       lmap = hashlib.sha256(repr(sorted(label_map.items())).encode()).hexdigest()[:16]
       return (f"{short_name}|maxlen={max_length}|labels={num_labels}|lmap={lmap}"
               f"|vocab={vocab_fp}|det={det_mode}|amp={int(amp)}|stride={stride}"
               f"|ibs={inf_batch}|apb={art_batch}|ckpt={ckpt}")
   ```
5. **`MultiModelSentimentEngine.__init__`** 增字段: `self._cache=None`; `self._cache_enabled=_BERT_INFERENCE_CACHE`;
   `self._composites={}`; `self._model_paths={}` (全 inert 赋值, off 路径无影响)。
6. **`load_all`**: 加载成功后无条件 `self._model_paths[short_name] = model_path` (单字典赋值, model_path 在 `:493` 已算, 对 off 无影响)。
   load 循环**结束后**, **仅当 `self._cache_enabled`**:
   - **fail-fast (R1 P3-15)**: `if _DETERMINISTIC_MODE not in ('cpu_strict','gpu_strict'): raise RuntimeError(...)` (enabled 必确定性, 保 no-NaN)。
   - 打开缓存 `self._cache = LLMCache(resolve_cache_db_path(CONFIG['paths']['output_dir'], 'local_model'))`。
   - 为每个已加载模型 `self._composites[sn] = _compute_composite(short_name=sn, max_length=cfg['max_length'], num_labels=cfg['num_labels'], label_map=cfg['label_map'], vocab_fp=_tokenizer_fingerprint(self.tokenizers[sn]), det_mode=_DETERMINISTIC_MODE, amp=USE_AMP, stride=WINDOW_STRIDE_RATIO, inf_batch=INFERENCE_BATCH_SIZE, art_batch=ARTICLES_PER_BATCH, ckpt=_checkpoint_fingerprint(self._model_paths[sn]))`。
   - 日志一行: 启用 + 库路径 + `self._cache.size()`。
7. **`run_all_models` dispatch** (核心 golden-safe 机制):
   - 把**当前 `run_all_models` 方法体逐字重命名**为 `_run_all_models_uncached(self, texts)` (保留 `@torch.inference_mode()`)。
   - 新:
     ```python
     @torch.inference_mode()
     def run_all_models(self, texts: list) -> dict:
         if not self._cache_enabled or self._cache is None:
             return self._run_all_models_uncached(texts)   # ← off 路径: 逐字旧实现, 字节中性
         return self._run_all_models_cached(texts)
     ```
8. **`_run_all_models_cached(self, texts)`** (仅 enabled):
   - 逐 (text, model) 查缓存。**content 口径与 uncached 空文本判定严格对齐 (R1 P3-3/P3-4)**:
     `content = text if (isinstance(text, str) and text.strip()) else ""` (空/空白/非 str 全归一为 `""` → 同 key 去重)。
     `hit = self._cache.get(self._composites[sn], content, prompt_version=_BERT_CACHE_VERSION)`。
   - 任一模型 miss 的 text 入 **有序 list** `miss_idx` (R1 P3-6: 子集构建与回填须同序迭代); 命中值 `json.loads` 还原。
   - **`if miss_idx:`** (R1 P3-3 空守卫, 防空子集触发 GPU no-op) → `fresh = self._run_all_models_uncached([texts[i] for i in miss_idx])`;
     回填 + `self._cache.put(self._composites[sn], content_of(gi), json.dumps(r, ensure_ascii=False, allow_nan=False), prompt_version=_BERT_CACHE_VERSION)`。
     ⚠ **`allow_nan=False` (R2 P3-9 写边界硬门)**: 把 §1.4 no-NaN 不变量从散文升级为 fail-loud — 万一未来某改动让 `run_all_models` 漏出 NaN/inf, `json.dumps` 直接 raise ValueError (而非静默写 `NaN` token 污染 golden)。
   - **put 在 `_run_all_models_uncached` 成功返回之后** → 前向异常冒泡时**零半写** (R1 seam 评审确认); `process_all_models` 异常兜底逐篇重试 (现有路径不变, 失败哨兵由其产生, 不进缓存)。
   - ⚠ 逐模型部分命中 (A 命中/B miss 同一文章): 该文入 miss_idx 后被整文重算全部模型 (A 命中算力丢弃, 确定性下逐字段相等, 可接受; R1 P3-6 文档承认)。
   - 返回 `{short_name: [result_per_text]}`, 形状/语义与 uncached 严格一致。
9. **`unload_all`**: close 前先存 stats (见 step 10); 末尾 `if self._cache is not None: self._cache.close(); self._cache=None` (off 恒 None=no-op)。
10. **stats 摘要落点 (R1 P2.2/P3.1/P3.10/P3.13 — 死代码修正)**: `main()` 在 `:1418` 调 `engine.unload_all()` **早于**收尾日志 →
    必须在 `engine.unload_all()` **之前**捕获 `_bert_cache_stats = engine._cache.stats() if engine._cache else None` + `size()`, 收尾处打印 (与 stage 21/嵌入对齐)。
11. **日志/docstring 措辞**: 三处 (模块 docstring `:85` + banner `:1115` + env-info `:1150-1151`) 的"无 LLM API、无 _llm_cache.db" → "默认无缓存 (纯本地推理); 启用 inference_cache 时经 `_local_model_cache.db` 穿透 (default-off)" (R2 P3-10 补 :85)。纯日志 golden-safe。
- **golden**: safe (default-off → `run_all_models` 逐字旧实现 → 产物字节不变)。enabled 后 needs-regen (见 §5)。

### W8-C · `config/sentiment.yaml` — 新增 `inference_cache: false` (default-off)

`tone_berts:` 块内 (`strict_models: true` `:289` 之后, `models:` `:292` 之前):
```yaml
    # W8 (2026-06-29) BERT 推理缓存开关 (default-off, golden 安全铁律)。
    # false (默认): run_all_models 走逐字旧路径, stage 23 产物字节级不变 (无任何缓存读写)。
    # true: 仅在生产受控播种窗口启用 (PYTHONHASHSEED=0 + 全 BLAS 线程钉 1 + 固定 inference_batch_size/articles_per_batch + GPU 保留 + HF 离线);
    #   逐 (文章×模型) 缓存推理结果到 _local_model_cache.db, 命中即免重算 (只前向 miss 文章)。
    #   ⚠ 须 deterministic_mode ∈ {cpu_strict,gpu_strict} (否则 load_all fail-fast raise; AMP-on 会产 NaN/非确定)。
    #   ⚠ 编辑任一模型 label_map / max_length / inference_batch_size 等会自动改复合键 (cache miss, 安全);
    #     改 BERT 推理数学层 (窗口/池化) 须 bump _BERT_CACHE_VERSION。启用后须受控 golden 重生 (见执行计划 §5)。
    inference_cache: false
```
- **golden**: safe (新增默认 false 的 flag, 不改任何现值)。

### W8-D · `tests/test_w8_bert_inference_cache.py` — 新测试 (纯逻辑, `pytest.importorskip("torch")`)

测试**不加载真实模型** (monkeypatch 注入假 `models`/`loaded_configs`/`tokenizers` + stub `_run_all_models_uncached` 计数调用):
- `test_default_off_delegates_to_uncached`: 默认 `_cache_enabled is False` → `run_all_models` 等价 `_run_all_models_uncached` (stub 每次被调, 返回同对象)。
- `test_enabled_caches_and_skips_uncached_on_second_call`: enabled (tmp_path 库) → 首跑 stub 全 miss 被调; 同 texts 二跑 stub **不再被调** (全命中), 结果逐字段相等。
- `test_partial_miss_only_forwards_missing`: 缓存 2/3 → 跑 5 篇 (2 旧+3 新) → stub 仅以 3 篇 miss 子集被调一次。
- `test_per_model_partial_hit_reforwards_all_models` (R1 P3-6): 文章 X 对 A 命中 / B miss → X 入 miss_idx, stub 收到 X (全模型重算), 结果仍正确。
- `test_compute_composite_sensitive_to_every_dim` (R1 P2.5 — 调**纯 helper** `_compute_composite`): 逐一改 short_name/maxlen/num_labels/label_map/vocab_fp/det/amp/stride/inf_batch/art_batch/ckpt → 复合串变; 全同 → 串同。
- `test_failure_sentinel_never_cached` (R1 P2.6 — 异常路径): enabled + stub 对 poison text raise、其余成功 → 驱动 `process_all_models` → 断言 (a) poison 行写 `_failure_result` (num_windows=-1), (b) good 行入缓存, (c) poison content **不在** `_local_model_cache.db` (直查 sqlite)。
- `test_no_nan_boundary_and_json_roundtrip` (R1 P3-5/P3-9/P3-12/P3-16 — 重构): 断言 `_empty_result()` 概率全 `math.isfinite` 且无 NaN; `_failure_result()` 概率全 NaN; 一个**有限**真实形状 dict 经 `json.dumps/loads` 字节无损往返; **spy `cache.put`** 确认其 value 永不含 `'NaN'`/`'Infinity'` 子串且 `num_windows != -1`。
- `test_fail_fast_requires_deterministic_mode` (R1 P3-15): enabled + `deterministic_mode='off'` → `load_all` 启用块 raise。
- `test_resolve_cache_db_path`: 三 kind → 三文件名; 未知 kind → `ValueError`。

> ⚠ **覆盖边界 (R2 P3-11)**: 以上 9 测试均 stub `_run_all_models_uncached` → 只验缓存**管道** (dispatch / miss 有序 / no-NaN 结构 / fail-fast / 复合键敏感 / 哨兵不入库)。`cold==warm` / `partial-miss==full` 的**数值等价**无法在本机 (无真实模型) 测, 唯由 DEFERRED §5.2② 受控实证门把关。

### W8-F · RR1 (结果评审第一轮) 落地精化 (golden-safe; 仅 enabled/测试路径, off 路径不变)

R1+R2 评审定稿后, 对**已实现代码**的第一轮结果评审 (6 智能体, 0 P0/0 P1, 全 SHIP) 折入以下精化:
- **P2.1**: enabled 播种写库由逐 (文章×模型) `put()` (每次 commit) 改为 **`put_batch` 每模型一次 commit** —— 冷全量播种 (千万级写) 的提交开销骤降; 复用嵌入缓存既有 `put_batch`。写值字节不变 → golden-safe。
- **P3.1**: deterministic_mode fail-fast **前移到 `load_all` 顶部** (模型加载之前) → 误配即省去昂贵 GPU 加载。
- **P3.9/P3.3**: 复合键构建循环抽成 `_build_composites(loaded_names)` 方法 → 字段接线 (cfg→helper) 可直接单测 (`test_build_composites_wires_runtime_values`), 无需真实模型。
- **P3.5/P3.11/P3.13**: 回填用 `fresh[sn]` 直取 (漏模型 → KeyError 清晰, 非 IndexError); **全部序列化成功后再统一 put_batch** (all-or-nothing per batch, NaN fail-loud 在 put 前 → 零半写)。
- **P3.7**: `_checkpoint_fingerprint` 异常窄化为 `(OSError, ValueError)` (文件系统类瞬时错误退化, 意外异常 fail-loud)。
- **P3.2/P3.8**: 加注释 (轨身份由 content 携带; amp 维在 enabled 下恒 0, 保留作 defense-in-depth)。
- **新增 3 测试**: `test_checkpoint_fingerprint_local_and_hub` (P3.10) / `test_cache_version_bump_invalidates` (P3.15) / `test_build_composites_wires_runtime_values` (P3.9) → 总 12 测试。

---

## §3 验收门禁 (本机, 提交前必过; R1 P2.8 改逐文件 A/B)

1. `pytest tests/test_w8_bert_inference_cache.py -v` 全绿。
2. **off 路径回归 (字节中性主证据之一)**: `pytest tests/test_tone_berts_deterministic.py tests/test_23_tone_berts.py tests/test_omni_fix_berts.py -v` 全绿。
3. `pytest tests/integration/test_dag_consistency.py` 绿; 计数不变 (16/16/35/16)。
4. **off 路径字节中性代码论证 (主证据)**: `run_all_models` off 分支逐字调 `_run_all_models_uncached`; 无 config 时 `_BERT_INFERENCE_CACHE=False` → 缓存代码全不执行 (R1 九评审已独立核验)。
5. **逐文件 A/B churn 检 (替代不可靠的全量 stash, R1 P2.8; R2 P3-14 路径限定)**: 先 `git checkout -- ../data/processed/v3_5_1_constants.json` + `export PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1`;
   **路径限定** `git stash push -u -- pipeline/sentiment/tone_berts.py core/caching.py config/sentiment.yaml tests/test_w8_bert_inference_cache.py` (仅入栈本会话文件 + 新 test, **不清扫并发会话 untracked WIP**) → 跑 `pytest tests/test_23_tone_berts.py tests/test_tone_berts_deterministic.py tests/test_omni_fix_berts.py -q` 记 BASE → `git stash pop` → 同命令记 MINE → 断言**通过/失败集 IDENTICAL** (default-off dormant 故必然一致)。两次 run 之间各还原 constants.json。
6. `ruff check .` clean; `python -m py_compile` 改动文件全过。

---

## §4 提交纪律 (by-name + 逐文件 diff 复核 + 防 pytest-bump)

- **by-name 暂存** (绝不 `git add .` / `-A`): 仅 `core/caching.py` · `pipeline/sentiment/tone_berts.py` · `config/sentiment.yaml` ·
  `tests/test_w8_bert_inference_cache.py` · `scripts/audit/UNIFIED_MODEL_CACHE_BERT_W8_EXECUTION_PLAN_2026-06-29.md` (+ 必要时 CLAUDE.md/MEMORY)。
- **逐文件 diff 复核 (R1 P2.9 — 共享树并发协同改动防护)**: 提交前对 5 个文件逐一 `git diff <file>` 确认**只含 W8 hunk**;
  若发现 `core/caching.py` / `config/sentiment.yaml` 已被并发会话协同改动, 该文件改走外科 `git apply --cached` 仅暂存本会话 hunk (Method-C 先例), 不整文件 add。
- **跑 pytest 会 bump `data/processed/v3_5_1_constants.json`** → 提交前 `git checkout -- ../data/processed/v3_5_1_constants.json`, **绝不暂存**。
- HEREDOC commit message + `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`; 不 `--no-verify`; 不 amend; 在 `main` 提交并 `git push origin main`。

---

## §5 DEFERRED (生产语料机, 本机不可做)

启用 `inference_cache: true` 后的生产落地 (本机无生产语料 + 不可逆):
1. **受控环境播种**: `PYTHONHASHSEED=0` + **固定 `inference_batch_size`/`articles_per_batch`** + `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`;
   **首选纯 CPU 播种** (`MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1` + 强制 `DEVICE=cpu`) 使 §1.6 字节不变性真实成立; **若用 GPU 播种, §5.2② 为启用前硬前置** (CPU 线程钉死对 cuBLAS 无效 → GPU partial-miss 不变性不被任何 config 保证)。全量重跑 stage 23 → `_local_model_cache.db` 播种逐 (文章×模型×轨) 结果。
2. **冷暖 + 增量一致性验证 (硬门, R1 P2.4③ / R2 P2.1-2.4)**: 同环境 ① 冷跑 (空缓存全量) == 暖跑 (满缓存全量) 产物 content-sha256 逐位一致;
   ② **半播种后再跑全量 (一半命中/一半 miss)** == 一次 from-scratch 全量 uncached 跑。**这是 enabled-path 数值等价的唯一实证门**: 若 ② 失败 (典型 = GPU batch 组成漂移), 则该环境**禁用** `inference_cache` (回退 uncached), 不得据此缓存重生 golden。
3. **受控 golden 重生 (措辞精确, R1 P3-8 / R2 P3-1)**: golden **始终在空缓存冷全量上重生** (§1.6 承重论证: 冷播种逐批转发 ≡ uncached) → 与 from-scratch 数值一致, 启用本身不改值; 须受控重生/重验的根因是**把 `_local_model_cache.db` 纳入复现锚 + 防跨机漂移**。stage 23 列哈希纳入 golden (排除 3 BLAS-FP 网络列); `test_panel_reproducibility` 绿。
4. **HF hub ckpt 指纹增强 (R1 P3-11/P3-14 DEFERRED TODO)**: 播种前为 hub 模型 (无本地 `models/<sn>` 副本) 解析其 HF cache snapshot dir, 对 config.json + 权重文件大小做与本地目录同款 cheap 指纹, 取代 `no-ckpt:<id>` 退化 (闭合 §5-E "资源以内容入键"对 hub 模型的残留偏离)。
5. **披露**: codebook/方法附录登记: ① BERT 缓存 = freeze-anchor (跨机读冻结字节, 非各机重算); ② HF hub 模型 ckpt 指纹退化 `no-ckpt:<id>` (纯权重换版/极性重排保护退化为加载期 `_label_order_consistent` fail-loud + 手动 `_BERT_CACHE_VERSION` bump; `HF_HUB_OFFLINE` 冻结本地快照为主要实操护栏); ③ 本地 finbert2 ckpt 为 size-only cheap 指纹 (同字节大小权重改动须手动 bump)。
6. **勿删** `_local_model_cache.db` (启用后即成 stage 23 复现锚)。
7. ⚠ 与 W5 联动: W5 阶段级 skip 已覆盖"输入 parquet 哈希不变即整阶段跳过" → W8 主增益是**输入部分变化** (部分文章新增) 时逐文章免重算; 全量不变场景 W8 与 W5 等效 ($0)。

---

## 附: 风险矩阵 (R1 修正)

| 风险 | 缓解 |
|---|---|
| off 路径意外改产物 | dispatch 逐字 `_run_all_models_uncached`; `test_default_off_delegates_to_uncached` + 逐文件 A/B (§3.5); R1 九评审独立核验字节中性 |
| 缓存值 NaN/哨兵进缓存破 golden | `run_all_models` 输出全有限; 失败哨兵在 `process_all_models` 不进缓存; `test_failure_sentinel_never_cached` + put-spy (`test_no_nan_boundary_and_json_roundtrip`) |
| 复合键漏维 → silent stale | 复合串 11 维 (**short_name**/maxlen/labels/**labelmap 内容哈希**/vocab/det/amp/stride/**ibs**/**apb**/ckpt) + `_BERT_CACHE_VERSION`; `test_compute_composite_sensitive_to_every_dim` |
| batch 组成致命中值≠重算值 | golden 安全由 **cold-seed 逐批转发≡uncached** 承重 (§1.6, 与 batch 不变性无关); partial-miss==full 由纯 CPU 单线程不变性 + §5.2② 实证**硬门**保障 (GPU 不过则禁用增量); ibs/apb 入键仅隔离跨会话 config 批宽变更 |
| NaN/inf 漏出污染 golden | 写边界 `json.dumps(allow_nan=False)` fail-loud (R2 P3-9); `run_all_models` 输出全有限 (§1.4); put-spy 测试 |
| enabled 误配 AMP 产 NaN | §1.5 load_all fail-fast (enabled ⇒ deterministic_mode); `test_fail_fast_requires_deterministic_mode` |
| 部分命中假提速 / 错位 | `_run_all_models_cached` 只前向 miss 有序子集; `test_partial_miss_only_forwards_missing` + `test_per_model_partial_hit_reforwards_all_models` |
| HF hub ckpt 指纹退化 | 已披露 (§5.5); 加载期 `_label_order_consistent` fail-loud + label_map 内容入键 + `_BERT_CACHE_VERSION`; §5.4 DEFERRED 增强 |
| 跨机命中非本机重算 | §1.7 freeze-anchor 语义显式 (device 不入键, 同 `_llm_cache.db` 复现锚纪律); §5.5 披露 |
| stats 摘要死代码 | §2 step 10: unload_all 前捕获 stats |
| 并发会话协同改同文件 | §4 逐文件 `git diff` + 外科 `git apply --cached` |
| pytest bump constants.json | §4 提交前 `git checkout --` 还原 |
| enabled 后 argmax 跨机漂移污染 golden | default-off; 启用须受控播种 + 受控 golden 重生 (DEFERRED §5) |
