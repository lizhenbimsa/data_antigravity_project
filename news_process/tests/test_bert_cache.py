"""
tests/test_bert_cache.py — utils/bert_cache.py 单元测试
========================================================
"""

import os
import sys
import json
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.bert_cache as bert_cache_mod


# ============================================================================
# Fixture: 隔离缓存数据库
# ============================================================================

@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """每个测试使用独立的临时 SQLite 缓存数据库。"""
    db_path = str(tmp_path / 'test_bert_cache.db')
    monkeypatch.setattr(bert_cache_mod, '_cache_db_path', db_path)
    monkeypatch.setattr(bert_cache_mod, '_db_initialized', False)
    yield db_path


# ============================================================================
# 测试用例
# ============================================================================

class TestBertCache:
    """测试 BERT 缓存批量操作。"""

    def _make_result(self, label='正面', num_windows=3):
        """创建模拟推理结果字典。"""
        return {
            'label': label,
            'probabilities': {'正面': 0.8, '中性': 0.1, '负面': 0.1},
            'num_windows': num_windows,
        }

    def test_save_and_get_batch(self):
        """批量写入后批量读取应一致。"""
        texts = ['文章一', '文章二', '文章三']
        model = 'finbert_cn'
        results = [
            self._make_result('正面'),
            self._make_result('中性'),
            self._make_result('负面'),
        ]

        bert_cache_mod.save_batch_to_cache(texts, model, results)
        cached = bert_cache_mod.get_batch_from_cache(texts, model)

        assert len(cached) == 3
        assert cached[0]['label'] == '正面'
        assert cached[1]['label'] == '中性'
        assert cached[2]['label'] == '负面'

    def test_get_batch_partial_hit(self):
        """部分命中应只返回命中的条目。"""
        texts = ['已缓存', '未缓存']
        model = 'test_model'

        # 仅缓存第一条
        bert_cache_mod.save_batch_to_cache(
            ['已缓存'], model, [self._make_result()]
        )

        cached = bert_cache_mod.get_batch_from_cache(texts, model)
        assert 0 in cached
        assert 1 not in cached

    def test_get_batch_empty_input(self):
        """空输入应返回空字典。"""
        cached = bert_cache_mod.get_batch_from_cache([], 'model')
        assert cached == {}

    def test_save_batch_with_indices(self):
        """使用 indices 模式保存应正确关联。"""
        texts = ['不保存A', '要保存的文章A', '不保存B', '要保存的文章B']
        model = 'test_model'
        results = [self._make_result('正面'), self._make_result('负面')]
        indices = [1, 3]

        bert_cache_mod.save_batch_to_cache(texts, model, results, indices)

        cached = bert_cache_mod.get_batch_from_cache(texts, model)
        assert 1 in cached
        assert 3 in cached
        assert 0 not in cached
        assert 2 not in cached
        assert cached[1]['label'] == '正面'
        assert cached[3]['label'] == '负面'

    def test_corrupted_cache_entry(self, tmp_path, monkeypatch):
        """损坏的 JSON 条目应被跳过而不报错。"""
        db_path = str(tmp_path / 'test_bert_corrupt.db')
        monkeypatch.setattr(bert_cache_mod, '_cache_db_path', db_path)
        monkeypatch.setattr(bert_cache_mod, '_db_initialized', False)

        # 手动插入一条损坏的 JSON
        bert_cache_mod._ensure_db()
        import hashlib
        text = '损坏的文章'
        model = 'broken_model'
        hk = hashlib.sha256(f"{model}_{text}".encode('utf-8')).hexdigest()

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO bert_cache '
                '(hash_key, text_preview, model_name, result_json) '
                'VALUES (?, ?, ?, ?)',
                (hk, text[:100], model, '{invalid json!!!}')
            )

        # 读取不应崩溃，损坏条目应被跳过
        cached = bert_cache_mod.get_batch_from_cache([text], model)
        assert len(cached) == 0

    def test_save_empty_results(self):
        """空结果列表不应崩溃。"""
        bert_cache_mod.save_batch_to_cache(['t1'], 'model', [])
        # 不应有缓存
        cached = bert_cache_mod.get_batch_from_cache(['t1'], 'model')
        assert len(cached) == 0

    def test_skip_zero_windows(self):
        """num_windows=0 的结果不应被缓存。"""
        texts = ['无窗口文章']
        model = 'test_model'
        results = [self._make_result(num_windows=0)]

        bert_cache_mod.save_batch_to_cache(texts, model, results)
        cached = bert_cache_mod.get_batch_from_cache(texts, model)
        assert len(cached) == 0

    def test_hash_deterministic(self):
        """哈希应确定性重复。"""
        h1 = bert_cache_mod._get_hash("相同文本", "same_model")
        h2 = bert_cache_mod._get_hash("相同文本", "same_model")
        assert h1 == h2


# ============================================================================
# 增强测试：大批量与隔离性
# ============================================================================

class TestBertCacheEnhanced:
    """增强测试：大批量操作和模型隔离。"""

    @staticmethod
    def _make_result(label='正面', num_windows=1):
        return {
            'label': label,
            'probabilities': {'正面': 0.8, '中性': 0.1, '负面': 0.1},
            'num_windows': num_windows,
        }

    def test_large_batch_consistency(self, isolated_cache):
        """大批量写入后应全部正确读取。"""
        n = 100
        texts = [f"文本内容_{i}" for i in range(n)]
        model = "test_model"
        results = [self._make_result(label=f"label_{i}") for i in range(n)]

        bert_cache_mod.save_batch_to_cache(texts, model, results)
        cached = bert_cache_mod.get_batch_from_cache(texts, model)

        assert len(cached) == n
        for i in range(n):
            assert cached[i]['label'] == f"label_{i}"

    def test_different_models_isolation(self, isolated_cache):
        """相同文本不同模型应独立缓存。"""
        text = "相同的文本内容"
        model_a = "finbert_cn"
        model_b = "erlangshen"

        result_a = [self._make_result(label='正面')]
        result_b = [self._make_result(label='负面')]

        bert_cache_mod.save_batch_to_cache([text], model_a, result_a)
        bert_cache_mod.save_batch_to_cache([text], model_b, result_b)

        cached_a = bert_cache_mod.get_batch_from_cache([text], model_a)
        cached_b = bert_cache_mod.get_batch_from_cache([text], model_b)

        assert cached_a[0]['label'] == '正面'
        assert cached_b[0]['label'] == '负面'

    def test_unicode_texts(self, isolated_cache):
        """Unicode 文本应正常缓存。"""
        texts = ["中文银行新闻 🎉", "日本語テスト", "한국어 뉴스"]
        model = "unicode_model"
        results = [self._make_result() for _ in texts]

        bert_cache_mod.save_batch_to_cache(texts, model, results)
        cached = bert_cache_mod.get_batch_from_cache(texts, model)

        assert len(cached) == 3

    def test_overwrite_preserves_latest(self, isolated_cache):
        """覆盖写入应保留最新结果。"""
        texts = ["测试文本"]
        model = "test_model"

        old_result = [self._make_result(label='中性')]
        bert_cache_mod.save_batch_to_cache(texts, model, old_result)

        new_result = [self._make_result(label='正面')]
        bert_cache_mod.save_batch_to_cache(texts, model, new_result)

        cached = bert_cache_mod.get_batch_from_cache(texts, model)
        assert cached[0]['label'] == '正面'

    def test_mixed_hit_miss_batch(self, isolated_cache):
        """批量查询时应正确返回命中和未命中。"""
        texts = ["已缓存", "未缓存"]
        model = "test_model"

        bert_cache_mod.save_batch_to_cache(["已缓存"], model,
                                            [self._make_result(label='正面')])

        cached = bert_cache_mod.get_batch_from_cache(texts, model)
        assert 0 in cached  # "已缓存" 应命中
        assert 1 not in cached  # "未缓存" 应未命中

