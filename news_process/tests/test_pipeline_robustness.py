import os
import sys
from unittest.mock import patch

import numpy as np
import pytest

# Phase 5c-2: 注入项目父目录解析 ``news_process.*``
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache

# Phase 2a: 15's body migrated to news_process.pipeline.filtering.policy_alignment.
# The legacy importlib.spec_from_file_location("15_article_policy_alignment.py")
# loaded the (now shim) root file and expected its body symbols.
# Updated to import the canonical body directly.
from news_process.pipeline.filtering import policy_alignment as mod15  # noqa: E402


@pytest.fixture(autouse=True)
def _mock_embedding_config(monkeypatch):
    """CI 上无 .env / 真实 LLM key, 注入 mock EMBEDDING_CONFIG 让通过 config 校验.

    `mod15._get_embeddings_api_dynamic` (policy_alignment.py L264-265) 在调 API 前
    会校验 `EMBEDDING_CONFIG.base_url / api_key`, 缺失即 raise RuntimeError.
    本 fixture 注入 sentinel mock 值, 让 config 校验放行; 真实网络请求由各 test
    内的 `aiohttp.ClientSession.post` mock 拦截 (避免任何 outbound network).
    """
    monkeypatch.setattr(
        mod15, "EMBEDDING_CONFIG",
        {"base_url": "https://mock.invalid", "api_key": "mock-key-ci-only",
         "model": "text-embedding-3-small"},
        raising=False,
    )

def test_cache_put_batch(tmp_path):
    """
    测试 LLMCache 的批量写入和读取功能。
    验证点：
    1. 批量写入的数据能被正确且完整地读取。
    2. 未写入的数据返回 None。
    3. cache 内部记录的 size 正确。
    使用 pytest 的 tmp_path 确保测试用例间环境隔离，避免由于断言失败导致测试数据库未清理的隐患。
    """
    db_path = str(tmp_path / "test_cache_batch.db")
    
    with LLMCache(db_path) as cache:
        cache.put_batch("model-x", ["p1", "p2"], ["r1", "r2"])
        assert cache.get("model-x", "p1") == "r1", "缓存 p1 命中失败或值不匹配"
        assert cache.get("model-x", "p2") == "r2", "缓存 p2 命中失败或值不匹配"
        assert cache.get("model-x", "p3") is None, "缓存 p3 应为空"
        assert cache.size() == 2, f"缓存大小应该为 2，实际为 {cache.size()}"

    print(f"[OK] test_cache_put_batch passed (DB: {db_path})")


def test_cache_key_includes_prompt_version(tmp_path):
    """Plan-r3 P3-17: 缓存键必须包含 prompt_version 维度.

    旧版仅 (model_id, prompt) 时, 改写 prompts/sentiment_cot.txt 后旧
    cache 仍命中错答案 (silent staleness). 新版加 prompt_version, 改一行
    prompt → cache miss → 重新调 API.
    """
    db_path = str(tmp_path / "test_cache_pv.db")
    with LLMCache(db_path) as cache:
        cache.put("m1", "prompt-A", "resp-v6", prompt_version="v6-2026-05-09")
        # 同 (model, prompt) 但不同 prompt_version → 不应命中
        assert cache.get("m1", "prompt-A", prompt_version="v6-2026-05-09") == "resp-v6"
        assert cache.get("m1", "prompt-A", prompt_version="v7-2026-06-01") is None
        # 不传 prompt_version (默认 v0) 也不应命中 v6
        assert cache.get("m1", "prompt-A") is None


def test_cache_key_includes_temperature(tmp_path):
    """Plan-r3 P3-17: 缓存键必须包含 temperature 维度.

    temperature=0.0 与 temperature=0.5 的 LLM 响应分布不同, 共用 cache
    会污染. 新版让两种 temperature 命中各自命名空间.
    """
    db_path = str(tmp_path / "test_cache_temp.db")
    with LLMCache(db_path) as cache:
        cache.put("m1", "prompt-A", "resp-det", temperature=0.0)
        cache.put("m1", "prompt-A", "resp-stoch", temperature=0.5)
        assert cache.get("m1", "prompt-A", temperature=0.0) == "resp-det"
        assert cache.get("m1", "prompt-A", temperature=0.5) == "resp-stoch"
        # 默认 temperature=0.0 命中 deterministic
        assert cache.get("m1", "prompt-A") == "resp-det"


def test_cache_temperature_precision_no_collision(tmp_path):
    """Plan-r3 P3-17 recode 审查: temperature 浮点精度边界.

    历史 bug: f"{temp:.4f}" 让 1e-30 与 0.0 都格式化为 "0.0000" → 键碰撞.
    修复后改用 repr(float(temp)) 保证 shortest unambiguous representation.
    """
    db_path = str(tmp_path / "test_cache_temp_precision.db")
    with LLMCache(db_path) as cache:
        cache.put("m1", "p1", "resp_zero", temperature=0.0)
        # 1e-30 必须与 0.0 区分 (repr('0.0') != repr('1e-30'))
        result = cache.get("m1", "p1", temperature=1e-30)
        assert result is None, (
            f"temperature=1e-30 不应命中 temperature=0.0 的命名空间 "
            f"(实际命中: {result!r}). 修复已用 repr(float()) 替换 .4f."
        )

        cache.put("m1", "p2", "resp_low", temperature=0.05)
        # 0.05 与 0.0500001 在 repr 下不同
        assert cache.get("m1", "p2", temperature=0.05) == "resp_low"
        assert cache.get("m1", "p2", temperature=0.0500001) is None


def test_cache_key_seed_dimension_backward_compatible_at_temp_zero():
    """audit S2 修复: random_seed 仅在 temperature != 0.0 时进键。

    关键不变量 (零缓存失效): temperature=0.0 (贪心解码) 下 seed 对输出无影响,
    故带 seed 与不带 seed 的 key 必须字节级一致 — 这保证现存 _llm_cache.db
    (332MB, 历史无 seed 维度) 在本次修复后仍全部命中, 无需 bump SCHEMA_VERSION
    / 重跑 stage 21。
    """
    k_no_seed = LLMCache._make_key("m1", "p1", prompt_version="v8", temperature=0.0)
    k_seed42 = LLMCache._make_key("m1", "p1", prompt_version="v8",
                                  temperature=0.0, random_seed=42)
    k_seed99 = LLMCache._make_key("m1", "p1", prompt_version="v8",
                                  temperature=0.0, random_seed=99)
    # temp=0.0: seed 不进键 → 三者完全相同 (向后兼容历史 P3-17 schema)
    assert k_no_seed == k_seed42 == k_seed99


def test_cache_key_seed_matters_at_nonzero_temperature():
    """audit S2 修复: temperature>0 时 seed 决定采样路径, 必须进键。

    防止温度/种子稳健性扫描在 temp>0 下静默命中按错误 seed 算出的旧响应。
    """
    base = LLMCache._make_key("m1", "p1", prompt_version="v8", temperature=0.7)
    seed42 = LLMCache._make_key("m1", "p1", prompt_version="v8",
                                temperature=0.7, random_seed=42)
    seed99 = LLMCache._make_key("m1", "p1", prompt_version="v8",
                                temperature=0.7, random_seed=99)
    # temp>0 且传 seed: 不同 seed → 不同键; 且与"不传 seed"也不同
    assert seed42 != seed99
    assert base != seed42
    assert base != seed99


def test_cache_get_put_seed_roundtrip_at_nonzero_temp(tmp_path):
    """audit S2 修复: get/put 透传 random_seed, temp>0 下不同 seed 各自命名空间。"""
    db_path = str(tmp_path / "test_cache_seed.db")
    with LLMCache(db_path) as cache:
        cache.put("m1", "pA", "resp-s42", temperature=0.7, random_seed=42)
        cache.put("m1", "pA", "resp-s99", temperature=0.7, random_seed=99)
        assert cache.get("m1", "pA", temperature=0.7, random_seed=42) == "resp-s42"
        assert cache.get("m1", "pA", temperature=0.7, random_seed=99) == "resp-s99"


def test_cache_pipe_in_prompt_version_no_collision(tmp_path):
    """Plan-r3 P3-17 recode 审查: prompt_version 含 '|' 字符不引发键碰撞.

    我加的键格式用 '|' 作分隔, 若 prompt_version 含 '|' 必须靠长度前缀
    防碰撞. 验证: ('m', 'p', pv='a|b') vs ('m', 'p', pv='a|c') 必须不同.
    """
    db_path = str(tmp_path / "test_cache_pipe.db")
    with LLMCache(db_path) as cache:
        cache.put("m1", "p1", "resp_ab", prompt_version="a|b")
        cache.put("m1", "p1", "resp_ac", prompt_version="a|c")
        assert cache.get("m1", "p1", prompt_version="a|b") == "resp_ab"
        assert cache.get("m1", "p1", prompt_version="a|c") == "resp_ac"


def test_cache_none_vs_empty_string_no_collision(tmp_path):
    """final recode F2 + round-3 review R8: None 与空字符串必须哈希到不同键 (接口契约).

    旧实现 ``str(x) if x is not None else ""`` 让 None ≡ "" 共用 namespace.
    用 ASCII 哨兵 ``'<<NULL_SENTINEL>>'`` 区分 (round-3 review R8 替换原
    null byte 哨兵, 避免 sqlite/终端跨版本边角问题).
    生产 code path 不会传 None (yaml 配置必有值), 但作为公开 API 接口必须严格.
    """
    db_path = str(tmp_path / "test_cache_none.db")
    with LLMCache(db_path) as cache:
        cache.put(None, "p1", "resp_none_model")
        cache.put("", "p1", "resp_empty_model")
        # 两次 put 应建立两条独立记录, 不互相覆盖
        assert cache.get(None, "p1") == "resp_none_model"
        assert cache.get("", "p1") == "resp_empty_model"
        # 总条目数 = 2 (而非 1)
        assert cache.size() == 2

        # prompt 维度的 None vs "" 同样区分
        cache.put("m1", None, "resp_none_prompt")
        cache.put("m1", "", "resp_empty_prompt")
        assert cache.get("m1", None) == "resp_none_prompt"
        assert cache.get("m1", "") == "resp_empty_prompt"


def test_cache_sentinel_known_limitation_with_literal_input(tmp_path):
    """round-3 review R8: 文档化已知 trade-off — 当用户字面量传入与 ``_NONE_SENTINEL``
    完全相同的字符串时, 与 ``None`` 输入会产生键碰撞.

    设计原因: ``_NONE_SENTINEL = '<<NULL_SENTINEL>>'`` (ASCII) 让两者哈希到
    同一 raw 字符串, 经长度前缀编码后键相同. 这是从 ``\\x00`` 哨兵换 ASCII
    哨兵 (避免 sqlite/终端跨版本边角) 的代价.

    生产保护: yaml 配置永远不传该字面量 (model_id 是 'gpt-5-nano-...' 等
    标准字符串); prompts/*.txt 也不会含 ``'<<NULL_SENTINEL>>'`` 这种 ASCII
    字符串. 因此 known limitation 不影响任何生产 code path.

    本测试 assert ``size == 1`` (碰撞) 而非 ``== 2``, 显式守护这是当前
    实现的 *预期行为*. 任何后续重构若把该 test 改成 ``size == 2`` (区分
    了字面量与 None), 应同步 v3.0 升级 SCHEMA_VERSION.
    """
    from news_process.core.caching import _NONE_SENTINEL
    db_path = str(tmp_path / "test_cache_sentinel_limitation.db")
    with LLMCache(db_path) as cache:
        cache.put(None, "p1", "resp_real_none")
        cache.put(_NONE_SENTINEL, "p1", "resp_literal_sentinel")
        # 已知 limitation: 后 put 静默覆盖前 put
        assert cache.size() == 1, (
            f"None vs 字面量哨兵 size={cache.size()} != 1; "
            "实现已变更, 请同步 SCHEMA_VERSION 与本 test 文档."
        )
        # 后 put 的值胜出 (INSERT OR REPLACE 语义)
        assert cache.get(None, "p1") == "resp_literal_sentinel"
        assert cache.get(_NONE_SENTINEL, "p1") == "resp_literal_sentinel"


def test_cache_v0_fallback_priority_when_v1_exists(tmp_path):
    """final recode F3: v1 cache 与 v0 cache 同时存在时, get 必须优先 v1.

    避免"新代码升级后 cache 仍命中旧 v0 响应"的 silent staleness 反向风险.
    """
    db_path = str(tmp_path / "test_cache_v0_v1_coexist.db")
    with LLMCache(db_path) as cache:
        v0_key = LLMCache._make_key_v0("m1", "p1")
        import time
        # 手动插入 v0
        cache._conn.execute(
            "INSERT INTO llm_cache (cache_key, model_id, response, created_at) "
            "VALUES (?, ?, ?, ?)",
            (v0_key, "m1", "OLD_v0_response", time.time())
        )
        cache._conn.commit()
        # 然后用新代码 put v1
        cache.put("m1", "p1", "NEW_v1_response")

        # 默认 get 必须命中 v1, 不应回退 v0 (v1 优先)
        result = cache.get("m1", "p1")
        assert result == "NEW_v1_response", (
            f"v1+v0 共存时 fallback 优先级颠倒: "
            f"应返回 NEW_v1_response, 实际 {result!r}"
        )


def test_cache_v0_fallback_only_on_default_params(tmp_path):
    """Plan-r3 P3-17 recode 审查: v0 fallback 仅在 (pv='v0', temp=0.0) 触发.

    确保用户传入新 prompt_version 或非默认 temperature 时, 不会误命中
    历史 v0 命名空间 (silent staleness 防御的核心契约).
    """
    db_path = str(tmp_path / "test_cache_v0_fallback.db")
    with LLMCache(db_path) as cache:
        # 手动插入 v0 cache 模拟历史
        v0_key = LLMCache._make_key_v0("m1", "p1")
        import time
        cache._conn.execute(
            "INSERT INTO llm_cache (cache_key, model_id, response, created_at) "
            "VALUES (?, ?, ?, ?)",
            (v0_key, "m1", "v0_legacy", time.time())
        )
        cache._conn.commit()

        # 默认参数 → 应 fallback 命中
        assert cache.get("m1", "p1") == "v0_legacy"

        # 非默认 temperature → 不应 fallback
        assert cache.get("m1", "p1", temperature=0.5) is None

        # 非默认 prompt_version → 不应 fallback
        assert cache.get("m1", "p1", prompt_version="v6_2026") is None

        # v0 fallback 命中后, v1 cache 不应被自动写入 (避免污染)
        v1_key = LLMCache._make_key("m1", "p1")
        cur = cache._conn.execute(
            "SELECT COUNT(*) FROM llm_cache WHERE cache_key = ?", (v1_key,)
        )
        assert cur.fetchone()[0] == 0, "v0 fallback 不应自动 put v1 (避免污染)"


def test_cache_schema_version_invalidates_v0_keys(tmp_path):
    """Plan-r3 P3-17: SCHEMA_VERSION 升级 ('v0' -> 'v1') 让历史 cache 自动 silent miss.

    本测试通过对比 v1 schema 下 _make_key 与手写 v0 schema 哈希的差异,
    验证 SCHEMA_VERSION 确实参与键的哈希 (任何 v0 旧记录的 cache_key 都不会
    匹配 v1 算法生成的新键, 即等效 silent miss).
    """
    import hashlib

    from news_process.core.caching import SCHEMA_VERSION, LLMCache

    assert SCHEMA_VERSION == "v1", \
        f"SCHEMA_VERSION 当前值 '{SCHEMA_VERSION}' 不是 Plan-r3 P3-17 的 'v1'"

    # 模拟 v0 算法手算键
    m_id, prompt = "m1", "prompt-A"
    v0_raw = f"{len(m_id)}:{m_id}:{prompt}"
    v0_key = hashlib.sha256(v0_raw.encode('utf-8')).hexdigest()

    # 当前 (v1) 算法生成的键
    v1_key = LLMCache._make_key(m_id, prompt)

    assert v0_key != v1_key, (
        "v0 旧键与 v1 新键相同 — SCHEMA_VERSION 未参与哈希? "
        "Plan-r3 P3-17 升级失败."
    )

class MockResponse:
    def __init__(self, status, json_data=None, text_data=""):
        self.status = status
        self._json = json_data
        self._text = text_data

    async def json(self):
        return self._json

    async def text(self):
        return self._text
        
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_get_embeddings_api_dynamic_success(tmp_path):
    """
    测试 LLM API 调用的缓存穿透与命中逻辑（模拟成功响应）。
    验证点：
    1. 首次调用 API 时，应发起真实网络请求并存入缓存。
    2. 再次调用时，应直接命中缓存，不再发起网络请求。
    """
    db_path = str(tmp_path / "test_cache_success.db")
        
    texts = ["hello", "world"]
    token_counts = [1, 1]
    
    # 模拟成功的返回值
    mock_json = {
        "data": [
            {"index": 0, "embedding": [0.1, 0.2]},
            {"index": 1, "embedding": [0.3, 0.4]}
        ]
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value = MockResponse(200, json_data=mock_json)
        
        with LLMCache(db_path) as cache:
            # 第一次调用，预期走 API
            embs = await mod15._get_embeddings_api_dynamic(texts, token_counts, cache)
            assert embs.shape == (2, 2), "返回的 embedding 形状不正确"
            assert np.allclose(embs[0], [0.1, 0.2]), "解析的 embedding 数值不匹配"
            assert mock_post.call_count == 1, "应该发起 1 次网络请求"
            
            # 第二次调用，预期命中缓存，走 Cache
            embs2 = await mod15._get_embeddings_api_dynamic(texts, token_counts, cache)
            assert embs2.shape == (2, 2), "缓存返回的 embedding 形状不正确"
            assert np.allclose(embs2[0], [0.1, 0.2]), "缓存返回的 embedding 数值不匹配"
            assert mock_post.call_count == 1, "命中缓存时不应发起新请求"

    print(f"[OK] test_get_embeddings_api_dynamic_success passed (DB: {db_path})")

@pytest.mark.asyncio
async def test_get_embeddings_api_dynamic_retry():
    """
    测试 LLM API 调用的异常重试机制。
    验证点：
    1. 遇到网络异常（如 429 Too Many Requests）时，代码应能捕获并进行重试。
    2. 重试达到预期次数后若成功，则返回正确结果；验证请求次数是否符合预期。
    """
    texts = ["retry_test"]
    token_counts = [2]
    
    mod15.RETRY_DELAY = 0.1 # 缩短测试重试等待时间
    
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return MockResponse(429, text_data="Too many requests")
        else:
            return MockResponse(200, json_data={"data": [{"index": 0, "embedding": [0.99]}]})
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.side_effect = side_effect
        embs = await mod15._get_embeddings_api_dynamic(texts, token_counts, cache=None)
        assert embs.shape == (1, 1), "重试成功后返回的形状不正确"
        assert np.allclose(embs[0], [0.99]), "重试成功后返回的数据不正确"
        assert call_count == 3, f"应该重试并成功在第 3 次调用，实际调用了 {call_count} 次"
        
    print("[OK] test_get_embeddings_api_dynamic_retry passed")

