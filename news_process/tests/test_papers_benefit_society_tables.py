"""tests/test_papers_benefit_society_tables.py — Round 44 quality-hardening.

`benefit_society/tables.py` 含 build_table1 + write_table1 + 8 个 thin wrapper
(build_tableN / build_table_aN) delegate 到 papers/_common 通用工具. 此前
完全无 unit test → 65.85% (14/41 miss). Mock delegate target 验证调用路径.
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

# 映射表: (函数名, 期望的 csv 文件名子串)
_TARGETS = [
    ('build_table2_main',                 'table2_main.csv'),
    ('build_table3_mechanism',            'table3_mechanism.csv'),
    ('build_table4_heterogeneity',        'table4_heterogeneity.csv'),
    ('build_table5_robustness',           'table5_robustness.csv'),
    ('build_table_a1_inter_track_kappa',  'tableA1_inter_track_kappa.csv'),
    ('build_table_a2_attitude_track_switch', 'tableA2_attitude_track_switch.csv'),
    ('build_table_8b_shrinkage_dual',     'table8b_shrinkage_dual.csv'),
    ('build_table_a9_external_validation', 'tableA9_external_validation.csv'),
    ('build_table_a10_placebo',           'tableA10_placebo_business_lines.csv'),
    ('build_table_a11_anchor_alt',        'tableA11_anchor_family_alternative.csv'),
]


@pytest.mark.parametrize("fn_name,expected_csv", _TARGETS)
def test_build_table_wrapper_delegates_to_read_paper_esttab(fn_name, expected_csv):
    """各 build_table* wrapper 调 read_paper_esttab(paper_id, csv, paper_config)."""
    mod = importlib.import_module('news_process.papers.benefit_society.tables')
    fn = getattr(mod, fn_name)
    fake_df = pd.DataFrame({'M1': [1.0, 2.0]}, index=['a', 'b'])
    with patch('news_process.papers._common.stata_postprocess.read_paper_esttab',
               return_value=fake_df) as mock_read:
        result = fn()
        assert mock_read.called
        args = mock_read.call_args[0]
        assert args[0] == 'benefit_society'
        assert args[1] == expected_csv
        assert isinstance(result, pd.DataFrame)


def test_build_table1_delegates_with_paper_id_and_variables():
    """build_table1 用 paper_id='benefit_society' + _TABLE1_VARIABLES 调 _common."""
    from news_process.papers.benefit_society import tables as t_mod
    fake_df = pd.DataFrame({'mean': [0.1, 0.2]}, index=['a', 'b'])
    with patch.object(t_mod, 'build_summary_table', return_value=fake_df) as m:
        result = t_mod.build_table1()
        args, kwargs = m.call_args
        assert args[0] == 'benefit_society'
        assert args[1] == t_mod._TABLE1_VARIABLES
        assert kwargs.get('paper_config') is None
        assert result is fake_df


def test_write_table1_default_filenames():
    """write_table1 默认 filename/dta_filename."""
    from news_process.papers.benefit_society import tables as t_mod
    fake_path = Path('/tmp/fake.csv')
    with patch.object(t_mod, 'write_summary_table', return_value=fake_path) as m:
        result = t_mod.write_table1()
        args, kwargs = m.call_args
        assert args[0] == 'benefit_society'
        assert args[1] == t_mod._TABLE1_VARIABLES
        assert kwargs.get('filename') == 'table1_summary_stats.csv'
        assert kwargs.get('dta_filename') == 'table1_summary_stats.dta'
        assert result is fake_path


def test_table1_variables_anchors():
    """_TABLE1_VARIABLES 锚定 8 个 benefit_* 变量 + 2 个信息环境对照."""
    from news_process.papers.benefit_society.tables import _TABLE1_VARIABLES
    must_have = {
        'benefit_mean_full', 'benefit_mean_ctx', 'benefit_mean_ss',
        'benefit_std_full', 'benefit_std_ctx', 'benefit_std_ss',
        'benefit_pos_frac_full', 'benefit_pos_frac_ctx', 'benefit_pos_frac_ss',
        'benefit_neg_frac_full', 'benefit_neg_frac_ctx', 'benefit_neg_frac_ss',
        'n_articles', 'ln_news_coverage',
    }
    actual = set(_TABLE1_VARIABLES)
    missing = must_have - actual
    assert not missing
    # v3.9.0 三轨: 4 个 benefit 测度各补 _ss 孪生 (10→14)
    assert len(_TABLE1_VARIABLES) == 14


def test_module_exports_match_all():
    """__all__ 锁定 12 个 public table builders."""
    from news_process.papers.benefit_society import tables as t_mod
    expected_in_all = {
        'build_table1', 'write_table1',
        'build_table2_main', 'build_table3_mechanism',
        'build_table4_heterogeneity', 'build_table5_robustness',
        'build_table_a1_inter_track_kappa',
        'build_table_a2_attitude_track_switch',
        'build_table_8b_shrinkage_dual',
        'build_table_a9_external_validation',
        'build_table_a10_placebo',
        'build_table_a11_anchor_alt',
    }
    assert set(t_mod.__all__) == expected_in_all
