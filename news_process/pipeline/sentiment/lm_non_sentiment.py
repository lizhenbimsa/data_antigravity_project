"""news_process.pipeline.sentiment.lm_non_sentiment — A1 LM 4 子词典中文实现.

v3.5.2 PR #3 (与 forward_looking.py 同 sprint) — 复用 v3.5.1 A1 lexical
clarity 的 ``_compute_clarity_for_text`` + ``_dual_analyze`` 真双轨架构,
但喂入 LM 2011 JF non-sentiment 4 个子词典:
    uncertainty / litigious / constraining / modal_strong

学术依据
--------
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability?
Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65.

Bochkay, K., Hales, J., & Chava, S. (2020). Hyperbole or Reality? Investor
Response to Extreme Language in Earnings Conference Calls. The Accounting
Review, 95(2), 31-60.

panel 新增 8 列 (双轨 × 4 子集)
-------------------------------
``uncert_frac_{full,ctx}``     不确定性词频比例
``litig_frac_{full,ctx}``      诉讼/监管风险词频比例
``constr_frac_{full,ctx}``     约束词频比例
``modal_strong_frac_{full,ctx}`` 强势模态词频比例

集成点 (PR #14)
---------------
``pipeline.sentiment.tone_words::_dual_analyze`` 内对 content_full / content_ctx
各调用一次本模块的 ``_compute_lm_non_sentiment_for_text``, 把 4 项结果
加入 result dict.

stub 说明
---------
词表 v0.1.5 共 314 词 (uncert 83 / litig 104 / constr 76 / modal_strong 51),
status=AWAITING_EXPERT_AUDIT (见 config/lm_non_sentiment_dicts.json::_meta).
v0.2 由中文金融专家扩至 LM 2011 原版 1219 词覆盖 (G-A1.1 准入门控).
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

_LM_DICT_PATH = (
    Path(__file__).resolve().parents[2] / 'config' / 'lm_non_sentiment_dicts.json'
)

_SUBSETS = ('uncertainty', 'litigious', 'constraining', 'modal_strong')

# panel 列前缀映射 (与 LM 原文 + Bochkay 2020 命名约定一致)
SUBSET_PREFIX = {
    'uncertainty': 'uncert',
    'litigious': 'litig',
    'constraining': 'constr',
    'modal_strong': 'modal_strong',
}


@lru_cache(maxsize=1)
def load_lm_non_sentiment_dicts() -> dict[str, frozenset[str]]:
    """加载 LM 4 子词典 (lru_cache 单例).

    Returns:
        {subset_name: frozenset(words)} for 4 subsets.

    Note:
        当前是 v0.1.5 (共 314 词: uncert 83 / litig 104 / constr 76 / modal_strong 51);
        G-A1.1 门控通过后由专家扩展.
    """
    if not _LM_DICT_PATH.exists():
        return {s: frozenset() for s in _SUBSETS}
    with open(_LM_DICT_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return {
        s: frozenset(raw.get(s, []) or [])
        for s in _SUBSETS
    }


def _compute_lm_non_sentiment_for_text(
    text: str,
    dicts: dict[str, frozenset[str]] | None = None,
) -> dict[str, float]:
    """单文本 LM 4 子集词频; 仿 v3.5.1 ``_compute_clarity_for_text`` 接口.

    与 ``_dual_analyze`` (tone_words.py:982) 在 content_full / content_ctx
    各调用一次, 实现真双轨 (修双轨假化, 参见 v3.5.1 plan §2.1).

    Args:
        text: 待分析的中文文本.
        dicts: 4 子词典 dict; ``None`` 用 ``load_lm_non_sentiment_dicts()``.

    Returns:
        {
            'n_tokens': int,
            'n_uncert': int, 'frac_uncert': float | nan,
            'n_litig': int, 'frac_litig': float | nan,
            'n_constr': int, 'frac_constr': float | nan,
            'n_modal_strong': int, 'frac_modal_strong': float | nan,
        }

    Note:
        nan 仅在 n_tokens == 0 (空文本/全停用词) 时出现.
    """
    dicts = dicts or load_lm_non_sentiment_dicts()
    empty = {
        'n_tokens': 0,
        'n_uncert': 0, 'frac_uncert': float('nan'),
        'n_litig': 0, 'frac_litig': float('nan'),
        'n_constr': 0, 'frac_constr': float('nan'),
        'n_modal_strong': 0, 'frac_modal_strong': float('nan'),
    }
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

    # 词典级匹配 (token in frozenset, O(1) 查找)
    counts = {s: 0 for s in _SUBSETS}
    for tok in tokens:
        for s in _SUBSETS:
            if tok in dicts[s]:
                counts[s] += 1

    return {
        'n_tokens': n_tokens,
        'n_uncert': counts['uncertainty'],
        'frac_uncert': counts['uncertainty'] / n_tokens,
        'n_litig': counts['litigious'],
        'frac_litig': counts['litigious'] / n_tokens,
        'n_constr': counts['constraining'],
        'frac_constr': counts['constraining'] / n_tokens,
        'n_modal_strong': counts['modal_strong'],
        'frac_modal_strong': counts['modal_strong'] / n_tokens,
    }


def get_panel_columns(suffix: str) -> list[str]:
    """返回 panel 应追加的 4 列名 (按指定后缀, 双轨各 4 列).

    Args:
        suffix: '_full' 或 '_ctx'.

    Returns:
        [f'uncert_frac{suffix}', f'litig_frac{suffix}', ...]
    """
    return [f'{p}_frac{suffix}' for p in
            ('uncert', 'litig', 'constr', 'modal_strong')]


__all__ = [
    'load_lm_non_sentiment_dicts',
    '_compute_lm_non_sentiment_for_text',
    'get_panel_columns',
    'SUBSET_PREFIX',
]
