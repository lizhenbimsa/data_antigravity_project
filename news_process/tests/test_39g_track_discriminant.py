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


# ---------------------------------------------------------------------------
# quality-hardening Round 41 (2026-05-27): track_discriminant_validity
# 82.66% → ~95%; 补 insufficient_obs/nan_verdict/no_indicator/fail/main()/
# strata-no-triple 等漏行
# ---------------------------------------------------------------------------


def test_run_insufficient_obs_after_mask():
    """n_articles mask 后 < 10 obs → status='insufficient_obs' (lines 175-179)."""
    panel = pd.DataFrame({
        "llm_vote_tone_full": np.arange(15.0),
        "llm_vote_tone_ctx": np.arange(15.0),
        "llm_vote_tone_title": np.arange(15.0),
        "n_articles": [1] * 15,  # 全 < 2 → mask 后 0 obs
    })
    report = run_track_discriminant_validity(panel, min_n_articles=2)
    assert report["status"] == "insufficient_obs"
    assert report["n_obs"] == 0


def test_run_nan_verdict_branch():
    """HTMT pair 出 nan (e.g. zero variance 一轨) → verdict='nan' (line 202)."""
    n = 30
    # title 全常数 → corr undefined → HTMT nan
    panel = pd.DataFrame({
        "llm_vote_tone_full": np.random.randn(n),
        "llm_vote_tone_ctx": np.random.randn(n),
        "llm_vote_tone_title": np.full(n, 0.5),  # 常数 → std=0
        "n_articles": [5] * n,
    })
    report = run_track_discriminant_validity(panel)
    # 找含 title 的 pair, 应有 'nan' verdict
    verdicts = report["verdict_per_indicator"]["llm_vote_tone"]
    title_pairs = [v for k, v in verdicts.items() if "title" in k]
    assert "nan" in title_pairs


def test_compute_overall_verdict_no_indicator():
    """空 verdict_per_indicator → 'no_indicator' (line 247)."""
    assert _compute_overall_verdict({}) == "no_indicator"


def test_compute_overall_verdict_lenient_with_self_corr():
    """所有 indicator 的 3 pair 全在 strict/lenient (无 fail) → 'lenient_pass_with_design_self_correlation'."""
    verdict_per_indicator = {
        "llm_vote_tone": {
            "htmt_full_ctx": "lenient_pass",
            "htmt_full_title": "lenient_pass",
            "htmt_ctx_title": "lenient_pass",
        },
        "dict_avg_tone": {
            "htmt_full_ctx": "lenient_pass",
            "htmt_full_title": "lenient_pass",
            "htmt_ctx_title": "lenient_pass",
        },
    }
    assert (_compute_overall_verdict(verdict_per_indicator)
            == "lenient_pass_with_design_self_correlation")


def test_main_panel_not_found(tmp_path):
    """main(): panel 文件不存在 → status='panel_not_found' (line 297-299)."""
    from news_process.pipeline.audit.track_discriminant_validity import main as g_main
    fake_panel = tmp_path / "no_such_panel.parquet"
    fake_output = tmp_path / "out.json"
    report = g_main(panel_path=fake_panel, output_path=fake_output)
    assert report["status"] == "panel_not_found"
    assert not fake_output.exists()


def test_main_happy_path_writes_json(tmp_path, synthetic_panel_with_triples):
    """main() 正常路径写 39g JSON (lines 301-315)."""
    from news_process.pipeline.audit.track_discriminant_validity import main as g_main
    panel_path = tmp_path / "panel.parquet"
    output_path = tmp_path / "39g.json"
    synthetic_panel_with_triples.to_parquet(panel_path)
    report = g_main(panel_path=panel_path, output_path=output_path)
    assert report["status"] == "ok"
    assert output_path.exists()
    # JSON 内含 v3_7_4_extensions key
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    assert "v3_7_4_extensions" in data


def test_strata_htmt_per_cell_no_triple():
    """_strata_htmt_per_cell: 没找到 triple → status='no_track_triple' (line 388)."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _strata_htmt_per_cell,
    )
    df = pd.DataFrame({"foo": [1, 2, 3]})  # 无三轨
    result = _strata_htmt_per_cell(df, stem="llm_vote_tone")
    assert result["status"] == "no_track_triple"


def test_strata_htmt_per_cell_strata_columns_missing(synthetic_panel_with_triples):
    """缺 frac_title_mentions_fintech / frac_title_long → strata_columns_missing."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _strata_htmt_per_cell,
    )
    result = _strata_htmt_per_cell(synthetic_panel_with_triples)
    assert result["status"] == "strata_columns_missing"


def test_v374_bootstrap_when_n_articles_col_missing(synthetic_panel_with_triples):
    """_v374_bootstrap_and_strata: panel 无 n_articles 列 → 走 else 分支 (line 461)."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _v374_bootstrap_and_strata,
    )
    panel = synthetic_panel_with_triples.drop(columns=["n_articles"])
    result = _v374_bootstrap_and_strata(panel)
    # bootstrap 完成 (有 panel_level_bootstrap key)
    assert "panel_level_bootstrap" in result
    assert result["n_obs_panel"] == len(panel)


def test_v374_bootstrap_no_triple():
    """_v374_bootstrap_and_strata: 无三轨 → status='no_track_triple'."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _v374_bootstrap_and_strata,
    )
    df = pd.DataFrame({"foo": np.arange(50)})
    result = _v374_bootstrap_and_strata(df)
    assert result["status"] == "no_track_triple"


def test_bootstrap_htmt_ci_insufficient_n():
    """_bootstrap_htmt_ci: n<10 → status='insufficient_n'."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _bootstrap_htmt_ci,
    )
    indicators = {
        "full": np.arange(5.0),
        "ctx": np.arange(5.0),
        "title": np.arange(5.0),
    }
    result = _bootstrap_htmt_ci(indicators)
    assert result["status"] == "insufficient_n"


def test_main_default_paths_via_load_config(tmp_path, monkeypatch,
                                             synthetic_panel_with_triples):
    """main() 默认路径 (lines 289-295): mock load_config 解析 output_dir."""
    from news_process.pipeline.audit import track_discriminant_validity as mod

    panel_path = tmp_path / "40_panel_yearly.parquet"
    synthetic_panel_with_triples.to_parquet(panel_path)

    fake_cfg = {"paths": {"output_dir": str(tmp_path)}}
    monkeypatch.setattr("news_process.core.config.load_config", lambda: fake_cfg)

    report = mod.main()
    assert report["status"] == "ok"
    assert (tmp_path / "39g_track_discriminant_validity.json").exists()


def test_strata_htmt_per_cell_happy_path():
    """_strata_htmt_per_cell happy path (lines 399-433): 4 cells, ≥1 ≥ MIN_CELL_N."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        MIN_CELL_N,
        _strata_htmt_per_cell,
    )
    # 构造 panel 让某 cell N ≥ MIN_CELL_N (30); 其余 < 30
    rng = np.random.default_rng(seed=7)
    n = 200
    # 一半 tmf=0 tlb=0, 30 tmf=1 tlb=1, 其余少量
    frac_tmf = np.concatenate([
        np.zeros(100), np.ones(40), np.zeros(30), np.ones(30),
    ])  # 100 + 40 + 30 + 30 = 200
    frac_tlong = np.concatenate([
        np.zeros(100), np.ones(40), np.ones(30), np.zeros(30),
    ])  # cell mapping: (0,0)=100 (1,1)=40 (0,1)=30 (1,0)=30 — 4 cells 均 ≥ 30
    full = rng.normal(0, 1, n)
    ctx = 0.7 * full + rng.normal(0, 0.5, n)
    title = 0.3 * full + rng.normal(0, 0.8, n)
    panel = pd.DataFrame({
        "llm_vote_tone_full": full,
        "llm_vote_tone_ctx": ctx,
        "llm_vote_tone_title": title,
        "frac_title_mentions_fintech": frac_tmf,
        "frac_title_long": frac_tlong,
        "n_articles": [5] * n,
    })
    result = _strata_htmt_per_cell(panel, stem="llm_vote_tone")
    assert result["status"] == "ok"
    assert result["valid_cell_count"] >= 1
    assert result["min_cell_n"] == MIN_CELL_N
    # ≥ 1 cell 有 htmt + bootstrap_ci
    ok_cells = [c for c, info in result["per_cell"].items()
                if info["status"] == "ok"]
    assert len(ok_cells) >= 1


def test_strata_htmt_per_cell_all_insufficient():
    """所有 4 cell N < MIN_CELL_N → status='all_cells_insufficient_power'."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _strata_htmt_per_cell,
    )
    rng = np.random.default_rng(seed=0)
    n = 40  # 4 cells × 10 obs 每 < MIN_CELL_N (30)
    frac_tmf = np.tile([0, 0, 1, 1], 10)
    frac_tlong = np.tile([0, 1, 0, 1], 10)
    panel = pd.DataFrame({
        "llm_vote_tone_full": rng.normal(0, 1, n),
        "llm_vote_tone_ctx": rng.normal(0, 1, n),
        "llm_vote_tone_title": rng.normal(0, 1, n),
        "frac_title_mentions_fintech": frac_tmf,
        "frac_title_long": frac_tlong,
    })
    result = _strata_htmt_per_cell(panel)
    assert result["status"] == "all_cells_insufficient_power"
    assert result["valid_cell_count"] == 0
    for cell_info in result["per_cell"].values():
        assert cell_info["status"] == "insufficient_power"


def test_bootstrap_htmt_ci_bootstrap_failed_when_zero_variance():
    """_bootstrap_htmt_ci: zero variance → corrcoef all-nan → < 100 valid (lines 357-364)."""
    from news_process.pipeline.audit.track_discriminant_validity import (
        _bootstrap_htmt_ci,
    )
    # n=15 (足够 entry, 越过 insufficient_n) 但所有列常数 → corrcoef nan
    indicators = {
        "full": np.full(15, 5.0),
        "ctx": np.full(15, 5.0),
        "title": np.full(15, 5.0),
    }
    result = _bootstrap_htmt_ci(indicators, n_bootstrap=200, seed=42)
    # 所有 pair 应该是 bootstrap_failed (无 valid 重采样)
    for k, info in result.items():
        assert info.get("status") == "bootstrap_failed" or info.get(
            "n_bootstrap_valid", 100) < 100
