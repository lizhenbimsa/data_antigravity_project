"""news_process.core.logging — logger 配置、ANSI 着色 formatter、计时装饰器。

由历史 ``utils/helpers.py:196-523`` 拆分而来。
保留的公开 API: ``setup_logging``、``log_and_time``、``log_memory_usage``、
``log_stage_summary``、``_ColoredFormatter``。

Phase 1 规划要求的日志目录布局为 ``logs/runs/<run_id>/<stage>.log``;
``setup_logging`` 通过读取 ``NEWS_PROCESS_RUN_ID`` 环境变量决定具体路径:
存在时日志写入 ``<log_dir>/runs/<run_id>/<stage>.log``;
否则回退到 ``<log_dir>/<stage>.log`` (legacy fallback)。
"""

from __future__ import annotations

import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

import pandas as pd
import psutil


_RUN_ID_ENV = "NEWS_PROCESS_RUN_ID"


def get_run_id() -> str | None:
    """返回 NEWS_PROCESS_RUN_ID 环境变量的值, 不存在返回 None。"""
    return os.environ.get(_RUN_ID_ENV)


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


def setup_logging(stage_name, log_dir, file_mode='w', console_only=False,
                  level=logging.INFO, max_bytes=50*1024*1024, backup_count=3):
    """配置一个集成了 rotating 文件输出 + 着色 console 输出的 logger。

    Args:
        stage_name:    Logger 命名空间, 同时作为日志文件名词干。
        log_dir:       日志根目录。当 ``NEWS_PROCESS_RUN_ID`` 环境变量已
                       设置时, 实际写入路径为
                       ``<log_dir>/runs/<run_id>/<stage_name>.log``;
                       否则为 ``<log_dir>/<stage_name>.log``。
        file_mode:     ``'w'`` (启动时截断) 或 ``'a'`` (追加)。
        console_only:  若为 True, 不创建文件 handler。用于子进程, 避免
                       多进程并发写同一文件造成日志错乱。
        level:         默认日志级别。
        max_bytes:     单文件大小上限 (达到后 rotate, 默认 50 MB)。
        backup_count:  rotate 保留的备份数量。

    Returns:
        logging.Logger: 已配置好的 logger 实例 (幂等 — 重复调用会先清空
        现有 handler 再注册)。
    """
    # 解析实际的日志目录: 若 NEWS_PROCESS_RUN_ID 已设置, 用 per-run 子目录。
    run_id = get_run_id()
    if run_id and not console_only:
        actual_log_dir = os.path.join(log_dir, 'runs', run_id)
    else:
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
        if file_mode == 'w' and os.path.exists(log_file):
            try:
                open(log_file, 'w').close()
            except OSError:
                pass
        fh = RotatingFileHandler(
            log_file, mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
        )
        fh.setLevel(level)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(_ColoredFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(ch)

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


def log_memory_usage(logger, tag=""):
    """记录当前进程 RSS 内存与系统可用内存。"""
    process = psutil.Process()
    rss_bytes = process.memory_info().rss
    available_bytes = psutil.virtual_memory().available

    def _fmt(b):
        if b >= 1024 ** 3:
            return f"{b / (1024 ** 3):.2f} GB"
        return f"{b / (1024 ** 2):.1f} MB"

    prefix = f"{tag} | " if tag else ""
    logger.info(
        f"[Memory] {prefix}RSS: {_fmt(rss_bytes)} | "
        f"Available: {_fmt(available_bytes)}"
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
    if rss >= 1024 ** 3:
        logger.info(f"  内存RSS:  {rss / (1024 ** 3):.2f} GB")
    else:
        logger.info(f"  内存RSS:  {rss / (1024 ** 2):.1f} MB")

    if extra_info:
        for k, v in extra_info.items():
            logger.info(f"  {k}: {v}")

    logger.info("═" * 50)
