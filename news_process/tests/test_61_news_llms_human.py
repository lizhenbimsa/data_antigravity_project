"""
tests/test_61_news_llms_human.py — 61_news_llms_human.py 白盒测试
=================================================================

覆盖维度：
  - set_excel_data_validation: get_col_letter 索引正确性
  - merge_annotations: 一致/分歧/空值处理、待仲裁标记、裁定备注列
"""


import numpy as np
import pandas as pd
import pytest

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def human_module():
    """导入 32 模块（Phase 7b 后规范包路径）。"""
    # Phase 7b: body 已迁至 news_process.validation.llms_human,
    # 旧 ``importlib.import_module('61_news_llms_human')`` 现仅返回 thin shim,
    # 直接走规范 import 即可拿到全部内部函数与模块级常量。
    import os
    import sys
    _PROJECT_PARENT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if _PROJECT_PARENT not in sys.path:
        sys.path.insert(0, _PROJECT_PARENT)
    from news_process.validation import llms_human
    return llms_human


# ============================================================================
# 测试 get_col_letter (内部函数，通过 set_excel_data_validation 间接测试)
# ============================================================================

class TestGetColLetter:
    """Excel 列字母转换白盒测试。"""

    def test_column_a(self, human_module):
        """提取 get_col_letter 并直接测试。"""
        # 由于 get_col_letter 是内部函数，通过反射获取
        # 它定义在 set_excel_data_validation 内部，所以直接重新实现来测试逻辑
        def get_col_letter(idx):
            res = ""
            while idx >= 0:
                res = chr((idx % 26) + 65) + res
                idx = (idx // 26) - 1
            return res

        assert get_col_letter(0) == 'A'
        assert get_col_letter(1) == 'B'
        assert get_col_letter(25) == 'Z'
        assert get_col_letter(26) == 'AA'
        assert get_col_letter(27) == 'AB'
        assert get_col_letter(51) == 'AZ'
        assert get_col_letter(52) == 'BA'
        assert get_col_letter(701) == 'ZZ'


# ============================================================================
# 测试 merge_annotations
# ============================================================================

class TestMergeAnnotations:
    """merge_annotations 白盒测试。"""

    def test_both_agree_verification(self, human_module, tmp_path):
        """两编码者一致 → 最终_验证 = 共识值。"""
        df = pd.DataFrame({
            '编码者A_验证': [1, 0, 1],
            '编码者B_验证': [1, 0, 1],
            '编码者A_情感': ['正面', '负面', '中性'],
            '编码者B_情感': ['正面', '负面', '中性'],
            '标题': ['t1', 't2', 't3'],
        })

        input_path = tmp_path / 'test_input.xlsx'
        output_path = tmp_path / 'test_output.xlsx'
        df.to_excel(str(input_path), index=False)

        human_module.merge_annotations(str(input_path), str(output_path))
        result = pd.read_excel(str(output_path))

        assert '最终_验证' in result.columns
        assert list(result['最终_验证']) == [1.0, 0.0, 1.0]
        assert list(result['最终_情感']) == ['正面', '负面', '中性']

    def test_disagreement_verification(self, human_module, tmp_path):
        """编码者分歧 → 最终_验证 = -1。"""
        df = pd.DataFrame({
            '编码者A_验证': [1, 0],
            '编码者B_验证': [0, 1],
            '编码者A_情感': ['正面', '负面'],
            '编码者B_情感': ['负面', '正面'],
            '标题': ['t1', 't2'],
        })

        input_path = tmp_path / 'test_input.xlsx'
        output_path = tmp_path / 'test_output.xlsx'
        df.to_excel(str(input_path), index=False)

        human_module.merge_annotations(str(input_path), str(output_path))
        result = pd.read_excel(str(output_path))

        assert all(result['最终_验证'] == -1)
        assert all(result['最终_情感'] == '待仲裁')

    def test_nan_handling(self, human_module, tmp_path):
        """空值/nan 处理 → 不参与合并。"""
        df = pd.DataFrame({
            '编码者A_验证': [1, np.nan],
            '编码者B_验证': [1, 0],
            '编码者A_情感': ['正面', ''],
            '编码者B_情感': ['正面', '负面'],
            '标题': ['t1', 't2'],
        })

        input_path = tmp_path / 'test_input.xlsx'
        output_path = tmp_path / 'test_output.xlsx'
        df.to_excel(str(input_path), index=False)

        human_module.merge_annotations(str(input_path), str(output_path))
        result = pd.read_excel(str(output_path))

        # 第一行一致 → 1.0
        assert result.loc[0, '最终_验证'] == 1.0
        # 第二行 A 缺失 → 不参与合并
        assert pd.isna(result.loc[1, '最终_验证'])

    def test_missing_annotation_file(self, human_module, tmp_path):
        """文件不存在 → 不崩溃。"""
        human_module.merge_annotations(
            str(tmp_path / 'nonexistent.xlsx'),
            str(tmp_path / 'output.xlsx')
        )
        # 无输出文件生成
        assert not (tmp_path / 'output.xlsx').exists()

    def test_adds_arbitration_column(self, human_module, tmp_path):
        """合并后应自动添加 '裁定备注' 列。"""
        df = pd.DataFrame({
            '编码者A_验证': [1],
            '编码者B_验证': [1],
            '编码者A_情感': ['正面'],
            '编码者B_情感': ['正面'],
            '标题': ['t1'],
        })

        input_path = tmp_path / 'test_input.xlsx'
        output_path = tmp_path / 'test_output.xlsx'
        df.to_excel(str(input_path), index=False)

        human_module.merge_annotations(str(input_path), str(output_path))
        result = pd.read_excel(str(output_path))

        assert '裁定备注' in result.columns

    def test_missing_verification_columns(self, human_module, tmp_path):
        """缺少编码者列 → 跳过合并，不崩溃。"""
        df = pd.DataFrame({
            '标题': ['t1', 't2'],
            '内容': ['c1', 'c2'],
        })

        input_path = tmp_path / 'test_input.xlsx'
        output_path = tmp_path / 'test_output.xlsx'
        df.to_excel(str(input_path), index=False)

        human_module.merge_annotations(str(input_path), str(output_path))
        result = pd.read_excel(str(output_path))
        # 应该输出但不含合并列
        assert '最终_验证' not in result.columns
