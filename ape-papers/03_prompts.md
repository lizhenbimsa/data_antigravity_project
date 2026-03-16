# APEP 复现 — AI 提示词集合

> 以下提示词用于驱动 AI Agent 完成 APEP 项目各阶段的工作。
> 每个提示词都可直接复制使用，仅需替换 `{变量}` 部分。

---

## 1. 创意生成提示词

### 1.1 生成研究创意

```
你是一位计量经济学研究者。请为政策评估研究生成 5 个具有可信因果识别策略的研究创意。

要求：
1. 每个创意必须使用以下方法之一:
   - 双重差分法 (Difference-in-Differences, DiD) — 适用于政策在不同州/时间交错实施的情况
   - 断点回归设计 (Regression Discontinuity Design, RDD) — 适用于基于年龄/收入/分数等存在明确阈值的情况

2. 数据必须可从以下公共 API 免费获取:
   - US Census Bureau ACS (tidycensus)
   - Bureau of Labor Statistics (blsAPI)
   - Federal Reserve FRED (fredr)

3. 每个创意需包含以下结构:
   ## 创意 N: [标题]
   **研究问题**: [一句话描述因果关系]
   **政策背景**: [2-3 句描述政策]
   **识别策略**: [DiD/RDD，解释为什么可信]
   **数据来源**: [具体 API 和变量]
   **预期结果**: [假设方向及理由]
   **原创性评分**: [1-10]
   **可行性评分**: [1-10]

4. 避免以下已被广泛研究的主题:
   - 最低工资对就业的基本效果
   - ACA 对保险覆盖率的基本效果
   - 基础的枪支管制研究

请确保每个想法都有清晰的排他组和控制组定义。
```

### 1.2 创意排名提示词

```
请对以下 5 个研究创意进行排名和评分。评分维度:

1. **原创性** (0-10): 是否填补了学术文献的空白？
2. **可行性** (0-10): 数据是否真实可获取？API 是否稳定？
3. **因果可信度** (0-10): 识别策略是否能说服 AER/AEJ 编辑？
4. **政策相关性** (0-10): 结论对政策制定者是否有价值？

请输出 JSON 格式:
```json
{
  "rankings": [
    {
      "idea_id": 1,
      "title": "...",
      "originality": 8,
      "feasibility": 9,
      "causal_credibility": 7,
      "policy_relevance": 8,
      "total": 32,
      "ranking_rationale": "..."
    }
  ],
  "recommended": 1,
  "recommendation_rationale": "..."
}
```

[在此粘贴 ideas.md 的内容]
```

---

## 2. 研究计划提示词

### 2.1 初始研究计划

```
你是一位高级计量经济学家。请为以下研究主题撰写一份详细的研究计划 (initial_plan.md)。

研究主题: {选定的研究创意}

研究计划必须包含以下部分:

## 1. 研究问题
[清晰、可检验的因果命题]

## 2. 文献回顾
[该领域 5-8 篇关键参考文献，说明本研究的边际贡献]

## 3. 制度背景
[政策实施的时间线、具体内容、实施州/地区]

## 4. 识别策略

### 4.1 方法选择
[详细解释为什么选择 {DiD/RDD}]

### 4.2 主要回归模型
[LaTeX 公式，如:]
$$Y_{ist} = \alpha + \beta \cdot D_{st} + \gamma_s + \delta_t + \epsilon_{ist}$$
其中:
- $Y_{ist}$: 个体 i 在州 s 第 t 年的结果变量
- $D_{st}$: 处理指示变量
- $\gamma_s$: 州固定效应
- $\delta_t$: 年份固定效应

### 4.3 识别假设
[平行趋势假设/连续性假设的论证]

## 5. 数据

### 5.1 数据来源
[具体 API、表名、变量代码]

### 5.2 时间范围
[如 2010-2023]

### 5.3 样本定义
[如 18-64 岁劳动力人口]

### 5.4 核心变量
| 变量名 | 描述     | 来源     | 代码       |
| ------ | -------- | -------- | ---------- |
| Y      | 就业率   | ACS      | B23025_004 |
| treat  | 政策实施 | 手动编码 | —          |

## 6. 稳健性检验
- 安慰剂检验
- 子样本分析
- 替代度量
- 预趋势敏感性

## 7. 预期结果与贡献
[假设方向及对政策的意义]
```

---

## 3. 数据获取提示词

### 3.1 R 数据获取代码

```
你是一位 R 程序员。请编写一个 R 脚本 (01_fetch_data.R) 来获取以下研究的数据:

研究计划:
{粘贴 initial_plan.md 的内容}

要求:
1. 使用 tidycensus 包从 Census ACS API 获取数据
2. 需要 Census API Key（通过 census_api_key() 设置）
3. 变量列表参考: https://api.census.gov/data/2022/acs/acs1/variables.html
4. 循环获取 {起始年份} 到 {结束年份} 的数据
5. 构建处理变量 (treatment indicator)，定义各州的政策实施年份
6. 生成州-年面板数据集
7. 保存为 RDS 格式到 output/ 目录
8. 包含详细注释解释每个变量
9. 添加数据质量检查（缺失值、异常值、样本量报告）

代码结构:
- 加载包
- 设置 API Key
- 定义变量列表
- 定义政策实施年份（向量）
- 循环获取数据
- 数据清洗与合并
- 构造面板数据
- 生成描述性统计
- 保存输出
```

---

## 4. 计量分析提示词

### 4.1 DiD 分析代码

```
你是一位高级 R 统计程序员。请编写主分析脚本 (03_main_analysis.R)。

研究设计:
- 方法: 交错双重差分法 (Staggered DiD)
- 处理方式: 不同州在不同年份实施政策
- 面板数据: State × Year

要求:
1. 加载 output/ 中的面板数据
2. 运行以下所有估计量:
   a) 标准 TWFE (fixest::feols)
   b) Sun-Abraham 交互加权估计 (fixest::sunab)
   c) Callaway-Sant'Anna (did::att_gt)
   d) did2s 两步估计 (did2s::did2s)
3. 生成事件研究图 (Event Study Plot)
4. 运行稳健性检验:
   - 安慰剂年份检验
   - 子样本分析（按人口统计特征）
   - 不同控制变量组合
5. 生成 modelsummary 回归表格
6. 将所有结果保存到 output/
7. 图表保存为 PDF 到 figures/
8. 所有回归使用州级聚类标准误

变量定义:
- 结果变量: {Y_variable}
- 处理变量: {treatment_indicator}
- 固定效应: state + year
- 聚类: state
```

### 4.2 RDD 分析代码

```
你是一位高级 R 统计程序员。请编写断点回归分析脚本 (03_main_analysis.R)。

研究设计:
- 方法: 断点回归设计 (Sharp RDD)
- 断点变量 (Running variable): {变量名}
- 断点值 (Cutoff): {值}

要求:
1. 使用 rdrobust 包进行非参数局部多项式估计
2. 最优带宽选择 (MSE-optimal bandwidth)
3. 密度检验 (rddensity_test)
4. 安慰剂断点检验 (在假断点处估计)
5. 协变量平衡检验 (在断点处检验协变量是否连续)
6. 不同带宽的敏感性分析
7. RD 图 (rdplot)
8. 置信区间图
```

---

## 5. 论文撰写提示词

### 5.1 完整论文撰写

```
你是一位经济学教授，专长于撰写政策评估论文。请基于以下材料撰写一篇完整的学术论文 (LaTeX 格式):

研究计划: {粘贴 research_plan.md}
分析结果: {粘贴主要回归结果}
图表: {描述图表内容}

论文结构要求:
1. Title: 简洁有力，包含政策名称和方法
2. Abstract: 250 词以内，含方法、发现、意义
3. Introduction (2-3 页): 动机、贡献声明、结构预览
4. Institutional Background (1-2 页): 政策详情和时间线
5. Data (1-2 页): 数据来源、变量定义、描述性统计
6. Empirical Strategy (1-2 页): 模型设定、识别假设论证
7. Results (2-3 页): 主要发现、事件研究图解读
8. Robustness (1-2 页): 稳健性检验汇总
9. Discussion (1 页): 机制探讨、局限性
10. Conclusion (0.5 页): 总结与政策建议

写作风格:
- 参考 AER/AEJ 期刊水平
- 使用被动语态
- 数字精确到小数点后三位
- 结果需有经济学意义的解读
- 引用格式: \citet{} 和 \citep{}

LaTeX 格式要求:
- 使用 article 文档类
- 12pt 字体，双倍行距
- 使用 booktabs 制作表格
- 图表编号和标题规范
- 脚注用于补充细节
```

---

## 6. 同行评审提示词

### 6.1 评审报告生成

```
你是一位严格的学术审稿人，被邀请为一篇提交到顶级经济学期刊的论文撰写评审报告。

请阅读以下论文并撰写详细的评审报告:

{粘贴 paper.tex 或论文内容}

评审报告格式:

## 总体评价
[论文质量的整体判断：接收/小修/大修/拒稿]

## 主要问题 (Major Concerns)
1. [识别策略的可信性]
2. [数据质量问题]
3. [遗漏变量偏误]
...

## 次要问题 (Minor Concerns)
1. [写作问题]
2. [引用不完整]
...

## 具体建议
- [建议增加的分析]
- [需要修正的图表]
- [需要补充的稳健性检验]

## 对作者的问题
1. [关于研究设计的问题]
2. [关于结果解释的问题]

评审标准:
- 是否有令人信服的因果识别？
- 预趋势是否平行？
- 结果是否对不同规范稳健？
- 是否讨论了 SUTVA 违反的可能性？
- 是否存在处理效果异质性？
- 数据和代码是否可复现？
```

### 6.2 修订计划提示词

```
你是一位资深经济学家。请根据以下评审意见，制定一份系统的修订计划。

评审意见:
{粘贴所有评审报告}

请输出:

## 修订计划

### 重大修改
| 编号 | 评审意见 | 修改方案 | 优先级 |
| ---- | -------- | -------- | ------ |
| R1.1 | [意见]   | [方案]   | 高     |

### 次要修改
| 编号 | 评审意见 | 修改方案 | 优先级 |
| ---- | -------- | -------- | ------ |
| R2.1 | [意见]   | [方案]   | 中     |

### 回复评审信
[对每条意见的逐一回复，解释如何修改或为何不修改]

### 新增分析清单
- [ ] [新的稳健性检验]
- [ ] [新的子样本分析]
- [ ] [新的图表]
```

---

## 7. 元数据生成提示词

### 7.1 metadata.json

```
请为以下论文生成规范的 metadata.json:

论文标题: {title}
论文 ID: apep_{XXXX}
方法: {DiD/RDD/DR}
版本: {N}
撰写模型: {model_name}
贡献者: {contributor}

输出 JSON:
{
  "paper_id": "apep_{XXXX}_v{N}",
  "title": "{title}",
  "method": "{method}",
  "policy_id": null,
  "contributor": "{contributor}",
  "authoring_model": "{model_name}",
  "published_at": "{ISO 8601 datetime}",
  "paper_family_id": "apep_{XXXX}",
  "version": {N}
}
```

---

## 8. 复现指南提示词

### 8.1 REPLICATION.md

```
请为以下论文生成复现指南 (REPLICATION.md):

论文: {paper_id}
代码文件: {列出所有 R 脚本}
数据来源: {API 列表}

格式:
# Replication Guide for {paper_id}

## Requirements
- R >= 4.3.0
- 所需 R 包列表
- API Keys

## Steps
1. 安装依赖: `Rscript code/00_packages.R`
2. 获取数据: `Rscript code/01_fetch_data.R`
3. 运行分析: `Rscript code/03_main_analysis.R`
4. 生成图表: `Rscript code/05_figures.R`
5. 编译论文: `pdflatex paper.tex`

## Expected Output
- `output/panel_data.rds` — 面板数据集
- `figures/*.pdf` — 所有图表
- `paper.pdf` — 最终论文

## Notes
[特殊说明或已知问题]
```
