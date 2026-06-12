"""孤儿特征面板 merge 修复 (2026-05-30) — stage 18 / 39f 特征面板并入 40_panel_yearly。

Stage 18 (staleness) 与 39f (cross_media_alpha) 各产出一个 bank-year 特征面板,
其列在 stata_export.py core_patterns 已登记, 但此前没有任何环节把它们 merge 进
40_panel_yearly。runner.py main() 现有一个条件 left-merge 循环: opt-in 阶段跑过
就把列并进来, 文件缺失时优雅 no-op (注: stage 18 原为 disabled-by-default,
2026-06-01 全功能打开后配置已显式启用; merge 循环的存在性守卫不变)。

`pytest.mark.fast` (纯源码检查 + 内存 pandas; 无 IO/LLM)。

# 白话: "孤儿面板"指算出来了却没人接进总面板的特征表。这组测试确保 runner
# 的并表循环存在、左连接不丢行、键重复时大声报错、文件不在时安静跳过。
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
    """8c merge 循环必须引用两个尚存的孤儿特征面板
    (18 staleness + 39f cross_media_alpha, 后者是 paper-10 主 treatment)。"""
    src = _runner_src()
    for fname in ("18_staleness_panel.parquet",
                  "39f_cross_media_alpha.parquet"):
        assert fname in src, f"runner.py missing feature-merge for {fname}"


def test_runner_merge_is_key_safe_and_graceful():
    """merge 必须: 键重复 fail-loud、left-join、行数漂移即 raise,
    且受 os.path.exists 守卫 (opt-in 阶段没跑时优雅跳过)。

    断言更新 (fix(omni-g-runner-16), 2026-06-11): 旧断言锁
    `drop_duplicates(['target_bank', 'year'])` (静默取任意首行, 使行数守卫永真
    空转) — 新契约为重复键即 raise + 特征文件 mtime 新鲜度守卫。
    """
    src = _runner_src()
    assert "duplicated(['target_bank', 'year'])" in src
    assert "拒绝静默取首行" in src
    # 新鲜度守卫: 特征文件的 mtime 不得早于其登记的上游产物
    assert "_OPTIN_FEATURE_UPSTREAMS" in src
    assert "getmtime" in src
    assert "how='left'" in src
    # 行数完整性守卫 (用 raise 而非 assert — python -O 下不会被剥掉)
    assert re.search(r"feature merge 改变面板行数", src)
    assert "os.path.exists(_opath)" in src


# --- 行为契约 (在 fixture 上镜像 8c 循环的语义) -----------

def _merge_feature(panel: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    """对单个特征面板复刻 runner.py 8c merge 契约。

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
        'target_bank': ['工商', '农业'],  # 建设 没有 staleness 行
        'year': [2018, 2018],
        'surface_staleness_full': [0.5, 0.7],
    })
    out = _merge_feature(panel, feat)
    assert len(out) == 3                      # left-join 保留 panel 全部行
    assert 'surface_staleness_full' in out.columns
    assert out.loc[out['target_bank'] == '工商', 'surface_staleness_full'].iloc[0] == 0.5
    assert pd.isna(out.loc[out['target_bank'] == '建设', 'surface_staleness_full'].iloc[0])


def test_feature_merge_raises_on_duplicate_keys():
    """特征面板中重复的 (bank, year) 行必须 fail-loud。

    断言更新 (fix(omni-g-runner-16), 2026-06-11): 旧契约 drop_duplicates 静默
    取任意首行 (0.5 vs 0.9 不确定) 且使行数守卫永真空转 — 新契约重复键即 raise。
    """
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '工商'],   # 重复键
        'year': [2018, 2018],
        'surface_staleness_full': [0.5, 0.9],
    })
    with pytest.raises(RuntimeError, match="duplicate"):
        _merge_feature(panel, feat)


def test_feature_merge_does_not_overwrite_existing_panel_column():
    """特征列与既有 panel 列同名时跳过该列 (panel 优先)。"""
    panel = _panel()
    feat = pd.DataFrame({
        'target_bank': ['工商', '建设', '农业'],
        'year': [2018, 2018, 2018],
        'llm_vote_tone_full': [9.9, 9.9, 9.9],   # 与 panel 既有列同名冲突
        'surface_staleness_full': [0.5, 0.6, 0.7],
    })
    out = _merge_feature(panel, feat)
    # panel 既有值保留, 不被特征面板的 9.9 覆盖
    assert out.loc[out['target_bank'] == '工商', 'llm_vote_tone_full'].iloc[0] == 0.1
    assert 'surface_staleness_full' in out.columns
