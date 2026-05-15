"""v3.2.0 panel migration utility 测试 (plan v14 §3.6).

测试 v3.1.1 → v3.2.0 panel parquet BREAKING rename:
  - bare innovation_locus → innovation_locus_full (rename)
  - 新加 innovation_locus_ctx 列 (NaN, 待重跑 stage 21)
  - 派生 llm_verified_dual_full_only / _ctx_only / _both 三互斥指示
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


@pytest.fixture
def mock_v3_1_panel(tmp_path):
    """模拟 v3.1.1 panel: bare innovation_locus / innovation_substantiveness."""
    df = pd.DataFrame({
        'target_bank': ['工商银行', '建设银行', '招商银行'],
        'year': [2020, 2020, 2020],
        'innovation_locus':            ['底层技术', '应用场景', '底层技术'],
        'innovation_substantiveness':  ['实质性', '象征性', '实质性'],
        'category_confidence':         [0.9, 0.8, 0.85],
        'llm_verified_full':           [True, True, False],
        'llm_verified_ctx':            [True, False, True],
    })
    p = tmp_path / "v3_1_panel.parquet"
    df.to_parquet(p, index=False)
    return p


def test_upgrade_renames_bare_columns(mock_v3_1_panel, tmp_path):
    """v3.1.1 bare 列名 → v3.2.0 _full 后缀."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    out = tmp_path / "v3_2_panel.parquet"
    stats = upgrade_panel(str(mock_v3_1_panel), str(out))
    assert stats['n_renamed'] == 3  # locus + substantiveness + category_confidence

    df = pd.read_parquet(out)
    # 旧 bare 列不存在
    assert 'innovation_locus' not in df.columns
    assert 'innovation_substantiveness' not in df.columns
    assert 'category_confidence' not in df.columns
    # 新 _full 列存在
    assert 'innovation_locus_full' in df.columns
    assert 'innovation_substantiveness_full' in df.columns
    assert 'category_confidence_full' in df.columns


def test_upgrade_adds_ctx_columns_as_nan(mock_v3_1_panel, tmp_path):
    """新加 _ctx 列填 NaN, 用户需重跑 stage 21 LLM 产实际值."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    out = tmp_path / "v3_2_panel.parquet"
    stats = upgrade_panel(str(mock_v3_1_panel), str(out))
    assert stats['n_added_nan'] == 3

    df = pd.read_parquet(out)
    assert 'innovation_locus_ctx' in df.columns
    assert 'innovation_substantiveness_ctx' in df.columns
    assert 'category_confidence_ctx' in df.columns
    # ctx 列全 NaN (待重跑)
    assert df['innovation_locus_ctx'].isna().all()


def test_upgrade_derives_dual_gate(mock_v3_1_panel, tmp_path):
    """派生 dual gate 三互斥指示列 (基于 verified_full/ctx)."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    out = tmp_path / "v3_2_panel.parquet"
    stats = upgrade_panel(str(mock_v3_1_panel), str(out))
    assert stats['n_dual_gate_derived'] == 3

    df = pd.read_parquet(out)
    # mock_v3_1_panel: 3 行 verified (full, ctx):
    #   行 0: (T, T) → both
    #   行 1: (T, F) → full_only
    #   行 2: (F, T) → ctx_only
    assert list(df['llm_verified_dual_full_only']) == [False, True, False]
    assert list(df['llm_verified_dual_ctx_only'])  == [False, False, True]
    assert list(df['llm_verified_dual_both'])      == [True, False, False]


def test_upgrade_preserves_n_rows(mock_v3_1_panel, tmp_path):
    """升级不丢行."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    out = tmp_path / "v3_2_panel.parquet"
    stats = upgrade_panel(str(mock_v3_1_panel), str(out))
    assert stats['n_rows'] == 3
    df_new = pd.read_parquet(out)
    assert len(df_new) == 3


def test_upgrade_missing_old_columns_no_error(tmp_path):
    """如果 v3.1.1 已是部分升级 (缺 bare 列), 仍能完成 ctx 列 + dual gate."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    # 已有 _full 后缀的 panel (假装已部分升级)
    df = pd.DataFrame({
        'target_bank': ['工行'],
        'year': [2020],
        'innovation_locus_full': ['底层技术'],
        'llm_verified_full': [True],
        'llm_verified_ctx': [True],
    })
    inp = tmp_path / "partial.parquet"
    df.to_parquet(inp, index=False)
    out = tmp_path / "out.parquet"
    stats = upgrade_panel(str(inp), str(out))
    assert stats['n_renamed'] == 0  # bare 列不存在, 无 rename
    assert stats['n_added_nan'] >= 1  # 仍加 _ctx 列


def test_upgrade_missing_file_raises():
    """输入文件不存在 → FileNotFoundError."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import upgrade_panel
    with pytest.raises(FileNotFoundError, match="不存在"):
        upgrade_panel("/no/such/file.parquet", "/tmp/out.parquet")


def test_cli_main_callable():
    """CLI main importable + argparse 配置."""
    from news_process.scripts.migrate import v3_1_to_v3_2_panel_upgrade as mod
    assert hasattr(mod, 'main')
    assert hasattr(mod, 'upgrade_panel')


def test_cli_returns_nonzero_on_missing_input(tmp_path, capsys):
    """CLI 输入不存在 → exit code 1 + stderr message."""
    from news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade import main
    rc = main(['/no/such/file.parquet', str(tmp_path / "out.parquet")])
    assert rc == 1
    captured = capsys.readouterr()
    assert '[ERROR]' in captured.err
