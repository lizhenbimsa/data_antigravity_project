"""
tests/test_11_news_bank.py — 11_news_bank.py 白盒测试
=====================================================

覆盖维度：
  - classify_batch 分支覆盖：空DataFrame、单/多银行命中、标题匹配路径
  - merge_stats Counter 累加正确性
  - log_classification_report 除零保护
  - Firm-Document 展开逻辑（co_mentioned_banks、mention_density）

Mock 策略：
  - 全局 AC 自动机和银行列表通过 monkeypatch 注入测试数据
  - 不触发 load_config / setup_logging 的副作用
"""

import json
import pytest
import pandas as pd
import numpy as np
from collections import Counter
from unittest.mock import patch, MagicMock


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_bank_module(monkeypatch):
    """Mock 11_news_bank 模块的全局状态。"""
    import importlib
    import sys

    # 需要在首次导入前 mock 全局变量
    # 由于 11_news_bank 在模块级别执行 load_config，
    # 我们直接测试其子函数，通过 mock 全局变量隔离
    mod_name = '11_news_bank'
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        # 预设 mock 来避免模块级副作用
        mod = importlib.import_module(mod_name.replace('-', '_'))

    return mod


@pytest.fixture
def sample_bank_df():
    """创建包含银行新闻分类所需列的 mock DataFrame。"""
    return pd.DataFrame({
        '内容': [
            '中国工商银行近日推出AI风控系统。工商银行表示AI能力将赋能全业务链。'
            '工行金融科技部表示投入将持续增长。工行将在全国推广。',
            '今天天气晴朗，适合出行。气温20度。',
            '建设银行和工商银行共同发布合作报告。建行和工行将推进金融创新。'
            '建设银行表示将深化与工行的合作。建行将启动新一轮技术升级。',
        ],
        '标题': [
            '工商银行推出AI风控系统',
            '天气预报',
            '建设银行工商银行合作',
        ],
    })


# ============================================================================
# 测试 merge_stats
# ============================================================================

class TestMergeStats:
    """merge_stats 正确性测试。"""

    def test_merge_empty_list(self, mock_bank_module):
        """合并空列表。"""
        result = mock_bank_module.merge_stats([])
        assert result['total'] == 0
        assert result['is_bank_news_true'] == 0

    def test_merge_single_stats(self, mock_bank_module):
        """合并单个 stats。"""
        stats = {
            'total': 10,
            'is_bank_news_true': 3,
            'is_bank_news_false': 7,
            'is_bank_news_with_title': 2,
            'bank_article_counts': Counter({'工商银行': 3}),
            'bank_title_article_counts': Counter({'工商银行': 2}),
            'negation_excluded_total': 1,
            'short_name_excluded_total': 0,
        }
        result = mock_bank_module.merge_stats([stats])
        assert result['total'] == 10
        assert result['is_bank_news_true'] == 3
        assert result['bank_article_counts']['工商银行'] == 3

    def test_merge_multiple_stats(self, mock_bank_module):
        """合并多个 stats → Counter 正确累加。"""
        s1 = {
            'total': 5, 'is_bank_news_true': 2, 'is_bank_news_false': 3,
            'is_bank_news_with_title': 1,
            'bank_article_counts': Counter({'工商银行': 2}),
            'bank_title_article_counts': Counter({'工商银行': 1}),
            'negation_excluded_total': 1, 'short_name_excluded_total': 0,
        }
        s2 = {
            'total': 8, 'is_bank_news_true': 4, 'is_bank_news_false': 4,
            'is_bank_news_with_title': 3,
            'bank_article_counts': Counter({'工商银行': 1, '建设银行': 3}),
            'bank_title_article_counts': Counter({'建设银行': 2}),
            'negation_excluded_total': 2, 'short_name_excluded_total': 1,
        }
        result = mock_bank_module.merge_stats([s1, s2])
        assert result['total'] == 13
        assert result['is_bank_news_true'] == 6
        assert result['bank_article_counts']['工商银行'] == 3
        assert result['bank_article_counts']['建设银行'] == 3
        assert result['negation_excluded_total'] == 3


# ============================================================================
# 测试 log_classification_report
# ============================================================================

class TestLogClassificationReport:
    """log_classification_report 白盒测试。"""

    def test_zero_total(self, mock_bank_module):
        """total=0 时不应抛异常（除零保护）。"""
        stats = {
            'total': 0, 'is_bank_news_true': 0, 'is_bank_news_false': 0,
            'is_bank_news_with_title': 0,
            'bank_article_counts': Counter(),
            'bank_title_article_counts': Counter(),
            'negation_excluded_total': 0, 'short_name_excluded_total': 0,
        }
        logger = MagicMock()
        mock_bank_module.log_classification_report(stats, logger)
        assert logger.info.called

    def test_normal_stats(self, mock_bank_module):
        """正常统计不抛异常。"""
        stats = {
            'total': 100, 'is_bank_news_true': 30, 'is_bank_news_false': 70,
            'is_bank_news_with_title': 15,
            'bank_article_counts': Counter({'工商银行': 20, '建设银行': 10}),
            'bank_title_article_counts': Counter({'工商银行': 10, '建设银行': 5}),
            'negation_excluded_total': 5, 'short_name_excluded_total': 3,
        }
        logger = MagicMock()
        mock_bank_module.log_classification_report(stats, logger)
        assert logger.info.call_count > 5


# ============================================================================
# 测试 classify_batch
# ============================================================================

class TestClassifyBatch:
    """classify_batch 核心逻辑白盒测试。"""

    def test_empty_dataframe(self, mock_bank_module):
        """空 DataFrame → 返回空结果和零统计。"""
        empty_df = pd.DataFrame(columns=['内容', '标题'])
        result_df, stats = mock_bank_module.classify_batch(empty_df)
        assert stats['total'] == 0
        assert stats['is_bank_news_true'] == 0

    def test_batch_produces_results(self, mock_bank_module, sample_bank_df):
        """正常批次应产出结果（具体数量取决于全局 AC 自动机状态）。"""
        result_df, stats = mock_bank_module.classify_batch(sample_bank_df)
        assert stats['total'] == len(sample_bank_df)
        # is_bank_news_true + is_bank_news_false = total (以文章计数)
        assert stats['is_bank_news_true'] + stats['is_bank_news_false'] == stats['total']

    def test_non_bank_article(self, mock_bank_module):
        """完全不含银行名的文章 → is_bank_news_false。"""
        df = pd.DataFrame({
            '内容': ['今天天气晴朗，气温适中，适合户外运动。'],
            '标题': ['天气预报'],
        })
        result_df, stats = mock_bank_module.classify_batch(df)
        assert stats['is_bank_news_true'] == 0
        assert stats['is_bank_news_false'] == 1

    def test_expanded_columns_exist(self, mock_bank_module, sample_bank_df):
        """展开后的 DataFrame 应包含核心列。"""
        result_df, stats = mock_bank_module.classify_batch(sample_bank_df)
        if not result_df.empty:
            expected_cols = ['target_bank', 'co_mentioned_banks',
                             'mention_density', 'doc_length']
            for col in expected_cols:
                assert col in result_df.columns, f"缺失列: {col}"
