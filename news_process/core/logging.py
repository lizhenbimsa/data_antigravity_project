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
import os
import sys
import time
import warnings
from functools import wraps
from logging.handlers import RotatingFileHandler

import pandas as pd
import psutil

_RUN_ID_ENV = "NEWS_PROCESS_RUN_ID"


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


class _MaxLevelFilter(logging.Filter):
    """只放行级别低于 ``max_level`` 的日志记录。"""

    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.max_level


class _ColoredFormatter(logging.Formatter):
    """ANSI 着色 console formatter (按日志等级染色)。"""

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

    def __init__(self, datefmt=None):
        super().__init__(datefmt=datefmt)
        self.default_msec_format = '%s.%03d'

    def format(self, record):
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
        '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s',
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

    console_formatter = _ColoredFormatter(datefmt='%Y-%m-%d %H:%M:%S')

    ch_out = logging.StreamHandler(sys.stdout)
    ch_out.setLevel(level)
    ch_out.addFilter(_MaxLevelFilter(logging.WARNING))
    ch_out.setFormatter(console_formatter)
    logger.addHandler(ch_out)

    ch_err = logging.StreamHandler(sys.stderr)
    ch_err.setLevel(max(level, logging.WARNING))
    ch_err.setFormatter(console_formatter)
    logger.addHandler(ch_err)

    logger.propagate = False

    return logger


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

                logger.info(
                    f"--- 执行完毕: {func_name} | "
                    f"耗时: {duration:.2f}s | "
                    f"内存变化: {mem_delta:+.1f}MB | "
                    f"结果: {output_summary} ---"
                )

        return wrapper
    return decorator


def _format_bytes(b: int) -> str:
    """将字节数格式化为 GB/MB 字符串 (>=1GB 用 GB, 否则 MB)。"""
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
    logger.info(f"  耗时:     {elapsed:.2f} 秒 ({minutes:.2f} 分钟)")

    if input_rows is not None:
        logger.info(f"  输入:     {input_rows:,} 行")
    if output_rows is not None:
        logger.info(f"  输出:     {output_rows:,} 行")
        if input_rows and input_rows > 0:
            retention = output_rows / input_rows * 100
            logger.info(f"  保留率:   {retention:.1f}%")

    rss = psutil.Process().memory_info().rss
    logger.info(f"  内存RSS:  {_format_bytes(rss)}")

    if extra_info:
        for k, v in extra_info.items():
            logger.info(f"  {k}: {v}")

    logger.info("═" * 50)
