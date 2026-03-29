"""
tests/test_12_news_fintech.py — 12_news_fintech.py 白盒测试
============================================================

覆盖维度：
  - classify_batch 分支覆盖：空DataFrame、阈值边界、标题匹配路径
  - merge_stats Counter 累加正确性
  - log_classification_report 除零保护
  - keyword_details JSON 序列化
"""

import pytest
import pandas as pd
from collections import Counter
from unittest.mock import MagicMock


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fintech_module():
    """导入 12_news_fintech 模块。"""
    import importlib
    return importlib.import_module('12_news_fintech')


@pytest.fixture
def fintech_sample_df():
    """创建包含金融科技关键词的 mock DataFrame。"""
    return pd.DataFrame({
        '内容': [
            '工商银行推出人工智能和大数据驱动的智能风控平台。'
            '该平台结合了机器学习和云计算技术，实现了数字化转型。'
            '工商银行表示区块链和物联网也将在新阶段引入。',

            '今天天气晴朗，适合出行。气温20度。没有金融科技内容。',

            '建设银行发布数字支付报告。仅提到了数字支付一个关键词。',
        ],
        '标题': [
            '工商银行金融科技创新',
            '天气预报',
            '建行数字支付',
        ],
    })


# ============================================================================
# 测试 merge_stats
# ============================================================================

class TestFintechMergeStats:
    """merge_stats 正确性测试。"""

    def test_merge_empty_list(self, fintech_module):
        result = fintech_module.merge_stats([])
        assert result['total'] == 0

    def test_merge_multiple(self, fintech_module):
        s1 = {
            'total': 10, 'is_fintech_news_true': 5, 'is_fintech_news_false': 5,
            'is_fintech_news_with_title': 3,
            'keyword_article_counts': Counter({'人工智能': 3, '大数据': 2}),
            'keyword_title_article_counts': Counter({'人工智能': 1}),
        }
        s2 = {
            'total': 8, 'is_fintech_news_true': 2, 'is_fintech_news_false': 6,
            'is_fintech_news_with_title': 1,
            'keyword_article_counts': Counter({'大数据': 3, '云计算': 1}),
            'keyword_title_article_counts': Counter({'大数据': 1}),
        }
        result = fintech_module.merge_stats([s1, s2])
        assert result['total'] == 18
        assert result['is_fintech_news_true'] == 7
        assert result['keyword_article_counts']['大数据'] == 5

    def test_merge_preserves_with_title_count(self, fintech_module):
        s1 = {
            'total': 5, 'is_fintech_news_true': 2, 'is_fintech_news_false': 3,
            'is_fintech_news_with_title': 2,
            'keyword_article_counts': Counter(),
            'keyword_title_article_counts': Counter(),
        }
        result = fintech_module.merge_stats([s1])
        assert result['is_fintech_news_with_title'] == 2


# ============================================================================
# 测试 log_classification_report
# ============================================================================

class TestFintechLogReport:
    """log_classification_report 白盒测试。"""

    def test_zero_total(self, fintech_module):
        stats = {
            'total': 0, 'is_fintech_news_true': 0, 'is_fintech_news_false': 0,
            'is_fintech_news_with_title': 0,
            'keyword_article_counts': Counter(),
            'keyword_title_article_counts': Counter(),
        }
        logger = MagicMock()
        fintech_module.log_classification_report(stats, logger)
        assert logger.info.called

    def test_normal_report(self, fintech_module):
        stats = {
            'total': 50, 'is_fintech_news_true': 20, 'is_fintech_news_false': 30,
            'is_fintech_news_with_title': 10,
            'keyword_article_counts': Counter({'人工智能': 15, '大数据': 10}),
            'keyword_title_article_counts': Counter({'人工智能': 5}),
        }
        logger = MagicMock()
        fintech_module.log_classification_report(stats, logger)
        assert logger.info.call_count > 3


# ============================================================================
# 测试 classify_batch
# ============================================================================

class TestFintechClassifyBatch:
    """classify_batch 核心逻辑白盒测试。"""

    def test_empty_dataframe(self, fintech_module):
        empty_df = pd.DataFrame(columns=['内容', '标题'])
        result_df, stats = fintech_module.classify_batch(empty_df)
        assert stats['total'] == 0
        assert result_df.empty

    def test_batch_processes_normally(self, fintech_module, fintech_sample_df):
        result_df, stats = fintech_module.classify_batch(fintech_sample_df)
        assert stats['total'] == len(fintech_sample_df)
        assert 'is_fintech_news' in result_df.columns
        assert 'fintech_keyword_details' in result_df.columns

    def test_non_fintech_article(self, fintech_module):
        df = pd.DataFrame({
            '内容': ['今天天气晴朗，气温适中。没有任何技术内容。'],
            '标题': ['天气预报'],
        })
        result_df, stats = fintech_module.classify_batch(df)
        assert stats['is_fintech_news_true'] == 0
        assert stats['is_fintech_news_false'] == 1

    def test_output_columns_complete(self, fintech_module, fintech_sample_df):
        result_df, _ = fintech_module.classify_batch(fintech_sample_df)
        expected_cols = [
            'is_fintech_news', 'fintech_total_count', 'fintech_upper_count',
            'fintech_lower_count', 'fintech_in_title',
            'fintech_distinct_keywords', 'fintech_keyword_details',
        ]
        for col in expected_cols:
            assert col in result_df.columns

    def test_keyword_details_json_valid(self, fintech_module, fintech_sample_df):
        """keyword_details 应为有效 JSON 字符串。"""
        import json
        result_df, _ = fintech_module.classify_batch(fintech_sample_df)
        for details_str in result_df['fintech_keyword_details']:
            if details_str:
                parsed = json.loads(details_str)
                assert isinstance(parsed, list)

    def test_stats_consistency(self, fintech_module, fintech_sample_df):
        """统计量一致性：true + false = total。"""
        _, stats = fintech_module.classify_batch(fintech_sample_df)
        assert stats['is_fintech_news_true'] + stats['is_fintech_news_false'] == stats['total']
