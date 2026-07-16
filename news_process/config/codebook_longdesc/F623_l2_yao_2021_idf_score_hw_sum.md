---
family_id: F623
novelty_exempt_rationale: "该家族是 yao_2021 情感词典基础分数上叠加 IDF 稀有度加权与羊群 (herd) 衰减加权两个正交聚合权重维度的消融/组合变体 (idf_score_hw_sum), 与同词典的等权求和/单纯IDF/单纯herd等变体构成互为稳健性的权重梯度, 其测度定义的学术依据已在母族词典 (Yao 2021) 及 IDF/羊群加权原始文献 (Jegadeesh & Wu 2013; Spärck Jones 1972) 中给出, 非独立新构念, 不需追加 2023+ 新颖文献。"
columns:
- yao_2021_idf_score_hw_sum_ctx
- yao_2021_idf_score_hw_sum_full
- yao_2021_idf_score_hw_sum_ss
unit: 无量纲 (IDF加权且羊群加权的情感得分逐篇合计; 聚合分子分量, 非归一化到 [-1,1] 的语调值)
formula: "yao_2021_idf_weight(w) = winsorize_{P1,P99}( normalize_mean1( log10(N/(1+df(w))) ) ), N/df(w) 在同一 content_full 语料上统计 (Gentzkow, Kelly & Taddy 2019 JEL §2.2 口径); yao_2021_idf_score{track} = Σ(final_score × yao_2021_idf_weight(w))/Σ|final_score × yao_2021_idf_weight(w)| ∈ [-1,1] (Yao 2021 词典查得极性 × 词稀有度权重, 经否定/程度/转折全语言学规则); herd_weight{track} = 1/(1 + n_similar_articles{track}); yao_2021_idf_score_hw{track} = yao_2021_idf_score{track} × herd_weight{track}; yao_2021_idf_score_hw_sum{track} = Σ_{article ∈ bank-year} yao_2021_idf_score_hw{track}"
producer: news_process/pipeline/sentiment/tone_words.py (build_idf_weights + _build_idf_weighted_dict, IDF 词权重构建) ; news_process/pipeline/sentiment/herd_decay.py (compute_herd_weights, herd_weight = 1/(1+n_similar_articles) 真实计算) ; news_process/pipeline/panel/runner.py (步骤3d 逐篇羊群加权相乘) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (bank-year sum)
upstream:
- 22_tone_words.parquet (yao_2021_idf_score_full / _ctx / _ss)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss)
citations:
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
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
本家族刻画一个银行-年度层面的中间聚合量: 以 Yao (2021) 中文金融情感词典为底、经"词汇稀有度 IDF 加权"再叠加"羊群衰减"权重的逐篇情感得分, 在同一银行同一年度内对全部报道求和, 得到 yao_2021_idf_score_hw_sum。名称四段各有明确所指: yao_2021 指所用极性词典是 Yao (2021) 面向中文金融文本构建的情感词库; idf_score 指底层文章级测度并非直接取词典原始极性计数, 而是先对每个命中情感词按其在语料中的逆文档频率 (inverse document frequency) 缩放幅值, 再归一化到 [-1, +1] —— 稀有词 (低 df, 高 idf) 获得更大权重, 高频套话词 (高 df, 低 idf) 被系统性压低, 这是 Gentzkow, Kelly 与 Taddy (2019, *Journal of Economic Literature*) §2.2 归纳的文本计量学标准做法在词典法情感度量上的具体落地; hw (herd-weighted, 羊群加权) 指每篇报道在进入求和前再乘以一个反映其信息独立性的降权乘子; sum 指银行-年度层内对经双重加权的逐篇得分作合计而非取均值。因此本量不是一个落在 [-1, +1] 的语调值, 而是双重加权求和的分子分量: 它与配套的羊群权重合计 sum_herd_weight 相除, 才还原为可比的 IDF 加权羊群语调 yao_2021_idf_tone_hw。将分子单列落盘, 目的是让下游可在 Stata 侧显式复算比值、审计分子分母同域, 并支持对分母口径 (是否用有效掩码分母) 的敏感性检验。

【方法学与计算】
计算链路分三段。第一段在 stage 22 词典法内, 又细分两步: (a) IDF 权重构建 —— 在与 TF 打分同一语料 (content_full, 标题 prepend 后的全文, 与裸"内容"列不同源, 避免标题词 df 被低估) 上, 对 Yao (2021) 词典中每个词 w 统计文档频率 df(w) 与语料内唯一文档数 N, 算得 log10(N/(1+df(w))), 再做均值归一到 1、并在 P1/P99 分位做 winsorize 截尾以抑制极端稀有词的权重爆炸, 得到 yao_2021_idf_weight(w); 该权重词典与原始极性词典逐词一一对应, 权重仅缩放幅值、不改变极性归属, 与原始词典比较时跨类重叠词集口径一致 (两侧计数取绝对值)。(b) 逐篇打分 —— 对每篇报道分词后, 在 IDF 加权词典上做逐词匹配, 命中情感词依次施加三条语言学规则 (否定词在其后固定窗口内翻转极性、程度副词按倍率缩放幅值、转折词在从句作用域内按转折权重放大后半句, 遇句末标点重置规则状态), 得到每个情感词的 final_score (已含 IDF 幅值缩放), 文章级得分归一化为 Σ(final_score)/Σ|final_score|, 落在 [-1, +1], 即 yao_2021_idf_score。此 IDF 加权口径与不加权的原始 yao_2021_score 互为稳健性、刻意不混用, 二者分别捕获"稀有词驱动的语调"与"全部词等权的语调"两种构念假设。第二段在 stage 24 羊群衰减处理: 对同一目标银行的报道按发布年度截断, 用 TF-IDF 余弦相似度统计每篇报道在同年早前存在多少篇高度相似 (疑似转抄、回声式跟风) 的报道, 记为 n_similar_articles, 再令 herd_weight = 1/(1 + n_similar_articles); 转抄越多则权重越低, 越接近独立首发则权重越接近 1。注意此处羊群衰减用于相似度判定的 TF-IDF 与第一段情感度量用的 IDF 加权词典是两套独立构造 (前者刻画文档间的整体文本相似度, 后者刻画情感词在语料内的稀有度), 命名巧合不代表口径共享。第三段在面板聚合 (runner 步骤 3d 逐篇相乘, encode 的 build_aggregation_dict 求和): 文章级 yao_2021_idf_score 乘以同轨 herd_weight 得到 yao_2021_idf_score_hw, 再在银行-年度分组内求和得到本列。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列。

【文献定位】
本测度的方法学谱系由四支文献锚定。IDF 加权情感度量的直接方法学依据是 Jegadeesh 与 Wu (2013, *Journal of Financial Economics*) 提出的"词汇力量" (word power) 框架 —— 该文论证情感词对市场反应的边际信息含量并非均一, 应按词的相对信息量而非等权计数赋权, 这正是本列在 yao_2021 原始词典之上再叠加逐词 IDF 权重的经济学动机: 高频套话词 (如"发展"、"稳健") 信息量低, 应予压低; 低频专有情感表述信息量高, 应予放大。IDF 权重本身的统计构造 (逆文档频率、log(N/df)) 溯源自信息检索经典文献 Spärck Jones (1972, *Journal of Documentation*), 该文首次系统阐释词项特异性的统计解释及其在检索中的应用, 是本管道全部 idf_score 系列指标共享的权重原语出处。词典本身取 Yao (2021), 与本项目使用的其余五部中文金融情感词典 (Jiang 2021、Bian 2021、Du 2022、You 2018、Loughran 中文译本) 并列, 领域特异性价值由 Du et al. (2022, *Review of Finance*) 在顶刊层面进一步确证 —— 该文系统论证语言与领域特异性对中文金融情感度量至关重要, 通用英文词典直译到中文会因制度与语言差异系统性失准, 这正是本管道优先选用中文金融专用词典而非直译词典的依据, 也是 IDF 加权在词典法内部 (而非跨词典) 做稳健性检验的理论前提。逐词施加否定、程度、转折规则并作从句级作用域重置, 遵循 Taboada et al. (2011, *Computational Linguistics*) 确立的词典法情感分析范式。而将 IDF 加权轨与原始等权轨、及词典法整体与机器学习/大模型法并置互证, 呼应 Frankel, Jennings 与 Lee (2022, *Management Science*) 关于披露情感的机器学习法与词典法互为稳健性的先例。需强调本项目内 IDF 加权 (idf_score) 与羊群加权 (hw) 是两个正交的聚合权重维度, 二者叠加使用时各自的稳健性证成互不替代; 六部词典各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同词典或不同聚合权重方案 (等权 sum / IDF 加权 idf_score / 羊群加权 hw / 二者叠加 idf_score_hw) 混进同一 over-identified Hansen J 检验。

## VAR: yao_2021_idf_score_hw_sum_full

【变体差分】
本列是家族三轨中的 full (全文) 轨。文本口径为标题 prepend 后的报道全文正文: stage 14 的 ctx_materializer 把标题前置到正文, IDF 词权重的分子分母 (N、df(w)) 亦在同一 content_full 语料上统计, 保证 TF 打分与 IDF 语料同源。情感词典在完整标题加正文上匹配 Yao (2021) 的 IDF 加权词典并施加否定/程度/转折全规则, 算得文章级 yao_2021_idf_score_full。羊群权重取 full 轨的 herd_weight_full, 即在全文 TF-IDF 相似度空间上统计的同年转抄计数所得的 1/(1 + n_similar_articles_full); 因此本轨的降权判据与情感判据同在全文空间, 二者口径一致。逐篇 yao_2021_idf_score_full 乘 herd_weight_full 得 yao_2021_idf_score_hw_full, 银行-年度内求和即本列。在三轨中 full 轨承担留篇门控职责 (full-only 口径, 2026-06-29): 某报道是否计入银行-年度报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 故 full 轨行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。作为"IDF 加权 × 羊群加权"双重加权聚合方案, 本列与同家族的等权求和 (yao_2021_score_sum)、单纯羊群加权 (yao_2021_score_hw_sum)、单纯 IDF 加权无羊群 (yao_2021_idf_score_sum) 属彼此正交的聚合权重方案组合: idf 按词汇稀有度缩放幅值、hw 按转抄独立性降权整篇, 二者刻画不同稳健性维度, 叠加时任一维度的权重设定敏感性都应独立披露。full 轨在全文空间上算得的相似度计数通常最密, 因转抄回声在整篇层面比在实体窗或同句片段层面更易被 TF-IDF 捕获, 故 full 轨的羊群降权幅度往往强于另两轨, 这也是把三轨分列而非合并的实证理由。本列作为双重加权聚合分子, 与 sum_herd_weight_full 相除还原为可比语调 yao_2021_idf_tone_hw_full, 供 Stata 侧显式复算与分母口径敏感性检验。

## VAR: yao_2021_idf_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx: 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关的段落。IDF 词权重构建仍统一在 content_full 语料上统计 (保持全部三轨共享同一套稀有度基准, 避免因窗口裁剪改变 df 分母而导致三轨权重不可比), 但 TF 打分本身在 content_ctx 片段上进行: 用该 IDF 加权词典逐词匹配 Yao (2021) 极性并施加否定/程度/转折全规则, 算得文章级 yao_2021_idf_score_ctx。羊群权重取 ctx 轨的 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不再走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权; 因此本轨情感判据在实体窗空间, 而降权判据同样在实体窗空间, 与 full 轨在全文空间的口径系统性不同。逐篇 yao_2021_idf_score_ctx 乘 herd_weight_ctx 后在银行-年度内求和即本列。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。相对 full 轨, ctx 轨把情感信号收窄到实体近旁, 削弱远端无关文本对语调的稀释, 是 full 轨的规格稳健性并排轨; 由于 IDF 权重共享同一 content_full 基准而 TF 打分窗口收窄, ctx 轨相对 full 轨的差异主要来自"哪些稀有词被实际观测到", 而非稀有度权重本身的重新标定。需强调本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ctx 相除还原 yao_2021_idf_tone_hw_ctx, 作为 full 轨语调的首要稳健性对照。

## VAR: yao_2021_idf_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中判据最严。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss: 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本, 再在此片段上用同一 content_full 基准构建的 IDF 加权词典算 Yao (2021) 得分 yao_2021_idf_score_ss。回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 轨的回退机制同构; 回退发生时该篇实际用的文本与相似度判据均等同于 full 轨。羊群权重取 herd_weight_ss, 在 ss 超级文档上做 TF-IDF 相似度所得; 当 ss 文本大面积回退到全文时, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷 (回退率越高、真三轨独立性越弱, 日志会告知)。逐篇 yao_2021_idf_score_ss 乘 herd_weight_ss 后银行-年度求和即本列。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。在开发期 T=2 小样本上, ss 轨因同句共现稀疏可能出现零方差或大面积回退, 属预期退化, 生产期 T=19 恢复正常。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及、且该句所用词汇有多稀有"这一双重条件下的情感倾向, 因而对识别银行金科关联报道的语调最具针对性, 但也最易受回退稀释与样本量不足双重影响。ss 轨的严格同句判据 (银行与金科同句共现) 与 ctx 轨的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ss 相除还原 yao_2021_idf_tone_hw_ss, 作为三轨中判据最严的稳健性并排轨, 解读时须与回退率一并披露。

<!-- rendered-citations:begin -->
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
