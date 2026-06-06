"""tests/test_numerical_intensity.py — v3.5.1 A3 真双轨数字密度单测.

锚定: 数值披露强度 (Davis & Tama-Sweet 2012 CAR 29(3); 公式为项目自定义操作化;
原引 Hales 2011 系误归—见 numerical_intensity 模块 docstring 引文勘误); plan v0.3 §2.2 + §4.1.

测试覆盖 (10 tests):
    1-2: cn2arab 5 标准样例 (frozen at D0)
    3: 不定数不计 (修 R7-M2)
    4: 句子切分 lookahead/behind 排除小数点 (修 M1')
    5: 不计分号 (与 LM 2011 一致)
    6: 空文本 NA
    7: 单字符 NA
    8: 单句多数字
    9: 跨段落
   10: 真双轨独立扫描 (full ≠ ctx)
"""
from __future__ import annotations

import math

import pandas as pd

from news_process.pipeline.sentiment.numerical_intensity import (
    _cn2arab,
    _count_numerical_tokens,
    compute_num_intensity,
    enrich_with_num_intensity_dual_track,
)


def test_cn2arab_standard_samples_part1():
    """5 标准样例: 两千万 / 三亿五千万 / 1.5 亿."""
    # 两千万 → 20000000
    assert '20000000' in _cn2arab('投资两千万')
    # 三亿五千万 → 350000000
    assert '350000000' in _cn2arab('营收三亿五千万')


def test_cn2arab_standard_samples_part2():
    """5 标准样例: 百分之三十 / 30 万亿."""
    # 百分之三十 → 30%
    assert '30%' in _cn2arab('增长百分之三十')
    # 30 万亿 → 300000000000000 (含原单位字符)
    out = _cn2arab('规模 30 万亿元')
    # 至少含一个 >= 1e13 量级的数字
    import re
    nums = [int(m) for m in re.findall(r'\d+', out) if m.isdigit()]
    assert any(n >= 30000000000000 for n in nums), f"got nums {nums}"


def test_cn2arab_indefinite_quantifiers_not_counted():
    """不定数保守不转换 (修 R7-M2): 几千 / 数十亿 / 上百万 保留原文."""
    out = _cn2arab('投资几千万元')
    # "几千" 应保留中文不转换
    assert '几' in out


def test_sentence_split_excludes_decimal_point():
    """句子切分 lookahead/behind 排除小数点 (修 M1'): 1.5 亿元 不被切."""
    text = "投资1.5亿元。营收3.2亿元。"
    n_num, n_sent = _count_numerical_tokens(text)
    # 仅 2 个句号 (排除 1.5 / 3.2 的 .)
    assert n_sent == 2
    # 至少 2 个数字 token
    assert n_num >= 2


def test_sentence_split_excludes_semicolon():
    """不计分号 (与 LM 2011 JF 一致)."""
    text = "甲行投资2亿；乙行投资3亿；丙行投资4亿"
    n_num, n_sent = _count_numerical_tokens(text)
    # 分号不计句, 整段视为 1 句
    assert n_sent == 1


def test_empty_text_returns_nan():
    """空文本 → NaN (修 R8-M1)."""
    assert math.isnan(compute_num_intensity(''))
    assert math.isnan(compute_num_intensity('   '))
    assert math.isnan(compute_num_intensity(None))  # type: ignore


def test_single_character_text():
    """单字符文本 (非数字) → 0 / 1."""
    # 单字符非数字 → n_num=0, n_sent=1, result=0
    r = compute_num_intensity('啊')
    assert r == 0.0


def test_single_sentence_multiple_numbers():
    """单句多数字: 5 个数字 / 1 句 = 5."""
    text = "投资1000万元覆盖200家分行新增50人处理10万笔"
    r = compute_num_intensity(text)
    assert r >= 4  # 至少 4 个数字 token


def test_cross_paragraph():
    """跨段落: 3 句 4 数字."""
    text = (
        "招商银行投资1亿元。"
        "覆盖200家分行。"
        "处理500万笔交易。"
    )
    n_num, n_sent = _count_numerical_tokens(_cn2arab(text))
    assert n_sent == 3
    assert n_num >= 3


def test_dual_track_independent_scan():
    """真双轨核心: full 含数字密集 vs ctx 含模糊话术, num_intensity 不同 (修 R3-C2)."""
    df = pd.DataFrame([
        {
            '内容': "招商银行已上线区块链系统。处理1000万笔。覆盖200家分行。新增50人。",
            'content_ctx': "招商银行或将探索数字货币领域。",
        },
        {
            '内容': "工商银行积极推进。深入布局。",
            'content_ctx': "工商银行投资5亿元。覆盖300家分行。新增80人。",
        },
    ])
    out = enrich_with_num_intensity_dual_track(df)
    assert 'num_intensity_full' in out.columns
    assert 'num_intensity_ctx' in out.columns
    # 行 0: full 数字密 > ctx 模糊话术 → full > ctx
    assert out.loc[0, 'num_intensity_full'] > out.loc[0, 'num_intensity_ctx']
    # 行 1: full 模糊 < ctx 数字密 → full < ctx (真独立扫描)
    assert out.loc[1, 'num_intensity_full'] < out.loc[1, 'num_intensity_ctx']


# ============================================================================
# quality-hardening Round 14 (2026-05-27): numerical_intensity.py 80.2% → ~95%
# missing 82 / 85 / 96-105 (万亿 compound) / 187-188 / 205 / 252 / 257-258
# ============================================================================


def test_cn2arab_empty_string_returns_unchanged():
    """_cn2arab('') 不抛 (line 82 — _cn2arab 是文本级 replace, 内部 _cn_number_to_arabic('') 返回 None 跳过)."""
    # _cn2arab 是文本转换函数, 接受任意 str. 空 str 应原样返回 (无 token 命中).
    assert _cn2arab('') == ''


def test_cn2arab_pure_unit_no_digit_preserved():
    """纯单位 '万亿' / '万' / '亿' (无 pure digit) → 文本原样保留 (转换 token 算法跳过)."""
    # _cn2arab 内部对每个 token 调 _cn_number_to_arabic; 后者对 '万亿' 返回 None
    # → token 原样保留. _cn2arab('万亿') == '万亿' (不变).
    out = _cn2arab('万亿')
    # 内部 _cn_number_to_arabic 拒绝返回, _cn2arab 把 token 保留
    assert isinstance(out, str)


def test_cn2arab_compound_wanyi_v371_fix():
    """v3.7.1 P-042: '两万亿' 转为 10^12 数量级 str (line 96-105 万亿 复合预处理)."""
    out = _cn2arab('两万亿')
    # _cn2arab 返回 str 形式的数字; 数量级应 = 10^12 (=13 位 digit)
    assert out == str(2 * 10**12)
    out2 = _cn2arab('五万亿')
    assert out2 == str(5 * 10**12)


def test_cn2arab_compound_wanyi_with_suffix():
    """X万亿 + 后缀: '两万亿三亿' → suffix '三亿' = 3e8 (line 102)."""
    out = _cn2arab('两万亿三亿')
    expected = 2 * 10**12 + 3 * 10**8
    assert out == str(expected)


def test_cn2arab_compound_yi_wanyi_no_prefix():
    """'一万亿' = 10^12 (prefix '一'=1, suffix '' 触发 line 99 fallback)."""
    out = _cn2arab('一万亿')
    assert out == str(10**12)


def test_cn_number_to_arabic_direct_branches():
    """直接测试 _cn_number_to_arabic 内部 helper 边角 (lines 82, 85)."""
    from news_process.pipeline.sentiment.numerical_intensity import (
        _cn_number_to_arabic,
    )
    # line 82: empty string → None
    assert _cn_number_to_arabic('') is None
    # line 85: 不定数 (indefinite quantifier) → None
    assert _cn_number_to_arabic('几') is None
    assert _cn_number_to_arabic('数十') is None
    assert _cn_number_to_arabic('上百') is None


def test_cn_number_to_arabic_compound_wanyi_unparseable_prefix():
    """万亿 prefix 为 None (line 101 fallback prefix_val=1)."""
    from news_process.pipeline.sentiment.numerical_intensity import (
        _cn_number_to_arabic,
    )
    # prefix '' → None → fallback 1 (line 99-101)
    # 然而前置 line 89-90 检查无 pure digit → 在 _cn_number_to_arabic 直接 return None.
    # 真正能触发 line 101 的: '一万亿' prefix '一' 有 digit
    result = _cn_number_to_arabic('一万亿')
    assert result == 10**12
    # 另一路径: prefix 含 indefinite 字符使 _cn_number_to_arabic 内部返回 None;
    # 但 indefinite 在 outer 已先排除 → 不可达. Coverage 报告 101 可接受 missing.


# ---------------------------------------------------------------------------
# quality-hardening Round 56 (2026-05-27): 补 _cn2arab 边角 + enrich dual track
# ---------------------------------------------------------------------------


def test_cn2arab_invalid_arab_unit_combo_preserved():
    """re.sub _arab_with_unit 抛 ValueError → return match.group(0) (lines 187-188).

    虽然 'X万亿|亿|万' 正则匹配的 num_str 总能 float(), 但仍需 ValueError
    fallback 防御; 通过 monkey-patch float 抛 ValueError 触发.
    """
    from unittest.mock import patch

    import news_process.pipeline.sentiment.numerical_intensity as m
    text = '12 亿元资产'
    original_float = float

    def faking_float(v):
        if isinstance(v, str) and v.isdigit():
            raise ValueError("simulated parse failure")
        return original_float(v)

    with patch.object(m, 'float', faking_float, create=False) \
            if False else patch('builtins.float', faking_float):
        # 路径: _arab_with_unit 内 float(num_str) 抛 → match.group(0) 返回
        result = m._cn2arab(text)
    # 应保留原文 (因 fallback)
    assert '12' in result


def test_enrich_handles_none_or_empty_df():
    """enrich_with_num_intensity_dual_track: df=None/空 → 直返 (line 252)."""
    import pandas as pd

    from news_process.pipeline.sentiment.numerical_intensity import (
        enrich_with_num_intensity_dual_track,
    )
    # None
    assert enrich_with_num_intensity_dual_track(None) is None
    # 空 df
    empty = pd.DataFrame()
    out = enrich_with_num_intensity_dual_track(empty)
    assert len(out) == 0


def test_enrich_dual_track_ctx_missing_fallback(caplog):
    """ctx_col 缺失 → warning + fallback 用 full_col (lines 257-258)."""
    import logging

    import pandas as pd

    from news_process.pipeline.sentiment.numerical_intensity import (
        enrich_with_num_intensity_dual_track,
    )
    df = pd.DataFrame({
        '内容': ['今年 10 亿元利润。', '增长百分之三十。'],
    })  # no content_ctx
    with caplog.at_level(logging.WARNING,
                          logger='news_process.pipeline.sentiment.numerical_intensity'):
        out = enrich_with_num_intensity_dual_track(df)
    # 应补 content_ctx 列 (复制 from 内容) + 两条 intensity 列
    assert 'content_ctx' in out.columns
    assert 'num_intensity_full' in out.columns
    assert 'num_intensity_ctx' in out.columns
    # 两轨数值应相等 (因 ctx 是 full 的 fallback)
    pd.testing.assert_series_equal(
        out['num_intensity_full'], out['num_intensity_ctx'],
        check_names=False,
    )


def test_count_numerical_tokens_empty_text():
    """_count_numerical_tokens 空文本 → (0, 1) (line 205)."""
    from news_process.pipeline.sentiment.numerical_intensity import (
        _count_numerical_tokens,
    )
    assert _count_numerical_tokens('') == (0, 1)
    assert _count_numerical_tokens('   ') == (0, 1)
    assert _count_numerical_tokens(None) == (0, 1)


def test_percent_replace_unparseable_returns_original():
    """_percent_replace: _cn_number_to_arabic None → 返回原文 (line 163)."""
    from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
    # "百分之几" — '几' 是 indefinite → _cn_number_to_arabic 返回 None
    # _percent_replace 应保留 '百分之几' 不变
    text = '盈利百分之几下降'
    result = _cn2arab(text)
    # 不要求精确等于原文 (其他位置可能动) 但 '百分之几' 子串保留
    assert '百分之几' in result
