"""tests/test_boilerplate_chunked.py — boilerplate OOM 硬化 exact two-pass gate.

执行计划 BOILERPLATE_CHUNKED_TWOPASS_OOM_HARDENING (2026-07-06) §4 十项 gate:
chunked (in_memory) 与 legacy (single_pass) 逐字节等价 + chunk_size 不变性 + 结构不变量 +
SAFE 降级 + vectorizer 参数锁 + top-k 集合等价 + config 穿透 + fail-loud (disk/hard 闸)。

铁律: chunked exact two-pass 输出与 legacy 单遍逐字节一致 (golden 零漂移)。
legacy single_pass 臂 = 字节等价参照实现, 只要本文件存在即禁改 _compute_single_pass_legacy。
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.sentiment import boilerplate as B
from news_process.pipeline.sentiment.boilerplate import (
    compute_boilerplate_ratios,
    enrich_with_boilerplate,
)


def _eq(a, b) -> bool:
    """逐元素相等 (NaN-aware)。"""
    if len(a) != len(b):
        return False
    return all(
        (isinstance(x, float) and math.isnan(x) and isinstance(y, float) and math.isnan(y))
        or x == y
        for x, y in zip(a, b))


def _corpus_with_boiler():
    """含达阈值套话 + 退化(空格单字) + 空/哨兵 + total 非平凡分布的合成语料。"""
    return [
        '本报讯记者今日报道有限公司业绩情况良好',
        '本报讯某公司发布有限公司重大事项公告',
        '记者今日报道股份制改革进展顺利完成',
        '有限公司年度报告披露完毕主要结果',
        '本报讯有限公司召开临时股东大会决议',
        '独家深度分析市场趋势多种复杂变化',
        '本报讯记者有限公司高管独家专访实录',
        '股份制银行改革持续深化稳步推进',
        '有限公司季度财报超出市场普遍预期',
        '本报讯有限公司引入战略投资者布局',
        '中 国 银 行 分 行',          # 过 _clean(≥4实字) 但空格单字 token (退化, char_wb 短词)
        '', 'nan', None,              # 空/哨兵 → nan
        '本报讯有限公司发布社会责任报告',
        '有限公司完成重大资产重组事项',
    ]


# ── §4-1: chunked (in_memory) vs legacy (single_pass) 逐字节等价 ──

def test_chunked_equals_singlepass():
    docs = _corpus_with_boiler()
    a = compute_boilerplate_ratios(docs, memory_tier='single_pass')
    b = compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=4)
    assert _eq(a, b), 'chunked 与 legacy 单遍逐字节不等 (字节等价被破)'
    # 退化文档跨块边界交错 (小 chunk_size 令 '中 国 银 行 分 行' 与正常文档分处不同块)
    b1 = compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=1)
    assert _eq(a, b1), 'chunk_size=1 下退化文档跨块处理与单遍不等'


# ── §4-2: chunk_size 不变性 (纯性能参数, 输出恒同) ──

def test_chunk_size_invariance():
    docs = _corpus_with_boiler()
    n = len(docs)
    ref = compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=n)
    for cs in (1, 7, n - 1, n, 2 * n):
        got = compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=cs)
        assert _eq(ref, got), f'chunk_size={cs} 输出与参照不等 (非纯性能参数)'
    # 畸值 clamp: chunk_size=0 不死循环, 与正常等价
    got0 = compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=0)
    assert _eq(ref, got0), 'chunk_size=0 clamp 后与参照不等'


# ── §4-4: 结构不变量 (每次 fit_transform 收到文档数 ≤ chunk_size; 直证不物化全量 CSR) ──

def test_memory_structural_invariant(monkeypatch):
    docs = _corpus_with_boiler()
    chunk_size = 4
    seen_sizes = []
    from sklearn.feature_extraction.text import CountVectorizer
    orig_fit = CountVectorizer.fit_transform

    def _spy_fit(self, raw, *a, **k):
        seen_sizes.append(len(raw))
        return orig_fit(self, raw, *a, **k)

    monkeypatch.setattr(CountVectorizer, 'fit_transform', _spy_fit)
    compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=chunk_size)
    assert seen_sizes, 'Pass1 未调用 fit_transform'
    assert all(s <= chunk_size for s in seen_sizes), \
        f'某次 fit_transform 收到 {max(seen_sizes)} > chunk_size={chunk_size} (物化了全量 CSR)'


# ── §4-5: SAFE 降级 (态 a/c/d 可达 + _clean 退化 逐字节同单遍) ──

def test_safe_degradation_preserved():
    # 态 a: 全空/哨兵 → 全 nan
    assert all(math.isnan(v) for v in compute_boilerplate_ratios(['', 'nan', None]))
    # _clean 退化 (实字 < 4) → nan, 与 single_pass 一致
    mixed = _corpus_with_boiler()
    a = compute_boilerplate_ratios(mixed, memory_tier='single_pass')
    b = compute_boilerplate_ratios(mixed, memory_tier='in_memory')
    assert _eq(a, b)
    # 空/哨兵位置两臂均 nan
    for k in (11, 12, 13):  # '', 'nan', None
        assert math.isnan(a[k]) and math.isnan(b[k])


# ── §4-7: vectorizer 参数锁 (类型感知 assert 防 1==1.0 逃逸; ngram_range 穿透) ──

def test_vectorizer_params_locked():
    v = B._make_vectorizer()
    assert type(v.min_df) is int and v.min_df == 1
    assert isinstance(v.max_df, float) and v.max_df == 1.0
    assert v.max_features is None
    assert v.analyzer == 'char_wb'
    # ngram_range 穿透 (非硬编码常量 → 非死参)
    v2 = B._make_vectorizer(ngram_range=(3, 5))
    assert v2.ngram_range == (3, 5)
    # vocabulary 穿透
    v3 = B._make_vectorizer(vocabulary=['  abc '])
    assert v3.vocabulary == ['  abc ']


# ── §4-8: 构念效度 top-k 集合等价 + DF 谱数值等 (log-only, 不比逐序) ──

def test_construct_log_set_equivalence():
    # 直接比对两臂的套话集 (boiler_set) 与 DF 谱: 由不变量 I 精确相等。
    from sklearn.feature_extraction.text import CountVectorizer
    docs = [t for t in _corpus_with_boiler() if isinstance(t, str) and t.strip()
            and len(t.strip()) >= 4]
    thr = B.DF_RATIO_THRESHOLD
    # single-pass boiler_set + DF 谱
    vec = CountVectorizer(analyzer='char_wb', ngram_range=B.NGRAM_RANGE)
    X = vec.fit_transform(docs)
    n = len(docs)
    dfc = np.asarray((X > 0).sum(axis=0)).ravel()
    mask = (dfc / n) >= thr
    feats = vec.get_feature_names_out()
    sp_set = set(feats[np.flatnonzero(mask)])
    sp_spectrum = np.sort(dfc[mask] / n)
    # chunked global_df boiler_set + DF 谱
    gdf = {}
    for s in range(0, n, 4):
        chunk = docs[s:s + 4]
        vc = B._make_vectorizer()
        Xc = vc.fit_transform(chunk)
        fe = vc.get_feature_names_out()
        dc = np.asarray((Xc > 0).sum(axis=0)).ravel()
        for j, ng in enumerate(fe):
            gdf[ng] = gdf.get(ng, 0) + int(dc[j])
    ck_set = {ng for ng, d in gdf.items() if d / n >= thr}
    ck_spectrum = np.sort(np.asarray([gdf[ng] / n for ng in ck_set]))
    assert sp_set == ck_set, 'top-k 套话集不等 (不变量 I 被破)'
    assert np.array_equal(sp_spectrum, ck_spectrum), 'DF 谱数值不等'


# ── §4-9: config 真穿透 (非默认值经 enrich 抵达 compute; 防 KeyError 崩/死接线) ──

def test_config_wiring(monkeypatch):
    captured = {}
    orig = B.compute_boilerplate_ratios

    def _spy(texts, *a, **k):
        captured.update(k)
        return orig(texts, *a, **k)

    monkeypatch.setattr(B, 'compute_boilerplate_ratios', _spy)
    # 注入非默认 config (顶层 boilerplate 块); 断言全部四键穿透 (防某键接线漂移静默失效)。
    # budget 用非默认大值 (不触发 warn/hard 闸, 仅验穿透)。
    _cfg = {'boilerplate': {'chunk_size': 7, 'memory_tier': 'in_memory',
                            'df_dict_budget_warn': 77000000, 'df_dict_budget_hard': 99000000}}
    # enrich 内 from ... import load_config → patch core.config.load_config
    import news_process.core.config as cfg
    monkeypatch.setattr(cfg, 'load_config', lambda: _cfg)
    df = pd.DataFrame({'content_full': _corpus_with_boiler()})
    enrich_with_boilerplate(df)
    assert captured.get('chunk_size') == 7, f'config chunk_size 未穿透到 compute: {captured}'
    assert captured.get('memory_tier') == 'in_memory'
    assert captured.get('df_dict_budget_warn') == 77000000, 'df_dict_budget_warn 未穿透 (接线漂移)'
    assert captured.get('df_dict_budget_hard') == 99000000, 'df_dict_budget_hard 未穿透 (接线漂移)'


def test_config_malformed_graceful(monkeypatch):
    # config 畸值 (chunk_size=null / budget 非数值) → 优雅回落默认, 不裸 TypeError 崩 stage 22
    import news_process.core.config as cfg
    monkeypatch.setattr(
        cfg, 'load_config',
        lambda: {'boilerplate': {'chunk_size': None, 'df_dict_budget_hard': 'oops'}})
    df = pd.DataFrame({'content_full': _corpus_with_boiler()})
    out = enrich_with_boilerplate(df)          # 不应抛 TypeError
    assert 'boilerplate_phrase_ratio_full' in out.columns
    assert not out['boilerplate_phrase_ratio_full'].isna().all()
    # compute 直调畸值亦兜底 (含 None / ±inf(OverflowError) / 非数值字符串)
    ref = compute_boilerplate_ratios(_corpus_with_boiler())
    for bad in (None, float('inf'), float('-inf'), float('nan'), 'x', True):
        r = compute_boilerplate_ratios(_corpus_with_boiler(), chunk_size=bad,
                                       df_dict_budget_warn=bad, df_dict_budget_hard=bad)
        assert _eq(ref, r), f'chunk_size={bad!r} 兜底后应与默认等价 (不崩不漂)'


def test_three_track_multichunk_byte_equal(monkeypatch):
    # P5 dev A/B 固化为单元 gate: enrich 三轨 (full/ctx/ss) 各异文本 + 小 chunk_size 强制多块,
    # in_memory 三轨列须与 single_pass 逐字节等 (装配层 + ctx/ss 多块保护)。
    full = _corpus_with_boiler()
    ctx = [t[:8] if isinstance(t, str) else t for t in full]     # ctx 窗口: 各异文本
    ss = [t[2:10] if isinstance(t, str) else t for t in full]
    # 逐轨 compute A/B (small chunk_size 强制多块)
    for trk_texts in (full, ctx, ss):
        clean_texts = [t for t in trk_texts if isinstance(t, str)]
        a = compute_boilerplate_ratios(clean_texts, memory_tier='single_pass')
        b = compute_boilerplate_ratios(clean_texts, memory_tier='in_memory', chunk_size=2)
        assert _eq(a, b), '三轨某轨 single_pass vs in_memory(多块) 不等'
    # enrich 装配层: 三轨列齐全 (in_memory 默认路径)
    import news_process.core.config as cfg
    monkeypatch.setattr(cfg, 'load_config',
                        lambda: {'boilerplate': {'chunk_size': 2, 'memory_tier': 'in_memory'}})
    df = pd.DataFrame({'content_full': [t for t in full if isinstance(t, str)],
                       'content_ctx': [t for t in ctx if isinstance(t, str)],
                       'content_ss': [t for t in ss if isinstance(t, str)]})
    out = enrich_with_boilerplate(df)
    for trk in ('full', 'ctx', 'ss'):
        assert f'boilerplate_phrase_ratio_{trk}' in out.columns


def test_compute_zero_config_defaults():
    # compute 直调零 config 走模块默认 (不 import config)
    docs = _corpus_with_boiler()
    r = compute_boilerplate_ratios(docs)  # 无 kwargs
    assert len(r) == len(docs)
    assert all(math.isnan(v) or 0.0 <= v <= 1.0 for v in r)


# ── §4-10: fail-loud (disk/auto → SystemExit⊂BaseException 穿透 except Exception; hard 闸 in-loop → SystemExit) ──

@pytest.mark.parametrize('tier', ['disk', 'auto'])
def test_disk_tier_fail_loud_systemexit(tier):
    # tier2 DEFERRED → SystemExit (⊂BaseException), 穿透调用方 `except Exception`, 绝不静默丢列
    with pytest.raises(SystemExit, match='DEFERRED'):
        compute_boilerplate_ratios(_corpus_with_boiler(), memory_tier=tier)


def test_disk_tier_propagates_through_broad_except():
    # 模拟调用方 tone_words 的 `except Exception` graceful-skip: SystemExit 须穿透, 不被吞
    caught_as_exception = False
    try:
        try:
            compute_boilerplate_ratios(_corpus_with_boiler(), memory_tier='disk')
        except Exception:  # noqa: BLE001 — 模拟 tone_words:2344 宽 except
            caught_as_exception = True
    except SystemExit:
        pass  # 期望: SystemExit 穿透 except Exception
    assert not caught_as_exception, 'disk tier 的 SystemExit 被 except Exception 吞 (fail-loud 被击穿)'


def test_nonpositive_budget_warns_gate_disabled(caplog):
    import logging
    with caplog.at_level(logging.WARNING):
        compute_boilerplate_ratios(_corpus_with_boiler(), memory_tier='in_memory',
                                   df_dict_budget_hard=0, df_dict_budget_warn=-1)
    msgs = ' '.join(r.message for r in caplog.records)
    assert '硬闸已禁用' in msgs, 'budget_hard≤0 应 loud 警告闸已禁用 (防静默 footgun)'


def test_hard_budget_systemexit_in_loop():
    docs = _corpus_with_boiler()
    # 极小硬上限 → Pass1 循环内即 SystemExit (in-loop, 非 post-loop)
    with pytest.raises(SystemExit) as ei:
        compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=2,
                                   df_dict_budget_hard=5)
    assert str(ei.value), 'SystemExit 应携带可操作消息'


def test_hard_budget_in_loop_not_post_loop(monkeypatch):
    # 证明硬闸 in-loop: 在第 2 块累加时即触发 (Pass1 未处理完全部块)
    docs = _corpus_with_boiler()
    from sklearn.feature_extraction.text import CountVectorizer
    call_count = {'n': 0}
    orig = CountVectorizer.fit_transform

    def _count(self, raw, *a, **k):
        call_count['n'] += 1
        return orig(self, raw, *a, **k)

    monkeypatch.setattr(CountVectorizer, 'fit_transform', _count)
    # chunk_size=2 → 8 块; hard=极小 → 应在前几块即 raise, 而非跑完 8 块
    with pytest.raises(SystemExit):
        compute_boilerplate_ratios(docs, memory_tier='in_memory', chunk_size=2,
                                   df_dict_budget_hard=5)
    n_chunks_total = math.ceil(len([t for t in docs if isinstance(t, str) and t.strip()
                                    and len(t.strip()) >= 4]) / 2)
    assert call_count['n'] < n_chunks_total, \
        f'硬闸 post-loop (跑完 {call_count["n"]} 块); 应 in-loop 提前中止 (总 {n_chunks_total} 块)'


def test_unknown_tier_falls_back_in_memory():
    docs = _corpus_with_boiler()
    ref = compute_boilerplate_ratios(docs, memory_tier='in_memory')
    got = compute_boilerplate_ratios(docs, memory_tier='bogus_tier')
    assert _eq(ref, got), '未知 tier 应回退 in_memory'
