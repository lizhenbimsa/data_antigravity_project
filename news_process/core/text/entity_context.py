"""
utils/entity_context.py - 实体特异性上下文提取引擎
==================================================

为每个 (文章, 目标银行) 对提取局部上下文窗口,
消除非目标实体的情感污染。

问题背景:
  一篇新闻可能同时提及多家银行, 且对不同银行的情感可能截然不同:
  “工商银行利润大增, 但建设银行因不良贷款报亏”。如果对全文做情感分析,
  两家银行会获得相同的混合情感分数。实体特异性上下文提取
  通过仅保留目标银行周围的句子来解决这个问题。

算法原理 (基于句号边界的滑动窗口 + O(N log N) 区间合并):

  步骤 1: 全文 -> 句子序列
    "工行利润增。建行亏损。交行扩张。中行稳定。"
    -> [S0, S1, S2, S3]

  步骤 2: 定位目标银行出现的句子索引 (target="工行")
    -> hit_indices = {0}

  步骤 3: 扩展窗口 (radius=1)
    -> 原始区间 = [(max(0, 0-1), min(3, 0+1))] = [(0, 1)]

  步骤 4: 区间合并 (消除重叠)
    -> merged = [(0, 1)]

  步骤 5: 拼接输出
    -> "工行利润增。建行亏损。"  (仅保留 S0+S1, 排除了 S2+S3)

学术参考: Hassan et al. (2019, QJE) Proximity-based Attribution。
该方法确保情感分数仅反映目标实体周围的文本内容,
而非全文混合情感。
"""

import re
import json
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# 中文句号边界正则:
# 句号(。)、问号(？?)、感叹号(！!)、分号(；;) 作为硬分割点。
# 不使用逗号/顿号作为分割点, 因为它们在中文中常用于句内停顿,
# 分割后会产生过多破碎片段, 降低上下文质量。
_SENT_SPLIT_RE = re.compile(r'([。！？!?；;])')


def _split_sentences(text: str) -> List[str]:
    """将中文文本按句号/问号/感叹号/分号切分为句子列表。

    保留标点符号附着到前一句末尾，确保句子完整性。

    Returns:
        list[str]: 非空句子列表。
    """
    # re.split 使用捕获组 () 时, 分隔符本身会作为独立元素保留在结果中。
    # 例如: "工行好。建行差。" -> ["工行好", "。", "建行差", "。", ""]
    # 我们需要将标点重新附着到前一句末尾: "工行好。", "建行差。"
    parts = _SENT_SPLIT_RE.split(text)
    sentences = []
    i = 0
    while i < len(parts):
        seg = parts[i]
        # 如果下一个 part 是标点, 拼接到当前句子末尾
        if i + 1 < len(parts) and _SENT_SPLIT_RE.fullmatch(parts[i + 1]):
            seg += parts[i + 1]
            i += 2  # 跳过已处理的标点部分
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
    # 步骤 1: 按起始位置升序排序 -> O(N log N)
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_iv[0])]
    for curr_start, curr_end in sorted_iv[1:]:
        prev = merged[-1]
        # 相邻(+1)或重叠 -> 合并: 扩展前一个区间的右边界
        if curr_start <= prev[1] + 1:
            prev[1] = max(prev[1], curr_end)
        else:
            # 不重叠 -> 新开一个区间
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

    # 当句子分割退化(< 3 句)时, 回退到字符级窗口。
    # 退化场景: 文本过短或缺少句号标点(如标题、摘要)
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

    # 构建窗口区间: 每个命中句子向前后扩展 sentence_radius 句
    # 例如: hit=5, radius=1 -> 区间 [4, 6]
    n = len(sentences)
    raw_intervals = [
        (max(0, i - sentence_radius), min(n - 1, i + sentence_radius))
        for i in hit_indices
    ]

    # 区间合并: 当多个命中句子的窗口有重叠时, 合并为一个连续区间
    # 避免同一句子被重复包含导致情感分数偏移
    merged = _merge_intervals(raw_intervals)

    # 拼接: 非连续区间用 " [...] " 分隔, 表示省略了中间的无关内容
    fragments = ["".join(sentences[s:e + 1]) for s, e in merged]
    return " [...] ".join(fragments)


def _char_level_fallback(
    text: str,
    target_aliases: List[str],
    radius: int = 150,
) -> str:
    """字符级回退: 当文本过短无法有效分句时使用。

    策略: 以银行名称出现位置为中心, 前后各取 radius 个字符。
    多个匹配位置的窗口仍执行区间合并。
    """
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


# ============================================================================
# G-14: 距离衰减结构化输出
# ============================================================================
# 学术依据:
#   Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023).
#   Firm-level climate change exposure. The Journal of Finance, 78(3),
#   1449–1498. DOI: 10.1111/jofi.13228 (§2.2):
#     "We weight each bigram token by its inverse distance to the
#      nearest climate change keyword."
#   本函数返回句子+距离对, 供下游词典法做距离加权情感计算。
# ============================================================================

def extract_entity_context_with_distances(
    text: str,
    target_aliases: List[str],
    sentence_radius: int = 2,
) -> List[Tuple[str, int]]:
    """返回窗口内句子及其到最近目标实体的句级距离。

    与 extract_entity_context() 的区别:
      - 返回 [(sentence_text, min_distance), ...] 而非拼接字符串
      - min_distance = 该句到最近实体提及句的距离 (0=命中句本身)
      - 默认 radius=2 (比 ctx 轨道的 1 更大, 提供衰减空间)

    Args:
        text:            文章全文。
        target_aliases:  目标银行的所有名称变体。
        sentence_radius: 句子级窗口半径 (默认 2)。

    Returns:
        list[tuple[str, int]]: 窗口内的 (句子文本, 距离) 对。
            空列表表示未匹配到目标银行。
    """
    if not text or not target_aliases:
        return []

    sentences = _split_sentences(text)

    if len(sentences) < 3:
        # 短文本退化: 检查是否有任何句子命中目标银行
        has_hit = any(
            alias in s
            for s in sentences
            for alias in target_aliases
        )
        if has_hit:
            return [(sent, 0) for sent in sentences]
        return []

    # 定位命中句索引
    hit_indices = set()
    for i, sent in enumerate(sentences):
        for alias in target_aliases:
            if alias in sent:
                hit_indices.add(i)
                break

    if not hit_indices:
        return []

    # 构建窗口区间
    n = len(sentences)
    raw_intervals = [
        (max(0, i - sentence_radius), min(n - 1, i + sentence_radius))
        for i in hit_indices
    ]
    merged = _merge_intervals(raw_intervals)

    # 计算每个窗口内句子到最近命中句的距离
    result = []
    for start, end in merged:
        for i in range(start, end + 1):
            min_dist = min(abs(i - h) for h in hit_indices)
            result.append((sentences[i], min_dist))

    return result


# === 别名查询(带文件级缓存, 避免重复读盘) ===
# 设计: 全局缓存策略
#   - _BANK_DATA: 缓存整个 bank_names.json 文件内容(首次读取后不再读盘)
#   - _ALIASES_CACHE: 缓存每个银行的别名列表(避免重复遍历 JSON 数组)
#   在处理 ~50,000 篇文章 x ~500 家银行时, 缓存可避免数百万次重复查找
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
