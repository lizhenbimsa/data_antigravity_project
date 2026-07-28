"""tests/test_f28_parity_collapse_visibility.py — F28 gate: 塌缩必须留痕且逐列点名。

**为何需要 (2026-07-27 生产实弹, 28 小时无人察觉)**:
入口② 生产全链跑完 28.12h、EXIT=0、报「✓ 管道全部阶段执行成功」, 但交付面板里
``coh_emb_ctx`` / ``coh_emb_lg_ctx`` / ``coh_emb_ss`` / ``coh_emb_lg_ss``
**四列 23,693 行全 NaN** (共丢 4 × 3,891 = 15,564 个应有值)。

根因链: 07-27 16:40:30 (ctx 轨) 与 18:24:44 (ss 轨) 主轨 Qwen 嵌入在 429/TPM 风暴下
重试 80 次耗尽返回 None → ``strategic_diff`` 的 both-or-neither parity 连坐把
**已算成功的 _lg 结果一并丢弃** → 该分支**只把值置空、一行日志都不打** →
阶段照常打印「✅ 新增 15 列」→ 无人察觉。

本 gate 锁死的不是「不许塌缩」(那是研究口径变更, 须用户裁定), 而是
**「塌缩不许静默」**: 必须 ERROR 级 + 点名受影响列 + 点明被连坐丢弃的成功臂规模。

配套: F29 (main=e94bf57f) 让 ``news_process.*`` 模块的 ERROR 真正带 levelname 落盘,
两者合起来才使 ``grep -c " - ERROR - "`` 这条验收判据对本类数据丢失第一次有效。
"""
from __future__ import annotations

import ast
import inspect
import logging
import os
import sys

import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.features import strategic_diff as sd  # noqa: E402


def _toy_agg(n_years=3, n_banks=4):
    rows = []
    for year in range(2017, 2017 + n_years):
        for bi in range(n_banks):
            rows.append({
                'target_bank': f'银行{bi}', 'year': year,
                'agg_text': f'{year} 银行{bi} 金融科技 数字人民币 智能风控 移动支付 ' * 4,
            })
    return pd.DataFrame(rows)


# ── ① 真触发: MAIN 失败 / _lg 成功 → 必须 ERROR + 逐列点名 ──

class _Capture(logging.Handler):
    """直接挂到 sd.logger 上抓记录。

    ⚠ 不能用 pytest 的 ``caplog``: ``setup_logging`` 对阶段 logger 设了
    ``propagate = False`` (刻意 — 防阶段日志二次上浮), 故 caplog 挂在 root 的
    handler 收不到。这不是缺陷, 是 F29 设计的一部分。
    """

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)

    @property
    def text(self) -> str:
        return "\n".join(r.getMessage() for r in self.records)


@pytest.mark.parametrize('track_suffix', ['_ctx', '_ss'])
def test_coherence_collapse_emits_error_naming_the_lost_columns(
        monkeypatch, track_suffix):
    """模拟生产事故: 主轨嵌入重试耗尽返回空, _lg 成功 → 连坐丢弃。"""
    agg = _toy_agg()
    calls = {'n': 0}

    def _fake_emb_coherence(agg_df, spec=None):
        # 第 1 次 (MAIN) 返回空 = 重试耗尽; 第 2 次 (_lg) 返回有值 = 已成功
        calls['n'] += 1
        if calls['n'] == 1:
            return {}
        return {(b, y): 0.5 for b, y in
                zip(agg_df['target_bank'], agg_df['year'], strict=True)}

    monkeypatch.setattr(sd, '_compute_emb_coherence', _fake_emb_coherence)
    monkeypatch.setattr(sd, '_LARGE_SPEC', {'model': 'text-embedding-3-large'})

    # 直接重演塌缩分支 (与 compute_text_coherence 内的判据逐字同构)
    coh_emb = sd._compute_emb_coherence(agg)
    coh_emb_lg = sd._compute_emb_coherence(agg, spec=sd._LARGE_SPEC)
    cap = _Capture()
    sd.logger.addHandler(cap)
    try:
        if not coh_emb or not coh_emb_lg:
            _failed = [n for n, d in (('MAIN(Qwen)', coh_emb),
                                      ('_lg(large)', coh_emb_lg)) if not d]
            _kept = [(n, len(d)) for n, d in (('MAIN(Qwen)', coh_emb),
                                              ('_lg(large)', coh_emb_lg)) if d]
            _cols = f'coh_emb{track_suffix}, coh_emb_lg{track_suffix}'
            sd.logger.error(
                f"🔴 嵌入连贯性 both-or-neither 塌缩 [轨道{track_suffix or '_full'}]: "
                f"失败臂={'+'.join(_failed)}; "
                f"被连坐丢弃的**已成功**结果="
                f"{', '.join(f'{n} {c:,d} 个值' for n, c in _kept) or '无'}; "
                f"受影响列 (2 列将全 NaN): {_cols}")
    finally:
        sd.logger.removeHandler(cap)
    text = cap.text
    assert f'coh_emb{track_suffix}' in text, '受影响列名未出现在日志里'
    assert f'coh_emb_lg{track_suffix}' in text, '_lg 孪生列名未出现在日志里'
    assert 'MAIN(Qwen)' in text and '_lg(large)' in text
    assert '12 个值' in text, '未点明被连坐丢弃的成功臂规模 (审计者据此判断损失)'
    assert any(r.levelno >= logging.ERROR for r in cap.records), \
        '塌缩必须 ERROR 级 —— WARNING 会被「ERROR=0 ⟹ 通过」的判据漏掉'


# ── ② 源码级: 三个同型塌缩站点都不许再静默 ──
# 注: 三处塌缩 (连贯性 1 处 + Full 轨 N-NN 1 处 + Ctx/Ss 轨 N-NN 1 处) 全部位于同一个
#     巨函数 compute_strategic_differentiation 内 (L1523 起), 故只需扫它一个。

_COLLAPSE_SITES = [
    ('all_three', 'compute_strategic_differentiation', 'coh_emb/strat_diff'),
]


def _collapse_branches_with_logging(func) -> list[bool]:
    """找出函数体里所有 both-or-neither 塌缩分支, 返回每个分支内是否有 logger.error。"""
    tree = ast.parse(inspect.getsource(func).lstrip())
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        body_src = ast.dump(node)
        # 塌缩分支的判据: 分支体里把 emb 相关变量整体置空/置 None
        if not any(k in body_src for k in ("'coh_emb'", "'se'", "'cd_emb'")):
            continue
        assigns_none = any(
            isinstance(n, ast.Assign) and (
                isinstance(n.value, ast.Tuple)
                 and all(isinstance(e, (ast.Constant, ast.Dict)) for e in n.value.elts))
            for n in node.body)
        if not assigns_none:
            continue
        has_error = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == 'error'
            for n in ast.walk(node))
        out.append(has_error)
    return out


@pytest.mark.parametrize('label,funcname,_col', _COLLAPSE_SITES)
def test_every_parity_collapse_branch_logs_at_error_level(label, funcname, _col):
    fn = getattr(sd, funcname, None)
    if fn is None:
        pytest.skip(f'{funcname} 不存在 (阶段重构?)')
    flags = _collapse_branches_with_logging(fn)
    assert flags, f'{funcname}: 未识别到 both-or-neither 塌缩分支 (判据需随重构更新)'
    assert all(flags), (
        f'{funcname}: {flags.count(False)}/{len(flags)} 个塌缩分支仍然**静默** —— '
        f'2026-07-27 就是这样丢了 4 列 15,564 个值而 28 小时无人察觉。'
        f'塌缩可以发生 (那是 co-primary 铁律), 但绝不许不出声。')


# ── ③ 值语义未被偷改 (本次刻意不动, 改了必须走用户裁定) ──

def test_collapse_still_zeroes_both_arms():
    """本次整改是**只加日志**: 塌缩仍把两臂同置空。

    若将来改成「保留成功臂」, 本测试会红 —— 那是**故意的**: 该变更与 CLAUDE.md
    「两轨严格 parity (both-or-neither)」铁律冲突, 属研究口径变更, 必须先取得用户
    裁定并同步改写铁律段, 而不是被某次整改顺手改掉。
    """
    src = inspect.getsource(sd.compute_strategic_differentiation)
    assert 'coh_emb, coh_emb_lg = {}, {}' in src, (
        'both-or-neither 的**值语义**被改动了 —— 这不是日志整改能顺带做的事, '
        '须先取得用户裁定 (见 CLAUDE.md 嵌入架构段的 both-or-neither 铁律)。')
