"""P2/P3/P4 三篇 paper 的 tables.py thin wrapper 测试。

quality-hardening Round 33 (2026-05-27): bank_fintech_attention/locus/substance
tables.py 各 22 stmts, 之前覆盖率 ~55%. 加 mock-based 测试覆盖
build_tableN_X 4 个 thin wrapper (按各论文的真实函数名逐一列举).
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


# 各论文真实函数名清单 (部分论文用 _mechanism, P3 substance 用
# _dual_outcome)。逐项枚举以避免笛卡尔积导致的名称错配。
_TARGETS = [
    # (paper_id, fn_name, expected_csv_substring)
    ('bank_fintech_attention', 'build_table2_main',          'table2'),
    ('bank_fintech_attention', 'build_table3_mechanism',     'table3'),
    ('bank_fintech_attention', 'build_table4_heterogeneity', 'table4'),
    ('bank_fintech_attention', 'build_table5_robustness',    'table5'),
    ('bank_fintech_locus',     'build_table2_main',          'table2'),
    ('bank_fintech_locus',     'build_table3_mechanism',     'table3'),
    ('bank_fintech_locus',     'build_table4_heterogeneity', 'table4'),
    ('bank_fintech_locus',     'build_table5_robustness',    'table5'),
    ('bank_fintech_substance', 'build_table2_main',          'table2'),
    ('bank_fintech_substance', 'build_table3_dual_outcome',  'table3'),  # P3 variant
    ('bank_fintech_substance', 'build_table4_heterogeneity', 'table4'),
    ('bank_fintech_substance', 'build_table5_robustness',    'table5'),
]


@pytest.mark.parametrize("paper_id,fn_name,expected_csv_substr", _TARGETS)
def test_table_wrapper_delegates_to_read_paper_esttab(paper_id, fn_name,
                                                     expected_csv_substr):
    """build_tableN_X 委托 read_paper_esttab(paper_id, csv, paper_config).

    Mock read_paper_esttab, 验证调用路径 + 参数 + CSV 文件名子串.
    """
    tables_mod = importlib.import_module(f"news_process.papers.{paper_id}.tables")
    fn = getattr(tables_mod, fn_name)
    fake_df = pd.DataFrame({'M1': [1, 2]}, index=['a', 'b'])
    with patch('news_process.papers._common.stata_postprocess.read_paper_esttab',
               return_value=fake_df) as mock_read:
        result = fn()
        assert mock_read.called
        args = mock_read.call_args[0]
        assert args[0] == paper_id
        csv_name = args[1]
        assert expected_csv_substr in csv_name
        assert csv_name.endswith('.csv')
        assert isinstance(result, pd.DataFrame)
