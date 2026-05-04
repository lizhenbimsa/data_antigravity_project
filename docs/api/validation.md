# `news_process.validation` — 验证模块 API

`validation` 是 v2.0 重构（Phase 7b）从根级数字前缀脚本迁入的扁平包，
包含 13 个独立的稳健性检验 / 三角验证 / 敏感性分析模块，由
``run_pipeline_validation.py`` 编排。

设计原则：**扁平布局**而非按子分类再划分子包。理由是 12 个验证模块彼此**独立、关系平行**，
强行加一层 `validation/sensitivity/`、`validation/comparison/` 的分组反而增加耦合，
违反 Occam's Razor。

```{eval-rst}
.. autosummary::

   news_process.validation.text2vec
   news_process.validation.threshold
   news_process.validation.llms_human
   news_process.validation.dedup_threshold
   news_process.validation.llms_evaluation
   news_process.validation.tone_validation
   news_process.validation.radius_sensitivity
   news_process.validation.entity_masking
   news_process.validation.dict_coverage
   news_process.validation.media_diversity
   news_process.validation.temporal_mask
   news_process.validation.decay_sensitivity
   news_process.validation.prompt_sensitivity
```

## 验证矩阵速查

| 阶段 | 模块 | 检验类型 | 学术依据 |
|---|---|---|---|
| 30 | `text2vec` | 文本相似度稳健性 | Mikolov et al. (2013) Word2Vec |
| 31 | `threshold` | 阈值敏感性（11/12 分类参数） | Loughran-McDonald (2011, JF) |
| 32 | `llms_human` | 人工抽样验证样本生成 | — |
| 32a | `dedup_threshold` | 去重阈值敏感性 | Broder (1997, IEEE SEQUENCES) |
| 33 | `llms_evaluation` | LLM 一致性评估 | Cohen's κ + Krippendorff's α |
| 34 | `tone_validation` | 情感三角验证 | Denzin (1978) Triangulation |
| 35 | `radius_sensitivity` | 上下文窗口半径 | Hassan et al. (2019, QJE) |
| 36 | `entity_masking` | 实体掩码稳健性 | Carlson & Burbano (2026, SMJ) |
| 37 | `dict_coverage` | 金融科技词典覆盖率审计 | Cochran-Armitage Trend Test |
| 38 | `media_diversity` | 媒体来源 + 地域多样性 | HHI / Shannon / Gini |
| 38a | `temporal_mask` | 时间掩码（前视偏误） | Tetlock (2008, JF) |
| 38b | `decay_sensitivity` | 距离衰减权重稳健性 | uniform / inverse / exponential |
| 39 | `prompt_sensitivity` | Prompt 措辞敏感度 | Wang et al. (2023, ICLR) Self-consistency |

## 调用约定

每个 validation 模块遵循统一的入口契约：

* 顶层定义 `STAGE_NAME = "NN_xxx"`（与 `core/dag.STAGES_VALIDATION` 中的 `script` 字段对应）
* 顶层定义 `main()` 函数，接受零参数，从 `core.config.load_config()` 读取所有运行参数
* 通过 `if __name__ == "__main__": main()` 支持 `python -m news_process.validation.<name>` 直接调用
* 历史 `python NN_xxx.py` 调用契约由项目根目录极薄 CLI 兼容脚本保留
