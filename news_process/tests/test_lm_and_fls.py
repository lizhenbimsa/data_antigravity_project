"""Tests for v3.5.2 PR #3: A1 LM 6 子词典 + A2 Forward-Looking Statements.

覆盖:
- pipeline.sentiment.lm_non_sentiment._compute_lm_non_sentiment_for_text
- pipeline.sentiment.lm_non_sentiment.load_lm_non_sentiment_dicts
- pipeline.sentiment.forward_looking.compute_fls_for_text
- stage 22 集成验证 (LM + FLS 已挂入 _dual_analyze, 通过 import 验证)
"""
from __future__ import annotations

import math

import pytest

pytestmark = pytest.mark.fast


# ── LM 6 子词典 (PR #3 A1) ──────────────────────────────────────────
class TestLmNonSentimentLoad:
    def test_load_returns_6_subsets(self):
        # v3.10.0: 6 子集 (原 4 + weak_modal/complexity)。
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _SUBSETS,
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        assert set(d.keys()) == set(_SUBSETS)
        assert set(d.keys()) == {
            'uncertainty', 'litigious', 'constraining', 'modal_strong',
            'weak_modal', 'complexity',
        }

    def test_each_subset_is_frozenset(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        for k, v in d.items():
            assert isinstance(v, frozenset)
            assert len(v) > 0, f"{k} 词典为空"

    def test_subset_sizes_within_range(self):
        # 2026-06-18 替代: 4 个非情感子集源自 loughran_mcdonald_zh_2026 对应非极性类别
        # (uncertainty 392 / litigious 913 / constraining 174 / strong_modal→modal_strong 54);
        # 原 314 词 stub (lm_non_sentiment) 已删除。上限放宽到 2000 容纳 L&M 全本翻译。
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        for k, v in d.items():
            assert 20 <= len(v) <= 2000, \
                f"{k} 词数 {len(v)} 超出预期范围 (loughran 非情感类别)"

    def test_lru_cache_idempotent(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d1 = load_lm_non_sentiment_dicts()
        d2 = load_lm_non_sentiment_dicts()
        assert d1 is d2, "lru_cache 应返回同一对象"

    def test_load_returns_empty_subsets_when_dict_file_missing(self, monkeypatch, tmp_path):
        """词典文件不存在 → 返回 {subset: frozenset()} 4 个空集 (lm_non_sentiment.py:71)."""
        from news_process.pipeline.sentiment import lm_non_sentiment as M
        # 清缓存避免 lru_cache hit
        M.load_lm_non_sentiment_dicts.cache_clear()
        monkeypatch.setattr(M, '_LM_DICT_PATH', tmp_path / 'nonexistent.json')
        try:
            d = M.load_lm_non_sentiment_dicts()
            assert set(d.keys()) == set(M._SUBSETS)  # v3.10.0: 6 子集
            assert all(len(v) == 0 for v in d.values())
            assert all(isinstance(v, frozenset) for v in d.values())
        finally:
            # 恢复后再次清缓存, 让后续测试重新加载真词典
            M.load_lm_non_sentiment_dicts.cache_clear()


class TestLmNonSentimentScan:
    def test_empty_text_returns_nan_fracs(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("")
        assert r['n_tokens'] == 0
        for subset in ('uncert', 'litig', 'constr', 'modal_strong', 'modal_weak', 'complexity'):
            assert math.isnan(r[f'frac_{subset}'])

    def test_whitespace_only_after_jieba_returns_empty(self):
        """jieba 切空白产生的全 whitespace token 应被 filter → n_tokens=0 → empty
        (lm_non_sentiment.py:119, post-jieba n_tokens==0 branch)."""
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        # 纯空白多字符: bool(text)=True, text.strip()=='' → 走早 return (line 113-114)
        # 而要触发 line 119 需要 text 非空白但 jieba 切完后 token 全空: 例如全标点
        # 实测 jieba 对 '   ' 会保留空 token; 用单字符空格保证 line 119 触发
        r = _compute_lm_non_sentiment_for_text(" ")  # bool True, strip 空 → line 113
        assert r['n_tokens'] == 0
        import math
        assert math.isnan(r['frac_uncert'])
        # 真正触发 line 119 (jieba 切了但 n_tokens=0): 用全空白 + 制表符组合
        r2 = _compute_lm_non_sentiment_for_text("\t ")  # NBSP + tab
        assert r2['n_tokens'] == 0
        assert math.isnan(r2['frac_litig'])

    def test_uncertainty_detected(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("银行业务存在风险, 可能出现波动")
        assert r['n_uncert'] >= 1
        assert r['frac_uncert'] > 0

    def test_litigious_detected(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("被监管处罚, 立案调查违规事项")
        assert r['n_litig'] >= 2
        assert r['frac_litig'] > 0

    def test_constraining_detected(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("受到严格限制, 不得超出上限")
        assert r['n_constr'] >= 2
        assert r['frac_constr'] > 0

    def test_modal_strong_detected(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("一定坚决推进, 必定成功")
        assert r['n_modal_strong'] >= 2

    def test_neutral_text_low_fracs(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("银行年报数据公布, 资产规模 100 亿元")
        # 中性陈述, 各类 frac 应低 (< 0.1)
        for subset in ('uncert', 'litig', 'constr', 'modal_strong', 'modal_weak', 'complexity'):
            v = r[f'frac_{subset}']
            assert math.isnan(v) or v < 0.2, f"{subset} 在中性句中 frac={v} 过高"

    def test_frac_is_normalized(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("银行业务推广战略转型")
        for subset in ('uncert', 'litig', 'constr', 'modal_strong', 'modal_weak', 'complexity'):
            v = r[f'frac_{subset}']
            assert math.isnan(v) or (0.0 <= v <= 1.0), f"{subset} frac={v} 越界"

    def test_genericization_backward_compat_keys(self):
        """v3.10.0 字节等价守卫: 泛型化 (4→6 子集) 后, 现有 4 子集的返回键名/顺序不变,
        且新 2 子集追加在末尾。两个实现 (只读模块 + tone_words tone_tok 包装) 须同构。"""
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
            load_lm_non_sentiment_dicts,
        )
        from news_process.pipeline.sentiment.tone_words import (
            _compute_lm_non_sentiment_for_text_tone_tok,
        )
        txt = "银行可能存在重大不确定性诉讼风险，必须依法合规，未来或将复杂化。"
        expected = [
            'n_tokens',
            'n_uncert', 'frac_uncert',
            'n_litig', 'frac_litig',
            'n_constr', 'frac_constr',
            'n_modal_strong', 'frac_modal_strong',
            'n_modal_weak', 'frac_modal_weak',
            'n_complexity', 'frac_complexity',
        ]
        r1 = _compute_lm_non_sentiment_for_text(txt)
        r2 = _compute_lm_non_sentiment_for_text_tone_tok(txt, load_lm_non_sentiment_dicts())
        assert list(r1.keys()) == expected, "只读模块返回键名/顺序漂移"
        assert list(r2.keys()) == expected, "tone_tok 包装返回键名/顺序漂移"


class TestLmPanelColumnsHelper:
    def test_get_panel_columns_full(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            get_panel_columns,
        )
        cols = get_panel_columns('_full')
        assert cols == [
            'uncert_frac_full', 'litig_frac_full',
            'constr_frac_full', 'modal_strong_frac_full',
            'modal_weak_frac_full', 'complexity_frac_full',
        ]

    def test_get_panel_columns_ctx(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            get_panel_columns,
        )
        cols = get_panel_columns('_ctx')
        assert all(c.endswith('_ctx') for c in cols)
        assert len(cols) == 6  # v3.10.0: 6 子集


# ── A2 FLS (PR #3) ──────────────────────────────────────────────────
class TestForwardLooking:
    def test_empty_text(self):
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        r = compute_fls_for_text("")
        assert r['n_sentences'] == 0
        assert math.isnan(r['frac_fls'])

    def test_no_fls_sentence(self):
        # 含 future 词 "将" 但无 time 词
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        r = compute_fls_for_text("银行将其业务划转给子公司处理。")
        assert r['n_fls_sentences'] == 0
        assert r['frac_fls'] == 0.0

    def test_double_gate_pass(self):
        # 同时含 future ("计划") + time ("未来三年")
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        r = compute_fls_for_text("银行计划未来三年达 500 亿规模。")
        assert r['n_fls_sentences'] == 1
        assert r['frac_fls'] == 1.0

    def test_mixed_sentences(self):
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        r = compute_fls_for_text(
            "银行业务规模达 100 亿。计划未来三年达 500 亿。"
        )
        assert r['n_sentences'] == 2
        assert r['n_fls_sentences'] == 1
        assert abs(r['frac_fls'] - 0.5) < 0.01

    def test_multiple_fls_sentences(self):
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        text = (
            "预计未来五年实现数字化转型。"
            "计划到 2030 年达全球前 50。"
            "将于明年推出新业务。"
        )
        r = compute_fls_for_text(text)
        assert r['n_sentences'] == 3
        assert r['n_fls_sentences'] >= 2  # 至少前 2 句明确 FLS

    def test_frac_in_range(self):
        from news_process.pipeline.sentiment.forward_looking import (
            compute_fls_for_text,
        )
        r = compute_fls_for_text("一段长文本。多个句子。各种情况。")
        v = r['frac_fls']
        assert math.isnan(v) or (0.0 <= v <= 1.0)

    def test_get_panel_columns(self):
        from news_process.pipeline.sentiment.forward_looking import (
            get_panel_columns,
        )
        cols = get_panel_columns('_full')
        assert cols == ['frac_fls_full']


# ── stage 22 集成验证 (P0.2 修复后, 真接入) ──────────────────────────
class TestStage22Integration:
    def test_tone_words_imports_lm_and_fls(self):
        """stage 22 顶部 import 含 LM + FLS (PR #14 集成验证)."""
        import inspect

        from news_process.pipeline.sentiment import tone_words
        src = inspect.getsource(tone_words)
        assert "_compute_lm_non_sentiment_for_text" in src, \
            "tone_words.py 未集成 LM 6 子词典 (PR #3)"
        assert "compute_fls_for_text" in src, \
            "tone_words.py 未集成 FLS (PR #3 A2)"

    def test_dual_analyze_emits_lm_fls_keys(self):
        """_dual_analyze 输出含 LM + FLS panel keys 的拼接来源 (P0.2 verify).

        注: stage 22 用循环 + f-string 拼接列名 (``f'{col}_full'``),
        所以源码不含 literal 'uncert_frac_full', 仅含构造前缀 'uncert' 等.
        """
        import inspect

        from news_process.pipeline.sentiment import tone_words
        src = inspect.getsource(tone_words)
        # v3.10.0: stage 22 改用泛型 SUBSET_PREFIXES 循环 + f-string 拼接列名
        # (取代硬编码 4-prefix 元组), 故源码不含 literal 'uncert' 等裸前缀。
        assert "SUBSET_PREFIXES" in src, \
            "_dual_analyze 未用泛型 SUBSET_PREFIXES 迭代 LM 子集"
        assert "_compute_lm_non_sentiment_for_text_tone_tok" in src, \
            "_dual_analyze 未调用 LM 非情感扫描"
        assert "_frac_full" in src, "_dual_analyze 未拼接 LM frac 列 (f'{k}_frac_full')"
        assert "frac_fls" in src or "compute_fls_for_text" in src, \
            "_dual_analyze 未集成 FLS (PR #3 A2)"


# ---------------------------------------------------------------------------
# quality-hardening Round 30 (2026-05-27): forward_looking 91.67% → ~100%
# missing lines 110 (_is_fls_sentence empty short-circuit) + 148 (n_sents==0)
# ---------------------------------------------------------------------------


def test_is_fls_sentence_empty_returns_false():
    """_is_fls_sentence 接受空字符串 → False (line 109-110)."""
    from news_process.pipeline.sentiment.forward_looking import _is_fls_sentence
    assert _is_fls_sentence('') is False
    assert _is_fls_sentence(None) is False
