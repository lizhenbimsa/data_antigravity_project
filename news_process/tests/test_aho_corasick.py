"""
tests/test_aho_corasick.py — utils/aho_corasick.py 单元测试
=============================================================
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.aho_corasick import (
    load_bank_names, load_exclusion_patterns, is_match_excluded,
    analyze_bank_matches, load_fintech_dict, analyze_fintech_matches,
)


# ============================================================================
# load_bank_names 测试
# ============================================================================

class TestLoadBankNames:
    """测试银行名称加载与 AC 自动机构建。"""

    def test_valid_file(self, mock_bank_names_json):
        """正确加载银行名称并构建 AC 自动机。"""
        banks, ac, variant_map = load_bank_names(mock_bank_names_json)
        assert len(banks) == 3
        assert ac is not None
        assert '中国工商银行' in variant_map
        assert '工行' in variant_map

    def test_missing_file(self):
        """文件不存在返回空列表。"""
        banks, ac, variant_map = load_bank_names('/nonexistent/file.json')
        assert banks == []
        assert ac is None
        assert variant_map == {}

    def test_empty_file(self, tmp_dir):
        """空列表 JSON 返回空结果。"""
        path = tmp_dir / 'empty_banks.json'
        path.write_text('[]', encoding='utf-8')
        banks, ac, variant_map = load_bank_names(str(path))
        assert banks == []
        assert ac is None

    def test_variant_to_bank_mapping(self, mock_bank_names_json):
        """变体→银行索引映射应正确。"""
        banks, ac, variant_map = load_bank_names(mock_bank_names_json)
        # 工商银行的变体应指向索引 0
        assert variant_map['工行'] == 0
        # 建设银行的变体应指向索引 1
        assert variant_map['建行'] == 1


# ============================================================================
# load_exclusion_patterns 测试
# ============================================================================

class TestLoadExclusionPatterns:
    """测试否定模式和短名歧义消解加载。"""

    def test_valid_file(self, mock_bank_name_exclusions_json):
        """正确加载否定模式配置。"""
        neg_ac, short_excl, ctx_window = load_exclusion_patterns(
            mock_bank_name_exclusions_json
        )
        assert neg_ac is not None
        assert '工行' in short_excl
        assert ctx_window == 5

    def test_missing_file(self):
        """文件不存在应返回 None 和空字典。"""
        neg_ac, short_excl, ctx_window = load_exclusion_patterns(
            '/nonexistent/file.json'
        )
        assert neg_ac is None
        assert short_excl == {}


# ============================================================================
# is_match_excluded 测试
# ============================================================================

class TestIsMatchExcluded:
    """测试匹配排除检查。"""

    def test_negation_exclusion(self, mock_bank_name_exclusions_json):
        """否定模式应排除匹配。"""
        neg_ac, short_excl, ctx_window = load_exclusion_patterns(
            mock_bank_name_exclusions_json
        )
        text = '中国银行业监管'
        # 模拟 "中国银行" 在 "中国银行业" 中被匹配
        # match_end_pos = "中国银行"的最后一个字符位置 = 3
        result = is_match_excluded(
            text, 3, '中国银行',
            negation_ac=neg_ac,
            short_name_exclusions=short_excl,
            context_window=ctx_window,
        )
        assert result == 'negation'

    def test_short_name_exclusion(self, mock_bank_name_exclusions_json):
        """短名歧义应排除匹配。"""
        neg_ac, short_excl, ctx_window = load_exclusion_patterns(
            mock_bank_name_exclusions_json
        )
        text = '该施工行为违规'
        # "工行" 在 "施工行为" 中
        # 找到 "工行" 位置: text.find("工行") = 2, match_end_pos = 3
        result = is_match_excluded(
            text, 3, '工行',
            negation_ac=neg_ac,
            short_name_exclusions=short_excl,
            context_window=ctx_window,
        )
        assert result == 'short_name'

    def test_no_exclusion(self, mock_bank_name_exclusions_json):
        """正常匹配不应被排除。"""
        neg_ac, short_excl, ctx_window = load_exclusion_patterns(
            mock_bank_name_exclusions_json
        )
        text = '中国工商银行发布了最新公告'
        # "工行" 单独出现，不在排除上下文中
        # 需要一个不触发排除的场景
        result = is_match_excluded(
            text, 6, '工商银行',
            negation_ac=neg_ac,
            short_name_exclusions=short_excl,
            context_window=ctx_window,
        )
        assert result is None


# ============================================================================
# analyze_bank_matches 测试
# ============================================================================

class TestAnalyzeBankMatches:
    """测试银行匹配分析。"""

    @pytest.fixture
    def bank_setup(self, mock_bank_names_json):
        """构建测试用的银行 AC 自动机。"""
        banks, ac, variant_map = load_bank_names(mock_bank_names_json)
        return banks, ac

    def test_single_bank_match(self, bank_setup):
        """单银行匹配应正确识别。"""
        banks, ac = bank_setup
        content = ('中国工商银行今日宣布新产品上线。工商银行表示该产品利用了金融科技。'
                    '工行金融科技部负责人对此进行了说明。')
        result = analyze_bank_matches(
            content, '工商银行新闻', ac, banks,
            split_ratio=0.5, min_name_occurrences=2,
            min_upper=1, min_lower=1,
        )
        assert result['is_bank_news'] is True
        assert len(result['matched_banks']) > 0
        assert result['matched_banks'][0]['bank_name'] == '中国工商银行'

    def test_empty_content(self, bank_setup):
        """空内容应返回 False。"""
        banks, ac = bank_setup
        result = analyze_bank_matches(
            '', '', ac, banks,
            split_ratio=0.5, min_name_occurrences=3,
        )
        assert result['is_bank_news'] is False

    def test_no_bank_ac(self):
        """无 AC 自动机时应返回 False。"""
        result = analyze_bank_matches(
            '中国工商银行', '标题', None, [],
            split_ratio=0.5,
        )
        assert result['is_bank_news'] is False

    def test_multi_bank_match(self, bank_setup):
        """多银行匹配应正确识别。"""
        banks, ac = bank_setup
        content = ('中国工商银行与中国建设银行联合推出。工商银行方面表示合作进展良好。'
                    '建设银行也发表了声明。工行和建行将继续深化合作。')
        result = analyze_bank_matches(
            content, '工行建行合作', ac, banks,
            split_ratio=0.5, min_name_occurrences=2,
            min_upper=1, min_lower=1,
        )
        assert result['is_bank_news'] is True
        bank_names = [b['bank_name'] for b in result['matched_banks']]
        assert '中国工商银行' in bank_names

    def test_threshold_not_met(self, bank_setup):
        """未达到最低出现次数阈值应返回 False。"""
        banks, ac = bank_setup
        content = '工行'  # 仅出现1次
        result = analyze_bank_matches(
            content, '', ac, banks,
            split_ratio=0.5, min_name_occurrences=5,
            min_upper=3, min_lower=3,
        )
        assert result['is_bank_news'] is False


# ============================================================================
# load_fintech_dict 测试
# ============================================================================

class TestLoadFintechDict:
    """测试金融科技词典加载。"""

    def test_valid_file(self, mock_fintech_dict_json):
        """正确加载词典并构建 AC 自动机。"""
        keywords, ac = load_fintech_dict(mock_fintech_dict_json)
        assert len(keywords) == 13
        assert ac is not None

    def test_missing_file(self):
        """文件不存在应返回空列表。"""
        keywords, ac = load_fintech_dict('/nonexistent/file.json')
        assert keywords == []
        assert ac is None

    def test_keywords_sorted_by_length(self, mock_fintech_dict_json):
        """关键词应按长度降序排列。"""
        keywords, _ = load_fintech_dict(mock_fintech_dict_json)
        for i in range(len(keywords) - 1):
            assert len(keywords[i]) >= len(keywords[i + 1])


# ============================================================================
# analyze_fintech_matches 测试
# ============================================================================

class TestAnalyzeFintechMatches:
    """测试金融科技匹配分析。"""

    @pytest.fixture
    def fintech_setup(self, mock_fintech_dict_json):
        """构建测试用的金融科技 AC 自动机。"""
        keywords, ac = load_fintech_dict(mock_fintech_dict_json)
        return keywords, ac

    def test_fintech_news_detected(self, fintech_setup):
        """金融科技新闻应被正确识别。"""
        _, ac = fintech_setup
        content = ('人工智能和大数据技术在金融领域的应用日益广泛。'
                    '云计算平台为金融科技提供了基础设施支撑。'
                    '智能风控系统利用机器学习技术进行实时监控。')
        result = analyze_fintech_matches(
            content, '金融科技人工智能创新', ac,
            split_ratio=0.5, min_distinct_keywords=3,
            min_upper=1, min_lower=1,
        )
        assert result['is_fintech_news'] is True
        assert result['distinct_count'] >= 3

    def test_non_fintech_news(self, fintech_setup):
        """非金融科技新闻应返回 False。"""
        _, ac = fintech_setup
        content = '今天天气晴朗，适合外出散步。冬季食谱推荐。'
        result = analyze_fintech_matches(
            content, '天气预报', ac,
            split_ratio=0.5, min_distinct_keywords=3,
        )
        assert result['is_fintech_news'] is False

    def test_diversity_requirement(self, fintech_setup):
        """未满足多样性条件（不同关键词数）应返回 False。"""
        _, ac = fintech_setup
        content = '人工智能人工智能人工智能'  # 仅一个关键词
        result = analyze_fintech_matches(
            content, '', ac,
            split_ratio=0.5, min_distinct_keywords=3,
        )
        assert result['is_fintech_news'] is False
        assert result['distinct_count'] < 3

    def test_empty_content(self, fintech_setup):
        """空内容应返回 False。"""
        _, ac = fintech_setup
        result = analyze_fintech_matches(
            '', '', ac, split_ratio=0.5,
        )
        assert result['is_fintech_news'] is False

    def test_title_match(self, fintech_setup):
        """标题中的关键词应被检测。"""
        _, ac = fintech_setup
        content = '这是一篇普通文章。'
        result = analyze_fintech_matches(
            content, '人工智能大数据云计算', ac,
            split_ratio=0.5, min_distinct_keywords=3,
            min_upper=1,
        )
        assert result['in_title'] is True
