"""news_process.core — shared kernel.

Replaces the legacy `utils/helpers.py` mega-module. Provides config loading,
logging, parallelism, locking, caching, schemas, etc., to all upstream modules.

Each public utility's canonical home is documented in the module-level docstring;
the legacy `utils/<module>.py` paths remain importable as forward shims during
the compatibility window (Phase 1 -> 3).
"""
