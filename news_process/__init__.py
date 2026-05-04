"""news_process — bank-fintech news to bank-year panel pipeline package.

This file makes the project root a real Python package, enabling
``import news_process.<sub>`` from any cwd. See the project root README.md
for the layered topology (core / pipeline / papers / config split / etc.)
and CHANGELOG.md for the phase-by-phase architectural evolution.

Phase 6 baseline (2026-05-04): root scripts + orchestrators migrated
from utils.* to canonical news_process.core.*; news_process/utils/
forward-shim package deleted (v2.0 promise fulfilled). Full pytest
778 passed / 7 skipped / 0 failed.
"""

__version__ = "0.6.0-phase6"
