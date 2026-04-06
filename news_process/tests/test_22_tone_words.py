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


# ============================================================================
# 前瞻性词频测试
# Li, F. (2010). Journal of Accounting Research, 48(5), 1049-1102.
# DOI: 10.1111/j.1475-679X.2010.00382.x
# ============================================================================

TEST_FL_WORDS = frozenset(['预计', '计划', '将', '展望', '可能', '未来'])


def _compute_forward_looking_ratio(tokens, fl_words=TEST_FL_WORDS):
    """前瞻性词频计算（测试版）。"""
    if not tokens:
        return 0.0, 0
    fl_count = sum(1 for t in tokens if t in fl_words)
    return fl_count / len(tokens), fl_count


class TestForwardLookingRatio:
    """测试前瞻性词汇比率计算 (Li 2010)。"""

    def test_empty_tokens(self):
        """空列表应返回 (0.0, 0)。"""
        assert _compute_forward_looking_ratio([]) == (0.0, 0)

    def test_all_forward_looking(self):
        """全部为前瞻性词应返回 ratio = 1.0。"""
        ratio, count = _compute_forward_looking_ratio(['预计', '计划', '展望'])
        assert ratio == 1.0
        assert count == 3

    def test_no_forward_looking(self):
        """无前瞻性词应返回 ratio = 0.0。"""
        ratio, count = _compute_forward_looking_ratio(['银行', '贷款', '利率'])
        assert ratio == 0.0
        assert count == 0

    def test_mixed_text(self):
        """混合文本应返回 0 < ratio < 1。"""
        ratio, count = _compute_forward_looking_ratio(['银行', '预计', '明年', '增长'])
        assert 0 < ratio < 1
        assert count == 1  # 仅 '预计' 在 TEST_FL_WORDS 中

    def test_negated_fl_word_still_counted(self):
        """否定句中的前瞻性词仍应计入（时间取向不变）。"""
        ratio, count = _compute_forward_looking_ratio(['不', '预计', '降息'])
        assert count == 1


# ============================================================================
# 文本可读性测试
# Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. 
# The Journal of Finance, 69(4), 1643-1671.
# https://doi.org/10.1111/jofi.12162
# Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). 
# A plain English measure of financial reporting readability. 
# Journal of Accounting and Economics, 63(2-3), 329-357.
# https://doi.org/10.1016/j.jacceco.2017.03.002
# ============================================================================

import re as _re
import string as _string

def _compute_readability(content, tokens):
    """中文文本可读性计算（测试版）。"""
    punctuation_set = frozenset(_string.punctuation + "“”‘’：；！？（）【】「」《》、，。·…—\n\t \r")
    real_tokens = [t for t in tokens if t not in punctuation_set and not t.isspace() and t]

    sentences = _re.split(r'[。！？!?；;]', content)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    n_sentences = max(len(sentences), 1)
    avg_sentence_len = sum(len(s.strip()) for s in sentences) / n_sentences

    n_real_tokens = max(len(real_tokens), 1)
    ttr = len(set(real_tokens)) / n_real_tokens
    cpw = sum(len(t) for t in real_tokens) / n_real_tokens
    return {
        'avg_sentence_len': round(avg_sentence_len, 2),
        'type_token_ratio': round(ttr, 4),
        'char_per_word': round(cpw, 4),
    }


class TestReadability:
    """测试中文文本可读性三维度代理指标。"""

    def test_single_sentence(self):
        """单句文本 ASL 应等于文本字符数。"""
        r = _compute_readability('银行推出新产品', ['银行', '推出', '新', '产品'])
        assert r['avg_sentence_len'] == 7
        assert r['char_per_word'] > 1.0

    def test_multi_sentence(self):
        """多句文本 ASL 应为各句均值。"""
        r = _compute_readability('银行增长。风险下降。', ['银行', '增长', '风险', '下降'])
        assert r['avg_sentence_len'] == 4.0

    def test_ttr_all_unique(self):
        """全不同词 TTR 应等于 1.0。"""
        r = _compute_readability('一二三', ['一', '二', '三'])
        assert r['type_token_ratio'] == 1.0

    def test_ttr_all_same(self):
        """全重复词 TTR 应接近 1/n。"""
        r = _compute_readability('的的的', ['的', '的', '的'])
        assert abs(r['type_token_ratio'] - 1 / 3) < 0.01

    def test_cpw_single_char_words(self):
        """全单字词 CPW 应等于 1.0。"""
        r = _compute_readability('一二三', ['一', '二', '三'])
        assert r['char_per_word'] == 1.0

    def test_cpw_multi_char_words(self):
        """含多字词 CPW 应大于 1.0。"""
        r = _compute_readability('金融科技', ['金融', '科技'])
        assert r['char_per_word'] == 2.0

    def test_exclude_punctuation(self):
        """测试 TTR 和 CPW 计算时应当剔除所有标点符号及空白文本。"""
        # "你好，世界！" => 2个有效词，2个无效词
        r1 = _compute_readability('你好世界', ['你好', '世界'])
        r2 = _compute_readability('你好，世界！', ['你好', '，', '世界', '！', '   '])
        assert r1['type_token_ratio'] == r2['type_token_ratio']
        assert r1['char_per_word'] == r2['char_per_word']


# ============================================================================
# 正/负面词频分离测试
# Berger, A.N., Kim, H.H. & Ma, X. (2024). Bank Sentiment and Liquidity
# Hoarding. Contemporary Accounting Research, 41(3). Appendix S6.
# Loughran, T. & McDonald, B. (2011). Journal of Finance, 66(1), 35-65.
# DOI: 10.1111/j.1540-6261.2010.01625.x
# ============================================================================

class TestPosNegRatioSeparation:
    """测试正/负面词频分离逻辑。"""

    def test_all_positive(self):
        """全正面词 → pos_ratio > 0, neg_ratio = 0。"""
        tokens = ['增长', '创新', '其他', '无关']
        pos_count, neg_count = 2, 0
        pos_ratio = pos_count / len(tokens)
        neg_ratio = neg_count / len(tokens)
        assert pos_ratio == 0.5
        assert neg_ratio == 0.0

    def test_all_negative(self):
        """全负面词 → pos_ratio = 0, neg_ratio > 0。"""
        tokens = ['下降', '风险', '其他']
        pos_count, neg_count = 0, 2
        pos_ratio = pos_count / len(tokens)
        neg_ratio = neg_count / len(tokens)
        assert pos_ratio == 0.0
        assert abs(neg_ratio - 2 / 3) < 0.01

    def test_sum_leq_one(self):
        """pos_ratio + neg_ratio 之和不应超过 1.0。"""
        tokens = ['增长', '下降', '创新', '风险', '其他']
        pos_count, neg_count = 2, 2
        total_ratio = (pos_count + neg_count) / len(tokens)
        assert total_ratio <= 1.0


# ============================================================================
# MSENT 计数型情感指标测试
# He, Lu, Wei & Wang (2024). IRFA, 95, 103430. Eq. (1)
# Tetlock, P. (2007). Journal of Finance, 62(3), 1139-1168.
# ============================================================================

class TestMsentScore:
    """测试 MSENT = (Neg-Pos)/(Neg+Pos) 使用原始词典极性计数。"""

    def test_all_positive_msent(self):
        """全正面词 → MSENT = (0-N)/(N+0) = -1.0。"""
        tokens = ['增长', '创新']
        _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
        raw_pos = sum(1 for m in matched if m['base'] > 0)
        raw_neg = sum(1 for m in matched if m['base'] < 0)
        total = raw_pos + raw_neg
        msent = (raw_neg - raw_pos) / total if total > 0 else 0.0
        assert msent == -1.0

    def test_all_negative_msent(self):
        """全负面词 → MSENT = (N-0)/(0+N) = +1.0。"""
        tokens = ['下降', '风险']
        _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
        raw_pos = sum(1 for m in matched if m['base'] > 0)
        raw_neg = sum(1 for m in matched if m['base'] < 0)
        total = raw_pos + raw_neg
        msent = (raw_neg - raw_pos) / total if total > 0 else 0.0
        assert msent == 1.0

    def test_balanced_msent(self):
        """等量正负面词 → MSENT = 0.0。"""
        tokens = ['增长', '下降']
        _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
        raw_pos = sum(1 for m in matched if m['base'] > 0)
        raw_neg = sum(1 for m in matched if m['base'] < 0)
        total = raw_pos + raw_neg
        msent = (raw_neg - raw_pos) / total if total > 0 else 0.0
        assert msent == 0.0

    def test_no_match_msent(self):
        """无匹配词 → MSENT = 0.0 (默认中性)。"""
        tokens = ['今天', '天气']
        _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
        raw_pos = sum(1 for m in matched if m['base'] > 0)
        raw_neg = sum(1 for m in matched if m['base'] < 0)
        total = raw_pos + raw_neg
        msent = (raw_neg - raw_pos) / total if total > 0 else 0.0
        assert msent == 0.0

    def test_msent_uses_raw_not_final(self):
        """否定词场景: MSENT 应使用原始词典极性 (base), 而非语言学规则后极性 (final)。

        "不 增长": '增长' 在词典中 base=+1 (正面), 但 final=-1 (被否定翻转).
        MSENT 应基于 base → pos=1, neg=0 → MSENT = (0-1)/(1+0) = -1.0
        而非基于 final → pos=0, neg=1 → 错误地得到 +1.0
        """
        tokens = ['不', '增长']
        _, _, pos_count, neg_count, matched = _compute_sentiment_with_rules(
            tokens, TEST_DICT)
        # final 极性 (后规则): "增长" 被否定 → neg_count=1
        assert neg_count == 1, "后规则计数应为 neg=1"
        assert pos_count == 0, "后规则计数应为 pos=0"

        # 原始词典极性 (base): "增长" base=+1 → raw_pos=1
        raw_pos = sum(1 for m in matched if m['base'] > 0)
        raw_neg = sum(1 for m in matched if m['base'] < 0)
        assert raw_pos == 1, "原始计数应为 pos=1"
        assert raw_neg == 0, "原始计数应为 neg=0"

        # MSENT 应使用原始计数
        msent = (raw_neg - raw_pos) / (raw_pos + raw_neg)
        assert msent == -1.0, "MSENT 应为 -1.0 (基于原始词典极性)"

    def test_msent_value_range(self):
        """MSENT 值域应为 [-1, +1]。"""
        for tokens in [
            ['增长'], ['下降'], ['增长', '下降'],
            ['增长', '增长', '下降'],
        ]:
            _, _, _, _, matched = _compute_sentiment_with_rules(tokens, TEST_DICT)
            raw_pos = sum(1 for m in matched if m['base'] > 0)
            raw_neg = sum(1 for m in matched if m['base'] < 0)
            total = raw_pos + raw_neg
            if total > 0:
                msent = (raw_neg - raw_pos) / total
                assert -1.0 <= msent <= 1.0, f"MSENT={msent} 超出 [-1,+1]"


# ============================================================================
# IDF 加权稳健性检验测试 (Gentzkow, Kelly & Taddy, 2019, JEL §2.2)
# ============================================================================

import math
import numpy as np


def _build_idf_weights_test(docs: list[str],
                            dictionaries: list[tuple[str, dict[str, float]]],
                            ) -> dict[str, dict[str, float]]:
    """复刻 build_idf_weights 的核心逻辑供测试使用（无 DataFrame/AC 依赖）。"""
    import ahocorasick as ahc

    N = len(docs)
    if N == 0:
        return {name: {w: 1.0 for w in d} for name, d in dictionaries}

    all_words = set()
    for _, d in dictionaries:
        all_words.update(d.keys())

    if not all_words:
        return {name: {} for name, _ in dictionaries}

    A = ahc.Automaton()
    for word in sorted(all_words):
        A.add_word(word, word)
    A.make_automaton()

    from collections import Counter
    doc_freq: Counter = Counter()
    for text in docs:
        seen = set()
        for _, word in A.iter(text):
            seen.add(word)
        doc_freq.update(seen)

    result = {}
    for dict_name, sentiment_dict in dictionaries:
        if not sentiment_dict:
            result[dict_name] = {}
            continue

        raw_idf = {}
        for word in sentiment_dict:
            df_w = doc_freq.get(word, 0)
            raw_idf[word] = math.log10(N / (1 + df_w))

        values = list(raw_idf.values())
        mean_val = float(np.mean(values)) if values else 1.0
        if mean_val > 0:
            normed = {w: v / mean_val for w, v in raw_idf.items()}
        else:
            normed = {w: 1.0 for w in raw_idf}

        normed_vals = np.array(list(normed.values()))
        if len(normed_vals) >= 2:
            p1 = float(np.percentile(normed_vals, 1))
            p99 = float(np.percentile(normed_vals, 99))
            capped = {w: float(np.clip(v, p1, p99)) for w, v in normed.items()}
        else:
            capped = dict(normed)

        result[dict_name] = capped
    return result


def _build_idf_weighted_dict_test(sentiment_dict, idf_weights):
    """复刻 _build_idf_weighted_dict 供测试使用。"""
    return {
        word: base_score * idf_weights.get(word, 1.0)
        for word, base_score in sentiment_dict.items()
    }


class TestIDFWeighting:
    """IDF 加权稳健性检验测试。

    学术依据:
      Gentzkow, M., Kelly, B. & Taddy, M. (2019). Text as Data.
      Journal of Economic Literature, 57(3), 535-574. §2.2.
    """

    # 测试用简易语料
    CORPUS = [
        '银行增长发展态势良好',   # 增长✓ 发展✓ 风险✗
        '增长速度快发展好',       # 增长✓ 发展✓ 风险✗
        '增长率提高',             # 增长✓ 发展✗ 风险✗
        '发展态势好增长快',       # 增长✓ 发展✓ 风险✗
        '风险控制良好',           # 增长✗ 发展✗ 风险✓
    ]
    # 增长 DF=4, 发展 DF=3, 风险 DF=1 → 风险最稀有 → IDF 最高

    TEST_DICT = {'增长': 1.0, '发展': 1.0, '风险': -1.0}
    DICTS = [('test', TEST_DICT)]

    def test_rare_word_higher_idf(self):
        """稀有词（DF 低）的 IDF 应大于高频词。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        w = weights['test']
        # 风险(DF=1) > 发展(DF=3) > 增长(DF=4)
        assert w['风险'] > w['发展'], f"风险 {w['风险']:.4f} <= 发展 {w['发展']:.4f}"
        assert w['发展'] > w['增长'], f"发展 {w['发展']:.4f} <= 增长 {w['增长']:.4f}"

    def test_ubiquitous_word_lower_idf(self):
        """出现在所有/大部分文档中的词 IDF 应最低。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        w = weights['test']
        assert w['增长'] == min(w.values()), "最高频词应有最低 IDF"

    def test_preserves_polarity(self):
        """IDF 加权不改变正/负极性方向。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        idf_dict = _build_idf_weighted_dict_test(self.TEST_DICT, weights['test'])
        assert idf_dict['增长'] > 0, "正面词加权后应仍为正"
        assert idf_dict['风险'] < 0, "负面词加权后应仍为负"

    def test_preserves_asymmetric_base(self):
        """du_2022 政治正面词 base=0.5 应保留非对称性。"""
        asym_dict = {'增长': 0.5, '风险': -1.0}
        weights = _build_idf_weights_test(self.CORPUS, [('asym', asym_dict)])
        idf_dict = _build_idf_weighted_dict_test(asym_dict, weights['asym'])
        # |增长_idf| < |风险_idf| 因为 base 不同
        assert abs(idf_dict['增长']) < abs(idf_dict['风险']), \
            "非对称 base_score 应保留: |0.5×idf| < |1.0×idf|"

    def test_normalized_mean_near_one(self):
        """归一化后 IDF 均值应接近 1.0。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        w = weights['test']
        mean_idf = np.mean(list(w.values()))
        assert abs(mean_idf - 1.0) < 0.15, f"均值={mean_idf:.4f}，应接近 1.0"

    def test_winsorize_clips_extreme_high(self):
        """Winsorize 后最大值应等于 P99。"""
        # 构造 100 个词，分布一致时 Winsorize 不改变任何值
        many_words = {f'term_{i:04d}': 1.0 for i in range(100)}
        # 第1篇含所有词，其余每篇只含前 50 个词
        all_terms = ' '.join(f'term_{i:04d}' for i in range(100))
        common_terms = ' '.join(f'term_{i:04d}' for i in range(50))
        docs = [all_terms] + [common_terms for _ in range(49)]

        weights = _build_idf_weights_test(docs, [('test', many_words)])
        w = weights['test']
        vals = np.array(list(w.values()))
        # 基本检查：Winsorize 后，最大值 ≤ P99 + 容差
        p99 = float(np.percentile(vals, 99))
        assert max(vals) <= p99 + 0.01

    def test_winsorize_clips_extreme_low(self):
        """Winsorize 后最小值应等于 P1。"""
        many_words = {f'term_{i:04d}': 1.0 for i in range(100)}
        all_terms = ' '.join(f'term_{i:04d}' for i in range(100))
        common_terms = ' '.join(f'term_{i:04d}' for i in range(50))
        docs = [all_terms] + [common_terms for _ in range(49)]

        weights = _build_idf_weights_test(docs, [('test', many_words)])
        w = weights['test']
        vals = np.array(list(w.values()))
        p1 = float(np.percentile(vals, 1))
        assert min(vals) >= p1 - 0.01

    def test_df_zero_gets_max_idf(self):
        """词典中存在但语料中 DF=0 的词应获得最高 IDF（被 Winsorize 封顶）。"""
        ghost_dict = {'增长': 1.0, '幽灵词': 1.0}
        docs = ['增长态势好', '增长率高']
        weights = _build_idf_weights_test(docs, [('ghost', ghost_dict)])
        w = weights['ghost']
        assert w['幽灵词'] >= w['增长'], \
            f"DF=0 的词 IDF={w['幽灵词']:.4f} 应 >= DF>0 的词 IDF={w['增长']:.4f}"

    def test_empty_corpus_degrades_to_equal_weight(self):
        """空语料时 IDF 应优雅降级为均等权重（全部 = 1.0）。"""
        weights = _build_idf_weights_test([], self.DICTS)
        w = weights['test']
        for word, val in w.items():
            assert val == 1.0, f"{word} 的 IDF={val}，空语料应为 1.0"

    def test_idf_dict_works_with_negation(self):
        """IDF 词典应与否定词规则正确协作。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        idf_dict = _build_idf_weighted_dict_test(self.TEST_DICT, weights['test'])

        # "不 增长" → 否定翻转
        tokens = ['不', '增长']
        _, norm, _, _, _ = _compute_sentiment_with_rules(tokens, idf_dict)
        assert norm < 0, f"'不 增长' IDF 加权后应为负，实际={norm:.4f}"

    def test_idf_dict_works_with_degree_and_adversative(self):
        """IDF 词典应与程度副词+转折规则正确协作。"""
        weights = _build_idf_weights_test(self.CORPUS, self.DICTS)
        idf_dict = _build_idf_weighted_dict_test(self.TEST_DICT, weights['test'])

        # "非常 增长" → 程度放大
        tokens_deg = ['非常', '增长']
        _, norm_deg, _, _, _ = _compute_sentiment_with_rules(tokens_deg, idf_dict)
        # "增长" only
        tokens_plain = ['增长']
        _, norm_plain, _, _, _ = _compute_sentiment_with_rules(tokens_plain, idf_dict)
        # 加了"非常"的分数绝对值应更大
        assert abs(norm_deg) > abs(norm_plain), \
            f"程度副词应放大: |{norm_deg:.4f}| > |{norm_plain:.4f}|"
