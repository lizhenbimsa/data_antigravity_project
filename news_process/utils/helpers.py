"""utils.helpers — DEPRECATED forward shim (Phase 1 compatibility layer).

The 632-line monolith that used to live here was split during Phase 1 of
the news_process restructuring into eight focused modules under
``news_process.core``.  This file is preserved as a thin re-export shim so
that the 30+ existing call sites of the form ``from utils.helpers import X``
keep working until Phase 3 deprecation removal.

New code SHOULD import from the canonical locations:

    from news_process.core.config    import load_config
    from news_process.core.logging   import setup_logging, log_and_time, \
                                            log_memory_usage, log_stage_summary
    from news_process.core.parallel  import parallelize_dataframe
    from news_process.core.reporting import save_dataset, safe_save_preview_csv
    from news_process.core.stage     import run_stage
"""

from __future__ import annotations

import warnings as _warnings

# Inject project root onto sys.path so that ``import news_process`` works
# whether this module is reached via ``utils.helpers`` (legacy CWD-relative)
# or any other entrypoint.
import os as _os
import sys as _sys
_PROJECT_PARENT = _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in _sys.path:
    _sys.path.insert(0, _PROJECT_PARENT)

_warnings.warn(
    "utils.helpers is deprecated; import from news_process.core.* instead "
    "(see module docstring for the new mapping). Slated for removal in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)


# Forward every public name historically exported from this module.
from news_process.core.config import load_config  # noqa: E402,F401
from news_process.core.logging import (  # noqa: E402,F401
    _ColoredFormatter,
    log_and_time,
    log_memory_usage,
    log_stage_summary,
    setup_logging,
)
from news_process.core.parallel import parallelize_dataframe  # noqa: E402,F401
from news_process.core.reporting import (  # noqa: E402,F401
    safe_save_preview_csv,
    save_dataset,
)
from news_process.core.stage import run_stage  # noqa: E402,F401


__all__ = [
    "load_config",
    "setup_logging",
    "log_memory_usage",
    "log_stage_summary",
    "safe_save_preview_csv",
    "save_dataset",
    "log_and_time",
    "parallelize_dataframe",
    "run_stage",
    "_ColoredFormatter",
]
