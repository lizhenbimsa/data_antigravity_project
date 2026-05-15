"""v3.2.0 — Stage 46 stata_export 测试 (plan v14 §9.5)

测试范围:
    - 类别变量编码 (中文 str → byte 0/1)
    - variable labels ≤ 80 字符
    - 列名 ≤ 32 字符
    - core/aux 拆分 (Stata IC ≤ 2048 兼容)
    - labels .do 文件生成
    - 编码方向 (R32-B: 0=baseline, 1=对照)

注: 不依赖 pyreadstat 安装 (除集成测试外, pyreadstat 调用以 ImportError skip)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


@pytest.fixture
def mock_panel():
    """模拟 panel DataFrame, 含双轨 stage 3 字段."""
    return pd.DataFrame({
        'target_bank': ['工商银行', '建设银行', '招商银行'] * 4,
        'year': [2020, 2021, 2022, 2023] * 3,
        'n_articles': [100, 80, 60, 50, 120, 90, 70, 55, 110, 85, 65, 52],
        'innovation_locus_full': ['底层技术', '应用场景', '底层技术', None,
                                  '应用场景', '应用场景', '底层技术', '应用场景',
                                  '底层技术', '应用场景', '底层技术', '应用场景'],
        'innovation_locus_ctx': ['应用场景', '应用场景', '底层技术', '底层技术',
                                 '应用场景', '底层技术', '底层技术', '应用场景',
                                 '应用场景', '应用场景', '底层技术', None],
        'innovation_substantiveness_full': ['实质性', '象征性', '实质性', '象征性',
                                            '实质性', '实质性', '象征性', '实质性',
                                            '象征性', '实质性', '实质性', '象征性'],
        'innovation_substantiveness_ctx':  ['象征性', '象征性', '实质性', '实质性',
                                            '实质性', '象征性', '象征性', '实质性',
                                            '象征性', '实质性', '象征性', '实质性'],
        'llm_vote_tone_full': np.random.RandomState(42).uniform(-1, 1, 12),
        'llm_vote_tone_ctx':  np.random.RandomState(43).uniform(-1, 1, 12),
        'llm_verified_dual_full_only': [False] * 12,
        'llm_verified_dual_ctx_only':  [False] * 12,
        'llm_verified_dual_both':      [True] * 12,
        'category_confidence_full': np.random.RandomState(44).uniform(0.6, 0.95, 12),
        'category_confidence_ctx':  np.random.RandomState(45).uniform(0.6, 0.95, 12),
    })


def test_encoding_direction_locus():
    """R32-B 编码方向: 0=底层技术 (baseline), 1=应用场景 (对照)."""
    from news_process.pipeline.panel.stata_export import LOCUS_ENCODING
    assert LOCUS_ENCODING['底层技术'] == 0
    assert LOCUS_ENCODING['应用场景'] == 1


def test_encoding_direction_substantiveness():
    """R32-B 编码方向: 0=实质性 (baseline), 1=象征性 (对照).

    天然解释方向: 洗稿率框架下 β 解释 "象征性相对实质性的差异".
    """
    from news_process.pipeline.panel.stata_export import SUBSTANTIVENESS_ENCODING
    assert SUBSTANTIVENESS_ENCODING['实质性'] == 0
    assert SUBSTANTIVENESS_ENCODING['象征性'] == 1


def test_encode_categorical_columns(mock_panel):
    """中文 str 列编码为 Int8 0/1."""
    from news_process.pipeline.panel.stata_export import encode_categorical_columns
    encoded_df, value_labels = encode_categorical_columns(mock_panel)
    # 类别列变 Int8
    assert encoded_df['innovation_locus_full'].dtype.name == 'Int8'
    assert encoded_df['innovation_locus_ctx'].dtype.name == 'Int8'
    assert encoded_df['innovation_substantiveness_full'].dtype.name == 'Int8'
    assert encoded_df['innovation_substantiveness_ctx'].dtype.name == 'Int8'
    # value labels 包含 4 个类别列
    assert 'innovation_locus_full' in value_labels
    assert 'innovation_locus_ctx' in value_labels
    assert 'innovation_substantiveness_full' in value_labels
    assert 'innovation_substantiveness_ctx' in value_labels
    # value labels 内容正确 (R32-B 双语)
    assert value_labels['innovation_locus_full'][0] == "底层技术 (Technology)"
    assert value_labels['innovation_substantiveness_full'][1] == "象征性 (Symbolic)"


def test_encoded_none_becomes_nan(mock_panel):
    """plan v14 §9.1: None 类别 → pd.NA (extended missing 在 pyreadstat 层映射 . / .a / .b)."""
    from news_process.pipeline.panel.stata_export import encode_categorical_columns
    encoded_df, _ = encode_categorical_columns(mock_panel)
    # mock_panel 在 innovation_locus_full 行 3 = None → encoded 应为 pd.NA
    assert pd.isna(encoded_df.loc[3, 'innovation_locus_full'])


def test_variable_label_length_under_80(mock_panel):
    """plan v14 §9.5: 全部 variable label ≤ 80 字节 (UTF-8)."""
    from news_process.pipeline.panel.stata_export import STATA_VAR_LABEL_MAXLEN, build_variable_labels
    labels = build_variable_labels(mock_panel)
    too_long = [(c, l, len(l.encode('utf-8'))) for c, l in labels.items()
                if len(l.encode('utf-8')) > STATA_VAR_LABEL_MAXLEN]
    assert not too_long, f"Labels 超 80 字节: {too_long[:5]}"


def test_column_name_length_under_32(mock_panel):
    """plan v14 §9.5 + §2.5: 全部列名 ≤ 32 字符 (Stata 硬限)."""
    from news_process.pipeline.panel.stata_export import STATA_VAR_NAME_MAXLEN
    too_long = [c for c in mock_panel.columns if len(c) > STATA_VAR_NAME_MAXLEN]
    assert not too_long, f"列名超 32 字符: {too_long}"


def test_core_columns_fit_ic(mock_panel):
    """plan v14 §9.1 + §9.5 (R42-A): core 列 ≤ 2048 (Stata IC 兼容)."""
    from news_process.pipeline.panel.stata_export import STATA_IC_MAX_VARS, assign_core_columns
    core = assign_core_columns(mock_panel)
    assert len(core) <= STATA_IC_MAX_VARS, f"Core 列数 {len(core)} 超 IC 限 {STATA_IC_MAX_VARS}"


def test_labels_do_file_generated(mock_panel, tmp_path):
    """plan v14 §9.1: labels .do 含 label var + label define + label values."""
    from news_process.pipeline.panel.stata_export import (
        build_variable_labels,
        encode_categorical_columns,
        write_labels_do_file,
    )
    encoded, value_labels = encode_categorical_columns(mock_panel)
    var_labels = build_variable_labels(encoded)
    do_path = tmp_path / "test_labels.do"
    write_labels_do_file(str(do_path), var_labels, value_labels)
    content = do_path.read_text(encoding='utf-8')
    # 必含三类 Stata 命令
    assert 'label var ' in content
    assert 'label define locus_lbl' in content
    assert 'label define subst_lbl' in content
    assert 'label values' in content
    # 双语 value labels
    assert '底层技术 (Technology)' in content
    assert '实质性 (Substantive)' in content


def test_validate_stata_compat_rejects_long_name():
    """validate_stata_compat 必须拒绝 > 32 字符列名."""
    from news_process.pipeline.panel.stata_export import validate_stata_compat
    bad_df = pd.DataFrame({
        'a_column_name_that_is_definitely_longer_than_32_chars': [1, 2, 3]
    })
    with pytest.raises(ValueError, match="Stata 兼容性"):
        validate_stata_compat(bad_df, {})


def test_validate_stata_compat_rejects_long_label():
    """validate_stata_compat 必须拒绝 > 80 字节 label."""
    from news_process.pipeline.panel.stata_export import validate_stata_compat
    df = pd.DataFrame({'col': [1, 2]})
    long_label = "X" * 90
    with pytest.raises(ValueError, match="Stata 兼容性"):
        validate_stata_compat(df, {'col': long_label})


def test_shorten_long_column_names_idf_score():
    """v3.2.0 M3/7: idf_score → idfsc 缩写覆盖 33-char 列名."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'jiang_2021_idf_score_hw_sum_title': [1.0, 2.0],
        'target_bank': ['工行', '建行'],
    })
    df_new, rename_map = shorten_long_column_names(df)
    # 应缩短到 ≤ 32 字符
    for col in df_new.columns:
        assert len(col) <= 32, f"col '{col}' still {len(col)} chars"
    # rename_map 记录反向映射
    assert 'jiang_2021_idf_score_hw_sum_title' in rename_map.values()


def test_shorten_long_column_names_leave1out():
    """v3.2.0 M3/7: leave1out → l1o 缩写覆盖 33+ char 列名."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'prov_leave1out_dict_avg_tone_full': [1.0],  # 33 chars
        'city_leave1out_dict_avg_tone_title': [2.0],  # 34 chars
    })
    df_new, rename_map = shorten_long_column_names(df)
    for col in df_new.columns:
        assert len(col) <= 32
    assert len(rename_map) == 2


def test_shorten_long_column_names_handles_conflicts(tmp_path):
    """v3.2.0 M3/7: 截断后冲突自动加 _1/_2 后缀防覆盖."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    # 两个超长 col 在截断到 32 字符时会冲突
    df = pd.DataFrame({
        'a_very_long_column_name_that_will_be_truncatedX': [1],
        'a_very_long_column_name_that_will_be_truncatedY': [2],
    })
    df_new, rename_map = shorten_long_column_names(df)
    assert len(set(df_new.columns)) == len(df_new.columns), "冲突未防止"


def test_shorten_long_column_names_short_unchanged():
    """≤ 32 char 列名不改."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'target_bank': [1],
        'innovation_locus_full': [1],
        'short_col': [1],
    })
    df_new, rename_map = shorten_long_column_names(df)
    assert list(df_new.columns) == ['target_bank', 'innovation_locus_full', 'short_col']
    assert rename_map == {}


def test_select_dta_backend():
    """v3.2.0 M1/7: backend 探测 — pyreadstat 优先, pandas fallback."""
    from news_process.pipeline.panel.stata_export import _select_dta_backend
    name, writer = _select_dta_backend()
    assert name in ('pyreadstat', 'pandas')
    assert callable(writer)


def test_export_panel_pandas_fallback_when_no_pyreadstat(tmp_path, mock_panel, monkeypatch):
    """v3.2.0 M1/7: pyreadstat 未装时 fallback 到 pandas to_stata (graceful)."""
    panel_path = tmp_path / "panel.parquet"
    mock_panel.to_parquet(panel_path)

    # Simulate "no pyreadstat" by patching _select_dta_backend
    from news_process.pipeline.panel import stata_export
    monkeypatch.setattr(stata_export, '_select_dta_backend',
                        lambda: ('pandas', stata_export._write_dta_pandas_fallback))

    result = stata_export.export_panel_to_stata(str(panel_path), str(tmp_path))

    # 验证产出文件存在
    import os
    assert os.path.exists(result['core_dta'])
    assert os.path.exists(result['full_dta'])
    assert os.path.exists(result['labels_do'])
    assert result['backend'] == 'pandas'


def test_export_panel_returns_backend_info(tmp_path, mock_panel):
    """v3.2.0 M1/7: export_panel_to_stata 返回 dict 含 backend 字段."""
    panel_path = tmp_path / "panel.parquet"
    mock_panel.to_parquet(panel_path)
    from news_process.pipeline.panel.stata_export import export_panel_to_stata
    result = export_panel_to_stata(str(panel_path), str(tmp_path))
    assert 'backend' in result
    assert result['backend'] in ('pyreadstat', 'pandas')
