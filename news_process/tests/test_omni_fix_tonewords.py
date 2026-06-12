"""tests/test_omni_fix_tonewords.py — OMNI 2026-06-11 g-tonewords 组修复回归锁.

覆盖 (fix omni-g-tonewords-*, 2026-06-11; 裁决见 scripts/audit/_omni_fix/g-tonewords.json):
- 01/05: pos_ratio/neg_ratio/msent_score 计数基 = 5 词典固定 union 词典
         (build_union_dictionary, 多数票消歧+平票剔除), 替代逐篇漂移 best-dict
- 02/06/12: clarity / {dict}_pos|neg_ratio / 全局 pos|neg_ratio 分母 word-token 化
         (复用 lm_non_sentiment._LMFLS_NONWORD_RE, 与 lmfls-01 LM/FLS 修复同口径)
- 03/07: 词典加载 positive∩negative 跨类重叠显式双侧剔除 (jiang 21 / you_2018 5,
         含 '打破'/'反弹'); clarity definite∩ambiguous ('不可') 同款
- 04: build_idf_weights DF/N 按唯一文档去重 ((article×bank) 展开行不再膨胀 DF)
- 09: 程度副词×3.0/转折×1.5 加权 tone 归一化分母 = Σ|final_score| → 恒有界 [-1,1]
- 10/11: jieba 注入隔离 — 领域词只进独立 tone tokenizer, 全局 jieba 纯净
         (lexical_complexity posseg / forward_looking FLS 双门控不再被注入污染);
         FLS 标记注入移除; LM 扫描走 tone-tokenizer 包装防 completeness-02 回归
- 13: z-score σ 退化分支整列 NaN + 降级披露 (替代 0.0 伪零分)
- empty-text contract: score/ratio/msent 空文本 → NaN (对称化)

注: g-tonewords-08 (numerical_intensity._count_word_tokens) 属并行组 g-numlex
管辖文件, 不在本文件覆盖范围。
"""
from __future__ import annotations

import inspect
import json
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

import jieba  # noqa: E402

from news_process.pipeline.sentiment import lm_non_sentiment as lm  # noqa: E402
from news_process.pipeline.sentiment import tone_words as tone  # noqa: E402


@pytest.fixture(autouse=True)
def _preserve_tone_globals():
    """保存/还原 tone_words 模块级可变全局 (防跨测试污染)."""
    saved = (
        tone.ALL_DICTIONARIES,
        tone.IDF_DICTIONARIES,
        tone._UNION_DICT_CACHE,
        tone._CLARITY_DICTS,
    )
    yield
    (tone.ALL_DICTIONARIES, tone.IDF_DICTIONARIES,
     tone._UNION_DICT_CACHE, tone._CLARITY_DICTS) = saved


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-03/-07: positive∩negative 跨类重叠双侧剔除
# ════════════════════════════════════════════════════════════════════════

class TestCrossPolarityOverlapResolution:
    def test_overlap_words_dropped_from_both_sides(self):
        """jiang_2021 (21 词, 含 '打破') / you_2018 (5 词, 含 '反弹') 重叠词
        加载后双侧消失 — 旧实现 last-writer-wins 静默判负 (-1.0)。"""
        with open(tone.TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        loaded = dict(tone.load_all_dictionaries())
        for key in ('jiang_2021', 'you_2018'):
            pos = {str(w).strip() for w in raw[key]['positive'] if str(w).strip()}
            neg = {str(w).strip() for w in raw[key]['negative'] if str(w).strip()}
            overlap = pos & neg
            assert overlap, f"前提失效: {key} 源词典应存在 pos∩neg 重叠"
            for w in overlap:
                assert w not in loaded[key], (
                    f"{key} 重叠词 {w!r} 应被双侧剔除 (旧行为: 静默判负)")
        # 高频代表词显式锁定
        assert '打破' not in loaded['jiang_2021']
        assert '反弹' not in loaded['you_2018']

    def test_loaded_counts_match_post_resolution_sets(self):
        """剔除后正/负词条数 = 源 set 差集大小 (数量断言, 防回归静默覆盖)。"""
        with open(tone.TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        loaded = dict(tone.load_all_dictionaries())
        entry = raw['jiang_2021']
        pos = {str(w).strip() for w in entry['positive'] if str(w).strip()}
        neg = {str(w).strip() for w in entry['negative'] if str(w).strip()}
        overlap = pos & neg
        d = loaded['jiang_2021']
        assert sum(1 for v in d.values() if v > 0) == len(pos - overlap)
        assert sum(1 for v in d.values() if v < 0) == len(neg - overlap)

    def test_clarity_cross_overlap_dropped(self):
        """clarity definite∩ambiguous ('不可' 1 词) 双侧剔除 → 387/177。"""
        tone._CLARITY_DICTS = None
        def_set, amb_set = tone.load_clarity_dictionaries()
        assert not (def_set & amb_set)
        assert '不可' not in def_set and '不可' not in amb_set
        assert len(def_set) == 387
        assert len(amb_set) == 177


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-01/-05: 固定 union 词典 (替代逐篇漂移 best-dict)
# ════════════════════════════════════════════════════════════════════════

class TestUnionDictionary:
    def test_majority_vote_and_tie_drop(self):
        dicts = [
            ('d1', {'反弹': 1.0, '风险': -1.0}),
            ('d2', {'反弹': 1.0, '稳健': 1.0}),
            ('d3', {'反弹': -1.0}),
        ]
        union = tone.build_union_dictionary(dicts)
        assert union['反弹'] == 1.0   # 2 正 vs 1 负 → 多数票判正
        assert union['风险'] == -1.0
        assert union['稳健'] == 1.0
        # 平票 → 极性歧义剔除 (LM 2011 惯例)
        tie = tone.build_union_dictionary(
            [('d1', {'整顿': 1.0}), ('d2', {'整顿': -1.0})])
        assert '整顿' not in tie

    def test_order_invariant_deterministic(self):
        a = [('d1', {'好': 1.0, '坏': -1.0}), ('d2', {'好': 1.0, '糟': -1.0})]
        assert tone.build_union_dictionary(a) == \
            tone.build_union_dictionary(list(reversed(a)))

    def test_political_positive_magnitude_rule(self):
        """0.5 政治词幅值仅当无 ±1.0 同向词时保留。"""
        assert tone.build_union_dictionary(
            [('d1', {'引领': 0.5}), ('d2', {'引领': 1.0})])['引领'] == 1.0
        assert tone.build_union_dictionary([('d1', {'引领': 0.5})])['引领'] == 0.5

    def test_union_cache_invalidates_on_dict_change(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'好': 1.0})])
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        assert tone._get_union_dictionary() == {'好': 1.0}
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'坏': -1.0})])
        assert tone._get_union_dictionary() == {'坏': -1.0}

    def test_aggregate_ratios_use_union_not_best_dict(self, monkeypatch):
        """旧 best-dict 会选匹配数最多的词典 a (3 词) → neg_ratio=0;
        union 词典含 b 的独有负词 '下跌' → neg_ratio > 0。"""
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [
            ('a', {'上涨': 1.0, '增长': 1.0, '提升': 1.0}),
            ('b', {'下跌': -1.0}),
        ])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', None)
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        res = tone._analyze_single_article('上涨 增长 提升 下跌')
        # 分母 = 4 个 word token; union 分子 pos=3 / neg=1
        assert res['pos_ratio'] == pytest.approx(3 / 4)
        assert res['neg_ratio'] == pytest.approx(1 / 4)
        # msent = (raw_neg - raw_pos) / total = (1-3)/4
        assert res['msent_score'] == pytest.approx(-0.5)
        # sentiment_details 为 union 口径 (含两词典的词)
        details = json.loads(res['sentiment_details'])
        words = {m['word'] for m in details}
        assert '下跌' in words and '上涨' in words


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-02/-06/-12: 比率/clarity 分母 word-token 化
# ════════════════════════════════════════════════════════════════════════

class TestWordTokenDenominator:
    def test_dict_and_global_ratio_excludes_punct_digits(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'上涨': 1.0})])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', None)
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        # word tokens: 上涨/股票 = 2; '，' '。' '2023' 被排除 (旧分母=5)
        res = tone._analyze_single_article('上涨 ， 2023 。 股票')
        assert res['a_pos_ratio'] == pytest.approx(0.5)
        assert res['pos_ratio'] == pytest.approx(0.5)
        assert res['a_neg_ratio'] == pytest.approx(0.0)

    def test_clarity_denominator_excludes_punct_digits(self):
        def_set = frozenset(['百分百'])
        amb_set = frozenset()
        r = tone._compute_clarity_for_text('百分百 2023 ， 100 。', def_set, amb_set)
        assert r['n_tokens_clarity_base'] == 1   # 仅 '百分百' (旧分母=5)
        assert r['frac_definite'] == pytest.approx(1.0)

    def test_clarity_pure_punct_digit_text_nan(self):
        r = tone._compute_clarity_for_text('2023 。 100', frozenset(['百分百']), frozenset())
        assert r['n_tokens_clarity_base'] == 0
        assert math.isnan(r['clarity_score'])

    def test_same_filter_as_lmfls01(self):
        """与 lm_non_sentiment lmfls-01 同口径: 复用同一 _LMFLS_NONWORD_RE。"""
        assert tone._LMFLS_NONWORD_RE is lm._LMFLS_NONWORD_RE


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-09: 加权幅度和分母 → tone 恒有界 [-1, 1]
# ════════════════════════════════════════════════════════════════════════

class TestBoundedNormalizedScore:
    @pytest.fixture(autouse=True)
    def _rules(self, monkeypatch):
        monkeypatch.setattr(tone, 'NEGATION_WORDS', frozenset(['不']))
        monkeypatch.setattr(tone, 'DEGREE_WORDS', {'极其': 3.0})
        monkeypatch.setattr(tone, 'ADVERSATIVE_WORDS', frozenset(['但是']))
        monkeypatch.setattr(tone, 'SENTENCE_END_MARKERS', frozenset(['。']))
        monkeypatch.setattr(tone, 'ADVERSATIVE_BOOST', 1.5)
        monkeypatch.setattr(tone, 'NEGATION_WINDOW', 2)

    def test_degree_weighted_single_word_bounded(self):
        sd = {'好': 1.0, '差': -1.0}
        total, norm, p, n, _ = tone._compute_sentiment_with_rules(['极其', '好', '。'], sd)
        assert total == pytest.approx(3.0)
        # 旧实现 norm = 3.0/1 = 3.0 (值域逃逸); 现 = 3.0/3.0 = 1.0
        assert norm == pytest.approx(1.0)

    def test_mixed_weighted_ratio(self):
        sd = {'好': 1.0, '差': -1.0}
        # '差'(-1) + 但是 极其 好 (+1×3.0×1.5=+4.5) → 分子 3.5 / 分母 5.5
        _, norm, *_ = tone._compute_sentiment_with_rules(
            ['差', '但是', '极其', '好'], sd)
        assert norm == pytest.approx(3.5 / 5.5)
        assert -1.0 <= norm <= 1.0

    def test_no_match_returns_zero(self):
        _, norm, *_ = tone._compute_sentiment_with_rules(['股票', '。'], {'好': 1.0})
        assert norm == 0.0


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-04: IDF 唯一文档去重
# ════════════════════════════════════════════════════════════════════════

class TestIdfUniqueDocumentDedup:
    def test_duplicate_rows_do_not_inflate_df(self):
        """(article×bank) 展开重复行不改变 IDF — 与去重后语料逐值相等。
        (本例若不去重: N=3, df(上涨)=2 → 与 N=2, df=1 的归一化结果可区分。)"""
        dicts = [('t', {'上涨': 1.0, '下跌': -1.0})]
        df_dup = pd.DataFrame({'内容': ['股票 上涨 上涨', '股票 上涨 上涨', '市场 下跌']})
        df_uni = pd.DataFrame({'内容': ['股票 上涨 上涨', '市场 下跌']})
        w_dup = tone.build_idf_weights(df_dup, dicts, text_col='内容')
        w_uni = tone.build_idf_weights(df_uni, dicts, text_col='内容')
        assert w_dup == w_uni

    def test_empty_corpus_fallback_unchanged(self):
        df = pd.DataFrame({'内容': []})
        w = tone.build_idf_weights(df, [('t', {'上涨': 1.0})], text_col='内容')
        assert w['t']['上涨'] == 1.0


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-10/-11: jieba 注入隔离 (独立 tone tokenizer)
# ════════════════════════════════════════════════════════════════════════

class TestJiebaInjectionIsolation:
    def test_injection_leaves_global_jieba_pure(self):
        """注入前后全局 jieba 切分不变; 注入词只进 tone tokenizer。"""
        tone.ALL_DICTIONARIES = tone.load_all_dictionaries()
        sample = '银行布局金融科技与数字化转型, 提出了中长期目标'
        before = list(jieba.cut(sample))
        tone._inject_custom_dicts_to_jieba()
        after = list(jieba.cut(sample))
        assert before == after, '全局 jieba 不得被 stage-22 领域词注入污染'

        # 找一个全局 OOV 的多字情感词, 验证其只在 tone tokenizer 中整词化
        tk = tone._get_tone_tokenizer()
        oov = next(
            w for _, d in tone.ALL_DICTIONARIES for w in d
            if len(w) >= 3 and not jieba.dt.FREQ.get(w)
        )
        assert tk.FREQ.get(oov, 0) > 0, f'tone tokenizer 应含注入词 {oov!r}'
        assert not jieba.dt.FREQ.get(oov), f'全局 jieba 不应含注入词 {oov!r}'

    def test_fls_markers_not_injected_source_lock(self):
        """fix-11: FLS 前瞻词注入已移除 (会吞掉 forward_looking 2 字门控 token);
        全文件不再 import _FUTURE_WORDS / _TIME_FUTURE_MARKERS。"""
        src = inspect.getsource(tone)
        assert '_FUTURE_WORDS' not in src
        assert '_TIME_FUTURE_MARKERS' not in src

    def test_no_global_jieba_cut_in_scan_paths_source_lock(self):
        """词典匹配/clarity/IDF/LM 扫描路径全部走 tone tokenizer, 不再调全局
        jieba.cut (源码级锁, 防回归)。"""
        src = inspect.getsource(tone)
        assert 'jieba.cut(' not in src
        assert 'jieba.add_word(' not in src

    def test_fls_double_gate_survives_injection(self):
        """fix-11 端到端: 注入后 '公司提出了中长期目标' 仍判 FLS
        (旧行为: 注入复合词 '中长期目标' 吞掉 future 门控 '目标' → False)。"""
        from news_process.pipeline.sentiment.forward_looking import _is_fls_sentence
        sent = '公司提出了中长期目标'
        if jieba.dt.FREQ.get('中长期目标'):
            pytest.skip('全局 jieba 已被本会话其他测试注入该复合词, 前提失效')
        tone.ALL_DICTIONARIES = tone.load_all_dictionaries()
        tone._inject_custom_dicts_to_jieba()
        assert _is_fls_sentence(sent) is True


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-10/-11 配套: LM 扫描 tone-tokenizer 包装
# (防 completeness-02 多字 LM 词注入修复被注入隔离静默回归)
# ════════════════════════════════════════════════════════════════════════

class TestLmScanToneTokenizerWrapper:
    def test_wrapper_matches_injected_compound_global_does_not(self):
        tk = tone._get_tone_tokenizer()
        compound = '量子不确定性测试词'
        tk.add_word(compound)
        dicts = {
            'uncertainty': frozenset([compound]),
            'litigious': frozenset(),
            'constraining': frozenset(),
            'modal_strong': frozenset(),
        }
        text = f'公司面临{compound}冲击'
        r_tone = tone._compute_lm_non_sentiment_for_text_tone_tok(text, dicts)
        assert r_tone['n_uncert'] == 1, 'tone tokenizer 整词化的 LM 复合词应命中'
        # 对照: 只读原函数走全局纯净 jieba → 复合词被切碎, 不命中
        r_global = lm._compute_lm_non_sentiment_for_text(text, dicts)
        assert r_global['n_uncert'] == 0, (
            '全局 jieba (纯净) 应切碎该 OOV 复合词 — 证明包装的必要性')

    def test_wrapper_contract_mirrors_readonly_function(self):
        """空文本 → 同款 NaN 契约; 键结构逐项同构。"""
        dicts = lm.load_lm_non_sentiment_dicts()
        r_tone = tone._compute_lm_non_sentiment_for_text_tone_tok('', dicts)
        r_ro = lm._compute_lm_non_sentiment_for_text('', dicts)
        assert set(r_tone.keys()) == set(r_ro.keys())
        assert math.isnan(r_tone['frac_uncert']) and math.isnan(r_ro['frac_uncert'])

    def test_wrapper_word_token_denominator(self):
        """分母 lmfls-01 同口径: 标点/纯数字不计入。"""
        dicts = {
            'uncertainty': frozenset(['或许']),
            'litigious': frozenset(),
            'constraining': frozenset(),
            'modal_strong': frozenset(),
        }
        r = tone._compute_lm_non_sentiment_for_text_tone_tok('或许 2023 ， 上涨', dicts)
        # word tokens: 或许/上涨 = 2
        assert r['n_tokens'] == 2
        assert r['frac_uncert'] == pytest.approx(0.5)


# ════════════════════════════════════════════════════════════════════════
# fix omni-g-tonewords-13: z-score σ 退化分支整列 NaN
# ════════════════════════════════════════════════════════════════════════

class TestZscoreDegenerateNan:
    def test_all_nan_column_stays_nan(self):
        out = tone._zscore_or_nan(pd.Series([np.nan, np.nan, np.nan]), 'x')
        assert out.isna().all(), '全 NaN 列不得被回填 0.0 伪零分'

    def test_constant_column_nan(self):
        out = tone._zscore_or_nan(pd.Series([0.5, 0.5, 0.5]), 'x')
        assert out.isna().all(), 'σ=0 常数列 z-score 数学未定义 → NaN'

    def test_normal_column_propagates_nan_and_standardizes(self):
        s = pd.Series([1.0, 2.0, np.nan, 3.0])
        out = tone._zscore_or_nan(s, 'x')
        assert math.isnan(out.iloc[2])
        assert out.mean() == pytest.approx(0.0, abs=1e-12)
        assert out.std() == pytest.approx(1.0)


# ════════════════════════════════════════════════════════════════════════
# empty-text contract 对称化: score/ratio/msent 空文本 → NaN
# ════════════════════════════════════════════════════════════════════════

class TestEmptyTextContract:
    def test_empty_and_none_yield_nan(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'上涨': 1.0})])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', [('a', {'上涨': 1.2})])
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        for content in ('', '   ', None):
            res = tone._analyze_single_article(content)
            assert math.isnan(res['a_score'])
            assert math.isnan(res['a_pos_ratio'])
            assert math.isnan(res['pos_ratio'])
            assert math.isnan(res['neg_ratio'])
            assert math.isnan(res['msent_score'])
            assert math.isnan(res['a_idf_score'])
            # 类别/长度列保持真值语义
            assert res['a_label'] == '中性'
            assert res['avg_sentence_len'] == 0.0

    def test_pure_punct_text_ratio_nan(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'上涨': 1.0})])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', None)
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        res = tone._analyze_single_article('。。！！2023')
        assert math.isnan(res['pos_ratio'])
        assert math.isnan(res['msent_score'])
