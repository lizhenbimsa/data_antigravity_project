# 基于《Human Capital Disclosure and Labor Market Outcomes: Evidence from Regulation S-K》的项目分析与执行计划

=========================================
## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断
- **理论与方法论映射**：参考论文的核心方法学创新在于，为了评估公司披露真实性，使用了生成式大语言模型（GLLM）对极大规模的非结构化文本（520万份招聘启事）进行自动化阅读，从四个预设维度（承诺度、企业文化、员工福利、无歧视要求）分别给出 0/0.5/1 的定量打分，并强制模型提取支持性的“文本片段 (Snippets)”和推理过程，从而**将“高度公司特异性的实质披露 (firm-specific/credible)”与空泛的“套话 (boilerplate)”严格剥离**。
- **当前项目盲区**：目前项目（`news_process`）的阶段21（`21_tone_llms.py`）仅将大模型用作一维的验证仪（真/伪）与情感分类（正面/中性/负面）。这种做法面临严峻的“伪数字化”盲区：我们无法区分某条“正面金融科技新闻”是银行真正投入真金白银的“实质性落地”，还仅仅是顺应政策号召或迎合热点概念的“公关套话（Boilerplate）”。金融科技新闻中同样存在类似 DEI 的 Cheap Talk 现象。

### 2. 实质性改进项（宁缺毋滥）
> - **改进 A：引入基于大模型的多维度“可信度打分”与“套话甄别”机制**。
>   - **[具体修改建议]**：全面重构阶段21的 Prompt，仿照论文对招聘广告的打分机制，对判断为“真金融科技”的新闻增加三个维度的强制打分（0/0.5/1分）：(1) 战略承诺度（如是否有明确的数字化战略目标），(2) 资源投入及技术开发深度，(3) 业务场景落地情况。同时，要求大模型输出对应的“支持性文本片段（Snippets）”，若缺少具体支持性内容，则打上 `is_boilerplate=true` 标签。
>   - **[标明论文依据]**：对应论文 *4.3 Analysis of the DEI Credibility of Job Postings* 节，使用 GLLM 进行多维度定量打分（Scores: DEI Commitment, Corporate Culture等），并利用提取的 Snippets 区分“Firm-specific statements”与“Boilerplate statements”。
>   - **[预期的边际贡献/解决的内生性问题]**：直接破解“金融科技洗绿/嘴炮”带来的测量误差（Measurement Error）内生性。能够构建更干净的“实质性金融科技创新指数（Substantive FinTech Index）”，排除虚构和夸大引发的噪音偏差。

### 3. 冗余剥离
- **直接剔除词典法与中小参数 BERT 情感模块**：配置文件中当前大量保留着极其繁琐的中文情感词典构建（各类程度词、转折词、否定词配重，设于阶段22）和多个性能极度不均的 BERT 变体（设于阶段23）。由于项目已具备结构极其完善的多模型大语言模型阵列（GPT-5 Nano 等，含 CoT，阶段21），且即将升级为更复杂的多维可信度评分系统，传统的词典法和中小模型 BERT 分析在这个量级的研究中已经成为拉低精度下限的“伪需求”，徒增算力消耗与代码复杂度。**建议彻底废弃并移除 `22_tone_words.py` 和 `23_tone_berts.py` 相关代码及它们在 YAML 中的所有配置。**

=========================================
## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布
- **速赢项（Quick Wins）**：清理 `config.yaml` 冗余。删除 `sentiment_analysis` 下的 `tone_words` 和 `tone_berts` 节点配置。移除后置面板阶段不必要的变量对齐代码。
- **核心攻坚项**：重写并测试 `21_tone_llms` 中的 Prompt，设计科学合理的金融科技 3 个打分维度，并调试确保输出准确的 JSON 格式及 Snippets 抽取判定。

### 2. 阶段化执行指令 (SOP)

- **阶段一（机制重塑与Prompt工程）：**
  - **指令**：修改 `config/config.yaml` 中的 `prompt_template`。
  - **交会物标准**：新的 Prompt 必须引入阶段三的“可信度与套话判别”。要求对于判定为 true 的新闻：
    1. 计算三个指标（`score_strategy`, `score_tech_depth`, `score_application`），仅接受 0, 0.5, 1 三个值。
    2. 提取文本中的对应 `snippet_justification`。
    3. 加入布尔值判别 `is_boilerplate`：如果各维度得分总和小于X或者 Snippet 为明显套话，要求 LLM 输出 true。
  - **指令**：同步修改 `21_tone_llms.py` 或对应解析脚本的 Pydantic 模型/JSON 返回值定义，确保新增字段能被平滑写入被解析为 Parquet 的列。

- **阶段二（实证/模型重构与检验）：**
  - **指令**：以 `max_concurrency` 和较小 batch_size，全量重跑 阶段21 的 LLM 推理。
  - **指令**：调整阶段 32 (`32_news_llms_human.py`) 的人工验证脚本。提取验证样本时，重点验证 `is_boilerplate=true` 与 `is_boilerplate=false` 组别在人工视角的差异，证明 GLLM 代替人工甄别“套话”的有效性。此时的验证集应报告 boilerplate 分类的 F1-Score。

- **阶段三（结论重构）：**
  - **指令**：修改 `45_panel_export_main.py`。
  - **动作**：从原本简单的词频构建升级为双重构建：(1) 全量 Fintech 新闻指数；(2) 实质性 Fintech 新闻指数（只筛选 `is_boilerplate == false` 且综合总分阈值不低于 1.5/3.0 的核心样本）。未来的基准回归必须对比这两个变量对银行真实绩效的异质性影响规律。

### 3. 风险预案 (Plan B)
- **风险预判**：将“真伪判定”、“情感单向”和新增的“三维度打分加 Snippets 提取”强行合并在一个 Prompt 里，极易造成小模型（如 GPT-5 Nano 或 Haiku）指令跟随失效，JSON 爆出格式错误或幻觉截断。
- **替代方案 (Plan B)**：放弃“One-Pass”操作，拆分成级联调用（Cascade Calls）。第一次 API Call 维持原有逻辑清洗真伪（是/否为目标银行非套话新闻）。保存结果后，对于判定为 true 的样本批次，单独发起第二次 API Call，采用名为 `prompt_template_credibility` 的特定 Prompt 进行专业的 0/0.5/1 多维打分与 Snippets 抽取验证。这会以增加一定推理时间换取绝对的字段稳定性和任务效果。
