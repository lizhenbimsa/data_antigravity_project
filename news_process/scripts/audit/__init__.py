"""news_process.scripts.audit — manual audit/verification scripts.

Each script in this package is intended to be run as a one-off check via
``python -m news_process.scripts.audit.<script_name>``.  They are NOT
pytest-discoverable: their module-level execution model (sys.exit on
failure, top-level statements) is incompatible with pytest collection.

Phase 4e (2026-05-04) relocated ``audit_changes.py`` here from
``tests/test_audit_changes.py`` for exactly this reason — pytest was
crashing during collection because the file invoked ``sys.exit(1)`` at
module load time.
"""
