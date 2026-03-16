# {PAPER_TITLE}

**来自{POLICY_CONTEXT}的经验证据**

**作者：**
AutoPaper Working Paper No. paper_XXXX
Autonomous Policy Evaluation Project

**日期：** {DATE}

---

## 摘要

{ABSTRACT_TEXT: 描述研究问题、数据来源（商业银行面板数据）、识别策略、主要发现和政策含义。250 字以内。}

**关键词：** {keyword1}, {keyword2}, {keyword3}
**JEL 分类：** {G21}, {G28}, {G34}

---

## 1. 引言

{INTRO_PARAGRAPH_1: 引出研究问题，说明商业银行监管政策背景的重要性。}

{INTRO_PARAGRAPH_2: 商业银行研究的文献空白与本文贡献。}

本文对以下几个方面做出了贡献：第一，……第二，……第三，……

{INTRO_PARAGRAPH_3: 方法概述和主要发现预览。}

本文的结构安排如下：第 2 节介绍制度背景。第 3 节描述数据。第 4 节阐述实证策略。第 5 节报告主要结果。第 6 节进行稳健性检验。第 7 节分析异质性。第 8 节探究影响机制。第 9 节为进一步研究。第 10 节为结论。

## 2. 制度背景

{BACKGROUND: 银行业监管政策的详细时间线、实施内容、覆盖范围。}

**表 1: 政策实施时间线**

| 银行类型/批次 | 实施年份 | 关键条款     |
| :------------ | :------: | :----------- |
| {Type1}       | {Year1}  | {Provision1} |
| {Type2}       | {Year2}  | {Provision2} |

*注：{表格注释}*

## 3. 数据

### 3.1 数据来源
{DATA_SOURCES: 描述商业银行面板数据来源、data.dta、时间覆盖、银行类型覆盖。}

### 3.2 变量定义
{VARIABLES: 关键银行变量的定义和构造方法。包括因变量、核心自变量（DID）、控制变量（Ln_Assets, CAR, NPL, NIM, CIR, LDR 等）。}

### 3.3 描述性统计

**表 2: 主要变量描述性统计**

| 变量        |   N   | 均值  | 标准差 | 最小值 | 最大值 |
| :---------- | :---: | :---: | :----: | :----: | :----: |
| {Y}         |       |       |        |        |        |
| {Ln_Assets} |       |       |        |        |        |
| {CAR}       |       |       |        |        |        |
| {NPL}       |       |       |        |        |        |
| {NIM}       |       |       |        |        |        |

*注：{来源和样本描述}*

## 4. 实证策略

本文利用{POLICY_NAME}在不同银行/时间的交错实施，采用双重差分法进行因果识别。基准回归模型为：

$$ Y_{bt} = \alpha + \beta \cdot D_{bt} + \gamma_b + \delta_t + X_{bt}'\theta + \epsilon_{bt} $$

其中 $Y_{bt}$ 为银行 $b$ 在第 $t$ 年的{OUTCOME_DESCRIPTION}，$D_{bt}$ 为处理指示变量（若银行 $b$ 在第 $t$ 年已受到{POLICY_NAME}影响则取值为 1），$\gamma_b$ 和 $\delta_t$ 分别为银行和年份固定效应，$X_{bt}$ 为时变控制变量。标准误在银行层面聚类。

### 4.1 识别假设
{ASSUMPTIONS: 平行趋势假设的论证。}

### 4.2 补充分析方法
为增强结论的稳健性，本文还采用以下方法：
- 系统 GMM 动态面板估计（xtabond2），控制因变量的动态持续性
- Driscoll-Kraay 标准误（xtscc），处理银行间截面相关性
- 泊松伪极大似然估计（ppmlhdfe），适用于计数型因变量

## 5. 主要结果

### 5.1 基准回归结果

{RESULTS_DISCUSSION: 解读主要回归结果，强调经济意义和统计显著性。}

### 5.2 平行趋势检验

![平行趋势检验](figures/parallel_trends.png)

*注：{图表注释}*

{PARALLEL_TRENDS_DISCUSSION: 平行趋势检验结果的解读，事前各期系数应不显著。}

## 6. 稳健性检验

### 6.1 PSM-DID 倾向得分匹配
{PSM_DID: PSM-DID 检验结果。}

### 6.2 安慰剂检验
{PLACEBO: 随机置换安慰剂检验结果。}

### 6.3 工具变量回归
{IV: 工具变量两阶段回归结果。}

### 6.4 系统 GMM 动态面板
{GMM: 系统 GMM 估计结果，包括 AR(2) 和 Hansen 检验。}

### 6.5 其他稳健性检验
{OTHER_ROBUSTNESS: 排除竞争政策、交替固定效应、排除特定样本等。}

## 7. 异质性分析

### 7.1 按银行类型
{HETEROGENEITY_TYPE: 国有大行 / 股份制 / 城商行 / 农商行的分组结果与 bdiff 组间差异检验。}

### 7.2 按银行规模
{HETEROGENEITY_SIZE: 大型银行 / 中小型银行的分组结果。}

### 7.3 按产权性质与地区
{HETEROGENEITY_OTHER: 国有/非国有控股、东部/中西部分组结果。}

## 8. 影响机制分析

### 8.1 风险管理渠道
{MECHANISM_RISK: 不良贷款率 / 拨备覆盖率 / 风险加权资产的机制检验结果。}

### 8.2 信贷配置渠道
{MECHANISM_CREDIT: 中小微贷款占比 / 绿色信贷占比 / 贷款集中度的机制检验结果。}

### 8.3 金融创新渠道
{MECHANISM_INNOVATION: 非利息收入占比 / 金融科技指数的机制检验结果。}

## 9. 进一步研究

### 9.1 调节效应
{MODERATION: 监管压力 / 市场竞争 / 金融科技调节效应的交互项回归结果。}

### 9.2 前瞻性经济后果
{FORWARD_LOOKING: 对 F1.NPL、F1.ROA、F1.LoanGrowth 的前瞻回归结果。}

## 10. 结论

{CONCLUSION: 总结主要发现、对银行业监管政策的启示、局限性和未来研究方向。}

---

## 参考文献

[References List]

---

## 附录

### A. 补充表格与图表

{APPENDIX_TABLES_FIGURES}
