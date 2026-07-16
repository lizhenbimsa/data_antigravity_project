"""news_process.pipeline.llm_archive — v3.7.0 LLM raw response 永久归档模块.

V4 audit F-P2.1 critical 修复 + V6 verification 必修项.

设计目标
--------
顶刊 reproducibility 硬约束: 即使 LLM 模型升级 (GPT-5.4-nano → 5.5 已发生),
审稿人 fresh API call 时仍能从归档复现实验结果.

v3.5.1 仅 prompt frozen (字节级) 不够; v3.7.0 升级为 *response frozen*:
归档所有 LLM 调用的 (request, response, metadata) 三元组 + SHA-256 manifest.

架构
----
**Wrapping pattern**: 不重写现有 core.caching.LLMCache (SQLite WAL prompt → response
cache), 只在 cache miss + API 调用后 *append-only* 归档到独立 JSONL store.

::

    LLM API call → LLMCache.get() (hit?)
                     │ miss
                     ▼
                   actual API call
                     │
                     ▼
                   LLMCache.put() (常规缓存)
                   LLMArchive.append() (NEW, append-only 归档)
                     │
                     ▼
                   data/llm_archive/
                     ├── responses/
                     │     ├── 2026-05-18.jsonl  (按日切分)
                     │     └── ...
                     ├── manifest.json           (per-file SHA-256)
                     └── README.md               (复现协议)

归档字段 (per record)
--------------------
- request_id:        UUID v4
- timestamp_utc:     ISO 8601
- cache_key:         与 LLMCache 一致 (sha256, 反向 lookup)
- model_id:          "gpt-5.4-nano" 等用户配置标识
- model_version:     "gpt-5.4-nano-2026-01" API 返回 actual version (关键!)
- prompt_version:    "v8" (v3.5.1 frozen)
- temperature:       0.0
- prompt:            完整 prompt 文本
- response_raw:      API 返回的完整 JSON (不仅是 content, 还有 finish_reason, usage 等)
- api_endpoint:      "https://api.yunwu.ai/v1/chat/completions"
- http_status:       200
- http_headers:      {x-request-id, x-ratelimit-*}   (可选, default off)

Manifest (manifest.json)
-----------------------
- per-file SHA-256 checksum
- record count
- 总 bytes
- 创建时间
- v3.5.1 prompt_version 锚定 (与 sidecar JSON 一致)

Git LFS 配置
-----------
.gitattributes:
    data/llm_archive/responses/*.jsonl filter=lfs diff=lfs merge=lfs -text

预估大小: 40 万新闻 × 6 stage 调用 (21/27/34/36/39/48) × ~2KB/response ≈ 5GB
LFS quota: GitHub 默认 1GB 免费 + $5/月 50GB → 充裕

复现协议
-------
审稿人复现步骤:
1. git lfs pull 拉取 archive
2. manifest checksum 验证 (调用 verify_manifest, 暂无独立 CLI 子命令):
   python -c "from news_process.pipeline.llm_archive import verify_manifest; ok, errs = verify_manifest(); print('PASS' if ok else f'FAIL: {errs}')"
3. python run_pipeline_function.py (LLMCache 命中时无 API 调用)
   注: 从 archive 直接重建 LLMCache 的 "replay-to-cache" 工具尚未实现 (roadmap 项);
       当前复现依赖既有的 _llm_cache.db 缓存命中。

覆盖范围限制 (fix(omni-g-tonellms-04, 2026-06-11) 如实披露)
--------------------------------------------------------
归档仅在 **缓存 miss → 新 API 调用成功 (HTTP 200)** 时触发 (tone_llms.py 的
200 分支); 缓存命中提前返回, 永不归档。当前 frozen v8 生产语料 7020 响应
全部命中 v3.7.0 接线前已建成的 ``_llm_cache.db`` (133,687 条) → **本归档对
该语料的覆盖恒为空集** (data/llm_archive/ 不存在, manifest 从未写出,
verify_manifest 直接返回 "manifest 不存在")。即:
- 本模块实际仅覆盖 **v3.7.0 接线后的新 API 调用** (如全量 约1,819万 语料重处理);
- frozen 语料的复现锚点仍是 ``_llm_cache.db`` (勿删铁律) + 离线守卫
  ``NEWS_PROCESS_LLM_OFFLINE=1``, 而非本归档;
- "审稿人 fresh API call 时仍能从归档完整复现" 的设计目标对 frozen 语料
  尚未兑现 — 需 cache→archive backfill 工具 (遍历 _llm_cache.db,
  model_version 标 'backfill-unknown') + write_manifest, 与 replay-to-cache
  同列 roadmap 项, 均未实现。
- 写入顺序已修 (tone_llms.py fix omni-g-tonellms-04): archive append 先于
  cache.put, 归档失败时跳过 put — 消除 "先 put 后归档异常 → 响应被永久缓存、
  后续命中短路 → 一次性永久漏档" 的窗口。

接口 (与 __all__ 一致)
----
- LLMArchive: 主类, append-only 归档
- archive_record: 单次写入函数
- compute_manifest: 生成 manifest dict
- write_manifest: 生成并写入 manifest.json (顶层公开 API, 迁移/复现脚本调用)
- verify_manifest: 验证 manifest checksum (SHA-256)
"""

from .archive import LLMArchive, archive_record
from .manifest import compute_manifest, verify_manifest, write_manifest

__all__ = [
    'LLMArchive',
    'archive_record',
    'compute_manifest',
    'write_manifest',
    'verify_manifest',
]

# v3.7.0 schema version (与 core.caching.SCHEMA_VERSION 独立)
ARCHIVE_SCHEMA_VERSION = "v1"

# v3.7.0 frozen at: 2026-05-18 (与第 10 + 11 篇 M0 立项同步)
ARCHIVE_FROZEN_DATE = "2026-05-18"
