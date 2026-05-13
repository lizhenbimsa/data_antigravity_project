"""news_process.pipeline.preprocess.load — 加载层 (AC 自动机 + 单文件并行入口).

Phase 4b 从 ``runner.py`` 提取。包含:
- ``_build_ac_automaton`` / ``_ac_contains_any`` — AC 多模式匹配 helper
- ``BANK_KW_AUTOMATON`` — 模块级单例, 在 import 时一次性构建
- ``_process_single_file`` — ProcessPoolExecutor 工作进程入口, 处理单个 XLSX

依赖关系:
    load.py ← _constants.py
    load.py ← filter.py (Python 子模块, 间接调用)
    load.py ← normalize.py (clean_text_batch)

为打破"_process_single_file 调 filter.py 调 load.py" 的潜在循环, 我们让
filter.py *不再* 在模块顶部 import load.py, 而是改成 lazy import。这样
load.py 仅依赖 _constants 与 normalize, 形成单向 DAG。
"""

from __future__ import annotations

import os
import warnings

import ahocorasick
import numpy as np
import pandas as pd

from news_process.pipeline.preprocess._constants import (
    BANK_KEYWORDS,
    CHINESE_CHAR_PATTERN,
    PARAMS,
    REQUIRED_COLUMNS,
    SHEET_NAME,
    logger,
)

# ============================================================================
# 1. Aho-Corasick 自动机 (多模式匹配, O(n) 时间复杂度)
# ============================================================================
# 技术原理: AC 自动机在文本上的一次线性扫描中同时匹配所有关键词,
# 时间复杂度 O(文本长度 + 匹配数), 相比逐关键词正则匹配的
# O(文本长度 × 关键词数) 有数量级提升。


def _build_ac_automaton(keywords):
    """构建 Aho-Corasick 自动机, 用于 O(n) 时间同时匹配所有关键词.

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


def _ac_contains_any(text: str, automaton) -> bool:
    """O(n) 时间检查文本是否包含自动机中的任一关键词.

    Args:
        text:      待检查的文本。
        automaton: 已构建的 AC 自动机。

    Returns:
        bool: 文本中是否包含至少一个关键词。
    """
    for _ in automaton.iter(text.lower()):
        return True
    return False


BANK_KW_AUTOMATON = _build_ac_automaton(BANK_KEYWORDS) if BANK_KEYWORDS else None
if BANK_KW_AUTOMATON is not None:
    logger.info(f"Aho-Corasick 自动机构建完成({len(BANK_KEYWORDS)} 个关键词)")


# ============================================================================
# 2. 单文件处理 (并行工作进程入口)
# ============================================================================


def _process_single_file(file_path: str) -> pd.DataFrame | None:
    """读取并清洗单个 XLSX 文件.

    设计为在 ``ProcessPoolExecutor`` 的工作进程中运行(spawn 模式)。
    每个文件独立处理, 进程间无共享状态。

    处理流程: Excel 读取 → 过滤 → 文本标准化 → 长度过滤

    Args:
        file_path: XLSX 文件的绝对路径。

    Returns:
        pd.DataFrame | None: 处理后的 DataFrame, 或 None(处理失败/数据为空)。
    """
    # Lazy imports to avoid module-load-time circulars:
    # - filter.py imports BANK_KW_AUTOMATON from this module
    # - normalize.py is a sibling that depends only on _constants
    from news_process.pipeline.preprocess.filter import _clean_and_filter_dataframe
    from news_process.pipeline.preprocess.normalize import clean_text_batch

    file_name = os.path.basename(file_path)
    try:
        logger.info(f"--- 开始处理: {file_name} ---")

        # 使用 calamine 引擎(基于 Rust, 比 openpyxl 快 5-10x)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df_chunk = pd.read_excel(
                file_path, sheet_name=SHEET_NAME,
                engine="calamine", usecols=REQUIRED_COLUMNS
            )

        logger.info(f"  加载 {len(df_chunk):,} 行, 开始过滤...")

        # ── 初步过滤 ──
        df_cleaned = _clean_and_filter_dataframe(df_chunk)
        del df_chunk  # 及早释放原始数据内存

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 过滤后无有效数据, 跳过")
            return None

        # ── 文本标准化 ──
        logger.info(f"  开始文本标准化({len(df_cleaned):,} 行)...")
        df_cleaned = clean_text_batch(df_cleaned)

        # 统计疑似代码/结构化文档(仅记录, 不过滤)
        if 'suspected_code_doc' in df_cleaned.columns:
            suspect_count = df_cleaned['suspected_code_doc'].sum()
            if suspect_count > 0:
                logger.info(f"  疑似代码/结构化文档: {suspect_count} 条")
            df_cleaned.drop(columns=['suspected_code_doc'], inplace=True)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 标准化后无有效数据, 跳过")
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

        # 内容汉字数过滤(上下限合并为一次计算, 避免创建两个中间布尔 Series)
        rows_before = len(df_cleaned)
        content_chinese_len = df_cleaned['内容'].astype(str).str.count(CHINESE_CHAR_PATTERN)
        df_cleaned = df_cleaned[
            (content_chinese_len >= CONTENT_MIN_LEN) & (content_chinese_len <= CONTENT_MAX_LEN)
        ]
        logger.info(
            f"  [内容长度 {CONTENT_MIN_LEN}~{CONTENT_MAX_LEN}] "
            f"移除 {rows_before - len(df_cleaned):,} 行 → 剩余 {len(df_cleaned):,}"
        )

        # Schema 安全检查: 确保所有 object 列转为 string
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].fillna('').astype(str)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 长度过滤后无有效数据, 跳过")
            return None

        logger.info(f"--- 完成: {file_name} → 保留 {len(df_cleaned):,} 行 ---")
        return df_cleaned

    except Exception as e:
        logger.error(f"处理文件 {file_name} 时出错: {e}", exc_info=True)
        return None


# numpy is needed for the AC mask in _clean_and_filter_dataframe but
# imported here too to make sure ProcessPoolExecutor workers re-import it
# fresh on spawn (defensive against subtle import-order timing issues).
_ = np  # silence "imported but unused"


__all__ = [
    '_build_ac_automaton',
    '_ac_contains_any',
    'BANK_KW_AUTOMATON',
    '_process_single_file',
]
