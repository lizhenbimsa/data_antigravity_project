"""Tests for ``news_process.run_paper`` — multi-paper CLI dispatcher.

quality-hardening Round 23 (2026-05-27): run_paper.py 0% → ~95%. 模块此前在
tests/ 中零直接覆盖. 覆盖 6 类 CLI 路径:
  1. --list → 打印列表 + return 0
  2. 无参数 → 打印列表 + return 0
  3. 未知 paper_id → 错误 + return 2
  4. 已知 paper_id → 调度子模块 main + 返回其退出码
  5. import 失败 → return 1
  6. 子模块缺 main → return 1
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_list_flag_returns_zero_and_prints(capsys):
    """--list 打印 paper 列表 + 退出 0 (line 105-107)."""
    from news_process.run_paper import main
    rc = main(['--list'])
    assert rc == 0
    out = capsys.readouterr().out
    assert '可调度论文列表' in out
    assert 'bank_fintech_tone' in out


def test_no_args_defaults_to_list(capsys):
    """无 paper_id → 默认打印列表 + return 0 (line 109-112)."""
    from news_process.run_paper import main
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert '可调度论文列表' in out


def test_unknown_paper_id_returns_2(capsys):
    """未知 paper_id → stderr 错误 + return 2 (line 114-121)."""
    from news_process.run_paper import main
    rc = main(['totally_unknown_paper_xyz'])
    assert rc == 2
    err = capsys.readouterr().err
    assert 'ERROR' in err
    assert 'totally_unknown_paper_xyz' in err


def test_known_paper_id_dispatches_to_analysis_main():
    """已知 paper_id → 调度子模块 main, 转发 --stage 与 --dry-run (line 123-149)."""
    from news_process import run_paper
    with patch('news_process.papers.bank_fintech_tone.analysis.main',
               return_value=0) as mock_main:
        rc = run_paper.main(['bank_fintech_tone', '--dry-run'])
        assert rc == 0
        # 验证转发的 argv 含 --stage all + --dry-run
        called_args = mock_main.call_args[0][0]
        assert '--stage' in called_args
        assert 'all' in called_args
        assert '--dry-run' in called_args


def test_dispatch_returns_int_from_analysis_main():
    """analysis.main 返回 None → run_paper 转 0 (line 149 `or 0` fallback)."""
    from news_process import run_paper
    with patch('news_process.papers.bank_fintech_tone.analysis.main',
               return_value=None):
        rc = run_paper.main(['bank_fintech_tone'])
        assert rc == 0


def test_dispatch_returns_nonzero_from_analysis_main():
    """analysis.main 返回 3 → run_paper 转 3."""
    from news_process import run_paper
    with patch('news_process.papers.bank_fintech_tone.analysis.main',
               return_value=3):
        rc = run_paper.main(['bank_fintech_tone'])
        assert rc == 3


def test_dispatch_handles_import_error():
    """子模块 import 失败 → return 1 (line 133-135)."""
    from news_process import run_paper
    with patch('importlib.import_module',
               side_effect=ImportError("simulated missing module")):
        rc = run_paper.main(['bank_fintech_tone'])
        assert rc == 1


def test_dispatch_handles_module_without_main():
    """analysis 模块缺 main 属性 → return 1 (line 137-142)."""
    import types
    fake_mod = types.ModuleType('fake_no_main')
    # 故意不加 main 属性
    from news_process import run_paper
    with patch('importlib.import_module', return_value=fake_mod):
        rc = run_paper.main(['bank_fintech_tone'])
        assert rc == 1


def test_dispatch_forwards_unknown_args():
    """parse_known_args 把未知 flag (e.g. --extra-foo) 透传给子模块 main."""
    from news_process import run_paper
    with patch('news_process.papers.bank_fintech_tone.analysis.main',
               return_value=0) as mock_main:
        run_paper.main(['bank_fintech_tone', '--extra-foo', 'val'])
        called_args = mock_main.call_args[0][0]
        # extra-foo + val 应被透传
        assert '--extra-foo' in called_args
        assert 'val' in called_args


@pytest.mark.parametrize("stage", ['pipeline', 'tables', 'figures', 'all'])
def test_dispatch_stage_choices_forwarded(stage):
    """全部 4 个 --stage 选项被正确转发."""
    from news_process import run_paper
    with patch('news_process.papers.bank_fintech_tone.analysis.main',
               return_value=0) as mock_main:
        run_paper.main(['bank_fintech_tone', '--stage', stage])
        called_args = mock_main.call_args[0][0]
        assert called_args[called_args.index('--stage') + 1] == stage


def test_paper_summaries_cover_all_dispatchable_ids():
    """_PAPER_SUMMARIES 必须与 _VALID_PAPER_IDS 精确相等 — 防 --list 出 '(no summary)'。

    回归锁: 白名单 5→8 扩容 (paper_registry.PAPER_IDS_NEW) 时漏补 summary 即红。
    精确相等而非子集: P5 bank_fintech_collab 刻意不在白名单, summary 也不应含它, 双向守护。
    """
    from news_process.papers._common.paper_config import _VALID_PAPER_IDS
    from news_process.run_paper import _PAPER_SUMMARIES
    keys = set(_PAPER_SUMMARIES)
    valid = set(_VALID_PAPER_IDS)
    assert keys == valid, (
        f"summary↔白名单漂移: 缺={valid - keys}, 多={keys - valid}"
    )
