---
family_id: F232
novelty_exempt_rationale: "该家族是 bian_2021 词典情感的双重衍生/消融变体 (exc_ 前缀=剔疑似停刊媒体的稳健性子样本聚合, advonly=规则消融梯度中仅保留转折规则的技术变体), 非独立新构念, 其测度定义的学术依据已在正文引文的母族词典 (Bian et al. 2021) 与规则消融方法学文献 (Taboada et al. 2011) 中给出。"
columns:
- exc_bian_2021_score_advonly_ctx
- exc_bian_2021_score_advonly_full
- exc_bian_2021_score_advonly_ss
unit: 情感得分 (无量纲, bank-year 均值, 值域约 [-1, 1])
formula: "exc_bian_2021_score_advonly_{track} = mean over articles with _is_ceased_media==0 of bian_2021_score_advonly_{track}, 按 (target_bank, year) 分组; bian_2021_score_advonly = Bian 等 (2021) 词典加权自归一化净情感 = Σ(signed final weights) / Σ|final weights| (tone_words.py::_compute_sentiment_with_rules 的 _abl_norm), 仅施加转折(adversative)规则并对转折从句权重施加 ADVERSATIVE_BOOST=1.5, 否定翻转与程度副词两规则关闭; 分母为加权 Σ|final| 而非裸 (pos+neg) 词计数, (pos-neg)/(pos+neg) 仅为无加权情形的简化近似"
producer: news_process/pipeline/panel/attention_media.py (exc_* 剔停刊动态发现聚合 C.4); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores
upstream:
- 22_tone_words.parquet (bian_2021_score_advonly_{full,ctx,ss})
- 40_panel_export_main (attention_media 剔疑似停刊媒体后重聚合)
citations:
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.48550/arXiv.2603.20237
  type: arxiv
  authors: Muhammad, T.
  year: 2026
  title: "Temporal coverage bias in financial panel data: A coverage-aware structuring framework with evidence from the Dhaka Stock Exchange"
  venue: arXiv
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
- doi: "10.1093/llc/fqae013"
  type: "journal"
  authors: "Venglařová, K., & Matlach, V."
  year: 2024
  title: "Beyond content: discriminatory power of function words in text type classification"
  venue: "Digital Scholarship in the Humanities"
  vol: "39"
  issue: "2"
  pages_or_artno: "765-789"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是, 在把疑似退出银行-金融科技话题覆盖的媒体来源保守剔出样本之后, 按 Bian 等 (2021) 中文财经情感词典对某银行某年报道重新计算的净情感得分。它不是一条独立的新构念, 而是家族 bian_2021 词典情感的一条稳健性孪生轨: 前缀 exc 的含义是"剔除疑似停刊 (exclude ceased media)", 词干 bian_2021_score 指 Bian 等 (2021) 词典的净情感打分, 后缀 advonly 指该打分只施加了转折 (adversative) 一条语言学规则。三列分别对应 full/ctx/ss 三条文本轨。构念动机来自媒体覆盖的幸存者偏差: 当部分地方性或专业性媒体在样本期内逐步退出对目标银行金融科技议题的报道时, 若不加处理, 银行-年度层面的情感聚合会向持续存活的媒体口径倾斜, 从而系统性污染以媒体情感为核心解释变量的面板估计, 并进一步扭曲以媒体来源结构为基础的 Bartik 型工具变量。当本地报纸或专业媒体退出对目标议题的持续报道时, 会在该议题上形成局部监督与信息真空, 使存活媒体的口径不成比例地主导银行-年度层面的情感聚合, 这为把"覆盖退出"作为停刊的保守代理、并将疑似退出媒体剔出样本以检验幸存者偏差提供了识别层面的动机。需要诚实披露的是, 本实现以"话题覆盖退出 (topic exit)"作为停刊的保守代理而非经证实的报纸停刊: 媒体可能仍在正常出版, 只是不再覆盖该银行的金融科技议题, 因此本族三列应解读为"疑似退出覆盖媒体"口径下的稳健性度量, 不可在正文中表述为严格的出版停刊口径。

【方法学与计算】
计算分两层。文章层由 tone_words.compute_dict_scores 产出 bian_2021_score_advonly_{track}: 先用 Bian 等 (2021) 词典在每篇报道的对应文本轨上匹配正负情感词并按规则赋加权权重, 再由 _compute_sentiment_with_rules 计算加权自归一化得分, 即带符号的最终权重之和除以最终权重绝对值之和 (signed Σfinal 除以 Σ|final|, 源码内记为 _abl_norm), 分母是加权后的权重绝对值和而非裸正负词计数, 因此常写作的 (pos 减 neg) 除以 (pos 加 neg) 仅是无加权情形下的简化近似; 其中 advonly 变体对应规则消融梯度里的 (否定关闭, 程度关闭, 转折开启) 组合, 只保留转折从句边界处理并对转折从句施加 ADVERSATIVE_BOOST=1.5 的加权, 而关闭否定翻转与程度副词放大。面板层由 attention_media 在 40_panel_export_main 步骤内完成: 先经覆盖退出检测 detect_defacto_cessation 得到疑似停刊媒体集合 (数据驱动的末次覆盖年早于样本末年减阈值且报道数达门槛, 再与 NPPA 出版状态交叉验证, 但未经证实的 suspected 全量进入剔除集), 对每篇报道打上 _is_ceased_media 标记; 随后在剔除停刊媒体的存活子集上, 按 (target_bank, year) 分组对文章层得分取算术均值, 经动态发现循环物化为 exc_ 前缀列。对零报道或全停刊的银行-年度, 该情感类列按契约保持缺失而不做零填 (只有计数类 n_articles_exc 才零填), 以免把"无观测"混淆为"中性"。规则消融梯度是自归一化、非可加分解的: advonly 与家族内 raw/negonly/degonly/negdeg/negadv/degadv/全规则各变体在实证上高度共线, 应报告相关性而非并入同一可加分解式。

【文献定位】
词典源 Bian 等 (2021) 构建了面向会计与金融文本的中文财经情感词典, 是本族打分的词表基础。方法学上, Taboada 等 (2011) 系统论证了基于词典的情感分析中否定、程度与转折等语言学规则的作用, 是 advonly 只保留转折规则这一消融设计的直接依据。Du 等 (2022) 在 Review of Finance 上强调中文财经情感测度的语言与领域特异性, 为多词典并置与规则敏感性检验提供了顶刊层面的构念锚。Frankel 等 (2022) 在 Management Science 上比较词典法与机器学习情感, 论证不同测度并置互为稳健的范式, 支持本族作为词典轨稳健性列的定位。van Atteveldt 等 (2021) 则对词典、众包与机器学习情感的效度做了对照评估, 提示词典法在细粒度语境下的局限。剔停刊设计的时序覆盖偏差维度另可参照 Muhammad (2026) 关于金融面板时序覆盖偏差的框架。需强调三轨口径铁律: full/ctx/ss 三条文本轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混入同一 over-identified 的 Hansen J 检验; 同理剔停刊轨与全样本轨、以及 advonly 与其余规则消融变体, 亦属规格稳健性并置而非可加叠加。留篇门控沿用 full-only 口径 (2026-06-29): 某篇是否计入一篇银行金融科技报道只看 full 轨的 llm_verified_full, ctx/ss 为 conditional-on-full 的从属稳健轨。 就剔停刊口径的现实动机, Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 说明媒体退出并非无害的样本损耗, 而是有经济后果的样本组成变化, 这正锚定本族先剔除疑似退出覆盖媒体、再做银行-年度聚合这一环节; 迁移边界须诚实标明: 该文停刊判定取自外部事件数据、DV 为本地股票交易活动且以停刊作识别冲击, 而本族 ceased_set 由 detect_defacto_cessation 自语料内部推断 (confirmed ∪ suspected), 属保守代理而非严格停刊事实, 仅作稳健性子样本之用, 且该文为工作论文尚未经同行评审。就 advonly 单留转折规则的构念前提, Venglařová 与 Matlach (2024) 实证显示连词一类功能词在文本类型判别上具有独立于内容词的信息量, 提示转折/逆接标记本身是一条值得单独计量的语言维度; 但该文任务为文本类型分类、语料非中文金融新闻, 且不区分转折连词与其他功能词类, 更未在词典内部做规则消融, 故仅在构念层为把转折单列成一条可开关的臂提供动机, 不构成 ADVERSATIVE_BOOST 取值的直接依据。
## VAR: exc_bian_2021_score_advonly_ctx

【变体差分】
本列为剔疑似停刊媒体后、Bian 等 (2021) 词典 advonly 变体在 ctx 实体窗轨上的银行-年度均值。ctx 轨的文本口径是标题 prepend 后拼接目标银行与金融科技实体上下文窗口内的内容 (content_ctx), 由 stage 14 ctx_materializer 物化; 相对 full 全文轨, 它把打分文本收窄到实体邻近语境, 用以剥离与银行金融科技议题无关的段落噪声。与本家族其余两列的唯一差别是文本轨: 三列共享完全相同的 advonly 规则组合 (仅转折开启, 否定与程度关闭)、相同的 Bian 等 (2021) 词表、相同的自归一化净情感公式, 以及相同的剔停刊聚合口径 (只对 _is_ceased_media 为 0 的存活媒体报道按 target_bank 与 year 取均值), 差别仅在于对哪一段文本计数正负情感词。ctx 轨在早期试跑 T=2 小样本上可能因实体窗覆盖稀疏而与 full 轨高度共线甚至局部退化, 在生产期 T=19 全量语料下才充分体现其收窄语境的稳健性价值。相对 ss 同句轨, ctx 轨的语境收窄更宽松: 它取的是实体上下文窗口而非严格同句共现, 因而在召回与语境纯度之间处于 full 与 ss 之间的中间档位, 三轨由此构成一条由宽到严的文本语境阶梯, 对读者判断主结果对语境口径的敏感性提供并排参照。advonly 只保留转折规则意味着本列对"但是、然而"等语义反转连词后的分句会做边界处理, 而对否定与程度副词不做翻转或放大, 因此与家族全规则轨相比, 本列刻意隔离出转折规则的单独贡献。按三轨铁律, 本列与 full、ss 两列各自 just-identified 并排, 互为稳健性、不分主次, 禁混入同一 over-identified Hansen J; 情感类列在零报道或全停刊银行-年度保持缺失不零填, 只有计数类 n_articles_exc 才按契约零填并恢复整型。

## VAR: exc_bian_2021_score_advonly_full

【变体差分】
本列为剔疑似停刊媒体后、Bian 等 (2021) 词典 advonly 变体在 full 全文轨上的银行-年度均值, 是本家族的 canonical 文本轨。full 轨的文本口径是标题 prepend 后拼接报道全文正文 (content_full), 覆盖最完整的语义信息, 也是留篇门控 (full-only, 2026-06-29) 判定"一篇银行金融科技报道"的唯一依据轨。相对 ctx 实体窗轨与 ss 同句轨, full 轨不做任何语境收窄, 因此在噪声与召回之间偏向高召回一端。与本族另两列的唯一差别仍是文本轨: 三列共享同一 advonly 规则组合 (仅施加转折从句边界处理, 关闭否定翻转与程度副词放大)、同一 Bian 等 (2021) 词表与自归一化净情感公式, 以及同一剔停刊聚合口径。剔停刊的语义是: 先由覆盖退出检测把末次覆盖年过早且报道量达门槛的媒体标为疑似停刊 (含未经 NPPA 证实的 suspected 全量), 再在存活媒体子集上按 target_bank 与 year 取文章层得分均值; 因此本列相对全样本的同名情感列, 净变化只反映"剔除疑似退出媒体"这一保守剔除, 用于检验主结果对媒体幸存者偏差的敏感性。按三轨铁律与规则消融铁律, 本列与 ctx、ss 及各规则变体各自 just-identified 并排、互为稳健性, 禁混入同一 over-identified Hansen J。

## VAR: exc_bian_2021_score_advonly_ss

【变体差分】
本列为剔疑似停刊媒体后、Bian 等 (2021) 词典 advonly 变体在 ss 同句轨上的银行-年度均值。ss 轨的文本口径是标题 prepend 后, 取目标银行与金融科技词在同一句子内共现、并沿正负若干句窗展开的超级文档 (content_ss), 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制 (默认 1)。它是三轨中语境最严的一轨, 只对银行与金融科技真正同句共现处的文本打分, 因而最贴近"银行的金融科技叙事"这一目标构念, 代价是召回最低。ss 轨遵循镜像 ctx 的优雅回退语义: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 与 ctx 共享 n_articles 分母; 当金融科技 AC 词典为空时相应 fallback 标记全真而优雅降级。与本族另两列的唯一差别依旧是文本轨: 三列共用同一 advonly 规则组合、Bian 等 (2021) 词表、自归一化净情感公式与剔停刊聚合口径。早期试跑 T=2 上 ss 轨因同句共现稀疏可能大面积回退乃至局部零方差, 属预期退化, 生产期 T=19 方充分显现。需要留意的是 ss 轨的超级文档由 content_ss 原样拼接而成, 已内嵌 prepend 的标题作为第 0 句, 因此不再单独走标题通道以免双标题污染; 这一点与 ctx、full 两轨在文本组织上一致而在语境半径上更严。advonly 规则在三轨间完全一致, 本列与 full、ctx 的差别纯粹来自对哪一段文本统计 Bian 等 (2021) 正负情感词, 而非规则、词表或聚合口径的差异。按三轨铁律, 本列与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; 情感类列零报道或全停刊时保持缺失不零填, 与全样本同名列相比其净变化只反映剔除疑似退出媒体这一保守剔除。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Muhammad, T. (2026). Temporal coverage bias in financial panel data: A coverage-aware structuring framework with evidence from the Dhaka Stock Exchange. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2603.20237
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
<!-- rendered-citations:end -->
