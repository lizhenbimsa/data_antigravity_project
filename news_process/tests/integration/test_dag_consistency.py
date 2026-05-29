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
    """``STAGES_MAIN`` 阶段数须等于 v3.7.0 + v2.3 计划增量 − stage 30 退役 (19)。"""
    # v3.7.0 baseline 15: 00 + 11 + 12 + 13 + 14 + 15 + 21 + 22 + 23 + 24 + 45 + 46 + 49 + 51 (+30 历史)
    # v3.2.0 M6: + stage 46 Stata 导出
    # v3.6.0 (Plan E P4 A1): + stage 13 content_ctx 物化, 让 14/15 双轨化前置可用
    # v3.7.0 (DC2 + C2, 2026-05-18): + stage 49 risk_taking_outcomes (第 10/11 篇)
    # v2.3 计划增量 +5: 16/17/18/19/30a (B1 EPU / D1 BERTopic / D2 staleness /
    #   D4 LLM CEO NER / D 组前置 SBERT 持久化) → 曾达 20
    # 2026-05-29 双模型重构: stage 30 (robustness_text2vec) 退役 (其 _t2v 列改由
    #   stage 15/25 内联双模型产出) → 20 − 1 = 19
    assert len(core_dag.STAGES_MAIN) == 19, (
        f"STAGES_MAIN 数量漂移: 期望 19 (v3.7.0 + v2.3 − stage 30 退役), "
        f"实际 {len(core_dag.STAGES_MAIN)}. 若有意增删阶段, 请同步更新本测试。"
    )


def test_validation_stage_count(core_dag):
    """``STAGES_VALIDATION`` 阶段数须等于 v3.7.3 计划累计 (18)。

    v3.4.0 baseline = 13 (含 39a inter_track_kappa).
    v3.5.0 +1 = 14: 加 39c construct_orthogonality (NMI 正交性 D3 stage)
    v3.5.1 +1 = 15: 加 39d lexical_discriminant_validity (A1+A3 HTMT/AVE/κ/α)
    v2.3 PR-#4 +1 = 16: 加 39e lm_discriminant_validity (LM 4 子词典 HTMT)
    v2.3 PR-D3 +1 = 17: 加 39f cross_media_alpha (Krippendorff α + variance)
    v3.7.3 +1 = 18: 加 39g track_discriminant_validity (_full/_ctx/_title HTMT 3×3)
    """
    # 31 + 32 + 32a + 33 + 34 + 35 + 36 + 37 + 38 + 38a + 38b + 39 + 39a + 39c + 39d + 39e + 39f + 39g = 18
    assert len(core_dag.STAGES_VALIDATION) == 18, (
        f"STAGES_VALIDATION drift: expected 18 (v3.7.3 +39g), got {len(core_dag.STAGES_VALIDATION)}."
    )


def test_v3_5_1_stage_39d_registered(core_dag):
    """v3.5.1 stage 39d 必须在 STAGES_VALIDATION 中且 not in OUTPUT_REGISTRY.

    Per plan v0.3 §3.1: 39d 是 validation stage, dependencies=["22_tone_words.py",
    "46_panel_export_main.py"] 双依赖 (修 R7-M4); 不进 OUTPUT_REGISTRY (与 39a/39c 一致).
    """
    scripts = {stage.script for stage in core_dag.STAGES_VALIDATION}
    assert '39d_lexical_discriminant_validity.py' in scripts, (
        "39d_lexical_discriminant_validity.py 未在 STAGES_VALIDATION 中 (v3.5.1 plan §3.1)"
    )


def test_v3_5_1_stage_39d_not_in_output_registry(core_dag):
    """v3.5.1 stage 39d 不进 OUTPUT_REGISTRY (与 39a/39c 历史约定一致, 修 plan v0.3 §3)."""
    from news_process.core.schemas import OUTPUT_REGISTRY
    assert '39d_lexical_discriminant_validity.py' not in OUTPUT_REGISTRY, (
        "39d 应作 validation stage, 不进 OUTPUT_REGISTRY (per schemas.py:134 历史约定)"
    )


def test_no_orphan_twelve_in_validation_count():
    """Guards against future maintainers leaving stale `12` references.

    Uses ``\\b12\\b`` word-boundary regex across the entire function source
    (covers docstring, comments, f-strings, and numeric tokens).
    Plan v1.37 §4.3.5 + Round-12 R12B-01 + Round-36/v1.31 expected count = 13.
    """
    import inspect
    import re

    src = inspect.getsource(test_validation_stage_count)
    hits = re.findall(r"\b12\b", src)
    assert hits == [], (
        f"Stale '12' references in test_validation_stage_count: "
        f"{len(hits)} hit(s). Expected only '13' after P1 (39a) lands. "
        f"Check docstring (L96), enumeration comment (L97), "
        f"assertion (L98), error f-string (L99)."
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
        core_dag.risk_taking_outcomes_enabled,  # v3.7.0 C4 修复
        core_dag.executive_ner_enabled,         # v3.7.1 P-016 修复
        core_dag.article_topic_enabled,         # O2 sample-run finding 2026-05-25
        core_dag.article_staleness_enabled,     # O2 sample-run finding 2026-05-25
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
    # v3.7.0 (C4 修复): stage 49 默认 disabled (opt-in), 故下面 enabled count
    # 与 v3.6.0 保持一致 — stage 49 通过单独 cfg_risk_taking 测试.

    # 三种情感方法全开 -> v3.7.1: stage 19 改 opt-in (P-016), 默认 disabled.
    # O2 2026-05-25: stage 17/18 也改 opt-in, 默认 disabled.
    # 2026-05-29: stage 30 (always_enabled) 退役 → total 20 → 19.
    # 故全开 enabled count = 19 - 4 (19/17/18/49 opt-in) = 15.
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 15

    # 仅 LLM -> 15 - 2 (words+berts) - 1 (24 跟随 berts) = 12
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 12

    # 无情感方法 -> 15 - 3 (llm+words+berts) - 1 (24 跟随 berts) = 11
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 11
    )

    # v3.7.0 NEW: risk_taking_outcomes opt-in 启用 stage 49 → 15 + 1 = 16
    cfg_with_risk_taking = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
        "risk_taking_outcomes": {"enabled": True},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_with_risk_taking)) == 16

    # O2 NEW 2026-05-25: article_topic + article_staleness opt-in 启用 → 15 + 2 = 17
    cfg_with_d_group = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
        "article_topic": {"enabled": True},
        "article_staleness": {"enabled": True},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_with_d_group)) == 17

    # v3.7.1 NEW: P-016 修复 — executive_ner opt-in 启用 stage 19 → 15 + 1 = 16
    cfg_with_ner = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
        "executive_ner": {"enabled": True},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_with_ner)) == 16


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

    现状有多个 None 条目 (30a_article_sbert + 3 个 40_attn_index_* + 5 个 stage46 .dta);
    必须正常通过 (stage 30 已于 2026-05-29 退役, 不再计入). 本测试用未污染的 schemas
    直接调用, 不抛即过.
    """
    from news_process.core import schemas
    schemas._validate_registry_invariant()  # 真实数据, 不抛 = 通过
