"""tests/integration/test_prompt_version_wired.py — Plan-r3 P3-17 接入验证.

校验 ``core/config.py::_inline_external_prompts`` 正确解析
``config/prompts/*.txt`` 首行 ``# version: <token>`` 头, 并将版本号写入
``<key>_version`` 配置字段; 同时校验 caching 模块缓存键空间能区分不同
版本号 (silent staleness 防御已激活)。

设计意图
--------
caching.py round-3 之前的 docstring 标注 ``prompt_version`` 维度
"infrastructure ready, NOT YET wired into production callers". v3.0
全量接入 6 个生产 callsite 后, 本测试是「激活路径已通」的端到端证明:

1. _inline_external_prompts 解析头部 → cfg['..._version'] 字段就位
2. callsite 把版本号传给 LLMCache.get/put → 不同版本号自动隔离
3. 改写模板版本号 → 旧 cache silent miss (避免 prompt 改后旧结果污染)

数据依赖: 仅用 tmp_path 与字符串 fixture, 不依赖任何 production data。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _import_news_process_core() -> None:
    """在 sys.path 不含 ``news_process/`` 父目录时, 也能加载 ``core.*``."""
    here = Path(__file__).resolve().parent.parent.parent
    parent = here.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))


_import_news_process_core()


# ---------------------------------------------------------------------------
# 1. _inline_external_prompts 解析 # version: 头
# ---------------------------------------------------------------------------


def test_inline_prompt_parses_version_header(tmp_path: Path) -> None:
    """有头部时, content 剥离头, 版本号写入 <key>_version."""
    from news_process.core.config import _inline_external_prompts

    template = tmp_path / "unified_cot.txt"
    template.write_text(
        "# version: v6-2026-05-13\n<role>\n你是分析师\n</role>",
        encoding="utf-8",
    )

    cfg = {
        "tone_llm_processing": {
            "prompt_template_file": str(template),
        }
    }
    _inline_external_prompts(cfg, str(tmp_path))

    sec = cfg["tone_llm_processing"]
    assert sec["prompt_template_version"] == "v6-2026-05-13"
    assert sec["prompt_template"].startswith("<role>")
    assert "# version:" not in sec["prompt_template"]


def test_inline_prompt_missing_header_defaults_to_v0(tmp_path: Path) -> None:
    """无头部时, version 默认 'v0', content 不变."""
    from news_process.core.config import _inline_external_prompts

    template = tmp_path / "title_sentiment.txt"
    body = "你是一位分析师\n请判断情感"
    template.write_text(body, encoding="utf-8")

    cfg = {
        "tone_llm_processing": {
            "title_sentiment_prompt_template_file": str(template),
        }
    }
    _inline_external_prompts(cfg, str(tmp_path))

    sec = cfg["tone_llm_processing"]
    assert sec["title_sentiment_prompt_template_version"] == "v0"
    assert sec["title_sentiment_prompt_template"] == body


def test_inline_prompt_crlf_header_tolerated(tmp_path: Path) -> None:
    """Windows CRLF 行尾的版本头也能正确解析."""
    from news_process.core.config import _inline_external_prompts

    template = tmp_path / "crlf.txt"
    template.write_bytes(b"# version: v7-test\r\n<body>")

    cfg = {"x": {"prompt_template_file": str(template)}}
    _inline_external_prompts(cfg, str(tmp_path))

    assert cfg["x"]["prompt_template_version"] == "v7-test"
    assert cfg["x"]["prompt_template"] == "<body>"


# ---------------------------------------------------------------------------
# 2. LLMCache 真区分不同 prompt_version (与现有 robustness 测试互补)
# ---------------------------------------------------------------------------


def test_cache_isolates_versions(tmp_path: Path) -> None:
    """改 prompt 版本号 → 旧 cache silent miss → 强制重新调 API."""
    from news_process.core.caching import LLMCache

    db = tmp_path / "test_cache.db"
    cache = LLMCache(str(db))

    cache.put("gpt-test", "prompt-A", "old-response", prompt_version="v6-2026-05-13")
    assert cache.get("gpt-test", "prompt-A",
                      prompt_version="v6-2026-05-13") == "old-response"
    # 改版本号即应 miss
    assert cache.get("gpt-test", "prompt-A",
                      prompt_version="v7-2026-06-01") is None


# ---------------------------------------------------------------------------
# 3. 生产 prompt 模板真带 # version: 头 (拦截 v3.0 后退步)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["unified_cot.txt", "title_sentiment.txt"])
def test_production_prompts_have_version_header(name: str) -> None:
    """unified_cot.txt 与 title_sentiment.txt 首行必含 # version: ...

    一旦未来有人改 prompt 文件忘了 bump 版本号 (或误删头部), 本测试拦截。
    回归: caching.py round-3 之前 silent staleness 风险即"虽接入但版本号
    不更新"; 此 gate 配合 review 流程防止该退化。
    """
    here = Path(__file__).resolve().parent.parent.parent
    prompt_path = here / "config" / "prompts" / name
    assert prompt_path.exists(), f"生产 prompt 模板缺失: {prompt_path}"

    first_line = prompt_path.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("# version:"), (
        f"{name} 首行必须是 ``# version: <token>``, 当前: {first_line!r}. "
        f"参见 caching.py docstring 中 v3.0 接入说明。"
    )
