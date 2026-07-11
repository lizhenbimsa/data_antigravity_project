---
family_id: F006
columns:
- app_frac
- app_frac_lc
- app_frac_ls
unit: 比率/占比 (proportion, 值域 [0,1], 无量纲; 分母为零或零新闻银行-年保持 NaN 不填 0)
formula: "app_frac{,_lc,_ls} = n_articles_app{,_lc_ctx,_ls_ss} / n_articles_llm_valid{,_ctx,_ss}; 分子 = 该轨 innovation_locus_{full,ctx,ss} == '应用场景' 的篇数, 分母 = 该轨 llm_vote_score_{full,ctx,ss} 非缺 (LLM 成功打分) 的篇数; 分母为 0 时置 NaN"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (bank-year 分组计数与比率构造); 文章级标签 producer = news_process/pipeline/sentiment/tone_llms.py::_resolve_locus_track + majority_vote_categorical (stage 21); Stata 导出方向编码 = news_process/pipeline/panel/stata_export.py::LOCUS_ENCODING
upstream:
- 21_tone_llms.parquet (innovation_locus_{full,ctx,ss} / llm_vote_score_{full,ctx,ss} / llm_verified_full)
- 14_news_with_ctx.parquet (content_full / content_ctx / content_ss 三轨物化文本 + *_is_fallback)
citations:
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2024.04608
  type: journal
  authors: He, Z., Jiang, S., Xu, D., & Yin, X.
  year: 2026
  title: "Investing in lending technology: IT spending in banking"
  venue: Management Science
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: "102306"
- doi: 10.1016/j.jfineco.2024.103957
  type: journal
  authors: Vives, X., & Ye, Z.
  year: 2025
  title: "Information technology and lender competition"
  venue: Journal of Financial Economics
  vol: 163
  pages_or_artno: "103957"
- doi: 10.1007/s10693-024-00442-w
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2025
  title: "The role of banks' business models in their FinTech acquisitions"
  venue: Journal of Financial Services Research
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: "FinTech credit and entrepreneurial growth"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3309-3359
- doi: 10.1086/727712
  type: journal
  authors: Lerner, J., Seru, A., Short, N., & Sun, Y.
  year: 2024
  title: "Financial innovation in the twenty-first century: Evidence from US patents"
  venue: Journal of Political Economy
  vol: 132
  issue: 5
  pages_or_artno: 1391-1449
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2618-2646
- doi: 10.1093/restud/rdad018
  type: journal
  authors: Rambachan, A., & Roth, J.
  year: 2023
  title: "A more credible approach to parallel trends"
  venue: The Review of Economic Studies
  vol: 90
  issue: 5
  pages_or_artno: 2555-2591
- doi: 10.52202/075280-3000
  type: journal
  authors: Egami, N., Hinck, M., Stewart, B. M., & Wei, H.
  year: 2023
  title: "Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models"
  venue: Advances in Neural Information Processing Systems
  vol: 36
  pages_or_artno: 68589-68601
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1146/annurev-financial-101521-112042
  type: journal
  authors: Berg, T., Fuster, A., & Puri, M.
  year: 2022
  title: "FinTech lending"
  venue: Annual Review of Financial Economics
  vol: 14
  pages_or_artno: 187-207
- doi: 10.1093/rfs/hhac022
  type: journal
  authors: Parlour, C. A., Rajan, U., & Zhu, H.
  year: 2022
  title: "When FinTech competes for payment flows"
  venue: The Review of Financial Studies
  vol: 35
  issue: 11
  pages_or_artno: 4985-5024
- doi: 10.1016/j.jmoneco.2022.04.001
  type: journal
  authors: Pierri, N., & Timmer, Y.
  year: 2022
  title: "The importance of technology in banking during a crisis"
  venue: Journal of Monetary Economics
  vol: 128
  pages_or_artno: 88-104
- doi: 10.1016/j.jfs.2020.100836
  type: journal
  authors: Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L.
  year: 2021
  title: "Fintech: What's old, what's new?"
  venue: Journal of Financial Stability
  vol: 53
  pages_or_artno: "100836"
- doi: 10.1016/j.jeconom.2020.09.006
  type: journal
  authors: Sun, L., & Abraham, S.
  year: 2021
  title: "Estimating dynamic treatment effects in event studies with heterogeneous treatment effects"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 175-199
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: The Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1146/annurev-financial-100719-120854
  type: journal
  authors: Vives, X.
  year: 2019
  title: "Digital disruption in banking"
  venue: Annual Review of Financial Economics
  vol: 11
  pages_or_artno: 243-272
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital Finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
- doi: 10.1002/jae.2508
  type: journal
  authors: MacKinnon, J. G., & Webb, M. D.
  year: 2017
  title: "Wild bootstrap inference for wildly different cluster sizes"
  venue: Journal of Applied Econometrics
  vol: 32
  issue: 2
  pages_or_artno: 233-254
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: Strategic Management Journal
  vol: 31
  issue: 3
  pages_or_artno: 306-333
- doi: 10.1287/isre.1100.0322
  type: journal
  authors: Yoo, Y., Henfridsson, O., & Lyytinen, K.
  year: 2010
  title: "The new organizing logic of digital innovation: An agenda for information systems research"
  venue: Information Systems Research
  vol: 21
  issue: 4
  pages_or_artno: 724-735
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1016/0895-4356(90)90158-l
  type: journal
  authors: Feinstein, A. R., & Cicchetti, D. V.
  year: 1990
  title: "High agreement but low Kappa: I. The problems of two paradoxes"
  venue: Journal of Clinical Epidemiology
  vol: 43
  issue: 6
  pages_or_artno: 543-549
new_dois: []
---

## CORE

【构念与来源】
app_frac 家族度量的构念是银行金融科技媒体叙事的创新位点 (innovation locus) 结构: 在一家银行给定年度全部被验证为银行金融科技报道、且大语言模型成功完成打分的新闻中, 创新位点被分类为"应用场景"的报道所占的比例。这里的"应用场景"指报道主题落在支付结算、消费信贷、财富管理、场景金融等直接面向业务功能的金融科技应用一侧; 与之对照的"底层技术"指报道主题落在区块链、人工智能、云计算、大数据基础设施等使能技术一侧。构念的直接理论出处是 Gomber, Koch & Siering (2017) 提出的数字金融立方体 (Digital Finance Cube) 框架, 该框架把数字金融研究对象沿数字金融业务功能、数字金融技术与技术概念、数字金融机构三个维度做正交切分, 其中"业务功能维"与"技术维"的区分构成本家族二元分类的骨架: 一条银行金科新闻要么在讲银行把某项使能技术引入自身技术栈 (技术维), 要么在讲银行把金融科技能力落到某个具体业务功能上 (业务功能维)。信息系统文献为这一区分提供了更一般的组织理论基础: Yoo, Henfridsson & Lyytinen (2010) 的分层模块化架构 (layered modular architecture) 指出数字创新天然分布在设备、网络、服务、内容等松耦合层上, 处于不同层的创新有不同的组织逻辑与价值捕获方式; Adner & Kapoor (2010) 则从创新生态系统角度论证, 上游组件技术与下游应用互补资产在生态位上的位置差异会系统性地改变技术代际更替中的企业绩效, 这正是"银行在技术层还是在应用层发力会带来差异化创新产出"这一研究假设的战略管理学根基。银行业实证文献进一步表明位点差异有真实的经济后果: Pierri & Timmer (2022) 发现危机前的银行技术采用强度显著影响危机期的贷款表现; Kwan, Lin, Pursiainen & Tai (2024) 用移动应用质量对银行数字能力做压力测试, 属于典型的应用场景侧测度; He, Jiang, Xu & Yin (2026) 把银行 IT 支出拆分为面向贷款技术的投资并考察其配置逻辑; Vives & Ye (2025) 在理论上刻画信息技术如何改变贷款人竞争格局。本家族与这些基于财务支出、应用评分或专利的技术强度测度互补: 它不度量银行"花了多少钱、拿了多少专利", 而是从媒体叙事中提取银行金融科技活动被公众话语感知到的位点结构。数据来源是本管道 stage 13 银行与金融科技词邻近共现硬过滤、stage 14 三轨文本物化之后的中文银行金融科技新闻语料 (生产口径约一千七百万条原始报道过滤后的留存集, 2007 至 2024 年, 110 家银行), 文章级创新位点标签在 stage 21 由三家大语言模型分类产生, 面板层在 stage 40 聚合为银行-年占比。

【方法学与计算】
计算链路分文章级与面板级两层。文章级: stage 21 以字节级冻结的 prompt v8、temperature 0.0、强制 JSON 响应格式, 向三家彼此独立的大语言模型 (gpt-5.4-nano 与 gemini-3.1-flash-lite 走 yunwu 网关, deepseek-v4-flash 直连官方端点) 请求对每篇文章逐轨输出 innovation_locus 标签 (取值限于"底层技术"与"应用场景") 及配套置信度; JSON 不可解析或缺失验证键的响应触发重试, 重试穷尽后按该模型缺席处理, 缺席模型不投票也不贡献置信度。三家标签经 majority_vote_categorical 多数决聚合, 平局策略为 conservative, 即两类得票相等时归入 tie_default 应用场景 — 这等价于均匀先验下把平局归入 modal class 的最大后验 (MAP) 决策; 情感三分类的生产调用点自 2026-06-23 起亦已把平局策略提升为保守"中性"(同款 conservative 最大后验决策, "平局即未定义"仅保留为函数默认值供单元测试与稳健性检验, verified 轨因此不再产出未定义计数), 两处生产口径同属研究者显式声明的保守平局决策。多数票之上还有一层关键词交叉验证: canonicalize_topic 关键词分类器基于各模型返回的 fintech_topic 证据独立给出 (类目, 置信度) 对, 若大语言模型多数票与关键词类目一致则最终置信度获得 0.2 的加成 (封顶 1.0), 若分歧则关键词置信度乘 0.5 作衰减; 当大语言模型三家全部空票时, 仅在关键词置信度严格大于零 (即存在真实关键词证据) 时才回退采用关键词类目, 零证据一律返回未定类 — 这一修复封堵了旧版把"零票且零证据"文章按分类器基率默认划入应用场景的系统性偏置。因此 locus 标签是一个混合 (HYBRID) 标签: 大语言模型多数票、关键词置信度调整与空票关键词回退三种机制共同参与, 这一点在效度评估中必须披露 (见局限节)。留篇门控遵循 full-only 口径 (2026-06-29 裁定): 一篇文章是否算作"银行金融科技报道"只看 llm_verified_full 是否为真, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 逐轨标签照算但不改变门控。面板级: encode.py 的 aggregate_panel 按银行-年分组, 先对该轨 locus 标签落在合法类目集 {底层技术, 应用场景} 内的文章逐类计数 (非预期标签值触发告警并不计入分类聚合), 得到分子 n_articles_app 族计数列; 分母取 n_articles_llm_valid 族, 即该轨 llm_vote_score 非缺 (大语言模型成功完成情感打分) 的篇数, 而非全部留篇数 n_articles。这一分母口径有两个刻意后果: 其一, 位点分类部分失败 (打分成功但 locus 标签为缺) 的文章仍留在分母中, 因此 tech_frac 与 app_frac 之和小于等于 1, 缺口恰为未定类占比, 属于保守口径 — 若把未定类从分母剔除, 小样本银行-年的占比会被机械抬高; 其二, 分母与媒体关注度用的 n_articles 分离, 使占比不受"报道多但模型打分失败率高"的银行-年污染。这一"和不超过一"的关系由 encode 层的分区恒等式校验以逻辑必然的弱不等式落实: 校验断言分母大于等于底层技术篇数与应用场景篇数之和, 差额恰为该维度分类失败 (标签缺失) 的文章累计数, 仅作信息级日志输出, 只有分母严格小于两类计数之和 (逻辑上不可能, 除非上游竞态) 才触发真告警。早期实现曾对 locus 与 substantiveness 维用严格相等校验, 在任一标签缺失时误报, 现三维度统一为弱不等式口径, 与 collab_mode 维一致。分母为零时该银行-年占比置 NaN; 面板平衡步骤对零新闻银行-年同样保持 NaN 而不填零, 因为把"当年无任何报道"编码为"应用场景占比为零"会混淆缺失与真实的零。导出层 stata_export 以 LOCUS_ENCODING 规定方向: 底层技术编码 0 为基线, 应用场景编码 1 为对照, 全仓与 substantiveness、collab_mode 两个姊妹维度保持同一"0 基线 1 对照"模式。作为由大语言模型标注生成的回归元, 本测度的计量地位受 generated regressor 文献约束: Ludwig, Mullainathan & Rambachan (2026) 系统刻画了大语言模型标注进入计量回归时的测量误差、提示词敏感性与可复现性要求; Egami, Hinck, Stewart & Wei (2023) 提出用少量人工金标对大语言模型代理标签做设计式监督学习校正下游推断; Carlson & Burbano (2026) 针对管理学研究给出大语言模型标注的基础指引与警告清单。本管道对这些要求的工程落实是: 提示词字节级冻结、温度归零、全部请求进 llm 缓存使离线零缺失时可零成本字节级复现, 以及双盲人工标注与机器标签的 Cohen kappa 与 Krippendorff alpha 准则效度评估 (生产 T=18 语料上待完成)。

【文献定位】
本家族嵌入银行金融科技实证文献中"技术层与应用层差异化后果"的脉络。综述层面, Boot, Hoffmann, Laeven & Ratnovski (2021) 把金融科技创新拆解为信息与通信两条技术脉络并追问"什么是旧的什么是新的", Vives (2019) 刻画数字颠覆对银行业竞争结构的冲击, 两者都强调不能把"银行做金融科技"当作同质处理 — 这正是本家族把叙事位点显式二元化的动机。应用场景一侧的代表性研究包括 Parlour, Rajan & Zhu (2022) 对金融科技竞争支付流的均衡分析、Berg, Fuster & Puri (2022) 对金融科技信贷的系统综述, 以及 Hau, Huang, Lin, Shan, Sheng & Wei (2024) 用中国场景证明金融科技信贷对创业成长的因果作用; 底层技术一侧, Chen, Wu & Yang (2019) 用专利文本把金融科技创新按底层技术类别 (区块链、物联网、机器人投顾等) 分组并发现价值含量高度异质, Lerner, Seru, Short & Sun (2024) 对二十一世纪金融专利的全景刻画同样显示技术类别间回报差异巨大。银行对外部金融科技的资本介入研究 (Alfhaili, Bakoush & Wolfe 2025 论银行业务模式与其金融科技收购的匹配, Alfhaili, Bakoush & Wolfe 2026 论金融科技股权投资与银行创新) 则提示位点结构可能与银行获取金融科技能力的组织通道相互作用。相对这些用专利、并购、支出等行政或财务数据构造的位点测度, 本家族的边际贡献是把媒体话语位点作为独立信息源: 媒体叙事捕捉的是银行金融科技活动的公众可见面与战略传播面, 与内部投入型测度既相关又不重合, 使"叙事位点"本身可以作为处理变量进入回归。

【识别策略定位】
app_frac 是论文 P4 (bank_fintech_locus) 的处理变量主列之一, 属于本仓 codebook 的 core 家族。P4 的处理对由面板真实列 tech_frac 与 app_frac 直接推导 (在 Stata 数据准备模板内构造, 不落 parquet): locus_layer_full 定义为 tech_frac 严格大于 app_frac 的示性 (底层技术主导), locus_scenario_full 定义为 app_frac 严格大于 tech_frac 的示性 (应用场景主导), 两者皆要求双列非缺; 次级处理 locus_gap 等于二者之差, 取值负一、零、正一, 平票 (含两占比皆零) 时两示性同为零、gap 为零作参照组。确证性推断只登记单一预设主假设: locus_layer_full 对引用加权专利产出的效应 (银行与年份双固定效应), 其余全部规格 — 包括 app_frac 自身系数、次级结果、异质性切分 — 均显式标注为探索性。事件研究基线为 2013 年余额宝事件乘 locus 分类的强度设计, 动态处理效应估计遵循 Sun & Abraham (2021) 对交错异质效应的稳健加权, 平行趋势的局部偏离敏感性以 Rambachan & Roth (2023) 的相对幅度限制 (M-band) 部分识别方法评估。工具变量策略针对叙事位点的反射性内生 (银行间位点选择互相参照, Manski 1993 的 reflection problem): 主工具为同银行类型乘年份内的留一 (leave-one-out) 同业 tech_frac 均值, 排他性论证沿 Leary & Roberts (2014) 的同业效应识别路线; 引擎另产滞后一期变体规避同期反射, 以及 ctx 与 ss 轨镜像工具 (lpeer 前缀紧凑命名)。仓内 IV 扩展引擎同时物化广义 Bartik 型工具族, 其识别条件的两条论证路线 — 份额外生 (Goldsmith-Pinkham, Sorkin & Swift 2020) 与冲击外生 (Borusyak, Hull & Jaravel 2022) — 在论文附录按测度族分别声明。多重假设控制: locus_layer_full 与 locus_scenario_full 构成双处理同族, 族内以 Romano & Wolf (2005) 的 step-down 重抽样程序控制族错误率; 银行或省级聚类数偏小及少处理簇事件研究场景下, 解析聚类标准误偏小, 改用 wild cluster bootstrap 推断 (MacKinnon & Webb 2017)。轨道与梯子口径铁律: full、ctx、ss 三轨 (app_frac、app_frac_lc、app_frac_ls) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨的矩条件混入同一 over-identified Hansen J 检验 — 三轨是同一构念在不同文本窗口上的替代测量, 高度相关的孪生测度合成过度识别检验只会制造虚假的排他性证据; 同理, 各工具变体 (full 滞后、ctx 同期、ctx 滞后、ss 同期、ss 滞后) 各配各的内生孪生列分别估计, 不做跨轨合成。作为由大语言模型标注生成的处理变量, 本家族的识别还须正面处理 generated regressor 的测量误差传导: Ludwig, Mullainathan & Rambachan (2026) 论证大语言模型代理标签进入回归会同时引入向零的衰减偏误与被系统性低估的解析标准误, 排他性与精度的论证因此不能止于点估计; 本仓的工程对策是把标签生成路径 (提示词 v8 字节冻结、温度归零、三家独立模型多数投票、关键词证据交叉验证、空票零证据不回退) 全程留痕, 使误差结构可审可复现, 并按 Egami, Hinck, Stewart & Wei (2023) 的设计式监督学习 (design-based supervised learning) 思路预留少量人工金标对下游系数做偏误校正的接口, 与 Carlson & Burbano (2026) 给管理学研究开列的大语言模型标注警告清单逐条对照 (人工金标校正在生产 T=18 语料上待执行)。位点维在处理构造中的位置也须与另两个二元维度做正交隔离: locus 与 substantiveness、collab_mode 在同一批文章上交叉出 cell_id 一至八, 其编码式为 cell_id 等于 substantiveness 位乘四加 locus 位乘二再加 collab 位加一, cell 1 是三维全基线的实质性·底层技术·自主研发、cell 8 是三维全对照的象征性·应用场景·外部协同, 八个单元以纯 ASCII 值标签落盘以保 Stata 兼容; P4 确证主回归只登记 locus 对为处理, 把 substantiveness 与 collab_mode 维留作协变量与探索性替代规格, 严防三维联合塞进同一处理向量造成维度混淆与自由度浪费。

【与相邻测度的构念区分】
与 tech_frac 的关系是同分母互补但不精确加总为一: 两列共享分母 n_articles_llm_valid, 分子分别取应用场景与底层技术篇数, 由于位点分类部分失败的文章留在分母, 两列之和与一的缺口即未定类占比, 因此 app_frac 不能用一减 tech_frac 机械恢复, 面板中两列并存且各自承重。与 sub_frac 与 symb_frac (P3 的 substantiveness 维, 实质性对象征性) 及 indep_frac 与 collab_frac (P5 的 collab_mode 维, 自主研发对外部协同) 的区分是维度正交: 三个二元维度在同一批文章上交叉出八个单元 (cell_id 一至八), locus 回答"讲的是技术层还是业务层", substantiveness 回答"是实质行动还是象征表态", collab_mode 回答"能力来自自建还是外部", 三者两两交叉但构念独立, P4 主回归只用 locus 对, collab_mode 仅作替代规格控制。与 attention_pct (P2 的媒体关注度) 的区分是量纲性质: 后者是曝光强度标量, 前者是类别构成占比, 一家银行可以关注度极高而位点结构均衡。与 llm_vote_tone 族 (P1 的连续情感) 的区分是属性对情感: locus 是报道内容的客观分类属性, 不携带正负方向。与 avg_locus_prob_score 族的区分是硬标签对软概率: 后者由文章级 compute_prob_score_binary 以应用场景为 positive_class 逐篇算出二分类概率 (标签命中应用场景时取置信度 c、否则取一减 c, 置信度恰为零时退化为 one-hot 即命中记一未命中记零), 再在验证篇上按银行-年取均值, 保留分类不确定性作连续信号; app_frac 则先把每篇折叠为多数决硬类再计占比。两者对同一构念给出离散与连续两种读数: 大量置信度贴近临界的边界文章会拉开硬占比与软均值, 因此二者差值本身可作标签稳定性的诊断量, 供交叉验证。与 tone_gap_tech_app 的区分是构成对条件差: 后者是底层技术类与应用场景类报道的类内情感差, 且施加两类各至少五篇的守门, 度量的是"两个位点被报道的语气差", 不是位点构成本身。与 avg_category_confidence 的区分是标签对元数据: 后者是混合分类器的置信度均值, 度量标签质量而非位点结构。

【已知局限与稳健性梯子】
局限一, 混合标签的关键词回路。locus 标签含 canonicalize_topic 关键词证据的置信度调整与空票回退, 其准则效度 kappa 因此继承了一份关键词循环性 — 若人工编码员也部分依赖同类表面关键词, 一致性会被机械抬高 — 这使 locus 维的效度数字与纯大语言模型标注的 substantiveness、collab 两维不可直接比较, 论文侧已按审稿裁定作强制披露。kappa 解读还须警惕 Feinstein & Cicchetti (1990) 的高一致低 kappa 悖论: 当类别边际分布高度偏斜时 (银行金科语料中应用场景类天然占多数), 观察一致率很高而 kappa 偏低不必然意味着标签质量差, 效度报告因此并行给出 Gwet AC1 与 Krippendorff alpha。局限二, 平局默认的基率偏置。有票平局归应用场景的 MAP 决策是显式研究者选择, 会给 app_frac 注入轻微的向上偏置; 缓解在于平局在三模型两类别设置下只发生于恰有两家有效投票且分歧的情形, 占比可从存档的 per-model 标签列审计, 且 per-model 梯子提供了完全不经平局决策的替代读数。局限三, 分母口径的错位风险。n_articles_llm_valid 以情感打分成功为准, 与位点标签成功率不完全重合, 极端情形下某银行-年打分全部成功而位点全部未定, 则 app_frac 为零而非缺失 — 解读接近零的占比时应对照未定类缺口。局限四, 开发环境退化。本机 T=2 开发面板上小样本银行-年的占比方差极大且事件研究模板优雅跳过, 一切分布陈述以生产 T=18 全量语料为准。局限五, 分轨分母的历史脆弱性 (已硬化但值得警醒)。三轨占比的分母必须逐轨对齐 (ctx 分子配 ctx 轨大语言模型成功打分数, ss 分子配 ss 轨), 早期实现曾错用 full 轨分母, 因各轨成功率不同而使 ctx 轨占比越界至三倍上限 (metric-audit 2026-06-02 修复); 现行代码在分轨分母列缺失时把该轨占比整列置 NaN 并发 loud warning、绝不静默回借 full 分母, 三维度的分区恒等式亦已从早期对 locus 与 substantiveness 的严格相等校验统一放宽为 collab 一致的弱不等式 (分母大于等于两类计数之和, 差额即分类失败累计, 仅信息级日志), 消除了任一标签缺失即触发的伪告警。这一硬化提示: 解读跨轨占比差值前应先确认三轨分母列齐备且各自非零, 分轨样本框不可互相借用。稳健性梯子共三条, 全部遵循"各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J、梯子间正交不交叉"的仓级铁律。梯子一, 三轨文本梯子: app_frac (full), app_frac_lc (ctx), app_frac_ls (ss), 同构念三窗口。梯子二, 跨厂商 per-model 梯子 (2026-07-03 分类维度扩展): LLM_CLASS_SPEC 把 locus 维映射到面板 metric 基名 tech_frac、分子目标类底层技术, 三家模型各产 gpt54nano、gemini31、deepseekv4 前缀的 per-model 占比列, 分母为该模型自身 verified 篇数, co-equal 互为稳健; 注意共识列不等于存档裸多数票, per-model 列也不等于裸存档聚合 — per-model 面板占比的分子与分母均经该模型自身 verified 门控 (门控指示列仅在该模型该轨 verified 为真的行上取零一值, 其余置缺, 分母即该模型自身 verified 篇数), 但不经共识轨独有的 final_v 清票与关键词回退清洗; 真正不门控的只是文章级 per-model 存档标签列 (审计保留模型原始输出); 真正的族错误率控制由根级 27_tableA12 Panel C 的跨模型 Romano-Wolf 模板承担, paper_spec 中的 cross_model_classifier 条目是声明式文档、运行时无消费者。梯子三, 替代分类器轨: 由 ctx 与 ss 轨占比推导的 locus_layer_ctx 与 locus_layer_ss 处理示性作探索性替代。三条梯子分别回答文本窗口敏感性、标注器厂商敏感性与处理构造敏感性, 互不交叉展开以避免列组合爆炸。

## VAR: app_frac

【变体差分】
本列是家族 canonical 列, full 轨, tier=core。差分要素逐项如下。轨道: 分类输入为 innovation_locus_full, 判读文本是 content_full, 即 prepend 标题后的完整正文 — 标题在 stage 14 物化时拼接为文本首句, 因此标题中的位点信号 (如标题即点明"区块链"或"手机银行") 直接参与大语言模型判读。分子: 该银行-年内 innovation_locus_full 等于应用场景的篇数 (n_articles_app, 合法类目集精确匹配, 非预期标签值告警且不计入)。分母: n_articles_llm_valid, 即 llm_vote_score_full 非缺篇数; 与 ctx、ss 两列不同, 本列的分母轨与全仓留篇门控轨重合 — full-only 门控 (2026-06-29) 规定一篇文章是否算银行金科报道只看 llm_verified_full, 因此本列是三列中唯一"门控轨即测度轨"的列, 其分母宇宙就是面板全部情感与分类测度的公共留篇集, 不存在跨轨分母借用问题。core 地位依据: 本列是 paper_spec bank_fintech_locus 的 treatment 主列, 处理对 locus_layer_full 与 locus_scenario_full 由 tech_frac 与 app_frac 的严格不等比较直接推导 (Stata 数据准备模板内构造, 不落 parquet): locus_layer_full 为 tech_frac 严格大于 app_frac 的示性 (底层技术主导), locus_scenario_full 为 app_frac 严格大于 tech_frac 的示性 (应用场景主导), 次级处理 locus_gap 为二占比之差、取负一/零/正一, 三者皆要求两列同时非缺。确证性主假设以 layer 侧为处理估计引用加权专利产出的银行与年份双固定效应, 但 app_frac 既是 scenario 侧示性的构造件、又是 gap 的减数, 与 tech_frac 同等承重 — 两示性与 gap 的定义都同时消费两列, 任一列缺失则整个处理对缺失, 因此本列的核心地位并非来自它单独作为处理系数, 而来自它与 tech_frac 联合决定 P4 全部处理构造; 2013 年余额宝冲击乘 locus 分类强度的事件研究基线中, 本列刻画应用场景侧的处理强度。方向语义: 导出层 LOCUS_ENCODING 规定应用场景编码 1 为对照、底层技术编码 0 为基线, app_frac 上升解读为该银行金科叙事向应用场景侧倾斜; 按 Gomber, Koch & Siering (2017) 框架, 这对应银行金融科技活动的公众叙事从使能技术层移向业务功能层。缺失语义: 分母为零 (当年无一篇大语言模型成功打分) 或零新闻银行-年一律 NaN, 面板平衡不回填零, 因为把"当年无报道"编码为"应用场景占比为零"会混淆缺失与真实的零。分区恒等式与非精确互补: 本列与 tech_frac 共享分母 n_articles_llm_valid, encode 层对二者施加弱不等式恒等式校验 (分母大于等于底层技术篇数加应用场景篇数), 差额即该银行-年 locus 标签缺失 (打分成功但位点未定) 的文章累计数, 属信息级日志而非告警, 只有分母严格小于两类之和才提示上游竞态; 因此把 app_frac 读作一减 tech_frac 会系统性高估, 未定类占比越大高估越严重, 面板中两列必须并存、在 codebook 中互为独立条目、各自承重。软硬两读: 本列是多数决硬标签占比, 与文章级软概率的银行-年均值 avg_locus_prob_score_full 是同一构念的离散与连续两种读数 — 后者对每篇文章保留应用场景侧的二分类后验概率 (positive_class 为应用场景) 再按银行-年取均值、保留分类不确定性, app_frac 则先在文章级折叠为硬类再计占比; 两者高度相关但不等价, 大量置信度接近临界的边界文章会拉开硬占比与软均值的差距, 供交叉验证标签稳定性。per-model 梯子在本维的面板基名落在 tech_frac 侧 (LLM_CLASS_SPEC 将 locus 维映射到 metric 基名 tech_frac、分子目标类底层技术), 本列没有同名 per-model 孪生列, 跨厂商稳健性读数经由 per-model tech_frac 与各模型自身 verified 篇数分母间接获得, 且 per-model 面板聚合经各模型自身 verified 门控 (分母即该模型 verified 篇数) 但不经共识轨独有的 final_v 清票与关键词回退清洗、与共识轨语义不同 (文章级 per-model 标签列才是不门控的审计存档); 该梯子与本列各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: app_frac_lc

【变体差分】
ctx 轨孪生列, 后缀 _lc 读作 locus-ctx, tier=standard。差分要素: 分类输入为 innovation_locus_ctx, 判读文本是 content_ctx, 即 prepend 标题加目标银行实体邻近窗口拼接的上下文文本 — 实体邻近判读的动机是剥离与目标银行无关的段落噪声, 让位点标签只反映文章中真正谈论该银行的部分, 属于实体邻近分类的谱系做法。分子为 n_articles_app_lc_ctx, 分母为 n_articles_llm_valid_ctx, 即 ctx 轨自身大语言模型成功打分的篇数。分母的轨道对称是本列的承重细节: 各轨大语言模型成功率不同, 历史实现曾错用 full 轨分母导致占比越界超过一 (metric-audit 2026-06-02 修复), 现行代码在 ctx 分母列缺失时将本列整列置 NaN 并发 loud warning, 绝不静默回借 full 分母。行宇宙口径: 本列是 conditional-on-full 测度轨 — 留篇门控只看 llm_verified_full, ctx 轨只在 full 留篇集的子集上改变判读文本与分母, 不独立扩张或收缩文章宇宙。与 canonical 列的关系遵循双轨互为稳健性铁律: 两列不以相关性分主次, 各自 just-identified 并排进各自的回归, 严禁把 full 与 ctx 的矩条件混入同一 over-identified Hansen J; 工具变量侧的镜像是 lpeer_locus_iv_ctx 及其滞后变体, ctx 内生孪生列配 ctx 同业工具, 不与 full 轨工具交叉。判读文本 content_ctx 在 stage 14 由 ctx_materializer 物化 (prepend 标题为首句, 不改原始内容列), 其实体窗口的判定采用不对称口径: 银行侧经否定与短名过滤定位目标银行提及, 金融科技侧用裸自动机匹配, 两侧近邻交集内的段落进入窗口。per-model 跨厂商稳健读数在本轨同样逐轨物化: LLM_CLASS_SPEC 把 locus 维映射到面板基名 tech_frac、分子目标类底层技术, 三家模型各产 ctx 轨前缀占比列、分母为各模型自身在 ctx 轨的 verified 篇数, 与本共识轨 co-equal 互为稳健、不分主次, 且 per-model 面板聚合经该模型自身 verified 门控 (分母即该模型 ctx 轨 verified 篇数) 但不经共识轨独有的 final_v 清票与关键词回退清洗、语义与共识轨不同, 严禁把 per-model 与共识轨的矩条件混进同一 over-identified Hansen J。解读注意: 实体窗口截断会削弱依赖全文语境的位点线索 (如文末才出现的技术细节), 因此 ctx 轨占比与 full 轨的系统性差值本身有信息量, 反映位点信号在文内相对目标银行提及位置的分布; 该差值只应在两轨分母列均齐备且非零的银行-年上解读, 分轨样本框不互借。

## VAR: app_frac_ls

【变体差分】
ss 轨列, 后缀 _ls 读作 locus-ss, tier=standard。差分要素: 分类输入为 innovation_locus_ss, 判读文本是 content_ss, 即 prepend 标题加"目标银行与金融科技词出现在同一句 (含正负一句半径窗)"的最严格共现文本, 三轨中窗口最窄、银行-金科绑定最强的一轨。分子为 n_articles_app_ls_ss, 分母为 n_articles_llm_valid_ss, 镜像 ctx 轨的分母对称口径 (ss 分子必须配 ss 分母, 防占比越界), 缺 ss 分母列时整列置 NaN 并 loud warning。回退语义是本列区别于 ctx 的关键 (镜像 ctx 的仓级口径): 当一篇留篇文章不存在银行与金科词的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 该篇仍共享 n_articles 分母; 金科词自动机不可用时全部文章按回退处理并优雅降级。回退的解读后果: 回退篇的 ss 判读文本与 full 轨高度趋同, 因此高回退率的银行-年上本列与 app_frac 会机械收敛, 两列差值在这类格点上不再反映窗口效应 — 解读本列相对 canonical 的偏离时应对照面板中的 ss 回退占比列。行宇宙口径与 ctx 相同: conditional-on-full, 门控只看 llm_verified_full, ss 只改测度不改留篇。轨道铁律同前: full、ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨合成同一 over-identified Hansen J, 也不做机械的 ctx 到 ss 后缀替换式过度识别; 工具变量镜像为 lpeer_locus_iv_ss 及其滞后变体, ss 内生孪生列配 ss 同业工具。同句窗半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制 (默认一句), 这与 stage 13 共现硬过滤所用的 cooccurrence_filter.sentence_radius 是两个不同的键、不可混淆: 前者决定 ss 轨判读文本的取词窗, 后者决定上游留篇过滤的松紧; 判据原语亦分家 —— ss 轨物化调用严格同句的 extract_bank_fintech_cooccurrence, 与 stage 13 的 has_bank_fintech_cooccurrence_within_radius 不同口径, 禁互相复用。per-model 跨厂商稳健读数在 ss 轨同样逐轨物化 (基名 tech_frac、分子底层技术、分母各模型 ss 轨自身 verified 篇数), 与共识轨 co-equal 互为稳健、不分主次, per-model 面板聚合经各模型自身 verified 门控但不经共识轨独有的 final_v 清票与关键词回退、语义有别于共识轨, 禁与共识轨或其他轨的矩条件混进同一 over-identified Hansen J。本列的构念定位是"当且仅当银行与金融科技在句法上直接绑定时, 叙事位点落在应用侧的强度", 是三轨中对共现语义要求最苛刻、也最不易被文章其他话题污染的读数; 但正因回退篇会退化为全文判读, 高回退率银行-年上本列的这一苛刻语义被稀释, 解读须始终对照 ss 回退占比。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
He, Z., Jiang, S., Xu, D., & Yin, X. (2026). Investing in lending technology: IT spending in banking. Management Science. https://doi.org/10.1287/mnsc.2024.04608
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2025). The role of banks' business models in their FinTech acquisitions. Journal of Financial Services Research. https://doi.org/10.1007/s10693-024-00442-w
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. Journal of Political Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. The Review of Economic Studies, 90(5), 2555-2591. https://doi.org/10.1093/restud/rdad018
Egami, N., Hinck, M., Stewart, B. M., & Wei, H. (2023). Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models. Advances in Neural Information Processing Systems, 36, 68589-68601. https://doi.org/10.52202/075280-3000
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Berg, T., Fuster, A., & Puri, M. (2022). FinTech lending. Annual Review of Financial Economics, 14, 187-207. https://doi.org/10.1146/annurev-financial-101521-112042
Parlour, C. A., Rajan, U., & Zhu, H. (2022). When FinTech competes for payment flows. The Review of Financial Studies, 35(11), 4985-5024. https://doi.org/10.1093/rfs/hhac022
Pierri, N., & Timmer, Y. (2022). The importance of technology in banking during a crisis. Journal of Monetary Economics, 128, 88-104. https://doi.org/10.1016/j.jmoneco.2022.04.001
Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L. (2021). Fintech: What's old, what's new?. Journal of Financial Stability, 53, 100836. https://doi.org/10.1016/j.jfs.2020.100836
Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics, 225(2), 175-199. https://doi.org/10.1016/j.jeconom.2020.09.006
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation?. The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Vives, X. (2019). Digital disruption in banking. Annual Review of Financial Economics, 11, 243-272. https://doi.org/10.1146/annurev-financial-100719-120854
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital Finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
MacKinnon, J. G., & Webb, M. D. (2017). Wild bootstrap inference for wildly different cluster sizes. Journal of Applied Econometrics, 32(2), 233-254. https://doi.org/10.1002/jae.2508
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Yoo, Y., Henfridsson, O., & Lyytinen, K. (2010). The new organizing logic of digital innovation: An agenda for information systems research. Information Systems Research, 21(4), 724-735. https://doi.org/10.1287/isre.1100.0322
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low Kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543-549. https://doi.org/10.1016/0895-4356(90)90158-l
<!-- rendered-citations:end -->
