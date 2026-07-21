"""
银行领域关键词生成与判别工具

功能：
    1. 使用多个 LLM 模型并行生成银行领域关键词
    2. 去重 → 去数字字母 → 词根精简 → 拼音排序
    3. 使用顶级模型批量判别每个关键词的专业度
    4. 汇总保存为多 Sheet 的 Excel 文件

用法：
    python LLMs_for_dic/LLMs_for_dic.py                  # 运行完整流程
    python LLMs_for_dic/LLMs_for_dic.py --view-logs       # 列出当前日志文件
    python LLMs_for_dic/LLMs_for_dic.py --view-log latest # 查看最新运行日志
"""

# === 标准库 ===
import argparse
import concurrent.futures
import hashlib
import json
import logging
import os
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
    DATA_DIR,
    DOMAINS,
    JUDGE_BATCH_SIZE,
    JUDGE_MODELS,
    LOG_DIR,
    MAX_RETRIES,
    MAX_TOTAL_RETRIES,
    MAX_WORKERS_GENERATE,
    MAX_WORKERS_JUDGE,
    MAX_PARSE_RETRIES,
    MAX_JUDGE_RETRIES,
    MAX_CONCURRENT_PER_MODEL,
    MAX_OUTPUT_TOKENS,
    MODEL_FAIL_THRESHOLD,
    MODELS,
    NUM_JUDGE_REPS,
    JUDGE_REP_MAJORITY,
    NUM_REPEAT_PER_MODEL,
    SAMPLING_PARAM_FILTERED_MODELS,
    REQUEST_TIMEOUT,
    SCRIPT_DIR,
    get_client_config,
    get_model_params,
    build_generate_prompt,
    build_judge_prompt,
    reason_text_from_index,
    CACHE_DB_FILE,
    CACHE_ENABLED,
    OFFLINE_MODE,
)
from llm_cache import LLMCache, LLMCacheMissError
# 学术化日志支撑 (四位有效数字格式化 + 经核验 APA 参考文献注册表; 详见 academic.py)
from academic import sig4, pct4, cite, references_block

# 目录级独立 LLM 缓存（LLMS_DIC_CACHE=0 可停用；LLMS_DIC_OFFLINE=1 为 $0 离线重放）
_llm_cache: Optional[LLMCache] = LLMCache(CACHE_DB_FILE) if CACHE_ENABLED else None

# 零温例外披露去重集（每模型每次运行仅记一次 WARNING；GIL 下 add 原子，并发下极端
# 情况最多重复一条日志，无正确性影响——见 _call_llm_with_retry 内披露块）
_sampling_filter_logged: set = set()

# 配置冲突守卫: 离线守卫依赖缓存, CACHE=0 + OFFLINE=1 会让离线承诺 fail-open
# (静默直连付费 API), 拒绝启动
if OFFLINE_MODE and _llm_cache is None:
    raise SystemExit(
        "[配置冲突] LLMS_DIC_OFFLINE=1 (离线重放) 与 LLMS_DIC_CACHE=0 (缓存停用) 不可同设: "
        "离线守卫依赖缓存, 该组合会静默直连付费 API。请去掉其中一个环境变量。"
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
    """初始化日志系统：同时输出到控制台和日志文件。

    日志文件名固定为「同 py 文件名」（``00_LLMs_for_dic.log``），文件 Handler
    以 ``mode="w"`` 覆盖写入 —— 每次运行只保留最近一次日志，不再滚动累积。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 日志文件名 = 脚本名（同 py 文件名），每次运行覆盖，只留最近一次
    log_filepath = LOG_DIR / f"{Path(__file__).stem}.log"

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

    # 文件 Handler（mode="w" 覆盖写入，只保留最近一次运行日志）
    fh = logging.FileHandler(str(log_filepath), mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(f"日志文件: {log_filepath}")
    return logger


def view_logs() -> None:
    """列出当前日志文件（每脚本仅保留最近一次，文件名同 py 文件名）。"""
    if not LOG_DIR.exists():
        print("暂无运行日志。")
        return
    files = sorted(f for f in LOG_DIR.iterdir() if f.suffix == ".log")
    if not files:
        print("暂无运行日志。")
        return
    print(f"\n{'=' * 60}")
    print(f"  当前日志文件 (共 {len(files)} 个)")
    print(f"  目录: {LOG_DIR.resolve()}")
    print(f"{'=' * 60}")
    for i, fp in enumerate(files, 1):
        size = fp.stat().st_size
        mtime = datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_str = f"{sig4(size / 1024)}KB" if size >= 1024 else f"{size}B"
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
        # 主运行日志固定名 = 脚本名；缺失时回退到按名排序末位
        main_log = f"{Path(__file__).stem}.log"
        target = main_log if main_log in files else files[-1]
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
# 学术化运行头 / 尾部参考文献块
# ════════════════════════════════════════════════════════════════
# 本轮日志所引全部文献的 handle 集合（footer 由 academic.references_block 渲染为
# APA 全表）。每个 handle 均对应 academic.REFERENCES 中一条经核验、逐字誊抄自手稿
# §6 书目的条目——严禁在日志中出现注册表之外的引文。
_RUN_CITED_HANDLES = [
    # 方法学根基：金融文本量化 / 专属词典
    "gentzkow_2019", "loughran_2011", "tetlock_2007", "tetlock_2008",
    "garcia_2023", "kearney_2014",
    # 金融科技领域界定与银行数字化测度
    "gomber_2018", "thakor_2020", "cheng_2020", "goldstein_2021",
    # 设计原理：群体智能 / 集成学习（多样性聚合胜过单一最强模型）
    "galton_1907", "hong_2004", "dietterich_2000", "breiman_2001", "wang_2022",
    # 阶段一：种子引导并发生成（默认温度采样，无梯度微调）
    "brown_2020", "dekok_2025",
    # 阶段二：集合规约（无监督扩容的过度映射/假阳性问题）
    "blei_2003", "hanley_2019", "li_2021",
    # 阶段三：LLM-as-a-Judge 群体盲审（零温；模型内三轮 self-consistency 多数 +
    # 模型间严格过半数；判别端凝缩型 CoT 约束）
    # 含 LLM-as-annotator / LLM-as-judge 综述 / 幻觉综述（交叉盲审的动因）
    "zheng_2023", "liu_2023", "gu_2024", "gilardi_2023", "ouyang_2022",
    "bernard_2026", "gopal_2025", "wei_2022", "ji_2023",
    # 验证：评分者间一致性——Fleiss' Kappa（双口径披露）+ 一致性系数族（Cohen κ / Krippendorff α / Gwet AC1）
    "fleiss_1971", "landis_1977", "mchugh_2012", "cohen_1960", "hayes_2007", "gwet_2008",
]


def _log_run_header(logger: logging.Logger) -> None:
    """在运行开始处输出学术化项目信息 + 方法学 + 数据 I/O + 配置快照。

    仅陈述本管道的客观设计与运行时配置（读 config 动态值），并以 in-text 引用
    锚定方法学依据；不预告任何尚未产生的结果，避免过度声明。
    """
    bar = "═" * 78
    logger.info(bar)
    logger.info("LLMs_for_FinTech_dic ─ 基于大语言模型群体智能的金融科技领域词典构建管道")
    logger.info(bar)
    # ── 项目信息 / 方法学 ──────────────────────────────────────────
    logger.info("【项目信息 Project】面向商业银行「金融科技」垂直领域，构建可复现的高信噪比")
    logger.info("  特征词典，用于大规模非结构化金融文本的软信息量化测度 "
                + cite("gentzkow_2019", "loughran_2011", "tetlock_2008", "kearney_2014"))
    logger.info("  动因：专家先验种子词典存在选择性偏差与更新时滞，无监督向量/主题扩容又易")
    logger.info("  因语境共现引入偏离金融因果逻辑的假阳性噪声 "
                + cite("tetlock_2007", "hanley_2019", "li_2021", "garcia_2023"))
    logger.info("  领域界定与银行数字化测度锚定金融科技实证文献 "
                + cite("gomber_2018", "thakor_2020", "cheng_2020", "goldstein_2021"))
    logger.info("【方法学 Method】三阶段全自动构建工作流（无人工在环），另附一致性验证：")
    logger.info("  ◆ 设计原理（群体智能 Swarm Intelligence）：以多异构模型的多样性聚合替代单一模型——")
    logger.info("     群体智慧与集成学习理论表明，足够多样的评委/学习器聚合可胜过任一单个最强者，"
                "其 LLM 原生对应即多路采样多数投票（self-consistency） "
                + cite("galton_1907", "hong_2004", "dietterich_2000", "breiman_2001", "wang_2022"))
    logger.info("  ① 种子引导并发生成（Seed-guided Concurrency Generation，无梯度微调）：各异构基座模型")
    logger.info("     在默认温度下、以领域种子词与格式示范为条件并发重复采样，以查全率/特征分布探测为目标 "
                + cite("brown_2020", "dekok_2025"))
    logger.info("  ② 集合迭代精简（Set-based Reduction）：Unicode NFKC 规范化 + 哈希去重 + 超子串")
    logger.info("     包容剔除算子，收敛为正交原子词根，抑制派生词重复计量 "
                + cite("blei_2003", "hanley_2019", "li_2021"))
    logger.info(f"  ③ 机器交叉盲审（LLM-as-a-Judge Swarm，零温 T=0）：多模型各 {NUM_JUDGE_REPS} 轮独立背靠背评分，")
    logger.info(f"     双层多数投票——模型内 ≥{JUDGE_REP_MAJORITY}/{NUM_JUDGE_REPS} 轮多数（self-consistency）聚成正式票，"
                "模型间按严格过半数（strict majority，需 > 1/2 家模型认可）截断，判别端施加凝缩型思维链（CoT）约束、"
                "削减单体模型偏误与幻觉、分离弱共识噪声（大模型作评判者/标注员的一致性与幻觉动因） "
                + cite("wang_2022", "zheng_2023", "gu_2024", "gilardi_2023", "liu_2023", "ouyang_2022",
                       "bernard_2026", "wei_2022", "ji_2023"))
    # ⚠ 零温例外披露（动态：仅当判别名单含采样参数受限模型时输出；详见 config.py 常量处）
    _t0_filtered = [m for m in JUDGE_MODELS if m in SAMPLING_PARAM_FILTERED_MODELS]
    if _t0_filtered:
        logger.info(f"     ⚠ 零温例外披露：{' / '.join(_t0_filtered)}（属 claude-opus-4.7+）官方 API 不支持自定义")
        logger.info("       temperature/top_p/top_k——该限制非单独「废弃政策」公告，而是新模型技术规格随模型发布")
        logger.info("       同步生效；yunwu 中转自 2026-07-10 00:00 起对其静默过滤（不报错、照常返回）→ 零温 T=0")
        logger.info(f"       对该 {len(_t0_filtered)} 家不生效（实际按模型默认温度采样），其判别票可复现性由冻结 LLM 缓存")
        logger.info('       保证（缓存键仍含 temperature="0"），属缓存冻结级而非 API 级确定性')
    logger.info("  ◇ 验证（Validation，非流水线阶段）：Fleiss' Kappa 评分者间一致性，Landis-Koch 与 McHugh 双口径分级披露；"
                "并锚定一致性系数族（Cohen κ / Krippendorff α / Gwet AC1）以佐证效度 "
                + cite("fleiss_1971", "landis_1977", "mchugh_2012", "cohen_1960", "hayes_2007", "gwet_2008"))
    # ── 数据 I/O ──────────────────────────────────────────────────
    logger.info("【数据 I/O】输入：Prompt 驱动（无外部原始语料，词汇源自模型预训练知识图谱）；")
    logger.info(f"  产物 Excel（多 Sheet，含逐步中间态与判别结果）→ {OUTPUT_FILE}")
    _cache_desc = (f"启用 · {CACHE_DB_FILE}" if CACHE_ENABLED else "停用（直连 API）")
    logger.info(f"  目录级独立 LLM 缓存：{_cache_desc}"
                + ("（离线重放 $0）" if OFFLINE_MODE else ""))
    # ── 配置快照（运行时动态值）──────────────────────────────────
    _gen_tasks = len(MODELS) * len(DOMAINS) * NUM_REPEAT_PER_MODEL
    logger.info("【配置快照 Config（运行时动态）】")
    logger.info(f"  生成模型 {len(MODELS)} 家 · 判别模型 {len(JUDGE_MODELS)} 家 × 每家 {NUM_JUDGE_REPS} 轮"
                f"（内部多数门 ≥{JUDGE_REP_MAJORITY}）· 领域 {len(DOMAINS)} 个 · "
                f"每模型重复 {NUM_REPEAT_PER_MODEL} 次 → 生成任务 {_gen_tasks} 个")
    logger.info(f"  判别批大小 {JUDGE_BATCH_SIZE} · 生成并发 {MAX_WORKERS_GENERATE} · 判别并发 {MAX_WORKERS_JUDGE} · "
                f"单次超时 {REQUEST_TIMEOUT}s · 全局重试上限 {MAX_TOTAL_RETRIES} · 失败跳过阈值 {MODEL_FAIL_THRESHOLD}")
    logger.info(bar)


def _log_run_references(logger: logging.Logger) -> None:
    """在运行结束处输出本轮日志引用的全部 APA 参考文献（经核验、逐字誊抄自手稿书目）。"""
    for line in references_block(_RUN_CITED_HANDLES):
        logger.info(line)


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


def _salvage_json_objects(text: str) -> List[dict]:
    """从**截断/畸形** JSON 文本中打捞所有括号配平、且能解析为 dict 的内层对象。

    专治部分模型（实测 kimi-k2.6）响应被输出上限截断、或前置自然语言（"用户要求
    生成…"）导致最外层 JSON 无法闭合的情形：`_safe_parse_json` 此时返回 {}（正则
    `\\{.*\\}` 在缺失收尾 `}` 时匹配失败），整条响应连同已生成的上百个完整词条一起
    被丢弃 → 触发大量无谓重试。本函数扫描文本，**跳过无法闭合的最外层容器**，逐个
    提取内层完整 `{...}` 叶子对象（如 {"keyword": "...", "reason": "..."}）。

    - 字符串感知：正确跳过字符串值内的花括号与转义，不被其误导括号深度。
    - 遇最外层包装（如 {"keywords": [...]}）：下潜一层继续逐对象打捞（而非整吞）。
    - 仅作为主解析失败后的兜底路径调用；happy-path（合法 JSON）不经此函数，零行为变更。
    """
    if not text:
        return []
    objects: List[dict] = []
    n = len(text)
    i = 0
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        # 从 i 处做「字符串感知」的括号配平，定位与之匹配的收尾 '}'
        depth = 0
        in_str = False
        esc = False
        end = -1
        j = i
        while j < n:
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
            j += 1
        if end == -1:
            # 从 i 起无法闭合（截断的外层 / 末尾半截对象）：跳过此 '{'，继续找下一个内层对象
            i += 1
            continue
        try:
            obj = json.loads(text[i:end + 1])
        except (json.JSONDecodeError, ValueError):
            obj = None
        if isinstance(obj, dict) and "keyword" in obj:
            objects.append(obj)
            i = end + 1  # 已消费该叶子对象，从其后继续扫描
        else:
            # 非叶子（外层包装 / 无 keyword 键）：仅前进一格，下潜到内层继续打捞（并避免死循环）
            i += 1
    return objects


# 推理模型 (reasoning/thinking) 思维链兜底打捞的触发阈值：单模型正常应产 ~200 词，
# 仅当 JSON 主解析 + 对象打捞合计仍远低于此（几乎颗粒无收）才启用思维链枚举打捞，
# 避免对「已成功输出大部分 JSON」的正常/半截响应做无谓的二次扫描。
_REASONING_SALVAGE_TRIGGER: int = 20

# 思维链「N. 候选词 (可选理由)」编号清单的单行匹配：数字序号 + 分隔符 + 单个无空白词根，
# 行尾仅允许一个可选括注 (如 "(2)")。行尾锚定 ($) 刻意排除英文分析散文
# (如 "1. Must contain exactly 200 terms")——其序号后是多词句子，不会整行匹配。
_THINK_ENUM_LINE_RE = re.compile(
    r"^\s*\d+\s*[.、)]\s*([^\s()（）]{2,20})\s*(?:[（(][^)）]*[)）])?\s*$"
)


def _salvage_reasoning_keywords(text: str) -> List[str]:
    """从推理 (reasoning/thinking) 模型的 <think> 思维链中打捞其枚举出的候选词。

    专治 MiniMax-M3 等推理模型：整段 <think> 思维链逐条编号列举 ~100 个候选词
    (并含二次复核)，输出预算 (max_tokens) 在收尾输出 JSON **之前**即被耗尽 →
    finish_reason=length，content 内根本没有可解析的 JSON (仅一段未闭合的思维链)。
    此时 `_safe_parse_json` 与 `_salvage_json_objects` 均近乎颗粒无收 (实测仅 3 词)。
    本函数改从思维链的「N. 候选词」编号清单直接回收该模型列举的候选词——生成阶段
    本就是过采样 (over-generation)，候选一律交由下游判别阶段 (LLM-as-judge) 过滤，
    故从思维链回收其枚举候选**等价于**其正常 JSON 产出，不引入方法学偏差，且纯文本
    处理不调用任何 API (离线重放确定可复现)。亦顺带兜底「模型直接返回 markdown 编号
    清单而非 JSON」的退化响应。

    - 优先扫描 <think> 区域 (含未闭合)；无 <think> 标签则退回全文以兼容裸思维链。
    - 行尾锚定的严格单行匹配，排除英文分析散文与破折号复核项 (非编号行)。
    - 按词去重保序；跨分节重启编号 (如 50+80+70) 因按词去重而天然正确。
    """
    if not text:
        return []
    m = re.search(r"<think>(.*?)(?:</think>|\Z)", text, re.DOTALL)
    region = m.group(1) if m else text
    seen: Set[str] = set()
    out: List[str] = []
    for line in region.splitlines():
        mm = _THINK_ENUM_LINE_RE.match(line)
        if not mm:
            continue
        kw = mm.group(1).strip("：:，,、。.·-—")
        # 至少含一个中日韩表意文字或拉丁字母，排除纯数字/符号噪声
        if not kw or not re.search(r"[一-鿿A-Za-z]", kw):
            continue
        if kw in seen:
            continue
        seen.add(kw)
        out.append(kw)
    return out


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
    cache_tag: str = "",
) -> Optional[str]:
    """
    带重试的 LLM 调用。统一处理缓存、重试逻辑、退避策略、中断检测和费用保护。

    Args:
        client: OpenAI 客户端
        model_name: 模型名称
        prompt: 提示词
        task_id: 任务标识（用于日志）
        logger: 日志记录器
        force_temperature: 强制使用的 temperature 值。
            None = 不传 temperature，使用模型默认值；
            数值 = 强制使用该 temperature（如 0 表示最大确定性）。
        cache_tag: 缓存键区分标签。同一 prompt 的多次刻意重复采样（生成阶段
            rep 序号）与解析失败重试（try 序号）必须传不同 tag，否则会被缓存
            折叠成同一个响应。

    Returns:
        LLM 返回的文本内容，失败返回 None
    """
    model_params = get_model_params(model_name)
    # 根据 force_temperature 参数决定是否传递 temperature
    if force_temperature is not None:
        model_params["temperature"] = force_temperature
    else:
        model_params.pop("temperature", None)

    # ⚠ 零温例外披露（每模型每次运行仅记一次 WARNING；缓存命中路径亦记录——披露同样
    # 适用于既有缓存响应的来源口径）：SAMPLING_PARAM_FILTERED_MODELS（claude-opus-4.7+）
    # 的 temperature/top_p/top_k 官方 API 不支持（技术规格随模型发布同步生效，非单独
    # 废弃公告），yunwu 自 2026-07-10 00:00 起静默过滤 → 注入的 temperature 不生效
    # （实际默认温度采样），确定性由冻结缓存保证（缓存键仍含 temperature="0"，刻意不改）。
    if (
        force_temperature is not None
        and model_name in SAMPLING_PARAM_FILTERED_MODELS
        and model_name not in _sampling_filter_logged
    ):
        _sampling_filter_logged.add(model_name)
        logger.warning(
            f"  [{task_id}] ⚠ 采样参数披露: {model_name} 属 claude-opus-4.7+，官方 API 不支持"
            f"自定义 temperature/top_p/top_k（技术规格随模型发布同步生效，非单独废弃公告；"
            f"yunwu 2026-07-10 起静默过滤）→ 注入的 temperature="
            f"{format(float(force_temperature), 'g')} 不生效（实际按模型默认温度采样），"
            '其判别票可复现性由冻结 LLM 缓存保证（缓存键仍含 temperature="0"）'
        )

    # ── 缓存前置检查：命中直接返回（$0，不占用信号量/重试预算） ──
    # 数字规范化: int 0 与 float 0.0 归一为 "0"，防止调用方类型漂移导致键分裂
    temp_key = (
        format(float(force_temperature), "g")
        if force_temperature is not None
        else "model-default"
    )
    if _llm_cache is not None:
        cached = _llm_cache.get(model_name, prompt, temp_key, cache_tag)
        if cached is not None:
            logger.debug(f"  [{task_id}] 缓存命中 ($0)")
            return cached
        if OFFLINE_MODE:
            raise LLMCacheMissError(
                f"[{task_id}] 离线模式 (LLMS_DIC_OFFLINE=1) 下缓存未命中 "
                f"(model={model_name}, tag={cache_tag})，拒绝调用付费 API"
            )

    consecutive_timeouts = 0
    # max_tokens 显式上限：抬高防止个别模型（如 kimi-k2.6 在 yunwu 默认上限偏低）把
    # 200 词对象数组截断成非法 JSON。极少数模型/端点若拒绝该参数，下方 except 会侦测
    # 到「max_tokens/max_completion_tokens」错误签名并**移除后重试**（graceful，绝不
    # 因新增参数把原本可用的模型打成失败）。
    use_max_tokens = isinstance(MAX_OUTPUT_TOKENS, int) and MAX_OUTPUT_TOKENS > 0

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
            if use_max_tokens:
                call_kwargs["max_tokens"] = MAX_OUTPUT_TOKENS
            # 使用模型信号量控制并发，防止触发 429 限流
            sem = _get_model_semaphore(model_name)
            sem.acquire()
            try:
                resp = client.chat.completions.create(**call_kwargs)
            finally:
                sem.release()
            choice = resp.choices[0]
            content = choice.message.content
            # 截断预警：finish_reason=length 表示响应因输出上限被硬截断（大概率非法 JSON）。
            # 仍照常缓存 + 返回，交由下游 _salvage_json_objects 尽力打捞已生成的完整对象；
            # 此处显式记 WARNING，令截断成为一眼可辨的诊断信号（而非神秘的解析失败）。
            if getattr(choice, "finish_reason", None) == "length":
                logger.warning(
                    f"  [{task_id}] ⚠ 响应因长度上限被截断 "
                    f"(finish_reason=length, max_tokens={MAX_OUTPUT_TOKENS if use_max_tokens else '模型默认'})，"
                    f"将尽力打捞已生成内容"
                )
            # 成功响应写入缓存（原样存，含后续可能解析失败的响应，保证重放可复现）
            if _llm_cache is not None and isinstance(content, str):
                _llm_cache.put(model_name, prompt, temp_key, cache_tag, content)
            return content

        except Exception as e:
            error_str = str(e)
            # 参数兼容守卫：个别模型/端点不接受 max_tokens（或要求 max_completion_tokens）。
            # 侦测到该签名即移除参数后立即重试（不占退避/全局重试预算），保证不因新增参数
            # 把原本可用的模型误伤为失败；移除后回退各模型默认上限（等同本次改动前的行为）。
            low = error_str.lower()
            if use_max_tokens and ("max_tokens" in low or "max_completion_tokens" in low):
                use_max_tokens = False
                logger.warning(
                    f"  [{task_id}] 模型拒绝 max_tokens 参数，已移除后重试: {error_str[:120]}"
                )
                continue
            # 参数兼容守卫（关思考）：个别端点/代理不接受 extra_body 里的 thinking 字段。
            # 侦测到即移除 extra_body 后立即重试（不占退避/全局重试预算），优雅降级为思考开启
            # + 思维链打捞兜底，绝不因新增参数把原本可用的模型（如 MiniMax-M3）打成硬失败。
            if model_params.get("extra_body") and "thinking" in low:
                model_params.pop("extra_body", None)
                logger.warning(
                    f"  [{task_id}] 端点拒绝 thinking(关思考) 参数，已移除后重试"
                    f"（回退思考开启，交思维链打捞兜底）: {error_str[:120]}"
                )
                continue
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
                    f"  [{task_id}] 连续超时{consecutive_timeouts}次，等待{sig4(wait)}s"
                )
            logger.debug(f"  [{task_id}] 等待 {sig4(wait)}s 后重试")
            time.sleep(wait)

    logger.error(f"  [{task_id}] 达到最大重试次数，任务失败")
    return None


# ════════════════════════════════════════════════════════════════
# 盲审可复现性审计（P1/P2, 2026-07-21 执行计划）
# ════════════════════════════════════════════════════════════════
# ⚠ 铁律：本审计设施只挂判别（盲审）阶段 judge_batch 及其后的纯读环节，
#   生成阶段 fetch_batch 零触碰（用户 2026-07-21 铁律「严禁动生成阶段」）。
# 结构：{"tasks": {(model, batch_idx, rep): {"attempts": [...], "outcome": str, ...}}}
#   - rep: 三轮 self-consistency 的轮序号 0..NUM_JUDGE_REPS-1；历史 v1 manifest
#     冻结重放（单轮 legacy tag 口径）传 None。同一 run 内 rep 恒同类型（全 int
#     或全 None），排序用 -1 代 None 防御性归一。
#   - attempts: 逐 try 记录 {try, key, cached_before, got_response}
#   - outcome:  full / partial_adopt / hard_fail / health_skip / shutdown / offline_miss
# 判决规则（_emit_replay_verdict）：
#   可复现 ⇔ 全部任务 outcome ∈ {full, partial_adopt}
#           ∧ 每个尝试过的 try 均有响应入缓存（got_response 全 True）
#           ∧ 聚合层全格覆盖（len(JUDGE_MODELS)×len(词表) 无缺格——堵 executor
#             break 丢弃已完成 future 的假阴性通路 G1b）
#   partial_adopt 单列声明：其重放确定性成立（同缓存响应→同解析路径→同部分采纳），
#   但存在"覆盖不足补 0"的口径须披露。
_replay_audit_lock = threading.Lock()
_replay_audit: Dict[Tuple[str, int, Optional[int]], Dict[str, Any]] = {}


def _rep_sort_key(task_key: Tuple[str, int, Optional[int]]) -> Tuple[str, int, int]:
    """审计任务键排序归一：rep=None（legacy 单轮）映射为 -1，防御 None 参与比较。"""
    model, bi, rep = task_key
    return (model, bi, -1 if rep is None else rep)


def _task_label(model: str, batch_idx: int, rep: Optional[int]) -> str:
    """人读任务标签：轮序号仅在三轮口径下展示（legacy 单轮与历史日志格式一致）。"""
    label = f"{model}/批次{batch_idx + 1}"
    return label if rep is None else f"{label}/轮{rep + 1}"

# 严格重放门（生产定稿跑用）：判决不通过即 SystemExit(1) 拒绝出结果；默认关。
STRICT_REPLAY: bool = os.environ.get("LLMS_DIC_STRICT_REPLAY", "").strip().lower() in {
    "1", "true", "yes", "on",
}


def _audit_task(model: str, batch_idx: int, rep: Optional[int]) -> Dict[str, Any]:
    """取（或惰性建）某判别任务的审计记录（线程安全）。rep=None 为 legacy 单轮口径。"""
    with _replay_audit_lock:
        rec = _replay_audit.get((model, batch_idx, rep))
        if rec is None:
            rec = {"attempts": [], "outcome": None, "consumed_try": None, "coverage": None}
            _replay_audit[(model, batch_idx, rep)] = rec
        return rec


def _audit_attempt(
    model: str, batch_idx: int, rep: Optional[int], attempt: int, key: str,
    cached_before: bool, got_response: bool,
) -> None:
    """记录一次判别 try：缓存键、调用前是否已有缓存（命中/新写判别）、是否拿到响应。"""
    rec = _audit_task(model, batch_idx, rep)
    with _replay_audit_lock:
        rec["attempts"].append({
            "try": attempt,
            "key": key,
            "cached_before": cached_before,
            "got_response": got_response,
        })


def _audit_outcome(
    model: str, batch_idx: int, rep: Optional[int], outcome: str,
    consumed_try: Optional[int] = None, coverage: Optional[float] = None,
) -> None:
    """记录判别任务终局（幂等：首个终局为准，防重试路径重复覆写）。"""
    rec = _audit_task(model, batch_idx, rep)
    with _replay_audit_lock:
        if rec["outcome"] is None:
            rec["outcome"] = outcome
            rec["consumed_try"] = consumed_try
            rec["coverage"] = coverage


def _emit_replay_verdict(
    kw_list: List[str],
    model_results: Dict[Tuple[str, Optional[int]], Dict[str, Any]],
    logger: logging.Logger,
    judge_models: Optional[List[str]] = None,
    n_judge_reps: Optional[int] = None,
) -> Dict[str, Any]:
    """盲审可复现性判决：计数器 + 全格覆盖对账，输出判决日志块并返回判决 dict。

    judge_models 缺省用当前 config 的 JUDGE_MODELS；--from-manifest 重放传入
    manifest 冻结名单（冻结重放语义：以首跑口径对账，不受 config 后续漂移影响）。
    n_judge_reps=None → legacy 单轮口径（v1 manifest 冻结重放，聚合键 rep=None，
    判决字段与改造前同构）；int → 三轮口径（全格 = 模型 × 词 × 轮）。
    """
    from collections import Counter

    _models = list(judge_models) if judge_models is not None else list(JUDGE_MODELS)
    _reps: List[Optional[int]] = [None] if n_judge_reps is None else list(range(n_judge_reps))
    outcome_counts: Counter = Counter()
    bad_tasks: List[str] = []
    no_response_attempts: List[str] = []
    with _replay_audit_lock:
        tasks_snapshot = {k: dict(v, attempts=list(v["attempts"])) for k, v in _replay_audit.items()}
    for (model, bi, rep), rec in sorted(tasks_snapshot.items(), key=lambda kv: _rep_sort_key(kv[0])):
        outcome = rec["outcome"] or "unknown"
        outcome_counts[outcome] += 1
        if outcome not in {"full", "partial_adopt"}:
            bad_tasks.append(f"{_task_label(model, bi, rep)}={outcome}")
        for att in rec["attempts"]:
            if not att["got_response"]:
                no_response_attempts.append(f"{_task_label(model, bi, rep)}/try{att['try']}")

    # 聚合层全格对账（G1b）：executor break 丢弃已完成 future → model_results 缺格补 0。
    # 三轮口径下全格 = 模型 × 词 × 轮（每轮独立一格；vote 由分数纯函数派生，不另计格）。
    expected_cells = len(_models) * len(kw_list) * len(_reps)
    actual_cells = sum(len(model_results.get((m, r), {})) for m in _models for r in _reps)
    missing_cells: List[str] = []
    if actual_cells != expected_cells:
        for m in _models:
            for r in _reps:
                cell_map = model_results.get((m, r), {})
                miss = [kw for kw in kw_list if kw not in cell_map]
                if miss:
                    _m_label = m if r is None else f"{m}/轮{r + 1}"
                    missing_cells.append(
                        f"{_m_label}: 缺 {len(miss)} 词 (如 {', '.join(miss[:3])} ...)"
                    )

    reproducible = (
        not bad_tasks
        and not no_response_attempts
        and actual_cells == expected_cells
        and outcome_counts.get("unknown", 0) == 0
    )

    logger.info("═" * 78)
    logger.info("--- 盲审可复现性判决 (Judge Replay Verdict) ---")
    logger.info(
        f"  任务终局分布: " + (", ".join(f"{k}={v}" for k, v in sorted(outcome_counts.items())) or "（无任务）")
    )
    logger.info(f"  聚合覆盖对账: {actual_cells}/{expected_cells} 格")
    if reproducible:
        logger.info("  ✅ 判决: 本次盲审可 $0 离线逐字节复现（0 降级、0 无响应 try、全格覆盖）")
        if outcome_counts.get("partial_adopt", 0) > 0:
            logger.warning(
                f"  ⚠ 口径声明: {outcome_counts['partial_adopt']} 个任务走部分采纳"
                "（重放确定性成立，但存在覆盖不足补 0，须在使用侧披露）"
            )
    else:
        logger.warning("  ⚠ 判决: 本次盲审不可 $0 离线复现，明细如下:")
        for item in bad_tasks[:20]:
            logger.warning(f"    - 降级任务: {item}")
        for item in no_response_attempts[:20]:
            logger.warning(f"    - 无响应 try（缓存空洞）: {item}")
        for item in missing_cells[:20]:
            logger.warning(f"    - 聚合缺格: {item}")
        n_more = max(0, len(bad_tasks) + len(no_response_attempts) + len(missing_cells) - 60)
        if n_more:
            logger.warning(f"    ...（另有 {n_more} 条从略，全量见 manifest）")
    logger.info("═" * 78)

    verdict = {
        "reproducible": reproducible,
        "outcome_counts": dict(outcome_counts),
        "expected_cells": expected_cells,
        "actual_cells": actual_cells,
        "bad_tasks": bad_tasks,
        "no_response_attempts": no_response_attempts,
        "missing_cells": missing_cells,
    }
    if n_judge_reps is not None:
        # 三轮口径专属字段；legacy（v1 冻结重放）不加，保持判决结构与改造前同构
        verdict["n_judge_reps"] = n_judge_reps
    if STRICT_REPLAY and not reproducible:
        logger.error(
            "[LLMS_DIC_STRICT_REPLAY=1] 判决不通过，拒绝产出结果（已付费响应均已入缓存，"
            "修复后重跑为 $0 重放）"
        )
        raise SystemExit(1)
    return verdict


def _wordlist_sha256(kw_list: List[str]) -> str:
    """冻结词表指纹：按当前顺序以 \\n 连接后取 sha256（顺序敏感——顺序决定批次切分）。"""
    return hashlib.sha256("\n".join(kw_list).encode("utf-8")).hexdigest()


def _write_judge_manifest(
    kw_list: List[str],
    verdict: Dict[str, Any],
    logger: logging.Logger,
    output_file: Path,
    judge_models: Optional[List[str]] = None,
    batch_size: Optional[int] = None,
    n_judge_reps: Optional[int] = None,
    rep_majority: Optional[int] = None,
) -> Optional[Path]:
    """盲审清单 manifest 落盘（P2）：复现凭证，供 verify_judge_cache_coverage.py 核验。

    rep_majority: 与 n_judge_reps 配套的模型内多数门。fix(评审A, 2026-07-21): 冻结
    重放须传 manifest 冻结值——否则活体 config 协议演进后, 重放新写的 manifest 会
    落盘 n_judge_reps=冻结值 + rep_majority=活体值 的自相矛盾存根。None 回退当前
    config 的 JUDGE_REP_MAJORITY（main 首跑口径）。

    n_judge_reps=None → legacy 单轮口径（v1 manifest 冻结重放产出），schema/v1、
    任务键 {model}|batch{bi}，与改造前逐字段同构（历史核验链不断）；
    int → 三轮口径，schema/v2、任务键 {model}|batch{bi}|rep{r}，并冻结投票协议参数
    （n_judge_reps / rep_majority / final_vote_threshold）进复现凭证。
    附加产物，不改动 xlsx 任何 sheet/列；写失败按 WARNING 降级（绝不因留存根失败
    丢掉已付费判别结果）。
    """
    import platform

    try:
        import pypinyin as _pypinyin
        _pypinyin_ver = getattr(_pypinyin, "__version__", "unknown")
    except Exception:  # pragma: no cover - 依赖缺失时留痕即可
        _pypinyin_ver = "unavailable"

    _models = list(judge_models) if judge_models is not None else list(JUDGE_MODELS)
    _bsize = batch_size if batch_size is not None else JUDGE_BATCH_SIZE
    ts = output_file.stem.replace("bank_keywords_", "").replace("judge_replay_", "")
    manifest_path = DATA_DIR / f"judge_manifest_{ts}.json"
    with _replay_audit_lock:
        tasks_out = {
            (f"{model}|batch{bi}" if rep is None else f"{model}|batch{bi}|rep{rep}"): {
                "attempts": list(rec["attempts"]),
                "outcome": rec["outcome"],
                "consumed_try": rec["consumed_try"],
                "coverage": rec["coverage"],
            }
            for (model, bi, rep), rec in sorted(
                _replay_audit.items(), key=lambda kv: _rep_sort_key(kv[0])
            )
        }
    manifest = {
        "schema": (
            "llmsdic-judge-manifest/v1" if n_judge_reps is None
            else "llmsdic-judge-manifest/v2"
        ),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "run_output_file": output_file.name,
        "offline_mode": OFFLINE_MODE,
        "cache_enabled": CACHE_ENABLED,
        "strict_replay": STRICT_REPLAY,
        "judge_models": _models,
        "judge_batch_size": _bsize,
        "max_judge_retries": MAX_JUDGE_RETRIES,
        "temperature": "0",
        "n_words": len(kw_list),
        "wordlist_sha256": _wordlist_sha256(kw_list),
        "wordlist": list(kw_list),
        "n_batches": (len(kw_list) + _bsize - 1) // _bsize,
        "tasks": tasks_out,
        "verdict": verdict,
        "env": {
            "python": platform.python_version(),
            "pypinyin": _pypinyin_ver,  # 未钉版；决定词表排序→批次切分→全部判别缓存键
            "pandas": pd.__version__,
        },
    }
    if n_judge_reps is not None:
        # v2 投票协议冻结（复现凭证完备性）：轮数 / 模型内多数门 / 模型间入选门槛
        manifest["n_judge_reps"] = n_judge_reps
        manifest["rep_majority"] = (
            JUDGE_REP_MAJORITY if rep_majority is None else int(rep_majority)
        )
        manifest["final_vote_threshold"] = {
            "rule": "total_score > n_models * 0.5",
            "n_models": len(_models),
            "min_votes": len(_models) // 2 + 1,
        }
    try:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(f"  [复现凭证] 盲审 manifest 已落盘 -> {manifest_path}")
        return manifest_path
    except Exception as e:
        logger.warning(f"  [复现凭证] manifest 写盘失败（判别结果不受影响）: {e}")
        return None


# ════════════════════════════════════════════════════════════════
# 核心任务函数
# ════════════════════════════════════════════════════════════════

def fetch_batch(args: Tuple) -> Tuple[str, str, List[str], int]:
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

        # cache_tag 带 rep 序号 + 解析重试序号：NUM_REPEAT_PER_MODEL 次刻意重复采样各占独立缓存槽位
        try:
            text = _call_llm_with_retry(
                client, model_name, prompt, f"任务 {task_id}", logger,
                cache_tag=f"gen|{dom_name}|rep{idx}|try{parse_attempt}",
            )
        except LLMCacheMissError as e:
            # 离线重放遇到首跑缓存空洞：置全局停止走优雅中断，
            # 不让异常炸穿 executor
            logger.error(f"  [任务 {task_id}] {e}")
            _shutdown_event.set()
            return (model_name, dom_name, [], idx)
        if text is None:
            return (model_name, dom_name, [], idx)

        logger.debug(f"  [任务 {task_id}] LLM 原始响应:\n{text}")
        data = _safe_parse_json(text)

        # 提取列表：优先按契约 Key "keywords" 精确取，无则回退遍历首个 list（兼容不同 key 名称）。
        # 元素三态兼容（build_generate_prompt 现要求对象数组，但需向后兼容旧缓存/退化响应）：
        #   - dict → 新契约 {"keyword","reason"}，只取 "keyword"（reason 仅生成端 CoT 约束，不落盘）
        #   - str  → 旧契约纯词表 / 模型退化返回裸字符串
        #   - list → 极少数模型把词拆成字符列表，扁平化收字符串
        result_list: List[str] = []
        if isinstance(data, dict):
            _kw = data.get("keywords")
            for v in ([_kw] if isinstance(_kw, list) else data.values()):
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            result_list.append(item)
                        elif isinstance(item, dict):
                            kw = item.get("keyword")
                            if isinstance(kw, str) and kw.strip():
                                result_list.append(kw)
                        elif isinstance(item, list):
                            result_list.extend(str(i) for i in item if isinstance(i, str))
                    break

        # 兜底打捞：主解析拿不到任何词，多因响应被输出上限截断成非法 JSON（外层未闭合）。
        # 逐个提取已生成的完整 {"keyword",...} 对象，避免把上百个有效词连同半截尾巴一起丢弃。
        if not result_list:
            for obj in _salvage_json_objects(text or ""):
                kw = obj.get("keyword")
                if isinstance(kw, str) and kw.strip():
                    result_list.append(kw)
            if result_list:
                logger.warning(
                    f"  [任务 {task_id}] 主解析失败，从截断/畸形响应打捞出 {len(result_list)} 个词"
                    f"（疑似 max_tokens 截断，已尽力恢复）"
                )

        # 兜底打捞②（推理模型专治）：主解析 + JSON 对象打捞合计仍严重不足时，多因
        # 推理 (reasoning/thinking) 模型整段 <think> 思维链耗尽 max_tokens、收尾 JSON
        # 尚未输出即被截断（实测 MiniMax-M3 仅打捞出 3 词）。改从思维链的「N. 候选词」
        # 编号清单直接回收其枚举出的候选（生成阶段本就过采样、交由判别阶段过滤，故等价
        # 于正常 JSON 产出）。取更充分者，且纯文本处理不调用 API（离线重放可复现）。
        if len(result_list) < _REASONING_SALVAGE_TRIGGER:
            reasoned = _salvage_reasoning_keywords(text or "")
            if len(reasoned) > len(result_list):
                result_list = reasoned
                logger.warning(
                    f"  [任务 {task_id}] JSON 解析/打捞均近乎失败，从思维链编号清单枚举"
                    f"打捞出 {len(result_list)} 个候选词"
                    f"（reasoning 模型输出被 max_tokens 截断或未按 JSON 契约输出，已尽力恢复）"
                )

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


def judge_batch(args: Tuple) -> Tuple[str, Optional[int], List[Tuple[str, int, str]]]:
    """
    批量判别任务：一次发送一批关键词给模型，获取判别得分及理由。

    Args:
        args: (model_name, keywords_batch, batch_idx, rep, client_config) 元组。
            rep: self-consistency 轮序号 0..NUM_JUDGE_REPS-1（进缓存 tag，三轮各占
            独立缓存槽位）；None = legacy 单轮口径（仅历史 v1 manifest 冻结重放传入，
            走改造前 tag judge|try{n} 以命中既有缓存条目）。

    Returns:
        (模型名, 轮序号, [(关键词, 得分, 理由), ...])
    """
    model_name, keywords_batch, batch_idx, rep, client_config = args

    client = _get_client(client_config)
    logger = logging.getLogger("LLMs_for_dic")
    task_id = f"判别-{_task_label(model_name, batch_idx, rep)}"
    # 方案 B 统一 tag 命名：三轮 judge|rep{r}|try{n}；legacy（rep=None）保持 judge|try{n}
    # 逐字节不变——历史 v1 manifest 的 $0 离线重放依赖旧 tag 命中旧缓存条目。
    _tag_prefix = "judge" if rep is None else f"judge|rep{rep}"

    best_partial_results = []
    best_partial_count = 0

    for attempt in range(MAX_JUDGE_RETRIES):
        if _shutdown_event.is_set():
            _audit_outcome(model_name, batch_idx, rep, "shutdown")
            return (model_name, rep, [(kw, 0, "") for kw in keywords_batch])

        # 模型健康检查
        if _model_health.should_skip(model_name):
            _audit_outcome(model_name, batch_idx, rep, "health_skip")
            return (model_name, rep, [(kw, 0, "") for kw in keywords_batch])

        prompt = build_judge_prompt(keywords_batch)
        # temperature=0 确定性判别：prompt 本身含全部关键词即可唯一定位；
        # try 序号防止缓存里的坏响应把解析重试锁死在同一条上。
        # ⚠ 零温例外（2026-07-21 披露）：SAMPLING_PARAM_FILTERED_MODELS（claude-opus-4.7+，
        # 现即 claude-fable-5 / claude-opus-4-8）的 temperature/top_p/top_k 官方 API 不支持
        # （技术规格随模型发布同步生效，非单独废弃公告），yunwu 自 2026-07-10 起静默过滤
        # → 对这两家 temperature=0 不生效（实际默认温度采样），确定性降级为缓存冻结级
        # （缓存键仍含 temperature="0"，刻意不改）。完整披露见 config.py 该常量处。
        # ⚠ 键=整批 prompt：上游词表哪怕漂移一个词，批次切片整体移位 → 判别缓存
        # 几乎全 miss（正确性无损，纯成本放大）；词表稳定时才有 $0 重放。
        # ── 复现审计（P1/P2）：记录本 try 的缓存键与命中态（与 _call_llm_with_retry
        #    的 temp_key="0"/tag 构造严格同构；键结构改动须双处同步） ──
        _audit_tag = f"{_tag_prefix}|try{attempt}"
        _audit_key = LLMCache.make_key(model_name, prompt, "0", _audit_tag)
        _cached_before = (
            _llm_cache.has(model_name, prompt, "0", _audit_tag)
            if _llm_cache is not None else False
        )
        try:
            text = _call_llm_with_retry(
                client, model_name, prompt, task_id, logger,
                force_temperature=0, cache_tag=_audit_tag,
            )
        except LLMCacheMissError as e:
            # 离线重放遇到首跑缓存空洞：置全局停止走优雅中断，不炸穿 executor
            _audit_attempt(model_name, batch_idx, rep, attempt, _audit_key, False, False)
            _audit_outcome(model_name, batch_idx, rep, "offline_miss")
            logger.error(f"  [{task_id}] {e}")
            _shutdown_event.set()
            return (model_name, rep, [(kw, 0, "") for kw in keywords_batch])

        _audit_attempt(
            model_name, batch_idx, rep, attempt, _audit_key, _cached_before, text is not None
        )
        if text is None:
            logger.warning(f"  [{task_id}] 第{attempt + 1}次尝试失败，返回为None")
        else:
            logger.debug(f"  [{task_id}] LLM 原始响应:\n{text}")
            data = _safe_parse_json(text)
            # 防御：_safe_parse_json 对顶层 JSON 数组返回 list，下方 .get 会 AttributeError；
            # 非 dict 一律视为空，走既有"解析结果不足→重试"兜底（镜像 fetch_batch 的 isinstance 守卫）。
            if not isinstance(data, dict):
                data = {}

            # 提取 results 列表
            results_list = data.get("results", [])
            if not results_list:
                for v in data.values():
                    if isinstance(v, list) and len(v) > 0:
                        results_list = v
                        break

            # 兜底打捞：判别端每批 200 条 {keyword,score,reason}（比生成端更长），同样可能被
            # 输出上限截断。主解析空时，逐个提取已生成的完整判别对象喂给下方 result_map；
            # 配合既有「部分覆盖 ≥95% 提前采纳」逻辑，截断响应也能贡献大部分判别而非全批重试。
            if not results_list:
                salvaged = _salvage_json_objects(text or "")
                if salvaged:
                    results_list = salvaged
                    logger.warning(
                        f"  [{task_id}] 主解析失败，从截断/畸形响应打捞出 {len(salvaged)} 条判别"
                        f"（疑似 max_tokens 截断，已尽力恢复）"
                    )

            if results_list and len(results_list) > 0:
                # 构建 keyword -> (score, reason) 的映射
                result_map: Dict[str, Tuple[int, str]] = {}
                for item in results_list:
                    if isinstance(item, dict) and "keyword" in item:
                        kw = str(item["keyword"]).strip()
                        # fix(S12, 2026-07-14): int() 裸转换在 score 为非数字/None/list 等
                        # 畸形值时会 ValueError/TypeError 炸穿整个判别主循环 → 改为 try/except
                        # 记 warning 并跳过该坏项，不让单条坏响应拖垮整批判别；该词缺席
                        # result_map 后，走下方既有"未匹配补默认值 0"兜底路径。
                        raw_score = item.get("score", 0)
                        try:
                            sc = int(raw_score)
                        except (TypeError, ValueError):
                            logger.warning(
                                f"  [{task_id}] 判别结果坏项: keyword={kw!r} "
                                f"score={raw_score!r} 无法转为 int，已跳过该词（按未匹配处理）"
                            )
                            continue
                        # fix(评审B, 2026-07-21): 0/1 域强制——Prompt 契约 score∈{0,1},
                        # 但越界整数 (如 score/reason 字段错置产生的 3) 能通过 int() 转换,
                        # 而下游 _rep_vote 对原始分求和过门 → 单轮一个越界值即可伪造
                        # ([3,0,0]→sum≥2) 或否决 ([-1,1,1]→sum<2) 模型内多数。域外按坏项
                        # 跳过 (镜像上方 S12 语义, 走"未匹配补 0"兜底), 使二值不变量在
                        # 代码层强制而非仅存于 Prompt 文字契约。
                        if sc not in (0, 1):
                            logger.warning(
                                f"  [{task_id}] 判别结果坏项: keyword={kw!r} "
                                f"score={sc!r} 越出 0/1 域，已跳过该词（按未匹配处理）"
                            )
                            continue
                        # 模型按新契约只回 reason 序号 (0-5)；此处纯本地查表把序号映回
                        # REASONS 理由全文，使落盘 _reason 列保持可读（非法/越界/空/仍是全文
                        # 均 fail-soft 原样返回，不崩批）。见 config.reason_text_from_index。
                        rs = reason_text_from_index(item.get("reason", ""))
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
                    _audit_outcome(model_name, batch_idx, rep, "full", consumed_try=attempt, coverage=1.0)
                    return (model_name, rep, batch_results)
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
                    f"  [{task_id}] 重试{attempt + 1}次后覆盖率达 {pct4(best_partial_count, len(keywords_batch))} "
                    f"({best_partial_count}/{len(keywords_batch)})，提前采纳部分结果"
                )
                _audit_outcome(
                    model_name, batch_idx, rep, "partial_adopt",
                    consumed_try=attempt, coverage=coverage,
                )
                return (model_name, rep, best_partial_results)

        if attempt < MAX_JUDGE_RETRIES - 1:
            wait = min(15, 2 * (2 ** attempt)) + random.uniform(0, 5)  # 退避等待
            logger.info(f"  [{task_id}] 判定失败，等待 {sig4(wait)}s 后进行第 {attempt + 2} 次重试...")
            time.sleep(wait)

    # 超过最大重试次数，如果有部分成功的结果，则返回最佳部分成功结果
    if best_partial_count > 0:
        logger.warning(f"  [{task_id}] 达到最大重试次数，采纳最佳部分判别结果 ({best_partial_count}/{len(keywords_batch)})，其余标记为0")
        _audit_outcome(
            model_name, batch_idx, rep, "partial_adopt",
            coverage=best_partial_count / len(keywords_batch),
        )
        return (model_name, rep, best_partial_results)

    # 超过最大重试次数，标记失败
    logger.error(f"  [{task_id}] 失败，全部标记为0")
    _audit_outcome(model_name, batch_idx, rep, "hard_fail")
    return (model_name, rep, [(kw, 0, "") for kw in keywords_batch])


# ════════════════════════════════════════════════════════════════
# 判别聚合：模型内 self-consistency 投票 + 判别语义 DataFrame 单一构建器
# ════════════════════════════════════════════════════════════════

def _rep_vote(scores: List[int], majority: int) -> int:
    """模型内 self-consistency 多数票：三轮 0/1 判分之和过 majority(常态=2) 门。

    奇数轮 + 二值判分 → 永无平票；缺轮（该轮 hard_fail/health_skip 全 0 或聚合缺格）
    按 0 计——保守方向，缺轮绝不可能把词投成 1（判决块会曝光缺轮降级）。
    0/1 域在 judge_batch 解析处强制（越界整数按坏项跳过），故求和过门即真多数。
    fix(评审A, 2026-07-21): majority 改显式参数——冻结重放须用 manifest 记录的
    rep_majority 而非活体 config 值，防 config 轮数协议后续演进使历史 v2 manifest
    重放的投票门静默漂移（写而不读缺陷）。
    """
    return 1 if sum(scores) >= majority else 0


def _build_judge_dataframe(
    kw_list: List[str],
    model_results: Dict[Tuple[str, Optional[int]], Dict[str, Any]],
    judge_models: List[str],
    n_judge_reps: Optional[int],
    rep_majority: Optional[int] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """由 (model, rep) → {kw: [score, reason]} 聚合层构建判别语义 DataFrame。

    ⚠ 单一构建器：main() 与 --judge-only 冻结重放共用本函数，杜绝历史上「两处
    DataFrame 副本各改各的」漂移通路（镜像 stage21 双门控教训）。

    n_judge_reps=None → legacy 单轮口径（v1 manifest 冻结重放）：每模型输出
      {key}_score / {key}_reason 两列，total_score = 13 次单判之和——与改造前
      逐字节同构（历史重放 A/B 对拍锚）。
    n_judge_reps=int → 三轮口径：每模型 7 列（score_r1..r3 + reason_r1..r3 + vote），
      vote = 该模型三轮判分的 ≥rep_majority 多数，total_score = 13 家 vote 之和。
    rep_majority: 模型内多数门。fix(评审A, 2026-07-21): v2 冻结重放必须传 manifest
      冻结值（防活体 config 协议演进使历史重放静默失真）；None 回退当前 config
      的 JUDGE_REP_MAJORITY（main 首跑口径）。

    Returns:
        (df_judged, ordered_cols)：ordered_cols 以 total_score 开头、按模型序排列
        判别列（不含 id/keyword，由调用方拼装列序前缀）。
    """
    _majority = JUDGE_REP_MAJORITY if rep_majority is None else int(rep_majority)
    reps: List[Optional[int]] = [None] if n_judge_reps is None else list(range(n_judge_reps))
    judge_rows: List[Dict[str, Any]] = []
    for kw in kw_list:
        row: Dict[str, Any] = {"keyword": kw}
        total = 0
        for model in judge_models:
            key = model.replace(".", "_").replace("-", "_")
            if n_judge_reps is None:
                res = model_results[(model, None)].get(kw, [0, ""])
                if isinstance(res, (int, float)):
                    score, reason = int(res), ""
                else:
                    score = int(res[0])
                    reason = str(res[1]) if len(res) > 1 else ""
                row[f"{key}_score"] = score
                row[f"{key}_reason"] = reason
                total += score
            else:
                rep_scores: List[int] = []
                for r in reps:
                    res = model_results[(model, r)].get(kw, [0, ""])
                    if isinstance(res, (int, float)):
                        score, reason = int(res), ""
                    else:
                        score = int(res[0])
                        reason = str(res[1]) if len(res) > 1 else ""
                    row[f"{key}_score_r{r + 1}"] = score
                    row[f"{key}_reason_r{r + 1}"] = reason
                    rep_scores.append(score)
                vote = _rep_vote(rep_scores, _majority)
                row[f"{key}_vote"] = vote
                total += vote
        row["total_score"] = total
        judge_rows.append(row)

    df_judged = pd.DataFrame(judge_rows)
    ordered_cols: List[str] = ["total_score"]
    for model in judge_models:
        key = model.replace(".", "_").replace("-", "_")
        if n_judge_reps is None:
            ordered_cols += [f"{key}_score", f"{key}_reason"]
        else:
            ordered_cols += [f"{key}_score_r{r + 1}" for r in reps]
            ordered_cols += [f"{key}_reason_r{r + 1}" for r in reps]
            ordered_cols.append(f"{key}_vote")
    return df_judged, ordered_cols


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
    logger.info(
        f"--- 阶段② 词根精简（Set-based Reduction）: 超子串包容剔除算子，收敛为正交原子"
        f"词根以抑制派生词重复计量与无监督扩容假阳性 {cite('hanley_2019', 'li_2021')} ---"
    )
    logger.info(f"  当前去重后词数: {len(unique_keywords)} ...")

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
            logger.info(
                f"  已处理 {count}/{total} 个词 ({pct4(count, total)}), "
                f"耗时 {sig4(elapsed)}s, 速度 {sig4(rate)} 词/s"
            )

    elapsed = time.time() - start_time
    logger.info(
        f"阶段② 词根精简完成：保留 {len(simplified)}/{total}（保留率 {pct4(len(simplified), total)}），"
        f"总耗时 {sig4(elapsed)}s"
    )
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

            # 对判分类列应用条件格式，覆盖三代列形态:
            # {key}_score (v1 单轮) / {key}_score_r{n} + {key}_vote (三轮) / total_score
            for col_idx, cell in enumerate(ws[1], 1):
                header_val = str(cell.value or "")
                if re.search(r"(_score(_r\d+)?|_vote)$", header_val) or header_val == "total_score":
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

def main(dry_run: bool = False) -> None:
    """
    主入口：执行完整的关键词生成 → 处理 → 判别 → 保存流程。

    Args:
        dry_run: 仅显示任务规模和成本预估，不实际执行
    """
    if not API_KEY:
        print("❌ 错误: API Key 未配置。请设置环境变量 YUNWU_FULL_KEY")
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
    _log_run_header(logger)
    # client_config 现在按模型动态获取，见下方任务构建处

    # 缓存状态汇报
    if _llm_cache is not None:
        cs = _llm_cache.stats()
        mode = "离线重放 (miss 即报错, $0)" if OFFLINE_MODE else "在线 (miss 才调 API)"
        logger.info(
            f"🗄️ LLM 缓存已启用 [{mode}]: {cs['db_path']} "
            f"(现有 {cs['total_entries']} 条, {sig4(cs['size_mb'])} MB)"
        )
        logger.info(
            "   注意: 缓存命中=重放历史响应; 若要全新多样性采样, "
            "设 LLMS_DIC_CACHE=0 或先 python llm_cache.py --clear --yes"
        )
    else:
        logger.info("🗄️ LLM 缓存已停用 (LLMS_DIC_CACHE=0)，所有请求直连 API")

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
        # 判别任务规模: 词表在生成阶段完成前未知, 报公式; 若盘上有冻结 manifest 则附参考数
        logger.info(
            f"  判别阶段任务数 = {len(JUDGE_MODELS)} 模型 × ceil(词数/{JUDGE_BATCH_SIZE}) 批"
            f" × {NUM_JUDGE_REPS} 轮 (self-consistency, 内部多数门 ≥{JUDGE_REP_MAJORITY})"
        )
        _latest_mf = sorted(DATA_DIR.glob("judge_manifest_*.json"))
        if _latest_mf:
            try:
                _mf = json.loads(_latest_mf[-1].read_text(encoding="utf-8"))
                _nb = int(_mf.get("n_batches", 0))
                if _nb:
                    logger.info(
                        f"  参考最新冻结词表 ({_latest_mf[-1].name}): {_mf.get('n_words')} 词/"
                        f"{_nb} 批 → 判别任务 {len(JUDGE_MODELS) * _nb * NUM_JUDGE_REPS} 个"
                    )
            except Exception:
                pass
        logger.info(f"  判别批次大小: {JUDGE_BATCH_SIZE}")
        logger.info(f"  判别并发数: {MAX_WORKERS_JUDGE}")
        logger.info(f"  单次超时: {REQUEST_TIMEOUT}s")
        logger.info(f"  全局重试上限: {MAX_TOTAL_RETRIES}")
        logger.info(f"  模型失败跳过阈值: {MODEL_FAIL_THRESHOLD}")
        est_minutes = gen_task_count * 15 / MAX_WORKERS_GENERATE / 60
        logger.info(f"  预估生成阶段耗时: ~{sig4(est_minutes)} 分钟 (假设平均 15s/任务)")
        logger.info("=" * 60)
        logger.info("提示: 去掉 --dry-run 参数即可正式执行")
        return

    # ====================================================================
    # 第一阶段：生成关键词
    # ====================================================================
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
                tasks.append((model, dom["name"], prompt, i, get_client_config(model)))

    # 随机打乱任务顺序，避免同一模型的请求扎堆导致限流
    random.shuffle(tasks)

    total_tasks = len(tasks)
    logger.info(
        f"--- 阶段① 开始并行执行: {len(MODELS)} 个模型 × {len(DOMAINS)} 个领域 "
        f"× {NUM_REPEAT_PER_MODEL} 次 = {total_tasks} 个总量 ---"
    )
    logger.info(
        "    机制：各异构基座模型在默认温度下、以领域种子词与格式示范为条件并发重复采样"
        "（Monte-Carlo，无梯度微调），以查全率与特征分布探测为目标 "
        + cite("brown_2020", "dekok_2025")
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_GENERATE) as executor:
        futures = [executor.submit(fetch_batch, task) for task in tasks]

        completed = 0
        for future in concurrent.futures.as_completed(futures):
            if _shutdown_event.is_set():
                logger.warning("中断信号已设置，提前结束生成阶段...")
                break

            gen_model, dom_name, res, _idx = future.result()
            completed += 1

            if res:
                dom_keywords[dom_name].extend(res)
                all_keywords.extend(res)
                keywords_raw_count += len(res)
                for kw in res:
                    all_records.append({"domain": dom_name, "keyword": kw, "model": gen_model})

            # 进度汇报
            if completed % 10 == 0 or completed == total_tasks:
                logger.info(
                    f"  📊 生成进度: {completed}/{total_tasks} "
                    f"({pct4(completed, total_tasks)}), "
                    f"已收集 {keywords_raw_count} 个原始词条"
                )

    if _shutdown_event.is_set():
        logger.warning("⚠️ 因中断信号提前结束生成阶段，将用已有结果继续。")

    if not all_keywords:
        logger.error("未获取到任何数据")
        return

    # 清洗关键词
    all_keywords = _clean_keywords(all_keywords)

    # 去重
    unique_keywords = sorted(set(all_keywords))

    # 去数字字母：只要词汇中包含数字或 ASCII 字母 (如 "P2P"/"AI风控"/"5G支付")
    # 即整词删除。位于去重之后、词根精简之前；unique_keywords 仍保留纯去重口径
    # (供 "2-去重后" 表与统计的"去重"列)，过滤结果 filtered_keywords 流向下游。
    _HAS_ALNUM = re.compile(r"[0-9A-Za-z]")
    filtered_keywords = [kw for kw in unique_keywords if not _HAS_ALNUM.search(kw)]
    logger.info(
        f"  去数字字母: {len(unique_keywords)} → {len(filtered_keywords)} "
        f"(删除含数字/字母词 {len(unique_keywords) - len(filtered_keywords)} 个)"
    )

    # 词根精简
    simplified_keywords = _simplify_keywords(filtered_keywords)

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

    # ====== 步骤 2b: 去数字字母 ======
    df_step2b = pd.DataFrame({"id": range(1, len(filtered_keywords) + 1), "keyword": filtered_keywords})

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
            f"--- 阶段③ 开始批量判别 (共 {final_count} 个词, "
            f"每批 {JUDGE_BATCH_SIZE} 个, {len(JUDGE_MODELS)} 个模型 × 每家 {NUM_JUDGE_REPS} 轮) ---"
        )
        logger.info(
            "    机制：机器交叉盲审（LLM-as-a-Judge Swarm），各模型零温 T=0 背靠背评分；"
            f"双层多数投票——模型内 {NUM_JUDGE_REPS} 轮独立盲审按 ≥{JUDGE_REP_MAJORITY} 轮多数"
            "（self-consistency）聚成正式票，模型间按严格过半数（strict majority，> 1/2 家）截断，"
            "并施加凝缩型思维链（CoT）约束削减单体偏误与幻觉 "
            + cite("wang_2022", "zheng_2023", "gu_2024", "gilardi_2023", "liu_2023", "ouyang_2022",
                   "bernard_2026", "wei_2022", "ji_2023")
        )
        # ⚠ 零温例外披露（动态；详见 config.py::SAMPLING_PARAM_FILTERED_MODELS 常量处）
        _t0_filtered = [m for m in JUDGE_MODELS if m in SAMPLING_PARAM_FILTERED_MODELS]
        if _t0_filtered:
            logger.info(
                f"    ⚠ 零温例外：{' / '.join(_t0_filtered)}（claude-opus-4.7+）的 "
                "temperature/top_p/top_k 官方 API 不支持（技术规格随模型发布同步生效，"
                "非单独废弃公告；yunwu 2026-07-10 00:00 起静默过滤）→ "
                f"该 {len(_t0_filtered)} 家实际按模型默认温度采样，其判别票可复现性由"
                '冻结 LLM 缓存保证（缓存键仍含 temperature="0"，缓存 miss 重取时同词判别票可能翻转）'
            )

    judge_start_time = time.time()

    kw_list = df_step4["keyword"].tolist()
    batches = [kw_list[i:i + JUDGE_BATCH_SIZE] for i in range(0, len(kw_list), JUDGE_BATCH_SIZE)]
    logger.info(f"  共 {len(batches)} 个批次")

    # 构建判别任务: 模型 × 轮 × 批次（rep 序号进缓存 tag，三轮各占独立缓存槽位）
    judge_tasks = []
    for model in JUDGE_MODELS:
        for rep in range(NUM_JUDGE_REPS):
            for bi, batch in enumerate(batches):
                judge_tasks.append((model, batch, bi, rep, get_client_config(model)))

    # 随机打乱判别任务
    random.shuffle(judge_tasks)
    logger.info(f"  总判别请求数: {len(judge_tasks)} 次")

    # 收集判别结果: {(model, rep): {keyword: [score, reason]}}
    model_results: Dict[Tuple[str, Optional[int]], Dict[str, List[Any]]] = {
        (m, r): {} for m in JUDGE_MODELS for r in range(NUM_JUDGE_REPS)
    }

    if not _shutdown_event.is_set():
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_JUDGE) as executor:
            futures = [executor.submit(judge_batch, t) for t in judge_tasks]
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                if _shutdown_event.is_set():
                    logger.warning("中断信号已设置，提前结束判别阶段...")
                    break
                model_name, rep, batch_results = future.result()
                for kw, score, reason in batch_results:
                    model_results[(model_name, rep)][kw] = [score, reason]
                completed += 1
                # 进度汇报
                if completed % 5 == 0 or completed == len(judge_tasks):
                    logger.info(f"  📊 判别进度: {completed}/{len(judge_tasks)} ({pct4(completed, len(judge_tasks))})")

    # 汇报被跳过的模型
    skipped = _model_health.get_skipped()
    if skipped:
        logger.warning(f"  ⚠️ 以下模型因连续失败被自动跳过: {', '.join(skipped)}")

    logger.info("判别完成，正在整理结果...")
    judge_duration = time.time() - judge_start_time

    # ── 盲审可复现性判决 + manifest 落盘（P1/P2；STRICT_REPLAY=1 时判决不过即拒绝出结果）──
    _verdict = _emit_replay_verdict(kw_list, model_results, logger, n_judge_reps=NUM_JUDGE_REPS)
    _write_judge_manifest(kw_list, _verdict, logger, OUTPUT_FILE, n_judge_reps=NUM_JUDGE_REPS)

    # ====================================================================
    # 构建判别结果 DataFrame（单一构建器，与 --judge-only 冻结重放共用）
    # 每模型 7 列: 三轮 score_r1..r3 + 三轮 reason_r1..r3 + 内部多数票 vote；
    # total_score = 13 家 vote 之和（语义: 13 张模型内部多数票之和）
    # ====================================================================
    df_judged, _judge_cols = _build_judge_dataframe(
        kw_list, model_results, JUDGE_MODELS, NUM_JUDGE_REPS
    )

    # 合并 ID
    df_final = pd.merge(df_step4, df_judged, on="keyword", how="left")

    # 调整列顺序: id, keyword, total_score, 各模型三轮判分/理由 + vote
    ordered_cols = ["id", "keyword"] + _judge_cols
    ordered_cols += [c for c in df_final.columns if c not in ordered_cols]
    df_final = df_final[ordered_cols]

    # 按 total_score 降序排序
    df_final = df_final.sort_values(by="total_score", ascending=False).reset_index(drop=True)
    df_final["id"] = range(1, len(df_final) + 1)

    # ====================================================================
    # 汇总保存
    # ====================================================================
    filtered_set = set(filtered_keywords)
    simplified_set = set(simplified_keywords)
    final_kw_set = set(kw_list)
    # fix(S2, 2026-07-14): 阈值由 >= (含平票=4) 改严格多数 > (=≥5/8)。
    # 更新(2026-07-17): 入选判据由简单严格多数 (>1/2) 收紧为 2/3 严格多数 (历史台账)。
    # 更新(2026-07-21): 按用户裁定回调为严格过半数 (> len(JUDGE_MODELS) * 0.5;
    # 当前 13 家 → >6.5, 即至少 7 票)；同批引入模型内三轮 self-consistency,
    # total_score 语义变为「13 张模型内部多数票之和」(每票 = 该模型 NUM_JUDGE_REPS 轮
    # 独立盲审的 ≥JUDGE_REP_MAJORITY 多数)。阈值不进 LLM
    # 缓存键，此改动只影响未来重跑的词表筛选，不动现有 fintech_dict.json。
    # ⚠ 家数写死仅作示意；真实门槛恒随 JUDGE_MODELS 动态计算，改模型列表后本行数字须同步。
    judge_ok_set = set(
        df_final[df_final["total_score"] > len(JUDGE_MODELS) * 0.5]["keyword"]
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
            "去数字字母": len(dom_set & filtered_set),
            "精简": len(dom_set & simplified_set),
            "最终": len(dom_set & final_kw_set),
            "AI认可": len(dom_set & judge_ok_set),
        })
    stats_rows.append({
        "领域": "【汇总】",
        "原始": total_generated,
        "去重": len(unique_keywords),
        "去数字字母": len(filtered_keywords),
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
            df_step2b.to_excel(writer, sheet_name="2b-去数字字母后", index=False)
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

                # 去数字字母后
                dom_filtered = sorted(kw for kw in dom_set if kw in filtered_set)
                if dom_filtered:
                    df_af = pd.DataFrame({"id": range(1, len(dom_filtered) + 1), "keyword": dom_filtered})
                    writer_sheet = f"去数字字母-{dom_name}"[:31]
                    df_af.to_excel(writer, sheet_name=writer_sheet, index=False)

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
    _n_ai = len(judge_ok_set)
    logger.info("═" * 78)
    logger.info("--- 任务完成：运行结果与统计摘要 (Results & Statistics) ---")
    logger.info("═" * 78)
    logger.info(
        f"【运行期 Runtime】生成耗时 {sig4(gen_duration)}s | 判别耗时 {sig4(judge_duration)}s | "
        f"总耗时 {sig4(duration)}s（生成占比 {pct4(gen_duration, duration)}）"
    )
    logger.info(f"【领域 Domain】数量 {len(DOMAINS)}")
    # 结果链：生成 → 去重 → 去数字字母 → 精简/最终 → AI 认可，附四位有效数字留存/认可率
    logger.info(
        f"【结果链 Pipeline】生成 {total_generated} → 去重 {len(unique_keywords)} "
        f"→ 去数字字母 {len(filtered_keywords)} → 精简/最终 {final_count} → AI 认可 {_n_ai}"
    )
    logger.info(
        f"  去重率 {pct4(len(unique_keywords), total_generated)}（去冗余）｜"
        f"去字母率 {pct4(len(filtered_keywords), len(unique_keywords))}（删含数字/字母词）｜"
        f"精简率 {pct4(final_count, len(filtered_keywords))}（超子串正交化）｜"
        f"AI 认可率 {pct4(_n_ai, final_count)}（占最终词表）"
    )
    if _total_retry_count > 0:
        logger.info(f"【稳健性 Robustness】全局重试总次数 {_total_retry_count}（费用保护上限 {MAX_TOTAL_RETRIES}）")
    if _llm_cache is not None:
        n_req = _llm_cache.hits + _llm_cache.misses
        logger.info(
            f"【缓存 Cache】命中 {_llm_cache.hits} / 未命中 {_llm_cache.misses} "
            f"(命中率 {pct4(_llm_cache.hits, n_req)}, 命中部分 $0；确定性 $0 重放锚)"
        )

    # 判别统计（total_score 分布，附四位有效数字占比）
    score_counts = df_final["total_score"].value_counts().sort_index(ascending=False)
    _n_judged = int(score_counts.sum())
    logger.info(
        f"【AI 判别 total_score 分布】受审 {_n_judged} 词，票数越高表示越多模型共识认可 "
        + cite("zheng_2023", "gopal_2025")
    )
    for sc, cnt in score_counts.items():
        logger.info(f"  得分 {sc}: {cnt} 个词（占 {pct4(cnt, _n_judged)}）")
    # fix(S2, 2026-07-14) + 更新(2026-07-17→2026-07-21): 口径声明——上方分布及下表
    # "AI认可"列均按严格过半数 (>1/2，即 JUDGE_MODELS 中 >len(JUDGE_MODELS)*0.5 家
    # 模型认可) 统计；total_score = 13 张模型正式票之和 (每票 = 该模型 NUM_JUDGE_REPS
    # 轮独立盲审的内部多数)。⚠ "恰好半数"的临界平票仅当模型数为偶数时存在（当前
    # 13 家奇数 → 13*0.5=6.5 非整数，严格 > 天然无平票）。
    _min_pass = len(JUDGE_MODELS) // 2 + 1
    logger.info(
        f"  口径声明(S2): 'AI认可'/上方 total_score 分布均按严格过半数统计"
        f"(> {sig4(len(JUDGE_MODELS) * 0.5)}，即 {len(JUDGE_MODELS)} 家模型中需 ≥{_min_pass} 票; "
        f"每家正式票 = 其 {NUM_JUDGE_REPS} 轮盲审的 ≥{JUDGE_REP_MAJORITY} 轮内部多数)"
    )

    logger.info("【各领域统计 Per-domain】")
    logger.info(
        f"  {'领域名称':<16s} {'原始':>6s} {'去重':>6s} {'去数字字母':>6s} "
        f"{'精简':>6s} {'最终':>6s} {'AI认可':>6s} {'认可率':>8s}"
    )
    logger.info(f"  {'-' * 16} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 8}")
    for dom in DOMAINS:
        dom_name = dom["name"]
        dom_raw = dom_keywords.get(dom_name, [])
        dom_set = set(dom_raw)
        n_raw = len(dom_raw)
        n_uniq = len(dom_set)
        n_filt = len(dom_set & filtered_set)
        n_simp = len(dom_set & simplified_set)
        n_final = len(dom_set & final_kw_set)
        n_ai = len(dom_set & judge_ok_set)
        logger.info(
            f"  {dom_name:<16s} {n_raw:>6d} {n_uniq:>6d} {n_filt:>6d} "
            f"{n_simp:>6d} {n_final:>6d} {n_ai:>6d} {pct4(n_ai, n_final):>8s}"
        )
    # 一致性验证指针（κ 由 calculate_kappa.py 独立离线计算，读该脚本内指定的判别结果 xlsx，
    # 非本进程内联、亦非必为本轮 OUTPUT_FILE — 当前脚本硬编码指向一份 v1 冻结判别件）
    logger.info(
        "【一致性验证 Validation】模型间评分者一致性 Fleiss' Kappa 由 calculate_kappa.py 独立离线"
        "计算（读该脚本内指定的判别结果 xlsx，当前为 v1 冻结件；非本进程内联）；"
        "分级采用 Landis-Koch 与 McHugh 双口径披露，一致性系数族（Cohen κ / Krippendorff α / Gwet AC1）为佐证 "
        + cite("fleiss_1971", "landis_1977", "mchugh_2012", "cohen_1960", "hayes_2007", "gwet_2008")
    )
    logger.info(f"【产物 Output】结果已保存至: {OUTPUT_FILE}")
    # 尾部：本轮日志引用的全部 APA 参考文献（经 crossref/doi.org 核验，逐字誊抄自手稿书目）
    _log_run_references(logger)


# ════════════════════════════════════════════════════════════════
# D2: 盲审冻结重放（--judge-only --from-manifest）
# ════════════════════════════════════════════════════════════════

def judge_replay_from_manifest(manifest_path: Path) -> None:
    """从 manifest 冻结词表直接重放盲审（跳过生成阶段——正典盲审复现通道）。

    冻结语义：词表、批次大小、模型名单一律取 manifest 记录值（首跑口径），
    不受当前 config 后续漂移影响；与 config 不一致时 loud WARNING 但照冻结值跑。
    产物 = **全阶段完整 workbook**（2026-07-21 用户要求，取代旧「判别语义精简件」口径）：
    生成阶段各 sheet 从首跑产物（manifest.run_output_file）**只读拷贝**，判别语义
    sheet（5-AI判别结果 / 判别-*）以本次重放结果重建，4-最终结果 恒以 manifest 冻结
    词表为准（sha256 已验）；首跑产物缺失时 loud WARNING 降级为判别语义精简件
    （4-最终结果 + 5-AI判别结果）。另产新 manifest（可再次被验证器核验）。
    ⚠ 生成阶段零触碰铁律：本函数不 import、不调用 fetch_batch 及任何生成侧逻辑——
    「完整册」仅复制冻结产物的既有 sheet，不重新执行任何生成计算。
    """
    logger = setup_logger()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    _schema = manifest.get("schema")
    if _schema not in {"llmsdic-judge-manifest/v1", "llmsdic-judge-manifest/v2"}:
        raise SystemExit(f"[manifest] 无法识别的 schema: {_schema!r}")
    # v1（改造前单轮口径）→ frozen_reps=None → judge_batch 走 legacy tag judge|try{n}
    # 命中旧缓存条目（方案 B 下旧条目保留不删，历史 $0 复现锚不断）；
    # v2 → 按记录轮数重放（tag judge|rep{r}|try{n}）。
    frozen_reps: Optional[int] = (
        int(manifest["n_judge_reps"]) if _schema.endswith("/v2") else None
    )
    # fix(评审A, 2026-07-21): 模型内多数门同样取 manifest 冻结值（此前写而不读——
    # _rep_vote 恒用活体 config, 若 config 轮数协议后续演进, 历史 v2 manifest 重放的
    # 投票会静默漂移且判决照旧盖「可复现」）。缺省回退 frozen_reps//2+1（派生律）。
    frozen_majority: Optional[int] = None
    if frozen_reps is not None:
        frozen_majority = int(manifest.get("rep_majority", frozen_reps // 2 + 1))

    kw_list: List[str] = list(manifest["wordlist"])
    recorded_sha = manifest["wordlist_sha256"]
    actual_sha = _wordlist_sha256(kw_list)
    if actual_sha != recorded_sha:
        raise SystemExit(
            f"[manifest] 词表完整性校验失败: 记录 sha256={recorded_sha[:16]}... "
            f"实算 {actual_sha[:16]}...（manifest 疑被篡改/损坏，拒绝重放）"
        )
    frozen_models: List[str] = list(manifest["judge_models"])
    frozen_bsize: int = int(manifest["judge_batch_size"])
    if frozen_models != list(JUDGE_MODELS):
        logger.warning(
            "  ⚠ manifest 冻结模型名单与当前 config.JUDGE_MODELS 不一致——按冻结名单重放"
        )
    if frozen_bsize != JUDGE_BATCH_SIZE:
        logger.warning(
            f"  ⚠ manifest 冻结批次大小 {frozen_bsize} ≠ 当前 config {JUDGE_BATCH_SIZE}"
            "——按冻结值重放"
        )
    if frozen_reps is not None and (
        frozen_reps != NUM_JUDGE_REPS or frozen_majority != JUDGE_REP_MAJORITY
    ):
        logger.warning(
            f"  ⚠ manifest 冻结轮次协议 ({frozen_reps} 轮/多数门 ≥{frozen_majority}) ≠ "
            f"当前 config ({NUM_JUDGE_REPS} 轮/≥{JUDGE_REP_MAJORITY})——按冻结协议重放"
        )

    output_file = DATA_DIR / (
        f"bank_keywords_judge_replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    logger.info("═" * 78)
    logger.info("--- 盲审冻结重放 (--judge-only --from-manifest) ---")
    logger.info(f"  manifest: {manifest_path}")
    _reps_label = "单轮(legacy)" if frozen_reps is None else f"{frozen_reps} 轮/模型"
    logger.info(
        f"  冻结口径: {len(kw_list)} 词 / 每批 {frozen_bsize} / {len(frozen_models)} 模型 / "
        f"{_reps_label} / 离线={OFFLINE_MODE} 缓存={CACHE_ENABLED} 严格门={STRICT_REPLAY}"
    )

    start_time = time.time()
    batches = [kw_list[i:i + frozen_bsize] for i in range(0, len(kw_list), frozen_bsize)]
    _reps_iter: List[Optional[int]] = [None] if frozen_reps is None else list(range(frozen_reps))
    judge_tasks = []
    for model in frozen_models:
        for rep in _reps_iter:
            for bi, batch in enumerate(batches):
                judge_tasks.append((model, batch, bi, rep, get_client_config(model)))
    random.shuffle(judge_tasks)
    logger.info(
        f"  共 {len(batches)} 批 × {len(frozen_models)} 模型 × {len(_reps_iter)} 轮 "
        f"= {len(judge_tasks)} 任务"
    )

    model_results: Dict[Tuple[str, Optional[int]], Dict[str, Any]] = {
        (m, r): {} for m in frozen_models for r in _reps_iter
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_JUDGE) as executor:
        futures = [executor.submit(judge_batch, t) for t in judge_tasks]
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            if _shutdown_event.is_set():
                logger.warning("中断信号已设置，提前结束判别阶段...")
                break
            model_name, rep, batch_results = future.result()
            for kw, score, reason in batch_results:
                model_results[(model_name, rep)][kw] = [score, reason]
            completed += 1
            if completed % 5 == 0 or completed == len(judge_tasks):
                logger.info(f"  📊 重放进度: {completed}/{len(judge_tasks)} ({pct4(completed, len(judge_tasks))})")

    verdict = _emit_replay_verdict(
        kw_list, model_results, logger,
        judge_models=frozen_models, n_judge_reps=frozen_reps,
    )
    _write_judge_manifest(
        kw_list, verdict, logger, output_file,
        judge_models=frozen_models, batch_size=frozen_bsize,
        n_judge_reps=frozen_reps, rep_majority=frozen_majority,
    )

    # 判别语义 DataFrame（单一构建器，与 main 共用；v1 冻结口径自动回落
    # 单轮 score/reason 两列形态，与改造前产物逐字节同构；
    # v2 投票门用 manifest 冻结值 frozen_majority, 不受活体 config 漂移影响）
    df_judged, _judge_cols = _build_judge_dataframe(
        kw_list, model_results, frozen_models, frozen_reps, rep_majority=frozen_majority
    )
    df_wordlist = pd.DataFrame({"id": range(1, len(kw_list) + 1), "keyword": kw_list})
    df_final = pd.merge(df_wordlist, df_judged, on="keyword", how="left")
    ordered_cols = ["id", "keyword"] + _judge_cols
    ordered_cols += [c for c in df_final.columns if c not in ordered_cols]
    df_final = df_final[ordered_cols]
    df_final = df_final.sort_values(by="total_score", ascending=False).reset_index(drop=True)
    df_final["id"] = range(1, len(df_final) + 1)

    # ── 全阶段完整 workbook（2026-07-21 用户要求：生成 + 盲审全部阶段同册）────────
    # 生成阶段各 sheet 从首跑产物（manifest.run_output_file）**只读拷贝**——生成阶段
    # 零触碰铁律不破（不执行任何生成侧逻辑，仅复制冻结产物既有 sheet，sheet 顺序保持
    # 首跑原样）；判别语义 sheet（5-AI判别结果 / 判别-*）以本次重放结果重建；
    # 4-最终结果 恒以 manifest 冻结词表为准（sha256 已验，词表唯一权威）；统计总览
    # 「AI认可」列在 v2 口径下按 manifest 冻结门槛与本次重放判别重算（其余列均为生成
    # 阶段事实，原样拷贝），v1 口径无冻结门槛字段、不重算（原样拷贝并留痕）。
    _src_name = manifest.get("run_output_file")
    _src_path = (DATA_DIR / _src_name) if _src_name else None
    src_sheets: Dict[str, pd.DataFrame] = {}
    if _src_path is not None and _src_path.exists():
        try:
            src_sheets = pd.read_excel(_src_path, sheet_name=None)
            logger.info(
                f"  [完整册] 生成阶段 sheet 自首跑产物只读拷贝: {_src_name}"
                f"（{len(src_sheets)} 个 sheet）"
            )
        except Exception as e:
            src_sheets = {}
            logger.warning(
                f"  ⚠ [完整册] 首跑产物读取失败（{_src_name}: {e}）——降级为判别语义精简件"
            )
    else:
        logger.warning(
            f"  ⚠ [完整册] 首跑产物缺失（{_src_name!r}）——无生成阶段 sheet 可拷贝，"
            "降级为判别语义精简件（4-最终结果 + 5-AI判别结果）"
        )

    # v2: 入选门槛取 manifest 冻结值（缺字段按冻结名单严格过半数派生，min_votes=n//2+1，
    # 与 main 的 > n*0.5 在整数票下恒等价）；v1 无冻结门槛 → 不重算「AI认可」。
    _frozen_min_votes: Optional[int] = None
    judge_ok_set: Set[str] = set()
    if frozen_reps is not None:
        _fvt = manifest.get("final_vote_threshold") or {}
        _frozen_min_votes = int(_fvt.get("min_votes", len(frozen_models) // 2 + 1))
        judge_ok_set = set(
            df_final[df_final["total_score"] >= _frozen_min_votes]["keyword"]
        )
    elif src_sheets:
        logger.info(
            "  [完整册] v1 口径无冻结入选门槛字段——统计总览「AI认可」列原样拷贝首跑值（不重算）"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    _written: Set[str] = set()
    with pd.ExcelWriter(str(output_file), engine="openpyxl") as writer:
        for sheet_name, src_df in src_sheets.items():
            if sheet_name == "4-最终结果":
                df_wordlist.to_excel(writer, sheet_name=sheet_name, index=False)
            elif sheet_name == "5-AI判别结果":
                df_final.to_excel(writer, sheet_name=sheet_name, index=False)
            elif sheet_name.startswith("判别-"):
                # 该域受审子集 = 首跑同名 sheet 的词集（域归属是生成阶段事实，只读复用；
                # 词表 sha 已验 → 首跑与重放的受审全集恒同）
                _kws = set(src_df["keyword"]) if "keyword" in src_df.columns else set()
                dom_judged = df_final[df_final["keyword"].isin(_kws)].copy()
                if dom_judged.empty and len(_kws) > 0:
                    logger.warning(
                        f"  ⚠ [完整册] {sheet_name} 词集与冻结词表零交集——原样拷贝首跑 sheet"
                    )
                    src_df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    dom_judged = dom_judged.sort_values(
                        by="total_score", ascending=False
                    ).reset_index(drop=True)
                    dom_judged["id"] = range(1, len(dom_judged) + 1)
                    dom_judged.to_excel(writer, sheet_name=sheet_name, index=False)
            elif (
                sheet_name == "银行关键词统计"
                and _frozen_min_votes is not None
                and "领域" in src_df.columns
                and "AI认可" in src_df.columns
            ):
                df_stats = src_df.copy()
                for _i, _dom in df_stats["领域"].items():
                    if _dom == "【汇总】":
                        df_stats.at[_i, "AI认可"] = len(judge_ok_set)
                    else:
                        _fin = src_sheets.get(f"最终-{_dom}"[:31])
                        if _fin is not None and "keyword" in _fin.columns:
                            df_stats.at[_i, "AI认可"] = len(
                                set(_fin["keyword"]) & judge_ok_set
                            )
                        else:
                            logger.warning(
                                f"  ⚠ [完整册] 首跑产物缺「最终-{_dom}」sheet——"
                                f"统计行「{_dom}」的 AI认可 保留首跑拷贝值"
                            )
                df_stats.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                src_df.to_excel(writer, sheet_name=sheet_name, index=False)
            _written.add(sheet_name)
        # 判别语义两 sheet 兜底保证在册（无首跑产物 / 首跑产物缺该 sheet 时）
        if "4-最终结果" not in _written:
            df_wordlist.to_excel(writer, sheet_name="4-最终结果", index=False)
        if "5-AI判别结果" not in _written:
            df_final.to_excel(writer, sheet_name="5-AI判别结果", index=False)
    _format_excel_workbook(output_file)

    if _llm_cache is not None:
        n_req = _llm_cache.hits + _llm_cache.misses
        logger.info(
            f"【缓存 Cache】命中 {_llm_cache.hits} / 未命中 {_llm_cache.misses} "
            f"(命中率 {pct4(_llm_cache.hits, n_req)})"
        )
    logger.info(f"【产物 Output】重放结果已保存至: {output_file}")
    logger.info(f"  重放总耗时 {sig4(time.time() - start_time)}s")


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
        "--dry-run", action="store_true",
        help="仅显示任务规模和成本预估，不实际执行",
    )
    parser.add_argument(
        "--judge-only", action="store_true",
        help="仅重放盲审（须配 --from-manifest；跳过生成阶段，从冻结词表直接判别）",
    )
    parser.add_argument(
        "--from-manifest", type=str, metavar="PATH", default=None,
        help="盲审 manifest 路径（默认取 data_processed/ 下最新一份 judge_manifest_*.json）",
    )
    args = parser.parse_args()

    if args.view_logs:
        view_logs()
    elif args.view_log:
        view_log(args.view_log)
    elif args.judge_only:
        _mf = args.from_manifest
        if _mf is None:
            _candidates = sorted(DATA_DIR.glob("judge_manifest_*.json"))
            if not _candidates:
                raise SystemExit("[--judge-only] data_processed/ 下无 judge_manifest_*.json，"
                                 "请先跑一次完整流程产出 manifest 或用 --from-manifest 指定")
            _mf = _candidates[-1]
        judge_replay_from_manifest(Path(_mf))
    else:
        if args.from_manifest:
            raise SystemExit("[--from-manifest] 须与 --judge-only 连用")
        main(dry_run=args.dry_run)
