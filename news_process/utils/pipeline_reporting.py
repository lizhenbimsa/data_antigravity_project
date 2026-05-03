"""utils.pipeline_reporting — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.reporting``.
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
    "utils.pipeline_reporting is deprecated; import from "
    "news_process.core.reporting. Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.reporting import generate_pipeline_summary  # noqa: E402,F401

__all__ = ["generate_pipeline_summary"]
