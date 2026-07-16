---
family_id: F216
columns:
- du_2022_idf_score_w_sum_ctx
- du_2022_idf_score_w_sum_full
- du_2022_idf_score_w_sum_ss
unit: 无量纲情感得分的价值加权和 (bank-year 内跨报道对"报道净语调×提及密度"求和, 本身未归一化)
formula: "du_2022_idf_score_w_sum{track} = Σ_i (du_2022_idf_score_i{track} × mention_density_i); 其中 du_2022_idf_score = 以 IDF 权重缩放 du_2022 词典 base_score 后, 经否定/程度/转折三条语言学规则得到的逐篇净语调 (political_positive 1,434 词以 0.5 权重计入正侧); 除以 sum_mention_density 即得价值加权语调 du_2022_idf_tone_vw{track}"
producer: news_process/pipeline/sentiment/tone_words.py (逐篇 du_2022_idf_score) ; news_process/pipeline/panel/runner.py 步骤3b (逐篇 _w 加权列 = idf_score × mention_density) ; news_process/pipeline/panel/encode.py (bank-year _w_sum 聚合)
upstream:
- 21_tone_llms.parquet (content_full/content_ctx/content_ss + mention_density)
- 22_tone_words.parquet (du_2022_idf_score{track})
- 22_idf_weights.json (逐词 IDF 权重, 可复现锚)
citations:
- doi: 10.1038/s41586-026-10251-x
  type: journal
  authors: Brodeur, A., Mikola, D., Cook, N., et al.
  year: 2026
  title: "Reproducibility and robustness of economics and political science research"
  venue: Nature
  vol: 652
  issue: 8108
  pages_or_artno: 151-156
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  venue: "Expert Systems with Applications, 264, 125739"
  type: "journal"
  one_sentence_zh: "构建面向中国境内投资者的细粒度中文情感词典(CN-FSD)并验证其在金融文本情感测度上的应用效果, 与本家族 du_2022 中文金融情感词典构念直接相关。"
- doi: "10.1080/00031305.2025.2539241"
  title: "A Fisher's Exact Test Justification of the TF–IDF Term-Weighting Scheme"
  authors: "Sheridan, P., Ahmed, Z., & Farooque, A. A."
  year: 2025
  venue: "The American Statistician, 80(1), 146-156"
  type: "journal"
  one_sentence_zh: "为 TF-IDF 词项加权方案提供基于 Fisher 精确检验的统计学理论依据, 支撑本家族逐词 IDF 权重构造的方法学正当性。"
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1017/CBO9780511809071
  type: book
  authors: Manning, C. D., Raghavan, P., & Schütze, H.
  year: 2008
  title: "Introduction to information retrieval"
  venue: Cambridge University Press
new_dois:
  - "10.1016/j.eswa.2024.125739"
  - "10.1080/00031305.2025.2539241"
---

## CORE

【构念与来源】
本家族三列 du_2022_idf_score_w_sum_full / _ctx / _ss 记录的是, 在给定 bank-year 单元内, 对该单元下每一篇报道的"IDF 加权 du_2022 词典净语调 × 该篇提及密度"逐篇求和后得到的价值加权分子和。它并非一个可直接解读的语调水平, 而是价值加权语调 du_2022_idf_tone_vw 的分子: encode 阶段以 sum_mention_density (同一 bank-year 内所有报道提及密度之和) 作分母去除本列, 才得到落在语调量纲上的价值加权测度。之所以把分子单独物化落盘, 是为了让 Stata 侧能够在需要时重新组合分子分母、施加不同的样本掩码或稳健性权重, 而不必回到逐篇文本层重算, 这是把价值加权暴露的分子与分母各自物化、在面板层保留重组自由度的标准落地方式。

构念上, du_2022 指的是 Du、Huang、Wermers 与 Wu (2022) 发表于 Review of Finance 的中文金融情感词典 (含 positive 2,235 词、negative 2,986 词, 另有 political_positive 1,434 词)。该词典相较早期直译自 Loughran 与 McDonald 英文表的方案, 强调语言与领域特异性, 尤其识别出一类"政治正面词"其市场信号弱于普通正面词, 因而在本管道生产口径中以 0.5 权重计入正侧。逐篇 du_2022_idf_score 即在此词典基础上, 先由 IDF 权重缩放每个词的 base_score, 再叠加否定翻转、程度副词、转折增强三条语言学规则, 归一化为落在正负之间的净语调。

【方法学与计算】
计算链条分三段跨三个阶段。第一段在 stage 22 (tone_words) 内: build_idf_weights 以含标题的 content_full 为 IDF 语料 (使 IDF 语料与 TF 语料同源, 避免标题词文档频率被低估), 对每部词典逐词估计逆文档频率权重并存入 22_idf_weights.json (N = 去重后唯一文档数, 附 n_rows 供对账, 满足可复现要求); _build_idf_weighted_dict 把该权重乘入词典 base_score, 保留极性符号与非对称幅值; 随后 _compute_sentiment_with_rules 在 IDF 加权词典上, 沿用与 raw 口径同一的跨类重叠词处理 (both_sided_words, 幅值取绝对值两侧计数), 输出逐篇 du_2022_idf_score{track}。第二段在 panel runner 步骤3b: 以提及密度 mention_density 为价值权重 w, 构造逐篇 du_2022_idf_score_w{track} = idf_score × w。第三段在 encode: 按 bank-year 分组对该加权列求和 (sum), 得本家族三列; 零新闻 bank-year 的和按"空集求和为 0"口径填 0, 与 sum_mention_density 等兄弟列同契约。

IDF 加权本身是 Gentzkow、Kelly 与 Taddy 文本即数据方法学谱系下的稳健性检验设计: 罕见词往往携带更强的区分性信息, 故给予更高权重, 与均权 raw 词频构成互为稳健性的并排臂。IDF 权重只缩放幅值、不改变词的极性归属, 因此政治词 0.5 权重、否定/程度/转折三规则均在 IDF 之上正交叠加, 三者的语义边界互不侵占。

【文献定位】
词典来源锚定 Du 等 (2022, Review of Finance) 这一顶刊文, 其对中文金融文本语言与领域特异性的论证, 以及政治正面词信号偏弱的实证发现, 是本管道对该类词降权处理的直接依据。IDF/词权重的内容分析传统可上溯 Jegadeesh 与 Wu (2013) 在 Journal of Financial Economics 提出的 word power 方法 (以词项权重刻画文本信息含量), 以及 Manning、Raghavan 与 Schütze (2008) 对逆文档频率的信息检索经典化处理; 领域特异性情感词表的语料驱动归纳则见 Hamilton 等 (2016)。把 IDF 加权轨与 raw 词频轨并排, 而非以其替换主轨, 与 Brodeur 等 (2026, Nature) 对经济学与政治学研究可复现性与稳健性的呼吁一致: 测度设计的每一个自由度都应以并排稳健性臂而非单点选择来承载。铁律层面, 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨或 IDF 与 raw 混进同一 over-identified Hansen J 的过度识别集。此外, Ma, Zhang 和 Zhang (2025, Expert Systems with Applications) 构建面向中国境内投资者的细粒度中文情感词典(CN-FSD)并验证其在金融文本情感测度上的应用效果, 与本家族 du_2022 中文金融情感词典构念直接相关; Sheridan, Ahmed 和 Farooque (2025, The American Statistician) 为 TF-IDF 词项加权方案提供基于 Fisher 精确检验的统计学理论依据, 支撑本家族逐词 IDF 权重构造的方法学正当性。

## VAR: du_2022_idf_score_w_sum_full

【变体差分】
本列是 full 轨实现。full 轨的逐篇文本 content_full = 标题 prepend 到全文正文 (stage 14 ctx_materializer 物化, 原始"内容"列不动), 因此其 du_2022_idf_score_full 覆盖整篇报道的全部词汇, 是三轨中信息面最宽的一轨。与 _ctx / _ss 的唯一差别在文本范围: full 不施加银行-金科实体邻近或同句约束, 分子对"报道级 IDF 加权净语调 × 提及密度"沿整篇文本求和。需要强调, 本列与留篇门控 (full-only, 2026-06-29) 口径一致: 某报道是否被判为"一篇银行金科报道"仅取决于 llm_verified_full, 行宇宙 = full 留篇集, ctx/ss 为其 conditional-on-full 子集轨; 但本词典价值加权分子是 per-track 逐轨照算的, 并不以门控翻转而改变 full 轨自身的求和口径。作为价值加权分子, 本列本身未归一化, 解读须配合 sum_mention_density 还原为 du_2022_idf_tone_vw_full; 直接在回归中使用本列等价于以提及密度加权的语调总量 (随报道数与提及强度共同放大), 适合作暴露量而非强度量。IDF 加权使罕见但高区分度的情感词获得更高权重, 与 full 轨的 raw 词频价值加权分子 du_2022_score_w_sum_full 构成互为稳健性的并排臂 — 二者各自 just-identified, 严禁混入同一 over-identified Hansen J。政治正面词在本列内以 0.5 生产权重计入正侧, 该权重的 {0.0, 0.5, 1.0} 敏感性梯子在 du_2022_score 主族另有物化, 与本 IDF 分子正交、不交叉。

## VAR: du_2022_idf_score_w_sum_ctx

【变体差分】
本列是 ctx 轨 (实体窗) 实现。ctx 轨的逐篇文本 content_ctx = 标题 prepend 到"目标银行实体上下文窗口"内的正文片段, 相对 full 轨收窄到与目标银行邻近的语境, 意在剥离整篇报道中与该银行无关的段落对语调的稀释。因此本列的 du_2022_idf_score_ctx 只在实体窗文本上匹配 du_2022 词典并施加 IDF 加权与三条语言学规则, 再乘以提及密度并在 bank-year 内求和。与 full 轨相比, 差别纯在文本范围 (实体窗 vs 整篇), 词典、IDF 权重表、政治词 0.5 权重、否定/程度/转折规则、价值加权分子的构造方式完全一致。当某报道缺失有效实体窗时, ctx 文本按管道回退公理处理, 本列对该篇的贡献相应退化。作为 conditional-on-full 的稳健性/测度轨 (行宇宙 = full 留篇集子集), ctx 分子是逐轨独立求和, 不借用 full 轨的分母或分子。本列同样是未归一化的价值加权分子, 须除以 sum_mention_density 还原为 du_2022_idf_tone_vw_ctx。ctx 轨与 full、ss 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; ctx 的 IDF 加权臂与其 raw 词频臂亦为并排稳健性关系, 不得联立于同一过度识别集。政治词 0.5 权重口径与 full 轨完全对称。ctx 轨的独立价值在于, 当报道大篇幅涉及多家银行或与目标银行无关的宏观叙事时, 整篇 full 语调可能被无关段落污染, 而实体窗聚焦能提供对目标银行更贴近的语调读数; 二者孰更接近真实构念是一个实证问题, 故并排保留而非取舍。IDF 权重表在 ctx 轨与 full、ss 轨之间共享同一份 22_idf_weights.json (逐词逆文档频率仍以 full 语料估计), 保证跨轨的词权重可比、差异纯粹来自匹配文本范围而非权重口径漂移。

## VAR: du_2022_idf_score_w_sum_ss

【变体差分】
本列是 ss 轨 (同句) 实现, 三轨中约束最严。ss 轨的逐篇文本 content_ss = 标题 prepend 到"目标银行与金科词在同一句子内共现 (±N 句窗, 默认半径 1)"的片段, 只保留银行与金融科技真正同句出现的语境, 是刻画银行-金科直接关联语调的最窄轨。据此本列的 du_2022_idf_score_ss 仅在同句共现片段上做 du_2022 词典匹配、IDF 加权与三规则处理, 乘提及密度后在 bank-year 内求和。ss 轨的回退语义镜像 ctx: 当某报道不存在银行∧金科同句共现时, content_ss 退化为全文 body 且 ss_is_fallback 置真, 此时本列对该篇的语调贡献等同于以全文计, 而非置空 — 这一优雅降级确保分母 (共享 n_articles / sum_mention_density 口径) 不被人为掏空。在开发期 T=2 小样本上, ss 轨常因同句共现稀疏而大面积回退, 其价值加权分子可能与 full/ctx 高度接近甚至退化, 属预期现象, 生产期 T=19 语料下方能体现同句约束的甄别力。本列仍为未归一化分子, 还原为 du_2022_idf_tone_vw_ss 须除以 sum_mention_density。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨或 IDF/raw 臂混进同一 over-identified Hansen J。政治正面词 0.5 生产权重、IDF 权重表、语言学规则集与另两轨完全一致, 差别自始至终只在文本范围这一维。ss 轨的构念定位是三轨中最贴近"银行与金融科技直接关联语调"的一轨: 它排除了那些仅在报道别处顺带提及银行、却在谈论金科时并未与该银行同句关联的语境, 因而对"这家银行自身的金科相关语调"给出最保守、最少借用的读数。也正因约束最严、回退最频繁, 单独使用 ss 分子时须警惕其有效样本被回退稀释, 解读应与 full/ctx 并置对照而非孤立断言。IDF 加权表跨三轨共享同一份逐词逆文档频率, 使 ss 轨与另两轨在词权重维度严格可比。

<!-- rendered-citations:begin -->
Brodeur, A., Mikola, D., Cook, N., et al. (2026). Reproducibility and robustness of economics and political science research. Nature, 652(8108), 151-156. https://doi.org/10.1038/s41586-026-10251-x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sheridan, P., Ahmed, Z., & Farooque, A. A. (2025). A Fisher's Exact Test Justification of the TF–IDF Term-Weighting Scheme. The American Statistician, 80(1), 146-156. https://doi.org/10.1080/00031305.2025.2539241
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
<!-- rendered-citations:end -->
