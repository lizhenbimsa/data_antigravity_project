"""P2/P3/P4 三篇 paper-level analysis CLI 的 smoke 测试。

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


# ---------------------------------------------------------------------------
# quality-hardening Round 46 (2026-05-27): P2/P3/P4 analysis.py 覆盖率 57.14% → 100%
# 覆盖非 dry-run 路径 (lines 45-65 in P2/P3/P4 analysis.py)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_pipeline_stage_calls_run_main_pipeline(paper_id):
    """--stage pipeline 调 run_main_pipeline."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    with patch.object(mod, 'run_main_pipeline') as mock_pipe:
        rc = mod.main(['--stage', 'pipeline'])
    assert rc == 0
    assert mock_pipe.called


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_tables_stage_invokes_write_table1(paper_id, tmp_path):
    """--stage tables 调 tables.write_table1."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    with patch.object(tables_mod, 'write_table1',
                       return_value=tmp_path / 'fake.csv') as mw:
        rc = mod.main(['--stage', 'tables'])
    assert rc == 0
    assert mw.called


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_tables_stage_handles_filenotfound(paper_id):
    """tables.write_table1 抛 FileNotFoundError → warning 不传播 (P2/P3/P4 行 54-55)."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    with patch.object(tables_mod, 'write_table1',
                       side_effect=FileNotFoundError("panel 缺失")):
        rc = mod.main(['--stage', 'tables'])
    assert rc == 0


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_figures_stage_handles_filenotfound(paper_id):
    """figures.plot 抛 FileNotFoundError → warning 不传播 (lines 62-63)."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    figures_mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    # 每篇 paper 都有不同的 plot 函数名; 用 dir() 找第一个 callable plot_*
    plot_fns = [n for n in dir(figures_mod)
                if n.startswith('plot_') and callable(getattr(figures_mod, n))]
    assert len(plot_fns) >= 1, f"{paper_id}/figures.py 应至少有 1 个 plot_* 函数"
    # P2/P3/P4 analysis.py 默认调用第一个 plot 函数 (依源码: plot_attention_distribution
    # / plot_*_distribution 等)
    primary_plot = plot_fns[0]
    with patch.object(figures_mod, primary_plot,
                       side_effect=FileNotFoundError("pipeline 输出缺失")):
        rc = mod.main(['--stage', 'figures'])
    assert rc == 0


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_figures_stage_happy_path(paper_id, tmp_path):
    """plot 成功返回 → walk [OK] logging branch (line 61 in attention / 58 in locus/substance)."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    figures_mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    plot_fns = [n for n in dir(figures_mod)
                if n.startswith('plot_') and callable(getattr(figures_mod, n))]
    primary_plot = plot_fns[0]
    fake_out = tmp_path / 'fake.png'
    with patch.object(figures_mod, primary_plot,
                       return_value=fake_out):
        rc = mod.main(['--stage', 'figures'])
    assert rc == 0


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_paper_main_all_stage_runs_pipeline_and_handles_missing_data(paper_id):
    """--stage all 调 run_main_pipeline + tables + figures (各 except 路径)."""
    from unittest.mock import patch
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    figures_mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    with patch.object(mod, 'run_main_pipeline') as mp:
        with patch.object(tables_mod, 'write_table1',
                           side_effect=FileNotFoundError("missing")):
            # plot_* 也走 except
            plot_fns = [n for n in dir(figures_mod)
                        if n.startswith('plot_')
                        and callable(getattr(figures_mod, n))]
            with patch.object(figures_mod, plot_fns[0],
                               side_effect=FileNotFoundError("missing")):
                rc = mod.main(['--stage', 'all'])
    assert rc == 0
    assert mp.called
