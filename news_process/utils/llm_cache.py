"""
utils/llm_cache.py — LLM 请求级 SQLite 缓存
=============================================

功能:
  对 LLM API 请求进行持久化缓存，避免重复调用相同 prompt 的 API。
  使用 SHA-256(len(model_id) + ":" + model_id + ":" + prompt_text) 作为缓存键，
  长度前缀防止 model_id 含冒号时的键碰撞（如 "a:b" + "c" vs "a" + "b:c"）。
  仅缓存 HTTP 200 成功响应，失败/超时不缓存（避免永久化瞬时故障）。

线程安全:
  sqlite3.connect(db_path, check_same_thread=False) + WAL 日志模式，
  支持多线程并发读写（asyncio 事件循环中的同步调用为微秒级，不阻塞）。

学术依据:
  缓存机制确保实验可复现性 —— 相同输入始终返回相同输出，
  符合 Carlson & Burbano (2026, SMJ §3.3) 对 LLM 实验可复现性的要求。
"""

import os
import sqlite3
import hashlib
import time
import logging
import threading

logger = logging.getLogger(__name__)


class LLMCache:
    """LLM 请求级 SQLite 缓存。

    缓存键: sha256(len(model_id) + ":" + model_id + ":" + prompt_text)
    缓存值: API 原始响应文本 + 模型标识 + 时间戳

    Attributes:
        db_path: SQLite 数据库文件路径。
    """

    def __init__(self, db_path: str):
        """初始化 LLM 缓存。

        Args:
            db_path: SQLite 数据库文件路径。若不存在则自动创建。
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        # WAL 模式: 支持并发读，写入不阻塞读取
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key   TEXT PRIMARY KEY,
                model_id    TEXT NOT NULL,
                response    TEXT NOT NULL,
                created_at  REAL NOT NULL
            )
        """)
        self._conn.commit()

    @staticmethod
    def _make_key(model_id: str, prompt: str) -> str:
        """生成缓存键: sha256(len(model_id) + ":" + model_id + ":" + prompt_text)。

        使用长度前缀消除 model_id 含冒号时的键碰撞风险。

        Args:
            model_id: 模型标识符。
            prompt:   请求的 prompt 文本。

        Returns:
            str: 64 字符的十六进制 SHA-256 哈希值。
        """
        raw = f"{len(model_id)}:{model_id}:{prompt}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get(self, model_id: str, prompt: str) -> str | None:
        """查询缓存。

        Args:
            model_id: 模型标识符。
            prompt:   请求的 prompt 文本。

        Returns:
            str | None: 缓存的响应文本，未命中时返回 None。
        """
        key = self._make_key(model_id, prompt)
        with self._lock:
            cursor = self._conn.execute(
                "SELECT response FROM llm_cache WHERE cache_key = ?", (key,)
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def put(self, model_id: str, prompt: str, response: str) -> None:
        """写入缓存（仅成功响应应调用此方法）。

        使用 INSERT OR REPLACE 确保幂等性。

        Args:
            model_id: 模型标识符。
            prompt:   请求的 prompt 文本。
            response: API 返回的原始响应文本。
        """
        key = self._make_key(model_id, prompt)
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (key, model_id, response, time.time())
            )
            self._conn.commit()

    def size(self) -> int:
        """返回缓存中的总条目数。

        Returns:
            int: 缓存条目数。
        """
        with self._lock:
            cursor = self._conn.execute("SELECT COUNT(*) FROM llm_cache")
            return cursor.fetchone()[0]

    def close(self) -> None:
        """关闭数据库连接。"""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
