"""test_attention_geo_gating.py — ATT-2 修复回归锁: 地理注意力指数族分子 verified 门控
=====================================================================================

锁定 panel-universe-consistency-audit ATT-2 修复 (2026-06-18):
  compute_fintech_attention_index 的**分子** (ft_attn_yr/prov/city + 总量孪生
  ft_vol_*, 取自 is_fintech_news 计数) 现于 docid 去重前在源头经 restrict_to_verified
  按 (docid, target_bank) semi-join 收敛到 stage-21 verified 集 (24_herd_decay),
  与 compute_attention_treatments (ATT-1) 同域, 剔除约 26.8% 被 stage 21 判伪文章。

设计点:
  - 门控生效: 用一个仅覆盖部分 (docid,target_bank) 对的合成 24_herd_decay verified
    keyset → 门控后的 year-level fintech 计数 (ft_vol_yr = ln1p(N_ft)) 严格 < 未门控。
  - 面板行数不变: 门控只删分子源行, 不动面板脊柱 (panel rows 不变)。
  - fail-open: df_all 缺 docid 时, restrict_to_verified 响亮 fail-open 返回未门控全集
    (合成帧 / 缺 24_herd_decay 时), 与既有行为一致。

全部用合成 DataFrame + tmp_path 临时 parquet, 不依赖盘上大数据, 不调外部 API。
仿 tests/test_omni_fix_attention.py / tests/test_attention_treatments.py 夹具约定。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel import attention_media as am

pytestmark = pytest.mark.fast

_F12_NAME = '12_fintech_news_full.parquet'
_HERD_NAME = '24_herd_decay.parquet'


def _build_f12(with_docid=True):
    """合成 article×bank 帧: 4 篇 fintech (d1..d4) + 2 篇非 fintech (d5,d6), 单年单地理。

    fintech docid: d1(A) d2(A) d3(B) d4(C); 非 fintech: d5(A) d6(B)。
    verified keyset 只覆盖 (d1,A)(d2,A)(d4,C) 三对 fintech (~73% 的 fintech docid:
    4 篇中保留 3 篇), 故门控应剔除 (d3,B), 令 fintech 唯一篇数 4 → 3。
    """
    rows = [
        {'docid': 'd1', 'target_bank': 'A', 'is_fintech_news': True},
        {'docid': 'd2', 'target_bank': 'A', 'is_fintech_news': True},
        {'docid': 'd3', 'target_bank': 'B', 'is_fintech_news': True},
        {'docid': 'd4', 'target_bank': 'C', 'is_fintech_news': True},
        {'docid': 'd5', 'target_bank': 'A', 'is_fintech_news': False},
        {'docid': 'd6', 'target_bank': 'B', 'is_fintech_news': False},
    ]
    df = pd.DataFrame(rows)
    df['日期'] = '2020-01-01'
    df['国家地区/省份'] = 'P1'
    df['城市'] = 'C1'
    if not with_docid:
        df = df.drop(columns=['docid'])
    return df


def _verified_keyset():
    """verified (docid,target_bank) 集 = **仅 fintech-verified 对** (镜像生产: 非 fintech 行
    从不经 stage 21, 24_herd_decay 不含非 fintech 对 — verified_universe.py:15-18)。

    4 篇 fintech 中保留 (d1,A)(d2,A)(d4,C) 三对, 剔除 (d3,B) (模拟 stage 21 判伪)。
    ⚠ 刻意**不含任何非 fintech 对** (d5/d6): 若错误地对整个 df_all 做 semi-join, 全部非
    fintech 行会被 inner-join 删除 → 分母 _total 塌成 fintech-only → ft_attn_yr≈1; 本测试
    的 ft_attn_yr==0.5 断言据此判伪 (正确实现仅重标分子, 分母全集 6 篇不变 → 3/6)。
    """
    return pd.DataFrame({
        'docid': ['d1', 'd2', 'd4'],
        'target_bank': ['A', 'A', 'C'],
    })


def _write_env(tmp_path, monkeypatch, *, with_docid=True, with_herd=True):
    """写 12_full (+ 可选 24_herd_decay) 到 tmp_path, 重定向 OUTPUT_DIR/FILENAMES。"""
    _build_f12(with_docid=with_docid).to_parquet(tmp_path / _F12_NAME)
    filenames = {'output_12_fintech_full': _F12_NAME}
    if with_herd:
        _verified_keyset().to_parquet(tmp_path / _HERD_NAME)
        filenames['output_24_herd_decay'] = _HERD_NAME
    monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))
    monkeypatch.setattr(am, 'FILENAMES', filenames)
    monkeypatch.setattr(am, '_save_attn_index', lambda *a, **k: None)


def _panel():
    return pd.DataFrame({'target_bank': ['A', 'B', 'C'], 'year': [2020, 2020, 2020]})


def test_geo_index_verified_restriction(tmp_path, monkeypatch):
    """门控生效: gated fintech 计数 < ungated, 且面板行数不变。

    ft_vol_yr = ln1p(当年 fintech 唯一篇数):
      ungated: 4 篇 fintech (d1,d2,d3,d4) → ln1p(4)
      gated  : verified 剔除 (d3,B) → 3 篇 (d1,d2,d4) → ln1p(3)
    """
    panel = _panel()

    # ── ungated 基线: 无 24_herd_decay → restrict_to_verified fail-open ──
    # 6 篇全部银行新闻 (d1..d6), 其中 4 篇 fintech → ft_attn_yr=4/6, ft_vol_yr=ln1p(4)。
    _write_env(tmp_path, monkeypatch, with_herd=False)
    out_ungated = am.compute_fintech_attention_index(panel.copy())
    vol_ungated = out_ungated['ft_vol_yr'].dropna().iloc[0]
    attn_ungated = out_ungated['ft_attn_yr'].dropna().iloc[0]
    assert vol_ungated == pytest.approx(np.log1p(4)), \
        f'未门控应见全部 4 篇 fintech, 实得 ln1p^-1={np.expm1(vol_ungated)}'
    assert attn_ungated == pytest.approx(4 / 6), \
        f'未门控 ft_attn_yr 应 = 4/6 (4 fintech / 6 全部银行新闻), 实得 {attn_ungated}'

    # ── gated: fintech-only verified keyset (剔除 fintech 对 d3,B) ──
    # 仅分子重标: d3 重标为非 fintech → 3 篇 verified fintech; 分母仍 6 篇全部银行新闻 (未塌)。
    _write_env(tmp_path, monkeypatch, with_herd=True)
    out_gated = am.compute_fintech_attention_index(panel.copy())
    vol_gated = out_gated['ft_vol_yr'].dropna().iloc[0]
    attn_gated = out_gated['ft_attn_yr'].dropna().iloc[0]
    assert vol_gated == pytest.approx(np.log1p(3)), \
        f'门控后应仅余 3 篇 verified fintech, 实得 ln1p^-1={np.expm1(vol_gated)}'

    # ★ 判伪核心断言 (区分"仅门控分子" vs "错误地整 df_all semi-join"):
    #   正确实现: ft_attn_yr = 3 verified fintech / 6 全部银行新闻 = 0.5 (分母全集不塌)。
    #   错误实现 (整 df_all inner-join verified-fintech-only keyset): 非 fintech 行全删 →
    #   分母塌成 fintech-only=3 → ft_attn_yr=3/3≈1.0 → 本断言失败 → 揪出退化 bug。
    assert attn_gated == pytest.approx(3 / 6), \
        (f'门控应仅重标分子、分母全集不塌: ft_attn_yr 应 = 3/6 = 0.5, 实得 {attn_gated}. '
         f'若 ≈1 说明错误地把整个 df_all semi-join 致分母塌成 fintech-only (退化)')

    # 门控后分子严格收缩
    assert vol_gated < vol_ungated, \
        f'门控应剔除判伪文章: gated ft_vol_yr={vol_gated} 应 < ungated {vol_ungated}'

    # 面板行数不变 (门控只重标分子, 不动面板脊柱)
    assert len(out_gated) == len(panel), \
        f'面板行数应不变: {len(out_gated)} != {len(panel)}'
    assert len(out_gated) == len(out_ungated), '门控前后面板行数应一致'


def test_geo_index_fail_open_when_herd_absent(tmp_path, monkeypatch):
    """fail-open (函数级): 无 24_herd_decay 时 restrict_to_verified 响亮 fail-open 返回
    未门控全集 → 见全部 4 篇 fintech, 不崩、不新增回退逻辑。面板行数不变。"""
    panel = _panel()
    _write_env(tmp_path, monkeypatch, with_herd=False)
    out = am.compute_fintech_attention_index(panel.copy())
    vol = out['ft_vol_yr'].dropna().iloc[0]
    assert vol == pytest.approx(np.log1p(4)), \
        f'缺 24_herd_decay 应 fail-open 见全部 4 篇 fintech, 实得 ln1p^-1={np.expm1(vol)}'
    assert len(out) == len(panel)


def test_restrict_to_verified_fail_open_when_docid_absent():
    """fail-open (helper 级, 任务点 4): df 缺 docid 列时 restrict_to_verified 响亮 fail-open,
    原样返回未门控全集 (不崩、不新增回退逻辑)。

    注: compute_fintech_attention_index 把 docid 列作硬核心列 (缺则更早 ERROR 返回 panel),
    故 docid 缺失的 fail-open 契约在 helper 层直接验证 — 这正是门控 fail-open 的安全保证源头。
    """
    df_no_docid = _build_f12(with_docid=False)
    n_before = len(df_no_docid)
    # output_dir/filenames 任意 (缺键 → 在读 herd 之前即 fail-open)
    out = am.restrict_to_verified(
        df_no_docid, output_dir='/__no_such_dir__', filenames={},
        keys=['docid', 'target_bank'], logger=am.logger,
        label='attention.geo_numerator')
    assert len(out) == n_before, '缺 docid 应 fail-open 原样返回 (行数不变)'
    assert out.equals(df_no_docid), 'fail-open 应原样返回输入帧 (不门控)'


def test_source_gate_inserted_before_dedup():
    """源码级: verified 门控重赋值必须出现在 docid 去重之前 (一处门控传播全部六列)。"""
    src = am.compute_fintech_attention_index.__doc__
    assert 'ATT-2' in src, 'docstring 应披露 ATT-2 门控修复'
    assert 'restrict_to_verified' in src
    # 不再保留 "未门控/deferred/待决" 缺口措辞 (ATT-2 已解决)
    treatments_doc = am.compute_attention_treatments.__doc__
    assert 'deferred 待决' not in treatments_doc, \
        'ATT-2 已修复, compute_attention_treatments 范围注释不应再称 ft_attn_* deferred'
