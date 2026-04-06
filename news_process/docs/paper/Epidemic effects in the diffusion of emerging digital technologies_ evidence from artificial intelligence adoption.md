# 基于参考论文的项目分析与诊断报告及执行计划书

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断
**论文核心机制**：该文献（Dahlke et al., 2024/2026）旨在研究新兴数字技术（AI）在企业层面的传染病式扩散效应（Epidemic Effects）。其机制包含三个核心维度：(1) 间接的环境同型模仿压力（Regional/Sectoral Mimetic Pressure）；(2) 直接的网络互动与知识传递（网络中心度、链路强度）；(3) 知识深度的异质性（Deep Knowledge 即实质落地，vs Superficial Knowledge 即概念信息传递）。同时强调了“认知邻近度（Cognitive Proximity）”和“地理邻近度（Geographic Proximity）”在知识溢出中的调节作用。
**当前项目盲区**：目前本项目在 `news_process` 中采用孤立个体的视角（将银行作为独立的观测主体计算金融科技新闻曝光和情感得分），严重缺乏**网络联动和扩散机制**的度量。此外，目前的 LLM prompt 仅停留在“底层技术/应用场景”及“正面/负面情绪”的判定，未能敏锐捕捉银行业在金融科技转型中真实的“应用深度（Deep vs Superficial）”，不足以排除跟风式“信息噪音”的内生性干扰。

### 2. 实质性改进项（宁缺毋滥）
> - **改进 A：基于 LLM 的金融科技“知识深度（Knowledge Depth）”甄别重构**
>   - **标明论文依据**：理论引入自论文对 "Deep AI knowledge"（AI人员、核心产品和服务、内部流程整合）与 "Superficial AI knowledge"（浅层信息流、科普文章）的 Transformer 训练分类。
>   - **预期的边际贡献**：在阶段21的 LLM 精筛（`tone_llm_processing`）中剥离纯粹的情感打分，将其重构为对银行数字化转型“实质深度”的维度评估。此举不仅将消除大量媒体公关稿件带来的“虚假研发”噪音，更能为面板面板数据提供结构化、高质量的实证依赖变量。
>
> - **改进 B：引入传染病扩散网络机制（Epidemic Diffusion Networks & Proximities）**
>   - **标明论文依据**：论文通过超链接网络和文本向量（Cosine Similarity）生成企业间的 `degree_ai`、`betw_all` 以及 `cogn_mean`，并结合地理位置算出了区域模仿渗透率（`AI_reg`）。
>   - **预期的边际贡献**：由于本数据以新闻文本为基础，可利用跨篇章的新闻实体库构建两项革命性工具变量 / 解释变量机制：一是用新闻中提取的“同文共提银行（Co-mentions）”生成银行间的直接关联图谱（Direct Transmission Network），提取网络中心性；二是用某银行的全量新闻特征向量与其他银行求余弦相似度，产生“认知邻近度（Cognitive Proximity）”并与基于 `bank_addresses_file` 生成的“地理同型模仿压力”交叉验证。极大拓宽实证口径。

### 3. 冗余剥离
明确剔除偏离主线或价值极低的“伪需求”模块：
- **果断剔除基于字典与基准 BERT 的情感分析（阶段 22 和 23）**：本文证明，研究新兴数字技术的扩散，其核心在于评估其“应用深度”（Deep vs Superficial）及“网络溢出特性”，单纯的情感正负面已成为时代的边缘议题。使用滞后的金融词典（`tone_words`）或单维度的 BERT 倾向判定不但无法捕捉认知网络相似度，反而大大增加了算力损耗和后续稳健性解释的冗余压力，建议直接从 `config.yaml` 的 `sentiment_analysis` 中清退。

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布
- **速赢项（Quick Wins）**：耗时短、收益大。即刻重写 `21_tone_llms` 中的 Prompt，将输出分类结构切换至深度实质应用评估（Deep FinTech Adoption）与浅层关注（Superficial Mentions）。停用传统的情感词典分析任务。
- **核心攻坚项**：在阶段40中开发新闻级别的图计算模块，构造银行业的金融科技共现网络（Co-mention Graph），并生成面板级别的认知邻近度矩阵（Cognitive Proximity Matrix）与地理溢出测度。

### 2. 阶段化执行指令 (SOP)

#### 阶段一（机制重塑/数据清洗）：
- **核心动作**：修改 `config.yaml` 配置文件。
- **交付物标准**：
  1. 重写 `prompt_template`，将原有的 `fintech_category` 和 `sentiment` 替换为 `"knowledge_depth": "deep/superficial/none"`，并指令模型区分实质应用（研发、产品落地等 deep 层）与表象宣传（参会散稿、宏观讨论等 superficial 层）。
  2. 强行把 `tone_words` 和 `tone_berts` 对应的方法从 `enabled_methods` 列表中移除，精简流水线开销。

#### 阶段二（实证/模型重构与检验）：
- **核心动作**：注入关系数据与地理溢出数据生成模块入面板（Panel Building）。
- **交付物标准**：
  1. 引入 Python 图计算库（如 `networkx`），利用精筛阶段（阶段21）识别的 `co_mentioned_banks`，构建“银行信息关联网络”，得出每年的 `degree_ai` 和 `betweenness_centrality` 并沉淀在 Bank-Year 面板中。
  2. 生成“认知空间溢出变量（Cognitive Proximity Spillovers）”——提取各银行的年度新闻向量特征均值计算成对相似度，作为网络扩散强度的度量。
  3. 利用 `bank_addresses_file` 生成地级/省级市的区域采用渗透率（Regional Mimetic Pressure）。

#### 阶段三（结论重构）：
- **核心动作**：将回归基准模型的核心聚焦于“技术传染与同构驱动”。
- **交付物标准**：验证银行自身的数字化深度落地（Deep Adoption）究竟是由自身的内部资源禀赋引发，还是明显受到网络中心度（Relational Embeddedness）、高认知邻近度同业的带动，以及地理区域环境下的模仿压力影响，形成具有开创型的时序因果网络实证链条。

### 3. 风险预案 (Plan B)
- **致命卡点预判**：基于新闻文本中提取“同文共提银行”极可能遇到数据极度稀疏的问题，即绝大多数银行的单篇新闻中仅提及自己，导致共现网络构建失败，出现大量零节点孤岛。
- **Plan B 替代方案**：若关联图谱难以建立，直接舍弃基于单篇文章共现（Co-mentions）的物理链路关系图，退而求其次仅运用所有新闻的 **LLM 文本向量表征重构认知网络体系**。把两家银行在金融科技领域新闻话语体系或向量高斯分布的“Cosine Similarity”定为**隐性强连接**，并依据此隐性连接计算所有中心性指标和知识传染力，作为网络拓扑学的核心数据。
