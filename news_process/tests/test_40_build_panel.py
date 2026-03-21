"""
test_40_build_panel.py — 40_build_panel 端到端单元测试
======================================================
用合成数据模拟上游 23_bert_tone.parquet 的完整列结构，
验证 40_build_panel.py 各步骤的数据流正确性。
"""
import os
import sys
import json
import pytest
import importlib
import numpy as np
import pandas as pd

# 确保能 import 项目代码
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 以数字开头的模块名需要特殊导入
_mod_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    '40_build_panel.py'
)
_spec = importlib.util.spec_from_file_location('build_panel', _mod_path)
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)


# ============================================================================
# Fixtures: 合成上游数据
# ============================================================================

LLM_SHORTS = ['gpt5nano', 'gemini3', 'claude4h']
DICT_NAMES = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
BERT_SHORTS = ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
THREE_CLASS = {'finbert_cn', 'fin_sent_zh', 'hw2942'}


def _build_banks_info(bank_names, title_banks=None):
    """构造 matched_banks_info JSON 字符串。"""
    title_banks = title_banks or []
    info = []
    for b in bank_names:
        info.append({
            'bank_name': b,
            'in_title': b in title_banks,
            'match_count': 2
        })
    return json.dumps(info, ensure_ascii=False)


@pytest.fixture
def synthetic_df():
    """创建模拟 23_bert_tone.parquet 的 DataFrame（Firm-Document Level）。"""
    np.random.seed(42)
    n = 20

    data = {
        '日期': pd.date_range('2020-01-01', periods=n, freq='90D'),
        'target_bank': [
            '工商银行', '工商银行', '建设银行', '农业银行',
            '工商银行', '建设银行', '农业银行', '工商银行',
            '工商银行', '建设银行', '农业银行', '工商银行',
            '建设银行', '农业银行', '工商银行', '建设银行',
            '农业银行', '工商银行', '建设银行', '农业银行',
        ],
        'co_mentioned_banks': [
            '', '建设银行', '', '',
            '', '', '', '建设银行;农业银行',
            '', '', '', '',
            '', '', '', '',
            '', '', '', '',
        ],
        'target_bank_in_title': np.random.choice([0, 1], n),
        'llm_sentiment': np.random.choice(['正面', '中性', '负面'], n),
        'llm_agreement_rate': np.random.uniform(0.5, 1.0, n),
        '媒体(中文)': np.random.choice(['新浪财经', '第一财经', '澎湃新闻', '财新网'], n),
        'is_fintech_news': np.random.choice([True, False], n),
    }

    # LLM 逐模型列
    for short in LLM_SHORTS:
        data[f'{short}_sentiment'] = np.random.choice(['正面', '中性', '负面'], n)
        data[f'{short}_sentiment_confidence'] = np.random.uniform(0.5, 1.0, n)

    # 词典法列
    for d in DICT_NAMES:
        data[f'{d}_score'] = np.random.uniform(-1, 1, n)
        data[f'{d}_label'] = np.random.choice(['正面', '中性', '负面'], n)

    # BERT 列
    for b in BERT_SHORTS:
        data[f'{b}_正面'] = np.random.uniform(0, 1, n)
        data[f'{b}_负面'] = np.random.uniform(0, 1, n)
        data[f'{b}_label'] = np.random.choice(['正面', '中性', '负面'], n)
        if b in THREE_CLASS:
            data[f'{b}_中性'] = np.random.uniform(0, 1, n)

    # matched_banks_info JSON
    banks_info_list = []
    for i in range(n):
        bank_name = data['target_bank'][i]
        in_title = bool(data['target_bank_in_title'][i])
        banks_info_list.append(_build_banks_info([bank_name], [bank_name] if in_title else []))
    data['matched_banks_info'] = banks_info_list

    df = pd.DataFrame(data)

    # 计算多银行特征（与 40_build_panel.py:main() 中的逻辑一致）
    df['bank_count'] = df['co_mentioned_banks'].apply(
        lambda x: len(str(x).split(';')) + 1 if x and str(x).strip() else 1
    )
    df['is_multi_bank'] = (df['bank_count'] > 1).astype(int)
    df['ln_bank_count'] = np.log1p(df['bank_count'])
    df['in_title'] = df['target_bank_in_title'].astype(int)

    return df


# ============================================================================
# 测试: 步骤 2 — 情感编码
# ============================================================================

class TestEncoding:
    def test_discrete_encoding(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        assert 'llm_vote_score' in df.columns
        assert set(df['llm_vote_score'].unique()).issubset({-1, 0, 1})
        # 互斥性: 每行只能属于一个类别
        total = df['is_positive'] + df['is_negative'] + df['is_neutral']
        assert (total == 1).all()

    def test_continuous_encoding(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        assert df['llm_vote_cont'].between(-1, 1).all()
        for short in LLM_SHORTS:
            assert df[f'{short}_cont'].between(-1, 1).all()

    def test_per_model_score(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        for short in LLM_SHORTS:
            assert set(df[f'{short}_score'].unique()).issubset({-1, 0, 1})


# TestExplode 已移除 — explode_banks 函数已迁移至 11_news_bank.py
# 数据在测试中已直接以 Firm-Document Level 形式提供


# ============================================================================
# 测试: 步骤 4 — 时间解析
# ============================================================================

class TestTimeParser:
    def test_year_extraction(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        assert 'year' in df.columns
        assert df['year'].dtype == int


# ============================================================================
# 测试: 步骤 5 — Bank-Year 聚合
# ============================================================================

class TestAggregation:
    def test_panel_unique_keys(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        combos = panel[['target_bank', 'year']].apply(tuple, axis=1)
        assert combos.is_unique

    def test_aggregation_columns(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        required = [
            'llm_vote_tone', 'llm_vote_tone_sum', 'llm_vote_tone_std',
            'pos_frac', 'neg_frac', 'pos_count', 'neg_count',
            'n_articles', 'ln_news_coverage', 'headline_frac',
            'media_breadth', 'multi_bank_frac',
            'avg_bank_count', 'max_bank_count', 'avg_agreement_rate',
        ]
        for col in required:
            assert col in panel.columns, f"Missing: {col}"

    def test_frac_in_range(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        assert panel['pos_frac'].between(0, 1).all()
        assert panel['neg_frac'].between(0, 1).all()


# ============================================================================
# 测试: 步骤 6 — 面板平衡
# ============================================================================

class TestPanelBalancing:
    def test_balanced_shape(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        balanced = bp.balance_panel(panel)
        n_banks = balanced['target_bank'].nunique()
        n_years = balanced['year'].nunique()
        assert len(balanced) == n_banks * n_years

    def test_zero_fill_correct(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        balanced = bp.balance_panel(panel)
        zero_rows = balanced[balanced['n_articles'] == 0]
        if len(zero_rows) > 0:
            sum_cols = [c for c in zero_rows.columns if c.endswith('_sum')]
            for col in sum_cols:
                assert (zero_rows[col] == 0).all(), f"{col} not 0 for no-news"
            assert (zero_rows['pos_count'] == 0).all()

    def test_nan_preserved_for_means(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        balanced = bp.balance_panel(panel)
        zero_rows = balanced[balanced['n_articles'] == 0]
        if len(zero_rows) > 0:
            assert zero_rows['llm_vote_tone'].isna().all()
            assert zero_rows['pos_frac'].isna().all()


# ============================================================================
# 测试: 步骤 7 — 综合指标
# ============================================================================

class TestCompositeIndicators:
    def test_composite_columns_exist(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        panel = bp.balance_panel(panel)
        panel = bp.compute_composite_indicators(panel)
        expected = [
            'llm_models_avg_tone', 'llm_models_avg_tone_sum',
            'llm_models_avg_cont', 'llm_models_avg_cont_sum',
            'llm_models_avg_tone_std',
            'dict_avg_tone', 'dict_avg_tone_sum', 'dict_avg_tone_std',
            'bert_avg_pos', 'bert_avg_neg', 'bert_avg_neu',
            'bert_avg_pos_sum', 'bert_avg_neg_sum', 'bert_avg_neu_sum',
            'bert_avg_pos_std',
        ]
        for col in expected:
            assert col in panel.columns, f"Missing: {col}"


# ============================================================================
# 测试: Config 读取正确性
# ============================================================================

class TestConfigReading:
    def test_llm_models_from_config(self):
        assert bp.LLM_MODELS == ['gpt5nano', 'gemini3', 'claude4h']

    def test_bert_models_from_config(self):
        assert bp.BERT_MODELS == ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']

    def test_three_class_models(self):
        assert 'finbert_cn' in bp.THREE_CLASS_MODELS
        assert 'erlangshen' not in bp.THREE_CLASS_MODELS


# ============================================================================
# 测试: 完整 E2E 流水线
# ============================================================================

class TestEndToEnd:
    def test_full_pipeline_no_crash(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        df_exploded = df.copy()
        panel = bp.aggregate_panel(df)
        panel = bp.balance_panel(panel)
        panel = bp.compute_composite_indicators(panel)
        bp.log_diagnostics(panel, df_exploded)
        assert len(panel) > 0

    def test_column_count_reasonable(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        panel = bp.balance_panel(panel)
        panel = bp.compute_composite_indicators(panel)
        assert panel.shape[1] > 50, f"Only {panel.shape[1]} cols"
