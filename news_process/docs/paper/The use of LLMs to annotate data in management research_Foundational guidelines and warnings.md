【角色设定】
你是一位顶尖的学术评审与项目操盘专家，精通理论框架推演与实证金融学项目落地。输出要求极致精简、直击痛点、逻辑严密。

=========================================
第一部分：基于参考论文的项目分析与诊断报告

1. 范式映射与盲区诊断：
   论文《The use of LLMs to annotate data in management research》的核心机制在于：LLM标注的第一阶段高准确率不能保证下游回归的无偏性，因为若分类误差的方向与下游变量相关，会导致严重的内生性偏误。因此，必须通过“系统性Prompt变体生成（覆盖多种基础推演策略）”及其下游结果分布分析来界定影响边界。
   盲区诊断：反观当前项目（如`39_prompt_sensitivity.py`），虽然不仅具备了提示词敏感度测试的意识（注释更是直接引用了该论文框架），但其工程实现存在重大断层。当前仅采用人工硬编码的4种变体（Role、Structure、Concise、Paraphrase），它们本质上是单一思维框架（CoT）下的“同义词组替换（Paraphrasing）”，而未实现论文强调的跨策略族系测试（如Zero-Shot vs Few-Shot vs ToT vs RoT等），这导致了测试范围受限，不足以衡量在不同逻辑路径下的模型异质性方差。

2. 实质性改进项（宁缺毋滥）：
   - 改进 A：升级Prompt敏感度测试体系，从“句法改写（Paraphrasing）”转向“全策略家族生成（Strategy-based Prompt Families）”。
     -> [标明论文依据]：第三节 Prompt Engineering (Table 3) 及 Figure 2（Template for producing family of prompt variations）。
     -> [阐述预期的边际贡献/解决的内生性问题]：能够彻底打破单一逻辑推理方式的局限。针对Zero-Shot、Few-Shot、Role-Based、CoT、ToT、RoT进行组合测试，才能准确捕获模型由于不同激活特征对标签偏移产生的影响，真正达到论文推崇的最佳敏感性鲁棒边界检验。
   - 改进 B：将敏感度评估终端从单纯的“标注一致率（Kappa/Alpha指标）”切透到下游面板及“回归系数分布（Distribution of Regression Coefficients）鉴定”。
     -> [标明论文依据]：Section 3.5 (Validation and robustness) 及其中心主线——The direction of the first-stage error will bias the second-stage coefficients downwards。
     -> [阐述预期的边际贡献/解决的内生性问题]：从方法学上阻断 p-hacking 隐患。通过引入对下游经验回归系数分布（区间估计），展示即使 Prompt 改变带来了标签的局部微动，自变量与因变量的核心正向/负向关系在统计学上始终具有稳健的界定。

3. 冗余剥离：
   当前 `39_prompt_sensitivity.py` 中的硬编码变体构建（V1_role 至 V4_paraphrase），在方法论厚度上存在局限，属于为测试而测试的半成品“伪需求”。建议直接将其剔除，并将全部算力转向系统级Prompt模板字典读取。

=========================================
第二部分：项目重构与优化执行计划书

1. 优先级排布：
   - 速赢项（Quick Wins）：快速改写 Prompt 变体池机制，引入基于外部 CSV/JSON 读取功能的系统性策略字典解析功能。
   - 核心攻坚项：打通 39 模块至下游（45面板/回归）的管道链路，通过生成不同变体的标注组，批量化拟合下游模型以绘制回归系数稳健分布图谱。

2. 阶段化执行指令 (SOP)：

   阶段一（机制重塑/数据清洗）：
   - 动作指令：编写独立脚本 `tools/generate_prompt_families.py`。依照论文 Figure 2 的元提示词模版，输入到最新大模型进行泛化，自动生成包括 zero_shot, few_shot, role_based, cot, self_consistency, tot, rot 共七大类别的各 5 种随机变体，输出并保存为 `config/prompt_variants_strategy.csv`。交付物为可插拔调用的Prompt字典库。

   阶段二（实证/模型重构与检验）：
   - 动作指令：深度重构 `39_prompt_sensitivity.py`，剔除 V1-V4 硬编码序列，代之以循环调用外部 CSV 文件中提取的 35 种核心变体进行 `run_variant_llms` 多模型双轨推理请求计算。执行并保存 35 种变体下各自的 `llm_verified` 定量结果体系。

   阶段三（结论重构）：
   - 动作指令：在面板数据合并（Stage 41-45）之后，新增评估模块。分别取 35 种标注矩阵进行独立的回归计算，提取系数 $\beta$ 及显著性 P-value。并对齐论文（Figure 3），使用 Matplotlib 绘制该 35 批次实验所产生的统计分布图，直观展现 “True Effect”的上下边界，以验证结论稳健性。

3. 风险预案 (Plan B)：
   - 并发与成本超时：当变体数剧增，API Token开销可能面临极速攀升以及高并发速率限制（Rate Limit）。
   - 替代方案（降本手段）：采用论文 Section 3.6 中推荐的“短句摘要（Short Descriptions）降本法”。结合项目现有的 `content_ctx` 双轨架构，若 Full Track 遇到性能和成本瓶颈时，可以一键收缩至全流程仅使用 Context-Snippet Track。由于只测试 Prompt 措辞敏感性，该截断机制对鲁棒性分布的影响极小，却可削减高达80%的成本消耗。
