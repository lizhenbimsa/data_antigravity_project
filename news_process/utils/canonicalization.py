"""utils.canonicalization — DEPRECATED forward shim (Phase 1).

Canonical location: ``news_process.core.text.canonicalization``.
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
    "utils.canonicalization is deprecated; import from "
    "news_process.core.text.canonicalization.  Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

from news_process.core.text.canonicalization import *  # noqa: E402,F401,F403
from news_process.core.text import canonicalization as _src  # noqa: E402

# Re-export ALL symbols (including private helpers like ``_normalize_text``)
# because some tests legitimately reach into the private API.
for _name in dir(_src):
    if _name not in {"__name__", "__doc__", "__package__", "__loader__",
                     "__spec__", "__file__", "__builtins__", "__cached__"}:
        globals()[_name] = getattr(_src, _name)
del _src, _name
