"""W3: PEER_PROMPT frozen-hash 护栏 (内联 prompt 常量须配 frozen-hash 单测)。

见 core/caching.py docstring §5-D。改 PEER_PROMPT 正文 → 本测试红 → 强制同 diff bump
PEER_PROMPT_VERSION (让旧 _llm_cache.db silent miss) 并重算哈希。EOL 归一 (.replace) 防
Windows CRLF 跨 checkout / CI 误红 (llm_peer_iv.py 在 Windows 仓库, .py 未标 binary)。
"""
import hashlib

from news_process.pipeline.panel.llm_peer_iv import (
    PEER_PROMPT,
    PEER_PROMPT_SHA256,
    PEER_PROMPT_VERSION,
)


def test_peer_prompt_frozen():
    actual = hashlib.sha256(PEER_PROMPT.replace("\r\n", "\n").encode("utf-8")).hexdigest()
    assert actual == PEER_PROMPT_SHA256, (
        f"PEER_PROMPT 正文已变 (actual={actual!r})。若是有意修改, 必须同 diff: "
        f"(1) bump PEER_PROMPT_VERSION (现 {PEER_PROMPT_VERSION!r}) 让旧 _llm_cache.db silent miss; "
        f"(2) 把 llm_peer_iv.PEER_PROMPT_SHA256 改为上面的 actual。"
    )


def test_peer_prompt_placeholders_intact():
    # PEER_PROMPT.format(bank_name=, year=, numbered_sentences=) 依赖这 3 个占位符。
    for ph in ("{year}", "{bank_name}", "{numbered_sentences}"):
        assert ph in PEER_PROMPT, f"PEER_PROMPT 缺占位符 {ph} → .format 会 KeyError"
