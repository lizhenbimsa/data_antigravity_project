"""news_process — bank-fintech news to bank-year panel pipeline package.

This file makes the project root a real Python package, enabling
``import news_process.<sub>`` from any cwd. See the project root README.md
for the layered topology (core / pipeline / papers / papers_assets /
validation / config split / etc.) and CHANGELOG.md for the phase-by-phase
architectural evolution.

v2.0.0 / phase-8-baseline (2026-05-04): the full restructuring program
(Phases 0 → 8) is complete. End state:
  - 26 numeric-prefix root scripts: all ≤30-line thin shims
  - news_process.{core, pipeline, papers, validation, scripts, config}:
    full canonical layout, single declarative DAG (core/dag.py)
  - 7-domain split config + externalized prompts
  - Multi-paper productization (papers/ + papers_assets/)
  - Data layout normalized: data_processed/ → data/processed/ (Phase 8)
  - Full pytest: 778 passed / 7 skipped / 0 failed.
"""

__version__ = "2.0.0"
