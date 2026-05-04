"""news_process — bank-fintech news to bank-year panel pipeline package.

This file makes the project root a real Python package, enabling
``import news_process.<sub>`` from any cwd. See the project root README.md
for the layered topology (core / pipeline / papers / config split / etc.)
and CHANGELOG.md for the phase-by-phase architectural evolution.

Phase 5 baseline (2026-05-04): pipeline/ + tests/ migrated from utils.*
to canonical news_process.core.*; full pytest 778 passed / 7 skipped /
0 failed; project root README + CHANGELOG materialized.
"""

__version__ = "0.5.0-phase5"
