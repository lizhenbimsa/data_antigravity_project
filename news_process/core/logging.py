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
