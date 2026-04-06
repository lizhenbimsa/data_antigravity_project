# 《The voice of monetary policy》项目分析与执行计划书

> [!IMPORTANT]
> 本报告基于顶刊论文《The voice of monetary policy》（Gorodnichenko et al., 2023, AER）的理论框架，结合当前处于 C:\Users\lizhe\.gemini\antigravity 并对应 `F:\WiseSearch\data_antigravity_project\news_process` 目录下的银行金融科技新闻流水线现状进行深度对标与诊断。
> 全文力求**拒绝形式主义**，以**最高学术标准**实现从“理论洞察”到“代码工程”的硬核映射。

---

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断
**论文核心机制：** 该论文最卓著的贡献在于对政策沟通信息通道的绝佳解耦——证明了剥离了“政策实际动作（Policy Actions, 如利率调整）”与“书面标准化措辞的字面语义（Text Sentiment, Dovish/hawkish）”之后，单凭高管（美联储主席）在非剧本化语境（如脱稿问答）中流露出的**隐性语气和情绪（Voice Tone）**，同样包含极大边际信号，能显著牵动金融市场。

**当前项目盲区：** 当前项目流水线（如 `21_tone_llms.py` 和 `config.yaml` 中的评估逻辑）采取了一种“宏大叙事”的处理方式，即将整篇带有公关修饰性质的新闻文本混合打包进行单一的正面/负面情绪提取。这存在两个致命的学术逻辑断层：
1. **混淆了“动作事实”与“媒体情感”**：银行上线新APP是一项客观行动（Action），媒体对此的吹捧则是报道感情（Sentiment），项目未做拆分。
2. **掩盖了真正的“Tone（语气）”**：新闻作为结构化的书面表达（Scripted Text），掩盖了高管对该项技术真实、微妙的个人态度（unscripted voice/tone）。这完全背离了论文试图捕获“软信息（Soft Information）”初衷。

### 2. 实质性改进项（宁缺毋滥）

#### 改进 A：信源多维解构——分离“高管引用语气（Executive Quotes Tone）”与“客观新闻基调（News Sentiment）”
- **论文依据**：论文（P.3、P.6 及图1）强调了书面陈述（Scripted statement）与现场问答（Unscripted Q&A）之间由于语境不同导致的情感分化（Congruence in words and tone is not perfect）。
- **预期的边际贡献（解决内生性问题）**：彻底解决当前因单篇新闻情感同质化而带来的信息冗余内生性。通过大语言模型专门抽取新闻中出现的“银行高管/发言人的直接引语（Direct Quotes）”，并对引语蕴含的隐含底气、保守担忧或亢奋预期（Tone）进行独立量化。这种脱离官方公关外壳的“第一人称情绪”，是纯文本数据中对《AER》中“Voice Tone”最深刻的平替，将大幅提高对企业真实技术战略信号捕捉的信噪比。

#### 改进 B：构造事实冲击隔离变量（Hard Action Dummy vs Media Tone）
- **论文依据**：论文公式(4) `Outcome = b1(VoiceTone) + b2(TextSentiment) + b3(FFRShock)` 严格控制了实质性动作。
- **预期的边际贡献**：要求对文本提炼新增一个布尔维度——判定该新闻所提及的金融科技事项是否为“已落地的硬性投入事实（Hard Action）”。在面板回归中控制此 Action 变量，我们才能纯净地衡量“描述方式”（Tone/Sentiment）本身的经济学溢价，使得项目研究达到顶刊的识别要求。

### 3. 冗余剥离
> [!WARNING]
> 必须“下狠手”剔除毫无学术增量、甚至阻碍结论稳健性的伪需求模块。

- **剔除 `22_tone_words.py`（静态词典法模块）**：论文已证明，捕捉深层情绪或反转语境必须依赖于深度网络或上下文感知的模型（论文使用的是 BERT/RoBERTa 等预训练模型）。当前 `config.yaml` 仍挂载的词典情感分析在复杂财经文本下不仅准度灾难，且极度拖慢大规模数据并行处理效率，完全属于妥协性工业遗骸。**在此定调：立刻废弃，宁缺毋滥。**

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布
- **速赢项（Quick Wins）**：修改配置文件，切断词典法脚本执行节点；利用在代码架构中已存的 `unified CoT`，无缝嵌入针对高管引言与行动评估的 Prompt 重构。
- **核心攻坚项**：基于上述解构，重塑面板特征的聚合方式（`45_panel_export_main.py`），生成三维正交指标集（事实实施 Action / 媒体基调 News Sentiment / 高管语调 Quotes Tone）。

### 2. 阶段化执行指令 (SOP)

#### 阶段一：机制重塑与数据提纯（LLM 预处理优化）
**【直接指示】**修改 `news_process/config/config.yaml` 中的 `tone_llm_processing.prompt_template`。
- **动作 1**：在要求输出 JSON 中加入字段 `"is_hard_action"`（判定银行是否有真金白银的技术投产、而不是概念务虚）。
- **动作 2**：在提取过程中加入专门针对信源引语的深筛： `"exec_quotes": "..."` 和字段 `"quotes_tone": "正面/保守/焦虑（若无引语填 null）"`，强制 LLM 进行“人物发声”特征量化。
- **动作 3**：从 `enabled_methods` 中移除 `tone_words`。

#### 阶段二：实证/模型重构与检验（面板数据衍生）
**【直接指示】**重写特征池（`41_panel_encode_aggregate.py` 至 `45_panel_export_main.py`）。
- **指标拆分**：聚合按（Bank-Year）粒度的横截面特征，抛弃单一的“金融科技情绪分”，变更为：
  1. `Fintech_Action_Index` (硬事实发生强度) 
  2. `Media_Coverage_Sentiment` (总体媒体情感分)
  3. `Exec_Quotes_Tone_Score` (高管预期的 Tone 值，若某年缺失采用插值或中性基准)。
- **经验模型映射**：直接移植论文公式(4)，采用 OLS 或局部投影法评估该三因素对于银行超额收益/风险敞口的非协同冲击。

#### 阶段三：结论重构
**【直接指示】**重点阐述“如何说（How they say it: 媒体/高管语气）”较于“做什么（What they do: 技术硬投入）”是否存在时间维度的超前指引作用，借此向 AER 论文进行核心对话发现。

### 3. 风险预案 (Plan B)

> [!CAUTION]
> 致命卡点预判与挽救措施

- **潜在卡点**：新闻库中包含“高管/直接引用言论”的文本比例极度稀疏（例如不足新闻总量的 10%），导致大批样本在 Quotes Tone 上缺失 (null)，引发回归模型共线或自由度灾难。
- **替代方案 (Plan B)**：
  如果第一人称语料不足，将 Tone 的代理变量降维映射为：**“叙事的亢奋程度（Narrative Exuberance）”**。修改 LLM 任务，让模型对比新闻的客观基础事实，量化其新闻语气的相对膨胀/夸张比例。若媒体刻意用高频强指向性的宏大修辞（颠覆、重塑、领跑），则视同此为高于事实文本情感的“衍生语调（Divergent Tone）”，用其作为 Voice Tone 的替代因子。
