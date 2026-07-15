---
family_id: F137
columns:
- brok_bip_between_cent
- brok_bip_closeness_cent
- brok_bip_clustering_ra
- brok_bip_degree_cent
- brok_bip_node_redundancy
unit: 二分图网络中心度 (无量纲; degree/closeness/clustering/redundancy ∈ [0,1], betweenness 为二分图归一化介数)
formula: "brok_bip_degree_cent = deg(bank) / n_media_year (nx.bipartite.degree_centrality); brok_bip_between_cent = nx.bipartite.betweenness_centrality(G, bank_nodes); brok_bip_closeness_cent = nx.bipartite.closeness_centrality(LCC 子图, 仅 LCC 内银行, 否则 NaN); brok_bip_clustering_ra = nx.bipartite.clustering(G, mode='dot'); brok_bip_node_redundancy = nx.bipartite.node_redundancy(G, 仅 degree>=2 银行, 否则 NaN); G = 年度媒体-银行二分加权图, 边权 = 该媒体该年报道该银行的文章数 (between/clustering/redundancy 按 networkx API 约束丢边权, 为无权拓扑测度)"
producer: news_process/pipeline/panel/network_brokerage.py::_bipartite_bank_metrics (由 compute_brokerage_centrality 逐年调用, Stage 40 步骤 7h-brok; Stata 标签见 pipeline/panel/export.py)
upstream:
- "11_news_bank.parquet (df_exploded 篇章级: 媒体(中文) x target_bank x year)"
- 40_panel_yearly.parquet (left join 合并, 无匹配 Bank-Year 为 NaN)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: "10.1287/mnsc.2024.04492"
  type: "journal"
  authors: "Lin, C., Lu, F., Michaely, R., & Qin, S."
  year: 2026
  title: "SPAC IPOs and Sponsor Network Centrality"
  venue: "Management Science"
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
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: Article 102163
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: Article 103223
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: Article 76
- doi: 10.1038/s41598-021-03238-3
  type: journal
  authors: Neal, Z. P., Domagalski, R., & Sagan, B.
  year: 2021
  title: "Comparing alternatives to the fixed degree sequence model for extracting the backbone of bipartite projections"
  venue: Scientific Reports
  vol: 11
  issue: 1
  pages_or_artno: Article 23929
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: 10.1016/j.socnet.2007.04.006
  type: journal
  authors: Latapy, M., Magnien, C., & Del Vecchio, N.
  year: 2008
  title: "Basic notions for the analysis of large two-mode networks"
  venue: Social Networks
  vol: 30
  issue: 1
  pages_or_artno: 31-48
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: 39-54
- doi: 10.1023/B:CMOT.0000032580.12184.c0
  type: journal
  authors: Robins, G., & Alexander, M.
  year: 2004
  title: "Small worlds among interlocking directors: Network structure and distance in bipartite graphs"
  venue: Computational & Mathematical Organization Theory
  vol: 10
  issue: 1
  pages_or_artno: 69-94
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: 243-269
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: 157-191
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
  type: journal
  authors: "Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F."
  year: 2024
  title: "Analyst Coverage Networks and Corporate Financial Policies"
  venue: "Management Science"
  one_sentence_zh: "该文构建分析师-公司二分覆盖网络并证明网络结构位置影响公司财务政策，为本家族媒体-银行二分图经纪度测度提供同构的构念与方法论先例。"
- doi: "10.3390/e26050378"
  title: "Systemic Importance and Risk Characteristics of Banks Based on a Multi-Layer Financial Network Analysis"
  authors: "Gao, Q., Fan, H., & Yu, C."
  year: 2024
  venue: "Entropy"
  type: "journal"
- doi: "10.1016/j.physa.2024.129624"
  title: "Financial risk contagion based on dynamic multi-layer network between banks and firms"
  authors: "Jin, Q., Sun, L., Chen, Y., & Hu, Z.-L."
  year: 2024
  venue: "Physica A: Statistical Mechanics and its Applications"
  type: "journal"
new_dois:
- 10.1016/j.socnet.2007.04.006
- "10.1287/mnsc.2023.4891"
- "10.3390/e26050378"
- "10.1287/mnsc.2024.04492"
- "10.1016/j.physa.2024.129624"
---

## CORE

该文以网络中心度测量SPAC发起人在私募股权与风险投资网络中的结构位置,证明其解释了并购后回报的显著变异,为本家族二分图经纪度测度提供同构的金融应用先例。

【构念与来源】本家族 5 列测量的核心构念是银行在年度"媒体-银行"二分信息网络中的结构位置, 即银行作为新闻信息分发体系中一个节点的可见度广度与信息经纪 (information brokerage) 地位。理论出发点是 Han, Kim & Nanda (2024) 在机构经纪网络研究中提出的二分图分析框架: 原文以基金-券商二分图刻画机构投资者经由券商网络获得流动性供给的中介结构, 本项目将其改造为媒体-银行二分图 — 二分图的一端 (bipartite=0) 是新闻媒体来源, 另一端 (bipartite=1) 是被报道的目标银行, 一条边表示"该媒体在该年至少报道过该银行一次", 边权等于该媒体该年报道该银行的文章篇数。在这一网络里, 银行的结构位置回答的是一组与单纯报道数量不同的问题: 这家银行的报道来自多少家不同媒体 (广度), 它是否桥接了彼此原本不相连的媒体渠道 (经纪), 报道它的媒体之间是否高度重叠 (冗余), 以及它到网络中其余节点的信息距离有多近 (可达性)。之所以关心这些结构维度, 是因为中国语境下媒体报道本身就是银行信息环境的一等构件: You, Zhang & Zhang (2018) 证明中国不同产权与市场化程度的媒体在"笔杆子的力量"上系统分化, 媒体身份决定其报道的信息含量与治理效果; Xu (2024) 进一步证明财经记者的社会网络结构直接塑造新闻偏差的方向与大小。因此银行接入的媒体渠道组合的拓扑形状 — 而非仅报道条数 — 承载独立的信息环境含义。数据来源上, 本家族完全由 Stage 11 (news_bank) 解析产出的篇章级 df_exploded 驱动: 该表的"媒体(中文)"列给出每篇报道的中文媒体名称, target_bank 列给出该篇匹配的目标银行, year 列给出报道年份; Stage 40 面板导出的 7h-brok 步骤按年份 groupby 聚合 (媒体, 银行) 对的文章计数作为边权, 构建年度二分图后在银行端计算 5 个原生二分图中心度, 再以 left join 并回 bank-year 面板, 无匹配的银行-年自动为 NaN。本家族属 2026-06-21 网络指标扩展的 WS-B 工作流: 扩展前本模块仅产出加权特征向量中心度 brokerage_eigen_cent, WS-B 补齐了度、介数、接近、聚类、冗余 5 个二分图原生指标, 使二分图一侧的结构刻画从单一"声望"维度扩展为覆盖 Freeman (1978) 经典三中心度分类加二分图特有冗余与聚类的完整谱系。用白话概括这五个维度各自在问什么: 度中心度问"报道你的媒体占当年活跃媒体的几成"(广度); 介数中心度问"有多少信息流动的最短路必须路过你"(桥接); 接近中心度问"消息从你出发几步能传遍全网"(可达); 聚类系数问"报道你的那些媒体是不是同一个圈子的"(抱团); 节点冗余度问"把你拿掉之后你的媒体们还能不能经由别的银行互相连上"(可替代性)。五个问题合起来给出一家银行信息环境的立体画像, 任何单一计数变量都无法复现这一画像 — 这正是家族存在的理由。

【方法学与计算】五列全部由 pipeline/panel/network_brokerage.py 的 _bipartite_bank_metrics 函数在同一张年度二分图 G 上计算, 且共享一组防御性守卫。构图阶段: build_media_bank_bipartite 对每个年份取 df_exploded 子集, 按 (媒体(中文), target_bank) groupby 计数得边表, 分别挂媒体节点 (bipartite=0) 与银行节点 (bipartite=1), 加权边 weight 取整数文章数; 构图后以显式 raise 断言 nx.is_bipartite (刻意不用裸 assert, 防 python -O 优化剥离守卫); 节点总数不足 3 (至少 1 媒体加 2 银行) 的年份整年跳过。指标阶段的第一条铁律是: networkx 的全部 nx.bipartite.* 中心度函数返回的字典同时覆盖两端节点, 必须过滤到 bank_nodes 集合才落面板, 否则媒体节点的数值会混入银行列。第二条铁律是逐指标独立降级: 每个指标的调用各自包 try/except, 单指标计算失败只将该指标置 NaN 并写 warning 日志, 不连坐其余四列, 也不崩阶段。具体到各列: 度中心度用 nx.bipartite.degree_centrality, 其归一化分母是对侧节点集规模, 即银行的度除以当年媒体总数, 得到"年内相对"量纲, 年份固定效应下跨年媒体总量的漂移被吸收; 介数中心度用 nx.bipartite.betweenness_centrality, 采用 Borgatti & Everett (1997) 针对二分图修正的归一化常数 (二分图中最短路径可达的节点对组合受两端集合规模约束, 直接套用一分图归一化会系统低估); 聚类系数用 nx.bipartite.clustering 的 mode='dot' 变体, 其实现口径为 Latapy, Magnien & Del Vecchio (2008) 定义的成对邻域重叠 (两节点共享邻居集的 Jaccard 型点积比) — 列名后缀 _ra 是历史命名, 并非指 Robins & Alexander (2004) 的四环系数 (后者在 NetworkX 中是未被本模块调用的独立函数 robins_alexander_clustering, 详见对应 VAR 节的估计量纠正); 接近中心度受 R13 审计裁决约束, 只在最大连通分量 (LCC) 的子图上用 nx.bipartite.closeness_centrality 计算并只对 LCC 内的银行赋值, LCC 外银行一律 NaN — 依据是断连图上跨分量的接近中心度不可比, 项目实测出现过孤立小分量节点取值 1.5 而大分量核心节点仅 1.0 的排名倒挂; 节点冗余用 nx.bipartite.node_redundancy, 但该函数对度小于 2 的节点直接抛 NetworkXError 崩溃, 故先以 degree>=2 预过滤出合格银行集 (F5 铁律), 度不足的银行置 NaN。一个必须写明的 API 约束: networkx 的二分图介数、聚类、冗余实现不消费边权 (这是库函数签名的硬约束, 不是研究者选择), 因此这三列是无权拓扑测度, 度量"渠道存在与否"的结构; 与之互补, 同图上的 brokerage_eigen_cent 走加权特征向量路径, 度量"渠道强度加权"的声望, 两类测度合起来覆盖 Opsahl, Agneessens & Skvoretz (2010) 所论证的无权/加权中心度分野的两端。落盘链路上, 逐年计算的结果先累积到以 (银行, 年份) 为键的字典 bip_results, 循环结束后一次性转 DataFrame 并以 target_bank 加 year 联合键 left join 回 bank-year 面板 — left join 保证面板行数在合并前后严格不变, 图中未出现的银行-年组合自动为 NaN 而非被丢行, 这是面板完整性的承重设计。由此本家族的 NaN 携带三层可区分语义: 整年图退化 (节点不足 3) 时该年全体银行五列皆缺; closeness 对 LCC 外银行单列缺; redundancy 对度小于 2 银行单列缺 — 三层缺失各有结构含义, 下游填补策略必须区别对待, 一律填零会把"处于信息网络边缘"改写成"处于网络中心度为零的位置", 属语义错误。日志侧, 模块以一次性 banner 输出环境、配置与方法论引用三大块, 逐年输出媒体数、银行数、边数与所用方法, 输入端回显 df_exploded 的行列形态与必需列存在性作 provenance 存档, 全部日志为纯观测、golden-safe。计算全程为精确确定性算法 (精确最短路径与邻域集合运算, 无随机初始向量、无迭代特征分解), 因此本家族 5 列不在面板已知的 BLAS 浮点非确定列清单内 (该清单为 bank_clustering 等 3 基名乘三判据共 9 列), golden 验证无需对其做漂移豁免, 跨 run 字节级可复现。

【文献定位】本家族的文献谱系有三层。测度理论层: Freeman (1978) 奠定度、介数、接近三大中心度的概念区分 — 度对应直接沟通活动量, 介数对应对信息流的潜在控制, 接近对应独立可达性 — 本家族的三个同名列是该分类在二分图上的直接移植; Borgatti & Everett (1997) 与 Faust (1997) 是二分图 (2-mode / affiliation) 中心度的方法论源头, 前者给出二分图上度、介数、接近的归一化修正, 后者系统讨论隶属网络中心度的构念含义, 二者共同回答"为何不能把一分图公式原样套在二分图上"; Robins & Alexander (2004) 与 Latapy et al. (2008) 补齐二分图特有的聚类与冗余测度; Boldi & Vigna (2014) 以公理化方法比较各中心度对"重要性"直觉的满足程度, 为多测度并排而非单测度独断提供理论理由; Newman (2005) 的随机游走介数说明介数亦有非最短路径变体, 本家族取标准最短路径口径, 该文界定了口径边界。测度选择层: Neal, Domagalski & Sagan (2021) 与 Cimini et al. (2022) 系统评估了将二分图投影为一分图再算指标的信息损失与虚假边问题, 支持本家族"原生二分图指标、不做投影"的设计决策 — 投影会让共享任一媒体的银行对全部连边, 稠密化后的一分图指标混入大量投影伪影。应用与效度层: Han, Kim & Nanda (2024) 是构念锚, 证明二分经纪网络位置影响流动性供给这一真实经济结果; Yu, Hu & Zhong (2024) 与 Xu & Zhao (2024) 分别证明金融网络中心度对信息扩散、资产定价与价格预测有增量解释力; Nezami, Chisam & Palmatier (2025) 对网络中心度-企业绩效关系做了元分析, 给出跨研究的效应量基准与边界条件; Li et al. (2026) 展示从文本披露构建金融网络并测量关联性的前沿做法, 与本项目"从新闻文本构建媒体-银行网络"的路径同源; Sadeghi & Feinstein (2024) 则提醒网络中心度作为统计量需要显著性验证, 构成本家族局限讨论的方法论参照。Gomes, Gopalan, Leary & Marcet (2024, Management Science) 构建分析师-公司二分覆盖网络并证明网络结构位置影响公司财务政策, 为本家族媒体-银行二分图经纪度测度提供同构的构念与方法论先例。Gao, Fan & Yu (2024, Entropy) 该文以多层金融网络刻画银行间多重关联并识别系统重要性银行, 为本家族媒体-银行二分图的多层/多关系网络测度思路提供同期方法论参照。Jin, Sun, Chen & Hu (2024, Physica A: Statistical Mechanics and its Applications) 该文构建银行-企业动态多层网络模型刻画风险传染路径, 与本家族媒体-银行二分图均属以二分/多层结构刻画银行外部关联的建模范式, 为网络拓扑测度的经济含义提供同期实证支持。

【识别策略定位】本家族在计量设计中定位为描述性结构测度与异质性调节变量, 不是任何一篇论文的 treatment 主变量, 也不进入 IV 三引擎 (LOO 均值 / 广义 Bartik / outlet house-style) 的工具构造。使用场景有三: 一是作为银行信息环境的控制变量进入主回归右侧; 二是作为调节变量做分组或交互 (如高经纪地位银行对媒体情感冲击的敏感度差异); 三是作为网络结构本身的描述统计支撑机制叙事。识别口径上有四点铁律级约束。其一, 五列同族但构念各异 (广度/桥接/重叠/可达/冗余), 使用时各自 just-identified 并排进入各自的回归规格, 互为稳健性、不分主次, 严禁将多列同时塞进同一个 over-identified 的 Hansen J 检验矩条件 — 这与项目内三轨、co-primary 双轨嵌入、政治词权重梯子的口径完全一致。其二, 本家族是 track-agnostic 的元数据测度: 输入只有媒体名、银行名、年份三个字段, 完全不消费 content_full/content_ctx/content_ss 三轨文本, 因此不存在 _ctx/_ss 孪生列, 也因其非嵌入测度而不在 co-primary 双轨 carve-out 之列, 无 _lg 孪生 — 这属于"唯一不能双轨"的 track-agnostic 例外, 缺孪生是 by design 而非缺口。其三, 度中心度分母为当年媒体总数, 使指标天然是年内相对量, 建议规格始终含年份固定效应, 使跨年媒体生态规模变化 (媒体创刊停刊、语料覆盖变化) 不被误读为银行结构位置变动。其四, 网络位置本身是内生结果 (更大的银行天然接入更多媒体), 任何将其作因果解释的用法须交由外生冲击设计, 本家族自身只承诺测度效度不承诺识别效度; Sadeghi & Feinstein (2024) 式的中心度显著性检验可作为结构位置差异非噪声的前置证据。此外, 若下游将本家族列用于同伴效应类规格 (如以网络位置定义参照组再回归同伴均值), 须直面 Manski 反射问题: Bramoullé, Djebbari & Fortin (2009) 证明经由网络结构的排他性约束 (存在二阶邻居非一阶邻居的节点三元组) 才能分离内生同伴效应与外生特征效应, 而媒体-银行二分图恰好天然提供这类非传递结构, 这是二分图相对全连接参照组在识别上的额外价值; 但项目现行 IV 三引擎均不消费本家族列, 上述讨论仅界定潜在扩展的识别前提, 不描述现状。最后须说明与留篇口径的关系: 本家族的输入 df_exploded 属篇章级元数据宇宙, 其行集在主线过滤链 (含 stage 13 共现硬过滤) 之后形成, 与 stage 21 情感留篇的 full-only 门控 (2026-06-29) 属两条正交口径 — 本家族不消费任何 llm_verified 门控列, 也不参与 n_articles 分母的构造, 换 LLM 或改门控不会波及本家族数值。

【与相邻测度的构念区分】面板中与本家族最易混淆的有四组邻居。第一组是同图兄弟 brokerage_eigen_cent: 同一张媒体-银行二分图, 但走加权特征向量路径 (按连通分量确定性迭代, 微小分量 NaN, 不收敛分量 degree 兜底并升 CRITICAL 日志), 构念是"被高影响力媒体报道的声望", 与本家族的无权拓扑测度形成加权/无权互补, 两者并排不互替。第二组是 bank_* 共现网络家族 (bank_degree_cent, bank_clustering, bank_constraint 等 33 基名乘同篇/_win1/_sent 三判据): 那是银行-银行同质一分图, 边定义为两银行在同一篇文章内共现, 刻画银行间的媒体叙事关联; 本家族是媒体-银行异质二分图, 刻画银行与信息渠道的隶属结构 — 一分图共现回答"哪些银行被一起谈论", 二分图回答"谁在谈论这家银行", 构念正交。第三组是 gf_* Gould-Fernandez 经纪角色五列: 同样以"经纪"命名, 但定义在银行共现一分图的三元组上, 按中介者与两端的群组归属划分协调人/巡回/守门-代表/联络人角色, 与本家族在二分图上的几何介数是不同代数结构。第四组是 attention 族计数类列 (如 n_articles, 媒体覆盖计数): 那些是一阶总量, 本家族是二阶结构 — 两家银行可以报道篇数完全相同而二分图位置截然不同, 这正是本家族相对计数变量的增量信息所在, 也是 Nezami et al. (2025) 元分析强调中心度效应独立于规模效应的操作化前提。

【已知局限与稳健性梯子】已知局限五条。一, 无权约束: 介数、聚类、冗余因 networkx API 丢边权, 一条一篇报道的弱边与一条五百篇的强边在这三列眼中等价, 强度信息须由 brokerage_eigen_cent 与计数族补足 (Opsahl et al. 2010 的批评直接适用)。二, 媒体名标准化风险: 节点身份取自"媒体(中文)"字符串, 同一媒体的名称变体若未在上游归一会被拆成多个节点, 系统性抬高表观度数; 该风险由上游 Stage 11 的媒体名解析约束, 但无法在本模块内消除。三, 年度切片: 边在年内聚合, 年初与年末的报道拓扑等价, 网络动态在年内被抹平; 更细时间窗会使图过稀, 是分辨率与稠度的权衡。四, 结构性缺失值有三个来源且语义不同 — 整年节点不足 3 跳年、LCC 外银行的 closeness 为 NaN、度小于 2 银行的 redundancy 为 NaN — 使用者不应将这三类 NaN 与"未被报道"混同, 亦不应简单以 0 填补。五, dev 盘 (T=2, 约 220 行) 上二分图极稀, closeness 与 redundancy 的非缺失覆盖率天然偏低, 属预期退化, 生产 T=18 全量语料 (约 3,740 家媒体来源的原始普查规模) 下年度图的节点与边基数将高出数个量级, 缺失结构与数值分布均以生产盘实测为准, 不应以 dev 盘分布外推。稳健性梯子方面: 本家族五列自身即构成一组"同图异构念"的规格稳健性并排, 主结论若在度、介数、接近三个经典维度上同向, 便不被单一中心度定义驱动 (Boldi & Vigna 2014 的公理化分析正是多测度并排的理论依据); 与 brokerage_eigen_cent 的加权/无权对照构成第二级梯子; 与 bank_* 一分图共现指标的二分/一分对照构成第三级梯子。三级梯子同受铁律约束: 各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J; 梯子间不做交叉组合, 避免规格空间爆炸。测量误差方向上还可给出一个有用的先验: 媒体名归一化不足造成的节点分裂会同时抬高分子 (表观媒体家数) 与分母 (表观媒体总数), 对度中心度的净偏差方向不定但量级受限, 而对介数与冗余的影响则可能非单调 (分裂节点人为制造桥接假象), 故当五列结论出现分歧时应优先怀疑上游实体归一质量而非急于做经济学解释 — 这也是把五列设计为并排稳健性臂而非单列独断的又一实证理由。最后指出一个刻意未实施、但方法论上成立的潜在第四级梯子以界定边界: 其一是中心度的统计显著性验证, 即以随机图零模型检验观测到的结构位置差异是否超出偶然波动, Sadeghi & Feinstein (2024) 在金融传染网络上示范了这一程序; 其二是二分图骨架抽取, 即先以固定度序列零模型筛除统计上不显著的边再算指标, Neal, Domagalski & Sagan (2021) 系统比较了各类零模型的功效差异。两者均要求引入随机置换或解析零分布, 会破坏本家族现有的精确确定性与字节级 golden 可复现承诺, 且在年度全量图上计算代价可观, 故现行实现刻意停留在观测图的确定性指标层; 若未来某篇论文的审稿意见要求"网络位置差异非噪声"的正式检验, 应在论文侧以独立脚本实施而非改动本模块, 以免污染面板的确定性锚。这一取舍本身也应在使用本家族列的论文方法节中作一句透明披露。

## VAR: brok_bip_between_cent

【变体差分】本列是家族中唯一直接操作化 Han, Kim & Nanda (2024) "信息经纪"构念的列: 二分图介数中心度, 度量该银行落在多少对其他节点 (媒体对媒体、媒体对银行、银行对银行) 之间最短路径上的归一化份额。区别于家族 canonical 的度中心度只数直接渠道条数, 介数捕捉的是桥接地位 — 一家银行若同时被两个彼此从不共同报道任何其他银行的媒体群覆盖, 它就成为这两个信息社区之间的必经节点, 介数高企; 反之一家被大量媒体报道、但这些媒体彼此高度重叠的银行, 度可以很高而介数接近零。计算走 nx.bipartite.betweenness_centrality, 归一化常数按 Borgatti & Everett (1997) 的二分图修正 (分母由两端集合规模分别决定, 而非一分图的 (n-1)(n-2)/2), 因此数值与一分图介数不可直接比较水平。Freeman (1978) 将介数解释为对信息流的潜在控制力, 移植到本语境即: 高介数银行处在跨媒体社区信息汇聚的枢纽位, 其新闻信息环境更多元、更不易被单一媒体阵营的叙事垄断。与家族其余列的差分还包括: 本列按 API 约束不消费边权 (无权拓扑介数), 全图计算不做 LCC 限制 (断连图上介数天然为分量内量, 跨分量对为不可达、贡献为零, 无 closeness 式的跨分量倒挂问题), 亦无 degree>=2 预过滤; 失败降级独立于其余四列。使用口径: 与 canonical 度中心度并排作互为稳健性检验、不分主次, 禁与家族其他列混入同一 over-identified Hansen J; Newman (2005) 的随机游走介数是本列刻意未采的替代口径 (信息不必走最短路径), 引用以界定测度边界。

## VAR: brok_bip_closeness_cent

【变体差分】二分图接近中心度, 度量银行到网络中其余可达节点的平均最短路径距离的倒数型指标: 值越高, 该银行在信息拓扑上离媒体生态整体越近, 新闻信息以越少的中转步数即可波及全网。区别于家族 canonical 的关键差分是 LCC 限制守卫 (R13 审计裁决): 接近中心度在断连图上跨分量不可比 — 一个只有两三个节点的孤立小分量里, 节点间距离全为 1 或 2, 机械计算会给出比大分量核心节点更高的数值, 项目实测出现过孤立点 1.5 对连通核心 1.0 的排名倒挂 — 因此本列只在最大连通分量的子图上调用 nx.bipartite.closeness_centrality, 且只对落在 LCC 内的银行赋值, LCC 外银行一律 NaN。这意味着本列的 NaN 有双重语义: 要么该银行-年整年图退化被跳过, 要么该银行在该年落在主信息网络之外的小岛上 — 后者本身就是有信息量的结构事实, 使用者做样本选择时须意识到"closeness 非缺失"等价于"处于主流媒体信息圈内", 这是一个内生的子样本。归一化沿 Borgatti & Everett (1997) 的二分图口径: 二分图中同侧节点最短距离必为偶数、异侧必为奇数, 归一化常数须按两端集合规模分别修正, Faust (1997) 对隶属网络中该测度"信息可达性"含义有系统讨论。与家族其余列口径一致: 无权、逐指标独立降级、与其余四列各自 just-identified 并排互为稳健性, 禁混同一 over-identified Hansen J。

## VAR: brok_bip_clustering_ra

【变体差分】二分图聚类系数, 实际估计量口径以 producer 真实调用为准 = Latapy, Magnien & Del Vecchio (2008) 的成对邻域重叠 (pairwise-overlap) 系数, 而非列名后缀 ra 字面所暗示的 Robins-Alexander 口径。这里必须先纠正一个源码显式警告要避免的误归因: 列名后缀 _ra 是项目早期的历史命名产物, 并不代表本列的真实算法身份。查 network_brokerage.py 的 white-box 注释 (brok_bip_clustering_ra 由 nx.bipartite.clustering(G, mode='dot') 计算) 可知, NetworkX 该函数的 dot/min/max 三种模式实现的都是 Latapy et al. (2008) 定义的成对邻域重叠聚类系数; 而 Robins & Alexander (2004) 提出的四环 (four-cycle) 二分图聚类系数在 NetworkX 中是另一个独立函数 robins_alexander_clustering, 本模块从未调用它。因此本列的真实计算是: 对银行节点, 取其邻居 (报道它的媒体) 集合, 与经由共享媒体可达的其他银行节点两两比较, 以邻居集合的点积型重叠比 (交集规模对并集规模的比, Jaccard 式) 度量该银行局部邻域的重叠闭合程度; 这是 Latapy et al. (2008) 的 dot-overlap 定义, 不涉及四环枚举。构念上区别于家族 canonical 的度中心度与介数: 聚类回答的不是"渠道多不多"或"桥不桥", 而是"这家银行所处的媒体-银行局部生态有多抱团" — 高聚类意味着报道该银行的媒体们同时也系统性地共同报道同一批其他银行, 形成紧密的报道社区; 低聚类意味着其媒体渠道组合彼此独立、各自覆盖不同的银行群。一分图的三角形闭合定义在二分图上不可用 (二分图无奇数环、无三角形), 二分图的局部闭合须另立定义 — Robins & Alexander (2004) 在董事连锁二分网络上以四环刻画闭合, Latapy et al. (2008) 则以邻域重叠比刻画; 本列采用的是后者。这也正是本列不能与面板中一分图共现网络的 bank_clustering 混同的根本原因 — 两者名称相近但代数对象不同 (二分图邻域重叠对一分图三角形闭合), 且 bank_clustering 属 BLAS 浮点非确定豁免列而本列是精确集合运算、完全确定。计算铁律: mode='dot' 是三种模式 (dot/min/max) 中的对称口径; 不消费边权; 返回字典含两端节点须过滤 bank_nodes; 失败独立降级为 NaN。使用口径同家族: 与其余四列各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

## VAR: brok_bip_degree_cent

【变体差分】本列是家族 canonical 兼 core 列 (2026-07-10 类别 6 扩围①签核): 二分图银行端度中心度, WS-B 媒体-银行中心性家族中最基础、最可解释、缺失最少的一列, 因而被选为家族的规范代表进入 core 层。定义与计算: nx.bipartite.degree_centrality 取银行节点的度 (该年报道过该银行的去重媒体家数) 除以对侧集合规模 (该年图中媒体节点总数), 得到落在 [0,1] 区间的年内相对广度 — 取值 0.30 可直读为"该年活跃媒体中有三成报道过这家银行"。这一归一化选择是本列语义的承重梁: 分母随年份的媒体生态规模浮动, 使指标自动剔除语料覆盖面逐年扩张的机械趋势, 代价是跨年水平比较必须在年份固定效应下进行, 这也是源码注释"degree 除以当年媒体数, 年内相对, 年 FE"的确切含义。归一化口径出自 Borgatti & Everett (1997) 对二分图度中心度的修正 (一分图除以 n-1 在二分图上无意义, 因为银行的邻居只能来自媒体侧), Faust (1997) 进一步论证了隶属网络中度作为"参与广度"的构念效度。与家族其余四列的差分: 度是唯一不涉及任何路径、分量或邻域高阶结构的一阶测度, 因此没有 LCC 限制 (closeness 专属)、没有 degree>=2 预过滤 (redundancy 专属)、没有最短路径枚举 (between 专属)、没有邻域重叠计算 (clustering 专属), 是五列中结构性 NaN 最少、对图稀疏度最鲁棒的一列 — 只要银行该年出现在图中即有定义, 这正是它适合作 canonical 的工程理由; 概念上, Freeman (1978) 三分类中度对应"直接沟通活动量", 是其余高阶测度的公共基座, Boldi & Vigna (2014) 的公理化分析中度中心度也是满足尺寸公理与密度公理的基准测度。工程细节上, 本列由 nx.bipartite.degree_centrality 一次调用产出两端全部节点的字典, 落面板前按 bank_nodes 过滤并逐值 float 化, 缺键回退 NaN; 该调用是五列中唯一 O(节点数) 的线性计算, 无路径枚举开销, 生产 T=18 全量下也不构成性能热点。构念上须与两类邻居严格区分: 其一, 与 attention 族原始计数 (报道篇数) 不同, 本列在媒体维度去重且按媒体总量归一 — 一家被单一媒体密集报道五百篇的银行, 篇数计数很高而本列很低, 两者的分歧本身就是信息集中度的信号; 其二, 与同图的 brokerage_eigen_cent 不同, 度对所有媒体一视同仁, 特征向量则按媒体自身的连接广度加权, "被十家小报报道"与"被十家全国大报报道"在本列等值、在特征向量列分化, 两列并排即构成"广度对声望"的稳健性对照。效度文献上, 度中心度是 Nezami, Chisam & Palmatier (2025) 元分析中覆盖研究最多的中心度形式, 其与企业绩效的正相关在控制规模后依然稳健; Yu, Hu & Zhong (2024) 与 Xu & Zhao (2024) 在金融网络中证明度型中心度对信息扩散速度与资产价格预测有一阶解释力; Han, Kim & Nanda (2024) 的二分经纪框架中, 度对应经纪关系组合的规模边际。本列的动态分布统计 (dtype、极值、均值、缺失率、非缺失样本量) 由引擎在组装期从面板实测注入, 见本列描述末尾的统计特征段。已知局限: 媒体名归一化误差直接进入分子; 无权口径忽略报道强度, 单媒体密集报道与多媒体零星报道的差异须由加权列与计数列补足; dev 盘 T=2 下年度图稀疏, 数值分布压缩属预期退化, 生产 T=18 下分布形态以实测为准。使用铁律与家族一致: 本列与其余四列及 brokerage_eigen_cent 各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J; 本列 track-agnostic, 无 _ctx/_ss/_lg 孪生, 均属 by design。

## VAR: brok_bip_node_redundancy

【变体差分】二分图节点冗余度 (Latapy, Magnien & Del Vecchio 2008 的 redundancy coefficient), 度量: 若把该银行从图中移除, 其邻居 (报道它的媒体) 之间经由其他银行仍然保持的二步连接对占其全部邻居对的比例。构念上是 Burt 式结构洞逻辑在二分图上的镜像反转: 冗余度越高, 说明该银行的媒体渠道之间本就通过其他银行彼此关联, 该银行对其信息网络是可替代的; 冗余度越低, 该银行越接近其媒体邻居之间独一无二的连接点, 其结构洞租金越大 — 因此本列与 brok_bip_between_cent 构成"经纪地位"的一对互补测度 (介数从全局路径看桥接, 冗余从局部邻域看不可替代性), 但二者代数上独立, 高介数低冗余才是强经纪位的完整证据。区别于家族 canonical 的关键工程差分是 F5 铁律预过滤: nx.bipartite.node_redundancy 对度小于 2 的节点直接抛 NetworkXError (单邻居节点的"邻居对"集合为空, 比例无定义), 该异常若不拦截会崩掉整个 Stage 40 步骤, 故源码先以 G.degree(b) >= 2 筛出合格银行集再调用, 度为 0 或 1 的银行置 NaN。由此本列的 NaN 语义与 closeness 的 LCC-NaN 又不相同: 它标记的是"该年仅被至多一家媒体报道"的极低覆盖银行, 做样本筛选时等价于一个隐含的最低媒体多样性门槛, 使用者须警惕由此产生的选择效应 (小银行系统性缺失)。计算不消费边权、返回值过滤 bank_nodes、失败独立降级, 均同家族口径; dev 盘 T=2 稀疏图上非缺失覆盖偏低属预期退化。使用铁律: 与其余四列各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Lin, C., Lu, F., Michaely, R., & Qin, S. (2026). SPAC IPOs and Sponsor Network Centrality. Management Science. https://doi.org/10.1287/mnsc.2024.04492
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, Article 102163. https://doi.org/10.1016/j.najef.2024.102163
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, Article 103223. https://doi.org/10.1016/j.irfa.2024.103223
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), Article 76. https://doi.org/10.1038/s42005-022-00856-9
Neal, Z. P., Domagalski, R., & Sagan, B. (2021). Comparing alternatives to the fixed degree sequence model for extracting the backbone of bipartite projections. Scientific Reports, 11(1), Article 23929. https://doi.org/10.1038/s41598-021-03238-3
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Robins, G., & Alexander, M. (2004). Small worlds among interlocking directors: Network structure and distance in bipartite graphs. Computational & Mathematical Organization Theory, 10(1), 69-94. https://doi.org/10.1023/B:CMOT.0000032580.12184.c0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F. (2024). Analyst Coverage Networks and Corporate Financial Policies. Management Science. https://doi.org/10.1287/mnsc.2023.4891
Gao, Q., Fan, H., & Yu, C. (2024). Systemic Importance and Risk Characteristics of Banks Based on a Multi-Layer Financial Network Analysis. Entropy. https://doi.org/10.3390/e26050378
Jin, Q., Sun, L., Chen, Y., & Hu, Z.-L. (2024). Financial risk contagion based on dynamic multi-layer network between banks and firms. Physica A: Statistical Mechanics and its Applications. https://doi.org/10.1016/j.physa.2024.129624
<!-- rendered-citations:end -->
