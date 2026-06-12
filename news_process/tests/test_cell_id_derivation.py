"""v3.5.0 D2 文章级 cell_id 派生单元测试。

依据 v3.5.0 D2 article-level cell_id derivation §2.1.1 / §4.1 (文档已随 docs/ 删除):
    8 个测试覆盖:
        - 编号公式 (cell_id = subst*4 + locus*2 + collab + 1 ∈ {1..8})
        - dirty label 防御 (空白 / 全角 / 换行 normalize, 修 F32)
        - NA 传播 (任一维 NaN → cell_id NA)
        - Int8 nullable dtype
        - 缺列守卫 (修 F28: 缺列返回全 NA, 不抛 KeyError)
        - NaN dtype 安全 (修 F49)
        - 边界值 (cell 1 三维全 baseline, cell 8 三维全 contrast)
        - 模块级 helper `_normalize_label` 可独立测试 (修 F47)

依赖: 合成小 fixture (按 plan §4.1 F36 test fixture 策略); 不依赖真实 LLM 输出。
"""
from __future__ import annotations

import pandas as pd

from news_process.pipeline.panel.encode_collab import (
    CELL_LABEL_MAP,
    VALID_COLLAB,
    VALID_LOCUS,
    VALID_SUBST,
    _normalize_label,
    compute_cell_id,
)


def _make_df(rows: list[tuple]) -> pd.DataFrame:
    """Helper: 用 (subst_full, locus_full, collab_full) 行构造 df。"""
    return pd.DataFrame(
        rows,
        columns=[
            'innovation_substantiveness_full',
            'innovation_locus_full',
            'innovation_collab_mode_full',
        ],
    )


# ----------------------------------------------------------------------------
# Test 1: cell_id 编号公式 (cell 1 vs cell 8 等关键 corner)
# ----------------------------------------------------------------------------

def test_cell_id_encoding_formula_baseline_to_contrast():
    """8 个 cell 编号 = subst*4 + locus*2 + collab + 1, cell 1 / cell 8 边界."""
    df = _make_df([
        ('实质性', '底层技术', '自主研发'),   # cell 1: (0,0,0) baseline
        ('实质性', '底层技术', '外部协同'),   # cell 2: (0,0,1)
        ('实质性', '应用场景', '自主研发'),   # cell 3: (0,1,0)
        ('实质性', '应用场景', '外部协同'),   # cell 4: (0,1,1)
        ('象征性', '底层技术', '自主研发'),   # cell 5: (1,0,0)
        ('象征性', '底层技术', '外部协同'),   # cell 6: (1,0,1)
        ('象征性', '应用场景', '自主研发'),   # cell 7: (1,1,0)
        ('象征性', '应用场景', '外部协同'),   # cell 8: (1,1,1) contrast
    ])
    cell = compute_cell_id(df, 'full')
    assert cell.tolist() == [1, 2, 3, 4, 5, 6, 7, 8]
    assert cell.dtype == 'Int8', f"Expected Int8, got {cell.dtype}"


# ----------------------------------------------------------------------------
# Test 2: CELL_LABEL_MAP 与公式 round-trip 一致
# ----------------------------------------------------------------------------

def test_cell_label_map_matches_formula():
    """CELL_LABEL_MAP 的 8 个条目应正确描述 (s,l,c) cell 组合。"""
    assert len(CELL_LABEL_MAP) == 8
    # cell 1 = baseline 三维全 0
    assert CELL_LABEL_MAP[1] == '实质性·底层技术·自主研发'
    # cell 8 = contrast 三维全 1
    assert CELL_LABEL_MAP[8] == '象征性·应用场景·外部协同'


# ----------------------------------------------------------------------------
# Test 3: dirty label 防御 — trailing whitespace / 全角空格 / newline
# ----------------------------------------------------------------------------

def test_dirty_label_whitespace_normalize_to_cell_1():
    """v3.4.0 stage 21 LLM 输出 '实质性 ', '实质性　' 等 noise 应 normalize 后归类 cell 1 (修 F32)."""
    df = _make_df([
        ('实质性 ', '底层技术', '自主研发'),       # 尾部 ASCII 空格
        ('实质性　', '底层技术', '自主研发'),  # 尾部全角空格
        ('实质性\n', '底层技术', '自主研发'),       # 尾部换行
        (' 实质性', '底层技术', '自主研发'),       # 首部空格
    ])
    cell = compute_cell_id(df, 'full')
    assert cell.tolist() == [1, 1, 1, 1], (
        f"whitespace 规范化后应全归 cell 1, got {cell.tolist()}"
    )


# ----------------------------------------------------------------------------
# Test 4: 未知 / dirty label → pd.NA
# ----------------------------------------------------------------------------

def test_unknown_label_yields_na():
    """v3.4.0 encode.py:980 已暴露的 '非预期 collab_mode 值' 应归 NA (修 M3 + F32)."""
    df = _make_df([
        ('未知', '底层技术', '自主研发'),     # 未知 subst 标签
        ('实质性', 'unknown locus', '自主研发'),  # 未知 locus
        ('实质性', '底层技术', ''),            # collab 为空字符串
    ])
    cell = compute_cell_id(df, 'full')
    # 3 行均应为 NA, 因至少一维非法
    assert cell.isna().all(), f"Unknown labels should produce NA, got {cell.tolist()}"


# ----------------------------------------------------------------------------
# Test 5: NaN 传播 — 任一维 NaN → cell_id NA
# ----------------------------------------------------------------------------

def test_nan_propagation_any_dim_nan_yields_na():
    """三维任一为 NaN → cell_id NA (依 plan §2.1.1 docstring)。"""
    df = _make_df([
        (None, '底层技术', '自主研发'),        # subst NaN
        ('实质性', None, '自主研发'),          # locus NaN
        ('实质性', '底层技术', None),          # collab NaN
        ('实质性', '底层技术', '自主研发'),    # 有效 → cell 1
    ])
    cell = compute_cell_id(df, 'full')
    assert cell.isna().tolist()[:3] == [True, True, True]
    assert cell.iloc[3] == 1


# ----------------------------------------------------------------------------
# Test 6: Missing column guard — 修 F28, 不抛 KeyError
# ----------------------------------------------------------------------------

def test_missing_column_returns_all_na_no_keyerror():
    """缺列 (e.g., v3.4.0 hotfix 移除 ctx 列) → 全 NA Int8 + warning, 不 raise."""
    # df 不含任何 innovation_*_ctx 列
    df = _make_df([
        ('实质性', '底层技术', '自主研发'),
        ('象征性', '应用场景', '外部协同'),
    ])
    cell_ctx = compute_cell_id(df, 'ctx')  # ctx 列缺失
    assert cell_ctx.isna().all(), "缺 ctx 列应返回全 NA"
    assert cell_ctx.dtype == 'Int8'
    assert len(cell_ctx) == len(df)


# ----------------------------------------------------------------------------
# Test 7: _normalize_label NaN dtype safety (修 F49) — module-level helper
# ----------------------------------------------------------------------------

def test_normalize_label_nan_dtype_safety():
    """`_normalize_label` 接受全 NaN Series (float64 dtype) 直接 return, 不 .str accessor crash."""
    # object dtype 的全 NaN Series
    s_object = pd.Series([None, None, None], dtype=object)
    result_object = _normalize_label(s_object)
    assert result_object.isna().all(), "all-NaN object series should preserve NaN"

    # float64 dtype (非 object) 的全 NaN Series — F49 NaN dtype 守卫
    s_float = pd.Series([float('nan'), float('nan')], dtype='float64')
    result_float = _normalize_label(s_float)
    # F49 守卫: 非 object dtype → 原样返回 Series
    assert result_float.dtype == 'float64'
    assert result_float.isna().all()


# ----------------------------------------------------------------------------
# Test 8: VALID_* 集合各含 2 个元素 (二元维度)
# ----------------------------------------------------------------------------

def test_valid_label_sets_binary():
    """VALID_SUBST / LOCUS / COLLAB 各 2 元素 (binary dim assumption)."""
    assert {'实质性', '象征性'} == VALID_SUBST
    assert {'底层技术', '应用场景'} == VALID_LOCUS
    assert {'自主研发', '外部协同'} == VALID_COLLAB
