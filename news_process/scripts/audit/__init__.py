"""news_process.scripts.audit — manual audit/verification scripts.

Each script in this package is intended to be run as a one-off check via
``python -m news_process.scripts.audit.<script_name>``.  They are NOT
pytest-discoverable: their module-level execution model (sys.exit on
failure, top-level statements) is incompatible with pytest collection.

Phase 4e (2026-05-04) established this directory as the home for such
non-pytest-discoverable audit scripts (originally to host scripts that
invoked ``sys.exit(1)`` at module load time and crashed pytest collection).

Phase 9c (Phase 9 baseline) removed several entries here (``audit_changes``
/ ``final_integrity``) once their grep targets — Phase 7a thin shims —
emptied of the strings they checked, leaving them as dead code. The
remaining ``audit_deep`` still verifies canonical core API and is kept.
"""
