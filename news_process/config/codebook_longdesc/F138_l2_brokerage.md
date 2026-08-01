---
family_id: F138
columns:
- brokerage_eigen_cent
- brokerage_fire_sale
unit: 网络结构指标 (无量纲; brokerage_eigen_cent 为连通分量内 L2 归一的特征向量中心度, brokerage_fire_sale 为中心度滞后项与行业负面冲击的乘积)
formula: "brokerage_eigen_cent_{i,t} = 年度媒体-银行加权二分图上银行节点 i 的特征向量中心度 (按连通分量分别做确定性幂迭代, max_iter=2000, tol=1e-06, weight=边报道篇数, 分量内 L2 归一; 节点数 < 3 的微小分量置 NaN); brokerage_fire_sale_{i,t} = brokerage_eigen_cent_{i,t-1} × industry_neg_shock_{i,t} (shock 为 canonical full 轨同期 LOO 行业负面比率均值)"
producer: pipeline/panel/network_brokerage.py::compute_brokerage_centrality / compute_fire_sale_interaction (panel runner 步骤 7h-brok / 7h-fire; 消费占位符登记于 papers/_common/derivative_replication.py)
upstream:
- 11_news_bank 篇章级 df_exploded (媒体(中文) / target_bank / year 三列, 供二分图建边)
- 41_panel_encode_aggregate (neg_count_full + n_articles_llm_valid, 供 industry_neg_shock 分子分母)
- compute_industry_neg_shock (同模块步骤 7h-neg 产 industry_neg_shock, 供 fire_sale 交乘因子)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1057/s41599-026-07085-3"
  type: "journal"
  authors: "Wei, W., Wang, Z., Wang, Y., & Song, Y."
  year: 2026
  title: "Transfer entropy, multidimensional multiple correlation network, and risk contagion of bank capital shortage"
  venue: "Humanities and Social Sciences Communications"
- doi: "10.1016/j.physa.2025.130838"
  type: "journal"
  authors: "Lei, J., Shen, P., & Li, Z."
  year: 2025
  title: "Multilayer bank-firm networks and financial risk contagion"
  venue: "Physica A: Statistical Mechanics and its Applications"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. (H.), & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: "103223"
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: "102163"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1111/jofi.13010
  type: journal
  authors: Duarte, F., & Eisenbach, T. M.
  year: 2021
  title: "Fire-sale spillovers and systemic risk"
  venue: The Journal of Finance
  vol: 76
  issue: 3
  pages_or_artno: 1251-1294
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: 171-202
- doi: 10.1080/15427951.2013.865686
  type: journal
  authors: Boldi, P., & Vigna, S.
  year: 2014
  title: "Axioms for centrality"
  venue: Internet Mathematics
  vol: 10
  issue: 3-4
  pages_or_artno: 222-262
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
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1103/PhysRevE.71.056103
  type: journal
  authors: Estrada, E., & Rodríguez-Velázquez, J. A.
  year: 2005
  title: "Subgraph centrality in complex networks"
  venue: Physical Review E
  vol: 71
  issue: 5
  pages_or_artno: "056103"
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: 243-269
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: 157-191
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
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
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: 1170-1182
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: Bonacich, P.
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: 113-120
- doi: "10.1016/j.jfs.2024.101231"
  title: "Modelling fire sale contagion across banks and non-banks"
  authors: "Caccioli, F., Ferrara, G., & Ramadiah, A."
  year: 2024
  venue: "Journal of Financial Stability"
  type: "journal"
- doi: "10.1057/s41283-026-00215-w"
  title: "Spillover exposure in North American banks: persistence, macroeconomic conditions, and network structure"
  authors: "Ogunsanya, A."
  year: 2026
  venue: "Risk Management"
  type: "journal"
new_dois:
- "10.1057/s41599-026-07085-3"
- "10.1016/j.physa.2025.130838"
- "10.1016/j.jfs.2024.101231"
- "10.1057/s41283-026-00215-w"
---

## CORE

该文用转移熵构建银行间多维多重相关网络并结合空间杜宾模型分解直接效应与网络溢出效应,研究银行资本短缺风险的传染路径,与本家族用媒体-银行网络中心度刻画信息传导与冲击放大的构念高度同构。 该文构建包含银团贷款、银企信贷、企业间贸易信用等五类连边的多层银行-企业网络并模拟外部冲击下的风险传染机制,为本家族网络位置放大行业负面冲击(fire sale 交乘项)的机制提供多层网络视角的补充证据。

【构念与来源】
本家族刻画的核心构念是银行在信息分发网络中的结构位置, 以及这一位置在行业性负面舆论冲击到来时的放大效应, 共含两个 core 列: brokerage_eigen_cent 是银行在年度媒体与银行二分图上的特征向量中心度, 操作化银行的信息枢纽地位; brokerage_fire_sale 是该中心度的滞后一期取值与当年行业负面冲击指数的交乘项, 操作化信息枢纽银行在全行业负面舆论压力下所承受的差异化冲击暴露。构念的直接学术原型是 Han, Kim 与 Nanda (2024) 在机构经纪网络上的研究, 该文以基金与券商之间的交易关系构造二分图, 证明处于网络枢纽位置的经纪商在市场压力时期承担了系统性的流动性提供角色, 网络位置本身构成一种可以定价、可以传导冲击的经济属性。本项目将其基金与券商的二分图架构移植到中文银行新闻语料上: 二分图的一侧节点集合是新闻媒体来源, 取自 11_news_bank 阶段解析出的篇章级中文媒体名称列; 另一侧节点集合是被报道银行, 即篇章级展开表的目标银行列; 一条边连接一家媒体与一家银行, 边权重等于该媒体在该年度报道该银行的文章篇数。在这一网络里, 银行端特征向量中心度高意味着该银行不仅被很多媒体报道, 而且被那些自身连接广泛、影响力大的媒体报道, 其经济含义是信息可见度更高、信息传播渠道更加异质与冗余、在信息中介链条中处于更接近枢纽的位置。这一从媒体网络位置到银行信息属性的推理链条在近年文献中有直接的同构证据: Xu (2024) 在金融新闻语料上构建财经记者的社会网络, 并以网络中心度解释报道语调的系统性偏向, 说明媒体侧网络结构确实塑造银行收到的新闻覆盖; Fang, Wang, Wang 与 Yuan (2024) 用中国银行业数据证明媒体情绪与存款稳定性及银行系统性风险显著相关, 为媒体舆论作为银行风险传导渠道提供了中国场景的经验支撑; Khan, Hasan 与 Anupam (2024) 则以硅谷银行挤兑事件为例, 展示了社交媒体信息在银行网络上引发多米诺式传染的现实机制。fire sale 一词的命名与机制来自 Duarte 与 Eisenbach (2021): 该文测度火灾甩卖溢出对系统性风险的贡献, 核心机制是处于网络中心位置的机构在系统性负面冲击下会经由资产负债表与信息渠道放大溢出损失; 本家族的交乘项把这一机制翻译到舆论空间, 检验的是信息枢纽银行是否在行业负面舆论冲击中承受不成比例的声誉与价值损失。构念层面还须交代 brokerage 一词的谱系: 社会学传统中 Gould 与 Fernandez (1989) 给出了经纪角色的形式化分类, 强调经纪是在原本不相连的主体之间充当中介; 本家族的 brokerage_eigen_cent 采用的是声望或影响力意义上的特征向量刻画而非严格的 Gould 与 Fernandez 角色计数, 列名前缀 brokerage 标记的是所属论文模块 brokerage_network 的构念域, 精确的算法语义以下节方法学描述为准。

【方法学与计算】
计算入口在 pipeline/panel/network_brokerage.py, 由 40_panel_export_main 面板 runner 以步骤 7h-brok 与 7h-fire 调用, 全程纯 CPU、无任何 LLM 或网络 API 开销。第一步逐年构建媒体与银行二分图: 对每个面板年份, 从篇章级展开表按媒体名称与目标银行分组计数得到边表, 媒体节点标记 bipartite 等于零, 银行节点标记 bipartite 等于一, 边权重为整数篇数; 建图后显式校验二分性, 校验失败直接抛错而非静默继续, 且该守卫刻意用显式 raise 而非裸 assert 以免优化模式下被剥离。媒体名称列缺失或该年无边时返回空图, 全图节点数不足三个的年份整年跳过。第二步在图上计算银行端特征向量中心度。特征向量中心度的定义源自 Bonacich (1972), 其思想是节点的重要性等于其邻居重要性的加权和, 即中心度向量是邻接矩阵主特征值对应的特征向量, 与网页排序算法同族; Bonacich (1987) 进一步把这一思想推广为带参数的权力中心度族。实现上有两处经过审计事故驱动的硬化, 均已固化为当前生产语义。其一是按连通分量分别计算: 早期实现曾在非连通图上整体做幂迭代, 迭代收敛到主分量的特征向量, 非主分量节点得到的数值只是随迭代步数指数衰减的数值残渣, 同构位置在不同年份间可以相差悬殊的数量级, 不具备任何网络含义; 现行实现遍历连通分量, 节点数达到门槛值三的分量才在其子图上单独计算, 中心度在分量内做 L2 归一, 孤立点与微小分量的银行不赋值, 面板左连接后自然为缺失。其二是确定性迭代路径: 曾经的备选实现走数值特征分解, 底层稀疏特征求解器不固定初始向量, 同一张图同一进程重算即不能逐位复现, 属于潜伏的非确定性来源, 该路径已整体删除, 现行实现统一使用均匀初始向量的纯迭代法, 最大迭代两千步、收敛容差百万分之一、以边报道篇数为权重, 连通图作为单分量与非连通图共用同一代码路径, 跨运行逐位可复现; 个别极端退化分量若幂迭代不收敛, 该分量以度中心度兜底并写入最高级别日志供事后排查, 这一兜底与特征向量构念不同, 属于显式披露的降级而非静默替换。加权处理上, 特征向量中心度天然消费边权, 与 Opsahl, Agneessens 与 Skvoretz (2010) 强调的加权网络中心度应同时反映连接数量与连接强度的主张一致; 同模块另产的五个二分图原生中心度因上游算法接口约束是无权拓扑量, 两族互补, 详见构念区分节。第三步构造火灾甩卖交乘项: 面板先按银行与年份排序, 组内平移取得每家银行上一年的 brokerage_eigen_cent, 再与当年 canonical 轨的 industry_neg_shock 相乘, 首年观测因无上一期自动缺失。行业负面冲击指数本身由同模块步骤 7h-neg 生产, 属另一家族, 但其口径决定交乘项语义故在此交代: 它是留一均值, 即银行 i 在年份 t 的取值等于同年除自身外全部有效银行的负面报道比率的均值, 分子是 LLM 三家投票判定为负面的文章数, 分母是 LLM 有效判定篇数, 单家银行有效篇数低于五篇时该银行比率置缺失以防单篇极值独家设定全行业水平; 分母口径与全仓留篇门控一致, 即一篇文章是否计入银行金科报道宇宙只看 full 轨 LLM 验证结果, 这是 full-only 门控口径, ctx 与 ss 轨是 conditional-on-full 的测度轨。留一设计的动机来自 Manski (1993) 的反射问题: 若直接用含自身的行业均值, 银行自身的负面新闻会同时进入因变量与解释变量形成机械相关, 留一排除自身消除了这一机械性自相关; 但必须同样明确, 同期留一并不解决反射问题的同时性内核, 同年同行的结果仍由共同冲击联合决定, 要将其用作处理变量或工具须滞后一期或另行工具化, 这正是交乘项刻意取中心度滞后一期的原因之一。

【文献定位】
方法学谱系上, Freeman (1978) 是中心度概念的厘清母锚, 界定了度、介数、接近三族中心度各自回答的问题; Bonacich (1972, 1987) 确立了特征向量与权力中心度传统, 本家族主列即属此族; Boldi 与 Vigna (2014) 从公理化视角比较各类中心度对基本性质的满足情况, 为选择特征向量族而非其它族提供了规范性参照; Newman (2005) 的随机游走介数与 Estrada 及 Rodríguez-Velázquez (2005) 的子图中心度代表了两条本家族未采用但常被审稿人问及的替代路线, 前者放松了信息只沿最短路径流动的假设, 后者以闭合游走谱刻画节点参与度, 两者与特征向量中心度的相关性与分歧是稳健性讨论的常规素材。二分图专用方法上, Faust (1997) 系统讨论了隶属网络上中心度的定义与解释, Borgatti 与 Everett (1997) 给出双模数据网络分析的操作规范, 两文共同支撑本家族坚持在二分图原生结构上计算而不做单模投影的选择, 因为投影会丢失媒体侧的异质性信息。应用文献上, Han, Kim 与 Nanda (2024) 是构念直接来源; Yu, Hu 与 Zhong (2024) 证明网络中心度经由信息扩散渠道进入资产定价, Xu 与 Zhao (2024) 证明金融网络节点中心度对资产价格预测有增量信息, 两文共同支撑中心度作为信息可见度代理的外部效度; Nezami, Chisam 与 Palmatier (2025) 对网络中心度与企业绩效关系做了元分析, 提示该关系的方向与强度存在情境依赖, 为解释系数符号提供了先验分布; Li, Yuan, Zhu, Emrouznejad, Hao 与 Jin (2026) 从文本风险披露中恢复金融网络结构, 与本项目从新闻文本构建网络的做法同属文本驱动金融网络前沿; Sadeghi 与 Feinstein (2024) 提出金融网络传染中心度的统计显著性检验框架, 提醒中心度排序本身携带抽样不确定性。系统性风险与冲击传导侧, Jackson 与 Pernoud (2021) 的综述确立了网络位置决定冲击暴露与放大这一总框架, Duarte 与 Eisenbach (2021) 提供火灾甩卖溢出的具体测度传统, 交乘项的机制解释锚定于此。识别方法侧, Manski (1993) 与 Bramoullé, Djebbari 与 Fortin (2009) 分别给出同伴效应识别的反射难题与网络结构化解方案, 是本家族识别披露的方法论底座。

【识别策略定位】
在 brokerage_network 论文模块的回归体系中, 本家族两列均不是主处理变量而是网络机制层的核心解释变量。derivative_replication 的占位符登记显示, 主中心度槽位由银行与银行共现图的介数中心度占据, brokerage_eigen_cent 登记为次级中心度对照槽与调节交乘槽, 即一方面作为信息枢纽的替代测度与介数经纪测度并排对照, 另一方面在调节规格中承担网络位置乘外部冲击的交互项构造角色; brokerage_fire_sale 则是 centrality-outcome 主题表的主题列, 直接检验网络位置与行业冲击的交互效应。识别上有三层披露必须逐条写明。第一层是反射与同时性: 依 Manski (1993), 同期留一均值只去机械自相关, 不构成外生变异来源, 同行结果与自身结果仍由共同冲击联合决定; 依 Bramoullé, Djebbari 与 Fortin (2009), 网络结构的非传递性可以恢复同伴效应识别, 但本家族的行业冲击是全行业留一而非局部网络加权, 不满足其排除条件, 因此项目口径明确要求将其作处理变量时须滞后一期或工具化。第二层是年固定效应下的精确共线: 同期留一均值在代数上是年内总和项与自身比率项的仿射组合, 年固定效应吸收总和项后, 剩余识别变异与银行自身负面比率在年内精确共线且符号翻转, 任何含年固定效应的规格中同期冲击水平项的系数实际上是自身比率效应的重标度, 因此含年固定效应的规格必须改用滞后一期的冲击变体作主效应; 交乘项本身因中心度滞后项跨银行变异而保留银行乘年份维度的识别变异, 不受这一完全共线约束, 但其主效应项的选择须遵循上述规则。第三层是网络位置自身的内生性: 媒体报道模式与银行基本面互为因果, 当年冲击可能改变当年报道结构进而改变当年中心度, 交乘项取中心度滞后一期正是为了切断这一同期反馈; 更强的因果主张需要借助模块内已铺设的工具变量族与外生政策冲击占位符, 本家族自身不主张排除性约束成立。第四层是测度选择的规范性辩护: 审稿人常质疑为何以特征向量族而非介数或子图族承载信息枢纽构念, 依 Boldi 与 Vigna (2014) 的公理化比较, 特征向量中心度满足节点重要性对邻居重要性的单调递归公理, 恰是信息可见度构念所需的性质, 即被重要媒体连接应比被同样多的边缘媒体连接得分更高; 而 Newman (2005) 的随机游走介数与 Estrada 及 Rodríguez-Velázquez (2005) 的子图中心度分别刻画流量桥接与游走参与, 与本构念错位, 因此测度选择本身不是自由度而是构念决定, 这一辩护须在方法附录中明确以堵住测度挑选内生性的质疑。第五层是估计量的抽样不确定性: 依 Sadeghi 与 Feinstein (2024), 从有限样本网络恢复的中心度排序携带非平凡的抽样噪声, 当交乘项进入主表时, 滞后中心度因子的排序误差会经由乘积传导, 因此涉及枢纽排序的关键结论应辅以排序自助或对中心度分箱后的稳健性对照, 而非把点估计的中心度值当作无误差回归元。

【与相邻测度的构念区分】
第一组区分是与同模块 WS-B 扩展的五个二分图原生中心度列族: 那五列在同一张媒体银行二分图上计算度、介数、接近、聚类与冗余, 其中二分图介数才是对 Gould 与 Fernandez (1989) 意义上桥接性经纪的直接操作化, 即银行是否桥接了原本互不相连的媒体渠道; 而 brokerage_eigen_cent 是声望或影响力测度, 度量的是与重要媒体相连的程度而非桥接稀缺通道的程度, 两者在构念上分别对应影响力与结构洞两条传统, 且五列因上游算法接口约束为无权拓扑量, 与消费边权的特征向量中心度形成加权与无权的互补对。还须补充五列族实现层各带的分量可比性守卫, 因为它们与本家族的微小分量门槛同属一条纪律: 接近中心度只在最大连通分量的子图上计算, 否则断连图上孤立结构的接近值会系统性高于连通主体造成排名倒挂; 冗余度只对媒体连接数不低于二的银行计算, 单渠道银行的邻域重叠无定义; 度中心度以当年媒体总数归一使其成为年内相对量, 便于年固定效应下解释。这三项守卫与本家族的微小分量置缺失表达的是同一判断, 即断连二分图上的位置量只有在限定可比范围之后才有解释力, 审计对照时应把两族的缺失模式放进同一框架核对, 而不是把缺失当作数据质量问题分别处置。第二组区分是与 46_network_spillovers 的银行与银行同质共现网络指标族: 那一族的图是银行节点之间因同篇或同句共现而连边的单模图, 携带同篇、窗口一句、严格同句三档构造判据变体, 三判据各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J; 本家族的图是媒体与银行的双模图, 节点集合、边语义与经济含义均不同, 银行在两张图上的中心度回答的是两个不同问题, 前者是同业信息网络中的位置, 后者是媒体分发网络中的位置, 二者并排恰好构成网络机制的双通道证据。第三组区分是与行业负面冲击指数家族: industry_neg_shock 是交乘项的一个因子但自成家族, 它有 full、ctx、ss 三条情感轨变体, 分子分母严格逐轨、三轨互为稳健性不分主次、各自 just-identified 并排、禁混同一 over-identified Hansen J; 而 brokerage_fire_sale 刻意只消费 canonical 轨冲击, 判据是范围控制而非遗漏, 因为交乘的另一因子 brokerage_eigen_cent 本身是轨道无关量, 按报道篇数建边、不消费任何情感列, 为交乘项造三轨孪生不会带来新的识别变异却会放大列爆炸。第四组区分是与嵌入依赖列族: 本家族两列均为纯图论量, 属非嵌入 carve-out, 不存在 canonical 与 _lg 的 co-primary 双轨孪生, 嵌入模型更换对本家族零影响; 全仓 co-primary 双轨口径中两嵌入轨各自 just-identified 并排、互为稳健性、严格列名双射的铁律适用于嵌入列族, 本家族因不消费嵌入而天然豁免, 但在同一回归中若同时使用本家族列与嵌入派生列, 仍须遵守各梯子不混入同一 over-identified Hansen J 的总纪律。第五组区分是加权与无权处理的构念后果: 依 Opsahl, Agneessens 与 Skvoretz (2010), 加权网络中心度应同时反映连接数量与连接强度, 本家族主列消费报道篇数边权正是落实这一主张, 因此它对被同一头部媒体密集报道的银行更敏感; 而同模块五列族因上游二分图算法接口只接受无权拓扑, 只反映连接的存在与否, 对报道强度不敏感, 两族并置时数量效应与强度效应被自然分离, 这一分离不是冗余而是构念解耦, 审计对照时应把加权与无权视为回答不同问题而非同一问题的两个精度档。第六组区分是与新闻覆盖裸计数列: 后者是年内报道篇数的简单加总, 度量数量; 本列度量渠道质量加权后的位置, 两列可同时入式以分离数量与位置两种效应, 依 Yu, Hu 与 Zhong (2024) 与 Xu 及 Zhao (2024) 的证据, 位置量携带独立于裸计数的信息扩散与定价信号, 故不可用裸计数替代本列, 亦不可将本列解读为报道量的单调变换。

【已知局限与稳健性梯子】
第一, 分量内归一导致中心度水平只在同一连通分量内可比, 跨分量比较只在是否处于大分量的意义上成立, 跨年比较亦受当年图结构影响, 回归中应以银行固定效应吸收持久性水平差异并侧重年内相对变异。第二, 微小分量与孤立点置缺失是刻意的构念保真选择, 代价是覆盖率随图的碎片化程度波动, 缺失并非随机, 样本选择与报道稀疏的小银行系统相关, 结论外推须谨慎; 早期试跑盘面年份深度极浅时交乘项可能因某年冲击整体为零而退化为零方差常量, 属预期退化而非缺陷, 生产全量语料下须复核。第三, 边权取原始报道篇数, 未按报道语调或篇幅加权, 中心度混合了正面与负面可见度; 与冲击指数交乘后部分恢复了负面维度, 但中心度自身的语调中性是解释时须交代的口径。第四, 媒体名称解析质量直接决定节点集合, 同一媒体的名称变体若未归并会稀释真实枢纽度, 该风险由上游预处理的媒体名称规范化控制。第五, 幂迭代不收敛分量的度中心度兜底是构念上的降级, 由最高级日志显式披露, 生产运行中应核查此类分量占比。第六, 本家族依赖图算法库, 该库缺席时中心度整体优雅跳过而非崩阶段, 面板中两列全缺席时应首先排查依赖安装而非上游数据; 与之相邻的另一条运行期防线是生产日志在交乘构造处显式报告滞后中心度与同期冲击两因子的配对相关诊断与零方差退化告警, 配对相关的判定刻意在两因子同时非缺失的配对完备子集上做零方差守卫, 因为全局有方差不代表配对子集有方差, 复核交乘项可用性时应以该诊断为第一入口。第七, 特征向量族的一个已知病态是局部化, 即在含高度节点的稀疏图上主特征向量可能过度集中于少数枢纽及其邻域, 使多数节点得分被压向零, 分量内 L2 归一虽消除了标度歧义却不消除这一集中形态, 因此本列的截面分布可能高度右偏, 回归中直接用水平值可能让少数枢纽银行主导识别, 建议以银行固定效应吸收持久枢纽地位并对分布右偏做稳健性对照或分箱检验, 这与 Sadeghi 与 Feinstein (2024) 强调的排序不确定性属同一类审慎。第八, 二分图坚持原生结构而不做单模投影是刻意选择, 依 Faust (1997) 与 Borgatti 及 Everett (1997), 投影到银行单模会把共享媒体的银行强行连边并丢失媒体侧异质性, 使中心度退化为共享媒体数量的函数, 本家族因此在双模图上直接计算; 代价是双模特征向量的解释不如单模直观, 须始终以媒体连接质量而非银行间关系来叙述系数, 这是解释纪律而非实现缺陷。稳健性梯子方面, 家族内部的梯子是中心度族替代: 二分图介数、度、接近、聚类、冗余五列与特征向量列互为稳健性、不分主次, 各自 just-identified 并排进入各自回归, 禁混进同一 over-identified Hansen J, 这一口径与全仓三轨、co-primary 双轨、词典消融、政治词权重、判据梯子的并排纪律完全同构; 家族外部的梯子是双模媒体网络与单模同业网络的双通道对照, 以及冲击因子侧的三轨与滞后变体替换。依 Sadeghi 与 Feinstein (2024) 的提醒, 中心度点估计的排序携带统计不确定性, 关键结论应辅以排序稳健性或自助推断; 依 Nezami, Chisam 与 Palmatier (2025) 的元分析证据, 中心度与绩效的关系强度存在情境异质性, 系数解释应避免超出银行业媒体网络这一具体情境。该文建模火灾甩卖传染如何在银行与非银行机构之间跨部门扩散, 为本家族 brokerage_fire_sale 交乘项的系统性冲击放大机制提供最新的跨机构证据, 引用格式为 Caccioli, Ferrara 与 Ramadiah (2024, Journal of Financial Stability)。该文用2005-2024年北美银行数据证明溢出暴露具有强持续性且与网络中心度正相关, 直接支持本家族以中心度滞后项刻画银行差异化冲击暴露的构造逻辑, 引用格式为 Ogunsanya (2026, Risk Management)。

## VAR: brokerage_eigen_cent

【变体差分】
本列是家族的 canonical 主列, 语义为银行 i 在年份 t 的媒体银行加权二分图上的特征向量中心度。与家族公式的对应关系是精确一比一: 逐年从篇章级展开表聚合媒体乘银行的报道篇数边表建二分图, 按连通分量分别做确定性幂迭代, 均匀初始向量、最大迭代两千步、收敛容差百万分之一、以报道篇数为边权, 分量内 L2 归一; 节点数不足三的微小分量与孤立点不赋值, 面板左连接后为缺失; 极端退化分量幂迭代不收敛时以度中心度兜底并写最高级日志。列的取值非负, 水平仅在同一连通分量内可比。轨道维度上本列是轨道无关量: 它只消费媒体名称、目标银行与年份三列, 按报道篇数建边, 不消费任何 full、ctx、ss 轨情感或文本列, 因此不存在三轨孪生, 这一点与行业负面冲击指数的三轨族形成鲜明对照; 模型维度上本列不依赖任何 LLM、词典或 BERT 情感输出, 与 per-model 梯子无关; 嵌入维度上本列是纯图论量, 属非嵌入 carve-out, 无 _lg 双轨孪生, 更换嵌入模型对本列零影响。滞后维度上本列是同期量, 无内建滞后; 其滞后一期形态不单独成列, 而是在交乘列 brokerage_fire_sale 内部即时构造后丢弃。阈值与判据维度上, 本列携带一个微小分量门槛判据, 门槛取三个节点, 语义是一媒体加两银行的最小可比结构, 该门槛是固定生产口径而非可调梯子, 与银行同业网络指标族的三档共现判据梯子无关, 后者的判据后缀不出现在本列列名中。与同模块五个二分图原生中心度列的差分在于: 本列消费边权、走影响力构念, 依 Bonacich (1972) 的特征向量传统度量与重要媒体相连的程度; 五列族走无权拓扑构念, 其中介数列才直接操作化桥接性经纪, 两族并排互为稳健性、不分主次, 各自 just-identified 进入各自规格, 禁混进同一 over-identified Hansen J。回归使用上, 本列在 brokerage_network 模块登记为次级中心度对照槽与调节交乘槽, 常规用法是作信息可见度代理进入含银行固定效应的规格, 或以滞后形态进入交互规格; 依 Xu (2024) 与 Yu, Hu 与 Zhong (2024) 的证据, 高中心度对应更强的信息扩散能力, 系数解释应锚定信息渠道而非直接的资产负债表渠道。确定性口径上, 本列走纯迭代路径, 无稀疏特征求解器的随机初值问题, 跨运行逐位可复现, 不在全仓已知的 BLAS 浮点漂移网络列清单之内。分母与门控口径上还须交代一点边界: 本列建边只数报道篇数, 篇章宇宙来自上游共现硬过滤与留篇门控之后的银行金科报道集合, 留篇判定遵循 full-only 口径, 即一篇文章是否进入宇宙只看 full 轨 LLM 验证结果; 因此本列虽然轨道无关, 其样本框仍与全仓 n_articles 分母同源, 门控口径变更会经由篇章宇宙间接改变图的边权与节点集合, 这是复现审计时容易漏查的隐式依赖。解释直觉可用一句白话概括: 被十家小报各报一篇, 不如被一家同时连接着全行业的头部财经媒体报一篇, 本列给后者更高的分数, 因为它度量的是渠道质量加权后的可见度而非裸报道量; 裸报道量另有新闻覆盖计数列承载, 两者在回归中可同时入式以分离数量与位置两种效应。

## VAR: brokerage_fire_sale

【变体差分】
本列是家族的交乘派生列, 语义为银行 i 上一年的信息枢纽地位与当年行业负面舆论冲击的乘积, 即 brokerage_eigen_cent 滞后一期乘 industry_neg_shock 同期。与 canonical 列的差分有五个维度。滞后维度: 中心度因子取 t 减一期, 这是刻意的识别设计而非数据约束, 目的是切断当年冲击改变当年报道结构进而改变当年中心度的同期反馈回路; 实现上面板先按银行与年份排序再组内平移, 保证滞后语义正确, 每家银行的首个观测年自动缺失。轨道维度: 冲击因子刻意只取 canonical 无后缀轨, 不为 ctx 与 ss 轨造交乘孪生, 判据是范围控制而非遗漏, 因为中心度因子本身轨道无关, 三轨孪生不增加独立识别变异; 冲击家族自身的三轨互为稳健性、不分主次、各自 just-identified 并排、禁混同一 over-identified Hansen J 的口径由该家族文档承载, 本列不参与该梯子。缺失传播维度: 本列继承两个因子的缺失并集, 中心度滞后项缺失于首年、微小分量年与建图失败年, 冲击项缺失于有效篇数不足五篇且无有效同行的银行年, 因此本列覆盖率恒不高于两因子各自覆盖率, 解释样本构成时须同时交代两条缺失来源。识别维度: 交乘项因滞后中心度跨银行变异而保留银行乘年份的识别变异, 不受同期冲击项在年固定效应下与自身负面比率精确共线这一约束的直接影响, 但规格书写有硬规则, 即含年固定效应时冲击主效应必须用滞后一期变体而非同期水平项, 无年固定效应的描述性规格才允许同期主效应入式; 交互规格还应同时报告两主效应分量的相关结构以防交互系数误读。构念维度: 本列的机制锚是 Duarte 与 Eisenbach (2021) 的火灾甩卖溢出传统与 Jackson 及 Pernoud (2021) 综述的网络位置放大冲击框架, 预期符号为正, 即信息枢纽银行在行业负面舆论冲击下遭受更大的声誉与价值损失, 对应 Han, Kim 与 Nanda (2024) 中枢纽机构在压力期暴露上升的发现在舆论空间的对偶; 若估出负号则指向枢纽位置的信息缓冲解释, 即渠道冗余反而稀释单一负面叙事的冲击, 两种解释的甄别依赖结果变量的选取与机制检验。早期试跑盘面年份深度极浅时, 某年冲击可能整体为零使本列退化为零方差常量并被共线性剔除, 生产日志对此有显式告警, 属预期退化; 生产全量语料下应复核其变异充足后再纳入主表。与相邻交乘构造的差分也值得点明: 全仓网络溢出族中存在以银行同业图权重矩阵加权的同行语调滞后项, 那一族的交乘对象是同业网络位置与同行情感, 回答的是同业传染问题; 本列的交乘对象是媒体网络位置与全行业冲击, 回答的是信息放大问题, 两者机制不同、图不同、并排使用时各自 just-identified 进入各自规格, 同样禁混进同一 over-identified Hansen J。量纲上本列是两个无量纲量的乘积, 自身无自然单位, 系数大小不宜直接跨样本比较, 报告时建议对两因子先做标准化再交乘或在表注中给出因子的分布刻度; 由于中心度分量内归一的水平可比性限制同样传导到本列, 主表规格应含银行固定效应以吸收持久性水平差异, 让识别落在年内相对变异与跨期冲击变异的交互上。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Wei, W., Wang, Z., Wang, Y., & Song, Y. (2026). Transfer entropy, multidimensional multiple correlation network, and risk contagion of bank capital shortage. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-026-07085-3
Lei, J., Shen, P., & Li, Z. (2025). Multilayer bank-firm networks and financial risk contagion. Physica A: Statistical Mechanics and its Applications. https://doi.org/10.1016/j.physa.2025.130838
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 056103. https://doi.org/10.1103/PhysRevE.71.056103
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Caccioli, F., Ferrara, G., & Ramadiah, A. (2024). Modelling fire sale contagion across banks and non-banks. Journal of Financial Stability. https://doi.org/10.1016/j.jfs.2024.101231
Ogunsanya, A. (2026). Spillover exposure in North American banks: persistence, macroeconomic conditions, and network structure. Risk Management. https://doi.org/10.1057/s41283-026-00215-w
<!-- rendered-citations:end -->
