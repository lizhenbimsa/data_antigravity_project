---
family_id: F144
columns:
- cater_gpt54nano_ctx
- cater_gpt54nano_full
- cater_gpt54nano_ss
unit: 无量纲情感差值 (词典语调减单模型语调, 取值域随两侧归一化语调而定, 正值=词典更正面)
formula: "cater_gpt54nano{track} = dict_avg_tone{track} − gpt54nano_tone{track}; track ∈ {_full, _ctx, _ss}"
producer: "news_process/pipeline/panel/runner.py (步骤 8d 算法迎合度全展开, C 组: 综合词典 vs 单深层模型)"
upstream:
- 21_tone_llms.parquet (gpt54nano_tone{track})
- 22_tone_words.parquet (dict_avg_tone{track})
- 24_herd_decay.parquet (df_exploded, article×bank verified 集)
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
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
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.2139/ssrn.5153587"
  type: "wp"
  authors: "Bose, I., Hu, N., Liang, P., & Yang, X."
  year: 2025
  title: "Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment"
  venue: "SSRN"
  pages_or_artno: "5153587"
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
本家族刻画的构念是"算法迎合度"(algorithmic catering) 中以 gpt54nano 大模型为深层参照的那一支: 同一篇 (或同一银行-年度聚合后的) 银行金融科技报道, 用两把口径迥异的量尺读它的情感语调, 一把是基于人工构造词表逐词计分的综合词典 (dict_avg_tone), 另一把是让 gpt54nano 大语言模型整体阅读全文后给出的语调判断 (gpt54nano_tone); 二者相减得到的差值即为迎合度。构念的经济学出发点来自这样一个观察: 当报道的撰写方或转述方意识到下游读者不再只是人类, 而越来越多是靠词典、关键词计分等浅层规则来抓取情感信号的机器时, 撰写方存在策略性地堆砌"词典友好"的正面词汇、以在浅层量尺上显得更乐观的动机, 而这种堆砌未必能骗过语义理解更深的大模型。因此当词典读数系统性地高于大模型读数 (差值为正) 时, 文本层面就残留了一种"对着机器说话"的语用痕迹。这一构念的原始理论与实证锚点是 Cao et al. (2023) 关于"机器在听时如何说话"的研究, 他们证明当机器下载与算法阅读增加后, 企业信息披露的语言会朝着让算法读出更正面情绪的方向系统性漂移; 本家族把这一思想从企业自我披露迁移到第三方银行报道语境, 用词典与大模型两把量尺之差作为其可观测代理。

【方法学与计算】
计算落在面板总装阶段 (pipeline/panel/runner.py 步骤 8d), 属纯后处理的列相减, 不新调任何模型: 分被减数 dict_avg_tone{track} 来自 stage 22 的多词典综合归一化语调, 减数 gpt54nano_tone{track} 来自 stage 21 三家投票中 gpt54nano 单模型自身的归一化语调, 两侧均已在各自阶段完成 [-1, 1] 量纲的归一化, 故差值无量纲、正值意味着词典比 gpt54nano 更正面、负值反之。此差值在语义上就是 Frankel et al. (2022) 所讨论的"机器学习读数与词典读数之差"的一个具体实例: 他们指出词典法与模型法在同一文本上的分歧本身携带信息, 分歧的方向与幅度可用于识别披露的策略性成分。本家族严格是"综合词典 vs 单一深层模型"这一 C 组切面: 与之并列的还有综合词典对综合 LLM 投票 (algo_cater)、综合词典对单一 BERT 模型 (cater_finbert 系) 等切面, 它们各自捕捉不同的机器参照, 互为稳健性、不分主次, 各自 just-identified 并排进入回归, 禁混进同一 over-identified 的 Hansen J 过度识别检验。三条文本轨 (full/ctx/ss) 同理: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技报道宇宙, 只看 full 轨的 gpt54nano 及投票是否 verified; ctx/ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技词的同句共现时, ss 文本回退为全文正文并置 fallback 标记, 与 ctx 的回退口径一致。

【文献定位】
测度谱系上, 本家族一端连着以 Loughran & McDonald (2011) 为代表的金融文本词典传统——他们证明通用情感词表在金融语境会系统性误判、须用领域专用词表, 这正是 dict_avg_tone 一侧多词典综合的动因; 在中文金融语境, Du et al. (2022) 进一步论证语言与领域双重专用性对情感词典效度的决定性, 是本项目中文词典构造的直接依据。另一端连着大模型文本理解的新范式: Huang et al. (2023) 的 FinBERT 与 de Kok (2025) 对生成式大模型用于文本分析的系统评估, 共同界定了 gpt54nano 一侧"深层语义读数"的方法学地位与其相对词典的增量。Bochkay et al. (2023) 对会计文本分析下一步走向的综述, 把"词典 vs 机器学习读数之差"明确列为一类值得挖掘的信息源, 为本家族把差值本身当作构念而非噪声提供了方法论正当性。综合而言, cater_gpt54nano 家族坐落在"文本情感测度分歧即信息"这一新兴文献脉络上, 以 gpt54nano 为深层锚, 度量银行金融科技报道中词典友好型语言相对深层语义判断的偏离。 晚近的头对头比较为这一定位提供了更直接的测度学依据: Bose、Hu、Liang 与 Yang (2025) 在同一批管理层文本上把 GPT、FinBERT 与情感词典三类方法并排评估, 报告三者对同一段文本的语调判读存在系统性不一致, 从而实证了本家族差值的非零成分主要不是抽样噪声, 而是两把量尺读法差异的结构性产物; 惟该文语料为英文管理层沟通文本、词典侧为英文词表、模型侧为通用 GPT 与 FinBERT (非本项目的三家投票 LLM 与三个中文 BERT), 分析停在文档级方法比较而未做 bank-year 聚合, 亦未把差值本身构造为指标, 且属尚未经同行评议的工作论文, 故只支撑「两端读数会稳定分歧」这一前提, 不支撑本项目对差值方向的具体解释。gpt54nano 一侧作为可复现连续测度的构造合法性另由 Yang、Duan、Liu 与 Tam (2024) 的 LLM-Measure 框架背书, 该文提出并检验用大模型生成社科文本测度的效度、一致性与可复现性; 其为通用社科方法而非金融语调专用, 可复现性依赖隐层表征提取路径, 与本项目冻结 prompt、temperature=0、缓存固化的路径不同, 且未设词典对照臂, 故援引仅及于 LLM 侧测度构造本身, 属工作论文。反向的约束来自 Kristensen-McLachlan、Canavan、Kárdos、Jacobsen 与 Aarøe (2025): 该文系统检验大模型作为文本标注器的可靠性, 结论是其表现随任务而异、并非一致优于监督式模型与人工基线; 其任务为社科英文标注、对照臂不含中文金融词典, 与本家族口径相距甚远, 但足以否证「gpt54nano 读数即语义真值」这一隐含前提: cater_gpt54nano 的正负号只应读作两把量尺的相对位置, 不能单向归因于词典侧偏误, 这也正是三家 LLM 的逐模型迎合缺口须各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 的根据。
## VAR: cater_gpt54nano_full

【变体差分】
本列是 full 轨切面: 被减数与减数均取 full 轨读数, 即 cater_gpt54nano_full = dict_avg_tone_full − gpt54nano_tone_full。full 轨的文本口径是"标题 prepend + 全文正文", 即把报道标题拼接到正文之前后整体送入词典计分与 gpt54nano 阅读, 覆盖报道的完整语篇。在三轨中, full 轨具有特殊地位: 留篇门控是 full-only (2026-06-29), 一篇报道能否计入银行金融科技报道宇宙只由 full 轨的 gpt54nano verified 状态决定, 因此本列的行覆盖即为该家族的 canonical 覆盖基准, ctx 与 ss 两列的行宇宙都是本列行宇宙的子集。相对家族内另两条轨, 本列的差异纯粹在文本范围: 它读整篇报道, 不做实体窗口或同句裁剪, 因而语料信息量最大、也最易受与银行金融科技主题无关的段落稀释。本列与 cater_gpt54nano_ctx、cater_gpt54nano_ss 三者互为稳健性、不分主次, 各自 just-identified 并排进入回归, 禁混进同一 over-identified 的 Hansen J。与相邻的 algo_cater_full (综合词典对综合 LLM 投票)、cater_gemini31_full、cater_deepseekv4_full 等列的区别在于减数所用的深层模型: 本列锁定 gpt54nano 单模型, 是三家 LLM per-model 稳健性并排中的一支, 各家各自 just-identified、禁混同一 over-identified Hansen J。需要强调的是, gpt54nano 属情感投票三家 LLM 之一 (与 gemini31、deepseekv4 并列), 与 co-primary 嵌入模型、与 BERT 三模型均无关, 换嵌入模型或换 BERT 权重时本列零误改。作为 full 轨的 canonical 覆盖基准, 本列在解释迎合度回归系数时须优先, ctx 与 ss 两列则用于验证结论不被文本裁剪口径驱动: 若三轨系数同号同量级, 说明词典相对 gpt54nano 的迎合偏离不是某一文本范围的伪影, 而是稳健地存在于银行金融科技报道的语言中。

## VAR: cater_gpt54nano_ctx

【变体差分】
本列是 ctx 轨切面: cater_gpt54nano_ctx = dict_avg_tone_ctx − gpt54nano_tone_ctx, 两侧均取 ctx 轨读数。ctx 轨的文本口径是"标题 prepend + 实体上下文窗口", 即只保留报道中银行等目标实体附近的上下文窗口 (由 config 的 context_window 控制) 再送入词典计分与 gpt54nano 阅读, 相对 full 轨剔除了远离实体的段落, 意在把语调判断聚焦到与目标银行直接相关的语句上、压低无关内容的稀释。因而本列与 full 列的差异不在计算式而在文本范围: 同一篇报道, 若正面词汇集中在与银行无关的段落, 本列会读出比 full 列更中性或不同方向的迎合度。留篇门控是 full-only, 本列是 conditional-on-full 的测度与稳健性轨, 行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。本列与 cater_gpt54nano_full、cater_gpt54nano_ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified 的 Hansen J。与相邻 cater_gemini31_ctx、cater_deepseekv4_ctx 的区别同样仅在减数所用深层模型锁定 gpt54nano; 与 algo_cater_ctx 的区别在于本列减数是单一 gpt54nano 模型而非三家投票共识, 二者为不同参照下的并排稳健切面。在解释上, 本列相对 full 列的价值在于剥离主题稀释: 当 full 列因无关正面段落而读出较大迎合度、而本列在实体窗口内读出的迎合度显著收窄时, 说明该迎合痕迹并非发生在银行相关语句本身, 而是报道其他部分的语言噪声; 反之若本列与 full 列迎合度相当, 则迎合确实落在与目标银行直接相关的表述上。因此本列既是稳健性轨, 也是迎合信号定位到实体语境的诊断轨。

## VAR: cater_gpt54nano_ss

【变体差分】
本列是 ss 轨切面: cater_gpt54nano_ss = dict_avg_tone_ss − gpt54nano_tone_ss, 两侧均取 ss 轨读数。ss 轨的文本口径最严: "标题 prepend + 银行与金融科技同句共现的 ±N 句窗口" (窗半径由 config 的 ss_sentence_radius 控制, 默认 1), 即只保留银行与金融科技词真正落在同一句 (或近邻句窗) 的语句, 把语调判断进一步收窄到银行金融科技交汇的核心语境。本列与 ctx 列的差异在裁剪判据: ctx 依实体上下文窗口, ss 依银行与金融科技的同句共现, 判据更严、保留文本更少。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技的同句共现时, ss 文本优雅回退为全文正文并置 fallback 标记, 与该篇共享 n_articles 分母, 因此本列在无同句共现的报道上会退化为等同 full 语料的读数。留篇门控是 full-only, 本列同为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集。本列与 cater_gpt54nano_full、cater_gpt54nano_ctx 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified 的 Hansen J; 与 cater_gemini31_ss、cater_deepseekv4_ss 的区别仅在减数深层模型锁定 gpt54nano, 属三家 LLM per-model 并排稳健的一支。本列的解释重心是最严语境下的迎合度: 当词典与 gpt54nano 只读银行与金融科技同句交汇的语句时, 若仍读出正向迎合偏离, 说明词典友好型语言恰好堆砌在这一核心语境, 迎合信号最不易被稀释、构念效度最高; 但须注意在无同句共现而回退全文的报道上, 本列读数等同 full 语料, 解释时须结合 ss_is_fallback 标记区分真同句语境与回退语境, 避免把回退样本的读数误当作核心语境证据。三轨系数的一致性是判断迎合稳健性的最终依据。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next? Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Bose, I., Hu, N., Liang, P., & Yang, X. (2025). Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment. SSRN No. 5153587 [Working Paper]. https://doi.org/10.2139/ssrn.5153587
Yang, Y., Duan, H., Liu, J., & Tam, K. Y. (2024). LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research. SSRN No. 4961494 [Working Paper]. https://doi.org/10.2139/ssrn.4961494
Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L. (2025). Are chatbots reliable text annotators? Sometimes. PNAS Nexus, 4(4), pgaf069. https://doi.org/10.1093/pnasnexus/pgaf069
<!-- rendered-citations:end -->
