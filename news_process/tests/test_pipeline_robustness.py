import os
import sys
import numpy as np
import pytest
from unittest.mock import patch

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


def test_cache_schema_version_invalidates_v0_keys(tmp_path):
    """Plan-r3 P3-17: SCHEMA_VERSION 升级 ('v0' -> 'v1') 让历史 cache 自动 silent miss.

    本测试通过对比 v1 schema 下 _make_key 与手写 v0 schema 哈希的差异,
    验证 SCHEMA_VERSION 确实参与键的哈希 (任何 v0 旧记录的 cache_key 都不会
    匹配 v1 算法生成的新键, 即等效 silent miss).
    """
    import hashlib
    from news_process.core.caching import LLMCache, SCHEMA_VERSION

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

