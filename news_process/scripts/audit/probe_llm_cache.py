"""probe_llm_cache — LLM cache occupancy probe (V4 T0.0).

One-shot diagnostic: report cached entry count and time range of the
SQLite-backed LLM cache. Does NOT measure hit-rate (that requires
counters on LLMCache.get/put — out of scope for Wave 0; future work).

Usage:
    python -m news_process.scripts.audit.probe_llm_cache

Output (stdout, also appended to docs/llm_cache_probe_<date>.log):
    cached entries:   <int>
    earliest entry:   <ISO timestamp or '(empty)'>
    latest entry:     <ISO timestamp or '(empty)'>
    db file size:     <human-readable>
    db path:          <absolute>
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve project root from this file's location (no chdir, no load_config side-effects).
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
