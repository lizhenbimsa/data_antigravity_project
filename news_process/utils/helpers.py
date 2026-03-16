"""
utils/helpers.py
================
新闻处理流水线的公共基础设施模块。

提供以下核心功能：
  1. load_config()         — YAML 配置文件加载与路径自动解析
  2. setup_logging()       — 日志记录器配置（文件+控制台，支持轮转）
  3. log_and_time()        — 函数执行计时与 I/O 摘要装饰器
  4. log_memory_usage()    — 当前进程内存使用快照
  5. log_stage_summary()   — 阶段级别统计摘要（行数变化、耗时、内存）
  6. parallelize_dataframe — 基于 joblib 的 DataFrame 并行分批处理

依赖：
  - pyyaml, pandas, joblib, psutil
"""

import os
import time
import yaml
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

import pandas as pd
from joblib import Parallel, delayed
import psutil


# ============================================================================
# 1. 配置文件加载
# ============================================================================

def load_config(config_path=None):
    """加载 YAML 配置文件，并将相对路径解析为绝对路径。

    Args:
        config_path: 配置文件路径。若为 None，则自动定位到
                     ``<project_root>/config/config.yaml``。
                     若传入相对路径，则基于项目根目录解析。

    Returns:
        dict: 解析后的配置字典，所有以 ``./`` 开头的值已转为绝对路径。

    Raises:
        FileNotFoundError: 配置文件不存在时抛出。
    """
    # 获取 utils/ 目录的父目录 → 项目根目录 (news_process/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    if config_path is None:
        config_path = os.path.join(project_root, 'config', 'config.yaml')
    else:
        if not os.path.isabs(config_path):
            config_path = os.path.join(project_root, config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    def resolve_paths(d, root):
        """递归将 ``./`` 开头的相对路径转为绝对路径。"""
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and (v.startswith('./') or v.startswith('.\\')):
                    d[k] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[k], (dict, list)):
                    resolve_paths(d[k], root)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, str) and (v.startswith('./') or v.startswith('.\\')):
                    d[i] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[i], (dict, list)):
                    resolve_paths(d[i], root)

    resolve_paths(config, project_root)
    return config


# ============================================================================
# 2. 日志配置
# ============================================================================

class _ColoredFormatter(logging.Formatter):
    """终端彩色日志格式化器，使用 ANSI 转义码为不同级别上色。

    颜色方案（与 IDE 日志文件语法高亮视觉一致）：
      - 时间戳：灰色          - 阶段名：蓝色
      - DEBUG：青色           - INFO：绿色
      - WARNING：黄色         - ERROR / CRITICAL：红色
    """

    # ANSI 颜色代码
    _GREY    = '\033[38;5;245m'
    _BLUE    = '\033[38;5;75m'
    _CYAN    = '\033[36m'
    _GREEN   = '\033[32m'
    _YELLOW  = '\033[33m'
    _RED     = '\033[31m'
    _BOLD_RED = '\033[1;31m'
    _RESET   = '\033[0m'

    _LEVEL_COLORS = {
        logging.DEBUG:    _CYAN,
        logging.INFO:     _GREEN,
        logging.WARNING:  _YELLOW,
        logging.ERROR:    _RED,
        logging.CRITICAL: _BOLD_RED,
    }

    def __init__(self, datefmt=None):
        # 不在 __init__ 中设置 fmt，format() 中动态拼接
        super().__init__(datefmt=datefmt)
        self.default_msec_format = '%s.%03d'

    def format(self, record):
        level_color = self._LEVEL_COLORS.get(record.levelno, self._RESET)
        # 拼接带颜色的格式串
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
    """配置带有文件轮转和控制台输出的日志记录器。

    Args:
        stage_name:    阶段名称，用于日志文件名和 logger 命名空间。
        log_dir:       日志文件输出目录。
        file_mode:     首次文件打开模式，'w'（覆盖）或 'a'（追加）。
        console_only:  若为 True，仅输出到控制台。
                       用于子进程，避免多进程并发写文件损坏。
        level:         日志级别，默认 ``logging.INFO``。
        max_bytes:     单个日志文件最大字节数（默认 50MB），超过后自动轮转。
        backup_count:  保留的日志轮转备份数（默认 3 份）。

    Returns:
        logging.Logger: 配置好的 logger 实例。
    """
    os.makedirs(log_dir, exist_ok=True)

    # 防止重复添加 handler（模块重新加载时）
    logger = logging.getLogger(stage_name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    # 纯文本格式（用于文件输出，不含 ANSI 颜色）
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_formatter.default_msec_format = '%s.%03d'

    # 文件处理器（仅主进程使用，带轮转）
    if not console_only:
        log_file = os.path.join(log_dir, f"{stage_name}.log")
        # 首次运行时清空旧日志（file_mode='w'），之后由 RotatingFileHandler 管理轮转
        if file_mode == 'w' and os.path.exists(log_file):
            try:
                open(log_file, 'w').close()  # 清空文件
            except OSError:
                pass
        fh = RotatingFileHandler(
            log_file, mode='a', maxBytes=max_bytes,
            backupCount=backup_count, encoding='utf-8'
        )
        fh.setLevel(level)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # 控制台处理器（彩色输出）
    ch = logging.StreamHandler()
    ch.setLevel(level)
    console_formatter = _ColoredFormatter(datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)

    # 防止日志向 root logger 传播导致重复输出
    logger.propagate = False

    return logger


# ============================================================================
# 3. 执行计时与 I/O 摘要装饰器
# ============================================================================

def log_and_time(logger):
    """装饰器工厂：为函数添加开始/结束日志、耗时统计和 I/O 尺寸记录。

    功能：
      - 自动检测并记录第一个 ``pd.DataFrame`` 参数的行数。
      - 根据返回值类型（DataFrame / int / 其他）智能生成输出摘要。
      - 捕获并记录异常（不吞没异常，重新抛出）。
      - 记录函数执行内存变化。

    Args:
        logger: 用于记录日志的 ``logging.Logger`` 实例。

    Returns:
        装饰器函数。

    Usage::

        @log_and_time(logger)
        def my_function(df):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.info(f"--- 开始执行: {func_name} ---")

            # --- 智能输入日志：记录第一个 DataFrame 参数的行数 ---
            input_df = None
            all_args = list(args) + list(kwargs.values())
            for arg in all_args:
                if isinstance(arg, pd.DataFrame):
                    input_df = arg
                    logger.info(f"输入DataFrame行数: {len(input_df):,}")
                    break

            # 记录起始内存
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
                mem_delta = (mem_after - mem_before) / (1024 ** 2)  # MB

                # --- 智能输出摘要 ---
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
                        output_summary = f"输出 {type(result).__name__}，大小为 {len(result):,}"
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


# ============================================================================
# 4. 内存使用快照
# ============================================================================

def log_memory_usage(logger, tag=""):
    """记录当前进程的内存使用情况和系统可用内存。

    Args:
        logger: 用于记录日志的 ``logging.Logger`` 实例。
        tag:    可选标签，附加到日志消息前缀（如 ``"加载完成后"``）。

    输出格式::

        [Memory] 加载完成后 | RSS: 1.23 GB | Available: 8.45 GB
    """
    process = psutil.Process()
    rss_bytes = process.memory_info().rss
    available_bytes = psutil.virtual_memory().available

    # 自动选择合适的单位
    def _fmt(b):
        if b >= 1024 ** 3:
            return f"{b / (1024 ** 3):.2f} GB"
        return f"{b / (1024 ** 2):.1f} MB"

    prefix = f"{tag} | " if tag else ""
    logger.info(f"[Memory] {prefix}RSS: {_fmt(rss_bytes)} | Available: {_fmt(available_bytes)}")


# ============================================================================
# 5. 阶段级别统计摘要
# ============================================================================

def log_stage_summary(logger, stage_name, start_time, input_rows=None,
                      output_rows=None, extra_info=None):
    """输出阶段执行完成的统计摘要。

    Args:
        logger:      用于记录日志的 ``logging.Logger`` 实例。
        stage_name:  阶段名称（如 ``"00_preprocessing"``）。
        start_time:  阶段开始时间（``time.time()`` 的返回值）。
        input_rows:  输入行数（可选）。
        output_rows: 输出行数（可选）。
        extra_info:  额外信息字典（可选），键值对会逐行输出。

    输出格式::

        ════════════════════════════════════════════
        阶段摘要: 00_preprocessing
        ────────────────────────────────────────────
          耗时:     123.45 秒 (2.06 分钟)
          输入:     17,000,000 行
          输出:     5,200,000 行 (保留 30.6%)
          内存RSS:  2.34 GB
        ════════════════════════════════════════════
    """
    elapsed = time.time() - start_time
    minutes = elapsed / 60

    logger.info("═" * 50)
    logger.info(f"阶段摘要: {stage_name}")
    logger.info("─" * 50)
    logger.info(f"  耗时:     {elapsed:.2f} 秒 ({minutes:.2f} 分钟)")

    if input_rows is not None:
        logger.info(f"  输入:     {input_rows:,} 行")
    if output_rows is not None:
        logger.info(f"  输出:     {output_rows:,} 行", )
        if input_rows and input_rows > 0:
            retention = output_rows / input_rows * 100
            logger.info(f"  保留率:   {retention:.1f}%")

    # 内存快照
    rss = psutil.Process().memory_info().rss
    if rss >= 1024 ** 3:
        logger.info(f"  内存RSS:  {rss / (1024 ** 3):.2f} GB")
    else:
        logger.info(f"  内存RSS:  {rss / (1024 ** 2):.1f} MB")

    if extra_info:
        for k, v in extra_info.items():
            logger.info(f"  {k}: {v}")

    logger.info("═" * 50)


# ============================================================================
# 6. DataFrame 并行分批处理
# ============================================================================

def parallelize_dataframe(df, func, n_jobs=-1, batch_size=10000,
                          logger=None, desc=None):
    """使用 joblib 对 Pandas DataFrame 进行并行分批处理。

    将 DataFrame 按 ``batch_size`` 切分为多个批次，使用 ``n_jobs`` 个并行进程
    分别对每个批次调用 ``func``，最后合并结果。

    Args:
        df:         待处理的 DataFrame。
        func:       应用于每个批次的函数，签名 ``func(df_batch) -> df_result``。
        n_jobs:     并行进程数。``-1`` 表示使用全部 CPU 核心减一。
        batch_size: 每个批次的行数（默认 10,000）。
        logger:     可选的日志记录器，用于输出进度。
        desc:       进度描述文字（如 ``"银行新闻分类"``）。

    Returns:
        pd.DataFrame: 所有批次处理结果纵向拼接后的 DataFrame。
    """
    if n_jobs == -1:
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    # 使用 numpy array_split 避免逐批 iloc 切片的内存拷贝
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    task_desc = desc or "批次处理"
    if logger:
        logger.info(
            f"{task_desc}: 共 {num_batches} 个批次，"
            f"每批次 {batch_size} 行，使用 {n_jobs} 个并行进程"
        )

    # 使用 joblib 并行处理，generator 模式支持实时进度回调
    results = []
    completed = 0
    for result in Parallel(n_jobs=n_jobs, return_as="generator")(
        delayed(func)(batch) for batch in df_batches
    ):
        results.append(result)
        completed += 1
        if logger and (completed % max(1, num_batches // 10) == 0 or completed == num_batches):
            progress_pct = (completed / num_batches) * 100
            logger.info(f"{task_desc}: 进度 {completed}/{num_batches} ({progress_pct:.1f}%)")

    return pd.concat(results)

# ============================================================================
# 7. CSV 预览安全落盘
# ============================================================================

def safe_save_preview_csv(df: pd.DataFrame, preview_path: str, logger=None):
    """安全保存预览用的 CSV 文件。
    
    遭遇 PermissionError (例如文件正被 Excel 打开占用) 时，
    仅产生警告或打印错误信息，确保主计算流水线不会因此中断崩溃。
    默认保存前 5000 行。
    """
    try:
        df_preview = df.head(5000) if hasattr(df, 'head') else df
        df_preview.to_csv(preview_path, index=False, encoding='utf-8-sig')
        if logger:
            logger.info(f"已生成预览文件: {preview_path}")
    except PermissionError as e:
        if logger:
            logger.warning(f"无法保存预览文件 (可能正被其它软件占用): {preview_path} | {e}")
    except Exception as e:
        if logger:
            logger.error(f"保存预览文件时发生未知错误: {preview_path} | {e}")


# ============================================================================
# 8. 数据集保存（parquet + csv 双格式）
# ============================================================================

def save_dataset(df: pd.DataFrame, output_path: str, logger=None):
    """将 DataFrame 保存为 parquet 文件，并同时输出对应的 CSV 预览文件。

    Args:
        df:           待保存的 DataFrame。
        output_path:  目标 .parquet 文件的完整路径。
        logger:       可选的日志记录器。

    行为：
        - 自动创建输出目录（若不存在）。
        - 保存完整数据为 parquet。
        - 同目录下生成同名 .csv 文件（utf-8-sig 编码，供 Excel 预览）。
        - 若 CSV 写入因权限原因失败，仅输出警告，不中断流程。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        df.to_parquet(output_path, index=False)
        if logger:
            logger.info(f"已保存 parquet 文件: {output_path}  ({len(df):,} 行)")
    except Exception as e:
        if logger:
            logger.error(f"保存 parquet 文件失败: {output_path} | {e}")
        raise

    # 同步输出 CSV 预览（非关键路径，失败不终止）
    csv_path = os.path.splitext(output_path)[0] + ".csv"
    safe_save_preview_csv(df, csv_path, logger)


# ============================================================================
# 9. 流水线阶段子进程执行器
# ============================================================================

def run_stage(stage_script: str, stage_name: str, logger,
              base_dir: str | None = None,
              timeout: int = 3600) -> tuple:
    """运行单个流水线阶段脚本（作为子进程）。

    Args:
        stage_script: 阶段脚本文件名（如 ``"00_preprocessing.py"``）。
        stage_name:   阶段显示名称（用于日志）。
        logger:       日志记录器实例。
        base_dir:     脚本所在目录。若为 None，使用调用方所在目录。
        timeout:      子进程超时秒数（默认 3600 秒）。超时后强制终止。

    Returns:
        tuple: (success: bool, elapsed_seconds: float)
    """
    import sys
    import subprocess

    if base_dir is None:
        # 回退：使用 helpers.py 的父目录（news_process/）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    script_path = os.path.join(base_dir, stage_script)

    if not os.path.exists(script_path):
        logger.error(f"阶段脚本未找到: {script_path}")
        return False, 0.0

    logger.info(f"{'─'*60}")
    logger.info(f"▶ 开始执行: {stage_name} ({stage_script})")
    logger.info(f"{'─'*60}")
    log_memory_usage(logger, f"阶段 {stage_name} 开始前")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=timeout,
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            logger.info(f"✓ {stage_name} 执行成功（耗时 {elapsed:.1f}s）")
            return True, elapsed
        else:
            logger.error(f"✗ {stage_name} 执行失败（返回码 {result.returncode}）")
            # 输出最后 30 行 stderr 用于快速诊断
            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                last_lines = stderr_lines[-30:]
                logger.error("最后 30 行 stderr:")
                for line in last_lines:
                    logger.error(f"  | {line}")
            return False, elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 执行超时（超过 {timeout}s），已强制终止")
        return False, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 执行异常: {e}")
        return False, elapsed