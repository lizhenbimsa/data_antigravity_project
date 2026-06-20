"""W2 守护测试: compute_attention_treatments (P2 attention 处理变量) 在真实试跑数据
(15_fintech_intensity + 12_fintech_news_full) 上的正确性与全部 foolproof 守卫。

覆盖审核报告 P2_ATTENTION_FOOLPROOF_DUALTRACK_AUDIT 的硬坑:
  B1 全集脊柱防选择偏差 (零-fintech bank-year 不丢、index/pct=0)
  B2 pct 分母独立读 12_full (无除零)
  B3 强度密度非[0,1]不叫share (值域校验)
  B4 归因份额有界构造 Σctx/(Σctx+Σfull) ∈ [0,1] (fix(omni-g-attention-01/08):
     旧 clip(Σctx/Σfull) 右删失构造已废弃)
  H1 强度SD N<2→NaN 守卫
  双轨=互为稳健性: index/density/sd 各产 _full/_ctx 成对
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel.attention_media import (
    FILENAMES,
    OUTPUT_DIR,
    compute_attention_treatments,
)

_S14 = os.path.join(OUTPUT_DIR, FILENAMES.get(
    'output_14_fintech_intensity', '15_fintech_intensity.parquet'))
_F12 = os.path.join(OUTPUT_DIR, FILENAMES.get(
    'output_12_fintech_full', '12_fintech_news_full.parquet'))

pytestmark = pytest.mark.skipif(
    not (os.path.exists(_S14) and os.path.exists(_F12)),
    reason='需 15_fintech_intensity + 12_fintech_news_full 试跑产物',
)

_OUT_COLS = [
    'attention_index_full', 'attention_index_ctx', 'attention_pct_full',
    'attention_intensity_density_full', 'attention_intensity_density_ctx',
    'attention_disp_full', 'attention_intensity_sd_full', 'attention_intensity_sd_ctx',
    'attention_gap_full_ctx', 'attention_attr_share',
    'n_fintech_articles', 'n_outlets',
]


def _universe_panel() -> pd.DataFrame:
    """以 12_full 全 bank-year 全集作面板脊柱 (含零-fintech bank-year, 直接压 B1/B2)。"""
    f12 = pd.read_parquet(_F12, columns=['target_bank', '日期'])
    f12['year'] = pd.to_datetime(f12['日期'], errors='coerce').dt.year
    f12 = f12.dropna(subset=['year'])
    f12['year'] = f12['year'].astype(int)
    return (f12.drop_duplicates(['target_bank', 'year'])[['target_bank', 'year']]
            .reset_index(drop=True))


@pytest.fixture(scope='module')
def out():
    return compute_attention_treatments(_universe_panel())


def test_all_columns_present(out):
    for c in _OUT_COLS:
        assert c in out.columns, f'缺列 {c}'


def test_no_selection_bias_full_universe(out):
    # 全集脊柱: 输出行数 == 输入全集行数 (零-fintech 银行不被丢, B1)
    assert len(out) == len(_universe_panel())
    # 应真有零-fintech bank-year (否则测试空转)
    assert (out['n_fintech_articles'] == 0).sum() > 0


def test_index_nonneg_no_nan(out):
    # 累积 index: 零-fintech→log1p(0)=0, 全集无 NaN, 恒 ≥0
    for c in ['attention_index_full', 'attention_index_ctx']:
        v = out[c]
        assert v.notna().all(), f'{c} 含 NaN'
        assert (v >= 0).all(), f'{c} 含负值'


def test_pct_bounded_no_divzero(out):
    # B2: pct=N_ft/N_all, 分母全集来自 12_full 恒≥1 → 无除零, ∈[0,1], 无 NaN/inf
    p = out['attention_pct_full']
    assert p.notna().all() and np.isfinite(p).all()
    assert p.between(0, 1).all(), f'pct 越界 [{p.min()},{p.max()}]'


def test_density_is_not_share(out):
    # B3: 强度密度值域 [0,+∞), 实测可 >1 (故不叫 share); 但 ≥0 无 NaN(零fintech→0)
    for c in ['attention_intensity_density_full', 'attention_intensity_density_ctx']:
        v = out[c]
        assert v.notna().all() and (v >= 0).all()


def test_attr_share_bounded(out):
    # B4 修订 fix(omni-g-attention-01/08, 2026-06-11): share = Σctx/(Σctx+Σfull)
    # 结构性 ∈ [0,1] (旧 clip(Σctx/Σfull,0,1) 把 ctx>full 质量右删失到 1.0, 已废弃)
    s = out['attention_attr_share'].dropna()
    assert s.between(0, 1).all(), f'attr_share 越界 [{s.min()},{s.max()}]'


def test_disp_hhi_bounded(out):
    # 跨媒体 HHI ∈(0,1]; 零-fintech→NaN; 单 outlet→1.0 合法
    d = out['attention_disp_full'].dropna()
    assert d.between(0, 1).all(), f'HHI 越界 [{d.min()},{d.max()}]'
    # 零-fintech bank-year 的 disp 应为 NaN (无报道无离散度)
    z = out['n_fintech_articles'] == 0
    assert out.loc[z, 'attention_disp_full'].isna().all()


def test_sd_guard_n_lt_2(out):
    # H1: 强度SD 在 n_fintech<2 的 bank-year 必为 NaN (ddof=1)
    lt2 = out['n_fintech_articles'] < 2
    assert out.loc[lt2, 'attention_intensity_sd_full'].isna().all()
    assert out.loc[lt2, 'attention_intensity_sd_ctx'].isna().all()
    # n≥2 的应有非 NaN (至少部分可算)
    ge2 = out['n_fintech_articles'] >= 2
    if ge2.sum() > 0:
        assert out.loc[ge2, 'attention_intensity_sd_full'].notna().any()


def test_zero_fintech_semantics(out):
    # 零-fintech bank-year: index/pct/density=0 (真零曝光); gap/share=NaN (无可归因)
    z = out['n_fintech_articles'] == 0
    assert (out.loc[z, 'attention_index_full'] == 0).all()
    assert (out.loc[z, 'attention_index_ctx'] == 0).all()
    assert (out.loc[z, 'attention_pct_full'] == 0).all()
    assert out.loc[z, 'attention_gap_full_ctx'].isna().all()
    assert out.loc[z, 'attention_attr_share'].isna().all()


def test_dualtrack_pairs_present(out):
    # 双轨=互为稳健性: 三组度量各产 _full/_ctx 成对
    for base in ['attention_index', 'attention_intensity_density', 'attention_intensity_sd']:
        assert f'{base}_full' in out.columns and f'{base}_ctx' in out.columns


def test_pct_le_one_invariant(out):
    # n_ft ≤ n_all 不变量 (stage14 ⊆ 12_full); n_fintech_articles 不超过该 bank-year 总篇
    assert (out['n_fintech_articles'] >= 0).all()


def test_panel_superset_rows_are_nan():
    """NaN 非对称契约: panel 含 12_full universe 之外的 bank-year (完全无新闻) → 全 12 列 NaN
    (区别于 in-universe 零-fintech 行的 index/pct/density=0 真零曝光)。"""
    panel = _universe_panel()
    fake = pd.DataFrame({'target_bank': ['__FAKE_BANK_NOT_IN_12FULL__'], 'year': [2099]})
    out_plus = compute_attention_treatments(pd.concat([panel, fake], ignore_index=True))
    row = out_plus[(out_plus['target_bank'] == '__FAKE_BANK_NOT_IN_12FULL__')
                   & (out_plus['year'] == 2099)]
    assert len(row) == 1, '伪银行行应保留 (LEFT-join 不丢)'
    for c in _OUT_COLS:
        assert row[c].isna().all(), f'{c} 应为 NaN (panel⊋universe 无新闻不可测), 实得 {row[c].values}'


_HERD = os.path.join(OUTPUT_DIR, FILENAMES.get(
    'output_24_herd_decay', '24_herd_decay.parquet'))


@pytest.mark.skipif(not os.path.exists(_HERD),
                    reason='需 24_herd_decay 试跑产物 (verified 域门控)')
def test_verified_gate_applied(out):
    """panel-universe-consistency-audit ATT-1/ATT-2: fintech 分子收敛到 stage-21 verified
    集 (24_herd_decay)。实测 Σn_fintech_articles 应等于 verified (docid,target_bank) 行数,
    且严格 < 未门控的 15_fintech_intensity 唯一对数 — 后者实质检验门控真生效 (未门控会泄漏
    约 26.8% 被 stage 21 判伪文章)。"""
    n_verified = (pd.read_parquet(_HERD, columns=['docid', 'target_bank'])
                  .drop_duplicates().shape[0])
    n_ungated = (pd.read_parquet(_S14, columns=['docid', 'target_bank'])
                 .drop_duplicates().shape[0])
    total_ft = int(out['n_fintech_articles'].sum())
    assert total_ft == n_verified, \
        f'门控后 Σn_fintech_articles={total_ft} 应 == verified 行数 {n_verified}'
    assert total_ft < n_ungated, \
        f'门控应剔除假阳性: Σn_fintech={total_ft} 应 < 未门控 s14 {n_ungated}'


def test_verified_gate_preserves_nan_zero_contract(out):
    """门控后 n_ft 与 disp/sd 的 NaN-vs-0 一致性必须保持 (gated s14 与 gated f12_ft 同收敛
    到 verified 集 → 非空 bank-year 集恒一致)。冗余于 test_zero_fintech_semantics, 但显式
    锁定"同时门控两个分子源"这一设计点 (只门控一边会产生契约违反)。"""
    z = out['n_fintech_articles'] == 0
    assert out.loc[z, 'attention_disp_full'].isna().all(), 'n_ft=0 但 disp 非 NaN (分子源未同域门控?)'
    assert out.loc[z, 'attention_intensity_sd_full'].isna().all()
    assert (out.loc[z, 'attention_index_full'] == 0).all()


def test_denominator_is_full_bank_news_universe(out):
    """守卫: 门控只作用于分子, 分母 (n_all) 必须保持 12_full 全部银行新闻全集 (未门控)。
    attention_pct_full = n_fintech_articles / n_all, 故用**全集** n_all 反推
    pct*n_all == n_fintech_articles 应成立。若有人误把分母也门控到 verified 集
    (n_all 从全集塌缩到 857), 该恒等式破裂 → 本测试是唯一能逮住"分母被误门控"的守卫
    (其余测试只查分子/边界, 见 verification wf_c1e23964-a18 completeness-honesty)。"""
    f12 = pd.read_parquet(_F12, columns=['target_bank', '日期'])
    f12['year'] = pd.to_datetime(f12['日期'], errors='coerce').dt.year
    f12 = f12.dropna(subset=['year'])
    f12['year'] = f12['year'].astype(int)
    n_all_full = (f12.groupby(['target_bank', 'year']).size()
                  .rename('_n_all_full').reset_index())
    m = out.merge(n_all_full, on=['target_bank', 'year'], how='inner')
    nz = m['n_fintech_articles'] > 0
    assert nz.any(), '需至少一个非零-fintech bank-year 才有判别力'
    recon = m.loc[nz, 'attention_pct_full'] * m.loc[nz, '_n_all_full']
    assert np.allclose(recon, m.loc[nz, 'n_fintech_articles'], atol=1e-6), \
        '分母非 12_full 全集 (n_all 被误门控?): pct*n_all_full != n_fintech_articles'
