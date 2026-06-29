"""
core/text/ahocorasick.py - AC 自动机构建与匹配的公共模块
====================================================

提供银行名称和金融科技关键词的 AC 自动机构建、加载与匹配功能。

供以下脚本共享调用:
  - 11_news_bank.py      (银行新闻分类)
  - 12_news_fintech.py   (金融科技新闻分类)
  - 60_bank_fintech_threshold.py (阈值敏感性分析)

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

from news_process.core.logging import pct4, sig4  # 日志四位有效数字/百分比渲染 (golden-safe, 仅供 logger.*)

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 银行名称 AC 自动机
#
# 银行名称数据结构 (bank_names.json):
#   [{"bank_name": "招商银行", "variants": ["招行", "招商银行", "CMB", ...]}, ...]
#   每家银行可能有多个名称变体(variants), 包括简称、英文缩写等。
#   AC 自动机返回所有重叠匹配; 下游 analyze_bank_matches 通过
#   _scan_dedup_bank_matches 做最长匹配位置去重 (longest-match resolution),
#   嵌套/交叉跨度只计最长一个 (fix omni-g-entity-01/02, 2026-06-11 兑现本承诺)。
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
        logger.info(
            f"银行名称 AC 自动机: 已加载 {len(banks):,d} 家银行 / "
            f"{len(variant_to_bank):,d} 个名称变体 (Aho-Corasick 多模式 O(n+m) 全文匹配)"
        )
        # 📊 结果统计 (词典规模与变体长度分布; 全部 log-only, 不参与产物计算)
        _v_lens = [len(v) for v in variant_to_bank]
        _short_n = sum(1 for _l in _v_lens if _l <= 2)  # 短名 (≤2 字, 须短名歧义消解)
        _mean_var_len = sum(_v_lens) / len(_v_lens)
        _avg_var_per_bank = len(variant_to_bank) / len(banks)
        logger.info(
            f"  📊 变体长度: min={min(_v_lens)} / mean={sig4(_mean_var_len)} / "
            f"max={max(_v_lens)} 字符; 短名 (≤2 字) {_short_n:,d} 个; "
            f"平均每家 {sig4(_avg_var_per_bank)} 个变体"
        )
        # 📖 方法论依据 (核心算法学术出处, Crossref 真值核验 DOI):
        logger.info("  📖 方法论依据:")
        #    Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: an aid to
        #    bibliographic search. Communications of the ACM, 18(6), 333-340.
        logger.info(
            "    [多模式匹配算法] Aho, A. V., & Corasick, M. J. (1975). Efficient string "
            "matching: an aid to bibliographic search. Communications of the ACM, 18(6), "
            "333-340. https://doi.org/10.1145/360825.360855"
        )
        logger.info(
            "      (白话: 把数百个银行名变体编成一台有限状态自动机, 全文扫一遍即拿到"
            "所有命中, O(n+m) 而非逐词正则 O(n*k))"
        )
        #    Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information
        #    retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
        logger.info(
            "    [词典查找/检索原语] Manning, C. D., Raghavan, P., & Schütze, H. (2008). "
            "Introduction to information retrieval. Cambridge University Press. "
            "https://doi.org/10.1017/CBO9780511809071"
        )
        logger.info(
            "      (白话: 实体/关键词词典查找与文本扫描的标准 IR 教科书依据, 锚定本模块"
            "的 dictionary-based term spotting 范式)"
        )
        #    Ash, E., & Hansen, S. (2023). Text algorithms in economics.
        #    Annual Review of Economics, 15, 659-688.
        logger.info(
            "    [经济学文本算法] Ash, E., & Hansen, S. (2023). Text algorithms in "
            "economics. Annual Review of Economics, 15, 659-688. "
            "https://doi.org/10.1146/annurev-economics-082222-074352"
        )
        logger.info(
            "      (白话: 把字符串匹配/词典算法纳入经济学实证工具箱的近期综述, 锚定本模块"
            "以 AC 自动机做大规模银行实体/金科主题 term-spotting 以构建银行-金科年度面板)"
        )
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
        # 📊 否定模式字面长度分布 (log-only, 不参与匹配; 审计否定窗口的字面跨度)
        _neg_lens = [len(p.strip()) for p in neg_patterns if p.strip()]
        if _neg_lens:
            logger.info(
                f"  📊 否定模式字面长度: min={min(_neg_lens)} / "
                f"mean={sig4(sum(_neg_lens) / len(_neg_lens))} / max={max(_neg_lens)} 字符 "
                "(匹配位置前后各取 10 字符上下文做包含/交叉判定)"
            )

    # 加载短名歧义消解配置
    short_cfg = raw.get('short_name_context_exclusions', {})
    context_window = short_cfg.get('context_window', 5)
    short_exclusions = short_cfg.get('exclusions', {})
    if short_exclusions:
        logger.info(
            f"短名歧义消解: 已加载 {len(short_exclusions)} 个短名称的排除规则，"
            f"上下文窗口: {context_window} 字符"
        )
        # 📊 短名排除上下文规模 (log-only): 每个短名映射若干歧义上下文词
        _excl_ctx_counts = [len(v) for v in short_exclusions.values()
                            if isinstance(v, (list, tuple))]
        if _excl_ctx_counts:
            _total_ctx = sum(_excl_ctx_counts)
            logger.info(
                f"  📊 排除上下文词总数 {_total_ctx:,d} 条; "
                f"平均每短名 {sig4(_total_ctx / len(_excl_ctx_counts))} 条 "
                f"(min={min(_excl_ctx_counts)} / max={max(_excl_ctx_counts)}; "
                "短名 ≤2 字时才触发上下文歧义消解)"
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


def has_unexcluded_occurrence(text: str, pattern: str, negation_ac=None,
                              short_name_exclusions: dict = None,
                              context_window: int = 5) -> bool:
    """检查 pattern 在 text 中是否存在至少一次【未被排除规则命中】的出现。

    fix(omni-g-entity-03/12/16, 2026-06-11): 供 ctx 窗口锚定 (entity_context)
    与导语显著性 (news_salience.target_in_lead) 复用 stage 11 分类的同一套
    negation/short-name 排除语义 (单一匹配语义事实源)。未传排除配置时退化为
    裸子串匹配 (`pattern in text`), 与旧调用方行为兼容。

    Args:
        text:                  待检查文本 (句子 / 导语 / 标题等片段)。
        pattern:               银行名称变体。
        negation_ac:           否定模式 AC 自动机 (可选)。
        short_name_exclusions: 短名歧义排除规则 (可选)。
        context_window:        短名上下文检查窗口。

    Returns:
        bool: True 表示存在至少一次有效出现。
    """
    if not text or not pattern:
        return False
    if negation_ac is None and not short_name_exclusions:
        return pattern in text
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            return False
        end_pos = pos + len(pattern) - 1
        if is_match_excluded(text, end_pos, pattern, negation_ac,
                             short_name_exclusions, context_window) is None:
            return True
        start = pos + 1


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
        logger.info(
            f"金融科技关键词 AC 自动机: 已加载 {len(all_keywords):,d} 个关键词 "
            "(Aho-Corasick 多模式 O(n+m) 全文匹配; 同一算法见 load_bank_names 的 📖 出处)"
        )
        # 📊 结果统计 (关键词长度分布; 全部 log-only, 不参与产物计算)
        _kw_lens = [len(k) for k in all_keywords]
        _kw_short = sum(1 for _l in _kw_lens if _l <= 2)
        logger.info(
            f"  📊 关键词长度: min={min(_kw_lens)} / mean={sig4(sum(_kw_lens) / len(_kw_lens))} / "
            f"max={max(_kw_lens)} 字符; 短词 (≤2 字) {_kw_short:,d} 个 "
            f"({pct4(_kw_short / len(all_keywords))})"
        )
    else:
        ac = None

    return all_keywords, ac


# ============================================================================
# 3. 银行匹配分析(含否定模式和短名歧义消解)
#
# 判定策略(影响精确率和召回率的核心参数):
#   一篇文章被判定为某银行相关新闻需同时满足:
#     (a) 出现次数 >= min_name_occurrences (默认 2)
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
#
#   匹配消解 (fix omni-g-entity-01/02/04/08/09/11/14/15, 2026-06-11):
#     1) 全文【单次】AC 扫描, 按匹配【起点】相对 split_pos 归入上/下半
#        (替代原"先切两半再各自扫描" — 原实现使横跨切分点的名称在两半都
#        不完整而被无声丢失, 且否定/短名上下文窗口在边界被截断);
#     2) 最长匹配位置去重 (longest-match resolution): 嵌套/交叉重叠的跨度
#        只保留最长一个, 跨银行同样适用 — 一次物理提及 "中国工商银行" 不再
#        同时给 "工商银行" 变体计数 (同行 1771 对嵌套变体双计), 一次
#        "法国兴业银行" 不再给 "兴业银行" (另一家银行) 计数 (跨行 71 对)。
# ============================================================================

def _scan_dedup_bank_matches(text: str, bank_ac,
                             negation_ac=None,
                             short_name_exclusions: dict = None,
                             context_window: int = 5) -> tuple:
    """对 text 做单次 AC 全文扫描 → 排除检查 → 最长匹配位置去重。

    fix(omni-g-entity-01/02/04, 2026-06-11):
      - 排除检查在【全文】上做 (否定/短名上下文窗口不再被上下半边界截断);
      - 去重规则: 命中按 (长度降序, 起点升序) 排序, 用 occupied-position set
        丢弃与已保留更长匹配位置重叠的命中 (移植自
        canonicalization._match_keywords 的同型最长匹配范式)。
        嵌套变体 (同行或跨行) 一律归属最长串对应银行。

    Returns:
        tuple: (selected, negation_excluded, short_name_excluded)
          - selected: list[(start, end_pos, bank_idx, variant)] 去重后保留的命中
    """
    negation_excluded = 0
    short_name_excluded = 0
    survivors = []
    for end_pos, (bank_idx, variant) in bank_ac.iter(text):
        reason = is_match_excluded(text, end_pos, variant,
                                   negation_ac, short_name_exclusions,
                                   context_window)
        if reason == 'negation':
            negation_excluded += 1
            continue
        if reason == 'short_name':
            short_name_excluded += 1
            continue
        survivors.append((end_pos - len(variant) + 1, end_pos, bank_idx, variant))

    # 长度降序 + 起点升序 (等长交叉时左侧优先, 保证确定性)
    survivors.sort(key=lambda m: (-(m[1] - m[0] + 1), m[0]))
    occupied: set = set()
    selected = []
    for start, end_pos, bank_idx, variant in survivors:
        positions = range(start, end_pos + 1)
        if any(p in occupied for p in positions):
            continue  # 被更长 (或等长更靠左) 匹配占据 → 丢弃短/后命中
        occupied.update(positions)
        selected.append((start, end_pos, bank_idx, variant))
    return selected, negation_excluded, short_name_excluded

def analyze_bank_matches(content: str, title: str,
                         bank_ac, banks_list: list,
                         split_ratio: float,
                         negation_ac=None,
                         short_name_exclusions: dict = None,
                         context_window: int = 5,
                         min_name_occurrences: int = 2,
                         min_upper: int = 1,
                         min_lower: int = 1) -> dict:
    """分析单篇文章的银行匹配（带否定模式排除和短名歧义消解）。

    这是 11_news_bank.py 和 60_bank_fintech_threshold.py 的共享核心逻辑。

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

    Note:
        fix(omni-g-entity-01/02/04/08/09/11/14/15, 2026-06-11): 改为全文单次
        AC 扫描 (按匹配起点 < split_pos 判定上/下半归属) + 最长匹配位置去重
        (见 _scan_dedup_bank_matches)。语义变更: 嵌套变体不再双计 (同行),
        被他行更长变体覆盖的命中归属最长串对应银行 (跨行); 横跨切分点的
        名称不再丢失; 排除上下文窗口在全文上取, 不再被边界截断。
    """
    content_str = content if isinstance(content, str) else ""
    title_str = title if isinstance(title, str) else ""

    empty_result = {"is_bank_news": False, "matched_banks": [],
                    "negation_excluded": 0, "short_name_excluded": 0}

    if not content_str.strip() and not title_str.strip():
        return empty_result

    if bank_ac is None:
        return empty_result

    # 上下半分割点: 仅作为【位置阈值】使用 (fix omni-g-entity-04/11: 不再物理
    # 切割文本 — 全文单次扫描后按匹配起点归半, 跨切分点的命中归上半)
    split_pos = int(len(content_str) * split_ratio)

    # bank_stats[bank_idx][variant] = {upper: 上半出现次数, lower: 下半出现次数, ...}
    # 使用双层 defaultdict 避免手动初始化
    bank_stats = defaultdict(
        lambda: defaultdict(
            lambda: {'upper': 0, 'lower': 0, 'in_title': False, 'title_count': 0}
        )
    )

    # 扫描正文 (全文单次 + 最长匹配去重)
    body_matches, negation_excluded, short_name_excluded = _scan_dedup_bank_matches(
        content_str, bank_ac, negation_ac, short_name_exclusions, context_window
    )
    for start, _end_pos, bank_idx, variant in body_matches:
        if start < split_pos:
            bank_stats[bank_idx][variant]['upper'] += 1
        else:
            bank_stats[bank_idx][variant]['lower'] += 1

    # 扫描标题 (同样做最长匹配去重: 标题中 "法国兴业银行" 不再给 "兴业银行"
    # 记 in_title — fix omni-g-entity-09 标题路径)
    title_matches, neg_t, short_t = _scan_dedup_bank_matches(
        title_str, bank_ac, negation_ac, short_name_exclusions, context_window
    )
    negation_excluded += neg_t
    short_name_excluded += short_t
    for _start, _end_pos, bank_idx, variant in title_matches:
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
                            min_distinct_keywords: int = 2,
                            min_upper: int = 1,
                            min_lower: int = 1) -> dict:
    """分析单篇文章的金融科技关键词匹配。

    这是 12_news_fintech.py 和 60_bank_fintech_threshold.py 的共享核心逻辑。

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

    Note:
        fix(omni-g-entity-07/11, 2026-06-11): 改为全文单次 AC 扫描, 按匹配
        起点 < split_pos 归入上/下半 — 原"先切两半再各自扫描"使横跨切分点的
        关键词在两半都不完整而被无声丢失 (漏计 total_count / keyword_details
        → 下游 DF/IDF 低估, 边缘文档 is_fintech_news 判定可被翻转)。
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

    # split_pos 仅作位置阈值 (fix omni-g-entity-07/11: 不再物理切割文本)
    split_pos = int(len(content_str) * split_ratio)

    kw_stats = defaultdict(lambda: {'upper': 0, 'lower': 0, 'in_title': False})

    for end_pos, kw in fintech_ac.iter(content_str):
        start = end_pos - len(kw) + 1
        if start < split_pos:
            kw_stats[kw]['upper'] += 1
        else:
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
