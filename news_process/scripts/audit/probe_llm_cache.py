"""probe_llm_cache — LLM 缓存占用探针 (V4 T0.0)。

一次性诊断: 报告 SQLite LLM 缓存 (_llm_cache.db) 的条目总数与时间范围。
**不**测量命中率 (那需要在 LLMCache.get/put 上加计数器 — 超出 Wave 0 范围,
留作后续工作; 命中率审计请用 verify_stage21_cache_coverage)。

用法:
    python -m news_process.scripts.audit.probe_llm_cache

输出 (stdout, 同时追加写入 docs/llm_cache_probe_<date>.log):
    cached entries:   <int>
    earliest entry:   <ISO 时间戳或 '(empty)'>
    latest entry:     <ISO 时间戳或 '(empty)'>
    db file size:     <人类可读大小>
    db path:          <绝对路径>

白话: 只是数一数缓存数据库里存了多少条、最早最晚各是什么时候、文件多大,
纯读不写, 不花钱不联网。
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# 从本文件位置解析项目根 (不 chdir, 不触发 load_config 副作用)。
# probe_llm_cache.py → scripts/audit/ → scripts/ → news_process/
_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[2]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "_llm_cache.db"
LOG_DIR = PROJECT_ROOT / "docs"


def _humansize(n_bytes: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n_bytes < 1024 or unit == "GiB":
            return f"{n_bytes:.1f} {unit}"
        n_bytes = n_bytes / 1024
    return f"{n_bytes:.1f} GiB"


def main() -> int:
    if not DB_PATH.exists():
        print(f"SKIP: cache db not found at {DB_PATH}", file=sys.stderr)
        return 0

    size = DB_PATH.stat().st_size
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM llm_cache"
        ).fetchone()
    finally:
        conn.close()

    count, min_ts, max_ts = row
    earliest = (
        datetime.fromtimestamp(min_ts, timezone.utc).isoformat()
        if min_ts is not None
        else "(empty)"
    )
    latest = (
        datetime.fromtimestamp(max_ts, timezone.utc).isoformat()
        if max_ts is not None
        else "(empty)"
    )

    report = (
        f"=== LLM cache probe ({datetime.now(timezone.utc).isoformat()}) ===\n"
        f"cached entries:   {count}\n"
        f"earliest entry:   {earliest}\n"
        f"latest entry:     {latest}\n"
        f"db file size:     {_humansize(size)}\n"
        f"db path:          {DB_PATH}\n"
    )
    print(report)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"llm_cache_probe_{datetime.now(timezone.utc).date().isoformat()}.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"appended to {log_file.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
