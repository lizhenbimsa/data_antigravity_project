---
family_id: F224
columns:
- du_2022_score_hw_sum_ctx
- du_2022_score_hw_sum_full
- du_2022_score_hw_sum_ss
unit: 无量纲 (羊群加权情感得分逐篇合计; 聚合分子分量, 非归一化到 [-1,1] 的语调值)
formula: "du_2022_score{track} = Σ(final_score)/Σ|final_score| ∈ [-1,1] (Du 2022 词典查得极性 + 否定/程度/转折全语言学规则; 正侧含 political_positive 以 0.5 权重计入, 即 canonical polw05 口径); herd_weight{track} = 1/(1 + n_similar_articles{track}); du_2022_score_hw{track} = du_2022_score{track} × herd_weight{track}; du_2022_score_hw_sum{track} = Σ_{article ∈ bank-year} du_2022_score_hw{track}"
producer: news_process/pipeline/panel/runner.py (步骤3d 逐篇羊群加权) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (bank-year sum)
upstream:
- 22_tone_words.parquet (du_2022_score_full / _ctx / _ss)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: 113917
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
- doi: 10.18653/v1/d16-1057
  type: wp
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个银行-年度层面的中间聚合量: 以 Du et al. (2022) 中文金融情感词典逐篇算得的报道情感得分, 先按"羊群衰减"权重逐篇缩放, 再在同一银行同一年度内对所有报道求和, 得到 du_2022_score_hw_sum。名称四段各有明确所指: du_2022 指所用词典是 Du, Huang, Wermers 与 Wu (2022) 发表于 Review of Finance 的中文金融情感词典, 该词典的一个鲜明特征是在正面词集之外额外区分出一类政治正面词 (political_positive, 1,434 词); score 指底层文章级测度是该词典的归一化情感极性得分, 取值区间 [-1, +1]; hw (herd-weighted, 羊群加权) 指每篇报道在进入求和前先乘以一个反映其信息独立性的降权乘子; sum 指银行-年度层内对经加权的逐篇得分作合计而非取均值。因此本量不是一个落在 [-1, +1] 的语调值, 而是加权求和的分子分量: 它与配套的羊群权重合计 sum_herd_weight 相除, 才还原为可比的羊群加权语调 du_2022_tone_hw。将分子单列落盘, 目的是让下游可在 Stata 侧显式复算比值、审计分子分母同域, 并支持对分母口径 (是否用有效掩码分母) 的敏感性检验。需特别说明的是, du_2022 家族在计分口径上带有一个词典专属维度: 其正侧幅值由普通正面词与政治正面词两部分构成, 后者依据 Du et al. (2022) "政治正面词信号弱于普通正面词"的发现按 0.5 权重计入, 本家族采用的正是这一 canonical 权重口径 (记作 polw05)。

【方法学与计算】
计算链路分三段。第一段在 stage 22 词典法内: 对每篇报道分词后, 在 Du et al. (2022) 词典上做逐词匹配, 普通正面词记 +1、负面词记 -1、政治正面词记 +0.5, 命中情感词依次施加三条语言学规则 —— 否定词在其后固定窗口内翻转极性、程度副词按倍率缩放幅值、转折词在从句作用域内按转折权重放大后半句, 遇句末标点重置规则状态; 由此得到每个情感词的 final_score, 文章级得分归一化为 Σ(final_score)/Σ|final_score|, 落在 [-1, +1], 正值偏正面、负值偏负面。此归一化口径与仅取原始词典极性计数的 msent 计数口径互为稳健性, 二者刻意不混用。跨类重叠词 (正负两侧兼登记的词条) 按用户 2026-06-24 决策保留并两侧计入, 以 (+1, -1) 平衡双票喂入, 使个体词典净语调拉向中性而不武断选边。第二段在 stage 24 羊群衰减处理: TF-IDF 向量空间按 as-of 年度拟合 (年 t 文章的向量空间仅用 year ≤ t 的文档拟合词汇/IDF, 严格不含未来信息), 但候选前驱集合并非"同年内所有更早报道", 而是由 TIME_WINDOW_DAYS (默认 7 天) 界定的滚动时间窗: 对同一目标银行的报道, 统计每篇报道 j 在其发布前 7 天窗内、与更早文章 i 的 TF-IDF 余弦相似度是否 ≥ SIMILARITY_THRESHOLD (0.35), 达标记为一次跟风前驱, 累计计数记为 n_similar_articles, 再令 herd_weight = 1/(1 + n_similar_articles); 转抄越多则权重越低, 越接近独立首发则权重越接近 1。年度截断只约束向量空间的拟合语料范围 (防止未来信息泄露), 与前驱候选集的 7 天时间窗是两个不同的口径维度, 不可混同。第三段在面板聚合 (runner 步骤 3d 逐篇相乘, encode 的 build_aggregation_dict 求和): 文章级 du_2022_score 乘以同轨 herd_weight 得到 du_2022_score_hw, 再在银行-年度分组内求和得到本列。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列。

【文献定位】
本测度的方法学谱系由数支文献锚定。词典本身与政治词降权口径均取自 Du et al. (2022): 该文发表于顶刊 Review of Finance, 系统论证了语言与领域特异性对中文金融情感度量至关重要, 通用英文词典直译到中文会因语言与制度差异产生系统性偏误, 这正是本管道选用中文金融专用词典而非直译词典的依据; 该文同时给出政治正面词信号弱于普通正面词的证据, 是本家族对 political_positive 施加 0.5 降权的直接来源。中文金融专用词典的持续构建脉络由 Ma et al. (2025) 的细粒度投资者情感词典 (CN-FSD) 与 Sun et al. (2025) 将词典知识注入预训练语言模型的工作延续, 二者共同印证词典法在中文金融文本上的可解释与可复现优势, 也说明单一词典难以穷尽领域语义、需以多部词典互证。政治色彩文本的语调对资本市场具信息含量这一点由 Xu et al. (2024) 就中国政府主导媒体的语调研究佐证, 支持 du_2022 显式区分政治正面词而非将其与普通正面词混同的建模选择。逐词施加否定、程度、转折规则并按语料诱导领域极性, 与 Hamilton et al. (2016) 从无标注语料诱导领域特异情感词典的方法学传统一脉相承; 而将文本语调作为可度量的经济信号, 呼应 Hwang 与 Kim (2017) 关于文本可读性与语调具市场定价含义的先例。需强调本家族的六部词典 (Du 2022 与 Jiang 2021、Yao 2021、Bian 2021、You 2018、Loughran) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同词典或不同聚合权重混进同一 over-identified Hansen J 检验; 同理三轨 (full/ctx/ss) 与不同聚合权重方案 (hw/idf/简单均值) 亦各自 just-identified 并排, 不得混入同一过度识别检验。

## VAR: du_2022_score_hw_sum_full

【变体差分】
本列是家族三轨中的 full (全文) 轨。文本口径为标题 prepend 后的报道全文正文: stage 14 的 ctx_materializer 把标题前置到正文, Du et al. (2022) 词典在完整标题加正文上匹配并施加否定/程度/转折全规则, 正侧含以 0.5 权重计入的政治正面词, 算得文章级 du_2022_score_full (canonical polw05 口径)。羊群权重取 full 轨的 herd_weight_full, 即在全文 TF-IDF 相似度空间上、按 as-of 年度拟合向量空间并在发布前 7 天滚动窗内统计跟风前驱计数所得的 1/(1 + n_similar_articles_full); 因此本轨的降权判据与情感判据同在全文空间, 二者口径一致。逐篇 du_2022_score_full 乘 herd_weight_full 得 du_2022_score_hw_full, 银行-年度内求和即本列。在三轨中 full 轨承担留篇门控职责 (full-only 口径, 2026-06-29): 某报道是否计入银行-年度报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 故 full 轨行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。作为羊群加权 (hw) 聚合方案, 本列与同家族的简单均值聚合、以及 idf 加权得分聚合属彼此正交的聚合权重方案: hw 按信息独立性降权转抄式跟风报道, idf 按词汇稀有度缩放幅值, 二者刻画不同的稳健性维度; 各聚合权重方案同样各自 just-identified 并排、互为稳健性、不分主次, 严禁与不同权重方案混进同一 over-identified Hansen J。full 轨在全文空间上算得的相似度计数通常最密, 因转抄回声在整篇层面比在实体窗或同句片段层面更易被 TF-IDF 捕获, 故 full 轨的羊群降权幅度往往强于另两轨, 这也是把三轨分列而非合并的实证理由。本列作为羊群加权聚合分子, 与 sum_herd_weight_full 相除还原为可比语调 du_2022_tone_hw_full, 供 Stata 侧显式复算与分母口径敏感性检验。

## VAR: du_2022_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx: 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关的段落, 再在此片段上用 Du et al. (2022) 词典逐词匹配并施加否定/程度/转折全规则 (政治正面词仍以 0.5 权重计入), 算得文章级 du_2022_score_ctx。羊群权重取 ctx 轨的 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不再走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权; 因此本轨情感判据与降权判据同在实体窗空间, 与 full 轨在全文空间的口径系统性不同。逐篇 du_2022_score_ctx 乘 herd_weight_ctx 后在银行-年度内求和即本列。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。相对 full 轨, ctx 轨把情感信号收窄到实体近旁, 削弱远端无关文本对语调的稀释, 是 full 轨的规格稳健性并排轨。因情感与降权判据都在实体窗内, ctx 轨在语义上更贴近"关于该银行的这段话是正面还是负面、且是否为跟风转抄"这一构念, 但代价是可用文本更短、方差更高。需强调本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用: 实体窗按目标实体邻近范围裁剪, 与同句判据的句法边界不同。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ctx 相除还原 du_2022_tone_hw_ctx, 作为 full 轨语调的首要稳健性对照。

## VAR: du_2022_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中判据最严。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss: 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本, 再在此片段上算 Du et al. (2022) 词典得分 du_2022_score_ss (正侧政治词仍按 0.5 权重)。回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 轨的回退机制同构。羊群权重取 herd_weight_ss, 在 ss 超级文档上做 TF-IDF 相似度所得; 当 ss 文本大面积回退到全文时, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷 (回退率越高、真三轨独立性越弱, 日志会告知)。逐篇 du_2022_score_ss 乘 herd_weight_ss 后银行-年度求和即本列。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。在早期试跑 T=2 小样本上, ss 轨因同句共现稀疏可能出现零方差或大面积回退, 属预期退化, 生产期 T=19 恢复正常。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及时的情感倾向", 因而对识别银行金科关联报道的语调最具针对性, 但也最易受回退稀释: 一旦回退, 该篇实际用的是全文文本与全文相似度, ss 轨对 full 轨的独立性随回退率上升而衰减, 故解读 ss 轨时须与回退率一并披露。ss 轨的严格同句判据 (银行与金科同句共现) 与 ctx 轨的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ss 相除还原 du_2022_tone_hw_ss, 作为三轨中判据最严的稳健性并排轨。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing No. 595-605 [Working Paper]. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
