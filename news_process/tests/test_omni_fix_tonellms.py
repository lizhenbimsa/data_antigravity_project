"""OMNI 2026-06-11 g-tonellms 组缺陷修复回归锁 (防静默 revert)。

覆盖 (裁决准绳, 全部 action=fixed-deferred-disk):
- g-tonellms-01/08: 解析失败/缺键响应 → 模型缺席 (不投 False 票, 不计 n_valid_votes)
- g-tonellms-02:    HTTP 200 空串/不可解析响应不写缓存 (_is_cacheable_llm_response)
- g-tonellms-03:    _strip_prepended_title 非精确逆 — 行为冻结 + 披露锁
- g-tonellms-04:    archive append 先于 cache.put; 归档失败跳过 put; __init__ 覆盖披露
- g-tonellms-05:    manifest prompt_sha256 sidecar 绝对路径解析 (env override)
- g-tonellms-06:    LLM 禁用分支 schema 补 avg_collab 双列 + 占位 NaN (源码锁)
- g-tonellms-07/11: compute_prob_score NaN/越界 confidence → P3_INV 拒绝
- g-tonellms-09:    创新三维度 verified 门控 (模型级 if v: + 文章级 final_v gate)
- g-tonellms-10:    locus 零证据回退 None (_resolve_locus_track, 与 subst/collab 对称)
- g-tonellms-12:    逐模型 prob_score 缺席 default (NaN, 'MISSING') (源码锁)
- g-tonellms-13:    行级创新置信度聚合域与标签域对齐 (_avg_innovation_confidence)
- g-tonellms-15:    缓存层冻结空串在读取侧按模型缺席处理 (勿动缓存库本体)

⚠ 本组严禁改 prompt 构造/缓存键 — iter_article_track_prompts 行为不变,
  测试不触发任何真实 API/网络/缓存库写入。

# 白话: 三个 LLM 投票判断文章情感, 这组测试守住投票的公平性: 某个模型返回
# 的 JSON 是坏的/空的, 就当它"没来投票", 不能算成一张"反对票"去稀释一致率;
# 坏响应也绝不能写进缓存(缓存是可复现性的命根子); 置信度是 NaN 或超出 0~1
# 的怪值一律拒收, 不能当满分; 没被验证为金融科技新闻的文章, 它的创新维度
# 标签不算数; 标题拼接的剥离逻辑已字节级冻结, 谁也不许"好心修复"——动了
# 缓存键就要重新花钱跑 LLM。
"""
from __future__ import annotations

import asyncio
import inspect
import json
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

# 注入项目父目录, 让 ``news_process.*`` 在任意 cwd 解析 (仓约定)
_HERE = Path(__file__).resolve()
_PROJECT_PARENT = _HERE.parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.sentiment import tone_llms as T  # noqa: E402

# ────────────────────────────────────────────────────────────────────────────
# 共用 fixtures / helpers
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def models():
    return [
        {"short_name": "gpt54nano", "model_name": "gpt-5.4-nano"},
        {"short_name": "gemini31111", "model_name": "gemini-3.1-flash-lite-preview"},
        {"short_name": "deepseekv4", "model_name": "deepseek-v4-flash"},
    ]


def _resp(verified=True, sentiment="正面", locus=None, subst=None, collab=None,
          topic=None, locus_conf=0.0, subst_conf=0.0, collab_conf=0.0) -> str:
    """构造 v8 schema 响应 JSON (创新三维度可选)。"""
    d = {
        "is_bank_fintech_news": verified,
        "sentiment": sentiment,
        "verification_confidence": 0.9,
        "sentiment_confidence": 0.85,
        "fintech_topic": topic,
        "innovation_locus": locus,
        "innovation_locus_confidence": locus_conf,
        "innovation_substantiveness": subst,
        "innovation_substantiveness_confidence": subst_conf,
        "innovation_collab_mode": collab,
        "innovation_collab_mode_confidence": collab_conf,
    }
    return json.dumps(d, ensure_ascii=False)


# 18-tuple 索引 (见 _aggregate_track docstring)
IDX = dict(final_v=0, final_s=1, agree_rate_v=2, agree_rate_s=3,
           n_valid_votes=4, n_verifying_votes=5, call_failure=6, undefined=7,
           per_model_parsed=8, topics=9, innov_loci=10, innov_substs=11,
           n_failures=12, avg_prob_score=13, avg_subst_prob_score=14,
           avg_locus_prob_score=15, innov_collab_modes=16,
           avg_collab_prob_score=17)


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-01/08: 解析失败/缺键 → 模型缺席 (兑现 parse_json_response 契约)
# ────────────────────────────────────────────────────────────────────────────

class TestParseFailureIsModelAbsence:

    def test_truncated_json_counts_as_absence_not_false_vote(self, models):
        """截断 JSON (盘上 deepseekv4 8 例同型) → verified=None, 不入 v_votes。

        旧行为: jd={} 走正常分支 → v=False 拒绝票 + verified=False →
        n_valid_votes=3 / agree_rate_v=0.667; 新行为: n_valid=2 / agree=1.0。
        """
        truncated = '{"is_bank_fintech_news": true, "sentiment": "正'  # 中途截断
        res = {
            "gpt-5.4-nano": _resp(True, "正面"),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": truncated,
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['final_v']] is True
        assert out[IDX['n_valid_votes']] == 2, "解析失败不得计入 n_valid_votes"
        assert out[IDX['agree_rate_v']] == pytest.approx(1.0), \
            "解析失败不得稀释 agree_rate_v (旧值 0.667 污染 encode ×agreement 衰减 + HC 子样本)"
        assert out[IDX['n_failures']] == 1
        parsed = out[IDX['per_model_parsed']]
        assert parsed["deepseekv4_verified"] is None, \
            "解析失败应与 call-failure 同口径 verified=None (非 False)"
        assert parsed["deepseekv4_sentiment"] is None

    def test_parseable_but_missing_verification_key_is_absence(self, models):
        """可解析但缺 is_bank_fintech_news 键 → 同样按模型缺席处理。"""
        missing_key = json.dumps({"sentiment": "正面"}, ensure_ascii=False)
        res = {
            "gpt-5.4-nano": _resp(True, "正面"),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": missing_key,
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['n_valid_votes']] == 2
        assert out[IDX['n_failures']] == 1
        assert out[IDX['per_model_parsed']]["deepseekv4_verified"] is None

    def test_final_v_flip_regression_parse_failure_plus_call_failure(self, models):
        """审计核心场景: [True 票, call-failure, 解析失败]。

        旧行为 v_votes=[True, False] → 1 不超过 2/2=1.0 → final_v=False (翻转,
        改变样本构成); 新行为 v_votes=[True] → final_v=True。
        """
        res = {
            "gpt-5.4-nano": _resp(True, "正面"),
            "gemini-3.1-flash-lite-preview": None,           # call-failure
            "deepseek-v4-flash": '{"broken": ',               # parse-failure
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['final_v']] is True, \
            "解析失败 False 票与 call-failure 叠加曾翻转 final_v — 回归锁"
        assert out[IDX['n_valid_votes']] == 1
        assert out[IDX['n_failures']] == 2

    def test_genuine_false_vote_still_counts(self, models):
        """对照: 真实 'is_bank_fintech_news': false 仍是有效拒绝票 (勿过度修)。"""
        res = {
            "gpt-5.4-nano": _resp(False, "中性"),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": _resp(True, "正面"),
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['n_valid_votes']] == 3
        assert out[IDX['n_failures']] == 0
        assert out[IDX['per_model_parsed']]["gpt54nano_verified"] is False


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-15: 缓存层历史冻结的空串在读取侧按缺席处理 (勿动缓存库)
# ────────────────────────────────────────────────────────────────────────────

class TestFrozenEmptyStringReadSide:

    @pytest.mark.parametrize("frozen", ["", "   ", "\n\t"])
    def test_empty_or_whitespace_response_is_absence(self, models, frozen):
        """盘上 idx 982 ctx×deepseekv4 空串已冻结 → 读取侧与 None 同路径。"""
        res = {
            "gpt-5.4-nano": _resp(True, "正面"),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": frozen,
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['n_valid_votes']] == 2
        assert out[IDX['n_failures']] == 1
        assert out[IDX['per_model_parsed']]["deepseekv4_verified"] is None


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-02: 200 成功路径写缓存前内容校验 (write-side guard)
# ────────────────────────────────────────────────────────────────────────────

class TestCacheableResponseGuard:

    @pytest.mark.parametrize("bad", ["", "   ", "\n", None, 123])
    def test_empty_or_nonstr_not_cacheable(self, bad):
        assert T._is_cacheable_llm_response(bad, force_json=False) is False

    def test_truncated_json_not_cacheable_under_force_json(self):
        assert T._is_cacheable_llm_response(
            '{"is_bank_fintech_news": tru', force_json=True) is False

    def test_valid_json_cacheable(self):
        assert T._is_cacheable_llm_response(_resp(), force_json=True) is True

    def test_markdown_wrapped_json_cacheable(self):
        wrapped = "```json\n" + _resp() + "\n```"
        assert T._is_cacheable_llm_response(wrapped, force_json=True) is True

    def test_garbage_text_cacheable_when_force_json_off(self):
        """force_json=False 时仅要求非空 (历史宽松语义保留)。"""
        assert T._is_cacheable_llm_response("plain text", force_json=False) is True


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-02/04/15: fetch_llm_async 200 分支集成 (mock aiohttp, 零网络)
# ────────────────────────────────────────────────────────────────────────────

class _FakeResp:
    def __init__(self, content):
        self.status = 200
        self._content = content

    async def json(self):
        return {"choices": [{"message": {"content": self._content}}],
                "model": "fake-model-v1"}

    async def text(self):
        return ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def __init__(self, content):
        self._content = content

    def post(self, *a, **kw):
        return _FakeResp(self._content)


class _RecordingCache:
    """假缓存: get 恒 miss, put 记录调用顺序到共享 ledger。"""

    def __init__(self, ledger):
        self.ledger = ledger

    def get(self, *a, **kw):
        return None

    def put(self, *a, **kw):
        self.ledger.append("put")


def _run_fetch(monkeypatch, content, archive_raises=False):
    """同步驱动 fetch_llm_async (本机无 pytest-asyncio, 用 asyncio.run)。"""
    ledger = []
    monkeypatch.setattr(T, "LLM_OFFLINE", False)
    monkeypatch.setattr(T, "_LLM_ARCHIVE_AVAILABLE", True)

    def _fake_archive_record(**kw):
        if archive_raises:
            raise RuntimeError("simulated archive failure")
        ledger.append("archive")

    monkeypatch.setattr(T, "_llm_archive_record", _fake_archive_record)
    cache = _RecordingCache(ledger)

    async def _go():
        sem = asyncio.Semaphore(1)
        session = _FakeSession(content)
        return await T.fetch_llm_async(
            session, sem, "test prompt",
            {"model_name": "fake-model", "short_name": "fake",
             "base_url": "http://invalid.localhost", "api_key": "x"},
            row_idx=0, track="full", cache=cache, max_retries=1,
            prompt_version="test-v0",
        )

    result = asyncio.run(_go())
    return result, ledger


def test_g04_archive_append_before_cache_put(monkeypatch):
    """fix(omni-g-tonellms-04): 归档先于 cache.put, 消除一次性永久漏档窗口。"""
    result, ledger = _run_fetch(monkeypatch, _resp())
    assert result[2] == _resp(), "正常 200 响应应原样返回"
    assert ledger == ["archive", "put"], \
        f"顺序必须 archive→put (实际 {ledger}); put 在前则归档异常时响应被永久缓存漏档"


def test_g04_archive_failure_skips_cache_put_but_returns_response(monkeypatch):
    """归档失败 → 不写缓存 (下次 run 重调+重试归档), 本次投票仍用该响应。"""
    result, ledger = _run_fetch(monkeypatch, _resp(), archive_raises=True)
    assert result[2] == _resp(), "归档失败不阻塞 pipeline, 响应仍返回"
    assert "put" not in ledger, "归档失败时绝不 cache.put (防永久漏档)"


def test_g02_empty_200_response_never_cached(monkeypatch):
    """200 但 completion 空串 → 按可重试失败处理, 不 cache.put 不归档。"""
    result, ledger = _run_fetch(monkeypatch, "")
    assert result[2] is None, "空响应耗尽重试后应返回 None (模型缺席)"
    assert ledger == [], "空串绝不写入确定性锚点 (盘上 idx 982 同型故障)"


def test_g02_truncated_200_response_never_cached(monkeypatch):
    """200 但 JSON 截断 (FORCE_JSON 下可解析性校验失败) → 不缓存。"""
    monkeypatch.setattr(T, "FORCE_JSON", True)
    result, ledger = _run_fetch(monkeypatch, '{"is_bank_fintech_news": tr')
    assert result[2] is None
    assert ledger == []


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-07/11: compute_prob_score 无效 confidence 域 → P3_INV 拒绝
# ────────────────────────────────────────────────────────────────────────────

class TestProbScoreInvalidConfidenceDomain:

    @pytest.mark.parametrize("bad_conf", [float('nan'), 95, 5.0, 1.5, -0.5, "nan"])
    def test_invalid_domain_rejected_p3_inv(self, bad_conf):
        """NaN/越界/百分制误报 → 全 NaN + P3_INV (镜像 binary 版 NaN-reject)。"""
        r = T.compute_prob_score("正面", bad_conf)
        assert r["prob_source"] == "P3_INV"
        assert math.isnan(r["prob_score"]), \
            f"conf={bad_conf!r} 旧行为静默编码为满置信 ±1.0 — 回归锁"
        assert math.isnan(r["prob_pos"]) and math.isnan(r["prob_neg"])

    @pytest.mark.parametrize("falsy", [0.0, None, 0])
    def test_falsy_missing_keeps_p3_onehot(self, falsy):
        """falsy 缺失保持历史 P3 one-hot 语义 (生产 caller 默认 0.0, 盘上兼容)。"""
        r = T.compute_prob_score("负面", falsy)
        assert r["prob_source"] == "P3"
        assert r["prob_score"] == -1.0

    def test_valid_p2_path_unchanged(self):
        r = T.compute_prob_score("正面", 0.8)
        assert r["prob_source"] == "P2"
        assert r["prob_score"] == pytest.approx(0.8 - 0.1)
        assert (r["prob_pos"] + r["prob_neu"] + r["prob_neg"]) == pytest.approx(1.0)

    def test_policy_aligned_with_binary_version(self):
        """同一无效输入, 3-class 与 binary 政策一致: 双双拒绝为 NaN。"""
        r3 = T.compute_prob_score("正面", 5.0)
        rb = T.compute_prob_score_binary("实质性", 5.0, "象征性")
        assert math.isnan(r3["prob_score"]) and math.isnan(rb["prob_score"])

    def test_p3_inv_score_excluded_from_track_aggregation(self, models):
        """P3_INV 的 NaN 分数不得进入 avg_prob_score 聚合 (isnan 守卫)。"""
        bad = json.loads(_resp(True, "正面"))
        bad["sentiment_confidence"] = 95  # 百分制误报 → P3_INV
        good = json.loads(_resp(True, "正面"))
        good["sentiment_confidence"] = 0.8
        res = {
            "gpt-5.4-nano": json.dumps(bad, ensure_ascii=False),
            "gemini-3.1-flash-lite-preview": json.dumps(good, ensure_ascii=False),
            "deepseek-v4-flash": json.dumps(good, ensure_ascii=False),
        }
        out = T._aggregate_track(res, models)
        avg = out[IDX['avg_prob_score']]
        assert not math.isnan(avg), "有效模型分数仍应聚合"
        assert avg == pytest.approx(0.7), \
            "P3_INV NaN 不得入均值 (两个 0.8-conf 正面 → 0.7); 旧行为满置信 1.0 抬高均值"


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-09: 创新三维度 verified 门控 (模型级 + 文章级)
# ────────────────────────────────────────────────────────────────────────────

class TestInnovationVerifiedGating:

    def test_model_level_gate_unverified_labels_not_voted(self, models):
        """verified=False 模型 emit 标签 (违反 prompt 软约束) → 不入维度票。"""
        res = {
            "gpt-5.4-nano": _resp(False, "中性", locus="底层技术", subst="实质性",
                                  collab="外部协同", locus_conf=0.9,
                                  subst_conf=0.9, collab_conf=0.9),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": _resp(True, "正面"),
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['final_v']] is True
        assert out[IDX['innov_loci']] == [], "未验证模型的 locus 标签不得入票"
        assert out[IDX['innov_substs']] == []
        assert out[IDX['innov_collab_modes']] == []
        # per-model 存档列不门控 (审计保留原始输出)
        parsed = out[IDX['per_model_parsed']]
        assert parsed["gpt54nano_innovation_locus"] == "底层技术"
        assert parsed["gpt54nano_innovation_substantiveness"] == "实质性"
        assert parsed["gpt54nano_innovation_collab_mode"] == "外部协同"

    def test_model_level_gate_binary_prob_scores_verified_only(self, models):
        """未验证模型的三维度 binary prob_score 不入聚合均值。"""
        res = {
            "gpt-5.4-nano": _resp(False, "中性", subst="象征性", subst_conf=0.9),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": _resp(True, "正面"),
        }
        out = T._aggregate_track(res, models)
        assert math.isnan(out[IDX['avg_subst_prob_score']]), \
            "仅未验证模型有 subst 标签 → 聚合应 NaN (verified-only 收紧)"

    def test_verified_model_labels_still_vote(self, models):
        """对照: verified=True 模型标签正常入票/聚合 (勿过度修)。"""
        res = {
            "gpt-5.4-nano": _resp(True, "正面", locus="底层技术", subst="实质性",
                                  collab="自主研发", locus_conf=0.8,
                                  subst_conf=0.8, collab_conf=0.8),
            "gemini-3.1-flash-lite-preview": _resp(True, "正面"),
            "deepseek-v4-flash": _resp(True, "正面"),
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['innov_loci']] == ["底层技术"]
        assert out[IDX['innov_substs']] == ["实质性"]
        assert out[IDX['innov_collab_modes']] == ["自主研发"]
        assert not math.isnan(out[IDX['avg_subst_prob_score']])
        assert not math.isnan(out[IDX['avg_locus_prob_score']])
        assert not math.isnan(out[IDX['avg_collab_prob_score']])

    def test_article_level_gate_final_v_false_clears_labels_and_scores(self, models):
        """整文 ensemble 判非 fintech → 三维度标签票清空 + 连续分数 NaN。

        盘上实证: ctx 轨 62 个 llm_verified=False 行 62/62 带 locus 标签 —
        本 gate 镜像 final_s=None (PROBGATE-1) 的标签层对应物。
        """
        res = {
            "gpt-5.4-nano": _resp(False, "中性", locus="应用场景", subst="象征性",
                                  collab="外部协同", topic="数字人民币",
                                  locus_conf=0.9, subst_conf=0.9, collab_conf=0.9),
            "gemini-3.1-flash-lite-preview": _resp(False, "中性", locus="应用场景"),
            "deepseek-v4-flash": _resp(False, "中性"),
        }
        out = T._aggregate_track(res, models)
        assert out[IDX['final_v']] is False
        assert out[IDX['topics']] == []
        assert out[IDX['innov_loci']] == []
        assert out[IDX['innov_substs']] == []
        assert out[IDX['innov_collab_modes']] == []
        assert math.isnan(out[IDX['avg_subst_prob_score']])
        assert math.isnan(out[IDX['avg_locus_prob_score']])
        assert math.isnan(out[IDX['avg_collab_prob_score']])


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-10: locus 零证据回退 None (与 subst/collab empty_fallback 对称)
# ────────────────────────────────────────────────────────────────────────────

class TestResolveLocusTrackZeroEvidence:

    def test_zero_evidence_returns_none(self):
        """LLM 零票 + 零关键词证据 → (None, 0.0), 不再硬默认 '应用场景'。

        盘上实证: null=0/857 而 subst/collab 分别 234/295 null; ctx 轨 62
        未验证行 60 获标签其中 30 个零置信 — 回归锁。
        """
        assert T._resolve_locus_track([], []) == (None, 0.0)

    def test_zero_votes_empty_topic_string_returns_none(self):
        """topics 全空串 → canonicalize_topic 基率默认 (conf=0) → None。"""
        label, conf = T._resolve_locus_track([], [''])
        assert label is None and conf == 0.0

    def test_keyword_backed_fallback_retained(self):
        """LLM 零票但 keyword 有真实证据 (conf>0) → keyword 回退保留。"""
        label, conf = T._resolve_locus_track([], ['区块链 人工智能'])
        assert label == '底层技术'
        assert conf > 0

    def test_voted_path_unchanged(self):
        """有 LLM 票时多数决 + 交叉验证 boost/penalty 行为不变。"""
        # 多数 底层技术, keyword 无证据 (kw_cat=应用场景@0.0) → 分歧 penalty 0.0
        assert T._resolve_locus_track(['底层技术', '底层技术', '应用场景'], []) \
            == ('底层技术', 0.0)
        # 多数 应用场景 与零证据 kw_cat 同名 → boost 0+0.2 (历史行为冻结)
        assert T._resolve_locus_track(['应用场景', '应用场景'], []) \
            == ('应用场景', pytest.approx(0.2))

    def test_tie_default_retained(self):
        """平局 tie_default='应用场景' 保留 (有票的 MAP 是另一回事)。"""
        label, _ = T._resolve_locus_track(['底层技术', '应用场景'], [])
        assert label == '应用场景'


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-13: 行级创新置信度聚合域与标签域对齐
# ────────────────────────────────────────────────────────────────────────────

class TestAvgInnovationConfidenceDomain:

    MODELS2 = [{"short_name": "a"}, {"short_name": "b"}]

    def test_null_label_confidence_excluded(self):
        """标签 None (被拒/null) 的模型置信度不入均值 (盘上 subst full=7/ctx=13 同型)。"""
        parsed = {
            "a_innovation_substantiveness": "实质性",
            "a_innovation_substantiveness_confidence": 0.8,
            "b_innovation_substantiveness": None,        # 标签 null 却 emit 置信度
            "b_innovation_substantiveness_confidence": 0.9,
        }
        avg = T._avg_innovation_confidence(parsed, "innovation_substantiveness", self.MODELS2)
        assert avg == pytest.approx(0.8), "标签 null 的 0.9 不得入均值"

    def test_all_null_labels_returns_zero(self):
        parsed = {
            "a_innovation_locus": None, "a_innovation_locus_confidence": 0.7,
            "b_innovation_locus": None, "b_innovation_locus_confidence": 0.6,
        }
        assert T._avg_innovation_confidence(parsed, "innovation_locus", self.MODELS2) == 0.0

    def test_normal_mean_over_labeled_models(self):
        parsed = {
            "a_innovation_collab_mode": "自主研发",
            "a_innovation_collab_mode_confidence": 0.6,
            "b_innovation_collab_mode": "外部协同",
            "b_innovation_collab_mode_confidence": 0.8,
        }
        avg = T._avg_innovation_confidence(parsed, "innovation_collab_mode", self.MODELS2)
        assert avg == pytest.approx(0.7)

    def test_zero_confidence_labeled_model_excluded_from_denominator(self):
        """conf<=0 项继续被剔除 (历史 valid 过滤语义保留)。"""
        parsed = {
            "a_innovation_locus": "底层技术", "a_innovation_locus_confidence": 0.0,
            "b_innovation_locus": "底层技术", "b_innovation_locus_confidence": 0.5,
        }
        assert T._avg_innovation_confidence(parsed, "innovation_locus", self.MODELS2) \
            == pytest.approx(0.5)

    def test_main_wires_module_level_function(self):
        """main() 必须调用模块级 _avg_innovation_confidence (防 revert 回内联无门控版)。"""
        src = inspect.getsource(T.main)
        assert "_avg_innovation_confidence(" in src
        assert "def _avg_conf" not in src, "内联无门控闭包不得复活"


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-14: stage 21 备援物化与 stage 13 语义对齐 (prepend + content_full)
# ────────────────────────────────────────────────────────────────────────────

class TestFallbackMaterializationSemantics:

    def _df(self):
        return pd.DataFrame({
            '内容': ['银行推出数字钱包业务。市场反应积极。', '另一篇正文。'],
            '标题': ['银行新闻标题', None],          # 第二行: 缺失标题
            'target_bank': ['', ''],                  # 空 target → fallback 路径
        })

    def test_produces_content_full_and_prepends_title(self):
        from news_process.core.text.entity_context import prepend_title
        df = T._materialize_content_ctx(self._df())
        assert 'content_full' in df.columns, \
            "备援路径必须产 content_full (双路径同名同语义列不变量)"
        body0 = '银行推出数字钱包业务。市场反应积极。'
        assert df.loc[0, 'content_full'] == prepend_title('银行新闻标题', body0)
        assert df.loc[0, 'content_full'].startswith('银行新闻标题')
        assert df.loc[0, 'content_ctx'] == df.loc[0, 'content_full'], \
            "fallback 行 ctx 应等于 full (均含标题)"

    def test_missing_title_treated_as_empty(self):
        df = T._materialize_content_ctx(self._df())
        assert df.loc[1, 'content_full'] == '另一篇正文。', \
            "标题 NaN → 按空标题处理, 不得出现 'nan' 字符串前缀"
        assert df.loc[1, 'content_ctx'] == '另一篇正文。'

    def test_ctx_is_fallback_compares_bodies_not_titled_text(self):
        """关键回归: 注入标题后 fallback 判定必须比较去标题 body。

        旧判定 content_ctx == 内容 在加 prepend 后恒 False → fallback 统计归零。
        """
        df = T._materialize_content_ctx(self._df())
        assert bool(df.loc[0, 'ctx_is_fallback']) is True
        assert bool(df.loc[1, 'ctx_is_fallback']) is True

    def test_prompt_construction_invariant_after_fallback_materialization(self):
        """⚠ 缓存键铁律: 备援物化改动后, iter_article_track_prompts 产出的
        prompt 与 stage 13 路径逐字一致 (剥标题后 ctx body 不含标题)。"""
        df = T._materialize_content_ctx(self._df())
        prompts = list(T.iter_article_track_prompts(df))
        # row0 full 轨: content = 原始 内容 (不剥离)
        idx0_full = [p for p in prompts if p[0] == 0 and p[1] == 'full'][0]
        assert '银行推出数字钱包业务' in idx0_full[2]
        # row0 ctx 轨: content_ctx 剥标题后不得再含标题前缀双注入
        idx0_ctx = [p for p in prompts if p[0] == 0 and p[1] == 'ctx'][0]
        assert idx0_ctx[2].count('银行新闻标题') == 1, \
            "ctx prompt 标题仅 {title} 字段 1 次 (剥离 content_ctx 前缀)"


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-03: _strip_prepended_title 非精确逆 — 行为冻结 + 披露锁
# ────────────────────────────────────────────────────────────────────────────

class TestStripPrependedTitleDisclosure:

    def test_normal_roundtrip(self):
        from news_process.core.text.entity_context import prepend_title
        body = '正文第一句。第二句。'
        title = '某银行标题'
        assert T._strip_prepended_title(prepend_title(title, body), title) == body

    def test_textual_prefix_strip_behavior_frozen(self):
        """body 本身以 title 开头 (prepend 跳过拼接) 时仍剥前缀 — 非精确逆,
        但行为已字节级冻结 (缓存键铁律), 锁定现状防"好心修复"破坏缓存命中。"""
        title = '银行公告'
        body = '银行公告今日发布。后续内容。'
        stripped = T._strip_prepended_title(body, title)
        assert stripped == '今日发布。后续内容。', \
            "剥离按文本前缀 (冻结行为); 改动此处会让 ctx prompt 漂移 → 缓存 miss"

    def test_docstrings_disclose_non_exact_inverse(self):
        assert 'omni-g-tonellms-03' in (T._strip_prepended_title.__doc__ or '')
        src = inspect.getsource(T.iter_article_track_prompts)
        assert 'omni-g-tonellms-03' in src, "0.6% full 轨双注入披露不得删除"


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-06/12: main() 内联修复源码锁 (禁用分支 schema + 缺席 default)
# ────────────────────────────────────────────────────────────────────────────

class TestMainInlineFixesSourceLock:

    def test_g06_disabled_branch_has_collab_columns_and_nan_placeholders(self):
        src = inspect.getsource(T.main)
        assert "df[f'avg_collab_prob_score{track}'] = _np.nan" in src, \
            "禁用分支必须补 avg_collab_prob_score 双列 (三配置态 schema 等价)"
        assert "df[f'llm_prob_score{track}'] = _np.nan" in src, \
            "禁用分支 llm_prob_score 占位必须 NaN (0.0 与合法中性不可区分)"
        assert "df[f'llm_prob_score{track}'] = 0.0" not in src

    def test_g12_per_model_archive_defaults_nan_missing(self):
        src = inspect.getsource(T.main)
        for track in ("full", "ctx"):
            assert f"parsed_{track}.get(f\"{{short}}_prob_score\", float('nan'))" in src, \
                f"{track} 轨缺席模型 prob_score default 必须 NaN (失败≠中性)"
            assert f"parsed_{track}.get(f\"{{short}}_prob_source\", 'MISSING')" in src
            assert f"parsed_{track}.get(f\"{{short}}_prob_score\", 0.0)" not in src
            assert f"parsed_{track}.get(f\"{{short}}_prob_source\", 'P3')" not in src


# ────────────────────────────────────────────────────────────────────────────
# g-tonellms-04/05: llm_archive 披露 + sidecar 绝对路径
# ────────────────────────────────────────────────────────────────────────────

class TestLlmArchiveFixes:

    def test_g04_init_docstring_discloses_coverage_gap(self):
        import news_process.pipeline.llm_archive as A
        doc = A.__doc__ or ''
        assert 'omni-g-tonellms-04' in doc
        assert 'backfill' in doc, "必须承认 cache→archive backfill 缺失"

    def test_g05_sidecar_env_override_and_absolute(self, tmp_path, monkeypatch):
        from news_process.pipeline.llm_archive import manifest as M
        target = tmp_path / 'sidecar.json'
        monkeypatch.setenv('LLM_ARCHIVE_SIDECAR_PATH', str(target))
        resolved = M._resolve_sidecar_path()
        assert resolved == target.resolve()
        assert resolved.is_absolute()

    def test_g05_config_resolution_is_absolute(self, monkeypatch):
        """无 env override 时经 config 解析为绝对路径 (cwd-漂移免疫)。"""
        from news_process.pipeline.llm_archive import manifest as M
        monkeypatch.delenv('LLM_ARCHIVE_SIDECAR_PATH', raising=False)
        resolved = M._resolve_sidecar_path()
        # config 可用 → 绝对路径; 仅 config 完全不可用才回落相对 (单测兜底)
        assert resolved.name.endswith('v3_5_1_constants.json')
        assert resolved.is_absolute(), \
            "config 在位时 sidecar 必须绝对路径 (audit S3 同源原则)"

    def test_g05_sidecar_happy_path_reads_sha(self, tmp_path, monkeypatch):
        from news_process.pipeline.llm_archive import manifest as M
        sha = 'b' * 64
        sidecar = tmp_path / 'v3_5_1_constants.json'
        sidecar.write_text(json.dumps({'prompt_v8_sha256': sha}), encoding='utf-8')
        monkeypatch.setenv('LLM_ARCHIVE_SIDECAR_PATH', str(sidecar))
        assert M._read_prompt_sha256_from_sidecar() == sha
