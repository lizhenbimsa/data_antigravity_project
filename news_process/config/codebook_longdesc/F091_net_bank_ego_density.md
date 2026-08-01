---
family_id: F091
columns:
- bank_ego_density
- bank_ego_density_sent
- bank_ego_density_win1
unit: 无量纲比率 (∈ [0,1]; 自我网络中邻居间实际边数占最大可能边数之比)
formula: "bank_ego_density = ego_edges / [k(k-1)/2]; k = 焦点银行在年度共现网中的度数, ego_edges = 其 k 个邻居两两之间实际存在的边数 (二值拓扑, 忽略边权); k <= 1 -> NaN。判据变体 {同篇 (无后缀)/±1 句窗 _win1/严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (panel runner 步骤 7h; ego_density = 函数内 Part B、计算内部编号 (12), 手工邻居对枚举) ; build_adjacency_matrix (判据分轨 article/win1/sent) ; 标签 pipeline/panel/codebook.py::_infer_label
upstream:
- "24_herd_decay.parquet (df_exploded: docid + target_bank + year + 内容 + 标题; full-only 留篇 verified 集)"
- 40_panel_yearly.parquet (bank-year 面板骨架, 追加 33 网络列)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: 104218
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
  authors: de Paula, Á., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
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
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould–Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: 2693
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
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
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1086/421787
  type: journal
  authors: Burt, R. S.
  year: 2004
  title: "Structural holes and good ideas"
  venue: American Journal of Sociology
  vol: 110
  issue: 2
  pages_or_artno: 349-399
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
- doi: "10.1111/acfi.13091"
  type: journal
  authors: "Wang, L., Hou, W., & Liu, Y."
  year: 2023
  title: "How do co-shareholding networks affect negative media coverage? Evidence from China"
  venue: "Accounting & Finance"
- doi: "10.1007/s44176-024-00031-0"
  type: journal
  authors: "Guan, F."
  year: 2024
  title: "Ego-network characteristics moderates the interaction of structural hole and centrality on market performance: based on coopetition network"
  venue: "Management System Engineering"
- doi: "10.1016/j.emj.2024.05.005"
  title: "Don't ignore either side: The differential impact of ego-network density of the focal firm and partner on technological invasion"
  authors: "Tang, L., Wang, T., Guan, F., & Sun, L."
  year: 2025
  venue: "European Management Journal"
  type: "journal"
  one_sentence_zh: "发现焦点企业自我网络密度与技术侵入呈倒U型关系、而伙伴企业自我网络密度呈负向关系,为本列'自我网络密度'构念在联盟情境下的非线性经济后果提供了2025年最新实证对照。"
- doi: "10.1080/09537325.2023.2217458"
  title: "How does ego-network structure affect innovation within industrial clusters? The moderating effect of ego-network density"
  authors: "Huang, C.-H., & Hsueh, C.-C."
  year: 2023
  venue: "Technology Analysis & Strategic Management"
  type: "journal"
  one_sentence_zh: "考察产业集群内自我网络密度对结构洞与中心度影响创新绩效的调节作用,支持本列'密度需与其他结构量联合解读、不宜单独作为回归右手侧'的处理原则。"
new_dois:
  - "10.1111/acfi.13091"
  - "10.1007/s44176-024-00031-0"
  - "10.1016/j.emj.2024.05.005"
  - "10.1080/09537325.2023.2217458"
---

## CORE

【构念与来源】
本家族刻画的是"自我网络密度"(ego-network density), 即在年度银行共现网络里, 以某一家焦点银行为中心, 把它直接相连的所有邻居银行圈出来后, 这些邻居彼此之间实际存在的连边占它们两两之间最多可能连边的比例。用大白话讲, 它回答的问题是"这家银行认识的那一圈同行, 彼此之间是不是也互相认识": 如果焦点银行的邻居们相互之间高度抱团、几乎两两成对地被媒体一同报道, 自我网络密度就接近一; 如果焦点银行像一座桥, 把两拨互不往来的银行连在一起、而这些邻居之间几乎没有直接的共现联系, 自我网络密度就接近零。这个构念直接对接社会网络分析里的"结构洞"(structural holes) 传统: Burt (2004) 指出, 一个行动者若身处稀疏、开放、邻居互不连通的局部结构中, 就占据了跨越结构洞的经纪位置, 能优先获取并重组来自互不重叠信息源的非冗余信息; 反之, 邻居高度互连的封闭三角结构则对应 Coleman 式的闭合社会资本, 强调信任、规范与冗余的信息核验。自我网络密度正是把这一对立的两极压缩进单一的 [0,1] 标量: 低值一端指向经纪与信息优势, 高值一端指向封闭与冗余。

数据来源方面, 本家族的底层不是任何外生的股权、担保或同业拆借关系, 而是"银行在同一批中文新闻里被一同提及"这一文本共现关系。原始语料为项目全量中文银行/金融科技新闻, 经预处理、银行实体识别、金科实体识别、共现硬过滤 (stage 13) 与三轨文本物化 (stage 14) 之后, 在情感 LLM 语义精筛 (stage 21) 与羊群衰减处理 (stage 24) 后得到 verified 篇章级展开帧 (df_exploded = 24_herd_decay.parquet)。这一展开帧遵循 full-only 留篇门控 (2026-06-29): 一篇报道是否算作"一篇银行金科报道"只看 full 轨的 LLM 判定 (llm_verified_full == True), 因而进入网络构造的文章宇宙与全仓其余面板测度 (聚合域同为 24_herd_decay) 严格对齐, 不含 stage 14 规则预筛阶段混入的假阳性文章。生产者按年份 (year) 切片, 对每一年独立建图: 节点全集为该年在展开帧中幸存的全部 target_bank, 边则由"两家银行在同一文章 (或更严判据下的同句窗/同句) 内共现"确定, 每篇文章的每一对共现银行贡献一次计数。中文银行媒体网络的构造与其对存款稳定、系统性风险、信息扩散的意义, 有 You, Zhang 和 Zhang (2018)、Fang 等 (2024) 与 Cookson 等 (2026) 提供机构语境: 媒体报道不仅被动记录、更能主动塑造存款人预期与银行间风险传染路径, 因而"哪些银行被一同置于媒体聚光灯下"本身就是一个有经济含义的结构量。

【方法学与计算】
计算实现见 network_spillover.py 的 compute_bank_network_centrality (panel runner 步骤 7h; 本列在函数内属 Part B、计算内部编号 (12))。对给定年份, 生产者先由 build_adjacency_matrix 得到对称邻接矩阵, 再用 networkx 建立无向图 G (边权取该对银行的年内共现次数), 并显式补入孤立节点以保证节点全集完整。自我网络密度采用手工双重循环精确计算, 不调用任何谱分解或迭代求解: 记焦点银行在图 G 中的度数为 k (即它的邻居数目), 取出其邻居列表, 对邻居中每一对无序组合逐一用 G.has_edge 检验是否存在直接连边, 累加得到邻居间实际边数 ego_edges; 最大可能边数为 k 乘以 (k 减一) 再除以二, 即 k 个邻居两两配对的组合数; 自我网络密度 = ego_edges 除以该最大可能边数。当 k 小于等于一时置为 NaN — 因为焦点银行只有零个或一个邻居时, 邻居之间根本不存在"两两配对"这一对象, 密度在数学上无定义。

有三处方法学细节必须与相邻网络列区分清楚。第一, 本列是纯二值拓扑量: 判定邻居间是否成边时只看 has_edge 的真假, 完全忽略边权 (共现次数)。这与同家族在生产者内相邻实现的加权量在数学基底上根本不同。第二, 也正因为它是整数计数除以整数组合数, 全过程不涉及任何浮点线性代数 (无特征向量、无当前流、无最短路径的浮点累加), 因而在跨次重建中逐位可复现; 它不属于项目登记的 BLAS 浮点漂移非确定网络列清单 (那份清单里的三个基名各自的三判据变体共九列, 因加权几何平均或谱运算的求和次序敏感而无法逐位复现)。这一确定性使自我网络密度成为网络族里对复现要求最友好的结构指标之一。第三, 图的构造遵循"每篇每对加一"的等权口径 (article 主路径); 生产者预留了 Newman 度守恒的超边归一开关 (hyperedge_normalize), 但该开关在 config 与 runner 中均未接线、生产不可达, 判据分轨路径更是显式拒绝该开关以防三判据轨无警告分叉。因此当前所有落盘取值一律为未做超边归一的等权口径。加权网络分析的一般框架与"权重是否进入结构量"的取舍, 可参 Opsahl, Agneessens 和 Skvoretz (2010) 与 Barrat 等 (2004); 局部三角结构与聚类的经典刻画则见 Watts 和 Strogatz (1998)。

邻接矩阵的构造分主路径与判据分轨路径两条, 二者共享同一节点全集但边判据不同。同篇主路径 (article) 走 both-verified 口径: 在同一 docid 分组内, 把该篇幸存的 target_bank 行集合两两配对、每对恰加一次计数 (对称落 A[i,j] 与 A[j,i]), 每篇文章的每一对共现银行因此贡献且仅贡献一条计权边。判据分轨路径 (win1/sent) 则在每个多银行 docid 分组内重扫文本: 先取该组幸存银行的别名字典 (仅幸存 target_bank 入参, 非幸存银行不参与定位、不可能成边——这是 phantom 边防线), 再逐句判定各银行的出现句集, 最后按句距阈值判对成边。这一"只让幸存银行入参"的设计确保了三判据轨的节点全集严格一致 (同为该年 df_year 幸存银行), 边集则随判据收紧而单调变严。值得注意的是, 自我网络密度在计算时用的是完整图 G 的邻居集, 而非最大连通分量子图 (后者只服务于当前流介数、偏心率、平均路径这类需要连通性的路径型指标); 因此即便焦点银行落在某个小连通块内, 只要它有不少于两个邻居, 本列仍有定义。边权 (共现次数) 在建图时被记录进 weight 属性, 但自我网络密度只用图的连通结构、不读 weight, 故一篇里共现二十次的银行对与共现一次的银行对, 对本列的贡献完全相同——这是它区别于加权聚类系数的最根本一点。

从社会资本理论看, 自我网络密度低与高分别对应两种截然不同、各有优劣的结构位置, 不宜先验地把某一端当作"更好"。低密度 (开放、稀疏的自我网络) 对应 Burt (2004) 的经纪优势: 焦点银行连接着彼此不往来的信息源, 可优先获取非冗余信息、并在互不知情的两方之间行使一定的控制。高密度 (闭合、抱团的自我网络) 对应 Coleman 式闭合社会资本: 邻居间的相互连通提供了信息的交叉核验、声誉约束与规范执行, 有利于信任与协调, 但也意味着信息高度冗余、创新性外部信息的流入受限。在银行媒体共现的语境里, 一家自我网络密度高的银行往往被反复地与同一批同行 (例如同为国有大行、或同处一地的城商行) 一同报道, 结构上嵌入一个封闭的舆论簇; 密度低的银行则更可能被媒体当作横跨不同银行群体的连接点来书写。这一解读须与后文识别策略结合: 结构位置既可能是银行行为的原因, 也可能是其属性 (规模、股权、地域) 的结果, 因果方向不能仅凭结构量本身断定。

【文献定位】
在测度学谱系上, 自我网络密度属于 Freeman (1978) 奠基的社会网络中心性与结构量传统的一支, 但它落在"结构洞—闭合"这条专门的轴线上, 而非度数、介数、接近度那条"谁更居中"的轴线。Burt (2004) 是本列最直接的构念锚: 结构洞理论把行动者局部邻域的稀疏程度 (低自我网络密度) 解释为跨越信息与控制断层的经纪优势来源。经纪的形式化传统进一步由 Gould 和 Fernandez (1989) 的中介结构与 Zádor 等 (2022) 的加权归一 Gould–Fernandez 经纪度量延展, 二者与自我网络密度共享"稀疏局部结构=经纪"的直觉, 但把经纪细分为协调者、看门人、联络人等角色, 属互补而非替代的刻画。在金融经济学侧, 网络位置与主体绩效、风险和资产定价的联系有较厚的实证累积: Nezami, Chisam 和 Palmatier (2025) 的元分析系统汇总了中心性与企业绩效的关联证据 (但该元分析不专门背书任何单一聚类型测度, 此处仅援引其"网络位置与绩效相关"的总体判断); Yu, Hu 和 Zhong (2024) 把节点中心性与信息扩散、资产定价打通; Jackson 和 Pernoud (2021) 综述了金融网络中的系统性风险传导; Gao, Ru 和 Yang (2022) 则从银行贷款的所有权网络出发论证了网络结构的信息角色。这些工作共同支撑一个判断: 银行在媒体共现网络中的局部封闭程度, 是一个可能与其融资成本、风险暴露和同群行为相关的结构性协变量, 值得作为面板变量纳入。

【识别策略定位】
在本项目的因果框架里, 网络结构量 (含自我网络密度) 主要充当两类角色, 二者须分清。其一是作为刻画银行所处同群环境的结构性协变量或调节变量, 直接进入含银行与年份双向固定效应的回归: 银行固定效应吸收掉不随时间变化的结构禀赋 (例如某国有大行天然嵌入某个稳定舆论簇的倾向), 年份固定效应吸收掉全网层面的年度冲击, 使得本列被真正利用的方差是"同一家银行的自我网络密度在年际间相对全网趋势的偏离", 而非可能内生于规模、股权、地域的横截面水平差。其二是为同群溢出、模仿压力与 Bartik/LOO 类工具变量提供网络权重矩阵 W 的构造基底: 本项目三条 IV 引擎 (同组 LOO 均值、广义 Bartik、媒体来源 house-style 暴露) 以及嵌入同业网、认知邻近网都以银行共现邻接为底层拓扑, 而自我网络密度正是这一拓扑局部封闭程度的标量刻画。这里必须澄清一个易错点: 自我网络密度本身不是 W 矩阵, 而是从与 W 同源的邻接结构里读出的一个结构位置指标; 若把它误当作行标准化后的权重直接放进空间自回归的右手侧、与 W×y 溢出项并列, 会产生机械共线, 是识别上的错误接法。

这里必须正视 Manski (1993) 的反射问题: 同群主体的结果彼此内生决定, 使得内生同群效应、外生 (情境) 同群效应与相关效应在观测数据里一般不可分离识别; 在完全传递、人人互连的封闭群 (自我网络密度恒为一) 里, 这三种效应的设计矩阵近乎线性相依, 识别几近失效。Bramoullé, Djebbari 和 Fortin (2009) 给出的出路恰恰依赖自我网络密度的反面: 当网络存在"朋友的朋友并非自己的朋友"的结构非传递性 (即低自我网络密度、开放的自我网络) 时, 二阶及更高阶邻居的特征可充当排除性工具, 部分同群效应因此可识别; Bramoullé, Djebbari 和 Fortin (2020) 与 Boucher 等 (2024) 进一步综述并推广了这一"以网络拓扑异质换取识别"的逻辑。因此自我网络密度不仅是一个描述量, 它的跨银行离散本身就是同群效应可识别性的一个来源: 邻居越不互连 (密度越低), 网络排除限制越有咬合力; 高密度银行则更接近反射问题的不可识别退化端。这一"结构差异即识别资产"的视角, 也说明本列不宜被简单当成可有可无的噪声控制变量丢弃——它携带识别信息。

将结构量接入银行—年面板的具体识别设计, 可借鉴公司金融侧的同群效应实证 (Leary 和 Roberts (2014) 用同群特质冲击构造工具、Grieser 等 (2022) 用空间自回归刻画公司财务政策的网络外溢) 以及从面板数据反推网络连边的方法学 (de Paula, Rasul 和 Souza (2024) 证明了在何种条件下网络结构本身可从结果面板中被识别出来)。经纪型网络位置与信息中介的因果解读, 还可参 Han, Kim 和 Nanda (2024) 对机构经纪网络促进流动性供给的研究, 它把"占据稀疏局部结构"翻译成可度量的中介收益, 为低自我网络密度的经济含义提供了金融市场侧的对照证据。需要强调三点边界: 第一, 本家族当前主要在描述统计与稳健性层消费, 若将自我网络密度升为核心回归的右手侧变量, 须补齐上述识别策略并明确 W 的外生性论证, 不能仅凭"结构量看起来外生"就直接放入; 第二, 三条判据轨 (article/win1/sent) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们当作同一构念的多个工具混进同一个 over-identified Hansen J 过度识别检验——那会把规格稳健性误当成过度识别的检验力来源; 第三, 媒体共现与银行舆论热度、危机时点存在双向反馈, 因而以本列或本邻接构造的 W 未必满足严格外生, 稳健性设计须对这一反馈显式讨论而非默认外生。

识别侧还有一个更隐蔽的测量层威胁, 值得单独点名: 媒体共现网络的边不仅由银行行为决定, 也由新闻生产者一侧的社会网络决定。Xu (2024) 记录了金融记者自身的社会关系网络如何系统性地影响其报道的选题与倾向——若某一批记者习惯性地把同一组银行放进同一篇稿件的写作框架, 观测到的银行间共现边就部分反映记者侧网络而非银行侧经济关联, 焦点银行自我网络密度的一部分方差因此可能来自新闻编辑室的写作惯例。这一威胁在本项目里有两层缓解而非根除: 其一, 银行固定效应吸收掉"某银行长期被特定媒体圈以固定框架报道"的稳态成分, 剩余年际变化受写作惯例驱动的程度较低; 其二, 三条 IV 引擎里的媒体来源 house-style 暴露工具恰恰把"媒体侧写作风格"当作可利用的外生变异来源显式建模, 这意味着分析者在把本列或其底层邻接当作银行侧结构量解读时, 应当同时报告以媒体来源结构为条件的规格, 检验结论是否随媒体侧构成的控制而翻转。此外, 判据梯子本身也承担识别层的压力测试职能: 记者把多家银行松散罗列进同一篇稿件所制造的"惯例边"多为跨段落弱共现, 在 ±1 句窗与严格同句判据下会被大量滤除, 因此若某一经济关联仅在同篇宽判据下显著、收紧后消失, 就应怀疑其被写作惯例边驱动; 反之若三判据下方向与量级稳定, 记者惯例解释的空间就被压缩。这正是判据敏感性设计在识别层 (而不仅是测量层) 的价值。

【与相邻测度的构念区分】
自我网络密度与生产者内相邻的多个结构量常被混淆, 须逐一切分。其一是加权聚类系数 (家族外相邻列, 生产者内以 networkx 的加权 clustering 计算): 在无权二值图上, 局部聚类系数与自我网络密度在数学上恒等 (都等于邻居间实际边数除以邻居对组合数); 但本项目的聚类系数采用 Onnela 型加权几何平均口径, 把构成三角形的三条边的权重各取立方根后相乘、再对焦点银行的所有邻居对求平均, 而自我网络密度只数边的有无、完全丢弃权重。二者因此在同一张加权图上取值不同, 且聚类系数因几何平均涉及浮点开方与求和次序敏感而落入 BLAS 非确定网络列清单, 自我网络密度则纯整数运算逐位确定——这是它们最实用、最可操作的区分点。其二是结构约束 (constraint, Burt 口径): 结构约束是加权的、把焦点银行对各邻居的投资 (共现强度) 集中度也计入的复合指标, 度量的是焦点银行受制于其邻域的程度, 且同样在度数小于二时置 NaN; 自我网络密度只测邻居间连通比例、不测焦点银行对各邻居的权重分布, 语义更单纯, 二者虽同属结构洞轴线但一个测"约束"、一个测"闭合"。其三是有效规模 (effective size): 它测的是"扣除冗余后焦点银行还剩多少个非冗余接触", 量纲是接触数目而非比例, 与自我网络密度大体呈此消彼长但并非互为倒数或线性变换。

除结构洞三兄弟外, 还须与几个语义相近但轴线不同的指标划清界限。与核数 (coreness, 生产者内 bank_coreness) 的区分在于层级: coreness 是 Seidman (1983) 最小度嵌套分解所赋予的全局层级标签, 回答"这家银行属于网络第几层核", 是一个跨越整张图的全局位置量; 自我网络密度只看焦点银行一跳邻域内部的连通, 是纯局部量, 高 coreness 的银行未必有高自我网络密度。与平均邻居度 (bank_avg_nbr_deg) 的区分在于对象: 后者测"我的邻居们各自有多少朋友" (邻居的受欢迎程度), 而自我网络密度测"我的邻居们彼此是不是朋友" (邻居间的相互连通), 二者刻画的是邻域的两个正交侧面, 可以一个高一个低。与集体影响力 (bank_ci) 的区分在于机制: CI 把焦点银行度数与其若干跳外邻居度数相乘, 是传播影响力 (谁是最优扩散种子) 的代理, 与"局部是否闭合"无直接关系。最后须与网络级年度指标 (net_avg_cluster_yr、net_transitivity_yr) 区分粒度: 后者是把全网所有节点的聚类/传递性求年度平均后落到面板每一行 (同年所有银行取同一值), 属年份级标量; 自我网络密度是逐银行逐年的局部量, 承载银行间横截面异质。理解这一整套区分, 才能在回归里避免把高度共线的结构洞族测度、与语义不同的核层型或传播型指标错误地并入同一识别式; 也才能把"闭合轴" (聚类/密度/约束) 与"居中轴" (度数/介数/接近度) 以及 Newman (2005) 那类基于随机游走当前流的路径型中心度, 分辨为互补而非替代的刻画。

最后还须在"网络从何而来"这一更根本的层面, 把本列的底层邻接与项目内外两类相邻网络基底区分开。项目内, 银行间除了本家族依托的报道共现网, 还有认知邻近网 (以银行报道文本的 TF-IDF 相似度为边权) 与嵌入同业网 (以付费嵌入向量余弦为边权): 共现网的边是离散的联合曝光事件计数, 回答"谁和谁被一同报道"; 认知/嵌入网的边是连续的语言相似度, 回答"谁和谁被以相似的方式报道"。两类基底可以给出完全不同的邻居集——两家从不同篇现身、但被媒体用几乎相同话语框架书写的银行, 在共现网中无边、在认知网中却高度邻近——因此从共现网读出的自我网络密度, 不能与认知/嵌入网上的任何结构量互换解读。这一"共现计数 vs 文本相似"的分野在文献里有清晰对应: Hoberg 和 Phillips (2016) 用产品描述文本相似度构造的产业网络属后者的经典范式, Li 等 (2026) 从风险披露文本中恢复金融网络连通结构亦属同一传统; 本列则站在共现计数一侧。Wang, Hou 和 Liu (2023, Accounting & Finance) 证明公司在共同持股网络中的结构洞(邻居互不连通、低密度)位置可通过信息控制机制降低负面媒体报道, 为本列"自我网络密度低=经纪/信息控制优势"在媒体覆盖情境下的经济含义提供直接实证对照。Guan (2024, Management System Engineering) 发现自我网络密度会调节结构洞与中心度对市场绩效的交互效应, 支持本列在结构洞轴线以外还需与度数等其他结构量联合解读的处理原则。Tang, Wang, Guan 和 Sun (2025, European Management Journal) 发现焦点企业自我网络密度与技术侵入呈倒U型关系、而伙伴企业自我网络密度呈负向关系,为本列自我网络密度构念在联盟情境下的非线性经济后果提供了2025年最新实证对照。Huang 和 Hsueh (2023, Technology Analysis & Strategic Management) 考察产业集群内自我网络密度对结构洞与中心度影响创新绩效的调节作用,支持本列密度需与其他结构量联合解读、不宜单独作为回归右手侧的处理原则。项目外, 还须与真实敞口网络划界: Wang 等 (2020) 刻画的中国企业间担保网络、以及同业拆借与股权网络, 边代表真金白银的合同性风险敞口; 媒体共现网的边只代表舆论注意力层面的联合曝光, 二者对系统性风险的含义不同 (前者传导违约损失, 后者传导预期与关注)。把本列的高低误读为"资产负债表意义上的抱团"是构念漂移; 正确的表述是"媒体注意力结构意义上的局部闭合", 其与真实敞口网络结构量的相关性本身是一个待检验的实证问题, 而非可默认的前提。

【已知局限与稳健性梯子】
本家族的稳健性设计核心是"网络构造判据敏感性"(2026-07-03 引入): 同一自我网络密度按银行∧银行共现判据分三轨计算——同篇 (无后缀 canonical, 现行口径)、±1 句窗 (_win1)、严格同句 (_sent)。判据主体是银行与银行的邻近共现, 判定原语为 entity_context.map_bank_sentence_positions 加 bank_pairs_within_sentence_window, 扫描文本恒为 prepend_title 拼接后的标题加正文 (标题自成第 0 句, match_in_title 恒真, 镜像 stage 13 的标题盲区修复)。判据分轨路径还内置 phantom 边防线: 每个多银行 docid 分组内只让该篇幸存的 target_bank 别名入参定位, 非幸存银行不参与句级扫描、不可能凭空成边, 从而保证三判据轨的节点全集严格一致、边集随判据收紧单调变严。必须钉死的一条铁律是: 判据后缀 (_win1/_sent) 与三轨文本后缀 (_full/_ctx/_ss) 是两个正交的概念空间——前者刻画银行∧银行边的严格程度, 后者刻画银行∧金科文本窗口, 两者禁混进同一 over-identified Hansen J。三判据之间也同理: article、win1、sent 三者各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 它们属于规格稳健性并排 (镜像政治词权重梯度、词典消融梯度的先例), 刻意不设 FWER 模板——因为 Romano 和 Wolf (2005) 式的跨模型 rwolf 步降检验先例只覆盖"同一构念的替代 headline 测量", 而三判据是同一构念在不同边定义下的规格变体, 不属该模板适用域。判据轨呈嵌套关系: 严格同句的边集是 ±1 句窗边集的子集, 后者又是同篇边集的子集; 但自我网络密度不是判据的单调变换, 因为收紧判据同时缩小分子 (邻居间边) 与分母 (焦点银行度数 k), 比值可上可下, 且更多银行因 k 降至一以下而落 NaN, 可计算样本随之收缩——这正是判据梯子作为真实稳健性 (而非机械重标度) 的价值所在。

除判据梯子外, 本家族还有若干必须在解读时正视的局限。第一, 结构洞族的高度共线性: 自我网络密度与同族的结构约束、有效规模在构念上描述的是同一枚硬币 (局部封闭对经纪) 的不同侧面, 三者在样本内通常高度相关, 因而绝不可把它们同时塞进同一个识别式充当彼此独立的解释变量——这与词典消融梯度里各语言学规则变体高度共线时"报相关而非并入同式"的处理原则同源; 正确做法是择一进入主回归、其余作为不分主次的稳健性对照并排呈现。第二, 0 与 NaN 语义须严格区分: NaN = 焦点银行邻居数不足二、密度不可计算, 0.0 = 有至少两个邻居但邻居间零互连 (真实的纯结构洞/经纪位), 下游回归绝不可把二者混为一谈, 此约定与结构约束、有效规模的 0-vs-NaN 约定一致; 对本列做均值或分位聚合时必须显式声明是在"可计算子群"上聚合, 否则会把结构不足的银行—年悄悄排除、制造样本选择偏倚。第三, 超边等权口径的抬升偏倚: 一篇提及多家银行的榜单式或批量监管通报会在其涉及银行间贡献大量等权边, 可能人为抬高相关邦联的邻居互连度、进而抬高自我网络密度; 度守恒的超边归一开关 (hyperedge_normalize, Newman 型 1/(N−1) 归一) 目前只在同篇主路径预留、判据分轨路径显式拒绝, 且 config 与 runner 均未透传、生产不可达, 因此这一潜在偏倚当前只能定性提示, 分析者若怀疑结果被大 N 榜单驱动, 可在稳健性检验中显式剔除超大共现文章后重算本列作为旁证。第四, 媒体共现的内生反馈: 媒体报道并非被动记录, 它与银行舆论热度、危机时点存在双向关系——You, Zhang 和 Zhang (2018) 记录了中文媒体"笔杆子权力"如何被有选择地行使, Fang 等 (2024) 与 Cookson 等 (2026) 则记录了媒体报道与存款人预期、风险传染之间的双向塑造, 因而本列的年度波动不宜简单解读为纯外生的结构变化。第五, 确定性作为稳健性资产: 与落入 BLAS 浮点漂移非确定网络列清单的加权聚类、当前流介数、调和中心度三基名 (各自的无后缀/_win1/_sent 三判据变体共九列) 不同, 自我网络密度纯整数计数除以整数组合数、不涉任何浮点线性代数, 跨次重建逐位可复现, 因而它在 golden 复现校验中可作稳定参照, 无需像那九列一样按全名 drop 排除。第六, 开发态退化: 在浅面板 (早期试跑 T=2) 上, 判据收紧后大量银行度数不足, _sent/_win1 轨的可计算格显著减少、退化为大面积 NaN 属预期; 生产态 T=19 全量语料的判据分轨播种目前 DEFERRED, 相关取值待生产机受控重生后方能落定。第七, 年度切片的时序粗化: 网络按自然年切片构建, 同年一月与十二月的共现在图上不可区分, 危机窗口内的密集联合曝光与平静期的零星同框被压进同一张年度图; 对于以周或月为尺度演化的舆论事件 (如挤兑传闻的社交媒体扩散, 参 Cookson 等 (2026)), 年度自我网络密度只能捕捉其年均痕迹而非动态峰值, 分析高频事件时不应指望本列提供窗口内分辨率。第八, 密度对度数 k 的机械依赖: 在有限图上, 邻居越多、要求其两两互连的组合数按 k 的平方增长, 大 k 银行的密度天然趋低, 小 k 银行的密度呈粗粒离散 (k 等于二时只能取零、二分之一不可达、或一), 因此密度的横截面比较隐含地混杂着度数差异; 稳健做法是在回归中同时控制度数、或按度数分层解读, 切忌把"国有大行密度低于城商行"这类原始差异直接读成经纪位置差异——其中相当一部分是 k 的组合数学在说话。这两点与前述结构洞族共线、0-vs-NaN 语义共同构成本列进入任何回归前必须过一遍的解读清单。

## VAR: bank_ego_density

【变体差分】
本列是家族 canonical, 即同篇共现判据 (article) 下的无后缀基准列, 也是本核心家族的 core 列。它区别于两个判据变体的唯一维度就是"边定义": 只要两家银行出现在同一篇 verified 报道内 (docid 相同、且两者均为该篇幸存的 target_bank), 就在该年共现网中记一条边, 无论二者在正文里相距多远、是否落在同一句或相邻句。这是三判据里最宽松的一端, 因而在给定年份下, 焦点银行的邻居数目 k 最大、自我网络的边最稠密, 可计算 (非 NaN) 的银行—年格也最多。就其自身语义而言: 它测的是"焦点银行在整篇报道层面认识的那一圈同行, 彼此之间在整篇报道层面也互相认识的比例"。取值一端为一, 表示焦点银行的邻居们几乎两两都曾与彼此同篇现身、局部结构高度闭合、信息冗余、对应 Coleman 式闭合社会资本; 另一端为零, 表示这些邻居彼此从不同篇共现、焦点银行处在把互不往来的两拨银行桥接起来的经纪位、跨越结构洞、对应 Burt (2004) 的信息与控制优势。

作为 canonical 列, 它承担三重职责。其一, 它是家族的确定性锚: 因为纯整数计数除以整数组合数、不涉浮点线性代数, 它跨次重建逐位可复现, 不进入 BLAS 浮点漂移非确定网络列清单 (那份清单收的是加权聚类、当前流介数、调和中心度三基名的九个判据变体), 因而可放心用作 golden 复现的稳定参照。其二, 它是判据梯子的基准臂: _win1 与 _sent 两个更严变体一律以本列为不分主次的稳健性对照, 三者各自 just-identified 并排、禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀 (_full/_ctx/_ss) 属正交概念空间, 亦禁混同一 Hansen J。其三, 它是结构洞—闭合轴线在面板里的落点, 与同为结构洞族的加权聚类系数、结构约束、有效规模构念相邻但口径各异 (本列纯二值、无权、比例归一)。落列时的口径细节: 焦点银行度数 k 小于等于一时该格为 NaN (邻居不足两个、密度无定义), 此 NaN 须与取值 0.0 (有邻居但邻居间零互连、真实经纪位) 在下游严格区分, 不可当作缺失一概填补或删除。数据域为 full-only 留篇门控下的 verified 展开帧 (24_herd_decay), 与全仓其余面板测度聚合域一致, 因而本列的银行—年宇宙与 n_articles 口径同源、不含规则预筛假阳性。构念的绩效与识别含义参见 Nezami, Chisam 和 Palmatier (2025)、Bramoullé, Djebbari 和 Fortin (2009) 与 Grieser 等 (2022)。

需要进一步澄清本 canonical 列在同篇口径下的两个边界行为, 以免下游误用。第一个边界是"孤立与叶节点": 若焦点银行在某年完全不与任何其他银行同篇共现 (度数为零), 或只与唯一一家银行共现 (度数为一), 本列一律为 NaN——前者是因为它根本没有自我网络, 后者是因为单一邻居无法构成任何邻居对。这类 NaN 在浅面板上尤为常见, 分析者若直接对本列做均值或分位数聚合, 必须显式声明是在"可计算子群"上聚合, 否则会把结构不足的银行—年悄悄排除、制造样本选择。第二个边界是"完全闭合的小自我网络": 当焦点银行恰有两个邻居且这两个邻居也直接共现时, 本列取值为一 (唯一的邻居对已成边); 这类高值在小 k 情形下极易出现, 因而在解读高密度时须联合度数 k 一起看, 单看密度可能把"只有两三个抱团邻居的小城商行"与"有几十个互连邻居的国有大行"混为一谈——前者的高密度统计上更脆弱、更易被单篇报道扰动。正因如此, 本列在实证中通常不单独进入回归, 而是与度数、有效规模、结构约束等结构洞族测度联合解读, 或作为同群溢出权重矩阵 W 构造中"局部封闭度"这一维度的输入; 金融网络位置对绩效、风险与信息扩散的经济含义可再参 Yu, Hu 和 Zhong (2024)、Jackson 和 Pernoud (2021)。

## VAR: bank_ego_density_sent

【变体差分】
本列是自我网络密度在严格同句判据 (criterion='sent', 落列后缀 _sent) 下的稳健性变体, tier=standard。它与 canonical 的唯一差异在边定义收到最紧的一端: 两家银行只有出现在同一句话里 (win_radius=0), 才在该年共现网中成边——判定走 docid 组内的句级重扫, 由 map_bank_sentence_positions 在 prepend_title 拼接后的标题加正文上定位各银行的句索引集合 (标题为第 0 句), 再由 bank_pairs_within_sentence_window 以句距为零判定成对。节点全集与 canonical 完全一致 (同为该年幸存银行), 仅边集更严: 严格同句的边集是 ±1 句窗与同篇边集的共同子集。收紧到同句的后果是, 焦点银行的邻居数目 k 系统性变小、更多银行度数跌破二而落 NaN, 邻居间的实际连边也更稀疏, 因而本列的可计算样本比 canonical 更小、更聚焦于"在单句尺度上被强绑定同框"的银行子群。语义上, 它测的是最保守口径下的局部封闭度: 只有当焦点银行那些"同句级密友"彼此之间也常在同一句里被并列提及时, 本列才取高值。之所以保留这一严判据轨, 是因为同篇共现可能把仅在一篇长报道里各自被提及、实则语义无关的两家银行也记为邻居 (弱共现噪声), 而同句判据能滤掉这类跨段落的偶然同篇、只留下真正被文本强关联的银行对, 从而检验 canonical 结论是否被弱共现边驱动。本列与 canonical 及 _win1 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据后缀 _sent 与三轨文本后缀 _ss 虽都涉"同句", 但主体不同 (银行∧银行 vs 银行∧金科)、属正交概念空间, 严禁混用。0-vs-NaN 语义、确定性 (纯整数计数、非 BLAS 漂移列) 与 canonical 一致。开发态早期试跑 T=2 上本轨大面积退化为 NaN 属预期; 生产态判据分轨播种 DEFERRED。

## VAR: bank_ego_density_win1

【变体差分】
本列是自我网络密度在 ±1 句窗判据 (criterion='win1', 落列后缀 _win1) 下的稳健性变体, tier=standard, 严格程度居于 canonical (同篇) 与 _sent (严格同句) 之间。它与 canonical 的唯一差异同样落在边定义: 两家银行只有出现在相距不超过一句的句窗内 (win_radius=1, 取自 config/panel.yaml::network_criteria.win_radius) 才成边——判定同样走 docid 组内句级重扫, 由 map_bank_sentence_positions 在 prepend_title 拼接文本上定位句索引 (标题为第 0 句, match_in_title 恒真), 再由 bank_pairs_within_sentence_window 以句距不超过一判定成对。须特别提示: 此处的 win_radius 键与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科保留判据) 是两个不同键、互不联动, 判据主体一个是银行∧银行、一个是银行∧金科, 不可混淆。边集嵌套关系为: 严格同句边集 ⊆ ±1 句窗边集 ⊆ 同篇边集, 故本列的稠密度与可计算样本量介于两端之间。语义上, ±1 句窗放宽了"同句"的过严约束, 承认相邻一句内的银行并置也构成有意义的媒体强关联 (例如上一句点名甲行、下一句紧接乙行的对比式行文), 又比同篇口径更能排除跨段落的偶然同框, 因而它捕捉的是"近距离文本邻近"尺度上的局部封闭度。保留本轨的价值在于, 它与 _sent 一同构成一条从宽到严的判据梯子: 若自我网络密度的经济关联在同篇、±1 句窗、严格同句三种边定义下方向一致、量级稳健, 就能证明主结论不被某一特定共现口径的宽严取值所驱动。本列与 canonical 及 _sent 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据后缀 _win1 与三轨文本后缀属正交概念空间。0-vs-NaN 语义 (k≤1→NaN 不可计算, 0.0 为真实经纪位)、纯整数计数的逐位确定性均与 canonical 一致, 本列不属 BLAS 浮点漂移非确定网络列。开发态早期试跑 T=2 上判据收紧导致的大面积 NaN 退化属预期, 生产态 T=19 判据分轨播种 DEFERRED。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
de Paula, Á., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Han, M., Kim, S. H., & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould–Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Wang, L., Hou, W., & Liu, Y. (2023). How do co-shareholding networks affect negative media coverage? Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13091
Guan, F. (2024). Ego-network characteristics moderates the interaction of structural hole and centrality on market performance: based on coopetition network. Management System Engineering. https://doi.org/10.1007/s44176-024-00031-0
Tang, L., Wang, T., Guan, F., & Sun, L. (2025). Don't ignore either side: The differential impact of ego-network density of the focal firm and partner on technological invasion. European Management Journal. https://doi.org/10.1016/j.emj.2024.05.005
Huang, C.-H., & Hsueh, C.-C. (2023). How does ego-network structure affect innovation within industrial clusters? The moderating effect of ego-network density. Technology Analysis & Strategic Management. https://doi.org/10.1080/09537325.2023.2217458
<!-- rendered-citations:end -->
