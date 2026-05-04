"""tests/integration/test_dag_consistency.py — Phase 1.7 交付物。

校验两条流水线编排器均消费 ``news_process.core.dag`` 中的规范 DAG 声明,
而非各自维护平行阶段列表。此为重整方案所要求的*单一真源*检验,
用于杜绝历史上「双轨编排」反模式 (见 ``news_process-restructure-blueprint`` §1 缺陷 #1)。

断言三条性质:

1. ``run_pipeline_function.STAGES is core.dag.STAGES_MAIN`` (对象同一性)
2. ``run_pipeline_validation.STAGES is core.dag.STAGES_VALIDATION``
3. 任一 ``StageSpec.enabled_when`` 须为 ``core.dag`` 模块级谓词之一;
   从而防止未来误将新 ``lambda`` 内联进 ``StageSpec``、导致跨模块 ``is`` 校验失效。
"""

from __future__ import annotations

import importlib.util as _iu
import os
import sys

import pytest


# ---------------------------------------------------------------------------
# 测试夹具
# ---------------------------------------------------------------------------


def _news_process_dir() -> str:
    """返回 ``news_process/`` 目录路径 (tests 目录的上级之上级)。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_orchestrator(filename: str, module_name: str):
    """按文件路径加载编排器模块, 不执行 ``main()``。"""
    path = os.path.join(_news_process_dir(), filename)
    spec = _iu.spec_from_file_location(module_name, path)
    mod = _iu.module_from_spec(spec)
    sys.modules[module_name] = mod
    # 预设 NEWS_PROCESS_RUN_ID, 避免日志目录解析污染宿主环境。
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
# 测试用例
# ---------------------------------------------------------------------------


def test_main_orchestrator_uses_canonical_stages(rpf, core_dag):
    """``run_pipeline_function.STAGES`` 必须与 ``core.dag.STAGES_MAIN`` 对象同一。"""
    assert hasattr(rpf, "STAGES"), \
        "run_pipeline_function 须在模块级暴露 STAGES (Phase 1.3 上收)"
    assert rpf.STAGES is core_dag.STAGES_MAIN, (
        "run_pipeline_function.STAGES 与 core.dag.STAGES_MAIN 非同一对象 "
        "(检测到双轨编排回归)。"
    )


def test_validation_orchestrator_uses_canonical_stages(rpv, core_dag):
    """``run_pipeline_validation.STAGES`` 必须与 ``core.dag.STAGES_VALIDATION`` 同一。"""
    assert hasattr(rpv, "STAGES"), \
        "run_pipeline_validation 须在模块级暴露 STAGES (Phase 1.3 上收)"
    assert rpv.STAGES is core_dag.STAGES_VALIDATION, (
        "run_pipeline_validation.STAGES 与 core.dag.STAGES_VALIDATION 非同一对象。"
    )


def test_main_stage_count(core_dag):
    """``STAGES_MAIN`` 阶段数须等于 Phase 1 基线 (11)。"""
    # 00 + 11 + 12 + 14 + 15 + 21 + 22 + 23 + 24 + 45 + 51 = 11
    assert len(core_dag.STAGES_MAIN) == 11, (
        f"STAGES_MAIN 数量漂移: 期望 11, 实际 {len(core_dag.STAGES_MAIN)}. "
        "若有意增删阶段, 请同步更新本测试。"
    )


def test_validation_stage_count(core_dag):
    """``STAGES_VALIDATION`` 阶段数须等于 Phase 1 验证基线 (12)。"""
    # 31 + 32 + 32a + 33 + 34 + 35 + 36 + 37 + 38 + 38a + 38b + 39 = 12
    assert len(core_dag.STAGES_VALIDATION) == 12, (
        f"STAGES_VALIDATION drift: expected 12, got {len(core_dag.STAGES_VALIDATION)}."
    )


def test_predicate_identity_module_scope(core_dag):
    """任一 ``StageSpec.enabled_when`` 须为 ``core.dag`` 模块级可调用对象。

    防止将新 ``lambda`` 内联进 ``StageSpec``, 导致跨模块 ``is`` 一致性检查失效。
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
            f"STAGES_MAIN[{spec.name}].enabled_when 非已知模块级谓词; 得到 {spec.enabled_when!r}"
        )

    for spec in core_dag.STAGES_VALIDATION:
        assert spec.enabled_when in expected_predicates, (
            f"STAGES_VALIDATION[{spec.name}].enabled_when 非已知模块级谓词; "
            f"得到 {spec.enabled_when!r}"
        )


def test_filter_enabled_respects_predicate(core_dag):
    """``filter_enabled()`` 须正确应用 ``enabled_when`` 谓词。"""
    # 三种情感方法全开 -> 11 阶段
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 11

    # 仅 LLM -> 11 - 2 = 9
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 9

    # 无情感方法 -> 11 - 3 = 8
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 8
    )
