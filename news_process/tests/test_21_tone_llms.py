"""
tests/test_21_tone_llms.py — 21_tone_llms.py 核心逻辑测试
==========================================================

测试 LLM 语义精筛中的纯函数：JSON 解析、多数投票、批量 Prompt 构建。
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 复刻纯函数（避免导入 21_tone_llms.py 时触发配置加载和 API 初始化）
# ============================================================================

def parse_json_response(res_text: str) -> dict:
    """尝试从大模型结果中解析 JSON。"""
    try:
        text = res_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception:
        return {}


def majority_vote_bool(bools: list) -> bool:
    """严格多数决判断真伪（超过半数才通过）。"""
    if not bools:
        return False
    return sum(bools) > (len(bools) / 2.0)


def majority_vote_sentiment(sents: list) -> str:
    """多数决判断情感，平局降级为中性。"""
    from collections import Counter
    if not sents:
        return "中性"
    c = Counter(sents)
    most_common = c.most_common()
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        return "中性"
    return most_common[0][0]


def parse_batch_json_response(res_text: str, expected_ids: list) -> dict:
    """解析批量 JSON 数组响应。"""
    try:
        text = res_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        parsed = json.loads(text.strip())

        if not isinstance(parsed, list):
            return {}

        result = {}
        for item in parsed:
            if isinstance(item, dict) and 'input_id' in item:
                result[str(item['input_id'])] = item

        if len(result) != len(expected_ids):
            return {}

        return result
    except Exception:
        return {}


# ============================================================================
# parse_json_response 测试
# ============================================================================

class TestParseJsonResponse:
    """测试 LLM JSON 响应解析。"""

    def test_valid_json(self):
        """正常 JSON 应正确解析。"""
        text = '{"is_bank_fintech_news": true, "sentiment": "正面"}'
        result = parse_json_response(text)
        assert result['is_bank_fintech_news'] is True
        assert result['sentiment'] == '正面'

    def test_markdown_wrapped(self):
        """```json 包裹的 JSON 应正确解析。"""
        text = '```json\n{"is_bank_fintech_news": false}\n```'
        result = parse_json_response(text)
        assert result['is_bank_fintech_news'] is False

    def test_markdown_no_json_tag(self):
        """``` 包裹（无 json 标签）应正确解析。"""
        text = '```\n{"key": "value"}\n```'
        result = parse_json_response(text)
        assert result['key'] == 'value'

    def test_invalid_json(self):
        """无效 JSON 应返回空字典。"""
        result = parse_json_response('这不是JSON')
        assert result == {}

    def test_empty_string(self):
        """空字符串应返回空字典。"""
        result = parse_json_response('')
        assert result == {}

    def test_nested_json(self):
        """嵌套 JSON 应正确解析。"""
        text = '{"outer": {"inner": 42}}'
        result = parse_json_response(text)
        assert result['outer']['inner'] == 42

    def test_json_with_unicode(self):
        """含中文 Unicode 的 JSON。"""
        text = '{"sentiment": "正面", "reason": "银行创新突破"}'
        result = parse_json_response(text)
        assert result['sentiment'] == '正面'

    def test_json_with_whitespace(self):
        """前后有空白的 JSON。"""
        text = '  \n  {"key": "value"}  \n  '
        result = parse_json_response(text)
        assert result['key'] == 'value'

    def test_bool_string_values(self):
        """字符串布尔值解析。"""
        text = '{"is_bank_fintech_news": true, "verification_confidence": 0.95}'
        result = parse_json_response(text)
        assert result['is_bank_fintech_news'] is True
        assert result['verification_confidence'] == 0.95


# ============================================================================
# majority_vote_bool 测试
# ============================================================================

class TestMajorityVoteBool:
    """测试布尔多数投票。"""

    def test_all_true(self):
        assert majority_vote_bool([True, True, True]) is True

    def test_all_false(self):
        assert majority_vote_bool([False, False, False]) is False

    def test_majority_true(self):
        assert majority_vote_bool([True, True, False]) is True

    def test_majority_false(self):
        assert majority_vote_bool([True, False, False]) is False

    def test_tie_two(self):
        """双方 1:1 平局应返回 False（未超半数）。"""
        assert majority_vote_bool([True, False]) is False

    def test_empty_list(self):
        assert majority_vote_bool([]) is False

    def test_single_true(self):
        assert majority_vote_bool([True]) is True

    def test_single_false(self):
        assert majority_vote_bool([False]) is False

    def test_five_models_3_2(self):
        """5 模型 3:2 应返回 True。"""
        assert majority_vote_bool([True, True, True, False, False]) is True

    def test_five_models_2_3(self):
        """5 模型 2:3 应返回 False。"""
        assert majority_vote_bool([True, True, False, False, False]) is False


# ============================================================================
# majority_vote_sentiment 测试
# ============================================================================

class TestMajorityVoteSentiment:
    """测试情感多数投票。"""

    def test_majority_positive(self):
        assert majority_vote_sentiment(['正面', '正面', '中性']) == '正面'

    def test_majority_negative(self):
        assert majority_vote_sentiment(['负面', '负面', '正面']) == '负面'

    def test_majority_neutral(self):
        assert majority_vote_sentiment(['中性', '中性', '正面']) == '中性'

    def test_tie_degrades_to_neutral(self):
        """2:2 平局应降级为中性（而不是选票数最多的）。"""
        result = majority_vote_sentiment(['正面', '负面'])
        assert result == '中性'

    def test_three_way_tie(self):
        """三方平局应降级为中性。"""
        result = majority_vote_sentiment(['正面', '负面', '中性'])
        assert result == '中性'

    def test_empty_list(self):
        assert majority_vote_sentiment([]) == '中性'

    def test_single_value(self):
        assert majority_vote_sentiment(['正面']) == '正面'

    def test_all_same(self):
        assert majority_vote_sentiment(['负面', '负面', '负面']) == '负面'


# ============================================================================
# parse_batch_json_response 测试
# ============================================================================

class TestParseBatchJsonResponse:
    """测试批量 JSON 数组解析。"""

    def test_valid_batch(self):
        """正常批量 JSON 数组。"""
        text = json.dumps([
            {"input_id": "0", "is_bank_fintech_news": True},
            {"input_id": "1", "is_bank_fintech_news": False},
        ])
        result = parse_batch_json_response(text, ["0", "1"])
        assert len(result) == 2
        assert result["0"]["is_bank_fintech_news"] is True
        assert result["1"]["is_bank_fintech_news"] is False

    def test_count_mismatch(self):
        """条目数量不匹配应返回空字典。"""
        text = json.dumps([
            {"input_id": "0", "is_bank_fintech_news": True},
        ])
        result = parse_batch_json_response(text, ["0", "1"])
        assert result == {}

    def test_missing_input_id(self):
        """缺少 input_id 字段应返回空字典。"""
        text = json.dumps([
            {"is_bank_fintech_news": True},
            {"input_id": "1"},
        ])
        result = parse_batch_json_response(text, ["0", "1"])
        assert result == {}

    def test_not_array(self):
        """非数组应返回空字典。"""
        text = '{"is_bank_fintech_news": true}'
        result = parse_batch_json_response(text, ["0"])
        assert result == {}

    def test_invalid_json(self):
        """无效 JSON 应返回空字典。"""
        result = parse_batch_json_response('not json', ["0"])
        assert result == {}

    def test_markdown_wrapped_batch(self):
        """```json 包裹的批量 JSON。"""
        batch_data = [
            {"input_id": "0", "sentiment": "正面"},
            {"input_id": "1", "sentiment": "负面"},
        ]
        text = f'```json\n{json.dumps(batch_data)}\n```'
        result = parse_batch_json_response(text, ["0", "1"])
        assert len(result) == 2

    def test_numeric_input_id(self):
        """数字类型 input_id 应转为字符串。"""
        text = json.dumps([
            {"input_id": 0, "sentiment": "正面"},
            {"input_id": 1, "sentiment": "负面"},
        ])
        result = parse_batch_json_response(text, ["0", "1"])
        assert len(result) == 2
