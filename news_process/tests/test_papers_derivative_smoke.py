"""brokerage_network / llm_peer / strategic_diff 三篇 analysis CLI 的 smoke 测试。

quality-hardening Round 47 (2026-05-27): 3 篇衍生论文 analysis.py 此前在
tests/ 中零直接覆盖. 参照 test_papers_p2_p3_p4_smoke.py 的 pattern, 验证两类
不变量:
  1. 模块可 import + STAGES 是 list 拷贝 + main 可调
  2. analysis.main 在 dry-run + 各 --stage 下返回 0
  3. 非 dry-run pipeline / tables / figures 路径走 mock delegate + 异常 fallback
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# 每项格式: (paper_id, 主 plot 函数名, table builder 函数名列表)
_DERIVATIVE_PAPERS = [
    ('brokerage_network', 'plot_brokerage_centrality_distribution',
     ['build_table2_main', 'build_table3_mechanism',
      'build_table4_heterogeneity', 'build_table5_robustness']),
    ('llm_peer', 'plot_cutoff_sensitivity',
     ['build_table2_main', 'build_table3_cutoff',
      'build_table4_heterogeneity', 'build_table5_robustness']),
    ('strategic_diff', 'plot_strategic_diff_n5_distribution',
     ['build_table2_main', 'build_table3_mechanism',
      'build_table4_heterogeneity', 'build_table5_robustness']),
]

_PAPER_IDS = [t[0] for t in _DERIVATIVE_PAPERS]


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_derivative_paper_analysis_importable(paper_id):
    """analysis 子模块可 import 且暴露 main."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    assert callable(mod.main)


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_derivative_stages_is_list_copy(paper_id):
    """STAGES = list(STAGES_MAIN) 是 list 拷贝."""
    from news_process.core.dag import STAGES_MAIN
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    assert isinstance(mod.STAGES, list)
    assert len(mod.STAGES) == len(STAGES_MAIN)
    assert mod.STAGES is not STAGES_MAIN


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
@pytest.mark.parametrize("stage", ["pipeline", "tables", "figures", "all"])
def test_derivative_main_dry_run_accepts_all_stages(paper_id, stage):
    """4 种 --stage 值在 --dry-run 下均返回 0."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    rc = mod.main(['--dry-run', '--stage', stage])
    assert rc == 0


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_derivative_main_pipeline_stage_calls_run_main_pipeline(paper_id):
    """--stage pipeline 调 run_main_pipeline."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    with patch.object(mod, 'run_main_pipeline') as mp:
        rc = mod.main(['--stage', 'pipeline'])
    assert rc == 0
    assert mp.called


@pytest.mark.parametrize("paper_id,_,table_builders", _DERIVATIVE_PAPERS)
def test_derivative_main_tables_stage_walks_all_builders(paper_id, _,
                                                          table_builders,
                                                          tmp_path):
    """--stage tables 调 write_table1 + 4 个 build_tableN 全部走 happy path."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    fake_df = __import__('pandas').DataFrame({'M1': [1.0, 2.0]})
    with patch.object(tables_mod, 'write_table1',
                       return_value=tmp_path / 'fake.csv'):
        patches = []
        for builder_name in table_builders:
            p = patch.object(tables_mod, builder_name, return_value=fake_df)
            p.start()
            patches.append(p)
        try:
            rc = mod.main(['--stage', 'tables'])
        finally:
            for p in patches:
                p.stop()
    assert rc == 0


@pytest.mark.parametrize("paper_id,_,table_builders", _DERIVATIVE_PAPERS)
def test_derivative_main_tables_stage_handles_filenotfound(paper_id, _,
                                                            table_builders,
                                                            tmp_path):
    """build_tableN 抛 FileNotFoundError → warning 不传播."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    with patch.object(tables_mod, 'write_table1',
                       return_value=tmp_path / 'fake.csv'):
        patches = []
        for builder_name in table_builders:
            p = patch.object(tables_mod, builder_name,
                              side_effect=FileNotFoundError("Stata not run"))
            p.start()
            patches.append(p)
        try:
            rc = mod.main(['--stage', 'tables'])
        finally:
            for p in patches:
                p.stop()
    assert rc == 0


@pytest.mark.parametrize("paper_id,plot_fn,_", _DERIVATIVE_PAPERS)
def test_derivative_main_figures_stage_happy_path(paper_id, plot_fn, _, tmp_path):
    """plot 函数成功 → [OK] log."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    figures_mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    fake_out = tmp_path / 'fake.png'
    with patch.object(figures_mod, plot_fn, return_value=fake_out):
        rc = mod.main(['--stage', 'figures'])
    assert rc == 0


@pytest.mark.parametrize("paper_id,plot_fn,_", _DERIVATIVE_PAPERS)
def test_derivative_main_figures_stage_handles_filenotfound(paper_id, plot_fn, _):
    """plot 抛 FileNotFoundError → warning 不传播."""
    mod = importlib.import_module(f"news_process.papers.{paper_id}.analysis")
    figures_mod = importlib.import_module(f"news_process.papers.{paper_id}.figures")
    with patch.object(figures_mod, plot_fn,
                       side_effect=FileNotFoundError("pipeline 输出缺失")):
        rc = mod.main(['--stage', 'figures'])
    assert rc == 0
