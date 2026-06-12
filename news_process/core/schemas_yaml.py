"""news_process.core.schemas_yaml — YAML 域 schema 校验.

P1-2 (cleanup/2026-05-13) 落地.

背景
----
``core.config.load_config()`` 之前对 YAML 字段无 schema 校验. 业务代码用
``CONFIG.get('panel_building', {}).get('compute_bartik_iv', True)`` 散落式访问,
YAML 中 typo 一个 key (例如 ``compute_brtik_iv``) 会 silent fallback 到 default,
不报错. 本模块在 ``load_config()`` 之后做"知名字段 + 类型"校验, 未知 key 给
warning, 类型错误给 raise.

设计原则
--------
- **零运行时 dep**: 仅用标准库 ``dataclasses`` + 手写校验函数, 不引入
  ``pydantic`` (项目 dep 收敛). 见 cleanup plan 补审-1.
- **三域起步**: ``tone_llm_processing`` / ``panel_building`` / ``herd_detection``
  按 consumer 频次审计排序 (cleanup plan 审-6 的 P1-2a/b 拆分);
  其他域 (preprocessing/filtering/features/paths/validation) 暂不校验,
  等本批落地稳定后再扩.
- **warn-on-unknown**: 未知 key 仅 warning, 不 raise — 允许 YAML 早于 schema
  扩展 (例如新增字段时不必同步本文件). 拼写错误的"老 key 仍 default"问题
  由 warning 暴露给用户, 而非阻塞 pipeline.
- **raise-on-type-mismatch**: 类型不对 (例如 ``temperature: "0.0"`` 字符串)
  raise — 这种错误下游访问会更隐晦, 早 fail 更友好.

边界
----
- 不校验 ``models`` 列表 (各 model entry 由 LLM caller ``_ensure_llm_config``
  自带 schema, 重复校验无意义);
- 不校验 path 字段 (``paths.yaml`` 自身有 path resolve 路径, 校验它需要
  另一套路径模型, 留待 v3.0 范围);
- 不校验跨域约束 (例如 panel_building 启用 ↔ sentiment.enabled_methods),
  那是 ``_validate_enabled_methods_consistency`` (P0-3) 的范围.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# tone_llm_processing — sentiment.yaml 顶层节
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class ToneLLMSchema:
    """已知字段集 + 类型契约. 默认值仅用于结构展示, 不参与运行时."""

    enabled: bool = True
    timeout: int = 600
    connect_timeout: int = 120
    sock_connect_timeout: int = 120
    sock_read_timeout: int = 600
    ttl_dns_cache: int = 300
    keepalive_timeout: int = 60
    max_retries: int = 8
    retry_delay: int = 5
    retry_backoff: str = "exponential"  # 'exponential' | 'linear'
    retry_backoff_cap: int = 600
    max_concurrency: int = 40
    temperature: float = 0.0
    random_seed: int = 42
    force_json: bool = True
    ensemble_method: str = "majority_vote"
    auth_probe_timeout: int = 30
    # 这些字段是 list/dict 复合, 类型仅校验为 list/dict, 内容不深入:
    models: list = field(default_factory=list)
    logit_to_score: dict = field(default_factory=dict)
    # 这些字段为 prompt 文件路径 / 内联值, 内容由 _inline_external_prompts 写回:
    prompt_template_file: str = ""
    title_sentiment_prompt_template_file: str = ""
    # _inline_external_prompts 自动生成:
    prompt_template: str = ""
    prompt_template_version: str = "v0"
    title_sentiment_prompt_template: str = ""
    title_sentiment_prompt_template_version: str = "v0"


# ----------------------------------------------------------------------------
# panel_building — panel.yaml 顶层节
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class PanelBuildingSchema:
    """``panel.yaml::panel_building`` 节的不可变 schema 与默认值锚点。"""

    aggregation_frequency: str = "yearly"
    export_stata: bool = True
    compute_attention_index: bool = True
    compute_media_heterogeneity: bool = True
    compute_media_authority_weighting: bool = True
    compute_bartik_iv: bool = True
    bartik_base_year: Any = "auto"  # int 或 'auto'
    bartik_pre_treatment_cutoff: int = 2019
    compute_policy_shocks: bool = True


# ----------------------------------------------------------------------------
# herd_detection — sentiment.yaml 内 (跨域字段)
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class HerdDetectionSchema:
    """``sentiment.yaml::herd_detection`` 节的不可变 schema 与默认值锚点。"""

    similarity_threshold: float = 0.35
    time_window_days: int = 7
    max_features: int = 10000
    min_df: int = 5
    max_df: float = 0.9
    chunk_size: int = 1000


# ----------------------------------------------------------------------------
# 校验引擎
# ----------------------------------------------------------------------------


def _type_check(field_name: str, value: Any, expected_type: type, domain: str) -> None:
    """value 与 expected_type 类型不匹配时 raise TypeError.

    bool ↔ int 关系特殊处理: Python ``isinstance(True, int)`` 返回 True, 但我们
    不希望把 ``compute_bartik_iv: true`` 当作"int 字段被填了 1". 反之亦然.
    """
    if expected_type is bool:
        if not isinstance(value, bool):
            raise TypeError(f"{domain}.{field_name}: 期望 bool, 实际 {type(value).__name__} ({value!r})")
        return
    if expected_type is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{domain}.{field_name}: 期望 int, 实际 {type(value).__name__} ({value!r})")
        return
    if expected_type is float:
        # int 也接受 (YAML ``temperature: 0`` 应当合法)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{domain}.{field_name}: 期望 float, 实际 {type(value).__name__} ({value!r})")
        return
    if expected_type is str:
        if not isinstance(value, str):
            raise TypeError(f"{domain}.{field_name}: 期望 str, 实际 {type(value).__name__} ({value!r})")
        return
    if expected_type is list:
        if not isinstance(value, list):
            raise TypeError(f"{domain}.{field_name}: 期望 list, 实际 {type(value).__name__} ({value!r})")
        return
    if expected_type is dict:
        if not isinstance(value, dict):
            raise TypeError(f"{domain}.{field_name}: 期望 dict, 实际 {type(value).__name__} ({value!r})")
        return
    # Any 跳过 (例: PanelBuildingSchema.bartik_base_year)
    if expected_type is Any:
        return
    # 未知预期类型 — 不阻塞
    return


def _validate_domain(cfg_section: Mapping[str, Any], schema_cls: type, domain: str) -> None:
    """对一个 YAML 节做"已知字段类型校验 + 未知字段 warning".

    Args:
        cfg_section: ``config[domain]`` 字典.
        schema_cls:  对应的 ``@dataclass`` 类.
        domain:      错误消息中显示的 domain 名 (如 ``'panel_building'``).
    """
    if not isinstance(cfg_section, Mapping):
        # 整节缺失或类型异常 — 上游 config 加载应已 fail; 此处不再 raise.
        return

    schema_field_types = {f.name: f.type for f in fields(schema_cls)}

    # 类型校验 (已知字段)
    for key, value in cfg_section.items():
        if key in schema_field_types:
            expected = schema_field_types[key]
            # 处理 type-hint 字符串的情况 (PEP 563 / from __future__ import annotations)
            if isinstance(expected, str):
                expected_obj = {
                    "bool": bool,
                    "int": int,
                    "float": float,
                    "str": str,
                    "list": list,
                    "dict": dict,
                    "Any": Any,
                }.get(expected, Any)
            else:
                expected_obj = expected
            _type_check(key, value, expected_obj, domain)

    # 未知字段 warning (仅一行汇总, 避免日志炸裂)
    unknown = sorted(set(cfg_section.keys()) - set(schema_field_types.keys()))
    if unknown:
        _LOGGER.warning(
            "YAML 域 ``%s`` 包含 schema 未登记字段: %s. "
            "可能是 typo (旧字段拼写错误 silent fallback 到 default), "
            "或新字段尚未登记到 ``core/schemas_yaml.py`` 的 %s. "
            "前者请修字段名; 后者请扩 schema (并写测试守护).",
            domain,
            unknown,
            schema_cls.__name__,
        )


def validate_config_schema(config: Mapping[str, Any]) -> None:
    """对 P1-2 范围内的三个 YAML 域做 schema 校验.

    在 ``load_config()`` 末尾被调用. 不阻塞 pipeline (类型错误 raise; 未知字段
    仅 warning).
    """
    if "tone_llm_processing" in config:
        _validate_domain(config["tone_llm_processing"], ToneLLMSchema, "tone_llm_processing")
    if "panel_building" in config:
        _validate_domain(config["panel_building"], PanelBuildingSchema, "panel_building")
    if "herd_detection" in config:
        _validate_domain(config["herd_detection"], HerdDetectionSchema, "herd_detection")


__all__ = [
    "ToneLLMSchema",
    "PanelBuildingSchema",
    "HerdDetectionSchema",
    "validate_config_schema",
]
