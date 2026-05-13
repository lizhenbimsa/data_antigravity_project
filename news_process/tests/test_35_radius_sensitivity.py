"""
tests/test_35_radius_sensitivity.py — 35_radius_sensitivity.py 白盒测试
=======================================================================

覆盖维度：
  - compute_label_agreement: 完全一致/不一致/空列表/长度不等
  - compute_cohens_kappa: 完美一致/随机一致/空输入/单标签集
  - _score_to_label: 阈值边界精确测试
  - _compute_sentiment_with_rules: 否定词翻转/程度词/转折词/句末重置
"""

import pytest

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sensitivity_module():
    """导入 35 模块（Phase 7b 后规范包路径）。"""
    # Phase 7b: body 已迁至 news_process.validation.radius_sensitivity,
    # 旧 ``importlib.import_module('35_radius_sensitivity')`` 现仅返回 thin shim,
    # 直接走规范 import 即可拿到全部内部函数与模块级常量。
    import os
    import sys
    _PROJECT_PARENT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if _PROJECT_PARENT not in sys.path:
        sys.path.insert(0, _PROJECT_PARENT)
    from news_process.validation import radius_sensitivity
    return radius_sensitivity


# ============================================================================
# 测试 compute_label_agreement
# ============================================================================

class TestComputeLabelAgreement:
    """compute_label_agreement 白盒测试。"""

    def test_perfect_agreement(self, sensitivity_module):
        a = ['正面', '中性', '负面', '正面']
        b = ['正面', '中性', '负面', '正面']
        assert sensitivity_module.compute_label_agreement(a, b) == 1.0

    def test_zero_agreement(self, sensitivity_module):
        a = ['正面', '中性', '负面']
        b = ['负面', '正面', '中性']
        assert sensitivity_module.compute_label_agreement(a, b) == 0.0

    def test_partial_agreement(self, sensitivity_module):
        a = ['正面', '中性', '负面', '正面']
        b = ['正面', '负面', '负面', '中性']
        assert sensitivity_module.compute_label_agreement(a, b) == 0.5

    def test_empty_lists(self, sensitivity_module):
        assert sensitivity_module.compute_label_agreement([], []) == 0.0

    def test_unequal_length(self, sensitivity_module):
        a = ['正面', '中性']
        b = ['正面']
        assert sensitivity_module.compute_label_agreement(a, b) == 0.0


# ============================================================================
# 测试 compute_cohens_kappa
# ============================================================================

class TestComputeCohensKappa:
    """compute_cohens_kappa 白盒测试。"""

    def test_perfect_agreement(self, sensitivity_module):
        a = ['正面', '中性', '负面', '正面', '负面']
        b = ['正面', '中性', '负面', '正面', '负面']
        kappa = sensitivity_module.compute_cohens_kappa(a, b)
        assert kappa == 1.0

    def test_empty_input(self, sensitivity_module):
        assert sensitivity_module.compute_cohens_kappa([], []) == 0.0

    def test_moderate_agreement(self, sensitivity_module):
        """部分一致 → 0 < κ < 1。"""
        a = ['正面', '正面', '中性', '负面', '正面']
        b = ['正面', '中性', '中性', '负面', '负面']
        kappa = sensitivity_module.compute_cohens_kappa(a, b)
        assert 0.0 < kappa < 1.0

    def test_single_category(self, sensitivity_module):
        """所有标签相同时 p_e=1.0 → κ=1.0 (特殊处理)。"""
        a = ['中性', '中性', '中性']
        b = ['中性', '中性', '中性']
        kappa = sensitivity_module.compute_cohens_kappa(a, b)
        assert kappa == 1.0

    def test_symmetric(self, sensitivity_module):
        """κ 应具有对称性。"""
        a = ['正面', '中性', '负面']
        b = ['中性', '正面', '负面']
        k1 = sensitivity_module.compute_cohens_kappa(a, b)
        k2 = sensitivity_module.compute_cohens_kappa(b, a)
        assert abs(k1 - k2) < 1e-10


# ============================================================================
# 测试 _score_to_label
# ============================================================================

class TestScoreToLabel:
    """_score_to_label 阈值边界测试。"""

    def test_positive(self, sensitivity_module):
        # POS_THRESHOLD 默认是 0.1
        assert sensitivity_module._score_to_label(0.5) == "正面"

    def test_negative(self, sensitivity_module):
        assert sensitivity_module._score_to_label(-0.5) == "负面"

    def test_neutral(self, sensitivity_module):
        assert sensitivity_module._score_to_label(0.0) == "中性"

    def test_exact_positive_threshold(self, sensitivity_module):
        """恰好等于正面阈值 → 中性（不严格大于）。"""
        threshold = sensitivity_module.POS_THRESHOLD
        assert sensitivity_module._score_to_label(threshold) == "中性"

    def test_just_above_positive_threshold(self, sensitivity_module):
        threshold = sensitivity_module.POS_THRESHOLD
        assert sensitivity_module._score_to_label(threshold + 0.001) == "正面"

    def test_exact_negative_threshold(self, sensitivity_module):
        threshold = sensitivity_module.NEG_THRESHOLD
        assert sensitivity_module._score_to_label(threshold) == "中性"

    def test_just_below_negative_threshold(self, sensitivity_module):
        threshold = sensitivity_module.NEG_THRESHOLD
        assert sensitivity_module._score_to_label(threshold - 0.001) == "负面"


# ============================================================================
# 测试 _compute_sentiment_with_rules
# ============================================================================

class TestComputeSentimentWithRules:
    """_compute_sentiment_with_rules 语言学规则白盒测试。"""

    def test_empty_tokens(self, sensitivity_module):
        raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
            [], {'增长': 1.0, '下降': -1.0}
        )
        assert raw == 0.0
        assert norm == 0.0
        assert pos == 0 and neg == 0

    def test_basic_positive(self, sensitivity_module):
        raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
            ['增长', '创新'], {'增长': 1.0, '创新': 1.0}
        )
        assert raw > 0
        assert pos == 2
        assert neg == 0

    def test_basic_negative(self, sensitivity_module):
        raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
            ['下降', '风险'], {'下降': -1.0, '风险': -1.0}
        )
        assert raw < 0
        assert pos == 0
        assert neg == 2

    def test_mixed_sentiment(self, sensitivity_module):
        raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
            ['增长', '下降'], {'增长': 1.0, '下降': -1.0}
        )
        assert raw == 0.0
        assert pos == 1
        assert neg == 1

    def test_negation_flips_sentiment(self, sensitivity_module):
        """否定词应翻转情感极性。"""
        negation_words = sensitivity_module.NEGATION_WORDS
        if negation_words:
            neg_word = list(negation_words)[0]
            raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
                [neg_word, '增长'], {'增长': 1.0}
            )
            # 否定翻转后，原始正面词变负面
            assert raw < 0

    def test_sentence_end_resets_state(self, sensitivity_module):
        """句末标点应重置否定/转折/程度状态。"""
        negation_words = sensitivity_module.NEGATION_WORDS
        if negation_words:
            neg_word = list(negation_words)[0]
            # 否定词 → 句号 → 正面词（否定已被重置）
            raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
                [neg_word, '。', '增长'], {'增长': 1.0}
            )
            assert raw > 0

    def test_unmatched_tokens_ignored(self, sensitivity_module):
        """不在词典中的 token 应被忽略。"""
        raw, norm, pos, neg = sensitivity_module._compute_sentiment_with_rules(
            ['我', '今天', '很', '开心', '增长'], {'增长': 1.0}
        )
        assert pos == 1  # 仅 '增长' 匹配
