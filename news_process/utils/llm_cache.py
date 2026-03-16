"""
utils/llm_cache.py
==================
LLM API 本地文本缓存模块。
基于 SQLite 实现，通过比对 SHA-256(prompt+model_name) 来避免重复发起真实网络请求，
能够在发生中断或增量调试时瞬间恢复并节约 API 成本。
"""

import os
import sqlite3
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 获取模块所在的根目录以便存放缓存文件
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 缓存数据库路径（懒加载时解析）
_cache_db_path: Optional[str] = None
_db_initialized: bool = False


def _resolve_cache_path() -> str:
    """使用 load_config() 统一解析缓存路径，失败则回退到默认路径。"""
    default = os.path.join(PROJECT_ROOT, 'data_processed', 'llm_cache.db')
    try:
        from utils.helpers import load_config
        cfg = load_config()
        output_dir = cfg.get('paths', {}).get('output_dir', '')
        if output_dir:
            return os.path.join(output_dir, 'llm_cache.db')
    except Exception:
        pass
    return default


def _get_cache_path() -> str:
    """获取缓存数据库路径（懒加载，首次调用时解析）。"""
    global _cache_db_path
    if _cache_db_path is None:
        _cache_db_path = _resolve_cache_path()
    return _cache_db_path


def _ensure_db():
    """确保数据库表已初始化（懒加载，仅在首次实际使用时创建）。"""
    global _db_initialized
    if _db_initialized:
        return
    cache_path = _get_cache_path()
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with sqlite3.connect(cache_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    hash_key TEXT PRIMARY KEY,
                    prompt TEXT,
                    model_name TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        _db_initialized = True
    except Exception as e:
        logger.warning(f"初始化 LLM 缓存数据库失败: {e}")


def _get_hash(prompt: str, model_name: str) -> str:
    """计算 Prompt 和 Model 组合的 SHA-256 哈希值，作为缓存的 Key。"""
    hash_input = f"{model_name}_{prompt}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def get_from_cache(prompt: str, model_name: str) -> Optional[str]:
    """从本地 SQLite 查询缓存。"""
    _ensure_db()
    hash_key = _get_hash(prompt, model_name)
    try:
        with sqlite3.connect(_get_cache_path()) as conn:
            row = conn.execute('SELECT response FROM api_cache WHERE hash_key = ?', (hash_key,)).fetchone()
            if row:
                return row[0]
    except Exception as e:
        logger.warning(f"  读取 LLM 缓存失败: {e}")
    return None


def save_to_cache(prompt: str, model_name: str, response: str):
    """将成功的请求结果写入 SQLite 缓存。"""
    _ensure_db()
    hash_key = _get_hash(prompt, model_name)
    try:
        with sqlite3.connect(_get_cache_path()) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO api_cache (hash_key, prompt, model_name, response) VALUES (?, ?, ?, ?)',
                (hash_key, prompt, model_name, response)
            )
    except Exception as e:
        logger.warning(f"  写入 LLM 文本缓存失败: {e}")
