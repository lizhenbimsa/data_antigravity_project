"""Tests for compute_prob_score_binary (plan v1.37 P2 §5.3.5).

13 test functions; 17 parametrized cases (test 12: 2 P-paths; test 13: 4 mixes).
"""
import numpy as np
import pytest

from news_process.pipeline.sentiment.tone_llms import (
    compute_prob_score,
    compute_prob_score_binary,
)


def test_positive_label_positive_class():
    """Item 1: positive label matches positive_class, c=1.0."""
    r = compute_prob_score_binary("象征性", 1.0, "象征性")
    assert r == {"prob_score": 1.0, "prob_source": "P2_BIN"}


def test_negative_label_positive_class():
    """Item 2: label != positive_class, c=1.0 → 0.0 P2_BIN."""
    r = compute_prob_score_binary("实质性", 1.0, "象征性")
    assert r == {"prob_score": 0.0, "prob_source": "P2_BIN"}


def test_mid_confidence_positive():
    """Item 3: positive class match, c=0.5 → 0.5."""
    r = compute_prob_score_binary("象征性", 0.5, "象征性")
    assert r == {"prob_score": 0.5, "prob_source": "P2_BIN"}


def test_none_label():
    """Item 4: label None → NaN P3_BIN."""
    r = compute_prob_score_binary(None, 0.7, "象征性")
    assert np.isnan(r["prob_score"]) and r["prob_source"] == "P3_BIN"


def test_invalid_label():
    """Item 5: label not in VALID_BINARY_LABELS → NaN P3_BIN."""
    r = compute_prob_score_binary("invalid", 0.7, "象征性")
    assert np.isnan(r["prob_score"]) and r["prob_source"] == "P3_BIN"


def test_zero_confidence_positive():
    """Item 6: c=0, label==positive_class → 1.0 P3_BIN (one-hot fallback)."""
    r = compute_prob_score_binary("象征性", 0.0, "象征性")
    assert r == {"prob_score": 1.0, "prob_source": "P3_BIN"}


def test_zero_confidence_negative():
    """Item 7: c=0, label!=positive_class → 0.0 P3_BIN."""
    r = compute_prob_score_binary("实质性", 0.0, "象征性")
    assert r == {"prob_score": 0.0, "prob_source": "P3_BIN"}


def test_all_none_aggregation():
    """Item 8: 5 (None, NaN, positive) tuples → np.nanmean returns NaN."""
    results = [compute_prob_score_binary(None, np.nan, "象征性") for _ in range(5)]
    scores = [r["prob_score"] for r in results]
    # All NaN → np.nanmean of all-NaN returns NaN with warning
    with np.errstate(all="ignore"):
        result = np.nanmean(scores) if any(not np.isnan(s) for s in scores) else float("nan")
    assert np.isnan(result)


def test_mismatched_positive_class():
    """Item 9: positive_class not in VALID → NaN P3_BIN (Rule 0)."""
    r = compute_prob_score_binary("象征性", 1.0, "不存在")
    assert np.isnan(r["prob_score"]) and r["prob_source"] == "P3_BIN"


def test_confidence_clamp_above_one():
    """Item 10: c > 1 → NaN P3_BIN."""
    r = compute_prob_score_binary("象征性", 1.0001, "象征性")
    assert np.isnan(r["prob_score"]) and r["prob_source"] == "P3_BIN"


def test_confidence_clamp_below_zero():
    """Item 11: c < 0 → NaN P3_BIN."""
    r = compute_prob_score_binary("象征性", -0.0001, "象征性")
    assert np.isnan(r["prob_score"]) and r["prob_source"] == "P3_BIN"


@pytest.mark.parametrize(
    "args, expected",
    [
        # P2 path: (正面, 0.7) → prob_score = 0.7 - 0.15 = 0.55, P2 source
        (("正面", 0.7),
         {"prob_pos": 0.7, "prob_neu": pytest.approx(0.15),
          "prob_neg": pytest.approx(0.15), "prob_score": 0.55, "prob_source": "P2"}),
        # P3 path: (None, 0.0) → cls=neutral, c=0, P3 one-hot, prob_score=0
        ((None, 0.0),
         {"prob_pos": 0.0, "prob_neu": 1.0, "prob_neg": 0.0,
          "prob_score": 0.0, "prob_source": "P3"}),
    ],
)
def test_three_class_compute_prob_score_unchanged_smoke(args, expected):
    """Item 12: parametrized smoke for 3-class compute_prob_score (P2/P3 paths)."""
    r = compute_prob_score(*args)
    for k, v in expected.items():
        if isinstance(v, float):
            assert r[k] == v or r[k] == pytest.approx(v), f"{k}: {r[k]} != {v}"
        else:
            assert r[k] == v, f"{k}: {r[k]} != {v}"


@pytest.mark.parametrize(
    "case",
    [
        "all_valid",
        "one_invalid_label",
        "one_missing_field",
        "one_api_failure",
    ],
)
def test_per_model_innovation_labels_stored(case):
    """Item 13 (4 cases): _aggregate_track stores per-model innovation
    labels in per_model_parsed for all 3 models, regardless of branch."""
    import json as _json

    from news_process.pipeline.sentiment.tone_llms import _aggregate_track
    models = [
        {"short_name": "m1", "model_name": "model_1"},
        {"short_name": "m2", "model_name": "model_2"},
        {"short_name": "m3", "model_name": "model_3"},
    ]
    base = {
        "is_bank_fintech_news": True,
        "sentiment": "正面",
        "sentiment_confidence": 0.8,
        "verification_confidence": 0.9,
        "innovation_locus": "底层技术",
        "innovation_substantiveness": "实质性",
        "innovation_locus_confidence": 0.7,
        "innovation_substantiveness_confidence": 0.7,
    }
    res = {"model_1": _json.dumps(base),
           "model_2": _json.dumps(base),
           "model_3": _json.dumps(base)}
    if case == "one_invalid_label":
        bad = dict(base); bad["innovation_locus"] = "其他"
        res["model_2"] = _json.dumps(bad)
    elif case == "one_missing_field":
        miss = dict(base); miss.pop("innovation_locus")
        res["model_2"] = _json.dumps(miss)
    elif case == "one_api_failure":
        res["model_2"] = None

    out = _aggregate_track(res, models)
    parsed = out[8]

    # All 3 models' 4 innovation keys must be present (per Step A default-init)
    for sh in ["m1", "m2", "m3"]:
        assert f"{sh}_innovation_locus" in parsed
        assert f"{sh}_innovation_substantiveness" in parsed
        assert f"{sh}_innovation_locus_confidence" in parsed
        assert f"{sh}_innovation_substantiveness_confidence" in parsed

    if case == "all_valid":
        assert parsed["m2_innovation_locus"] == "底层技术"
    else:
        # m2 has invalid/missing/api-failure → label None
        assert parsed["m2_innovation_locus"] is None
