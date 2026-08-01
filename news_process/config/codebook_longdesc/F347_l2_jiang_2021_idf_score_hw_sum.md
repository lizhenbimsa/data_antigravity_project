---
family_id: F347
novelty_exempt_rationale: "该家族是 jiang_2021 词典的 IDF加权×羊群衰减(hw) 双重加权组合变体, 测度定义依据已在母族词典文献(姜富伟等2021)及IDF/羊群衰减方法学文献(Spärck Jones 1972; Jegadeesh & Wu 2013)中给出, 属加权梯子的组合变体而非独立新构念, 无需追加2023+新文献。"
columns:
- jiang_2021_idf_score_hw_sum_ctx
- jiang_2021_idf_score_hw_sum_full
- jiang_2021_idf_score_hw_sum_ss
unit: 无量纲加权得分和 (IDF 加权词典分再叠加羊群衰减权重的逐篇乘积, bank-year 内合计; 非归一化到 [-1,1] 的语调值)
formula: "jiang_2021_idf_score{track} = _compute_sentiment_with_rules(tokens, jiang_2021 的 IDF 加权词典, 否定/程度/转折全语言学规则) 归一化得分 (Gentzkow et al. 2019 JEL §2.2 口径; stage 22 tone_words.py); herd_weight{track} = 1/(1 + n_similar_articles{track}) (stage 24 herd_decay); jiang_2021_idf_score_hw{track} = jiang_2021_idf_score{track} × herd_weight{track} (panel runner 步骤 3d 逐篇现算, 非 stage 22 落盘列); jiang_2021_idf_score_hw_sum{track} = Σ_{article ∈ bank-year} jiang_2021_idf_score_hw{track}"
producer: news_process/pipeline/panel/runner.py (步骤3d 逐篇 IDF 加权分 × 羊群权重相乘) ; news_process/pipeline/panel/encode.py (F 段 bank-year sum 聚合, L1069) ; news_process/pipeline/panel/stata_export.py (标签导出)
upstream:
- 22_tone_words.parquet (jiang_2021_idf_score_full / _ctx / _ss, IDF 加权词典逐篇得分)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: "10.1016/j.econlet.2026.113002"
  type: "journal"
  authors: "Nakatsuka, H., & Suimon, Y."
  year: 2026
  title: "How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures"
  venue: "Economics Letters"
  vol: "265"
  pages_or_artno: "113002"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个银行-年度层面的中间聚合量: 以姜富伟、孟令超与唐国豪 (2021, 《经济学(季刊)》) 构建的中文媒体文本情绪词典为底本, 先对逐词命中按其 IDF (逆文档频率) 缩放幅值, 得到 IDF 加权的文章级情感得分, 再叠加"羊群衰减"权重逐篇缩放, 最后在同一银行同一年度内对全部报道求和, 得到 jiang_2021_idf_score_hw_sum。列名五段各有明确所指: jiang_2021 指所用词典是姜富伟等 (2021) 建立、并已在 Frankel, Jennings 与 Lee (2022) 等文献所属方法学谱系中确立地位的中文金融/媒体情感词典; idf 指该词典命中的每个情感词并非等权计入, 而是按其在语料库中的稀有度 (逆文档频率) 加权 —— 常见词权重被压低, 罕见但信息量大的词权重被放大, 这一思路承袭 Spärck Jones (1972) 提出的词汇特异性统计诠释, 并在 Jegadeesh 与 Wu (2013) "word power" 一文中被系统引入金融文本情感度量; score 指底层文章级测度是该 IDF 加权词典的归一化情感得分; hw (herd-weighted, 羊群加权) 指每篇报道在进入求和前先乘以一个反映其信息独立性的降权乘子, 转抄或跟风报道被系统性降权; sum 指银行-年度层内对经加权的逐篇得分作合计而非取均值。本量因此不是一个落在 [-1, +1] 区间的可比语调值, 而是加权求和的分子分量: 它与配套的羊群权重合计 (sum_herd_weight) 相除, 才还原为可比的羊群加权 IDF 语调 jiang_2021_idf_tone_hw。将分子单独落盘的用意, 是让 Stata 侧能显式复算比值、审计分子分母同域, 并支持对分母口径 (是否用有效掩码分母) 的敏感性检验, 而不是把两次加权 (IDF 幅值加权 + 羊群独立性加权) 隐藏在一个已归一的比值里。

【方法学与计算】
计算链路分三段, 三段分处三个不同阶段的脚本, 须严格区分归属, 不可把 IDF 加权或羊群加权误挂到彼此的阶段上。第一段在 stage 22 词典法内落盘 jiang_2021_idf_score{track}: 对每篇报道分词后, 在姜富伟等 (2021) 词典的 IDF 加权版本上做逐词匹配 (`IDF_DICTIONARIES`), 命中的情感词先按语料库逆文档频率缩放幅值, 再依次施加否定/程度/转折三条语言学规则 (否定词在固定窗口内翻转极性、程度副词按倍率缩放、转折词在从句作用域内放大后半句), 由 `_compute_sentiment_with_rules` 归一化输出, 口径遵循 Gentzkow, Kelly 与 Taddy (2019, Journal of Economic Literature §2.2) 关于文本计量中 IDF 加权与词典法情感度量的规范讨论。此列与不加 IDF 幅值缩放的裸词典分 jiang_2021_score 互为稳健性并排、不分主次: 前者按词汇稀有度加大信息量高的词的贡献, 后者对全部命中词等权处理, 二者刻意不混用同一识别式。第二段在 stage 24 羊群衰减处理中落盘 herd_weight{track}: 对同一目标银行的报道按发布年度截断, 用 TF-IDF 余弦相似度统计每篇报道在同年早前存在多少篇高度相似 (疑似转抄、回声式跟风) 的报道, 记为 n_similar_articles, 再令 herd_weight = 1/(1 + n_similar_articles); 转抄越多则权重越低, 越接近独立首发则权重越接近 1。第三段是运行期现算而非落盘中间列: panel runner 步骤 3d 把 stage 22 的 IDF 加权逐篇分 jiang_2021_idf_score{track} 与 stage 24 的 herd_weight{track} 逐行相乘, 现算出 jiang_2021_idf_score_hw{track}; encode.py 的 F 段随即在银行-年度分组内对该现算列求和, 落盘为本列。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列, 零新闻银行-年按空集求和 (Σ over ∅ = 0) 落 0 而非缺失。

【文献定位】
本测度的方法学谱系由三条线索交织。词典本身取姜富伟、孟令超与唐国豪 (2021) 发表于《经济学(季刊)》的媒体文本情绪度量, 该文以中国媒体语料为对象构建情绪词典并验证其对股票回报的预测力, 是本仓六部中文情感词典 (jiang_2021 与 bian_2021、yao_2021、du_2022、you_2018、loughran) 之一。IDF 加权幅值缩放的统计学依据溯源至 Spärck Jones (1972) 关于词汇特异性的经典诠释, 并在 Jegadeesh 与 Wu (2013) 发表于 Journal of Financial Economics 的 "word power" 方法中被引入金融文本情感构造 —— 稀有但携带强烈情感信息的词应比常见泛化词获得更大权重, 这正是本列相对于裸词典分额外叠加的第一层加权。将 IDF 加权词典结果与羊群衰减权重叠加、并与 LLM 法及 BERT 法并置互证, 呼应 Frankel, Jennings 与 Lee (2022) 关于披露情感的机器学习法与词典法互为稳健性的先例, 以及 van Atteveldt, van der Velden 与 Boukes (2021) 对人工标注、词典法与机器学习法效度的横向比较。需强调本项目的多重加权口径 (等权 tone、IDF 加权、羊群加权 hw、媒体权威加权 mw、提及密度加权 w) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同加权方案或不同词典混进同一 over-identified Hansen J 检验; 三轨 (full/ctx/ss) 同理各自 just-identified 并排、禁混同一 Hansen J。 在羊群衰减这一层加权上, Nakatsuka 与 Suimon (2026) 提供了近期的经验参照: 该文对日本公司披露文本联合分析文本相似度 (新颖性) 与情感, 检验市场对文本新颖性的反应, 论证相似度与情感须联合而非各自单独考察, 正对应本列把 IDF 加权词典分再乘以 1/(1 + n_similar_articles) 从而将情感与新颖性 (相似度的减函数) 折叠为乘性结构的设计意图。迁移边界须如实标明: 该文语料为日文的公司披露文件而非第三方媒体报道, 其相似度为披露文本间的连续相似度且与情感取联合分析/交互形式, 并未采用本列这一具体的倒数衰减函数, 亦未把二者的乘积再于银行-年内求和; 其分析层级为披露事件, 而非本列的银行-年三轨。
## VAR: jiang_2021_idf_score_hw_sum_full

【变体差分】
本列是家族三轨中的 full (全文) 轨, 亦是留篇门控的判定轨。文本口径为标题 prepend 后的报道全文正文: stage 14 的 ctx_materializer 把标题前置到正文, IDF 加权词典在完整标题加正文上匹配姜富伟等 (2021) 词典命中词并按语料库逆文档频率缩放幅值, 再施加否定/程度/转折全规则, 算得文章级 jiang_2021_idf_score_full。羊群权重取 full 轨的 herd_weight_full, 即在全文 TF-IDF 相似度空间上统计的同年转抄计数所得的 1/(1 + n_similar_articles_full); 因此本轨的降权判据与情感判据同在全文空间, 二者口径一致。panel runner 步骤 3d 现算 jiang_2021_idf_score_full × herd_weight_full 得 jiang_2021_idf_score_hw_full, 银行-年度内求和即本列。留篇门控采用 full-only 口径 (2026-06-29): 某报道是否计入银行-年度报道宇宙, 由其 full 轨是否被判为一篇银行金科报道决定, 故 full 轨行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。作为"IDF 加权 + 羊群加权"的双重加权方案, 本列与家族内其他单一或不同组合的加权口径 (裸词典 sum、单独 IDF 加权 idf_tone_sum、单独羊群加权 score_hw_sum、提及密度加权 idf_score_w_sum、媒体权威加权 idf_score_mw_sum) 彼此正交并排: IDF 缩放的是"这个词有多稀有/多有信息量", 羊群衰减缩放的是"这篇报道有多独立、非转抄", 两者刻画不同维度的稳健性, 同样各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。full 轨在全文空间上算得的相似度计数通常最密, 因转抄回声在整篇层面比在实体窗或同句片段层面更易被 TF-IDF 捕获, 故 full 轨的羊群降权幅度往往强于另两轨, 这也是把三轨分列而非合并的实证理由。本列作为双重加权聚合分子, 与 sum_herd_weight_full 相除还原为可比语调 jiang_2021_idf_tone_hw_full, 供 Stata 侧显式复算与分母口径敏感性检验。

## VAR: jiang_2021_idf_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx: 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关的段落, 再在此片段上用姜富伟等 (2021) IDF 加权词典逐词匹配并施加否定/程度/转折全规则, 算得文章级 jiang_2021_idf_score_ctx。羊群权重取 ctx 轨的 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不再走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权; 因此本轨情感判据与降权判据同在实体窗空间, 与 full 轨在全文空间的口径系统性不同。panel runner 步骤 3d 现算 jiang_2021_idf_score_ctx × herd_weight_ctx 后在银行-年度内求和即本列。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。相对 full 轨, ctx 轨把情感信号与 IDF 幅值统计都收窄到实体近旁, 削弱远端无关文本对语调及词频统计的稀释, 是 full 轨的规格稳健性并排轨。需强调本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用: 实体窗按目标实体邻近范围裁剪, 与同句判据的句法边界不同, 与 stage 13 邻近共现的硬过滤判据也不相同。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ctx 相除还原 jiang_2021_idf_tone_hw_ctx, 作为 full 轨语调的首要稳健性对照。在早期试跑 T=2 小样本上, 实体窗轨可能因命中稀疏而呈现较大波动, 属预期退化, 生产期 T=19 语料下方回归正常。

## VAR: jiang_2021_idf_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中判据最严。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss: 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (config filtering.yaml::context_window.ss_sentence_radius, 默认 ±1 句) 窗内共现的文本, 再在此片段上算姜富伟等 (2021) IDF 加权词典得分 jiang_2021_idf_score_ss。回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 与 ctx 轨的回退机制同构、共享 n_articles 分母口径; 若上游金融科技 AC 词典为空则 ss_is_fallback 全 True 优雅降级。羊群权重取 herd_weight_ss, 在 ss 超级文档上做 TF-IDF 相似度所得; 当 ss 文本大面积回退到全文时, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷 (回退率越高、真三轨独立性越弱)。panel runner 步骤 3d 现算 jiang_2021_idf_score_ss × herd_weight_ss 后银行-年度求和即本列。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及时、经稀有度加权的情感倾向", 因而对识别银行金科关联报道的语调最具针对性, 但也最易受回退稀释: 一旦回退, 该篇实际用的是全文文本、全文 IDF 统计域与全文相似度, ss 轨对 full 轨的独立性随回退率上升而衰减, 故解读 ss 轨时须与回退率一并披露。ss 轨的严格同句判据与 ctx 轨的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列与 sum_herd_weight_ss 相除还原 jiang_2021_idf_tone_hw_ss, 作为三轨中判据最严的稳健性并排轨。在早期试跑 T=2 上 ss 轨因同句共现稀疏可能出现零方差或大面积回退, 属预期退化, 生产期 T=19 恢复正常, 不影响本列作为双重加权分子的口径定义。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Nakatsuka, H., & Suimon, Y. (2026). How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures. Economics Letters, 265, 113002. https://doi.org/10.1016/j.econlet.2026.113002
<!-- rendered-citations:end -->
