"""news_process.pipeline.audit.inter_track_kappa — Stage 39a (P1 of three-dim borrowing plan v1.37).

Compute article-level Cohen's κ between full and ctx tracks for the two
innovation dimensions (locus and substantiveness) on the
``llm_verified_dual_both == True`` subset; emit machine-readable CSV +
paper-ready TeX to ``eval_reports/``.

Mirrors the Stata template ``20_tableA1_inter_track_kappa.do.tmpl``.

Academic anchors:
  - Cohen (1960) — κ formula.
  - Landis & Koch (1977) — κ interpretation thresholds.
  - docs/methodology/inter_track_agreement_interpretation.md §2:
    κ ∈ [0.50, 0.70] expected (not "higher is better"); κ > 0.70 flags
    redundant dual-track; κ < 0.30 flags noise.
  - Plan v1.37 §4.3.1: bootstrap CI with NaN-aware percentile + 50%
    finite-fraction guard (R30A-01/R30B-01).
"""
import os
import warnings

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import setup_logging
from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat

STAGE_NAME = "39a_inter_track_kappa"

# Plan v1.37 §4.3.1 thresholds (from inter_track_agreement_interpretation.md).
# v3.4.0 §J.4: 第三维度 collab_mode κ ≥ 0.45 (mirrors substantiveness fair-to-moderate
# 标准; Chesbrough 2003 + L&S 2006 SMJ; additive supplementation per Nosek 2018 PNAS).
_THRESHOLDS = {
    'innovation_locus': 0.50,
    'innovation_substantiveness': 0.45,
    'innovation_collab_mode': 0.45,
}


def _compute_kappa_with_bootstrap(y1, y2, n_boot=1000, seed=42):
    """Return (kappa_point, ci_low, ci_high, n_obs) with NaN-safe bootstrap.

    Implementation per plan v1.37 §4.3.1 steps 1-5:
      1. Short-circuit n_obs < 3 → (nan, nan, nan, n_obs).
      2. Point κ via cohens_kappa_2cat(...)['kappa'] (R29C-01 dict access).
      3. Bootstrap n_boot resamples; append ['kappa'] per resample.
      4. NaN-aware percentile (R30A-01/R30B-01): require ≥50% finite kappas
         else return (kappa_point, nan, nan, n_obs) + WARN.
      5. Edge: original input with one column constant → (nan, nan, nan, n_obs).
    """
    y1 = np.asarray(y1)
    y2 = np.asarray(y2)
    n_obs = len(y1)
    if n_obs < 3:
        return (float('nan'), float('nan'), float('nan'), int(n_obs))

    point = cohens_kappa_2cat(y1, y2)
    kappa_point = point['kappa']
    # Original-input constant-column edge (point is NaN already → return NaN tuple)
    if np.isnan(kappa_point):
        return (float('nan'), float('nan'), float('nan'), int(n_obs))

    rng = np.random.default_rng(seed)
    kappas = []
    for _ in range(n_boot):
        idx = rng.choice(n_obs, size=n_obs, replace=True)
        kb = cohens_kappa_2cat(y1[idx], y2[idx])['kappa']
        kappas.append(kb)

    finite = [k for k in kappas if not np.isnan(k)]
    if len(finite) < 0.5 * n_boot:
        warnings.warn(
            f"Bootstrap degenerate: only {len(finite)}/{n_boot} finite κ "
            f"resamples (< 50%); CI bounds returned as NaN.",
            RuntimeWarning,
            stacklevel=2,
        )
        return (float(kappa_point), float('nan'), float('nan'), int(n_obs))

    ci_low = float(np.nanpercentile(kappas, 2.5))
    ci_high = float(np.nanpercentile(kappas, 97.5))
    return (float(kappa_point), ci_low, ci_high, int(n_obs))


def compute_inter_track_kappa(df):
    """Return DataFrame with 7 columns: field, kappa_point, ci_95_low,
    ci_95_high, n_obs, threshold, passes_threshold.

    One row per innovation dimension (locus, substantiveness, collab_mode [v3.4.0])."""
    rows = []
    for field, threshold in _THRESHOLDS.items():
        col_full = f"{field}_full"
        col_ctx = f"{field}_ctx"
        if col_full not in df.columns or col_ctx not in df.columns:
            rows.append({
                'field': field,
                'kappa_point': float('nan'),
                'ci_95_low': float('nan'),
                'ci_95_high': float('nan'),
                'n_obs': 0,
                'threshold': threshold,
                'passes_threshold': False,
            })
            continue
        # Drop NaN-paired rows
        sub = df[[col_full, col_ctx]].dropna()
        kp, lo, hi, n = _compute_kappa_with_bootstrap(
            sub[col_full].to_numpy(),
            sub[col_ctx].to_numpy(),
        )
        passes = (not np.isnan(kp)) and (kp >= threshold)
        rows.append({
            'field': field,
            'kappa_point': kp,
            'ci_95_low': lo,
            'ci_95_high': hi,
            'n_obs': n,
            'threshold': threshold,
            'passes_threshold': bool(passes),
        })
    return pd.DataFrame(rows, columns=[
        'field', 'kappa_point', 'ci_95_low', 'ci_95_high',
        'n_obs', 'threshold', 'passes_threshold',
    ])


def _render_tex(table_df, out_path):
    """Booktabs-style TeX table; matches plan v1.37 §4.7 acceptance regex
    (\\toprule / \\midrule / \\bottomrule; 7 columns; 2 data rows)."""
    cols = list(table_df.columns)
    n_cols = len(cols)
    lines = [
        "\\begin{tabular}{" + "l" + "r" * (n_cols - 1) + "}",
        "\\toprule",
        " & ".join(cols) + " \\\\",
        "\\midrule",
    ]
    for _, r in table_df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("NaN" if np.isnan(v) else f"{v:.4f}")
            elif isinstance(v, (bool, np.bool_)):
                cells.append("True" if bool(v) else "False")
            else:
                cells.append(str(v))
        lines.append(" & ".join(cells) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path_str = str(out_path)
    with open(out_path_str, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")


def run_stage(config=None, logger=None):
    """Stage 39a entry point.

    Reads ``21_tone_llms.parquet`` from configured output dir, filters on
    ``llm_verified_dual_both == True``, computes inter-track κ for both
    innovation dimensions, writes CSV + TeX to ``eval_reports/``.
    """
    if config is None:
        config = load_config()
    if logger is None:
        logger = setup_logging(STAGE_NAME, config["paths"]["log_dir"])

    output_dir = config["paths"]["output_dir"]
    input_path = os.path.join(output_dir, "21_tone_llms.parquet")

    if not os.path.exists(input_path):
        logger.warning(f"Input not found: {input_path}; emitting NaN row table.")
        df_subset = pd.DataFrame(columns=[
            'innovation_locus_full', 'innovation_locus_ctx',
            'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
            'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
            'llm_verified_dual_both',
        ])
    else:
        df = pd.read_parquet(input_path)
        if 'llm_verified_dual_both' not in df.columns:
            logger.warning(
                "Column 'llm_verified_dual_both' absent; emitting NaN rows."
            )
            df_subset = df.iloc[0:0]
        else:
            df_subset = df[df['llm_verified_dual_both'] == True].copy()
            if len(df_subset) == 0:
                logger.warning("dual_both subset empty; emitting NaN rows.")

    table = compute_inter_track_kappa(df_subset)

    eval_dir = os.path.join(output_dir, "eval_reports")
    os.makedirs(eval_dir, exist_ok=True)
    csv_path = os.path.join(eval_dir, "inter_track_kappa_table.csv")
    tex_path = os.path.join(eval_dir, "inter_track_kappa_table.tex")

    table.to_csv(csv_path, index=False, encoding='utf-8')
    _render_tex(table, tex_path)

    # Threshold range warning per plan v1.37 §4.3.1 step 6
    for _, r in table.iterrows():
        k = r['kappa_point']
        if not np.isnan(k) and (k < 0.30 or k > 0.70):
            warnings.warn(
                f"{r['field']} κ={k:.4f} outside expected [0.30, 0.70]; "
                f"<0.30 = one track noise; >0.70 = dual-track redundant.",
                RuntimeWarning,
                stacklevel=2,
            )
            logger.warning(
                f"{r['field']} κ={k:.4f} outside [0.30, 0.70] sentinel range."
            )

    logger.info(f"Wrote {csv_path} + {tex_path} (n_obs={int(table['n_obs'].iloc[0] if len(table) else 0)})")
    return table
