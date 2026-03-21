"""
utils/entity_context.py — 实体特异性上下文提取引擎
==================================================

为每个 (文章, 目标银行) 对提取局部上下文窗口，
消除非目标实体的情感污染。

算法：基于句号边界的滑动窗口 + O(N log N) 区间合并。
学术参考：Hassan et al. (2019, QJE) Proximity-based Attribution。
"""

import re
import json
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# 中文句号边界正则（句号、问号、感叹号、分号作为硬分割点）
_SENT_SPLIT_RE = re.compile(r'([。！？!?；;])')


def _split_sentences(text: str) -> List[str]:
    """将中文文本按句号/问号/感叹号/分号切分为句子列表。

    保留标点符号附着到前一句末尾，确保句子完整性。

    Returns:
        list[str]: 非空句子列表。
    """
    parts = _SENT_SPLIT_RE.split(text)
    sentences = []
    i = 0
    while i < len(parts):
        seg = parts[i]
        # 如果下一个 part 是标点，拼接到当前句子
        if i + 1 < len(parts) and _SENT_SPLIT_RE.fullmatch(parts[i + 1]):
            seg += parts[i + 1]
            i += 2
        else:
            i += 1
        seg = seg.strip()
        if seg:
            sentences.append(seg)
    return sentences


def _merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """O(N log N) 区间合并，消除重叠窗口的双倍计算。

    Args:
        intervals: [(start, end), ...] 索引区间列表。

    Returns:
        list[tuple]: 合并后的不重叠区间列表。
    """
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_iv[0])]
    for curr_start, curr_end in sorted_iv[1:]:
        prev = merged[-1]
        if curr_start <= prev[1] + 1:  # 相邻或重叠
            prev[1] = max(prev[1], curr_end)
        else:
            merged.append([curr_start, curr_end])
    return [tuple(iv) for iv in merged]


def extract_entity_context(
    text: str,
    target_aliases: List[str],
    sentence_radius: int = 1,
    fallback_char_radius: int = 150,
) -> str:
    """为目标银行提取实体特异性上下文摘要。

    算法步骤：
      1. 将全文按句号分割为句子序列。
      2. 定位目标银行（及其所有别名）出现的句子索引集合。
      3. 对每个命中句子，取其前后各 sentence_radius 句窗口。
      4. 对所有窗口执行 O(N log N) 区间合并，消除重叠。
      5. 将合并后的非连续区间拼接为摘要，用 " [...] " 分隔。

    Args:
        text:                 文章全文（'内容' 列）。
        target_aliases:       目标银行的所有名称变体列表。
        sentence_radius:      句子级窗口半径（默认 1 = 前后各1句）。
        fallback_char_radius: 回退时的字符级窗口半径。

    Returns:
        str: 实体特异性摘要文本。空字符串表示未匹配到目标银行。
    """
    if not text or not target_aliases:
        return ""

    sentences = _split_sentences(text)

    # 当句子分割退化（<3 句）时，回退到字符级窗口
    if len(sentences) < 3:
        return _char_level_fallback(text, target_aliases, fallback_char_radius)

    # 定位目标银行出现的句子索引
    hit_indices = set()
    for i, sent in enumerate(sentences):
        for alias in target_aliases:
            if alias in sent:
                hit_indices.add(i)
                break  # 一个别名命中即可

    if not hit_indices:
        return ""

    # 构建窗口区间
    n = len(sentences)
    raw_intervals = [
        (max(0, i - sentence_radius), min(n - 1, i + sentence_radius))
        for i in hit_indices
    ]

    # 区间合并
    merged = _merge_intervals(raw_intervals)

    # 拼接
    fragments = ["".join(sentences[s:e + 1]) for s, e in merged]
    return " [...] ".join(fragments)


def _char_level_fallback(
    text: str,
    target_aliases: List[str],
    radius: int = 150,
) -> str:
    """字符级回退：当文本过短无法有效分句时使用。"""
    intervals = []
    for alias in target_aliases:
        start_pos = 0
        while True:
            pos = text.find(alias, start_pos)
            if pos == -1:
                break
            intervals.append((max(0, pos - radius),
                              min(len(text) - 1, pos + len(alias) + radius)))
            start_pos = pos + 1

    if not intervals:
        return ""

    merged = _merge_intervals(intervals)
    return " [...] ".join(text[s:e + 1] for s, e in merged)


# === 别名查询（带文件级缓存，避免重复读盘） ===
_ALIASES_CACHE = {}   # {bank_name: [aliases]}
_BANK_DATA = None     # 缓存整个 bank_names.json


def get_target_aliases(target_bank: str, bank_names_file: str) -> List[str]:
    """获取目标银行的所有名称变体。首次调用加载文件，后续走缓存。

    Args:
        target_bank:    标准银行名称。
        bank_names_file: bank_names.json 文件路径。

    Returns:
        list[str]: 该银行的所有名称变体（含标准名称本身）。
    """
    global _BANK_DATA

    if target_bank in _ALIASES_CACHE:
        return _ALIASES_CACHE[target_bank]

    if _BANK_DATA is None:
        try:
            with open(bank_names_file, 'r', encoding='utf-8') as f:
                _BANK_DATA = json.load(f)
        except Exception as e:
            logger.warning(f"加载银行别名文件失败: {e}")
            _BANK_DATA = []

    for bank in _BANK_DATA:
        if bank.get('bank_name') == target_bank:
            aliases = list(bank.get('variants', []))
            if target_bank not in aliases:
                aliases.insert(0, target_bank)
            _ALIASES_CACHE[target_bank] = aliases
            return aliases

    # 未找到时，至少用标准名称本身
    _ALIASES_CACHE[target_bank] = [target_bank]
    return [target_bank]
