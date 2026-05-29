"""news_process.pipeline.text.embedding_engine — 双模型嵌入统一引擎 (2026-05-29).

设计目标
--------
让任意 callsite (stage 15 policy_alignment / 25 strategic_diff / 26 policy_similarity
/ 27 benefit_society / network embedding peer) 用 **显式 spec** 嵌入文本, 从而在
一次运行内对同一批文本用两个模型各算一遍:

  - MAIN (canonical):     text-embedding-3-small (OpenAI-compat, yunwu) — 主轨
  - ROBUSTNESS (`_t2v`):  shibing624/text2vec-base-chinese (local) — 稳健 twin

spec 是一个 dict (来自 ``config/features.yaml::embedding_api`` 或 ``embedding_robustness``):

    {model, base_url, api_key, text_pipeline_version, batch_size}

本模块**不** import ``pipeline.panel.encode`` (避免循环导入); spec 由 callsite 从其
自有的 CONFIG 传入。LLMCache 键以 ``model_id`` 为首字段 (见 core/caching.py),
故主轨 (text-embedding-3-small) 与稳健轨 (text2vec) 的缓存天然隔离不串。

历史: 本引擎把原先散落在 4 个 feature 模块里近重复的
``_get_embeddings_api`` / ``_encode_embeddings_local`` / ``_embed_texts_with_chunk_pooling``
统一为 spec 参数化的公共函数 (DRY + 让双轨成为一等公民)。

学术依据 (沿用 strategic_diff/policy_alignment 既有锚点):
  - Reimers & Gurevych (2019, EMNLP) Sentence-BERT mean pooling, DOI 10.18653/v1/D19-1410
  - Guenther et al. (2024, arXiv:2409.04701) Early Chunking 超长文本分段
  - Carlson & Burbano (2026, SMJ §3.3) version-aware provenance (cache 版本维度)
"""

from __future__ import annotations

import asyncio
import json
import logging

import numpy as np
import tiktoken

logger = logging.getLogger(__name__)

# ── Embedding token 级精确截断 (统一 stage 15 标准) ──
# text-embedding-3-small 用 cl100k_base 编码, 单条上限 8,191 tokens;
# 超长文本 (如权威政策语料) 走 Early Chunking + Mean Pooling。
_EMB_ENCODING = tiktoken.get_encoding("cl100k_base")
EMB_MAX_TOKENS = 8191
EMB_MAX_TOKENS_PER_REQUEST = 250_000

RETRY_DELAY = 5
MAX_RETRY_DELAY = 60

# local SentenceTransformer 按 model_id 缓存 (允许两个 spec 都是 local 时各持其模型)
_LOCAL_MODELS: dict[str, object] = {}

_LOCAL_BASE_URLS = {
    'local',
    'local://',
    'sentence-transformers',
    'sentence_transformers',
}

# LLM raw response archive (顶刊 reproducibility; 不可用时静默降级, 不阻塞)
try:  # pragma: no cover - import 形态依赖可选包
    from news_process.core.caching import LLMCache
    from news_process.pipeline.llm_archive.archive import (
        _get_default_archive as _get_archive,
    )
    _LLM_ARCHIVE_AVAILABLE = True
except ImportError:  # pragma: no cover
    from news_process.core.caching import LLMCache  # caching 是核心依赖, 必存在
    _get_archive = None
    _LLM_ARCHIVE_AVAILABLE = False


def spec_uses_local(spec: dict | None) -> bool:
    """spec 是否指向本地 sentence-transformers (而非 API 端点)。"""
    base_url = str((spec or {}).get('base_url') or '').strip().lower()
    return base_url in _LOCAL_BASE_URLS


def spec_model(spec: dict | None, default: str = 'text-embedding-3-small') -> str:
    """取 spec 的 model 名; 缺失时回退到 default。"""
    return (spec or {}).get('model') or default


def spec_version(spec: dict | None) -> str:
    """取 spec 的 cache prompt_version 命名空间 (缺失 → 'v0')。"""
    return (spec or {}).get('text_pipeline_version', 'v0')


def split_text_for_embedding(text) -> list[str]:
    """按 token 粒度切分超长文本 (Early Chunking, Guenther et al. 2024)。

    短文本原样返回 (避免 encode/decode 往返); 超长文本切成 <= EMB_MAX_TOKENS 的段。
    """
    try:
        import pandas as pd
        if pd.isna(text):
            text = ""
    except (TypeError, ValueError, ImportError):
        pass
    text = str(text)
    if not text:
        text = " "
    tokens = _EMB_ENCODING.encode(text)
    if len(tokens) <= EMB_MAX_TOKENS:
        return [text]
    return [
        _EMB_ENCODING.decode(tokens[i:i + EMB_MAX_TOKENS])
        for i in range(0, len(tokens), EMB_MAX_TOKENS)
    ]


def encode_local(texts, spec: dict, *, log_prefix: str = "Embedding") -> np.ndarray:
    """用本地 sentence-transformers 模型 (spec['model']) 编码文本。

    模型按 model_id 进程级缓存; 默认 shibing624/text2vec-base-chinese (768 维)。
    """
    from sentence_transformers import SentenceTransformer

    model_id = spec_model(spec, 'shibing624/text2vec-base-chinese')
    if model_id not in _LOCAL_MODELS:
        logger.info(f"    {log_prefix}: 加载本地嵌入模型 {model_id}")
        _LOCAL_MODELS[model_id] = SentenceTransformer(model_id)
    batch_size = int((spec or {}).get('batch_size', 32) or 32)
    emb_local = _LOCAL_MODELS[model_id].encode(
        list(texts), batch_size=batch_size, show_progress_bar=False,
    )
    return np.asarray(emb_local, dtype=np.float32)


async def get_embeddings_api(texts, spec: dict, cache=None, *,
                             enable_archive: bool = True) -> np.ndarray:
    """通过 API 获取文本 Embedding — 穿透式缓存 + 动态分批 + 死战不退容错。

    spec 提供 base_url / api_key / model / text_pipeline_version。
    与 LLMCache 配合: cache 命中的文本不重复调用; 写回时按 model_id+version 命名空间。
    """
    import aiohttp

    texts = [] if texts is None else list(texts)
    if len(texts) == 0:
        return np.empty((0, 0), dtype=np.float32)

    base_url = (spec or {}).get('base_url')
    api_key = (spec or {}).get('api_key')
    embedding_model = spec_model(spec)
    if not base_url or not api_key:
        raise RuntimeError("Embedding API spec missing base_url or api_key")
    base_url = str(base_url).rstrip("/")
    text_pipeline_version = spec_version(spec)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    cached_results = [
        cache.get(embedding_model, text, prompt_version=text_pipeline_version)
        if cache else None
        for text in texts
    ]
    missing_indices = [i for i, res in enumerate(cached_results) if res is None]
    missing_texts = [texts[i] for i in missing_indices]

    if len(texts) > 1:
        logger.info(
            f"    缓存拦截: 命中 {len(texts) - len(missing_texts)} 条, "
            f"缺失 {len(missing_texts)} 条 (model={embedding_model})"
        )

    missing_embs: list = []
    if missing_texts:
        # 动态分批: 单批 <= 2000 条 且 token 总和 <= EMB_MAX_TOKENS_PER_REQUEST
        batches: list[list[str]] = []
        current_batch: list[str] = []
        current_tokens = 0
        for text in missing_texts:
            n_tok = max(1, len(_EMB_ENCODING.encode(text)))
            if n_tok > EMB_MAX_TOKENS:
                raise RuntimeError(
                    f"Embedding 单条输入超限: {n_tok} > {EMB_MAX_TOKENS}"
                )
            if current_batch and (
                len(current_batch) >= 2000
                or current_tokens + n_tok > EMB_MAX_TOKENS_PER_REQUEST
            ):
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            current_batch.append(text)
            current_tokens += n_tok
        if current_batch:
            batches.append(current_batch)

        if len(batches) > 1:
            logger.info(f"    网络请求: 动态分批为 {len(batches)} 批")

        async with aiohttp.ClientSession() as session:
            for batch_idx, batch in enumerate(batches):
                delay = RETRY_DELAY
                while True:
                    try:
                        async with session.post(
                            f"{base_url}/embeddings",
                            json={"model": embedding_model, "input": batch},
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=180),
                        ) as resp:
                            status = resp.status
                            if status == 200:
                                data = await resp.json()
                                if 'data' not in data:
                                    raise ValueError(
                                        f"API 响应格式异常(缺少'data'): {str(data)[:200]}"
                                    )
                                sorted_data = sorted(
                                    data['data'], key=lambda x: x.get('index', 0))
                                batch_embs = [d['embedding'] for d in sorted_data]
                                missing_embs.extend(batch_embs)
                                if cache:
                                    cache.put_batch(
                                        embedding_model,
                                        batch,
                                        [json.dumps(emb) for emb in batch_embs],
                                        prompt_version=text_pipeline_version,
                                    )
                                if enable_archive and _LLM_ARCHIVE_AVAILABLE:
                                    try:
                                        actual_version = data.get(
                                            'model', embedding_model)
                                        api_endpoint = f"{base_url}/embeddings"
                                        records = [
                                            {
                                                'cache_key': LLMCache.make_key(
                                                    embedding_model, text,
                                                    prompt_version=text_pipeline_version,
                                                ),
                                                'model_id': embedding_model,
                                                'model_version': actual_version,
                                                'prompt': text,
                                                'response_raw': json.dumps({
                                                    'embedding': emb,
                                                    'batch_index': i,
                                                    'batch_total': len(batch_embs),
                                                    'batch_id': batch_idx,
                                                }, ensure_ascii=False),
                                                'prompt_version': text_pipeline_version,
                                                'temperature': 0.0,
                                                'api_endpoint': api_endpoint,
                                                'http_status': status,
                                            }
                                            for i, (text, emb) in enumerate(
                                                zip(batch, batch_embs))
                                        ]
                                        _get_archive().append_batch(records)
                                    except Exception as _arch_exc:
                                        logger.warning(
                                            f"    LLM archive (batch {batch_idx + 1}) "
                                            f"失败 (不阻塞): {_arch_exc!r}"
                                        )
                                break
                            elif status in (429, 500, 502, 503, 504):
                                err_text = await resp.text()
                                logger.warning(
                                    f"    HTTP {status} (batch {batch_idx + 1}): "
                                    f"{err_text[:100]}。休眠 {delay}s 后重试..."
                                )
                                await asyncio.sleep(delay)
                                delay = min(delay * 2, MAX_RETRY_DELAY)
                            else:
                                err_text = await resp.text()
                                raise ValueError(
                                    f"不可恢复的 API 错误 {status} "
                                    f"(batch {batch_idx + 1}): {err_text[:200]}"
                                )
                    except ValueError:
                        raise
                    except Exception as e:
                        logger.warning(
                            f"    网络异常 (batch {batch_idx + 1}): "
                            f"{type(e).__name__}: {e}。休眠 {delay}s 后重试..."
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, MAX_RETRY_DELAY)

    assert len(missing_embs) == len(missing_texts), (
        f"返回数量异常: expected {len(missing_texts)}, got {len(missing_embs)}"
    )
    final_embs = []
    missing_ptr = 0
    for res in cached_results:
        if res is not None:
            final_embs.append(json.loads(res))
        else:
            final_embs.append(missing_embs[missing_ptr])
            missing_ptr += 1
    return np.array(final_embs, dtype=np.float32)


def embed_texts(texts, spec: dict, *,
                cache_db_path: str | None = None,
                log_prefix: str = "Embedding",
                enable_archive: bool = True) -> np.ndarray | None:
    """文本 → 文本级 Embedding 向量 (n_texts, dim), spec 决定模型与路径。

    超长文本走 Early Chunking + Mean Pooling。local spec 走 sentence-transformers,
    API spec 走 get_embeddings_api (经 LLMCache 穿透)。失败/形状异常 → None。

    Returns:
        np.ndarray (n_texts, dim) | None
    """
    texts = [] if texts is None else list(texts)
    if len(texts) == 0:
        return None

    all_chunks: list[str] = []
    chunk_map: list[tuple[int, int]] = []
    for text in texts:
        chunks = split_text_for_embedding(text)
        start = len(all_chunks)
        all_chunks.extend(chunks)
        chunk_map.append((start, len(all_chunks)))

    n_orig = len(texts)
    n_chunks = len(all_chunks)
    if n_chunks > n_orig:
        logger.info(
            f"    {log_prefix} 分段: {n_orig} 文本 → {n_chunks} 段 "
            f"(含 {n_chunks - n_orig} 个超长文本扩展段)"
        )

    if spec_uses_local(spec):
        raw_emb = encode_local(all_chunks, spec, log_prefix=log_prefix)
    else:
        if cache_db_path:
            with LLMCache(cache_db_path) as cache:
                raw_emb = asyncio.run(
                    get_embeddings_api(all_chunks, spec, cache,
                                       enable_archive=enable_archive))
        else:
            raw_emb = asyncio.run(
                get_embeddings_api(all_chunks, spec, None,
                                   enable_archive=enable_archive))
        logger.info(f"    {log_prefix}: API ({spec_model(spec)}) 成功")

    raw_emb = np.asarray(raw_emb)
    if raw_emb.ndim != 2 or raw_emb.shape[0] != n_chunks:
        logger.warning(
            f"    {log_prefix}: 向量形状异常 "
            f"(expected {n_chunks}×D, got {raw_emb.shape})"
        )
        return None

    emb = np.zeros((n_orig, raw_emb.shape[1]), dtype=raw_emb.dtype)
    for i, (start, end) in enumerate(chunk_map):
        if end - start == 1:
            emb[i] = raw_emb[start]
            continue
        pooled = raw_emb[start:end].mean(axis=0)
        norm = np.linalg.norm(pooled)
        emb[i] = pooled / norm if norm > 0 else pooled
    return emb
