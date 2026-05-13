"""
news_process.pipeline.sentiment.tone_llms — 阶段21：统一 LLM 语义精筛与情感分析（双轨版）
==========================================================================================

迁移说明 (Phase 7a-4)：
    本模块由原 root script ``21_tone_llms.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.tone_llms``

功能：
    将早期的 `13_news_llms.py` (真伪精筛) 和 `23_tone_llms.py` (情感分析) 组合，
    使用同一个大模型 Prompt 构建思维链 (Chain-of-Thought)，单次请求获取"真伪"与"情感"。
    采用多模型（如 gpt54nano, gemini31111, deepseekv4）逐条并发请求，并使用多数投票（Majority Vote）
    合成最终共识，满足顶级学术期刊的交叉验证和三角验证标准。
    每条新闻独立请求各模型，通过信号量控制并发。

    【双轨输入】每条新闻同时以全文 (_full) 和上下文片段 (_ctx) 两种输入分别请求模型，
    生成两套完整的验证与情感判定结果，供下游消融研究和三角验证使用。

    【标题轨道】对已通过 full 轨道验证的样本，批量提取标题短文本 LLM 情感，
    供三角验证使用。

方法论依据：
    多模型投票共识机制:
      Wang, X., Wei, J., Schuurmans, D., et al. (2023). Self-consistency
      improves chain of thought reasoning in language models. Proceedings
      of ICLR 2023. DOI: https://doi.org/10.48550/arXiv.2203.11171
    三角验证 (Triangulation):
      Denzin, N. K. (1978/2017). The research act: A theoretical introduction
      to sociological methods. Routledge. DOI: https://doi.org/10.4324/9781315134543
    LLM 金融文本分析可复现性:
      Bybee, L. (2024). The ghost in the machine: Generating beliefs with
      large language models. Journal of Finance, 79(5), 3345-3395.
      DOI: https://doi.org/10.1111/jofi.13366

输入：
    模块二前置输出的 `14_fintech_intensity.parquet`
    (该文件在 12_fintech_news.parquet 基础上追加了 fintech_intensity_score 和 intensity_verified 列)
    (向下兼容: 若跳过阶段14, 自动回退读取 12_fintech_news.parquet)
    
输出：
    筛选后的合法新闻 `21_tone_llms.parquet`
"""

import asyncio
import json
import os
import sys
import time
from collections import Counter

import aiohttp
import pandas as pd

# Phase 7a-4: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/tone_llms.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache
from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging
from news_process.core.reporting import save_dataset
from news_process.core.text.canonicalization import canonicalize_topic
from news_process.core.text.entity_context import extract_entity_context, get_target_aliases

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "21_tone_llms"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# v3 / Fix 3: 把顶层 sys.exit(1) 改为 raise RuntimeError 以消除"严重档"
# 顶层副作用 — sys.exit 会让任何 import 链路 (包括 pytest 测试套件)
# 被进程级 SystemExit 杀掉, 无法在 pytest 单测粒度被报告; raise RuntimeError
# 保持子进程入口的退出码一致 (未捕获异常 → 非零退出码), 但允许 import
# 路径下的调用方 (如 tests/integration/test_papers_imports.py 通过
# importlib.import_module 间接 import 本模块) 在 pytest 中正常 fail
# 而非杀掉整个 session.
#
# 当前事实: 真实环境下 sentiment.yaml 总能提供 tone_llm_processing 节,
# raise 路径从未触发; 但作为防御性反模式仍应消除. 详见 v3 plan A.3 的
# "副作用三档分级" 论证.
def _ensure_llm_config(cfg: dict) -> dict:
    """读取并校验 tone_llm_processing 配置; 缺失或类型异常时 raise.

    recode 加固: 除"缺失"外, 还守住"YAML 把该节写成非 dict 值"
    (如笔误成字符串/列表) — 此场景下下游 ``LLM_CONFIG.get('models', [])``
    会抛 AttributeError, 错误信息不友好且根因不明。本 helper 在源头
    给出明确诊断。
    """
    llm = cfg.get('tone_llm_processing')
    if not llm:
        # 包含 None / {} / [] / "" / 0 等 falsy 情况 — 都视为"未配置"
        raise RuntimeError(
            "在 sentiment.yaml 中未找到 tone_llm_processing 配置节 (或为空); "
            "请检查 config split 是否完整或 legacy config.yaml 是否包含此节。"
        )
    if not isinstance(llm, dict):
        raise RuntimeError(
            f"tone_llm_processing 配置节类型异常: 期望 dict, 实际 "
            f"{type(llm).__name__} ({llm!r:.80s}); "
            f"请检查 sentiment.yaml 该节的 YAML 缩进与值类型。"
        )
    return llm


LLM_CONFIG = _ensure_llm_config(CONFIG)

# 模型列表: 多模型并行请求以支持多数投票(Majority Vote)共识机制
# 推荐至少 3 个模型, 以实现 2/3 多数投票的稳健共识
# 学术依据: Wang et al. (2023, ICLR) — Self-consistency 要求多路径采样后取多数
MODELS = LLM_CONFIG.get('models', [])
MAX_CONCURRENCY = max(1, int(LLM_CONFIG.get('max_concurrency', 10)))
# Prompt 模板: 包含 {title}, {content}, {target_bank}, {co_mentioned_banks} 占位符
PROMPT_TEMPLATE = LLM_CONFIG.get('prompt_template', '')
# Plan-r3 P3-17 接入: 由 core/config.py::_inline_external_prompts 从
# config/prompts/unified_cot.txt 首行 ``# version: <token>`` 自动解析.
# 用于 LLMCache.get/put 的 prompt_version 维度, 防止改 prompt 模板后旧
# cache 静默命中污染分析结果. 默认 "v0" (与 LLMCache 默认值兼容).
PROMPT_VERSION = LLM_CONFIG.get('prompt_template_version', 'v0')
# G-06: 温度参数锁定 — temperature=0 确保确定性推理输出, 保证可复现性
# 学术依据: Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price
#           movements? Return predictability and large language models.
#           SSRN Working Paper No. 4412788.
#           DOI: https://doi.org/10.2139/ssrn.4412788
#           "We use temperature = 0 to ensure deterministic outputs for
#           reproducibility of sentiment labels."
# 同见: Carlson & Burbano (2026, SMJ §3.3, forthcoming):
#       "temperature should be fixed and reported"
TEMPERATURE = LLM_CONFIG.get('temperature', 0.0)
RANDOM_SEED = LLM_CONFIG.get('random_seed', 42)
FORCE_JSON = LLM_CONFIG.get('force_json', True)

# 显式记录 LLM 推理参数 (G-06: 审稿人可追溯的参数报告)
logger.info(f"LLM 推理参数: temperature={TEMPERATURE}, seed={RANDOM_SEED}, "
            f"force_json={FORCE_JSON}, models={len(MODELS)}, "
            f"concurrency={MAX_CONCURRENCY}")

MAX_RETRIES = LLM_CONFIG.get('max_retries', 5)
RETRY_DELAY = LLM_CONFIG.get('retry_delay', 10)
# v6/N4: 指数退避 — 单 yunwu 账户避免雪崩
RETRY_BACKOFF = LLM_CONFIG.get('retry_backoff', 'linear')  # 'exponential' or 'linear'
RETRY_BACKOFF_CAP = LLM_CONFIG.get('retry_backoff_cap', 600)
REQUEST_TIMEOUT_TOTAL = float(LLM_CONFIG.get('timeout', 600))
REQUEST_TIMEOUT_CONNECT = float(LLM_CONFIG.get('connect_timeout', min(120, REQUEST_TIMEOUT_TOTAL)))
REQUEST_TIMEOUT_SOCK_CONNECT = float(LLM_CONFIG.get('sock_connect_timeout', REQUEST_TIMEOUT_CONNECT))
REQUEST_TIMEOUT_SOCK_READ = float(LLM_CONFIG.get('sock_read_timeout', REQUEST_TIMEOUT_TOTAL))
CONNECTOR_TTL_DNS_CACHE = int(LLM_CONFIG.get('ttl_dns_cache', 300))
CONNECTOR_KEEPALIVE = float(LLM_CONFIG.get('keepalive_timeout', 60))
AUTH_PROBE_TIMEOUT = float(LLM_CONFIG.get('auth_probe_timeout', min(30, REQUEST_TIMEOUT_TOTAL)))


def _compute_retry_sleep(attempt: int) -> float:
    """v6/N4: 计算第 attempt 次重试的 sleep 秒数。

    指数退避: delay = min(RETRY_DELAY * 2**attempt, RETRY_BACKOFF_CAP)
    线性回退到原行为: delay = RETRY_DELAY
    """
    if RETRY_BACKOFF == 'exponential':
        return min(RETRY_DELAY * (2 ** attempt), RETRY_BACKOFF_CAP)
    return RETRY_DELAY


def build_llm_timeout() -> aiohttp.ClientTimeout:
    """Create a conservative timeout profile for high-volume validation calls."""
    return aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT_TOTAL,
        connect=REQUEST_TIMEOUT_CONNECT,
        sock_connect=REQUEST_TIMEOUT_SOCK_CONNECT,
        sock_read=REQUEST_TIMEOUT_SOCK_READ,
    )


def build_llm_connector(limit: int) -> aiohttp.TCPConnector:
    """Build the shared LLM connector with an explicit per-host cap."""
    safe_limit = max(1, int(limit))
    return aiohttp.TCPConnector(
        limit=safe_limit,
        limit_per_host=safe_limit,
        ttl_dns_cache=CONNECTOR_TTL_DNS_CACHE,
        keepalive_timeout=CONNECTOR_KEEPALIVE,
        enable_cleanup_closed=True,
    )


class AsyncRequestPacer:
    """Serialize request starts so large validation batches do not burst."""

    def __init__(self, spacing_seconds: float = 0.0):
        self.spacing_seconds = max(0.0, float(spacing_seconds or 0.0))
        self._lock = asyncio.Lock()
        self._last_started_at = 0.0

    async def wait(self) -> None:
        if self.spacing_seconds <= 0:
            return
        async with self._lock:
            now = time.monotonic()
            sleep_s = self._last_started_at + self.spacing_seconds - now
            if sleep_s > 0:
                await asyncio.sleep(sleep_s)
            self._last_started_at = time.monotonic()


def build_model_pacers(models: list, spacing_seconds: float = 0.0) -> dict:
    """Build one request-start pacer per model."""
    spacing = max(0.0, float(spacing_seconds or 0.0))
    return {m['model_name']: AsyncRequestPacer(spacing) for m in models} if spacing > 0 else {}


class AsyncModelAvailability:
    """Per-run circuit breaker for permanent model failures."""

    def __init__(self):
        self._disabled: dict[str, str] = {}
        self._preflighted: set[str] = set()
        self._lock = asyncio.Lock()

    def is_disabled(self, model_id: str) -> bool:
        return model_id in self._disabled

    def is_preflighted(self, model_id: str) -> bool:
        return model_id in self._preflighted

    async def disable(self, model_id: str, reason: str) -> None:
        async with self._lock:
            if model_id in self._disabled:
                return
            self._disabled[model_id] = reason
            logger.info(
                f"[{model_id}] 模型本轮停用: {reason}; "
                "后续缺缓存请求将跳过，已缓存响应仍会复用"
            )

    async def mark_preflighted(self, model_id: str) -> None:
        async with self._lock:
            self._preflighted.add(model_id)

    async def note_transient_failure(self, model_id: str, reason: str, row_idx: int) -> None:
        """Record a one-off transport/server failure without disabling the model."""
        logger.info(f"[{model_id}] 行 {row_idx}: {reason}，该次结果将从投票中排除")


AUTH_FAILURE_STATUSES = {401, 403}


def _summarize_auth_failure(status: int, resp_text: str) -> str:
    """Return a compact, secret-free authorization failure summary."""
    message = ""
    try:
        payload = json.loads(resp_text or "{}")
        err = payload.get("error", payload)
        if isinstance(err, dict):
            message = str(err.get("message") or err.get("type") or "").strip()
    except (json.JSONDecodeError, TypeError):
        message = str(resp_text or "").strip()
    if "(request id:" in message:
        message = message.split("(request id:", 1)[0].strip()
    if len(message) > 120:
        message = message[:117] + "..."
    return f"状态码 {status} 授权失败" + (f" ({message})" if message else "")


def _build_llm_request(model_id: str, api_key: str, prompt: str) -> tuple[dict, dict]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "seed": RANDOM_SEED,
    }
    if FORCE_JSON:
        payload["response_format"] = {"type": "json_object"}
    return headers, payload


async def preflight_model_availability(
    session: aiohttp.ClientSession,
    models: list,
    model_availability: AsyncModelAvailability,
) -> None:
    """Probe model authorization once before a high-volume batch starts."""
    probe_timeout = aiohttp.ClientTimeout(
        total=AUTH_PROBE_TIMEOUT,
        connect=min(AUTH_PROBE_TIMEOUT, REQUEST_TIMEOUT_CONNECT),
        sock_connect=min(AUTH_PROBE_TIMEOUT, REQUEST_TIMEOUT_SOCK_CONNECT),
        sock_read=AUTH_PROBE_TIMEOUT,
    )
    prompt = '请只返回 JSON: {"ok": true}'

    for m in models:
        model_id = m['model_name']
        if model_availability.is_disabled(model_id) or model_availability.is_preflighted(model_id):
            continue
        base_url = m.get('base_url', '')
        api_key = m.get('api_key', '')
        if not base_url or not api_key:
            await model_availability.disable(model_id, "base_url 或 api_key 为空")
            continue
        headers, payload = _build_llm_request(model_id, api_key, prompt)
        try:
            async with session.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=probe_timeout,
            ) as resp:
                if resp.status == 200:
                    await model_availability.mark_preflighted(model_id)
                    continue
                resp_text = await resp.text()
                if resp.status in AUTH_FAILURE_STATUSES:
                    await model_availability.disable(
                        model_id, _summarize_auth_failure(resp.status, resp_text)
                    )
                else:
                    await model_availability.mark_preflighted(model_id)
                    logger.info(
                        f"[{model_id}] 模型预检返回状态码 {resp.status}; "
                        "保留正式请求路径以复用重试策略"
                    )
        except asyncio.TimeoutError:
            await model_availability.mark_preflighted(model_id)
            logger.info(f"[{model_id}] 模型预检等待超过时限，保留正式请求路径")
        except Exception:
            await model_availability.mark_preflighted(model_id)
            logger.info(f"[{model_id}] 模型预检暂不可达，保留正式请求路径")


def _log_retryable_transport_issue(
    model_id: str,
    attempt: int,
    sleep_s: float,
    max_attempts: int = MAX_RETRIES,
) -> None:
    logger.debug(
        f"[{model_id}] 连接暂不可用 "
        f"(attempt {attempt + 1}/{max_attempts}) - 等待 {sleep_s:.1f}s 后重试..."
    )

# ── Logit-to-Score 概率映射法（稳健性检验指标）──────────────────────────
# 将 LLM 三分类标签 + sentiment_confidence 转化为 [-1, +1] 连续分数。
# 学术依据:
#   Törnberg, P. (2024). arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
#   Shapiro, A.H. et al. (2022). JoE, 228(2). DOI: 10.1016/j.jeconom.2020.07.053
LOGIT_SCORE_CFG = LLM_CONFIG.get('logit_to_score', {})
LOGIT_SCORE_ENABLED = LOGIT_SCORE_CFG.get('enabled', False)
logger.info(f"Logit-to-Score 概率映射: enabled={LOGIT_SCORE_ENABLED}")


# ============================================================================
# 2. 异步请求大模型 API
# ============================================================================

async def fetch_llm_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                          prompt: str, model_cfg: dict, row_idx: int, track: str,
                          cache: LLMCache = None,
                          request_pacer: AsyncRequestPacer | None = None,
                          model_availability: AsyncModelAvailability | None = None,
                          request_timeout: aiohttp.ClientTimeout | None = None,
                          max_retries: int | None = None,
                          prompt_version: str = "v0") -> tuple:
    """异步请求单个模型的单篇文章，自带重试保护和缓存。

    model_cfg 结构示例：
        {model_name: ..., short_name: ..., base_url: ..., api_key: ...}
    每个模型可独立指定 base_url 和 api_key。

    Args:
        track: 'full'、'ctx' 或 'title'，标识本次请求使用的文本轨道。
        cache: LLMCache 实例，用于查询/写入缓存。
        prompt_version: prompt 模板版本字符串 (例如 ``"v6-2026-05-13"``),
            传给 ``LLMCache.get/put`` 用作缓存键命名空间。caller 根据
            track 选择对应模板的版本号 (full/ctx → PROMPT_VERSION,
            title → TITLE_PROMPT_VERSION)。

    Returns:
        tuple: (row_idx, model_id, result_text, track)
    """
    model_id = model_cfg['model_name']
    base_url = model_cfg.get('base_url', '')
    api_key  = model_cfg.get('api_key', '')

    # 缓存查询（sqlite3 同步调用为微秒级，不阻塞事件循环）
    if cache is not None:
        cached_response = cache.get(model_id, prompt, prompt_version=prompt_version)
        if cached_response is not None:
            return row_idx, model_id, cached_response, track

    if model_availability is not None and model_availability.is_disabled(model_id):
        return row_idx, model_id, None, track

    # 准备请求
    headers, payload = _build_llm_request(model_id, api_key, prompt)

    req_timeout = request_timeout or build_llm_timeout()
    max_attempts = MAX_RETRIES if max_retries is None else max(1, int(max_retries))

    last_failure_reason = f"连续 {max_attempts} 次请求未成功"

    async with semaphore:
        for attempt in range(max_attempts):
            if model_availability is not None and model_availability.is_disabled(model_id):
                return row_idx, model_id, None, track

            sleep_s = _compute_retry_sleep(attempt)
            has_more_attempts = attempt < max_attempts - 1
            try:
                if request_pacer is not None:
                    await request_pacer.wait()
                async with session.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=req_timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result_text = data['choices'][0]['message']['content']
                        if cache is not None:
                            cache.put(model_id, prompt, result_text,
                                      prompt_version=prompt_version)
                        return row_idx, model_id, result_text, track
                    elif resp.status in (429, 500, 502, 503, 504):
                        last_failure_reason = f"连续 {max_attempts} 次请求未成功，最后状态码 {resp.status}"
                        if has_more_attempts:
                            logger.debug(
                                f"[{model_id}] API 状态码 {resp.status} "
                                f"(attempt {attempt+1}/{max_attempts}) - 等待 {sleep_s:.1f}s 后重试..."
                            )
                            await asyncio.sleep(sleep_s)
                    else:
                        resp_text = await resp.text()
                        if resp.status in AUTH_FAILURE_STATUSES:
                            reason = _summarize_auth_failure(resp.status, resp_text)
                            if model_availability is not None:
                                await model_availability.disable(model_id, reason)
                            else:
                                logger.info(
                                    f"[{model_id}] 模型本轮停用: {reason}; "
                                    "后续缺缓存请求将跳过，已缓存响应仍会复用"
                                )
                            return row_idx, model_id, None, track
                        logger.error(f"[{model_id}] API 错误 {resp.status}: {resp_text}")
                        break
            except asyncio.TimeoutError:
                last_failure_reason = f"连续 {max_attempts} 次请求等待超过时限"
                if has_more_attempts:
                    logger.debug(
                        f"[{model_id}] 请求等待超过时限 "
                        f"(attempt {attempt+1}/{max_attempts}) - 等待 {sleep_s:.1f}s 后重试..."
                    )
                    await asyncio.sleep(sleep_s)
            except Exception:
                last_failure_reason = f"连续 {max_attempts} 次连接暂不可用"
                if has_more_attempts:
                    _log_retryable_transport_issue(model_id, attempt, sleep_s, max_attempts)
                    await asyncio.sleep(sleep_s)

    # 所有重试均失败，返回 None 标记（区别于空 JSON，避免影响多数投票）。
    # 5xx/429/网络抖动通常是瞬时问题，不能因此停用整轮模型；否则大样本验证会
    # 因单次故障跳过后续缺缓存请求，扭曲稳健性指标。
    if model_availability is not None:
        await model_availability.note_transient_failure(model_id, last_failure_reason, row_idx)
    else:
        logger.info(f"[{model_id}] 行 {row_idx}: {last_failure_reason}，该模型结果将从投票中排除")
    return row_idx, model_id, None, track

async def run_all_llms(df: pd.DataFrame, models: list, cache: LLMCache = None) -> dict:
    """逐条并发执行 DataFrame 中所有行对所有配置模型的双轨请求。
    
    为每行 × 每模型 × 每轨道 生成独立 prompt，通过信号量控制并发数。
    要求 df 中已包含 'content_ctx' 列（由 main() 预计算并物化）。
    
    Returns:
        dict: {row_idx: {'full': {model_id: res_text}, 'ctx': {model_id: res_text}}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {'full': {}, 'ctx': {}} for i in df.index}
    
    total_tasks = len(df) * len(models) * 2  # ×2 因为双轨
    logger.info(f"逐条请求: {len(df)} 条新闻 × {len(models)} 模型 × 2 轨道 = {total_tasks} 个请求")
    
    # 连接池优化：复用 TCP 连接 + keepalive，减少握手和 TLS 协商开销
    connector = build_llm_connector(MAX_CONCURRENCY)
    request_pacers = build_model_pacers(models, LLM_CONFIG.get('request_spacing_seconds', 0.0))
    model_availability = AsyncModelAvailability()
    async with aiohttp.ClientSession(connector=connector, timeout=build_llm_timeout()) as session:
        await preflight_model_availability(session, models, model_availability)
        # 构建任务列表：每行 x 每轨道 x 每模型
        real_tasks = []
        for idx, row in df.iterrows():
            content_full = str(row.get('内容', ''))
            content_ctx = str(row.get('content_ctx', content_full))
            target_bank = str(row.get('target_bank', ''))
            
            for track, content in [('full', content_full), ('ctx', content_ctx)]:
                prompt = PROMPT_TEMPLATE.format(
                    title=str(row.get('标题', '')),
                    content=content,
                    target_bank=target_bank,
                    co_mentioned_banks=str(row.get('co_mentioned_banks', '无')),
                )
                for m in models:
                    real_tasks.append(
                        fetch_llm_async(
                            session, semaphore, prompt, m, idx, track, cache=cache,
                            request_pacer=request_pacers.get(m['model_name']),
                            model_availability=model_availability,
                            prompt_version=PROMPT_VERSION,
                        )
                    )
        
        completed = 0
        total = len(real_tasks)
        report_interval = max(1, total // 20)  # 每 5% 汇报一次
        next_report = report_interval
        logger.info(f"📡 LLM 双轨逐条请求开始: 共 {total} 个请求")
        
        for coro in asyncio.as_completed(real_tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total * 100
                logger.info(f"📡 LLM 请求进度: {completed}/{total} ({pct:.1f}%)")
                next_report += report_interval
        
        logger.info(f"📡 LLM 双轨逐条请求完成: 共 {total} 个请求全部处理完毕")
    
    return results_map


# ============================================================================
# 3. 结果提取与多数投票聚合
# ============================================================================

def parse_json_response(res_text: str) -> dict:
    """尝试从大模型结果中解析 JSON。

    容错策略:
    1. 自动去除 markdown 代码块包围(```json ... ```),
       因为部分模型(如 GPT 系列)倾向于在 JSON 响应外添加代码块标记。
    2. 若解析结果是 list (DeepSeek Grok 偶尔返回 [{...}] 数组包裹形式),
       且首元素为 dict, 则解包返回首元素。
    3. 任何其他非 dict 解析结果统一返回 {}, 由上层视为"模型缺席"通道。
    """
    try:
        # 去除 markdown json 代码块包围
        text = res_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            return result[0]
        return {}
    except Exception:
        return {}

def majority_vote_bool(bools: list) -> bool:
    """严格多数决判断真伪（超过半数才通过）。
    
    采用严格多数（strict majority, >50%）而非简单多数（plurality）：
    投票数必须**严格超过**总票数的一半才判定为通过。
    例如 2 票中 1 票为 True → 不通过（1 不超过 2/2=1.0）。
    
    学术依据:
      Wang, X., et al. (2023). Self-consistency improves chain of thought
      reasoning in language models. ICLR 2023.
      DOI: https://doi.org/10.48550/arXiv.2203.11171
      该文提出多路径采样后取多数投票作为最终答案的共识机制。
    """
    if not bools: return False
    return sum(bools) > (len(bools) / 2.0)

def majority_vote_sentiment(sents: list, tie_strategy: str = 'undefined'):
    """多数决判断情感（v6/F2: 平局策略可配置）。

    v6 改动 (F2 修复)：
    ----------------
    历史行为：平局 → 强制返回 "中性"，与"全员中性"在数据上不可区分，
              且与上层 verified=False → forced "中性" 共同污染 is_neutral 列。
              诊断显示 81.7%(_full) / 84.1%(_ctx) 的中性标签源自污染，
              而非真实中性新闻。
    新行为：默认平局返回 None，交由上层标记为 llm_undefined=1，与真实
            中性严格区分；保留 'neutral' 作 robustness 备选。

    Args:
        sents: list of "正面"/"中性"/"负面" labels
        tie_strategy: 'undefined' (返回 None) / 'neutral' (历史行为，返回"中性")

    Returns:
        str | None: 多数决结果；None 表示空票或平局-undefined 策略
    """
    if not sents:
        return None
    c = Counter(sents)
    most_common = c.most_common()
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        if tie_strategy == 'neutral':
            return "中性"
        return None
    return most_common[0][0]


def compute_prob_score(sentiment_label: str, confidence: float) -> dict:
    """基于情感标签和置信度计算概率映射连续分数 [-1, +1]。

    【白话解释】
      把大模型输出的"正面/中性/负面"标签 + 它自己报的置信度数字，
      转换成一个 -1 到 +1 之间的连续分数。分数越接近 +1 表示越正面，
      越接近 -1 表示越负面，0 表示中性。

    【学术依据】
      概率映射法 (Logit-to-Score):
        Törnberg, P. (2024). How to use large language models for text analysis.
        arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
        → 利用 LLM 分类输出构建连续分析指标的方法论框架

      连续情感度量在金融计量中的必要性:
        Shapiro, A.H., Sudhof, M. & Wilson, D.J. (2022). Measuring news
        sentiment. Journal of Econometrics, 228(2), 221-243.
        DOI: 10.1016/j.jeconom.2020.07.053

      剩余概率均分 (1-c)/2 的理论基础 — 最大熵原理:
        Jaynes, E.T. (1957). Information theory and statistical mechanics.
        Physical Review, 106(4), 620-630. DOI: 10.1103/PhysRev.106.620
        → 在已知主类概率 c 的约束下，最大化 Shannon 熵的
          唯一解为其余类均匀分布: P(其余) = (1-c)/2

    【局限性声明】
      sentiment_confidence 是 LLM 生成的文本数值（verbalized confidence），
      非内部 softmax 概率。它作为分类确信度的**序数代理变量**使用，
      不可直接解释为校准后的概率。

      已知局限 — 系统性过度自信:
        Xiong, M. et al. (2024). Can LLMs express their uncertainty?
        ICLR 2024. DOI: 10.48550/arXiv.2306.13063
        → LLM verbalized confidence 倾向过度自信，但保序性基本成立，
          即 conf(A) > conf(B) 时 acc(A) > acc(B)，
          因此作为序数代理变量（ordinal proxy）在排序层面可靠。

      LLM 文本标注能力的基准验证:
        Gilardi, F. et al. (2023). PNAS, 120(30), e2305016120.
        DOI: 10.1073/pnas.2305016120

    【概率模拟策略】
      P2 路径 (confidence > 0):
        主类概率 = c, 其余两类概率 = (1-c)/2
        公式: Score = P(正面) - P(负面)
      P3 路径 (confidence ≤ 0 或无效):
        one-hot: 主类=1.0, 其余=0.0
        Score ∈ {+1.0, 0.0, -1.0}

    【数学性质】（已数学证明，P2 路径 c ∈ (0, 1]）
      - label="中性" → Score ≡ 0（∀ c，因 P_pos = P_neg = (1-c)/2）
      - label="正面" → Score = (3c-1)/2 ∈ (-0.5, 1.0]
        当 c > 1/3 时 Score > 0（符合直觉）
        当 c = 1/3 时 Score = 0（三类等概率，信号消失）
        当 c < 1/3 时 Score < 0（模型不确定性压倒分类标签）
        实践中 LLM confidence 通常 ∈ [0.6, 0.95]，Score 始终 > 0
      - label="负面" → Score = (1-3c)/2 ∈ [-1.0, 0.5)
        对称于"正面"，c > 1/3 时 Score < 0
      - Σ(P_pos + P_neu + P_neg) = 1（概率公理）

    Args:
        sentiment_label: "正面" / "中性" / "负面"
        confidence: LLM 自报 sentiment_confidence ∈ [0, 1]

    Returns:
        dict: prob_pos, prob_neu, prob_neg (各∈[0,1], Σ=1),
              prob_score ∈ [-1, +1],
              prob_source: "P2" 或 "P3"
    """
    LABEL_MAP = {"正面": "positive", "中性": "neutral", "负面": "negative"}
    cls = LABEL_MAP.get(sentiment_label, "neutral")

    c = max(0.0, min(1.0, confidence)) if confidence else 0.0
    if c > 0:
        probs = {k: (1.0 - c) / 2.0 for k in ["positive", "neutral", "negative"]}
        probs[cls] = c
        source = "P2"
    else:
        probs = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        probs[cls] = 1.0
        source = "P3"

    score = probs["positive"] - probs["negative"]

    return {
        "prob_pos": probs["positive"],
        "prob_neu": probs["neutral"],
        "prob_neg": probs["negative"],
        "prob_score": round(score, 6),
        "prob_source": source,
    }


def _aggregate_track(model_res_dict: dict, models: list) -> tuple:
    """对某一轨道的模型响应进行解析和多数投票聚合。

    v6/F2 改动 (篇章级编码契约重写)
    ----------------------------------
    1. **解除 verification 与 sentiment 的耦合**：单模型 verified=False 不再
       强制改写其 sentiment 为 "中性"。每个模型独立保留自己的 sentiment 判定。
    2. **聚合 sentiment 投票仅纳入"通过 verification 的模型"**：避免拒绝该
       新闻为金融科技的模型对情感投票产生噪声贡献。
    3. **平局 → undefined**：majority_vote_sentiment 默认返回 None，上层
       标记 llm_undefined=1；下游 panel 层把 None 映射为 NaN 而非"中性"。
    4. **新增 4 个状态指标**：n_valid_votes / n_verifying_votes /
       call_failure / undefined，用于下游精细化掩码。
    5. **agree_rate 拆分**：agree_rate_v (验证投票一致率) /
       agree_rate_s (情感投票一致率，仅在 verifying 子集上计算)。

    Returns:
        tuple: (final_v, final_s, agree_rate_v, agree_rate_s,
                n_valid_votes, n_verifying_votes,
                call_failure, undefined,
                per_model_parsed, topics, llm_categories, text_types,
                n_failures, avg_prob_score)
            per_model_parsed: {f'{short}_verified': v, ...} 的字典
            avg_prob_score: Logit-to-Score 多模型平均概率分数 ∈ [-1, +1]
    """
    v_votes = []
    s_votes_all = []           # 所有成功调用模型的 sentiment（含 verified=False 模型）
    s_votes_verified_only = [] # 仅含 verified=True 模型的 sentiment（v6/F2 新逻辑）
    topics = []
    llm_categories = []
    text_types = []
    per_model_parsed = {}
    n_failures = 0
    n_models = len(models)

    for m in models:
        short = m['short_name']
        m_id = m['model_name']
        raw_text = model_res_dict.get(m_id)

        if raw_text is None:
            n_failures += 1
            per_model_parsed[f"{short}_verified"] = None
            per_model_parsed[f"{short}_sentiment"] = None
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0
            continue

        jd = parse_json_response(raw_text)
        # 双重保险：parse_json_response 已统一返回 dict，但仍防御 LLM 异常输出
        if not isinstance(jd, dict):
            jd = {}

        v = jd.get('is_bank_fintech_news', False)
        if isinstance(v, str):
            v = v.strip().lower() in ('true', '1', 'yes')
        v = bool(v)

        s_raw = jd.get('sentiment')
        if isinstance(s_raw, str):
            s = s_raw.strip()
            if s not in ('正面', '中性', '负面'):
                s = None
        else:
            s = None

        v_votes.append(v)

        if s is not None:
            s_votes_all.append(s)
            if v:
                s_votes_verified_only.append(s)

        per_model_parsed[f"{short}_verified"] = v
        per_model_parsed[f"{short}_sentiment"] = s
        try:
            per_model_parsed[f"{short}_verification_confidence"] = float(jd.get('verification_confidence', 0.0) or 0.0)
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
        try:
            per_model_parsed[f"{short}_sentiment_confidence"] = float(jd.get('sentiment_confidence', 0.0) or 0.0)
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0

        topic = jd.get('fintech_topic')
        if topic and str(topic).strip().lower() not in ('null', 'none', ''):
            topics.append(str(topic))
        llm_cat = jd.get('fintech_category')
        if llm_cat:
            cat_str = str(llm_cat).strip().replace('；', ';')
            for part in cat_str.split(';'):
                part = part.strip()
                if part in ('底层技术', '应用场景'):
                    llm_categories.append(part)
                    break
        llm_tt = jd.get('text_type')
        if llm_tt:
            tt_str = str(llm_tt).strip()
            if tt_str in ('实质性', '描述性'):
                text_types.append(tt_str)

    final_v = majority_vote_bool(v_votes)

    # v6/F2: 仅在通过 verification 的模型子集上计算情感多数票。
    if final_v:
        final_s = majority_vote_sentiment(s_votes_verified_only, tie_strategy='undefined')
    else:
        # 整篇被多数判为非金融科技 → 情感无意义；标记为 undefined（None）。
        final_s = None

    n_valid_votes = len(v_votes)
    n_verifying_votes = sum(1 for v in v_votes if v == final_v) if final_v else 0
    agree_v_count = sum(1 for x in v_votes if x == final_v)
    agree_rate_v = agree_v_count / n_valid_votes if n_valid_votes > 0 else 0.0
    if s_votes_verified_only and final_s is not None:
        agree_rate_s = sum(1 for x in s_votes_verified_only if x == final_s) / len(s_votes_verified_only)
    else:
        agree_rate_s = float('nan')

    call_failure = 1 if n_valid_votes == 0 else 0
    undefined = 1 if (final_v and final_s is None) else 0

    prob_scores = []
    for m in models:
        short = m['short_name']
        s_label = per_model_parsed.get(f"{short}_sentiment")
        s_conf = per_model_parsed.get(f"{short}_sentiment_confidence", 0.0)
        if s_label is not None:
            ps_result = compute_prob_score(s_label, s_conf)
            per_model_parsed[f"{short}_prob_score"] = ps_result['prob_score']
            per_model_parsed[f"{short}_prob_source"] = ps_result['prob_source']
            prob_scores.append(ps_result['prob_score'])
    avg_prob_score = sum(prob_scores) / len(prob_scores) if prob_scores else float('nan')

    return (
        final_v, final_s,
        agree_rate_v, agree_rate_s,
        n_valid_votes, n_verifying_votes,
        call_failure, undefined,
        per_model_parsed, topics, llm_categories, text_types,
        n_failures, avg_prob_score,
    )


def _materialize_content_ctx(df: pd.DataFrame) -> pd.DataFrame:
    """预计算并物化 content_ctx 列，供双轨分析和下游阶段复用。

    对每个 (文章, 目标银行) 对调用 extract_entity_context() 提取
    实体特异性上下文片段，结果存入 'content_ctx' 列。下游阶段
    22_tone_words 和 23_tone_berts 直接读取此列，避免重复计算
    并确保三种情感分析方法对完全一致的文本进行分析。

    窗口参数从 config.yaml 的 context_window 节读取，确保参数
    可追溯性和审计透明度：
      - sentence_radius: 句子级窗口半径（默认 1 = 命中句前后各1句）
      - fallback_char_radius: 文本过短时的字符级回退半径

    学术依据:
      Hassan et al. (2019, QJE) Proximity-based Attribution。
      敏感性检验: 35_radius_sensitivity.py 验证 radius ∈ {0,1,2,3} 的稳健性。

    Args:
        df: 含 '内容' 和 'target_bank' 列的 DataFrame。

    Returns:
        pd.DataFrame: 增加了 'content_ctx' 列的 DataFrame。
    """
    # 从 config.yaml 读取窗口参数（显式参数化，取代函数默认值）
    _ctx_cfg = CONFIG.get('context_window', {})
    _sentence_radius = _ctx_cfg.get('sentence_radius', 1)
    _fallback_char_radius = _ctx_cfg.get('fallback_char_radius', 150)

    logger.info(f"物化 content_ctx 列（实体特异性上下文提取）"
                f"— sentence_radius={_sentence_radius}, "
                f"fallback_char_radius={_fallback_char_radius}")
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache = {}

    ctx_list = []
    for _, row in df.iterrows():
        content_full = str(row.get('内容', ''))
        target_bank = str(row.get('target_bank', ''))

        # 防御性检查：当 target_bank 为 NaN 时 str() 会产出 'nan'，
        # 需将其视为空值以避免冗余的别名查找和文件读取
        if target_bank and target_bank not in ('nan', 'None'):
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(target_bank, _bnf)
            content_ctx = extract_entity_context(
                content_full, _alias_cache[target_bank],
                sentence_radius=_sentence_radius,
                fallback_char_radius=_fallback_char_radius,
            )
            if not content_ctx:
                content_ctx = content_full  # 回退公理：无匹配时保留全文
        else:
            content_ctx = content_full  # 无目标银行时回退至全文

        ctx_list.append(content_ctx)

    df['content_ctx'] = ctx_list
    n_fallback = sum(1 for ctx, full in zip(ctx_list, df['内容'].astype(str)) if ctx == full)
    # 统计逻辑与 L404 的 NaN 防御保持一致：排除 'nan'/'None'/空字符串
    _bank_strs = df['target_bank'].astype(str).str.strip()
    n_with_bank = ((_bank_strs != '') & (_bank_strs != 'nan') & (_bank_strs != 'None')).sum()
    logger.info(f"  content_ctx 列物化完成: {len(df)} 行, "
                f"回退至全文: {n_fallback}/{n_with_bank} 条"
                f"（{n_fallback/max(n_with_bank,1)*100:.1f}%）")
    return df


def _write_run_lineage(stage_start: float):
    """v6/N8: 写入本次 stage 21 运行的 LLM 配置 lineage 清单。

    解决"换模型不留痕"问题：每次重跑生成 21_tone_llms_lineage_<timestamp>.json，
    持久化记录 (slot, model_name, base_url, run_start_ts) 三元组。
    """
    lineage = {
        "stage": STAGE_NAME,
        "run_start_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stage_start)),
        "run_start_ts": stage_start,
        "models": [
            {
                "short_name": m.get("short_name"),
                "model_name": m.get("model_name"),
                "description": m.get("description"),
                "base_url": m.get("base_url"),
            }
            for m in MODELS
        ],
        "concurrency": MAX_CONCURRENCY,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "retry_backoff": RETRY_BACKOFF,
        "retry_backoff_cap": RETRY_BACKOFF_CAP,
        "temperature": TEMPERATURE,
        "random_seed": RANDOM_SEED,
        "force_json": FORCE_JSON,
        "logit_to_score_enabled": LOGIT_SCORE_ENABLED,
    }
    out_dir = CONFIG["paths"]["output_dir"]
    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime(stage_start))
    out_path = os.path.join(out_dir, f"21_tone_llms_lineage_{ts}.json")
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(lineage, f, ensure_ascii=False, indent=2)
        logger.info(f"  [N8 lineage] 已写入: {out_path}")
    except Exception as e:
        logger.warning(f"  [N8 lineage] 写入失败 (非阻塞): {e}")


def main():
    """Stage 21 LLM 三模型 ensemble 情感分析主入口.

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, 505 行 god function)

        本函数是 stage 21 的双轨 (full + ctx) LLM 调用主流程, 内部职责:
        1. 加载 stage 12/14 上游 + schema 守护 (含 ``stage 14 fallback to 12``
           硬化反模式根除, 见 line 727-732 的 "Step 4(a) 硬化")
        2. 双轨数据准备 + content/ctx 物化
        3. 三家族 LLM (gpt54nano / gemini31111 / deepseekv4) 并发请求 +
           majority-vote ensemble (logit-to-score)
        4. SQLite 缓存读写 (P3-17 拟升级缓存键含 prompt_version)
        5. N8 lineage 记录 + parquet 双轨输出

        v3.0 拆分应让 LLM 调用层独立可测 (mock yunwu API), 与上下游
        IO 解耦.
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} (双轨模式) ---")
    _write_run_lineage(stage_start)

    # Step 4(a) 硬化 (致命问题 5 / 红队 v6 修订): 删除"14 不存在则回退 12"的
    # 静默 fallback。Stage 14 输出 fintech_intensity_score / intensity_verified
    # 是 LLM 双轨语义筛选的关键信号; fallback 到 12 会让 LLM 失去 TF-IDF 强度
    # 锚点, 静默降级为旧版"无强度筛选"模式, 与 v6 三家族 LLM 设计假设矛盾。
    # 若 stage 14 真的缺失, 必须通过 raise 让 orchestrator 立即停止并修复上游,
    # 而非继续生产含有"未见过的隐性降级"标签的 21_tone_llms.parquet。
    input_14 = CONFIG['filenames'].get('output_14_fintech_intensity', '14_fintech_intensity.parquet')
    path_14 = os.path.join(CONFIG["paths"]["output_dir"], input_14)

    if not os.path.exists(path_14):
        raise RuntimeError(
            f"[stage 21] 上游输入缺失: {path_14} 不存在。"
            f" Stage 21 (LLM 双轨情感分析) 硬依赖 stage 14 输出的 "
            f"fintech_intensity_score 列。请先运行 "
            f"`python -m news_process.pipeline.filtering.fintech_intensity` "
            f"产出 {input_14} 后再重试。"
        )
    input_path = path_14
    logger.info(f"使用阶段14输出: {input_14}")
        
    logger.info(f"加载预筛数据: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"总计候选新闻: {len(df)}")
    log_memory_usage(logger, "数据加载完成")
    
    # 物化 content_ctx 列（供 LLM 双轨请求 + 下游阶段 22/23 直接复用）
    df = _materialize_content_ctx(df)
    
    if not LLM_CONFIG.get('enabled', False):
        logger.info("统一 LLM 处理已在 config.yaml 中禁用。将透传输入数据并填入默认值。")

        # 添加空的 LLM 双轨列，确保下游阶段不因缺列报错
        df['llm_verified_full'] = True
        df['llm_verified_ctx'] = True
        df['llm_sentiment_full'] = '中性'
        df['llm_sentiment_ctx'] = '中性'
        df['llm_agreement_rate_full'] = 0.0
        df['llm_agreement_rate_ctx'] = 0.0
        # v6/F2 新增掩码列（禁用分支默认值）
        df['llm_agreement_rate_s_full'] = float('nan')
        df['llm_agreement_rate_s_ctx'] = float('nan')
        df['n_valid_votes_full'] = 0
        df['n_valid_votes_ctx'] = 0
        df['n_verifying_votes_full'] = 0
        df['n_verifying_votes_ctx'] = 0
        df['llm_call_failure_full'] = 0
        df['llm_call_failure_ctx'] = 0
        df['llm_undefined_full'] = 0
        df['llm_undefined_ctx'] = 0
        df['fintech_category'] = '应用场景'
        df['category_confidence'] = 0.0
        df['text_type'] = None
        # 标题轨道虚拟列补全（与启用分支输出对齐）
        df['llm_verified_title'] = True
        df['llm_sentiment_title'] = '中性'
        df['llm_agreement_rate_title'] = 0.0
        # 逐模型虚拟列补全（双轨 + 标题轨道）
        for m in MODELS:
            short = m['short_name']
            for track in ['_full', '_ctx']:
                df[f'{short}_verified{track}'] = True
                df[f'{short}_sentiment{track}'] = '中性'
                df[f'{short}_verification_confidence{track}'] = 0.0
                df[f'{short}_sentiment_confidence{track}'] = 0.0
            # 标题轨道逐模型列
            df[f'{short}_sentiment_title'] = '中性'
            df[f'{short}_sentiment_confidence_title'] = 0.0

        # Logit-to-Score 禁用分支虚拟列（与启用分支输出列对齐）
        if LOGIT_SCORE_ENABLED:
            # 聚合级概率分数（三轨道）
            for track in ['_full', '_ctx', '_title']:
                df[f'llm_prob_score{track}'] = 0.0
            # 逐模型概率分数（三轨道）
            for m in MODELS:
                short = m['short_name']
                for track in ['_full', '_ctx']:
                    df[f'{short}_prob_score{track}'] = 0.0
                    df[f'{short}_prob_source{track}'] = 'P3'
                # 标题轨道逐模型列（与 L620-621 对齐）
                df[f'{short}_prob_score_title'] = 0.0
                df[f'{short}_prob_source_title'] = 'P3'


        output_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
        input_file = os.path.join(CONFIG['paths']['output_dir'],
                                  CONFIG['filenames']['output_14_fintech_intensity'])
        save_dataset(df, output_path, logger,
                    stage_name="21_tone_llms",
                    config=CONFIG,
                    input_files=[input_file])

        log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
        logger.info(f"已透传 {len(df)} 行数据至 {output_path}")
        return
        

    # 初始化 LLM 请求级 SQLite 缓存
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
    with LLMCache(cache_db) as cache:
        logger.info(f"LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")

        # 异步并发大模型（双轨）
        logger.info(f"开始分发双轨组合模型处理任务，包含模型: {[m['short_name'] for m in MODELS]}")
        results_map = asyncio.run(run_all_llms(df, MODELS, cache=cache))

        # 提取与投票（双轨）
        logger.info("开始聚合各模型 JSON 响应并执行双轨多数投票三角验证...")

        llm_verified_full_arr = []
        llm_verified_ctx_arr = []
        llm_sentiment_full_arr = []
        llm_sentiment_ctx_arr = []
        agreement_rate_full_arr = []
        agreement_rate_ctx_arr = []
        # v6/F2 新增掩码列
        agreement_rate_s_full_arr = []
        agreement_rate_s_ctx_arr = []
        n_valid_votes_full_arr = []
        n_valid_votes_ctx_arr = []
        n_verifying_votes_full_arr = []
        n_verifying_votes_ctx_arr = []
        call_failure_full_arr = []
        call_failure_ctx_arr = []
        undefined_full_arr = []
        undefined_ctx_arr = []
        fintech_category_arr = []
        category_confidence_arr = []
        text_type_arr = []

        # 预分配每个模型 × 每轨道的独立判断列表
        per_model_cols = {}
        for m in MODELS:
            short = m['short_name']
            for track in ['_full', '_ctx']:
                per_model_cols[f"{short}_verified{track}"] = []
                per_model_cols[f"{short}_sentiment{track}"] = []
                per_model_cols[f"{short}_verification_confidence{track}"] = []
                per_model_cols[f"{short}_sentiment_confidence{track}"] = []
                if LOGIT_SCORE_ENABLED:
                    per_model_cols[f"{short}_prob_score{track}"] = []
                    per_model_cols[f"{short}_prob_source{track}"] = []

        # Logit-to-Score 轨道级数组
        prob_score_full_arr = []
        prob_score_ctx_arr = []

        n_api_failures = 0

        for idx, row in df.iterrows():
            row_results = results_map.get(idx, {'full': {}, 'ctx': {}})

            # ── Full 轨道聚合 (v6/F2: 14 元组返回) ──
            (final_v_full, final_s_full,
             agree_rate_full, agree_rate_s_full,
             n_valid_full, n_verifying_full,
             call_failure_full, undefined_full,
             parsed_full, topics_full, llm_cats_full, text_types_full,
             n_fail_full, avg_prob_full) = _aggregate_track(row_results.get('full', {}), MODELS)
            n_api_failures += n_fail_full

            llm_verified_full_arr.append(final_v_full)
            llm_sentiment_full_arr.append(final_s_full)
            agreement_rate_full_arr.append(agree_rate_full)
            agreement_rate_s_full_arr.append(agree_rate_s_full)
            n_valid_votes_full_arr.append(n_valid_full)
            n_verifying_votes_full_arr.append(n_verifying_full)
            call_failure_full_arr.append(call_failure_full)
            undefined_full_arr.append(undefined_full)

            for m in MODELS:
                short = m['short_name']
                per_model_cols[f"{short}_verified_full"].append(parsed_full.get(f"{short}_verified"))
                per_model_cols[f"{short}_sentiment_full"].append(parsed_full.get(f"{short}_sentiment"))
                per_model_cols[f"{short}_verification_confidence_full"].append(parsed_full.get(f"{short}_verification_confidence", 0.0))
                per_model_cols[f"{short}_sentiment_confidence_full"].append(parsed_full.get(f"{short}_sentiment_confidence", 0.0))
                if LOGIT_SCORE_ENABLED:
                    per_model_cols[f"{short}_prob_score_full"].append(parsed_full.get(f"{short}_prob_score", 0.0))
                    per_model_cols[f"{short}_prob_source_full"].append(parsed_full.get(f"{short}_prob_source", 'P3'))
            prob_score_full_arr.append(avg_prob_full)

            # ── Ctx 轨道聚合 (v6/F2: 14 元组返回) ──
            (final_v_ctx, final_s_ctx,
             agree_rate_ctx, agree_rate_s_ctx,
             n_valid_ctx, n_verifying_ctx,
             call_failure_ctx, undefined_ctx,
             parsed_ctx, topics_ctx, llm_cats_ctx, text_types_ctx,
             n_fail_ctx, avg_prob_ctx) = _aggregate_track(row_results.get('ctx', {}), MODELS)
            n_api_failures += n_fail_ctx

            llm_verified_ctx_arr.append(final_v_ctx)
            llm_sentiment_ctx_arr.append(final_s_ctx)
            agreement_rate_ctx_arr.append(agree_rate_ctx)
            agreement_rate_s_ctx_arr.append(agree_rate_s_ctx)
            n_valid_votes_ctx_arr.append(n_valid_ctx)
            n_verifying_votes_ctx_arr.append(n_verifying_ctx)
            call_failure_ctx_arr.append(call_failure_ctx)
            undefined_ctx_arr.append(undefined_ctx)

            for m in MODELS:
                short = m['short_name']
                per_model_cols[f"{short}_verified_ctx"].append(parsed_ctx.get(f"{short}_verified"))
                per_model_cols[f"{short}_sentiment_ctx"].append(parsed_ctx.get(f"{short}_sentiment"))
                per_model_cols[f"{short}_verification_confidence_ctx"].append(parsed_ctx.get(f"{short}_verification_confidence", 0.0))
                per_model_cols[f"{short}_sentiment_confidence_ctx"].append(parsed_ctx.get(f"{short}_sentiment_confidence", 0.0))
                if LOGIT_SCORE_ENABLED:
                    per_model_cols[f"{short}_prob_score_ctx"].append(parsed_ctx.get(f"{short}_prob_score", 0.0))
                    per_model_cols[f"{short}_prob_source_ctx"].append(parsed_ctx.get(f"{short}_prob_source", 'P3'))
            prob_score_ctx_arr.append(avg_prob_ctx)

            # ── 金融科技主题标准化分类（仅基于 full 轨道） ──
            combined_topic = ' '.join(topics_full) if topics_full else ''
            kw_category, kw_confidence = canonicalize_topic(combined_topic)

            if llm_cats_full:
                cat_votes = Counter(llm_cats_full)
                top = cat_votes.most_common(2)
                if len(top) >= 2 and top[0][1] == top[1][1]:
                    # 二分类平局：保守降为应用场景
                    llm_majority_cat = '应用场景'
                else:
                    llm_majority_cat = top[0][0] if top else kw_category
                if llm_majority_cat == kw_category:
                    final_confidence = min(kw_confidence + 0.2, 1.0)
                else:
                    final_confidence = round(kw_confidence * 0.5, 3)
                fintech_category_arr.append(llm_majority_cat)
                category_confidence_arr.append(final_confidence)
            else:
                fintech_category_arr.append(kw_category)
                category_confidence_arr.append(kw_confidence)

            # ── 文本类型分类多数决（仅基于 full 轨道，二分类） ──
            if text_types_full:
                tt_votes = Counter(text_types_full)
                tt_top = tt_votes.most_common(2)
                if len(tt_top) >= 2 and tt_top[0][1] == tt_top[1][1]:
                    text_type_arr.append('描述性')  # 二分类平局：保守降为描述性（方案A）
                else:
                    text_type_arr.append(tt_top[0][0])
            else:
                text_type_arr.append(None)



        # 批量赋值各模型独立判断列
        for col_name, col_values in per_model_cols.items():
            df[col_name] = col_values

        df['llm_verified_full'] = llm_verified_full_arr
        df['llm_verified_ctx'] = llm_verified_ctx_arr
        df['llm_sentiment_full'] = llm_sentiment_full_arr
        df['llm_sentiment_ctx'] = llm_sentiment_ctx_arr
        df['llm_agreement_rate_full'] = agreement_rate_full_arr
        df['llm_agreement_rate_ctx'] = agreement_rate_ctx_arr
        # v6/F2 新增掩码 / 元数据列
        df['llm_agreement_rate_s_full'] = agreement_rate_s_full_arr
        df['llm_agreement_rate_s_ctx'] = agreement_rate_s_ctx_arr
        df['n_valid_votes_full'] = n_valid_votes_full_arr
        df['n_valid_votes_ctx'] = n_valid_votes_ctx_arr
        df['n_verifying_votes_full'] = n_verifying_votes_full_arr
        df['n_verifying_votes_ctx'] = n_verifying_votes_ctx_arr
        df['llm_call_failure_full'] = call_failure_full_arr
        df['llm_call_failure_ctx'] = call_failure_ctx_arr
        df['llm_undefined_full'] = undefined_full_arr
        df['llm_undefined_ctx'] = undefined_ctx_arr
        df['fintech_category'] = fintech_category_arr
        df['category_confidence'] = category_confidence_arr
        df['text_type'] = text_type_arr

        # ── Logit-to-Score 概率分数写入 DataFrame ──
        if LOGIT_SCORE_ENABLED:
            df['llm_prob_score_full'] = prob_score_full_arr
            df['llm_prob_score_ctx'] = prob_score_ctx_arr
            n_rows = len(prob_score_full_arr)
            mean_full = sum(prob_score_full_arr) / max(n_rows, 1)
            mean_ctx = sum(prob_score_ctx_arr) / max(n_rows, 1)
            logger.info(f"Logit-to-Score: "
                        f"full mean={mean_full:.4f}, ctx mean={mean_ctx:.4f}, "
                        f"n={n_rows}")

        if n_api_failures > 0:
            logger.warning(f"共有 {n_api_failures} 次模型 API 调用失败，已从对应投票中排除")

        # 统计分类分布（基于 full 轨道）
        if df['llm_verified_full'].sum() > 0:
            verified_df = df[df['llm_verified_full']]
            cat_counts = verified_df['fintech_category'].value_counts()
            for cat, cnt in cat_counts.items():
                logger.info(f"  金融科技分类 [{cat}]: {cnt}")

        # 结果统计（双轨对比）
        total_len = len(df)
        for track in ['_full', '_ctx']:
            ver_col = f'llm_verified{track}'
            sent_col = f'llm_sentiment{track}'
            passed_len = df[ver_col].sum()
            logger.info(f"[{track}] 多数决判定为真: {passed_len}/{total_len} ({passed_len/total_len*100:.1f}%)")

            if passed_len > 0:
                sent_counts = df[df[ver_col]][sent_col].value_counts()
                for s_type, cnt in sent_counts.items():
                    logger.info(f"  [{track}] [{s_type}]: {cnt} ({cnt/passed_len*100:.1f}%)")

        # 保存全量结果（含 llm_verified=True 和 False），供验证模块使用
        full_output_filename = CONFIG.get('filenames', {}).get(
            'output_21_tone_llms_full', '21_tone_llms_full.parquet')
        full_output_path = os.path.join(CONFIG["paths"]["output_dir"], full_output_filename)
        input_file = os.path.join(CONFIG['paths']['output_dir'],
                                  CONFIG['filenames']['output_14_fintech_intensity'])
        save_dataset(df, full_output_path, logger,
                    stage_name="21_tone_llms",
                    config=CONFIG,
                    input_files=[input_file])
        logger.info(f"全量 LLM 结果已保存: {full_output_path} ({len(df)} 行)")

        # 过滤丢弃不相关的假新闻（基于 full 轨道）
        df_filtered = df[df['llm_verified_full'] == True].copy()

        # ── B1-2: 标题轨道独立情感提取（仅已验证样本） ──
        # 学术依据: 姜富伟, 熊健, 朱林义 (2024). 大语言模型驱动的金融科技
        #           情感分析: 方法与实证. 管理世界, (8), 58-72.
        #           该文证明: 标题短文本LLM情感与全文情感的交叉验证可有效
        #           识别"标题党"偏差并提升情感度量的鲁棒性。
        TITLE_PROMPT_TEMPLATE = LLM_CONFIG.get('title_sentiment_prompt_template', '')
        # Plan-r3 P3-17 接入: 与 PROMPT_VERSION 同源, 由 core/config.py
        # 自动从 config/prompts/title_sentiment.txt 的 ``# version:`` 头解析.
        TITLE_PROMPT_VERSION = LLM_CONFIG.get(
            'title_sentiment_prompt_template_version', 'v0'
        )

        if TITLE_PROMPT_TEMPLATE and len(df_filtered) > 0:
            logger.info(f"── 标题轨道情感提取开始 ({len(df_filtered)} 条已验证样本) ──")

            BATCH_SIZE = 100
            titles = df_filtered['标题'].fillna('').astype(str).tolist()
            indices = df_filtered.index.tolist()

            # 按批次分组
            batches = []
            for i in range(0, len(titles), BATCH_SIZE):
                batch_titles = titles[i:i+BATCH_SIZE]
                batch_indices = indices[i:i+BATCH_SIZE]
                numbered = '\n'.join(f"{j+1}. {t}" for j, t in enumerate(batch_titles))
                prompt = TITLE_PROMPT_TEMPLATE.format(numbered_titles=numbered)
                batches.append((batch_indices, batch_titles, prompt))

            logger.info(f"  共 {len(batches)} 批 × {len(MODELS)} 模型 = {len(batches)*len(MODELS)} 次 API 调用")

            async def _run_title_batches():
                """批量调用LLM获取标题情感"""
                semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
                connector = build_llm_connector(MAX_CONCURRENCY)
                timeout = build_llm_timeout()
                request_pacers = build_model_pacers(MODELS, LLM_CONFIG.get('request_spacing_seconds', 0.0))
                model_availability = AsyncModelAvailability()

                # {batch_idx: {model_id: response_text}}
                batch_results = {}

                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    await preflight_model_availability(session, MODELS, model_availability)
                    tasks = []
                    for b_idx, (b_indices, b_titles, prompt) in enumerate(batches):
                        for m in MODELS:
                            tasks.append(
                                fetch_llm_async(
                                    session, semaphore, prompt, m, b_idx, 'title', cache=cache,
                                    request_pacer=request_pacers.get(m['model_name']),
                                    model_availability=model_availability,
                                    prompt_version=TITLE_PROMPT_VERSION,
                                )
                            )

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for res in results:
                        if isinstance(res, Exception):
                            logger.warning(f"  标题批次请求异常: {res}")
                            continue
                        b_idx, model_id, text, track = res
                        if b_idx not in batch_results:
                            batch_results[b_idx] = {}
                        batch_results[b_idx][model_id] = text

                return batch_results

            batch_results = asyncio.run(_run_title_batches())

            # 解析批量结果 → 逐条多数决
            title_sentiment_map = {}  # {df_index: {'sentiment': ..., 'confidence': ..., per_model...}}

            for b_idx, (b_indices, b_titles, _) in enumerate(batches):
                # 收集每个模型对这批的解析结果
                per_model_parsed = {}  # {model_short: [{id, sentiment, confidence}, ...]}

                for m in MODELS:
                    short = m['short_name']
                    m_id = m['model_name']
                    raw = batch_results.get(b_idx, {}).get(m_id, None)

                    if raw is None:
                        per_model_parsed[short] = [None] * len(b_indices)
                        continue

                    jd = parse_json_response(raw)
                    items = jd.get('results', [])

                    # 构建 id → item 映射（防止 id 缺失或乱序）
                    id_map = {}
                    for item in items:
                        if isinstance(item, dict):
                            id_map[item.get('id', -1)] = item

                    parsed_list = []
                    for j in range(len(b_indices)):
                        item = id_map.get(j + 1)
                        if item:
                            try:
                                conf_val = float(item.get('confidence', 0.0))
                            except (ValueError, TypeError):
                                conf_val = 0.0
                            parsed_list.append({
                                'sentiment': item.get('sentiment', '中性'),
                                'confidence': conf_val
                            })
                        else:
                            parsed_list.append(None)
                    per_model_parsed[short] = parsed_list

                # 逐条多数决
                for j, df_idx in enumerate(b_indices):
                    s_votes = []
                    per_model_data = {}

                    for m in MODELS:
                        short = m['short_name']
                        item = per_model_parsed[short][j]
                        if item is not None:
                            s_votes.append(item['sentiment'])
                            per_model_data[f'{short}_sentiment_title'] = item['sentiment']
                            per_model_data[f'{short}_sentiment_confidence_title'] = item['confidence']
                            if LOGIT_SCORE_ENABLED:
                                ps = compute_prob_score(item['sentiment'], item['confidence'])
                                per_model_data[f'{short}_prob_score_title'] = ps['prob_score']
                                per_model_data[f'{short}_prob_source_title'] = ps['prob_source']
                        else:
                            per_model_data[f'{short}_sentiment_title'] = None
                            per_model_data[f'{short}_sentiment_confidence_title'] = 0.0
                            if LOGIT_SCORE_ENABLED:
                                per_model_data[f'{short}_prob_score_title'] = 0.0
                                per_model_data[f'{short}_prob_source_title'] = 'P3'

                    # 多数决（统一使用 majority_vote_sentiment，确保平局处理
                    # 与 full/ctx 轨道一致：平局时降级为中性）
                    if s_votes:
                        final_s = majority_vote_sentiment(s_votes)
                        agree_count = sum(1 for v in s_votes if v == final_s)
                        agree_rate = agree_count / len(s_votes)
                    else:
                        final_s = '中性'
                        agree_rate = 0.0

                    title_sentiment_map[df_idx] = {
                        'llm_sentiment_title': final_s,
                        'llm_agreement_rate_title': agree_rate,
                        **per_model_data
                    }

            # 写入 DataFrame
            for col in ['llm_sentiment_title', 'llm_agreement_rate_title']:
                df_filtered[col] = df_filtered.index.map(
                    lambda idx, c=col: title_sentiment_map.get(idx, {}).get(c))

            for m in MODELS:
                short = m['short_name']
                for suffix in ['_sentiment_title', '_sentiment_confidence_title']:
                    col = f'{short}{suffix}'
                    df_filtered[col] = df_filtered.index.map(
                        lambda idx, c=col: title_sentiment_map.get(idx, {}).get(c))

            # Step 1c: llm_verified_title 固定为 True（已通过 full 轨道验证）
            df_filtered['llm_verified_title'] = True

            # Logit-to-Score 标题轨道概率分数
            if LOGIT_SCORE_ENABLED:
                # 计算每篇文章的多模型平均 prob_score
                def _calc_title_prob(idx):
                    data = title_sentiment_map.get(idx, {})
                    scores = [data.get(f'{m["short_name"]}_prob_score_title', 0.0) for m in MODELS
                              if data.get(f'{m["short_name"]}_sentiment_title') is not None]
                    return sum(scores) / len(scores) if scores else 0.0
                df_filtered['llm_prob_score_title'] = df_filtered.index.map(_calc_title_prob)

                for m in MODELS:
                    short = m['short_name']
                    for suffix in ['_prob_score_title', '_prob_source_title']:
                        col = f'{short}{suffix}'
                        df_filtered[col] = df_filtered.index.map(
                            lambda idx, c=col: title_sentiment_map.get(idx, {}).get(c))

            # 统计
            sent_counts = df_filtered['llm_sentiment_title'].value_counts()
            logger.info(f"── 标题轨道情感提取完成 ──")
            for s_type, cnt in sent_counts.items():
                logger.info(f"  [_title] [{s_type}]: {cnt} ({cnt/len(df_filtered)*100:.1f}%)")
        else:
            if not TITLE_PROMPT_TEMPLATE:
                logger.info("  title_sentiment_prompt_template 未配置，跳过标题轨道")
            else:
                logger.info("  无已验证样本，跳过标题轨道")

        # ======================================================================
        # 4. 保存文件与报告
        # ======================================================================
        output_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)

        logger.info(f"正在保存处理结果至 {output_path}...")
        input_file = os.path.join(CONFIG['paths']['output_dir'],
                                  CONFIG['filenames']['output_14_fintech_intensity'])
        save_dataset(df_filtered, output_path, logger,
                    stage_name="21_tone_llms",
                    config=CONFIG,
                    input_files=[input_file])

        log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df_filtered))

if __name__ == "__main__":
    main()
