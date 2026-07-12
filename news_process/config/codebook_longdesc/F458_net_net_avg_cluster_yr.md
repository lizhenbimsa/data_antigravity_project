---
family_id: F458
columns:
- net_avg_cluster_yr
- net_avg_cluster_yr_sent
- net_avg_cluster_yr_win1
unit: 无量纲结构指标 (加权平均聚类系数, 取值域 [0,1])
formula: "net_avg_cluster_yr = average_clustering(G_year, weight='weight'); G_year = 年度银行∧银行共现加权网络 (节点=当年幸存 target_bank, 边权=同篇共现次数); 判据变体 {同篇 无后缀 / ±1句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality ; news_process/pipeline/panel/export.py
upstream:
- 40_article_bank_level (篇章级 docid + target_bank + 年份 + 内容)
citations:
- doi: 10.1093/rfs/hhae025
  type: journal
  authors: Hirshleifer, D., Peng, L., & Wang, Q.
  year: 2025
  title: "News diffusion in social networks and stock market reactions"
  venue: The Review of Financial Studies
  vol: 38
  issue: 3
  pages_or_artno: 883-937
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
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  issue: ""
  pages_or_artno: 103223
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
  issue: ""
  pages_or_artno: 603-629
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: 10.1103/PhysRevE.69.026113
  type: journal
  authors: Newman, M. E. J., & Girvan, M.
  year: 2004
  title: "Finding and evaluating community structure in networks"
  venue: Physical Review E
  vol: 69
  issue: 2
  pages_or_artno: 026113
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A.
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: 3747-3752
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是年度银行共现网络的整体抱团程度, 即在给定年份内, 由媒体报道的"同篇共现"关系所连成的银行关系网, 其局部三角闭合的稠密程度。核心列 net_avg_cluster_yr 是该网络的加权平均聚类系数 (weighted average clustering coefficient): 对网络中每一个银行节点, 先计算其邻居之间实际存在的加权三角闭合相对于所有可能三角的比例 (即该节点的局部聚类系数), 再对全部节点取算术平均, 得到一个落在 [0,1] 区间的无量纲标量。聚类系数越高, 说明"我的共现伙伴彼此之间也常常共现", 网络呈现出紧密的小团体 (clique) 结构; 聚类系数越低, 说明共现关系更接近星状或链状的松散连接。这一构念直接承袭 Watts 与 Strogatz (1998) 提出的聚类系数与小世界网络刻画, 是网络科学中衡量局部凝聚性 (local cohesion) 最经典的结构统计量之一。

数据来源上, 网络的节点与边并非来自任何外部的股权、董事联锁或同业拆借数据, 而是完全内生于本项目的新闻文本处理链路。上游是篇章级的银行归属数据 (40_article_bank_level 口径): 每一篇通过银行侧与金科侧双重判定 (both-verified) 的报道, 都携带一个文档标识 docid 与其命中的目标银行 target_bank。生产函数 network_spillover.py::compute_bank_network_centrality 按年份分组, 以 docid 为聚合键: 凡在同一篇 docid 内同时幸存 (即均通过 verification) 的银行, 其两两无序对 {A,B} 记一次共现, 邻接矩阵对称累加。由此得到的年度加权图 G_year 中, 节点是当年出现过的银行, 边权 weight 是两家银行在当年被同一篇报道并提的次数。net_avg_cluster_yr 即在此加权图上调用 average_clustering(G, weight='weight') 计算得到。之所以强调 docid 聚合而非旧口径的 co_mentioned_banks 展开, 是因为后者会把未通过验证的银行也拉进邻接, 产生 phantom 边; docid 主路径确保只有真正 both-verified 的银行进入网络, 幽灵边防线 (omni-g-net-spill-01) 由此闭合。

【方法学与计算】
聚类系数的加权化处理是本列区别于教科书无权版本的关键。无权聚类系数只问"邻居之间有没有边", 加权版本进一步问"这些三角边有多重", 使得高频共现构成的三角比低频偶发共现构成的三角贡献更大。加权网络结构测度的这一推广思路可追溯至 Barrat 等 (2004) 对复杂加权网络架构的系统刻画, 其核心洞见是: 在真实的信息与交互网络里, 边的强度携带了拓扑之外的重要信息, 忽略权重会抹平"骨干关系"与"偶发关系"的差异。在实现层, networkx 的加权 average_clustering 以三角三条边权的几何均值定义局部贡献并对最大边权归一, 从而把边权尺度的任意性消去, 返回一个可跨年可比的 [0,1] 标量。全部节点级与网络级指标 (共 33 个基名, SSOT = network_spillover.NETWORK_METRIC_BASES) 的加权中心度均统一采用 weight='weight' 口径计算, 避免同一张图上部分指标用权、部分不用权导致的口径分叉。

需要特别说明网络级 (net-level) 与节点级 (bank-level) 指标的层级差异。net_avg_cluster_yr 属于 export.py 分块中的 Part C 网络级控制变量: 它是对整张年度图求一个标量, 因此在同一年份内对所有银行取同一个值, 再广播 (broadcast) 到该年每一条 bank-year 面板行上。这一"年度广播"性质带来一个重要的计量后果: 在含年份固定效应 (year FE) 的回归里, 任何逐年常数、跨银行不变的网络级标量都会被年份虚拟变量完全吸收 (absorbed), 因而 net_avg_cluster_yr 无法作为年份内的横截面识别变量, 它的价值在于刻画整个共现网络逐年演化的宏观结构状态 (例如金融科技叙事从少数头部银行的孤立报道逐步演化为行业性抱团报道时, 年度聚类系数会系统性抬升), 用于描述性叙事、样本期结构性突变检验, 以及作为不含年份 FE 或采用连续时间趋势设定时的时变网络状态控制。这与逐银行取值、承载横截面识别力的节点级聚类系数 bank_clustering (Part A) 在语义上截然不同, 二者不可混用。

还需澄清几个易被误解的实现细节, 以免使用者对本列做出超出其构造能力的解读。其一, 边权的语义是"当年同一批 both-verified 银行被写进同一篇报道的次数", 而非任何情感、金额或强度加权; 因此聚类系数刻画的是纯粹的共现拓扑抱团, 与情感极性、报道倾向无关, 不应被解读为"抱团的银行受到更正面/更负面报道"。其二, 网络的节点全集在三判据下保持一致 (均为当年幸存 target_bank), 判据只影响边集稀疏度而不影响节点集, 因此三变体的聚类系数差异纯粹来自成边严格度而非样本框变动, 这保证了三者作为稳健性梯子的可比性。其三, 加权 average_clustering 对边权尺度做了归一, 故聚类系数在不同年份、不同报道体量之间可比, 不会因某年报道总量翻倍而机械抬升——这正是选择加权几何均值口径而非简单计数的方法学理由。其四, 孤立节点与单边对 (度数不足以构成任何三角) 的局部聚类系数按定义为零并计入平均, 因此在报道极稀、大量银行仅被孤立提及的年份, 平均聚类系数会被这些零值系统性拉低, 这是数值退化而非结构信号, 使用者须结合当年节点数与边数一并解读。

【方法学与计算续】
从网络演化的角度看, 年度平均聚类系数提供了一条刻画中国银行业金融科技叙事结构变迁的时间序列。在金融科技概念初兴、仅少数头部银行被媒体单独报道的早期年份, 共现网络接近松散的星状或若干孤立对, 聚类系数偏低; 随着监管政策、行业事件把越来越多银行卷入同一批报道 (例如某一年集中出现的行业性金融科技整改), 网络的三角闭合迅速增加, 聚类系数系统性抬升; 而当叙事再度分化、各银行走上差异化的金融科技路径时, 抱团可能回落。这种非单调的结构演化本身即是有价值的描述性事实, 也是把本列纳入结构性突变检验的动因。与之互补的模块度 net_modularity_yr (Newman 与 Girvan 2004 的社区结构口径, 经 Clauset-Newman-Moore 贪心检测) 从"网络是否可清晰划分为若干社区"的角度刻画同一张图, 聚类系数则从"局部三角是否闭合"的角度切入, 二者共同构成年度网络的多维结构画像, 但在含年份 FE 的回归里同样被吸收, 定位一致。

【文献定位】
把媒体共现网络当作银行间信息与关注溢出的载体, 与近年金融网络文献的主线高度契合。Hirshleifer、Peng 与 Wang (2025) 证明新闻在社会网络中的扩散会系统性地驱动股票市场反应, 说明"谁与谁被一起谈论"本身携带定价相关信息; Yu、Hu 与 Zhong (2024) 进一步表明金融网络中的中心度会通过信息扩散渠道影响资产定价。在公司金融层面, Grieser 等 (2022) 与 Leary 和 Roberts (2014) 记录了同群 (peer) 企业的网络效应如何塑造公司财务政策, 为把银行嵌入其共现关系网、以网络结构解释其行为提供了实证先例。在系统性风险维度, Jackson 与 Pernoud (2021) 的综述以及 Duarte 与 Eisenbach (2021) 对火线抛售溢出的量化, 说明金融机构间的网络拓扑 (尤其是抱团与集中程度) 是传染与共同风险暴露的结构基础——年度聚类系数正是刻画这种"抱团稠密度"的自然候选。就测度本体而言, Watts 与 Strogatz (1998) 奠定了聚类系数与小世界结构的概念地基, Barrat 等 (2004) 提供了加权推广, Newman 与 Girvan (2004) 的社区结构方法则从互补角度刻画同一张图的模块化程度, 与聚类系数共同构成年度网络的多维结构画像。Freeman (1978) 对中心性概念的澄清则提醒我们, 网络结构指标是一族而非单一, 聚类只是其中刻画局部凝聚的一支。Nezami 等 (2025) 对网络中心度与企业绩效的元分析在为"结构—绩效"关联提供总体证据的同时也警示效应异质性显著 (该元分析并不专门背书聚类系数这一具体测度), 提示本列宜作描述与稳健性佐证而非因果主锚。

还应把本家族置于本项目更宽的媒体—银行研究脉络中理解。项目的整体研究关切是中国银行业在金融科技冲击下的媒体叙事及其经济后果, 银行共现网络是这一叙事的关系维度: 当媒体把若干银行反复放进同一篇金融科技报道时, 它们在投资者认知中被归为同一叙事板块, 这种被建构的关联可能影响其融资成本、金融科技投入与同群模仿。You、Zhang 与 Zhang (2018) 记录了媒体"笔杆子的权力"如何被不同主体俘获, 提示媒体共现并非中性的信息映射而带有构造性; 在此背景下, 用聚类系数量化"叙事抱团"的年度演化, 为后续把网络位置与银行行为相连接提供了结构底座。需强调的是, 本家族只提供网络的整体结构描述 (net-level), 承载横截面识别与个体异质性的是节点级中心度与经纪角色列 (bank_ 与 gf_ 前缀); 二者分工明确, 不可越界互替。

【口径归属与嵌入无关性】
还须澄清本家族在整个项目度量体系中的一个易被忽视的归属问题, 以免使用者错误地为其寻找并不存在的孪生列。net_avg_cluster_yr 及其两个判据变体是纯拓扑结构测度, 其唯一输入是年度银行∧银行共现的加权邻接矩阵, 计算过程只涉及图论意义上的三角闭合统计, 与任何文本嵌入向量、语义相似度、余弦距离均无关。因此本家族属于非嵌入 carve-out, 明确不设 co-primary 双轨嵌入所要求的 _lg 孪生列——它既没有 canonical Qwen 4096 维轨, 也没有 text-embedding-3-large 3072 维轨, 更不受 co-primary 双轨 both-or-neither 列双射守卫的约束。这一点与项目中另一类同样带判据/后缀但本质是嵌入的测度 (如 bank_emb_sim_mean 系列) 形成鲜明对照: 后者随嵌入模型切换而须同步维护双轨 parity, 而本家族的三个判据变体在任何嵌入模型下都字节不变, 换嵌入时全族零误改。使用者若在 dta 中检索 net_avg_cluster_yr_lg 之类的列名, 会一无所获, 这是设计使然而非缺漏。与之对称的是, 本家族亦不进入情感 LLM 三家投票、BERT 三模型或政治词权重梯子等测度族——它是一条独立的结构稳健性梯子 (仅三判据一维), 与上述各族在概念空间上正交、不交叉、不合并。

【识别策略定位】
在因果推断框架下, 用网络结构解释结果变量绕不开 Manski (1993) 的反射问题 (reflection problem): 当个体行为既影响又被其所在群体的行为影响时, 内生同群效应、外生同群效应与关联效应难以分离识别。Bramoullé、Djebbari 与 Fortin (2009) 证明, 当网络并非完全传递 (即存在"朋友的朋友不是我的朋友"这类开放三元组) 时, 网络的高阶邻接结构可提供识别内生同群效应所需的排除性约束; Bramoullé 等 (2020) 的综述与 Boucher 等 (2024) 的一般化理论进一步系统化了这一识别逻辑。聚类系数在此扮演一个微妙角色: 它恰恰度量网络的传递性/闭合程度, 而闭合程度越高、开放三元组越少, 基于网络拓扑的工具变量式识别就越弱。因此本家族的定位是明确的——net_avg_cluster_yr 及其判据变体是网络结构的描述性刻画与稳健性梯子的一环, 而非同群效应因果识别的主处理变量; 真正承载识别的是本项目 IV 扩展中的留一同群均值、广义 Bartik 与媒体来源 house-style 暴露三引擎。把年度聚类作为识别锚会与年份 FE 共线并落入反射问题, 故刻意不这么用。

【与相邻测度的构念区分】
必须严格区分本列与三处易混测度。其一, 与节点级 bank_clustering 的区分: 后者逐银行取值、进入横截面识别, 前者是其年度均值的网络级广播标量, 两者共享底层局部聚类定义但层级与用途不同。其二, 与网络传递性 net_transitivity_yr 的区分: 平均聚类系数是"先算每个节点局部比例再取节点平均", 传递性是"全图闭合三元组占开放三元组的比例 (三倍三角形除以连通三元组)", 前者对低度数节点赋予与高度数节点等同的权重、易被大量叶节点抬高, 后者以三元组为分母、由高度数枢纽主导, 二者在偏斜度数分布下可显著背离, 因此并列而非互相替代。其三, 与整个"银行∧金科"三轨文本体系 (full/ctx/ss) 的判据后缀区分: 三轨后缀刻画的是银行与金融科技词的文本邻近口径, 而本家族的 _win1/_sent 后缀刻画的是银行与银行之间共现边的构造严格度, 两者是正交的概念空间, 后缀字面相似 (都涉及 sentence) 但语义完全不同, 因此 _sent/_win1 在标签中显式带 bank-bank 限定以与文本轨 _ss 的 same-sent 区分。codebook 的三处推断函数在匹配前必须先剥离判据后缀, 否则 sent 子串会被误归为情感测度。

【已知局限与稳健性梯子】
第一重局限是识别层面的: 如上所述, 年度网络级标量在年份 FE 下被吸收, 且聚类本身与反射问题纠缠, 故本列不承担因果识别。第二重是测度稳健性: 加权平均聚类系数属于对图结构非线性、依赖浮点特征分解邻接的一类量, 在 BLAS 多线程下存在极小的浮点非确定漂移 (与 bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 同属需在 golden 零漂移验证时按全名 drop 排除的网络列族), 因此 golden 快照对这些列不做逐位复现要求, 而以确定性种子 (PYTHONHASHSEED=0 且全 BLAS 线程钉 1) 下的受控重生为准。第三重也是本家族的核心方法学贡献: 网络构造判据敏感性。同一张年度共现图, 究竟以何种"邻近"判定两家银行成边, 存在口径选择的自由度——是只要出现在同一篇报道即算共现 (同篇, 无后缀 canonical, 现行生产口径), 还是要求两家银行出现在相距不超过一个句子的窗口内 (_win1, ±win_radius 句窗, win_radius 取 config/panel.yaml::network_criteria.win_radius 默认 1), 抑或要求严格出现在同一句内 (_sent)。判据越严, 边集越稀疏, 网络越松散, 聚类系数通常越低。本家族据此并排给出三个判据变体, 它们各自 just-identified、互为稳健性、不分主次, 用于证明结构结论不被"共现"这一构造选择所驱动。铁律: 三判据各自 just-identified 并排, 严禁把 net_avg_cluster_yr、net_avg_cluster_yr_win1、net_avg_cluster_yr_sent 三者混进同一个 over-identified Hansen J 检验 (这与三轨文本、co-primary 双轨嵌入、政治词权重梯子、per-model 稳健性同属并排稳健性而非过度识别工具集的铁律); 判据敏感性属规格稳健性并排, 镜像政治词权重与词典消融先例, 不设 FWER 模板 (跨模型 rwolf 先例仅覆盖同构念的替代 headline 测量, 本族不适用)。在开发期 T=2 的极小面板上, 由于每年报道极稀, 严格判据变体上的网络可能退化为几乎无边、聚类系数趋近于零或大量 NaN, 属预期退化; 生产 T=18 全语料下三判据方能展现有意义的分离。第四重局限涉及连通性与聚类系数的交互: 平均聚类系数并不区分网络是单一巨型连通分量还是碎裂为多个孤立小团, 一张由若干独立三角组成的碎裂网络与一张单一致密网络可能给出相近的聚类系数, 因此本列须与巨分量占比 net_giant_share_yr、连通分量数 net_n_components_yr、平均路径长度 net_avg_path_yr 联合解读, 单看聚类系数会遗漏"抱团是否互相连通"这一维度。第五重是与经典社会网络方法论的对接: Freeman (1978) 早已指出结构指标是一族互补而非可互替的量, 聚类只刻画局部凝聚, 中心性刻画节点重要性, 路径长度刻画全局可达性, 因此本项目刻意在同一张年度图上并列产出 33 个结构基名而非单一"网络得分", 使用者应按研究问题择取而非机械堆叠。综合而言, net_avg_cluster_yr 家族的价值定位是: 以最经典、最可比、最稳健 (三判据梯子) 的方式刻画年度银行共现网络的局部抱团稠密度, 服务于描述性叙事、结构性突变检验与稳健性佐证, 而把因果识别与横截面异质性让渡给专门的 IV 引擎与节点级测度。

## VAR: net_avg_cluster_yr

【变体差分】
本列是家族的 canonical 判据变体, 也是唯一的 core 列, 取"同篇共现"口径 (article, 无后缀)。其精确语义是: 只要两家银行 (均为 both-verified) 出现在同一篇 docid 的报道中, 即在年度图上为它们记一条边并累加边权, 不对二者在文内的句间距离做任何约束。这是三判据中最宽松的成边标准, 因而生成的年度共现网络边最稠密、连通性最强, 聚类系数在三变体中通常最高。它之所以被选为 canonical, 一是与本项目其余网络指标 (全部 33 基名的无后缀列) 的现行生产口径一致, 二是"同篇并提"最贴合媒体关注溢出的经济学直觉——被同一篇报道一起讨论, 本身就意味着两家银行在叙事上被投资者与记者归为一类, 无需苛求它们在同一句内相邻。

计算链路上, 本列取 average_clustering(G_year, weight='weight'), 其中 G_year 的边权是同篇共现次数的对称累加。net_avg_cluster_yr 落在 [0,1]: 值接近 1 表示当年银行的共现伙伴彼此高度互相共现, 网络呈现紧密抱团的板块化叙事 (例如某年金融科技监管风波把一批银行同时卷入同一批报道); 值接近 0 表示共现关系松散、缺乏三角闭合, 银行更多是被各自单独或成对提及。作为网络级标量, 它对同一年份内所有银行取同值并广播到每条 bank-year 行, 因此在含年份 FE 的设定下会被吸收, 其主用途是: 描述性地刻画共现网络逐年演化的宏观抱团程度、在结构性突变检验中作为年度网络状态量、以及在不含年份 FE 或采用时间趋势的设定中作为时变网络控制。

作为 core 列, 它承担家族的构念锚定职责: net_avg_cluster_yr_win1 与 net_avg_cluster_yr_sent 是它在更严成边判据下的稳健性孪生, 三者共享同一加权平均聚类系数定义与同一底层 docid 聚合逻辑, 仅在"两家银行相距多近才算共现"这一构造维度上分叉。三者各自 just-identified、互为稳健性、不分主次, 严禁混入同一个 over-identified Hansen J。相对于节点级 bank_clustering, 本列是后者的年度网络均值广播版本, 层级更高、不承载横截面识别; 相对于 net_transitivity_yr, 本列是节点平均口径而非三元组口径, 在偏斜度数分布下二者可显著背离。使用者在解释本列时应始终牢记其年度广播与 year-FE 吸收特性, 避免把它误当作银行层面的横截面处理变量, 亦不宜把它作为同群效应因果识别的主锚 (受 Manski 反射问题与聚类-传递性纠缠约束)。在开发期 T=2 面板上本列可能因报道稀疏而数值退化, 生产全样本下方具解释力。使用本列时还应注意, 由于它是加权几何均值口径而非无权计数, 少数极高频共现的银行对 (例如常年被并提的几家国有大行) 所构成的强三角会对年度均值有可观贡献, 但归一化处理确保这种贡献不会因单纯的报道体量膨胀而失真; 这也意味着本列对"抱团核心由谁构成"不敏感——它只回答"整体抱团有多紧", 至于具体是哪些银行构成抱团核心, 须转而查阅节点级 bank_clustering 与经纪角色 gf_ 系列列。综上, net_avg_cluster_yr 的恰当用法是: 作为年度共现网络凝聚度的宏观描述量、结构性突变与稳健性叙事的一环, 而非银行层面的横截面处理变量或同群效应因果识别主锚。

## VAR: net_avg_cluster_yr_sent

【变体差分】
本列是家族的严格同句判据变体 (_sent), 取三判据中最严的成边标准: 只有当两家 both-verified 银行出现在同一句子之内时, 才在年度共现图上为它们记边。判据原语走 docid 组内文本重扫——对每篇报道, 以 prepend_title 拼接标题与正文 (标题视为第 0 句, 镜像 stage 13 的 match_in_title 口径), 通过 core/text/entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 定位银行在各句的位置, 仅同句内的银行对成边; 节点全集仍与同篇口径一致 (当年幸存 target_bank), 但边集显著更稀疏。相比 canonical 的同篇口径, 严格同句要求"被写在同一句话里"这一更强的叙事绑定, 剔除了那些虽在同篇但分处不同段落、彼此语义关联较弱的银行对, 因此生成的网络更松散、平均聚类系数通常在三变体中最低。

本列与 canonical 列除成边判据外的一切计算逻辑完全相同 (同为加权 average_clustering、同为 docid 聚合、同为年度网络级广播标量、同样在 year FE 下被吸收), 它是 canonical 列的稳健性孪生而非独立构念: 其存在意义在于证明年度抱团结构的结论不被"同篇即共现"这一宽松构造所人为放大——若在最严的同句判据下结构性结论依然成立, 则对成边口径的选择具备稳健性。判据后缀 _sent 显式带 bank-bank 限定, 与银行∧金科文本轨的 same-sentence (_ss) 是正交概念空间, 严禁混淆。net_avg_cluster_yr、_win1、_sent 三者各自 just-identified、互为稳健性、不分主次, 严禁混进同一个 over-identified Hansen J (镜像三轨/双轨/权重梯子铁律)。在开发期 T=2 极稀面板上, 严格同句判据极易使年度网络退化为近乎无边, 导致本列趋零或 NaN, 属预期退化; 生产 T=18 全语料下方能与其余两判据展现有意义的分离。

## VAR: net_avg_cluster_yr_win1

【变体差分】
本列是家族的句窗判据变体 (_win1), 严格度介于同篇 (canonical) 与严格同句 (_sent) 之间: 当两家 both-verified 银行出现在相距不超过 win_radius 个句子的窗口内时成边, win_radius 取自 config/panel.yaml::network_criteria.win_radius (默认 1, 即 ±1 句窗)。判据原语同样走 docid 组内文本重扫, 以 prepend_title 拼接标题与正文并逐句定位银行位置, 仅落在 ±1 句窗内的银行对成边。相比严格同句, 句窗口径放宽到相邻句, 容纳了"上一句提 A、下一句提 B"这类紧邻但不同句的共现; 相比同篇口径, 它又排除了分处远段落的弱关联对。因此其生成网络的稠密度与平均聚类系数通常落在另外两个变体之间, 构成一条平滑的判据严格度梯子。

需要强调 win_radius 这一键与 stage 13 银行∧金科共现过滤所用的 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的不同配置键: 前者管网络构造判据 (银行∧银行成边), 后者管留篇硬过滤 (银行∧金科), 改动一个不会影响另一个, 使用者切勿混淆。除成边判据外, 本列与 canonical 列的一切计算 (加权 average_clustering、docid 聚合、年度网络级广播、year-FE 吸收) 完全一致, 是其稳健性孪生而非独立构念。判据后缀 _win1 显式带 bank-bank 限定, 与银行∧金科文本轨正交。net_avg_cluster_yr、_win1、_sent 三者各自 just-identified、互为稳健性、不分主次, 严禁混进同一个 over-identified Hansen J。在开发期 T=2 面板上句窗判据同样可能因报道稀疏而数值退化, 生产全样本下方具解释力。

<!-- rendered-citations:begin -->
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
<!-- rendered-citations:end -->
