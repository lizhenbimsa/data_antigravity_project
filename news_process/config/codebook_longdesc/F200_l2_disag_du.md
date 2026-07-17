---
family_id: F200
columns:
- disag_du_2022_ctx
- disag_du_2022_full
- disag_du_2022_ss
unit: 无量纲离散度指标, 取值区间 [0, 1]
formula: "disag_du_2022 = sqrt(1 - ((P - N) / (P + N))^2); 其中 P = avg_du_2022_pos_ratio (银行-年度内, 逐篇 du_2022 正面词比率 = 正面命中数 / word-token 数, 再对篇章取均值), N = avg_du_2022_neg_ratio (同法负面词比率的银行-年度均值), 逐轨 (full/ctx/ss) 独立计。P + N = 0 时该轨置 NaN。"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022 词典逐篇逐轨正/负面词比率 {d}_pos_ratio / {d}_neg_ratio, = 命中数 / word-token 数)
- 24_herd_decay.parquet (df_exploded, article×bank verified 集)
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
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
- doi: "10.1080/10293523.2024.2398338"
  type: "journal"
  authors: "Wang, G., Chen, M., Wang, X., Dong, Y., & Wang, Z."
  year: 2025
  title: "Opinion divergence, investor sentiment, and stock liquidity: Evidence from social media"
  venue: "Investment Analysts Journal"
  vol: "54"
  issue: "2"
  pages_or_artno: "167-186"
- doi: "10.1177/0148558x251384064"
  type: "journal"
  authors: "Driskill, M. W."
  year: 2025
  title: "Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns"
  venue: "Journal of Accounting, Auditing & Finance"
  pages_or_artno: "0148558X251384064"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是一家银行在给定年度内, 其被报道文本所承载情感信号的内部离散度 (tone dispersion / disagreement), 而非情感的方向或强度。构念的直觉是: 若一批报道对某银行的评价几乎一边倒地正面或一边倒地负面, 则该银行当年的舆论"共识度"高、离散度低; 反之, 若正面词与负面词势均力敌、彼此抵消, 则文本内部存在强烈的语义冲突, 离散度高。该指标刻意与净语调 (tone) 正交: 净语调回答"整体偏正还是偏负", 本指标回答"这份偏向到底有多确定、多一致"。两者构成对同一情感底层信号的互补切片——前者是一阶矩 (方向), 后者近似二阶矩 (弥散)。

情感计数的底层词典来源为 du_2022 中文金融情感词典。该词典由 Du、Huang、Wermers 与 Wu (2022) 在 Review of Finance 上系统构建, 强调金融领域与语言的双重特异性 (language and domain specificity): 通用情感词典迁移到中文金融文本时会因领域漂移与语言差异而系统性失真, 因此需要一部在中文金融语料上重新校准的词典。本项目采用该词典的正面词表与负面词表, 但离散度的输入并非原始命中计数, 而是词级比率: 在篇章级逐轨先算每篇的 du_2022 正面词比率 (该篇正面命中数除以 word-token 总数) 与负面词比率 (负面命中数除以 word-token 总数), 于面板聚合阶段对同一银行-年度内所有篇章的比率取算术均值, 得到该银行-年度的 P = avg_du_2022_pos_ratio 与 N = avg_du_2022_neg_ratio, 再据此合成离散度。之所以以 word-token 归一化的比率 (而非绝对计数) 作分子分母, 是要剥离篇幅长短对情感密度的机械影响——长文天然命中更多词, 若直接用计数会让长报道被过度加权; 转成"每千词命中密度"式的比率后, 长短文在同一尺度上可比, 银行-年度均值才真正反映情感极性的平均密度而非报道体量。选用 du_2022 而非通用词典, 正是为了让"共识/分歧"的判定建立在对中文金融语境敏感的词汇边界上, 避免把领域中性词误判为情感词而虚高或虚低离散度。

【方法学与计算】
离散度的闭式定义为 disag = 根号下 (1 − ((P − N) / (P + N)) 的平方)。令归一化净语调 r = (P − N) / (P + N) ∈ [−1, 1], 则本指标 = 根号 (1 − r 的平方)。几何上, 若把 r 视为单位圆上的余弦分量, 则本指标恰为对应的正弦分量: 当报道完全一边倒 (r = ±1, 纯正或纯负) 时取 0, 表示零分歧; 当正负词恰好相等 (r = 0) 时取 1, 表示最大分歧。因此取值严格落在闭区间 [0, 1], 无量纲。此处 P、N 均为银行-年度的比率均值 (P = avg_du_2022_pos_ratio, N = avg_du_2022_neg_ratio), 而非绝对计数; 分母 P + N 为该轨正负情感密度均值之和。当 P + N = 0 (该轨全年无任何 du_2022 情感命中, 或所有篇章因纯标点/数字文本使比率为 NaN 而聚合后无有效值) 时, 比值无定义, 该轨该单元置 NaN 而非置零——这一 fail-quiet 口径避免把"没有情感信号"误编码为"零分歧的强共识", 二者语义截然不同。计算发生在 pipeline/panel/runner.py 步骤 8b (disag 段, 单词典分支), 属篇章级词级比率经面板聚合 (groupby 银行-年度取均值) 后的纯后处理, 不额外调用任何 LLM 或嵌入 API。上游依赖为 stage 22 的 du_2022 逐篇逐轨正负词比率与 stage 14 物化的三轨文本, 经 stage 24 herd_decay 的 verified 篇章集汇入面板总装阶段。需辨明: 同族的 disag_llm 分支才以篇章级 pos_count / neg_count 计数为输入, 本单词典分支 (disag_du_2022) 与之口径不同, 计数比与均值比数值上并不等价, 不可混同。

【文献定位】
"分歧/离散度可定价"是资产定价与文本金融的核心命题。Carlin、Longstaff 与 Matoba (2014) 在 Journal of Financial Economics 中直接论证了投资者分歧与资产价格及风险溢价的联系, 为"把文本内部情感冲突当作一个独立于方向的定价相关状态变量"提供了理论支点; 本指标可视为该分歧构念在新闻文本层面的可观测代理。Li 与 Luan (2025) 进一步在 Review of Accounting Studies 上把"基于新闻的投资者分歧" (news-based investor disagreement) 显式操作化并与股票收益关联, 与本家族"以报道文本正负抵消程度度量舆论分歧"的思路高度同构, 是本指标最贴近的方法学对照。词典侧, 除锚定 du_2022 (Du et al., 2022) 外, Ma、Zhang 与 Zhang (2025) 构建的 CN-FSD 细粒度中文投资者情感词典, 以及 Sun、Yuan 与 Xu (2025) 关于把词典知识与中性特征融入预训练语言模型的工作, 共同印证了中文金融情感测度对领域专用词表与中性/冲突信号处理的强依赖——这也解释了本指标为何必须以领域词典 (而非通用词典) 的正负词比率均值为分母基。 近期工作从测度学层面为本指标补足了三点依据。Fu、Huang、Wermers、Zhang 与 Zhang (2026) 以 FinBERT 测算盈利电话会 Q&A 环节内分析师之间的语调离散, 证明该离散的信息含量增量于整体语调水平, 支持本家族把语调的散布与语调水平分列为两族测度; 该文为未经同行评审的工作论文, 单位是英文盈利电话会 Q&A、层级为公司-事件, 其离散取自 BERT 分类器概率的统计散布, 与本指标对 du_2022 词级比率所作的 Antweiler-Frank 型闭式变换数学形式不同, 仅在构念上同族。Goulding、Harvey 与 Kurtović (2026) 系统比较了金融学中多种分歧代理变量, 指出不同构造方法给出的分歧度量彼此相关性低、结论亦不一致, 这构成本项目逐词典各出一条 disag_*、互为稳健性、不分主次并排之做法的必要性依据; 惟该 NBER 工作论文的对象是美国市场的分析师预测与交易量类代理, 且并未评价本指标所用公式。Wang、Chen、Wang、Dong 与 Wang (2025) 用社交媒体的看多看空投票构造零售投资者观点分歧指数、以机器学习从评论文本构造在线投资者情绪指数, 发现二者均显著影响股票流动性, 且情绪对分歧到流动性的路径起中介作用; 据此须对上文措辞作一处诚实的边界补正——该文恰恰表明分歧与情绪水平相互纠缠而非各自独立, 故本家族并排保留 disag_du_2022 与 du_2022 净语调两族的依据只能是二者非同一量、值得分别观测, 而不能声称二者在统计上相互独立。其分歧源为投票而非词典对文本的正负标注, 因变量为股票流动性, 层级为公司-期, 与本项目银行-年、以财务哨兵列为因变量的设定不同。Driskill (2025) 则通过前推 ex ante 窗口、压缩 ex post 窗口, 证明既有分析师离散度测度与盈利公告期异常成交的弱关联源自预测窗口设定不当, 修正后方稳健恢复正向关联; 其一般测度学教训是分歧指标的构造选择会实质改变效度与结论方向, 因而本指标的逐轨聚合口径与 P + N = 0 置 NaN 的样本纳入规则须显式披露并接受敏感性检验。该文未讨论分母标准化或归一化选择, 亦不涉及媒体文本, 故不构成本指标分母基设定的直接参照。
【三轨口径铁律】
本家族的三列对应 full / ctx / ss 三条文本轨, 分子分母严格逐轨: 每一轨的 P、N 均取该轨自身的 du_2022 正负词比率的银行-年度均值, 绝不跨轨借用分母。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。full 轨 (标题 prepend + 全文正文) 是留篇门控主轨: 一篇报道是否计入某银行当年样本, 由 full 轨的 full-only 门控 (2026-06-29) 判定; ctx / ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。ss 轨的回退语义镜像 ctx: 当某篇无银行∧金科同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母。三轨在开发规模 (T=2) 上, ctx / ss 可能因样本稀薄而出现零方差退化, 属预期现象, 生产规模 (T=19) 恢复正常。

## VAR: disag_du_2022_full

【变体差分】
本列取 full 文本轨的 du_2022 正负词比率均值计算离散度, 即 P = avg_du_2022_pos_ratio_full、N = avg_du_2022_neg_ratio_full (逐篇比率 = 命中数 / word-token 数, 再对全年篇章取均值)。full 轨定义为"标题 prepend + 全文正文", 即把新闻标题拼接到正文之前、对整篇内容统计 du_2022 情感词命中并归一化为词级比率。它是三轨中的留篇门控主轨 (full-only 口径, 2026-06-29): 一篇报道是否被判为该银行当年的一条有效样本, 只看 full 轨的 llm_verified_full, 因此 full 轨的行宇宙即整个 verified 留篇集, 而非任何子集。相较 ctx / ss 两条上下文收窄轨, full 轨覆盖文本最完整、情感词命中最丰、比率均值 P + N 通常最大, 分母最稳、置 NaN 的概率最低, 故在实证中一般作为首要测度轨使用。与本家族另两列的唯一差异纯粹是文本轨: 词典 (du_2022)、公式 (根号 (1 − r 的平方))、聚合口径完全一致。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把 full 与 ctx / ss 混入同一 over-identified Hansen J 检验。full 轨与 ctx / ss 轨在数值上系统性偏大或偏小均属文本覆盖差异的机械结果, 非缺陷。需强调本列度量的是离散度而非方向: 即便 full 轨净语调偏正或偏负, 只要正负词并非一边倒, 本列仍会取到显著高于 0 的值, 因此它与同轨的 du_2022 净语调列在构念上正交、可同入自回归而不互为冗余。就实证解读而言, full 轨离散度偏高提示该银行当年舆论存在实质性正负拉锯 (例如既有金融科技创新利好又有风险合规质疑并存), 偏低则提示口径趋同; 由于 full 轨样本框最广, 该读数对全年整体舆论氛围最具代表性, 常作为分歧类稳健性检验的基准臂。

## VAR: disag_du_2022_ctx

【变体差分】
本列取 ctx 文本轨的 du_2022 正负词比率均值计算离散度, 即 P = avg_du_2022_pos_ratio_ctx、N = avg_du_2022_neg_ratio_ctx。ctx 轨定义为"标题 prepend + 实体上下文窗口": 相较 full 轨的整篇正文, ctx 只截取目标银行实体邻近的上下文片段进行情感词统计, 意在剥离与目标银行无关的段落噪声, 使离散度更聚焦于"关于该银行本身"的舆论分歧。ctx 轨为 conditional-on-full 测度/稳健性轨: 其行宇宙是 full 留篇集的子集 (留篇判定仍由 full 轨门控), ctx 仅在被 full 判为有效后, 对该篇的实体窗口文本另算 P、N。因窗口收窄, ctx 轨的 P + N 常小于 full 轨, 分母更易触及 0 而置 NaN, 尤其在开发规模 (T=2) 稀薄样本上可能出现零方差退化——属预期, 生产规模恢复。与家族其余两列的唯一差异是文本轨: 词典、闭式公式、置 NaN 口径均与 full / ss 完全一致, 分子分母严格取 ctx 轨自身的正负词比率均值, 绝不跨轨借分母。ctx 与 full / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。相对 full 轨, ctx 轨的价值在于回答一个更收敛的问题: 当只看"围绕该银行本身"的文字时, 舆论分歧是否依然存在。若 full 轨离散度高而 ctx 轨离散度回落, 说明冲突主要来自与目标银行弱相关的背景段落 (如行业综述、他行对比), 而非针对该行的直接评价; 反之若两轨同高, 则分歧确系针对该行。正因此, ctx 轨在实证中常与 full 轨并列汇报, 用以剥离段落层面的噪声、检验分歧信号是否稳健于文本窗口的收窄, 而绝不与 full 轨拼入同一过度识别的工具变量集。

## VAR: disag_du_2022_ss

【变体差分】
本列取 ss (same-sentence) 文本轨的 du_2022 正负词比率均值计算离散度, 即 P = avg_du_2022_pos_ratio_ss、N = avg_du_2022_neg_ratio_ss。ss 轨定义为"标题 prepend + 银行∧金科同句共现窗口 (±N 句, 默认半径 1)": 相较 ctx 的实体邻近窗口, ss 进一步收窄到目标银行与金融科技词在同一句 (或近同句) 共现的最严判据文本, 使离散度只反映"银行与金科被同时提及的语境"里的情感冲突。ss 轨的回退语义严格镜像 ctx: 当某篇不存在银行∧金科同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; 当 FINTECH_AC=None 时 ss_is_fallback 全 True 优雅降级。作为三轨中判据最严的一条, ss 轨的 P + N 往往最小, 置 NaN 与零方差退化的概率最高, 在 T=2 开发规模上尤为明显 (属预期, 生产 T=19 正常)。与家族其余两列的唯一差异仍是文本轨: du_2022 词典、根号 (1 − r 的平方) 公式、逐轨分母口径完全一致, ss 的 P、N 严格取 ss 轨自身的正负词比率均值, 不跨轨借用。ss 属 conditional-on-full 稳健性轨, 与 full / ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。ss 轨承担的是最保守的稳健性问询: 当把文本收窄到银行与金融科技词严格同句共现的语境时, 分歧信号是否仍然成立。这一轨对主结论的意义在于排除"分歧来自泛泛报道而非金科相关语境"的替代解释——若 ss 轨与 full / ctx 同向, 则可判定舆论分歧确实附着于银行金融科技这一议题本身。由于判据最严、命中词最少, ss 读数波动更大、对个别篇章更敏感, 故只宜作为方向性佐证轨, 而非精度基准; 在开发规模上其退化为 NaN 或零方差应按预期对待, 不得据此判为管道缺陷。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Fu, J. Y., Huang, A. G., Wermers, R. R., Zhang, J., & Zhang, Y. (2026). The Information Content of Tone Dispersion: Evidence from Earnings Conference Call Q&As. SSRN Electronic Journal No. 6566038 [Working Paper]. https://doi.org/10.2139/ssrn.6566038
Goulding, C., Harvey, C., & Kurtović, H. (2026). Disagreement of Disagreement. National Bureau of Economic Research No. 35049 [Working Paper]. https://doi.org/10.3386/w35049
Wang, G., Chen, M., Wang, X., Dong, Y., & Wang, Z. (2025). Opinion divergence, investor sentiment, and stock liquidity: Evidence from social media. Investment Analysts Journal, 54(2), 167-186. https://doi.org/10.1080/10293523.2024.2398338
Driskill, M. W. (2025). Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns. Journal of Accounting, Auditing & Finance, 0148558X251384064. https://doi.org/10.1177/0148558x251384064
<!-- rendered-citations:end -->
