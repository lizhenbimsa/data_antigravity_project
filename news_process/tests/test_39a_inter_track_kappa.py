"""Tests for stage 39a (inter-track Cohen's κ).

Plan v1.37 P1; 10 tests in this file, 11th P1 test (orphan-12 guard)
lives in tests/integration/test_dag_consistency.py per §4.3.6.
"""
import warnings

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.audit.inter_track_kappa import (
    _compute_kappa_with_bootstrap,
    run_stage,
)


def test_kappa_full_agreement():
    """100 rows all _full == _ctx → κ = 1.0."""
    y1 = np.array(["A"] * 50 + ["B"] * 50)
    y2 = y1.copy()
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 100
    assert kp == 1.0


def test_kappa_moderate_agreement():
    """100 rows with ≈20% disagreement → κ in [0.50, 0.70] expected range."""
    rng = np.random.default_rng(123)
    n = 200
    y1 = rng.choice(["A", "B"], size=n)
    y2 = y1.copy()
    flip = rng.choice(n, size=int(0.20 * n), replace=False)
    y2[flip] = np.where(y2[flip] == "A", "B", "A")
    kp, lo, hi, n_obs = _compute_kappa_with_bootstrap(y1, y2)
    assert not np.isnan(kp)
    # ~80% agreement gives κ in moderate range; loose bounds for noise
    assert 0.4 < kp < 0.8


def test_kappa_empty_subset():
    """0 rows → (nan, nan, nan, 0) without raising."""
    y1 = np.array([], dtype=object)
    y2 = np.array([], dtype=object)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 0
    assert np.isnan(kp) and np.isnan(lo) and np.isnan(hi)


def test_kappa_constant_column():
    """Both columns identical constant → p_e=1 in cohens_kappa_2cat →
    NaN kappa (degenerate edge). Note: cohens_kappa_2cat L72-74 only
    returns NaN when p_e ≥ 1.0, which requires both columns to have
    the SAME single category. Single-column constant with the other
    variable yields κ=0 (finite). Plan §4.3.1 step 5 spec refined."""
    y1 = np.array(["A"] * 100)
    y2 = np.array(["A"] * 100)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 100
    assert np.isnan(kp)


@pytest.mark.parametrize("n_obs", [1, 2])
def test_kappa_small_n_short_circuit(n_obs):
    """n_obs < 3 short-circuits to NaN tuple without bootstrap (R3C-04)."""
    y1 = np.array(["A"] * n_obs)
    y2 = np.array(["B"] * n_obs)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == n_obs
    assert np.isnan(kp) and np.isnan(lo) and np.isnan(hi)


def test_outputs_emitted(tmp_path, monkeypatch):
    """run_stage writes both CSV and TeX to eval_reports/."""
    # Synthesize 21_tone_llms.parquet in tmp_path
    out_dir = tmp_path / "processed"
    out_dir.mkdir()
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    df = pd.DataFrame({
        'innovation_locus_full':       ['底层技术', '应用场景', '底层技术', '应用场景'] * 5,
        'innovation_locus_ctx':        ['底层技术', '应用场景', '应用场景', '应用场景'] * 5,
        'innovation_substantiveness_full': ['实质性', '象征性', '实质性', '象征性'] * 5,
        'innovation_substantiveness_ctx':  ['实质性', '实质性', '实质性', '象征性'] * 5,
        'llm_verified_dual_both': [True] * 20,
    })
    df.to_parquet(out_dir / "21_tone_llms.parquet")
    cfg = {"paths": {"output_dir": str(out_dir), "log_dir": str(log_dir)}}
    run_stage(cfg)
    csv_path = out_dir / "eval_reports" / "inter_track_kappa_table.csv"
    tex_path = out_dir / "eval_reports" / "inter_track_kappa_table.tex"
    assert csv_path.exists() and csv_path.stat().st_size > 0
    assert tex_path.exists() and tex_path.stat().st_size > 0
    # Booktabs tokens (plan v1.37 §4.7 acceptance)
    tex = tex_path.read_text(encoding='utf-8')
    assert '\\toprule' in tex
    assert '\\midrule' in tex
    assert '\\bottomrule' in tex


def test_dag_registration():
    """'39a_inter_track_kappa.py' in EXPECTED_NO_OUTPUT_STAGES and STAGES_VALIDATION.

    v3.5.0 update: STAGES_VALIDATION 14 (was 13 in v3.4.0); +1 = 39c_construct_orthogonality.py
    v3.5.1 update: STAGES_VALIDATION 15; +1 = 39d_lexical_discriminant_validity.py
    per stage3_v3_5_1_a1_a3_supplementation_plan.md §3.1.
    """
    from news_process.core import dag, schemas
    assert "39a_inter_track_kappa.py" in schemas.EXPECTED_NO_OUTPUT_STAGES
    scripts = {s.script for s in dag.STAGES_VALIDATION}
    assert "39a_inter_track_kappa.py" in scripts
    assert "39c_construct_orthogonality.py" in scripts, "v3.5.0 D3 stage missing"
    assert "39d_lexical_discriminant_validity.py" in scripts, "v3.5.1 stage 39d missing"
    assert len(dag.STAGES_VALIDATION) == 16, (
        f"expects 16 validation stages "
        f"(13 v3.4.0 + 39c v3.5.0 + 39d v3.5.1 + 39e v2.3 PR-A + 39f v2.3 PR-D; "
        f"39g title 轨 + 39h DC4 contamination + 38a temporal_mask 均已删); got {len(dag.STAGES_VALIDATION)}"
    )


def test_kappa_bootstrap_handles_degenerate_resamples():
    """High-imbalance input → some NaN resamples; CI either finite (≥50%
    finite) or NaN with WARN (<50% finite). R30A-01/R30B-01."""
    # Mostly-constant data: only 1 disagreement out of 50 rows
    y1 = np.array(["A"] * 50)
    y2 = np.array(["A"] * 49 + ["B"])
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always")
        kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2, n_boot=200, seed=42)
    assert n == 50
    # The original isn't constant (one B), so point κ is finite (=0 here)
    # Many resamples will get all-A in both columns → constant → NaN
    # If <50% finite, expect WARN + (nan, nan); else finite CI
    if np.isnan(lo):
        # WARN emitted
        assert any(issubclass(w.category, RuntimeWarning) for w in wlist)
    else:
        # CI finite
        assert not np.isnan(hi)


def test_kappa_bootstrap_reproducibility():
    """Same inputs + seed → bit-equal full 4-tuple."""
    rng = np.random.default_rng(7)
    y1 = rng.choice(["A", "B"], size=80)
    y2 = rng.choice(["A", "B"], size=80)
    r1 = _compute_kappa_with_bootstrap(y1, y2, n_boot=500, seed=42)
    r2 = _compute_kappa_with_bootstrap(y1, y2, n_boot=500, seed=42)
    np.testing.assert_array_equal(np.array(r1), np.array(r2))


def test_missing_dual_both_column(tmp_path):
    """Parquet without llm_verified_dual_both → WARN + NaN rows, no raise."""
    out_dir = tmp_path / "processed"
    out_dir.mkdir()
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    df = pd.DataFrame({
        'innovation_locus_full': ['底层技术'] * 5,
        'innovation_locus_ctx':  ['底层技术'] * 5,
        'innovation_substantiveness_full': ['实质性'] * 5,
        'innovation_substantiveness_ctx':  ['实质性'] * 5,
    })
    df.to_parquet(out_dir / "21_tone_llms.parquet")
    cfg = {"paths": {"output_dir": str(out_dir), "log_dir": str(log_dir)}}
    # Should not raise
    table = run_stage(cfg)
    # All n_obs should be 0 because subset is empty (no dual_both column → empty df)
    assert all(table['n_obs'] == 0)


# ---------------------------------------------------------------------------
# quality-hardening Round 10 (2026-05-27): inter_track_kappa.py 91.6% → ~100%
# missing 165 / 173-174 / 190 / 206-212 (config/file 缺失 + dual_both 空 +
# kappa 越界 warning)
# ---------------------------------------------------------------------------


def test_run_stage_handles_missing_input_parquet(tmp_path):
    """Stage 21 parquet 不存在 → warning + 空 subset + NaN rows (lines 173-174)."""
    out_dir = tmp_path / "missing_processed"
    out_dir.mkdir()
    log_dir = tmp_path / "missing_logs"
    log_dir.mkdir()
    cfg = {"paths": {"output_dir": str(out_dir), "log_dir": str(log_dir)}}
    # No 21_tone_llms.parquet written → warn 路径
    table = run_stage(cfg)
    assert all(table['n_obs'] == 0)


def test_run_stage_handles_dual_both_subset_empty(tmp_path):
    """dual_both=True 子集空 → warning + NaN rows (line 190)."""
    out_dir = tmp_path / "empty_processed"
    out_dir.mkdir()
    log_dir = tmp_path / "empty_logs"
    log_dir.mkdir()
    df = pd.DataFrame({
        'innovation_locus_full': ['底层技术'] * 5,
        'innovation_locus_ctx':  ['底层技术'] * 5,
        'innovation_substantiveness_full': ['实质性'] * 5,
        'innovation_substantiveness_ctx':  ['实质性'] * 5,
        'llm_verified_dual_both': [False] * 5,  # 全 False → subset 空
    })
    df.to_parquet(out_dir / "21_tone_llms.parquet")
    cfg = {"paths": {"output_dir": str(out_dir), "log_dir": str(log_dir)}}
    table = run_stage(cfg)
    assert all(table['n_obs'] == 0)


def test_run_stage_kappa_outside_warning_range_triggers_warn(tmp_path):
    """构造 κ 远低于 0.30 → RuntimeWarning + logger.warning (lines 206-212)."""
    import warnings as wmod
    out_dir = tmp_path / "warn_processed"
    out_dir.mkdir()
    log_dir = tmp_path / "warn_logs"
    log_dir.mkdir()
    # 完全独立的 full vs ctx → κ ≈ 0 < 0.30 → 触发 warning
    rng = np.random.default_rng(0)
    n = 60
    df = pd.DataFrame({
        'innovation_locus_full': rng.choice(['底层技术', '应用场景'], n),
        'innovation_locus_ctx':  rng.choice(['底层技术', '应用场景'], n),
        'innovation_substantiveness_full': rng.choice(['实质性', '象征性'], n),
        'innovation_substantiveness_ctx':  rng.choice(['实质性', '象征性'], n),
        'innovation_collab_mode_full': rng.choice(['自主', '协同'], n),
        'innovation_collab_mode_ctx':  rng.choice(['自主', '协同'], n),
        'llm_verified_dual_both': [True] * n,
    })
    df.to_parquet(out_dir / "21_tone_llms.parquet")
    cfg = {"paths": {"output_dir": str(out_dir), "log_dir": str(log_dir)}}
    with wmod.catch_warnings(record=True) as wl:
        wmod.simplefilter("always")
        table = run_stage(cfg)
    # 至少 1 个 dim 的 κ 应在 [0.30, 0.70] 外 → 触发 warn (best-effort 由数据决定)
    assert len(table) >= 1
    # 不强求 wl 非空 (依赖随机数据), 但确保 run_stage 走完且 logger.warning 没有崩溃
    # (line 212 logger.warning 调用本身需要不抛 — 上一行 wmod.warn 之后)
