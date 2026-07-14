---
family_id: F649
columns:
- you_2018_score_hw_sum_ctx
- you_2018_score_hw_sum_full
- you_2018_score_hw_sum_ss
unit: 无量纲 (羊群加权情感得分逐篇合计; 聚合分子分量, 非归一化到 [-1,1] 的语调值)
formula: "you_2018_score{track} = Σ(final_score)/Σ|final_score| ∈ [-1,1] (You et al. 2018 词典查得极性 + 否定/程度/转折全语言学规则); herd_weight{track} = 1/(1 + n_similar_articles{track}); you_2018_score_hw{track} = you_2018_score{track} × herd_weight{track}; you_2018_score_hw_sum{track} = Σ_{article ∈ bank-year} you_2018_score_hw{track}"
producer: news_process/pipeline/panel/runner.py (步骤3d 逐篇羊群加权) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (bank-year sum) ; news_process/pipeline/sentiment/tone_words.py (词典法文章级 score)
upstream:
- 22_tone_words.parquet (you_2018_score_full / _ctx / _ss)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: "10.1111/jfir.70039"
  type: journal
  authors: "Yang, N., Fernandez-Perez, A., & Indriawan, I."
  year: 2026
  title: "Social media sentiment, investor herding and informational efficiency"
  venue: "Journal of Financial Research"
- doi: "10.1016/j.iref.2024.01.067"
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  venue: "International Review of Economics & Finance"
  type: "journal"
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  venue: "Expert Systems with Applications"
  type: "journal"
new_dois:
  - "10.1111/jfir.70039"
  - "10.1016/j.iref.2024.01.067"
  - "10.1016/j.eswa.2024.125739"
---

## CORE

【构念与来源】
本家族刻画一个银行-年度层面的中间聚合量: 以 You, Zhang 与 Zhang (2018) 面向中国资本市场构建的中文金融情感词典逐篇算得的报道情感得分, 先按"羊群衰减"权重逐篇缩放, 再在同一银行同一年度内对所有报道求和, 得到 you_2018_score_hw_sum。名称三段各有明确所指: you_2018 指所用词典是 You, Zhang 与 Zhang (2018, RFS)「Who captures the power of the pen?」一文构建的中文金融情感词典 (含 positive 1,425 词、negative 1,583 词, 另有 definite 388 词、ambiguous 178 词两个非情感极性子集, 后者仅在 clarity 族测度中启用, 与本家族无关); score 指底层文章级测度是该词典的归一化情感极性得分, 取值区间 [-1, +1]; hw (herd-weighted, 羊群加权) 指每篇报道在进入求和前先乘以一个反映其信息独立性的降权乘子; sum 指银行-年度层内对经加权的逐篇得分作合计而非取均值。因此本量不是一个落在 [-1, +1] 的语调值, 而是加权求和的分子分量: 它与配套的羊群权重合计 sum_herd_weight 相除, 才还原为可比的羊群加权语调 you_2018_tone_hw。将分子单列落盘, 目的是让下游可在 Stata 侧显式复算比值、审计分子分母同域, 并支持对分母口径 (是否用有效掩码分母) 的敏感性检验。You et al. (2018) 的原始研究关切是财经记者笔下的措辞如何影响股价走势 (即"谁在操纵笔杆子"), 该词典正是为刻画中文财经文本中媒体措辞的正负面倾向而构建, 与本管道用其度量银行-金融科技报道情感的构念高度贴合。

【方法学与计算】
计算链路分三段。第一段在 stage 22 词典法内: 对每篇报道分词后, 在 You et al. (2018) 词典上做逐词匹配, 命中情感词依次施加三条语言学规则 —— 否定词在其后固定窗口内翻转极性、程度副词按倍率缩放幅值、转折词在从句作用域内按转折权重放大后半句, 遇句末标点重置规则状态; 由此得到每个情感词的 final_score, 文章级得分归一化为 Σ(final_score)/Σ|final_score|, 落在 [-1, +1], 正值偏正面、负值偏负面。此归一化口径与仅取原始词典极性计数的 msent 计数口径互为稳健性, 二者刻意不混用。词典消歧口径: you_2018 词典 positive∩negative 跨类重叠 5 词, 按 2026-06-24 用户决策「保留并两侧计数」处理 —— 重叠词同时计入 pos 与 neg (对该词典个体 you_2018_score 净语调拉向中性、不武断选边), 运行时词条数为原始 |pos∪neg|, 而聚合测度所用的固定 union 词典因重叠词以 (+1,−1) 平衡双票喂入而极性 margin 守恒、逐位不变。第二段在 stage 24 羊群衰减处理: 对同一目标银行的报道按发布年度截断, 用 TF-IDF 余弦相似度统计每篇报道在同年早前存在多少篇高度相似 (疑似转抄、回声式跟风) 的报道, 记为 n_similar_articles, 再令 herd_weight = 1/(1 + n_similar_articles); 转抄越多则权重越低, 越接近独立首发则权重越接近 1。第三段在面板聚合 (runner 步骤 3d 逐篇相乘, encode 的 build_aggregation_dict 求和): 文章级 you_2018_score 乘以同轨 herd_weight 得到 you_2018_score_hw, 再在银行-年度分组内求和得到本列。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列。

【文献定位】
本测度的方法学谱系由数支文献锚定。词典本身取 You, Zhang 与 Zhang (2018, The Review of Financial Studies) —— 该顶刊文献构建了面向中国资本市场的中文财经文本情感词典, 证明媒体笔调 (media tone) 对公司层面结果具有独立于事实内容的预测力; 本家族沿用其词典完成对银行-金融科技报道文本的情感极性打分, 是该文方法学在银行业金融科技情境下的直接应用。词典的领域特异性价值进一步由 Du et al. (2022, Review of Finance) 确证 —— 该文指出语言与领域特异性对中文金融情感度量至关重要, 通用词典 (如直译版 Loughran-McDonald) 在中文语料上系统性偏误, 这正是本管道并置多部中文金融专用词典 (you_2018、bian_2021、du_2022 等) 而非仅依赖直译词典的依据。逐词施加否定、程度、转折规则并作从句级作用域重置, 遵循 Taboada et al. (2011) 确立的词典法情感分析范式。而将词典法结果单独成轨、与机器学习及大模型法并置互证, 呼应 Frankel, Jennings 与 Lee (2022) 关于披露情感的机器学习法与词典法互为稳健性的先例, 以及 van Atteveldt, van der Velden 与 Boukes (2021) 对人工标注、词典法与机器学习法效度的横向比较; Barbaglia et al. (2025) 亦重申词典法在经济文本上的可解释与可复现优势。需强调本家族的六部词典 (you_2018 与 jiang_2021、yao_2021、bian_2021、du_2022、loughran) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同词典或不同聚合权重混进同一 over-identified Hansen J 检验。此外, Yang, Fernandez-Perez 与 Indriawan (2026, Journal of Financial Research) 证明社媒情感通过投资者羊群行为影响信息效率, 为本家族在情感得分之外叠加羊群衰减权重 (herd_weight) 这一构造思路提供了羊群行为与情感测度交互影响资本市场结果的实证支撑。Fang, Wang, Wang 与 Yuan (2024, International Review of Economics & Finance) 构建银行层面媒体情感指数, 证明负面媒体情感通过削弱存款稳定性推高中国银行系统性风险, 为本家族用词典法情感测度银行相关报道语调的构念效度提供最新中国银行业实证支撑。Ma, Zhang 与 Zhang (2025, Expert Systems with Applications) 面向中国投资者构建细粒度中文情感词典并验证其对市场异动的预测力, 与 You et al. (2018) 词典法路线同属中文金融文本情感词典构建谱系, 印证领域专用词典相较通用/直译词典的必要性。

## VAR: you_2018_score_hw_sum_full

【变体差分】
本列是家族三轨中的 full (全文) 轨。文本口径为标题 prepend 后的报道全文正文: stage 14 的 ctx_materializer 把标题前置到正文, 情感词典在完整标题加正文上匹配 You et al. (2018) 词典并施加否定/程度/转折全规则, 算得文章级 you_2018_score_full。羊群权重取 full 轨的 herd_weight_full, 即在全文 TF-IDF 相似度空间上统计的同年转抄计数所得的 1/(1 + n_similar_articles_full); 因此本轨的降权判据与情感判据同在全文空间, 二者口径一致。逐篇 you_2018_score_full 乘 herd_weight_full 得 you_2018_score_hw_full, 银行-年度内求和即本列。在三轨中 full 轨承担留篇门控职责 (full-only 口径, 2026-06-29): 某报道是否计入银行-年度报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 故 full 轨行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。作为羊群加权 (hw) 聚合方案, 本列与同家族的简单均值聚合、以及 idf 加权得分聚合属彼此正交的聚合权重方案: hw 按信息独立性降权转抄式跟风报道, idf 按词汇稀有度缩放幅值, 二者刻画不同的稳健性维度; 各聚合权重方案同样各自 just-identified 并排、互为稳健性、不分主次, 严禁与不同权重方案混进同一 over-identified Hansen J。full 轨在全文空间上算得的相似度计数通常最密, 因转抄回声在整篇层面比在实体窗或同句片段层面更易被 TF-IDF 捕获, 故 full 轨的羊群降权幅度往往强于另两轨, 这也是把三轨分列而非合并的实证理由。本列作为羊群加权聚合分子, 与 sum_herd_weight_full 相除还原为可比语调 you_2018_tone_hw_full, 供 Stata 侧显式复算与分母口径敏感性检验。

## VAR: you_2018_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx: 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关的段落, 再在此片段上用 You et al. (2018) 词典逐词匹配并施加否定/程度/转折全规则, 算得文章级 you_2018_score_ctx。羊群权重取 ctx 轨的 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不再走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权; 因此本轨情感判据与降权判据同在实体窗空间, 与 full 轨在全文空间的口径系统性不同。逐篇 you_2018_score_ctx 乘 herd_weight_ctx 后在银行-年度内求和即本列。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。相对 full 轨, ctx 轨把情感信号收窄到实体近旁, 削弱远端无关文本对语调的稀释, 是 full 轨的规格稳健性并排轨。因情感与降权判据都在实体窗内, ctx 轨在语义上更贴近"关于该银行的这段话是正面还是负面、且是否为跟风转抄"这一构念, 但代价是可用文本更短、方差更高。需强调本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用: 实体窗按目标实体邻近范围裁剪, 与同句判据的句法边界不同。ctx 轨不承担留篇门控, 亦不因文本收窄而改变留篇集, 只在 full 留篇子集上按自身列照算。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ctx 相除还原 you_2018_tone_hw_ctx, 作为 full 轨语调的首要稳健性对照。

## VAR: you_2018_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中判据最严。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss: 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本, 再在此片段上算 You et al. (2018) 词典得分 you_2018_score_ss。回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 轨的回退机制同构。羊群权重取 herd_weight_ss, 在 ss 超级文档上做 TF-IDF 相似度所得; 当 ss 文本大面积回退到全文时, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷 (回退率越高、真三轨独立性越弱, 日志会告知)。逐篇 you_2018_score_ss 乘 herd_weight_ss 后银行-年度求和即本列。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。在开发期 T=2 小样本上, ss 轨因同句共现稀疏可能出现零方差或大面积回退, 属预期退化, 生产期 T=18 恢复正常。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及时的情感倾向", 因而对识别银行金科关联报道的语调最具针对性, 但也最易受回退稀释: 一旦回退, 该篇实际用的是全文文本与全文相似度, ss 轨对 full 轨的独立性随回退率上升而衰减, 故解读 ss 轨时须与回退率一并披露。ss 轨的严格同句判据 (银行与金科同句共现) 与 ctx 轨的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ss 相除还原 you_2018_tone_hw_ss, 作为三轨中判据最严的稳健性并排轨。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Yang, N., Fernandez-Perez, A., & Indriawan, I. (2026). Social media sentiment, investor herding and informational efficiency. Journal of Financial Research. https://doi.org/10.1111/jfir.70039
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
<!-- rendered-citations:end -->
