"""tests/integration/test_dag_consistency.py — Phase 1.7 deliverable.

Verifies that the two pipeline orchestrators consume the canonical DAG
declarations from ``news_process.core.dag`` rather than maintaining their
own parallel stage lists.  This is the *single-source* check the plan
identifies as the antidote to the legacy "double-orchestration" antipattern
(see ``news_process-restructure-blueprint`` plan §1 defect #1).

Three properties are asserted:

1. ``run_pipeline_function.STAGES is core.dag.STAGES_MAIN``  (object identity)
2. ``run_pipeline_validation.STAGES is core.dag.STAGES_VALIDATION``
3. Every ``StageSpec.enabled_when`` is one of the module-scope predicates
   in ``core.dag``; this rules out a future regression where someone
   accidentally inlines a fresh ``lambda`` predicate that would defeat the
   ``is`` check.
"""

from __future__ import annotations

import importlib.util as _iu
import os
import sys

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _news_process_dir() -> str:
    """Return the news_process/ directory (parent-of-tests-dir)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_orchestrator(filename: str, module_name: str):
    """Load an orchestrator module by file path without exec-ing main()."""
    path = os.path.join(_news_process_dir(), filename)
    spec = _iu.spec_from_file_location(module_name, path)
    mod = _iu.module_from_spec(spec)
    sys.modules[module_name] = mod
    # Ensure NEWS_PROCESS_RUN_ID is set so log dir resolution doesn't pollute.
    os.environ.setdefault("NEWS_PROCESS_RUN_ID", "test_dag_consistency")
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def core_dag():
    from news_process.core import dag as _d
    return _d


@pytest.fixture(scope="module")
def rpf():
    return _load_orchestrator("run_pipeline_function.py", "_dagtest_rpf")


@pytest.fixture(scope="module")
def rpv():
    return _load_orchestrator("run_pipeline_validation.py", "_dagtest_rpv")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_main_orchestrator_uses_canonical_stages(rpf, core_dag):
    """run_pipeline_function.STAGES MUST be core.dag.STAGES_MAIN by identity."""
    assert hasattr(rpf, "STAGES"), \
        "run_pipeline_function must expose module-level STAGES (Phase 1.3 lift)"
    assert rpf.STAGES is core_dag.STAGES_MAIN, (
        "run_pipeline_function.STAGES is NOT identical to core.dag.STAGES_MAIN "
        "(double-orchestration regression detected)."
    )


def test_validation_orchestrator_uses_canonical_stages(rpv, core_dag):
    """run_pipeline_validation.STAGES MUST be core.dag.STAGES_VALIDATION."""
    assert hasattr(rpv, "STAGES"), \
        "run_pipeline_validation must expose module-level STAGES (Phase 1.3 lift)"
    assert rpv.STAGES is core_dag.STAGES_VALIDATION, (
        "run_pipeline_validation.STAGES is NOT identical to "
        "core.dag.STAGES_VALIDATION."
    )


def test_main_stage_count(core_dag):
    """STAGES_MAIN should declare exactly the legacy stage set (Phase 1 baseline = 11)."""
    # 00 + 11 + 12 + 14 + 15 + 21 + 22 + 23 + 24 + 45 + 51 = 11
    assert len(core_dag.STAGES_MAIN) == 11, (
        f"STAGES_MAIN drift: expected 11, got {len(core_dag.STAGES_MAIN)}. "
        "Update this test if a stage was intentionally added/removed."
    )


def test_validation_stage_count(core_dag):
    """STAGES_VALIDATION should declare exactly the legacy validation stage set (Phase 1 baseline = 12)."""
    # 31 + 32 + 32a + 33 + 34 + 35 + 36 + 37 + 38 + 38a + 38b + 39 = 12
    assert len(core_dag.STAGES_VALIDATION) == 12, (
        f"STAGES_VALIDATION drift: expected 12, got {len(core_dag.STAGES_VALIDATION)}."
    )


def test_predicate_identity_module_scope(core_dag):
    """Every StageSpec.enabled_when MUST be a module-scope callable in core.dag.

    This rules out the regression where someone inlines a fresh ``lambda``
    in a StageSpec, which would defeat ``is`` comparisons in cross-module
    consistency checks.
    """
    expected_predicates = {
        core_dag.always_enabled,
        core_dag.llm_method_enabled,
        core_dag.words_method_enabled,
        core_dag.berts_method_enabled,
        core_dag.temporal_mask_enabled,
    }
    expected_predicates.update(core_dag._VALIDATION_PREDS.values())

    for spec in core_dag.STAGES_MAIN:
        assert spec.enabled_when in expected_predicates, (
            f"STAGES_MAIN[{spec.name}].enabled_when is not a known module-scope "
            f"predicate; got {spec.enabled_when!r}"
        )

    for spec in core_dag.STAGES_VALIDATION:
        assert spec.enabled_when in expected_predicates, (
            f"STAGES_VALIDATION[{spec.name}].enabled_when is not a known "
            f"module-scope predicate; got {spec.enabled_when!r}"
        )


def test_filter_enabled_respects_predicate(core_dag):
    """filter_enabled() must respect enabled_when predicates."""
    # All sentiment methods enabled -> 11 stages
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 11

    # Only LLM enabled -> 11 - 2 = 9
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 9

    # No sentiment methods -> 11 - 3 = 8
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 8
    )
