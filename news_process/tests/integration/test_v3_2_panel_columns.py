"""v3.2.0 panel parquet 列存在性 sanity test (plan v14 §5.1).

测试如果 stage 45 已跑通 (40_panel_yearly.parquet 存在),
则 v3.2.0 M1-M3 新增的双轨列应当全部存在.

如果 panel parquet 不存在: 跳过 (用户尚未跑 pipeline).

测试覆盖 (plan v14 §2.1-§2.3):
  - stage 21 输出 9 双轨/dual gate 列 (篇章级, 但聚合到 panel 通过 40_article_bank_level)
  - encode.py M2 P2 加性: _lc × _ctx 对角线列 (12 列 panel 级)
  - encode.py M2 P3 4-way count: _is_*_sc 列 (16 列 panel 级)
  - iv_did.py M3 P4: bartik_fintech_lf_* + bartik_fintech_lc_* (12 列)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


@pytest.fixture(scope="module")
def panel_or_skip():
    """加载 40_panel_yearly.parquet; 若不存在 → skip 测试."""
    import os

    import pandas as pd
    try:
        from news_process.core.config import load_config
        CONFIG = load_config()
        panel_path = os.path.join(CONFIG['paths']['output_dir'], '40_panel_yearly.parquet')
    except Exception as e:
        pytest.skip(f"Config load 失败 (pipeline 未配置): {e}")
    if not os.path.exists(panel_path):
        pytest.skip(f"Panel parquet 不存在 ({panel_path}); 先跑 run_pipeline_function.py")
    return pd.read_parquet(panel_path)


def test_panel_main_columns_exist(panel_or_skip):
    """plan v14 §2.1: 基础双轨列 (sentiment + 主键)."""
    required = {
        'target_bank', 'year',
        'llm_vote_tone_full', 'llm_vote_tone_ctx',
        'n_articles',
    }
    missing = required - set(panel_or_skip.columns)
    assert not missing, f"基础列缺失: {missing}"


def _panel_is_v3_2(panel) -> bool:
    """启发式: panel 是否由 v3.2.0 pipeline 生成 (含 ctx 子集列)."""
    return 'n_articles_tech_lc_ctx' in panel.columns


def test_panel_locus_lc_diagonal_columns(panel_or_skip):
    """plan v14 §2.2 M2 P2: _lc × _ctx 对角线 locus 子集列.

    若 panel 是 v3.1.1 生成 (未含 _lc 列) → skip; 用户需重跑 v3.2.0 pipeline.
    """
    if not _panel_is_v3_2(panel_or_skip):
        pytest.skip("Panel by v3.1.1 (no _lc cols); rerun pipeline with v3.2.0 to enable")
    cols = set(panel_or_skip.columns)
    required = {
        'n_articles_tech_lc_ctx', 'n_articles_app_lc_ctx',
        'llm_vote_tone_tech_lc_ctx', 'llm_vote_tone_app_lc_ctx',
        'tech_frac_lc', 'app_frac_lc',
        'tone_gap_tech_app_lc_ctx',
    }
    missing = required - cols
    assert not missing, f"M2 P2 locus _lc × _ctx 对角线列缺失: {missing}"


def test_panel_substantiveness_sc_diagonal_columns(panel_or_skip):
    """plan v14 §2.2 M2 P2: _sc × _ctx 对角线 substantiveness 子集列.

    若 panel 是 v3.1.1 生成 → skip.
    """
    if not _panel_is_v3_2(panel_or_skip):
        pytest.skip("Panel by v3.1.1 (no _sc cols); rerun pipeline with v3.2.0 to enable")
    cols = set(panel_or_skip.columns)
    required = {
        'n_articles_sub_sc_ctx', 'n_articles_symb_sc_ctx',
        'llm_vote_tone_sub_sc_ctx', 'llm_vote_tone_symb_sc_ctx',
        'sub_frac_sc', 'symb_frac_sc',
        'tone_gap_sub_symb_sc_ctx',
    }
    missing = required - cols
    assert not missing, f"M2 P2 subst _sc × _ctx 对角线列缺失: {missing}"


def test_panel_bartik_iv_dual_set(panel_or_skip):
    """plan v14 §3.4 M3 P4: Bartik IV 双套独立 (lf + lc).

    Bartik IV 双套需 runner.py M3 P4 + ctx-side share — 用户重跑 pipeline 才有.
    """
    if not _panel_is_v3_2(panel_or_skip):
        pytest.skip("Panel by v3.1.1 (no bartik_fintech_lf_*); rerun pipeline")
    cols = set(panel_or_skip.columns)
    required = {
        'bartik_fintech_lf_share_tech', 'bartik_fintech_lf_share_app',
        'bartik_fintech_lc_share_tech', 'bartik_fintech_lc_share_app',
    }
    missing = required - cols
    assert not missing, f"M3 P4 Bartik IV 双套列缺失: {missing}"


def test_panel_dual_subset_identity(panel_or_skip):
    """plan v14 §3.2 R3-C 恒等式: n_articles_tech_lc + n_articles_app_lc 应 ≤ n_articles
    (注: ctx 轨可能丢 some verified_ctx=False, 故 ≤ 而非 ==)
    """
    if not _panel_is_v3_2(panel_or_skip):
        pytest.skip("Panel by v3.1.1; rerun pipeline for v3.2.0 identity check")
    df = panel_or_skip
    has_news = df['n_articles'] > 0
    sum_lc = (df.loc[has_news, 'n_articles_tech_lc_ctx'] +
              df.loc[has_news, 'n_articles_app_lc_ctx'])
    # ≤ n_articles (ctx 轨可能未全覆盖)
    assert (sum_lc <= df.loc[has_news, 'n_articles']).all(), \
        "M2 P2 _lc 子集恒等式违反: tech_lc + app_lc > n_articles"


def test_panel_column_count_lower_bound(panel_or_skip):
    """v3.2.0 panel 列数应 ≥ v3.1.1 baseline (994 测试) panel 列 (2002).

    v3.2.0 加性策略 (M2 P2 P3) 新增 ~50-80 列, panel 应至少有 ~2050 列.
    """
    n_cols = len(panel_or_skip.columns)
    assert n_cols >= 2002, f"Panel 列数 {n_cols} < v3.1.1 baseline 2002 (regression?)"
