"""
00_preprocessing.py — 第一阶段：数据预处理流水线
=====================================================

处理对象：
    176 个 XLSX 文件（~37GB, ~1700万条媒体报道记录）

处理流程：
    1. 并行加载 XLSX → pd.DataFrame（使用 calamine 引擎，Rust 实现，比 openpyxl 快 5-10x）
    2. 初步过滤（地域 / 媒体类型 / 缺失值 / 广告关键词 / 银行关键词保留）
    3. 文本标准化（编码修复 / 繁简转换 / 全角半角 / HTML去除 / 噪声去除）
    4. 长度过滤（标题和内容的汉字数上下限）
    5. 增量缓存（已处理文件写入 Parquet 缓存，避免重复处理）
    6. 精确去重（标题+内容完全匹配，按媒体权重优先保留）
    7. 近似去重（MinHash LSH + 5工作日时间窗口，Jaccard ≥ 0.8 视为重复）

性能特性：
    - ProcessPoolExecutor 多进程并行处理独立 XLSX 文件
    - Aho-Corasick 自动机实现 O(n) 银行关键词匹配
    - 预编译正则合并（单次 re.sub 替代多次调用）
    - pandarallel 并行 MinHash 生成
    - 增量缓存避免重复处理
    - Parquet + Snappy 压缩减少磁盘 I/O

输入：
    config.yaml 中 ``paths.raw_data_dir`` 指定的目录下所有 .xlsx 文件

输出：
    config.yaml 中 ``paths.output_dir / filenames.output_00_preprocessing`` 指定的 Parquet 文件

依赖：
    pandas, pyarrow, openpyxl/calamine, ftfy, opencc-python-reimplemented,
    ahocorasick, selectolax, pandarallel, datasketch, tqdm
"""

import os
import re
import gc
import glob
import time
import string
import concurrent.futures
import json
from functools import partial
from typing import Any, Callable, Dict, Set

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import warnings
import pandas as pd
import ftfy
import opencc
import ahocorasick
from selectolax.parser import HTMLParser
from pandarallel import pandarallel
from datasketch import MinHash, MinHashLSH

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from utils.helpers import (
    load_config, setup_logging, log_and_time,
    parallelize_dataframe, log_memory_usage, log_stage_summary,
    safe_save_preview_csv
)

# ============================================================================
# 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "00_preprocessing"
PARAMS = CONFIG['preprocessing']

# 子进程（ProcessPoolExecutor spawn 模式）重新导入本模块时，
# 使用 console_only 模式避免多进程并发写同一日志文件导致损坏
_is_subprocess = (__name__ != "__main__")
logger = setup_logging(STAGE_NAME, CONFIG['paths']['log_dir'], console_only=_is_subprocess)

# 去重相关配置
DEDUP_PARAMS = CONFIG.get('deduplication', {})
nb_workers = DEDUP_PARAMS.get("parallel_workers", os.cpu_count() or 1)
pandarallel.initialize(progress_bar=False, nb_workers=nb_workers)

# ============================================================================
# 从配置中提取常量（模块加载时执行一次，避免运行时重复查找）
# ============================================================================

KEY_COLUMNS = PARAMS.get('key_columns_for_na_check', [])
MEDIA_TYPES_TO_EXCLUDE = PARAMS.get('media_types_to_exclude', [])
REQUIRED_COLUMNS = PARAMS.get('required_columns', [])
SHEET_NAME = PARAMS.get('sheet_name', 'Sheet1')
MAINLAND_CHINA_REGIONS = PARAMS.get('mainland_china_regions', [])
AD_KEYWORDS = PARAMS.get('ad_keywords', [])

# 文本标准化配置
NORMALIZATION_PARAMS = CONFIG.get('normalization', {})
CLEANING_PARAMS = CONFIG.get('normalization', {})

# OpenCC 转换器（延迟初始化：每个工作进程首次调用时创建，避免 fork 不安全）
_worker_cc = None

# ============================================================================
# 预编译翻译表（一次构建，全局复用）
# ============================================================================
# 技术原理：str.translate() 使用 C 级别的字符映射表，
# 单次调用可同时完成全角→半角和引号标准化，比分步 str.replace() 快 3-5x。

_FULL_CHARS = (
    '０１２３４５６７８９'
    'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    '－（）～！＠＃￥％︿＆＊＋＝＼｜，．？＜＞｛｝【】；：　'
)
_HALF_CHARS = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    "-()~!@#$%^&*+=\\|,.?<>{}[];: "
)
_full_to_half_table = str.maketrans(_FULL_CHARS, _HALF_CHARS)

# 中文引号 → ASCII 直引号
_quote_table = {
    0x201C: '"',  0x201D: '"',       # 左右双弯引号
    ord('「'): '"', ord('」'): '"',  # 日文引号
    ord('『'): '"', ord('』'): '"',  # 日文书名号
}

# 合并为单个翻译表
COMBINED_TRANS = {**_full_to_half_table, **_quote_table}

TEXT_COLUMNS = ['标题', '内容']

# ============================================================================
# 加载外部资源文件
# ============================================================================

# 噪声模式正则（从 JSON 文件加载，支持热更新而无需改代码）
try:
    with open(CONFIG['paths']['noise_patterns_file'], 'r', encoding='utf-8') as f:
        noise_data = json.load(f)
        # 跳过以 '_' 开头的注释键
        noise_patterns_list = [v for k, v in noise_data.items() if not k.startswith('_')]
        logger.info(f"已加载 {len(noise_patterns_list)} 个噪声模式")
except Exception as e:
    logger.error(f"无法加载噪声模式文件: {e}")
    noise_patterns_list = []

# 银行关键词（用于内容预过滤，只保留提及银行的新闻）
try:
    with open(CONFIG['paths']['bank_keywords_file'], 'r', encoding='utf-8') as f:
        BANK_KEYWORDS = json.load(f)
        logger.info(f"已加载 {len(BANK_KEYWORDS)} 个银行关键词")
except Exception as e:
    logger.error(f"无法加载银行关键词文件: {e}")
    BANK_KEYWORDS = []

# ============================================================================
# Aho-Corasick 自动机（多模式匹配，O(n) 时间复杂度）
# ============================================================================
# 技术原理：AC 自动机在文本上的一次线性扫描中同时匹配所有关键词，
# 时间复杂度 O(文本长度 + 匹配数)，相比逐关键词正则匹配的
# O(文本长度 × 关键词数) 有数量级提升。

def _build_ac_automaton(keywords):
    """构建 Aho-Corasick 自动机，用于 O(n) 时间同时匹配所有关键词。

    Args:
        keywords: 关键词列表。

    Returns:
        ahocorasick.Automaton: 构建好的自动机实例。
    """
    A = ahocorasick.Automaton()
    for kw in keywords:
        A.add_word(kw.lower(), kw)
    A.make_automaton()
    return A


BANK_KW_AUTOMATON = _build_ac_automaton(BANK_KEYWORDS) if BANK_KEYWORDS else None
if BANK_KW_AUTOMATON is not None:
    logger.info(f"Aho-Corasick 自动机构建完成（{len(BANK_KEYWORDS)} 个关键词）")


def _ac_contains_any(text: str, automaton) -> bool:
    """O(n) 时间检查文本是否包含自动机中的任一关键词。

    Args:
        text:      待检查的文本。
        automaton: 已构建的 AC 自动机。

    Returns:
        bool: 文本中是否包含至少一个关键词。
    """
    for _ in automaton.iter(text.lower()):
        return True
    return False


# ============================================================================
# 预编译正则表达式（避免每个文件/每行重复编译）
# ============================================================================

# 各类噪声文本的匹配模式
control_char_pattern_str = r'[\x00-\x1f\x7f-\x9f]'
url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
phone_pattern = re.compile(r'(?:\+?86)?1[3-9]\d{9}|\d{3,4}[-\s]?\d{7,8}')
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
    "\U00002700-\U000027BF\U00002600-\U000026FF\U0001F1E6-\U0001F1FF"
    "]+", flags=re.UNICODE
)

# 噪声模式合并为单个正则（减少 re.sub 调用次数）
all_removal_patterns = noise_patterns_list + [control_char_pattern_str]
try:
    combined_removal_pattern = (
        re.compile('|'.join(all_removal_patterns))
        if all_removal_patterns
        else re.compile(r'\b\B')  # 永远不匹配的空模式
    )
    logger.info("噪声模式正则编译成功")
except re.error as e:
    logger.error(f"噪声模式正则编译失败: {e}")
    combined_removal_pattern = re.compile(control_char_pattern_str)

# 统一去除正则：URL + Email + 电话 + Emoji + 噪声 + 控制字符
# 合并为单个正则，一次 re.sub 调用完成所有清除
try:
    UNIFIED_CLEANUP_PATTERN = re.compile(
        '|'.join([url_pattern.pattern, email_pattern.pattern,
                  phone_pattern.pattern, emoji_pattern.pattern])
        + '|' + combined_removal_pattern.pattern
    )
    logger.info("统一清除正则编译成功")
except re.error as e:
    logger.error(f"统一清除正则编译失败，将回退到分步模式: {e}")
    UNIFIED_CLEANUP_PATTERN = None

# 尾部清理：重复字符 + 冗余标点 + 空白序列，合并为单个正则
_TAIL_CLEANUP_PATTERN = re.compile(
    r'(.)\1{2,}'                        # 重复字符 (如 'aaaaa' → 'aa')
    r'|([,，.。!！?？;；:：、])\2+'     # 冗余标点 (如 '。。。' → '。')
    r'|\s+'                              # 空白字符序列 → 单个空格
)


def _tail_cleanup_repl(m: re.Match) -> str:
    """``_TAIL_CLEANUP_PATTERN`` 的替换回调函数。

    替换规则：
      - 重复字符 → 保留 2 个（如 ``aaa`` → ``aa``）
      - 冗余标点 → 保留 1 个（如 ``。。。`` → ``。``）
      - 空白序列 → 单个空格
    """
    if m.group(1):
        return m.group(1) * 2
    elif m.group(2):
        return m.group(2)
    else:
        return ' '


# 广告关键词模式：支持字符间插入空白的弹性匹配（如"广 告"也能匹配"广告"）
AD_PATTERN = None
if AD_KEYWORDS:
    flexible_patterns = [r'\s*'.join(list(kw)) for kw in AD_KEYWORDS]
    AD_PATTERN = re.compile('|'.join(flexible_patterns), re.IGNORECASE)

# 中国大陆地区名匹配
REGION_PATTERN = re.compile('|'.join(MAINLAND_CHINA_REGIONS)) if MAINLAND_CHINA_REGIONS else None

# 汉字字符匹配（用于统计标题/内容中的汉字数量）
CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff]')

# 媒体类型排除集（frozenset 的 __contains__ 比 list 快 O(1) vs O(n)）
MEDIA_TYPES_EXCLUDE_SET = frozenset(MEDIA_TYPES_TO_EXCLUDE)


# ============================================================================
# 数据过滤
# ============================================================================

def _clean_and_filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """对单个 DataFrame 执行全部初始过滤操作。

    过滤顺序经过精心设计，按数据淘汰率从高到低排列，
    确保高淘汰率的过滤先执行，最大化减少后续步骤的数据量：
      1. 媒体地域过滤（淘汰率最高，~60-70%）
      2. 媒体类型过滤（~5-10%）
      3. 缺失值过滤（~2-5%）
      4. 广告关键词过滤（~1-3%）
      5. 银行关键词保留过滤（Aho-Corasick，~30-50%）
      6. Schema 统一（object → string，不改变行数）

    Args:
        df: 从 Excel 文件读取的原始 DataFrame。

    Returns:
        pd.DataFrame: 过滤和标准化后的 DataFrame。
    """
    if df.empty:
        return df

    # 1. 媒体地域过滤：仅保留中国大陆地区的媒体
    if REGION_PATTERN is not None:
        rows_before = len(df)
        region_cleaned = df['国家地区/省份'].astype(str).str.replace(r'\s+', '', regex=True)
        df = df[region_cleaned.str.contains(REGION_PATTERN, na=False, regex=True)]
        logger.info(f"  [1/5 地域过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 2. 媒体类型过滤：排除 APP、微博、政府等
    rows_before = len(df)
    df = df[~df['媒体类型(中文)'].isin(MEDIA_TYPES_EXCLUDE_SET)]
    logger.info(f"  [2/5 类型过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 3. 关键字段缺失值过滤（标题、内容、媒体名、日期任一为空则移除）
    rows_before = len(df)
    df = df.dropna(subset=KEY_COLUMNS)
    logger.info(f"  [3/5 缺失值过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 4. 广告关键词过滤（检查标题、版面、栏名三个字段）
    if AD_PATTERN is not None:
        for field_name, col_name in [('标题', '标题'), ('版面', '版面'), ('栏名', '栏名')]:
            rows_before = len(df)
            df = df[~df[col_name].astype(str).str.contains(AD_PATTERN, na=False, regex=True)]
            if rows_before - len(df) > 0:
                logger.info(
                    f"  [4/5 广告过滤-{field_name}] "
                    f"移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}"
                )

    # 5. 银行关键词保留过滤（Aho-Corasick O(n) 复杂度）
    # 只保留内容中提及至少一个银行关键词的新闻
    if BANK_KW_AUTOMATON is not None:
        rows_before = len(df)
        content_values = df['内容'].astype(str).values
        # 向量化版本：使用 numpy 布尔数组避免 Python 级别循环开销
        mask = np.fromiter(
            (_ac_contains_any(t, BANK_KW_AUTOMATON) for t in content_values),
            dtype=bool,
            count=len(content_values)
        )
        df = df[mask]
        logger.info(f"  [5/5 银行关键词过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 6. Schema 统一：object 列 → string，确保后续 Parquet 序列化安全
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('').astype(str)

    return df


# ============================================================================
# 文本标准化
# ============================================================================

def _strip_html(text: str) -> str:
    """去除 HTML 标签，保留纯文本内容。

    使用 selectolax（基于 C 的 Modest 引擎）解析 HTML，
    比 BeautifulSoup 快约 10-30x。

    Args:
        text: 可能包含 HTML 标签的文本。

    Returns:
        str: 去除 HTML 标签后的纯文本。
    """
    return HTMLParser(text).text(separator=' ', strip=True) if '<' in text else text


def _clean_single_text(text: str, cc) -> str:
    """对单个文本执行完整的清洗流水线。

    将 ftfy 编码修复、繁简转换、全角转半角、HTML去除、噪声去除、
    尾部清理合并为单个函数调用，减少 Series 中间对象创建。

    Args:
        text: 待清洗的原始文本。
        cc:   OpenCC 转换器实例。

    Returns:
        str: 清洗后的文本。
    """
    if not text:
        return text
    # 步骤 1: 编码修复（修复 mojibake 乱码）
    text = ftfy.fix_text(text)
    # 步骤 2: 繁体转简体
    text = cc.convert(text)
    # 步骤 3: 全角转半角 + 引号标准化（单次 translate 调用）
    text = text.translate(COMBINED_TRANS)
    # 步骤 4: HTML 标签去除
    text = _strip_html(text)
    # 步骤 5: 噪声去除（URL/Email/电话/Emoji/控制字符）
    if UNIFIED_CLEANUP_PATTERN is not None:
        text = UNIFIED_CLEANUP_PATTERN.sub('', text)
    else:
        for pat in [url_pattern, email_pattern, phone_pattern,
                    emoji_pattern, combined_removal_pattern]:
            text = pat.sub('', text)
    # 步骤 6: 尾部清理（重复字符+冗余标点+空白标准化）
    text = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, text).strip()
    return text


def clean_text_batch(df_batch: pd.DataFrame) -> pd.DataFrame:
    """对 DataFrame 批次执行综合文本清洗。

    对"标题"和"内容"列执行以下处理管道：
      1. 编码修复（ftfy）— 修复 UTF-8 编码错误和 mojibake 乱码
      2. 繁体转简体（OpenCC）— t2s 配置
      3. 全角转半角 + 引号标准化 — 合并为单次 str.translate()
      4. HTML 标签去除 — selectolax 高性能解析
      5. 噪声去除 — URL/Email/电话/Emoji/控制字符/自定义噪声模式
      6. 尾部清理 — 重复字符压缩/冗余标点合并/空白标准化

    使用合并后的 ``_clean_single_text`` 函数减少 Series 中间对象创建，
    相比逐步 ``.map()`` 调用减少约 30% 的 Python 解释器开销。

    Args:
        df_batch: 包含"标题"和"内容"列的 DataFrame 批次。

    Returns:
        pd.DataFrame: 清洗后的 DataFrame（就地修改并返回）。
    """
    global _worker_cc

    batch_size = len(df_batch)
    logger.debug(f"正在处理批次（{batch_size} 行）")

    # 延迟初始化 OpenCC（每个工作进程首次调用时创建一次）
    if _worker_cc is None:
        opencc_config = NORMALIZATION_PARAMS.get('opencc_config', 't2s')
        logger.info(f"工作进程 {os.getpid()} 初始化 OpenCC（{opencc_config}）...")
        _worker_cc = opencc.OpenCC(opencc_config)

    df_batch['suspected_code_doc'] = False
    stats = {'total_chars_before': 0, 'total_chars_after': 0}

    for col in TEXT_COLUMNS:
        if col not in df_batch.columns:
            continue

        # 类型安全：确保列为字符串类型
        series = df_batch[col].fillna('') if df_batch[col].dtype == object else df_batch[col].astype(str)

        original_len = series.str.len()
        stats['total_chars_before'] += original_len.sum()

        # 合并清洗管道：单次 map 替代多次 map，减少 Series 创建开销
        series = series.map(lambda t: _clean_single_text(t, _worker_cc))

        # 检测疑似代码/结构化文档（HTML 移除后长度大幅缩减的记录）
        len_after = series.str.len()
        reduction_ratio = (original_len - len_after) / original_len.replace(0, 1)
        threshold = CLEANING_PARAMS.get('html_removal_length_threshold', 0.7)
        is_suspect = reduction_ratio > threshold
        df_batch['suspected_code_doc'] = df_batch['suspected_code_doc'] | is_suspect

        stats['total_chars_after'] += len_after.sum()
        df_batch[col] = series

    if stats['total_chars_before'] > 0:
        reduction_pct = (1 - stats['total_chars_after'] / stats['total_chars_before']) * 100
        logger.debug(
            f"字符数: {stats['total_chars_before']:,} → "
            f"{stats['total_chars_after']:,}（减少 {reduction_pct:.1f}%）"
        )

    return df_batch


# ============================================================================
# 单文件处理（并行工作进程入口）
# ============================================================================

def _process_single_file(file_path: str) -> pd.DataFrame | None:
    """读取并清洗单个 XLSX 文件。

    设计为在 ``ProcessPoolExecutor`` 的工作进程中运行（spawn 模式）。
    每个文件独立处理，进程间无共享状态。

    处理流程：Excel 读取 → 过滤 → 文本标准化 → 长度过滤

    Args:
        file_path: XLSX 文件的绝对路径。

    Returns:
        pd.DataFrame | None: 处理后的 DataFrame，或 None（处理失败/数据为空）。
    """
    file_name = os.path.basename(file_path)
    try:
        logger.info(f"--- 开始处理: {file_name} ---")

        # 使用 calamine 引擎（基于 Rust，比 openpyxl 快 5-10x）
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df_chunk = pd.read_excel(
                file_path, sheet_name=SHEET_NAME,
                engine="calamine", usecols=REQUIRED_COLUMNS
            )

        logger.info(f"  加载 {len(df_chunk):,} 行，开始过滤...")

        # ── 初步过滤 ──
        df_cleaned = _clean_and_filter_dataframe(df_chunk)
        del df_chunk  # 及早释放原始数据内存

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 过滤后无有效数据，跳过")
            return None

        # ── 文本标准化 ──
        logger.info(f"  开始文本标准化（{len(df_cleaned):,} 行）...")
        df_cleaned = clean_text_batch(df_cleaned)

        # 统计疑似代码/结构化文档（仅记录，不过滤）
        if 'suspected_code_doc' in df_cleaned.columns:
            suspect_count = df_cleaned['suspected_code_doc'].sum()
            if suspect_count > 0:
                logger.info(f"  疑似代码/结构化文档: {suspect_count} 条")
            df_cleaned.drop(columns=['suspected_code_doc'], inplace=True)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 标准化后无有效数据，跳过")
            return None

        # ── 长度过滤 ──
        TITLE_MIN_LEN = PARAMS.get('title_min_length', 2)
        CONTENT_MIN_LEN = PARAMS.get('content_min_length', 100)
        CONTENT_MAX_LEN = PARAMS.get('content_max_length', 10000)

        # 标题汉字数过滤
        rows_before = len(df_cleaned)
        title_chinese_len = df_cleaned['标题'].astype(str).str.count(CHINESE_CHAR_PATTERN)
        df_cleaned = df_cleaned[title_chinese_len >= TITLE_MIN_LEN]
        logger.info(
            f"  [标题长度≥{TITLE_MIN_LEN}] "
            f"移除 {rows_before - len(df_cleaned):,} 行 → 剩余 {len(df_cleaned):,}"
        )

        # 内容汉字数过滤（上下限合并为一次计算，避免创建两个中间布尔 Series）
        rows_before = len(df_cleaned)
        content_chinese_len = df_cleaned['内容'].astype(str).str.count(CHINESE_CHAR_PATTERN)
        df_cleaned = df_cleaned[
            (content_chinese_len >= CONTENT_MIN_LEN) & (content_chinese_len <= CONTENT_MAX_LEN)
        ]
        logger.info(
            f"  [内容长度 {CONTENT_MIN_LEN}~{CONTENT_MAX_LEN}] "
            f"移除 {rows_before - len(df_cleaned):,} 行 → 剩余 {len(df_cleaned):,}"
        )

        # Schema 安全检查：确保所有 object 列转为 string
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].fillna('').astype(str)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 长度过滤后无有效数据，跳过")
            return None

        logger.info(f"--- 完成: {file_name} → 保留 {len(df_cleaned):,} 行 ---")
        return df_cleaned

    except Exception as e:
        logger.error(f"处理文件 {file_name} 时出错: {e}", exc_info=True)
        return None


# ============================================================================
# 去重逻辑
# ============================================================================

class ArticleDeduplicator:
    """文章去重器：精确去重 + 近似去重（MinHash LSH + 时间窗口）。

    算法说明：
      ① 精确去重：基于 (标题 + 内容) 字符串完全匹配。
         在重复组内，按媒体权重降序、docid升序保留首条。

      ② 近似去重：
         - 对每篇文章计算 MinHash 签名（128 个置换），
           使用字符级 3-gram 作为特征。
         - 构建 LSH 索引（阈值 = Jaccard ≥ 0.8），O(1) 查询近似重复簇。
         - 在每个重复簇内，按日期排序，5个工作日内的后发文章标记为重复。

    复杂度分析：
      - 精确去重：O(n log n)（排序）+ O(n)（去重） = O(n log n)
      - 近似去重：O(n)（MinHash 生成，并行化）+ O(n)（LSH 插入+查询）
      - 总体空间：O(n)（MinHash 签名 + LSH 索引）

    Attributes:
        COL_WEIGHT:   媒体权重临时列名。
        COL_LENGTH:   内容长度临时列名。
        COL_COMBINED: 标题+内容合并临时列名。
    """

    COL_WEIGHT = 'temp_media_weight'
    COL_LENGTH = 'temp_content_length'
    COL_COMBINED = 'temp_title_content'
    SORT_BY_COLS = [COL_WEIGHT, 'docid', COL_LENGTH]
    SORT_ASCENDING = [False, True, False]

    # 标点和空白字符清洗表：用于 MinHash 分词前的文本规范化
    PUNCTUATION = (
        string.punctuation
        + "＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～"
        + "｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—''‛"
        + "\"\"„‟…‧﹏."
    )
    WHITESPACE = " \n\t\r\u3000"
    CLEANING_TABLE = str.maketrans('', '', PUNCTUATION + WHITESPACE)

    def __init__(self, config: Dict[str, Any], logger_instance):
        """初始化去重器。

        Args:
            config:          已解析的配置字典。
            logger_instance: 日志记录器实例。
        """
        self.params = config['deduplication']
        self.paths = config['paths']
        self.logger = logger_instance

        self.media_weights = self._load_media_weights()
        self.default_weight = self.media_weights.get("其他媒体", 10)

        self.num_perm = self.params.get('minhash_permutations', 128)
        self.threshold = self.params.get('jaccard_similarity_threshold', 0.85)
        self.ngram_size = self.params.get('ngram_size', 3)

    def _load_media_weights(self) -> Dict[str, int]:
        """从 JSON 文件加载媒体权重评分表。

        Returns:
            dict: ``{媒体名称: 权重分数}``，权重越高越优先保留。
        """
        filepath = self.paths['media_weights_file']
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"媒体权重文件未找到: {filepath}")
        except json.JSONDecodeError as e:
            self.logger.error(f"媒体权重文件格式错误: {e}")
        return {}

    def _clean_and_tokenize(self, text: str) -> Set[str]:
        """清洗文本并生成字符级 n-gram 集合作为 MinHash 特征。

        Args:
            text: 原始文本。

        Returns:
            set[str]: 字符级 n-gram 集合。
        """
        if not isinstance(text, str) or not text:
            return set()
        cleaned_text = text.translate(self.CLEANING_TABLE)
        n = self.ngram_size
        if len(cleaned_text) < n:
            return {cleaned_text} if cleaned_text else set()
        return {cleaned_text[i:i + n] for i in range(len(cleaned_text) - n + 1)}

    @staticmethod
    def _create_minhash(text: str, num_perm: int,
                        tokenizer_func: Callable[[str], Set[str]]) -> MinHash | None:
        """为单个文本创建 MinHash 签名。

        Args:
            text:           待处理文本。
            num_perm:       置换函数数量（越大越精确，越慢）。
            tokenizer_func: 分词函数，返回 token 集合。

        Returns:
            MinHash | None: MinHash 签名，或 None（空文本）。
        """
        from datasketch import MinHash
        m = MinHash(num_perm=num_perm)
        tokens = tokenizer_func(str(text))
        if not tokens:
            return None
        # 批量更新替代逐 token 循环，减少 Python 函数调用开销（2-3x 加速）
        m.update_batch([t.encode('utf8') for t in tokens])
        return m

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加去重所需的辅助列（媒体权重、内容长度、合并文本、日期）。

        Args:
            df: 待去重的 DataFrame。

        Returns:
            pd.DataFrame: 添加了辅助列的 DataFrame。
        """
        self.logger.info("添加辅助列...")
        df[self.COL_WEIGHT] = (
            df['媒体(中文)'].map(self.media_weights)
            .fillna(self.default_weight)
            .astype(int)
        )
        df[self.COL_LENGTH] = df['内容'].str.len().fillna(0).astype(int)
        df[self.COL_COMBINED] = df['标题'].fillna('') + " " + df['内容'].fillna('')

        # 日期解析（coerce 模式：无法解析的值设为 NaT）
        df['temp_datetime'] = pd.to_datetime(df['日期'], errors='coerce')
        valid_dates = df['temp_datetime'].notna().sum()
        total_rows = len(df)
        self.logger.info(
            f"日期解析: {valid_dates:,}/{total_rows:,} 有效（{valid_dates/total_rows:.1%}）"
        )
        if valid_dates < total_rows:
            self.logger.warning(
                f"{total_rows - valid_dates:,} 条日期解析失败，去重时默认保留"
            )
        return df

    def _perform_exact_deduplication(self, df: pd.DataFrame) -> pd.DataFrame:
        """精确去重：基于标题+内容完全匹配，保留媒体权重最高者。

        Args:
            df: 含辅助列的 DataFrame。

        Returns:
            pd.DataFrame: 去除精确重复后的 DataFrame。
        """
        self.logger.info("执行精确去重...")
        pre_count = len(df)
        df_sorted = df.sort_values(by=self.SORT_BY_COLS, ascending=self.SORT_ASCENDING)
        df_deduped = df_sorted.drop_duplicates(subset=[self.COL_COMBINED], keep='first')
        removed = pre_count - len(df_deduped)
        self.logger.info(
            f"精确去重完成: 移除 {removed:,} 条，剩余 {len(df_deduped):,}"
        )
        return df_deduped

    def _perform_near_deduplication(self, df: pd.DataFrame) -> pd.DataFrame:
        """近似去重：MinHash LSH + 5个工作日时间窗口。

        算法流程：
          1. 并行生成所有文档的 MinHash 签名
          2. 构建 LSH 索引
          3. 对每篇文章查询 LSH 获得相似簇
          4. 在簇内按日期排序，5个工作日内的后发文章标记为重复

        Args:
            df: 含辅助列的 DataFrame。

        Returns:
            pd.DataFrame: 去除近似重复后的 DataFrame。
        """
        self.logger.info("执行近似去重（LSH + 时间窗口）...")

        # ── Step 1: 并行生成 MinHash 签名 ──
        self.logger.info(f"生成 MinHash 签名（{self.num_perm} 个置换）...")
        create_minhash_with_params = partial(
            self._create_minhash,
            num_perm=self.num_perm,
            tokenizer_func=self._clean_and_tokenize
        )
        minhashes = df[self.COL_COMBINED].parallel_apply(create_minhash_with_params).dropna()

        if minhashes.empty:
            self.logger.warning("无有效 MinHash，跳过近似去重")
            return df

        # ── Step 2: 构建 LSH 索引 ──
        self.logger.info(f"构建 LSH 索引（{len(minhashes):,} 个文档）...")
        lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        lsh_data = list(minhashes.items())
        insert_errors = 0

        lsh_iterator = tqdm(lsh_data, desc="构建LSH索引") if TQDM_AVAILABLE else lsh_data
        for index, m_hash in lsh_iterator:
            try:
                lsh.insert(index, m_hash)
            except ValueError:
                insert_errors += 1
        if insert_errors > 0:
            self.logger.warning(f"LSH 插入跳过 {insert_errors:,} 个重复键")

        # ── Step 3: 查询 LSH 并应用时间窗口规则 ──
        self.logger.info("查询 LSH 索引，应用时间窗口去重...")
        processed_indices = set()
        all_indices_to_drop = set()
        index_to_minhash = dict(lsh_data)

        iterator = (
            tqdm(df.index, total=len(df), desc="查找重复簇")
            if TQDM_AVAILABLE else df.index
        )

        for idx in iterator:
            if idx in processed_indices:
                continue
            if idx not in index_to_minhash:
                continue

            result_cluster = lsh.query(index_to_minhash[idx])
            processed_indices.update(result_cluster)

            if len(result_cluster) <= 1:
                continue

            # 簇内排序：日期升序 → 权重降序 → docid 升序
            cluster_df = df.loc[result_cluster]
            sorted_cluster = cluster_df.sort_values(
                by=['temp_datetime', self.COL_WEIGHT, 'docid'],
                ascending=[True, False, True],
                na_position='last'
            )

            # 时间窗口去重：5个工作日内的后发相似文章视为重复
            kept_articles = []
            for row in sorted_cluster.itertuples():
                current_idx = row.Index
                current_date = row.temp_datetime
                is_redundant = False

                if pd.isna(current_date):
                    # 日期无效的文章默认保留
                    kept_articles.append((current_idx, current_date))
                    continue

                for kept_idx, kept_date in kept_articles:
                    if pd.isna(kept_date):
                        continue
                    try:
                        d1 = np.datetime64(kept_date, 'D')
                        d2 = np.datetime64(current_date, 'D')
                        if 0 <= np.busday_count(d1, d2) <= 5:
                            is_redundant = True
                            break
                    except Exception:
                        pass

                if is_redundant:
                    all_indices_to_drop.add(current_idx)
                else:
                    kept_articles.append((current_idx, current_date))

        self.logger.info(f"近似去重完成: 找到 {len(all_indices_to_drop):,} 条近似重复")
        return df.drop(index=list(all_indices_to_drop)) if all_indices_to_drop else df

    @log_and_time(logger)
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行完整去重流程（精确 + 近似）。

        Args:
            df: 待去重的 DataFrame。

        Returns:
            pd.DataFrame: 去重后的 DataFrame（辅助列已清理）。
        """
        if df.empty:
            self.logger.warning("输入为空，跳过去重")
            return df

        df_prepared = self._prepare_dataframe(df)
        df_exact = self._perform_exact_deduplication(df_prepared)
        df_near = self._perform_near_deduplication(df_exact)

        # 清理辅助列
        cols_to_drop = [self.COL_WEIGHT, self.COL_LENGTH, self.COL_COMBINED, 'temp_datetime']
        return df_near.drop(
            columns=[c for c in cols_to_drop if c in df_near.columns],
            errors='ignore'
        )


# ============================================================================
# 主处理函数
# ============================================================================

@log_and_time(logger)
def load_and_process_data(raw_data_dir: str, output_path: str) -> int:
    """并行加载和处理所有 XLSX 文件，将结果写入单个 Parquet 文件。

    处理流程：
      1. 扫描 XLSX 文件列表，检查增量缓存
      2. 读取已缓存的 Parquet 文件
      3. 并行处理未缓存的 XLSX 文件（ProcessPoolExecutor）
      4. 将处理结果追加写入输出 Parquet 文件，同时写入缓存

    Args:
        raw_data_dir: 原始 XLSX 文件目录。
        output_path:  输出 Parquet 文件路径。

    Returns:
        int: 最终写入的总行数。
    """
    xlsx_files = glob.glob(os.path.join(raw_data_dir, '*.xlsx'))
    logger.info(f"找到 {len(xlsx_files)} 个 XLSX 文件")

    if not xlsx_files:
        logger.error("未找到任何 XLSX 文件！")
        return 0

    # ── 增量缓存检查 ──
    # 已处理的文件写入 Parquet 缓存，下次运行时直接读取
    cache_dir = os.path.join(os.path.dirname(output_path), '_cache')
    os.makedirs(cache_dir, exist_ok=True)

    files_to_process = []
    cached_files = []
    for xlsx_file in xlsx_files:
        cache_path = os.path.join(
            cache_dir, os.path.basename(xlsx_file).replace('.xlsx', '.parquet')
        )
        # 缓存有效条件：缓存文件存在 且 修改时间晚于源文件
        if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(xlsx_file):
            cached_files.append(cache_path)
        else:
            files_to_process.append(xlsx_file)

    logger.info(f"增量处理: {len(cached_files)} 个已缓存，{len(files_to_process)} 个待处理")

    writer = None
    total_rows = 0

    # 工作进程数：取 CPU 核心数和配置值的较小者，防止内存溢出
    cpu_count = os.cpu_count() or 4
    num_workers = PARAMS.get('num_workers', min(cpu_count, 32))
    logger.info(f"并行工作进程: {num_workers}（CPU 核心数: {cpu_count}）")
    log_memory_usage(logger, "并行处理开始前")

    # ── Step 1: 读取缓存 ──
    if cached_files:
        logger.info(f"读取 {len(cached_files)} 个缓存文件...")
        for cache_path in cached_files:
            try:
                table = pq.read_table(cache_path)
                if writer is None:
                    writer = pq.ParquetWriter(output_path, table.schema, compression='snappy')
                writer.write_table(table)
                total_rows += table.num_rows
            except Exception as e:
                logger.warning(f"缓存 {os.path.basename(cache_path)} 读取失败，将重新处理: {e}")
                xlsx_name = os.path.basename(cache_path).replace('.parquet', '.xlsx')
                xlsx_path = os.path.join(raw_data_dir, xlsx_name)
                if os.path.exists(xlsx_path) and xlsx_path not in files_to_process:
                    files_to_process.append(xlsx_path)
        logger.info(f"缓存数据加载完成: {total_rows:,} 行")

    # ── Step 2: 并行处理新文件 ──
    if files_to_process:
        completed = 0
        total_to_process = len(files_to_process)

        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_file = {
                executor.submit(_process_single_file, f): f
                for f in files_to_process
            }

            for future in concurrent.futures.as_completed(future_to_file):
                completed += 1
                source_file = future_to_file[future]
                file_name = os.path.basename(source_file)

                try:
                    df_cleaned = future.result()
                except Exception as e:
                    logger.error(f"处理 {file_name} 异常: {e}")
                    continue

                if df_cleaned is not None and not df_cleaned.empty:
                    table = pa.Table.from_pandas(df_cleaned)
                    if writer is None:
                        writer = pq.ParquetWriter(
                            output_path, table.schema, compression='snappy'
                        )
                    writer.write_table(table)
                    total_rows += len(df_cleaned)

                    # 写入增量缓存
                    cache_path = os.path.join(
                        cache_dir, file_name.replace('.xlsx', '.parquet')
                    )
                    try:
                        pq.write_table(table, cache_path, compression='snappy')
                    except Exception as e:
                        logger.warning(f"缓存写入失败 {cache_path}: {e}")

                    del df_cleaned, table

                logger.info(
                    f"进度: [{completed}/{total_to_process}] {file_name} | "
                    f"累计 {total_rows:,} 行"
                )

                # 每处理 5 个文件执行一次垃圾回收，控制内存峰值
                if completed % 5 == 0:
                    gc.collect()

    if writer:
        writer.close()
        logger.info(f"数据加载完成，共 {total_rows:,} 行 → {output_path}")
    else:
        logger.warning("所有文件均为空或无法处理，未生成输出文件")

    log_memory_usage(logger, "并行处理完成后")
    return total_rows


# ============================================================================
# 主函数
# ============================================================================

def main() -> None:
    """主执行函数：数据加载 → 文本标准化 → 过滤 → 去重。"""
    stage_start = time.time()
    logger.info(f"{'='*70}")
    logger.info(f"=== 开始执行: {STAGE_NAME} ===")
    logger.info(f"{'='*70}")
    log_memory_usage(logger, "阶段启动")

    output_dir = CONFIG['paths']['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, CONFIG['filenames']['output_00_preprocessing'])

    # ── 数据加载、过滤和标准化 ──
    load_rows = load_and_process_data(CONFIG['paths']['raw_data_dir'], output_path)

    # ── 去重 ──
    if os.path.exists(output_path):
        logger.info("读取合并数据，执行去重...")
        df = pd.read_parquet(output_path)
        df = df.reset_index(drop=True)
        input_rows = len(df)
        log_memory_usage(logger, "去重前")

        if not df.empty:
            deduplicator = ArticleDeduplicator(config=CONFIG, logger_instance=logger)
            df = deduplicator.run(df)

            logger.info(f"写入去重结果 → {output_path}")
            table = pa.Table.from_pandas(df, preserve_index=False)
            pq.write_table(
                table, output_path,
                compression='snappy',
                row_group_size=100_000,
                use_dictionary=True,       # 字符串列字典编码，节省磁盘空间
                write_statistics=True,     # 列统计信息，加速后续谓词下推过滤
            )

            # 生成 CSV 预览（前 2000 行，便于用 Excel 快速检查）
            preview_path = output_path.replace('.parquet', '.csv')
            safe_save_preview_csv(df, preview_path, logger)

            output_rows = len(df)
        else:
            output_rows = 0
    else:
        input_rows = load_rows
        output_rows = load_rows

    # ── 阶段摘要 ──
    log_stage_summary(
        logger, STAGE_NAME, stage_start,
        input_rows=input_rows, output_rows=output_rows,
        extra_info={"加载总行数": f"{load_rows:,}"}
    )
    logger.info(f"=== 完成: {STAGE_NAME} ===")


if __name__ == "__main__":
    main()
