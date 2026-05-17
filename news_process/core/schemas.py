"""news_process.core.schemas — 列契约 + ``OUTPUT_REGISTRY`` (Phase 2d)。

Phase 2d 交付的单源 ``OUTPUT_REGISTRY`` 把每个阶段脚本名映射到它产出的
parquet 文件列表。orchestrator (用于陈旧数据预清理) 与 stage runner
(用于写入路径解析) 共同消费此字典。

Phase 1 时 orchestrator 内部持有一份私有的 ``_get_stage_output_files``
硬编码, 而各 stage 又独立从 ``CONFIG['filenames']['output_XX_*']``
读取文件名 — 教科书级 "双源真值" 风险。Phase 2d 通过本注册表消除这一
分歧。

注册表逐字保留历史 parquet 文件名契约, 确保 ``data/processed/`` 下既有
文件在新抽象下仍可访问。

v3 (Plan A.5 / Fix 5): 把原来的 ``_FILENAME_KEYS`` 列表下标对齐契约
重写为 ``_OUTPUT_FILENAME_KEYS`` 复合 key 字典 ``(script, default_filename) ->
filename_key | None``, 以彻底消除 "改一处忘改另一处导致 40_attn_index_city_year
错映射" 的脆弱性。同时保留 ``OUTPUT_REGISTRY: Mapping[str, list[str]]`` 公共
类型, 下游 ``papers/_common/panel_loader.py`` 等无需改动 (它们消费
``parquets[i]`` 仍是 str)。

模块加载时通过 ``_validate_registry_invariant()`` 做"纯结构 assert"型
顶层校验 — 凡 ``OUTPUT_REGISTRY`` 中出现的 ``(script, filename)`` 必须
在 ``_OUTPUT_FILENAME_KEYS`` 中显式登记 (str 或 None), 反之亦然。任何
漂移在 import 时立即抛 ``RuntimeError``, 不会静默通过。

注册表设计原则:
- ``OUTPUT_REGISTRY[script] = list[默认文件名]`` 保持 ``list[str]`` 公开
  类型, 既有调用方 (例如 ``panel_loader.list_available_panels``) 无需改动。
- ``_OUTPUT_FILENAME_KEYS[(script, default_filename)] = filename_key | None``:
  ``str`` 表示 paths.yaml 中存在该 key (用户可改名); ``None`` 表示该输出
  是 stage 内部副产物, 永远使用默认文件名。
"""

from __future__ import annotations

from typing import Mapping, Optional

# 阶段脚本名 (历史 root 文件名, 保留以做向后兼容) → 该阶段产出的 parquet
# 文件名列表。runner main() 不写 parquet 的阶段 (例如只产 eval_reports/*.csv
# 的验证类 runner) 故意不在此处登记; orchestrator 把缺失视为 "无需做预
# 清理"。
OUTPUT_REGISTRY: Mapping[str, list[str]] = {
    # 模块一: preprocess
    "00_preprocessing.py": ["00_preprocessing.parquet"],
    # 模块二: filtering
    "11_news_bank.py": ["11_bank_news.parquet"],
    "12_news_fintech.py": [
        "12_fintech_news.parquet",
        "12_fintech_news_full.parquet",
    ],
    # v3.6.0 (Plan E P4 A1): stage 13 = 12 + content_ctx 列, 供 stage 14/15 双轨化
    "13_materialize_ctx.py": ["13_news_with_ctx.parquet"],
    "14_fintech_intensity.py": ["14_fintech_intensity.parquet"],
    "15_article_policy_alignment.py": ["15_article_alignment.parquet"],
    # 模块三: sentiment
    "21_tone_llms.py": [
        "21_tone_llms.parquet",
        "21_tone_llms_full.parquet",
    ],
    "22_tone_words.py": ["22_words_tone.parquet"],
    "23_tone_berts.py": ["23_bert_tone.parquet"],
    "24_herd_decay_processor.py": ["24_herd_decay.parquet"],
    # 模块四c: text2vec 双轨稳健性指标 (战略差异 + 政策对齐 _full/_ctx)
    "30_robustness_text2vec.py": ["30_text2vec_indicators.parquet"],
    # 模块五: panel construction (阶段 45 产出 bank-year + article-bank 两类面板)
    "45_panel_export_main.py": [
        "40_panel_yearly.parquet",
        "40_article_bank_level.parquet",
        "40_attn_index_year.parquet",
        "40_attn_index_province_year.parquet",
        "40_attn_index_city_year.parquet",
    ],
    # v3.2.0 M6 (plan v14 §9.1): Stata 数据导出层
    "46_stata_export.py": [
        "46_panel_yearly_core.dta",
        "46_panel_yearly_full.dta",
        "46_panel_yearly_aux.dta",
        "46_panel_yearly_labels.do",
        "46_panel_yearly_codebook.xlsx",
    ],
    # 模块六: falsification
    "51_falsification_test.py": ["51_panel_with_controls.parquet"],
}


# v3 / Fix 5: 复合 key 替换历史的列表下标对齐契约
# ─────────────────────────────────────────────────────────────────────────────
# 旧设计 (Phase 9 plan m2):
#     _FILENAME_KEYS[script] = list[filename_key | None]   # 与 OUTPUT_REGISTRY 下标一一对应
# 旧风险:
#     若 OUTPUT_REGISTRY[script] 列表顺序改了一处忘改 _FILENAME_KEYS, 例如
#     45_panel_export_main 的 5 个输出顺序漂移, 会让 40_attn_index_city_year.parquet
#     被错映射到 'output_40_article_bank' 配置键 — 静默且严重。
# 新设计 (本 Fix 5):
#     _OUTPUT_FILENAME_KEYS[(script, default_filename)] = filename_key | None
# 新优势:
#     - 复合 key 直接用 (script, filename) 字面量定位, 不依赖列表下标。
#     - import 时通过 _validate_registry_invariant() 做双向覆盖校验, 任何
#       漂移立即在 import 阶段抛 RuntimeError (fail-fast)。
#     - OUTPUT_REGISTRY 公共 API (Mapping[str, list[str]]) 保持不变,
#       下游 papers/_common/panel_loader.py、tests/integration/test_dag_consistency.py
#       等消费方零改动。
_OUTPUT_FILENAME_KEYS: Mapping[tuple[str, str], Optional[str]] = {
    ("00_preprocessing.py", "00_preprocessing.parquet"): "output_00_preprocessing",
    ("11_news_bank.py", "11_bank_news.parquet"): "output_11_bank_news",
    ("12_news_fintech.py", "12_fintech_news.parquet"): "output_12_fintech_news",
    ("12_news_fintech.py", "12_fintech_news_full.parquet"): "output_12_fintech_full",
    # v3.6.0 (Plan E P4 A1)
    ("13_materialize_ctx.py", "13_news_with_ctx.parquet"): "output_13_news_with_ctx",
    ("14_fintech_intensity.py", "14_fintech_intensity.parquet"): "output_14_fintech_intensity",
    ("15_article_policy_alignment.py", "15_article_alignment.parquet"): "output_15_article_alignment",
    ("21_tone_llms.py", "21_tone_llms.parquet"): "output_21_tone_llms",
    ("21_tone_llms.py", "21_tone_llms_full.parquet"): "output_21_tone_llms_full",
    ("22_tone_words.py", "22_words_tone.parquet"): "output_22_words_tone",
    ("23_tone_berts.py", "23_bert_tone.parquet"): "output_23_bert_tone",
    ("24_herd_decay_processor.py", "24_herd_decay.parquet"): "output_24_herd_decay",
    # 30_text2vec_indicators 输出文件名硬编码在 validation/text2vec.py, 无 config key
    ("30_robustness_text2vec.py", "30_text2vec_indicators.parquet"): None,
    ("45_panel_export_main.py", "40_panel_yearly.parquet"): "output_40_panel_yearly",
    ("45_panel_export_main.py", "40_article_bank_level.parquet"): "output_40_article_bank",
    # 40_attn_index_* 三个 — stage 内部副输出, 无 config key
    ("45_panel_export_main.py", "40_attn_index_year.parquet"): None,
    ("45_panel_export_main.py", "40_attn_index_province_year.parquet"): None,
    ("45_panel_export_main.py", "40_attn_index_city_year.parquet"): None,
    # v3.2.0 M6 (plan v14 §9.1): stage 46 Stata 数据导出层产出 5 文件
    ("46_stata_export.py", "46_panel_yearly_core.dta"): None,
    ("46_stata_export.py", "46_panel_yearly_full.dta"): None,
    ("46_stata_export.py", "46_panel_yearly_aux.dta"): None,
    ("46_stata_export.py", "46_panel_yearly_labels.do"): None,
    ("46_stata_export.py", "46_panel_yearly_codebook.xlsx"): None,
    ("51_falsification_test.py", "51_panel_with_controls.parquet"): "output_51_panel_controls",
}


# v3 / Fix 4: 显式登记"已知不产 parquet"的 stage 集合
# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT_REGISTRY 历史上对 STAGES_VALIDATION (stage 31-39) 故意不登记 —
# 这些 stage 只写 eval_reports/*.csv, 不写 parquet。但旧的
# _get_stage_output_files 用 ``if not files: logger.debug(...)`` 兜底,
# 让"故意空"与"忘了登记 (新增 stage 漏)"无法区分, 后者的陈旧文件预清理
# 会静默失效。
#
# Fix 4 引入 EXPECTED_NO_OUTPUT_STAGES 显式集合: orchestrator 在缺登记
# 时, 若 stage 在此集合内 → debug log 跳过预清理 (合理); 否则 → raise
# RuntimeError 强制开发者明确决定 (登记 OUTPUT_REGISTRY 或加入此集合)。
#
# 注: 52_stata_data_audit.py / 53_export_stats_excel.py 不在 STAGES_MAIN/
# STAGES_VALIDATION 中, orchestrator 永远不会调 _get_stage_output_files()
# 查它们, 故不列入此集合 (避免无效条目误导维护者)。
EXPECTED_NO_OUTPUT_STAGES: frozenset[str] = frozenset({
    # validation stages (31-39): 只写 eval_reports/*.csv, 不写 parquet
    "31_bank_fintech_threshold.py",
    "32_news_llms_human.py",
    "32a_dedup_threshold_sensitivity.py",
    "33_news_llms_evaluation.py",
    "34_tone_validation.py",
    "35_radius_sensitivity.py",
    "36_entity_masking_test.py",
    "37_dict_coverage_audit.py",
    "38_media_diversity.py",
    "38a_temporal_mask_test.py",
    "38b_decay_sensitivity.py",
    "39_prompt_sensitivity.py",
    "39a_inter_track_kappa.py",
    "39c_construct_orthogonality.py",  # v3.5.0 D3 NMI: 写 data/processed/39c_*.parquet 但走 validation 约定 (per schemas.py:134 historical)
    "39d_lexical_discriminant_validity.py",  # v3.5.1 A1/A3 HTMT+κ+α: 写 data/processed/39d_*.parquet + 39d_htmt_matrix.json, validation 不进 OUTPUT_REGISTRY
})


def _validate_registry_invariant() -> None:
    """import-time 不变式五项校验 (recode round 1 + round 2 加固版):

    1. OUTPUT_REGISTRY 与 _OUTPUT_FILENAME_KEYS 的 (script, filename) 双向覆盖 —
       凡 OUTPUT_REGISTRY 中出现的 (script, default_filename) 必须在
       _OUTPUT_FILENAME_KEYS 中显式登记 (str 或 None), 反之亦然。
    2. OUTPUT_REGISTRY 各 script 的文件名列表内不允许重复 (防笔误如
       ``["a.parquet", "a.parquet"]`` 让 panel_loader 重复迭代).
    3. OUTPUT_REGISTRY 与 EXPECTED_NO_OUTPUT_STAGES 必须互斥 — 一个 stage 不能
       既"产 parquet"又"不产 parquet"; 重叠通常意味着维护者把 main stage 误标
       为 no-output, 会让预清理被错误跳过 → 陈旧文件污染下游.
    4. 跨 stage 文件名唯一性 (recode round 2) — 同一 parquet 文件名不允许出现
       在两个 stage 的输出列表中. 否则 panel_loader._find_producer_stage 反查
       只命中字典首位的 stage, 另一个 stage 的存在性被静默忽略.
    5. _OUTPUT_FILENAME_KEYS 中 filename_key 跨条目唯一性 (recode round 2) —
       不允许两个不同 (script, filename) 共享同一 paths.yaml::filenames key.
       否则用户改名会让两个 stage 写到同一文件 → 数据竞争 + 互相覆盖. None
       值不参与唯一性校验 (允许多个 stage 都标"无 config key").

    这是 v3 plan 中"允许的顶层副作用 (纯结构 assert)" 模式: 只验模块自身
    内部表示自洽, 不依赖运行时外部状态; 触发时抛 RuntimeError 可被 pytest
    / 上游 try/except 正常捕获 — 与 Python 社区 attrs/pydantic 等标准
    实践一致。
    """
    # ── 校验 1: 双向覆盖 ──
    expected = {(s, f) for s, files in OUTPUT_REGISTRY.items() for f in files}
    actual = set(_OUTPUT_FILENAME_KEYS.keys())
    missing_keys = expected - actual
    extra_keys = actual - expected
    if missing_keys or extra_keys:
        raise RuntimeError(
            f"OUTPUT_REGISTRY ↔ _OUTPUT_FILENAME_KEYS 不变式破坏: "
            f"missing={sorted(missing_keys)}, extra={sorted(extra_keys)}"
        )

    # ── 校验 2: 列表内去重 (recode round 1) ──
    for script, files in OUTPUT_REGISTRY.items():
        if len(files) != len(set(files)):
            dups = sorted({f for f in files if files.count(f) > 1})
            raise RuntimeError(
                f"OUTPUT_REGISTRY[{script!r}] 列表内有重复文件名: {dups}; "
                f"会让 panel_loader.list_available_panels 重复处理 — 请去重."
            )

    # ── 校验 3: 与 EXPECTED_NO_OUTPUT_STAGES 互斥 (recode round 1) ──
    overlap = set(OUTPUT_REGISTRY.keys()) & EXPECTED_NO_OUTPUT_STAGES
    if overlap:
        raise RuntimeError(
            f"OUTPUT_REGISTRY ∩ EXPECTED_NO_OUTPUT_STAGES 必须为空, 实际重叠: "
            f"{sorted(overlap)}; 一个 stage 不能既'产 parquet'又'不产'. "
            f"若该 stage 真的产 parquet, 从 EXPECTED_NO_OUTPUT_STAGES 移除; "
            f"否则从 OUTPUT_REGISTRY 移除."
        )

    # ── 校验 4: 跨 stage 文件名唯一性 (recode round 2) ──
    # 现状: 18 个 parquet 文件名两两不同; 校验防御未来 copy-paste 笔误.
    all_files = [f for files in OUTPUT_REGISTRY.values() for f in files]
    if len(all_files) != len(set(all_files)):
        from collections import Counter as _Counter
        cross_dups = sorted(
            {f for f, n in _Counter(all_files).items() if n > 1}
        )
        # 反向定位: 找出每个重复文件名涉及的 stage 列表
        producers: dict[str, list[str]] = {}
        for stage_script, files in OUTPUT_REGISTRY.items():
            for f in files:
                if f in cross_dups:
                    producers.setdefault(f, []).append(stage_script)
        raise RuntimeError(
            f"OUTPUT_REGISTRY 中跨 stage 出现重复 parquet 文件名: {cross_dups}; "
            f"涉及 stage: {producers}; 会让 papers/_common/panel_loader."
            f"_find_producer_stage 反查只命中字典首位 stage, 静默忽略其它. "
            f"请给每个 stage 的输出文件取唯一名."
        )

    # ── 校验 5: filename_key 跨条目唯一性 (recode round 2) ──
    # None 值不参与校验 — 允许多个内部副输出都标 None.
    non_none_keys = [k for k in _OUTPUT_FILENAME_KEYS.values() if k is not None]
    if len(non_none_keys) != len(set(non_none_keys)):
        from collections import Counter as _Counter
        key_dups = sorted(
            {k for k, n in _Counter(non_none_keys).items() if n > 1}
        )
        # 反向定位: 找出每个重复 filename_key 涉及的 (script, filename) 对
        sharers: dict[str, list[tuple[str, str]]] = {}
        for (s, f), key in _OUTPUT_FILENAME_KEYS.items():
            if key in key_dups:
                sharers.setdefault(key, []).append((s, f))
        raise RuntimeError(
            f"_OUTPUT_FILENAME_KEYS 中 filename_key 跨条目重复 (排除 None): "
            f"{key_dups}; 涉及 (script, filename): {sharers}; "
            f"用户在 paths.yaml::filenames 改名会让两个 stage 写到同一文件 "
            f"→ 数据竞争 + 互相覆盖. 请给每个条目取唯一 filename_key."
        )


_validate_registry_invariant()  # 模块加载即校验 (fail-fast)


def get_stage_outputs(stage_script: str,
                      config: Optional[Mapping] = None) -> list[str]:
    """返回阶段脚本产出的 parquet 文件名列表 (无登记返回空列表).

    Args:
        stage_script: 阶段脚本名 (例如 ``'00_preprocessing.py'``).
        config: 可选; 当提供时, 函数会先尝试从
            ``config['filenames'][filename_key]`` 解析实际文件名,
            未配置或键缺失时 fallback 到 OUTPUT_REGISTRY 默认文件名.
            ``None`` 时返回 OUTPUT_REGISTRY 默认文件名 (向后兼容).

    Returns:
        文件名列表 (顺序与 OUTPUT_REGISTRY 一致).

    实现注 (v3): 通过 ``_OUTPUT_FILENAME_KEYS[(script, default_filename)]``
    复合 key 反查 filename_key, 不再依赖与 OUTPUT_REGISTRY 的列表下标对齐.
    """
    defaults = OUTPUT_REGISTRY.get(stage_script, [])
    if not defaults:
        return []
    if config is None:
        return list(defaults)

    filenames_cfg = config.get('filenames', {}) or {}

    out: list[str] = []
    for default_filename in defaults:
        key = _OUTPUT_FILENAME_KEYS.get((stage_script, default_filename))
        if key is not None and key in filenames_cfg:
            out.append(filenames_cfg[key])
        else:
            out.append(default_filename)
    return out


__all__ = ["OUTPUT_REGISTRY", "EXPECTED_NO_OUTPUT_STAGES", "get_stage_outputs"]
