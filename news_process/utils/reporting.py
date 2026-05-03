"""utils.reporting — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.reporting``.

Historically this file held DataFrame analysis helpers; ``utils.helpers``
held dataset persistence; ``utils.pipeline_reporting`` held end-of-run
summaries. Phase 1 merges all three concerns into ``core.reporting``.
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
    "utils.reporting is deprecated; import from news_process.core.reporting. "
    "Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.reporting import (  # noqa: E402,F401
    _format_stat,
    _is_categorical,
    generate_dataframe_report,
)

__all__ = [
    "_format_stat",
    "_is_categorical",
    "generate_dataframe_report",
]
