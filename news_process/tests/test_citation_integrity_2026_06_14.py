"""引文完整性 source-text lock 测试 (审计 2026-06-14 CIT-1 / DI-7)。

这些是 *回归锁* — 断言已订正的误引字符串不会悄悄回归到源码注释/docstring。
本仓库有 fabricated/miscited DOI 与作者的历史 (见 memory citation-corrections),
故对两处已修的硬误引加字节级守卫:

  CIT-1  encode.py            : Hillert-Jacobs-Müller (2014) 原误标 "Journal of Finance,
                                69(5), 2095-2143" → 实为 RFS 27(12):3467-3501。
  DI-7   article_staleness.py : "Text as Data" (2019 JEL) 第二作者原误作 Shapiro
                                → 实为 Kelly (Gentzkow, Kelly & Taddy)。

按 *文件路径* 读源码 (不 import 模块 — 避免裸环境缺 faiss/datasketch 导致 collection error)。
纯文本断言, 不触发任何 stage / golden 重生 / 付费调用。
"""
from __future__ import annotations

from pathlib import Path

import pytest

# tests/ 在 news_process/ 下 → parent.parent = 包根 news_process/
_PKG_ROOT = Path(__file__).resolve().parent.parent
_ENCODE = _PKG_ROOT / "pipeline" / "panel" / "encode.py"
_STALENESS = _PKG_ROOT / "pipeline" / "text" / "article_staleness.py"


def test_hillert_not_miscited_as_jf_in_encode() -> None:
    """CIT-1: encode.py 不得把 Hillert 2014 标成 JF 69(5)/2095-2143。"""
    src = _ENCODE.read_text(encoding="utf-8")
    assert "Journal of Finance, 69(5), 2095-2143" not in src, (
        "CIT-1 回归: Hillert 2014 又被误标为 'Journal of Finance, 69(5), 2095-2143' "
        "(正确为 The Review of Financial Studies, 27(12), 3467-3501)"
    )


def test_hillert_correct_rfs_anchor_present() -> None:
    """CIT-1: 正确的 RFS 27(12) 锚点必须在场 (防整段被误删)。"""
    src = _ENCODE.read_text(encoding="utf-8")
    assert "Hillert" in src
    assert "27(12), 3467-3501" in src, "Hillert 2014 的正确 RFS 卷期页缺失"


def test_text_as_data_authorship_correct_in_staleness() -> None:
    """DI-7: 'Text as data' 第二作者必须是 Kelly, 不得是 Shapiro。"""
    src = _STALENESS.read_text(encoding="utf-8")
    assert "Shapiro, J. M., & Taddy" not in src, (
        "DI-7 回归: 'Text as data' 第二作者又被误作 Shapiro (正确为 Kelly)"
    )
    assert "Gentzkow, M., Kelly, B., & Taddy" in src, (
        "'Text as data' 正确署名 (Gentzkow, Kelly & Taddy) 缺失"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
