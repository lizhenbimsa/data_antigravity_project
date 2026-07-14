---
family_id: F424
columns:
- loughran_score_hw_sum_ctx
- loughran_score_hw_sum_full
- loughran_score_hw_sum_ss
unit: 无量纲 (羊群加权情感得分逐篇合计; 聚合分子分量, 非归一化到 [-1,1] 的语调值)
formula: "loughran_score{track} = Σ(final_score)/Σ|final_score| ∈ [-1,1] (Loughran-McDonald 2011 中文主译本词典查得极性 + 否定/程度/转折全语言学规则); herd_weight{track} = 1/(1 + n_similar_articles{track}); loughran_score_hw{track} = loughran_score{track} × herd_weight{track}; loughran_score_hw_sum{track} = Σ_{article ∈ bank-year} loughran_score_hw{track}"
producer: news_process/pipeline/panel/runner.py (步骤3d 逐篇羊群加权) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (bank-year sum)
upstream:
- 22_tone_words.parquet (loughran_score_full / _ctx / _ss)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss)
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个银行-年度层面的中间聚合量: 以 Loughran-McDonald (2011) 中文主译本情感词典逐篇算得的报道情感得分, 先按"羊群衰减"权重逐篇缩放, 再在同一银行同一年度内对所有报道求和, 得到 loughran_score_hw_sum。名称三段各有明确所指: loughran 指所用词典是 Loughran 与 McDonald 面向英文 10-K 文本构建、后经领域专家译制并本土化扩充的中文主译本 (config/tone_dicts.json 中登记为 loughran_mcdonald_zh_2026, 列前缀别名 loughran), 含正面词 1,295 个、负面词 3,729 个, 另含不确定性、诉讼、强势、弱势与约束性等 5 类非极性词类 (本家族仅消费极性正负两类, 非极性词类供其他家族的构念区分测度); score 指底层文章级测度是该词典的归一化情感极性得分, 取值区间 [-1, +1]; hw (herd-weighted, 羊群加权) 指每篇报道在进入求和前先乘以一个反映其信息独立性的降权乘子; sum 指银行-年度层内对经加权的逐篇得分作合计而非取均值。因此本量不是一个落在 [-1, +1] 的语调值, 而是加权求和的分子分量: 它与配套的羊群权重合计 sum_herd_weight 相除, 才还原为可比的羊群加权语调 loughran_tone_hw。将分子单列落盘, 目的是让下游可在 Stata 侧显式复算比值、审计分子分母同域, 并支持对分母口径 (是否用有效掩码分母) 的敏感性检验。词典加载时对该词典 positive∩negative 跨类重叠词 (原始 61 词, 经 2026-06-24 用户决策"两侧保留判断"消歧, 38 词已归单侧、余 23 词不可约简而保留) 按用户决策"保留而非剔除": 该 23 词同时计入 pos/neg 两侧计数, 对个体 loughran_score 的净语调拉向中性而不武断选边; 这不影响 6 词典固定 union 词典的极性 margin (重叠词以 +1/-1 平衡双票喂入 union, 逐位守恒)。

【方法学与计算】
计算链路分三段。第一段在 stage 22 词典法内: 对每篇报道分词后, 在 Loughran-McDonald 中文主译本词典上做逐词匹配, 命中情感词依次施加三条语言学规则 —— 否定词在其后固定窗口内翻转极性、程度副词按倍率缩放幅值、转折词在从句作用域内按转折权重放大后半句, 遇句末标点重置规则状态; 由此得到每个情感词的 final_score, 文章级得分归一化为 Σ(final_score)/Σ|final_score|, 落在 [-1, +1], 正值偏正面、负值偏负面。此归一化口径与仅取原始词典极性计数的 msent / pos_count / neg_count 计数口径互为稳健性, 二者刻意不混用; pos_ratio / neg_ratio / msent_score 等聚合测度另按 6 词典固定 union 词典计数 (build_union_dictionary, 兑现固定词表构念, 与逐词典的 loughran_score 系口径不同, 亦不混用)。第二段在 stage 24 羊群衰减处理: 对同一目标银行的报道按发布年度截断, 用 TF-IDF 余弦相似度统计每篇报道在同年早前存在多少篇高度相似 (疑似转抄、回声式跟风) 的报道, 记为 n_similar_articles, 再令 herd_weight = 1/(1 + n_similar_articles); 转抄越多则权重越低, 越接近独立首发则权重越接近 1。第三段在面板聚合 (runner 步骤 3d 逐篇相乘, encode 的 build_aggregation_dict 求和): 文章级 loughran_score 乘以同轨 herd_weight 得到 loughran_score_hw, 再在银行-年度分组内求和得到本列。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列。

【文献定位】
本测度的方法学谱系直接锚定 Loughran 与 McDonald 一系顶刊工作。原创词典出自 Loughran & McDonald (2011, The Journal of Finance) —— 该文发现基于通用 (非金融领域) 词典 (如 Harvard Psychosociological Dictionary) 判定的"负面词"中, 相当比例在 10-K 文本语境下并非真正负面 (即标题"When is a liability not a liability?" 所指的领域特异性偏误), 由此构建面向会计与金融文本的领域专用英文情感词典, 后经领域专家译制并本土化扩充为中文主译本供本管道使用。该词典法路线在 Loughran & McDonald (2016, Journal of Accounting Research) 的综述中被系统化为会计与金融文本分析的标准工具, 并在 Loughran & McDonald (2020, Annual Review of Financial Economics) 中进一步梳理词典法在金融文本挖掘中的适用边界与局限。词典的领域特异性价值在中文语境下由 Du et al. (2022, Review of Finance) 顶刊工作进一步确证 —— 该文指出语言与领域特异性对中文金融情感度量至关重要, 通用词典或简单直译词典在中文语料上存在系统性偏误, 这正是本管道并列使用 Loughran 中文主译本与其他五部中文原生金融情感词典 (而非唯独依赖直译词典) 的方法学依据。逐词施加否定、程度、转折规则并作从句级作用域重置, 遵循 Taboada et al. (2011) 确立的词典法情感分析范式。而将词典法结果单独成轨、与机器学习及大模型法并置互证, 呼应 Frankel, Jennings 与 Lee (2022) 关于披露情感的机器学习法与词典法互为稳健性的先例。需强调本家族的六部词典 (loughran 中文主译本与 jiang_2021、yao_2021、bian_2021、du_2022、you_2018) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同词典或不同聚合权重混进同一 over-identified Hansen J 检验。

## VAR: loughran_score_hw_sum_full

【变体差分】
本列是家族三轨中的 full (全文) 轨。文本口径为标题 prepend 后的报道全文正文: stage 14 的 ctx_materializer 把标题前置到正文, 情感词典在完整标题加正文上匹配 Loughran-McDonald 中文主译本词典并施加否定/程度/转折全规则, 算得文章级 loughran_score_full。羊群权重取 full 轨的 herd_weight_full, 即在全文 TF-IDF 相似度空间上统计的同年转抄计数所得的 1/(1 + n_similar_articles_full); 因此本轨的降权判据与情感判据同在全文空间, 二者口径一致。逐篇 loughran_score_full 乘 herd_weight_full 得 loughran_score_hw_full, 银行-年度内求和即本列。在三轨中 full 轨承担留篇门控职责 (full-only 口径, 2026-06-29): 某报道是否计入银行-年度报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 故 full 轨行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。作为羊群加权 (hw) 聚合方案, 本列与同家族的简单求和 (loughran_score_sum)、以及 idf 加权得分聚合 (loughran_idf_tone_sum) 属彼此正交的聚合权重方案: hw 按信息独立性降权转抄式跟风报道, idf 按词汇稀有度缩放幅值, 二者刻画不同的稳健性维度; 各聚合权重方案同样各自 just-identified 并排、互为稳健性、不分主次, 严禁与不同权重方案混进同一 over-identified Hansen J。full 轨在全文空间上算得的相似度计数通常最密, 因转抄回声在整篇层面比在实体窗或同句片段层面更易被 TF-IDF 捕获, 故 full 轨的羊群降权幅度往往强于另两轨, 这也是把三轨分列而非合并的实证理由。本列作为羊群加权聚合分子, 与 sum_herd_weight_full 相除还原为可比语调 loughran_tone_hw_full, 供 Stata 侧显式复算与分母口径敏感性检验。

## VAR: loughran_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx: 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关的段落, 再在此片段上用 Loughran-McDonald 中文主译本词典逐词匹配并施加否定/程度/转折全规则, 算得文章级 loughran_score_ctx。羊群权重取 ctx 轨的 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不再走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权; 因此本轨情感判据与降权判据同在实体窗空间, 与 full 轨在全文空间的口径系统性不同。逐篇 loughran_score_ctx 乘 herd_weight_ctx 后在银行-年度内求和即本列。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。相对 full 轨, ctx 轨把情感信号收窄到实体近旁, 削弱远端无关文本对语调的稀释, 是 full 轨的规格稳健性并排轨。因情感与降权判据都在实体窗内, ctx 轨在语义上更贴近"关于该银行的这段话是正面还是负面、且是否为跟风转抄"这一构念, 但代价是可用文本更短、方差更高。需强调本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用: 实体窗按目标实体邻近范围裁剪, 与同句判据的句法边界不同。ctx 轨不承担留篇门控, 亦不因文本收窄而改变留篇集, 只在 full 留篇子集上按自身列照算。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ctx 相除还原 loughran_tone_hw_ctx, 作为 full 轨语调的首要稳健性对照。

## VAR: loughran_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中判据最严。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss: 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本, 再在此片段上算 Loughran-McDonald 中文主译本词典得分 loughran_score_ss。回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 轨的回退机制同构。羊群权重取 herd_weight_ss, 在 ss 超级文档上做 TF-IDF 相似度所得; 当 ss 文本大面积回退到全文时, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷 (回退率越高、真三轨独立性越弱, 日志会告知)。逐篇 loughran_score_ss 乘 herd_weight_ss 后银行-年度求和即本列。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。在开发期 T=2 小样本上, ss 轨因同句共现稀疏可能出现零方差或大面积回退, 属预期退化, 生产期 T=18 恢复正常。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及时的情感倾向", 因而对识别银行金科关联报道的语调最具针对性, 但也最易受回退稀释: 一旦回退, 该篇实际用的是全文文本与全文相似度, ss 轨对 full 轨的独立性随回退率上升而衰减, 故解读 ss 轨时须与回退率一并披露。ss 轨的严格同句判据 (银行与金科同句共现) 与 ctx 轨的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ss 相除还原 loughran_tone_hw_ss, 作为三轨中判据最严的稳健性并排轨。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
