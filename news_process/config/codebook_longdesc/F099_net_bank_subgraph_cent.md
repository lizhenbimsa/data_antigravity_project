---
family_id: F099
columns:
- bank_subgraph_cent
- bank_subgraph_cent_sent
- bank_subgraph_cent_win1
unit: 子图中心度 (subgraph centrality, 闭合游走加权和, 无量纲, 下界 1 于孤立节点)
formula: "SC_i = [exp(A)]_ii = Σ_j (v_j^i)^2 · e^{λ_j}; A = 年度银行共现网络的无权邻接矩阵 (nx.subgraph_centrality 不消费边权); 判据变体 = 银行∧银行共现判据 {同篇 canonical 无后缀 / ±1 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (Part A 第 7 项; 基名 SSOT = NETWORK_METRIC_BASES)
upstream:
- 11_news_bank.parquet (docid + co_mentioned_banks 降级兜底)
- 13_cooccurrence_filter.parquet (银行∧金科共现硬过滤后的文章宇宙)
- 40_article_bank_level (article × bank 展开帧 df_exploded)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1007/s10614-025-11287-3"
  type: "journal"
  authors: "Akgüller, Ö., & Balcı, M. A."
  year: 2026
  title: "Detecting Financial Contagion Through Higher-Order Networks: A Deep Learning Approach to Emerging Market Risk"
  venue: "Computational Economics"
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
  pages_or_artno: "102163"
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: "2691-2729"
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
- doi: 10.1103/PhysRevE.71.056103
  type: journal
  authors: Estrada, E., & Rodríguez-Velázquez, J. A.
  year: 2005
  title: "Subgraph centrality in complex networks"
  venue: Physical Review E
  vol: 71
  issue: 5
  pages_or_artno: "Article 056103"
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: "39-54"
- doi: 10.1007/978-3-540-31856-9_44
  type: book
  authors: Brandes, U., & Fleischer, D.
  year: 2005
  title: "Centrality measures based on current flow"
  venue: "STACS 2005 (Lecture Notes in Computer Science, Vol. 3404), Springer"
  pages_or_artno: "533-544"
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: "440-442"
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: "1170-1182"
- doi: 10.1016/0378-8733(83)90028-X
  type: journal
  authors: Seidman, S. B.
  year: 1983
  title: "Network structure and minimum degree"
  venue: Social Networks
  vol: 5
  issue: 3
  pages_or_artno: "269-287"
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: "215-239"
- doi: "10.1371/journal.pone.0335506"
  type: journal
  authors: "Bonato, A., Chavez Palan, J., & Szava, A."
  year: 2025
  title: "Leaders in the global banking network: Analysis of the Bank for International Settlements network data"
  venue: "PLOS ONE"
- doi: "10.1007/s11424-025-4338-6"
  title: "The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes"
  authors: "Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X."
  year: 2025
  venue: "Journal of Systems Science and Complexity"
  type: "journal"
- doi: "10.1016/j.najef.2024.102307"
  title: "Text Spillover: Measuring connectedness of financial institutions based on news text data"
  authors: "Klaucke, K."
  year: 2025
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
new_dois:
- "10.1007/s10614-025-11287-3"
- "10.1371/journal.pone.0335506"
- "10.1007/s11424-025-4338-6"
- "10.1016/j.najef.2024.102307"
---

## CORE

该文用高阶网络(超越简单成对连接的拓扑结构,与子图中心度所刻画的闭合游走/圈层嵌入构念相呼应)与深度学习方法检测新兴市场金融网络中的传染风险。

【构念与来源】
子图中心度 (subgraph centrality) 度量的是一家银行在年度银行共现网络中参与「闭合游走」(closed walk, 即从自身出发又回到自身的路径) 的加权总量, 其构念内核可以用一句大白话概括: 一家银行不仅要看它直接被和多少同业一起报道 (度中心度回答的问题), 更要看它嵌入了多少大大小小的「圈子」— 三角形、四边形乃至更高阶的稠密子结构。参与的闭合结构越多、越短, 该银行在媒体叙事版图中的位置就越「核心」。该测度由 Estrada 与 Rodríguez-Velázquez (2005) 在复杂网络物理学文献中提出, 其数学定义为邻接矩阵指数的对角元: 节点 i 的子图中心度等于 exp(A) 矩阵的第 i 个对角元, 谱形式等于对全部特征值 λ_j 求和的 (v_j 第 i 分量)^2 乘 e^{λ_j}, 其中 v_j 是对应特征向量。由于长度为 k 的闭合游走在矩阵指数展开中被 1/k! 阶乘衰减加权, 短闭合游走 (三角形、四元环) 的贡献占绝对主导, 这使子图中心度天然强调「局部稠密嵌入」而非「全局可达性」, 与最短路径类测度 (介数、接近度) 和长游走极限类测度 (特征向量中心度) 形成互补的构念光谱。Boldi 与 Vigna (2014) 的中心度公理化体系亦将其归入谱类 (spectral) 测度并讨论了其与其他家族在单调性、密度敏感性公理上的差异, 为本仓在 33 个结构指标中并置多族中心度提供了理论依据 — 没有任何单一中心度在全部公理下占优, 并排报告是方法论上的必然选择。本家族的数据来源是本项目自建的中文银行新闻语料: 经 stage 11 银行实体识别 (否定过滤 + 短名排除, 防「涉农行业」误命中「农行」一类假阳性)、stage 13 银行∧金融科技邻近共现硬过滤后留存的报道集, 按 article × bank 展开为 df_exploded 帧, 再在每个年度截面上把「同一篇报道中共同被提及的银行对」连成边, 边权为该年度内共现篇数 (每篇文章每个银行对计一次, 按 docid 去重, 不受同篇内重复提及次数干扰)。节点集为银行清单全体, 孤立银行 (当年零共现) 亦被显式加入图中。这一「文本共现即连边」的建网思路承接 Hoberg 与 Phillips (2016) 用产品文本相似度构造企业网络的范式, 以及 Li 等 (2026) 从风险披露文本还原金融网络结构与关联度的近期实践: 当真实的银行间敞口 (同业拆借、支付清算) 数据不可得或不公开时, 媒体叙事网络提供了一个可观测、可复现、逐年更新的位置代理。用大白话把这三层来源串起来: 我们先从海量中文财经报道里认出每篇文章提到了哪些银行 (并小心排除否定语境和短名误伤), 只留下真正谈论银行与金融科技交叉话题的报道, 然后把「同一篇文章里一起出现」当作两家银行之间的一条线, 一年攒下来就是一张银行关系图; 子图中心度回答的是「在这张图上, 谁被织进了最多的小圈子」。之所以选择闭合游走而非简单连线数, 是因为中国银行业的媒体叙事高度圈层化 — 国有大行之间、股份行之间、区域城商行与本地农商行之间各有报道生态, 一家银行的系统重要性更多体现在它被多少个这样的稠密圈层同时接纳, 而不是单纯被点名的次数; 阶乘衰减的闭合游走计数恰好是对「圈层接纳度」的一个无参数、全谱、对分量破碎稳健的数学化。

【方法学与计算】
生产函数为 network_spillover.py 中的 compute_bank_network_centrality, 属 33 个网络结构指标基名 SSOT 元组 NETWORK_METRIC_BASES 中 Part A 节点级组的第 7 项。逐年计算流程为: 第一步按共现判据 criterion 构建年度邻接矩阵 (build_adjacency_matrix), canonical 路径是「同篇共现」— 只要两家银行的验证通过提及出现在同一 docid 内即计一条共现; 第二步据邻接矩阵建 networkx 无向图, 正权边逐条写入, 并补挂全部孤立银行节点; 第三步调用 nx.subgraph_centrality(G)。此处有一个必须写进 codebook 的实现细节: networkx 的子图中心度实现不接受边权参数, 计算发生在二值化拓扑上 — 也就是说本列刻画的是「共现结构的形状」而非「共现的强度」, 强度维度由同组的加权度中心度 (bank_strength_cent, Opsahl 等 (2010) 加权推广) 承接, 两列构念互补而非冗余。孤立节点的子图中心度依定义等于 e 的零次幂即 1, 构成本列的理论下界; 数值上界随网络规模与稠密度指数增长 (主特征值进入 e 的指数位), 因此生产代码用 try/except 捕获 OverflowError、ValueError 与线性代数异常, 溢出年份整年置 NaN 并落 WARNING 日志, 绝不静默写入无穷大或残缺值。判据敏感性设计 (2026-07-03 网络三轨与判据敏感性扩展) 为本家族生成三个判据变体: 无后缀 canonical 为同篇判据; _win1 为 ±1 句窗判据 (两家银行的提及句距不超过 win_radius, 配置键 panel.yaml 下 network_criteria.win_radius, 默认 1); _sent 为严格同句判据 (句距为零)。判据分轨路径在 docid 组内逐句重扫原文, 判据原语为 entity_context 模块的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 审计脚本与生产共用同一原语保证审计等于生产; 扫描文本为 prepend_title 口径, 标题被当作第 0 句参与判定, 镜像 stage 13 的 match_in_title 生产口径; 银行提及判定复用与 stage 11、13 相同的否定词典与短名排除事实源, 禁裸 Aho-Corasick 匹配。生产函数对 criterion 与落列后缀做硬配对校验 (article 对空后缀、win1 对 _win1、sent 对 _sent), 错配即 raise, 从机制上排除「判据算错列」这一类静默污染。需要特别强调两条口径铁律: 其一, 判据后缀与三轨文本后缀 (_full/_ctx/_ss, 银行∧金融科技口径) 是两个正交的概念空间 — 判据主体是银行∧银行共现, 与情感三轨的银行∧金科邻近完全不同, codebook 推断入口须先剥判据后缀再匹配; 其二, network_criteria.win_radius 与 stage 13 的 cooccurrence_filter.sentence_radius 是两个互不联动的配置键, 前者管银行间建网判据, 后者管文章留存硬过滤, 混淆两键属 P0 级口径错误。上游文章宇宙与 full-only 留篇门控 (2026-06-29 口径) 保持一致: 进入展开帧的报道即 stage 21 门控后的留存集, 因此本列与面板中 n_articles 分母族共享同一篇章宇宙, 无独立的行选择。

【文献定位】
本家族在文献坐标系中位于三条研究线的交点。第一条是网络中心度测量理论本身: Freeman (1978) 的概念澄清奠定了度、介数、接近度三分法; Estrada 与 Rodríguez-Velázquez (2005) 引入子图中心度并证明其对区分度中心度无法分辨的节点位置具有更细的分辨率 — 两个度数相同的节点若一个嵌在三角形密集区、另一个挂在树状边缘, 子图中心度能将其分开而度中心度不能; Newman (2005) 的随机游走介数与 Boldi 与 Vigna (2014) 的公理化则共同说明「游走计数」类测度与「最短路径」类测度回答的是不同问题, 本仓将两类并置正是对这一理论分歧的实证回应。第二条是金融网络与系统性关联研究: Wang、Zhang 与 Yang (2020) 刻画了中国担保网络在金融危机与刺激计划下的演化, 说明中国银行体系的网络结构本身是随宏观政策周期剧烈变动的研究对象, 逐年重建网络 (而非用全样本池化网) 是必要而非可选; Gao、Ru 与 Yang (2022) 证明所有权网络在中国银行信贷决策中承载真实信息, 支持「网络位置影响银行行为」这一本家族赖以成立的前提; Sadeghi 与 Feinstein (2024) 提出金融网络传染中心度的统计显著性检验框架, 提示中心度点估计须辅以对网络抽样噪声的稳健性讨论。第三条是中心度作为资产定价与绩效解释变量的应用计量: Yu、Hu 与 Zhong (2024) 发现网络中心度经由信息扩散渠道进入资产定价; Xu 与 Zhao (2024) 系统比较了金融网络中不同节点中心度对价格预测的边际贡献, 其结论 — 不同中心度族的预测力不可互相替代 — 直接支持本仓 33 指标并排的设计; Nezami、Chisam 与 Palmatier (2025) 对中心度与企业绩效关系做了元分析, 给出跨研究的效应量基准, 为解读本列回归系数的经济显著性提供外部标尺。此外, Bonato, Chavez Palan, & Szava (2025, PLOS ONE) 用银行间网络中心度识别全球银行体系中的隐性领导者与高暴露节点, 支持本家族以共现网络位置刻画银行系统重要性的构念思路。Huang, Deng, Yang, Cai, & Zhao (2025, Journal of Systems Science and Complexity) 用符号化与互信息法构建2006-2021年中国上市公司动态股票网络, 发现网络中心度更高的公司未来股价崩盘风险更低, 机制是中心位置提升投资效率并抑制盈余管理导致的坏消息囤积, 为「网络位置具有实质经济信息」这一前提提供了中国市场的补充证据。Klaucke (2025, The North American Journal of Economics and Finance) 用近4.7万条新闻文本中金融机构的共现构造文本溢出指数, 并与Diebold-Yilmaz溢出指数对照验证, 证明媒体文本共现网络可作为传统数值型关联度量的可行替代或补充, 与本家族「用文本共现代理银行网络位置」的建网思路直接呼应。

【识别策略定位】
本列在计量识别链条中的定位是「网络位置测度」而非「处理变量」: 各论文主轨 treatment 是情感与属性变量 (如 llm_vote_tone_full), 子图中心度进入方程的典型角色是调节变量、异质性切分维度或网络暴露控制项。这一定位由社会网络计量的根本困难决定: Bramoullé、Djebbari 与 Fortin (2009) 证明同伴效应在网络数据下的识别依赖排除性网络结构 (朋友的朋友非朋友), 而媒体共现网络的稠密传递性使这类排除约束通常不满足; 把中心度直接当因果处理解读会同时遭遇反射问题、关联同质性与共同冲击三重混淆。Grieser 等 (2022) 在公司金融政策网络效应研究中展示的空间计量处理与 Hughes (2026) 针对带固定效应非线性网络模型的刀切偏差修正, 代表了当前对这类偏误的前沿修补; de Paula、Rasul 与 Souza (2024) 则从面板数据反向识别网络连边本身, 提示媒体共现网络作为「观测到的代理网」与「真实经济网」之间存在测量误差层, 系数解释须限定在叙事网络位置的语义上。与此对应, 本仓为网络指标族配套的稳健性阶梯不走工具变量路线, 而走测量口径并排路线: 三判据 (同篇/±1 句窗/严格同句) 各自 just-identified 并排、互为稳健性、不分主次, 铁律禁止把多个判据变体混进同一个 over-identified 的 Hansen J 检验 — 三个变体测的是同一构念在不同精度-召回权衡下的实现, 把它们当多工具堆叠等于假装拥有三条独立排除约束, 是对过度识别检验的滥用。判据梯子属「规格稳健性并排」范畴 (镜像政治词权重梯子与词典消融梯子先例), 刻意不设跨判据 FWER 模板: 跨模型 rwolf 先例仅覆盖同构念替代 headline 测量的多重检验, 判据梯子的目的不是挑选赢家而是展示结论对建网口径的不敏感。在具体的方程设定层面, 本列的推荐用法有三种形态: 一是作为银行层异质性的切分变量 — 按年度截面中位数把银行分为核心嵌入组与边缘组, 检验情感处理效应是否在网络核心银行更强或更弱, 这对应信息扩散与同伴压力两类竞争机制的区分; 二是作为交互项进入主方程 — 处理变量乘标准化子图中心度, 系数解读为「网络嵌入每提高一个标准差, 处理效应的边际变化」; 三是作为控制变量吸收网络位置与结果变量的共同相关。三种形态都要求配套银行固定效应与年份固定效应, 其中年份固定效应会自动吸收全部年度广播的网络级指标 (net 前缀族), 因此节点级的本列与网络级指标不会在同一方程内竞争解释力。此外须注意逐年重建网络带来的组内动态: 本列的年际变动同时来自银行自身报道行为的变化与整张网络稠密度的漂移, 若研究问题只关心前者, 建议以年内截面标准化后的名次量进入方程, 把网络级漂移从组内变异中剥离。在双向固定效应设定下还应对识别变异的来源做一次显式分解: 银行固定效应吸收的是「国有大行恒居核心、区域小行恒居边缘」这类持久位置差, 年份固定效应吸收的是全网稠密化或萎缩的共同冲击, 真正剩给系数的是「某银行在某年相对自身常态、相对当年全网基准的位置偏移」— 这个残余变异的信噪比在指数加权的本列上尤其值得警惕, 因为头部银行的一次偶发共现结构变化在指数尺度上被急剧放大, 稳健做法是同时报告名次化与对数化两套组内变换的结果。比识别策略更根本的是网络形成本身的内生性: 媒体是否把两家银行写进同一篇报道, 与两行同期的战略动作、监管事件、财务表现同时相关, 因而「边」本身可能与结果方程的扰动项相关; 文献中的常规缓解手段包括用滞后一期的预定网络计算位置、把事件窗内的报道从建网语料中剔除, 以及 de Paula、Rasul 与 Souza (2024) 式的把连边估计与效应估计在面板中分离的结构化路线, 本仓的选择是最保守的一种 — 不给节点级中心度赋予因果地位, 把上述手段留给具体论文按研究问题裁量。测量误差的方向性也须写明: 若把叙事网视为「真实经济网加媒体噪声」, 经典测量误差会把交互项与切分估计推向零, 结论偏保守; 但媒体的可见度偏差是系统性的 — 大行的弱关联更容易被报道成连边 — 这属非经典误差, 偏误方向先验不定, 只能靠银行固定效应、规模控制与三判据梯子从不同精度端夹逼同一结论来间接约束。最后是推断层面: 网络生成的截面依赖使按银行聚类的标准误只覆盖同行内的时间相关, 不覆盖共现相连银行之间的横截面相关, 论文应以年份聚类或双向聚类做推断敏感性; 若设定含滞后被解释变量或滞后网络位置, 短面板动态偏误须另行处理, Hughes (2026) 针对带固定效应非线性网络模型的刀切修正给出了可移植的模板。

【与相邻测度的构念区分】
在同族 18 个节点级指标内部, 子图中心度须与五个近邻严格区分。与度中心度 (bank_degree_cent) 的差异在游走长度: 度只数长度为一的边, 子图中心度数全部长度的闭合游走并按阶乘衰减, 因而度相同、嵌入深度不同的银行在本列上分离。与特征向量中心度 (bank_eigen_cent) 的差异在谱权重结构: 特征向量中心度是长游走极限下主特征值分量的单极近似, 在近似二部或分量破碎的图上退化 (本仓因此对微小分量按门槛置 NaN 并按连通分量分块计算), 而子图中心度用全谱信息加权, 对孤立点、小分量均有良定义值, 分量破碎年份不需要兜底策略 — 这一「全谱稳健性」正是 Estrada 与 Rodríguez-Velázquez (2005) 强调的工程优势。与 Katz 中心度 (bank_katz_cent) 的差异在衰减核与游走类型: Katz 用几何衰减计数全部游走且依赖衰减参数 α 小于主特征值倒数的可行域, 子图中心度用阶乘衰减且只计闭合游走, 无自由参数, 免除了 α 选择的研究者自由度。与介数类 (bank_between_cent, bank_cfbetween_cent) 的差异在构念本体: 介数刻画「桥梁性」— 节点坐落在多少他人对之间的通路上, 子图中心度刻画「圈层嵌入」— 节点自身参与多少闭合结构, 一家坐在两个社群割点上的银行介数极高而子图中心度可以很低。与聚类系数 (bank_clustering, Watts 与 Strogatz (1998) 小世界系数) 的差异在归一化: 聚类系数是三角形占开三元组的比例 (强度归一的局部密度), 子图中心度是未按度归一的绝对游走总量, 两者在回归中一个近似「密度」一个近似「规模乘密度」, 共线但不可互代。在五个核心近邻之外, 还有四组构念边界值得逐一划清。与距离类可达测度 (bank_closeness_cent 接近度、bank_harmonic_cent 调和中心度) 的区分: 距离类回答「该银行到全网其他银行有多近」, 是全局可达效率的度量, 而子图中心度回答「该银行自身被织进多少闭合结构」, 是局部嵌入深度的度量; 值得注意的是调和中心度与子图中心度同享「不连通图上良定义」这一工程性质 (前者对不可达对贡献零、后者对孤立点取下界一), 但工程性质相同不等于构念相同, 稀疏年份两列同为可用列却绝不可互代。与 k-核层级 (bank_coreness, Seidman (1983) 最小度剥离层级) 的区分: k-核是序数的「剥洋葱」深度 — 反复剥去度数不足 k 的节点后该银行最深能留在第几层, 它只看度序列的嵌套结构, 对同层内三角形参与度的差异完全钝感; 子图中心度是基数的游走总量, 对局部每一条加边都敏感。两列组合使用可以区分「深层但松散」与「浅层但稠密」两类位置形态, 单用任何一列都会把这两类银行混为一谈。与结构洞族 (bank_constraint 约束、bank_effective_size 有效规模, Burt 结构洞理论) 的区分最具理论张力: 结构洞理论强调邻域的非冗余 — 邻居之间彼此不相识才有经纪租金, 而闭合游走计数恰是冗余闭合的度量, 高子图中心度在构念上几乎就是低结构洞机会; 因此两族在数据中呈现的负相关是理论预测的实现而非数据缺陷, 论文若同时报告两族应在表注点明这层对偶关系。与电流介数 (bank_cfbetween_cent, Brandes 与 Fleischer (2005) 电流模型) 的区分: 电流介数用随机游走口径修正了最短路介数「只认测地线」的脆弱性, 与子图中心度同属游走计数家族, 但前者数的是「经过该节点」的穿越流量、后者数的是「回到该节点自身」的闭合环流, 一字之差对应桥梁性与嵌入性两个正交构念; 顺带一提, 电流介数是本仓确证的 BLAS 浮点非确定三基名之一而子图中心度不在此清单, 两列的可复现性口径亦不同。谱类家族内部的分叉还可再往下切一层: Bonacich (1987) 的幂中心度用参数符号区分「连接强邻居获益」与「连接强邻居受损」两种权力语义, 说明即便同用邻接矩阵谱信息, 参数化选择也会翻转构念方向; 本仓的特征向量与 Katz 实现对应其正参数分支, 子图中心度则以阶乘核完全绕开了这一参数选择。跨家族地, 本列与 W 轨同伴效应族 (emb_peer_tone 等) 的分工是「位置」对「暴露」: 前者是节点在网络拓扑中的标量坐标, 后者是沿网络加权平均的同伴情感信号, 二者分处方程的不同槽位; 与网络级广播列 (net_density_yr、net_transitivity_yr 等) 的分工是「节点坐标」对「全网形状」, 后者在含年份固定效应的方程中被完全吸收, 只在描述统计与结构漂移诊断中出场, 两层指标不存在解释力竞争。

【已知局限与稳健性梯子】
第一, 测量层局限: 媒体共现网络是叙事网络而非交易网络, 边的存在反映编辑室的联想与议程设置, 不必然对应真实银行间敞口; 国有大行因媒体覆盖密度天然占据高共现位置, 本列水平值部分吸收「媒体可见度」而非纯网络结构, 回归须搭配银行固定效应与规模控制, 且解释锚定在标准化系数上。第二, 计算层局限: 矩阵指数的数值范围随网络稠密化指数膨胀, 生产代码的溢出防线是整年置 NaN, 这意味着极稠密年份可能整列缺失 — 使用者遇到年度整体缺失应首查 stage 40 面板构建日志中的溢出 WARNING 而非怀疑上游数据 (溢出防线在 network_spillover.py 内触发, 该模块属 stage 40 panel 构建阶段, WARNING 落 stage 40 日志; stage 46 是 stata_export 阶段, 不产此告警); 子图中心度经谱分解计算, 理论上属 BLAS 浮点敏感类, 但当前确证的非确定网络列清单 (三基名乘三判据共九列) 不含本列, 该边界待生产机 golden 重生时实证统一, 在此之前跨机器逐位比对本列须保持审慎。第三, 分布形态局限: 指数加权使本列右偏极重, 头部银行与尾部银行可差多个数量级, 进入回归前的对数化或组内标准化属常规操作, codebook 使用者不应直接比较原始水平的组间均值。第四, 稀疏面板退化: 开发环境短面板与小语料下, 严格判据变体 (_sent) 的网络可能退化为大量孤立点加零星小分量, 本列大面积取下界 1 且组内方差趋零属预期退化而非缺陷, 生产全量语料 (跨年长面板) 下不复现。第五, 二值化信息损失: networkx 的子图中心度实现只消费拓扑不消费边权, 一年一篇共现与一年一百篇共现在本列眼中同权; 这一损失被两条渠道部分补偿 — 其一, 判据梯子在功能上近似强度筛选, 更严格的判据 (相邻句、同句) 留下的边天然偏向高强度、高语义密度的共现关系, 因此三判据并排在某种意义上就是「阈值化强度」的敏感性检验; 其二, 强度维度由同族的加权度中心度显式承接。本仓刻意不提供「强度加权闭合游走」这类自定义谱计算, 因为边权进指数矩阵需要研究者选择权重归一方案, 引入的参数自由度与 Katz 的 α 选择问题同构, 与本列「无自由参数」的核心卖点相悖。第六, 时间聚合口径: 年度切片把一月与十二月的共现同权聚合进同一张网, 年内的网络动态 (如某并购事件引发的短期共现潮) 被抹平; 由此, 任何以本列滞后项进入的设定, 其语义都是「上一个自然年的整体位置」而非「事件前位置」, 需要事件研究粒度的论文应回到文章级数据自建窗口网络而非复用本列。第七, 稳健性梯子的完整叙述: 本家族的稳健性证据链由三级构成 — 判据梯子 (本家族三列, 建网口径敏感性)、同族异测度并排 (度/强度/特征向量/Katz/介数/聚类等, 中心度构念的测量方式敏感性)、以及网络级指标 (net_density_yr 等年度广播列, 用于诊断结构漂移是否驱动节点级结论)。三级各自 just-identified 并排、互为稳健性、不分主次, 任何一级内部与跨级之间都禁止混入同一 over-identified Hansen J; 与三轨文本测度、co-primary 双轨嵌入、政治词权重梯子等本仓其他并排族一样, 这一铁律的目的都是把「规格稳健性展示」与「工具有效性检验」两类统计任务在机制上隔离开。判据梯子的读表方式也应预先写明: canonical、_win1、_sent 三个变体下的网络单调稀疏化, 若主效应沿梯子收紧方向单调增强, 说明信号集中在强语义连边上 (编辑刻意并置的银行对承载真实关联), 结论最硬; 若沿梯子单调衰减, 说明弱联想连边承载了效应, 提示机制更可能是媒体议程设置而非银行间实质关联, 解释须相应降格; 若三档同向且量级相近, 则结论对建网口径整体稳健 — 三种模式都是有信息量的结果, 梯子的价值在于区分它们, 而不在于挑出「最显著」的一档报告。

## VAR: bank_subgraph_cent

【变体差分】
本列是 F099 家族的 canonical 列与 core 列: 同篇共现判据 (criterion 为 article) 下的银行子图中心度, 无判据后缀即现行生产口径。建网规则为: 两家银行的验证通过提及出现在同一篇 docid 内 (标题按 prepend_title 口径参与) 即记一条共现, 年度内共现篇数为边权, 但子图中心度本身在二值化拓扑上计算 (networkx 实现不接受边权), 故本列只对「有没有共现」敏感, 对「共现多少次」不敏感 — 强度信息由 bank_strength_cent 承接。同篇判据是三判据中召回最高、精度最低的一端: 只要编辑把两家银行写进同一篇报道, 哪怕分处首尾两段, 也计入连边; 由此得到的年度网络最稠密、连通分量最大、孤立点最少, 子图中心度的截面方差与区分度也最充分, 这是它被定为 canonical 的测量学理由 — 在短面板与中等语料下, 稠密判据保证指标有足够的统计寿命, 而其潜在的假阳性连边风险恰好由 _win1 与 _sent 两个更严格变体从上方压顶检验。数值语义: 孤立银行 (当年无任何同篇共现) 依矩阵指数定义取下界 1; 全年溢出时整年 NaN 并落日志; 未进入当年展开帧的银行年格为缺失。本列的 Stata 变量标签为 Co-mention Subgraph Centrality 并挂 Estrada (2005) 出处注记, 基名收录于 network_spillover.py 的 NETWORK_METRIC_BASES 元组 (33 指标 SSOT, stata_export 判据标签机械块与 gate 测试 import 复用防漂移)。使用建议: 作为网络位置的调节变量或异质性切分维度进入各论文方程, 不作因果处理解读; 因右偏极重, 回归前对数化或标准化; 与 _win1、_sent 两变体各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与同族其他中心度并排报告时按标准化系数比较, 不比原始水平。与两个判据变体的精确差分关系为: 三列共享完全相同的下游计算函数、溢出防线、孤立点语义与列名机制, 唯一的差分维度是建网时「两家银行靠多近才算共现」— 本列不设句距约束 (同篇即可), _win1 要求句距不超过一, _sent 要求同句; 因此三列的取值满足一个结构性单调关系: 严格判据网络的边集是宽判据网络边集的子集, 任一银行在 _sent 网络中的闭合游走数不会超过其在本列网络中的对应值 (孤立点下界 1 两端同取), 数据中若出现反向即为判据实现层缺陷, 可作免费的完整性哨兵。与同族相邻列的槽位分工再强调一次以防误用: 需要「共现强度」用 bank_strength_cent, 需要「桥梁位置」用介数族, 需要「局部密度比例」用 bank_clustering, 需要「全网可达性」用接近度与调和中心度; 本列专管「多尺度圈层嵌入的绝对量」, 在论文表格中与上述近邻并排时务必在表注写明构念差异, 避免审稿人把高相关的中心度族误读为同一测度的重复检验。另注意本列不属于 co-primary 嵌入双轨族 — 它是纯拓扑计数, 无 _lg 孪生列、不消费任何嵌入 API, 换嵌入模型对本列零影响; 也不属于情感三轨族, 无 _full/_ctx/_ss 变体, 家族内的后缀全部是银行∧银行判据后缀。缺失值语义按优先级排列: 年度网络节点数不足两个时整年跳过 (全列缺失); 矩阵指数溢出时该年全体银行置 NaN 并落 WARNING; 银行当年无任何验证通过报道则不进入展开帧, 该银行年格缺失; 银行有报道但零共现则显式挂为孤立节点, 取下界 1 而非缺失 — 「1」与「NaN」在本列中承载完全不同的信息, 使用者做样本筛选时切勿把下界值当缺失剔除。

## VAR: bank_subgraph_cent_sent

【变体差分】
本列是严格同句判据变体 (criterion 为 sent, 后缀 _sent): 只有当两家银行的验证通过提及落在同一个句子内 (句距为零, 即 ±0 句窗) 时才计一条共现连边, 是三判据梯子中精度最高、召回最低的一端。实现上走判据分轨路径: 在 docid 组内用 entity_context 模块的 map_bank_sentence_positions 逐句定位银行提及 (prepend_title 口径下标题为第 0 句, 镜像 stage 13 的 match_in_title), 再经 bank_pairs_within_sentence_window 以半径零取同句银行对; 银行判定复用与 stage 11 相同的否定过滤与短名排除事实源, 禁裸 AC 匹配。同句共现在语义上最接近「编辑刻意并置」— 两家银行被写进同一句, 通常意味着直接比较、合作或并列关系, 假阳性连边最少; 代价是网络急剧稀疏, 分量破碎、孤立点增多, 短面板小语料下本列大面积取下界 1 且方差趋零属预期退化。⚠ 判据后缀 _sent 与三轨文本后缀 _ss (银行∧金科同句) 是两个正交概念空间, 主体分别是银行∧银行与银行∧金科, codebook 推断须先剥判据后缀再匹配, 严禁混淆。本列与 canonical 及 _win1 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 用法上作 canonical 结论的精度上限检验 — 若主结论在同句判据下方向一致, 即排除「稠密判据的假阳性连边驱动结果」这一质疑。

## VAR: bank_subgraph_cent_win1

【变体差分】
本列是 ±1 句窗判据变体 (criterion 为 win1, 后缀 _win1): 两家银行的验证通过提及句距不超过 win_radius 时计一条共现连边, 半径取配置键 panel.yaml 下 network_criteria.win_radius, 默认 1, 即允许相邻句共现。⚠ 该键与 stage 13 银行∧金科硬过滤的 filtering.yaml 下 cooccurrence_filter.sentence_radius 是两个互不联动的配置键 — 前者管银行间建网判据, 后者管文章留存, 数值恰好同为 1 属巧合而非联动, 改动任一键不影响另一键。实现路径与 _sent 完全同源 (docid 组内逐句重扫, map_bank_sentence_positions 加 bank_pairs_within_sentence_window, prepend_title 标题为第 0 句, 复用否定与短名排除事实源), 唯一差分是窗口半径由零放宽到一。构念定位为三判据梯子的中间档: 相邻句共现覆盖了「上句说甲行、下句接乙行」的连续叙述场景, 比同句判据多捕获跨句排比与承接关系, 比同篇判据剔除了首尾远隔的弱联想连边, 精度与召回俱居中, 网络稠密度亦介于两端之间。生产函数对 criterion 与后缀做硬配对校验 (win1 必须配 _win1), 错配即 raise。本列与 canonical 及 _sent 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 三判据同向则结论对建网口径稳健, 若本列与 _sent 同向而 canonical 反向, 则提示同篇判据的远距假阳性连边值得单独审计。另注意本列网络的边集恒为 canonical 边集的子集、又恒为 _sent 边集的超集, 三列取值的这一结构单调性可作免费的实现层完整性哨兵; 短面板小语料下本列稀疏退化程度介于两端之间, 方差通常仍可用。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Akgüller, Ö., & Balcı, M. A. (2026). Detecting Financial Contagion Through Higher-Order Networks: A Deep Learning Approach to Emerging Market Risk. Computational Economics. https://doi.org/10.1007/s10614-025-11287-3
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, Article 2693. https://doi.org/10.1038/s41467-020-16535-8
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), Article 056103. https://doi.org/10.1103/PhysRevE.71.056103
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Brandes, U., & Fleischer, D. (2005). Centrality measures based on current flow. STACS 2005 (Lecture Notes in Computer Science, Vol. 3404), Springer. https://doi.org/10.1007/978-3-540-31856-9_44
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonato, A., Chavez Palan, J., & Szava, A. (2025). Leaders in the global banking network: Analysis of the Bank for International Settlements network data. PLOS ONE. https://doi.org/10.1371/journal.pone.0335506
Huang, C., Deng, Y., Yang, X., Cai, Y., & Zhao, X. (2025). The Benefit of Being Central: Stock Network Centrality and Stock Price Crashes. Journal of Systems Science and Complexity. https://doi.org/10.1007/s11424-025-4338-6
Klaucke, K. (2025). Text Spillover: Measuring connectedness of financial institutions based on news text data. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2024.102307
<!-- rendered-citations:end -->
