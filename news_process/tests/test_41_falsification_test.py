"""
test_41_falsification_test.py — 伪造检验单元测试
=================================================

使用合成数据验证 41_falsification_test.py 的核心逻辑:
  1. Anti-join 正确性
  2. 恒等式 all_n_articles == n_articles + nf_n_articles
  3. fintech_share ∈ [0, 1]
  4. 合并后不丢失面板列
  5. 零新闻行的对照变量 = 0
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# 确保可以导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from importlib import import_module
mod = import_module('41_falsification_test')


# ============================================================================
# Fixtures: 合成数据
# ============================================================================

@pytest.fixture
def synthetic_full():
    """全量银行新闻 (模拟 12_fintech_news_full.parquet)。

    共 10 条记录:
      - 4 条 is_fintech_news=True (银行A: 3条, 银行B: 1条)
      - 6 条 is_fintech_news=False (银行A: 2条, 银行B: 3条, 银行C: 1条)
    """
    return pd.DataFrame({
        'target_bank': ['银行A'] * 5 + ['银行B'] * 4 + ['银行C'],
        '标题': [
            'A金融科技1', 'A金融科技2', 'A金融科技3', 'A普通新闻1', 'A普通新闻2',
            'B金融科技1', 'B普通新闻1', 'B普通新闻2', 'B普通新闻3',
            'C普通新闻1'
        ],
        '日期': [
            '2023-01-15', '2023-06-20', '2024-03-10', '2023-02-01', '2024-01-05',
            '2023-07-01', '2023-08-15', '2024-02-20', '2024-05-01',
            '2024-06-01'
        ],
        'is_fintech_news': [
            True, True, True, False, False,
            True, False, False, False,
            False
        ],
        'target_bank_in_title': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        '媒体(中文)': [
            '经济日报', '金融时报', '经济日报', '人民日报', '新华社',
            '证券时报', '第一财经', '经济观察报', '第一财经',
            '新华社'
        ],
        '内容': ['内容'] * 10,
    })


@pytest.fixture
def synthetic_panel_articles():
    """面板文章 (模拟 40_article_bank_level.parquet)。

    只有 3 条 (对应 full 中的 fintech 文章, 但银行B的1条被LLM拒绝):
      - 银行A: 3条通过
      - 银行B: 0条通过 (B金融科技1 被LLM拒绝)
    """
    return pd.DataFrame({
        'target_bank': ['银行A', '银行A', '银行A'],
        '标题': ['A金融科技1', 'A金融科技2', 'A金融科技3'],
        '日期': pd.to_datetime(['2023-01-15', '2023-06-20', '2024-03-10']),
        '内容': ['内容'] * 3,
        'llm_sentiment_full': ['正面', '中性', '负面'],
    })


@pytest.fixture
def synthetic_panel():
    """已有面板 (模拟 40_panel_yearly.parquet)。

    银行A: 2023 (2篇), 2024 (1篇)
    银行B: 2023 (0篇), 2024 (0篇)  -- B金融科技1 被LLM拒绝
    银行C: 2023 (0篇), 2024 (0篇)  -- 无 fintech 文章
    """
    return pd.DataFrame({
        'target_bank': ['银行A', '银行A', '银行B', '银行B', '银行C', '银行C'],
        'year': [2023, 2024, 2023, 2024, 2023, 2024],
        'n_articles': [2, 1, 0, 0, 0, 0],
        'llm_vote_tone_full': [0.5, -0.3, np.nan, np.nan, np.nan, np.nan],
        'media_breadth': [1.1, 0.7, 0.0, 0.0, 0.0, 0.0],
    })


# ============================================================================
# Tests
# ============================================================================

class TestAntiJoin:
    """Test 2: Anti-join 正确性。"""

    def test_panel_articles_excluded(self, synthetic_full, synthetic_panel_articles):
        """面板文章不出现在 non-fintech 组。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)

        # 面板中的3篇 (银行A的3篇fintech) 不应出现
        for title in ['A金融科技1', 'A金融科技2', 'A金融科技3']:
            assert title not in df_nf['标题'].values, \
                f"面板文章 '{title}' 不应出现在 non-fintech 组"

    def test_llm_rejected_in_nf(self, synthetic_full, synthetic_panel_articles):
        """LLM 拒绝的文章 (B金融科技1) 应在 non-fintech 组。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)

        # B金融科技1 在 full 中 is_fintech=True, 但不在面板中 → 应在 nf
        assert 'B金融科技1' in df_nf['标题'].values, \
            "LLM拒绝的文章 'B金融科技1' 应归入 non-fintech 组"

    def test_count_consistency(self, synthetic_full, synthetic_panel_articles):
        """anti-join 数量一致性。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        # full=10, panel=3, nf 应=7
        assert len(df_nf) == 7


class TestAggregation:
    """Test 3-5: 聚合与合并。"""

    def test_identity(self, synthetic_full, synthetic_panel_articles, synthetic_panel):
        """恒等式 all_n_articles == n_articles + nf_n_articles。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        panel = mod.merge_to_panel(synthetic_panel.copy(), nf_agg)

        assert (panel['all_n_articles'] == panel['n_articles'] + panel['nf_n_articles']).all(), \
            "恒等式 all = fintech + non-fintech 不成立"

    def test_fintech_share_range(self, synthetic_full, synthetic_panel_articles, synthetic_panel):
        """fintech_share ∈ [0, 1]。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        panel = mod.merge_to_panel(synthetic_panel.copy(), nf_agg)

        assert (panel['fintech_share'] >= 0).all(), "fintech_share < 0"
        assert (panel['fintech_share'] <= 1).all(), "fintech_share > 1"

    def test_no_column_loss(self, synthetic_full, synthetic_panel_articles, synthetic_panel):
        """合并后不丢失已有面板列。"""
        original_cols = set(synthetic_panel.columns)
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        panel = mod.merge_to_panel(synthetic_panel.copy(), nf_agg)

        for col in original_cols:
            assert col in panel.columns, f"原面板列 '{col}' 丢失"

    def test_zero_news_fill(self, synthetic_full, synthetic_panel_articles, synthetic_panel):
        """零新闻行的对照变量应为 0。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        panel = mod.merge_to_panel(synthetic_panel.copy(), nf_agg)

        # 银行C 2023年在 full 中无记录 → nf_n_articles 应为 0
        bank_c_2023 = panel[
            (panel['target_bank'] == '银行C') & (panel['year'] == 2023)
        ]
        if len(bank_c_2023) > 0:
            assert bank_c_2023['nf_n_articles'].iloc[0] == 0, \
                "零新闻行的 nf_n_articles 应为 0"

    def test_fintech_share_zero_division(self, synthetic_full, synthetic_panel_articles, synthetic_panel):
        """all_n_articles=0 时 fintech_share 不应为 NaN。"""
        df_nf = mod.build_non_fintech(synthetic_full, synthetic_panel_articles)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        panel = mod.merge_to_panel(synthetic_panel.copy(), nf_agg)

        zero_total = panel[panel['all_n_articles'] == 0]
        if len(zero_total) > 0:
            assert not zero_total['fintech_share'].isna().any(), \
                "all_n_articles=0 时 fintech_share 不应为 NaN"
            assert (zero_total['fintech_share'] == 0).all(), \
                "all_n_articles=0 时 fintech_share 应为 0"
