"""news_process.core.caching — LLM 请求级 SQLite 缓存。

源自 Phase 1 mega-module ``utils/llm_cache.py`` 拆分 (Plan-r3 P2-11
头部修正).

功能
-----
对 LLM API 请求进行持久化缓存，避免重复调用相同 prompt 的 API。

缓存键组成 (Plan-r3 P3-17 升级)
-------------------------------
键 = SHA-256 哈希:

    ``f"{SCHEMA_VERSION}|{len(model_id)}:{model_id}|{len(prompt)}:{prompt}|{prompt_version}|{temperature:.4f}"``

各字段含义:

- ``SCHEMA_VERSION`` (常量) — 本模块版本标识. 任何 prompt 模板 / system
  prompt / 响应格式约定层面的修改, 都应 bump 此常量, 让全部历史 cache
  自动失效 (silent miss → 重新调 API). v0 是 round 1+2 历史; v1 是
  Plan-r3 P3-17 引入 prompt_version + temperature 维度的标记.
- ``len(x):x`` 长度前缀 — 防止 ``("a", "b:c")`` 与 ``("a:b", "c")`` 的拼接
  歧义碰撞 (round 1 已有的设计).
- ``prompt_version`` — 调用方显式传入的 prompt 模板版本 (例如
  ``"v6-2026-05-09"``, 与 ``config/prompts/*.txt`` 头部 ``# version: ...``
  对齐). 默认 ``"v0"`` 表示未指定.
- ``temperature`` — LLM 推理温度 (默认 0.0 = 确定性). 0.0 与 0.5 的响应
  分布完全不同, 共用同一缓存键会污染.

设计意图
---------
- silent staleness 防御 — round 1+2 缓存键仅 (model_id, prompt), 当
  prompts/sentiment_cot.txt 改写时, 旧 cache 仍命中, 分析结果不反映新提示词.
  现在 prompt_version 进键, 改一行 prompt → cache miss → 重新调 API.
- BREAKING — Plan-r3 P3-17 把 SCHEMA_VERSION 从 ``"v0"`` 升至 ``"v1"``,
  既有 ``_llm_cache.db`` (236 MiB) 全部 silent miss, 下次跑 stage 21 / 15
  / 27 会冷启动. 用户已在 plan 中 explicit 接受此代价.
- 向后兼容 API — ``get/put/put_batch`` 新增的两个参数 ``prompt_version``
  / ``temperature`` 都有默认值 (v0 / 0.0); 旧调用方不修改也能跑, 只是
  键会落到 (v1, v0, 0.0) 命名空间, 与 round 1+2 (v0 命名空间) 完全隔离.

线程安全
---------
sqlite3.connect(db_path, check_same_thread=False) + WAL 日志模式。

学术依据
---------
Carlson & Burbano (2026, SMJ §3.3) — LLM 实验可复现性要求确定性缓存.
Plan-r3 P3-17 的 prompt_version 维度直接对应 §3.3.2 "version-aware
provenance" 实践: 任何 prompt 改动必须导致 cache invalidate.
"""

import os
import sqlite3
import hashlib
import time
import logging
import threading

logger = logging.getLogger(__name__)


# Plan-r3 P3-17: 缓存键 schema 版本. 任何键组成或语义层面的破坏性变更
# 都必须 bump 此常量, 让所有历史 cache 静默失效 (重新调 API).
#
# v0 — round 1+2 (key = sha256(len:model_id:prompt))
# v1 — Plan-r3 P3-17 (key = sha256(SCHEMA|len:model_id|len:prompt|pv|temp))
SCHEMA_VERSION = "v1"


class LLMCache:
    """LLM 请求级 SQLite 缓存。

    缓存键: sha256(SCHEMA_VERSION|len:model_id|len:prompt|prompt_version|temperature).
    缓存值: API 原始响应文本 + 模型标识 + 时间戳.

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
    def _make_key(model_id: str, prompt: str,
                  *, prompt_version: str = "v0",
                  temperature: float = 0.0) -> str:
        """生成缓存键 (Plan-r3 P3-17 升级版).

        Args:
            model_id:        模型标识符 (例如 "gpt-5-nano-2025-08-07").
            prompt:          请求的 prompt 文本.
            prompt_version:  prompt 模板版本字符串 (例如 "v6-2026-05-09").
                             默认 "v0" 表示调用方未指定 — 与新 prompt 改动后
                             的 cache 自然分离.
            temperature:     LLM 推理温度 (默认 0.0 = 确定性).

        Returns:
            str: 64 字符的十六进制 SHA-256 哈希值。

        Note:
            键格式见模块 docstring "缓存键组成". 任何破坏性变更必须 bump
            模块级 ``SCHEMA_VERSION`` 常量.
        """
        m_id = str(model_id) if model_id is not None else ""
        p_str = str(prompt) if prompt is not None else ""
        pv = str(prompt_version) if prompt_version is not None else "v0"
        temp_str = f"{float(temperature):.4f}"
        # SCHEMA|len:model|len:prompt|pv|temp
        raw = (
            f"{SCHEMA_VERSION}|"
            f"{len(m_id)}:{m_id}|"
            f"{len(p_str)}:{p_str}|"
            f"{pv}|{temp_str}"
        )
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get(self, model_id: str, prompt: str,
            *, prompt_version: str = "v0",
            temperature: float = 0.0) -> str | None:
        """查询缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        Args:
            model_id:        模型标识符.
            prompt:          请求的 prompt 文本.
            prompt_version:  prompt 模板版本 (默认 "v0", 与历史无关键值兼容).
            temperature:     推理温度 (默认 0.0).

        Returns:
            str | None: 缓存的响应文本, 未命中返回 None.
        """
        key = self._make_key(model_id, prompt,
                             prompt_version=prompt_version,
                             temperature=temperature)
        with self._lock:
            cursor = self._conn.execute(
                "SELECT response FROM llm_cache WHERE cache_key = ?", (key,)
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def put(self, model_id: str, prompt: str, response: str,
            *, prompt_version: str = "v0",
            temperature: float = 0.0) -> None:
        """写入缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        仅在 HTTP 200 成功响应时调用. 使用 INSERT OR REPLACE 确保幂等性.

        Args:
            model_id:        模型标识符.
            prompt:          请求的 prompt 文本.
            response:        API 返回的原始响应文本.
            prompt_version:  prompt 模板版本.
            temperature:     推理温度.
        """
        key = self._make_key(model_id, prompt,
                             prompt_version=prompt_version,
                             temperature=temperature)
        m_id = str(model_id) if model_id is not None else ""
        r_str = str(response) if response is not None else ""
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (key, m_id, r_str, time.time())
            )
            self._conn.commit()

    def put_batch(self, model_id: str, prompts: list[str], responses: list[str],
                  *, prompt_version: str = "v0",
                  temperature: float = 0.0) -> None:
        """批量原子写入缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        使用 executemany 配合事务大幅提升高并发环境下的写入吞吐量。
        在处理 Batch Embedding (每批数千条) 时可避免频繁的 I/O 锁抢占。

        Args:
            model_id:        模型标识符.
            prompts:         请求的 prompt 列表.
            responses:       API 对应的响应文本列表.
            prompt_version:  prompt 模板版本.
            temperature:     推理温度.
        """
        if not prompts or not responses or len(prompts) != len(responses):
            return

        now = time.time()
        rows = []
        m_id = str(model_id) if model_id is not None else ""
        for p, r in zip(prompts, responses):
            key = self._make_key(model_id, p,
                                 prompt_version=prompt_version,
                                 temperature=temperature)
            r_str = str(r) if r is not None else ""
            rows.append((key, m_id, r_str, now))

        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                rows
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

    def __enter__(self):
        """上下文管理器入口。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，自动关闭连接。"""
        self.close()
        return False
