# 依据 De Kok (2025)《ChatGPT for textual analysis? How to use generative LLMs in accounting research》的项目审查与执行计划

=========================================
### 第一部分：基于参考论文的项目分析与诊断报告

**1. 范式映射与盲区诊断**
- **核心机制映射**：De Kok (2025)指出GLLMs的核心优势不仅在于替代传统ML，更在于其通过自然语言提示实现**多维特征的零样本联合提取（Multidimensional Extraction）**，以及基于大模型自左向右生成文本特性而构建的**真实思维链逻辑（Chain-of-Thought, CoT）**。
- **项目盲区诊断**：当前项目（`config.yaml` 的Stage 21）虽然建立了前沿的多模型交叉验证与LLM推理体系，但在底层提示工程执行上存在**违背大语言模型自回归生成机制**的盲区：JSON输出模版中先要求大模型输出最终结论（`is_bank_fintech_news: true/false` 和 `sentiment`），其后才输出推理理由（`verification_reason` 和 `sentiment_reason`）。这种排列导致模型在给出判定结论时，实际上并未享有“中间计算推理（Intermediate Reasoning）”缓冲，白白丧失了CoT消除幻觉的红利；同时，当前应用仍局限于传统“情感倾向”单一维度，未遵循文献指引发挥“多维语义解构”的全部效能。

**2. 实质性改进项（宁缺毋滥）**
- **改进 A：重排 JSON 输出序列以激活底层 CoT 推理红利**
  - **具体建议**：修改 Stage 21 的 Prompt 模板，在 `output_format` 前端优先放置 `verification_reason` 字段，然后再放置 `is_bank_fintech_news`；优先放置 `sentiment_reason`，然后再放置 `sentiment`（参考论文 Appendix C/D：要求模型先做 "assessment"，再给出 "your_classification"）。
  - **论文依据**：De Kok (2025) Appendix C明确指出：“GLLMs Generate Text Left to Right... the explanation becomes part of the context that can help create better and more consistent classifications relative to only asking the model to do the final classification.”
  - **预期边际贡献**：无需额外增加 Token API 成本，仅靠顺应左到右生成的特性迫使模型“先思后答”，即可显著降低分类中的假阳性和幻觉偏误，从源头提高核心变量度量的极化信噪比。

- **改进 B：嵌入复杂的管理层语境联合表征（粉饰度与实质阶段）**
  - **具体建议**：在 LLM 的单次查询中新增对“科技赋能应用阶段（务虚规划 vs. 实质落地）”与“文本修辞粉饰度及炒作度（Hype/Sentiment Spin：客观陈述/夸大渲染）”维度的联合提取判定。
  - **论文依据**：论文 Case Study （Section 4.2）展示了将非回答（Nonanswer）分解为理由、问题类型、情感粉饰（Sentiment spin）等多个维度的做法。利用大模型极低的边际多维抽取成本刻画复杂的公司沟通策略。
  - **预期边际贡献**：打破传统的“正面/负面”单向限制，为主回归提供针对金融科技“伪科技/漂绿（Greenwashing）”噪音的精准剔除机制，更能创造有深度的异质性检验控制工具。

**3. 冗余剥离**
- **基于漏斗架构（Funnel Approach）的低性能 BERT 冗余清理**：De Kok指出，对千万级语料应采取漏斗式架构以节约成本。当前项目采用前置词表等规则过滤（Stage 00/11/12）并连接至精细化大语言模型阵列（Stage 21），已完美契合 Funnel 范式。在此背景下，`tone_berts` 模块同时并行了5个不同源的情感模型。像 `hw2942` 和 `erlangshen` 等以小规模新闻或百科预料训练、模型参数与泛化能力均偏弱的网络，在已有强力 LLM 三角验证下，完全属于对集群算力及磁盘 I/O 的伪需求浪费。建议坚决剥离其他，仅保留学术界认可度最高、金融泛化最稳的基准网络（如 `finbert_cn` 和 `fin_sent_zh`）充当词典法与 LLM 法之间的基准对照。

=========================================
### 第二部分：项目重构与优化执行计划书

**1. 优先级排布**
- **速赢项（Quick Wins）**：篡位重排序 `config.yaml` 中 LLM 输出 JSON 序列（完全解锁 CoT 特效）；裁剪表现欠佳的冗余小微 BERT 模型。
- **核心攻坚项**：为 Prompt 追加科技语境衍生维度（落地实质性、战略粉饰度）判定；并打通至后端的 `39_prompt_sensitivity` 与 `34_sentiment_validation` 验证框架体系中。

**2. 阶段化执行指令 (SOP)**

- **阶段一（底层机制重塑与网络架构瘦身）：**
  - **核心动作 1**：修改 `config.yaml` 中 `tone_llm_processing.prompt_template`，强制令 `output_format` 为严格顺延逻辑推理的结构：
    ```json
    {
      "verification_reason": "先输出详细的金融科技关联性判定依据...",
      "is_bank_fintech_news": true/false,
      "confirmed_bank": "确认关联的银行...",
      "fintech_topic": "主题简述...",
      "fintech_category": "分类...",
      "sentiment_reason": "先输出情感偏向判定依据...",
      "sentiment": "正面/中性/负面",
      "sentiment_confidence": 0.0~1.0
    }
    ```
  - **核心动作 2**：在配置文件 `sentiment_analysis.tone_berts.models` 中剔除或注释低价值基线（保留 `yiyanghkust/finbert-tone-chinese` 及 `bardsai/finance-sentiment-zh-base`）。
  - **交付物标准**：高信噪比生成、参数极致精简的 `config.yaml` 配置文件。

- **阶段二（实证/模型重构与特征增强）：**
  - **核心动作**：在 Stage 21 的 Prompt 指令模版中新增结构化输出定义指令：
    1. 新增字段 `"implementation_status": "务虚战略规划 / 已有实质落地 / 无法判定"`。
    2. 新增字段 `"hype_spin": "客观中立陈述 / 重度主观修饰与夸大"`。
  - **交付物标准**：更新的 `21_tone_llms.py` 处理脚手架代码；数据层输出包含 `implementation_status` 与 `hype_spin` 列的 `21_tone_llms.parquet` 表格。

- **阶段三（结论架构与高阶鲁棒检验重塑）：**
  - **核心动作**：介入现有的检验与评估组件（Stage 3X），针对新生成的 `implementation_status` 和 `hype_spin`，配置与现有情感度（Sentiment）平行的多元一致性评定指标计算（Krippendorff's Alpha, Cohen's Kappa），纳入验证统计与报告系统。
  - **交付物标准**：囊括新增标签维度的学术级验证检验报告输出，保障新特征维度的置信度可溯源。

**3. 风险预案 (Plan B)**
- **预判致命卡点**：将数个带有极强发散特征的 “*reason” 推理字段全盘前置于 JSON 返回结构，可能会触发那些上下文长度严格锁定（或设定 Max_tokens 极强管控）特性的轻量级模型（例如此方案里的 `gpt-5-nano` 或早期 Gemini flash 版本）过度发散回答并触发截断机制，导致后续的标准 JSON 序列完全崩溃、核心键值对丢失。
- **替代方案 (Plan B/Chaining Prompts)**：
  - 倘若运行监控中捕获到大面积（>5%）的 JSON Token Truncation，则立即采用 De Kok 给出的另一关键范式——“Chaining Prompts”。将单请求切断：
    请求 A：专门下发无冗长推理的严格多字段解析框架判定任务（分类+多维标签）。
    请求 B（针对命中类目子样本）：使用专门包含“请详细论述为什么”的结构体诱发 CoT。
  不仅绕开了截断上限，更能利用更廉价的算力在请求 A 阶层迅速清洗杂音数据。
