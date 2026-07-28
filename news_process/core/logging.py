"""news_process.core.logging — logger 配置、ANSI 着色 formatter、计时装饰器。

由历史 ``utils/helpers.py:196-523`` 拆分而来。
保留的公开 API: ``setup_logging``、``log_and_time``、``log_memory_usage``、
``log_stage_summary``、``_ColoredFormatter``。

日志目录布局为扁平的 ``logs/<stage>.log`` (每个阶段固定一个文件);
``setup_logging`` 不再按 ``NEWS_PROCESS_RUN_ID`` 分 per-run 子目录
(用户决策 2026-06-15: 只保留最新一次运行的日志, 新的覆盖旧的,
不再累积历次运行日志)。配合 ``file_mode='w'`` 的首写截断
(见 ``_DelayedTruncatingRotatingHandler``), 每次运行从头截断上一次
同名日志 —— 天然实现"只留最新"。``NEWS_PROCESS_RUN_ID`` 仍生成并随
子进程传播, 但仅作为日志行内的运行关联标记, 不再影响落盘路径。
"""

from __future__ import annotations

import logging
import math
import multiprocessing
import os
import sys
import time
import warnings
from functools import wraps
from logging.handlers import RotatingFileHandler

import pandas as pd
import psutil

_RUN_ID_ENV = "NEWS_PROCESS_RUN_ID"

# 落盘日志行的**无色**格式 (单一事实源): 文件 handler 恒用它; console handler 在
# 输出流非 TTY (被管道捕获 / 重定向到文件) 时也退化到它, 以保证两类输出在无色
# 路径上字节一致, 且 ANSI 转义码绝不进入任何落盘文件 (见 _should_colorize)。
_PLAIN_LINE_FMT = (
    '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s'
)


def _install_warning_filters() -> None:
    """抑制已知的可选加速器警告 (CPU 环境下无害, 如 triton 找不到 CUDA)。"""
    warnings.filterwarnings(
        "ignore",
        message=r"Failed to find CUDA\.",
        category=UserWarning,
        module=r"triton\.windows_utils",
    )


def _configure_standard_streams() -> None:
    """让被重定向的 Windows 标准流容忍 UTF-8 流水线日志 (errors=replace)。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _configure_third_party_loggers() -> None:
    """把第三方依赖的可恢复噪音日志压到 ERROR 级, 避免污染阶段 stderr。"""
    for name in (
        "huggingface_hub",
        "huggingface_hub.utils._http",
        "transformers",
        "urllib3",
        "sentence_transformers",
    ):
        logging.getLogger(name).setLevel(logging.ERROR)


def get_run_id() -> str | None:
    """返回 NEWS_PROCESS_RUN_ID 环境变量的值, 不存在返回 None。"""
    return os.environ.get(_RUN_ID_ENV)


def _is_spawned_child_process() -> bool:
    """判定「本进程是 multiprocessing / loky spawn 出来的**工作子进程**」。

    **为何需要 (F27, 2026-07-27 生产实弹)**: stage 40 的逐年进程并行 (F25) 起 12 个
    loky worker, 每个 worker import ``pipeline.features.strategic_diff`` → 传递触发
    ``pipeline/panel/encode.py:48`` 的模块级 ``setup_logging("40_build_panel", …)``
    → ``_DelayedTruncatingRotatingHandler`` 的「本进程首写即截断」把父进程已写的
    212 KB 日志抹成 **99.8% NUL、只剩 3 行**。同型风险覆盖 stage 15/22/24/40 四个
    已用进程并行的阶段。此前对策是**逐个 emit 点**加守卫 (``silent=`` /
    ``parent_process() is None``, 见 ``pipeline/text/fintech_intensity.py``), 属打地鼠;
    根治点是**不给子进程装文件 handler** —— 把 ``console_only`` 从「调用方自觉传参」
    升级为「基建强制」。⚠ ``setup_logging`` 的 docstring 本来就写着 console_only
    「用于子进程, 避免多进程并发写同一文件造成日志错乱」—— 机制早就有, 只是没接上。

    **三谓词取并集** (缺一不可; 2026-07-28 Windows 真机探针实测):
      P1 ``parent_process() is not None`` —— 在 ``BaseProcess._bootstrap()`` 里赋值。
         loky 的 worker 目标是 loky 自己的 ``_process_worker``, 用户模块要到**任务
         出队反序列化**时才 import, 那已在 ``_bootstrap`` 之后 → LokyProcess 恒 True。
      P2 ``current_process().name != 'MainProcess'`` —— 在 ``spawn.prepare()`` 第一行
         赋值, 早于 ``_fixup_main_from_path`` 对 ``__main__`` 的重执行。**这是 P1
         覆盖不到的致命窗口**: stdlib ``ProcessPoolExecutor(spawn)`` 的子进程会把
         ``__main__`` (= ``NN_*.py`` shim) 当 ``__mp_main__`` 重跑一遍, 那一刻
         P1=False 而 P2=True。只用 parent_process() 会在这个窗口漏判。
      P3 ``_inheriting`` —— ``spawn._main()`` 读 preparation_data **之前**置位、
         反序列化完成后删除, 兜住 P2 赋值前的极窄窗口。

    **主进程恒三谓词皆 False** —— 含 orchestrator 用 ``subprocess.Popen`` 拉起的每个
    stage 子进程: 那是**全新解释器**, ``current_process()`` 恒为 ``_MainProcess``
    (name='MainProcess')、``parent_process()`` 恒 None → 照常装文件 handler。
    **主进程写盘行为零变化** —— 这是本判据的安全底线 (单向收紧: 只加静音不放宽)。
    """
    try:
        proc = multiprocessing.current_process()
        if multiprocessing.parent_process() is not None:      # P1
            return True
        if proc.name != "MainProcess":                        # P2
            return True
        return bool(getattr(proc, "_inheriting", False))      # P3
    except Exception:  # noqa: BLE001 — 极端环境 (冻结/嵌入解释器) → 保守判为主进程
        return False


class _MaxLevelFilter(logging.Filter):
    """只放行级别低于 ``max_level`` 的日志记录。"""

    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.max_level


def _should_colorize(stream) -> bool:
    """判断某输出流是否应启用 ANSI 着色 —— 仅当其连接真实终端且未被显式禁用时。

    ANSI 着色只对人类在**交互式终端**阅读有意义。一旦输出流被重定向 / 管道捕获
    (阶段子进程的 stdout 被 orchestrator 以 ``subprocess.PIPE`` 捕获, 或
    ``python x.py > out.log`` 重定向到文件), 着色就会把 ``\\x1b[...m`` 转义码写进
    落盘文件; 尤其 orchestrator 会把捕获到的子进程 stdout 原样转发进
    ``run_pipeline_*.log``, 转义码随之污染日志。故此处以 ``isatty()`` 为统一闸门,
    并遵循 NO_COLOR 事实标准 (https://no-color.org): 任何非空 ``NO_COLOR`` 即禁用着色。
    """
    if os.environ.get("NO_COLOR"):
        return False
    try:
        return bool(stream.isatty())
    except Exception:  # 流无 isatty / 已关闭 / 捕获对象等 → 保守判为非终端
        return False


class _ColoredFormatter(logging.Formatter):
    """ANSI 着色 console formatter (按日志等级染色)。

    ``use_color=False`` 时**退化为与文件 handler 完全一致的无色纯文本**
    (``_PLAIN_LINE_FMT``): 当输出流不是真实终端 (被 PIPE 捕获 / 重定向到文件) 时,
    一律输出无色文本, 避免 ANSI 转义码污染落盘日志 (是否着色由 ``setup_logging``
    经 :func:`_should_colorize` 按流逐一判定后注入)。
    """

    _GREY = '\033[38;5;245m'
    _BLUE = '\033[38;5;75m'
    _CYAN = '\033[36m'
    _GREEN = '\033[32m'
    _YELLOW = '\033[33m'
    _RED = '\033[31m'
    _BOLD_RED = '\033[1;31m'
    _RESET = '\033[0m'

    _LEVEL_COLORS = {
        logging.DEBUG: _CYAN,
        logging.INFO: _GREEN,
        logging.WARNING: _YELLOW,
        logging.ERROR: _RED,
        logging.CRITICAL: _BOLD_RED,
    }

    def __init__(self, datefmt=None, use_color: bool = True):
        super().__init__(datefmt=datefmt)
        self.default_msec_format = '%s.%03d'
        self._use_color = use_color

    def format(self, record):
        if not self._use_color:
            # 无色路径: 与文件 handler 字节一致, 不写入任何 ANSI 转义码。
            self._style._fmt = _PLAIN_LINE_FMT
            return super().format(record)
        level_color = self._LEVEL_COLORS.get(record.levelno, self._RESET)
        fmt = (
            f'{self._GREY}%(asctime)s{self._RESET} - '
            f'{self._BLUE}%(name)s{self._RESET} - '
            f'{self._GREY}PID:%(process)d{self._RESET} - '
            f'{level_color}%(levelname)s{self._RESET} - '
            f'%(message)s'
        )
        self._style._fmt = fmt
        return super().format(record)


class _DelayedTruncatingRotatingHandler(RotatingFileHandler):
    """RotatingFileHandler 变体, 同时满足两个目标:

    1. ``delay=True``: 仅在第一条日志真正写入时才创建文件, 因此"只 import 模块"
       或"阶段在产出任何日志前就退出"都不会留下 0 字节空 log。
    2. ``file_mode='w'`` 语义: 本进程"首次"打开 base 文件时以 ``'w'`` 截断
       (实现"每次运行从头"), 其后 (含 rollover 重开) 以 ``'a'`` 追加。

    为何需要自定义 (LOG-1 audit 2026-05-30): stdlib ``RotatingFileHandler.__init__``
    在 ``maxBytes > 0`` 时会把构造参数 ``mode`` 强制改成 ``'a'`` (防止多次运行因
    ``'w'`` 截断而丢历史日志), 因此无法用 ``mode='w'`` 表达"每次运行从头"。本类
    在 ``_open()`` 层面对"本进程首次打开"强制 ``'w'`` 截断, 既不依赖被覆盖的
    ``mode`` 参数, 又与 ``delay`` 兼容 (truncate 推迟到首次写入)。
    """

    def __init__(self, *args, truncate_on_first_open: bool = False, **kwargs):
        # 在 super().__init__ 之前置位: delay=False 时父类构造期即会调用 _open()。
        self._truncate_on_first_open = truncate_on_first_open
        self._has_opened = False
        super().__init__(*args, **kwargs)

    def _open(self):
        if self._truncate_on_first_open and not self._has_opened:
            self._has_opened = True
            saved_mode = self.mode
            self.mode = 'w'  # 本进程首次写入: 截断上一次运行遗留的内容
            try:
                return super()._open()
            finally:
                self.mode = saved_mode  # 其后 (rollover 重开) 回到 append
        self._has_opened = True
        return super()._open()


def setup_logging(stage_name, log_dir, file_mode='w', console_only=False,
                  level=logging.INFO, max_bytes=50*1024*1024, backup_count=3):
    """配置一个集成了 rotating 文件输出 + 着色 console 输出的 logger。

    Args:
        stage_name:    Logger 命名空间, 同时作为日志文件名词干。
        log_dir:       日志根目录。日志固定写入扁平路径
                       ``<log_dir>/<stage_name>.log`` (每阶段一个文件)。
                       配合 ``file_mode='w'`` 的首写截断, 每次运行覆盖
                       上一次同名日志 —— 只保留最新一次运行 (不再按
                       ``NEWS_PROCESS_RUN_ID`` 分 per-run 子目录)。
        file_mode:     ``'w'`` (首次写入日志时截断, 见下方 delay 说明) 或
                       ``'a'`` (追加)。
        console_only:  若为 True, 不创建文件 handler。用于子进程, 避免
                       多进程并发写同一文件造成日志错乱。
        level:         默认日志级别。
        max_bytes:     单文件大小上限 (达到后 rotate, 默认 50 MB)。
        backup_count:  rotate 保留的备份数量。

    Returns:
        logging.Logger: 已配置好的 logger 实例 (幂等 — 重复调用会先清空
        现有 handler 再注册)。
    """
    # ── F27 硬闸 (2026-07-28): spawn/loky 工作子进程一律不装文件 handler ──
    # 单向收紧 (只加静音不放宽): 主进程行为逐字节不变; 子进程无论从哪条 import 链
    # 触发 setup_logging, 都不可能再打开阶段 .log ⟹ 「本进程首写即截断」在结构上
    # 不可发生。这是 F27 的**根治点** —— 逐个 emit 点加守卫是打地鼠, 而 import 链
    # 上任何一个模块级 setup_logging 都足以毁掉整份日志 (2026-07-27 实弹: 12 个
    # loky worker 把 40_build_panel.log 抹成 99.8% NUL)。
    # ⚠ 代价 (刻意接受): worker 体内的 logger 调用**不再进阶段 .log**, 只走 console。
    #   ⚠ 2026-07-28 订正: 本处原写「会静默 (loky 默认丢弃 worker stdout)」——
    #     **该前提已被 S5 A/B 证伪**: loky worker 继承父进程 stdout/stderr, 其日志
    #     确实会落到父进程的输出 (生产上再由 orchestrator 捕获镜像)。故不是"静默",
    #     而是"只走 console 且行序不可预测"。
    #   ⟹ F25 立下的「worker 体内零 logger 调用, 告警回传父端 emit」纪律**仍然必须
    #     遵守** —— 但理由是**行序**而非可见性: 并行下 worker 的行会乱序交错, 业务
    #     告警必须经 log_sink 回传父端按提交序回放才对得上。本闸不是它的替代品。
    if _is_spawned_child_process():
        console_only = True

    _install_warning_filters()
    _configure_standard_streams()
    _configure_third_party_loggers()

    # 日志一律写入扁平的 <log_dir>/<stage>.log: 每个阶段固定一个文件, 不再按
    # NEWS_PROCESS_RUN_ID 分 per-run 子目录 (用户决策 2026-06-15: 只保留最新一次
    # 运行, 新覆盖旧, 不再累积历次运行日志)。"只留最新"由 file_mode='w' 的首写
    # 截断 (见 _DelayedTruncatingRotatingHandler) 实现 —— 本次运行从头截断上一次
    # 同名日志, 因此无需 per-run 子目录即可天然避免跨运行累积。
    actual_log_dir = log_dir
    os.makedirs(actual_log_dir, exist_ok=True)

    logger = logging.getLogger(stage_name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    file_formatter = logging.Formatter(
        _PLAIN_LINE_FMT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_formatter.default_msec_format = '%s.%03d'

    if not console_only:
        log_file = os.path.join(actual_log_dir, f"{stage_name}.log")
        # delay=True (2026-05-30 根因修复): 不在 setup 时急切创建/截断文件,
        # 推迟到第一条日志真正 emit 时才 open。仅 import 模块 (pytest 收集 /
        # 单独 import 一个顶层调 setup_logging() 的 stage 模块), 或阶段在产出
        # 任何日志前就退出时, 不会再留下 0 字节空 log (logs/ 顶层历史空 log 根因)。
        # file_mode='w' 的 "每次运行从头" 截断语义由 _DelayedTruncatingRotatingHandler
        # 在本进程首次写入时实现 —— 不能直接靠 mode='w', 因为 stdlib 在 maxBytes>0
        # 时会把它强制改 'a' (LOG-1 audit 2026-05-30), 必须在 _open() 层截断。
        fh = _DelayedTruncatingRotatingHandler(
            log_file, mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
            delay=True,
            truncate_on_first_open=(file_mode == 'w'),
        )
        fh.setLevel(level)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # ANSI 着色仅在 console 流连接真实终端时启用: 一旦被管道捕获 (阶段子进程的
    # stdout 被 orchestrator 以 PIPE 捕获) 或重定向到文件, 即退化为无色纯文本 ——
    # 否则转义码会被 orchestrator 原样转发落入 run_pipeline_*.log, 污染日志
    # (LOG-COLOR 修复 2026-06-25)。逐流判定 (stdout / stderr 可能一个是 TTY 一个
    # 被重定向), 故各自构造独立 formatter。
    ch_out = logging.StreamHandler(sys.stdout)
    ch_out.setLevel(level)
    ch_out.addFilter(_MaxLevelFilter(logging.WARNING))
    ch_out.setFormatter(_ColoredFormatter(
        datefmt='%Y-%m-%d %H:%M:%S',
        use_color=_should_colorize(ch_out.stream)))
    logger.addHandler(ch_out)

    ch_err = logging.StreamHandler(sys.stderr)
    ch_err.setLevel(max(level, logging.WARNING))
    ch_err.setFormatter(_ColoredFormatter(
        datefmt='%Y-%m-%d %H:%M:%S',
        use_color=_should_colorize(ch_err.stream)))
    logger.addHandler(ch_err)

    logger.propagate = False

    # ── F29 / F16 (2026-07-28): 让 news_process.* 模块 logger 的记录真正可见 ──
    _attach_namespace_console(stage_name, [ch_out, ch_err], level, console_only)

    return logger


#: 全项目包命名空间 = 所有 ``logging.getLogger(__name__)`` 模块 logger 的公共祖先。
_NS_LOGGER_NAME = "news_process"
#: 命名空间 owner 阶段名 (首次非 console_only 调用即锁定, 之后不再改) —— 见下方说明。
_NS_OWNER: str | None = None
#: 已挂到命名空间 logger 上的 handler (身份引用, 供幂等去重)。
_NS_ATTACHED: list[logging.Handler] = []


def _attach_namespace_console(stage_name: str, handlers, level: int,
                              console_only: bool) -> None:
    """把本次 setup_logging 造出的 **console** handler 挂到 ``news_process`` 命名空间。

    **为何 (F29 + F16, 2026-07-27 实弹)**: 23 个 pipeline/core 模块用
    ``logging.getLogger(__name__)`` (如 ``news_process.pipeline.text.embedding_engine``),
    而 stage logger 名是 ``"40_build_panel"`` 这类**裸阶段名** —— 两条互不相交的
    logger 链。后果: 模块日志既进不了阶段 ``.log``, 又因 root 无 handler 落到
    ``logging.lastResort`` (裸 ``%(message)s`` 写 stderr, **levelname 丢失**)。
    于是 embedding_engine 那条「重试 80 次仍失败 → 该轨列将置 NaN」的 ``logger.error``
    在 orchestrator 镜像里变成 WARNING, ``grep -c " - ERROR - "`` = **0** ——
    验收判据对真实数据丢失完全失明 (这就是 F28 被漏判 28 小时的直接原因)。

    **两条刻意的设计约束** (2026-07-28 对抗审查裁决, 各换掉一个致命问题):

    ① **只挂 console handler, 永不挂 file handler**。
       否则命名空间 logger 会持有第二个 ``_DelayedTruncatingRotatingHandler`` 指向
       同一个 ``.log`` —— 那是 F27 的**同型二次截断**风险。console 已足够: 阶段子
       进程的 stdout/stderr 全部被 orchestrator 捕获并镜像落盘, 记录不会丢。

    ② **owner 锁定, 不用 last-wins**。生产实测: 一个 stage 40 进程会调用 ≥4 次
       ``setup_logging`` (``encode``→40_build_panel · ``llm_peer_iv``→48 ·
       ``network_brokerage``→47 · ``network_spillover``→46, 均模块级)。若按「最后一次
       调用赢」绑定, F29 的载荷会被路由到**错误的阶段**, 那就是自造一个 F27。
       故取**首次非 console_only 调用**为 owner (= 该进程真正的宿主阶段), 之后
       只做幂等校验不再改绑。

    零重复落盘: 挂的是**同一批 handler 实例**; stage logger 名 (裸阶段名) 无一位于
    ``news_process.`` 命名空间下 ⟹ 任一 LogRecord 只沿一条链走到这批 handler,
    ``callHandlers`` 对每个 handler 只调一次。刻意**不动** ``propagate`` (保持 True):
    生产阶段进程内 root 恒无 handler 故无二次 emit, 而 ``callHandlers`` 的
    ``found > 0`` 顺带关掉 lastResort —— 旧的丢 levelname 裸 stderr 路径就此消失;
    保持 True 是为了 pytest ``caplog`` (既有测试对 ``news_process.core.config``
    这类 logger 的断言依赖这条传播链)。
    """
    global _NS_OWNER

    def _bind(hs):
        ns = logging.getLogger(_NS_LOGGER_NAME)
        for h in _NS_ATTACHED:      # 幂等: 同一进程重复调用先摘旧
            ns.removeHandler(h)
        _NS_ATTACHED.clear()
        for h in hs:
            ns.addHandler(h)
            _NS_ATTACHED.append(h)
        # ⚠ 必须显式设级: 不设则 NOTSET → 继承 root 的 WARNING, 模块的 INFO 仍然落空
        # (F16 只修一半)。默认取阶段级别, 可用 env 单独放宽以做归因跑
        # (如 7h-emb 的 API/CPU 分段归因需要 embedding_engine 的 INFO)。
        _lv = os.environ.get('NEWS_PROCESS_NS_LOG_LEVEL', '').strip().upper()
        ns.setLevel(getattr(logging, _lv, level) if _lv else level)

    if console_only:
        # 子进程 (F27 硬闸) 或调用方显式 console_only: **不参与 owner 竞争, 但仍要挂**。
        #
        # ⚠ 2026-07-28 订正 (S5 A/B 实测): 本分支原先直接 `return`, 理由写的是
        #   「子进程里挂命名空间 handler 无意义 (loky 默认丢弃 worker stdout)」——
        #   **该前提已被证伪**: S5 逐年并行的 A/B 里, loky worker 的 12 条
        #   「分词器已注入 607 个金科词」确实落到了父进程 stdout (worker 继承父进程
        #   的 stdout/stderr, 生产上再由 orchestrator 捕获镜像)。
        #   前提错了, 代价是真的: 并行段内 `news_process.*` 模块日志**整段消失** ——
        #   同一次 A/B 实测并行臂 embedding_engine 相关行 = **0**, 其中包括
        #   缓存命中率、F18 分段计时、以及「重试 80 次仍失败 → 置 NaN」那条 ERROR。
        #   最后一条尤其致命: 它正是 F28 的现场信号, 一旦并行化就又看不见了,
        #   等于把 F29 刚补上的洞在并行路径上重新挖开。
        #
        # 不锁 owner: 子进程生命周期内只服务一个阶段, 无 owner 竞争问题 (owner 锁是
        # 为父进程里 ≥4 次模块级 setup_logging 的错绑准备的)。
        # ⚠ 这**不放松**「worker 体内零 logger 调用」的纪律 —— 那条纪律管的是**行序**
        #   (worker 日志交错不可预测, 故业务告警一律经 log_sink 回传父端按序回放),
        #   与第三方模块日志是否可见是两回事。纪律由 AST gate 强制, 不靠这里。
        _bind(handlers)
        return
    if _NS_OWNER is not None and stage_name != _NS_OWNER:
        return                      # 已锁定 owner, 后续模块级 setup_logging 不改绑
    _NS_OWNER = stage_name
    _bind(handlers)


def log_and_time(logger):
    """装饰器工厂: 自动打印进入/退出、耗时、RSS 内存增量、I/O 规模摘要。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.info(f"--- 开始执行: {func_name} ---")

            input_df = None
            all_args = list(args) + list(kwargs.values())
            for arg in all_args:
                if isinstance(arg, pd.DataFrame):
                    input_df = arg
                    logger.info(f"输入DataFrame行数: {len(input_df):,}")
                    break

            mem_before = psutil.Process().memory_info().rss

            start_time = time.time()
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"函数 {func_name} 执行时发生错误: {e}", exc_info=True)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                mem_after = psutil.Process().memory_info().rss
                mem_delta = (mem_after - mem_before) / (1024 ** 2)

                output_summary = "无返回值"
                if result is not None:
                    if isinstance(result, pd.DataFrame):
                        output_summary = f"输出DataFrame行数: {len(result):,}"
                        if input_df is not None:
                            filtered_count = len(input_df) - len(result)
                            output_summary += f" (已过滤 {filtered_count:,} 行)"
                    elif isinstance(result, int):
                        output_summary = f"处理完成，共计 {result:,} 行"
                    elif hasattr(result, '__len__'):
                        output_summary = (
                            f"输出 {type(result).__name__}，"
                            f"大小为 {len(result):,}"
                        )
                    else:
                        output_summary = f"返回一个 {type(result).__name__} 对象"

                # 耗时是运行期结果统计 → sig4 四位有效数字 (项目规范 2026-06-24)。
                # 内存变化 (mem_delta) 是操作性 housekeeping 显示量, 非论文报告统计量,
                # 沿用 ±0.1f 直观显示 (与 _format_bytes 同属"内存显示豁免", 不套 sig4)。
                logger.info(
                    f"--- 执行完毕: {func_name} | "
                    f"耗时: {sig4(duration)}s | "
                    f"内存变化: {mem_delta:+.1f}MB | "
                    f"结果: {output_summary} ---"
                )

        return wrapper
    return decorator


def sig4(value, sig: int = 4) -> str:
    """将非整数数字格式化为 ``sig`` 位有效数字 (significant figures, 默认 4 位)。

    项目规范 (用户决策 2026-06-24): **日志中所有非整数数字一律保留四位有效数字**。
    本函数是该规范的单一事实源 —— 富集日志时凡打印 float/比率/分数/统计量, 统一
    经 ``sig4(...)`` 渲染, 以保证全流水线日志的有效数字口径一致、可审计、可复现。

    与 Python 内建 ``format(x, '.4g')`` 的区别 (后者**不**满足"保留四位有效数字"):
      * ``.4g`` 会丢弃尾随零 (``0.5 -> '0.5'``, 仅 1 位有效数字呈现);
        本函数补齐为 ``'0.5000'`` (4 位有效数字), 忠于"保留"。
      * ``.4g`` 对 ≥1e4 即切科学计数法 (``12345 -> '1.234e+04'``);
        本函数在常规量级保持定点 (``'12340'``), 仅在极端量级才回退科学计数法,
        使日志对人类读者更友好。

    边界: ``nan``/``inf``/``0``/非数值入参均安全降级 (返回可读串, 绝不抛异常)。
    纯字符串格式化, 不参与任何产物计算 —— 仅用于 ``logger.*`` 输出 (golden-safe)。

    Examples:
        >>> sig4(0.5)            # '0.5000'  (4 sig figs, 尾随零补齐)
        >>> sig4(98.234567)      # '98.23'
        >>> sig4(0.00123456)     # '0.001235'
        >>> sig4(12345.6)        # '12350'   (定点, 4 sig figs)
        >>> sig4(1.0)            # '1.000'
    """
    try:
        x = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(x):
        return "nan"
    if math.isinf(x):
        return "inf" if x > 0 else "-inf"
    if x == 0:
        return "0." + "0" * (sig - 1) if sig > 1 else "0"
    # 极端量级 (过大/过小) 回退科学计数法, 避免荒谬长定点串
    if abs(x) >= 10 ** (sig + 6) or abs(x) < 10 ** -(sig + 5):
        return f"{x:.{sig - 1}e}"
    decimals = sig - 1 - math.floor(math.log10(abs(x)))
    if decimals < 0:
        # 整数部分位数已 ≥ sig: 在相应数量级上四舍五入到 sig 位有效数字
        factor = 10 ** (-decimals)
        x = round(x / factor) * factor
        return f"{x:.0f}"
    return f"{x:.{decimals}f}"


def pct4(value, fraction: bool = True, sig: int = 4) -> str:
    """百分比格式化到 ``sig`` 位有效数字并追加 ``'%'`` (配合 :func:`sig4`)。

    Args:
        value:    数值。``fraction=True`` 时按比例解读 (``0.5 -> '50.00%'``);
                  ``fraction=False`` 时按已是百分数解读 (``50.0 -> '50.00%'``)。
        fraction: 入参是否为比例 (0–1 区间), 默认 True。
        sig:      有效数字位数, 默认 4。
    """
    try:
        x = float(value)
    except (TypeError, ValueError):
        return str(value)
    if fraction:
        x *= 100.0
    return sig4(x, sig) + "%"


def _format_bytes(b: int) -> str:
    """将字节数格式化为 GB/MB 字符串 (>=1GB 用 GB, 否则 MB)。

    内存字节量是操作性 housekeeping 显示量 (RSS / 可用内存), 非论文报告的研究统计量,
    刻意豁免"非整数四位有效数字"规范 (项目规范 2026-06-24): 保留人类友好的 GB=.2f /
    MB=.1f 显示, 也与 ``tests/test_helpers.py`` 对 ``"500.0 MB"`` / ``"1.0 MB"`` 的
    精确断言保持一致。运行期/结果统计量 (耗时、比率) 仍一律走 sig4/pct4。
    """
    if b >= 1024 ** 3:
        return f"{b / (1024 ** 3):.2f} GB"
    return f"{b / (1024 ** 2):.1f} MB"


def log_memory_usage(logger, tag=""):
    """记录当前进程 RSS 内存与系统可用内存。"""
    process = psutil.Process()
    rss_bytes = process.memory_info().rss
    available_bytes = psutil.virtual_memory().available

    prefix = f"{tag} | " if tag else ""
    logger.info(
        f"[Memory] {prefix}RSS: {_format_bytes(rss_bytes)} | "
        f"Available: {_format_bytes(available_bytes)}"
    )


def log_stage_summary(logger, stage_name, start_time, input_rows=None,
                      output_rows=None, extra_info=None):
    """打印阶段执行完毕摘要块 (输入/输出行数、耗时、RSS 内存)。"""
    elapsed = time.time() - start_time
    minutes = elapsed / 60

    logger.info("═" * 50)
    logger.info(f"阶段摘要: {stage_name}")
    logger.info("─" * 50)
    # 耗时/保留率为运行期结果统计 → sig4/pct4 四位有效数字 (项目规范 2026-06-24)。
    logger.info(f"  耗时:     {sig4(elapsed)} 秒 ({sig4(minutes)} 分钟)")

    if input_rows is not None:
        logger.info(f"  输入:     {input_rows:,} 行")
    if output_rows is not None:
        logger.info(f"  输出:     {output_rows:,} 行")
        if input_rows and input_rows > 0:
            retention = output_rows / input_rows * 100
            # retention 已是百分数 (×100) → pct4(..., fraction=False)
            logger.info(f"  保留率:   {pct4(retention, fraction=False)}")

    rss = psutil.Process().memory_info().rss
    logger.info(f"  内存RSS:  {_format_bytes(rss)}")

    if extra_info:
        for k, v in extra_info.items():
            logger.info(f"  {k}: {v}")

    logger.info("═" * 50)
