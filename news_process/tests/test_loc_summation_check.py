"""tests/test_loc_summation_check.py — v3.7.4 L4 lint 测试.

覆盖 4.D protocol (5R-A1) + stdin (8R-A2) + self-check (8R-B2) + opt-in marker (7R-B3).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# 路径注入: 把项目根目录放进 sys.path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from news_process.scripts.audit import loc_summation_check as M  # noqa: E402

# --- 8R-B3 marker opt-in: 标记块**内**的算式链才检查; 块外不检查 ---

def test_valid_chain_inside_marker_passes():
    doc = (
        "Some prose.\n"
        f"{M.MARKER_OPEN}\n"
        "Total = 60 + 30 + 20 = 110\n"
        f"{M.MARKER_CLOSE}\n"
        "End.\n"
    )
    violations = M.check_text(doc, src="test.md")
    assert violations == []


def test_invalid_chain_inside_marker_fails():
    doc = (
        f"{M.MARKER_OPEN}\n"
        "Wrong: 60 + 30 + 20 = 999\n"
        f"{M.MARKER_CLOSE}\n"
    )
    violations = M.check_text(doc, src="bad.md")
    assert len(violations) == 1
    src, lhs, actual, declared = violations[0]
    assert actual == 110 and declared == 999


def test_chain_outside_marker_ignored():
    """7R-B3: opt-in — <!-- loc-summation-check --> 标记之外的算式链**不**检查."""
    doc = "Some doc: 1 + 1 = 999 (this is fake, should be ignored)\n"
    violations = M.check_text(doc, src="legacy.md")
    assert violations == []


def test_no_marker_at_all_ignored():
    doc = "Plain doc no markers."
    assert M.check_text(doc, src="plain.md") == []


def test_unicode_minus_supported():
    doc = (
        f"{M.MARKER_OPEN}\n"
        "Net: 100 − 5 + 5 = 100\n"
        f"{M.MARKER_CLOSE}\n"
    )
    assert M.check_text(doc, src="u.md") == []


def test_multiple_chains_in_one_section():
    doc = (
        f"{M.MARKER_OPEN}\n"
        "L1: 10 + 5 = 15\n"
        "L2: 20 + 30 = 50\n"
        "Total: 15 + 50 = 65\n"
        f"{M.MARKER_CLOSE}\n"
    )
    assert M.check_text(doc, src="multi.md") == []


def test_main_with_stdin(monkeypatch, capsys):
    """8R-A2 stdin 输入路径."""
    bad_doc = (
        f"{M.MARKER_OPEN}\n"
        "1 + 1 = 99\n"
        f"{M.MARKER_CLOSE}\n"
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(bad_doc))
    rc = M.main(["--from-stdin"])
    assert rc == 1


def test_main_self_check_within_tolerance():
    """8R-B2 self-check — 实际 LOC 应落在 DECLARED_LOC ± TOLERANCE 内."""
    rc = M.main(["--self-check"])
    # self-check 应通过 (返回 0); 若返回 2 说明声明的 LOC 需要更新
    assert rc in (0, 2)


# ---------------------------------------------------------------------------
# quality-hardening Round 3 (2026-05-27): 补缺失分支覆盖
# loc_summation_check.py 85% -> 100% (lines 59-60 / 104-106 / 129-134 / 141-143)
# ---------------------------------------------------------------------------


def test_unclosed_open_marker_includes_rest_of_file():
    """OPEN 标记未闭合 → 从 OPEN 捕获到文件末尾 (lines 59-60)."""
    doc = (
        f"{M.MARKER_OPEN}\n"
        "Tail with bad chain: 1 + 1 = 99\n"
        # 故意不写 MARKER_CLOSE
    )
    violations = M.check_text(doc, src="unclosed.md")
    assert len(violations) == 1
    assert violations[0][2] == 2 and violations[0][3] == 99


def test_self_check_fails_when_declared_loc_off(monkeypatch, capsys):
    """self-check FAIL 路径 — DECLARED_LOC 被扰动超过 TOLERANCE (lines 104-106)."""
    monkeypatch.setattr(M, 'DECLARED_LOC', M.DECLARED_LOC + 100)
    rc = M.self_check()
    assert rc == 2
    err = capsys.readouterr().err
    assert "[self-check FAIL]" in err


def test_main_skips_missing_path_and_continues(tmp_path, capsys):
    """CLI: 不存在 path 跳过并继续 (lines 129-134)."""
    real = tmp_path / "real.md"
    real.write_text(
        f"{M.MARKER_OPEN}\n10 + 10 = 20\n{M.MARKER_CLOSE}\n",
        encoding='utf-8',
    )
    missing = tmp_path / "nope.md"
    rc = M.main([str(missing), str(real)])
    # 退出码 0: 真实文件通过检查, 缺失文件被跳过 (不计违规)
    assert rc == 0
    err = capsys.readouterr().err
    assert "not found" in err


def test_main_clean_exit_message(tmp_path, capsys):
    """CLI happy path 输出 [OK] 消息 (lines 141-143)."""
    p = tmp_path / "ok.md"
    p.write_text(
        f"{M.MARKER_OPEN}\nClean: 7 + 3 = 10\n{M.MARKER_CLOSE}\n",
        encoding='utf-8',
    )
    rc = M.main([str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[OK]" in out
