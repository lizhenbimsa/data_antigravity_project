# AutoPaper 项目完整复现指南 — 概述

> **Autonomous Paper System (AutoPaper)**
> 自主政策评估工作论文系统

## 项目简介

AutoPaper 是一个**AI 自主科学研究**实验平台。AI 智能体（Agent）能够自动完成从选题到论文发表的完整流程：

1. **选题** — 识别具有可信因果识别策略的政策研究问题
2. **数据加载与清洗** — 从项目提供的统一本地 DTA 数据库中提取和关联所需变量
3. **计量分析** — 执行双重差分法（DiD）、断点回归设计（RDD）等计量经济学分析
4. **论文撰写** — 生成完整的 Markdown 学术论文
5. **同行评审** — 经过多模型评审（GPT-5-mini, Grok-4.1-Fast, Gemini-3-Flash, Codex-Mini）
6. **修订迭代** — 根据评审意见自动修订论文

## 核心机制

```
公共镜像（本仓库）  ←  自动同步  ←  私有生产仓库
```

   - **数据与分析**: LLM 生成 Stata do 脚本提取数据并执行回归，本地安全执行代码、统一格式的本地 DTA 数据
- **不包含**: 生产基础设施（竞赛系统、评审管道、Agent 代码）

## 单篇论文文件夹结构

```
paper_XXXX/
├── v1/                         # 版本目录（可能有 v2, v3...）
│   ├── paper.md                # Markdown 源码
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
│   ├── code/                   # Stata 分析脚本
│   │   ├── 00_packages.do      # 依赖包安装
│   │   ├── 01_fetch_data.do    # 本地数据加载与清洗
│   │   ├── 03_main_analysis.do # 主要分析
│   │   └── 05_figures.do       # 图表生成
│   ├── data/                   # 本地复现数据（包含必须的 DTA 数据文件或链接）
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

| 文档                                       | 内容                        |
| ------------------------------------------ | --------------------------- |
| [01_env_config.md](01_env_config.md)       | Stata/API 环境搭建          |
| [02_replication.md](02_replication.md)     | 人工检查与复现说明          |
| [03_prompts.md](03_prompts.md)             | 驱动流水线的各类提示词      |
| [04_stata_templates/](04_stata_templates/) | DiD/RDD 分析 Stata 模板     |
| [06_评审系统.md](06_评审系统.md)           | 多模型评审流程              |
| [07_数据源指南.md](07_数据源指南.md)       | 本地 DTA 数据指南及字段概览 |
| [08_配置模板/](08_配置模板/)               | metadata.json 等配置模板    |
