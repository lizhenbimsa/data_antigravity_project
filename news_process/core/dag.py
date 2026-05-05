"""news_process.core.dag — 声明式流水线 DAG.

Phase 1 交付物: ``StageSpec`` 数据类 + ``STAGES_MAIN`` / ``STAGES_VALIDATION``
列表。这两份列表是 "哪些阶段存在 / 何时运行" 的 **单源真值**;
``run_pipeline_function.py`` (主流水线执行器) 与
``run_pipeline_validation.py`` (验证执行器) 都从此处 import 自己的
``STAGES`` 常量, 并由 ``tests/integration/test_dag_consistency.py``
通过 ``is`` 身份比对验证两端绑定一致。

命名纪律: ``StageSpec`` 是 DAG 中使用的 *声明式* 记录 (frozen dataclass);
刻意与未来某 phase 将在 ``core/stage.py`` 引入的 *运行时* ``Stage``
抽象基类区分开, 以避免命名冲突。

配置条件性动态分支 (例如 sentiment.enabled_methods 决定 21/22/23 启停)
通过 ``enabled_when`` 谓词捕获, 而非 orchestrator 内部分支。谓词必须是
模块级 Python callable, 这样在多个 import 站点之间 ``is`` 身份比对才有
意义 — DAG 一致性测试依赖这一点。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


# ----------------------------------------------------------------------------
# enabled_when 谓词集。声明在模块作用域, 以使 ``is`` 身份比对跨 import 站点
# 仍然成立 — DAG 一致性测试依赖此性质来确认两个 orchestrator 复用同一个
# 谓词对象。
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
    """返回一个读取 ``cfg['validation'][key]`` 的谓词 (默认值 True)。"""
    def predicate(cfg: dict[str, Any]) -> bool:
        return cfg.get('validation', {}).get(key, default)
    predicate.__name__ = f"validation_{key}_enabled"
    return predicate


def temporal_mask_enabled(cfg: dict[str, Any]) -> bool:
    return cfg.get('temporal_mask_test', {}).get('enabled', False)


# 验证模块谓词句柄集 — 仅在模块作用域声明一次, 以使
# core/dag.STAGES_VALIDATION 与 run_pipeline_validation.STAGES 复用同一
# 个 callable 对象。
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
# StageSpec — 声明式 DAG 记录。
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class StageSpec:
    """单个流水线阶段的声明式描述符。

    Attributes:
        name:         人类可读的阶段标签 (用于日志、摘要)。
        script:       相对于项目根的文件名 (``"00_preprocessing.py"``)。
        group:        ``"main"`` | ``"validation"`` | ``"feature"``。
        kind:         自由格式的类别标签。
        timeout:      子进程超时秒数。
        enabled_when: 谓词 ``(cfg) -> bool``, 决定运行时是否纳入该阶段;
                      无条件运行的阶段使用 ``always_enabled``。

    Phase 1 刻意不填充 ``inputs`` / ``outputs`` 字段;
    Phase 2d 将通过 ``core.schemas.OUTPUT_REGISTRY`` 串接二者。
    """

    name: str
    script: str
    group: str
    kind: str = "stage"
    timeout: int = 3600
    enabled_when: Callable[[dict[str, Any]], bool] = always_enabled


# ----------------------------------------------------------------------------
# STAGES_MAIN — 生产流水线 DAG (run_pipeline_function)。
# 镜像 run_pipeline_function.py:run_pipeline() 的 stages 列表;
# 配置驱动的条件分支通过 enabled_when 谓词捕获。
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
        timeout=7200,  # 阶段内含 Embedding API 调用
    ),

    # ── 模块三：新闻情感模块 (由 sentiment_analysis.enabled_methods 配置条件性启停) ──
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

    # ── 模块四c：text2vec 双轨稳健性指标 (战略差异 + 政策对齐 _full/_ctx) ──
    StageSpec(
        name="阶段30: text2vec 双轨稳健性指标",
        script="30_robustness_text2vec.py",
        group="main", kind="robustness",
        timeout=7200,  # 含 sentence-transformers 本地 GPU 编码 (双轨)
    ),

    # ── 模块五：面板数据构建 ──
    StageSpec(
        name="阶段40-45: Bank-Year 面板数据构建",
        script="45_panel_export_main.py",
        group="main", kind="panel",
        timeout=7200,  # 阶段内含 Stage 25/26/27 Embedding 计算
    ),

    # ── 模块六：伪造检验 ──
    StageSpec(
        name="阶段51: 伪造检验对照变量构建",
        script="51_falsification_test.py",
        group="main", kind="falsification",
    ),
]


# ----------------------------------------------------------------------------
# STAGES_VALIDATION — 稳健性/验证执行器 (run_pipeline_validation)。
# 所有谓词复用 _VALIDATION_PREDS 中的模块级句柄, 以使 `is` 身份比对
# 跨 import 站点成立。
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
        # always_enabled — 历史 runner 对 stage 32 没有专门的 flag
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
        # always_enabled — 历史 runner 对 38b 没有专门的 flag
    ),
    StageSpec(
        name="阶段39: Prompt措辞敏感度测试",
        script="39_prompt_sensitivity.py",
        group="validation", kind="robustness",
        enabled_when=_VALIDATION_PREDS['prompt_sensitivity'],
    ),
]


# ----------------------------------------------------------------------------
# 供 orchestrator / 测试使用的便捷工具函数。
# ----------------------------------------------------------------------------


def filter_enabled(stages: list[StageSpec],
                   config: dict[str, Any]) -> list[StageSpec]:
    """返回 ``stages`` 中 ``enabled_when(config)`` 为 True 的子集。"""
    return [s for s in stages if s.enabled_when(config)]
