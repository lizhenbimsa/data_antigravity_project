---
family_id: F640
columns:
- you_2018_idf_score_hw_sum_ctx
- you_2018_idf_score_hw_sum_full
- you_2018_idf_score_hw_sum_ss
unit: 无量纲加权得分之和 (bank-year 内文章级 IDF 加权情感得分 × 羊群衰减权重 逐篇求和)
formula: 'you_2018_idf_score_hw_sum{track} = Σ_{i∈bank-year} (you_2018_idf_score{track}_i × herd_weight_{track}_i); 其中 you_2018_idf_score{track}_i = _compute_sentiment_with_rules(tokens_i, you_2018_idf_weighted_dict, both_sided_words) 归一化情感得分 (词典基分 ±1.0 × build_idf_weights 产出的 Winsorize 后归一化 IDF 权重), herd_weight_{track}_i = 1/(1+相似历史报道数) 的 TF-IDF 羊群衰减权重'
producer: pipeline\panel\runner.py (article-level `{d}_idf_score_hw{track}` = `{d}_idf_score{track}` × `herd_weight_{track}`, runner.py:884-886) ; pipeline\panel\encode.py (bank-year 聚合 `{d}_idf_score_hw_sum{track}` = groupby-sum, encode.py:1069; 供下游 `you_2018_idf_tone_hw{track}` = 本列 / hw_denom{track}, encode.py:2304-2306) ; pipeline\sentiment\tone_words.py (文章级 `you_2018_idf_score{track}` 的产生, build_idf_weights / _build_idf_weighted_dict / _compute_sentiment_with_rules) ; pipeline\sentiment\herd_decay.py (compute_herd_weights 产 herd_weight_{track})
upstream:
- 21_tone_llms (留篇门控 llm_verified_full, full-only)
- 22_tone_words (you_2018 词典 IDF 加权情感打分)
- 24_herd_decay_processor (herd_weight_{track} 羊群衰减权重)
citations:
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who captures the power of the pen?"
  venue: "The Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1016/j.jfineco.2013.08.018"
  type: journal
  authors: "Jegadeesh, N., & Wu, D."
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: "Journal of Financial Economics"
  vol: "110"
  issue: "3"
  pages_or_artno: "712-729"
- doi: "10.1108/eb026526"
  type: journal
  authors: "Spärck Jones, K."
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: "Journal of Documentation"
  vol: "28"
  issue: "1"
  pages_or_artno: "11-21"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514-5532"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
new_dois: []
---

## CORE

【构念与来源】
本家族 (F640) 度量的是 bank-year 面板层面「You et al. (2018) 中文金融情感词典 × 逆文档频率 (IDF) 加权情感得分」在羊群衰减加权 (herd-decay weighted) 口径下的分子求和量, 落盘 3 列, 对应 full/ctx/ss 三条文本轨。you_2018 词典来自 You, Zhang & Zhang (2018) "Who captures the power of the pen?" (Review of Financial Studies) 提出的媒体语调测度框架, 原文用于研究官方媒体与市场化媒体对企业股价的差异化影响力 ("捕获笔杆子的力量"), 其正/负情感词表 (positive 1,425 词 / negative 1,583 词, 另含 definite 388 词 / ambiguous 178 词供 clarity 族复用) 收录于 `config/tone_dicts.json`, 由 `pipeline\sentiment\tone_words.py` 在阶段 22 (词典法情感分析) 中作为六部词典之一 (与 jiang_2021 / yao_2021 / bian_2021 / du_2022 / loughran_mcdonald_zh_2026 并列) 参与打分。`hw` 后缀标记该列走的是「herd-decay weight (羊群衰减权重)」路径 —— 与同一情感基分并排的另外两条加权路径为 `_w` (mention-density 权重, VW) 与 `_mw` (媒体权威度权重, MW); 三条加权路径互为稳健性并排, 皆各自 just-identified, 严禁混入同一 over-identified Hansen J 估计式。`idf` 中缀标记该列的情感基分不是 you_2018 词典的裸打分 (`you_2018_score`), 而是先经阶段 22 `build_idf_weights` 对语料 (`content_full` 或 `内容` 兜底) 逐词计算逆文档频率、再用该 IDF 权重对词典基分 (正面 +1.0 / 负面 −1.0 / du_2022 政治正面词 +0.5, 本词典不涉及政治词) 逐词加权后打出的 `you_2018_idf_score`; `hw_sum` 则是该 IDF 情感得分与羊群衰减权重逐篇相乘后, 在 bank-year 分组内求和的中间分子列 (非最终均值), 供下游除以对应分母 (`_llm_denom` 或直接的 `hw_denom{track}`) 后得到 `you_2018_idf_tone_hw{track}` 这一羊群加权均值。因此本家族三列本身不是可直接解读的「均值情感倾向」, 而是构造该均值所需的加权求和分子, 落盘保留供审计追溯与自定义聚合复现。
【方法学与计算】
计算链条分三段。第一段 (阶段 22 `tone_words.py`): 对每篇经留篇门控 (阶段 21 `llm_verified_full == True`, full-only 门控, 2026-06-29 起 ctx/ss 行宇宙为 full 留篇集的子集) 保留的文章, 用 jieba 分词后, 先对整个语料 (以 `content_full`/`内容` 为 IDF 语料口径, 三轨共享同一套 IDF 权重表 — IDF 是语料级统计量, 不逐轨重算) 计算每个词的原始 IDF: raw_idf(w) = log₁₀(N / (1 + df(w))), 再对该词典全部词的 raw_idf 做均值归一化 normalized_idf(w) = raw_idf(w) / mean(raw_idf), 最后按 [P1, P99] Winsorize 截尾得到 final_idf(w); `_build_idf_weighted_dict` 用该权重对 you_2018 词典基分逐词相乘 (正面词 +1.0 × idf_weight, 负面词 −1.0 × idf_weight, 命中双侧重叠词表 `_BOTH_SIDED_BY_DICT['you_2018']` 的词按用户 2026-06-24 决策两侧对称计入而非武断消歧), 得到逐轨情感得分 `you_2018_idf_score{track}` (经 `_compute_sentiment_with_rules` 应用否定翻转/程度副词/转折三条语言学规则后归一化)。第二段 (阶段 24 `herd_decay.py`): 独立于情感打分, 用 TF-IDF 余弦相似度扫描每篇文章在其发布年内、按目标银行分组的历史报道, 对相似历史报道数越多的文章赋予越低的 `herd_weight_{track} = 1/(1+相似历史报道计数)` (羊群/转抄程度越高、独立信息含量越低, 权重越小), full/ctx/ss 三轨各自独立扫描 (ctx/ss 在其原始文本回退为全文时, 该轨 herd_weight 会退化为与 full 轨逐位相同, 属预期退化而非 bug)。第三段 (阶段 40 面板导出 `runner.py`/`encode.py`): 文章级相乘 `you_2018_idf_score_hw{track} = you_2018_idf_score{track} × herd_weight_{track}` (runner.py), 再在 `groupby(['银行','年份'])` 内对该乘积求和得到本家族三列 `you_2018_idf_score_hw_sum{track}` (encode.py `agg[...] = (..., 'sum')`), 下游据此与 `hw_denom{track}` (羊群权重加总的分母口径) 相除得到最终的羊群衰减加权 IDF 语调均值 `you_2018_idf_tone_hw{track}`, 该均值列另在 `geography.py` 参与跨词典聚合 `dict_avg_idf_tone_hw{track}`。三轨口径遵循全库统一定义: full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗 (ss 回退语义镜像 ctx: 无银行∧金科同句共现时 `content_ss` 回退为全文 body, `ss_is_fallback=True`); full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 估计式。
【文献定位】
you_2018 词典的方法学母本是 You, Zhang & Zhang (2018, *The Review of Financial Studies*) 关于媒体语调差异化影响力的实证框架, 本项目将其情感词表移植入中文语境并入六词典并排体系。IDF 加权情感打分的理论依据是词频-逆文档频率对词汇「区分度」的经典刻画, 溯源至 Spärck Jones (1972, *Journal of Documentation*) 首次提出 IDF 统计解释、并经 Jegadeesh & Wu (2013, *Journal of Financial Economics*) "Word power" 一文将 IDF 加权思想系统应用于金融文本情感/语调测度的构造 (对高信息含量、低泛用度的词汇赋予更高权重, 抑制停用词式套话对语调分数的稀释) —— 本家族的 `idf` 中缀正是这一传统在中文金融新闻场景下的直接实现。词典法本身 (lexicon-based sentiment scoring, 与本项目并排的 LLM 三家投票法、BERT 三模型法互为稳健性) 的方法学定位另见 Frankel, Jennings & Lee (2022, *Management Science*) 对词典法与机器学习法互为稳健性的系统比较, 以及 Du, Huang, Wermers & Wu (2022, *Review of Finance*) 关于中文金融情感词典本土化构造 (语言/领域特定性) 的论述, 后者也是本项目六词典之一 du_2022 与政治词权重敏感性梯度的直接方法学来源, 与 you_2018 同属「中文金融情感词典族」并排比较对象。

## VAR: you_2018_idf_score_hw_sum_ctx

【变体差分】
本列文本轨为 ctx (标题 + 实体窗口): 分子逐篇乘数中的 `you_2018_idf_score_ctx` 取自阶段 22 对 `content_ctx` 文本分词打分的结果 (IDF 权重表本身仍由 full 语料统一估计, 不逐轨重估), `herd_weight_ctx` 取自阶段 24 对 `content_ctx` 独立扫描的羊群衰减权重。`content_ctx` 是阶段 14 `ctx_materializer` 在标题基础上截取围绕目标实体 (银行/金科关键词) 的窗口文本 (`prepend_title` 拼接方式), 相比 full 轨去除了与目标实体无直接关联的段落, 理论上能提升情感打分与羊群相似度扫描对"目标相关内容"的聚焦度, 代价是文本长度显著缩短、可供 IDF 加权情感规则 (否定翻转/程度副词/转折) 捕捉的语境线索相应减少。行宇宙是 full-only 留篇门控 (阶段 21 `llm_verified_full == True`) 下的子集, 即 ctx 轨不单独决定"是否算一篇银行金科报道", 只在 full 已判定留篇的文章上计算 conditional-on-full 的测度/稳健性数值, 这是 2026-06-29 起全库统一切换的口径, 与阶段 21 `tone_llms.py::df_filtered` 及 `run_pipeline_function.py::_stage21_skip_is_compatible` 两处门控副本同步。若 `content_ctx` 因缺乏可界定的实体窗口而回退为全文, 该篇的 `herd_weight_ctx` 会与 `herd_weight_full` 逐位相同 (`content_ctx_is_fallback=True`), 从而使该篇对 hw_sum_ctx 的贡献退化为与 full 轨一致, 这是已知的、由回退机制导致的预期现象而非计算错误, 在小样本 dev 环境下该回退比例可能偏高、拉高 ctx 与 full 两轨的相关系数。本列与 `_full`/`_ss` 两个同族列互为稳健性并排, 三者各自 just-identified, 不得混入同一 over-identified Hansen J 估计式; 亦不得与非-hw 的 `_w` (mention-density 加权) / `_mw` (媒体权威度加权) 两条并排加权路径混入同一识别式, 三条加权路径分别捕捉"提及密度"“媒体权威”“羊群/转抄程度"三种不同的降权逻辑, 互不替代。

## VAR: you_2018_idf_score_hw_sum_full

【变体差分】
本列文本轨为 full (标题 + 正文全文), `you_2018_idf_score_full` 与 `herd_weight_full` 均直接对完整文章文本 (`content_full` = `prepend_title` 拼接后的标题+正文) 计算, 不涉及实体窗口截取或同句共现判据, 因而是三轨中唯一不受"回退退化为与自身相同"这一伪影响拖累的轨 —— ctx/ss 两轨在各自判据不满足时都会回退成与本轨逐位相同的数值, 而 full 轨本身不存在"回退到谁"的问题。full 轨同时也是阶段 21 留篇门控的判定依据本身 (`llm_verified_full == True`, full-only, 2026-06-29 起统一口径), 即本列所覆盖的行宇宙定义了 ctx/ss 两轨的父集合: 任何一篇文章只要未通过 full 轨的留篇判定, 无论其 ctx/ss 轨文本内容如何, 都不会出现在本家族任何一列的 bank-year 求和分子中。在羊群衰减权重的构造上, full 轨的 TF-IDF 相似度扫描面对的是信息量最完整的正文全文, 相比 ctx (实体窗口截断) 与 ss (同句窗口截断) 更不容易因文本片段过短而对相似度判定产生偏误, 是三轨中信噪比相对最稳定的一支, 在跨轨稳健性比较中常被用作参照基准, 但依 CLAUDE.md 铁律不因此获得"主测度"地位 —— full/ctx/ss 三轨在识别策略层面仍是互为稳健性、不分主次的并排关系, 各自 just-identified, 严禁混入同一 over-identified Hansen J 估计式。本列对应的最终羊群加权语调均值 `you_2018_idf_tone_hw_full` 亦是阶段 46 面板导出与多篇 paper 稳健性表 (herd-decay 敏感性网格) 中最常被引用的 full 轨基线。

## VAR: you_2018_idf_score_hw_sum_ss

【变体差分】
本列文本轨为 ss (标题 + 银行∧金科同句 ±N 窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1, 注意此键与阶段 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同配置键, 不可混用): `you_2018_idf_score_ss` 与 `herd_weight_ss` 均对 `content_ss` 计算, 该文本要求目标银行与金科关键词在同一句 (或 ±N 窗) 内共现方视为有效 ss 文本, 是三轨中判据最严格、文本片段通常最短的一支, 理论上最能剔除"同篇报道中与银行金科交集无关的段落"对情感打分与羊群相似度扫描的稀释。ss 回退语义严格镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True` (与 `n_articles` 分母口径共享), 此时该篇的 `herd_weight_ss` 会与 `herd_weight_full` 逐位相同, 对 hw_sum_ss 的贡献相应退化为 full 轨口径, 与 ctx 轨的回退退化现象结构上完全同构, 二者共享同一套"回退即等同 full"的设计哲学。行宇宙同样是 full-only 留篇门控下的子集, ss 轨不参与"是否算一篇银行金科报道"的判定, 仅在已留篇 (full 轨 `llm_verified_full == True`) 的文章上给出 conditional-on-full 的严格同句测度/稳健性数值。由于同句判据比 ctx 的实体窗口判据更严格, 在小样本 (如本机 T=2 dev 环境) 下 ss 轨回退比例可能显著高于 ctx 轨, 导致 ss 轨与 full 轨在数值上呈现异常高的相关性、甚至方差退化, 这是判据严格度差异下的预期统计特征而非计算缺陷, 生产全量语料 (T=18, 2007-2024) 下同句共现命中率通常显著提升、回退比例相应下降, ss 轨与 full/ctx 两轨的区分度届时会更充分体现。本列与 `_full`/`_ctx` 两列同为互为稳健性、不分主次的并排测度, 各自 just-identified, 不得混入同一 over-identified Hansen J 估计式。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
<!-- rendered-citations:end -->
