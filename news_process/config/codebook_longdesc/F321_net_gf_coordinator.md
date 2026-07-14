---
family_id: F321
columns:
- gf_coordinator
- gf_coordinator_sent
- gf_coordinator_win1
unit: 经纪三元组计数 (Gould-Fernandez 协调者型 2-path 条数, 非负整数值以 double 存储; 分组缺失时为 NaN)
formula: "gf_coordinator(i) = Σ_{a<c; a,c∈N(i); (a,c)∉E} 1[g(a)=g(i)=g(c)] — 年度银行共现无向图上, 枚举经纪行 i 的邻居中无序且互不直连的端点对 {a,c}, 计三方同群 (银行类型组) 的 2-path 条数; 判据变体 {同篇共现 canonical 无后缀 / ±win_radius 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::_gould_fernandez_roles (由 compute_bank_network_centrality Part E 在已建年度图 G 上挂载; 邻接矩阵 = build_adjacency_matrix; Stata 标签块 = pipeline/panel/export.py)
upstream:
- 40_article_bank_level (df_exploded 篇章级展开帧, docid 聚合 both-verified 银行集)
- pipeline/panel/iv_did.py::load_bank_group_maps (银行类型分组 SSOT, 年不变)
- config/panel.yaml::network_criteria.win_radius (_win1 判据窗宽, 默认 1)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
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
- doi: 10.1093/rfs/hhae025
  type: journal
  authors: Hirshleifer, D., Peng, L., & Wang, Q.
  year: 2025
  title: "News diffusion in social networks and stock market reactions"
  venue: The Review of Financial Studies
  vol: 38
  issue: 3
  pages_or_artno: "883-937"
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. (H.), & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: "2903-2935"
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
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: "1145-1182"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: "e0274475"
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: "247-272"
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: "171-202"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: "43-96"
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: "41-55"
- doi: 10.1086/421787
  type: journal
  authors: Burt, R. S.
  year: 2004
  title: "Structural holes and good ideas"
  venue: American Journal of Sociology
  vol: 110
  issue: 2
  pages_or_artno: "349-399"
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: "531-542"
- doi: 10.2307/270949
  type: journal
  authors: Gould, R. V., & Fernandez, R. M.
  year: 1989
  title: "Structures of mediation: A formal approach to brokerage in transaction networks"
  venue: Sociological Methodology
  vol: 19
  pages_or_artno: "89-126"
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: "215-239"
- doi: "10.1111/acfi.13091"
  title: "How do co-shareholding networks affect negative media coverage? Evidence from China"
  authors: "Wang, L., Hou, W., & Liu, Y."
  year: 2023
  venue: "Accounting & Finance"
  type: "journal"
- doi: "10.3390/jrfm16040226"
  title: "Enhancing Financial Market Analysis and Prediction with Emotion Corpora and News Co-Occurrence Network"
  authors: "McCarthy, S., & Alaghband, G."
  year: 2023
  venue: "Journal of Risk and Financial Management"
  type: "journal"
new_dois:
  - "10.1111/acfi.13091"
  - "10.3390/jrfm16040226"
---

## CORE

【构念与来源】

gf_coordinator 家族刻画的构念是目标银行在年度银行共现新闻网络中扮演的协调者型经纪角色强度。经纪 (brokerage) 是社会网络分析中最经典的中观构念之一: 当两个彼此没有直接联系的行动者只能经由第三方间接连通时, 这个居间的第三方就占据了经纪位置, 它对信息流动、资源传递与规范扩散拥有结构性的把关与撮合能力。Gould 与 Fernandez (1989) 在这一直觉之上给出了迄今最有影响力的形式化分解: 他们注意到, 单纯计数居间位置 (如 Freeman (1978) 系统化的介数中心度) 会把性质完全不同的居间情形混为一谈, 于是引入行动者的群归属 (group affiliation) 维度, 把每一条经纪路径按照路径两端与居间者三方的群归属组合, 分解为五种社会学含义截然不同的经纪角色: 协调者 (coordinator, 三方同群, 群内的内部撮合人)、巡回经纪 (itinerant broker, 两端同群而居间者为外群, 受雇于外的中介)、守门人 (gatekeeper, 控制外部信息进入本群)、代表 (representative, 代表本群向外输出)、以及联络人 (liaison, 三方分属三个不同群的纯外部桥接者)。这一分解让"处于中间"这个纯拓扑事实获得了群际结构语义, 成为组织社会学与经济社会学度量中介角色的标准工具, 也是本家族的直接算法出处。

本项目把该框架移植到中国银行业的媒体共现语境: 网络的节点是样本银行, 边来自新闻报道中的银行共现——若同一篇 (或按更严判据, 同一句窗、同一句内) 报道同时确证提及两家银行, 则两行之间累积一条 (加权) 共现边; 群归属取银行类型 (国有大行、股份制、城商行、农商行、民营、外资等), 由生产环节既有的银行分组事实源统一给出, 且年内不变。在这一语境下, gf_coordinator 度量的是: 目标银行作为居间者, 连接了多少对彼此不直接共现、但与它同属一个银行类型组的银行对。直觉上, 一家协调者得分高的城商行, 是城商行群体内部新闻叙事的枢纽——媒体在报道其他城商行时倾向于把它一并带出, 使它成为同类银行间隐含比较与信息聚合的参照点。媒体共现网络承载真实的信息扩散与市场后果, 这一前提在近年金融文献中有充分支撑: Hirshleifer, Peng 与 Wang (2025) 证明新闻在社会网络中的扩散结构影响股价反应的速度与幅度; Yu, Hu 与 Zhong (2024) 发现网络中心度经由信息扩散渠道进入资产定价; Fang, Wang, Wang 与 Yuan (2024) 在中国语境下确认媒体情绪影响存款稳定性与银行系统性风险; Cookson, Fox, Gil-Bazo, Imbet 与 Schiller (2026) 则给出社交媒体叙事可以成为银行挤兑催化剂的极端证据。在这些机制下, 一家银行在共现网络中的经纪位置并非新闻计数的机械副产品, 而是其在行业信息生态中结构角色的可解释测度。

【方法学与计算】

计算分为网络构建、分组挂载与角色计数三层, 全部在 pipeline/panel/network_spillover.py 内完成, 逐年独立执行。第一层网络构建由 build_adjacency_matrix 完成: 输入是篇章级展开帧 (每行为文章乘银行的展开记录, 仅保留通过银行侧验证的行, 文章宇宙与全仓 full-only 留篇门控口径一致), 按 docid 聚合出每篇文章内全部幸存目标银行的集合, 集合内每一无序银行对在对称邻接矩阵上恰好累加一次——这一"每篇每对加一"的口径修复了旧实现中同篇孪生行导致的一倍或两倍任意混计, 以及验证已拒绝银行经由共现字段混入的幽灵边问题。canonical 判据 (无后缀列) 即此同篇共现口径; 判据变体在第二节详述。邻接矩阵转为 networkx 无向加权图 G, 孤立银行保留为孤立节点, 节点全集为该年全部幸存目标银行。第二层分组挂载复用 iv_did.load_bank_group_maps 这一既有生产事实源, 得到银行到类型组的映射, 刻意不另造加载器以防口径漂移; 加载失败时映射为空, 全部经纪列优雅置为缺失而非静默填零。第三层角色计数由 _gould_fernandez_roles 执行: 对每个有分组的银行 i, 按银行名 canonical 排序枚举其邻居中的无序端点对 {a, c}, 并施加经典 Gould-Fernandez 铁律——只计端点不直连的对 (若 a 与 c 之间本就有边, 则 a 无须经 i 即可达 c, 该三元组不构成真经纪); 通过筛选的每一对按三方群归属唯一归入四类之一: 三方同群记入协调者, 两端同群而居间者异群记入巡回, 两端恰有一端与居间者同群记入守门代表合并类, 三方互异记入联络人。

两处设计决策需要展开。其一是无向坍缩: Gould 与 Fernandez (1989) 的原始定义建立在有向交易网上, 守门人与代表分别对应外群到本群、本群到外群两个方向; 本项目的新闻共现关系天然无向, 每条二步路径即其自身的逆, 守门人与代表在机械上完全共线, 因此二者合并为单一的守门代表角色, 家族全集落为四个可区分角色加一个总量列, gf_total 恒等于四角色之和, 该守恒关系由单元测试锁定。其二是零与缺失的语义区分: 若银行有分组但不存在任何可用二步路径 (孤立节点、邻居全部互相直连、或邻居分组全缺), 各经纪列取真实零值, 表示该行确实不占据任何经纪位置; 若银行本身的分组缺失, 则各经纪列取缺失值, 表示不可计算——下游回归必须区分"零经纪"与"未知", 这一约定与结构洞约束等相邻列的零对缺失约定一致。端点不直连的筛选还带来一项对文本共现网络尤其重要的稳健性: 一篇同时提及多家银行的文章在投影后形成完全子图 (clique), clique 内任意端点对全部互邻, 经纪计数天然为零, 因此该测度对超边投影造成的稠密伪结构具备内生免疫力, 这是它相对介数类指标的一个实质方法学优点。整套计数是纯组合运算, 邻居按名排序保证确定性, 不涉及任何谱分解或迭代求解, 因此本家族不在浮点库漂移的非确定网络列名单之内, 黄金快照对比时无须豁免。

判据分轨是本家族列结构的第二个维度。结构网络指标全集 (三十三个基名的单一事实源 NETWORK_METRIC_BASES) 按银行与银行共现的判定严格度分为三个判据轨: 无后缀 canonical 列采用同篇共现 (两银行同篇即成边, 现行生产口径); _win1 列要求两银行出现于相距不超过 win_radius 句的句窗内 (窗宽读取 config/panel.yaml 的 network_criteria.win_radius, 默认为一句; 注意该键与 stage 13 银行金科过滤的 filtering.yaml 句窗键是两个互不联动的配置); _sent 列要求严格同句共现。两个更严判据走 docid 组内的句级文本重扫, 扫描文本为标题前置后的正文 (标题记为第零句, 镜像 stage 13 的标题参与匹配口径), 判定原语复用 core/text/entity_context 的银行句位映射与句窗配对函数, 并与全管道共用同一套否定与短名排除事实源 (禁止裸自动机匹配, 以防"涉农行业"误命中"农行"一类假阳性)。三判据共享同一节点全集 (该年幸存银行), 仅边集单调收紧, 因此同一银行年的三个判据值可解释为"叙事关联强度"由宽到严的光谱。必须强调口径铁律: 判据后缀与情感三轨的文本后缀 (_full、_ctx、_ss, 银行与金科共现口径) 是两个正交的概念空间, 不可互相混淆; 三判据变体互为稳健性、不分主次, 各自 just-identified 并排进入各自的回归, 严禁把多个判据变体混进同一个 over-identified 的 Hansen J 检验——它们度量同一构念的不同操作化, 矩条件间的机械相关会使联合过度识别检验失去统计意义, 这一铁律与三轨、co-primary 双轨嵌入、词典消融与政治词权重梯子的处置完全同构。判据族属规格稳健性并排, 不设跨判据的多重检验校正模板, 因为跨模型 FWER 先例仅覆盖同一构念的替代 headline 测量, 而判据轨是同一测量在不同构造超参下的敏感性展示。

【文献定位】

本家族在文献坐标系中处于三条线索的交汇点。第一条是经纪与结构洞的社会网络理论传统: Gould 与 Fernandez (1989) 提供角色分解算法本身; Burt (2004) 证明占据结构洞 (即跨越不直接相连的对手方) 的行动者获得信息与创新优势, 为经纪位置的价值假说提供了经典因果叙事; Zádor, Zhu, Smith 与 Gorgoni (2022) 则将 Gould-Fernandez 计数推广到加权与规范化情形, 并系统讨论了原始计数对网络规模与度分布的敏感性——本项目保留原始未加权计数作为 canonical, 该文是理解其量纲局限与未来加权扩展方向的直接参照。第二条是金融网络与系统性风险文献: Jackson 与 Pernoud (2021) 的综述确立了银行间网络结构 (包括中介位置) 与传染及系统性风险的理论联系; Han, Kim 与 Nanda (2024) 在机构经纪网络中证明经纪位置直接影响流动性供给, 是"银行经纪角色具有实质经济后果"最贴近的实证锚; Li 等 (2026) 从文本风险披露中重建金融网络结构与关联度, 与本项目从新闻文本构建银行网络的做法在数据来源层面同构, 为文本源网络的效度提供方法学佐证。第三条是媒体与银行的信息生态: You, Zhang 与 Zhang (2018) 揭示中国媒体报道版图受制度性力量塑造, 提示共现网络的群际结构可能部分反映媒体制度而非纯粹的经济关联; Xu (2024) 证明财经记者自身的社会网络系统性地扭曲新闻内容, 是共现边形成机制中媒体侧噪声的直接证据。这三条线索共同界定了本测度的解释边界: 它是媒体叙事空间中的结构角色, 与真实银行间敞口网络 (如同业拆借、支付清算) 的经纪结构相关但不等同, 论文写作引用时须保持"叙事网络"限定语。该文证明中国上市公司在共同持股网络中的居间/结构洞位置分别经由信息共享与信息控制渠道降低负面媒体报道, 为本家族"网络结构位置具有媒体叙事后果"的核心假说提供最贴近的中国语境实证锚, 引用格式为 Wang, Hou, & Liu (2023, Accounting & Finance)。该文基于逾五十万篇金融新闻构建企业新闻共现网络并耦合情绪语料, 证明新闻共现结构与市场情绪及价格变动存在中度以上相关, 为本家族以新闻共现图刻画银行间叙事关联的构建方法提供直接的方法学先例, 引用格式为 McCarthy & Alaghband (2023, Journal of Risk and Financial Management)。

【识别策略定位】

在计量识别层面, 本家族在项目回归体系中的定位是网络结构解释变量与机制调节变量, 而非外生处理。将网络位置放入回归右端天然面临三重内生性: 其一是 Manski (1993) 的反射问题——银行的媒体表现与其网络位置互为因果, 群体均值回归无法区分内生社会效应与关联效应; 其二是共同冲击——行业性事件同时推高一组银行的共现与其个体结果; 其三是网络本身的测量内生——报道强度高的银行机械地拥有更多共现机会。项目对这三重问题的处置是: 以 Bramoullé, Djebbari 与 Fortin (2009) 的网络峰效应识别框架为基准, 利用二阶邻居的排除性构造工具变量 (经纪族回归的二阶同伴情绪工具正是该逻辑的实现); 以银行与年份双固定效应吸收时不变禀赋与共同冲击; 并以三判据轨的规格并排检验结论是否被共现判定的松紧驱动。近年方法进展进一步界定了推断的谨慎边界: Boucher, Rendall, Ushchev 与 Zenou (2024) 给出峰效应的一般理论并警示函数形式误设的后果; de Paula, Rasul 与 Souza (2024) 证明网络本身可从面板数据中识别, 提示以观测共现代理真实关联网络时存在的错设风险; Hughes (2026) 针对含固定效应的非线性网络模型给出刀切偏差修正, 与本项目网络指标进入非线性设定时的小样本偏差问题直接相关; Grieser, Hadlock, LeSage 与 Zekhnini (2022) 则示范了公司金融政策网络效应估计中空间计量工具的规范用法。综合而言, gf_coordinator 系数在项目论文中的规范解释是条件相关而非结构因果, 因果语言仅在工具变量规格通过弱工具与排除性论证后启用。

【与相邻测度的构念区分】

本家族与仓内多个相邻网络测度共享同一张年度共现图, 构念边界必须写清。与介数中心度 (bank_between_cent) 及电流介数 (bank_cfbetween_cent) 的区别: 介数计数所有最短路径 (或电流路径) 对节点的经过频率, 对群归属视而不见, 度量的是不加区分的拓扑居间性; Gould-Fernandez 分解恰恰以群归属为核心, gf_coordinator 只计三方同群的居间, 是"群内枢纽"而非"全网枢纽", 两者在群结构显著的网络中可以严重背离——一家只在城商行群内居间的银行可以协调者得分很高而介数平平。与特征向量类声望指标 (bank_eigen_cent、katz、subgraph) 的区别在生产注释中被明确标记为动机区分: 声望类指标度量"与重要者相连"的递归地位, 经纪类指标度量"连接不相连者"的桥接功能, 二者互补且不可互替, Nezami, Chisam 与 Palmatier (2025) 的元分析正是按这一功能分类整理中心度与企业绩效的异质效应的。与 Burt 结构洞族 (bank_constraint、bank_effective_size、bank_ego_density、bank_ci) 的区别: 结构洞指标在自我网络内度量邻居间的冗余与约束, 同样不使用群归属, 且约束是连续强度而非角色计数; gf 族可视为把结构洞的"桥接"直觉在群际维度上做的离散角色分型。与同家族其余四列 (gf_itinerant、gf_gatekeeper_rep、gf_liaison、gf_total) 的区别即角色类型本身: 协调者是群内撮合, 巡回是外群人撮合别群内部, 守门代表是群际边界上的单侧接口, 联络是三群纯桥接, 总量列为四者之和。与二分图经纪族 (brok_bip_ 前缀) 的区别: 后者建立在媒体与银行的二分图上, 度量银行经由共同媒体的间接连接, 图基底与本家族的银行投影图不同。最后, 与网络级年度控制 (net_ 前缀年度广播列) 的区别是层级: gf 族是节点年层面的银行特征, 在双固定效应下有 within 变异, 而年度广播列会被年固定效应吸收。

【已知局限与稳健性梯子】

本家族的已知局限与对应的稳健性安排如下。第一, 计数量纲问题: 原始 Gould-Fernandez 计数随网络规模与节点度数超线性增长, 跨年银行数与报道密度的漂移使原始计数水平跨年不可直接比较, Zádor 等 (2022) 对此有系统讨论并提出加权规范化方案; 项目现行处置是依赖年固定效应吸收水平漂移, 并建议回归使用对数或组内标准化变换, 规范化版本列为未来扩展而非现有列。第二, 分组粒度: 银行类型组是粗粒度分类, 组内异质性 (如头部与尾部城商行) 被压平, 且分组年不变, 无法反映银行改制导致的组别迁移; 分组缺失的银行全列缺失, 样本进入回归时须核对缺失模式是否与银行规模相关。第三, 投影偏误的残余: 端点不直连筛选免疫了单篇多银行文章造成的 clique 伪经纪, 但跨篇累积的稠密化仍会压低所有银行的经纪计数 (邻居间边越多, 可计三元组越少), 使该测度在报道极稠密的年份系统性偏低, 这正是三判据梯子存在的理由——更严的 _sent 判据剔除弱共现边, 在稠密年份恢复区分度。第四, 媒体侧形成机制噪声: 如 Xu (2024) 与 You, Zhang 与 Zhang (2018) 所示, 共现边部分由记者网络与媒体制度生成, 解释时须保留叙事网络限定。第五, 开发环境退化: 本机开发盘仅两年浅面板与极小语料, 共现网络稀疏, 经纪计数大面积为零或缺失属预期退化, 一切分布性结论以生产全量语料为准。稳健性梯子的正式结构为三判据并排 (canonical 同篇、_win1 句窗、_sent 同句), 铁律重申: 三者互为稳健性、不分主次, 各自 just-identified 进入各自规格, 严禁混入同一 over-identified Hansen J; 本家族为纯图论计数, 不属嵌入族, 无 _lg 孪生列 (镜像 MinHash 类指标的非嵌入 carve-out), 亦无 _full/_ctx/_ss 文本轨——判据后缀是唯一的变体维度。

## VAR: gf_coordinator

【变体差分】

本列是家族 canonical 列, tier 为 core, 采用同篇共现判据 (无后缀即 article 判据, 现行生产口径): 只要两家银行在同一篇通过验证的报道中同时以确证目标银行身份出现, 该无序银行对即在当年邻接矩阵累加一条边权, 无须任何句距约束。在此图上, 本列取值为目标银行 i 的协调者型经纪计数: 枚举 i 的全部邻居中无序且彼此不直接相连的端点对, 统计其中三方 (两端点与 i 自身) 同属一个银行类型组的对数。它回答的问题是: 有多少对同类型银行, 彼此在媒体叙事中并不直接关联, 却都与 i 共同出现——i 由此成为该银行类型群体内部叙事网络的内部撮合枢纽。同篇判据是三判据中最宽的口径, 边集最稠密, 协调者计数的绝对水平在三轨中最高, 也是全部三十三个网络结构基名共享的默认口径, 与仓内其余无后缀网络列 (介数、聚类、结构洞等) 处于同一张图上, 可在同一规格内作为相互控制使用而不产生图基底错配。取值语义须严格区分三种情形: 正值表示真实的群内经纪强度; 零值表示该行有分组但当年不占据任何协调者位置 (孤立、邻居全直连、或可计三元组全被端点直连筛除), 是有信息的真实零; 缺失表示该行分组不可得, 不可与零混用, 下游回归的样本构成须显式处理这一区分。本列与同家族 gf_total 满足加法守恒 (总量等于四角色之和), 可用于口径自检。计算为确定性纯组合计数, 邻居按银行名 canonical 排序枚举, 无谱分解、无迭代求解、无随机初值, 因此不在浮点漂移豁免名单内, 黄金对比按逐位相等验收——这一点把本列与特征向量、电流介数等需按全名排除的非确定网络列明确区分开。构念层面, 本列在五角色分解中的独特之处是它完全内向: 协调者的经纪价值不来自跨越群际边界 (那是守门代表与联络人的领地), 而来自在同群成员彼此叙事断裂处充当公共参照; 对银行业而言, 这对应监管分层与业务同质化造成的"同类相比"信息需求——分析师、储户与监管者评价一家城商行时天然以其他城商行为参照系, 媒体叙事把这一比较需求物化为共现结构, 而协调者银行正是该参照系的锚点。因此本列的高值银行假说上应表现出更强的群内信息溢出接收与发送能力, 这也是它区别于同图上介数与结构洞指标 (群盲) 的可检验含义。作为 core 列, 它是项目论文中群内信息中介机制叙事的首选操作化; 使用时注意三点: 原始计数量纲随年度网络规模与稠密度漂移, 进回归建议对数或组内标准化并始终携带年固定效应; 缺失样本 (分组不可得) 的剔除须核对是否与银行规模系统相关, 防止样本选择混入; 本列与 _win1、_sent 两个判据变体互为稳健性、不分主次, 各自 just-identified 并排进入各自规格, 严禁三者混入同一 over-identified Hansen J, 判据族亦不设跨判据 FWER 校正模板, 属规格稳健性并排而非多重假设族。

## VAR: gf_coordinator_sent

【变体差分】

本列是严格同句判据变体 (_sent 后缀): 建图时两家银行仅当在同一篇报道的同一个句子内共同出现才计一条共现边, 是三判据梯子中最严的一端。句级重扫在 docid 组内进行, 扫描文本为标题前置后的全文 (标题记为第零句, 镜像 stage 13 标题参与匹配的口径), 银行提及判定复用全管道统一的否定与短名排除事实源, 禁止裸自动机匹配以防短名假阳性。节点全集与 canonical 列完全一致 (该年全部幸存目标银行), 仅边集单调收紧为同篇边集的子集, 因此本列的协调者计数恒不超过对应银行年在更宽判据下可得的三元组供给上限所允许的范围, 且在稀疏年份更频繁地取真实零值。同句共现在语义上最接近"作者在一个命题内并置两家银行"的强叙事关联, 剔除了同篇但相隔遥远段落的弱关联边, 因而本列对稠密年份的投影稠密化偏误最鲁棒, 代价是小样本年份方差放大、零值堆积。开发环境浅面板下本列大面积为零属预期退化。注意判据后缀与情感三轨文本后缀是正交概念空间, 本列的 sent 指银行与银行的句级判据, 与 _ss 轨的银行与金科同句口径无关。本列与无后缀 canonical 及 _win1 互为稳健性、不分主次, 各自 just-identified 并排进入各自规格, 严禁混入同一 over-identified Hansen J。

## VAR: gf_coordinator_win1

【变体差分】

本列是句窗判据变体 (_win1 后缀), 严格度介于同篇与同句之间: 建图时两家银行在同一篇报道中出现于相距不超过 win_radius 句的窗口内即计一条共现边, 窗宽读取 config/panel.yaml 的 network_criteria.win_radius 键, 默认为一句 (即两银行所在句索引之差不超过一)。须特别注意该配置键与 stage 13 银行金科共现硬过滤的 filtering.yaml 句窗键是两个互不联动的独立键, 改动任一不影响另一。句级重扫口径与 _sent 列完全一致: docid 组内、标题前置文本、标题为第零句、统一否定与短名排除、禁裸自动机; 与 _sent 的唯一差别是允许跨句一步的邻近共现, 因而边集严格介于同句边集与同篇边集之间, 三判据在同一银行年上构成边集单调嵌套的光谱, 本列是其中间锚点。方法学动机是敏感性展示: 若 canonical 同篇判据下的协调者效应在收紧到句窗判据后方向与显著性保持, 则结论不被"同篇远距离弱共现"这类低质量边驱动; 若进一步收紧到同句后才衰减, 则可将效应归因于段落级而非命题级的叙事关联。节点全集与其余两列一致, 零与缺失语义、加法守恒、确定性计算等家族性质均同 canonical 列。本列与无后缀 canonical 及 _sent 互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; 判据族属规格稳健性并排, 不设跨判据 FWER 校正模板。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Wang, L., Hou, W., & Liu, Y. (2023). How do co-shareholding networks affect negative media coverage? Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13091
McCarthy, S., & Alaghband, G. (2023). Enhancing Financial Market Analysis and Prediction with Emotion Corpora and News Co-Occurrence Network. Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm16040226
<!-- rendered-citations:end -->
