"""utils — DEPRECATED legacy compatibility namespace.

This package was the project's original "shared utilities" home.  During
Phase 1 of the news_process restructuring its contents were re-homed under
``news_process.core``.  Each ``utils/<module>.py`` is preserved as a thin
forward shim that re-exports its canonical replacement; this ``__init__``
keeps the convenience symbol set ``from utils import X`` working.

Migration mapping:

    utils.helpers           -> news_process.core.{config,logging,parallel,reporting,stage}
    utils.pipeline_lock     -> news_process.core.locking
    utils.llm_cache         -> news_process.core.caching
    utils.data_quality      -> news_process.core.quality
    utils.aho_corasick      -> news_process.core.text.ahocorasick
    utils.canonicalization  -> news_process.core.text.canonicalization
    utils.entity_context    -> news_process.core.text.entity_context
    utils.reporting         -> news_process.core.reporting
    utils.pipeline_reporting-> news_process.core.reporting
    utils.extract_papers    -> archived to scripts/legacy/ (orphan)
    utils.schema_validator  -> archived to scripts/legacy/ (orphan)

The forward shims emit ``DeprecationWarning``; they will be removed in v2.0.
"""

from __future__ import annotations

# Forward the historically exported symbols.
# Each underlying utils.<X> shim re-exports from news_process.core.* —
# importing here lets ``from utils import load_config`` continue working
# alongside the explicit ``from utils.helpers import load_config``.
from utils.helpers import (  # noqa: F401
    load_config,
    setup_logging,
    log_memory_usage,
    log_stage_summary,
    safe_save_preview_csv,
    save_dataset,
    log_and_time,
    parallelize_dataframe,
    run_stage,
)

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
]
