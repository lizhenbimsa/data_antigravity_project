"""tests/test_run_id.py — Round 55 quality-hardening.

`core/run_id.py::generate_run_id` 此前无直接单测; 92.86% (1 miss = line 25
"return existing" 分支). 此文件补完两条路径: NEWS_PROCESS_RUN_ID 已存在 →
直通; 未设 → 生成新 ID 并写环境变量.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.core.run_id import generate_run_id


def test_generate_run_id_format(monkeypatch):
    """新生成的 run_id 满足 'YYYYMMDDTHHMMSSZ-host-pid' 格式."""
    monkeypatch.delenv("NEWS_PROCESS_RUN_ID", raising=False)
    rid = generate_run_id()
    assert "T" in rid
    assert rid.count("-") >= 2
    # ts 前缀 16 字符 'YYYYMMDDTHHMMSSZ'
    ts = rid.split("-")[0]
    assert len(ts) == 16
    assert ts.endswith("Z")
    # 写回环境变量
    import os
    assert os.environ["NEWS_PROCESS_RUN_ID"] == rid


def test_generate_run_id_reuses_env_when_set(monkeypatch):
    """NEWS_PROCESS_RUN_ID 已设 → 直接返回不生成新 ID (line 25)."""
    existing = "20251231T235959Z-fake_host-1234"
    monkeypatch.setenv("NEWS_PROCESS_RUN_ID", existing)
    rid = generate_run_id()
    assert rid == existing


def test_generate_run_id_truncates_long_hostname(monkeypatch):
    """长 FQDN hostname 应被截断到 ≤24 字符."""
    import socket as _socket
    monkeypatch.delenv("NEWS_PROCESS_RUN_ID", raising=False)
    monkeypatch.setattr(_socket, "gethostname",
                         lambda: "very.long.fqdn.example.subdomain.host.com")
    rid = generate_run_id()
    # 按 '-' 切分: ts, host(≤24 字符), pid
    parts = rid.split("-")
    # ts 含 '-' 否, 这里需更稳健解析: pid 是 trailing 数字, host 是其前
    pid = parts[-1]
    assert pid.isdigit()
    # ts + host + pid; ts 已知 16 字符 (含一个 'T'); host = rid[16:-len('-'+pid)] without 2 dashes
    # 更直接: rid 长度 = 16 + 1 + len(host) + 1 + len(pid); host = rid[17:-len(pid)-1]
    host = rid[17:-len(pid) - 1]
    assert len(host) <= 24
    assert "." not in host  # split('.') 后取第一段


def test_module_exports_generate_run_id():
    """__all__ 锁定单一 public name."""
    import news_process.core.run_id as mod
    assert mod.__all__ == ["generate_run_id"]
