"""测试 majority_vote_categorical 统一分类多数投票函数。

覆盖：
- 正常多数（含 binary + 3-class）
- 平局策略（undefined / conservative；2-way 与 3-way）
- 空票回退
- 入口 fail-fast 校验（H3）
- majority_vote_sentiment wrapper 向后兼容
"""

import pytest

from news_process.pipeline.sentiment.tone_llms import (
    majority_vote_categorical,
    majority_vote_sentiment,
)

# ============================================================================
# 1. 正常多数（无平局）
# ============================================================================


@pytest.mark.parametrize(
    "votes,expected",
    [
        (["A", "A", "B"], "A"),                            # binary, clear majority
        (["正面", "正面", "负面"], "正面"),                 # 3-class, clear majority
        (["底层技术", "应用场景", "应用场景"], "应用场景"),  # binary categorical
        (["A"], "A"),                                       # single vote
        (["A", "A", "A"], "A"),                            # all same
    ],
)
def test_normal_majority(votes, expected):
    """无平局时返回票数最多者，与 tie_strategy 无关。"""
    assert majority_vote_categorical(
        votes, tie_strategy="undefined"
    ) == expected
    assert majority_vote_categorical(
        votes, tie_strategy="conservative", tie_default="DUMMY"
    ) == expected


# ============================================================================
# 2. 平局 + 'undefined' 策略（H1 覆盖 2-way + 3-way tie）
# ============================================================================


@pytest.mark.parametrize(
    "votes",
    [
        ["正面", "负面"],            # 2-way tie
        ["A", "B"],                  # 2-way binary
        ["正面", "中性", "负面"],    # 3-way tie（H1 新增覆盖）
        ["A", "B", "C"],             # 3-way generic（H1 新增覆盖）
    ],
)
def test_undefined_tie_returns_none(votes):
    """平局 + 'undefined' → None（适用 sentiment 严格未定义语义）。"""
    assert majority_vote_categorical(
        votes, tie_strategy="undefined"
    ) is None


# ============================================================================
# 3. 平局 + 'conservative' 策略
# ============================================================================


@pytest.mark.parametrize(
    "votes,tie_default,expected",
    [
        (["底层技术", "应用场景"], "应用场景", "应用场景"),       # 2-way binary, innovation_locus (v7)
        (["实质性", "象征性"], "象征性", "象征性"),               # 2-way binary, innovation_substantiveness (v7; value 是翻译层后值域)
        (["A", "B", "C"], "DEFAULT", "DEFAULT"),                # 3-way（H1 覆盖）
        (["正面", "负面"], "中性", "中性"),                      # sentiment 历史 'neutral' 等效
    ],
)
def test_conservative_tie_returns_default(votes, tie_default, expected):
    """平局 + 'conservative' → tie_default（MAP under uniform prior）。"""
    assert majority_vote_categorical(
        votes, tie_strategy="conservative", tie_default=tie_default
    ) == expected


# ============================================================================
# 4. 空票 + empty_fallback
# ============================================================================


@pytest.mark.parametrize(
    "fallback",
    [None, "FALLBACK_STRING", 0, "应用场景"],
)
def test_empty_votes_returns_fallback(fallback):
    """votes 为空 → empty_fallback；任意类型（含 None / str / int）。"""
    # 'undefined' 策略不需 tie_default
    result_undefined = majority_vote_categorical(
        [], tie_strategy="undefined", empty_fallback=fallback
    )
    assert result_undefined == fallback  # None == None 为 True，覆盖所有取值
    # 'conservative' 策略也走 empty_fallback 而非 tie_default（因未触发平局）
    result_conservative = majority_vote_categorical(
        [],
        tie_strategy="conservative",
        tie_default="UNUSED",
        empty_fallback=fallback,
    )
    assert result_conservative == fallback


def test_empty_votes_default_fallback_is_none():
    """未传 empty_fallback 时空票返回 None。"""
    assert majority_vote_categorical(
        [], tie_strategy="undefined"
    ) is None
    assert majority_vote_categorical(
        [], tie_strategy="conservative", tie_default="X"
    ) is None


# ============================================================================
# 5. 入口 fail-fast 校验（H3）
# ============================================================================


def test_invalid_tie_strategy_raises_at_entry():
    """未知 tie_strategy 必须在函数入口立即抛 ValueError（fail-fast）。"""
    with pytest.raises(ValueError, match="Unknown tie_strategy"):
        majority_vote_categorical(["A", "B"], tie_strategy="garbage")
    # 即使 votes 为空（永不会平局），也应在入口被拦截
    with pytest.raises(ValueError, match="Unknown tie_strategy"):
        majority_vote_categorical([], tie_strategy="bogus")


def test_conservative_missing_tie_default_raises_at_entry():
    """tie_strategy='conservative' 但未传 tie_default → ValueError（fail-fast）。"""
    with pytest.raises(ValueError, match="requires tie_default"):
        majority_vote_categorical(["A", "B"], tie_strategy="conservative")
    # 即使 votes 为空也应在入口拦截（防御未来 misuse）
    with pytest.raises(ValueError, match="requires tie_default"):
        majority_vote_categorical([], tie_strategy="conservative")


# ============================================================================
# 6. majority_vote_sentiment wrapper 向后兼容
# ============================================================================


@pytest.mark.parametrize(
    "sents,tie_strategy,expected",
    [
        # 默认 'undefined' 策略
        ([], "undefined", None),
        (["正面"], "undefined", "正面"),
        (["正面", "正面", "负面"], "undefined", "正面"),
        (["正面", "负面"], "undefined", None),                # 2-way tie
        (["正面", "中性", "负面"], "undefined", None),        # 3-way tie
        # 'neutral' 策略（历史 robustness 备选）
        (["正面", "负面"], "neutral", "中性"),                # 2-way tie → 中性
        (["正面", "中性", "负面"], "neutral", "中性"),        # 3-way tie → 中性
        (["正面", "正面", "负面"], "neutral", "正面"),         # 无平局，策略不影响
        # 未知策略沿用 'undefined' 安全回退（历史行为）
        (["正面", "负面"], "garbage", None),
    ],
)
def test_sentiment_wrapper_backward_compat(sents, tie_strategy, expected):
    """majority_vote_sentiment wrapper 与重构前行为 byte-level 等价。"""
    assert majority_vote_sentiment(sents, tie_strategy=tie_strategy) == expected


def test_sentiment_wrapper_default_strategy_is_undefined():
    """默认 tie_strategy='undefined'（v6/F2 修订后语义）。"""
    # 默认调用应与显式传 'undefined' 等价
    assert majority_vote_sentiment(["正面", "负面"]) is None
    assert majority_vote_sentiment(["正面", "负面"]) == \
        majority_vote_sentiment(["正面", "负面"], tie_strategy="undefined")
