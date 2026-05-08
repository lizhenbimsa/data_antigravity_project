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
    """``STAGES_MAIN`` 阶段数须等于 Phase 1 基线 + Step 7a/v6 (12)。"""
    # 00 + 11 + 12 + 14 + 15 + 21 + 22 + 23 + 24 + 30 + 45 + 51 = 12
    # (v6 红队修复: 显式纳入 stage 30 双轨稳健性指标 / Step 3a)
    assert len(core_dag.STAGES_MAIN) == 12, (
        f"STAGES_MAIN 数量漂移: 期望 12, 实际 {len(core_dag.STAGES_MAIN)}. "
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
    # 三种情感方法全开 -> 12 阶段 (v6 红队修复: 含 stage 30 / Step 3a)
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 12

    # 仅 LLM -> 12 - 2 (words+berts) = 10
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 10

    # 无情感方法 -> 12 - 3 (llm+words+berts) = 9
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 9
    )


def test_stages_main_all_registered_in_output_registry(core_dag):
    """Phase 9d: STAGES_MAIN 中所有 stage 的 script 必须在 OUTPUT_REGISTRY 登记.

    9d 删除了 ``run_pipeline_function._get_stage_output_files`` 的历史 fallback
    dict, 任何 stage 缺登记会让陈旧文件预清理静默失效 (orchestrator 从
    ``_registry_outputs`` 拿到空列表). 本测试守护 STAGES_MAIN ↔
    OUTPUT_REGISTRY 一致性 — 与上方 ``test_main_orchestrator_uses_canonical_stages``
    一起构成 DAG ↔ orchestrator ↔ schemas registry 三角不变式.
    """
    from news_process.core.schemas import OUTPUT_REGISTRY

    missing = [s.script for s in core_dag.STAGES_MAIN
               if s.script not in OUTPUT_REGISTRY]
    assert not missing, (
        f"以下 STAGES_MAIN stage 未在 OUTPUT_REGISTRY 登记, "
        f"会让陈旧文件预清理失效: {missing}"
    )


def test_validation_stages_explicitly_marked_no_output(core_dag):
    """v3 / Fix 4: STAGES_VALIDATION 中所有 stage 必须显式归入两类之一.

    要么登记 OUTPUT_REGISTRY (产 parquet, 需预清理);
    要么列入 EXPECTED_NO_OUTPUT_STAGES (只产 eval_reports/*.csv, 跳过预清理).
    二者皆缺则 ``run_pipeline_function._get_stage_output_files`` 在 v3 后会
    raise RuntimeError, 杜绝"忘了登记导致陈旧文件预清理静默失效"的反模式.
    """
    from news_process.core.schemas import (
        OUTPUT_REGISTRY,
        EXPECTED_NO_OUTPUT_STAGES,
    )

    unaccounted = [
        s.script for s in core_dag.STAGES_VALIDATION
        if s.script not in OUTPUT_REGISTRY
        and s.script not in EXPECTED_NO_OUTPUT_STAGES
    ]
    assert not unaccounted, (
        f"以下 STAGES_VALIDATION stage 既未登记 OUTPUT_REGISTRY 也未列入 "
        f"EXPECTED_NO_OUTPUT_STAGES (Fix 4 后 orchestrator 会 raise): "
        f"{unaccounted}"
    )


def test_output_filename_keys_invariant():
    """v3 / Fix 5: import-time _validate_registry_invariant() 已校验,
    此处显式覆盖以保证未来不被静默回退 (例如有人删除该顶层调用).
    """
    from news_process.core import schemas
    schemas._validate_registry_invariant()  # 不抛即过


def test_method_to_predicate_covers_sentiment_specs(core_dag):
    """v3 / Fix 2: METHOD_TO_PREDICATE 必须覆盖 STAGES_MAIN 中所有
    kind='sentiment' 且非 always_enabled 的 stage 谓词, 反之亦然.

    stage 24 (24_herd_decay_processor.py) kind='sentiment' 但 enabled_when
    是 always_enabled (无配置开关), 故应被排除 — 它不属于"按方法名启停"
    的范畴.
    """
    sentiment_predicates = {
        s.enabled_when for s in core_dag.STAGES_MAIN
        if s.kind == 'sentiment' and s.enabled_when is not core_dag.always_enabled
    }
    map_predicates = set(core_dag.METHOD_TO_PREDICATE.values())
    assert sentiment_predicates == map_predicates, (
        f"METHOD_TO_PREDICATE 与 STAGES_MAIN sentiment specs 谓词集不一致; "
        f"STAGES_MAIN 独有: {sentiment_predicates - map_predicates}, "
        f"METHOD_TO_PREDICATE 独有: {map_predicates - sentiment_predicates}"
    )


def test_get_script_for_method_round_trip(core_dag):
    """v3 / Fix 2: METHOD_TO_PREDICATE 中所有 method 必须能反查到 STAGES_MAIN
    中的对应 script.
    """
    for method in core_dag.METHOD_TO_PREDICATE:
        script = core_dag.get_script_for_method(method)
        assert script is not None, (
            f"get_script_for_method({method!r}) 返回 None; "
            f"METHOD_TO_PREDICATE 与 STAGES_MAIN 之间存在漂移"
        )

    # 反向检查: 未登记 method 必须返回 None (不应误命中其他 stage)
    assert core_dag.get_script_for_method('totally_unknown_method') is None
