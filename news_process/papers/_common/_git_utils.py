"""news_process.papers._common._git_utils — Git commit-hash helper.

Q1.4 (post-P4 cleanup, 2026-05-15) — Extracted from
``stata_runner._get_git_commit_hash_with_dirty`` to break a circular import
between ``stata_runner`` and ``derivative_replication`` after the
``_PAPER_DEFAULTS`` single-source-of-truth consolidation.

Why a separate module
---------------------
Before Q1.4:
- ``derivative_replication.py`` imports ``stata_runner._get_git_commit_hash_with_dirty``
- ``stata_runner.py._PAPER_DEFAULTS`` had a redundant duplicate of
  ``derivative_replication._PAPER_DEFAULTS`` (4 derivative papers).

If we let ``stata_runner.py`` import from ``derivative_replication`` to
remove the duplicate, ``stata_runner`` ↔ ``derivative_replication`` would
form a cycle.

Solution: extract the commit-hash helper into this leaf-utility module.
Both ``stata_runner`` and ``derivative_replication`` import from here.
No upward dependencies → no cycle.
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
        # Three levels up: this file → _common → papers → news_process → repo_root.
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


# Backward-compat alias for stata_runner internal callers.
# stata_runner.py used to define this as `_get_git_commit_hash_with_dirty`;
# Q1.4 keeps that name resolvable via `from _git_utils import _get_git_commit_hash_with_dirty`.
_get_git_commit_hash_with_dirty = get_git_commit_hash_with_dirty


__all__ = [
    'get_git_commit_hash_with_dirty',
    '_get_git_commit_hash_with_dirty',  # legacy underscore name
]
