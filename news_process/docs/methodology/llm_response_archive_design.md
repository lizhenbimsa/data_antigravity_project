# LLM Response Archive 设计与复现协议 (v3.7.0)

> **Status**: M0 设计完成 (2026-05-18); 实施待第 10/11 篇 baseline 跑前完成
> **Owner**: news_process 项目第 10/11 篇 (DC3 deliverable)
> **修复**: V4 audit F-P2.1 critical + V6 verification FAIL

---

## 一、为什么需要 LLM Response Archive

### 问题

顶刊 (RFS / JAE / JF) reproducibility 要求审稿人 / 后续研究者能完整复现实验结果。当前项目状态:

- ✅ v3.5.1 已 **prompt frozen** (字节级, prompt_version = "v8" + jieba 0.42.1 frozen)
- ❌ 但 **LLM 模型本身可能升级**:
  - GPT-5.4-nano → GPT-5.5 升级 **已经发生** (2026-H1)
  - Gemini 3.1.111 → Gemini 3.2 待发布
  - DeepSeek-v4 → v4.5 待发布
- ❌ 现有 `core.caching.LLMCache` 是 *SQLite prompt → response 加速 cache*, 不是 *reproducibility ledger*
  - cache miss → 调 fresh API → 拿到的可能是新版模型 response
  - 旧 cache 可能被部分覆写 (虽然 v1 schema 设计上避免, 但 schema migration 时存在窗口)

### 后果

若不做 archive, **18 个月后 RFS reviewer 跑复现脚本时, 拿到的是 2027-Q4 的 LLM 输出, 与论文 baseline 完全不一致** → 直接被 reject。

---

## 二、设计原则

### Append-only

一旦写入永不修改 / 删除。每条 LLM API call 创建一条 record。

### 与 LLMCache 并存 (wrapping, 非替换)

```
LLM API call
   │
   ▼
LLMCache.get()  (hit? 直接返回)
   │ miss
   ▼
actual API call
   │
   ▼
LLMCache.put()         (常规加速缓存, 可被 schema 升级修改)
LLMArchive.append()    (永久归档, append-only, 不可修改)
```

### 完整 metadata (V4 F-P2.1)

每条 record 必含:

| 字段 | 含义 | 关键性 |
|---|---|---|
| `request_id` | UUID v4, 全局唯一 | 反向追溯 |
| `timestamp_utc` | ISO 8601 | 调用顺序还原 |
| `cache_key` | sha256(SCHEMA \| model_id \| prompt \| pv \| temp) | 与 LLMCache 反向 lookup |
| `model_id` | 配置名 (例 "gpt-5.4-nano") | 用户配置层 |
| **`model_version`** | API 返回的实际 version (例 "gpt-5.4-nano-2026-01") | **核心 critical, 不能省** |
| `prompt_version` | "v8" (v3.5.1 frozen) | 与 sidecar JSON anchor 一致 |
| `temperature` | 0.0 (项目默认确定性) | 复现条件 |
| `prompt` | 完整 prompt 文本 | input 完整记录 |
| `response_raw` | API 返回完整 JSON (不仅 content) | finish_reason / usage 等 |
| `api_endpoint` | API URL | 服务端识别 |
| `http_status` | 200 / 4xx / 5xx | 错误状态记录 |
| `http_headers` | 可选, 含 x-request-id 等 | 供 API provider 反向追溯 |

---

## 三、存储结构

```
data/llm_archive/
├── responses/
│   ├── 2026-05-18.jsonl    # 按 UTC 日切分
│   ├── 2026-05-19.jsonl
│   ├── 2026-05-20.jsonl
│   └── ...
├── manifest.json            # per-file SHA-256 + 全局 metadata
└── README.md                # 复现协议 (本文件)
```

### Manifest 格式

```json
{
  "schema_version": "v1",
  "archive_frozen_date": "2026-05-18",
  "generated_at_utc": "2026-05-18T13:45:00+00:00",
  "prompt_version_anchor": "v8",
  "files": {
    "2026-05-18.jsonl": {
      "sha256": "abc123...",
      "bytes": 1234567,
      "record_count": 1234
    }
  },
  "total_records": 12345,
  "total_bytes": 5678901
}
```

---

## 四、Git LFS 配置

### 预估归档体积 (v3.7.0 M16 校准 — 之前估算 ~5GB 严重低估)

**Chat completion API** (stage 21 + 34 + 36 + 39 + 48):
- 40 万新闻 × ~5 stage × 3 LLM 投票 ≈ **600 万条 record**
- 每条 ~2 KB (含 metadata + response_raw chat content) → **~12 GB**

**Embedding API** (stage 27 benefit + strategic_diff):
- 每条 embedding vector 1536 dim × float64 = **12 KB**
- 文章数 40 万 + bank-year 文档 ~9000 → 总 embedding 计算 ~80 万次
- 单条 record ≈ 12 KB embedding + 0.5 KB metadata = **12.5 KB**
- **~10 GB**

**总计估算: 20-25 GB** (实际可能浮动 ±50%, 视 prompt 长度)

### GitHub LFS 配额需求

| Option | 月费 | LFS storage |
|---|---|---|
| GitHub Free | $0 | 1 GB (远不够) |
| **GitHub LFS data pack × 1** | **$5/月** | **+50 GB** |
| GitHub LFS data pack × 2 | $10/月 | +100 GB (推荐双 buffer) |

→ 项目需要 **至少 1 data pack ($5/月), 推荐 2 packs ($10/月) 双 buffer**.

### 替代存储 (若 LFS 成本不可接受)

- **Zenodo** (顶刊推荐): 免费 + 永久 DOI + 50 GB/dataset
- **AWS S3**: ~$0.50/GB/月, public read 免费
- **Cloudflare R2**: egress 免费, $0.015/GB/月 storage

### .gitattributes 配置

在 repo root `.gitattributes` 加入:

```
data/llm_archive/responses/*.jsonl filter=lfs diff=lfs merge=lfs -text
data/llm_archive/manifest.json -text
```

### LFS 配额

| Tier | 月费 | LFS storage | LFS bandwidth |
|---|---|---|---|
| GitHub Free | $0 | 1 GB | 1 GB / 月 |
| GitHub Pro | $4 | 1 GB | 1 GB / 月 |
| **GitHub LFS data pack** | **$5 / 月** | **+50 GB** | **+50 GB / 月** |

→ 项目需要 **1 个 data pack** ($5/月), 5 GB archive 充裕。

### 替代方案 (若不用 GitHub LFS)

- AWS S3 + IAM read-only public link
- Cloudflare R2 (egress 免费)
- Zenodo (顶刊推荐, 永久 DOI)
- 项目自建 mirror (`https://archive.news-process.cn/llm_archive/`)

---

## 五、集成到现有 LLM Callsites

### 6 个待集成 stage

| Stage | 文件 | LLM 用途 |
|---|---|---|
| 21 | `pipeline/sentiment/tone_llms.py` | sentiment 3-LLM 投票 |
| 27 | `pipeline/features/benefit_society.py` | benefit_society embedding |
| 34 | `pipeline/sentiment/...` | substantiveness 分类 (W&Z) |
| 36 | `pipeline/sentiment/...` | locus 分类 (Gomber) |
| 39 | `pipeline/sentiment/...` | collab_mode 分类 (Chesbrough) |
| 48 | `pipeline/panel/llm_peer_iv.py` | LLM peer 识别 (Cao 2025 RAS) |

### 集成代码模板

每个 callsite 在 cache miss + API call 后加 2 行:

```python
from news_process.pipeline.llm_archive import archive_record

# ... 现有 LLM 调用 ...
response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
)

# v3.7.0 新增: 归档 raw response
archive_record(
    cache_key=cache_key,                    # 与 LLMCache 一致
    model_id=model_id,
    model_version=response.model,           # API 返回的实际 version, 关键!
    prompt=prompt,
    response_raw=response.model_dump_json(),
    prompt_version=PROMPT_VERSION,          # 例 "v8"
    temperature=0.0,
    api_endpoint=client.base_url + "/chat/completions",
)
```

---

## 六、复现协议 (供审稿人)

### Step 1: 拉取 archive

```bash
git lfs pull
```

### Step 2: 验证 archive 完整性

```bash
python -m news_process.pipeline.llm_archive.manifest verify
```

成功输出:
```
Manifest verification: PASS
total_records: 12345
total_bytes: 5,678,901
all files: SHA-256 OK
```

失败时列出每个 mismatch 文件 + 诊断。

### Step 3: 从 archive 重建 LLMCache

```bash
python -m news_process.pipeline.llm_archive replay --target data/.llm_cache.db
```

重建后所有 LLMCache.get() 全 cache hit, **不需要 fresh API call**。

### Step 4: 跑 pipeline (无 API 调用)

```bash
python run_pipeline_function.py
```

所有 stage 21/27/34/36/39/48 全 cache hit, 输出与原 paper 完全一致。

### Step 5: 验证 final panel 一致性

```bash
pytest tests/integration/test_panel_reproducibility.py
```

通过 = 完整复现成功。

---

## 七、与 v3.5.1 sidecar JSON anchor 的关系

v3.5.1 `data/processed/v3_5_1_constants.json` 已锚定:
- `median_amb_d0` (clarity 二值化中位数)
- `prompt_v8_sha256` (prompt 字节级冻结)
- `stage21_last_run_timestamp`

v3.7.0 archive 与之**互补**:
- sidecar JSON = *输入侧* frozen anchor (prompt + 衍生常量)
- LLM archive = *输出侧* frozen ledger (raw response + manifest)

两者共同构成 v3.7.0 完整 reproducibility 闭环。

---

## 八、与 V4 audit 决策的对应

| V4 finding | 修复 | 状态 |
|---|---|---|
| F-P2.1 [CRITICAL] LLM response 复现性 | 本模块 | ✅ DC3 |
| V6 [FAIL] LLM raw response archived | 本模块实施后 → PASS | ⏳ 待集成到 6 callsite |
| F-Adv.2 [CRITICAL] LLM training data contamination | DC4 后续 (holdout test) | 待启动 |

---

## 九、Definition of Done

- [ ] `pipeline/llm_archive/` 模块 (✅ M0 已完成: archive.py / manifest.py / __init__.py)
- [ ] `tests/test_llm_archive.py` 单元测试 ≥ 15 case (✅ M0 已完成)
- [ ] 集成到 6 stage callsite (待 M1-M2)
- [ ] `.gitattributes` Git LFS 配置 (待用户授权 commit)
- [ ] 首次完整 archive run (待第 10/11 篇 baseline 跑后)
- [ ] manifest.json 生成 + commit (待 first run 后)
- [ ] README.md (本文件) commit (待用户授权)

---

## 十、版本与变更

- **v3.7.0 (2026-05-18)**: 初始设计, 第 10/11 篇 DC3 deliverable
- 上游依赖: v3.5.1 prompt frozen (PROMPT_VERSION = "v8") + jieba 0.42.1 frozen
- 下游依赖: 第 10/11 篇 SSRN release (M14/M16) + 顶刊投稿 (M15+/M17+)
