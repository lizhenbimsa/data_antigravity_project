"""Orphan-panel merge fix (2026-05-30) — stage 18 / 39f feature panels into 40_panel_yearly.

Stage 18 (staleness) and 39f (cross_media_alpha) each
produce a bank-year FEATURE panel whose columns stata_export.py core_patterns already
declares, but nothing merged them into 40_panel_yearly. runner.py main() now has a
conditional left-merge loop that
brings their columns in when the (opt-in) stage has run, and is a graceful no-op when
the file is absent (the default, since stage 18 is disabled-by-default).

`pytest.mark.fast` (pure source-inspection + in-memory pandas; no IO/LLM).
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

pytestmark = pytest.mark.fast

_RUNNER = (Path(__file__).resolve().parents[1]
           / "pipeline" / "panel" / "runner.py")


def _runner_src() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_runner_has_feature_merge_block():
    """The 8c merge loop must reference both remaining orphan feature panels
    (18 staleness + 39f cross_media_alpha, paper-10 main treatment)."""
    src = _runner_src()
    for fname in ("18_staleness_panel.parquet",
                  "39f_cross_media_alpha.parquet"):
        assert fname in src, f"runner.py missing feature-merge for {fname}"


def test_runner_merge_is_key_safe_and_graceful():
    """The merge must fail-loud on duplicate keys, left-join, raise on row-count
    drift, and be guarded by os.path.exists (graceful when the opt-in stage didn't
    run).

    断言更新 (fix(omni-g-runner-16), 2026-06-11): 旧断言锁
    `drop_duplicates(['target_bank', 'year'])` (静默取任意首行, 使行数守卫永真
    空转) — 新契约为重复键即 raise + 特征文件 mtime 新鲜度守卫。
    """
    src = _runner_src()
    assert "duplicated(['target_bank', 'year'])" in src
    assert "拒绝静默取首行" in src
    # freshness guard: feature file must not predate its registered upstreams
    assert "_OPTIN_FEATURE_UPSTREAMS" in src
    assert "getmtime" in src
    assert "how='left'" in src
    # row-count integrity guard (raise, not assert — survives python -O)
    assert re.search(r"feature merge 改变面板行数", src)
    assert "os.path.exists(_opath)" in src


# --- behavioral contract (mirrors the 8c loop semantics on fixtures) -----------

def _merge_feature(panel: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    """Replicate the runner.py 8c merge contract for a single feature panel.

    契约更新 (fix(omni-g-runner-16), 2026-06-11): 重复 (bank,year) 键不再
    drop_duplicates 静默取首行, 而是 fail-loud raise (镜像
    _merge_optin_feature_panels 新语义)。
    """
    if feat.duplicated(['target_bank', 'year']).any():
        raise RuntimeError("duplicate (target_bank, year) keys in feature panel")
    bring = ['target_bank', 'year'] + [
        c for c in feat.columns
        if c not in ('target_bank', 'year') and c not in panel.columns]
    n_before = len(panel)
    out = panel.merge(feat[bring], on=['target_bank', 'year'], how='left')
    if len(out) != n_before:
        raise RuntimeError("feature merge changed row count (key not 1:1)")
    return out


def _panel():
    return pd.DataFrame({
        'target_bank': ['工商', '建设', '农业'],
        'year': [2018, 2018, 2018],
        'llm_vote_tone_full': [0.1, -0.2, 0.0],
    })


def test_feature_merge_preserves_rowcount_and_adds_cols():
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '农业'],  # 建设 has no staleness row
        'year': [2018, 2018],
        'surface_staleness_full': [0.5, 0.7],
    })
    out = _merge_feature(panel, feat)
    assert len(out) == 3                      # left-join preserves panel rows
    assert 'surface_staleness_full' in out.columns
    assert out.loc[out['target_bank'] == '工商', 'surface_staleness_full'].iloc[0] == 0.5
    assert pd.isna(out.loc[out['target_bank'] == '建设', 'surface_staleness_full'].iloc[0])


def test_feature_merge_raises_on_duplicate_keys():
    """Duplicate (bank,year) rows in the feature panel must fail-loud.

    断言更新 (fix(omni-g-runner-16), 2026-06-11): 旧契约 drop_duplicates 静默
    取任意首行 (0.5 vs 0.9 不确定) 且使行数守卫永真空转 — 新契约重复键即 raise。
    """
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '工商'],   # duplicate key
        'year': [2018, 2018],
        'surface_staleness_full': [0.5, 0.9],
    })
    with pytest.raises(RuntimeError, match="duplicate"):
        _merge_feature(panel, feat)


def test_feature_merge_does_not_overwrite_existing_panel_column():
    """A feature col that collides with an existing panel col is skipped (panel wins)."""
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '建设', '农业'],
        'year': [2018, 2018, 2018],
        'llm_vote_tone_full': [9.9, 9.9, 9.9],   # collides with panel
        'surface_staleness_full': [0.5, 0.6, 0.7],
    })
    out = _merge_feature(panel, feat)
    # existing panel value preserved, not overwritten by the feature panel's 9.9
    assert out.loc[out['target_bank'] == '工商', 'llm_vote_tone_full'].iloc[0] == 0.1
    assert 'surface_staleness_full' in out.columns
