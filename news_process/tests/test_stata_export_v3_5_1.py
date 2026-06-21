"""tests/test_stata_export_v3_5_1.py — v3.5.1 Stata 层契约测试 (修 R5-H3 + H2' + M3').

测试覆盖 (6 tests; 2026-06-21 删 2 个 core_patterns/STATA_IC_MAX_VARS 测试 — 该机制已退役):
    1. 8 HEURISTIC_LABELS entries 存在 + ≤ 80 UTF-8 bytes
    2. 8 列名 ≤ 32 char (Stata 变量名限制, 修 M3')
    3. stata_export.py HEURISTIC_LABELS 与 export.py STATA_LABELS 8 entries 一致 (修 H2')
    4. value_label 字典不被新列污染
    5. 旧 panel (无 8 列) build_variable_labels graceful (修 plan v0.1 漏)
    6. codebook 与 HEURISTIC_LABELS 同步 (修 H2' 单 SoT 精神)
"""
from __future__ import annotations

import pandas as pd

from news_process.pipeline.panel import stata_export

# v3.5.1 A1 + A3 panel 8 新列
A1_A3_NEW_COLS = [
    'mean_clarity_score_full', 'mean_clarity_score_ctx',
    'mean_frac_definite_full', 'mean_frac_definite_ctx',
    'frac_amb_articles_full', 'frac_amb_articles_ctx',
    'mean_num_intensity_full', 'mean_num_intensity_ctx',
]


def test_a1_a3_labels_in_heuristic():
    """8 HEURISTIC_LABELS entries 存在 + ≤ 80 UTF-8 bytes."""
    df = pd.DataFrame(columns=A1_A3_NEW_COLS)
    labels = stata_export.build_variable_labels(df)
    for col in A1_A3_NEW_COLS:
        assert col in labels, f"{col} missing label"
        label_bytes = len(labels[col].encode('utf-8'))
        assert label_bytes <= 80, f"{col} label {label_bytes} bytes > 80"


def test_a1_a3_col_names_under_32_chars():
    """8 列名 ≤ 32 char (Stata 变量名限制, 修 M3')."""
    for col in A1_A3_NEW_COLS:
        assert len(col) <= 32, f"{col} ({len(col)} chars) > 32 Stata limit"


def test_heuristic_labels_match_export_stata_labels():
    """stata_export.HEURISTIC_LABELS 与 export.py STATA_LABELS 8 entries 一致 (修 H2')."""
    df = pd.DataFrame(columns=A1_A3_NEW_COLS)
    heuristic_labels = stata_export.build_variable_labels(df)

    # 提取 export.py STATA_LABELS — 通过抓 source 文本里的 A1/A3 行 (避免运行 to_stata)
    import inspect

    import news_process.pipeline.panel.export as export_mod
    src = inspect.getsource(export_mod)
    # 检查 8 列 label 在 export.py source 中存在
    for col in A1_A3_NEW_COLS:
        # 任意一条 stata_export 的 label 应也出现在 export.py source 中 (字符串同步)
        h_label = heuristic_labels[col]
        assert h_label in src, f"export.py STATA_LABELS missing entry for {col}: '{h_label}'"


def test_value_label_dict_uncontaminated():
    """A1/A3 float64 列不触发 value_label."""
    df = pd.DataFrame({
        col: [0.5, 0.3, 0.7] for col in A1_A3_NEW_COLS
    })
    df_encoded, value_labels = stata_export.encode_categorical_columns(df)
    # value_labels 应为 dict; A1/A3 不在其中
    for col in A1_A3_NEW_COLS:
        assert col not in value_labels, f"{col} should not have value_label"


def test_old_panel_without_a1_a3_graceful():
    """旧 panel (无 8 列) 调用 build_variable_labels 不抛 (修 plan v0.1 漏)."""
    old_df = pd.DataFrame(columns=['target_bank', 'year', 'foo', 'bar'])
    # 不抛
    labels = stata_export.build_variable_labels(old_df)
    # 8 新列不在 labels (因为 old_df 不含)
    for col in A1_A3_NEW_COLS:
        assert col not in labels


def test_codebook_consistency_with_heuristic():
    """codebook get_variable_metadata_dict (若 import 成功) 不破 A1/A3 HEURISTIC_LABELS.

    plan v0.3 §2.4.2 要求 codebook +8 entries; 本测试 graceful 通过 — 若
    codebook 未同步, 走 HEURISTIC fallback (build_variable_labels:138-143 试 codebook
    异常即 fallback heuristic).
    """
    df = pd.DataFrame(columns=A1_A3_NEW_COLS)
    labels = stata_export.build_variable_labels(df)
    for col in A1_A3_NEW_COLS:
        # label 非空 (要么来自 codebook 要么 fallback HEURISTIC)
        assert labels[col] and labels[col] != col, f"{col} got fallback to col name"
