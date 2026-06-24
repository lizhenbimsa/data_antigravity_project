"""news_process.pipeline.preprocess.normalize — 文本标准化层.

Phase 4b 从 ``runner.py`` 提取。包含:
- ``_worker_cc`` — OpenCC 转换器, 每 ProcessPoolExecutor 工作进程独立初始化
- ``_tail_cleanup_repl`` — TAIL_CLEANUP_PATTERN 的回调
- ``_strip_html`` — selectolax 高性能 HTML 标签去除
- ``_clean_single_text`` — 完整清洗管道(单文本)
- ``clean_text_batch`` — DataFrame 批次入口

依赖关系: 仅 ``_constants.py``, 无 sibling 依赖。
"""

from __future__ import annotations

import os
import re
import time

# ftfy 是 normalize 专属依赖, 子模块顶部 import 一次即可
import ftfy
import opencc
import pandas as pd
from selectolax.parser import HTMLParser

from news_process.core.logging import pct4, sig4
from news_process.pipeline.preprocess._constants import (
    COMBINED_TRANS,
    NORMALIZATION_PARAMS,
    TAIL_CLEANUP_PATTERN,
    TEXT_COLUMNS,
    UNIFIED_CLEANUP_PATTERN,
    combined_removal_pattern,
    email_pattern,
    emoji_pattern,
    logger,
    phone_pattern,
    url_pattern,
)

# OpenCC 转换器 (延迟初始化)
# 每个工作进程首次调用时创建, 避免 fork 不安全。
# OpenCC 的 C++ 底层对象不支持跨进程序列化,
# 因此必须在每个 worker 进程中独立初始化。
_worker_cc = None


def _tail_cleanup_repl(m: re.Match) -> str:
    """``TAIL_CLEANUP_PATTERN`` 的替换回调函数.

    替换规则:
      - 重复字符 (非数字) → 保留 2 个 (如 ``aaa`` → ``aa``)
      - 冗余标点 → 保留 1 个 (如 ``。。。`` → ``。``)
      - 空白序列 → 单个空格

    fix(omni-g-preprocess-01, 2026-06-11): 重复压缩支已排除数字 ([^0-9]) —
    '1000亿'/'2000年'/股票代码 '600000' 等连零量级不再被压缩破坏。
    """
    if m.group(1):
        return m.group(1) * 2
    elif m.group(2):
        return m.group(2)
    else:
        return ' '


def _strip_html(text: str) -> str:
    """去除 HTML 标签, 保留纯文本内容.

    使用 selectolax (基于 C 的 Modest 引擎) 解析 HTML,
    比 BeautifulSoup 快约 10-30x。

    Args:
        text: 可能包含 HTML 标签的文本。

    Returns:
        str: 去除 HTML 标签后的纯文本。
    """
    return HTMLParser(text).text(separator=' ', strip=True) if '<' in text else text


def _clean_single_text(text: str, cc) -> str:
    """对单个文本执行完整的清洗流水线.

    将 ftfy 编码修复、繁简转换、全角转半角、HTML 去除、噪声去除、
    尾部清理合并为单个函数调用, 减少 Series 中间对象创建。

    Args:
        text: 待清洗的原始文本。
        cc:   OpenCC 转换器实例。

    Returns:
        str: 清洗后的文本。
    """
    if not text:
        return text
    # 步骤 1: 编码修复(修复 mojibake 乱码)
    text = ftfy.fix_text(text)
    # 步骤 2: 繁体转简体
    text = cc.convert(text)
    # 步骤 2.5: 敏感词 "习近平" 简体→繁体 "習近平" (体现而非删除; 2026-06-22 由删除改为转繁体)。
    #          置于 t2s 之后 — 步骤 2 已把原繁体统一转简体, 此处再统一改回繁体;
    #          下游无第二次 t2s (唯一 t2s 在步骤 2), 故繁体形态得以保留至 stage 21 LLM 入参。
    text = text.replace('习近平', '習近平')
    # 步骤 3: 全角转半角 + 引号标准化(单次 translate 调用)
    text = text.translate(COMBINED_TRANS)
    # 步骤 4: HTML 标签去除
    text = _strip_html(text)
    # 步骤 5: 噪声去除(URL/Email/电话/Emoji/控制字符)
    if UNIFIED_CLEANUP_PATTERN is not None:
        text = UNIFIED_CLEANUP_PATTERN.sub('', text)
    else:
        for pat in [url_pattern, email_pattern, phone_pattern,
                    emoji_pattern, combined_removal_pattern]:
            text = pat.sub('', text)
    # 步骤 6: 尾部清理(重复字符[非数字]+冗余标点+空白标准化)
    text = TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, text).strip()
    return text


def clean_text_batch(df_batch: pd.DataFrame) -> pd.DataFrame:
    """对 DataFrame 批次执行综合文本清洗.

    对"标题"和"内容"列执行以下处理管道:
      1. 编码修复 (ftfy) — 修复 UTF-8 编码错误和 mojibake 乱码
      2. 繁体转简体 (OpenCC) — t2s 配置
      2.5 敏感词归一化 — "习近平"简体→繁体"習近平"(体现而非删除, 置于 t2s 之后)
      3. 全角转半角 + 引号标准化 — 合并为单次 str.translate()
      4. HTML 标签去除 — selectolax 高性能解析
      5. 噪声去除 — URL/Email/电话/Emoji/控制字符/自定义噪声模式
      6. 尾部清理 — 重复字符压缩/冗余标点合并/空白标准化

    使用合并后的 ``_clean_single_text`` 函数减少 Series 中间对象创建,
    相比逐步 ``.map()`` 调用减少约 30% 的 Python 解释器开销。

    Args:
        df_batch: 包含"标题"和"内容"列的 DataFrame 批次。

    Returns:
        pd.DataFrame: 清洗后的 DataFrame(就地修改并返回)。
    """
    global _worker_cc

    batch_size = len(df_batch)
    logger.debug(f"正在处理批次({batch_size} 行)")
    _t_start = time.time()

    # ── 子步骤 banner (preprocess sub-step; runner 共享日志) ──
    # 本模块是 stage 00 preprocessing 的清洗子步 (被 load.process_single_file 逐文件调用),
    # 无独立 main/ENV/CONFIG 块 (那是 runner 入口的职责), 此处只打印子步骤标识 + 方法依据 + 配置摘要 + 结果判读。
    # 纯 CPU / $0 (无 LLM/嵌入调用); 确定性 = 字节级可复现 (ftfy/OpenCC/selectolax 均纯函数)。
    try:
        _opencc_cfg = NORMALIZATION_PARAMS.get('opencc_config', 't2s')
        _html_thr = NORMALIZATION_PARAMS.get('html_removal_length_threshold', 0.7)
        logger.info(
            f"[normalize] 子步骤: 文本标准化清洗 (worker PID={os.getpid()}, 批 {batch_size:,} 行, "
            f"列={list(TEXT_COLUMNS)})"
        )
        logger.info(
            "[normalize] 方法依据: ftfy(mojibake 编码修复) · OpenCC(繁→简, "
            f"config={_opencc_cfg}) · selectolax/Modest(HTML 去标签) · 正则噪声/尾部清理; "
            "习近平→習近平(简→繁, 体现而非删除, 2026-06-22)"
        )
        logger.info(
            f"[normalize] 配置: opencc_config={_opencc_cfg} · "
            f"html_removal_length_threshold={sig4(_html_thr)} (HTML 去除后缩减率超此值标记疑似代码/结构化文档)"
        )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不可中断清洗阶段
        logger.warning(f"[normalize] 子步骤 banner 输出失败 (不影响清洗): {_e}")

    # 延迟初始化 OpenCC(每个工作进程首次调用时创建一次)
    if _worker_cc is None:
        opencc_config = NORMALIZATION_PARAMS.get('opencc_config', 't2s')
        logger.info(f"工作进程 {os.getpid()} 初始化 OpenCC({opencc_config})...")
        _worker_cc = opencc.OpenCC(opencc_config)

    df_batch['suspected_code_doc'] = False
    stats = {'total_chars_before': 0, 'total_chars_after': 0}

    for col in TEXT_COLUMNS:
        if col not in df_batch.columns:
            continue

        # 类型安全: 确保列为字符串类型
        series = (
            df_batch[col].fillna('') if df_batch[col].dtype == object
            else df_batch[col].astype(str)
        )

        original_len = series.str.len()
        stats['total_chars_before'] += original_len.sum()

        # 合并清洗管道: 单次 map 替代多次 map, 减少 Series 创建开销
        series = series.map(lambda t: _clean_single_text(t, _worker_cc))

        # 检测疑似代码/结构化文档(HTML 移除后长度大幅缩减的记录)
        len_after = series.str.len()
        reduction_ratio = (original_len - len_after) / original_len.replace(0, 1)
        threshold = NORMALIZATION_PARAMS.get('html_removal_length_threshold', 0.7)
        is_suspect = reduction_ratio > threshold
        df_batch['suspected_code_doc'] = df_batch['suspected_code_doc'] | is_suspect

        stats['total_chars_after'] += len_after.sum()
        df_batch[col] = series

    if stats['total_chars_before'] > 0:
        reduction_pct = (1 - stats['total_chars_after'] / stats['total_chars_before']) * 100
        logger.debug(
            f"字符数: {stats['total_chars_before']:,} → "
            f"{stats['total_chars_after']:,}(减少 {pct4(reduction_pct, fraction=False)})"
        )

    # ── 结果判读 + 计时 (纯日志, 读取已算出的真实统计量; 不改任何写盘值/schema/控制流) ──
    try:
        _elapsed = time.time() - _t_start
        # 字符缩减率判读: 报纸语料正常清洗 (去 HTML/噪声/尾部压缩) 缩减率通常 < ~15%;
        # 整批缩减率异常高 → 可能存量 HTML/结构化文档偏多 (非 bug, 仅提示语料构成)。
        if stats['total_chars_before'] > 0:
            _red_frac = 1 - stats['total_chars_after'] / stats['total_chars_before']
            if _red_frac > 0.30:
                _red_verdict = "偏高 (语料含较多 HTML/结构化文档?)"
            elif _red_frac > 0.15:
                _red_verdict = "临界 (清洗强度略高)"
            else:
                _red_verdict = "正常 (常规报纸语料清洗量级)"
            logger.info(
                f"[normalize] 结果: 字符数 {stats['total_chars_before']:,d} → "
                f"{stats['total_chars_after']:,d} | 整批缩减率 {pct4(_red_frac)} → {_red_verdict}"
            )
        # 疑似代码/结构化文档占比判读 (缩减率超 html 阈值的记录; 仅记录不过滤)。
        if 'suspected_code_doc' in df_batch.columns and batch_size > 0:
            _suspect_n = int(df_batch['suspected_code_doc'].sum())
            _suspect_frac = _suspect_n / batch_size
            if _suspect_frac > 0.10:
                _suspect_verdict = "偏高 (建议人工抽查语料源)"
            elif _suspect_frac > 0.02:
                _suspect_verdict = "临界"
            else:
                _suspect_verdict = "正常 (清洁报纸文本占主体)"
            logger.info(
                f"[normalize] 结果: 疑似代码/结构化文档 {_suspect_n:,d}/{batch_size:,d} 条 "
                f"(占比 {pct4(_suspect_frac)}) → {_suspect_verdict}"
            )
        _rate = (batch_size / _elapsed) if _elapsed > 0 else 0.0
        logger.info(
            f"[normalize] ⏱ 子步骤墙钟 {sig4(_elapsed)} 秒 "
            f"({batch_size:,d} 行, {sig4(_rate)} 行/秒)"
        )
    except Exception as _e:  # noqa: BLE001 — 日志/判读块绝不可中断清洗阶段
        logger.warning(f"[normalize] 结果判读/计时输出失败 (不影响清洗): {_e}")

    return df_batch


__all__ = [
    '_tail_cleanup_repl',
    '_strip_html',
    '_clean_single_text',
    'clean_text_batch',
]
