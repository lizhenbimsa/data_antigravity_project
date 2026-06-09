# news_process v{{version}}

**银行金融科技舆情面板分析流水线** — 一套端到端的中文新闻文本处理系统，
从 ~37 GB 原始 XLSX 媒体报道生成可用于计量经济学研究的银行—年面板数据，
支持 **11 个独立的研究产品（论文）** 共享同一处理内核（Bank-FinTech 主线 5 篇 P1-P5 + 衍生 4 篇 + v3.7.0 立项 2 篇）。

```{admonition} 当前版本
:class: tip

**v3.7.0 + v2.3 implementation (2026-05-18; 最近 git tag: v3.6.0)**：
v2.1.0 八期重构 + Phase 9 cleanup 后，主线持续演进至 v3.7.x 多 epoch:
v3.2.0 三轨化双轨 + v3.4.0 第三维度 collab_mode + v3.5.0/v3.5.1 Stage 3
augmentation + v3.6.0 Plan E 双轨闭合 + v3.7.0 D 组 (staleness
/ α) + v2.3 集成层. 完整演进史见 [CHANGELOG](changelog.md) 与
[news_process/CLAUDE.md](https://github.com/example/news_process/blob/main/news_process/CLAUDE.md) 顶部 "Current version" 段。
```

## 30 秒导航

| 你想… | 看这里 |
|---|---|
| 5 分钟跑通 hello world | [快速上手](tutorial/01_quickstart.md) |
| 跑完整主流水线（22 GB 数据） | [主流水线教程](tutorial/02_main_pipeline.md) |
| 跑稳健性 / 三角验证模块 | [验证模块教程](tutorial/03_validation.md) |
| 同时驱动多篇论文 | [多论文工作流](tutorial/04_multi_paper.md) |
| 在 Stata 里调用面板 | [Stata 集成](tutorial/05_stata_integration.md) |
| 添加一个新阶段 | [新增 Stage 指南](guides/adding_stage.md) |
| 添加一个新研究产品 | [新增 Paper 指南](guides/adding_paper.md) |
| 理解声明式 DAG | [`StageSpec` 参考](reference/dag.md) |
| 找具体函数 / 类的文档 | [API 参考](api/core.md) |

## 核心特性（v3.7.0 当前态 / 下方 mermaid 仍反映 v2.1.0 epoch 阶段命名）

```{mermaid}
graph LR
    A[~37 GB XLSX 原始数据] -->|阶段 00| B[预处理]
    B -->|阶段 11/12/14| C[新闻筛选]
    C -->|阶段 15| C2[政策对齐]
    C2 -->|阶段 21-24| D[情感分析]
    D -->|阶段 41-48| E[Bank-Year 面板]
    E -->|阶段 51| F[伪造检验]
    E -->|阶段 52/53| G[Stata 审计 + 摘要]

    E -.->|阶段 30-39| V[验证模块矩阵]
    E -.->|paper_id 调度| P[多论文产品]
```

### 架构亮点

* **声明式 DAG 单源真值**：`news_process.core.dag.STAGES_MAIN` /
  `STAGES_VALIDATION` 是流水线编排的**唯一**事实来源；两个 orchestrator
  均通过 `filter_enabled(STAGES, CONFIG)` 消费，无内联 if-append 链。
* **Thin shim 调用契约**：v2.1.0 共 26 个数字前缀 root script，v3.x 演进
  到 **39 个**（含字母后缀 32a/38a/38b/39a/39c/39d/39e/39f/30a），全部
  统一为 ≤30 行 thin shim，保留 `python NN_xxx.py` 历史 subprocess
  调用契约，body 全部迁入 `news_process.{pipeline,validation}` 子包。
* **7 域配置拆分**：`config/{paths,preprocessing,filtering,sentiment,
  features,panel,validation}.yaml` + 外部化 prompt 模板，避免单文件巨石
  化。`load_config()` 自动 deep-merge + prompt 内联，对消费方 API 完全
  透明。
* **多论文产品化**：`papers/<paper_id>/` 是 Python 代码层；
  `papers_assets/<paper_id>/` 是非代码研究资产（Stata `.do`、drafts、
  output）。共享 `_common` 内核（`PaperConfig`、`load_panel`、tables/
  figures helpers、`stata_runner`）。
* **完整 rollback 锚点链**：从 `baseline-pre-restructure` 到
  `phase-9-baseline` / `v2.1.0` / `v3.2.0` / `v3.6.0` (2026-05-18 最近 tag),
  单点 `git revert <hash>` 可回滚任意子阶段。v3.5.2 / v3.6.1 / v3.7.0
  / v3.7.1 / v2.3 已合入 main 但未独立 tag。详见
  [Rollback 指南](reference/rollback_anchors.md)。

## 文档导航

```{toctree}
:maxdepth: 2
:caption: 总览

architecture
changelog
```

```{toctree}
:maxdepth: 2
:caption: 教程

tutorial/01_quickstart
tutorial/02_main_pipeline
tutorial/03_validation
tutorial/04_multi_paper
tutorial/05_stata_integration
```

```{toctree}
:maxdepth: 2
:caption: 开发指南

guides/adding_stage
guides/adding_paper
guides/config_split
guides/thin_shim_pattern
```

```{toctree}
:maxdepth: 2
:caption: 概念参考

reference/dag
reference/rollback_anchors
reference/output_registry
reference/env_vars
```

```{toctree}
:maxdepth: 2
:caption: API 参考

api/core
api/pipeline
api/validation
api/papers
```

## 索引与搜索

* {ref}`genindex` — 字母索引（所有公开 API 名称）
* {ref}`modindex` — 模块索引
* {ref}`search` — 全文搜索（中文友好，已启用 Sphinx jieba 分词）
