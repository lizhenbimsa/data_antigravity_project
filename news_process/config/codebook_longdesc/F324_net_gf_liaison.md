---
family_id: F324
columns:
- gf_liaison
- gf_liaison_sent
- gf_liaison_win1
unit: 无量纲非负计数 (Gould-Fernandez 经纪 2-path 角色计数, double 存储; 有分组但无可用 2-path = 0.0 真实零经纪, 分组缺失 = NaN 不可计算)
formula: "gf_liaison_i,t = |{无序邻居对 {a,c} ⊂ N(i): a-c 无边 (端点不直连) ∧ g(a), g(i), g(c) 三群两两互异}|, 于年度银行共现无向图 G_t 上逐银行枚举; 判据三变体: 同篇 (无后缀 canonical) / ±1 句窗 (_win1) / 严格同句 (_sent)"
producer: pipeline/panel/network_spillover.py::_gould_fernandez_roles (由 compute_bank_network_centrality 步骤 7g 逐年调用, 三判据各跑一遍)
upstream:
- 40_article_bank_level (df_exploded 篇章级展开帧; both-verified docid 聚合建边)
- config/bank_addresses.json (iv_did.load_bank_group_maps → NFRA 银行类型分组 g(·))
- config/panel.yaml::network_criteria.win_radius (_win1 判据句窗宽, 默认 1)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: 10.1093/rfs/hhae025
  type: journal
  authors: Hirshleifer, D., Peng, L., & Wang, Q.
  year: 2025
  title: "News diffusion in social networks and stock market reactions"
  venue: The Review of Financial Studies
  vol: 38
  issue: 3
  pages_or_artno: "883-937"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: "79-104"
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. (H.), & Nanda, V. K.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: "2903-2935"
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: "2693"
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
new_dois: []
---

## CORE

【构念与来源】
本家族测量的构念是银行在媒体报道共现网络中的联络人经纪地位, 即 Gould 与 Fernandez (1989) 经纪角色分解框架中的 liaison 角色计数。经纪的社会学含义是: 当两个彼此没有直接联系的行动者需要经由第三方才能连通时, 这个居间的第三方就占据了经纪位置; Gould 与 Fernandez (1989) 的关键贡献在于指出, 经纪并非单一同质的位置, 而应按照三方各自的群体归属进一步分解为性质迥异的角色类型。在他们的原始有向交易网框架里共有五种角色: 协调人 (三方同群)、巡回经纪人 (两端同群而居间者外群)、守门人 (居间者与接收端同群)、代表 (居间者与发送端同群)、联络人 (三方分属三个互不相同的群体)。其中联络人角色最为特殊: 它刻画的是纯粹的跨群桥接 — 居间银行既不属于信息来源一端的群体, 也不属于信息去向一端的群体, 而是以第三方群体成员的身份沟通两个彼此隔绝的群体。在群体边界构成信息与资源流动摩擦的场景下, 联络人位置被认为承载了最强的结构洞跨越收益与最重的中介负担, 这一逻辑与 Burt (2004) 关于跨越结构洞者更易获得好想法与绩效溢价的经典发现一脉相承。本项目将该构念移植到中国银行业的新闻共现语境: 图的节点是样本银行, 边表示两家银行在同一媒体报道中被共同提及 (共现), 群体归属取国家金融监督管理总局口径的银行类型七分类 (国有大型商业银行、股份制商业银行、城市商业银行、农村商业银行、民营银行、外资法人银行及其他), 经由 iv_did 模块的 load_bank_group_maps 从 config/bank_addresses.json 读入并映射为 soe/joint/city/rural/private/foreign/other 短标签。于是 gf_liaison 的白话含义是: 在当年的媒体共现网络里, 这家银行有多少次充当了两家彼此从未同篇共现、且分属另外两个不同类型群体的银行之间的唯一媒体叙事桥梁。举例而言, 若一家股份制银行的报道邻居中同时有一家城商行与一家农商行, 而这两家银行彼此从不同篇出现, 则该股份制银行为这一对银行贡献一次 liaison 计数 — 三方类型两两互异, 且两端确须经它才在媒体叙事空间中连通。

【方法学与计算】
计算分三步。第一步建图: 生产函数 compute_bank_network_centrality (network_spillover.py 步骤 7g) 逐年调用 build_adjacency_matrix, 以篇章级展开帧 df_exploded 为输入, 按 docid 聚合同一篇文章中全部通过银行实体校验的 target_bank 集合, 集合内每个无序银行对的邻接权重加一 (both-verified 口径, 每篇文章每对恰计一次; 该口径是 2026 年 6 月的边权统一修复, 封死了此前旧实现中同篇双行重复计数与未过校验银行以幻影边入网两类污染)。节点全集为该年幸存的全部目标银行, 含孤立点。第二步取分组: 复用生产单一事实源 load_bank_group_maps 得到银行到 NFRA 类型标签的映射; 加载失败时映射为空, 全部 gf 列优雅置 NaN 而非报错。第三步角色枚举: 对图中每个候选经纪银行 i, 先取其分组 g(i), 分组缺失者五个 gf 列全 NaN; 否则对其邻居按名称排序后 (canonical 序保证跨次运行确定性) 枚举全部无序邻居对 {a, c}, 施加经典 Gould-Fernandez 铁律 — 仅当 a 与 c 之间没有直接边时才计入, 即两端必须真正经由 i 才能连通; 随后按三元组 (g(a), g(i), g(c)) 归类: 三者全同记 coordinator, 两端同群而 i 外群记 itinerant, 两端恰有一端与 i 同群记 gatekeeper_rep, 三群两两互异记 liaison。gf_total 为四者之和, 由单元测试锚定守恒恒等式。两点设计须特别说明。其一, 原框架定义在有向网上, 而本项目共现图严格无向, 每条二步路径 a-i-c 即其自身的逆, 导致守门人与代表两角色机械坍缩为完全共线, 故合并为单列 gf_gatekeeper_rep, 全家族落地为四个可区分角色加合计共五列, 本家族即其中 liaison 一支。其二, 端点不直连约束使该测度对完全子图投影天然鲁棒: 新闻共现本质是超边 (一篇多银行报道) 向两两边的 clique 投影, 若不排除直连端点, 一篇提及许多银行的综述稿会为每家银行制造大量虚假经纪计数; 在端点不直连约束下, 同篇共现的银行对彼此直连, 相互之间的经纪计数恰为零, 虚增被结构性排除。缺失语义刻意区分两种情形: 银行有分组但当年无任何可用二步路径 (孤立点、邻居全部彼此直连、或邻居分组全缺) 时取值 0.0, 语义是真实的零经纪; 银行分组本身缺失时取 NaN, 语义是不可计算, 下游回归须区分零与未知, 与 bank_constraint 等结构洞列的零对 NaN 约定一致。单位为无量纲非负计数, 以浮点 double 存储; 该枚举为纯整数计数加排序遍历, 不涉及任何谱分解或迭代求解, 故不在 BLAS 浮点漂移的非确定列清单之内, 跨次重建逐位可复现。进入面板的文章宇宙与全流水线的留篇门控口径一致: 自 2026 年 6 月 29 日起是否判为一篇银行金融科技报道只看 full 轨 LLM 校验 (llm_verified_full), ctx 与 ss 为 conditional-on-full 的子集轨, 网络建边所用的篇章级展开帧继承这一 full-only 行宇宙。

【方法学补注: 复杂度、确定性与工程边界】
角色枚举的时间复杂度对单个经纪银行为其度数的平方乘以邻接查询常数, 全年全网为各节点度数平方之和的量级; 在银行数百量级、年度图远未饱和的生产语料下逐年计算开销可忽略, 且与谱类指标不同不需要任何线性代数库, 纯 Python 整数路径保证了跨平台逐位一致。确定性设计有三处显式落点: 邻居按名称排序后枚举 (canonical 序), 无序对只按索引上三角走一遍 (不重复计正逆), 分组映射为只读字典 — 三者合并保证同输入必同输出, 这使 gf 五列成为网络列族中少数可直接进入 golden 逐位校验、无需列入 BLAS 漂移排除清单的列。工程边界上, 判据参数与落列后缀在函数入口做配套断言 (article 对空后缀、win1 对 _win1、sent 对 _sent), 错配立即抛错而非静默串列; networkx 缺装时整个网络步骤优雅跳过并落警告, 分组文件缺失时仅 gf 五列置 NaN 而其余二十八个结构指标照常产出, 两级降级互不连坐。列名、判据标签与 Stata 变量标签由 NETWORK_METRIC_BASES 单一事实源机械派生, stata_export 与 gate 测试 import 复用同一元组防漂移, 任何对本家族的增删必须从该元组入手而非散改字符串。

【文献定位】
本家族在方法与实证两个层面各有清晰的文献锚点。方法层面, Gould 与 Fernandez (1989) 是角色分解算法的唯一出处; Freeman (1978) 的中心度概念澄清则是理解经纪与中心度之区分的前提 — 中介中心度衡量的是节点落在最短路径上的频率, 与群体归属无关, 而 GF 分解的全部信息增量恰在于把桥接行为按群体语义切开。Zádor 等 (2022) 系统讨论了经典 GF 计数的两个已知短板 (不加权、不归一) 并提出加权归一化改进, 本项目刻意保留经典未加权计数作为 canonical 口径, 将该文作为局限披露与未来稳健性方向的方法学参照。实证层面, 经纪与中心度位置影响金融主体行为与绩效的证据链包括: Han, Kim 与 Nanda (2024) 发现机构经纪网络实质性促进流动性供给; Yu, Hu 与 Zhong (2024) 表明网络中心度经由信息扩散渠道进入资产定价; Nezami, Chisam 与 Palmatier (2025) 的元分析确认中心度与企业绩效的稳健正相关但强调效应量对网络构造口径敏感; Grieser 等 (2022) 证明公司金融政策存在显著网络效应。银行与金融网络方向, Jackson 与 Pernoud (2021) 的系统性风险综述确立了银行间网络结构 (含跨群桥接位置) 对风险传染的核心作用; Gao, Ru 与 Yang (2022) 以中国股权网络证明网络信息在银行信贷决策中的作用; Wang, Zhang 与 Yang (2020) 刻画了中国担保网络在危机与刺激期的演化, 为中国银行间以群体为界的网络结构提供了直接背景。媒体文本建网这一数据来源的合法性由文本网络文献支撑: Li 等 (2026) 从文本风险披露中恢复金融网络结构与关联度, Xu (2024) 证明财经记者社交网络塑造新闻偏差 — 后者同时提醒共现网络部分内生于媒体生产过程; You, Zhang 与 Zhang (2018) 关于中国媒体笔杆子被俘获的证据, 与 Fang 等 (2024) 关于媒体情绪影响中国银行存款稳定与系统性风险的发现, 共同确立了媒体叙事对中国银行业结果变量的实质传导。Hirshleifer, Peng 与 Wang (2025) 与 Cookson 等 (2026) 则从新闻在网络中的扩散与社交媒体挤兑催化两个方向, 说明银行在信息网络中的位置本身即是风险与关注的传导管道 — 这正是把 liaison 位置作为面板解释性结构控制的经济学动机。

【识别策略定位】
本家族在诸论文规格中的定位是网络结构控制变量与机制调节变量, 不是任何一篇论文的处理变量或主结局。将其纳入回归的首要目的, 是在估计媒体情感或金融科技测度对银行结果的效应时, 吸收银行在媒体叙事网络中的结构位置差异 — 一家常年充当跨类型叙事桥梁的银行, 其被报道的强度、题材与语调分布均系统异于网络边缘银行, 遗漏该维度会使情感系数混入结构位置效应。识别上须直面网络计量的两大经典难题。其一是 Manski (1993) 的反射问题: 同群银行的结果与特征互为函数, 天真回归无法分离内生社会效应与外生特征效应; Bramoullé, Djebbari 与 Fortin (2009) 证明网络的不完全传递性 (朋友的朋友不是朋友) 可提供识别力, 而 liaison 计数恰恰以端点不直连为定义要件, 其变异正来自网络中的开放三元组, 与该识别逻辑同构。Boucher 等 (2024) 的一般化同伴效应理论进一步说明线性均值模型只是特例, 结构位置变量进入回归的函数形式本身即是规格选择。其二是网络内生性: 共现网络由媒体选题生成, 而选题与银行不可观测冲击相关。本项目的缓解路径是分层的 — 银行与年份双向固定效应吸收持久位置与年度网络整体形态 (gf 列是节点级测度, 年固定效应下仍有组内变异, 与被年固定效应完全吸收的 net 级年度广播列不同); IV 扩展族 (同组留一均值、广义 Bartik、媒体 house-style 暴露) 为情感处理变量提供外生变异; 判据梯子 (下述) 检验建边口径这一研究者自由度。gf 列自身不设工具变量, 其系数一律作条件相关而非因果解读, 相应论文稿的稳健性叙事亦按此披露。

【与相邻测度的构念区分】
面板中与 gf_liaison 共存的结构测度须逐一划界。第一, 与家族内三个兄弟角色列的区分是纯群体语义的: gf_coordinator 计三方同群的群内中介, gf_itinerant 计两端同群而居间者外群的外来仲裁, gf_gatekeeper_rep 计居间者与恰一端同群的边界把守, gf_liaison 计三群互异的纯跨群联络; 四者定义域互斥、并集恰为全部合格二步路径, gf_total 为其和。第二, 与路径型中介测度 (bank_between_cent, bank_cfbetween_cent) 的区分: 中介中心度对全图最短路径 (或电流路径) 加总, 完全不看群体归属, 且为归一化连续量; gf_liaison 只数局部二步路径且以三群互异为要件, 是未归一化计数。一家银行可以中介中心度很高而 liaison 为零 (它桥接的全是同类型银行), 反之亦然。第三, 与 Burt 结构洞族 (bank_constraint, bank_effective_size, bank_ego_density, bank_ci) 的区分: 结构洞测度刻画自我网络的冗余度, 同样不含群体语义; GF 分解可视为把结构洞跨越行为按群体标签再切分, 二者是互补而非替代 — 生产代码注释明确记载了声望 (特征向量类) 与真经纪 (GF 类) 的动机区分, 勿混。第四, 与 brokerage_network 论文的二分图族 (brok_bip_ 前缀) 的区分: 后者建在媒体对银行的二分图上, 图基底不同 (媒体节点显式入图), 而本家族建在银行对银行的单模共现投影上, 两族不可互替。第五, 与 net_ 前缀年度网络级列的区分: 那些是全网标量按年广播, 年固定效应下不可识别, 仅作描述与交互项母体; gf 列是节点级, 组内可识别。

【已知局限与稳健性梯子】
第一, 判据梯子。银行与银行何谓共现存在研究者自由度, 本家族按三档判据分轨落列: 同篇共现 (无后缀 canonical, 现行生产口径)、±1 句窗共现 (_win1)、严格同句共现 (_sent)。三判据各自 just-identified 并排、互为稳健性、不分主次, 铁律禁止混入同一 over-identified Hansen J 检验; 判据后缀与三轨文本后缀 (_full/_ctx/_ss, 银行与金融科技词共现口径) 是两个正交概念空间, 不得混淆, 同理三轨列亦禁与判据变体同入一个过度识别系统。第二, 未加权与未归一化。经典 GF 计数忽略边权 (共现强度) 且随度数机械膨胀, Zádor 等 (2022) 的加权归一化变体是明确的方法学替代方案, 本项目未实现, 属已知披露局限; 实务上回归中与度中心度或规模控制同列可部分吸收机械分量。第三, 分组粒度。七分类 NFRA 口径粗于股权或地理分组, liaison 的语义随分组定义漂移; 分组来自静态配置文件, 不随年份变动, 银行改制变更类型的极少数情形按现行标签处理。第四, clique 投影残留。端点不直连约束虽排除同篇虚增, 但跨篇的稠密报道簇仍可能抬高局部连通从而压低经纪计数, 方向为保守偏误。第五, 媒体生成过程内生性。共现由选题决定, Xu (2024) 与 You, Zhang 与 Zhang (2018) 的证据提示网络本身携带媒体偏差, 系数解读须限于条件相关。第六, 小样本退化。开发环境 T=2 面板上年度网络稀疏, gf 列大面积取零或 NaN 属预期退化, 生产 T=18 全语料下方有实质变异; 该列不在 BLAS 非确定清单内, 零漂移验证无需排除。第七, 缺失语义双态 (零对 NaN) 要求下游任何以 gf_liaison 为条件的样本切分显式处理 NaN, 直接 listwise 删除会系统性剔除分组缺失银行而非零经纪银行, 二者经济含义不同。第八, 时间聚合口径。网络按自然年切片重建, 年内共现的时序先后被抹平, 年末成边与年初成边等权; 跨年叙事链 (前一年铺垫、次年并提) 不产生跨年边, 对慢变量的经纪位置这是可接受的平滑, 但研究事件窗口内短期桥接行为时应改用更细时间切片, 面板层面不提供。第九, 计数右偏。经纪计数分布高度右偏且下端堆积于零, 回归前的对数或反双曲正弦变换、以及按报道量分层的敏感性检验, 均属推荐而未在面板层面预制的下游处理, 由各论文规格自行声明。第十, 分组静态性与坍缩残留。NFRA 类型标签取自静态配置, 不随年份更新, 少数银行的改制、合并或牌照变更在样本期内被按其现行类型一体处理, 由此在类型边界附近可能引入轻微的分组误置; 又因共现图严格无向导致守门人与代表两角色机械共线而合并, 本项目仅保留 liaison 这一三群互异角色作为纯跨群桥接的干净测度, 其相对于合并后 gatekeeper_rep 列的语义边界在于是否要求三方类型两两互异, 使用时须与该列并置理解而非替换。第十一, 与情感溢出列的正交性。本家族只刻画网络位置的结构几何, 不携带任何情感或语调信息; 面板中另有 peer_tone 系列一阶与二阶情感溢出列承载沿边传播的语调, 二者在回归中分工明确, 结构位置列吸收谁在网络中央、情感溢出列吸收邻居说了什么, 混用会造成机制解释的层级错置。

## VAR: gf_liaison

【变体差分】
本列为家族 canonical 列, tier=core, 判据取同篇共现 (criterion='article', 落列无后缀), 是 NETWORK_METRIC_BASES 单一事实源中 Part E 五个 Gould-Fernandez 经纪角色基名之一, 亦是本家族三列中唯一进入核心列扩围签核的列。精确语义: 对银行 i 在年度 t 的同篇共现图 G_t 上, 取其排序后的邻居集合, 枚举全部无序邻居对 {a, c}, 仅保留 a 与 c 之间无直接边 (当年从未同篇共现) 且三方分组均可得的对, 在其中统计分组三元组 (g(a), g(i), g(c)) 两两互异的对数。建边口径为 both-verified docid 聚合: 一篇文章中全部通过实体校验的银行两两加一条权重一的边贡献, 同篇多次提及不重复计数, 未过校验的银行不入网 (幻影边防线)。同篇判据是三档判据中最宽的一档: 只要两家银行出现在同一篇文章的任意位置即成边, 不要求句级邻近, 因而图最稠密、liaison 计数的机会集最大, 但也最可能把仅在长综述稿首尾分别被点名的弱关联计入。选它作 canonical 有两点理由: 其一是历史连续性, 全部网络列在判据分轨 (2026 年 7 月) 之前即按同篇口径生产, 无后缀列与既有 golden 快照及论文规格保持字节连续; 其二是与 build_adjacency_matrix 的 both-verified 主路径同构, 无需句级文本重扫, 计算最廉价且不依赖内容列在位。取值与缺失语义遵家族约定: 有分组但无合格二步路径取 0.0 (真实零经纪), 分组缺失取 NaN (不可计算); 数据类型 double, 值域为非负整数格点。与两个判据变体列的关系是互为稳健性、不分主次, 三列各自 just-identified 并排进入各自的回归规格, 铁律禁止三判据混入同一 over-identified Hansen J; 论文使用场景中本列作为默认结构控制进入主表, _win1 与 _sent 进入稳健性附表, 三列系数方向与显著性形态的一致性即为建边口径不驱动结论的证据。解读时注意本列为未归一化计数, 与银行报道量及网络度数正相关, 建议与度中心度或规模变量同列以分离机械分量; 年固定效应下节点级组内变异保留, 可识别。在四角色分解恒等式中, 本列与 gf_coordinator、gf_itinerant、gf_gatekeeper_rep 三列定义域互斥且并集穷尽全部合格二步路径, 四列之和恒等于 gf_total, 该守恒关系由单元测试锚定; 因此在回归中切勿将四角色列与 gf_total 同时放入右端 — 五列精确共线, 求解器的任意舍列行为会使系数不可解释, 正确用法是要么放 gf_total 一列取总经纪强度, 要么放至多四个角色列取分解结构。经济解读上, 本列在七分类分组下捕捉的是跨银行类型的叙事联络: 典型高值情形是全国性银行 (国有大型或股份制) 在报道中被媒体用作串联地方性机构 (城商行、农商行) 与新型机构 (民营、外资) 的参照锚, 此类银行在金融科技扩散、同业风险传染与监管叙事三条线上均处于信息干线位置; 而 liaison 恒为零的银行或者报道稀少, 或者其媒体叙事被锁定在单一类型圈层之内。作为家族 canonical, 本列亦是论文规格中判据梯子的基准臂与动态统计注入的默认锚列。补充两点使用提示: 其一, 因同篇判据把长综述稿首尾分别点名的弱关联也计入边集, 本列的机会集在报道密集年份显著大于句窗与同句变体, 研究者若关注强关联桥接应以 _sent 列为主锚而非本列; 其二, 本列在银行与年份双向固定效应下仍保留节点级组内变异, 与被年固定效应完全吸收的 net_ 前缀年度广播列不同, 可直接作为控制或调节项进入面板, 但因其为未归一化计数, 跨年比较须警惕全网整体密度随语料增长而抬升的水平漂移, 稳健做法是与度中心度或年度网络规模同列以吸收该趋势成分。

## VAR: gf_liaison_sent

【变体差分】
本列为严格同句判据变体 (criterion='sent', 后缀 _sent), tier=standard。与 canonical 列的唯一差分在建边判据: 两家银行必须在同一篇文章的同一个句子内共同出现才成边。实现走 build_adjacency_matrix 的判据分轨路径 — 对每个 docid 组内至少两家幸存银行的文章, 以幸存银行的别名字典为输入做句级文本重扫, 判据原语为 entity_context 模块的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window (窗宽取零即严格同句), 扫描文本为 prepend_title 口径的标题加正文且标题记为第零句 (镜像 stage 13 的 match_in_title 口径), 银行侧命中沿用否定与短名排除防线 (禁裸自动机匹配, 防涉农行业误命中农行一类假阳性)。节点全集与 canonical 完全一致 (同年幸存银行, 含孤立点), 仅边集为其子集且严格更保守, 故本列的图更稀疏、liaison 计数系统性不高于同年同行的宽判据列。构念上, 同句共现要求媒体在单个句法单位内并置两家银行, 语义关联强度最高, 最接近作者有意将两行主体并举的叙事行为, 代价是牺牲跨句照应与段落级关联。GF 角色枚举、分组映射、端点不直连铁律、零对 NaN 缺失语义与 canonical 逐项相同。铁律复述: 本列与无后缀及 _win1 列三判据各自 just-identified 并排、互为稳健性、不分主次, 禁混入同一 over-identified Hansen J; 判据后缀 _sent 与三轨文本后缀 _ss 是两个正交概念空间 (前者银行与银行口径, 后者银行与金融科技词口径), 名称近似但严禁互相类推或复用原语。

## VAR: gf_liaison_win1

【变体差分】
本列为句窗判据变体 (criterion='win1', 后缀 _win1), tier=standard。与 canonical 列的唯一差分在建边判据: 两家银行须在同一篇文章内、句序号相距不超过 win_radius 的窗口内共同出现才成边, 窗宽由 config/panel.yaml 的 network_criteria.win_radius 键控制, 默认取一, 即相邻正负一句。须特别注意该键与 config/filtering.yaml 下 cooccurrence_filter.sentence_radius (stage 13 银行与金融科技词共现硬过滤的窗宽) 是两个互不联动的不同配置键, 尽管默认值相同, 改动任一不影响另一。实现与 _sent 列共用同一句级重扫路径与同一判据原语 (bank_pairs_within_sentence_window), 仅窗宽参数不同; 标题按 prepend_title 口径记为第零句参与开窗, 与 stage 13 标题参与匹配的口径镜像。严格性上本列居三档中间: 边集是同篇判据的子集、同句判据的超集, 图密度与 liaison 计数亦单调居中, 因而它是检验结论对建边口径单调稳健性的关键中间锚点 — 若系数形态在同篇、句窗、同句三档间单调漂移, 即提示结果由弱关联边驱动。判据分轨路径暂不支持超边归一化参数 (仅 article 主路径预留), 传入即显式报错, 防止三判据轨在无警告下口径分叉。GF 枚举逻辑、NFRA 分组、端点不直连约束、零对 NaN 双态缺失语义与 canonical 完全一致。铁律复述: 本列与无后缀及 _sent 列互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混入同一 over-identified Hansen J; 判据后缀与 _full/_ctx/_ss 三轨文本后缀正交, 不得混淆。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
<!-- rendered-citations:end -->
