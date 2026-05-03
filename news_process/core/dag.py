"""news_process.core.dag — declarative pipeline DAG.

Phase 1 deliverable: ``StageSpec`` data class + ``STAGES_MAIN`` / ``STAGES_VALIDATION``
lists.  These are the **single source of truth** for which stages exist and
when they run; both ``run_pipeline_function.py`` (main pipeline runner) and
``run_pipeline_validation.py`` (validation runner) import their ``STAGES``
constant from here, and ``tests/integration/test_dag_consistency.py``
verifies the bindings match by identity.

Naming discipline: ``StageSpec`` is the *declarative* record (a frozen
dataclass) used in the DAG.  It is intentionally **distinct** from the
*runtime* ``Stage`` abstract base class that will live in ``core/stage.py``
in a later phase, to avoid a name collision.

Config-conditional dynamism (e.g. sentiment.enabled_methods filtering
21/22/23) is captured by the ``enabled_when`` predicate, not by branching
inside the orchestrator.  Predicates are first-class Python callables
declared at module scope so that identity (``is``) comparison is
meaningful for the DAG-consistency test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


# ----------------------------------------------------------------------------
# enabled_when predicates.  Declared at module scope so identity-equality
# (``is``) holds across import sites — the DAG consistency test relies on
# this to confirm both orchestrators reuse the same predicate object.
# ----------------------------------------------------------------------------


def always_enabled(_cfg: dict[str, Any]) -> bool:
    return True


def llm_method_enabled(cfg: dict[str, Any]) -> bool:
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_llms' in methods


def words_method_enabled(cfg: dict[str, Any]) -> bool:
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_words' in methods


def berts_method_enabled(cfg: dict[str, Any]) -> bool:
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_berts' in methods


def _validation_flag(key: str, default: bool = True
                     ) -> Callable[[dict[str, Any]], bool]:
    """Return a predicate that reads ``cfg['validation'][key]`` (default True)."""
    def predicate(cfg: dict[str, Any]) -> bool:
        return cfg.get('validation', {}).get(key, default)
    predicate.__name__ = f"validation_{key}_enabled"
    return predicate


def temporal_mask_enabled(cfg: dict[str, Any]) -> bool:
    return cfg.get('temporal_mask_test', {}).get('enabled', False)


# Validation predicate handles — declared once at module scope so both
# core/dag.STAGES_VALIDATION and run_pipeline_validation.STAGES reuse the
# same callable object.
_VALIDATION_PREDS: dict[str, Callable[[dict[str, Any]], bool]] = {
    'threshold_sensitivity': _validation_flag('threshold_sensitivity'),
    'dedup_sensitivity': _validation_flag('dedup_sensitivity'),
    'classification_eval': _validation_flag('classification_eval'),
    'sentiment_validation': _validation_flag('sentiment_validation'),
    'radius_sensitivity': _validation_flag('radius_sensitivity'),
    'entity_masking': _validation_flag('entity_masking'),
    'dict_coverage_audit': _validation_flag('dict_coverage_audit'),
    'media_diversity': _validation_flag('media_diversity'),
    'prompt_sensitivity': _validation_flag('prompt_sensitivity'),
}


# ----------------------------------------------------------------------------
# StageSpec — declarative DAG record.
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class StageSpec:
    """Declarative descriptor for a single pipeline stage.

    Attributes:
        name:         Human-readable stage label (used in logs, summaries).
        script:       Filename relative to project root (``"00_preprocessing.py"``).
        group:        ``"main"`` | ``"validation"`` | ``"feature"``.
        kind:         Free-form label for kind/category.
        timeout:      Subprocess timeout in seconds.
        enabled_when: Predicate ``(cfg) -> bool`` deciding runtime inclusion.
                      Use ``always_enabled`` for unconditional stages.

    Phase 1 deliberately omits ``inputs`` / ``outputs`` field population;
    those will be wired through ``core.schemas.OUTPUT_REGISTRY`` in Phase 2d.
    """

    name: str
    script: str
    group: str
    kind: str = "stage"
    timeout: int = 3600
    enabled_when: Callable[[dict[str, Any]], bool] = always_enabled


# ----------------------------------------------------------------------------
# STAGES_MAIN — the production pipeline DAG (run_pipeline_function).
# Mirrors run_pipeline_function.py:run_pipeline()'s stages list, with
# config-driven branches captured as enabled_when predicates.
# ----------------------------------------------------------------------------


STAGES_MAIN: list[StageSpec] = [
    # ── 模块一：新闻预处理模块 ──
    StageSpec(
        name="阶段00: 数据预处理",
        script="00_preprocessing.py",
        group="main", kind="preprocess",
        timeout=10000,
    ),

    # ── 模块二：新闻筛选模块 ──
    StageSpec(
        name="阶段11: 银行新闻判断",
        script="11_news_bank.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段12: 金融科技新闻判断 + 全量分类结果",
        script="12_news_fintech.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段14: 金融科技技术重度评分 (TF-IDF)",
        script="14_fintech_intensity.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段15: 文章级政策语义对齐度",
        script="15_article_policy_alignment.py",
        group="main", kind="filter",
        timeout=7200,  # contains Embedding API calls
    ),

    # ── 模块三：新闻情感模块 (config-conditional via enabled_methods) ──
    StageSpec(
        name="阶段21: 统一 LLM 语义精筛与情感分析",
        script="21_tone_llms.py",
        group="main", kind="sentiment",
        enabled_when=llm_method_enabled,
    ),
    StageSpec(
        name="阶段22: 词典法情感分析",
        script="22_tone_words.py",
        group="main", kind="sentiment",
        enabled_when=words_method_enabled,
    ),
    StageSpec(
        name="阶段23: BERT模型情感分析",
        script="23_tone_berts.py",
        group="main", kind="sentiment",
        enabled_when=berts_method_enabled,
    ),

    # ── 模块四b：跟风衰减权重 ──
    StageSpec(
        name="阶段24: 跟风衰减权重",
        script="24_herd_decay_processor.py",
        group="main", kind="sentiment",
    ),

    # ── 模块五：面板数据构建 ──
    StageSpec(
        name="阶段40-45: Bank-Year 面板数据构建",
        script="45_panel_export_main.py",
        group="main", kind="panel",
        timeout=7200,  # contains Stage 25/26/27 Embedding computation
    ),

    # ── 模块六：伪造检验 ──
    StageSpec(
        name="阶段51: 伪造检验对照变量构建",
        script="51_falsification_test.py",
        group="main", kind="falsification",
    ),
]


# ----------------------------------------------------------------------------
# STAGES_VALIDATION — robustness/validation runner (run_pipeline_validation).
# All predicates reuse the module-scope handles in _VALIDATION_PREDS so that
# `is` identity holds across import sites.
# ----------------------------------------------------------------------------


STAGES_VALIDATION: list[StageSpec] = [
    StageSpec(
        name="阶段31: 阈值敏感性分析",
        script="31_bank_fintech_threshold.py",
        group="validation", kind="sensitivity",
        enabled_when=_VALIDATION_PREDS['threshold_sensitivity'],
    ),
    StageSpec(
        name="阶段32: 人工抽样验证样本生成",
        script="32_news_llms_human.py",
        group="validation", kind="human",
        # always_enabled — the legacy runner has no flag for stage 32
    ),
    StageSpec(
        name="阶段32a: 去重阈值敏感性分析",
        script="32a_dedup_threshold_sensitivity.py",
        group="validation", kind="sensitivity",
        enabled_when=_VALIDATION_PREDS['dedup_sensitivity'],
    ),
    StageSpec(
        name="阶段33: 分类有效性评估",
        script="33_news_llms_evaluation.py",
        group="validation", kind="evaluation",
        enabled_when=_VALIDATION_PREDS['classification_eval'],
    ),
    StageSpec(
        name="阶段34: 情感三角验证",
        script="34_tone_validation.py",
        group="validation", kind="evaluation",
        enabled_when=_VALIDATION_PREDS['sentiment_validation'],
    ),
    StageSpec(
        name="阶段35: 窗口半径敏感性检验",
        script="35_radius_sensitivity.py",
        group="validation", kind="sensitivity",
        enabled_when=_VALIDATION_PREDS['radius_sensitivity'],
    ),
    StageSpec(
        name="阶段36: Entity Masking 稳健性测试",
        script="36_entity_masking_test.py",
        group="validation", kind="robustness",
        enabled_when=_VALIDATION_PREDS['entity_masking'],
    ),
    StageSpec(
        name="阶段37: 金融科技词典覆盖率审计",
        script="37_dict_coverage_audit.py",
        group="validation", kind="audit",
        enabled_when=_VALIDATION_PREDS['dict_coverage_audit'],
    ),
    StageSpec(
        name="阶段38: 媒体名称与地域多样性审计",
        script="38_media_diversity.py",
        group="validation", kind="audit",
        enabled_when=_VALIDATION_PREDS['media_diversity'],
    ),
    StageSpec(
        name="阶段38a: 时间掩码前视偏误检验",
        script="38a_temporal_mask_test.py",
        group="validation", kind="robustness",
        enabled_when=temporal_mask_enabled,
    ),
    StageSpec(
        name="阶段38b: 距离衰减权重敏感性检验",
        script="38b_decay_sensitivity.py",
        group="validation", kind="sensitivity",
        # always_enabled — legacy runner has no flag for 38b
    ),
    StageSpec(
        name="阶段39: Prompt措辞敏感度测试",
        script="39_prompt_sensitivity.py",
        group="validation", kind="robustness",
        enabled_when=_VALIDATION_PREDS['prompt_sensitivity'],
    ),
]


# ----------------------------------------------------------------------------
# Convenience helpers for orchestrators / tests.
# ----------------------------------------------------------------------------


def filter_enabled(stages: list[StageSpec],
                   config: dict[str, Any]) -> list[StageSpec]:
    """Return the subset of ``stages`` whose ``enabled_when(config)`` is True."""
    return [s for s in stages if s.enabled_when(config)]
