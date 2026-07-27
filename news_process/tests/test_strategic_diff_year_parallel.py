"""tests/test_strategic_diff_year_parallel.py — F25/F26 gate: 逐年并行 + LDA 线程钉死。

**为何需要 (2026-07-27 生产实弹)**: stage 40 跑满 21,600s 被父端强杀。逐子步骤归因显示
「相邻期文本连贯性」是第二大极 (单轨 TF-IDF char 28 分钟 + word 25 分钟, 三轨 ≈5h),
全程只用 32 逻辑核中的 1 核。F25 把该族三个函数的逐年循环改进程并行。

**F26 (同批发现)**: 首版真数据 A/B 抓到 `coh_lda` 并行臂与串行臂 265/277 个值位模式不同
(~1e-13)。根因探针确证是 **BLAS 线程数差异**, 非并行本身 —— 全 BLAS 钉 1 时 277/277
逐位相同。这暴露了一个既有隐患: `coh_lda*` / `*_lda` 族数值**本就依赖运行机器的 BLAS
线程数**, 而 fix(omni-g-strategic-16) 当初把 LDA `n_jobs=-1` 改 1 正是为消除核数依赖 ——
那次只堵了 sklearn 的 E-step 切片, 没堵住底层 BLAS。F26 在 LDA fit 现场钉线程补上,
顺带实测快 5.5× (775.2s → 140.0s)。

不变量:
  ① 任务切分与串行循环**同序同筛选** (漂移即静默改测度);
  ② 串/并两条路径产出**逐位相同** (不是 allclose);
  ③ 两个 LDA 现场都必须在 `_threadpool_limits(limits=1)` 域内 (F26 防回退);
  ④ 三个 worker 体内**零 logger 调用** —— worker 会被父进程直接调用 (串行回落),
     在里面降 logger 级别会掐掉整个 stage 的 INFO 日志 (自造 F16);
  ⑤ worker 数有上限 (n_jobs=-1 在 stage 22 已实弹 MemoryError)。
"""
from __future__ import annotations

import inspect
import os
import struct
import sys

import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.features import strategic_diff as sd  # noqa: E402

_WORKERS = ('_fluidity_year_worker', '_tfidf_coherence_year_worker',
            '_lda_coherence_year_worker')


def _toy_agg(n_years=6, n_banks=6):
    """合成 bank-year 超级文档: 年数 > 阈值 → 并行分支真触发。"""
    rows = []
    for yi, year in enumerate(range(2015, 2015 + n_years)):
        for bi in range(n_banks):
            rows.append({
                'target_bank': f'银行{bi}',
                'year': year,
                'agg_text': (f'第{year}年 银行{bi} 金融科技 数字人民币 智能风控 '
                             f'区块链 供应链金融 移动支付 ' * (3 + (bi + yi) % 4)),
            })
    return pd.DataFrame(rows)


# ── ① 任务切分与串行同序同筛选 ──

def test_task_split_matches_serial_loop_exactly():
    agg = _toy_agg()
    tasks = sd._adjacent_year_tasks(agg)
    # 串行循环的等价重演
    expect = []
    for year in sorted(agg['year'].unique()):
        df_t = agg[agg['year'] == year]
        df_t1 = agg[agg['year'] == year - 1]
        if df_t1.empty:
            continue
        expect.append(int(year))
    assert [t[0] for t in tasks] == expect, '任务年份序/筛选与串行循环不一致'
    for (year, dt, dt1) in tasks:
        src_t = agg[agg['year'] == year]
        src_t1 = agg[agg['year'] == year - 1]
        assert list(dt['target_bank']) == list(src_t['target_bank'])
        assert list(dt['agg_text']) == list(src_t['agg_text'])
        assert list(dt1['target_bank']) == list(src_t1['target_bank'])


def test_first_year_is_skipped():
    agg = _toy_agg()
    first = int(sorted(agg['year'].unique())[0])
    assert first not in [t[0] for t in sd._adjacent_year_tasks(agg)], \
        '首年无 t-1, 必须跳过 (与串行 df_t1.empty → continue 同)'


# ── ② 串/并逐位相同 ──

def _bits(v):
    return struct.pack('<d', float(v))


@pytest.mark.parametrize('fn,args', [
    (lambda a: sd._compute_tfidf_coherence(a, 'char'), 'tfidf_char'),
    (lambda a: sd._compute_tfidf_coherence(a, 'word'), 'tfidf_word'),
    (lambda a: sd._compute_lda_coherence(a), 'lda'),
    (lambda a: sd._compute_fluidity(a, 'char'), 'flu_char'),
])
def test_serial_and_parallel_paths_are_bit_identical(fn, args, monkeypatch):
    agg = _toy_agg()
    assert len(sd._adjacent_year_tasks(agg)) >= sd._PROC_PARALLEL_MIN_YEARS
    par = fn(agg)                                    # 并行路径
    monkeypatch.setattr(sd, '_PROC_PARALLEL_MIN_YEARS', 10_000)
    ser = fn(agg)                                    # 强制串行回落
    assert set(ser) == set(par), f'{args}: 键集合不同'
    bad = [k for k in ser if _bits(ser[k]) != _bits(par[k])]
    assert not bad, (
        f'{args}: {len(bad)}/{len(ser)} 个值位模式不同 —— 并行**不得**改数。'
        f'样例: {[(k, ser[k], par[k]) for k in bad[:3]]}')


# ── ③ F26: 两个 LDA 现场必须钉线程 ──

@pytest.mark.parametrize('fname', ['_build_lda_jsd_matrix', '_lda_coherence_year_worker'])
def test_lda_fit_is_wrapped_in_threadpool_limit(fname):
    src = inspect.getsource(getattr(sd, fname))
    assert '_threadpool_limits(limits=1)' in src, (
        f'{fname} 的 LDA fit 未包在 _threadpool_limits(limits=1) 内 —— '
        f'不钉 BLAS 线程时该函数数值随机器线程数漂 ~1e-13 (2026-07-27 实测 265/277 键), '
        f'且慢 5.5×。fix(omni-g-strategic-16) 的 n_jobs=1 只堵了 sklearn 层, 堵不住 BLAS。')
    assert 'fit_transform' in src


# ── ④ worker 体内零 logger 调用 ──

@pytest.mark.parametrize('fname', _WORKERS)
def test_worker_body_has_no_logger_calls(fname):
    # 走 AST 而非字符串扫描: docstring 里提到 "logger.warning" 是**说明文字**, 不是调用
    # (首版判据在此误报, 2026-07-27)。只认真正的 `logger.<attr>(...)` 调用节点。
    import ast
    tree = ast.parse(inspect.getsource(getattr(sd, fname)).lstrip())
    offenders = [
        f'line {n.lineno}: logger.{n.func.attr}(...)'
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == 'logger'
    ]
    assert not offenders, (
        f'{fname} 体内出现 logger 调用: {offenders} —— worker 会被父进程直接调用 '
        f'(串行回落 / LDA 路径), 在里面动 logger 会掐掉整个 stage 的 INFO 日志。'
        f'告警一律回传父端 emit。')


def test_no_silence_worker_logging_helper_resurrected():
    assert not hasattr(sd, '_silence_worker_logging'), (
        '`_silence_worker_logging` 不得复活 —— 串行回落会在父进程执行它, '
        '等于自造一个 F16 (日志落空)。')


# ── ⑤ worker 数上限 ──

def test_proc_workers_is_capped():
    assert sd._proc_workers(10_000) <= sd._PROC_PARALLEL_MAX_WORKERS
    assert sd._proc_workers(1) == 1
    assert sd._proc_workers(3) <= 3
    assert sd._PROC_PARALLEL_MAX_WORKERS <= 16, (
        'worker 上限过高 — 每 worker 各持一份注入 607 词的 jieba Trie + sklearn 词表; '
        'stage 22 已实弹 n_jobs=-1 → MemoryError')
