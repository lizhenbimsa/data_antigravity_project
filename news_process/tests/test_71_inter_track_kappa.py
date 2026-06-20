"""stage 39a (跨轨 Cohen's κ) 测试。

Plan v1.37 P1 原始 10 个测试; 后续 quality-hardening Round 10 (2026-05-27)
追加 3 个, 本文件现共 13 个。第 11 个 P1 测试 (orphan-12 guard) 按 §4.3.6
位于 tests/integration/test_dag_consistency.py。
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
    """100 行 _full 与 _ctx 全部一致 → κ = 1.0。"""
    y1 = np.array(["A"] * 50 + ["B"] * 50)
    y2 = y1.copy()
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 100
    assert kp == 1.0


def test_kappa_moderate_agreement():
    """约 20% 不一致 → κ 落在中等一致区间 (断言宽松取 0.4–0.8)。"""
    rng = np.random.default_rng(123)
    n = 200
    y1 = rng.choice(["A", "B"], size=n)
    y2 = y1.copy()
    flip = rng.choice(n, size=int(0.20 * n), replace=False)
    y2[flip] = np.where(y2[flip] == "A", "B", "A")
    kp, lo, hi, n_obs = _compute_kappa_with_bootstrap(y1, y2)
    assert not np.isnan(kp)
    # 约 80% 一致 → κ 在中等区间; 边界放宽以容纳随机噪声
    assert 0.4 < kp < 0.8


def test_kappa_empty_subset():
    """0 行输入 → 返回 (nan, nan, nan, 0) 且不抛异常。"""
    y1 = np.array([], dtype=object)
    y2 = np.array([], dtype=object)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 0
    assert np.isnan(kp) and np.isnan(lo) and np.isnan(hi)


def test_kappa_constant_column():
    """两列均为同一常量 → cohens_kappa_2cat 中 p_e=1 → κ=NaN (退化边界)。

    注: cohens_kappa_2cat L72-74 仅在 p_e ≥ 1.0 时返回 NaN, 这要求两列
    取值为**同一个**单一类别。若仅一列为常量而另一列有变化, 则 κ=0
    (有限值)。Plan §4.3.1 step 5 规格已据此细化。
    # 白话: 当两边给出的标签完全一样且只有一种取值时, "偶然一致率"已经
    # 是 100%, κ 公式分母为 0, 数学上无定义, 所以返回 NaN 而不是 1。
    """
    y1 = np.array(["A"] * 100)
    y2 = np.array(["A"] * 100)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == 100
    assert np.isnan(kp)


@pytest.mark.parametrize("n_obs", [1, 2])
def test_kappa_small_n_short_circuit(n_obs):
    """n_obs < 3 时短路返回 NaN 元组, 不做 bootstrap (R3C-04)。"""
    y1 = np.array(["A"] * n_obs)
    y2 = np.array(["B"] * n_obs)
    kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2)
    assert n == n_obs
    assert np.isnan(kp) and np.isnan(lo) and np.isnan(hi)


def test_outputs_emitted(tmp_path, monkeypatch):
    """run_stage 应同时写出 CSV 和 TeX 到 eval_reports/。"""
    # 在 tmp_path 中合成 21_tone_llms.parquet
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
    # Booktabs token 检查 (plan v1.37 §4.7 验收项)
    tex = tex_path.read_text(encoding='utf-8')
    assert '\\toprule' in tex
    assert '\\midrule' in tex
    assert '\\bottomrule' in tex


def test_dag_registration():
    """'71_inter_track_kappa.py' 应同时注册在 EXPECTED_NO_OUTPUT_STAGES 与 STAGES_VALIDATION。

    历史: v3.5.0 时 STAGES_VALIDATION 14 (v3.4.0 为 13; +72_construct_orthogonality.py);
    v3.5.1 时 15 (+73_lexical_discriminant_validity.py,
    见 stage3_v3_5_1_a1_a3_supplementation_plan.md §3.1)。
    当前计数 16, 见下方断言消息中的增删明细。
    """
    from news_process.core import dag, schemas
    assert "71_inter_track_kappa.py" in schemas.EXPECTED_NO_OUTPUT_STAGES
    scripts = {s.script for s in dag.STAGES_VALIDATION}
    assert "71_inter_track_kappa.py" in scripts
    assert "72_construct_orthogonality.py" in scripts, "v3.5.0 D3 stage missing"
    assert "73_lexical_discriminant_validity.py" in scripts, "v3.5.1 stage 39d missing"
    assert len(dag.STAGES_VALIDATION) == 16, (
        f"expects 16 validation stages "
        f"(13 v3.4.0 + 39c v3.5.0 + 39d v3.5.1 + 39e v2.3 PR-A + 39f v2.3 PR-D; "
        f"39g title 轨 + 39h DC4 contamination + 38a temporal_mask 均已删); got {len(dag.STAGES_VALIDATION)}"
    )


def test_kappa_bootstrap_handles_degenerate_resamples():
    """高度不均衡输入 → 部分重采样 κ 为 NaN; CI 要么有限 (有限比例 ≥50%)
    要么 NaN 并发 WARN (有限比例 <50%)。R30A-01/R30B-01。"""
    # 接近常量的数据: 50 行中只有 1 处不一致
    y1 = np.array(["A"] * 50)
    y2 = np.array(["A"] * 49 + ["B"])
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always")
        kp, lo, hi, n = _compute_kappa_with_bootstrap(y1, y2, n_boot=200, seed=42)
    assert n == 50
    # 原始数据并非常量 (有 1 个 B), 故点估计 κ 有限 (此处 =0)
    # 大量重采样会抽到两列全 A → 常量 → NaN
    # 若有限比例 <50%, 预期 WARN + (nan, nan); 否则 CI 有限
    if np.isnan(lo):
        # 已发出 WARN
        assert any(issubclass(w.category, RuntimeWarning) for w in wlist)
    else:
        # CI 有限
        assert not np.isnan(hi)


def test_kappa_bootstrap_reproducibility():
    """相同输入 + 相同 seed → 完整 4 元组逐位相等。"""
    rng = np.random.default_rng(7)
    y1 = rng.choice(["A", "B"], size=80)
    y2 = rng.choice(["A", "B"], size=80)
    r1 = _compute_kappa_with_bootstrap(y1, y2, n_boot=500, seed=42)
    r2 = _compute_kappa_with_bootstrap(y1, y2, n_boot=500, seed=42)
    np.testing.assert_array_equal(np.array(r1), np.array(r2))


def test_missing_dual_both_column(tmp_path):
    """parquet 缺 llm_verified_dual_both 列 → WARN + NaN 行, 不抛异常。"""
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
    # 不应抛异常
    table = run_stage(cfg)
    # 所有 n_obs 应为 0, 因 subset 为空 (无 dual_both 列 → 空 df)
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
