"""
core/text/entity_context.py - 实体特异性上下文提取引擎 (历史来源 utils/entity_context.py)
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

import json
import logging
import re
from typing import Dict, List, Set, Tuple

from news_process.core.logging import sig4
from news_process.core.text.ahocorasick import (
    has_unexcluded_occurrence,
    is_match_excluded,
)

logger = logging.getLogger(__name__)

# remove-title-track: 标题注入辅助。取消"标题轨"后, full / ctx 两轨用于情感
# 分析的文本都必须"包含标题"。词典法 (tone_words) 与 BERT (tone_berts) 在构建
# 轨文本时调用本函数把标题拼到正文/上下文前。
# 注意:
#   - LLM (tone_llms) 不调用 — 其 prompt 模板已用独立 title 字段把标题喂给模型
#     (frozen prompt v8), 再拼会重复标题。
#   - 实体窗口类特征 (fintech_intensity / policy_alignment) 消费的是 stage 13
#     ctx_materializer 物化的 content_full / content_ctx 列 — 两轨均已经
#     prepend_title 注入【同一标题】(对称设计, 2026-06-02 病根A修复), 因此
#     ctx 轨分母 (doc_length / token 数) 含标题字符及非连续窗口的 ' [...] '
#     人工分隔符 (每处 7 字符)。
#     fix(omni-g-entity-06, 2026-06-11): 原注释声称 "实体窗口类特征不调用本函数
#     / ctx 不含标题" 与 ctx_materializer.py 实际数据流矛盾, 已按实情更正。
_TITLE_SEP = "。"
_TITLE_END_PUNCT = ("。", "！", "？", "!", "?", "；", ";", "…")


def prepend_title(title: str, body: str) -> str:
    """把标题拼接到正文/上下文前 (full / ctx 两轨共用)。

    - 标题为空 → 原样返回 body。
    - body 已以标题开头 → 不重复拼接 (防"双标题")。
    - 标题末尾已是句末标点 → 直接相连; 否则插入中文句号分隔。
    """
    title = str(title or "").strip()
    body = str(body or "")
    if not title:
        return body
    if body.startswith(title):
        return body
    if title.endswith(_TITLE_END_PUNCT):
        return f"{title}{body}"
    return f"{title}{_TITLE_SEP}{body}"


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
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
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
        negation_ac:          否定模式 AC 自动机 (可选; 与 stage 11 分类共用)。
        short_name_exclusions: 短名歧义排除规则 (可选)。
        context_window:       短名上下文检查窗口。

    Returns:
        str: 实体特异性摘要文本。空字符串表示未匹配到目标银行。

    Note:
        fix(omni-g-entity-03/16, 2026-06-11): 锚句判定由裸 `alias in sent`
        改为 occurrence 级套用 stage 11 的 is_match_excluded 否定/短名排除
        (单一匹配语义事实源) — '涉农行业' 不再为 '农行' 锚定假窗口。
        排除参数缺省 None 时保持旧裸匹配行为 (向后兼容)。
    """
    if not text or not target_aliases:
        return ""

    sentences = _split_sentences(text)

    # 当句子分割退化(< 3 句)时, 回退到字符级窗口。
    # 退化场景: 文本过短或缺少句号标点(如标题、摘要)
    if len(sentences) < 3:
        return _char_level_fallback(
            text, target_aliases, fallback_char_radius,
            negation_ac=negation_ac,
            short_name_exclusions=short_name_exclusions,
            context_window=context_window,
        )

    # 定位目标银行出现的句子索引 (排除规则过滤后的有效出现)
    hit_indices = set()
    for i, sent in enumerate(sentences):
        for alias in target_aliases:
            if has_unexcluded_occurrence(sent, alias, negation_ac,
                                         short_name_exclusions, context_window):
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


def _sent_has_fintech(sent: str, fintech_ac) -> bool:
    """句内是否出现 ≥1 个金科词 (Aho-Corasick 裸匹配, 无否定/短名过滤)。

    与 scripts/audit/measure_bank_fintech_cooccurrence.py::sent_has_fintech 同口径
    (单一事实源, 保证审计==生产)。fintech_ac 为 None 或空句时返回 False。
    """
    if fintech_ac is None or not sent:
        return False
    for _ in fintech_ac.iter(sent):
        return True
    return False


def extract_bank_fintech_cooccurrence(
    text: str,
    target_aliases: List[str],
    fintech_ac,
    sentence_radius: int = 1,
    fallback_char_radius: int = 150,
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
) -> str:
    """第三轨 (ss): 提取【目标银行 ∧ 金融科技词 同句共现】的局部上下文。

    与 extract_entity_context() (ctx 轨, 仅锚银行) 平行, 但锚点改为"同一句内
    同时出现 目标银行 与 金科词"——度量的是文章里【真正把该银行与金融科技放在
    一起谈】的那几句话, 排除罚款/坏账等非金科的银行句 (ctx 轨会保留)。实测
    (disk 1170 篇): 银行句中仅 34% 同时含金科 (主题漂移 65.76%), 故 ss 与 ctx
    是实质不同的独立信号 (互为稳健性, 非冗余)。

    算法 (镜像 extract_entity_context, 复用同款原语):
      1. _split_sentences 分句;
      2. 命中句 = 该句【经否定/短名排除后仍含银行别名】∧【含 ≥1 金科词】;
      3. 命中句前后各 sentence_radius 句扩窗, _merge_intervals 合并;
      4. 拼接, 非连续区间用 ' [...] ' 分隔。
    无任何同句共现 → 返回 '' (空串); 由 stage 13 按【回退公理: 镜像 ctx】回填
    全文 body 并置 ss_is_fallback=True。

    ⚠ 不对称匹配口径 (有意, 与审计脚本一致):
      - 银行侧: has_unexcluded_occurrence —— 套用 stage 11/13 同款否定模式 + 短名
        歧义排除 (NEGATION_AC / SHORT_NAME_EXCLUSIONS)。
      - 金科侧: fintech_ac.iter 裸 AC 匹配 (607 词词典, 2026-07-21 换血), 不做否定/短名过滤。

    口径单一事实源 = scripts/audit/measure_bank_fintech_cooccurrence.py
    (sent_has_bank / sent_has_fintech), 保证审计==生产逐字节一致。

    学术谱系: 同句共现 (co-mention / collocation) 作为"主题相关性"归因过滤, 承接
      proximity-based attribution 谱系 —— Hassan et al. (2019) QJE §III.B (实体邻近
      归因) 与 Andreou et al. (2026) Research Policy (span 内 core-contextual 词对)
      的"同窗共现"特例。同句 (same-sentence, radius=0) 即上述 proximity 归因谱系的最严
      特例 (Hassan et al. 2019 实体邻近归因的零半径退化), 不另设专属同句文献锚点;
      相关 co-mention / collocation 旁证 (Gentzkow & Shapiro 2010 ECMA / Dougal et al.
      2012 RFS) 见 scripts/audit/LITERATURE_ANCHORS。

    Args / Returns: 同 extract_entity_context, 另加 fintech_ac (金科 AC 自动机)。
    """
    if not text or not target_aliases or fintech_ac is None:
        return ""

    sentences = _split_sentences(text)

    # 短文本 (<3 句) 退化: 走字符级回退, 传入 fintech_ac 要求"同窗共现"。
    if len(sentences) < 3:
        return _char_level_fallback(
            text, target_aliases, fallback_char_radius,
            negation_ac=negation_ac,
            short_name_exclusions=short_name_exclusions,
            context_window=context_window,
            fintech_ac=fintech_ac,
        )

    # 命中句索引: 银行 (排除过滤后) ∧ 金科 同句 (先筛金科, 便宜)。
    hit_indices = set()
    for i, sent in enumerate(sentences):
        if not _sent_has_fintech(sent, fintech_ac):
            continue
        for alias in target_aliases:
            if has_unexcluded_occurrence(sent, alias, negation_ac,
                                         short_name_exclusions, context_window):
                hit_indices.add(i)
                break

    if not hit_indices:
        return ""

    n = len(sentences)
    raw_intervals = [
        (max(0, i - sentence_radius), min(n - 1, i + sentence_radius))
        for i in hit_indices
    ]
    merged = _merge_intervals(raw_intervals)
    fragments = ["".join(sentences[s:e + 1]) for s, e in merged]
    return " [...] ".join(fragments)


def _char_level_fallback(
    text: str,
    target_aliases: List[str],
    radius: int = 150,
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
    fintech_ac=None,
) -> str:
    """字符级回退: 当文本过短无法有效分句时使用。

    策略: 以银行名称出现位置为中心, 前后各取 radius 个字符。
    多个匹配位置的窗口仍执行区间合并。

    fix(omni-g-entity-03/16, 2026-06-11): 出现位置先经 is_match_excluded
    否定/短名排除再开窗 (与句级路径同口径); 排除参数缺省时行为不变。

    三轨 (ss 同句共现轨, 2026-06-14): 可选 fintech_ac 参数。
      - fintech_ac=None  → 仅锚银行 (ctx 轨既有行为, 字节不变, 向后兼容)。
      - fintech_ac 提供  → 仅当【银行出现位置的字符窗口内同时含金科词】才开窗
        (短文本 <3 句无法分句时, 以"同窗口"近似"同句"共现, 与句级 ss 同取向)。
    """
    intervals = []
    for alias in target_aliases:
        start_pos = 0
        while True:
            pos = text.find(alias, start_pos)
            if pos == -1:
                break
            if (negation_ac is not None or short_name_exclusions) and \
                    is_match_excluded(text, pos + len(alias) - 1, alias,
                                      negation_ac, short_name_exclusions,
                                      context_window) is not None:
                start_pos = pos + 1
                continue  # 被排除规则命中的假出现不开窗
            lo = max(0, pos - radius)
            hi = min(len(text) - 1, pos + len(alias) + radius)
            # ss 轨: 该银行窗口内须同时含金科词, 否则非"同句共现", 不开窗。
            if fintech_ac is not None and not _sent_has_fintech(text[lo:hi + 1],
                                                                fintech_ac):
                start_pos = pos + 1
                continue
            intervals.append((lo, hi))
            start_pos = pos + 1

    if not intervals:
        return ""

    merged = _merge_intervals(intervals)
    return " [...] ".join(text[s:e + 1] for s, e in merged)


def has_bank_fintech_cooccurrence_within_radius(
    text: str,
    target_aliases: List[str],
    fintech_ac,
    sentence_radius: int = 1,
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
    fallback_char_radius: int = 150,
) -> bool:
    """Stage 12b 共现【保留判据】(通用 radius): 目标银行与金科词是否在
    ±sentence_radius 句窗口内共现。返回 True ⇒ 该 (文章, target_bank) 行保留;
    False ⇒ 丢弃。生产默认 radius=1 = ±1 句窗口邻近 (银行锚句 i 或其前后邻句含 ≥1 金科词);
    radius=0 = 严格同句 (银行锚句 i 自身含 ≥1 金科词, 最严特例, 稳健性备选)。

    Andreou et al. (2026, Research Policy) core-contextual word-pairing 的【句级
    窗口】操作化: 生产默认 radius=1 ±1 句窗口邻近是其句级窗口操作化; radius=0 同句是其
    零半径最严特例 (比 10-lexical-token span 更紧, 稳健性备选)。

    ⚠ 与 extract_bank_fintech_cooccurrence 口径【不同, 禁止互相替代】:
      - 本函数 (通用窗口): 命中 = ∃ 银行锚句 i (经否定/短名排除后仍含别名) 且
        闭区间 [i-sentence_radius, i+sentence_radius] 内任一句含 ≥1 金科词。
      - extract_bank_fintech_cooccurrence (严格同句): 命中句须【同一句】内同时
        含银行与金科, 再扩【输出窗】。
      二者在 sentence_radius=0 时于命中检测上等价 (radius=0 严格同句最严特例); 生产默认
      radius=1 时本函数更宽、二者不等价 (keep 集 ⊋ 严格同句集 → 下游 _ss 严格同句轨保留
      独立信号, frac_ss_fallback∈(0,1))。
      ⚠ 生产 stage 12b 默认 radius=1 (2026-06-29 决策, 取代 2026-06-27 的 radius=0, 见
      config/filtering.yaml + cooccurrence_filter.py): keep 集 ⊋ 同句集 → 下游 _ss 保留
      独立信号、frac_ss_fallback∈(0,1); 若改回 radius=0 严格同句 (稳健性备选) 则 keep 集 ≡
      同句集 → _ss 回退变异坍缩 (frac_ss_fallback→≈0, match_in_title=true 仅部分缓解)。

    不对称口径 (与 extract_bank_fintech_cooccurrence / 审计脚本一致):
      银行侧 has_unexcluded_occurrence (否定+短名排除); 金科侧裸 AC
      (_sent_has_fintech, 607 词)。

    短文本 (<3 句) 退化: 走 _char_level_fallback(fintech_ac=...) 字符窗近似,
    非空即视为共现 (与 extract_bank_fintech_cooccurrence 同回退路径; ⚠ 字符窗
    判据宽度与句窗不同, keep 率 gate 须分长/短文本两层披露)。

    Args / Returns: 同 extract_bank_fintech_cooccurrence, 但返回 bool。
    """
    if not text or not target_aliases or fintech_ac is None:
        return False

    sentences = _split_sentences(text)

    # 短文本 (<3 句): 复用字符级回退 (传 fintech_ac 要求同窗共现), 非空即共现。
    if len(sentences) < 3:
        return bool(_char_level_fallback(
            text, target_aliases, fallback_char_radius,
            negation_ac=negation_ac,
            short_name_exclusions=short_name_exclusions,
            context_window=context_window,
            fintech_ac=fintech_ac,
        ))

    n = len(sentences)
    for i, sent in enumerate(sentences):
        # 外层: 该句经否定/短名排除后仍含目标银行别名 (银行锚句)。
        if not any(
            has_unexcluded_occurrence(sent, alias, negation_ac,
                                      short_name_exclusions, context_window)
            for alias in target_aliases
        ):
            continue
        # 内层: 闭区间 [i-radius, i+radius] 任一句含 ≥1 金科词 → 命中。
        lo = max(0, i - sentence_radius)
        hi = min(n - 1, i + sentence_radius)
        for j in range(lo, hi + 1):
            if _sent_has_fintech(sentences[j], fintech_ac):
                return True
    return False


# ============================================================================
# 银行∧银行 句级共现原语 (network criteria sensitivity, 2026-07-03)
# ============================================================================
# ② 类"网络构造判据敏感性"专用: 结构网络指标按 {同篇(无后缀)/±1句窗 _win1/
# 严格同句 _sent} 三种银行∧银行共现判据分轨。本节两个原语是其唯一事实源
# (panel 生产 network_spillover.build_adjacency_matrix 与审计脚本
# scripts/audit/measure_bank_bank_cooccurrence.py 共用, 审计==生产)。
#
# ⚠ 与上方银行∧金科原语 (has_bank_fintech_cooccurrence_within_radius /
#   extract_bank_fintech_cooccurrence) 并列且【互不复用】— 判据主体不同
#   (银行∧银行 vs 银行∧金科), 口径铁律禁互代。
# ⚠ 实现口径 (计划 §8 实施偏差记录): 逐句 has_unexcluded_occurrence 判定
#   (与 ctx/ss 轨锚句判定字节级同款原语), 【不做】字符位置→句索引映射 —
#   _split_sentences 对每段 strip 且丢空段, 无法还原原文偏移, naive 累计
#   长度二分会把命中系统性映射到错误句索引 (评审 sparsity-numeric-1 实证)。
#   逐句判定从根上无此问题, 且与三轨文本的句窗语义共用同一 _split_sentences。
# ⚠ 文本口径 (D19, 镜像 stage 13 match_in_title=true): text =
#   prepend_title(标题, 正文) — 标题自成第 0 句, 参与 _sent 同句判定
#   (标题双银行 → 成边) 与 _win1 距离 (与正文首句相邻)。依据: stage 13 曾
#   实证修复"只读正文 → 标题点明实体的单向假阴性" (config/filtering.yaml)。
# ⚠ 短文本不设字符回退: 单句文章两银行必同句, 语义自洽 (D10)。
# ============================================================================

def map_bank_sentence_positions(
    title: str,
    body: str,
    banks_aliases: Dict[str, List[str]],
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
) -> Dict[str, Set[int]]:
    """定位一组银行在 (标题+正文) 中各自出现的句子索引集合。

    银行∧银行共现判据 (_win1/_sent) 的定位原语。调用方 (network_spillover
    B1) 须只传入该 docid 组的【幸存 target_bank】别名字典 — 非幸存银行
    不在输入即不可能成边 (phantom 边防线, omni-g-net-spill-01)。

    Args:
        title:          文章标题 ('标题' 列; 空串安全)。
        body:           文章正文 ('内容' 列)。
        banks_aliases:  {标准银行名: [别名列表]} — 仅幸存 target_bank。
        negation_ac:    否定模式 AC 自动机 (与 stage 11/13/ctx/ss 共用)。
        short_name_exclusions: 短名歧义排除规则 (同上)。
        context_window: 短名上下文检查窗口。

    Returns:
        dict[str, set[int]]: {银行名: 命中句索引集}; 无有效命中的银行不出现。
        句索引基于 prepend_title 后的 _split_sentences 口径 (标题=第 0 句)。
    """
    text = prepend_title(title, body)
    if not text or not banks_aliases:
        return {}
    sentences = _split_sentences(text)
    if not sentences:
        return {}
    out: Dict[str, Set[int]] = {}
    for bank, aliases in banks_aliases.items():
        if not aliases:
            continue
        hits: Set[int] = set()
        for i, sent in enumerate(sentences):
            for alias in aliases:
                if has_unexcluded_occurrence(sent, alias, negation_ac,
                                             short_name_exclusions,
                                             context_window):
                    hits.add(i)
                    break  # 一个别名命中即可
        if hits:
            out[bank] = hits
    return out


def bank_pairs_within_sentence_window(
    bank_sent_idx: Dict[str, Set[int]],
    win_radius: int = 0,
) -> Set[Tuple[str, str]]:
    """由句索引集判定银行无序对是否按句窗判据成边。

    判据 (D11 对称化): 无序对 {A, B} 成边 ⇔ min |i - j| ≤ win_radius
    (i ∈ A 的句集, j ∈ B 的句集)。|i-j| 天然对称, 等价于 "A 锚句 ±radius
    内含 B 或反之" 的 OR 口径。win_radius=0 = 严格同句 (_sent);
    win_radius=1 = ±1 句窗 (_win1)。

    Returns:
        set[tuple[str, str]]: canonical 名序 (sorted) 的成边无序对集合。
    """
    banks = sorted(b for b, idx in bank_sent_idx.items() if idx)
    edges: Set[Tuple[str, str]] = set()
    for a_pos, bank_a in enumerate(banks):
        idx_a = bank_sent_idx[bank_a]
        for bank_b in banks[a_pos + 1:]:
            idx_b = bank_sent_idx[bank_b]
            hit = any(abs(i - j) <= win_radius for i in idx_a for j in idx_b)
            if hit:
                edges.add((bank_a, bank_b))
    return edges


# ============================================================================
# G-14: 距离衰减结构化输出
# ============================================================================
# 学术依据:
#   Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023).
#   Firm-level climate change exposure. The Journal of Finance, 78(3),
#   1449–1498. DOI: 10.1111/jofi.13219 (§2.2):
#     "We weight each bigram token by its inverse distance to the
#      nearest climate change keyword."
#   本函数返回句子+距离对, 供下游词典法做距离加权情感计算。
# ============================================================================

def extract_entity_context_with_distances(
    text: str,
    target_aliases: List[str],
    sentence_radius: int = 2,
    negation_ac=None,
    short_name_exclusions: dict = None,
    context_window: int = 5,
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
        negation_ac:     否定模式 AC 自动机 (可选; 与 stage 11 分类共用)。
        short_name_exclusions: 短名歧义排除规则 (可选)。
        context_window:  短名上下文检查窗口。

    Returns:
        list[tuple[str, int]]: 窗口内的 (句子文本, 距离) 对。
            空列表表示未匹配到目标银行。

    Note:
        fix(omni-g-entity-03/16, 2026-06-11): 与 extract_entity_context 同步
        支持 occurrence 级否定/短名排除; 排除参数缺省时行为不变。
    """
    if not text or not target_aliases:
        return []

    sentences = _split_sentences(text)

    if len(sentences) < 3:
        # 短文本退化: 检查是否有任何句子命中目标银行 (排除规则过滤后)
        has_hit = any(
            has_unexcluded_occurrence(s, alias, negation_ac,
                                      short_name_exclusions, context_window)
            for s in sentences
            for alias in target_aliases
        )
        if has_hit:
            return [(sent, 0) for sent in sentences]
        return []

    # 定位命中句索引 (排除规则过滤后的有效出现)
    hit_indices = set()
    for i, sent in enumerate(sentences):
        for alias in target_aliases:
            if has_unexcluded_occurrence(sent, alias, negation_ac,
                                         short_name_exclusions, context_window):
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

        # ── 一次性 (首次加载触发, 每进程恰一次) 运行期/方法论日志 ──
        # 本块仅 emit 进日志, 不参与任何返回值/缓存内容计算 → golden-safe。
        # entity_context 是实体特异性上下文提取引擎的单一事实源 (ctx/ss 两轨 +
        # 距离衰减 + stage 12b 共现判据均复用本模块原语); 在其唯一"每进程一次"
        # 的入口 (银行别名词表加载) 处汇报词表规模与方法论锚点。
        _n_banks = len(_BANK_DATA)
        _variant_counts = [len(b.get('variants', [])) for b in _BANK_DATA]
        _total_variants = sum(_variant_counts)
        _mean_variants = (_total_variants / _n_banks) if _n_banks else 0.0
        _max_variants = max(_variant_counts) if _variant_counts else 0
        logger.info("=" * 60)
        logger.info("📊 entity_context 运行期参数 (实体特异性上下文提取引擎)")
        logger.info(f"   ├─ 银行别名词表           : {bank_names_file}")
        logger.info(f"   ├─ 目标银行实体数         : {_n_banks:,} 家")
        logger.info(f"   ├─ 名称变体 (别名) 总数   : {_total_variants:,} 条")
        logger.info(
            f"   ├─ 每行平均别名数         : {sig4(_mean_variants)} 条/家 "
            f"(单家最多 {_max_variants:,} 条)"
        )
        logger.info(
            "   └─ 提取原语: 句级窗口 [_split_sentences→hit→±radius 扩窗→"
            "O(N log N) _merge_intervals]; 三轨 ctx(仅锚银行) / ss(银行∧金科"
            "同句) / 距离衰减(inverse-distance), 不对称口径(银行侧否定+短名排除"
            "/金科侧裸 AC)"
        )
        logger.info("📖 方法论依据 (本模块所锚定的同行评议文献):")
        logger.info(
            "   [1] Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). "
            "Firm-level climate change exposure. The Journal of Finance, 78(3), "
            "1449–1498. https://doi.org/10.1111/jofi.13219"
        )
        logger.info(
            "       (白话: 以关键词/二元组命中构建 firm-level 文本暴露并按到最近"
            "关键词的 inverse-distance 加权 — 本模块距离衰减输出与词表锚定的范式来源)"
        )
        logger.info(
            "   [2] Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., "
            "Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. "
            "The Quarterly Journal of Economics, 140(2), 1299–1365. "
            "https://doi.org/10.1093/qje/qjaf002"
        )
        logger.info(
            "       (白话: 用文本 bigram 识别新兴技术并追踪其扩散 — 支撑 ss 轨"
            "以金科词同句命中度量「银行×金融科技」主题关注的合法性)"
        )
        logger.info(
            "   [3] Wu, D. (A.). (2024). Text-based measure of supply chain risk "
            "exposure. Management Science, 70(7), 4781–4801. "
            "https://doi.org/10.1287/mnsc.2023.4927"
        )
        logger.info(
            "       (白话: 种子词+词袋构 firm-level 文本暴露并以波动率外部验证 — "
            "本模块「实体特异性局部窗口→企业级文本度量」管线的同法近期实例)"
        )
        logger.info("=" * 60)

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
