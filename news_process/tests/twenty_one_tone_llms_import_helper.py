"""导入辅助: 从 21_tone_llms.py 中导入 compute_prob_score。

21_tone_llms.py 在模块加载时读取 config.yaml 和初始化全局变量，
直接 import 会触发副作用。此辅助模块通过提取函数源码方式绕过。

替代方案: 直接内联 compute_prob_score 的逻辑用于测试。
"""

import math


def compute_prob_score(sentiment_label: str, confidence: float) -> dict:
    """compute_prob_score 的测试用独立副本。

    与 pipeline/sentiment/tone_llms.py 中的实现完全一致。
    如果修改了原始函数，此处也需同步更新。

    fix(omni-g-tonellms-07/11, 2026-06-11): 同步生产实现 — NaN / 越界
    confidence 显式拒绝 (P3_INV, 全 NaN), 不再静默 clip / 满置信。
    """
    LABEL_MAP = {"正面": "positive", "中性": "neutral", "负面": "negative"}
    cls = LABEL_MAP.get(sentiment_label, "neutral")

    if confidence:
        try:
            _c_float = float(confidence)
        except (TypeError, ValueError):
            _c_float = float('nan')
        if math.isnan(_c_float) or _c_float < 0.0 or _c_float > 1.0:
            _nan = float('nan')
            return {
                "prob_pos": _nan,
                "prob_neu": _nan,
                "prob_neg": _nan,
                "prob_score": _nan,
                "prob_source": "P3_INV",
            }
        c = _c_float
    else:
        c = 0.0
    if c > 0:
        probs = {k: (1.0 - c) / 2.0 for k in ["positive", "neutral", "negative"]}
        probs[cls] = c
        source = "P2"
    else:
        probs = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        probs[cls] = 1.0
        source = "P3"

    score = probs["positive"] - probs["negative"]

    return {
        "prob_pos": probs["positive"],
        "prob_neu": probs["neutral"],
        "prob_neg": probs["negative"],
        "prob_score": round(score, 6),
        "prob_source": source,
    }
