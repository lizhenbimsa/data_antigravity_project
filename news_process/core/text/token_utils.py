"""news_process.core.text.token_utils — tiktoken 文本切分工具。

统一提供 cl100k_base 编码器 (OpenAI text-embedding-3-small 底层编码器) 的
token 计数、截断、分段函数,供 Stage 15 (policy_alignment) 与
Stage 27 (benefit_society) 等需要精确 token 切分的场景复用。

设计动机
--------
原实现散落在 ``pipeline/filtering/policy_alignment.py`` 与
``pipeline/features/benefit_society.py``, 两处完全同名同签名, token 上限
常量也各自硬编码, 变更成本 ×2。

常量
----
- ``MAX_TOKENS_PER_INPUT`` 默认 8191 (OpenAI text-embedding-3-small 上限)
- ``MAX_TOKENS_PER_REQUEST`` 默认 250_000 (单次请求经验上限)

调用方可通过参数覆盖这些默认值, 模块级常量仅作 fallback。
"""

from __future__ import annotations

import tiktoken

# cl100k_base 是 text-embedding-3-small 的底层编码器
_ENCODING = tiktoken.get_encoding("cl100k_base")

# OpenAI text-embedding-3-small 的硬性约束
MAX_TOKENS_PER_INPUT = 8191
MAX_TOKENS_PER_REQUEST = 250_000


def get_encoding():
    """返回模块级单例编码器, 避免重复实例化。"""
    return _ENCODING


def count_tokens(text: str) -> int:
    """精确计算文本的 token 数 (cl100k_base 编码器)。"""
    return len(_ENCODING.encode(text))


def truncate_to_max_tokens(text: str, max_tokens: int = MAX_TOKENS_PER_INPUT) -> str:
    """将文本精确截断至不超过 max_tokens 个 token。

    使用 tiktoken 编码→截断→解码三步法, 确保结果严格不超限。
    """
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _ENCODING.decode(tokens[:max_tokens])


def split_into_chunks(text: str, max_tokens: int = MAX_TOKENS_PER_INPUT) -> list[str]:
    """将超长文本按 token 粒度切分为多个不重叠分段。

    朴素分段 (naive / independent chunking):
    对超过 Embedding 模型单条上限的长文本, 先按固定 token 数切分为 K 个
    不重叠段, 各段独立嵌入后均值池化 (无跨段上下文)。
    """
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return [text]
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunks.append(_ENCODING.decode(tokens[i:i + max_tokens]))
    return chunks


__all__ = [
    "MAX_TOKENS_PER_INPUT",
    "MAX_TOKENS_PER_REQUEST",
    "get_encoding",
    "count_tokens",
    "truncate_to_max_tokens",
    "split_into_chunks",
]
