"""news_process.pipeline — main line: news -> bank-year panel.

Sub-packages: preprocess, filtering, sentiment, features, panel,
falsification, audit. Stage runners live under each sub-package and
emit a ``main()`` entrypoint consumed by both the legacy root-level
shim (e.g. ``00_preprocessing.py``) and the new ``cli`` orchestrator.
"""
