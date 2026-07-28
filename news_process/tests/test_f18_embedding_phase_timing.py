"""tests/test_f18_embedding_phase_timing.py — F18 gate: 嵌入引擎分段计时必须可达且落盘。

**为何需要 (2026-07-28 归因困境)**:
stage 40 的「步骤 7h-emb 嵌入同业网」吃掉 **20,471s = 整个 stage 的 20.31%**, 而它的
API/CPU 构成**至今无人知道** —— 因为本模块用 ``getLogger(__name__)``, 在 F29
(main=e94bf57f) 之前该 logger 链上无 handler, INFO 一条都没落过盘。审计当时只能靠
「``_llm_cache.db`` 文件长胖了多少」反推是否在付费。**审计不该是这个姿势。**

同一次归因还暴露: 43,006 条 429 限流告警被误判为 28 小时的主因 (实际仅 ~9.6%),
真正的极是纯 CPU 的串行 LDA —— 而这个误判本可以被分段计时一眼澄清。

本 gate 锁死三条:
  ① 全命中路径必须打「⏱ 分段计时」且含三段与 n_missing;
  ② 重试耗尽 (F28 事故现场) 的失败路径**也**必须打计时 —— 当时既不知道它等了多久,
     也不知道 API 段占多少;
  ③ 「缓存拦截: 命中 N 条」命中率行仍在 (F29 让它第一次可见, 不得回退)。
"""
from __future__ import annotations

import json
import logging
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.text import embedding_engine as eng  # noqa: E402

_DIM = 8
_SPEC = {
    'base_url': 'https://example.invalid/v1',
    'api_key': 'test-key',
    'model': 'probe-model',
    'text_pipeline_version': 'probe-v1',
}


class _AllHitCache:
    """桩缓存: 任何 key 都命中, 返回定长向量。

    ⚠ 真 ``LLMCache`` 存的是 **JSON 字符串** (引擎侧 ``json.loads`` 解析),
    故桩必须同构 —— 首版返回裸 list 导致 ``TypeError: the JSON object must be
    str, bytes or bytearray, not list``, 是桩写错不是引擎错。
    """

    def __init__(self, dim=_DIM):
        self.dim = dim
        self._payload = json.dumps([0.1] * dim)

    def get(self, *a, **kw):
        return self._payload

    def get_batch(self, keys, *a, **kw):
        return {k: self._payload for k in keys}

    def put_batch(self, *a, **kw):
        return None

    def put(self, *a, **kw):
        return None


class _Cap(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines: list[str] = []
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)
        self.lines.append(record.getMessage())

    def having(self, needle: str) -> list[str]:
        return [x for x in self.lines if needle in x]


@pytest.fixture()
def cap():
    h = _Cap()
    eng.logger.addHandler(h)
    eng.logger.setLevel(logging.INFO)
    try:
        yield h
    finally:
        eng.logger.removeHandler(h)


def _run(texts, cache):
    import asyncio
    return asyncio.run(eng.get_embeddings_api(texts, _SPEC, cache=cache,
                                              enable_archive=False))


# ── ① 全命中路径: 必须有分段计时 ──

def test_all_hit_path_emits_phase_timing(cap, monkeypatch):
    monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)
    texts = [f'探针文本{i} 金融科技 数字人民币' for i in range(6)]
    out = _run(texts, _AllHitCache())
    assert out is not None and out.shape == (6, _DIM), '全命中路径应直接返回矩阵'

    timing = cap.having('⏱ 分段计时')
    assert timing, (
        '全命中路径没有打分段计时 —— 2026-07-28 归因 stage 40 时正是因为缺这一行, '
        '20,471s (20.31%) 的 API/CPU 构成至今无解。')
    line = timing[0]
    for token in ('缓存查', 'API 段', '合计', 'n_missing='):
        assert token in line, f'分段计时缺字段 {token}: {line}'


def test_cache_hit_rate_line_still_visible(cap, monkeypatch):
    """F29 让这行第一次可见, 不得回退。"""
    monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)
    _run([f'文本{i}' for i in range(4)], _AllHitCache())
    assert cap.having('缓存拦截'), '缓存命中率行消失 —— 它是判断「是否在付费」的唯一线索'


# ── ② 失败路径 (F28 事故现场) 也必须留计时 ──

def test_retry_exhausted_path_also_emits_timing(cap, monkeypatch):
    """重试耗尽返回 None 时, 必须同时留下分段计时。

    2026-07-27 生产: 该路径触发两次 (ctx/ss 轨), 直接导致面板 4 列全 NaN。
    当时日志只说「重试 80 次仍失败」, **没有任何时间信息** —— 无法判断它是卡在
    退避上还是别的地方。
    """
    monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)

    class _MissCache(_AllHitCache):
        def get(self, *a, **kw):
            return None

        def get_batch(self, keys, *a, **kw):
            return {}

    async def _boom(*a, **kw):
        raise eng.EmbeddingRetryExhaustedError('模拟 429 重试耗尽')

    # 让批处理直接抛重试耗尽
    monkeypatch.setattr(eng.asyncio, 'gather', _boom)
    out = _run(['文本A', '文本B'], _MissCache())
    assert out is None, '重试耗尽应返回 None (调用方据此置 NaN)'

    err_timing = [x for x in cap.lines if '分段计时' in x and '失败' in x]
    assert err_timing, (
        '重试耗尽路径没有留下分段计时 —— 这正是 F28 的事故现场, '
        '当时既不知道等了多久, 也不知道 API 段占多少。')
    assert any(r.levelno >= logging.ERROR for r in cap.records), \
        '重试耗尽必须 ERROR 级 (配合 F29 才能被 grep ERROR 判据抓到)'


# ── ③ 源码级防回退 ──

def test_timing_instrumentation_present_in_source():
    import inspect
    src = inspect.getsource(eng.get_embeddings_api)
    for token in ('_t_start', '_t_cache_done', '_t_api_done', '⏱ 分段计时'):
        assert token in src, f'F18 计时探针缺 {token}'
    assert src.count('⏱ 分段计时') >= 2, \
        '成功与失败两条路径都必须打计时 (失败路径正是 F28 的事故现场)'
