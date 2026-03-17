"""
tests/test_llm_cache.py — utils/llm_cache.py 单元测试
======================================================
"""

import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.llm_cache as llm_cache_mod


# ============================================================================
# Fixture: 隔离缓存数据库
# ============================================================================

@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """每个测试使用独立的临时 SQLite 缓存数据库。"""
    db_path = str(tmp_path / 'test_llm_cache.db')
    # 重置模块级状态
    monkeypatch.setattr(llm_cache_mod, '_cache_db_path', db_path)
    monkeypatch.setattr(llm_cache_mod, '_db_initialized', False)
    yield db_path


# ============================================================================
# 测试用例
# ============================================================================

class TestLlmCache:
    """测试 LLM 缓存模块。"""

    def test_save_and_get_cache(self):
        """写入后读取应一致。"""
        prompt = "请分析这篇新闻"
        model = "gpt-5-nano"
        response = '{"is_bank_fintech_news": true}'

        llm_cache_mod.save_to_cache(prompt, model, response)
        cached = llm_cache_mod.get_from_cache(prompt, model)

        assert cached == response

    def test_get_cache_miss(self):
        """未缓存的查询应返回 None。"""
        result = llm_cache_mod.get_from_cache("不存在的 prompt", "fake_model")
        assert result is None

    def test_hash_consistency(self):
        """相同输入应产生相同哈希。"""
        h1 = llm_cache_mod._get_hash("test prompt", "model_a")
        h2 = llm_cache_mod._get_hash("test prompt", "model_a")
        assert h1 == h2

    def test_hash_different_models(self):
        """不同模型应产生不同哈希。"""
        h1 = llm_cache_mod._get_hash("same prompt", "model_a")
        h2 = llm_cache_mod._get_hash("same prompt", "model_b")
        assert h1 != h2

    def test_hash_different_prompts(self):
        """不同 prompt 应产生不同哈希。"""
        h1 = llm_cache_mod._get_hash("prompt_1", "model_a")
        h2 = llm_cache_mod._get_hash("prompt_2", "model_a")
        assert h1 != h2

    def test_cache_overwrite(self):
        """重复写入应覆盖旧值（INSERT OR REPLACE）。"""
        prompt = "覆盖测试"
        model = "test_model"

        llm_cache_mod.save_to_cache(prompt, model, "旧值")
        llm_cache_mod.save_to_cache(prompt, model, "新值")

        cached = llm_cache_mod.get_from_cache(prompt, model)
        assert cached == "新值"

    def test_unicode_support(self):
        """应支持中文 Unicode 内容。"""
        prompt = "这是一个中文提示词 🎉"
        model = "unicode_model"
        response = '{"sentiment": "正面", "reason": "银行创新突破"}'

        llm_cache_mod.save_to_cache(prompt, model, response)
        cached = llm_cache_mod.get_from_cache(prompt, model)
        assert cached == response

    def test_empty_prompt(self):
        """空 prompt 也应正常工作。"""
        llm_cache_mod.save_to_cache("", "model", "empty response")
        cached = llm_cache_mod.get_from_cache("", "model")
        assert cached == "empty response"

    def test_hash_is_sha256(self):
        """哈希值应为 64 字符的 SHA-256 十六进制字符串。"""
        h = llm_cache_mod._get_hash("test", "model")
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)


# ============================================================================
# 增强测试：批量与压力场景
# ============================================================================

class TestLLMCacheEnhanced:
    """增强测试：批量操作和特殊字符。"""

    def test_batch_write_read_consistency(self, isolated_cache):
        """批量写入后应全部正确读取。"""
        n = 50
        for i in range(n):
            llm_cache_mod.save_to_cache(f"prompt_{i}", f"model_{i % 3}", f"response_{i}")

        for i in range(n):
            cached = llm_cache_mod.get_from_cache(f"prompt_{i}", f"model_{i % 3}")
            assert cached == f"response_{i}"

    def test_special_characters_in_prompt(self, isolated_cache):
        """提示词包含特殊字符应正常工作。"""
        special_prompts = [
            "包含\n换行符\n的提示词",
            "包含\t制表符\t的提示词",
            "包含'单引号'和\"双引号\"的提示词",
            "包含反斜杠\\和路径C:\\Users",
            "包含SQL注入'; DROP TABLE cache; --",
        ]
        for i, prompt in enumerate(special_prompts):
            llm_cache_mod.save_to_cache(prompt, "model", f"response_{i}")
            cached = llm_cache_mod.get_from_cache(prompt, "model")
            assert cached == f"response_{i}"

    def test_very_long_prompt(self, isolated_cache):
        """超长提示词应正常处理。"""
        long_prompt = "A" * 100000
        llm_cache_mod.save_to_cache(long_prompt, "model", "response")
        cached = llm_cache_mod.get_from_cache(long_prompt, "model")
        assert cached == "response"

    def test_very_long_response(self, isolated_cache):
        """超长响应应正常存储和读取。"""
        long_response = '{"data": "' + 'X' * 50000 + '"}'
        llm_cache_mod.save_to_cache("prompt", "model", long_response)
        cached = llm_cache_mod.get_from_cache("prompt", "model")
        assert cached == long_response

    def test_same_prompt_different_models_isolated(self, isolated_cache):
        """相同提示词不同模型应独立缓存。"""
        llm_cache_mod.save_to_cache("prompt", "model_a", "response_a")
        llm_cache_mod.save_to_cache("prompt", "model_b", "response_b")
        assert llm_cache_mod.get_from_cache("prompt", "model_a") == "response_a"
        assert llm_cache_mod.get_from_cache("prompt", "model_b") == "response_b"

    def test_json_response_roundtrip(self, isolated_cache):
        """JSON 格式响应应完整保留。"""
        import json
        response = json.dumps({
            "sentiment": "正面",
            "confidence": 0.95,
            "reason": "银行业绩增长显著",
            "tags": ["金融", "银行", "增长"],
        }, ensure_ascii=False)
        llm_cache_mod.save_to_cache("分析文本", "gpt4", response)
        cached = llm_cache_mod.get_from_cache("分析文本", "gpt4")
        parsed = json.loads(cached)
        assert parsed["sentiment"] == "正面"
        assert parsed["confidence"] == 0.95

