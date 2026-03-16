# AutoPaper 复现 — AI 提示词集合

> 以下提示词用于驱动 AI Agent 完成 AutoPaper 项目各阶段的工作。
> 每个提示词都可直接复制使用，仅需替换 `{变量}` 部分。
> **研究领域：商业银行**

---

## 1. 创意生成提示词

### 1.1 生成研究创意

```
你是一位计量经济学研究者，专注于商业银行与金融监管领域。请为商业银行政策评估研究生成 5 个具有可信因果识别策略的研究创意。

要求：
1. 每个创意必须使用以下方法之一:
   - 双重差分法 (Difference-in-Differences, DiD) — 适用于银行业监管政策在不同时间/不同类型银行交错实施的情况
   - 断点回归设计 (Regression Discontinuity Design, RDD) — 适用于基于监管指标阈值（如资本充足率、不良贷款率、资产规模等）存在明确断点的情况

2. 数据必须且只能使用本项目提供的统一本地 DTA 数据库（data.dta）的现有变量：
   - 参考 data_schema.txt 的变量列表和标签
   - 严禁提出需要从外部获取数据的研究思路，或猜测本地不存在的数据变量。

3. 每个创意需包含以下结构:
   ## 创意 N: [标题]
   **研究问题**: [一句话描述因果关系]
   **政策背景**: [2-3 句描述银行业监管政策]
   **识别策略**: [DiD/RDD，解释为什么可信]
   **数据来源**: [具体变量及它在 data.dta 中的对应列名]
   **预期结果**: [假设方向及理由]
   **原创性评分**: [1-10]
   **可行性评分**: [1-10]

4. 避免以下已被广泛研究的主题:
   - 常规存贷款利率对利润的基础影响分析
   - 基础的资本充足率合规研究
   - 简单的规模与盈利正相关关系

请确保每个想法都有清晰的处理组和对照组定义。
```

### 1.2 创意排名提示词

```
请对以下 5 个研究创意进行排名和评分。评分维度:

1. **原创性** (0-10): 是否填补了商业银行研究的学术文献空白？
2. **可行性** (0-10): 数据是否真实可获取？变量是否在 data_schema.txt 中存在？
3. **因果可信度** (0-10): 识别策略是否能说服顶级金融学期刊编辑？
4. **政策相关性** (0-10): 结论对银行业监管决策者是否有价值？

请输出 JSON 格式:
```json
{
  "rankings": [
    {"idea_id": 1, "title": "...", "originality": X, "feasibility": X,
      "causal_credibility": X, "policy_relevance": X, "total": X,
      "ranking_rationale": "..."}
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
你是一位高级计量经济学家，专精于商业银行与金融监管研究。请为以下研究主题撰写一份详细的研究计划 (initial_plan.md)。

研究主题: {选定的研究创意}

研究计划必须包含以下部分:

## 1. 研究问题
[清晰、可检验的因果命题，聚焦于商业银行]

## 2. 文献回顾
[该领域 5-8 篇关键参考文献，说明本研究的边际贡献]

## 3. 制度背景
[银行业监管政策的实施时间线、具体内容、适用范围]

## 4. 识别策略

### 4.1 方法选择
[详细解释为什么选择 {DiD/RDD}]

### 4.2 主要回归模型
[Markdown 公式，如:]
$$Y_{bt} = \alpha + \beta \cdot D_{bt} + \gamma_b + \delta_t + X_{bt}'\theta + \epsilon_{bt}$$
其中:
- $Y_{bt}$: 银行 b 在第 t 年的结果变量
- $D_{bt}$: 处理指示变量
- $\gamma_b$: 银行个体固定效应
- $\delta_t$: 年份固定效应
- $X_{bt}$: 时变控制变量（银行规模、资本充足率、不良贷款率等）

### 4.3 识别假设
[平行趋势假设/连续性假设的论证]

## 5. 数据

### 5.1 数据来源
[明确指出使用的变量名及所在的 data.dta 数据集]

### 5.2 时间范围
[如 2007-2023]

### 5.3 样本定义
[如所有商业银行，或特定类型银行]

### 5.4 核心变量
| 变量名 | 描述         | 数据集来源 | 原始列名（来源于 data.dta） |
| ------ | ------------ | ---------- | --------------------------- |
| Y      | 不良贷款率   | data.dta   | 不良贷款率                  |
| treat  | 政策处理变量 | 构造变量   | —                           |

## 6. 稳健性检验
- PSM-DID 倾向得分匹配
- 安慰剂检验（随机置换）
- 系统 GMM 动态面板
- 工具变量回归
- 替代度量检验
- 排除竞争政策
- 子样本分析

## 7. 预期结果与贡献
[假设方向及对银行业监管政策的意义]
```

---

## 3. 数据提取提示词

### 3.1 Stata 数据清洗代码

```
你是一位 Stata 程序员。请编写一个 Stata 脚本 (01_fetch_data.do) 来为以下商业银行研究准备数据:

研究计划:
{粘贴 initial_plan.md 的内容}

要求:
1. 使用 `use` 从 data/ 目录读取 data/data.dta 数据。
2. 切勿使用任何网络请求读取远程 API，所有变量需从本地提取。
3. 务必处理缺失值并将相关的指标转化为数值类型（如使用 destring）。
4. 设定面板结构：`xtset bankid year`。
5. 构建银行研究所需的标准变量：
   - 银行特征控制变量（Ln_Assets, CAR, NPL, ROA, NIM, CIR, LDR 等）
   - 使用 winsor2 进行缩尾处理
   - DID 处理变量（Treat, Post, DID）
   - 交互固定效应（year_banktype_id, year_province_id）
   - 分组虚拟变量（银行类型、规模分组、上市状态等）
6. 保存到 data/clean_data.dta。
7. 保存描述性统计到 data/descriptive_stats.csv。
8. 脚本以中文注释。

代码结构:
- 读取数据 `use "data/data.dta", clear`
- 面板标识符编码与 xtset
- 银行特征控制变量生成（含 winsor2 缩尾）
- DID 处理变量构造
- 交互固定效应生成
- 样本筛选
- 保存输出 `save "data/clean_data.dta", replace`
```

---

## 4. 计量分析提示词

### 4.1 DiD 分析代码

```
你是一位高级 Stata 统计分析师。请编写主分析脚本 (03_main_analysis.do)。

研究设计:
- 方法: 双重差分法 (DiD)
- 处理方式: 不同银行在不同时间受到政策冲击
- 面板数据: 银行 × 年份

要求:
1. 加载 data/clean_data.dta
2. 定义全局控制变量宏:
   global Controls "Ln_Assets CAR NPL ROA NIM CIR LDR NonIntIncome LiquidRatio"
3. 运行主估计模型:
   - OLS 高维固定效应 (reghdfe)
   - 泊松伪极大似然估计 (ppmlhdfe，用于计数型因变量)
   - 系统 GMM (xtabond2，用于动态面板)
4. 运行多种固定效应组合:
   - 银行 + 年份（基准）
   - 银行 + 年份 + 年份×银行类型
   - 银行 + 年份 + 年份×省份
5. 生成 Driscoll-Kraay 标准误回归 (xtscc)
6. 生成汇总表格，写入 data/main_results_summary.csv
7. 所有回归使用银行层面聚类标准误 (vce(cluster bankid))
```

### 4.2 RDD 分析代码

```
你是一位高级 Stata 统计分析师。请编写断点回归分析脚本 (03_main_analysis.do)。

研究设计:
- 方法: 断点回归设计 (Sharp RDD)
- 断点变量 (Running variable): {银行监管指标，如资本充足率}
- 断点值 (Cutoff): {如 8%，即巴塞尔III最低资本充足率要求}

要求:
1. 使用 rdrobust 进行非参数局部多项式估计
2. 最优带宽选择 (MSE-optimal bandwidth)
3. McCrary 密度检验（关注银行报表操纵可能性）
4. 不同带宽和核函数的敏感性分析
5. 协变量平衡性检验
6. RD 图 (rdplot)
```

---

## 5. 论文撰写提示词

### 5.1 完整论文撰写

```
你是一位经济学教授，专长于撰写商业银行与金融监管研究论文。请基于以下材料撰写一篇完整的学术论文 (Markdown 格式):

研究计划: {粘贴 research_plan.md}
分析结果: {粘贴主要回归结果}
图表: {描述图表内容}

论文结构要求:
1. Title: 简洁有力，包含政策名称和方法
2. Abstract: 250 词以内，含方法、发现、意义
3. Introduction (2-3 页): 动机、贡献声明、结构预览
4. Institutional Background (1-2 页): 银行业监管政策详情和时间线
5. Data (1-2 页): 数据来源、银行变量定义、描述性统计
6. Empirical Strategy (1-2 页): 模型设定、识别假设论证
7. Results (2-3 页): 主要发现、平行趋势分析
8. Robustness (1-2 页): PSM-DID、安慰剂检验、系统GMM、工具变量等
9. Heterogeneity (1 页): 按银行类型/规模/产权性质的异质性分析
10. Mechanism (1 页): 风险管理/信贷配置/金融创新等机制分析
11. Further Analysis (0.5-1 页): 调节效应、前瞻性经济后果
12. Conclusion (0.5 页): 总结与政策建议

写作风格:
- 参考顶级金融学期刊水平
- 使用被动语态
- 数字精确到小数点后三位
- 结果需有经济学意义的解读

Markdown 格式要求:
- 使用标准的 Markdown 语法
- 图表编号和标题规范
- 全文用中文撰写
```

---

## 6. 同行评审提示词

### 6.1 评审报告生成

```
你是一位严格的学术审稿人，被邀请为一篇提交到顶级金融学期刊的商业银行研究论文撰写评审报告。

请阅读以下论文并撰写详细的评审报告:

{粘贴 paper.md 或论文内容}

评审报告格式:

## 总体评价
[论文质量的整体判断：接收/小修/大修/拒稿]

## 主要问题 (Major Concerns)
1. [识别策略的可信性]
2. [银行层面数据质量问题]
3. [遗漏变量偏误（银行层面特征）]
...

## 次要问题 (Minor Concerns)
1. [写作问题]
2. [引用不完整]
...

## 具体建议
- [建议增加的分析，如系统GMM稳健性检验]
- [需要修正的图表]
- [需要补充的异质性/机制分析]

## 对作者的问题
1. [关于银行面板内生性的处理]
2. [关于截面相关性的处理]

评审标准:
- 是否有令人信服的因果识别？
- 预趋势是否平行？
- 结果是否对不同规范稳健？（含系统 GMM）
- 是否讨论了银行间溢出效应（SUTVA 违反）的可能性？
- 是否存在处理效果异质性（按银行类型/规模）？
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
- [ ] [新的稳健性检验，如系统 GMM]
- [ ] [新的异质性分析，如按银行类型]
- [ ] [新的机制分析]
- [ ] [新的图表]
```

---

## 7. 元数据生成提示词

### 7.1 metadata.json

```
请为以下论文生成规范的 metadata.json:

论文标题: {title}
论文 ID: paper_{XXXX}
方法: {DiD/RDD/DR}
版本: {N}
撰写模型: {model_name}
贡献者: {contributor}

输出 JSON:
{
  "paper_id": "paper_{XXXX}_v{N}",
  "title": "{title}",
  "method": "{method}",
  "policy_id": null,
  "contributor": "{contributor}",
  "authoring_model": "{model_name}",
  "published_at": "{ISO 8601 datetime}",
  "paper_family_id": "paper_{XXXX}",
  "version": {N}
}
```

---

## 8. 复现指南提示词

### 8.1 REPLICATION.md

```
请为以下论文生成复现指南 (REPLICATION.md):

论文: {paper_id}
代码文件: {列出所有 Stata 脚本}
数据来源: {data.dta，列出对应的银行变量集}

格式:
# Replication Guide for {paper_id}

## Requirements
- Stata >= 15.0
- 所需 Stata 包列表（reghdfe, ppmlhdfe, psmatch2, bdiff, xtabond2, xtscc 等）

## Steps
1. 安装依赖: `stata-mp -e do code/00_packages.do`
2. 加载数据: `stata-mp -e do code/01_fetch_data.do`
3. 描述统计: `stata-mp -e do code/02_descriptive_stats.do`
4. 主要分析: `stata-mp -e do code/03_main_analysis.do`
5. 稳健性检验: `stata-mp -e do code/04_robustness.do`
6. 生成图表: `stata-mp -e do code/05_figures.do`
7. 异质性分析: `stata-mp -e do code/06_heterogeneity.do`
8. 机制分析: `stata-mp -e do code/07_mechanism.do`
9. 进一步研究: `stata-mp -e do code/08_further_analysis.do`

## Expected Output
- `data/clean_data.dta` — 银行面板数据集
- `figures/*.png` — 所有图表
- `tables/*.csv` — 所有回归结果表
- `paper.md` — 最终论文

## Notes
[特殊说明或已知问题]
```
