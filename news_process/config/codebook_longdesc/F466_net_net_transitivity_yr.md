---
family_id: F466
columns:
- net_transitivity_yr
- net_transitivity_yr_sent
- net_transitivity_yr_win1
unit: 无量纲比率 (全局传递性, 取值区间 [0, 1])
formula: "net_transitivity_yr = 3 × (三角形数) / (连通三元组数) = nx.transitivity(G); G = 年度银行共现无向图, 节点 = 目标银行, 边 = 同一判据下两家银行的共现 (每篇每对 +1 无权计边, transitivity 忽略边权)"
producer: news_process/pipeline/panel/network_spillover.py::_net_level_extra_metrics ; news_process/pipeline/panel/export.py (标签)
upstream:
- 13_cooccurrence_filter.parquet
- 40_article_bank_level (df_exploded 银行×文章展开集)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
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
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1103/PhysRevE.70.066111
  type: journal
  authors: Clauset, A., Newman, M. E. J., & Moore, C.
  year: 2004
  title: "Finding community structure in very large networks"
  venue: Physical Review E
  vol: 70
  issue: 6
  pages_or_artno: 066111
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
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1016/j.najef.2024.102307"
  title: "Text Spillover: Measuring connectedness of financial institutions based on news text data"
  authors: "Klaucke, Konstantin"
  year: 2025
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
- doi: "10.1016/j.jfineco.2025.104007"
  title: "Global Business Networks"
  authors: "Breitung, Christian, & Müller, Sebastian"
  year: 2025
  venue: "Journal of Financial Economics"
  type: "journal"
- doi: "10.3390/systems13121110"
  title: "Structure and Evolution of the Global Financial Services Greenfield FDI Network: Complex System Analysis Based on the TERGM Model"
  authors: "Zhang, Guoli, Qu, Ruxiao, Wang, Lujian, & Lu, Fang"
  year: 2025
  venue: "Systems"
  type: "journal"
new_dois:
  - "10.1016/j.procs.2023.08.056"
  - "10.1016/j.najef.2024.102307"
  - "10.1016/j.jfineco.2025.104007"
  - "10.3390/systems13121110"
---

## CORE

【构念与来源】
本家族刻画的是「银行共现网络」在给定年份的全局传递性 (global transitivity), 也就是网络科学里的整体聚类倾向。构念的直觉可以用一句大白话说清楚: 如果甲银行和乙银行经常被媒体放在同一篇报道里谈论, 乙银行又和丙银行经常一起出现, 那么甲和丙是不是也倾向于一起出现? 传递性衡量的正是这种「朋友的朋友也是朋友」的闭合程度。取值落在零到一的闭区间内, 数值越高说明该年的银行舆论网络越像一个个抱团的紧密团块, 三方共同被提及的三角闭合越普遍; 数值越低则说明网络更松散、更接近星形或链形, 银行之间的共同曝光缺乏三方闭合。

数据来源上, 本指标是新闻文本共现的年度聚合产物, 不依赖任何外部关系数据库。上游是经 stage 13 共现硬过滤后的报道集与 stage 40 的银行×文章展开集 (df_exploded): 每一条报道在被判定为「目标银行与金融科技词邻近共现」而留篇后, 若一篇报道同时提及两家及以上目标银行, 就在这些银行之间连一条无向边。把某一自然年内所有报道的这类共现对累加起来, 就得到该年的银行共现邻接矩阵, 再用 networkx 构造无向图 G, 节点是目标银行, 边权是两家银行在该年被同篇共同提及的次数。需要强调的是, 全局传递性的计算刻意忽略边权 (无权三角比), 因此它捕捉的是「拓扑上谁和谁闭合」而非「闭合得多紧」。这与家族内的加权强度类指标 (如 bank_strength_cent) 口径不同, 不可混读。

【方法学与计算】
落地实现是 nx.transitivity(G), 定义为三倍的三角形数除以连通三元组数, 即所有以某节点为中心的长度为二的路径中, 两端点也直接相连 (闭合成三角) 的比例。它与「平均聚类系数」(net_avg_cluster_yr, 逐节点聚类系数再平均) 是两个相关但不等价的量: 全局传递性以三元组为权重, 对高度数节点的三角贡献赋予更大权重, 而平均聚类系数对每个节点等权, 因此在度数高度不均的共现网络里两者会系统性分叉。本家族只承载全局传递性口径。

计算发生在纯拓扑层, 全程无随机数、无谱分解、无浮点迭代求解, 因此是确定性且 golden-safe 的 — 它不进入本项目已知的 BLAS 浮点漂移列排除集 (那三个基名 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 才逐位不可复现), 换言之本家族的三列在受控重生下逐位稳定。计算逻辑抽在 _net_level_extra_metrics 独立纯函数内, 只读复用已建的图对象 G, 不重建图, 遵循加性铁律以免扰动既有列的哈希。结果是年度网络级标量, 在落面板时被广播到该年所有银行行上 — 这意味着它在含年度固定效应的设定里会被年 FE 完全吸收 (年内对所有银行恒定), 只能作为不含年 FE 的结构控制或与银行层变量的交乘项进入回归, 这一点在 producer 源码注释中被明确标注 (§3.1 Q4)。另一处必须披露的方法学局限是「clique 膨胀」: 一篇同时提及 N 家银行的报道会在这 N 家之间投影出一个完全子图 (clique), 使三角闭合被机械抬高, 从而向上虚增全局传递性与模块度; transitivity 因忽略边权而无加权孪生列 (modularity 尚可有 net_modularity_hn_yr 加权版), 使用者须知道高传递性可能部分来自多银行长报道的 clique 投影而非真实的三方独立闭合。

【文献定位】
全局传递性与小世界结构的构念根源在 Watts 和 Strogatz (1998): 他们指出真实网络往往兼具高聚类 (高传递性) 与短路径长度, 传递性正是刻画「局部抱团」的核心量。将传递性置于社群结构谱系中理解, 可参照 Newman 和 Girvan (2004) 及 Clauset、Newman 和 Moore (2004) 的社群检测框架 — 高传递性网络通常对应清晰的社群划分, 与本家族并列的 net_modularity_yr 恰用后者的贪婪算法度量社群强度, 两者互为补充但口径正交。在金融与组织研究中, 网络结构指标作为解释变量的合法性由多支文献支撑: Nezami、Chisam 和 Palmatier (2025) 对网络中心度与企业绩效关系做了元分析, 提示网络位置对绩效的解释力真实但异质 (该白名单条目明确注记不背书具体的 bank_clustering 用法, 此处仅援引其构念层结论); Yu、Hu 和 Zhong (2024) 论证金融网络的中心度通过信息扩散影响资产定价; Li 等 (2026) 则直接从文本风险披露中抽取金融网络结构与连通性, 与本项目从新闻共现文本重构银行网络的方法论同源; Klaucke (2025, The North American Journal of Economics and Finance) 同样用新闻文本构造金融机构间的连通性测度, 与本家族从新闻共现文本自下而上重构银行网络并计算全局传递性的方法论直接同源。在系统性风险语境下, Jackson 和 Pernoud (2021) 的综述与 Duarte 和 Eisenbach (2021) 的火线抛售溢出研究表明, 网络的闭合与连通拓扑是传染放大的结构基础, 为把年度传递性作为系统性风险环境的代理变量提供了理论支点。需要说明的是, 本项目的银行共现网络是一张「舆论关注网」而非资金往来网或担保网, 边的语义是「被媒体放在一起谈论」, 因此它捕捉的是投资者与公众注意力层面的银行关联结构, 而非资产负债表意义上的直接风险敞口。这一区分很重要: 高传递性在本网络中意味着某年银行舆论呈现明显的抱团三角闭合, 可能反映行业性的集体叙事 (例如整个板块被同一政策或同一风险事件裹挟), 而这类叙事传染本身正是文本情感溢出研究关心的对象。把注意力网络的传递性与资金网络的传递性并置理解, 有助于避免把「一起被报道」误读为「一起有敞口」。

【构念的时间维度与经济含义】
由于本指标按自然年聚合, 它天然承载了银行舆论网络的年度演化信息。一个可检验的经济假说是: 在行业冲击年份 (如互联网金融整顿、某类系统性事件爆发), 媒体倾向于把更多银行卷入同一篇叙事, 从而抬高共现网络的稠密度与三角闭合, 使当年的全局传递性上升; 而在平稳年份, 报道更分散、更聚焦单家银行, 传递性回落。因此本家族的跨年时间序列本身就是一个关于「银行舆论一体化程度」的宏观信号, 可与金融科技强度、行业负面冲击等年度变量对照阅读。不过, 正因它在年内对所有银行恒定并被年 FE 吸收, 其经济含义主要在两种设定下释放: 其一, 在不含年 FE 的模型中作为刻画舆论网络结构环境的年度控制; 其二, 与银行层处理变量 (如某家银行的金融科技暴露、情感倾向) 交乘, 检验「网络越抱团时, 银行个体特征对结果的边际影响是否被放大或衰减」这类调节假说。后一种用法与 Grieser 等 (2022) 和 Leary 与 Roberts (2014) 在公司金融中把网络结构作为溢出调节量的思路一脉相承。

【数据构造的稳健性与退化行为】
在数据构造层面还有若干须向使用者交代的性质。第一, 边的累加对同一年内的重复共现是叠加计数的 (每篇每对 +1), 但传递性忽略边权, 因此重复共现只影响强度类指标而不影响本家族 — 本家族只关心该年是否存在过至少一次共现所形成的拓扑三角。第二, 只含单家银行的报道不产生任何边, 不进入网络构造, 因此本指标只由多银行报道驱动; 若某年多银行报道极少 (如开发态 T=2 的稀疏样本), 图可能几乎无边, 传递性退化为零或 NaN, 这属预期而非缺陷, 生产态 T=19 的全量语料下不会出现此类退化。第三, 判据分轨路径在缺少 docid 或正文列时会 fail-soft 地把该年邻接置为全零 (节点保留、无边) 并发出告警, 而非崩溃整个 stage, 这一容错设计镜像了 FINTECH_AC=None 时的优雅降级先例。第四, 当同一 docid 组内多行的正文文本不一致时, 判据分轨路径会 loud 告警并取组首行 (F0.18 实测应为零组), 保证单条脏数据不至于污染整年网络。这些设计共同确保本家族在从开发态到生产态的规模跨越中行为一致、可审、可复现。

【与文本网络重构文献的方法论对话】
本家族从新闻共现文本自下而上重构银行关系网络的做法, 与近年兴起的「文本网络」测量文献直接对话。Li 等 (2026) 从企业的文本风险披露中抽取金融网络的结构与连通性, 与本项目从媒体报道共现抽取银行网络在方法论上高度同源: 两者都把「文本中的共同出现」视为潜在经济关联的可观测代理, 再用网络科学工具刻画其结构。这类方法的核心优势是覆盖面广、时效性强, 不依赖往往滞后且不完整的官方关系数据; 其代价是共现关系语义模糊 — 「一起被报道」既可能反映真实的业务关联, 也可能只是记者的叙事便利。全局传递性作为二阶结构量, 在一定程度上对这种测量噪声有平滑作用: 单条噪声边难以同时闭合出多个三角, 因此传递性比单条边的存在与否更稳健地反映网络的系统性抱团倾向。这也是本项目在节点级中心度之外额外引入网络级传递性作为结构控制的理由之一 — 它提供了对「整体网络有多闭合」这一维度的、相对抗噪的年度刻画。同样从文本抽取网络结构的做法也见于 Breitung 和 Müller (2025, Journal of Financial Economics), 用GPT-3从企业文本描述中生成63,000余家全球公司的时变商业网络, 方法论上与本项目从新闻共现文本构造银行网络同源; 而 Zhang、Qu、Wang 和 Lu (2025, Systems) 用时序指数随机图模型刻画全球金融服务业绿地FDI网络的传递闭合与聚类结构演化, 佐证传递性作为金融网络结构量的经验适用性。

【识别、内生性与稳健性推断的完整叙事】
把网络结构指标引入因果推断链条时, 除前述反射问题外, 还须正视网络本身的内生性: 银行的舆论共现结构可能与不可观测的行业冲击、政策周期共同决定, 使传递性与结果变量之间存在遗漏变量偏误。本项目对此的应对是分层的。第一层是设定层面: 承认本指标在年 FE 下被吸收, 主张其只作为不含年 FE 的结构环境控制或交乘调节量, 从而不把它当作可干预的处理变量做因果宣称。第二层是识别层面: 沿 Bramoullé、Djebbari 和 Fortin (2009) 的思路, 网络的非传递性 (传递性严格小于一) 本身提供了识别同侪效应的结构工具, 而 Boucher、Rendall、Ushchev 和 Zenou (2024) 与 Bramoullé、Djebbari 和 Fortin (2020) 进一步刻画了这类识别策略在更一般同侪机制下的适用边界。第三层是推断层面: 在把网络指标纳入回归后, 标准误须考虑网络自相关与聚类结构, 本项目在稳健性 battery 中对相关设定采用聚类稳健与自助 (bootstrap) 推断, 并对多重比较施加族错误率控制。第四层是稳健性梯子层面: 本家族的三个判据变体构成一条完整的判据敏感性梯子, 让使用者能直接观察主结论是否随「共现口径松紧」而漂移; 与本项目其它稳健性族 (三轨文本、co-primary 双轨嵌入、词典消融、政治词权重、per-model) 一样, 判据梯子内各臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。四层叠加, 使本家族既能作为信息量充分的网络结构度量进入实证, 又不越界成为无根据的因果宣称。使用者在援引本家族任一列时, 应连同披露其判据口径、年 FE 吸收性质与 clique 膨胀风险, 方为可审、可复现的规范用法。

【识别策略定位】
把网络结构指标放进回归会立刻触及同侪效应识别的经典难题。Manski (1993) 的反射问题指出, 当个体行为受同侪均值影响时, 内生效应、外生 (情境) 效应与相关效应在线性均值模型中不可分离; Bramoullé、Djebbari 和 Fortin (2009) 证明网络的非完全重叠结构 (朋友的朋友不总是朋友, 即传递性小于一) 恰恰提供了识别同侪效应所需的排他性工具变量 — 这使传递性不仅是一个描述量, 更与识别力直接相关: 传递性越接近一 (网络越闭合), 二阶邻居越坍缩为一阶邻居, 可用于识别的结构变异越枯竭。Bramoullé、Djebbari 和 Fortin (2020) 与 Boucher、Rendall、Ushchev 和 Zenou (2024) 的后续综述与理论进一步厘清了这一识别边界。在公司金融的经验层, Leary 和 Roberts (2014) 与 Grieser、Hadlock、LeSage 和 Zekhnini (2022) 展示了如何在网络溢出框架下识别同侪对企业财务政策的因果影响。本项目据此把年度传递性定位为「网络环境的结构控制/交乘调节量」而非因果处理变量, 且因其被年 FE 吸收, 主要在跨年结构演化或与银行层处理变量的交乘中发挥作用。

【与相邻测度的构念区分】
本家族须与三类相邻测度严格区分。其一, 与节点级中心度族 (bank_degree_cent 等) 区分: 中心度刻画单家银行在网络中的位置, 是银行×年层面的量; 传递性是整张年度网络的标量结构属性, 层级不同。其二, 与 net_avg_cluster_yr 区分: 后者是逐节点局部聚类系数的算术平均, 对节点等权; 前者以三元组为权, 对枢纽节点的三角贡献加权更重, 两者在度分布不均时不等价, 不能互相替代解读。其三, 与加权口径 (强度、加权模块度) 区分: 传递性无权, 只看三角是否闭合, 不看共现次数多寡, 因此对「弱连边是否算数」这一判据选择格外敏感 — 这正是本家族设置三个判据变体的原因。

【已知局限与稳健性梯子】
核心局限有三: 一是 clique 膨胀 (上文已述), 多银行长报道机械抬高传递性; 二是年 FE 吸收, 限制其可用的识别位置; 三是判据敏感性, 即「两家银行在一篇报道里靠得多近才算共现一次」这一口径直接决定网络的边集稠密度, 进而决定三角闭合的多寡。针对第三点, 本家族沿网络构造判据方向铺设了一条严格的稳健性梯子: 同篇判据 (无后缀 canonical, 现行生产口径, 只要两家银行出现在同一篇留篇报道中即计一条共现边) / 正负一句窗判据 (_win1, 要求两家银行出现在相距不超过 win_radius 句的窗口内) / 严格同句判据 (_sent, 要求两家银行出现在同一句内)。三个判据由松到紧, 边集逐级收缩, 网络逐级稀疏。这三个判据变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同判据的传递性混进同一个 over-identified 的 Hansen J 过度识别检验 — 这是本项目贯穿三轨文本、co-primary 双轨嵌入、词典消融梯度、政治词权重梯子、per-model 稳健性诸族的统一铁律, 网络判据梯子同受此约束。须特别澄清: 网络判据后缀 (无后缀 / _win1 / _sent) 与三轨文本后缀 (_full / _ctx / _ss) 是两个正交的概念空间 — 前者的判据主体是银行与银行的邻近共现 (银行∧银行口径), 后者的判据主体是银行与金融科技词的共现 (银行∧金科口径), 两者分别源自不同的原语函数 (前者是 map_bank_sentence_positions + bank_pairs_within_sentence_window, 后者是 stage 13/14 的共现过滤与三轨物化), 且各自读取不同的 config 键 (前者是 panel.yaml::network_criteria.win_radius, 后者是 filtering.yaml::cooccurrence_filter.sentence_radius, 互不联动), 绝不可交叉复用或混入同一 Hansen J。此外, 本指标的留篇分母口径与全仓一致地锚定 full-only 门控 (2026-06-29): 是否算作一篇进入网络构造的银行报道, 取决于 full 轨的留篇判定, ctx/ss 不参与网络边的构造。

## VAR: net_transitivity_yr

【变体差分】
本列是家族 canonical, 采用「同篇」判据 (无后缀), 也是现行生产口径与网络指标扩展 2026-06-21 的原始定义。其边的构造规则最宽松: 只要一篇经 full 轨留篇门控保留的报道同时提及两家及以上目标银行, 就在这些银行之间各连一条无向边 (每篇每对 +1, 对称计权, 但传递性计算忽略边权只看是否闭合)。这条主路径由 both-verified 主口径实现: 在同一 docid 下所有幸存 target_bank 行的集合内逐无序对累加, 保证每篇文章每对恰计一次; 该路径还保留了 hyperedge_normalize (Newman 1/(N-1) 超边归一) 的预留参数, 但该参数在判据分轨路径 (_win1/_sent) 中尚未接线, 若在分轨路径显式开启会 raise ValueError 以防三判据轨口径无警告分叉 — 这意味着无后缀主列是唯一可能承载超边归一的口径, 现阶段该参数默认关闭。

作为 canonical, 本列在 NETWORK_METRIC_BASES 这一 33 指标基名 SSOT 中登记, stata_export 的判据标签机械块与 gate 测试 (test_network_tritrack_expansion.py) 均从该 SSOT import 复用以防标签漂移。它落面板时是年度网络级标量并广播到该年全部银行, 因而在含年度固定效应的设定下被吸收, 只应作为不含年 FE 的结构控制或与银行层变量的交乘调节量进入模型。数值上它系统性地不小于同族更严判据的两列 (_win1、_sent): 判据越宽边集越密, 三角闭合的机会越多, 传递性越高。使用者须结合 clique 膨胀披露谨慎解读 — 同篇口径对多银行长报道最敏感, 一篇提及众多银行的综述性报道会在其间投影出完整 clique, 把本列的传递性向上抬升。本列与 _win1、_sent 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 且判据后缀与三轨文本后缀 (_full/_ctx/_ss) 属正交概念空间, 不可交叉。它与家族外的 net_avg_cluster_yr (逐节点等权聚类均值) 构念区分明确: 本列以三元组为权、对枢纽节点三角贡献加权更重, 二者在度分布不均时不等价。

进一步说明 canonical 口径的经济解读与用法边界。作为最宽判据, 本列把「同篇被提及」全部记为共现关系, 因而它测量的是最广义的银行舆论关联 — 只要记者在一篇报道的任意位置把两家银行并置, 无论相隔多远, 都算作一次关联。这一宽口径的优点是样本利用最充分、边集最稠密, 在语料较薄的年份仍能给出非平凡的网络结构; 缺点是它对综述性、盘点性长报道最敏感 — 一篇年终盘点或行业综述可能同时点名十余家银行, 在它们之间投影出一个完整 clique, 使传递性被机械抬高。因此当研究关注的是「银行之间真正紧密的语境共现」时, 应以 _win1 或 _sent 作为更保守的对照臂检验主结论的判据稳健性。反之, 当研究关注的是「行业整体的舆论一体化程度」时, canonical 的宽口径反而更贴切, 因为它不排斥跨段落的行业性并置。实务上推荐的报告方式是: 以 canonical 为主口径给出点估计, 同时并列 _win1 与 _sent 两个更紧判据下的结果, 由读者判断结论是否随判据松紧而漂移。由于三列均被年 FE 吸收, 三者的对照通常发生在不含年 FE 的结构控制设定或交乘设定中, 而非在同一含年 FE 的回归里叠放。再次重申: 本列与 _win1、_sent 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同判据的传递性混进同一个 over-identified 的 Hansen J 过度识别检验, 也不得与三轨文本后缀 (_full/_ctx/_ss) 的银行∧金科口径交叉复用 — 判据敏感性与文本轨道敏感性是两条正交的稳健性梯子, 各走各的自回归、各进各的 just-identified 设定。

## VAR: net_transitivity_yr_sent

【变体差分】
本列是「严格同句」判据变体 (_sent 后缀), 是家族内最紧的判据臂。它区别于 canonical 的唯一维度是网络边的构造判据: 只有当两家目标银行出现在同一句内 (win_radius=0) 时才在它们之间计一条共现边, 而非 canonical 那样「同篇即计」。落地路径走判据分轨的 docid 组内句级重扫: 对每个含两家及以上幸存银行的 docid 组, 用 map_bank_sentence_positions 把标题与正文映射为逐句的银行位置, 再由 bank_pairs_within_sentence_window 以 radius=0 抽取同句共现对, 逐对在邻接矩阵累加。此路径复用与 stage 11/13/ctx/ss 同一套否定 AC 与短名排除事实源 (禁裸 AC, 防「涉农行业」误命中「农行」这类短名假阳性), 保证判据分轨与主线口径的实体识别一致。由于同句要求最严, _sent 的边集最稀疏、网络最松散, 其传递性数值通常是同族三列中最低的一档, 在样本稀疏 (如开发态 T=2) 时甚至可能因图内边过少而退化为零或近零, 属预期行为而非缺陷。它捕捉的是「真正被记者写进同一个句子里」的强共现闭合, 剔除了同篇但分处不同段落的弱关联, 因而对 clique 膨胀的敏感度低于 canonical。本列与 canonical、_win1 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀正交, 不可交叉。它同样是年度网络级标量, 广播到该年全部银行, 在年 FE 下被吸收。

## VAR: net_transitivity_yr_win1

【变体差分】
本列是「正负一句窗」判据变体 (_win1 后缀), 松紧介于 canonical 与 _sent 之间。它区别于 canonical 的唯一维度是边的构造判据: 两家目标银行须出现在相距不超过 win_radius 句的窗口内 (win_radius 取 config/panel.yaml::network_criteria.win_radius, 默认 1, 即正负一句窗) 才计一条共现边。落地同样走判据分轨的 docid 组内句级重扫路径, 与 _sent 共享 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 原语, 差别仅在传入的 radius: _sent 是 radius=0 (严格同句), _win1 是 radius=win_radius (默认 1)。因此边集稠密度与传递性数值一般落在 canonical (最宽、最高) 与 _sent (最紧、最低) 之间, 构成一条由松到紧的单调判据梯子中的中间档。须再次强调 win_radius 取自 panel.yaml::network_criteria.win_radius, 与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科过滤用的句半径) 是两个不同的 config 键, 互不联动, 改一个不会牵动另一个。本列同样复用与主线一致的否定 AC 与短名排除事实源, 保证实体识别口径统一。作为句窗判据, _win1 比 canonical 更能排除「同篇但相隔甚远」的伪共现, 又比 _sent 保留了跨句但邻近的语境共现, 提供了对判据松紧的中间敏感性检验。本列与 canonical、_sent 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀 (_full/_ctx/_ss) 属正交概念空间, 不可交叉。它是年度网络级标量, 广播到该年全部银行, 在含年度固定效应的设定下被吸收, 只应作为不含年 FE 的结构控制或与银行层变量的交乘项进入回归。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. Physical Review E, 70(6), 27721. https://doi.org/10.1103/PhysRevE.70.066111
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Klaucke, Konstantin. (2025). Text Spillover: Measuring connectedness of financial institutions based on news text data. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2024.102307
Breitung, Christian, & Müller, Sebastian. (2025). Global Business Networks. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2025.104007
Zhang, Guoli, Qu, Ruxiao, Wang, Lujian, & Lu, Fang. (2025). Structure and Evolution of the Global Financial Services Greenfield FDI Network: Complex System Analysis Based on the TERGM Model. Systems. https://doi.org/10.3390/systems13121110
<!-- rendered-citations:end -->
