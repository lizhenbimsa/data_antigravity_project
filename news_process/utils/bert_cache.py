"""
utils/bert_cache.py
===================
BERT 推理结果本地缓存模块。
基于 SQLite 实现，通过 SHA-256(text + model_name) 缓存每篇文章的推理结果，
中断后无需重新推理即可恢复，大幅加速增量运行场景。

与 llm_cache.py 的设计对称，但针对 BERT batch 推理场景提供批量接口。
"""

import os
import json
import sqlite3
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 懒加载状态
_cache_db_path: Optional[str] = None
_db_initialized: bool = False


def _resolve_cache_path() -> str:
    """解析缓存数据库路径，失败回退到默认路径。"""
    default = os.path.join(PROJECT_ROOT, 'data_processed', 'bert_cache.db')
    try:
        from utils.helpers import load_config
        cfg = load_config()
        output_dir = cfg.get('paths', {}).get('output_dir', '')
        if output_dir:
            return os.path.join(output_dir, 'bert_cache.db')
    except Exception:
        pass
    return default


def _get_cache_path() -> str:
    """获取缓存数据库路径（懒加载）。"""
    global _cache_db_path
    if _cache_db_path is None:
        _cache_db_path = _resolve_cache_path()
    return _cache_db_path


def _ensure_db():
    """确保数据库表已初始化（懒加载）。"""
    global _db_initialized
    if _db_initialized:
        return
    cache_path = _get_cache_path()
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with sqlite3.connect(cache_path, check_same_thread=False) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bert_cache (
                    hash_key TEXT PRIMARY KEY,
                    text_preview TEXT,
                    model_name TEXT,
                    result_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        _db_initialized = True
    except Exception as e:
        logger.warning(f"初始化 BERT 缓存数据库失败: {e}")


def _get_hash(text: str, model_name: str) -> str:
    """计算 text + model_name 的 SHA-256 哈希值。"""
    hash_input = f"{model_name}_{text}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def get_batch_from_cache(texts: list[str], model_name: str) -> dict[int, dict]:
    """批量查询缓存，返回命中的文章索引及其结果。

    Args:
        texts:      文本列表。
        model_name: 模型短名称（如 ``finbert_cn``）。

    Returns:
        dict: ``{文章索引: result_dict}``，仅包含命中缓存的条目。
              result_dict 结构: ``{'label': str, 'probabilities': dict, 'num_windows': int}``
    """
    _ensure_db()
    if not texts:
        return {}

    hash_keys = [_get_hash(t, model_name) for t in texts]
    cached_results = {}

    try:
        with sqlite3.connect(_get_cache_path(), check_same_thread=False) as conn:
            # 分批查询（SQLite 参数上限约 999）
            batch_size = 500
            for start in range(0, len(hash_keys), batch_size):
                batch_hashes = hash_keys[start:start + batch_size]
                placeholders = ','.join(['?'] * len(batch_hashes))
                rows = conn.execute(
                    f'SELECT hash_key, result_json FROM bert_cache WHERE hash_key IN ({placeholders})',
                    batch_hashes
                ).fetchall()

                hash_to_result = {row[0]: row[1] for row in rows}

                for i, hk in enumerate(batch_hashes):
                    if hk in hash_to_result:
                        try:
                            cached_results[start + i] = json.loads(hash_to_result[hk])
                        except json.JSONDecodeError:
                            pass  # 损坏的缓存条目，忽略并重新推理
    except Exception as e:
        logger.warning(f"批量读取 BERT 缓存失败: {e}")

    return cached_results


def save_batch_to_cache(texts: list[str], model_name: str,
                        results: list[dict], indices: list[int] | None = None):
    """批量写入推理结果到缓存。

    Args:
        texts:      完整的文本列表（与推理时保持一致）。
        model_name: 模型短名称。
        results:    推理结果字典列表（与 texts 等长，或与 indices 等长）。
        indices:    可选，指定 texts 中哪些索引对应 results。
                    若为 None，则 results 与 texts 一一对应。
    """
    _ensure_db()
    if not results:
        return

    rows_to_insert = []
    if indices is None:
        # results 与 texts 一一对应
        for i, (text, result) in enumerate(zip(texts, results)):
            if result and result.get('num_windows', 0) > 0:
                hk = _get_hash(text, model_name)
                preview = text[:100] if text else ''
                rows_to_insert.append((hk, preview, model_name, json.dumps(result, ensure_ascii=False)))
    else:
        # results 与 indices 一一对应
        for idx, result in zip(indices, results):
            if result and result.get('num_windows', 0) > 0 and idx < len(texts):
                text = texts[idx]
                hk = _get_hash(text, model_name)
                preview = text[:100] if text else ''
                rows_to_insert.append((hk, preview, model_name, json.dumps(result, ensure_ascii=False)))

    if not rows_to_insert:
        return

    try:
        with sqlite3.connect(_get_cache_path(), check_same_thread=False) as conn:
            conn.executemany(
                'INSERT OR REPLACE INTO bert_cache (hash_key, text_preview, model_name, result_json) '
                'VALUES (?, ?, ?, ?)',
                rows_to_insert
            )
    except Exception as e:
        logger.warning(f"批量写入 BERT 缓存失败: {e}")
