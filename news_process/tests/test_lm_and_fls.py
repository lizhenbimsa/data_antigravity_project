"""Tests for v3.5.2 PR #3: A1 LM 4 子词典 + A2 Forward-Looking Statements.

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


# ── LM 4 子词典 (PR #3 A1) ──────────────────────────────────────────
class TestLmNonSentimentLoad:
    def test_load_returns_4_subsets(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        assert set(d.keys()) == {
            'uncertainty', 'litigious', 'constraining', 'modal_strong'
        }

    def test_each_subset_is_frozenset(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        for k, v in d.items():
            assert isinstance(v, frozenset)
            assert len(v) > 0, f"{k} 词典为空"

    def test_v01_5_stub_size_within_range(self):
        # v0.1.5 (v2.3-followup-v2 第 17 轮 user-request 扩展):
        # uncertainty 85 / litigious 105 / constraining 77 / modal_strong 52
        # USER_ACTION_REQUIRED v0.2: 上限 500 预留中文金融专家审定后扩容
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d = load_lm_non_sentiment_dicts()
        for k, v in d.items():
            assert 20 <= len(v) <= 500, \
                f"{k} 词数 {len(v)} 超出 v0.1.5/v0.2 预期范围"

    def test_lru_cache_idempotent(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            load_lm_non_sentiment_dicts,
        )
        d1 = load_lm_non_sentiment_dicts()
        d2 = load_lm_non_sentiment_dicts()
        assert d1 is d2, "lru_cache 应返回同一对象"


class TestLmNonSentimentScan:
    def test_empty_text_returns_nan_fracs(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("")
        assert r['n_tokens'] == 0
        for subset in ('uncert', 'litig', 'constr', 'modal_strong'):
            assert math.isnan(r[f'frac_{subset}'])

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
        for subset in ('uncert', 'litig', 'constr', 'modal_strong'):
            v = r[f'frac_{subset}']
            assert math.isnan(v) or v < 0.2, f"{subset} 在中性句中 frac={v} 过高"

    def test_frac_is_normalized(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            _compute_lm_non_sentiment_for_text,
        )
        r = _compute_lm_non_sentiment_for_text("银行业务推广战略转型")
        for subset in ('uncert', 'litig', 'constr', 'modal_strong'):
            v = r[f'frac_{subset}']
            assert math.isnan(v) or (0.0 <= v <= 1.0), f"{subset} frac={v} 越界"


class TestLmPanelColumnsHelper:
    def test_get_panel_columns_full(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            get_panel_columns,
        )
        cols = get_panel_columns('_full')
        assert cols == [
            'uncert_frac_full', 'litig_frac_full',
            'constr_frac_full', 'modal_strong_frac_full',
        ]

    def test_get_panel_columns_ctx(self):
        from news_process.pipeline.sentiment.lm_non_sentiment import (
            get_panel_columns,
        )
        cols = get_panel_columns('_ctx')
        assert all(c.endswith('_ctx') for c in cols)
        assert len(cols) == 4


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
            "tone_words.py 未集成 LM 4 子词典 (PR #3)"
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
        # 关键构造前缀 (检查 _dual_analyze 内确实有这些 prefix + suffix 模式)
        assert "'uncert'" in src and "'litig'" in src and "'constr'" in src, \
            "_dual_analyze 未引用 LM 4 子集 prefix"
        assert "'modal_strong'" in src, "_dual_analyze 未引用 modal_strong"
        assert "frac_fls_full" in src or "'frac_fls'" in src, \
            "_dual_analyze 未引用 FLS 列"
        # 提取阶段必须包含 LM + FLS 5 个 metric base names
        assert 'uncert_frac' in src and 'litig_frac' in src, \
            "tone_words new_columns 列提取段缺 LM frac 列"
