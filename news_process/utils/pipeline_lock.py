"""utils.pipeline_lock — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.locking``.
"""

from __future__ import annotations

import os as _os
import sys as _sys
import warnings as _warnings

_PROJECT_PARENT = _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in _sys.path:
    _sys.path.insert(0, _PROJECT_PARENT)

_warnings.warn(
    "utils.pipeline_lock is deprecated; import from news_process.core.locking. "
    "Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.locking import PipelineLock  # noqa: E402,F401

__all__ = ["PipelineLock"]
