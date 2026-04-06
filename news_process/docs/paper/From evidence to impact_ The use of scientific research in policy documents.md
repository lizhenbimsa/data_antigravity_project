# 基于《From evidence to impact: The use of scientific research in policy documents》的项目分析与诊断报告及执行计划书

=========================================
## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断：
**提炼论文核心机制**：该顶刊论文利用自然语言处理（PubMedBERT）首次解耦了文档中的“显性引用（Formal Citations）”与“文本级语义实质借鉴（Textual Credit）”，从而识别出纯象征意义的**“象征性引用（Token Citations，徒有其名）”**和具有实质影响力的**“隐性应用（Hidden Citations，有实无名）”**。论文结论证实，前者旨在迎合外部审查以获取合法性（关联“表面/科学影响力”），后者则代表解决了实际阻碍的实质性采纳（关联“实际操作/病人影响力”）。

**盲区诊断**：映射至当前 `news_process` 银行金融科技（FinTech）文本分析项目，存在**重大的度量视角落差**。
当前流水线（如 `12_news_fintech.py` 和 `21_tone_llms.py`）过于依赖关键词字面命中和 LLM 二元判定，将“提及了数字货币/AI”直接等同于“参与了金融科技”。这无法剥离管理层的“漂绿/洗科技（Token Adoption，纯蹭热点、无技术细节）”与“实质性落地（Hidden/Substantive Adoption，真金白银投入核心系统重构但不一定用时髦的 Fintech 热词）”。这种“显性命中”与“实质语义”的混淆会导致严重的内生性偏误和衡量误差（Measurement Error）。

### 2. 实质性改进项（宁缺毋滥）：
>    - **改进 A：构建连续的“语义对齐指数”并剥离 Token/Hidden 采用特征**
>      - [具体修改建议]：引入预训练领域语言模型（如 `bge-large-zh-v1.5` 或 `FinBERT` Embedding库），选取监管层《金融科技发展规划》及代表性金融专利摘要作为**锚定金标准文本**。通过计算单篇新闻的段落级加权 Embedding 与金标准文本之间的余弦相似度（Cosine Similarity），替代原本非黑即白的 LLM 判断。通过组合 [词典匹配频次] 与 [语义相似度]，对数据进行两维划分：高频低相似度（Token，象征性洗科技）与低频高相似度（Hidden，实质性系统建设）。
>      - [标明论文依据]：严格映射 Distel et al. (2025) 方法论（Section 3.2.1），设定相似度阈值（如论文中的 67.0）来定义实质性对齐。
>      - [预期的边际贡献/解决的内生性问题]：解决金融科技度量中“说得多做得少”造成的向下偏误。分别评估 Token 采用对市场短期情绪的“合法性/科学性影响（ Legitimacy Function）”和 Hidden 采用对银行长效盈利指标的“实质性影响（Instrumental Function）”。

### 3. 冗余剥离：
- 明确指出需要剔除的**“伪需求”模块**：
单纯的金融科技关键词词典覆盖度审查（对应 `37_dict_coverage_audit.py` 中静态词频累加的部分逻辑）和完全无语境的线性情感词典法（`22_tone_words.py` 中等权 TF-IDF 以外的裸分词方法）。在顶刊框架下，单纯度量词汇有无及其表层覆盖率不仅学术价值极低，反而会被审稿人质疑为“噪音捕获器”。建议直接废弃该静态维度，全面由基于深度语境 Embedding 的 Token/Substantive 四象限指标接管。

=========================================
## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布：
- **速赢项（Quick Wins）**：在 `12_news_fintech.py` 中引入基础的 Sentence-Transformers，对筛选到的所有文章生成全局 Paragraph 级句向量，存入 Parquet。
- **核心攻坚项**：在阶段四（`45_panel_export_main.py`）进行面板聚合构建，对每家银行每年的新闻资产进行 Token、Hidden 和 Substantive 的分桶构建，生成多维“金融科技实质渗透率”面板指标。

### 2. 阶段化执行指令 (SOP)：

**阶段一（机制重塑/数据清洗）：**
- 创建 `config/reference_texts.json`：提取中国人民银行近三期《金融科技发展规划》的核心关键段落及银行硬核技术攻关摘要作为基础语义知识库。
- 引入 Embedding 层：新建脚本 `13_semantic_alignment.py`：
  - [动作] 读取 `11_bank_news.parquet`，针对每段文本调用开源模型（如 `shibing624/text2vec-base-chinese` 或 `BGE` ），计算基于句法长度加权的 Average Paragraph Embedding（执行参考论文 3.2.1 的计算机制）。
  - [标准] 产出包含 cosine_similarity 字段的数据列，将单篇文章对齐到金标准向量空间中。

**阶段二（实证/模型重构与检验）：**
- 将二维结构写入指标体系：修改 `41_panel_encode_aggregate.py`。
  - [动作] 生成三个组合标量：`Token_Adoption_Vol`（具有金融科技提及但相似度 < 预设阈值 P）、`Hidden_Adoption_Vol`（没有提及规定词典池但相似度 ≥ 预设阈值 P）、`Substantive_Adoption_Vol`（两者都满足）。
  - [标准] 引入模型校准（Calibration Test），先人工抽取 200 条验证分类门槛（Threshold），报告混淆矩阵（Confusion Matrix）及 Matthews correlation coefficient (MCC)，确保模型截断稳健性（参考论文中 Table 1 的方法论）。

**阶段三（结论重构）：**
- 回归主线重写。
  - [动作] 修改实证基准测试脚本：设定对短期超额收益（CAR）的回归主导变量为 `Token_Adoption_Vol`（市场情绪响应），对长期总资产收益率（ROA）、成本收入比的关键变量更新为 `Hidden/Substantive Adoption_Vol`（基本面吸收）。

### 3. 风险预案 (Plan B)：
- **文本相似度模型分布爆炸或极端趋同（区分度弱）风险**：
  - 若所有余弦相似度均收敛在 0.8~0.9 之间导致难以设定二分阈值，启动替代方案：改用余弦相似度的相对分位数（如年份/行业前25%）作为阈值定义 Substantive 标准，而不是固定绝对值；或转换使用 Contrastive Learning（对比学习）预训练，增加负样本锚点（如明显的“银行文娱广告”作为负极）。
- **计算资源过载风险**：
  - 如果超千万行的段落级 Embedding 造成内存及并发阻塞（现设置 batch_size 5000），可切换采用文章标题与首段（Abstract & Headings）的压缩 Embedding 计算替代全文铺开。

=========================================
