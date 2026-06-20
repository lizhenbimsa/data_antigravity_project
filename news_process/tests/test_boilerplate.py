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
