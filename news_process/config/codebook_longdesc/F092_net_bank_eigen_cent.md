---
family_id: F092
columns:
- bank_eigen_cent
- bank_eigen_cent_sent
- bank_eigen_cent_win1
unit: 网络结构指标 (无量纲); 特征向量中心度分量内 L2 归一, 微小分量与未参与银行置 NaN
formula: "年度银行共现加权无向图 (networkx; 节点=年内 full-only 留篇幸存银行, 边=同篇共现每对 +1) 上按连通分量分别求解主特征向量并分量内 L2 归一 (nx.eigenvector_centrality, weight='weight', max_iter=2000, tol=1e-06); <3 节点微小分量与未参与银行置 NaN。判据变体 {同篇 (无后缀) / ±1 句窗 _win1 / 严格同句 _sent}"
producer: "pipeline\\panel\\network_spillover.py::compute_bank_network_centrality (build_adjacency_matrix; runner 步骤 7h-cent 三判据调用); 描述表 papers\\brokerage_network\\tables.py::_TABLE1_VARIABLES"
upstream:
- 24_herd_decay.parquet (df_exploded; stage21 full-only 留篇 both-verified 篇章级集; 含 docid/target_bank/year/内容/标题)
- 40_panel_yearly.parquet (bank-year 面板骨架, left-join 目标)
- config/panel.yaml::network_criteria.win_radius (判据 _win1 句窗半径, 默认 1)
citations:
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: "79-104"
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Xuenan Yang, Zihan Liu, Jingyu Li, Qiwei Xie"
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: "2903-2935"
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: "543-565"
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: "103223"
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: "102163"
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: "2691-2729"
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: "247-272"
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: "e0274475"
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: "171-202"
- doi: 10.1080/15427951.2013.865686
  type: journal
  authors: Boldi, P., & Vigna, S.
  year: 2014
  title: "Axioms for centrality"
  venue: Internet Mathematics
  vol: 10
  issue: 3-4
  pages_or_artno: "222-262"
- doi: 10.1016/j.socnet.2010.03.006
  type: journal
  authors: Opsahl, T., Agneessens, F., & Skvoretz, J.
  year: 2010
  title: "Node centrality in weighted networks: Generalizing degree and shortest paths"
  venue: Social Networks
  vol: 32
  issue: 3
  pages_or_artno: "245-251"
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: "41-55"
- doi: 10.1103/PhysRevE.71.056103
  type: journal
  authors: Estrada, E., & Rodríguez-Velázquez, J. A.
  year: 2005
  title: "Subgraph centrality in complex networks"
  venue: Physical Review E
  vol: 71
  issue: 5
  pages_or_artno: "056103"
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: "39-54"
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: "157-191"
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: "243-269"
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: "531-542"
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: "1170-1182"
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: "215-239"
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: Bonacich, P.
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: "113-120"
- doi: "10.1016/j.jcorpfin.2023.102501"
  type: journal
  authors: "Fan, Y., Jiang, Y., Jin, P., & Mai, Y."
  year: 2023
  title: "CEO network centrality and bank risk: Evidence from US Bank holding companies"
  venue: "Journal of Corporate Finance"
- doi: "10.1111/abac.12341"
  title: "Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum"
  authors: "Guo, F., Lyu, B., Lyu, X., & Zheng, J."
  year: 2025
  venue: "Abacus"
  type: "journal"
- doi: "10.1007/s11424-025-4338-6"
  title: "The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes"
  authors: "Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X."
  year: 2025
  venue: "Journal of Systems Science and Complexity"
  type: "journal"
new_dois:
- "10.1016/j.procs.2023.08.056"
- "10.1016/j.jcorpfin.2023.102501"
- "10.1111/abac.12341"
- "10.1007/s11424-025-4338-6"
---

## CORE

基于新闻文本构建中国金融机构共现网络并用社区发现方法识别银行、证券、保险等行业聚簇, 与本家族银行新闻共现图特征向量中心度构念高度同源, 已通过 CrossRef API 核验题名/作者/年份/期刊完全吻合。

【构念与来源】
bank_eigen_cent 是"银行年度新闻共现网络"上的特征向量中心度 (eigenvector centrality), 为本家族的 canonical 列 (同篇判据, 落列无后缀)。构念回答一个递归式的重要性问题: 一家银行是否"重要", 不只看它与多少家同业在新闻里被一同提及 (那是度中心度 degree), 而要看与它共现的同业本身是否也重要 — 中心的邻居越多、邻居越中心, 该行的特征向量中心度越高。形式上, 若把年度加权共现图的邻接矩阵记作 A, 则特征向量中心度就是与最大特征值 (Perron-Frobenius 主特征值) 相配的主特征向量各分量: 一个节点的分值正比于其邻居分值的加权和, 因而"地位由邻居地位递归定义"。这一思想源自 Bonacich (1972) 的因子化与加权状态分数, 后经 Bonacich (1987) 系统化为一族权力与中心度测度 (其中引入负参数还可刻画"依附于弱者反而更有权力"的情形, 本项目只取标准正向特征向量一支); Freeman (1978) 对度、接近性、居间性三大中心度族做了概念澄清, 本项目 33 个网络结构指标即以该谱系为骨架, 特征向量中心度落在"声望与地位"一支, 与桥梁型的居间度、拓扑型的度中心度并列而不重叠。为什么用新闻共现来建这张网: 当两家银行在同一篇金融科技报道里被一并讨论, 说明它们在公众信息环境中被投射到同一议题空间 (同一监管动作、同一技术浪潮、同一业务竞合), 共现频次因而是"信息层面的同侪关联强度"的可观测代理; 把这些两两关联累积成年度图, 特征向量中心度即刻画"哪家银行处于媒体信息声望的高地"。数据来源方面: 网络的节点全集等于某年通过 stage 21 语义留篇门控 (full-only 口径, 2026-06-29) 后, 在篇章级 both-verified 帧 (df_exploded, 即 24_herd_decay) 中幸存的 target_bank; 边等于同一篇报道 (同一 docid) 内所有幸存银行之间的两两共现, 每篇每对无序对权重 +1, 邻接矩阵对称; 边权则等于年内该对共现的累计篇数。这里的 both-verified 指同一文章下、通过 stage 21 语义核验而幸存的目标银行行集合 (即真正被判定为"银行金科报道主体"的银行), 从而杜绝把核验已拒绝的银行也当节点或成边。由此得到逐年的加权无向共现图 (networkx Graph)。留篇门控是 full 轨的单一裁决: 一篇报道是否算"银行金科报道"只看 llm_verified_full, 因此共现网的边只由 full 轨留篇集诱导, 与 _ctx/_ss 文本轨无关; 这一口径必须与 full-only 门控保持一致, 不得误认为三轨各自建网, 也不得把 _ctx/_ss 的留篇集混入网络构造。

【方法学与计算】
邻接矩阵在 build_adjacency_matrix (criterion='article') 内构造: 对每个 docid 分组, 取该组幸存 target_bank 集合, 组内每一无序对 {A,B} 恰好 adj[A,B] += 1 且 adj[B,A] += 1 (每篇每对严格一次), 从根上杜绝旧实现里"twin 行 1 倍或 2 倍混计"以及 co_mentioned_banks 携带 verification 已拒绝银行而产生的 phantom 边 (口径统一记于 omni-g-net-spill-01)。矩阵建好后先转成加权无向图 G (边权取共现次数), 并把年内所有幸存银行都加入图中以保留孤立节点; 另建一张倒数权重图 G_inv (边权取 1/共现次数) 供路径型指标使用, 但特征向量中心度只用原始图 G。加权图 G 建成后, 特征向量中心度按连通分量分别计算 (P1-1 修复, network-metrics-audit 2026-06-13): 先以 connected_components 拆分连通分量, 对每个不少于 _CMNT_MIN_COMPONENT_SIZE (等于 3) 个节点的分量取其子图, 调用 nx.eigenvector_centrality (weight='weight', max_iter=2000, tol=1e-06) 在分量内做幂迭代求主特征向量, 并由 networkx 在该子图范围内做 L2 归一; 幂迭代的 tol 与 max_iter 决定收敛判据 (2000 步内相邻迭代差小于 1e-06 即收敛), 分量最小 3 节点的门槛对应"最小三角"— 少于 3 节点的分量 (孤立点或单边对) 特征向量平凡、无区分度, 一律置 NaN。若某分量在 2000 步内幂迭代仍不收敛 (抛 PowerIterationFailedConvergence), 则该分量退回 degree_centrality 兜底并升为 CRITICAL 日志 (仅极端退化分量触发, 语义已偏离特征向量, 故显式告警而非静默)。任何未落入合格分量的银行, 在把节点级结果左连接回面板后缺失, 即得到 NaN, 不再写 0 或数值残渣。P1-1 之所以关键, 在于旧实现是在整图 G 上跑幂迭代: 断连图下 networkx 并不抛不收敛异常而是收敛到谱半径最大的分量, 把特征向量质量几乎全部压到该分量, 其余分量 (含最大连通分量, 若其谱半径并非最大) 的银行只得到约 1e-42 量级的数值残渣 — 这不是 NaN, 会被回归当成"中心度极低的真银行", 造成系统性偏误; 且内部 eigen_done 标志会锁死, 使针对最大连通分量的 numpy 兜底永不触发。主控实证曾观察到非主导分量节点得到 3e-42 至 5e-42 的残渣。全量 T=19 的共现网几乎必然断连, 旧口径会造成大面积污染, 同型缺陷在 network_brokerage 的分量法 (_eigenvector_centrality_by_component) 里已先行修复, 此处移植同款逻辑。分量内计算的直接代价是一条必须披露的口径: 特征向量中心度的水平仅在分量内可比 (networkx 在子图范围内做 L2 归一), 跨分量比较只在"是否身处大分量"这一意义上成立, 池化任何跨分量的水平统计都会混标尺。补充两处工程细节以便复核: 其一, docid 主路径是 both-verified 的规范口径, 仅当帧缺 docid 列时才降级到旧的 co_mentioned_banks 逐行解析路径并给出告警, 生产数据带 docid 因此走主路径; 其二, 特征向量用的是原始加权图 G (边权即共现次数, 语义为"关系越强、连接越紧"), 而非路径型指标所用的倒数权重图 G_inv (边权 1/共现次数, 把"共现越多"翻译成"距离越短"), 也不局限于最大连通分量 G_lcc (那是当前流居间、离心率、平均路径长度等 LCC-only 指标的定义域)— 三种图的分工必须分清, 特征向量只吃 G。计算收尾时函数会记录逐列的非缺失覆盖率与均值, 并对特征向量列专门给出覆盖判读 (覆盖率低于 0.5 时提示"多数置 NaN, 断连图微小分量所致"), 同时诊断零方差列 (进回归会被年份或银行固定效应吸收); 这些诊断只写日志、绝不进入产物或控制流。

【文献定位】
特征向量类中心度在金融网络研究中被反复用作"结构重要性与信息枢纽"的代理。Yu、Hu 与 Zhong (2024) 记录网络中心度经由信息扩散进入资产定价, 与本列"媒体共现声望"的信息传导直觉同源; Xu 与 Zhao (2024) 检验金融网络中节点中心度对资产价格预测的贡献, 提供了另一条平行证据; Jackson 与 Pernoud (2021) 综述金融网络中结构位置与系统性风险之间的联系, 说明中心节点在冲击传导中承担放大作用; Sadeghi 与 Feinstein (2024) 进一步为金融网络中的传染性中心度提供统计验证框架, 提醒研究者中心度估计本身带有抽样不确定性、不宜当作无误差的确定量。Nezami、Chisam 与 Palmatier (2025) 对中心度与企业绩效关系做了元分析, 为"中心度可作解释变量或控制变量"提供了跨领域的汇聚证据; 须注意该元分析背书的是中心度到绩效这条链, 并不背书本项目某些特定的聚类型测度 (如 bank_clustering), 引用时不可越界扩大其结论边界。在测度选择的规范性上, Boldi 与 Vigna (2014) 提出的中心度公理为在众多候选测度中挑选特征向量族给出了理论依据 (特征向量满足其对"重要邻居传递重要性"的公理化要求); Opsahl、Agneessens 与 Skvoretz (2010) 把度与最短路中心度推广到加权网络, 恰好对应本图 weight='weight' 的加权口径, 说明在带边权的图上直接沿用二值中心度会丢弃共现强度信息。这些文献共同支撑一个立场: 在加权、可能断连的金融共现网上, 特征向量中心度是刻画"银行是否处于信息声望高地"的合适而非唯一的测度, 它与度、居间、子图等测度构成互补而非替代的谱系, 应并排报告而非择一。Fan, Jiang, Jin 与 Mai (2023, Journal of Corporate Finance) 以美国银行控股公司为样本, 用网络中心度刻画高管在关系网络中的地位并检验其与银行风险的关系, 为本列银行在信息/关系网络中所处结构位置这一构念在银行业情境下提供了新近的实证参照。Guo, Lyu, Lyu 与 Zheng (2025, Abacus) 利用中国股吧构建投资者社交媒体共现网络, 发现网络中心度与股价同步性显著负相关, 为共现网络中心度作为信息声望代理提供了新近实证支持。Huang, Deng, Yang, Cai 与 Zhao (2025, Journal of Systems Science and Complexity) 基于中国上市公司动态股票网络, 发现网络中心度更高的公司未来股价崩盘风险更低, 佐证网络中心度作为结构重要性代理与风险传导之间的联系。

【识别策略定位】
三判据 (article、win1、sent) 是规格稳健性梯子, 不是工具变量, 也不进同一 Hansen J。本家族三列 bank_eigen_cent、bank_eigen_cent_win1、bank_eigen_cent_sent 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同判据的同构念列混进同一 over-identified 的 Hansen J 过度识别检验 (镜像三轨文本、co-primary 双轨嵌入、政治词权重梯子、词典消融梯度的同款铁律)。须特别强调: 判据后缀 (article/win1/sent, 刻画银行与银行的邻近共现) 与三轨文本后缀 (_full/_ctx/_ss, 刻画银行与金科的同现) 是两个正交的概念空间, 禁止互相复用, 更禁止混进同一 Hansen J; 前者变的是"两家银行要多近才算一条边", 后者变的是"用哪段文本判定一篇是否银行金科报道", 二者调的是完全不同的旋钮。此处还须与另一处口径联动: 网络节点全集由 full-only 留篇门控 (2026-06-29) 诱导 — 一篇报道是否算"银行金科报道"只看 llm_verified_full, 边只由 full 轨留篇集诱导, 与 _ctx/_ss 文本轨无关 — 因此中心度对门控口径本身敏感, 换门控即换节点全集, 这一识别相关的设定必须与 full-only 口径一致披露, 不得误认为三轨各自建网。当把网络中心度当作回归右手变量时, 银行间的新闻共现天然带有 Manski (1993) 反射问题意义上的同伴内生性: 中心行的舆情既受邻居影响, 又反向塑造邻居, 简单把邻居均值放进回归无法区分内生、外生与关联效应。更进一层的内生性在于共现连边本身: 一家更受关注、更"上头条"的银行会吸引更多同篇提及, 网络结构因而与被解释变量联合决定, 边不是外生给定而是从媒体报道观测推断得来, 带观测噪声; 中心度作为邻接矩阵主特征向量的分量, 是边的高度非线性函数, 会继承并放大这层噪声。Bramoullé、Djebbari 与 Fortin (2009) 给出了通过社会网络结构 (朋友的朋友、即网络的高阶邻接) 识别同伴效应的条件, 是把中心度类变量接入因果设计的经典识别路径; Boucher、Rendall、Ushchev 与 Zenou (2024) 推进了同伴效应的一般理论, 放宽了线性均值互动的限制; Grieser、Hadlock、LeSage 与 Zekhnini (2022) 在公司财务政策中实证了网络溢出的存在, 示范了空间自回归式的网络计量应用; 而 de Paula、Rasul 与 Souza (2024) 专门讨论如何从面板数据里识别网络连边本身, 恰好点出本列的隐忧 — 当网络不是外生登记的确定连边、而须从观测数据推断时, 连边的测量误差会与同伴效应的识别问题叠加, 使"先估网络再算中心度再进回归"这一链条的每一环都携带不确定性。这些共同构成把 bank_eigen_cent 接入因果设计时的方法学坐标。本列本身是网络结构的描述性构造, 任何因果识别都须另配空间或网络计量工具 (如网络工具变量、高阶邻接排除限制、从面板推断连边的先验约束), 单凭把中心度放进回归右手不构成识别, 这一点在本项目内也由"本列不进论文回归 RHS"的约定强制体现。

【与相邻测度的构念区分】
bank_eigen_cent 须与四类相邻测度严格区分, 以免在解读或建模时张冠李戴。其一, 与本项目论文回归真正使用的 brokerage_eigen_cent 不同, 这是最容易混淆、也最要害的一处: 后者是 Han、Kim 与 Nanda (2024) 意义上的机构经纪网络特征向量中心度, 建在经纪与机构撮合网络上, 是 brokerage_network 论文的回归右手变量; 前者 (本列) 建在新闻共现网络上, 且因分量内归一, 池化的均值与标准差会混合不同分量的标尺, 只能作 brokerage_network 论文 Table 1 的粗略描述统计 (记于 NB-04, 表注宜注明"分量内归一"), 绝不进回归右手变量。两者名字相近、构念与图基底却完全不同, 引用与制表时必须点名区分。其二, 与同族其他谱型指标区分: bank_katz_cent (Katz 中心度, α 取 0.9/λ_max, 在全图带统一阻尼衰减、缺失写 0.0 而不置 NaN, 因阻尼常数对断连图更稳健) 与 bank_subgraph_cent (Estrada 与 Rodríguez-Velázquez 2005 的子图中心度, 通过邻接矩阵的矩加权计闭合环路数, 强调局部环路参与度) 同样度量"邻居质量与结构参与", 但归一方式与断连处理各异 — 特征向量按分量归一并对微小分量置 NaN, Katz 则以阻尼常数保证全图有定义; 须记得 Bonacich (1987) 的权力中心度族以参数 β 统一了特征向量 (β→1/λ_max 极限) 与 Katz 型阻尼两端, 本项目取两端分列而非合并, 正是为了并排呈现"纯声望"与"带阻尼衰减的声望"两种口径。其三, 与拓扑型和桥梁型指标区分: degree 只数邻居数量、strength 数加权共现强度 (即 Opsahl 2010 的 node strength, 本项目再做年内最大值归一), 都是"数量"语义; 居间型的 bank_between_cent 与当前流居间的 bank_cfbetween_cent (思想族可上溯 Newman 2005 的随机游走/当前流居间) 量的是"桥梁地位"; 而特征向量量的是"声望地位"— 高特征向量的银行未必是桥梁, 而是嵌在一个彼此都重要的稠密簇里。经纪角色一支 (Gould-Fernandez 的协调者、看门人、联络人等角色, 加权归一见 Zádor 等 2022) 又是另一维度, 与特征向量正交, 不可互相替代解读。其四, 与"二模隶属网络投影"这一底层数据结构区分, 这是本列构念上最隐蔽却最要害的一层: 新闻共现图本质是"文章×银行"二模 (two-mode) 隶属网络 (affiliation network) 向"银行×银行"一模的投影, 每篇报道诱导一个团、组内每对等权成边。Faust (1997) 专门讨论隶属网络的中心度, 指出把二模网投到一模会系统性夸大"同篇多提及"所诱导团内节点的度与特征向量分值; Borgatti 与 Everett (1997) 给出二模数据的网络分析框架, 提醒直接在投影图上算中心度会丢失"是哪一篇文章把它们连起来"的隶属信息。因此本列的特征向量不宜被解读为纯粹的"银行间关系强度", 而应理解为"经由共同报道议题投射出的声望", 其数值分布对大 N 报道诱导的团结构天然敏感 — 这一投影视角同时是下节局限的理论起点。

【已知局限与稳健性梯子】
局限一: 分量内归一使跨分量水平不可比, 池化描述统计 (brokerage_network 表 1 的 NB-04) 混合了不同分量的标尺, 因此严禁直接做跨行水平比较, 或把它当作未标准化的回归右手变量; 若确需回归, 须先改结构性归一或改用建在同一图基底、全图可比的中心度。局限二: 共现边默认未做超边归一 — 一篇提及 N 家银行的榜单或批量监管通报会贡献 C(N,2) 条等权边, 大 N 文章可凭边数膨胀而主导整张网, 污染特征向量的质量分布; 这正是上节二模投影视角所预言的伪影: 一篇 N-银行报道在投影图里生成一个 N-团, 团内每对等权, 特征向量会把这类由单篇隶属诱导的团误读为"彼此都重要的稠密簇", 从而把大 N 报道里所有被点名的银行一并抬高 (Faust 1997 对隶属网投影的中心度夸大给出了理论刻画)。缓解手段 hyperedge_normalize (保度归一: 每对贡献 1/(N-1) 使单篇总度贡献守恒) 是预留参数, 尚未接线到 config 与 runner, 在生产流水线中不可达, 而判据分轨路径 (win1/sent) 更直接对其 raise 拒绝以防三判据轨无警告分叉, 因此当前所有 bank_eigen_cent 都是未超边归一的口径, 解读时须记得大 N 文章的权重未被抑制; 从这个意义上, 三判据梯子 (同篇→句窗→同句) 也间接抑制了大 N 伪影 — 判据越严, 一篇报道能同时把多少家银行连成团就越受句级邻近约束, 团规模随之收缩, 因而 sent 判据下的中心度分布对超边膨胀的敏感度低于 article 判据。局限三: 确定性与工具口径 — 本列由固定 tol=1e-06、max_iter=2000 的分量内幂迭代产出, 不在权威的三列 BLAS 浮点非确定集 (bank_clustering、bank_cfbetween_cent、bank_harmonic_cent, 判据分轨后为该三基名的无后缀/_win1/_sent 共九列) 之内; 但 golden 差分守卫 diff_golden.py 的宽正则以子串方式顺带覆盖了 bank_eigen_cent, 这一"宽清单与三基名清单不一致"已被登记, 待生产机全量重生时实证统一 — 也就是说, 验零漂移的排除口径以权威三基名为准, 宽正则的顺带覆盖属工具侧保守设置, 不改变本列在方法上确定的判定。局限四: 在早期试跑 T=2 开发切片上, 共现网极稀疏且断连严重, 微小分量大量置 NaN 属预期退化, 覆盖率诊断 (低于 0.5 触发"多数置 NaN"提示) 与零方差诊断在 T=2 常亮红, 须待生产 T=19 才恢复正常, 审计时不得以 T=2 退化为由否定实现。稳健性梯子即三判据 (同篇、±1 句窗、严格同句) 逐级收紧边集: 判据越严, 图越稀、分量越碎、NaN 越多, 三条并排检验"共现越贴近同句时中心度结论是否依然稳健"; 三者各自 just-identified、互为稳健性、不分主次, 绝不并入同一过度识别检验。这条梯子回答的是测量效度问题 — 若结论只在最宽的同篇判据下成立、在同句判据下翻转, 就提示共现关系可能由"同篇不同段"的松散并置驱动而非真正的议题共嵌, 反之三判据一致则测量稳健。

【下游消费与制表约定】
本列的下游消费面窄而明确: 它进入 brokerage_network 论文的 Table 1 描述统计变量清单 (_TABLE1_VARIABLES), 与 bank_degree_cent、bank_strength_cent、bank_clustering、bank_constraint、bank_ego_density、bank_effective_size 等节点级指标并列作粗略画像, 但代码注释 NB-04 明确警示: 自 P1-1 起本列按连通分量内 L2 归一, 跨分量水平不可比, 表内池化的均值与标准差混合了不同分量的标尺, 因此只能作粗略描述、表注宜注明"分量内归一", 而真正进论文回归右手变量的是经纪网络上的 brokerage_eigen_cent, 不是本列。制表与写作时须守住这条边界, 不得把新闻共现网的特征向量中心度当作可跨行比较的回归自变量, 也不得把它与经纪网中心度混为一谈。系统性风险文献 (Jackson 与 Pernoud 2021) 提示中心节点在冲击传导中的放大角色, 但那是把中心度接入结构模型后的解释, 本列本身只提供描述性的结构位置刻画; 若要走到系统性重要性的因果论断, 须另配传染模型与识别策略, 且如 Sadeghi 与 Feinstein (2024) 所强调, 还须为中心度估计配上统计验证与不确定性刻画, 不能把点估计当无误差常量。

## VAR: bank_eigen_cent

【变体差分】
本列是家族 canonical, 判据等于 'article' (同篇), 落列无后缀。它区别于两个稳健性同胞的唯一维度, 是共现判据的宽严: article 判据只要求两家幸存银行出现在同一篇报道 (同一 docid) 内, 不论二者相隔多少句 — 这是现行生产口径, 也是 build_adjacency_matrix 的默认路径与 compute_bank_network_centrality (criterion='article', suffix='') 的对应产物 (criterion 与 suffix 通过 _expected_suffix 映射强绑, article 必配空后缀, 错配即 raise, 从签名层堵住判据与后缀分叉)。同篇判据是最宽的建边规则, 因而边最密、图最连通、合格连通分量最大、落入不少于 3 节点分量的银行最多、NaN 最少, 是三判据里覆盖率最高、最能在浅面板上出值的一条, 也因此被选作 canonical 与另两条判据的比较基准。计算路径与家族核心逐字一致, 此处不重复推导, 只强调三点差异化要点: 第一, 同篇建边不做任何句级重扫 (无需 map_bank_sentence_positions), 直接按 docid 幸存 target_bank 集合两两 +1, 因此它是唯一走 both-verified 主路径而非句级分轨路径的判据, 计算最轻; 第二, 由于边最多, 大 N 文章 (榜单/批量通报) 对本列的边数膨胀影响也最显著, 而超边归一在本列不可达 (预留参数未接线), 解读时须记得大 N 篇章权重未被抑制; 第三, 它承接家族全部口径铁律 — 由 full-only 留篇门控诱导边集、水平仅分量内可比、边未超边归一、按分量跑 nx.eigenvector_centrality (weight='weight', max_iter=2000, tol=1e-06)、微小分量与未参与银行置 NaN、不收敛退 degree 兼升 CRITICAL、且不进论文回归右手变量 (回归用 brokerage_eigen_cent, 见 NB-04)。作为无后缀 canonical, 它在 NETWORK_METRIC_BASES 这一 SSOT 内登记为 33 个基名之一, 是 win1 与 sent 两个判据变体天然的对照锚: 三者互为稳健性、不分主次、各自 just-identified 并排, 禁混同一 over-identified 的 Hansen J; 判据后缀 (银行与银行邻近) 与三轨文本后缀 (_full/_ctx/_ss, 银行与金科同现) 属正交概念空间, 不可互换。使用建议: 描述统计与稳健性主线用本列, 需检验"共现是否须句级邻近"时再并置 _win1 与 _sent; 它同时是 brokerage_network 论文 Table 1 描述变量清单 _TABLE1_VARIABLES 中的一员, 但仅作粗略描述, 表注须注明分量内归一, 不做跨行水平解读, 也不得据此对不同银行的中心度绝对值排座次。再补一处与两个句级判据同胞的关键实现差异: 同篇判据不走 docid 组内句级重扫, 因而不触发 map_bank_sentence_positions、也不消费正文 (内容) 与标题的逐句定位, 更不产生 win1/sent 路径特有的两项诊断 — 即"多银行 docid 组内正文不一致"计数 (n_inconsistent, 取组首行 fail-soft) 与"多银行组数"计数 (n_multi); 本列只需 docid 与 target_bank 两列即可建边, 因此它也是三判据里对缺列最鲁棒、计算开销最小的一条。正因为它是最宽判据、覆盖最全、又不依赖句级文本, 它被自然选作 canonical 与 NETWORK_METRIC_BASES 中登记的无后缀基名; 但须记住"无后缀"只是历史命名与先后顺序的产物, 并不意味着它在方法学上比 _win1/_sent "更主"— 三判据在稳健性意义上完全平权, 谁也不是谁的降级版。落到审计口径: 验 golden 零漂移时以权威三基名 (clustering/cfbetween/harmonic) 的九列为 BLAS 排除集, 本列 (含其两个判据同胞) 在方法上确定, 不因宽正则顺带覆盖而改变确定性判定。最后重申与三轨的正交关系: 本列的"同篇"是银行与银行的邻近判据, 与情感三轨的 full 轨 (银行与金科的文本范围判据) 名义上都可叫"全篇", 但一个调的是共现的空间尺度、一个调的是判定报道归属的文本尺度, 两者维度正交、禁止互相复用, 更禁止把它们混进同一 over-identified 的 Hansen J。

## VAR: bank_eigen_cent_sent

【变体差分】
本列判据等于 'sent' (严格同句), 落列后缀 _sent, 由 compute_bank_network_centrality (criterion='sent', suffix='_sent') 产出 (内部句窗半径 radius 强制取 0)。与 canonical 的唯一差别在建边: 两家银行必须落在同一句内共现才计一条边, 走 docid 组内的句级重扫路径 — map_bank_sentence_positions 先在"标题 prepend 加正文"的文本上逐句定位各行别名 (标题作为第 0 句, 镜像 stage 13 的 match_in_title 口径; 并用同一否定与短名排除事实源, 防"涉农行业"误命中"农行"式假阳性), 再由 bank_pairs_within_sentence_window (win_radius=0) 取严格同句对建对称边, 每篇每对同权 +1。节点全集与 article、win1 完全一致 (同一 df_year 幸存银行, 判据只改边不改点), 但边集最严: 同篇不同句的银行对在此不成边, 因而这是三判据里图最稀、连通分量最碎、微小分量最多、NaN 最多的一条, 在早期试跑 T=2 开发切片上零方差或全 NaN 的退化最明显 (属预期, 生产 T=19 方缓解, 审计不得据 T=2 退化否定实现)。它对应"共现须最贴近、必须落在同一句子里才算真正的议题共嵌"这一最严测量假设; 相较同篇判据, 它剔除了"同一篇报道里前段提甲行、后段提乙行"这类松散并置, 因此若某银行的高中心度只在 article 判据下成立、在 sent 判据下大幅回落, 就提示其共现关系偏松散。其余谱型计算 (分量内特征向量 L2 归一、微小分量置 NaN、不收敛退 degree、边未超边归一、不进回归 RHS) 与家族口径逐字一致。定位: 它是最严判据下的稳健性臂, 与 canonical 及 _win1 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified 的 Hansen J; 判据后缀 (银行与银行同句) 不等于三轨文本后缀 (_full/_ctx/_ss, 银行与金科), 二者是正交概念空间, 不可互换。

## VAR: bank_eigen_cent_win1

【变体差分】
本列判据等于 'win1' (±win_radius 句窗), 落列后缀 _win1, 由 compute_bank_network_centrality (criterion='win1', suffix='_win1') 产出。win_radius 取自 config/panel.yaml::network_criteria.win_radius (默认 1), 经 _get_bank_scan_ctx 惰性加载为进程级单例, 故生产口径等于 ±1 句窗: 两家银行落在相隔不超过一句的窗口内共现即计一条边。它是介于 canonical (同篇, 最宽) 与 _sent (同句, 最严) 之间的中间判据, 建边同样走 docid 组内句级重扫 (map_bank_sentence_positions 加 bank_pairs_within_sentence_window (win_radius=1)), 扫描文本等于"标题 prepend 加正文" (标题第 0 句), 沿用与 _sent 同一套否定与短名排除防线。须特别注意一处易错点: 此处的句窗半径 (network_criteria.win_radius) 与 stage 13 银行与金科硬过滤所用的 cooccurrence_filter.sentence_radius 是两个完全不同的 config 键, 互不联动、不得混用, 也不得因两者默认都是 1 而误以为同源。节点全集与 article、sent 一致 (判据只改边不改点), 边集宽严居中, 因而图的连通性、合格分量规模与 NaN 数量都介于两端, 它承接"共现须句级邻近但允许跨相邻一句"的中庸假设 — 既比同篇判据更贴近真实议题共嵌, 又比严格同句更宽容于跨句的连贯表述。其余谱型计算 (分量内特征向量归一、微小分量置 NaN、不收敛退 degree、边未超边归一、不进回归 RHS) 与家族核心逐字一致。定位: 它与 canonical 及 _sent 三者互为稳健性、不分主次、各自 just-identified 并排, 禁混同一 over-identified 的 Hansen J; 判据后缀 (银行与银行邻近) 与三轨文本后缀 (银行与金科同现) 属正交概念空间, 不可互换。三判据并排读的意义在于: 若结论随句窗从同篇收紧到同句仍稳定, 则中心度测量对"多近算共现"这一主观阈值不敏感, 稳健性得证。

<!-- rendered-citations:begin -->
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Xuenan Yang, Zihan Liu, Jingyu Li, Qiwei Xie. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage networks: Facilitating liquidity provision. Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 056103. https://doi.org/10.1103/PhysRevE.71.056103
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Fan, Y., Jiang, Y., Jin, P., & Mai, Y. (2023). CEO network centrality and bank risk: Evidence from US Bank holding companies. Journal of Corporate Finance. https://doi.org/10.1016/j.jcorpfin.2023.102501
Guo, F., Lyu, B., Lyu, X., & Zheng, J. (2025). Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum. Abacus. https://doi.org/10.1111/abac.12341
Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X. (2025). The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes. Journal of Systems Science and Complexity. https://doi.org/10.1007/s11424-025-4338-6
<!-- rendered-citations:end -->
