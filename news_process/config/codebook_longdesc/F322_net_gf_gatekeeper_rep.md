---
family_id: F322
columns:
- gf_gatekeeper_rep
- gf_gatekeeper_rep_sent
- gf_gatekeeper_rep_win1
unit: 非负整数计数 (2-path 经纪次数; 落列 dtype=double, 分组缺失时 NaN)
formula: "gf_gatekeeper_rep(i) = #{无序邻居对 (a,c): a,c ∈ N(i), a-c 无直连边, 且 g(a)、g(c) 中恰有一个等于 g(i)}; 年度银行共现无向图上按银行类型分组 g ∈ {soe, joint, city, rural, private, foreign, other} 计数; 判据变体 = 同篇 (无后缀) / ±1 句窗 (_win1) / 严格同句 (_sent)"
producer: news_process/pipeline/panel/network_spillover.py::_gould_fernandez_roles (经 compute_bank_network_centrality Part E 挂载; 判据透传 build_adjacency_matrix); Stata 标签见 pipeline/panel/export.py
upstream:
- 21_tone_llms.parquet (llm_verified_full 留篇门控后的篇章级展开帧 df_exploded, both-verified docid 聚合)
- config/bank_addresses.json 等银行分组事实源 (经 pipeline/panel/iv_did.py::load_bank_group_maps 加载 type_map)
- config/panel.yaml::network_criteria.win_radius (_win1 判据句窗半径, 默认 1)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
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
  pages_or_artno: 883-937
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
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: "103223"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
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
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: "10.3934/dsfe.2025021"
  title: "Statistical analysis and applications of financial network data in the era of digital intelligence"
  authors: "Deng, Y., Lu, M., Zhou, X., Qi, Y., & Ouyang, Z."
  year: 2025
  venue: "Data Science in Finance and Economics"
  type: "journal"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1016/j.procs.2023.08.056"
  - "10.3934/dsfe.2025021"
---

## CORE

【构念与来源】
本家族测度的构念是银行在媒体报道共现网络中的守门人兼代表经纪角色强度, 学理源头是 Gould 与 Fernandez (1989) 提出的经纪角色形式化分解框架。该框架的核心洞见是: 网络中介并非单一同质构念, 中介者与被中介双方的群体归属关系决定了中介的社会学含义。在原始的有向交易网络定义中, 一条二步路径 a 经 i 到 c 按三个节点的群归属组合分为五类角色: 协调人 (三者同群)、巡回经纪 (两端同群而中介者异群)、守门人 (信息流入中介者所在群, 即终点与中介者同群)、代表 (信息流出中介者所在群, 即起点与中介者同群)、联络人 (三者互异群)。本项目的银行共现图是严格无向图, 每条二步路径即其自身的逆路径, 守门人与代表两个角色在无向图上机械坍缩为完全共线的同一计数, 因此生产代码将二者合并为单列 gf_gatekeeper_rep, 家族落地为四个可区分角色加合计列的体系, 本家族即其中的守门人兼代表列及其两个判据变体。直观地讲, 该列回答的问题是: 当媒体在同一叙事单元内把两家银行并置报道时, 目标银行有多少次充当了本群体与外群体之间的单向边界接口, 即报道叙事把它与一家同类型银行和一家异类型银行同时串联、而那两家银行彼此并不直接共现。分组事实源复用生产单源 load_bank_group_maps 的银行类型映射, 类型空间为国有大行、股份制、城商行、农商行、民营、外资与其他七类, 与 iv_did 模块的同组均值、组内留一均值等构造共用同一分组口径, 保证跨模块分组语义一致。数据来源是经 llm_verified_full 留篇门控 (full-only 口径, 2026-06-29) 后的篇章级展开帧: 只有大模型验证确为银行金融科技报道的文章才进入建网宇宙, 边的原始语义是两家银行在同一篇幸存报道中均通过验证地被共同提及。用大白话概括本列在量什么: 想象每年把全部银行金融科技报道摊开, 凡两家银行被同一篇报道 (或更严判据下同一句、相邻句) 点名就在它们之间连一根线, 得到一张年度银行关系草图; 然后问某家银行, 在它认识的银行里, 有多少对是一家跟它同类、一家跟它不同类、而那两家彼此又不认识的组合, 每找到一对就给它记一分, 这个分数就是守门人兼代表计数。分数高意味着媒体叙事经常把这家银行放在本群体与外部世界的接缝上: 外部信息要进入它所在的群体、或群体的声音要传出去, 叙事路径都绕不开它。这为什么重要: 银行业的风险传染、创新扩散与监管信号传导都沿着此类叙事与认知通道行走, 处在接缝位置的银行既最先接触跨群冲击也最有条件套利跨群信息差, 该位置本身就是一种需要被测量的经济资源与风险暴露。

【方法学与计算】
计算分三层。第一层建网: build_adjacency_matrix 按年份切片篇章级展开帧, 以 docid 聚合每篇文章幸存的 target_bank 集合, 集合内每个无序银行对贡献一次对称加权, 即同一篇文章对任一银行对恰计一次, 这一 both-verified 聚合口径修复了旧实现中孪生行双计与幻影边两类缺陷 (fix 2026-06-11): 旧口径逐行解析 co_mentioned_banks 时, 同篇两行都幸存的对会被计两次, 且该字段仍列出验证已拒绝的银行, 使未通过验证的银行以边端点身份混入网络。节点全集为该年幸存 target_bank 全体, 含孤立节点。第二层是判据分轨 (2026-07-03 构造判据敏感性扩展): 无后缀 canonical 列采用同篇共现判据; _win1 与 _sent 变体在 docid 组内对标题加正文做句级重扫, 扫描文本为 prepend_title 物化文本且标题记为第零句, 镜像 stage 13 的 match_in_title 口径, 仅当两家银行的可信提及位置落在正负句窗半径之内 (win1, 半径取 config/panel.yaml 下 network_criteria.win_radius, 默认一) 或严格同句 (sent) 才成边; 句级重扫复用与 stage 11 及 13 相同的否定与短名排除事实源, 禁止裸自动机匹配, 以防涉农行业误判为农业银行一类的假阳性; 三判据下节点全集一致, 仅边集单调收紧。第三层是角色计数: _gould_fernandez_roles 对每个有分组的银行 i, 按字典序枚举其邻居中的无序对, 仅保留两端点彼此无直连边的对 (经典 GF 铁律, 保证 a 确须经 i 才能到达 c), 再按三方群归属归类, 当两端点中恰有一个与 i 同群时向 gf_gatekeeper_rep 计一。端点直连排除条款使该测度对文章级 clique 投影天然鲁棒: 一篇同时点名多家银行的报道会把这些银行投影成完全子图, 完全子图内部任意端点对彼此直连, 经纪计数恒为零, 故单篇大合辑报道不会虚增经纪角色。计数对无序对唯一计数, 不重复累加正逆两个方向, 与无向坍缩语义配套。缺失语义刻意区分两种零: 银行有分组但无可用二步路径 (孤立、邻居全直连或邻居全缺分组) 记零, 表示真实的零经纪; 银行分组缺失记 NaN, 表示不可计算, 下游回归须区分零经纪与未知, 该约定与 bank_constraint 等结构洞列一致。整条计数链路是纯整数比较与计数, 不涉线性代数, 不在 BLAS 浮点漂移的九列非确定清单内, 跨次重建逐位可复现; 邻居枚举按银行名字典序进行, 保证遍历顺序确定, 这是 golden 复现体系对本族的工程要求。落列侧的工程细节: compute_bank_network_centrality 按年循环建图后一次性计算三十三个结构指标并以银行年键左连回面板, 未出现在当年网络中的银行年格自然缺失; 判据与后缀在函数入口强制配套校验, article 对空后缀、win1 对 _win1、sent 对 _sent, 错配即抛异常终止, 封死判据与列名错位这一类静默污染路径; 分组映射在全年循环外一次性加载并复用, 加载失败时全年 gf 族列优雅置 NaN 且落 WARNING 日志, 绝不静默置零冒充真实零经纪。Stata 导出层为本列写入英文变量标签并标注无向合并语义, 三个判据变体的标签由判据机械派生循环统一追加判据说明, 防止 dta 消费端把变体误读为独立构念。

【文献定位】
在方法文献中, Gould 与 Fernandez (1989) 的角色分解至今仍是经纪测量的规范起点, Zádor 等 (2022) 将其推广到加权与归一化情形并系统讨论了原始计数对度数与群规模的敏感性, 本项目 canonical 口径保留原始未归一计数以维持可加分解与守恒关系, 归一化关切转由回归侧的规模控制与固定效应吸收。在金融经济学应用侧, Han 等 (2024) 证明机构经纪网络位置影响流动性供给, Grieser 等 (2022) 发现公司金融政策存在网络传导, Jackson 与 Pernoud (2021) 综述了金融网络中系统性风险如何依赖拓扑位置, 三者共同支撑网络经纪位置在银行研究中的经济意义。信息扩散机制侧, Hirshleifer 等 (2025) 刻画新闻在社交网络中的扩散如何驱动市场反应, Yu 等 (2024) 证明网络中心度经由信息扩散渠道进入资产定价, Cookson 等 (2026) 则给出社交媒体网络放大银行挤兑的极端案例, 说明媒体叙事网络中的位置对银行稳定性并非中性。中国语境下, You 等 (2018) 证明中国媒体的报道权力结构影响公司治理效果, Fang 等 (2024) 直接把媒体情绪与中国银行系统性风险及存款稳定性联系起来, Xu (2024) 则提醒记者社交网络本身会引入报道偏差, 为本项目以媒体共现构造银行网络的做法同时提供了合理性与测量误差两方面的文献坐标。文本驱动的网络构造范式另见 Li 等 (2026) 从风险披露文本恢复金融网络结构的工作, 与本家族从新闻共现恢复银行叙事网络思想同源。Freeman (1978) 的中心度概念澄清是全部节点级指标的公共前提, 本家族与其的区别见构念区分段。Deng, Lu, Zhou, Qi, & Ouyang (2025, Data Science in Finance and Economics) 综述数字智能时代金融网络数据的统计分析方法与应用, 为本家族基于共现网络刻画银行结构位置的方法论提供最新文献坐标。

【识别策略定位】
本家族在计量体系中定位为网络结构解释变量与机制刻画变量, 而非处理变量本身: 各论文主轨处理变量是情感与属性测度 (如 llm_vote_tone_full), gf_gatekeeper_rep 用于刻画银行在媒体叙事网络中的结构位置如何调节信息冲击的传导, 或作为溢出回归的异质性切片维度。以网络自变量入回归的根本威胁是 Manski 型反射问题与网络内生形成, Bramoullé 等 (2009) 给出的经典结果是二步邻居特征可在网络部分传递条件下识别同伴效应, 本 pipeline 的 brokerage 2SLS 规格正是以二阶滞后同伴情感作工具、以经纪位置刻画传导强度的该思路落地; de Paula 等 (2024) 进一步表明网络连边本身可从面板数据识别, 为共现边的测量效度提供计量理论支撑。判据梯子在识别层面的功能是排除建网自由度驱动结果的质疑: 同篇、句窗与同句三判据对应共现语义由宽到严的三个横断面, 若经纪效应仅在最宽判据下显现而在句级判据下消失, 则更可能反映长文列举噪声而非真实叙事关联。铁律必须复述: 三个判据变体各自 just-identified 并排、互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J; 该口径与三轨文本、co-primary 双轨嵌入、词典消融与政治词权重梯子的并排原则完全同构。判据后缀与三轨文本后缀是两个正交概念空间: 判据主体是银行与银行的共现关系, 三轨主体是银行与金融科技词的共现关系, 二者不可互换也不可交叉嵌套。年度网络逐年重建, 网络级量在年固定效应下不可识别, 但节点级的 gf_gatekeeper_rep 在银行与年双固定效应下仍有组内变异, 来源是银行逐年在叙事网络中角色位置的迁移。还须说明本列与处理变量及结局变量的边界: 本列不承担因果处理的角色声称, 其识别贡献在于条件化与机制切分, 典型规格是把守门经纪计数与情感处理变量交乘, 检验负面冲击是否在边界接口银行处呈现更强的跨群外溢, 或按经纪计数高低分样本对比传导系数; 由于共现网络由报道生成、报道又受银行基本面驱动, 网络位置与残差项的相关性无法先验排除, 涉及网络位置本身因果效应的表述一律须降格为条件相关或以工具变量策略另行处理, pipeline 内置的组内留一均值、广义 Bartik 与媒体来源风格暴露三类 IV 引擎为此提供了备选工具集。

【与相邻测度的构念区分】
第一, 与同模块 Bonacich 特征向量类声望测度 (bank_eigen_cent、bank_katz_cent) 的区分是生产注释中明示的动机区分: 声望测度回答邻居本身重不重要, 经纪测度回答是否真实跨群桥接, 一家只与国有大行密集互联的股份制银行可以声望极高而守门经纪为零。第二, 与 Freeman (1978) 谱系的介数中心度 (bank_between_cent) 区分: 介数计最短路径穿越次数, 对群归属无感知, 而 GF 分解的全部信息量恰在群归属组合上; 介数高而 gf_gatekeeper_rep 低的银行是群内枢纽, 反之是边界接口。第三, 与 Burt 结构洞族 (bank_constraint、bank_effective_size、bank_ego_density、bank_ci) 区分: 结构洞测度刻画自我网络的冗余度, 不区分洞两侧的群体身份, Burt (2004) 的好点子机制并不要求跨越的是制度类型边界; GF 守门人计数则要求恰好一侧同群, 是带方向语义 (在无向坍缩意义下为边界接口语义) 的结构洞细分。第四, 与家族内三个兄弟角色区分: 协调人是群内中介 (三方同群), 巡回经纪是被外群借用的中介 (两端同群而自身异群), 联络人是三群互异的纯外部中介, 守门人兼代表则是唯一一侧在群内一侧在群外的角色, 四者互斥且加总恰为 gf_total, 该守恒关系由单元测试锚定。第五, 与二分图经纪族 (brok_bip_between_cent 等) 区分: 后者建在媒体与银行的二模图上, 中介对象是媒体渠道; 本家族建在银行单模投影上, 中介对象是银行类型群体, 图基底不同, 不可互相替代。Nezami 等 (2025) 的元分析表明不同中心度构念对绩效的效应量存在系统差异, 混用构念是该文献中已被点名的常见错误。

【已知局限与稳健性梯子】
第一, 共现边是叙事关联的代理而非真实业务往来, 报道把两家银行并置可能出于同业比较、监管事件列举等与经纪无关的原因; 句级判据梯子部分缓解列举噪声, 但无法根除叙事性共现与关系性共现的构念间隙, 论文写作须将其表述为媒体叙事网络中的角色而非银行间真实交易网络中的角色。第二, GF 计数对群划分定义敏感: 七类银行类型是制度性分类, 若换用规模分箱或地域分组, 角色计数将系统改变, 该敏感性属构念定义层而非测量误差层, 当前版本未落地替代分组梯子。第三, 原始计数随节点度数平方级增长, 大行机械占优, Zádor 等 (2022) 的归一化批评适用于此, 回归侧须以度中心度或规模控制搭配使用, 或以银行固定效应吸收水平差异。第四, 缺失语义的零与 NaN 区分要求下游显式处理: 分组事实源加载失败时全列优雅置 NaN 并落 WARNING 日志, 不会静默置零。第五, 开发盘上 T 等于 2 的两年切片使年度网络稀疏, 判据收紧后句级变体在小样本上可能大面积为零, 属预期退化, 生产 T 等于 18 全量语料下方有正常变异。稳健性梯子的完整形态: 判据三臂 (无后缀、_win1、_sent) 各自 just-identified 并排, 互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与情感侧三轨、双轨嵌入、per-model 等梯子正交, 不做交叉组合以避免规格空间爆炸; 本族与网络指标家族的其余判据分轨列共用 NETWORK_METRIC_BASES 单源清单, 由 gate 测试锁定基名集合防漂移。留篇门控口径与全仓一致: 建网宇宙以 llm_verified_full 为唯一门控, n_articles 等分母量同受 full-only 口径约束, 判据重扫只改变边的成立条件, 不改变留篇集合。第六, 无向坍缩本身是信息损失: 原始 GF 框架中守门人与代表分别对应信息流入与流出群体边界, 方向语义在共现图上不可恢复, 因为一篇报道并置两家银行不携带信息流向; 若未来引入引用链或转载链等带向数据源, 守门与代表可重新拆分, 届时本列应作为二者之和的向后兼容锚而非被直接替换。第七, 分组粒度与网络稀疏度存在交互: 判据收紧使边变稀后, 满足端点不直连且分组齐备的二步路径进一步减少, 严判据臂的组间变异可能不足以支撑分组交乘规格, 使用者应先查有效非零格数再决定规格深度, 而非机械套用 canonical 臂的规格。

## VAR: gf_gatekeeper_rep

【变体差分】
本列是家族 canonical 列, tier 为 core, 采用同篇共现判据 (article, 无后缀即判据空间的历史命名产物, 非语义上的主), 是 2026-07-03 判据分轨扩展前的现行生产口径的直接延续, 也是 NETWORK_METRIC_BASES 单源清单中 Part E 五个 GF 经纪角色基名之一。其精确语义: 对年度银行共现无向图中每个有类型分组的银行 i, 计其邻居集中满足三个条件的无序端点对数目, 一是两端点都与 i 直接相邻 (即构成经 i 的二步路径), 二是两端点彼此无直连边 (经典 GF 端点不直连铁律, 保证中介地位真实不可绕过), 三是两端点的银行类型中恰有一个与 i 同型。同篇判据下, 边的成立条件最宽: 两家银行只要在同一篇通过 full-only 留篇门控的报道中均以 both-verified 身份出现即成边, 每篇文章对每个无序银行对恰贡献一次权重; 但须注意 GF 角色计数消费的是边的存在性而非权重大小, 共现强度信息由 bank_strength_cent 等加权指标承载, 本列对同一银行对报道频次不敏感, 这一设计使角色计数保持 Gould 与 Fernandez (1989) 原始定义的整数可分解性, 与三个兄弟角色列加总恰等于 gf_total 的守恒关系由测试锚定。作为 core 列, 其在论文体系中的承重位置是媒体叙事网络机制刻画的规范入口: 当研究问题涉及信息冲击如何跨银行类型边界传导时, 本列即边界接口强度的一阶测度, 与协调人列 (群内消化) 和联络人列 (纯外部中转) 构成互斥的机制三分。回归使用须搭配的口径约束: 与 _win1、_sent 两个判据变体各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀是正交概念空间, 本列虽无文本轨后缀, 其建网宇宙仍由 full 轨门控唯一决定。缺失语义: 分组缺失记 NaN, 有分组无二步路径记零, 二者不可混同; 本列为纯整数计数链路产物, 不在 BLAS 非确定九列清单内, 逐位可复现。选它作 canonical 的理由值得写明: 同篇判据是判据分轨扩展前唯一的历史生产口径, 全部既有 golden 锚、论文规格与下游模板都锚定在该口径上, 分轨扩展遵循加性铁律零改动存量列, 因此无后缀列的 canonical 地位是连续性约定而非严劣排序的结论; 同篇口径同时也是三臂中统计功效最高的一臂, 边最密、非零经纪格最多, 在开发期小切片上是唯一有稳定变异的臂。与兄弟角色列的搭配使用规范: 四个角色列可加分解 gf_total, 若回归同时纳入四列与合计列会产生精确共线, 正确做法是纳入四角色列省略合计, 或纳入合计列加至多三个角色份额; 若研究问题只关心跨群边界机制, 单独使用本列并以 gf_total 或度中心度控制总经纪规模是最简洁的规格。解释系数时的量纲提醒: 本列是未归一化的原始计数, 量纲随网络规模与银行度数膨胀, 跨年比较水平值无意义, 系数解释应基于组内标准化或对数变换后的相对变异, 与 BERT 族跨模型比较须标准化 β 的仓内先例同理。落地工程侧还须重申两点承重约定, 以免下游误用本 canonical 列。其一是判据与后缀在生产函数入口的强制配套校验: 本列作为无后缀 article 判据列, 只接受空后缀参数, 若调用方错传 _win1 或 _sent 后缀却指向同篇邻接矩阵, 函数即抛异常终止而非静默返回错值, 这一 fail-loud 设计封死了 canonical 口径被误当句级口径消费的污染路径, 是本列取值可信的前提。其二是本列与开发切片规模的交互提醒: 盘上 T 等于 2 的两年切片虽使年度网络稀疏, 但同篇判据是三臂中边最密的一臂, 本列在小切片上仍常有非零变异, 是三臂中唯一能在开发期支撑分组交乘规格试跑的一臂; 生产 T 等于 18 全量语料下, 本列的组间变异随语料密度进一步展开, 届时才应把句级两臂一并纳入判据梯子做完整稳健性对照, 而非在开发期因两严臂大面积为零就误判梯子失效。综上, 本列既是家族语义的规范锚, 也是全部既有 golden 快照、论文规格与 Stata 模板的历史锚定口径, 对其任何改动都须走加性铁律零改动存量列的路径, 判据分轨扩展正是遵此原则在不触碰本列取值的前提下追加两个句级兄弟变体的。

## VAR: gf_gatekeeper_rep_sent

【变体差分】
本列是严格同句判据变体 (_sent 后缀), 家族三判据梯子中最严的一臂。与 canonical 同篇判据的唯一差分在边的成立条件: 两家银行不仅须在同一篇留篇报道中均通过验证, 还须在 docid 组内句级重扫中存在至少一个句子同时包含两家银行的可信提及, 扫描文本为 prepend_title 物化的标题加正文且标题记为第零句 (镜像 stage 13 的 match_in_title 口径), 提及判定复用与 stage 11 及 13 相同的否定与短名排除事实源, 禁裸自动机匹配。节点全集与 canonical 完全一致 (同年幸存 target_bank 全体), 仅边集严格收紧为 canonical 边集的子集, 因此本列取值逐行不大于同年同行的 canonical 列在同一图局部结构下的对应量级, 但因端点不直连条款的存在, 边集收紧对经纪计数的影响并非单调: 删边既可能消灭二步路径 (计数下降) 也可能拆开原本直连的端点对使其转为可计的经纪对 (计数上升), 故不可先验断言本列小于 canonical。其构念定位是排除列举噪声的最强试金石: 同句并置是记者显式建立两行叙事关联的最强文本证据, 若 canonical 下的经纪效应在本列下方向一致, 则叙事关联解释得到强化。铁律: 与无后缀及 _win1 两臂各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 判据后缀 (银行与银行口径) 与三轨文本后缀 (银行与金科口径) 是两个正交概念空间, _sent 与 _ss 虽同为句级语义但主体不同, 禁互相复用原语。开发 T 等于 2 切片上本列大面积为零属预期退化, 生产全量下有正常变异。

## VAR: gf_gatekeeper_rep_win1

【变体差分】
本列是正负一句窗判据变体 (_win1 后缀), 家族三判据梯子的中间臂, 严格程度介于同篇与同句之间。与 canonical 的差分同样只在边的成立条件: docid 组内句级重扫要求两家银行的可信提及位置句距不超过 win_radius (取 config/panel.yaml 下 network_criteria.win_radius, 默认一, 即相邻句以内; 该键与 stage 13 银行金科共现过滤的 filtering.yaml 下 sentence_radius 是两个不同配置键, 互不联动, 勿混改), 扫描与排除口径与 _sent 变体完全一致 (prepend_title 标题为第零句、否定与短名排除事实源共用), 节点全集不变仅边集收紧, 且 _sent 边集是本列边集的子集。中间臂的方法学价值在于刻画剂量反应形态: 中文财经报道常以相邻两句完成一组银行间对比 (前句述甲行后句述乙行), 严格同句判据会漏掉这类真实叙事关联, 同篇判据又会纳入长文末尾的机械列举, 句窗判据恰居其中, 若三臂系数呈单调梯度则支持叙事关联强度与经纪效应的剂量解释, 若中间臂与两端断裂则提示特定判据下的测量伪影。与 _sent 变体相同, 端点不直连条款使边集收紧对经纪计数的影响不保证单调, 三臂间不可做数值大小的先验排序。铁律照录: 三判据各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 判据变体属规格稳健性并排, 镜像政治词权重与词典消融先例, 不设跨臂 FWER 模板; 判据后缀与三轨文本后缀正交, 不交叉嵌套。缺失与零的语义、整数计数的逐位可复现性均与 canonical 列一致。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Deng, Y., Lu, M., Zhou, X., Qi, Y., & Ouyang, Z. (2025). Statistical analysis and applications of financial network data in the era of digital intelligence. Data Science in Finance and Economics. https://doi.org/10.3934/dsfe.2025021
<!-- rendered-citations:end -->
