"""tests/test_caching_stats.py — T0.0a LLMCache hit/miss counters.

Verifies the runtime stats counters added by T0.0a so that future regressions
(e.g. removing a counter, breaking lock-scope, double-counting) trip a fast
unit test before the LLM stage logs misleading metrics.
"""

from __future__ import annotations

from news_process.core.caching import LLMCache


def test_stats_fresh_cache_is_zero(tmp_path):
    """新建空缓存的 stats 应全 0, hit_rate=0.0."""
    db_path = str(tmp_path / "stats_fresh.db")
    with LLMCache(db_path) as cache:
        s = cache.stats()
    assert s == {
        'hits': 0, 'v0_hits': 0, 'misses': 0,
        'writes': 0, 'lookups': 0, 'hit_rate': 0.0,
    }


def test_stats_after_miss(tmp_path):
    """空库 get -> 计入 miss, hit_rate=0."""
    db_path = str(tmp_path / "stats_miss.db")
    with LLMCache(db_path) as cache:
        result = cache.get("gpt54nano", "test prompt")
        s = cache.stats()
    assert result is None
    assert s['hits'] == 0
    assert s['v0_hits'] == 0
    assert s['misses'] == 1
    assert s['lookups'] == 1
    assert s['hit_rate'] == 0.0


def test_stats_after_put_and_hit(tmp_path):
    """put 后 get 同 key -> 计入 hit, hit_rate=1.0."""
    db_path = str(tmp_path / "stats_hit.db")
    with LLMCache(db_path) as cache:
        cache.put("gpt54nano", "test prompt", "response text",
                  prompt_version="v6", temperature=0.0)
        result = cache.get("gpt54nano", "test prompt",
                           prompt_version="v6", temperature=0.0)
        s = cache.stats()
    assert result == "response text"
    assert s['hits'] == 1
    assert s['misses'] == 0
    assert s['writes'] == 1
    assert s['hit_rate'] == 1.0


def test_stats_v0_fallback_path(tmp_path):
    """模拟旧 v0 缓存条目: 直接用 _make_key_v0 写, get(默认参数) 走 fallback 命中."""
    db_path = str(tmp_path / "stats_v0.db")
    with LLMCache(db_path) as cache:
        # 用 v0 算法的键直接写 (模拟旧版数据库)
        v0_key = LLMCache._make_key_v0("gpt54nano", "legacy prompt")
        import time
        with cache._lock:
            cache._conn.execute(
                "INSERT INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (v0_key, "gpt54nano", "legacy response", time.time())
            )
            cache._conn.commit()
        # 用默认参数 get → v1 miss → v0 fallback hit
        result = cache.get("gpt54nano", "legacy prompt")  # 默认 v0/0.0
        s = cache.stats()
    assert result == "legacy response"
    assert s['hits'] == 0
    assert s['v0_hits'] == 1
    assert s['misses'] == 0
    assert s['hit_rate'] == 1.0


def test_stats_put_batch_increments_writes(tmp_path):
    """put_batch 写入 N 条 -> writes += N (不是 1)."""
    db_path = str(tmp_path / "stats_batch.db")
    prompts = ["p1", "p2", "p3"]
    responses = ["r1", "r2", "r3"]
    with LLMCache(db_path) as cache:
        cache.put_batch("gpt54nano", prompts, responses,
                        prompt_version="v6", temperature=0.0)
        s = cache.stats()
        db_size = cache.size()
    assert s['writes'] == 3
    assert db_size == 3


def test_stats_hit_rate_mixed(tmp_path):
    """混合 hit + miss -> hit_rate = 命中数 / lookups."""
    db_path = str(tmp_path / "stats_mixed.db")
    with LLMCache(db_path) as cache:
        cache.put("m", "p1", "r1", prompt_version="v6", temperature=0.0)
        cache.get("m", "p1", prompt_version="v6", temperature=0.0)  # hit
        cache.get("m", "p2", prompt_version="v6", temperature=0.0)  # miss
        cache.get("m", "p3", prompt_version="v6", temperature=0.0)  # miss
        s = cache.stats()
    assert s['hits'] == 1
    assert s['misses'] == 2
    assert s['lookups'] == 3
    assert abs(s['hit_rate'] - 1.0 / 3) < 1e-9
