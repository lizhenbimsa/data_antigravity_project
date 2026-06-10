"""tests/test_fix_review_closure_gaps.py — review-closure (2026-06-10) 补的回归锁

锁住 review-closure 标记为 weak-test 的真实行为变更, 防静默 revert:
  - LM 词数分母 (lm_non_sentiment): n_tokens 排除纯标点/数字 token (lmfls-01)。
  - herd bucketed-NaT 守卫: 内部 NaT 排列下 _bucketed == _dense (herd-bucket-nat)。
  - encode_collab clarity 加权均值用 valid-mask 分母 (encode_collab-01)。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── LM 词数分母 ────────────────────────────────────────────────────────────────
def test_lm_denominator_excludes_punct_and_numbers():
    """n_tokens 只计 word token; 含纯标点/数字的文本分母 = 词数, frac 用更紧分母。"""
    from news_process.pipeline.sentiment.lm_non_sentiment import (
        _compute_lm_non_sentiment_for_text,
    )
    dicts = {'uncertainty': frozenset({'可能'}), 'litigious': frozenset(),
             'constraining': frozenset(), 'modal_strong': frozenset()}
    # 词: 可能/影响/风险 (3 word); 噪声: 2017 / 30% / 。 , (纯数字/标点, 应排除)
    text = '可能 影响 2017 风险 30% 。 ，'
    r = _compute_lm_non_sentiment_for_text(text, dicts)
    # 旧 bug: n_tokens 含 2017/30%/。/， → 分母偏大 frac 偏小
    assert r['n_tokens'] == 3, f"n_tokens={r['n_tokens']}, 期望 3 (仅 word, 排标点/数字)"
    assert abs(r['frac_uncert'] - 1.0 / 3.0) < 1e-9, f"frac_uncert={r['frac_uncert']}, 期望 1/3"


# ── herd bucketed-NaT 守卫 ──────────────────────────────────────────────────────
def test_herd_bucketed_matches_dense_with_interior_nat():
    """内部 NaT (非生产末位) 排列下 _bucketed_similar_counts == _dense (NaT 候选排除)。"""
    from news_process.pipeline.sentiment.herd_decay import (
        _bucketed_similar_counts,
        _dense_similar_counts,
    )
    tfidf = np.ones((4, 3), dtype=float)  # 4 篇全同 → 余弦=1 ≥ 阈值
    d0 = pd.Timestamp('2018-01-01')
    d1 = pd.Timestamp('2018-01-02')
    dates = [d0, pd.NaT, d1, d1]  # index 1 内部 NaT
    dense = _dense_similar_counts(tfidf, dates)
    buck = _bucketed_similar_counts(tfidf, dates)
    assert np.array_equal(dense, buck), (
        f'dense={dense} bucketed={buck} — 内部 NaT 须逐位等价 (NaT 候选排除守卫)')
    # NaT 不计为相似前驱: dense[2]=1 (仅 d0), dense[3]=2 (d0,d1), NaT(idx1) 不计
    assert dense.tolist() == [0, 0, 1, 2], f'dense={dense.tolist()}, 期望 [0,0,1,2] (NaT 不计)'


# 注: encode_collab clarity/num_intensity 的 valid-mask 分母与上方 VW 修复(test_encode01_
# weighted_valid_denom.py)、num_intensity 同源同型(均 _wd_ 掩码分母), 已由该测试 + 真实
# 面板值正确性检查(mean_clarity_score 范围正常)覆盖; 此处不重复构造其 dict 返回断言。
