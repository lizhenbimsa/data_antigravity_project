---
family_id: F095
columns:
- bank_is_hub
- bank_is_hub_sent
- bank_is_hub_win1
unit: 0/1 枢纽指示 (年内 top ~10% 度中心度阈值, dtype double)
formula: "bank_is_hub = 1 if bank_degree_cent >= cutoff else 0; cutoff = 年度共现网络内第 max(1, int(0.10*N)) 名银行的度中心度 (并列同判); 退化守卫: cutoff<=0 或全体同度 → 全置 0; 判据变体 {同篇(无后缀)/±1句窗 _win1/严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (runner 步骤 7g/7g_win1/7g_sent; 基名注册于 NETWORK_METRIC_BASES SSOT)
upstream:
- "41_panel_encode_aggregate (篇章级 df_exploded: docid/target_bank/year, both-verified 主路径)"
- 14_materialize_ctx 系文本列 (标题/内容; _win1/_sent 判据 docid 组内句级重扫, prepend_title 标题=第 0 句)
- config/panel.yaml::network_criteria.win_radius (默认 1; 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1016/j.jcorpfin.2023.102501"
  type: "journal"
  authors: "Fan, Y., Jiang, Y., Jin, P., & Mai, Y."
  year: 2023
  title: "CEO network centrality and bank risk: Evidence from US Bank holding companies"
  venue: "Journal of Corporate Finance"
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
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: "2691-2729"
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
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
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
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: "76"
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
- doi: 10.1016/j.socnet.2007.04.006
  type: journal
  authors: Latapy, M., Magnien, C., & Del Vecchio, N.
  year: 2008
  title: "Basic notions for the analysis of large two-mode networks"
  venue: Social Networks
  vol: 30
  issue: 1
  pages_or_artno: "31-48"
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
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: "440-442"
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: "531-542"
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
- doi: "10.3390/encyclopedia6010011"
  title: "Network Centrality and Information Cascades in Executive and Director Networks"
  authors: "Jiang, L., Rundo, J., Shi, L., & Zhou, N."
  year: 2026
  venue: "Encyclopedia"
  type: "journal"
- doi: "10.1016/j.heliyon.2024.e26952"
  title: "Research on systemic risk of China's bank-asset bipartite network"
  authors: "Fan, H., & Hu, C."
  year: 2024
  venue: "Heliyon"
  type: "journal"
new_dois:
- "10.1016/j.jcorpfin.2023.102501"
- "10.3390/encyclopedia6010011"
- "10.1016/j.heliyon.2024.e26952"
---

## CORE

该文以1999-2018年美国471家银行控股公司为样本,发现CEO(董事)网络中心度越高,银行风险越低,信息流动与CEO权力是两条传导渠道,为「网络枢纽位置影响银行行为/风险」这一构念提供了银行业情境下的直接实证支持。

【构念与来源】
本家族测度的构念是「银行在年度媒体共现网络中的枢纽地位」: 若某银行在给定年份的银行间新闻共现网络里, 其度中心度位居全体入网银行的前约百分之十, 则判为该年的网络枢纽, 取值一; 否则取值零。这里的「网络」不是真实的资金往来网络或股权关联网络, 而是由媒体报道文本诱导出的信息共现网络: 当同一篇银行金融科技报道中同时提及两家目标银行时, 这两家银行之间即记一条共现边, 全年累加得到年度邻接矩阵。枢纽指示因此刻画的是一种媒体注意力结构中的核心位置——被媒体在报道中反复与众多同业并置的银行, 处于行业新闻叙事的中心, 既更可能是信息扩散的源头与中转站, 也更可能在行业负面冲击中被舆论「点名连坐」。构念的理论源头有两支: 一支是社会网络分析中的中心度传统, Freeman (1978) 对度中心度、中介中心度与接近中心度作出经典的概念澄清, 其中度中心度以「直接连接的邻居数量」度量节点的交往活跃度, 是最直观也最稳健的中心度概念; 另一支是复杂网络科学中的枢纽概念, Watts 与 Strogatz (1998) 的小世界网络研究表明真实网络的连接高度不均匀, 少数高连接度节点承担了不成比例的网络连通功能, 这类节点在网络科学中被称为 hub。本家族把两支合流: 用 Freeman 的度中心度作定序标准, 用「年内前约百分之十」的相对阈值把连续中心度离散化为枢纽与非枢纽的二元分类, 与网络科学中「枢纽是分布尾部少数节点」的经验事实对齐。文本诱导网络的做法在金融经济学中已有成熟先例: Hoberg 与 Phillips (2016) 用产品描述文本相似度构造企业竞争网络并证明其相对静态行业分类的信息增量; Li 等 (2026) 从风险披露文本中恢复金融机构间的网络结构与关联度; 本项目的银行共现网络与之同属「以文本为图的基底」的谱系, 只是边的定义从语义相似换成了报道共现。数据来源是本 pipeline 的篇章级展开帧 df_exploded (由 41 号聚合阶段供给), 其行宇宙与 stage 21 的 full-only 留篇门控口径一致 (2026-06-29 口径: 是否判为一篇银行金融科技报道只看 llm_verified_full), 且共现边采用 both-verified 主路径——同一 docid 下只有两家银行都通过银行侧验证幸存, 该无序对才计一条边, 每篇文章每对恰好加一, 杜绝 phantom 边与 twin 行重复计数。

【方法学与计算】
计算分三步。第一步构图: 对每个年份, 取该年 df_exploded 中全部幸存的 target_bank 作为节点全集 (含孤立节点, 后续显式补入图中), 按 docid 分组, 组内幸存银行集合的每个无序对在邻接矩阵上对称加一, 得到无向加权图; 图构建使用 networkx。第二步算度中心度: 对全图跑标准度中心度 (即节点度数除以节点总数减一的归一化度, 纯拓扑、不吃边权), 落列 bank_degree_cent; 需要强调, 枢纽判定以这一不加权的度中心度为定序标准, 而非 Opsahl 等 (2010) 意义上的加权点强度 (后者单独落列 bank_strength_cent, 与本家族分工明确)。第三步做阈值离散化: 设该年入网银行数为 N, 取 top10_count 等于 max(1, int(N*0.10)), 将全体银行的度中心度降序排序, 以第 top10_count 名的取值为 cutoff, 凡度中心度大于等于 cutoff 的银行一律判为枢纽。这一「阈值并列同判」设计是 2026-06-13 网络指标审计 (N-08 项) 的修复产物: 旧实现按度数降序硬切前 top10_count 家, 当第 k 名与第 k+1 名度数并列时, 谁进谁出由排序的字典序副作用任意决定, 属于不可复现的边界任意性; 改为阈值法后, 同度银行同判, 结果确定且与排序实现无关, 代价是并列扩容时枢纽占比可能略高于百分之十, 这是刻意接受的确定性换精确占比的权衡。在阈值法之上另有一道退化守卫 (N-08 与 NB-05 复审补丁): 若 cutoff 小于等于零 (该年无任何共现对, 全体银行孤立、度数全为零), 或度数分布退化为单一值 (正则图, 全体银行同度), 则「大于等于 cutoff」会把全部银行收进枢纽集, 令该列沦为零方差常数列, 进回归被固定效应吸收且「人人皆枢纽」违背构念本义; 此时全体置零, 语义为「该年无明确枢纽」, 严格优于旧 top-k 实现在同一退化情形下任意点选一家的行为。全量 T=19 生产语料的稀疏早年与 T=2 试跑样本均可能命中该守卫, 属预期退化而非缺陷。工程接口上还有两道防呆闸值得记录: 其一, compute_bank_network_centrality 的 criterion 参数与 suffix 参数必须配套 (同篇对空后缀、句窗对 _win1、同句对 _sent), 错配立即 raise, 防止判据与落列名静默错位; 其二, article 主路径预留的 hyperedge_normalize 超边归一参数 (对多银行文章按 Newman 口径以共提银行数减一折减边权) 尚未在判据分轨路径接线, _win1/_sent 路径遇到该参数为真时显式 raise 而非静默忽略, 防止三判据轨在未来接线时无警告地分叉口径。落列类型为 double (0/1 取值), 由 runner 步骤 7g 系列写入面板; 基名 bank_is_hub 注册于 network_spillover.NETWORK_METRIC_BASES 这一 33 基名单一事实源, stata_export 的判据标签机械块与 gate 测试均 import 该元组防漂移; 又因基名不含 cent 子串, codebook 侧将其纳入 _NET_STRUCT_BASES 白名单, 保证 source_stage 与 category 两个推断函数不落「未知」。与家族内另三列非确定网络列不同, 枢纽指示的计算只涉及整数度数排序与阈值比较, 不经过任何 BLAS 浮点线性代数路径, 因此跨次重建逐位可复现, 不在 golden 零漂移验证需排除的九个 BLAS 漂移列之列。

【文献定位】
把「网络中心位置」与银行或企业结果变量相连的实证文献, 为本测度提供了外部效度锚。Nezami 等 (2025) 对网络中心度与企业绩效关系做了元分析, 汇总证据表明中心度与绩效存在稳健正相关但效应大小高度依赖网络类型与中心度算子的选择, 这正是本家族坚持把枢纽指示与连续度中心度、加权点强度并排落列而非只留其一的文献依据。信息扩散机制方面, Yu 等 (2024) 证明网络中心度通过信息扩散渠道进入资产定价, 中心节点的信息更快被市场消化; Xu 与 Zhao (2024) 进一步发现金融网络中节点中心度对资产价格可预测性有系统影响; Hirshleifer 等 (2025) 在社交网络框架下刻画新闻扩散的结构依赖, 表明信息事件的市场反应强度取决于事件在网络中的位置。这三篇共同支撑本测度的核心解释: 媒体共现网络中的枢纽银行是行业信息流的高暴露节点。银行网络的系统性风险文献则提供了枢纽地位的「双刃剑」解读: Jackson 与 Pernoud (2021) 综述金融网络中的系统性风险, 指出高连接度节点既分散风险又传染风险; Wang 等 (2020) 用中国担保网络的演化实证展示危机与刺激政策下枢纽机构的风险放大角色; Khan 等 (2024) 以硅谷银行事件证明社交媒体信息网络可以独立于资产负债表渠道触发银行间的股价多米诺, 这对本项目「媒体共现网络」的构念相关性是直接的事件证据。中国场景下, Gao 等 (2022) 证明所有权网络在银行放贷中承担信息角色, 说明中国银行业的网络位置具有真实的信息经济学含义。文本网络方法论上, 除前述 Hoberg 与 Phillips (2016) 与 Li 等 (2026) 外, 本家族与同 pipeline 的 llm_peer 方法学论文共享「媒体文本诱导银行网络」的基底设定。在测度选择的谱系上还应说明为何以二元枢纽指示补充连续中心度: 中心度与结果变量的关系在多数实证中呈非线性, 尾部节点的行为与网络功能同中段节点有质的差别 (信息级联的触发、危机传染的放大均集中于极少数高连接节点), 二元化把「是否处于尾部」这一非线性信息以最低参数成本注入线性回归框架, 同时作为分组维度天然适配异质性分析与三重差分设计; 而当研究问题关心组内连续排序时, 连续列始终在场, 两种参数化互为补充而非替代。这一「连续量与其尾部指示并排落列」的做法, 与本 pipeline 中极端负面占比阈值梯子等先例同构, 均遵循「离散化参数是研究者选择, 必须可被连续版本复核」的家规。

【识别策略定位】
在本项目的计量架构中, bank_is_hub 家族定位为描述性结构指标与调节变量, 不作任何主回归的处理变量 (treatment), 也不进入工具变量集。原因有三。其一是经典的反射问题: Manski (1993) 指出网络内生社会效应与相关效应在线性均值模型中不可分离, 银行的枢纽地位由其被报道行为内生决定, 与结果变量共同受未观测行业冲击驱动; Bramoullé 等 (2009) 给出的图结构排除性识别条件要求网络本身外生, 而媒体共现网络显然不满足。其二是网络本身是估计对象而非给定物: de Paula 等 (2024) 表明从面板数据识别网络连边需要强结构假设, 本项目的共现边只是真实银行间关联的噪声代理, 边的测量误差会以非经典方式污染节点统计量; Hughes (2026) 进一步证明带固定效应的非线性网络模型存在附带参数偏差需 jackknife 校正, 提示任何以网络统计量为回归元的推断都应对偶发参数问题保持警惕。其三是同伴效应文献的教训: Leary 与 Roberts (2014) 与 Grieser 等 (2022) 均说明企业金融政策的网络效应识别需要外生变异源, 本项目将外生变异的构造集中在 iv_extensions 的三引擎 (同组 leave-one-out 均值、广义 Bartik、媒体来源 house-style 暴露), 枢纽指示不与之混用。实际消费场景是: 描述统计表刻画样本网络的枢纽结构、异质性分析中作枢纽与非枢纽子样本的分组维度或交互项、以及作为网络溢出回归中的控制变量。凡此种种消费均须记住该列是年内相对指示: 阈值随各年入网银行数 N 漂移, 跨年水平不可比, 不宜作跨年增长率或水平趋势解读, 含年固定效应的回归内作年内横截面对比是其唯一稳妥用法。此外还有两条实操层面的识别纪律。其一是时序前定性: 当年枢纽地位由当年报道流决定, 与同年结果变量存在机械同期性, 若担心反向因果 (结果事件本身引来密集报道从而抬升共现度), 消费端应自行取滞后一期的枢纽指示作为前定调节变量——本家族刻意不落 lag 列, 因为滞后是消费侧一行代码的事而落列会让判据梯子的列数翻倍。其二是交互项的测量误差传导: 枢纽指示作为调节变量进入交互项时, 其阈值边界处的分类误差会与处理变量相乘, 使交互系数的衰减偏误不再是简单的向零收缩而可能改变显著性格局, 稳妥做法是同时报告以连续度中心度为调节变量的交互规格, 二者结论一致方可下调节结论; 这一「二元调节与连续调节并排」的纪律与 Nezami 等 (2025) 元分析揭示的「效应大小依赖中心度算子选择」直接呼应——算子选择本身就是研究者自由度, 必须以并排报告的方式向审稿人开放复核。

【与相邻测度的构念区分】
本家族与同源的三十三个网络结构指标家族共享同一张年度共现图, 但构念分工严格。与 bank_degree_cent 的区别是离散化: 度中心度是连续的归一化度, 枢纽指示是其年内前约百分之十的二元指示, 保留了「是否处于分布尾部」的分类信息而丢弃组内排序细节, 二者是同一定序变量的两种参数化, 绝不同时进同一回归右手边 (完全共线于阈值函数)。与 bank_strength_cent 的区别是边权: 点强度吃共现次数加权并按年内最大值归一, 枢纽判定刻意只吃不加权拓扑, 使其对个别高频共现对的边权极端值不敏感。与 bank_coreness 的区别是概念层次: Seidman (1983) 的 k-core 分解度量节点在逐层剥离下的嵌入深度, 是全局凝聚子图概念, 高度数节点可以低 coreness (星形中心), 枢纽指示只看局部度数不看嵌入结构。与 bank_eigen_cent、bank_katz_cent 的区别是递归性: 特征向量类中心度赋予「连接到高中心度邻居」额外权重, 枢纽指示对邻居身份不敏感。与 Gould-Fernandez 经纪角色五列 (gf_ 前缀) 的区别是中介性构念: 经纪角色度量跨群体的桥接位置, 枢纽度量连接总量, 星形网络中心是枢纽但未必是跨组经纪人。与 llm_peer 论文的嵌入同伴网络列 (emb_peer_tone 系) 的区别是图基底: 后者的 W 矩阵由文本嵌入相似度构造, 属 co-primary 双轨嵌入族, 有 _lg 孪生; 本家族是共现计数图上的拓扑统计量, 非嵌入测度, 按 carve-out 口径无 _lg 孪生, 也与三轨文本 (_full/_ctx/_ss, 银行与金融科技词的共现口径) 无涉。与 bank_eccentricity 的区别是度量几何: 离心率是距离类指标, 度量节点到图中最远节点的最短路长度, 依赖全局连通结构且仅在最大连通分量上有定义, 枢纽指示是局部连接量指标, 孤立节点亦有良定义取值 (度为零, 非枢纽)。与 net_ 前缀的网络级列 (如 net_density_yr、net_n_components_yr) 的区别是聚合层次: 后者是图层面的年度标量, 全体银行同年同值, 只能进年固定效应不可吸收的规格或作年度描述, 本家族是节点层面变量, 在年固定效应内仍有横截面变异——这也是为什么退化年守卫的判读须借助网络级列: 节点级的全零既可能是「有网络但无突出者」也可能是「图本身退化」, 两种形态只有图层列能区分。最后与 industry_neg_shock 三轨的区别是变量类型: 后者是网络加权的情感溢出流量, 本家族是纯结构存量; 顺带一提, 溢出流量列的 W 矩阵与本家族共享同一年度共现图, 因此枢纽指示可以自然地充当溢出回归的异质性维度——检验「溢出效应是否集中于枢纽银行」在图基底上是自洽的。

【已知局限与稳健性梯子】
局限有七点须在论文中如实披露。第一, 共现不等于关联: 两家银行同篇被提及可能只因同属一次监管政策的例行列举, 边的构念效度依赖 stage 13 共现硬过滤与银行侧验证已剔除的噪声之外的残余; 对此的防线是判据梯子——把「同篇」收紧到「±1 句窗」再收紧到「严格同句」, 边越严则例行列举型伪边越少, 见下方两个判据变体列。第二, 百分之十阈值是研究者选择, 无先验最优性; 由于连续的 bank_degree_cent 全程并排落列, 任何审稿人关切均可用连续变量重跑作阈值无关性检验。第三, 跨年不可比性: 阈值锚定年内排序, N 变则绝对 cutoff 变, 该列在设计上就是年内相对指示, 已在源码注释与本文档双处声明。第四, 退化年全零: 稀疏早年或全孤立年被守卫置零, 意味着「无枢纽」与「该年网络退化」在取值上不可分, 消费端如需区分须联合 net_n_components_yr 等网络级列判断当年图形态。第五, T=2 开发样本上年份维度过短, 任何涉及枢纽持续性或转移的动态刻画均须等 T=19 生产面板; 盘上开发面板仅约两个年份横截面, 枢纽指示在其上的方差与真实全量语料 (千万级报道、十九个年份) 不可同日而语, 审计与预研结论不得以开发样本的取值分布外推生产形态。第六, 二元指示天然承受组内信息损失与阈值附近的分类误差: 度中心度恰在 cutoff 附近的银行, 其枢纽身份对个别报道的增删敏感, 该测量误差在回归中表现为衰减偏误; 缓解之道仍是与连续列并排报告, 并在异质性分析中避免对阈值边界样本作过度解读。第七, 二部图投影的机械成团效应: 银行共现网络本质上是「文章×银行」二部图向银行侧的单模投影, Latapy 等 (2008) 系统阐明这类投影会把每篇多银行文章机械地变成银行侧的完全子图——一篇罗列 k 家银行的综述型报道即刻为其中每家银行贡献 k 减一个邻居, 单篇长名单文章足以把边缘银行推入枢纽集; Cimini 等 (2022) 进一步证明未经统计验证的二部投影边中相当比例可归因于度序列的随机配对而非真实关联, 提示共现边的信息含量应对节点活跃度作条件化评估。本家族对此的现有防线有二: 判据收紧臂 (_win1/_sent) 从边定义源头削弱名单型文章的成团能力, 因为罗列式提及很少落在同句或邻句; article 主路径预留的 Newman 口径超边归一参数 (按共提银行数减一折减边权) 则是针对该效应的直接矫正, 但须注意枢纽判定只读不加权拓扑, 即便超边归一未来接线, 折减的是边权而非邻接关系本身, 对枢纽指示的矫正力有限——彻底的投影去噪 (如按二部零模型滤边) 属于刻意不做的范围, 留待审稿人明确要求时以判据梯子回应。Jiang 等 (2026, Encyclopedia) 综述高中心度节点(枢纽)在高管/董事网络中如何驱动信息级联的传播与放大, 为本家族「枢纽银行=信息扩散高暴露节点」的构念解读提供最新文献支撑; Fan 与 Hu (2024, Heliyon) 以中国银行-资产二部网络实证系统性风险传导, 与本家族「文章×银行」二部图投影为银行侧共现网络的构造逻辑及其局限披露直接呼应。稳健性梯子的口径铁律 (与 CLAUDE.md 当前状态铁律逐字对齐): 本家族三列构成网络构造判据敏感性梯子, 同篇 (无后缀 canonical)、±1 句窗 (_win1)、严格同句 (_sent) 三判据互为稳健性、不分主次, 各自 just-identified 并排进各自的回归, 严禁把两个及以上判据变体混进同一 over-identified Hansen J 检验——三者是同一构念在不同边定义下的替代测量, 相关性极高, 混入同一矩条件组既无识别增益又会制造虚假的过度识别检验通过率。判据后缀与三轨文本后缀是两个正交概念空间: _win1/_sent 限定的是银行与银行的共现判据, _full/_ctx/_ss 限定的是银行与金融科技词的文本轨, 前者不存在 _lg 嵌入孪生也不与政治词权重、词典消融等其他梯子交叉。判据敏感性属规格稳健性并排, 镜像政治词权重与词典消融先例, 不设跨模型 FWER 模板 (rwolf 先例仅覆盖同构念替代 headline 测量)。

## VAR: bank_is_hub

【变体差分】
本列是家族 canonical 列, tier 为 core: 采用同篇 (article) 判据的年内枢纽指示, 无判据后缀——依 NETWORK_METRIC_BASES 单一事实源的命名约定, 无后缀即现行生产口径, 与 _win1、_sent 两个判据变体互为稳健性、不分主次, 无后缀是历史命名产物而非「主测度」的地位声明。边的定义: 同一 docid (同一篇文章) 内两家银行均通过银行侧验证幸存, 该无序银行对在当年邻接矩阵上对称加一 (both-verified 主路径, 每篇每对恰计一次, twin 行重复计数与 phantom 边已由 2026-06-11 修复根除); 文章宇宙与 stage 21 full-only 留篇门控一致, 即只有 llm_verified_full 为真的银行金融科技报道进入构图。判定流程: 对该年全图算归一化度中心度 (不加权、纯拓扑), 取入网银行数 N 的百分之十截断整数 (下限一) 作为名次锚, 以该名次银行的度中心度为 cutoff, 度中心度大于等于 cutoff 者取一, 其余取零; 并列同判 (第 k 名与其后同度银行一律进枢纽集), 这是 N-08 审计修复后的确定性设计, 消除了旧 top-k 硬切在并列边界处由排序副作用任意定夺的不可复现性。两道退化守卫: 该年无任何共现对 (cutoff 为零) 或全体银行同度 (正则图退化) 时全体置零, 语义为该年无明确枢纽, 防止零方差常数列与「人人皆枢纽」的构念违背。取值域为 0/1, dtype double。同篇判据是三判据中最宽的边定义: 只要求两家银行出现在同一篇报道的任意位置, 不要求句子邻近, 因此边最多、网络最稠密、枢纽集合的年内区分度通常最好, 但也最容易纳入例行列举型伪边 (如政策新闻结尾罗列多家银行), 这正是需要 _win1 与 _sent 两个收紧臂护航的原因。关于阈值的两点细则须消费端知悉: 其一, 名次锚取整采用向下截断再取下限一的组合, 入网银行不足十家的稀疏年份恰有一个名次锚, 该年枢纽集合退化为「并列最高度数的银行组」, 枢纽占比可远高于百分之十, 解读小 N 年份时应联合当年节点数与网络级列判断; 其二, 并列同判意味着枢纽占比是「至少约百分之十」而非「恰好百分之十」, 度数分布离散度低的年份并列扩容更明显, 这是确定性换精确占比的刻意取舍, 与旧 top-k 实现在同一情形下由字典序任意点选相比, 阈值法的偏差方向透明且可审计。消费提示: 本列为年内相对指示, 跨年水平不可比, 稳妥用法是含年固定效应回归内的年内横截面对比、枢纽与非枢纽分组的异质性分析、以及与处理变量的交互项; 与 bank_degree_cent 完全函数相关, 二者绝不同入同一回归右手边; 三判据变体各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 本列非嵌入测度, 无 _lg 孪生, 与 _full/_ctx/_ss 三轨文本后缀无涉。计算路径无 BLAS 浮点线性代数, 跨次重建逐位可复现, 不在 golden 验证需排除的九个漂移列之列。另因基名不含 cent 子串, 本列依赖 codebook 侧的结构指标白名单归类, 其来源阶段与类别推断不走中心度字符串匹配, 迁移或改名时须同步维护该白名单条目, 否则标签推断落「未知」。同篇判据下还须留意二部投影的机械成团对本列的特殊敏感性: 一篇罗列多家银行的名单型报道会同时抬高其中每家银行的度数, 使枢纽集在稠密报道年份向「常被例行点名的大行」系统性倾斜, 这既是构念的一部分 (被媒体反复并置本就是枢纽含义) 也是噪声来源, 解读时应与两个收紧臂对照——若某银行仅在同篇判据下为枢纽而在句窗与同句判据下均否, 其枢纽地位很可能由名单型文章驱动。

## VAR: bank_is_hub_sent

【变体差分】
本列是严格同句 (_sent) 判据变体: 与 canonical 列的唯一差分在边的定义——两家幸存银行必须在同一篇文章的同一个句子内共同出现, 该无序对才计一条边; 节点全集与同篇判据完全一致 (同一 df_year 幸存银行, 含孤立节点), 仅边集更严, 是三判据中最紧的臂。实现走 docid 组内文本重扫路径: 以 prepend_title 口径拼接标题与正文 (标题作为第 0 句参与扫描, 镜像 stage 13 的 match_in_title 口径), 判据原语为 entity_context 模块的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window (半径取零即严格同句), 扫描共用与 stage 11/13 相同的否定过滤与短名排除事实源 (禁裸 AC 匹配, 防「涉农行业」误命中「农行」一类假阳性), 且仅该组幸存 target_bank 的别名入参, 非幸存银行不可能成边。同句共现是最强的语义关联信号: 两家银行被写进同一个句子, 几乎必然存在比较、并购、合作或同案陈述关系, 例行列举型伪边被最大程度剔除; 代价是边大幅稀疏, 稀疏年份更易触发全零退化守卫, 且枢纽集合对个别深度报道的敏感性上升。注意本判据的「同句」限定的是银行与银行, 与 _ss 文本轨的银行与金融科技词同句口径是不同原语、不同概念空间, 二者禁互相复用。阈值法、并列同判与退化守卫逻辑与 canonical 逐字相同, 仅作用在更严的图上。本列与无后缀、_win1 两臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; codebook 推断函数入口先剥 _sent 后缀再匹配基名, 防止 sent 子串被误归情感指标。

## VAR: bank_is_hub_win1

【变体差分】
本列是 ±1 句窗 (_win1) 判据变体, 边定义的严格度介于同篇与严格同句之间: 两家幸存银行的提及位置落在彼此 ±win_radius 个句子的窗口内即计边, 窗口半径读 config/panel.yaml 的 network_criteria.win_radius 键 (默认 1, 即相邻句也算共现)——须注意该键与 filtering.yaml 中 stage 13 银行金融科技共现硬过滤的 cooccurrence_filter.sentence_radius 是两个互不联动的不同配置键, 前者限定银行与银行判据, 后者限定银行与金融科技词过滤, 改动任一不影响另一。实现与 _sent 列同走 docid 组内句级重扫路径: prepend_title 拼接、标题为第 0 句、map_bank_sentence_positions 定位提及句、bank_pairs_within_sentence_window 以半径一判窗, 共用否定与短名排除事实源, 节点全集与同篇判据一致仅边集收紧。句窗判据的构念定位是折中臂: 相邻句共现容纳了「上句说甲行、下句接乙行」的对照叙述与承接叙述, 比严格同句宽容跨句指代与分句改写, 比同篇又强得多地要求语篇邻近, 因此在伪边剔除与边稀疏之间取得平衡, 通常是判据敏感性检验中与 canonical 相关性最高的臂; 若主结论在同篇与句窗两臂间显著翻转, 提示同篇判据的枢纽结构被文末列举型伪边驱动, 应以收紧臂为准重新审视。阈值离散化、并列同判、全零退化守卫与 canonical 完全一致。本列与无后缀、_sent 两臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 判据后缀与三轨文本后缀正交, 本列无 _lg 孪生; codebook 三推断函数入口剥 _win1 后缀后按基名归类, 保证标签与来源阶段推断不漂移。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Fan, Y., Jiang, Y., Jin, P., & Mai, Y. (2023). CEO network centrality and bank risk: Evidence from US Bank holding companies. Journal of Corporate Finance. https://doi.org/10.1016/j.jcorpfin.2023.102501
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883-937. https://doi.org/10.1093/rfs/hhae025
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Jiang, L., Rundo, J., Shi, L., & Zhou, N. (2026). Network Centrality and Information Cascades in Executive and Director Networks. Encyclopedia. https://doi.org/10.3390/encyclopedia6010011
Fan, H., & Hu, C. (2024). Research on systemic risk of China's bank-asset bipartite network. Heliyon. https://doi.org/10.1016/j.heliyon.2024.e26952
<!-- rendered-citations:end -->
