---
family_id: F268
novelty_exempt_rationale: "停刊稳健性(exc_)×词典(loughran)×规则消融(degonly)三重派生变体家族, 其测度定义依据母族 Loughran & McDonald 词典文献与规则消融梯子既有方法论, 非独立新构念, 无需追新文献"
columns:
- exc_loughran_score_degonly_ctx
- exc_loughran_score_degonly_full
- exc_loughran_score_degonly_ss
unit: 无量纲词典净得分 (自归一化, 值域约 [-1, 1]); bank-year 级排除停刊媒体后的算术均值
formula: "exc_loughran_score_degonly_{track} = mean_{i ∈ bank-year, _is_ceased_media_i = 0} loughran_score_degonly_{track, i}; loughran_score_degonly = L&M(2011) 中文主译词典的正负词净得分, 仅激活程度副词强化规则 (否定翻转与转折规则关闭)"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性 C.4 动态发现聚合)
upstream:
- 22_tone_words.parquet (loughran_score_degonly_full / _ctx / _ss 文章级列)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 40_panel_export_main 内 detect_defacto_cessation 产 _is_ceased_media 覆盖退出代理
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
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
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
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
本家族刻画的是一条"停刊稳健性 × 词典法情感 × 规则消融 × 文本三轨"四重交叉的银行-年度情感强度测度。列名可拆为四段各自独立的语义单元: 前缀 exc_ 表示该聚合仅在剔除疑似退出覆盖媒体后的存活样本上计算 (cessation-robust 子集); 中段 loughran 指第六部情感词典, 即 Loughran 与 McDonald (2011) 在会计与金融文本分析中确立的正负词表的中文主译版本 (在本仓库前缀别名体系中记为 loughran, 权威源为 tone_words 的词典别名映射); score 表示取该词典的正负词净得分 (自归一化的连续信号) 而非经进一步聚合的 tone 倾向列; degonly 是三条语言学规则的消融变体之一, 只激活程度副词强化规则, 关闭否定翻转与转折规则。三个成员列 exc_loughran_score_degonly_full / _ctx / _ss 分别落在标题-全文、标题-实体窗口、标题-银行与金科同句共现三条文本轨上。构念上, 它回答的是: 在把疑似停止报道该银行的媒体保守剔出样本之后, 存活媒体对该银行的报道在"仅计程度副词、不做否定与转折修正"这一保守语言学口径下, 呈现出多强的正负情感净倾向。数据来源链条起于原始中文银行/金科新闻语料, 经共现硬过滤与三轨文本物化, 在词典情感阶段生成文章级 loughran_score_degonly_{track}, 再在面板导出阶段的停刊稳健性模块内, 对每个银行-年度、在存活媒体子集上取算术均值。

【方法学与计算】
计算分两层。文章层由词典情感阶段产出 loughran_score_degonly_{track}: 对每篇文章的对应轨文本 (content_full / content_ctx / content_ss) 用 jieba 冻结分词后匹配 Loughran 中文词表的正词与负词, 在只应用程度副词强化规则的口径下累计正负贡献, 得到一个自归一化的净得分。所谓 degonly, 是把否定翻转、程度副词、转折三条规则做全 powerset 消融后取"仅程度副词"这一格: 即当词表命中词前存在程度副词 (如很、极、非常) 时按规则放大其权重, 但不因否定词前缀翻转极性, 也不因转折连词重分配句内权重。该变体与同族其余六个非-full 消融变体 (raw、negonly、advonly、negdeg、negadv、degadv) 以及全规则 full 口径高度共线, 属自归一化、非可加分解的规格稳健性梯子, 审计口径要求报告变体间相关而非把它们并入同一线性分解式。面板层的 exc_ 聚合发生在 attention_media 的停刊稳健性模块: 先由覆盖退出检测 (de-facto cessation proxy) 标注 _is_ceased_media, 该标注以"话题覆盖退出"为报纸停刊的保守代理而非经证实的出版停刊; 随后在存活子集 df_alive (\_is_ceased_media 为 0) 上按 target_bank 与 year 分组, 对文章级 loughran_score_degonly_{track} 取均值, 列名前缀 exc_。零文章的银行-年度对比例类与情感类列按契约保持 NaN 而非零填 (仅计数类如 n_articles_exc 才 Σ over ∅ 归零)。留篇门控口径遵循 full-only 铁律 (2026-06-29): 一篇报道是否计入银行金科报道宇宙只看 full 轨的 llm 判定, ctx 与 ss 轨在此之下降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, per-track 列照算。三条文本轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁把三轨混进同一 over-identified 的 Hansen J 过度识别检验; 同理 exc_ 存活子集与全样本口径、以及规则消融梯子的各格之间也遵守同一并排铁律。

【文献定位】
词表本体锚定于 Loughran 与 McDonald (2011) 发表于 Journal of Finance 的经典工作, 该文以"When is a liability not a liability"为题, 证明通用情感词典 (如 Harvard-IV) 在金融文本上系统性误分类, 并给出针对财经语域重构的正负词表, 是本家族 loughran 前缀词典的直接方法学源头。其后 Loughran 与 McDonald (2016) 在 Journal of Accounting Research 的综述、以及 Loughran 与 McDonald (2020) 在 Annual Review of Financial Economics 的回顾, 系统梳理了词典法在会计金融文本分析中的适用边界与规格敏感性, 为本家族把否定/程度/转折三规则做消融梯子、并把结果作为规格稳健性而非主效应提供了方法论依据。词典法在跨语域移植时的语言特异性问题, 由 Du 等 (2022) 在 Review of Finance 针对中文财经情感词典给出系统论证, 支撑本仓库采用中文主译词表而非直接套用英文原表的选择。词典法相对机器学习法的相对效度, 由 Frankel、Jennings 与 Lee (2022) 在 Management Science 做过直接比较, 为本仓库把词典、LLM、BERT 三法并置为互为稳健性轨提供先例。程度副词与转折等句法规则对词典情感的调制机制, 可追溯到 Taboada 等 (2011) 在 Computational Linguistics 提出的 lexicon-based 方法框架, 是 degonly 变体所激活的程度强化规则的规范出处。中文细粒度情感词典的最新构造 (Ma、Zhang 与 Zhang, 2025) 则为该测度族的持续可比性提供了当代参照。

## VAR: exc_loughran_score_degonly_ctx

【变体差分】
本列是 exc_loughran_score_degonly 家族在 ctx 轨上的成员。相对家族共享的 exc/loughran/score/degonly 四段语义, 本列的唯一区分维度是文本轨: ctx 轨的输入文本为 content_ctx, 即标题 prepend 之后再拼接以银行实体为中心的上下文窗口 (实体两侧若干句), 而非 full 轨的整篇正文。因此本列度量的是"在只看与目标银行实体邻近的句子、且仅剔除停刊媒体、且仅计程度副词规则"这一收窄口径下的 Loughran 净情感。相对 full 轨, ctx 轨过滤掉了远离银行实体的段落噪声, 使情感信号更贴近对该银行的直接评述, 代价是牺牲全文语境。轨道口径上, ctx 是 conditional-on-full 的稳健性测度轨: 其行宇宙是 full 轨留篇集的子集 (留篇门控 full-only, 2026-06-29), 一篇报道是否计入银行金科报道宇宙只由 full 轨判定, ctx 列在该子集上照常逐篇计算并在存活媒体子集上取银行-年度均值。degonly 规则口径与 full 轨完全一致 (仅程度副词强化, 无否定翻转、无转折重分配), 使得 ctx 与 full 之间的差异可干净归因于文本轨而非规则差异。本列与 exc_loughran_score_degonly_full、exc_loughran_score_degonly_ss 互为稳健性、不分主次, 三轨各自 just-identified 并排进入自回归, 严禁把三轨同时塞进同一 over-identified 的 Hansen J 过度识别检验; 同理本列与全样本 (非 exc) 口径、以及规则消融梯子的其余各格亦属并排稳健性关系。零文章银行-年度按情感类契约保持 NaN。

## VAR: exc_loughran_score_degonly_full

【变体差分】
本列是 exc_loughran_score_degonly 家族在 full 轨上的成员, 也是三轨中口径最完整、承担留篇门控职能的一轨。full 轨的输入文本为 content_full, 即标题 prepend 之后拼接整篇正文, 覆盖全文语境。因此本列度量的是"在整篇报道语境下、仅剔除停刊媒体、仅计程度副词规则"这一口径下的 Loughran 净情感。full 轨在本仓库中具有特殊地位: 留篇门控是 full-only (2026-06-29), 即一篇报道是否被判为"一篇银行金科报道"只看 full 轨的 llm 判定, 因此 full 轨的留篇集是 ctx/ss 两轨行宇宙的上界; 但就本词典家族而言, full 轨仍只是三条互为稳健性轨中的一条测度轨, 其规则口径 (仅程度副词) 与 ctx/ss 严格一致, 从而三轨间差异可干净归因于文本范围。degonly 变体相对全规则 full 口径、以及 raw/negonly/advonly/negdeg/negadv/degadv 等其余消融格, 属自归一化、高度共线的规格稳健性梯子, 只报变体间相关而不做可加分解。exc_ 前缀表明该列在覆盖退出代理剔除疑似停报媒体后的存活子集上聚合, 用于对情感面板系数做停刊稳健性检验。本列与 ctx、ss 两轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J。零文章银行-年度按情感类契约保持 NaN 而非零填。

## VAR: exc_loughran_score_degonly_ss

【变体差分】
本列是 exc_loughran_score_degonly 家族在 ss 轨上的成员。ss 轨的输入文本为 content_ss, 即标题 prepend 之后拼接"目标银行与金科词在同一句±N 句窗内共现"的句子集合, 是三轨中范围最窄、语义定向性最强的一轨: 它只保留银行与金融科技概念真正被放在一起讨论的文本片段, 从而度量"在银行谈及金科的直接语境下、仅剔除停刊媒体、仅计程度副词规则"的 Loughran 净情感。ss 轨的回退语义严格镜像 ctx 轨: 当某篇报道不存在银行与金科的同句共现时, content_ss 优雅降级为全文正文 body, 并置 ss_is_fallback 为 True, 与 ctx 共享 n_articles 分母; 若金科自动机词表整体缺席则 ss_is_fallback 全 True 优雅降级。轨道口径上 ss 同为 conditional-on-full 的稳健性测度轨, 行宇宙受 full-only 留篇门控约束 (2026-06-29), 是 full 留篇集的子集。degonly 规则口径 (仅程度副词强化, 无否定翻转、无转折) 与 full/ctx 完全一致, 使三轨差异可干净归因于文本范围。本列与 exc_loughran_score_degonly_full、exc_loughran_score_degonly_ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁三轨混入同一 over-identified 的 Hansen J 过度识别检验; 与全样本口径及消融梯子其余各格同属并排稳健性关系。因 ss 轨的共现约束最严, 在盘上浅面板 (T=2) 上该轨极易出现零方差或大量回退, 属预期的退化行为而非缺陷, 生产深面板 (T=18) 上信号方差恢复正常。零文章银行-年度按情感类契约保持 NaN 而非零填, 以免与兄弟计数列 n_articles_exc 的零值口径混淆。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
