"""测试 v3.3.0 → v3.4.0 panel 迁移脚本 (plan §C2 hard deliverable).

镜像 test_v3_1_to_v3_2_migration.py 模式, 验证 4 个新增 collab_mode 列
(innovation_collab_mode_{full,ctx} + innovation_collab_mode_confidence_{full,ctx})
通过迁移脚本正确补齐为 None / 0.0 占位; 现有列不动 (idempotent + backward compat).

学术依据: Chesbrough 2003 Open Innovation + Laursen & Salter 2006 SMJ
27(2):131-150 第三维度 additive supplementation (Nosek 2018 PNAS).
"""
from __future__ import annotations

import pandas as pd
import pytest

from news_process.scripts.migrate.v3_3_to_v3_4_panel_upgrade import (
    NEW_CONFIDENCE_COLUMNS,
    NEW_LABEL_COLUMNS,
    upgrade_panel_v3_3_to_v3_4,
)


def _build_v33_panel() -> pd.DataFrame:
    """构造最小 v3.3.0 panel fixture (含 v3.2.0 BREAKING 后的双轨列)."""
    return pd.DataFrame({
        'docid': ['a1', 'a2', 'a3'],
        'target_bank': ['工商银行', '建设银行', '招商银行'],
        'year': [2017, 2018, 2018],
        # v3.2.0 双轨列 (BREAKING 后)
        'innovation_locus_full': ['底层技术', '应用场景', None],
        'innovation_locus_ctx': ['底层技术', None, '应用场景'],
        'innovation_substantiveness_full': ['实质性', '象征性', '实质性'],
        'innovation_substantiveness_ctx': ['实质性', None, None],
    })


def test_upgrade_adds_4_new_columns():
    """v3.3.0 → v3.4.0 迁移后, 必新增 4 个 collab_mode 列."""
    df_v33 = _build_v33_panel()
    assert 'innovation_collab_mode_full' not in df_v33.columns
    assert 'innovation_collab_mode_ctx' not in df_v33.columns

    df_v34 = upgrade_panel_v3_3_to_v3_4(df_v33)
    for col in NEW_LABEL_COLUMNS + NEW_CONFIDENCE_COLUMNS:
        assert col in df_v34.columns, f'缺失列: {col}'


def test_upgrade_new_label_columns_are_none():
    """新增 label 列以 None 占位 (用户需重跑 stage 21 prompt v8 才有实际值)."""
    df_v34 = upgrade_panel_v3_3_to_v3_4(_build_v33_panel())
    for col in NEW_LABEL_COLUMNS:
        assert df_v34[col].isna().all(), f'{col} 应全 None: {df_v34[col].tolist()}'


def test_upgrade_new_confidence_columns_are_zero():
    """新增 confidence 列以 0.0 占位 (与 tone_llms.py 空 dataframe fallback 一致)."""
    df_v34 = upgrade_panel_v3_3_to_v3_4(_build_v33_panel())
    for col in NEW_CONFIDENCE_COLUMNS:
        assert (df_v34[col] == 0.0).all(), f'{col} 应全 0.0: {df_v34[col].tolist()}'


def test_upgrade_preserves_existing_columns():
    """v3.3.0 既有列在 v3.4.0 中数值不变 (backward compat per master plan §3.4)."""
    df_v33 = _build_v33_panel()
    df_v34 = upgrade_panel_v3_3_to_v3_4(df_v33)
    for col in df_v33.columns:
        pd.testing.assert_series_equal(
            df_v33[col].reset_index(drop=True),
            df_v34[col].reset_index(drop=True),
            check_names=False,
            obj=f'列 {col} 不应被迁移修改',
        )


def test_upgrade_preserves_row_count():
    """迁移不增删行 (panel obs 数不变, v3.3.0 168 obs 仍是 168)."""
    df_v33 = _build_v33_panel()
    df_v34 = upgrade_panel_v3_3_to_v3_4(df_v33)
    assert df_v34.shape[0] == df_v33.shape[0]
    assert df_v34.shape[1] == df_v33.shape[1] + 4, \
        f'shape: v33={df_v33.shape}, v34={df_v34.shape}; 应 +4 列'


def test_upgrade_idempotent_when_columns_exist():
    """若 v3.4.0 列已存在 (如重跑 stage 21 后), 迁移脚本保留原值."""
    df = _build_v33_panel()
    df['innovation_collab_mode_full'] = ['自主研发', '外部协同', None]
    df['innovation_collab_mode_ctx'] = ['自主研发', None, '外部协同']
    df['innovation_collab_mode_confidence_full'] = [0.85, 0.72, 0.0]
    df['innovation_collab_mode_confidence_ctx'] = [0.91, 0.0, 0.68]

    df_v34 = upgrade_panel_v3_3_to_v3_4(df)
    # 已有值应保留 (不被 None / 0.0 覆盖)
    assert df_v34['innovation_collab_mode_full'].tolist() == ['自主研发', '外部协同', None]
    assert df_v34['innovation_collab_mode_confidence_full'].tolist() == [0.85, 0.72, 0.0]


def test_upgrade_does_not_mutate_input():
    """迁移脚本不应修改输入 DataFrame (返回拷贝)."""
    df_v33 = _build_v33_panel()
    cols_before = list(df_v33.columns)
    _ = upgrade_panel_v3_3_to_v3_4(df_v33)
    assert list(df_v33.columns) == cols_before, '输入 df 列被修改'
    assert 'innovation_collab_mode_full' not in df_v33.columns


@pytest.mark.parametrize('label_col', NEW_LABEL_COLUMNS)
def test_new_label_columns_dtype_object(label_col: str):
    """新增 label 列应是 object dtype (容纳 str + None)."""
    df_v34 = upgrade_panel_v3_3_to_v3_4(_build_v33_panel())
    assert df_v34[label_col].dtype == object


@pytest.mark.parametrize('conf_col', NEW_CONFIDENCE_COLUMNS)
def test_new_confidence_columns_dtype_numeric(conf_col: str):
    """新增 confidence 列应是 numeric dtype."""
    df_v34 = upgrade_panel_v3_3_to_v3_4(_build_v33_panel())
    assert pd.api.types.is_numeric_dtype(df_v34[conf_col])
