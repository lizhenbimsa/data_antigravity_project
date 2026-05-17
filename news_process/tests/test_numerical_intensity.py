"""tests/test_numerical_intensity.py — v3.5.1 A3 真双轨数字密度单测.

锚定: Hales-Kuang-Venkataraman (2011) CAR 28(1) Eq.(1); plan v0.3 §2.2 + §4.1.

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
