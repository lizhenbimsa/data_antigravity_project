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
统一为 spec 参数化的公共函数 (DRY + 让 MAIN/ROBUSTNESS 两个嵌入模型成为一等公民)。
注: 此处 "两个模型" 指 text-embedding-3-small 主轨 vs text2vec ``_t2v`` 稳健轨这一
**模型** 维度, 与情感文本的 full/ctx/ss 三轨是两个独立维度。

学术依据 (沿用 strategic_diff/policy_alignment 既有锚点):
  - Reimers & Gurevych (2019, EMNLP) Sentence-BERT mean pooling, DOI 10.18653/v1/D19-1410
  - 朴素分段 (naive / independent chunking) 超长文本分段
  - Carlson & Burbano (2026, SMJ §3.3) version-aware provenance (cache 版本维度)

白话:
    全项目所有"把文本变成向量"的需求都走这一个模块: 调用方传一份 spec
    (写明用哪个模型、走 API 还是本地), 同一批文本就能分别用主模型和稳健
    模型各算一遍向量。算过的结果存在缓存里, 下次同样的文本不再花钱重算;
    太长的文本先切成小段、各段算完再加权平均成一条向量。
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
# 超长文本 (如权威政策语料) 走朴素分段 (naive chunking) + Mean Pooling。
_EMB_ENCODING = tiktoken.get_encoding("cl100k_base")
EMB_MAX_TOKENS = 8191
EMB_MAX_TOKENS_PER_REQUEST = 250_000

RETRY_DELAY = 5
MAX_RETRY_DELAY = 60

# API 嵌入批次最大并发数 (asyncio.gather + Semaphore 上限)。各批次结果按 batch_idx
# 索引收集再按序重组 (绝不依赖完成顺序), 故并发对产出逐位不变, 仅缩短 wall-clock。
# ⚠ 若调高需留意上游 API 的 RPS / 并发限流 (429 已由 per-batch 退避重试兜底)。
EMB_API_CONCURRENCY = 100

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


# 进程级幂等标志: 确定性硬化只设一次 (torch 全局开关, 重复设置无害但避免日志噪声)
_TORCH_DETERMINISM_DONE = False


def ensure_torch_determinism(seed: int = 42) -> None:
    """本地 torch 推理确定性硬化 (对齐 stage 23 tone_berts.py V4 T1.1a 块).

    fix(omni-g-embed-07, 2026-06-11): article_sbert.encode_articles 与本模块
    encode_local 此前裸调 model.encode, 无 seed/deterministic/cudnn 设置 — CPU 单机
    通常逐位稳定, 但 CUDA 机上 cudnn.benchmark 自动调优可致 run-to-run kernel 选择
    漂移, 跨机必有 FP 级漂移; 下游 argsort top-k 近邻 (strat_sim) 与 staleness 阈值
    化 (surface_highstale) 会把 FP 漂移放大为离散值翻转。本 helper 抽取 tone_berts
    确定性块为共享入口: seed 四源 (random/numpy/torch/transformers) +
    use_deterministic_algorithms(warn_only=True) + cuDNN deterministic/benchmark。
    幂等 (进程内只设一次); torch 缺失时静默 no-op (本地编码路径必有 torch, 纯防御)。
    """
    global _TORCH_DETERMINISM_DONE
    if _TORCH_DETERMINISM_DONE:
        return
    try:
        import torch
    except ImportError:  # pragma: no cover - 本地编码环境必有 torch
        return
    import random as _stdlib_random

    _stdlib_random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    try:
        from transformers import set_seed as _hf_set_seed
        _hf_set_seed(seed)
    except ImportError:  # pragma: no cover - transformers 旧版无 set_seed
        pass
    # warn_only=True: CPU 上几乎不抛错; GPU 个别 op 输出 warning 但继续 (同 tone_berts)
    torch.use_deterministic_algorithms(True, warn_only=True)
    if torch.cuda.is_available():  # pragma: no cover - 本机 CPU-only, GPU 机生效
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    _TORCH_DETERMINISM_DONE = True
    logger.info(f"    本地嵌入确定性硬化: seed={seed}, deterministic_algorithms=on")


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
    """按 token 粒度切分超长文本 (朴素分段 / naive independent chunking)。

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


def _select_torch_device() -> str:
    """显式选择本地嵌入设备 (2026-06-23 加固): 有 CUDA → 'cuda', 否则 'cpu'。

    此前 ``SentenceTransformer(model_id)`` 不传 device, 依赖 ST 当前默认 (新版
    自动探测 → 有 GPU 取 'cuda:0')。写成显式契约防未来 ST 改默认把本应跑 GPU 的
    嵌入 stage 静默拖回 CPU (本机 RTX 3090 上会从 ~65s 暴涨到 ~100min)。
    与既有自动探测**同设备** → 数值 byte-for-byte 不变, golden-safe。
    """
    try:
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:  # pragma: no cover - 本地编码环境必有 torch
        return 'cpu'


def encode_local(texts, spec: dict, *, log_prefix: str = "Embedding") -> np.ndarray:
    """用本地 sentence-transformers 模型 (spec['model']) 编码文本。

    模型按 model_id 进程级缓存; 默认 shibing624/text2vec-base-chinese (768 维)。

    fix(omni-g-embed-04/07, 2026-06-11) 两处语义变更:
    1. 超出模型 max_seq_length (t2v=128 token) 的文本此前被模型**静默截断**到首段
       (split_text_for_embedding 的 8191 cl100k 上限远大于本地模型上限, 拦不住);
       现按模型自身 tokenizer 分块后 mean-pool (逐块 L2 归一 + token 数加权, 与
       embed_texts 池化口径一致); 不超长文本原样直送, 输出与旧实现逐位一致。
    2. 推理前调 ensure_torch_determinism() (对齐 stage 23 tone_berts 硬化)。
    """
    from sentence_transformers import SentenceTransformer

    ensure_torch_determinism()  # fix(omni-g-embed-07, 2026-06-11)

    model_id = spec_model(spec, 'shibing624/text2vec-base-chinese')
    if model_id not in _LOCAL_MODELS:
        device = _select_torch_device()
        logger.info(f"    {log_prefix}: 加载本地嵌入模型 {model_id} (device={device})")
        _LOCAL_MODELS[model_id] = SentenceTransformer(model_id, device=device)
    model = _LOCAL_MODELS[model_id]
    batch_size = int((spec or {}).get('batch_size', 32) or 32)
    texts = list(texts)

    # ── fix(omni-g-embed-04, 2026-06-11): 按模型 max_seq_length 分块, 防静默截断 ──
    max_seq = int(getattr(model, 'max_seq_length', 0) or 0)
    tokenizer = getattr(model, 'tokenizer', None)
    if max_seq <= 0 or tokenizer is None:
        # 无 tokenizer/max_seq 元数据 (如测试 fake 模型) → 旧行为直送
        emb_local = model.encode(
            texts, batch_size=batch_size, show_progress_bar=False,
        )
        return np.asarray(emb_local, dtype=np.float32)

    effective_max = max(1, max_seq - 2)  # 留 [CLS]/[SEP] 特殊 token 位
    chunks: list = []
    chunk_map: list[tuple[int, int]] = []
    chunk_weights: list[int] = []  # 与 chunks 等长, 单位 = 本地模型 token 数
    for text in texts:
        t = str(text) if text is not None else ''
        ids = tokenizer.encode(t, add_special_tokens=False) if t else []
        start = len(chunks)
        if len(ids) <= effective_max:
            chunks.append(text)  # 不超长 → 原样直送 (与旧实现逐位一致)
            chunk_weights.append(max(1, len(ids)))
        else:
            for s in range(0, len(ids), effective_max):
                seg = ids[s:s + effective_max]
                chunks.append(tokenizer.decode(seg, skip_special_tokens=True))
                chunk_weights.append(max(1, len(seg)))
        chunk_map.append((start, len(chunks)))

    if len(chunks) > len(texts):
        logger.info(
            f"    {log_prefix}: 本地模型 max_seq_length={max_seq} 分块: "
            f"{len(texts)} 文本 → {len(chunks)} 段 (防静默截断)"
        )

    raw = np.asarray(
        model.encode(chunks, batch_size=batch_size, show_progress_bar=False),
        dtype=np.float32,
    )
    if len(chunks) == len(texts):
        return raw  # 无超长文本 → 与旧实现逐位一致

    out = np.zeros((len(texts), raw.shape[1]), dtype=np.float32)
    for i, (start, end) in enumerate(chunk_map):
        if end - start == 1:
            out[i] = raw[start]
            continue
        # 逐块 L2 归一 + token 数加权 mean-pool (KNOWN-OPEN⑧: 未归一向量的等权 mean
        # 隐含按块范数加权; 等权下尾段碎片块与整块同权 → 双重权重失真)
        block = raw[start:end].astype(np.float64)
        norms = np.linalg.norm(block, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        unit = block / norms
        w = np.asarray(chunk_weights[start:end], dtype=np.float64)
        pooled = (unit * w[:, None]).sum(axis=0) / w.sum()
        nrm = np.linalg.norm(pooled)
        out[i] = (pooled / nrm if nrm > 0 else pooled).astype(np.float32)
    return out


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
    text_pipeline_version = spec_version(spec)

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
        # fix(2026-06-19 run-check F1): API spec 校验 + headers 构造下移至此 —
        # 仅当确有未缓存文本需联网时才要求 base_url/api_key。全命中路径 (含离线
        # 空 key) 由缓存直接返回, 兑现 stage 15 banner "命中即逐位 $0 复现" 契约,
        # 修复 stage 15/45 在嵌入缓存完整时仍因空 key 在 cache 查找前误崩。
        if not base_url or not api_key:
            raise RuntimeError("Embedding API spec missing base_url or api_key")
        base_url = str(base_url).rstrip("/")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
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

        n_batches = len(batches)
        if n_batches > 1:
            logger.info(
                f"    网络请求: 动态分批为 {n_batches} 批 "
                f"(并发度 ≤ {min(EMB_API_CONCURRENCY, n_batches)})"
            )

        # ── 并发批次 (asyncio.gather + Semaphore) ──
        # ⚠ 铁律 (verify:concurrent-batches-safe 对抗审计逮到的静默错位坑):
        #   旧实现用 ``missing_embs.extend(batch_embs)`` 顺序累加, 一旦批次**完成顺序**
        #   乱序 (并发必然发生), 向量就被静默错位拼装 → 下游余弦全错且无任何报错。
        #   修复: 各批次结果写入 ``_embs_by_idx[batch_idx]`` 锁定位置, gather 后再按
        #   batch_idx **升序**重组 → 完成顺序无关, 产出与逐次串行逐位一致 (仅快)。
        _embs_by_idx: dict[int, list] = {}
        _done = 0
        _sem = asyncio.Semaphore(max(1, min(EMB_API_CONCURRENCY, n_batches)))

        async def _process_batch(batch_idx: int, batch: list[str], session) -> None:
            nonlocal _done
            delay = RETRY_DELAY
            async with _sem:
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
                                # 按 batch_idx 锁定位置 (asyncio 单线程, dict 赋值原子,
                                # 完成顺序无关 → 重组后逐位等价串行)
                                _embs_by_idx[batch_idx] = batch_embs
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
                                _done += 1
                                if _done % 5 == 0 or _done == n_batches:
                                    logger.info(
                                        f"    API 进度: {_done}/{n_batches} 批完成")
                                return
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

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[
                _process_batch(i, b, session) for i, b in enumerate(batches)
            ])

        # 按 batch_idx 升序重组 → 与 missing_texts 原始顺序严格一致 (批次本就按
        # missing_texts 顺序切分, 故顺序拼接即复原)。
        for i in range(n_batches):
            missing_embs.extend(_embs_by_idx[i])

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


def _encode_local_cached(chunks, spec: dict, *,
                         cache=None,
                         cache_db_path: str | None = None,
                         log_prefix: str = "Embedding") -> np.ndarray:
    """``encode_local`` 的穿透式缓存封装 (2026-06-23)。

    本地 sentence-transformers (text2vec) 此前是全项目**唯一不走缓存**的嵌入路径
    → 每次重跑 / 每个 stage (16/26/27/network 都嵌同一批 content_full) 都从头
    forward 一遍。本封装按 ``(model_id, 完整 chunk 文本, text_pipeline_version)``
    查 LLMCache: 命中即读 (反序列化), 仅未命中的 chunk 真正 ``encode_local`` 一次
    并回写。键以 ``model_id`` 为首字段 → 与 API 主轨缓存天然隔离不串。

    golden 语义 (与 API 轨 / stage 21 ``_llm_cache.db`` 锚点同源): 缓存冻结**首次
    计算值** → 此后重跑逐位复现, 反而比"每 run 重算 (BLAS/CUDA-FP 漂移)"更稳。
    首次播种须受控环境 (PYTHONHASHSEED=0 + BLAS 线程=1 + 保留 GPU + HF offline),
    之后离线 $0 字节级复现。值经 ``json.dumps(float32.tolist())`` 往返**字节级无损**
    (float32 ⊂ float64; repr 最短可逆 → 读回 ``np.float32`` 与原值逐位相等)。

    cache 解析: 传入已打开的 ``cache`` → 复用 (跨多次调用省重复 open); 否则按
    ``cache_db_path`` 自开自关; 两者皆缺 → 退化为无缓存裸 ``encode_local`` (向后兼容,
    如测试直送 local spec 不带 cache_db_path 的路径)。
    """
    model_id = spec_model(spec, 'shibing624/text2vec-base-chinese')
    version = spec_version(spec)

    own_cache = None
    if cache is None and cache_db_path:
        own_cache = LLMCache(cache_db_path)
        cache = own_cache
    try:
        cached = [
            cache.get(model_id, c, prompt_version=version) if cache is not None else None
            for c in chunks
        ]
        missing_idx = [i for i, res in enumerate(cached) if res is None]
        if len(chunks) > 1:
            logger.info(
                f"    {log_prefix} 本地缓存拦截: 命中 {len(chunks) - len(missing_idx)} "
                f"条, 缺失 {len(missing_idx)} 条 (model={model_id})"
            )

        # 缺失项内部去重 (golden 正确性 + 提速): 同一文本在三轨/回退场景下可重复出现
        # (实测 content_full nunique 1329/1542)。GPU 批 forward 对"同文本不同批位"会给
        # 1-ULP 级 FP 漂移 → 若不去重, 同文本两次出现可取不同值, 而 put_batch 同键后写
        # 覆盖前 → 冷跑(各取各值)与暖跑(同读一值)不一致, 破坏 golden 逐位复现。去重后每个
        # 唯一文本只 forward 一次 (取值唯一确定) → 冷暖逐位一致 + 更快。(跨 full/ctx/ss 三
        # 轨的去重则由共享 cache 连接天然达成: 先嵌的轨写入后, 后续轨同文本即缓存命中。)
        computed_map: dict = {}
        uniq_dim = None
        if missing_idx:
            missing_chunks = [chunks[i] for i in missing_idx]
            unique_texts = list(dict.fromkeys(missing_chunks))  # 保序去重
            if len(unique_texts) < len(missing_chunks):
                logger.info(
                    f"    {log_prefix} 本地去重: 缺失 {len(missing_chunks)} 条 → "
                    f"唯一 {len(unique_texts)} 条 (省 "
                    f"{len(missing_chunks) - len(unique_texts)} 次 forward)"
                )
            uniq_emb = np.asarray(
                encode_local(unique_texts, spec, log_prefix=log_prefix),
                dtype=np.float32,
            )
            uniq_dim = int(uniq_emb.shape[1])
            computed_map = {t: uniq_emb[k] for k, t in enumerate(unique_texts)}
            if cache is not None:
                cache.put_batch(
                    model_id, unique_texts,
                    [json.dumps(uniq_emb[k].tolist()) for k in range(len(unique_texts))],
                    prompt_version=version,
                )

        # 按 chunks 原序复原 (命中条目反序列化 + 新算唯一向量按文本映射回各位置)
        if uniq_dim is not None:
            dim = uniq_dim
        elif cached and cached[0] is not None:
            dim = len(json.loads(cached[0]))
        else:  # 空输入防御 (上游 embed_texts 已挡空 texts, 纯兜底)
            return np.empty((0, 0), dtype=np.float32)
        out = np.empty((len(chunks), dim), dtype=np.float32)
        for i, res in enumerate(cached):
            if res is None:
                out[i] = computed_map[chunks[i]]
            else:
                out[i] = np.asarray(json.loads(res), dtype=np.float32)
        return out
    finally:
        if own_cache is not None:
            own_cache.close()


def embed_texts(texts, spec: dict, *,
                cache_db_path: str | None = None,
                cache=None,
                log_prefix: str = "Embedding",
                enable_archive: bool = True) -> np.ndarray | None:
    """文本 → 文本级 Embedding 向量 (n_texts, dim), spec 决定模型与路径。

    超长文本走朴素分段 (naive chunking) + Mean Pooling。local spec 走 sentence-transformers,
    API spec 走 get_embeddings_api (经 LLMCache 穿透)。失败/形状异常 → None。

    传入已打开的 ``cache`` (LLMCache 实例) 可跨多次 embed_texts 调用复用同一
    sqlite 连接, 省去重复 open/WAL/建表 (2026-06-23 零风险小优化); 未传时按
    ``cache_db_path`` 自动 open/close (向后兼容)。
    local spec (2026-06-23 起) 同样穿透缓存 (经 _encode_local_cached, 键
    = model_id+文本+text_pipeline_version) — 命中即读, 跨 run/跨 stage $0 复现;
    两参数皆缺时退化为无缓存裸 encode_local (向后兼容)。

    fix(omni-g-embed-04, 2026-06-11): 多块池化改为"逐块 L2 归一 + token 数加权"
    (此前等权 mean — 8191+1 token 切分的 1-token 尾段碎片占 50% 方向权重)。切分
    边界与缓存键 (块文本) 不变, 仅消费端池化权重修正。

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
        # 2026-06-23: 本地嵌入改走穿透式缓存 (_encode_local_cached) — 此前每 run
        # 全量重算 (text2vec 是唯一不缓存的嵌入路径)。命中即读 → 跨 run/跨 stage $0。
        raw_emb = _encode_local_cached(
            all_chunks, spec, cache=cache, cache_db_path=cache_db_path,
            log_prefix=log_prefix)
    else:
        if cache is not None:
            # 调用方传入已打开的共享连接 → 跨多次 embed_texts 复用, 省重复 open
            raw_emb = asyncio.run(
                get_embeddings_api(all_chunks, spec, cache,
                                   enable_archive=enable_archive))
        elif cache_db_path:
            with LLMCache(cache_db_path) as _cache:
                raw_emb = asyncio.run(
                    get_embeddings_api(all_chunks, spec, _cache,
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
        # fix(omni-g-embed-04, 2026-06-11) + KNOWN-OPEN⑧ 池化权重修正:
        # (a) 逐块先 L2 归一再平均 — 未归一向量的 mean 隐含按块范数加权 (cosine
        #     消费端尺度不变, 但池化方向被大范数块拖偏);
        # (b) 按块 token 数加权 — 等权下 (8191, 1) 切分的 1-token 尾段碎片占 50%
        #     方向权重, 严重扭曲超长文本的向量表征。
        # 切分边界/块文本不变 → API 路径 LLMCache 缓存键与已存向量不受影响。
        # 白话: 长文切块后合并时, 先把每块向量拉到同一长度(归一), 再按每块
        # 实际有多少字(token 数)来定话语权 — 否则结尾只剩 1 个 token 的小尾巴
        # 会和整整一大块平起平坐, 把合并结果带歪。
        block = raw_emb[start:end].astype(np.float64)
        norms = np.linalg.norm(block, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        unit = block / norms
        w = np.array(
            [max(1, len(_EMB_ENCODING.encode(str(all_chunks[j]))))
             for j in range(start, end)],
            dtype=np.float64,
        )
        pooled = (unit * w[:, None]).sum(axis=0) / w.sum()
        norm = np.linalg.norm(pooled)
        emb[i] = (pooled / norm if norm > 0 else pooled).astype(raw_emb.dtype)
    return emb
