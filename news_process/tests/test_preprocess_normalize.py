"""``news_process.pipeline.preprocess.normalize`` 文本清洗管道的测试。

quality-hardening Round 24 (2026-05-27): normalize.py 0% → ~90%. 该模块此前在
tests/ 中无直接覆盖 (已有的 test_00_preprocessing.py 用本地副本测试 `_tail_cleanup_repl`
而不是 import 真实模块).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_tail_cleanup_repl_repeated_char_keeps_two():
    """重复字符 → 保留 2 个 (aaa → aa)."""
    from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
    from news_process.pipeline.preprocess.normalize import _tail_cleanup_repl
    assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'aaaaa') == 'aa'


def test_tail_cleanup_repl_redundant_punct_keeps_one():
    """重复标点 (3+ 同字符) 走 group(1) 分支 → 保留 2 个 (。。。→ 。。).

    注意 TAIL_CLEANUP_PATTERN 第一个 alternation `([^0-9])\1{2,}` 优先
    (fix omni-g-preprocess-01: 重复压缩支排除数字), 故 3+ 重复标点会先匹配
    group(1), 返回 g1*2 = 2 字符. group(2) `(标点)\2+` 只对 2-长重复触发
    (此时不命中 g1).
    """
    from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
    from news_process.pipeline.preprocess.normalize import _tail_cleanup_repl
    assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '。。。') == '。。'


def test_tail_cleanup_repl_two_repeated_punct_keeps_one():
    """2 个重复标点 → group(2) 分支 → 保留 1 个 (。。→ 。).

    `([^0-9])\1{2,}` 要求 3+ 重复 (fix omni-g-preprocess-01 排除数字),
    2 重复落 group(2) `(标点)\2+` 一次匹配 → return g2.
    """
    from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
    from news_process.pipeline.preprocess.normalize import _tail_cleanup_repl
    assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '。。') == '。'


def test_tail_cleanup_repl_whitespace_to_single_space():
    """空白序列 (\\s+) → 单个空格 (else branch, group 1 + 2 都 None)."""
    from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
    from news_process.pipeline.preprocess.normalize import _tail_cleanup_repl
    # '   ' = 3 spaces: 实测 ([^0-9])\1{2,} 会先匹配 3+ space → group(1) 命中 → 返回 ' '*2 = '  '
    # (fix omni-g-preprocess-01: 空格属 [^0-9], 行为与旧 (.)\1{2,} 一致)
    # 要触发 else (group 1 + 2 都 None) 需要 \s+ 但不是重复同字符, e.g. ' \t ' 或 '\n '
    assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, ' \t ') == ' '


def test_strip_html_with_tags():
    """HTML 标签去除."""
    from news_process.pipeline.preprocess.normalize import _strip_html
    assert _strip_html('<p>Hello <b>World</b></p>') == 'Hello World'


def test_strip_html_no_tags_short_circuit():
    """无 < 字符 → 原样返回 (short-circuit)."""
    from news_process.pipeline.preprocess.normalize import _strip_html
    assert _strip_html('plain text no tags') == 'plain text no tags'


def test_strip_html_empty_returns_empty():
    """空字符串无 HTML → 空."""
    from news_process.pipeline.preprocess.normalize import _strip_html
    assert _strip_html('') == ''


def test_clean_single_text_full_pipeline():
    """_clean_single_text 走完整 6-step 管道."""
    import opencc

    from news_process.pipeline.preprocess.normalize import _clean_single_text
    cc = opencc.OpenCC('t2s')
    text = '<p>銀行公告。。。 https://example.com</p>'
    cleaned = _clean_single_text(text, cc)
    # 繁体应转简体
    assert '银行公告' in cleaned
    # URL 应去除
    assert 'https' not in cleaned
    # HTML tags 应去除
    assert '<p>' not in cleaned


def test_clean_single_text_empty_string_short_circuit():
    """空文本走 short-circuit (line 89-90)."""
    import opencc

    from news_process.pipeline.preprocess.normalize import _clean_single_text
    cc = opencc.OpenCC('t2s')
    assert _clean_single_text('', cc) == ''
    assert _clean_single_text(None, cc) is None


def test_clean_text_batch_returns_dataframe_with_suspect_column():
    """clean_text_batch 处理 DataFrame 加 suspected_code_doc 列."""
    from news_process.pipeline.preprocess.normalize import clean_text_batch
    df = pd.DataFrame({
        '标题': ['<title>新闻头条</title>', '正常标题'],
        '内容': ['<div>正文</div>', '<html><body>banking news</body></html>'],
    })
    out = clean_text_batch(df)
    assert 'suspected_code_doc' in out.columns
    # HTML 标签应被去除
    assert '<title>' not in out['标题'].iloc[0]
    assert '<div>' not in out['内容'].iloc[0]
    # 行数不变
    assert len(out) == len(df)


def test_clean_text_batch_handles_missing_columns():
    """clean_text_batch 在缺 TEXT_COLUMNS 之一时跳过 (line 146-147)."""
    from news_process.pipeline.preprocess.normalize import clean_text_batch
    # 只有 '标题', 没有 '内容'
    df = pd.DataFrame({'标题': ['<p>测试</p>'], 'extra': ['x']})
    out = clean_text_batch(df)
    assert 'suspected_code_doc' in out.columns
    assert '<p>' not in out['标题'].iloc[0]
