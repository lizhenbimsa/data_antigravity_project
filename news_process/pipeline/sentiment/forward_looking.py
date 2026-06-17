"""news_process.pipeline.sentiment.forward_looking — A2 中文 FLS 实施.

v3.5.2 PR #3 (与 lm_non_sentiment.py 同 sprint) — 中文 Forward-Looking
Statements 句子级双门控判定. 复用 v3.5.2 PR #1 ``cn_text_utils`` 的中文
分句器, 不依赖任何 v3.6.0 之外的新包.

学术依据
--------
Li, F. (2010). The Information Content of Forward-Looking Statements in
Corporate Filings — A Naïve Bayesian Machine Learning Approach. Journal of
Accounting Research, 48(5), 1049-1102.

Bozanic, Z., Roulstone, D. T., & Van Buskirk, A. (2018). Management
earnings forecasts and other forward-looking statements. Journal of
Accounting and Economics, 65(1), 1-20.

判定规则 (双门控)
-----------------
一个句子是 FLS 当且仅当:
    ∃ w ∈ s: w ∈ D_future  ∧  ∃ t ∈ s: t ∈ D_time

D_future = {将, 拟, 预计, 计划, 望, 展望, 期待, 着力, 力争, 致力于, 有望, ...}
D_time   = {未来, 明年, 下季, 三年内, 中长期, 下一阶段, ...}

panel 新增 3 列 (v3.9.0 三轨, +ss)
---------------------------------
``frac_fls_{full,ctx,ss}`` = (FLS 句数) / (总句数) ∈ [0, 1]
(ss = 银行+金科同句共现轨; ``compute_fls_for_text`` 本身 track-agnostic,
第三轨由调用方用 content_ss 文本驱动, 本模块无需改动)

集成点 (PR #14)
---------------
``pipeline.sentiment.tone_words::_dual_analyze`` 内对 content_full / content_ctx /
content_ss 各调用一次本模块的 ``compute_fls_for_text`` (三轨).

G-A2.1 准入门控
---------------
词表 ≥ 100 词 + 500 句人工标注 precision ≥ 0.80; 当前是 v0.1.6 双门控
(future 68 词 + time 53 词 = 121 词; fix(omni-g-numlex-03, 2026-06-11) 自
v0.1.5 删 10 个非未来指向词, 见该词表 _meta 变更披露).

数据源 (2026-06-18 统一)
-----------------------
双门控词表已从本文件内联 frozenset 外置到 ``config/tone_dicts.json`` 顶层条目
``forward_looking_statements`` (future_words / time_words 两数组; 单一事实源,
与 7 部情感/非情感词典同居一文件), 本模块 import 时加载为模块级 ``_FUTURE_WORDS`` /
``_TIME_FUTURE_MARKERS`` frozenset; 词表逐字不变 (3 个 frac_fls panel 列结果不变).
⚠ 加载契约: 词表在 **import 时**一次性读 tone_dicts.json 并绑定为模块级 frozenset
(非 lru_cache, import 后 monkeypatch _FLS_DICT_PATH 不再生效); 文件/条目缺失时**静默降级
空集** (frac_fls→0/nan)。因 tone_dicts.json 是项目核心必备文件、且原内联 frozenset 本就
无缺失态, 此降级仅为防御。需热加载/可 patch 时改 _load_fls_wordlists 为 lazy lru_cache。
"""

from __future__ import annotations

import json
from pathlib import Path

import jieba

from news_process.core.text.cn_text_utils import cn_split_sentence

# P-038 修复 (v3.7.1): single-char "望"/"盼"/"将" substring 匹配会命中
# "希望"/"绝望"/"瞭望"/"将其"/"将该" 等非 forward-looking 上下文. 改用
# jieba.cut() 精确 token 匹配, 避免 substring false positives.
# Performance: jieba 单例 cache, ~0.1ms/sentence.

# ── FLS 双门控词表 (v0.1.6, future 68 + time 53; 2026-06-18 外置进 config/tone_dicts.json) ──
# 词表已从本文件内联 frozenset 外置到 config/tone_dicts.json::forward_looking_statements
# (单一事实源, future_words / time_words 两数组), 本模块 import 时加载为模块级 frozenset。
# 历史/口径/变更披露 (P-038 jieba 精确匹配 + omni-g-numlex-03 v0.1.5→v0.1.6 删进行体动词/
# 裸时距/当期词) 见该条目 _meta; 词表成员由 tests/test_omni_fix_numlex.py 锁定。
_FLS_DICT_PATH = (
    Path(__file__).resolve().parents[2] / 'config' / 'tone_dicts.json'
)
_FLS_DICT_KEY = 'forward_looking_statements'


def _load_fls_wordlists() -> tuple[frozenset[str], frozenset[str]]:
    """从 config/tone_dicts.json::forward_looking_statements 读双门控词表.

    Returns:
        (future_words, time_words) 两个 frozenset; 文件/条目缺失 → 两个空集 (优雅降级).
    """
    if not _FLS_DICT_PATH.exists():
        return frozenset(), frozenset()
    try:
        with open(_FLS_DICT_PATH, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return frozenset(), frozenset()
    entry = raw.get(_FLS_DICT_KEY, {}) if isinstance(raw, dict) else {}
    if not isinstance(entry, dict):
        entry = {}
    return (
        frozenset(entry.get('future_words', []) or []),
        frozenset(entry.get('time_words', []) or []),
    )


_FUTURE_WORDS, _TIME_FUTURE_MARKERS = _load_fls_wordlists()


def _is_fls_sentence(sentence: str) -> bool:
    """双门控判定: 句中同时含 future 词与 time 词.

    P-038 修复 (v3.7.1): 改 jieba 精确 token 匹配, 避免单字 "望/盼/将"
    substring 误命中 "希望/绝望/瞭望/将其/将该" 等非 forward-looking 上下文.
    """
    if not sentence:
        return False
    tokens = set(jieba.cut(sentence))
    has_future = bool(tokens & _FUTURE_WORDS)
    has_time = bool(tokens & _TIME_FUTURE_MARKERS)
    # fix(forward-looking-jieba, metric-audit 2026-06-10): jieba 默认词典常把多字标记切碎
    # (如 '下一财年'→下/一/财年, '中长期目标'→中长期/目标), 其成分若不在词集 → 整词漏判。
    # 对 **≥3 字** 标记补 substring 命中 (纯加性: 只把门控置 True, 不移除任何 token 命中,
    # 故不会像 add_word 那样反而拆掉 '未来三年' 的 '未来' future token; 单/双字仍仅 token 匹配
    # 以保 P-038 精度 — 单字 substring 误判风险高)。空格统一剥除以兼容 '到 2030' 类标记。
    # 白话: jieba 有时会把"下一财年"这类长词切成碎片, 碎片对不上词表就漏判。
    # 补救办法是: 只对 3 字以上的词表词, 再直接在原句里找一遍字面子串;
    # 这只会"多认出"前瞻句, 不会把已认出的取消, 而 1-2 字短词仍走精确分词匹配以防误伤。
    _s = sentence.replace(' ', '')
    if not has_future:
        has_future = any(len(w) >= 3 and w.replace(' ', '') in _s for w in _FUTURE_WORDS)
    if not has_time:
        has_time = any(len(w) >= 3 and w.replace(' ', '') in _s for w in _TIME_FUTURE_MARKERS)
    return has_future and has_time


def compute_fls_for_text(text: str) -> dict[str, float]:
    """单文本 FLS 比例; 仿 v3.5.1 ``_compute_clarity_for_text`` 接口.

    Args:
        text: 待分析的中文文本.

    Returns:
        {
            'n_sentences': int,
            'n_fls_sentences': int,
            'frac_fls': float | nan,
        }

    Examples:
        >>> r = compute_fls_for_text("银行业务规模达 100 亿。计划未来三年达 500 亿。")
        >>> r['n_sentences']
        2
        >>> r['n_fls_sentences']
        1
        >>> r['frac_fls']
        0.5
    """
    if not text or not text.strip():
        return {
            'n_sentences': 0,
            'n_fls_sentences': 0,
            'frac_fls': float('nan'),
        }
    sents = cn_split_sentence(text)
    n = len(sents)
    if n == 0:
        return {
            'n_sentences': 0,
            'n_fls_sentences': 0,
            'frac_fls': float('nan'),
        }
    fls_n = sum(1 for s in sents if _is_fls_sentence(s))
    return {
        'n_sentences': n,
        'n_fls_sentences': fls_n,
        'frac_fls': fls_n / n,
    }


def get_panel_columns(suffix: str) -> list[str]:
    """返回 panel 应追加的 1 列名 (按指定后缀; 三轨各 1 列, 共 3 列, v3.9.0 +ss).

    suffix-parameterized → 本函数 track-agnostic, 调用方传 '_ss' 即得同句共现轨列名。

    Args:
        suffix: '_full' / '_ctx' / '_ss' (ss = 银行+金科同句共现轨).

    Returns:
        [f'frac_fls{suffix}']
    """
    return [f'frac_fls{suffix}']


__all__ = [
    '_FUTURE_WORDS',
    '_TIME_FUTURE_MARKERS',
    'compute_fls_for_text',
    'get_panel_columns',
]
