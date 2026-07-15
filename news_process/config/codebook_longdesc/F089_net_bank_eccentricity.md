---
family_id: F089
columns:
- bank_eccentricity
- bank_eccentricity_sent
- bank_eccentricity_win1
unit: 网络结构指标 (无量纲; 加权最短路距离的最大值, 单位 = 距离 = 1/共现次数)
formula: "bank_eccentricity(v) = max_{u in LCC} d(v, u); d = 倒数权重图 G_inv 上的加权最短路距离, 边距离 = 1/共现次数; 仅对当年最大连通分量 (LCC, 节点数 >= 2) 计算, 非 LCC 节点与 LCC 退化年置 NaN; 判据变体 {同篇 article 无后缀 / +-1 句 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (含 build_adjacency_matrix); 列标签 pipeline/panel/export.py
upstream:
- 24_herd_decay.parquet (both-verified 银行×文章展开帧; docid/target_bank/year/内容/标题 → 银行∧银行共现判据)
- 40_panel_yearly.parquet (bank-year 面板骨架, 中心度就地合并)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: "Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y."
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: "10.1016/j.iref.2025.104355"
  type: "journal"
  authors: "Fang, Y., Lin, H., & Lu, L."
  year: 2025
  title: "Measuring systemic risk from textual Analysis: Evidence from Chinese Banks"
  venue: "International Review of Economics & Finance"
- doi: "10.1108/cfri-06-2023-0155"
  type: "journal"
  authors: "Ma, W., Li, K., Pan, W.-F., & Wang, X."
  year: 2024
  title: "Measuring systemic risk in China: a textual analysis"
  venue: "China Finance Review International"
- doi: 10.1016/j.jeconom.2025.106130
  type: journal
  authors: "Hughes, D. W."
  year: 2026
  title: "A jackknife bias correction for nonlinear network data models with fixed effects"
  venue: Journal of Econometrics
  vol: 253
  pages_or_artno: 106130
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: "Nezami, M., Chisam, N., & Palmatier, R. W."
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.1093/rfs/hhae025
  type: journal
  authors: "Hirshleifer, D., Peng, L., & Wang, Q."
  year: 2025
  title: "News diffusion in social networks and stock market reactions"
  venue: The Review of Financial Studies
  vol: 38
  issue: 3
  pages_or_artno: 883-937
- doi: 10.1103/4pg6-mtmt
  type: journal
  authors: "Kirkley, A."
  year: 2025
  title: "Fast nonparametric inference of network backbones for weighted graph sparsification"
  venue: Physical Review X
  vol: 15
  issue: 3
  pages_or_artno: Article 031013
- doi: 10.1093/restud/rdae088
  type: journal
  authors: "de Paula, Á., Rasul, I., & Souza, P. C. L."
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: "Yu, M., Hu, X., & Zhong, A."
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: 103223
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: "Xu, Y., & Zhao, X."
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: 102163
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1017/S0022109021000788
  type: journal
  authors: "Gao, H., Ru, H., & Yang, X."
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: "Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A."
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: Article 76
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: "Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M."
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: "Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S."
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: "Jackson, M. O., & Pernoud, A."
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: 171-202
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: "Wang, Y., Zhang, Q., & Yang, X."
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: Article 2693
- doi: 10.1086/688176
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1016/j.socnet.2010.03.006
  type: journal
  authors: "Opsahl, T., Agneessens, F., & Skvoretz, J."
  year: 2010
  title: "Node centrality in weighted networks: Generalizing degree and shortest paths"
  venue: Social Networks
  vol: 32
  issue: 3
  pages_or_artno: 245-251
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: "Bramoullé, Y., Djebbari, H., & Fortin, B."
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: "Romano, J. P., & Wolf, M."
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: "Newman, M. E. J."
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: "Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A."
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: 3747-3752
- doi: 10.1103/PhysRevE.69.026113
  type: journal
  authors: "Newman, M. E. J., & Girvan, M."
  year: 2004
  title: "Finding and evaluating community structure in networks"
  venue: Physical Review E
  vol: 69
  issue: 2
  pages_or_artno: 026113
- doi: 10.1038/30918
  type: journal
  authors: "Watts, D. J., & Strogatz, S. H."
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
- doi: 10.2307/2298123
  type: journal
  authors: "Manski, C. F."
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1016/0378-8733(83)90028-X
  type: journal
  authors: "Seidman, S. B."
  year: 1983
  title: "Network structure and minimum degree"
  venue: Social Networks
  vol: 5
  issue: 3
  pages_or_artno: 269-287
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: "Freeman, L. C."
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: "Bonacich, P."
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: 113-120
- doi: "10.1080/1540496x.2025.2562336"
  title: "Analyst Network: Implications for Systemic Risk of Non-Financial Firms in China"
  authors: "Xiang, Y., & Borjigin, S."
  year: 2025
  venue: "Emerging Markets Finance and Trade"
  type: "journal"
- doi: "10.1007/s11424-025-4338-6"
  title: "The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes"
  authors: "Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X."
  year: 2025
  venue: "Journal of Systems Science and Complexity"
  type: "journal"
new_dois:
- "10.1016/j.iref.2025.104355"
- "10.1108/cfri-06-2023-0155"
- "10.1080/1540496x.2025.2562336"
- "10.1007/s11424-025-4338-6"
---

## CORE

基于711家中国银行的媒体报道共现网络构建负面新闻指数, 发现2013年后中小银行(而非大型银行)成为银行业系统性风险传染的主要驱动者, 与本条目所属的银行共现网络偏心率(核心-周边结构)测度构念高度相关。 利用中国26家主流报纸的文本信息构建系统性风险指数, 为以新闻文本共现推断的银行网络结构指标(如偏心率)提供了同期方法学参照。

【构念与来源】
bank_eccentricity 是"银行共现网络 (co-mention network)"上的偏心率 (eccentricity) 指标, 属图论中最基础的路径型结构量之一。给定一张银行两两相连的加权图, 某节点 v 的偏心率被定义为 v 到图中所有其他可达节点的最短路距离里的最大值, 即"从这家银行出发, 走到离它最远那家银行需要跨越的最短距离"。偏心率最小的节点构成图的中心 (center), 最大的构成图的周边 (periphery); 全图偏心率的最大值等于直径 (diameter), 最小值等于半径 (radius)。因此偏心率天然是一枚"边缘度 / 核心度"标尺: 数值越大, 银行在新闻话语的关系网络里越偏居一隅、越难以经由少量中介触达全局; 数值越小, 银行越处于四通八达的枢纽地带、与网络中任意成员都相距不远。这一构念可上溯到 Harary (1969) 的图论体系, 本项目在 export.py 的列标签中据此署名 Co-mention Eccentricity (Harary 1969)。

白话版: 把每家银行想象成一个点, 只要两家银行在同一篇新闻里被一起提到, 就在它们之间牵一条线, 一起被提到得越频繁线就越"粗 (权重越大)"。偏心率回答的问题是——"从这家银行沿着这些线走, 到网络里离它最远的那家银行, 最少要走多长的路"。如果这个"最远距离"很大, 说明该银行躲在关系网的角落里, 和主流圈子隔得远; 如果很小, 说明它站在人人都够得着的中央位置。它衡量的不是"认识多少家 (那是 degree)", 也不是"平均离大家多近 (那是 closeness)", 而是"最坏情形下离得有多远", 是一个关注"极端边缘性"的稳健视角。

数据来源与生产口径: 该指标由 pipeline/panel/network_spillover.py 的 compute_bank_network_centrality 在面板构建的步骤 7h-net (runner "同行网络传染/溢出效应"步骤) 产出, 是 33 个结构网络指标基名 (NETWORK_METRIC_BASES 单一事实源) 中 18 个节点级指标里 Part B 的一员。上游是 both-verified 的银行×文章展开帧 (24_herd_decay.parquet): 节点全集 = 该年通过留篇门控的银行集合, 门控采用 full-only 口径 (2026-06-29): 一篇是否算作"银行金科报道"只看 llm_verified_full 是否为真, ctx/ss 轨为 conditional-on-full 的测度轨, 不参与是否留篇的判定。边由 build_adjacency_matrix 按 docid 聚合生成: 同一篇文章中全部通过验证的 target_bank 集合内, 每一个无序对恰好加 1 (对称累加, 每篇每对同权), 从根上杜绝了旧口径下 twin 行 1x/2x 混合与 phantom 边入网的问题。边权即共现次数, 计入面板后与 bank-year 骨架按 (target_bank, year) 就地合并。

偏心率的取值区间与解释谱系值得展开。由于距离取共现次数的倒数, 两家银行同框越频繁其间距离越小, 一条被反复共同报道的银行关系会把两点在距离图上"拉近"; 反之, 仅偶尔同框的关系距离大。一家银行的偏心率因此综合了"它到全网各处的可达链条里最长那一段"的信息: 既受它自身连边稀疏度影响, 也受它所能触及的最远角落有多偏僻影响。这使偏心率成为一个"全局包络"量——它不因某家银行局部邻居众多而降低, 只要它通往网络另一端的最短路径中存在一段昂贵 (稀共现) 的跳转, 其偏心率就会被抬高。这一性质决定了它与纯局部量 (度、强度) 及"平均可达"量 (紧密中心度) 的信息互补, 也决定了它对断连结构高度敏感 (跨分量不可达即无定义), 从而必须限定在最大连通分量上度量。

【方法学与计算】
偏心率是路径型指标, 其"距离"语义与谱型 / 结构型指标截然不同, 因此计算走的是"倒数权重距离图"而非原始共现强度图。具体地: 先由邻接矩阵搭出原始图 G, 边权 = 共现次数 (强度语义); 再逐边取倒数搭出 G_inv, 边权 = 1/共现次数 (距离语义)——共现越频繁, 两家银行在距离图上就越"近"。这一"强度转距离"的加权最短路做法正是 Opsahl 等 (2010) 为加权网络推广度与最短路时确立的标准操作化, 也与 Barrat 等 (2004) 对复杂加权网络架构的刻画一脉相承。偏心率随后由 networkx 在 G_inv 的最大连通分量 (LCC) 上按加权最短路计算 (nx.eccentricity(G_inv_lcc, weight='weight'))。之所以限定 LCC, 是因为断连图上跨分量的最短路为无穷、偏心率无定义; 项目据此约定: 仅当 LCC 节点数不少于 2 时计算, 非 LCC 节点以及 LCC 退化 (不足 2 节点) 的年份一律置 NaN, 与同族电流中介 (CFB)、平均路径 (net_avg_path_yr) 及网络级直径 net_diameter_yr 的 LCC 约定保持一致。须精确区分: 同为倒数图路径型的 betweenness/harmonic/closeness 三枚是在全图 G_inv 上直接计算的, 并不限定 LCC——它们对跨分量不可达的处理是"该对贡献 0"(中介无路可过、调和距离倒数为 0) 或按可达集缩放 (closeness 的 Wasserman-Faust 修正), 数学上无须有限直径; 唯独偏心率取"最大距离", 一旦存在不可达对即为无穷, 才被迫收缩到 LCC 上定义。这也是为什么本列的缺失结构 (非 LCC 即 NaN) 与兄弟路径量的全覆盖 (断连年仍出 0 或缩放值) 系统性不同, 合并回归时二者的样本构成不可想当然视为同一。

判据敏感性是本族的第二重结构。同一套 33 指标会按"银行∧银行"共现的邻近判据整批算三遍: 同篇 (无后缀 canonical, criterion='article')、±win_radius 句窗 (_win1, criterion='win1')、严格同句 (_sent, criterion='sent'), 分别落无后缀 / _win1 / _sent 三套列 (runner 步骤连续三次调用 compute_bank_network_centrality, suffix 由 _expected_suffix 严格配套, 错配即 raise)。同篇判据沿用 docid 组内 both-verified 幸存银行两两加 1 的主路径; _win1/_sent 判据则改走 docid 组内文本重扫: 由 core/text/entity_context 的 map_bank_sentence_positions 定位每家银行在标题+正文中的句级位置 (标题 prepend 为第 0 句, match_in_title 恒真, 镜像 stage 13 口径), 再由 bank_pairs_within_sentence_window 按 win_radius 取对 (sent 判据取 radius=0, win1 判据取 config/panel.yaml::network_criteria.win_radius, 默认 1)。这两条重扫路径与生产共用同一套否定 AC 与短名排除事实源, 禁裸 AC, 以拦截"涉农行业→农行"一类假阳性。三判据的节点全集一致 (皆为当年幸存 target_bank), 仅边集越来越严: 同篇最宽、句窗居中、同句最严。

最大连通分量的选取与退化处理须逐条讲清。项目先对原始图 G 求全部连通分量, 取节点数最多者为 LCC (存在并列极大分量时取先遇者), 并在其上同时计算 CFB、偏心率与平均路径等路径型量, 保证这几枚指标共用同一子图基底。偏心率仅当 LCC 至少含 2 节点时以 nx.eccentricity 求值, 逐节点回填 metrics; 若当年图退化到 LCC 不足 2 节点, 或某银行根本不在 LCC 内, 则该银行本列取 NaN。这一"仅 LCC、否则 NaN"的策略与网络级直径 (net_diameter_yr, 亦以 G_lcc 上的最大偏心率给出, 但走无权 BFS) 的口径协同, 避免把不可达距离当作有限值污染回归。此外, article 主路径与 win1/sent 分轨路径共享同一 both-verified 幸存银行集合作为节点全集, 分轨路径在 docid 组内重扫时若遇多银行组的正文文本不一致 (F0.18 实测为 0), 会发出显式告警并取组首行 (fail-soft, 镜像 FINTECH_AC=None 优雅降级先例), 不让单条脏数据崩掉整个步骤。

需要特别澄清两组同形异义的后缀。其一, 判据后缀 (无后缀/_win1/_sent, 银行∧银行) 与三轨文本后缀 (_full/_ctx/_ss, 银行∧金科) 是两个正交的概念空间, 判据主体不同, 绝不可混用或相互复用。其二, network_criteria.win_radius 与 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的键, 前者服务本族银行∧银行判据, 后者服务 stage 13 银行∧金科硬过滤。此外, build_adjacency_matrix 保留了一个 hyperedge_normalize (Newman 1/(N-1) 超边归一) 预留参数, 但它尚未接线到 config/runner, 生产不可达; 且在 _win1/_sent 分轨路径上被显式守卫拦截 (True 即 raise), 以防三判据轨在未接线状态下无警告分叉口径。

【文献定位】
偏心率坐落在 Freeman (1978) 对中心度所做的概念澄清谱系中: Freeman 将中心度归纳为 degree、betweenness、closeness 三大家族, 偏心率与 closeness 同属"距离基"一脉, 但 closeness 关注到各点距离之和的倒数 (平均可达性), 偏心率关注到各点距离的最大值 (最坏可达性), 二者互补而非重复。加权化的处理沿用 Opsahl 等 (2010) 与 Barrat 等 (2004) 的加权网络框架; 偏心率的两个极值——半径与直径——正是 Watts 与 Strogatz (1998) 小世界研究里刻画网络"可达尺度"的核心量, 本族的 net_diameter_yr 即 LCC 内偏心率的最大值。同族其他指标各有其经典源头: current-flow betweenness 承 Newman (2005) 的随机游走视角, 社区结构与模块度承 Newman 与 Girvan (2004), k-核承 Seidman (1983), 特征向量中心度承 Bonacich (1972), Gould-Fernandez 经纪角色的加权归一承 Zádor 等 (2022)。这些兄弟指标与偏心率并排、各量不同侧面的"结构位置", 共同构成本项目的网络位置控制变量库。

把偏心率放进金融与银行语境, 有两条互相支撑的文献脉络。其一是"网络位置是否 (以及如何) 影响结果"的相关性证据: Nezami 等 (2025) 以元分析确认了中心度与企业绩效之间存在稳健但异质的关联, Yu 等 (2024) 与 Xu 与 Zhao (2024) 分别记录了金融网络中的节点中心度对信息扩散、资产定价与价格预测的作用; 这些工作为"为什么值得为每家银行测度一整套网络位置"提供了外部效度支点 (须留意元分析注记: 该证据支持中心度—绩效关联这一构念级命题, 并不逐一背书本族任一具体指标的操作化)。其二是"金融/银行网络的结构与系统性风险"这一制度脉络: Jackson 与 Pernoud (2021) 系统综述了金融网络中的系统性风险与核心—周边结构, Gao 等 (2022) 揭示了所有权网络在银行信贷中的信息角色, Wang 等 (2020) 刻画了中国担保网络在危机与刺激下的演化——偏心率所度量的"边缘 vs 核心"恰是这些研究关心的结构维度。就本项目的数据生成过程而言, 银行共现网络本质是从文本派生的关系网络, 与 Hoberg 与 Phillips (2016) 的文本相似度产业网络、Li 等 (2026) 从文本风险披露还原金融网络连通性的思路同源; 而以新闻共现为纽带的扩散与情绪传染, 又与 Hirshleifer 等 (2025) 的社交网络新闻扩散、Fang 等 (2024) 关于媒体情绪与中国银行系统性风险的证据直接呼应。

在信息与注意力经济的读法下, 偏心率还承载一层"话语可见度"含义。银行共现网络是媒体报道把哪些机构反复并置在同一叙事框架里的沉淀: 处于低偏心率核心的银行, 往往是被媒体持续放在行业整体叙事中一并讨论的"标杆"参照对象, 其名字在报道网络里与任何其他机构都相距不远; 处于高偏心率周边的银行, 则更多被单独或小圈子提及, 与主流叙事的距离更长。这一"报道可见度—网络位置"的对应关系, 与 Hirshleifer 等 (2025) 关于新闻在网络中扩散并引发市场反应的机制、以及 Fang 等 (2024) 关于媒体情绪经由银行关系传导至系统性风险的证据相互印证——偏心率因此不只是抽象的图论量, 更是"一家银行在新闻话语网络中处于中心还是边缘"的可操作代理。需要克制的是, 上述解读均为构念层面的定位, 具体到本样本的方向与量级须由回归结果 (占位, 由引擎注入统计段) 而非先验断言给出。

【识别策略定位】
在计量识别上, 偏心率及其兄弟指标进入回归的定位是"网络暴露的结构性控制 / 同行效应测度", 而非因果处理变量本身——本项目的处理变量是 full-only 门控下的情感/属性列 (如 llm_vote_tone_full, 一篇是否算作银行金科报道只看 llm_verified_full), 银行∧银行判据下的网络位置量与之处于两个正交概念空间, 只承担条件化 (conditioning) 职能。把这一定位放进 Manski (1993) 的三分法看得最清楚: Manski 将参照群体对个体的影响拆成内生效应 (个体结果随群体结果变动)、外生/语境效应 (个体结果随群体特征变动) 与相关效应 (共同冲击造成的伪相关) 三类, 并证明当参照群体结构完全传递时三者线性不可分, 即反射问题 (reflection problem)。偏心率是当年网络拓扑的一个预定 (predetermined) 结构特征, 落在"语境/外生"这一格, 用来吸收"银行身处网络核心还是边缘"的异质暴露, 而非充当被内生反射污染的群体结果本身。Bramoullé 等 (2009) 进一步证明, 一旦网络非完全传递——存在"朋友的朋友并非自己朋友"的结构落差——邻接矩阵的高阶幂 (W, W², W³) 线性无关, 可为内生同行效应提供识别工具; 网络位置量因此不是可有可无的协变量, 而是溢出识别链条里的自然构件。本项目的一阶/二阶溢出列 (W×tone、W²×tone) 与嵌入同行网络列正是这一思路的落地, 偏心率作为同一 W 拓扑的节点级摘要与它们并列进入方程右端, 刻画结构性同行压力沿网络的传导。

偏心率相对其它节点级量还有一层"慢变、抗局部扰动"的识别性质值得点明: 它取的是节点到全 LCC 各处最短路距离的最大值, 是一个全局包络量, 任何单家银行局部邻边的微小变动通常不会移动这个最大值 (除非恰好落在决定最长测地线的那条链上), 因此偏心率对来自单一银行当期结果的同时性反向因果相对钝感, 比度、强度这类纯局部量更接近"结构性、缓慢变化"的预定回归元。这一点让它更适合当控制而非处理, 但须克制: 相对预定不等于因果外生, 偏心率仍可能与不可观测的银行基本面、行业周期共同波动, 故本族一律以控制/稳健性口径而非处理效应口径解读, 数值方向与量级须由回归结果 (占位, 由引擎注入统计段) 给出。将结构网络量放进公司金融面板并非本项目独创: Grieser 等 (2022) 以网络效应刻画公司财务政策的相互影响, 为"以网络位置作为面板协变量"提供了金融领域的直接先例。还须诚实交代一个识别前提: 本族的银行网络并非行政观测到的产权或授信关系, 而是从新闻共现文本重构出来的关系网, 属"推断得到 (inferred)"而非"直接观测"的网络; de Paula 等 (2024) 关于从面板数据识别网络连边的研究提醒, 以代理数据反推的连边带有测量误差, 会削弱 (attenuate) 或扭曲下游网络系数, 这是把偏心率当结构控制时须一并披露的边界条件。此外, 对银行×年这类双向固定效应网络面板, Hughes (2026) 的刀切偏差校正提示非线性网络数据模型在固定效应下存在增量参数 (incidental parameter) 偏误, 是估计阶段须警惕的计量细节。

关于三判据变体的推断口径, 须严格复述项目铁律: 无后缀 (同篇)、_win1 (句窗)、_sent (同句) 三判据各自 just-identified、并排、互为稳健性、不分主次; 它们是规格稳健性梯子, 绝不可混进同一个 over-identified 的 Hansen J 检验 (镜像三轨文本、co-primary 双轨嵌入、政治词权重梯子、per-model 稳健轨的同一先例)。理由是三判据度量的是同一"边缘度"构念在越来越严"算共现"标准下的替代实现, 彼此高度相关, 叠成过度识别矩条只会人为制造相关矩条、扭曲 Hansen J 的分布与解读, 得出似是而非的过度识别拒绝。真正的跨规格族错误率控制应走 Romano 与 Wolf (2005) 式的 stepwise 多重检验 (rwolf) 的 FWER 框架, 在保持各判据 just-identified 的前提下对"是否有任一规格显著"施加族错误率约束, 而不是把稳健性梯子误当工具集塞进同一条估计方程。

【与相邻测度的构念区分】
偏心率极易与本族几枚"看似同类"的指标混淆, 须逐一切开。一个统一的看法先行: 把某节点到 LCC 内其余各点的加权最短路距离排成一个"距离向量", 偏心率、紧密中心度、调和中心度不过是对同一距离向量做了三种不同的聚合——偏心率取该向量的最大值 (相当于 L∞/上确界范数), 紧密中心度取距离之和的倒数 (相当于对 L1 求倒), 调和中心度取距离倒数之和 (对断点容忍)。三者同源于最短路距离, 却分别放大了分布的不同部位: 偏心率被最远的那一个尾点独家驱动, 紧密关注整体平均可达, 调和则对近点加权更重。因此与 closeness_cent (紧密中心度) 相比, 偏心率对单个远点极端敏感、对多数近邻不敏感, 二者可以给出方向相反的排序——一家银行可能平均离大家都很近 (高 closeness), 却因存在一个极偏的远点而偏心率偏高。与 harmonic_cent (调和中心度) 相比, 调和以距离倒数求和, 天然容忍断连 (不可达贡献 0)、无须限定 LCC, 覆盖率更稳; 偏心率因取最大距离必须限定 LCC (源码对 LCC 不足 2 节点或非 LCC 节点一律置 NaN), 覆盖率因此更依赖当年图的连通性。

偏心率与本族两个"核心—周边"味道的量也须切开, 以免望文生义。其一是 net_diameter_yr (网络级直径): 直径是 LCC 内所有节点偏心率的最大值, 与本节点量同属"半径—直径"谱系的两端, 但源码里直径走的是无权 BFS (对 G_lcc 求 eccentricity 不带 weight), 本列走的是 1/共现次数加权最短路 (在 G_inv_lcc 上以 weight 计), 二者作用在不同图对象上、加权口径不同, 因此本列列内最大值并不等同于 net_diameter_yr, 二者是构念平行而非数值嵌套的关系。其二是 bank_coreness (k-核数, Seidman 1983): 核数由反复剥离低度节点的 degeneracy 剥壳给出, 刻画"局部稠密的核心", 而偏心率刻画"到最远点的距离包络"; 一家银行完全可能身处高 k-核 (周围抱团稠密) 却仍有较高偏心率 (那一团核心整体离某个边缘挂件很远), 两种"核心"概念不可互换。与 betweenness/cfbetween_cent (中介/电流中介) 相比, 中介类量的是"多少最短路必须经过我"的桥梁控制地位, 关注中介而非距离远近, 一家边缘银行也可能因扼守唯一通道而中介值不低。与 degree/strength (度/强度) 相比, 度类只数局部邻居的多寡与总权重, 是纯局部量, 不必遍历全 LCC; 偏心率是需要遍历全 LCC 的全局量。与 eigen/katz/subgraph (特征向量/Katz/子图) 相比, 这些是"邻居本身重不重要"的递归声望量, 与"距最远点多远"正交。与 constraint/effective_size/ego_density/ci (Burt 结构洞族) 相比, 后者度量的是自我中心网 (ego-network) 内的经纪机会与冗余, 属局部结构洞视角, 同样与全局距离正交。简言之, 偏心率在本族独占"全局最坏可达距离 / 核心—周边"这一语义生态位。最后须记住一个构造前提: 银行共现网络是"文章×银行"二部图向银行单模的投影, Cimini 等 (2022) 对二部投影的元验证提示, 单模投影会因同时提及众多银行的大文章而系统性放大边密度; 偏心率作为距离量对这类密度伪影相对稳健 (距离由最短路而非局部密度主导), 但解释时仍应意识到投影这一构造前提。

【已知局限与稳健性梯子】
第一重局限是覆盖率对连通性的依赖: 由于限定 LCC 且要求 LCC 至少 2 节点, 在稀疏或高度断连的年份 (尤其本机 T=2 开发语料的退化情形), 大量银行会落在 LCC 之外而取 NaN, _sent 这类最严判据尤甚; 当某列在某年退化到零方差或近全缺, 它进回归后会被银行/年固定效应吸收或直接掉出可用样本, 其解释力实质悬置。生产 T=18 全量语料下图更稠密、LCC 更大, 覆盖显著改善, 因此本族指标的方差与解释力应以生产规模语料为准, 不宜以开发样本的退化表现外推。第二重是判据严苛度与信息量的权衡: 越严的判据 (sent) 边越少、图越碎、偏心率越可能缺失或呈零方差, 越宽的判据 (article) 则可能纳入"同篇但语义无关"的跨句偶然共现。三判据并排正是把这一权衡显性化为稳健性梯子, 而非事后择一; 但也须承认梯子只离散地探了三档严苛度, 档间连续的敏感性 (如任意句窗半径) 并未逐一物化。第三重是网络本身的测量误差: 银行共现网络并非行政观测到的产权、授信或担保关系, 而是媒体叙事把哪些银行反复并置的文本沉淀, 是一层"话语可见度"代理; 以代理反推的连边带测量误差, de Paula 等 (2024) 关于从面板识别网络连边的研究表明这类误差会削弱或扭曲下游网络系数, 且二部投影本身 (Cimini 等 (2022)) 会因大文章放大边密度——两者叠加意味着偏心率度量的是"新闻话语网络中的边缘性", 不可直接等同于"经济关系网络中的边缘性"。第四重是加权方案的任意性: 距离取 1/共现次数是 Opsahl 等 (2010) 框架下的标准但非唯一选择, 任何其它单调递减映射, 或先做加权图骨架提取 (backbone extraction) 再算距离, 都会给出不同的距离标度; Kirkley (2025) 的非参数骨架稀疏化即是一条尚未在本族物化的替代加权稳健性方向。第五重涉及确定性复现: 本族已知的 BLAS 浮点非确定列集中在 clustering/cfbetween/harmonic 三基名 (乘以三判据共 9 列), 偏心率属基于最短路的路径型量, 最短路搜索与取最大值均为确定性运算, 不在该 9 列之列, 在 PYTHONHASHSEED=0 且 BLAS 线程钉死为 1 的条件下可稳定复现 (golden 重生的一般纪律仍适用); 唯一残留的口径依赖是 LCC 选取在出现两个并列极大分量时取先遇者, 属实现约定而非随机源。综上, 偏心率的稳健性叙事由三判据梯子承载: 无后缀 / _win1 / _sent 各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 跨规格推断以 FWER (Romano 与 Wolf, 2005) 收口。以中国上市公司分析师网络为对象, 发现网络中心度更高的企业系统性风险更低, 为网络位置量与金融风险关联提供了2025年新证据 (Xiang & Borjigin, 2025, Emerging Markets Finance and Trade)。基于中国上市公司动态股票网络, 发现中心度更高的公司未来股价崩盘风险更低, 呼应偏心率一类核心—周边网络位置量的实证价值 (Huang et al., 2025, Journal of Systems Science and Complexity)。

## VAR: bank_eccentricity

【变体差分】
本列是家族 canonical (无后缀) 列, 对应共现判据 criterion='article'、落列后缀为空, 也是 core 层列与 NETWORK_METRIC_BASES 单一事实源中的一员; export.py 赋予的固定标签为 Co-mention Eccentricity (Harary 1969)。它区别于同族 _win1/_sent 变体的唯一维度是"银行∧银行"共现的邻近判据: 本列采用最宽的"同篇 (same-article)"判据——只要两家 both-verified 银行在同一篇新闻 (同一 docid) 中被共同提及, 就在它们之间累加一条边 (每篇每对加 1, 对称)。这条主路径不做句级重扫, 直接在 docid 组内对全部通过验证的 target_bank 集合两两加权, 因此边最稠密、LCC 最大、偏心率的非缺失覆盖在三判据中最高。

计算细节与家族口径一致但值得就本列点明: 邻接矩阵经"强度图 G → 倒数距离图 G_inv (边距 = 1/共现次数)"转换后, 偏心率在 G_inv 的最大连通分量 (LCC, 节点数不少于 2) 上以加权最短路取"到最远节点的最大距离", 非 LCC 节点及 LCC 退化年置 NaN。数值解释: 本列越大, 该银行在当年"同篇共现"关系网中越偏居周边、越难以经由少量中介触达全网; 越小, 越处枢纽核心。白话说, 就是"从这家银行沿着同篇共现的线走, 到网络里离它最远那家银行, 最短也要走这么远", 数值大即处在报道话语网的边角、数值小即身居人人够得着的中心。在回归中, 本列充当银行网络位置 (核心—周边) 的结构性控制或同行暴露测度, 与本项目一阶/二阶溢出及嵌入同行网络列互补 (Bramoullé 等 (2009)、Manski (1993) 的同行效应识别框架)。

作为三判据中最宽的一档, 本列在实证使用上有三点须点明。其一是覆盖率优势: 同篇判据的边最稠密、LCC 最大, 本列的非缺失比例在 bank_eccentricity/_win1/_sent 三兄弟中最高, 因此通常被选作偏心率构念的主报告列, 而 _win1/_sent 作为逐步收紧判据的稳健性对照。其二是与网络级直径的对应关系须精确交代: 本列取银行个体到最远点的加权最大距离 (在倒数距离图 G_inv 的 LCC 上以 weight 计), 而同族网络级列 net_diameter_yr 虽同属"半径—直径"谱系的上端, 却是在无权 G_lcc 上以 BFS 求得的最大偏心率, 加权口径与所作用的图对象均不同于本列; 因此二者是构念平行、粒度不同 (节点级 vs 网络级) 的关系, 本列列内最大值并不数值等同于 net_diameter_yr, 回归中亦不宜把二者同时作自变量以免语义重叠。其三是退化处理: 若当年 LCC 不足 2 节点, 或某银行根本不在 LCC 内, 本列取 NaN; 这一"仅 LCC、否则 NaN"策略避免把跨分量的不可达距离当作有限值污染估计。

须强调本列所属的稳健性口径与识别定位。本列是当年银行∧银行同篇共现拓扑的一个预定 (predetermined) 结构摘要, 在回归中承担的是"条件化异质网络暴露"的控制/同行效应测度职能, 而非因果处理变量本身 (处理变量是 full-only 门控下的情感/属性列); 它可与本项目一阶/二阶溢出 (W×tone、W²×tone) 及嵌入同行网络列并列进入右端, 呼应 Bramoullé 等 (2009) 与 Manski (1993) 的同行效应识别框架。由于取的是全 LCC 距离向量的最大值 (全局包络量), 本列对单家银行局部邻边的微小扰动相对钝感, 比度、强度这类纯局部量更接近缓变结构量, 但相对预定不等于因果外生, 仍以控制/稳健性口径解读。

须强调本列所属的稳健性口径: 无后缀 (本列, 同篇)、_win1 (句窗)、_sent (同句) 三判据各自 just-identified、并排、互为稳健性、不分主次, 严禁把它们叠进同一个 over-identified 的 Hansen J 检验; 跨判据的稳健性推断走 Romano 与 Wolf (2005) 式的 rwolf FWER, 而非过度识别矩条。另需与三轨文本后缀 (_full/_ctx/_ss, 银行∧金科口径) 严格区分: 本列的"无后缀"是判据维度的 canonical, 与文本轨道正交, 二者分处两个概念空间, 禁互相复用或混入同一 Hansen J。留篇门控采用 full-only 口径 (2026-06-29): 参与建网的节点全集由 llm_verified_full 判定的留篇集决定, ctx/ss 不改变是否留篇。本列与 closeness_cent/harmonic_cent/betweenness 等兄弟量的语义切分见 CORE 节【与相邻测度的构念区分】——偏心率独占"全局最坏可达距离"这一生态位, 不可与"平均可达"或"桥梁中介"相替代。偏心率属基于最短路的路径型确定性量, 不在本族已知 BLAS 浮点非确定的 clustering/cfbetween/harmonic 九列之列, 在固定随机种子与钉死 BLAS 线程条件下可稳定复现。

## VAR: bank_eccentricity_sent

【变体差分】
本列是 standard 层的"严格同句 (same-sentence)"判据变体, 对应 criterion='sent'、落列后缀 _sent。它与 canonical (bank_eccentricity, 同篇) 及 _win1 (句窗) 的唯一差分维度仍是"银行∧银行"共现的邻近判据, 且本列取三判据中最严的一档: 两家银行必须出现在同一句话内, 才在它们之间累加一条共现边。实现上, docid 组内由 map_bank_sentence_positions 定位每家银行在标题+正文 (标题 prepend 为第 0 句, match_in_title 恒真) 中的句级位置, 再由 bank_pairs_within_sentence_window 以 win_radius=0 (严格同句, 而非句窗) 取对; 与生产共用同一套否定 AC 与短名排除事实源, 禁裸 AC, 以拦截"涉农行业→农行"式假阳性。

因为同句判据剔除了所有跨句的偶然共现, 边集最稀、图最碎、LCC 最小, 本列的偏心率缺失 (NaN) 比例在三判据中最高, 在稀疏或本机 T=2 退化语料上尤易呈全 NaN 或零方差 (进回归被固定效应吸收), 生产 T=18 全量下方显信息量。其构念含义是"最保守的同框标准下的边缘度"——只有真正被写进同一句话的银行关系才被承认, 因此对"编辑把两家银行排在同一篇但语义无关"的噪声最不敏感。本列与 canonical、_win1 各自 just-identified、并排、互为稳健性、不分主次, 三判据严禁混进同一 over-identified 的 Hansen J, 跨判据推断以 Romano 与 Wolf (2005) 的 FWER 收口。须再次区分: _sent 是"银行∧银行"判据后缀, 与三轨文本后缀 _ss (银行∧金科同句) 分处两个正交概念空间, 名形近而口径不同, 禁互相复用。win_radius 键 (取 0 时即本列判据) 与 stage 13 的 cooccurrence_filter.sentence_radius 互不联动。

## VAR: bank_eccentricity_win1

【变体差分】
本列是 standard 层的"±1 句窗 (sentence-window)"判据变体, 对应 criterion='win1'、落列后缀 _win1, 严苛度居于 canonical (同篇) 与 _sent (同句) 之间。它与其余两列的唯一差分维度同样是"银行∧银行"共现的邻近判据: 两家银行只要出现在相邻正负 win_radius 句的范围内即算一条共现边。实现上, docid 组内经 map_bank_sentence_positions 定位银行句级位置后, 由 bank_pairs_within_sentence_window 以 win_radius = config/panel.yaml::network_criteria.win_radius (默认 1) 取对, 即"同句或相邻一句内共现"皆计边; 判据主体、否定 AC 与短名排除、match_in_title 恒真等口径与 _sent 完全一致, 仅句窗半径由 0 放宽到 1。

相较同篇判据, 句窗判据剔除了"同篇但相隔甚远"的松散共现, 又比严格同句宽容一句之遥的紧邻语境, 因此边密度、LCC 规模与偏心率覆盖率通常介于 article 与 sent 之间, 是三判据梯子的中间档。其构念含义是"以局部语境邻近为准的边缘度", 在保留语义相关性的同时不至于像同句判据那样过度稀疏。须复述稳健性口径: 无后缀、_win1 (本列)、_sent 三判据各自 just-identified、并排、互为稳健性、不分主次, 严禁叠进同一 over-identified 的 Hansen J; 跨判据的稳健性推断走 Romano 与 Wolf (2005) 式 rwolf FWER。两处易混须再次切开: 其一, _win1 是"银行∧银行"判据后缀, 与三轨文本后缀 (_full/_ctx/_ss, 银行∧金科) 正交, 分处两个概念空间; 其二, 本列所用的 network_criteria.win_radius 与 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的键, 服务不同判据主体, 数值巧合亦不联动。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Fang, Y., Lin, H., & Lu, L. (2025). Measuring systemic risk from textual Analysis: Evidence from Chinese Banks. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2025.104355
Ma, W., Li, K., Pan, W.-F., & Wang, X. (2024). Measuring systemic risk in China: a textual analysis. China Finance Review International. https://doi.org/10.1108/cfri-06-2023-0155
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
Kirkley, A. (2025). Fast nonparametric inference of network backbones for weighted graph sparsification. Physical Review X, 15(3), Article 031013. https://doi.org/10.1103/4pg6-mtmt
de Paula, Á., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), Article 76. https://doi.org/10.1038/s42005-022-00856-9
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, Article 2693. https://doi.org/10.1038/s41467-020-16535-8
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Xiang, Y., & Borjigin, S. (2025). Analyst Network: Implications for Systemic Risk of Non-Financial Firms in China. Emerging Markets Finance and Trade. https://doi.org/10.1080/1540496x.2025.2562336
Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X. (2025). The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes. Journal of Systems Science and Complexity. https://doi.org/10.1007/s11424-025-4338-6
<!-- rendered-citations:end -->
