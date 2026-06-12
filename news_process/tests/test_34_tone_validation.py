"""
tests/test_34_tone_validation.py — 34_tone_validation.py 纯函数测试
====================================================================

测试情感分析三角验证中可独立导入的纯函数。
由于 34_tone_validation.py 在 import 时会加载配置，采用复刻策略。
"""

import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 复刻纯函数（避免 import 34_tone_validation 时触发全局初始化）
# ============================================================================

SENTIMENT_MAP = {'正面': 1, '中性': 0, '负面': -1}
SENTIMENT_MAP_REVERSE = {1: '正面', 0: '中性', -1: '负面'}


def label_to_numeric(series: pd.Series) -> pd.Series:
    """将情感标签转为数值：正面=+1, 中性=0, 负面=-1。

    audit-fixes 2026-05-29 (M-tv): 与生产 validation/tone_validation.py 对齐 —
    未映射/缺失保留 NaN, 不再 fillna(0) (失败≠中性)。生产行为另由
    test_audit_fixes_20260529.py 直接 import 守卫。
    """
    return series.map(SENTIMENT_MAP).astype(float)


def discover_sentiment_columns(df: pd.DataFrame) -> dict:
    """自动发现 DataFrame 中的情感分析输出列。"""
    columns = list(df.columns)
    result = {'words': {}, 'bert': {}, 'llm': {}}

    score_suffix = '_score'
    label_suffix = '_label'
    sentiment_suffix = '_sentiment'
    confidence_suffix = '_confidence'

    for col in columns:
        if col.endswith(score_suffix):
            dict_name = col[:-len(score_suffix)]
            label_col = f'{dict_name}{label_suffix}'
            if label_col in columns:
                result['words'][dict_name] = {'score': col, 'label': label_col}

    for col in columns:
        if col.endswith(sentiment_suffix):
            short_name = col[:-len(sentiment_suffix)]
            # 置信度列查找：优先 _sentiment_confidence 模式（21_tone_llms.py 输出格式）
            # 回退到 _confidence 模式以兼容旧数据
            conf_col_primary = f'{short_name}_sentiment{confidence_suffix}'
            conf_col_fallback = f'{short_name}{confidence_suffix}'
            if conf_col_primary in columns:
                conf_col = conf_col_primary
            elif conf_col_fallback in columns:
                conf_col = conf_col_fallback
            else:
                conf_col = None
            result['llm'][short_name] = {
                'sentiment': col,
                'confidence': conf_col,
            }

    words_names = set(result['words'].keys())
    llm_names = set(result['llm'].keys())
    for col in columns:
        if col.endswith(label_suffix):
            name = col[:-len(label_suffix)]
            if name not in words_names and name not in llm_names:
                probs = {}
                for c in columns:
                    if c.startswith(f'{name}_') and c != col:
                        prob_label = c[len(f'{name}_'):]
                        if prob_label not in ('label', 'score', 'sentiment', 'confidence'):
                            probs[prob_label] = c
                result['bert'][name] = {'label': col, 'probs': probs}

    return result


def compute_spearman_matrix(df_numeric: pd.DataFrame) -> pd.DataFrame:
    return df_numeric.corr(method='spearman').round(4)


def compute_pearson_matrix(df_numeric: pd.DataFrame) -> pd.DataFrame:
    return df_numeric.corr(method='pearson').round(4)


def compute_cronbachs_alpha(df_numeric: pd.DataFrame) -> float:
    df_clean = df_numeric.dropna()
    if len(df_clean) < 10 or df_clean.shape[1] < 2:
        return np.nan

    k = df_clean.shape[1]
    item_vars = df_clean.var(axis=0, ddof=1)
    total_var = df_clean.sum(axis=1).var(ddof=1)

    if total_var == 0:
        return 1.0

    alpha = (k / (k - 1)) * (1 - item_vars.sum() / total_var)
    return round(alpha, 4)


def compute_label_agreement_rate(labels_df: pd.DataFrame) -> dict:
    valid = labels_df.dropna(how='any')
    n = len(valid)
    if n == 0:
        return {'full_agreement_rate': 0.0, 'majority_agreement_rate': 0.0,
                'n_samples': 0}

    n_methods = valid.shape[1]
    nunique_per_row = valid.nunique(axis=1)
    full_agree = int((nunique_per_row == 1).sum())
    mode_counts = valid.apply(lambda row: row.value_counts().iloc[0], axis=1)
    # audit-fixes 2026-05-29 (M-tv): 严格多数 > n/2 (与生产对齐; 旧 >= 把偶数
    # 方法数的 k/2-k/2 平局误算为多数)
    majority_agree = int((mode_counts > n_methods / 2).sum())

    return {
        'full_agreement_rate': round(full_agree / n, 4),
        'majority_agreement_rate': round(majority_agree / n, 4),
        'n_samples': n,
        'n_methods': n_methods,
    }


def majority_vote(labels_df: pd.DataFrame) -> pd.Series:
    def _vote(row):
        values = row.dropna().tolist()
        if not values:
            return '中性'
        counter = Counter(values)
        max_count = counter.most_common(1)[0][1]
        candidates = [k for k, v in counter.items() if v == max_count]
        for pref in ['中性', '负面', '正面']:
            if pref in candidates:
                return pref
        return candidates[0]

    return labels_df.apply(_vote, axis=1)


def weighted_average_score(scores_df: pd.DataFrame,
                           weights: dict = None) -> pd.Series:
    if weights is None:
        return scores_df.mean(axis=1)

    total_weight = sum(weights.get(col, 1.0) for col in scores_df.columns)
    weighted_sum = sum(
        scores_df[col] * weights.get(col, 1.0)
        for col in scores_df.columns
    )
    return weighted_sum / total_weight


# ============================================================================
# discover_sentiment_columns 测试
# ============================================================================

class TestDiscoverSentimentColumns:
    """测试情感列自动发现。"""

    def test_discover_words_columns(self):
        """应正确识别词典法列。"""
        df = pd.DataFrame({
            'jiang_2021_score': [0.5],
            'jiang_2021_label': ['正面'],
            'yao_2021_score': [0.3],
            'yao_2021_label': ['中性'],
        })
        result = discover_sentiment_columns(df)
        assert len(result['words']) == 2
        assert 'jiang_2021' in result['words']
        assert 'yao_2021' in result['words']

    def test_discover_llm_columns(self):
        """应正确识别 LLM 列（旧格式: _confidence 回退）。"""
        df = pd.DataFrame({
            'gpt4_sentiment': ['正面'],
            'gpt4_confidence': [0.9],
            'claude_sentiment': ['负面'],
        })
        result = discover_sentiment_columns(df)
        assert len(result['llm']) == 2
        assert result['llm']['gpt4']['confidence'] == 'gpt4_confidence'
        assert result['llm']['claude']['confidence'] is None

    def test_discover_llm_confidence_new_format(self):
        """应优先匹配新格式 _sentiment_confidence 列名（21_tone_llms.py 输出）。"""
        df = pd.DataFrame({
            'gpt54nano_sentiment': ['正面'],
            'gpt54nano_sentiment_confidence': [0.92],
            'gemini31111_sentiment': ['中性'],
            'gemini31111_sentiment_confidence': [0.78],
        })
        result = discover_sentiment_columns(df)
        assert result['llm']['gpt54nano']['confidence'] == 'gpt54nano_sentiment_confidence'
        assert result['llm']['gemini31111']['confidence'] == 'gemini31111_sentiment_confidence'

    def test_discover_llm_confidence_priority(self):
        """新旧格式共存时应优先选择新格式 _sentiment_confidence。"""
        df = pd.DataFrame({
            'model_a_sentiment': ['负面'],
            'model_a_sentiment_confidence': [0.85],  # 新格式（应优先）
            'model_a_confidence': [0.60],             # 旧格式
        })
        result = discover_sentiment_columns(df)
        assert result['llm']['model_a']['confidence'] == 'model_a_sentiment_confidence'

    def test_discover_bert_columns(self):
        """应正确识别 BERT 列（排除 words 和 llm 已识别的）。"""
        df = pd.DataFrame({
            'finbert_cn_label': ['正面'],
            'finbert_cn_正面': [0.8],
            'finbert_cn_负面': [0.1],
            'finbert_cn_中性': [0.1],
        })
        result = discover_sentiment_columns(df)
        assert len(result['bert']) == 1
        assert 'finbert_cn' in result['bert']
        assert '正面' in result['bert']['finbert_cn']['probs']

    def test_mixed_columns(self):
        """混合列应正确分类。"""
        df = pd.DataFrame({
            'jiang_2021_score': [0.5],
            'jiang_2021_label': ['正面'],
            'finbert_cn_label': ['中性'],
            'gpt4_sentiment': ['负面'],
        })
        result = discover_sentiment_columns(df)
        assert len(result['words']) == 1
        assert len(result['bert']) == 1
        assert len(result['llm']) == 1

    def test_empty_dataframe(self):
        """空 DataFrame 应返回空字典。"""
        df = pd.DataFrame()
        result = discover_sentiment_columns(df)
        assert result == {'words': {}, 'bert': {}, 'llm': {}}

    def test_no_sentiment_columns(self):
        """无情感列应返回空字典。"""
        df = pd.DataFrame({'标题': ['新闻A'], '内容': ['文本']})
        result = discover_sentiment_columns(df)
        assert result['words'] == {}
        assert result['bert'] == {}
        assert result['llm'] == {}

    def test_score_without_label_excluded(self):
        """只有 _score 没有对应 _label 的列不应被识别为词典法。"""
        df = pd.DataFrame({
            'orphan_score': [0.5],
        })
        result = discover_sentiment_columns(df)
        assert len(result['words']) == 0


# ============================================================================
# label_to_numeric 测试
# ============================================================================

class TestLabelToNumeric:
    """测试标签数值化转换。"""

    def test_standard_labels(self):
        s = pd.Series(['正面', '中性', '负面'])
        result = label_to_numeric(s)
        assert list(result) == [1.0, 0.0, -1.0]

    def test_unknown_label(self):
        """audit-fixes 2026-05-29 (M-tv): 未知/缺失标签 → NaN (非 0), 不当作中性。"""
        s = pd.Series(['正面', '未知', None])
        result = label_to_numeric(s)
        assert result.iloc[0] == 1.0
        assert pd.isna(result.iloc[1])
        assert pd.isna(result.iloc[2])

    def test_all_positive(self):
        s = pd.Series(['正面', '正面', '正面'])
        result = label_to_numeric(s)
        assert all(v == 1.0 for v in result)

    def test_empty_series(self):
        s = pd.Series([], dtype=str)
        result = label_to_numeric(s)
        assert len(result) == 0


# ============================================================================
# compute_cronbachs_alpha 测试
# ============================================================================

class TestComputeCronbachsAlpha:
    """测试 Cronbach's Alpha 计算。"""

    def test_perfect_consistency(self):
        """完全一致的数据应返回 1.0。"""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'b': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        })
        alpha = compute_cronbachs_alpha(df)
        assert alpha == 1.0

    def test_high_consistency(self):
        """高度一致的数据应返回高 alpha。"""
        np.random.seed(42)
        base = np.arange(50, dtype=float)
        df = pd.DataFrame({
            'a': base + np.random.normal(0, 0.1, 50),
            'b': base + np.random.normal(0, 0.1, 50),
            'c': base + np.random.normal(0, 0.1, 50),
        })
        alpha = compute_cronbachs_alpha(df)
        assert alpha > 0.95

    def test_too_few_samples(self):
        """样本数不足 10 应返回 NaN。"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [1, 2, 3]})
        alpha = compute_cronbachs_alpha(df)
        assert np.isnan(alpha)

    def test_single_column(self):
        """少于 2 列应返回 NaN。"""
        df = pd.DataFrame({'a': list(range(20))})
        alpha = compute_cronbachs_alpha(df)
        assert np.isnan(alpha)

    def test_constant_columns(self):
        """常量列（zero variance）应返回 1.0。"""
        df = pd.DataFrame({
            'a': [5] * 15,
            'b': [5] * 15,
        })
        alpha = compute_cronbachs_alpha(df)
        assert alpha == 1.0

    def test_negative_correlation(self):
        """反向相关的列应得到低/负 alpha。"""
        # 使用不完全对称的反向数据（sum 不是常量），使 total_var != 0
        np.random.seed(123)
        a = np.arange(20, dtype=float)
        b = 20 - a + np.random.normal(0, 2, 20)  # 加噪声使 sum 非常量
        df = pd.DataFrame({'a': a, 'b': b})
        alpha = compute_cronbachs_alpha(df)
        assert alpha < 0.5

    def test_with_nan_rows(self):
        """含 NaN 的行应被 dropna 后正常处理。"""
        data = list(range(15))
        df = pd.DataFrame({
            'a': data,
            'b': data,
        })
        df.loc[0, 'a'] = np.nan  # 一行 NaN
        alpha = compute_cronbachs_alpha(df)
        assert alpha == 1.0  # 删掉一行后仍然完全一致


# ============================================================================
# compute_label_agreement_rate 测试
# ============================================================================

class TestComputeLabelAgreementRate:
    """测试标签一致率计算。"""

    def test_full_agreement(self):
        """所有行完全一致应返回 1.0。"""
        df = pd.DataFrame({
            'M1': ['正面', '负面', '中性'],
            'M2': ['正面', '负面', '中性'],
            'M3': ['正面', '负面', '中性'],
        })
        result = compute_label_agreement_rate(df)
        assert result['full_agreement_rate'] == 1.0
        assert result['majority_agreement_rate'] == 1.0

    def test_no_agreement(self):
        """完全不一致（三方平局）。"""
        df = pd.DataFrame({
            'M1': ['正面', '正面'],
            'M2': ['负面', '负面'],
            'M3': ['中性', '中性'],
        })
        result = compute_label_agreement_rate(df)
        assert result['full_agreement_rate'] == 0.0
        # 多数一致率也为 0.0（每行最高频次=1, 严格多数判定 1 > 3/2=1.5 为 False）
        # （原注释误写"仍为 1.0", 与下行断言 == 0.0 矛盾, 已更正）
        assert result['majority_agreement_rate'] == 0.0

    def test_majority_partial(self):
        """2/3 一致算多数一致。"""
        df = pd.DataFrame({
            'M1': ['正面'],
            'M2': ['正面'],
            'M3': ['负面'],
        })
        result = compute_label_agreement_rate(df)
        assert result['full_agreement_rate'] == 0.0
        assert result['majority_agreement_rate'] == 1.0

    def test_empty_dataframe(self):
        """空 DataFrame 应返回 0。"""
        df = pd.DataFrame({'M1': [], 'M2': []})
        result = compute_label_agreement_rate(df)
        assert result['full_agreement_rate'] == 0.0
        assert result['n_samples'] == 0

    def test_with_nan(self):
        """含 NaN 的行应被排除。"""
        df = pd.DataFrame({
            'M1': ['正面', None],
            'M2': ['正面', '负面'],
        })
        result = compute_label_agreement_rate(df)
        assert result['n_samples'] == 1
        assert result['full_agreement_rate'] == 1.0

    def test_two_methods(self):
        """两个方法的情况。"""
        df = pd.DataFrame({
            'M1': ['正面', '正面', '负面', '中性'],
            'M2': ['正面', '负面', '负面', '中性'],
        })
        result = compute_label_agreement_rate(df)
        assert result['n_methods'] == 2
        # 完全一致：row 0, 2, 3 → 3/4 = 0.75
        assert result['full_agreement_rate'] == 0.75


# ============================================================================
# majority_vote 测试
# ============================================================================

class TestMajorityVote:
    """测试多数投票合成。"""

    def test_clear_majority(self):
        """明确多数应返回多数标签。"""
        df = pd.DataFrame({
            'M1': ['正面', '正面', '负面'],
            'M2': ['正面', '负面', '负面'],
            'M3': ['正面', '正面', '负面'],
        })
        result = majority_vote(df)
        assert result.iloc[0] == '正面'
        assert result.iloc[2] == '负面'

    def test_tie_conservative(self):
        """平局应按保守策略：中性 > 负面 > 正面。"""
        df = pd.DataFrame({
            'M1': ['正面'],
            'M2': ['负面'],
        })
        result = majority_vote(df)
        assert result.iloc[0] == '负面'  # 保守策略：中性>负面>正面

    def test_tie_with_neutral(self):
        """平局有中性时应选中性。"""
        df = pd.DataFrame({
            'M1': ['正面'],
            'M2': ['中性'],
        })
        result = majority_vote(df)
        assert result.iloc[0] == '中性'

    def test_three_way_tie(self):
        """三方平局应选中性。"""
        df = pd.DataFrame({
            'M1': ['正面'],
            'M2': ['负面'],
            'M3': ['中性'],
        })
        result = majority_vote(df)
        assert result.iloc[0] == '中性'

    def test_all_nan(self):
        """全 NaN 应返回中性。"""
        df = pd.DataFrame({
            'M1': [None],
            'M2': [None],
        })
        result = majority_vote(df)
        assert result.iloc[0] == '中性'

    def test_single_method(self):
        """单方法应直接返回其标签。"""
        df = pd.DataFrame({'M1': ['负面', '正面', '中性']})
        result = majority_vote(df)
        assert list(result) == ['负面', '正面', '中性']


# ============================================================================
# weighted_average_score 测试
# ============================================================================

class TestWeightedAverageScore:
    """测试加权平均得分。"""

    def test_equal_weights(self):
        """等权应为算术平均。"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0],
            'b': [3.0, 2.0, 1.0],
        })
        result = weighted_average_score(df)
        assert list(result) == [2.0, 2.0, 2.0]

    def test_custom_weights(self):
        """自定义权重应正确加权。"""
        df = pd.DataFrame({
            'a': [1.0],
            'b': [3.0],
        })
        result = weighted_average_score(df, weights={'a': 1.0, 'b': 3.0})
        # (1*1 + 3*3) / (1+3) = 10/4 = 2.5
        assert abs(result.iloc[0] - 2.5) < 0.001

    def test_weight_missing_column(self):
        """权重中缺少的列应使用默认权重 1.0。"""
        df = pd.DataFrame({
            'a': [2.0],
            'b': [4.0],
        })
        result = weighted_average_score(df, weights={'a': 2.0})
        # (2*2 + 4*1) / (2+1) = 8/3 ≈ 2.667
        assert abs(result.iloc[0] - 8 / 3) < 0.001

    def test_all_zeros(self):
        """全零应返回零。"""
        df = pd.DataFrame({'a': [0.0], 'b': [0.0]})
        result = weighted_average_score(df)
        assert result.iloc[0] == 0.0


# ============================================================================
# compute_spearman_matrix / compute_pearson_matrix 测试
# ============================================================================

class TestCorrelationMatrices:
    """测试相关矩阵计算。"""

    def test_spearman_perfect_monotonic(self):
        """完美单调关系应返回 1.0 Spearman。"""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [2, 4, 6, 8, 10],
        })
        corr = compute_spearman_matrix(df)
        assert corr.loc['a', 'b'] == 1.0

    def test_pearson_perfect_linear(self):
        """完美线性关系应返回 1.0 Pearson。"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0],
            'b': [2.0, 4.0, 6.0, 8.0, 10.0],
        })
        corr = compute_pearson_matrix(df)
        assert corr.loc['a', 'b'] == 1.0

    def test_spearman_inverse(self):
        """完美反向单调应返回 -1.0。"""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [5, 4, 3, 2, 1],
        })
        corr = compute_spearman_matrix(df)
        assert corr.loc['a', 'b'] == -1.0

    def test_diagonal_is_one(self):
        """对角线应为 1.0。"""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [5, 3, 1, 4, 2],
        })
        corr = compute_spearman_matrix(df)
        assert corr.loc['a', 'a'] == 1.0
        assert corr.loc['b', 'b'] == 1.0

    def test_matrix_shape(self):
        """3 列应生成 3×3 矩阵。"""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [5, 4, 3, 2, 1],
            'c': [1, 3, 2, 5, 4],
        })
        corr = compute_pearson_matrix(df)
        assert corr.shape == (3, 3)
