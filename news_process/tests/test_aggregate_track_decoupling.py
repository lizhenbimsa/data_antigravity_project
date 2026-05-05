"""F2 修复 — 篇章级编码契约重写 单元测试 (v6/E1)

校验点:
1. _aggregate_track 不再因 verified=False 强制改 sentiment 为 "中性"
2. majority_vote_sentiment 平局返回 None (tie_strategy='undefined')
3. 21 输出含 n_valid_votes_* / n_verifying_votes_* / llm_call_failure_* / llm_undefined_*
4. encode_sentiment 把 测量失败/平局/verification 失败 行映射为 NaN 而非 0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

# Phase 7a-4: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = Path(__file__).resolve()
_PROJECT_PARENT = _HERE.parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def _build_response(verified: bool, sentiment: str, ver_conf: float = 0.9, sent_conf: float = 0.85) -> str:
    return json.dumps({
        "is_bank_fintech_news": verified,
        "sentiment": sentiment,
        "verification_confidence": ver_conf,
        "sentiment_confidence": sent_conf,
        "fintech_topic": "数字人民币",
        "fintech_category": "应用场景",
        "text_type": "实质性",
    }, ensure_ascii=False)


@pytest.fixture(scope="module")
def models():
    return [
        {"short_name": "gpt5nano", "model_name": "gpt-5-nano-2025-08-07"},
        {"short_name": "gemini3", "model_name": "gemini-3-flash-preview-nothinking"},
        {"short_name": "grok41", "model_name": "grok-4-1-fast-non-reasoning"},
    ]


def test_majority_vote_sentiment_tie_returns_none():
    from news_process.pipeline.sentiment.tone_llms import majority_vote_sentiment
    # 平局: 1 正面 + 1 负面 → undefined (None)
    assert majority_vote_sentiment(["正面", "负面"]) is None
    # 平局-neutral 兼容路径
    assert majority_vote_sentiment(["正面", "负面"], tie_strategy='neutral') == "中性"
    # 一致: 全 正面
    assert majority_vote_sentiment(["正面", "正面", "正面"]) == "正面"
    # 多数: 2 正面 + 1 负面
    assert majority_vote_sentiment(["正面", "正面", "负面"]) == "正面"
    # 空票
    assert majority_vote_sentiment([]) is None


def test_aggregate_track_no_forced_neutral(models):
    """单模型 verified=False 时，其 sentiment 应保持原值，不被强制改写为中性。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    # gpt5nano 拒绝（verified=False, sentiment 标 "正面"）；gemini3/grok41 通过
    res = {
        "gpt-5-nano-2025-08-07": _build_response(False, "正面"),
        "gemini-3-flash-preview-nothinking": _build_response(True, "正面"),
        "grok-4-1-fast-non-reasoning": _build_response(True, "正面"),
    }
    out = _aggregate_track(res, models)
    final_v, final_s, agree_v, agree_s, n_valid, n_verifying, call_fail, undefined, parsed, *_ = out
    assert final_v is True
    assert final_s == "正面"
    # 关键: gpt5nano 的 sentiment 不再被强制改为 "中性"
    assert parsed["gpt5nano_sentiment"] == "正面"
    assert parsed["gpt5nano_verified"] is False
    assert n_valid == 3
    assert n_verifying == 2
    assert call_fail == 0
    assert undefined == 0


def test_aggregate_track_three_way_disagreement_yields_undefined(models):
    """三方完全分歧（正面/中性/负面）且全部 verified → 平局 → final_s = None, undefined=1。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    res = {
        "gpt-5-nano-2025-08-07": _build_response(True, "正面"),
        "gemini-3-flash-preview-nothinking": _build_response(True, "中性"),
        "grok-4-1-fast-non-reasoning": _build_response(True, "负面"),
    }
    out = _aggregate_track(res, models)
    final_v, final_s, _, _, n_valid, n_verifying, _, undefined, *_ = out
    assert final_v is True
    assert final_s is None
    assert n_valid == 3
    assert n_verifying == 3
    assert undefined == 1


def test_aggregate_track_call_failure(models):
    """全部模型 API 调用失败 → call_failure=1, final_s=None。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    res = {
        "gpt-5-nano-2025-08-07": None,
        "gemini-3-flash-preview-nothinking": None,
        "grok-4-1-fast-non-reasoning": None,
    }
    out = _aggregate_track(res, models)
    final_v, final_s, _, _, n_valid, n_verifying, call_fail, undefined, *_ = out
    assert final_v is False
    assert final_s is None
    assert n_valid == 0
    assert call_fail == 1


def test_aggregate_track_only_verifying_models_vote_sentiment(models):
    """关键 F2 测试：拒绝模型 (verified=False) 的 sentiment 不参与最终情感投票。

    历史 bug：拒绝模型 sentiment 被强制改为 "中性"后 → 进入投票 → 拉低 final_s。
    v6 行为：拒绝模型 sentiment 不计入 final_s 计算。
    """
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    # gpt5nano 拒绝且 sentiment="负面"（如果走旧逻辑会被改为"中性"再进投票）
    # gemini3 + grok41 通过 + sentiment="正面" → 应得 final_s="正面"
    res = {
        "gpt-5-nano-2025-08-07": _build_response(False, "负面"),
        "gemini-3-flash-preview-nothinking": _build_response(True, "正面"),
        "grok-4-1-fast-non-reasoning": _build_response(True, "正面"),
    }
    out = _aggregate_track(res, models)
    final_v, final_s, *_ = out
    assert final_v is True
    assert final_s == "正面"  # 应是"正面"（仅 verifying 模型投票）；旧逻辑可能为"中性"


def test_encode_sentiment_propagates_nan_for_invalid_rows(monkeypatch):
    """encode_sentiment 应让 verification 失败 / call_failure / undefined 行的
    is_neutral / vote_score 为 NaN（pandas Int8 nullable），而非 0。"""
    from news_process.pipeline.panel import encode

    df = pd.DataFrame({
        # row 0: verified=True, sentiment="正面" → score=1, is_neutral=0
        # row 1: verified=False (拒绝), sentiment="中性" → score=NaN, is_neutral=NaN
        # row 2: verified=True, undefined=1 (平局) → score=NaN, is_neutral=NaN
        # row 3: verified=True, call_failure=1 → score=NaN, is_neutral=NaN
        # row 4: verified=True, sentiment="中性"（真实中性）→ score=0, is_neutral=1
        "llm_verified_full": [True, False, True, True, True],
        "llm_sentiment_full": ["正面", "中性", None, None, "中性"],
        "llm_call_failure_full": [0, 0, 0, 1, 0],
        "llm_undefined_full": [0, 0, 1, 0, 0],
        "llm_agreement_rate_full": [1.0, 0.67, 0.33, 0.0, 1.0],
    })
    out = encode.encode_sentiment(df.copy())

    # row 0: verified+positive → vote_score=1
    assert out["llm_vote_score_full"].iloc[0] == 1
    assert out["is_positive_full"].iloc[0] == 1
    assert out["is_neutral_full"].iloc[0] == 0

    # row 1: verified=False → vote_score 应为 <NA>
    assert pd.isna(out["llm_vote_score_full"].iloc[1])
    assert pd.isna(out["is_neutral_full"].iloc[1])

    # row 2: undefined=1 → vote_score 应为 <NA>
    assert pd.isna(out["llm_vote_score_full"].iloc[2])
    assert pd.isna(out["is_neutral_full"].iloc[2])

    # row 3: call_failure=1 → vote_score 应为 <NA>
    assert pd.isna(out["llm_vote_score_full"].iloc[3])
    assert pd.isna(out["is_neutral_full"].iloc[3])

    # row 4: 真实中性 → vote_score=0, is_neutral=1
    assert out["llm_vote_score_full"].iloc[4] == 0
    assert out["is_neutral_full"].iloc[4] == 1


def test_v6_llm_models_are_real_three_families():
    """v6 锁定: LLM_MODELS 应为真三家族 (OpenAI + Google + xAI)，无 claude4h。"""
    from news_process.pipeline.panel.encode import LLM_MODELS
    assert "claude4h" not in LLM_MODELS
    # short_name 顺序应反映 sentiment.yaml 配置（默认 fallback: gpt5nano/gemini3/grok41）
    assert set(LLM_MODELS) == {"gpt5nano", "gemini3", "grok41"} or \
        len(LLM_MODELS) == 3  # 容许配置自定义但必须 3 slot
