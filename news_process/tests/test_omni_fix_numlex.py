"""tests/test_omni_fix_numlex.py — omni 2026-06-11 g-numlex 组缺陷修复回归锁.

覆盖 (组级裁决 + scripts/audit/_omni_fix/g-numlex.json adjudication):
- g-numlex-01/-08 (P1): 单字中文数字成语/功能词不再计入 num_intensity 分子
  (单字仅数量语境计入: 后接量词/单位白名单或前置守卫); 政治专名
  (十九大/十三五) 与 malformed 数词 (万一→10001) 守卫; 披露改实测口径。
- g-numlex-02 (P2): 句子分母正则 digit-guard 仅限半角句点, 全角 。！？ 不再守卫。
- g-numlex-03 (P2): FLS 词表 D_time 删纯时长词 (三年/五年/十年) 与当期词
  (本年度/本季度/本财年), D_future 删进行体动词 (推进/推动/促进/努力)。
- g-numlex-04 (P2): rare_word_ratio 分子排除纯数字/纯拉丁 token。
- g-numlex-05 (P2): within_doc_redundancy 长度依赖披露 + redundancy_log_length
  控制变体列。
- g-numlex-06 (P3): specificity m 词性分子排除模糊量词 (一些/许多/若干/几X)。
- g-numlex-07 (P3): 后缀不定数 (三十多万/二十余家/百分之三十几) 按 R7-M2 不计。
- word-denominator: _count_word_tokens 加 _LMFLS_NONWORD_RE 同口径过滤。
- jieba-isolation: lexical_complexity 走独立未注入 Tokenizer, 注入态免疫。

全部为防静默 revert 的行为锁; 修复仅改纯函数, 不触 LLM/缓存/golden
(panel 数值变更 deferred 到下次 stage 22 重跑 + golden 重生)。

# 白话: "数字密集度/词汇复杂度/前瞻性陈述"这几个文本测度的修复锁:
# "进一步""一起""十九大""万一"里的"一""万"不是数字, 不能算进"文中有多少
# 数字"; "三十多万""二十余家"是约数也不算; 生僻词比例不能被阿拉伯数字和
# 英文字母灌水; "推进""三年"这类词不代表"在谈未来", 从前瞻词表里删掉;
# 分词器用独立干净实例, 不被别处注入的自定义词污染。
"""
from __future__ import annotations

import math

import pytest

pytestmark = pytest.mark.fast


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-01 / -08 (P1): 单字中文数字数量语境门控
# ════════════════════════════════════════════════════════════════════════════
class TestSingleCharNumberGate:
    """组级裁决点名: 进一步/一起/统一/之一/十九大/十三五 必须不再计入."""

    def test_mandated_function_words_not_converted(self):
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        # 组级裁决逐字点名的 6 个 must-not-count
        for text in ('进一步推进改革', '大家一起努力', '统一监管标准',
                     '排名之一', '深入学习十九大精神', '落实十三五规划'):
            out = _cn2arab(text)
            assert out == text, f'{text!r} 应原样保留, 实得 {out!r}'

    def test_mandated_zero_num_intensity(self):
        from news_process.pipeline.sentiment.numerical_intensity import (
            compute_num_intensity,
        )
        # 全句仅功能词/专名数字 → 分子 0
        assert compute_num_intensity(
            '进一步统一标准, 一起落实十三五规划, 这是任务之一。') == 0.0
        assert compute_num_intensity('深入学习十九大精神。') == 0.0

    def test_common_collocations_not_converted(self):
        """高频固定搭配 (审计实测 top 噪声源) 不再计入."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        for text in ('一带一路倡议', '一方面发展', '新一代系统', '一是加强',
                     '一系列举措', '一站式服务', '周三上午开会'):
            assert _cn2arab(text) == text, f'{text!r} 应原样保留'

    def test_wanyi_idiom_not_misconverted(self):
        """'万一' 旧实现误算 10001 (malformed 前导单位字守卫)."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        out = _cn2arab('万一发生违约')
        assert '万一' in out and '10001' not in out

    def test_shisanwu_not_misconverted_to_15(self):
        """'十三五' 旧实现错算 15 (malformed 相邻纯数字守卫)."""
        from news_process.pipeline.sentiment.numerical_intensity import (
            _cn_number_to_arabic,
        )
        assert _cn_number_to_arabic('十三五') is None

    def test_single_char_with_unit_whitelist_still_counted(self):
        """单字数字在数量语境 (后接量词/单位白名单) 仍计入 — 不得过度击杀."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert '5' in _cn2arab('五家银行')
        assert '1' in _cn2arab('一笔贷款')
        assert '3' in _cn2arab('共三人')
        # 注: '十年' 不在此列 — 单独 '十' 无 pure-digit 字符, 修复前后均不转
        # (既有纯单位排除, v3.5.1), 非本修复行为。
        assert '3' in _cn2arab('三年之后')

    def test_single_char_with_preceding_quant_guard_counted(self):
        """前置数量修饰守卫 (约/近/逾/超/达/共/仅) 也开门."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert '3' in _cn2arab('合计达三')

    def test_prev_blacklist_overrides_unit_whitelist(self):
        """黑名单优先: 前字是 之/统/进/这/同/唯 时即使后接白名单字也不计."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert _cn2arab('统一个人账户管理') == '统一个人账户管理'
        assert _cn2arab('这一年发展迅速') == '这一年发展迅速'
        assert _cn2arab('同一家银行') == '同一家银行'
        # '唯一一家': '一一' 成 2 字块, 由相邻纯数字 malformed 守卫覆盖
        assert _cn2arab('唯一一家银行') == '唯一一家银行'

    def test_multichar_blocks_unaffected_anti_regression(self):
        """多字数字块 (cn2arab 5 锁定样例) 不受单字门控影响 — frozen at D0."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert '20000000' in _cn2arab('投资两千万')
        assert '350000000' in _cn2arab('营收三亿五千万')
        assert '30%' in _cn2arab('增长百分之三十')
        assert _cn2arab('两万亿') == str(2 * 10**12)
        assert '300000' in _cn2arab('三十万用户')

    def test_disclosure_updated_to_measured_caliber(self):
        """披露改实测口径: 失真的 '≈ 1%' 旧声称必须消失, 实测数字必须在场."""
        import inspect

        from news_process.pipeline.sentiment import numerical_intensity as m
        src = inspect.getsource(m)
        assert '5-15\n        article / 1170' not in src
        assert '94.5%' in src and '42.3%' in src, '实测口径披露缺失'


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-02 (P2): 句子分母 digit-guard 仅限半角句点
# ════════════════════════════════════════════════════════════════════════════
class TestSentenceRegexFullwidthUnguarded:
    def test_fullwidth_period_adjacent_digit_counted(self):
        """'…显著。2017年…' 旧正则只计 1 句 (digit-guard 误伤全角), 修后 2 句."""
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_numerical_tokens,
        )
        _, n_sent = _count_numerical_tokens('去年增长显著。2017年继续增长。')
        assert n_sent == 2

    def test_digit_before_fullwidth_period_counted(self):
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_numerical_tokens,
        )
        _, n_sent = _count_numerical_tokens('增速达120。2018年继续。')
        assert n_sent == 2

    def test_ascii_decimal_point_still_guarded(self):
        """半角小数点保护不回归: 1.5 / 3.2 的 '.' 不切句."""
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_numerical_tokens,
        )
        _, n_sent = _count_numerical_tokens('投资1.5亿元。营收3.2亿元。')
        assert n_sent == 2


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-07 (P3): 后缀不定数旁路守卫 (R7-M2)
# ════════════════════════════════════════════════════════════════════════════
class TestSuffixIndefiniteGuard:
    def test_suffix_indefinite_not_converted(self):
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        for text in ('三十多万用户', '二十余家银行', '十来个项目'):
            assert _cn2arab(text) == text, f'{text!r} 后缀不定数应整体不计'

    def test_percent_suffix_indefinite_not_converted(self):
        """'百分之三十几' 旧实现转出 '30%几' 计 1 token."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        out = _cn2arab('增长百分之三十几')
        assert '百分之三十几' in out and '%' not in out

    def test_prefix_indefinite_still_excluded_anti_regression(self):
        """前缀不定数 (几千/数十亿/上百万) 原有守卫不回归."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert '几' in _cn2arab('投资几千万元')

    def test_definite_counterpart_still_counted(self):
        """对照: 去掉不定后缀的 '三十万' 必须照常转换 (不得过度击杀)."""
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        assert '300000' in _cn2arab('三十万用户')


# ════════════════════════════════════════════════════════════════════════════
# word-denominator: _count_word_tokens 加 _LMFLS_NONWORD_RE 同口径过滤
# ════════════════════════════════════════════════════════════════════════════
class TestWordTokenDenominatorCaliber:
    def test_punct_excluded(self):
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_word_tokens,
        )
        # 银行 / ， / 发展 / 。 → word-token 仅 2
        assert _count_word_tokens('银行，发展。') == 2

    def test_pure_digit_token_excluded(self):
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_word_tokens,
        )
        assert _count_word_tokens('银行 100') == 1

    def test_same_caliber_as_lm_non_sentiment(self):
        """与 lm_non_sentiment word-token 口径逐 token 一致 (单一事实源复用)."""
        import jieba

        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _LMFLS_NONWORD_RE,
        )
        from news_process.pipeline.sentiment.numerical_intensity import (
            _count_word_tokens,
        )
        text = '本行2023年净利润增长百分之三十，不良率1.5%！'
        expected = sum(
            1 for t in jieba.cut(text)
            if t.strip() and not _LMFLS_NONWORD_RE.fullmatch(t.strip())
        )
        assert _count_word_tokens(text) == expected


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-04 (P2): rare_word_ratio 分子排除纯数字/纯拉丁 token
# ════════════════════════════════════════════════════════════════════════════
class TestRareWordNumeratorExclusion:
    def test_digits_and_latin_not_rare(self):
        """纯数字/拉丁 token (OOV freq=0) 不再洪泛 rare 分子."""
        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        # 全数字文本: 修前 rare=1.0 (全部 OOV), 修后 0.0
        assert compute_lexical_complexity('100 200 300')['rare_word_ratio'] == 0.0
        # 数字+拉丁混合: 同样 0.0
        assert compute_lexical_complexity('2017 ABC 3.5%')['rare_word_ratio'] == 0.0

    def test_true_rare_chinese_words_still_counted(self):
        """真低频中文词仍计入 — 不得过度击杀.

        '璞玉' jieba 冻结词典 freq=3 ≤ cutoff(3.0) → rare; '如同' 高频非 rare
        → ratio = 1/2 (用确定词频锚定, 勿换成 freq>3 的"看着生僻"词如 饕餮=46)。
        """
        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        assert compute_lexical_complexity('如同璞玉')['rare_word_ratio'] == 0.5

    def test_digit_flood_does_not_raise_rare_ratio(self):
        """对同一中文底文, 注入数字 token 不应抬高 rare_word_ratio."""
        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        base = compute_lexical_complexity('银行净利润增长')['rare_word_ratio']
        flooded = compute_lexical_complexity(
            '银行净利润增长 100 200 300 400 500')['rare_word_ratio']
        assert flooded <= base


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-05 (P2): redundancy 长度依赖披露 + log-length 控制变体列
# ════════════════════════════════════════════════════════════════════════════
class TestRedundancyLogLengthVariant:
    def test_key_registered_and_emitted(self):
        from news_process.pipeline.sentiment.lexical_complexity import (
            LEXICAL_COMPLEXITY_KEYS,
            compute_lexical_complexity,
        )
        assert 'redundancy_log_length' in LEXICAL_COMPLEXITY_KEYS
        r = compute_lexical_complexity('银行推动数字化转型服务实体经济')
        assert 'redundancy_log_length' in r

    def test_value_is_ln_of_dewhitespaced_char_count(self):
        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        text = '银行 数字 化转型'  # 去空白 7 字 (银行+数字+化转型)
        r = compute_lexical_complexity(text)
        assert r['redundancy_log_length'] == pytest.approx(math.log(7), abs=1e-6)

    def test_same_domain_as_redundancy(self):
        """与 within_doc_redundancy 同定义域: <3 字 → 双 nan; 空/哨兵 → nan."""
        from news_process.pipeline.sentiment.lexical_complexity import (
            _char_trigram_redundancy,
            compute_lexical_complexity,
        )
        red, loglen = _char_trigram_redundancy('银行')
        assert math.isnan(red) and math.isnan(loglen)
        for bad in ('', '   ', 'nan', '<NA>'):
            assert math.isnan(
                compute_lexical_complexity(bad)['redundancy_log_length'])

    def test_length_dependence_disclosed_in_module(self):
        """长度依赖披露落在模块 docstring (corr / 五分位单调) — 防静默删除."""
        from news_process.pipeline.sentiment import lexical_complexity as m
        doc = m.__doc__
        assert '长度依赖' in doc and 'redundancy_log_length' in doc


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-06 (P3): specificity m 词性排除模糊量词
# ════════════════════════════════════════════════════════════════════════════
class TestSpecificityVagueQuantifierExclusion:
    def test_vague_quantifiers_zero_specificity(self):
        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        # 一些/许多/若干 全标 'm' 但是 vague 侧 → 分子 0
        assert compute_lexical_complexity(
            '一些许多若干机构宣布')['specificity_index'] == 0.0

    def test_indefinite_prefix_ji_shu_excluded(self):
        from news_process.pipeline.sentiment.lexical_complexity import (
            _is_hard_m_token,
        )
        assert _is_hard_m_token('几十家') is False
        assert _is_hard_m_token('数百') is False
        assert _is_hard_m_token('一些') is False

    def test_hard_numbers_still_counted(self):
        from news_process.pipeline.sentiment.lexical_complexity import (
            _is_hard_m_token,
            compute_lexical_complexity,
        )
        assert _is_hard_m_token('100') is True
        assert _is_hard_m_token('亿元') is True
        assert _is_hard_m_token('三十') is True
        assert compute_lexical_complexity('投资100亿元')['specificity_index'] > 0.0


# ════════════════════════════════════════════════════════════════════════════
# jieba-isolation: lexical_complexity 独立未注入 Tokenizer
# ════════════════════════════════════════════════════════════════════════════
class TestLexicalJiebaIsolation:
    def test_immune_to_global_jieba_injection(self):
        """全局 jieba add_word 注入前后, 本测度族输出逐键一致 (确定性)."""
        import jieba

        from news_process.pipeline.sentiment.lexical_complexity import (
            compute_lexical_complexity,
        )
        text = '银行围绕金融科技数字化转型发布一系列举措但是风险仍存'
        before = compute_lexical_complexity(text)
        try:
            jieba.add_word('金融科技数字化', freq=10000, tag='x')
            jieba.add_word('一系列举措', freq=10000, tag='x')
            after = compute_lexical_complexity(text)
        finally:
            jieba.del_word('金融科技数字化')
            jieba.del_word('一系列举措')
        for k in before:
            b, a = before[k], after[k]
            assert (math.isnan(b) and math.isnan(a)) or b == a, \
                f'{k}: 注入前 {b} != 注入后 {a} (注入态泄漏)'

    def test_pristine_tokenizer_is_not_global_dt(self):
        import jieba

        from news_process.pipeline.sentiment.lexical_complexity import (
            _get_pristine_posseg,
            _get_pristine_tokenizer,
        )
        tk = _get_pristine_tokenizer()
        assert tk is not jieba.dt
        assert _get_pristine_posseg().tokenizer is tk


# ════════════════════════════════════════════════════════════════════════════
# g-numlex-03 (P2): FLS 词表收紧 (词表变更测试锁定)
# ════════════════════════════════════════════════════════════════════════════
class TestFlsWordlistTightening:
    def test_progressive_verbs_removed_from_future(self):
        from news_process.pipeline.sentiment.forward_looking import _FUTURE_WORDS
        for w in ('推进', '推动', '促进', '努力'):
            assert w not in _FUTURE_WORDS, f'进行体动词 {w!r} 应已删除'

    def test_bare_duration_and_current_period_removed_from_time(self):
        from news_process.pipeline.sentiment.forward_looking import (
            _TIME_FUTURE_MARKERS,
        )
        for w in ('三年', '五年', '十年', '本年度', '本季度', '本财年'):
            assert w not in _TIME_FUTURE_MARKERS, f'非未来指向时间词 {w!r} 应已删除'

    def test_future_anchored_words_retained(self):
        """未来锚定词保留 — 不得过度击杀 (组级裁决仅删点名词)."""
        from news_process.pipeline.sentiment.forward_looking import (
            _FUTURE_WORDS,
            _TIME_FUTURE_MARKERS,
        )
        for w in ('三年内', '五年内', '十年内', '未来三年', '未来', '明年',
                  '下一财年', '年内', '年底'):
            assert w in _TIME_FUTURE_MARKERS, f'{w!r} 不应被误删'
        for w in ('着力', '致力于', '力争', '推行', '推动力', '计划', '将'):
            assert w in _FUTURE_WORDS, f'{w!r} 不应被误删'

    def test_double_gate_total_still_above_100(self):
        """G-A2.1 准入门控: 删词后双门控词表总量仍 ≥ 100."""
        from news_process.pipeline.sentiment.forward_looking import (
            _FUTURE_WORDS,
            _TIME_FUTURE_MARKERS,
        )
        assert len(_FUTURE_WORDS) + len(_TIME_FUTURE_MARKERS) >= 100

    def test_retrospective_sentences_no_longer_fls(self):
        """审计实测误判句 (回溯性成就报道) 修后不再判 FLS."""
        from news_process.pipeline.sentiment.forward_looking import (
            _is_fls_sentence,
        )
        assert _is_fls_sentence('过去三年,该行持续推进零售转型。') is False
        assert _is_fls_sentence('本年度上半年,该行推进了多项改革。') is False

    def test_true_fls_still_detected_anti_regression(self):
        from news_process.pipeline.sentiment.forward_looking import (
            _is_fls_sentence,
        )
        assert _is_fls_sentence('银行计划未来三年达 500 亿规模。') is True
        assert _is_fls_sentence('将于明年推出新产品。') is True
        assert _is_fls_sentence('公司将在下一财年完成产能扩张') is True
