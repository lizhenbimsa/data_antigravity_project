---
family_id: F457
columns:
- net_assortativity_yr
- net_assortativity_yr_sent
- net_assortativity_yr_win1
unit: 无量纲相关系数 (度-度 Pearson 相关, 取值域 [-1, 1])
formula: "net_assortativity_yr = 年度银行共现网络上度-度 Pearson 相关系数 (networkx degree_assortativity_coefficient); 三判据变体 {同篇 (无后缀 canonical) / ±1 句窗 _win1 / 严格同句 _sent} 各自独立重建邻接后计算"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality ; news_process/pipeline/panel/export.py (标签块)
upstream:
- "11_news_bank.parquet (银行实体命中: 逐篇被提及银行集合)"
- "14_materialize_ctx.parquet (content_full: 供 _win1/_sent 判据的分句扫描文本源)"
citations:
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: "10.1057/s41599-025-04419-5"
  type: "journal"
  authors: "Petersen, A. M."
  year: 2026
  title: "University digital media co-occurrence networks reveal structure and dynamics of brand visibility in the attention economy"
  venue: "Humanities and Social Sciences Communications"
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  issue: ""
  pages_or_artno: 103223
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
  issue: ""
  pages_or_artno: 171-202
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  issue: ""
  pages_or_artno: 603-629
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1103/PhysRevE.69.026113
  type: journal
  authors: Newman, M. E. J., & Girvan, M.
  year: 2004
  title: "Finding and evaluating community structure in networks"
  venue: Physical Review E
  vol: 69
  issue: 2
  pages_or_artno: 026113
- doi: 10.1103/PhysRevE.70.066111
  type: journal
  authors: Clauset, A., Newman, M. E. J., & Moore, C.
  year: 2004
  title: "Finding community structure in very large networks"
  venue: Physical Review E
  vol: 70
  issue: 6
  pages_or_artno: 066111
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
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1016/j.ejor.2023.07.010"
  type: journal
  authors: "Ricca, F., & Scozzari, A."
  year: 2024
  title: "Portfolio optimization through a network approach: Network assortative mixing and portfolio diversification"
  venue: "European Journal of Operational Research"
- doi: "10.1080/14697688.2026.2681609"
  title: "A network-based mixture transition distribution approach to portfolio optimization"
  authors: "De Blasis, R., Galati, L., & Petroni, F."
  year: 2026
  venue: "Quantitative Finance"
  type: "journal"
- doi: "10.1371/journal.pone.0284861"
  title: "Systemic risk prevention policies targeting systemically important banks: Does clustering pattern matter?"
  authors: "Zhu, B., Hu, X., Deng, Y., & Lin, R."
  year: 2023
  venue: "PLOS ONE"
  type: "journal"
new_dois:
- "10.1057/s41599-025-04419-5"
- "10.1016/j.ejor.2023.07.010"
- "10.1080/14697688.2026.2681609"
- "10.1371/journal.pone.0284861"
---

## CORE

该文构建大学数字媒体共现网络并分析其度混合(assortativity)结构与动态, 揭示品牌能见度在注意力经济中呈现异配式排序, 为本家族用共现网络度混合系数刻画媒体报道结构提供了2025年的同类方法学同行范例。

【构念与来源】
本家族刻画的是银行同现网络 (co-mention network) 的年度度混合模式 (degree assortativity), 即在给定年份内, 由媒体报道所织成的银行-银行关系图中, "高连接度节点是否倾向于与高连接度节点相邻"这一整体结构属性。构念的数据源头是新闻语料: 当两家目标银行在同一篇报道 (或同一句窗、同一句) 中被共同提及时, 判定二者之间存在一条无向边, 边权为共现次数; 把某一年内全部报道累积起来, 就得到该年的银行同现网络。度混合系数正是在这张年度网络上, 对所有相邻节点对的度取 Pearson 相关系数的结果, 取值域为闭区间 [-1, 1]。正值 (assortative, 同配) 表示大银行倾向与大银行同框、边缘银行倾向与边缘银行同框, 网络呈现"核心-核心抱团"的层级化结构; 负值 (disassortative, 异配) 表示高度节点更多连向低度节点, 呈"星形辐射/枢纽-外围"结构; 接近 0 则度与邻居度无系统关联。金融与技术类网络在经验上常呈弱异配, 而社会性网络常呈同配, 因此该系数是判别同现网络"究竟更像社交攀附还是更像信息辐射"的一个高度浓缩的形状指标。

【构念与来源】
之所以把度混合系数纳入面板, 是因为它捕捉的是单一节点级中心度无法表达的二阶结构信息: 两张网络可以有完全相同的度分布 (因而 net_degree_gini_yr 一致)、相同的密度 (net_density_yr 一致), 却因为"谁连谁"的搭配规则不同而呈现截然相反的传染与信息扩散动力学。系统性风险与同业传染文献 (Jackson & Pernoud, 2021) 反复强调, 网络的连接拓扑而非单纯的连接数量, 决定了冲击沿网络放大还是耗散; 资产定价侧的证据 (Yu et al., 2024) 也表明, 节点在信息扩散网络中的位置塑造了收益可预测性。度混合作为一个网络级 (whole-graph) 汇总量, 与本项目其余 32 个结构基名 (见 network_spillover.NETWORK_METRIC_BASES 的 33 基名 SSOT) 一同构成"共现网络形状"的多维刻画, 服务于同业情绪溢出、跟风与关注度等下游研究设计对网络异质性的控制与机制解读需求。

【方法学与计算】
计算入口是 network_spillover.compute_bank_network_centrality: 先由逐篇被提及银行集合累积出年度加权邻接 (边权=共现次数), 再用 networkx 在该图上求度混合系数 (degree_assortativity_coefficient, 即 Newman 意义下按边端点度构造联合分布后的 Pearson 度-度相关)。须精确披露一处易被 formula 框架误导的实现细节: 引擎调用 degree_assortativity_coefficient(G) 时未传 weight 参数, networkx 默认 weight=None, 因而"度"取的是无权度 (unweighted degree, 即每个节点的邻居计数), 而非以共现次数加权的强度 (weighted degree/strength)。换言之, 邻接图虽携带边权, 但度混合的度-度相关是在无权度上计算的; 边权仅影响其余以 weight='weight' 显式传参的指标 (如 net_modularity_yr), 不参与本系数。加权度口径下的度混合是一条尚未落地的敏感性方向, 详见 CORE 局限节。net_assortativity_yr 属于"网络级、年广播"指标 —— 同一年份下所有银行共享同一个标量, 因此在含年份固定效应 (year FE) 的回归中会被完全吸收 (export.py 标签明确标注 year-FE absorbed)。这一点决定了它在项目里的定位: 不是作为逐行变异的处理变量或结果变量进入主回归, 而是作为 (a) 跨年份网络演化的描述性证据、(b) 交互项母项 (与银行级变量交乘后不再被年 FE 吸收)、(c) 子样本切分或异质性分层的依据。这与 Watts & Strogatz (1998) 开创的"以少数全图标量概括复杂网络形状"的传统一脉相承 —— 聚类系数、平均路径长度、度混合共同构成"小世界/层级/随机"三分判别的经典指标组。

【方法学与计算】
边的判定原语是共现 (co-occurrence) 而非任何语义相似度或情绪一致度, 主体是"银行∧银行", 与 stage 13 共现硬过滤的"银行∧金科"判据是两个正交的概念空间, 禁止互相复用其阈值或原语。银行侧命中沿用与 stage 11/13/ctx/ss 同一套否定与短名排除事实源 (load_exclusion_patterns 提供的 negation_ac 与 short_name_exclusions), 以防"涉农行业"误触发"农行"这类短名假阳性; 扫描文本包含 prepend 后的标题 (第 0 句), 镜像 stage 13 的 match_in_title 口径。窗口半径 win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1), 与 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的独立键, 切勿混淆。对于孤立点或仅有单边对等平凡结构, 度混合系数在数学上可能退化为 NaN (度-度相关的分母度方差为零), 引擎对此的处理是一道专属的度方差守卫: 当全图度序列去重后取值不超过一个 (即所有节点同度, len(set(degrees)) <= 1) 时直接置 NaN, 否则调用 networkx 并对返回的非有限值 (inf/NaN) 再置 NaN, 退化格记 NaN 而非虚假 0。须特别澄清: 本指标的 NaN 退化与连通分量最小门槛无关 —— 引擎里的 _CMNT_MIN_COMPONENT_SIZE = 3 仅作用于 bank_eigen_cent 等节点级中心度的巨分量筛选, 度混合系数是网络级全图量, 不施加该分量门槛, 其唯一的退化来源就是上述度方差为零的守卫。

【文献定位】
度混合系数最初由网络物理学界提出用于刻画度-度关联, 本项目沿用其在社会与金融网络中的解读传统。在网络计量与同业效应识别脉络上, 它与 Bramoullé et al. (2009) 关于"通过社会网络识别同业效应"的框架相衔接: 网络的拓扑形状 (包括度混合) 决定了 Manski (1993) 反射问题下内生、外生与关联效应能否被分离 —— 当网络存在充分的度异质与非完全传递结构时, 邻居的邻居可作为工具从而打破反射问题的不可识别性。Bramoullé et al. (2020) 的综述与 Boucher et al. (2024) 的一般化理论进一步指出, 同一度分布下不同的连接搭配 (即不同的度混合) 会实质改变同业效应的可识别性与效应量。公司金融侧, Leary & Roberts (2014) 与 Grieser et al. (2022) 证明同业网络结构显著塑造企业融资与资本结构决策, 为"把网络形状纳入银行面板作为环境控制"提供了直接的实证正当性。

【文献定位】
在方法学层面, 度混合系数的估计与推断须与本项目的稳健性推断工具链协同。因其属年度广播量、样本单位是"年份-网络"而非"银行-年", 常规的银行层聚类稳健标准误对本指标的直接回归并不适用; 在把它作为交互母项使用时, 交互项的推断须回到银行-年层并采用适当的聚类或 wild bootstrap。这与本项目在同业溢出、跟风等设计中采用的多重检验校正 (根级 rwolf 模板) 和网络计量识别框架 (Bramoullé et al., 2009) 是一致的方法论姿态: 网络形状变量不是即插即用的回归自变量, 而是需要显式声明其年 FE 吸收性质、样本层级与推断口径的结构量。Yu et al. (2024) 与 Han et al. (2024) 在资产定价与市场微结构语境下对网络位置变量的处理, 为这种"先声明结构性质、再选推断口径"的做法提供了同行范例。此外, 度混合系数与社群结构算法 (Newman & Girvan, 2004; Clauset et al., 2004) 在计算上共享同一张年度邻接图但回答不同问题, 二者的联合报告能帮助读者区分"网络是否分块"与"高度节点是否抱团"这两个常被混淆的结构维度, 从而降低对度混合符号的过度解读风险。正因如此, 本项目坚持把度混合与模块度、传递性、密度、基尼等网络级形状量成组入库而非择一保留, 使任何单一维度都无法孤立地主导对银行舆论共现网络整体形状演化的判读。De Blasis, Galati, & Petroni (2026, Quantitative Finance) 该文将网络式度量(含度混合/连接结构)嵌入投资组合优化框架, 为本家族把度混合系数用作金融网络整体形状测度提供最新方法学同行范例。Zhu, Hu, Deng, & Lin (2023, PLOS ONE) 该文考察银行网络中同质银行抱团(clustering pattern)对系统性风险防范政策有效性的影响, 为度混合(同配/异配)结构与系统性风险传染的关联提供了2023年的实证证据。Ricca & Scozzari (2024, European Journal of Operational Research) 该文将度/强度混合系数(degree/strength assortativity)直接引入金融资产网络构建与投资组合优化, 为本家族把度混合系数用作银行舆论共现网络整体形状测度提供了同一测度在金融网络语境下的最新方法学同行范例。

【文献定位】
在中心度与网络绩效的更广谱系里, Freeman (1978) 奠定了中心度的概念澄清, Newman (2005) 与 Newman & Girvan (2004)、Clauset et al. (2004) 分别贡献了随机游走介数与社群结构 (模块度) 的度量与算法 —— 它们与度混合共同属于"网络级形状"家族的不同侧面: 模块度 (net_modularity_yr) 回答"网络是否分块", 度混合回答"高度节点是否抱团", 二者可以正交变化。Nezami et al. (2025) 对中心度-绩效关系的元分析提醒: 网络位置效应高度依赖于测度选择与网络构造口径, 因而本项目刻意并排多种网络级形状指标与多重构造判据, 以避免单一测度驱动结论。金融网络传染 (Jackson & Pernoud, 2021)、经纪流动性 (Han et al., 2024) 与信息扩散资产定价 (Yu et al., 2024) 则从系统性风险、市场微结构与定价三个维度, 说明为何银行同现网络的整体形状具备经济含义。

【方法学与计算】
关于符号与经济解读的先验期待, 须结合中国银行业舆论场的制度背景给出。银行同现网络的度天然高度右偏: 少数大型国有商业银行与全国性股份制银行因业务覆盖广、政策关注度高, 几乎在任何涉银行报道中都可能被点名, 从而积累极高的共现度; 大量地方城商行、农商行则度很低。若媒体倾向于把"大行与大行并列点评" (例如同题报道六大行), 网络将呈同配 (正度混合); 若报道更多是"一家大行辐射式带出若干小行" (如龙头引领区域银行的产业报道), 则呈异配 (负度混合)。因此本指标的年度符号本身即携带对"媒体叙事结构"的可检验含义, 而其跨年演化 (是否随金融科技叙事兴起、监管周期变化而系统性漂移) 是描述性证据的主要落点。正因符号对语料结构敏感, 本项目才以三判据梯子而非单一口径入库, 让"符号是否稳健于邻近半径"成为一等公民式的稳健性问题。

【识别策略定位】
本家族在识别上的角色须精确界定, 以免误用。首先, 由于 net_assortativity_yr 及其两个判据变体都是"一年一值"的网络级广播量, 它们在任何含 year FE 的规格中都被完全共线吸收, 不能单独作为主回归右手侧的处理变量出现 —— 这是设计意图而非缺陷 (export.py 标签写明 year-FE absorbed)。其可用识别位置有三: 其一, 作为描述性时序证据, 刻画银行舆论网络在样本期内 (真实全量 2007-2025, T=19) 从异配走向同配 (或反之) 的结构演化; 其二, 作为交互母项, 与银行级或年份内变异变量交乘, 交互项因携带跨银行变异而逃逸年 FE 吸收, 从而识别"网络形状如何调节个体层机制"; 其三, 作为样本分层或稳健性子样本切分的依据。凡将本指标用于任何回归设定, 都须显式声明其被年 FE 吸收的事实, 并将其归入网络形状规格稳健性并排族, 而非因果处理变量。

【识别策略定位】
在同业效应 (peer effects) 识别的更严格框架下, 度混合系数的价值在于诊断而非工具本身。Bramoullé et al. (2009, 2020) 指出, 网络结构的非传递性 (intransitivity) 是"邻居的邻居"型工具变量成立的前提, 而度混合与传递性 (net_transitivity_yr)、模块度共同刻画了这种结构条件是否满足; 当网络高度同配且高传递时, 反射问题 (Manski, 1993) 更难被打破。因此本项目把度混合与其余网络级形状量并置, 主要用于事后论证识别假设的合理性区间, 以及在 Boucher et al. (2024) 式一般同业效应模型下解释效应量的结构来源。需要强调, 这三个判据变体互为稳健性、不分主次, 各自 just-identified 并排; 严禁把 net_assortativity_yr、net_assortativity_yr_win1、net_assortativity_yr_sent 三者混入同一个 over-identified 的 Hansen J 过度识别检验 —— 这与本项目三轨 (full/ctx/ss)、co-primary 双轨嵌入、政治词权重梯度、词典消融梯度所遵循的同一条铁律完全一致。

【与相邻测度的构念区分】
度混合系数须与本项目若干形近的网络级或节点级测度严格区分, 以免解读串扰。与 net_degree_gini_yr (年度度分布基尼) 的区分: 基尼只看度分布的不平等程度 (一阶边际), 完全不看谁连谁; 两张网络可以有相同基尼但相反符号的度混合。与 net_modularity_yr (CNM 社群模块度, Clauset et al., 2004; Newman & Girvan, 2004) 的区分: 模块度衡量网络能否被切成内密外疏的社群块, 是"分块性", 而度混合是"度相似性搭配", 一个高度同配的网络未必模块化, 反之亦然。与 net_transitivity_yr / net_avg_cluster_yr (全局传递性 / 平均聚类, Watts & Strogatz, 1998) 的区分: 后者衡量三角闭合倾向 (朋友的朋友也是朋友), 与度混合正交 —— 度混合看的是相邻两端的度是否匹配, 与三角闭合无必然关系。

【与相邻测度的构念区分】
与节点级中心度族 (bank_degree_cent、bank_eigen_cent、bank_between_cent 等, 见 Freeman, 1978; Newman, 2005) 的区分尤为关键: 中心度是"一个银行在网络中的个体位置", 逐行变异、在年 FE 下存活、可作处理变量; 度混合是"整张年度网络的宏观形状", 一年一值、被年 FE 吸收。二者回答的问题层级不同 —— 前者服务于"哪家银行更居于舆论枢纽", 后者服务于"今年的银行舆论场整体更像抱团还是辐射"。此外, 度混合不同于经纪与结构洞族 (bank_constraint、gf_* 系列, Han et al., 2024 构念锚): 后者刻画个体跨结构洞的中介能力, 度混合不含任何"中介"语义。把这些测度并排入库、而非择一, 正是回应 Nezami et al. (2025) 元分析的告诫: 网络位置与绩效的关系对测度口径极度敏感, 唯有多测度并列才能证伪"单一测度驱动结论"的质疑。

【已知局限与稳健性梯子】
第一类局限是测量层面。共现网络的边完全由"被同框提及"定义, 因此度混合系数继承了媒体报道的一切选择性偏差 —— 报道强度高、常被并列点名的大型国有行天然获得更高度, 网络形状因而部分反映的是媒体注意力结构而非银行间真实业务关联。第二类是稀疏与退化局限: 在早期试跑 T=2 开发切片 (约 110 家银行 × 2 年) 或任一年内共现极稀疏时, 年度网络可能不连通、巨分量偏小, 度混合系数方差不稳甚至退化为 NaN; 生产 T=19 全量语料下这一问题大幅缓解, 但仍须以巨分量份额 (net_giant_share_yr) 与连通分量数 (net_n_components_yr) 作伴随诊断。第三类是浮点非确定性: 与 bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 类似, 部分网络列在不同 BLAS 线程配置下存在末位浮点漂移, golden 复现须钉死 PYTHONHASHSEED=0 且全 BLAS 线程置 1 后按全名排除相关列比对。

【已知局限与稳健性梯子】
第四类局限是解释边界。度混合系数是一个高度浓缩的全图标量, 它把整张网络"谁连谁"的复杂搭配压缩为一个数, 因而对局部结构变化 (如某几家银行的连边重排) 可能不敏感, 也无法定位"是哪一部分节点在驱动同配/异配"。这意味着它更适合作为宏观形状的粗粒度描述, 而非精细机制的证据; 需要更细结构时应转向节点级中心度族 (Freeman, 1978; Newman, 2005) 或社群/经纪测度 (Newman & Girvan, 2004; Han et al., 2024)。第五类是可比性局限: 度混合系数对网络规模与密度并非完全不变, 跨年比较时若年度网络规模差异悬殊 (报道量随语料年份增长), 系数的可比性会受影响, 因此跨年解读须同时报告 net_density_yr 与节点数作为背景, 避免把"规模效应"误读为"结构演化"。

【已知局限与稳健性梯子】
第六类是加权口径的敏感性。度混合系数在本项目中按 networkx 的度-度定义在累积邻接上计算, 其"度"取无权度还是加权度会实质改变系数量级与符号: 若以共现次数为边权计加权度, 高频并置的大行对会被进一步放大, 系数更易呈同配; 若仅以是否共现计无权度, 则弱化了媒体重复点名的强度信息。本项目的现行生产口径明确取无权度 (network_spillover 引擎调用 degree_assortativity_coefficient(G) 未传 weight, networkx 默认 weight=None, 即以邻居计数而非共现次数计度), 因此当前入库的三判据系数刻画的是"是否共现"这一结构层面的度匹配, 而非"共现多密集"这一强度层面的匹配; 加权度口径 (以共现次数为边权) 尚未落地为独立列。读者在跨研究比较时须留意度混合的加权约定差异, 不可将不同加权口径下的系数直接并列。这一敏感性与前述"对网络规模/密度非完全不变"的可比性局限相互叠加, 共同要求跨年、跨口径解读时都以 net_density_yr 与节点数、边数作为背景注脚。度混合作为二阶结构量的高浓缩性, 使其在信息量与可解释性之间存在固有张力: 它以单一标量概括了整张网络的搭配规则, 因而极适合作为规格稳健性并排族的宏观形状锚, 却不适合承担精细的、可定位到具体银行对的机制论证。

针对上述局限, 本家族内建的一级稳健性梯子正是三判据变体 {同篇 (无后缀 canonical) / ±1 句窗 _win1 / 严格同句 _sent}: 三者以逐渐收紧的邻近性阈值重建邻接, 检验"网络形状结论是否对'多近才算共现'这一构造选择稳健"。同篇判据最宽松 (只要同文即连边), 句窗判据要求两行在 ±1 句范围内共现, 严格同句判据最保守 (须落在同一句)。判据越严, 网络越稀疏、边越少, 度混合估计的样本量与稳定性也随之变化 —— 因此三变体并排既是稳健性证据, 也是对"媒体并置强度"这一潜在混杂的分层探测。再次重申铁律: 三判据变体各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 判据后缀 (article/win1/sent, 银行∧银行) 与三轨文本后缀 (full/ctx/ss, 银行∧金科) 属两个正交概念空间, 不得跨族混用。与本项目 n_articles 相关的留篇门控口径 (2026-06-29 起 full-only) 只作用于情绪留篇与文本轨, 与本网络家族的银行∧银行判据无耦合关系, 二者不应相互推断。

## VAR: net_assortativity_yr

【变体差分】
本列是家族 canonical (无判据后缀), 也是 tier=core 的核心列, 对应 network_spillover.NETWORK_METRIC_BASES 中的 net_assortativity_yr 基名。它采用最宽松的"同篇 (article)"共现判据: 只要两家目标银行在同一篇报道内 (标题 prepend 后的全文范围) 被共同提及, 即在该年网络中连一条边并累积权重; 随后在累积得到的年度加权银行同现图上, 用 networkx 计算度混合系数 (度-度 Pearson 相关), 取值域 [-1, 1]。与两个带后缀的兄弟列相比, 本列不施加任何句级邻近约束, 因而在三判据中给出最稠密的年度网络、最大的边集与最稳定的样本量, 是其余两个变体的稳健性参照基准。这一"同篇即共现"口径是本项目网络指标族的现行生产口径 (与 stage 13 共现硬过滤的宽松端一致的邻近哲学, 但主体为银行∧银行、判据原语为 map_bank_sentence_positions 系而非 stage 13 的银行∧金科原语, 两者禁互相复用)。

【变体差分】
作为核心列, 本列承担家族的语义锚定与下游默认引用: 当研究设计只需单一网络形状代表值时, 默认取本无后缀列; _win1 与 _sent 仅在稳健性小节被并列引用。须再次明确其识别定位: 本列一年一值、网络级广播, 在含 year FE 的任何规格中被完全吸收 (export.py 标签: Newman 2002; year-FE absorbed), 故只能作描述性证据、交互母项或分层依据, 不能作主回归处理变量。计算上, 对孤立点、单边对或度方差为零的平凡年度网络, 系数由一道度方差守卫 (全图度去重后取值不超过一个即 len(set(degrees)) <= 1 时直接置 NaN) 加 networkx 返回值的非有限检查共同退化置 NaN, 绝不虚构 0 值; 该退化与连通分量最小门槛 _CMNT_MIN_COMPONENT_SIZE 无关 (后者只筛节点级中心度的巨分量, 不作用于本网络级量); 在早期试跑 T=2 开发切片上因网络极稀疏, 本列可能大面积 NaN 或方差不稳, 属预期退化, 生产 T=19 全量语料下方给出可解读的年度序列。本列与家族内 net_degree_gini_yr、net_modularity_yr、net_transitivity_yr 正交互补 (分别刻画度不平等、分块性、三角闭合), 联合读取方能完整描述共现网络形状; 其局限、浮点非确定性与稳健性梯子叙事已在 CORE 节完整给出, 此处不再重复。作为核心列, 本列亦是三判据稳健性并排的 canonical 参照臂 —— 三变体各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

【变体差分】
在与文献对话的层面, 本核心列是把 Newman 传统的度混合概念落地到"银行舆论共现网络"这一特定语料上的具体实现, 其经济含义须放在同业效应与系统性风险两条脉络下解读。一方面, 网络的度混合结构是 Bramoullé et al. (2009, 2020) 与 Boucher et al. (2024) 所论同业效应可识别性的结构前提之一: 高度异配 (枢纽-外围) 网络往往具备更强的非传递性, 更利于"邻居的邻居"型工具打破 Manski (1993) 反射问题; 高度同配 (核心抱团) 网络则相反。另一方面, Jackson & Pernoud (2021) 强调传染沿网络放大与否取决于拓扑而非连边数量, 而 Grieser et al. (2022)、Leary & Roberts (2014) 证明同业网络形状实质影响企业融资决策 —— 这为把本核心列作为"银行所处舆论网络环境"的宏观刻画、进而作交互母项或分层依据提供了实证正当性。同时须谨记 Nezami et al. (2025) 元分析的告诫: 网络位置-绩效关系对测度与构造口径高度敏感, 故本核心列绝不单独承载结论, 必与家族内 net_modularity_yr、net_transitivity_yr、net_degree_gini_yr 等正交形状量以及两个判据兄弟列并排解读, 方能证伪"单一测度或单一构造口径驱动结论"的质疑。本列作为 canonical 默认引用臂的地位, 正是这一多测度、多判据并排哲学的锚点。

## VAR: net_assortativity_yr_sent

【变体差分】
本列 (tier=standard) 是度混合系数的"严格同句 (sent)"判据变体: 仅当两家目标银行落在同一个句子内被共同提及时才连边, 是三判据中最保守、最稠密约束的口径。相较 canonical 的"同篇即共现", 严格同句判据剔除了大量"同文但分处不同段落/句子"的弱共现, 因而重建出的年度网络边最少、最稀疏, 度混合估计所依赖的相邻节点对样本量也最小。其构念意图是检验"网络形状结论是否只在最紧密的句级并置证据下依然成立"—— 若同篇与同句判据给出方向一致的度混合符号, 则可较有力地排除"结论仅由松散的跨句共现噪声驱动"这一替代解释。判据原语沿用 core/text/entity_context 的银行分句定位系 (逐句 has_unexcluded_occurrence 扫描, 含 prepend 标题第 0 句), 与 canonical 共享同一套否定/短名排除事实源, 差异仅在邻近半径收紧至同句。

【变体差分】
本列与 canonical、_win1 互为稳健性、不分主次, 三者各自 just-identified 并排, 严禁三列混入同一 over-identified Hansen J —— 这是判据敏感性梯子的核心铁律。须特别注意, 本列的 _sent 后缀是网络构造判据 (银行∧银行, 严格同句), 与三轨文本体系里 _ss 轨 (银行∧金科同句) 是两个正交概念空间, 后缀字面相近但语义无涉, 不得跨族混读或混入同一识别检验。识别定位与 canonical 完全一致: 一年一值、网络级广播、在 year FE 下被吸收, 只作描述、交互母项或分层用。在早期试跑 T=2 开发切片上, 因同句判据把本已稀疏的网络进一步稀疏化, 本列出 NaN 或零方差的概率高于 canonical, 属预期退化, 须结合 net_giant_share_yr 与 net_n_components_yr 判读其可靠性; 生产 T=19 全量语料下方具备稳定可解读性。

## VAR: net_assortativity_yr_win1

【变体差分】
本列 (tier=standard) 是度混合系数的"±1 句窗 (win1)"判据变体, 邻近性严格程度居于 canonical (同篇) 与 _sent (严格同句) 之间: 当两家目标银行落在 ±win_radius 句窗内 (win_radius 取 config/panel.yaml::network_criteria.win_radius, 默认 1, 即目标句及其前后各一句) 被共同提及时连边。它比同篇判据更强调局部邻近 (排除跨段落的远距共现), 又比严格同句判据更宽容 (容许相邻句的语义延续), 因而重建出的年度网络稠密度介于二者之间。其构念意图是提供一个"适度邻近"的中间参照, 使三判据构成一条由松到紧的连续梯子, 从而更细致地探测度混合符号与量级对邻近半径的敏感性曲线 —— 若三点 (同篇/句窗/同句) 给出单调或方向一致的结论, 则网络形状证据对构造口径高度稳健。

【变体差分】
win_radius 键与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科硬过滤) 是两个互不联动的独立键, 切勿混淆或联动修改; 判据原语同为银行∧银行的分句定位系, 与 canonical/_sent 共享否定与短名排除事实源, 仅邻近半径不同。本列与 canonical、_sent 互为稳健性、不分主次, 三者各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。识别定位与家族一致: 一年一值、网络级广播、在 year FE 下被完全吸收, 只能作描述性证据、交互母项或样本分层依据, 不作主回归处理变量。同样地, _win1 后缀属网络构造判据空间, 与三轨文本后缀正交, 不得跨族混读。早期试跑 T=2 开发切片上因网络稀疏可能出现 NaN 或方差不稳, 属预期退化, 须以巨分量份额与连通分量数伴随诊断; 生产 T=19 全量语料下方给出可解读的年度度混合序列。

<!-- rendered-citations:begin -->
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Petersen, A. M. (2026). University digital media co-occurrence networks reveal structure and dynamics of brand visibility in the attention economy. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-025-04419-5
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Han, M., Kim, S. H., & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. Physical Review E, 70(6), 27721. https://doi.org/10.1103/PhysRevE.70.066111
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Ricca, F., & Scozzari, A. (2024). Portfolio optimization through a network approach: Network assortative mixing and portfolio diversification. European Journal of Operational Research. https://doi.org/10.1016/j.ejor.2023.07.010
De Blasis, R., Galati, L., & Petroni, F. (2026). A network-based mixture transition distribution approach to portfolio optimization. Quantitative Finance. https://doi.org/10.1080/14697688.2026.2681609
Zhu, B., Hu, X., Deng, Y., & Lin, R. (2023). Systemic risk prevention policies targeting systemically important banks: Does clustering pattern matter? PLOS ONE. https://doi.org/10.1371/journal.pone.0284861
<!-- rendered-citations:end -->
