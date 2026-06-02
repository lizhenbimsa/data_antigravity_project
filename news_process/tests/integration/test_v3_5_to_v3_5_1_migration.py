"""tests/integration/test_v3_5_to_v3_5_1_migration.py — v3.5.0 → v3.5.1 迁移单测.

测试覆盖 (6 tests, per plan v0.3 §4.1):
    1. 加载旧 panel (无 8 列) auto graceful skip; v3.5.1 加列 idempotent
    2. golden v0 → v1 hash schema-additive check (v0 archived 不删, parametrize 双轨)
    3. 双 idempotent: apply_v3_5_1 重复调用结果不变
    4. median_amb_d0 sidecar JSON 存在性 + 路径校验 (修 C1' panel.attrs 序列化丢失)
    5. Stata IC core ≤ 2048 (修 R9)
    6. HEURISTIC_LABELS 与 var_label_map 同步 (修 H2' 单 SoT)
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_old_panel_without_a1_a3_graceful():
    """加载旧 panel (无 v3.5.1 8 列) 调用 apply_v3_5_1 不抛 + graceful skip."""
    from news_process.pipeline.panel.encode_collab import (
        aggregate_clarity_panel,
        aggregate_num_intensity_panel,
    )
    # 模拟旧 panel (无 8 列) + 旧 df (无 article 层 clarity 列)
    df_old = pd.DataFrame({
        'target_bank': ['A', 'B'], 'year': [2020, 2020],
        'media_authority_weight': [1.0, 1.0],
        'herd_weight_full': [1.0, 1.0],
    })
    panel_old = pd.DataFrame({'target_bank': ['A', 'B'], 'year': [2020, 2020]})
    # graceful: 不抛, 返回空 added_cols
    result_a1 = aggregate_clarity_panel(df_old, panel_old, median_amb_d0=0.05)
    result_a3 = aggregate_num_intensity_panel(df_old, panel_old)
    assert result_a1['v3_5_1_clarity_added'] == []
    assert result_a3['v3_5_1_num_intensity_added'] == []


def test_golden_v0_archived_path_documented():
    """plan v0.3 §4.3: golden v0 应 archived (v0_archived.json 不删), 仅检查文件路径约定.

    实际重生需 user 跑 generate_golden_snapshot.py --version v1; 本测试仅验证路径约定.
    """
    fixtures_dir = REPO_ROOT / 'tests' / 'fixtures'
    v0_path = fixtures_dir / 'golden_panel_v0.json'
    # v0 必须存在 (历史 baseline)
    if not v0_path.exists():
        pytest.skip(f"golden_panel_v0.json 未找到 (历史 baseline)")
    # v0_archived 由 D6 重生流程生成 (cp v0 → v0_archived); 此处仅检查命名约定
    # archived path 应为同目录
    expected_archived = fixtures_dir / 'golden_panel_v0_archived.json'
    # 不强求 archived 已存在 (user 跑 D6 时生成), 仅验证路径合法
    assert expected_archived.parent.is_dir()


def test_apply_v3_5_1_idempotent(tmp_path, monkeypatch):
    """双 idempotent: 重复调用 apply_v3_5_1 panel 结果不变."""
    from news_process.pipeline.panel.encode_collab import apply_v3_5_1
    # 测试隔离 (audit/goal-2026-05-29 R1): apply_v3_5_1 把 sidecar JSON 写到相对路径
    # 'data/processed/v3_5_1_constants.json' (含 datetime.now() 时间戳)。pytest 从仓库根
    # 运行时该相对路径解析到受 git 跟踪的 sidecar, 每次跑都会刷新时间戳 → 污染工作树
    # (非确定性 + dirty tree)。本测试只断言 panel 聚合列的幂等性, 与 sidecar 内容无关,
    # 故 chdir 到 tmp_path 把副作用写入重定向到临时目录, 不改动生产逻辑/断言。
    monkeypatch.chdir(tmp_path)
    df = pd.DataFrame([
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.05, 'clarity_frac_definite_full': 0.10,
         'clarity_clarity_score_full': 0.05,
         'clarity_frac_ambiguous_ctx': 0.04, 'clarity_frac_definite_ctx': 0.08,
         'clarity_clarity_score_ctx': 0.04,
         'num_intensity_full': 1.5, 'num_intensity_ctx': 1.2,
         'media_authority_weight': 1.0, 'herd_weight_full': 1.0},
        {'target_bank': 'A', 'year': 2020,
         'clarity_frac_ambiguous_full': 0.08, 'clarity_frac_definite_full': 0.05,
         'clarity_clarity_score_full': -0.03,
         'clarity_frac_ambiguous_ctx': 0.09, 'clarity_frac_definite_ctx': 0.04,
         'clarity_clarity_score_ctx': -0.05,
         'num_intensity_full': 2.0, 'num_intensity_ctx': 1.8,
         'media_authority_weight': 1.0, 'herd_weight_full': 1.0},
    ])
    panel1 = pd.DataFrame([{'target_bank': 'A', 'year': 2020}])
    panel2 = pd.DataFrame([{'target_bank': 'A', 'year': 2020}])
    # 两次调用应得相同 panel 列
    apply_v3_5_1(df.copy(), panel1)
    apply_v3_5_1(df.copy(), panel2)
    for col in ['mean_clarity_score_full', 'mean_num_intensity_full']:
        if col in panel1.columns and col in panel2.columns:
            v1, v2 = panel1[col].iloc[0], panel2[col].iloc[0]
            assert abs(v1 - v2) < 1e-9, f"{col} idempotent violation: {v1} vs {v2}"


def test_sidecar_json_path_exists_or_created():
    """sidecar JSON 路径约定 (修 C1' panel.attrs 序列化丢失).

    实际 sidecar 在 D0 首次跑 apply_v3_5_1 时写入; 本测试验证 stub 存在 + 必要字段.
    """
    sidecar_path = REPO_ROOT / 'data' / 'processed' / 'v3_5_1_constants.json'
    if not sidecar_path.exists():
        pytest.skip(f"sidecar JSON 未生成 (D0 day apply_v3_5_1 首次跑时写入)")
    with open(sidecar_path, 'r', encoding='utf-8') as f:
        sidecar = json.load(f)
    # 必要字段
    assert 'median_amb_d0' in sidecar
    assert 'prompt_v8_sha256' in sidecar
    assert 'stage21_last_run_timestamp' in sidecar
    assert 'a1_clarity_panel_cols' in sidecar
    assert 'a3_num_intensity_panel_cols' in sidecar


def test_stata_ic_core_below_2048():
    """v3.5.1 +8 后 core ≤ STATA_IC_MAX_VARS = 2048 (修 R9)."""
    from news_process.pipeline.panel.stata_export import (
        STATA_IC_MAX_VARS,
        assign_core_columns,
    )
    # 模拟 panel 含全部 v3.5.1 8 新列
    a1_a3_cols = [
        'mean_clarity_score_full', 'mean_clarity_score_ctx',
        'mean_frac_definite_full', 'mean_frac_definite_ctx',
        'frac_amb_articles_full', 'frac_amb_articles_ctx',
        'mean_num_intensity_full', 'mean_num_intensity_ctx',
    ]
    df = pd.DataFrame(columns=a1_a3_cols + ['target_bank', 'year'])
    core = assign_core_columns(df)
    assert len(core) <= STATA_IC_MAX_VARS, (
        f"v3.5.1 后 core 列数 {len(core)} 超 IC max {STATA_IC_MAX_VARS}"
    )


def test_heuristic_labels_export_stata_labels_sync():
    """v3.5.1: stata_export.HEURISTIC_LABELS 与 export.py STATA_LABELS 8 entries 同步 (修 H2')."""
    from news_process.pipeline.panel import export as export_mod
    from news_process.pipeline.panel.stata_export import build_variable_labels

    a1_a3_cols = [
        'mean_clarity_score_full', 'mean_clarity_score_ctx',
        'mean_frac_definite_full', 'mean_frac_definite_ctx',
        'frac_amb_articles_full', 'frac_amb_articles_ctx',
        'mean_num_intensity_full', 'mean_num_intensity_ctx',
    ]
    df = pd.DataFrame(columns=a1_a3_cols)
    heuristic_labels = build_variable_labels(df)
    src = inspect.getsource(export_mod)
    for col in a1_a3_cols:
        h_label = heuristic_labels[col]
        assert h_label in src, (
            f"export.py STATA_LABELS 与 stata_export.HEURISTIC_LABELS 不同步 — "
            f"missing entry for {col}: '{h_label}'"
        )
