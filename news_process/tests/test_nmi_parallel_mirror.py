"""tests/test_nmi_parallel_mirror.py — S11/S12 gate: NMI 逐 cell 进程并行 + 整数编码;
**两侧均不镜像** (S12 撤销了 S11 的 bootstrap 上三角镜像, 文件名保留为历史锚)。

**事故 (2026-07-29 入口③ 生产真跑)**: 阶段 72 `72_construct_orthogonality.py`
**被 10,800s 超时闸强杀**, 后续阶段 73/74/75 连坐跳过, 整个评估验证管道判 ✗。
这是同一根因第 4 次复发 (stage 15 / 23 / 40 / 72): **超时按估算或早期试跑 T=2 定,
从未按生产规模复核**。

本模块 docstring 原写「N≈40 万标签单线程约 77 分钟, 故 DAG timeout=10800」,
并写着「64 核 MP 上 n_jobs=16 约 5 分钟」—— 但**代码里从来没有并行**。真数据实测:
    单次 bootstrap 迭代 754 ms  → 单 cell(1000) 12.6 分钟 → 48 cell = 10.05h
    单次 permutation 迭代 774 ms → 单 cell(1000) 12.9 分钟 → **36** cell = 7.74h
    合计 **17.79 小时**, 是那句估算的约 14 倍 (且 N=169,811 比假设的 40 万还小)。
    ⚠ 2026-08-01 订正: 旧文按 permutation 也走 48 格算成 20.4h; 实测它全阶段只调 2 次
    (3 维 30 格 + 6 维 6 格 = 36), 故真值是 17.79h。只影响"串行兜底要多久"的估算,
    不影响任何取值; DAG timeout=108000 仍远超。

本 gate 锁死六件事:
  ① 并行阈值按 **cells × bootstrap_n** 而非 cell 数 —— 现存单测用的维度数与生产
     **相同** (DIMS_FULL 3 维 / ALL_DIMS 6 维), 只把 bootstrap_n 调小, 按 cell 数
     设闸会让单测一起走进并行分支 (桩不传播进 loky 子进程 ⟹ 测试失真)。
  ② worker 体内零 logger 调用 (退化告警回传父端)。
  ③ **两侧都不镜像** (S12, 2026-07-31 起)。S11 曾对 bootstrap 侧镜像, 依据是
     "NMI 实测逐位对称 (点估计 3/3 + bootstrap 3/3)"。该依据已被真数据复测证伪:
     全 15 对 × 40 次真实 bootstrap 重采样中 **6/600 非逐位对称**, 全部集中在
     (innovation_collab_mode_full, innovation_collab_mode_ctx) 一对, max|Δ|=1.11e-16
     (≈1 ulp; 机理 = 交换两列即转置列联表, `contingency_matrix` 按行主序装配, 求和序变)。
     点估计侧则确实 0/15 全对称。⚠ 该 1 ulp 在**矩阵级**被分位数吸收 (撤销前后
     真数据 A/B: point/ci/n_pair 0 格不同), 故撤销的定性是**前提证伪 + 稳健性加固**,
     不是"修正已发布的错数" —— 但"分位数会吸收"不是受控保证, 且代价已被整数编码
     吸收 (端到端 685.2 s → 74.5 s = 9.2×), 故仍撤销。
  ④ ⚠ **permutation 绝不可镜像**: (i,j) 打乱第 j 列、(j,i) 打乱第 i 列, 是两次
     **不同的随机化**, 实测 0/5 逐位相同。这条最容易被后人"顺手优化"掉 —— 看到
     bootstrap 减半了就以为另一半也能减半, 那是**静默改数**。
  ⑤ 守卫 (len<100 / F40 退化 / n_pair) 仍对**全部** (i,j) 逐格执行。
  ⑥ **整数编码逐位等价** (S12): `_encode_codes` 必须用 `np.unique` 的排序序,
     不得改用 `pd.factorize` 的出现序 —— 后者会置换列联表行列, 改变浮点求和序。
"""
from __future__ import annotations

import ast
import inspect
import logging
import os
import struct
import sys

import numpy as np
import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.audit import construct_orthogonality as co  # noqa: E402

_D = list(co.DIMS_FULL)


def _toy(n=400, seed=0):
    """三维离散标签的合成样本 (足够大以过 len<100 闸, 又足够小让单测秒完)。"""
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        _D[0]: rng.integers(0, 3, n),
        _D[1]: rng.integers(0, 3, n),
        _D[2]: rng.integers(0, 2, n),
    })


def _bits(v):
    return b'NaN' if (isinstance(v, float) and np.isnan(v)) else struct.pack('<d', float(v))


# ── ① 阈值 ──

def test_parallel_threshold_is_work_based_not_cell_based():
    assert co._NMI_PARALLEL_MIN_WORK >= 5000, (
        f'_NMI_PARALLEL_MIN_WORK={co._NMI_PARALLEL_MIN_WORK} 过低 —— '
        '现存单测的维度数与生产相同 (3 维/6 维), 只把 bootstrap_n 调到 20-100; '
        '生产侧**单次调用**的工作量最小是 6,000 (3 维轨 6 格 × 1000), 最大 30,000 '
        '(6 维 cross 30 格 × 1000); 单测最大 30×30=900 —— 阈值必须落在两者之间, '
        '且距 6,000 只有 1.2× 余量 (2026-08-01 订正: 旧文写 48,000 是把四次调用的'
        '格数总和当成了单次 min_work)。')
    src = inspect.getsource(co._run_cells)
    assert 'min_work' in src, '并行判据不再基于工作量 (改回按 cell 数会让单测失真)'


def test_toy_fixture_stays_serial():
    """toy 规模必须走串行 —— 否则 monkeypatch 桩不传播进子进程, 测试当场失真。

    ⚠ 2026-08-01 订正: 原式是 `(n_off // 2) * boot` —— 那是 **S11 镜像时期**的口径
    (只算上三角, 格数减半)。S12 撤销镜像后任务池装的是**全部**非对角格, 真实工作量
    是 `n_off * boot`, 旧式把它系统性低估 2×。低估意味着这条 gate 的守护带宽只有名义
    的一半: 若哪天把 toy 的 bootstrap_n 提到 900, 旧式算 2,700 < 5,000 判"安全",
    而真实工作量 5,400 ≥ 5,000, 单测会**静默走进 loky 并行分支** —— 正是本 gate 要防的失真。
    """
    n_off = len(_D) * (len(_D) - 1)          # 6 (全部非对角格, 撤镜像后不再减半)
    for boot in (20, 50, 100):
        assert n_off * boot < co._NMI_PARALLEL_MIN_WORK, (
            f'bootstrap_n={boot} 的 toy 工作量 {n_off * boot} 已达并行阈值')


# ── ② worker 零 logger ──

@pytest.mark.parametrize('fn', ['_boot_cell_worker', '_perm_cell_worker'])
def test_worker_has_zero_logger_calls(fn):
    node = ast.parse(inspect.getsource(getattr(co, fn))).body[0]
    bad = [f'logger.{n.func.attr}' for n in ast.walk(node)
           if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
           and isinstance(n.func.value, ast.Name) and n.func.value.id == 'logger']
    assert not bad, (
        f'{fn} 体内出现 logger 调用 {bad} —— worker 在 loky 子进程里跑, '
        '行序不可预测; 且它也会被父进程直接调用于串行回落路径。告警一律回传父端。')


# ── ③ 两侧都不镜像 (S12 撤销了 bootstrap 侧镜像) ──

def test_point_estimates_are_symmetric_bitwise():
    """点估计侧确实逐位对称 (真数据 0/15) —— 这条 S12 复测后仍成立, 保留为回归锚。

    ⚠ 注意本条**不能**推广到 bootstrap CI: 同一批复测里 CI 侧 6/600 非对称。
    """
    df = _toy()
    point, _lo, _hi, _n = co.compute_nmi_matrix(df, _D, bootstrap_n=20, seed=42)
    for i, d1 in enumerate(_D):
        for j, d2 in enumerate(_D):
            if j <= i:
                continue
            assert _bits(point.loc[d1, d2]) == _bits(point.loc[d2, d1]), (
                f'point 上下三角不对称: [{d1},{d2}]={point.loc[d1,d2]!r} '
                f'vs [{d2},{d1}]={point.loc[d2,d1]!r}')


def test_bootstrap_mirror_is_removed():
    """源码级: bootstrap 侧**不得**再出现"只算上三角 + 镜像回填"。

    这是 S12 的核心断言。回退成镜像 = 重新把一个**已被证伪的前提**当依据用,
    而它不会让任何测试变红 (1 ulp 在分位数处通常被吸收) —— 正因为看不见, 才要锁。
    """
    src = inspect.getsource(co.compute_nmi_matrix)
    assert 'point.iloc[_j, _i]' not in src, (
        'bootstrap 侧出现镜像回填 —— S12 已证伪其前提 (6/600 非逐位对称), '
        '不得回退')
    assert 'ci_low.iloc[_j, _i]' not in src and 'ci_high.iloc[_j, _i]' not in src, \
        'CI 侧出现镜像回填 —— 同上'
    assert '_boot_tasks' in src, 'bootstrap 任务池缺失 (并行化被回退)'


def test_boot_task_pool_covers_all_offdiagonal_cells():
    """**行为级**锁: bootstrap 任务池必须装全部非对角格 (镜像时只会装一半)。

    ⚠ 为什么要它: `test_bootstrap_mirror_is_removed` 是纯源码字符串匹配, 一次无害的
    局部重命名 (`for _a, _b, *_ in _boot_tasks: point.iloc[_b, _a] = ...`) 或
    `iloc → iat/values` 重构就能把镜像加回去而不触发那条字面量断言; 而全部**行为级**
    用例对镜像都不敏感 (镜像同样会把下三角填满、n_pair 与 F40 本就逐格跑)。
    ⟹ 撤镜像这条不变量此前只有一根字符串锚在守。这里补一根拿得住的: 直接数任务池。
    """
    seen = []
    orig = co._run_cells

    def _spy(tasks, worker, *extra, min_work, n_jobs=None, label='cells'):
        seen.append((label.split()[0], len(tasks)))
        return orig(tasks, worker, *extra, min_work=min_work, n_jobs=n_jobs,
                    label=label)

    co._run_cells = _spy
    try:
        co.compute_nmi_matrix(_toy(), _D, bootstrap_n=20, seed=42)
    finally:
        co._run_cells = orig
    n_off = len(_D) * (len(_D) - 1)
    boot = [n for lab, n in seen if lab.startswith('bootstrap')]
    assert boot == [n_off], (
        f'bootstrap 任务池格数 {boot} != 全部非对角格 {n_off} —— '
        f'{n_off // 2} 说明上三角镜像被加了回来 (S12 已证伪其前提: 6/600 非逐位对称)')


def test_all_offdiagonal_cells_get_ci():
    """全部非对角格都必须有各自算出的 CI (不是靠镜像补上的)。"""
    df = _toy()
    _p, lo, hi, _n = co.compute_nmi_matrix(df, _D, bootstrap_n=20, seed=42)
    for d1 in _D:
        for d2 in _D:
            if d1 == d2:
                continue
            assert not np.isnan(lo.loc[d1, d2]), f'ci_low[{d1},{d2}] 缺失'
            assert not np.isnan(hi.loc[d1, d2]), f'ci_high[{d1},{d2}] 缺失'


# ── ⑥ 整数编码逐位等价 (S12 的提速手段, 也是最容易被改坏的一处) ──

def test_encode_codes_uses_sorted_order_not_appearance_order():
    """`_encode_codes` 必须按 `np.unique` 的**排序序**赋码。

    改用 `pd.factorize` (出现序) 会置换列联表的行列 ⟹ 浮点求和序变 ⟹ 不再逐位等价。
    本数据上两者恰好重合过, 那是巧合, 不可依赖 —— 故这里用一个**出现序 ≠ 排序序**
    的样本把两者分开。
    """
    s = pd.DataFrame({'x': ['b', 'b', 'a', 'c', 'a']})
    codes = co._encode_codes(s)['x'].tolist()
    assert codes == [1, 1, 0, 2, 0], (
        f'_encode_codes 得到 {codes}, 期望排序序 [1,1,0,2,0]; '
        '若得到 [0,0,1,2,1] 说明改成了 pd.factorize 的出现序 —— 会破坏逐位等价')


def test_encode_codes_is_bitwise_equivalent_for_nmi():
    """编码前后 NMI 逐位相同 (点估计 + bootstrap 重采样两条路径都验)。"""
    nmi = co._lazy_import_nmi()
    rng = np.random.default_rng(11)
    raw = pd.DataFrame({
        'x': rng.choice([f'L{i:02d}' for i in range(7)], 3000),
        'y': rng.choice([f'M{i:02d}' for i in range(5)], 3000),
    })
    enc = co._encode_codes(raw)
    assert _bits(nmi(raw['x'], raw['y'], average_method='arithmetic')) == \
        _bits(nmi(enc['x'], enc['y'], average_method='arithmetic')), \
        '点估计在编码后不再逐位相同'
    for st in (7, 99, 12345):
        a = raw.sample(frac=1, replace=True, random_state=st)
        b = enc.sample(frac=1, replace=True, random_state=st)
        assert (a.index.values == b.index.values).all(), \
            '同 random_state 下编码前后重采样下标序列不同 (语义已变)'
        assert _bits(nmi(a['x'], a['y'], average_method='arithmetic')) == \
            _bits(nmi(b['x'], b['y'], average_method='arithmetic')), \
            f'bootstrap 重采样 (random_state={st}) 在编码后不再逐位相同'


def test_encode_codes_applied_in_both_entrypoints():
    """两个入口都必须真的用上编码 —— 否则 worker 拿到的仍是 object 列, 白改。"""
    for fn in (co.compute_nmi_matrix, co.compute_permutation_null):
        assert '_encode_codes(' in inspect.getsource(fn), \
            f'{fn.__name__} 未应用 _encode_codes'


# ── ④ permutation 绝不可镜像 (最易被误优化的一条) ──

def test_permutation_null_is_NOT_mirrored():
    """(i,j) 与 (j,i) 必须是**各自独立算出**的, 不得相等。

    实测依据: (i,j) 打乱第 j 列而 (j,i) 打乱第 i 列 —— 两次不同的随机化,
    真数据 0/5 逐位相同 (值相差若干量级)。若哪天这两格相等了, 说明有人
    "顺手"把 bootstrap 的镜像套到了 permutation 上 —— 那是静默改数。
    """
    df = _toy(n=600, seed=1)
    p95, p99 = co.compute_permutation_null(df, _D, n_permutations=40, seed=43)
    equal_pairs = []
    for i, d1 in enumerate(_D):
        for j, d2 in enumerate(_D):
            if j <= i:
                continue
            if _bits(p95.loc[d1, d2]) == _bits(p95.loc[d2, d1]):
                equal_pairs.append((d1, d2))
    assert not equal_pairs, (
        f'permutation null 出现上下三角逐位相等的格 {equal_pairs} —— '
        '几乎必然是有人给 permutation 也套了镜像。(i,j) 打乱第 j 列、'
        '(j,i) 打乱第 i 列, 是两次不同随机化, 相等在概率上不该发生。')


def test_permutation_source_has_no_mirror():
    src = inspect.getsource(co.compute_permutation_null)
    assert 'null_p95.iloc[_j, _i]' not in src and 'null_p99.iloc[_j, _i]' not in src, \
        'permutation 出现镜像回填 —— 静默改数'
    assert '_perm_tasks' in src, 'permutation 未并行化'


# ── ⑤ 守卫仍逐格执行 ──

def test_n_pair_filled_for_all_cells_including_lower_triangle():
    df = _toy()
    _, _, _, n_pair = co.compute_nmi_matrix(df, _D, bootstrap_n=20, seed=42)
    for d1 in _D:
        for d2 in _D:
            assert n_pair.loc[d1, d2] > 0, (
                f'n_pair[{d1},{d2}] 未填 —— 该矩阵是样本量披露, 下三角同样要有值')


def test_degenerate_guard_still_fires_for_every_cell():
    """常量列 → F40 logger.error 条数不因只算上三角而减少。"""
    df = _toy()
    df[_D[2]] = 1                       # 造一个常量列
    cap = []

    class _C(logging.Handler):
        def emit(self, r):
            if r.levelno >= logging.ERROR:
                cap.append(r.getMessage())

    h = _C()
    co.logger.addHandler(h)
    try:
        co.compute_nmi_matrix(df, _D, bootstrap_n=10, seed=42)
    finally:
        co.logger.removeHandler(h)
    degen = [m for m in cap if 'degenerate' in m]
    # 常量列参与的格: (d2,*) 与 (*,d2) 共 2*(n-1)+1 = 5 格 (含对角)
    assert len(degen) >= 5, (
        f'F40 退化告警只有 {len(degen)} 条 (期望 ≥5) —— 守卫必须对全部 (i,j) 逐格执行, '
        '不能因为只算上三角就漏报下三角')


# ── 运维旁路 / 兜底 ──

@pytest.mark.parametrize('raw,expect_le', [('4', 4), ('1', 1)])
def test_jobs_env_override(monkeypatch, raw, expect_le):
    monkeypatch.setenv(co._NMI_JOBS_ENV, raw)
    assert co._nmi_workers(100) <= expect_le


def test_jobs_env_invalid_falls_back(monkeypatch):
    monkeypatch.setenv(co._NMI_JOBS_ENV, 'oops')
    assert co._nmi_workers(100) >= 1


def test_run_cells_has_oom_fallback():
    src = inspect.getsource(co._run_cells)
    assert '回落串行' in src and 'except Exception' in src, \
        '_run_cells 缺 OOM 兜底 —— worker 被 OS 杀掉会让数小时工作归零'


def test_module_does_not_import_features_layer():
    """audit 层不得反向依赖 features 层 (故本模块自带 _run_cells 而非复用 strategic_diff)。"""
    src = inspect.getsource(co)
    assert 'from news_process.pipeline.features' not in src, \
        'audit 层反向依赖了 features 层 (分层倒置)'
