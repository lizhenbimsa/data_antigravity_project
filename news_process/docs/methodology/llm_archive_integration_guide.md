# LLM Archive 集成指南 (C1 deliverable)

> **Status**: 已集成 2 / 4 production callsite (M0 完成 tone_llms + llm_peer_iv);
> 余 2 个 embedding callsite (benefit_society + strategic_diff) 模式不同, M1 完成.
> **目标**: V4 audit F-P2.1 critical + V6 verification PASS

---

## 一、已集成的 callsite (2 个 chat completion API)

### 1. `pipeline/sentiment/tone_llms.py` (Stage 21)

**位置**: `async with session.post(...) as resp: if resp.status == 200:`

**集成代码** (M0 已加, 见文件 ~440 行):
```python
if cache is not None:
    cache.put(model_id, prompt, result_text, prompt_version=prompt_version)
# v3.7.0 (C1): LLM raw response archive (V4 F-P2.1 critical)
if _LLM_ARCHIVE_AVAILABLE:
    try:
        actual_version = data.get('model', model_id)
        cache_key = LLMCache._make_key(model_id, prompt, prompt_version=prompt_version)
        _llm_archive_record(
            cache_key=cache_key,
            model_id=model_id,
            model_version=actual_version,
            prompt=prompt,
            response_raw=json.dumps(data, ensure_ascii=False),
            prompt_version=prompt_version,
            temperature=0.0,
            api_endpoint=f"{base_url}/chat/completions",
            http_status=resp.status,
        )
    except Exception as _arch_exc:
        logger.warning(f"LLM archive 失败 (不阻塞 pipeline): {_arch_exc!r}")
```

**覆盖范围**: stages 21 (sentiment) + 34 (substantiveness) + 36 (locus) + 39 (collab_mode)
所有共用 tone_llms.py 模块的下游 (3 维度 + sentiment 投票).

### 2. `pipeline/panel/llm_peer_iv.py` (Stage 48)

**位置**: 同样在 `if resp.status == 200:` 块内 (M0 已加, 见文件 ~338 行).

**覆盖范围**: stage 48 (LLM peer determination, Cao 2025 RAS 范式).

---

## 二、待集成的 callsite (2 个 embedding API, M1 完成)

### 3. `pipeline/features/benefit_society.py` (Stage 27)

**位置**: `_get_embeddings_api` 内的 `cache.put_batch(...)` 调用 (~L297).

**集成模式不同**:
- 用 `put_batch` 而非 `put` (一次 API 调用返回多个 embedding)
- 每个 embedding 单独 archive (batch 拆开成 N 条 record)
- response_raw 应包含完整 batch JSON (不仅是单个 embedding 向量)

**伪代码**:
```python
async def _get_embeddings_api(texts, token_counts, cache=None):
    # ... 现有代码 ...
    response = await session.post(embeddings_endpoint, json=batch_payload, ...)
    data = await response.json()
    embeddings = [e['embedding'] for e in data['data']]
    if cache is not None:
        cache.put_batch(model_id, texts, [json.dumps(e) for e in embeddings], ...)

    # v3.7.0 (C1) NEW: archive 整个 batch (单条 record 含全部 N 个 embedding)
    if _LLM_ARCHIVE_AVAILABLE:
        try:
            for i, (text, emb) in enumerate(zip(texts, embeddings)):
                _llm_archive_record(
                    cache_key=LLMCache._make_key(model_id, text, prompt_version=PROMPT_V),
                    model_id=model_id,
                    model_version=data.get('model', model_id),
                    prompt=text,  # embedding 的 "prompt" = input text
                    response_raw=json.dumps({'embedding': emb, 'batch_index': i,
                                             'batch_total': len(embeddings)}),
                    prompt_version=PROMPT_V,
                    temperature=0.0,  # embedding API 无 temperature
                    api_endpoint=embeddings_endpoint,
                    http_status=response.status,
                )
        except Exception as _arch_exc:
            logger.warning(f"LLM archive (benefit_society batch) 失败: {_arch_exc!r}")
```

### 4. `pipeline/features/strategic_diff.py` (复用 embedding API)

**位置**: 同样 `cache.put_batch` 后 (~L547).

**集成模式**: 同 #3 (embedding batch 拆开归档).

---

## 三、Verification (集成后必跑)

### 跑一次 stage 21 with 5-10 articles 测试

```bash
# 1. 准备 mini dataset (10 articles)
python -c "
import pandas as pd
df = pd.read_parquet('data/processed/12_fintech_news.parquet').head(10)
df.to_parquet('data/processed/12_fintech_news_test.parquet')
"

# 2. 跑 stage 21 mini (会调真实 LLM API, 消耗 ~$0.5)
python news_process/21_tone_llms.py --input data/processed/12_fintech_news_test.parquet

# 3. 验证 archive 写入
ls -la data/llm_archive/responses/
wc -l data/llm_archive/responses/$(date +%Y-%m-%d).jsonl

# 4. 生成 manifest
python -c "
from news_process.pipeline.llm_archive.manifest import write_manifest
write_manifest()
"

# 5. 验证 manifest
python -c "
from news_process.pipeline.llm_archive import verify_manifest
ok, errors = verify_manifest()
print('PASS' if ok else 'FAIL'); print(errors)
"
```

### 预期输出

- `data/llm_archive/responses/2026-MM-DD.jsonl` 存在
- record count = 10 articles × 3 LLM = 30 (若 sentiment 用 3-LLM 投票)
- `data/llm_archive/manifest.json` 含每个文件 sha256
- verify 输出 `PASS`

---

## 四、为什么 archive 失败不阻塞 pipeline

每个 callsite 都用 `try/except` 包裹 archive 调用:

```python
try:
    _llm_archive_record(...)
except Exception as _arch_exc:
    logger.warning(f"LLM archive 失败 (不阻塞 pipeline): {_arch_exc!r}")
```

**理由**:
1. Archive 是 reproducibility 强化, 不是 critical path
2. 万一磁盘满 / IO 错误 → pipeline 继续走 cache 路径
3. logger.warning 留下 trail, 便于事后追溯
4. CI/CD 测试不会因 archive 子系统问题失败

**例外**: 若用户要求 strict reproducibility mode (M1 可选 feature):
- 设置 env var `LLM_ARCHIVE_STRICT=1`
- 失败时 raise (pipeline 中止)
- 当前 M0 默认 lenient (warning-only)

---

## 五、与现有 LLMCache 的协作

```
LLM API call
   │
   ▼
LLMCache.get()  (从 SQLite 查)
   │
   ├─ hit  → 直接返回 cached response (不进 archive, 已经在 cache 里)
   └─ miss
         ▼
       actual API call
         │
         ▼
       LLMCache.put()        (写 SQLite 加速 cache, 可能被 schema migration 改写)
       LLMArchive.append()   (NEW, 写 JSONL append-only, 永远不改)
         │
         ▼
       返回 fresh response
```

**关键**: `LLMArchive.append` 只在 cache miss + API call 后调用, 不会重复归档.
12 月后审稿人复现时 `LLMCache` 全 hit (从 archive 重建), 不会有 fresh API call.

---

## 六、Definition of Done

- [x] tone_llms.py 集成 (stage 21/34/36/39, M0 已加)
- [x] llm_peer_iv.py 集成 (stage 48, M0 已加)
- [ ] benefit_society.py 集成 (stage 27, M1 完成 — 模式不同需重新设计)
- [ ] strategic_diff.py 集成 (M1 完成)
- [ ] mini stage 21 end-to-end 测试 (~$0.5 LLM 成本, 用户运行)
- [ ] 首次 manifest.json 生成 (M1, baseline 跑后)
- [ ] git LFS commit archive (M1, user-authorized)

---

## 七、与 V4 audit 对应

| V4 finding | 修复 | 状态 |
|---|---|---|
| F-P2.1 [CRITICAL] LLM response 复现 | tone_llms + llm_peer_iv 集成 | ✅ 2/4 done, 2/4 待 M1 |
| V6 [PENDING] LLM raw response archive | 模块 + 2 集成完成 | ⏳ 部分 PASS (待 4/4 完成) |
| F-Adv.2 [CRITICAL] LLM contamination test | DC4 后续 (holdout) | 待 M1 启动 |

---

## 八、commit 建议 (M0 收尾)

```bash
cd F:\WiseSearch\data_antigravity_project
git add news_process/pipeline/sentiment/tone_llms.py \
        news_process/pipeline/panel/llm_peer_iv.py \
        news_process/docs/methodology/llm_archive_integration_guide.md
git commit -m "C1 partial: LLM archive 集成到 tone_llms (stage 21/34/36/39) + llm_peer_iv (stage 48)"
```

> benefit_society + strategic_diff 集成留 M1 single commit.
