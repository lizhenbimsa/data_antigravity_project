"""tests/test_track_nan_asymmetry_guard.py — S10 gate: 三轨「不对称全空」守卫。

**事故原型 (2026-07-27, 必须能被本 gate 重现并抓住)**:
stage 40 跑满 28.12 小时、全部阶段 ✓、``grep -c " - ERROR - "`` **= 0**,
而最终面板里这四列 **100% NaN**:
    coh_emb_ctx · coh_emb_ss · coh_emb_lg_ctx · coh_emb_lg_ss
共丢 15,564 个值。成因是两次 Qwen 嵌入重试耗尽 (16:40:30 ctx / 18:24:44 ss),
both-or-neither 把**已经算成功的 `_lg` 臂**也一并置 NaN。
当时的验收判据完全瞎: 零 ERROR, 且没有任何一行日志点名这四列。

三道防线各司其职, 本文件锁的是第三道:
  · F29 (e94bf57f) — 让 ERROR 真的能落盘 (此前阶段 logger 链上无 handler);
  · S3  (ec39ac3b) — 在崩塌**现场**逐列点名 (产出侧);
  · S10 (本 gate)  — 在**验收侧**兜底: 不管未来换成哪条崩塌路径, 只要症状是
                     "同族一轨有值 / 另一轨整列空", 就必须 loud ERROR。

**刻意不做"凡全 NaN 就报错"**: T=2 dev 与未播种轨上大量列合法全 NaN, 那样报只会
变成噪声、进而被无视 —— 那是告警失效的经典路径。判据取"列**存在**却整列空, 同族
别的轨却有值", 因为轨整体缺失时列压根不会被创建, 故此状态无歧义。
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.panel import export as ex  # noqa: E402

_N = 20


class _Cap(logging.Handler):
    """⚠ 不用 pytest ``caplog``: 阶段 logger 是 ``propagate=False`` (F29 刻意设计),
    caplog 挂 root 上什么也抓不到。2026-07-28 这个坑已在 F28/S5 上各踩过一次。"""

    def __init__(self):
        super().__init__()
        self.recs: list[logging.LogRecord] = []

    def emit(self, record):
        self.recs.append(record)

    def at(self, level):
        return [r.getMessage() for r in self.recs if r.levelno == level]

    @property
    def errors(self):
        return self.at(logging.ERROR)

    @property
    def text(self):
        return '\n'.join(r.getMessage() for r in self.recs)


def _run(panel: pd.DataFrame) -> _Cap:
    cap = _Cap()
    ex.logger.addHandler(cap)
    try:
        ex._log_track_nan_asymmetry(panel)
    finally:
        ex.logger.removeHandler(cap)
    return cap


def _vals():
    return np.linspace(0.1, 0.9, _N)


def _nans():
    return np.full(_N, np.nan)


# ── ① F28 事故原样重现 ──

def test_f28_incident_is_caught():
    """coh_emb: full 有 6,224 值 / ctx·ss 全空 —— 当年零 ERROR, 现在必须报。"""
    panel = pd.DataFrame({
        'target_bank': [f'行{i}' for i in range(_N)],
        'coh_emb_full': _vals(),
        'coh_emb_ctx': _nans(),
        'coh_emb_ss': _nans(),
        'coh_emb_lg_full': _vals(),
        'coh_emb_lg_ctx': _nans(),
        'coh_emb_lg_ss': _nans(),
    })
    cap = _run(panel)
    errs = '\n'.join(cap.errors)
    assert errs, (
        '三轨不对称全空未报 ERROR —— 这正是 2026-07-27 那次「28 小时全绿但丢 4 列」'
        '之所以能通过验收的原因。')
    for col in ('coh_emb_ctx', 'coh_emb_ss', 'coh_emb_lg_ctx', 'coh_emb_lg_ss'):
        assert col in errs, f'ERROR 未点名全空列 {col} —— 不点名就无法定位'
    assert 'coh_emb_full' in errs and 'coh_emb_lg_full' in errs, \
        'ERROR 未同时点名"有值轨", 无法判断丢了多少'


def test_lg_family_is_separate_from_main():
    """`_lg` 中置 ⟹ coh_emb 与 coh_emb_lg 必须是两个独立族, 各自 3 轨。"""
    panel = pd.DataFrame({
        'coh_emb_full': _vals(), 'coh_emb_ctx': _vals(), 'coh_emb_ss': _vals(),
        'coh_emb_lg_full': _vals(), 'coh_emb_lg_ctx': _nans(),
        'coh_emb_lg_ss': _nans(),
    })
    cap = _run(panel)
    errs = '\n'.join(cap.errors)
    assert 'coh_emb_lg_ctx' in errs, '_lg 族的不对称未被检出'
    # MAIN 族三轨都有值 → 不应被点名为全空
    assert '族 coh_emb:' not in errs, \
        f'MAIN 族三轨齐全却被误报 (说明 _lg 被并进了 MAIN 族): {errs[:300]}'


# ── ② 合法场景不得误报 (否则告警会被无视) ──

def test_whole_family_empty_is_not_an_error():
    """三轨全空 = 该族整体未播种 (T=2 dev 常态), 只记不报。"""
    panel = pd.DataFrame({
        'coh_emb_full': _nans(), 'coh_emb_ctx': _nans(), 'coh_emb_ss': _nans(),
    })
    cap = _run(panel)
    assert not cap.errors, f'整族全空被误报为 ERROR: {cap.errors}'


def test_missing_track_column_is_not_an_error():
    """轨整体缺列 (content_ss 未物化) → 列不存在, 无从比较, 不报。"""
    panel = pd.DataFrame({'coh_emb_full': _vals(), 'coh_emb_ctx': _vals()})
    cap = _run(panel)
    assert not cap.errors, f'仅两轨且都有值却被误报: {cap.errors}'


def test_all_tracks_filled_is_not_an_error():
    panel = pd.DataFrame({
        'coh_emb_full': _vals(), 'coh_emb_ctx': _vals(), 'coh_emb_ss': _vals(),
    })
    cap = _run(panel)
    assert not cap.errors


def test_single_track_family_is_not_an_error():
    """无三轨孪生的列 (如 surface_staleness, 见 CLAUDE.md carve-out) 不参与比较。"""
    panel = pd.DataFrame({'surface_staleness_full': _nans()})
    cap = _run(panel)
    assert not cap.errors


def test_partial_nan_is_not_an_error():
    """部分缺失是常态 (零报道 bank-year), 只有**整列**空才算异常。"""
    v = _vals().copy()
    v[:_N // 2] = np.nan
    panel = pd.DataFrame({
        'coh_emb_full': _vals(), 'coh_emb_ctx': v, 'coh_emb_ss': _vals(),
    })
    cap = _run(panel)
    assert not cap.errors, f'部分缺失被误报: {cap.errors}'


# ── ③ 诊断绝不崩阶段 ──

def test_never_raises_on_degenerate_input():
    for p in (pd.DataFrame(), pd.DataFrame({'a_full': []}), None):
        _run(p)          # 不抛即通过


def test_never_raises_on_non_numeric_columns():
    panel = pd.DataFrame({
        'note_full': ['甲'] * _N,
        'note_ctx': [None] * _N,
        'note_ss': ['乙'] * _N,
        'coh_emb_full': _vals(), 'coh_emb_ctx': _nans(), 'coh_emb_ss': _nans(),
    })
    cap = _run(panel)
    assert cap.errors, '异构列不得让扫描静默放过真正的不对称'


# ── ④ 扫描摘要恒出 (即便无异常) ──

def test_summary_line_always_emitted():
    panel = pd.DataFrame({
        'coh_emb_full': _vals(), 'coh_emb_ctx': _vals(), 'coh_emb_ss': _vals(),
    })
    cap = _run(panel)
    assert '三轨完整性扫描' in cap.text, \
        '无异常时也必须留下扫描摘要 —— 否则无法区分"扫过且干净"与"根本没扫"'


def test_guard_is_wired_into_log_diagnostics():
    import inspect
    src = inspect.getsource(ex.log_diagnostics)
    assert '_log_track_nan_asymmetry' in src, \
        '守卫未挂进 log_diagnostics —— 写了不调用等于没写'
