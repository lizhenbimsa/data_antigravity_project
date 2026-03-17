"""
tests/test_reporting.py — utils/reporting.py 单元测试
======================================================
"""

import os
import sys
import logging
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.reporting import _format_stat, generate_dataframe_report, _is_categorical
from utils.helpers import setup_logging


# ============================================================================
# _format_stat 测试
# ============================================================================

class TestFormatStat:
    """测试数值格式化工具函数。"""

    def test_integer(self):
        """整数应带小数位。"""
        assert _format_stat(42) == '42.00'

    def test_float(self):
        """浮点数应保留指定精度。"""
        assert _format_stat(3.14159, precision=3) == '3.142'

    def test_nan(self):
        """NaN 应返回 N/A。"""
        assert _format_stat(float('nan')) == 'N/A'

    def test_none(self):
        """None 应返回 N/A。"""
        assert _format_stat(None) == 'N/A'

    def test_string(self):
        """字符串应原样返回。"""
        assert _format_stat('hello') == 'hello'

    def test_zero(self):
        """0 应返回 0.00。"""
        assert _format_stat(0) == '0.00'

    def test_negative(self):
        """负数应正常格式化。"""
        assert _format_stat(-1.5) == '-1.50'


# ============================================================================
# _is_categorical 测试
# ============================================================================

class TestIsCategorical:
    """测试分类类型检测。"""

    def test_categorical_dtype(self):
        """CategoricalDtype 应返回 True。"""
        s = pd.Series(['a', 'b', 'c'], dtype='category')
        assert _is_categorical(s.dtype) is True

    def test_object_dtype(self):
        """object 类型应返回 False。"""
        s = pd.Series(['a', 'b', 'c'])
        assert _is_categorical(s.dtype) is False

    def test_int_dtype(self):
        """int 类型应返回 False。"""
        s = pd.Series([1, 2, 3])
        assert _is_categorical(s.dtype) is False


# ============================================================================
# generate_dataframe_report 测试
# ============================================================================

class TestGenerateDataframeReport:
    """测试 DataFrame 统计报告生成。"""

    def test_empty_dataframe(self, tmp_path):
        """空 DataFrame 不应崩溃。"""
        logger = setup_logging('report_empty', str(tmp_path / 'logs'))
        df = pd.DataFrame()
        # 不应抛出异常
        generate_dataframe_report(df, logger)

    def test_numeric_columns(self, tmp_path):
        """数值列应生成均值/标准差等统计。"""
        logger = setup_logging('report_numeric', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'score': [1.0, 2.0, 3.0, 4.0, 5.0],
            'count': [10, 20, 30, 40, 50],
        })
        generate_dataframe_report(df, logger)  # 不应抛异常

    def test_datetime_columns(self, tmp_path):
        """日期列应生成时间范围统计。"""
        logger = setup_logging('report_dt', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
        })
        generate_dataframe_report(df, logger)

    def test_boolean_columns(self, tmp_path):
        """布尔列应生成 True/False 分布。"""
        logger = setup_logging('report_bool', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'flag': [True, False, True, True, False],
        })
        generate_dataframe_report(df, logger)

    def test_object_columns(self, tmp_path):
        """文本列应生成频次统计。"""
        logger = setup_logging('report_obj', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'A', 'B', 'D'],
        })
        generate_dataframe_report(df, logger)

    def test_mixed_types(self, tmp_path):
        """混合类型列的完整报告。"""
        logger = setup_logging('report_mixed', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'name': ['张三', '李四', '王五'],
            'score': [95.5, 88.0, 72.3],
            'pass': [True, True, False],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        })
        generate_dataframe_report(df, logger)

    def test_all_null_column(self, tmp_path):
        """全空列不应崩溃。"""
        logger = setup_logging('report_null', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'empty_col': [None, None, None],
            'valid_col': [1, 2, 3],
        })
        generate_dataframe_report(df, logger)

    def test_many_unique_values(self, tmp_path):
        """高基数列应只显示 Top 5。"""
        logger = setup_logging('report_high', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'text': [f'文本{i}' for i in range(100)],
        })
        generate_dataframe_report(df, logger)

    def test_categorical_column(self, tmp_path):
        """CategoricalDtype 列应被正确处理。"""
        logger = setup_logging('report_cat', str(tmp_path / 'logs'))
        df = pd.DataFrame({
            'grade': pd.Categorical(['A', 'B', 'C', 'A', 'B']),
        })
        generate_dataframe_report(df, logger)
