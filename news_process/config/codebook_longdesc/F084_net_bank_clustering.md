---
family_id: F084
columns:
- bank_clustering
- bank_clustering_sent
- bank_clustering_win1
unit: 网络结构指标 (无量纲, 取值 [0,1])
formula: "bank_clustering = nx.clustering(G, weight='weight') 上银行节点的加权局部聚类系数; G = 年度银行共现加权无向图 (节点=当年幸存 target_bank, 边=两行共现, 边权=同语境共现篇数); 判据变体 {同篇 (无后缀) / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (build_adjacency_matrix 建图) ; news_process/pipeline/panel/codebook.py (标签推断)
upstream:
- "40_article_bank_level.parquet (篇章级展开帧 df_exploded: docid / target_bank / year / 内容 / 标题)"
- config/panel.yaml::network_criteria (win_radius=1, match_in_title=true)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1371/journal.pone.0327421"
  type: "journal"
  authors: "Amancio, D. R., Machicao, J., & Quispe, L. V. C."
  year: 2025
  title: "Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis"
  venue: "PLOS ONE"
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
  pages_or_artno: 103223
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: 2693
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
- doi: 10.1023/B:CMOT.0000032580.12184.c0
  type: journal
  authors: Robins, G., & Alexander, M.
  year: 2004
  title: "Small worlds among interlocking directors: Network structure and distance in bipartite graphs"
  venue: Computational & Mathematical Organization Theory
  vol: 10
  issue: 1
  pages_or_artno: 69-94
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
  venue: The Review of Economic Studies
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
- doi: "10.1016/j.procs.2023.08.056"
  title: "Communities of co-occurrence network of financial firms in news"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  venue: "Procedia Computer Science"
  type: "journal"
- doi: "10.3390/risks13110210"
  title: "A Bibliometric Analysis on Network-Based Systemic Risk"
  authors: "Rojas Rincón, J. S., Acosta-Prado, J. C., & Castellanos Narciso, J. E."
  year: 2025
  venue: "Risks"
  type: "journal"
  one_sentence_zh: "对2020–2025年网络化系统性风险文献做文献计量分析,印证拓扑结构分析在解释机构间关联与风险扩散中的持续活跃度。"
- doi: "10.1371/journal.pone.0284861"
  title: "Systemic risk prevention policies targeting systemically important banks: Does clustering pattern matter?"
  authors: "Zhu, B., Hu, X., Deng, Y., & Lin, R."
  year: 2023
  venue: "PLOS ONE"
  type: "journal"
  one_sentence_zh: "用网络优化模型证明系统重要性银行的聚类模式与系统性风险传染密切相关,聚类程度更高的网络系统性风险显著更高。"
new_dois:
- "10.1371/journal.pone.0327421"
- "10.1016/j.procs.2023.08.056"
- "10.3390/risks13110210"
- "10.1371/journal.pone.0284861"
---

## CORE

对文本共现网络的聚类系数等统计性质做系统分析,为本族由报道共现构图并计算聚类系数的方法学提供了共现网络指标行为的旁证。

【构念与来源】
bank_clustering 是「银行共现网络结构指标」家族 F084 的 canonical 列, 度量每家目标银行在其所处「年度银行共现网络」中的加权局部聚类系数 weighted local clustering coefficient, 取值域 [0, 1], 无量纲。构念上, 聚类系数回答的是一个关于「三元闭合」的问题: 与某家银行 v 在同一新闻语境里被一同提及的那些「邻居银行」, 它们彼此之间是否也倾向于被一同提及。若 v 的邻居两两之间高度互连 (三角形稠密), 聚类系数趋近 1, 表明 v 嵌在一个内聚、抱团的媒体叙事簇里; 若 v 的邻居彼此互不相连, 使 v 像一根连接多个互不相识群体的辐条, 聚类系数趋近 0, 表明 v 处于一个开放、桥接式的结构位置。这一构念直接继承自 Watts 与 Strogatz (1998) 在提出小世界网络时定义的聚类系数 —— 网络科学中刻画「局部内聚性 / 传递性」的经典原语 —— 并沿 Freeman (1978) 奠定的社会网络结构测量传统, 把「谁与谁一同出现在新闻里」翻译为可计算的图结构位置。它与刻画「谁最居中」的中心度族属于两条正交的结构语义线, 后者的构念梳理正源自 Freeman (1978) 对中心度概念的澄清。用大白话说, 聚类系数量的不是「这家银行有多红」, 而是「常和这家银行一起上新闻的那几家银行, 它们彼此之间是不是也常常一起上新闻」: 若是, 这家银行就处在一个抱成一团的媒体小圈子中央; 若不是, 它就像一座横跨几个互不往来圈子的独木桥。

在银行业媒体语境里, 两家银行被一同提及往往折射出三类共同暴露: 共同的事件冲击 (同一波监管通报、同一轮金融科技浪潮、同一场市场波动被并列报道)、竞争性并置 (同类同规模银行在业务对比或榜单中被并排点名)、以及体系性关联 (风险传导、担保链、同业业务在报道中被牵连叙述)。因此银行共现网络本质上是一张「媒体注意力结构图」, 而聚类系数在其中读出的是一家银行媒体邻域的内聚程度: 一个由若干城商行组成、总被放在一起报道的区域性簇, 其成员聚类系数偏高; 一家既进国有大行叙事、又进金融科技合作叙事、还进区域风险叙事的银行, 若这三组邻居彼此不重叠, 则聚类系数偏低、桥接性强。聚类系数是 2026-06-21 网络指标扩展后 33 个结构指标中的节点级第 7 项 (Part A, 源码 SSOT NETWORK_METRIC_BASES 元组顺序: 度、强度、特征向量、Katz、子图、电流介数之后), 与度、强度、介数、特征向量、Katz、子图、电流介数、约束、hub 等同族并列, 各自量的是「重要 / 居中 / 桥接 / 内聚」的不同侧面。

数据来源为篇章级展开帧 df_exploded, 每行 = 一篇报道 × 一家被判定命中的目标银行, 携 docid、target_bank、year、内容、标题等列。网络节点全集 = 该年度在留篇后仍幸存的目标银行 target_bank; 网络的边 = 两家银行在同一新闻语境内共现。canonical 口径 (bank_clustering 无后缀列) 采用「同篇共现」判据: 同一 docid 报道内同时幸存的任意两家银行之间连一条边, 边权 weight = 该两家银行同篇共现的报道篇数 (每篇每对 +1, 对称累加)。因此这是一张年度重建、以共现频次为权重的加权无向图。底层报道全集继承 full-only 留篇口径 (2026-06-29): 一家银行-年只有在该年至少有一篇报道通过 full 轨留篇门控时才进入当年网络, 故网络的节点 / 边总体与主面板 n_articles 分母口径严格一致; 判据分轨只收紧边集, 绝不改动节点全集。

【方法学与计算】
生产实现落在 pipeline/panel/network_spillover.py。整个网络是「逐年重建」的: 每个日历年独立建一张图, 年与年之间不连边, 因此本族提供的是年度网络的重复截面, 而非跨年的动态网络 —— 时间维度由银行-年面板承载, 网络本身只刻画当年的共现结构。对每个年度, build_adjacency_matrix 先按判据构造对称邻接矩阵 adj_df (index 与 columns 均为该年幸存银行的排序列表), 再由 compute_bank_network_centrality 用 networkx 建图: G = nx.Graph(), 对 adj_df 上三角每个正元素 add_edge(b1, b2, weight=共现次数), 并把所有幸存银行 (含孤立节点) 显式 add_node 加入图, 保证节点全集与面板对齐。函数入口设有 criterion 与 suffix 的配套守卫 (article↔无后缀 / win1↔_win1 / sent↔_sent), 错配即 raise, 杜绝判据与列名后缀无声分叉。聚类系数由 cc = nx.clustering(G, weight='weight') 一次算出, 落列 metrics[b]['bank_clustering'] = cc.get(b, 0.0) —— 即度数小于 2 或未进入任何三角计算的节点 (孤立点、悬挂点) 取 0.0 而非缺失。由于 networkx 对度数小于 2 的节点定义聚类系数为 0, 稀疏年份里大量银行会落在 0 值。须注意同一模块还会另建一张倒数权重图 G_inv (边权取 1/共现次数) 供介数 / 调和 / 接近度等路径型指标使用, 并对最大连通分量 (LCC) 单独取子图供电流介数、离心率、平均路径长度使用; 但聚类系数刻意在原始加权图 G 上、对全图所有连通分量一并计算, 不走倒数图、也不限于 LCC —— 这与它「纯局部三角内聚」的构念定位一致。

计算采用的是加权版聚类系数: 对节点 v, 遍历所有以 v 为顶点、且三条边俱存在的三角形, 每个三角形按其三条边权先除以全网最大边权、再取三者的几何均值 (立方根乘积) 计一份「三角形强度」, 累加后除以 v 的度数所允许的三角形对数 k(k-1)/2 (k 为 v 的度), 得到落在 [0, 1] 的加权聚类值。这一「三角形强度」式加权推广, 与 Watts 与 Strogatz (1998) 的无权原始定义在无权图上退化一致, 又能吸收「共现越频繁、闭合越强」的加权信息; 它与 Barrat 等 (2004) 在刻画复杂加权网络架构时提出的、以节点强度归一的另一支加权聚类系数, 属同一问题的不同解, 二者取舍是加权网络测量文献长期讨论的建模选择, 本项目采用 networkx 内置的强度几何均值口径, 亦呼应 Opsahl 等 (2010) 对加权网络指标须显式声明权重语义、不可与无权口径混用的方法学告诫 (同一模块的 bank_strength_cent 即直接实现该文的加权度)。重要确定性注记: bank_clustering 与同族路径型指标 bank_cfbetween_cent、bank_harmonic_cent 一样, 受底层 BLAS 浮点求和次序影响, 跨次重建非逐位可复现 (memory: panel-3-network-cols-nondeterministic); 三判据各自都带一份, 故全套 9 列 (3 基名 × 无后缀 / _win1 / _sent) 在 golden 零漂移校验时须按全名 drop 排除, 稳健性叙事以「符号与秩序稳健」而非「逐位复现」为准绳。

【文献定位】
把新闻文本共现重建为金融网络、再以网络结构位置解释银行行为与绩效, 正是近年金融网络实证的活跃前沿。Li 等 (2026) 直接从文本风险披露中抽取金融网络结构与连通性, 与本项目「由报道共现建图」的思路同源, 是最贴近本族数据生成机制的方法学参照。Jackson 与 Pernoud (2021) 的系统性风险综述为「网络拓扑塑造金融体系脆弱性」提供了总纲, Duarte 与 Eisenbach (2021) 则以火线抛售外溢给出网络结构放大冲击的具体机制, 二者共同说明银行网络的局部结构 (含内聚簇) 具有实质的风险含义。就中国银行业语境, Wang 等 (2020) 刻画了金融危机与刺激计划下中国担保网络的演化, Gao 等 (2022) 论证了所有权网络在银行信贷中的信息角色, Fang 等 (2024) 更把媒体情绪、存款稳定与银行系统性风险在中国样本上串起 —— 三者支撑「银行确实嵌在可观测的网络结构中, 且该结构对信贷 / 风险有实质含义」这一前提, 也直接对接本项目由中文银行新闻建网的语料基础。在方法与构念联结上, Yu 等 (2024) 证明网络中心度经由信息扩散进入资产定价, Grieser 等 (2022) 用网络结构解释公司财务政策, Nezami 等 (2025) 以元分析汇总网络中心度与企业绩效的整体关联。这些工作合起来把 bank_clustering 定位为: 一个从媒体共现图上读出的、刻画银行局部结构内聚性的结构变量, 可作解释变量进入银行-年回归。值得强调的是, 上述文献多聚焦中心度与整体连通, 对「局部内聚 / 三元闭合」这一节点级结构侧面着墨较少, 恰是本列力图补足的构念缝隙, 也是它与既有中心度测度并排、互为稳健性而不彼此替代的意义所在。Yang 等 (2023, Procedia Computer Science) 用新闻文本构建中国金融机构共现网络并做社区/聚类检测, 与本族由银行报道共现建图、以聚类系数刻画媒体邻域内聚性的构造思路直接同源。Rojas Rincón 等 (2025, Risks) 对2020–2025年网络化系统性风险文献做文献计量分析, 印证拓扑结构分析在解释机构间关联与风险扩散中的持续活跃度。Zhu 等 (2023, PLOS ONE) 用网络优化模型证明系统重要性银行的聚类模式与系统性风险传染密切相关, 聚类程度更高的网络系统性风险显著更高。

【识别策略定位】
在计量识别上, 局部聚类 / 三元闭合结构不仅是描述量, 更是识别同群效应 peer effects 的关键几何。Manski (1993) 的反射问题把同群相关拆为三重来源: 内生效应 (endogenous, 个体行为受同群行为影响)、外生 / 情境效应 (contextual, 个体行为受同群外生特征影响) 与关联效应 (correlated, 同群因共处同一环境而行为相似); 当个体所处群体完全重叠、且三重效应线性叠加时, 内生效应与情境效应在期望上退化为同一线性项而无法分离, 这正是反射问题的核心。Bramoullé 等 (2009) 证明, 只要网络存在 intransitive triads (A 与 B 相连、B 与 C 相连、但 A 与 C 不相连的非闭合三元组), 由邻接矩阵 G 及其幂 G² 张成的行向量便彼此线性无关, 「朋友的朋友但非自己朋友」的外生特征可充当同群结果的结构工具, 从而打破反射问题、识别内生同群效应; 而银行与年度固定效应负责吸收 Manski 意义上的关联效应 (银行不变禀赋与全局年度冲击)。聚类系数正是三元闭合程度的直接度量: 聚类越低 (开放三元组越多), G 与 G² 的行差异越大、可用于识别的结构变异越丰富, 网络拓扑越利于 Bramoullé 式识别; 聚类越高 (邻居近乎全互连、三元组趋于闭合), 结构越逼近完全重叠的群体, 可识别空间随之收窄。因此 bank_clustering 在本面板中兼具双重角色 —— 既是可解释银行结果的结构自变量, 也是判断网络拓扑是否支持同群效应识别的诊断量。在实证接入上, 它通常与银行与年度固定效应并用: 固定效应吸收银行不变的结构禀赋与全局年度冲击, 而聚类系数的年内变异刻画一家银行媒体邻域内聚性的移动; 它也常作为调节变量, 检验同群溢出在高内聚 (信息冗余、回声室) 与低内聚 (跨簇桥接、信息多元) 结构下的强弱异质。Bramoullé 等 (2020) 的同群效应综述与 Boucher 等 (2024) 的一般化同群效应理论进一步厘清了这类基于网络几何的识别在何种条件下成立: 前者系统梳理了 intransitive triads 作为识别来源的适用与失效边界, 后者放宽 linear-in-means 假设、允许异质与非线性的同群聚合, 指出网络的局部闭合结构决定了究竟哪一种同群统计量 (均值、极值抑或加权和) 可被识别。二者共同为把 bank_clustering 用于识别叙事划定了适用边界 —— 当群体重叠过高 (聚类过高) 或链接内生 (共现由不可观测的共同冲击驱动) 时, 识别会失效。须强调本列由媒体共现构造, 边的形成本身可能内生于报道选择, 故其识别用途是「诊断网络几何是否留有识别空间」而非「直接充当外生工具」; 换言之, 它标示的是识别的可行性边界, 真正的外生变异仍须另行寻找 (如判据分轨、冲击事件或来源结构工具)。

【与相邻测度的构念区分】
bank_clustering 在 33 指标结构族中占据一个特定的构念坐标, 须与三类相邻测度严格区分, 以免被误当替身混用。其一, 与中心度族 (bank_degree_cent / bank_eigen_cent / bank_between_cent 等) 的区分: 中心度衡量「银行有多居中 / 多重要」, 聚类系数衡量「银行的邻居之间有多互连」—— 前者是节点自身的地位, 后者是节点周边邻域的内聚性, 二者语义正交。Nezami 等 (2025) 的元分析覆盖的是中心度-绩效关联, 注册表特别标注其「不背书 bank_clustering」, 这恰恰印证了二者是不同构念、不可互相替代: 一家中心度极高的银行 (被广泛提及) 其邻居未必互连, 聚类可以很低。其二, 与结构洞 / 约束的区分: Burt (2004) 的结构洞理论中, 高聚类 (邻居互连、信息冗余) 与高约束、低经纪机会同向, 而低聚类对应跨越结构洞的桥接位置; 本族的 bank_constraint 正是 Burt 约束的直接实现, 与 bank_clustering 语义互补但不等同 (前者含度数惩罚与投入比重的加权), 二者不可并入同一线性组合。其三, 与路径型 / 电流型指标 (bank_cfbetween_cent、bank_harmonic_cent) 的区分: 后者刻画的是全局可达性与桥接流量, 且在建图时对边权取倒数 (共现越多、距离越近), 与聚类系数纯局部三角、用原始加权图的逻辑不同源。此外还须与两个语义最接近的同族列划清界限: 其一是 bank_ego_density —— 它由代码手工计算, 度量的是 v 的邻居之间实际存在的边数占最大可能边数的比例, 是二值 (无权) 的自我网闭合度; 而 bank_clustering 是加权的三角形强度均值, 二者虽同属「自我网闭合」构念, 但一个用边权、一个不用, 数值与排序并不等同, 不可互相替代或并入同式。其二是网络级 (年度级) 的 net_avg_cluster_yr 与 net_transitivity_yr —— 前者是全网所有节点聚类系数的平均、后者是全网闭合三元组占比, 二者按年广播到所有银行、每年内对所有银行取同一值, 是网络整体的内聚性; 而 bank_clustering 是逐银行的节点级量, 承载横截面变异。把节点级聚类与网络级传递性混用, 会抹掉本列赖以进入回归的银行间差异。除上述之外, 还须与凝聚性 / 冗余度同族的两个节点级指标 (bank_coreness、bank_effective_size) 区分: bank_coreness 由 k-core 分解给出, 度量的是银行嵌入某个「每个成员至少与 k 个组内成员相连」的稠密子群的最高阶数, 刻画的是群体层面的结构凝聚深度而非节点自身邻域的三角闭合; bank_effective_size 源自 Burt (2004) 的经纪度体系, 度量剔除邻居间冗余联系后一家银行的「非冗余邻居数」, 与结构约束互为倒向。三者虽都与「邻域是否稠密」沾边, 但 coreness 问的是「嵌得多深」、effective_size 问的是「邻居有多少不冗余」、clustering 问的是「邻居之间闭合几何如何」, 语义各异, 不可并入同一线性组合或互相替代。厘清这多重区分, 是避免把聚类系数误读为中心度、经纪度、全局桥接度、无权自我网密度、网络整体传递性、群体凝聚深度或邻居非冗余数的前提。

【已知局限与稳健性梯子】
第一重局限来自超边等权口径: 一篇同时提及 N 家银行的报道 (榜单、批量监管通报) 会贡献 C(N,2) 条等权边, 大-N 文章可凭边数膨胀主导网络结构, 从而系统性抬高相关银行的聚类系数。生产默认按每对 +1 等权累加 (golden-safe); Newman 型 degree-preserving 归一 (每对贡献 1/(N-1), 使单篇总度贡献守恒) 作为预留参数 hyperedge_normalize 存在于代码中, 但尚未接线到 config 与 runner, 故当前生产不可达 —— 这是解读高聚类值时须明示的建模局限, 而「同篇」判据 (canonical) 对该局限的暴露最强。第二重是判据敏感性, 也是本族最重要的稳健性梯子: 结构指标按银行∧银行共现的邻近判据分三轨重算 —— 同篇 (无后缀 canonical) / ±1 句窗 (_win1) / 严格同句 (_sent), 判据越严, 边集越稀、聚类系数系统性下移。三判据各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 检验。铁律: 此处的判据后缀 (_win1 / _sent) 属「银行∧银行边形成粒度」轴, 与三轨文本后缀 (_full / _ctx / _ss, 属「银行∧金科文本窗口」轴) 是两个正交概念空间, 后者并不适用于本结构族 —— 两轴禁止交叉、禁混同一 Hansen J。第三重是加权 / 无权口径差异: 本列是加权聚类系数 (吸收共现频次), 其数值与同一图上的无权聚类、以及无权自我网密度 bank_ego_density 都不相同; 报告时须明确说明用的是加权口径, 以免与文献中常见的无权聚类系数直接比水平。第四重是构造性内生: 边由媒体共现界定, 而报道并置本身受编辑议程、版面容量与热点周期左右, 因此高聚类既可能反映真实的经济 / 风险抱团, 也可能只是「常被放在一起写」的报道习惯; Fang 等 (2024) 提示媒体情绪与银行风险在中国样本中相互纠缠, 提醒本列的经济解释须谨慎、宜结合非媒体来源的结构变量交叉印证。第五重是年度快照局限: 网络逐年重建、年间不连边, 无法捕捉跨年的关系延续或缓慢演化, 一次性事件驱动的高共现会在其发生年度集中抬高聚类, 而不向邻年扩散。第六重是 T=2 开发样本上的退化: 网络稀疏、许多银行-年度数小于 2 使聚类系数取 0, 结构变异须待生产 T=18 全量语料方能充分体现; 加之前述 BLAS 浮点非确定性, 本列的解释应侧重相对秩序与符号方向, 而非绝对水平的逐位精确。第七重是单模投影的机械聚类偏倚, 它是本列作为共现测度最须交代的结构性缺陷: 银行共现网络本质上是「文章 × 银行」二模 affiliation 网络的单模投影, 而任何单模投影都会把同一篇报道内的全部银行连成一个完全子图 (clique), 使这些银行的邻居天然两两相连、三角形密度被结构性抬高。因此即便银行之间并无真实的经济抱团, 单模投影本身也会产生偏高的聚类系数 —— 这是所有由共同隶属关系构造的网络 (合著网、董事联结网、共现网) 的共性偏倚, 而非本项目语料所独有。Latapy 等 (2008) 系统讨论了二模网络分析中聚类等指标须以适配二模结构的方式重新定义、不能简单套用单模投影口径的方法学问题; Robins 与 Alexander (2004) 则在董事联结的二模投影上实证了这种投影如何机械地制造小世界式的高聚类。对本列的直接含义是: 高聚类不宜径直解读为「银行真实抱团」, 须与第一重超边等权局限合并考量, 并优先以三判据梯子的相对变化 (而非绝对水平) 作证据 —— 越严的判据 (_win1、_sent) 越能剥离「同篇同 clique」带来的机械三角, 逼近真实的紧邻共现闭合, 因此三判据梯子不仅检验判据严格度的稳健性, 也间接缓释单模投影的膨胀。综合而言, 本族的稳健性叙事以三判据梯子 (同篇 / _win1 / _sent) 的单调一致为主证据: 若主结论在三种越来越严的共现定义下保持符号与显著性, 则说明它不被任一特定判据严格度所驱动。

## VAR: bank_clustering

【变体差分】
bank_clustering 是本家族的 canonical 列, 即无判据后缀的基准形态, 采用「同篇共现」判据 (criterion='article'): 只要两家目标银行在同一 docid 报道内同时幸存, 就在二者间连一条边, 边权取其同篇共现的报道篇数。这是三判据梯子中最宽松的一端 —— 它不追问两家银行在文中相隔多远, 只要落在同一篇报道即算「共现 / 认识」, 因此产生的边集最密、聚类系数在三判据中系统性最高。它对应生产流水线的现行主口径, 也是 NETWORK_METRIC_BASES 结构指标 SSOT 中登记的 canonical 基名, 其列名逐字节不带任何后缀 (suffix='' 路径零改动), 与带 _win1 / _sent 后缀的两个稳健性变体并排落盘。

在计算上, canonical 路径由 build_adjacency_matrix 的 both-verified 主分支处理: 优先按 docid 分组、对同篇幸存银行集合内逐无序对累加成边, 而非退化到旧的 co_mentioned_banks 口径 (仅当缺 docid 列时才降级)。与 _win1 / _sent 走「docid 组内句级重扫」不同, canonical 不做句级定位、不加载否定与短名排除上下文, 因为「同篇」判据只关心两家银行是否落在同一篇, 不关心句间距离; 这也使 canonical 路径计算最轻、且与历史生产口径逐字节一致 (suffix='' 时列名与合并逻辑零改动)。聚类系数随后由 nx.clustering(G, weight='weight') 在这张同篇加权图上算出, 度数小于 2 的银行取 0.0。作为 tier=core 列, 它承担家族的主叙事: 既是可进入银行-年回归的结构自变量, 又是判断网络是否支持 Bramoullé 等 (2009) 式同群效应识别的三元闭合诊断量, 家族的构念、方法、识别与局限叙事均以本列为基准展开, 两个判据变体则是围绕它的稳健性侧翼。相较两个更严的判据变体, canonical 的「同篇」口径对超边等权局限的暴露也最强 —— 一篇提及 N 家银行的榜单式报道会一次性在这些银行间铺满 C(N,2) 条等权边, 显著抬高该篇涉及银行的同篇聚类; 因此高值银行须结合 _win1 / _sent 变体交叉核对聚类是否由大-N 报道驱动, 这也正是设置三判据梯子的初衷之一。

另有两点计算细节值得为 canonical 单独交代。其一, 度数小于 2 的银行 (孤立点、悬挂点) 聚类系数取 0.0 而非缺失: 由于同篇判据边集在三判据中最密, canonical 下落入 0 值的银行数最少, 结构变异保留得最充分; 越严的 _win1、_sent 判据边集越稀, 度数小于 2 的银行越多、0 值占比越高, 横截面变异随之收缩 —— 这一点在解读三判据梯子的水平差异时须一并纳入, 否则容易把「零值增多导致的均值下移」误读为纯粹的内聚性下降。其二, 前述预留参数 hyperedge_normalize (Newman degree-preserving 归一, 每对贡献 1/(N-1) 使单篇总度贡献守恒) 仅在 article 主路径实现, 判据分轨路径 (_win1 / _sent) 对该参数显式 raise 拒绝; 这意味着即便未来把该归一接线到 config 与 runner, 它也只能作用于 canonical 这一「同篇」形态。换言之, 超边等权局限及其唯一的候选缓解手段都集中在本列身上, 进一步印证 canonical 是三判据梯子中对超边规模最敏感、也最须与更严变体交叉核对的一端; 而当前生产口径下该归一未接线、路径不可达, 故本列落盘值仍为等权 (每对 +1) 的加权聚类系数。

须再次强调三条口径边界。其一, 底层报道全集继承 full-only 留篇口径 (2026-06-29): 一篇报道是否算「一篇银行金科报道」只看 full 轨留篇门控 (llm_verified_full), 节点全集 = 当年 full 轨留篇后幸存银行, 判据分轨只收紧边集、绝不改动节点集, 故本列与主面板 n_articles 分母同源、与 ctx / ss 文本轨的 conditional-on-full 口径不冲突。其二, 本列受 BLAS 浮点求和次序影响, 与 bank_cfbetween_cent、bank_harmonic_cent 同属 9 个非确定网络列之一, golden 零漂移校验须按全名 drop, 解读以符号与秩序稳健为准。其三, canonical 的「同篇」判据与其两个变体 _win1、_sent 各自 just-identified 并排、互为稳健性、不分主次, 三者严禁混入同一 over-identified Hansen J。在报告实践上, canonical 通常作为正文主口径呈现, _win1 与 _sent 作为稳健性侧翼进入附注或稳健性表, 三者共同证明结论不随共现严格度而反转。综上, 相对于两个稳健性变体, 本列的差分语义可一句话概括为: 判据 = 同篇 (最宽), 边最密, 聚类值系统性最高, 且是唯一登记为 canonical、列名无后缀、承担识别与解释主轨的形态; 其余两列均在保持节点全集与本列一致的前提下, 仅以更严的边形成规则重算同一构念, 与本列构成完整的判据敏感性梯子。

## VAR: bank_clustering_sent

【变体差分】
bank_clustering_sent 是「严格同句」判据变体 (criterion='sent', 后缀 _sent), 处于三判据梯子最严的一端。与 canonical 的「同篇即连边」不同, 本列只有当两家银行落在同一句话里被一同提及时才连边: build_adjacency_matrix 走判据分轨路径, 在 docid 组内用 map_bank_sentence_positions 逐句定位各银行别名的出现位置, 再由 bank_pairs_within_sentence_window 以 win_radius=0 (同句) 抽取共现银行对累加成边。扫描文本 = prepend_title 拼接的标题与正文, 标题自成第 0 句参与同句判定 (match_in_title 恒 true, 镜像 stage 13 口径)。判定复用与 stage 11 / 13 同一份否定 / 短名排除事实源 (禁裸 AC, 防「涉农行业」误命中「农行」的假阳性)。节点全集与 canonical 完全一致 (同为当年幸存银行), 仅边集最稀 —— 只保留最紧邻的同句共现关系, 故聚类系数在三判据中系统性最低、零值最多。

差分语义: 判据 = 严格同句 (最严), 边最稀, 聚类值系统性最低。铁律: _sent 是「银行∧银行边形成粒度」轴上的判据后缀, 与三轨文本后缀 _ss (银行∧金科同句共现, 判据主体完全不同) 不可混淆; 本列与 canonical、_win1 各自 just-identified 并排、互为稳健性、不分主次, 三者严禁混入同一 over-identified Hansen J。本列同属 BLAS 非确定网络列, golden 零漂移校验须按全名 drop。作为最严判据臂, 它主要用于反向确认: 若某银行在 canonical 下聚类偏高而在 _sent 下骤降, 提示其同篇共现多为「同文异句」的松散共现而非紧密同句关系, 是甄别超边等权污染的稳健性抓手。

## VAR: bank_clustering_win1

【变体差分】
bank_clustering_win1 是「±1 句窗」判据变体 (criterion='win1', 后缀 _win1), 处于三判据梯子的中间强度 —— 比 canonical「同篇」严、比 _sent「严格同句」宽。连边条件为: 两家银行出现在相隔不超过 win_radius 句的窗口内, 其中 win_radius 取 config/panel.yaml::network_criteria.win_radius, 默认 1, 即本句及其前后各一句。计算路径与 _sent 同源 (docid 组内句级重扫、map_bank_sentence_positions 加 bank_pairs_within_sentence_window、prepend_title 标题为第 0 句、复用否定 / 短名排除事实源), 唯一区别是把窗口半径从 0 (同句) 放宽到 win_radius (相邻句)。因此其边集稠密度介于 canonical 与 _sent 之间, 聚类系数水平也居中, 提供一个「近邻但不必同句」的中庸共现定义。

须辨明: 此处 win_radius 是 panel.yaml::network_criteria 键, 与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科保留判据) 是两个不同键、判据主体不同 (银行∧银行 vs 银行∧金科)、互不联动, 改一个不影响另一个。差分语义: 判据 = ±1 句窗 (中), 边稠密度居中, 聚类值居中。铁律: 本列与 canonical、_sent 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 判据后缀 _win1 属「银行∧银行边形成粒度」轴, 与三轨文本后缀 (_full / _ctx / _ss) 正交, 不得交叉。本列同属 BLAS 非确定网络列, golden 校验须按全名 drop。作为中间臂, _win1 与 canonical、_sent 三点共同构成聚类系数对「共现邻近度」定义的单调稳健性梯子: 边稠密度随判据收紧单调下降 (同篇 大于等于 ±1 句窗 大于等于 同句), 聚类值水平亦随之单调下移, 用以检验主结论不被任一特定判据严格度驱动。若三臂符号与显著性一致, 即为本族最有力的稳健性证据。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Amancio, D. R., Machicao, J., & Quispe, L. V. C. (2025). Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis. PLOS ONE. https://doi.org/10.1371/journal.pone.0327421
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Robins, G., & Alexander, M. (2004). Small worlds among interlocking directors: Network structure and distance in bipartite graphs. Computational & Mathematical Organization Theory, 10(1), 69-94. https://doi.org/10.1023/B:CMOT.0000032580.12184.c0
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Rojas Rincón, J. S., Acosta-Prado, J. C., & Castellanos Narciso, J. E. (2025). A Bibliometric Analysis on Network-Based Systemic Risk. Risks. https://doi.org/10.3390/risks13110210
Zhu, B., Hu, X., Deng, Y., & Lin, R. (2023). Systemic risk prevention policies targeting systemically important banks: Does clustering pattern matter?. PLOS ONE. https://doi.org/10.1371/journal.pone.0284861
<!-- rendered-citations:end -->
