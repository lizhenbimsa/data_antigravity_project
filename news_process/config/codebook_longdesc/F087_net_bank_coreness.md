---
family_id: F087
columns:
- bank_coreness
- bank_coreness_sent
- bank_coreness_win1
unit: k-核序数 (整数值拓扑指标, 无量纲)
formula: "bank_coreness = 节点在年度银行共现图 G 上的 k-core number = 最大的 k 使得该银行属于 G 的 k-核; 由 networkx.core_number(G) 求解 (纯拓扑, 忽略边权); 判据变体 {同篇(无后缀 canonical) / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: pipeline\panel\network_spillover.py::compute_bank_network_centrality (nx.core_number) ; pipeline\panel\codebook.py (标签/类目/来源阶段推断)
upstream:
- 24_herd_decay.parquet (df_exploded; both-verified 篇章×银行帧, docid 分组内幸存 target_bank 定义边集)
- 40_panel_yearly.parquet (bank-year 面板骨架, 追加 33 结构指标 × 3 判据变体)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.1103/4pg6-mtmt
  type: journal
  authors: Kirkley, A.
  year: 2025
  title: "Fast nonparametric inference of network backbones for weighted graph sparsification"
  venue: Physical Review X
  vol: 15
  issue: 3
  pages_or_artno: "031013"
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
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
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
- doi: 10.1023/B:CMOT.0000032580.12184.c0
  type: journal
  authors: Robins, G., & Alexander, M.
  year: 2004
  title: "Small worlds among interlocking directors: Network structure and distance in bipartite graphs"
  venue: Computational & Mathematical Organization Theory
  vol: 10
  issue: 1
  pages_or_artno: 69-94
- doi: 10.1086/421787
  type: journal
  authors: Burt, R. S.
  year: 2004
  title: "Structural holes and good ideas"
  venue: American Journal of Sociology
  vol: 110
  issue: 2
  pages_or_artno: 349-399
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
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
- doi: "10.1080/00036846.2024.2302932"
  type: journal
  authors: "Ma, Y., & Zhao, J."
  year: 2024
  title: "Do interfund network centralities affect fund systematic risk? Evidence from China open-ended funds"
  venue: "Applied Economics"
- doi: "10.1080/00036846.2025.2597474"
  title: "Beyond single-network assumptions: structural uncertainty and systemic risk in financial networks"
  authors: "Pang, C., Fan, H., Wu, J., Gao, Q., & Chen, N."
  year: 2025
  venue: "Applied Economics"
  type: "journal"
- doi: "10.1111/abac.12341"
  title: "Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum"
  authors: "Guo, F., Lyu, B., Lyu, X., & Zheng, J."
  year: 2024
  venue: "Abacus"
  type: "journal"
new_dois:
  - "10.1080/00036846.2024.2302932"
  - "10.1080/00036846.2025.2597474"
  - "10.1111/abac.12341"
---

## CORE

【构念与来源】
本家族刻画的是银行在年度新闻共现网络中的核性 (coreness), 即该银行嵌入网络凝聚核心的深度。核性以 k-核序数 (k-core number) 操作化: 给定一个无向图, 其 k-核是反复删除所有度数小于 k 的节点后仍留存的最大子图; 一个节点的核序数则是使它仍属于该 k-核的最大 k 值。核序数由 Seidman (1983) 在研究网络结构与最小度时提出, 是刻画凝聚子群与网络稳固内核的经典拓扑量, 直觉上回答的问题是: 这家银行所处的邻域有多致密、多难被外围修剪剥离。度数高但邻居全是悬挂末梢的银行, 会在逐层剥离中迅速掉核, 核序数低; 反之, 一家银行即便度数不算最高, 只要它与一批彼此也高度互连的同侪共处于一个致密团块, 就会获得高核序数。因此核性度量的不是"认识多少家"(那是度中心度, Freeman 1978), 而是"处在多深的抱团核心里"。核序数在算法上等价于图的退化序 (degeneracy ordering) 中每个节点被剥离时的层壳编号: 反复摘除当前最小度节点并记录其被摘时的度, 即得逐节点的 k-壳层级, 这一构造保证核性是良定义、确定且与节点标注顺序无关的整数序。

数据来源为本项目的中文银行新闻语料。构念的网络底座是年度银行共现图: 节点为银行, 边为两家银行在同一年被同一批新闻共同提及的关系。为何用"共现"承载银行间关系? 因为新闻媒体在报道一则事件、一项监管动作或一类业务时, 往往把处境相近、业务关联或同受一事牵动的银行并置于同一篇报道, 这种并置本身就是市场与舆论把它们归为"同一议题簇"的外显信号; 把海量报道里"谁与谁一起被谈论"的成对信号累加成年度网络, 银行在其中的核性便代理了它嵌入公众关注与信息传播结构的深度。这一"从非结构化文本还原可计算网络结构"的方法思路与 Li et al. (2026) 从文本风险披露中提取金融网络结构、度量连通性的做法同源, 二者都主张把文本里的共同出现信号提炼为网络结构量, 只是本项目的语料是新闻而非风险披露, 度量对象是银行的位置深度而非系统连通性水平。银行共现网络一经建立, 银行的核性即成为其在信息-关注结构中所处位置的稳健刻画, 与资产定价、系统性风险等经济后果的网络中心度文献 (Yu, Hu, & Zhong 2024; Xu & Zhao 2024; Nezami, Chisam, & Palmatier 2025) 在构念层面相衔接: 处在网络核心深处的银行, 其信息更易被扩散、其风险更易被联想传染、其估值更易被同侪牵动。在相邻的基金网络情境中, Ma & Zhao (2024, Applied Economics) 实证发现基金间网络中心度 (度中心度与接近中心度) 显著提升基金的系统性风险, 支持网络位置越居中越难以幸免于系统冲击的机制, 与本家族把银行核性作为系统重要性媒体侧代理的构念定位相衔接。Pang, Fan, Wu, Gao, & Chen (2025, Applied Economics) 该文主张系统性风险评估须显式处理金融网络结构本身的不确定性, 而非假设网络被单一、精确观测, 呼应本家族核性构念对判据梯子与边定义敏感性的强调。Guo, Lyu, Lyu, & Zheng (2024, Abacus) 该文以中国股票论坛社交网络数据构造公司间网络中心度, 发现其与股价同步性显著负相关, 为本项目从中文媒体文本构造银行共现网络、以网络位置代理信息结构的思路提供同源实证参照。

【方法学与计算】
计算在 pipeline\panel\network_spillover.py 的 compute_bank_network_centrality 内完成, 是该函数产出的 33 个结构指标之一 (节点级 18 个中的第 18 项)。流程为逐年重建网络后取拓扑量。边集构造走 build_adjacency_matrix: 在无后缀 canonical 口径 (criterion='article') 下, 对每个 docid (一篇文章) 取其在 both-verified 展开帧中幸存的 target_bank 集合, 集合内每一无序银行对恰计一次共现, 对称累加进邻接矩阵; 这一"按文章聚合、每篇每对加一"的口径修正了旧实现中同一对因两条孪生行去留不同而 1 倍/2 倍任意混计、以及验证已拒绝银行仍以幽灵边入网的问题。节点全集取该年幸存 target_bank 的并集, 含孤立节点。由邻接矩阵建 networkx 无向图 G 后, 核性直接调用 nx.core_number(G) 求得, 孤立银行 (度为 0) 取核序数 0。

在同一逐年循环内, 系统还基于同一邻接矩阵构建了倒数权重图 (边权取共现次数的倒数, 供介数、调和、接近、离心率等路径型指标把"共现越多=距离越近"翻译为最短路), 并识别最大连通分量供仅对连通片有意义的指标使用; 但核性既不走倒数图也不限于最大连通分量 — 它在含孤立节点的完整原始图上一次性求全体银行的核序数, 断连与孤立对它不构成障碍, 这正是 k-核相对谱类中心度的稳健之处。函数每年还会诊断性地记录提及超过十家银行的大-N 文章数与最大提及规模, 因为这类"榜单式"报道会以等权团投影贡献大量边、可能主导网络结构, 该记录为核性的超边敏感性审计留痕。

关键口径须明确: 核序数是纯拓扑量, 只看边的有无、不看边权。共现图虽携带以共现次数为值的边权 (供 strength、加权路径类指标使用, 参照 Opsahl, Agneessens, & Skvoretz 2010 的加权节点中心度框架, 该文把度与最短路推广到加权网络), 但 core_number 忽略权重, 因此一对银行被共同提及一次还是上百次, 对核性的贡献等同。这一"退回无权"的选择换来的是整数值的可解释性与逐位可复现性: 核性不涉任何浮点谱运算或迭代收敛, 不属于本项目已知受 BLAS 浮点漂移影响、跨次重建非逐位可复现的三列 (bank_clustering / bank_cfbetween_cent / bank_harmonic_cent), 因此在钉死 PYTHONHASHSEED 与各 BLAS 线程数为一的前提下, 核性列可字节级重现, 是家族中确定性最强的一类指标。留篇宇宙沿用 2026-06-29 起的 full-only 口径: 定义边的银行必须是通过 full 轨 LLM 留篇门控的篇章内幸存者, 且共现边只在同一篇文章内均通过 both-verified 验证的银行对之间建立, 已被验证拒绝的银行不以幽灵边入网。因此核性网络的节点与边集严格继承 full-only 留篇集, 与 n_articles 等分母口径一致, 不掺入 ctx/ss 轨的条件留篇差异 — 这保证了核性、篇数与其它 full 口径面板量在同一留篇宇宙上可比。

【文献定位】
核性度量根植于社会网络分析的凝聚子群与最小度结构传统 (Seidman 1983), 并与中心度谱系互补而非重叠: 度中心度 (Freeman 1978) 量局部连接数, 特征向量与地位类中心度 (Bonacich 1972) 递归地按邻居的重要性对节点加权, 基于随机游走的电流介数 (Newman 2005) 量节点作为信息/资金流桥接枢纽的地位, 结构洞类指标 (Burt 2004) 量一个节点的邻居间是否互不相识、从而衡量其跨结构洞的经纪机会, 网络级的聚类与小世界结构 (Watts & Strogatz 1998) 则刻画三角闭合密度与短路径共存的宏观形态。核性在这一谱系中占据"凝聚核心深度"的独特位置 — 它既非纯局部 (不同于度), 也非纯谱 (不同于特征向量), 而是以逐层剥离的组合过程界定节点距网络"最稳固内核"的远近。在金融应用侧, 银行网络位置与系统性风险、传染及资产价格的关联有系统综述与实证支撑: Jackson & Pernoud (2021) 综述金融网络系统性风险时反复强调核心-外围结构对脆弱性与传染路径的塑造, 处于核心的机构其冲击更易外溢也更易被外溢波及; Duarte & Eisenbach (2021) 刻画火线抛售溢出如何沿资产重叠与网络位置传播, 位置越居中的机构承受与施加的溢出越大; 而 Yu, Hu, & Zhong (2024)、Xu & Zhao (2024) 与 Nezami, Chisam, & Palmatier (2025) 分别从信息扩散驱动的资产定价、金融网络中节点中心性对资产价格预测的贡献、以及跨大量研究的网络中心性-企业绩效元分析三个角度, 佐证了网络中心性对经济后果具有稳健的解释力。本项目把这一传统迁移到"新闻共现"这一媒体信息网络上, 使银行核性成为其在公众关注与信息传播结构中所处深度的代理, 从而把上述系统性风险与资产定价的网络位置逻辑接入到可由媒体文本大规模、逐年测量的银行面板中。

【识别策略定位】
把银行核性作为回归右手侧结构变量时, 须直面网络型同侪效应的识别难题。Manski (1993) 的反射问题指出, 当个体结果同时受同侪结果 (内生效应)、同侪特征 (外生/情境效应) 与共同环境 (关联效应) 影响时, 三者在线性均值模型中难以分离, 因为个体与其同侪均值互为镜像; 这是所有把网络位置或同侪量放进回归的研究必须正面回应的根本障碍。Bramoullé, Djebbari, & Fortin (2009) 证明: 当网络存在传递性缺失 (即并非任意两点都相连、图不是完全图) 时, 同侪的同侪 (二阶邻居) 特征可作为工具, 使内生与外生效应重获识别; 这正是本项目网络溢出识别的理论支点。Bramoullé, Djebbari, & Fortin (2020) 把这一框架系统综述并厘清其适用边界, Boucher, Rendall, Ushchev, & Zenou (2024) 则进一步走向更一般的同侪效应理论, 放松线性-均值设定。Grieser, Hadlock, LeSage, & Zekhnini (2022) 把网络效应识别落地到企业财务政策情境, 用空间计量与网络工具处理同侪财务政策的相互影响, 与本项目银行情境高度平行, 是把上述计量理论用于金融面板的直接范例。核性在本框架中的定位须精确: 它是一个纯粹的结构位置量 (拓扑深度), 不含任何同侪的结果或情感取值, 因此当它进入以银行结果为因变量的溢出回归时, 扮演的是外生网络位置度量的角色, 而非把同侪结果直接搬进右侧 — 这一"位置量而非结果量"的性质使其相对更少直接触发反射问题的内生-外生纠缠。但须清醒: 银行的核性会随其被媒体共同报道的模式逐年内生演化 (例如卷入同一监管风波的银行当年核性同升), 因此跨年核性水平不可当作外生给定, 实证上须以年份固定效应吸收全网共同冲击、以银行固定效应吸收时不变的结构禀赋, 并在需要因果解读处辅以网络工具变量策略 (Bramoullé, Djebbari, & Fortin 2009) 或适当的移动-份额/工具构造。此外, 核性作为整数量在含固定效应的回归中提供的是层级跳变而非连续边际, 解释系数时须注意其粗粒度含义。

识别策略还须直面一个本项目特有的层次: 与社会网络计量文献常假设网络"被观测"不同, 本项目的银行共现网络是从媒体文本"被测量、被构造"出来的, 边并非事先给定的客观纽带, 而是由报道并置这一噪声信号还原而得。这带来两重须分辨的识别隐患。其一是网络结构本身的测量误差: 同一批银行关系在不同判据、不同语料覆盖、不同去重口径下会得到略有差异的边集, 从而使核性带有非经典测量误差; 近期把网络纽带从面板数据中加以识别、并显式处理纽带不确定性的计量进展 (de Paula, Rasul, & Souza 2024) 提示, 当网络是被推断而非被直接观测时, 结构量的估计不确定性须纳入推断, 本项目对此的实用回应是提供由松到严的判据梯子, 让核性对边定义标准的敏感度可被审计而非被隐藏。其二是共现过程与银行结果的同时性: 媒体之所以把某几家银行并置报道, 往往正因为它们同期共同卷入某一可观测或不可观测事件, 而该事件可能同时驱动银行的经济结果, 于是核性与结果之间存在由共同冲击引致的伪相关。这一同时性无法被"位置量而非结果量"的性质自动化解, 只能靠年份固定效应吸收全网共同的时间冲击、银行固定效应吸收时不变的媒体曝光禀赋, 并在核性水平的因果解读处审慎地把它当作可能内生的处理变量而非外生协变量。须补充的技术警示是: 在把银行-年面板与网络派生的核性一同放入含双向固定效应的模型时, 网络数据与固定效应叠加会放大有限样本偏差与推断的相依性, 故须以银行层面聚类或适当的网络稳健标准误处理误差的横截面相依 (核性同升的银行其残差亦可能相关), 避免把网络诱导的相依误当作独立信息而高估显著性。综上, 核性作为外生网络位置度量的相对优势是真实的, 但"相对更少触发反射问题"绝不等于"外生", 使用者须以固定效应、判据梯子与稳健推断三者合力, 把核性的内生演化、测量误差与同时性一并纳入识别设计。

【与相邻测度的构念区分】
核性须与本项目共现网络家族的相邻测度严格区分, 以免在解释与建模上混淆。相对度中心度: 核性是递归的、全局的凝聚深度, 度数只是局部邻居计数; 高度低核的银行 (中心连一堆外围末梢) 与低度高核的银行 (深嵌小而致密的团块) 在核性上会给出与度数相反的排序。相对特征向量与 Katz 类谱中心度 (Bonacich 1972): 后者以谱迭代按邻居重要性连续加权、需连通分量内收敛且对断连敏感, 核性则是组合数意义上的整数退化序, 无需分量分解、无收敛问题、对图断连稳健。相对电流介数 (Newman 2005): 介数量的是"多少路径必须经过它"的桥接地位, 核性量的是"处在多深的核里"的成员地位, 二者甚至可以负相关 (跨核桥接节点可能自身核序数不高)。相对聚类系数 (Watts & Strogatz 1998): 聚类是局部三角密度, 核性是全局 k-壳层级。相对结构洞类指标如约束、有效规模、自我网密度 (Burt 2004): 那些量的是邻居间的互不相连 (跨结构洞的经纪机会), 与核性量的凝聚嵌入方向相反。相对基于边权的强度与加权路径量 (Opsahl, Agneessens, & Skvoretz 2010): 核性刻意退回无权拓扑, 不受共现频次幅度影响, 因而不会因少数高频共现对而被拉高, 但也丧失了区分强弱关系的能力。相对超边归一后的度守恒指标: 核性建立在等权团投影上, 对大-N 榜单文章的稠密团尤为敏感 (见局限段), 这与那些按 1/(N-1) 归一以守恒单篇总度贡献的口径在敏感性方向上不同。一个尤须澄清的构念边界是核性与网络级指标的关系: 家族兄弟中的 net_* 系列 (如密度、模块度、直径) 是逐年全网单值、在含年份固定效应的回归中被年 FE 完全吸收而不可识别; 而 bank_coreness 是节点级、随银行-年变化, 保有截面识别力, 二者不可混为一谈。还有一层更根本的构念区分须点明: 本项目的银行共现网络在数学上是一个二模 (two-mode/affiliation) 网络向单模 (one-mode) 网络的投影。原始数据天然是"文章-银行"二部图 (bipartite graph): 一侧节点是文章, 另一侧节点是银行, 一篇文章提及一家银行即连一条跨模边。银行共现网络则是把这张二部图沿银行一侧投影 (projection) 而得的单模图 — 只要两家银行同被某篇文章提及, 就在投影图上连一条银行间边。核性正是在这张投影图上计算的。这一投影视角带来两点必须澄清的构念含义, 而它们恰是隶属网络 (affiliation network) 分析的经典议题 (Borgatti & Everett 1997; Faust 1997; Latapy, Magnien, & Del Vecchio 2008)。第一, 投影会把每篇文章内被共同提及的银行集合坍缩成一个完全子图 (clique): 一篇点名 N 家银行的文章, 在投影图上贡献 N(N−1)/2 条边、构成一个 N-团, 而 k-核序数对稠密团块极其敏感 — 一个大团会一次性把其中所有银行的核序数抬高至接近 N−1。因此核性并非度量银行两两之间独立确认的关系强度, 而是度量它们在"同篇隶属"意义上的抱团深度, 这与直接观测的银行间业务往来或股权纽带在构念上不同。第二, 隶属网络投影天然带有比随机图更高的聚类与更短的路径 (即人造的小世界结构), 这在董事联结等二部图投影研究中被系统记录 (Robins & Alexander 2004), 提示核性、聚类系数一类凝聚型指标在投影网络上会被结构性地放大, 解读其绝对水平时须以此为参照。也正因投影会系统性地扭曲单模结构量, 关于二部投影保真度的方法学研究主张对投影施加零模型校验或显著性过滤 (Cimini, Carra, Didomenicantonio, & Zaccaria 2022): 本项目的核性目前建立在未过滤的等权团投影上, 未做此类零模型稀疏化, 这是其与"经统计显著性净化的投影网络位置量"之间的又一构念边界。理解核性=投影图上的凝聚深度, 而非银行间独立纽带的抱团深度, 是正确使用本家族的前提。最后须钉死: 本家族的判据后缀 (_win1 / _sent) 与三轨文本后缀 (_full / _ctx / _ss) 是两个正交的概念空间 — 前者刻画银行∧银行成边的邻近判据松紧, 后者刻画银行∧金科文本抽取轨道, 判据主体 (银行对银行 vs 银行对金科) 与所量对象截然不同, 二者禁混进同一 over-identified Hansen J; codebook 三推断入口对此专门先剥判据后缀再按基名匹配, 正是为防 _sent 子串被误归情感类、或 _yr 联合判据被后缀破坏而落"未知"。

【已知局限与稳健性梯子】
核性有若干须披露的局限。其一, 整数粗粒度: k-核序数取值稀疏离散, 在小而稀的年度共现网络里大量银行会并列取 0 或 1, 截面方差有限; 开发期 T=2 的极浅面板上核性尤易退化 (多数银行同核), 生产期 T=18 的深面板才具备足够核结构层次, 审计不应以 T=2 的退化为核性构念的缺陷。其二, 超边膨胀敏感, 且这一敏感对核性尤为致命: 榜单式或批量监管通报类文章一次提及众多银行, 会以等权团投影 (见构念区分段所述二模→单模投影) 贡献一个 N-团, 而 k-核序数对稠密团块的响应是阶跃式的 — 一篇点名 N 家银行的文章可一次性把其中每家银行的核序数抬至接近 N−1, 单条超边即足以主导被点名银行的核性排序。因此相较度、强度这类线性累加的局部量, 核性对大-N 文章的放大是非线性的、更难以事后线性调整消解, 这也是逐年循环诊断性记录大-N 文章数与最大提及规模的原因。用于消解该膨胀的 hyperedge_normalize (按 1/(N−1) 对单篇团边降权、守恒单篇总度贡献) 目前仅在 article 主路径预留、尚未接线到 config 与 runner, 且在判据分轨路径下被守卫显式拒绝以防三判据轨在超边归一上无声分叉, 故现行核性建立在"每篇每对加一"的等权团投影上。须指出, 除按度守恒归一外, 关于二模投影保真度的方法学文献还提供了另一条正交的应对路径 — 对投影图施加零模型显著性过滤或骨架 (backbone) 抽取以剔除由大隶属集机械产生的伪边 (Cimini, Carra, Didomenicantonio, & Zaccaria 2022; Kirkley 2025); 本项目目前既未做度守恒归一、也未做骨架稀疏化, 核性建立在未净化的原始团投影上, 使用者解读高核银行时须回查其核深是否由个别榜单式超边驱动。其三, 无权盲区: 核性不区分一次共现与高频共现, 加权 k-核未实现, 属可解释性与可复现性权衡下的有意取舍。其四, 孤立即零: 孤立银行取核序数 0 而非缺失, 使"从未被共同提及"与"确处外围"在数值上合流, 解释时须并看度数。针对边定义敏感性, 本家族提供了判据梯子作为稳健性设计: 同篇 (canonical)、±1 句窗 (_win1) 与严格同句 (_sent) 三种由松到严的成边判据各自重算核性, 三者互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 由于严格同句边集嵌套于 ±1 句窗边集、句窗边集又嵌套于同篇边集 (三者的节点全集恒相同、仅边集逐级收紧), 而 k-核序数对边集单调不减, 三个判据变体在同一节点全集上满足逐点单调关系 (同句 ≤ 句窗 ≤ 同篇), 为核性对"算共现"标准松紧的敏感度提供了可审、可证伪的方向性证据: 若主结论在最严同句判据下仍稳健, 则不太可能由宽判据下的榜单式虚假共现驱动。须补充说明: 判据分轨路径下 hyperedge_normalize 尚未实现且被守卫显式拒绝, 以防三判据轨在超边归一上无声分叉; 而开发期浅面板上严判据变体易出现大面积零共现导致核性退化 (多数银行同核甚至全零), 属预期的样本深度限制而非度量缺陷, 生产期深面板方能让三级判据梯子展开出有意义的层级差异。综上, 核性是一个确定性强、可解释、对断连稳健、并配备完整边定义稳健性梯子的银行网络位置量, 其主要代价是整数粗粒度与对等权团投影下超边膨胀的敏感性, 使用者应结合度数与判据梯子综合解读, 并避免在浅面板上过度解读其截面方差。

## VAR: bank_coreness

【变体差分】
本列是家族 canonical 无后缀列, tier=core, 对应共现判据 criterion='article' (同篇口径)。其成边规则为: 两家银行只要在同一 docid (同一篇文章) 内均通过 full 轨留篇门控并幸存于 both-verified 展开帧, 即在该年计一条共现边, 且按文章聚合、每篇每对恰加一次 (对称累加进邻接矩阵)。这一"按 docid 聚合而非逐行计数"的口径是关键修正: 旧实现对验证过滤后的展开帧逐行解析同提及银行并双向加权, 导致同一对因两条孪生行去留不同而在一倍与两倍之间任意混计, 且共现字段仍列出验证已拒绝的银行、产生幽灵边; 现行口径只在同篇内均幸存的银行对间恰计一次, 消除了这两类偏差。同篇是三个判据变体中最宽松的成边标准 — 只要求两家银行"出现在同一篇文章里", 不要求段落、句窗或同句邻近 — 因而产生最稠密的年度共现图, 相应地在同一节点全集上给出逐点不小于 _win1 与 _sent 变体的核序数 (核性对边集单调, 加边只增不减任一节点的核序数)。计算上, 该列由 nx.core_number 在无后缀口径重建的无向图 G 上一次求得, 纯拓扑忽略边权, 度为 0 的孤立银行取核序数 0。

本列是家族的生产主口径, export 标签登记为 Co-mention K-Core Number (Seidman 1983), 也是 NETWORK_METRIC_BASES 单一事实源中登记的 33 个结构基名之一, 并作为 stata_export 判据标签机械块与 codebook 三推断入口 (标签/类目/来源阶段) 剥判据后缀后归一时的基名; codebook 特意把 bank_coreness 列入无 cent 子串的结构基名白名单, 以免其 _win1/_sent 变体落入"未知"类目。须强调"canonical"仅指它是家族无后缀的默认成边口径, 并不意味着它在计量上比 _win1 / _sent 更"主": 三判据是互为稳健性、不分主次的并排规格, 各自 just-identified, 严禁把三者混进同一 over-identified Hansen J 过度识别检验。本列的判据后缀 (空) 与三轨文本后缀 (_full/_ctx/_ss) 分属两个正交概念空间 (前者是银行∧银行成边邻近判据, 后者是银行∧金科文本抽取轨道), 不可混用; 作为纯整数拓扑量, 本列不涉浮点谱运算, 不属于受 BLAS 浮点漂移影响的三非确定列, 在钉死 PYTHONHASHSEED 与 BLAS 线程数后可字节级复现。在建模定位上, 本列刻画银行嵌入新闻共现凝聚核心的深度, 是外生的网络位置量而非同侪结果量, 用作溢出回归右手侧时相对更少直接触发 Manski (1993) 反射问题的内生-外生纠缠, 但跨年核性的内生演化仍须以年份与银行固定效应及必要的网络工具变量策略 (Bramoullé, Djebbari, & Fortin 2009) 处理; 其经济含义与系统性风险及资产定价的网络中心性文献 (Jackson & Pernoud 2021; Yu, Hu, & Zhong 2024) 相衔接, 可用作银行在信息-关注结构中系统重要性的媒体侧代理。须提醒使用者: 因整数取值粗粒度, 在开发期 T=2 的极浅面板上本列易退化 (多数银行并列取低核), 其充分的跨截面变异须在生产期 T=18 的深面板上才充分显现。作为唯一的 core 列, 本列亦承担家族的解释与建模锚点职责: 家族的 _win1 与 _sent 变体均以本列的同篇口径为参照系, 三者的逐点单调关系 (同句 ≤ 句窗 ≤ 同篇) 使本列成为判据梯子的上包络, 也使其核序数天然是同一银行-年在三判据下可取的最大核深; 因此在报告主结果时通常以本列为主轴、以两严判据变体为稳健性旁证, 而非反之。数值上本列取非负整数, 孤立银行取 0, 使用时须并看度数以区分"确处外围"与"当年未被共同报道"两种同为 0 核的情形。

## VAR: bank_coreness_sent

【变体差分】
本列 tier=standard, 对应共现判据 criterion='sent' (严格同句口径, 落列后缀 _sent), 是家族中成边标准最严的判据变体。其成边规则为: 在同一 docid 组内对幸存银行重扫文本, 仅当两家银行的别名出现在同一句话内 (句窗半径 radius=0) 才计一条边; 扫描文本采用 prepend_title 口径 (标题作为第 0 句, 镜像 stage 13 的 match_in_title), 判据原语为 core/text/entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 并复用与 stage 11/13 同一的否定 AC 与短名排除事实源 (防"涉农行业"误配"农行"类假阳性)。由于同句边集嵌套于 ±1 句窗边集又嵌套于同篇边集, 本列在同一节点全集上给出三变体中逐点最小的核序数, 稠密度最低。本列与 canonical 及 _win1 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 判据后缀 _sent 与三轨文本后缀 _ss 虽字面都涉"同句", 却是正交概念 (前者银行∧银行成边, 后者银行∧金科文本抽取), codebook 三推断入口特意先剥判据后缀再匹配, 以免 _sent 子串被误归情感指标。与 canonical 同篇口径相比, 本列剔除了"同篇但不同句"的松散共现边, 因而边集最稀、核序数在三变体中逐点最低, 是判据梯子最严的一端: 它只承认"被写在同一句话里"这种最强的语义共同出现, 因此对榜单式或跨段并置产生的虚假共现最不敏感, 用作稳健性检验时提供了主结论抗宽判据虚假边污染的最强证据。开发期浅面板上严判据尤易使多数银行同句无共现而核序数退化 (大面积取 0), 属预期的样本深度限制, 生产期深面板方具解释力。作为纯整数拓扑量, 本列同样不涉浮点谱运算、不受 BLAS 漂移影响, 可逐位复现。

## VAR: bank_coreness_win1

【变体差分】
本列 tier=standard, 对应共现判据 criterion='win1' (±win_radius 句窗口径, 落列后缀 _win1), 松紧介于 canonical 同篇与 _sent 严格同句之间。其成边规则为: 在同一 docid 组内重扫文本, 当两家银行别名出现在相距不超过 win_radius 句的窗口内即计一条边; win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1, 即 ±1 句窗)。须注意该键与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科保留判据) 是两个不同键、互不联动, 判据主体不同 (银行∧银行 vs 银行∧金科)。扫描口径与 _sent 一致 (prepend_title、标题为第 0 句、同一否定/短名排除源), 仅句窗半径由 0 放宽为 win_radius。由于 ±1 句窗边集包含同句边集又被同篇边集包含, 本列核序数在同一节点全集上逐点介于 _sent 与 canonical 之间。本列与 canonical 及 _sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 判据后缀 _win1 与三轨文本后缀正交, codebook 推断入口剥后缀后按基名归一 (否则 net_*_yr 的按 _yr 结尾联合判据会被后缀破坏落"未知")。win_radius 默认取 1 意味着两家银行相隔至多一句即算共现, 其松紧恰位于同篇与同句之间, 因而边集嵌套关系为同句 ⊆ 句窗 ⊆ 同篇, 本列核序数逐点介于 _sent 与 canonical 之间。相较同篇口径, 本列排除了"同篇但相隔数句以上"的远距离并置边, 削弱了跨段落榜单式共现的影响; 相较同句口径, 本列又保留了因断句/标点切分而被拆到相邻句的语义连续共现, 避免了严判据下因分句噪声而漏计真实并置。本列亦为纯整数拓扑量, 不涉浮点谱运算、不属 BLAS 非确定列, 可逐位复现; 它与 _sent、canonical 共同构成家族对"算共现"邻近标准松紧的判据敏感性梯子, 三者互为稳健性、不分主次、各自 just-identified, 禁混进同一 over-identified Hansen J, 三点的单调排序为核性度量对边定义松紧的稳健性提供可审方向。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Kirkley, A. (2025). Fast nonparametric inference of network backbones for weighted graph sparsification. Physical Review X, 15(3), 031013. https://doi.org/10.1103/4pg6-mtmt
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Robins, G., & Alexander, M. (2004). Small worlds among interlocking directors: Network structure and distance in bipartite graphs. Computational & Mathematical Organization Theory, 10(1), 69-94. https://doi.org/10.1023/B:CMOT.0000032580.12184.c0
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Ma, Y., & Zhao, J. (2024). Do interfund network centralities affect fund systematic risk? Evidence from China open-ended funds. Applied Economics. https://doi.org/10.1080/00036846.2024.2302932
Pang, C., Fan, H., Wu, J., Gao, Q., & Chen, N. (2025). Beyond single-network assumptions: structural uncertainty and systemic risk in financial networks. Applied Economics. https://doi.org/10.1080/00036846.2025.2597474
Guo, F., Lyu, B., Lyu, X., & Zheng, J. (2024). Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum. Abacus. https://doi.org/10.1111/abac.12341
<!-- rendered-citations:end -->
