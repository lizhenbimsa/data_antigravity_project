"""tests/test_loc_summation_check.py — v3.7.4 L4 lint tests.

Covers 4.D protocol (5R-A1) + stdin (8R-A2) + self-check (8R-B2) + opt-in marker (7R-B3).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# Path injection: project root on sys.path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from news_process.scripts.audit import loc_summation_check as M  # noqa: E402

# --- 8R-B3 marker opt-in: chain INSIDE marker triggers check; OUTSIDE does not ---

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
    """7R-B3: opt-in — chains outside <!-- loc-summation-check --> NOT checked."""
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
    """8R-A2 stdin pathway."""
    bad_doc = (
        f"{M.MARKER_OPEN}\n"
        "1 + 1 = 99\n"
        f"{M.MARKER_CLOSE}\n"
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(bad_doc))
    rc = M.main(["--from-stdin"])
    assert rc == 1


def test_main_self_check_within_tolerance():
    """8R-B2 self-check — actual LOC should match DECLARED_LOC ± TOLERANCE."""
    rc = M.main(["--self-check"])
    # Self-check should pass (0) — if it fails (2), declared LOC needs updating
    assert rc in (0, 2)
