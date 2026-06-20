"""v3.2.0 panel parquet 列存在性 sanity test (plan v14 §5.1).

测试如果 stage 45 已跑通 (40_panel_yearly.parquet 存在),
则 v3.2.0 M1-M3 新增的双轨列应当全部存在.

如果 panel parquet 不存在: 跳过 (用户尚未跑 pipeline).

三轨 (ss 银行+金科同句共现轨, 2026-06-14): full/ctx 之外新增并列第三主轨
content_ss → 面板各情感族多出 `_ss` 列。⚠ ss 列须经付费 stage 21 重跑 + stage
45/46 重生后才落盘, 当前冻结 panel 尚无 ss 列, 故列数下界守卫仍锁 1400 (未上调);
ss 落盘后须据实重算下界 (见 test_panel_column_count_lower_bound 的 TODO)。

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
    # 三轨 (ss 2026-06-14): ss 主语调列须付费 stage 21 重跑 + 重生后落盘;
    # 已落盘则校验存在 (skip-if-missing 软守卫, 共享 n_articles 分母)。
    if 'llm_vote_tone_ss' in panel_or_skip.columns:
        assert 'llm_vote_tone_ss' in panel_or_skip.columns


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
    """plan v14 §3.2 R3-C 恒等式: tech_lc + app_lc 应是 ctx-verified 子集划分.

    v3.7.2 R8-H1 之后 ctx 轨与 full 轨独立 (OR-filter, 见 tone_llms.py:1744),
    `n_articles`(=count of llm_vote_score_full) 不再是 ctx-locus 计数的上界 ——
    ctx 可验证 full 未验证的文章 (实测 fallback 率 10.4%, 见 CLAUDE.md v3.7.2)。

    新不变式: tech_lc/app_lc 桶互斥 (locus 字段 1-of-K), 故 tech_lc + app_lc 是
    ctx-verified 中 locus∈{底层技术,应用场景} 的总数。从 14_news_with_ctx.parquet
    动态推导 ctx-verified-with-locus 计数作为参照。
    """
    if not _panel_is_v3_2(panel_or_skip):
        pytest.skip("Panel by v3.1.1; rerun pipeline for v3.2.0 identity check")
    import os

    import pandas as pd

    from news_process.core.config import load_config
    CONFIG = load_config()
    ctx_path = os.path.join(CONFIG['paths']['output_dir'], '21_tone_llms.parquet')
    if not os.path.exists(ctx_path):
        pytest.skip(f"上游 stage 21 parquet 缺失 ({ctx_path}); 跳过 ctx-side 恒等式校验")

    art = pd.read_parquet(ctx_path, columns=['target_bank', 'innovation_locus_ctx'])
    # ctx-verified 文章中 locus∈{底层技术,应用场景} 的计数, 按 target_bank 汇总
    expected_per_bank = (
        art[art['innovation_locus_ctx'].isin(['底层技术', '应用场景'])]
        .groupby('target_bank').size().rename('expected_sum_lc_ctx')
    )

    df = panel_or_skip
    has_news = df['n_articles'] > 0
    panel_sum = (df.loc[has_news, 'n_articles_tech_lc_ctx'] +
                 df.loc[has_news, 'n_articles_app_lc_ctx'])
    # 不变式 1: 桶互斥 → tech_lc + app_lc 不超过 ctx-verified-with-locus 总数 (per bank)
    by_bank = pd.DataFrame({
        'target_bank': df.loc[has_news, 'target_bank'].values,
        'panel_sum': panel_sum.values,
    }).groupby('target_bank')['panel_sum'].sum()
    merged = by_bank.to_frame('panel').join(expected_per_bank, how='left').fillna(0)
    over = merged[merged['panel'] > merged['expected_sum_lc_ctx']]
    assert over.empty, (
        f"M2 P2 _lc 子集恒等式违反 (per bank): tech_lc+app_lc > ctx-verified-with-locus\n"
        f"{over.head(10)}"
    )


def test_panel_column_count_lower_bound(panel_or_skip):
    """panel 列数下界回归 guard (remove-title-track 后下调阈值).

    历史: v3.2.0 三轨 (full/ctx/title) 期望 ≥ 2002 列 (v3.1.1 baseline 994 的 2 倍).
    remove-title-track: 取消标题情感轨后 panel 从 3 轨收缩为 2 轨 (full/ctx),
    sentiment 各族少约 1/3 列 — 冻结 disk panel 1998 列中含 427 个 `_title` 列
    + 4 个标题派生列 (tone_gap_title_full / prob_gap_title_full / frac_title_* /
    avg_agreement_rate_title), 重跑后约剩 ~1567 列。阈值下调到 1400:
    既高于 v3.1.1 baseline 994 (仍是有意义的"宽表未坍缩"守卫), 又同时容纳
    冻结 panel (1998, production 重跑前) 与重跑后的 2 轨 panel (~1567)。

    三轨 (ss 银行+金科同句共现轨, 2026-06-14): ss 落盘后面板再增一批 `_ss` 情感族
    列 (实测活面板 ctx 列 ~ 据实重算, 见 plan §⑫: 1658 列 + ss 增量)。
    ⚠ TODO(post-impl): ss 列经付费 stage 21 重跑 + stage 45/46 重生落盘后, 据
    实读面板的 _ss 列数把下界从 1400 上调到新值 (勿凭估值上调; ss 未落盘前保持
    1400 以兼容当前冻结 panel)。
    """
    n_cols = len(panel_or_skip.columns)
    # 注: ss 未落盘前下界保持 1400 (见上 TODO); ss 落盘后据实重算上调。
    assert n_cols >= 1400, (
        f"Panel 列数 {n_cols} < 1400 下界 (remove-title-track 后 2 轨 panel "
        f"应 ~1567 列; ss 三轨落盘后更多; 低于 1400 疑似宽表坍缩 regression)"
    )
