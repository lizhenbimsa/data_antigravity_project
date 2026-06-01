"""
core/text/ahocorasick.py - AC 自动机构建与匹配的公共模块
====================================================

提供银行名称和金融科技关键词的 AC 自动机构建、加载与匹配功能。

供以下脚本共享调用:
  - 11_news_bank.py      (银行新闻分类)
  - 12_news_fintech.py   (金融科技新闻分类)
  - 31_bank_fintech_threshold.py (阈值敏感性分析)

设计目标:
  1. 消除三处重复实现带来的同步维护风险
  2. 确保阈值敏感性分析(阶段 31)与主分类逻辑(阶段 11/12)使用完全一致的
     匹配规则, 包括否定模式排除和短名歧义消解

AC 自动机 (Aho-Corasick) 算法原理:
  - 核心思想: 将多个模式串(如 500+ 个银行名称变体)构建为一个
    有限状态自动机, 允许在 O(n + m) 时间内完成全文扫描
    (n = 文本长度, m = 匹配结果数)。
  - 三大函数:
    goto():    前缀运动函数, 将模式串插入到 Trie 树中
    failure(): 失败指针函数, 当匹配失败时跳转到最长后缀(BFS 构建)
    output():  输出函数, 记录每个状态可以输出的匹配模式
  - pyahocorasick 库封装了这些实现, 提供 .add_word() 和 .iter() API
  - 对比替代方案:
    · 逐个模式 re.search(): O(n * k), k=模式数, 当 k=500 时慢 500 倍
    · str.find() 循环:    同上, 且无法处理重叠匹配
    · 正则合并 re.compile('|'.join(patterns)): O(n * k), 且模式过多时
      编译内存暴增
"""

import json
import logging
import os
from collections import defaultdict

import ahocorasick

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 银行名称 AC 自动机
#
# 银行名称数据结构 (bank_names.json):
#   [{"bank_name": "招商银行", "variants": ["招行", "招商银行", "CMB", ...]}, ...]
#   每家银行可能有多个名称变体(variants), 包括简称、英文缩写等。
#   变体按长度降序排列, 确保较长的匹配优先(AC 自动机返回所有匹配,
#   但按长度降序插入有助于下游统计时识别最长匹配)。
# ============================================================================

def load_bank_names(bank_names_file: str) -> tuple:
    """从 bank_names.json 加载银行名称分组数据并构建 AC 自动机。

    Args:
        bank_names_file: 银行名称 JSON 文件路径。

    Returns:
        tuple: (banks_list, ac_automaton, variant_to_bank_map)
          - banks_list: [{'bank_name': str, 'variants': [str, ...]}, ...]
          - ac_automaton: AC 自动机实例（用于 O(n) 全文匹配）
          - variant_to_bank_map: {变体名称: bank_index}
    """
    if not bank_names_file or not os.path.exists(bank_names_file):
        logger.error(f"银行名称配置文件未找到: {bank_names_file}")
        return [], None, {}

    with open(bank_names_file, 'r', encoding='utf-8') as f:
        raw_banks = json.load(f)

    banks = []
    variant_to_bank = {}
    ac = ahocorasick.Automaton()

    for bank_idx, entry in enumerate(raw_banks):
        bank_name = entry.get('bank_name', '')
        variants = entry.get('variants', [])
        if not bank_name or not variants:
            continue

        # 变体按长度降序排序, 确保较长的名称优先入库
        clean_variants = []
        for v in sorted(variants, key=len, reverse=True):
            v = v.strip()
            if v:
                clean_variants.append(v)
                # add_word(模式, 值): 匹配时返回 (bank_idx, 变体名称)
                # bank_idx 用于反查 banks_list 获取银行完整信息
                ac.add_word(v, (bank_idx, v))
                variant_to_bank[v] = bank_idx

        if clean_variants:
            banks.append({
                'bank_name': bank_name,
                'variants': clean_variants,
            })

    if banks:
        # make_automaton(): 构建 failure 链接和 output 函数
        # 调用后自动机进入“只读”状态, 不能再添加新模式
        ac.make_automaton()
    else:
        ac = None

    return banks, ac, variant_to_bank


def load_exclusion_patterns(exclusion_file: str) -> tuple:
    """加载否定模式和短名歧义消解配置。

    Args:
        exclusion_file: bank_name_exclusions.json 文件路径。

    Returns:
        tuple: (negation_ac, short_name_exclusions, context_window)
          - negation_ac: 否定模式 AC 自动机(如 "非工商银行", "中国银行业监督管理委员会")
          - short_name_exclusions: {短名称: [排除上下文列表]}
            例如: {"光大": ["光大的", "光大贡献"]} —— 防止将“光大”误匹配为光大银行
          - context_window: 上下文检查窗口大小(字符数, 默认 5)
    """
    if not os.path.exists(exclusion_file):
        logger.warning(f"否定模式配置文件未找到: {exclusion_file}，将跳过否定模式检查")
        return None, {}, 5

    with open(exclusion_file, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # 构建否定模式 AC 自动机
    neg_patterns = raw.get('negation_patterns', [])
    neg_ac = None
    if neg_patterns:
        neg_ac = ahocorasick.Automaton()
        for pattern in neg_patterns:
            pattern = pattern.strip()
            if pattern:
                neg_ac.add_word(pattern, pattern)
        neg_ac.make_automaton()
        logger.info(f"否定模式: 已加载 {len(neg_patterns)} 个模式")

    # 加载短名歧义消解配置
    short_cfg = raw.get('short_name_context_exclusions', {})
    context_window = short_cfg.get('context_window', 5)
    short_exclusions = short_cfg.get('exclusions', {})
    if short_exclusions:
        logger.info(
            f"短名歧义消解: 已加载 {len(short_exclusions)} 个短名称的排除规则，"
            f"上下文窗口: {context_window} 字符"
        )

    return neg_ac, short_exclusions, context_window


def is_match_excluded(text: str, match_end_pos: int, variant: str,
                      negation_ac=None, short_name_exclusions: dict = None,
                      context_window: int = 5) -> str | None:
    """检查一个匹配是否应被排除（否定模式或短名歧义）。

    Args:
        text:                   原始文本。
        match_end_pos:          AC 自动机返回的匹配结束位置（含）。
        variant:                匹配到的银行名称变体。
        negation_ac:            否定模式 AC 自动机。
        short_name_exclusions:  短名歧义排除规则字典。
        context_window:         上下文检查窗口大小。

    Returns:
        str | None: 排除原因（'negation' 或 'short_name'），None 表示不排除。
    """
    variant_len = len(variant)
    # 计算匹配的起始位置: AC 自动机返回的是结束位置(end_pos, 含),
    # 起始位置 = end_pos - len(variant) + 1
    match_start = match_end_pos - variant_len + 1

    # --- 否定模式检查 ---
    # 取匹配位置前后 10 个字符作为上下文窗口, 检查是否存在否定模式。
    # 例如: 匹配到 "工商银行" 但上下文是 "非工商银行借贷" → 排除
    if negation_ac is not None:
        ctx_start = max(0, match_start - 10)
        ctx_end = min(len(text), match_end_pos + 10 + 1)
        context = text[ctx_start:ctx_end]
        for neg_end, neg_pattern in negation_ac.iter(context):
            # 将否定模式在上下文中的相对位置转换为原文的绝对位置
            neg_start_in_ctx = neg_end - len(neg_pattern) + 1
            neg_abs_start = ctx_start + neg_start_in_ctx
            neg_abs_end = ctx_start + neg_end
            # 检查否定模式与银行名称是否有位置重叠(能‍“包含”或“交叉”)
            if neg_abs_start <= match_start and neg_abs_end >= match_end_pos:
                return 'negation'  # 否定模式完全包含了银行名称
            if neg_abs_start <= match_end_pos and neg_abs_end >= match_start:
                return 'negation'  # 否定模式与银行名称有交叉

    # --- 短名歧义消解 ---
    # 对于长度 <= 2 的短名称(如 "光大"、"建行"、"华夏"), 检查其上下文
    # 是否包含排除词。例如 "光大" 可能被误匹配为光大银行,
    # 但上下文是 "光大的前途" → 排除
    # context_window: 上下文窗口大小(默认 5 字符, 即前后各 5 个字)
    if short_name_exclusions and variant_len <= 2 and variant in short_name_exclusions:
        exclusion_list = short_name_exclusions[variant]
        ctx_start = max(0, match_start - context_window)
        ctx_end = min(len(text), match_end_pos + context_window + 1)
        context = text[ctx_start:ctx_end]
        for excl_word in exclusion_list:
            if excl_word in context:
                return 'short_name'  # 在上下文中发现排除词, 认为是歧义匹配

    return None


# ============================================================================
# 2. 金融科技关键词 AC 自动机
# ============================================================================

def load_fintech_dict(fintech_dict_file: str) -> tuple:
    """从 fintech_dict.json 加载金融科技词典并构建 AC 自动机。

    Args:
        fintech_dict_file: 金融科技词典 JSON 文件路径。

    Returns:
        tuple: (all_keywords_list, ac_automaton)
    """
    if not fintech_dict_file or not os.path.exists(fintech_dict_file):
        logger.error(f"金融科技词典文件未找到: {fintech_dict_file}")
        return [], None

    with open(fintech_dict_file, 'r', encoding='utf-8') as f:
        raw_dict = json.load(f)

    all_keywords = []
    ac = ahocorasick.Automaton()

    for kw in raw_dict:
        kw = kw.strip()
        if kw:
            all_keywords.append(kw)
            ac.add_word(kw, kw)

    all_keywords.sort(key=len, reverse=True)

    if all_keywords:
        ac.make_automaton()
    else:
        ac = None

    return all_keywords, ac


# ============================================================================
# 3. 银行匹配分析(含否定模式和短名歧义消解)
#
# 判定策略(影响精确率和召回率的核心参数):
#   一篇文章被判定为某银行相关新闻需同时满足:
#     (a) 出现次数 >= min_name_occurrences (默认 3)
#     (b) 上下半分布: 上半 >= min_upper(1) 且 下半 >= min_lower(1)
#         或: 出现在标题中 且 正文总次数 >= min_upper
#
#   上下半分割的学术依据:
#     Hassan (2019, QJE) "Firm-Level Political Risk" 提出了
#     文本内新闻实体 空间分布一致性 的重要性 —— 如果一个实体
#     仅在文章开头提及(例如“据某银行报道”), 但全文实际讨论的是
#     其他主题, 则不应将该文章归类为该银行的相关新闻。
#     上下半分割 + 最少分布要求(上下半各至少出现 1 次)就是
#     对这一思想的操作化实现。
# ============================================================================

def analyze_bank_matches(content: str, title: str,
                         bank_ac, banks_list: list,
                         split_ratio: float,
                         negation_ac=None,
                         short_name_exclusions: dict = None,
                         context_window: int = 5,
                         min_name_occurrences: int = 3,
                         min_upper: int = 1,
                         min_lower: int = 1) -> dict:
    """分析单篇文章的银行匹配（带否定模式排除和短名歧义消解）。

    这是 11_news_bank.py 和 31_bank_fintech_threshold.py 的共享核心逻辑。

    Args:
        content:                文章内容文本。
        title:                  文章标题文本。
        bank_ac:                银行名称 AC 自动机。
        banks_list:             银行信息列表。
        split_ratio:            上下半分割比例。
        negation_ac:            否定模式 AC 自动机（可选）。
        short_name_exclusions:  短名歧义排除规则（可选）。
        context_window:         上下文检查窗口大小。
        min_name_occurrences:   最少出现次数。
        min_upper:              上半最少出现次数。
        min_lower:              下半最少出现次数。

    Returns:
        dict: 包含 is_bank_news, matched_banks, negation_excluded,
              short_name_excluded 的分析结果。
    """
    content_str = content if isinstance(content, str) else ""
    title_str = title if isinstance(title, str) else ""

    empty_result = {"is_bank_news": False, "matched_banks": [],
                    "negation_excluded": 0, "short_name_excluded": 0}

    if not content_str.strip() and not title_str.strip():
        return empty_result

    if bank_ac is None:
        return empty_result

    # 上下半分割: 将文章内容按 split_ratio(默认 0.5)分为上半和下半
    # 分别统计各银行名称在上/下半的出现次数, 以检验分布一致性
    split_pos = int(len(content_str) * split_ratio)
    upper_half = content_str[:split_pos]
    lower_half = content_str[split_pos:]

    # bank_stats[bank_idx][variant] = {upper: 上半出现次数, lower: 下半出现次数, ...}
    # 使用双层 defaultdict 避免手动初始化
    bank_stats = defaultdict(
        lambda: defaultdict(
            lambda: {'upper': 0, 'lower': 0, 'in_title': False, 'title_count': 0}
        )
    )
    negation_excluded = 0   # 被否定模式排除的匹配数(调试统计用)
    short_name_excluded = 0  # 被短名歧义消解排除的匹配数

    # 扫描上半
    for end_pos, (bank_idx, variant) in bank_ac.iter(upper_half):
        reason = is_match_excluded(upper_half, end_pos, variant,
                                   negation_ac, short_name_exclusions, context_window)
        if reason == 'negation':
            negation_excluded += 1
            continue
        if reason == 'short_name':
            short_name_excluded += 1
            continue
        bank_stats[bank_idx][variant]['upper'] += 1

    # 扫描下半
    for end_pos, (bank_idx, variant) in bank_ac.iter(lower_half):
        reason = is_match_excluded(lower_half, end_pos, variant,
                                   negation_ac, short_name_exclusions, context_window)
        if reason == 'negation':
            negation_excluded += 1
            continue
        if reason == 'short_name':
            short_name_excluded += 1
            continue
        bank_stats[bank_idx][variant]['lower'] += 1

    # 扫描标题
    for end_pos, (bank_idx, variant) in bank_ac.iter(title_str):
        reason = is_match_excluded(title_str, end_pos, variant,
                                   negation_ac, short_name_exclusions, context_window)
        if reason == 'negation':
            negation_excluded += 1
            continue
        if reason == 'short_name':
            short_name_excluded += 1
            continue
        bank_stats[bank_idx][variant]['in_title'] = True
        bank_stats[bank_idx][variant]['title_count'] += 1

    # 汇总结果
    matched_banks = []
    is_bank_news = False

    for bank_idx, variant_stats in bank_stats.items():
        bank_name = banks_list[bank_idx]['bank_name']
        bank_upper_total = 0
        bank_lower_total = 0
        bank_title_total = 0
        bank_in_title = False
        variant_details = []

        for variant, stats in variant_stats.items():
            upper_count = stats['upper']
            lower_count = stats['lower']
            title_count = stats['title_count']
            total = upper_count + lower_count
            variant_in_title = stats['in_title']

            if variant_in_title:
                bank_in_title = True

            if total > 0 or variant_in_title:
                variant_details.append({
                    'variant': variant,
                    'total': total,
                    'upper': upper_count,
                    'lower': lower_count,
                    'in_title': variant_in_title,
                })
                bank_upper_total += upper_count
                bank_lower_total += lower_count
                bank_title_total += title_count

        bank_total_with_title = bank_upper_total + bank_lower_total + bank_title_total

        if bank_upper_total > 0 or bank_lower_total > 0 or bank_in_title:
            matched_banks.append({
                'bank_name': bank_name,
                'total_count': bank_upper_total + bank_lower_total,
                'total_with_title': bank_total_with_title,
                'upper_count': bank_upper_total,
                'lower_count': bank_lower_total,
                'in_title': bank_in_title,
                'variant_details': variant_details,
            })

            # 判定条件 1: 总出现次数(含标题) >= 阈值
            meets_occurrence = bank_total_with_title >= min_name_occurrences
            # 判定条件 2: 上下半分布一致性
            # 路径 A: 正文上半 >= min_upper 且 下半 >= min_lower
            # 路径 B: 出现在标题中 且 正文总次数 >= min_upper(宽松条件)
            meets_distribution = (
                (bank_upper_total >= min_upper and bank_lower_total >= min_lower)
                or (bank_in_title and bank_upper_total + bank_lower_total >= min_upper)
            )
            if meets_occurrence and meets_distribution:
                is_bank_news = True

    matched_banks.sort(key=lambda x: x['total_count'], reverse=True)

    return {"is_bank_news": is_bank_news, "matched_banks": matched_banks,
            "negation_excluded": negation_excluded, "short_name_excluded": short_name_excluded}


# ============================================================================
# 4. 金融科技匹配分析
#
# 与银行匹配的差异:
#   - 银行匹配关注“某一家银行是否被提及”(实体级别)
#   - 金融科技匹配关注“文章是否讨论金融科技主题”(主题级别)
#   - 因此使用“不同关键词数”而非“总出现次数”作为主要判定指标,
#     确保文章真正涵盖多个金融科技子领域而非仅重复提及单一词汇
# ============================================================================

def analyze_fintech_matches(content: str, title: str,
                            fintech_ac, split_ratio: float,
                            min_distinct_keywords: int = 3,
                            min_upper: int = 1,
                            min_lower: int = 1) -> dict:
    """分析单篇文章的金融科技关键词匹配。

    这是 12_news_fintech.py 和 31_bank_fintech_threshold.py 的共享核心逻辑。

    Args:
        content:               文章内容文本。
        title:                 文章标题文本。
        fintech_ac:            金融科技关键词 AC 自动机。
        split_ratio:           上下半分割比例。
        min_distinct_keywords: 最少不同关键词数。
        min_upper:             上半最少出现次数。
        min_lower:             下半最少出现次数。

    Returns:
        dict: 包含 is_fintech_news、汇总计数和关键词详情的分析结果。
    """
    content_str = content if isinstance(content, str) else ""
    title_str = title if isinstance(title, str) else ""

    empty_result = {
        "is_fintech_news": False,
        "total_count": 0, "upper_count": 0, "lower_count": 0,
        "in_title": False, "keyword_details": [],
    }

    if not content_str.strip() and not title_str.strip():
        return empty_result

    if fintech_ac is None:
        return empty_result

    split_pos = int(len(content_str) * split_ratio)
    upper_half = content_str[:split_pos]
    lower_half = content_str[split_pos:]

    kw_stats = defaultdict(lambda: {'upper': 0, 'lower': 0, 'in_title': False})

    for _, kw in fintech_ac.iter(upper_half):
        kw_stats[kw]['upper'] += 1

    for _, kw in fintech_ac.iter(lower_half):
        kw_stats[kw]['lower'] += 1

    for _, kw in fintech_ac.iter(title_str):
        kw_stats[kw]['in_title'] = True

    keyword_details = []
    grand_upper_total = 0
    grand_lower_total = 0
    any_in_title = False

    for kw, stats in kw_stats.items():
        upper_count = stats['upper']
        lower_count = stats['lower']
        total = upper_count + lower_count
        kw_in_title = stats['in_title']

        if kw_in_title:
            any_in_title = True

        if total > 0 or kw_in_title:
            keyword_details.append({
                'keyword': kw,
                'total': total,
                'upper': upper_count,
                'lower': lower_count,
                'in_title': kw_in_title,
            })
            grand_upper_total += upper_count
            grand_lower_total += lower_count

    grand_total = grand_upper_total + grand_lower_total

    # 判定条件 1: 不同关键词数 >= min_distinct_keywords (多样性要求)
    distinct_keyword_count = len(keyword_details)
    meets_diversity = distinct_keyword_count >= min_distinct_keywords
    # 判定条件 2: 上下半分布一致性(与银行匹配相同的逻辑)
    meets_distribution = (
        (grand_upper_total >= min_upper and grand_lower_total >= min_lower)
        or (any_in_title and grand_total >= min_upper)
    )
    # 两个条件均满足时才判定为金融科技新闻
    is_fintech_news = meets_diversity and meets_distribution

    keyword_details.sort(key=lambda x: x['total'], reverse=True)

    return {
        "is_fintech_news": is_fintech_news,
        "total_count": grand_total,
        "upper_count": grand_upper_total,
        "lower_count": grand_lower_total,
        "distinct_count": distinct_keyword_count,
        "in_title": any_in_title,
        "keyword_details": keyword_details,
    }
