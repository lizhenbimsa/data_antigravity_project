"""test_prompt_audit_s7_s8.py — S7/S8 专属断言 (PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12)
================================================================================
锁定两处"归档/缓存写入闸"整改后的行为, 防静默 revert:

- S7 (`pipeline/panel/llm_peer_iv.py::_call_llm_peer`): 机械镜像
  `tone_llms.py` omni-g-tonellms-04 的 `_archive_ok` 模式 —— archive 先于
  cache.put, archive 失败则本次跳过 put (下次 run 因未命中缓存会重调 API
  并重试归档)。同批新增本通道写入闸 `_is_cacheable_peer_response`
  (校验键 "peers", 不可直接 import 复用 tone_llms 版本 —— 见
  `llm_peer_iv.py` 内 `_is_cacheable_peer_response` docstring 的复用陷阱披露)。

- S8 (`scripts/migrate/v7_wz_audit.py::call_llm_with_cache`): 在线路径
  cache.put 前补写入闸, 直接 import 复用 `tone_llms._is_cacheable_llm_response`
  (本工具 PROMPT_TEMPLATE 读活 config, 与 stage 21 同一份 v8 unified_cot.txt /
  同一 JSON 契约, 无 S7 场景下的校验键语义分歧)。

全部测试 mock LLMCache / archive 函数 / aiohttp session, 不真调外部 API、
不真写生产 `_llm_cache.db`, 标记 fast。

# 白话: 这两处以前都是"先把响应存进缓存, 再去归档留证据"——如果归档半路
# 炸了, 坏响应已经永久存进缓存了, 以后每次都直接读这条坏缓存、再也没机会
# 重试。现在改成"先归档, 归档成功才存缓存"; 同时新增一道"内容像不像样"
# 的把关, 空的/解析不出来的响应不准存进缓存。
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# 注入 news_process 父目录, 解析 ``news_process.*`` (与既有测试一致习惯)
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.panel import llm_peer_iv as lpi  # noqa: E402
from news_process.scripts.migrate import v7_wz_audit as v7a  # noqa: E402

pytestmark = pytest.mark.fast


# ============================================================================
# 共用 fake aiohttp 对象 (镜像 test_omni_fix_llm_peer.py 的合成风格,
# 不依赖真实网络/真实 aiohttp.ClientSession)
# ============================================================================

class _FakeResponse:
    """伪 aiohttp 响应: 支持 `async with session.post(...) as resp:` 用法。"""

    def __init__(self, status: int, json_data: dict):
        self.status = status
        self._json_data = json_data

    async def json(self):
        return self._json_data

    async def text(self):
        return json.dumps(self._json_data, ensure_ascii=False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    """伪 aiohttp session: `.post(...)` 直接返回可 `async with` 的响应对象
    (与真实 aiohttp 一致 —— session.post() 本身不 await)。"""

    def __init__(self, response: _FakeResponse):
        self._response = response

    def post(self, *args, **kwargs):
        return self._response


class _StubCache:
    """伪 LLMCache: get() 返回预设值 (None=强制走在线分支), put() 用
    MagicMock 记录调用次数/参数, 不触碰真实 SQLite。"""

    def __init__(self, get_return=None):
        self._get_return = get_return
        self.put = MagicMock()

    def get(self, *a, **k):
        return self._get_return


# ============================================================================
# (a) S7 — archive-first 顺序 gate (镜像 tone_llms omni-g-tonellms-04)
# ============================================================================

class TestS7ArchiveOrderGate:
    _MODEL_CFG = {'model_name': 'stub-model', 'api_key': 'k', 'base_url': 'http://x'}

    def _run(self, monkeypatch, archive_mock, content: str):
        monkeypatch.setattr(lpi, 'LLM_OFFLINE', False)
        monkeypatch.setattr(lpi, '_LLM_ARCHIVE_AVAILABLE', True)
        monkeypatch.setattr(lpi, '_llm_archive_record', archive_mock)

        resp = _FakeResponse(200, {
            'choices': [{'message': {'content': content}}],
            'model': 'stub-model-2026',
        })
        session = _FakeSession(resp)
        cache = _StubCache(get_return=None)
        semaphore = asyncio.Semaphore(1)

        bank, year, result = asyncio.run(lpi._call_llm_peer(
            session, semaphore, '中国工商银行', 2018, ['句子。'],
            self._MODEL_CFG, cache))
        return bank, year, result, cache

    def test_archive_failure_skips_put(self, monkeypatch):
        """archive 抛异常 → cache.put 绝不能被调用 (核心修复点: 消除
        "先 put 后 archive 异常 → 坏响应永久锚死"的窗口)。"""
        archive_mock = MagicMock(side_effect=RuntimeError('archive 网络炸了'))
        bank, year, result, cache = self._run(
            monkeypatch, archive_mock, '{"peers": ["中国建设银行"]}')

        assert archive_mock.called, 'archive 应先于 put 被尝试调用'
        assert cache.put.call_count == 0, 'archive 失败后 put 不应被调用'
        # 本次调用仍应把响应内容返回给上层 (不阻塞 pipeline)
        assert result == '{"peers": ["中国建设银行"]}'
        assert (bank, year) == ('中国工商银行', 2018)

    def test_archive_success_then_put(self, monkeypatch):
        """archive 成功 → cache.put 正常被调用一次 (正常路径零漂移)。"""
        archive_mock = MagicMock()  # 无异常 = 归档成功
        bank, year, result, cache = self._run(
            monkeypatch, archive_mock, '{"peers": ["中国建设银行"]}')

        assert archive_mock.called
        assert cache.put.call_count == 1
        put_kwargs = cache.put.call_args
        # put(model_id, prompt, result, prompt_version=..., temperature=..., random_seed=...)
        assert put_kwargs.args[0] == 'stub-model'
        assert put_kwargs.args[2] == '{"peers": ["中国建设银行"]}'
        assert result == '{"peers": ["中国建设银行"]}'


# ============================================================================
# (a-cont) S7 — 本通道自带写入闸 _is_cacheable_peer_response
# ============================================================================

class TestS7CacheableGate:
    _MODEL_CFG = {'model_name': 'stub-model', 'api_key': 'k', 'base_url': 'http://x'}

    def test_gate_function_exists_and_keyed_on_peers(self):
        assert hasattr(lpi, '_is_cacheable_peer_response')
        assert lpi._PEER_VERIFICATION_KEY == 'peers'

    def test_empty_string_not_cacheable(self):
        assert lpi._is_cacheable_peer_response('') is False
        assert lpi._is_cacheable_peer_response('   ') is False
        assert lpi._is_cacheable_peer_response(None) is False

    def test_missing_peers_key_not_cacheable(self):
        assert lpi._is_cacheable_peer_response(
            '{"other_field": 1}', force_json=True) is False

    def test_unparseable_json_not_cacheable(self):
        assert lpi._is_cacheable_peer_response(
            'not a json at all', force_json=True) is False

    def test_valid_peers_payload_cacheable(self):
        assert lpi._is_cacheable_peer_response(
            '{"peers": ["中国建设银行"]}', force_json=True) is True

    def test_empty_peers_list_still_cacheable(self):
        """{"peers": []} = 已查证但零同行 (omni-g-llm-peer-07 既有语义),
        不应被本闸误伤为不合格。"""
        assert lpi._is_cacheable_peer_response(
            '{"peers": []}', force_json=True) is True

    def test_end_to_end_noncacheable_response_skips_put(self, monkeypatch):
        """全链路: 200 响应缺 "peers" 键 → archive 不尝试、put 不调用。"""
        monkeypatch.setattr(lpi, 'LLM_OFFLINE', False)
        monkeypatch.setattr(lpi, '_LLM_ARCHIVE_AVAILABLE', True)
        archive_mock = MagicMock()
        monkeypatch.setattr(lpi, '_llm_archive_record', archive_mock)

        resp = _FakeResponse(200, {
            'choices': [{'message': {'content': '{"unexpected": true}'}}],
            'model': 'stub-model-2026',
        })
        session = _FakeSession(resp)
        cache = _StubCache(get_return=None)
        semaphore = asyncio.Semaphore(1)

        bank, year, result = asyncio.run(lpi._call_llm_peer(
            session, semaphore, '中国工商银行', 2018, ['句子。'],
            self._MODEL_CFG, cache))

        assert archive_mock.call_count == 0, '不可缓存响应不应触发归档'
        assert cache.put.call_count == 0, '不可缓存响应不应写入缓存'
        # 响应内容仍原样返回给调用方 (不新增重试逻辑, 与计划范围一致)
        assert result == '{"unexpected": true}'


# ============================================================================
# (b) S8 — v7_wz_audit.call_llm_with_cache 写入闸
#      (直接 import 复用 tone_llms._is_cacheable_llm_response)
# ============================================================================

class TestS8CacheGate:
    def test_reuses_tone_llms_gate_directly(self):
        """S8 决策记录: 复用而非本地重实现 —— 同一 prompt_template/契约。"""
        from news_process.pipeline.sentiment.tone_llms import (
            _is_cacheable_llm_response as _tone_gate,
        )
        assert v7a._is_cacheable_llm_response is _tone_gate

    def test_noncacheable_response_skips_put(self, monkeypatch):
        """构造按 _is_cacheable_llm_response 判负的样例 (缺
        is_bank_fintech_news 验证键) → cache.put 不被调用。"""
        monkeypatch.setenv('YUNWU_API_KEY', 'stub-key-for-mock')
        monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)

        resp = _FakeResponse(200, {
            'choices': [{'message': {'content': '{"sentiment_reason": "x"}'}}],
        })
        session = _FakeSession(resp)
        cache = _StubCache(get_return=None)  # 强制走在线分支

        text, hit = asyncio.run(
            v7a.call_llm_with_cache(session, cache, 'dummy prompt'))

        assert hit is False
        assert cache.put.call_count == 0, '缺验证键的响应不应写入生产缓存'
        # 本次报告仍可消费原始文本 (不阻塞 audit, 只防污染缓存)
        assert text == '{"sentiment_reason": "x"}'

    def test_cacheable_response_still_puts(self, monkeypatch):
        """正控: 合格响应 (含验证键) 仍正常写入缓存 —— 新增的闸不应
        误伤合法响应。"""
        monkeypatch.setenv('YUNWU_API_KEY', 'stub-key-for-mock')
        monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)

        resp = _FakeResponse(200, {
            'choices': [{'message': {
                'content': '{"is_bank_fintech_news": true, "sentiment_reason": "x"}'
            }}],
        })
        session = _FakeSession(resp)
        cache = _StubCache(get_return=None)

        text, hit = asyncio.run(
            v7a.call_llm_with_cache(session, cache, 'dummy prompt'))

        assert hit is False
        assert cache.put.call_count == 1


# ============================================================================
# (c) S8 — 源码断言: docstring 弃用声明在位
# ============================================================================

class TestS8DeprecationNotice:
    def test_docstring_contains_deprecation_keywords(self):
        src = Path(v7a.__file__).read_text(encoding='utf-8')
        assert '仅对 v8 语料/缓存有效' in src
        assert 'checkout' in src
        assert 'v9' in src

    def test_docstring_names_v9_upgrade_plan_pointer(self):
        """预先兑现 §11.4-#15: 声明须指向 v9 升级流程, 不能只说"以后会变"。"""
        src = Path(v7a.__file__).read_text(encoding='utf-8')
        assert '11.4-#15' in src

    def test_dead_fallback_annotated(self):
        """死 fallback 'v7-2026-05-14' 保留字面量 (防误删), 但须有旁注说明
        其实际不可达。"""
        src = Path(v7a.__file__).read_text(encoding='utf-8')
        assert "'v7-2026-05-14'" in src
        assert '死 fallback' in src
