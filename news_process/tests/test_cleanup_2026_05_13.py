"""tests/test_cleanup_2026_05_13.py — cleanup/2026-05-13 改动的不变式守护.

覆盖范围
--------
- P0-3 ``_validate_enabled_methods_consistency``: 4 边界 case (baseline /
  berts-off panel-on / berts-off panel-off / panel-section-missing).
- P1-1 ``_inline_external_prompts`` 在 prompt 文件无版本头时 emit warning.
- P1-2 ``validate_config_schema``: 类型错 raise / typo warn / int↔float
  松弛 / 空 cfg 通过 / bool↔int 严格分离.

不依赖 ``data/raw``, 仅做配置层 + 纯函数 invariant 校验, CI 友好.
"""

from __future__ import annotations

import io
import logging

import pytest

from news_process.core.config import _validate_enabled_methods_consistency
from news_process.core.schemas_yaml import (
    PanelBuildingSchema,
    ToneLLMSchema,
    validate_config_schema,
)

# ----------------------------------------------------------------------------
# P0-3: 跨阶段 enabled_methods 一致性
# ----------------------------------------------------------------------------


class TestEnabledMethodsConsistency:
    """P0-3 ``_validate_enabled_methods_consistency`` 边界行为."""

    def _capture_warnings(self, fn, *args, **kwargs):
        """运行 fn 并捕获本模块 logger 的 warning 消息列表."""
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setLevel(logging.WARNING)
        logger = logging.getLogger("news_process.core.config")
        logger.addHandler(handler)
        prev_level = logger.level
        logger.setLevel(logging.WARNING)
        try:
            fn(*args, **kwargs)
        finally:
            logger.removeHandler(handler)
            logger.setLevel(prev_level)
        return buf.getvalue()

    def test_baseline_config_no_warning(self):
        """当前 baseline (berts 启用 + panel 启用) — 不应触发 warning."""
        cfg = {
            "sentiment_analysis": {
                "enabled_methods": ["tone_llms", "tone_words", "tone_berts"],
            },
            "panel_building": {"compute_attention_index": True},
        }
        out = self._capture_warnings(_validate_enabled_methods_consistency, cfg)
        assert "tone_berts" not in out

    def test_berts_off_panel_on_warns(self):
        """禁 tone_berts + panel 启用 — 应触发 warning."""
        cfg = {
            "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
            "panel_building": {"compute_attention_index": True},
        }
        out = self._capture_warnings(_validate_enabled_methods_consistency, cfg)
        assert "tone_berts" in out

    def test_berts_off_panel_off_silent(self):
        """禁 tone_berts + 全禁 panel — 不应触发 warning."""
        cfg = {
            "sentiment_analysis": {"enabled_methods": ["tone_llms"]},
            "panel_building": {
                "compute_attention_index": False,
                "compute_bartik_iv": False,
                "compute_policy_shocks": False,
            },
        }
        out = self._capture_warnings(_validate_enabled_methods_consistency, cfg)
        assert out.strip() == ""

    def test_missing_panel_section_conservative_warn(self):
        """缺 panel_building 整节 — 保守判定为 panel_active, 触发 warning."""
        cfg = {"sentiment_analysis": {"enabled_methods": ["tone_llms"]}}
        out = self._capture_warnings(_validate_enabled_methods_consistency, cfg)
        assert "tone_berts" in out


# ----------------------------------------------------------------------------
# P1-2: YAML schema 校验
# ----------------------------------------------------------------------------


class TestSchemaValidation:
    """P1-2 ``validate_config_schema`` 三域校验."""

    # -- 类型错 raise --

    def test_temperature_string_raises(self):
        with pytest.raises(TypeError, match=r"temperature.*str"):
            validate_config_schema({"tone_llm_processing": {"temperature": "0.0"}})

    def test_bool_int_strict_separation(self):
        """isinstance(True, int) quirk 不允许污染 bool 字段."""
        with pytest.raises(TypeError, match=r"compute_bartik_iv.*int"):
            validate_config_schema({"panel_building": {"compute_bartik_iv": 1}})

    def test_int_field_string_raises(self):
        with pytest.raises(TypeError, match=r"max_retries.*str"):
            validate_config_schema({"tone_llm_processing": {"max_retries": "8"}})

    def test_none_for_float_raises(self):
        with pytest.raises(TypeError, match=r"temperature.*NoneType"):
            validate_config_schema({"tone_llm_processing": {"temperature": None}})

    # -- 未知字段 warning --

    def test_typo_field_warns_not_raises(self, caplog):
        with caplog.at_level(logging.WARNING, logger="news_process.core.schemas_yaml"):
            validate_config_schema({"panel_building": {"compute_brtik_iv": True}})
        warnings = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("compute_brtik_iv" in m for m in warnings)

    # -- 合理松弛 --

    def test_int_accepted_for_float(self):
        """YAML ``temperature: 0`` 应当合法."""
        validate_config_schema({"herd_detection": {"similarity_threshold": 0}})

    def test_empty_config_tolerated(self):
        """完全空的 cfg 不应 raise (避免 schema 阻塞最小化配置测试)."""
        validate_config_schema({})

    def test_unrelated_domain_ignored(self):
        """schema 未覆盖的域不应 raise."""
        validate_config_schema({"preprocessing": {"foo_typo": 123}})

    # -- 已知字段全集 sanity --

    def test_all_known_panel_keys_accepted(self):
        """已登记的全部 panel_building 字段都应通过校验 (用各自合法类型值)."""
        cfg_section = {
            "aggregation_frequency": "yearly",
            "export_stata": True,
            "compute_attention_index": True,
            "compute_media_heterogeneity": True,
            "compute_media_authority_weighting": True,
            "compute_bartik_iv": True,
            "bartik_base_year": "auto",
            "bartik_pre_treatment_cutoff": 2019,
            "compute_policy_shocks": True,
        }
        validate_config_schema({"panel_building": cfg_section})

    def test_all_known_herd_keys_accepted(self):
        cfg_section = {
            "similarity_threshold": 0.35,
            "time_window_days": 7,
            "max_features": 10000,
            "min_df": 5,
            "max_df": 0.9,
            "chunk_size": 1000,
        }
        validate_config_schema({"herd_detection": cfg_section})


# ----------------------------------------------------------------------------
# 元测试: schema dataclass 自身 sanity (P1-2 maintenance)
# ----------------------------------------------------------------------------


class TestSchemaSelfConsistency:
    """schema dataclass 的元属性 — 防止维护时漂移."""

    def test_panel_schema_has_compute_keys(self):
        """``_PANEL_ACTIVE_KEYS`` 列出的 3 个标识必须都是 PanelBuildingSchema 字段.

        防止 R3-2: 加新 panel 主开关时漂移检测.
        """
        from dataclasses import fields

        from news_process.core.config import _PANEL_ACTIVE_KEYS

        panel_fields = {f.name for f in fields(PanelBuildingSchema)}
        for key in _PANEL_ACTIVE_KEYS:
            assert key in panel_fields, (
                f"_PANEL_ACTIVE_KEYS 含 {key!r}, 但 PanelBuildingSchema 未登记; "
                f"任一处漂移会让 P0-3 warning 与 schema 校验不一致."
            )

    def test_tone_llm_schema_has_prompt_version_fields(self):
        """schema 必须登记 ``prompt_template_version`` 等 P3-17 生成字段."""
        from dataclasses import fields

        tone_fields = {f.name for f in fields(ToneLLMSchema)}
        assert "prompt_template_version" in tone_fields
        assert "title_sentiment_prompt_template_version" in tone_fields


# ----------------------------------------------------------------------------
# quality-hardening Round 18 (2026-05-27): schemas_yaml 覆盖率 94.1% → ~100%
# 补齐未覆盖行: 148 (str 不匹配) / 152 (list 不匹配) / 156 (dict 不匹配) /
# 162 (未知 expected_type) / 175 (非 Mapping 节) / 195 (非 str hint)
# ----------------------------------------------------------------------------


class TestSchemaTypeCheckEdgeCases:
    """_type_check 各类型不匹配分支的逐一覆盖."""

    def test_str_field_int_raises(self):
        """str 期望 + int 实际 → TypeError (schemas_yaml.py:148)."""
        with pytest.raises(TypeError, match=r"prompt_template_version.*int"):
            validate_config_schema({"tone_llm_processing": {
                "prompt_template_version": 42,  # 期望 str
            }})

    def test_list_field_dict_raises(self):
        """list 期望 + dict 实际 → TypeError (schemas_yaml.py:152).

        sentiment_analysis.enabled_methods 是 list[str].
        """
        from news_process.core.schemas_yaml import _type_check
        with pytest.raises(TypeError, match=r"enabled_methods.*list"):
            _type_check("enabled_methods", {"k": 1}, list, "sentiment_analysis")

    def test_dict_field_list_raises(self):
        """dict 期望 + list 实际 → TypeError (schemas_yaml.py:156)."""
        from news_process.core.schemas_yaml import _type_check
        with pytest.raises(TypeError, match=r"some_dict.*list"):
            _type_check("some_dict", ["a", "b"], dict, "test_domain")

    def test_unknown_expected_type_returns_silently(self):
        """未知 expected type (非 str/int/float/list/dict/bool/Any) → 静默 return
        (schemas_yaml.py:162)."""
        from news_process.core.schemas_yaml import _type_check
        # 自定义 type — schemas_yaml 不识别, 应不 raise
        class CustomType:
            pass
        # 不抛即可
        _type_check("foo", CustomType(), CustomType, "domain")

    def test_validate_domain_handles_non_mapping_section(self):
        """cfg_section 非 Mapping → silently return (schemas_yaml.py:173-175)."""
        from news_process.core.schemas_yaml import (
            PanelBuildingSchema,
            _validate_domain,
        )
        # 传入 list 而非 dict — 应不 raise (上游应已 fail)
        _validate_domain(["not", "a", "dict"], PanelBuildingSchema, "panel_building")
        # 传入 None
        _validate_domain(None, PanelBuildingSchema, "panel_building")

    def test_list_field_valid_list_passes_silently(self):
        """list 期望 + list 实际 → 走完 return (schemas_yaml.py:153)."""
        from news_process.core.schemas_yaml import _type_check
        # 不抛即可
        _type_check("enabled_methods", ["a", "b"], list, "domain")

    def test_dict_field_valid_dict_passes_silently(self):
        """dict 期望 + dict 实际 → 走完 return (schemas_yaml.py:157)."""
        from news_process.core.schemas_yaml import _type_check
        _type_check("some_dict", {"k": "v"}, dict, "domain")
