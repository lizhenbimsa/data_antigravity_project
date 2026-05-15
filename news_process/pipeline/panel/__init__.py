"""news_process.pipeline.panel — Stages 41-48 + monolithic 45 -> bank-year panel.

Phase 1: stages 41-48 + 45 stayed at the project root (importlib reflection
preserves their locations).
Phase 2a: library files (41/42/43/44/46/47/48) migrated here renamed; 45's body
moved into ``runner.py``; the 13 importlib reflections were atomically replaced
with proper imports.
Phase 2b (originally planned ``runner.py`` <=500 / ``extras.py`` <=700 /
``export.py`` <=300 行拆分) **未执行**; ``runner.py`` 与 ``export.py`` 至今
仍是 monolithic god function, 待 Plan-r3 P1-7 真正落地。
Phase 2c: 51's shared panel-assembly logic extracted into
``falsification_helpers.py`` (physical isolation from runner.py).
"""
