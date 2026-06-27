"""test_gemini_semantic_validity — gemini 余弦语义有效性绑定门 (v3.14.0, 执行计划 §6/§13)。

背景: gemini-embedding-2-preview 经 yunwu OpenAI-compat 路径**无法指定** `SEMANTIC_SIMILARITY`
task_type (实测返回单位归一向量, 余弦=点积形式可用), 故不能假设其余弦语义 = text-embedding-3-small。
本门用**两 co-primary 的跨厂商一致性**作语义有效性证据: 若 gemini(无后缀) 与 large(`_lg`) 在同一批
文本上的余弦测度高度一致 (Spearman ρ ≥ 0.80, ≥500 对), 则 gemini 余弦语义有效。

⚠ 绑定阈值 (替代不可证伪的"抽检"): ρ ≥ 0.80 / n ≥ 500。
⚠ DEFERRED: 本机无生产语料 + gemini/large 缓存空 → 盘上 panel 无非 NaN 的 co-primary 余弦对时
   skip; 须在生产语料机播种 gemini+large 缓存、重生 panel 后此门方生效。
"""
from __future__ import annotations

import os

import pytest

# 成对的 (无后缀, _lg) 余弦/相似度列候选 (取 panel 中实际存在的前若干对)。
_PAIR_CANDIDATES = [
    ("policy_cosine_sim_full", "policy_cosine_sim_lg_full"),
    ("policy_cosine_sim_ctx", "policy_cosine_sim_lg_ctx"),
    ("auth_sim_emb_full", "auth_sim_emb_lg_full"),
    ("strat_sim_max_emb", "strat_sim_max_emb_lg"),
    ("centroid_diff_emb", "centroid_diff_emb_lg"),
    ("benefit_mean_full", "benefit_mean_lg_full"),
    ("fintech_intensity_score_full", "fintech_intensity_score_lg_full"),
    ("semantic_staleness_full", "semantic_staleness_full_lg"),
]

RHO_THRESHOLD = 0.80
MIN_PAIRS = 500


def _load_panel():
    import pandas as pd  # noqa: PLC0415

    from news_process.core.config import load_config  # noqa: PLC0415
    out_dir = load_config()["paths"]["output_dir"]
    for fn in ("51_panel_with_controls.parquet", "40_panel_yearly.parquet",
               "16_article_alignment.parquet"):
        p = os.path.join(out_dir, fn)
        if os.path.exists(p):
            return pd.read_parquet(p)
    return None


def test_gemini_large_cosine_agreement():
    df = _load_panel()
    if df is None:
        pytest.skip("DEFERRED: 盘上无 panel 产物")
    try:
        from scipy.stats import spearmanr  # noqa: PLC0415
    except ImportError:
        pytest.skip("scipy 未安装 — 无法计算 Spearman ρ")

    import numpy as np  # noqa: PLC0415

    checked = 0
    failures = []
    for main_c, lg_c in _PAIR_CANDIDATES:
        if main_c not in df.columns or lg_c not in df.columns:
            continue
        sub = df[[main_c, lg_c]].apply(lambda s: np.asarray(s, dtype="float64"))
        mask = (~sub[main_c].isna()) & (~sub[lg_c].isna())
        n = int(mask.sum())
        if n < MIN_PAIRS:
            continue
        rho, _ = spearmanr(sub.loc[mask, main_c], sub.loc[mask, lg_c])
        checked += 1
        if not (rho >= RHO_THRESHOLD):
            failures.append(f"{main_c}⟂{lg_c}: ρ={rho:.4f} < {RHO_THRESHOLD} (n={n:,})")

    if checked == 0:
        pytest.skip(
            "DEFERRED: 盘上 panel 无任何含 ≥500 非 NaN 值的 co-primary 余弦对 "
            "(gemini/large 缓存未播种或 panel 未重生); 须生产语料机播种+重生后此门方生效"
        )
    assert not failures, (
        "gemini⟂large 跨厂商余弦一致性低于阈值 (gemini 余弦语义有效性存疑):\n"
        + "\n".join(failures)
    )
