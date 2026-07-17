"""tests/integration/test_dag_consistency.py — Phase 1.7 交付物。

校验两条流水线编排器均消费 ``news_process.core.dag`` 中的规范 DAG 声明,
而非各自维护平行阶段列表。此为重整方案所要求的*单一真源*检验,
用于杜绝历史上「双轨编排」反模式 (见 ``news_process-restructure-blueprint`` §1 缺陷 #1)。

断言三条性质:

1. ``run_pipeline_function.STAGES is core.dag.STAGES_MAIN`` (对象同一性)
2. ``run_pipeline_validation.STAGES is core.dag.STAGES_VALIDATION``
3. 任一 ``StageSpec.enabled_when`` 须为 ``core.dag`` 模块级谓词之一;
   从而防止未来误将新 ``lambda`` 内联进 ``StageSpec``、导致跨模块 ``is`` 校验失效。

白话: 流水线的阶段清单只许有一份 (写在 core/dag.py 里), 两个编排器必须
直接引用同一个 list 对象 (用 ``is`` 比对内存同一性, 而非内容相等) —
谁要是自己复制了一份清单, 哪怕内容一模一样, 这里也会立刻报错。
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
    # 预设 NEWS_PROCESS_RUN_ID, 锁定运行关联标记避免每个测试进程重新生成。
    # (日志已扁平化为 logs/<stage>.log, 此 ID 不再影响落盘路径, 仅作关联标记。)
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
    """``STAGES_MAIN`` 阶段数须等于 16 (15 + 2026-06-15 stage 12b 邻近共现硬过滤)。"""
    # baseline 14: 00 + 11 + 12 + 13 + 14 + 15 + 21 + 22 + 23 + 24 + 45 + 46 + 51 (+30 历史)
    # v3.2.0 M6: + stage 46 Stata 导出
    # v3.6.0 (Plan E P4 A1): + stage 13 content_ctx 物化, 让 14/15 双轨化前置可用
    # v2.3 计划增量: 17/18/19/30a (D1 BERTopic / D2 staleness /
    #   D4 LLM CEO NER / D 组前置 SBERT 持久化) → 连同一度存在的 stage 16 曾达 20
    # 2026-05-29 双模型重构: stage 30 (robustness_text2vec) 退役 (其 _t2v 列改由
    #   stage 15/25 内联双模型产出) → 20 − 1 = 19
    # 2026-06-05: stage 16 (宏观控制 merge) 整体移除 → 19 − 1 = 18
    # 2026-06-09: stage 17 (D1 BERTopic 叙事主题) + stage 19 (D4 LLM CEO NER) 整体移除 → 18 − 2 = 16
    # 2026-06-12: stage 49 (risk_taking_outcomes) 整体移除 (无财务数据无法计算) → 16 − 1 = 15
    # 2026-06-15: stage 12b (银行×金科邻近共现硬过滤, Andreou et al. 2026) 新增 → 15 + 1 = 16
    assert len(core_dag.STAGES_MAIN) == 16, (
        f"STAGES_MAIN 数量漂移: 期望 16 (15 + stage 12b 邻近共现硬过滤), "
        f"实际 {len(core_dag.STAGES_MAIN)}. 若有意增删阶段, 请同步更新本测试。"
    )


def test_validation_stage_count(core_dag):
    """``STAGES_VALIDATION`` 阶段数须等于 16 (39g title 轨 + 39h DC4 污染检验 + 38a 时间掩码均已删除)。

    v3.4.0 baseline = 13 (含 39a inter_track_kappa).
    v3.5.0 +1 = 14: 加 39c construct_orthogonality (NMI 正交性 D3 stage)
    v3.5.1 +1 = 15: 加 39d lexical_discriminant_validity (A1+A3 HTMT/AVE/κ/α)
    v2.3 PR-#4 +1 = 16: 加 39e lm_discriminant_validity (LM 6 子词典 HTMT)
    v2.3 PR-D3 +1 = 17: 加 39f cross_media_alpha (Krippendorff α + variance)
    2026-06-05 +1 = 18: 加 39h llm_contamination_test (DC4 接线, opt-in 默认禁用)
    随后 −1 = 17: 删 39h (其唯一 outcome 源 stage 49 移除, 无财务数据无法计算)
    本次 −1 = 16: 删 38a temporal_mask_test (时间掩码前视偏误检验移除)
    """
    # 31 + 32 + 32a + 33 + 34 + 35 + 36 + 37 + 38 + 38b + 39 + 39a + 39c + 39d + 39e + 39f = 16
    assert len(core_dag.STAGES_VALIDATION) == 16, (
        f"STAGES_VALIDATION drift: expected 16 (39g/39h/38a removed), got {len(core_dag.STAGES_VALIDATION)}."
    )


def test_v3_5_1_stage_39d_registered(core_dag):
    """v3.5.1 stage 39d 必须在 STAGES_VALIDATION 中且 not in OUTPUT_REGISTRY.

    Per plan v0.3 §3.1: 39d 是 validation stage, dependencies=["22_tone_words.py",
    "40_panel_export_main.py"] 双依赖 (修 R7-M4); 不进 OUTPUT_REGISTRY (与 39a/39c 一致).
    """
    scripts = {stage.script for stage in core_dag.STAGES_VALIDATION}
    assert '73_lexical_discriminant_validity.py' in scripts, (
        "73_lexical_discriminant_validity.py 未在 STAGES_VALIDATION 中 (v3.5.1 plan §3.1)"
    )


def test_v3_5_1_stage_39d_not_in_output_registry(core_dag):
    """v3.5.1 stage 39d 不进 OUTPUT_REGISTRY (与 39a/39c 历史约定一致, 修 plan v0.3 §3)."""
    from news_process.core.schemas import OUTPUT_REGISTRY
    assert '73_lexical_discriminant_validity.py' not in OUTPUT_REGISTRY, (
        "39d 应作 validation stage, 不进 OUTPUT_REGISTRY (per schemas.py:134 历史约定)"
    )


def test_no_orphan_twelve_in_validation_count():
    """守护未来维护者不在 test_validation_stage_count 中遗留陈旧的 `12` 引用。

    用 ``\\b12\\b`` 词边界正则扫描该函数的完整源码
    (覆盖 docstring、注释、f-string 与数字 token)。
    Plan v1.37 §4.3.5 + Round-12 R12B-01 + Round-36/v1.31 期望计数 = 16 (39g/39h/38a 已删)。

    白话: 本测试用 inspect.getsource 把上面那个计数测试的源代码当文本读出来,
    检查里面没有残留历史计数 "12" 字样 — 改阶段数时漏改注释也会被抓。
    因此修改 test_validation_stage_count 内的任何文字都可能影响本测试;
    只能追加不含独立 "12" 的内容, 勿随意替换。
    """
    import inspect
    import re

    src = inspect.getsource(test_validation_stage_count)
    hits = re.findall(r"\b12\b", src)
    assert hits == [], (
        f"Stale '12' references in test_validation_stage_count: "
        f"{len(hits)} hit(s). Expected count = 16 (39g/39h/38a removed). "
        f"Check docstring, enumeration comment, assertion, and "
        f"error f-string in test_validation_stage_count."
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
    """``filter_enabled()`` 在全 always-on 后恒返回 STAGES_MAIN 全集 (16)。

    2026-06-13 更新: 三种情感方法 (21/22/23/24) 与 stage 18 (staleness) 均已改为
    无条件 always_enabled (用户决策: 全部启用而非条件启用), 不再随 enabled_methods /
    article_staleness.enabled 启停。因此无论 cfg 如何配置, filter_enabled 都返回
    全部 main stage。(历史上 21/22 随 enabled_methods、18 随 opt-in 条件启停,
    计数曾随 cfg 在不同配置下漂移; 全 always-on 后统一。)
    2026-06-15: 新增 stage 12b (邻近共现硬过滤, always-on) → 全集 15 → 16。
    """
    # STAGES_MAIN 当前 16 个 stage, 全部 always_enabled → 任何 cfg 下都恒选中全集。
    cfg_full = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_full)) == 16

    # 仅 LLM: 21/22/23/24 全 always-on, words 不再被排除 → 仍 16
    cfg_llm_only = {
        "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
        "validation": {},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_llm_only)) == 16

    # 无情感方法: 三种方法均 always-on, 不再被排除 → 仍 16
    cfg_no_sentiment = {
        "sentiment_analysis": {"enabled_methods": []},
        "validation": {},
    }
    assert (
        len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_no_sentiment)) == 16
    )

    # article_staleness 显式启用: stage 18 本就 always-on → 仍 16 (与上方一致)
    cfg_with_d_group = {
        "sentiment_analysis": {
            "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
        },
        "validation": {},
        "article_staleness": {"enabled": True},
    }
    assert len(core_dag.filter_enabled(core_dag.STAGES_MAIN, cfg_with_d_group)) == 16


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
    # D3 (2026-07-18 第六轮审计): 反向恒等 — 删阶段忘删 registry 条目时孤儿键会被
    # get_stage_outputs 继续对外供给 (幽灵 producer), 且 CLAUDE.md「OUTPUT_REGISTRY=16」
    # 计数不变量此前无测试等价物。集合恒等同时给出正向包含、反向包含与 len==16。
    # 若未来有意新增「MAIN 无输出阶段」, 须放宽本恒等式为 ∪-覆盖+互斥,
    # 并同步更新 CLAUDE.md 计数不变量 (OUTPUT_REGISTRY=16)。
    main_scripts = {s.script for s in core_dag.STAGES_MAIN}
    assert set(OUTPUT_REGISTRY) == main_scripts, (
        f"OUTPUT_REGISTRY 与 STAGES_MAIN scripts 不恒等 — 孤儿键: "
        f"{sorted(set(OUTPUT_REGISTRY) - main_scripts)}; 缺登记: "
        f"{sorted(main_scripts - set(OUTPUT_REGISTRY))}. "
        f"(若有意新增 MAIN 无输出阶段, 放宽本恒等式并更新 CLAUDE.md 计数不变量)"
    )
    assert len(OUTPUT_REGISTRY) == 16


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
    # D3 (2026-07-18): 反向恒等 — 删验证阶段忘删 EXPECTED_NO_OUTPUT_STAGES 条目
    # 此前零测试可捕获。当前事实态: 全部 16 个验证阶段均无**注册** parquet 输出
    # (OUTPUT_REGISTRY 意义上; 72/73/75 的盘上 parquet 为 registry 外验证产物), 集合恒等。
    # 若未来有验证阶段产注册 parquet (入 OUTPUT_REGISTRY), 放宽为 ∪-覆盖+互斥。
    val_scripts = {s.script for s in core_dag.STAGES_VALIDATION}
    assert set(EXPECTED_NO_OUTPUT_STAGES) == val_scripts, (
        f"EXPECTED_NO_OUTPUT_STAGES 与 STAGES_VALIDATION scripts 不恒等 — 孤儿: "
        f"{sorted(set(EXPECTED_NO_OUTPUT_STAGES) - val_scripts)}; 缺列: "
        f"{sorted(val_scripts - set(EXPECTED_NO_OUTPUT_STAGES))}"
    )
    assert len(EXPECTED_NO_OUTPUT_STAGES) == 16


def test_stage_scripts_unique(core_dag):
    """N6 (2026-07-18 第六轮审计): STAGES 列表内 script 唯一性 —
    复制粘贴改名遗漏会让 orchestrator 双跑同一脚本且漏跑被顶掉的阶段,
    而 16 计数/⊆ 关系/谓词断言全部探不到 (CLAUDE.md「无重名」承诺的测试等价物)。"""
    for stages, label in ((core_dag.STAGES_MAIN, "STAGES_MAIN"),
                          (core_dag.STAGES_VALIDATION, "STAGES_VALIDATION")):
        scripts = [s.script for s in stages]
        dupes = sorted({x for x in scripts if scripts.count(x) > 1})
        assert len(scripts) == len(set(scripts)), f"{label} 存在重名 script: {dupes}"


def test_output_filename_keys_invariant():
    """v3 / Fix 5: import-time _validate_registry_invariant() 已校验,
    此处显式覆盖以保证未来不被静默回退 (例如有人删除该顶层调用).
    """
    from news_process.core import schemas
    schemas._validate_registry_invariant()  # 不抛即过


def test_method_to_predicate_covers_sentiment_specs(core_dag):
    """v3 / Fix 2: METHOD_TO_PREDICATE 必须覆盖 STAGES_MAIN 中所有
    kind='sentiment' 且非 always_enabled 的 stage 谓词, 反之亦然.

    2026-06-12 修订: stage 23 (BERT) 与 stage 24 (herd_decay) 已改为无条件
    always_enabled, 并从 METHOD_TO_PREDICATE 移除 'tone_berts'。故 kind='sentiment'
    且非 always_enabled 的 stage 仅剩 21/22 → sentiment_predicates = {llm, words}
    = METHOD_TO_PREDICATE.values()。本测试仍成立, 通过.
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

    现状有多个 None 条目 (25_article_sbert + 3 个 40_attn_index_* + 3 个 stage46 导出 .dta/.do/.xlsx);
    必须正常通过 (stage 30 已于 2026-05-29 退役, 不再计入). 本测试用未污染的 schemas
    直接调用, 不抛即过.
    """
    from news_process.core import schemas
    schemas._validate_registry_invariant()  # 真实数据, 不抛 = 通过
