【角色设定】
你是一位顶尖的学术评审与项目操盘专家，精通理论框架推演与实证金融学项目落地。输出要求极致精简、直击痛点、逻辑严密。

=========================================
第一部分：基于参考论文的项目分析与诊断报告

1. 范式映射与盲区诊断： 
参考论文《ChatGPT for Textual Analysis? How to use Generative LLMs in Accounting Research》的核心机制是探讨 Generative Large Language Models (GLLMs) 替代传统非生成式 NLP 方法解决复杂会计/金融文本任务的能力。论文证明了 GLLMs 在零样本（zero-shot）下即可实现超强的情境推理，并提出“漏斗策略”（Funnel approach，先用低成本关键词法过滤，再交由 LLM 解决硬核分类）以控制成本；最后，其特别强调在学术应用中必须建立人工验证评估集（Construct Validity），并严密控制可复现性（Replicability）。

**当前项目诊断：维持原状。**
当前项目（news_process）的机制已在极高标准上契合甚至超越了参考论文的部署规范。我们在阶段11与12成功实施了廉价的结构与关键词筛选（精确切合论文的漏斗策略），在阶段21采用统一的多 LLM 模型（GPT-5、Gemini 3、Claude 4.5）使用 Chain-of-Thought 进行零样本推理，并在阶段32-39配置了完整的人工验证集（样本数1000）、提示词敏感度、实体掩码和多重统计有效性检验系统。主体文本分析逻辑已处于逻辑自洽且超越本论文实践水平的最优态，因此核心架构应当维持原状。

2. 实质性改进项（宁缺毋滥）： 
- 改进 A： **全面强化 LLM 原始生成数据的内容备份以确保可复现性** -> 依据论文 [Section 5.2 Replicability] -> 论文明确指出鉴于第三方 API 模式下大模型的不可预测性，研究者必须“always store and backup the raw prompts and completions exactly as they enter in and exit out of the source”。当前流水线应当保证每一条经解析的 json 背后，无损保留其输入 Prompt 和生成的原始 completion 字符串，以解决基于云端 API 的内生性数据验证衰变问题。

3. 冗余剥离：
当前项目配置中依然包含了 `22_tone_words.py` (词典法) 和 `23_tone_berts.py` (BERT基础模型) 相关的生成文件与路径声明。鉴于项目阶段21已经彻底证明了多大语言模型融合的优越性，且论文多次批判静态字典和浅层机器学习在复杂语境下的局限，这类“退化”的冗余模块应被直接作为偏离主线且价值极低的“伪需求”剔除，以保证理论框架的纯净度。

=========================================
第二部分：项目重构与优化执行计划书

1. 优先级排布： 
- **速赢项（Quick Wins）**：清理并剥离旧时代文本分析方法（词典法、BERT）的废弃脚本、配置文件及词典依赖。
- **核心攻坚项**：为 `21_tone_llms.py` 的数据产出增加无损快照留存机制（Raw Prompts & Completions）。

2. 阶段化执行指令 (SOP)：

**阶段一（机制重塑/数据清洗）：**
- 指令 1：在流水线任务调度中，完全剔除 `22_tone_words.py` 与 `23_tone_berts.py`。
- 指令 2：在 `config.yaml` 中删除 `tone_dicts_file`, `sentiment_dicts_dir` 等配置，移除 `output_22_words_tone` 与 `output_23_bert_tone` 定义，仅保留 `tone_llms` 作为唯一信任的情感定性信源。

**阶段二（实证/模型重构与检验）：**
- 指令 1：修改 `21_tone_llms.py` 解析模块，在导出的 `21_tone_llms.parquet` 文件结构中强制增设 `raw_prompt` 与 `raw_completion` 两列数据（字符串格式），确保与解析用的各 json 字段平行存储。
- 指令 2：核对 `config.yaml` 确认 `temperature: 0.0` 以及 `random_seed: 42` 作为全局冻结配置项不可变，并以此作为回复审稿人（Replicability）的关键操作点。

**阶段三（结论重构）：**
- 指令 1：在项目主说明文档（如 README 或 Methodologies 部分）显式添加《LLM assistance statement》，内容不仅需声明代码辅助，必须申明文本情感测量的方法论完全符合 De Kok (2024) 所倡导的 GLLM Zero-Shot 范式。

3. 风险预案 (Plan B)： 
- 致命卡点：强行将 `raw_prompt` 和长文本 `raw_completion` 写入主干 Parquet 文件会导致数据体积呈指数膨胀，乃至引发 OOM（内存耗尽）或降低下游面板聚合清洗的性能。
- 替代方案：实施分离式冷热存储架构。修改 `21_tone_llms.py` 使主 Parquet 仅含结构化 JSON 提取结果用于下游实证，同时将包含 `docid`, `llm_model`, `raw_prompt`, `raw_completion` 的详细日志序列化存储至独立的 `.jsonl` 或辅助压缩包内存档备查，以时间换取空间。
