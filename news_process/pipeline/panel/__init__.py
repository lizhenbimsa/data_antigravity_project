"""news_process.pipeline.panel — Stages 41-48 + monolithic 45 -> bank-year panel.

Phase 1: stages 41-48 + 45 stay at the project root (importlib reflection
preserves their locations).
Phase 2a: library files (41/42/43/44/46/47/48) migrate here renamed; 45's body
moves into ``runner.py`` (still monolithic 2680 lines); the 13 importlib
reflections are atomically replaced with proper imports.
Phase 2b: ``runner.py`` is split into ``runner.py`` (<=500 lines orchestration)
+ ``extras.py`` (<=700 lines: washing-ratio / JF / disag / algo_cater)
+ ``export.py`` (<=300 lines: parquet/Stata + log_diagnostics).
Phase 2c: 51's shared panel-assembly logic extracted into
``falsification_helpers.py`` (physical isolation from runner.py).
"""
