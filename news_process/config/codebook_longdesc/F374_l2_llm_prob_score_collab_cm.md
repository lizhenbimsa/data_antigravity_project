---
family_id: F374
columns:
- llm_prob_score_collab_cm_ctx
- llm_prob_score_collab_cm_ss
unit: 无量纲概率化得分, 取值范围 [0, 1]
formula: 'avg_collab_prob_score{track} = mean_over_valid_models( compute_prob_score_binary(innovation_collab_mode_label_i{track}, confidence_i{track}) ), 三模型 (gpt54nano/gemini31/deepseekv4) 逐篇二分类概率打分后取算术平均; collab_mode 标签空间 = {外部协同, 自主研发} 二元 (平局 tie_default=''自主研发'', conservative=uniform-prior MAP 保守降级)'
producer: pipeline\sentiment\tone_llms.py ; pipeline\panel\encode.py
upstream:
- 15_fintech_intensity.parquet
- 21_tone_llms.parquet
citations:
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1002/smj.507"
  type: journal
  authors: "Laursen, K., & Salter, A."
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: "Strategic Management Journal"
  vol: "27"
  issue: "2"
  pages_or_artno: "131-150"
- doi: "10.1145/1102351.1102430"
  type: journal
  authors: "Niculescu-Mizil, A., & Caruana, R."
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: "Proceedings of the 22nd International Conference on Machine Learning (ICML)"
  pages_or_artno: "625-632"
- doi: "10.48550/arxiv.2207.05221"
  type: "arxiv"
  authors: "Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J."
  year: 2022
  title: "Language Models (Mostly) Know What They Know"
  venue: "arXiv"
- doi: "10.48550/arxiv.2306.13063"
  type: "arxiv"
  authors: "Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B."
  year: 2023
  title: "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"
  venue: "arXiv"
- doi: "10.18653/v1/2023.emnlp-main.330"
  type: "journal"
  authors: "Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C."
  year: 2023
  title: "Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback"
  venue: "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "5433-5442"
- doi: "10.18653/v1/2024.emnlp-main.173"
  type: "journal"
  authors: "Zhang, M., Huang, M., Shi, R., Guo, L., Peng, C., Yan, P., Zhou, Y., & Qiu, X."
  year: 2024
  title: "Calibrating the Confidence of Large Language Models by Eliciting Fidelity"
  venue: "Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "2959-2979"
new_dois: []
---

## CORE

【构念与来源】
llm_prob_score_collab_cm 家族刻画的是"银行的金融科技创新, 究竟是依托外部协同实现, 还是内部自主研发实现"这一判断的概率化强度, 而不是简单的 0/1 类别标签。它的原始判据来自 stage 21 (`tone_llms.py`) 对每篇合格新闻做的第三个分类维度: innovation_collab_mode, 与情感极性判断(正面/负面/中性)、locus 判断(底层技术/应用场景)并列, 三者由同一批大语言模型在同一次异步请求里一并给出。三个 LLM 家族 (gpt-5.4-nano 短名 gpt54nano、gemini-3.1-flash-lite 短名 gemini31、deepseek-v4-flash 短名 deepseekv4, 其中前两家经 OpenLux 网关中转、deepseekv4 直连 api.deepseek.com) 各自独立读文本并给出类别判断与置信度, 再经多数决投票 (majority_vote_categorical) 得到该篇文章 collab_mode 的共识标签; 当票数打平或存在缺票时按保守策略 (conservative=uniform-prior MAP) 回退到 tie_default='自主研发', 目的是不让一个不确定的判断被硬性归为对结论更有利的一侧, 而是系统性偏向"未证实存在外部协同"这一更保守的解释, 从而避免虚报银行与金融科技企业的协同强度。这一分类维度的理论根基来自开放式创新 (Chesbrough, 2003) 与吸收能力 (Cohen & Levinthal, 1990) 两条经典文献: 银行既可以像封闭式创新组织一样把技术能力留在内部积累, 也可以像开放式创新组织一样通过外部联盟、投资、并购获取金融科技能力; 这两种路径在公司战略与创新管理文献中被反复证明具有不同的绩效含义 (Laursen & Salter, 2006), 因此把它们从新闻文本中识别出来, 是论文 P5 (bank_fintech_collab, provisional) 主线构念 collab_frac 的直接文本基础。
llm_prob_score_collab_cm 与其姊妹家族 (无后缀 canonical、以及本家族收录的 _ctx/_ss 两个稳健轨) 共同构成"该篇文章有多大概率被判定为'外部协同型'金融科技报道"的连续化度量。与离散的多数决标签 (只有'外部协同'/'自主研发'两种取值, 且没有区分模型有多确信) 不同, llm_prob_score_collab_cm 把每个模型给出的分类标签与其自评置信度共同折算成 [0, 1] 区间上的一个实数, 再对三个模型取算术平均, 因此它既保留了"哪一类更可能"的方向信息, 也保留了"模型有多确信"的强度信息。这种概率化处理让下游面板分析 (例如聚合成 collab_frac 这一银行-年份维度的外部协同占比测度) 能够使用连续变量做更细粒度的加权和区间估计, 而不是被迫在离散标签上做粗糙的计数。

【方法学与计算】
概率化的具体算法由 `compute_prob_score_binary` 实现 (对应源码注释中的 P2_BIN/P3_BIN 两级处理): 输入是某个模型对某篇文章、某一轨文本给出的 collab_mode 二元标签 (外部协同记为偏向 1 的一侧, 自主研发记为偏向 0 的一侧) 及其置信度 confidence ∈ [0, 1]; 算法先做输入合法性检查, 对 NaN 或越界的 confidence 直接拒绝该条记录参与聚合 (源码标注为 P3_INV, 防止无效置信度污染均值), 通过检查后按标签方向把 confidence 映射、折算到 [0, 1] 区间上离 0.5 (最不确定) 或两端 (最确定) 的位置, 使得"高置信度判定为外部协同"落在接近 1 处, "高置信度判定为自主研发"落在接近 0 处, 置信度越低越向 0.5 收拢。三个模型各自算出这样一个 [0, 1] 分数后, `avg_subst/locus/collab_prob_score{track}` 在 encode.py 里对三家有效值取简单算术平均, 得到该篇文章、该轨文本上的家族级 collab 概率分数; 若某个模型该维度本身缺票或未通过 verified 门控, 该模型的分数记为缺失, 不参与均值分母 (逐模型独立降级, 不是 co-primary 嵌入式的 both-or-neither)。
读者需特别注意两点口径。第一, 三轨 (full/ctx/ss) 各自独立完整地跑一遍这一整套分类与概率化流程, 三轨的 collab_mode 判断彼此互为稳健性、不分主次并排存在, 禁止把三轨的 llm_prob_score_collab_cm 混进同一个 over-identified 的 Hansen J 检验框架, 只能各自作为 just-identified 的稳健性对照使用; full 轨是留篇门控 (2026-06-29 起改为 full-only) 唯一依据, 也就是说, 一篇文章是否被判定为"合法的银行-金融科技报道"只看 llm_verified_full, 而 ctx/ss 两轨的 collab_mode 概率分数是在 full 轨已确定的留篇行集合之上计算的 conditional-on-full 测度/稳健性轨, 它们的样本行宇宙是 full 轨留篇集合的子集, 不会反向影响哪些文章被保留进面板。第二, ss 轨的取材范围回退语义严格镜像 ctx 轨: 当一篇文章里找不到"目标银行与金融科技词汇同句共现"的片段时, `content_ss` 退化为全文正文 (与 content_full 相同), 并把 `ss_is_fallback` 标记为 True, 这时 ss 轨算出的 collab 概率分数实质上是在读跟 full 轨几乎相同的文本, 因此 ss 与 full 出现高相关是预期现象而非异常; 反之当同句共现存在时, ss 轨只读取被严格限定在同一句话内的窗口文本, 判断样本远小于 full/ctx, 概率分数的方差通常更大。ctx 轨介于二者之间, 以实体窗口 (银行与金融科技相关实体附近的句子) 为取材范围, 缺失窗口时同样优雅回退到 content_full。
【文献定位】
本家族在方法学上直接继承了把大语言模型分类输出转换为连续概率度量这一做法, 其合理性受两方面文献支持。一是机器学习校准 (probability calibration) 文献早已指出, 分类器给出的置信度只有经过恰当校准才能被当作概率使用 (Niculescu-Mizil & Caruana, 2005), 本项目通过对置信度设定合法性检查 (拒绝 NaN/越界) 并用简单折算函数而非直接照搬模型自报的原始 logit, 是在计算成本与可解释性之间的折中处理; 二是近年来会计与金融文本分析领域对"用大语言模型做文本标注"这一范式本身进行了系统方法论审视, de Kok (2025, *Management Science*) 系统讨论了在会计研究中使用生成式大语言模型做文本分析时, temperature=0 的确定性推理、prompt 冻结与结果缓存等做法如何影响可复现性与稳健性, 这与本项目 Prompt v8 字节级冻结 + `_llm_cache.db` 确定性锚点的工程实践直接呼应, 也是本仓库为何选择让三个厂商的模型分别独立打分、再做多数决与均值聚合、而不是只信任单一模型输出的方法论依据之一。在构念层面, collab_mode 这一分类维度所测量的"外部协同 vs 自主研发"二分, 源自开放式创新框架下企业在技术获取路径上的经典权衡 (Chesbrough, 2003; Laursen & Salter, 2006, *Strategic Management Journal*): 后者以英国制造业企业为样本, 系统检验了企业对外部知识来源的"开放度"(openness) 如何影响创新绩效, 为本家族把媒体报道中银行与金融科技企业协作的文本线索操作化为一个可度量的开放度代理指标提供了构念上的先例。llm_prob_score_collab_cm 正是把这一组织理论构念嫁接到大语言模型文本分类管线上、并进一步做概率化处理后的产物, 使其既能承接开放式创新文献的理论语言, 也能满足计量分析对连续变量的技术需求。 就 confidence 字段的取数方式与可信性而言, 近年大语言模型置信度文献给出了一条较为完整的证据链。Kadavath 等 (2022) 系统研究了语言模型能否自评答案正确性, 发现较大模型在格式恰当的多选/判断题上校准良好, 并提出先给答案再自评 P(True) 的自评范式, 为"LLM 自评概率携带真实信息、具备一定校准性"这一前提提供了早期奠基性证据; 但其自评经由专门的 P(True)/P(IK) 探针与 logit 读数, 与本家族从 prompt 结构化输出字段直接读取 confidence 的做法并非同一路径, 模型代次为 2022 年 Anthropic 内部模型, 与本项目三家生产模型不可比, 原文亦未提出把剩余概率在非主类间按最大熵均分再作差的映射——该映射系研究者选择。Xiong 等 (2023) 是黑箱场景下"直接向 LLM 索取自报置信度"这一 elicitation 范式的系统评测原点, 建立了 verbalize-based confidence 的基准协议并记录了模型普遍过度自信, 交代了本家族 conf 列取数方式的方法来源; 其评测对象为当时的 GPT/LLaMA 系模型, 任务为英文常识与算术推理, 不含本项目所用模型, 亦无面板聚合。Tian 等 (2023) 进一步证明对经 RLHF 微调的模型, 以自然语言索要口头概率所得的置信度比模型内部 logit 条件概率更为校准, 这正是本家族在商用 RLHF 类模型上以 prompt 索取 confidence 字段、再送入概率折算的实证依据; 但原文在英文事实型 QA 数据集上度量 ECE, 本项目未在中文银行—金融科技语料与创新维度分类上复测 ECE, 该校准优势能否迁移至两家非 OpenAI 模型亦未经验证。Zhang 等 (2024) 把语言模型置信度分解为对问题的不确定性与对自身所生成答案的保真度, 提出 UF Calibration 并在多个 RLHF-LM 与 MCQA 数据集上验证, 另提出 IPR/CE 两个校准评价指标, 表明 LLM 置信度可被分解并校准; 惟其置信度由 UF 分解估计得到而非自报值, 该方法在仅可访问输出的黑箱 API 场景下是否适用原文未作声明, 且其所需的选项集/参考答案结构在本家族 collab_mode 二分类标注中并不具备, 故本项目未实施该校准算子, 现口径仍为三家原始自报置信度经二分类概率折算后取算术均值。
## VAR: llm_prob_score_collab_cm_ctx

【变体差分】
本列是家族在 ctx (实体窗口) 轨下的取值, 取材范围限定为"标题 + 目标银行/金融科技相关实体附近窗口内的句子" (`content_ctx`, 由 stage 14 `ctx_materializer` 物化, prepend_title 拼接标题), 而非全文正文。它与 canonical 的 full 轨 (`llm_prob_score_collab_cm` 无后缀, 若存在于 panel 中) 共享完全相同的三模型多数决 + `compute_prob_score_binary` 概率折算 + 简单均值聚合算法, 唯一差别是喂给三个 LLM 的输入文本更短、更聚焦。这意味着 ctx 轨的判断建立在"文章中提到银行/金融科技的那一小块上下文"上, 剔除了全文中可能存在的、与协作模式判断无关的段落 (例如银行的其他业务新闻、监管公告转述等), 理论上应当降低噪声但也可能因窗口截断丢失关键的协作细节描述 (例如具体的合作方名称、合作金额出现在窗口之外)。ctx 轨与 full 轨、ss 轨三者互为稳健性、并排存在、不分主次, 三者数值间出现分歧 (尤其在窗口截断导致信息缺失的情形下) 是预期现象, 不代表其中某一轨"更对", 使用者在做识别策略设计时应把三轨都作为独立的 just-identified 稳健性检验对照, 禁止把三轨混入同一个 over-identified 的 Hansen J 过度识别检验。ctx 轨样本行宇宙同样受 full-only 留篇门控约束: 一篇文章是否进入面板取决于其 full 轨的 llm_verified_full 判定, ctx 轨概率分数只在该留篇集合内计算, 是 conditional-on-full 的稳健性测度, 不参与留篇决定本身。当该篇文章缺乏可识别的实体窗口 (`ctx_is_fallback=True`) 时, `content_ctx` 退化为全文, 此时本列数值与 full 轨在取材上趋同, 二者差异主要来自模型对相同文本重复推理时的随机性残余 (虽然 temperature=0.0 下理论上应确定性一致, 但缓存命中键、prompt 版本等因素仍可能带来边际差异)。

## VAR: llm_prob_score_collab_cm_ss

【变体差分】
本列是家族在 ss (同句共现) 轨下的取值, 取材范围进一步收窄为"标题 + 目标银行与金融科技相关词汇在同一句话内共现的片段" (`content_ss`, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 生产默认为 1, 即以命中句为中心向前后各扩展一句、共约三句窗口, 而非零半径的严格同句; 注意该键与 stage 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同的配置项, 不可混用)。ss 轨相较 ctx 轨施加了更严格的取材约束: ctx 轨允许银行实体与金融科技实体分别出现在窗口内不同的句子, 而 ss 轨要求二者的核心共现落在以同句为中心的窄窗口内, 因此 ss 轨能读到的文本量通常仍显著小于 ctx 与 full (但并非退化到单句), 这使得 ss 轨上的 collab_mode 分类与概率化打分更容易受制于该窄窗口本身是否恰好包含足以判断'外部协同/自主研发'的信息量——很多协作细节 (合作对象、合作方式) 需要跨句叙述才能完整表达, 而±1句窗口虽比 ctx 更聚焦, 仍可能只捕捉到浅层的共同提及, 缺乏充分的判据支撑, 这一点在解释 ss 轨概率分数偏向 tie_default 保守值 (即偏向 0, 代表自主研发/未证实协同) 时应予以关注。
ss 轨的回退语义严格镜像 ctx 轨的设计: 当一篇文章找不到银行与金融科技词汇同句共现的片段时, `content_ss` 直接退化为全文正文 (与 content_full 相同), 并将 `ss_is_fallback` 标记为 True, 与 ctx 轨的 `ctx_is_fallback` 共享同一套"缺失同句窗口即优雅降级为全文"设计原则, 而不是让该篇文章的 collab 概率分数变为缺失值; 这一设计保证了 ss 轨在 n_articles 分母口径上与 full/ctx 轨保持一致, 不会因窗口构造失败而人为缩小样本。ss 轨与 full、ctx 两轨一样是 full-only 留篇门控之下的 conditional-on-full 稳健性测度, 三轨互为稳健性、各自 just-identified 并排存在、不分主次, 严禁混入同一个 over-identified 的 Hansen J 检验; 三轨间数值差异, 尤其是 ss 轨相对更极端或更接近 tie_default 保守值的分布形态, 应被理解为取材范围收紧带来的信息量差异, 而非模型判断质量本身的差异。当同句共现存在且信息充分时, ss 轨提供了三轨中判据最严格、最不易受无关段落干扰的协作模式概率化度量, 是 full/ctx 两轨之外的第三重稳健性交叉验证。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2306.13063
Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
Zhang, M., Huang, M., Shi, R., Guo, L., Peng, C., Yan, P., Zhou, Y., & Qiu, X. (2024). Calibrating the Confidence of Large Language Models by Eliciting Fidelity. Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, 2959-2979. https://doi.org/10.18653/v1/2024.emnlp-main.173
<!-- rendered-citations:end -->
