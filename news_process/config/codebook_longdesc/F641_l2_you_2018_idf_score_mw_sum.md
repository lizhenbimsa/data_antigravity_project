---
family_id: F641
columns:
- you_2018_idf_score_mw_sum_ctx
- you_2018_idf_score_mw_sum_full
- you_2018_idf_score_mw_sum_ss
unit: 无量纲得分 (逆文档频率加权词计数之和; 未除以文章长度, 量级随文章词数与词典命中密度变化)
formula: 'you_2018_idf_score_mw_sum{track} = Σ_{i∈bank-year} (you_2018_idf_score{track}_i × media_authority_weight_i); 其中 you_2018_idf_score{track}_i 是阶段 22 `tone_words.py` 对 you_2018 词典 IDF 加权情感打分 (build_idf_weights 产出 Winsorize 归一化 IDF 权重 × 词典基分 ±1.0, 经否定翻转/程度副词/转折语言学规则调整), media_authority_weight_i 是阶段 40 `compute_media_authority_weights` 依据 `config/media_weights.json` 静态权威性评分 (10-100, 归一化至 raw_weight/mean(raw_weight)) 产出的媒体权威性加权乘子 (Holzman, Miller & Twedt 2023, The Accounting Review, Appendix A Outlet Impact Media Sent 加权方法的简化替代实现); mw 后缀标记该列走"媒体权威性加权 (media authority weight)"路径, 与同一情感基分并排的另外两条加权路径为 `_hw` (herd-decay 羊群衰减权重) 与 `_w` (mention-density 提及密度权重), 三条加权路径互为稳健性并排, 皆各自 just-identified, 严禁混入同一 over-identified Hansen J 估计式; 与罕见词频次 cutoff 消融梯度 (`rare_word_ratio_c{2,5}` 等, 另族) 无关。'
producer: pipeline\panel\runner.py (文章级 `{d}_idf_score_mw{track}` = `{d}_idf_score{track}` × `media_authority_weight`, runner.py:797-821; media_authority_weight 由 `compute_media_authority_weights` 产出) ; pipeline\panel\encode.py (bank-year 聚合 `{d}_idf_score_mw_sum{track}` = groupby-sum, encode.py:1096) ; pipeline\sentiment\tone_words.py (文章级 `you_2018_idf_score{track}` 的产生, build_idf_weights / _build_idf_weighted_dict / _compute_sentiment_with_rules)
upstream:
- config/tone_dicts.json::you_2018
- config/media_weights.json (媒体权威性静态评分表)
- 14_materialize_ctx (content_full/content_ctx/content_ss 三轨文本物化)
- 21_tone_llms (llm_verified_full 留篇门控)
- 22_tone_words (you_2018 词典 IDF 加权情感打分)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: 'Word power: A new approach for content analysis'
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11-21
- doi: 10.1080/00031305.2025.2539241
  type: journal
  authors: Sheridan, P., Ahmed, Z., & Farooque, A. A.
  year: 2026
  title: A Fisher's exact test justification of the TF-IDF term-weighting scheme
  venue: The American Statistician
  vol: '80'
  issue: '1'
  pages_or_artno: 146-156
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
- doi: "10.1016/j.ememar.2024.101234"
  type: journal
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: "Emerging Markets Review"
- doi: "10.1002/fut.70090"
  type: journal
  authors: "Han, Q., Hsieh, P., & Zhang, L."
  year: 2026
  title: "Commodity Futures Report Text Sentiment and Returns"
  venue: "Journal of Futures Markets"
new_dois:
  - "10.1002/isaf.1549"
  - "10.1016/j.ememar.2024.101234"
  - "10.1002/fut.70090"
---

## CORE

【构念与来源】
本家族 (F641) 度量的是 bank-year 面板层面「You et al. (2018) 中文金融情感词典 × 逆文档频率 (IDF) 加权情感得分」在媒体权威性加权 (media-authority weighted) 口径下的分子求和量, 落盘 3 列, 对应 full/ctx/ss 三条文本轨。you_2018 词典来自 You, Zhang & Zhang (2018, Review of Financial Studies)《Who captures the power of the pen?》构建的中文金融情感词典 (positive 1,425 词 / negative 1,583 词, 另含 definite 388 词与 ambiguous 178 词两个非本家族消费的清晰度子集), 其原始设计理念是刻画媒体报道遣词造句所"捕获的笔锋力量"——同一客观事件, 措辞的情感极性选择本身携带增量信息, 这一构念传统在中文语境下由 You et al. (2018) 本土化确立, 是本仓库六部情感词典矩阵 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026) 中的一员, 各词典互为跨来源稳健性对照、不设主次。idf 中缀标记该列的情感基分不是 you_2018 词典的裸打分, 而是先经阶段 22 `build_idf_weights` 对语料逐词计算逆文档频率、再用该 IDF 权重对词典基分 (正面 +1.0 / 负面 −1.0) 逐词加权后打出的 `you_2018_idf_score`, 溯源自 Spärck Jones (1972) 的逆文档频率统计定义与 Jegadeesh & Wu (2013, Journal of Financial Economics)《Word power: A new approach for content analysis》确立的"word power" IDF 加权范式——简单的词典命中计数把每个情感词一视同仁, 但某些词在语料中信息密度更高、更具区分力, 用语料级逆文档频率对命中词加权可以把"稀有但有力"的措辞与"常见但泛化"的措辞区分开。mw 后缀标记该列走的是「media authority weight (媒体权威性加权)」路径——与同一 IDF 情感基分并排的另外两条加权路径为 `_hw` (herd-decay 羊群衰减权重) 与 `_w` (mention-density 提及密度权重); 三条加权路径互为稳健性并排, 皆各自 just-identified, 严禁混入同一 over-identified Hansen J 估计式。媒体权威性加权的构念依据是: 不同媒体的报道影响力不同 (权威财经媒体的措辞相较小报的同类措辞对市场/读者的实际影响力更大), 若不加区分地等权汇总, 会让高频但低影响力的小报报道稀释权威媒体的信号; 该权重在阶段 40 `compute_media_authority_weights` 中由 `config/media_weights.json` 收录的静态权威性评分 (量级 10-100, 按精确匹配→去括号归一化匹配→默认权重的三级匹配策略解析媒体名, 再做 raw_weight/mean(raw_weight) 归一化使量级约等于等权版) 产出, 是 Holzman, Miller & Twedt (2023, The Accounting Review) 论文中滚动回归估计媒体对股票周转率边际贡献、再按排名百分位加权方法 (Appendix A Outlet Impact Media Sent) 的简化静态替代实现——本项目未逐年重估该滚动回归, 而是采用固定的媒体权威性评分表, 使用者在解读跨年份差异时应留意这一"静态权重近似"的简化假设, 与随时间变化的媒体影响力真实结构可能存在偏离。`sum` 后缀表示该列是逐篇 IDF×媒体权威性加权乘积在 bank-year 分组内求和的中间分子列 (非最终均值), 供下游除以对应权重加总分母后得到最终的媒体权威性加权 IDF 语调均值; 落盘保留供审计追溯与自定义聚合复现, 其量级同时受该银行-年报道篇数、篇均长度、词典命中密度与媒体权威性评分分布共同驱动, 使用者在跨银行-年比较时应留意这一"体量效应"与"情感强度"的混合成分。

【方法学与计算】
计算链条分两段。第一段 (阶段 22 `tone_words.py`): 对每篇经留篇门控 (阶段 21 `llm_verified_full == True`, full-only 门控, 2026-06-29 起 ctx/ss 行宇宙为 full 留篇集的子集) 保留的文章, 用 jieba 分词后, 先对整个语料计算每个词的原始 IDF: raw_idf(w) = log₁₀(N / (1 + df(w))), 再对该词典全部词的 raw_idf 做均值归一化, 最后按 [P1, P99] Winsorize 截尾得到最终 IDF 权重; `_build_idf_weighted_dict` 用该权重对 you_2018 词典基分逐词相乘 (正面词 +1.0 × idf_weight, 负面词 −1.0 × idf_weight, 命中双侧重叠词表 `_BOTH_SIDED_BY_DICT['you_2018']` 的词按用户 2026-06-24 决策两侧对称计入而非武断消歧, 该词典有 5 个此类重叠词), 得到逐轨情感得分 `you_2018_idf_score{track}` (经 `_compute_sentiment_with_rules` 应用否定翻转/程度副词/转折三条语言学规则后归一化)。第二段 (阶段 40 面板导出 `runner.py`/`encode.py`): `compute_media_authority_weights` (runner.py, 步骤 3c) 依据文章 `媒体(中文)` 字段查 `media_weights.json` 产出 `media_authority_weight` 列 (缺省填 1.0, 即无匹配媒体退化为等权), 文章级相乘 `you_2018_idf_score_mw{track} = you_2018_idf_score{track} × media_authority_weight` (runner.py:797-821), 再在 `groupby(['银行','年份'])` 内对该乘积求和得到本家族三列 `you_2018_idf_score_mw_sum{track}` (encode.py:1096, `agg[...] = (..., 'sum')`)。三轨口径遵循全库统一定义: full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗 (ss 回退语义镜像 ctx: 无银行∧金科同句共现时 `content_ss` 回退为全文 body, `ss_is_fallback=True`, 与 `n_articles` 分母口径共享); media_authority_weight 是文章级、与轨道无关的静态权重 (不逐轨重算, 只按发文媒体查表), 因此三轨得分的差异完全来自 `you_2018_idf_score{track}` 本身随轨道文本变化, 而非媒体权威性权重本身随轨道变化。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 估计式。

【文献定位】
you_2018 词典的方法学母本是 You, Zhang & Zhang (2018, The Review of Financial Studies) 关于媒体语调差异化影响力的实证框架, 本项目将其情感词表移植入中文语境并入六词典并排体系。IDF 加权情感打分的理论依据是词频-逆文档频率对词汇「区分度」的经典刻画, 溯源至 Spärck Jones (1972, Journal of Documentation) 首次提出 IDF 统计解释、并经 Jegadeesh & Wu (2013, Journal of Financial Economics) "Word power" 一文将 IDF 加权思想系统应用于金融文本情感测度的构造。Sheridan, Ahmed & Farooque (2025/2026, The American Statistician) 从统计推断视角为 TF-IDF 加权方案提供了 Fisher 精确检验意义下的理论正当性, 说明 IDF 权重并非纯经验启发式而具备可推导的统计学基础。本家族的 `mw` 加权乘子来自 Holzman, Miller & Twedt (2023, The Accounting Review)《Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements》Appendix A 提出的"按媒体对市场反应的边际贡献差异化加权情感"这一方法学洞见 (本项目代码注释与日志中记录该出处, DOI: 10.2308/TAR-2020-0104, 未收录于本家族白名单引文池, 故此处不作结构化引文条目, 仅作方法学溯源陈述); 该论文本身未进入本家族结构化 citations 列表, 但其"媒体影响力异质性应被显式建模而非等权处理"的核心主张是本家族存在的直接方法学依据。本家族与仓库内另一部政治词权重敏感性词典 Du, Huang, Wermers & Wu (2022, Review of Finance) 属同一"中文金融情感词典矩阵"内的平行成员——两部词典在构念上均服务于金融文本情感极性判定, 但覆盖词表与构建语料不同, 互为跨词典稳健性对照。方法论定位上, 本家族的词典法 IDF 加权得分与 Frankel, Jennings & Lee (2022, Management Science) 所讨论的"机器学习 vs. 词典法"情感测度谱系相呼应: 词典法 (含本家族) 相对机器学习/LLM 法更透明、可复现、无需训练数据, 但对语境与反讽的敏感度较低, 该差异构成三条情感测度轨道 (LLM/词典/BERT) 互为稳健性、不分主次的方法学依据。Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析方法谱系 (词典法/机器学习法/深度学习法), 为本家族所属的词典法 IDF 加权情感测度在方法学谱系中的定位提供最新的文献综述依据。Xu, Hua & Zhang (2025, Emerging Markets Review) 构建官方媒体情感指数并证实其对中国股市散户交易行为与收益反转具有显著解释力, 呼应本家族媒体权威性加权构念中"不同来源媒体报道影响力应差异化建模"的核心主张。Han, Hsieh & Zhang (2026, Journal of Futures Markets) 对分析师研究报告文本情感进行加权测度并检验其对期货收益的预测力, 为本家族词典法文本情感加权测度在金融文本分析谱系中的适用性提供最新的跨市场证据。

## VAR: you_2018_idf_score_mw_sum_ctx

【变体差分】
本列文本轨为 ctx (标题 + 实体窗口): 分子逐篇乘数中的 `you_2018_idf_score_ctx` 取自阶段 22 对 `content_ctx` 文本分词打分的结果 (IDF 权重表本身由语料统一估计, 不逐轨重估), `media_authority_weight` 是文章级、与轨道无关的静态权重 (按发文媒体查 `media_weights.json`, 三轨共享同一个数值, 不逐轨重算)。`content_ctx` 是阶段 14 `ctx_materializer` 在标题基础上截取围绕目标实体 (银行/金科关键词) 的窗口文本 (`prepend_title` 拼接方式), 相比 full 轨去除了与目标实体无直接关联的段落, 理论上能提升 IDF 加权情感打分对"目标相关内容"的聚焦度, 代价是文本长度显著缩短、可供语言学规则 (否定翻转/程度副词/转折) 捕捉的语境线索相应减少。行宇宙是 full-only 留篇门控 (阶段 21 `llm_verified_full == True`) 下的子集, 即 ctx 轨不单独决定"是否算一篇银行金科报道", 只在 full 已判定留篇的文章上计算 conditional-on-full 的测度/稳健性数值, 这是 2026-06-29 起全库统一切换的口径, 与阶段 21 `tone_llms.py::df_filtered` 及 `run_pipeline_function.py::_stage21_skip_is_compatible` 两处门控副本同步。若 `content_ctx` 因缺乏可界定的实体窗口而回退为全文 (`content_ctx_is_fallback=True`), 该篇的 `you_2018_idf_score_ctx` 会与 `you_2018_idf_score_full` 逐位相同 (媒体权威性权重本身与轨道无关, 不受此回退影响), 从而使该篇对 mw_sum_ctx 的贡献退化为与 full 轨一致, 这是已知的、由文本回退机制导致的预期现象而非计算错误, 小样本 dev 环境下该回退比例可能偏高、拉高 ctx 与 full 两轨的相关系数。本列与 `_full`/`_ss` 两个同族列互为稳健性并排, 三者各自 just-identified, 不得混入同一 over-identified Hansen J 估计式; 亦不得与非-mw 的 `_hw` (羊群衰减加权) / `_w` (mention-density 加权) 两条并排加权路径混入同一识别式, 三条加权路径分别捕捉"媒体权威"“羊群/转抄程度”“提及密度"三种不同的降权逻辑, 互不替代。

## VAR: you_2018_idf_score_mw_sum_full

【变体差分】
本列文本轨为 full (标题 + 正文全文), `you_2018_idf_score_full` 直接对完整文章文本 (`content_full` = `prepend_title` 拼接后的标题+正文) 计算, 不涉及实体窗口截取或同句共现判据, 因而是三轨中唯一不存在"回退到谁"这一问题的轨——ctx/ss 两轨在各自判据不满足时都会回退成与本轨逐位相同的数值, 而 full 轨本身没有更上一级可回退的对象。full 轨同时也是阶段 21 留篇门控的判定依据本身 (`llm_verified_full == True`, full-only, 2026-06-29 起统一口径), 即本列所覆盖的行宇宙定义了 ctx/ss 两轨的父集合: 任何一篇文章只要未通过 full 轨的留篇判定, 无论其 ctx/ss 轨文本内容如何, 都不会出现在本家族任何一列的 bank-year 求和分子中。媒体权威性权重 `media_authority_weight` 是文章级、跨轨道共享的静态量 (查 `媒体(中文)` 字段匹配 `media_weights.json`), 因此本列与 ctx/ss 两列在权重乘子上完全一致, 三轨得分的差异全部来自 `you_2018_idf_score{track}` 本身随文本轨道变化, 而非媒体权威性权重变化。依 CLAUDE.md 铁律, full 轨不因承担门控职能而获得"主测度"地位——full/ctx/ss 三轨在识别策略层面仍是互为稳健性、不分主次的并排关系, 各自 just-identified, 严禁混入同一 over-identified Hansen J 估计式; 亦不得与 `_hw`/`_w` 两条并排加权路径混入同一识别式。

## VAR: you_2018_idf_score_mw_sum_ss

【变体差分】
本列文本轨为 ss (标题 + 银行∧金科同句 ±N 窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1, 注意此键与阶段 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同配置键, 不可混用): `you_2018_idf_score_ss` 对 `content_ss` 计算, 该文本要求目标银行与金科关键词在同一句 (或 ±N 窗) 内共现方视为有效 ss 文本, 是三轨中判据最严格、文本片段通常最短的一支, 理论上最能剔除"同篇报道中与银行金科交集无关的段落"对 IDF 加权情感打分的稀释。media_authority_weight 与 ctx/full 两轨完全共享同一数值 (文章级、不分轨道), 不参与本轨特有的构造。ss 回退语义严格镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True` (与 `n_articles` 分母口径共享), 此时该篇的 `you_2018_idf_score_ss` 会与 `you_2018_idf_score_full` 逐位相同, 对 mw_sum_ss 的贡献相应退化为 full 轨口径, 与 ctx 轨的回退退化现象结构上完全同构。行宇宙同样是 full-only 留篇门控下的子集, ss 轨不参与"是否算一篇银行金科报道"的判定, 仅在已留篇 (full 轨 `llm_verified_full == True`) 的文章上给出 conditional-on-full 的严格同句测度/稳健性数值。由于同句判据比 ctx 的实体窗口判据更严格, 在小样本 (如本机 T=2 dev 环境) 下 ss 轨回退比例可能显著高于 ctx 轨, 导致 ss 轨与 full 轨在数值上呈现异常高的相关性、甚至方差退化, 这是判据严格度差异下的预期统计特征而非计算缺陷, 生产全量语料 (T=19, 2007-2025) 下同句共现命中率通常显著提升、回退比例相应下降。ss 轨判定"同句共现"的原语是 `extract_bank_fintech_cooccurrence`, 与 stage 13 共现硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` (±1 句窗口, 用于决定文章是否进入语料而非用于物化文本) 是两个不同口径的判据函数, 禁止互相复用或混淆。本列与 `_full`/`_ctx` 两列同为互为稳健性、不分主次的并排测度, 各自 just-identified, 不得混入同一 over-identified Hansen J 估计式; 亦不得与 `_hw`/`_w` 两条并排加权路径混入同一识别式。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Sheridan, P., Ahmed, Z., & Farooque, A. A. (2026). A Fisher's exact test justification of the TF-IDF term-weighting scheme. The American Statistician, 80(1), 146-156. https://doi.org/10.1080/00031305.2025.2539241
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
Han, Q., Hsieh, P., & Zhang, L. (2026). Commodity Futures Report Text Sentiment and Returns. Journal of Futures Markets. https://doi.org/10.1002/fut.70090
<!-- rendered-citations:end -->
