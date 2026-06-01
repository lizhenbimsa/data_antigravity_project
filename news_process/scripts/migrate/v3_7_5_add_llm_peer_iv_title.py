"""v3.7.5 Tier-2 — validation-gated, cache-only backfill of llm_peer_tone_iv_title. [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨已删): 本脚本物化的列 llm_peer_tone_iv_title (2SLS 标题工具变量) 是标题情感轨
产物, 已随 remove-title-track 标题轨取消。请勿再对 panel 写入该已废列。仅作历史留存。下方为历史描述。

Materializes the genuine 2SLS title instrument on the EXISTING frozen panel WITHOUT a
full stage 14-40 re-run, with two hard safety gates:

  1. CACHE-ONLY: `_call_llm_peer` is monkeypatched so a cache MISS returns None and makes
     NO API call (the miss count is reported). The LLM peer network is rebuilt purely
     from `_llm_cache.db` -> $0 incremental LLM. Any nonzero miss count means the
     reconstruction diverged from the panel-build run.
  2. FAITHFULNESS GATE: the rebuilt `llm_peer_tone_iv_full` is compared key-by-key
     against the on-panel values. The new `llm_peer_tone_iv_title` is written ONLY if
     every key matches exactly (same peer network -> consistent instrument). Otherwise
     the script aborts WITHOUT touching the panel.

df_exploded is reconstructed from `24_herd_decay.parquet` (the runner's `input_path`,
runner.py:173-180) with year derived from `日期` (runner.py:1101-1102 convention) —
faithful because compute_llm_peer_iv consumes only {target_bank, year,
co_mentioned_banks, 标题, 内容} and no rows are dropped before df_exploded.

Usage:
  python scripts/migrate/v3_7_5_add_llm_peer_iv_title.py            # DRY (validate only)
  python scripts/migrate/v3_7_5_add_llm_peer_iv_title.py --write    # write if faithful
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

from news_process.pipeline.panel import llm_peer_iv

_REPO = Path(__file__).resolve().parents[2]
_PANEL = _REPO / "data" / "processed" / "40_panel_yearly.parquet"
_ARTICLES = _REPO / "data" / "processed" / "24_herd_decay.parquet"

_MISS = {"n": 0}


async def _cache_only_call(session, semaphore, bank, year, sentences, model_cfg, cache):
    """Cache-only replacement for llm_peer_iv._call_llm_peer: NO API on miss."""
    model_id = model_cfg["model_name"]
    prompt = llm_peer_iv.PEER_PROMPT.format(
        bank_name=bank,
        year=year,
        numbered_sentences="\n".join(f"{i + 1}. {s}" for i, s in enumerate(sentences)),
    )
    if cache is not None:
        cached = cache.get(
            model_id,
            prompt,
            prompt_version=llm_peer_iv.PEER_PROMPT_VERSION,
            temperature=llm_peer_iv.TEMPERATURE,
            random_seed=llm_peer_iv.RANDOM_SEED,
        )
        if cached:
            return bank, year, cached
    _MISS["n"] += 1
    return bank, year, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="materialize column if faithful")
    args = ap.parse_args()

    if not llm_peer_iv.HAS_AIOHTTP:
        sys.exit("ABORT: aiohttp unavailable")
    if not llm_peer_iv.MODELS:
        sys.exit("ABORT: no LLM models configured (config tone_llm_processing.models)")

    # Gate 1: cache-only — no API calls possible.
    llm_peer_iv._call_llm_peer = _cache_only_call

    panel = pd.read_parquet(_PANEL)
    df_exploded = pd.read_parquet(_ARTICLES)
    df_exploded["year"] = pd.to_datetime(df_exploded["日期"], errors="coerce").dt.year
    print(f"panel: {panel.shape}; df_exploded: {df_exploded.shape}; "
          f"years={sorted(df_exploded['year'].dropna().unique().tolist())}")

    iv_prefixes = ("llm_peer_tone_iv", "llm_peer_count", "llm_peer_coverage")
    drop_cols = [c for c in panel.columns
                 if c.startswith(iv_prefixes) or c == "peer_compete_idx"]
    panel_in = panel.drop(columns=drop_cols)

    result = llm_peer_iv.compute_llm_peer_iv(panel_in.copy(), df_exploded)
    print(f"cache MISSES (no API made): {_MISS['n']}")

    if "llm_peer_tone_iv_full" not in result.columns:
        sys.exit("ABORT: reconstruction produced no llm_peer_tone_iv_full")

    keys = ["target_bank", "year"]
    old = panel[keys + ["llm_peer_tone_iv_full"]].dropna(subset=["llm_peer_tone_iv_full"])
    new = result[keys + ["llm_peer_tone_iv_full"]].dropna(subset=["llm_peer_tone_iv_full"])
    m = old.merge(new, on=keys, suffixes=("_old", "_new"), how="outer", indicator=True)
    both = m[m["_merge"] == "both"]
    only_old = int((m["_merge"] == "left_only").sum())
    only_new = int((m["_merge"] == "right_only").sum())
    max_diff = (
        (both["llm_peer_tone_iv_full_old"] - both["llm_peer_tone_iv_full_new"]).abs().max()
        if len(both) else float("nan")
    )
    print(f"iv_full reproduction: on_panel={len(old)} rebuilt={len(new)} "
          f"matched={len(both)} only_old={only_old} only_new={only_new} max_abs_diff={max_diff:.3e}")

    faithful = (
        _MISS["n"] == 0
        and only_old == 0
        and only_new == 0
        and len(both) == len(old) > 0
        and max_diff < 1e-9
    )
    print(f"FAITHFUL = {faithful}")
    if not faithful:
        sys.exit("ABORT: reconstruction NOT faithful (see metrics above); panel untouched.")

    if "llm_peer_tone_iv_title" not in result.columns:
        sys.exit("ABORT: faithful but llm_peer_tone_iv_title not produced "
                 "(llm_vote_tone_title peer coverage empty?).")
    title = result[keys + ["llm_peer_tone_iv_title"]].dropna(subset=["llm_peer_tone_iv_title"])
    print(f"llm_peer_tone_iv_title non-null: {len(title)}")
    print("sample:", title.head(5).to_dict("records"))

    if not args.write:
        print("DRY RUN OK (faithful). Re-run with --write to materialize.")
        return

    if "llm_peer_tone_iv_title" in panel.columns:
        print("idempotent: llm_peer_tone_iv_title already on panel; nothing to do.")
        return
    backup = str(_PANEL) + ".v375bak"
    shutil.copy2(_PANEL, backup)
    out = panel.merge(title, on=keys, how="left")
    assert len(out) == len(panel), "row count changed — aborting"
    out.to_parquet(_PANEL, index=False)
    print(f"WROTE llm_peer_tone_iv_title ({len(title)} non-null) -> {_PANEL.name} (backup: {Path(backup).name})")


if __name__ == "__main__":
    main()
