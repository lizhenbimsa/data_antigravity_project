---
family_id: F090
columns:
- bank_effective_size
- bank_effective_size_sent
- bank_effective_size_win1
unit: 有效规模 (Burt 结构洞非冗余邻居数; 无量纲, 尺度同节点度数, 近似值域 [1, 度数 k])
formula: "bank_effective_size = nx.effective_size(G, weight='weight'); G = 年度银行∧银行共现无向加权图 (节点=当年幸存 target_bank, 边=同 docid 共现, 边权=当年共现文章数); 有效规模 = 度数 − 加权冗余度 (Burt 结构洞); G.degree(b)==0 → NaN。判据变体后缀 {同篇无后缀 / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: "news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (build_adjacency_matrix + nx.effective_size); 标签与判据后缀归一 news_process/pipeline/panel/codebook.py"
upstream:
- 24_herd_decay.parquet (df_exploded; verified 篇章级 docid/target_bank/year/内容/标题, 年度银行∧银行共现网络构造输入)
- 40_panel_yearly.parquet (bank-year 面板骨架; 33 网络列按 target_bank+year left-join 落面板)
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
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: 103223
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: Review of Economic Studies
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
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
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
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: "10.1080/2833115x.2026.2662558"
  type: journal
  authors: "Lei, J., Campbell-Verduyn, M., Steglich, C., & Wittek, R."
  year: 2026
  title: "The evolution of global bank-to-nonbank networks, 2002–2022: a stochastic actor-oriented analysis"
  venue: "Finance and Space"
- doi: "10.1016/j.najef.2024.102307"
  title: "Text Spillover: Measuring connectedness of financial institutions based on news text data"
  authors: "Klaucke, K."
  year: 2025
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
- doi: "10.1007/s10490-026-10116-x"
  title: "Agentic, powerful, but unethical: New ventures' ethical practices as the outcome of entrepreneurs' networking behaviors and structural holes"
  authors: "Wang, Y., & Wei, F."
  year: 2026
  venue: "Asia Pacific Journal of Management"
  type: "journal"
new_dois:
  - "10.1080/2833115x.2026.2662558"
  - "10.1016/j.najef.2024.102307"
  - "10.1007/s10490-026-10116-x"
---

## CORE

【构念与来源】
本家族刻画的是每一家目标银行在"银行∧银行新闻共现网络"中的有效规模, 即 Burt (2004) 结构洞理论中的 effective size 概念在中国银行业金融科技新闻语料上的落地。有效规模回答的问题是: 一家银行在同一批新闻里与多少家其它银行被一起提及, 而这些被共同提及的同行之间又有多少是"彼此重复的"。若一家银行的所有共现同行彼此之间也高度互相共现, 那么它们所承载的信息在很大程度上是冗余的, 该银行真正能触达的"非重复"信息源就少; 反之, 若它的共现同行彼此互不相干、分处不同的信息簇, 该银行就跨越了多个结构洞, 其有效规模接近其原始共现邻居数。构念的经济学含义是: 有效规模高的银行处在信息不重叠、跨群桥接的位置上, 更可能率先接触到异质的金融科技动向、监管信号与同业创新, 而有效规模低的银行则被锁在一个内部高度冗余的小圈子里。数据来源是本项目的中文银行与金融科技新闻语料, 经 stage 13 银行∧金科邻近共现硬过滤、stage 21 full-only 留篇门控清洗后, 进入 24_herd_decay 的 verified 篇章级宇宙 (df_exploded), 每一行是一篇文章对一家目标银行的命中记录, 携带 docid、target_bank、year 与标题正文文本。网络的"节点"是当年在该 verified 宇宙中存活的目标银行, "边"是这些银行在同一篇报道中被共同提及的事实。需要强调, 此处的判据主体是银行与银行的共现 (bank∧bank), 与 stage 13 用于留篇的银行与金融科技词的共现 (bank∧fintech) 是两个正交的概念空间, 边权与节点集均由前者决定。之所以选择新闻共现而非监管报表或持股关系来构造银行间网络, 是因为本项目的研究对象是媒体信息环境对银行金融科技行为的塑造: 两家银行被同一篇报道并列书写, 意味着它们在公众与市场的认知里被归入同一叙事框架 (同一波监管风向、同一类创新竞争、同一场风险事件), 这种"叙事共现"恰是信息溢出与同群比较发生的天然界面。有效规模由此度量的是"一家银行在媒体叙事网络里所处的桥接位置能触达多广的非重叠信息面"。落到面板, 本家族三列均为 bank-year 粒度: 网络逐年重建, 有效规模按 target_bank 与 year 左连接进 40_panel_yearly 面板, 因此同一家银行在不同年份可有不同的有效规模, 反映其网络位置随媒体叙事结构的年度演化。直观上, 有效规模高的银行像是横跨多个不相往来的新闻小圈子的"信息枢纽", 有效规模低的银行则被困在一个成员彼此高度重复报道的封闭簇内。

【方法学与计算】
计算在 network_spillover.py 的 compute_bank_network_centrality 中逐年进行。第一步 build_adjacency_matrix 对给定年份切出 df_year, 取其 target_bank 去重排序得到节点全集, 然后按 docid 分组: 凡在同一篇文章 (同一 docid) 内共同出现的银行, 其两两无序对在对称邻接矩阵上各加一, 因而边权等于"当年共同提及这两家银行的文章篇数", 是一个正整数计数权重。第二步据此邻接矩阵建立无向加权图 G (边属性 weight = 共现次数), 并把当年所有节点 (含孤立银行) 都放进图里。第三步调用 networkx 的 nx.effective_size(G, weight='weight') 得到每个节点的有效规模。在无权情形下, 有效规模等于度数减去邻居间的平均冗余, 即 k − 2t/k (k 为度数, t 为邻居之间的连边数); 在本项目的加权图上, networkx 采用 Burt 结构洞框架的加权推广, 用比例投入强度与边际强度衡量每个邻居的冗余程度, 再由度数扣减冗余总量得到有效规模, 因此边权 (共现强度) 越强的冗余联系被扣减得越多。缺失约定是: 当 G.degree(b)==0 (该银行当年无任何共现邻居, 孤立点) 时, bank_effective_size 置 NaN 而非 0, 以区分"零非冗余邻居"与"网络中缺席"; 计算过程一旦抛异常, 该年全体银行的有效规模亦置 NaN, 属 fail-soft 降级。判据敏感性由 criterion 与配套 suffix 参数驱动: 同篇口径 (criterion='article') 落无后缀 canonical 列, ±win_radius 句窗口径 (criterion='win1') 落 _win1, 严格同句口径 (criterion='sent', 内部 radius=0) 落 _sent; win_radius 取自 config/panel.yaml 的 network_criteria.win_radius (默认 1), 与 filtering.yaml 中 stage 13 的 cooccurrence_filter.sentence_radius 是互不联动的两个键。win1 与 sent 走 docid 组内文本重扫路径, 复用 entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 原语, 扫描文本经 prepend_title 把标题接为第 0 句参与句级判定, 镜像 stage 13 的 match_in_title 口径; 三判据的节点全集一致 (均为当年幸存银行), 仅边集逐级收紧。就实现细节而言, 同篇 canonical 路径 (criterion='article') 走的是 both-verified 主路径: 对每个 docid 分组内幸存 target_bank 的去重集合逐无序对累加, 单银行文章不产边; 邻接矩阵以稀疏 lil_matrix 累积后转稠密 DataFrame, 且对一篇提及超过十家银行的大-N 文章会打印诊断日志以提示其等权 clique 投影可能主导网络。有效规模只在原始加权图 G 上计算, 不使用路径型指标所需的倒数权重图 G_inv (后者仅供 betweenness、harmonic、closeness、eccentricity 一类"距离越短越近"的度量), 因为结构洞冗余度衡量的是邻居间连边的存在与强度, 与最短路径距离无关。孤立节点在建 G 时被显式加入 (add_node), 保证节点全集完整, 从而 degree==0 的银行能被正确识别并置 NaN, 而不是因不在图中被静默丢失。runner 在面板构造步骤中对同一 df_exploded 依次以 article、win1、sent 三个 criterion 各调用一次 compute_bank_network_centrality, 分别落无后缀、_win1、_sent 三套 33 列, 三次调用彼此独立、加性叠加, 互不改写对方列。win1 与 sent 的句窗判据分轨路径当前不支持 hyperedge_normalize (仅 article 主路径预留该参数且尚未接线), 一旦误传即 raise, 以防三判据轨在无警告下分叉出不同的边权归一口径。

【文献定位】
有效规模的理论根脉是 Burt (2004) 的结构洞框架: 处于结构洞两侧、连接原本不相往来群体的行动者, 因掌握非冗余的信息与控制优势而获益, 有效规模正是量化这一"非冗余触达广度"的核心算子。作为一个建立在共现图上的节点位置度量, 它与 Freeman (1978) 对社会网络中心度的经典厘清一脉相承, 但刻画的不是"居中程度"而是"跨结构洞的信息不重叠度"。由于本项目的共现图是加权的 (边权=共现文章数), 有效规模的加权实现直接承接 Opsahl, Agneessens & Skvoretz (2010) 关于加权网络节点中心度推广的思路, 以及 Barrat, Barthélemy, Pastor-Satorras & Vespignani (2004) 对复杂加权网络架构的刻画。在金融应用层面, 银行间由共现或所有权关系构成的网络位置已被证明具有经济后果: Gao, Ru & Yang (2022) 显示银行所有权网络承载信息角色并影响信贷, Wang, Zhang & Yang (2020) 追踪了中国担保网络在危机与刺激下的演化, Jackson & Pernoud (2021) 综述了金融网络中的系统性风险传导, Yu, Hu & Zhong (2024) 则把网络中心度与信息扩散、资产定价直接关联。就"从文本构造金融网络"这一方法论传统而言, Hoberg & Phillips (2016) 的文本网络产业分类与 Li 等 (2026) 从文本风险披露中还原金融网络连通性, 为以新闻共现刻画银行结构位置提供了外部支撑。结构洞与经纪的社会学谱系还包括 Gould & Fernandez (1989) 对交易网络中中介结构的形式化, 以及 Han, Kim & Nanda (2024) 对机构经纪网络促成流动性供给的金融实证, 二者与有效规模同属"中介/桥接"构念族, 但落点不同 (见下文构念区分)。把有效规模嵌入一个包含度、强度、介数、特征向量、约束、聚类等多种度量的中心度全集, 也回应了 Freeman (1978) 的核心洞见: 没有单一的"中心度"能概括节点在网络中的全部重要性, 不同算子量的是不同的结构角色, 应并置而非相互替代。加权网络的引入使这一多度量策略更贴近真实: Barrat 等 (2004) 与 Opsahl 等 (2010) 均指出, 一旦边带上强度信息, 单纯拓扑度数会遗漏"联系有多强"的维度, 加权有效规模因此比无权版本更能区分"频繁被一起报道"与"偶然被一起报道"的邻居。就中国情境的银行网络证据链而言, Wang 等 (2020) 的担保网络、Gao 等 (2022) 的所有权网络与 Yu 等 (2024) 的中心度—定价关联共同表明, 银行的网络位置并非纯粹描述性标签, 而是承载信息传导与风险外溢的结构变量; Jackson & Pernoud (2021) 的系统性风险综述则从理论上说明为何桥接位置 (低冗余、高有效规模) 在传染与信息扩散中扮演关键角色。Lei, Campbell-Verduyn, Steglich & Wittek (2026, Finance and Space) 用随机行动者导向模型追踪了 2002-2022 年全球银行与非银行机构网络的动态演化, 为本家族以新闻共现刻画银行间网络结构位置随年度变化的构造思路提供了银行网络动态演化视角的外部实证支撑。Klaucke (2025, The North American Journal of Economics and Finance) 用约4.7万篇新闻文本构造银行等金融机构的文本共现溢出测度并与Diebold-Yilmaz计量测度对照,证明新闻共现可直接反映机构间连通性,为本家族以银行新闻共现构造网络的方法论提供直接外部支撑。Wang & Wei (2026, Asia Pacific Journal of Management) 考察创业者跨越结构洞的网络行为如何通过赋能与议价力影响新创企业的商业伦理实践,延伸Burt结构洞框架在企业层面行为后果上的最新实证证据。

【识别策略定位】
在计量识别上, 有效规模主要以两种身份进入本项目的面板回归。第一种身份是银行网络位置的结构性控制变量: 一家银行处在信息不重叠、跨群桥接的位置这一事实, 本身可能同时影响它接触金融科技动向的广度与它被媒体书写的方式, 若不加控制便会与金融科技新闻情感、注意力等主处理变量纠缠, 使系数估计混入网络位置的异质性; 把有效规模纳入回归右端可吸收这一维度, 让主处理变量的估计更接近"给定网络位置后"的净效应。第二种身份是同群暴露 (peer exposure) 与网络溢出构造中的位置权重成分: 有效规模刻画的"桥接了多少非重叠信息面"正是溢出强度的天然调节量, 一家跨越更多结构洞的银行更可能把异质的同业信息聚合、转译并再扩散, 因而在留一同群均值、广义 Bartik 暴露等溢出算子里承担位置权重角色。需要强调, 无论作为控制还是权重, 有效规模所依托的银行∧银行共现网络其节点与边宇宙都继承自 full-only 留篇门控 (2026-06-29): 只有 llm_verified_full 为真的报道才被判为一篇银行金融科技报道并进入 24_herd_decay 的 verified 篇章级宇宙, 网络的年度重建即建立在这一 full-only 留篇集之上, 因此有效规模的宇宙口径与主处理变量的留篇口径严格一致, 不存在网络用一套留篇、情感用另一套留篇的错配。
网络位置进入回归后无法回避 Manski (1993) 的反射问题: 个体行为与其同群平均行为互为因果, 内生效应、外生 (情境) 效应与关联效应难以分离。Bramoullé, Djebbari & Fortin (2009) 证明当网络存在"朋友的朋友并非朋友"这类结构上的非传递性时, 高阶邻居的特征可作为工具从而恢复识别——这正是有效规模、约束度这类结构洞度量之所以承载识别信息的机理: 它们量化的恰是自我网络中冗余与非冗余联系的构成, 而非冗余联系带来的正是识别所需的结构变异。Grieser, Hadlock, LeSage & Zekhnini (2022) 在公司财务政策框架下把这一网络识别思路落到实证, de Paula, Rasul & Souza (2024) 则进一步给出从面板数据反推网络关系本身的识别理论, 二者共同支撑"网络位置可作为识别信息载体"的立场。就经济后果而言, 网络中心度对企业绩效的作用已有跨研究的系统证据: Nezami, Chisam & Palmatier (2025) 的元分析汇总了中心度与企业绩效的关联, Yu, Hu & Zhong (2024) 把网络中心度与信息扩散、资产定价直接联系起来, 说明有效规模这类位置变量并非纯描述性标签而是有经济含义的结构变量。
就本家族三个判据变体而言, 铁律是: 同篇 (无后缀)、±1 句窗 (_win1)、严格同句 (_sent) 三判据各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三者混进同一个 over-identified 的 Hansen J 过度识别检验。三判据回答的是"共现网络的边定义得多严"这一规格稳健性问题, 应以并列自回归、并列规格的方式呈现, 而非塞进同一工具集做联合过度识别; 这一并排口径与本项目三轨文本 (_full/_ctx/_ss)、co-primary 双轨嵌入、政治词权重梯子、词典消融梯度的既定处理完全同构。在具体建模里, 有效规模常与留一同群均值、广义 Bartik 暴露等工具构造并行: 前者刻画"我处在什么位置", 后者刻画"我暴露于什么冲击", 二者在识别上分工而非替代。还须警惕有效规模自身的潜在内生性: 一家银行因创新活跃而被更广泛地跨圈报道, 反过来会推高其有效规模, 故当它进入因果链自变量侧时须辅以滞后、固定效应或外生工具, 而当它仅作为吸收网络异质性的控制变量时相对稳妥。三判据梯子在此处的价值正是稳健性诊断: 若主结论只在同篇最宽松口径下显著、在 _win1 或 _sent 收紧后消失, 便提示结果可能由大-N 榜单文章的机械共现驱动而非实质的紧密同现, 这类诊断必须以三判据并列呈现, 不能用一个联合过度识别检验掩盖。

【与相邻测度的构念区分】
有效规模与家族外若干相邻网络列易混, 需精确区分。相对 bank_degree_cent (原始度中心度, 纯粹数邻居数), 有效规模是"度数扣掉冗余"后的净值, 因此永远不大于度数, 且仅当邻居彼此完全互不相连 (纯结构洞) 时才与度数相等; 度数只回答"认识几家", 有效规模回答"其中有几家承载的是不重复的信息"。相对 bank_strength_cent (加权度/点强度, 邻居边权之和), 强度衡量的是共现联系的总体量而完全不问邻居间是否冗余, 一家与少数几家银行被极高频共同报道的银行强度很高却可能有效规模很低 (邻居高度互连), 二者一个量"联系多强"、一个量"信息多不重叠"。相对 bank_constraint (Burt 约束度) 与由其取倒数得到的 bank_ci (源码 bank_ci=1/constraint), 约束度以自我网络中各联系的比例投入平方项加总衡量"自我网络被少数高冗余联系锁死的总体压力", 随冗余上升而增大, 是一个聚合标量; 有效规模则是"非冗余邻居的绝对个数", 方向与约束度相反且非简单互为倒数 (约束度含比例投入与二阶间接投入的平方结构, ci 只是其代数倒数), 本家族刻意与 constraint/ci 分列, 因量纲、单调方向与退化边界 (约束度 degree<2 置 NaN) 均不同。相对 bank_ego_density (自我网络密度, 邻居对中实际相连比例, 值域落在 0 到 1, 源码 k 不超过 1 置 NaN), 密度是纯比例、不含度数规模信息, 有效规模则把度数规模与非冗余比例合成为一个绝对计数, 二者是"比例"与"规模折算"的分工。相对 bank_avg_nbr_deg (平均邻居度), 后者刻画"我的邻居自己有多少邻居"这一二跳扩散潜力, 与"邻居彼此是否冗余"无关。
相对 Gould-Fernandez 的 gf_* 经纪角色 (按外生节点分组区分协调者、看门人、代表、联络人等具体中介类型), 有效规模不区分被桥接群体的类型, 只回答"我的邻居有多不重叠", 是无类型的自我网络结构洞度量; gf_* 与 Han, Kim & Nanda (2024)、Gould & Fernandez (1989) 的经纪构念要求外生的群组划分, 而有效规模无须任何分组。相对 bank_between_cent 与随机游走式 bank_cfbetween_cent (介数类), 介数是全局最短路径 (或电流流) 意义上的桥接, 度量"多少条最短路径必经过它", 有效规模则是局部自我网络意义上的非冗余, 一个看全网、一个只看一跳邻域; 值得注意 cfbetween 属本项目已知受 BLAS 浮点漂移影响的列, 而有效规模不受此影响 (详见下节)。相对特征向量类度量 (bank_eigen_cent、bank_katz_cent、bank_subgraph_cent), 后三者刻画"邻居本身是否重要"的递归声望或子图参与度, 有效规模则完全不看邻居的全局地位、只看邻居彼此是否冗余, 因此一个高有效规模的银行可以拥有一群本身并不显赫的邻居, 只要这些邻居分处互不相干的信息簇。相对 bank_coreness (k-核层级, 源码缺省 0) 与 bank_is_hub (年内度数前约十分位指示, 跨年不可比), 它们回答"处在网络核心密集区还是边缘"以及"是不是当年度数枢纽", 是密度/规模意义上的位置, 而有效规模回答"桥接了多少非重叠信息", 一家高有效规模的银行未必是度数枢纽 (它可以只连着少数几个彼此隔绝的簇)。相对 bank_closeness_cent 与 bank_eccentricity (距离类, 建在倒数权重图上), 它们量"到全网其它银行平均多近/最远多远", 是可达性视角, 而有效规模只在原始加权图上计算、与最短路径距离无关。相对 net_*_yr 一族网络级年度指标 (密度、模块度、直径、giant 分量占比等), 那是整张年度网络的宏观形状、每年一个标量, 有效规模则是节点级、每家银行一个值。这一系列区分共同说明: 有效规模在本项目三十三个网络指标里占据一个不可被其它列替代的构念槽位——它是唯一以"结构洞非冗余触达广度"为语义、以"度数扣减加权冗余"为算子的自我网络级度量, 与聚合约束、纯密度、纯度数、点强度、全局介数、递归声望、可达距离、角色化经纪、网络级宏观形状均正交, 故独立成族。

【已知局限与稳健性梯子】
第一, 有效规模建立在"每篇文章内共同提及的银行两两成边"的 clique 投影上, 因此提及众多银行的大-N 文章 (年度榜单、批量监管通报) 会一次性贡献 C(N,2) 条等权边, 可能系统性抬高被频繁列入榜单的银行的度数与有效规模, 而这类共现的信息含量往往低于两三家银行被专门并列深度分析的报道; network_spillover.py 对单篇提及超过十家银行的大-N 文章打印诊断日志以示警, 并预留了 hyperedge_normalize (Newman degree-preserving 归一, 每对贡献倒数于邻居数减一) 参数以缓解此偏, 但该参数目前仅在同篇 article 主路径预留、尚未接线到 config 与 runner (win1/sent 分轨路径一旦误传即 raise 以防三判据口径无警告分叉), 生产口径仍是等权加一, 大-N 文章的膨胀属已知且未消解的局限。第二, 有效规模是绝对水平随当年网络规模与稀疏度漂移的量: 其跨年可比性有限, 在含年固定效应的回归中应审慎处理, 语料稀薄的早年更易出现大量孤立点而落 NaN; 缺失语义上须严格区分 degree 为 0 时的 NaN (网络中孤立/缺席) 与"有效规模极小的真实低桥接银行", 下游回归不可把二者混为 0。第三, 网络的节点与边宇宙继承媒体覆盖本身的选择性: 被报道更密集的银行天然进入更多共现、网络更稠密, 这一覆盖偏差与银行的规模、显著度内生相关, 使有效规模无法被解读为纯外生的结构禀赋。第四, win1 与 sent 判据的句级重扫复用与 stage 11/13 同一套否定与短名排除事实源, 以防"涉农行业→农行"一类假阳性污染边集, 但该防线依赖别名词典的完备性, 属工程上可审但非零风险的一环。第五, 确定性上, 有效规模是纯拓扑/加权代数运算, 逐位可复现, 不属于本项目已知受 BLAS 浮点漂移影响的三基名九列 (bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 各自的无后缀/_win1/_sent 变体), 故 golden 复现中不需按那九列特殊排除。第六, 也是最重要的稳健性设计: 本家族提供同篇 (无后缀)、±1 句窗 (_win1)、严格同句 (_sent) 三条判据梯子, 分别对应"算认识"越来越严的三种标准, 三者互为稳健性、不分主次, 各自 just-identified 并排进入分析, 禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀 (_full/_ctx/_ss) 是两个正交空间, 前者变的是"银行∧银行边怎么连", 后者变的是"银行∧金科文本取哪段", 二者亦禁在同一过度识别检验里混用。稳健结论应表现为三判据下有效规模的符号与显著性方向一致, 而在试跑样本 (T 很小) 上 sent 判据可能因边极稀疏而近零方差、大面积 NaN, 属判据收紧下的预期退化而非缺陷, 不应据此判定测度失效。

## VAR: bank_effective_size

【变体差分】
本列是家族 canonical, 对应同篇共现判据 (criterion='article'), 无判据后缀, 是 NETWORK_METRIC_BASES 中 bank_effective_size 基名的现行生产口径。它的边定义最宽松: 只要两家银行在同一篇报道 (同一 docid) 内被共同提及, 无论相隔多远、是否在同一句或相邻句, 都算作一条边, 边权等于当年共同提及该对银行的文章篇数。因此在三个判据变体里, 同篇口径的图边数最多、图最稠密, 由此算出的有效规模在数值上通常最大 (度数基数最高), 也最容易被大-N 榜单文章推高。作为 canonical, 本列是家族对外的默认引用对象: 家族层面的构念定义、方法学、文献定位与识别策略均以本列为锚, _win1 与 _sent 两个变体则是在保持节点全集不变、仅收紧边判据的前提下对本列做规格稳健性检验。取值上, 本列尺度同节点度数, 无量纲, 近似落在 [1, 度数 k] 区间: 当一家银行的所有同篇共现同行彼此完全不再共现时, 有效规模趋近其度数 (纯结构洞位置); 当这些同行彼此高度互相共现时, 有效规模被冗余扣减而趋近下界。缺失语义严格遵循家族约定: 当年度数为 0 (无任何同篇共现邻居) 的银行置 NaN, 表示"网络中孤立/缺席", 与"有效规模极小的真实低桥接银行"区分开; 计算异常时该年全员 NaN。需重申铁律: 本列与 _win1、_sent 各自 just-identified 并排, 互为稳健性、不分主次, 三者禁混进同一 over-identified Hansen J; 同篇判据后缀 (此处为无后缀) 与三轨文本后缀 (_full/_ctx/_ss) 属两个正交概念空间, 判据主体是银行∧银行, 与银行∧金科文本轨互不换算。本列亦是家族内唯一 tier=core 列, 其长文承载家族核心叙事, 是 codebook 家族地图对 F090 的规范入口。就与两个变体列的定量关系而言, 由于同篇边集是 _win1 边集的超集、_win1 边集又是 _sent 边集的超集 (相邻句共现必然同篇, 同句共现必然在 ±1 句窗内), 在其它条件相同的年份, 本列的度数基数逐判据不降, 因而本列有效规模的绝对水平在三判据里通常最高、NaN (孤立点) 占比通常最低。这一单调包含关系是三判据可比性的结构保证, 也是把本列选为 canonical 的技术理由: 最宽松口径给出的是网络位置的"上包络", 变体列在其上做保守收紧, 稳健的结论应在上包络与收紧口径下方向一致。使用者尤需留意本列对大-N 文章的敏感: 一篇同时提及数十家银行的年度榜单或批量监管通报, 在同篇口径下会为这数十家银行两两连边, 机械地抬高它们的度数与有效规模, 而这类共现的信息含量往往低于两三家银行被专门并列分析的深度报道; hyperedge_normalize 归一虽已在源码中预留却尚未接线, 故本列在生产口径下仍承载这一未消解的膨胀风险, 在把本列用作回归自变量前应结合 _win1/_sent 的收紧结果判断结论是否稳健。本列的缺失、异常降级、边权累加与加权有效规模算子均为家族的基准定义, 两个变体列除边判据外的一切口径都以本列为参照系; 因此对本列语义的任何误读都会连带波及整族的解释, 这也是它被单列为 core 深度长文的原因。最后重申判据与文本轨的正交铁律: 本列无判据后缀不等于"无轨", 它是同篇银行∧银行判据这一具体口径的实例, 与银行∧金科的 _full/_ctx/_ss 文本轨在概念上不可换算、在过度识别检验中不可合流。

## VAR: bank_effective_size_sent

【变体差分】
本列是严格同句判据变体 (criterion='sent', 内部 win_radius 被强制为 radius=0), 落 _sent 后缀。它把成边门槛收到最紧: 两家银行必须出现在同一句话之内 (标题经 prepend_title 接为第 0 句参与判定) 才算一条边, 仅仅"同篇但分处不同句"不再成边。相对 canonical 的同篇口径, 严格同句口径丢弃了绝大多数跨句共现, 图边数最少、图最稀疏, 由此每家银行的度数基数被大幅压缩, 有效规模的绝对水平通常在三判据里最低, 孤立点 (度数为 0 → NaN) 也最多; 在语料稀薄的早年或试跑样本 (T 很小) 上, 本列可能大面积退化为 NaN 或近零方差, 属判据收紧下的预期行为, 而非缺陷。其经济含义是"只承认在同一句话里被并列书写的银行才构成真正紧密的信息共现", 是对同篇口径最保守的稳健性对照。除边判据外, 本列的节点全集、边权累加规则 (每篇每对 +1)、加权有效规模算子、degree==0→NaN 的缺失约定, 均与 canonical 完全一致, 唯一变动量是"何为一条边"。铁律照旧: 本列与 canonical、_win1 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三判据混进同一 over-identified Hansen J; 判据后缀 _sent 是银行∧银行同句边的记号, 与银行∧金科文本轨 _ss 的"同句共现"名字虽近但语义正交 (codebook 推断函数刻意剥判据后缀后再匹配, 措辞上也把 bank-bank same-sent edge 与文本轨 same-sent 区分), 二者禁互相换算、禁混同一过度识别检验。

## VAR: bank_effective_size_win1

【变体差分】
本列是句窗判据变体 (criterion='win1', radius=win_radius, 生产默认取 config/panel.yaml 的 network_criteria.win_radius=1), 落 _win1 后缀。它的成边门槛介于同篇与严格同句之间: 两家银行只要出现在相隔不超过 ±1 句的窗口内 (标题为第 0 句) 即算一条边, 因此比严格同句宽松 (容纳相邻句的共现)、比同篇严格 (排除跨越多句的远距离共现)。由此本列的图密度、度数基数与有效规模水平在三判据里居中, 是同篇与同句两端之间的"中庸"稳健性对照点。其构念意图是"把相邻一句内的并列书写也视作紧密共现", 以检验主结论是否只在最宽松的同篇口径下成立、还是在更严的邻句口径下依然稳健。win_radius 是记录性参数, 由 _get_bank_scan_ctx 在进程级单例中读入, 与 stage 13 银行∧金科保留判据的 sentence_radius 是互不联动的不同键; 本列的句级重扫走 docid 组内文本路径, 复用 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 原语, 与 _sent 共享同一套否定/短名排除事实源以防"涉农行业→农行"类假阳性。除边判据 (±1 句窗) 外, 节点全集、每篇每对 +1 的边权、加权有效规模算子与 degree==0→NaN 缺失约定均与 canonical 一致。铁律重申: 本列与 canonical、_sent 各自 just-identified 并排, 互为稳健性、不分主次, 三判据禁混进同一 over-identified Hansen J; 判据后缀 _win1 (银行∧银行 ±1 句边) 与三轨文本后缀 (_full/_ctx/_ss, 银行∧金科文本) 属两个正交空间, 禁互换、禁在同一过度识别检验里合流。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. H., & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Lei, J., Campbell-Verduyn, M., Steglich, C., & Wittek, R. (2026). The evolution of global bank-to-nonbank networks, 2002–2022: a stochastic actor-oriented analysis. Finance and Space. https://doi.org/10.1080/2833115x.2026.2662558
Klaucke, K. (2025). Text Spillover: Measuring connectedness of financial institutions based on news text data. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2024.102307
Wang, Y., & Wei, F. (2026). Agentic, powerful, but unethical: New ventures' ethical practices as the outcome of entrepreneurs' networking behaviors and structural holes. Asia Pacific Journal of Management. https://doi.org/10.1007/s10490-026-10116-x
<!-- rendered-citations:end -->
