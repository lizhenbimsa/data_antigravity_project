---
family_id: F459
columns:
- net_avg_path_yr
- net_avg_path_yr_sent
- net_avg_path_yr_win1
unit: 平均最短路径长度 (无量纲, 加权口径, 边距离=1/共现频次, 定义于最大连通分量 LCC)
formula: "net_avg_path_yr(t) = mean over all ordered node pairs (u,v) in LCC of d(u,v); d(u,v) = 加权最短路距离, 单边距离 = 1/共现频次 (Opsahl 2010 式加权路径, α=1 特例; 共现越强边距离越短); LCC = 年度银行∧银行共现网络的最大连通分量; 判据变体 {同篇(无后缀)/±1句窗(_win1)/严格同句(_sent)}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality ; news_process/pipeline/panel/export.py
upstream:
- 13_cooccurrence_filter.parquet
- 14_materialize_ctx.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.1016/j.socnet.2010.03.006
  type: journal
  authors: Opsahl, T., Agneessens, F., & Skvoretz, J.
  year: 2010
  title: "Node centrality in weighted networks: Generalizing degree and shortest paths"
  venue: Social Networks
  vol: 32
  issue: 3
  pages_or_artno: 245-251
- doi: "10.3390/e26050378"
  type: "journal"
  authors: "Gao, Q., Fan, H., & Yu, C."
  year: 2024
  title: "Systemic Importance and Risk Characteristics of Banks Based on a Multi-Layer Financial Network Analysis"
  venue: "Entropy"
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
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
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: 171-202
- doi: 10.1111/jofi.13010
  type: journal
  authors: Duarte, F., & Eisenbach, T. M.
  year: 2021
  title: "Fire-sale spillovers and systemic risk"
  venue: The Journal of Finance
  vol: 76
  issue: 3
  pages_or_artno: 1251-1294
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1111/1475-679x.12560"
  type: journal
  authors: "Xu, G."
  year: 2024
  title: "News Bias in Financial Journalists' Social Networks"
  venue: "Journal of Accounting Research"
- doi: "10.1111/acfi.13091"
  type: journal
  authors: "Wang, L., Hou, W., & Liu, Y."
  year: 2023
  title: "How do co-shareholding networks affect negative media coverage? Evidence from China"
  venue: "Accounting & Finance"
- doi: "10.1016/j.heliyon.2024.e26952"
  type: journal
  authors: "Fan, H., & Hu, C."
  year: 2024
  title: "Research on systemic risk of China's bank-asset bipartite network"
  venue: "Heliyon"
- doi: "10.1057/s41599-026-07085-3"
  type: journal
  authors: "Wei, W., Wang, Z., Wang, Y., & Song, Y."
  year: 2026
  title: "Transfer entropy, multidimensional multiple correlation network, and risk contagion of bank capital shortage"
  venue: "Humanities and Social Sciences Communications"
new_dois:
- "10.3390/e26050378"
- "10.1111/1475-679x.12560"
- "10.1111/acfi.13091"
- "10.1016/j.heliyon.2024.e26952"
- "10.1057/s41599-026-07085-3"
---

## CORE

该文构建中国银行间多层金融网络(含银行-银行、银行-资产等关系层)并用改进PageRank算法识别系统重要性银行及网络拓扑风险特征,为文本共现投影网络上度量银行间路径紧凑度提供同源的银行网络拓扑构造与系统性风险分析参照。

【构念与来源】
本家族刻画年度银行共现网络的全局形状指标之一: 平均最短路径长度 (average shortest path length, 又称特征路径长度 characteristic path length)。构念对象不是单家银行, 而是整张"某一年度里被媒体报道共同提及的银行两两邻近关系"所构成的图。网络的节点是当年出现在语料中的银行实体, 无向边则表示两家银行在同一批媒体报道中以满足既定判据的方式邻近共现 (银行∧银行共现, 与三轨文本口径的银行∧金科共现是两个不同概念, 见下文构念区分)。在这张年度图上, net_avg_path_yr 取所有可达节点对之间加权最短路距离的算术平均, 并把计算限定在最大连通分量 (largest connected component, LCC) 之内 — 因为一旦图不连通, 跨分量的路径长度为无穷, 直接对全图取均值会发散。此处的"距离"不是无权的边跳数, 而是共现频次的倒数: 两家银行被同一媒体叙事一同提及的次数越多, 其间边距离越短, 故本指标度量的是"沿共现强度看的有效拓扑距离" (即 Opsahl et al., 2010 加权最短路框架中以 1/w 为单边距离的 α=1 特例), 对共现强弱敏感。因此本指标度量的是"在当年被媒体一同提及而彼此关联的银行群体里, 任意两家银行在共现关系网上要经过几步才能相连"的典型距离。数值越小, 说明这张年度共现网越紧凑、信息在银行群体间传导的拓扑捷径越短; 数值越大, 则说明网络越松散、越像稀疏的链状或星状结构。该构念承袭 Watts & Strogatz (1998) 对"小世界"网络的刻画: 小世界的两大标志正是高聚类系数 (由同家族相邻的 net_avg_cluster_yr 度量) 与短的特征路径长度 (即本指标)。把这一经典拓扑量搬到"银行被同一媒体叙事捆绑提及"的语义共现网上, 目的是获得一个不依赖任何单家银行属性、纯粹刻画年度媒体关注结构的宏观形状变量。

数据来源链条为: 原始媒体报道经 stage 00 预处理与去重后, 由 stage 11/12 完成银行实体与金科词识别, stage 13 共现硬过滤给出"银行与金科邻近共现"的留篇集; 在此语料之上, 银行∧银行的两两共现由 core/text/entity_context 的判据原语 (map_bank_sentence_positions 与 bank_pairs_within_sentence_window) 逐年逐篇扫描而成邻接关系, 生产函数 network_spillover.py::compute_bank_network_centrality 用 networkx 逐年建图并计算 33 个结构指标 (SSOT = NETWORK_METRIC_BASES), net_avg_path_yr 是其中 10 个网络级 (Part C 与 WS-A) 指标之一, 最终经 export.py 落入 40_panel_yearly.parquet 的银行-年面板, 英文标签为 "Annual Avg Path Length (LCC)"。判据后缀 (无后缀 / _win1 / _sent) 由 _ADJ_CRITERIA 三元组驱动, win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1), 与 stage 13 filtering.yaml::cooccurrence_filter.sentence_radius 是互不联动的两个键。银行名判定复用与 stage 11/13 同一份否定与短名排除事实源 (禁裸 Aho-Corasick 匹配, 以防"涉农行业"误命中"农行"一类假阳性)。判据原语在生产管道与审计脚本之间共用同一份代码, 即"审计等于生产", 使家族的三个判据臂在离线复算时与在线落盘取值严格一致, 消除了口径漂移的隐患。整条链路里没有任何一步依赖单家银行的财务或市值数据: 平均路径长度纯由"谁和谁被同一篇媒体叙事捆绑提及"这一文本事实决定, 因而它是一个完全内生于媒体关注语料、独立于外部财务面板的结构变量, 财务哨兵列日后接入时不会改变本指标的取值。

之所以选择"平均最短路径长度"而非其他全局距离量作为家族核心, 有三重考量。首先, 平均路径长度是网络科学里最被广泛使用、语义最直观的连通紧凑度标量, 从 Watts & Strogatz (1998) 起就与聚类系数并列为刻画网络形状的两根支柱, 具备极强的跨文献可比性。其次, 相较于直径 (net_diameter_yr, 取最长的最短路, 对单个离群远点极端敏感), 平均路径长度对全体节点对取均值, 更稳健地反映"典型距离"而非"最坏距离"。第三, 它与同家族的度分布基尼 (net_degree_gini_yr, 刻画中心化程度)、模块度 (net_modularity_yr, 刻画社群划分)、巨分量占比 (net_giant_share_yr, 刻画连通规模) 构成互补而非冗余的宏观形状谱: 平均路径长度专司"连得多紧", 其余各司中心化、社群化、连通化, 合起来才刻画出年度共现网的完整轮廓。

【方法学与计算】
计算分三步。第一步建图: 对给定年度 t, 遍历当年每篇留篇报道, 依当前判据把同篇 (或同窗、同句) 内共现的银行两两配对, 累积共现次数为无向边权 weight (共现越频繁边权越大); 再由此派生一张距离图 G_inv, 其单边距离取共现次数的倒数 1/weight — 共现越强、两节点间边距离越短。第二步取最大连通分量: 由于媒体共现网通常并非全连通 (总有若干只被零星提及、彼此不相连的银行), 直接对全图求平均路径会因存在不可达对而未定义, 故遵循网络科学惯例把计算限制在 LCC 上, 报告的是"主体连通银行群"的内部典型距离。第三步聚合: 在 LCC 的距离图上对每一对可达节点求加权最短路距离 (即沿途各边 1/共现频次 之和最小的那条路径的距离), 再取全体有序对的算术平均, 得到当年的单一标量 net_avg_path_yr(t)。因此本指标是共现强度敏感的加权路径量, 而非仅数边跳数的无权路径。因为这是一个网络级 (network-level) 量, 它对当年所有银行取同一个值, 即在银行-年面板中沿银行维度是年内广播常数 (annual broadcast), 只沿年度维度变化。这一"年内不随银行变"的性质对下游计量识别至关重要 (见识别策略定位)。与之相对, 同家族里以银行为节点的 18 个节点级中心度指标 (如度中心性、介数、聚类系数) 才在银行维度上有截面变异。net_avg_path_yr 属于刻画"整张网长什么样"的宏观形状族, 与 Watts & Strogatz (1998) 的特征路径长度、Freeman (1978) 奠基的中心性谱系、以及 Newman (2005) 基于随机游走的路径类度量同属最短路/可达性这一测度传统。

【文献定位】
把银行放进由媒体共现构造的关系网并度量其拓扑形状, 其学理正当性来自三条互补的文献线。其一是金融网络与系统性风险文献: Jackson & Pernoud (2021) 系统综述了金融网络结构如何塑造传染与系统性风险, Duarte & Eisenbach (2021) 则量化了火线抛售溢出如何沿网络放大冲击 — 平均路径长度作为网络"紧凑度"的宏观刻画, 与这类传染半径、冲击传导速度的构念天然相关。其二是网络中心性与资产定价/绩效的实证文献: Yu et al. (2024) 与 Xu & Zhao (2024) 分别论证了金融网络中的节点中心度对信息扩散与资产价格预测的作用, Nezami et al. (2025) 对中心性—企业绩效关系做了元分析, 提示网络位置具有可度量的经济后果。其三是从文本构造金融网络的方法学文献: Li et al. (2026) 直接示范了如何从文本化风险披露中抽取金融网络结构与关联度, 与本项目"由媒体共现文本反演银行关系网"的路径同源, 为共现网这一测度对象提供了当代方法论背书。此外, Han et al. (2024) 对机构经纪网络的刻画为"网络中介与连通结构影响资源流动"的构念提供了金融情境锚点; Grieser et al. (2022) 关于公司财务政策沿网络传导的证据, 则说明网络连通结构本身即可承载可估计的经济后果。Xu (2024, Journal of Accounting Research) 以财经记者社交网络的连通结构解释报道偏向的溢出效应, 为本项目由媒体共提及构造银行关系网并度量其拓扑紧凑度提供了同源的媒体网络方法论参照; Wang, Hou, & Liu (2023, Accounting & Finance) 在中国情境下用共同持股网络的中心性与结构洞刻画企业间关联并检验其对负面媒体报道的影响, 呼应本指标以网络位置刻画媒体关注结构的测度取径。Fan & Hu (2024, Heliyon) 以中国银行数据构建银行-资产二模网络并用改进DebtRank算法度量系统性风险, 为文本共现网络投影下度量银行间紧凑度提供同源的银行网络构造与拓扑分析参照。Wei, Wang, Wang, & Song (2026, Humanities and Social Sciences Communications) 构建中国银行资本短缺的多层传导网络并报告其平均路径长度与紧凑度呈现小世界特征, 为本指标以平均最短路径刻画银行网络紧凑度的构念提供中国银行业情境下的实证参照。需要强调的是, 上述文献是构念与情境锚, 而非对本指标具体算法或对某一下游因果结论的背书 — 平均路径长度在本项目中是媒体关注结构的宏观形状描述量, 不预设任何银行层面的因果机制。

在方法学谱系上, 本指标与最短路/可达性这一测度传统一脉相承。Freeman (1978) 对中心性概念的奠基性厘清确立了以"最短路径"为核心的一整套网络位置度量, 接近中心性与介数中心性都建立在两点间最短路之上; Newman (2005) 进一步把介数从"仅走最短路"推广为"基于随机游走"的路径度量, 提示了同一可达性构念的不同算子化选择。平均路径长度取的是这一谱系中最聚合的一端: 不落到单点、而对全网所有点对的最短路取平均, 从而得到刻画整张网的单一形状标量。把这套源自社会网络与复杂网络物理的工具迁移到金融情境, 近年已成显学 — Yu et al. (2024)、Xu & Zhao (2024) 在资产定价语境下验证了网络位置的定价含义, Nezami et al. (2025) 的元分析则跨大量实证汇总了中心性与绩效的关系, Li et al. (2026) 更直接示范由文本反演金融网络结构与连通度。这些工作共同支撑了"以文本共现构造银行关系网、再以经典拓扑量刻画其形状"这一测度路线的当代正当性。

【识别策略定位】
net_avg_path_yr 是年内广播常数: 它对当年全部银行取同一数值, 只随年度变动。这直接决定了它在计量上的可识别边界。在含年份固定效应的双向固定效应设定下, 任何纯粹年内不变、只沿年度变化的回归元都与年度虚拟变量共线, 会被年 FE 完全吸收 — 因此本指标不能作为主设定 (银行×年双向 FE) 下的独立解释变量单独进入, 这一点与同家族里被显式标注 "year-FE absorbed" 的 net_modularity_yr / net_assortativity_yr 同理。它的合法用法是: (一) 作为刻画媒体关注结构逐年演化的宏观描述统计与时间序列证据; (二) 在放松年 FE 的设定 (如仅含银行 FE、或以年份线性趋势替代年 FE) 下作为年度层面的解释变量; (三) 与银行层面变量做交互, 让"网络紧凑度×银行特征"的交互项承载识别, 此时年内广播的主效应被吸收而交互斜率仍可识别 (Boucher et al., 2024 的一般化同群效应框架、Bramoullé et al., 2009; 2020 对通过社会网络识别同群效应的论述, 为这类基于网络结构的交互识别提供了方法论坐标, 亦提醒须警惕 Manski (1993) 的反射问题即内生/外生/关联效应的混同)。de Paula et al. (2024) 关于从面板数据识别网络连边的理论则提示: 由共现观测反演出的边本身带测量结构, 使用时应把网络视为估计对象而非外生已知。总之, 本指标的识别定位是"宏观年度结构描述量 + 交互式调节变量", 而非主回归的处理变量。

进一步就"为什么年内广播性质是识别约束而非缺陷"作三点展开。第一, 年内广播是网络级指标的构念本质而非度量瑕疵: 平均最短路径长度刻画的对象本就是"整张年度网的形状", 逻辑上不存在"某家银行的平均路径"这一概念 (那属于节点级的接近/调和中心性), 因此它在银行维度上取同值是构念定义的直接推论, 而非数据缺陷或聚合损失。把它误当银行截面变量, 相当于用一个总量去解释个体间差异, 属构念误用。第二, 与年份固定效应的共线是精确共线而非近似共线: 由于本列对全部银行严格取同一年度值, 它与年度虚拟组张成的列空间完全落入后者, 主设定下的系数不可识别不是"弱识别"或"多重共线导致方差膨胀", 而是秩亏导致的不可估, 任何报告出的非零系数都必为软件对秩亏矩阵的数值假象, 须一律警惕。第三, 合法识别通道的方法论坐标须交代清楚: 走"网络形状×银行特征"交互识别时, 是让年内广播的主效应被年 FE 吸收、而交互斜率承载"网络紧凑度对某类银行的差异化关联", 这一策略的正当性根植于同群效应识别文献 (Bramoullé et al., 2009; 2020; Boucher et al., 2024 的一般化框架), 但须同时正视 Manski (1993) 的反射问题: 网络结构、个体行为与共同环境三者的效应在观测数据中天然纠缠, 单纯的交互显著不足以断言因果, 须辅以外生变异或结构假设。而 de Paula et al. (2024) 的连边识别理论更根本地提醒: 本项目的边由媒体共现"反演"而来, 网络本身即是带测量误差的估计对象, 任何以网络结构为自变量的回归都嵌套了一层"网络测量"的一阶不确定性, 严谨的推断应把这层不确定性向下游传播 (如对建图判据做敏感性、对连边阈值做扰动), 而非把估计出的网络当外生已知的真值处理。因此本列在识别谱系里的准确站位是: 一个供描述与调节、而非供处理效应估计的年度宏观结构协变量, 其价值在于刻画媒体关注结构的逐年演化, 而非承载银行层面的因果箭头。

【与相邻测度的构念区分】
须与四类相邻测度严格区分。第一, 与同家族节点级度量区分: bank_between_cent (介数中心性)、bank_closeness_cent (接近中心性)、bank_harmonic_cent (调和中心性) 等虽同属最短路/可达性传统, 但它们是逐银行的节点属性 (回答"这家银行在网中处于多中枢的位置"), 而 net_avg_path_yr 是整张网的单一全局标量 (回答"这张网整体多紧凑"), 前者有银行截面变异、后者没有。第二, 与聚类形状量区分: net_avg_cluster_yr (年度平均聚类系数)、net_transitivity_yr (全局传递性) 刻画的是"邻居之间是否也互为邻居"的局部抱团, 与平均路径长度共同构成小世界的两个正交维度 (Watts & Strogatz, 1998), 不可互相替代。第三, 与判据后缀的正交概念空间区分: 本家族的 _win1/_sent 后缀是银行∧银行共现的邻近判据 (同篇/同窗/同句), 与三轨文本 _full/_ctx/_ss (银行∧金科口径, 服务情感与强度测度) 是两套完全正交的后缀空间, 严禁混淆, 更禁把两套后缀的列并入同一个 over-identified 的 Hansen J 检验。第四, 与情感溢出量区分: 同为"网络"标签的 peer_tone_lag1_* 是把邻居情感沿网络加权传导的溢出测度 (承载 W×tone 的语义), 而 net_avg_path_yr 只描述网络拓扑本身、不含任何情感信息。留篇门控口径遵循全项目 full-only 铁律 (2026-06-29): 一篇报道是否计入银行金科语料只看 llm_verified_full == True, 银行∧银行共现网的建图语料因此以 full 轨留篇集为宇宙, 本指标不因判据后缀而改变留篇门控。第五, 与无权跳数路径概念区分: 本列取加权口径, 单边距离等于共现频次的倒数 1/共现次数 (即 Opsahl et al., 2010 在广义度与加权最短路框架下以 1/w 类变换让边权参与距离计算的 α=1 特例), 故它回答的是"沿共现强度看有效距离几何"而非"拓扑上要走几跳"; 与仅数边跳数、不看共现强度的无权最短路属两种不同的路径构念, 二者对同一张网可给出方向不一致的紧凑度排序, 不可互指。本家族刻意选加权口径是为让共现强度参与距离刻画 (被反复一同提及的银行对视作彼此更近), 若研究问题只需不受共现频次尺度影响的纯拓扑跳数, 应另立无权度量而非重解读本列。第六, 与二模/隶属网络的投影距离区分: 本网络是把"银行—报道"的隶属关系投影为"银行—银行"一模图后再算路径, 投影本身会系统性抬高共现稠密度 (同一篇多提及的银行被投成完全子图), 故本列的路径长度须理解为"一模投影网"上的距离, 而非隶属二模网上的真实可达步数; 读者不应把它与直接在二模网上定义的距离量混为一谈。上述六重区分的共同要旨是: 平均最短路径长度是一个网络级、无权、定义于一模投影 LCC 的年度拓扑标量, 它既不是任何银行的个体属性, 也不携带情感/强度/加权信息, 更不与三轨文本后缀共享概念空间, 使用时须精确对齐其构念边界方不致误读。

【已知局限与稳健性梯子】
三条局限须披露。其一, LCC 限定带来选择性: 只被零星提及、落在小分量或孤立点上的银行不进入路径平均, 故本指标刻画的是"主体连通银行群"的距离, 在语料稀薄的早年或极端稀疏判据 (如严格同句) 下, LCC 可能很小甚至退化, 使指标方差受限 — 在盘上 T=2 的开发样本上, 严格同句判据的年度网可能过稀而使指标退化, 属预期而非缺陷, 生产 T=18 全量语料下方能正常。其二, 加权口径对共现频次尺度敏感: 本指标以 1/共现频次 为单边距离, 故对共现计数的尺度与离群高频对高度敏感 — 少数被反复一同提及的银行对因边距离极短而可能主导整条路径乃至路径均值; 其 1/w 边权变换是 Opsahl et al. (2010) 加权最短路框架中 α=1 的研究者选择, 换用其他 α (放大或压平强度差异) 或改回无权跳数口径都可能改变紧凑度排序, 属应另行披露的测量自由度, 而非唯一正确口径。其三, 共现≠真实业务关联: 媒体把两家银行写进同一叙事可能出于行业综述、政策解读等与实际业务往来无关的原因, 故本网络是"媒体关注结构"而非"资金/担保往来网络"; Li et al. (2026) 从文本反演金融网络的工作同样承认这一文本来源的测量属性。稳健性由判据梯子承载: 无后缀 (同篇)、_win1 (±1 句窗)、_sent (严格同句) 三个判据变体各自独立建图、各自 just-identified 并排, 互为稳健性、不分主次, 用以证明主结论不被"多近才算共现"这一研究者取值驱动; 三者严禁混进同一个 over-identified 的 Hansen J 检验 (镜像本项目三轨/co-primary 双轨嵌入/政治词权重梯子的统一铁律)。当多个网络形状指标或多个判据臂并列进入同一族推断时, 族层错误率控制应走根级的 rwolf/stepwise 多重检验模板, 其方法学依据为 Romano & Wolf (2005)。net_avg_path_yr 不在本项目已知的 BLAS 浮点非确定网络列清单内 (那三列是 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的判据变体), 故其取值在钉死随机种子与 BLAS 线程后可逐位复现, 属 golden 快照可安全比对的确定性列。

除上述三条主局限外, 尚有三点须补充披露以免误用。其一, 平均路径长度对语料规模的机械依赖: 报道量越大的年份越易连出稠密网、平均路径越短, 这是投影一模网的算术必然而非结构演化, 故跨年比较升降前须先控制或披露当年银行覆盖数与留篇量, 否则会把"媒体报道更多"误读成"银行关系更紧"; 稳健的做法是把逐年语料规模作为协变量或以巨分量占比归一后再比。其二, LCC 退化时的解释脆弱: 当 LCC 收缩到极少数银行 (稀疏判据或稀薄早年), 平均路径可能因样本极小而剧烈波动甚至趋近平凡值 (二三个节点的链), 此时一个"很短的平均路径"其实是退化假象而非真紧凑, 故报告本列时应强制并列 net_giant_share_yr 与连通分量数, 让读者据以判断路径均值算在多大比例的银行群上。其三, 判据梯子承载的是"邻近半径"这一单一维度的稳健性, 不覆盖其他建模自由度 (无权/加权、一模投影方式、留篇门控口径), 故三臂一致只证明结论不被"多近算共现"驱动, 不等于对全部测量选择稳健; 完整披露应在判据梯子之外另报无权与其他口径的敏感性。就稳健性梯子的统计纪律再作强调: 无后缀 (同篇)、_win1 (±1 句窗)、_sent (严格同句) 三个判据变体是同一构念在不同邻近门槛下的重复测量, 彼此高度共线, 只能各自独立建图、各自 just-identified 并排比对系数方向与显著性的一致性, 互为稳健性、不分主次, 严禁把三臂列并入同一个 over-identified 的 Hansen J 过度识别检验 (此为镜像本项目三轨 full/ctx/ss、co-primary 双轨嵌入、政治词权重、词典消融各梯子的统一铁律)。当多个网络形状指标或多个判据臂并列进入同一族的多重假设推断时, 族层错误率 (FWER) 的控制应走根级 rwolf/stepwise 多重检验模板, 其方法学依据为 Romano & Wolf (2005) 关于把逐步多重检验形式化为数据窥探控制的工作; 切勿以逐臂单独显著充当族层结论。

最后就下游使用给出几点操作性提示。第一, 报告本指标时须显式说明"定义于最大连通分量"这一限定, 并同时报告巨分量占比 (net_giant_share_yr) 与连通分量数 (net_n_components_yr), 以便读者判断路径平均是在多大比例的银行群体上算出的 — 否则一个很短的平均路径可能只是因为 LCC 退化到极少数银行所致, 会造成"网络很紧凑"的误读。第二, 由于本指标是年内广播常数, 任何把它当作银行截面处理变量、又同时放年份固定效应的设定都会得到被完全吸收的零系数, 这不是"无效应"而是共线性人为造成的假象; 正确做法是移到年度层面分析或走交互式识别。第三, 跨年比较平均路径长度时须注意语料规模的逐年变化: 报道量大的年份更易连出稠密网、路径更短, 故直接把逐年平均路径的升降解读为"银行关系真的变紧或变松"时, 应先控制或至少披露当年语料规模与银行覆盖数, 避免把语料规模效应误当结构演化。第四, 本指标与情感、强度等文本测度正交, 可与后者交叉但不可互相替代: 平均路径长度只回答"网络长什么形状", 不携带任何关于报道情感倾向或金科强度的信息, 二者服务不同的研究问题。综上, 本家族提供的是一个纯拓扑、纯年度、判据可调的媒体关注结构紧凑度标量, 其价值在于以经典且可跨文献比对的方式刻画"银行被媒体共同提及的关系网有多紧密", 并通过同篇、句窗、同句三档判据梯子把这一刻画的稳健性系统地做实。

## VAR: net_avg_path_yr

【变体差分】
本列是家族 canonical、tier=core, 采用无后缀判据即"同篇共现"口径: 只要两家银行出现在同一篇留篇报道中 (银行名扫描以 prepend_title 后的标题作为第 0 句、正文顺次其后, 镜像 stage 13 的 match_in_title 口径), 即在当年图上连一条无向边, 不要求它们出现在相近的句子里。这是三个判据变体中最宽松的一档, 因而建出的年度共现网最稠密、连通性最强、LCC 覆盖的银行最多, 相应地平均最短路径长度通常最短。它被指定为家族核心列的理由是: 同篇共现是本项目银行∧银行共现网的历史现行口径与默认锚 (NETWORK_METRIC_BASES 中登记的正是此无后缀基名), _win1 与 _sent 是围绕它展开的判据敏感性稳健臂。语义上, 本列度量"在当年被任一媒体叙事共同提及而彼此关联的银行群体内, 两家银行在共现关系网上典型要走几步才相连", 取值定义于最大连通分量、以加权最短路距离计 (单边距离=1/共现频次, 共现越强边越短)。作为网络级年内广播常数, 本列对当年全部银行取同一值、只随年度变化, 在含年份固定效应的主设定下会被年 FE 吸收, 其合法角色是宏观年度结构描述量与交互式调节变量 (识别定位详见 CORE 识别策略段)。本列与 _win1、_sent 两个更严判据臂各自独立建图、各自 just-identified 并排, 三者互为稳健性、不分主次, 严禁并入同一 over-identified 的 Hansen J; 判据后缀空间与三轨文本 _full/_ctx/_ss (银行∧金科口径) 正交, 不得混用。须再次强调: 无后缀在此仅表"canonical 同篇口径"的命名产物, 不隐含它比另两臂"更主要或更真"的地位, 判据孰优应由三臂并列的实证一致性判定, 而非由后缀有无判定。就取值行为而言, 因同篇是最宽判据, 本列的年度共现网在三臂中连边最多、巨分量最大, LCC 覆盖的银行数最高, 故其平均路径长度在同一年份上通常最短且方差相对充裕, 在语料稀薄的早年或开发样本上退化的风险也最小 (相比之下严格同句臂最易退化)。这一"最宽判据 → 最紧网络 → 最短路径"的单调倾向, 使本列成为家族里信息量最饱满、最适合承载家族核心叙事的一档, 其余两臂用来回答"把共现门槛收紧后结论是否依旧成立"。使用建议: 在报告年度媒体关注结构的演化趋势、或构造"网络紧凑度×银行特征"交互项时, 优先以本 canonical 列为主轴, 再以 _win1、_sent 两臂做并列稳健性复现; 切勿把三臂当作三个独立信息源塞进同一个过度识别的工具变量集或 Hansen 过度识别检验, 因为它们本质是同一构念在不同邻近门槛下的重复测量, 高度共线, 只能各自 just-identified 并排比对系数方向与显著性的一致性。作为家族核心列, 本列亦是家族命名的锚点: NETWORK_METRIC_BASES 登记的正是本无后缀基名, _win1 与 _sent 由 _ADJ_CRITERIA 三元组在建图阶段机械派生, 三列共享同一套银行名扫描与否定/短名排除事实源, 仅在"多近算共现"这一维度上取值不同。因此读者若只需一个代表性网络紧凑度变量, 应默认取本列; 若需完整披露稳健性, 则三列并列同报。

## VAR: net_avg_path_yr_sent

【变体差分】
本列 tier=standard, 采用最严的"严格同句"判据 (_sent): 仅当两家银行出现在同一个句子内时才在当年图上连边, 跨句共现一律不计。相对于 canonical 的同篇口径, 这是三档判据里最保守的一档 — 它把"关联"的门槛收到最紧, 只承认句子层级的紧邻共提。后果是: 建出的年度共现网最稀疏、边最少、连通性最弱, 最大连通分量往往显著变小, 落在小分量或孤立点上而被排除出路径平均的银行最多; 在语料稀薄时该判据下的年度网可能过稀甚至退化 (开发样本 T=2 上尤为明显, 属预期退化而非缺陷)。因此本列刻画的是"仅凭句内紧邻共提所构成的银行核心关联网"的紧凑度, 是对 canonical 结论"是否只由宽松的同篇共现口径撑起"的稳健性检验臂。判据原语与 canonical 同源 (map_bank_sentence_positions 逐句定位银行、以严格同句配对), 只是把配对窗口收到句内。本列与 canonical 及 _win1 各自独立建图、各自 just-identified 并排, 三者互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J。须注意 _sent 是银行∧银行共现的邻近判据后缀, 与三轨文本的 _ss (银行∧金科严格同句) 分属两个正交概念空间, 名字里都有"句"却口径迥异, 不可互指或互相复用。

## VAR: net_avg_path_yr_win1

【变体差分】
本列 tier=standard, 采用居中的"±1 句窗"判据 (_win1): 当两家银行出现在相距不超过 win_radius 个句子的窗口内时即连边, win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1)。它介于 canonical 的同篇 (最宽) 与 _sent 的严格同句 (最严) 之间, 是三档判据梯子的中间刻度 — 既比严格同句宽松, 承认跨相邻句的紧邻共提; 又比同篇严格, 排除相隔很远、可能只是同篇罗列而无真实语义关联的银行对。因此本列建出的年度共现网稠密度与连通性居中, 平均最短路径长度通常落在同篇口径与严格同句口径之间, 用以检验主结论对"共现邻近半径"这一研究者取值是否稳健、是否只在某一特定窗口下成立。win_radius 键与 stage 13 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的键, 前者管银行∧银行网络建图、后者管银行∧金科留篇过滤, 不得混淆。本列与 canonical 及 _sent 各自独立建图、各自 just-identified 并排, 三者互为稳健性、不分主次, 严禁并入同一 over-identified 的 Hansen J; 判据后缀 _win1 与三轨文本后缀属正交概念空间。作为网络级年内广播常数, 本列同样在含年份固定效应的主设定下被年 FE 吸收, 合法角色为年度结构描述量与交互调节项。取值上, 由于 ±1 句窗判据的松紧居中, 本列建出的网稠密度与连通性介于同篇与严格同句之间, 其平均路径长度一般也落在两端之间, 恰好提供一个连续收紧共现半径的中间观测点: 若三臂 (同篇 → ±1 句窗 → 严格同句) 的结论随门槛单调而平滑地变化, 则说明主结论对邻近半径取值稳健; 若中间臂出现方向翻转或显著性断裂, 则提示结论可能对特定窗口敏感, 须审慎解读。

<!-- rendered-citations:begin -->
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Gao, Q., Fan, H., & Yu, C. (2024). Systemic Importance and Risk Characteristics of Banks Based on a Multi-Layer Financial Network Analysis. Entropy. https://doi.org/10.3390/e26050378
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Han, M., Kim, S. H., & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Xu, G. (2024). News Bias in Financial Journalists' Social Networks. Journal of Accounting Research. https://doi.org/10.1111/1475-679x.12560
Wang, L., Hou, W., & Liu, Y. (2023). How do co-shareholding networks affect negative media coverage? Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13091
Fan, H., & Hu, C. (2024). Research on systemic risk of China's bank-asset bipartite network. Heliyon. https://doi.org/10.1016/j.heliyon.2024.e26952
Wei, W., Wang, Z., Wang, Y., & Song, Y. (2026). Transfer entropy, multidimensional multiple correlation network, and risk contagion of bank capital shortage. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-026-07085-3
<!-- rendered-citations:end -->
