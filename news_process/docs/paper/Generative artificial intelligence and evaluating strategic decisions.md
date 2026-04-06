# 基于《Generative artificial intelligence and evaluating strategic decisions》的项目分析与执行计划

## 第一部分：基于参考论文的项目分析与诊断报告

**1. 范式映射与盲区诊断：**
参考论文的核心发现是：生成式AI在单一视角的战略决策或复杂评估中，存在极其显著的“不一致性（Inconsistency）”与“排列偏误（Bias）”。但通过引入“群体智慧”——即构建**多样性（多模型、多角色Role、多提示词Prompt）**与**规模化（多次评估聚合）**的AI评委团，其评估准确度和专家共识度会发生质的飞跃。
对照当前项目 `news_process` 现状，盲区在于：项目已有对LLM及提示词敏感性探讨的基础（如 `32_news_llms_human.py`, `39_prompt_sensitivity.py`），但模型设计可能仍停留在“单模型、单角色直接输出决定”的线性单薄模式。未能利用LLM“角色扮演（Role-playing）”来提供认知多样性，也未能通过群体智慧防伪并抵消单一LLM对信息结构的固有偏好。

**2. 实质性改进项（宁缺毋滥）：**
- **改进 A：构建基于大模型评审团的“多样性评估模型”（Diversity-based AI Evaluators）**
  -> **标明论文依据：** Study 1 & 2揭示的 Diversity effect。论文通过集成不同LLMs、10种Persona Roles（如投资者、高管、外部评论员网络）及不同Prompts来产生多样化视角。
  -> **阐述预期的边际贡献/解决的内生性问题：** 通过引入多维角色，强制大语言模型以不同站位进行文本研判，从而产生认知冲突与互补，完美抵消单一大模型处理长文本信息所自带的主观偏差和定位盲区（解决测度单向度的内生噪音）。

- **改进 B：引入规模平滑与聚合验证机制（Scale-based Validation）**
  -> **标明论文依据：** Scaling effect。论文指出规模化的多次判断（如换序 A vs B / B vs A，多次抽样计算胜率）能最大幅度拉升AI评判置信度直至超越普通人类。
  -> **阐述预期的边际贡献/解决的内生性问题：** 将绝对值的评分判定，降维改写为“多次评估求共识概率（Win Proportion / Consensus）”。这解决了直接依靠大模型抽卡带来的回归极端值和幻觉问题，使得文本分析分数（如Tone或Sentiment）具备高度抗压的统计学稳健性。

**3. 冗余剥离：**
明确建议直接剔除 `22_tone_words.py`（词典法）与 `23_tone_berts.py`（传统黑盒BERT）。上述方法缺乏生成式AI进行角色模拟的逻辑推理能力，且与本项目追求的高度复杂语境理解背道而驰。保留其不仅消耗系统算力，更是偏离基于生成式AI框架主线的“伪基准”。

---

## 第二部分：项目重构与优化执行计划书

**1. 优先级排布：**
- **速赢项（Quick Wins）**：清理冗余代码，重构 `21_tone_llms.py`，将其改写为多角色驱动机制，用相同的廉价LLM（如低成本或开源模型API）配置4-5种基础核心角色（Founder, Investor, Critic, Employee），引入Base聚合共识分。
- **核心攻坚项**：重构新闻与文本的大规模评估引擎，利用双盲交叉验证或循环推理（A vs B, B vs A）进行共识投票计算及去偏（De-biasing）引擎搭建。

**2. 阶段化执行指令 (SOP)：**

- **阶段一（机制重塑/数据清洗）：**
  - **核心动作指令**：立即下线/删除 `22_tone_words.py` 和 `23_tone_berts.py`。全面升级 `21_tone_llms.py` 内部逻辑。增设角色字典（Role Config），同时实现 `Prompt=Base` 与 `Prompt=Chain-of-Thought` 参数控制，使单条新闻输入能在后台自动发散成 `Roles × Prompts` 的请求矩阵。
  - **交付物标准**：输出支持多维度模拟及并行请求调用的LLM统一分析组件库（Comprehensive AI Evaluator API Backend）。

- **阶段二（实证/模型重构与检验）：**
  - **核心动作指令**：在 `33_news_llms_evaluation.py` 中编写平滑聚合算法。将底层打分结果归一化。计算统一AI评估团的置信度。针对核心文本段落，实施对倒顺序和异质性提问（Consistency Checks），若存在严重冲突则拉取中位数或多数表决共识。
  - **稳健性检验标准**：统计模型内部的变异系数（CV），必须论证出“集成了不同Role与Prompt的综合得分”相较于“单一Prompt评估”拥有更低的结果方差，重现论文中的方差收敛特性。

- **阶段三（结论重构）：**
  - **核心动作指令**：在 `41_panel_encode_aggregate.py` 及以后的全部回归组（`42` 到 `45`）中，默认将最终用于面板建模的自变量替换为基于 **Comprehensive AI Evaluator** 生成的高稳健共识分数（Consensus Score）。

**3. 风险预案 (Plan B)：**
若矩阵式多角色调用（N个Roles × 2种Prompts）对数十万条新闻库引发不可控的API成本崩盘或并发限流（Token耗尽）：
- **替代预案**：退而求其次剥离全量矩阵运算。退化为使用单一高性能基座（如单一的 Claude-3.5-haiku 或 GPT-4o-mini），但强制它在同一个长Prompt中模拟出三个不同视角的分析报告并要求其自行给出带权重的“共识折衷评分（Wisdom consensus inside one response）”，从而在一轮交互内极大压榨模型的内部多样性能力，控制调用成本。
