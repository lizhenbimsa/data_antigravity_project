# `StageSpec` 与声明式 DAG

`news_process.core.dag` 是 v2.0 的**单源 DAG 真值**。两个 orchestrator
（`run_pipeline_function.py` + `run_pipeline_validation.py`）都从这里
import 阶段定义，无任何重复。

## 1. `StageSpec` Dataclass

```python
@dataclass(frozen=True)
class StageSpec:
    name: str                                          # 人类可读阶段名
    script: str                                        # 文件名: "11_news_bank.py"
    group: str                                         # "main" | "validation" | "feature"
    kind: str = "stage"                                # 自由分类标签
    timeout: int = 3600                                # subprocess 超时秒数
    enabled_when: Callable[[dict], bool] = always_enabled  # 启用谓词
```

`frozen=True`：`StageSpec` 实例是 hashable + immutable，可作为 set
元素 / dict key。

## 2. `enabled_when` 谓词

谓词是 `(config: dict) -> bool` 的 callable。返回 `True` 时 orchestrator
将该 stage 加入执行队列。

### 内置谓词

```python
def always_enabled(_cfg: dict) -> bool:
    return True

def llm_method_enabled(cfg: dict) -> bool:
    return 'tone_llms' in cfg.get('sentiment_analysis', {}).get('enabled_methods', [])

def words_method_enabled(cfg: dict) -> bool:
    return 'tone_words' in cfg.get('sentiment_analysis', {}).get('enabled_methods', [])

def berts_method_enabled(cfg: dict) -> bool:
    return 'tone_berts' in cfg.get('sentiment_analysis', {}).get('enabled_methods', [])

def temporal_mask_enabled(cfg: dict) -> bool:
    return cfg.get('temporal_mask_test', {}).get('enabled', False)
```

### `_validation_flag()` 工厂

11 个 validation 谓词共享同一工厂：

```python
def _validation_flag(key: str, default: bool = True
                     ) -> Callable[[dict], bool]:
    def predicate(cfg: dict) -> bool:
        return cfg.get('validation', {}).get(key, default)
    predicate.__name__ = f"validation_{key}_enabled"
    return predicate

_VALIDATION_PREDS = {
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
```

```{warning}
**关键约束**：谓词必须是**模块级** callable，不能是 lambda 或局部
closure。`test_dag_consistency.py` 用 `is` 比对 orchestrator 持有的谓词
对象与 `core.dag` 模块属性，要求**身份相等**（不仅 ==）。lambda 在每次
import 时是新对象，会破坏此契约。
```

## 3. `STAGES_MAIN`（11 阶段）

```python
STAGES_MAIN: list[StageSpec] = [
    StageSpec(name="阶段00: 数据预处理",
              script="00_preprocessing.py",
              group="main", kind="preprocess",
              timeout=10000),  # 大 timeout（22 GB 数据需要 ~30 min）

    StageSpec(name="阶段11: 银行新闻判断",
              script="11_news_bank.py",
              group="main", kind="filter"),
    StageSpec(name="阶段12: 金融科技新闻判断 + 全量分类结果",
              script="12_news_fintech.py",
              group="main", kind="filter"),
    StageSpec(name="阶段14: 金融科技技术重度评分 (TF-IDF)",
              script="14_fintech_intensity.py",
              group="main", kind="filter"),
    StageSpec(name="阶段15: 文章级政策语义对齐度",
              script="15_article_policy_alignment.py",
              group="main", kind="filter",
              timeout=7200),  # Embedding API 慢

    StageSpec(name="阶段21: 统一 LLM 语义精筛与情感分析",
              script="21_tone_llms.py",
              group="main", kind="sentiment",
              enabled_when=llm_method_enabled),
    StageSpec(name="阶段22: 词典法情感分析",
              script="22_tone_words.py",
              group="main", kind="sentiment",
              enabled_when=words_method_enabled),
    StageSpec(name="阶段23: BERT模型情感分析",
              script="23_tone_berts.py",
              group="main", kind="sentiment",
              enabled_when=berts_method_enabled),
    StageSpec(name="阶段24: 跟风衰减权重",
              script="24_herd_decay_processor.py",
              group="main", kind="sentiment"),

    StageSpec(name="阶段40-45: Bank-Year 面板数据构建",
              script="45_panel_export_main.py",
              group="main", kind="panel",
              timeout=7200),  # Stage 25/26/27 Embedding 慢

    StageSpec(name="阶段51: 伪造检验对照变量构建",
              script="51_falsification_test.py",
              group="main", kind="falsification"),
]
```

## 4. `STAGES_VALIDATION`（12 阶段）

```python
STAGES_VALIDATION: list[StageSpec] = [
    StageSpec(name="阶段31: 阈值敏感性分析",
              script="31_bank_fintech_threshold.py", group="validation",
              kind="sensitivity",
              enabled_when=_VALIDATION_PREDS['threshold_sensitivity']),

    StageSpec(name="阶段32: 人工抽样验证样本生成",
              script="32_news_llms_human.py", group="validation",
              kind="human"),  # always_enabled (legacy 无 flag)

    StageSpec(name="阶段32a: 去重阈值敏感性分析",
              script="32a_dedup_threshold_sensitivity.py", group="validation",
              kind="sensitivity",
              enabled_when=_VALIDATION_PREDS['dedup_sensitivity']),

    StageSpec(name="阶段33: 分类有效性评估",
              script="33_news_llms_evaluation.py", group="validation",
              kind="evaluation",
              enabled_when=_VALIDATION_PREDS['classification_eval']),

    StageSpec(name="阶段34: 情感三角验证",
              script="34_tone_validation.py", group="validation",
              kind="evaluation",
              enabled_when=_VALIDATION_PREDS['sentiment_validation']),

    StageSpec(name="阶段35: 窗口半径敏感性检验",
              script="35_radius_sensitivity.py", group="validation",
              kind="sensitivity",
              enabled_when=_VALIDATION_PREDS['radius_sensitivity']),

    StageSpec(name="阶段36: Entity Masking 稳健性测试",
              script="36_entity_masking_test.py", group="validation",
              kind="robustness",
              enabled_when=_VALIDATION_PREDS['entity_masking']),

    StageSpec(name="阶段37: 金融科技词典覆盖率审计",
              script="37_dict_coverage_audit.py", group="validation",
              kind="audit",
              enabled_when=_VALIDATION_PREDS['dict_coverage_audit']),

    StageSpec(name="阶段38: 媒体名称与地域多样性审计",
              script="38_media_diversity.py", group="validation",
              kind="audit",
              enabled_when=_VALIDATION_PREDS['media_diversity']),

    StageSpec(name="阶段38a: 时间掩码前视偏误检验",
              script="38a_temporal_mask_test.py", group="validation",
              kind="robustness",
              enabled_when=temporal_mask_enabled),  # 单独 flag

    StageSpec(name="阶段38b: 距离衰减权重敏感性检验",
              script="38b_decay_sensitivity.py", group="validation",
              kind="sensitivity"),  # always_enabled

    StageSpec(name="阶段39: Prompt措辞敏感度测试",
              script="39_prompt_sensitivity.py", group="validation",
              kind="robustness",
              enabled_when=_VALIDATION_PREDS['prompt_sensitivity']),
]
```

```{note}
**为什么 30 不在 `STAGES_VALIDATION`？**
`30_robustness_text2vec.py` 是阶段 30 的 thin shim → `validation/text2vec.py`
存在但**不在 DAG 中**。它是按需手动调用的辅助检验，不进流水线编排。
```

## 5. `filter_enabled` 公开 API

```python
def filter_enabled(stages: list[StageSpec],
                   config: dict) -> list[StageSpec]:
    """Return stages whose ``enabled_when(config)`` returns True."""
    return [s for s in stages if s.enabled_when(config)]
```

orchestrator 用法：

```python
# run_pipeline_function.py
from news_process.core.dag import STAGES_MAIN, filter_enabled
from news_process.core.config import load_config

CONFIG = load_config()
active_specs = filter_enabled(STAGES_MAIN, CONFIG)
stages = [(s.script, s.name, s.timeout) for s in active_specs]

for script, name, timeout in stages:
    success, elapsed = run_stage(script, name, logger, SCRIPT_DIR, timeout=timeout)
    # ...
```

## 6. DAG 一致性测试

`tests/integration/test_dag_consistency.py` 验证：

1. orchestrator 中 `STAGES` 与 `core.dag.STAGES_MAIN` 是**身份相等**：
   ```python
   from news_process.run_pipeline_function import STAGES as RPF_STAGES
   from news_process.core.dag import STAGES_MAIN
   assert RPF_STAGES is STAGES_MAIN
   ```
2. 每个 `StageSpec.enabled_when` 在 orchestrator 与 `core.dag` 中是同一
   callable 对象（`is` 等价）。

`tests/integration/test_papers_imports.py::test_paper_analysis_has_stages_list`
验证每篇论文的 `analysis.STAGES`：

1. 存在且为非空 list
2. 通常由 ``STAGES = list(STAGES_MAIN)`` 拷贝得到 (允许切片如
   ``list(STAGES_MAIN[:N])``)

> Phase 9a 改动: 原 ``test_papers_dag_consistency.py`` 用 16 个测试守护
> '5 个空壳必须 == STAGES_MAIN' (即 16 个测试守护 0 个差异), 已整删;
> ``papers.<id>.dag`` 子模块也已删除, ``STAGES`` 直接挂在 ``analysis``
> 模块顶部.

## 7. 扩展 DAG（添加新 stage）

详见 [新增 Stage 指南](../guides/adding_stage.md)。

## 8. 见也

* [`core.dag` API 参考](../api/core.md)
* [Thin shim 设计模式](../guides/thin_shim_pattern.md)
* [配置拆分指南](../guides/config_split.md)
