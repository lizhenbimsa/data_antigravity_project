"""news_process.validation — robustness / validation stage implementations.

Current status (Phase 7b migration completed)
----------------------------------------------
The Phase 7b migration is done: the canonical bodies of the validation
stages now live in this package (e.g. ``temporal_mask.py``,
``decay_sensitivity.py``, ``radius_sensitivity.py``, ``threshold.py``,
``tone_validation.py``, ``media_diversity.py``, ``dedup_threshold.py``,
``entity_masking.py``, ``prompt_sensitivity.py`` 等)。每个模块顶部均带有
"本模块由原 root script ... 迁入 (Phase 7b)" 的迁移说明。

The project-root ``NN_*.py`` files for these stages are thin ``importlib``
shims that delegate to the modules here; the validation pipeline discovers
them via ``run_pipeline_validation.py`` consuming
``news_process.core.dag.STAGES_VALIDATION``.

Notes
-----
1. ``import news_process.validation`` resolves immediately; the modules are
   importable directly (e.g. ``python -m news_process.validation.temporal_mask``).
2. The directory is a contract marker — changes to it are localised to a
   single sub-tree, not the project root.
"""
