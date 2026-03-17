"""
tests/test_canonicalization.py — utils/canonicalization.py 单元测试
=====================================================================
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.canonicalization import _normalize_text, canonicalize_topic


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
        cat, sub, conf = canonicalize_topic('人工智能技术研发')
        assert cat == '底层技术'
        assert sub == '人工智能'
        assert conf > 0

    def test_technology_blockchain(self):
        """区块链应归为底层技术。"""
        cat, sub, conf = canonicalize_topic('区块链分布式账本')
        assert cat == '底层技术'
        assert sub == '区块链'

    def test_technology_cloud(self):
        """云计算应归为底层技术。"""
        cat, sub, conf = canonicalize_topic('云计算平台')
        assert cat == '底层技术'
        assert sub == '云计算'

    def test_technology_bigdata(self):
        """大数据应归为底层技术。"""
        cat, sub, conf = canonicalize_topic('大数据分析平台')
        assert cat == '底层技术'
        assert sub == '大数据'

    def test_technology_iot(self):
        """物联网应归为底层技术。"""
        cat, sub, conf = canonicalize_topic('物联网传感器')
        assert cat == '底层技术'
        assert sub == '物联网'

    # --- 应用场景 ---

    def test_application_payment(self):
        """数字支付应归为应用场景。"""
        cat, sub, conf = canonicalize_topic('移动支付跨境支付')
        assert cat == '应用场景'
        assert sub == '数字支付'

    def test_application_risk(self):
        """智能风控应归为应用场景。"""
        cat, sub, conf = canonicalize_topic('智能风控反欺诈系统')
        assert cat == '应用场景'
        assert sub == '智能风控'

    def test_application_credit(self):
        """数字信贷应归为应用场景。"""
        cat, sub, conf = canonicalize_topic('数字信贷供应链金融')
        assert cat == '应用场景'
        assert sub == '数字信贷'

    def test_application_digital_bank(self):
        """数字银行应归为应用场景。"""
        cat, sub, conf = canonicalize_topic('手机银行开放银行')
        assert cat == '应用场景'
        assert sub == '数字银行'

    # --- 混合与边界 ---

    def test_mixed_keywords_weighted(self):
        """混合关键词应按加权评分判定。"""
        # 底层技术关键词权重更高时
        cat, sub, conf = canonicalize_topic('人工智能深度学习机器学习神经网络')
        assert cat == '底层技术'
        assert sub == '人工智能'

    def test_empty_input(self):
        """空字符串应返回默认值。"""
        cat, sub, conf = canonicalize_topic('')
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_none_input(self):
        """None 输入应返回默认值。"""
        cat, sub, conf = canonicalize_topic(None)
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_null_string(self):
        """'null' 字符串应返回默认值。"""
        cat, sub, conf = canonicalize_topic('null')
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_confidence_range(self):
        """置信度应在 0~1 之间。"""
        cat, sub, conf = canonicalize_topic('人工智能')
        assert 0.0 <= conf <= 1.0

    def test_no_overlap_scoring(self):
        """最长匹配优先，不应有重叠计分。"""
        # "大数据平台" 应作为整体匹配（权重2.0），而不是拆分为 "大数据"(2.0) + "平台"
        cat, sub, conf = canonicalize_topic('大数据平台')
        assert cat == '底层技术'
        assert sub == '大数据'

    def test_fullwidth_input(self):
        """全角输入应自动归一化后匹配。"""
        cat, sub, conf = canonicalize_topic('人工智能')
        assert cat == '底层技术'

    def test_subcategory_returned(self):
        """子类别应正确返回。"""
        cat, sub, conf = canonicalize_topic('联邦学习隐私计算')
        assert cat == '底层技术'
        # 子类别应为"其他底层技术"
        assert sub == '其他底层技术'


# ============================================================================
# 增强测试：边界条件与子类别覆盖
# ============================================================================

class TestCanonicalizeTopicEnhanced:
    """增强测试：覆盖更多边界条件和子类别。"""

    def test_equal_score_defaults_to_application(self):
        """当 tech_score == app_score 时应归为应用场景（代码逻辑 else 分支）。"""
        # 找一个同时含底层技术和应用场景关键词且评分相等的输入
        # "区块链数字支付" → 区块链(2.0, 底层技术) + 数字支付(2.0, 应用场景)
        cat, sub, conf = canonicalize_topic('区块链数字支付')
        assert cat == '应用场景'

    def test_empty_string(self):
        """空字符串应返回默认值。"""
        cat, sub, conf = canonicalize_topic('')
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_whitespace_only(self):
        """纯空白字符串应返回默认值。"""
        cat, sub, conf = canonicalize_topic('   ')
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_none_string(self):
        """字符串 'none' 应返回默认值。"""
        cat, sub, conf = canonicalize_topic('none')
        assert cat == '应用场景'
        assert sub == '未分类'
        assert conf == 0.0

    def test_case_insensitive_keywords(self):
        """不区分大小写的英文关键词应匹配。"""
        cat, sub, conf = canonicalize_topic('ai')
        assert cat == '底层技术'
        assert sub == '人工智能'

    def test_iot_keyword(self):
        """IoT 关键词应匹配底层技术/物联网。"""
        cat, sub, conf = canonicalize_topic('IOT技术应用')
        assert cat == '底层技术'
        assert sub == '物联网'

    def test_digital_payment_subcategory(self):
        """数字支付关键词应返回正确子类别。"""
        cat, sub, conf = canonicalize_topic('移动支付')
        assert cat == '应用场景'
        assert sub == '数字支付'

    def test_smart_risk_control(self):
        """智能风控关键词应返回正确子类别。"""
        cat, sub, conf = canonicalize_topic('智能风控反欺诈')
        assert cat == '应用场景'
        assert sub == '智能风控'

    def test_green_finance(self):
        """绿色金融关键词。"""
        cat, sub, conf = canonicalize_topic('绿色金融ESG')
        assert cat == '应用场景'
        assert sub == '绿色金融'

    def test_blockchain_technology(self):
        """区块链关键词应返回底层技术。"""
        cat, sub, conf = canonicalize_topic('区块链智能合约')
        assert cat == '底层技术'
        assert sub == '区块链'

    def test_cloud_computing(self):
        """云计算关键词应返回底层技术/云计算。"""
        cat, sub, conf = canonicalize_topic('云原生微服务容器化')
        assert cat == '底层技术'
        assert sub == '云计算'

    def test_insurance_tech(self):
        """保险科技关键词应返回应用场景。"""
        cat, sub, conf = canonicalize_topic('保险科技智能核保')
        assert cat == '应用场景'
        assert sub == '保险科技'

    def test_digital_bank(self):
        """数字银行关键词。"""
        cat, sub, conf = canonicalize_topic('手机银行开放银行')
        assert cat == '应用场景'
        assert sub == '数字银行'

    def test_unrecognized_topic(self):
        """完全无关的文本应返回未分类。"""
        cat, sub, conf = canonicalize_topic('今天天气很好')
        assert sub == '未分类'
        assert conf < 0.5  # 置信度应较低

    def test_very_long_input(self):
        """超长输入不应崩溃。"""
        long_text = '人工智能 ' * 1000
        cat, sub, conf = canonicalize_topic(long_text)
        assert cat == '底层技术'
        assert sub == '人工智能'

    def test_multiple_tech_keywords_highest_weight_wins(self):
        """多个底层技术关键词时，最高权重子类别胜出。"""
        # 2个人工智能关键词 vs 1个大数据关键词
        cat, sub, conf = canonicalize_topic('机器学习深度学习和数据分析')
        assert cat == '底层技术'
        assert sub == '人工智能'  # 人工智能权重更高

    def test_fullwidth_digits_and_letters(self):
        """全角数字和字母应正确归一化。"""
        cat, sub, conf = canonicalize_topic('５Ｇ技术')
        assert cat == '底层技术'

