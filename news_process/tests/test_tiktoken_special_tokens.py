"""F2 (2026-07-16) gate: tiktoken 特殊 token 毒丸防护。

缺陷: cl100k ``encode()``/``encode_batch()`` 默认 ``disallowed_special='all'`` —
语料中出现 "<|endoftext|>" 等特殊 token 字面量 (2023-2025 年 AI/大模型报道高发)
即抛 ValueError, 且发生在嵌入引擎的分批/重试/None→NaN 降级之前、无任何捕获 →
单篇毒丸文章崩掉整个嵌入消费阶段 (stage 16/25/26)。

修复: 全部 8 个裸调用点 (4 文件) 统一 ``disallowed_special=()`` — 特殊 token
字面量按普通文本 BPE。对不含特殊字面量的一切文本, 输出逐 token 不变 (字节等价,
T2 锚死); 缓存键为文本键, 零漂移。

计划: scripts/audit/FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN_2026-07-16.md §2-F2。
"""

# cl100k 特殊 token 字面量毒丸样本 (含正文夹带 / 开头 / 多枚混合)
POISON_TEXTS = [
    "正文<|endoftext|>结尾",
    "<|fim_prefix|>开头的报道",
    "解释 tokenizer 机制的报道原样引用 <|endofprompt|> 与 <|fim_suffix|> 字面量",
]


# ---------------------------------------------------------------- T1 毒丸不抛
class TestPoisonNoRaise:
    def test_token_utils_count_tokens(self):
        from news_process.core.text.token_utils import count_tokens
        for t in POISON_TEXTS:
            assert count_tokens(t) > 0

    def test_token_utils_truncate(self):
        from news_process.core.text.token_utils import truncate_to_max_tokens
        for t in POISON_TEXTS:
            out = truncate_to_max_tokens(t, max_tokens=5)
            assert isinstance(out, str) and out

    def test_token_utils_split_into_chunks(self):
        from news_process.core.text.token_utils import split_into_chunks
        for t in POISON_TEXTS:
            chunks = split_into_chunks(t, max_tokens=5)
            assert chunks and all(isinstance(c, str) for c in chunks)

    def test_embedding_engine_split(self):
        from news_process.pipeline.text.embedding_engine import split_text_for_embedding
        for t in POISON_TEXTS:
            chunks = split_text_for_embedding(t)
            assert chunks and all(isinstance(c, str) for c in chunks)

    def test_strategic_diff_split(self):
        from news_process.pipeline.features.strategic_diff import _split_text_for_embedding
        for t in POISON_TEXTS:
            chunks = _split_text_for_embedding(t)
            assert chunks and all(isinstance(c, str) for c in chunks)

    def test_policy_alignment_batch_count(self):
        from news_process.pipeline.filtering.policy_alignment import _count_tokens_batch
        counts = _count_tokens_batch(POISON_TEXTS)
        assert len(counts) == len(POISON_TEXTS) and all(n > 0 for n in counts)

    def test_policy_alignment_batch_equals_single(self):
        # encode_batch(disallowed_special=()) 与逐条 count_tokens 在毒丸上仍逐位等价
        from news_process.pipeline.filtering.policy_alignment import _count_tokens, _count_tokens_batch
        assert _count_tokens_batch(POISON_TEXTS) == [
            _count_tokens(t) for t in POISON_TEXTS]


# ------------------------------------------------- T2 无特殊字面量 → 逐 token 不变
def test_equivalence_on_normal_corpus():
    """字节等价锚: 对不含特殊 token 字面量的文本, disallowed_special=() 与默认
    编码输出逐 token 相同 → 现存语料的切块边界/token 计数/缓存语义零漂移。"""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    samples = [
        f"某银行发布金融科技战略公告第{i}号: 数字化转型、区块链与人工智能布局, "
        f"含标点、数字 {i * 37} 与英文 FinTech mixed 文本。"
        for i in range(100)
    ]
    for s in samples:
        assert enc.encode(s, disallowed_special=()) == enc.encode(s)


# ------------------------------------------------------------- T3 超长毒丸切块
def test_long_poison_chunking():
    from news_process.pipeline.text.embedding_engine import EMB_MAX_TOKENS, split_text_for_embedding
    long_poison = ("金融科技银行数字化转型" * 2000) + "<|endoftext|>" + ("区块链人工智能" * 2000)
    chunks = split_text_for_embedding(long_poison)
    assert len(chunks) >= 2  # 确已超限并切块
    from news_process.core.text.token_utils import count_tokens
    assert all(count_tokens(c) <= EMB_MAX_TOKENS for c in chunks)
