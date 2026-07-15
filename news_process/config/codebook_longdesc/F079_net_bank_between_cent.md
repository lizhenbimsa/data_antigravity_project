---
family_id: F079
columns:
- bank_between_cent
- bank_between_cent_sent
- bank_between_cent_win1
unit: 介数中心度 (无量纲, networkx 默认归一化 ∈ [0,1])
formula: "bank_between_cent = 年度银行共现网络倒数权重图 G_inv (edge_weight = 1/共现篇数) 上的 Freeman 最短路径介数中心度 nx.betweenness_centrality(G_inv, weight='weight') (归一化); 判据变体后缀 {同篇 article 无后缀 / ±win_radius 句窗 _win1 / 严格同句 _sent} 仅收紧银行∧银行邻接边集, 节点全集在三判据下恒等"
producer: pipeline\panel\network_spillover.py::compute_bank_network_centrality (runner 步骤 7g / 7g_win1 / 7g_sent); 消费方 papers\_common\derivative_replication.py (brokerage_network .do 模板占位 CENTRALITY_BTW / PRIMARY_CENT / MEDIATOR_CENT)
upstream:
- 24_herd_decay.parquet (df_exploded: 篇章级 target_bank + docid + year + 内容 + 标题; 网络邻接构造的唯一文本/共现输入, 已过 full-only 留篇门控的验证集)
- 40_panel_yearly.parquet (bank-year 面板骨架; 33 指标按 (bank, year) 键 merge 回填)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1080/1540496x.2025.2562336"
  type: "journal"
  authors: "Xiang, Y., & Borjigin, S."
  year: 2025
  title: "Analyst Network: Implications for Systemic Risk of Non-Financial Firms in China"
  venue: "Emerging Markets Finance and Trade"
- doi: "10.1111/1467-8551.12849"
  type: "journal"
  authors: "Chen, S., Cumming, D., Liu, X., Ma, H., & Yan, C."
  year: 2024
  title: "Alumni Network Centrality and Competitive Aggressiveness"
  venue: "British Journal of Management"
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
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, Á., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: 2691-2729
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
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
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
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
  venue: STACS 2005 (Lecture Notes in Computer Science)
  vol: 3404
  pages_or_artno: 533-544
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
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: "10.1287/mnsc.2023.4891"
  type: "journal"
  authors: "Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F."
  year: 2024
  title: "Analyst Coverage Networks and Corporate Financial Policies"
  venue: "Management Science"
- doi: "10.1007/s40822-026-00371-0"
  title: "Contagion and systemic risk in the European banking sector: implications for sustainable regulation and financial system resilience"
  authors: "Zoricakova, J., Filickova, N., & Kocisova, K."
  year: 2026
  venue: "Eurasian Economic Review"
  type: "journal"
- doi: "10.1007/s44163-025-00350-5"
  title: "Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence"
  authors: "Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S. B., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A."
  year: 2025
  venue: "Discover Artificial Intelligence"
  type: "journal"
new_dois:
- "10.1080/1540496x.2025.2562336"
- "10.1111/1467-8551.12849"
- "10.1287/mnsc.2023.4891"
- "10.1007/s40822-026-00371-0"
- "10.1007/s44163-025-00350-5"
---

## CORE

该文用中国上市公司分析师网络中心度衡量企业在信息网络中的居中地位, 发现居中企业系统性风险更低, 机制为信息透明度与公司治理提升, 与本家族用媒体共现网络介数中心度刻画银行结构位置的思路高度平行。 该文用高管校友网络的中心度衡量企业在人际关系网络中的结构位置, 并考察其对企业竞争行为的影响, 为网络结构位置度量 (含介数类中心度) 应用于企业层面结果变量提供了另一实证范式。

【构念与来源】
本家族度量的是介数中心度 (betweenness centrality) —— 一家银行在年度新闻共现网络中占据"桥梁 / 中介"位置的程度。构念源头是 Freeman (1978) 对社会网络中心度的经典厘清: 介数中心度衡量一个节点落在其他所有节点对之间最短路径上的相对频次, 数值越高, 说明信息或资源在网络里流转时越是必须途经该节点, 它越是叙事结构中的"咽喉"或"守门人"。在本项目里, 节点是银行, 边是"两家银行在同一批新闻报道里被共同提及"这一媒体共现关系。因此 bank_between_cent 捕捉的既不是银行的资产规模也不是市场份额, 而是它在媒体话语结构中的经纪地位: 当两簇本来不直接同框的银行, 要靠某家银行才被叙事连在一起时, 这家银行的介数值就高; 反过来, 一家银行即便被频繁报道, 只要它总与同一批银行扎堆出现、从不充当跨群的连接点, 其介数也可以很低。这一"居中即有信息优势"的直觉, 与结构洞理论强调的跨群桥接收益、以及 Grieser 等 (2022) 在公司财务政策网络效应中论证的"中介节点会放大同群溢出"是一脉相承的; 而把银行系统当作一张互联网络来理解风险与信息传导, 正是 Jackson 与 Pernoud (2021) 系统性风险综述、以及 Fang 等 (2024) 关于媒体情绪经由网络影响银行系统性风险与存款稳定性的研究所奠定的分析范式。

数据来源是篇章级的验证后新闻帧 (上游 24_herd_decay.parquet 提供的 df_exploded), 按年切片。这一篇章帧已经过 full-only 留篇门控 (2026-06-29 口径): 一篇报道是否算作"一篇银行金科报道"只看 llm_verified_full 是否为真, ctx / ss 轨降为 conditional-on-full 的稳健性测度。因此喂给共现网络的文章宇宙, 就是 full 轨留篇集, 网络的节点与边都建立在这一验证幸存集之上, 而非未过滤的原始语料。以新闻文本反推出银行间的结构关系, 方法论上承袭 Hoberg 与 Phillips (2016) 用文本相似度构造产业网络的思路, 也呼应 Li 等 (2026) 从文本风险披露里抽取金融网络结构与连通性的近期工作 —— 二者共同确立了"以文本共现为边、以实体为节点"这一文本网络构造范式的合法性。

值得强调的是, 网络在每一年独立重估: 每个年度切片各自建图、各自算介数, 因此 bank_between_cent 是一个随时间变化的结构位置度量, 能捕捉某家银行在特定年份因某类金融科技议题 (如某年监管风暴、某轮联合授信通报) 而临时跃升为叙事枢纽的动态, 也允许同一家银行的桥接地位在不同年份此消彼长。构边所用的 target_bank 是经银行别名字典 (get_target_aliases) 归一后的规范银行名, 别名解析与否定 / 短名排除防线与上游 stage 11 / 13 共用同一事实源, 从而把"农业银行 / 农行"归为同一节点, 又不至于把"涉农行业"误判成"农行"。同时须诚实交代这一构念的边界: 媒体同框是一种软关联代理, 它反映的是叙事与关注结构, 未必等价于董事联结、同业拆借或股权交叉这类硬关联; 因此本家族的介数应解读为"银行在媒体金融科技话语网络中的中介地位", 而非其在真实业务网络里的桥接地位, 下游因果解读须始终携带这一测量语义。

【方法学与计算】
计算落在 pipeline\panel\network_spillover.py::compute_bank_network_centrality 内, 由 runner 步骤 7g / 7g_win1 / 7g_sent 依次调用三次 (对应三判据)。逐年流程如下: 先在 build_adjacency_matrix 里对同一 docid 下幸存的 target_bank 集合逐无序对累加边权, 每篇每对 +1, 边权最终是"两行全年被同框提及的报道篇数", 得到对称加权邻接矩阵; 再据此建无向共现图 G (含孤立节点), 边权 = 共现篇数。介数属于路径型指标, 语义上"共现越多 = 关系越近", 因此在计算前须把强度翻译成距离: 引擎另建一张倒数权重图 G_inv, 边权取 1 / 共现篇数, 于是共现越密的两家银行在 G_inv 里距离越短。bank_between_cent 即 nx.betweenness_centrality(G_inv, weight='weight') 的输出。networkx 默认对介数做归一化 (无向图归一化因子为 2 除以 (n-1)(n-2)), 使数值落在无量纲的 [0,1] 区间, 可跨年份、跨规模粗略比较 —— 这也是本家族 unit 记为"无量纲归一化"的由来。把"共现强度"取倒数当距离、进而在加权图上算最短路径中心度, 正是 Opsahl 等 (2010) 对加权网络度与最短路径中心度做的一般化处理, 本实现与其口径一致。节点缺失语义须分两层说清: 只有进入该年 bank_list 节点集的银行 (含孤立节点) 才会被 bc.get(b, 0.0) 兜底 —— 在网但未参与任何最短路径者取 0.0, 这是真实的"不居中"而非缺测; 而该年没有任何幸存报道的银行根本不进 build_adjacency_matrix 的 all_banks 节点集、不产生该年的指标行, merge 回面板后该格为 NaN 而非 0.0。0.0 与 NaN 分别对应"在网却不居中"与"当年缺席网络"两种语义, 不可混淆, 与家族内 constraint 等指标的 0-vs-NaN 约定同理。断连图不构成问题: 最短路径介数在多连通分量下天然可算 (分量间无路径, 贡献为零), 无需像 cfbetween / eccentricity 那样限定在最大连通分量上。从算法层面看, networkx 的 betweenness_centrality 在带权图上以 Dijkstra 最短路径为基础, 对每个源点累计经过各中间节点的最短路径条数占比 (记 σ_st(v) 为经过 v 的 s 到 t 最短路径数、σ_st 为 s 到 t 最短路径总数, 取二者之比再对所有源汇点对求和), 无向图下每条路径被计两次, 归一化因子 2 除以 (n-1)(n-2) 恰好抵消并把上界压到 1。归一化对本项目尤为关键: 银行共现网络的规模 n 随年份波动 (幸存银行数逐年不同), 若不归一化, 介数的原始尺度会随网络变大而机械抬升, 令跨年份比较失真; 归一化后, 数值表达的是"相对于同规模网络理论最大值的占比", 才具备跨年可比性。这也解释了为何路径型指标 (betweenness / harmonic / closeness / eccentricity) 统一在倒数权重图 G_inv 上算, 而谱型与结构型指标 (degree / strength / eigen / katz / clustering / constraint) 在原始权重图 G 上算 —— 两组指标对边权的语义要求恰好相反: 前者要"距离 (越小越近)", 后者要"强度 (越大越紧)", 混用会导致符号错乱。33 个结构指标基名的唯一事实源是 network_spillover.NETWORK_METRIC_BASES 元组, bank_between_cent 列于其 18 个节点级指标之中; stata_export 的判据标签机械块与 gate 测试均 import 复用该元组以防漂移。须提示一处等权投影的已知偏差: 一篇提及 N 家银行的报道 (榜单、批量监管通报) 会贡献 C(N,2) 条等权边, 大 N 文章可凭边数膨胀而主导网络; 引擎预留了 hyperedge_normalize (Newman degree-preserving 归一, 每对贡献 1/(N-1)) 选项, 但该参数在生产 runner 中尚未接线, 现行口径恒为 +1 等权, 属 golden-safe 冻结默认值。

【文献定位】
介数中心度在金融与营销文献里被反复验证为"结构位置转化为绩效 / 定价优势"的核心度量。Nezami 等 (2025) 对网络中心度与企业绩效关系做的元分析确认了中心度的绩效相关性 (须注意该元分析背书的是中心度族的一般结论, 并不专门背书本家族外的 bank_clustering 等聚类系指标); Yu 等 (2024) 则直接把网络中心度与信息扩散、资产定价挂钩, 论证居中节点因更早、更全地获取信息而享有定价优势 —— 这恰是本项目把媒体共现网络中心度纳入银行面板的理论动机: 媒体叙事里的居中银行更可能是市场关注与信息汇聚的焦点。把银行系统视为网络、用中心度刻画其在风险与信息传导中的枢纽地位, 上承 Jackson 与 Pernoud (2021) 的系统性风险网络综述, 下接 Fang 等 (2024) 对媒体情绪、存款稳定与银行系统性风险互动的中国情境证据。中心度作为一个"家族"而非单一量的自觉, 在测度论上由 Boldi 与 Vigna (2014) 的中心度公理化工作给出: 不同中心度满足不同公理、回答不同的"何谓重要", 因此并列多种中心度并非冗余, 而是对结构重要性的多棱镜刻画 —— 这一立场直接支撑本项目在同一共现图上并置介数、度、特征向量、closeness、结构洞等 18 个节点级指标的设计。从信息经济学视角进一步看, 介数高的银行处在信息必经的通道上, 更可能率先接触并加工市场信息, 这正是 Yu 等 (2024) 论证的"中心度—信息扩散—定价"链条的微观机制; 而媒体作为这一信息网络的构造者, 其对被报道对象市场认知的塑造力, 是本项目把媒体共现网络 (而非交易网络) 作为中心度底图的立论前提, 也与 Fang 等 (2024) 记录的"媒体情绪经由银行间关联传导至系统性风险"的证据相互印证。更晚近地, Xu 与 Zhao (2024) 直接检验节点在金融网络中的中心度对资产价格预测的增益, 发现把中心度信息纳入预测模型能系统性提升对个体资产价格走势的刻画力, 从预测视角为"结构位置携带定价相关信息"再添一证; 但须强调, 中心度对价格的预测增益属于相关性与信息含量层面的发现, 与"中心度经由某条同群机制因果地驱动结果"是两回事, 后者的识别负担由下一节交代的专门装置承担, 不能因中心度可预测价格便径直赋予其因果解读 —— 这一"可预测 ≠ 可识别"的分界, 正是本家族把介数定位为控制 / 调节而非被工具化处理变量的直接理由。Gomes 等 (2024, Management Science) 用分析师覆盖网络刻画企业间的结构性联结并考察其对公司财务政策的影响, 与本家族用媒体共现网络中心度刻画银行结构位置、进而作为财务规格控制变量的思路高度平行, 为网络结构位置影响企业层面结果这一构念提供了2024年顶刊的最新佐证。文献层面还须补一层"媒体是网络构造者"的自觉: 媒体不仅报道银行, 更以其报道选择塑造哪些银行被并置叙事、进而塑造市场对银行间关联的认知, 因此本家族介数量的是"媒体话语所建构的中介地位", 其效度边界与解读口径都须回到这一构造起点, 而 Boldi 与 Vigna (2014) 的公理化立场恰提醒我们, 任何单一中心度都只回答某一组公理下的"何谓重要", 故须以家族并置而非孤量断言来刻画结构重要性。

【识别策略定位】
本家族在计量上的定位须先厘清一条红线: bank_between_cent 是网络的结构属性变量, 用作控制变量、异质性分组或调节交乘项 (在 brokerage_network 论文的 .do 模板里分别占位 CENTRALITY_BTW / PRIMARY_CENT / MEDIATOR_CENT), 而不是被当作可以直接放进结构式的内生同群回归量。原因是网络型同群效应的识别本身就困难: Manski (1993) 的反射问题指出, 当个体行为同时是同群均值的因和果时, 内生效应、外生 (情境) 效应与相关效应在线性均值模型中不可分离识别; Bramoullé 等 (2009) 证明在部分重叠的社会网络里, 利用"朋友的朋友但非自己朋友"作为工具可恢复识别, 其 2020 年综述 (Bramoullé 等) 进一步系统梳理了网络同群效应识别的边界条件, Boucher 等 (2024) 则把这类效应推广到更一般的非线性偏好结构。这些工作共同的启示是: 网络结构度量一旦进入回归右手边, 其系数的因果解读高度依赖网络本身的外生性假设。本项目对此的处理是保守的 —— 结构中心度作为规格控制与调节项, 真正的识别力交给专门构造的工具变量族 (同组 LOO 均值 / 广义 Bartik / 媒体来源 house-style 暴露), 而 de Paula 等 (2024) 关于从面板数据识别网络连边本身的工作, 提示了当网络边也可能测量有误或内生时的进一步稳健化方向。具体到 brokerage_network 论文, bank_between_cent 被安排为主中心度控制与中介 / 调节通道 (角色 1/5 的主中心度 PRIMARY_CENT + 角色 2 的中介通道 MEDIATOR_CENT), 而内生同群项由 peer_tone_lag1 承担、并以二阶同群 (peer_tone_2nd_lag1) 及地理族同省 leave-one-out 均值作工具, 恰是 Bramoullé 等 (2009) 网络工具变量思路的落地; 项目层面的 IV 扩展 (leave_one_out_peer 同组 LOO 均值、广义 Bartik、outlet house-style 三引擎, runner 步骤 8z) 进一步为面板提供了 just-identified 与 over-identified 两套识别装置。介数中心度在这套安排里始终是"结构位置"控制而非被工具化的处理变量, 这一分工是本家族计量定位的基石, 也避免了把一个可能内生的结构度量误当外生工具混入过度识别检验。更进一步, 网络边本身的测量误差与内生性也须正视: 媒体共现是对"银行间真实关联"的一个含噪代理, 报道选择、议题周期与媒体来源偏好都会扰动边的生成, de Paula 等 (2024) 关于从面板数据识别网络连边的框架恰提示, 当连边可能被误测或由与结果相关的因素内生决定时, 直接把由该网络算出的中心度当作外生右手边变量, 会招致衰减偏差与遗漏网络偏差, 使系数解读脱靶。本项目据此把结构中心度严格限定为控制 / 调节 / 分组变量, 而把可识别的因果负担转移到项目层面的面板 IV 三引擎上: 同组 leave-one-out 均值工具 (借道 Bramoullé 等 2009 的"朋友的朋友但非自身朋友"排他性思路)、广义 Bartik 移份工具、以及媒体来源 house-style 暴露工具, 分别可配出 just-identified 与 over-identified 两套识别装置; 其中 just-identified 规格不产生过度识别约束、不触发 Hansen J, 只有 over-identified 规格 (工具数超过内生变量数) 才触发 Hansen J 过度识别检验, 二者用途迥异、不可混为一谈。由此, 前文所述"中心度可预测价格"这一相关性发现, 与"中心度经由同群通道因果驱动结果"这一识别命题被清晰隔离: 前者容许中心度作为信息含量控制进入规格, 后者的举证责任始终由外生工具承担, 而非由中心度自身承担。须再次界清 Manski (1993) 反射问题的适用范围: 它警示的是把同群均值行为直接放进结构式所导致的内生 / 外生 / 相关三效应不可分离, 而本家族介数并非同群均值行为、而是结构位置的标量属性, 因此它进入规格的方式 (控制 / 调节交乘) 天然规避了反射问题的核心陷阱, 但这不等于它外生 —— 它仍可能与遗漏的银行层异质性相关, 故其系数只作条件相关而非结构因果读取, 真正的因果读取仍须回到被工具化的处理项 peer_tone_lag1 及其二阶同群工具。铁律层面: 三判据变体 (无后缀 / _win1 / _sent) 属规格稳健性并排, 各自 just-identified, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验 —— 判据变体是"同一构念、不同构造口径"的替代测量, 而非彼此正交的多重工具。

【与相邻测度的构念区分】
介数中心度须与共现网络上其余 17 个节点级指标严格区分, 尤其要防止与两个近亲混淆。其一是电流流介数 bank_cfbetween_cent (Brandes-Fleischer / Newman 谱系): Newman (2005) 提出的随机游走 / 电流流介数放弃"信息只走最短路径"的假设, 改设信息像电流一样沿所有路径按电导分流, 因此它给非最短路径上的居中节点也赋权, 与本家族的 Freeman 最短路径介数是两种不同的信息流假设、两个不同的构念, 数值不可互替。Brandes 与 Fleischer (2005) 进一步给出了电流流中心度的电网络等价形式与高效算法, 从计算与刻画两侧确证它与随机游走介数一致, 也使其与 Freeman 最短路径介数的假设分野更为清晰: 电流流版本回答的是"在允许迂回、按电导分流的扩散过程里, 哪个节点承载了最多净流量", 而本家族最短路径版本回答的是"在信息只走测地线的假设下, 哪个节点卡在最多的最短通道上"。两者在稠密、多桥的共现网里可能给出相当不同的节点排序, 稀疏网里则趋近, 因此稳健性叙事里它们互为对照而非互替 —— 若主结论仅在最短路径介数下成立、在电流流介数下翻转, 恰说明结论对"信息是否只走测地线"这一假设敏感, 这类诊断价值正是并置两版介数的目的。这一区分还有一个工程后果: bank_cfbetween_cent (连同 bank_clustering / bank_harmonic_cent) 因谱 / 线性代数运算受 BLAS 浮点漂移, 跨次重建非逐位可复现, 被列入 golden 验零漂移的排除清单; 而 bank_between_cent 走确定性最短路径算法, 不在该 BLAS-FP 漂移清单内 —— 这既是构念区分也是数值确定性区分。其二是度中心度 bank_degree_cent (认识多少邻居) 与特征向量 / Katz 中心度 (邻居本身重不重要): 介数量的是"多少最短路径必须经过我"的桥梁性, 与"连接数量"或"邻居声望"正交, 一家度数不高却卡在两簇之间的银行可以有很高介数。介数亦不同于结构洞族的 bank_constraint / bank_effective_size (刻画自我中心网内邻居是否互相认识) 与 Gould-Fernandez 经纪角色 (按端点群归属把桥接分解为 coordinator / itinerant / gatekeeper_rep / liaison): 后两者是局部 / 分群视角的经纪, 介数是全局最短路径视角的经纪, 互补而非替代。最后, 判据后缀 (_win1 / _sent) 与三轨文本后缀 (_full / _ctx / _ss) 是两个正交的概念空间 —— 前者调的是银行∧银行的邻接构造口径, 后者调的是银行∧金科的文本范围口径, 二者禁混进同一 Hansen J。

【已知局限与稳健性梯子】
第一重局限是共现网络的等权 clique 投影偏差 (前述大 N 文章问题), 现行以 +1 等权冻结、hyperedge_normalize 未接线, 生产重估前须知晓其对高提及度年份中心度的潜在膨胀。从网络类型看, 银行共现网本质是一张两模 (文章 × 银行) 隶属网络向单模 (银行 × 银行) 的投影: 每篇报道是一个"事件", 被同篇提及的银行是该事件的"成员", 一次投影就把一篇提及 N 家银行的报道机械地转成一个 N 节点全连通团, 贡献 C(N,2) 条等权边。Faust (1997) 对隶属网络中心度的系统分析早已指出, 这类由二模投影得到的单模网络, 其中心度会被大规模事件 (此处即榜单式、批量监管通报式的高提及报道) 系统性抬高, 且不同的投影与加权约定会给出实质不同的中心度排序, 因此"投影方式"本身就是一个须披露的研究者选择而非中性操作。引擎为此预留了 hyperedge_normalize (Newman degree-preserving 归一, 每对贡献 1/(N-1) 使单篇总度贡献守恒) 作为缓解手段, 但该参数在生产 runner 中尚未接线, 且在 _win1 / _sent 判据分轨路径下会直接 raise 而非静默降级 (仅 article 主路径实现该选项), 故现行口径恒为 +1 等权、golden-safe 冻结; 高提及度年份的介数读数须据此审慎解读, 生产重估若切换归一约定则须整体重生 golden 并披露数值副作用。第二重是判据敏感性 —— 何谓"两家银行共现"本身是一个研究者选择, 本家族因此把同一介数指标按银行∧银行邻接判据分成三轨: 同篇 (无后缀 canonical) / ±win_radius 句窗 (_win1) / 严格同句 (_sent), 边集依次收紧、节点全集恒等, 三者互为稳健性、不分主次, 用于证明主结论不被"共现判据取多宽"这一取值驱动。这套判据梯子镜像项目内政治词权重梯度与词典消融梯度的先例: 三判据各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J, 且本族刻意不设跨判据的 FWER 校正模板 —— 因为跨模型 rwolf 的先例仅覆盖"同一构念的不同 headline 测量替代", 而判据变体属规格稳健性并排, 不适用族级家庭错误率校正。第三重是样本深度: 本机 T=2 (2017-2018, 约 110 家银行) 的开发面板上, 严格同句判据 (_sent) 的边极稀疏, 介数可能大面积退化为 0 或近零方差, 这是 T=2 的预期退化, 生产 T=18 语料下方能体现判据梯子的真实分辨力。第四重是共现网络作为"真实关联"代理的效度边界 —— 媒体同框未必等于经济关联, Sadeghi 与 Feinstein (2024) 对金融网络传染中心度所做的统计验证, 提示这类由观测数据构造的中心度需要针对零模型做显著性检验, 是本家族未来可补的效度稳健化方向。Zoricakova 等 (2026, Eurasian Economic Review) 用2015-2024年全球系统重要性银行股价数据构建网络, 以介数中心度等中心度指标刻画欧洲银行业系统性风险传染路径, 支撑可持续监管; Alamsyah 等 (2025, Discover Artificial Intelligence) 以新闻文本共现构造企业网络并计算中心度指标, 发现银行类企业在新闻共现网络中占据居中位置, 为媒体共现网络刻画金融机构结构地位提供了另一实证范式。第五重是可比性与解读的谨慎: Nezami 等 (2025) 的元分析同时提示中心度与绩效的关系存在显著情境异质性 (行业、网络类型、绩效口径不同, 效应强弱乃至方向都可能变化), 因此本家族介数进入回归时, 其系数不宜作跨样本的普适因果解读, 而应结合银行类型、媒体结构等调节因素审慎诠释。此外, 归一化介数虽在同一年内可比, 但跨年比较仍受"每年网络规模与稠密度不同"的残余影响 —— 严格的跨年比较宜引入年度固定效应吸收网络层面的年度共同冲击, 而非直接比较归一化数值的绝对水平。综合来看, bank_between_cent 及其两个判据变体的价值不在于给出某个"真实"的桥接系数, 而在于提供一组构造透明、口径互补、各自 just-identified 的结构位置度量, 供主回归做控制、异质性分组与规格稳健性之用; 三判据的分辨力须在生产 T=18 语料上才充分释放, 本机 T=2 的近零方差退化不应被误读为指标失效。

## VAR: bank_between_cent

【变体差分】
本列是家族的 canonical 无后缀主列, tier=core, 也是 network_spillover.NETWORK_METRIC_BASES 元组里 18 个节点级指标的介数基名锚点。它采用最宽松的"同篇 (article)"银行∧银行共现判据: 只要两家银行在同一 docid 报道里被共同提及, 即在该年共现网络中记一条边, 边权累加为全年同框篇数。这条判据走的是 build_adjacency_matrix 的 both-verified 主路径 (criterion='article', suffix=''), 由同 docid 幸存 target_bank 集合逐无序对 +1 生成邻接, 保证每篇报道对每一对银行恰贡献一次计数、杜绝旧 co_mentioned_banks 逐行口径的重复计数与幻影边, 因而其边集是三判据里最稠密的 —— _win1 与 _sent 的边集都是本列边集的子集 (同篇内进一步要求句窗邻近或严格同句)。数值上, 本列 = 倒数权重图 G_inv (边权 = 1 / 同框篇数) 上的 Freeman 最短路径介数中心度, networkx 默认归一化到 [0,1]; 该年在网 (进入 bank_list 节点集) 但未参与任何最短路径的银行取 0.0; 该年无任何幸存报道、未进节点集的银行 merge 回面板后为 NaN 而非 0.0。之所以以"同篇"为 canonical, 是因为它口径最稳、对句级分词与句界切分的噪声最不敏感, 且与项目其余共现构造 (如 fintech_share 分母、共现硬过滤的文章级留存) 的文章级粒度一致, 便于横向对齐; _win1 / _sent 依赖句界切分与句窗扫描, 天然引入更多分词与切句的实现敏感性, 更适合当稳健性轨而非主轨。消费侧, brokerage_network 论文的复现模板把本列同时占位为 CENTRALITY_BTW (主中心度控制)、PRIMARY_CENT (角色 1 主中心度, 语义锚 Freeman 1978 介数 = 经纪 / 桥接) 与 MEDIATOR_CENT (角色 2 中介通道, 与 PRIMARY 同列但语义独立以防模板分叉), 均消费面板实存列、golden-safe。须点明本列在 brokerage_network 五角色蓝图里的精确分工: 角色 1 与角色 5 的主中心度 (PRIMARY_CENT, 源码注释即"角色1/5 主中心度") 及角色 2 的中介通道 (MEDIATOR_CENT) 均由本列 bank_between_cent 承担, 语义锚定 Freeman (1978) 的最短路径介数 = 经纪 / 桥接; 信息枢纽对照 (SECONDARY_CENT, 源码未赋角色编号) 与角色 4 的调节交乘中心度 (MOD_CENT) 则刻意换用 brokerage_eigen_cent (特征向量系, 语义锚 Bonacich 声望枢纽), 二者分别刻画"卡在最短通道上的桥梁"与"连着重要邻居的枢纽"两种不同的居中, 不可互相顶替; 角色 3 是跨族第二工具 OVERID_IV2 (地理族同省 leave-one-out 均值 prov_leave1out_tone_full), 根本不属于中心度族; 角色 5 的网络分组哑变量则由 NET_HET_VAR = bank_is_hub 提供, 离散化的枢纽分组与本列的连续介数分工不同。这一角色分配确保本列在模板里始终扮演"最短路径经纪"这一唯一构念, 即便 PRIMARY 与 MEDIATOR 占位同一物理列, 也以独立占位符命名以防下游模板在角色演化时发生分叉。至于内生同群处理项则由 peer_tone_lag1 承担、本列不越位充当被工具化的处理变量, 与本家族识别定位一以贯之: 本列进规格的合法身份是"结构位置控制 / 异质性分组 / 调节交乘", 其系数作条件相关读取, 因果举证交外生工具, 绝不把它自身当成外生工具混入过度识别检验。由于同篇判据的边集是三判据里最稠密的超集, 本列的介数在数值上通常也最平滑: 边越多、连通性越强, 最短路径越多、越分散, 单一节点垄断路径的概率下降, 极端高介数更少出现; 反之 _win1 / _sent 收紧边集后, 网络更稀疏、更易出现明显的桥接瓶颈, 同一家银行的介数可能相对抬升。因此三判据并非同一数值的微扰, 而是"共现判据取多宽"这一构造维度上的系统性移动, 用作规格稳健性时应关注结论符号与显著性的稳定, 而非点估计的逐位吻合。作为家族 SSOT 锚点, 本列的基名 bank_between_cent 被 codebook 的三个推断函数 (标签 / 来源阶段 / 类别) 与 stata_export 标签机械块共同 import 复用: 推断入口会先用 _CRITERIA_SFX_RE 剥去 _win1 / _sent 判据后缀再匹配, 使三判据变体共享同一套中文标签与"bank-bank edge"判据注解, 从根上杜绝后缀导致的标签分叉。在网银行取 0.0 的语义 (真实"不居中") 亦须在下游回归里与"当年缺席网络"所致的 NaN 区分对待, 否则会把"无桥接地位"错当"数据缺失"删样本, 或反过来把缺席年份误填成零居中。铁律提示: 本列与 _win1 / _sent 两个判据变体互为稳健性、不分主次, 三者各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J; 并且本列所属的判据后缀空间 (银行∧银行邻接口径) 与情感三轨的 _full / _ctx / _ss 文本后缀空间 (银行∧金科文本范围) 正交, 两套后缀在任何过度识别检验里都不得交叉混用。本列走确定性最短路径算法, 不在 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的 BLAS 浮点漂移排除清单内, 是家族中数值可逐位复现的介数主列 —— 这与它的电流流版表亲 bank_cfbetween_cent (受谱运算 BLAS 漂移、跨次非逐位可复现) 恰成鲜明对照。

## VAR: bank_between_cent_sent

【变体差分】
本列 tier=standard, 是介数中心度在最严"严格同句 (sent)"银行∧银行共现判据下的稳健性变体。与 canonical 的差别只在邻接构造口径: 两家银行必须落在同一个句子里被共同提及才记一条边 (win_radius=0), 而非只要同篇即可。实现上, criterion='sent' 走 build_adjacency_matrix 的判据分轨路径, 在每个 docid 组内对文本做句级重扫 —— 用 map_bank_sentence_positions 定位各银行别名的落句位置, 再由 bank_pairs_within_sentence_window (radius=0) 抽取同句共现对; 扫描文本采用 prepend_title 拼接 (标题为第 0 句), 镜像 stage 13 的 match_in_title 口径。这条路径复用与 stage 11/13/ctx/ss 同一套否定 AC 与短名排除事实源 (禁裸 Aho-Corasick 匹配, 例如防"涉农行业"误命中"农行"的假阳性), 而非裸词匹配。因此本列的边集是三判据里最稀疏的 (严格同句 ⊆ ±1 句窗 ⊆ 同篇), 对应的介数刻画的是"仅在同句强共现语境下才成立"的桥接地位。节点全集与 article / win1 判据恒等 (同为该年幸存 target_bank), 仅边更严。须注意本机 T=2 开发面板上, 严格同句边极稀疏, 本列可能大面积为 0 或近零方差, 属预期退化, 生产 T=18 方有分辨力。也正因为同句判据的信噪比最高、假阳性最少, 一旦在生产语料下其介数呈现稳定信号, 它反而是三判据里对"真实强共现桥接"最有说服力的一轨。铁律: 本列与无后缀 canonical、_win1 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混同一 over-identified Hansen J; 判据后缀 _sent 与三轨文本后缀 _ss 分属两个正交概念空间 (银行∧银行邻接 vs 银行∧金科文本), 措辞上刻意区分"bank-bank same-sent edge"与文本轨的 same-sentence 口径, 不得混用。

## VAR: bank_between_cent_win1

【变体差分】
本列 tier=standard, 是介数中心度在"±win_radius 句窗 (win1)"银行∧银行共现判据下的稳健性变体, 严格度介于 canonical 同篇与 _sent 严格同句之间。差别仅在邻接构造口径: 两家银行须在相隔不超过 win_radius 个句子的窗口内被共同提及才成边, win_radius 取自 config/panel.yaml::network_criteria.win_radius (默认 1)。实现上 criterion='win1' 与 _sent 共用 build_adjacency_matrix 的判据分轨路径, 同样在 docid 组内做句级重扫 (map_bank_sentence_positions + bank_pairs_within_sentence_window, radius=win_radius), 扫描 prepend_title 文本、复用同一否定 AC 与短名排除防线, 唯一区别是句窗半径为 1 而非 0。因此本列边集满足"严格同句 ⊆ ±1 句窗 ⊆ 同篇"的包含链, 介数刻画的是"在近邻句范围内共现"这一中等强度共现语境下的桥接地位。一处关键提示: 此处的 win_radius (panel.yaml::network_criteria) 与 stage 13 共现硬过滤所用的 filtering.yaml::cooccurrence_filter.sentence_radius 是两个不同的配置键、互不联动 —— 前者调的是银行∧银行结构网络的邻接窗, 后者调的是银行∧金科留篇过滤的窗, 不可混淆。节点全集与 article / sent 判据恒等, 仅边集介于两者之间。直观上, ±1 句窗判据在"同篇过宽 (整篇任意两处提及即算关联)"与"同句过严 (须挤在同一句内)"之间取折中, 更贴近"两家银行在同一段叙事语境里被并置讨论"的语感, 因而常被视为三判据中语义最平衡的一轨, 既滤掉了跨段落的偶然同框, 又不像严格同句那样把跨句衔接的强关联一并丢弃。铁律: 本列与无后缀 canonical、_sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混同一 over-identified Hansen J; 判据后缀 _win1 属银行∧银行邻接口径, 与情感三轨的 _full / _ctx / _ss 文本口径正交, 两套后缀不得在同一过度识别检验中交叉。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Xiang, Y., & Borjigin, S. (2025). Analyst Network: Implications for Systemic Risk of Non-Financial Firms in China. Emerging Markets Finance and Trade. https://doi.org/10.1080/1540496x.2025.2562336
Chen, S., Cumming, D., Liu, X., Ma, H., & Yan, C. (2024). Alumni Network Centrality and Competitive Aggressiveness. British Journal of Management. https://doi.org/10.1111/1467-8551.12849
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
de Paula, Á., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Brandes, U., & Fleischer, D. (2005). Centrality measures based on current flow. STACS 2005 (Lecture Notes in Computer Science). https://doi.org/10.1007/978-3-540-31856-9_44
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F. (2024). Analyst Coverage Networks and Corporate Financial Policies. Management Science. https://doi.org/10.1287/mnsc.2023.4891
Zoricakova, J., Filickova, N., & Kocisova, K. (2026). Contagion and systemic risk in the European banking sector: implications for sustainable regulation and financial system resilience. Eurasian Economic Review. https://doi.org/10.1007/s40822-026-00371-0
Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S. B., Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A. (2025). Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence. Discover Artificial Intelligence. https://doi.org/10.1007/s44163-025-00350-5
<!-- rendered-citations:end -->
