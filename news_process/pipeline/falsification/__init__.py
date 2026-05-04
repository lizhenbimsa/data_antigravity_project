"""news_process.pipeline.falsification — Stage 51 falsification test.

Phase 2c migrated the body of ``51_falsification_test.py`` here as
``controls.py``; the project-root file remains as a thin CLI shim.

Phase 4c (2026-05-04) further extracted the 1016-line embedded Stata
regression template to
``papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl``,
shrinking ``controls.py`` from 2141 to 1135 lines.

Phase 4c also explicitly *cancelled* the originally-planned Phase 2c-2
helper-split sub-task: the ``build_non_fintech``,
``aggregate_non_fintech``, ``merge_to_panel`` functions inside
``controls.py`` are falsification-specific (not cross-paper helpers), so
relocating them to ``pipeline/panel/falsification_helpers.py`` would not
increase reusability.  ``controls.py`` therefore remains the single home
for stage 51's logic.
"""
