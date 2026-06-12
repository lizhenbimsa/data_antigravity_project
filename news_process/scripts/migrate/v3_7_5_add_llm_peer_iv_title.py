"""v3.7.5 Tier-2 — validation-gated, cache-only backfill of llm_peer_tone_iv_title. [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨已删): 本脚本物化的列 llm_peer_tone_iv_title (2SLS 标题工具变量) 是标题情感轨
产物, 已随 remove-title-track 标题轨取消。请勿再对 panel 写入该已废列。仅作历史留存。下方为历史描述。

在**现有** frozen panel 上物化真 2SLS 标题工具变量, 而**无需**重跑完整
stage 14-40, 设两道硬安全门:

  1. CACHE-ONLY (纯缓存): monkeypatch `_call_llm_peer`, 使缓存 MISS 直接返回 None
     且**不**调 API (miss 数会被报告)。LLM peer 网络纯由 `_llm_cache.db` 重建
     -> 增量 LLM 成本 $0。miss 数非零即说明重建与 panel-build 那次运行有分歧。
  2. FAITHFULNESS GATE (忠实性门): 重建出的 `llm_peer_tone_iv_full` 与 panel 上
     的现值逐 key 比对。**仅当**每个 key 都精确一致 (同一 peer 网络 -> 工具变量
     一致) 才写入新列 `llm_peer_tone_iv_title`; 否则脚本中止, 不碰 panel。

df_exploded 由 `24_herd_decay.parquet` 重建 (即 runner 的 `input_path`,
runner.py:173-180), year 按 `日期` 派生 (runner.py:1101-1102 约定) — 之所以忠实,
是因为 compute_llm_peer_iv 只消费 {target_bank, year, co_mentioned_banks,
标题, 内容}, 且 df_exploded 之前不丢任何行。

用法:
  python scripts/migrate/v3_7_5_add_llm_peer_iv_title.py            # DRY (只验证)
  python scripts/migrate/v3_7_5_add_llm_peer_iv_title.py --write    # 忠实才写入

白话: 先用缓存"免费重演"一遍 LLM 同行网络, 重演结果若和面板上原有列一字不差,
才敢把新算的标题工具变量列补进面板; 任何一点对不上就立刻放弃, 面板原样不动。
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
    """llm_peer_iv._call_llm_peer 的纯缓存替身: miss 时不调 API。"""
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

    # 门 1: 纯缓存 — 物理上不可能发出 API 调用。
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
