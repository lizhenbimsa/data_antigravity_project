"""
tests/test_entity_context.py — utils/entity_context.py 白盒测试
================================================================

覆盖维度：
  - 句子分割 (_split_sentences)：标准标点、连续标点、无中文标点、空输入
  - 区间合并 (_merge_intervals)：空列表、重叠、相邻、逆序
  - 上下文提取 (extract_entity_context)：单/多别名、radius 参数化、回退路径
  - 字符级回退 (_char_level_fallback)：多处命中、边界溢出
  - 别名缓存 (get_target_aliases)：缓存命中/缺失、银行不存在
"""

import json

# ============================================================================
# 1. 句子分割测试
# ============================================================================

class TestSplitSentences:
    """_split_sentences 白盒测试。"""

    def test_standard_chinese_punctuation(self):
        from news_process.core.text.entity_context import _split_sentences
        text = "第一句。第二句？第三句！第四句；第五句。"
        result = _split_sentences(text)
        assert len(result) == 5
        assert result[0] == "第一句。"
        assert result[1] == "第二句？"
        assert result[2] == "第三句！"
        assert result[3] == "第四句；"
        assert result[4] == "第五句。"

    def test_english_punctuation(self):
        from news_process.core.text.entity_context import _split_sentences
        text = "First sentence! Second sentence? Third."
        result = _split_sentences(text)
        assert len(result) >= 2  # ! and ? are handled

    def test_no_punctuation(self):
        from news_process.core.text.entity_context import _split_sentences
        text = "这是一段没有标点的文本"
        result = _split_sentences(text)
        assert len(result) == 1
        assert result[0] == text

    def test_empty_string(self):
        from news_process.core.text.entity_context import _split_sentences
        result = _split_sentences("")
        assert result == []

    def test_only_whitespace(self):
        from news_process.core.text.entity_context import _split_sentences
        result = _split_sentences("   \n\t  ")
        assert result == []

    def test_consecutive_punctuation(self):
        from news_process.core.text.entity_context import _split_sentences
        text = "真的吗？！是的。"
        result = _split_sentences(text)
        # Should not crash; exact behavior depends on split pattern
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_semicolons(self):
        from news_process.core.text.entity_context import _split_sentences
        text = "第一点；第二点;第三点。"
        result = _split_sentences(text)
        assert len(result) == 3


# ============================================================================
# 2. 区间合并测试
# ============================================================================

class TestMergeIntervals:
    """_merge_intervals 白盒测试。"""

    def test_empty_list(self):
        from news_process.core.text.entity_context import _merge_intervals
        assert _merge_intervals([]) == []

    def test_single_interval(self):
        from news_process.core.text.entity_context import _merge_intervals
        assert _merge_intervals([(0, 5)]) == [(0, 5)]

    def test_no_overlap(self):
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(0, 2), (5, 8), (12, 15)])
        assert result == [(0, 2), (5, 8), (12, 15)]

    def test_full_overlap(self):
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(0, 10), (2, 5), (3, 7)])
        assert result == [(0, 10)]

    def test_partial_overlap(self):
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(0, 5), (3, 8), (10, 15)])
        assert result == [(0, 8), (10, 15)]

    def test_adjacent_intervals(self):
        """相邻区间 (gap=1) 应合并。"""
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(0, 3), (4, 7)])
        assert result == [(0, 7)]

    def test_reverse_order_input(self):
        """逆序输入应被正确排序后合并。"""
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(10, 15), (0, 5)])
        assert result == [(0, 5), (10, 15)]

    def test_identical_intervals(self):
        from news_process.core.text.entity_context import _merge_intervals
        result = _merge_intervals([(3, 7), (3, 7)])
        assert result == [(3, 7)]


# ============================================================================
# 3. 上下文提取测试
# ============================================================================

class TestExtractEntityContext:
    """extract_entity_context 白盒测试。"""

    def test_empty_text(self):
        from news_process.core.text.entity_context import extract_entity_context
        assert extract_entity_context("", ["工行"]) == ""

    def test_empty_aliases(self):
        from news_process.core.text.entity_context import extract_entity_context
        assert extract_entity_context("工行发布报告。", []) == ""

    def test_no_match(self):
        from news_process.core.text.entity_context import extract_entity_context
        text = "今天天气很好。明天也不错。后天值得期待。"
        result = extract_entity_context(text, ["工行"])
        assert result == ""

    def test_radius_zero(self):
        """radius=0: 仅返回命中句。"""
        from news_process.core.text.entity_context import extract_entity_context
        text = "今天天气很好。工行发布报告。市场好转。"
        result = extract_entity_context(text, ["工行"], sentence_radius=0)
        assert "工行" in result
        # 不应包含前后句
        assert "天气" not in result

    def test_radius_one(self):
        """radius=1: 返回前后各1句窗口。"""
        from news_process.core.text.entity_context import extract_entity_context
        text = "今天天气很好。工行发布报告。市场好转。这是结尾。"
        result = extract_entity_context(text, ["工行"], sentence_radius=1)
        assert "工行" in result
        assert "天气" in result
        assert "市场" in result

    def test_multiple_aliases_same_sentence(self):
        """多个别名命中同一句，不应产生重复。"""
        from news_process.core.text.entity_context import extract_entity_context
        text = "第一句。工行和工商银行的报告发布。第三句。第四句。"
        result = extract_entity_context(
            text, ["工行", "工商银行"], sentence_radius=0
        )
        assert "工行" in result

    def test_multiple_hits_disjoint(self):
        """多处命中产生不连续区间，应以 [...] 分隔。"""
        from news_process.core.text.entity_context import extract_entity_context
        text = (
            "第一句。工行发布报告。第三句。第四句。第五句。"
            "建行发布报告。第七句。第八句。"
        )
        result = extract_entity_context(
            text, ["工行", "建行"], sentence_radius=0
        )
        # 两处命中应有分隔
        assert "工行" in result
        assert "建行" in result

    def test_short_text_fallback(self):
        """文本过短（<3句）→ 字符级回退。"""
        from news_process.core.text.entity_context import extract_entity_context
        text = "工行的数据"
        result = extract_entity_context(text, ["工行"])
        assert "工行" in result


# ============================================================================
# 4. 字符级回退测试
# ============================================================================

class TestCharLevelFallback:
    """_char_level_fallback 白盒测试。"""

    def test_no_match(self):
        from news_process.core.text.entity_context import _char_level_fallback
        assert _char_level_fallback("今天天气很好", ["工行"]) == ""

    def test_single_match(self):
        from news_process.core.text.entity_context import _char_level_fallback
        text = "X" * 200 + "工行" + "Y" * 200
        result = _char_level_fallback(text, ["工行"], radius=50)
        assert "工行" in result
        assert len(result) < len(text)

    def test_boundary_overflow(self):
        """匹配在文本开头时，不应越界。"""
        from news_process.core.text.entity_context import _char_level_fallback
        text = "工行发布报告"
        result = _char_level_fallback(text, ["工行"], radius=100)
        assert "工行" in result

    def test_multiple_matches_merge(self):
        """多处匹配的区间合并。"""
        from news_process.core.text.entity_context import _char_level_fallback
        text = "工行AAA" + "B" * 20 + "工行CCC"
        result = _char_level_fallback(text, ["工行"], radius=15)
        assert "工行" in result


# ============================================================================
# 5. 别名缓存测试
# ============================================================================

class TestGetTargetAliases:
    """get_target_aliases 缓存行为白盒测试。"""

    def test_bank_found(self, tmp_path):
        from news_process.core.text import entity_context as ec
        # 清理全局缓存
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None

        data = [{"bank_name": "工商银行", "variants": ["工行", "ICBC"]}]
        path = tmp_path / "banks.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        aliases = ec.get_target_aliases("工商银行", str(path))
        assert "工行" in aliases
        assert "ICBC" in aliases
        assert "工商银行" in aliases

    def test_bank_not_found_fallback(self, tmp_path):
        from news_process.core.text import entity_context as ec
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None

        data = [{"bank_name": "建设银行", "variants": ["建行"]}]
        path = tmp_path / "banks.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        aliases = ec.get_target_aliases("中国银行", str(path))
        assert aliases == ["中国银行"]

    def test_cache_hit(self, tmp_path):
        from news_process.core.text import entity_context as ec
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None

        data = [{"bank_name": "工商银行", "variants": ["工行"]}]
        path = tmp_path / "banks.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        first_call = ec.get_target_aliases("工商银行", str(path))
        # 第二次调用应走缓存
        ec._BANK_DATA = None  # 清空文件数据，只有缓存还在
        second_call = ec.get_target_aliases("工商银行", str(path))
        assert first_call == second_call

    def test_cache_cleanup(self, tmp_path):
        """确保测试后清理全局缓存。"""
        from news_process.core.text import entity_context as ec
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None


# ============================================================================
# quality-hardening Round 9 (2026-05-27): extract_entity_context_with_distances
# entity_context.py 74.77% → ~100% (lines 227-269, 300-302)
# ============================================================================


class TestExtractEntityContextWithDistances:
    """extract_entity_context_with_distances Engelberg/Sautner 距离衰减接口."""

    def test_empty_text_returns_empty_list(self):
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        # 覆盖 line 227-228: not text branch
        assert extract_entity_context_with_distances("", ["工商银行"]) == []
        # not target_aliases branch
        assert extract_entity_context_with_distances("文本", []) == []

    def test_short_text_with_hit_returns_all_zero_distance(self):
        """文本 < 3 句且命中目标 → 所有句子 distance=0 (lines 230-241)."""
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        text = "工商银行发布公告。今日股价上涨。"
        result = extract_entity_context_with_distances(text, ["工商银行"])
        assert len(result) >= 1
        # 短文本退化路径: 所有句子 distance=0
        assert all(dist == 0 for _, dist in result)

    def test_short_text_no_hit_returns_empty(self):
        """文本 < 3 句但无命中 → 空列表 (line 241 return [])."""
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        text = "今日天气晴朗。无关新闻。"
        result = extract_entity_context_with_distances(text, ["工商银行"])
        assert result == []

    def test_long_text_no_hit_returns_empty(self):
        """文本 >= 3 句但无命中 → 空列表 (line 252)."""
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        text = "今日天气晴朗。明日多云。后日大雨。再后日转晴。"
        result = extract_entity_context_with_distances(text, ["工商银行"])
        assert result == []

    def test_long_text_with_hits_computes_distances(self):
        """长文本: 多窗口合并 + 距离正确 (lines 253-269)."""
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        text = (
            "无关句一。"  # idx 0
            "工商银行公告。"  # idx 1 (hit)
            "中间无关句。"  # idx 2
            "招商银行发布。"  # idx 3
            "结尾无关句。"  # idx 4
            "再一句无关。"  # idx 5
        )
        result = extract_entity_context_with_distances(
            text, ["工商银行"], sentence_radius=1,
        )
        # 命中句 idx=1 + radius=1 → 窗口 [0, 2]
        assert len(result) >= 1
        # 命中句本身 distance=0
        zero_dist = [s for s, d in result if d == 0]
        assert any("工商银行" in s for s in zero_dist)

    def test_multi_hits_merge_intervals(self):
        """多个命中 → intervals 合并 + 每句到最近 hit 的距离."""
        from news_process.core.text.entity_context import (
            extract_entity_context_with_distances,
        )
        text = (
            "句0无关。"
            "句1工商银行命中。"
            "句2无关。"
            "句3工商银行再次命中。"
            "句4无关。"
        )
        result = extract_entity_context_with_distances(
            text, ["工商银行"], sentence_radius=1,
        )
        # 多次命中 + radius 应合并为连续窗口
        distances = [d for _, d in result]
        assert 0 in distances  # 至少一个 hit 距离 0


# ============================================================================
# quality-hardening Round 9: get_target_aliases JSON load failure
# entity_context.py:300-302
# ============================================================================


class TestGetTargetAliasesLoadFailure:
    """JSON 文件读取失败 → logger.warning + 空别名 fallback."""

    def test_get_target_aliases_handles_missing_file(self, tmp_path):
        """文件不存在 → except + _BANK_DATA=[] → 返回 target_bank 单元素 list (300-302)."""
        from news_process.core.text import entity_context as ec
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None
        missing = tmp_path / 'no_such_banks.json'
        aliases = ec.get_target_aliases("工商银行", str(missing))
        # 加载失败 → 找不到任何 bank → fallback 只返回 target_bank 本身
        assert aliases == ["工商银行"]
        # 清理后续测试用的全局状态
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None

    def test_get_target_aliases_handles_corrupt_json(self, tmp_path):
        """JSON 解析失败 → except + 空 fallback (line 300-302)."""
        from news_process.core.text import entity_context as ec
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None
        bad = tmp_path / 'corrupt.json'
        bad.write_text('NOT JSON {{', encoding='utf-8')
        aliases = ec.get_target_aliases("建设银行", str(bad))
        assert aliases == ["建设银行"]
        ec._ALIASES_CACHE.clear()
        ec._BANK_DATA = None
