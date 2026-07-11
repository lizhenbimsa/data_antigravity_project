---
family_id: F461
columns:
- net_density_yr
- net_density_yr_sent
- net_density_yr_win1
unit: 网络结构指标 (无量纲比率, 取值区间 0 至 1)
formula: "net_density_yr = 2 * E / (N * (N - 1)); E = 年度银行共现网络实际无向边数, N = 该年出现的目标银行节点数; 判据变体 {同篇 (无后缀 canonical) / ±1 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (nx.density) ; 落列标签 news_process/pipeline/panel/export.py
upstream:
- 13_cooccurrence_filter.parquet (幸存篇章 docid / target_bank / year)
- 14_materialize_ctx.parquet (content 文本, 供 _win1/_sent 判据句级重扫)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
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
  venue: North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: 102163
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
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
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
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
本家族的核心构念是「年度银行共现网络密度」net_density_yr, 它刻画在给定一年内, 出现于新闻语料中的目标银行之间, 通过被同一批报道共同提及而形成的关系网究竟有多稠密。构念的落脚点不是任何单家银行的位置, 而是整张年度网络的宏观拓扑形态: 当年出现的所有银行两两之间, 可能存在的共现关系有多少被实际的媒体报道所激活。这一测度承接社会网络分析中最基础的结构描述量, 用以概括一个由媒体注意力编织出来的、以银行为节点的信息共现结构在时间维度上的疏密变迁。数据来源上, 网络的节点集来自共现硬过滤后仍然幸存的篇章 (上游 stage 13 只保留「目标银行与至少一个金融科技词邻近共现」的文章), 节点即为在该年至少被报道提及一次的目标银行; 边的构造则由银行与银行之间的共现判据决定, canonical 口径下, 只要两家银行被同一篇文章 (同一 docid) 共同提及, 就在两者之间记一条无向边。密度构念因此本质上是媒体共同注意力的年度凝聚程度: 密度高, 意味着当年舆论把众多银行放在一起讨论的现象普遍, 银行群体在公众信息空间中被高度关联; 密度低, 则意味着银行大多各自被孤立报道, 群体层面的舆论关联稀薄。需要强调的是, 本构念度量的是「共同被报道」这一媒体层面的关联, 而非资产负债表上的同业拆借、担保或股权关系, 也不是价格层面的收益率联动; 它是一个基于文本共现的信息网络测度, 与金融机构之间的真实经济纽带同源而不等同。从构念史的角度看, 以「共同出现于同一文本」作为节点间关联的最小定义, 是文本网络分析长期沿用的操作化路径: 两个实体越频繁被同一批话语放在一起, 越可能在公众认知与信息处理中被联结。银行舆论场尤其适合这一操作化, 因为银行业本身高度同质、竞争与监管环境共享, 一则政策、一次风险事件、一波金融科技浪潮往往同时点名多家银行, 使得「共同被报道」成为捕捉银行群体被舆论一体化看待程度的天然探针。年度聚合的选择则出于两点考量: 其一, 面板的时间粒度为年, 网络量须与之对齐才能进入银行—年面板; 其二, 年度窗口足够长以平滑单条重大新闻的偶发冲击, 又足够短以保留舆论环境的时变结构, 从而让密度的逐年变迁能反映舆论关联强度的中期演化。密度作为这一年度网络最凝练的单一标量, 承担的正是「用一个数概括当年银行舆论共现网有多稠密」的构念职能。

【方法学与计算】
计算实现直接调用 networkx 的 nx.density(G): 对于无向图, 密度定义为实际边数 E 与最大可能边数之比, 即 net_density_yr = 2 * E / (N * (N - 1)), 其中 N 是该年网络的节点数 (幸存目标银行数), E 是无向边数。取值区间落在 0 到 1 之间, 无量纲。构造流程分若干步: 首先按年份切分幸存篇章, 取当年出现的全部目标银行为节点全集并排序建立稳定索引; 随后逐篇 (或逐 docid 组) 判定哪些银行对满足共现判据, 对满足者在对称邻接矩阵上加权累加 (每篇每对加一, 保持对称); 由邻接矩阵建图后, 密度只取决于是否存在边而与边权大小无关 — nx.density 只数边的条数, 不读 weight 通道, 因此同一对银行在多篇报道中反复共现只贡献一条边, 不会抬高密度。节点数不足两家 (N 小于 2) 时网络退化, 不产生有意义的密度。由于 net_density_yr 是「年度级」量, 对当年所有银行取同一个值, 在合并进面板时按年份广播到每一家银行行上; 这一广播特性带来一个直接的计量后果: 在含年份固定效应的回归中, net_density_yr 在同一年内对所有银行恒定, 会被 year FE 完全吸收, 因而它只能进入不含年 FE 的规格, 或以与银行层特征交乘的形式参与识别。生产口径的 canonical 列 net_density_yr 采用「同篇」判据 (无后缀); 该测度所在的结构指标全集由 network_spillover.py 的 NETWORK_METRIC_BASES 单一事实源统一登记 (33 个基名, 密度属其中 10 个网络级指标之一), stata_export 的标签块与 gate 测试均从该 SSOT import 复用以防命名漂移。在具体的边构造上, 判据分轨路径 (_win1/_sent) 走 docid 组内的句级重扫: 对每个含两家及以上幸存银行的 docid 组, 取组首行正文并 prepend 标题 (标题记为第 0 句), 以 map_bank_sentence_positions 定位各银行别名在句序列中的位置, 再由 bank_pairs_within_sentence_window 在给定半径下判定成对; 非幸存银行不入别名字典, 从源头杜绝幻影边。同篇 canonical 路径则更简单, 只要同一 docid 组内出现两家银行即两两连边。三条路径共享同一套否定/短名排除事实源, 与 stage 11/13 及 ctx/ss 物化保持一致的判定原语, 确保「涉农行业」不会被误判为「农行」而虚增边。密度作为全局标量, 对上述三种判据分别独立成图、独立取 nx.density, 落列为 net_density_yr / net_density_yr_win1 / net_density_yr_sent 三个并排列。

密度的度量哲学值得单独说明: 它是一个「关系已实现比例」量, 分子是被媒体实际激活的银行对数, 分母是理论上可能的银行对数 N(N-1)/2, 因此它对节点数 N 的变化极为敏感 — 当某年被报道的银行数骤增, 即便实际共现边数同比增长, 密度也可能因分母以平方阶膨胀而下降。这一「规模效应」意味着跨年比较密度水平时必须意识到, 密度下降未必代表舆论关联减弱, 也可能只是被纳入舆论场的银行更多、网络更大更稀。正因如此, 密度在实证中更宜作为控制或调节变量吸收年度舆论环境, 而非作为需要给出结构解释的因变量; 若要刻画「关联强度」而非「关联比例」, 应转向不受分母平方膨胀影响的加权强度类测度。

【文献定位】
网络密度作为结构描述量, 其方法学根基可追溯至社会网络分析对中心与结构的经典厘清, Freeman (1978) 对中心性概念的澄清奠定了从图论量刻画社会结构的范式, 而 Watts 与 Strogatz (1998) 关于小世界网络的工作则把聚类与路径这类宏观拓扑量引入对真实网络疏密与凝聚形态的刻画, 密度与聚类系数正是描述这类形态最基础的一对量。在把网络结构接入经济金融实证的脉络上, Bramoullé、Djebbari 与 Fortin (2009) 及其后续综述 (Bramoullé 等, 2020) 系统论证了如何借助社会网络结构识别同群效应, Manski (1993) 的反射问题则界定了这类识别的根本困难; Boucher 等 (2024) 进一步给出同群效应的一般化理论。金融网络与系统性风险方向, Jackson 与 Pernoud (2021) 的综述梳理了网络拓扑如何放大或抑制冲击传染; Grieser 等 (2022) 记录了企业财务政策中的网络效应; Gao、Ru 与 Yang (2022) 揭示了所有权网络在银行信贷中的信息角色。就以银行为节点、以媒体共现为纽带这一具体设定而言, Li 等 (2026) 展示了如何从文本风险披露中还原金融网络结构与连通性, 与本家族「从新闻共现构造银行网络」的思路直接呼应; Nezami、Chisam 与 Palmatier (2025) 的元分析则提醒网络位置与绩效的关系存在情境依赖, 不宜简单外推。资产定价一侧, Yu、Hu 与 Zhong (2024) 以及 Xu 与 Zhao (2024) 论证了网络中心度与信息扩散、资产价格之间的联系。这些文献共同界定了 net_density_yr 的读法: 它是一个媒体注意力共现网络的宏观疏密指标, 可作为刻画舆论关联环境的年度背景控制或调节变量, 而非因果处理变量本身。进一步看, 从文本共现构造经济网络这一方法论传统, 一端连接以文本相似度刻画产业网络的做法, 另一端连接以新闻社交扩散刻画信息传播的做法; 本家族选择「同一篇报道共同提及」作为最小关联单元, 是这一传统在银行舆论场景下的具体化。de Paula、Rasul 与 Souza (2024) 关于从面板数据识别网络连边的工作, 从计量角度提示: 当网络本身是从观测数据 (此处为媒体共现) 推断而来时, 连边的构造判据本身就是一个需要做敏感性检验的设定选择 — 这正是本家族设三判据变体的方法论依据。系统性风险与传染文献 (Jackson 与 Pernoud, 2021) 则从反面界定了本测度的边界: 密度虽可作为舆论关联环境的概括, 但媒体共现网的稠密不等于真实敞口网的稠密, 后者才是传染动力学的载体; 把二者混淆会误导对系统风险的判断。综合而言, 密度在本项目中的合法读法是「年度舆论共现环境的宏观强度」, 其解释力止步于媒体注意力层面。

【识别策略定位】
在识别框架中, net_density_yr 的定位是「网络环境背景量 / 调节变量」而非核心处理变量。它的年度广播特性决定了单独进入含年 FE 的主回归会被吸收, 因此它的识别用途主要有二: 其一, 作为不含年 FE 的规格里对整体舆论共现环境的控制, 吸收「某些年份银行普遍被一起讨论」这一宏观时变混杂; 其二, 与银行层处理变量交乘, 检验个体层效应是否随年度网络稠密程度而放大或衰减 — 这正契合同群效应文献 (Bramoullé 等, 2009, 2020; Boucher 等, 2024) 对网络结构调节个体互动强度的论证, 也回应 Manski (1993) 反射问题对内生互动识别的警示。判据敏感性构成本家族识别稳健性的主线: 同篇 (canonical)、±1 句窗 (_win1)、严格同句 (_sent) 三个判据变体是同一密度构念在「共现空间粒度」这一维度上的三种测量, 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁把三判据变体混进同一个 over-identified 的 Hansen J 统计量。这里必须与三轨文本 (full/ctx/ss, 银行∧金融科技口径) 严格区分: 判据后缀刻画的是银行∧银行邻近的句法粒度, 与三轨文本后缀是两个正交的概念空间, 同样禁混同一 Hansen J。判据的 win_radius 取自 config/panel.yaml 的 network_criteria.win_radius (默认 1), 与 stage 13 银行∧金融科技共现过滤的 filtering.yaml::cooccurrence_filter.sentence_radius 是两个互不联动的不同键, 不可混用。

【与相邻测度的构念区分】
net_density_yr 与家族内、家族外的若干相邻测度须精确区分。与同为网络级的 net_transitivity_yr / net_avg_cluster_yr 相比, 密度只问「边有多少」, 不问「边如何抱团」: 后两者刻画三角闭合与局部聚集, 与密度在数学上相关但语义不同 (稀疏网络也可高度聚类, 稠密网络也可低聚类)。与 net_degree_gini_yr 相比, 密度是关系总量的均值型量, 而 Gini 是度分布的不平等型量, 一个测「多不多」一个测「均不均」。与节点级中心度 (bank_degree_cent / bank_eigen_cent 等) 相比, 密度是整张网络的单一标量而非逐银行的位置量, 不能用来比较银行个体。尤其要与「加权强度」口径划清: 密度以及 net_degree_gini_yr 采用无权边计数, 度量的是拓扑连接的有无, 而 bank_strength_cent 等走 weight 通道度量共现强度分布, 两者口径不同不可混读。更须与经济纽带划界: 本密度是媒体共同报道意义上的信息共现关联, 不是同业拆借、担保 (对照担保网络文献如相关中国担保网研究) 或所有权网络 (Gao 等, 2022) 那样的真实资金/契约纽带; 把媒体共现密度误读为金融传染通道会高估结构性系统风险 (Jackson 与 Pernoud, 2021 意义上的传染须以真实敞口网络为底)。同样须与同群效应识别中的「网络」区分: Bramoullé 等 (2009, 2020) 与 Boucher 等 (2024) 所用的网络是个体间影响传导的结构, 密度在那里作为网络整体连通程度的概括量进入识别, 而本项目的密度是媒体共现的宏观背景量, 两者虽共用密度这一图论概念, 但底层网络的经济含义不同, 不可不加界定地互相援引结论。

【已知局限与稳健性梯子】
已知局限有三层。第一层是多行文章的团投影 (clique projection) 膨胀: 一篇同时提及 k 家银行的报道, 在共现图上会生成一个 k 阶完全子图, 把 k 家银行两两连边, 从而系统性抬高边数与密度 — 密度对这种「大新闻把很多银行一锅端」高度敏感, 判据收紧 (_win1 / _sent) 正是抑制这一膨胀的主要手段, 越严的判据剥离越多仅因同篇但语境无关的伪共现。第二层是留篇与样本框依赖: 节点全集来自 stage 13 硬过滤后的幸存篇章, 留篇门控在 full 轨口径 (2026-06-29 铁律) 下判定一篇是否为银行金融科技报道, ctx/ss 为条件于 full 的稳健性轨; 因此密度刻画的是「已进入金融科技相关舆论场的银行」之间的共现, 而非全体媒体报道的银行共现, 读数须锚定这一样本框。第三层是年度广播导致的识别退化 (年 FE 吸收) 与小样本波动: 在 T=2 的开发盘上, 密度只有两个年度取值, 判据分轨的极端稀疏可能使 _win1 / _sent 出现零方差退化, 属预期现象, 生产 T=18 语料下方能体现判据梯子的区分度。稳健性梯子的组织原则始终是: 三判据变体各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据梯子与三轨文本、co-primary 双轨嵌入等其它稳健性维度彼此正交, 不交叉组合以免列爆炸。密度的 BLAS-FP 确定性总体良好 (纯边计数, 无谱分解), 不属于 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 那三个需按全名排除的非确定网络列。第四层局限涉及跨判据可比性的语义漂移: 同篇、句窗、同句三档虽同名为「密度」, 但它们数的是不同粒度下的边, 三档之间的水平差不应被解读为「测量误差」, 而应被解读为「共现在不同语义紧密度下的实现程度」; 因此三档只宜作为同一构念的稳健性并排, 报告主结论在三档下的稳定性, 而不宜把三档水平直接相减或做过度识别的联合约束。第五层局限是网络的方向性缺失: 本共现图是无向的, 密度不区分「A 报道带出 B」与「B 报道带出 A」的非对称注意力流, 若研究关切注意力的方向传导, 需转向有向或经纪角色类测度 (如 Gould-Fernandez 族), 密度仅给出无向关联的总量视角。就稳健性梯子的实践操作而言, 建议的报告方式是: 以 canonical 同篇密度为主报口径给出网络稠密程度的宽口径基准, 以 _win1 为首要稳健性轨, 以 _sent 为最保守的精确率导向轨, 三者在正文中并列呈现而非合并进单一统计量, 让读者看到主结论对共现粒度设定的敏感度。所有这些局限的共同底色是: 密度是一个高度依赖构造设定 (留篇门控、共现判据、节点全集) 的合成量, 其绝对水平的可比性弱、相对变化与结构稳健性的信息量强, 使用时应侧重后者。

## VAR: net_density_yr

【变体差分】
本列是本家族的 canonical 无后缀列, 也是家族的 core 列, 采用「同篇」共现判据: 只要两家目标银行在同一 docid 的报道中被共同提及, 即在两者间记一条无向边, 不要求二者在文中邻近或同句。它代表最宽松、召回最高的银行∧银行共现口径, 是 network_spillover.py 中 compute_bank_network_centrality 在 criterion='article' 主路径下的产出, 也是 NETWORK_METRIC_BASES 登记的密度基名。数值上, net_density_yr = 2E/(N(N-1)), E 为同篇判据下的无向边数, N 为当年幸存目标银行数; nx.density 只数边不读权, 故同一对银行的多篇共现不重复计边。相较两个收紧判据的姊妹列, 本列的语义特征是最大化地纳入「同篇即算关联」, 因而对多行大新闻的团投影膨胀最敏感, 密度读数系统性高于 _win1 与 _sent; 这既是它作为召回上界基准的价值所在 (给出年度共现网稠密程度的宽口径上界), 也是解读时必须警惕的偏向。作为年度级广播量, 本列对同年所有银行取同值, 在含 year FE 的规格中被吸收, 只适用于无年 FE 控制或与银行层特征交乘的识别用途, 定位为舆论共现环境的背景/调节变量, 而非因果处理变量。本列与两个判据变体 net_density_yr_win1 / net_density_yr_sent 各自 just-identified 并排、互为稳健性、不分主次, 三者严禁被混入同一个 over-identified 的 Hansen J 过度识别检验; 判据后缀所在的银行∧银行句法粒度空间, 与三轨文本 (full/ctx/ss) 的银行∧金融科技口径正交, 亦禁混同一 Hansen J。留篇样本框在 full 轨门控 (2026-06-29 口径) 下确定, 本列刻画的是已进入金融科技相关舆论场的银行群体之共现密度。

进一步刻画本列相对姊妹列的精确差分: 三档判据共享完全相同的节点全集 (同年幸存目标银行) 与完全相同的否定/短名排除事实源, 唯一变化的自由度是「两家银行相距多远才算一条边」— 同篇口径把这一阈值放到最宽 (只要同一 docid 即可), 因此本列在三档中边数最多、密度读数最高, 是共现召回的上界基准。这一宽口径的代价是对多行大新闻的团投影膨胀最为敏感: 一篇同时点名 k 家银行的综述性报道会一次性贡献 k(k-1)/2 条边, 把这 k 家银行在该年的密度整体抬高, 即便这些银行在文中彼此并无实质语境关联。因此本列的数值应被理解为「同篇即算」意义下的关联比例上界, 阅读时须搭配 _win1 与 _sent 两档收紧口径共同判断结论的稳健性。作为 core 列, 本列还是家族对外的默认代表: 当下游模板或 codebook 以无后缀名引用密度时指向的即是本列, 其 nx.density 只数边不读权的计算特性、年度广播导致的 year FE 吸收约束、以及规模效应下密度随节点数平方阶稀释的解读要点, 都以本列为准。在识别用途上, 本列既可在无年 FE 的规格中作为年度舆论共现环境的宏观控制, 吸收「某些年份银行普遍被一起讨论」的时变混杂, 也可与银行层处理变量交乘, 检验个体层效应是否随年度网络稠密程度而放大或衰减; 但它自身不承担因果处理变量的角色, 因为其年度恒定性与合成量属性都不满足外生冲击的要求。凡涉本列与两个判据变体的联用, 一律遵循各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J 的铁律; 凡涉与三轨文本口径的交界, 一律牢记判据后缀 (银行∧银行句法粒度) 与三轨后缀 (银行∧金融科技口径) 正交、同禁混同一 Hansen J。

## VAR: net_density_yr_sent

【变体差分】
本列是「严格同句」判据变体 (criterion='sent', win_radius=0), 是本家族密度构念在共现空间粒度维度上最严的一档。它区别于 canonical 同篇口径之处在于: 两家银行必须在报道正文的同一个句子内被提及, 才在两者间记边; 走 docid 组内的句级重扫路径, 以 map_bank_sentence_positions 定位各银行别名的句位置, 再由 bank_pairs_within_sentence_window 在 win_radius=0 (同句) 下判定成对, 扫描文本为标题 prepend 正文 (标题记为第 0 句, 镜像 stage 13 的 match_in_title 口径), 并沿用与 stage 11/13 一致的否定/短名排除事实源以防「涉农行业→农行」类假阳性。由于同句共现远比同篇稀有, 本列剥离了绝大多数仅因同篇但语境无关的伪共现, 边数与密度读数系统性低于 canonical 与 _win1, 是三判据中最保守、精确率导向的一档, 对多行大新闻的团投影膨胀抑制最强。节点全集与 canonical 一致 (同年幸存银行), 仅边集更严, 因此密度差异纯粹来自判据收紧而非样本变化。本列与 net_density_yr / net_density_yr_win1 各自 just-identified 并排、互为稳健性、不分主次, 三者禁混进同一 over-identified 的 Hansen J; 判据后缀与三轨文本后缀正交, 同禁混。作为年度广播量, 本列同受 year FE 吸收约束。在 T=2 开发盘上, 同句判据的极端稀疏可能使本列出现零方差退化, 属预期现象, 生产 T=18 语料下方显区分度。定位上, 本列在三判据梯子中承担「精确率上界 / 保守基准」职能: 当主报口径 (canonical 同篇) 与折中口径 (_win1) 给出的结论在本列这一最严口径下依然成立时, 可判定主结论不被团投影膨胀所驱动; 反之若结论仅在宽口径成立而在同句口径消失, 则提示该关联很可能是「同篇但语境无关」的伪共现所致。因此本列的合法读法不是与 canonical 直接比水平差 (三档数的是不同粒度的边, 水平差反映的是共现语义紧密度的实现程度而非测量误差), 而是并排检验主结论对共现粒度设定的敏感度。凡涉本列与 canonical、_win1 的联用, 一律遵循各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J 的铁律。

## VAR: net_density_yr_win1

【变体差分】
本列是「±1 句窗」判据变体 (criterion='win1', win_radius 取 config 的 network_criteria.win_radius 默认 1), 在共现粒度上介于同篇 canonical 与严格同句 _sent 之间, 是一档折中口径。它区别于 canonical 之处在于: 两家银行不再只要同篇即算关联, 而必须落在彼此相距不超过一个句子的窗口内 (同句或相邻句) 才记边; 计算走与 _sent 相同的 docid 组内句级重扫路径, 差别仅在传入 bank_pairs_within_sentence_window 的 radius 为 1 而非 0。这一窗口既比同篇严格 — 剔除了跨段落、语境无关的远距共现, 抑制团投影膨胀 — 又比严格同句宽松, 保留了「相邻句陈述同一事件」这类语义上真实相关但未落在同一句的共现, 因而密度读数通常落在 canonical 与 _sent 之间, 提供召回与精确率的中间平衡点。节点全集与 canonical 及 _sent 一致, 仅边集因窗口约束而收紧; 扫描文本同样是标题 prepend 正文、标题为第 0 句, 并共用否定/短名排除事实源。须再次强调 win_radius 取自 panel.yaml 的 network_criteria.win_radius, 与 stage 13 银行∧金融科技过滤的 cooccurrence_filter.sentence_radius 是两个互不联动的不同键。本列与 net_density_yr / net_density_yr_sent 各自 just-identified 并排、互为稳健性、不分主次, 三者禁混进同一 over-identified 的 Hansen J; 判据后缀空间与三轨文本 (full/ctx/ss) 正交, 同禁混同一 Hansen J。作为年度广播量本列亦受 year FE 吸收, 在 T=2 盘上可能零方差退化, 属预期。本列在三判据梯子中的独特职能是提供「召回—精确率折中」的中间参照: canonical 给出宽口径召回上界, _sent 给出严口径精确率基准, 本列则落在二者之间, 使得三档共同勾勒出密度读数随共现粒度收紧而单调下降的轨迹, 让读者能判断主结论究竟稳定于哪一段粒度区间。须再次强调, 三档水平差应被解读为共现在不同语义紧密度下的实现程度, 而非同一真值的测量抖动, 故本列只宜作为同一密度构念的稳健性并排轨与 canonical、_sent 共同报告, 不宜把三档水平直接相减或联合成过度识别约束。凡涉本列与两个姊妹判据变体的联用, 一律遵循各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J 的铁律。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
