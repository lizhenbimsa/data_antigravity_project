---
family_id: F080
columns:
- bank_cfbetween_cent
- bank_cfbetween_cent_sent
- bank_cfbetween_cent_win1
unit: 网络结构指标 (无量纲; networkx 归一化电流-流量介数中心度, 量级 ∈ [0,1])
formula: "bank_cfbetween_cent = current_flow_betweenness_centrality(G_lcc, weight=共现次数) 的节点值; G_lcc = 年度银行共现网络最大连通分量; 判据变体后缀 {同篇=无后缀 canonical / ±win_radius 句窗=_win1 / 严格同句=_sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (build_adjacency_matrix 建图); 列标签 news_process/pipeline/panel/export.py
upstream:
- 篇章级 both-verified 展开帧 df_exploded (docid / target_bank / year / 内容 / 标题 列; runner 步骤 7h-cent 输入, _win1/_sent 判据据此句级重扫)
- bank-year 面板骨架 panel (33 网络列 left-join 落点)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research (Advance online publication)
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
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
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
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: 2693
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
- doi: 10.1007/978-3-540-31856-9_44
  type: book
  authors: Brandes, U., & Fleischer, D.
  year: 2005
  title: "Centrality measures based on current flow"
  venue: "STACS 2005 (Lecture Notes in Computer Science, Vol. 3404)"
  pages_or_artno: 533-544
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
new_dois: []
---

## CORE

【构念与来源】
bank_cfbetween_cent 是"银行共现网络"节点级结构指标家族的 canonical 列, 度量单家银行在年度银行∧银行共现网络中充当"信息电流中转枢纽"的结构地位, 采用 Newman (2005) 提出的电流-流量介数中心度 (current-flow betweenness centrality, 亦称随机游走介数)。构念根植于社会网络分析对"中介性"(betweenness) 的经典刻画: Freeman (1978) 最早把介数中心度定义为"经过某节点的最短路径 (测地线) 占全网所有点对最短路径的比例", 用以识别处在信息必经之路上的守门人。然而 Freeman 口径隐含一条强假设——信息只沿最短路径传播、且传播者预先知晓全局最短路。对于媒体注意力、情绪、风险在银行体系内的扩散而言, 这条假设并不成立: 舆情并不知道最短路, 它更像电流一样沿所有可行路径按电导分流。Newman (2005) 正是为松弛该假设而提出电流-流量介数——把网络视作电阻网络, 每条边是一根电阻 (电导等于边权), 对每个源-汇点对在源端注入单位电流、在汇端抽出, 节点的电流-流量介数即为流经该节点的电流在所有点对上的平均值。Brandes 与 Fleischer (2005) 进一步给出其与随机游走介数的等价性刻画与快速算法, 奠定了该测度可在中大规模网络上稳定计算的工程基础。本项目把这一构念迁移到媒体共现语境: 若两家银行在同一篇 (或更严的同句窗) 新闻报道中被共同提及, 即视其在公众信息空间中被连接; 电流-流量介数高的银行, 处在众多其它银行对之间信息流动的中转位置, 具备把一处舆情或风险冲击向全网转导的结构潜能。

从随机游走视角看 (Newman 2005 的等价刻画), 电流-流量介数等于: 从源银行出发、以汇银行为吸收态的无偏随机游走, 期望经过中间银行的净次数在所有源-汇对上的平均。这一等价性使该测度获得一个直观的舆情语义——若把一则消息想象成在银行共现网上随机漫游的信息包, 电流-流量介数高的银行就是这些信息包在从任一银行流向另一银行途中期望频繁路过的中转站。与最短路介数只承认唯一最优路径不同, 随机游走承认所有路径并按其可达性加权, 因此它对网络中的冗余路径 (多条平行通道) 天然敏感: 当一个中转银行同时坐落在多条并行信息通道上时, 其电流-流量介数会显著高于仅按最短路计数的 Freeman 介数。这一性质对刻画银行体系的舆情与风险转导尤为重要, 因为现实中的信息与恐慌往往并不沿单一最优路径传播, 而是沿多条媒体叙事线并行漫灌; 电流-流量介数正是把这种多路径漫灌的中转贡献量化为单一节点标量的测度。

数据来源为篇章级 both-verified 展开帧 (df_exploded): 每篇报道经银行侧 (否定加短名过滤) 与金科侧判定后, 幸存的 target_bank 集合内每一无序银行对在当年邻接矩阵上加一, 逐篇累加得到年度加权共现网 (边权等于年内共现次数)。节点全集为当年幸存银行, 网络逐年重建 (银行-年面板)。喂入网络的报道宇宙即留篇 (both-verified) 集合, 而留篇门控自二零二六年六月二十九日起统一为 full-only 口径——即是否算作一篇银行金科报道只看 full 轨的 llm_verified_full, ctx 与 ss 降为 conditional-on-full 测度轨; 因此本家族三条判据变体 (见下) 均在同一个 full-only 留篇报道集合上操作, 判据后缀改变的只是边如何画, 绝不重新开闸留篇, 与 full-only 口径完全一致。

【方法学与计算】
计算入口为 network_spillover.py 的 compute_bank_network_centrality (建图原语 build_adjacency_matrix), 属 runner 步骤 7h-cent, 落列标签在 export.py 标为 Co-mention Current-Flow Betw (Newman 2005)。逐年流程: 其一, build_adjacency_matrix 按判据聚合出对称邻接矩阵与银行列表; 其二, 用共现次数为边权建原始图 G (含孤立节点); 其三, 识别最大连通分量 (LCC); 其四, 仅在 LCC 上调用 networkx 的 current_flow_betweenness_centrality 并传入边权。之所以限定 LCC, 是因为电流-流量介数需要连通图才有良定义的电阻网络解 (断连图的跨分量点对无电流路径); 落在 LCC 之外的银行该年该列取空值, 当 LCC 节点数少于二时全年置空。边权语义上共现次数越高电导越大、电阻越小、越易导流, 这与共现越频繁等于公众信息空间中关系越紧的直觉一致; 注意路径类指标 (如 closeness 与 harmonic) 另建倒数图 (距离等于共现次数的倒数), 而电流-流量介数直接吃电导 (共现次数本身), 两者建图口径不同, 不可混用。networkx 默认作归一化输出, 按点对规模量级归一, 故该列无量纲、量级落在零到一附近, 但因归一分母含当年 LCC 规模, 跨年水平仅在同规模网络间严格可比, 跨年比较应视作相对中转地位而非绝对流量。

三条判据变体的邻接构造在 build_adjacency_matrix 内分岔: 同篇 (article) 走 docid 聚合主路径, 对每个 docid 组内幸存的 target_bank 集合逐无序对加一, 每篇每对恰一次 (杜绝旧口径下 twin 行 1x 与 2x 混计以及把已被 verification 拒绝的银行列入 co_mentioned_banks 而产生的 phantom 边); win1 与 sent 走 docid 组内句级重扫路径——对每个多银行 docid 组, 取组首行的标题与正文, 以 prepend_title 把标题拼作第零句, 调用 map_bank_sentence_positions 定位每家银行 (经 get_target_aliases 别名展开、否定 AC 与短名排除过滤) 的句位集合, 再由 bank_pairs_within_sentence_window 按窗宽 (sent 取零、win1 取 win_radius) 枚举落在窗内的银行对并加一。三条判据的节点全集完全一致 (同为当年 df_year 幸存银行), 仅边集随判据收紧而单调变稀, win1 与 sent 的边集是 article 边集的子集。该分岔刻意复用与 stage 11、stage 13、ctx、ss 同一套否定与短名排除事实源 (禁裸 AC, 防涉农行业误判为农行), 确保跨阶段判定口径一致; 且句级重扫在 hyperedge_normalize 为真时对 win1 与 sent 路径显式 raise (防未接线的超边归一在判据轨无警告分叉)。win_radius 取自 config/panel.yaml 的 network_criteria.win_radius (默认一), 与 stage 13 银行∧金科的 cooccurrence_filter.sentence_radius 是两个不同键、互不联动——前者管银行∧银行邻接的句窗, 后者管银行∧金科硬过滤的句窗, 混用即口径错配。

家族共三十三个结构指标 (十八个节点级加十个网络级加五个 Gould-Fernandez 经纪角色), 其基名清单以 network_spillover 的 NETWORK_METRIC_BASES 为单一事实源 (SSOT), stata_export 标签机械块与 gate 测试均 import 复用防漂移; bank_cfbetween_cent 属其中节点级谱与结构组的第八项。

【文献定位】
电流-流量介数处在中心度测度谱系的流量-based 一端。谱系另一端是 Freeman (1978) 的测地线介数 (最短路), 退化到局部则是度中心度; 谱-based 一端有 Bonacich (1972) 的特征向量中心度 (以邻居的重要性递归定义) 与 Estrada 与 Rodríguez-Velázquez (2005) 的子图中心度 (以闭合游走计数刻画节点参与的子结构数)。Boldi 与 Vigna (2014) 用公理化框架系统比较了各类中心度对敏感度、单调性、规模等公理的满足情况, 指出没有一个中心度在所有公理下占优, 因此用一族而非单一测度刻画节点地位才是稳健做法——这正是本项目并排产出十八个节点级指标的方法论依据。由于共现网是加权网, Opsahl、Agneessens 与 Skvoretz (2010) 关于加权网络中心度 (把度与最短路推广到权重) 以及 Barrat 等 (2004) 关于加权复杂网络架构的工作, 支撑了以共现次数为边权的处理选择。网络的小世界与聚集背景由 Watts 与 Strogatz (1998) 奠定, k-核视角由 Seidman (1983) 提供 (对应家族内 bank_coreness)。在金融应用侧, 近年文献密集验证了中心度对资产定价与传染的解释力: Yu、Hu 与 Zhong (2024) 发现网络中心度经由信息扩散影响资产定价, Xu 与 Zhao (2024) 检验节点中心度对资产价格预测的贡献, Sadeghi 与 Feinstein (2024) 提出对金融网络传染中心度的统计验证框架, Nezami、Chisam 与 Palmatier (2025) 的元分析则量化了中心度与绩效关联的总体效应量。这些工作共同支持: 在媒体驱动的银行舆情网络中, 中转型中心度是刻画谁能把局部冲击转导为系统性传染的合适结构变量。

把电流-流量介数放进金融网络语境, 其核心价值在于对系统重要性的刻画区别于规模或声望型度量。规模型度量 (如资产) 回答谁大, 声望型度量 (特征向量、Katz) 回答谁的邻居重要, 而中转型的电流-流量介数回答谁的结构位置使其能够转导冲击。Yu、Hu 与 Zhong (2024) 与 Xu 与 Zhao (2024) 的实证提示, 中心度经由信息扩散渠道进入资产定价与预测, 意味着处在信息中转位置的银行, 其舆情更可能被市场当作对同业的先行信号; Sadeghi 与 Feinstein (2024) 则从统计验证角度警示, 金融网络中心度的点估计需配以对抽样与构造不确定性的稳健性评估——这与本项目用三判据梯子做规格稳健性、并在 golden 校验中显式登记该列非确定性的做法一脉相承。Nezami、Chisam 与 Palmatier (2025) 的元分析虽在企业绩效语境下得出中心度与绩效正关联的总体效应, 但也提示效应量随中心度类型与网络定义而异——这恰是本家族用一族测度乘以三判据、而非押注单一测度单一口径的现实理由。

【识别策略定位】
本列所属论文族为 brokerage_network (经纪网络), 其识别关切是"结构位置到银行结果"的因果或半因果关联: 一家银行是否因其在信息网络中处于中转枢纽位置, 而在融资成本、风险传染或同业模仿上表现出可辨识的差异。之所以选电流-流量介数而非度中心度来刻画这一位置, 是因为经纪 (brokerage) 的理论内核是"夹在原本断开的两方之间"所带来的中介租金与信息控制力: 度中心度只数直接邻居的多寡 (谁认识的人多), 而介数才刻画"多少他人之间的联系必经于我" (谁卡在别人中间); 电流-流量介数进一步把"必经"从最短路松弛为所有可行路径的电流加权, 使其对多路径冗余敏感, 更贴合舆情多线漫灌的传播机制。因此在本论文族里, 电流-流量介数是"中转型结构位置"这一处理变量的首选算子, 而非可随意替换的任意中心度; 若改用度或强度, 度量的构念就从"中介控制"退化为"关系数量", 与经纪理论错位。

网络型解释变量固有 Manski 反射问题与同群内生性: 当把同业的平均结果放进个体方程右侧时, 个体与同业互为因果, 系数不可识别。Bramoullé、Djebbari 与 Fortin (2009) 证明, 当网络存在非完全传递的结构 (即存在"朋友的朋友但非我的朋友"的间接联系) 时, 这些二阶邻居的外生特征可作为工具、经由网络拓扑本身达成识别; Grieser、Hadlock、LeSage 与 Zekhnini (2022) 在公司财务政策的网络效应研究中把这一思路落地为空间自回归设定, 以网络位置构造同群暴露、并用拓扑本身生成工具, 是与本论文族识别策略最接近的实证模板。须区分的是: 本项目的银行∧银行连边由媒体共现文本直接观测得到, 并不需要像 de Paula、Rasul 与 Souza (2024) 那样从面板数据的行为共动里反推潜在的网络连边——他们处理的是"网络不可观测、须从数据识别连边"的问题, 而共现网的连边是显式的文本事件, 这一侧的不确定性来自共现判据的界定 (故设三判据梯子) 而非连边存在与否的推断。但反射问题在结果 (outcome) 一侧依然成立: 一旦把同业情绪或同业结果按本列所隐含的结构位置加权进方程, Manski 式内生性仍在, 须用 Bramoullé 等 (2009) 的拓扑工具或 Bartik / shift-share 类外生份额构造来处理。

在本项目的落地上, bank_cfbetween_cent 既可作 Table 1 描述统计的结构位置刻画, 也可在识别设计中进入同群暴露或广义 Bartik 构造 (以结构位置作为暴露强度权重)。关键纪律: 判据敏感性 (同篇、win1、sent) 是规格稳健性并排, 三条判据各自 just-identified、互为稳健性、不分主次, 严禁把三判据变体同时塞进同一条 over-identified 回归再跑 Hansen J 过度识别检验——这会把同一构念的三种测量口径误当三个独立矩条件, 制造虚假的过度识别自由度, 使 Hansen J 的自由度与临界值均失真。该纪律与政治词权重梯子、词典消融梯度、co-primary 双轨嵌入、三轨文本的 Hansen J 隔离铁律同源。判据变体属规格曲线式并排, 刻意不设 rwolf 或 FWER 模板 (跨模型 rwolf 先例只覆盖同构念替代 headline 测量, 本族不适用)。

这一互为稳健性、不分主次、各自 just-identified 并排的架构, 与本项目其它梯子在方法论上完全同构: 政治词权重取零、零点五、一三档并排, 词典消融梯度在否定翻转、程度副词、转折三规则的全 powerset 上并排, co-primary 双轨嵌入 (Qwen 与 text-embedding-3-large) 并排, 三轨文本 (full、ctx、ss) 并排, LLM 三家与 BERT 三模型并排——所有这些梯子共享同一条铁律: 同一构念的多个测量口径各自单独进入 just-identified 设定、互相印证, 绝不被拼进同一条 over-identified 回归的矩条件集合去跑 Hansen J, 否则会把测量口径的多重性伪装成识别信息的多重性。判据敏感性 (同篇、win1、sent) 是这条铁律在银行∧银行邻接维度上的实例。另须注意, 本家族的三判据结构指标是同期 (contemporaneous) 度量, 与网络 W-轨里显式带 lag1 的同业情绪暴露 (如 bank_emb_sim_mean_lag1) 不同——判据梯子调的是邻接定义而非时间对齐, 二者是正交的设计维度, 使用者若需滞后结构位置, 须自行在面板上取 L1, 不可把判据后缀误读为时间口径。

【与相邻测度的构念区分】
最易混淆的相邻列是 bank_between_cent (家族 F079, Freeman 1978 最短路介数)。二者都叫介数、都刻画中转地位, 但底层流模型截然不同: Freeman 介数只计最短路, 对网络中次优但仍可行的旁路完全无视, 因而对个别边的增删极敏感、且在存在大量等长最短路时行为不稳; 电流-流量介数计入所有路径按电导加权, 对旁路的存在更敏感、对单边扰动更平滑, 更贴合舆情多路径漫灌式扩散。因此二者在同一网络上可给出显著不同的节点排序, 应作互补测度并排解读而非替代——这也是本项目按 Boldi 与 Vigna (2014) 的公理化多测度理念、并排产出一族而非单一介数列的直接体现: 没有单一介数在所有公理下占优, 故须以电流-流量与最短路两种介数并列刻画同一"中介"构念的不同侧面。

第二组须区分的是家族内的 Gould-Fernandez 经纪角色列 (gf_coordinator、gf_itinerant、gf_gatekeeper_rep、gf_liaison、gf_total)。它们与电流-流量介数虽同属"经纪 (brokerage)"大类, 但尺度与口径不同: GF 角色是局部的、基于三元组 (triad) 的、依赖群组划分的经纪计数——统计一个节点在多少个"甲经本节点连乙、而甲乙不直连"的三元桥接里充当中介, 并按甲、乙与本节点的群属把桥接细分为协调者、门房、代表、联络人等角色; 而电流-流量介数是全局的、基于路径的、无需群组划分的单一标量, 度量的是全网所有点对的电流有多少流经本节点。前者回答"我在哪些具体三元桥接里扮演何种角色", 后者回答"全网信息流整体上有多依赖我中转"。二者可正交并入模型: 一家银行可能 GF 桥接计数不高 (少有典型三元桥接) 却电流-流量介数很高 (坐落在众多长程路径的必经段上), 反之亦然。

第三组是结构洞家族 (bank_constraint、bank_effective_size、bank_ego_density、bank_ci)。这些列刻画的是自我网络 (ego-network) 内部的冗余度与结构洞富集度, 即"我的邻居彼此之间有多不相连", 属局部的、以本节点直接邻域为界的度量; 而电流-流量介数是跨全网点对的全局中介性。一家银行可能自我网络充满结构洞 (邻居互不相连、局部经纪机会多) 却在全网层面并非关键中转 (不落在多数长程路径上), 因此结构洞列与本列度量的是同一"经纪"母题下相互正交的两个层次 (局部邻域冗余 vs 全局路径中介), 不可相互替代。

第四组是路径可达性口径的 closeness 与 harmonic (家族 F083 与 F094)——它们刻画"到达他人有多快", 而电流-流量介数刻画"多少信息必经于我", 前者是自我-中心的可达性、后者是全网点对的中介性, 构念维度正交; 且二者建图口径不同 (可达性类另建距离等于共现次数倒数的图, 电流-流量介数直接吃电导), 已在方法学节说明, 不可混用建图口径。与谱-based 的 eigen、katz、subgraph 相比, 后者刻画"邻居有多重要"的递归声望 (你被重要的人连接就重要), 与"处在多少点对之间"的中介性亦不同——一个节点可以声望极高却不中介 (居于致密核心内部), 也可以声望平平却是关键桥 (居于两簇之间)。

最后须从二模网络投影的角度厘清共现网的本质: 银行∧银行共现网并非天然的一模网络, 而是"文章×银行"二模隶属网络 (affiliation network) 在银行端的一模投影——每篇报道是一个隶属事件, 把其提及的全部银行连成一个团 (clique)。Faust (1997) 对隶属网络中心度的分析指出, 这类投影会系统性放大共同出现在大型隶属事件里的节点的中心度: 一篇同时点名 N 家银行的榜单, 在投影后贡献 C(N,2) 条等权边, 使这些银行的介数被单一隶属事件抬高。理解这一投影机制, 既解释了下节讨论的超边膨胀从何而来, 也说明了为何三判据梯子 (尤其 _win1 与 _sent) 通过要求更强的语义邻近, 能部分抑制大型隶属事件对投影中心度的机械抬升。

判据后缀 (无后缀、_win1、_sent) 与三轨文本后缀 (_full、_ctx、_ss) 是两个正交的概念空间: 前者调银行∧银行邻接的严格度, 后者调银行∧金科文本范围, 二者禁混进同一 Hansen J。

【已知局限与稳健性梯子】
第一大局限是 BLAS 浮点非确定性。电流-流量介数需对图拉普拉斯做 (伪) 逆与稠密线性代数分解, 底层 LAPACK 与 BLAS 的线程归约次序不可结合, 导致跨次运行结果非逐位可复现。bank_cfbetween_cent 与 bank_clustering、bank_harmonic_cent 一道, 是本项目登记在案的 BLAS-FP 非确定列; 判据分轨后, 三基名乘以无后缀、_win1、_sent 三判据共九列均受此影响。因此 golden 零漂移校验须按全名 drop 排除这九列, 重生 golden 须钉死 PYTHONHASHSEED=0 且全 BLAS 线程数为一 (MKL、OPENBLAS、NUMEXPR、OMP 均设一) 才能把非确定源压到最小。须强调该非确定性完全来自稠密线代分解的浮点归约次序, 与 LLM 或嵌入缓存无关——本列是纯 CPU 网络指标, 即便上游 LLM 命中缓存离线零成本复现, 该列仍须按全名从逐位校验中排除; 换言之, 离线可复现保证的是"不再付费调用与上游数值一致", 不保证本列逐位一致。

第二是超边膨胀, 其根源即上节所述的二模投影机制: 一篇提及 N 家银行的榜单或批量监管通报文章贡献 C(N,2) 条等权边, 大-N 文章可凭边数机械主导网络, 使这些银行的介数被单一隶属事件抬高而非源于真实的信息中转。生产默认仍每对加一 (golden-safe), 预留 Newman degree-preserving 归一选项 (hyperedge_normalize) 但判据分轨路径尚未接线 (win1/sent 路径在该开关为真时显式 raise, 防未接线的归一在判据轨无警告分叉)。三判据梯子是对超边膨胀的一线防御: _win1 与 _sent 通过要求同句或近句共现, 天然过滤掉仅因同列一张榜单而共现的弱关联。第三, LCC 限定使非最大连通分量与孤立银行取空值 (LCC 节点数少于二时全年置空), 在稀疏年份 (尤其 _sent 严判据下) 空值比例升高, 回归时须显式处理缺失机制, 不可把这一结构性缺失误当随机缺失。第四, 归一分母含当年 LCC 规模, 跨年水平不可直接比较, 升为回归 RHS 前宜先做 within-bank 标准化或规模校正, 否则年际网络规模波动会经乘性重标度混入系数, 且无法被加性年固定效应吸收。

最后一层构念局限须显式披露且最为根本: 媒体共现是公众信息空间中的关联, 不等于银行间的真实经济纽带 (同业拆借、担保、股权)。两家银行频繁共现, 可能仅因它们同属某类被媒体成组报道的对象 (如同批被监管点名、同列一张榜单), 而非因其存在业务往来。与之对照, 文献中已有直接观测真实经济纽带的银行网络: Gao、Ru 与 Yang (2022) 研究银行间共同持股的所有权网络对信贷的信息作用, Wang、Zhang 与 Yang (2020) 刻画金融危机与刺激计划下中国担保网络的演化——这些是有法律与合约支撑的真实纽带, 而本列的媒体共现只是其带噪代理。因此本列刻画的是媒体信息网络中的中转地位, 对经济传染网络中的中转地位只是一个带噪代理; 解读时应克制把它直接读作系统性风险中转的冲动, 而将其定位为媒体注意力与舆情转导的结构变量。近期已有工作探索从文本直接构造金融网络并度量连通性: Li 等 (2026) 从上市公司的文本风险披露里抽取金融网络结构与连通度, 与本项目从媒体共现构造银行网络同属"文本→网络"路线, 也共享同一方法论要求——文本派生的网络指标须配以对构造口径的稳健性验证, 不可只报单一口径。这正是三判据梯子的用武之地: 越严的判据 (同句) 越接近银行被真正放在同一语义情境中讨论, 越宽的判据 (同篇) 越可能纳入榜单式弱共现, 二者并排可帮助研究者判断结论对共现语义强度的敏感性。Sadeghi 与 Feinstein (2024) 亦强调金融网络中心度需统计验证, 判据敏感性正是本项目对此的落地手段之一: 同篇口径最宽、边最密; ±1 句窗 (_win1) 收紧到局部邻近; 严格同句 (_sent) 最严、边最稀。三者刻画同一中转地位构念在不同邻接严格度下的稳健性, 结论若不被判据取值驱动方为可信。稳健性重生的确定性配置须与项目 golden 铁律一致: 除钉死 PYTHONHASHSEED 与全 BLAS 线程数为一外, 涉 LLM 与嵌入的上游若命中缓存可离线零成本复现, 但本列的非确定性与 LLM 缓存无关, 故即便离线复现, 该列仍须按全名从逐位校验中排除。

## VAR: bank_cfbetween_cent

【变体差分】
本列是家族 canonical (无判据后缀), 对应同篇共现判据 (criterion 取 article): 只要两家银行在同一篇 both-verified 报道 (同 docid) 中被共同提及, 当年邻接矩阵对应无序对即加一, 每篇每对恰计一次 (docid 聚合口径, 杜绝 twin 行 1x 与 2x 混计以及 phantom 边)。这是三条判据里最宽松的邻接定义, 因而网络最稠密、LCC 最大、取空值的银行最少, 也是现行生产的默认口径与 Table 1 描述统计消费的列。其数值语义已在 CORE 详述: 年度银行共现网 LCC 上的 Newman (2005) 电流-流量介数, 边权等于共现次数 (电导), networkx 归一化输出, 量级落在零到一附近。

作为 canonical, 它承担家族的主测量角色, _win1 与 _sent 是它的判据稳健性臂。三者构念相同 (中转地位), 仅边如何画不同, 各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。需再次强调无后缀仅是历史命名产物、代表同篇这一最宽判据, 并不意味它比 _win1 或 _sent 在方法论上更正确; 三者是并排的规格稳健性梯子。与家族内 Freeman 最短路介数 bank_between_cent 的区别 (流模型: 所有路径按电导 vs 仅最短路)、与 closeness 及 harmonic (可达性 vs 中介性)、与 eigen 及 katz (声望 vs 中介) 的区别均见 CORE。

本列的三判据变体是九个 BLAS-FP 非确定列之一, 跨次非逐位可复现, golden 校验须按全名排除。作为核心列, 它在识别设计里可进入结构位置类解释变量或同群暴露构造, 但其归一分母含 LCC 规模、跨年水平不可直接比, 升 RHS 前须做规模校正或 within-bank 标准化——这一点比宽松判据带来的稠密网收益更值得在建模时优先处理。由于同篇判据最宽, 本列对超边膨胀也最敏感: 一篇同时点名众多银行的行业榜单或批量监管通报, 会在本口径下一次性注入大量等权边, 使这些银行的共现度与中转介数被单篇放大; 从二模投影视角看 (Faust 1997), 同篇口径正是把"文章×银行"隶属网络原样投影到银行端、每个大型隶属事件都生成一个完整团, 因而本 canonical 列承受的投影膨胀在三判据中最重。_win1 与 _sent 因要求同句或近句共现, 天然过滤掉仅因同列一张榜单而共现的弱关联, 对超边膨胀的抵抗力更强。因此当研究者担心榜单类文章驱动结果时, 应优先参照 _win1 与 _sent 臂; 当关注广义同篇语境下的信息中转时, 本 canonical 列信息量最饱满。两种关切的答案若一致, 才说明中转地位的估计不被邻接口径的松紧驱动。

在计量落地上, 本 canonical 列是家族三判据比较的参照臂: 稳健性表通常以本列为主设定, 再以 _win1 与 _sent 作并排列展示系数在邻接口径收紧下的稳定性。由于同篇网最密, 本列的可估格子最多 (空值最少), 在 T=2 开发语料这类稀疏样本上, 它往往是三判据中唯一非退化的一列——这既是它作为 canonical 的实用理由, 也提醒使用者: 若主结论只在最宽判据下成立、在 _win1 与 _sent 下消失, 则很可能由榜单式弱共现驱动, 须审慎。本列与家族内认知邻近 (bank_cogn_mean)、嵌入相似 (bank_emb_sim_mean) 等 W-轨度量不同: 后者刻画银行内容或语义的相似度 (是谁像谁), 本列刻画信息流的中转位置 (是谁夹在中间), 二者可同时进入模型作正交的结构控制。需再次强调, 本列升为回归右侧变量前, 因其归一分母含当年 LCC 规模而具跨年不可比性, 宜先做 within-bank 去均值或全样本标准化, 否则年际网络规模波动会经乘性重标度混入系数, 且无法被加性年固定效应吸收——这一乘性重标度隐患与本项目对 bank_strength_cent 年相对归一的披露口径同源。

## VAR: bank_cfbetween_cent_sent

【变体差分】
本列采用最严判据 (criterion 取 sent, 严格同句, radius 为零): 仅当两家银行在同一篇报道的同一个句子内被共同提及, 才在当年邻接矩阵上计一条边。判据原语为 entity_context 的 map_bank_sentence_positions 定位各银行的句位、再由 bank_pairs_within_sentence_window 以窗宽零取严格同句对; 扫描文本为 prepend_title 后的全文 (标题作第零句, 镜像 stage 13 的 match_in_title 口径), 银行别名经 get_target_aliases 展开并套用否定加短名排除 (防涉农行业误判为农行的假阳性)。相对同篇 canonical, 同句判据把共现收紧到最强的语义邻近, 边集最稀、网络最碎、LCC 最小, 因而取空值的银行最多、电流-流量介数的可估格子最少; 在开发期 T=2 语料上尤易退化。

它与无后缀 canonical、_win1 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三判据同塞一条 over-identified 回归跑 Hansen J。判据后缀与三轨文本后缀 (_full、_ctx、_ss) 正交: 前者调银行∧银行邻接严格度, 后者调银行∧金科文本范围, 二者禁混同一 Hansen J。本列亦属九个 BLAS-FP 非确定列之一 (bank_cfbetween_cent 基名的 _sent 变体), 跨次非逐位可复现, golden 校验按全名 drop。config 记录键为 panel.yaml 的 network_criteria (win_radius), 与 filtering.yaml 的 cooccurrence_filter.sentence_radius (stage 13 银行∧金科) 是不同键、互不联动。作为最严臂, 若同句口径下的中转地位排序仍与同篇口径一致, 则最有力地证明结论不被仅因同篇而共现的弱关联驱动。

三点实现细节影响解读: 其一, 三判据的节点全集完全一致 (同为当年 df_year 幸存银行), 本列相对 canonical 变化的只是边集, 且边集满足严格嵌套——同句边集是句窗边集的子集、句窗边集是同篇边集的子集, 因此本列的空值集必是 canonical 空值集的超集, 三判据比较时须先对齐到共同可估样本再比系数, 否则样本构成差异会与判据效应混同。其二, 判据原语 (map_bank_sentence_positions 加 bank_pairs_within_sentence_window) 是审计脚本与生产共用的同一函数 (审计等于生产), 复核本列时不存在第二套并行实现造成的口径漂移。其三, hyperedge_normalize 开关在本判据路径未接线、为真时显式 raise 而非静默跳过, 故本列数值恒为每对加一的原始口径, 不存在被隐式归一污染的可能; 同句判据本身已是对超边膨胀最强的结构性防御——一篇点名众多银行的榜单极少把多家银行写进同一个句子, 故榜单式弱共现在本列中被机械剔除, 这也是它作为最严稳健性臂的构念价值所在。

## VAR: bank_cfbetween_cent_win1

【变体差分】
本列采用中间判据 (criterion 取 win1, ±win_radius 句窗, 生产 win_radius 为一): 两家银行须在同一篇报道内相隔不超过一个句子 (同句或相邻句) 被提及, 才计一条边。它介于同篇 canonical (最宽) 与严格同句 _sent (最严) 之间, 网络稠密度、LCC 规模、空值比例均处中位。判据原语同 _sent (map_bank_sentence_positions 加 bank_pairs_within_sentence_window), 差别仅在窗宽取 win_radius 为一而非零; 扫描文本同为 prepend_title 全文 (标题第零句), 套用同一否定加短名排除事实源。win_radius 取自 config/panel.yaml 的 network_criteria.win_radius (默认一), 与 stage 13 银行∧金科的 cooccurrence_filter.sentence_radius 是不同键、互不联动。

_win1 的设计意图是提供局部语义邻近但不至严苛到同句的中间稳健性档: 它过滤掉仅同篇但相隔甚远的弱共现 (抵抗榜单类超边膨胀), 又保留了跨相邻句的正常叙述性共现。它与无后缀 canonical、_sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀正交, 亦禁混同一 Hansen J。本列同属九个 BLAS-FP 非确定列之一 (cfbetween 基名的 _win1 变体), 跨次非逐位可复现, golden 零漂移校验按全名排除。与 _sent 相比, _win1 允许跨相邻句的共现, 因而在保留正常叙述性关联的同时仍能剔除相隔甚远的同篇弱共现, 是三判据梯子里兼顾覆盖率与语义强度的折中档; 在 _sent 因过稀而大面积退化的稀疏年份, _win1 常是比 _sent 更可用、又比同篇更严格的稳健性参照。三判据并排读出的中转地位若单调稳健, 方说明电流-流量介数估计不被邻接窗宽驱动。

两点须记录的语义边界: 其一, 本列的边集嵌套在同篇边集之内、又包含同句边集 (节点全集三判据恒同), 故其网络稠密度与空值率必然落在两端之间, 与 canonical 或 _sent 比较系数时同样须先对齐共同可估样本。其二, 本列语义与 win_radius 配置值绑定——列名后缀 win1 固化的是生产默认窗宽一, 若 config 中 network_criteria.win_radius 被改动, 重建后的列仍叫 _win1 但实际窗宽已变, 复现与审计时应以 config 记录键的当次取值为准核对口径, 这也是该键被显式登记为 config 记录键的原因。与 _sent 相同, hyperedge_normalize 在本判据路径为真时显式 raise, 本列恒为每对加一原始口径; 判据原语与审计脚本共用同一函数, 无并行实现漂移。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research (Advance online publication). https://doi.org/10.1007/s10479-026-07305-8
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Brandes, U., & Fleischer, D. (2005). Centrality measures based on current flow. STACS 2005 (Lecture Notes in Computer Science, Vol. 3404). https://doi.org/10.1007/978-3-540-31856-9_44
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 23619. https://doi.org/10.1103/PhysRevE.71.056103
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
<!-- rendered-citations:end -->
