"""utils.llm_cache — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.caching``.
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
    "utils.llm_cache is deprecated; import from news_process.core.caching. "
    "Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.caching import LLMCache  # noqa: E402,F401

__all__ = ["LLMCache"]
