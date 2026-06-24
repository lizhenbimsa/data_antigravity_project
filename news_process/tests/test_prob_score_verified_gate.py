"""tests/test_prob_score_verified_gate.py — tonellms-prob-score 修复回归锁

avg_prob_score (连续稳健/falsification 主 DV) 与离散主 DV (final_s) 须在**同一观测子集**:
  - 模型级门控: 仅 verified=True 模型计入 (镜像 s_votes_verified_only)。
  - 文章级门控 (PROBGATE-1, review-closure 2026-06-10): final_s 为 None 时 avg_prob_score 同步置 NaN。
fix metric-audit 2026-06-10 (升 P1) + review-closure。注: 落盘待 production run。

⚠ 更新 (用户决策 2026-06-23, 逆转 v6/F2): verified 轨情感**平局/空票不再产 None**,
  改保守降级为'中性' (final_s 非 None) → 其 avg_prob_score 取 verified 模型 prob 均值
  (不再 NaN)。故"final_s is None ⇒ avg NaN"现**仅** = final_v=False (Case B 非金科) 一种态;
  原 test_sentiment_tie_nulls_avg_prob (断言平局→None→NaN) 是该提交遗漏更新的陈旧锁, 已随
  2026-06-24 平局/空票重试工作对齐为 test_sentiment_tie_yields_neutral_avg_is_verified_mean。
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


def test_sentiment_tie_yields_neutral_avg_is_verified_mean():
    """用户决策 2026-06-23 (逆转 v6/F2): final_v=True 但 verified 模型情感平局 (正面/负面)
    → 保守降级 final_s='中性' (不再 None), avg_prob_score = 两 verified 模型 prob 均值
    (不再 NaN; 正/负对称 → ≈0)。与 test_aggregate_track_decoupling 的同款保守降级断言一致。

    注 (2026-06-24): 该平局发生前, 生产路径 (run_all_llms→_resolve_unresolved_sentiment_tracks)
    会先绕过缓存重试至多 80 轮 (逐轮全局 barrier, 每轮内并发) 尝试打破; 本测试直接调
    _aggregate_track 验证**重试耗尽后**的保守降级兜底 (即仍平局时的最终聚合契约)。"""
    from news_process.pipeline.sentiment import tone_llms
    models = [{'short_name': 'm1', 'model_name': 'model-1'},
              {'short_name': 'm2', 'model_name': 'model-2'}]
    # 两 verified 模型 正面+负面 → final_v=majority([T,T])=True, sentiment tie → 保守降级 '中性'
    mrd = {
        'model-1': json.dumps({'is_bank_fintech_news': True, 'sentiment': '正面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
        'model-2': json.dumps({'is_bank_fintech_news': True, 'sentiment': '负面',
                               'sentiment_confidence': 0.9, 'verification_confidence': 0.9}),
    }
    final_v, final_s, avg = _idx(tone_llms._aggregate_track(mrd, models))
    assert final_v is True and final_s == '中性'   # 保守降级 (用户决策 2026-06-23), 非 None
    assert not math.isnan(avg), f'平局保守降级中性后 avg_prob_score 应取 verified 均值, 不应 NaN, 实得 {avg}'
    # avg = mean(prob(正面,0.9), prob(负面,0.9)); 正/负对称 → 0
    exp = (tone_llms.compute_prob_score('正面', 0.9)['prob_score']
           + tone_llms.compute_prob_score('负面', 0.9)['prob_score']) / 2
    assert abs(avg - exp) < 1e-9, f'avg_prob_score={avg}, 期望 verified 模型均值 {exp}'
