"""v3.2.0 — Stage 3 双轨化测试 (plan v14 §5.1 + §5.4)

锚定文献:
    Hassan, Hollander, van Lent, Tahoun (2019, QJE) entity-proximity attribution
    Sautner, Van Lent, Vilkov, Zhang (2023, JF) firm × topic 邻近化
    Bingler, Kraus, Leippold, Webersinke (2022, FRL) substantive vs cheap talk
    Westphal & Zajac (1994, 1998, ASQ) substantive-symbolic
    Gomber, Kauffman, Parker, Weber (2018, JMIS) enabling tech vs business function
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def _build_dual(
    verified: bool = True,
    sentiment: str = "正面",
    locus: str = "应用场景",
    subst: str = "实质性",
    ver_conf: float = 0.9,
    sent_conf: float = 0.85,
    loc_conf: float = 0.9,
    sub_conf: float = 0.85,
    topic: str = "数字人民币",
) -> str:
    """构造 v7 JSON 响应, 各字段可显式覆盖。"""
    return json.dumps({
        "is_bank_fintech_news": verified,
        "sentiment": sentiment,
        "verification_confidence": ver_conf,
        "sentiment_confidence": sent_conf,
        "fintech_topic": topic,
        "innovation_locus": locus,
        "innovation_locus_confidence": loc_conf,
        "innovation_substantiveness": subst,
        "innovation_substantiveness_confidence": sub_conf,
    }, ensure_ascii=False)


@pytest.fixture(scope="module")
def models():
    return [
        {"short_name": "gpt54nano", "model_name": "gpt-5.4-nano"},
        {"short_name": "gemini31", "model_name": "gemini-3.1-flash-lite-preview"},
        {"short_name": "deepseekv4", "model_name": "deepseek-v4-flash"},
    ]


def test_ctx_locus_independent_of_full(models):
    """Plan v14 §3.1 P1 (R3-B): ctx 轨 locus 应当与 full 轨独立, 可输出不同标签。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    # 全部 verified=True; full 轨全部标"底层技术"
    full = {
        m["model_name"]: _build_dual(locus="底层技术") for m in models
    }
    out_full = _aggregate_track(full, models)
    # v3.4.0: 18 元组 (为 Chesbrough 2003 新增 innov_collab_modes + avg_collab_prob_score)
    _, _, _, _, _, _, _, _, _, _, innov_loci_full, _, _, _, _, _, _, _ = out_full
    assert innov_loci_full == ["底层技术", "底层技术", "底层技术"], innov_loci_full

    # ctx 轨独立: 全部标 "应用场景"
    ctx = {
        m["model_name"]: _build_dual(locus="应用场景") for m in models
    }
    out_ctx = _aggregate_track(ctx, models)
    _, _, _, _, _, _, _, _, _, _, innov_loci_ctx, _, _, _, _, _, _, _ = out_ctx
    assert innov_loci_ctx == ["应用场景", "应用场景", "应用场景"], innov_loci_ctx


def test_ctx_substantiveness_independent_of_full(models):
    """W&Z framework: full 轨判 '实质性' 时 ctx 轨可独立判 '象征性'."""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    full = {m["model_name"]: _build_dual(subst="实质性") for m in models}
    ctx = {m["model_name"]: _build_dual(subst="象征性") for m in models}

    # v3.4.0: 18 元组 (为 Chesbrough 2003 新增 innov_collab_modes + avg_collab_prob_score)
    _, _, _, _, _, _, _, _, _, _, _, innov_substs_full, _, _, _, _, _, _ = _aggregate_track(full, models)
    _, _, _, _, _, _, _, _, _, _, _, innov_substs_ctx, _, _, _, _, _, _ = _aggregate_track(ctx, models)

    assert innov_substs_full == ["实质性"] * 3
    assert innov_substs_ctx == ["象征性"] * 3


def test_tie_strategy_symmetry_locus(models):
    """Plan v14 §3.1 P1.5: ctx 轨 locus 平局策略与 full 轨完全对称 (降至 '应用场景')."""
    from news_process.pipeline.sentiment.tone_llms import majority_vote_categorical
    # 1 vs 1 平局
    for track in ['full', 'ctx']:
        out = majority_vote_categorical(
            ["底层技术", "应用场景"],
            tie_strategy='conservative',
            tie_default='应用场景',
            empty_fallback='应用场景',
        )
        assert out == "应用场景", f"track={track}: {out}"


def test_tie_strategy_symmetry_substantiveness(models):
    """Plan v14 §3.1 P1.5: ctx 轨 substantiveness 平局策略与 full 轨对称 (降至 '象征性')."""
    from news_process.pipeline.sentiment.tone_llms import majority_vote_categorical
    out = majority_vote_categorical(
        ["实质性", "象征性"],
        tie_strategy='conservative',
        tie_default='象征性',
        empty_fallback=None,
    )
    assert out == "象征性"


def test_empty_ctx_locus_falls_back_to_keyword(models):
    """Plan v14 §3.1 P1: ctx 轨 locus 空票回退到 canonicalize_topic(topics_ctx)."""
    from news_process.pipeline.sentiment.tone_llms import majority_vote_categorical
    # 空 votes + fallback
    out = majority_vote_categorical(
        [],
        tie_strategy='conservative',
        tie_default='应用场景',
        empty_fallback='底层技术',  # 模拟 kw_category(topics_ctx) 结果
    )
    assert out == "底层技术"  # 关键词分类器输出, 非 tie_default


def test_empty_ctx_substantiveness_falls_back_to_none(models):
    """W&Z: ctx 轨 substantiveness 空票 → None (不强制象征性)."""
    from news_process.pipeline.sentiment.tone_llms import majority_vote_categorical
    out = majority_vote_categorical(
        [],
        tie_strategy='conservative',
        tie_default='象征性',
        empty_fallback=None,
    )
    assert out is None
