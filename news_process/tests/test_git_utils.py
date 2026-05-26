"""Tests for ``news_process.papers._common._git_utils.get_git_commit_hash_with_dirty``.

quality-hardening Round 2 (2026-05-27): 既有 test_build_replication_package
覆盖到 happy path, missing 的 fallback 路径 (subprocess 失败 → 'unknown') 由
本文件补齐, 使 _git_utils.py 行覆盖 84.62% → 100%.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common._git_utils import (
    _get_git_commit_hash_with_dirty,
    get_git_commit_hash_with_dirty,
)


def test_legacy_alias_points_to_same_function():
    """Q1.4 后向兼容: 下划线别名必须与 public name 指向同一对象。"""
    assert _get_git_commit_hash_with_dirty is get_git_commit_hash_with_dirty


def test_returns_unknown_when_git_binary_missing():
    """git 不在 PATH → FileNotFoundError → 'unknown'."""
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=FileNotFoundError("git not on PATH")):
        assert get_git_commit_hash_with_dirty() == 'unknown'


def test_returns_unknown_on_timeout():
    """subprocess 超时 → 'unknown'."""
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=subprocess.TimeoutExpired(cmd='git', timeout=10)):
        assert get_git_commit_hash_with_dirty() == 'unknown'


def test_returns_unknown_on_called_process_error():
    """git 非零退出码 (e.g. 非 repo) → 'unknown'."""
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=subprocess.CalledProcessError(
                   returncode=128, cmd='git rev-parse HEAD')):
        assert get_git_commit_hash_with_dirty() == 'unknown'


def _mk_completed(stdout: str = ''):
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout)


def test_clean_tree_returns_short_hash():
    """clean working tree → 12-char hash, 不附 +dirty 后缀。"""
    fake_hash = 'abcdef012345abcde'  # 17 chars; helper 截到 12
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=[_mk_completed(fake_hash + '\n'),
                            _mk_completed('')]):
        result = get_git_commit_hash_with_dirty()
        assert result == 'abcdef012345'
        assert '+dirty' not in result


def test_dirty_tree_appends_dirty_suffix():
    """dirty working tree (git status --porcelain 非空) → '<hash>+dirty'."""
    fake_hash = '1234567890ab'
    fake_status = ' M news_process/__init__.py\n'
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=[_mk_completed(fake_hash + '\n'),
                            _mk_completed(fake_status)]):
        result = get_git_commit_hash_with_dirty()
        assert result == '1234567890ab+dirty'


@pytest.mark.parametrize("exc", [
    FileNotFoundError("git binary missing"),
    subprocess.TimeoutExpired(cmd='git', timeout=10),
    subprocess.CalledProcessError(returncode=1, cmd='git'),
])
def test_all_three_caught_exceptions_yield_unknown(exc):
    """docstring 列出的 3 类异常都应 catch 并返回 'unknown' (覆盖 except 行 49-50)."""
    with patch('news_process.papers._common._git_utils.subprocess.run',
               side_effect=exc):
        assert get_git_commit_hash_with_dirty() == 'unknown'
