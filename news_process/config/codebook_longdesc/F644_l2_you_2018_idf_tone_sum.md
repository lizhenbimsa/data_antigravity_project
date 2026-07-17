---
family_id: F644
columns:
- you_2018_idf_tone_sum_ctx
- you_2018_idf_tone_sum_full
- you_2018_idf_tone_sum_ss
unit: 语调加总得分 (连续, 未归一化, 量纲随文章长度与语料 IDF 分布浮动; 聚合至 bank-year 取篇均值后落入面板)
formula: 逐篇 idf_tone_sum = Σ_{w∈pos∩you_2018} idf(w)·tf(w,article) − Σ_{w∈neg∩you_2018} idf(w)·tf(w,article); idf(w) 以 config/tone_dicts.json::you_2018 词表在 content_full (标题+全文, 含标题拼接) 语料上统一计算一次, raw_idf(w)=log₁₀(N/(1+df(w))) (smooth IDF), 再做均值归一化 normalized_idf(w)=raw_idf(w)/mean(raw_idf), 最后 P1/P99 Winsorize 得 final idf(w); N=去重后 (同 content 视为同一文档) 文章总数, df(w)=含词 w 的去重文章数; **三轨 (full/ctx/ss) 共享同一份基于 content_full 计算的 idf(w), 绝不按轨分语料重算** — 三轨列差异只来自各轨自身文本上逐篇计算的 tf(w,article), 而非 idf(w) 本身; positive∩negative 交叉词按用户 2026-06-24 决策两侧保留, 同时计入正负两侧加总 (对该词典个体分值净拉向中性, 不武断消歧); 面板列为 bank-year 内 idf_tone_sum 的算术均值。
producer: pipeline\sentiment\tone_words.py（词典加载/IDF 计算/逐篇打分）; pipeline\panel\export.py（bank-year 聚合与列物化）
upstream:
- news_process/config/tone_dicts.json::you_2018
- 14_materialize_ctx（content_full/content_ctx/content_ss 三轨文本物化）
- 21_tone_llms（llm_verified_full 留篇门控，决定进入聚合的文章行宇宙）
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43–96
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673–719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514–5532
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: The construction of a Chinese fine-grained sentiment dictionary for Chinese
    domestic investors (CN-FSD) and its application
  venue: Expert Systems with Applications
  vol: '264'
  issue: ''
  pages_or_artno: '125739'
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti,
    E.
  year: 2025
  title: 'Sentiment analysis of economic text: A lexicon-based approach'
  venue: Economic Inquiry
  vol: '63'
  issue: '1'
  pages_or_artno: 125–143
- doi: "10.1016/j.intfin.2023.101920"
  type: "journal"
  authors: "Aysan, A. F., Caporin, M., & Cepni, O."
  year: 2024
  title: "Not all words are equal: Sentiment and jumps in the cryptocurrency market"
  venue: "Journal of International Financial Markets, Institutions and Money"
  vol: "91"
  pages_or_artno: "101920"
new_dois: []
---

## CORE

【构念与来源】
you_2018_idf_tone_sum 家族衡量的是"一篇报道对目标银行整体语气偏正面还是偏负面, 并以该篇中每个情感词在整体语料中的信息量 (逆文档频率) 加权后的强度"。词典来源是 You, Zhang & Zhang (2018, Review of Financial Studies)《Who Captures the Power of the Pen?》构建的中文金融情感词典 you_2018: 正面词 1,425 个、负面词 1,583 个 (另含 definite 388/ambiguous 178 两个确定性词类, 由 clarity 族独立消费, 与本家族无关)。该词典由 You et al. 面向"谁在把持媒体这支笔"这一媒体控制/公司治理命题构建, 本项目将其复用作银行—金科报道的语调测度锚之一, 与项目内另外 5 部情感词典 (jiang_2021/yao_2021/bian_2021/du_2022/loughran) 并列, 互为稳健性, 不设唯一"正确"词典。所有词典的正式来源与词条计数以 config/tone_dicts.json 为单一事实源 (SSOT), 本文档只做转述, 不重复维护词表本身。
idf_tone_sum 是项目内 you_2018 词典下的一种打分口径, 与同族兄弟 score/pos_count/neg_count 等口径 (若存在) 平行, 区别在于它不是简单的正负词计数或均一权重求和, 而是逐词乘以 IDF 权重再累加。IDF 权重的直觉是: 一个情感词如果在语料里几乎每篇文章都出现 (df 很高、idf 很低), 它对区分"这篇报道是不是特别正面/负面"贡献的信息量小; 反之如果一个情感词只在少数文章里出现 (df 低、idf 高), 它一旦出现就更能标识该篇文章的语气特异性。idf_tone_sum 借用信息检索里经典的 TF-IDF 思想, 把这种"词的语料稀有度"折算进语调打分, 是对纯计数/纯均一权重打分的一种加权稳健性替代, 而非替换关系——三者在面板里并排存在, 供研究者做测度选择上的敏感性检验, 不预设哪个口径更优。

【方法学与计算】
计算分两个层面, 一个是 IDF 权重的计算 (对全体语料只做一次), 一个是逐篇打分 (对每篇文章各自做)。IDF 权重层面: idf(w) 不是按 full/ctx/ss 三轨各自独立计算, 而是在 content_full (标题+全文, prepend_title 拼接) 这一份统一语料上算一次, 三轨共享同一份数值——这是一处容易误读的关键口径, 务必与下文"三轨打分不同"区分开。具体公式分三步: 第一步 smooth IDF, raw_idf(w) = log₁₀(N / (1 + df(w))), 其中 N 是 content_full 语料按内容去重后的文章总数 (同一 content 视为同一文档, 同篇多银行展开行不重复计入 N), df(w) 是含词 w 的去重文章数 (每篇文章内该词只计一次, 不管篇内重复次数), 分母加 1 平滑防止 df(w)=0 时除零; 第二步均值归一化, normalized_idf(w) = raw_idf(w) / mean(raw_idf), 用于把 IDF 加权后的分数量级拉回与均一权重版本大致可比的尺度, 便于跨口径共享阈值; 第三步 P1/P99 Winsorization, 把归一化后的权重在第 1、第 99 百分位截尾, 防止个别极端稀有词的权重畸高、或极高频词权重被压到接近零而失去区分度, 最终得到逐词的 final idf(w)。逐篇打分层面才是三轨真正产生差异的地方: 对每篇文章 (full/ctx/ss 三选一其文本), 逐词计算 tf(w, article) (该词在本篇轨道文本内的原始出现次数, term frequency), 用同一份 idf(w) 乘以各轨自身的 tf(w, article), 累加正面词得到正侧强度, 累加负面词得到负侧强度, 二者相减 (正−负) 得到该篇该轨的 idf_tone_sum。也就是说三轨列的数值差异, 根源在于 tf(w, article) 因文本范围不同 (全文 vs 实体窗口 vs 同句窗口) 而不同, 而不在于 idf(w) 本身发生了变化。与词典内其他打分口径 (如未加权的 score/纯计数 pos_count/neg_count) 不同, idf_tone_sum 不做篇长归一化, 也不除以词典总词数, 数值量纲直接由该篇的词频与共享的 IDF 权重共同决定, 因而是一个未标准化的"加总"型测度 (sum), 数值范围理论上不封顶, 与 frontmatter 中标注为 [-1,1] 的归一化语调得分 (如 score/net_tone 类列) 不属同一数值尺度, 使用时不应直接跨口径比较绝对水平, 只适合做同口径内的横截面/时间序列比较或标准化后的回归系数比较。
词典消歧口径: you_2018 正负两侧存在 5 个跨类重叠词 (同一词既在 positive 又在 negative 集合中出现), 项目按 2026-06-24 用户决策"保留并两侧计数"处理, 即该词的 tf·idf 同时计入正侧加总与负侧加总, 净效应是把该词对最终 idf_tone_sum 的净贡献拉向中性, 而非武断地为其单选一侧或从两侧同时剔除。该决策逆转了历史上 fix omni-g-tonewords-03/-07 曾采用的"双侧剔除"惯例, 因此若与更早期版本产出比较需注意口径差异不可比。
本家族三个成员列的唯一差分维度是底层文本轨道: full (标题+正文全文)、ctx (标题+围绕目标银行/金科实体的窗口文本)、ss (标题+银行∧金科同句共现窗口文本, 默认句子半径见 config/filtering.yaml::context_window.ss_sentence_radius)。这里必须澄清一个容易误读的口径: idf(w) 本身不是三轨各自独立计算的量——真实实现 (pipeline/sentiment/tone_words.py::build_idf_weights) 是在 content_full 语料上统一计算一次 IDF 权重, 三轨共享同一份 idf(w) 数值, 绝不按轨分语料重算 (ss 轨亦复用此权重)。三轨列的数值差异根源在于逐篇打分环节的 tf(w, article): full/ctx/ss 三轨各自的文本范围不同 (全文 vs 实体窗口 vs 同句窗口), 同一情感词在不同轨道文本里的出现次数 tf(w, article) 不同, 用同一份 idf(w) 乘以不同的 tf 再累加, 才使得三轨最终的 idf_tone_sum 产生差异。尽管共享 IDF 权重本身, 三轨列在测度定位上仍遵循项目铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨列混入同一个 over-identified Hansen J 检验 (三轨差异来自文本覆盖范围而非统计量重算, 并不改变三者互为稳健性替代测度的定位)。ss 轨对无银行∧金科同句共现的文章执行镜像 ctx 的回退语义: content_ss 退化为全文 body, 对应 ss_is_fallback 标记为 True, 分母 n_articles 与 ctx 共享同一套统计口径。留篇门控自 2026-06-29 起统一为 full-only: 一篇报道是否被认定为"有效的银行—金科报道"只看 llm_verified_full 是否为 True, ctx/ss 两轨在此基础上退化为 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集合的子集, 但各轨自身的 idf_tone_sum 仍按各自轨道文本独立计算 tf(w, article) 打分, 不借用 full 轨的分值。
面板层聚合发生在 pipeline/panel/export.py: 文章级 idf_tone_sum (逐轨) 先按 bank-year 分组, 再取算术均值, 得到本家族三个面板列。分组前已经过 stage 13 共现硬过滤 (银行×金科邻近共现) 与 stage 21 情感 LLM 的 full-only 留篇门控, 因此进入聚合的文章行宇宙与项目内其他情感/属性面板列 (如 llm_vote_tone_full、其余词典口径) 共享同一套"哪些文章算数"的口径, 差异只体现在打分公式本身。

【文献定位】
you_2018 词典的构念根基来自 You, Zhang & Zhang (2018, Review of Financial Studies)"Who Captures the Power of the Pen?", 该文构建中文金融情感词典并将其用于研究媒体报道语气与公司治理/资本市场结果的关系, 是项目内中文金融文本情感词典谱系 (与 jiang_2021/yao_2021/bian_2021/du_2022/loughran 并列) 的组成锚点之一。idf_tone_sum 的 IDF 加权思路呼应词典/词库方法在情感分析文献中的一般性做法: Taboada et al. (2011) 在 Computational Linguistics 综述了基于词典的情感分析方法学, 强调词的语料统计特征 (稀有度、位置、否定/转折上下文) 应折算进打分而非简单计数; Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 系统评估了经济文本上词典法的构建与校准问题, 指出词权重设定对测度效度的影响不可忽视, 与本家族用 IDF 替代均一权重的动机一致。Du, Huang, Wermers & Wu (2022, Review of Finance) 构建的中文金融情感词典 du_2022 是本项目内 you_2018 的姊妹口径, 两部词典虽独立构建但共享"通用情感词典在金融领域信号偏弱、需要领域特化"的问题意识, 本项目将二者及另外四部词典并列而非相互替代, 呼应 Frankel, Jennings & Lee (2022, Management Science) 关于词典法与机器学习法应互为稳健性检验而非相互取代的方法学立场——本项目进一步把这一"互为稳健性"的精神细化到词典内部的多种打分口径 (计数/均一权重/IDF 加权) 与三文本轨道两个维度上。Ma, Zhang & Zhang (2025, Expert Systems with Applications) 近年提出面向中国投资者的细粒度情感词典 CN-FSD, 延续了中文金融语境下词典法仍具有可解释性优势、适合与黑箱模型 (BERT/LLM) 并列作为稳健性锚点的判断, 支持本项目在情感三法 (词典/BERT/LLM) 之间设置多重互证结构、而非仅依赖单一测度的设计取向。 至于本家族「词典词条不应等权计入、须按信息量差异化赋权」这一前提本身, Aysan、Caporin 与 Cepni (2024) 提供了近期的实证呼应: 该文以日内跳跃检测配合 logistic 回归, 发现信息发布提高跳跃概率, 且局限于情绪类或关涉市场基本面的情感维度比其它维度更易引发跳跃, 据此提出词并非生而等权的论断。须严格限定该锚点的适用口径: 原文所称的「非等权」是情感维度/类别层面 (情绪 vs 基本面) 的差异, 而非本家族按语料稀有度施加的词项级 IDF 加权 (raw_idf(w) = log₁₀(N/(1+df(w))), 再经均值归一化与 P1/P99 Winsorize), 二者只在「反对等权」这一动机上相通, 函数形式与信息来源完全不同; 其标的为加密货币日内跳跃、语料为英文新闻, 既无 bank-year 求和聚合亦无三轨文本口径, 因此该文只锚差异化赋权的动机, 不锚本家族 IDF 权重的具体构造与打分公式。
## VAR: you_2018_idf_tone_sum_ctx

【变体差分】
本列使用 ctx 轨文本 (标题 + 围绕目标银行/金科实体的窗口文本, 由 stage 14 ctx_materializer 以 prepend_title 方式物化) 作为逐篇 tf(w, article) 打分的文本基础; idf(w) 权重本身不在 ctx 轨语料上单独重算, 而是与 full/ss 两轨共享同一份基于 content_full 统一计算的 idf(w) (smooth IDF + 均值归一化 + P1/P99 Winsorize, 见 CORE), 三轨差异不来自 IDF 统计量。ctx 轨与 full 轨的核心差异在于: 逐篇计算 tf(w, article) 时使用的文本范围收窄到围绕目标实体的窗口文本而非全文正文, 因此同一情感词在同一篇文章上, ctx 轨的 tf(w, article) 一般小于或不同于 full 轨 (窗口外的词频不计入), 用相同的 idf(w) 乘以不同的 tf 后累加, 使 ctx 轨的 idf_tone_sum 与 full 轨产生差异, 这是三轨互为稳健性而非互相替代的直接来源。ctx 轨的构念意图是聚焦"报道中紧贴目标实体的那部分语气", 剔除全文中与银行—金科关系无关的段落对打分的稀释或污染, 但也因窗口更短、tf 基数更小而更易受个别高权重稀有词左右, 数值波动性通常大于 full 轨。行宇宙口径遵循 2026-06-29 确立的 full-only 留篇门控: 本列只在 llm_verified_full == True 的文章子集上计算与聚合, 是 conditional-on-full 的测度轨, 不构成独立的留篇判定标准。本列与 you_2018_idf_tone_sum_full、you_2018_idf_tone_sum_ss 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一个 over-identified Hansen J 检验中同时使用三轨列作为过度识别的工具变量或内生变量替代。

## VAR: you_2018_idf_tone_sum_full

【变体差分】
本列使用 full 轨文本 (标题 + 完整正文全文, prepend_title 拼接) 作为逐词 tf·idf 打分与 IDF 统计的语料基础, 是本家族的默认/规模最大的文本口径, 也是项目内多数 P1 主线情感/属性变量 (如 llm_vote_tone_full) 采用的同名后缀轨道, 与之在"文本覆盖面最全"这一属性上口径一致 (但打分方法不同, llm_vote_tone_full 是三家 LLM 多数投票, 本列是词典 IDF 加权计数, 二者互为方法学稳健性, 非同一构念的重复)。IDF 统计的 N 与 df(w) 覆盖该轨全部已通过 stage 13 共现硬过滤、stage 21 llm_verified_full == True 门控的文章全文, 因此在样本覆盖上是三轨中最宽的一支, 情感词稀有度估计也最稳定 (样本量最大、抽样噪声最小)。留篇门控本身即以 full 轨的 llm_verified_full 为准绳, 本列与该门控同源, 是三轨中唯一"既定义门控、又被门控约束"的一支, ctx/ss 两轨则是在此基础上派生的条件测度轨。本列与 you_2018_idf_tone_sum_ctx、you_2018_idf_tone_sum_ss 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一个 over-identified Hansen J 检验中同时使用三轨列。使用建议: 若研究关心的是报道整体基调对银行—金科关系的总体渲染 (例如报道篇幅、行业背景铺陈等边缘信息是否也裹挟进语气测度), full 轨是三者中信息量最完整、也最贴近读者实际感知的一支, 适合作为主设定 (primary specification); ctx/ss 两轨则用于检验结论是否被无关段落的语气噪声驱动, 三者共同构成一条从"全文"到"实体窗口"再到"严格同句"的构念收紧梯子, 供研究者按信息完整度与判据严格度做权衡取舍, 而非彼此竞争的替代关系。

## VAR: you_2018_idf_tone_sum_ss

【变体差分】
本列使用 ss 轨文本 (标题 + 银行∧金科同句共现窗口文本, 判据镜像 ctx 但共现半径收紧到严格同句±N, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 作为逐篇 tf(w, article) 打分的文本基础, 是三轨中文本范围最窄、判据最严格的一支。与 full/ctx 两轨相同, ss 轨不单独重算 idf(w): 三轨共享同一份基于 content_full 统一计算的 IDF 权重体系 (smooth IDF + 均值归一化 + P1/P99 Winsorize), ss 轨对该共享权重不做任何调整或重估。ss 轨与其余两轨的差异只体现在逐篇 tf(w, article) 的取值范围上: 仅统计满足银行—金科同句共现条件的窗口文本内的词频, 窗口外内容 (即便在 full/ctx 范围内) 一概不计入 tf。对于不存在银行∧金科同句共现的文章, ss 轨执行镜像 ctx 的回退语义: content_ss 退化为全文 body (等同于该篇的 full 轨文本), 对应 ss_is_fallback 标记为 True, 此时该篇在 ss 轨下的 tf(w, article) 实际是在全文文本上统计, 但打分仍使用与 full/ctx 相同的共享 idf(w) (回退篇与非回退篇共享同一个分母 n_articles, 不做二次拆分)。这一设计使 ss 轨在"金科与银行紧密同句提及"的样本上给出最严格意义下的语气测度 (差异来自 tf 的文本范围收窄, 而非另起炉灶的 IDF 统计), 同时通过优雅降级避免因共现条件过严而丢失整篇文章的语调信息。本列与 you_2018_idf_tone_sum_full、you_2018_idf_tone_sum_ctx 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一个 over-identified Hansen J 检验中同时使用三轨列。使用建议: ss 轨适合用来回答"当报道明确把银行与金科在同一句话里放在一起谈论时, 语气是正面还是负面"这一更精细的问题, 排除了银行与金科分处全文不同段落、彼此并无直接语义关联却被 stage 13 共现硬过滤纳入的边缘样本, 因而对"银行—金科关系"本身的语气刻画理论上噪声最小、但受回退语义影响, 在共现稀疏的样本上会退化为与 full 轨高度重合, 解读时应结合 ss_is_fallback 标记区分真严格同句样本与回退样本两个子群体。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43–96. https://doi.org/10.1093/rfs/hhx055
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673–719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514–5532. https://doi.org/10.1287/mnsc.2021.4156
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125–143. https://doi.org/10.1111/ecin.13264
Aysan, A. F., Caporin, M., & Cepni, O. (2024). Not all words are equal: Sentiment and jumps in the cryptocurrency market. Journal of International Financial Markets, Institutions and Money, 91, 101920. https://doi.org/10.1016/j.intfin.2023.101920
<!-- rendered-citations:end -->
