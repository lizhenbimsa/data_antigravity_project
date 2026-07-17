---
family_id: F098
columns:
- bank_strength_cent
- bank_strength_cent_sent
- bank_strength_cent_win1
unit: 网络结构指标 (无量纲; 年内最大加权度归一, 取值 [0,1])
formula: "bank_strength_cent{sfx} = s_i / max_j s_j; s_i = Σ_j w_ij (node strength, 加权度), w_ij = 年度银行共现网络边权 (两银行按判据共现的文章对计数, 每篇每对 +1); 判据 sfx ∈ {同篇(无后缀 canonical) / ±1 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (建图 = 同文件 build_adjacency_matrix; runner 步骤 7g 调用三次, 判据×后缀配对守卫)
upstream:
- 40 面板构建期篇章级展开帧 df_exploded (docid × target_bank, full-only 留篇门控后的 verified 宇宙)
- config/panel.yaml::network_criteria (win_radius, 默认 1; 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键)
- core/text/entity_context.py::map_bank_sentence_positions / bank_pairs_within_sentence_window (_win1/_sent 判据原语)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: "10.1016/j.jbankfin.2026.107694"
  type: "journal"
  authors: "Kazinnik, S., Killen, C., Scidá, D., & Wu, J. Y."
  year: 2026
  title: "News and networks: Using financial news coverage to measure bank interconnectedness"
  venue: "Journal of Banking & Finance"
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: "Advance online publication"
- doi: 10.1016/j.jeconom.2025.106130
  type: journal
  authors: Hughes, D. W.
  year: 2026
  title: "A jackknife bias correction for nonlinear network data models with fixed effects"
  venue: Journal of Econometrics
  vol: 253
  pages_or_artno: "106130"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: "79-104"
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: "181-204"
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: "2691-2729"
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
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: "Article 102163"
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: "Article 76"
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: "247-272"
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: "2993-3017"
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: "171-202"
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: "603-629"
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: "2586-2624"
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: "Article 2693"
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: "1423-1465"
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: "139-178"
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
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A.
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: "3747-3752"
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: "440-442"
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
  venue: Review of Economic Studies
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
- doi: "10.1111/abac.12341"
  type: journal
  authors: "Guo, F., Lyu, B., Lyu, X., & Zheng, J."
  year: 2024
  title: "Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum"
  venue: "Abacus"
- doi: "10.1016/j.frl.2024.105780"
  type: journal
  authors: "Wu, Y., & Wang, X."
  year: 2024
  title: "The cross section of information transmission in news media and stock returns"
  venue: "Finance Research Letters"
- doi: "10.1007/s44163-025-00350-5"
  type: journal
  authors: "Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A."
  year: 2025
  title: "Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence"
  venue: "Discover Artificial Intelligence"
- doi: "10.1111/acfi.13091"
  type: journal
  authors: "Wang, L., Hou, W., & Liu, Y."
  year: 2023
  title: "How do co-shareholding networks affect negative media coverage? Evidence from China"
  venue: "Accounting & Finance"
new_dois:
- "10.1016/j.jbankfin.2026.107694"
- "10.1111/abac.12341"
- "10.1016/j.frl.2024.105780"
- "10.1007/s44163-025-00350-5"
- "10.1111/acfi.13091"
---

## CORE

该文用金融新闻报道中银行共同提及构建文本网络并以中心度测度银行间关联度,与本家族用媒体共现网络刻画银行强度中心度的构念高度同源。

【构念与来源】
本家族测量的构念是银行在年度媒体共现网络中的加权连接强度, 即节点强度中心度 (node strength centrality)。其底层直觉是: 当两家银行反复被同一批新闻报道共同提及时, 二者在媒体信息空间中形成一条可量化的联系通道 — 这种通道既可能反映真实的业务与同业关联 (同一监管事件、同一银团、同类金融科技合作), 也可能反映媒体叙事把两家银行归入同一认知类别 (如同为股份制银行、同陷某类风险事件), 无论哪种机制, 通道的存在与强度都刻画了信息、情绪与关注度在银行间扩散的潜在路径。Freeman (1978) 对中心度概念做了奠基性澄清, 把节点重要性区分为度 (直接连接数)、中介 (桥梁地位)、接近 (到全网的距离) 三种互不可替代的语义; 在无权图中, 度中心度只回答一家银行认识多少邻居。但媒体共现网络天然是加权的: 两家银行一年内共现一篇与共现上百篇, 联系强度不可同日而语。Barrat et al. (2004) 系统论证了加权网络的结构性质不能由无权拓扑还原, 并把节点强度 (与该节点相连全部边权之和) 确立为加权网络的一阶节点统计量; Opsahl et al. (2010) 进一步把度与强度统一进一个可调参数族, 指出强度是加权度中心度在纯权重端的极限情形。本家族的 bank_strength_cent 即取 Opsahl 意义上的 node strength 构念: 对每家银行, 把它在当年共现网络中所有边的权重求和, 得到该银行经由媒体共同报道积累的总连接强度, 再做年内最大值归一 (细节与口径警示见方法学段)。数据来源上, 网络的原材料是本项目新闻处理流水线的篇章级展开帧: 经 stage 13 银行与金融科技词邻近共现硬过滤、stage 21 三家 LLM 投票留篇门控 (full-only 口径, 2026-06-29 起只看 llm_verified_full 判定一篇是否为银行金融科技报道) 之后幸存的文章宇宙, 按 docid 与目标银行展开为文章银行对。也就是说, 本网络不是全体银行新闻的共现网, 而是银行金融科技语料上的共现网 — 节点是当年至少出现在一篇幸存报道中的目标银行, 边是判据意义下的共同被提及关系。这一构造在方法论上与 Hoberg and Phillips (2016) 用文本相似度内生刻画产品市场网络一脉相承: 关系不由外生名录给定, 而由文本证据逐年重估; 也与 Li et al. (2026) 从风险披露文本中恢复金融网络结构、Wang et al. (2020) 从担保关系数据刻画中国银行企业网络演化的思路同属从非结构化或半结构化数据中构建金融关联的谱系。

【方法学与计算】
计算在 pipeline/panel/network_spillover.py 的 compute_bank_network_centrality 中完成, 属 runner 步骤 7g, 是 NETWORK_METRIC_BASES 所列三十三个结构指标基名之一 (SSOT 元组, stata_export 标签块与 gate 测试直接 import 复用防漂移)。第一步由 build_adjacency_matrix 按年构建对称邻接矩阵: 取当年篇章级展开帧, 节点全集为该年出现过的全部目标银行 (排序后编号, 含孤立节点); canonical 同篇判据下, 按 docid 分组, 同一篇文章内幸存的银行集合中每个无序对的边权加一 — 每篇文章对每对银行恰贡献一次, 这等价于把文章乘银行的二部隶属网络做 clique 投影到银行单模网络, 边权即共现文章计数。Borgatti and Everett (1997) 与 Faust (1997) 对二模数据的单模投影及其中心度语义有系统讨论, 提醒投影会丢失隶属结构信息; 源码对这一点有显式披露: 一篇提及 N 家银行的榜单或批量监管通报会贡献 N 取 2 条等权边, 大 N 文章可凭组合爆炸主导网络。producer 预留了 Newman 式 1/(N-1) 度守恒超边归一参数 hyperedge_normalize, 但按 NB-01 披露该参数尚未接线到 config 与 runner, 生产路径恒为等权加一, 且判据分轨路径遇 True 会直接 raise 以防三判据轨无警告分叉口径。第二步在 networkx 无向加权图 G 上取 strength 等于 G.degree(weight='weight'), 即每个节点相连边权之和; 随后除以当年全网最大强度做 max-normalize, 全零时分母置一防除零, 未入图银行取零。这里有两条必须逐字转述的源码口径警示 (network-metrics-audit 2026-06-13, P2-7): 其一, Opsahl et al. (2010) 只定义了 node strength 为边权和, 并不含按网络内最大值归一这一步 — max-normalize 是本项目的 ad-hoc 实现细节, 面板导出标签中的 Opsahl 指涉仅限 strength 构念本身; 其二, 该归一是年相对度量, 每年加权度最大的银行恒等于一, 故数值水平跨年不可比, 且除以年份特定标量是乘性重标度, 无法被含年固定效应回归中的加性年效应吸收 — 若要把本列升格为回归右手边变量, 须先改为结构性归一 (如对数强度、全样本归一或组内标准化); 当前生产消费面仅 Table 1 描述统计, 无任何 Stata 模板把它放上回归右侧。判据维度上, 家族三列对应三种银行与银行共现判据: 无后缀列为同篇判据 (现行 canonical); _win1 列要求两银行出现在相距不超过 win_radius 句的句子内 (win_radius 取 config/panel.yaml 的 network_criteria.win_radius, 默认一, 与 stage 13 银行金融科技过滤的 filtering.yaml 中 cooccurrence_filter.sentence_radius 是两个不同键, 互不联动); _sent 列要求严格同句。后两种判据在 docid 组内做文本级重扫: 判据原语为 core/text/entity_context.py 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 扫描文本为标题加正文的 prepend_title 拼接 (标题记为第零句, 镜像 stage 13 的 match_in_title 口径), 银行识别与 stage 11 及 13 共用同一否定词与短名排除事实源 (禁裸 Aho-Corasick 匹配, 防涉农行业误命中农行一类假阳性), 仅有至少两家幸存银行的文章组可能成边, 非幸存银行不进入原语入参因而不可能产生幽灵边。三判据的节点全集与同篇判据完全一致 (同为该年幸存银行), 仅边集依次收严, 因此同一银行年在三列间的取值差异纯由边集判据驱动。runner 对三判据各调用一次 compute_bank_network_centrality, 函数入口设 criterion 与 suffix 配对守卫 (同篇对空后缀、句窗对 _win1、同句对 _sent, 错配即 raise), 从机制上排除判据算错落错列的静默口径污染。上游数据链条须完整交代以界定网络的样本框: 原始语料经 stage 00 预处理与媒体类型过滤、stage 11 银行主体识别 (否定与短名排除)、stage 12 金融科技词识别、stage 13 银行与金融科技词邻近共现硬过滤丢行、stage 14 三轨文本物化、stage 21 三家大模型投票留篇门控, 只有 full 轨判定为银行金融科技报道的文章才进入面板构建期的篇章级展开帧 — 因此本家族网络中每条边的两端都以同一篇被验证的金融科技报道为证据载体, 边权计数的分母宇宙与面板 n_articles 的 full-only 口径一致。数值性质上, strength 是纯求和运算, 无谱分解无随机数, 属确定性 golden-safe 指标, 不在本项目九个 BLAS 浮点漂移网络列 (三个基名乘三判据后缀) 的排除清单内, 跨次重建可逐位复现。

【文献定位】
本测度在三支文献的交汇处。第一支是加权网络中心度的方法文献: Freeman (1978) 确立中心度三分法, Bonacich (1987) 提出把邻居重要性递归计入的幂中心度族并厘清正负参数下中心度与权力的分野, Barrat et al. (2004) 与 Opsahl et al. (2010) 把度推广到加权情形, Boldi and Vigna (2014) 则用公理化方法检验各中心度是否满足规模单调与密度敏感等基本性质 — 强度中心度作为最直接的一阶加权统计量, 是这一谱系中解释成本最低、对测量误差最不敏感的成员, 也因此常被用作更复杂谱型指标 (特征向量、Katz) 的稳健性参照。第二支是金融网络与系统性风险文献: Jackson and Pernoud (2021) 综述了金融网络中风险传染对网络位置的依赖, 指出高连接强度节点既可能分散风险也可能放大传染, 方向取决于冲击规模与网络密度的相互作用; Sadeghi and Feinstein (2024) 提出对传染中心度做统计显著性检验的框架, 提醒任何中心度点估计都伴随网络抽样误差; Yu et al. (2024) 与 Xu and Zhao (2024) 分别给出网络中心度经由信息扩散影响资产定价及节点中心度改善金融网络中价格预测的近期证据; Nezami et al. (2025) 对网络中心度与企业绩效关系做元分析, 发现中心度绩效关联的方向与强度高度依赖网络类型与中心度指标选择 — 这正是本项目把三十三个结构指标并排物化而非只挑单一指标的文献理由。第三支是媒体与银行的中国语境文献: Fang et al. (2024) 证明媒体情绪影响中国银行的存款稳定性与系统性风险, Cookson et al. (2026) 记录了社交媒体在银行挤兑中的催化角色, Khan et al. (2024) 用机器学习刻画硅谷银行事件经社交媒体向银行股指数的多米诺传导, Gao et al. (2022) 则展示了股权网络在中国银行信贷决策中的信息角色。这些研究共同支撑本家族的前提: 银行间的媒体共同报道不是噪声, 而是信息与情绪传导的可测通道, 其强度分布本身就是有经济含义的网络暴露特征。近期文献进一步充实了这一论证: Guo, Lyu, Lyu, & Zheng (2024, Abacus) 证明基于媒体与社交网络的公司中心度与股价同步性显著负相关, 为本家族用媒体共现网络中心度刻画银行信息暴露的构念提供了同题材的近期实证参照; Wu & Wang (2024, Finance Research Letters) 用新闻媒体信息传导的截面证据说明媒体关注与共现结构如何影响资产回报, 呼应本家族把媒体共现网络位置作为信息传导通道的识别定位。Alamsyah et al. (2025, Discover Artificial Intelligence) 用新闻共现网络刻画印尼上市公司间的媒体关联结构并连接情感与股价, 与本家族用媒体共现网络度量银行强度中心度的构念高度同源; Wang, Hou, & Liu (2023, Accounting & Finance) 证明中国企业在共同持股网络中的度中心度与结构洞位置显著影响其负面媒体报道的数量与严重程度, 为本家族网络位置调节效应的解读提供中国语境近期实证参照。

【识别策略定位】
在本项目的计量架构中, bank_strength_cent 族的角色是网络位置控制变量与异质性调节变量, 不是处理变量也不是工具变量。各论文的处理变量是文章级情感与属性测度聚合 (如 llm_vote_tone_full), 结果变量是外部财务指标; 强度中心度进入分析的方式是刻画哪类银行更暴露于媒体网络中心位置, 从而支持调节效应检验 (中心银行的语调冲击是否传导更强) 与溢出机制叙事 (industry_neg_shock 与 emb_peer_tone 等同伴暴露测度的网络结构背景)。把网络位置放进回归须直面两类身份识别难题: 其一是 Manski (1993) 的反射问题 — 银行间行为相互影响时, 内生同伴效应、外生特征效应与相关效应观测等价; Bramoullé et al. (2009) 证明网络结构本身 (排除性的二度邻居) 可提供识别杠杆, Grieser et al. (2022) 在公司金融政策场景展示了网络计量的空间计量实现, de Paula et al. (2024) 更进一步从面板数据中同时恢复未知网络与同伴效应。其二是网络本身的内生性与测量误差 — 媒体共现由编辑选择生成, 与银行不可观测特征相关; Hughes (2026) 给出非线性网络模型固定效应估计的刀切偏差修正, 提示带网络回归元的固定效应估计存在附带参数偏误。本项目的务实立场是: 强度中心度当前仅进入描述统计与机制叙事, 升格为回归右手边前须完成上文所述归一改造, 并按同伴效应识别文献的要求配置工具或结构假设; IV 扩展模块 (leave-one-out 同组均值、广义 Bartik、媒体来源暴露) 为这一升格预留了工具变量货架。进一步说, 本项目同伴暴露测度族与本列在识别架构中的分工须写明: industry_neg_shock 三轨族是行业层面负面冲击暴露 (分子分母严格逐轨), emb_peer_tone 与 bank_cogn_mean 族是以嵌入相似度或词频余弦为权重矩阵的同伴语调加权平均 — 这些 W 轨暴露测度回答的是别家银行的语调经何种关联通道传到本行, 是回归右手边的暴露变量; 而强度中心度只回答本行在共现网络中的位置有多中心, 不携带任何语调内容, 是位置调节变量, 二者在机制检验中互补而非替代, 且各自的权重来源 (嵌入相似度对文本余弦对共现计数) 互不派生, 不存在一列由另一列线性变换可得的冗余关系。同伴效应文献近年的进展亦为升格路径提供了操作模板: Bramoullé et al. (2020) 综述了网络同伴效应识别的完整工具箱, 明确了排除性网络结构、组规模变异与面板时序三类识别杠杆的适用边界; Boucher et al. (2024) 给出同伴效应的一般理论框架, 把线性均值模型与其非线性推广统一在同一偏好基础上, 提示线性设定本身是可检验假设而非免费午餐; Leary and Roberts (2014) 是公司金融同伴效应用特质冲击作工具的经典先例。若以共现网络定义同组, leave-one-out 均值工具的有效性依赖组内排除约束 (同组他行的冲击不得经网络外通道直接影响本行结果), 广义 Bartik 类工具 (Goldsmith-Pinkham et al. 2020; Borusyak et al. 2025) 则把识别负担转移到基期份额或冲击序列的外生性上, 二者的可信度论证责任不同, 应在论文正文按所选路线逐项交代。无论哪条路线, 强度中心度作为网络位置的一阶汇总统计量都是刻画暴露异质性的首选调节维度: 相对谱型指标它解释成本低、不依赖幂迭代收敛细节、对断连图天然稳健, 审稿沟通中不需要额外的数值方法附录。

【与相邻测度的构念区分】
同家族三十三个网络指标间的构念边界须写清。与 bank_degree_cent 的区别是加权与否: 度中心度用 networkx 的 degree_centrality, 只数不同邻居个数并按节点数减一归一, 回答连接广度; 强度中心度把每条边按共现文章数加权求和, 回答连接总量 — 一家只与四大行各共现百篇的城商行, 度很低而强度可以很高, 两列分歧本身携带集中对分散连接模式的信息。与 bank_eigen_cent 及 bank_katz_cent 的区别是递归性: 特征向量与 Katz 中心度按 Bonacich (1987) 思想把邻居自身的重要性递归计入, 强度只做一阶求和, 不区分邻居质量; 谱型指标依赖连通分量结构且有幂迭代数值细节 (本项目按分量分别计算并对微小分量置缺失), 强度对断连图天然稳健。与 bank_between_cent 及 bank_harmonic_cent 的区别是路径语义: 中介与调和中心度在倒数权重图上度量桥梁与可达性, 强度不涉及任何路径概念。与 bank_clustering 及 bank_constraint 的区别是局部结构: 聚类系数 (Watts and Strogatz 1998) 与 Burt 约束度量邻居间的闭合与结构洞, 强度对邻居间是否相连完全无感。与网络级列 net_degree_gini_yr 的区别有一处源码显式警示: 该基尼系数刻意用无权度数刻画连接数不平等, 不是加权强度分布的不平等, 两者口径不同勿混读。与 n_articles 及关注度类曝光测度的区别是关系性: 一家银行可以被海量单独报道而极少与同业共同出现, 此时曝光量高而强度低; 强度捕捉的是媒体叙事中的关系性嵌入而非报道数量本身, 两者在大银行样本中高度相关但构念上可分, 且强度的证据载体是文章内的银行对而非文章计数, 单篇独家深度报道对 n_articles 与强度的贡献方向可以完全相反。与 W 轨同伴暴露列 (emb_peer_tone 族、bank_cogn_mean 族) 的区别是内容负载: 那些列把邻居的语调按权重加权平均, 数值随邻居情感变化而变化; 强度中心度只由网络结构决定, 邻居的语调再极端也不改变本列取值, 因此把强度当机制变量解读语调传导是构念错置, 正确用法是以强度划分暴露强弱的子样本或与暴露变量交乘。最后, 判据后缀与三轨文本后缀是两个正交概念空间: _win1 与 _sent 是银行与银行共现判据 (本家族维度), _full、_ctx 与 _ss 是银行与金融科技的三轨文本口径 (情感与属性测度维度), 判据列不存在三轨孪生, 情感列也不存在判据孪生, 任何把二者混同的读法都是口径错误。

【已知局限与稳健性梯子】
第一, 归一口径局限: 年内最大值归一使数值只有年内相对序数含义, 跨年水平比较无意义, 且乘性年标量不可被加性年固定效应吸收 — 这是源码审计留下的最重要消费警示, codebook 使用者引用本列做任何跨年陈述前必须复述。第二, clique 投影膨胀: 等权投影下大 N 文章贡献平方级边权, Cimini et al. (2022) 对二部网络投影提出的元验证框架说明未经零模型校准的投影权重可能高估真实关联; 度守恒超边归一是已预留未接线的对照臂, 真接线须改值重生 golden。第三, 媒体选择内生性: 共现由报道决定, 报道由新闻价值决定, 高强度银行几乎必然是大银行与风险事件银行的混合体, 任何解释都须与规模和事件暴露控制并读。第四, 语料窗口: 网络建立在银行金融科技过滤后的语料上, 强度反映的是金融科技议题内的共现强度而非全议题媒体网络; 开发环境仅两年面板, 网络指标在生产十九年语料上才有完整跨期变异, 且大样本共现网几乎必然断连, 强度对断连的稳健性 (孤立节点取零而非缺失) 在解释缺失模式时须与谱型指标的分量置缺口径对照理解。第五, 判据变体的文本依赖: 句窗与同句两档依赖切句器行为与标题拼接约定, 快讯体与长篇深度报道的句长分布差异会让判据收紧的力度在文体间不均匀, 跨媒体来源比较时应意识到这层测量异质性; 同时两档变体的重扫路径遇 docid 或正文列缺失时按源码约定退化为该年判据邻接全零 (节点保留、无边) 并落警告日志, 消费端见到变体列整年为零而 canonical 非零时应首先排查这一退化而非解读为真实网络消失。稳健性梯子方面, 本家族的判据梯子 (同篇、±1 句窗、严格同句) 构成从宽到严的三档构造判据敏感性检验, 三列互为稳健性、不分主次, 各自 just-identified 并排进入各自的回归设定, 铁律禁止把多判据列混进同一 over-identified Hansen J 检验 — 该口径与三轨文本、co-primary 双轨嵌入、词典消融与政治词权重梯子的并排原则完全同构; 判据梯子属规格稳健性并排, 不设跨判据 FWER 模板 (跨模型 rwolf 先例仅覆盖同构念替代 headline 测量)。此外, 强度与度、特征向量等相邻指标的并排本身构成指标选择敏感性检验, 呼应 Nezami et al. (2025) 元分析中中心度结论对指标选择敏感的告诫; 若未来把强度升格为回归元, 除归一改造外还应参照 Sadeghi and Feinstein (2024) 的思路对中心度排名做抽样不确定性评估, 并以对数强度与组内标准化两种结构性归一互为对照, 使梯子从判据维度延伸到函数形式维度。第六, 梯子间正交不交叉是刻意的架构决策: 判据维度不与三轨文本、词典消融、政治词权重、per-model 等其它梯子做笛卡尔积物化 (否则列数组合爆炸且交叉格大多无独立构念含义), 消费端若确需交叉稳健性, 应在回归设计层面把相关规格逐一并排报告, 而不是要求流水线生成交叉列; 这一防线与规则消融梯度不与政治词权重交叉的先例同构。第七, 开发环境退化须预先声明: 本机两年开发面板上网络规模与跨期变异都远小于生产十九年语料, 判据收紧后变体列在小语料上可能大面积为零, 这属预期退化而非缺陷, 任何基于开发面板的强度分布描述都不可外推到生产语料。

## VAR: bank_strength_cent

【变体差分】
本列是家族 canonical, tier 为 core, 采用同篇共现判据 (源码判据枚举中的 article, 落列无后缀)。精确语义: 对每个面板年, 在当年幸存文章的篇章级展开帧上按 docid 分组, 同一篇文章内出现的全部目标银行两两组成无序对, 每对每篇边权加一, 汇总为对称加权邻接矩阵; 银行 i 的原始强度等于其所有边权之和 (networkx 加权度), 再除以当年全网最大强度得到本列取值, 落在零到一闭区间, 当年最大强度银行恒为一, 无任何共现边的孤立银行为零。同篇判据的含义是: 只要两家银行出现在同一篇幸存报道的任意位置 (标题或正文任意段落), 即计一次共现, 不要求句子层面邻近 — 这是三判据中最宽的口径, 边集是 _win1 与 _sent 的超集, 因此本列是三列中取值最稠密、对文本切句细节最不敏感的一档, 被选为 canonical 既因它是项目历史现行口径, 也因它不依赖切句器与句窗参数, 构造自由度最小。工程细节上有两点与变体列不同: 其一, 本列走 build_adjacency_matrix 的 docid 主路径, 不做文本重扫, 计算成本最低; 当输入帧缺 docid 列时存在兼容降级路径 (退回 co_mentioned_banks 逐行双向计数, 伴 loud WARNING, 含单双计数混合与幽灵边风险), 该降级仅为旧 schema 与合成测试帧兜底, 生产帧恒有 docid 不触发。其二, 预留的超边归一参数只在本判据主路径有实现 (变体路径遇 True 直接 raise), 但生产未接线, 本列恒为等权计数口径。边界情形的取值约定须逐条写明: 该年出现但与任何其他银行无共现边的孤立银行, 强度和为零, 归一后取零 (是真实零而非缺失, 与特征向量中心度对微小分量置缺失的约定不同, 两列缺失模式不可互推); 当年全网最大强度为零 (理论上仅在全年无任何边时出现) 时分母置一防除零, 全体银行落零; 银行列表在建图前排序编号, 邻接矩阵严格对称, 保证跨次运行的图遍历顺序确定。同篇判据下源码另有大 N 文章诊断日志: 单篇提及超过十家银行的文章会被计数并记录最大提及数, 提示等权 clique 投影下这类榜单文章可能主导当年网络 — 解读本列的年间跳变时应先查该日志排除单篇批量通报驱动的伪变异。解释口径上, 本列的年内序数含义清晰: 取值靠近一的银行是当年金融科技媒体叙事中共现联系最密集的枢纽 (典型为频繁与同业并列报道的大型银行), 取值靠近零的银行处在叙事边缘; 但任何跨年的水平陈述 (如某银行强度从某值升到某值) 都是口径错误, 合法的跨年比较只能基于年内排名或另行标准化。消费口径警示随家族: 年内 max-normalize 使本列跨年不可比, 现仅 Table 1 描述统计消费, 无 Stata 模板把它放上回归右侧; 升格为回归元前须改结构性归一并处理 Manski (1993) 与 Bramoullé et al. (2009) 意义上的同伴效应识别。本列与 _win1、_sent 两变体互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 本列数值确定性良好 (纯求和), 不属 BLAS 浮点漂移排除列。与两变体的失败模式差异还须写明: 本列走 docid 集合路径不依赖切句, 对正文列缺失免疫; 变体列的文本重扫退化 (整年判据邻接全零伴警告日志) 不会波及本列, 故本列非零而变体全零的组合是排查变体退化的诊断信号, 反向组合 (本列为零而变体非零) 在逻辑上不可能出现, 因变体边集恒为本列边集的子集。

## VAR: bank_strength_cent_sent

【变体差分】
本列是严格同句判据变体 (源码判据枚举中的 sent, 后缀 _sent), 三档判据梯子中最严的一档。与 canonical 的唯一差分在边集构造: 两家银行只有在同一个句子内同时被识别到才计一次共现 (句窗半径取零), 实现上不走 docid 集合路径, 而是对每个至少含两家幸存银行的文章组做文本级重扫 — 用 map_bank_sentence_positions 在标题加正文的 prepend_title 拼接文本上逐句定位各银行 (标题记为第零句, 镜像 stage 13 的 match_in_title 口径), 银行识别复用与 stage 11 及 13 相同的否定词与短名排除事实源 (禁裸自动机匹配, 防涉农行业误命中农行一类假阳性), 再由 bank_pairs_within_sentence_window 以半径零枚举同句银行对, 每篇每对加一, 与 canonical 同权。节点全集与 canonical 完全一致 (该年全部幸存目标银行), 仅边集是 canonical 的子集且不超过 _win1 — 因此本列相对 canonical 的取值收缩幅度, 度量了同篇共现中有多少联系经不起句子级邻近的检验: 榜单式罗列与批量通报在同句判据下大量成边 (同句逗号并列), 而分散在不同段落的弱关联被剔除。构念上, 同句共现最接近媒体明确把两家银行放进同一命题陈述的强关联语义, 代价是对切句质量与银行短名识别最敏感, 且在句子较短的快讯语料上可能系统性偏向并列句式。本列与无后缀 canonical 及 _win1 互为稳健性、不分主次, 三判据各自 just-identified 并排, 铁律禁混同一 over-identified Hansen J; 判据后缀与三轨文本后缀 (_full、_ctx、_ss) 是正交概念空间, 本列不存在三轨孪生。年内 max-normalize 的归一分母按本列自身判据的年内最大强度取, 与 canonical 的分母银行可能不同, 故两列比值不构成边集保留率的直接估计, 比较应在排序或标准化后进行。

## VAR: bank_strength_cent_win1

【变体差分】
本列是句窗判据变体 (源码判据枚举中的 win1, 后缀 _win1), 判据梯子的中间档。与 canonical 的差分同样只在边集: 两家银行须出现在相距不超过 win_radius 句的句子内才计一次共现, win_radius 读取 config/panel.yaml 的 network_criteria.win_radius, 默认为一, 即允许相邻句共现 — 注意该键与 stage 13 银行金融科技共现硬过滤所用的 filtering.yaml 中 cooccurrence_filter.sentence_radius 是两个互不联动的不同配置键, 前者管银行与银行的网络构造判据, 后者管银行与金融科技词的留篇过滤, 改一处不影响另一处。实现路径与 _sent 完全同源: docid 组内 prepend_title 文本重扫 (标题为第零句), 同一套否定与短名排除防线, 同一个句对枚举原语, 仅句窗半径参数不同 (本列取配置值, _sent 强制取零), 因此本列边集介于 canonical 与 _sent 之间, 构成三档单调收严序列的中项。构念上, ±1 句窗对应语篇分析中跨句指代与承接的典型距离: 上句点名甲银行、下句以同样此类等指代引出乙银行的行文, 在同句判据下漏计而在句窗判据下被捕获, 故本列比 _sent 更能容忍新闻写作的分句习惯, 又比同篇判据显著过滤掉纯粹版面并置的弱联系。选择本列作对照可回答的问题是: 主结论对共现判据从文档级收紧到语篇邻近级是否稳健。口径铁律与 _sent 列一致: 本列与无后缀 canonical、_sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀正交, 无三轨孪生; 年内 max-normalize 分母按本列自身年内最大强度取, 跨年与跨判据的水平比较均须先标准化。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Kazinnik, S., Killen, C., Scidá, D., & Wu, J. Y. (2026). News and networks: Using financial news coverage to measure bank interconnectedness. Journal of Banking & Finance. https://doi.org/10.1016/j.jbankfin.2026.107694
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, Article 102163. https://doi.org/10.1016/j.najef.2024.102163
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), Article 76. https://doi.org/10.1038/s42005-022-00856-9
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, Article 2693. https://doi.org/10.1038/s41467-020-16535-8
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Guo, F., Lyu, B., Lyu, X., & Zheng, J. (2024). Social Media Networks and Stock Price Synchronicity: Evidence from a Chinese Stock Forum. Abacus. https://doi.org/10.1111/abac.12341
Wu, Y., & Wang, X. (2024). The cross section of information transmission in news media and stock returns. Finance Research Letters. https://doi.org/10.1016/j.frl.2024.105780
Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A. (2025). Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence. Discover Artificial Intelligence. https://doi.org/10.1007/s44163-025-00350-5
Wang, L., Hou, W., & Liu, Y. (2023). How do co-shareholding networks affect negative media coverage? Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13091
<!-- rendered-citations:end -->
