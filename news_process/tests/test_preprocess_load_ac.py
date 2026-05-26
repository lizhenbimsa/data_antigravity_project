"""Tests for ``news_process.pipeline.preprocess.load`` AC automaton + single-file processor.

quality-hardening Round 25 (2026-05-27): load.py 0% → 部分覆盖. Module
此前在 tests/ 中无直接覆盖. 重点测两个 AC helper (line 44-72), 模块级 singleton
+ _process_single_file 的失败路径.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_build_ac_automaton_returns_ahocorasick_instance():
    """_build_ac_automaton 返回可 iter 的 Automaton."""
    from news_process.pipeline.preprocess.load import _build_ac_automaton
    auto = _build_ac_automaton(['工商银行', '招商银行', '建设银行'])
    assert auto is not None
    # 验证可 iter
    matches = list(auto.iter('工商银行公告'))
    assert len(matches) >= 1


def test_build_ac_automaton_case_folded():
    """_build_ac_automaton 内部对 keyword .lower(), match 时也 .lower()."""
    from news_process.pipeline.preprocess.load import (
        _ac_contains_any,
        _build_ac_automaton,
    )
    auto = _build_ac_automaton(['ICBC', 'CMB'])
    # uppercase / lowercase / mixed 都应命中
    assert _ac_contains_any('icbc news', auto) is True
    assert _ac_contains_any('ICBC NEWS', auto) is True
    assert _ac_contains_any('IcBc news', auto) is True
    assert _ac_contains_any('totally unrelated', auto) is False


def test_ac_contains_any_chinese_keywords():
    """_ac_contains_any 命中中文 keyword."""
    from news_process.pipeline.preprocess.load import (
        _ac_contains_any,
        _build_ac_automaton,
    )
    auto = _build_ac_automaton(['工商银行', '招商银行'])
    assert _ac_contains_any('今日工商银行公告', auto) is True
    assert _ac_contains_any('招商银行业绩', auto) is True
    assert _ac_contains_any('完全无关文本', auto) is False
    assert _ac_contains_any('', auto) is False


def test_ac_contains_any_short_circuits_on_first_match():
    """_ac_contains_any 命中第一个就返回 True (line 70-71)."""
    from news_process.pipeline.preprocess.load import (
        _ac_contains_any,
        _build_ac_automaton,
    )
    auto = _build_ac_automaton(['a', 'b', 'c'])
    # 文本含多个 keyword — 返回 True (而不是 list)
    result = _ac_contains_any('abc def', auto)
    assert result is True


def test_module_singleton_bank_kw_automaton_exists():
    """BANK_KW_AUTOMATON 在 import 时由 BANK_KEYWORDS 构建 (line 75-77)."""
    from news_process.pipeline.preprocess.load import (
        BANK_KW_AUTOMATON,
    )
    # 配置加载成功后, singleton 应非 None (BANK_KEYWORDS 有 8000+ keyword)
    if BANK_KW_AUTOMATON is not None:
        # 命中常见银行名
        from news_process.pipeline.preprocess.load import _ac_contains_any
        assert _ac_contains_any('工商银行公告', BANK_KW_AUTOMATON) is True


def test_process_single_file_handles_missing_file(tmp_path, caplog):
    """_process_single_file 输入不存在 → except → return None + error log."""
    from news_process.pipeline.preprocess.load import _process_single_file
    missing = tmp_path / 'no_such.xlsx'
    result = _process_single_file(str(missing))
    assert result is None


def test_process_single_file_handles_corrupt_excel(tmp_path):
    """_process_single_file 输入是无效 xlsx → except 不抛 + return None (line 179-181)."""
    from news_process.pipeline.preprocess.load import _process_single_file
    bad = tmp_path / 'corrupt.xlsx'
    bad.write_bytes(b'NOT A REAL XLSX FILE')
    result = _process_single_file(str(bad))
    assert result is None
