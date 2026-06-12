"""news_process.papers._common._git_utils — Git commit-hash helper。

Q1.4 (post-P4 cleanup, 2026-05-15) — 从
``stata_runner._get_git_commit_hash_with_dirty`` 抽出, 以打破
``_PAPER_DEFAULTS`` 单源化合并后 ``stata_runner`` 与
``derivative_replication`` 之间的循环 import。

为什么独立成模块
---------------------
Q1.4 之前:
- ``derivative_replication.py`` import ``stata_runner._get_git_commit_hash_with_dirty``
- ``stata_runner.py._PAPER_DEFAULTS`` 冗余复制了一份
  ``derivative_replication._PAPER_DEFAULTS`` (4 篇衍生论文)。

若让 ``stata_runner.py`` 反过来从 ``derivative_replication`` import 来
消除重复, ``stata_runner`` ↔ ``derivative_replication`` 就会成环。

解法: 把 commit-hash helper 抽到这个叶子工具模块,
``stata_runner`` 与 ``derivative_replication`` 都从这里 import。
本模块无任何向上依赖 → 无环。
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_git_commit_hash_with_dirty() -> str:
    """Plan v14 §9.3 (R48-A + R49-A): git commit hash + dirty 检测.

    Returns:
        '<hash>' (clean) 或 '<hash>+dirty' (working tree dirty);
        'unknown' (no git / no repo / timeout / etc.)
    """
    try:
        # 向上四级: 本文件 → _common → papers → news_process → repo_root。
        repo_root = Path(__file__).resolve().parents[3]
        h = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        ).stdout.strip()[:12]
        dirty = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        return f'{h}+dirty' if dirty else h
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return 'unknown'


# 供 stata_runner 内部调用方的向后兼容别名。
# stata_runner.py 原本以 `_get_git_commit_hash_with_dirty` 之名定义此函数;
# Q1.4 保留该名可经 `from _git_utils import _get_git_commit_hash_with_dirty` 解析。
_get_git_commit_hash_with_dirty = get_git_commit_hash_with_dirty


__all__ = [
    'get_git_commit_hash_with_dirty',
    '_get_git_commit_hash_with_dirty',  # 遗留下划线旧名
]
