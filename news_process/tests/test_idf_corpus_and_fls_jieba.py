"""tests/test_idf_corpus_and_fls_jieba.py — tone_words IDF 语料 + forward_looking FLS jieba 修复

- IDF document-frequency 须在与 TF 同一语料 (content_full) 上算 (Gentzkow-Kelly-Taddy 2019)。
- forward_looking 双门控: 多字标记 jieba 切碎时补 ≥3 字 substring 命中 (纯加性, 不破坏
  component token 匹配)。fix metric-audit 2026-06-10 (golden 落盘 defer 到 stage 22 重跑)。
"""
from __future__ import annotations

import pandas as pd


# ── forward_looking ───────────────────────────────────────────────────────────
def test_fls_substring_catches_split_time_compound():
    """'下一财年' jieba 切碎(下/一/财年, 成分不在 time 词集) → 仅靠 ≥3 substring 补命中。"""
    from news_process.pipeline.sentiment.forward_looking import _is_fls_sentence
    # future '将'(token) + time '下一财年'(≥3 substring) → FLS
    assert _is_fls_sentence('公司将在下一财年完成产能扩张') is True


def test_fls_requires_both_gates():
    """只有 time 无 future → 非 FLS (双门控不被 substring 修破坏)。"""
    from news_process.pipeline.sentiment.forward_looking import _is_fls_sentence
    assert _is_fls_sentence('下一财年的财务报表附注') is False


def test_fls_component_match_still_works():
    """'未来三年' 经 component token (未来∈time, 三年∈time) + '计划'(future) 仍命中 (无回归)。"""
    from news_process.pipeline.sentiment.forward_looking import _is_fls_sentence
    assert _is_fls_sentence('计划在未来三年内实现翻倍') is True


# ── tone_words IDF 语料 ───────────────────────────────────────────────────────
def test_idf_df_reflects_given_text_col():
    """build_idf_weights 在传入的 text_col 上统计 DF: 标题词 '银行' 仅在 content_full 出现,
    故 content_full 语料下其 DF (=2) ≠ 裸 '内容' 语料下 (=0) → idf 不同。"""
    from news_process.pipeline.sentiment.tone_words import build_idf_weights
    df = pd.DataFrame({
        '内容': ['科技 发展 创新', '研发 突破 提升'],
        'content_full': ['银行 科技 发展 创新', '银行 研发 突破 提升'],
    })
    dicts = [('test', {'银行': 1.0, '科技': 1.0})]
    idf_neirong = build_idf_weights(df, dicts, text_col='内容')
    idf_full = build_idf_weights(df, dicts, text_col='content_full')
    # '银行' 在 '内容' 语料 df=0 (OOV), 在 content_full df=2 → 两语料 idf 应不同
    assert idf_neirong['test'].get('银行') != idf_full['test'].get('银行'), (
        'IDF 应随 text_col 语料变化 ("银行" 仅在 content_full 出现)')
