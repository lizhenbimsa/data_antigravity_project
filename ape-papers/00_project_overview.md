# APEP 项目完整复现指南 — 概述

> **Autonomous Policy Evaluation Papers (APEP)**
> 自主政策评估工作论文系统

## 项目简介

APEP 是一个**AI 自主科学研究**实验平台。AI 智能体（Agent）能够自动完成从选题到论文发表的完整流程：

1. **选题** — 识别具有可信因果识别策略的政策研究问题
2. **数据获取** — 从公共 API（Census、BLS、FRED 等）获取真实数据
3. **计量分析** — 执行双重差分法（DiD）、断点回归设计（RDD）等计量经济学分析
4. **论文撰写** — 生成完整的 LaTeX 学术论文
5. **同行评审** — 经过多模型评审（GPT-5-mini, Grok-4.1-Fast, Gemini-3-Flash, Codex-Mini）
6. **修订迭代** — 根据评审意见自动修订论文

## 仓库来源

- GitHub: https://github.com/SocialCatalystLab/ape-papers
- 维护者: [Social Catalyst Lab](https://github.com/SocialCatalystLab)

## 核心机制

```
公共镜像（本仓库）  ←  自动同步  ←  私有生产仓库
```

- **包含**: 完整复现包 — PDF、LaTeX 源码、R 代码、数据
- **不包含**: 生产基础设施（竞赛系统、评审管道、Agent 代码）

## 单篇论文文件夹结构

```
apep_XXXX/
├── v1/                         # 版本目录（可能有 v2, v3...）
│   ├── paper.pdf               # 最终 PDF
│   ├── paper.tex               # LaTeX 源码
│   ├── metadata.json           # 自描述元数据
│   ├── initial_plan.md         # 原始研究计划（首次提交后不再修改）
│   ├── research_plan.md        # 最终研究计划（演进版本）
│   ├── ideas.md                # 研究创意候选列表
│   ├── ideas_ranked.json       # 创意排序与评分
│   ├── ranking.md              # 排名分析
│   ├── REPLICATION.md          # 复现指南
│   ├── scan_report.json        # 质量扫描报告
│   ├── revision_plan_1.md      # 第1轮修订计划
│   ├── reply_to_reviewers_1.md # 回复评审意见
│   ├── review_gpt_*.md         # GPT 模型评审
│   ├── review_cc_*.md          # 其他模型评审
│   ├── code/                   # R 分析脚本
│   │   ├── 00_packages.R       # 依赖包安装
│   │   ├── 01_fetch_data.R     # 数据获取
│   │   ├── 03_main_analysis.R  # 主要分析
│   │   └── 05_figures.R        # 图表生成
│   ├── data/                   # 复现数据（或通过 API 获取）
│   ├── figures/                # 生成的图表
│   └── tables/                 # 生成的表格
```

## 质量标准

所有论文均需满足：
- ✅ 研究计划在数据分析前提交（git 时间戳证明顺序）
- ✅ 通过多模型评审（GPT-5-mini, Grok-4.1-Fast, Gemini-3-Flash, Codex-Mini）
- ✅ 完整的复现包（`code/` 和 `data/`）
- ✅ 贡献者归因
- ✅ 自描述的 `metadata.json`

## 主要研究方法

| 方法缩写 | 全名                                            | 适用场景                             |
| -------- | ----------------------------------------------- | ------------------------------------ |
| DiD      | Difference-in-Differences（双重差分法）         | 政策的交错实施（Staggered adoption） |
| RDD      | Regression Discontinuity Design（断点回归设计） | 基于年龄/收入等阈值的政策效果        |
| DR       | Doubly Robust（双重稳健）                       | 需要同时控制选择偏差和模型错误       |

## 文档索引

| 文档                                 | 内容                     |
| ------------------------------------ | ------------------------ |
| [01_环境配置.md](01_环境配置.md)     | R/LaTeX/API 环境搭建     |
| [02_复现流程.md](02_复现流程.md)     | 端到端工作流程           |
| [03_提示词集合.md](03_提示词集合.md) | AI Agent 各阶段提示词    |
| [04_R代码模板/](04_R代码模板/)       | DiD/RDD 分析代码模板     |
| [05_论文模板/](05_论文模板/)         | LaTeX 论文模板           |
| [06_评审系统.md](06_评审系统.md)     | 多模型评审流程           |
| [07_数据源指南.md](07_数据源指南.md) | 公共数据 API 参考        |
| [08_配置模板/](08_配置模板/)         | metadata.json 等配置模板 |
