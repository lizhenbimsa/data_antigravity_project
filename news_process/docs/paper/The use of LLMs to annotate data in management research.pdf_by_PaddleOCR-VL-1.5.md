# 基于 Carlson & Burbano (2026)《The Use of LLMs to Annotate Data in Management Research》的项目评估与执行计划

=========================================
## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断
**项目现状对标基准**：
当前项目在数据注释机制上已具备极高的前沿性，其中 `21_tone_llms.py` 采用了多模型投票（Majority Vote，包含 GPT-5 Nano、Gemini 3、Claude 4.5）和锁定温度（Temperature=0），并在 `39_prompt_sensitivity.py` 中实现了《管理研究中运用大语言模型：基础准则与警示》(Carlson & Burbano, 2026)中第五阶段提及的“Prompt措辞敏感度的族群测试 (Family of prompts)”的双轨架构（全文 vs 片段）。从模型稳定性和第一阶段的分类一致性（Fleiss' $\kappa$ 等）来看，**当前系统在工程实现上已达到甚至部分优于参考论文的严谨度。**

**核心盲区诊断**：
论文（SMJ §3）的核心理论突破和核心警示机制在于：“第一阶段的分类高准确率，并不能保证第二阶段（下游回归分析）的推断无偏。一旦分类误差与模型应变量存在系统性相关，回归系数将被大幅扭曲”。
当前项目在 `39` 阶段的敏感性分析仅停留在**第一阶段（First-Stage）的一致性观测**（如真伪率的方差、$\kappa$ 矩阵热力图），未能将不同 Prompt 变体对标注的影响穿透输送至下游（Second-Stage Downstream Regression）。这导致项目虽然证明了“分类标签稳定”，却无法解答“核心实证结论（回归系数）是否存在由 Prompt 工程造成的 p-hacking”这一论文关注的终极内生性挑战。

### 2. 实质性改进项（宁缺毋滥）
- **改进 A：将敏感度检验端到端延伸，建立“第二阶段回归系数边界化分析（Bounded Estimates）”** 
  - **论文依据**：论文 Figure 1, Figure 3 以及 Stage 5 要求：“researchers should document the sensitivity of their findings… report bounded estimates that reflect underlying methodological uncertainty.”
  - **预期边际贡献**：打通 `39` 模块的输出结果至模块四（`45` 与 `51` 回归推断模块）。通过向评委展示因 Prompt 差异导致的核心回归系数（$\beta$）分布范围，提前阻断任何审稿人针对 LLM 标注导致“结果操控性质（p-hacking）”的质疑。这为该金融实证项目提供了最强的因果下限证明。

- **改进 B：扩展 Prompt 变体的策略深度（引入推理型策略）**
  - **论文依据**：Table 2 (Prompt Engineering Strategies) 和 §3.3，主张必须比对基础分类指令（Role-Based、Zero-Shot）与复杂推理框架（Chain-of-Thought、Tree-of-Thought）在此类判定中的差异。
  - **预期边际贡献**：目前 `39_prompt_sensitivity.py` 中的 V1-V4 仅属于“表述方式（Wording）”上的句式重组。引入论文推荐的逻辑深度变体（如 `V5_ToT` 思维树变体），可通过结构化消融测试，阐明为何当前 `21_tone_llms.py` 选择的思想链（CoT）处于成本和收益的最佳平衡点。

### 3. 冗余剥离（维持原状与剔除）
- **多模型集成方案无需退推（维持原状）**：当前 `21_tone_llms` 使用异构多模型 Majority Vote，并使用固定的 Temp=0 获取强确定性。论文仅对比了单一各个模型性能，故本项目这一机制**显著优于论文标准，绝对维持原状**。
- **剥离冗杂的第一阶段分析扩充（拒绝形式主义）**：不建议依据论文生成 100 组随机 Prompt。在数据量庞大的金融文本库中（百万级Token开销），100组提示词徒增巨大测试成本而边际校验价值极低，只需保留5-8个经代表性提取的范式变体即可论证稳健性。

=========================================
## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布
- **核心攻坚项（高优先级，强理论收益）**：针对现有变体结果，贯穿进行“回归估计边界（Bounding Estimates）”检验（横跨阶段 39 到阶段 5X 等逻辑链路）。
- **速赢项（Quick Wins）**：向现有的 `39_prompt_sensitivity.py` 数据结构中低成本硬编码加入“Few-Shot”或“Tree-of-Thought (ToT)”两种经典策略的学术基准变体。

### 2. 阶段化执行指令 (SOP)

**阶段一（模型设定与增量评估拓展）**：
- **指令**：编辑 `news_process/39_prompt_sensitivity.py`，向 `VARIANT_PROMPTS` 字典中增加 `V5_few_shot`（带样例对标论文 Few-Shot结构）和 `V6_tot`（Tree-of-Thought结构）两个核心理论基准。
- **交付物**：更新的 `prompt_sensitivity_detail.csv`，使样本具备 Baseline + 6套主流变体的异构标签结果，以备下游使用。

**阶段二（实证重构验证，开发端到端稳健性穿透模块）**：
- **指令**：新增阶段测试脚本（如 `52_downstream_prompt_sensitivity.py`），对 `39` 输出的抽样/或全量数据集执行下述循环：（1）将面板聚合脚本指向特定变体列（如 `$variant$_verified`）；（2）执行简化版的核心 OLS/DID 回归检验；（3）记录所有变体结果所拟合出的参数估计量。
- **检验标准**：不再评价 First-Stage（例如 Kappa 或 Alpha），聚焦记录“变体组的 Coefficient $\beta$, 标准误以及 p-value”。

**阶段三（报告与图表生成）**：
- **指令**：基于阶段二的结果清单，生成用于论文附件的“跨提示词回归系数分布表（Distribution of Downstream Regression Coefficients Across Call-Paths）”。
- **目标输出**：验证并证明在全部 7 种测试环境（Baseline+V1~V6）下，金融科技影响（或情感衰减等研究核心结论）的主影响系数其下限不仅完全显著异于 0，且符号和量级处于一致性区间内。

### 3. 风险预案 (Plan B)
- **风险卡点**：如果使用变体标注去重新拉通 `45` 面板构建与合并、控制变量映射将导致内存爆炸或执行耗时超阈值。
- **替代方案 (Plan B)**：严格遵循论文 3.5 节给出的优化方案（Bootstrapping for Large Samples）。无需在全量几百万条原始数据上跑每个 Prompt 变体。只需（1）针对随机抽样的核心面板样本跑多变体标注；（2）使用这部分子数据建立 Bootstrap 回归拟合，由此描绘核心结论点估计波动的置信区间（$1\sigma$），大幅度缩减运算规模，满足经济发表的敏感试验标准即可。
