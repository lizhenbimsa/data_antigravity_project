---
family_id: F325
columns:
- gf_total
- gf_total_sent
- gf_total_win1
unit: 经纪 2-path 计数 (非负计数, 银行-年; 分组缺失置 NaN, 有分组但无可用 2-path 记 0)
formula: "gf_total = gf_coordinator + gf_itinerant + gf_gatekeeper_rep + gf_liaison; broker i 枚举其邻居中无序且端点不直连的对 {a,c}, 按三元组 (g(a), g(i), g(c)) 的银行类型分组归类为四角色后求和; 判据变体 = 同篇 (无后缀) / ±1 句窗 (_win1) / 严格同句 (_sent)"
producer: news_process/pipeline/panel/network_spillover.py::_gould_fernandez_roles (经 compute_bank_network_centrality Part E 落列; 邻接矩阵 = build_adjacency_matrix)
upstream:
- 40_article_bank_level (df_exploded 篇章级展开帧, both-verified docid 聚合)
- pipeline/panel/iv_did.py::load_bank_group_maps (银行类型分组 SSOT)
- config/panel.yaml::network_criteria.win_radius (_win1 判据窗宽, 默认 1)
- core/text/entity_context.py::map_bank_sentence_positions (_win1/_sent 句级重扫原语)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: "10.1007/s10693-025-00454-0"
  type: "journal"
  authors: "Allen, L., Shan, Y., Tang, Y., & Yildirim, A."
  year: 2025
  title: "What's Your Bank's FinTech Score? Technology Integrating Banking into the Broker Intermediation Model"
  venue: "Journal of Financial Services Research"
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
  authors: Han, M., Kim, S. (H.), & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
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
  pages_or_artno: "103223"
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: "2693"
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
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
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: 11
  pages_or_artno: 727-753
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
- doi: "10.1016/j.jbusres.2025.115452"
  title: "Structural holes and firm innovation in industrial clusters: A dual embeddedness perspective"
  authors: "You, S., Wang, L., Zhou, K. Z., & Jia, L."
  year: 2025
  venue: "Journal of Business Research"
  type: "journal"
- doi: "10.1007/s44163-025-00350-5"
  title: "Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence"
  authors: "Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S. bin, Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A."
  year: 2025
  venue: "Discover Artificial Intelligence"
  type: "journal"
new_dois:
- "10.3390/bdcc9100263"
- "10.1007/s10693-025-00454-0"
- "10.1080/2833115x.2026.2662558"
- "10.1016/j.jbusres.2025.115452"
- "10.1007/s44163-025-00350-5"
---

## CORE

该文构建银行金融科技评分并考察技术如何将银行整合进经纪中介(broker intermediation)模式, 与本家族以经纪角色刻画银行媒体网络中介地位的构念相呼应。

【构念与来源】

本家族测度的构念是银行在年度新闻共现网络中扮演的经纪角色总量, 理论源头是 Gould (1989) 与 Fernandez 合作提出的交易网络中介结构形式化框架 (Gould 与 Fernandez (1989))。该框架的核心洞见是: 网络中介 (brokerage) 不是一个同质概念, 而应按中介三方的群体归属分解为不同的结构角色。给定一条由中间人 i 连接两个互不相识端点 a 与 c 的二步路径 (2-path), 按三个节点所属群体的异同组合, 原始有向版本可区分出协调人 (coordinator, 三方同群)、巡回经纪人 (itinerant broker, 两端同群而中间人异群)、守门人 (gatekeeper, 信息流入本群时把关)、代表人 (representative, 信息流出本群时代言) 与联络人 (liaison, 三方分属三个不同群体) 五种角色。这一分解把"谁在群体之间搭桥"从"谁在网络中居中"里剥离出来: 一个节点可以拥有很高的中心度却完全不做跨群中介, 也可以度数平平却是两个群体之间唯一的信息闸门。用白话说, 传统中心度回答"你认识多少人、你离大家多近", 而经纪角色回答"有多少对彼此不相识的人必须经过你才能搭上话, 以及这些被你撮合的双方分别来自哪个圈子"; 前者是知名度, 后者是掮客地位, 两者在理论机制与经验分布上都可以脱钩。社会学与组织研究的后续经典进一步论证了跨群桥接位置的信息优势, 如 Burt (2004) 证明跨越结构洞的个体更可能产出被组织采纳的好想法; Zádor 等 (2022) 则将 Gould-Fernandez 角色计数推广到加权与归一化情形, 说明该测度族至今仍是网络方法论的活跃前沿。

在本项目语境下, 网络的基底是中文财经新闻的银行共现图: 节点为通过实体验证的目标银行, 边为两家银行在同一报道语境中被共同提及的事件, 逐年切片构图。共现网络承载的经济含义是媒体信息空间中的"共同曝光"结构 —— 两家银行被同篇报道并置, 意味着记者、监管叙事或市场事件把它们放进了同一个信息束, 投资者与储户在阅读时会同时更新对两者的信念。金融文献已经证明这类文本派生网络具有真实的经济内容: Hoberg 与 Phillips 的文本网络传统之外, Li 等 (2026) 直接从风险披露文本中恢复金融网络结构与关联度; Xu (2024) 证明财经记者的社会网络会系统性地塑造新闻偏向; You, Zhang 与 Zhang (2018) 在中国场景下证明媒体报道权力受制度约束并影响公司治理结果。银行的"群"在本实现中取银行类型分组 (国有大行、股份制、城商行、农商行、民营、外资及其他), 因此 gf_total 回答的问题是: 某银行在多大程度上充当了不同类型银行群体之间 (以及群体内部) 的媒体信息中介。中国银行体系恰好具有强分层结构 —— 类型即监管地位、股东背景与业务半径的代理 —— 使得按类型分组的经纪角色分解有清晰的制度含义: 一家在报道中频繁把国有大行与城商行"并置"起来的股份制银行, 处在跨层信息扩散的枢纽位; Wang, Zhang 与 Yang (2020) 对中国担保网络演化的研究表明, 这类跨群桥接位置在危机与刺激周期中的系统性意义尤其突出。以中国产业集群221家企业匹配调查数据证明, 占据更多结构洞对企业创新反而有害, 该负向效应受社会与政治嵌入性调节, 为经纪/结构洞类测度的边际收益非单调性提供了最新经验证据, 引自 You, Wang, Zhou 与 Jia (2025, Journal of Business Research)。基于19万余篇印尼财经新闻构建行业归属与新闻共现网络, 以AI情感分析与网络关联度量刻画公司间媒体共同曝光如何传导至股价, 直接支持本家族以新闻共现图作为经济内容承载基底的构念前提, 引自 Alamsyah 等 (2025, Discover Artificial Intelligence)。

【方法学与计算】

计算分三层: 建图、分组、角色计数。第一层建图由 build_adjacency_matrix 完成: 对篇章级展开帧 (df_exploded, 即 40 号阶段的文章×银行展开) 按年份切片, 以 docid 聚合取每篇文章内全部通过验证的目标银行集合 (both-verified 口径), 集合内每个无序银行对在对称邻接矩阵上恰好加一。这一口径修复过历史缺陷: 旧实现逐行解析共提列会让同一文章的孪生行重复计边 (一对银行按幸存行数计 1 或 2 次不定), 且共提列中仍残留验证已拒绝的银行导致幽灵边入网; 现行 docid 聚合保证每篇文章对每个银行对的贡献恰为一, 且节点全集只含验证幸存银行。第二层分组复用生产单一事实源 load_bank_group_maps (与 IV/DID 模块同源), 将银行名映射到类型标签; 加载失败时分组映射为空, 全部角色列优雅置 NaN 而非静默填零。第三层角色计数由 _gould_fernandez_roles 执行: 对每个中间人 i, 按字典序枚举其邻居集内的无序对 {a, c}, 并施加经典 Gould-Fernandez 铁律 —— 仅当 a 与 c 之间没有直接边时该 2-path 才计入 (端点必须真的需要经过 i 才能相互到达)。这一排除直连的约束对新闻共现图尤其重要: 同篇报道提及多家银行会在投影图上生成完全子图 (clique), 若不排除直连, 一篇罗列十几家银行的行业综述就会给每家银行灌入大量虚假"经纪"计数; 排除直连后, clique 内部端点全互邻, 经纪计数自动为零, 测度对超边投影天然鲁棒。随后按三元组 (g(a), g(i), g(c)) 归类: 三方同群计入协调人; 两端同群且异于中间人计入巡回经纪人; 两端中恰有一端与中间人同群计入守门-代表合并角色; 三群互异计入联络人。gf_total 即四者之和, 该恒等式由单元测试守恒锁定。

一个不可省略的实现细节是有向到无向的坍缩: 原始 Gould-Fernandez 定义在有向交易网上区分五角色, 但本项目的共现图严格无向 —— 每条 2-path 即其自身的逆 —— 守门人与代表人在无向图上机械等同 (完全共线), 故合并为单一的 gf_gatekeeper_rep, 落地为四个可区分角色加总量。缺失值语义经过刻意设计并与其他节点级指标的零对缺失约定对齐: 中间人有分组但没有任何可用 2-path (孤立点、邻居全部互相直连、或邻居分组全部缺失) 记为真实的零经纪 0.0; 中间人自身分组缺失则记 NaN 表示不可计算。下游回归必须区分"零经纪"与"未知", 二者混同会把样本选择问题伪装成经纪效应。邻居枚举采用排序后的规范序, 整个计数过程是纯 Python 整数运算, 不经线性代数库, 因此本家族三列全部逐位确定 —— 它们不在面板九个 BLAS 浮点漂移列 (聚类系数、电流介数、调和中心度各三判据) 之列, golden 零漂移核验时无须排除。计算复杂度上界为各节点度数平方之和, 在年度银行网络的百节点量级上可忽略; 分组加载与银行扫描上下文均为进程级惰性单例, 三个判据臂共享同一分组事实源, 保证判据间差异纯粹来自边集而不掺入分组版本漂移。

【文献定位】

本家族在文献中的位置由三条线索交汇而成。Lei, Campbell-Verduyn, Steglich 与 Wittek (2026, Finance and Space) 用随机行动者导向模型刻画银行与非银行金融机构网络连接二十年间的演化机制, 为本家族逐年切片重建银行共现网络、并以经纪角色刻画结构位置动态变化的做法提供了同类网络动态建模的外部参照。第一条是网络中心度与企业绩效的实证传统: Freeman (1978) 奠定了度、介数、接近度等中心度概念的公理化澄清, 是本模块 Part A 节点级指标的总源头; Nezami, Chisam 与 Palmatier (2025) 的元分析汇总了数百个中心度-绩效效应量, 证实网络位置与企业绩效的关联稳健存在但高度依赖测度选择与情境, 这正是本项目将经纪角色与声望型中心度并列落盘、供规格曲线检验的动机。第二条是金融网络与系统性风险文献: Jackson 与 Pernoud (2021) 的综述系统化了金融网络中风险传染的理论机制, Yu, Hu 与 Zhong (2024) 证明网络中心度通过信息扩散渠道进入资产定价, Han, Kim 与 Nanda (2024) 则直接以机构经纪网络解释流动性供给 —— 经纪位置而非单纯连接数才是信息与流动性中介的关键, 与 Gould-Fernandez 分解的构念内核一致。第三条是媒体文本网络: Li 等 (2026) 与 Xu (2024) 分别从披露文本与记者社交网络两端证明文本派生网络承载真实金融关联, 为"新闻共现图是有经济内容的网络基底"这一前提提供了外部效度。本家族把第一、三条线索的测度工具装配到第二条线索的银行研究对象上, 服务于 brokerage_network 论文模块的核心问题: 银行在媒体信息网络中的经纪位置是否影响其经营结果。就方法谱系而言, 本家族在同类文本网络研究中的边际贡献有二: 一是把群体感知的角色分解引入银行新闻共现图 —— 既有银行网络研究多止步于群体盲的中心度排名, 而中国银行业的类型分层使"桥接谁与谁"本身携带制度信息; 二是与同模块的判据梯子、二分图经纪族、溢出族构成一张互为稳健性的测度网, 使经纪假说可以在多个正交的操作化维度上接受一致性检验, 而非依赖单一测度的显著性。

【识别策略定位】

gf_total 在计量设计中的角色是网络位置型解释变量或调节变量, 其识别威胁与所有内生网络测度共享, 必须放在同伴效应识别文献的坐标系里陈述。Manski (1993) 的反射问题指出, 群体内的行为相似可能来自内生同伴效应、外生特征效应或相关效应, 三者在线性均值模型中一般不可分; Bramoullé, Djebbari 与 Fortin (2009) 证明网络结构本身 (排除性 2-path 的存在) 可以打破反射对称并提供识别, Bramoullé, Djebbari 与 Fortin (2020) 的综述进一步系统化了基于网络拓扑的识别条件; de Paula, Rasul 与 Souza (2024) 则展示了在面板数据中恢复未观测网络连接的前沿方法。本项目的落地策略与这些结果一致: 经纪与溢出族指标进入回归时以银行与年份双固定效应吸收相关效应, 二阶同伴情感 (peer_tone_2nd_lag1_full) 按 Bramoullé 式排除约束充当 brokerage 二阶段最小二乘的工具变量, 而 gf_total 本身不作处理变量而作结构位置控制或异质性切割维度。公司金融的同伴效应实证 (Leary 与 Roberts (2014); Grieser 等 (2022)) 提醒我们网络效应的估计对连接定义高度敏感 —— 这正是本家族按三种共现判据分轨落列的识别动机: 若经纪效应只在最宽松的同篇判据下显著、在同句判据下消失, 则效应更可能由行业综述式报道的并列噪声驱动而非真实的语境级信息中介。需要如实陈述的边界是: 新闻共现网络是媒体选择的结果, 报道倾向本身与银行基本面相关, 因此任何以 gf_total 为解释变量的估计都应解读为条件关联而非结构因果, 除非配合工具变量或事件式冲击设计。工具强度亦须诚实汇报: 以二阶同伴情感为工具时, 网络稠密度低的开发切片上排除性 2-path 稀少, 弱工具风险不可忽视, 应参照 Andrews, Stock 与 Sun (2019) 的弱工具诊断与稳健推断实践给出一阶段 F 与稳健置信区间, 而非仅报点估计; 生产全量语料下网络变密后该风险缓解, 但仍应逐规格披露。此外, gf_total 作为异质性切割维度时, 高低经纪组之间在银行规模、上市状态、媒体覆盖上系统性不平衡, 组间差异不能天真归因于经纪位置本身, 应以协变量平衡或双向固定效应吸收可观测混淆后再做子样本对比。

【与相邻测度的构念区分】

本家族与面板中多个相邻网络测度共享同一张年度共现图, 构念边界必须写清。其一, 与声望型中心度的区分: brokerage 模块的特征向量中心度族 (Bonacich 传统) 度量的是"邻居本身有多重要"的递归声望, 与 GF 经纪角色度量的"跨群桥接量"是互补而非替代 —— 一家与全部国有大行相连的银行声望极高, 但若其邻居彼此互连则经纪计数为零; 生产代码注释明确二者勿混。其二, 与介数中心度 (bank_between_cent) 的区分: 介数计最短路径经过量, 对群体归属视而不见且依赖全图路径结构; GF 只看局部 2-path 且按分组归类, 是群体感知的局部经纪测度。其三, 与 Burt 结构洞族 (bank_constraint, bank_effective_size, bank_ego_density, bank_ci) 的区分: 结构洞测度刻画自我网络的冗余度, 同样不感知分组; GF 角色分解的增量信息恰恰在"桥接的是谁和谁"。其四, 与二分图经纪族 (brok_bip_ 前缀) 的区分: 后者建立在媒体-银行二分图上, 度量银行经由共同媒体的间接关联; 本家族建立在银行-银行投影图上, 两套图基底不同不可互替。其五, 与溢出族 (peer_tone 系列) 的区分: 溢出族是网络加权的同伴结果变量, 本家族是网络结构位置本身; 前者进入回归右端时携带反射问题, 后者的内生性来自网络形成而非同伴行为。

【已知局限与稳健性梯子】

第一, 判据梯子。银行∧银行共现判据分三轨: 同篇 (无后缀 canonical, 现行口径)、正负一句窗 (_win1)、严格同句 (_sent), 由 33 个结构指标基名的单一事实源统一分轨, 本家族三列即 gf_total 在三判据下的并排落地。铁律: 三判据各自 just-identified 并排、互为稳健性、不分主次, 禁止混进同一个 over-identified Hansen J 检验 —— 三列高度相关, 塞进同一工具集只会制造虚假的过度识别检验通过。同样必须复述的口径边界是: 判据后缀与三轨文本后缀 (银行∧金融科技口径的 full/ctx/ss) 是两个正交的概念空间, gf_total 没有 ctx 或 ss 文本轨孪生, 判据变体的主体是银行与银行的共现位置关系, 与情感三轨禁止交叉配对。第二, 计数未归一。经典 GF 角色是原始计数, 随度数与网络规模机械膨胀, Zádor 等 (2022) 提出的加权归一化版本刻意未纳入 (保持与原始定义的可比性); 使用者应在回归中控制度中心度或网络规模, 或对计数做对数化处理, 跨年比较时须意识到语料规模变化会平移计数水平。第三, 分组划分依赖。角色归类完全由银行类型分组驱动, 分组粒度改变 (例如把城商行与农商行合并) 会重排四个子角色之间的分布, 虽然 gf_total 对纯粹的组内组间重排比子角色更钝感, 但并非完全不变。第四, 无向坍缩。守门人与代表人不可区分意味着信息流方向性假说 (谁把关流入、谁代言流出) 在本数据上不可检验, 相关论述只能停留在"跨群把关或代言的合并强度"。第五, 开发环境退化。当前盘上为两年开发切片, 年度网络稀疏, 经纪计数大面积为零或缺失属预期退化, 生产十八年全量语料下的分布以生产机重跑为准; 涉及本家族的实测统计一律由组装器动态注入, 不在正文手填。第六, 边权信息未被利用。GF 角色计数只消费邻接矩阵的二值化骨架 (有边或无边), 共现次数携带的强度信息在本家族中被刻意丢弃 —— 一对银行当年共现一次与共现百次在经纪计数上等价。这一选择忠实于 Gould 与 Fernandez (1989) 的原始定义并保证计数的整数可解释性, 但意味着"弱边"与"强边"对经纪位置的贡献相同; 关心强度维度的使用者应将本家族与同图的强度中心度 (bank_strength_cent) 或路径型加权指标联合报告, 二者分别承载拓扑与强度两类信息。第七, 网络形成的媒体选择偏差。共现图的边由媒体的报道决策生成, 报道概率与银行规模、上市状态、事件强度相关, 小银行的低经纪计数部分反映的是媒体覆盖不足而非结构位置边缘; 以银行固定效应吸收时间不变的覆盖倾向、以年份固定效应吸收语料总量波动, 是使用本家族列的最低规格要求。第八, 分年切片的独立性假设。年度网络逐年独立重建, 不携带跨年记忆, 银行经纪位置的持续性完全来自数据本身而非构造; 这与半衰期加权的溢出族形成对照, 研究经纪位置动态时应显式引入滞后项而非假定构造内含平滑。

## VAR: gf_total

【变体差分】

本列是家族 canonical 列与 core 列: 无后缀即同篇判据 (article criterion) 下的 Gould-Fernandez 经纪角色总量, 也是 33 个网络结构指标基名单一事实源中 Part E 五列的加总项。其精确语义为: 在银行-年粒度上, 以当年全部通过双侧验证的报道构建同篇共现图 —— 只要两家银行在同一篇 (docid 聚合) 报道中同时作为验证幸存的目标银行出现, 邻接矩阵该对加一 —— 然后对该银行作为中间人的全部端点不直连 2-path, 按银行类型三元组归类为协调人、巡回经纪人、守门-代表合并、联络人四角色并求和。恒等式 gf_total 等于四个子角色列之和由单元测试守恒锁定, 使用者可任取总量或分解进入规格, 但不应将总量与全部四个子角色同时放入同一线性回归 (完全共线)。同篇判据是三判据中最宽松的一档: 只要求两银行进入同一报道的验证幸存集合, 不要求句子层面的邻近, 因此边集最稠密、经纪计数水平最高, 对"报道级共同曝光"的构念覆盖最完整, 但也最容易被罗列式行业综述稀释 —— 端点不直连约束已在机制上剔除了 clique 内部的虚假经纪, 残余风险主要是跨段落弱关联并置。缺失值语义: 银行当年不在分组映射中记 NaN (不可计算), 有分组但无可用 2-path 记真实零; 回归前应显式决定零与缺失的处理而非放任 listwise 删除。本列为纯整数计数的浮点存储, 计算路径不经 BLAS, 逐位确定可复现, 不在 golden 核验需排除的九个浮点漂移列之列。作为 core 列, 它是 brokerage_network 论文模块中经纪位置假说的首选结构测度: 相对介数、结构洞等群体盲测度, 它唯一编码了"桥接的两端属于哪类银行"的制度信息; 相对四个子角色, 它以单列概括总中介强度, 自由度成本最低。与 _win1、_sent 两个判据变体的关系是互为稳健性、不分主次的并排臂: 无后缀只是历史命名产物而非统计意义上的"主轨", 三者各自 just-identified 进入各自的回归, 禁混同一 over-identified Hansen J。使用建议上, 本列的典型进场姿态有三种: 作为结构位置控制变量与其他节点级中心度并列进入基准回归, 此时建议同时控制度中心度以剥离"连接多"与"桥接多"的机械相关; 作为异质性切割维度, 按经纪计数高低分组检验信息传导假说的强弱差异; 作为对数化或按网络规模标准化后的连续解释变量, 缓解计数随语料规模膨胀的水平漂移。解读时须牢记两层缺口: 高经纪计数既可能反映银行真实的跨群业务或事件关联, 也可能只是媒体叙事习惯把某类银行当作参照系反复并置; 以及开发切片上大面积零值与缺失属预期退化, 分布形状以生产全量语料重跑为准, 本节不手填任何实测数字, 统计摘要由组装器动态注入。子角色分解的解读也值得一句: 若总量效应主要由联络人分量驱动, 说明跨三类银行群的桥接位置承载了效应; 若由协调人分量驱动, 则效应更接近群内枢纽而非跨群中介, 总量列的单列便利以牺牲这一分辨率为代价。再补一层方法论提醒: 本列是二值化邻接骨架上的整数计数, 共现强度 (同年共现次数) 被刻意丢弃, 因此一对当年偶然并置一次的银行与一对被反复捆绑报道的银行对经纪计数贡献等价; 忠实于 Gould 与 Fernandez (1989) 原始定义并保证整数可解释性的代价, 是弱边与强边不可区分, 关心强度维度者应与同图的强度中心度联合报告。与相邻声望测度的分工也值得在进场前想清: 若研究关心的是"银行的媒体知名度", 应取特征向量或度中心度; 若关心的是"银行是否卡在不同类型银行群之间的信息通道上", 才取本列 —— 二者在中国银行业强分层结构下经验上可脱钩, 一家只与同类股份制银行密集共现的银行可能声望高而经纪计数低。最后重申判据梯子的报告纪律: 本列 (同篇) 与 gf_total_win1、gf_total_sent 构成嵌套边集下的三判据并排臂, 三者各自 just-identified、互为稳健性、不分主次, 论文正文应三臂齐列以定位效应衰减的判据位置, 禁止只挑显著者、亦禁将三列塞入同一 over-identified Hansen J。

## VAR: gf_total_sent

【变体差分】

本列与 canonical 的唯一差分是建图判据收紧为严格同句: 两家银行必须在同一句子内共同出现 (经否定与短名排除防线过滤的真实提及) 才成边, 判据实现走 docid 组内句级重扫 —— 对每篇文章以标题加正文的 prepend_title 口径切句, 标题记为第零句, 镜像 13 号阶段 match_in_title 的扫描约定; 银行位置定位复用实体上下文原语 map_bank_sentence_positions, 与审计脚本共用同一原语保证审计等于生产。节点全集与 canonical 一致 (当年验证幸存银行), 仅边集更严, 因此 _sent 网络是同篇网络的边子图, 经纪计数水平系统性更低、零值更多。构念上, 同句共现要求记者在单句语法单元内并置两家银行, 是"语境级直接关联"的最强文本证据, 最大程度剔除了行业综述中跨段罗列造成的弱关联边; 代价是稀疏化 —— 开发切片上该判据下大量年份网络退化属预期。铁律复述: 本列与 gf_total、gf_total_win1 三判据各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据后缀 _sent 与三轨文本后缀 (full/ctx/ss, 银行∧金融科技口径) 是正交概念空间, 尤其注意本列的同句语义主体是银行∧银行, 与 ss 文本轨的银行∧金科同句口径判据主体不同, 二者不可互相替换或复用。实务上, 本列适合作为经纪效应的保守下界臂报告: 若主结论在本判据下依然成立, 说明效应由句内强关联驱动, 抵御"综述并列噪声"批评的能力最强; 若仅在同篇判据下成立, 则应在文中如实降格表述。

## VAR: gf_total_win1

【变体差分】

本列与 canonical 的唯一差分是建图判据取正负一句窗: 两家银行的提及位置落在彼此相距不超过 win_radius 句 (窗宽由 config/panel.yaml 下 network_criteria.win_radius 配置, 默认取一) 的范围内即成边, 松于严格同句、紧于同篇, 是判据梯子的中间臂。实现与 _sent 同走 docid 组内句级重扫路径: prepend_title 口径切句、标题为第零句、复用同一实体上下文原语与否定短名排除防线, 节点全集与 canonical 一致、仅边集介于两端之间, 因此三判据网络构成嵌套边集序列 (同句边集包含于句窗边集包含于同篇边集), 经纪计数单调性不保证逐行成立 (端点不直连约束下, 加边既可能创造新 2-path 也可能把既有 2-path 的端点连通而剔除计数), 这一非单调性是解读三臂差异时的重要细节。⚠ 配置键辨析: 本判据的 win_radius 与 13 号阶段共现硬过滤的 filtering.yaml 下 cooccurrence_filter.sentence_radius 是两个不同的配置键, 语义主体分别为银行∧银行与银行∧金融科技, 互不联动, 修改任一不影响另一。铁律复述: 本列与 gf_total、gf_total_sent 三判据各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 判据后缀 _win1 不是三轨文本后缀, 与情感测度的 full/ctx/ss 轨道禁止交叉配对使用。作为梯子的中间臂, 本列的诊断价值在于定位效应衰减发生的位置: 若同篇臂显著而本臂已不显著, 说明关联主要来自跨段落弱并置; 若本臂仍显著而同句臂消失, 则效应存在于邻句语境但未达句内强度, 报告时应完整呈现三臂而非只挑显著者。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Allen, L., Shan, Y., Tang, Y., & Yildirim, A. (2025). What's Your Bank's FinTech Score? Technology Integrating Banking into the Broker Intermediation Model. Journal of Financial Services Research. https://doi.org/10.1007/s10693-025-00454-0
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Lei, J., Campbell-Verduyn, M., Steglich, C., & Wittek, R. (2026). The evolution of global bank-to-nonbank networks, 2002–2022: a stochastic actor-oriented analysis. Finance and Space. https://doi.org/10.1080/2833115x.2026.2662558
You, S., Wang, L., Zhou, K. Z., & Jia, L. (2025). Structural holes and firm innovation in industrial clusters: A dual embeddedness perspective. Journal of Business Research. https://doi.org/10.1016/j.jbusres.2025.115452
Alamsyah, A., Ramadhani, D. P., Kristanti, F. T., Nasution, A. H., Mohamad, M. S. bin, Sokkalingam, R., Widiyanesti, S., & Saputra, M. A. A. (2025). Deciphering news sentiment and stock price relationships in Indonesian companies: an AI-based exploration of industry affiliation and news co-occurrence. Discover Artificial Intelligence. https://doi.org/10.1007/s44163-025-00350-5
<!-- rendered-citations:end -->
