"""
test_45_panel_export_main.py — 面板构建模块 (41-45) 端到端单元测试
======================================================
用合成数据模拟上游 23_bert_tone.parquet 的完整列结构，
验证 45_panel_export_main.py 各步骤的数据流正确性。
"""
import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

# Phase 5a: 注入 news_process 父目录, 解析 ``news_process.*``
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 2c 拆分: 45_panel_export_main.py 已变为 thin shim, body 迁到
# pipeline/panel/{encode, export, geography, runner}.py。Phase 5a 修复测试
# 导入路径, 通过 facade 把被测函数与常量整合到 ``bp`` 命名空间。
from news_process.pipeline.panel import encode as _enc  # noqa: E402
from news_process.pipeline.panel import export as _exp  # noqa: E402
from news_process.pipeline.panel import geography as _geo  # noqa: E402


class _BpFacade:
    """Phase 5a: 桥接层, 供测试以 ``bp.<x>`` 访问迁移后的函数与常量."""
    # Functions
    encode_sentiment = staticmethod(_enc.encode_sentiment)
    parse_time = staticmethod(_enc.parse_time)
    aggregate_panel = staticmethod(_enc.aggregate_panel)
    balance_panel = staticmethod(_enc.balance_panel)
    compute_composite_indicators = staticmethod(_geo.compute_composite_indicators)
    log_diagnostics = staticmethod(_exp.log_diagnostics)
    # Module-level constants (从 encode.py 透传)
    LLM_MODELS = _enc.LLM_MODELS
    BERT_MODELS = _enc.BERT_MODELS
    THREE_CLASS_MODELS = _enc.THREE_CLASS_MODELS


bp = _BpFacade()


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
        '媒体(中文)': np.random.choice(['新浪财经', '第一财经', '澎湃新闻', '财新网'], n),
        'is_fintech_news': np.random.choice([True, False], n),
    }

    # LLM 投票结果 + 逐模型列（双轨）
    for track in ['_full', '_ctx', '_title']:
        data[f'llm_sentiment{track}'] = np.random.choice(['正面', '中性', '负面'], n)
        data[f'llm_agreement_rate{track}'] = np.random.uniform(0.5, 1.0, n)
        for short in LLM_SHORTS:
            data[f'{short}_sentiment{track}'] = np.random.choice(['正面', '中性', '负面'], n)
            data[f'{short}_sentiment_confidence{track}'] = np.random.uniform(0.5, 1.0, n)

    # 词典法列（双轨）
    for d in DICT_NAMES:
        for track in ['_full', '_ctx', '_title']:
            data[f'{d}_score{track}'] = np.random.uniform(-1, 1, n)
            data[f'{d}_label{track}'] = np.random.choice(['正面', '中性', '负面'], n)

    # BERT 列（双轨）
    for b in BERT_SHORTS:
        for track in ['_full', '_ctx', '_title']:
            data[f'{b}_正面{track}'] = np.random.uniform(0, 1, n)
            data[f'{b}_负面{track}'] = np.random.uniform(0, 1, n)
            data[f'{b}_label{track}'] = np.random.choice(['正面', '中性', '负面'], n)
            if b in THREE_CLASS:
                data[f'{b}_中性{track}'] = np.random.uniform(0, 1, n)

    # matched_banks_info JSON
    banks_info_list = []
    for i in range(n):
        bank_name = data['target_bank'][i]
        in_title = bool(data['target_bank_in_title'][i])
        banks_info_list.append(_build_banks_info([bank_name], [bank_name] if in_title else []))
    data['matched_banks_info'] = banks_info_list

    # 可读性、正负面分离（双轨）
    for track in ['_full', '_ctx', '_title']:

        data[f'avg_sentence_len{track}'] = np.random.uniform(20, 80, n)
        data[f'type_token_ratio{track}'] = np.random.uniform(0.3, 0.9, n)
        data[f'char_per_word{track}'] = np.random.uniform(1.2, 2.5, n)
        data[f'pos_ratio{track}'] = np.random.uniform(0, 0.05, n)
        data[f'neg_ratio{track}'] = np.random.uniform(0, 0.05, n)

    df = pd.DataFrame(data)

    # 计算多银行特征（与 45_panel_export_main.py:main() 中的逻辑一致）
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
        for track in ['_full', '_ctx', '_title']:
            assert f'llm_vote_score{track}' in df.columns
            assert set(df[f'llm_vote_score{track}'].unique()).issubset({-1, 0, 1})
            # 互斥性: 每行只能属于一个类别
            total = df[f'is_positive{track}'] + df[f'is_negative{track}'] + df[f'is_neutral{track}']
            assert (total == 1).all()

    def test_continuous_encoding(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        for track in ['_full', '_ctx', '_title']:
            assert df[f'llm_vote_cont{track}'].between(-1, 1).all()
            for short in LLM_SHORTS:
                assert df[f'{short}_cont{track}'].between(-1, 1).all()

    def test_per_model_score(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        for track in ['_full', '_ctx', '_title']:
            for short in LLM_SHORTS:
                assert set(df[f'{short}_score{track}'].unique()).issubset({-1, 0, 1})


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
        # 双轨列使用 _full 后缀检查（_ctx 同理）
        required = [
            'llm_vote_tone_full', 'llm_vote_tone_sum_full', 'llm_vote_tone_std_full',
            'pos_frac_full', 'neg_frac_full', 'pos_count_full', 'neg_count_full',
            'n_articles', 'ln_news_coverage', 'headline_frac',
            'media_breadth', 'multi_bank_frac',
            'avg_bank_count', 'max_bank_count', 'avg_agreement_rate_full',

            # 可读性 (Loughran & McDonald 2014, Journal of Finance)
            'avg_sent_len_full', 'avg_ttr_full', 'avg_cpw_full',
            # 正/负面分离 (Berger et al. 2024, Appendix S6)
            'avg_pos_ratio_full', 'avg_neg_ratio_full',
        ]
        for col in required:
            assert col in panel.columns, f"Missing: {col}"

    def test_frac_in_range(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        for track in ['_full', '_ctx', '_title']:
            assert panel[f'pos_frac{track}'].between(0, 1).all()
            assert panel[f'neg_frac{track}'].between(0, 1).all()


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
            sum_cols = [c for c in zero_rows.columns if c.endswith('_sum') or
                        c.endswith('_sum_full') or c.endswith('_sum_ctx')]
            for col in sum_cols:
                assert (zero_rows[col] == 0).all(), f"{col} not 0 for no-news"
            assert (zero_rows['pos_count_full'] == 0).all()

    def test_nan_preserved_for_means(self, synthetic_df):
        df = bp.encode_sentiment(synthetic_df.copy())
        df = bp.parse_time(df)
        panel = bp.aggregate_panel(df)
        balanced = bp.balance_panel(panel)
        zero_rows = balanced[balanced['n_articles'] == 0]
        if len(zero_rows) > 0:
            assert zero_rows['llm_vote_tone_full'].isna().all()
            assert zero_rows['pos_frac_full'].isna().all()


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
            'llm_models_avg_tone_full', 'llm_models_avg_tone_sum_full',
            'llm_models_avg_cont_full', 'llm_models_avg_cont_sum_full',
            'llm_models_avg_tone_std_full',
            'dict_avg_tone_full', 'dict_avg_tone_sum_full', 'dict_avg_tone_std_full',
            'bert_avg_pos_full', 'bert_avg_neg_full', 'bert_avg_neu_full',
            'bert_avg_pos_sum_full', 'bert_avg_neg_sum_full', 'bert_avg_neu_sum_full',
            'bert_avg_pos_std_full',
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
