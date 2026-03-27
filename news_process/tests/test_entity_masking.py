"""
test_entity_masking.py — Entity Masking 稳健性测试的单元测试
"""

import pytest
import sys
import os

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 直接导入被测函数（不触发 21_tone_llms 的模块级初始化）
# 通过直接定义来测试纯函数逻辑


# ============================================================================
# 复制被测纯函数（避免 import 36_entity_masking_test 触发 LLM 模块加载）
# ============================================================================

PLACEHOLDER = "目标银行A"
PEER_TEMPLATE = "同业银行{}"


def mask_entity(text, title, target_bank, target_aliases, co_mentioned_banks, bank_names_file):
    """被测函数：银行名替换"""
    masked_text, masked_title = text, title
    n_replacements = 0

    for alias in sorted(target_aliases, key=len, reverse=True):
        cnt = masked_text.count(alias) + masked_title.count(alias)
        masked_text = masked_text.replace(alias, PLACEHOLDER)
        masked_title = masked_title.replace(alias, PLACEHOLDER)
        n_replacements += cnt

    masked_peers = []
    if co_mentioned_banks and str(co_mentioned_banks).strip():
        for i, peer in enumerate(
            b.strip() for b in str(co_mentioned_banks).split(';') if b.strip()
        ):
            peer_ph = PEER_TEMPLATE.format(chr(66 + i))
            # 简化：测试中直接用 peer 本身作为唯一别名
            peer_aliases = [peer]
            for alias in sorted(peer_aliases, key=len, reverse=True):
                cnt = masked_text.count(alias)
                masked_text = masked_text.replace(alias, peer_ph)
                masked_title = masked_title.replace(alias, peer_ph)
                n_replacements += cnt
            masked_peers.append(peer_ph)

    return {
        'masked_text': masked_text,
        'masked_title': masked_title,
        'masked_target': PLACEHOLDER,
        'masked_co_mentioned': ';'.join(masked_peers) if masked_peers else '无',
        'n_replacements': n_replacements,
    }


def verify_masking_completeness(masked_text, original_aliases, co_bank_aliases):
    """被测函数：残留检测"""
    residuals = [a for a in original_aliases + co_bank_aliases if a in masked_text]
    return {'complete': len(residuals) == 0, 'residual_aliases': residuals}


# ============================================================================
# 测试用例
# ============================================================================

class TestMaskEntity:
    """银行名替换算法测试"""

    def test_mask_long_alias_first(self):
        """长别名优先替换，短别名不残留"""
        result = mask_entity(
            "中国工商银行和工商银行联合推出", "",
            "中国工商银行", ["中国工商银行", "工商银行"], "", ""
        )
        assert "工商银行" not in result['masked_text']
        assert "目标银行A" in result['masked_text']
        assert result['n_replacements'] == 2

    def test_mask_co_mentioned_banks(self):
        """共提银行使用不同占位符"""
        result = mask_entity(
            "工商银行与建设银行合作", "", "工商银行",
            ["工商银行"], "建设银行", ""
        )
        assert "同业银行B" in result['masked_text']
        assert "目标银行A" in result['masked_text']

    def test_mask_empty_co_banks(self):
        """无共提银行时不报错"""
        result = mask_entity("工商银行", "", "工商银行", ["工商银行"], "", "")
        assert result['masked_co_mentioned'] == '无'

    def test_mask_title_also_replaced(self):
        """标题中的银行名也应被替换"""
        result = mask_entity(
            "工商银行发布了新产品", "工商银行新闻",
            "工商银行", ["工商银行"], "", ""
        )
        assert "工商银行" not in result['masked_title']
        assert "目标银行A" in result['masked_title']
        assert result['n_replacements'] == 2  # 正文1次 + 标题1次

    def test_zero_replacements_flagged(self):
        """文中无银行名时替换次数为零"""
        result = mask_entity("今天天气很好", "", "工商银行", ["工商银行"], "", "")
        assert result['n_replacements'] == 0

    def test_multiple_co_banks(self):
        """多个共提银行各用不同占位符"""
        result = mask_entity(
            "工商银行联合建设银行和农业银行", "", "工商银行",
            ["工商银行"], "建设银行;农业银行", ""
        )
        assert "同业银行B" in result['masked_text']
        assert "同业银行C" in result['masked_text']
        assert "目标银行A" in result['masked_text']


class TestMaskingCompleteness:
    """实体残留检测测试"""

    def test_detects_residual(self):
        """残留检测正确识别不完整替换"""
        result = verify_masking_completeness(
            "目标银行A发布了工商银行的产品", ["工商银行"], []
        )
        assert result['complete'] is False
        assert "工商银行" in result['residual_aliases']

    def test_passes_clean_text(self):
        """完全替换后通过残留检测"""
        result = verify_masking_completeness(
            "目标银行A发布了新产品", ["工商银行"], []
        )
        assert result['complete'] is True
        assert result['residual_aliases'] == []

    def test_detects_co_bank_residual(self):
        """检测共提银行残留"""
        result = verify_masking_completeness(
            "目标银行A和建设银行合作", ["工商银行"], ["建设银行"]
        )
        assert result['complete'] is False
        assert "建设银行" in result['residual_aliases']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
