---
family_id: F143
columns:
- cater_gemini31_ctx
- cater_gemini31_full
- cater_gemini31_ss
unit: 情感倾向差值 (无量纲, 两个归一化 tone 之差, 取值近似 [-2, 2])
formula: "cater_gemini31{track} = dict_avg_tone{track} - gemini31_tone{track}"
producer: news_process/pipeline/panel/runner.py (步骤 8d, 算法迎合度全展开的逐模型分支); 标签 news_process/pipeline/panel/export.py
upstream:
- "22_tone_words.parquet (dict_avg_tone{track}: 六词典综合词典语调)"
- "21_tone_llms.parquet (gemini31_tone{track}: 单家 LLM gemini-3.1-flash-lite 篇章级语调)"
- 24_herd_decay.parquet (df_exploded, article×bank verified 集, 面板聚合前主输入)
citations:
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
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: "10.2139/ssrn.4961494"
  type: "wp"
  authors: "Yang, Y., Duan, H., Liu, J., & Tam, K. Y."
  year: 2024
  title: "LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research"
  venue: "SSRN"
  pages_or_artno: "4961494"
- doi: "10.1093/pnasnexus/pgaf069"
  type: "journal"
  authors: "Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L."
  year: 2025
  title: "Are chatbots reliable text annotators? Sometimes"
  venue: "PNAS Nexus"
  vol: "4"
  issue: "4"
  pages_or_artno: "pgaf069"
new_dois: []
---

## CORE

【构念与来源】
算法迎合度 (algorithmic catering) 度量的是同一批银行金融科技报道在两套异质情感测度下的系统性落差, 而本家族 cater_gemini31 是这一迎合缺口谱系里"以单家大语言模型 gemini-3.1-flash-lite 的逐篇语调作对照基准"的那一支。其一端是基于关键词计数的综合词典语调 dict_avg_tone (六部中文金融情感词典逐词匹配后自归一化的均值), 另一端不再是三家 LLM 多数投票的共识语调, 而是单独取 gemini31 一家模型对每篇报道判读所得的篇章级倾向 gemini31_tone。本家族取二者之差作面板列, 正值表示词典读法比 gemini31 语义读法更正面, 负值反之。其构念直觉源自 Cao et al. (2023) 的核心洞见: 当信息发布方知道自己的文本会被机器算法阅读并据以定价时, 会策略性地调整措辞以迎合算法读数, 使得表层关键词情感与语义实质情感产生可测量的背离; 这一背离本身即是"面向算法写作"这一行为的代理变量。对新闻语料而言, 报道措辞的关键词正面性与其经语义模型判读的实质正面性之间的缺口, 捕捉的是媒体文本中"堆砌正面词却语义空洞"或"字面中性而语义负面"一类的表里不一, 是研究媒体语气可信度、报道操纵与算法可读性策略的直接抓手。

【方法学与计算】
本列在面板总装阶段 (pipeline/panel/runner.py 步骤 8d, 算法迎合度全展开的逐模型分支) 逐轨计算, 公式为 cater_gemini31{track} = dict_avg_tone{track} − gemini31_tone{track}。两个被减项均为先在 article×bank verified 集上算得篇章级语调、再经银行-年度聚合而成的面板列: dict_avg_tone 来自 stage 22 词典情感, 对六部词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 的自归一化得分取综合均值; gemini31_tone 来自 stage 21, 是三家投票 LLM 中 gemini-3.1-flash-lite 一家 (经 yunwu 路由) 对每篇报道单独判读的逐篇倾向, 而非三家多数投票的共识。差值仅在两个被减项在面板中同时存在时物化 (源码以 if dc in panel.columns and lc in panel.columns 一类守卫护栏), 否则该轨静默跳过而非产出伪零, 与同族 algo_cater、log_sent、Janis-Fadner、disag 对零覆盖行输出 NaN 的缺失语义一致。取值理论上近似落在 [−2, 2] 区间 (两个归一化 tone 各约 [−1, 1] 之差), 无量纲。cater_gemini31 属"逐模型迎合缺口"这一并列展开: 同层另有 cater_gemini31 的两个兄弟 cater_gpt54nano、cater_deepseekv4 (换另一家 LLM 作对照), 以及以三家投票共识为对照的 algo_cater、以 BERT 为对照的 algo_cater_b/cater_{finbert_cn,fin_sent_zh,finbert2}、以及逐词典对 LLM 的 {d}_cater 展开。依 CLAUDE.md 的 LLM 三家互为稳健性铁律, gpt54nano、gemini31、deepseekv4 三家的逐模型子测度并排为互为稳健性、不分主次的跨厂商轨, 各自 just-identified 并排, 严禁把三家的迎合缺口混进同一 over-identified Hansen J 过度识别检验; 单家模型缺席只令其自身族降级, 不连坐其余两家 (per-model 独立降级, 非 co-primary 嵌入那种 both-or-neither)。

【文献定位】
本家族直接落地 Cao et al. (2023, Review of Financial Studies) "机器在听时如何说话"的迎合假说, 该文以美国上市公司披露文本为样本, 证明当机构投资者依赖机器下载与算法阅读时, 公司会系统性调整措辞以迎合机器读数, 从而在表层词汇情感与语义实质之间制造可测缺口——这一顶刊构念正是本迎合差值的方法学母题。Cao et al. (2023) 的关键贡献在于把"表层词汇情感与语义实质情感的背离"从一个测量噪声重新解释为一种可观测的策略行为信号: 当写作者预期文本会被算法阅读时, 会有意识地在关键词层面堆砌正面表述, 而这种堆砌未必被更贴近语义的深层读者所认同, 二者之差即为迎合行为的代理。将这一顶刊构念迁移到中文银行金融科技新闻语料, 本家族用综合词典语调代表表层关键词读法、用单家语义模型 gemini31 的逐篇判读代表语义实质读法, 取二者之差还原 Cao et al. (2023) 意义上的迎合缺口, 使媒体报道中"字面正面而语义空洞"或"字面中性而语义偏负"的表里不一得以量化。以单家语义模型 gemini31 的逐篇读数作对照基准的合法性, 借 Huang et al. (2023, Contemporary Accounting Research) FinBERT 一系工作确立: 该文系统论证经过金融文本微调的深层语言模型在情感判读上显著优于通用词典法, 深层模型被视为更贴近语义实质、更难被表层词汇操纵的测度, 故本迎合差值以词典减深层语义模型定义迎合方向具有测量学根据。同理, 词典法与语义模型在情感判读上的系统性分歧本身正是深层模型对照价值的来源: 若二者判读完全一致, 迎合缺口将恒为零而无信息量; 恰因二者对同一文本存在稳定而可解释的读数落差, 本差值方能携带"表层与语义背离程度"这一独立信号。之所以为每一家 LLM 单独保留一支迎合缺口, 而不只保留三家投票的 algo_cater, 是因为投票共识会掩盖单模型的厂商特异读数偏好; 保留 gemini31 单支, 可检验主结论是否被某一家模型的判读风格所驱动, 这正是跨厂商互为稳健性设计的用意所在——三家逐模型迎合缺口各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。以生成式大语言模型 gemini31 作语义读数基准的方法学正当性另有 de Kok (2025, Management Science) 的直接支撑: 该文系统给出在会计与金融文本分析中调用生成式 LLM 的规范流程与效度证据, 论证在受控 prompt 与温度设定下, 生成式模型的逐篇文本判读可作可复现、可审计的语义测度, 与本家族以冻结 prompt、temperature=0 逐篇调用 gemini31 得到 gemini31_tone 的做法口径一致, 从而为把单家生成式模型读数嵌入迎合缺口构造提供了操作层面的效度背书。 这一操作层面的效度背书另可由 Yang、Duan、Liu 与 Tam (2024) 提出的 LLM-Measure 框架加以补强: 该文系统检验用大语言模型生成社科文本测度的效度、一致性与可复现性, 是「把 LLM 逐篇输出当作可复现连续测度」这一做法的方法学存在性证明; 惟其为尚未经期刊同行评议的工作论文, 语料为通用社科文本而非中文金融报道, 其可复现性又依赖隐层表征提取路径, 与本项目冻结 prompt v8、temperature=0 加缓存固化的复现路径不同, 且原文只讨论 LLM 侧测度构造、未设词典对照臂, 故本家族仅援其一般性结论, 不移植其具体实现。与此同时, 把 gemini31 的逐篇读数视作语义实质的「无误差参照」并不成立: Kristensen-McLachlan、Canavan、Kárdos、Jacobsen 与 Aarøe (2025) 对聊天机器人作为文本标注器的可靠性作系统检验, 结论是其表现随任务而异、并非一致优于监督式模型与既有人工基线。该文任务为社科英文文本标注, 对照臂为监督式微调模型与人工标注, 既不含中文金融情感词典, 也未涉及 bank-year 聚合与迎合构念, 所用 LLM 家族亦与本项目三家不同, 故只能在效度前提层面援引; 但其含义对本列解读构成硬约束——cater_gemini31 的非零取值不得被单向读作词典侧偏误, 它同时承载 gemini31 一家判读自身的误差与厂商特异读数风格, 这也正是三家逐模型迎合缺口须各自 just-identified 并排、互为稳健性、不分主次, 而非择一家充当真值基准的根据。
## VAR: cater_gemini31_full

【变体差分】
本列为 full 轨、gemini31 单模型对照的迎合度, 即 dict_avg_tone_full 减 gemini31_tone_full。相对家族对照基准, 本列有两重差分: 其一是对照测度从三家 LLM 多数投票共识 (algo_cater 用的 llm_vote_tone) 换成单家 gemini-3.1-flash-lite 的逐篇读数 gemini31_tone, 属逐模型跨厂商稳健性轨; 其二是文本轨道取 full。full 轨文本 = 标题 prepend 后的标题加全文正文 (content_full), 是三轨中的 canonical 主轨。依据 2026-06-29 确立的 full-only 留篇门控口径, 一篇报道是否计入"银行金融科技报道"仅由 llm_verified_full == True 判定, 面板行宇宙 (n_articles 分母) 由 full 轨留篇集锚定; ctx、ss 两轨为 conditional-on-full 的从属测度轨。因此本 full 列的两个被减项均在完整留篇宇宙上聚合, 口径最完整, 迎合缺口的统计功效最高。减法方向固定为词典减 gemini31: 正值意味着关键词读法比 gemini31 语义读法更正面, 对应 Cao et al. (2023) 意义上"面向算法堆砌正面词"的迎合方向; 负值则提示报道字面偏中性而 gemini31 判读的语义实质更负面。gemini31 一家的判读风格未必与 gpt54nano、deepseekv4 一致, 故本列与 cater_gpt54nano_full、cater_deepseekv4_full 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家的迎合缺口混进同一 over-identified Hansen J; 同理三轨 (full/ctx/ss) 亦各自 just-identified 并排, 不得拼入同一组工具变量矩阵。gemini31 若在某年缺席只令本 gemini31 族降级, 不连坐其余两家。作为迎合缺口谱系里以单家模型为对照的一支, 本 full 列在实证上既可与 algo_cater_full (三家投票共识为对照) 对照以检验共识是否掩盖了单模型的厂商特异读数偏好, 也可与同层 BERT 对照的 cater_{finbert_cn,fin_sent_zh,finbert2}_full 并列以判别迎合缺口是否随语义模型家族更替而稳健, 从而把 Cao et al. (2023) 的迎合假说落到"换一个语义读者是否仍见同向缺口"这一最严格的稳健性问法上。

## VAR: cater_gemini31_ctx

【变体差分】
本列为 ctx 轨、gemini31 单模型对照的迎合度, 即 dict_avg_tone_ctx 减 gemini31_tone_ctx。相对 full canonical 轨, 本列差异纯粹来自被减项所依据的文本轨道不同——对照模型仍是 gemini-3.1-flash-lite 单家, 聚合公式、词典集合、减法方向完全一致, 仅底层篇章文本从全文收窄为实体上下文窗口。ctx 轨文本 = 标题加实体上下文窗口 (content_ctx), 只截取目标银行与金融科技实体邻近的语境片段而非全文, 意在过滤与银行金融科技主题无关的段落噪声, 使情感测度更聚焦于相关语境。作为 conditional-on-full 的从属测度轨, ctx 列的行宇宙是 full 留篇集的子集, 逐轨 per-track 列照常计算但留篇判定不重做——是否算作一篇银行金融科技报道仍只看 full 轨的 llm_verified_full。之所以并列这一轨, 是因为全文语调可能被与银行金科主题无关的段落 (如宏观时评、其它公司新闻) 稀释或污染, 而实体窗口聚焦后, 词典与 gemini31 语义模型对"真正相关语境"的读数分歧是否仍然存在, 是对迎合构念的一次收窄再检验。若 ctx 迎合度与 full 迎合度同号且量级相近, 说明主结果并非由无关语境的噪声驱动。本列与同轨的 cater_gpt54nano_ctx、cater_deepseekv4_ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家混入同一 over-identified Hansen J; ctx 迎合度作 full 主结果的首要稳健性对照轨独立进入回归, 绝不与 full、ss 列拼入同一组工具变量矩阵。

## VAR: cater_gemini31_ss

【变体差分】
本列为 ss 轨、gemini31 单模型对照的迎合度, 即 dict_avg_tone_ss 减 gemini31_tone_ss。ss (same-sentence) 轨文本 = 标题加"银行与金融科技词同句共现 ±N 句窗"片段 (content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语境最严格的一轨, 只保留银行实体与金科词真正同句 (或紧邻句) 出现的文本, 判据比 ctx 的实体窗口更窄。回退语义镜像 ctx: 当某篇报道不存在银行与金科词的同句共现时, content_ss 优雅降级为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 整体降级。相对 full canonical, 本列差异同样纯粹来自文本轨道从全文收窄至同句共现窗, 对照模型仍是 gemini-3.1-flash-lite 单家, 聚合与减法口径不变。ss 属 conditional-on-full 从属测度轨, 行宇宙为 full 留篇集子集, 留篇判定不重做仍取 full 轨。ss 轨的意义在于把语境收紧到最保守的同句共现层级: 只有当银行与金融科技词真正落在同一句 (或紧邻一句) 时才计入语调计算, 从而最大限度排除"银行与金科在同一篇报道但实为两件不相关事"的伪共现。若词典对 gemini31 语义模型的迎合缺口在如此严苛的同句语境下依然稳健存在, 则该缺口更难被解释为语境错配的假象, 对迎合假说的支持最强。需注意 ss 存在回退降级, 大量无同句共现的报道会退回全文正文, 故 ss 与 ctx 在测量口径上并非严格互斥而是从属递进关系。本列与同轨的 cater_gpt54nano_ss、cater_deepseekv4_ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家的迎合缺口混入同一 over-identified Hansen J; ss、ctx、full 三轨同样各自 just-identified 并排, ss 迎合度作平行稳健性列独立进入各自回归, 不与 full、ctx 拼入同一组工具变量矩阵。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Yang, Y., Duan, H., Liu, J., & Tam, K. Y. (2024). LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research. SSRN No. 4961494 [Working Paper]. https://doi.org/10.2139/ssrn.4961494
Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L. (2025). Are chatbots reliable text annotators? Sometimes. PNAS Nexus, 4(4), pgaf069. https://doi.org/10.1093/pnasnexus/pgaf069
<!-- rendered-citations:end -->
