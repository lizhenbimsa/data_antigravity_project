---
family_id: F464
columns:
- net_modularity_yr
- net_modularity_yr_sent
- net_modularity_yr_win1
unit: 无量纲模块度分值 Q (取值区间约 [-0.5, 1); 网络级年度标量, 同年全体银行共享)
formula: "net_modularity_yr = modularity(G, C, weight='weight'); C = greedy_modularity_communities(G, weight='weight') (Clauset-Newman-Moore 2004 贪心社区检测); G = 年度银行共现加权无向图"
producer: news_process/pipeline/panel/network_spillover.py::_net_level_extra_metrics ; news_process/pipeline/panel/export.py (标签注入)
upstream:
- 13_cooccurrence_filter.parquet
- 40_panel_yearly.parquet (银行-年面板骨架)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: 10.1371/journal.pone.0324981
  type: journal
  authors: Jiang, J., Jiang, X., Yan, Y., Xie, S., & Yao, J.
  year: 2025
  title: "Alliance-based modeling of interbank lending networks: Insights into risk contagion dynamics"
  venue: PLOS ONE
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
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
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
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"年度银行共现网络的社区分化程度", 以网络模块度 (modularity, 记作 Q) 为核心测度。构念的实体来源是新闻文本: 当同一篇 (或同一句窗内) 报道同时提到两家或以上银行时, 这两家银行之间即建立一条"共现边", 一年内所有此类共现在银行节点上累积成一张加权无向图 G。模块度衡量的是这张图能被划分成"内部致密、彼此稀疏"的社区结构的强弱: Q 越高, 说明当年的媒体叙事越把银行分割成若干相对独立的报道簇 (例如国有大行一簇、区域城商行一簇、涉某类事件的机构一簇); Q 越低乃至趋近于零, 说明银行之间的共现更接近随机混合, 没有清晰的板块边界。它不是刻画某一家银行在网络中的位置 (那是中心度家族的职责), 而是刻画整张年度网络的"宏观拓扑形态", 因此是一个网络级 (net-level) 而非节点级的标量: 同一年内所有银行共享同一个 net_modularity_yr 取值。

数据链路上, 银行共现的原始判定发生在 stage 13 共现硬过滤及其上游的实体识别: 银行侧采用否定加短名过滤 (防"涉农行业"误触发"农行"这类假阳性), 以 core/text/entity_context 中的银行句位映射原语为准。年度网络的构造与全部结构指标的计算集中在 pipeline/panel/network_spillover.py 的 compute_bank_network_centrality 与其抽出的纯函数 _net_level_extra_metrics 中; export.py 只负责把英文标签 (Annual Co-mention Modularity, CNM 2004) 注入面板导出层, 不参与数值计算。需要强调的是: 本家族的共现判据主体是"银行∧银行"的邻接关系, 与三轨文本 (full/ctx/ss, 那是"银行∧金融科技"口径) 是两个正交的概念空间, 严禁把两者的后缀或语义混为一谈。

【方法学与计算】
模块度的计算分两步, 均在加权图上进行且完全确定性、无随机数发生器介入, 故对 golden 快照安全。第一步是社区检测: 调用 networkx 的 greedy_modularity_communities(G, weight='weight'), 即 Clauset-Newman-Moore (2004) 贪心凝聚算法——从每个节点自成一社区出发, 每步合并使 Q 增量最大的两个社区, 直至无法再提升。第二步是打分: 对上一步得到的社区划分 C, 调用 nx.community.modularity(G, C, weight='weight') 求出 Q。这里有一个刻意固定的口径细节 (源码 §3.1 Q2/R10 记载): 检测与打分两步都显式传 weight='weight'。若不显式指定, greedy_modularity_communities 默认 weight=None 而 modularity 默认 weight='weight', 两者口径不一致会导致划分与打分错配、甚至使 Q 出现符号翻转。因此本实现把两步锚死在同一加权口径上, 保证内部自洽。边权 weight 取该对银行当年的共现频次 (或其等价累积计数), 使高频共现的银行对在社区划分中获得更大话语权。

守卫逻辑上: 当年度图无边 (G.number_of_edges()==0) 时直接置 NaN; 当 greedy 或 modularity 抛出 ZeroDivisionError / NetworkXError / ValueError (退化拓扑如全孤立点、单边对) 时捕获并置 NaN 并记 warning, 绝不返回一个虚假的零值。取值区间上, 模块度理论上落在约 [-0.5, 1) 区间: 正值表示存在优于随机的社区结构, 接近 0 表示无显著社区结构, 负值 (罕见) 表示比随机划分还要"反社区"。Newman & Girvan (2004) 给出了 Q 的原始定义与评估框架, 是本测度的方法学锚点。

从测度公式看, 模块度的直觉是"实际落在社区内部的边权占比"减去"在保持度分布的随机零模型下期望落在社区内部的边权占比": 若一个划分下社区内部边显著多于随机期望, 差值为正且越大表示社区结构越强。这一"实测减随机期望"的构造使 Q 具有天然的基准校正性质——它不会因为图整体变稠密就自动升高, 而是度量"结构化程度"相对随机的超额。也正因如此, Q 对图的规模与稀疏度并非尺度不变: 不同年份、不同判据下节点数与边数变化会影响 Q 的可比性, 跨年比较时须谨慎, 更稳妥的做法是把 net_modularity_yr 作为随时间演化的状态序列观察其相对高低, 而非绝对水平的机械对照。贪心 CNM 算法给出的是模块度的一个近似最大化解 (模块度精确最大化是 NP 难), 但因其确定性 (无随机重启、无 RNG)、对同一输入图恒返回同一划分, 保证了跨 run 的字节级可复现, 契合本项目的 golden 锚定纪律。边权来源于共现频次, 使得"被反复一同报道"的银行对在社区归并中权重更高, 从而让高频关联主导板块边界的划定。

值得补充的是, 本家族只落地 net_modularity_yr 这一无向加权口径, 未派生加权孪生 net_modularity_hn_yr (团投影去重/半正规化变体)。须精确澄清 _net_level_extra_metrics 这一纯函数的实际产出边界: 该函数在同一张只读年度图 G / 巨连通分量 G_lcc / 分量集上一次性返回 6 个网络级标量——模块度本身, 加上度相关性 (assortativity)、传递性 (transitivity)、直径 (diameter)、巨片占比 (giant_share)、连通分量数 (n_components) 这 5 个兄弟指标, 因此与 net_modularity_yr 严格"同批、同图、同函数"算出的兄弟列只有这 5 个。而同属网络级家族的另外 4 个指标——密度、平均聚类、平均路径、度基尼——并不在 _net_level_extra_metrics 内计算, 由本函数之外的其它计算路径产出, 不可将其误并入"与模块度同批算出"的清单。上述 5 个兄弟指标与模块度共享同一只读图对象、不重建图 (加性铁律), 因此不扰动既有 BLAS 敏感列的哈希。这一"只读复用、抽纯函数"的实现方式既保证了新增列 golden-safe, 又便于对各拓扑分支 (空图、单边、单分量、多分量) 直接单测。

【文献定位】
模块度源自复杂网络的社区检测文献, Newman & Girvan (2004) 是其奠基性定义, 把"社区结构强弱"操作化为一个可优化的标量, 随后 Clauset-Newman-Moore 的贪心算法使其在大规模网络上可高效计算——本实现正是采用该贪心变体。在金融网络这一应用侧, 近年文献把社区检测与模块度直接用于刻画金融机构的板块化: Jiang 等 (2025) 将社区检测与模块度用于银行间借贷网络的风险传染建模, 是与本列构念最贴近的近期金融应用; Li 等 (2026) 从文本风险披露中还原金融网络结构与连通度, 与本项目"从新闻文本构造银行网络"的路径同源。更广的网络结构—绩效关系上, Nezami 等 (2025) 以元分析综合了网络中心度与企业绩效的关系 (但该文献不背书任何具体的银行聚类列, 仅作构念对话对象), Yu 等 (2024) 讨论网络中心度、信息扩散与资产定价。金融网络的系统性风险视角由 Jackson & Pernoud (2021) 的综述统摄, Gao 等 (2022) 则从所有权网络的信息角色切入银行放贷, 为"银行网络结构承载信息外溢"提供了机制叙事。

需要澄清本测度与既有金融网络文献在"网络来源"上的差异: 上述金融文献多以真实的借贷敞口、担保关系、所有权链条或价格连通度构造网络 (如 Jiang 等 2025 的银行间借贷网、Gao 等 2022 的所有权网), 而本项目的银行网络是"媒体共现网"——边的语义是"被同一篇/同一句报道一同提及", 承载的是媒体注意力与叙事关联, 而非资金或产权的实体连接。这一区别决定了 net_modularity_yr 的板块结构应被解读为"舆论上被打包看待的银行群组", 与借贷网络的风险传染社区不必重合, 但两者可能因共同的行业冲击或监管事件而相关。Li 等 (2026) 从文本风险披露还原金融网络的做法, 恰恰印证了"从文本构造金融网络并计算其结构指标"这一方法路径的合法性与前沿性, 是本家族方法学上最直接的同类对话。就"网络作为溢出通道"的经济学含义, Grieser 等 (2022) 与 Boucher 等 (2024)、Bramoullé 等 (2020, 2009) 一脉的同伴效应文献提供了把网络拓扑接入结果方程的规范框架, 也提醒使用者网络结构量往往内生于未观测冲击、其系数须审慎解读。

【识别策略定位】
本家族在计量识别中的定位需格外谨慎, 这也是它被标注"年 FE 下不可识别 (year-FE absorbed)"的原因: net_modularity_yr 是网络级年度标量, 在同一年内对所有银行取同一数值, 因此一旦回归纳入年份固定效应, 该列会被完全吸收、系数不可识别。它只能在两类设定中进入右手边: 其一是不含年 FE 的设定 (例如以时间趋势或宏观控制替代年 FE); 其二是与银行级异质性变量的交乘项 (net_modularity_yr × 银行特征), 交乘后跨银行有变异, 得以在年 FE 下存活。因此本列的主要用途是"网络环境状态量"——刻画某一年整个银行舆论网络的板块化强度, 作为溢出效应 (peer effect) 的调节或情境变量, 而非直接的处理变量。社会网络中的同伴效应识别本身就受反射问题 (reflection problem) 与内生网络的困扰, Manski 传统由 Bramoullé 等 (2009) 与其综述 Bramoullé 等 (2020)、以及 Boucher 等 (2024) 的一般理论所推进; Grieser 等 (2022) 在公司财务政策的网络效应中给出了实证范式。使用本列作情境调节时, 须承接这套识别谱系的告诫: 网络拓扑与被解释结果可能同源于未观测的行业冲击, 模块度的系数应作关联性而非因果性解读。更具体地, 反射问题指的是"个体行为与其参照群体的平均行为互为因果"这一联立性: 若把年度模块度理解为对同伴效应强度的间接刻画, 则当年被媒体切分成板块的强弱本身可能既是同伴传导的结果、又是其成因, 单靠横截面相关无法把二者拆开。Bramoullé 等 (2009) 证明了在网络结构非完全 (即存在"朋友的朋友不是朋友"的三元开放结构) 时, 内生、外生与相关效应可借助网络的高阶邻接矩阵获得识别, 这为把网络结构量接入结果方程提供了理论出口; 但该识别依赖网络外生 (edge 的形成与误差项无关) 这一强假设, 而媒体共现网的边恰恰由不可控的新闻生产过程决定, 外生性难以先验成立。因此本项目对 net_modularity_yr 的定位保守: 它进入右手边时首选作与银行特征的交乘调节项 (让识别来自跨银行的异质响应而非网络级水平本身), 或作时代情境的描述性状态量, 而不主张对其系数作结构式因果解释。Boucher 等 (2024) 的一般理论进一步表明, 同伴效应的函数形式 (线性均值 vs 更一般的分布依赖) 会显著改变可识别的参数集, 提示使用者在把模块度这类聚合网络量纳入模型时须对设定的函数形式保持透明。

【与相邻测度的构念区分】
net_modularity_yr 属于 NETWORK_METRIC_BASES 定义的 33 个结构指标基名中的 10 个"网络级"指标之一, 需与同族相邻测度严格区分。与聚类/传递性 (net_avg_cluster_yr / net_transitivity_yr) 的区别: 后两者刻画"局部三角闭合"即朋友的朋友也是朋友的倾向, 是微观致密度; 模块度刻画的是"全局板块切分"即整张图能否被切成边界清晰的社区, 是宏观分化度——一张高传递性的图未必高模块度 (可能是一个致密的大团块), 反之亦然。这一区分可借小世界网络的经典刻画看清: Watts & Strogatz (1998) 指出真实网络往往同时具备"高聚类系数"与"短平均路径"两个特征, 高聚类正是三角闭合密集的微观致密度, 而它与是否存在清晰的宏观板块 (高模块度) 是两个可各自独立取值的维度——小世界网络可以在整体高聚类的同时并不呈现分明的社区边界, 这恰说明聚类/传递性与模块度度量的是网络拓扑的不同层面。与度分布基尼 (net_degree_gini_yr)、度相关性 (net_assortativity_yr) 的区别: 后两者刻画度的不平等与同配性, 是度序列的一维统计, 不涉及社区划分。与巨片占比 (net_giant_share_yr)、连通分量数 (net_n_components_yr) 的区别: 后两者是连通性指标, 一张全连通图 (单一分量、巨片占比为 1) 内部仍可有很高的模块度。特别提示两处口径披露 (源码 §3.1 Q2): net_transitivity_yr 与 net_modularity_yr 都会被"多银行同现的单篇报道"投影成的团 (clique) 向上虚增——一篇同时点名 N 家银行的报道会在图上生成一个 N 团, 人为抬高致密度与社区结构; transitivity 因忽略权重无加权孪生, 而 modularity 因加权可派生出加权变体 net_modularity_hn_yr (本家族当前不含该孪生列)。

再从计量角色上区分: 与节点级中心度家族 (bank_degree_cent、bank_eigen_cent、bank_between_cent 等 18 个) 相比, 那些列在同一年内跨银行有变异、可在含年 FE 甚至银行×年双向 FE 的设定中识别, 是刻画"单家银行网络地位"的处理/控制变量; 而本家族的 net_*_yr 是网络级年度广播量, 年内对全体银行恒定, 在含年 FE 时被完全吸收。这一根本差异决定了两类指标在同一回归里的分工: 中心度作个体处理量, 网络级模块度作时代情境量或交乘调节量, 二者互补而非替代。与经纪角色家族 (Gould-Fernandez 的 gf_coordinator 等 5 列) 相比, 后者刻画节点在跨群中介中的具体角色, 是结构洞理论下的中介性度量, 关注"谁在连接不同板块"; 而模块度关注"板块本身是否清晰存在", 两者恰构成"板块内部结构 (谁是桥) 与板块整体分化 (板块有多分明) "的一体两面。使用者若同时纳入模块度与经纪角色, 应意识到二者度量的是社区结构的不同层面, 并非冗余。再与网络中心度—绩效的实证脉络对齐: Nezami 等 (2025) 的元分析综合了大量"中心度→企业绩效"的研究, 指出中心度效应的方向与量级高度依赖于中心度的具体算子 (度、介数、特征向量) 与情境, 这一提醒同样适用于网络级结构量——模块度对结果的关联并非普适常数, 而随行业结构、样本期与网络构造口径而变, 故本家族坚持以三判据梯子并置报告而非单点断言 (须重申: 该元分析不背书本项目任何具体的银行网络列, 仅作构念对话)。Yu 等 (2024) 从中心度、信息扩散与资产定价的角度说明网络位置如何调制信息在节点间的流动, 由此反推: 当整张网络高度模块化 (Q 高) 时, 信息扩散更可能被板块边界所阻隔、局限于簇内, 这正是把模块度理解为"信息传导情境量"的经济学依据。与系统性风险文献 (Jackson & Pernoud 2021 的综述) 的边界也需澄清: 该脉络的社区指的是"风险传染在其内部快速蔓延的机构簇", 边的语义是资金/敞口连接; 而本家族的社区是"被舆论打包看待的银行群组", 边的语义是媒体共同提及——两者可能因共同冲击而相关, 但绝不能等同, 把媒体共现网的高模块度直接读作"风险传染社区清晰"是构念误用。此外, 本家族的判据敏感性梯子与节点级中心度中受 BLAS 浮点影响的非确定列在数值纪律上分属两类: 模块度三判据变体均为确定性 golden-safe 列, 而 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的三判据共 9 列才是需在零漂移验证时按全名 drop 排除的 BLAS 敏感列, 二者不可混淆。其中 bank_cfbetween_cent 属电流流/随机游走型介数中心度, 其理论源正是 Newman (2005) 提出的基于随机游走的介数中心度测度——它不像最短路介数那样只沿测地线计数, 而是以随机游走在节点间流动的期望通过量刻画中介性, 因而对稠密加权图的中间桥接更敏感; 该类测度的迭代/线性代数求解正是其在浮点重排下非逐位可复现 (BLAS 敏感) 的根源, 与确定性的模块度形成鲜明对照, 进一步印证网络级模块度与节点级中介测度在数值纪律与构念上均分属两类。

【已知局限与稳健性梯子】
第一, 团投影虚增 (如上): 同篇多银行报道天然生成完全子图, 使模块度对"报道的篇幅广度"敏感而非纯粹的银行关系, 解读时须警惕。第二, 年 FE 不可识别 (如上): 决定了它只能作情境/交乘变量, 不能作独立处理变量。第三, 判据敏感性: "两家银行是否算共现"这一判定本身有口径自由度, 本家族据此给出三个判据变体——同篇 (无后缀 canonical)、±1 句窗 (_win1)、严格同句 (_sent), 分别对应"松—中—紧"的邻接门槛。这三个判据变体是本家族稳健性梯子的骨架: 它们各自 just-identified 并排、互为稳健性、不分主次, 证明主结论不被某一特定的共现判据取值驱动; 铁律是三判据严禁混进同一 over-identified Hansen J 检验 (与三轨文本、co-primary 双轨嵌入的并排口径同源)。需注意判据后缀 (_win1/_sent) 与三轨文本后缀 (_full/_ctx/_ss) 是两个正交概念空间, 前者是银行∧银行邻接门槛, 后者是银行∧金融科技的文本范围, 不可互相复用或混淆。第四, 数值确定性的例外: 模块度本身无 RNG、golden-safe, 但同族部分谱依赖的中心度列 (bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的三判据变体共 9 列) 受 BLAS 浮点重排影响非逐位可复现; net_modularity_yr 不在该非确定清单内, 属确定性列。第五, 退化拓扑: 在开发期 T=2 的极小样本上, 年度图可能过于稀疏使社区结构不显著或触发 NaN 守卫, 属预期退化; 生产 T=18、全量 1700 万条语料下网络方具备统计意义上的板块结构。判据口径记录键为 config/panel.yaml::network_criteria (win_radius 默认 1), 与 stage 13 的 cooccurrence_filter.sentence_radius 是互不联动的不同键。第五之补, 跨年可比性: 前已论及 Q 非尺度不变, 年际节点数与边数的变化会独立于"真实板块化"而移动 Q, 故本家族不建议对 net_modularity_yr 作跨年绝对水平的机械比较; 稳健的用法是把它当作随时间演化的状态序列观察相对起伏, 或在回归中经年内去均值/与银行特征交乘后使用, 让识别来自截面异质而非年际水平漂移。与本项目"从文本还原金融网络"的方法同源工作 Li 等 (2026) 也提示: 文本构造的网络其边密度天然随语料体量与报道偏好波动, 结构指标的跨期解读须锚定构造口径不变这一前提。

第六, 社区数与划分的不确定性: 贪心 CNM 给出的社区划分并非全局最优, 不同算法 (Louvain、Leiden、谱方法) 或不同分辨率参数会得到略异的社区数与 Q 值; 本实现固定采用 networkx 的 greedy_modularity_communities 默认口径, 以确定性与可复现优先, 未引入分辨率梯子, 这是一处刻意的设计取舍——若未来需分辨率敏感性, 应作为额外梯子并列而非替换 canonical。第七, 边权口径的自洽性风险: 前已述及, 检测与打分两步必须同传 weight='weight', 否则 greedy (默认 None) 与 modularity (默认 weight) 口径错配会致 Q 符号翻转, 这是一个已被源码注释与测试锚死的命门, 任何后续对该两步的改动都须保持双侧加权口径一致, 否则整列失真。第八, 与三轨/嵌入/情感梯子的正交性: 本家族的判据梯子只在"银行∧银行邻接门槛"这一维度展开, 不与三轨文本 (银行∧金融科技范围)、co-primary 双轨嵌入 (Qwen 4096 维 / text-embedding-3-large 3072 维)、情感 LLM 三家投票、词典消融与政治词权重等其它梯子交叉, 各梯子在各自维度内 just-identified 并排, 跨梯子严禁并入同一 over-identified Hansen J——这是全项目一致的稳健性并排纪律, 用意是避免过度识别检验因混入异质度量而失去解释力。

综合而言, net_modularity_yr 家族提供的是"年度银行媒体共现网络的宏观社区分化"这一状态量, 以确定性的加权贪心模块度为核, 以同篇/±1 句窗/严格同句三判据为稳健性梯子; 它在计量上因网络级年度标量的性质只能作情境或交乘变量而非独立处理变量, 在解读上应作媒体注意力板块化的关联性刻画而非实体风险传染的因果度量, 在实现上以只读复用年度图、抽纯函数、固定加权口径三条纪律保证 golden 可复现与单测可达。使用者在报告本家族任一列时, 都应同时呈现三判据变体、复述年 FE 吸收约束、并明确它与相邻致密度/连通性指标以及节点级中心度、经纪角色家族的构念边界, 避免把媒体共现网的板块化误读为实体借贷网的风险社区。

## VAR: net_modularity_yr

【变体差分】
本列是家族 canonical (无后缀), 对应"同篇 (article) 判据": 只要两家银行出现在同一篇报道中 (含标题 prepend 的第 0 句在内的全篇范围), 即在年度共现图上建立一条边。这是三个判据变体中门槛最松的一档——邻接的空间粒度是"整篇文章", 不要求两家银行在文本上彼此靠近。因此本列生成的年度图边最稠密、团投影虚增最强 (一篇点名 N 家银行的长报道直接贡献一个 N 团), 模块度也最可能反映"被同一篇报道打包提及"这一较宽泛的关联, 而非银行之间语义上的紧密并置。它是 NETWORK_METRIC_BASES SSOT 中登记的规范网络级模块度列, 也是 stata_export 判据标签机械块与 gate 测试 import 复用的锚点。

数值上, 本列由 _net_level_extra_metrics 在同篇判据构造的加权图 G 上, 经 greedy_modularity_communities(weight='weight') 检测社区、再由 nx.community.modularity(weight='weight') 打分求得, 完全确定性且 golden-safe。作为 canonical, 它承担家族的主报告职责: 在计量设定中作网络环境情境量, 因是网络级年度标量而在含年 FE 的设定中被吸收 (year-FE absorbed), 仅在无年 FE 或与银行特征交乘时可识别。它与两个判据变体 net_modularity_yr_win1、net_modularity_yr_sent 构成稳健性梯子——三者各自 just-identified 并排、互为稳健性、不分主次, 用以证明"银行网络板块化"这一构念的度量不被共现判据的松紧取值所驱动; 三判据严禁混入同一 over-identified Hansen J。需重申: 本列的"同篇"是银行∧银行邻接的空间门槛 (最松档), 与银行∧金融科技三轨文本的 full 轨在概念上正交, 无字符串或语义上的可达关系, 不可将两者的"无后缀即最宽"直觉相互套用。相较同族的局部致密度指标 (聚类系数、传递性) 与连通性指标 (巨片占比、分量数), 本列独有的信息是"全局社区切分强度", 即整张年度银行舆论网络能否被划成边界清晰的报道板块; 在开发期 T=2 稀疏图上可能不显著或触 NaN 守卫, 属预期退化, 生产 T=18 全量语料下方具解释力。

作为无后缀 canonical, 本列还承担面板导出层的标签与注册职责: export.py 为其注入英文标签 Annual Co-mention Modularity (CNM 2004; year-FE absorbed), 其中 year-FE absorbed 是对使用者的显式警示——提醒该列在含年 FE 的设定中被吸收、不可作独立处理变量。使用建议是把它当作"当年银行舆论生态的板块化温度计": 板块化强 (Q 高) 的年份, 银行被媒体切分成若干相对封闭的报道簇, 同伴情绪的传导更可能局限在簇内; 板块化弱 (Q 低) 的年份, 银行共现更趋弥散, 舆论冲击更易跨簇扩散。这一情境解读使本列适合作为溢出/同伴效应模型中的调节变量, 而非结果或直接原因。就与判据变体的关系再作一次强调: 本 canonical 列锚定"同篇"这一最松邻接门槛, 是三判据梯子中边最稠、团投影虚增最强的一端, 其数值应与 _win1 (中档)、_sent (紧档) 并置解读, 三者互为稳健性、各自 just-identified 并排、严禁混入同一 over-identified Hansen J, 共同回答"银行网络板块化的度量是否稳健于共现判据取值"这一稳健性问题; 若三判据下模块度的高低模式一致, 则主结论不被判据松紧驱动, 反之则须在正文披露判据敏感性。

## VAR: net_modularity_yr_sent

【变体差分】
本列是"严格同句 (sent) 判据"变体: 仅当两家银行出现在同一个句子内时, 才在年度共现图上建立一条边。这是三个判据变体中门槛最紧的一档——邻接的空间粒度收缩到单句级, 要求两家银行在文本上真正贴近、被同一句话并置提及。相较 canonical 的同篇判据, 严格同句会滤掉大量"仅因同处一篇长报道而被动共现"的弱关联, 只保留语义上紧密并置的银行对。其后果是: 本列生成的年度图边最稀疏、团投影虚增最弱, 模块度更纯粹地反映"被同一句话直接关联的银行"所形成的社区结构, 但也因边数骤减而在小样本上更易触发稀疏退化 (社区不显著或 NaN)。判据原语为 core/text/entity_context 的银行句位映射 (map_bank_sentence_positions) 与逐句未排除占位判定, 扫描文本含 prepend_title 的标题第 0 句 (镜像 stage 13 的 match_in_title)。数值口径与 canonical 完全一致 (同一 greedy_modularity_communities + modularity 加权两步、确定性 golden-safe), 唯一差异是输入图 G 由更紧的同句邻接构造。本列与 canonical、_win1 各自 just-identified 并排、互为稳健性、不分主次, 三者共同构成判据敏感性梯子, 严禁混入同一 over-identified Hansen J。须强调判据后缀 _sent 是银行∧银行的邻接门槛 (最紧档), 与三轨文本的 ss 轨 (银行∧金融科技同句) 是正交概念, 尽管都含"同句"直觉却不可互相复用: 前者判两家银行是否同句, 后者判银行与金融科技词是否同句。同样受年 FE 吸收约束, 仅在无年 FE 或交乘设定中可识别。

## VAR: net_modularity_yr_win1

【变体差分】
本列是"±1 句窗 (win1) 判据"变体: 当两家银行出现在相隔不超过 win_radius (默认取 1, 由 config/panel.yaml::network_criteria.win_radius 配置) 个句子的窗口内时, 即在年度共现图上建立一条边。它是三个判据变体中的"中间档"——门槛介于同篇 (canonical, 最松) 与严格同句 (_sent, 最紧) 之间: 既不像同篇那样把整篇文章内任意两家银行都判为邻接, 也不像严格同句那样苛求落在同一句, 而是允许跨越一个相邻句的短距并置, 捕捉"上一句提甲行、下一句提乙行"这类紧邻但不同句的关联。相应地, 本列生成的年度图边稠密度、团投影虚增强度均居中, 模块度取值通常也介于 canonical 与 _sent 之间。判据原语同为 core/text/entity_context 的银行句位映射加句窗配对 (bank_pairs_within_sentence_window), 审计与生产共用同一原语 (审计==生产)。⚠ win_radius 取自 network_criteria.win_radius, 与 stage 13 银行∧金融科技的 filtering.yaml::cooccurrence_filter.sentence_radius 是互不联动的两个不同键, 改一个不影响另一个。数值计算口径与 canonical 完全一致 (greedy_modularity_communities + modularity 双步加权、确定性 golden-safe), 唯一差异在输入图由 ±1 句窗邻接构造。本列与 canonical、_sent 各自 just-identified 并排、互为稳健性、不分主次, 三判据共同构成敏感性梯子且严禁混入同一 over-identified Hansen J。判据后缀 _win1 仍是银行∧银行邻接门槛, 与三轨文本后缀正交, 不可混淆。同受年 FE 吸收约束, 仅在无年 FE 或与银行特征交乘的设定中可识别; T=2 稀疏样本上可能退化, 属预期。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Jiang, J., Jiang, X., Yan, Y., Xie, S., & Yao, J. (2025). Alliance-based modeling of interbank lending networks: Insights into risk contagion dynamics. PLOS ONE. https://doi.org/10.1371/journal.pone.0324981
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
<!-- rendered-citations:end -->
