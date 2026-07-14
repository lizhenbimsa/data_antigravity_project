---
family_id: F094
columns:
- bank_harmonic_cent
- bank_harmonic_cent_sent
- bank_harmonic_cent_win1
unit: 网络中心度 (无量纲; 倒数距离之和, networkx 原始值未按 n-1 归一化)
formula: "bank_harmonic_cent(u) = sum_{v != u} 1/d_Ginv(u,v); d_Ginv = 倒数权重图最短路距离, G_inv 边权 = 1/w, w = 年度银行对共现强度 (both-verified, docid 聚合, 每篇每无序对 +1); 实现 = networkx.harmonic_centrality(G_inv, distance='weight'); 不可达对贡献 0; 判据变体 {同篇 canonical 无后缀 / ±1 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (邻接构造 build_adjacency_matrix; 判据原语 core/text/entity_context.py; 面板 runner 步骤 7f/7g/7h)
upstream:
- 21_tone_llms.parquet (full-only 留篇门控 llm_verified_full==True 后的 article×bank 展开帧, docid 聚合)
- 40_panel_yearly.parquet (落列宿主面板)
- config/panel.yaml::network_criteria.win_radius (默认 1; 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1016/j.jeconom.2025.106130
  type: journal
  authors: Hughes, D. W.
  year: 2026
  title: "A jackknife bias correction for nonlinear network data models with fixed effects"
  venue: Journal of Econometrics
  vol: 253
  pages_or_artno: "106130"
- doi: 10.1080/00036846.2025.2476213
  type: journal
  authors: Zhang, X., & Li, Z.
  year: 2026
  title: "FinTech and branch network expansion: Evidence from China's banking industry"
  venue: Applied Economics
  vol: 58
  issue: 12
  pages_or_artno: 2321-2336
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
  pages_or_artno: "103223"
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: Article 102163
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: Article 2693
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
- doi: "10.1371/journal.pone.0335506"
  title: "Leaders in the global banking network: Analysis of the Bank for International Settlements network data"
  authors: "Bonato, A., Chavez Palan, J., & Szava, A."
  year: 2025
  venue: "PLOS One"
  type: "journal"
- doi: "10.3390/encyclopedia6010011"
  title: "Network Centrality and Information Cascades in Executive and Director Networks"
  authors: "Jiang, L., Rundo, J., Shi, L., & Zhou, N."
  year: 2026
  venue: "Encyclopedia"
  type: "journal"
new_dois:
  - "10.1371/journal.pone.0335506"
  - "10.3390/encyclopedia6010011"
---

## CORE

【构念与来源】
本家族测量的构念是目标银行在年度媒体共现网络中的信息可达性, 载体为调和中心度 (harmonic centrality)。所谓媒体共现网络, 指以银行为节点、以"同一篇新闻报道共同提及两家银行"为边的年度无向加权图: 若某年内一篇通过全套实体核验的报道同时确认提及银行甲与银行乙, 则甲乙之间的边权累加一次; 一年内共同被报道的文章越多, 两行之间的连接越强。调和中心度定义为节点到网络中其余所有节点的最短路距离之倒数逐一求和, 距离越近的对手方贡献越大, 完全不可达的对手方贡献恰好为零。直觉上, 这个量回答的是: 在该年度的银行业新闻叙事版图里, 这家银行距离其他所有银行有多近, 关于它的信息 (或关于其他银行的信息) 沿着媒体共同报道的渠道扩散到全网有多容易。用大白话说, 调和中心度高的银行是新闻叙事网络的"交通枢纽", 与网络中绝大多数银行只隔很少几步共同报道链条; 调和中心度低的银行则处在叙事版图的边缘, 甚至孤悬于主连通分量之外, 媒体谈论其他银行时几乎不会顺带谈到它。构念的学术源头有两支: 一支是社会网络分析对"接近性"这一维度的经典刻画, Freeman (1978) 把中心度厘清为度、中介、接近三个概念维度, 其中接近中心度捕捉节点抵达全网的平均效率; 另一支是对接近中心度在断连图上失效问题的公理化修正, Boldi 与 Vigna (2014) 系统提出中心度应满足的公理组 (规模单调性、密度公理、分数提升公理), 并证明在其考察的多种经典中心度中调和中心度是同时满足全部公理的测度, 从而为在天然断连、逐年重建的实证网络上使用调和中心度而非经典接近中心度提供了公理层面的依据。本家族选用调和中心度而非接近中心度作为路径可达类的稳健刻画, 正是因为年度银行共现网络在样本早期年份普遍存在多个连通分量与孤立节点, 接近中心度在断连图上要么无定义、要么依赖任意的分量内归一化约定, 而调和中心度对断连结构天然良定义。数据来源上, 本列不依赖任何外部网络数据库, 完全由本流水线的新闻语料内生构造: 上游是 stage 21 情感处理后的篇章级 article×bank 展开帧, 行宇宙受 full-only 留篇门控约束 (2026-06-29 口径: 一篇文章是否计入银行金科报道宇宙只看 llm_verified_full 是否为真), 边的两个端点银行都必须各自通过实体核验 (both-verified), 未通过核验的银行不入图、不成边。这一构造使得本家族与基于股权、担保、同业拆借等真实金融关联构造的银行网络 (如 Gao, Ru 与 Yang (2022) 的股权网络、Wang, Zhang 与 Yang (2020) 的中国担保网络) 在构念上明确分工: 本家族刻画的是信息与叙事层面的关联拓扑, 而非资产负债表层面的风险敞口拓扑。

【方法学与计算】
计算链路分三段: 邻接构造、倒数图变换、中心度求值。第一段由 build_adjacency_matrix 完成: 按年份切片篇章级展开帧, 节点全集取该年幸存的全部目标银行; 边权按 docid 聚合 — 文章 k 在帧中幸存的目标银行集合 (即全部通过核验的银行) 内, 每个无序对恰好使对称邻接矩阵双向各加一。这一 docid 聚合口径是 2026-06-11 边权审计修复后的统一口径, 修复前旧实现逐行解析 stage 11 的共提及字段, 同一文章的孪生行是否双双幸存会导致同一对银行被计一次或两次的混合污染, 且已被核验拒绝的银行仍可能以幻影边入网; 修复后每篇文章对每个无序对至多贡献一次, 幻影边被彻底排除。第二段是加权图到距离图的语义翻译: 共现次数是"强度"量纲 (越大越近), 而最短路算法消费的是"距离"量纲 (越小越近), 因此按 Opsahl, Agneessens 与 Skvoretz (2010) 处理加权网络最短路的标准做法, 对原始图取边权倒数得到 G_inv (边距离等于一除以共现次数), 共同报道越频繁的两家银行在 G_inv 上距离越短。全部路径型指标 (中介、调和、接近、离心率) 统一在 G_inv 上计算, 保证同族指标的距离语义一致。第三段调用 networkx 的 harmonic_centrality 函数, 传入 distance 参数指定按边权求最短路; 返回值是未经 n 减一归一化的原始倒数距离和, 不可达节点对贡献零, 孤立银行取值恰为零; 未出现在当年图中的银行按零回填 (与特征向量中心度对微小分量置缺失值的口径不同, 详见局限节)。判据维度上, 家族三列对应银行与银行共现判据的三档严格度: 无后缀列按"同篇"判据 (canonical, 现行生产口径), _win1 列要求两家银行出现在相距不超过 win_radius 句的句子里 (win_radius 取 config/panel.yaml 的 network_criteria.win_radius 键, 默认为一; 注意这与 stage 13 银行与金科共现过滤的 filtering.yaml sentence_radius 是两个互不联动的不同配置键), _sent 列要求严格同句。_win1 与 _sent 的边判定走 docid 组内句级文本重扫, 判据原语为 core/text/entity_context 模块的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 扫描文本采用 prepend_title 口径 (标题作为第零句参与扫描, 镜像 stage 13 的 match_in_title), 且与 stage 11、13 及 ctx/ss 物化共用同一否定与短名排除事实源 (禁裸 Aho-Corasick 匹配, 防"涉农行业"误命中"农行"一类假阳性); 仅含至少两家幸存银行的文章组才可能成边, 非幸存银行不进入原语入参, 幻影边防线在判据分轨路径同样成立。三档判据共享同一节点全集 (与同篇判据一致), 差别仅在边集: 判据越严边越稀疏, 因此调和中心度水平随判据收紧单调不升。工程执行环境上, 本家族在面板导出主 runner 的网络指标步骤内计算 (network_spillover 函数库, 对应日志阶段名 46_network_spillovers), 属纯 CPU 确定性计算、零 API 成本, 与同模块内需要付费嵌入的同业相似网络列在成本与依赖上完全隔离; networkx 缺失时全部中心度列优雅跳过而非报错, 使用者遇到整族缺列应首查依赖安装而非上游数据。逐年重建意味着每个银行年格点的取值只由当年语料决定, 不含任何跨年平滑, 网络结构的年际跳变会原样传导到本列。另有两处工程边界须记录: 其一, hyperedge_normalize 超边归一化参数目前仅同篇主路径实现, 判据分轨路径传真值会显式抛错, 防止三判据轨无警告地分叉口径; 其二, 本列是全仓九个 BLAS 浮点漂移非确定列之一 (三个基名乘三判据后缀), 跨次重建不保证逐位可复现, golden 零漂移验证按全名剔除这九列。

【文献定位】
本家族在文献坐标系中位于三条线的交点。第一条是网络测度方法学线: Freeman (1978) 奠定中心度三分类, Watts 与 Strogatz (1998) 的小世界结构分析使聚类与路径长度成为实证网络的标准刻画, Newman (2005) 用随机游走重构中介中心度提示"同一构念可有多种路径语义", Opsahl, Agneessens 与 Skvoretz (2010) 把度与最短路系统推广到加权网络 (本家族倒数权重建图直接承袭其框架), Boldi 与 Vigna (2014) 的公理化工作则是调和中心度取代接近中心度的直接理论依据。第二条是金融网络实证线: 金融文本挖掘方向上, Li, Yuan, Zhu, Emrouznejad, Hao 与 Jin (2026) 从文本风险披露中恢复金融机构网络结构与关联度, 与本家族"从新闻文本内生构造银行网络"的思路同属文本金融网络方法族; 资产定价方向上, Yu, Hu 与 Zhong (2024) 发现网络中心度通过信息扩散渠道影响资产定价, Xu 与 Zhao (2024) 检验金融网络节点中心度对资产价格预测的贡献, 二者共同支撑"中心度是信息扩散位置的有效代理"这一本家族的核心解释路径; 传染与系统性风险方向上, Sadeghi 与 Feinstein (2024) 提出金融网络传染中心度的统计检验框架, Khan, Hasan 与 Anupam (2024) 记录硅谷银行事件中社交媒体叙事沿银行网络的多米诺传导, 说明媒体叙事网络位置本身就是银行部门冲击传导研究的一手对象。第三条是中国银行业场景线: Wang, Zhang 与 Yang (2020) 刻画金融危机与刺激计划下中国担保网络的演化, Gao, Ru 与 Yang (2022) 证明股权网络在银行信贷中承担信息角色, Zhang 与 Li (2026) 研究金融科技冲击下中国银行业分支网络扩张, 三者共同说明中国银行体系的网络结构具有独立的信息含量与政策相关性, 为在中文银行新闻语料上构造网络测度提供场景合法性。跨学科证据方面, Nezami, Chisam 与 Palmatier (2025) 对网络中心度与企业绩效关系的元分析确认中心度对绩效的平均效应显著但高度依赖测度选择与网络类型, 这正是本家族把调和中心度与同族其他十七个节点级指标并排提供、而非独尊单一测度的文献理由。

【识别策略定位】
在计量识别链条中, 本家族三列的定位是结构位置控制变量与异质性调节变量, 而非任何一篇论文的主处理变量。三点定位须明确。第一, 内生性属性: 银行在新闻共现网络中的位置由媒体报道行为内生决定, 与银行规模、新闻热度、事件冲击同源, 直接把当期中心度放上回归右侧解释当期结果只有条件相关解释力; 项目内的同行溢出主规格因此采用严格滞后一年口径 (去年网络乘去年同行情感), 以规避 Manski 反射问题的机械同期性, 网络溢出效应的正式识别依据是 Bramoullé, Djebbari 与 Fortin (2009) 建立的通过网络局部结构差异识别同伴效应的条件, 更前沿的补充是 de Paula, Rasul 与 Souza (2024) 从面板数据本身识别网络连边的理论 (为"新闻共现边是否代理真实关联"提供可检验思路) 与 Hughes (2026) 对带固定效应的非线性网络模型的刀切偏差修正 (提示网络回归中附带参数偏差的处理方案)。Grieser, Hadlock, LeSage 与 Zekhnini (2022) 对公司金融政策网络效应的处理则示范了在承认网络内生的前提下用空间计量与工具变量组合作稳健推断的路径, 项目面板层的 IV 扩展 (同组留一均值、广义 Bartik、媒体来源风格暴露三引擎) 与之呼应。第二, 量纲与固定效应: 本列是节点级逐年重算的银行年变量, 在银行固定效应与年份固定效应下仍有组内变异, 可识别; 与之相对, 同族十个网络级年度指标是年内广播常量, 会被年份固定效应完全吸收, 使用时不可混淆层级。第三, 口径铁律: 家族内三判据变体 (同篇、句窗、同句) 是同一构念在判据严格度梯子上的三档测量, 各自 just-identified 并排、互为稳健性、不分主次, 绝对禁止把多档判据混进同一个 over-identified 的 Hansen J 检验; 判据后缀与情感三轨文本后缀 (full、ctx、ss, 银行与金科口径) 是两个正交概念空间, 同样禁止交叉混入同一过度识别系统。本家族所依赖的文章宇宙与 n_articles 分母遵循 full-only 留篇门控口径, 与全仓 2026-06-29 切换保持一致。补充一点识别层面的实务提示: 若研究者以本列作调节变量构造交互项 (例如检验高中心度银行是否对行业负面冲击反应更强), 应意识到中心度与银行可观测规模高度相关, 交互项的识别须同时纳入规模与处理变量的交互作为对照, 否则中心度交互可能只是规模交互的换装; 同理, 若以滞后中心度进入工具变量第一阶段, 排除性约束的论证必须直面"网络位置由历史报道内生"这一事实, 单凭滞后并不自动获得外生性, 更稳妥的做法是把网络位置留在控制集而把外生变异来源交给项目内已实现的三类 IV 引擎。

【与相邻测度的构念区分】
同族十八个节点级指标覆盖不同的"重要性"语义, 本列的独特构念边界须与近邻逐一划清。与接近中心度 (bank_closeness_cent) 的区别最细也最关键: 两者同在倒数图上刻画可达性, 但接近中心度是平均距离的倒数, 在断连图上依赖 networkx 的分量内归一化约定, 孤立分量内的小团体可能获得虚高取值; 调和中心度是倒数距离的和, 不可达对贡献零, 断连惩罚内生于定义, 无需任何约定 (Boldi 与 Vigna (2014) 的公理化对比正是围绕这一点)。与中介中心度 (bank_between_cent) 的区别是"位于通路上"与"离所有人近"的区别: 中介量桥梁地位 (多少最短路必须经过它), 调和量抵达效率; 一家挂在枢纽旁的卫星银行可以调和很高而中介近零。与电流中介 (bank_cfbetween_cent) 的区别在路径语义: 后者按 Newman (2005) 的随机游走电导语义在原始强度图上计算, 不走倒数图, 与本列不共享距离变换。与度和强度中心度 (bank_degree_cent, bank_strength_cent) 的区别是局部与全局: 度类只看直接邻居, 调和聚合全网最短路, 两家度数相同的银行可因所处分量规模不同而调和差异巨大。与特征向量和 Katz 中心度的区别是递归声望语义 (邻居的重要性加权) 对阵纯距离语义, 且特征向量列对微小连通分量置缺失值而本列对孤立节点置零, 缺失结构不同。与离心率 (bank_eccentricity) 的区别是最坏情形对阵调和平均: 离心率只看最远可达节点且仅对最大连通分量计算。最后, 本家族与判据无关的网络级列 (如年度密度、巨分量占比) 层级不同, 与 GF 经纪角色列 (Gould-Fernandez 分组经纪) 构念不同, 均不可替换使用。

【已知局限与稳健性梯子】
第一, 构念层局限: 新闻共现是叙事关联而非合约关联, 两家银行同篇出现可能因真实业务关联、同类政策冲击、也可能仅因编辑排版惯例 (行业综述例行罗列各大行); 因此本列应解释为信息叙事网络位置, 向资产负债表关联外推须谨慎, 并建议与 Gao, Ru 与 Yang (2022) 式股权网络或 Wang, Zhang 与 Yang (2020) 式担保网络证据互证。第二, 测量层局限: 边权由报道计数驱动, 大银行媒体覆盖高, 中心度与银行规模正相关是机械成分, 回归中须以银行固定效应与规模控制吸收; 调和中心度未归一化, 其水平随当年入网银行数与语料规模漂移, 跨年水平比较须依赖年份固定效应, 不宜直接比较原始水平。第三, 数值层局限: 本列属 BLAS 浮点漂移九列之一, 跨次重建非逐位可复现, 任何 golden 字节级校验须按全名剔除; 孤立银行取零而非缺失, 使用者若视"不在网络中"为信息缺失应自行掩码。第四, 开发环境退化: 当前盘上为两年开发切片, 网络逐年重建导致早年小网络上路径类指标方差压缩, 属预期退化, 生产十八年语料下正常。第五, 报告口径: 涉及本列的描述统计与回归系数一律由引擎在生成期注入动态统计段, 本文不手填任何面板实测数字; 判据梯子的三列建议在同一表内相邻列并排呈现以便读者直观比对判据敏感性方向。第六, 稳健性梯子: 家族内生的判据梯子 (同篇、句窗一、同句) 是主报告应并排展示的第一梯子, 三档各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 第二梯子是同族异构念指标并排 (调和对阵接近、中介、度), 检验结论是否被单一测度选择驱动, 呼应 Nezami, Chisam 与 Palmatier (2025) 元分析对测度依赖性的警示; 补充证据上, Bonato, Chavez Palan 与 Szava (2025, PLOS One) 提出对抗网络方法定位全球银行网络中的关键影响国家, 支撑本家族网络位置即信息与风险传导代理的解释路径, Jiang, Rundo, Shi 与 Zhou (2026, Encyclopedia) 系统梳理度、中介、接近、特征向量等中心度维度如何驱动高管与董事网络中的信息级联, 呼应本家族多测度并排而非独尊单一中心度的设计理由; 第三梯子是与情感三轨、co-primary 双轨嵌入等其他家族梯子的正交关系 — 各梯子之间不交叉组合、不进入同一过度识别系统, 主结论应在每一梯子内部单独复核。

## VAR: bank_harmonic_cent

【变体差分】
本列是家族 canonical 列, 采用同篇 (article) 判据且无后缀, 对应 NETWORK_METRIC_BASES 单一事实源中的基名本身, 亦是 2026-07-10 签核扩围后本家族唯一的 core 列。其精确语义为: 目标银行在当年同篇共现网络倒数图上的调和中心度原始值。邻接判据是三档梯子中最宽的一档 — 只要一篇通过 full-only 留篇门控且两端银行均通过实体核验的报道在全文任意位置 (含 prepend_title 后的标题) 同时提及两家银行, 该无序对的边权即按 docid 聚合累加一次, 不要求两行名出现在同一句或相邻句。因此本列的边集是 _win1 与 _sent 两个变体边集的超集, 网络最稠密、连通性最强、调和取值的截面水平在三档中最高; 判据收紧只会移除边而不会改变节点全集, 故三列间的水平差异纯粹来自边集严格度, 这是判据梯子可解释性的关键设计。作为 canonical 列, 它是全部下游消费场景的默认口径: Stata 导出中它挂接经典标签 (共现调和中心度), 同行溢出与结构异质性分析默认引用它, 判据变体仅作稳健性并排。与两个变体共享的实现细节在此列同样成立: 倒数图距离语义、不可达对零贡献、孤立与缺席银行按零回填、未按节点数归一化。使用注意有三: 其一, 本列在 memory 与源码双重登记为 BLAS 浮点漂移非确定列 (与聚类系数、电流中介两基名并列, 三基名乘三判据共九列), 跨次重建仅统计等价不保证逐位相等, 复现验证须按全名剔除; 其二, 因未归一化, 其量纲随年度入网银行数漂移, 任何跨年或跨样本比较必须经年份固定效应或标准化处理; 其三, 同篇判据下行业综述类报道会批量制造弱边, 若研究设计对"仪式性共提及"敏感, 应以 _sent 严格判据列做下界稳健性检验。本列与家族外近邻列 (接近中心度、中介中心度) 的构念区分见核心节, 引用时不可互相替换; 与三轨文本后缀列亦无任何对应关系 — 本列判据主体是银行与银行共现, 无 full、ctx、ss 变体, 也无 _lg 嵌入孪生 (非嵌入 carve-out)。在单一事实源治理上, 基名 bank_harmonic_cent 登记于 network_spillover 模块的三十三基名元组 (十八节点级、十网络级、五经纪角色), 本列属节点级 Part B 路径可达型组 (与中介、接近、离心率、核数、崩塌影响力、枢纽哨兵同组, 区别于 Part A 十一个度类与自我网结构指标); Stata 导出的判据变体标签机械块与 gate 测试均直接 import 该元组防漂移, 任何改名必须从该元组入手而非散点替换。分析定位上, 本列在同行溢出主规格中以严格滞后一年的形态参与网络加权 (去年结构乘去年同行情感, 规避反射问题的同期性), 当期值则主要用作结构位置控制与异质性切分变量; 网络级年度指标被年份固定效应吸收而本列不受此约束, 是家族中少数在双向固定效应下仍可识别的层级。开发切片下的预期形态亦须记录: 两年开发面板上入网银行少、单一巨分量未必形成, 本列出现大量零值与小分量内压缩取值属预期退化而非缺陷, 生产十八年语料下分布自然展开。最后给使用者一条实操建议: 在描述统计与回归表中报告本列时, 建议同时报告当年入网银行数与巨分量占比作背景量, 让读者能够判断中心度水平的年际变化中有多少来自网络规模本身的扩张; 若做跨行截面排序分析, 更稳妥的做法是先在年内做百分位或标准化变换再入模, 以剥离未归一化量纲随语料规模漂移的机械成分。

## VAR: bank_harmonic_cent_sent

【变体差分】
本列是判据梯子最严一档: 只有当两家均通过核验的银行出现在同一个句子内时, 该文章才为这对银行贡献一次边权。判据原语为 entity_context 模块的银行句位映射与句窗对提取 (窗口半径取零等价于严格同句), 扫描文本采用 prepend_title 口径, 标题被视作第零句参与同句判定, 镜像 stage 13 的 match_in_title 设计; 否定与短名排除与 stage 11、13 共用同一事实源, 防止裸字符串匹配的假阳性边。相对 canonical 同篇列, 本列边集是其子集且通常显著稀疏: 同句共提及基本剔除了行业综述式的仪式性罗列, 幸存的边更可能对应真实的成对叙事 (合作、并购、对比、传染), 因此本列可解释为高精度低召回的叙事关联网络, 调和中心度水平系统性低于 canonical 列, 断连分量更多、零值银行占比更高。节点全集与 canonical 一致 (当年全部幸存银行), 差异纯在边集。使用口径: 本列与无后缀及 _win1 列各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据后缀 _sent 与情感三轨的 _ss 后缀 (银行与金科同句) 是两个不同概念空间的判据, 后者主体是银行与金融科技词共现且属文本轨维度, 严禁混淆或互相复用判据原语。工程注意两点: 其一, codebook 的来源推断入口对本列先剥判据后缀再匹配, 防止列名中 sent 子串被误归入情感族; 其二, hyperedge_normalize 归一化在本判据路径未实现, 显式传真值会抛错, 属刻意的口径分叉防线。本列同为 BLAS 漂移九列之一, 复现校验按全名剔除。分析价值层面, 本列是判据梯子的严格下界锚: 若某一实证结论在最宽的同篇 canonical 列上成立而在本列上消失, 提示该结论可能被行业综述式的仪式性共提及批量弱边驱动, 属需要警惕的判据敏感性信号; 反之若结论在本高精度低召回列上依然稳健, 则可对"叙事关联位置"这一构念的因果解读给予更强信心。使用者据此把无后缀列与本列并排报告时, 二者水平差与符号一致性本身即是一项可读的稳健性证据, 但仍须恪守铁律: 两列各自 just-identified 并排、互为稳健性、不分主次, 绝不并入同一 over-identified 的 Hansen J 系统。开发切片下同句判据边极稀疏, 本列大量取零、方差被进一步压缩, 属预期退化, 生产十八年语料下同句成对叙事样本充足、分布自然展开。与家族外近邻列 (接近、中介、度、强度中心度) 的构念区分与 canonical 列同理, 不可互相替换; 本列判据主体是银行与银行同句共现, 无三轨文本后缀、无 _lg 嵌入孪生 (非嵌入 carve-out)。

## VAR: bank_harmonic_cent_win1

【变体差分】
本列是判据梯子的中间档: 两家均通过核验的银行出现在相距不超过 win_radius 句的句子内即成边, win_radius 由 config/panel.yaml 的 network_criteria.win_radius 键控制, 默认为一, 即允许相邻句共现; 列后缀中的数字一记录的正是该默认半径。须特别注意配置键的辨析: 这一键与 stage 13 银行金科共现硬过滤所用的 filtering.yaml 下 cooccurrence_filter.sentence_radius 是两个互不联动的独立配置键, 前者管银行与银行的网络判据, 后者管银行与金科的留篇过滤, 改动任何一个都不影响另一个。实现上本列与 _sent 列共走 docid 组内句级重扫路径: prepend_title 口径下标题为第零句, 与正文第一句相邻, 因此标题提及甲行、首句提及乙行的文章在本判据下成边而在严格同句判据下不成边; 否定与短名排除、幻影边防线、节点全集与另两列完全一致。构念上本列平衡精度与召回: 相邻句窗口既能捕捉跨句展开的成对叙事 (前句述甲、后句承乙的行文), 又过滤掉相隔全文的松散共提及, 边集严格介于同篇超集与同句子集之间, 调和中心度水平亦介于两档之间, 是检验结论对判据严格度单调敏感性的中间锚点。使用口径与家族铁律一致: 与无后缀 canonical 及 _sent 列各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; _win1 判据后缀与三轨文本后缀无对应关系, 不存在 full、ctx、ss 或 _lg 变体。本列同属 BLAS 浮点漂移九列, golden 验证按全名剔除; hyperedge_normalize 在本路径同样未实现、传真值抛错。分析定位上, 本列作为梯子中间锚具有独特诊断价值: 在同篇超集与同句子集之间, 若调和中心度的实证效应随判据从宽到严呈单调变化, 三列并排即勾勒出一条清晰的判据敏感性曲线, 中间档取值提供曲线的转折信息, 帮助研究者判断结论对"共提及紧密度"这一维度的依赖程度; 若三档取值与效应大体平行, 则说明结论不被判据严格度驱动, 稳健性证据更强。使用时仍须谨记铁律: 三档判据各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J; 判据后缀空间与情感三轨 full、ctx、ss 后缀空间正交, 严禁交叉组合入同一过度识别系统。本列不存在三轨文本变体, 也无 co-primary 双轨嵌入的 _lg 孪生, 因其判据主体是银行与银行共现拓扑而非任何嵌入或情感测度。开发切片下相邻句窗边数介于同篇与同句之间, 早年小网络上仍可能出现路径类指标方差压缩, 属预期退化, 生产语料下正常。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Zhang, X., & Li, Z. (2026). FinTech and branch network expansion: Evidence from China's banking industry. Applied Economics, 58(12), 2321-2336. https://doi.org/10.1080/00036846.2025.2476213
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, Article 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, Article 2693. https://doi.org/10.1038/s41467-020-16535-8
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonato, A., Chavez Palan, J., & Szava, A. (2025). Leaders in the global banking network: Analysis of the Bank for International Settlements network data. PLOS One. https://doi.org/10.1371/journal.pone.0335506
Jiang, L., Rundo, J., Shi, L., & Zhou, N. (2026). Network Centrality and Information Cascades in Executive and Director Networks. Encyclopedia. https://doi.org/10.3390/encyclopedia6010011
<!-- rendered-citations:end -->
