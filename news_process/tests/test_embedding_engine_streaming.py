"""F1 (2026-07-16) gate: 嵌入引擎缓存拼装流式化 — 等价性/守卫/内存 十项。

缺陷 (fatal): get_embeddings_api 旧实现全量物化 N 条缓存 JSON 字符串 + N 条
json.loads Python 列表 (双份同活 ~217KB/篇 ≈ 13.5× 临时放大) → 生产 post-13
语料 ≥~55 万篇越过 128GB; 离线 0-miss 复现路径同样中招。

修复: 命中侧逐条流式写入预分配 (N, dim) float32 矩阵; miss 批成功后按
batch_rows fancy indexing 直写全局行 (_embs_by_idx 退役); 逐批数量校验走
ValueError 穿透重试环; _rows_written 完备计数。

计划: scripts/audit/FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN_2026-07-16.md §2-F1。
mock 纪律: 零网络 (patch aiohttp.ClientSession.post), 零真实 data/processed 写。
"""
import asyncio
import json
import tracemalloc
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from news_process.pipeline.text import embedding_engine as eng

SPEC = {'base_url': 'http://fake-endpoint', 'api_key': 'test-key',
        'model': 'test-embed-model', 'text_pipeline_version': 'v-test'}

_REAL_DB = (Path(__file__).resolve().parents[1] / 'data' / 'processed'
            / '_llm_cache.db')


def _vec(seed: int, dim: int) -> list[float]:
    rng = np.random.default_rng(seed)
    return [float(x) for x in rng.normal(size=dim)]


class FakeCache:
    """最小缓存假体: get 返回 JSON 字符串或 None; put_batch 记账。"""

    def __init__(self, store=None, lazy_dim=None):
        self._store = dict(store or {})
        self._lazy_dim = lazy_dim  # 惰性模式: get 时才生成 JSON (T7 tracemalloc 语义)
        self.put_calls: list[list[str]] = []

    def get(self, model, text, prompt_version=None):
        if self._lazy_dim is not None:
            return json.dumps(_vec(hash(text) % (2**32), self._lazy_dim))
        return self._store.get(text)

    def put_batch(self, model, texts, responses, prompt_version=None):
        self.put_calls.append(list(texts))
        for t, r in zip(texts, responses):
            self._store[t] = r


class _FakeResp:
    def __init__(self, status, payload=None, text='', pre_json=None, pre_text=None):
        self.status = status
        self._payload = payload
        self._text = text
        self._pre_json = pre_json   # 可等待钩子: json() 前 await (T9 乱序注入)
        self._pre_text = pre_text   # 可等待钩子: text() 前 await (T8 定序)

    async def json(self):
        if self._pre_json is not None:
            await self._pre_json()
        return self._payload

    async def text(self):
        if self._pre_text is not None:
            await self._pre_text()
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _ok_payload(batch, dim, seed_fn):
    return {'data': [{'index': i, 'embedding': _vec(seed_fn(t), dim)}
                     for i, t in enumerate(batch)]}


def _reference(texts, store, dim, seed_fn):
    """旧实现语义参考臂: 全量列表 → np.array(list_of_lists, float32)。"""
    final = []
    for t in texts:
        res = store.get(t)
        final.append(json.loads(res) if res is not None else _vec(seed_fn(t), dim))
    return np.array(final, dtype=np.float32)


def _run(texts, cache, **kw):
    return asyncio.run(eng.get_embeddings_api(
        texts, SPEC, cache=cache, enable_archive=False, **kw))


@pytest.fixture()
def online(monkeypatch):
    """miss-网络路径测试: 确保离线守卫不拦 (pytest 会话可能带 OFFLINE=1)。"""
    monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)
    monkeypatch.setattr(eng, 'RETRY_DELAY', 0)


# ---------------------------------------------------------------- T1 全命中等价
def test_t1_all_hit_bitwise_equivalence():
    dim = 64
    texts = [f'文本{i}' for i in range(30)]
    store = {t: json.dumps(_vec(i, dim)) for i, t in enumerate(texts)}
    out = _run(texts, FakeCache(store))
    ref = _reference(texts, store, dim, lambda t: 0)
    assert out.dtype == np.float32 and out.shape == (30, dim)
    assert out.tobytes() == ref.tobytes()


@pytest.mark.skipif(not _REAL_DB.exists(),
                    reason='_llm_cache.db 不在盘 (data/ 不随 checkout 分发)')
def test_t1b_real_cache_entries_equivalence():
    """盘上真条目子用例: 真实 JSON 串的 double→float32 舍入逐位等价。"""
    import sqlite3
    try:
        con = sqlite3.connect(f'file:{_REAL_DB}?mode=ro', uri=True)
        tbl = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchone()[0]
        rows = con.execute(
            f"SELECT response FROM {tbl} WHERE response LIKE '[%' LIMIT 3"
        ).fetchall()
        con.close()
    except Exception as exc:  # noqa: BLE001 — 库 schema 变化即跳过, 不红
        pytest.skip(f'读取真缓存条目失败: {exc!r}')
    if not rows:
        pytest.skip('真缓存无嵌入 JSON 条目')
    texts = [f'真条目{i}' for i in range(len(rows))]
    store = {t: r[0] for t, r in zip(texts, rows)}
    out = _run(texts, FakeCache(store))
    ref = np.array([json.loads(r[0]) for r in rows], dtype=np.float32)
    assert out.tobytes() == ref.tobytes()


# ------------------------------------------------------------- T2 hit/miss 交错
def test_t2_interleaved_hit_miss(online):
    dim = 32
    texts = [f'条目{i}' for i in range(10)]
    store = {t: json.dumps(_vec(100 + i, dim))
             for i, t in enumerate(texts) if i % 2 == 0}  # 偶数命中, 奇数 miss
    cache = FakeCache(store)
    seed_fn = lambda t: 500 + int(t[2:])  # noqa: E731

    def fake_post(self, url, **kw):
        batch = kw['json']['input']
        return _FakeResp(200, _ok_payload(batch, dim, seed_fn))

    with patch('aiohttp.ClientSession.post', new=fake_post):
        out = _run(texts, cache)
    ref = _reference(texts, store, dim, seed_fn)
    assert out.tobytes() == ref.tobytes()  # 命中/缺失行各归其位, 无错位


# ---------------------------------------------------------------- T3 全 miss 等价
def test_t3_all_miss(online):
    dim = 16
    texts = [f'新文{i}' for i in range(7)]
    cache = FakeCache()
    seed_fn = lambda t: 900 + int(t[2:])  # noqa: E731

    def fake_post(self, url, **kw):
        batch = kw['json']['input']
        return _FakeResp(200, _ok_payload(batch, dim, seed_fn))

    with patch('aiohttp.ClientSession.post', new=fake_post):
        out = _run(texts, cache)
    ref = _reference(texts, {}, dim, seed_fn)
    assert out.tobytes() == ref.tobytes()
    assert cache.put_calls  # 成功批已写缓存


# ----------------------------------------------------- T4 OFFLINE+miss 守卫不变
def test_t4_offline_miss_raises_before_network(monkeypatch):
    monkeypatch.setenv('NEWS_PROCESS_LLM_OFFLINE', '1')
    calls = []

    def fake_post(self, url, **kw):
        calls.append(url)
        return _FakeResp(200, {'data': []})

    with patch('aiohttp.ClientSession.post', new=fake_post):
        with pytest.raises(RuntimeError, match='离线确定性模式'):
            _run(['缺失文本'], FakeCache())
    assert calls == []  # raise 发生在任何网络调用之前


# ------------------------------------------------------------- T5 维度不齐 fail-loud
def test_t5_dim_mismatch_fail_loud():
    dim = 8
    texts = ['甲', '乙', '丙']
    store = {'甲': json.dumps(_vec(1, dim)),
             '乙': json.dumps([1.0]),          # 损坏条目: len=1 (标量广播毒饵)
             '丙': json.dumps(_vec(3, dim))}
    with pytest.raises(RuntimeError, match='维度不齐'):
        _run(texts, FakeCache(store))


# ---------------------------------------------------------------- T6 空输入早退
def test_t6_empty_input():
    out = _run([], FakeCache())
    assert out.shape == (0, 0) and out.dtype == np.float32


# ------------------------------------------------------------ T7 峰值内存 < 3×final
def test_t7_peak_memory_regression():
    dim, n = 4096, 64
    texts = [f'大文本{i}' for i in range(n)]
    cache = FakeCache(lazy_dim=dim)  # 惰性生成 JSON 串 (tracemalloc 窗口内分配)
    final_bytes = n * dim * 4        # n=64: final=1.0MB; 逐行瞬态 ~220KB → peak≈1.2×
    tracemalloc.start()
    out = _run(texts, cache)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert out.shape == (n, dim)
    assert peak < 3 * final_bytes, f'peak={peak:,} >= 3×final={3 * final_bytes:,}'


# ------------------------------------------- T8 重试穷尽 → None, 部分矩阵不外泄
def test_t8_retry_exhausted_returns_none(online, monkeypatch):
    monkeypatch.setattr(eng, 'EMB_MAX_RETRIES', 2)
    monkeypatch.setattr(eng, 'EMB_MAX_TOKENS_PER_REQUEST', 1)  # 每文本一批
    monkeypatch.setattr(eng, 'EMB_API_CONCURRENCY', 4)
    dim = 8
    texts = ['成功批文本', '失败批文本']
    cache = FakeCache()
    success_done = asyncio.Event()

    def fake_post(self, url, **kw):
        batch = kw['json']['input']
        if batch == ['成功批文本']:
            async def _mark():
                pass
            return _FakeResp(200, _ok_payload(batch, dim, lambda t: 7))
        # 失败批: 每次 5xx; text() 先等成功批 put_batch 落地 (定序, 非调度巧合)
        async def _wait():
            await success_done.wait()
        return _FakeResp(503, text='boom', pre_text=_wait)

    orig_put = FakeCache.put_batch

    def put_and_signal(self, model, texts_, responses, prompt_version=None):
        orig_put(self, model, texts_, responses, prompt_version=prompt_version)
        success_done.set()

    monkeypatch.setattr(FakeCache, 'put_batch', put_and_signal)
    with patch('aiohttp.ClientSession.post', new=fake_post):
        result = _run(texts, cache)
    assert result is None                      # 部分填充矩阵绝不外泄
    assert ['成功批文本'] in cache.put_calls   # 已成功批副作用保留 (与旧行为一致)


# ------------------------------------------------------------- T9 乱序完成等价
def test_t9_out_of_order_completion(online, monkeypatch):
    monkeypatch.setattr(eng, 'EMB_MAX_TOKENS_PER_REQUEST', 1)  # 每文本一批
    monkeypatch.setattr(eng, 'EMB_API_CONCURRENCY', 8)
    dim = 12
    texts = [f'批{i}' for i in range(5)]
    seed_fn = lambda t: 300 + int(t[1:])  # noqa: E731

    def fake_post(self, url, **kw):
        batch = kw['json']['input']
        idx = int(batch[0][1:])

        async def _delay():
            await asyncio.sleep((5 - idx) * 0.02)  # 逆序完成: 批4 最先, 批0 最后

        return _FakeResp(200, _ok_payload(batch, dim, seed_fn), pre_json=_delay)

    with patch('aiohttp.ClientSession.post', new=fake_post):
        out = _run(texts, FakeCache())
    ref = _reference(texts, {}, dim, seed_fn)
    assert out.tobytes() == ref.tobytes()  # 批→行映射在乱序下锁死


# ---------------------------------------------- T10 短响应 → ValueError 穿透重试环
def test_t10_short_response_raises_valueerror(online, monkeypatch):
    monkeypatch.setattr(eng, 'EMB_MAX_RETRIES', 2)
    dim = 8
    texts = ['多条一', '多条二', '多条三']  # 单批 m=3

    def fake_post(self, url, **kw):
        batch = kw['json']['input']
        # 恶意短响应: m>1 只回 1 条 (若直写将被广播成整段复制行)
        return _FakeResp(200, {'data': [{'index': 0,
                                         'embedding': _vec(1, dim)}]})

    with patch('aiohttp.ClientSession.post', new=fake_post):
        with pytest.raises(ValueError, match='返回数量异常'):
            _run(texts, FakeCache())


# ----------------------------------------------------- 源码级: 断言机制不可回退
def test_source_level_guards():
    import inspect
    src = inspect.getsource(eng.get_embeddings_api)
    assert '_rows_written' in src                      # 写行完备计数在位
    assert 'assert _rows_written == len(texts)' in src
    assert '返回数量异常' in src and 'ValueError' in src  # 逐批校验走 ValueError
    # 旧机制以【代码用法形态】断言退役 (裸词在 F1 说明注释中合法出现):
    assert '_embs_by_idx[' not in src                  # 中转 dict 下标写入已退役
    assert '_embs_by_idx: dict' not in src             # 中转 dict 声明已退役
    assert 'final_embs.append' not in src              # 全量列表拼装已退役
    assert 'cached_results = [' not in src             # 全量 JSON 串物化已退役
    # OFFLINE 守卫仍在 miss 分支、网络调用之前
    assert 'NEWS_PROCESS_LLM_OFFLINE' in src


# ------------------------------------------- M1: 归档先于缓存 (_archive_ok 范式)
class TestM1ArchiveBeforeCache:
    """M1 (2026-07-16, FATAL_DEFECT_REMEDIATION §2-M1): put_batch 先于 archive 且
    归档失败仅 warning → 该批永久命中缓存、归档一次性永久漏档。修法镜像 tone_llms
    omni-g-tonellms-04: 归档前移, 失败跳缓存 (下次 run 重调+重归档)。"""

    def _run_one_miss(self, monkeypatch, archive_raises, enable_archive=True):
        monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)
        monkeypatch.setattr(eng, 'RETRY_DELAY', 0)
        dim = 8
        cache = FakeCache()
        calls = {'archive': 0}

        class _FakeArchive:
            def append_batch(self, records):
                calls['archive'] += 1
                if archive_raises:
                    raise OSError('archive down')

        monkeypatch.setattr(eng, '_LLM_ARCHIVE_AVAILABLE', True)
        monkeypatch.setattr(eng, '_get_archive', lambda: _FakeArchive())

        def fake_post(self, url, **kw):
            batch = kw['json']['input']
            return _FakeResp(200, _ok_payload(batch, dim, lambda t: 5))

        with patch('aiohttp.ClientSession.post', new=fake_post):
            out = asyncio.run(eng.get_embeddings_api(
                ['单条缺失'], SPEC, cache=cache, enable_archive=enable_archive))
        return out, cache, calls

    def test_archive_fail_skips_cache(self, monkeypatch):
        out, cache, calls = self._run_one_miss(monkeypatch, archive_raises=True)
        assert out is not None and calls['archive'] == 1
        assert cache.put_calls == []   # 归档失败 → 不写缓存 (永久漏档窗口关闭)

    def test_archive_ok_then_cache(self, monkeypatch):
        out, cache, calls = self._run_one_miss(monkeypatch, archive_raises=False)
        assert calls['archive'] == 1
        assert cache.put_calls == [['单条缺失']]

    def test_enable_archive_false_still_caches(self, monkeypatch):
        out, cache, calls = self._run_one_miss(monkeypatch, archive_raises=True,
                                               enable_archive=False)
        assert calls['archive'] == 0
        assert cache.put_calls == [['单条缺失']]   # 与 tone_llms 同语义: 不归档仍缓存
