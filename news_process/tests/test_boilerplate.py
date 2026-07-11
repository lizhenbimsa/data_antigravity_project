"""tests/test_boilerplate.py — 跨文档套话比率 (WS-B2) 单测.

断言稳健性质 (取值域 / 确定性 / SAFE 降级), 不绑定具体 n-gram 结果.
"""
from __future__ import annotations

import math

import pandas as pd

from news_process.pipeline.sentiment.boilerplate import (
    OUT_COL,
    compute_boilerplate_ratios,
    enrich_with_boilerplate,
)


def _corpus():
    # 含大量重复套话短语 ("本报讯记者报道") 的语料, 保证套话集非空
    common = "本报讯记者报道某银行金融科技合作"
    return [common + f"项目第{i}期进展顺利金额若干亿元。" for i in range(20)]


def test_range_and_determinism():
    texts = _corpus()
    r1 = compute_boilerplate_ratios(texts)
    r2 = compute_boilerplate_ratios(texts)
    assert len(r1) == len(texts)
    # 取值域 [0,1] ∪ nan
    assert all(math.isnan(v) or 0.0 <= v <= 1.0 for v in r1)
    # 确定性 (sorted vocab + 固定参数, 无 HASHSEED 依赖) → 两次逐值相等
    assert all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(r1, r2))


def test_safe_empty_corpus_all_nan():
    # 全空/哨兵 → 全 nan (SAFE 降级, 不崩)
    r = compute_boilerplate_ratios(["", "   ", "nan", "<NA>"])
    assert len(r) == 4
    assert all(math.isnan(v) for v in r)


def test_enrich_adds_single_track_column():
    df = pd.DataFrame({'content_full': _corpus()})
    out = enrich_with_boilerplate(df)
    assert OUT_COL in out.columns
    assert OUT_COL == 'boilerplate_phrase_ratio_full'  # 单轨命名锁定
    assert all(math.isnan(v) or 0.0 <= v <= 1.0 for v in out[OUT_COL])


def test_enrich_missing_text_col_graceful():
    df = pd.DataFrame({'other': [1, 2, 3]})
    out = enrich_with_boilerplate(df)
    assert OUT_COL in out.columns
    assert out[OUT_COL].isna().all()  # 缺列 → 全 nan graceful


# ── 三轨化 (2026-07-03, ROBUSTNESS_GAP_BACKFILL §4 WP-C) ──


def test_enrich_adds_ctx_ss_robustness_tracks():
    texts = _corpus()
    df = pd.DataFrame({
        'content_full': texts,
        'content_ctx': texts[::-1],
        'content_ss': texts,
    })
    out = enrich_with_boilerplate(df)
    for trk in ('full', 'ctx', 'ss'):
        col = f'boilerplate_phrase_ratio_{trk}'
        assert col in out.columns, f'缺三轨列 {col}'
        assert all(math.isnan(v) or 0.0 <= v <= 1.0 for v in out[col])
    # ss 文本 == full 文本 → 独立建集结果逐值相等 (各轨独立两遍的可复现性)
    assert all(
        (math.isnan(a) and math.isnan(b)) or a == b
        for a, b in zip(out['boilerplate_phrase_ratio_full'],
                        out['boilerplate_phrase_ratio_ss']))


def test_full_canonical_unchanged_by_track_extension():
    # canonical 锚: 三轨化后 full 轨数值与直接单轨计算逐字节一致
    texts = _corpus()
    direct = compute_boilerplate_ratios(texts)
    df = pd.DataFrame({'content_full': texts, 'content_ctx': texts, 'content_ss': texts})
    out = enrich_with_boilerplate(df)
    assert all(
        (math.isnan(a) and math.isnan(b)) or a == b
        for a, b in zip(direct, out[OUT_COL]))


def test_missing_ctx_ss_graceful_per_track():
    # ctx/ss 缺文本列 → 该轨全 nan, full 轨照常 (逐轨独立降级)
    df = pd.DataFrame({'content_full': _corpus()})
    out = enrich_with_boilerplate(df)
    assert not out['boilerplate_phrase_ratio_full'].isna().all()
    assert out['boilerplate_phrase_ratio_ctx'].isna().all()
    assert out['boilerplate_phrase_ratio_ss'].isna().all()


def test_panel_agg_three_tracks():
    from news_process.pipeline.panel.encode import build_aggregation_dict
    agg = build_aggregation_dict()
    for trk in ('full', 'ctx', 'ss'):
        assert agg[f'avg_boilerplate_{trk}'] == (f'boilerplate_phrase_ratio_{trk}', 'mean')
        assert len(f'avg_boilerplate_{trk}') <= 32


def test_codebook_and_stata_labels_three_tracks():
    from news_process.pipeline.panel import stata_export as se
    from news_process.pipeline.panel.codebook import get_variable_metadata_dict
    meta = get_variable_metadata_dict()
    # WP3 (2026-07-10) 标签中文化: full 条目 label 改中文 (轨后缀=全文轨)
    assert meta['avg_boilerplate_full'].label == '跨文档套话比率(全文轨)'
    for trk in ('ctx', 'ss'):
        assert f'avg_boilerplate_{trk}' in meta
    import pandas as pd_
    cols = [f'avg_boilerplate_{t}' for t in ('full', 'ctx', 'ss')]
    labels = se.build_variable_labels(pd_.DataFrame({c: [0.0] for c in cols}))
    for c in cols:
        assert labels[c] != c and len(labels[c].encode('utf-8')) <= 80
