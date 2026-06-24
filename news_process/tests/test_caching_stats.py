"""tests/test_caching_stats.py — T0.0a LLMCache hit/miss 计数器。

验证 T0.0a 新增的运行时 stats 计数器, 使未来回归 (如删掉某计数器、
破坏锁作用域、重复计数) 先被快速单测拦截, 而不是等 LLM stage
打出误导性指标后才发现。
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


# ────────────────────────────────────────────────────────────────────────────
# delete() — 读取侧自愈坏缓存条目 (2026-06-23)
# ────────────────────────────────────────────────────────────────────────────

def test_delete_v1_entry_evicts_and_reports_count(tmp_path):
    """put 后 delete 同 key -> 条目被删, get 返回 None, 删除计数=1."""
    db_path = str(tmp_path / "del_v1.db")
    with LLMCache(db_path) as cache:
        cache.put("m", "p1", "bad resp", prompt_version="v6", temperature=0.0)
        removed = cache.delete("m", "p1", prompt_version="v6", temperature=0.0)
        after = cache.get("m", "p1", prompt_version="v6", temperature=0.0)
    assert removed == 1
    assert after is None


def test_delete_miss_returns_zero(tmp_path):
    """删除不存在的条目 -> 返回 0, 不报错."""
    db_path = str(tmp_path / "del_miss.db")
    with LLMCache(db_path) as cache:
        removed = cache.delete("m", "nope", prompt_version="v6", temperature=0.0)
    assert removed == 0


def test_delete_v0_fallback_entry(tmp_path):
    """默认参数 (v0/0.0) 下 delete 一并清除 v0 旧 schema 键, 防 fallback 再命中."""
    db_path = str(tmp_path / "del_v0.db")
    with LLMCache(db_path) as cache:
        import time
        v0_key = LLMCache._make_key_v0("m", "legacy")
        with cache._lock:
            cache._conn.execute(
                "INSERT INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (v0_key, "m", "legacy bad", time.time())
            )
            cache._conn.commit()
        # 默认参数 get 走 v0 fallback 命中
        assert cache.get("m", "legacy") == "legacy bad"
        removed = cache.delete("m", "legacy")  # 默认 v0/0.0 → 删 v1+v0
        after = cache.get("m", "legacy")
    assert removed == 1, "应删除 v0 fallback 条目"
    assert after is None, "删除后 v0 fallback 不再命中"


def test_delete_evicts_both_v1_and_v0(tmp_path):
    """同 (model, prompt) 同时存在 v1 + v0 条目时, 默认参数 delete 两者全清 (返回 2)."""
    db_path = str(tmp_path / "del_both.db")
    with LLMCache(db_path) as cache:
        import time
        # v1 条目 (默认 v0/0.0 → put 走 v1 算法)
        cache.put("m", "dup", "v1 bad")
        # v0 条目直接写
        v0_key = LLMCache._make_key_v0("m", "dup")
        with cache._lock:
            cache._conn.execute(
                "INSERT INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (v0_key, "m", "v0 bad", time.time())
            )
            cache._conn.commit()
        removed = cache.delete("m", "dup")
    assert removed == 2, "应同时删除 v1 与 v0 两条"
