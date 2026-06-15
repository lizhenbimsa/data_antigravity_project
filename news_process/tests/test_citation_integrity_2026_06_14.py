"""引文完整性 source-text lock 测试 (审计 2026-06-14 CIT-1 / DI-7)。

这些是 *回归锁* — 断言已订正的误引字符串不会悄悄回归到源码注释/docstring。
本仓库有 fabricated/miscited DOI 与作者的历史 (见 memory citation-corrections),
故对两处已修的硬误引加字节级守卫:

  CIT-1  encode.py            : Hillert-Jacobs-Müller (2014) 原误标 "Journal of Finance,
                                69(5), 2095-2143" → 实为 RFS 27(12):3467-3501。
  DI-7   article_staleness.py : "Text as Data" (2019 JEL) 第二作者原误作 Shapiro
                                → 实为 Kelly (Gentzkow, Kelly & Taddy)。
  CITE-1 run_paper.py /        : Cookson & Niessner (2020) 原误标 RFS (+ 杜撰卷页) →
         instantiate_paper_     实为 JF 75(1):173-228, DOI 10.1111/jofi.12852
         stata.py / replication (PROJECT_REAUDIT_TOPTIER_T18 2026-06-14)。
         README.md

按 *文件路径* 读源码 (不 import 模块 — 避免裸环境缺 faiss/datasketch 导致 collection error)。
纯文本断言, 不触发任何 stage / golden 重生 / 付费调用。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# tests/ 在 news_process/ 下 → parent.parent = 包根 news_process/
_PKG_ROOT = Path(__file__).resolve().parent.parent
_ENCODE = _PKG_ROOT / "pipeline" / "panel" / "encode.py"
_STALENESS = _PKG_ROOT / "pipeline" / "text" / "article_staleness.py"
# CITE-1: Cookson-Niessner 误标 RFS 的 dev 注释/元数据/replication 载体 (服务第10篇 provisional)
_COOKSON_CITE_FILES = [
    _PKG_ROOT / "run_paper.py",
    _PKG_ROOT / "scripts" / "instantiate_paper_stata.py",
    _PKG_ROOT / "papers" / "bank_media_disagreement" / "replication" / "README.md",
    # PROJECT_REAUDIT_TOPTIER_T18 2026-06-14: spec:44 是最严重的一处 (误标 RFS + 杜撰卷页
    # "33:4327-4373"); 该处此前无任何测试守护。纳入扫描 + 杜撰卷页绝迹断言 (见下方专测)。
    _PKG_ROOT / "papers" / "bank_media_disagreement" / "paper_spec.yaml",
]


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


@pytest.mark.parametrize("path", _COOKSON_CITE_FILES, ids=lambda p: p.name)
def test_cookson_niessner_not_miscited_as_rfs(path: Path) -> None:
    """CITE-1: Cookson-Niessner (2020) 不得标成 RFS (正确为 JF)。"""
    if not path.exists():
        pytest.skip(f"{path.name} 不在盘 (provisional 复现包未实例化)")
    src = path.read_text(encoding="utf-8")
    # 仅当源文件确实提及 Cookson 时才核验 (避免对无关文件误判)
    if "Cookson" not in src:
        pytest.skip(f"{path.name} 未提及 Cookson-Niessner")
    # 逐处出现都不得紧跟 RFS (允许中间有作者/年份/DOI), 避免"Cookson ... RFS"误标回潮
    offenders = re.findall(r"Cookson[^\n]{0,60}?RFS", src)
    assert not offenders, (
        f"CITE-1 回归: {path.name} 把 Cookson-Niessner 标为 RFS "
        f"(正确为 JF 75(1):173-228, DOI 10.1111/jofi.12852): {offenders}"
    )


def test_cookson_niessner_jf_anchor_present_in_instantiator() -> None:
    """CITE-1: 实例化器须携带正确 JF + DOI 锚点 (防整段被误删)。"""
    inst = _PKG_ROOT / "scripts" / "instantiate_paper_stata.py"
    src = inst.read_text(encoding="utf-8")
    assert "Cookson-Niessner (2020) JF" in src
    assert "10.1111/jofi.12852" in src, "Cookson-Niessner 正确 DOI 缺失"


def test_cookson_niessner_fabricated_volume_absent_in_spec() -> None:
    """CITE-1: disagreement spec 不得残留杜撰卷页 '33:4327-4373' (原 spec:44 误标)。"""
    spec = (
        _PKG_ROOT / "papers" / "bank_media_disagreement" / "paper_spec.yaml"
    )
    src = spec.read_text(encoding="utf-8")
    assert "4327-4373" not in src, (
        "CITE-1 回归: paper_spec.yaml 又出现 Cookson-Niessner 杜撰卷页 '33:4327-4373' "
        "(正确为 JF 75(1):173-228, DOI 10.1111/jofi.12852)"
    )
    # 正确 JF 锚点须在场 (防整段被误删)
    assert "75(1):173-228" in src, "Cookson-Niessner 正确 JF 卷期页缺失"
    assert "10.1111/jofi.12852" in src, "Cookson-Niessner 正确 DOI 缺失"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
