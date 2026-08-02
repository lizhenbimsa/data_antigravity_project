"""news_process.pipeline.text.embedding_engine — 双 API 模型嵌入统一引擎 (v3.15.0, all-API; Qwen ⟂ large co-primary).

设计目标
--------
让任意 callsite (stage 15 policy_alignment / fintech_intensity / 25 article_sbert /
26 policy_similarity / 27 benefit_society / network embedding peer) 用 **显式 spec**
嵌入文本, 从而在一次运行内对同一批文本用两个 co-primary API 模型各算一遍:

  - CO-PRIMARY ① (canonical, 无后缀):  Qwen/Qwen3-Embedding-8B (阿里, OpenAI-compat / 硅基流动, 4096 维)
  - CO-PRIMARY ② (`_lg`):              text-embedding-3-large (OpenAI, OpenAI-compat / OpenLux, 3072 维)

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
  - Sandve et al. (2013, PLoS Comput Biol) 可复现计算研究: 版本化/provenance 留痕
    (text_pipeline_version 作 cache 版本维度), DOI 10.1371/journal.pcbi.1003285

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
import time

try:
    from threadpoolctl import threadpool_limits as _threadpool_limits
except ImportError:      # threadpoolctl 是 sklearn 依赖; 极端裸环境缺失则退化为无操作
    from contextlib import nullcontext as _nullcontext

    def _threadpool_limits(limits=None, user_api=None):
        return _nullcontext()

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
# fix(2026-07-24): 新增环境变量 NEWS_PROCESS_EMB_MAX_TOKENS_PER_REQ 运维覆盖 (默认
#   250_000 不变)。动因 = stage 16 生产首播 `_lg`/OpenLux 轨: 25 万 token 大批在服务端
#   高峰时段响应超过单次尝试 180s 超时 → 全部批反复 TimeoutError 重试, 吞吐塌缩到
#   ~5 批/80min (2026-07-24 18:20-19:44 实证)。调小单批 token 上限使响应回到秒级即可
#   绕开; 分批口径只影响请求分组, 不进缓存键 (缓存键=逐字文本), 对产出逐位无影响。
EMB_MAX_TOKENS_PER_REQUEST = int(os.environ.get(
    'NEWS_PROCESS_EMB_MAX_TOKENS_PER_REQ', '250000'))

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
# fix(2026-07-24): 新增环境变量 NEWS_PROCESS_EMB_CONCURRENCY 运维覆盖 (默认 250 不变,
#   仍即 2026-07-21 用户决策)。动因 = stage 16 生产首播 (2025 语料新嵌入面) 撞硅基流动
#   TPM 限流: 250 并发把 token 预算瞬间打满 → 大面积 429 重试风暴, 尾部批 80 次×10s
#   重试耗尽 → 整轨 None→NaN。TPM 是吞吐硬约束时降并发不损失 wall-clock, 却把"排队深度
#   超过 800s 重试耐心"的耗尽风险显著压低; 并发只影响墙钟不影响产出字节 (见上注)。
EMB_API_CONCURRENCY = int(os.environ.get('NEWS_PROCESS_EMB_CONCURRENCY', '250'))

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
            "text-embedding-3-large `_lg`) 在线 miss 即付费, 命中 $0 (离线 "
            "NEWS_PROCESS_LLM_OFFLINE=1 时 miss→raise RuntimeError 零网络); 两轨缓存按 "
            "model_id 隔离 → 命中逐位复现。")
        # 📖 version-aware provenance 运行期出处 (docstring §40 早已声明, 此处兑现到 .log):
        # 本引擎以 text_pipeline_version 作 LLMCache 命名空间 + preview/可换端点的模型漂移
        # caveat, 正是"可复现计算研究"对版本化、provenance 留痕规约的具体落地。
        # 白话: 嵌入是模型产出的"数据", 换模型/换端点结论可能变, 故每条缓存都带模型版本号,
        # 重跑时按版本对齐, 这一可复现做法的方法学出处即下文 (引文逐字取自经核验注册表)。
        logger.info(
            "     📖 版本感知 provenance (cache 版本维度 / 模型生成数据可复现):")
        logger.info(
            "         Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). "
            "Ten simple rules for reproducible computational research. "
            "PLoS Computational Biology, 9(10), e1003285. "
            "https://doi.org/10.1371/journal.pcbi.1003285")
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
    # F2 (2026-07-16): disallowed_special=() — 语料含 "<|endoftext|>" 等特殊 token
    # 字面量时按普通文本 BPE 而非抛 ValueError (该 ValueError 发生在分批/重试/None→NaN
    # 降级之前且无捕获, 单篇毒丸文章曾可崩掉整个嵌入阶段); 无特殊字面量的文本逐 token
    # 不变 (字节等价, 缓存键为文本键零漂移)。本文件三处同修 (:246/:346/:617 原行号)。
    tokens = _EMB_ENCODING.encode(text, disallowed_special=())
    if len(tokens) <= EMB_MAX_TOKENS:
        return [text]
    # ── F21 后置条件强制 (2026-07-26 生产实弹) ──────────────────────────────
    # 现场: stage 40 (strategic_diff bank-year 超级文档, 2017 年) 跑 2 小时后崩于
    #   `RuntimeError: Embedding 单条输入超限: 8192 > 8191` —— 即**本函数切出的块**
    #   在下游 `get_embeddings_api` 被重新 encode 时算出 8192 token, 违反本函数契约,
    #   而那条守卫是**致命不可重试**的 raise → 整阶段报废。
    # 复现记录 (据实): 前两次尝试 (①真实语料滑动 292 个切点; ②按 '\n' 复刻 2017 年
    #   428 条超级文档) **均未复现** —— 因连接符错了 (strategic_diff 实际用**空格**
    #   `' '.join`) 且未取最长文档。第三次按真实口径取**最长 60 条** bank-year 超级文档,
    #   **复现成功**: 4 条含病态块 (受影响年份 2017/2018/2022/2023)。
    #   即便如此, 本函数仍**不依赖对成因的判断**, 而是直接强制后置条件: 每个返回块实测
    #   回编码 ≤ EMB_MAX_TOKENS, 不满足就收缩 token 窗口重切 —— 与漂移成因无关, 恒成立。
    # 兼容性 (实测, 非推断): 对回编码守恒的文本, `hi` 一次命中即等于旧的
    #   `tokens[i:i+EMB_MAX_TOKENS]` → 切块字面与旧版**逐字节相同** (60 条最长超级文档中
    #   **56 条完全一致**)。仅含病态块的 4 条文档切块改变 (707/14,684 块 = 4.81%);
    #   而**那些文档此前根本产不出结果** —— 实测变化前后的 707 个块在缓存中命中数**均为 0**
    #   ⟹ **零有效结果失效、零重复付费** (新块属首次付费, 本就要付)。
    out: list[str] = []
    lo, n_tok = 0, len(tokens)
    while lo < n_tok:
        hi = min(lo + EMB_MAX_TOKENS, n_tok)
        piece = _EMB_ENCODING.decode(tokens[lo:hi])
        # 回编码守恒守卫: 超限则按几何比例收缩窗口 (避免逐 token 回退的 O(n) 重编码)
        for _ in range(64):                       # 有界重试, 防病态输入死循环
            if len(_EMB_ENCODING.encode(piece, disallowed_special=())) <= EMB_MAX_TOKENS:
                break
            shrink = max(1, (hi - lo) // 32)
            hi = max(lo + 1, hi - shrink)
            piece = _EMB_ENCODING.decode(tokens[lo:hi])
        else:
            logger.warning(
                f"    split_text_for_embedding: 块 [{lo}:{hi}] 收缩 64 次仍超限 "
                f"(原文 {n_tok:,d} token) — 按当前窗口放行, 交由下游守卫处理")
        out.append(piece)
        lo = hi
    return out


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

    # ── F18 (2026-07-28): 分段计时 —— 让「这段时间到底花在 API 还是 CPU」可归因 ──
    # 为何: 2026-07-27 生产跑里 stage 40 的「步骤 7h-emb 嵌入同业网」吃掉 20,471s
    # (整个 stage 的 **20.31%**), 而它是 API/CPU 各占多少**至今无人知道** —— 因为
    # 本模块用 getLogger(__name__) 且此前无 handler (F29), INFO 一条都没落过盘,
    # 审计只能靠「数据库文件长胖了多少」反推是否在付费。这不该是审计的姿势。
    # 三段: ①缓存查 (SQLite 读) ②API 等 (含 429 退避) ③写回+组装。
    _t_start = time.time()
    _t_cache_done = _t_api_done = None
    texts = [] if texts is None else list(texts)
    if len(texts) == 0:
        return np.empty((0, 0), dtype=np.float32)

    base_url = (spec or {}).get('base_url')
    api_key = (spec or {}).get('api_key')
    embedding_model = spec_model(spec)
    text_pipeline_version = spec_version(spec)

    # ── F1 流式化 (2026-07-16, FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN §2-F1) ──
    # 旧实现: cached_results 全量物化 N 条 JSON 字符串 (~90KB/条实测) + final_embs
    # 全量 json.loads Python 列表 (~130KB/条) 双份同活 ≈ 13.5× 临时放大 → 生产
    # post-13 语料 ≥~55 万篇越过 128GB; 离线 0-miss 复现路径 (最常用) 同样中招。
    # 新实现: 逐条 get → json.loads → 立即写入预分配 (N, dim) float32 矩阵并释放;
    # miss 批成功后经 fancy indexing 直写对应全局行。数值逐位等价: 逐行
    # np.asarray(lst, float32) 与旧 np.array(list_of_lists, float32) 同 JSON 输入
    # 逐位相同 (同一 double→float32 舍入路径; gate = test_embedding_engine_streaming)。
    out: np.ndarray | None = None   # dim 由首个命中 (全 miss 时由首个完成批) 确定后分配
    dim: int | None = None
    # 写行完备**掩码** (F2 修复 2026-07-25, 取代旧的单调自增计数器 `_rows_written`):
    # 旧计数器在「批已成功写 out → 随后 cache.put_batch 抛异常 (如 SQLite
    # `disk I/O error` / `database is locked`) → 被泛 except 捕获 → 整批重试 → 再次
    # `+= len(batch)`」路径下**重复计数**, 使终局 `assert _rows_written == len(texts)`
    # 误报为写行完备性破坏, 把一次可恢复的瞬时 DB 故障放大成 **AssertionError 崩掉整轨**
    # (生产 stage 25 首播实弹: `written=2108 != N=2000`, 2026-07-25 22:35)。
    # 掩码按**全局行号**置位, 幂等 ⟹ 同批重试任意次结果不变; 语义 (防漏写/双写/错位) 不变。
    _written = np.zeros(len(texts), dtype=bool)
    missing_indices: list[int] = []
    # 命中分桶诊断 (按字符长度) — 同遍累加计数器, 不再依赖全量结果列表 (输出格式不变)
    _buckets = {'短 (<2000 字)': [0, 0], '中 (2000-20000 字)': [0, 0],
                '长 (>20000 字, 多走分段)': [0, 0]}

    def _alloc_out(_dim: int) -> np.ndarray:
        logger.info(
            f"    预分配输出矩阵: {len(texts):,} × {_dim} float32 "
            f"≈ {len(texts) * _dim * 4 / 1e6:,.1f} MB (F1 流式化, 峰值 ≈ 矩阵本身)"
        )
        return np.empty((len(texts), _dim), dtype=np.float32)

    for _i, _text in enumerate(texts):
        _res = (cache.get(embedding_model, _text, prompt_version=text_pipeline_version)
                if cache else None)
        _ln = len(str(_text))
        _bk = _buckets['短 (<2000 字)' if _ln < 2000
                       else '中 (2000-20000 字)' if _ln <= 20000
                       else '长 (>20000 字, 多走分段)']
        _bk[0] += 1
        if _res is None:
            missing_indices.append(_i)
            continue
        _bk[1] += 1
        _row = json.loads(_res)
        if dim is None:
            dim = len(_row)
            out = _alloc_out(dim)
        if len(_row) != dim:
            # 逐行维度断言 (含首个之后每行) — 防损坏缓存条目 (如 len=1) 被 numpy
            # 标量广播静默填行冒充有效嵌入
            raise RuntimeError(
                f"缓存嵌入维度不齐: 第 {_i} 条 len={len(_row)} != dim={dim} "
                f"(model={embedding_model})"
            )
        out[_i] = np.asarray(_row, dtype=np.float32)
        _written[_i] = True

    missing_texts = [texts[_i] for _i in missing_indices]
    _t_cache_done = time.time()          # F18 分段①: 缓存查结束

    if len(texts) > 1:
        _n_hit = len(texts) - len(missing_texts)
        logger.info(
            f"    缓存拦截: 命中 {_n_hit:,} 条, "
            f"缺失 {len(missing_texts):,} 条 / 共 {len(texts):,} 条 "
            f"(命中率 {pct4(_n_hit / len(texts))}, model={embedding_model})"
        )
        try:
            _parts = [
                f"{_k} {_v[1]:,}/{_v[0]:,} ({pct4(_v[1] / _v[0])})"
                for _k, _v in _buckets.items() if _v[0] > 0
            ]
            if _parts:
                logger.info("      └─ 命中分桶 (字符长度): " + " | ".join(_parts))
        except Exception as _bkt_exc:  # noqa: BLE001 — 诊断分桶, 失败不阻塞嵌入
            logger.debug(f"      └─ 命中分桶诊断跳过 (不影响产物): {_bkt_exc!r}")

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
        # 动态分批: 单批 <= 2000 条 且 token 总和 <= EMB_MAX_TOKENS_PER_REQUEST;
        # F1: 同步预存每批对应的全局行号 (missing_indices 子数组, 直写定位用)
        batches: list[list[str]] = []
        batch_rows: list[list[int]] = []
        current_batch: list[str] = []
        current_rows: list[int] = []
        current_tokens = 0
        for _pos, text in enumerate(missing_texts):
            n_tok = max(1, len(_EMB_ENCODING.encode(text, disallowed_special=())))
            if n_tok > EMB_MAX_TOKENS:
                # F21 (2026-07-26): 本守卫在 stage 40 生产跑中被触发 (8192 > 8191) 并
                # 致命中断整阶段, 但旧消息**只有两个数字**, 无法定位是哪条文本/哪次调用
                # → 上游排查只能靠猜 (实测两条复现路径均未命中)。补足可定位信息;
                # split_text_for_embedding 已强制后置条件, 正常路径下本分支不可达。
                raise RuntimeError(
                    f"Embedding 单条输入超限: {n_tok} > {EMB_MAX_TOKENS} "
                    f"(model={embedding_model}, missing_texts 第 {_pos} 条 / 共 "
                    f"{len(missing_texts):,d}, 全局行号={missing_indices[_pos]}, "
                    f"字符数={len(str(text)):,d}, 首 80 字={str(text)[:80]!r}) — "
                    f"上游 split_text_for_embedding 的后置条件被破坏, 请连同本消息报缺陷"
                )
            if current_batch and (
                len(current_batch) >= 2000
                or current_tokens + n_tok > EMB_MAX_TOKENS_PER_REQUEST
            ):
                batches.append(current_batch)
                batch_rows.append(current_rows)
                current_batch = []
                current_rows = []
                current_tokens = 0
            current_batch.append(text)
            current_rows.append(missing_indices[_pos])
            current_tokens += n_tok
        if current_batch:
            batches.append(current_batch)
            batch_rows.append(current_rows)

        n_batches = len(batches)
        if n_batches > 1:
            logger.info(
                f"    网络请求: 动态分批为 {n_batches} 批 "
                f"(并发度 ≤ {min(EMB_API_CONCURRENCY, n_batches)})"
            )

        # ── 并发批次 (asyncio.gather + Semaphore) ──
        # ⚠ 铁律 (verify:concurrent-batches-safe 对抗审计逮到的静默错位坑):
        #   旧实现曾用顺序累加, 批次完成乱序即向量静默错位。F1 (2026-07-16):
        #   _embs_by_idx 中转 dict 退役 — 各批成功后立即把 batch_embs 直写 out 的
        #   对应全局行 out[batch_rows[batch_idx]] (fancy indexing — hit/miss 交错时
        #   行号非连续, 禁 out[offset:offset+m] 连续切片; asyncio 单线程写行原子,
        #   完成乱序无碍, gate T9 锁死), miss 侧不再累积全量 Python 列表 (首次播种
        #   路径同样去放大)。
        _done = 0
        _sem = asyncio.Semaphore(max(1, min(EMB_API_CONCURRENCY, n_batches)))

        async def _process_batch(batch_idx: int, batch: list[str], session) -> None:
            nonlocal _done, out, dim
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
                                # F1 逐批数量校验 (旧全局断言的逐批等价迁移): API 短
                                # 响应若直写会被 numpy (1,dim)→(m,dim) 广播成整段复制
                                # 行。必须 ValueError (经下方 except ValueError: raise
                                # 穿透重试环, 镜像上方缺 'data' 先例); 裸 assert 会被
                                # 泛捕获吞入 80×10s 重试后 return None — fail-loud
                                # 退化为慢速降级 (R3 评审定谳)。
                                if len(batch_embs) != len(batch):
                                    raise ValueError(
                                        f"批 {batch_idx + 1} 返回数量异常: "
                                        f"expected {len(batch)}, got {len(batch_embs)}"
                                    )
                                if dim is None:
                                    # 全 miss 场景: dim 由首个完成的批确定 (asyncio
                                    # 单线程, 无竞态; 后续批按 shape 校验对齐)
                                    dim = len(batch_embs[0])
                                    out = _alloc_out(dim)
                                _arr = np.asarray(batch_embs, dtype=np.float32)
                                if _arr.ndim != 2 or _arr.shape[1] != dim:
                                    raise ValueError(
                                        f"批 {batch_idx + 1} 嵌入维度不齐: "
                                        f"shape={_arr.shape} != (*, {dim})"
                                    )
                                _rows_idx = np.asarray(batch_rows[batch_idx], dtype=np.intp)
                                out[_rows_idx] = _arr
                                _written[_rows_idx] = True      # 幂等置位 (重试安全, 见 F2)
                                # fix(M1, 2026-07-16, FATAL_DEFECT_REMEDIATION §2-M1):
                                # 归档前移至 put_batch 之前, 归档失败跳过缓存写入 —
                                # 消除"先 put 后 archive 失败 → 批已入缓存永久命中、
                                # 归档一次性永久漏档"窗口 (镜像 tone_llms
                                # omni-g-tonellms-04 的 _archive_ok 范式; 代价 =
                                # 归档失败批下次 run 重调一次)。enable_archive=False
                                # / 归档模块缺席时照常缓存 (与 tone_llms 同语义)。
                                _archive_ok = True
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
                                        _archive_ok = False
                                        logger.warning(
                                            f"    LLM archive (batch {batch_idx + 1}) "
                                            f"失败 (不阻塞; 本批不写缓存, 下次 run "
                                            f"重调+重试归档): {_arch_exc!r}"
                                        )
                                if cache and _archive_ok:
                                    # fix(F2, 2026-07-25): put_batch 失败**不再冒泡**到外层
                                    # 泛 except → 不再触发整批重试。旧行为下一次 SQLite 瞬时
                                    # 故障 (`disk I/O error` / 并发 `database is locked`) 会
                                    # ① 白白**重调一次付费 API**, ② 令写行计数重复 (见 F2 掩码
                                    # 注释) 进而 AssertionError 崩掉整轨。本批向量此刻已正确写入
                                    # `out`, 缺的只是缓存条目 → 语义与上方归档失败一致:
                                    # 本轮结果照常可用, 下次 run 该批 cache miss 重调即可自愈。
                                    try:
                                        cache.put_batch(
                                            embedding_model,
                                            batch,
                                            [json.dumps(emb) for emb in batch_embs],
                                            prompt_version=text_pipeline_version,
                                        )
                                    except Exception as _put_exc:  # noqa: BLE001
                                        logger.warning(
                                            f"    缓存写入 (batch {batch_idx + 1}) 失败 "
                                            f"(不阻塞、不重试、不重调 API; 本批向量本轮有效, "
                                            f"下次 run 该批 cache miss 重调自愈): {_put_exc!r}"
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
                _t_api_done = time.time()      # F18 分段②: API 段结束 (仅成功路径)
            except EmbeddingRetryExhaustedError as _exhausted:
                # 任一批瞬时失败重试 EMB_MAX_RETRIES 次仍失败 → 整个 spec/轨优雅返回 None
                # (上游列置 NaN), 对称 tone_llms 80 次后缺席投票; 不向上冒泡 (区别于致命
                # ValueError 的现有崩溃路径)。F1: 部分填充的 out 随作用域丢弃, 绝不外泄
                # (已成功批的 put_batch/归档副作用照旧保留, 与旧行为一致)。
                logger.error(
                    f"    嵌入 API 重试 {EMB_MAX_RETRIES} 次仍失败 → 返回 None "
                    f"(该轨列将置 NaN): {_exhausted}"
                )
                # F18: 失败路径也要留下分段计时 —— 这条正是 F28 那次数据丢失的现场,
                # 当时既不知道它等了多久, 也不知道 API/CPU 各占多少。
                logger.error(
                    f"    ⏱ 分段计时 (失败): 缓存查 "
                    f"{sig4(_t_cache_done - _t_start)}s → API 段 "
                    f"{sig4(time.time() - _t_cache_done)}s (重试耗尽) | "
                    f"model={embedding_model} n_texts={len(texts):,} "
                    f"n_missing={len(missing_texts):,}"
                )
                return None

    # 写行完备断言 — 旧全局数量断言 (len(missing_embs)==len(missing_texts)) 的
    # 流式等价物: 防漏写/双写/错位 (gate T2/T9 顺带断言其语义)。
    if out is None:
        raise RuntimeError(
            f"嵌入输出矩阵未分配 (内部不变量破): n_texts={len(texts)}, "
            f"n_missing={len(missing_texts)}"
        )
    _n_written = int(_written.sum())
    assert _n_written == len(texts), (
        f"写行完备性异常: written={_n_written} != N={len(texts)} "
        f"(未写行号前 10: {np.flatnonzero(~_written)[:10].tolist()})"
    )
    # ── F18 分段计时落盘 (成功路径) ──
    # 判读: API 段占比高 ⟹ 该段是 API-bound (治法 = 并发/退避/分批, 或播种后就快了);
    #       缓存查段占比高 ⟹ SQLite 点查是瓶颈 (治法 = 批量取代逐条);
    #       两段都小而外层耗时大 ⟹ 时间在**调用方的 CPU** (治法 = 并行化)。
    # 这三条判读正是 2026-07-28 归因 stage 40 时缺失的东西。
    if len(texts) > 1:
        _t_end = time.time()
        _api = (_t_api_done or _t_end) - _t_cache_done
        logger.info(
            f"    ⏱ 分段计时: 缓存查 {sig4(_t_cache_done - _t_start)}s | "
            f"API 段 {sig4(_api)}s ({pct4(_api / max(_t_end - _t_start, 1e-9))}) | "
            f"合计 {sig4(_t_end - _t_start)}s | "
            f"n_texts={len(texts):,} n_missing={len(missing_texts):,} "
            f"model={embedding_model}"
        )
    return out


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
    # F44 (2026-08-01): 钉 BLAS 线程 —— 与 F26 (LDA fit) / F41 (emb cosine) 同一手法,
    # 补的是**池化现场**这个口子。下方那行 `norm = np.linalg.norm(pooled)` (自带
    # `# ← F44 钉的就是这一步` 标记) 对 1-D 走 `x.dot(x)` = MKL `ddot`, 其归约序随线程
    # 数变: 实测 (300 独立样本 × 线程档 [1,1,2,4,8,16,24,32], 含同线程数控制组)
    # **dim=4096 有 84/300 逐位不同** (canonical Qwen 轨正是 4096 维; `_lg` 的 3072 维
    # 在本机 MKL 下 0/300, 但那是阈值巧合不是保证)。
    # 本函数在 `_auth_year_worker` (S5) 与 `_strat_year_worker` (S13) 两个 loky worker
    # 里都被调到, 而 joblib 给 worker 的线程数是 `cpu_count() // n_jobs`, 故这一步的
    # 取值确实**依赖并行度**。
    # ⚠ **但别把收益说过头** (2026-08-01 第二轮终审订正; 我上一版写成"嵌入向量本身会
    #   随并行度漂移、再经 cosine 传播成面板末位差异", 那是**未经证实的推断**):
    #   漂移只有 1–2 个 **float64** ULP (max_rel ≈ 3.0e-16), 而 `emb` 是 **float32**
    #   (`get_embeddings_api` 三条出口全部预分配 float32), 相对间距 1.19e-07 ——
    #   大 4×10⁸ 倍。落到 `.astype(raw_emb.dtype)` 时被完全舍掉: 5,000 条多块文本 ×
    #   4096 维实测 **0 / 20,480,000 个交付值不同**, 单值翻位概率上界 ~2.5e-9。
    #   ⟹ 本条的性质是**防御性钉死** (让这一步与 F26/F41 同协议、与线程数无关),
    #      **不是**修复已观测到的产物漂移。F41 注释里那句"补齐后才真正成立"同此口径。
    # ⚠ 只钉线程、**不改公式**: 换成 `sqrt((pooled*pooled).sum())` 虽也能去掉线程依赖,
    # 但那是**改数** (pairwise 求和 vs ddot), 在钉线程协议下也不等价; 而
    # `threadpool_limits(1)` 在四个 BLAS 环境变量全 =1 时是逐位 no-op ⟹ golden-safe。
    # (仅多块池化分支受影响; `end - start == 1` 的直通分支不含任何归约。)
    # ⚠ `with` 放在循环**外**: 进出 `threadpool_limits` 要遍历并改写**所有已加载**的
    # 线程库, 成本随加载了几个库而变 —— 裸 numpy 环境 (只有 MKL) 实测 523 µs, 而本函数
    # 的真实现场 (stage 40 / loky worker, sklearn 已 import ⟹ 另有两个 OpenMP) 实测
    # **9.9 ms**, 差 19×。放循环内 = 每条多块文本各付一次这个钱; 放外面整段只付一次。
    # (上一版写的 701 µs 是在裸 numpy 环境测的, 2026-08-01 第二轮终审订正。)
    # 覆盖区域是超集 (2-D `norm(block, axis=1)` 本就线程无关), 数值完全相同。
    with _threadpool_limits(limits=1):
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
                [max(1, len(_EMB_ENCODING.encode(str(all_chunks[j]), disallowed_special=())))
                 for j in range(start, end)],
                dtype=np.float64,
            )
            pooled = (unit * w[:, None]).sum(axis=0) / w.sum()
            norm = np.linalg.norm(pooled)               # ← F44 钉的就是这一步 (1-D → MKL ddot)
            emb[i] = (pooled / norm if norm > 0 else pooled).astype(raw_emb.dtype)

    # ── 输出产物 provenance + 单位向量不变量自检 (纯日志, 读已构好的 emb, 绝不复用下游) ──
    # 维度 (dim) 是区分两 co-primary 来源的"指纹": Qwen3-Embedding-8B (canonical 无后缀)
    # = 4096 维, text-embedding-3-large (`_lg`) = 3072 维 → 落 .log 即可从日志反查某面板列
    # 由哪个 co-primary 产出 (此前每条日志均缺该维度信息)。norm 自检验证 banner (Opitz et al.
    # 2025) 所断言的"输出单位向量 → 下游余弦 ≡ 点积"不变量: 单块行直透 API 原始向量
    # (API 返回 norm=1.0), 多块行在上面显式归一 (line 609) → 全体应 ≈ 1.0000; 任何偏离都
    # 提示上游 (policy_alignment/strategic_diff/benefit_society/fintech_intensity 的余弦测度)
    # 结构性依赖被破坏。任何异常被吞 (golden-safe), 不影响返回的 emb。
    try:
        logger.info(
            f"    {log_prefix}: 输出 {n_orig:,} 文本 → 向量矩阵 "
            f"{emb.shape[0]:,}×{emb.shape[1]:,} (dim={emb.shape[1]:,d}, "
            f"model={spec_model(spec)})"
        )
        _norms = np.linalg.norm(emb, axis=1)
        if _norms.size:
            logger.info(
                f"      └─ 单位向量自检 (应 ≈1.0000 → 余弦≡点积): "
                f"mean={sig4(float(_norms.mean()))} · std={sig4(float(_norms.std()))} · "
                f"min={sig4(float(_norms.min()))} · max={sig4(float(_norms.max()))}"
            )
    except Exception as _prov_exc:  # noqa: BLE001 — 输出 provenance/自检诊断, 失败不阻塞
        logger.debug(f"      └─ 输出 provenance/单位向量自检跳过 (不影响产物): {_prov_exc!r}")
    return emb
