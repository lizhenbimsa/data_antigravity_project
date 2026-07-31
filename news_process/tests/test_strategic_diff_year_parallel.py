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

import ast
import inspect
import logging
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


# ════════════════════════════════════════════════════════════════════════════
# ⑥ 流式回调 on_result (2026-07-28, S5 引入)
# ════════════════════════════════════════════════════════════════════════════
# **为何需要**: 老路径整批算完才返回 ⟹ 调用方只能等全部结束再打日志。实弹后果:
# policy_similarity 生产上跑 10.57 小时, 其间 111 条 "LDA K=…" 是唯一进度信号,
# 缓冲到最后再吐 = 十小时日志空白; 且 2026-07-27 stage 40 曾被超时闸强杀 ——
# 那种情况下缓冲的日志连同进度**全部丢失**。
# joblib `return_as='generator'` 仍按**提交序**产出, 故顺序保证不变。


def _pid_worker(task):
    """回传 (任务, PID) —— 据此判断是否真起了子进程。"""
    return (task, os.getpid())


def _child_only_boom_worker(task):
    """只在**子进程**里崩 —— 模拟 "worker 被 OS 杀掉但串行能跑通"。"""
    import multiprocessing
    if multiprocessing.parent_process() is not None:
        raise RuntimeError('模拟 worker 在子进程中被杀')
    return (task, os.getpid())


def test_on_result_streams_in_submission_order_serial():
    seen = []
    out = sd._run_year_tasks(list(range(3)), _pid_worker,
                             on_result=seen.append)          # 3 < 4 → 串行
    assert [t for t, _ in seen] == [0, 1, 2], f'串行回调序错: {seen}'
    assert out == seen, '返回 list 与回调所见必须一致'


def test_on_result_streams_in_submission_order_parallel():
    seen = []
    n = 16
    out = sd._run_year_tasks(list(range(n)), _pid_worker, on_result=seen.append)
    assert [t for t, _ in seen] == list(range(n)), (
        f'并行回调**不是提交序**: {[t for t, _ in seen]} —— '
        "return_as='generator' 必须保持提交序 (不可误用 generator_unordered), "
        '否则日志行序与归并序都会漂。')
    assert out == seen
    assert len({p for _, p in seen if p != os.getpid()}) > 0, \
        '并行臂没有真起子进程, 本测试失去意义'


def test_on_result_called_exactly_once_per_task():
    cnt = {}

    def _tally(r):
        cnt[r[0]] = cnt.get(r[0], 0) + 1

    sd._run_year_tasks(list(range(16)), _pid_worker, on_result=_tally)
    assert sorted(cnt) == list(range(16))
    assert set(cnt.values()) == {1}, f'有任务被回调多次或漏回调: {cnt}'


def test_default_path_unchanged_without_on_result():
    """不传 on_result 时必须走老路径 (源码级: 仍有非流式的 Parallel 调用)。"""
    src = inspect.getsource(sd._run_year_tasks)
    assert "if on_result is None:" in src, 'on_result 缺省分支消失 — 老路径不再受保护'
    assert "return_as='generator'" in src, '流式路径缺失'
    out = sd._run_year_tasks(list(range(16)), _pid_worker)
    assert [t for t, _ in out] == list(range(16))


class _Cap(logging.Handler):
    """⚠ 不能用 pytest 的 ``caplog``: 阶段 logger 是 ``propagate=False``
    (F29 的刻意设计 — 阶段日志不外溢到 root), caplog 挂在 root 上什么也抓不到。
    2026-07-28 这个坑在 F28 与本条上各踩过一次, 故显式挂 Handler。"""

    def __init__(self):
        super().__init__()
        self.msgs: list[str] = []

    def emit(self, record):
        self.msgs.append(record.getMessage())


def test_streaming_oom_fallback_reruns_only_remaining():
    """流式下并行崩掉 → 只补跑剩余, 不整批重来, 且结果完整且按序。"""
    seen = []
    cap = _Cap()
    sd.logger.addHandler(cap)
    try:
        out = sd._run_year_tasks(list(range(16)), _child_only_boom_worker,
                                 on_result=seen.append)
    finally:
        sd.logger.removeHandler(cap)
    assert [t for t, _ in out] == list(range(16)), (
        f'兜底后结果不完整或乱序: {[t for t, _ in out]}')
    assert all(p == os.getpid() for _, p in out), \
        '兜底应在父进程串行完成 (子进程 worker 必崩)'
    msgs = ' '.join(cap.msgs)
    assert '回落串行补跑' in msgs and '已完成' in msgs, (
        f'流式兜底未 loud ERROR 或文案退化: {msgs[:300]}')


# ══════════════════════════════════════════════════════════════════════════
# S13 (2026-07-31) gate: 主逐年循环 (`compute_strategic_differentiation`) 的并行
# ══════════════════════════════════════════════════════════════════════════
# F25 只并行了三个「相邻期」循环; 本函数**自己的**三轨逐年循环才是大头, S13 补上。
# 这里锁四件事, 每一件都对应一个具体的翻车方式:
#   ① 嵌入 API 并发必须按 worker 数**等比缩小** —— 否则 P×250 打爆 TPM, 重演 F28
#      (重试耗尽 → 整族嵌入列静默 NaN)。这是 S13 唯一的硬阻断项。
#   ② 并行阈值必须把 T=2 dev 与单测留在串行 (桩不传播进 loky ⟹ 测试当场失真)。
#   ③ worker 体内零 logger 调用 (同 F25 的 ④, 串行回落路径会在父进程跑它)。
#   ④ 任务切分与串行循环同序同筛选, 且 <3 家银行的年份**照样进池** (由 worker 内
#      守卫早退) —— 在切分处提前筛掉会让告警时序偏离串行。

@pytest.mark.parametrize('n_jobs', [2, 8, 12])
def test_s13_total_emb_concurrency_never_exceeds_budget(monkeypatch, n_jobs):
    """① 端点**总**并发 = per-worker × worker 数 ≤ 预算, 绝不能是 P × 预算。

    ⚠ 2026-08-01 重写: 初版用「写 os.environ 让新 worker import 时读到」并且在
    "运维已显式设过"时**不缩放** —— 那把运维给的**总**预算当成了 per-worker 预算,
    运维设 6 反而变成 12×6=72, 恰好制造它声称要防的 F28。现改为显式传参 +
    总预算语义, 两条分支 (未设 / 已设) 都必须满足总量上界。
    """
    for raw in (None, '6', '250'):
        if raw is None:
            monkeypatch.delenv(sd._EMB_CONCURRENCY_ENV, raising=False)
            budget = sd._EMB_CONCURRENCY_BASELINE
        else:
            monkeypatch.setenv(sd._EMB_CONCURRENCY_ENV, raw)
            budget = int(raw)
        per = sd._worker_emb_concurrency(n_jobs)
        assert per >= 1
        # ⚠ 口径: "总量 ≤ 预算" 是**驱动器**的不变量 (它会在预算 < 并行度时压 n_jobs),
        #   不是本函数单独能保证的 —— 本函数只负责 "预算够用时按 worker 数均分"。
        #   驱动器侧的封顶由 `test_s13_parallelism_capped_by_emb_budget` 锁。
        if n_jobs <= budget:
            assert per * n_jobs <= budget, (
                f'env={raw} n_jobs={n_jobs}: 总并发 {per}×{n_jobs}={per * n_jobs} '
                f'超出预算 {budget} —— 这正是 F28 的成因')
            assert per == budget // n_jobs, '预算够用时应按 worker 数均分'
        else:
            assert per == 1, '预算不足时每 worker 保底 1 (总量由驱动器压 n_jobs 兜住)'


def test_s13_operator_env_is_treated_as_total_budget(monkeypatch):
    """① 之二: 运维经 env 给的是**总**预算, 不是 per-worker 预算。"""
    monkeypatch.setenv(sd._EMB_CONCURRENCY_ENV, '6')
    assert sd._emb_total_budget() == 6
    assert sd._worker_emb_concurrency(12) == 1, (
        '运维设 6 + 12 worker 应得 per-worker=1 (总 12→被 max(1,·) 抬到 12), '
        '绝不能让每个 worker 各开 6 (总 72)')
    monkeypatch.setenv(sd._EMB_CONCURRENCY_ENV, 'oops')
    assert sd._emb_total_budget() == sd._EMB_CONCURRENCY_BASELINE, '非整数应回落基线'


@pytest.mark.parametrize('raw', ['0', '-1', '-250'])
def test_s13_emb_budget_clamps_nonpositive_to_one(monkeypatch, raw):
    """① 之二 b: env ≤ 0 必须 **clamp 到 1**, 绝不回落基线 250。

    ⚠ 本闸 2026-08-01 第三轮终审补: 上一个 commit 修了这条并在 message 里写
    "实测 0/-3 → 1", 但那是**手工探针**, 仓内没有任何测试会因回退而变红 ——
    把 `return 1` 改回 `return _EMB_CONCURRENCY_BASELINE` 当时全绿。
    这与本轮反复批评的"空闸"是同一形态: 只有会红的闸才算数。

    口径依据: 项目其它嵌入现场读同一个 env 的方式是
    ``Semaphore(max(1, min(EMB_API_CONCURRENCY, n_batches)))`` ⟹ 0/负数在那里等于 1。
    而"把并发调到极小"正是撞 TPM 后的标准止血手段, `0` 是踩刹车最常见写法 ——
    若这里回落 250, 运维想刹车反而拿到 S13 独家 240 并发, 恰是 F28 成因。
    """
    monkeypatch.setenv(sd._EMB_CONCURRENCY_ENV, raw)
    assert sd._emb_total_budget() == 1, (
        f'{raw} 应 clamp 到 1 而非回落基线 {sd._EMB_CONCURRENCY_BASELINE} —— '
        '运维踩刹车反而拿到满并发, 正是 F28 的成因')
    # 并发数**不为 0**: 下游 asyncio.Semaphore(0) 会永久阻塞。
    assert sd._worker_emb_concurrency(12) >= 1


def test_s13_no_env_mutation_anywhere(monkeypatch):
    """① 之三: 整条路径**不得**再写 os.environ (初版靠它传参, 三重脆弱)。

    ⓐ 把运维值当 per-worker; ⓑ loky 复用常驻 worker 时对已存在的 executor 是 no-op;
    ⓒ 永不还原, 泄漏给同进程后续步骤 (runner:1846 的 compute_authoritative_similarity)。
    """
    # ⚠ 用 **AST** 扫对 `os.environ` 的写入 (下标赋值 / setdefault / update),
    #   不用文本匹配。上一版第一条断言写的是 `'os.environ[sd._EMB_CONCURRENCY_ENV]'
    #   not in src` —— 模块源码里根本不会出现 `sd.` 前缀, 该断言**结构上恒为真**,
    #   与本轮自己刚逮到的 F28 空闸 (`assert flags and all(flags)` 在 [True] 上恒成立)
    #   是同一形态。变异测试实证: 那条对 5 种回归形态捕获 0/5。
    tree = ast.parse(inspect.getsource(sd))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (isinstance(tgt, ast.Subscript)
                        and isinstance(tgt.value, ast.Name)
                        and tgt.value.id == 'os'):
                    bad.append('os[...] = ')
                if (isinstance(tgt, ast.Subscript)
                        and isinstance(tgt.value, ast.Attribute)
                        and tgt.value.attr == 'environ'):
                    bad.append(f'os.environ[...] = (line {tgt.lineno})')
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ('setdefault', 'update', 'pop')
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == 'environ'):
            bad.append(f'os.environ.{node.func.attr}() (line {node.lineno})')
    assert not bad, (
        f'strategic_diff 里出现了对 os.environ 的**写入** {bad} —— '
        '嵌入并发改走显式传参正是为了摆脱 env 的三重脆弱 (总/单预算语义搞反 · '
        'loky 复用池时改 env 是 no-op · 永不还原会泄漏给后续步骤), 不得回退')
    before = os.environ.get(sd._EMB_CONCURRENCY_ENV)
    sd._worker_emb_concurrency(12)
    sd._emb_total_budget()
    assert os.environ.get(sd._EMB_CONCURRENCY_ENV) == before, '函数改了进程环境'


def test_s13_worker_only_sets_concurrency_in_child_process():
    """① 之四: worker 内改 `EMB_API_CONCURRENCY` 必须**只在子进程**做。

    串行臂与 OOM 兜底会让父进程直接调 worker; 在那里改模块属性就污染了父进程
    (与 F42 的 `logging.disable` 同一类陷阱)。
    """
    from news_process.pipeline.text import embedding_engine as _e
    before = _e.EMB_API_CONCURRENCY
    task = ('Full', '', 2010, ['a', 'b'], ['x', 'y'])   # <3 家银行 → 立即早退
    sd._strat_year_worker(task, [5], [5], True, 'x{year}{exc}', '{n}',
                          emb_concurrency=3)
    assert before == _e.EMB_API_CONCURRENCY, (
        'worker 在父进程里改了 EMB_API_CONCURRENCY —— 串行臂/OOM 兜底会污染父进程')
    src = inspect.getsource(sd._strat_year_worker)
    assert 'parent_process()' in src, 'worker 缺进程身份闸'


@pytest.mark.parametrize('body_raises', [False, True])
def test_s13_worker_restores_concurrency_after_task(monkeypatch, body_raises):
    """① 之五: worker 每个 task 结束必须**还原** `EMB_API_CONCURRENCY` (含抛异常时)。

    ⚠ 本闸 2026-08-01 第三轮终审补。上一个 commit 用 try/finally 修了这条 (EMBC-1:
    loky **复用**常驻 worker ⟹ 不还原就把 S13 的 per-worker 值留给复用同一批 worker 的
    S5 fan-out), 但**没留任何会红的闸** —— 把 `finally` 体删空当时全绿。
    这与 EMBC-2 是同一形态: 修了、写了散文、没做闸。

    ⚠ 本闸必须伪装成**子进程**才有意义: 父进程里 `parent_process()` 闸会短路整段
    赋值, 于是"还原成功"会因为"根本没设过"而恒成立 —— 那又是一条永真断言。
    故先断言**设进去了** (调用期内 == 3), 再断言**还原了**。
    """
    import multiprocessing

    from news_process.pipeline.text import embedding_engine as _e

    monkeypatch.setattr(multiprocessing, 'parent_process', lambda: object())
    before = _e.EMB_API_CONCURRENCY
    seen = []

    def _spy_body(*a, **k):
        seen.append(_e.EMB_API_CONCURRENCY)      # 调用期内的实际值
        if body_raises:
            raise RuntimeError('模拟 worker 体内崩')
        return ({'sc': None}, [])

    monkeypatch.setattr(sd, '_strat_year_worker_body', _spy_body)
    task = ('Full', '', 2010, ['a', 'b', 'c'], ['x', 'y', 'z'])
    if body_raises:
        with pytest.raises(RuntimeError):
            sd._strat_year_worker(task, [5], [5], True, 'x{year}{exc}', '{n}',
                                  emb_concurrency=3)
    else:
        sd._strat_year_worker(task, [5], [5], True, 'x{year}{exc}', '{n}',
                              emb_concurrency=3)

    assert seen == [3], (
        f'worker 调用期内 EMB_API_CONCURRENCY={seen} ≠ [3] —— 并发根本没设进去, '
        '本闸会退化成永真断言 (还原成功只因为没设过)')
    assert before == _e.EMB_API_CONCURRENCY, (
        f'task 结束后未还原 ({_e.EMB_API_CONCURRENCY} ≠ {before})'
        f"{' (异常路径)' if body_raises else ''} —— loky 复用常驻 worker, "
        '残留值会被随后复用同一批 worker 的 S5 fan-out 读到 (EMBC-1)')


def test_s13_driver_uses_streaming_callback():
    """② 驱动器必须走**流式**回放, 否则整轨日志缓冲到轨末。

    实测对照 (同 worker/同 n_jobs, 唯一变量是 on_result): 非流式首条日志出现在总时长
    的 100% 处, 流式在 33% 处。后果不是行序变化而是**时机**: 被超时闸 SIGKILL 时,
    该轨已算出的 F28 塌缩 ERROR (该站点唯一现场信号) 一条都不会落盘。
    """
    src = inspect.getsource(sd._run_strat_year_tasks)
    assert 'on_result=on_result' in src, (
        '_run_strat_year_tasks 没把 on_result 透传给 _run_year_tasks —— '
        '退回缓冲路径, 见同模块 _run_year_tasks docstring 的实弹记载')
    body = inspect.getsource(sd.compute_strategic_differentiation)
    assert body.count('on_result=_emit_strat_logs') == 2, (
        '两处调用点 (Full 轨 + ctx/ss 子轨) 都必须传流式回调')


def test_s13_replay_dispatches_to_original_logger_methods():
    """② 之二: 回放必须按级别分派回 warning/info/error, 不得统一 logger.log()。

    2026-07-28 在 policy_similarity 上已实弹一次: 统一走 `logger.log(lvl, msg)` 输出的
    日志行完全相同, 但 Mock 断言 `logger.warning` 的守卫测试当场变红 ——
    而**日志逐行 A/B 抓不到这个** (Handler 分辨不出两者)。S13 初版又踩了一次。
    """
    src = inspect.getsource(sd._emit_strat_logs)
    assert 'logger.warning(_msg)' in src and 'logger.info(_msg)' in src         and 'logger.error(_msg)' in src, '回放未按级别分派回原调用面'
    # ⚠ 判据必须是 **AST 而非文本**: docstring 里为了讲清这条禁令, 必然要写到
    #   `logger.log(`, 于是任何 `in src` 式断言都会被自己的解释文本命中而假红
    #   (本次实弹踩到两次: 先是裸 `in src`, 再是按行首字符过滤 docstring 也没滤干净)。
    #   AST 只看真实调用节点, 与注释/文档字符串无关。
    node = ast.parse(src.lstrip()).body[0]
    bad = [n_.func.attr for n_ in ast.walk(node)
           if isinstance(n_, ast.Call) and isinstance(n_.func, ast.Attribute)
           and isinstance(n_.func.value, ast.Name) and n_.func.value.id == 'logger'
           and n_.func.attr == 'log']
    assert not bad, (
        '回放退回了统一 logger.log() —— 会绕过 Logger.warning, 让 Mock 断言失效')


def test_s13_parallelism_capped_by_emb_budget(monkeypatch, caplog):
    """① 之五: 嵌入总预算 < 并行度时, 必须**压并行度**而不是超发。

    `max(1, budget // n_jobs)` 的下界 1 会让总在飞 = n_jobs; 运维把预算调到 6 正是
    因为端点吃不住更多, 这时开 12 个 worker 各 1 个仍是 12 —— 仍然超发 2×。
    """
    monkeypatch.setenv(sd._EMB_CONCURRENCY_ENV, '4')
    seen = {}

    def _fake_run(tasks, worker, *extra, min_tasks=None, n_jobs=None, on_result=None):
        seen['n_jobs'] = n_jobs
        seen['emb_k'] = extra[-1]
        return []

    monkeypatch.setattr(sd, '_run_year_tasks', _fake_run)
    sd._run_strat_year_tasks(list(range(19)), [5], [5], True, 'x{year}{exc}', '{n}')
    assert seen['n_jobs'] <= 4, (
        f"总预算 4 但并行度 {seen['n_jobs']} —— 未按预算封顶, 端点会被超发")
    assert seen['emb_k'] * seen['n_jobs'] <= 4, '总在飞超预算'


def test_s13_threshold_keeps_toy_and_t2_serial():
    """② T=2 dev (每轨 2 个任务) 与单测 fixture 必须留在串行臂。"""
    assert sd._STRAT_PARALLEL_MIN_YEARS >= 12, (
        f'_STRAT_PARALLEL_MIN_YEARS={sd._STRAT_PARALLEL_MIN_YEARS} 过低 —— '
        'T=2 dev 与单测会走进 loky, 而 monkeypatch 桩不传播进子进程')


def test_s13_worker_has_zero_logger_calls():
    """③ worker 体内零 logger (它会被父进程直接调用于串行回落路径)。"""
    node = ast.parse(inspect.getsource(sd._strat_year_worker)).body[0]
    bad = [f'logger.{n.func.attr}' for n in ast.walk(node)
           if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
           and isinstance(n.func.value, ast.Name) and n.func.value.id == 'logger']
    assert not bad, (
        f'_strat_year_worker 体内出现 logger 调用 {bad} —— 串行回落时它在父进程跑, '
        '会掐掉整个 stage 的日志; 告警一律经 logs 回传父端 emit')


def test_s13_task_split_keeps_small_years_and_is_sorted():
    """④ 切分与串行同序, 且 <3 家银行的年份照样进池 (由 worker 守卫早退)。"""
    agg = pd.DataFrame({
        'year': [2011, 2011, 2011, 2010, 2010, 2012],
        'target_bank': ['a', 'b', 'c', 'a', 'b', 'a'],
        'agg_text': ['t'] * 6,
    })
    tasks = sd._strat_year_tasks(agg, 'Full', '')
    assert [t[2] for t in tasks] == [2010, 2011, 2012], '年份未按 sorted 提交'
    assert len(tasks[0][3]) == 2 and len(tasks[2][3]) == 1, (
        '<3 家银行的年份被提前筛掉了 —— 守卫告警时序会偏离串行')


def test_s13_worker_early_exits_and_warns_like_serial():
    """④ 之二: <3 家银行 → 返回 None + (Full 轨) 告警; 子轨保持无告警。"""
    task = ('Full', '', 2010, ['a', 'b'], ['x', 'y'])
    payload, logs = sd._strat_year_worker(
        task, [5], [5], True, '  LDA 失败 ({exc}) year={year}', '{n} 家')
    assert payload is None
    assert any('仅 2 家银行' in m for _, m in logs), 'Full 轨少了 <3 家告警'
    task_sub = ('_ctx', '_ctx', 2010, ['a', 'b'], ['x', 'y'])
    payload2, logs2 = sd._strat_year_worker(
        task_sub, [5], [5], False, '  LDA 失败 ({exc}) year={year}', '{n} 家')
    assert payload2 is None and logs2 == [], (
        '子轨原本是裸 continue 无告警, 不得借机补告警 (会改变日志基线)')


def test_s13_worker_is_module_level_picklable():
    """loky 进程后端要求 worker 模块级 (pickle-by-ref)。"""
    import pickle
    assert sd._strat_year_worker.__module__ == sd.__name__
    assert pickle.loads(pickle.dumps(sd._strat_year_worker)) is sd._strat_year_worker
