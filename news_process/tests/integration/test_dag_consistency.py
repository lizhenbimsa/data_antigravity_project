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
    """``filter_enabled()`` 须正确应用 ``enabled_when`` 谓词。

    Plan P1-4 后的预期更新: stage 24 (herd_decay) 增加
    ``enabled_when=berts_method_enabled`` 谓词, 与 stage 23 同步启停.
    因此 cfg_llm_only / cfg_no_sentiment 下被排除的 stage 数 +1.
    """
    # 三种情感方法全开 -> 12 阶段 (v6 红队修复: 含 stage 30 / Step 3a)
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 12

    # 仅 LLM -> 12 - 2 (words+berts) - 1 (24 跟随 berts) = 9
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 9

    # 无情感方法 -> 12 - 3 (llm+words+berts) - 1 (24 跟随 berts) = 8
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 8
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
        EXPECTED_NO_OUTPUT_STAGES,
        OUTPUT_REGISTRY,
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

    Plan P1-4 修订: stage 24 (24_herd_decay_processor.py) kind='sentiment'
    现在 enabled_when=berts_method_enabled (原为 always_enabled).
    它复用与 stage 23 相同的 berts 谓词, 故集合层面 sentiment_predicates
    仍是 {llm, words, berts} = METHOD_TO_PREDICATE.values() (集合自动去重).
    本测试不变, 通过.
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


# ===========================================================================
# recode 加固: 三项 schemas.py 不变式的破坏性测试 (验证守护机制本身有效)
# ===========================================================================


def test_recode_invariant_detects_dup_within_stage_outputs(monkeypatch):
    """recode 加固校验 2: OUTPUT_REGISTRY 内重复文件名必须被 invariant 捕获.

    精确隔离: 同步 _OUTPUT_FILENAME_KEYS 让校验 1 (双向覆盖) 通过 — 必须
    既加新 (script, "a.parquet") key 又删除被替换的原 (script, "00_preprocessing.parquet") key,
    才能让 expected ↔ actual 完全匹配, 从而走到校验 2.
    """
    from news_process.core import schemas

    bad_registry = dict(schemas.OUTPUT_REGISTRY)
    bad_registry["00_preprocessing.py"] = ["a.parquet", "a.parquet"]
    monkeypatch.setattr(schemas, 'OUTPUT_REGISTRY', bad_registry)

    # 同步 _OUTPUT_FILENAME_KEYS: 删除原 key + 加新 key, 让校验 1 通过, 隔离校验 2
    bad_keys = dict(schemas._OUTPUT_FILENAME_KEYS)
    del bad_keys[("00_preprocessing.py", "00_preprocessing.parquet")]
    bad_keys[("00_preprocessing.py", "a.parquet")] = "output_dup"
    monkeypatch.setattr(schemas, '_OUTPUT_FILENAME_KEYS', bad_keys)

    with pytest.raises(RuntimeError, match=r"列表内有重复文件名"):
        schemas._validate_registry_invariant()


def test_recode_invariant_detects_overlap_with_no_output_set(monkeypatch):
    """recode 加固校验 3: OUTPUT_REGISTRY 与 EXPECTED_NO_OUTPUT_STAGES 重叠必须被捕获."""
    from news_process.core import schemas

    overlapping = frozenset(schemas.EXPECTED_NO_OUTPUT_STAGES) | {"00_preprocessing.py"}
    monkeypatch.setattr(schemas, 'EXPECTED_NO_OUTPUT_STAGES', overlapping)

    with pytest.raises(RuntimeError, match=r"必须为空, 实际重叠"):
        schemas._validate_registry_invariant()


def test_recode_invariant_detects_missing_filename_key(monkeypatch):
    """recode 加固校验 1 的回归测试 (双向覆盖): 在 OUTPUT_REGISTRY 加新 entry
    但不同步 _OUTPUT_FILENAME_KEYS, 必须被捕获."""
    from news_process.core import schemas

    bad_registry = dict(schemas.OUTPUT_REGISTRY)
    bad_registry["999_phantom.py"] = ["phantom.parquet"]
    monkeypatch.setattr(schemas, 'OUTPUT_REGISTRY', bad_registry)

    with pytest.raises(RuntimeError, match=r"missing="):
        schemas._validate_registry_invariant()


def test_recode_invariant_detects_cross_stage_filename_collision(monkeypatch):
    """recode round 2 校验 4: 同一 parquet 文件名出现在两个 stage 必须被捕获.

    精确隔离: 让 21_tone_llms.py 与 22_tone_words.py 都声明 'shared.parquet'.
    校验 1 (双向覆盖) 通过: _OUTPUT_FILENAME_KEYS 用复合 key 同时登记两条.
    校验 2 (列表内去重) 通过: 每个 list 内仍唯一.
    校验 3 (互斥) 通过: 与 EXPECTED 无重叠.
    → 校验 4 必须捕获.
    """
    from news_process.core import schemas

    bad_registry = dict(schemas.OUTPUT_REGISTRY)
    bad_registry["21_tone_llms.py"] = ["shared.parquet"]
    bad_registry["22_tone_words.py"] = ["shared.parquet"]
    monkeypatch.setattr(schemas, 'OUTPUT_REGISTRY', bad_registry)

    # 同步 _OUTPUT_FILENAME_KEYS 让校验 1 通过, 隔离校验 4
    bad_keys = dict(schemas._OUTPUT_FILENAME_KEYS)
    # 删除原 21/22 的 entry
    del bad_keys[("21_tone_llms.py", "21_tone_llms.parquet")]
    del bad_keys[("21_tone_llms.py", "21_tone_llms_full.parquet")]
    del bad_keys[("22_tone_words.py", "22_words_tone.parquet")]
    # 加新的 entry, 用唯一的 filename_key 让校验 5 也通过
    bad_keys[("21_tone_llms.py", "shared.parquet")] = "output_shared_a"
    bad_keys[("22_tone_words.py", "shared.parquet")] = "output_shared_b"
    monkeypatch.setattr(schemas, '_OUTPUT_FILENAME_KEYS', bad_keys)

    with pytest.raises(RuntimeError, match=r"跨 stage 出现重复 parquet 文件名"):
        schemas._validate_registry_invariant()


def test_recode_invariant_detects_filename_key_collision(monkeypatch):
    """recode round 2 校验 5: 两个 (script, filename) 共享同一 filename_key 必须被捕获.

    精确隔离: 让 22_tone_words.py 的 entry 借用 21_tone_llms.py 的 filename_key.
    校验 1-4 全部通过 (类型 / 列表 / 互斥 / 跨 stage 文件名都正确).
    → 校验 5 必须捕获.
    """
    from news_process.core import schemas

    bad_keys = dict(schemas._OUTPUT_FILENAME_KEYS)
    # 把 22_words_tone 的 filename_key 改成与 21_tone_llms 共享
    bad_keys[("22_tone_words.py", "22_words_tone.parquet")] = "output_21_tone_llms"
    monkeypatch.setattr(schemas, '_OUTPUT_FILENAME_KEYS', bad_keys)

    with pytest.raises(RuntimeError, match=r"filename_key 跨条目重复"):
        schemas._validate_registry_invariant()


def test_recode_invariant_allows_multiple_none_filename_keys(monkeypatch):
    """recode round 2 校验 5 边界: 多个 None filename_key 必须被允许 (不参与唯一性校验).

    现状已有 4 个 None 条目 (30_text2vec + 3 个 40_attn_index_*); 必须正常通过.
    本测试用未污染的 schemas 直接调用, 不抛即过.
    """
    from news_process.core import schemas
    schemas._validate_registry_invariant()  # 真实数据, 不抛 = 通过
