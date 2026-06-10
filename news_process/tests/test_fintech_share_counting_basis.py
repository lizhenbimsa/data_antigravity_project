"""tests/test_fintech_share_counting_basis.py — fintech_share 计数基修复回归锁

fintech_share 分子改用去重口径 ft_n_articles_dedup (与分母 NF 同基), 替代物理
n_articles。ft_dedup_agg=None → 回退物理 (向后兼容)。fix metric-audit 2026-06-10。
"""
from __future__ import annotations

import pandas as pd


def _panel_nf():
    panel = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'n_articles': [10]})
    nf_agg = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'nf_n_articles': [5]})
    return panel, nf_agg


def test_fintech_share_uses_deduped_numerator():
    """提供 ft_dedup_agg → fintech_share = ft_dedup / (ft_dedup + nf), 同基。"""
    import news_process.pipeline.falsification.controls as mod
    panel, nf_agg = _panel_nf()
    # 物理 n_articles=10 但去重 fintech 篇数=8 (2 篇重复); nf=5
    ft_dedup = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'ft_n_articles_dedup': [8]})
    out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
    got = out['fintech_share'].iloc[0]
    # 正确(去重同基) = 8/(8+5) = 0.6154 ; 旧物理 bug = 10/(10+5) = 0.6667
    assert abs(got - 8.0 / 13.0) < 1e-9, f'fintech_share={got}, 期望 8/13 (去重同基), 非 10/15 (物理)'


def test_fintech_share_fallback_physical_when_no_dedup():
    """ft_dedup_agg=None → 回退旧物理口径 (向后兼容旧调用/测试)。"""
    import news_process.pipeline.falsification.controls as mod
    panel, nf_agg = _panel_nf()
    out = mod.merge_to_panel(panel.copy(), nf_agg)  # 无 ft_dedup_agg
    got = out['fintech_share'].iloc[0]
    # 回退物理 = n_articles/(n_articles+nf) = 10/(10+5) = 0.6667
    assert abs(got - 10.0 / 15.0) < 1e-9, f'fallback fintech_share={got}, 期望 10/15 (物理回退)'


def test_build_non_fintech_exposes_dedup_count():
    """build_non_fintech 经 df_nf.attrs 暴露去重 fintech 篇数 (供 fintech_share 分子)。"""
    import news_process.pipeline.falsification.controls as mod
    # df_art: A-2018 有 3 行, 其中 2 行 (target_bank,标题,日期) 重复 → 去重后 2 篇
    df_art = pd.DataFrame({
        'target_bank': ['A', 'A', 'A'],
        '标题': ['t1', 't1', 't2'],            # t1 重复
        '日期': ['2018-01-01', '2018-01-01', '2018-02-02'],
        'year': [2018, 2018, 2018],
    })
    df_full = pd.DataFrame({
        'target_bank': ['A', 'A', 'A', 'A'],
        '标题': ['t1', 't2', 't3', 't4'],
        '日期': ['2018-01-01', '2018-02-02', '2018-03-03', '2018-04-04'],
        'year': [2018, 2018, 2018, 2018],
    })
    df_nf = mod.build_non_fintech(df_full, df_art)
    ft = df_nf.attrs.get('ft_dedup_agg')
    assert ft is not None and 'ft_n_articles_dedup' in ft.columns
    # A-2018: 去重 fintech 篇数 = 2 (t1 去重, t2)
    row = ft[(ft['target_bank'] == 'A') & (ft['year'] == 2018)]
    assert int(row['ft_n_articles_dedup'].iloc[0]) == 2
