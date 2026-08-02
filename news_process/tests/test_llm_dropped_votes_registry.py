"""tests/test_llm_dropped_votes_registry.py — D1 弃票登记表单测 (2026-08-02)。

背景: 模型对个别 (model, prompt) 格**永久拒绝**出票 —— 实测两型: DeepSeek 返
HTTP 400 "Content Exists Risk" 内容风控; gemini31 对特定长文本连续 30 次返回空
completion。这类响应按承重设计绝不写入主缓存 (`_is_cacheable_llm_response` 闸门),
于是这些格永久缺条目, 离线确定性模式下 miss → raise → **整个付费阶段崩溃**。

用户裁定 (2026-08-02) 采用「仅 permanent」变体的弃票登记表: 独立表登记已证实的
永久失败, 离线遇之按缺票放行 (与在线路径逐字节一致); **瞬时故障绝不登记**, 遇之
照旧 hard-fail 提醒回填。

本文件覆盖该裁定的四条不变量:
  1. 读取侧 — 离线 miss 但登记表有据 → 返回 None 票, 不抛。
  2. 读取侧 — 离线 miss 且登记表无据 → 仍抛 LLMCacheMissError (纪律不松)。
  3. 写入侧 — 不可重试 HTTP (400) → 登记为 http_permanent。
  4. 写入侧 — 瞬时故障 (超时/5xx) → **不**登记 (这是「仅 permanent」的落点);
     连续空响应但次数不足地板值 → 亦不登记。
外加: 登记表与主缓存**语义正交** (登记绝不污染主缓存)。

全程零网络: 需要 HTTP 的用例用 fake session 桩替代 aiohttp。
"""
from __future__ import annotations

import asyncio

import pytest

from news_process.core.caching import LLMCache
from news_process.pipeline.sentiment import tone_llms


def _model_cfg():
    return {'model_name': 'unit-test-model', 'short_name': 'utm',
            'base_url': 'http://invalid.localhost', 'api_key': 'k'}


def _key_kw():
    """与 fetch_llm_async 内部完全一致的键参数 — 键不一致等于测了个寂寞。"""
    return dict(prompt_version=tone_llms.PROMPT_VERSION,
                temperature=tone_llms.TEMPERATURE,
                random_seed=tone_llms.RANDOM_SEED)


# ---------------------------------------------------------------------------
# 零网络 HTTP 桩: 模拟 aiohttp 的 `async with session.post(...) as resp`
# ---------------------------------------------------------------------------

class _FakeResp:
    def __init__(self, status: int, payload: dict | None = None, text: str = ''):
        self.status = status
        self._payload = payload or {}
        self._text = text

    async def json(self):
        return self._payload

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    """按预设脚本逐次返回响应; 记录调用次数供断言重试行为。"""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def post(self, *_args, **_kwargs):
        self.calls += 1
        item = self._responses[min(self.calls - 1, len(self._responses) - 1)]
        if isinstance(item, Exception):
            raise item
        return item


def _run_fetch(session, cache, cfg, prompt, *, max_retries):
    return asyncio.run(tone_llms.fetch_llm_async(
        session, asyncio.Semaphore(1), prompt, cfg, 0, 'full',
        cache=cache, max_retries=max_retries,
        prompt_version=tone_llms.PROMPT_VERSION,
    ))


# ---------------------------------------------------------------------------
# 1 / 2 — 读取侧 (离线)
# ---------------------------------------------------------------------------

def test_offline_registered_dropped_vote_returns_none_instead_of_raising(
        tmp_path, monkeypatch):
    """离线 + 主缓存 miss + 登记表有据 → 返 None 票放行, 不抛。

    这正是本次 D1 整改要解决的生产事故: 4 个物理不可回填的格让整条离线主流水线
    exit=1。放行后行为与在线路径 (返 None 票、退化为 2 票多数决) 逐字节一致。
    """
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', True)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'permanently-refused-prompt'
    try:
        cache.put_dropped_vote(
            cfg['model_name'], prompt,
            failure_kind='http_permanent',
            reason='HTTP 400 不可重试错误: Content Exists Risk',
            attempts=1, http_status=400, **_key_kw())

        row_idx, model_id, res, track = _run_fetch(
            None, cache, cfg, prompt, max_retries=80)

        assert res is None, "登记为永久弃票的格应返回 None 票 (缺票), 而非响应文本"
        assert (row_idx, model_id, track) == (0, cfg['model_name'], 'full')
        # 语义正交: 放行绝不能顺手往主缓存塞东西
        assert cache.get(cfg['model_name'], prompt, **_key_kw()) is None
    finally:
        cache.close()


def test_offline_unregistered_miss_still_raises(tmp_path, monkeypatch):
    """离线 + 主缓存 miss + 登记表**无**据 → 仍 raise (纪律不因整改而松)。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', True)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    try:
        # 登记另一个 prompt, 确认判定是按键精确匹配而非"表非空就放行"
        cache.put_dropped_vote(
            cfg['model_name'], 'some-other-prompt',
            failure_kind='http_permanent', reason='r', attempts=1,
            http_status=400, **_key_kw())
        with pytest.raises(tone_llms.LLMCacheMissError):
            _run_fetch(None, cache, cfg, 'never-seen-prompt', max_retries=80)
    finally:
        cache.close()


def test_registry_lookup_is_model_scoped(tmp_path, monkeypatch):
    """同一 prompt 下, A 模型的登记不得放行 B 模型 (键含 model_id)。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', True)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg_a = _model_cfg()
    cfg_b = dict(cfg_a, model_name='other-model')
    prompt = 'shared-prompt'
    try:
        cache.put_dropped_vote(cfg_a['model_name'], prompt,
                               failure_kind='http_permanent', reason='r',
                               attempts=1, http_status=400, **_key_kw())
        # A 放行
        assert _run_fetch(None, cache, cfg_a, prompt, max_retries=80)[2] is None
        # B 仍抛
        with pytest.raises(tone_llms.LLMCacheMissError):
            _run_fetch(None, cache, cfg_b, prompt, max_retries=80)
    finally:
        cache.close()


# ---------------------------------------------------------------------------
# 3 / 4 — 写入侧 (在线)
# ---------------------------------------------------------------------------

def test_permanent_http_failure_is_registered(tmp_path, monkeypatch):
    """不可重试 HTTP 400 → 登记 http_permanent, 且只调用 1 次 (fail-fast)。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', False)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'risky-content-prompt'
    session = _FakeSession([_FakeResp(400, text='{"error":"Content Exists Risk"}')])
    try:
        res = _run_fetch(session, cache, cfg, prompt, max_retries=80)[2]
        assert res is None
        assert session.calls == 1, "400 属不可重试错误, 必须 fail-fast 不重试"

        rec = cache.get_dropped_vote(cfg['model_name'], prompt, **_key_kw())
        assert rec is not None, "不可重试 HTTP 必须登记为永久弃票"
        assert rec['failure_kind'] == 'http_permanent'
        assert rec['http_status'] == 400
        # 语义正交: 坏响应绝不进主缓存 (承重设计零妥协)
        assert cache.get(cfg['model_name'], prompt, **_key_kw()) is None
    finally:
        cache.close()


def test_sustained_empty_response_is_registered(tmp_path, monkeypatch):
    """每次都返空 + 尝试数 ≥ 地板值 → 登记 empty_response。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', False)
    monkeypatch.setattr(tone_llms, 'RETRY_DELAY', 0)   # 不真 sleep
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'always-empty-prompt'
    n = tone_llms._PERMANENT_EMPTY_MIN_ATTEMPTS
    empty = _FakeResp(200, {'choices': [{'message': {'content': ''}}]})
    session = _FakeSession([empty] * n)
    try:
        assert _run_fetch(session, cache, cfg, prompt, max_retries=n)[2] is None
        rec = cache.get_dropped_vote(cfg['model_name'], prompt, **_key_kw())
        assert rec is not None, "连续 N 次稳定返空属永久型, 应登记"
        assert rec['failure_kind'] == 'empty_response'
        assert rec['attempts'] == n
        assert cache.get(cfg['model_name'], prompt, **_key_kw()) is None
    finally:
        cache.close()


def test_empty_response_below_floor_is_not_registered(tmp_path, monkeypatch):
    """空响应但尝试次数 < 地板值 → **不**登记。

    守的是判据强度: 若判据写成"用满 max_retries 即永久", 把 max_retries 调到 1
    就能让任何一次偶发失败被登记成永久弃票。地板值与 max_retries 解耦即为此。
    """
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', False)
    monkeypatch.setattr(tone_llms, 'RETRY_DELAY', 0)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'briefly-empty-prompt'
    n = tone_llms._PERMANENT_EMPTY_MIN_ATTEMPTS - 1
    assert n >= 1
    empty = _FakeResp(200, {'choices': [{'message': {'content': ''}}]})
    session = _FakeSession([empty] * n)
    try:
        assert _run_fetch(session, cache, cfg, prompt, max_retries=n)[2] is None
        assert cache.get_dropped_vote(cfg['model_name'], prompt, **_key_kw()) is None
    finally:
        cache.close()


def test_transient_failures_are_not_registered(tmp_path, monkeypatch):
    """超时 / 5xx 等瞬时故障耗尽重试 → **不**登记 (「仅 permanent」的落点)。

    这类格下次跑可能成功; 静默放行会把真实的网络问题固化成"缺票"而不再提醒回填。
    """
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', False)
    monkeypatch.setattr(tone_llms, 'RETRY_DELAY', 0)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    n = tone_llms._PERMANENT_EMPTY_MIN_ATTEMPTS + 2
    try:
        # ① 全程 503 (可重试状态码)
        s1 = _FakeSession([_FakeResp(503, text='busy')] * n)
        assert _run_fetch(s1, cache, cfg, 'p-503', max_retries=n)[2] is None
        assert cache.get_dropped_vote(cfg['model_name'], 'p-503', **_key_kw()) is None

        # ② 全程超时
        s2 = _FakeSession([asyncio.TimeoutError()] * n)
        assert _run_fetch(s2, cache, cfg, 'p-timeout', max_retries=n)[2] is None
        assert cache.get_dropped_vote(cfg['model_name'], 'p-timeout',
                                      **_key_kw()) is None
    finally:
        cache.close()


def test_mixed_empty_and_transient_is_not_registered(tmp_path, monkeypatch):
    """空响应中掺了一次瞬时故障 → 判为瞬时, **不**登记 (empty == attempts 才算)。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', False)
    monkeypatch.setattr(tone_llms, 'RETRY_DELAY', 0)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'mixed-failure-prompt'
    n = tone_llms._PERMANENT_EMPTY_MIN_ATTEMPTS + 1
    empty = _FakeResp(200, {'choices': [{'message': {'content': ''}}]})
    # 第 1 次 503, 其余全空 → empty_attempts = n-1 < attempts_used = n
    session = _FakeSession([_FakeResp(503, text='busy')] + [empty] * (n - 1))
    try:
        assert _run_fetch(session, cache, cfg, prompt, max_retries=n)[2] is None
        assert cache.get_dropped_vote(cfg['model_name'], prompt, **_key_kw()) is None
    finally:
        cache.close()


# ---------------------------------------------------------------------------
# 表本身的行为
# ---------------------------------------------------------------------------

def test_reregistration_preserves_first_seen(tmp_path):
    """同一格重复登记 → first_seen 保留首次值, last_seen/attempts 刷新。"""
    cache = LLMCache(str(tmp_path / 'c.db'))
    try:
        kw = dict(failure_kind='empty_response', reason='r1', http_status=None,
                  **_key_kw())
        cache.put_dropped_vote('m', 'p', attempts=5, **kw)
        first = cache.get_dropped_vote('m', 'p', **_key_kw())
        cache.put_dropped_vote('m', 'p', attempts=30,
                               **dict(kw, reason='r2'))
        second = cache.get_dropped_vote('m', 'p', **_key_kw())
        assert second['first_seen'] == first['first_seen']
        assert second['last_seen'] >= first['last_seen']
        assert second['attempts'] == 30
        assert second['reason'] == 'r2'
    finally:
        cache.close()


def test_dropped_vote_stats_groups_by_kind(tmp_path):
    """dropped_vote_stats 按 failure_kind 分组计数 (供阶段日志对账)。"""
    cache = LLMCache(str(tmp_path / 'c.db'))
    try:
        assert cache.dropped_vote_stats() == {'total': 0, 'by_kind': {}}
        cache.put_dropped_vote('m', 'p1', failure_kind='http_permanent',
                               reason='r', attempts=1, http_status=400, **_key_kw())
        cache.put_dropped_vote('m', 'p2', failure_kind='empty_response',
                               reason='r', attempts=30, **_key_kw())
        cache.put_dropped_vote('m', 'p3', failure_kind='empty_response',
                               reason='r', attempts=30, **_key_kw())
        st = cache.dropped_vote_stats()
        assert st['total'] == 3
        assert st['by_kind'] == {'http_permanent': 1, 'empty_response': 2}
    finally:
        cache.close()


def test_registry_is_isolated_from_main_cache(tmp_path):
    """登记表与主缓存互不串味: 登记不影响 get(), 主缓存写入不影响登记查询。"""
    cache = LLMCache(str(tmp_path / 'c.db'))
    try:
        cache.put_dropped_vote('m', 'p', failure_kind='http_permanent',
                               reason='r', attempts=1, http_status=400, **_key_kw())
        assert cache.get('m', 'p', **_key_kw()) is None

        cache.put('m2', 'p2', '{"ok": true}', **_key_kw())
        assert cache.get_dropped_vote('m2', 'p2', **_key_kw()) is None
    finally:
        cache.close()
