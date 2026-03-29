"""
tests/test_23_tone_berts.py — 23_tone_berts.py 白盒测试
========================================================

覆盖维度：
  - _build_model_configs: YAML 配置解析、label_map str→int 转换、fallback 默认值
  - MultiModelSentimentEngine._empty_result: 已加载/未加载模型的返回格式
  - log_classification_report: 正常输出、total=0 边界、多窗口统计

Mock 策略：
  - 不加载真实 BERT 模型
  - 通过 monkeypatch 控制全局配置
"""

import pytest
import numpy as np
from collections import Counter
from unittest.mock import MagicMock, patch


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def berts_module():
    """导入 23_tone_berts 模块。"""
    import importlib
    return importlib.import_module('23_tone_berts')


# ============================================================================
# 测试 _build_model_configs
# ============================================================================

class TestBuildModelConfigs:
    """_build_model_configs 配置解析白盒测试。"""

    def test_default_configs_structure(self, berts_module):
        """内置默认配置应有至少 1 个模型。"""
        configs = berts_module.MODEL_CONFIGS
        assert isinstance(configs, list)
        assert len(configs) >= 1

    def test_label_map_int_keys(self, berts_module):
        """label_map 的键应为 int 类型。"""
        for mc in berts_module.MODEL_CONFIGS:
            for key in mc['label_map'].keys():
                assert isinstance(key, int), f"{mc['short_name']} label_map 键不是 int: {key}"

    def test_required_fields(self, berts_module):
        """每个模型配置应包含必需字段。"""
        for mc in berts_module.MODEL_CONFIGS:
            assert 'model_id' in mc
            assert 'short_name' in mc
            assert 'max_length' in mc
            assert 'label_map' in mc

    def test_label_map_values_are_chinese(self, berts_module):
        """label_map 值应为中文情感标签。"""
        valid_labels = {'正面', '中性', '负面'}
        for mc in berts_module.MODEL_CONFIGS:
            for label in mc['label_map'].values():
                assert label in valid_labels, f"无效标签: {label} in {mc['short_name']}"


# ============================================================================
# 测试 MultiModelSentimentEngine._empty_result
# ============================================================================

class TestEmptyResult:
    """_empty_result 返回格式白盒测试。"""

    def test_default_empty_result(self, berts_module):
        """未加载模型时，_empty_result 返回默认格式。"""
        engine = berts_module.MultiModelSentimentEngine([])
        result = engine._empty_result("nonexistent_model")
        assert result['label'] == '中性'
        assert result['num_windows'] == 0
        assert isinstance(result['probabilities'], dict)

    def test_empty_result_with_loaded_config(self, berts_module):
        """已加载模型配置时，概率字典应匹配模型标签。"""
        engine = berts_module.MultiModelSentimentEngine([])
        engine.loaded_configs['test_model'] = {
            'label_map': {0: '负面', 1: '正面'},
            'num_labels': 2,
        }
        result = engine._empty_result('test_model')
        assert '负面' in result['probabilities']
        assert '正面' in result['probabilities']
        assert result['probabilities']['负面'] == 0.0
        assert result['probabilities']['正面'] == 0.0


# ============================================================================
# 测试 log_classification_report
# ============================================================================

class TestBertLogReport:
    """log_classification_report 白盒测试。"""

    def test_normal_output(self, berts_module):
        """正常统计不抛异常。"""
        output = {
            'finbert_cn': {
                'columns': {'finbert_cn_label': ['正面'] * 10},
                'stats': {'finbert_cn_正面': 6, 'finbert_cn_中性': 3, 'finbert_cn_负面': 1},
                'avg_windows': 2.5,
                'num_windows_list': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1],
            }
        }
        berts_module.log_classification_report(output, total=10)

    def test_zero_total(self, berts_module):
        """total=0 不应抛异常。"""
        output = {
            'finbert_cn': {
                'columns': {'finbert_cn_label': []},
                'stats': {'finbert_cn_正面': 0, 'finbert_cn_中性': 0, 'finbert_cn_负面': 0},
                'avg_windows': 0,
                'num_windows_list': [],
            }
        }
        berts_module.log_classification_report(output, total=0)

    def test_multi_window_stats(self, berts_module):
        """多窗口和单窗口文章的统计。"""
        output = {
            'finbert_cn': {
                'columns': {'finbert_cn_label': ['正面'] * 5},
                'stats': {'finbert_cn_正面': 5, 'finbert_cn_中性': 0, 'finbert_cn_负面': 0},
                'avg_windows': 3.0,
                'num_windows_list': [1, 5, 3, 0, 2],  # 含 0（空文本）
            }
        }
        berts_module.log_classification_report(output, total=5)


# ============================================================================
# 测试 DEFAULT_LABEL_MAP 常量
# ============================================================================

class TestLabelMapConstants:
    """标签映射常量白盒测试。"""

    def test_3_class_map(self, berts_module):
        assert berts_module.DEFAULT_LABEL_MAP == {0: "负面", 1: "中性", 2: "正面"}

    def test_2_class_map(self, berts_module):
        assert berts_module.DEFAULT_LABEL_MAP_2CLASS == {0: "负面", 1: "正面"}

    def test_window_stride_ratio(self, berts_module):
        """滑动窗口步长比例应在 (0, 1] 范围内。"""
        assert 0 < berts_module.WINDOW_STRIDE_RATIO <= 1.0


# ============================================================================
# 测试 Engine 初始化
# ============================================================================

class TestEngineInit:
    """MultiModelSentimentEngine 初始化白盒测试。"""

    def test_empty_configs(self, berts_module):
        """空配置列表不应崩溃。"""
        engine = berts_module.MultiModelSentimentEngine([])
        assert len(engine.models) == 0
        assert len(engine.tokenizers) == 0

    def test_unload_all(self, berts_module):
        """unload_all 应清空所有内部状态。"""
        engine = berts_module.MultiModelSentimentEngine([])
        engine.models['test'] = 'mock_model'
        engine.tokenizers['test'] = 'mock_tokenizer'
        engine.loaded_configs['test'] = {}
        engine.unload_all()
        assert len(engine.models) == 0
        assert len(engine.tokenizers) == 0
        assert len(engine.loaded_configs) == 0
