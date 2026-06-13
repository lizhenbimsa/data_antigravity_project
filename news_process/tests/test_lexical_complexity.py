"""tests/test_lexical_complexity.py — 词汇/句法复杂度 $0 测度族单测 (批 #2–#6).

断言以**稳健性质** (取值域 / 单调比较) 为主, 不绑定 posseg 逐 token 精确结果。
"""
from __future__ import annotations

import math

from news_process.pipeline.sentiment.lexical_complexity import (
    HAN_COUNT_KEY,
    LEXICAL_COMPLEXITY_KEYS,
    WORD_COUNT_KEY,
    _common_char_set,
    _rare_word_cutoff,
    compute_lexical_complexity,
)

_ALL_KEYS = set(LEXICAL_COMPLEXITY_KEYS) | {WORD_COUNT_KEY, HAN_COUNT_KEY}


def _finite_or_nan_in_unit(v: float) -> bool:
    return math.isnan(v) or (0.0 <= v <= 1.0)


def test_empty_and_sentinel_all_nan():
    for bad in ("", "   ", "nan", "None", "<NA>"):
        r = compute_lexical_complexity(bad)
        assert set(r.keys()) == _ALL_KEYS
        assert all(math.isnan(v) for v in r.values())


def test_all_keys_present_and_in_range():
    r = compute_lexical_complexity(
        "中国工商银行2023年净利润增长百分之三十，但是不良率仍需关注。"
    )
    assert set(r.keys()) == _ALL_KEYS
    # 比率类键 ∈ [0,1] 或 nan; 词数计数键单独校验 (非比率)
    # fix(omni-g-numlex-05, 2026-06-11) + fix(hanzi-char-dual, 2026-06-13) 断言更新:
    # 'redundancy_log_length' (字符口径) 与 'redundancy_han_log_length' (汉字口径) 均为
    # ln(长度) 控制变体列 (非 [0,1] 比率), 从比率断言豁免、单独校验 > 0。
    _NON_RATIO_KEYS = {'redundancy_log_length', 'redundancy_han_log_length'}
    ratio_keys = [k for k in LEXICAL_COMPLEXITY_KEYS if k not in _NON_RATIO_KEYS]
    assert all(_finite_or_nan_in_unit(r[k]) for k in ratio_keys)
    assert r['redundancy_log_length'] > 0  # 该样例 > 3 字 → ln(长度) 有限正值
    assert r['redundancy_han_log_length'] > 0  # 该样例 ≥ 3 汉字 → ln(汉字数) 有限正值
    assert r[WORD_COUNT_KEY] >= 1.0  # 该样例有多个词
    assert r[HAN_COUNT_KEY] >= 1.0  # 该样例有多个汉字 (汉字口径文章长度)


def test_helpers_nonempty():
    cc = _common_char_set()
    assert len(cc) > 1000  # 常用字集应有数千字
    assert '的' in cc and '银' in cc  # 高频字必在
    assert _rare_word_cutoff() > 0


def test_hard_char_obscure_gt_common():
    common = compute_lexical_complexity("今天公司开会讨论业务发展")
    obscure = compute_lexical_complexity("饕餮魑魅魍魉貔貅")
    assert obscure['hard_char_ratio'] > common['hard_char_ratio']


def test_hard_char_short_text_nan():
    # < _MIN_HAN_CHARS(5) Han 字 → nan
    assert math.isnan(compute_lexical_complexity("银行。。。")['hard_char_ratio'])


def test_function_word_heavy_gt_content_heavy():
    fw = compute_lexical_complexity("他在和我们的这个会议上又说了一些")
    cw = compute_lexical_complexity("银行净利润大幅增长营收创历史新高")
    assert fw['function_word_ratio'] > cw['function_word_ratio']


def test_adversative_present_vs_absent():
    with_adv = compute_lexical_complexity("业绩增长但是风险上升然而前景乐观")
    no_adv = compute_lexical_complexity("业绩增长风险上升前景乐观稳健")
    assert with_adv['adversative_ratio'] > 0.0
    assert no_adv['adversative_ratio'] == 0.0


def test_specificity_entities_gt_vague():
    concrete = compute_lexical_complexity("中国工商银行行长在北京宣布投资100亿元")
    vague = compute_lexical_complexity("该机构宣布了一项重要决定将持续推进相关工作")
    assert concrete['specificity_index'] > vague['specificity_index']


def test_redundancy_repeated_gt_varied():
    repeated = compute_lexical_complexity("数字化转型数字化转型数字化转型数字化转型")
    varied = compute_lexical_complexity("数字化转型服务实体经济推动高质量发展创新")
    assert repeated['within_doc_redundancy'] > varied['within_doc_redundancy']


# ── fix(hanzi-char-dual, 2026-06-13): 汉字口径冗余孪生 (字符 vs 汉字双口径) ──
def test_han_redundancy_repeated_gt_varied():
    # 汉字口径冗余与字符口径同向: 复读 > 多样
    repeated = compute_lexical_complexity("数字化转型数字化转型数字化转型数字化转型")
    varied = compute_lexical_complexity("数字化转型服务实体经济推动高质量发展创新")
    assert repeated['within_doc_redundancy_han'] > varied['within_doc_redundancy_han']


def test_han_redundancy_excludes_non_han():
    # 汉字全互异 + 大量重复数字: 字符口径被数字"888"重复拉高, 汉字口径只看汉字 → 0
    r = compute_lexical_complexity("甲乙丙丁戊己庚辛8888888888")
    assert r['within_doc_redundancy_han'] == 0.0  # 8 个互异汉字 → 无重复 3-gram
    assert r['within_doc_redundancy'] > r['within_doc_redundancy_han']  # 数字重复抬高字符版


def test_han_redundancy_short_han_nan():
    # 仅 2 个汉字 (<3) → 汉字口径双 nan; 但 6 字符 (≥3) → 字符口径非 nan
    r = compute_lexical_complexity("银行ABCD")
    assert math.isnan(r['within_doc_redundancy_han'])
    assert math.isnan(r['redundancy_han_log_length'])
    assert not math.isnan(r['within_doc_redundancy'])


def test_han_log_length_is_ln_han_count():
    # "银行数字化" = 5 个汉字 → redundancy_han_log_length = ln(5)
    r = compute_lexical_complexity("银行数字化")
    assert abs(r['redundancy_han_log_length'] - math.log(5)) < 1e-6


# ── fix(hanzi-char-dual, 2026-06-13): 汉字口径文章长度 n_han_real (供 ln_han_count) ──
def test_n_han_real_counts_only_han():
    # 汉字数只数 CJK 汉字, 剔除数字/标点/拉丁 token
    r = compute_lexical_complexity("中国工商银行2024年GDP增长")
    # 中国工商银行(6) + 年(1) + 增长(2) = 9; 2024/GDP 不计
    assert r[HAN_COUNT_KEY] == 9.0


def test_n_han_real_excludes_non_han_chars():
    # 汉字口径长度只数 CJK 汉字, 严格小于字符口径(含数字/拉丁/标点)
    text = "银行2024年GDP增长5.2%净利润"
    r = compute_lexical_complexity(text)
    n_chars = len(text.replace(' ', ''))  # 字符口径(去空白) = 19
    # 银行(2)+年(1)+增长(2)+净利润(3) = 8 个汉字; 2024/GDP/5.2/% 不计
    assert r[HAN_COUNT_KEY] == 8.0
    assert r[HAN_COUNT_KEY] < n_chars  # 汉字口径严格 < 字符口径 (双口径差异有牙)


def test_n_han_real_nan_on_zero_han():
    # fix(hanzi-char-dual final-audit Gap#4): 零汉字文章 (纯数字/拉丁) → nan 而非 0.0,
    # 避免在 avg_han_count 被当有效 0 长度计入 (与 within_doc_redundancy_han nan-跳过对称)
    r = compute_lexical_complexity("2024 GDP PMI CPI 5.2%")
    assert math.isnan(r[HAN_COUNT_KEY])


def test_n_han_real_nan_on_empty():
    for bad in ("", "   ", "nan", "<NA>"):
        assert math.isnan(compute_lexical_complexity(bad)[HAN_COUNT_KEY])


def test_nominalization_finite_and_nonneg():
    r = compute_lexical_complexity("推进数字化转型提升安全性与合规度的制度")
    assert _finite_or_nan_in_unit(r['nominalization_ratio'])
