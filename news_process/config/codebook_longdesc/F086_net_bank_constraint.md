---
family_id: F086
columns:
- bank_constraint
- bank_constraint_sent
- bank_constraint_win1
unit: 网络结构约束指标 (无量纲)
formula: "bank_constraint = Σ_j (p_ij + Σ_q p_iq*p_qj)^2 (Burt 1992 network constraint); p_ij = 节点 i 投向邻居 j 的关系比例, 边权 = 年度银行∧银行共现文章数; degree<2 → NaN; 判据变体: 无后缀 (同篇) / _win1 (±1 句窗) / _sent (严格同句)"
producer: pipeline\panel\network_spillover.py::compute_bank_network_centrality (nx.constraint on raw-weight graph); 判据后缀归一 pipeline\panel\codebook.py
upstream:
- "24_herd_decay.parquet (stage-21 verified 宇宙, 篇章级 df_exploded: docid / target_bank / year / 内容 / 标题)"
- config/bank_names + config/bank_name_exclusions.json (win1/sent 判据的银行别名字典 + 否定 AC + 短名排除扫描上下文)
- config/panel.yaml::network_criteria.win_radius (win1 判据的句窗半径, 默认 1)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.3390/su16104190"
  type: "journal"
  authors: "Feng, H., Zhang, Z., Wang, Q., & Yang, L."
  year: 2024
  title: "Does a Company's Position within the Interlocking Director Network Influence Its ESG Performance?—Empirical Evidence from Chinese Listed Companies"
  venue: "Sustainability"
- doi: 10.1016/j.jeconom.2025.106130
  type: journal
  authors: Hughes, D. W.
  year: 2026
  title: "A jackknife bias correction for nonlinear network data models with fixed effects"
  venue: Journal of Econometrics
  vol: 253
  pages_or_artno: 106130
- doi: 10.1103/4pg6-mtmt
  type: journal
  authors: Kirkley, A.
  year: 2025
  title: "Fast nonparametric inference of network backbones for weighted graph sparsification"
  venue: Physical Review X
  vol: 15
  issue: 3
  pages_or_artno: "Article 031013"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: 103223
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: 102163
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould–Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: "Article 76"
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1016/j.socnet.2010.03.006
  type: journal
  authors: Opsahl, T., Agneessens, F., & Skvoretz, J.
  year: 2010
  title: "Node centrality in weighted networks: Generalizing degree and shortest paths"
  venue: Social Networks
  vol: 32
  issue: 3
  pages_or_artno: 245-251
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A.
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: 3747-3752
- doi: 10.1086/421787
  type: journal
  authors: Burt, R. S.
  year: 2004
  title: "Structural holes and good ideas"
  venue: American Journal of Sociology
  vol: 110
  issue: 2
  pages_or_artno: 349-399
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.2307/270949
  type: journal
  authors: Gould, R. V., & Fernandez, R. M.
  year: 1989
  title: "Structures of mediation: A formal approach to brokerage in transaction networks"
  venue: Sociological Methodology
  vol: 19
  pages_or_artno: 89-126
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: "10.1086/730630"
  type: journal
  authors: "Burt, R. S., & Opper, S."
  year: 2024
  title: "Guanxi and Structural Holes: Strong Bridges from Relational Embedding"
  venue: American Journal of Sociology
- doi: "10.1287/mnsc.2024.06313"
  type: journal
  authors: "Harris, J. H., Spyridopoulos, I., Zekhnini, M., & Brunetti, C."
  year: 2026
  title: "The Role of Networks in Loan Syndicate Markets"
  venue: Management Science
- doi: "10.1002/smj.3679"
  title: "Toward an improved causal test of network effects: Does alliance network position enhance firm innovation?"
  authors: "Hernandez, E., Lee, J. K., & Shaver, J. M."
  year: 2024
  venue: "Strategic Management Journal"
  type: "journal"
- doi: "10.1016/j.jbusres.2025.115452"
  title: "Structural holes and firm innovation in industrial clusters: A dual embeddedness perspective"
  authors: "You, S., Wang, L., Zhou, K. Z., & Jia, L."
  year: 2025
  venue: "Journal of Business Research"
  type: "journal"
new_dois:
- "10.3390/su16104190"
- "10.1086/730630"
- "10.1287/mnsc.2024.06313"
- "10.1002/smj.3679"
- "10.1016/j.jbusres.2025.115452"
---

## CORE

以中国上市公司为样本,研究公司在董事联结网络中的结构位置(涉及结构洞/网络约束相关直觉)如何影响其ESG表现,为银行等金融机构网络结构位置指标的经济后果提供了同类实证参照。

【构念与来源】
bank_constraint 家族度量的是一家银行在"年度新闻共现网络"中所承受的结构性约束 (network constraint), 它是 Burt (1992) 结构洞 (structural holes) 理论的核心节点级指标, 用来刻画某个节点的关系是否被少数彼此又互相连通的邻居所"锁定"。构念直觉可以这样把握: 若一家银行在新闻里频繁并列出现的那几个伙伴银行, 彼此之间也高度互联, 而这家银行又把它有限的关系投入几乎全部集中于这几个互联伙伴, 那么它就嵌在一个封闭、冗余的局部三角结构里 — 信息来回流转但少有新意, 约束高、可供套利的结构洞少; 反过来, 若它的伙伴彼此并不往来、它的关系投入又分散到互不相识的多个方向, 那么这家银行就跨越了结构洞、居于经纪 (brokerage) 位置, 约束低。用大白话说, constraint 回答的是"这家银行在新闻场里的人脉是不是全挤在一个小圈子里、圈里人还彼此都熟": 是, 就约束高、被圈住; 不是, 关系摊得开、圈子之间还得靠它牵线, 就约束低、有周旋余地。这一"约束高等于被封闭三角包裹、约束低等于跨越结构洞"的语义, 使 constraint 与同一 producer 内的 effective_size (有效规模) 与 bank_ci (定义上恰为 constraint 的倒数) 共同构成一组结构洞测度; 它们与纯拓扑的度中心度 (degree)、以最短路为基底的中介与接近中心度 (betweenness, closeness) 从彼此不同的维度刻画节点地位, 因而在信息量上互补而非重复。Freeman (1978) 对中心度概念的经典厘清指出, "中心"其实对应度、中介、接近三种彼此不可通约的直觉; 结构洞类指标则再引入第四种直觉 — 邻居之间是否互相认识, 即本家族所要捕捉的对象。约束值在数学上并非限定于零到一区间: 当一家银行只与少数几个彼此紧密互联的邻居相连时, 直接投入与间接投入叠加后平方求和可以超过一, 这一点在解释绝对水平时需留意, 也是它与取值天然落在零到一之间的聚类系数、密度类指标的又一区别。

数据来源是本项目的银行×金融科技新闻语料, 在篇章级去重、both-verified 过滤之后聚合而成的"银行∧银行"年度共现网络。每一篇通过验证的新闻文章, 其内部并列出现的目标银行两两配对, 在该年度邻接矩阵上贡献一条 (或加权的) 边; 边权等于两家银行在该年共同出现的文章数, 即共现计数。网络逐年独立构建, 是年度截面网络而非跨年累积, 因此 bank_constraint 是一个随每年新闻共现结构而变动的 bank-year 面板变量; 同一家银行在不同年份可以从高约束滑向低约束 (或反之), 这一时间维度的变化正是把它接入含银行与年度固定效应的面板回归的价值所在。以文本共现来构造网络这一做法, 与 Hoberg 与 Phillips (2016) 用招股说明书文本余弦相似度构造企业产品市场网络、Li 等 (2026) 从文本化风险披露中抽取金融网络结构与连通性的思路一脉相承 — 网络的"边"并非来自持股、董事联结或交易台账等台账型数据, 而是来自媒体文本中实体的同现模式, 是一种"信息共现"或"共同被关注"意义上的关系, 需在解释时与产权网络、借贷网络、担保网络等台账型关系严格区别对待。换言之, 本家族刻画的是"媒体注意力空间中的结构位置", 它反映一家银行是否常与同一小群同业被并置报道、抑或横跨互不相干的报道语境, 而非它与其他银行是否存在真实的资金或股权往来。这一来源属性既是它的独特信息价值 (捕捉了台账数据看不到的舆论共现结构), 也是其解释边界 (不能直接读作业务关联强度) 的根源。

【方法学与计算】
计算分三步。第一步是年度邻接矩阵构造 (build_adjacency_matrix): 对目标年份内每一个 docid (文章), 取其在 both-verified 过滤后幸存的 target_bank 集合, 对该集合内每一个无序银行对令对称邻接权各加一, 做到每篇文章每对恰计一次。这一"按 docid 聚合、每篇每对加一"的口径, 修正了旧实现按 co_mentioned_banks 串逐行双向计数所引入的两类偏差: 其一是同一篇文章的两个孪生行同时幸存时该对被计为二、仅一行幸存时被计为一的 1x/2x 混计; 其二是共现串里仍列出验证已拒绝银行所形成的 phantom 边。修正后, 边权严格等于"两端银行均通过验证"的共现文章数。第二步由邻接矩阵建立 networkx 无向加权图 G, 边权取原始共现计数。这里有一个关键的口径分岔: constraint 走的是原始权重图 G, 而非路径型指标 (中介、接近、离心率) 所用的倒数权重图 G_inv; 倒数图把"共现越多等于关系越近"翻译成"距离越短", 适合最短路语义, 但结构洞的关系投入比例在语义上应与关系强度正相关 — 共现越多、投入份额越大 — 故 constraint 必须用原始强度而不能用其倒数。加权网络下节点地位的度量口径可参照 Opsahl 等 (2010) 对度与最短路在加权情形的推广, 以及 Barrat 等 (2004) 对复杂加权网络结构的刻画。第三步调用 networkx 的 constraint 例程, 传入 weight 参数得到每家银行的 Burt 约束值。Burt 约束的定义为: 节点 i 的约束等于对其每一个邻居 j 累加 (p_ij 加上经由共同邻居 q 的间接投入 Σ_q p_iq 乘 p_qj) 的平方, 其中 p_ij 是 i 投向 j 的关系比例, 即 i 与 j 的边权占 i 全部边权之和的份额。邻居越集中、邻居之间越互联, 平方项越大, 约束越高。

关于边权口径还需补充两点, 它们决定了 constraint 数值的可信度。其一是 both-verified 过滤: 邻接矩阵只承认"两端银行在该 docid 下均通过验证"的共现, 修正前的旧实现按 co_mentioned_banks 分号串逐行双向计数, 既会因孪生行的幸存情况不同而把同一对计成一或二 (1x/2x 混计), 又会把验证已拒绝的银行 (phantom) 也连进网络, 二者都会系统性地扭曲 ego 网结构、进而污染 constraint。改按 docid 聚合、每篇每对恰加一之后, 边权成为干净的"共现文章数", ego 网拓扑才真实。其二是超边投影的规模效应: 一篇同时点名很多家银行的文章 (如行业榜单或批量监管通报) 会一次性贡献一个大团 (clique) 的全部两两边, 若不加约束, 少数大 N 文章即可凭组合数级的边数主导整张网络、抬高相关银行的邻居互联度从而系统性拉高其 constraint; producer 为此预留了 Newman 度守恒归一的开关 (每对贡献一除以 N 减一使单篇总度贡献守恒), 但该参数目前尚未接线到 config 与 runner, 生产路径仍走每对加一的 golden-safe 口径, 解释 constraint 时须记得大 N 文章对约束的潜在抬升尚未被中和。

缺失语义遵循 0-vs-NaN 约定。约束在邻居数不足时无定义: producer 对 degree 小于二的银行显式置 NaN (只有零个或一个邻居时结构洞概念退化, 无从谈"邻居之间是否互联"); 当 networkx 约束例程整体抛异常时, 该年全部银行的 constraint 置 NaN。这一"不可计算即 NaN"的约定, 与同 producer 内 Gould 与 Fernandez (1989) 式经纪角色 gf_* 的"真实零经纪记 0.0、分组缺失或不可计算记 NaN"约定保持一致 — 下游回归必须区分"结构上确实不受约束 (低值)"与"无法计算约束 (缺失)", 不可把 NaN 当作零处理, 也不可在描述统计里把 NaN 折算成任何数值填充。需要提醒的是, 本家族不属于本项目已知的 BLAS 浮点非确定网络列 (那三个是 clustering、cfbetween_cent、harmonic_cent 各自的无后缀、_win1、_sent 判据变体); constraint 的计算路径不含谱迭代、随机游走或最短路求解等对浮点求和顺序敏感的环节, 在钉死随机种子与全部 BLAS 线程数为一后逐位可复现, 因此在 golden 重生时不进入需按列名排除的非确定清单。

【文献定位】
在测量理论谱系上, 本家族上承 Freeman (1978) 的中心度概念厘清与 Burt (1992, 2004) 的结构洞纲领: Freeman (1978) 把"中心"拆解为度、中介、接近三种不可通约的直觉, 提醒任何单一中心度都只捕捉网络地位的一个侧面; Burt (1992) 则把视角从"节点有多中心"转向"节点周围有没有结构洞", 而 Burt (2004) 进一步论证跨越结构洞的经纪者更易获得非冗余信息与"好想法", 为"低约束等于信息与创新优势"提供了机理叙事 — constraint 正是这一纲领的量化闭式。加权网络下的度量口径, 本项目参照 Opsahl 等 (2010) 对度与最短路在加权情形的推广, 以及 Barrat 等 (2004) 对复杂加权网络架构 (强度分布、加权聚类) 的刻画, 二者共同支撑了"用共现计数而非零一边、并以强度比例定义关系投入"的做法。在把网络位置接入经济结果的实证脉络上, Nezami 等 (2025) 对网络中心度与企业绩效关系的元分析给出一个务实的定位: 网络位置确实系统性地关联绩效, 但不同中心度测度的预测力并不一致、异质性可观 — 这恰好从反面支持了本项目并排保留多种正交网络指标 (度、路径、结构洞) 而非单押一个"中心度"的做法, 也提示 constraint 的绩效含义须放在具体机制中审视而非一概而论。在金融网络语境中, Yu 等 (2024) 与 Xu 与 Zhao (2024) 分别论证节点中心度经由信息扩散影响资产定价、以及金融网络中的节点中心度对资产价格预测的增量价值; Gao 等 (2022) 则揭示银行所处的产权网络在贷款决策中的信息角色; Grieser 等 (2022) 记录了公司财务政策沿网络的外溢。这些工作共同说明: 银行在信息网络中的结构位置, 是一个既有理论支撑又有实证回报的构念, 而 constraint 从"结构封闭度、结构洞可利用性"这一独特侧面刻画了它, 与度、路径类指标共同拼出银行网络地位的完整画像。Burt 与 Opper (2024, American Journal of Sociology) 以中国关系 (guanxi) 情境重新检验结构洞理论, 论证强关系亦可充当跨越结构洞的桥梁, 为本家族 constraint 所依托的 Burt 结构洞纲领提供了最新的理论延伸与边界条件; Harris 等 (2026, Management Science) 证明银行在贷款银团网络中的连接位置影响其组建银团的规模与费用收益, 为银行网络结构位置具有实证经济后果这一构念提供了最新的银行业场景证据。Hernandez, Lee 与 Shaver (2024, Strategic Management Journal) 提出区分自驱动与他驱动网络变化的研究设计以改进结构洞对企业创新因果效应的识别, 发现结构洞 (而非网络闭合) 仅在自驱动网络变化下促进创新, 为本家族 constraint 指标的因果解释边界提供最新方法论参照。You, Wang, Zhou 与 Jia (2025, Journal of Business Research) 以中国产业集群企业样本论证结构洞对企业创新的影响可为负向, 其效应受经纪企业的社会与政治嵌入性调节, 为 constraint (结构洞倒数意义上的约束) 与经济结果关系的机理提供了与 Burt 经典纲领相反方向的最新场景证据, 提示解释须视具体情境机制而非一概而论。

【识别策略定位】
本家族在因果识别链条中的定位需谨慎陈述, 且这一谨慎有其技术根源。须先厘清一点: constraint 在数学上是网络拓扑的确定性函数 — 给定年度邻接矩阵, 每家银行的约束值由其 ego 网内部的关系投入比例唯一决定, 不含任何行为方程或随机扰动。因此当它作为回归右手边解释某个银行结果 (如融资成本、金科投资、绩效) 时, 所面临的并非 Manski (1993) 反射问题 (reflection problem) 意义上最严格的"同时性不可分" — 反射问题针对的是"个体行为受其参照组当期平均行为影响"这一联立结构, 内生效应 (endogenous effect)、外生情境效应 (contextual effect) 与相关效应 (correlated effect) 在线性均值模型下无法分离; 而 constraint 作为一个预先构造的结构位置协变量, 更贴切的识别威胁是相关效应: 某些未被观测的因素 (银行业务战略、地域、被监管关注度) 可能同时驱动它在新闻共现网络中的结构位置与它的经济结果, 使 constraint 的系数吸收了这层混淆而非纯粹的"结构约束因果"。Bramoullé 等 (2009) 证明, 当网络含有非完全传递的三元结构 (即存在"我的朋友的朋友并非我的朋友"这类开放三角) 时, 二阶、三阶邻居的特征可作为工具, 内生与外生同伴效应因而可被分离识别; Bramoullé 等 (2020) 的综述进一步把这一"利用网络拓扑的不完全传递性实现识别"的条件系统化, 并厘清其对网络测量误差与选择性连边的敏感性; Boucher 等 (2024) 则把同伴效应从线性均值模型推广到更一般的社会互动理论框架, 说明识别结论对效用函数形式与互动机制设定的依赖, 提醒任何"网络位置到结果"的因果读法都须交代其背后的行为假设。

本项目对网络族变量的立场因此是审慎而克制的: constraint 及其判据变体主要作为刻画银行结构位置的描述性与稳健性协变量进入分析, 而非承担核心因果识别的处理变量。由于它是逐年构造的 bank-year 面板变量, 接入含银行与年度双向固定效应的设定后, 时不变的银行异质性 (规模、类型、总部所在地) 与全体银行共担的年度冲击 (宏观周期、行业性监管) 已被吸收, 剩余的识别威胁集中在"银行内部随时间变化的结构位置是否与同期未观测冲击相关"这一较窄的通道上。当分析涉及网络溢出的设定时, 外生变异不由 constraint 自身提供, 而依赖项目另行构造的三工具引擎 — 同组留一均值 (leave-one-out peer mean, 剔除自身以缓解机械相关)、广义 Bartik 移动份额 (generalized Bartik, 其识别逻辑与 Goldsmith-Pinkham 等 (2020) 对 Bartik 工具的份额-冲击分解一脉相承, 把外生性寄于份额或冲击的其中一侧)、以及媒体来源 house-style 暴露。这一分工使本家族避免了把"结构约束"直接当作外生处理的过强主张, 也与项目"网络位置是被解释的结构特征、外生变异另找来源"的一贯识别哲学相容。

识别层面还须补充两点与"网络本身如何得来"相关的注意事项, 它们是常规同伴效应文献之外、对本家族尤为切身的威胁。第一是网络测量误差 (mismeasured network): 本家族的邻接矩阵并非观测到的真实关系台账, 而是从新闻文本共现中构造的代理网络 — 边的有无与权重都携带媒体报道选择所致的测量噪声, 而 constraint 又是边权比例的非线性 (平方) 函数, 边层面的噪声经平方闭合结构放大后, 对约束值的扰动并不对称, 经典的"衰减偏误朝零"直觉未必适用, 系数方向与显著性都可能被非线性传播的测量误差扭曲。de Paula 等 (2024) 的工作从另一个方向照亮了这一问题: 他们证明在足够长的面板下, 网络连边本身可以从个体结果的协动中被识别与估计出来, 这既提示"文本共现网络"与"结果协动所隐含的真实互动网络"是两个原则上可分离、可互相校验的对象, 也提示未来可用结果面板反推的连边结构对本家族的共现边做外部效度检验, 而不是把文本共现当作互动结构的无误差观测。第二是非线性模型中的伴生参数偏误: 当 constraint 进入含个体固定效应的非线性设定 (如以银行固定效应刻画异质性的离散选择或计数模型) 时, Hughes (2026) 所刻画的固定效应网络数据模型伴生参数问题会以短面板偏误的形式出现, 其提出的 jackknife 偏误校正提示: 若未来以非线性方式消费本家族, 不能照搬线性双向固定效应"内生威胁已窄化"的结论, 须另行处理偏误。在当前项目的线性 reghdfe 主设定下这一威胁不 binding, 但作为口径记录在此, 防止下游误迁移。凡涉及本家族三判据变体进入回归的场合, 均须复述其规格稳健性并排的性质 (见下节稳健性梯子): 三判据各自 just-identified 并排、互为稳健性、不分主次, 不得把不同判据下的估计当作彼此独立的证据累加, 更不得把它们混进同一 over-identified 的 Hansen J 过度识别检验。

【与相邻测度的构念区分】
constraint 需与一整组语义相近但口径不同的测度严格区分, 逐一厘清如下。其一, 结构洞族内部 (effective_size 与 bank_ci): 三者共享"邻居冗余度"的直觉, 但操作化不同 — effective_size 度量去冗余后的有效邻居数 (邻居越互联、有效规模越小), bank_ci 在定义上恰为 constraint 的倒数 (constraint 为正时取其倒数, 否则 NaN, 故二者缺失模式与信息内容严格对偶), 而 constraint 独有"直接投入加经由共同邻居的间接投入之和, 再平方并对全部邻居累加"这一加权闭合结构, 对邻居集中度 (投入是否押在少数邻居) 与邻居互联度 (这些邻居彼此是否相识) 双重敏感, 不能被 effective_size 线性替代。三者提供族内的收敛效度交叉验证, 但不可互相代入同一回归充当独立证据。其二, 经纪角色族 (Gould 与 Fernandez (1989) 的 gf_* 五类角色): 经纪测度基于外生的节点分组 (如银行类型) 统计跨组中介的有向 2-path 类型 (协调者、守门人、代表、巡回经纪、联络人), 关注"谁在哪种群际位置上充当中介", 其加权与归一化的现代版本见 Zádor 等 (2022), 金融市场中机构经纪网络的构念与经济含义见 Han 等 (2024); 而 constraint 不需要任何外生分组, 纯由 ego 网内部拓扑决定。二者虽同源于结构洞/经纪的社会学纲领, 却是该纲领的两种不同操作化 — 一个数"跨组桥接的机会", 一个数"自身关系被封闭的程度" — 禁止混用为同一构念的替代测量。其三, 纯拓扑闭合度 (聚类系数 bank_clustering): 聚类只看 ego 的邻居之间实际连边占可能连边的比例, 是一个落在零到一的拓扑量, constraint 则在此之上叠加了 ego 对各邻居的关系投入权重与直接、间接投入的平方闭合结构, 因而二者虽正相关却非单调等价 — 两家聚类系数相同的银行, 若关系投入集中度不同 (一家把关系押在一个邻居、另一家均摊), constraint 可以显著不同; 也正因如此, constraint 能落到区间以外 (可大于一), 而聚类系数天然被界在零一之间。与聚类系数同属"局部闭合"直觉的还有 ego 网密度 (bank_ego_density), 它与 constraint 的差分更须点明: producer 中 ego 网密度是手工计算的无权量 — 只数 ego 的邻居两两之间是否存在边, 除以可能的邻居对数, 完全不看边权; 而 constraint 与带权聚类系数都以共现计数为权重。因此当共现强度分布高度偏斜时 (少数银行对共现数十次、多数只共现一两次), 无权的 ego 密度会把强弱边一视同仁地计入闭合度, constraint 则由强边主导 — 两者的分歧本身携带信息: 若某银行 ego 密度高而 constraint 不高, 说明其邻居间虽普遍有弱连接、但该行的关系投入并未押在互联的强边上。三个闭合类指标 (constraint、带权聚类、无权 ego 密度) 因此构成"是否加权、是否计入 ego 自身投入份额"两个维度上的完整对照格, 不可互相替代。其四, 规模与路径类中心度 (度/强度中心度、中介/接近中心度): 度中心度只数邻居个数、强度中心度只加总边权, 都不含"邻居之间是否互联"的闭合信息; 中介与接近中心度以最短路为基底, 且在本 producer 中走的是倒数权重图 G_inv (共现越多等于距离越短), 与 constraint 所用的原始权重 ego 图 G 是两张不同的图, 语义上前者刻画"跨越全网的桥梁/可达地位"、后者刻画"局部 ego 网的封闭度", 不可混为一谈。其五, 递归声望类 (特征向量/Katz/子图中心度): 这些指标回答"邻居本身是否重要", 是关于地位的递归定义, 与 constraint 的"邻居之间是否互联"正交。其六也是本项目最易误读的一点: 本家族的判据后缀 _win1 与 _sent 度量的是"银行∧银行"在文本中的邻近共现口径 (同篇/±1 句窗/严格同句), 与情感三轨的文本后缀 _full、_ctx、_ss (度量"银行∧金融科技"的文本范围) 是两个正交的概念空间; codebook 的三个推断函数入口正是先剥判据后缀再匹配, 以免 _sent 的 sent 子串被误归情感指标, 判据后缀因而绝不等同于三轨文本后缀, 严禁在解释或建模时相互套用。

【已知局限与稳健性梯子】
已知局限有四, 逐一如下。第一, 超边 (hyperedge) 规模效应: 由于共现网络由"一篇文章内并列银行两两成边"投影而来, 一篇同时点名很多家银行的文章 (行业榜单、批量监管通报) 会一次性贡献一个大团 (clique) 的全部两两边, 其边数随点名银行数按组合数级膨胀; 少数大 N 文章即可凭边数主导整张网络、抬高相关银行的邻居互联度, 从而系统性推高其 constraint。producer 为此预留了 Newman 度守恒归一开关 (每对贡献除以 N 减一, 使单篇的总度贡献守恒而非随 N 平方增长), 但该参数目前尚未接线到 config 与 runner, 判据分轨路径亦未实现该归一, 生产路径仍走每对加一的 golden-safe 口径 — 若未来接线须受控重生 golden, 解释当前 constraint 绝对水平时须记得大 N 文章对约束的潜在抬升尚未被中和 (同篇 canonical 轨受此影响最重, _win1 与 _sent 因边界更严而受大团投影干扰更小)。第二, 时序深度与跨年可比局限: 在早期试跑 T=2 的开发样本上, 严格判据 (尤其 _sent) 会使网络极度稀疏、大量银行 degree 小于二而落 NaN, constraint 在该样本上可能大面积缺失或退化, 这属预期行为, 须在生产 T=19 全量语料上评估; 又因网络逐年独立构建 (年度截面网络, 非跨年累积), 每年的语料密度不同会使网络整体稠密度随之起伏, constraint 的跨年绝对水平比较须谨慎, 更适合在控制年度固定效应后解读其银行内变化。第三, 文本共现不等于真实业务关系: constraint 捕捉的是"被媒体一同报道"意义上的结构约束, 属信息共现/共同被关注空间, 而非持股、董事联结、借贷或担保等台账型关系; 与之对照, Gao 等 (2022) 刻画的是真实产权网络在银行贷款中的信息角色, Grieser 等 (2022) 记录的是公司财务政策沿网络的外溢, Yu 等 (2024) 论证的是节点中心度经由信息扩散影响资产定价 — 本家族的经济含义须放在"媒体注意力共现"这一来源属性下审慎诠释, 不可直接读作业务关联强度。第四, 数据质量前提: constraint 数值的可信度系于 both-verified 边权口径 — 邻接矩阵只承认两端银行在同一 docid 下均通过验证的共现, 修正了旧实现按共现串逐行双向计数所引入的 1x/2x 混计与 phantom 边; 这一前提若在上游被破坏, ego 网拓扑即失真、constraint 随之污染。此外还有两条实现层细节应向下游披露。其一, 族内缺失门槛并不完全对齐: constraint 对 degree 小于二置 NaN, 而同族 effective_size 仅对 degree 等于零置 NaN — 恰有一个邻居的银行在 effective_size 上有值 (退化为一) 而在 constraint 上缺失, 因此结构洞族三列的缺失模式并非严格重合, 做族内收敛效度对照或 listwise 删失时须按各列自身的缺失掩码对齐样本框, 不可假定"一列缺则三列同缺"。其二, 异常兜底是年度粒度的: networkx 约束例程一旦整体抛异常, producer 把该年全部银行的 constraint 置 NaN (整年连坐), 这与逐银行 degree 门槛的 NaN 在语义上不同 — 前者是计算层故障、后者是概念上无定义, 但两者在落盘数据中不可区分, 只能回看该年日志辨别; 解释某一年整列缺失时应先排查计算层故障而非直接作结构解读。

从投影方法学看, 上述超边规模效应本质上是"二部网络投影"的一般性问题: 文章×银行的二部结构被压成银行×银行的一模网络时, 投影本身会制造系统性的虚假聚集与团结构。Cimini 等 (2022) 对二部投影方法的元验证系统比较了多种投影与统计验证方案, 说明未加验证的朴素投影会显著扭曲下游拓扑量 — 这为本家族"解释绝对水平须警惕大团投影"的提示提供了方法学定位, 也指出了未来可行的升级路径 (对投影边做统计显著性过滤后再算 constraint)。同一方向上, Kirkley (2025) 的加权图骨架化 (backbone) 非参推断提供了另一条候选稳健性检验: 先以骨架化剔除统计上可归入噪声的弱边、保留信息承载边, 再在骨架图上重算约束, 若结论不变则说明 constraint 的信号不依赖海量弱边的堆积。这两条 (投影验证、骨架化) 目前均未接线, 属记录在案的候选梯子而非现行产出, 引入任何一条都会改变列值、须受控重生 golden。

稳健性梯子方面, 本家族的核心设计即"网络构造判据敏感性"。同一 constraint 指标按银行∧银行共现判据分为三轨 — 同篇 (无后缀 canonical)、±1 句窗 (_win1)、严格同句 (_sent), 边集由宽到严, 对"边界定义"这一测量选择做系统性对照。三判据各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 过度识别检验; 它们属于规格稳健性并排 (镜像政治词权重梯度、词典消融梯度、co-primary 双轨嵌入的先例), 因而刻意不设跨判据的 FWER (族错误率) 模板 — 项目内跨模型 rwolf 的先例只覆盖对同一构念的 headline 替代测量, 而判据梯子是同一测量在不同边界定义下的规格稳健对照, 不属该 FWER 框架的适用范围。除判据梯子外, 结构洞族内的 effective_size 与 bank_ci 提供收敛效度的交叉验证 (三者应在同方向上一致移动), 度、强度、中介、接近等跨维度中心度则提供判别效度的对照 (若 constraint 与它们高度共线, 说明约束信息未超出规模/路径维度; 若相对独立, 则印证其承载了结构洞特有的信息)。此外, 原始权重 ego 图 G 与路径型指标所用的倒数权重图 G_inv 的口径分岔本身, 也是一层隐含的稳健性设计: constraint 坚持用原始强度定义关系投入比例, 与最短路语义刻意分开, 避免把"关系越强"错译成"距离越远"。

## VAR: bank_constraint

【变体差分】
本列是家族 canonical 列, 对应共现判据 criterion 取 article (同篇), 落列时后缀为空, 因此列名逐字节保持 bank_constraint 不变。其边界定义在三判据中最宽: 两家银行只要在同一篇通过验证的文章中并列出现 (无论在文本中相隔多远) 即形成一条边, 边权累计为二者当年共同出现的文章数。相对于两个更严的判据变体 (_win1 要求出现在 ±1 句窗内、_sent 要求出现在严格同一句内), 同篇判据产生的网络最稠密、连通度最高、degree 小于二而落 NaN 的银行最少, 因而在早期试跑样本上通常是三判据中覆盖率最高、可用观测最多的一轨。必须强调, "无后缀"并不意味着它在稳健性层级中是"主"而其余两轨是"从" — 无后缀只是历史沿用的现行 canonical 口径, 三判据在方法论上互为稳健性、平权并排, 谁也不比谁更"正确"; 它们各自 just-identified, 严禁把不同判据的 constraint 混进同一 over-identified Hansen J。计算上, 本列在原始共现计数权重图 G (而非倒数权重图) 上调用 Burt 约束例程, 对 degree 小于二的银行置 NaN, 例程整体异常时该年全部置 NaN; 这一 0-vs-NaN 约定与同 producer 的经纪角色一致, 下游须区分"结构上不受约束"与"无法计算"。它是同族 bank_ci 的构造母体 (bank_ci 在 constraint 为正时取其倒数, 否则 NaN), 因此本列在 degree 小于二处的 NaN 会沿链条传导为 bank_ci 的 NaN, 二者的缺失模式高度耦合, 在描述统计与回归样本框对齐时须一并考虑。本列亦是 NETWORK_METRIC_BASES 这一 33 基名 SSOT 中的一员, 其判据分轨、标签推断 (codebook 三推断函数入口先剥判据后缀再匹配)、以及 stata 导出标签均以该 SSOT 为单一事实源机械复用, 以防列名漂移。作为家族 canonical, 本列是解释"该银行新闻共现关系被少数互联伙伴锁定程度"的默认口径, 也是与 effective_size、聚类系数、度中心度做跨指标构念区分时的锚点列。从取值方向理解本列: 数值越高, 表示该银行的新闻共现伙伴越集中且越彼此互联, 它越被封闭三角包裹、越缺少结构洞; 数值越低, 表示其共现关系越分散、伙伴之间越互不相识, 它越处于经纪位置、越可能横跨互不相干的报道语境获取非冗余信息 (Burt 2004 意义上的信息优势)。本列也在超边规模效应上最为敏感: 因同篇判据允许一篇文章内任意两家银行成边, 榜单类大 N 文章一次投影出的整团边会显著抬高相关银行的邻居互联度、从而系统性推高其同篇 constraint, 这一点在解释本列绝对水平时应予警惕 (相较之下 _win1 与 _sent 因边界更严, 受大团投影的干扰更小)。作为最宽判据轨, 本列在数值上也最可能超过一 — 当一家银行只与少数彼此紧密互联的邻居相连时, 直接投入与经由共同邻居的间接投入叠加、平方再求和可越过一, 解释其绝对水平须留意这一非有界特性, 不可套用聚类系数、密度等零一区间量的直觉。在稳健性对照的分工上, 本列因覆盖率最高, 常被取为结构洞族收敛效度 (与 effective_size、bank_ci 是否同向一致移动) 与规模、路径类中心度判别效度 (与度、强度、中介、接近是否相对独立) 的默认锚点轨: 收敛度量应与本列同向、判别度量则应相对独立, 二者共同界定本列所承载的结构洞信息是否超出规模与路径维度而具备增量价值。最后须点明, 本列的空后缀属"银行∧银行同篇"判据空间, 与情感三轨里 full 轨的"银行∧金融科技全文"语义无任何对应关系, 二者是正交概念空间、不可类比套用。

## VAR: bank_constraint_sent

【变体差分】
本列是严格同句判据变体, 对应 criterion 取 sent、落列后缀 _sent, 在 producer 的判据分轨路径中以扫描半径 radius 等于零实现 (即 bank_pairs_within_sentence_window 的窗口宽度为零, 只认落在同一句子里的银行对)。它与 canonical 的唯一差别是成边的邻近判据: 两家银行必须出现在严格同一句子内才形成一条边, 因而这是三判据中最严的边界定义, 产生的网络最稀疏、边最少, degree 小于二而落 NaN 的银行也最多。判据分轨路径复用 core/text/entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 原语, 扫描文本采用 prepend_title 口径 (标题作为第 0 句拼接到正文之前, 镜像 stage 13 的 match_in_title), 且只对同 docid 组内幸存的 target_bank 别名建立位置图, 非幸存银行不入参、不可能成边, 与 phantom 边防线一致。在早期试跑 T=2 样本上, 严格同句判据常使多数银行 degree 小于二、constraint 大面积落 NaN 或退化, 属预期行为, 须在生产 T=19 全量语料上评估其信息量, 不应据该样本的稀疏退化否定该轨。就构念而言, _sent 捕捉的是"最紧的文本邻接下"银行的结构约束: 只有被写进同一句话的银行才算共现伙伴, 因而它对"真正被并置讨论"的信号最纯、对宽松同篇共现里可能混入的偶然并列最不敏感, 代价是覆盖率最低、噪声方差在稀疏年份可能偏大。铁律重述: _sent 与无后缀 (同篇)、_win1 (±1 句窗) 三判据各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三判据属规格稳健性并排 (镜像政治词权重、词典消融先例), 刻意不设跨判据 FWER 模板。且此处的 _sent 判据后缀刻画的是"银行∧银行严格同句", 与情感三轨里 _ss 后缀的"银行∧金融科技同句共现"是两个正交概念空间, 措辞上刻意与 _ss 的官方压缩词区分, 不可混淆套用。

## VAR: bank_constraint_win1

【变体差分】
本列是句窗判据变体, 对应 criterion 取 win1、落列后缀 _win1, 成边条件是两家银行出现在 ±win_radius 句窗之内; win_radius 取自 config/panel.yaml 的 network_criteria.win_radius, 默认为一, 即 ±1 句窗。其严格程度介于 canonical 的同篇判据 (全篇任意距离即可成边) 与 _sent 的严格同句判据 (窗口为零) 之间: 比同篇严 (要求文本邻近), 比严格同句宽 (允许相邻一句), 因而网络稠密度与 NaN 比例也居于两者之间, 提供了一个中间粒度的边界稳健性对照。计算路径与 _sent 共用同一套句级重扫原语 (map_bank_sentence_positions 加 bank_pairs_within_sentence_window), 仅窗口半径不同 (win1 用 win_radius, sent 用零); 扫描文本同样是 prepend_title 口径、只对同 docid 组内幸存银行建位置图。一个易错点须特别标注: 此处控制窗口宽度的 network_criteria.win_radius 键, 与 stage 13 共现硬过滤所用的 filtering.yaml 里 cooccurrence_filter.sentence_radius 键是两个互不联动的不同键 — 前者管"银行∧银行"网络成边判据, 后者管"银行∧金融科技"留篇过滤, 切勿因数值同为一而误认为同一参数。就构念定位而言, _win1 是同篇与严格同句之间的折中口径: 它比同篇更强调文本邻近 (只有相隔不超过一句的银行才成边, 剔除了全文两端遥相呼应的偶然并列), 又比严格同句宽容 (容许跨一句的邻接), 因而覆盖率与噪声都居中, 常被用作对"边界定义"这一测量选择的中间敏感性对照。铁律重述: _win1 与无后缀、_sent 三判据各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三判据属规格稳健性并排, 刻意不设跨判据 FWER 模板。判据后缀 (银行∧银行) 与情感三轨文本后缀 (银行∧金融科技) 是正交概念空间, 不可相互套用。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Feng, H., Zhang, Z., Wang, Q., & Yang, L. (2024). Does a Company's Position within the Interlocking Director Network Influence Its ESG Performance?—Empirical Evidence from Chinese Listed Companies. Sustainability. https://doi.org/10.3390/su16104190
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Kirkley, A. (2025). Fast nonparametric inference of network backbones for weighted graph sparsification. Physical Review X, 15(3), Article 031013. https://doi.org/10.1103/4pg6-mtmt
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould–Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), Article 76. https://doi.org/10.1038/s42005-022-00856-9
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Burt, R. S., & Opper, S. (2024). Guanxi and Structural Holes: Strong Bridges from Relational Embedding. American Journal of Sociology. https://doi.org/10.1086/730630
Harris, J. H., Spyridopoulos, I., Zekhnini, M., & Brunetti, C. (2026). The Role of Networks in Loan Syndicate Markets. Management Science. https://doi.org/10.1287/mnsc.2024.06313
Hernandez, E., Lee, J. K., & Shaver, J. M. (2024). Toward an improved causal test of network effects: Does alliance network position enhance firm innovation? Strategic Management Journal. https://doi.org/10.1002/smj.3679
You, S., Wang, L., Zhou, K. Z., & Jia, L. (2025). Structural holes and firm innovation in industrial clusters: A dual embeddedness perspective. Journal of Business Research. https://doi.org/10.1016/j.jbusres.2025.115452
<!-- rendered-citations:end -->
