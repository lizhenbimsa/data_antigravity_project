---
family_id: F454
columns:
- neg_sub_count_ctx
- neg_sub_count_full
- neg_sub_count_ss
unit: 篇数/计数 (count)
formula: 'neg_sub_count{track} = sum(_is_neg_sub{track}), 逐篇布尔指示列在该轨文本上求和; {track} ∈ {_full, _ctx, _ss}(_full 在部分下游用无后缀 track 表示); 分子来自 encode.py 第 K 段"洗稿率聚合"逐轨遍历中的方法 B(反向验证)'
producer: pipeline\panel\encode.py ; pipeline\panel\runner.py
upstream: []
citations:
- doi: '10.1016/j.jbankfin.2024.107191'
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: '10.1016/j.frl.2022.102776'
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: 'Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: '10.1111/1475-679X.12071'
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: '10.1016/j.dss.2016.05.009'
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: 'Negation scope detection in sentiment analysis: Decision support for news-driven trading'
  venue: Decision Support Systems
  vol: '88'
  pages_or_artno: 67-75
- doi: "10.1016/j.jaccpubpol.2024.107181"
  type: "journal"
  authors: "Cheng, C. A., Jiang, L., & Song, W.-L."
  year: 2024
  title: "Media coverage and debt financing choice"
  venue: "Journal of Accounting and Public Policy"
  vol: "44"
  pages_or_artno: "107181"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
new_dois: []
---

## CORE

【构念与来源】
`neg_sub_count` 家族刻画一篇银行金科报道中"实质性负面"表述的篇内累计数量, 是 encode.py 第 K 段"洗稿率聚合"(套话/洗稿率测度族)中方法 B(反向验证)的分子端计数列。所谓"实质性"(substantive, 缩写 sub)与"象征性"(symbolic, 缩写 symb)是本项目对企业文本语调的一对经典二分: 前者指落在具体、可核实的负面陈述(如具体不良资产处置、监管处罚、亏损数字)上的措辞, 后者指抽象、口号化、难以证伪的负面姿态性措辞(如泛泛的"风险犹存""形势严峻")。逐篇布尔指示列 `_is_neg_sub{track}` 由上游情感/文本处理管线在句子或短语层面标注, `neg_sub_count{track}` 只是 encode.py 里对该指示列按银行-年分组求和(`'sum'` 聚合), 得到该银行-年下"被标记为实质性负面"的篇数(count 单位, 非比率)。这一构念直接呼应企业可持续/环境信息披露文献中"言辞廉价"(cheap talk)与"樱桃采摘"(cherry-picking)问题的度量传统: Bingler et al. (2022, *Finance Research Letters*) 在 ClimateBERT 框架下正是用"具体承诺 vs. 空泛姿态"的区分来识别企业气候信息披露中的言过其实成分, 本家族把同一逻辑迁移到中国银行金科新闻报道的负面语调上。
【方法学与计算】
`neg_sub_count` 是分子(numerator)角色列, 其配对分母是同轨 `neg_count{track}`(该轨全部负面篇数)与 `neg_substvalid_count{track}`(该轨负面且判定有效的篇数, 经 `_svd_denom` 同域校正), 三者共同喂给 runner.py 里的"方法 B: 反向验证"公式, 产出比率型下游指标 `neg_sub_ratio{track} = neg_sub_count{track} / max(neg_substvalid_count{track}, neg_count{track})`(`_safe_ratio` + `_svd_denom` 双重护栏防零除/防分母小于分子的口径不一致), 以及非对称性诊断列 `washing_asymmetry{track} = neg_sub_ratio{track} - (1 - washing_ratio{track})`, 用以检验"正面洗稿"(washing_ratio, 方法 A, 正面象征性占比)与"负面实质性"是否呈系统性不对称——若企业倾向把正面消息说得空洞而把负面消息说得具体(或反之), 该差值会偏离零。`neg_sub_count` 本身作为纯计数列出现在面板(panel)中, 供研究者在使用 `neg_sub_ratio` 之外, 直接观察篇数层面的绝对暴露规模, 也便于对"小样本银行-年"做稀疏性诊断(计数过小时比率不稳定)。该列的构造发生在 encode.py 第 K 段"洗稿率聚合"逐 `track` 遍历循环内, 与方法 A(LLM 投票极化条件法, 产出 `pos_symb_count`)、方法 D(词典均值)、方法 E(BERT 均值)并列, 是"多方法测度洗稿/实质性程度"梯子的负面-反向验证支柱, fix(omni-g-runner-10, 2026-06-11) 之后分母统一改为 substvalid 同域计数, 确保跨方法可比。
【文献定位】
本家族方法学根基有三支: 一是 Bingler, Kraus, Leippold, & Webersinke (2024, *Journal of Banking & Finance*) 关于企业气候信息披露"言辞廉价"如何与实际气候行动、排放与声誉风险脱钩的实证发现, 与其 2022 年 ClimateBERT 一文共同构成"具体承诺 vs. 空泛姿态"这一实质性/象征性二分构念在金融文本领域的直接方法学源头, 是本家族区分"实质性负面"与"象征性负面"最贴近的构念锚点(而非仅一般性的情感强度测度); 二是 Piotroski, Wong, & Zhang (2015, *Journal of Accounting Research*, 该刊为会计学顶刊) 关于中国上市公司政治激励抑制负面信息的发现, 为"负面信息在中国语境下存在系统性压制/软化动机"提供了制度背景, 支撑本家族区分"实质性负面"与"象征性负面"的现实意义(若企业或媒体倾向用抽象姿态稀释具体负面事实, 单纯的负面词计数会低估真实风险暴露); 三是 Pröllochs, Feuerriegel, & Neumann (2016, *Decision Support Systems*) 关于新闻情感分析中否定范围检测的方法学, 为"实质性负面"判定中涉及的否定处理提供技术参照(negonly 消融臂即呼应此支)。三支文献共同框定了本家族"计数—反向验证—制度动机"三层含义: 计数是测度层(Bingler et al. 提供实质性/象征性二分的构念根基), 反向验证(与方法 A 对照)是方法论层, 制度背景(Piotroski et al.)是解释层, 否定检测(Pröllochs et al.)是技术层。 在测量形态层面, 本家族"逐篇布尔指示→按银行-年求和"的聚合范式与近期主流实证一致: Cheng、Jiang 与 Song (2024) 把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量与新闻情感进入债务融资方式选择回归, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率, 表明按主体-年对负面极性指示求和所得的计数确有经济含义。迁移边界: 该文极性来自 RavenPack 专有事件情感分析 (ESS), 而非公开词典或本项目的逐篇标注, 主体为美国上市公司而非银行, 故只锚定聚合形态, 不锚定判定原语, 更不涉及"实质性负面 vs 象征性负面"的篇内区分。Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 佐证把新闻情感按银行主体归集并进入银行层面实证在同域已被顶级期刊接受, 为本家族的银行-年负面计数提供外部效度参照; 但该文语境为美国银行监管 (DV 为监管评级/监管行动), 其情感测度既无实质性/象征性二分, 亦无 full/ctx/ss 三轨设计, 因而不能据以背书本家族分子端的实质性判定口径。
## VAR: neg_sub_count_ctx

【变体差分】
`neg_sub_count_ctx` 是三轨(full/ctx/ss)测度梯子中的 ctx(context, 实体窗口)轨: 母文本 `content_ctx` = 标题 + 银行实体周边窗口正文(由 stage 14 `ctx_materializer` 物化, `prepend_title` 前置标题), 而非全文。`_is_neg_sub_ctx` 指示列在该窗口文本上标注"实质性负面"表述, 求和后得到该银行-年在实体上下文窗口内的实质性负面篇数。三轨(full/ctx/ss)口径遵循项目铁律: 各自独立 just-identified 并排构造, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定——即不可把 `neg_sub_count_full`/`neg_sub_count_ctx`/`neg_sub_count_ss` 同时作为同一工具变量集合的过度识别工具, 三者分别在各自的稳健性回归中单独进入右端。留篇门控是否计入该银行-年样本, 采用 full-only 口径(2026-06-29 起): 一篇报道是否被判定为"一篇银行金科报道"只看 `llm_verified_full == True`, ctx 轨的计数是 full 留篇集合内的条件测度/稳健性轨, 行宇宙是 full 留篇集的子集, 而非独立样本框。相较 `neg_sub_count_full`, ctx 轨聚焦实体附近文本, 剔除了与目标银行不直接相关的段落, 因而更贴近"针对该银行本身的实质性负面陈述"这一构念, 但也可能因窗口截断而遗漏跨段落展开的具体负面论证, 是 full 轨的互补而非替代测度。在实证使用上, `neg_sub_count_ctx` 更适合用于检验"负面报道是否直接针对目标银行本身"这一构念(而非泛泛的行业背景负面情绪), 与 `neg_sub_count_full` 并列进入不同稳健性设定, 而非二者相加或相减, 以避免虚构一个混合窗口口径。

## VAR: neg_sub_count_full

【变体差分】
`neg_sub_count_full` 是三轨梯子中的 full(全文)轨, 也是该家族在下游多数文档与部分下游列命名中的无后缀("canonical" 意义上的默认)轨: 母文本 `content_full` = 标题 + 完整正文, `_is_neg_sub_full`(即 encode.py 循环中 `track='_full'` 时的 `_is_neg_sub{track}`)在全篇文本上标注实质性负面表述后求和。full 轨承担留篇门控的唯一判据角色(2026-06-29 起铁律): 一篇报道是否计入某银行-年样本, 完全由 `llm_verified_full` 决定, 与 ctx/ss 轨的判定结果无关; 因此 `neg_sub_count_full` 所依附的行宇宙即为该银行-年留篇集合本身, 而 ctx/ss 轨是这一集合之上的条件测度。full 轨捕捉的是全文范围内所有实质性负面陈述, 既包含直接谈及目标银行的段落, 也包含报道整体氛围/背景中的负面细节描述, 因而比 ctx 轨更"宽", 比 ss 轨(银行∧金科词同句共现)更不受"是否同时提及金科"这一额外条件约束。三轨互为稳健性、各自 just-identified、禁止混入同一 over-identified Hansen J 的铁律同样适用于本列, 不得将其与 ctx/ss 两轨的计数值相加合并为一个"总实质性负面计数", 因为三者建立在部分重叠但不等同的母文本之上。实证上 `neg_sub_count_full` 常被报告为主口径(primary), ctx/ss 作为条件于同一留篇集合的稳健性口径并排出现, 三者的系数方向与显著性一致性是判断结论对文本窗口选择是否稳健的关键证据。

## VAR: neg_sub_count_ss

【变体差分】
`neg_sub_count_ss` 是三轨梯子中的 ss(同句共现, sentence-cooccurrence)轨: 母文本 `content_ss` = 标题 + 银行实体与金科词在同一句(±N 窗口, 默认半径 1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`)共同出现的句子集合, 由 stage 14 物化。`_is_neg_sub_ss` 在该更严格的共现文本上标注实质性负面表述并求和, 因此该列只统计"银行与金科议题被同句直接关联提及、且该关联语境中带有实质性负面色彩"的篇数, 是三轨中口径最窄、构念最贴近"银行金科业务本身的具体负面风险"的一轨。回退语义镜像 ctx 轨: 当一篇报道中不存在银行∧金科同句共现时, `content_ss` 退化为全文 body(与 `content_full` 相同), 并置 `ss_is_fallback=True`(与 ctx 轨共享 `n_articles` 分母口径); 若上游 `FINTECH_AC` 词典未加载(`None`), 则 `*_is_fallback` 全部置 True, 测度优雅降级为 full 轨等价物而非报错清空。同样地, ss 轨的留篇资格由 full 轨门控决定, 三轨(full/ctx/ss)在识别策略上各自独立 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定。在应用上, `neg_sub_count_ss` 是三轨中最严格的口径, 适合用于检验"银行与金科业务被明确关联提及且伴随具体负面陈述"这一更强构念, 计数普遍小于 ctx/full 两轨(样本稀疏时应结合 `ss_is_fallback` 标志一并解读, 避免把回退样本误当作真实同句共现样本处理)。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
<!-- rendered-citations:end -->
