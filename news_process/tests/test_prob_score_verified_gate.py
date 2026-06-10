"""tests/test_prob_score_verified_gate.py — tonellms-prob-score 修复回归锁

avg_prob_score (连续稳健/falsification 主 DV) 与离散主 DV (final_s) 须在**同一观测子集**:
  - 模型级门控: 仅 verified=True 模型计入 (镜像 s_votes_verified_only)。
  - 文章级门控 (PROBGATE-1, review-closure 2026-06-10): final_s 为 None 时 (final_v=False 整文
    被拒, 或 sentiment tie/undefined) avg_prob_score 同步置 NaN。
fix metric-audit 2026-06-10 (升 P1) + review-closure。注: 落盘待 production run。
"""
from __future__ import annotations

import json
import math


def _idx(result):
    # _aggregate_track 返回元组: (final_v, final_s, ..., n_failures(12), avg_prob_score(13), ...)
    return result[0], result[1], result[13]


def test_rejected_article_nulls_avg_prob():
    """final_v=False(多数判非 fintech) → final_s=None → avg_prob_score 同步 NaN(文章级门控)。"""
    from news_process.pipeline.sentiment import tone_llms
    models = [{'short_name': 'm1', 'model_name': 'model-1'},
              {'short_name': 'm2', 'model_name': 'model-2'}]
    # m1 verified=True 正面, m2 verified=False 负面 → majority_vote_bool([T,F])=False
    mrd = {
        'model-1': json.dumps({'is_bank_fintech_news': True, 'sentiment': '正面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
        'model-2': json.dumps({'is_bank_fintech_news': False, 'sentiment': '负面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
    }
    final_v, final_s, avg = _idx(tone_llms._aggregate_track(mrd, models))
    assert final_v is False and final_s is None
    assert math.isnan(avg), f'final_v=False 时 avg_prob_score 应 NaN(与离散 DV 同子集), 实得 {avg}'


def test_verified_majority_uses_verified_models_only():
    """final_v=True 无 tie: avg_prob_score = 仅 verified 模型均值 (模型级门控, 排除未验证)。"""
    from news_process.pipeline.sentiment import tone_llms
    models = [{'short_name': 'm1', 'model_name': 'model-1'},
              {'short_name': 'm2', 'model_name': 'model-2'},
              {'short_name': 'm3', 'model_name': 'model-3'}]
    # m1,m2 verified 正面(prob 0.85); m3 未验证 负面(prob -0.85) → final_v=majority([T,T,F])=True
    mrd = {
        'model-1': json.dumps({'is_bank_fintech_news': True, 'sentiment': '正面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
        'model-2': json.dumps({'is_bank_fintech_news': True, 'sentiment': '正面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
        'model-3': json.dumps({'is_bank_fintech_news': False, 'sentiment': '负面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
    }
    final_v, final_s, avg = _idx(tone_llms._aggregate_track(mrd, models))
    assert final_v is True and final_s == '正面'
    # 仅 m1,m2 verified → mean(0.85,0.85)=0.85; 旧 bug 含 m3 → mean(0.85,0.85,-0.85)=0.283
    assert abs(avg - 0.85) < 1e-6, f'avg_prob_score={avg}, 期望 0.85 (仅 verified 模型), 非 0.283'


def test_sentiment_tie_nulls_avg_prob():
    """final_v=True 但 verified 模型情感 tie → final_s=None(undefined) → avg_prob_score NaN。"""
    from news_process.pipeline.sentiment import tone_llms
    models = [{'short_name': 'm1', 'model_name': 'model-1'},
              {'short_name': 'm2', 'model_name': 'model-2'}]
    # 两 verified 模型 正面+负面 → final_v=majority([T,T])=True, sentiment tie → final_s=None
    mrd = {
        'model-1': json.dumps({'is_bank_fintech_news': True, 'sentiment': '正面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
        'model-2': json.dumps({'is_bank_fintech_news': True, 'sentiment': '负面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
    }
    final_v, final_s, avg = _idx(tone_llms._aggregate_track(mrd, models))
    assert final_v is True and final_s is None
    assert math.isnan(avg), f'sentiment tie(final_s None) 时 avg_prob_score 应 NaN, 实得 {avg}'
