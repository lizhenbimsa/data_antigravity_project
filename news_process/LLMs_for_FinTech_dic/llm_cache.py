"""
LLMs_for_FinTech_dic 独立大模型缓存模块

与主项目 news_process/core/caching.py 完全独立：本目录脚本以 top-level 方式运行
(from config import ...)，缓存库落在本目录 data_processed/_llm_cache.db。

设计要点：
- SQLite 单文件缓存，线程安全（WAL + 全局锁），适配主脚本 200 线程并发。
- 缓存键 = sha256(model | temperature | tag | prompt)：
  * 生成阶段 temperature=模型默认（非确定性采样），tag 必须携带重复序号
    rep{idx} 与解析重试序号 try{n} —— 同一次运行的 100 次重复各占独立槽位，
    不会把 100 次多样性采样折叠成 1 个答案。
  * 判别阶段 temperature=0（确定性），同一批词 + 同一 prompt 天然同键。
- 原始响应照存（包括后来解析失败的响应）：重放时命中同样的"坏"响应会走同一条
  解析重试路径（try 序号变 → 新键 → 才会真调 API），保证重放行为可复现。
- ⚠ "$0 离线重放" 的前提 = 首跑干净收尾：首跑中 API 硬失败耗尽重试、模型被
  健康追踪器跳过、Ctrl+C 中断的槽位没有缓存条目（缓存空洞），重放走到即 miss。
  另外 _model_health 状态不进缓存 —— 有模型被跳过的首跑不具备逐字节可复现性。
- 离线模式：环境变量 LLMS_DIC_OFFLINE=1 时 miss → raise LLMCacheMissError
  （fail-loud，绝不静默调 API 付费，镜像主项目 NEWS_PROCESS_LLM_OFFLINE 语义；
  消费方 00 脚本捕获后置全局停止事件走优雅中断）。
- 整体开关：环境变量 LLMS_DIC_CACHE=0 可停用（读写全跳过，行为等同无缓存）。
- ⚠ 缓存默认开启意味着"再跑一遍"= 重放而非重新采样；想要新的多样性采样，
  须 LLMS_DIC_CACHE=0 或先 --clear 清库。

CLI：
    python llm_cache.py --stats        # 查看缓存统计（条数/大小/按模型分布）
    python llm_cache.py --clear --yes  # 清空缓存（必须显式加 --yes 确认）
"""

import hashlib
import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class LLMCacheMissError(RuntimeError):
    """离线模式 (LLMS_DIC_OFFLINE=1) 下缓存未命中时抛出，阻止任何付费 API 调用。"""


class LLMCache:
    """线程安全的 SQLite 大模型响应缓存。

    单连接 + 全局锁：本脚本的瓶颈在 API 网络往返（秒级），SQLite 读写是微秒级，
    串行化不构成瓶颈；WAL 模式避免读写互斥放大。
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # timeout=60: 多进程并发（另一脚本实例 / CLI --clear 的 VACUUM 独占锁）时
        # 等锁而非 5s 默认就抛 "database is locked"
        self._conn = sqlite3.connect(
            str(self._db_path), check_same_thread=False, timeout=60
        )
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_cache (
                key         TEXT PRIMARY KEY,
                model       TEXT NOT NULL,
                temperature TEXT NOT NULL,
                tag         TEXT NOT NULL,
                prompt      TEXT NOT NULL,
                response    TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
            """
        )
        self._conn.commit()
        # 会话内命中统计（跨进程不累计）
        self.hits = 0
        self.misses = 0

    @staticmethod
    def make_key(model: str, prompt: str, temperature: str, tag: str) -> str:
        # JSON 数组编码：字段边界无歧义（分隔符方案在 prompt 含控制字符时
        # 理论上可构造相邻字段边界移动的碰撞）
        raw = json.dumps([model, temperature, tag, prompt], ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, model: str, prompt: str, temperature: str, tag: str) -> Optional[str]:
        """命中返回缓存的响应文本，未命中（或读取异常降级）返回 None。

        读取异常（库损坏/孤立代理对等编码问题）按 miss 降级并记 WARNING，
        不炸穿调用方 worker 线程。
        """
        try:
            key = self.make_key(model, prompt, temperature, tag)
            with self._lock:
                row = self._conn.execute(
                    "SELECT response FROM llm_cache WHERE key = ?", (key,)
                ).fetchone()
                if row is not None:
                    self.hits += 1
                    return row[0]
                self.misses += 1
                return None
        except Exception as e:
            logging.getLogger("LLMs_for_dic").warning(f"LLM 缓存读取失败 (按未命中处理): {e}")
            with self._lock:
                self.misses += 1
            return None

    def put(self, model: str, prompt: str, temperature: str, tag: str, response: str) -> None:
        """写入响应（同键重复写入以首次为准，保证重放稳定）。

        写失败只记 WARNING 绝不上抛：此时 API 已成功返回、费用已发生，缓存写失败
        若上抛会被调用方误当 API 失败 → 丢弃响应重复付费。兜 Exception 而非仅
        sqlite3.Error：孤立代理对（LLM 垃圾输出）在 sqlite 绑定时抛 UnicodeEncodeError。
        """
        try:
            key = self.make_key(model, prompt, temperature, tag)
            with self._lock:
                self._conn.execute(
                    "INSERT OR IGNORE INTO llm_cache "
                    "(key, model, temperature, tag, prompt, response, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (key, model, temperature, tag, prompt, response,
                     datetime.now().isoformat(timespec="seconds")),
                )
                self._conn.commit()
        except Exception as e:
            logging.getLogger("LLMs_for_dic").warning(
                f"LLM 缓存写入失败 (响应不受影响, 仅本条不缓存): {e}"
            )

    def stats(self) -> Dict:
        """返回缓存整体统计：总条数、按模型分布、库文件大小（含 WAL/SHM 侧车）。"""
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM llm_cache").fetchone()[0]
            by_model = dict(
                self._conn.execute(
                    "SELECT model, COUNT(*) FROM llm_cache GROUP BY model ORDER BY 2 DESC"
                ).fetchall()
            )
        size_bytes = sum(
            p.stat().st_size
            for p in (
                self._db_path,
                self._db_path.with_name(self._db_path.name + "-wal"),
                self._db_path.with_name(self._db_path.name + "-shm"),
            )
            if p.exists()
        )
        return {
            "db_path": str(self._db_path),
            "total_entries": total,
            "by_model": by_model,
            "size_mb": size_bytes / 1024 / 1024,
            "session_hits": self.hits,
            "session_misses": self.misses,
        }

    def clear(self) -> int:
        """清空全部缓存条目，返回删除条数。"""
        with self._lock:
            n = self._conn.execute("SELECT COUNT(*) FROM llm_cache").fetchone()[0]
            self._conn.execute("DELETE FROM llm_cache")
            self._conn.commit()
            self._conn.execute("VACUUM")
        return n

    def close(self) -> None:
        with self._lock:
            self._conn.close()


def _cli() -> None:
    import argparse
    import sys

    from config import CACHE_DB_FILE

    # zh-CN Windows 控制台/重定向默认 GBK，非 GBK 字符会 UnicodeEncodeError 崩溃
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="LLMs_for_FinTech_dic 独立 LLM 缓存管理")
    parser.add_argument("--stats", action="store_true", help="查看缓存统计")
    parser.add_argument("--clear", action="store_true", help="清空缓存（须配合 --yes）")
    parser.add_argument("--yes", action="store_true", help="确认执行破坏性操作")
    args = parser.parse_args()

    cache = LLMCache(CACHE_DB_FILE)
    try:
        if args.clear:
            if not args.yes:
                print("[警告] 清空缓存是不可逆操作，请加 --yes 确认: python llm_cache.py --clear --yes")
                print("[警告] 清空前请确认主脚本 00_LLMs_for_dic.py 未在运行 (VACUUM 需独占锁)")
                return
            n = cache.clear()
            print(f"[完成] 已清空缓存 {n} 条 ({cache._db_path})")
        else:
            s = cache.stats()
            print(f"缓存库: {s['db_path']}")
            print(f"总条数: {s['total_entries']}  |  大小: {s['size_mb']:.2f} MB")
            if s["by_model"]:
                print("按模型分布:")
                for m, c in s["by_model"].items():
                    print(f"  {m:<40s} {c:>8d}")
    finally:
        cache.close()


if __name__ == "__main__":
    _cli()
