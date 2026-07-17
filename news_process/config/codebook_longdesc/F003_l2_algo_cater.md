---
family_id: F003
columns:
- algo_cater_ctx
- algo_cater_full
- algo_cater_ss
unit: 情感倾向差值 (无量纲, 两个归一化 tone 之差, 取值近似 [-2, 2])
formula: "algo_cater{track} = dict_avg_tone{track} - llm_vote_tone{track}"
producer: news_process/pipeline/panel/runner.py (步骤 8d, 算法迎合度全展开); 标签 news_process/pipeline/panel/export.py
upstream:
- "22_tone_words.parquet (dict_avg_tone{track}: 六词典综合词典语调)"
- "21_tone_llms.parquet (llm_vote_tone{track}: 三家 LLM 多数投票共识语调)"
- 24_herd_decay.parquet (df_exploded, article×bank verified 集, 面板聚合前主输入)
citations:
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: 110
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1146/annurev-economics-082222-074352
  type: journal
  authors: Ash, E., & Hansen, S.
  year: 2023
  title: "Text algorithms in economics"
  venue: Annual Review of Economics
  vol: 15
  issue: 1
  pages_or_artno: 659-688
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: "10.2139/ssrn.5153587"
  type: "wp"
  authors: "Bose, I., Hu, N., Liang, P., & Yang, X."
  year: 2025
  title: "Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment"
  venue: "SSRN"
  pages_or_artno: "5153587"
- doi: "10.1145/3677052.3698675"
  type: "journal"
  authors: "Kim, W., Spörer, J., Lee, C. L., & Handschuh, S."
  year: 2024
  title: "Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER"
  venue: "Proceedings of the 5th ACM International Conference on AI in Finance"
  pages_or_artno: "626-633"
- doi: "10.1093/pnasnexus/pgaf069"
  type: "journal"
  authors: "Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L."
  year: 2025
  title: "Are chatbots reliable text annotators? Sometimes"
  venue: "PNAS Nexus"
  vol: "4"
  issue: "4"
  pages_or_artno: "pgaf069"
- doi: "10.1017/s0047279424000382"
  type: "journal"
  authors: "Gielens, E., Sowula, J., & Leifeld, P."
  year: 2026
  title: "Goodbye human annotators? Content analysis of social policy debates using ChatGPT"
  venue: "Journal of Social Policy"
  vol: "55"
  issue: "2"
  pages_or_artno: "385-404"
- doi: "10.2139/ssrn.4961494"
  type: "wp"
  authors: "Yang, Y., Duan, H., Liu, J., & Tam, K. Y."
  year: 2024
  title: "LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research"
  venue: "SSRN"
  pages_or_artno: "4961494"
- doi: "10.1016/j.eswa.2023.122936"
  type: "journal"
  authors: "Lin, W., & Liao, L.-C."
  year: 2024
  title: "Lexicon-based prompt for financial dimensional sentiment analysis"
  venue: "Expert Systems with Applications"
  vol: "244"
  pages_or_artno: "122936"
- doi: "10.2139/ssrn.6143029"
  type: "wp"
  authors: "Wang, Y., Wong, T., & Zhang, T."
  year: 2026
  title: "Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "6143029"
new_dois:
- 10.1093/rfs/hhad021
- 10.1111/1911-3846.12832
---

## CORE

【构念与来源】
算法迎合度 (algorithmic catering) 度量的是同一批银行金融科技报道在两套异质情感测度下的系统性落差: 一端是基于关键词计数的综合词典语调 dict_avg_tone (六部中文金融情感词典逐词匹配后归一化的均值), 另一端是基于大语言模型语义理解的共识语调 llm_vote_tone (三家 LLM 多数投票所得的篇章级倾向)。本家族取二者之差作面板列, 正值表示词典读法比深层模型读法更正面, 负值反之。其构念直觉源自 Cao et al. (2023) 的核心洞见: 当信息发布方知道自己的文本会被机器算法阅读并据以定价时, 会策略性地调整措辞以迎合算法的读数, 使得表层关键词情感与语义实质情感产生可测量的背离; 这一背离本身即是"面向算法写作"这一行为的代理变量。对新闻语料而言, 报道措辞的关键词正面性与其经语义模型判读的实质正面性之间的缺口, 捕捉的是媒体文本中"堆砌正面词却语义空洞"或"字面中性而语义负面"一类的表里不一, 是研究媒体语气可信度、报道操纵与算法可读性策略的直接抓手。

【方法学与计算】
本列在面板总装阶段 (pipeline/panel/runner.py 步骤 8d) 逐轨计算, 公式为 algo_cater{track} = dict_avg_tone{track} − llm_vote_tone{track}。两个被减项均为先在 article×bank verified 集上算得篇章级语调、再经银行-年度聚合而成的面板列: dict_avg_tone 来自 stage 22 词典情感, 对六部词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 的自归一化得分取综合均值; llm_vote_tone 来自 stage 21, 由 gpt54nano、gemini31、deepseekv4 三家逐篇投票取多数共识。差值仅在两个被减项在面板中同时存在时物化 (源码 if dc in panel.columns and lc in panel.columns 守卫), 否则该轨静默跳过而非产出伪零, 与同族 log_sent、Janis-Fadner、disag 对零覆盖行输出 NaN 的缺失语义一致。取值理论上近似落在 [−2, 2] 区间 (两个归一化 tone 各约 [−1, 1] 之差), 无量纲。同族并列另有 algo_cater_b (词典对 BERT)、逐词典 {d}_cater (单部词典对 LLM)、逐模型 cater_{m}/cater_{b} 等展开变体, 各自度量不同测度对之间的迎合缺口。

【文献定位】
本家族直接落地 Cao et al. (2023) "机器在听时如何说话"的迎合假说, 并借 Huang et al. (2023) FinBERT 一系工作确立"深层模型语义读数"作为对照基准的合法性——深层模型被视为更贴近语义实质、更难被表层词汇操纵的测度, 故以词典减深层模型定义迎合方向。词典法与机器学习法在情感判读上的系统性分歧本身是文本计量方法学的经典议题: van Atteveldt et al. (2021) 通过人工标注、众包、词典与机器学习的横向对照, 证明词典法与语义模型在效度上存在稳定落差, 为本差值构念提供了测量学根据; Ash & Hansen (2023) 综述经济学文本算法时亦强调不同文本表征方法所得测度不可简单互换, 其差异可携带独立信息。Khan et al. (2024) 在硅谷银行挤兑事件中比较多种机器与深度学习情感算法对银行股指的解释力, 佐证了算法读数差异在银行金融语境下具有实质经济后果, 支持将本迎合缺口作为解释变量或稳健性维度纳入面板。 晚近围绕词典法与生成式模型法的评测文献, 进一步收紧了本家族两端的效度前提。Bose、Hu、Liang 与 Yang (2025) 在同一批管理层文本上把 GPT、FinBERT 与情感词典三类方法头对头比较, 实证三者语调评分的系统性不一致, 为"词典减 LLM"之差非零并非噪声提供直接的测度学依据; 其语料为英文管理层沟通文本、词典侧为英文词表、模型侧为 GPT 与 FinBERT 而非本项目 gpt54nano、gemini31、deepseekv4 三家投票, 层级为文档级方法比较, 且系工作论文, 故只作分歧存在性的定性支撑。Kim、Spörer、Lee 与 Handschuh (2024) 在中央银行沟通语料上并排评测 VADER 词典与 FinBERT 族及 GPT-4、Llama-3-70B, 说明模型规模更大不必然与词典读数一致; 其语料为美联储 FOMC 英文文本, 词典臂为通用词典 VADER, 评价目标是对齐人工标签的分类准确率而非有向差值, 系会议论文。尤须强调的是, 减项 llm_vote_tone 不可被当作无误差参照: Kristensen-McLachlan、Canavan、Kárdos、Jacobsen 与 Aarøe (2025) 系统检验 LLM 作为文本标注器相对监督式模型与既有基线的可靠性, 结论是其表现随任务而异、并非一致优于传统方法; Gielens、Sowula 与 Leifeld (2026) 则以人工编码为基准评估 ChatGPT 对政策辩论文本的分类, 发现整体准确率虽高但 precision 与 recall 显著偏低且在论点类别间差异极大, 据此不建议在未经人工校验时直接采用其分类结果 (须澄清该文的对照臂仅为人工标注者, 既无情感词典亦无 BERT 或监督式模型对照, 故不得据以主张其比较了既有自动化内容分析方法, 亦不得用以锚定以 BERT 净语调为减项的姊妹家族)。两文任务均为英文社科文本标注、所用 LLM 家族亦与本项目三家不同, 结论以准确率或一致率呈现而非连续净语调差, 但其共同含义可迁移: 本家族的有向差值不应被单向解读为词典侧偏误。在 LLM 端测度构造的合法性上, Yang、Duan、Liu 与 Tam (2024) 提出并检验以 LLM 生成社科文本测度的效度、一致性与可复现性框架, 是"把 LLM 输出当作可复现连续测度"这一做法的方法学存在性证明; 该文为通用社科测度方法而非金融语调专用、非中文语料, 其可复现性依赖隐层表征提取路径, 与本项目固定 prompt v8、temperature=0 加缓存冻结的可复现路径不同, 且未设词典对照臂、未做银行—年聚合, 系工作论文。在词典端携带独立信号这一前提上, Lin 与 Liao (2024) 把情感词典信息注入提示词以改进金融维度情感分析, 其增益的成立前提即是词典法携带了生成式模型端未能捕捉的信号, 呼应本家族两侧信息不完全重合、故有向差携带信息而非纯噪声的构念依据; 但该文用途与本家族相反 (融合两侧以提升准确率, 而非保留分歧作迎合测度), 情感维度为 valence/arousal 连续维而非本项目 [-1,1] 归一净语调, 无 bank-year 层级, 且现有著录仅能证实"词典加提示词加金融维度情感", 无法证实其设有判别式模型对照臂, 故不得外推至以 BERT 为减项的姊妹家族。Wang、Wong 与 Zhang (2026) 在中国语境下并置两类媒体文本语调、以一方识别另一方的乐观偏差, 与本家族"相减取有向差并解读为系统性偏离"同型; 惟其差值轴为媒体来源之间的偏差, 而非同一文本上词典法与深层模型法之间的方法层偏差, 语料为国有媒体与社交媒体而非银行金融科技报道, 层级为公司或事件层, 无三家投票口径, 系工作论文。
## VAR: algo_cater_full

【变体差分】
本列为 full 轨迎合度, 即 dict_avg_tone_full 减 llm_vote_tone_full。full 轨文本 = 标题 prepend 后的标题加全文正文 (content_full), 是三轨中的 canonical 主轨。依据 2026-06-29 确立的 full-only 留篇门控口径, 一篇报道是否计入"银行金融科技报道"仅由 llm_verified_full == True 判定, 面板行宇宙 (n_articles 分母) 由 full 轨留篇集锚定; ctx、ss 两轨为 conditional-on-full 的从属测度轨, 其行宇宙是 full 留篇集的子集。因此本 full 列的两个被减项均在完整留篇宇宙上聚合, 分子分母口径最完整, 迎合缺口的统计功效最高, 是回归主轨与论文表格默认采用的迎合度测度。需要强调的是, 减法方向固定为词典减 LLM: 正值意味着关键词读法比语义模型读法更正面, 对应 Cao et al. (2023) 意义上"面向算法堆砌正面词"的迎合方向; 负值则提示报道字面偏中性或克制而语义实质更负面, 是反向背离。两个被减项分别源自 stage 22 的六词典综合均值与 stage 21 的三家 LLM 多数投票, 两套测度在生成机理上高度异质, 故其差值携带任一单侧测度都不含的表里落差信息。三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁将三轨混入同一 over-identified Hansen J 过度识别检验; 换言之, full 列作主结果时, ctx/ss 列只可作平行稳健性列独立进入各自回归, 不得与 full 列拼进同一组工具变量矩阵。

## VAR: algo_cater_ctx

【变体差分】
本列为 ctx 轨迎合度, 即 dict_avg_tone_ctx 减 llm_vote_tone_ctx。ctx 轨文本 = 标题加实体上下文窗口 (content_ctx), 只截取目标银行与金融科技实体邻近的语境片段而非全文, 意在过滤与银行金融科技主题无关的段落噪声, 使情感测度更聚焦于相关语境。相对 full canonical 轨, 本列的差异纯粹来自被减项所依据的文本轨道不同——聚合公式、词典集合、LLM 三家投票机制、减法方向完全一致, 仅底层篇章文本从全文收窄为实体窗口。作为 conditional-on-full 的从属测度轨, ctx 列的行宇宙是 full 留篇集的子集, 逐轨 per-track 列照常计算但留篇判定不重做——是否算作一篇银行金融科技报道仍只看 full 轨的 llm_verified_full。之所以并列这一轨, 是因为全文语调可能被与银行金科主题无关的段落 (如宏观时评、其它公司新闻) 稀释或污染, 而实体窗口聚焦后, 词典与语义模型对"真正相关语境"的读数分歧是否仍然存在, 是对迎合构念的一次收窄再检验。若 ctx 迎合度与 full 迎合度同号且量级相近, 说明主结果并非由无关语境的噪声驱动。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; ctx 迎合度作 full 主结果的首要稳健性对照轨独立进入回归, 绝不与 full、ss 列拼入同一组工具变量矩阵。

## VAR: algo_cater_ss

【变体差分】
本列为 ss 轨迎合度, 即 dict_avg_tone_ss 减 llm_vote_tone_ss。ss (same-sentence) 轨文本 = 标题加"银行与金融科技词同句共现 ±N 句窗"片段 (content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语境最严格的一轨, 只保留银行实体与金科词真正同句 (或紧邻句) 出现的文本, 判据比 ctx 的实体窗口更窄。回退语义镜像 ctx: 当某篇报道不存在银行与金科词的同句共现时, content_ss 优雅降级为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 整体降级。相对 full canonical, 本列差异同样纯粹来自文本轨道从全文收窄至同句共现窗, 聚合与减法口径不变。ss 属 conditional-on-full 从属测度轨, 行宇宙为 full 留篇集子集, 留篇判定不重做仍取 full 轨。ss 轨的意义在于把语境收紧到最保守的同句共现层级: 只有当银行与金融科技词真正落在同一句 (或紧邻一句) 时才计入语调计算, 从而最大限度排除"银行与金科在同一篇报道但实为两件不相关事"的伪共现。若词典对语义模型的迎合缺口在如此严苛的同句语境下依然稳健存在, 则该缺口更难被解释为语境错配的假象, 对迎合假说的支持最强。需注意 ss 存在回退降级, 大量无同句共现的报道会退回全文正文, 故 ss 与 ctx 在测量口径上并非严格互斥而是从属递进关系。ss、ctx、full 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; ss 迎合度作平行稳健性列独立进入各自回归, 不与 full、ctx 拼入同一组工具变量矩阵。

<!-- rendered-citations:begin -->
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Ash, E., & Hansen, S. (2023). Text algorithms in economics. Annual Review of Economics, 15(1), 659-688. https://doi.org/10.1146/annurev-economics-082222-074352
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bose, I., Hu, N., Liang, P., & Yang, X. (2025). Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment. SSRN No. 5153587 [Working Paper]. https://doi.org/10.2139/ssrn.5153587
Kim, W., Spörer, J., Lee, C. L., & Handschuh, S. (2024). Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER. Proceedings of the 5th ACM International Conference on AI in Finance, 626-633. https://doi.org/10.1145/3677052.3698675
Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L. (2025). Are chatbots reliable text annotators? Sometimes. PNAS Nexus, 4(4), pgaf069. https://doi.org/10.1093/pnasnexus/pgaf069
Gielens, E., Sowula, J., & Leifeld, P. (2026). Goodbye human annotators? Content analysis of social policy debates using ChatGPT. Journal of Social Policy, 55(2), 385-404. https://doi.org/10.1017/s0047279424000382
Yang, Y., Duan, H., Liu, J., & Tam, K. Y. (2024). LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research. SSRN No. 4961494 [Working Paper]. https://doi.org/10.2139/ssrn.4961494
Lin, W., & Liao, L.-C. (2024). Lexicon-based prompt for financial dimensional sentiment analysis. Expert Systems with Applications, 244, 122936. https://doi.org/10.1016/j.eswa.2023.122936
Wang, Y., Wong, T., & Zhang, T. (2026). Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China. SSRN Electronic Journal No. 6143029 [Working Paper]. https://doi.org/10.2139/ssrn.6143029
<!-- rendered-citations:end -->
