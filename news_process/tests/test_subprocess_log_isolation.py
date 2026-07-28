"""tests/test_subprocess_log_isolation.py — F27 / F29 / F29b gate: 子进程日志隔离与模块日志可见性。

三件事故串成一条线, 本文件把三者的修复一次锁死:

**F27 (2026-07-27 实弹)** — 12 个 loky worker 把 `40_build_panel.log` 抹成
**99.8% NUL**。根因: `_DelayedTruncatingRotatingHandler` 按「本进程首写即截断」实现
`file_mode='w'`, 而 worker 只要 import 链上碰到任何一个模块级 `setup_logging`
就会打开同一个 .log 并截断它。修复取**根治点**: spawn 子进程一律不装文件 handler。

**F29 (同一次事故的另一半)** — 23 个 pipeline/core 模块用
`logging.getLogger(__name__)` (如 `news_process.pipeline.text.embedding_engine`),
与裸阶段名 logger (`"40_build_panel"`) 是两条互不相交的链 ⟹ 模块日志既不进阶段 .log,
又因 root 无 handler 落到 `logging.lastResort` (裸 `%(message)s`, **levelname 丢失**)。
后果: embedding_engine 那条「重试 80 次仍失败 → 该轨列将置 NaN」的 `logger.error`
在镜像里根本不是 ERROR ⟹ `grep -c " - ERROR - "` = **0** ⟹ F28 的四列全 NaN
安然通过验收, 28 小时后才被发现。

**F29b (2026-07-28, S5 A/B 实测订正)** — F29 首版在 `console_only` 分支直接
`return`, 理由写的是「子进程里挂命名空间 handler 无意义 (loky 默认丢弃 worker
stdout)」。**该前提被证伪**: S5 逐年并行 A/B 里, worker 的 12 条「分词器已注入」
确实落到了父进程 stdout。而不挂的代价是实测出来的: 并行臂里 embedding_engine
相关行 = **0** —— 缓存命中率、F18 分段计时、以及那条「重试耗尽」ERROR 全部消失,
等于把 F29 刚补上的洞在并行路径上重新挖开。故改为**子进程也挂 (但不锁 owner)**。
"""
from __future__ import annotations

import inspect
import logging
import multiprocessing
import os
import sys
import tempfile

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core import logging as nplog  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_ns():
    """每个用例前后复位命名空间 logger 与 owner, 防跨用例污染。"""
    ns = logging.getLogger(nplog._NS_LOGGER_NAME)
    old_h, old_lv = list(ns.handlers), ns.level
    old_owner, old_att = nplog._NS_OWNER, list(nplog._NS_ATTACHED)
    yield
    ns.handlers[:] = old_h
    ns.setLevel(old_lv)
    nplog._NS_OWNER = old_owner
    nplog._NS_ATTACHED[:] = old_att


def _real_src(func_name: str) -> str:
    """从**模块文件**取某函数的源码。

    ⚠ 不能用 ``inspect.getsource(nplog.setup_logging)``: ``tests/conftest.py`` 在模块级
    把 ``setup_logging`` 替换成了测试包装器 ``_testing_setup_logging`` (强制写生产
    logs/ 的调用走 console_only), 于是 getsource 拿到的是**包装器**的源码, 断言
    「硬闸在函数开头」会以 substring not found 假红。2026-07-28 实弹踩到。
    """
    import ast
    tree = ast.parse(inspect.getsource(nplog))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(inspect.getsource(nplog), node) or ''
    raise AssertionError(f'{func_name} 不在 core/logging.py 里 (被改名或删除?)')


def _setup(stage, console_only=False, log_dir=None):
    return nplog.setup_logging(stage, log_dir or tempfile.mkdtemp(prefix='nplog_'),
                               console_only=console_only)


def _ns():
    return logging.getLogger(nplog._NS_LOGGER_NAME)


# ── F27: 子进程判定与硬闸 ──

def test_spawned_child_predicate_is_three_way_union():
    """三谓词并集: parent_process() / 进程名 / _inheriting。缺一都会漏判。"""
    src = inspect.getsource(nplog._is_spawned_child_process)
    for tok in ('parent_process', 'MainProcess', '_inheriting'):
        assert tok in src, (
            f'子进程判据缺 {tok} —— 三条各覆盖一类子进程 (fork/spawn/正在 spawn 途中), '
            '漏一条就会有 worker 溜进去截断生产日志 (F27 实弹)。')


def test_main_process_is_not_treated_as_child():
    assert nplog._is_spawned_child_process() is False, \
        '主进程被误判为子进程 → 主进程也不装文件 handler, 生产日志全丢'


def test_child_process_forced_console_only(monkeypatch):
    """子进程即使显式传 console_only=False, 也必须被硬闸改成 True。"""
    monkeypatch.setattr(nplog, '_is_spawned_child_process', lambda: True)
    d = tempfile.mkdtemp(prefix='nplog_child_')
    lg = _setup('40_build_panel_probe', console_only=False, log_dir=d)
    from logging.handlers import RotatingFileHandler
    files = [h for h in lg.handlers if isinstance(h, RotatingFileHandler)]
    assert not files, (
        f'子进程仍装了文件 handler {files} —— F27 的根治点被绕过, '
        '「本进程首写即截断」会再次把生产日志抹成 NUL。')


def test_hard_gate_is_at_top_of_setup_logging():
    """硬闸必须在函数**开头**, 不能被任何早退路径绕过。"""
    src = _real_src('setup_logging')
    gate = src.index('_is_spawned_child_process()')
    mkdir = src.index('os.makedirs')
    assert gate < mkdir, '硬闸位置晚于目录创建 —— 存在被绕过的路径'


# ── F29: 命名空间 handler ──

def test_namespace_gets_console_handlers_in_parent():
    _setup('probe_stage_a')
    assert _ns().handlers, (
        'news_process 命名空间无 handler —— embedding_engine 一类 getLogger(__name__) '
        '模块的日志会落到 lastResort, levelname 丢失, ERROR 判据当场失明 (F29 事故)。')


def test_namespace_never_gets_file_handler():
    """只挂 console: 挂文件 handler = F27 同型二次截断风险。"""
    from logging.handlers import RotatingFileHandler
    _setup('probe_stage_b')
    bad = [h for h in _ns().handlers if isinstance(h, RotatingFileHandler)]
    assert not bad, f'命名空间挂上了文件 handler {bad} —— 第二个截断源, F27 同型复发'


def test_namespace_level_is_set_explicitly():
    """不显式设级 → NOTSET → 继承 root 的 WARNING, 模块 INFO 仍然落空 (F16 只修一半)。"""
    _setup('probe_stage_c')
    assert _ns().level != logging.NOTSET, '命名空间 level 仍是 NOTSET, 模块 INFO 落不了盘'


def test_ns_level_env_override(monkeypatch):
    monkeypatch.setenv('NEWS_PROCESS_NS_LOG_LEVEL', 'DEBUG')
    _setup('probe_stage_d')
    assert _ns().level == logging.DEBUG, 'NEWS_PROCESS_NS_LOG_LEVEL 覆盖失效 (归因跑需要它)'


def test_owner_locks_on_first_not_last(monkeypatch):
    """owner = **首次非 console_only** 调用, 不是 last-wins。

    生产实测: 一个 stage 40 进程会调 ≥4 次 setup_logging (encode→40 · llm_peer_iv→48 ·
    network_brokerage→47 · network_spillover→46, 均模块级)。last-wins 会把 F29 的载荷
    路由到**错误的阶段** —— 那就是自造一个 F27。
    """
    nplog._NS_OWNER = None
    _setup('40_build_panel')
    first = list(_ns().handlers)
    _setup('48_llm_peer_iv')
    assert nplog._NS_OWNER == '40_build_panel', \
        f'owner 被后续调用改绑成 {nplog._NS_OWNER} (last-wins) — F29 载荷会路由到错误阶段'
    assert list(_ns().handlers) == first, 'owner 已锁定, handler 不应被替换'


# ── F29b: 子进程**也**要挂 (2026-07-28 订正) ──

def test_child_process_also_binds_namespace(monkeypatch):
    """console_only 分支不得再直接 return。

    首版直接 return, 理由「loky 默认丢弃 worker stdout」已被 S5 A/B 证伪
    (worker 的 12 条「分词器已注入」确实进了父进程 stdout)。
    代价实测: 并行臂 embedding_engine 相关行 = 0, 含 F18 分段计时与
    「重试耗尽 → 置 NaN」ERROR —— F29 补上的洞在并行路径上被重新挖开。
    """
    nplog._NS_OWNER = None
    logging.getLogger(nplog._NS_LOGGER_NAME).handlers.clear()
    nplog._NS_ATTACHED.clear()
    monkeypatch.setattr(nplog, '_is_spawned_child_process', lambda: True)
    _setup('40_build_panel_worker')
    assert _ns().handlers, (
        '子进程里命名空间仍无 handler —— 并行段内 news_process.* 模块日志整段消失, '
        '其中包括 embedding_engine 的「重试耗尽 → 该轨列置 NaN」ERROR (F28 现场信号)。')


def test_child_binding_does_not_claim_owner(monkeypatch):
    """子进程挂 handler 但**不锁 owner** (owner 锁是为父进程多次模块级调用准备的)。"""
    nplog._NS_OWNER = None
    monkeypatch.setattr(nplog, '_is_spawned_child_process', lambda: True)
    _setup('40_build_panel_worker')
    assert nplog._NS_OWNER is None, \
        f'子进程抢占了 owner (={nplog._NS_OWNER}) — 会干扰父进程语义'


def test_module_logger_record_reaches_namespace_handler_once(monkeypatch):
    """端到端: 模块 logger 的一条 ERROR 必须**恰好一次**到达命名空间 handler。

    「恰好一次」两头都要防: 0 次 = F29 事故 (ERROR 判据失明);
    ≥2 次 = 重复落盘 (会让「ERROR 条数」这类计数判据失真)。
    """
    got = []

    class _Cap(logging.Handler):
        def emit(self, r):
            got.append((r.levelname, r.getMessage()))

    nplog._NS_OWNER = None
    _setup('probe_stage_e')
    cap = _Cap()
    _ns().addHandler(cap)
    nplog._NS_ATTACHED.append(cap)
    try:
        logging.getLogger('news_process.pipeline.text.embedding_engine').error('探针-重试耗尽')
    finally:
        _ns().removeHandler(cap)
    hits = [g for g in got if g[1] == '探针-重试耗尽']
    assert len(hits) == 1, f'模块 ERROR 到达命名空间 handler {len(hits)} 次 (期望恰好 1): {got}'
    assert hits[0][0] == 'ERROR', 'levelname 丢失 —— 正是 F29 事故里 grep ERROR 归零的机制'


# ── 反向: 纪律不得被误解为放松 ──

def test_worker_zero_logger_discipline_still_documented():
    """F29b 让 worker 日志可见, 但**不放松**「worker 体内零 logger 调用」纪律。

    两者管的是不同的东西: 纪律管**行序** (worker 日志交错不可预测, 业务告警必须
    经 log_sink 回传父端按提交序回放), F29b 管**可见性** (第三方模块日志别整段丢)。
    源码里必须把这层区分写清楚, 否则下一个人会以为可以直接在 worker 里 logger。
    """
    src = _real_src('setup_logging') + _real_src('_attach_namespace_console')
    assert '零 logger 调用' in src, 'worker 零 logger 纪律的说明被删除'
    assert '行序' in src, '未说明纪律的真正理由是行序 (而非可见性), 易被误解为可放松'


def test_multiprocessing_import_present():
    """三谓词依赖 multiprocessing; 缺 import 会让判据整体 except 掉 → 恒返回 False。"""
    assert multiprocessing is not None
    assert 'import multiprocessing' in inspect.getsource(nplog)
