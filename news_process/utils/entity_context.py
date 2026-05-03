"""utils.entity_context — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.text.entity_context``.
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
    "utils.entity_context is deprecated; import from "
    "news_process.core.text.entity_context.  Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.text.entity_context import *  # noqa: E402,F401,F403
from news_process.core.text import entity_context as _src  # noqa: E402

# Re-export ALL symbols (including ``_split_sentences`` / ``_merge_intervals``
# referenced directly by tests/test_content_ctx_materialization.py).
for _name in dir(_src):
    if _name not in {"__name__", "__doc__", "__package__", "__loader__",
                     "__spec__", "__file__", "__builtins__", "__cached__"}:
        globals()[_name] = getattr(_src, _name)
del _src, _name
