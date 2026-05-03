"""news_process.core.logging — logger setup, ANSI formatter, timing decorator.

Split from legacy ``utils/helpers.py:196-523``.
Public API preserved: ``setup_logging``, ``log_and_time``, ``log_memory_usage``,
``log_stage_summary``, ``_ColoredFormatter``.

The Phase 1 plan specifies a per-run log directory layout
``logs/runs/<run_id>/<stage>.log``; ``setup_logging`` reads the
``NEWS_PROCESS_RUN_ID`` environment variable. When present, logs go to
``<log_dir>/runs/<run_id>/<stage>.log``; otherwise to ``<log_dir>/<stage>.log``
(legacy fallback).
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
    """Return the value of NEWS_PROCESS_RUN_ID env var, or None."""
    return os.environ.get(_RUN_ID_ENV)


class _ColoredFormatter(logging.Formatter):
    """ANSI-colored console formatter (different colors per log level)."""

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
    """Configure a logger with rotating file + colored console output.

    Args:
        stage_name:    Logger namespace and log filename stem.
        log_dir:       Base log directory.  When env var
                       ``NEWS_PROCESS_RUN_ID`` is set, the actual file is
                       ``<log_dir>/runs/<run_id>/<stage_name>.log``;
                       otherwise ``<log_dir>/<stage_name>.log``.
        file_mode:     'w' (truncate-on-start) or 'a' (append).
        console_only:  If True, no file handler is created.  Used by
                       subprocesses to avoid corruption from concurrent
                       file writes.
        level:         Default logging level.
        max_bytes:     Per-file size cap before rotation (default 50MB).
        backup_count:  Number of rotated backups to retain.

    Returns:
        logging.Logger: configured logger instance (idempotent — re-calling
        clears existing handlers first).
    """
    # Resolve actual log directory: per-run subdir if NEWS_PROCESS_RUN_ID set.
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
    """Decorator factory: log entry/exit, runtime, RSS delta, I/O size summary."""
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
    """Log current process RSS + system available memory."""
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
    """Print a stage-completion summary block (rows in/out, elapsed, RSS)."""
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
