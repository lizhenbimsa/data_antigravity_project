"""tests/test_papers_build_table1_wrappers.py — Round 54 quality-hardening.

6 篇 paper-level (bank_fintech_attention/locus/substance/brokerage_network/
llm_peer/strategic_diff) 的 tables.py 都含 build_table1 + write_table1 两个
thin wrapper. 各文件 90.91-91.30% 覆盖率, 漏的就是这俩 wrapper. 这里 mock
delegate target 到 100%.

镜像 Round 36 (bank_fintech_tone) + Round 44 (benefit_society) 模式.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


_PAPER_IDS = [
    'bank_fintech_attention',
    'bank_fintech_locus',
    'bank_fintech_substance',
    'brokerage_network',
    'llm_peer',
    'strategic_diff',
]


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_build_table1_delegates_to_common(paper_id):
    """build_table1() 必须 delegate _common.build_summary_table 用本论文 paper_id."""
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    fake_df = pd.DataFrame({'mean': [0.1, 0.2]}, index=['a', 'b'])
    with patch.object(tables_mod, 'build_summary_table',
                       return_value=fake_df) as mock_b:
        result = tables_mod.build_table1()
        args, _ = mock_b.call_args
        assert args[0] == paper_id
        assert args[1] == tables_mod._TABLE1_VARIABLES
        assert result is fake_df


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_write_table1_delegates_to_common(paper_id, tmp_path):
    """write_table1() 必须 delegate _common.write_summary_table 且默认 csv/dta filenames."""
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    fake_path = tmp_path / 'fake.csv'
    with patch.object(tables_mod, 'write_summary_table',
                       return_value=fake_path) as mock_w:
        result = tables_mod.write_table1()
        args, kwargs = mock_w.call_args
        assert args[0] == paper_id
        assert args[1] == tables_mod._TABLE1_VARIABLES
        assert kwargs.get('filename') == 'table1_summary_stats.csv'
        assert kwargs.get('dta_filename') == 'table1_summary_stats.dta'
        assert result is fake_path


@pytest.mark.parametrize("paper_id", _PAPER_IDS)
def test_table1_variables_nonempty(paper_id):
    """_TABLE1_VARIABLES 必须非空 (每篇论文均有 Table 1 核心变量)."""
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    assert isinstance(tables_mod._TABLE1_VARIABLES, list)
    assert len(tables_mod._TABLE1_VARIABLES) > 0


# 衍生三篇 paper 的 build_tableN delegate 测试 (brokerage/llm_peer/strategic_diff)
_DERIVATIVE_TABLE_TARGETS = [
    # (paper_id, fn_name, expected_csv_substring)
    ('brokerage_network', 'build_table2_main',          'table2_main_iv_2sls.csv'),
    ('brokerage_network', 'build_table3_mechanism',     'table3_mechanism_policy.csv'),
    ('brokerage_network', 'build_table4_heterogeneity', 'table4_heterogeneity.csv'),
    ('brokerage_network', 'build_table5_robustness',    'table5_robustness.csv'),
    ('llm_peer',          'build_table2_main',          'table2_main_iv_2sls.csv'),
    ('llm_peer',          'build_table3_cutoff',        'table3_cutoff_sensitivity.csv'),
    ('llm_peer',          'build_table4_heterogeneity', 'table4_heterogeneity.csv'),
    ('llm_peer',          'build_table5_robustness',    'table5_robustness.csv'),
    ('strategic_diff',    'build_table2_main',          'table2_main.csv'),
    ('strategic_diff',    'build_table3_mechanism',     'table3_mechanism.csv'),
    ('strategic_diff',    'build_table4_heterogeneity', 'table4_heterogeneity.csv'),
    ('strategic_diff',    'build_table5_robustness',    'table5a_n_sensitivity.csv'),
]


@pytest.mark.parametrize("paper_id,fn_name,expected_csv", _DERIVATIVE_TABLE_TARGETS)
def test_derivative_table_delegates_to_read_paper_esttab(paper_id, fn_name, expected_csv):
    """衍生三篇 paper 的 build_tableN delegate 到 read_paper_esttab."""
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    fn = getattr(tables_mod, fn_name)
    fake_df = pd.DataFrame({'M1': [1.0]}, index=['a'])
    with patch('news_process.papers._common.stata_postprocess.read_paper_esttab',
                return_value=fake_df) as mock_read:
        result = fn()
        assert mock_read.called
        args = mock_read.call_args[0]
        assert args[0] == paper_id
        assert args[1] == expected_csv
        assert isinstance(result, pd.DataFrame)
