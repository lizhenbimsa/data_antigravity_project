"""tests/test_sentiment_tie_retry.py — 用户决策 2026-06-24 平局/空票重试单测.

覆盖 stage 21 的新行为: verified 轨情感**平局/空票**在 _aggregate_track 保守
降级'中性'**之前**, 先对该 (行×轨) 的 3 个模型票**绕过缓存**重新调实时 API
最多 SENTIMENT_TIE_RETRY_ROUNDS 轮 (默认 80, 温度=0), 试图打破平局/补齐缺票;
仍未决再交保守降级。新票回写缓存 (确定性锚点)。**并发结构** (用户决策 2026-06-24,
第三轮回退第二轮的"各轨独立协程"): **逐轮全局 barrier + 每轮内并发** —— 每一轮
把当前全部待决 (行×轨) × 模型票一次性铺开并发, 本轮全部跑完才统一重判、进下一轮;
某轨被打破即从下一轮 pending 剔除 (不再重复重调)。

校验点:
1. ``_verified_sentiment_unresolved`` 口径 = 「final_v=True 且情感平局/空票」:
   - 三方完全分歧 (正面/中性/负面) 全 verified → True (平局);
   - verified 但无任一可解析情感票 (空票) → True;
   - 清晰多数 → False; 非金科 (final_v=False, Case B) → False。
2. ``fetch_llm_async(force_refresh=True)`` **跳过缓存读取**强制实时 API, 但
   写入侧仍 ``cache.put`` 回写覆盖旧条目 (用 mock session 验证)。
3. ``_resolve_unresolved_sentiment_tracks`` 对平局轨逐轮重试, 一旦解析即剔除出
   下一轮 pending, 并把新票写回 results_map + cache; 非待决轨不被触碰。
4. **逐轮 barrier**: 某轨某轮被打破后, 后续轮次不再重调它 (从 pending 剔除),
   故已解析轨不会白跑后续轮; results_map 各轨键互斥无写冲突。
5. 离线确定性模式 (LLM_OFFLINE) 下重试被调用方守卫跳过 (本测试验证守卫语义)。
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

_HERE = Path(__file__).resolve()
_PROJECT_PARENT = _HERE.parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.core.caching import LLMCache  # noqa: E402
from news_process.pipeline.sentiment import tone_llms  # noqa: E402


def _resp(verified: bool, sentiment, ver_conf: float = 0.9, sent_conf: float = 0.85) -> str:
    payload = {
        "is_bank_fintech_news": verified,
        "verification_confidence": ver_conf,
        "innovation_locus": "应用场景",
        "innovation_locus_confidence": 0.9,
        "innovation_substantiveness": "实质性",
        "innovation_substantiveness_confidence": 0.85,
    }
    if sentiment is not None:
        payload["sentiment"] = sentiment
        payload["sentiment_confidence"] = sent_conf
    return json.dumps(payload, ensure_ascii=False)


@pytest.fixture
def models():
    return [
        {"short_name": "gpt54nano", "model_name": "gpt-5.4-nano",
         "base_url": "http://invalid.localhost", "api_key": "k"},
        {"short_name": "gemini31", "model_name": "gemini-3.1-flash-lite-preview",
         "base_url": "http://invalid.localhost", "api_key": "k"},
        {"short_name": "deepseekv4", "model_name": "deepseek-v4-flash",
         "base_url": "http://invalid.localhost", "api_key": "k"},
    ]


def _res_dict(models, sentiments, verified=(True, True, True)):
    """构造 {model_name: raw_json} (sentiments[i]=None ⇒ 该模型不给可解析情感票)."""
    return {
        m["model_name"]: _resp(verified[i], sentiments[i])
        for i, m in enumerate(models)
    }


# ── 1. 谓词口径 ────────────────────────────────────────────────────────────

def test_unresolved_true_on_three_way_tie(models):
    """三方完全分歧 (正面/中性/负面) 全 verified → 平局 → True."""
    d = _res_dict(models, ["正面", "中性", "负面"])
    assert tone_llms._verified_sentiment_unresolved(d, models) is True


def test_unresolved_true_on_empty_sentiment(models):
    """verified 但无任一可解析情感票 (空票) → True."""
    d = _res_dict(models, [None, None, None])
    assert tone_llms._verified_sentiment_unresolved(d, models) is True


def test_unresolved_false_on_clear_majority(models):
    """清晰多数 (2 正面 1 负面) → 非平局 → False."""
    d = _res_dict(models, ["正面", "正面", "负面"])
    assert tone_llms._verified_sentiment_unresolved(d, models) is False


def test_unresolved_false_when_not_fintech(models):
    """整篇被多数判非金科 (final_v=False, Case B) → 情感 N/A → False (不触发重试).

    即便情感票本身平局, 只要 final_v=False 就不重试 (用户决策范围限 verified 轨)。
    """
    d = _res_dict(models, ["正面", "中性", "负面"], verified=(False, False, False))
    assert tone_llms._verified_sentiment_unresolved(d, models) is False


def test_unresolved_two_way_verified_tie(models):
    """两 verified 模型情感平局 (正面/负面), 第三非 verified → True (verified-only 门控)."""
    d = {
        models[0]["model_name"]: _resp(True, "正面"),
        models[1]["model_name"]: _resp(True, "负面"),
        models[2]["model_name"]: _resp(False, "中性"),  # 非 verified, 情感不计入
    }
    assert tone_llms._verified_sentiment_unresolved(d, models) is True


# ── 2. force_refresh 绕过读取 + 回写 ───────────────────────────────────────

class _FakeResp:
    def __init__(self, payload):
        self.status = 200
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self):
        return self._payload

    async def text(self):
        return json.dumps(self._payload)


def _fake_session(content_text):
    """返回一个 session, 其 .post 始终回 200 + 指定 message.content."""
    session = MagicMock()
    payload = {"choices": [{"message": {"content": content_text}}], "model": "x"}
    session.post = MagicMock(return_value=_FakeResp(payload))
    return session


def test_force_refresh_skips_cache_read_but_writes_back(tmp_path, monkeypatch):
    """force_refresh=True: 即便缓存已有旧票也不读, 走实时 API; 新票回写覆盖."""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    cache = LLMCache(str(tmp_path / "c.db"))
    cfg = {"model_name": "m1", "short_name": "m1",
           "base_url": "http://x", "api_key": "k"}
    prompt = "P"
    old = _resp(True, "正面")
    new = _resp(True, "负面")
    # 预置旧票
    cache.put(cfg["model_name"], prompt, old,
              prompt_version=tone_llms.PROMPT_VERSION,
              temperature=tone_llms.TEMPERATURE, random_seed=tone_llms.RANDOM_SEED)
    session = _fake_session(new)
    try:
        out = asyncio.run(tone_llms.fetch_llm_async(
            session, asyncio.Semaphore(1), prompt, cfg, 0, "full",
            cache=cache, prompt_version=tone_llms.PROMPT_VERSION,
            force_refresh=True,
        ))
        # 走了实时 API → 返回 new (而非缓存里的 old)
        assert out == (0, "m1", new, "full")
        session.post.assert_called()  # 确实打了 API (没短路命中缓存)
        # 回写覆盖: 缓存现为 new
        cached = cache.get(cfg["model_name"], prompt,
                           prompt_version=tone_llms.PROMPT_VERSION,
                           temperature=tone_llms.TEMPERATURE,
                           random_seed=tone_llms.RANDOM_SEED)
        assert cached == new
    finally:
        cache.close()


def test_no_force_refresh_hits_cache(tmp_path, monkeypatch):
    """对照: force_refresh=False (默认) 仍命中缓存短路, 不打 API."""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    cache = LLMCache(str(tmp_path / "c.db"))
    cfg = {"model_name": "m1", "short_name": "m1",
           "base_url": "http://x", "api_key": "k"}
    prompt = "P"
    good = _resp(True, "正面")
    cache.put(cfg["model_name"], prompt, good,
              prompt_version=tone_llms.PROMPT_VERSION,
              temperature=tone_llms.TEMPERATURE, random_seed=tone_llms.RANDOM_SEED)
    session = _fake_session(_resp(True, "负面"))
    try:
        out = asyncio.run(tone_llms.fetch_llm_async(
            session, asyncio.Semaphore(1), prompt, cfg, 0, "full",
            cache=cache, prompt_version=tone_llms.PROMPT_VERSION,
        ))
        assert out == (0, "m1", good, "full")  # 命中缓存
        session.post.assert_not_called()        # 没打 API
    finally:
        cache.close()


# ── 3. 重试编排: 平局 → 重试打破 → 停止 ────────────────────────────────────

def _df(n=1):
    rows = [{
        "内容": f"招商银行上线区块链{i}。", "content_ctx": f"招商银行区块链窗口{i}。",
        "content_ss": f"招商银行金科同句{i}。", "标题": f"招行科技{i}",
        "target_bank": "招商银行", "co_mentioned_banks": "无",
    } for i in range(n)]
    return pd.DataFrame(rows)


def test_resolver_breaks_tie_and_stops(monkeypatch, models):
    """平局轨重试后变清晰多数 → 移出待决 + 新票写回 results_map; 第二轮不再调它."""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    monkeypatch.setattr(tone_llms, "MODELS", models, raising=False)
    monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_RETRY_ROUNDS", 5)

    df = _df(1)
    # 首跑: full 轨平局 (正面/中性/负面); ctx/ss 清晰多数 (不待决)
    results_map = {
        0: {
            "full": _res_dict(models, ["正面", "中性", "负面"]),
            "ctx": _res_dict(models, ["正面", "正面", "负面"]),
            "ss": _res_dict(models, ["负面", "负面", "正面"]),
        }
    }

    calls = {"n": 0}

    async def fake_fetch(session, semaphore, prompt, m, idx, track, **kw):
        # 断言重试一定带 force_refresh
        assert kw.get("force_refresh") is True
        calls["n"] += 1
        # 重试后所有模型都投"正面" → 打破平局
        return idx, m["model_name"], _resp(True, "正面"), track

    monkeypatch.setattr(tone_llms, "fetch_llm_async", fake_fetch)

    asyncio.run(tone_llms._resolve_unresolved_sentiment_tracks(
        session=None, semaphore=asyncio.Semaphore(1), df=df, models=models,
        results_map=results_map, cache=None, request_pacers={},
        model_availability=None,
    ))

    # 只有 full 轨待决 → 第一轮 3 个模型各 1 次 = 3 次调用; 解析后停, 不进第二轮
    assert calls["n"] == 3
    # full 轨已被新票覆盖为全"正面" → 不再平局
    assert tone_llms._verified_sentiment_unresolved(results_map[0]["full"], models) is False
    # ctx/ss 未被触碰 (非待决)
    assert results_map[0]["ctx"][models[0]["model_name"]] == _resp(True, "正面")


def test_resolver_exhausts_rounds_when_persistent_tie(monkeypatch, models):
    """重试始终返回平局 → 跑满 N 轮, 保留原态交保守降级 (不抛错)."""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_RETRY_ROUNDS", 3)

    df = _df(1)
    results_map = {0: {
        "full": _res_dict(models, ["正面", "中性", "负面"]),
        "ctx": _res_dict(models, ["正面", "正面", "负面"]),
        "ss": _res_dict(models, ["正面", "正面", "负面"]),
    }}

    rounds = {"n": 0}

    async def fake_fetch(session, semaphore, prompt, m, idx, track, **kw):
        rounds["n"] += 1
        # 永远平局 (按模型顺序回 正面/中性/负面)
        i = [mm["model_name"] for mm in models].index(m["model_name"])
        return idx, m["model_name"], _resp(True, ["正面", "中性", "负面"][i]), track

    monkeypatch.setattr(tone_llms, "fetch_llm_async", fake_fetch)

    asyncio.run(tone_llms._resolve_unresolved_sentiment_tracks(
        session=None, semaphore=asyncio.Semaphore(1), df=df, models=models,
        results_map=results_map, cache=None, request_pacers={},
        model_availability=None,
    ))
    # 3 轮 × 3 模型 = 9 次 (full 轨始终待决, 跑满)
    assert rounds["n"] == 9
    # 仍平局 → 交 _aggregate_track 保守降级 (此处只验证未解析)
    assert tone_llms._verified_sentiment_unresolved(results_map[0]["full"], models) is True


def test_resolver_noop_when_rounds_zero(monkeypatch, models):
    """SENTIMENT_TIE_RETRY_ROUNDS<=0 → 直接返回, 不调 fetch (退回改前行为)."""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_RETRY_ROUNDS", 0)
    df = _df(1)
    results_map = {0: {
        "full": _res_dict(models, ["正面", "中性", "负面"]),
        "ctx": _res_dict(models, ["正面", "正面", "负面"]),
        "ss": _res_dict(models, ["正面", "正面", "负面"]),
    }}
    called = {"n": 0}

    async def fake_fetch(*a, **k):
        called["n"] += 1
        return 0, "x", "{}", "full"

    monkeypatch.setattr(tone_llms, "fetch_llm_async", fake_fetch)
    asyncio.run(tone_llms._resolve_unresolved_sentiment_tracks(
        session=None, semaphore=asyncio.Semaphore(1), df=df, models=models,
        results_map=results_map, cache=None, request_pacers={},
        model_availability=None,
    ))
    assert called["n"] == 0


# ── 4. 逐轮 barrier: 已解析轨在轮间被剔除, 不白跑后续轮 ─────────────────────

def test_resolver_drops_resolved_tracks_between_rounds(monkeypatch, models):
    """两个待决轨收敛轮数不同 (full 第 1 轮解析 / ss 第 3 轮才解析): full 被打破后
    从下一轮 pending 剔除, 不再重调 → 仅 3 次; ss 跑满 3 轮 → 9 次。

    用户决策 2026-06-24 (第三轮回退第二轮): 逐轮全局 barrier — 每轮把当前全部
    待决 (行×轨) × 模型票铺开并发, 本轮跑完才统一重判; 已解析轨剔除出下一轮。
    本测试按累计调用数验证"已解析轨不白跑后续轮" (call-count 与并发结构无关,
    barrier / per-track 两种调度下均成立, 故回退后断言不变)。"""
    monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
    monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_RETRY_ROUNDS", 10)

    df = _df(1)
    # full + ss 待决 (平局); ctx 清晰多数 (不待决)
    results_map = {0: {
        "full": _res_dict(models, ["正面", "中性", "负面"]),
        "ctx": _res_dict(models, ["正面", "正面", "负面"]),
        "ss": _res_dict(models, ["正面", "中性", "负面"]),
    }}

    # 每轨独立的累计重调计数 (一轮 = 该轨 3 个模型票各调一次)
    track_calls = {"full": 0, "ss": 0}

    async def fake_fetch(session, semaphore, prompt, m, idx, track, **kw):
        assert kw.get("force_refresh") is True
        track_calls[track] += 1
        # full 轨第 1 轮即全"正面"→解析 (随后被剔除, 不再重调);
        # ss 轨前 2 轮仍平局, 第 3 轮起全"负面"→解析。逐轮 barrier 下本轮全部
        # 跑完才重判, 故按 ss 累计调用序号 k 推所属轮号: k=1..3→轮1, 4..6→轮2,
        # 7..9→轮3 (同轮内 3 票轮号一致 → 与 as_completed 完成顺序无关)。
        if track == "full":
            sent = "正面"
        else:  # ss
            k = track_calls["ss"]
            round_no = (k - 1) // len(models) + 1
            if round_no >= 3:
                sent = "负面"
            else:
                i = [mm["model_name"] for mm in models].index(m["model_name"])
                sent = ["正面", "中性", "负面"][i]
        return idx, m["model_name"], _resp(True, sent), track

    monkeypatch.setattr(tone_llms, "fetch_llm_async", fake_fetch)
    asyncio.run(tone_llms._resolve_unresolved_sentiment_tracks(
        session=None, semaphore=asyncio.Semaphore(100), df=df, models=models,
        results_map=results_map, cache=None, request_pacers={},
        model_availability=None,
    ))

    # full 轨第 1 轮即解析 → 剔除出后续轮, 仅 1 轮 × 3 模型 = 3 次
    assert track_calls["full"] == 3
    # ss 轨第 3 轮才解析 → 3 轮 × 3 模型 = 9 次
    assert track_calls["ss"] == 9
    # 两轨均已解析 (不再平局)
    assert tone_llms._verified_sentiment_unresolved(results_map[0]["full"], models) is False
    assert tone_llms._verified_sentiment_unresolved(results_map[0]["ss"], models) is False
    # ctx 未被触碰
    assert results_map[0]["ctx"][models[1]["model_name"]] == _resp(True, "正面")
