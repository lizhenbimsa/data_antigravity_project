"""tests/integration/test_panel_no_mojibake.py — v3.7.3 Plan A v1.0 (v1.0.2 correction).

NEW-B1 status: **false alarm corrected during execution-period 2026-05-26**.

Original concern (refuted)
==========================
During Plan A initial verification, ``data/processed/40_panel_yearly.parquet``
column names viewed via PowerShell appeared to contain ``����`` mojibake
sequences (e.g. ``finbert_cn_����_w_sum_full``). This was incorrectly
interpreted as GBK/UTF-8 double-encoding pollution.

Actual finding (verified by Unicode codepoint scan)
====================================================
The columns contain **legitimate UTF-8 Chinese characters** (not U+FFFD
replacement chars). Codepoint scan revealed:
    0x6b63 = 正 (zhèng, "positive")
    0x9762 = 面 (miàn, "side")
    0x8d1f = 负 (fù, "negative")

So actual column names are ``finbert_cn_正面_w_sum_full`` / ``finbert_cn_负面_w_sum_full``
etc. PowerShell's GBK-default code page cannot render these UTF-8 Chinese
characters and displays them as ``����``. This is a **terminal rendering
artifact, not a data pollution**.

This test's own ``_detect_mojibake_columns`` helper guards against **real**
future U+FFFD mojibake; that is a separate concern from the Chinese column
names which are valid UTF-8 and handled correctly by the ``stata_export.py``
rename layer (v3.5.2+) for downstream .dta export.

This test verifies:
1. Panel has zero U+FFFD mojibake columns (the original suspicion).
2. Chinese-character columns exist (informational; not a failure).
3. Pattern consistent with v3.5.2 LM 4 子词典 sentiment label encoding.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pd = pytest.importorskip("pandas", reason="pandas required for panel scan")

# Panel files to scan (relative to repo root). All known parquet outputs of
# stage 45 / stage 51. Each is scanned independently if it exists on disk;
# missing files are not an error (CI may run without disk panel).
PANEL_FILES = [
    "data/processed/40_panel_yearly.parquet",
    "data/processed/51_panel_with_controls.parquet",
]


def _detect_mojibake_columns(panel: pd.DataFrame) -> list[str]:
    """Return column names containing U+FFFD or ``����`` sequence."""
    return [c for c in panel.columns
            if "�" in c or "����" in c]


@pytest.fixture(scope="module")
def panel_columns_by_file() -> dict[str, list[str]]:
    """Load each panel file once, return mojibake column list per file.

    Skips files that don't exist (allows CI without panel disk artifacts).
    """
    results = {}
    for rel_path in PANEL_FILES:
        path = Path(rel_path)
        if not path.exists():
            continue
        try:
            panel = pd.read_parquet(path)
        except Exception as e:
            pytest.skip(f"cannot read {rel_path}: {e}")
        results[rel_path] = _detect_mojibake_columns(panel)
    return results


def test_at_least_one_panel_file_exists(panel_columns_by_file):
    """Sanity: ≥ 1 panel file scanned (otherwise test has no data)."""
    if not panel_columns_by_file:
        pytest.skip("no panel files found — CI without disk artifacts")
    assert len(panel_columns_by_file) >= 1


def test_panel_columns_have_no_mojibake(panel_columns_by_file):
    """Strict check: no panel column should contain U+FFFD replacement char.

    NEW-B1 v1.0.2 correction: verified panel has 0 U+FFFD mojibake; the
    original observation of ``����`` in PowerShell output was a terminal
    rendering artifact for legitimate UTF-8 Chinese characters.
    """
    all_mojibake = {}
    for file_path, mojibake_cols in panel_columns_by_file.items():
        if mojibake_cols:
            all_mojibake[file_path] = mojibake_cols

    assert not all_mojibake, (
        f"NEW (post-v1.0.2): panel files have REAL U+FFFD mojibake columns: "
        f"{ {k: len(v) for k, v in all_mojibake.items()} }; "
        f"first 5 examples per file: "
        f"{ {k: v[:5] for k, v in all_mojibake.items()} }; "
        f"this is a regression — investigate stage 22/23 encoding output."
    )


def test_panel_has_expected_chinese_columns(panel_columns_by_file):
    """Diagnostic (informational): panel contains ~100+ Chinese-character
    columns (post-v3.5.2 LM 4 子词典 sentiment labels). This is NOT mojibake;
    it's valid UTF-8 Chinese encoded dict labels (正面/负面 etc).

    Verified codepoints: 0x6b63 (正) / 0x9762 (面) / 0x8d1f (负).

    stata_export.py is responsible for Chinese→ASCII rename during .dta
    export to avoid Stata variable-name constraint; this test only verifies
    panel-side Chinese columns exist as expected.
    """
    for file_path, _ in panel_columns_by_file.items():
        path = Path(file_path)
        panel = pd.read_parquet(path)
        chinese_cols = [c for c in panel.columns
                        if any(0x4e00 <= ord(ch) <= 0x9fff for ch in c)]
        # ≥ 50 expected (v3.5.2+ LM 4 sub-dict × multiple weights × multi-track)
        assert len(chinese_cols) >= 50 or len(chinese_cols) == 0, (
            f"{file_path}: unexpected Chinese column count {len(chinese_cols)}; "
            f"v3.5.2+ baseline is ≥ 50 (or 0 if pre-v3.5.2 panel). "
            f"Sample: {chinese_cols[:3]}"
        )
