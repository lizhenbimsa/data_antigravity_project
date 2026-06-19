"""news_process.pipeline.sentiment.lm_non_sentiment — A1 LM 6 子词典中文实现.

v3.5.2 PR #3 (与 forward_looking.py 同 sprint) — 复用 v3.5.1 A1 lexical
clarity 的 ``_compute_clarity_for_text`` + ``_dual_analyze`` (函数名为历史 legacy,
现已三轨 full/ctx/ss) 真三轨 (full/ctx/ss) 架构,
但喂入 LM 2011 JF non-sentiment 6 个子词典 (v3.10.0 由 4→6, 新增 weak_modal/complexity):
    uncertainty / litigious / constraining / modal_strong / weak_modal / complexity

学术依据
--------
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability?
Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65.

Bochkay, K., Hales, J., & Chava, S. (2020). Hyperbole or Reality? Investor
Response to Extreme Language in Earnings Conference Calls. The Accounting
Review, 95(2), 31-60.

panel 新增 18 列 (v3.10.0 三轨 × 6 子集; 原 v3.9.0 为 12 列 × 4 子集)
---------------------------------------
``uncert_frac_{full,ctx,ss}``     不确定性词频比例
``litig_frac_{full,ctx,ss}``      诉讼/监管风险词频比例
``constr_frac_{full,ctx,ss}``     约束词频比例
``modal_strong_frac_{full,ctx,ss}`` 强势模态词频比例
``modal_weak_frac_{full,ctx,ss}``   弱势模态词频比例 (weak_modal, v3.10.0 新增)
``complexity_frac_{full,ctx,ss}``   复杂度词频比例 (complexity, v3.10.0 新增)
(ss = 银行+金科同句共现轨; ``_compute_lm_non_sentiment_for_text`` 本身 track-agnostic,
第三轨由调用方用 content_ss 文本驱动, 本模块无需改动)

集成点 (PR #14)
---------------
``pipeline.sentiment.tone_words::_dual_analyze`` 内对 content_full / content_ctx /
content_ss 各调用一次本模块的 ``_compute_lm_non_sentiment_for_text`` (三轨), 把 6 项结果
加入 result dict.

数据源 (2026-06-18 替代)
-----------------------
原手工 stub v0.1.5 (``lm_non_sentiment``, 314 词, AWAITING_EXPERT_AUDIT) 经用户 directive
"用 loughran_mcdonald_zh_2026 完全替代 lm_non_sentiment" 已**废弃并从 tone_dicts.json 删除**。
本模块 6 个非情感子集现取自 L&M 情感主译全本 ``config/tone_dicts.json::loughran_mcdonald_zh_2026``
的对应非极性类别 (uncertainty 392 / litigious 913 / constraining 174 / strong_modal 54 /
weak_modal 55 / complexity 129 = 1717 词; 经 325-agent 审计的全本翻译, 远超原 314 词 stub)。
⚠ loughran 类别键用 strong_modal/weak_modal, 本模块 subset 沿用 modal_strong/modal_weak → 经 ``_SUBSET_SOURCE`` 映射。
⚠ 这是**有意的测度变更** (非行为保持): 18 个 frac panel 列 (uncert/litig/constr/modal_strong/modal_weak/complexity_frac
× full/ctx/ss) 的数值随词表扩大而改变, golden 须重生 (M0 gate)。
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import jieba

# fix(lmfls-01, 2026-06-10): 纯标点/纯数字/下划线 token 正则 (LM 2011 词数分母须排除)。
# \w (re.UNICODE 默认) 含 CJK 与字母 → [\W\d_]+ 仅匹配全标点/全数字/下划线串; 含一个汉字
# 或字母的 token 不会 fullmatch, 被保留为 word。
_LMFLS_NONWORD_RE = re.compile(r'[\W\d_]+')

# 数据源 (2026-06-18 替代): 6 个非情感子集取自 L&M 情感主译全本 ``loughran_mcdonald_zh_2026``
# 的对应非极性类别 (原 lm_non_sentiment stub 已删除)。_LM_DICT_PATH 指向 tone_dicts.json;
# _LM_DICT_KEY = 源条目顶层键。
_LM_DICT_PATH = (
    Path(__file__).resolve().parents[2] / 'config' / 'tone_dicts.json'
)
_LM_DICT_KEY = 'loughran_mcdonald_zh_2026'

# v3.10.0: 6 个非情感子集 (原 4 + weak_modal/complexity)。
_SUBSETS = ('uncertainty', 'litigious', 'constraining', 'modal_strong',
            'weak_modal', 'complexity')

# 本模块 subset 名 → loughran_mcdonald_zh_2026 条目内的源类别键
# (loughran 用 strong_modal; 其余同名)。
_SUBSET_SOURCE = {
    'uncertainty': 'uncertainty',
    'litigious': 'litigious',
    'constraining': 'constraining',
    'modal_strong': 'strong_modal',
    'weak_modal': 'weak_modal',
    'complexity': 'complexity',
}

# panel 列前缀映射 (与 LM 原文 + Bochkay 2020 命名约定一致)。
# 注: 'modal_weak' 与既有 'modal_strong' 对仗; 'complexity' 列名 complexity_frac_full=20<32
# 无需缩短 (v3.10.0 命名约定, 全项目统一用 modal_weak_frac / complexity_frac)。
SUBSET_PREFIX = {
    'uncertainty': 'uncert',
    'litigious': 'litig',
    'constraining': 'constr',
    'modal_strong': 'modal_strong',
    'weak_modal': 'modal_weak',
    'complexity': 'complexity',
}

# 前缀元组 (按 _SUBSETS 顺序, 供 tone_words 等下游泛型迭代; 取代各处硬编码 4-元组)。
SUBSET_PREFIXES = tuple(SUBSET_PREFIX[s] for s in _SUBSETS)


@lru_cache(maxsize=1)
def load_lm_non_sentiment_dicts() -> dict[str, frozenset[str]]:
    """加载 LM 6 子词典 (lru_cache 单例).

    Returns:
        {subset_name: frozenset(words)} for 6 subsets.

    Note:
        源自 loughran_mcdonald_zh_2026 的 6 个非极性类别 (v3.10.0 起):
        uncert 392 / litig 913 / constr 174 / modal_strong←strong_modal 54 /
        weak_modal 55 / complexity 129; 原 314 词 stub 已删除 (见模块 docstring 数据源段)。
    """
    if not _LM_DICT_PATH.exists():
        return {s: frozenset() for s in _SUBSETS}
    with open(_LM_DICT_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    # 自 config/tone_dicts.json::loughran_mcdonald_zh_2026 取 6 个非极性类别 (2026-06-18 替代);
    # 经 _SUBSET_SOURCE 映射 (modal_strong←strong_modal, modal_weak←weak_modal)。文件/条目缺失 → 6 空 frozenset (优雅降级)。
    entry = raw.get(_LM_DICT_KEY, {}) if isinstance(raw, dict) else {}
    if not isinstance(entry, dict):
        entry = {}
    return {
        s: frozenset(entry.get(_SUBSET_SOURCE[s], []) or [])
        for s in _SUBSETS
    }


def _compute_lm_non_sentiment_for_text(
    text: str,
    dicts: dict[str, frozenset[str]] | None = None,
) -> dict[str, float]:
    """单文本 LM 6 子集词频; 仿 v3.5.1 ``_compute_clarity_for_text`` 接口.

    与 ``_dual_analyze`` (tone_words.py:1417) 在 content_full / content_ctx / content_ss
    各调用一次, 实现真三轨 (修双轨假化, 参见 v3.5.1 plan §2.1; v3.9.0 +ss=银行+金科同句
    共现轨)。本函数 track-agnostic (输入单一文本), 第三轨由调用方传 content_ss 驱动。

    Args:
        text: 待分析的中文文本.
        dicts: 6 子词典 dict; ``None`` 用 ``load_lm_non_sentiment_dicts()``.

    Returns:
        {
            'n_tokens': int,
            'n_uncert': int, 'frac_uncert': float | nan,
            'n_litig': int, 'frac_litig': float | nan,
            'n_constr': int, 'frac_constr': float | nan,
            'n_modal_strong': int, 'frac_modal_strong': float | nan,
            'n_modal_weak': int, 'frac_modal_weak': float | nan,
            'n_complexity': int, 'frac_complexity': float | nan,
        }

    Note:
        nan 仅在 n_tokens == 0 (空文本/全停用词) 时出现.
    """
    dicts = dicts or load_lm_non_sentiment_dicts()
    # v3.10.0 泛型化: empty/return dict 按 _SUBSETS 循环构建 (取代逐子集硬编码 9 键)。
    # 对现有 4 子集字节等价 (键名/顺序不变: n_tokens, n_uncert, frac_uncert, ...)。
    empty = {'n_tokens': 0}
    for s in _SUBSETS:
        p = SUBSET_PREFIX[s]
        empty[f'n_{p}'] = 0
        empty[f'frac_{p}'] = float('nan')
    if not text or not text.strip():
        return empty

    tokens = list(jieba.cut(text))
    # fix(lmfls-01, metric-audit 2026-06-10): Loughran-McDonald (2011, JF) 的词表占比分母是
    # **词数** (排除纯数字与标点 token), 原 n_tokens 含 ~19% 标点/纯数字 token → 四个 frac
    # (uncert/litig/constr/modal_strong) 系统性下偏。仅计含字母/汉字的 word token。
    # 注: 数值分子 counts 不变 (LM 词典词均为真词, 标点/数字本不命中), 仅分母收紧。
    # 白话: 算"不确定词占比"时, 分母原来把逗号、句号、纯数字也当词数了,
    # 等于把蛋糕做大却没多放料, 比例被系统性压低; 现在分母只数真正的词。
    word_tokens = [t for t in tokens if t.strip() and not _LMFLS_NONWORD_RE.fullmatch(t.strip())]
    n_tokens = len(word_tokens)
    if n_tokens == 0:
        return empty

    # 词典级匹配 (token in frozenset, O(1) 查找)。
    # dicts.get(s, frozenset()): 容忍部分 dict (调用方可只传子集, 如单测); 真实 6-key
    # dict 下与 dicts[s] 字节等价 (与 tone_words tone_tok 包装同口径)。
    counts = {s: 0 for s in _SUBSETS}
    for tok in tokens:
        for s in _SUBSETS:
            if tok in dicts.get(s, frozenset()):
                counts[s] += 1

    result = {'n_tokens': n_tokens}
    for s in _SUBSETS:
        p = SUBSET_PREFIX[s]
        result[f'n_{p}'] = counts[s]
        result[f'frac_{p}'] = counts[s] / n_tokens
    return result


def get_panel_columns(suffix: str) -> list[str]:
    """返回 panel 应追加的 6 列名 (按指定后缀, 三轨各 6 列 = 18 列, v3.10.0).

    suffix-parameterized → 本函数 track-agnostic, 调用方传 '_ss' 即得同句共现轨列名。

    Args:
        suffix: '_full' / '_ctx' / '_ss' (ss = 银行+金科同句共现轨).

    Returns:
        [f'uncert_frac{suffix}', f'litig_frac{suffix}', ..., f'complexity_frac{suffix}']
    """
    return [f'{p}_frac{suffix}' for p in SUBSET_PREFIXES]


__all__ = [
    'load_lm_non_sentiment_dicts',
    '_compute_lm_non_sentiment_for_text',
    'get_panel_columns',
    'SUBSET_PREFIX',
    'SUBSET_PREFIXES',
    '_SUBSETS',
]
