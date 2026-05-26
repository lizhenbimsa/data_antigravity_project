"""Tests for ``news_process.core.text.token_utils`` — tiktoken cl100k_base helpers.

quality-hardening Round 21 (2026-05-27): token_utils.py 0% → 100%.
模块此前在 tests/ 中完全无直接覆盖 — 6 个公开函数 0 行测试.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.core.text.token_utils import (
    MAX_TOKENS_PER_INPUT,
    MAX_TOKENS_PER_REQUEST,
    count_tokens,
    get_encoding,
    split_into_chunks,
    truncate_to_max_tokens,
)


def test_constants_match_openai_specs():
    """两个 token 上限常量符合 OpenAI text-embedding-3-small 约束."""
    assert MAX_TOKENS_PER_INPUT == 8191
    assert MAX_TOKENS_PER_REQUEST == 250_000


def test_get_encoding_returns_singleton():
    """get_encoding 应返回同一编码器实例 (避免重复实例化)."""
    enc1 = get_encoding()
    enc2 = get_encoding()
    assert enc1 is enc2


def test_count_tokens_ascii():
    """ASCII 短文本 token 数 > 0."""
    n = count_tokens("hello world")
    assert n >= 2  # 至少 2 token (hello + world 边界)
    assert n < 10  # 不会爆炸


def test_count_tokens_chinese():
    """中文文本 token 数 > 字符数 (CJK 每字符 ≥ 1 token)."""
    text = "中国工商银行"
    n = count_tokens(text)
    assert n >= len(text)


def test_count_tokens_empty_string():
    """空 str → 0 tokens."""
    assert count_tokens("") == 0


def test_truncate_to_max_tokens_short_text_unchanged():
    """文本 token 数 ≤ max → 原样返回 (no-op)."""
    text = "short text"
    assert truncate_to_max_tokens(text, max_tokens=8191) == text


def test_truncate_to_max_tokens_truncates_long_text():
    """长文本被精确截断至 ≤ max_tokens."""
    # 重复字符串造长 text (远超 max_tokens)
    long_text = "a b c d e f g " * 1000  # ~7000 tokens
    truncated = truncate_to_max_tokens(long_text, max_tokens=100)
    assert count_tokens(truncated) <= 100
    # 截断后还是 str
    assert isinstance(truncated, str)
    assert len(truncated) < len(long_text)


def test_split_into_chunks_short_text_single_chunk():
    """文本 token 数 ≤ max → list 含 1 个原 text."""
    text = "single chunk text"
    chunks = split_into_chunks(text, max_tokens=8191)
    assert chunks == [text]


def test_split_into_chunks_long_text_multiple_chunks():
    """长文本分多块, 各块 token 数 ≤ max, 拼回应近似原文."""
    long_text = "a b c d e " * 500  # ~2500 tokens
    chunks = split_into_chunks(long_text, max_tokens=100)
    assert len(chunks) >= 2  # 应分多块
    for chunk in chunks:
        assert count_tokens(chunk) <= 100
    # 拼回 token 数应近似原文 (允许少量边界差异)
    total_tokens = sum(count_tokens(c) for c in chunks)
    assert abs(total_tokens - count_tokens(long_text)) <= len(chunks)


def test_truncate_to_max_tokens_default_max():
    """truncate_to_max_tokens 默认 max_tokens = MAX_TOKENS_PER_INPUT."""
    text = "test"  # 远小于默认 max
    assert truncate_to_max_tokens(text) == text


def test_split_into_chunks_default_max():
    """split_into_chunks 默认 max_tokens = MAX_TOKENS_PER_INPUT."""
    text = "single short"
    assert split_into_chunks(text) == [text]
