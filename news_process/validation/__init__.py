"""news_process.validation — placeholder package for future Phase 5+ scope.

Current status (Phase 4g, 2026-05-04)
-------------------------------------
This package is intentionally **empty**.  It exists as a namespace anchor
for a future phase that may relocate stages 31-39
(``31_bank_fintech_threshold.py`` … ``39_prompt_sensitivity.py``) here from
the news_process root.

As of Phase 4 those stages remain at the project root as thin
``importlib`` shims; the canonical bodies live under
``news_process/`` (still named with the legacy 31-39 prefix) and are
discovered via ``run_pipeline_validation.py`` consuming
``news_process.core.dag.STAGES_VALIDATION``.

Why preserve the empty package?
-------------------------------
1. ``import news_process.validation`` resolves immediately, so any future
   stage migration into this package is non-breaking.
2. The directory is a contract marker — changes to it are localised to a
   single sub-tree, not the project root.
3. Phase 4g audit confirmed there are zero external imports of this
   package, so reserving it costs nothing.
"""
