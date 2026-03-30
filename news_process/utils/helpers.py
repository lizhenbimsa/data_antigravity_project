"""
utils/helpers.py - 新闻处理流水线公共基础设施模块
==================================================

本模块是整个流水线的"地基"--所有 16 个阶段脚本(00-41)均依赖
此处提供的配置加载、日志系统、计时装饰器和并行处理工具。
修改本模块时需格外谨慎, 因为任何变更都会传播到全部下游阶段。

提供以下核心功能:
  1. load_config()           - YAML 配置文件加载, 自动解析相对路径为绝对路径,
                               替换 ${VAR} 环境变量占位符, 加载 .env 文件
  2. setup_logging()         - 日志记录器配置: RotatingFileHandler 文件轮转
                               + 终端 ANSI 彩色输出, 支持子进程安全模式
  3. log_and_time()          - 函数执行计时与 I/O 摘要装饰器: 自动记录
                               输入/输出行数、耗时、内存变化
  4. log_memory_usage()      - 当前进程 RSS 内存使用快照 + 系统可用内存
  5. log_stage_summary()     - 阶段级别统计摘要(行数变化、保留率、耗时)
  6. parallelize_dataframe() - 基于 joblib 的 DataFrame 并行分批处理
  7. safe_save_preview_csv() - 权限安全的 CSV 预览文件写入
  8. save_dataset()          - Parquet + CSV 双格式持久化
  9. run_stage()             - 子进程隔离执行单个阶段脚本(含超时保护)

设计哲学:
  - **子进程隔离**: 每个阶段以独立子进程运行(run_stage),
    崩溃不影响主调度器, 内存由操作系统自动回收。
  - **日志安全**: 子进程使用 console_only 模式, 避免多进程并发写
    同一日志文件导致数据损坏(Windows 环境尤为关键)。
  - **幂等性**: load_config() 可被多次调用, 每次返回独立字典副本。
  - **防御式编程**: CSV 预览写入使用异常捕获, 永远不因非关键 I/O
    失败而中断主流水线。

依赖:
  - pyyaml   - YAML 配置解析
  - pandas   - DataFrame 操作
  - joblib   - 多进程并行执行(loky 后端)
  - psutil   - 跨平台进程/系统指标
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
#
# 设计: 采用两阶段解析策略
#   Phase 1: yaml.safe_load() 将 YAML 文本解析为嵌套 Python dict/list
#   Phase 2: resolve_paths() 递归遍历整个字典树, 对每个字符串值执行:
#            (a) ${VAR_NAME} -> os.environ[VAR_NAME] (环境变量替换)
#            (b) ./relative  -> /absolute/path (相对路径转绝对路径)
#
# 为什么不在 YAML 级别支持变量?
#   YAML 1.1 的 & / * 锚点语法仅支持文档内引用, 无法读取外部环境变量。
#   自定义 ${VAR} 语法提供了更灵活的运行时配置能力。
# ============================================================================

def load_config(config_path=None):
    """加载 YAML 配置文件，并将相对路径解析为绝对路径。

    支持环境变量替换：配置值中的 ``${VAR_NAME}`` 占位符将被自动替换为
    对应的环境变量值。启动时自动加载项目根目录下的 ``.env`` 文件。

    Args:
        config_path: 配置文件路径。若为 None，则自动定位到
                     ``<project_root>/config/config.yaml``。
                     若传入相对路径，则基于项目根目录解析。

    Returns:
        dict: 解析后的配置字典，所有以 ``./`` 开头的值已转为绝对路径，
              ``${VAR}`` 占位符已替换为环境变量值。

    Raises:
        FileNotFoundError: 配置文件不存在时抛出。
    """
    import re

    # 获取 utils/ 目录的父目录 → 项目根目录 (news_process/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # 加载 .env 文件（若存在），将其中的变量注入到 os.environ
    _load_dotenv(project_root)

    if config_path is None:
        config_path = os.path.join(project_root, 'config', 'config.yaml')
    else:
        if not os.path.isabs(config_path):
            config_path = os.path.join(project_root, config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 环境变量占位符模式: ${VAR_NAME}
    # 正则解释: \$\{ 匹配字面 "${", ([^}]+) 捕获花括号内的变量名, \} 匹配 "}"
    # 使用 [^}]+ (非贪婪) 确保 ${A}xxx${B} 中 A 和 B 被分别捕获
    _env_pattern = re.compile(r'\$\{([^}]+)\}')

    def _resolve_env_vars(value: str) -> str:
        """将字符串中的 ${VAR} 替换为环境变量值。"""
        def _replacer(match):
            var_name = match.group(1)
            env_val = os.environ.get(var_name, '')
            if not env_val:
                logging.getLogger(__name__).warning(
                    f"环境变量 {var_name} 未设置，配置值将为空。"
                    f"请在 .env 文件或系统环境变量中设置该值。"
                )
            return env_val
        return _env_pattern.sub(_replacer, value)

    def resolve_paths(d, root):
        """递归将 ``./`` 开头的相对路径转为绝对路径, 并替换 ``${VAR}`` 占位符。

        遍历策略: 深度优先递归, 对 dict 和 list 两种容器分别处理。
        处理优先级: 环境变量替换优先于路径解析, 因为 ${VAR} 可能
        包含相对路径前缀(如 ${DATA_ROOT}/output)。

        就地修改(in-place): 直接修改传入的 dict/list, 不创建副本,
        因为 yaml.safe_load() 已返回全新对象, 无需担心影响外部引用。
        """
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[k] = _resolve_env_vars(v)
                    elif v.startswith('./') or v.startswith('.\\'):
                        d[k] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[k], (dict, list)):
                    resolve_paths(d[k], root)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[i] = _resolve_env_vars(v)
                    elif v.startswith('./') or v.startswith('.\\'):
                        d[i] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[i], (dict, list)):
                    resolve_paths(d[i], root)

    resolve_paths(config, project_root)
    return config


def _load_dotenv(project_root: str):
    """加载项目根目录下的 .env 文件到 os.environ。

    优先使用 python-dotenv 库(功能更完善, 支持引号嵌套和注释);
    若未安装, 则回退到内置简易解析器(仅支持 KEY=VALUE 格式)。

    安全策略:
      - ``override=False`` / ``if key not in os.environ``:
        已存在的环境变量不会被 .env 覆盖。
        这确保 CI/CD 或 Docker 传入的环境变量优先于 .env 文件。
      - .env 文件不存在时静默返回, 不抛出异常。

    .env 文件示例::

        # API 密钥(每个 LLM 模型独立配置)
        GPT5NANO_API_KEY=sk-xxxxxxxx
        GEMINI3_API_KEY=AIzaSyxxxxxx
        CLAUDE4H_API_KEY=sk-ant-xxxxxxxx
    """
    env_path = os.path.join(project_root, '.env')
    if not os.path.exists(env_path):
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        # 简易 .env 解析器（无 python-dotenv 时的回退方案）
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value


# ============================================================================
# 2. 日志配置
#
# 架构设计:
#   主进程(__name__ == "__main__") -> 文件 + 控制台 双通道
#   子进程(__name__ != "__main__") -> 仅控制台(console_only=True)
#
# 为什么子进程不写文件?
#   Python 的 logging 模块在多进程(spawn 模式)下, 多个进程同时写入
#   同一日志文件会导致 I/O 竞争和数据交错损坏。Windows 环境下更为严重,
#   因为 Windows 默认对文件加排他锁。使用 console_only 模式让子进程
#   的日志通过 subprocess.PIPE 被主进程捕获并统一写入。
#
# 轮转策略:
#   RotatingFileHandler 在单个日志文件达到 max_bytes(默认 50MB)时,
#   自动轮转为 .log.1, .log.2, ... 最多保留 backup_count 份。
#   这防止长时间运行的流水线生成过大的日志文件。
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
        # 不在 __init__ 中设置固定 fmt 字符串:
        # 因为不同日志级别需要不同颜色, format() 方法会在每次调用时
        # 根据 record.levelno 动态拼接带颜色的格式串
        super().__init__(datefmt=datefmt)
        # 毫秒格式: '2026-03-30 11:30:00.123'(3 位毫秒精度)
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

    # 文件处理器(仅主进程使用, 带轮转)
    # 子进程(ProcessPoolExecutor spawn 模式)使用 console_only=True,
    # 避免多进程并发写同一日志文件导致数据损坏
    if not console_only:
        log_file = os.path.join(log_dir, f"{stage_name}.log")
        # 首次运行时清空旧日志(file_mode='w'), 确保每次流水线执行
        # 从干净的日志文件开始。之后由 RotatingFileHandler 管理轮转。
        # 注意: RotatingFileHandler 本身不支持 mode='w'(截断模式),
        # 因此需要手动清空文件后再以 mode='a' 创建 handler。
        if file_mode == 'w' and os.path.exists(log_file):
            try:
                open(log_file, 'w').close()  # 清空文件(截断为 0 字节)
            except OSError:
                pass  # Windows 下文件可能被其他进程锁定, 静默跳过
        fh = RotatingFileHandler(
            log_file, mode='a',            # 追加模式(配合手动清空实现截断语义)
            maxBytes=max_bytes,             # 单文件上限(默认 50MB)
            backupCount=backup_count,       # 保留轮转备份数(默认 3 份)
            encoding='utf-8'                # 确保中文日志正确编码
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
#
# 用法示例:
#   @log_and_time(logger)
#   def process_data(df: pd.DataFrame) -> pd.DataFrame:
#       ...
#
# 装饰后, 函数调用会自动产生如下日志:
#   --- 开始执行: process_data ---
#   输入DataFrame行数: 170,000
#   --- 执行完毕: process_data | 耗时: 12.34s | 内存变化: +45.2MB |
#       结果: 输出DataFrame行数: 52,000 (已过滤 118,000 行) ---
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

            # --- 智能输入日志: 自动检测第一个 DataFrame 参数并记录行数 ---
            # 遍历位置参数和关键字参数, 找到第一个 pd.DataFrame 实例。
            # 这样无论函数签名如何, 装饰器都能自适应地记录输入规模。
            input_df = None
            all_args = list(args) + list(kwargs.values())
            for arg in all_args:
                if isinstance(arg, pd.DataFrame):
                    input_df = arg
                    logger.info(f"输入DataFrame行数: {len(input_df):,}")
                    break

            # 记录起始内存(RSS = Resident Set Size, 进程实际占用的物理内存)
            # 通过比较函数执行前后的 RSS 差值, 可以粗略估计函数的内存开销。
            # 注意: RSS 包含共享库内存, 且受 GC 时机影响, 仅作参考。
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
                # 内存变化量 = 执行后 RSS - 执行前 RSS, 转换为 MB
                # 正值表示内存增长(可能有新对象未被 GC),
                # 负值表示内存释放(函数内 del 或 GC 触发)
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
#
# 在流水线的关键检查点(如数据加载后, 大批量处理后, 模型加载后)
# 调用 log_memory_usage() 记录当前内存状态, 帮助识别:
#   - 内存泄漏(RSS 持续增长且不回落)
#   - 内存瓶颈(Available 接近 0 时可能触发交换/OOM)
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
#
# 并行策略说明:
#   - 使用 joblib.Parallel 的 loky 后端(默认), 通过 spawn 模式
#     创建子进程, 避免 fork 模式在 macOS 和 Windows 上的不安全性。
#   - 每个子进程获得 DataFrame 切片的独立副本(pickle 序列化),
#     进程间无共享状态, 天然线程安全。
#   - return_as="generator" 模式支持实时进度回调, 而非等待全部
#     批次完成后才返回结果。
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
        # 保留 1 个 CPU 核心给操作系统和主进程, 避免系统卡顿
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    # 分批策略: 将 DataFrame 按 batch_size 行切分为多个批次
    # 公式: ceil(len(df) / batch_size) 等价于 (len(df) - 1) // batch_size + 1
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    task_desc = desc or "批次处理"
    if logger:
        logger.info(
            f"{task_desc}: 共 {num_batches} 个批次，"
            f"每批次 {batch_size} 行，使用 {n_jobs} 个并行进程"
        )

    # 使用 joblib 并行处理:
    #   return_as="generator" 使 Parallel 返回一个生成器而非列表,
    #   每完成一个批次就 yield 结果, 支持实时进度回调。
    #   对比 return_as="list"(默认), 生成器模式不需要等待全部
    #   批次完成, 用户可以更早看到进度信息。
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
#
# 设计意图:
#   CSV 文件仅用于人工快速预览(如在 Excel 中查看前 5000 行),
#   而非作为流水线的正式传输格式(Parquet 承担此职责)。
#   因此, CSV 写入失败(如文件被 Excel 占用)不应中断主流水线。
#
# Windows 特有问题:
#   当用户在 Excel 中打开 .csv 文件时, Windows 会对该文件加排他锁,
#   此时 Python 写入会抛出 PermissionError。本函数通过 try/except
#   捕获此异常, 仅输出警告而不中断流程。
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
# 8. 数据集保存(Parquet + CSV 双格式)
#
# 为什么选择 Parquet 作为主格式?
#   1. 列式存储: 读取特定列时仅加载所需列数据, I/O 减少 80%+
#   2. Snappy 压缩: 默认启用, 压缩比约 3-5x, 无需显式解压
#   3. 保留类型信息: string / int64 / datetime 等类型在读写间
#      不会丢失(CSV 会将所有值读为字符串)
#   4. 元数据内嵌: 行数等统计量可通过 footer metadata 获取,
#      无需加载全部数据(pipeline_reporting.py 利用此特性)
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
#
# 为什么使用子进程执行而非直接 import?
#   1. **内存隔离**: 每个阶段在独立进程地址空间中运行,
#      阶段完成后操作系统自动回收全部内存, 避免累积泄漏。
#      对于处理 ~37GB 原始数据的流水线, 这是关键设计。
#   2. **错误隔离**: 某个阶段的段错误、OOM Kill 不会影响
#      主调度器进程(run_pipeline_function.py)。
#   3. **全局状态清洁**: GPU 显存、jieba 全局词典、OpenCC 转换器等
#      进程级资源在阶段结束后自动释放, 无需手动清理。
#   4. **超时保护**: timeout 参数防止单个阶段无限挂起。
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
        # subprocess.run 参数说明:
        #   sys.executable: 使用当前 Python 解释器(确保虚拟环境一致性)
        #   capture_output=True: 捕获 stdout/stderr(不直接打印到终端)
        #   text=True: 将 stdout/stderr 以字符串而非 bytes 返回
        #   encoding='utf-8': 确保中文输出正确解码
        #   errors='replace': 遇到无法解码的字节时替换为 '?', 而非崩溃
        #   timeout: 超时秒数, 超过后抛出 TimeoutExpired 并终止子进程
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