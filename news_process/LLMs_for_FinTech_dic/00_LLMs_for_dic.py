"""
银行领域关键词生成与判别工具

功能：
    1. 使用多个 LLM 模型并行生成银行领域关键词
    2. 去重 → 词根精简 → 拼音排序
    3. 使用顶级模型批量判别每个关键词的专业度
    4. 汇总保存为多 Sheet 的 Excel 文件

用法：
    python LLMs_for_dic/LLMs_for_dic.py                  # 运行完整流程
    python LLMs_for_dic/LLMs_for_dic.py --resume          # 从断点继续（跳过生成阶段）
    python LLMs_for_dic/LLMs_for_dic.py --view-logs       # 列出所有历史日志
    python LLMs_for_dic/LLMs_for_dic.py --view-log latest # 查看最新日志
"""

# === 标准库 ===
import argparse
import concurrent.futures
import json
import logging
import random
import re
import signal
import threading
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# === 第三方库 ===
import pandas as pd
from openai import OpenAI
from pypinyin import lazy_pinyin

# === 本地配置 ===
from config import (
    API_KEY,
    CHECKPOINT_FILE,
    DATA_DIR,
    DOMAINS,
    JUDGE_BATCH_SIZE,
    JUDGE_CHECKPOINT_FILE,
    JUDGE_MODELS,
    LOG_DIR,
    LOG_RETENTION_COUNT,
    MAX_RETRIES,
    MAX_TOTAL_RETRIES,
    MAX_WORKERS_GENERATE,
    MAX_WORKERS_JUDGE,
    MAX_PARSE_RETRIES,
    MAX_JUDGE_RETRIES,
    MAX_CONCURRENT_PER_MODEL,
    MODEL_FAIL_THRESHOLD,
    MODELS,
    NUM_REPEAT_PER_MODEL,
    REQUEST_TIMEOUT,
    SCRIPT_DIR,
    get_client_config,
    get_model_params,
    get_temperature,
    is_thinking_model,
    build_generate_prompt,
    build_judge_prompt,
    GEN_CHECKPOINT_FILE,
)

# 输出文件路径（含时间戳，每次运行生成新文件）
OUTPUT_FILE = DATA_DIR / f"bank_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

# ════════════════════════════════════════════════════════════════
# 全局状态
# ════════════════════════════════════════════════════════════════

# 优雅中断：Ctrl+C 后置位，所有工作线程检测到后停止发起新请求
_shutdown_event = threading.Event()
# 全局重试计数器（线程安全）
_total_retry_count = 0
_retry_lock = threading.Lock()

# 按模型的并发信号量：限制每个模型同时在途的请求数，防止 429 限流
_model_semaphores: Dict[str, threading.Semaphore] = {}
_semaphore_lock = threading.Lock()

def _get_model_semaphore(model_name: str) -> threading.Semaphore:
    """获取指定模型的并发信号量（惰性初始化，线程安全）。"""
    if model_name not in _model_semaphores:
        with _semaphore_lock:
            if model_name not in _model_semaphores:
                _model_semaphores[model_name] = threading.Semaphore(MAX_CONCURRENT_PER_MODEL)
    return _model_semaphores[model_name]


class _ModelHealthTracker:
    """模型健康追踪器：自动跳过持续失败的模型，避免浪费时间和费用。"""

    def __init__(self, threshold: int = MODEL_FAIL_THRESHOLD) -> None:
        self._consecutive_fails: Dict[str, int] = {}
        self._skipped: Set[str] = set()
        self._lock = threading.Lock()
        self._threshold = threshold

    def record_success(self, model: str) -> None:
        """记录模型成功，重置其连续失败计数。"""
        with self._lock:
            self._consecutive_fails[model] = 0

    def record_failure(self, model: str) -> None:
        """记录模型失败。连续失败达到阈值后标记为跳过。"""
        with self._lock:
            self._consecutive_fails[model] = self._consecutive_fails.get(model, 0) + 1
            if self._consecutive_fails[model] >= self._threshold:
                self._skipped.add(model)

    def should_skip(self, model: str) -> bool:
        """检查模型是否应被跳过。"""
        with self._lock:
            return model in self._skipped

    def get_skipped(self) -> Set[str]:
        """返回所有已跳过的模型。"""
        with self._lock:
            return self._skipped.copy()


# 全局模型健康追踪器
_model_health = _ModelHealthTracker()


def _increment_retry_count() -> bool:
    """
    递增全局重试计数，返回是否仍允许重试。
    超过 MAX_TOTAL_RETRIES 时返回 False（费用保护）。
    """
    global _total_retry_count
    with _retry_lock:
        _total_retry_count += 1
        return _total_retry_count <= MAX_TOTAL_RETRIES


def _signal_handler(sig: int, frame: Any) -> None:
    """Ctrl+C 信号处理：设置中断标志，等待当前请求完成后安全退出。"""
    logger = logging.getLogger("LLMs_for_dic")
    logger.warning("⚠️ 收到中断信号 (Ctrl+C)，正在等待当前请求完成后安全退出...")
    _shutdown_event.set()


# 注册信号处理器
signal.signal(signal.SIGINT, _signal_handler)

# OpenAI 客户端缓存（线程安全）：复用连接，避免每次新建
_client_cache: Dict[str, OpenAI] = {}
_client_cache_lock = threading.Lock()


def _get_client(client_config: Dict[str, str]) -> OpenAI:
    """获取或创建缓存的 OpenAI 客户端，避免重复建连。"""
    key = f"{client_config.get('base_url', '')}:{client_config.get('api_key', '')[:8]}"
    with _client_cache_lock:
        if key not in _client_cache:
            _client_cache[key] = OpenAI(**client_config, max_retries=0)
        return _client_cache[key]

def setup_logger() -> logging.Logger:
    """初始化日志系统：同时输出到控制台和日志文件，自动清理旧日志。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 自动清理旧日志：仅保留最近 LOG_RETENTION_COUNT 个
    existing_logs = sorted(f for f in LOG_DIR.iterdir() if f.name.startswith("run_") and f.suffix == ".log")
    if len(existing_logs) > LOG_RETENTION_COUNT:
        for old_log in existing_logs[:-LOG_RETENTION_COUNT]:
            try:
                old_log.unlink()
            except OSError:
                pass

    log_filename = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = LOG_DIR / log_filename

    logger = logging.getLogger("LLMs_for_dic")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件 Handler
    fh = logging.FileHandler(str(log_filepath), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(f"日志文件: {log_filepath}")
    return logger


def view_logs() -> None:
    """列出所有历史日志文件。"""
    if not LOG_DIR.exists():
        print("暂无运行日志。")
        return
    files = sorted(f for f in LOG_DIR.iterdir() if f.suffix == ".log")
    if not files:
        print("暂无运行日志。")
        return
    print(f"\n{'=' * 60}")
    print(f"  历史运行日志 (共 {len(files)} 个)")
    print(f"  目录: {LOG_DIR.resolve()}")
    print(f"{'=' * 60}")
    for i, fp in enumerate(files, 1):
        size = fp.stat().st_size
        mtime = datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_str = f"{size / 1024:.1f}KB" if size >= 1024 else f"{size}B"
        print(f"  {i:>3}. {fp.name}  ({size_str}, {mtime})")
    print(f"{'=' * 60}")
    print(f"  使用 --view-log <文件名> 查看具体日志")
    print(f"  使用 --view-log latest 查看最新日志\n")


def view_log(name: str) -> None:
    """查看指定日志文件内容。"""
    if not LOG_DIR.exists():
        print("暂无运行日志。")
        return
    files = sorted(f.name for f in LOG_DIR.iterdir() if f.suffix == ".log")
    if not files:
        print("暂无运行日志。")
        return
    if name == "latest":
        target = files[-1]
    elif name in files:
        target = name
    else:
        print(f"日志文件 '{name}' 不存在。可用文件:")
        for f in files:
            print(f"  - {f}")
        return
    filepath = LOG_DIR / target
    print(f"\n{'=' * 60}")
    print(f"  日志文件: {target}")
    print(f"{'=' * 60}\n")
    print(filepath.read_text(encoding="utf-8"))
    print(f"\n{'=' * 60}\n")


# ════════════════════════════════════════════════════════════════
# 通用工具函数
# ════════════════════════════════════════════════════════════════

def _safe_parse_json(text: str) -> dict:
    """
    安全解析 JSON 文本。
    1. 去除 <think>...</think> 标签
    2. 去除 ```json ... ``` markdown 代码块包裹
    3. 先尝试直接解析，失败则用正则提取 {...} 部分

    Args:
        text: LLM 返回的原始文本

    Returns:
        解析后的 dict，解析失败返回空 dict
    """
    if not text:
        return {}
    # 去除 <think>...</think> 块（含未闭合的情况）
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)
    # 去除孤立的 </think> 或 </think（未闭合）及其后续内容
    text = re.sub(r"</think.*", "", text, flags=re.DOTALL)
    # 去除 markdown 代码块包裹：```json ... ``` 或 ``` ... ```
    text = re.sub(r"```(?:json)?\s*\n?", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        return {}


def _calculate_backoff(
    error_str: str,
    retry_index: int,
    consecutive_timeouts: int,
) -> float:
    """
    根据错误类型计算退避等待时间（指数退避 + 随机抖动）。

    Args:
        error_str: 错误信息字符串
        retry_index: 当前重试次数索引
        consecutive_timeouts: 连续超时次数

    Returns:
        等待秒数
    """
    if consecutive_timeouts >= 5:
        return 60 + random.uniform(0, 30)
    elif "429" in error_str or "负载已饱和" in error_str:
        return min(60, (2 ** min(retry_index, 6)) * 2) + random.uniform(0, 15)
    elif "timed out" in error_str.lower():
        return min(30, (2 ** min(retry_index, 5)) * 2) + random.uniform(0, 10)
    elif "502" in error_str or "503" in error_str:
        return min(60, (2 ** min(retry_index, 6)) * 3) + random.uniform(0, 15)
    else:
        return min(15, (2 ** min(retry_index, 4)) * 1) + random.uniform(0, 5)




def _call_llm_with_retry(
    client: OpenAI,
    model_name: str,
    prompt: str,
    task_id: str,
    logger: logging.Logger,
    force_temperature: Optional[float] = None,
) -> Optional[str]:
    """
    带重试的 LLM 调用。统一处理重试逻辑、退避策略、中断检测和费用保护。

    Args:
        client: OpenAI 客户端
        model_name: 模型名称
        prompt: 提示词
        task_id: 任务标识（用于日志）
        logger: 日志记录器
        force_temperature: 强制使用的 temperature 值。
            None = 不传 temperature，使用模型默认值；
            数值 = 强制使用该 temperature（如 0 表示最大确定性）。

    Returns:
        LLM 返回的文本内容，失败返回 None
    """
    model_params = get_model_params(model_name)
    # 根据 force_temperature 参数决定是否传递 temperature
    if force_temperature is not None:
        model_params["temperature"] = force_temperature
    else:
        model_params.pop("temperature", None)
    consecutive_timeouts = 0

    for i in range(MAX_RETRIES):
        # 检查是否收到中断信号
        if _shutdown_event.is_set():
            logger.warning(f"  [{task_id}] 检测到中断信号，停止重试")
            return None

        try:
            call_kwargs = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "timeout": REQUEST_TIMEOUT,
                **model_params,
            }
            # 使用模型信号量控制并发，防止触发 429 限流
            sem = _get_model_semaphore(model_name)
            sem.acquire()
            try:
                resp = client.chat.completions.create(**call_kwargs)
            finally:
                sem.release()
            return resp.choices[0].message.content

        except Exception as e:
            error_str = str(e)
            logger.warning(f"  [{task_id}] 重试 {i + 1}/{MAX_RETRIES}: {e}")

            # 连续超时计数
            if "timed out" in error_str.lower():
                consecutive_timeouts += 1
            else:
                consecutive_timeouts = 0

            # 费用保护：全局重试上限
            if not _increment_retry_count():
                logger.error(
                    f"  [{task_id}] ⚠️ 全局重试次数已达上限 ({MAX_TOTAL_RETRIES})，"
                    f"终止所有请求以保护费用"
                )
                _shutdown_event.set()
                return None

            # 计算退避时间
            wait = _calculate_backoff(error_str, i, consecutive_timeouts)
            if consecutive_timeouts >= 5:
                logger.warning(
                    f"  [{task_id}] 连续超时{consecutive_timeouts}次，等待{wait:.0f}s"
                )
            logger.debug(f"  [{task_id}] 等待 {wait:.1f}s 后重试")
            time.sleep(wait)

    logger.error(f"  [{task_id}] 达到最大重试次数，任务失败")
    return None


# ════════════════════════════════════════════════════════════════
# 核心任务函数
# ════════════════════════════════════════════════════════════════

def fetch_batch(args: Tuple) -> Tuple[str, str, List[str]]:
    """
    单个生成任务：按指定领域向指定模型请求关键词。

    Args:
        args: (model_name, dom_name, prompt, idx, client_config) 元组

    Returns:
        (模型名, 领域名, 关键词列表, 任务idx)，失败时列表为空
    """
    model_name, dom_name, prompt, idx, client_config = args

    if _shutdown_event.is_set():
        return (model_name, dom_name, [], idx)

    # 模型健康检查：跳过持续失败的模型
    if _model_health.should_skip(model_name):
        return (model_name, dom_name, [], idx)

    client = _get_client(client_config)
    logger = logging.getLogger("LLMs_for_dic")
    task_id = f"{model_name}/{dom_name} ({idx + 1})"
    logger.info(f"  [任务 {task_id}] 开始请求...")

    # 解析失败重试：API 调用成功但解析不到关键词时重试（最多 MAX_PARSE_RETRIES 次）
    for parse_attempt in range(MAX_PARSE_RETRIES + 1):
        if _shutdown_event.is_set():
            return (model_name, dom_name, [], idx)

        text = _call_llm_with_retry(client, model_name, prompt, f"任务 {task_id}", logger)
        if text is None:
            return (model_name, dom_name, [], idx)

        logger.debug(f"  [任务 {task_id}] LLM 原始响应:\n{text}")
        data = _safe_parse_json(text)

        # 提取列表（兼容不同 key 名称）
        result_list: List[str] = []
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            result_list.append(item)
                        elif isinstance(item, list):
                            result_list.extend(str(i) for i in item if isinstance(i, str))
                    break

        if result_list:
            logger.info(f"  [任务 {task_id}] 成功获取 {len(result_list)} 个词")
            _model_health.record_success(model_name)
            return (model_name, dom_name, result_list, idx)

        # 解析失败，判断是否需要重试
        if parse_attempt < MAX_PARSE_RETRIES:
            wait = min(10, 2 * (2 ** parse_attempt))  # 2s, 4s, 8s, 10s...
            logger.warning(
                f"  [任务 {task_id}] 解析失败 ({parse_attempt + 1}/{MAX_PARSE_RETRIES})，"
                f"等待 {wait}s 后重试... 原始响应: {(text or '')[:80]}"
            )
            time.sleep(wait)
        else:
            logger.error(f"  [任务 {task_id}] 失败：解析重试 {MAX_PARSE_RETRIES} 次后仍未提取到关键词列表")
            _model_health.record_failure(model_name)

    return (model_name, dom_name, [], idx)


def judge_batch(args: Tuple) -> Tuple[str, List[Tuple[str, int, str]]]:
    """
    批量判别任务：一次发送一批关键词给模型，获取判别得分及理由。

    Args:
        args: (model_name, keywords_batch, batch_idx, client_config) 元组

    Returns:
        (模型名, [(关键词, 得分, 理由), ...])
    """
    model_name, keywords_batch, batch_idx, client_config = args

    client = _get_client(client_config)
    logger = logging.getLogger("LLMs_for_dic")
    task_id = f"判别-{model_name}/批次{batch_idx + 1}"

    best_partial_results = []
    best_partial_count = 0

    for attempt in range(MAX_JUDGE_RETRIES):
        if _shutdown_event.is_set():
            return (model_name, [(kw, 0, "") for kw in keywords_batch])

        # 模型健康检查
        if _model_health.should_skip(model_name):
            return (model_name, [(kw, 0, "") for kw in keywords_batch])

        prompt = build_judge_prompt(keywords_batch)
        text = _call_llm_with_retry(client, model_name, prompt, task_id, logger, force_temperature=0)

        if text is None:
            logger.warning(f"  [{task_id}] 第{attempt + 1}次尝试失败，返回为None")
        else:
            logger.debug(f"  [{task_id}] LLM 原始响应:\n{text}")
            data = _safe_parse_json(text)

            # 提取 results 列表
            results_list = data.get("results", [])
            if not results_list:
                for v in data.values():
                    if isinstance(v, list) and len(v) > 0:
                        results_list = v
                        break

            if results_list and len(results_list) > 0:
                # 构建 keyword -> (score, reason) 的映射
                result_map: Dict[str, Tuple[int, str]] = {}
                for item in results_list:
                    if isinstance(item, dict) and "keyword" in item:
                        kw = str(item["keyword"]).strip()
                        sc = int(item.get("score", 0))
                        rs = str(item.get("reason", "")).strip()
                        result_map[kw] = (sc, rs)

                # 对原始列表按顺序输出，未匹配的补默认值
                batch_results = []
                for kw in keywords_batch:
                    if kw in result_map:
                        batch_results.append((kw, result_map[kw][0], result_map[kw][1]))
                    else:
                        batch_results.append((kw, 0, ""))

                if len(result_map) == len(keywords_batch):
                    logger.info(f"  [{task_id}] 成功判别 {len(result_map)}/{len(keywords_batch)} 个词")
                    return (model_name, batch_results)
                else:
                    logger.warning(f"  [{task_id}] 第{attempt + 1}次尝试部分判别成功 ({len(result_map)}/{len(keywords_batch)})，未完全覆盖，准备重试")
                    if len(result_map) > best_partial_count:
                        best_partial_count = len(result_map)
                        best_partial_results = batch_results

            else:
                # 解析结果不足，准备重试
                logger.warning(f"  [{task_id}] 第{attempt + 1}次尝试解析结果不足")

        # 提前退出：如果部分成功结果覆盖率已 >= 95% 且重试超过5次，直接采纳
        if best_partial_count > 0 and attempt >= 5:
            coverage = best_partial_count / len(keywords_batch)
            if coverage >= 0.95:
                logger.warning(
                    f"  [{task_id}] 重试{attempt + 1}次后覆盖率达 {coverage:.0%} "
                    f"({best_partial_count}/{len(keywords_batch)})，提前采纳部分结果"
                )
                return (model_name, best_partial_results)

        if attempt < MAX_JUDGE_RETRIES - 1:
            wait = min(15, 2 * (2 ** attempt)) + random.uniform(0, 5)  # 退避等待
            logger.info(f"  [{task_id}] 判定失败，等待 {wait:.1f}s 后进行第 {attempt + 2} 次重试...")
            time.sleep(wait)

    # 超过最大重试次数，如果有部分成功的结果，则返回最佳部分成功结果
    if best_partial_count > 0:
        logger.warning(f"  [{task_id}] 达到最大重试次数，采纳最佳部分判别结果 ({best_partial_count}/{len(keywords_batch)})，其余标记为0")
        return (model_name, best_partial_results)

    # 超过最大重试次数，标记失败
    logger.error(f"  [{task_id}] 失败，全部标记为0")
    return (model_name, [(kw, 0, "") for kw in keywords_batch])


# ════════════════════════════════════════════════════════════════
# 断点续传
# ════════════════════════════════════════════════════════════════

def _save_gen_checkpoint(
    dom_keywords: Dict[str, List[str]],
    all_keywords: List[str],
    all_records: List[Dict[str, str]],
    keywords_raw_count: int,
    completed_task_ids: List[str],
) -> None:
    """保存生成阶段的中间结果，支持在生成阶段中断后恢复。"""
    GEN_CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_data = {
        "timestamp": datetime.now().isoformat(),
        "dom_keywords": dom_keywords,
        "all_keywords": all_keywords,
        "all_records": all_records,
        "keywords_raw_count": keywords_raw_count,
        "completed_task_ids": completed_task_ids,
    }
    GEN_CHECKPOINT_FILE.write_text(
        json.dumps(checkpoint_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_gen_checkpoint() -> Optional[dict]:
    """加载生成阶段的中间断点文件，如果不存在返回 None。"""
    if not GEN_CHECKPOINT_FILE.exists():
        return None
    try:
        data = json.loads(GEN_CHECKPOINT_FILE.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def _save_checkpoint(
    dom_keywords: Dict[str, List[str]],
    all_keywords: List[str],
    all_records: List[Dict[str, str]],
    keywords_raw_count: int,
    unique_keywords: List[str],
    simplified_keywords: List[str],
) -> None:
    """保存生成阶段的结果到 checkpoint 文件，以便断点续传（进入判别阶段）。"""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_data = {
        "timestamp": datetime.now().isoformat(),
        "dom_keywords": dom_keywords,
        "all_keywords": all_keywords,
        "all_records": all_records,
        "keywords_raw_count": keywords_raw_count,
        "unique_keywords": unique_keywords,
        "simplified_keywords": simplified_keywords,
    }
    CHECKPOINT_FILE.write_text(
        json.dumps(checkpoint_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_checkpoint() -> Optional[dict]:
    """加载 checkpoint 文件，返回 None 如果不存在或解析失败。"""
    if not CHECKPOINT_FILE.exists():
        return None
    try:
        data = json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def _delete_checkpoint() -> None:
    """删除所有 checkpoint 文件。"""
    for fp in (CHECKPOINT_FILE, JUDGE_CHECKPOINT_FILE, GEN_CHECKPOINT_FILE):
        if fp.exists():
            fp.unlink()


def _save_judge_checkpoint(
    model_results: Dict[str, Dict[str, List[Any]]],
    completed_tasks: int,
    total_tasks: int,
) -> None:
    """保存判别阶段中间结果，支持判别阶段断点续传。"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "model_results": {
            m: {kw: v for kw, v in results.items()}
            for m, results in model_results.items()
        },
    }
    JUDGE_CHECKPOINT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load_judge_checkpoint() -> Optional[dict]:
    """加载判别阶段断点，返回 None 如果不存在。"""
    if not JUDGE_CHECKPOINT_FILE.exists():
        return None
    try:
        data = json.loads(JUDGE_CHECKPOINT_FILE.read_text(encoding="utf-8"))
        # 结果为具有分数和理由的列表（兼容旧版保存格式）
        model_results = {}
        for m, results in data.get("model_results", {}).items():
            model_results[m] = {}
            for kw, v in results.items():
                if isinstance(v, list):
                    score = int(v[0]) if len(v) > 0 else 0
                    reason = str(v[1]) if len(v) > 1 else ""
                    model_results[m][kw] = [score, reason]
                else:
                    model_results[m][kw] = [int(v), ""]
        data["model_results"] = model_results
        return data
    except (json.JSONDecodeError, KeyError):
        return None


# ════════════════════════════════════════════════════════════════
# 数据处理辅助函数
# ════════════════════════════════════════════════════════════════

def _clean_keywords(keywords: List) -> List[str]:
    """
    清洗关键词列表：过滤无效值，Unicode 规范化，去序号前缀，去前后标点。

    Args:
        keywords: 原始关键词列表（可能含 None、float 等）

    Returns:
        清洗后的字符串列表
    """
    # 序号前缀正则：匹配 "1. xxx" / "1、xxx" / "1) xxx" 等
    _NUM_PREFIX = re.compile(r"^\d+[\.\、\)\]\s]+")
    # 前后标点
    _PUNCT = re.compile(r'^[\s\-\—\–\•\·\"\"\'\'\u3001\u3002\uff0c\uff1b]+|[\s\-\—\–\•\·\"\"\'\'\u3001\u3002\uff0c\uff1b]+$')

    cleaned: List[str] = []
    for k in keywords:
        if k is None:
            continue
        s = str(k)
        if s.lower() in ("nan", "none", ""):
            continue
        # NFKC 规范化（全角 → 半角，兼容字符统一）
        s = unicodedata.normalize("NFKC", s)
        # 去序号前缀
        s = _NUM_PREFIX.sub("", s)
        # 去前后标点
        s = _PUNCT.sub("", s)
        s = s.strip()
        if s:
            cleaned.append(s)
    return cleaned



def _simplify_keywords(unique_keywords: List[str]) -> List[str]:
    """
    词根精简：移除被更短词完全包含的派生词。
    例如 "信用风险管理" 包含 "信用风险"，则去除 "信用风险管理"。
    优化：使用 Set 加速查找，替代纯 Python 实现的 Trie 树以提升性能。
    """
    logger = logging.getLogger("LLMs_for_dic")
    logger.info(f"开始词根精简，当前去重后词数: {len(unique_keywords)} ...")
    
    # 1. 按长度排序：短词在前
    sorted_by_len = sorted(unique_keywords, key=len)
    
    simplified_set = set() # 存储已保留的词（短词）
    simplified = []
    
    start_time = time.time()
    count = 0
    total = len(sorted_by_len)
    
    for word in sorted_by_len:
        is_derived = False
        # 检查 word 的所有子串是否存在于 simplified_set 中
        # 为了性能，直接生成子串检查。由于大多数词较短，这比 Trie 遍历（Python解释器开销）更快。
        word_len = len(word)
        # 优化：仅需检查长度小于 word_len 的子串，因为我们是按长度排序处理的
        # 且 simplified_set 里只可能有比当前 word 短或等长的词
        
        # 遍历可能的子串起点
        for i in range(word_len):
            # 遍历可能的子串终点
            for j in range(i + 1, word_len + 1):
                # 跳过 word 本身（如果本身已在 set 中，说明重复，应被过滤；虽然 unique_keywords 理论上无重复）
                if j - i == word_len:
                    continue
                
                sub = word[i:j]
                if sub in simplified_set:
                    is_derived = True
                    break
            if is_derived:
                break
        
        if not is_derived:
            simplified.append(word)
            simplified_set.add(word)
        
        count += 1
        if count % 10000 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            logger.info(f"  已处理 {count}/{total} 个词 ({count/total*100:.1f}%), 耗时 {elapsed:.1f}s, 速度 {rate:.0f}词/s")

    elapsed = time.time() - start_time
    logger.info(f"词根精简完成。保留: {len(simplified)}/{total}, 总耗时: {elapsed:.2f}s")
    return simplified


# ════════════════════════════════════════════════════════════════
# Excel 格式化
# ════════════════════════════════════════════════════════════════

def _format_excel_workbook(filepath: Path) -> None:
    """
    对已保存的 Excel 文件进行专业格式化：
    - 冻结首行
    - 自动列宽（根据内容最大长度）
    - 表头加粗 + 浅蓝底色
    - 判别结果 Sheet 的 score 列条件格式（0=红, 满分=绿）
    """
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter

        wb = load_workbook(filepath)
        header_fill = PatternFill(start_color="D6EAF8", end_color="D6EAF8", fill_type="solid")
        header_font = Font(bold=True, size=11)
        center_align = Alignment(horizontal="center", vertical="center")
        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        for ws in wb.worksheets:
            # 冻结首行
            ws.freeze_panes = "A2"

            # 表头样式
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align

            # 自动列宽
            for col_idx, col_cells in enumerate(ws.columns, 1):
                max_len = 0
                for cell in col_cells:
                    val = str(cell.value or "")
                    # 中文字符按 2 倍宽度计算
                    char_len = sum(2 if ord(c) > 127 else 1 for c in val)
                    max_len = max(max_len, char_len)
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 60)

            # 对 score 列应用条件格式（仅含 score 的 Sheet）
            for col_idx, cell in enumerate(ws[1], 1):
                header_val = str(cell.value or "")
                if header_val.endswith("_score") or header_val == "total_score":
                    for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                        for sc_cell in row:
                            if sc_cell.value == 0:
                                sc_cell.fill = red_fill
                            elif sc_cell.value == 1:
                                sc_cell.fill = green_fill
                            sc_cell.alignment = center_align

        wb.save(filepath)
    except Exception:
        pass  # 格式化失败不影响数据保存


# ════════════════════════════════════════════════════════════════
# 主函数
# ════════════════════════════════════════════════════════════════

def main(resume: bool = False, dry_run: bool = False) -> None:
    """
    主入口：执行完整的关键词生成 → 处理 → 判别 → 保存流程。

    Args:
        resume: 是否从断点继续（跳过生成阶段）
        dry_run: 仅显示任务规模和成本预估，不实际执行
    """
    if not API_KEY:
        print("❌ 错误: API Key 未配置。请设置环境变量 YUNWU_API_KEY")
        return

    # 输入验证
    if not MODELS:
        print("❌ 错误: MODELS 列表为空")
        return
    if not JUDGE_MODELS:
        print("❌ 错误: JUDGE_MODELS 列表为空")
        return
    if not DOMAINS:
        print("❌ 错误: DOMAINS 列表为空")
        return

    logger = setup_logger()
    start_time = time.time()
    # client_config 现在按模型动态获取，见下方任务构建处

    # Dry-run 模式：仅显示任务规模和预估信息
    gen_task_count = len(MODELS) * len(DOMAINS) * NUM_REPEAT_PER_MODEL
    if dry_run:
        logger.info("=" * 60)
        logger.info("📊 Dry-Run 模式：任务规模预估")
        logger.info("=" * 60)
        logger.info(f"  生成模型数: {len(MODELS)}")
        logger.info(f"  判别模型数: {len(JUDGE_MODELS)}")
        logger.info(f"  领域数: {len(DOMAINS)}")
        logger.info(f"  每模型重复次数: {NUM_REPEAT_PER_MODEL}")
        logger.info(f"  生成阶段总任务数: {gen_task_count}")
        logger.info(f"  生成并发数: {MAX_WORKERS_GENERATE}")
        logger.info(f"  判别批次大小: {JUDGE_BATCH_SIZE}")
        logger.info(f"  判别并发数: {MAX_WORKERS_JUDGE}")
        logger.info(f"  单次超时: {REQUEST_TIMEOUT}s")
        logger.info(f"  全局重试上限: {MAX_TOTAL_RETRIES}")
        logger.info(f"  模型失败跳过阈值: {MODEL_FAIL_THRESHOLD}")
        est_minutes = gen_task_count * 15 / MAX_WORKERS_GENERATE / 60
        logger.info(f"  预估生成阶段耗时: ~{est_minutes:.0f} 分钟 (假设平均 15s/任务)")
        logger.info("=" * 60)
        logger.info("提示: 去掉 --dry-run 参数即可正式执行")
        return

    # ====================================================================
    # 第一阶段：生成关键词（或从断点恢复）
    # ====================================================================
    if resume:
        checkpoint = _load_checkpoint()
        if checkpoint is None:
            logger.error("未找到断点文件，无法继续。请先完整运行一次。")
            return
        logger.info(f"✅ 从断点恢复 (保存时间: {checkpoint['timestamp']})")
        dom_keywords = checkpoint["dom_keywords"]
        all_keywords = checkpoint["all_keywords"]
        all_records = checkpoint["all_records"]
        keywords_raw_count = checkpoint["keywords_raw_count"]
        unique_keywords = checkpoint["unique_keywords"]
        simplified_keywords = checkpoint["simplified_keywords"]
    else:
        # 检查生成阶段断点
        gen_checkpoint = _load_gen_checkpoint()
        completed_task_ids = set()
        
        if gen_checkpoint:
            logger.info(f"✅ 从生成阶段中间断点恢复 (保存时间: {gen_checkpoint['timestamp']})")
            dom_keywords = gen_checkpoint["dom_keywords"]
            all_keywords = gen_checkpoint["all_keywords"]
            all_records = gen_checkpoint["all_records"]
            keywords_raw_count = gen_checkpoint["keywords_raw_count"]
            completed_task_ids = set(gen_checkpoint.get("completed_task_ids", []))
            
            # 确保各领域的 key 都存在
            for dom in DOMAINS:
                if dom["name"] not in dom_keywords:
                    dom_keywords[dom["name"]] = []
        else:
            # 按领域收集结果
            dom_keywords: Dict[str, List[str]] = {dom["name"]: [] for dom in DOMAINS}
            all_keywords: List[str] = []
            all_records: List[Dict[str, str]] = []
            keywords_raw_count = 0

        # 构建所有任务: 模型 × 领域 × 重复次数
        tasks = []
        for model in MODELS:
            for dom in DOMAINS:
                prompt = build_generate_prompt(dom)
                for i in range(NUM_REPEAT_PER_MODEL):
                    task_uid = f"{model}::{dom['name']}::{i}"
                    if task_uid not in completed_task_ids:
                        tasks.append((model, dom["name"], prompt, i, get_client_config(model)))

        if not tasks and completed_task_ids:
            logger.info("  ✅ 所有生成任务已完成，跳过并发执行阶段。")
        else:
            # 随机打乱任务顺序，避免同一模型的请求扎堆导致限流
            random.shuffle(tasks)

            total_tasks = len(tasks)
            completed_str = f" (已完成 {len(completed_task_ids)} 个，剩余 {total_tasks} 个)" if completed_task_ids else ""
            logger.info(
                f"--- 开始并行执行: {len(MODELS)} 个模型 × {len(DOMAINS)} 个领域 "
                f"× {NUM_REPEAT_PER_MODEL} 次 = {len(MODELS)*len(DOMAINS)*NUM_REPEAT_PER_MODEL} 个总量{completed_str} ---"
            )

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_GENERATE) as executor:
                futures = [executor.submit(fetch_batch, task) for task in tasks]

                completed = 0
                for future in concurrent.futures.as_completed(futures):
                    if _shutdown_event.is_set():
                        logger.warning("中断信号已设置，准备保存当前生成断点并退出...")
                        _save_gen_checkpoint(
                            dom_keywords, all_keywords, all_records,
                            keywords_raw_count, list(completed_task_ids)
                        )
                        break

                    gen_model, dom_name, res, idx = future.result()
                    completed += 1
                    task_uid = f"{gen_model}::{dom_name}::{idx}"
                    completed_task_ids.add(task_uid)

                    if res:
                        dom_keywords[dom_name].extend(res)
                        all_keywords.extend(res)
                        keywords_raw_count += len(res)
                        for kw in res:
                            all_records.append({"domain": dom_name, "keyword": kw, "model": gen_model})

                    # 进度汇报 + 定期保存断点
                    if completed % 10 == 0 or completed == total_tasks:
                        logger.info(
                            f"  📊 生成进度: {completed}/{total_tasks} "
                            f"({completed / total_tasks * 100:.0f}%), "
                            f"已收集 {keywords_raw_count} 个词"
                        )
                        _save_gen_checkpoint(
                            dom_keywords, all_keywords, all_records,
                            keywords_raw_count, list(completed_task_ids)
                        )

        if _shutdown_event.is_set():
            logger.warning("⚠️ 因中断信号提前结束生成阶段，已保存已有结果。")

        if not all_keywords:
            logger.error("未获取到任何数据")
            return

        # 清洗关键词
        all_keywords = _clean_keywords(all_keywords)

        # 去重
        unique_keywords = sorted(set(all_keywords))

        # 词根精简
        simplified_keywords = _simplify_keywords(unique_keywords)

        # 保存断点
        _save_checkpoint(
            dom_keywords, all_keywords, all_records,
            keywords_raw_count, unique_keywords, simplified_keywords,
        )
        logger.info(f"✅ 生成阶段完成，已保存断点到 {CHECKPOINT_FILE}")

    gen_duration = time.time() - start_time

    # ====================================================================
    # 数据处理步骤
    # ====================================================================

    # ====== 步骤 1: 原始汇总（含重复） ======
    total_generated = keywords_raw_count
    # 从 all_records 提取 model 信息，与 all_keywords 对齐
    all_models = [r.get("model", "") for r in all_records] if all_records else [""] * len(all_keywords)
    df_step1 = pd.DataFrame({
        "id": range(1, len(all_keywords) + 1),
        "keyword": all_keywords,
        "model": all_models[:len(all_keywords)],
    })

    # 带领域标签的原始词表
    df_step1b = pd.DataFrame(all_records)
    df_step1b.insert(0, "id", range(1, len(df_step1b) + 1))

    # ====== 步骤 2: 去重 ======
    df_step2 = pd.DataFrame({"id": range(1, len(unique_keywords) + 1), "keyword": unique_keywords})

    # ====== 步骤 3: 词根精简 ======
    df_step3 = pd.DataFrame({
        "id": range(1, len(simplified_keywords) + 1),
        "keyword": simplified_keywords,
    })

    # ====== 步骤 4: 拼音排序 ======
    simplified_keywords_sorted = sorted(simplified_keywords, key=lambda x: lazy_pinyin(x))
    df_step4 = pd.DataFrame({
        "id": range(1, len(simplified_keywords_sorted) + 1),
        "keyword": simplified_keywords_sorted,
    })

    final_count = len(simplified_keywords_sorted)

    # ====================================================================
    # 第二阶段：模型批量判别
    # ====================================================================
    if _shutdown_event.is_set():
        logger.warning("⚠️ 因中断信号跳过判别阶段，直接保存中间结果")
    else:
        logger.info(
            f"--- 开始批量判别 (共 {final_count} 个词, "
            f"每批 {JUDGE_BATCH_SIZE} 个, {len(JUDGE_MODELS)} 个模型) ---"
        )

    judge_start_time = time.time()

    kw_list = df_step4["keyword"].tolist()
    batches = [kw_list[i:i + JUDGE_BATCH_SIZE] for i in range(0, len(kw_list), JUDGE_BATCH_SIZE)]
    logger.info(f"  共 {len(batches)} 个批次")

    # 构建判别任务: 模型 × 批次
    judge_tasks = []
    for model in JUDGE_MODELS:
        for bi, batch in enumerate(batches):
            judge_tasks.append((model, batch, bi, get_client_config(model)))

    # 随机打乱判别任务
    random.shuffle(judge_tasks)
    logger.info(f"  总判别请求数: {len(judge_tasks)} 次")

    # 收集判别结果: {model: {keyword: [score, reason]}}
    model_results: Dict[str, Dict[str, List[Any]]] = {m: {} for m in JUDGE_MODELS}

    # 尝试加载判别阶段断点
    judge_cp = _load_judge_checkpoint()
    if judge_cp and resume:
        logger.info(f"✅ 从判别断点恢复 ({judge_cp['completed_tasks']}/{judge_cp['total_tasks']} 已完成)")
        model_results = judge_cp["model_results"]
        # 确保所有判别模型都有 key
        for m in JUDGE_MODELS:
            if m not in model_results:
                model_results[m] = {}
        
        # 过滤已完成的判别任务
        pending_tasks = []
        for t in judge_tasks:
            m_name, m_batch, _, _ = t
            # 若 batch 中的词都已经被该模型判别过，则跳过
            if all(kw in model_results.get(m_name, {}) for kw in m_batch):
                pass
            else:
                pending_tasks.append(t)
        
        if len(pending_tasks) < len(judge_tasks):
            logger.info(f"  ⏭️ 根据断点，跳过了 {len(judge_tasks) - len(pending_tasks)} 个批量判别任务，剩余 {len(pending_tasks)} 个待执行。")
        judge_tasks = pending_tasks

    if not _shutdown_event.is_set():
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_JUDGE) as executor:
            futures = [executor.submit(judge_batch, t) for t in judge_tasks]
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                if _shutdown_event.is_set():
                    logger.warning("中断信号已设置，保存判别进度后退出...")
                    _save_judge_checkpoint(model_results, completed, len(judge_tasks))
                    break
                model_name, batch_results = future.result()
                for kw, score, reason in batch_results:
                    model_results[model_name][kw] = [score, reason]
                completed += 1
                # 进度汇报 + 定期保存判别断点
                if completed % 5 == 0 or completed == len(judge_tasks):
                    pct = completed / len(judge_tasks) * 100 if len(judge_tasks) > 0 else 100
                    logger.info(f"  📊 判别进度: {completed}/{len(judge_tasks)} ({pct:.0f}%)")
                    _save_judge_checkpoint(model_results, completed, len(judge_tasks))

    # 汇报被跳过的模型
    skipped = _model_health.get_skipped()
    if skipped:
        logger.warning(f"  ⚠️ 以下模型因连续失败被自动跳过: {', '.join(skipped)}")

    logger.info("判别完成，正在整理结果...")
    judge_duration = time.time() - judge_start_time

    # ====================================================================
    # 构建判别结果 DataFrame
    # ====================================================================
    judge_rows = []
    for kw in kw_list:
        row: Dict[str, Any] = {"keyword": kw}
        total = 0
        for model in JUDGE_MODELS:
            key = model.replace(".", "_").replace("-", "_")
            res = model_results[model].get(kw, [0, ""])
            if isinstance(res, (int, float)):
                score = int(res)
                reason = ""
            else:
                score = int(res[0])
                reason = str(res[1]) if len(res) > 1 else ""
            row[f"{key}_score"] = score
            row[f"{key}_reason"] = reason
            total += score
        row["total_score"] = total
        judge_rows.append(row)

    df_judged = pd.DataFrame(judge_rows)

    # 合并 ID
    df_final = pd.merge(df_step4, df_judged, on="keyword", how="left")

    # 调整列顺序: id, keyword, total_score, 各模型 score 和 reason
    ordered_cols = ["id", "keyword", "total_score"]
    for model in JUDGE_MODELS:
        key = model.replace(".", "_").replace("-", "_")
        ordered_cols.append(f"{key}_score")
        ordered_cols.append(f"{key}_reason")
    ordered_cols += [c for c in df_final.columns if c not in ordered_cols]
    df_final = df_final[ordered_cols]

    # 按 total_score 降序排序
    df_final = df_final.sort_values(by="total_score", ascending=False).reset_index(drop=True)
    df_final["id"] = range(1, len(df_final) + 1)

    # ====================================================================
    # 汇总保存
    # ====================================================================
    simplified_set = set(simplified_keywords)
    final_kw_set = set(kw_list)
    judge_ok_set = set(
        df_final[df_final["total_score"] >= len(JUDGE_MODELS) * 0.5]["keyword"]
    )

    # 构建统计总览
    stats_rows = []
    for dom in DOMAINS:
        dom_name = dom["name"]
        dom_raw = dom_keywords.get(dom_name, [])
        dom_set = set(dom_raw)
        stats_rows.append({
            "领域": dom_name,
            "原始": len(dom_raw),
            "去重": len(dom_set),
            "精简": len(dom_set & simplified_set),
            "最终": len(dom_set & final_kw_set),
            "AI认可": len(dom_set & judge_ok_set),
        })
    stats_rows.append({
        "领域": "【汇总】",
        "原始": total_generated,
        "去重": len(unique_keywords),
        "精简": final_count,
        "最终": final_count,
        "AI认可": len(judge_ok_set),
    })
    df_stats = pd.DataFrame(stats_rows)

    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(str(OUTPUT_FILE), engine="openpyxl") as writer:
            # 主要 Sheet
            df_stats.to_excel(writer, sheet_name="银行关键词统计", index=False)
            df_step1.to_excel(writer, sheet_name="1-原始汇总", index=False)
            df_step1b.to_excel(writer, sheet_name="1b-按领域原始", index=False)
            df_step2.to_excel(writer, sheet_name="2-去重后", index=False)
            df_step3.to_excel(writer, sheet_name="3-词根精简后", index=False)
            df_step4.to_excel(writer, sheet_name="4-最终结果", index=False)
            df_final.to_excel(writer, sheet_name="5-AI判别结果", index=False)

            # 各领域独立 Sheet
            for dom in DOMAINS:
                dom_name = dom["name"]
                dom_raw = dom_keywords.get(dom_name, [])
                dom_raw = _clean_keywords(dom_raw)
                dom_set = set(dom_raw)
                if not dom_raw:
                    continue

                # 原始（含重复）
                df_raw = pd.DataFrame({"id": range(1, len(dom_raw) + 1), "keyword": dom_raw})
                writer_sheet = f"原始-{dom_name}"[:31]
                df_raw.to_excel(writer, sheet_name=writer_sheet, index=False)

                # 去重后
                dom_unique = sorted(dom_set)
                df_dom = pd.DataFrame({"id": range(1, len(dom_unique) + 1), "keyword": dom_unique})
                writer_sheet = f"去重-{dom_name}"[:31]
                df_dom.to_excel(writer, sheet_name=writer_sheet, index=False)

                # 词根精简后
                dom_simplified = sorted(kw for kw in dom_set if kw in simplified_set)
                if dom_simplified:
                    df_s = pd.DataFrame({"id": range(1, len(dom_simplified) + 1), "keyword": dom_simplified})
                    writer_sheet = f"精简-{dom_name}"[:31]
                    df_s.to_excel(writer, sheet_name=writer_sheet, index=False)

                # 最终结果（拼音排序）
                dom_final = sorted(
                    (kw for kw in dom_set if kw in final_kw_set),
                    key=lambda x: lazy_pinyin(x),
                )
                if dom_final:
                    df_f = pd.DataFrame({"id": range(1, len(dom_final) + 1), "keyword": dom_final})
                    writer_sheet = f"最终-{dom_name}"[:31]
                    df_f.to_excel(writer, sheet_name=writer_sheet, index=False)

                # AI 判别结果（含得分）
                dom_judged = df_final[df_final["keyword"].isin(dom_set)].copy()
                if not dom_judged.empty:
                    dom_judged = dom_judged.sort_values(
                        by="total_score", ascending=False
                    ).reset_index(drop=True)
                    dom_judged["id"] = range(1, len(dom_judged) + 1)
                    writer_sheet = f"判别-{dom_name}"[:31]
                    dom_judged.to_excel(writer, sheet_name=writer_sheet, index=False)

        logger.info(f"  [汇总] 所有步骤及判别结果已保存 -> {OUTPUT_FILE}")
        # Excel 专业格式化
        _format_excel_workbook(OUTPUT_FILE)
        logger.info("✅ Excel 格式化完成（冻结首行/自动列宽/表头样式/条件格式）")
        # 保存成功后删除断点文件
        _delete_checkpoint()
    except Exception as e:
        logger.error(f"汇总保存失败: {e}")
        bk_file = f"bank_keywords_{int(time.time())}.xlsx"
        df_final.to_excel(bk_file, index=False)
        logger.info(f"已保存到备份: {bk_file}")
        return

    # ====================================================================
    # 最终统计输出
    # ====================================================================
    duration = time.time() - start_time
    logger.info("--- 任务完成 ---")
    logger.info(f"生成耗时: {gen_duration:.1f}s | 判别耗时: {judge_duration:.1f}s | 总耗时: {duration:.1f}s")
    logger.info(f"领域数量: {len(DOMAINS)}")
    logger.info(
        f"生成词数: {total_generated} → 去重: {len(unique_keywords)} → 精简: {final_count}"
    )
    if _total_retry_count > 0:
        logger.info(f"全局重试总次数: {_total_retry_count}")

    # 判别统计
    score_counts = df_final["total_score"].value_counts().sort_index(ascending=False)
    logger.info("AI判别统计 (total_score 分布):")
    for sc, cnt in score_counts.items():
        logger.info(f"  得分 {sc}: {cnt} 个词")

    logger.info("各领域统计:")
    logger.info(
        f"  {'领域名称':<16s} {'原始':>6s} {'去重':>6s} "
        f"{'精简':>6s} {'最终':>6s} {'AI认可':>6s}"
    )
    logger.info(f"  {'-' * 16} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6}")
    for dom in DOMAINS:
        dom_name = dom["name"]
        dom_raw = dom_keywords.get(dom_name, [])
        dom_set = set(dom_raw)
        n_raw = len(dom_raw)
        n_uniq = len(dom_set)
        n_simp = len(dom_set & simplified_set)
        n_final = len(dom_set & final_kw_set)
        n_ai = len(dom_set & judge_ok_set)
        logger.info(
            f"  {dom_name:<16s} {n_raw:>6d} {n_uniq:>6d} "
            f"{n_simp:>6d} {n_final:>6d} {n_ai:>6d}"
        )
    logger.info(f"结果已保存至: {OUTPUT_FILE}")


# ════════════════════════════════════════════════════════════════
# 入口
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="银行领域关键词生成与判别工具")
    parser.add_argument("--view-logs", action="store_true", help="列出所有历史运行日志")
    parser.add_argument(
        "--view-log", type=str, metavar="NAME", help="查看指定日志 (文件名或 latest)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="从断点继续（跳过生成阶段，直接进入判别）",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅显示任务规模和成本预估，不实际执行",
    )
    args = parser.parse_args()

    if args.view_logs:
        view_logs()
    elif args.view_log:
        view_log(args.view_log)
    else:
        main(resume=args.resume, dry_run=args.dry_run)
