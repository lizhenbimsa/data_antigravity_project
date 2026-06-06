"""tests/test_num_intensity_word.py — word-level 数字密度 (§4.3 替代版) 单测.

2026-06-05 新增: compute_num_intensity_word 兑现 numerical_intensity 模块 docstring
§4.3 "同时报 word-level 替代版" 的承诺。分母从句数改为 jieba 词数, 对中文句读
sparse 互为稳健性。与句级版**共享分子** n_numeric, 故仅分母不同。
"""
from __future__ import annotations

import math

import pandas as pd

from news_process.pipeline.sentiment.numerical_intensity import (
    _cn2arab,
    _count_numerical_tokens,
    _count_word_tokens,
    compute_num_intensity,
    compute_num_intensity_word,
    enrich_with_num_intensity_dual_track,
)


def test_word_empty_and_sentinel_return_nan():
    """空文本 / pandas 字符串化 NaN 哨兵 → nan (与句级版同款保护)."""
    assert math.isnan(compute_num_intensity_word(""))
    assert math.isnan(compute_num_intensity_word("   "))
    for sentinel in ("nan", "NaN", "None", "<NA>", "NaT"):
        assert math.isnan(compute_num_intensity_word(sentinel))


def test_word_no_numbers_returns_zero():
    """有词无数字 → 0.0 (分子 0, 分母 > 0)."""
    txt = "本行将持续推进数字化转型服务实体经济"
    assert compute_num_intensity_word(txt) == 0.0


def test_word_shares_numerator_with_sentence_version():
    """词级与句级共享分子 n_numeric: word = n_numeric / n_words 应自洽."""
    txt = "本行2023年净利润增长百分之三十不良率为1.5%全年营收两千万元"
    n_num, _ = _count_numerical_tokens(_cn2arab(txt))
    n_words = _count_word_tokens(txt)
    expected = round(n_num / max(n_words, 1), 6)
    assert compute_num_intensity_word(txt) == expected
    assert n_num > 0  # 该样例确含数字, 防回归把分子算丢


def test_word_denominator_is_jieba_words_not_sentences():
    """单长句多数字: 句级分母≈1 → 句级值远大于词级值 (体现分母差异的核心动机)."""
    # 单句 (无句末标点) 多个数字; 句级 n_sentences=1, 词级分母=全部词数
    txt = "净利润100亿营收200亿总资产3000亿不良率1点5"
    sent_val = compute_num_intensity(txt)
    word_val = compute_num_intensity_word(txt)
    assert sent_val > word_val  # 句数分母被低估 → 句级系统性偏高
    assert word_val > 0.0


def test_enrich_emits_four_columns_dual_track():
    """enrich 产出句级 2 列 + 词级 2 列 = 4 列, 且 ctx 缺失时优雅回退."""
    df = pd.DataFrame({
        "内容": ["营收两千万元增长百分之三十。", "无数字的纯文本内容。"],
        "content_ctx": ["营收两千万元。", "无数字。"],
    })
    out = enrich_with_num_intensity_dual_track(df)
    for col in (
        "num_intensity_full", "num_intensity_ctx",
        "num_intensity_word_full", "num_intensity_word_ctx",
    ):
        assert col in out.columns
    # 词级第二行 (无数字) 应为 0.0
    assert out["num_intensity_word_full"].iloc[1] == 0.0


def test_count_word_tokens_matches_jieba_nonblank():
    """_count_word_tokens = jieba 非空白 token 数 (与项目 n_tokens 口径一致)."""
    import jieba
    txt = "商业银行 数字化 转型"
    expected = sum(1 for t in jieba.cut(txt) if t.strip())
    assert _count_word_tokens(txt) == expected
    assert _count_word_tokens("") == 0
