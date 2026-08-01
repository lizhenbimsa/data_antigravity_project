---
family_id: F081
columns:
- bank_ci
- bank_ci_sent
- bank_ci_win1
unit: "无量纲结构指标 (约束逆 = 1/Burt 网络约束); 正值、右偏、无固定上界; 节点度 < 2 或约束不可定义时为缺失"
formula: "bank_ci = 1 / bank_constraint (当 bank_constraint 有定义且 > 0, 否则 NaN); bank_constraint = networkx.constraint(G, weight='weight') 的 Burt (1992) 加权聚合约束, 节点度 < 2 → NaN; G = 年度银行∧银行共现网络 (无向, 边权 = 年内共现次数); 判据变体 {同篇 (无后缀 canonical) / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: "news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (面板 runner 步骤 7h-cent; 33 指标基名 SSOT = NETWORK_METRIC_BASES; codebook 条目 pipeline/panel/codebook.py)"
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
- doi: 10.1371/journal.pone.0327421
  type: journal
  authors: Amancio, D. R., Machicao, J., & Quispe, L. V. C.
  year: 2025
  title: "Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis"
  venue: PLOS ONE
  vol: 20
  issue: 7
  pages_or_artno: e0327421
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
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
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
  pages_or_artno: "2404.14337"
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.48550/arXiv.2308.04276
  type: arxiv
  authors: Hoshino, T.
  year: 2023
  title: "Causal interpretation of linear social interaction models with endogenous networks"
  venue: arXiv
  pages_or_artno: "2308.04276"
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: "76"
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: 171-202
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1371/journal.pone.0017994
  type: journal
  authors: Tumminello, M., Miccichè, S., Lillo, F., Piilo, J., & Mantegna, R. N.
  year: 2011
  title: "Statistically validated networks in bipartite complex systems"
  venue: PLoS ONE
  vol: 6
  issue: 3
  pages_or_artno: e17994
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
- doi: 10.1016/j.socnet.2007.04.006
  type: journal
  authors: Latapy, M., Magnien, C., & Del Vecchio, N.
  year: 2008
  title: "Basic notions for the analysis of large two-mode networks"
  venue: Social Networks
  vol: 30
  issue: 1
  pages_or_artno: 31-48
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
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
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: 157-191
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: 243-269
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
- doi: 10.1016/0378-8733(83)90028-X
  type: journal
  authors: Seidman, S. B.
  year: 1983
  title: "Network structure and minimum degree"
  venue: Social Networks
  vol: 5
  issue: 3
  pages_or_artno: 269-287
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: "10.1287/stsc.2024.0297"
  type: journal
  authors: "Johnson, J. C., & Sasson, A."
  year: 2026
  title: "Reassessing Constraint's Meaning: A Framework for Reinterpreting Structural Holes' Findings"
  venue: "Strategy Science"
- doi: "10.1002/smj.3538"
  type: journal
  authors: "Shipilov, A., Li, S. X., Bothner, M. S., & Truong, N."
  year: 2023
  title: "Network advantage: Uncontested structural holes and organizational performance in market crises"
  venue: "Strategic Management Journal"
- doi: "10.1007/s41060-024-00516-x"
  type: journal
  authors: "Miori, D., & Petrov, C."
  year: 2024
  title: "Narratives from GPT-derived networks of news and a link to financial markets dislocations"
  venue: "International Journal of Data Science and Analytics"
new_dois:
  - "10.1287/stsc.2024.0297"
  - "10.1002/smj.3538"
  - "10.1007/s41060-024-00516-x"
---

## CORE

【构念与来源】
本家族 F081 (家族键 net_bank_ci) 是银行共现网络结构指标族中刻画"结构洞与经纪优势"的一支, 共三列: bank_ci (家族 canonical, core 列, 同篇共现判据、无后缀)、bank_ci_sent (严格同句判据) 与 bank_ci_win1 (正负一句窗判据)。三列的构念内核同一, 度量的都是目标银行在年度"银行∧银行"新闻共现网络中的约束逆 (constraint inverse), 即 Burt 结构洞理论下网络约束 (network constraint) 的倒数。约束衡量一个节点的社会资本被其邻居"锁死"的程度: 当一家银行的共现伙伴数目少、彼此又高度互连、且注意力高度集中于个别伙伴时, 该节点的约束高, 意味着它嵌在一个封闭而冗余的小圈子里, 缺乏跨越结构洞的经纪机会; 反之, 当共现伙伴众多、彼此互不相识 (即伙伴之间存在大量结构洞) 时, 约束低, 该节点占据了可以中介非冗余信息的经纪位置。约束逆把这一关系翻转为直觉一致的正向刻度: bank_ci 越高, 约束越低, 结构洞越多, 该银行在共现网络中的经纪优势与信息中介潜力越大。取逆是本项目刻意的构念取向, 让"高值等于优势"以便回归系数符号解读与结构洞理论方向一致, 而不必沿用 networkx 原生输出的约束那种"高值等于劣势"的反直觉刻度。

结构洞理论的经典命题是低约束、跨结构洞的经纪位置与个体的信息优势和创新产出正相关。Burt (2004) 在企业内部经理网络上系统论证了处于结构洞两端的经纪者更早接触到非冗余想法、其提案被评为更有价值, 这是 bank_ci 构念方向的直接理论锚: 本列把这一"经纪即优势"的逻辑移植到银行的媒体共现网络上, 用约束逆刻画每家银行占据结构洞、跨群中介的相对位置。须强调的是, 本列度量的不是资本纽带或股权关联, 而是媒体报道共现意义上的关系嵌入——两家银行在同一篇 (或同一句) 财经报道中被并列提及, 构成一条共现边; 这种共现网络本质上是一个由"文章—银行"隶属关系投影而来的一模网络 (one-mode projection)。仿射/隶属网络的中心度测量传统 (Faust, 1997) 与二模数据的网络分析框架 (Borgatti & Everett, 1997; 大规模二模网络的基本分析概念见 Latapy 等, 2008) 为这种投影提供了方法学依据, 而共现网络作为一种统计对象的构造与可靠性近年在词共现网络 (Amancio 等, 2025)、二模投影的元验证 (Cimini 等, 2022) 与二部复杂系统中统计显著网络的甄别 (Tumminello 等, 2011) 中被进一步刻画——这些工作共同提醒: 由投影得到的共现边并非都等价, 部分边可能只是高活跃度节点的统计假象, 故本管道对本家族测度一律并排三判据而非独取一种。中心度构念本身的概念澄清可回溯到 Freeman (1978): 不同中心度回答"重要"的不同侧面, 而约束逆专门回答"这家银行的邻居之间是否互相认识"这一结构洞侧面, 与度、介数、特征向量等中心度正交而互补。

在金融网络的语境里, 以网络结构位置解释银行行为与定价已积累相当证据: 银行所有权网络承载了银行借贷中的信息传递 (Gao 等, 2022), 金融网络的系统性风险与连通结构密不可分 (Jackson & Pernoud, 2021), 节点中心度对资产价格预测与信息扩散有可测的解释力 (Yu 等, 2024; Xu & Zhao, 2024), 中心度与企业绩效的关联在跨领域元分析中被系统评估 (Nezami 等, 2025)。这些工作共同支撑了"银行在共现网络中的结构位置本身是一个有经济含义的变量"这一前提。以投资银行纵向数据检验2000年科网泡沫与2008年金融危机两次市场冲击下结构洞的绩效效应, 发现只有独占型 (而非共享型) 结构洞才在危机中带来经纪优势, 为 bank_ci 的经纪优势构念提供了银行业情境下的最新实证支持 (Shipilov, Li, Bothner, & Truong, 2023, Strategic Management Journal)。用 GPT 从新闻文本中抽取实体并按同文共现构建实体网络、计算图中心度以追踪市场叙事演化, 与市场脱序事件建立关联, 为本家族由媒体报道共现派生金融实体网络这一构造范式提供了新近的文本驱动网络方法学参照 (Miori & Petrov, 2024, International Journal of Data Science and Analytics)。与此同时, 由文本派生的金融网络已成为独立研究对象 (Li 等, 2026 从文本风险披露中还原金融网络结构与连通), 银行在社交媒体网络中的共提及甚至能刻画挤兑传染的多米诺路径 (Khan 等, 2024); 而由于本网络的边来自媒体报道, 记者社会网络自身的偏倚 (Xu, 2024) 提醒我们共现边是"谁与谁被一起写"的媒体产物, 解读时须与真实业务关联区分。

【方法学与计算】
上游输入是 df_exploded, 即 24_herd_decay.parquet 承载的 stage-21 verified 宇宙的篇章级展开帧, 含 docid、target_bank、year、内容、标题等列。该宇宙执行 full-only 留篇门控 (2026-06-29 裁定): 一篇文章是否算作"银行金融科技报道"只看 llm_verified_full 一个旗标, 因此本家族共现网络的节点全集就是全文经三家大模型投票核实的金融科技报道所提及的银行集合, 已剔除曾污染面板的假阳性文章。节点宇宙锚定这一 verified 集是本家族与其它测度共享的样本纪律, 而非孤立选择。

逐年计算分三步。第一步构建年度邻接矩阵。canonical 的同篇判据 (criterion='article') 走 both-verified 主路径: 在同一 docid 下, 该年幸存的 target_bank 集合内逐个无序对各加一权, 每篇文章每对恰记一次, 邻接对称。判据分轨路径 (win1/sent) 则在 docid 组内做句级重扫: 对每个多银行文章组, 取组首行正文并前置标题 (prepend_title, 标题作为第 0 句, 镜像 stage 13 的 match_in_title 口径), 调用 map_bank_sentence_positions 定位各银行别名的句位, 再由 bank_pairs_within_sentence_window 在给定句窗半径内产出银行对; win1 取 config/panel.yaml::network_criteria.win_radius (默认正负一句), sent 取半径零 (严格同句)。句级重扫复用与 stage 11/13 同源的否定 AC 与短名排除事实源 (禁裸 Aho-Corasick, 以防"涉农行业"误命中"农行"之类短名假阳性)。三判据的节点全集一致 (同为该年幸存银行), 只有边集逐级收紧: 同篇是最松的边, 句窗次之, 同句最严, 满足同篇边集包含句窗边集、句窗边集包含同句边集的嵌套关系。边权在三判据下都取年内共现次数 (每篇每对同权加一)。

第二步把邻接矩阵建成加权无向图 G (边权 weight 即共现次数), 并派生倒数权重图 G_inv 与最大连通分量 (供路径型指标使用, 本列不涉及)。加权网络的结构测量须以权重口径为准, 加权网络的拓扑架构与强度分布对结构量的影响在复杂加权网络文献中已有系统刻画 (Barrat 等, 2004), 而把度、路径等中心度推广到加权情形的一般化框架见 Opsahl 等 (2010)。第三步计算约束与约束逆。约束由 networkx.constraint(G, weight='weight') 给出, 是 Burt (1992) 的加权聚合约束: 对节点 i 的每个邻居 j, 记 p_ij 为 i 投入到 j 的关系比例 (按边权归一), 邻居 j 对 i 的约束贡献等于 (p_ij 加上 i 经由共同邻居 q 间接投向 j 的比例之和) 的平方, 节点约束是这些贡献之和; 直觉上, 邻居越少、越集中、越彼此互连, 约束越高。实现上, 节点度小于二的银行 (共现伙伴不足两家, 结构洞概念不可定义) 的约束一律置缺失。约束逆 bank_ci 则在约束有定义且严格为正时取其倒数, 否则置缺失。因此 bank_ci 缺失当且仅当该银行该年度小于二、或约束因图退化而不可定义。须特别指出, 本列的计算是纯组合拓扑运算, 确定性且零成本, 不落入受 BLAS 浮点漂移影响的三列非确定网络列 (聚类系数、电流介数、调和中心度), 跨次重建逐位可复现——这与家族内某些兄弟指标的可复现性状态不同, 是 bank_ci 作为 canonical core 列的一项良好性质。

约束的一个技术细节值得写清, 以便与相邻测度精确区分: networkx 输出的是聚合约束 (aggregate constraint), 即节点对其全部邻居的二元约束 (dyadic constraint) 之和, 而非单条二元约束。二元约束项衡量的是"邻居 j 对 i 的锁定"——它随 i 投入 j 的直接比例 p_ij 上升, 也随 i 与 j 之间的间接冗余路径 (经共同邻居 q) 上升, 平方使高冗余关系被非线性放大。因此约束高既可能来自邻居太少、投入太集中 (规模效应), 也可能来自邻居彼此高度互连 (闭合效应), 二者在聚合约束里被合并成一个标量; 约束逆 bank_ci 继承这一合并语义, 是对"结构自主性" (structural autonomy) 的单标量刻画, 而非分解出规模与闭合两成分。这一点决定了它与有效规模 (偏规模成分) 和自我网络密度 (偏闭合成分) 的构念不完全重合, 详见与相邻测度的区分段。权重进入 p_ij 的口径是"按边权归一的关系投入份额", 故大 N 报道带来的高共现次数会同时抬高相关银行对的边权与占比, 这也是下文超边敏感性局限的来源。

【文献定位】
在网络计量的测度谱系中, 本家族落在"结构洞与经纪"这一支, 与家族外的多支中心度构成分工。度与强度中心度回答"认识多少邻居、共现多密", 介数与电流介数回答"多少最短路径或电流必经此节点 (桥梁地位)", 特征向量与 Katz 回答"邻居本身重不重要", 而约束逆专门回答"邻居之间是否互相认识、我是否跨越了结构洞"。这一定位使 bank_ci 天然与经纪测量文献对话: 加权归一化的 Gould-Fernandez 经纪测度 (Zádor 等, 2022) 是把经纪从计数推广到加权网络的近期方法学进展, 与本管道同一生产函数产出的 gf 经纪角色列 (基于 Gould-Fernandez 1989 的分型经纪) 共同构成"经纪"这一构念的多个操作化侧面, 而约束逆提供的是不分型、基于自我网络封闭度的结构洞刻画。将 bank_ci 放进银行—媒体—金融网络的实证脉络中, 它既继承了金融网络结构解释力的一般证据 (Jackson & Pernoud, 2021; Yu 等, 2024; Nezami 等, 2025), 又以"由媒体共现文本派生"这一数据来源与文本金融网络的新兴范式 (Li 等, 2026; Amancio 等, 2025) 相衔接。须审慎的是, 中心度与绩效的元分析 (Nezami 等, 2025) 提醒不同中心度对结果的解释力异质且情境依赖, 本管道并不据此断言约束逆一定优于其它结构位置测度, 而是把它与家族内多支中心度并排提供、由稳健性检验裁断, 这也是共现网络作为统计对象须做可靠性核验 (Cimini 等, 2022) 的方法学纪律在测度选择层面的体现。方法学审慎的最新一层来自 Johnson 与 Sasson (2026, Strategy Science) 对约束测度本身的再评估: 该文用形式化、计算与实证方法重新审视 Burt 网络约束, 指出其主要操作化的其实是二元 (dyadic) 锁定机制而非三元结构洞构念本身, 为本家族 bank_ci (约束逆) 的构念解读边界提供了理论审慎依据, 提醒解读时不宜把约束逆的高低径直等同于三元结构洞多寡, 而应留意其背后二元关系集中度的成分。

【识别策略定位】
本家族三列均是节点级 (银行乘年份) 结构变量, 隶属 brokerage_network 论文脉络, 均不担任主处理变量。与网络级年度指标 (net_*_yr 一族, 按年广播、在年固定效应下被完全吸收而不可识别) 不同, 节点级的 bank_ci 在含年固定效应的面板中仍保有跨银行横截面变异、可识别, 这是它进入回归的前提, 也是它区别于同一生产函数产出的十个网络级 (net_*_yr) 汇总量的关键分界: 后者对全年所有银行取同一标量、在年虚拟变量下沦为常数, 前者逐银行取值、随结构位置变动。其识别定位有三: 其一, 作经纪优势协变量或调节变量——检验在同等注意力或情感处理水平下, 占据更多结构洞 (高 bank_ci) 的银行其结果是否系统不同, 从而刻画结构位置对处理效应的异质放大或衰减; 其二, 作机制变量——若主效应主要由高经纪位置银行驱动, 提示信息中介渠道在起作用; 其三, 进入描述统计与网络诊断表, 为审稿人提供网络构造透明度与样本框刻画。识别威胁须分层说明。共现网络的边与被报道对象的基本面互为因果 (一家银行因经营事件而频繁见报, 频繁见报又反过来塑造其在共现网络中的位置), 这使 bank_ci 与结果变量之间可能存在双向性; 网络型同伴效应更面临 Manski (1993) 反射问题所刻画的内生效应、外生 (情境) 效应与相关效应三者难分的联立困境, 简单地用邻居均值解释自身行为无法识别。文献给出的识别抓手是网络的局部不可传递性: Bramoullé 等 (2009) 证明当社会网络存在开放三元组 (我的邻居的邻居并非全是我的邻居) 时, 二阶而非一阶邻居的特征可充当工具、内生与情境效应得以分离识别。此后十余年网络同伴效应识别的进展与陷阱在 Bramoullé 等 (2020) 的综述中有系统梳理, 其核心告诫与本列直接相关: 基于网络结构的识别力量高度依赖网络本身外生这一维持假设, 而当网络由行为主体内生形成时, 结构工具的排他性约束即告可疑——媒体共现网络恰属后者 (边由报道决策生成, 报道决策又受银行基本面与事件驱动), 故本列进入识别链条时须把网络内生性列为第一顺位威胁而非脚注。这一识别逻辑恰与本列构念成镜像——网络约束正是三元组闭合程度的度量, 约束高意味着三元组高度闭合 (无结构洞、强可传递), 恰是 Bramoullé 识别失效的情形; 而 bank_ci 高 (约束低) 的银行嵌在富含开放三元组、结构洞密布的自我网络里, 正是同伴效应识别力量最强之处。因此 bank_ci 不仅是被识别的对象, 其取值本身还标示了同伴效应识别的可行区域, 这一双重身份是解读它时容易被忽略的一点。对内生网络下线性社会互动模型的因果解读, Hoshino (2023) 进一步给出网络形成内生时结构参数仍具因果含义的条件, 提醒把结构位置当外生调节须以网络形成机制在给定协变量下可忽略为前提, 否则调节系数会吸收网络—基本面共同决定的成分。据此, bank_ci 进入回归时按调节或中介框架处理 (Grieser 等, 2022 以空间计量加网络结构识别公司金融政策中的网络效应, 提供了同类实证范式), 不当作外生处理直接作因果解读, 必要时配合面板层已备的严格滞后与固定效应工具箱以缓解同期反向因果。口径铁律必须复述: 同篇、句窗、同句三个共现判据各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同判据的 bank_ci 变体混进同一个 over-identified 方程去跑 Hansen J; 且判据后缀 (无后缀/_win1/_sent, 银行∧银行邻接口径) 与三轨文本后缀 (_full/_ctx/_ss, 银行∧金科文本口径) 是两个正交概念空间, 严禁在同一过度识别方程内交叉混用。本家族是轨道无关 (track-agnostic) 的元数据式测度, 不产 _full/_ctx/_ss 三轨孪生; 其节点宇宙锚定 stage-21 full-only 留篇门控 (2026-06-29 裁定: 一篇是否算作银行金融科技报道只看 llm_verified_full 单旗标) 下的 verified 银行集, 因此 ss 轨"无银行∧金科同句共现即回退全文正文"的回退语义对本家族不产生列, 但该 full-only 分母口径在解读兄弟情感/强度测度时仍须知, 不可把三轨文本的回退语义张冠李戴到本家族的银行∧银行 _sent 判据上。

【与相邻测度的构念区分】
最易混淆的五组近邻须逐一厘清, 且须落到实现细节层面才不致误用。第一, bank_ci 对 bank_constraint (家族 F086): 二者是严格互为倒数的关系 (bank_ci 等于一除以 bank_constraint, 仅当约束有定义且严格为正时取值), 携带完全相同的信息、只是刻度方向相反, 因此它们高度共线、近乎完美负相关, 绝不可作为两个独立解释变量并列进同一回归——那是把同一测度用两种方向重复计入, 会造成完全共线或严重多重共线。二者并存的唯一意义是让研究者按解读方向 (要"约束/被邻居锁定"还是要"经纪优势/结构自主") 二选一取用; 二者的缺失格完全一致 (同为度小于二或图退化), 故不存在一列可补另一列的情形。第二, bank_ci 对 bank_effective_size (有效规模, 家族 F090): 二者同属结构洞谱系, 但有效规模数的是"非冗余邻居的当量数目" (邻居数扣除平均冗余), 侧重规模成分; 约束逆则综合伙伴数目、投入集中度与直接间接互连三重信息, 是结构自主性的单标量合并刻画。二者相关但不等价, 更有一处实现级差异不可忽视: 有效规模的缺失守卫是节点度等于零才置缺失, 而约束逆的缺失守卫是度小于二即置缺失, 因此恰好一个共现伙伴 (度等于一) 的银行有有效规模取值却无 bank_ci——两列有效样本框并不重合, 并排作稳健性时须知这一非对称缺失, 不可默认二者同格。第三, bank_ci 对 bank_ego_density (自我网络密度, 家族 F091): 自我网络密度算的是邻居之间实际边占可能边的比例, 与约束逆同刻画"闭合", 但有两点本质差异——其一, 密度是无权计算 (实现上仅数邻居对之间是否存在边、不看边权), 而约束逆经由按边权归一的关系投入份额 p_ij 进入、是加权量, 故在共现次数悬殊的年份二者可显著背离; 其二, 密度只含闭合成分、不含规模与集中度成分, 而约束逆把三者合并, 语义更综合。第四, bank_ci 对 bank_between_cent 与 bank_cfbetween_cent (介数/电流介数中心度, 家族 F079/F080): 后二者是全局路径型桥梁测度, 且在实现上跑于倒数权重图 G_inv (把强共现视作短距离) 之上——介数的随机对象是全网最短路径、电流介数 (基于随机游走的介数, Newman 2005) 的随机对象是全网电流, 二者刻画"多少流量必经此节点"的桥梁地位; 而约束逆跑于原始权重图 G、随机对象是节点直接邻域的封闭度, 是局部自我网络的结构洞测度。二者都沾"经纪/桥梁"意味但构念层级 (全局对局部) 与底图 (倒数图对原图) 均不同, 不可互替; 且电流介数属受 BLAS 浮点漂移影响的非确定网络列, 而约束逆是确定性纯拓扑量, 二者的可复现性状态亦不同。第五, bank_ci 对 gf 经纪角色一族 (gf_coordinator/gf_gatekeeper_rep/gf_liaison 等, 家族 F321 等): 后者是需要外生群组归属 (如银行类型分组) 的分型经纪测度, 依 Gould 与 Fernandez (1989) 的中介结构分型区分协调者、守门人、联络人等角色 (加权归一化推广见 Zádor 等, 2022), 而 bank_ci 是不分型、不需群组信息的自我网络结构洞刻画; 二者是"经纪"构念下的不同操作化, 并排提供互补侧面而非互替。以上五组区分共同界定了 bank_ci 在网络测度谱系中的精确坐标——局部而非全局、加权而非无权、原图而非倒数图、不分型而非分型、合并规模与闭合而非单成分——正是这一坐标使它与家族内外的近邻各守其位、不可彼此替代。

【已知局限与稳健性梯子】
局限一, 缺失与稀疏: 节点度小于二即置缺失 (少于两个共现伙伴时结构洞概念不可定义), 在共现稀薄的早年或浅样本上会产生大量缺失格; 此度阈值本身呼应最小度与网络凝聚子结构的经典讨论 (Seidman, 1983 论最小度与 k-core 对子群密度的刻画), 但它也意味着 bank_ci 的有效样本系统性偏向共现活跃、见报密集的大中型银行, 解读总体结论时须留意这一选择性——缺失并非随机, 而是与银行规模、媒体曝光相关。早期试跑盘 T 等于二深度下格间波动大、判据分轨的 win1/sent 边集尤其稀疏, 属预期退化, 本家族的设计功效须在生产 T 等于十八语料上方能充分释放。局限二, 分布形状: bank_ci 等于约束的倒数, 当银行处于极度开放的自我网络 (约束趋近于零) 时约束逆会趋向很大, 分布重右偏且无固定上界, 直接作回归右手变量前宜取对数或缩尾, 并以稳健推断对待长尾; 倒数变换还会把约束估计在小自我网络上的噪声非线性放大, 故稀疏年份的极端高值须审慎, 不宜据个别高值下强结论。局限三, 超边与权重敏感: 一篇同时提及大量银行的报道 (榜单、批量监管通报、行业综述) 会以等权 clique 投影贡献 N 取二条共现边, 可能凭边数组合膨胀主导网络进而抬高或压低相关银行的约束; 生产函数保留了 Newman 式超边归一化选项 (hyperedge_normalize, 对每篇 N 家银行的每对边赋 1/(N−1) 权以守恒单篇总度贡献, 使大 N 报道不因组合数爆炸而支配网络), 但该参数在判据分轨路径直接 raise 拒绝、在主路径亦仅为预留且尚未接线到 config 与 runner, 生产流水线中不可达; 现行口径一律等权加一, 解读时须知大 N 文章的潜在主导, 必要时须在样本层单独审视超边密集年份。局限四, 跨年可比性: 判据、节点集与网络规模逐年变化, 约束是局部量而非全网归一量, 故 bank_ci 的水平在跨年直接比较时并非严格可比 (镜像 bank_is_hub 一类绝对阈值量因每年 N 变化而漂移的问题), 宜作年内相对量或配合年固定效应使用。局限五, 边的媒体产物属性: 共现边来自"谁与谁被一起写", 记者社会网络自身的选择与偏倚 (Xu, 2024) 会渗入边的生成, 故约束逆刻画的是媒体注意力结构中的经纪位置, 未必等同真实业务或股权关联中的结构洞, 因果与政策解读须守此边界。与此相接的是边层面的统计效度问题: 投影共现网络的边中混有高活跃度节点的机械伴生边, 二部系统的统计显著网络甄别 (Tumminello 等, 2011) 与二模投影元验证 (Cimini 等, 2022) 提供了过滤这类伪边的方法学参照, 而金融网络中心度量对边集扰动的稳定性亦可用统计验证框架评估 (Sadeghi & Feinstein, 2024 对传染中心度的显著性检验即为此类工作)——本管道未对边做显著性剪枝 (保持原始共现证据的完整与可复现), 而是以三判据梯子从构造侧回答同一疑问: 若某条结论只在最松的同篇边集下成立、在句窗与同句边集下消失, 则该结论很可能由弱证据边驱动, 判据梯子在此起到与统计边过滤互补的证伪功能。稳健性梯子叙事: 同篇、句窗、同句三判据构成本家族的核心稳健性梯子, 随判据收紧边被移除, 一部分银行落到度小于二转为缺失, 幸存银行的自我网络结构洞随之改变, 三个变体各自 just-identified 并排、互为稳健性、不分主次, 用以检验结论是否被"银行如何算作邻近"这一构造选择所驱动; 该梯子与词典消融梯子、政治词权重梯子、跨厂商 per-model 稳健性梯子相互正交、不交叉组合, 一切梯子与判据的每一臂各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。须补记一项良好性质与其边界: bank_ci 是纯组合拓扑运算、确定性且零成本, 不落入受 BLAS 浮点漂移影响的三列非确定网络列 (聚类系数、电流介数、调和中心度及其判据变体), 跨次重建逐位可复现, 这使它作为 canonical core 列在 golden 复现体系中无需进入 BLAS 排除清单; 但须注意, 确定性仅指同一输入下计算结果逐位可复现, 并不消除上文所述边的构造性与样本选择性局限, 二者是不同层面的问题, 不可以前者搪塞后者。生产层面须披露的剔除比例、缺失率与判据敏感性对照数值由引擎注入的动态统计与生产日志承载, 本文不手填。

## VAR: bank_ci

【变体差分】本列是家族 canonical 且为 core 列, 承担银行共现网络"结构洞与经纪优势"测度的规范载体职能。判据为同篇共现 (criterion='article'), 无判据后缀: 两家银行只要在同一篇 (同一 docid) verified 金融科技报道中被一起提及, 即在该年度加权无向图上构成一条共现边, 边权累加为年内共现次数。约束逆 bank_ci 定义为一除以该银行在此图上的 Burt 加权聚合约束 (networkx.constraint 以 weight 为权), 仅当约束有定义且严格为正时取值, 否则置缺失; 而约束在银行度小于二时按定义不可测、置缺失。因此本列缺失当且仅当该银行该年度小于二 (共现伙伴不足两家) 或图退化致约束不可定义; 这一度小于二的缺失阈值严于家族内有效规模 (F090, 度等于零才缺失) 的守卫, 故恰好一个共现伙伴的银行有有效规模却无 bank_ci, 两列样本框刻意不重合。计算的加权口径值得写清: 约束对节点 i 的每个邻居 j 累加一项二元约束, 该项等于 i 直接投向 j 的关系份额 p_ij (按边权即年内共现次数归一) 加上 i 经共同邻居 q 间接投向 j 的份额之和, 再取平方; 平方使高冗余关系被非线性放大, 邻居越少、投入越集中于个别伙伴、伙伴间又越互连, 聚合约束越高、bank_ci 越低。正因权重经 p_ij 进入, 一篇大 N 报道抬高的高共现次数会同时改变相关银行对的边权与投入占比, 这也是下文超边敏感性的根源。数值语义: bank_ci 越大, 约束越低, 结构洞越多, 该银行在共现网络中越占据可中介非冗余信息的经纪位置; 值小则处于封闭冗余的小圈子, 经纪机会稀薄。同篇判据走 both-verified 主路径: 在同一 docid 分组内, 该年幸存于 verified 宇宙的 target_bank 集合逐无序对各加一权, 每篇每对恰一次, 从而每篇提及 N 家银行的报道贡献 N 取二条等权边; 相较无 docid 时退回 co_mentioned_banks 逐行计数的兼容口径 (含一倍二倍混计与幻影边), 主路径以文章为聚合单元, 边权口径干净可控。作为三判据中最松的边口径, 同篇判据产生最稠密的网络, 幸存 (度大于等于二) 银行最多、缺失最少, 故本列是三列中样本量最大、跨年覆盖最完整的一列; 相应地, 它对"同文即连边"的伪关联也最敏感, 这正是收紧句窗的两个稳健性臂要校正的对象。数值上, 约束逆的量纲为纯数、无固定上界, 当银行处于共现伙伴众多且彼此互不相识的极开放自我网络时可取很大的值, 落于长尾右端; 中位数附近的银行则处于伙伴适中、部分互连的常态结构。构念方向承 Burt (2004) 的结构洞即经纪优势逻辑, 拓扑基底则是"文章—银行"隶属关系的一模投影 (Faust, 1997; Borgatti & Everett, 1997), 加权约束的权重口径与加权网络结构测量传统一致 (Barrat 等, 2004; Opsahl 等, 2010)。须知两点解读要点: 其一, 同篇共现是一种较弱的邻接证据——被写进同一篇行业综述或榜单并不必然意味着两家银行有真实业务关联, 这一"过度包含"倾向正是 bank_ci_win1 与 bank_ci_sent 收紧句窗以求校正的对象, 三者并排即为判据敏感性稳健性梯子; 其二, 本列是纯组合拓扑运算、确定性且零成本, 不受 BLAS 浮点漂移影响, 跨次逐位可复现, 与家族内聚类系数、电流介数、调和中心度那三列非确定网络列的可复现性状态不同。计量用法: 作经纪优势的调节、机制或异质性协变量进入 brokerage_network 脉络, 节点级变异使其在年固定效应下仍可识别 (区别于 net_*_yr 年广播列); 因分布重右偏且理论上无上界, 建议取对数或缩尾后解读边际效应, 并按调节/中介框架而非外生处理作因果解读。铁律: 本列与 bank_ci_win1、bank_ci_sent 三判据各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 判据后缀口径 (银行∧银行邻接) 与三轨文本后缀 (银行∧金科文本) 正交, 禁交叉。另须警惕: 本列与 bank_constraint (F086) 互为倒数、近乎完美负相关, 绝不可并列作两个解释变量进同一回归。

## VAR: bank_ci_sent

【变体差分】本列是家族 canonical 的严格同句判据变体 (criterion='sent', suffix='_sent', 句窗半径为零), 与 canonical 的唯一差分在共现边的判据: 两家银行必须出现在同一句话内, 才算构成一条共现边。构造上, 该判据在 docid 组内做句级重扫——取组首行正文前置标题 (标题作第 0 句, 镜像 stage 13 的 match_in_title), 用 map_bank_sentence_positions 定位各银行别名句位, 再取严格同句 (半径零) 的银行对成边; 扫描复用与 stage 11/13 同源的否定 AC 与短名排除, 以防"涉农行业"误命中"农行"这类短名假阳性。这是三判据中最严的边口径: 只有并列于同一句的银行对才成边, 分处不同段落、仅因同属一篇长综述而被同篇判据连边的银行对在此被剔除, 因而它以最强的关系证据换取最稀疏的网络。语义上, 同句共现更接近"两家银行被真正相提并论"的强关联信号, 显著压低由长文泛提及产生的伪边, 使约束逆更贴近真实结构洞而非文章版式产物。代价是网络更稀疏: 更多银行落到度小于二转为缺失, 本列的样本量在三判据中最小、缺失最多, 幸存银行的自我网络也更小, 约束估计的噪声更大; 在早期试跑盘浅样本上尤其可能大面积退化, 须在生产 T 等于十八语料上评估其信息量。用法定位: 作 canonical 的判据稳健性臂, 检验主结论是否稳健于"用最严的同句证据定义银行邻近"这一收紧; 与 bank_ci、bank_ci_win1 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。关键警示: 后缀 _sent 是银行∧银行的同句邻接判据, 与三轨文本中 _ss 轨的"银行∧金科同句共现"是两套完全不同的口径 (一为银行对邻接、一为银行与金科词的文本轨), 命名相近但概念空间正交, 解读与建模时切勿混淆或交叉进同一方程。

## VAR: bank_ci_win1

【变体差分】本列是家族 canonical 的正负一句窗判据变体 (criterion='win1', suffix='_win1', 句窗半径取 config/panel.yaml::network_criteria.win_radius, 默认为一), 与 canonical 的唯一差分同样在共现边的判据: 两家银行须出现在相距不超过 win_radius 句 (默认正负一句) 的窗口内, 才构成一条共现边。构造路径与 sent 变体相同——docid 组内句级重扫、标题前置作第 0 句、map_bank_sentence_positions 定位句位、复用否定 AC 与短名排除防假阳性, 差别仅在句窗半径由零放宽到 win_radius。该判据的严格程度居中: 边集包含于同篇判据、又包含严格同句判据, 满足同篇边集包含句窗边集、句窗边集包含同句边集的嵌套关系。语义上, 它在同篇判据的"过度包含" (同文即连边, 易纳入长综述的伪关联) 与同句判据的"过度严格" (仅同句成边, 易漏掉紧邻两句的真关联) 之间取折中: 允许相邻一句内的银行对成边, 既保留跨句紧邻的真实相提并论, 又剔除相隔较远段落的泛提及, 通常给出比同句更稠密、比同篇更干净的网络, 缺失率介于二者之间。须注意句窗半径键 network_criteria.win_radius 与 stage 13 银行∧金科硬过滤所用的 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的不同配置键, 前者管本家族银行∧银行邻接、后者管上游银行∧金科留篇, 勿混用。用法定位: 作 canonical 的判据稳健性臂, 与 bank_ci、bank_ci_sent 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 判据后缀 (银行∧银行邻接) 与三轨文本后缀 _full/_ctx/_ss (银行∧金科文本) 是正交概念空间, 禁交叉进同一过度识别方程。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Amancio, D. R., Machicao, J., & Quispe, L. V. C. (2025). Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis. PLOS ONE, 20(7), e0327421. https://doi.org/10.1371/journal.pone.0327421
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Hoshino, T. (2023). Causal interpretation of linear social interaction models with endogenous networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2308.04276
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Tumminello, M., Miccichè, S., Lillo, F., Piilo, J., & Mantegna, R. N. (2011). Statistically validated networks in bipartite complex systems. PLoS ONE, 6(3), e17994. https://doi.org/10.1371/journal.pone.0017994
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Johnson, J. C., & Sasson, A. (2026). Reassessing Constraint's Meaning: A Framework for Reinterpreting Structural Holes' Findings. Strategy Science. https://doi.org/10.1287/stsc.2024.0297
Shipilov, A., Li, S. X., Bothner, M. S., & Truong, N. (2023). Network advantage: Uncontested structural holes and organizational performance in market crises. Strategic Management Journal. https://doi.org/10.1002/smj.3538
Miori, D., & Petrov, C. (2024). Narratives from GPT-derived networks of news and a link to financial markets dislocations. International Journal of Data Science and Analytics. https://doi.org/10.1007/s41060-024-00516-x
<!-- rendered-citations:end -->
