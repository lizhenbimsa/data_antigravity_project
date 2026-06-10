"""tests/test_encode01_weighted_valid_denom.py — encode-01 修复回归锁

VW/MW/HW 加权语调的 **LLM 族** 分母改用 valid-mask 权重和 (Σ weight over valid),
消除 valid-only 分子 ÷ physical 分母的向零衰减; **dict 族不改** (score=0 非 NA,
分子分母同全物理域, mask 会反向失配)。fix metric-audit 2026-06-10。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _agg(df):
    from news_process.pipeline.panel import encode
    from news_process.pipeline.panel.runner import _build_llm_valid_masked_weights
    df = df.copy()
    w = df['mention_density'].fillna(0)
    # 模拟 runner 3b: 加权分子 + LLM 族 valid-mask 权重
    df['llm_vote_score_w_full'] = df['llm_vote_score_full'] * w
    for k, v in _build_llm_valid_masked_weights(df, w, 'vw').items():
        df[k] = v
    return encode.aggregate_panel(df.copy())


def test_masked_weight_excludes_invalid_rows():
    """_build_llm_valid_masked_weights: weight 仅在 score 有效行保留 (无效 → NaN)。"""
    from news_process.pipeline.panel.runner import _build_llm_valid_masked_weights
    df = pd.DataFrame({
        'llm_vote_score_full': pd.array([1, -1, pd.NA], dtype='Int8'),
        'llm_vote_score_ctx': pd.array([1, pd.NA, pd.NA], dtype='Int8'),
    })
    w = pd.Series([2.0, 1.0, 5.0])
    out = _build_llm_valid_masked_weights(df, w, 'vw')
    # full: art3 无效 → masked weight = [2,1,NaN], sum=3
    assert np.isnan(out['_wd_vw_llm_full'].iloc[2])
    assert out['_wd_vw_llm_full'].iloc[:2].tolist() == [2.0, 1.0]
    # ctx: art2,3 无效 → [2,NaN,NaN], sum=2
    assert out['_wd_vw_llm_ctx'].notna().sum() == 1


def test_vw_llm_tone_uses_valid_denominator():
    """LLM 族 VW 语调 = Σ_valid(w·score) / Σ_valid(w), 非 physical 分母。"""
    # 3 篇: art1(score=1,w=2) art2(score=-1,w=1) art3(无效,w=5)
    # 正确 VW = (1*2 + -1*1)/(2+1) = 1/3 ; 旧 bug = 1/(2+1+5) = 1/8
    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'A'], 'year': [2018, 2018, 2018],
        'llm_vote_score_full': pd.array([1, -1, pd.NA], dtype='Int8'),
        'mention_density': [2.0, 1.0, 5.0],
    })
    pan = _agg(df)
    got = pan['llm_vote_tone_vw_full'].iloc[0]
    assert abs(got - 1.0 / 3.0) < 1e-9, f'VW LLM tone={got}, 期望 1/3 (valid 分母 3, 非 physical 8)'


def test_vw_dict_tone_keeps_physical_denominator():
    """dict 族 VW 语调仍用 physical 分母 (score=0 非 NA, 不该 mask; 防反向失配)。"""
    from news_process.pipeline.panel import encode
    from news_process.pipeline.panel.runner import _build_llm_valid_masked_weights
    # 词典 score: art3 词典命中 0 (非 NA), 仍是真实观测 → 分母含其权重
    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'A'], 'year': [2018, 2018, 2018],
        'llm_vote_score_full': pd.array([1, -1, pd.NA], dtype='Int8'),
        'jiang_2021_score_full': [1.0, -1.0, 0.0],   # dict: art3=0 (非 NA)
        'mention_density': [2.0, 1.0, 5.0],
    })
    df = df.copy()
    w = df['mention_density'].fillna(0)
    df['jiang_2021_score_w_full'] = df['jiang_2021_score_full'] * w
    for k, v in _build_llm_valid_masked_weights(df, w, 'vw').items():
        df[k] = v
    pan = encode.aggregate_panel(df.copy())
    # dict VW = (1*2 + -1*1 + 0*5)/(2+1+5) = 1/8 (physical 分母, art3 真零观测)
    got = pan['jiang_2021_tone_vw_full'].iloc[0]
    assert abs(got - 1.0 / 8.0) < 1e-9, f'dict VW tone={got}, 期望 1/8 (physical 分母, dict 不 mask)'
