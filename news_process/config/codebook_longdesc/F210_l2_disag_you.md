---
family_id: F210
columns:
- disag_you_2018_ctx
- disag_you_2018_full
- disag_you_2018_ss
unit: 无量纲分歧指数, 取值区间 [0, 1]
formula: "disag_you_2018 = sqrt(1 - ((P - N) / (P + N))^2); P = avg_you_2018_pos_ratio (You et al. 2018 中文金融情感词典正面词命中比率, 逐轨聚合), N = avg_you_2018_neg_ratio (同词典负面词命中比率)"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag; 单词典分支 for d in DICT_NAMES, d='you_2018')
upstream:
- stage 22 tone_words 聚合的 avg_you_2018_pos_ratio / avg_you_2018_neg_ratio (You et al. 2018 中文金融情感词典词级正/负比率, 逐轨)
- 24_herd_decay.parquet (df_exploded; 文章×银行留篇宇宙, 提供聚合分母与 full-only 门控)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: "10.1093/rfs/hhac075"
  type: journal
  authors: "Daniel, K., Klos, A., & Rottke, S."
  year: 2023
  title: "The Dynamics of Disagreement"
  venue: "Review of Financial Studies"
- doi: "10.2139/ssrn.6566038"
  type: "wp"
  authors: "Fu, J. Y., Huang, A. G., Wermers, R. R., Zhang, J., & Zhang, Y."
  year: 2026
  title: "The Information Content of Tone Dispersion: Evidence from Earnings Conference Call Q&As"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "6566038"
- doi: "10.3386/w35049"
  type: "wp"
  authors: "Goulding, C., Harvey, C., & Kurtović, H."
  year: 2026
  title: "Disagreement of Disagreement"
  venue: "National Bureau of Economic Research"
  pages_or_artno: "35049"
- doi: "10.1186/s40854-025-00835-3"
  type: "journal"
  authors: "Jin, X., & Tian, Z."
  year: 2026
  title: "Online investor disagreement, self-attribution bias, and future stock returns"
  venue: "Financial Innovation"
  vol: "12"
  issue: "1"
  pages_or_artno: "57"
- doi: "10.1177/0148558x251384064"
  type: "journal"
  authors: "Driskill, M. W."
  year: 2025
  title: "Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns"
  venue: "Journal of Accounting, Auditing & Finance"
  pages_or_artno: "0148558X251384064"
new_dois:
- "10.1093/rfs/hhac075"
---

## CORE

【构念与来源】
本家族度量的是一家银行在给定年度里, 被媒体报道所携带的情感在"正面对负面"这一维度上的分歧程度 (sentiment disagreement / polarization)。它不回答"整体偏正还是偏负"这个方向性问题, 而回答"报道口径有多撕裂、多不一致"这个离散度问题。此处的情感抽取口径须先厘清: 本家族的正负信号并非来自 stage 21 情感 LLM 三家投票, 而是来自 You, Zhang, and Zhang (2018) 构建的中文金融情感词典——即以词级命中为原语的词典轨 (stage 22 tone_words 聚合)。具体地, producer 消费的两个原始列是 avg_you_2018_pos_ratio 与 avg_you_2018_neg_ratio, 分别是该词典正面词、负面词在报道文本上的命中比率经逐轨聚合后的银行-年度均值; 命名沿用 You et al. (2018) 该词典的作者标签 (you_2018), 与 stata_labels_zh.json 中"情感分歧度(You2018词典)"的标注同源。LLM 投票版本的分歧另有独立列 disag_llm, 不属于本家族, 二者不可混淆。You et al. (2018) 关于"谁掌握了媒体之笔"的研究脉络指出: 媒体报道并非无摩擦地传递单一信号, 不同来源、不同立场的报道会对同一实体给出方向相反的评价, 而这种评价的分裂本身就是一个有信息含量的独立测度, 不能被平均语调 (mean tone) 所吸收。因此本家族把"分歧"从"语调水平"中剥离出来, 作为一条与情感均值正交的信号轨。

【方法学与计算】
计算的原始输入是 You et al. (2018) 中文金融情感词典在报道文本上的词级命中: 上游 stage 22 tone_words 先对每篇报道数出该词典的正面词、负面词命中并归一化为命中比率, 再逐轨聚合到银行-年度得到两列 avg_you_2018_pos_ratio 与 avg_you_2018_neg_ratio; 24_herd_decay.parquet 的 df_exploded 只用于界定"哪些报道进入该银行该年度"的留篇宇宙与聚合分母。对某银行某年度, 记该词典正面词命中比率 (avg_you_2018_pos_ratio) 为 P、负面词命中比率 (avg_you_2018_neg_ratio) 为 N。二者是 float 词级比率, 而非任何投票计数或篇章计数——这是本家族与 disag_llm (LLM 投票篇章计数) / disag_bert (BERT 概率均值) 两族在原语层面的根本区别。分歧指数定义为 disag = sqrt(1 − ((P − N) / (P + N))^2)。这个式子的几何含义清晰: 令 r = (P − N) / (P + N) 为方向性净比率 (∈ [−1, 1]), 则 disag = sqrt(1 − r^2) 恰是以 r 为横坐标的单位圆纵高。当词典命中一边倒 (P = 0 或 N = 0) 时 r = ±1, disag = 0, 表示零分歧; 当正负词命中比率相等 (P = N) 时 r = 0, disag 取最大值 1, 表示最大撕裂。该构造与本阶段步骤 7i 的 Janis-Fadner 系数共用同一对量 P、N 但语义正交: J-F 刻画的是净倾向的强度与符号, disag 刻画的是倾向的不确定性, 两者是同一分布的"一阶矩方向"与"离散度"两面。producer 落地于 pipeline/panel/runner.py 步骤 8b (disag) 的单词典分支 (for d in DICT_NAMES, d='you_2018'), 属纯后处理算术, 本阶段不再调用任何 LLM 或嵌入 API; 由于输入本就是 float 比率, runner 内对计数轨所做的 Int8→float64 防回绕转换对本列是 no-op。取值恒在 [0, 1] 闭区间, 无量纲。当 P + N = 0 (该单元词典正负词均零命中或无报道) 时分母为零, 结果按缺失 (NaN) 处理而非填零, 与全流水线"没报道标缺失、不标零"的口径一致。

【文献定位】
本家族坐落于"分歧与资产定价"这一成熟文献带的媒体测度侧。Hong and Stein (2007) 从理论上论证投资者意见分歧是理解交易量、动量与崩盘的核心状态变量; Carlin, Longstaff, and Matoba (2014) 用抵押证券市场的直接分歧代理验证了分歧与预期收益、收益波动、交易量同向相关; Cen, Wei, and Yang (2017) 进一步指出分析师层面的分歧伴随反应不足与可预测的横截面收益。到了以文本为原料的近端, Cookson and Niessner (2020) 把分歧分解为"跨投资风格"与"同风格内"两部分, 为"分歧不是噪声、而是可结构化的信号"提供了范式; Li and Luan (2025) 直接以基于新闻的投资者分歧构造测度并检验其对股票收益的解释力, 与本家族"用媒体报道的语调分裂构造银行层面分歧"的做法最为贴近。方法层面, Frankel, Jennings, and Lee (2022, Management Science) 系统比较了机器学习与词典法在披露情感抽取上的一致与背离, 提示任何情感聚合量都应交代其抽取引擎的口径依赖——本家族因此明确其 P、N 来自 You et al. (2018) 中文金融情感词典的词级正/负命中比率 (stage 22 tone_words 词典轨), 而非 stage 21 三家 LLM 投票或 stage 23 BERT 概率轨。Daniel, Klos, and Rottke (2023, Review of Financial Studies) 利用信息冲击后乐观者与悲观者估值分化的动态演变来刻画分歧强度随时间收敛的过程, 与本家族用媒体报道正负情感词命中比率构造的银行-年度分歧指数在"分歧作为可测度且随信息演化的独立状态变量"这一构念上相呼应。这一交代至关重要: 全仓另有 disag_llm (LLM 投票篇章计数) 与 disag_bert (BERT 概率均值) 两族分歧列, 三者度量同一"情感撕裂"构念但抽取引擎不同, 恰是 Frankel et al. (2022) 所论"引擎选择会改变情感读数"的具体落地——它们互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J。本家族只承载词典引擎这一支, 使用时不得与 disag_llm / disag_bert 在构念来源上混淆。同理, 本家族的三条轨道 (full/ctx/ss) 亦各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨的 disag 混进同一 over-identified 的 Hansen J 统计量。 就该构念的近期前沿, Fu、Huang、Wermers、Zhang 与 Zhang (2026) 以 FinBERT 测算盈利电话会 Q&A 环节内分析师之间的语调离散, 报告其信息含量增量于整体语调水平, 在构念层支持把语调的散布与语调的水平分列两族; 惟该文尚未经同行评审, 其离散来自英文电话会中分类器概率的统计散布, 与本族对中文新闻作 You et al. (2018) 词典正负比率的 AF 闭式变换并非同一路径, 仅作同族构念的前沿存在性引证, 而非公式出处。Goulding、Harvey 与 Kurtović (2026) 系统比较金融学中多种分歧代理, 指出不同构造方法所得度量彼此相关性低、结论不一致, 直接支撑本项目逐词典各出一条 disag_* 并令其互为稳健性、不分主次地并排; 其对象为美国市场的分析师预测与交易量类代理, 并未评价本族所用的 AF 一致性指标。Jin 与 Tian (2026) 在中国市场以在线文本度量投资者分歧并考察其与后续收益的关系, 表明中文语境下的文本型分歧测度仍属活跃前沿; 其文本源为投资者论坛、主体为上市公司, 与本族的报纸新闻语料、银行主体及银行-年层级在数据源与分歧公式上均不同。Driskill (2025) 检讨分析师分歧测度的构造设计与效度, 证明预测窗口设定不当会令离散度与公告期异常成交的关联沦为不一致且无定论, 前推 ex ante 窗口后方稳健恢复正向关联; 本族据此仅取一般测度学教训——样本纳入规则会实质改变分歧指标的效度, 故 disag_you_2018 的逐轨聚合口径与 P+N 为 0 时置 NaN 的纳入规则须显式披露并做敏感性检验; 原文未讨论分母标准化或归一化选择, 亦不涉媒体文本, 不能作为本族分母设定的直接参照。
## VAR: disag_you_2018_full

【变体差分】
本列是 full 轨的分歧指数, 也是本家族的 canonical 主轨。full 轨的文本口径为"标题 prepend + 全文正文"(content_full, 在 stage 14 ctx_materializer 物化时把标题前置拼入正文, 原始内容列不改动)。其 P、N 取自 You et al. (2018) 中文金融情感词典在 full 轨文本上的词级命中比率 (avg_you_2018_pos_ratio_full / avg_you_2018_neg_ratio_full, stage 22 tone_words 逐轨聚合), 而非任何 LLM 投票或 BERT 概率。留篇宇宙口径仍遵循 2026-06-29 起生效的 full-only 门控: 一篇报道是否被计入某银行某年度的报道宇宙, 只看 llm_verified_full == True; 因此 full 轨词级比率的聚合分母同域于"被判为一篇银行金融科技报道"的正式留篇集, 是三轨中口径最权威、样本最完整的一条。在本列上, P + N = 0 的单元 (整年词典正负词均零命中或无报道) 置 NaN, 不填零。与家族内 ctx/ss 两轨的区别纯粹在文本范围与命中域: full 轨对全文数词, 分歧信号来自整篇报道的正负词命中分布, 因而对长文中夹杂的多空混合措辞最敏感。作为 canonical 轨, 论文主回归若采用银行层面词典语调分歧作为处理或控制变量, 应以本列为首选测度; ctx 与 full 互为稳健性, 各自 just-identified 并排进入各自的估计式, 禁混进同一 over-identified Hansen J。需要强调的是, full 轨的分歧读数并不等价于对词典语调均值取绝对值再翻转: 由于 disag 是 sqrt(1 − r^2) 的凹变换, 同样的净比率偏移在接近中性 (r 约为 0) 处对分歧几乎无影响, 而在接近一边倒 (r 接近 ±1) 处对分歧的边际影响急剧放大, 因此本列对"从压倒性单向措辞中出现的第一批反向词汇"格外敏感。这一非线性正是它区别于线性语调控制项、能捕捉媒体口径撕裂拐点的地方; 使用时若与 full 轨词典语调均值同式, 应注意二者在极端语调区的机械相关, 避免共线误判。

## VAR: disag_you_2018_ctx

【变体差分】
本列是 ctx (context) 轨的分歧指数, 是与 full 轨互为稳健性的并排测度轨, 不分主次。ctx 轨的文本口径为"标题 prepend + 实体上下文窗口"(content_ctx): 只截取目标银行实体在正文中出现处附近的上下文, 而非整篇全文。其 P、N 同样是 You et al. (2018) 词典的词级正/负命中比率 (avg_you_2018_pos_ratio_ctx / avg_you_2018_neg_ratio_ctx), 但命中只在 ctx 轨截取的上下文文本上数出。在 2026-06-29 full-only 门控下, ctx 轨降为 conditional-on-full 测度: 其行宇宙是 full 留篇集的子集 (即先由 llm_verified_full 决定该篇是否留下, ctx 轨再在这些留篇上按自身文本重数词典命中比率)。因此本列刻画的是"把镜头收窄到银行实体近旁语境后, 报道口径的分歧还有多大"——若一篇长文整体多空措辞混杂但在银行实体近旁只有单一情感词, ctx 轨的分歧会低于 full 轨, 这一系统性差异正是它作为稳健性轨的价值所在。与 ss 轨的区别在于窗口判据: ctx 用的是实体上下文窗口, ss 用的是银行与金融科技同句共现窗口, 两者口径不可互相复用。作为稳健性轨, ctx 列的经济含义是检验主结论是否被"报道通篇的杂音"驱动: 若把注意力约束到银行实体近旁, 分歧信号大幅衰减而主回归系数随之消失, 则说明原本的分歧效应可能来自与银行无关的段落; 若系数稳健, 则分歧确实源于对该银行本身的评价分裂。dev 语料 T=2 上若该轨出现零方差或大量缺失属预期退化, 生产语料 T=19 恢复正常。铁律: ctx 与 full/ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: disag_you_2018_ss

【变体差分】
本列是 ss (same-sentence) 轨的分歧指数, 是三轨中判据最严格的稳健性轨。ss 轨的文本口径为"标题 prepend + 银行与金融科技同句 ±N 窗"(content_ss, 窗宽由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1 句): 只保留目标银行与金融科技词在同一句 (及邻近半径内) 共现的片段, 是对"这篇报道确实在讲这家银行的金融科技"这一命题要求最高的一条轨。其 P、N 是 You et al. (2018) 词典在该轨文本上的词级正/负命中比率 (avg_you_2018_pos_ratio_ss / avg_you_2018_neg_ratio_ss), 同为词典轨而非 LLM 投票或 BERT 概率。关键的回退语义须复述以避免误读: ss 轨镜像 ctx 轨的回退——当某篇报道不存在银行∧金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 轨共享 n_articles 分母; 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 优雅降级。因此本列上的分歧读数, 在无同句共现的篇目上实际等同于对全文词典命中比率算出的分歧读数 (但仍标记为 fallback), 使用时须结合 ss_is_fallback 判读。同样在 full-only 门控下, ss 轨为 conditional-on-full 测度, 行宇宙是 full 留篇集的子集。从稳健性梯子的角度看, ss 轨提供的是最保守的分歧读数: 它只承认那些在句法上把银行与金融科技紧紧绑在一起的评价, 因而最能排除"银行只是长文里顺带一提、分歧其实来自其他主体"的稀释。若主结论在这条最严判据轨上仍然成立, 则构念效度得到最强支撑; 若仅在 full 轨成立而在 ss 轨消失, 则提示分歧信号对文本范围敏感, 须在稳健性叙事中如实披露。ss、ctx、full 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Daniel, K., Klos, A., & Rottke, S. (2023). The Dynamics of Disagreement. Review of Financial Studies. https://doi.org/10.1093/rfs/hhac075
Fu, J. Y., Huang, A. G., Wermers, R. R., Zhang, J., & Zhang, Y. (2026). The Information Content of Tone Dispersion: Evidence from Earnings Conference Call Q&As. SSRN Electronic Journal No. 6566038 [Working Paper]. https://doi.org/10.2139/ssrn.6566038
Goulding, C., Harvey, C., & Kurtović, H. (2026). Disagreement of Disagreement. National Bureau of Economic Research No. 35049 [Working Paper]. https://doi.org/10.3386/w35049
Jin, X., & Tian, Z. (2026). Online investor disagreement, self-attribution bias, and future stock returns. Financial Innovation, 12(1), 57. https://doi.org/10.1186/s40854-025-00835-3
Driskill, M. W. (2025). Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns. Journal of Accounting, Auditing & Finance, 0148558X251384064. https://doi.org/10.1177/0148558x251384064
<!-- rendered-citations:end -->
