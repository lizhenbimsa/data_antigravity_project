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


def test_nf_headline_frac_ratio_stays_nan_on_zero_nf_rows():
    """零 NF 新闻的 bank-year 行: 比率列 nf_headline_frac 必须保 NaN (非伪 0)。

    回归锁 fix(nf-headline-frac-ratio-nan, 2026-06-25): nf_headline_frac =
    mean(target_bank_in_title) 是【比率】, 在 NF 新闻为空的行上为 0/0 未定义 → 必须
    NaN; 而计数 / 流量列 (nf_n_articles / nf_ln_coverage / nf_media_breadth) 仍正确
    填 0。此前 nf_headline_frac 被错误纳入 merge_to_panel 的 fillna(0) 列表 → 零-NF
    行伪 0, 污染 run_diagnostics 相关系数 (F3 红线: 零报道 ≠ 零比率, Allison 2001 /
    Heckman 1979; 与 encode.py balance_panel 让 *_frac 比率列保 NaN 的契约对齐)。
    """
    import numpy as np

    import news_process.pipeline.falsification.controls as mod
    # 面板两行: A-2018 有 NF 新闻 (在 nf_agg); B-2018 无 NF 新闻 (不在 nf_agg → 零覆盖)
    panel = pd.DataFrame({
        'target_bank': ['A', 'B'],
        'year': [2018, 2018],
        'n_articles': [10, 3],
    })
    nf_agg = pd.DataFrame({
        'target_bank': ['A'],
        'year': [2018],
        'nf_n_articles': [5],
        'nf_ln_coverage': [float(np.log1p(5))],
        'nf_media_breadth': [2],
        'nf_headline_frac': [0.4],
    })
    out = mod.merge_to_panel(panel.copy(), nf_agg)  # 无 ft_dedup_agg → 跨源校验跳过
    b = out[(out['target_bank'] == 'B') & (out['year'] == 2018)].iloc[0]
    # 零 NF 行: 比率列保 NaN (核心断言)
    assert pd.isna(b['nf_headline_frac']), (
        f"零 NF 行 nf_headline_frac 应为 NaN (比率未定义), 实际={b['nf_headline_frac']}")
    # 零 NF 行: 计数 / 流量列仍填 0 (语义正确, 未被本次修复波及)
    assert b['nf_n_articles'] == 0, f"零 NF 行 nf_n_articles 应填 0, 实际={b['nf_n_articles']}"
    assert b['nf_media_breadth'] == 0, f"零 NF 行 nf_media_breadth 应填 0, 实际={b['nf_media_breadth']}"
    # 有 NF 新闻的行: 比率原值完整保留 (未被误置 NaN/0)
    a = out[(out['target_bank'] == 'A') & (out['year'] == 2018)].iloc[0]
    assert abs(a['nf_headline_frac'] - 0.4) < 1e-9, (
        f"有 NF 行 nf_headline_frac 应保 0.4, 实际={a['nf_headline_frac']}")


def test_merge_to_panel_raises_on_cross_source_violation():
    """回归锁 fix(controls-cross-source-fail-loud, 2026-06-25): 去重 fintech 计数 >
    物理 n_articles (构造性不可能的不变量) 时 merge_to_panel 必须 fail-loud raise,
    而非仅 logger.error 后 return (此前静默放行错位面板)。
    """
    import pytest

    import news_process.pipeline.falsification.controls as mod
    panel = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'n_articles': [5]})
    nf_agg = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'nf_n_articles': [2]})
    # 去重 fintech 计数 8 > 物理 n_articles 5 → 跨源不变量被违反
    ft_dedup = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'ft_n_articles_dedup': [8]})
    with pytest.raises(RuntimeError, match='跨源一致性校验失败'):
        mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)


def test_merge_to_panel_passes_when_dedup_within_physical():
    """正例对照: 去重 fintech 计数 ≤ 物理 n_articles 时不 raise, 正常返回面板。"""
    import news_process.pipeline.falsification.controls as mod
    panel = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'n_articles': [10]})
    nf_agg = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'nf_n_articles': [5]})
    ft_dedup = pd.DataFrame({'target_bank': ['A'], 'year': [2018], 'ft_n_articles_dedup': [8]})
    out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
    assert len(out) == 1 and 'fintech_share' in out.columns
