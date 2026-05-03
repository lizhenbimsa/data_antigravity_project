"""utils.data_quality — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.quality``.
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
    "utils.data_quality is deprecated; import from news_process.core.quality. "
    "Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.quality import (  # noqa: E402,F401
    to_numeric_with_logging,
    validate_numeric_columns,
)

__all__ = ["to_numeric_with_logging", "validate_numeric_columns"]
