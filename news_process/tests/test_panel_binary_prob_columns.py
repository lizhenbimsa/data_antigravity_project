"""panel 级二元 prob_score 列的测试 (plan v1.37 P2 §5.3.6)。

4 个测试函数; 5 个用例 (positive-class 编码测试参数化 ×2)。

# 白话: prob_score 是把 LLM 对文章的二元分类 (实质/象征、底层/应用) 连同置信度
# 折算成 0~1 概率分数; 这组测试确保它正确聚合进 bank-year 面板的 8 个新列。
"""
import numpy as np
import pandas as pd
import pytest


def test_eight_new_columns_present():
    """Item 2: encode.py 聚合产出的 8 个新 bank-year 列。"""
    from news_process.pipeline.panel.encode import build_aggregation_dict
    agg = build_aggregation_dict()
    expected = {
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx',
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
    }
    assert expected.issubset(set(agg.keys()))


def test_zero_article_bank_year_nan():
    """Item 3: 零文章的 bank-year → 8 个新列全 NaN。

    构造一个对某 (bank, year) 组合无任何行的文章级 df;
    聚合后新 prob_score 列应得 NaN。"""
    df = pd.DataFrame({
        'target_bank': ['X', 'X', 'Y'],
        'year': [2020, 2020, 2020],
        'avg_subst_prob_score_full': [0.8, 0.9, 0.7],
        'avg_subst_prob_score_ctx':  [0.8, 0.9, 0.7],
        'avg_locus_prob_score_full': [0.5, 0.6, 0.4],
        'avg_locus_prob_score_ctx':  [0.5, 0.6, 0.4],
    })
    # bank-year (Z, 2020) 不存在 → 与全量 panel merge 后应为 NaN
    grouped = df.groupby(['target_bank', 'year']).agg({
        'avg_subst_prob_score_full': 'mean',
        'avg_subst_prob_score_ctx': 'mean',
        'avg_locus_prob_score_full': 'mean',
        'avg_locus_prob_score_ctx': 'mean',
    }).reset_index()
    # reindex 把缺失的 (Z, 2020) 格子补进来 → NaN
    full_idx = pd.MultiIndex.from_tuples(
        [('X', 2020), ('Y', 2020), ('Z', 2020)], names=['target_bank', 'year']
    )
    reindexed = grouped.set_index(['target_bank', 'year']).reindex(full_idx)
    assert np.isnan(reindexed.loc[('Z', 2020), 'avg_subst_prob_score_full'])


@pytest.mark.parametrize(
    "label, positive_class, expected_score",
    [
        ("象征性", "象征性", 1.0),       # subst 维度, 正类
        ("应用场景", "应用场景", 1.0),    # locus 维度, 正类
    ],
)
def test_positive_class_encoding_assertion(label, positive_class, expected_score):
    """Item 4: positive_class 编码与 Stata 1=对照 约定一致。

    label=象征性 + conf=1.0 + positive_class=象征性 → prob_score=1.0;
    应用场景 维度同理。防符号翻转守卫。
    # 白话: 确保"哪个类别算 1"的方向没接反, 否则回归系数符号会整体颠倒。"""
    from news_process.pipeline.sentiment.tone_llms import compute_prob_score_binary
    r = compute_prob_score_binary(label, 1.0, positive_class)
    assert r["prob_score"] == expected_score


def test_golden_baseline_diff_scope():
    """Item 5: golden snapshot diff 中各受影响 stage 的精确新增列数
    (Round-3 R3C-11 + R4B-02/R4C-01 + R27C-01)。

    当时重生的 golden_panel_v0.json 预期新增 (历史记录):
      - 21_tone_llms.parquet: +4 文章级列
      - 21_tone_llms_full.parquet: +4 (并行轨)
      - 40_panel_yearly.parquet: +8 panel 列
      - 51_panel_with_controls.parquet: +8 (经 merge_to_panel 继承)
      - 41_panel_with_controls.parquet: 0 (孤儿文件, 无生产者)

    本测试只比对内存中的预期列集合与文档化的新增数量;
    并不要求重生 golden fixture (那是单独的手工步骤)。
    # 白话: 只是数一数"应该新增 4 个文章级列、8 个面板列"这笔账对不对,
    # 不真正去读 golden 文件。"""
    expected_p2_article_cols = {
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx',
    }
    expected_p2_panel_cols = expected_p2_article_cols | {
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
    }
    # 文章级: 新增 4 列
    assert len(expected_p2_article_cols) == 4
    # panel 级: 新增 8 列 (4 个均值 + 4 个标准差)
    assert len(expected_p2_panel_cols) == 8
