"""test_audit_fixes_20260529 — 回归测试守卫 audit-fixes 2026-05-29 的生产改动.

10 轮 post-fix 审核 (r1/r3/r6/r7/r10) 发现这些生产修复缺回归测试 (且
test_34_tone_validation.py 是"复刻"文件, 本地副本仍内嵌旧逻辑、断言旧行为)。
本文件 import 真实生产函数, 断言修复后的新行为, 防止静默回退到 pre-fix 语义。

覆盖:
  M-tv  tone_validation.label_to_numeric (失败/未定义 → NaN 非 0)
        + compute_label_agreement_rate (严格多数 > n/2)
  M4    executive_ner.call_llm_for_ner (return_status: 调用失败 vs 确无高管)
  H3    stata_export.asciify_non_ascii_columns + validate_stata_compat 标识符门
  L1    encode.balance_panel (零新闻 bank-year 计数列填 0 非 NaN)
"""
import numpy as np
import pandas as pd
import pytest


# ── H1: 标题轨 LLM 全失败 → NaN (非中性 0), 连续 prob-score 路径 ──────────────
class TestH1TitleProbScore:
    MODELS = [{'short_name': 'm1'}, {'short_name': 'm2'}]

    def test_all_failed_returns_nan(self):
        from news_process.pipeline.sentiment.tone_llms import _avg_valid_title_prob_score
        # 所有模型 sentiment=None (整体调用失败) → NaN (旧 bug 返回 0.0)
        data = {'m1_sentiment_title': None, 'm2_sentiment_title': None,
                'm1_prob_score_title': 0.0, 'm2_prob_score_title': 0.0}
        assert np.isnan(_avg_valid_title_prob_score(data, self.MODELS))

    def test_partial_excludes_failed_stale_zero(self):
        from news_process.pipeline.sentiment.tone_llms import _avg_valid_title_prob_score
        # m1 成功(0.8), m2 失败(None, stale 0.0) → 仅算 m1 → 0.8 (stale 0.0 不污染)
        data = {'m1_sentiment_title': '正面', 'm2_sentiment_title': None,
                'm1_prob_score_title': 0.8, 'm2_prob_score_title': 0.0}
        assert _avg_valid_title_prob_score(data, self.MODELS) == pytest.approx(0.8)

    def test_all_valid_mean(self):
        from news_process.pipeline.sentiment.tone_llms import _avg_valid_title_prob_score
        data = {'m1_sentiment_title': '正面', 'm2_sentiment_title': '负面',
                'm1_prob_score_title': 0.6, 'm2_prob_score_title': -0.4}
        assert _avg_valid_title_prob_score(data, self.MODELS) == pytest.approx(0.1)


# ── M-tv: 失败/未定义 → NaN (非中性 0) + 严格多数 ──────────────────────────
class TestMtvFailureNotNeutral:
    def test_label_to_numeric_keeps_nan(self):
        from news_process.validation.tone_validation import label_to_numeric
        out = label_to_numeric(pd.Series(['正面', '未知', None, '负面']))
        assert out.iloc[0] == 1.0
        assert np.isnan(out.iloc[1])   # 未映射标签 → NaN (旧行为 fillna(0)=0.0)
        assert np.isnan(out.iloc[2])   # None → NaN
        assert out.iloc[3] == -1.0

    def test_majority_strict_excludes_even_tie(self):
        from news_process.validation.tone_validation import compute_label_agreement_rate
        # 2 方法 1-1 平局应非多数 (严格 > n/2); 旧 >= 会把平局误算为多数
        df = pd.DataFrame({'m1': ['正面', '正面'], 'm2': ['负面', '正面']})
        out = compute_label_agreement_rate(df)
        # row0 正/负 平局 → 非多数; row1 正/正 → 多数; rate = 1/2
        assert out['majority_agreement_rate'] == pytest.approx(0.5)
        assert out['n_methods'] == 2


# ── M4: 调用失败 vs 确无高管 区分 + 向后兼容 ────────────────────────────────
class TestM4CallFailureStatus:
    def test_empty_input_not_failure(self):
        from news_process.pipeline.sentiment.executive_ner import call_llm_for_ner
        execs, failed = call_llm_for_ner('', 'TestBank', return_status=True)
        assert execs == []
        assert failed is False   # 空输入 ≠ 调用失败

    def test_no_api_key_is_failure(self, monkeypatch):
        from news_process.pipeline.sentiment import executive_ner as en
        monkeypatch.delenv('YUNWU_API_KEY', raising=False)
        execs, failed = en.call_llm_for_ner(
            'audit-fix regression probe content', 'TestBank', return_status=True
        )
        assert execs == []
        assert failed is True    # 无 key → 空响应 → 调用失败

    def test_default_backward_compat_returns_list(self):
        from news_process.pipeline.sentiment.executive_ner import call_llm_for_ner
        out = call_llm_for_ner('', 'TestBank')   # 不传 return_status
        assert out == []         # 仍返回 list (既有调用方/测试不破)


# ── H3: 中文变量名转写 + validate 标识符门 ─────────────────────────────────
class TestH3Asciify:
    def test_cn_label_transliterated(self):
        from news_process.pipeline.panel.stata_export import asciify_non_ascii_columns
        df = pd.DataFrame(
            columns=['target_bank', 'finbert_cn_正面_w_sum_full', 'x_负面_y', 'z_中性']
        )
        out, mapping = asciify_non_ascii_columns(df)
        assert 'finbert_cn_pos_w_sum_full' in out.columns
        assert all(c.isascii() for c in out.columns)      # 0 残留非 ASCII
        assert len(out.columns) == len(set(out.columns))  # 无冲突
        assert mapping['finbert_cn_pos_w_sum_full'] == 'finbert_cn_正面_w_sum_full'

    def test_validate_rejects_non_ascii(self):
        from news_process.pipeline.panel.stata_export import validate_stata_compat
        with pytest.raises(ValueError):
            validate_stata_compat(pd.DataFrame(columns=['正面_col']), {})

    def test_validate_passes_clean_ascii(self):
        from news_process.pipeline.panel.stata_export import validate_stata_compat
        validate_stata_compat(pd.DataFrame(columns=['pos_col', 'neg_col']), {})  # no raise


# ── L1: 零新闻 bank-year 计数列填 0 (非 NaN) ───────────────────────────────
class TestL1ZeroFillCounts:
    def test_zero_news_cell_gets_zero_counts(self):
        from news_process.pipeline.panel.encode import balance_panel
        # 缺 B/2018 → balance 补该 cell; L1 修复后计数列应为 0 (旧 bug 留 NaN)
        panel = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2017, 2018, 2017],
            'n_articles': [3, 2, 1],
            'pos_count_full': [2.0, 1.0, 1.0],
            'neg_count_full': [1.0, 1.0, 0.0],
            'pos_count_vw_full': [2.0, 1.0, 1.0],
            'llm_vote_tone_full': [0.3, 0.0, 1.0],
        })
        bal = balance_panel(panel)
        filled = bal[(bal['target_bank'] == 'B') & (bal['year'] == 2018)]
        assert len(filled) == 1
        assert int(filled['n_articles'].iloc[0]) == 0
        assert float(filled['pos_count_full'].iloc[0]) == 0.0   # L1: 0 非 NaN
        assert float(filled['neg_count_full'].iloc[0]) == 0.0
        assert float(filled['pos_count_vw_full'].iloc[0]) == 0.0
        # 均值类语调列仍应为 NaN (零新闻无情感, 不被零填污染)
        assert pd.isna(filled['llm_vote_tone_full'].iloc[0])
