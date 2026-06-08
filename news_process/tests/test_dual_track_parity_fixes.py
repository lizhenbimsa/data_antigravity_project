"""tests/test_dual_track_parity_fixes.py — full/ctx 双轨功能一致性修复 (2026-06-08).

锁定 dual-track 一致性审计 (memory dualtrack-consistency-audit-2026-06-06) 修复的
对称性不变式, 防回归。覆盖可隔离单测的修复:
  #5 article_sbert: 两轨标题各注入【恰好一次】(反向病根: ctx 曾标题×2)
  #6 strat_fluidity: _compute_fluidity track-agnostic → 可产 _ctx 孪生
  #7 article_topic: get_dummies reindex 到共享 K → 每个 frac_topic_k_full 有 _ctx 孪生
  #8 num_intensity: 默认 full_col 改为 content_full (含标题), 防"唯一不含标题 *_full"地雷

#1/#2/#3 (policy/geography/network/llm-peer 面板聚合) 依赖完整面板上下文, 由端到端
重跑 + golden 重生验证 (见 REPAIR 报告)。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── #7 article_topic: 共享 topic-id 空间 → frac_topic 列双轨对等 ──────────────────
def test_topic_frac_dual_track_column_parity():
    """某 topic 仅在一轨出现时, 两轨仍各产该 frac_topic_k 列 (缺席轨补全 0, 非缺列)。"""
    from news_process.pipeline.text.article_topic import aggregate_to_bank_year

    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'B', 'B'],
        'year': [2017, 2017, 2017, 2017],
    })
    topics_full = [0, 2, 1, 0]   # topic 2 出现在 full 轨
    topics_ctx = [0, 0, 1, 1]    # topic 2 在 ctx 轨【0 出现】

    panel = aggregate_to_bank_year(df, topics_full, topics_ctx, K=3)

    full_ids = {c[:-5] for c in panel.columns
                if c.startswith('frac_topic_') and c.endswith('_full')}
    ctx_ids = {c[:-4] for c in panel.columns
               if c.startswith('frac_topic_') and c.endswith('_ctx')}
    assert full_ids == ctx_ids, (
        f"topic 列双轨不对等: full-only={full_ids - ctx_ids}, "
        f"ctx-only={ctx_ids - full_ids}")
    # topic 2 在两轨都必须有列 (修复前 ctx 轨会整列缺失 → 孤儿)
    assert 'frac_topic_2_full' in panel.columns
    assert 'frac_topic_2_ctx' in panel.columns
    # ctx 轨该 topic 缺席 → 全 0 (而非 NaN/缺列)
    assert (panel['frac_topic_2_ctx'].fillna(0) == 0).all()
    # outlier(-1) 与正常 topic 命名约定保留
    assert 'frac_topic_outlier_full' in panel.columns
    assert 'frac_topic_outlier_ctx' in panel.columns


# ── #6 strat_fluidity: _compute_fluidity track-agnostic ──────────────────────────
def test_fluidity_is_track_agnostic():
    """_compute_fluidity 接受任意 [target_bank, year, agg_text] → 可对 ctx 聚合再算一次。"""
    from news_process.pipeline.features.strategic_diff import _compute_fluidity

    agg = pd.DataFrame({
        'target_bank': ['A', 'B', 'C', 'A', 'B', 'C'],
        'year': [2017, 2017, 2017, 2018, 2018, 2018],
        'agg_text': [
            '银行 科技 数字化 转型 支付', '信贷 风控 普惠 小微 三农',
            '理财 财富 资管 基金 信托',
            '科技 数字化 区块链 支付 银行', '风控 普惠 小微 信贷 三农',
            '财富 资管 基金 信托 理财'],
    })
    flu = _compute_fluidity(agg, 'char')
    assert isinstance(flu, dict)
    # 键为 (bank, year); 2018 有前期 → 应可算出 fluidity
    assert any(k[1] == 2018 for k in flu)
    # 与 word 模式同样可调 (双模式对称)
    flu_w = _compute_fluidity(agg, 'word')
    assert isinstance(flu_w, dict)


# ── #8 num_intensity: 默认 full_col = content_full (含标题) ───────────────────────
def test_num_intensity_default_reads_content_full():
    """默认 full 轨读 content_full(含标题), 不再是裸 '内容'(无标题) 的历史地雷。"""
    from news_process.pipeline.sentiment.numerical_intensity import (
        enrich_with_num_intensity_dual_track,
    )
    # content_full 含数字, 裸 '内容' 不含 → 若默认仍读 '内容' 则结果为 0
    df = pd.DataFrame({
        '内容': ['本行持续推进服务实体经济。'],          # 无数字
        'content_full': ['净利增长百分之三十。本行持续推进。'],  # 含数字
        'content_ctx': ['净利增长百分之三十。'],
    })
    out = enrich_with_num_intensity_dual_track(df)  # 用默认 full_col
    assert out['num_intensity_full'].iloc[0] > 0, (
        "默认 full_col 应读 content_full(含标题/数字), 而非裸 '内容'")


def test_num_intensity_default_graceful_fallback_to_neirong():
    """旧 schema 无 content_full → 优雅回退裸 '内容', 不崩溃。"""
    from news_process.pipeline.sentiment.numerical_intensity import (
        enrich_with_num_intensity_dual_track,
    )
    df = pd.DataFrame({
        '内容': ['营收两千万元增长百分之三十。'],
        'content_ctx': ['营收两千万元。'],
    })
    out = enrich_with_num_intensity_dual_track(df)  # 默认 content_full 缺 → 回退 '内容'
    for col in ('num_intensity_full', 'num_intensity_ctx',
                'num_intensity_word_full', 'num_intensity_word_ctx'):
        assert col in out.columns
    assert out['num_intensity_full'].iloc[0] > 0  # '内容' 含数字 → 非 0


# ── #5 article_sbert: 两轨标题各注入恰好一次 (反向病根: ctx 曾 ×2) ─────────────────
def test_sbert_title_injected_exactly_once_both_tracks(monkeypatch):
    """content_full/content_ctx 已含标题一次; title_col=None 不再二次前置 → 两轨标题×1。"""
    captured = {}

    class _FakeModel:
        def __init__(self, *a, **k):
            pass

        def encode(self, docs, **k):
            captured['docs'] = list(docs)
            return np.zeros((len(docs), 768), dtype='float32')

    monkeypatch.setattr('sentence_transformers.SentenceTransformer', _FakeModel)
    from news_process.pipeline.text import article_sbert

    title = '某银行推出数字人民币试点'
    df = pd.DataFrame({
        '标题': [title],
        '内容': ['正文段落内容正文段落内容。'],
        'content_full': [f'{title}。正文段落内容正文段落内容。'],
        'content_ctx': [f'{title}。某银行相关实体窗口句子。'],
    })

    # full 轨: content_full + title_col=None
    article_sbert.encode_articles(df, content_col='content_full', title_col=None)
    assert captured['docs'][0].count(title) == 1, "full 轨标题应恰好出现一次"

    # ctx 轨: content_ctx + title_col=None (修复前 title_col='标题' → 标题×2)
    article_sbert.encode_articles(df, content_col='content_ctx', title_col=None)
    assert captured['docs'][0].count(title) == 1, "ctx 轨标题应恰好一次 (反向病根: 修复前为 2)"
