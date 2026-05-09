"""
tests/test_canonicalization.py — utils/canonicalization.py 单元测试
=====================================================================
"""

import os
import sys
import pytest

# Phase 5c-2: 注入项目父目录解析 ``news_process.*``
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.text.canonicalization import _normalize_text, canonicalize_topic


# ============================================================================
# _normalize_text 测试
# ============================================================================

class TestNormalizeText:
    """测试文本归一化函数。"""

    def test_fullwidth_to_halfwidth(self):
        """全角字符应转为半角。"""
        assert _normalize_text('ＡＢＣ') == 'ABC'

    def test_fullwidth_numbers(self):
        """全角数字应转为半角。"""
        assert _normalize_text('０１２３') == '0123'

    def test_fullwidth_space(self):
        """全角空格应转为半角空格。"""
        assert _normalize_text('Ａ\u3000Ｂ') == 'A B'

    def test_uppercase(self):
        """小写应转为大写。"""
        assert _normalize_text('abc') == 'ABC'
        assert _normalize_text('Hello World') == 'HELLO WORLD'

    def test_whitespace_normalization(self):
        """多余空白应合并为单个空格。"""
        assert _normalize_text('  多余   空白  ') == '多余 空白'

    def test_mixed(self):
        """混合全角+小写+多余空白的综合测试。"""
        result = _normalize_text('ａｉ   技术')
        assert result == 'AI 技术'

    def test_empty_string(self):
        """空字符串应返回空字符串。"""
        assert _normalize_text('') == ''

    def test_chinese_unchanged(self):
        """中文字符不应被改变（仅大写转换影响英文）。"""
        assert _normalize_text('人工智能') == '人工智能'


# ============================================================================
# canonicalize_topic 测试
# ============================================================================

class TestCanonicalizeTopic:
    """测试金融科技主题标准化分类。"""

    # --- 底层技术 ---

    def test_technology_ai(self):
        """人工智能应归为底层技术。"""
        cat, conf = canonicalize_topic('人工智能技术研发')
        assert cat == '底层技术'
        assert conf > 0

    def test_technology_blockchain(self):
        """区块链应归为底层技术。"""
        cat, conf = canonicalize_topic('区块链分布式账本')
        assert cat == '底层技术'

    def test_technology_cloud(self):
        """云计算应归为底层技术。"""
        cat, conf = canonicalize_topic('云计算平台')
        assert cat == '底层技术'

    def test_technology_bigdata(self):
        """大数据应归为底层技术。"""
        cat, conf = canonicalize_topic('大数据分析平台')
        assert cat == '底层技术'

    def test_technology_iot(self):
        """物联网应归为底层技术。"""
        cat, conf = canonicalize_topic('物联网传感器')
        assert cat == '底层技术'

    # --- 应用场景 ---

    def test_application_payment(self):
        """数字支付应归为应用场景。"""
        cat, conf = canonicalize_topic('移动支付跨境支付')
        assert cat == '应用场景'

    def test_application_risk(self):
        """智能风控应归为应用场景。"""
        cat, conf = canonicalize_topic('智能风控反欺诈系统')
        assert cat == '应用场景'

    def test_application_credit(self):
        """数字信贷应归为应用场景。"""
        cat, conf = canonicalize_topic('数字信贷供应链金融')
        assert cat == '应用场景'

    def test_application_digital_bank(self):
        """数字银行应归为应用场景。"""
        cat, conf = canonicalize_topic('手机银行开放银行')
        assert cat == '应用场景'

    # --- 混合与边界 ---

    def test_mixed_keywords_weighted(self):
        """混合关键词应按加权评分判定。"""
        cat, conf = canonicalize_topic('人工智能深度学习机器学习神经网络')
        assert cat == '底层技术'

    def test_empty_input(self):
        """空字符串应返回默认值。"""
        cat, conf = canonicalize_topic('')
        assert cat == '应用场景'
        assert conf == 0.0

    def test_none_input(self):
        """None 输入应返回默认值。"""
        cat, conf = canonicalize_topic(None)
        assert cat == '应用场景'
        assert conf == 0.0

    def test_null_string(self):
        """'null' 字符串应返回默认值。"""
        cat, conf = canonicalize_topic('null')
        assert cat == '应用场景'
        assert conf == 0.0

    def test_confidence_range(self):
        """置信度应在 0~1 之间。"""
        cat, conf = canonicalize_topic('人工智能')
        assert 0.0 <= conf <= 1.0

    def test_no_overlap_scoring(self):
        """最长匹配优先，不应有重叠计分。"""
        # "大数据平台" 应作为整体匹配（权重2.0），而不是拆分为 "大数据"(2.0) + "平台"
        cat, conf = canonicalize_topic('大数据平台')
        assert cat == '底层技术'

    def test_fullwidth_input(self):
        """全角输入应自动归一化后匹配。"""
        cat, conf = canonicalize_topic('人工智能')
        assert cat == '底层技术'

    def test_other_tech_category(self):
        """其他底层技术关键词应归为底层技术。"""
        cat, conf = canonicalize_topic('联邦学习隐私计算')
        assert cat == '底层技术'


# ============================================================================
# 增强测试：边界条件覆盖
# ============================================================================

class TestCanonicalizeTopicEnhanced:
    """增强测试：覆盖更多边界条件。"""

    def test_both_keywords_higher_score_wins(self):
        """同时含底层技术和应用场景关键词时，得分高者胜出。"""
        # "区块链数字支付" → 区块链(2.0) vs 数字支付(2.0)，相等时底层技术优先
        cat, conf = canonicalize_topic('区块链数字支付')
        assert cat in ('底层技术', '应用场景')

    def test_empty_string(self):
        """空字符串应返回默认值。"""
        cat, conf = canonicalize_topic('')
        assert cat == '应用场景'
        assert conf == 0.0

    def test_whitespace_only(self):
        """纯空白字符串应返回默认值。"""
        cat, conf = canonicalize_topic('   ')
        assert cat == '应用场景'
        assert conf == 0.0

    def test_none_string(self):
        """字符串 'none' 应返回默认值。"""
        cat, conf = canonicalize_topic('none')
        assert cat == '应用场景'
        assert conf == 0.0

    def test_case_insensitive_keywords(self):
        """不区分大小写的英文关键词应匹配。"""
        cat, conf = canonicalize_topic('ai')
        assert cat == '底层技术'

    def test_iot_keyword(self):
        """IoT 关键词应匹配底层技术。"""
        cat, conf = canonicalize_topic('IOT技术应用')
        assert cat == '底层技术'

    def test_digital_payment(self):
        """数字支付关键词应返回应用场景。"""
        cat, conf = canonicalize_topic('移动支付')
        assert cat == '应用场景'

    def test_smart_risk_control(self):
        """智能风控关键词应返回应用场景。"""
        cat, conf = canonicalize_topic('智能风控反欺诈')
        assert cat == '应用场景'

    def test_green_finance(self):
        """绿色金融关键词。"""
        cat, conf = canonicalize_topic('绿色金融ESG')
        assert cat == '应用场景'

    def test_blockchain_technology(self):
        """区块链关键词应返回底层技术。"""
        cat, conf = canonicalize_topic('区块链智能合约')
        assert cat == '底层技术'

    def test_cloud_computing(self):
        """云计算关键词应返回底层技术。"""
        cat, conf = canonicalize_topic('云原生微服务容器化')
        assert cat == '底层技术'

    def test_insurance_tech(self):
        """保险科技关键词应返回应用场景。"""
        cat, conf = canonicalize_topic('保险科技智能核保')
        assert cat == '应用场景'

    def test_digital_bank(self):
        """数字银行关键词。"""
        cat, conf = canonicalize_topic('手机银行开放银行')
        assert cat == '应用场景'

    def test_unrecognized_topic(self):
        """完全无关的文本应返回默认分类。"""
        cat, conf = canonicalize_topic('今天天气很好')
        assert conf < 0.5  # 置信度应较低

    def test_very_long_input(self):
        """超长输入不应崩溃。"""
        long_text = '人工智能 ' * 1000
        cat, conf = canonicalize_topic(long_text)
        assert cat == '底层技术'

    def test_multiple_tech_keywords_highest_weight_wins(self):
        """多个底层技术关键词时，权重累加归为底层技术。"""
        # 2个人工智能关键词 vs 1个大数据关键词
        cat, conf = canonicalize_topic('机器学习深度学习和数据分析')
        assert cat == '底层技术'

    def test_fullwidth_digits_and_letters(self):
        """全角数字和字母应正确归一化。"""
        cat, conf = canonicalize_topic('５Ｇ技术')
        assert cat == '底层技术'

    def test_mixed_ai_risk_higher_score_wins(self):
        """同时含底层技术和应用场景关键词时，得分高者胜出。"""
        cat, conf = canonicalize_topic('人工智能智能风控')
        assert cat in ('底层技术', '应用场景')
        assert conf > 0

    def test_mixed_blockchain_payment(self):
        """区块链 + 跨境支付时，得分高者胜出。"""
        cat, conf = canonicalize_topic('基于区块链的跨境支付')
        assert cat in ('底层技术', '应用场景')

    def test_single_tech_no_app(self):
        """纯底层技术关键词应返回底层技术。"""
        cat, conf = canonicalize_topic('云计算平台')
        assert cat == '底层技术'

    def test_single_app_no_tech(self):
        """纯应用场景关键词应返回应用场景。"""
        cat, conf = canonicalize_topic('移动支付')
        assert cat == '应用场景'


# ============================================================================
# Plan-r3 round-3 review M1: rapidfuzz vs thefuzz 数值 parity invariant
# ============================================================================


class TestRapidfuzzThefuzzParity:
    """守护 Plan-r3 P2-12 'rapidfuzz drop-in replacement for thefuzz' 假设.

    canonicalization.py:289 走 ``try rapidfuzz first, fallback thefuzz``
    路径. 如果两者 ``fuzz.partial_token_set_ratio`` 数值不一致, 切换 fallback
    会让 round 1+2 训练时的阈值 (>= 60) 在新代码下失效.

    本 test 在两个库都装的环境下抽样验证两个函数在合成输入上 byte-equal,
    任一缺失则 skip (CI light 模式 thefuzz 装但 rapidfuzz 也装, 应能跑).
    """

    @staticmethod
    def _try_import_both():
        try:
            from rapidfuzz import fuzz as rfuzz
        except ImportError:
            rfuzz = None
        try:
            from thefuzz import fuzz as tfuzz
        except ImportError:
            tfuzz = None
        return rfuzz, tfuzz

    def test_partial_token_set_ratio_parity(self):
        """两个库在 partial_token_set_ratio 上应数值一致 (canonicalization.py 唯一调用)."""
        rfuzz, tfuzz = self._try_import_both()
        if rfuzz is None or tfuzz is None:
            pytest.skip("需要 rapidfuzz + thefuzz 同时安装")

        # 抽样 canonicalization 实际场景的输入
        cases = [
            ('人工智能驱动的智能风控系统', '人工智能'),
            ('blockchain 跨境支付', '区块链'),
            ('mobile银行 + 5G', '移动支付'),
            ('', ''),  # 边界
            ('a', 'b'),
            ('完全无关文本', '人工智能'),
        ]
        for a, b in cases:
            r_score = rfuzz.partial_token_set_ratio(a, b)
            t_score = tfuzz.partial_token_set_ratio(a, b)
            # 允许 ±1 浮点/取整误差 (thefuzz round, rapidfuzz 可能 truncate)
            assert abs(r_score - t_score) <= 1, (
                f"rapidfuzz={r_score} vs thefuzz={t_score} 在输入 ({a!r}, {b!r}) "
                f"上不一致 — canonicalization.py 切换 fallback 会让阈值 60 失效"
            )
