---
family_id: F189
columns:
- dict_avg_idf_tone_sum_ctx
- dict_avg_idf_tone_sum_full
- dict_avg_idf_tone_sum_ss
unit: 语调得分 (无量纲, 约 [-1, 1]; 文章级 IDF 加权极性经 sum-pooling 后落到 bank-year)
formula: "dict_avg_idf_tone_sum{track} = mean over d in DICT_NAMES of ( d_idf_tone_sum{track} ); 其中 d_idf_tone_sum 为第 d 部词典在 IDF 加权下、以 sum-pooling (词数加总先做比再聚合) 口径算出的银行-年语调"
producer: news_process/pipeline/panel/geography.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (各词典 d_idf_tone_sum{track})
citations:
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
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
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  issue: ""
  pages_or_artno: 125739
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
new_dois: []
---

## CORE

【构念与来源】
本家族 dict_avg_idf_tone_sum 是词典法情感测度的一个"跨词典综合、IDF 加权、sum-pooling"三重限定的银行-年语调变量。它把项目内多部中文金融情感词典各自算出的 IDF 加权语调 (per-dict d_idf_tone_sum) 在词典维度上取等权算术平均, 得到一个不依赖任一单部词典特异性的综合极性指标。构念上它回答的问题是: 在某银行-年的金融科技相关报道语料中, 情感基调整体偏正还是偏负, 且当每个情感词按其"稀有度/区分度"加权、并以文章体量加权聚合时, 这一基调有多强。数据来源是本项目 stage 22 (22_tone_words) 落盘的逐词典语调列, 其上游文本轨由 stage 14 (14_materialize_ctx) 物化的 content_full / content_ctx / content_ss 三轨提供; 家族生产函数是 pipeline/panel/geography.py 中对 DICT_NAMES 逐词典求 _safe_mean 的综合步骤 (源码摘录第 233 行, 与 dict_avg_idf_tone 平均语调综合成对落列)。_safe_mean 对缺列优雅返回 NaN, 因此当某词典的 idf_tone_sum 源列在 golden 重生前尚未落盘时, 综合列不会崩而是退化为可用词典上的均值。

【方法学与计算】
理解本家族需拆开三个限定词。其一是"IDF 加权": 情感极性不再对命中的每个情感词等权计数, 而是按该词在语料中的逆文档频率赋权, 使罕见、区分度高的情感词贡献更大权重, 高频泛化的情感词贡献被压低。这一思路承袭文本即数据 (text-as-data) 中 tf-idf 加权的经典做法, 意在抑制"套话式"高频情感词对基调的稀释, 提升语调对真实语义偏向的敏感度; García, Hu 与 Rohrer (2023) 关于金融情感词"色彩"随语境与频率而异的发现, 以及 Algaba 等 (2020) 对情感计量方法族的综述, 都支撑对情感词做频率敏感加权而非裸计数。其二是"sum-pooling"(对应列名后缀 _sum): 与逐文章先算比值再对文章等权取均的口径 (无 _sum 的 _tone) 不同, sum-pooling 先把银行-年内所有文章的加权正负词贡献分别加总, 再在加总量上做一次极性归一, 等价于把该银行-年的全部报道视作一篇"超级文档"、按文章体量 (词数) 隐式加权。长文因携带更多情感词而对综合基调影响更大, 因此 sum-pooling 相对 mean-of-ratios 更贴近 Holzman, Miller 与 Twedt (2023) 所强调的"媒体信息量加权"的读者感知口径。其三是"跨词典综合": 项目并用多部中文金融情感词典 (含 Du 等 (2022) 的领域特化词典、Bian 等 (2021) 词典及若干通用/金融词典), 各词典对同一文本给出的语调因收词与极性标注差异而不完全一致; dict_avg_idf_tone_sum 对这些逐词典结果取等权平均, 目的不是构造"更准的单一真值", 而是提供一个词典选择无关 (dictionary-agnostic) 的稳健综合, 削弱任一词典构造选择对结论的驱动力。Frankel, Jennings 与 Lee (2022) 关于词典法与机器学习法在披露情感上各有系统偏差的证据, 正是本项目坚持多词典综合而非单点押注的理由。

【文献定位】
词典法情感测度是金融文本分析的方法学基石。García, Hu 与 Rohrer (2023) 发表于 Journal of Financial Economics 的研究表明, 金融语境中情感词的极性并非固定, 其"色彩"随使用频率与上下文漂移, 这直接为 IDF 频率加权 (压低泛化高频词、抬升区分性词) 提供了构念依据。Frankel, Jennings 与 Lee (2022, Management Science) 系统比较了词典法与机器学习法的披露情感刻画, 指出两类方法各自携带可辨识的系统偏差, 因而单一方法不可独断——这是本项目同时维护词典法、LLM 三家投票与 BERT 三模型三条互为稳健性测度线, 并在词典法内部做跨词典综合的方法论基础。Holzman, Miller 与 Twedt (2023, The Accounting Review) 论证媒体情感需按信息权威与体量加权方能刻画其对市场的规训作用, 呼应 sum-pooling 的体量加权口径。中文场景下, Du 等 (2022, Review of Finance) 构建的领域特化中文金融情感词典与 Ma, Zhang 与 Zhang (2025) 的细粒度投资者情感词典 (CN-FSD), 是本家族跨词典综合的重要成分词典来源; Barbaglia 等 (2025) 与 Algaba 等 (2020) 则从经济文本 lexicon-based 方法与情感计量方法族两个层面, 为词典法在面板计量中的合法性与稳健性叙事提供背书。需要强调的是, 本家族的三轨结构 (full/ctx/ss) 遵循项目铁律: full 轨=标题 prepend + 全文正文, ctx 轨=标题 + 银行实体窗口, ss 轨=标题 + 银行与金融科技同句共现窗 (ss 无同句共现时回退为全文 body, 镜像 ctx 回退公理, 共享 n_articles 分母); 留篇门控为 full-only 口径 (2026-06-29), 即某银行-年是否计为一篇银行金科报道只由 full 轨 LLM 判定决定, ctx/ss 降为 conditional-on-full 的测度/稳健性轨。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_idf_tone_sum_ctx

【变体差分】
本列是 dict_avg_idf_tone_sum 家族的 ctx 轨实例。它与 full、ss 两轨的唯一差别在于底层文本轨: ctx 轨的文本源为 stage 14 物化的 content_ctx, 即标题 prepend 之后仅保留银行实体上下文窗口 (围绕目标银行实体出现位置的邻近句窗), 而非全文正文。因此本列度量的是"当只聚焦到明确围绕目标银行展开的那部分报道文本时"、经 IDF 加权与 sum-pooling 聚合、再对多部词典取均后的综合语调。相对 full 轨, ctx 轨剥离了与目标银行关系较远的旁支段落, 语调更集中于银行主体, 但也因文本缩短而更易受少量情感词主导、方差结构不同。计算链路与家族一致: 逐词典的 d_idf_tone_sum_ctx (stage 22 落盘) 先在文章级以 IDF 频率权做加权极性、以 sum-pooling 按体量加总归一, 再由 geography.py 在 DICT_NAMES 上 _safe_mean 综合。留篇门控为 full-only: 本 ctx 列的行宇宙是 full 留篇集的子集, 属 conditional-on-full 的测度轨, 定位为对 full 轨主测度的稳健性并排, 而非独立的判篇依据。铁律: ctx 与 full、ss 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J; 亦不得把 ctx 轨语调与 full 轨语调当作同一构念的两个工具变量塞进过度识别检验。dev 语料 (早期试跑 T=2) 上 ctx 轨可能因文本极短而出现零方差退化, 属预期现象, 生产语料 (T=19) 下恢复正常。

## VAR: dict_avg_idf_tone_sum_full

【变体差分】
本列是 dict_avg_idf_tone_sum 家族的 full 轨实例, 也是家族在留篇门控意义上的 canonical 轨。full 轨的文本源为 stage 14 物化的 content_full, 即标题 prepend 之后拼接完整正文, 覆盖整篇报道而非任何实体窗口子集。因此本列度量的是"以整篇银行金科报道全文为口径"、经 IDF 频率加权与 sum-pooling 体量聚合、再跨多部中文金融情感词典取等权均后的综合语调。它是本家族信息最完整的一轨: 保留全文意味着长文携带的全部情感词都进入 sum-pooling 的加总, 体量加权效应最充分, 与 Holzman, Miller 与 Twedt (2023) 强调的读者实际接收信息量口径最贴合。计算链路: 逐词典 d_idf_tone_sum_full 在文章级完成 IDF 加权与 sum-pooling 归一 (stage 22), 再由 geography.py 在 DICT_NAMES 上 _safe_mean 综合成本列。按项目 full-only 门控铁律 (2026-06-29), 某银行-年是否计为一篇银行金科报道只由 full 轨 LLM 判定决定, 故 full 轨是三轨中唯一参与留篇判定的轨, ctx/ss 均是 conditional-on-full 的稳健性并排轨。尽管如此, full 轨在本家族内部与 ctx、ss 仍是互为稳健性、不分主次的并排关系 (canonical 仅指门控意义, 非"更真"意义), 三轨各自 just-identified、严禁混进同一 over-identified Hansen J。本列亦不得与同家族的 dict_avg_idf_tone_full (平均语调综合, 无 _sum) 当作同一构念的双工具塞入过度识别: _sum 与非 _sum 是聚合口径 (体量加权 vs 文章等权) 的规格稳健性并排, 高度共线但语义不同, 报稳健性而非并入同式。

## VAR: dict_avg_idf_tone_sum_ss

【变体差分】
本列是 dict_avg_idf_tone_sum 家族的 ss (same-sentence) 轨实例。ss 轨的文本源为 stage 14 物化的 content_ss, 即标题 prepend 之后仅保留目标银行与金融科技词在同一句内共现 (以 config 的 ss_sentence_radius 定义的同句±N窗, 默认 1) 的最窄文本轨。因此本列度量的是"当把文本收窄到银行与金科真正同句同现的语境"时、经 IDF 加权与 sum-pooling 聚合、再跨多词典取均的综合语调, 是三轨中语义最聚焦、也最稀疏的一轨: 它刻意排除了银行与金科分散在不同句子、仅在篇章层面共现的弱关联文本, 只保留强共现语境的情感基调。ss 轨遵循镜像 ctx 的回退公理: 当某文章不存在银行与金科的同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则 ss_is_fallback 全 True 优雅降级。计算链路与家族一致: 逐词典 d_idf_tone_sum_ss 在文章级完成 IDF 加权与 sum-pooling (stage 22), 再由 geography.py 在 DICT_NAMES 上 _safe_mean 综合。留篇门控同样为 full-only, 本 ss 列行宇宙是 full 留篇集子集, 属 conditional-on-full 稳健性并排轨。铁律: ss 与 full、ctx 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J; ss 的强共现口径与 ctx 的实体窗口口径是两种不同的文本收窄判据, 不得互相复用或当作同一测度的重复。dev 语料 (早期试跑 T=2) 上 ss 轨因文本极窄可能出现零方差或大量回退, 属预期退化, 生产语料下恢复区分度。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
<!-- rendered-citations:end -->
