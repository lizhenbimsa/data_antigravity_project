"""tests/test_policy_similarity_year_parallel.py — S5 gate: 权威政策相似度逐年并行。

**背景 (2026-07-28)**: stage 40 生产实测 28.12h, `compute_authoritative_similarity`
独占 38,066s = **37.8%**, 是单一最大极。真数据归因 (probe_s5_split.py) 实测其构成
≈ 95.6% CPU / 4.4% SQLite 缓存读 / **~0% API** (API 段 0.0004s), 故切成 (轨, 年)
任务后进程并行。

本 gate 锁死六件事, 每一件都对应一个**具体的、已经发生过或差点发生的**事故:

  ① `_AUTH_PARALLEL_MIN_TASKS` 不得降到 12 以下 —— 本模块任务池是「3 轨 × N 年」
     扁平池, 复用 strategic_diff 的 4 会让**现存单测也走进并行分支**, 而单测靠
     monkeypatch 打桩、桩不传播进 loky 子进程 ⟹ 测试当场失真。
  ② worker 体内**零 logger 调用** —— 这是 strategic_diff 既有护栏 ④。F25 首版曾
     试图用 `_silence_worker_logging()` 解决, 结果会在串行回落路径上把整个 stage
     的 INFO 掐掉 (自造 F16 型"日志落空"), 已废弃。
  ③ 两处 `_ghost_anchor_metrics` 调用**必须**带 log_sink —— 漏一处, 那一路的
     "LDA K=…" 与降级 warning 就会跑到子进程 console 上, 行序错乱且不入阶段日志。
  ④ `_build_lda_jsd_matrix` 的 **`threadpool_limits(1)` 不得移除** —— S5 的字节
     安全**完全**建立在它之上。F26 之前该函数因 BLAS 线程数差异漂 ~1e-13
     (265/277 键), 删掉它 S5 就开始静默漂移, 而 allclose 型断言看不出来。
  ⑤ 三条守卫路径 (<3 银行 / vintage 锚点 None×companion 开关 / allv 短路) 行为
     不变 —— A/B 用的是 2007-2012 真数据, 覆盖不到前视守卫 (语料最早 vintage
     =2001) 与 allv 短路 (需 ≥2025), 故在此直接调 worker 补齐。
  ⑥ "K 恒为 10" 的旧披露已被证伪, 不得回潮 —— 生产 428-584 银行/年 ⟹
     K ∈ {10,11,14,15,18,19} (stage 40 日志逐条核对), K 直接驱动 LDA 耗时。
"""
from __future__ import annotations

import ast
import inspect
import logging
import os
import sys

import numpy as np
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.features import policy_similarity as ps  # noqa: E402
from news_process.pipeline.features import strategic_diff as sd  # noqa: E402


def _dedent(src: str) -> str:
    import textwrap
    return textwrap.dedent(src)


# ── ① 阈值 ──

def test_min_tasks_threshold_not_lowered():
    assert ps._AUTH_PARALLEL_MIN_TASKS >= 12, (
        f"_AUTH_PARALLEL_MIN_TASKS={ps._AUTH_PARALLEL_MIN_TASKS} < 12 —— "
        "本模块是「3 轨 × N 年」扁平池, N≥2 就 ≥6 个任务。阈值低于 12 会让早期试跑 T=2 "
        "与 toy fixture 走进并行分支, 而 monkeypatch 桩不传播进 loky 子进程 ⟹ 单测失真。")


def test_min_tasks_is_not_borrowed_from_strategic_diff():
    """刻意**不等于** strategic_diff 的 4 —— 借用会踩上面那个坑。"""
    assert ps._AUTH_PARALLEL_MIN_TASKS != sd._PROC_PARALLEL_MIN_YEARS, (
        "阈值被改回复用 strategic_diff._PROC_PARALLEL_MIN_YEARS —— "
        "两者任务池形状不同 (相邻年对 vs 轨×年扁平池), 不可跨模块硬借。")


# ── ② worker 体内零 logger 调用 ──

def test_worker_body_has_zero_logger_calls():
    """AST 级判定, **不是**字符串扫描。

    ⚠ 字符串扫描曾在 F25 误报: docstring 里提到 'logger.' 就被当成调用。
    """
    tree = _dedent(inspect.getsource(ps._auth_year_worker))
    node = ast.parse(tree).body[0]
    bad = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                    and f.value.id == 'logger':
                bad.append(f"logger.{f.attr}()  @line {n.lineno}")
    assert not bad, (
        f"_auth_year_worker 体内出现 logger 调用: {bad} —— "
        "违反 strategic_diff 护栏 ④ (worker 零 logger, 告警一律回传父端 emit)。"
        "worker 在 loky 子进程里跑, 直接 logger 会打乱行序且不入阶段日志文件。")


# ── ③ 两处 _ghost_anchor_metrics 调用都带 log_sink ──

def test_worker_passes_log_sink_to_every_ghost_anchor_call():
    node = ast.parse(_dedent(inspect.getsource(ps._auth_year_worker))).body[0]
    calls = [n for n in ast.walk(node)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == '_ghost_anchor_metrics']
    assert len(calls) == 2, (
        f"worker 里 _ghost_anchor_metrics 调用数={len(calls)}, 期望 2 "
        "(vintage 主轨 + _allv 孪生)")
    for i, c in enumerate(calls):
        kw = {k.arg for k in c.keywords}
        assert 'log_sink' in kw, (
            f"第 {i+1} 处 _ghost_anchor_metrics 调用漏传 log_sink —— "
            "该路的 'LDA K=…' 与降级 warning 会跑到子进程 console, 不入阶段日志。")


def test_ghost_anchor_sink_routes_warning_not_logger(monkeypatch):
    """log_sink 给出时, 降级 warning 必须落 sink 而**不**落 logger。"""
    seen = []
    monkeypatch.setattr(ps.logger, 'warning', lambda m, *a, **k: seen.append(m))
    monkeypatch.setattr(ps, '_build_tfidf', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_emb', lambda *a, **k: (None, None))

    def _boom_lda(*a, **k):
        raise RuntimeError("模拟 LDA 崩")

    monkeypatch.setattr(ps, '_build_lda', _boom_lda)

    sink = []
    out = ps._ghost_anchor_metrics(['a', 'b', 'c'], 3, 2020, '锚点', '_full',
                                   log_sink=sink)
    assert out['lda'] and all(np.isnan(v) for v in out['lda'])
    assert any('LDA' in m for _lvl, m in sink), f"LDA 失败告警未进 sink: {sink}"
    assert not seen, f"log_sink 给出时仍直接 logger.warning: {seen}"


def test_ghost_anchor_default_still_logs_directly(monkeypatch):
    """log_sink=None (默认) 必须与旧码同路径 —— 直接 emit。"""
    seen = []
    monkeypatch.setattr(ps.logger, 'warning', lambda m, *a, **k: seen.append(m))
    monkeypatch.setattr(ps, '_build_tfidf', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_emb', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_lda',
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError('x')))
    ps._ghost_anchor_metrics(['a', 'b', 'c'], 3, 2020, '锚点', '_full')
    assert any('LDA' in m for m in seen), "默认路径没有直接落日志 (行为变了)"


# ── ④ BLAS 钉死不得移除 (S5 字节安全的地基) ──

def test_lda_blas_pinning_still_present():
    src = inspect.getsource(sd._build_lda_jsd_matrix)
    assert '_threadpool_limits(limits=1)' in src, (
        "_build_lda_jsd_matrix 的 threadpool_limits(1) 被移除 —— "
        "S5 (policy_similarity 逐年并行) 的字节安全**完全**建立在它之上: "
        "F26 之前该函数因 BLAS 线程数差异漂 ~1e-13 (265/277 键), "
        "父进程用满线程而 loky worker 默认钉 1 ⟹ 并行臂与串行臂算出不同的值。"
        "⚠ 这种漂移 allclose 断言看不出来, 只有位模式比对抓得到。")
    assert 'n_jobs=1' in src, "LDA 的 n_jobs=1 (fix omni-g-strategic-16) 被改动"


def test_lda_log_sink_switches_emitter(monkeypatch):
    """log_sink 给出时, 'LDA K=…' 行落 sink; 默认时落 logger。内容必须一致。"""
    infos = []
    monkeypatch.setattr(sd.logger, 'info', lambda m, *a, **k: infos.append(m))
    texts = [f"金融科技 数字人民币 区块链 支付 风控 {i}" * 20 for i in range(6)]

    sink = []
    sd._build_lda_jsd_matrix(texts, len(texts) - 1, log_sink=sink)
    assert sink and any('LDA K=' in m for _l, m in sink), f"LDA 行未进 sink: {sink}"
    assert not [m for m in infos if 'LDA K=' in m], "sink 模式下仍直接 logger.info"

    infos.clear()
    sd._build_lda_jsd_matrix(texts, len(texts) - 1)
    direct = [m for m in infos if 'LDA K=' in m]
    assert direct, "默认路径未落日志"
    assert direct[0] == [m for _l, m in sink if 'LDA K=' in m][0], (
        "sink 与直接 emit 的行内容不同 —— 日志内容必须逐字节一致, 只切换 emitter")


# ── ⑤ 三条守卫路径 (A/B 真数据覆盖不到, 在此补齐) ──

def test_worker_guard_too_few_banks():
    recs, logs = ps._auth_year_worker(
        ('_full', 2008, ['甲行', '乙行'], ['文本1', '文本2'], '锚点'),
        '静态锚点', True)
    assert recs == [], "银行数 <3 时不应产出记录"
    assert len(logs) == 1 and logs[0][0] == logging.WARNING
    assert '最低要求 3' in logs[0][1], f"守卫告警文案变了: {logs[0][1]}"


def test_worker_guard_vintage_none_companion_off():
    """前视守卫 + companion 关 → 跳过该年 (merge 后留 NaN)。"""
    recs, logs = ps._auth_year_worker(
        ('_full', 2000, ['甲', '乙', '丙'], ['a', 'b', 'c'], None),
        '静态锚点', False)
    assert recs == [], "companion 关闭时前视守卫年应直接跳过"
    assert any('前视守卫' in m for _l, m in logs), f"缺前视守卫告警: {logs}"


def test_worker_guard_vintage_none_companion_on(monkeypatch):
    """前视守卫 + companion 开 → **不**跳过, 仍用静态锚点产 _allv。"""
    monkeypatch.setattr(ps, '_build_tfidf', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_emb', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_lda', lambda *a, **k: (None, None))
    recs, logs = ps._auth_year_worker(
        ('_full', 2000, ['甲', '乙', '丙'], ['a', 'b', 'c'], None),
        '静态锚点', True)
    assert len(recs) == 3, f"companion 开启时应产出 3 条 (_allv 仍要算), 实得 {len(recs)}"
    assert any('前视守卫' in m for _l, m in logs)
    # vintage 主轨全 NaN, _allv 有列 (值由打桩决定, 此处只验列存在性)
    assert all(np.isnan(r['auth_sim_lda_full']) for r in recs)
    assert 'auth_sim_lda_allv_full' in recs[0], "companion 开启却没产 _allv 列"


def test_worker_allv_shortcircuit_avoids_recompute(monkeypatch):
    """vin 锚点 == 静态锚点 → allv 复用 vin 副本, **不重算** (省一半 TF-IDF/LDA/emb)。"""
    calls = []
    real = ps._ghost_anchor_metrics

    def _spy(texts, n, year, anchor, suffix, log_sink=None):
        calls.append(suffix)
        return real(texts, n, year, anchor, suffix, log_sink=log_sink)

    monkeypatch.setattr(ps, '_ghost_anchor_metrics', _spy)
    monkeypatch.setattr(ps, '_build_tfidf', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_emb', lambda *a, **k: (None, None))
    monkeypatch.setattr(ps, '_build_lda', lambda *a, **k: (None, None))

    recs, _ = ps._auth_year_worker(
        ('_full', 2025, ['甲', '乙', '丙'], ['a', 'b', 'c'], '同一锚点'),
        '同一锚点', True)
    assert calls == ['_full'], (
        f"allv 短路失效: _ghost_anchor_metrics 被调用 {calls}, 期望只有主轨一次 "
        "(vin==static 时 allv 应复用 vin 副本)")
    assert len(recs) == 3 and 'auth_sim_lda_allv_full' in recs[0]


# ── ⑥ K 不是常数 10 ──

@pytest.mark.parametrize("n_banks,expect_k", [
    (29, 10),      # 2007 生产实际银行数 → 兜底 10
    (307, 10),     # 2015: 307//30=10
    (428, 14),     # 2017
    (478, 15),     # 2018
    (584, 19),     # 2022 生产最大年
])
def test_lda_k_is_genuinely_adaptive(n_banks, expect_k):
    """锁死 "K 恒为 10 (伪自适应)" 这一旧披露的订正。

    该说法成立的前提是 "<300 银行/年"; 生产 T=19 语料 2017-2025 每年 428-584 家,
    stage 40 日志实测 K ∈ {10,11,14,15,18,19} (三轨各 37 次 fit 全部核对)。
    K 直接驱动 LDA 耗时 —— 这正是本模块占 stage 40 37.8% 的原因之一。
    """
    assert max(10, n_banks // 30) == expect_k


def test_k_constant_claim_purged_from_docstring():
    doc = sd._build_lda_jsd_matrix.__doc__ or ''
    assert '2026-07-28' in doc and '证伪' in doc, (
        "_build_lda_jsd_matrix docstring 里 'K 对本样本实为固定常数 10' 的订正被回退")


# ── 父端回放必须打回**原调用面** ──

def test_parent_replays_on_original_logger_methods():
    """回放不得统一走 ``logger.log(lvl, msg)``, 必须按级别分派回 warning/info。

    2026-07-28 实弹: 首版用 `logger.log(_lvl, _msg)` 统一回放, 输出的日志行与串行
    **完全相同**, 但 `test_omni_fix_policy` 里用 Mock 断言 `logger.warning` 被调用
    的两个守卫测试当场变红。

    ⚠ 更值得记的是: 本次改动自带的 A/B "日志逐行比对" **抓不到这个** ——
    A/B 用 `logging.Handler` 捕获, 而 Handler 分辨不出 `warning(m)` 与
    `log(WARNING, m)`。是既有单测补上了 A/B 的盲区。
    """
    src = inspect.getsource(ps.compute_authoritative_similarity)
    assert 'logger.warning(_msg)' in src and 'logger.info(_msg)' in src, \
        "父端回放没有按级别分派回原调用面 (logger.warning / logger.info)"
    assert 'logger.log(_lvl' not in src, \
        "父端回放退回了统一 logger.log() —— 会让 Mock 断言 logger.warning 的既有单测变红"


# ── 运维旁路 ──

@pytest.mark.parametrize("raw,expect", [
    ('', None), ('  ', None), ('8', 8), ('12', 12),
    ('0', None), ('-3', None), ('abc', None),
])
def test_auth_jobs_env_override(monkeypatch, raw, expect):
    if raw == '':
        monkeypatch.delenv(ps._AUTH_JOBS_ENV, raising=False)
    else:
        monkeypatch.setenv(ps._AUTH_JOBS_ENV, raw)
    assert ps._auth_jobs_override() == expect
