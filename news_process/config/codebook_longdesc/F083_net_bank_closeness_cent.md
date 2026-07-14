---
family_id: F083
columns:
- bank_closeness_cent
- bank_closeness_cent_sent
- bank_closeness_cent_win1
unit: 网络结构指标 (无量纲, 非负; 加权最短路径接近中心度, Wasserman-Faust 改进式; 加权距离=1/共现篇数, 边距可小于 1 故数值可超出 [0,1] 上界, 孤立银行取 0.0)
formula: "年度银行共现网络倒数图 G_inv (边距离 = 1/共现篇数) 上的接近中心度 clc = nx.closeness_centrality(G_inv, distance='weight'); WF 改进式 C(u) = [(r-1)/(N-1)] * [(r-1)/Σ d(u,v)], r=可达节点数含 u, N=节点全集; 孤立银行取 0.0。判据变体 {同篇无后缀 / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (阶段 40 panel_export_main 的 runner 网络溢出子步 7h-cent; 非独立注册阶段, 勿与 46_stata_export.py 混淆) ; news_process/pipeline/panel/export.py (英文标签)
upstream:
- 40_panel_yearly (bank-year 面板骨架)
- 篇章级 both-verified 展开帧 df_exploded (docid / target_bank / 内容 / 标题 / year)
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
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
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
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
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
  pages_or_artno: 056103
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
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: Bonacich, P.
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: 113-120
- doi: "10.1038/s41598-024-61511-7"
  type: journal
  authors: "Wu, Y., Ding, L., Li, N., & Yu, X."
  year: 2024
  title: "Unveiling the influence of global innovation networks on corporate innovation: evidence from the international semiconductor industry"
  venue: "Scientific Reports"
- doi: "10.1108/rbf-01-2025-0038"
  title: "Webs of influence: Do institutional networks enhance or distort stock price efficiency?"
  authors: "Iqbal, M. S., Bashir, Z., Usman, M., Sabir, S. A., & Sair, S. A."
  year: 2025
  venue: "Review of Behavioral Finance"
  type: "journal"
- doi: "10.1007/s44163-025-00350-5"
  title: "Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence"
  authors: "Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A."
  year: 2025
  venue: "Discover Artificial Intelligence"
  type: "journal"
new_dois:
  - "10.1038/s41598-024-61511-7"
  - "10.1108/rbf-01-2025-0038"
  - "10.1007/s44163-025-00350-5"
---

## CORE

【构念与来源】
bank_closeness_cent 是"年度银行共现网络"上的接近中心度 (closeness centrality), 度量一家银行在由媒体报道共同提及关系所织成的信息网络里, 到达其余全部银行的平均加权最短路径有多短。构念根源可追溯至 Freeman (1978) 对社会网络中心度族的概念澄清: 接近中心度刻画节点的"可达性、近便性"维度 — 一个到所有其他节点路径都短的节点, 处在信息可以最快扩散到达、也最快从各处汇聚而来的结构位置。把这一社会计量传统移植到本项目, 节点是每一自然年内出现于语料的银行, 边是"两家银行被同一批新闻报道共同提及"这一关系, 边权是共同提及的报道篇数。因此一家银行的接近中心度高, 意味着它与其他银行在媒体的共同关注结构中处于"近处": 无论是被直接一起报道, 还是经由若干中介银行的短链条相连, 它到网络中各家银行的加权距离都短, 从而在跨机构的信息传导上占据枢纽性、桥接性的近端位置。

数据来源上, 共现网络的原料是篇章级的 both-verified 展开帧 (df_exploded): 每篇通过验证的银行金科报道, 在其内幸存的 target_bank 集合内, 对每一无序银行对各计一次共现 (每篇每对 +1)。文章留篇口径遵循 2026-06-29 确立的 full-only 留篇门控 — 一篇报道是否算作"一篇银行金科报道"只由 llm_verified_full 为真决定; 因此喂给网络构造的文章全集即 full 轨留篇集, 与面板中 n_articles 一类分母的 full-only 口径严格一致, ctx/ss 轨在留篇层面降为 conditional-on-full 的子集, 不改变共现网的文章底盘。共现的判定主体是"银行∧银行", 与三轨文本 (full/ctx/ss) 所刻画的"银行∧金科"口径是两个正交的概念空间, 二者严禁混入同一个 over-identified Hansen J。构造边时刻意只把同一 docid 下真正通过验证的 target_bank 纳入, 已被验证拒绝的银行不进入共现集合, 从源头堵住 phantom 边 (幽灵边) 污染网络中心度 — 这是 omni-g-net-spill-01 边权口径统一后的既定防线。

须把本网络与银行间的产权、同业拆借或担保网络严格区分: 后者是资金或所有权的实际交易网, 本网络则是文本派生的"共同媒体注意力"网 — 边的生成机制是编辑与记者对哪些银行值得并置报道的联合选择, 承载的是信息环境与市场注意力的共享结构, 而非资产负债表上的实际敞口。两家银行被反复一起报道, 意味着分析师、投资者、监管者在处理其信息时倾向于将其并置、相互参照; 一家接近中心度高的银行因而处在银行业报道的"主流"与信息汇聚的近端, 其经营动态更容易被放进与全行业的比较框架中解读, 也更容易在同业冲击到来时被迅速联想、传导。接近中心度是 Freeman (1978) 界定的三种经典中心度 (度、介数、接近) 之一, 与度中心度所刻画的局部连接数量、介数中心度所刻画的中介桥接地位并列, 独占"到全网的整体近便性"这一构念切面; 在加权网络下其自然推广见 Opsahl 等 (2010), 亦与 Faust (1997) 对隶属网络中心度的处理最为贴切 — 因为报道-银行的二模隶属关系投影成的一模银行网, 正是隶属网络的典型形态。

【方法学与计算】
接近中心度在流水线阶段 40 (panel_export_main) 的 runner 网络溢出子步 (内部子步编号 7h-cent) 由 network_spillover.py 的 compute_bank_network_centrality 逐年计算; 须留意该子步在部分内部文档中曾以序号 46 标注, 但它不是独立注册阶段, 与注册 shim 46_stata_export.py (Stata 数据导出) 仅是编号巧合, 不可混淆。每一年先由 build_adjacency_matrix 构造对称加权邻接矩阵: 该年出现的银行取并集作为节点全集 (含孤立节点), 边权是共同提及篇数。随后派生两张图: 原始图 G (边权等于共现篇数, 供谱型、结构型指标使用) 与倒数图 G_inv (把每条边权取倒数 1/w 当作"距离", 供路径型指标使用)。接近中心度落在倒数图上计算, 调用 nx.closeness_centrality(G_inv, distance='weight'): 距离取共现篇数的倒数, 意味着被频繁一起报道的银行对之间"距离"短, 偶尔同现的对之间"距离"长; 于是一家银行若与众多银行经由高权重、短距离的边相连, 其加权最短路径之和小, 接近中心度就高。这正是 Opsahl 等 (2010) 所论"把边强度当作最短路径长度倒数"的加权中心度口径的直接落地, 也与 Barrat 等 (2004) 对加权复杂网络架构的刻画一脉相承 — 权重不只是二值连边, 而承载了共现强度的信息量。

逐年独立建网是刻意设计: 银行金科报道的强度与银行集合本身随年演进, 每年的共现网都在当年出现的银行并集上重建, 节点全集含当年虽出现却无任何合格共现的孤立银行 (它们在图中以孤立点入册, 接近中心度取 0.0)。为供离心率、电流介数、年内平均路径等仅在连通子图上有定义的指标使用, 每年还识别最大连通分量 (LCC, 由 nx.connected_components 取最大者); 但接近中心度不局限于 LCC, 而在全图上以改进式跨分量计算, 这也是它相对离心率、电流介数"稠密、原则上无 NaN"的根源。邻接矩阵以稀疏 lil_matrix 累加、对称化后转稠密数组; 原始图 G 保留共现篇数为权供谱型与结构型指标使用, 倒数图 G_inv 把每条边权取倒数当作距离供路径型指标使用, 二者节点集一致 (均补齐孤立节点)。接近中心度是 18 个节点级指标中的第 15 号, 归属 export 标注的 Part B; 家族整体每条判据轨落 33 列 (18 个节点级 + 10 个网络级 + 5 个 Gould-Fernandez 经纪角色), 接近中心度是其中唯一度量"整体近便性"的节点级路径型指标。

networkx 默认采用 Wasserman-Faust 改进式 (wf_improved=True), 对断连图作可达比例校正: 节点 u 的接近中心度等于 (可达节点数减一) 除以 (加权距离之和), 再乘以 (可达节点数减一) 除以 (全体节点数减一)。因而处于非巨分量的银行不会被简单地当作"无穷远"从而与巨分量银行无从比较, 而是按其可达邻域规模被线性缩放; 完全孤立的银行 (该年无任何共现) 的接近中心度取 0.0, 借 clc.get(b, 0.0) 兜底。这使接近中心度成为一个"稠密"指标 — 对全部银行都有定义、原则上不产生 NaN, 不像离心率 (bank_eccentricity) 或电流介数 (bank_cfbetween_cent) 仅在最大连通分量上有值、分量外置 NaN, 也不像特征向量中心度 (bank_eigen_cent) 对微小分量置 NaN。计算得到的逐年逐行结果并入银行-年面板; 判据分轨的落列按 _expected_suffix 映射 (article 对应无后缀、win1 对应 _win1、sent 对应 _sent) 严格配对, 错配即抛错。33 个网络结构指标基名的唯一事实源是 NETWORK_METRIC_BASES 常量, stata_export 的判据标签机械块与 gate 测试均从此 import 复用以防漂移。export.py 给本列的英文标签是 "Co-mention Closeness Centrality (Freeman 1979)", 其构念本源即 Freeman (1978) 的接近中心度定义。就确定性而言, 生产源码明确将 bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 三列标注为受 BLAS 浮点漂移影响、跨次重建非逐位可复现; 接近中心度不在此清单内, 其 Dijkstra 加权最短路径求解不经稠密特征分解, 在钉死 PYTHONHASHSEED 与全 BLAS 线程为 1 的受控环境下逐位可复现, 因此在 golden 验零漂移时不属需按全名排除的漂移列。

【文献定位】
接近中心度的方法学定位横跨社会网络计量与金融网络两支文献。计量本源方面, Freeman (1978) 奠定接近中心度的构念, Opsahl 等 (2010) 把度与最短路径中心度推广到加权网络、给出"边强度取倒数为距离"的加权口径, Boldi 与 Vigna (2014) 从公理化视角比较各类中心度、指出接近中心度与调和中心度在断连图上的行为差异, Newman (2005) 提出基于随机游走的介数中心度作为路径型度量的补充参照, Faust (1997) 专论隶属 (affiliation) 网络中的中心度 — 本项目的银行共现网正是由"报道-银行"二模隶属关系投影而来的一模网络, Faust 的处理与之最贴切。Nezami 等 (2025) 的元分析系统汇总网络中心度与企业绩效的关联证据 (该条在注册表中不背书 bank_clustering, 此处仅援引其对中心度-绩效一般关系的综述结论)。金融网络应用方面, Yu 等 (2024) 与 Xu 与 Zhao (2024) 分别论证金融网络中的节点中心度对信息扩散、资产定价与价格预测的作用, Jackson 与 Pernoud (2021) 综述金融网络中的系统性风险 — 中心度常被用作系统重要性代理, Grieser 等 (2022) 则实证网络位置对公司财务政策的影响。这些工作共同支撑了"银行在媒体共现网络中的接近中心度可能与其信息环境、融资与经营结果相关"的研究假设。这些应用文献的共同启示是: 中心度并非纯拓扑玩具, 而在信息扩散速度、系统重要性与政策传导上具有可检验的经济含义 — 一家在共现网络中接近中心度高的银行, 其正负面消息更可能被快速并置传播、纳入同业比较, 从而与其被市场关注的程度乃至融资成本相关联; Yu 等 (2024) 关于中心度与信息扩散、资产定价的证据, 与 Nezami 等 (2025) 元分析归纳的中心度-绩效正向关联, 为这一传导链条提供了跨情境的经验支撑, 而 Jackson 与 Pernoud (2021) 则从系统性风险视角提示了高中心度节点在冲击传染中的放大作用。此外, Wu, Ding, Li, & Yu (2024, Scientific Reports) 用企业间创新协作网络的中心度 (含接近中心度) 度量企业获取网络信息的便利程度并检验其对创新绩效的影响, 为本项目把媒体共现网络接近中心度解读为信息可达性代理提供了跨情境实证参照。Iqbal, Bashir, Usman, Sabir, & Sair (2025, Review of Behavioral Finance) 用机构股东共同持股网络的介数与接近中心度区分高连通与低连通机构, 检验网络位置是否带来信息优势并影响股价效率。Alamsyah, Ramadhani, Kristanti, Nasution, Mohamad, Sokkalingam, Widiyanesti, & Saputra (2025, Discover Artificial Intelligence) 基于新闻文本构造公司共现网络并结合情感分析, 考察行业归属与新闻共现结构对企业中心性地位及股价关联的影响。

【识别策略定位】
把网络位置 (接近中心度) 用作处理或暴露变量, 直面 Manski (1993) 揭示的反射问题 (reflection problem)。Manski 把一家银行结果对其同伴的依赖拆为三类难以互斥的混淆源: 内生效应 (同伴的结果反过来影响本行结果)、外生或情境效应 (同伴的可观测特征影响本行结果)、以及相关效应 (同伴与本行共处同一不可观测环境, 因而结果相似却非彼此因果)。在线性均值模型里, 内生效应与情境效应的系数因同伴均值互为镜像而无法分离 — 这正是"反射"的本义; 相关效应则与真正的溢出彼此难辨。接近中心度作为一个刻画银行在共现网络中整体近便性的结构位置摘要, 既可能经由信息可达性驱动其融资、经营结果, 也可能与那些同时决定它被频繁共同提及的不可观测特征 (资产规模、系统重要性、地域曝光度) 相混淆, 因此把它当作因果处理必须直面这三重内生性, 不可回避。

Bramoullé、Djebbari 与 Fortin (2009) 证明, 当网络含非传递三元组 (朋友之友并非都互为朋友, 亦即邻接矩阵 W 与其幂 W² 线性无关) 时, 网络结构本身就能为同伴效应提供识别: 二阶、三阶邻居的特征可充当工具, 把内生效应从情境效应中分离, 从而破解线性均值下的共线。本项目的银行共现网天然满足这一条件 — 两家银行的共同报道伙伴并不完全重合, 偏重叠的邻域结构保证了 I、W、W² 的线性无关, 为经由高阶邻居的外生变异留出空间。Bramoullé 等 (2020) 的综述系统梳理了网络同伴效应的识别工具箱及其对网络测量误差与内生成网的敏感性; Boucher、Rendall、Ushchev 与 Zenou (2024) 迈向同伴效应一般理论的工作则放松线性均值假设, 容纳非线性、异质的同伴影响, 厘清了不同网络位置度量 (含接近这类整体近便性度量) 进入结构模型的方式与识别条件。Grieser 等 (2022) 在公司财务政策上的网络实证, 正是这一识别路线在企业金融情境中的落地范例, 为"网络位置具有可检验经济含义"提供了方法学参照。

就本项目的定位而言, 网络结构指标不承担主线论文的 headline treatment, 而是作为"规格稳健性并排"的替代结构位置度量; 接近中心度作为路径型近便性度量, 与度、强度、特征向量等局部或谱型位置度量互为佐证。项目的 IV 扩展引擎 (iv_extensions.py) 提供同组留一均值、广义 Bartik 与媒体来源 house-style 暴露三套构造, 用以处理网络型暴露的内生性; 接近中心度的效度可在这套框架下被间接探查, 但它本身不承担因果识别负荷。判据敏感性三变体 (同篇、±句窗、严格同句) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同判据混进同一个 over-identified Hansen J; 且这一族属规格稳健性并排 (镜像政治词权重、词典消融先例), 不设跨模型 FWER 模板 — 因为项目内的 rwolf 跨模型先例仅覆盖同一构念的替代 headline 测量, 而判据变体、W 轨、行业冲击三轨这类规格稳健性族不适用该 FWER 框架。因此在解读上应把接近中心度当作对"信息网络位置"这一潜在机制的多角度佐证之一, 与度、强度、特征向量等局部或谱型位置度量相互印证, 而非孤立地赋予因果解释。

【与相邻测度的构念区分】
接近中心度须与家族内外的相邻测度严格区分, 以免在建模时误当冗余或重复计入。与调和中心度 (bank_harmonic_cent) 的区分最需强调: 两者都落在倒数图 G_inv 上, 但接近中心度是"距离之和的倒数" (先对可达节点的加权最短路径求和, 再取倒数), 调和中心度是"距离倒数之和" (先对每条最短路径取倒数, 再求和)。Boldi 与 Vigna (2014) 从公理化视角指出, 调和中心度对断连更稳健 (不可达节点自然贡献 1/∞ 即 0, 无须特殊处理), 而接近中心度靠 Wasserman-Faust 改进式对可达比例作校正来处理断连; 二者在连通图上高度相关却不冗余 — 调和更偏重近邻的边际贡献 (近处节点权重大), 接近强调整个可达集的平均近便性。

与介数 (bank_between_cent)、电流介数 (bank_cfbetween_cent) 的区分在构念方向: 接近度量"到所有人都近"的可达性, 介数度量"处在别人最短路径之间"的中介、桥接地位, Freeman (1978) 明确区分二者; Newman (2005) 进一步给出基于随机游走的介数变体 (电流介数), 以电导语义捕捉非最短路径上的信息流。二者刻画的是"枢纽"与"桥梁"两种不同的结构权力, 与接近的"近端汇聚"正交。与度、强度中心度 (bank_degree_cent、bank_strength_cent) 的区分在尺度: 度是局部的直接共现计数, 强度是加权直接共现之和, 接近是全局的路径可达性 — 一家银行可能直接共现很多 (度高) 却因其邻居都处网络边缘而接近中心度不高; 反之一家度不高的银行若恰好桥接若干高密社群, 其接近可以很高。强度中心度按年最大加权度归一 (每年最大恒为 1.0), 是纯乘性年重标度; 接近中心度的改进式归一则是对可达比例的结构性校正而非除以年特定标量, 前者可部分随 (N-1) 缩放、后者是纯年重标度, 二者的跨年可比性质因而并不一致。

与特征向量、子图中心度 (bank_eigen_cent、bank_subgraph_cent) 这类谱型度量的区分在计算基底与可比性: 特征向量中心度 (Bonacich 1972) 是"重要性递归" — 与重要邻居相连者更重要, 按连通分量分别作 L2 归一、仅分量内可比且微小分量置 NaN; 子图中心度 (Estrada 与 Rodríguez-Velázquez 2005) 以邻接矩阵的加权闭合游走 (矩阵指数对角元) 度量节点参与内聚子群的程度。两者均由谱分解驱动, 强调"与谁相连"的质量; 接近中心度则由 Dijkstra 加权最短路径驱动, 强调"到全网多近"的距离, 经改进式跨分量给出可达比例加权的有限值, 无 NaN 稀释。与聚类、核数 (bank_clustering、bank_coreness) 的区分在层级与语义: 聚类系数 (Watts 与 Strogatz 1998) 度量 ego 邻域的三元闭合密度 (朋友之间是否也互为朋友), 是局部密度而非位置或可达性度量; 核数 (Seidman 1983) 是 k-core 嵌套内聚核的整数级会员身份, 纯拓扑、离散。接近中心度既非密度亦非离散会员, 而是连续的路径可达性标量。此处须留意一个确定性对照: bank_clustering 是源码明确标注的 BLAS 浮点漂移列 (跨次重建非逐位可复现), 而接近中心度的 Dijkstra 求解不经稠密谱分解, 不在漂移清单内, golden 验零漂移时无须按名排除。

与经纪角色 (Gould-Fernandez gf_* 五列) 的区分在分组依赖: GF 经纪 (Gould 与 Fernandez 1989) 按节点的组归属把中介行为拆为协调者、守门人、代表、联络人、巡回经纪等角色, 依赖外生的节点分组; 接近中心度不区分角色类型、不依赖分组, 是无分组的整体近便性标量, 语义更基础、覆盖更全。最后, 接近中心度 (节点级) 与网络级年指标 (如 net_avg_path_yr 年内平均路径长度) 构念相关却层级不同: 前者是银行级位置度量、进回归后保留截面变异, 后者是整张年网络的宏观拓扑摘要, 在含年固定效应的模型中会被年 FE 完全吸收而不可识别, 二者不可互替。加权距离取 1/共现次数的口径亦区别于纯拓扑跳数, 承接 Opsahl 等 (2010) 与 Barrat 等 (2004) 的加权网络传统。

【已知局限与稳健性梯子】
第一, 超边膨胀风险: 一篇提及 N 家银行的榜单式或批量监管通报报道会贡献 C(N,2) 条等权边, 大-N 文章可凭边数膨胀主导网络结构, 使频繁进入大名单的银行接近中心度被抬高; 源码保留 hyperedge_normalize (Newman 度守恒归一) 作预留参数, 但生产口径尚未接线、默认仍每对 +1 (golden-safe), 故该膨胀在当前列值中未被中和, 解读时须留意。第二, 跨年可比性: 网络逐年重建, 随年内银行数 N 与网络密度变化, 接近中心度的水平会漂移, 改进式对 (N-1) 的归一只部分缓解密度变化, 因此本列更宜作年内相对位置或行内变化解读, 慎作跨年绝对水平比较。第三, 改进式缩放语义: 非巨分量银行按可达邻域规模线性缩小, 应理解为"可达性加权的近便性"而非纯距离倒数。第四, 加权距离取共现次数倒数使极端高共现对产生极短距离, 在原始计数上单调、未作 winsorize, 分布右尾偏重。稳健性梯子即判据敏感性三变体 (同篇无后缀、±win_radius 句窗 _win1、严格同句 _sent): 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J, 且不设 FWER 模板。确定性上本列不在 BLAS 漂移列清单内, 受控环境逐位可复现。开发期 T=2 试跑面板上网络稀疏、多数银行接近中心度低或为 0 属预期退化, 生产 T=18 全量语料方有实质截面变异。第五, 判据分轨路径下 hyperedge_normalize 尚未接线, 与 article 主路径同为预留参数, 在分轨轨上直接被守卫拒绝 (传 True 即抛错), 以防三判据轨在无告警下口径分叉; 因此三条判据轨在超边归一处理上口径一致 (均为每对每篇 +1), 判据间的差异纯粹来自邻接判据的严格度, 这保证了判据敏感性比较的干净可解释。第六, 本列作为稠密指标虽避免了 NaN 稀释, 但在全孤立年或极稀网络下会退化为近乎常数列 (大量 0 值挤占), 零方差或近零方差进回归会被固定效应吸收或抬高多重共线, 须在生产 T=18 的密度下评估其有效变异是否充足, 必要时改用年内相对秩或行内变化形式。

## VAR: bank_closeness_cent

【变体差分】
本列是接近中心度家族的 canonical 无后缀列, 对应 article 判据 (criterion='article', 落列后缀为空字符串) — 即"银行∧银行同篇共现": 只要两家银行出现在同一篇 both-verified 报道中 (文档级共现), 无论它们在文中相距多远, 就在该年网络里连一条边、边权累计该对的共同提及篇数。这是本项目现行的生产 canonical 口径, 也是三条判据变体中边集最宽的一条 — 相较 _win1 (要求两家银行落在 ±win_radius 句窗内) 与 _sent (要求严格同句), 同篇判据保留最多的边, 因而网络最稠密、连通性最强, 银行的加权最短路径之和普遍更小、接近中心度整体偏高, 孤立银行更少。计算上, 同篇邻接矩阵由 build_adjacency_matrix 走 docid 主路径构造: 对每个 docid 组内幸存的 target_bank 集合逐无序对 +1, 每篇每对恰计一次, 已被验证拒绝的银行不入边 (phantom 边防线); 随后在倒数图 G_inv 上以 nx.closeness_centrality(G_inv, distance='weight') 计算, 采用 Wasserman-Faust 改进式处理断连, 孤立银行取 0.0。

须强调本列后缀语义的两重正交性, 以免建模误用。其一, 判据后缀 (无后缀、_win1、_sent) 刻画的是"银行∧银行"邻接的判据严格度, 与三轨文本后缀 (_full、_ctx、_ss) 所刻画的"银行∧金科"文本范围是两个完全独立的概念空间, 二者不可字符串类比、更不可混入同一个 over-identified Hansen J; 本列作为 canonical, 其对应的稳健性对照是 _win1 与 _sent, 而非任何 _ctx、_ss 文本轨。其二, 三条判据变体各自 just-identified 并排、互为稳健性、不分主次, 检验主结论是否被"同现邻近度阈值"这一构造选择驱动; 该族属规格稳健性并排 (镜像政治词权重、词典消融先例), 不设跨模型 FWER 模板。就确定性而言, 本列的 Dijkstra 加权最短路径不经稠密谱分解, 不属源码标注的 BLAS 漂移三列 (clustering、cfbetween、harmonic), 在钉死随机种子与 BLAS 线程后逐位可复现, golden 验零漂移时无须按名排除。解读上, 本列高值表示该银行在媒体共同关注的信息网络中处于近端枢纽位置 — 其消息常与众多同业被并置讨论、经短链条即可触达全网, 契合 Freeman (1978) 与 Opsahl 等 (2010) 所界定的加权接近中心度构念。

就计算流程而言, 本列在阶段 40 的 runner 网络溢出子步逐年建网后, 于 build_adjacency_matrix 派生的双图体系中落在倒数图 G_inv 上求解: 原始图 G 保留共现篇数为权供谱型、结构型指标 (度、强度、特征向量、子图、聚类等) 使用, 倒数图 G_inv 把每条边权取倒数 1/w 当作"距离"供路径型指标 (介数、调和、接近、离心率) 使用, 两图节点集一致 (均补齐当年出现却无合格共现的孤立银行)。接近中心度是 18 个节点级指标中源码编号第 15 号, 归属 export 标注的 Part B; 家族整体每条判据轨落 33 列 (18 个节点级 + 10 个网络级 + 5 个 Gould-Fernandez 经纪角色), 本列是其中唯一度量"整体近便性"的节点级路径型指标。因同篇 canonical 边集最宽、网络最连通, 采用 Wasserman-Faust 改进式 (可达节点数减一, 除以加权距离之和, 再乘以可达比例) 后, 本列成为家族中"最稠密"的一列 — 对全部银行都有定义、原则上不产生 NaN, 不像离心率 (bank_eccentricity) 或电流介数 (bank_cfbetween_cent) 仅在最大连通分量上有值、分量外置 NaN, 也不像特征向量中心度 (bank_eigen_cent) 对微小分量置 NaN; 但稠密性也意味着在极稀年份本列可能被大量 0 值挤成近乎常数, 须结合生产 T=18 密度评估其有效变异。判据分轨的落列按 _expected_suffix 映射 (article 对应无后缀) 严格配对, 错配即抛错; 33 个基名的唯一事实源是 NETWORK_METRIC_BASES 常量, stata_export 判据标签块与 gate 测试均从此 import 复用防漂移。

就取值分布而言, 同篇 canonical 因边集最宽, 其接近中心度在同一年的三判据中通常最高、孤立银行最少; 这也意味着它对"同文但语义无关的偶然并置" (例如年度榜单、综述性长文把多家银行罗列在一起却各说各事) 最不设防, 超边膨胀风险在本列上体现得最充分, 解读高值时须结合该银行是否频繁进入大名单来判断其是否真反映信息近便性、抑或仅是被批量罗列的副产物。相对地, _win1 与 _sent 通过要求句级邻近, 过滤掉这类松散并置, 因而三判据的对照本身就是对"同现邻近度"这一构造假设的稳健性检验: 若主结论在同篇、±句窗、严格同句三种边定义下方向与显著性一致, 即可证其不被邻近度阈值的具体取值所驱动。本列作为 canonical 承担基准角色, 其余两轨作为收紧对照, 三者语义互补而非替代, 不得任取其一冒充另一者、更不得把不同判据的接近中心度并入同一个 over-identified Hansen J 或据此计算跨判据 FWER。最后须再次澄清"canonical"与"无后缀"仅是历史命名与落列约定的产物, 并不意味着同篇判据在方法论上优于 _win1 或 _sent — 三者是并排的规格选择, 生产口径以同篇为默认仅因其边集最全、退化最少, 而非其更"正确"。

## VAR: bank_closeness_cent_sent

【变体差分】
本列是接近中心度的严格同句判据变体 (criterion='sent', 落列后缀 _sent), 是三条判据中最严的一条。它把"银行∧银行共现"收紧为"两家银行必须出现在同一个句子内"才连边: 构造时走 build_adjacency_matrix 的判据分轨路径, 在每个多银行 docid 组内以 prepend_title 拼接后的文本 (标题作为第 0 句, 镜像 stage 13 的 match_in_title 口径) 重扫, 调用 core/text/entity_context 的 map_bank_sentence_positions 定位各银行的句位置, 再由 bank_pairs_within_sentence_window 以 win_radius=0 (严格同句, 与 win1 的关键差别正在于半径被强制取 0) 枚举同句银行对, 每对每篇 +1。因判定主体是银行∧银行且原语与审计脚本共用 (审计等于生产), 同样接入 stage 11/13 共用的否定与短名排除事实源, 防"涉农行业→农行"一类假阳性; 已被验证拒绝的银行不入参、不可能成边。相较同篇 canonical 与 ±句窗 _win1, 严格同句边集最稀, 网络最松散、孤立银行更多, 接近中心度整体偏低、更多银行取 0.0。

本列的角色是判据敏感性稳健性轨: 与无后缀 canonical、_win1 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J, 且该族不设 FWER 模板。须重申判据后缀 _sent 与三轨文本后缀 _ss 是两个正交概念空间 — 前者是"银行∧银行"同句邻接, 后者是"银行∧金科"同句文本范围, 不可混淆。其倒数图接近中心度算法与 canonical 完全一致 (仅邻接边集因判据收紧而变稀), 同样采用 Wasserman-Faust 改进式、孤立银行取 0.0, 亦不在 BLAS 漂移列内。开发期 T=2 上严格同句网络极稀、多数格取 0 属预期退化, 生产全量方有意义。

## VAR: bank_closeness_cent_win1

【变体差分】
本列是接近中心度的 ±句窗判据变体 (criterion='win1', 落列后缀 _win1), 严格度介于同篇 canonical 与严格同句 _sent 之间。它要求"银行∧银行共现"发生在 ±win_radius 个句子的窗口内才连边: 构造走判据分轨路径, 在多银行 docid 组内以 prepend_title 文本 (标题为第 0 句, 镜像 stage 13 match_in_title) 重扫定位句位置, 再以 win_radius (非零) 枚举窗口内银行对。此处 win_radius 取自 config/panel.yaml::network_criteria.win_radius (默认 1), 它与 config/filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科硬过滤所用) 是两个不同的配置键、互不联动 — 这是极易误连的雷区, 二者虽都名为"句半径"却服务于正交的判定轴, 切勿把 stage 13 的银行∧金科半径与本处的银行∧银行半径当作同一参数。相较同篇口径, ±句窗剔除了"同文但相隔甚远"的松散共现, 保留篇内语义邻近的银行对, 边集比同篇窄、比严格同句宽, 网络稠密度与接近中心度水平居中。

本列同为判据敏感性稳健性轨: 与无后缀 canonical、_sent 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J, 不设 FWER 模板。判据后缀 _win1 与三轨文本后缀 (_full/_ctx/_ss) 属正交概念空间, 不可类比或混用。倒数图接近中心度算法与 canonical 一致 (仅邻接边集因 ±句窗判据而变), 采用 Wasserman-Faust 改进式、孤立银行取 0.0, 不在 BLAS 漂移列内, 受控环境逐位可复现。开发期 T=2 网络稀疏、结果退化属预期, 生产 T=18 方有实质截面变异。

<!-- rendered-citations:begin -->
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 23619. https://doi.org/10.1103/PhysRevE.71.056103
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Wu, Y., Ding, L., Li, N., & Yu, X. (2024). Unveiling the influence of global innovation networks on corporate innovation: evidence from the international semiconductor industry. Scientific Reports. https://doi.org/10.1038/s41598-024-61511-7
Iqbal, M. S., Bashir, Z., Usman, M., Sabir, S. A., & Sair, S. A. (2025). Webs of influence: Do institutional networks enhance or distort stock price efficiency?. Review of Behavioral Finance. https://doi.org/10.1108/rbf-01-2025-0038
Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A. (2025). Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence. Discover Artificial Intelligence. https://doi.org/10.1007/s44163-025-00350-5
<!-- rendered-citations:end -->
