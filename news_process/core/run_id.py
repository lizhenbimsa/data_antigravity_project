"""news_process.core.run_id — 运行 ID 生成与复用。

提供唯一的 ``generate_run_id()`` 接口,
供 ``run_pipeline_function.py`` 与 ``run_pipeline_validation.py`` 复用。
"""

from __future__ import annotations

import datetime as _dt
import os
import socket as _socket


def generate_run_id() -> str:
    """生成本次运行的唯一标识符, 并写入环境变量供子进程继承。

    格式: ``YYYYMMDDTHHMMSSZ-<hostname>-<pid>``, 例如
    ``20260503T231245Z-DESKTOP-1234``。

    若环境变量 ``NEWS_PROCESS_RUN_ID`` 已存在 (例如上游 CI 已注入),
    则原样保留; 否则生成新值。
    """
    existing = os.environ.get("NEWS_PROCESS_RUN_ID")
    if existing:
        return existing

    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    host = _socket.gethostname().split(".")[0][:24]  # 截断过长 FQDN
    rid = f"{ts}-{host}-{os.getpid()}"
    os.environ["NEWS_PROCESS_RUN_ID"] = rid
    return rid


__all__ = ["generate_run_id"]
