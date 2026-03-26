# Project Introduction (500-word) / 项目介绍（500字版）

---

## English Version

### A Multi-Method Dual-Track Sentiment Analysis System for Bank-Level FinTech News

The rapid adoption of financial technology by commercial banks has made media sentiment toward bank-level FinTech activities a critical yet under-measured dimension in empirical finance. Constructing reliable sentiment indicators from Chinese financial news corpora poses three distinct challenges: (1) multi-entity news articles create a *sentiment attribution problem*, where article-level scores conflate tones directed at different banks; (2) Chinese financial text involves complex linguistic phenomena—negation cascades, degree adverb modulation, adversative conjunctions, and implicit sentiment in official discourse—that preclude direct application of English-language tools; and (3) the absence of multi-method triangulation frameworks in the existing literature limits any assessment of construct validity.

This project develops a comprehensive end-to-end system that addresses all three challenges through a **"Three-Method × Dual-Track"** sentiment measurement framework. Three complementary methods operate in parallel: an **LLM ensemble** (GPT-5 Nano, Gemini 3 Flash, Claude Haiku 4.5) with Chain-of-Thought prompting and anti-contamination directives; a **rule-enhanced lexicon approach** using five Chinese financial sentiment dictionaries augmented with negation, degree, and adversative linguistic rules; and a **BERT ensemble** aggregating five pre-trained financial language models via confidence-weighted sliding window pooling. Each method simultaneously processes a **full-text track** and a **context track**—the latter extracting entity-specific excerpts via a purpose-built engine that performs sentence-level windowing and O(N log N) interval merging around target bank mentions. This dual-track architecture provides built-in cross-validation and quantifies the degree of multi-entity sentiment confounding.

The system's thirteen-module pipeline processes corpora exceeding ten million records, leveraging Aho-Corasick automata for linear-time entity matching, MinHash LSH for sub-linear deduplication, FP16 mixed-precision GPU inference, and asyncio-based concurrent API orchestration. A rigorous validation framework integrates classification threshold sensitivity analysis, dual-coder human annotation (Cohen's Kappa, Krippendorff's Alpha), within-method internal consistency (Cronbach's Alpha), cross-method convergent validity, and context-radius robustness testing.

The final output is a balanced Bank×Year panel dataset in Parquet and Stata formats, containing 200+ variables of equal-weighted and value-weighted sentiment indicators alongside news coverage controls. This panel is directly compatible with standard econometric workflows for studying FinTech adoption effects, media sentiment transmission, and bank risk dynamics.

---

## 中文版

### 面向银行个体的金融科技新闻多方法双轨道情感分析系统

金融科技的快速渗透使得媒体对银行个体层面金融科技活动的情感评价成为实证金融研究中关键但度量不足的维度。从中文金融新闻语料构建可靠情感指标面临三重挑战：（1）多实体报道引发**情感归因问题**，文章级得分混淆了对不同银行的情感倾向；（2）中文金融文本特有的否定级联、程度缩放、转折翻转和官方话语中的隐性情感，使英文工具难以直接移植；（3）现有文献缺乏多方法三角验证框架，无法系统评估单一度量的构建效度。

本项目开发了完整的端到端系统，通过**"三方法×双轨道"**框架应对上述挑战。三种互补方法并行运行：基于GPT-5 Nano、Gemini 3 Flash和Claude Haiku 4.5多数投票的**大语言模型集成**，配合思维链提示词与抗污染指令；整合五部中文金融情感词典并叠加否定、程度和转折语言学规则的**规则增强词典法**；汇聚五个预训练金融语言模型并采用置信度加权滑动窗口池化的**BERT模型集成**。每种方法同时处理**全文轨道**与**上下文轨道**——后者通过专门的实体上下文引擎执行句子级窗口提取和O(N log N)区间合并，聚焦目标银行相关文本。双轨道架构提供内建交叉验证能力，可量化多实体情感混淆程度。

系统的十三模块管道处理千万级语料，采用Aho-Corasick自动机实现线性时间实体匹配、MinHash LSH亚线性去重、FP16混合精度推理和asyncio异步并发API调度。多层验证体系集成阈值敏感性分析、双编码者人工标注一致性检验（Cohen's Kappa、Krippendorff's Alpha）、方法内Cronbach's Alpha一致性、跨方法收敛效度和上下文半径稳健性检验。

最终输出为Parquet和Stata双格式的平衡Bank×Year面板数据集，包含200余个等权重与价值加权情感指标及新闻控制变量，直接兼容标准计量分析工作流，可支撑金融科技采纳效应、媒体情感传导和银行风险动态等多维度学术研究。

---
