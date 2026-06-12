"""Phase B' 合并诊断：F2 / F3 / F4 一次性确权（read-only on parquet）。"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

PROJ = Path(__file__).resolve().parents[3]
PROC = PROJ / "data" / "processed"

results = {}

# ── F2: 统计 (verified=False ∩ sentiment=中性) 行数 ──
p_full = PROC / "21_tone_llms_full.parquet"
if p_full.exists():
    df = pd.read_parquet(p_full)
    f2 = {}
    for track in ("_full", "_ctx"):
        v_col = f"llm_verified{track}"
        s_col = f"llm_sentiment{track}"
        if v_col in df.columns and s_col in df.columns:
            mask = (df[v_col] == False) & (df[s_col] == "中性")
            f2[f"forced_neutral_count{track}"] = int(mask.sum())
            f2[f"all_neutral{track}"] = int((df[s_col] == "中性").sum())
            f2[f"all_rows"] = len(df)
    results["F2"] = f2
else:
    results["F2"] = {"_error": f"{p_full} not found"}

# ── F3: panel n_articles==0 行的相似度列 NaN vs 0.0 ──
p_panel = PROC / "40_panel_yearly.parquet"
if p_panel.exists():
    panel = pd.read_parquet(p_panel)
    f3 = {"shape": panel.shape}
    if "n_articles" in panel.columns:
        zero_mask = panel["n_articles"] == 0
        f3["n_articles_zero"] = int(zero_mask.sum())
        for prefix in (
            "auth_sim_",
            "benefit_",
            "token_adopt_",
            "hidden_adopt_",
            "subst_adopt_",
            "article_sim_",
            "fintech_intensity_mean",
            "policy_cosine_sim_t2v",
        ):
            cols = [c for c in panel.columns if c.startswith(prefix)]
            if cols:
                sub = panel.loc[zero_mask, cols]
                eq_zero = (sub == 0.0).sum().sum()
                isna = sub.isna().sum().sum()
                f3[prefix] = {
                    "n_cols": len(cols),
                    "eq_zero_in_zeronews": int(eq_zero),
                    "isna_in_zeronews": int(isna),
                }
    # F4: bartik IV 列清点
    bartik_cols = sorted([c for c in panel.columns if c.startswith("bartik_")])
    f4 = {
        "bartik_total_cols": len(bartik_cols),
        "bartik_categories": sorted(
            set(c.split("_")[1] for c in bartik_cols if c.startswith("bartik_"))
        ),
        "bartik_first_30": bartik_cols[:30],
    }
    results["F3"] = f3
    results["F4"] = f4
else:
    results["F3"] = {"_error": f"{p_panel} not found"}
    results["F4"] = {"_error": "skipped (no panel)"}

out = Path(__file__).parent / "B_consolidated_diagnostics.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(results, ensure_ascii=False, indent=2))
print(f"\n[OK] saved -> {out}")
