"""v3.5.0 D2 panel 级 8-cell 聚合单元测试。

依据 v3.5.0 D2 panel 8-cell 聚合 §2.1.2 / §4.1 (文档已随 docs/ 删除):
    6 个测试覆盖:
        - bank-year panel 上的 8 个 cell 计数列 (n_articles_cell_1..8_full)
        - 主恒等式: n_articles == Σ_{i=1..8} n_articles_cell_i_full
        - 与 v3.4.0 _indep/_collab 二元后缀的交叉恒等式 (修 C-NEW-2):
            n_articles_indep == n_articles_cell_{1,3,5,7}_full
            n_articles_collab == n_articles_cell_{2,4,6,8}_full
        - 全 NA cell_id 时优雅跳过 (修 F46)
        - 空 panel 边界 (修 F27)
        - df < 1000 篇时设 panel.attrs['D2_small_sample_warning']

依赖: 合成 fixture (按 plan §4.1 F36)。
"""
from __future__ import annotations

import pandas as pd

from news_process.pipeline.panel.encode_collab import (
    aggregate_d2_panel,
    compute_cell_id,
)


def _make_article_df(rows: list[tuple]) -> pd.DataFrame:
    """rows = (target_bank, year, subst_full, locus_full, collab_full) 元组列表。

    生产约定 (见 encode.py:221 + 666): 银行列名是 'target_bank' 而非 'bank',
    测试与生产现状对齐。
    """
    df = pd.DataFrame(
        rows,
        columns=[
            'target_bank', 'year',
            'innovation_substantiveness_full',
            'innovation_locus_full',
            'innovation_collab_mode_full',
        ],
    )
    df['cell_id_full'] = compute_cell_id(df, 'full')
    return df


def _make_panel(article_df: pd.DataFrame) -> pd.DataFrame:
    """构造含 n_articles + indep + collab 计数的扁平 (target_bank, year) panel。

    生产约定: 扁平 DataFrame, target_bank + year 是**列** (非 MultiIndex)。
    """
    grouped = article_df.groupby(['target_bank', 'year']).size().reset_index(name='n_articles')
    panel = grouped.copy()
    panel_idx = pd.MultiIndex.from_frame(panel[['target_bank', 'year']])
    # v3.4.0 二元后缀: cell c=0 (cell 1/3/5/7) → indep; c=1 (cell 2/4/6/8) → collab
    indep_mask = article_df['cell_id_full'].isin([1, 3, 5, 7])
    collab_mask = article_df['cell_id_full'].isin([2, 4, 6, 8])
    indep_counts = (article_df[indep_mask].groupby(['target_bank', 'year']).size()
                    .reindex(panel_idx, fill_value=0).astype('Int32'))
    collab_counts = (article_df[collab_mask].groupby(['target_bank', 'year']).size()
                     .reindex(panel_idx, fill_value=0).astype('Int32'))
    panel['n_articles_indep'] = indep_counts.values
    panel['n_articles_collab'] = collab_counts.values
    return panel


# ----------------------------------------------------------------------------
# Test 1: 生成 8 个 cell 列 + dtype Int32
# ----------------------------------------------------------------------------

def test_panel_creates_8_cell_count_columns():
    """aggregate_d2_panel 应新增 n_articles_cell_{1..8}_full Int32 列。"""
    article_df = _make_article_df([
        ('B1', 2020, '实质性', '底层技术', '自主研发'),  # cell 1
        ('B1', 2020, '实质性', '底层技术', '外部协同'),  # cell 2
        ('B1', 2020, '象征性', '应用场景', '外部协同'),  # cell 8
        ('B2', 2020, '实质性', '应用场景', '自主研发'),  # cell 3
    ])
    panel = _make_panel(article_df)
    aggregate_d2_panel(article_df, panel)

    for i in range(1, 9):
        col = f'n_articles_cell_{i}_full'
        assert col in panel.columns, f"Missing {col}"
        assert panel[col].dtype == 'Int32', f"{col} dtype {panel[col].dtype} != Int32"


# ----------------------------------------------------------------------------
# Test 2: 主恒等式 n_articles == Σ n_articles_cell_i_full
# ----------------------------------------------------------------------------

def test_main_identity_n_articles_equals_sum_of_cells():
    """主恒等式: panel 每行 n_articles == 8 个 cell 计数之和。"""
    article_df = _make_article_df([
        ('B1', 2020, '实质性', '底层技术', '自主研发'),
        ('B1', 2020, '象征性', '应用场景', '外部协同'),
        ('B1', 2020, '实质性', '应用场景', '外部协同'),
        ('B2', 2020, '象征性', '底层技术', '自主研发'),
    ])
    panel = _make_panel(article_df)
    aggregate_d2_panel(article_df, panel)

    cell_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in range(1, 9))
    # 主恒等式对 n_articles > 0 的行成立
    has_news = panel['n_articles'] > 0
    assert (panel.loc[has_news, 'n_articles'] == cell_sum.loc[has_news]).all()


# ----------------------------------------------------------------------------
# Test 3: Cross identity vs v3.4.0 _indep/_collab 后缀 (修 C-NEW-2)
# ----------------------------------------------------------------------------

def test_cross_identity_with_v3_4_0_indep_collab_suffixes():
    """n_articles_indep == cell {1,3,5,7} 之和; n_articles_collab == cell {2,4,6,8} 之和。"""
    article_df = _make_article_df([
        ('B1', 2020, '实质性', '底层技术', '自主研发'),  # cell 1 (indep)
        ('B1', 2020, '实质性', '底层技术', '外部协同'),  # cell 2 (collab)
        ('B1', 2020, '实质性', '应用场景', '自主研发'),  # cell 3 (indep)
        ('B1', 2020, '象征性', '应用场景', '外部协同'),  # cell 8 (collab)
    ])
    panel = _make_panel(article_df)
    diag = aggregate_d2_panel(article_df, panel)

    # 交叉恒等式必须通过 (diag 返回失败计数)
    assert diag.get('indep_cross_fail', 0) == 0
    assert diag.get('collab_cross_fail', 0) == 0


# ----------------------------------------------------------------------------
# Test 4: 全 NA cell_id 时优雅跳过 (修 F46)
# ----------------------------------------------------------------------------

def test_graceful_skip_all_na_cell_id():
    """cell_id_full 全 NA (LLM 列缺失) → 跳过聚合, 不抛异常 (修 F46)。"""
    article_df = pd.DataFrame({
        'target_bank': ['B1', 'B1'],
        'year': [2020, 2020],
        'cell_id_full': pd.Series([pd.NA, pd.NA], dtype='Int8'),
    })
    panel = pd.DataFrame({
        'target_bank': ['B1'],
        'year': [2020],
        'n_articles': [2],
        'n_articles_indep': [0],
        'n_articles_collab': [0],
    })

    diag = aggregate_d2_panel(article_df, panel)
    assert diag.get('cell_aggregation_skipped') is True
    assert diag.get('skip_reason') == 'all_na_cell_id'


# ----------------------------------------------------------------------------
# Test 5: 空 panel 边界 (修 F27)
# ----------------------------------------------------------------------------

def test_empty_panel_graceful_skip():
    """空 panel (0 行) → 优雅跳过, 不抛异常 (修 F27 + F46)。"""
    article_df = _make_article_df([
        ('B1', 2020, '实质性', '底层技术', '自主研发'),
    ])
    # 含必需列但 0 行的空 panel (生产扁平结构)
    panel = pd.DataFrame(columns=['target_bank', 'year', 'n_articles',
                                   'n_articles_indep', 'n_articles_collab'])

    diag = aggregate_d2_panel(article_df, panel)
    assert diag.get('cell_aggregation_skipped') is True
    assert diag.get('skip_reason') == 'empty_panel'


# ----------------------------------------------------------------------------
# Test 6: df < 1000 篇时设 D2_small_sample_warning attr
# ----------------------------------------------------------------------------

def test_d2_small_sample_warning_attr():
    """df.shape[0] < 1000 → panel.attrs['D2_small_sample_warning'] = True, 不阻聚合."""
    # 100 篇文章分布在 2 银行 × 2 年
    rows = []
    for i in range(25):
        rows.append(('B1', 2020, '实质性', '底层技术', '自主研发'))
        rows.append(('B1', 2021, '象征性', '应用场景', '外部协同'))
        rows.append(('B2', 2020, '实质性', '应用场景', '外部协同'))
        rows.append(('B2', 2021, '象征性', '底层技术', '自主研发'))
    article_df = _make_article_df(rows)
    panel = _make_panel(article_df)

    diag = aggregate_d2_panel(article_df, panel)
    # 小样本下聚合仍照常进行
    assert diag.get('cell_aggregation_skipped') is False
    # 已设置 warning attr
    assert panel.attrs.get('D2_small_sample_warning') is True
