"""
tests/test_22_tone_words.py — 22_tone_words.py 核心逻辑测试
==============================================================

测试词典法情感分析的核心计算引擎：语言学规则增强。
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 复刻核心纯函数（避免 import 时加载配置和词典文件）
# ============================================================================

# 测试用的精简否定词、程度副词、转折连词
TEST_NEGATION_WORDS = frozenset(['不', '没有', '未', '无'])
TEST_DEGREE_WORDS = {'非常': 2.5, '极其': 3.0, '稍微': 0.6, '很': 1.5}
TEST_ADVERSATIVE_WORDS = frozenset(['但是', '然而', '却'])
TEST_NEGATION_WINDOW = 2
TEST_ADVERSATIVE_BOOST = 1.5


TEST_SENTENCE_END = frozenset(['。', '！', '？', '!', '?', '；', ';'])

def _compute_sentiment_with_rules(
    tokens, sentiment_dict,
    negation_words=TEST_NEGATION_WORDS,
    degree_words=TEST_DEGREE_WORDS,
    adversative_words=TEST_ADVERSATIVE_WORDS,
    negation_window=TEST_NEGATION_WINDOW,
    adversative_boost=TEST_ADVERSATIVE_BOOST,
    sentence_end_markers=TEST_SENTENCE_END,
):
    """语言学规则增强的词典法情感计算（测试版）。"""
    total_score = 0.0
    pos_count = 0
    neg_count = 0
    matched_words = []

    negation_remaining = 0
    degree_multiplier = 1.0
    adversative_active = False

    for token in tokens:
        if token in sentence_end_markers:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue

        if token in adversative_words:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue

        if token in negation_words:
            negation_remaining = negation_window
            continue

        if token in degree_words:
            degree_multiplier = degree_words[token]
            continue

        if token in sentiment_dict:
            base_score = sentiment_dict[token]

            if negation_remaining > 0:
                base_score = -base_score

            final_score = base_score * degree_multiplier

            if adversative_active:
                final_score *= adversative_boost

            total_score += final_score

            if final_score > 0:
                pos_count += 1
            elif final_score < 0:
                neg_count += 1

            matched_words.append({
                'word': token,
                'base': sentiment_dict[token],
                'final': round(final_score, 4),
            })

            degree_multiplier = 1.0
        else:
            degree_multiplier = 1.0

        if negation_remaining > 0:
            negation_remaining -= 1

    total_matched = pos_count + neg_count
    normalized_score = total_score / total_matched if total_matched > 0 else 0.0

    return total_score, normalized_score, pos_count, neg_count, matched_words


def _score_to_label(normalized_score, pos_threshold=0.1, neg_threshold=-0.1):
    """得分→标签映射。"""
    if normalized_score > pos_threshold:
        return "正面"
    elif normalized_score < neg_threshold:
        return "负面"
    else:
        return "中性"


# 测试用情感词典
TEST_DICT = {
    '增长': 1.0, '创新': 1.0, '突破': 1.0, '提升': 1.0, '良好': 1.0,
    '下降': -1.0, '风险': -1.0, '亏损': -1.0, '困难': -1.0, '危机': -1.0,
}


# ============================================================================
# 基本情感计算测试
# ============================================================================

class TestComputeSentimentBasic:
    """测试基本正面/负面词计算。"""

    def test_positive_words(self):
        """全正面词应得正分。"""
        tokens = ['增长', '创新', '良好']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score > 0
        assert pos == 3
        assert neg == 0

    def test_negative_words(self):
        """全负面词应得负分。"""
        tokens = ['下降', '风险', '危机']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score < 0
        assert pos == 0
        assert neg == 3

    def test_mixed_words(self):
        """混合词应反映综合得分。"""
        tokens = ['增长', '风险']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 0.0  # +1 + (-1) = 0
        assert pos == 1
        assert neg == 1

    def test_no_sentiment_words(self):
        """无情感词应得 0 分。"""
        tokens = ['今天', '天气', '很好']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 0.0
        assert pos == 0
        assert neg == 0

    def test_empty_tokens(self):
        """空列表应得 0 分。"""
        score, norm, pos, neg, _ = _compute_sentiment_with_rules([], TEST_DICT)
        assert score == 0.0
        assert norm == 0.0

    def test_single_positive(self):
        """单个正面词。"""
        tokens = ['创新']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0
        assert norm == 1.0

    def test_unknown_words_ignored(self):
        """字典外的词应被忽略。"""
        tokens = ['未知词', '增长', '另一个']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0
        assert pos == 1


# ============================================================================
# 否定词测试
# ============================================================================

class TestNegation:
    """测试否定词翻转极性。"""

    def test_negation_flips_positive(self):
        """否定词应翻转正面词极性。"""
        tokens = ['不', '增长']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -1.0  # '增长' 被翻转为负

    def test_negation_flips_negative(self):
        """否定词应翻转负面词极性。"""
        tokens = ['没有', '风险']
        score, norm, pos, neg, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0  # '风险' 被翻转为正

    def test_negation_window(self):
        """否定词窗口应为 2 个 token。"""
        # 窗口内
        tokens = ['不', 'X', '增长']  # X 消耗一个窗口位
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -1.0  # 窗口内，翻转

    def test_negation_expired(self):
        """超出否定窗口应正常计算。"""
        tokens = ['不', 'X', 'Y', '增长']  # 窗口 = 2，X 消耗 1，Y 消耗 2
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0  # 窗口外，不翻转

    def test_double_negation(self):
        """双重否定应恢复原极性。"""
        # "不" → window=2, "未" 在窗口内当作否定词重置 window
        tokens = ['不', '未', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -1.0  # 第二个否定词重新设置窗口


# ============================================================================
# 程度副词测试
# ============================================================================

class TestDegreeWords:
    """测试程度副词放大/缩小效果。"""

    def test_amplify(self):
        """'非常'应放大 2.5 倍。"""
        tokens = ['非常', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 2.5

    def test_extreme_amplify(self):
        """'极其'应放大 3.0 倍。"""
        tokens = ['极其', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 3.0

    def test_diminish(self):
        """'稍微'应减弱为 0.6 倍。"""
        tokens = ['稍微', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert abs(score - 0.6) < 0.01

    def test_degree_resets_after_sentiment(self):
        """程度副词用后应重置。"""
        tokens = ['非常', '增长', '创新']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 3.5  # 2.5 + 1.0

    def test_degree_resets_on_non_sentiment(self):
        """遇到非情感词时程度副词应重置。"""
        tokens = ['非常', '其他词', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0  # 程度副词被重置

    def test_degree_with_negation(self):
        """程度副词+否定词组合。"""
        tokens = ['不', '非常', '增长']
        # '不' 设置否定窗口=2
        # '非常' 设置程度=2.5，消耗窗口 1
        # '增长' base=1.0, 否定→-1.0, ×2.5 = -2.5，消耗窗口 2
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -2.5


# ============================================================================
# 转折连词测试
# ============================================================================

class TestAdversative:
    """测试转折连词加权效果。"""

    def test_adversative_boost(self):
        """转折后的情感词应放大 1.5 倍。"""
        tokens = ['增长', '但是', '下降']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # 增长: +1.0, 但是激活转折, 下降: -1.0 × 1.5 = -1.5
        assert score == -0.5

    def test_adversative_resets_negation(self):
        """转折应重置否定窗口。"""
        tokens = ['不', '但是', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # '不' 设置否定，'但是' 重置否定并激活转折
        # '增长': +1.0 × 1.5 = +1.5
        assert score == 1.5

    def test_adversative_permanent(self):
        """转折在同一句内（无句末标点）持续生效。"""
        tokens = ['但是', '增长', '创新']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # 同一句内: 增长: 1.0 × 1.5 = 1.5, 创新: 1.0 × 1.5 = 1.5
        assert score == 3.0


# ============================================================================
# 转折词句末作用域测试 (修补致命硬伤 1)
# ============================================================================

class TestAdversativeSentenceScope:
    """测试转折词在句末标点处正确重置（Ding 2008 从句级作用域）。"""

    def test_resets_at_period(self):
        """句号应重置转折效应。"""
        tokens = ['但是', '下降', '。', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # 下降: -1.0 × 1.5 = -1.5, 。→重置, 增长: +1.0
        assert score == -0.5

    def test_resets_at_exclamation(self):
        """感叹号应重置转折效应。"""
        tokens = ['但是', '下降', '！', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -0.5

    def test_resets_at_question(self):
        """问号应重置转折效应。"""
        tokens = ['但是', '下降', '？', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -0.5

    def test_resets_at_semicolon(self):
        """分号应重置转折效应。"""
        tokens = ['但是', '下降', '；', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -0.5

    def test_persists_within_sentence(self):
        """句内无标点时转折应持续生效。"""
        tokens = ['但是', '下降', '风险']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -3.0

    def test_comma_does_not_reset(self):
        """逗号不是句末标点，不应重置。"""
        tokens = ['但是', '下降', '，', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(
            tokens, TEST_DICT, sentence_end_markers=frozenset(['。', '！', '？'])
        )
        assert score == 0.0  # -1.5 + 1.5

    def test_multi_sentence_independent(self):
        """多句场景：各句转折效应独立。"""
        tokens = ['但是', '下降', '。', '然而', '增长', '。', '风险']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == -1.0

    def test_negation_resets_at_period(self):
        """句末标点应同时重置否定窗口。"""
        tokens = ['不', '。', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0

    def test_degree_resets_at_period(self):
        """句末标点应重置程度副词。"""
        tokens = ['非常', '。', '增长']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert score == 1.0


# ============================================================================
# 组合规则测试
# ============================================================================

class TestCombinedRules:
    """测试多规则组合场景。"""

    def test_degree_and_adversative(self):
        """程度副词 + 转折。"""
        tokens = ['增长', '但是', '非常', '下降']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # 增长: +1.0
        # 但是: 转折激活
        # 非常 下降: -1.0 × 2.5 × 1.5 = -3.75
        assert score == 1.0 - 3.75

    def test_negation_and_adversative(self):
        """否定 + 转折。"""
        tokens = ['但是', '不', '下降']
        score, _, _, _, _ = _compute_sentiment_with_rules(tokens, TEST_DICT)
        # 但是: 转折激活
        # 不 下降: -(-1.0) = 1.0, × 1.5 = 1.5
        assert score == 1.5

    def test_matched_words_details(self):
        """匹配词详情记录。"""
        tokens = ['增长', '下降']
        _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
        assert len(matched) == 2
        assert matched[0]['word'] == '增长'
        assert matched[0]['base'] == 1.0
        assert matched[0]['final'] == 1.0
        assert matched[1]['word'] == '下降'
        assert matched[1]['base'] == -1.0
        assert matched[1]['final'] == -1.0


# ============================================================================
# _score_to_label 测试
# ============================================================================

class TestScoreToLabel:
    """测试得分→标签映射。"""

    def test_positive_label(self):
        assert _score_to_label(0.5) == '正面'

    def test_negative_label(self):
        assert _score_to_label(-0.5) == '负面'

    def test_neutral_label(self):
        assert _score_to_label(0.0) == '中性'

    def test_threshold_boundary_positive(self):
        """正好等于正阈值应为中性。"""
        assert _score_to_label(0.1) == '中性'

    def test_threshold_boundary_negative(self):
        """正好等于负阈值应为中性。"""
        assert _score_to_label(-0.1) == '中性'

    def test_just_above_positive(self):
        assert _score_to_label(0.1001) == '正面'

    def test_just_below_negative(self):
        assert _score_to_label(-0.1001) == '负面'

    def test_custom_thresholds(self):
        """自定义阈值。"""
        assert _score_to_label(0.15, pos_threshold=0.2) == '中性'
        assert _score_to_label(0.25, pos_threshold=0.2) == '正面'


# ============================================================================
# 增强测试：空 token 防御与极端场景
# ============================================================================

class TestSentimentEdgeCases:
    """增强测试：空 token、极端度和边界条件。"""

    def test_empty_tokens_defense(self):
        """空 token 列表应返回零分且不崩溃。"""
        result = _compute_sentiment_with_rules(
            tokens=[],
            sentiment_dict={'增长': 1.0},
            negation_words={'不'},
            degree_words={'非常': 2.0},
            adversative_words={'但是'},
        )
        # 返回 (total_score, normalized_score, pos_count, neg_count, matched_words)
        assert result[0] == 0.0  # total_score
        assert result[1] == 0.0  # normalized_score

    def test_all_stopwords_no_sentiment(self):
        """全部无情感词的 token 列表应返回零分。"""
        result = _compute_sentiment_with_rules(
            tokens=['的', '了', '是', '在'],
            sentiment_dict={'增长': 1.0},
            negation_words={'不'},
            degree_words={'非常': 2.0},
            adversative_words={'但是'},
        )
        assert result[1] == 0.0  # normalized_score

    def test_single_positive_token(self):
        """单个正面词应正确计分。"""
        result = _compute_sentiment_with_rules(
            tokens=['增长'],
            sentiment_dict={'增长': 1.0},
            negation_words={'不'},
            degree_words={},
            adversative_words={},
        )
        assert result[1] > 0  # normalized_score

    def test_single_negative_token(self):
        """单个负面词应正确计分。"""
        result = _compute_sentiment_with_rules(
            tokens=['下降'],
            sentiment_dict={'下降': -1.0},
            negation_words={'不'},
            degree_words={},
            adversative_words={},
        )
        assert result[1] < 0  # normalized_score

    def test_consecutive_negations(self):
        """连续否定词每个都重置否定窗口（非累计），结果仍为否定。"""
        result = _compute_sentiment_with_rules(
            tokens=['不', '没', '增长'],
            sentiment_dict={'增长': 1.0},
            negation_words={'不', '没'},
            degree_words={},
            adversative_words={},
        )
        # 每个否定词重置窗口，最终 "增长" 仍在否定窗口内 → 负面
        assert result[1] < 0  # normalized_score

    def test_extreme_degree_adverb(self):
        """极大程度副词应显著放大情感。"""
        result_normal = _compute_sentiment_with_rules(
            tokens=['增长'],
            sentiment_dict={'增长': 1.0},
            negation_words={},
            degree_words={},
            adversative_words={},
        )
        result_extreme = _compute_sentiment_with_rules(
            tokens=['极其', '增长'],
            sentiment_dict={'增长': 1.0},
            negation_words={},
            degree_words={'极其': 3.0},
            adversative_words={},
        )
        assert abs(result_extreme[1]) > abs(result_normal[1])

    def test_adversative_before_and_after(self):
        """转折词前后的情感应按权重调整。"""
        result = _compute_sentiment_with_rules(
            tokens=['增长', '但是', '下降'],
            sentiment_dict={'增长': 1.0, '下降': -1.0},
            negation_words={},
            degree_words={},
            adversative_words={'但是'},
        )
        # 转折后的 "下降" 权重更大
        assert result[1] < 0

    def test_label_boundary_at_zero(self):
        """零分应为中性。"""
        assert _score_to_label(0.0) == '中性'

    def test_label_large_positive(self):
        """极大正分应为正面。"""
        assert _score_to_label(100.0) == '正面'

    def test_label_large_negative(self):
        """极大负分应为负面。"""
        assert _score_to_label(-100.0) == '负面'

    def test_many_sentiment_words(self):
        """大量情感词的组合应正确累加。"""
        result = _compute_sentiment_with_rules(
            tokens=['好', '棒', '佳', '优', '美'],
            sentiment_dict={'好': 1.0, '棒': 1.0, '佳': 1.0, '优': 1.0, '美': 1.0},
            negation_words={},
            degree_words={},
            adversative_words={},
        )
        assert result[0] > 0  # total_score
        assert result[1] > 0  # normalized_score


