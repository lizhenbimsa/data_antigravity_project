---
family_id: F450
columns:
- neg_frac_homecity_ctx
- neg_frac_homecity_full
- neg_frac_homecity_ss
unit: 比率/占比 (proportion, [0,1] 区间; 分母为该银行-年在"本市媒体"子样本中的报道篇数, 分子为其中判定为负面的篇数)
formula: 'neg_frac_homecity_trk = count(articles where outlet_city == bank_home_city AND tone_trk == negative) / count(articles where outlet_city == bank_home_city), 三轨(trk∈{full,ctx,ss})各自独立计算; 当该银行-年无本市媒体报道时缺失为 NaN(非 0)'
producer: pipeline\panel\attention_media.py::compute_media_heterogeneity() (地理邻近性维度⑨代码块, 指标3"负面过滤"; 上游情感判定来自 21_tone_llms / encode.py 三轨情感列 llm_vote_score_{track}/is_negative_{track})
upstream:
- llm_vote_score_full
- is_negative_full
- llm_vote_score_ctx
- is_negative_ctx
- llm_vote_score_ss
- is_negative_ss
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
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
本家族衡量"本地媒体对银行的负面报道强度"这一构念, 属地理邻近性维度⑨(与 homeprov 省级子族并排)的城市级别子测度。核心思想源自 Gurun & Butler (2012, Journal of Finance) 对本地媒体倾向性 (local media slant) 的经典发现: 出版机构与被报道对象所在地理位置越接近, 媒体在报道口吻上越可能表现出系统性偏离(通常偏正面, 因广告/社区利益/读者关系等在地激励), 从而形成"本地-非本地"报道口吻缺口。news_process 项目将该逻辑落到银行-年面板层面, 先以银行注册地(总部所在城市, 由 `config/bank_list.yaml` 等实体字典锚定)与新闻来源媒体的注册/发行城市做字符串/字典匹配, 划出"本市媒体"子样本, 再在该子样本内计算负面报道占比, 得到 `neg_frac_homecity_{trk}` 三列。与之并排的姊妹列 `neg_frac_homeprov_{trk}`(省级口径)、`tone_homecity_media_{trk}`(本市媒体平均口吻, 非二值负面占比)、`tone_gap_homecity_noncity_{trk}`(本市-非本市口吻缺口)共同构成同一维度⑨的完整测度矩阵; 本家族只取"负面占比"这一离散化视角, 与连续口吻均值视角(tone_homecity_media)互补但不可互相替代——负面占比对极端负面报道更敏感, 均值口吻则更平滑, 二者共同报告可作规格稳健性交叉验证, 但不应混入同一回归方程作左右手变量(会引入机械共线)。

【方法学与计算】
分子判据"负面"并非直接取用 `llm_vote_tone_{trk}` 这一列(该列不存在于本家族计算路径中), 而是 `compute_media_heterogeneity()` 内先由三家 LLM 多数投票分值 `llm_vote_score_{track}` 派生出的二值指示列 `is_negative_{track}`(该分值落入负面档记 1, 否则记 0), 再对"本市媒体"子样本按 `target_bank`、`year` 分组取 `is_negative_{track}` 的均值, 即得到 `neg_frac_homecity_{trk}`。因此本家族的负面口径本质上是 stage 21 三家 LLM 多数投票情感分值的二值化派生量, 与项目主情感测度(P1 `llm_vote_tone_full`, 由 `llm_vote_score_full` 另行离散化而来)同源但非同一列, 二者共享上游情感分值却经由不同的派生路径产生不同用途的下游列, 不应混为一谈。分母是该银行-年落在"本市媒体"子样本内、且情感判定非缺失(即通过 stage 21 full-only 留篇门控, `llm_verified_full == True`)的报道篇数——这一点须特别强调: 2026-06-29 起, 项目将"是否算作一篇有效银行-金科报道"的门控收紧为仅看 full 轨判定(`llm_verified_full`), ctx/ss 两轨的负面占比测度因此是 conditional-on-full 的稳健性测度, 其行宇宙(分母集合)是 full 轨留篇集的子集, 而非各轨独立留篇。当某银行-年完全没有本市媒体报道时(homecity_media_frac 分母为零的退化情形), 该银行-年的 `neg_frac_homecity_{trk}` 取 NaN 而非 0, 以避免把"无本地媒体覆盖"误读为"零负面报道"这一实质不同的经济含义——这是地理邻近性维度⑨全体测度共享的缺失处理约定, 与 `neg_frac_homeprov` 一致。城市匹配本身依赖实体字典的地址/注册地字段, 存在少量因媒体总部与实际采编地不一致、银行多级分支机构地址归并粒度等导致的测量误差, 这类误差方向不确定, 更可能造成经典衰减偏误(attenuation bias)而非系统性夸大。

【文献定位】
Gurun & Butler (2012, Journal of Finance) 是本地媒体倾向性研究的奠基文献, 其"不要相信炒作"标题本身即揭示本地媒体倾向于对本地企业更正面报道、进而影响广告收入与企业价值的机制链条; 但须澄清一个容易混淆之处——`compute_media_heterogeneity()` 源码内部对同一代码块下的三项并排指标分别标注了不同的文献支撑: 指标1(偏袒度 `tone_gap_*`)与指标2(封闭度 `*_media_frac`)的构念叙事对应 Gurun & Butler (2012) 的本地倾向性均值口径, 而指标3(即本家族的负面过滤 `neg_frac_*`)在源码行内注释处单独引用的是 Core, Guay & Larcker (2008, *Journal of Financial Economics*) 关于管理层如何通过媒体披露渠道选择性压制负面信息("the power of the pen")的机制——该文献强调的是负面消息尾部的选择性抑制而非口吻均值的系统性偏移, 与 neg_frac 这一离散化"负面占比"指标在构念上更贴合。Core, Guay & Larcker (2008) 的 DOI(10.1016/j.jfineco.2007.05.001)不在本项目引文白名单池内, 故本家族 citations 不直接收录该文献, 仅在此处如实披露源码注释的真实文献出处, 避免读者误以为 neg_frac_homecity 与 tone_gap/media_frac 三项指标共享同一篇奠基文献。就本家族实际收录的文献而言, Gurun & Butler (2012) 仍可作为"本地-非本地"报道口吻缺口这一更宽泛构念家族(维度⑨)的背景锚点, 但对 neg_frac 这一具体指标的解释力弱于对 tone_gap/media_frac 两项姊妹指标。Piotroski, Wong & Zhang (2015, Journal of Accounting Research) 在中国上市公司情境下研究了政治激励如何压制负面信息披露, 为本项目在中国银行业新闻语境下解读"本地负面占比偏低"提供了另一层制度性解释——除媒体商业动机外, 地方政府/监管关系也可能通过非正式渠道抑制本地负面报道, 两种机制在城市层面往往叠加、难以在观察性数据中完全分离, 这是使用本家族测度做因果解释时需要披露的局限。Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 关注情感分析中否定词处理对负面判定准确性的影响, 提醒本家族的负面标签本身继承自上游情感引擎(三家 LLM 投票派生的 `is_negative_{track}`), 其否定处理、程度副词、转折句式等语言学细节已在 stage 21/22 层面单独处理(词典消融梯度覆盖 negonly/degonly/advonly 等分支), 本家族不重复实现、仅承接结果, 但读者在解释"负面占比"数值时应知晓其继承自上游情感分类器的固有测量误差边界。 就"本市/非本市"子样本二分这一前置切分而言, Huang、Liu 与 Zhang (2024) 以本地报纸停刊作为本地媒体监督减弱的冲击, 检验公司非 GAAP 披露质量的变化, 其核心前提正是"总部同城的本地媒体与异地媒体在监督功能上不可替代", 为本家族划出"本市媒体"子样本、并以其负面占比与非本市口径对照提供了构念依据; 但该文的识别策略是停刊事件的 DiD, 本家族做的是横截面上的同城/异城子样本对比, 其语境为美国本地报纸与美国上市公司, DV 为披露质量而非媒体语调本身——该文只把本地媒体当作监督强度的处理变量, 并未度量本地媒体的报道语调, 故仅锚定"本地媒体独立构念"这一半, 不锚定本家族的负面判定算法; 该刊为快报型期刊, 篇幅所限其证据链亦相对简短。Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度, 并把它应用于银行融资条件这一银行层级的实证问题, 是"新闻语调→银行层级结果"链条的近期同域实践, 支撑本家族把银行-年媒体语调派生量当作可进入银行层级结果方程的变量; 迁移边界须如实标明: 该文语料为意大利媒体 (意/英文) 而非中国中文新闻, 其语调测度不经由本项目三家 LLM 投票的派生路径, 既无本市/非本市的媒体地理切分, 也不做负面篇占比的离散化, 亦无 full/ctx/ss 三轨文本切分, 其 DV 与本项目 P1 的 funding_cost 相近但口径与数据源不同, 因此它锚定的是应用域的同构性, 而非本家族公式中的任何一步。
## VAR: neg_frac_homecity_ctx

【变体差分】
本列是 `neg_frac_homecity` 家族的 ctx 轨变体, 分子分母均限定在实体窗口文本(标题+围绕目标银行实体的局部上下文窗口, 由 stage 14 `ctx_materializer` 物化的 `content_ctx` 字段)上计算的情感判定与留篇集合内。与 full 轨相比, ctx 轨的负面判定更聚焦于"紧邻银行实体的语境", 理论上能过滤掉同篇报道中与银行无关的负面段落(例如文章后半段讨论宏观经济下行但与该银行本身无直接负面关联), 从而降低负面误判率; 但代价是当银行相关句子稀疏或实体窗口截取不完整时, ctx 轨可能丢失部分真实语境, 产生系统性不同(未必更小)的负面占比估计。按 2026-06-29 起的 full-only 留篇门控, ctx 轨的行宇宙是 full 轨留篇集的子集(conditional-on-full), 即某银行-年若在 full 轨未通过留篇判定, 则该行在 ctx 轨也不参与计算, 但反向不必然成立——ctx 轨在同一留篇集合上重新计算城市匹配与负面占比, 不借用/回填 full 轨数值。本列与 `neg_frac_homecity_full`、`neg_frac_homecity_ss` 三者应作为并排的互为稳健性测度共同报告, 三轨各自 just-identified, 严禁在同一 over-identified Hansen J 型过度识别检验中把三轨系数混同为同一构念的多个工具, 这会人为夸大统计显著性并违反项目三轨口径铁律。

## VAR: neg_frac_homecity_full

【变体差分】
本列是家族的 full 轨变体, 也是三轨中的门控基准(canonical)轨: 分子分母均取自全文文本(标题+正文全文)上的情感判定, 且该轨的留篇判定(`llm_verified_full == True`)决定了整个 `neg_frac_homecity` 家族(含 ctx/ss 两个稳健性轨)的行宇宙——full 轨留篇集是三轨共享的分母上界。相较 ctx/ss 两轨, full 轨纳入了整篇报道的全部信息, 情感判定更接近人类读者对"这篇报道整体是否负面评价该银行"的直觉判断, 但也更容易受到文章中与银行本身弱相关的段落(如行业综述、监管政策背景介绍)拖拽情感极性, 引入与目标构念无关的噪音。作为 P1(`bank_fintech_tone`)等主线论文 headline 情感测度所在的轨道, full 轨在本地媒体倾向性维度⑨的应用中同样承担"主口径"角色: 若稳健性检验只能三选一报告, 应优先报告 full 轨结果, ctx/ss 轨作为附加稳健性表呈现, 但三者在方法论地位上互为稳健性、不存在统计意义上的主次之分, 仅是报告惯例上的默认展示顺序。使用者在解读本列时应留意: full 轨"本市媒体"子样本的城市匹配本身与情感判定轨道无关(城市匹配发生在媒体元数据层, 与三轨文本切分是两条独立处理链), 因此三轨之间的样本口径差异只体现在情感判定与留篇门控这一环, 而不体现在城市归属这一环; 这意味着三轨在同一银行-年上共享同一批"本市媒体"候选文章集合(留篇之前), 差异仅来自各轨各自的负面标签与 full-only 门控产生的行宇宙收缩, 理解这一点有助于避免把三轨数值差异误归因于城市匹配口径漂移。

## VAR: neg_frac_homecity_ss

【变体差分】
本列是家族的 ss(同句共现)轨变体, 分子分母限定在"银行实体与金科相关词汇在同一句子内共现(±N 句窗口, 默认半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认1)"的严格文本子集(标题+同句窗口, 由 stage 14 物化为 `content_ss`)上计算负面占比。ss 轨的回退语义严格镜像 ctx 轨: 当某银行-年报道中不存在银行∧金科同句共现时, 该篇文章的 `content_ss` 回退为全文 body(等同 full 轨文本), 并置 `ss_is_fallback=True`, 与 ctx 轨的回退行为在结构上完全对称、共享同一 `n_articles` 分母口径, 而非产生独立的孤儿分母。因此本列在金科/银行共现稀疏的样本区间(如银行金融科技报道占比很低的年份或银行)会出现较高比例的回退, 此时 ss 轨在数值上趋近于 full 轨而非提供额外的正交信息; 只有在共现丰富的子样本中, ss 轨才能真正体现"聚焦金科语境下的本地负面报道倾向"这一更窄的构念。与 ctx、full 两轨一样, ss 轨的留篇行宇宙也是 full 轨留篇集的子集(conditional-on-full), 三轨各自独立计算负面占比、互为稳健性并排报告, 禁止混入同一过度识别的 Hansen J 检验框架。ss 轨的价值在于为"本地媒体倾向性是否在金科相关报道上表现出不同强度"这一更细粒度的问题提供测度: 若地方媒体的正面偏向主要来自对本地传统银行业务的呵护, 而在金科合作/竞争议题上态度更中立甚至更负面(例如担忧金科对本地银行造成冲击), 则 ss 轨的负面占比应系统性高于 full 轨; 反之若地方媒体倾向性在金科议题上同样存在或更强, 则 ss 与 full 轨应趋同。由于回退机制的存在, 解读该差异时须先核查回退比例(可用 `ss_is_fallback` 均值间接推断), 回退比例过高的银行-年样本上 ss 轨与 full 轨的差异不具备"金科语境特异性"的解释力, 只是文本重合度高的机械结果。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Huang, W., Liu, J., & Zhang, R.-Z. (. (2024). Local newspaper closures and non-GAAP reporting quality. Finance Research Letters, 62, 105024. https://doi.org/10.1016/j.frl.2024.105024
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
