"""news_process.pipeline.text.embedding_engine — 双 API 模型嵌入统一引擎 (v3.15.0, all-API; Qwen ⟂ large co-primary).

设计目标
--------
让任意 callsite (stage 15 policy_alignment / fintech_intensity / 25 article_sbert /
26 policy_similarity / 27 benefit_society / network embedding peer) 用 **显式 spec**
嵌入文本, 从而在一次运行内对同一批文本用两个 co-primary API 模型各算一遍:

  - CO-PRIMARY ① (canonical, 无后缀):  Qwen/Qwen3-Embedding-8B (阿里, OpenAI-compat / 硅基流动, 4096 维)
  - CO-PRIMARY ② (`_lg`):              text-embedding-3-large (OpenAI, OpenAI-compat / yunwu, 3072 维)

两者 **co-primary 对等互证** (非"主轨 + 稳健性附录"): Qwen (阿里/硅基流动) ⟂ large (OpenAI)
是 **跨厂商 / 跨训练数据独立性** —— 审稿人质疑"结论是否只是某厂商模型的偶然产物"时,
两个对等主测度并排互证一致性作答。后缀 `_lg` **仅为列命名机制** (panel 不能两列同名),
**不表达任何主次/优劣**; 无后缀 = canonical 列槽、`_lg` = 孪生列槽。两者 **严格 parity**
(每个无后缀嵌入派生列 ⟺ 恰一个 `_lg` 孪生列, 反之亦然)。**铁律**: 两 co-primary 各自
just-identified 并排报告, **禁混进同一 over-identified Hansen J**。

> v3.14.0 BREAKING: 本引擎**零本地嵌入模型** —— 此前的本地 sentence-transformers 轨
> (text2vec `_t2v` / BAAI/bge-m3 `_bge`) 及其全部本地推理机器 (encode_local /
> torch determinism / HF offline) 已整体移除。所有 spec 均为 API spec, embed_texts
> 收为纯 API 路径 (经 LLMCache 穿透)。

spec 是一个 dict (来自 ``config/features.yaml::embedding_api`` / ``embedding_large``):

    {model, base_url, api_key, text_pipeline_version, batch_size}

本模块**不** import ``pipeline.panel.encode`` (避免循环导入); spec 由 callsite 从其
自有的 CONFIG 传入。LLMCache 键以 ``model_id`` 为首字段 (见 core/caching.py),
故 Qwen (无后缀) 与 large (`_lg`) 两 co-primary 的缓存天然按 model_id 隔离不串。

历史: 本引擎把原先散落在多个 feature 模块里近重复的
``_get_embeddings_api`` / ``_embed_texts_with_chunk_pooling`` 统一为 spec 参数化的
公共函数 (DRY + 让两个 co-primary 嵌入模型成为一等公民)。注: 此处 "多个模型" 指
Qwen3-Embedding-8B 无后缀 vs text-embedding-3-large ``_lg`` 这一 **模型** 维度, 与情感文本的
full/ctx/ss 三轨是两个独立维度。``_lg`` 为 config-gated 列: 仅当配置存在
``embedding_large`` 块时才产出 (缺配置则不产 `_lg` 列); v3.14.0 下两 co-primary
均为活动 config, parity 双射由测试门 + producer both-or-neither 强制。

学术依据 (沿用 strategic_diff/policy_alignment 既有锚点):
  - Reimers & Gurevych (2019, EMNLP) Sentence-BERT mean pooling, DOI 10.18653/v1/D19-1410
  - 朴素分段 (naive / independent chunking) 超长文本分段
  - Carlson & Burbano (2026, SMJ §3.3) version-aware provenance (cache 版本维度)

白话:
    全项目所有"把文本变成向量"的需求都走这一个模块: 调用方传一份 spec
    (写明用哪个 API 模型), 同一批文本就能分别用 Qwen3-Embedding-8B 和 text-embedding-3-large
    两个对等主模型 (跨 阿里/硅基流动 与 OpenAI 两厂商) 各算一遍向量, 互相印证。两者地位
    对等, `_lg` 后缀只是为了避免列名撞车, 没有主次之分。算过的结果存在缓存里,
    下次同样的文本不再花钱重算; 太长的文本先切成小段、各段算完再加权平均成一条向量。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

import numpy as np
import tiktoken

# 日志四位有效数字渲染 (项目规范 2026-06-24): 本模块日志中所有非整数 (命中率/
# 占比/耗时等) 统一经 sig4/pct4, 整数计数仍用千分位。仅供 logger.* 使用, 不参与
# 任何产物计算 (golden-safe)。
from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# ── Embedding token 级精确截断 (统一 stage 15 标准) ──
# cl100k_base 编码, 单条上限 8,191 tokens; 此上限对 Qwen/Qwen3-Embedding-8B (32K 上限) 是
# **保守高估** (cl100k 8191 远低于 Qwen 32K-token 上限 → 数学上恒保守安全; 2026-06-28 硅基流动短文探针正常, 长文全区间留上线实测验证) →
# 批次偏小、永不超限。超长文本 (如权威政策语料) 走朴素分段 (naive chunking) + Mean Pooling。
_EMB_ENCODING = tiktoken.get_encoding("cl100k_base")
EMB_MAX_TOKENS = 8191
EMB_MAX_TOKENS_PER_REQUEST = 250_000

# 2026-06-26 全项目统一: 嵌入 API 每次重试固定间隔 10s (flat, 不再指数退避)
RETRY_DELAY = 10

# 单批瞬时失败 (429/5xx/网络异常) 的最大重试次数。2026-06-23 用户决策: 大模型 / 嵌入
# API 调用失败一律按各自既有方法重试 80 次, 耗尽后走各自现有终态处理 — 与 stage 21
# tone_llms 的 tone_llm_processing.max_retries=80 统一 (此前嵌入是 ``while True`` 无限
# 重试)。耗尽 → raise EmbeddingRetryExhaustedError → get_embeddings_api 捕获 → 返回
# None → 上游 _cosine_for_spec / policy_alignment 把该 spec/轨列置 NaN (优雅降级, 对称
# tone_llms "瞬时失败重试 80 次后从多数投票缺席")。
EMB_MAX_RETRIES = 80


class EmbeddingRetryExhaustedError(RuntimeError):
    """嵌入 API 单批瞬时失败 (429/5xx/网络) 重试 ``EMB_MAX_RETRIES`` 次仍未成功。

    专用于把"可重试的瞬时故障耗尽"与"不可恢复的致命错误"区分开:
      - 本异常 (瞬时耗尽): 由 ``get_embeddings_api`` 捕获 → 返回 ``None`` → 上游列置 NaN
        (优雅降级, 与 stage 21 tone_llms 80 次后缺席投票对称)。
      - ``ValueError`` (致命: 401/403/400 等非 5xx 状态 / 缺 'data' 字段): **不**在
        ``get_embeddings_api`` 捕获, 仍按现有路径 raise 冒泡 (该 spec/轨 crash)。
    """

# API 嵌入批次最大并发数 (asyncio.gather + Semaphore 上限)。各批次结果按 batch_idx
# 索引收集再按序重组 (绝不依赖完成顺序), 故并发对产出逐位不变, 仅缩短 wall-clock。
# ⚠ 若调高需留意上游 API 的 RPS / 并发限流 (429 已由 per-batch 固定 10s 间隔重试兜底)。
EMB_API_CONCURRENCY = 100

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


# 进程级幂等标志: 引擎方法学/配置 banner 只 emit 一次 (本模块是无独立 main 的共享
# 嵌入引擎, 被 stage 15/25/26/27/network 的 runner 调用, 复用调用方阶段日志; banner
# 一旦在首个 callsite 触发即对全进程后续调用静默, 避免重复刷屏)。
_ENGINE_BANNER_DONE = False


def _log_engine_banner(spec: dict | None = None, *, log_prefix: str = "Embedding") -> None:
    """嵌入引擎子步骤 banner: 方法论引文 (含 DOI) + 关键引擎配置, 进程内只 emit 一次.

    本模块无独立 ``main()/run_stage()`` (是被 feature-stage runner 调用的共享库), 故
    依 ENRICHMENT_PLAYBOOK §0.5 "called-by-runner helper" 规约: **不**重复打 ENV/CONFIG
    全块 (那是 runner 入口职责), 仅在首个被调函数起始处打一个子步骤 banner —— 步骤名
    + 方法依据引文 (逐字取自经核验参考文献注册表) + 本引擎可调常量。emit 只发生在函数
    体内 (绝不在模块顶层 import 时执行, 避免 setup_logging 首写截断生产日志)。

    纯日志, 不读写任何产物 / 不改控制流; 任何异常被吞掉以保证绝不拖垮嵌入阶段
    (golden-safe)。
    """
    global _ENGINE_BANNER_DONE
    if _ENGINE_BANNER_DONE:
        return
    _ENGINE_BANNER_DONE = True
    try:
        logger.info(f"  ── 嵌入引擎子步骤: 文本→向量统一引擎 ({log_prefix}) ──")
        # ① 方法论依据 (引文逐字取自经核验注册表, 进 .log 而非仅留 docstring)
        logger.info("     📖 方法论依据 (核心方法/构念学术出处, 引文取自经核验注册表):")
        logger.info("       · 超长文本分段 Mean Pooling (Sentence-BERT mean pooling):")
        logger.info(
            "         Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence "
            "embeddings using Siamese BERT-networks. In Proceedings of the 2019 "
            "Conference on Empirical Methods in Natural Language Processing and the "
            "9th International Joint Conference on Natural Language Processing "
            "(EMNLP-IJCNLP) (pp. 3980-3990). Association for Computational "
            "Linguistics. https://doi.org/10.18653/v1/D19-1410")
        logger.info(
            "       白话: 太长的文本先按 token 切成小段, 各段算完向量后逐块归一+按 "
            "token 数加权平均成一条 (mean pooling), 避免超长文被静默截断。")
        logger.info("       · language embedding 测度范式 (用嵌入向量度量文本语义立场):")
        logger.info(
            "         Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit "
            "society? A language embedding approach. The Review of Financial Studies, "
            "39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012")
        logger.info(
            "       白话: 用 BERT 句嵌入测文本语义立场已成顶刊范式, 本引擎产出的向量即"
            "服务于 policy/strategic/benefit 等阶段的语义相似度 (余弦) 测度。")
        logger.info("       · 嵌入相似度的可解释性 (为何归一化向量余弦 = 语义相似度):")
        logger.info(
            "         Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. "
            "(2025). Interpretable text embeddings and text similarity explanation: A "
            "survey. In Proceedings of the 2025 Conference on Empirical Methods in "
            "Natural Language Processing (pp. 22314-22330). Association for Computational "
            "Linguistics. https://doi.org/10.18653/v1/2025.emnlp-main.1135")
        logger.info(
            "       白话: 本引擎对每条向量逐块 L2 归一后再加权池化 (输出单位向量), 故下游"
            "余弦 ≡ 点积 = 标准语义相似度; 该综述系统梳理嵌入相似度的可解释性与适用边界, "
            "为本引擎'归一→余弦'的测度链提供方法学依据。")
        # ② 关键引擎配置 (本模块可调常量 + 本次 spec; 路径/参数级 CONFIG 由 runner 入口打)
        # v3.14.0: 全 spec 均为 API spec (零本地模型) → 路径恒为 API (穿透 LLMCache)。
        if spec is not None:
            _model = spec_model(spec)
            _route = "API (穿透 LLMCache)"
            _bs = int((spec or {}).get('batch_size', 32) or 32)
            logger.info(
                f"     ⚙ 本次 spec: model={_model} · 路径={_route} · "
                f"batch_size={_bs:,d} · cache_version={spec_version(spec)}")
        logger.info(
            f"     ⚙ 引擎常量: 单条上限={EMB_MAX_TOKENS:,d} tokens (cl100k_base) · "
            f"单请求 token 上限={EMB_MAX_TOKENS_PER_REQUEST:,d} · "
            f"API 并发上限={EMB_API_CONCURRENCY:,d} · 瞬时失败重试={EMB_MAX_RETRIES:,d} 次")
        logger.info(
            "     ⚙ 确定性/成本: 两 co-primary API 模型 (Qwen3-Embedding-8B 无后缀 ⟂ "
            "text-embedding-3-large `_lg`) miss 即付费, 命中 $0; 两轨缓存按 model_id "
            "隔离 → 命中逐位复现。")
    except Exception as _banner_exc:  # pragma: no cover - banner 绝不拖垮阶段
        logger.warning(f"    嵌入引擎 banner 输出失败 (不阻塞): {_banner_exc!r}")


# 纯 base_url 谓词 (v3.14.0): 本地推理机器已整体删除, 全部 spec 为 API → 此谓词对任何
# API spec 恒 False。保留为纯函数, 让各 producer 的 fail-fast 守卫
# `if _eng.spec_uses_local(s) or s is EMBEDDING_CONFIG: raise` 语义稳定 (MAIN 崩 / _lg 软降级),
# 且未来若再引入本地 spec 可即生效。不再有任何本地编码路径消费它。
_LOCAL_BASE_URLS = {'local', 'local://', 'sentence-transformers', 'sentence_transformers'}


def spec_uses_local(spec: dict | None) -> bool:
    """spec 是否指向本地端点 (非 API)。v3.14.0 全 API → 对生产 spec 恒 False; 保留为纯谓词。"""
    base_url = str((spec or {}).get('base_url') or '').strip().lower()
    return base_url in _LOCAL_BASE_URLS


def spec_model(spec: dict | None, default: str = 'Qwen/Qwen3-Embedding-8B') -> str:
    """取 spec 的 model 名; 缺失时回退到 default (co-primary ① canonical)。"""
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


async def get_embeddings_api(texts, spec: dict, cache=None, *,
                             enable_archive: bool = True) -> np.ndarray | None:
    """通过 API 获取文本 Embedding — 穿透式缓存 + 动态分批 + 有界重试(80次)容错。

    spec 提供 base_url / api_key / model / text_pipeline_version。
    与 LLMCache 配合: cache 命中的文本不重复调用; 写回时按 model_id+version 命名空间。

    可重试的瞬时故障 (429/5xx/网络异常) 按 ``EMB_MAX_RETRIES`` (=80) 次固定 ``RETRY_DELAY`` (=10s) 间隔重试 (flat, 2026-06-26 全项目统一, 不再指数退避);
    任一批耗尽仍失败 → 捕获 EmbeddingRetryExhaustedError → 返回 ``None`` (调用方据此把
    该轨列置 NaN, 优雅降级, 对称 tone_llms 80 次后缺席投票)。不可恢复的致命错误 (非 5xx
    状态 / 缺 'data' / 缺 base_url+api_key / 单条超限) 仍立即 raise (现有路径不变)。
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
        _n_hit = len(texts) - len(missing_texts)
        logger.info(
            f"    缓存拦截: 命中 {_n_hit:,} 条, "
            f"缺失 {len(missing_texts):,} 条 / 共 {len(texts):,} 条 "
            f"(命中率 {pct4(_n_hit / len(texts))}, model={embedding_model})"
        )
        # 命中分桶诊断 (按字符长度: 短/中/长) — 揭示是否长文系统性更易 miss (长文走
        # 朴素分段 → 子块更多 → 任一子块 miss 即整文需联网回填)。按 len(str) 廉价分桶,
        # 不触 tiktoken / 不上热路径成本; 仅读已算好的 cached_results, 失败静默跳过 (golden-safe)。
        try:
            _buckets = {'短 (<2000 字)': [0, 0], '中 (2000-20000 字)': [0, 0],
                        '长 (>20000 字, 多走分段)': [0, 0]}
            for _t, _res in zip(texts, cached_results):
                _ln = len(str(_t))
                _key = ('短 (<2000 字)' if _ln < 2000
                        else '中 (2000-20000 字)' if _ln <= 20000
                        else '长 (>20000 字, 多走分段)')
                _buckets[_key][0] += 1                    # 该桶总条数
                if _res is not None:
                    _buckets[_key][1] += 1                # 该桶命中条数
            _parts = [
                f"{_k} {_v[1]:,}/{_v[0]:,} ({pct4(_v[1] / _v[0])})"
                for _k, _v in _buckets.items() if _v[0] > 0
            ]
            if _parts:
                logger.info("      └─ 命中分桶 (字符长度): " + " | ".join(_parts))
        except Exception as _bkt_exc:  # noqa: BLE001 — 诊断分桶, 失败不阻塞嵌入
            logger.debug(f"      └─ 命中分桶诊断跳过 (不影响产物): {_bkt_exc!r}")

    missing_embs: list = []
    if missing_texts:
        # P1→P3 加固 (2026-06-26): 与 stage 21 (tone_llms.LLMCacheMissError) 对称的离线确定性闸 —
        # NEWS_PROCESS_LLM_OFFLINE=1 时嵌入缓存 miss 即 raise (在 session.post 之前), 杜绝
        # 付费/非确定网络调用污染产物列, 兑现"离线 $0/零网络/逐位复现"契约。命中路径与生产
        # 首跑 (env 未设) 完全不变 → golden-safe。
        if os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '').strip().lower() in (
                '1', 'true', 'yes', 'on'):
            raise RuntimeError(
                f"离线确定性模式 (NEWS_PROCESS_LLM_OFFLINE=1) 嵌入缓存 miss: "
                f"model={embedding_model} prompt_version={text_pipeline_version} "
                f"n_missing={len(missing_texts):,}; 需在线回填嵌入缓存或检查语料/"
                f"text_pipeline_version 是否相对 golden 漂移"
            )
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
            last_err = ""
            async with _sem:
                for attempt in range(EMB_MAX_RETRIES):
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
                                last_err = f"HTTP {status}: {err_text[:100]}"
                                logger.warning(
                                    f"    HTTP {status} (batch {batch_idx + 1}): "
                                    f"{err_text[:100]}。重试 "
                                    f"{attempt + 1}/{EMB_MAX_RETRIES}, 休眠 {delay}s..."
                                )
                                await asyncio.sleep(delay)
                            else:
                                err_text = await resp.text()
                                raise ValueError(
                                    f"不可恢复的 API 错误 {status} "
                                    f"(batch {batch_idx + 1}): {err_text[:200]}"
                                )
                    except ValueError:
                        raise
                    except Exception as e:
                        last_err = f"{type(e).__name__}: {e}"
                        logger.warning(
                            f"    网络异常 (batch {batch_idx + 1}): "
                            f"{type(e).__name__}: {e}。重试 "
                            f"{attempt + 1}/{EMB_MAX_RETRIES}, 休眠 {delay}s..."
                        )
                        await asyncio.sleep(delay)
                # 瞬时失败 (429/5xx/网络) 重试 EMB_MAX_RETRIES 次仍未成功 → 抛
                # EmbeddingRetryExhaustedError, 由 get_embeddings_api 捕获 → 返回 None
                # → 该 spec/轨列置 NaN (优雅降级, 对称 tone_llms 80 次后缺席投票)。
                # 致命错误 (上方 raise ValueError) 不会到这里, 仍立即冒泡 (现有路径不变)。
                raise EmbeddingRetryExhaustedError(
                    f"嵌入 batch {batch_idx + 1} 重试 {EMB_MAX_RETRIES} 次仍失败"
                    + (f" (末次: {last_err})" if last_err else "")
                )

        async with aiohttp.ClientSession() as session:
            try:
                await asyncio.gather(*[
                    _process_batch(i, b, session) for i, b in enumerate(batches)
                ])
            except EmbeddingRetryExhaustedError as _exhausted:
                # 任一批瞬时失败重试 EMB_MAX_RETRIES 次仍失败 → 整个 spec/轨优雅返回 None
                # (上游列置 NaN), 对称 tone_llms 80 次后缺席投票; 不向上冒泡 (区别于致命
                # ValueError 的现有崩溃路径)。
                logger.error(
                    f"    嵌入 API 重试 {EMB_MAX_RETRIES} 次仍失败 → 返回 None "
                    f"(该轨列将置 NaN): {_exhausted}"
                )
                return None

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


def embed_texts(texts, spec: dict, *,
                cache_db_path: str | None = None,
                cache=None,
                log_prefix: str = "Embedding",
                enable_archive: bool = True) -> np.ndarray | None:
    """文本 → 文本级 Embedding 向量 (n_texts, dim), spec 决定 API 模型。

    超长文本走朴素分段 (naive chunking) + Mean Pooling。v3.14.0 起所有 spec 均为 API
    spec → 一律走 get_embeddings_api (经 LLMCache 穿透)。失败/形状异常 → None。

    传入已打开的 ``cache`` (LLMCache 实例) 可跨多次 embed_texts 调用复用同一
    sqlite 连接, 省去重复 open/WAL/建表 (2026-06-23 零风险小优化); 未传时按
    ``cache_db_path`` 自动 open/close (向后兼容); 两者皆缺则无缓存裸调 API。

    fix(omni-g-embed-04, 2026-06-11): 多块池化改为"逐块 L2 归一 + token 数加权"
    (此前等权 mean — 8191+1 token 切分的 1-token 尾段碎片占 50% 方向权重)。切分
    边界与缓存键 (块文本) 不变, 仅消费端池化权重修正。

    Returns:
        np.ndarray (n_texts, dim) | None
    """
    texts = [] if texts is None else list(texts)
    if len(texts) == 0:
        return None

    # called-by-runner 子步骤 banner (方法引文 + 引擎配置), 进程内只 emit 一次。
    _log_engine_banner(spec, log_prefix=log_prefix)

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
            f"    {log_prefix} 分段: {n_orig:,} 文本 → {n_chunks:,} 段 "
            f"(含 {n_chunks - n_orig:,} 个超长文本扩展段, "
            f"段/文本扩展因子 {sig4(n_chunks / n_orig)})"
        )

    # v3.14.0: 全 spec 均为 API spec (零本地模型) → 一律走 get_embeddings_api (LLMCache 穿透)。
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
    # get_embeddings_api 在瞬时失败重试 EMB_MAX_RETRIES 次耗尽时返回 None →
    # 该轨整体置 NaN (优雅降级, 对称 tone_llms 80 次后缺席投票)。
    if raw_emb is None:
        logger.warning(
            f"    {log_prefix}: API ({spec_model(spec)}) 重试耗尽返回 None "
            f"→ 该轨置 NaN"
        )
        return None
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
