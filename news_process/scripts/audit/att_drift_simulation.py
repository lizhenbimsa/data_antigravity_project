"""ATT 漂移模拟（Plan E P-1 D2 / F2 闭合）.

目的: 在 G3=A（main treatment 切换 _full → _ctx）执行前，
用 50% 随机抽样跑 P1 主回归 spec 的 ctx-only ATT，与现有 _full ATT
对比。若 |Δ ATT / ATT_full| > 30% 或 ctx 路径 t-stat < 1.5，
触发 G3 决策重审（可能需保留 _full 为 main）。

学术依据:
    ad-hoc 实务显著性启发式 (ad-hoc practical-significance heuristic):
    |Δ/baseline| > 30% 作为相对变化幅度阈值。
    (注: 此为相对变化比阈值, 非 Cohen (1988) 标准化效应量 d=0.2/0.5/0.8 约定, 勿混淆。)
    Andrews, Stock & Sun (2019, Annual Review of Economics) weak IV diagnostic: t-stat < 1.96
    in 50% subsample is a leading indicator of full-sample insignificance.

用法（user-run）:
    F:\\Anaconda3\\python.exe news_process/scripts/audit/att_drift_simulation.py

输出:
    logs/audit/att_drift_<timestamp>.json
    {
      "att_full": float,  "se_full": float,  "t_full": float,
      "att_ctx":  float,  "se_ctx":  float,  "t_ctx":  float,
      "delta_pct": float,
      "gate_decision": "PROCEED" | "REVIEW_G3" | "ABORT"
    }

Gate 规则:
    PROCEED    : |Δ%| ≤ 30 AND |t_ctx| ≥ 1.96
    REVIEW_G3  : |Δ%| ∈ (30, 50] OR t_ctx ∈ [1.5, 1.96)
    ABORT      : |Δ%| > 50 OR |t_ctx| < 1.5

白话: 在把主回归变量从"全文版"换成"上下文版"之前, 先抽一半样本试算一遍:
两个版本的估计效应差得不多且新版本依然显著 → 放行换; 差得有点多或显著性
变弱 → 回炉重审这个决定; 差得离谱或干脆不显著 → 直接叫停。
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402


def _load_panel() -> pd.DataFrame:
    cfg = load_config()
    output_dir = cfg['paths']['output_dir']
    filenames = cfg.get('filenames', {})
    panel_name = filenames.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    panel_path = os.path.join(output_dir, panel_name)
    if not os.path.exists(panel_path):
        raise SystemExit(f"Panel not found: {panel_path}. Run pipeline first.")
    return pd.read_parquet(panel_path)


def _ols_one_sided(df: pd.DataFrame, y_col: str) -> tuple[float, float, float]:
    """单变量 OLS — 仅用作 ATT 漂移代理 (不替代 Stata 主回归).

    spec: y_col ~ post + 银行 FE + 年 FE
    """
    if y_col not in df.columns:
        return (np.nan, np.nan, np.nan)
    sub = df[[y_col, 'target_bank', 'year']].dropna()
    if len(sub) < 100:
        return (np.nan, np.nan, np.nan)
    # 简化的 within 估计: 双向 demean
    sub = sub.copy()
    sub['post'] = (sub['year'] >= 2017).astype(float)
    y_demean = sub[y_col] - sub.groupby('target_bank')[y_col].transform('mean')
    y_demean = y_demean - y_demean.groupby(sub['year']).transform('mean')
    x_demean = sub['post'] - sub.groupby('target_bank')['post'].transform('mean')
    x_demean = x_demean - x_demean.groupby(sub['year']).transform('mean')
    if x_demean.var() < 1e-10:
        return (np.nan, np.nan, np.nan)
    beta = (x_demean * y_demean).sum() / (x_demean ** 2).sum()
    resid = y_demean - beta * x_demean
    n = len(sub)
    se = np.sqrt((resid ** 2).sum() / max(n - 2, 1) / max((x_demean ** 2).sum(), 1e-10))
    t = beta / se if se > 0 else np.nan
    return (float(beta), float(se), float(t))


def main():
    print("=" * 60)
    print("ATT Drift Simulation — Plan E P-1 D2 / F2 Gate")
    print("=" * 60)

    df = _load_panel()
    print(f"Panel loaded: {len(df)} rows, {len(df.columns)} cols")

    rng = np.random.default_rng(seed=42)
    sample_idx = rng.choice(df.index, size=len(df) // 2, replace=False)
    sub = df.loc[sample_idx].copy()
    print(f"50% subsample: {len(sub)} rows")

    # P1 主 spec 候选 outcome: avg_llm_vote_score (full / ctx)
    candidates_full = ['avg_llm_vote_score_full', 'llm_vote_score_hw_sum_full']
    candidates_ctx = ['avg_llm_vote_score_ctx', 'llm_vote_score_hw_sum_ctx']
    y_full = next((c for c in candidates_full if c in sub.columns), None)
    y_ctx = next((c for c in candidates_ctx if c in sub.columns), None)
    if y_full is None or y_ctx is None:
        print("[ERROR] full/ctx column not found; ensure pipeline complete.")
        sys.exit(2)

    print(f"Using y_full={y_full}, y_ctx={y_ctx}")
    att_f, se_f, t_f = _ols_one_sided(sub, y_full)
    att_c, se_c, t_c = _ols_one_sided(sub, y_ctx)

    delta_pct = abs(att_c - att_f) / max(abs(att_f), 1e-8) * 100 if not np.isnan(att_f) else np.nan

    if delta_pct <= 30 and abs(t_c) >= 1.96:
        decision = "PROCEED"
    elif delta_pct <= 50 and abs(t_c) >= 1.5:
        decision = "REVIEW_G3"
    else:
        decision = "ABORT"

    result = {
        "y_full": y_full,
        "y_ctx": y_ctx,
        "att_full": att_f,
        "se_full": se_f,
        "t_full": t_f,
        "att_ctx": att_c,
        "se_ctx": se_c,
        "t_ctx": t_c,
        "delta_pct": delta_pct,
        "gate_decision": decision,
        "subsample_n": len(sub),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    cfg = load_config()
    out_dir = os.path.join(cfg['paths'].get('log_dir', 'logs'), 'audit')
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"att_drift_{ts}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("-" * 60)
    print(f"ATT (full): {att_f:+.4f} (se={se_f:.4f}, t={t_f:+.2f})")
    print(f"ATT (ctx):  {att_c:+.4f} (se={se_c:.4f}, t={t_c:+.2f})")
    print(f"|Δ/full|:   {delta_pct:.1f}%")
    print(f"Decision:   {decision}")
    print(f"Saved:      {out_path}")
    print("=" * 60)

    if decision == "ABORT":
        sys.exit(3)


if __name__ == "__main__":
    main()
