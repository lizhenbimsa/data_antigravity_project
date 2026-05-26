"""Smoke tests for P2/P3/P4 paper-level analysis CLIs.

quality-hardening Round 22 (2026-05-27): bank_fintech_attention / locus / substance
analysis.py 模块此前在 tests/ 中零直接覆盖. 参照 test_papers_bank_fintech_tone.py
的 P1-8 pattern, 验证两类不变量:
  1. 模块可 import (无 import-time error / 循环依赖崩溃)
  2. analysis.main(['--dry-run']) 可调用且返回 0 (覆盖 CLI 上半 + dry-run 路径)
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


_PAPER_IDS = [
    'bank_fintech_attention',  # P2
    'bank_fintech_locus',      # P4
    'bank_fintech_substance',  # P3
]


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_root_importable(paper_id):
    """3 篇 paper-level 包根 (__init__) 可 import."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}")
    assert mod is not None


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_analysis_importable(paper_id):
    """analysis 子模块可 import 且暴露 main."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    assert callable(mod.main)


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_tables_importable(paper_id):
    """tables 子模块可 import."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    assert mod is not None


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_figures_importable(paper_id):
    """figures 子模块可 import."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    assert mod is not None


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_stages_is_list_copy(paper_id):
    """STAGES = list(STAGES_MAIN) 是 list, 长度 > 0, 非同一引用."""
    from news_process.core.dag import STAGES_MAIN
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    assert isinstance(mod.STAGES, list)
    assert len(mod.STAGES) == len(STAGES_MAIN)
    assert mod.STAGES is not STAGES_MAIN


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_dry_run_returns_zero(paper_id):
    """analysis.main(['--dry-run']) 返回 0 (覆盖 dry-run 路径整段)."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    rc = mod.main(['--dry-run'])
    assert rc == 0


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
@pytest.mark.parametrize("stage", ["pipeline", "tables", "figures", "all"])
def test_paper_main_dry_run_accepts_all_stages(paper_id, stage):
    """4 种 --stage 值在 --dry-run 下均返回 0."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    rc = mod.main(['--dry-run', '--stage', stage])
    assert rc == 0
