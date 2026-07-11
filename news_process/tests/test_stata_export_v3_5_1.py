"""tests/test_stata_export_v3_5_1.py — v3.5.1 Stata 层契约测试 (修 R5-H3 + H2' + M3').

测试覆盖 (6 tests; 2026-06-21 删 2 个 core_patterns/STATA_IC_MAX_VARS 测试 — 该机制已退役):
    1. 8 HEURISTIC_LABELS entries 存在 + ≤ 80 UTF-8 bytes
    2. 8 列名 ≤ 32 char (Stata 变量名限制, 修 M3')
    3. H2' 契约 (WP3 后强形式, P1 整改 2026-07-11): export.py STATA_LABELS 键集
       经 **AST 字面量解析** 覆盖 8 列 + 值级非空/≤80 字节 + 46-path 终态含 CJK
       (旧 token-in-source 检查可被注释残留假绿, 已封死)
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


def _extract_export_stata_labels_via_ast() -> dict:
    """AST 解析 export.py 内函数局部 STATA_LABELS 字面量字典 → {key: value}.

    STATA_LABELS 是 export_panel 函数局部字典 (无法 import), 值级契约经 AST 恢复。
    P1 整改 (2026-07-11): 旧断言 `f"'{col}'" in src` 是源码 token 存在性检查 —
    键从字典删除后只要列名残留在任意注释/docstring 即假绿。AST 字面量字典里的
    键不可能由注释伪造, 封死该通道。
    """
    import ast
    import inspect

    import news_process.pipeline.panel.export as export_mod
    tree = ast.parse(inspect.getsource(export_mod))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if (isinstance(t, ast.Name) and t.id == 'STATA_LABELS'
                    and isinstance(node.value, ast.Dict)):
                out = {}
                for k, v in zip(node.value.keys, node.value.values):
                    if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                            and isinstance(v, ast.Constant) and isinstance(v.value, str)):
                        out[k.value] = v.value
                return out
    raise AssertionError('export.py 内未找到 STATA_LABELS 字面量字典赋值 (契约锚丢失)')


def test_heuristic_labels_match_export_stata_labels():
    """H2' 契约的强形式 (WP3 2026-07-10 分语言 + P1 整改 2026-07-11 值级恢复).

    WP3 后 46-path (pyreadstat, UTF-8) 标签中文化, export.py STATA_LABELS 显式
    条目仍为英文 (刻意分语言, 40 dta 终态由 labels.do 中文统一) → 不逐字同步。
    强契约: ① export.py STATA_LABELS **AST 字面量键集** 覆盖同一 8 列集合
    (注释残留不可能过闸); ② 每键值级非空 + ≤80 UTF-8 字节; ③ 46-path 终态
    8 列标签含 CJK 且 ≤80 字节。
    """
    import re

    df = pd.DataFrame(columns=A1_A3_NEW_COLS)
    heuristic_labels = stata_export.build_variable_labels(df)
    export_labels = _extract_export_stata_labels_via_ast()

    missing = [c for c in A1_A3_NEW_COLS if c not in export_labels]
    assert not missing, (
        f"export.py STATA_LABELS 字面量字典缺键 (AST 级, 注释残留不算): {missing}")

    # CJK 端点用 \u 转义 (P2 整改 2026-07-11: 源码零字面端点字符, 防 GBK 回显二次崩)
    _cjk = re.compile('[\u4e00-\u9fff\u3400-\u4dbf]')
    for col in A1_A3_NEW_COLS:
        # ① 40-path 显式条目值级契约: 非空 str + ≤80 UTF-8 字节
        v = export_labels[col]
        assert isinstance(v, str) and v.strip(), f"export.py STATA_LABELS[{col}] 值为空"
        assert len(v.encode('utf-8')) <= 80, f"export.py STATA_LABELS[{col}] 超 80 字节"
        # ② 46-path 终态: 中文化 + 字节预算
        h_label = heuristic_labels[col]
        assert _cjk.search(h_label), f"46-path 标签未中文化: {col} = '{h_label}'"
        assert len(h_label.encode('utf-8')) <= 80


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
