---
family_id: F645
columns:
- you_2018_neg_count_ctx
- you_2018_neg_count_full
- you_2018_neg_count_ss
unit: 篇数/计数 (count)
formula: 逐篇对分词后正文按 you_2018 词典 negative 词表(1,583 词, 与 positive 侧 5 词跨类重叠、按用户决策两侧保留计数)做逐词典命中扫描, 命中一次计数加一, 得到该篇该轨的原始负向词命中总数 neg_count; 三个后缀列分别对应 full/ctx/ss 三条文本轨各自独立的逐篇计数, 面板层再按银行-年聚合(常见口径为 sum/mean, 具体聚合函数以 stata_export.py 标签映射与 panel 聚合脚本为准)
producer: pipeline\sentiment\tone_words.py (逐篇分词打分, you_2018 词典加载与命中计数原语); pipeline\panel\stata_export.py (Stata 变量标签映射, 不改变数值口径)
upstream: []
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
  vol: ''
  issue: ''
  pages_or_artno: '3446388'
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: 'Negation scope detection in sentiment analysis: Decision support for news-driven trading'
  venue: Decision Support Systems
  vol: '88'
  issue: ''
  pages_or_artno: 67-75
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: Financial reporting complexity and investor underreaction to 10-K information
  venue: Review of Accounting Studies
  vol: '14'
  issue: '4'
  pages_or_artno: 559-586
- doi: "10.1016/j.jcorpfin.2026.103033"
  type: "journal"
  authors: "Battalio, R., Loughran, T., & McDonald, B."
  year: 2026
  title: "How managers frame capital budgeting in investor communications"
  venue: "Journal of Corporate Finance"
  vol: "100"
  pages_or_artno: "103033"
- doi: "10.1016/j.cjar.2025.100406"
  type: "journal"
  authors: "Zhao, J., & Ren, M."
  year: 2025
  title: "Innovative or conservative? How clan culture shapes bank digital transformation in China"
  venue: "China Journal of Accounting Research"
  vol: "18"
  issue: "2"
  pages_or_artno: "100406"
new_dois: []
---

## CORE

【构念与来源】
you_2018_neg_count 家族测度的是"一篇报道里出现了多少个负面情感词", 是文本情感分析里最原始、最不加工的一层信号: 不做归一化, 不做方向翻转, 只是老老实实数词。它的构念来源是 You, Zhang & Zhang (2018, Review of Financial Studies)《Who captures the power of the pen?》一文构建的中文金融情感词典(you_2018), 该词典含 positive(1,425 词) / negative(1,583 词) 两个极性词表, 另含 definite(388 词) / ambiguous(178 词) 两个非极性词类(后者用于 clarity 族测度, 与本家族无关)。本项目在 `pipeline/sentiment/tone_words.py` 中把该词典作为六部情感词典之一(另五部为 jiang_2021、yao_2021、bian_2021、du_2022、loughran_mcdonald_zh_2026)并行加载, 逐篇、逐词典独立打分, 六部词典互为稳健性、不分主次地并排检验同一构念(报道语调), 而非彼此嵌套或取代关系。neg_count 是这条打分流水线里最靠前的一个中间产物: 在归一化为 tone/score 之类可比较的比率型测度之前, 先在词表命中层面记一次"生汤"计数, 供后续 tone/score 计算复用, 也单独暴露给下游作为"负面词密度"这一构念的原始度量。
【方法学与计算】
计算过程严格遵循 tone_words.py 的通用词典打分流程: 先对文章文本做中文分词(jieba, 版本冻结为 0.42.1 以保证跨 run 的确定性复现), 然后拿分词结果逐词比对 you_2018 词典的 negative 词表, 命中一次即计一次, 不做词频封顶、不做逆文档频率(idf)加权 —— idf 加权版本是另一族测度(参见 `*_idf_tone_sum` 系列), 与本家族原始计数正交。you_2018 词典本身在加载阶段对 positive∩negative 跨类重叠的 5 个词采用"两侧保留"策略(2026-06-24 用户决策, 逆转此前的单侧剔除做法): 重叠词在 positive 与 negative 两个计数器里都各计一次, 这样做的原因是词典本身把这些词同时收录进两个极性表, 项目组认为强行去重会引入主观判断误差, 保留双计更接近词典原始设计意图, 同时也保证了后续 union/msent/ratio 等派生测度的极性 margin 守恒(重叠词以对称 (+1,−1) 计入固定并集词典, 不改变净语调)。三个后缀列 `_full` / `_ctx` / `_ss` 对应的是本项目三轨文本架构下各自独立跑的同一套计数流程, 而不是同一次计数结果的三种切片; 三轨的文本来源不同(full = 标题拼正文全文, ctx = 标题拼实体窗口, ss = 标题拼银行∧金科同句±N窗口), 因此三列数值天然不同且不可相互还原。三轨之间是各自 just-identified 并排、互为稳健性、不分主次的关系, 铁律要求它们绝不可混入同一个 over-identified 的 Hansen J 检验框架, 因为把三条本质上度量不同文本范围的信号硬凑进同一超识别方程会人为制造过度识别约束, 掩盖三轨各自的边际信息。
【文献定位】
you_2018 词典的方法学根基来自 You, Zhang & Zhang (2018, Review of Financial Studies)《Who captures the power of the pen?》, 该文首创了针对中国资本市场语境的中文金融情感词典构建思路, 用于研究媒体报道语调对信息环境、股价发现效率的影响机制, 是本项目情感测度族里六部词典中本土化程度较高、且专门面向中国上市公司信息披露与媒体报道场景设计的一部, 与偏英文语境翻译扩充而来的 jiang_2021、bian_2021、loughran 系列形成方法论互补。作为最基础的逐词命中计数, neg_count 家族的角色定位是国内外词典法情感测度文献里普遍确立的"词典命中计数是语调测度的第一层构件"传统的一个具体实现 —— 后续的 tone(标准化语调得分)、score(带语言学规则调整的加权得分)都建立在 pos_count / neg_count 这一层原始计数之上。在方法学谱系上, neg_count 也呼应 Bian, Jia, Li & Yan (2021)提出的中文金融情感词典构建规范, 以及 Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 关于情感分析中否定词处理机制的讨论 —— 本家族的 neg_count 是"否定规则介入前"的裸计数, 与同族的 negonly/negdeg 等语言学规则消融变体形成对照, 后者在 neg_count 基础上叠加否定翻转规则重新计分, 两者构成规则消融梯度上相邻的两级, 彼此正交、互为稳健性检验, 不可混同解读。此外, 从测度哲学上看, 逐词计数这一路径也与 You, H., & Zhang, X.-J. (2009, Review of Accounting Studies)在披露复杂度测度上采取的"表层可数特征(如文档长度、生僻词占比)直接计数、不做语义加权"的朴素计量思路一脉相承 —— 两者都属于"先以可复现的表层特征计数作为构念代理, 再在其上叠加更复杂的加权/归一化处理"这一测度构建范式, neg_count 与该文的复杂度计数指标分属情感与复杂度两个不同构念, 但方法论血缘相近, 可作为本家族"裸计数优先于加权测度"这一设计取舍的一个跨构念参照。 就这一构造形态在当代金融顶刊中的存续状态而言, Battalio、Loughran 与 McDonald (2026) 自建 45 个资本预算术语的词表, 对 2010–2020 年业绩说明会文本做逐词命中统计以刻画管理者的措辞框架, 直接证明「固定词表逐词命中、不做长度归一、不跨词表聚合」的原始词次计数至今仍属活跃做法, 且该文有金融词典法原始提出者参与, 恰可锚定 neg_count 这一裸计数层的形态取舍。惟须严格限定: 原文测度的是术语使用频次而非情感极性, 既不作正/负面判定, 词表亦为英文术语表且无否定翻转/程度副词/转折规则层, 分析单元为公司-披露文档, 因此它只锚定原始命中词次的构造形态, 不为本家族 negative 侧的极性方向提供任何背书。同域参照方面, Zhao 与 Ren (2025) 以中国商业银行为样本, 发现宗族文化经短半径信任推高物理网点与人员依赖、风险规避降低风险承担意愿等机制抑制银行数字化转型, 与本项目同国别、同行业且同为银行-年层的文本型变量, 可作为「中国银行业以文本型变量构造银行-年测度」的同域存在性参照。仅此: 原文该测度是否为分词后固定词表逐词命中计数在可得材料中未见披露、未经核实, 故不可据此宣称词表命中频次的技术路线获得背书; 其词表 (若有) 为数字化/科技关键词而非情感词表, 文本源为每银行-年单份年报而非第三方新闻逐篇计数后聚合, 亦无三规则层与 full/ctx/ss 三轨设计。
## VAR: you_2018_neg_count_ctx

【变体差分】
本列使用的文本轨道是 ctx(实体窗口轨): 由 `14_materialize_ctx` 阶段在标题前拼接后, 正文部分只截取目标银行实体周围的窗口范围文本, 而非全文。因此 you_2018_neg_count_ctx 统计的是"银行实体附近窗口内出现了多少个 you_2018 负面词", 而不是整篇报道全文的负面词密度。这条轨道的设计意图是把情感信号聚焦到与目标银行直接相关的语境, 剔除报道里可能涉及的其它无关内容(例如同一篇报道里穿插的宏观经济评论、其它公司新闻)带来的噪声, 因而比 full 轨在"该银行本身语境"这一维度上更聚焦、但覆盖的词汇总量天然更少, 计数的绝对值通常系统性低于同篇 full 轨的对应值, 二者不可直接相减或做差值解读, 只能作为互为稳健性的并列证据看待。当一篇文章没有可识别的实体窗口锚点或该银行未在窗口逻辑下被定位时, ctx 轨会退回全文本作为窗口内容并标记 `is_fallback`, 这一退回机制与 ss 轨的退回语义是镜像对称的, 但退回后 ctx 与 ss 各自计算的 negative 命中数仍然是各自独立跑出来的, 不会因为共享退回内容而在数值上完全一致(除非两者都退回且退回文本相同)。使用该列做实证分析时, 若报道未通过留篇门控(full-only 口径下 `llm_verified_full == True` 才算一篇有效银行金科报道), ctx 轨的该值属于条件在 full 留篇集合子集上的稳健性/补充测度, 行宇宙范围严格是 full 留篇集合的子集而非独立样本。

## VAR: you_2018_neg_count_full

【变体差分】
本列使用的文本轨道是 full(全文轨): 文本内容为标题前置拼接完整正文全文, 是三轨里覆盖信息量最大、也是三轨中唯一承担"是否算一篇银行金科报道"这一留篇门控职能的轨道(2026-06-29 起确立的 full-only 口径: 无论 ctx/ss 判定结果如何, 只要 `llm_verified_full == True` 就纳入分母, ctx/ss 转为条件在该集合上的稳健性测度)。因此 you_2018_neg_count_full 是本家族里唯一的"主轨"计数, 数值上覆盖全篇正文里出现的全部 you_2018 negative 词命中次数, 不受实体窗口或同句共现范围限制, 是三轨里绝对数值通常最大、方差也相对最稳定的一列, 常被面板聚合层用作默认参照臂或与 llm_vote_tone_full 等 P1 主处理变量并列做交叉验证的候选控制变量。需要强调的是, full 轨虽然承担留篇门控职能, 但这并不意味着它在稳健性检验意义上优先于 ctx/ss —— 三轨之间仍严格遵循"各自 just-identified 并排、互为稳健性、不分主次"的铁律, full 只是在样本纳入这一独立维度上被指定为唯一裁判, 与其作为情感测度本身的地位无关, 二者是正交的两件事, 不应混为一谈, 更不能把 full 轨的计数值直接等同于"更权威的情感信号"。

## VAR: you_2018_neg_count_ss

【变体差分】
本列使用的文本轨道是 ss(同句轨): 由标题前置拼接目标银行与金科词严格同句(±N窗口, 默认半径 1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 与 stage 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个独立配置键, 不可混用)共同出现的句子集合而成, 是三轨里文本范围最窄、判据最严格的一条。you_2018_neg_count_ss 统计的是这个严格共现句子集合内出现的 you_2018 negative 词命中数, 意在捕捉"银行与金融科技被同一句话直接关联提及"这一最紧密语境下的情感基调, 是对 ctx 轨"实体窗口"概念的进一步收紧。当一篇报道不存在银行与金科的同句共现(例如两者虽同篇出现但分散在不同段落)时, ss 轨退回全文 body 作为内容并标记 `ss_is_fallback = True`, 这一退回逻辑镜像 ctx 轨的退回语义(共享 `n_articles` 分母口径), 退回后该篇的 ss 计数实质上等同于对全文重新跑一遍计数, 但仍与 full 轨列各自独立执行、独立落盘, 不做数值复用短路。当上游 `FINTECH_AC` 词典对象为 None(金科词识别失效)时, 三轨的 `*_is_fallback` 会整体优雅退化为全 True, ss 轨在这种情形下事实上退化为 full 轨的重复计数, 使用者在解读跨样本 ss 轨的统计特征时应留意这一退化边界情形, 不宜将其误判为真实的"同句强共现"信号缺失。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Battalio, R., Loughran, T., & McDonald, B. (2026). How managers frame capital budgeting in investor communications. Journal of Corporate Finance, 100, 103033. https://doi.org/10.1016/j.jcorpfin.2026.103033
Zhao, J., & Ren, M. (2025). Innovative or conservative? How clan culture shapes bank digital transformation in China. China Journal of Accounting Research, 18(2), 100406. https://doi.org/10.1016/j.cjar.2025.100406
<!-- rendered-citations:end -->
