---
family_id: F452
columns:
- neg_frac_noncity_ctx
- neg_frac_noncity_full
- neg_frac_noncity_ss
unit: 比率/占比 (proportion, [0,1])
formula: 'neg_frac_noncity_{trk} = count(articles with tone_{trk} < 0 AND outlet ∉ home-city media set) / count(articles with outlet ∉ home-city media set), 逐银行-年聚合, 分子分母同轨 {trk} ∈ {full, ctx, ss}'
producer: pipeline\panel\attention_media.py
upstream:
- 21_tone_llms
- 11_news_bank
- config/bank_addresses.json
- 国家地区/省份 (原始新闻元数据列, 媒体来源省份)
- 城市 (原始新闻元数据列, 媒体来源城市)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: Political incentives to suppress negative information Evidence from Chinese listed firms
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: Investor negativity derived from news shapes firm distress dynamics under bounded rationality
  venue: Journal of Economics and Development
  vol: '27'
  issue: '4'
  pages_or_artno: 309-321
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach
  venue: Social Network Analysis and Mining
  vol: '15'
  issue: '1'
  pages_or_artno: Article 20
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: Negation scope detection in sentiment analysis Decision support for news-driven trading
  venue: Decision Support Systems
  vol: '88'
  pages_or_artno: 67-75
- doi: "10.1016/j.frl.2024.105024"
  type: "journal"
  authors: "Huang, W., Liu, J., & Zhang, R.-Z. (."
  year: 2024
  title: "Local newspaper closures and non-GAAP reporting quality"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105024"
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量"异地媒体负面报道占比"——银行-年面板上, 由非家乡城市 (non-home-city) 媒体来源发出、且情感判为负面的报道数量, 占该银行当年全部"非家乡城市媒体报道"总量的比例。构念根植于地理邻近性对媒体报道倾向的影响这一文献传统: Gurun & Butler (2012, *The Journal of Finance*) 提出并证实, 本地媒体 (home media) 相较异地媒体在报道口径上存在系统性差异——本地媒体因广告收入依赖、读者关系与信息获取便利, 倾向于产出对本地企业更正面 (或更少负面) 的报道, 而异地/非本地媒体缺乏这层利益纠葛与人情因素, 报道更趋"中性到负面"。`neg_frac_noncity` 正是把这一"本地-异地"媒体报道倾向差异性检验落到"负面占比"这个具体统计量上, 与家族内并列的 `neg_frac_homecity`(家乡城市负面占比)、`tone_gap_homecity_noncity`(两者语气差) 共同构成"地理邻近性-媒体口径"这一维度⑨的完整测度组。城市 (city) 与省份 (province) 是两个粒度并行的地理切分口径, `neg_frac_noncity` 属城市粒度分支 (对应省份粒度分支为 `neg_frac_nonprov`), 两者原语相同、地理单位不同, 互为粒度稳健性而非包含关系。

【方法学与计算】
本家族的真实计算逻辑落在 `pipeline/panel/attention_media.py` 维度⑨ (地理邻近性, 同省/同城双层) 中, 而非面板导出模块——导出模块 (`pipeline/panel/export.py`) 只承载列名到 Stata 变量标签的字符串映射, 并不参与数值计算。分子分母的口径链条: 首先由 stage 11 `news_bank` 识别每篇报道的目标银行; 其次 `attention_media.py` 加载 `config/bank_addresses.json` 取得各银行注册地省份/城市, 与原始新闻元数据列「国家地区/省份」「城市」(经地名后缀清洗标准化) 逐行比对, 生成 `_is_homecity` 布尔编码 (1=同城/家乡城市媒体, 0=非同城/异地媒体, NaN=地理信息缺失时的显式出域, 不计入任一侧, 避免"来源不可知"被误判为异地); 再次由 stage 21 三家 LLM 投票情感在各轨给出逐篇 `is_negative_{trk}` 二值标记 (负面判定); 最后在银行-年面板聚合层, 对 `_is_homecity == 0` (noncity) 子集分别按轨 groupby(['target_bank','year']) 取 `is_negative_{trk}` 均值, 即 `neg_frac_noncity_{trk}` = (该银行-年内, 属 noncity 媒体子集且该轨情感为负的报道篇数) / (该银行-年内属 noncity 媒体子集的报道总篇数), 分子与分母严格同轨 {trk} 计算, 不跨轨借用分母。当某银行-年 noncity 媒体报道子集为空 (`sub.empty`) 时, groupby 结果天然缺该银行-年行, merge 后落为 NaN (避免 0/0 除法产生虚假 0 值)。变量口径继承 stage 21 的留篇门控与三轨架构: 门控 (是否判定为"一篇银行金科相关报道") 恒以 `llm_verified_full == True` 为准 (2026-06-29 起 full-only 门控铁律), ctx/ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但情感极性判定 (`is_negative_{trk}`) 逐轨独立计算, 不共用同一份判定结果; noncity 地理归属标签 (`_is_homecity`) 本身与文本轨道正交, 三轨共享同一套地理判据, 差异只落在情感极性判定环节。

【文献定位】
`neg_frac_noncity` 及其同族变量的地理邻近性构念直接承接 Gurun & Butler (2012, *The Journal of Finance*) 的本地媒体偏向 (local media bias) 框架——该文以美国上市公司为样本, 证明本地媒体对本地企业的报道正面度显著高于异地媒体, 且这一差异可预测公司未来经营绩效, 从而为"媒体地理距离影响报道倾向"提供了顶刊实证基础。本项目将该框架平移到中国银行业语境, 用"城市/省份"两级地理粒度、"负面占比/语气均值/语气差"三类统计量构造对应测度组, `neg_frac_noncity` 是其中"异地负面占比"一支。情感判定本身继承本项目的负面度量传统: 报道级情感极性来自三家 LLM 多数投票共识, 而"负面"这一二值判据的可靠性关切与新闻语境下否定处理 (negation handling) 的一般性方法学问题相关——Punetha & Jain (2025, *Social Network Analysis and Mining*) 与 Pröllochs, Feuerriegel & Neumann (2016, *Decision Support Systems*) 均指出, 情感分析中否定词处理不当会系统性扭曲负面判定的准确率, 这构成本项目在 stage 21/22 情感引擎设计 (LLM 三家投票 + 词典否定翻转规则) 时的方法学背景参照, 而非直接被 `neg_frac_noncity` 调用的算法组件。此外, 负面新闻对企业/银行经营动态的下游影响近年在中国及新兴市场语境下持续被证实, 如 Pham, Huynh, Nguyen & Luu (2025, *Journal of Economics and Development*) 发现投资者由新闻感知到的负面情绪会经由有限理性渠道影响企业困境动态, 为本家族"异地负面报道占比"这一自变量族的下游经济后果解释提供了理论呼应。本家族"noncity 负面占比"这一操作化选择还与 Piotroski, Wong & Zhang (2015, *Journal of Accounting Research*) 关于中国上市公司政治动机压制负面信息的发现相呼应——该文证明地方国有企业存在系统性抑制负面消息披露的政治激励, 而这种抑制在本地 (家乡) 信息渠道中更容易实现、在异地渠道中则更难被同等程度地施加, 从侧面为"家乡媒体 vs. 异地媒体负面占比存在系统性差异"这一构念提供了中国语境下的制度性解释: `neg_frac_noncity` 相对偏高、`neg_frac_homecity` 相对偏低的模式, 既可归因于 Gurun & Butler (2012) 式的本地媒体商业利益驱动的正面倾斜, 也可部分归因于 Piotroski 等 (2015) 式的本地政治关系驱动的负面信息压制, 二者在中国银行业语境下往往同时起作用、难以完全分离, 这是解读本变量组时需要留意的构念混淆来源。 在近期文献中, 上述本地/异地媒体二分的构念前提又获得两条独立的补强。Huang、Liu 与 Zhang (2024) 以美国本地报纸停刊作为本地媒体监督减弱的冲击, 检验公司非 GAAP 披露质量的相应变化, 其识别前提正是总部同城的本地媒体与异地媒体在监督功能上不可相互替代——这恰是本家族按媒体来源城市切出 homecity / noncity 两个子样本、并以负面占比作组间对比的构念依据; 需注意该文走的是停刊事件的 DiD 识别, 本家族则是横截面上的同城/异城子样本对比, 且其被解释变量为披露质量而非媒体语调本身, 该文并未度量本地媒体的报道倾向, 故此处只锚定“本地媒体构成不可替代的独立信息渠道”这一半, 不锚定其语调算法。Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度并将其应用于意大利银行的融资条件, 是“新闻语调 → 银行层级结果”这一链条的近期同域实践, 与本家族由报道级情感聚合到银行-年比率测度、再服务于银行层级结果的应用域一致; 但该文语料为意大利媒体 (意/英文), 其语调测度既未使用中文情感词典亦无三家 LLM 投票共识口径, 更无 full/ctx/ss 三轨文本切分与同城/异城媒体划分, 因此仅作同域存在性参照, 不构成对本家族具体构造口径的直接支持。
## VAR: neg_frac_noncity_ctx

【变体差分】
本列是 `neg_frac_noncity` 家族在 ctx (entity-window context) 轨上的实现: 分子分母的情感极性判定均取自 stage 21 对 `content_ctx` (标题+目标银行实体窗口文本) 的三家 LLM 投票结果, 而非全文正文。ctx 轨与 full 轨、ss 轨在方法论地位上完全对等——三轨"各自 just-identified 并排、互为稳健性、不分主次", 严禁将三轨情感测度混入同一个 over-identified Hansen J 检验框架 (会破坏过度识别约束的独立性假设)。ctx 轨的行宇宙是 full 轨留篇集 (`llm_verified_full == True`) 的子集, 即门控恒以全文判定为准, ctx 只在门控通过的报道范围内提供"聚焦于银行实体窗口"的情感测度, 用于检验负面占比结论是否对"是否纳入全文语境噪声"稳健。noncity 媒体归属的地理判据本身与文本轨道无关, 仅由发稿媒体与银行总部城市的比对决定, 三轨在这一步共享同一套 noncity 归属标签, 差异完全落在情感极性判定环节。
本轨相较家族 canonical (full 轨) 的精确差分在于: 当一篇报道的全文语境与实体窗口局部语境对情感极性判断产生分歧时 (例如全文整体基调正面但涉及目标银行的具体语句偏负面, 或反之), ctx 轨会给出与 full 轨不同的极性标签, 进而影响该银行-年落入分子的计数。由于分母 (noncity 报道总篇数) 在 full/ctx/ss 三轨下理论上一致 (均由留篇门控决定行宇宙、经济含义仍是"该银行-年的 noncity 媒体报道总量"), 三轨差异主要体现在分子 (负面篇数) 上。研究者在解读时应将 ctx 轨结果作为 full 轨主结果的稳健性佐证, 若两轨方向一致、显著性相近, 则说明"异地媒体负面偏向"结论不依赖于是否引入全文语境的额外信息; 若出现系统性偏离, 则提示全文层面的负面语气可能部分来自与目标银行无直接关系的段落 (如报道中夹叙的行业背景负面信息), 值得在稳健性附录中专门讨论。

## VAR: neg_frac_noncity_full

【变体差分】
本列是家族的 canonical / headline 轨, 情感极性判定取自 stage 21 对全文 `content_full` (标题+正文全文) 的三家 LLM 投票结果 (`llm_vote_tone_full`)。留篇门控本身即以 `llm_verified_full == True` 为准 (2026-06-29 起的 full-only 铁律), 因此 full 轨天然享有"门控口径与测度口径一致"的优势, 是本家族及绝大多数下游 paper 处理变量 (treatment) 的首选主测度; 例如 P1 `bank_fintech_tone` 主轨即已切至 `_full`。full 轨与 ctx、ss 两个稳健性轨"各自 just-identified 并排、互为稳健性、不分主次", 三者严禁混入同一个 over-identified Hansen J 检验; 在多轨联合呈现的稳健性表格中, full 轨通常置于首列作为基准, 但这只是呈现顺序惯例而非统计意义上的"更优"地位声明。
`neg_frac_noncity_full` 的具体差分语义在于: 全文文本涵盖标题、正文导语、主体叙述与结尾评论等全部语言材料, 情感判定天然吸收了报道全篇的整体基调, 因此更容易捕捉到"记者/编辑对整篇报道的总体立场", 但也更容易被与目标银行无直接关联的段落 (行业综述、监管政策背景、其他银行并列提及等) 拖动极性判断。分母口径与 ctx/ss 轨一致, 均为该银行-年内 noncity 媒体报道且通过 full-only 留篇门控的总篇数; 分子为其中 full 轨情感极性为负的篇数。当 `FINTECH_AC` 词典缺失或某银行-年无 noncity 媒体报道时, 本列按项目惯例优雅降级为 NaN, 不参与静默填零, 避免下游回归把"无异地媒体样本"误判为"异地媒体零负面"。

## VAR: neg_frac_noncity_ss

【变体差分】
本列是家族的 ss (same-sentence, 银行∧金科词同句共现窗口, ±N 句半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 轨, 情感极性判定取自 stage 21 对 `content_ss` 的三家 LLM 投票结果。ss 轨的回退语义严格镜像 ctx 轨: 当某篇报道中不存在银行与金科词同句 (或半径窗内) 共现时, `content_ss` 回退为全文 body, 对应 `ss_is_fallback` 标记为 True, 并与 `n_articles` 共享同一分母口径; 若 `FINTECH_AC` 词典整体缺失, 则 `*_is_fallback` 全量置 True, 测度优雅降级为等同于全文口径, 而非报错或产出空值。ss 轨与 full、ctx 轨同样"各自 just-identified 并排、互为稳健性、不分主次", 三者结果禁止混入同一个 over-identified Hansen J 检验框架。
本列相较家族 canonical (full 轨) 的精确差分在于: ss 轨的文本窗口最窄, 情感判定聚焦在银行与金科词严格共现的句子邻域, 理论上最能剔除与"银行-金科"主题无关的语境噪声, 但也因窗口收窄而更依赖共现是否成立——当共现缺失触发回退时, 该篇报道在 ss 轨上的情感判定退化为与 full 轨相同, 此时 ss 轨与 full 轨在该篇报道上不再提供额外区分度, 是研究者在解释 ss 轨与 full 轨差异幅度时需要留意的机制性来源 (差异幅度部分取决于回退发生的比例)。分子分母的地理归属判据 (noncity) 与轨道无关, 仍由发稿媒体与银行总部城市比对决定; 分母口径与 full/ctx 轨一致, 均以 full-only 留篇门控划定的行宇宙为准。在早期试跑样本 (T=2) 上, 由于报道量有限, ss 轨回退比例可能偏高, 该轨与 full 轨的数值差异幅度在生产语料 (T=19) 上预期更具区分力。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Huang, W., Liu, J., & Zhang, R.-Z. (. (2024). Local newspaper closures and non-GAAP reporting quality. Finance Research Letters, 62, 105024. https://doi.org/10.1016/j.frl.2024.105024
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
