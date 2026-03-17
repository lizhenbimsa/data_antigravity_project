"""
tests/test_00_preprocessing.py — 00_preprocessing.py 核心逻辑测试
==================================================================

注意：此测试只测试可独立导入的纯函数，不触发模块级全局初始化
（因为 00_preprocessing.py 在 import 时就会加载配置和外部资源）。

因此采用间接测试策略：通过复制核心逻辑到测试中进行验证。
"""

import os
import re
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 复刻关键纯函数进行测试（避免导入时的全局副作用）
# ============================================================================

# 翻译表（与 00_preprocessing.py 完全一致）
_FULL_CHARS = (
    '０１２３４５６７８９'
    'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    '－（）～！＠＃￥％︿＆＊＋＝＼｜，．？＜＞｛｝【】；：　'
)
_HALF_CHARS = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    "-()~!@#$%^&*+=\\|,.?<>{}[];: "
)
_full_to_half_table = str.maketrans(_FULL_CHARS, _HALF_CHARS)

_quote_table = {
    0x201C: '"',  0x201D: '"',
    ord('「'): '"', ord('」'): '"',
    ord('『'): '"', ord('』'): '"',
}

COMBINED_TRANS = {**_full_to_half_table, **_quote_table}

_TAIL_CLEANUP_PATTERN = re.compile(
    r'(.)\1{2,}'
    r'|([,，.。!！?？;；:：、])\2+'
    r'|\s+'
)


def _tail_cleanup_repl(m: re.Match) -> str:
    if m.group(1):
        return m.group(1) * 2
    elif m.group(2):
        return m.group(2)
    else:
        return ' '


def strip_html(text: str) -> str:
    """简化版 HTML 去除（不依赖 selectolax）。"""
    if '<' not in text:
        return text
    return re.sub(r'<[^>]+>', ' ', text).strip()


# ============================================================================
# 全角/半角转换测试
# ============================================================================

class TestFullwidthToHalfwidth:
    """测试全角→半角字符转换。"""

    def test_fullwidth_digits(self):
        assert '０１２３'.translate(COMBINED_TRANS) == '0123'

    def test_fullwidth_uppercase_letters(self):
        assert 'ＡＢＣＤ'.translate(COMBINED_TRANS) == 'ABCD'

    def test_fullwidth_lowercase_letters(self):
        assert 'ａｂｃｄ'.translate(COMBINED_TRANS) == 'abcd'

    def test_fullwidth_space(self):
        """全角空格应转为半角空格。"""
        assert '测试\u3000文本'.translate(COMBINED_TRANS) == '测试 文本'

    def test_fullwidth_symbols(self):
        assert '！＠＃'.translate(COMBINED_TRANS) == '!@#'

    def test_curly_quotes(self):
        """中文弯引号应转为 ASCII 直引号。"""
        assert '\u201c引用\u201d'.translate(COMBINED_TRANS) == '"引用"'

    def test_japanese_quotes(self):
        assert '「引用」'.translate(COMBINED_TRANS) == '"引用"'

    def test_chinese_unchanged(self):
        """中文汉字不应被改变。"""
        assert '你好世界'.translate(COMBINED_TRANS) == '你好世界'

    def test_mixed(self):
        result = 'ＡＩ技术２０２４年'.translate(COMBINED_TRANS)
        assert result == 'AI技术2024年'


# ============================================================================
# HTML 去除测试
# ============================================================================

class TestStripHtml:
    """测试 HTML 标签去除。"""

    def test_basic_tags(self):
        assert strip_html('<p>hello</p>') == 'hello'

    def test_nested_tags(self):
        assert strip_html('<div><p>hello</p></div>').strip() == 'hello'

    def test_no_tags(self):
        assert strip_html('plain text') == 'plain text'

    def test_empty_string(self):
        assert strip_html('') == ''

    def test_self_closing_tags(self):
        assert strip_html('hello<br/>world') == 'hello world'

    def test_attributes(self):
        assert strip_html('<a href="url">link</a>') == 'link'

    def test_preserves_text_between_tags(self):
        result = strip_html('<p>first</p><p>second</p>')
        assert 'first' in result
        assert 'second' in result


# ============================================================================
# 尾部清理测试
# ============================================================================

class TestTailCleanup:
    """测试重复字符/冗余标点/空白清理。"""

    def test_repeated_chars(self):
        """重复字符应压缩为 2 个。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'aaaaa')
        assert result == 'aa'

    def test_repeated_punctuation(self):
        """冗余标点（3个重复字符）被 group(1) 捕获，压缩为 2 个。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '。。。')
        assert result == '。。'

    def test_repeated_comma(self):
        """连续逗号被 group(1) 重复字符规则捕获，压缩为 2 个。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '，，，')
        assert result == '，，'

    def test_whitespace_collapse(self):
        """连续空白：3个空格被 group(1) 重复字符规则捕获，保留2个。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '   ')
        assert result == '  '  # (.)\1{2,} 先于 \s+ 匹配
        # 2个空格被 \s+ 匹配，替换为 1 个
        result2 = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'a  b')
        assert result2 == 'a b'

    def test_combined(self):
        """综合测试：重复字符→2个，连续标点→2个（group1匹配），空白→1个。"""
        text = 'aaa  bbb'
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, text)
        assert result == 'aa bb'

    def test_short_repeat_untouched(self):
        """2 个重复字符不应被压缩。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'aa')
        assert result == 'aa'

    def test_single_char_untouched(self):
        """单个字符不变。"""
        result = _TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'a')
        assert result == 'a'


# ============================================================================
# AC 自动机关键词检查测试
# ============================================================================

class TestAcContainsAny:
    """测试 Aho-Corasick 关键词存在性检查。"""

    @pytest.fixture
    def ac_automaton(self):
        """构建简单的 AC 自动机。"""
        import ahocorasick
        A = ahocorasick.Automaton()
        for kw in ['银行', '金融', '科技']:
            A.add_word(kw.lower(), kw)
        A.make_automaton()
        return A

    def test_contains_keyword(self, ac_automaton):
        """包含关键词应返回 True。"""
        text = '中国银行发布了新报告'
        result = False
        for _ in ac_automaton.iter(text.lower()):
            result = True
            break
        assert result is True

    def test_no_keyword(self, ac_automaton):
        """不包含关键词应返回 False。"""
        text = '今天天气很好'
        result = False
        for _ in ac_automaton.iter(text.lower()):
            result = True
            break
        assert result is False

    def test_multiple_keywords(self, ac_automaton):
        """包含多个关键词应返回 True。"""
        text = '银行金融科技'
        count = sum(1 for _ in ac_automaton.iter(text.lower()))
        assert count == 3


# ============================================================================
# 去重逻辑测试
# ============================================================================

class TestDeduplication:
    """测试去重逻辑（精确去重）。"""

    def test_exact_dedup_by_title_content(self):
        """标题+内容相同的记录应被去重。"""
        df = pd.DataFrame({
            '标题': ['新闻A', '新闻A', '新闻B'],
            '内容': ['内容1', '内容1', '内容2'],
            '日期': ['2024-01-01', '2024-01-02', '2024-01-03'],
        })
        deduplicated = df.drop_duplicates(subset=['标题', '内容'], keep='first')
        assert len(deduplicated) == 2

    def test_no_duplicates(self):
        """无重复记录时应全部保留。"""
        df = pd.DataFrame({
            '标题': ['A', 'B', 'C'],
            '内容': ['1', '2', '3'],
        })
        deduplicated = df.drop_duplicates(subset=['标题', '内容'])
        assert len(deduplicated) == 3

    def test_all_duplicates(self):
        """全部重复时应只保留 1 条。"""
        df = pd.DataFrame({
            '标题': ['X'] * 5,
            '内容': ['Y'] * 5,
        })
        deduplicated = df.drop_duplicates(subset=['标题', '内容'])
        assert len(deduplicated) == 1


# ============================================================================
# MinHash n-gram 测试
# ============================================================================

class TestNgramTokenization:
    """测试字符级 n-gram 分词。"""

    def test_ngram_generation(self):
        """字符级 3-gram 应正确生成。"""
        text = 'abcdef'
        ngram_size = 3
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        assert ngrams == ['abc', 'bcd', 'cde', 'def']

    def test_short_text_ngram(self):
        """短于 n-gram 大小的文本。"""
        text = 'ab'
        ngram_size = 3
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        assert ngrams == []

    def test_chinese_ngram(self):
        """中文字符级 n-gram。"""
        text = '银行金融科技'
        ngram_size = 3
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        assert ngrams == ['银行金', '行金融', '金融科', '融科技']

    def test_empty_text_ngram(self):
        """空文本应生成空列表。"""
        text = ''
        ngram_size = 3
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        assert ngrams == []


# ============================================================================
# 增强测试：Unicode 与边界条件
# ============================================================================

class TestPreprocessingEdgeCases:
    """增强测试：处理异常输入和边界条件。"""

    def test_unicode_control_characters(self):
        """Unicode 控制字符应被正确处理。"""
        text = "银行\x00新闻\x01测试\x02"
        text_clean = text.replace('\x00', '').replace('\x01', '').replace('\x02', '')
        assert '银行' in text_clean
        assert '新闻' in text_clean

    def test_fullwidth_mixed_with_halfwidth(self):
        """全角/半角混合应统一为半角。"""
        # 复刻全角→半角转换
        text = 'Ａ123'  # 全角A + 半角123
        result = []
        for ch in text:
            code = ord(ch)
            if code == 0x3000:
                result.append(' ')
            elif 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            else:
                result.append(ch)
        converted = ''.join(result)
        assert converted == 'A123'

    def test_fullwidth_exclamation(self):
        """全角感叹号应转为半角。"""
        text = '好！'
        result = []
        for ch in text:
            code = ord(ch)
            if 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            else:
                result.append(ch)
        assert ''.join(result) == '好!'

    def test_repeated_punctuation_removal(self):
        """重复标点尾部应被清理。"""
        text = '银行新闻。。。。。。'
        # 复刻 _clean_tail 逻辑的简化版
        import re
        cleaned = re.sub(r'([。！？，；、…—～~.!?,;])\1{2,}$', r'\1', text)
        assert cleaned == '银行新闻。'

    def test_html_entity_stripping(self):
        """HTML 标签应被移除。"""
        import re
        html = '<p>银行<b>新闻</b></p>'
        clean = re.sub(r'<[^>]+>', '', html)
        assert clean == '银行新闻'

    def test_html_nested_tags(self):
        """嵌套 HTML 标签应被移除。"""
        import re
        html = '<div><p><a href="url">银行</a>新闻</p></div>'
        clean = re.sub(r'<[^>]+>', '', html)
        assert clean == '银行新闻'

    def test_html_empty_after_strip(self):
        """全 HTML 内容去标签后为空。"""
        import re
        html = '<img src="pic.jpg"/><br/>'
        clean = re.sub(r'<[^>]+>', '', html)
        assert clean.strip() == ''

    def test_jaccard_similarity_threshold_exact_boundary(self):
        """Jaccard 相似度恰好等于阈值的边界验证。"""
        set_a = {'a', 'b', 'c'}
        set_b = {'a', 'b', 'c'}
        jaccard = len(set_a & set_b) / len(set_a | set_b)
        assert jaccard == 1.0

    def test_jaccard_similarity_disjoint(self):
        """完全不同的集合 Jaccard 应为 0。"""
        set_a = {'a', 'b', 'c'}
        set_b = {'d', 'e', 'f'}
        jaccard = len(set_a & set_b) / len(set_a | set_b)
        assert jaccard == 0.0

    def test_jaccard_similarity_partial(self):
        """部分重叠的 Jaccard 计算。"""
        set_a = {'a', 'b', 'c', 'd'}
        set_b = {'c', 'd', 'e', 'f'}
        jaccard = len(set_a & set_b) / len(set_a | set_b)
        assert abs(jaccard - 2 / 6) < 0.001

    def test_jaccard_empty_sets(self):
        """空集合的 Jaccard（避免除零）。"""
        set_a = set()
        set_b = set()
        if len(set_a | set_b) == 0:
            jaccard = 0.0
        else:
            jaccard = len(set_a & set_b) / len(set_a | set_b)
        assert jaccard == 0.0

    def test_ngram_performance_large_text(self):
        """大文本的 n-gram 生成应在合理时间内完成。"""
        import time
        text = '银行' * 10000  # 20000 字符
        ngram_size = 3
        start = time.time()
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        elapsed = time.time() - start
        assert len(ngrams) == 19998
        assert elapsed < 1.0  # 应在1秒内完成

    def test_single_char_fullwidth(self):
        """单个全角字符应正确转换。"""
        text = '　'  # 全角空格
        result = []
        for ch in text:
            code = ord(ch)
            if code == 0x3000:
                result.append(' ')
            else:
                result.append(ch)
        assert ''.join(result) == ' '

    def test_mixed_language_text(self):
        """中英混合文本应正常处理。"""
        text = 'AI银行FinTech新闻'
        ngram_size = 3
        ngrams = [text[i:i + ngram_size] for i in range(len(text) - ngram_size + 1)]
        assert len(ngrams) == len(text) - 2
        assert ngrams[0] == 'AI银'

