"""news_process.pipeline.audit.construct_orthogonality — v3.5.0 D3 NMI 正交性测度.

Stage 39c: 在 article 层算 substantiveness × locus × collab_mode 三 construct 的
normalized mutual information (NMI) matrix + permutation null distribution,
作 paper Appendix A.2 "Construct Validity Evidence" 的实证证据.

学术锚点 (v3.5.0 D3):
    - Vinh, Epps & Bailey (2010 JMLR 11:2837-2854) NMI arithmetic averaging
    - Fred & Jain (2003 CVPR) NMI for clustering comparison
    - Bagozzi & Yi (1988 JAMS 16:74-94) discriminant validity in CFA

Dependency stability (修 F35):
    sklearn 1.5-1.8 已验证 `normalized_mutual_info_score(..., average_method='arithmetic')`.
    若升级到 sklearn 2.x 必须 (a) 跑全 14 单元测试; (b) 比对 v3.5.0 baseline parquet hash
    (允许 ≤ ±0.001 漂移 per H-NEW-1 LLM stochasticity); (c) breaking change 触发 epoch 7 audit.

Reproducibility lock (修 H-NEW-1):
    输入 = data/processed/21_tone_llms.parquet @ v3.4.0 commit hash 450c1aa7
    (per plan §0 Tag-over-hash anchor; 实际 anchor 由 v3.4.0-baseline-frozen git tag 决定).

Performance estimate (修 F3):
    bootstrap 1000 × matrix cells: full 3×3 ≈ 7 min / ctx 3×3 ≈ 7 min /
    cross 6×6 ≈ 30 min; permutation 1000 × 30 off-diagonal ≈ 25 min.
    Total wall-time ≈ 70 min single-thread (sklearn NMI ~100 ms / call on N≈400k).
    Recommended default for D4 day (修 F31): n_jobs=16 → ~5 min on 64-core MP machine.

Concurrency (修 F7 + F43):
    本函数 single-thread 设计; SeedSequence.spawn 已 pre-allocate seeds 故 parallel 友好.
    sklearn `normalized_mutual_info_score` 内部 sparse contingency table 构造在
    sklearn 1.5-1.8 **基于源码 review 判断单调用线程安全** (无 sklearn 官方文档明确 claim,
    谨慎说法). joblib `n_jobs > 1` 可加速但需用 `prefer='processes'` (避免 GIL);
    默认实现保持 single-thread. 若 production parallel 触发 race condition 异常,
    立即 fallback `n_jobs=1` + audit log §E.thread_race_event 记录.

Logging 约定 (修 F13):
    与 v3.4.0 main pipeline 一致, 通过 logger.info / logger.warning 输出.
    stage 内禁止 print() 直接输出; 诊断信号全部走 logger.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DIMS_FULL = [
    'innovation_substantiveness_full',
    'innovation_locus_full',
    'innovation_collab_mode_full',
]
DIMS_CTX = [d.replace('_full', '_ctx') for d in DIMS_FULL]
ALL_DIMS = DIMS_FULL + DIMS_CTX

# 分类阈值口径 (fix(omni-g-audit-family-04, 2026-06-11)): 实现为 permutation null
# 分布的**单侧** 95% / 99% 分位 (≈ 单侧 Z 1.645 / 2.326), 而非旧注释宣称的
# "pre-registered 双侧 Z 1.96 / 2.58" — 旧 Z_STRONG/Z_MODERATE 常量从未被任何
# 代码引用, 预注册口径与执行口径不符, 已删除; 权威口径见 classify_orthogonality.


def _lazy_import_nmi():
    """Defer sklearn import to function scope (CI light job loads only when stage runs)."""
    from sklearn.metrics import normalized_mutual_info_score
    return normalized_mutual_info_score


def compute_nmi_matrix(
    df: pd.DataFrame,
    dims: list[str],
    sample_strategy: str = 'listwise_complete',
    bootstrap_n: int = 1000,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute NMI matrix + bootstrap 95% CI + per-pair n.

    Returns:
        (nmi_point, ci_low, ci_high, n_pair_matrix) — all 4 DataFrames indexed/columned by dims.

    sample_strategy:
        'listwise_complete' — 全 dims 同时非脏的 row (修 C-NEW-1; recommended for matrix)
        'pairwise_complete' — 每 (d1, d2) 各自 dropna (legacy, sample size 不可比)

    Bootstrap implementation (修 C1 + H-NEW-2):
        - 在 sampled DataFrame 上整体 resample (两列同步 row, 修 C1)
        - 用 NumPy 2.x SeedSequence.spawn 替代 rng.integers (跨 NumPy 版本 reproducible, 修 H-NEW-2)

    Degenerate dim-pair (修 F40):
        若 d1 或 d2 在 clean sample 上 nunique() < 2 (constant), 跳过该 pair 并 logger.error;
        n_pair[i, j] = 0; 写入 audit log §A.degenerate_dim_pair.
    """
    nmi_score = _lazy_import_nmi()

    n = len(dims)
    point = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_low = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_high = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    n_pair = pd.DataFrame(np.zeros((n, n), dtype=int), index=dims, columns=dims)

    # F-56: Missing column guard (对称 encode_collab.compute_cell_id 防御).
    # Production stage 21 pre-v3.4.0 缺 collab_mode 列 → 之前直接 raise KeyError.
    # 现在 graceful: 缺列 → 返回全 NaN matrix + logger.warning, 让调用方判断.
    missing_cols = [d for d in dims if d not in df.columns]
    if missing_cols:
        logger.warning(
            f"  v3.5.0 D3 NMI: missing dim columns {missing_cols}; "
            f"returning all-NaN matrix. "
            "Production stage 21 may pre-date v3.4.0 (lacks innovation_collab_mode_*). "
            "解决方案: 重跑 stage 21 with prompt v8 (含 collab_mode 维度)."
        )
        return point, ci_low, ci_high, n_pair

    if sample_strategy == 'listwise_complete':
        clean_base = df[dims].dropna()
    elif sample_strategy == 'pairwise_complete':
        clean_base = None
    else:
        raise ValueError(f"Unknown sample_strategy: {sample_strategy}")

    seed_sequence = np.random.SeedSequence(seed)
    boot_seeds = seed_sequence.spawn(bootstrap_n)

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if sample_strategy == 'pairwise_complete':
                # Dedupe column list to avoid duplicate-named columns when d1==d2
                # (DataFrame[[d1,d1]] would return DataFrame slice instead of Series).
                cols = [d1] if d1 == d2 else [d1, d2]
                clean = df[cols].dropna()
            else:
                clean = clean_base

            if len(clean) < 100:
                continue

            # F40: degenerate (both-constant) guard
            if clean[d1].nunique() < 2 or clean[d2].nunique() < 2:
                logger.error(
                    f"  v3.5.0 D3 degenerate dim-pair: ({d1}, {d2}) nunique < 2; "
                    "skipped per F40 (NMI undefined for constant cols)"
                )
                continue

            n_pair.iloc[i, j] = len(clean)

            # CR-9: 对角线 NMI(X,X) = 1.0 by definition (H(X,X)/H(X) = 1);
            # 跳过 bootstrap (省 ~1000 NMI calls 每个对角线; cross 6×6 节省 6×1000 calls)
            if d1 == d2:
                point.iloc[i, j] = 1.0
                ci_low.iloc[i, j] = 1.0
                ci_high.iloc[i, j] = 1.0
                continue

            point.iloc[i, j] = nmi_score(
                clean[d1], clean[d2], average_method='arithmetic'
            )

            # CR-10: bootstrap 只对 [d1, d2] 两列 resample (省 listwise 共享 base
            # 的 6-列 memory; 对 N=400k × 6 cols × 1000 boot × 36 cells, 减 ~70% peak)
            clean_pair = clean[[d1, d2]]

            # Bootstrap CI: integral row-pair resample (修 C1)
            # CR-11: degenerate fallback 改 NaN + 用 nanpercentile + count
            boot = np.full(bootstrap_n, np.nan)
            n_degenerate = 0
            for k, s in enumerate(boot_seeds):
                state = int(s.generate_state(1)[0])
                clean_boot = clean_pair.sample(frac=1, replace=True, random_state=state)
                # 防 bootstrap resample 后 degenerate (极不平衡 label 时常见)
                if clean_boot[d1].nunique() < 2 or clean_boot[d2].nunique() < 2:
                    n_degenerate += 1
                    continue  # leave boot[k] as NaN
                boot[k] = nmi_score(
                    clean_boot[d1], clean_boot[d2],
                    average_method='arithmetic'
                )
            # 记录 degenerate 比例 (审稿人 sanity check); >5% 触发 warning
            if n_degenerate > 0:
                degen_frac = n_degenerate / bootstrap_n
                if degen_frac > 0.05:
                    logger.warning(
                        f"  v3.5.0 D3 bootstrap ({d1}, {d2}): "
                        f"{n_degenerate}/{bootstrap_n} = {degen_frac:.1%} resamples degenerate; "
                        "CI computed via nanpercentile"
                    )
            # nanpercentile 自动跳过 NaN; 若 boot 全 NaN, 留 ci 为 NaN
            valid_boot = boot[~np.isnan(boot)]
            if len(valid_boot) > 0:
                ci_low.iloc[i, j] = float(np.percentile(valid_boot, 2.5))
                ci_high.iloc[i, j] = float(np.percentile(valid_boot, 97.5))

    return point, ci_low, ci_high, n_pair


def compute_permutation_null(
    df: pd.DataFrame,
    dims: list[str],
    n_permutations: int = 1000,
    seed: int = 43,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Permutation-based null distribution for NMI thresholds (修 C3).

    Returns (null_p95, null_p99) — matrices of NMI 95% / 99% percentile of null
    distribution per (d1, d2). Used as pre-registered threshold reference rather
    than ad-hoc 0.15 / 0.30 thresholds.

    Reads off-diagonal cells only (i != j); diagonals are NaN.
    """
    nmi_score = _lazy_import_nmi()
    n = len(dims)
    null_p95 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    null_p99 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)

    # F-56: Missing column guard (对称 compute_nmi_matrix 防御).
    missing_cols = [d for d in dims if d not in df.columns]
    if missing_cols:
        logger.warning(
            f"  v3.5.0 D3 permutation null: missing dim columns {missing_cols}; "
            f"returning all-NaN matrices."
        )
        return null_p95, null_p99

    clean = df[dims].dropna()

    if len(clean) < 100:
        logger.warning(
            f"  v3.5.0 D3 permutation: clean sample {len(clean)} < 100, returning all-NaN"
        )
        return null_p95, null_p99

    seed_sequence = np.random.SeedSequence(seed)
    perm_seeds = seed_sequence.spawn(n_permutations)

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if i == j:
                continue
            if clean[d1].nunique() < 2 or clean[d2].nunique() < 2:
                continue

            null = np.empty(n_permutations)
            d2_vals = clean[d2].values
            for k, s in enumerate(perm_seeds):
                rng = np.random.default_rng(s)
                d2_perm = rng.permutation(d2_vals)
                null[k] = nmi_score(
                    clean[d1], d2_perm, average_method='arithmetic'
                )
            null_p95.iloc[i, j] = float(np.percentile(null, 95))
            null_p99.iloc[i, j] = float(np.percentile(null, 99))

    return null_p95, null_p99


def classify_orthogonality(point: pd.DataFrame, null_p95: pd.DataFrame,
                           null_p99: pd.DataFrame) -> dict:
    """Permutation-null 单侧分位三档分类 (per plan §2.2.6).

    口径声明 (fix(omni-g-audit-family-04, 2026-06-11)): 阈值 = permutation null
    的单侧 95% / 99% 分位 (≈ 单侧 Z 1.645 / 2.326), 非双侧 Z 1.96 / 2.58.
    调用方必须保证 ``point`` 与 ``null_p95``/``null_p99`` 来自**同一 listwise
    样本域** (NMI 有限样本偏差随 N 变化, 域错配会使阈值失准).

    Returns dict per off-diagonal (d1, d2) pair:
        'strong'   if observed_NMI ≤ null_p95
        'moderate' if null_p95 < obs ≤ null_p99
        'weak'     if obs > null_p99 (triggers paper Appendix A.2 暂缓 per §2.2.6 R2)
    """
    result = {}
    for d1 in point.index:
        for d2 in point.columns:
            if d1 == d2:
                continue
            obs = point.loc[d1, d2]
            p95 = null_p95.loc[d1, d2]
            p99 = null_p99.loc[d1, d2]
            if pd.isna(obs) or pd.isna(p95) or pd.isna(p99):
                result[f'{d1}__{d2}'] = 'undefined'
                continue
            if obs <= p95:
                result[f'{d1}__{d2}'] = 'strong'
            elif obs <= p99:
                result[f'{d1}__{d2}'] = 'moderate'
            else:
                result[f'{d1}__{d2}'] = 'weak'
    return result


def run_stage(
    stage_21_parquet: Optional[str] = None,
    out_dir: Optional[str] = None,
    bootstrap_n: int = 1000,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """Stage 39c entry point: read stage 21 parquet, compute NMI matrices + null, write outputs.

    Outputs (per plan §2.2.3):
        39c_nmi_matrix_full.parquet   — full 3×3 NMI + CI + n_pair (multi-frame parquet)
        39c_nmi_matrix_ctx.parquet    — ctx  3×3 同
        39c_nmi_matrix_cross.parquet  — 6×6 full ∪ ctx cross-matrix
        39c_nmi_null_p95.parquet      — Permutation null 95% percentile reference
        39c_nmi_null_p99.parquet      — 99% percentile
        39c_nmi_summary.json          — {max_off_diag, classify_per_pair, interpretation}

    Reproducibility: 输入 parquet anchored to v3.4.0 commit 450c1aa7 (per plan §0 Tag-over-hash).
    """
    if stage_21_parquet is None:
        stage_21_parquet = os.environ.get(
            'STAGE_21_PARQUET',
            'data/processed/21_tone_llms.parquet',
        )
    if out_dir is None:
        out_dir = os.environ.get('OUT_DIR', 'data/processed')

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"v3.5.0 D3 stage 39c reading: {stage_21_parquet}")
    df = pd.read_parquet(stage_21_parquet)
    logger.info(f"  loaded {len(df):,} article rows")

    # CR-13: SeedSequence.spawn(2) 派生 2 个独立子序列, 避免 `seed + 1` 的耦合
    root_seq = np.random.SeedSequence(seed)
    boot_seed_state, perm_seed_state = (int(s.generate_state(1)[0])
                                        for s in root_seq.spawn(2))

    # full 3x3
    point_f, lo_f, hi_f, n_f = compute_nmi_matrix(
        df, DIMS_FULL, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # ctx 3x3
    point_c, lo_c, hi_c, n_c = compute_nmi_matrix(
        df, DIMS_CTX, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # cross 6x6
    point_x, lo_x, hi_x, n_x = compute_nmi_matrix(
        df, ALL_DIMS, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # permutation null (独立 seed) — 6×6 cross-matrix 参考 (落盘用)
    null_p95, null_p99 = compute_permutation_null(
        df, ALL_DIMS, n_permutations=n_permutations, seed=perm_seed_state,
    )

    # fix(omni-g-audit-family-04, 2026-06-11): classify 的观测值 point_f 在 DIMS_FULL
    # 3 列 listwise 样本上计算, 旧实现却对照 ALL_DIMS 6 列 listwise 样本的 null 阈值 —
    # NMI 有限样本偏差随 N 变化, 观测/阈值样本域不一致 (双轨缺失差异越大错配越大).
    # 现为 DIMS_FULL 在其自身 listwise 域上单独重算 null, 与 point_f 同域.
    null_p95_f, null_p99_f = compute_permutation_null(
        df, DIMS_FULL, n_permutations=n_permutations, seed=perm_seed_state,
    )

    # classify orthogonality (3 dim full only — simpler narrative for paper Appendix A.2)
    classify = classify_orthogonality(point_f, null_p95_f, null_p99_f)

    # Write outputs
    def _save_matrix(name: str, point: pd.DataFrame, lo: pd.DataFrame,
                     hi: pd.DataFrame, n: pd.DataFrame) -> None:
        # Stack 4 layers into long-form DataFrame for parquet
        long = []
        for d1 in point.index:
            for d2 in point.columns:
                long.append({
                    'd1': d1, 'd2': d2,
                    'nmi': point.loc[d1, d2],
                    'ci_low': lo.loc[d1, d2],
                    'ci_high': hi.loc[d1, d2],
                    'n_pair': int(n.loc[d1, d2]),
                })
        pd.DataFrame(long).to_parquet(out_path / name, index=False)  # CR-14

    _save_matrix('39c_nmi_matrix_full.parquet', point_f, lo_f, hi_f, n_f)
    _save_matrix('39c_nmi_matrix_ctx.parquet', point_c, lo_c, hi_c, n_c)
    _save_matrix('39c_nmi_matrix_cross.parquet', point_x, lo_x, hi_x, n_x)
    null_p95.to_parquet(out_path / '39c_nmi_null_p95.parquet')
    null_p99.to_parquet(out_path / '39c_nmi_null_p99.parquet')

    # off-diagonal max for summary (nan-safe in case some pairs degenerate)
    off_diag_mask = ~np.eye(len(ALL_DIMS), dtype=bool)
    off_diag_vals = point_x.values[off_diag_mask]
    max_off_diag = float(np.nanmax(off_diag_vals)) if not np.all(np.isnan(off_diag_vals)) else float('nan')

    # CR-15: vacuous truth bug fix — when classify is all 'undefined' (e.g.,
    # all permutation nulls failed due to degenerate dims), `all(... if v != 'undefined')`
    # returned True (vacuous), wrongly reporting 'strong'. Filter explicitly first.
    non_undefined = [v for v in classify.values() if v != 'undefined']
    if not non_undefined:
        interpretation = 'undefined'
    elif all(v == 'strong' for v in non_undefined):
        interpretation = 'strong'
    elif any(v == 'weak' for v in non_undefined):
        interpretation = 'mixed'
    else:
        interpretation = 'moderate'

    summary = {
        'max_off_diag_nmi': max_off_diag,
        'classify_full_3x3': classify,
        'interpretation': interpretation,
        # fix(omni-g-audit-family-04, 2026-06-11): 口径披露 — 观测与 null 同域 +
        # 单侧分位阈值 (非双侧 Z 1.96/2.58)
        'classify_threshold_scale': (
            'one-sided permutation percentile p95/p99 (≈ one-sided Z 1.645/2.326); '
            'observed NMI and null share the same DIMS_FULL 3-col listwise sample'),
        'reproducibility': {
            'stage_21_input': stage_21_parquet,
            'v3_4_0_anchor': '450c1aa7 (per plan §0 Tag-over-hash)',
            'bootstrap_n': bootstrap_n,
            'n_permutations': n_permutations,
            'seed': seed,
        },
    }
    with open(out_path / '39c_nmi_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(
        f"  ✓ v3.5.0 D3 stage 39c done; max off-diag NMI = {max_off_diag:.4f}; "
        f"interpretation = {summary['interpretation']}"
    )
    return summary
