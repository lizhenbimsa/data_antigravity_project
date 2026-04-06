# 项目分析与优化执行计划书：How news and its context drive risk and returns around the world

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断
**核心机制重述**：Calomiris & Mamaysky (2019) 提出了一种“非理论指导（atheoretical）”的文本分析范式，其核心贡献在于：1) 使用基于词汇共现网络的 **Louvain 社区发现算法**进行主题(Topic)划分（取代传统LDA和预设词典）；2) 利用4-gram条件概率构建新闻的**信息熵（Entropy / Unusualness）**指标，以捕捉异常新闻事件；3) 构建**主题特定情感（Topic-specific sentiment）**，并证明其对未来一年期的收益率、波动率（sigma）及最大回撤（drawdown）具有极强的预测能力。

**盲区诊断**：
当前 `news_process` 项目高度依赖预设的关键词词典（如 `fintech_dict.json`）和通过 LLM 进行特定主题定性（如二分类验证）。虽然在特定概念（如金融科技）的提取上精度较高，但在发现新兴的、未预料到的市场或系统性风险时存在严重的“预设偏差（A priori bias）”。项目目前完全缺乏对新闻“反常度（Unusualness/Entropy）”的度量，且因变量集中于横截面的面板实证，缺乏对尾部风险（最大回撤）和未来长期风险状态的时间序列/面板预测机制。

### 2. 实质性改进项（宁缺毋滥）

> - **改进 A：引入基于 Louvain 算法的无监督主题分类与词汇网络构建**
>   - **论文依据**：Section 2.1 "we apply atheoretical methods... to organize the flow of words... apply the Louvain community detection algorithm to find nonoverlapping clusters".
>   - **预期的边际贡献**：摆脱对人工维护的词典（如 `tone_dicts.json` 或 `fintech_dict.json` 中静态分类）的依赖。通过数据驱动方式自下而上识别出银行新闻中真实的语境分类（如信贷、宏观、监管、市场等），避免数据挖掘偏误（Data mining risks）。
> 
> - **改进 B：构建新闻的 n-gram 相对信息熵（Entropy）指标**
>   - **论文依据**：Section 2.1 "extract 4-grams... calculate the probability... The negative average log probability of all 4-g appearing in that article ($H_j$)".
>   - **预期的边际贡献/解决的内生性问题**：解决现有 LLM 情感分析“只能看好坏、不能看新旧”的痛点。信息熵能够对那些使用新语境描述的新兴冲击（如突发的政策黑天鹅、新型挤兑模式）提供高灵敏度的风险预警，其与情感指标结合将极大地增强对尾部风险（最大回撤）的解释力。
> 
> - **改进 C：预测目标拓展至长期波动率与最大回撤（Drawdown）**
>   - **论文依据**：Section 1 "we also employ the maximum one-year drawdown... down-side risk".
>   - **预期的边际贡献**：项目目前的面板实证大多关注基础的财务表现或政策效应。将因变量拓展至未来一年的最大回撤幅度（Drawdown）和已实现波动率（Sigma），能够完美契合银行系统性风险和流动性危机的研究内核。

### 3. 冗余剥离
明确剥离基于静态词典的情感计算模块（`22_tone_words.py`）以及非深度学习的词频统计算法。该论文证明了无监督网络方法加上标准的LM情感判定已经充分且高效。现有的高开销词典覆盖率审计（`37_dict_coverage_audit.py`）在引入非理论文本网络后将成为伪需求，建议搁置。

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布
- **速赢项（Quick Wins）**：计算金融新闻的 4-gram 信息熵，直接作为新的控制变量/解释变量加入现有 `45_panel_export_main.py` 的面板回归中，即可观察到显著增量效果。
- **核心攻坚项**：构建词汇共现矩阵（Co-occurrence matrix）并实现 Louvain 聚类算法，生成 `Topic-specific sentiment`，重构实证回归被解释变量为未来十二个月的最大回撤（Drawdown^{12}）。

### 2. 阶段化执行指令 (SOP)

**阶段一（机制重塑/数据清洗）：**
- **动作指令**：
  1. 新增脚本 `13_news_entropy_and_network.py`。
  2. 提取训练集语料，统计所有 3-gram 和 4-gram 的词频，根据论文公式计算每篇文章的交叉熵（$H_j$）。
  3. 基于词共现矩阵，调用 `python-louvain` 或 `networkx` 库计算模块度，提取无重叠的 Topic 集群。
- **交付物标准**：输出新的 `13_entropy_topic.parquet`，其中包含文章级指标：`entropy`, `topic_category`, 以及 `topic_weight`。

**阶段二（实证/模型重构与检验）：**
- **动作指令**：
  1. 修改 `21_tone_llms.py` 或直接在其输出基础上生成正负面比例，计算 Context-specific sentiment（即某主题占比 $\times$ 文章整体情感）。
  2. 在 `41_panel_encode_aggregate.py` 中，聚合月度/年度的 Country-level（或 Bank-level）的风险指标：收益率（return）、波动率（sigma，基于日收益率滚动计算）、最大回撤（drawdown，未来12个月从峰值到谷底的最大跌幅计算）。
- **稳健性检验标准**：使用双向固定效应面板回归（控制 Bank 和 Year/Month 固定效应），单独放入 Entropy 及其与 Sentiment 的交乘项进行预测测试。

**阶段三（结论重构）：**
- **动作指令**：
  基于新的实证结果重写文档。证明“银行层面的罕见新闻语境（高Entropy）”相比传统的“高负面情感”对银行未来的资产回撤和风险积累具有更独立、更前瞻的预测力。

### 3. 风险预案 (Plan B)
- **卡点预判**：海量新闻构建超大词汇共现矩阵并跑 Louvain 聚类可能会遭遇内存 OOM（Out of Memory）或极长的计算时间，特别是在多机分布式计算困难的情况下。
- **替代方案 (Plan B)**：放弃全量全词表聚类。预先使用 TF-IDF 筛选出头部 Top 5000 核心财经词汇作为“节点”，仅在这个缩减后的子网络上进行 Louvain 社区发现；或直接沿用论文已有的分类标签，利用 Word2Vec 或 FastText 计算每篇文章与预定义主题概念词的平均向量余弦相似度来实现主题分配。
