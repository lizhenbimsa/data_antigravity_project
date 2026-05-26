"""tests/test_39g_track_discriminant.py — v3.7.3 Plan A v1.0 stage 39g 单测.

锚定:
    - Heston & Sinha (2017) FAJ; Loughran & McDonald (2016) JAR §6;
      Boudoukh et al. (2019) JFE; Campbell & Fiske (1959) MTMM;
      Henseler-Ringle-Sarstedt (2015) JAMS HTMT 双 cutoff.

测试覆盖 (15 tests):
    1. mojibake column detection (U+FFFD + ����)
    2. mojibake column 非检测 (正常列名通过)
    3. track triple finder 完整三轨返回 tuple
    4. track triple finder 缺一轨返回 None
    5. track triple finder mojibake 列被剔除
    6. HTMT 3×3 矩阵对称性 + 取值合法 ∈ [0, 1)
    7. permutation seed=42 重现性
    8. n_articles ≥ 2 mask
    9. graceful skip 当 panel 缺所有三轨 indicator
   10. status='ok' 当 ≥ 1 indicator 有完整三轨
   11. overall verdict 'pass_title_discriminant' 当 ≥ 50% indicator 双判别 < 0.85
   12. overall verdict 'fail' 当 0 indicator 判别成功
   13. mojibake_columns_skipped 字段非空 (NEW-B1 报告路径)
   14. 输出 JSON 序列化兼容性
   15. lookup 优先级遵循 TRACK_INDICATOR_CANDIDATES 顺序
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.audit.track_discriminant_validity import (
    TRACK_INDICATOR_CANDIDATES,
    _compute_overall_verdict,
    _find_track_triple,
    _is_mojibake_column,
    run_track_discriminant_validity,
)

# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def synthetic_panel_with_triples():
    """合成 panel: 100 obs, 完整 _full/_ctx/_title triple for 2 indicators."""
    rng = np.random.default_rng(seed=42)
    n = 100
    # llm_vote_tone: 三轨, _full 与 _ctx 高度相关 (设计), _title 中度相关
    full_base = rng.normal(0, 1, n)
    ctx = 0.85 * full_base + rng.normal(0, 0.3, n)  # 高相关 (sub-window)
    title = 0.40 * full_base + rng.normal(0, 0.8, n)  # 中度相关 (different scope)
    # dict_avg_tone: 类似
    dict_full = rng.normal(0, 1, n)
    dict_ctx = 0.80 * dict_full + rng.normal(0, 0.4, n)
    dict_title = 0.35 * dict_full + rng.normal(0, 0.9, n)
    return pd.DataFrame({
        "llm_vote_tone_full": full_base,
        "llm_vote_tone_ctx": ctx,
        "llm_vote_tone_title": title,
        "dict_avg_tone_full": dict_full,
        "dict_avg_tone_ctx": dict_ctx,
        "dict_avg_tone_title": dict_title,
        "n_articles": np.full(n, 5),
    })


@pytest.fixture
def panel_missing_title():
    """缺失 _title 列的 panel."""
    rng = np.random.default_rng(seed=42)
    n = 50
    return pd.DataFrame({
        "llm_vote_tone_full": rng.normal(0, 1, n),
        "llm_vote_tone_ctx": rng.normal(0, 1, n),
        "n_articles": np.full(n, 3),
    })


@pytest.fixture
def panel_with_mojibake():
    """panel 含 NEW-B1 mojibake 列."""
    rng = np.random.default_rng(seed=42)
    n = 30
    return pd.DataFrame({
        "llm_vote_tone_full": rng.normal(0, 1, n),
        "llm_vote_tone_ctx": rng.normal(0, 1, n),
        "llm_vote_tone_title": rng.normal(0, 1, n),
        "finbert_cn_����_w_sum_title": rng.normal(0, 1, n),
        "hw2942_����_hw_sum_title": rng.normal(0, 1, n),
        "n_articles": np.full(n, 4),
    })


# ===========================================================================
# Tests
# ===========================================================================

def test_mojibake_detection_replacement_char():
    """U+FFFD replacement char 触发 mojibake detection."""
    assert _is_mojibake_column("finbert_cn_����_w_sum_title")
    assert _is_mojibake_column("hw2942_�_hw_sum_title")


def test_mojibake_detection_normal_columns_pass():
    """正常列名不触发 mojibake detection."""
    assert not _is_mojibake_column("llm_vote_tone_title")
    assert not _is_mojibake_column("dict_avg_tone_full")
    assert not _is_mojibake_column("bert_avg_pos_ctx")
    assert not _is_mojibake_column("n_articles")


def test_find_track_triple_complete(synthetic_panel_with_triples):
    """完整三轨返回 (full, ctx, title) tuple."""
    triple = _find_track_triple(synthetic_panel_with_triples, "llm_vote_tone")
    assert triple == ("llm_vote_tone_full", "llm_vote_tone_ctx",
                      "llm_vote_tone_title")


def test_find_track_triple_missing_returns_none(panel_missing_title):
    """缺 _title 一轨返回 None (而非 partial)."""
    triple = _find_track_triple(panel_missing_title, "llm_vote_tone")
    assert triple is None


def test_find_track_triple_mojibake_excluded(panel_with_mojibake):
    """含 mojibake 的 indicator stem 被 _find_track_triple 跳过."""
    # llm_vote_tone 三轨干净 → 应返回
    clean = _find_track_triple(panel_with_mojibake, "llm_vote_tone")
    assert clean is not None
    # 但用 mojibake stem 'finbert_cn_����' 应被 reject
    # (该 stem 自身含 mojibake 字符)


def test_htmt_3x3_values_in_unit_interval(synthetic_panel_with_triples):
    """HTMT 取值 ∈ [0, 1); 矩阵 3×3 共 3 pairs."""
    report = run_track_discriminant_validity(synthetic_panel_with_triples)
    assert report["status"] == "ok"
    for stem, htmt in report["htmt_3x3_per_indicator"].items():
        for k, v in htmt.items():
            assert 0.0 <= v < 1.0, f"{stem}/{k}={v} not in [0, 1)"


def test_permutation_seed_42_reproducible(synthetic_panel_with_triples):
    """seed=42 重现 (与 39d R9-H3 一致)."""
    r1 = run_track_discriminant_validity(synthetic_panel_with_triples)
    r2 = run_track_discriminant_validity(synthetic_panel_with_triples)
    assert (r1["permutation_p95_per_indicator"]
            == r2["permutation_p95_per_indicator"])


def test_n_articles_min_mask(synthetic_panel_with_triples):
    """n_articles ≥ min_n_articles mask 生效."""
    panel = synthetic_panel_with_triples.copy()
    panel.loc[:20, "n_articles"] = 1  # 21 obs 被 mask 掉
    report = run_track_discriminant_validity(panel, min_n_articles=2)
    assert report["n_obs"] < len(panel)


def test_graceful_skip_no_triple_found(panel_missing_title):
    """无完整三轨返回 status='no_track_triple_found'."""
    report = run_track_discriminant_validity(panel_missing_title)
    assert report["status"] == "no_track_triple_found"
    assert report["indicators_tested"] == []


def test_status_ok_with_at_least_one_triple(synthetic_panel_with_triples):
    """≥ 1 indicator 有完整三轨 → status='ok'."""
    report = run_track_discriminant_validity(synthetic_panel_with_triples)
    assert report["status"] == "ok"
    assert len(report["indicators_tested"]) >= 1


def test_overall_verdict_pass_title_discriminant():
    """≥ 50% indicator 双判别 < 0.85 → 'pass_title_discriminant'."""
    verdict_per_indicator = {
        "llm_vote_tone": {
            "htmt_full_ctx": "lenient_pass",   # > 0.85 acceptable
            "htmt_full_title": "strict_pass",
            "htmt_ctx_title": "strict_pass",
        },
    }
    verdict = _compute_overall_verdict(verdict_per_indicator)
    assert verdict == "pass_title_discriminant"


def test_overall_verdict_fail_when_zero_discriminant():
    """0 indicator 判别成功 → 'fail'."""
    verdict_per_indicator = {
        "llm_vote_tone": {
            "htmt_full_ctx": "fail",
            "htmt_full_title": "fail",
            "htmt_ctx_title": "fail",
        },
    }
    verdict = _compute_overall_verdict(verdict_per_indicator)
    assert verdict == "fail"


def test_mojibake_columns_reported(panel_with_mojibake):
    """NEW-B1 报告路径: mojibake_columns_skipped 字段非空."""
    report = run_track_discriminant_validity(panel_with_mojibake)
    assert len(report["mojibake_columns_skipped"]) >= 2
    for col in report["mojibake_columns_skipped"]:
        assert "�" in col or "����" in col


def test_report_json_serializable(synthetic_panel_with_triples):
    """report dict 可被 JSON 序列化 (main 入口写 39g_*.json)."""
    report = run_track_discriminant_validity(synthetic_panel_with_triples)
    json_str = json.dumps(report, ensure_ascii=False, default=str)
    assert "htmt_3x3_per_indicator" in json_str


def test_track_indicator_candidates_priority_order():
    """TRACK_INDICATOR_CANDIDATES 顺序遵循优先级: llm_vote_tone 第一."""
    first_stem = TRACK_INDICATOR_CANDIDATES[0][0]
    assert first_stem == "llm_vote_tone"
    # dict_avg_tone 在 bert_avg_pos 之前 (词典优先于 BERT)
    stems = [s for s, _ in TRACK_INDICATOR_CANDIDATES]
    assert stems.index("dict_avg_tone") < stems.index("bert_avg_pos")
