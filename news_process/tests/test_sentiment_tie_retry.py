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


@pytest.fixture(scope='module')
def source_code():
    """tone_llms.py 源码文本 — 供源码级回退闸使用 (行为闸测不出的静默回退)。"""
    from news_process.pipeline.sentiment import tone_llms as _t
    with open(_t.__file__, 'r', encoding='utf-8') as f:
        return f.read()


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
    # fix(archive-leak, 2026-07-14): 本测试真调 fetch_llm_async 且 fake session
    # 返回 200 → 生产 append-only 归档被真实写入 (m1/'P' mock 记录曾自 2026-06-24
    # 起累计泄漏 146 条进 data/llm_archive/responses/, 已record级清洗) → 必须关
    # 归档开关 (镜像 test_omni_fix_tonellms 隔离写法), 否则每次全量 pytest 都
    # 污染归档并使 verify_manifest 翻红。
    monkeypatch.setattr(tone_llms, "_LLM_ARCHIVE_AVAILABLE", False)
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
    # fix(archive-leak, 2026-07-14): 防御性同款隔离 (本测试命中缓存不 POST 理论
    # 上不归档; 若未来行为变化走到网络分支, 归档开关兜底防泄漏)。
    monkeypatch.setattr(tone_llms, "_LLM_ARCHIVE_AVAILABLE", False)
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


# ============================================================================
# 内层重试预算解耦 (用户决策 2026-07-25) — SENTIMENT_TIE_MAX_RETRIES
# ============================================================================
# 动因: 外层 `for round_no` 循环本身就是重试机制, 内层若继承主跑段
# MAX_RETRIES=80 则两层预算相乘 (最坏 6,400 次/格); 而每轮是全局 barrier,
# 一条跑满 80 次的 "200 空响应" 病链 (~1,000s) 会把整轮拖成 ~17 分钟
# (2026-07-25 两趟生产日志实证, 外推剩余轮次 ≈ 22h)。
# 这几个 gate 防的是**静默回退**: call site 漏传 max_retries 即重新继承 80,
# 且日志/lineage 仍报 80 → 现象只在生产真跑时才暴露 (早期 T=2 试跑盘测不出;
# 本机自 2026-07-27/28 起即 T=19 生产规模, 该盲区已消失)。


class TestSentimentTieMaxRetries:

    def test_constant_clamped_to_valid_range(self):
        """常量须落在 [1, MAX_RETRIES]: 0/负数无意义, 超过主跑段违背设计意图。"""
        assert isinstance(tone_llms.SENTIMENT_TIE_MAX_RETRIES, int)
        assert 1 <= tone_llms.SENTIMENT_TIE_MAX_RETRIES <= tone_llms.MAX_RETRIES

    def test_clamp_expression_present_in_source(self, source_code):
        """clamp 必须是 max(1, min(MAX_RETRIES, cfg)) 形态 (防日后改成裸 int())。"""
        seg_start = source_code.find("SENTIMENT_TIE_MAX_RETRIES = ")
        assert seg_start != -1, "SENTIMENT_TIE_MAX_RETRIES 常量未找到"
        seg = source_code[seg_start:seg_start + 240]
        assert "max(1" in seg and "min(" in seg and "MAX_RETRIES" in seg, (
            f"clamp 表达式缺失或被改写: {seg[:160]!r}"
        )
        assert "sentiment_tie_retry_max_retries" in seg, (
            "常量未从 config 键 sentiment_tie_retry_max_retries 读取 (硬编码?)"
        )

    def test_call_site_passes_max_retries(self, source_code):
        """源码闸: 平局重试 call site 必须显式传 max_retries, 否则静默继承 80。"""
        fn_start = source_code.find("async def _resolve_unresolved_sentiment_tracks")
        assert fn_start != -1, "_resolve_unresolved_sentiment_tracks 未找到"
        fn_end = source_code.find("\ndef ", fn_start)
        body = source_code[fn_start:fn_end if fn_end != -1 else len(source_code)]
        assert "max_retries=SENTIMENT_TIE_MAX_RETRIES" in body, (
            "平局重试 fetch_llm_async 调用未显式传 max_retries=SENTIMENT_TIE_MAX_RETRIES "
            "(回退到继承主跑段 MAX_RETRIES=80 → 单轮 barrier 可被一条病链拖到 ~1000s)"
        )

    def test_resolver_forwards_max_retries_kwarg(self, monkeypatch, models):
        """行为闸: 实际调用确实带上该 kwarg 且值 = 常量 (非仅源码字面量)。"""
        monkeypatch.setattr(tone_llms, "LLM_OFFLINE", False)
        monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_RETRY_ROUNDS", 2)
        monkeypatch.setattr(tone_llms, "SENTIMENT_TIE_MAX_RETRIES", 1)

        df = _df(1)
        results_map = {0: {
            "full": _res_dict(models, ["正面", "中性", "负面"]),
            "ctx": _res_dict(models, ["正面", "正面", "负面"]),
            "ss": _res_dict(models, ["正面", "正面", "负面"]),
        }}
        seen = []

        async def fake_fetch(session, semaphore, prompt, m, idx, track, **kw):
            seen.append(kw.get("max_retries"))
            # 始终平局 → 跑满 2 轮
            i = [mm["model_name"] for mm in models].index(m["model_name"])
            return idx, m["model_name"], _resp(True, ["正面", "中性", "负面"][i]), track

        monkeypatch.setattr(tone_llms, "fetch_llm_async", fake_fetch)
        asyncio.run(tone_llms._resolve_unresolved_sentiment_tracks(
            session=None, semaphore=asyncio.Semaphore(10), df=df, models=models,
            results_map=results_map, cache=None, request_pacers={},
            model_availability=None,
        ))
        assert seen, "未发生任何重试调用"
        assert set(seen) == {1}, f"max_retries kwarg 未按常量下传: {sorted(set(seen))}"
        # 总预算 = 轮数 × 内层 (此处 2 轮 × 3 模型 = 6 次调用)
        assert len(seen) == 2 * len(models)

    def test_budget_invariant_matches_main_pass(self):
        """预算不变量: 轮数 × 内层 ≥ 主跑段每格预算 (取 1 时恰好等同, 恢复机会不减)。

        这是"砍内层不减恢复机会"论证的可执行化 —— 若日后有人下调轮数而忘了
        同步上调内层 (或反之), 该 gate 会拦住 "总预算掉到主跑段之下"。
        """
        if tone_llms.SENTIMENT_TIE_RETRY_ROUNDS <= 0:
            pytest.skip("平局重试已关闭 (rounds<=0), 预算不变量不适用")
        budget = tone_llms.SENTIMENT_TIE_RETRY_ROUNDS * tone_llms.SENTIMENT_TIE_MAX_RETRIES
        assert budget >= tone_llms.MAX_RETRIES, (
            f"平局重试总预算 {budget} < 主跑段 {tone_llms.MAX_RETRIES} "
            "— 卡住格拿到的尝试次数反而少于主跑段, 违背设计意图"
        )

    def test_lineage_and_banner_disclose_inner_budget(self, source_code):
        """披露闸: lineage 元数据 + 启动横幅都须报内层预算 (只报 80 = 披露失真)。"""
        assert '"sentiment_tie_max_retries": SENTIMENT_TIE_MAX_RETRIES' in source_code, (
            "lineage 元数据未落账 sentiment_tie_max_retries"
        )
        assert '"sentiment_tie_retry_rounds": SENTIMENT_TIE_RETRY_ROUNDS' in source_code, (
            "lineage 元数据未落账 sentiment_tie_retry_rounds"
        )
        assert "sentiment_tie_max_retries={SENTIMENT_TIE_MAX_RETRIES" in source_code, (
            "启动横幅未回显内层重试上限"
        )
