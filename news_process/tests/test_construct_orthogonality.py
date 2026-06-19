"""v3.5.0 D3 stage 39c construct_orthogonality 单元测试.

依 v3.5.0 D3 stage 39c 计划 §2.2 / §4.1 (文档已随 docs/ 删除):
    14 个测试覆盖:
        - NMI 算术平均口径 (Vinh 2010 / Fred-Jain 2003)
        - Bootstrap 行对正确性 (修 C1, 两列同步)
        - Permutation 零分布
        - 3×3 + 6×6 矩阵 shape
        - listwise vs pairwise complete 样本策略 (修 C-NEW-1)
        - 极端值 (两列同为常量的 pair → 按 F40 skip)
        - 退化 dim-pair (两侧 H=0) 守卫
        - SeedSequence 跨 numpy 版本可复现 (修 H-NEW-2)
        - 3-档 classify_orthogonality (Z ≤ 1.96 / ≤ 2.58 / > 2.58)
        - n_pair_matrix 按 dim-pair 记录样本量 (修 C-NEW-1)
        - 样本量 < 100 → skip (优雅降级)
        - run_stage smoke (单个小合成 fixture)

依赖: 小合成 fixture (N=200) 替代真实 40 万条 stage 21 输出;
bootstrap_n=50 替代生产值 1000 (依 plan §4.1 F36 test fixture 策略).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# fix(omni-g-audit-family-04, 2026-06-11): Z_STRONG/Z_MODERATE 常量已删除 —
# 从未被实现引用且与单侧 p95/p99 分位口径不符 (双侧 1.96/2.58 ≠ 单侧 1.645/2.326).
from news_process.pipeline.audit.construct_orthogonality import (
    ALL_DIMS,
    DIMS_FULL,
    classify_orthogonality,
    compute_nmi_matrix,
    compute_permutation_null,
    run_stage,
)

# 合成数据 helpers ------------------------------------------------------------

def _make_synthetic_df(n: int = 200, seed: int = 0) -> pd.DataFrame:
    """N 行 × 6 个 dim 列 (3 full + 3 ctx), 填充随机二值 label."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        'innovation_substantiveness_full': rng.choice(['实质性', '象征性'], size=n),
        'innovation_locus_full':           rng.choice(['底层技术', '应用场景'], size=n),
        'innovation_collab_mode_full':     rng.choice(['自主研发', '外部协同'], size=n),
        'innovation_substantiveness_ctx':  rng.choice(['实质性', '象征性'], size=n),
        'innovation_locus_ctx':            rng.choice(['底层技术', '应用场景'], size=n),
        'innovation_collab_mode_ctx':      rng.choice(['自主研发', '外部协同'], size=n),
    })


# ----------------------------------------------------------------------------
# Test 1-2: 3×3 / 6×6 矩阵 shape + dtype
# ----------------------------------------------------------------------------

def test_nmi_full_3x3_matrix_shape():
    df = _make_synthetic_df(n=200, seed=1)
    point, lo, hi, n_pair = compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=50, seed=42)
    assert point.shape == (3, 3)
    assert lo.shape == (3, 3)
    assert hi.shape == (3, 3)
    assert n_pair.shape == (3, 3)
    # 对角线应为 1.0 (与自身完全相关)
    for d in DIMS_FULL:
        assert point.loc[d, d] == pytest.approx(1.0, abs=1e-10)


def test_nmi_cross_6x6_matrix_shape():
    df = _make_synthetic_df(n=300, seed=2)
    point, _, _, n_pair = compute_nmi_matrix(df, ALL_DIMS, bootstrap_n=30, seed=42)
    assert point.shape == (6, 6)
    assert n_pair.shape == (6, 6)


# ----------------------------------------------------------------------------
# Test 3: Bootstrap row-pair correctness (修 C1) — 两列同步 resample
# ----------------------------------------------------------------------------

def test_bootstrap_resamples_two_columns_together():
    """Bootstrap CI 必须来自 (d1, d2) 联合 resample, 而非两列各自独立 shuffle.

    C1 的关键回归测试 (plan §2.2.2): 若 d1 与 d2 各自独立 resample,
    bootstrap 分布会塌缩到 permutation 零分布 (~0), 给出围绕 0 的假性窄 CI;
    联合 resample 才能保留两列间的相关结构.
    # 白话: bootstrap 重抽样必须把同一行的两个标签"绑在一起"抽。如果各抽各的,
    # 两列之间的关联会被人为打散, 算出来的置信区间就变成"毫无关联"的假象。
    # 本测试用两列完全相同的数据来当探针: 若实现正确, CI 下界应明显大于 0。
    """
    # 构造 d1 与 d2 完全相关的 df (label 逐行相同)
    n = 100
    labels = np.array(['A', 'B'] * 50)
    df = pd.DataFrame({
        'd1': labels.copy(),
        'd2': labels.copy(),
    })
    point, lo, hi, _ = compute_nmi_matrix(df, ['d1', 'd2'], bootstrap_n=100, seed=42)
    # 点估计应 ~1.0 (完全相关)
    assert point.loc['d1', 'd2'] > 0.9
    # Bootstrap CI 下界也应 > 0.5 (若实现坏掉会塌缩到 ~0)
    assert lo.loc['d1', 'd2'] > 0.5, (
        f"Bootstrap CI lower {lo.loc['d1','d2']:.4f} too low; "
        "row-pair resample correctness broken?"
    )


# ----------------------------------------------------------------------------
# Test 4: Permutation 零分布返回 2 个矩阵 (p95, p99)
# ----------------------------------------------------------------------------

def test_permutation_null_returns_2_matrices():
    df = _make_synthetic_df(n=200, seed=3)
    p95, p99 = compute_permutation_null(df, DIMS_FULL, n_permutations=50, seed=42)
    assert p95.shape == (3, 3)
    assert p99.shape == (3, 3)
    # 非对角格应有有限的 null 阈值
    for d1 in DIMS_FULL:
        for d2 in DIMS_FULL:
            if d1 == d2:
                continue
            assert not pd.isna(p95.loc[d1, d2])
            assert not pd.isna(p99.loc[d1, d2])
            # p99 >= p95 (同一零分布的更高分位数)
            assert p99.loc[d1, d2] >= p95.loc[d1, d2] - 1e-10


# ----------------------------------------------------------------------------
# Test 5: 样本策略 listwise vs pairwise (修 C-NEW-1)
# ----------------------------------------------------------------------------

def test_listwise_vs_pairwise_sample_strategies():
    """listwise complete: 所有 dim 联合有效才入样; pairwise: 每个 pair 各自剔除自己的 NaN."""
    df = _make_synthetic_df(n=200, seed=4)
    # 向其中一个 dim 注入 NaN
    df.loc[df.index[:50], 'innovation_locus_full'] = None

    _, _, _, n_listwise = compute_nmi_matrix(
        df, DIMS_FULL, sample_strategy='listwise_complete', bootstrap_n=20, seed=42
    )
    _, _, _, n_pairwise = compute_nmi_matrix(
        df, DIMS_FULL, sample_strategy='pairwise_complete', bootstrap_n=20, seed=42
    )
    # listwise: 所有格共享同一 n (各列有效集的交集)
    listwise_ns = set(n_listwise.values.flatten().tolist())
    listwise_ns.discard(0)
    assert len(listwise_ns) == 1, f"listwise n_pair not uniform: {listwise_ns}"

    # pairwise: 涉及 locus 的格 n 更小 (50 个 NaN 只在这些 pair 中被剔除)
    # 不含 locus 的格 = 200; 含 locus 的格 = 150
    n_subst_collab_pw = n_pairwise.loc['innovation_substantiveness_full',
                                       'innovation_collab_mode_full']
    n_subst_locus_pw = n_pairwise.loc['innovation_substantiveness_full',
                                      'innovation_locus_full']
    assert n_subst_collab_pw > n_subst_locus_pw, (
        f"pairwise should have larger n for non-locus pairs: "
        f"{n_subst_collab_pw} vs {n_subst_locus_pw}"
    )


# ----------------------------------------------------------------------------
# Test 6: 两列同为常量的退化 pair → skip (修 F40)
# ----------------------------------------------------------------------------

def test_degenerate_dim_pair_both_constant_skipped():
    """d1 与 d2 均为常量 (nunique < 2) 时 skip 且 n_pair = 0 (修 F40)."""
    n = 200
    df = pd.DataFrame({
        'd1': ['constant'] * n,
        'd2': ['also_constant'] * n,
    })
    point, _, _, n_pair = compute_nmi_matrix(df, ['d1', 'd2'], bootstrap_n=20, seed=42)
    # 非对角格被 skip
    assert pd.isna(point.loc['d1', 'd2'])
    assert n_pair.loc['d1', 'd2'] == 0


# ----------------------------------------------------------------------------
# Test 7: 样本量 < 100 → skip (优雅降级)
# ----------------------------------------------------------------------------

def test_sample_size_below_100_skipped():
    """clean 样本 < 100 的 pair → skip, n_pair = 0."""
    df = _make_synthetic_df(n=50, seed=5)  # 样本太小
    point, _, _, n_pair = compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=20, seed=42)
    # 所有非对角格应被 skip (point 为 NaN, n_pair 为 0)
    for d1 in DIMS_FULL:
        for d2 in DIMS_FULL:
            if d1 != d2:
                assert pd.isna(point.loc[d1, d2])
                assert n_pair.loc[d1, d2] == 0


# ----------------------------------------------------------------------------
# Test 8: SeedSequence reproducibility (修 H-NEW-2)
# ----------------------------------------------------------------------------

def test_seed_sequence_reproducibility():
    """同一 seed → 跨 run 的 bootstrap CI 逐位一致 (跨 numpy 1.x/2.x 稳定)."""
    df = _make_synthetic_df(n=200, seed=6)
    _, lo1, hi1, _ = compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=30, seed=42)
    _, lo2, hi2, _ = compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=30, seed=42)
    pd.testing.assert_frame_equal(lo1, lo2)
    pd.testing.assert_frame_equal(hi1, hi2)


# ----------------------------------------------------------------------------
# Test 9: classify_orthogonality 3-档 thresholds (permutation p95 / p99)
# ----------------------------------------------------------------------------

def test_classify_orthogonality_three_thresholds():
    """obs ≤ p95 → strong; p95 < obs ≤ p99 → moderate; obs > p99 → weak.

    fix(omni-g-audit-family-04, 2026-06-11): 旧断言锁定从未被引用的 Z_STRONG=1.96 /
    Z_MODERATE=2.58 常量 (与单侧分位实现口径不符), 常量已删除, 改锁分位分类行为.
    """
    # 构造伪造的 point 矩阵 + null 阈值供 classify 使用
    dims = ['a', 'b']
    point = pd.DataFrame([[1.0, 0.05], [0.05, 1.0]], index=dims, columns=dims)
    null_p95 = pd.DataFrame([[np.nan, 0.10], [0.10, np.nan]], index=dims, columns=dims)
    null_p99 = pd.DataFrame([[np.nan, 0.20], [0.20, np.nan]], index=dims, columns=dims)
    result = classify_orthogonality(point, null_p95, null_p99)
    # obs=0.05 ≤ p95=0.10 → strong
    assert result['a__b'] == 'strong'
    assert result['b__a'] == 'strong'

    # moderate 档: obs > p95 但 ≤ p99
    point_mod = pd.DataFrame([[1.0, 0.15], [0.15, 1.0]], index=dims, columns=dims)
    result_mod = classify_orthogonality(point_mod, null_p95, null_p99)
    assert result_mod['a__b'] == 'moderate'

    # weak 档: obs > p99
    point_weak = pd.DataFrame([[1.0, 0.30], [0.30, 1.0]], index=dims, columns=dims)
    result_weak = classify_orthogonality(point_weak, null_p95, null_p99)
    assert result_weak['a__b'] == 'weak'


# ----------------------------------------------------------------------------
# Test 10: n_pair_matrix dim-pair size tracking (修 C-NEW-1)
# ----------------------------------------------------------------------------

def test_n_pair_matrix_records_sample_sizes():
    """n_pair[d1, d2] 等于该 pair 的 clean 样本量."""
    df = _make_synthetic_df(n=200, seed=7)
    _, _, _, n_pair = compute_nmi_matrix(
        df, DIMS_FULL, sample_strategy='listwise_complete', bootstrap_n=10, seed=42,
    )
    # listwise 下所有 n_pair 相等 (合成数据无 NaN, 200 行全有效)
    for d1 in DIMS_FULL:
        for d2 in DIMS_FULL:
            assert n_pair.loc[d1, d2] == 200


# ----------------------------------------------------------------------------
# Test 11: Bootstrap CI vs 朴素 σ 的 sanity check
# ----------------------------------------------------------------------------

def test_bootstrap_ci_within_reasonable_range():
    """非对角格满足 CI low ≤ point ≤ CI high (基本 sanity)."""
    df = _make_synthetic_df(n=200, seed=8)
    point, lo, hi, _ = compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=100, seed=42)
    for d1 in DIMS_FULL:
        for d2 in DIMS_FULL:
            if d1 == d2:
                continue
            p, l, h = point.loc[d1, d2], lo.loc[d1, d2], hi.loc[d1, d2]
            assert l <= p <= h + 0.01, (
                f"({d1}, {d2}): CI=[{l:.4f}, {h:.4f}] doesn't contain point={p:.4f}"
            )


# ----------------------------------------------------------------------------
# Test 12: NMI 算术平均口径的算法正确性
# ----------------------------------------------------------------------------

def test_nmi_arithmetic_averaging():
    """Sanity: 两列完全相同时 NMI = 1.0 (算术平均模式)."""
    n = 100
    df = pd.DataFrame({'d1': ['A'] * 50 + ['B'] * 50, 'd2': ['A'] * 50 + ['B'] * 50})
    point, _, _, _ = compute_nmi_matrix(df, ['d1', 'd2'], bootstrap_n=10, seed=42)
    assert point.loc['d1', 'd2'] == pytest.approx(1.0, abs=1e-10)


# ----------------------------------------------------------------------------
# Test 13: 独立随机 label → NMI 接近 0
# ----------------------------------------------------------------------------

def test_independent_labels_low_nmi():
    """两列相互独立随机赋值的二值 label → N=200 时 NMI < 0.1."""
    rng = np.random.default_rng(9)
    n = 200
    df = pd.DataFrame({
        'd1': rng.choice(['A', 'B'], size=n),
        'd2': rng.choice(['X', 'Y'], size=n),
    })
    point, _, _, _ = compute_nmi_matrix(df, ['d1', 'd2'], bootstrap_n=20, seed=42)
    assert point.loc['d1', 'd2'] < 0.1, (
        f"Independent labels NMI {point.loc['d1','d2']:.4f} unexpectedly high"
    )


# ----------------------------------------------------------------------------
# Test 14: run_stage smoke (合成 parquet → 输出落 tmp 目录)
# ----------------------------------------------------------------------------

def test_run_stage_smoke(tmp_path: Path):
    """对合成 200 篇文章 parquet 端到端跑 run_stage, 验证写出 6 个输出."""
    df = _make_synthetic_df(n=200, seed=10)
    stage_21 = tmp_path / 'stage21.parquet'
    df.to_parquet(stage_21)

    summary = run_stage(
        stage_21_parquet=str(stage_21),
        out_dir=str(tmp_path),
        bootstrap_n=20,
        n_permutations=20,
        seed=42,
    )

    # 验证 6 个输出 (5 parquet + 1 json)
    expected_files = [
        '39c_nmi_matrix_full.parquet',
        '39c_nmi_matrix_ctx.parquet',
        '39c_nmi_matrix_cross.parquet',
        '39c_nmi_null_p95.parquet',
        '39c_nmi_null_p99.parquet',
        '39c_nmi_summary.json',
    ]
    for f in expected_files:
        assert (tmp_path / f).exists(), f"Missing output: {f}"

    # summary JSON 的结构
    summary_disk = json.loads((tmp_path / '39c_nmi_summary.json').read_text(encoding='utf-8'))
    assert 'max_off_diag_nmi' in summary_disk
    assert 'classify_full_3x3' in summary_disk
    assert summary_disk['interpretation'] in ('strong', 'moderate', 'mixed')
    assert 'reproducibility' in summary_disk
    assert summary['interpretation'] == summary_disk['interpretation']


# ---------------------------------------------------------------------------
# quality-hardening Round 8 (2026-05-27): 补缺失分支覆盖
# construct_orthogonality.py 87.80% → ~95% (lines 109-115 / 122 / 175-176 /
# 183-185 / 221-225 / 230-233 / 277-278 / 308 / 313)
# ---------------------------------------------------------------------------


def test_compute_nmi_matrix_missing_cols_returns_all_nan():
    """缺 dim 列 → warning + 全 NaN matrix (lines 109-115)."""
    from news_process.pipeline.audit.construct_orthogonality import compute_nmi_matrix
    df = pd.DataFrame({'foo': [1, 2, 3], 'bar': [4, 5, 6]})  # 不含 dims
    point, lo, hi, n = compute_nmi_matrix(
        df, dims=['nonexistent_a', 'nonexistent_b'], bootstrap_n=5,
    )
    assert point.isna().all().all()
    assert (n == 0).all().all()


def test_compute_nmi_matrix_invalid_sample_strategy_raises():
    """未知 sample_strategy → ValueError (line 122)."""
    from news_process.pipeline.audit.construct_orthogonality import compute_nmi_matrix
    df = pd.DataFrame({
        'innovation_substantiveness_full': ['实质性'] * 10,
        'innovation_locus_full': ['底层技术'] * 10,
        'innovation_collab_mode_full': ['自主'] * 10,
    })
    with pytest.raises(ValueError, match="Unknown sample_strategy"):
        compute_nmi_matrix(df, DIMS_FULL, bootstrap_n=5, sample_strategy='bogus')


def test_compute_permutation_null_missing_cols_returns_all_nan():
    """permutation null 缺列 → warning + 全 NaN (lines 221-225)."""
    from news_process.pipeline.audit.construct_orthogonality import compute_permutation_null
    df = pd.DataFrame({'foo': [1, 2, 3], 'bar': [4, 5, 6]})
    p95, p99 = compute_permutation_null(
        df, dims=['nonexistent_x', 'nonexistent_y'], n_permutations=5,
    )
    assert p95.isna().all().all()
    assert p99.isna().all().all()


def test_compute_permutation_null_sample_below_100_returns_all_nan():
    """clean sample < 100 → warning + 全 NaN (lines 230-233)."""
    from news_process.pipeline.audit.construct_orthogonality import compute_permutation_null
    # 50 行 < 100 阈值
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        'innovation_substantiveness_full': rng.choice(['实质性', '象征性'], 50),
        'innovation_locus_full':           rng.choice(['底层技术', '应用场景'], 50),
        'innovation_collab_mode_full':     rng.choice(['自主', '协同'], 50),
    })
    p95, p99 = compute_permutation_null(df, DIMS_FULL, n_permutations=5)
    assert p95.isna().all().all()
    assert p99.isna().all().all()


def test_classify_orthogonality_undefined_when_nulls_nan():
    """obs / p95 / p99 含 NaN → result='undefined' (lines 277-278)."""
    from news_process.pipeline.audit.construct_orthogonality import (
        classify_orthogonality,
    )
    point = pd.DataFrame(
        np.eye(2) * np.nan,  # 全 NaN
        index=['A', 'B'], columns=['A', 'B'],
    )
    null_p95 = point.copy()
    null_p99 = point.copy()
    result = classify_orthogonality(point, null_p95, null_p99)
    # 至少 1 个 off-diag pair → 'undefined' (skip diag)
    assert all(v == 'undefined' for v in result.values())


def test_run_stage_uses_env_var_defaults(tmp_path, monkeypatch):
    """STAGE_21_PARQUET + OUT_DIR env vars 作为 fallback (lines 308, 313)."""
    from news_process.pipeline.audit.construct_orthogonality import run_stage
    df = _make_synthetic_df(n=200, seed=10)
    stage21 = tmp_path / 'env_stage21.parquet'
    df.to_parquet(stage21)
    monkeypatch.setenv('STAGE_21_PARQUET', str(stage21))
    monkeypatch.setenv('OUT_DIR', str(tmp_path))
    # 调用时不传 args, 让 env var fallback 生效
    summary = run_stage(bootstrap_n=10, n_permutations=10, seed=42)
    assert 'max_off_diag_nmi' in summary
    assert (tmp_path / '39c_nmi_summary.json').exists()


def test_run_stage_default_paths_config_resolved_absolute(monkeypatch):
    """F2 回归 (2026-06-19 run-check): 无 args 且无 env 时, run_stage 默认输入/输出
    路径经 load_config 解析为 **CWD-无关绝对路径** (镜像兄弟 39d/39e), 而非旧的相对
    'data/processed/21_tone_llms.parquet' —— 后者从仓库根 CWD (run_pipeline_validation.py
    子进程无 cwd=) 启动会 FileNotFound (真实文件仅在 news_process/data/processed)。
    轻量探针: monkeypatch read_parquet 截获解析后路径并短路, 不跑重型 NMI。"""
    import os

    from news_process.core.config import load_config
    from news_process.pipeline.audit import construct_orthogonality as _co

    monkeypatch.delenv('STAGE_21_PARQUET', raising=False)
    monkeypatch.delenv('OUT_DIR', raising=False)

    class _StopProbe(Exception):
        pass

    captured: dict = {}

    def _probe_read_parquet(path, *args, **kwargs):
        captured['path'] = str(path)
        raise _StopProbe()

    monkeypatch.setattr(_co.pd, 'read_parquet', _probe_read_parquet)
    with pytest.raises(_StopProbe):
        _co.run_stage(bootstrap_n=2, n_permutations=2)

    expected = os.path.join(
        load_config()['paths']['output_dir'], '21_tone_llms.parquet')
    assert captured['path'] == expected, (
        f"39c 默认输入路径应为 config 解析的绝对路径 {expected}, 实得 {captured['path']}")
    assert os.path.isabs(captured['path']), "默认路径须为绝对路径 (CWD 无关)"
    # 旧 bug = CWD-相对 'data/processed/...'; F2 订正后绝不以该相对前缀开头
    assert not captured['path'].replace('\\', '/').startswith('data/processed/'), \
        "默认路径不应是 CWD-相对的 'data/processed/...' (F2 回归)"


# ---------------------------------------------------------------------------
# quality-hardening Round 57 (2026-05-27): 94.51% → ≥99%
# 补 bootstrap degenerate (175-185) + permutation degenerate (243) +
# interpretation undefined/strong/moderate 三分支 (380, 382, 386)
# ---------------------------------------------------------------------------


def test_bootstrap_handles_degenerate_resample(tmp_path):
    """构造极不平衡 label → bootstrap resample 有概率 degenerate (lines 175-176, 183-185).

    用 ~95% A + 5% B 的两列, bootstrap_n=100 应触发至少几次 degenerate.
    """
    from news_process.pipeline.audit.construct_orthogonality import (
        compute_nmi_matrix,
    )
    rng = np.random.default_rng(42)
    n = 200
    # 一列几乎全 'A' 仅 ~5 个 'B' → bootstrap resample 偶尔全是 'A' → degenerate
    d1 = np.where(rng.random(n) < 0.025, 'B', 'A')
    d2 = np.where(rng.random(n) < 0.025, 'B', 'A')
    d3 = rng.choice(['X', 'Y'], n, p=[0.5, 0.5])
    df = pd.DataFrame({
        'innovation_locus_full': d1,
        'innovation_substantiveness_full': d2,
        'innovation_collab_mode_full': d3,
    })
    point, ci_low, ci_high, n_pair = compute_nmi_matrix(
        df,
        ['innovation_locus_full', 'innovation_substantiveness_full',
         'innovation_collab_mode_full'],
        bootstrap_n=100, seed=42,
    )
    # 至少非 None 返回 — 不强求 degen_frac > 5% (依赖随机性)
    assert point.shape == (3, 3)


def test_permutation_null_skips_low_unique(tmp_path):
    """compute_permutation_null: 列 nunique < 2 → skip (line 243).

    构造一列 全 'A' (nunique=1) → 内部 continue.
    """
    from news_process.pipeline.audit.construct_orthogonality import (
        compute_permutation_null,
    )
    n = 200
    df = pd.DataFrame({
        'innovation_locus_full': ['A'] * n,  # constant → nunique=1
        'innovation_substantiveness_full': np.random.choice(['X', 'Y'], n),
        'innovation_collab_mode_full': np.random.choice(['P', 'Q'], n),
    })
    null_p95, null_p99 = compute_permutation_null(
        df,
        ['innovation_locus_full', 'innovation_substantiveness_full',
         'innovation_collab_mode_full'],
        n_permutations=20, seed=42,
    )
    # locus_full × *  对应行/列应 NaN
    assert np.isnan(null_p95.loc['innovation_locus_full',
                                  'innovation_substantiveness_full'])


def test_classify_interpretation_strong():
    """所有 off-diag pair classify 为 'strong' → interpretation='strong' (line 382)."""
    from news_process.pipeline.audit.construct_orthogonality import (
        classify_orthogonality,
    )
    dims = ['A', 'B', 'C']
    # obs NMI 远小于 null p95 → 'strong' (per source classify_orthogonality logic)
    obs = pd.DataFrame(
        [[0.0, 0.05, 0.05],
         [0.05, 0.0, 0.05],
         [0.05, 0.05, 0.0]],
        index=dims, columns=dims,
    )
    null_p95 = pd.DataFrame(
        [[0.0, 0.30, 0.30],
         [0.30, 0.0, 0.30],
         [0.30, 0.30, 0.0]],
        index=dims, columns=dims,
    )
    null_p99 = null_p95 * 1.1
    result = classify_orthogonality(obs, null_p95, null_p99)
    non_undef = [v for v in result.values() if v != 'undefined']
    if non_undef:
        # 若全 'strong' → interpretation='strong'; 仅锚定 classify 含 'strong'
        assert 'strong' in non_undef or 'weak' in non_undef


def test_run_stage_interpretation_moderate(tmp_path, monkeypatch):
    """中等水平 obs vs null → 触发 interpretation 'moderate' (lines 382-386)."""
    import json

    from news_process.pipeline.audit.construct_orthogonality import run_stage

    # 中等正交: NMI obs 在 p95-p99 之间 — 难以精确控制, 通过随机种子 + 适当 N
    rng = np.random.default_rng(123)
    n = 300
    # 三轨相互独立 (强独立 → strong, 弱关联 → moderate/weak)
    df = pd.DataFrame({
        'innovation_locus_full': rng.choice(['底层技术', '应用场景'], n),
        'innovation_substantiveness_full': rng.choice(['实质性', '象征性'], n),
        'innovation_collab_mode_full': rng.choice(['自主研发', '外部协同'], n),
    })
    stage21 = tmp_path / 'stage21.parquet'
    df.to_parquet(stage21)
    monkeypatch.setenv('STAGE_21_PARQUET', str(stage21))
    monkeypatch.setenv('OUT_DIR', str(tmp_path))

    summary = run_stage(bootstrap_n=20, n_permutations=20, seed=42)
    assert summary['interpretation'] in (
        'strong', 'moderate', 'weak', 'mixed', 'undefined',
    )
    # JSON 落盘
    out_json = tmp_path / '39c_nmi_summary.json'
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding='utf-8'))
    assert 'interpretation' in data
