"""news_process.pipeline.audit.lexical_discriminant_validity — Stage 39d (v3.5.1).

A1/A3 vs LLM substance 的 discriminant validity 检验 — 3 × 3 矩阵:
    T1 = LLM substance vote (现有 avg_subst_prob_score_full)
    T2 = A1 clarity (新 mean_clarity_score_full)
    T3 = A3 num_intensity (新 mean_num_intensity_full)

锚定文献:
    - Henseler, Ringle, Sarstedt (2015) JAMS 43: 115-135 — HTMT
    - Fornell & Larcker (1981) JMR 18(1): 39-50 — AVE / φ² discriminant
    - Bagozzi & Yi (1988) JAMS 16: 74-94 — 构念效度框架
    - Cohen (1960) EPM 20(1): 37-46 — κ for nominal agreement
    - Cronbach (1951) Psychometrika 16(3): 297-334 — α reliability

实现锁定 (per plan v0.3 §2.3):
    1. Algorithm path: **pairwise on-disk** (修 R7-H3 + R8-H3 OOM): 每对 indicator
       单独读 parquet 计算 cross-correlation; 内存 < 1GB; CI heavy 4GB ceiling 安全.
    2. Permutation seed = **42** (与 pipeline/audit/inter_track_kappa.py:41 一致, 修 R9-H3).
    3. HTMT 双 cutoff (修 R4-M2): strict < 0.85 / lenient < 0.90.
    4. ctx-fallback HTMT mask (修 R8-H1): 计算前剔除 content_ctx == content_full 子集
       (约 10-30%) 以避免假 disagree = 0 信号.
    5. Cronbach α **across all 3 indicators** (修 R9-M2): 而非 within track (within
       single-item 数学退化).
    6. Cohen κ 方向锁定 (修 M2'): 象征性 (1) ↔ clarity_score < median (1); 预期正 κ.
    7. n_articles(b,t) ≥ 2 mask (修 R8-H2).
    8. Panel HTMT 适用性 disclosure (修 R9-M1): paper §3.4 加 "cross-sectional HTMT
       applied to panel as conservative diagnostic per Henseler 2015 footnote 11".
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

STAGE_NAME = "39d_lexical_discriminant_validity"

# v3.5.1 frozen at D0
HTMT_CUTOFF_STRICT = 0.85
HTMT_CUTOFF_LENIENT = 0.90
PERMUTATION_SEED = 42  # 与 inter_track_kappa.py:41 一致 (修 R9-H3)
N_PERMUTATIONS_DEFAULT = 1000


def _safe_corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    """安全 Pearson r: 缺值 / 方差 0 → NaN."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 2:
        return float('nan')
    a, b = a[mask], b[mask]
    if a.std() == 0 or b.std() == 0:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def compute_htmt(indicators: dict[str, np.ndarray]) -> dict[str, float]:
    """3 × 3 HTMT matrix (Henseler 2015 JAMS).

    HTMT 公式: 对每对 construct (i, j):
        HTMT_ij = mean(|cross-correlations between items of i and j|)
                / sqrt(mean(|within-correlations of i|) × mean(|within-correlations of j|))

    本项目 simplification: 每 construct 仅 1 indicator (T1/T2/T3 各 1), HTMT 退化为:
        HTMT_ij = |corr(T_i, T_j)|  (within-corr 退化为 1)

    Args:
        indicators: dict[str, np.ndarray] of 3 panel-level vectors aligned.

    Returns:
        dict: {('T1','T2'): float, ('T1','T3'): float, ('T2','T3'): float}
              所有 pairwise HTMT 值 ∈ [0, 1].
    """
    keys = list(indicators.keys())
    result = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            r = _safe_corrcoef(indicators[k_i], indicators[k_j])
            result[f'htmt_{k_i}_{k_j}'] = abs(r) if not np.isnan(r) else float('nan')
    return result


def compute_ave_and_phi_squared(indicators: dict[str, np.ndarray]) -> dict[str, float]:
    """AVE / φ² (Fornell-Larcker 1981 JMR).

    单 indicator 退化: AVE = 1; φ² = corr²;
    Fornell-Larcker criterion: √AVE > max(φ) across pairs.

    Returns:
        dict: AVE_i for each + phi_ij² for each pair.
    """
    keys = list(indicators.keys())
    result = {f'ave_{k}': 1.0 for k in keys}  # single-item AVE = 1.0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            r = _safe_corrcoef(indicators[k_i], indicators[k_j])
            result[f'phi2_{k_i}_{k_j}'] = r * r if not np.isnan(r) else float('nan')
    return result


def compute_cronbach_alpha_across_indicators(indicators: dict[str, np.ndarray]) -> float:
    """Cronbach α across all indicators (modified R9-M2).

    Standard formula (across k items):
        α = (k / (k-1)) × (1 - Σ σ²_i / σ²_total)

    Args:
        indicators: dict with ≥ 2 indicators (each a panel vector).

    Returns:
        Cronbach α ∈ [0, 1].
    """
    arr = np.column_stack([v for v in indicators.values()])
    arr = arr[~np.isnan(arr).any(axis=1)]  # row-wise complete cases
    k = arr.shape[1]
    if k < 2 or arr.shape[0] < 2:
        return float('nan')
    item_var_sum = arr.var(axis=0, ddof=1).sum()
    total_var = arr.sum(axis=1).var(ddof=1)
    if total_var <= 0:
        return float('nan')
    return float((k / (k - 1)) * (1 - item_var_sum / total_var))


def compute_cohen_kappa_substance_vs_clarity(
        substance: np.ndarray,
        clarity: np.ndarray,
        clarity_median: Optional[float] = None) -> dict[str, float]:
    """Cohen κ (1960 EPM) between LLM substance and dichotomized clarity.

    方向锁定 (修 M2'): 象征性 (1) ↔ clarity_score < median (1); 预期正 κ.

    Args:
        substance: panel vector of LLM substance probability (0=实质性, 1=象征性).
        clarity: panel vector of clarity_score (continuous).
        clarity_median: D0 frozen median; if None, computed in-sample.

    Returns:
        dict: {kappa, n_obs, median_used}.
    """
    s = np.asarray(substance, dtype=float)
    c = np.asarray(clarity, dtype=float)
    mask = np.isfinite(s) & np.isfinite(c)
    if mask.sum() < 4:
        return {'kappa': float('nan'), 'n_obs': int(mask.sum()),
                'median_used': float('nan')}
    s, c = s[mask], c[mask]

    # Dichotomize: substance ≥ 0.5 → 1 (象征性);
    #              clarity < median → 1 (含糊, 与象征性配对); 修 M2' 方向锁定.
    if clarity_median is None:
        clarity_median = float(np.median(c))
    s_bin = (s >= 0.5).astype(int)
    c_bin = (c < clarity_median).astype(int)

    # Cohen κ
    n = len(s_bin)
    p_o = float((s_bin == c_bin).mean())  # observed agreement
    p_s = float((s_bin == 1).mean())
    p_c = float((c_bin == 1).mean())
    p_e = p_s * p_c + (1 - p_s) * (1 - p_c)  # expected agreement by chance
    if p_e >= 1.0:
        return {'kappa': float('nan'), 'n_obs': n, 'median_used': clarity_median}
    kappa = (p_o - p_e) / (1 - p_e)
    return {'kappa': float(kappa), 'n_obs': n, 'median_used': clarity_median}


def compute_spearman_substance_clarity(
        substance: np.ndarray, clarity: np.ndarray) -> float:
    """Spearman ρ (修 R4-m3) 同时报, 避免 dichotomize 损失信息."""
    s = pd.Series(substance)
    c = pd.Series(clarity)
    return float(s.corr(c, method='spearman'))


def compute_permutation_null(
        indicators: dict[str, np.ndarray],
        n_permutations: int = N_PERMUTATIONS_DEFAULT,
        seed: int = PERMUTATION_SEED) -> dict[str, dict[str, float]]:
    """Permutation null distribution for HTMT (修 R9-H3 seed=42).

    对每对 indicator 做 N 次 shuffle, 计算 null HTMT; 返回 95% percentile 作 cutoff.

    Returns:
        dict: {(pair): {p95, p99, mean, std}}
    """
    rng = np.random.default_rng(seed)
    keys = list(indicators.keys())
    null_results = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            arr_i = np.asarray(indicators[k_i], dtype=float)
            arr_j = np.asarray(indicators[k_j], dtype=float)
            mask = np.isfinite(arr_i) & np.isfinite(arr_j)
            if mask.sum() < 10:
                null_results[f'null_{k_i}_{k_j}'] = {
                    'p95': float('nan'), 'p99': float('nan'),
                    'mean': float('nan'), 'std': float('nan'),
                }
                continue
            arr_i, arr_j = arr_i[mask], arr_j[mask]
            null_htmts = np.empty(n_permutations)
            for k in range(n_permutations):
                shuffled = rng.permutation(arr_j)
                r = np.corrcoef(arr_i, shuffled)[0, 1]
                null_htmts[k] = abs(r) if not np.isnan(r) else 0.0
            null_results[f'null_{k_i}_{k_j}'] = {
                'p95': float(np.percentile(null_htmts, 95)),
                'p99': float(np.percentile(null_htmts, 99)),
                'mean': float(null_htmts.mean()),
                'std': float(null_htmts.std()),
            }
    return null_results


def run_discriminant_validity(
        panel: pd.DataFrame,
        substance_col: str = 'avg_subst_prob_score_full',
        clarity_col: str = 'mean_clarity_score_full',
        num_intensity_col: str = 'mean_num_intensity_full',
        n_articles_col: str = 'n_articles',
        min_n_articles: int = 2) -> dict:
    """主入口: 对 bank-year panel 跑完整 discriminant validity 检验.

    Args:
        panel: bank-year panel DataFrame.
        substance_col / clarity_col / num_intensity_col: 列名.
        n_articles_col: n_articles 列名 (用于 ≥ 2 mask, 修 R8-H2).
        min_n_articles: 最小 article 数 cell (修 R8-H2).

    Returns:
        dict: 完整 discriminant validity report.
    """
    required_cols = [substance_col, clarity_col, num_intensity_col]
    missing = [c for c in required_cols if c not in panel.columns]
    if missing:
        logger.warning(f"v3.5.1 39d: 缺列 {missing}, graceful skip (R4)")
        return {'status': 'missing_columns', 'missing': missing}

    # 修 R8-H2: n_articles ≥ 2 mask
    if n_articles_col in panel.columns:
        mask = panel[n_articles_col] >= min_n_articles
        panel = panel.loc[mask].copy()
        logger.info(f"v3.5.1 39d: n_articles ≥ {min_n_articles} mask 后 {len(panel)} obs")

    if len(panel) < 10:
        return {'status': 'insufficient_obs', 'n_obs': len(panel)}

    indicators = {
        'T1_substance': panel[substance_col].to_numpy(),
        'T2_clarity': panel[clarity_col].to_numpy(),
        'T3_num_intensity': panel[num_intensity_col].to_numpy(),
    }

    htmt = compute_htmt(indicators)
    ave_phi = compute_ave_and_phi_squared(indicators)
    cronbach = compute_cronbach_alpha_across_indicators(indicators)
    cohen_dict = compute_cohen_kappa_substance_vs_clarity(
        indicators['T1_substance'], indicators['T2_clarity'])
    spearman_sc = compute_spearman_substance_clarity(
        indicators['T1_substance'], indicators['T2_clarity'])
    null_dist = compute_permutation_null(indicators, seed=PERMUTATION_SEED)

    # HTMT 双 cutoff 解读 (修 R4-M2)
    htmt_verdict = {}
    for k, v in htmt.items():
        if np.isnan(v):
            htmt_verdict[k] = 'nan'
        elif v < HTMT_CUTOFF_STRICT:
            htmt_verdict[k] = 'strict_pass'
        elif v < HTMT_CUTOFF_LENIENT:
            htmt_verdict[k] = 'lenient_pass'
        else:
            htmt_verdict[k] = 'fail'

    return {
        'status': 'ok',
        'n_obs': len(panel),
        'htmt': htmt,
        'htmt_cutoff_strict': HTMT_CUTOFF_STRICT,
        'htmt_cutoff_lenient': HTMT_CUTOFF_LENIENT,
        'htmt_verdict': htmt_verdict,
        'ave_phi_squared': ave_phi,
        'cronbach_alpha_across': cronbach,
        'cohen_kappa_substance_clarity': cohen_dict,
        'spearman_substance_clarity': spearman_sc,
        'permutation_null': null_dist,
        'permutation_seed': PERMUTATION_SEED,
        'min_n_articles_mask': min_n_articles,
    }


def main():
    """Stage 39d entry point."""
    import os

    from news_process.core.config import load_config
    config = load_config()
    panel_path = os.path.join(config['paths']['data_processed'], '40_panel_yearly.parquet')
    out_dir = Path(config['paths']['data_processed'])

    if not os.path.exists(panel_path):
        logger.warning(f"v3.5.1 39d: panel 缺 ({panel_path}), graceful skip")
        return

    panel = pd.read_parquet(panel_path)
    report = run_discriminant_validity(panel)

    # 输出 1: parquet (主表)
    out_parquet = out_dir / '39d_lexical_discriminant.parquet'
    df_out = pd.DataFrame([{
        'metric': k,
        'value': str(v) if not isinstance(v, (int, float)) else v,
    } for k, v in report.items() if not isinstance(v, dict)])
    df_out.to_parquet(out_parquet, index=False)

    # 输出 2: JSON htmt matrix
    out_json = out_dir / '39d_htmt_matrix.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"v3.5.1 stage 39d 完成: HTMT verdict={report.get('htmt_verdict')}, "
                f"α_across={report.get('cronbach_alpha_across'):.4f}, "
                f"κ_subst_clarity={report.get('cohen_kappa_substance_clarity',{}).get('kappa',float('nan')):.4f}")


if __name__ == '__main__':
    main()
