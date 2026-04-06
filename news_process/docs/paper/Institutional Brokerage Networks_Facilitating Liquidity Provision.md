# 基于《Institutional Brokerage Networks: Facilitating Liquidity Provision》的诊断与执行计划

**参考论文:** *Institutional Brokerage Networks: Facilitating Liquidity Provision* (Han, Kim, Nanda, 2024)
**目标项目:** `f:\WiseSearch\data_antigravity_project\news_process`

=========================================
## 第一部分：基于参考论文的项目分析与诊断报告
（侧重 Why & What）

### 1. 范式映射与盲区诊断
- **论文核心机制提炼**：论文的核心机制是“中介网络中心度溢价（Centrality Premium）”——处于经纪网络中心位置的机构（和经纪商），能够通过更广的隐性流动性池，有效缓解非信息驱动巨액交易的负面价格冲击，尤其在市场压力（连续资金流出/Fire Sales）和缺乏流动性的标的中作用最为显著。
- **当前项目真实落差与盲区**：目前项目聚焦于银行金融科技的新闻挖掘，并做了大量媒体异质性和权威性分析（如 `compute_media_heterogeneity`），但由于缺乏**网络拓扑维度（Network Topology）**的推演，依然停留于对资产（单一银行/单一新闻）的孤立评估。实际上，按照论文逻辑，媒体和资讯平台构成了一个庞大的“信息经纪网络（Information Brokerage Network）”。当前项目完全忽视了由于媒体共现（多个银行在同一权威媒体被报道，或通过新闻矩阵被联合报道）而形成的“媒体-银行双边网络”对声誉或市场反应的潜在乘数/分摊效应。

### 2. 实质性改进项（宁缺毋滥）
- **改进 A：由孤立特征转向网络拓扑——构建“媒体-银行”信息经纪网络及特征向量中心度（Eigenvector Centrality）测度**
  - **论文依据**：参考论文 Section 4 构建了机构与经纪商间的附属网络（Affiliation networks）并采用特征向量中心度衡量网络重要性。
  - **边缘贡献/解决的内生性**：利用阶段21大模型提取的 `confirmed_bank` 与 `co_mentioned_banks`，映射项目中的“Broker-Institution”网络，构建媒体发行端与提及银行间的双边关系图。测算各家银行及媒体在信息网络中的特征向量中心度。这不仅能够控制传统的个股异质性，还能吸纳面板中原先作为扰动项的“网络信息溢出效应（Network Spillover）”，量化银行业在金融科技转型声量的“网络垄断”地位。

- **改进 B：引入“信息抛售/舆情挤兑（Information Fire Sales）”极端条件下的中心度溢价检验**
  - **论文依据**：参考论文 Section 6.1 (The centrality premium when funds are forced to trade) 以及 Section 8 (资产抛售与网络结构踩踏效应)。
  - **边缘贡献**：检验机制转化——在面临集中性的行业负面新闻（声誉压力增加）时，信息经纪网络中心度高的银行，其所受到的负面影响被“分摊”削弱的程度。论文中指出若叠加冲击存在，关联网络反致踩踏；这为当前项目提供了极有深度的机制异质性检验方向，突破了当前简单的“新闻情感得分高低影响绩效”的线性平庸假设。

### 3. 冗余剥离
- **明确剥离伪需求**：论文表明机制深度远比底层工具堆叠重要。当前 `config.yaml` 模块三中依然配置并保留了大量复杂的静态词法分析（阶段22的各种否定词前瞻词窗处理）和多个低算力 BERT 模型（阶段23的 Erlangshen/FinBERT2 等）。在阶段21已经应用强语义 CoT 推理（GPT/Gemini大型多模态）后，继续维护、运行和后续对比词典与 BERT 数据将占用极高的算力对齐成本，且边际验证贡献极低，本质上是“由于惯性保留的伪需求”。建议直接废除阶段22和阶段23执行链路，将研发专注力直接迁移至网络测度的前沿面板切面。

=========================================
## 第二部分：项目重构与优化执行计划书
（侧重 How）

### 1. 优先级排布
- **速赢项（Quick Wins）：** 在 `config.yaml` 中剔除或禁用落后的 BERT 与词典配置，精简工作流。复用现成表包含的 `media`，`confirmed_bank` 及时间截面，直接聚合构建网络关联频率。
- **核心攻坚项：** 基于 NetworkX 实现面板结构下的双边二分图映射与 EigenCentrality 的跨期计算，同时设计针对“舆情压力（Information Fire Sales）”的定量甄别阈值指标框架。

### 2. 阶段化执行指令 (SOP)

- **阶段一（机制重塑/冗余清理）：**
  - **动作指令**：修改 `config.yaml` 停用 `sentiment_analysis.enabled_methods` 中的 `tone_words` 和 `tone_berts`。清理涉及这两个落后工作流的导出映射。仅保留并巩固 `tone_llms` 的权威性。
  - **交付物**：轻量化版本的分析框架配置文件。

- **阶段二（网络中心度提取与构建）：**
  - **动作指令**：新增特征工程脚本 `42_network_centrality_build.py`。读取 `21_tone_llms.parquet`，基于 `[媒体(中文), 银行主体]` 为边构建年度/半年度频次图。提取 Eigenvector Centrality、Degree Centrality 并持久化计算列输出至 `output_42_network_centrality.parquet`。
  - **交付物**：标准的 Bank-Year/Bank-Quarter 网络中心度长面板数据集（含银行特征向量中心度与所链接高权重新闻媒介的平均中心度）。

- **阶段三（实证模型重构与机制检验）：**
  - **动作指令**：在最终回归构建表（如 `45_panel_export_main.py` 环节）不仅汇入情感均值，还要对撞整合信息经纪中心度指标。设立 `Pressure` 压力变量模型（类似论文 Section 8 公式），检验 `Centrailty × Pressure` 交互项显著性。
  - **交付物**：一套具备稳健因果验证的实证表格导出程序与数据体。

### 3. 风险预案 (Plan B)
- **致命卡点**：不同银行受媒体覆盖频次差异存在极端的长尾效应（Power-law distribution），导致特征向量中心度（Eigenvector Centrality）可能发生不可解或不收敛、被几家巨头垄断吸收；此外，长尾甚至僵尸自媒体制造了过多的网络噪音伪连接。
- **替代方案 (Plan B)**：
  1. 提前对长尾媒体实行“噪音截断（Threshold Trimming）”，即仅保留年度发文覆盖过至少3家以上银行的核心/权威信息中介，构造核心网络。
  2. 倘若干预后 Eigen Centrality 分散度依然较差，可退化为计算改进版的度中心度（Weighted Degree Centrality/Information Access Pool）作为近似替代工具进行主验。
