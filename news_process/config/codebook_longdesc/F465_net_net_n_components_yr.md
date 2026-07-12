---
family_id: F465
columns:
- net_n_components_yr
- net_n_components_yr_sent
- net_n_components_yr_win1
unit: 连通分量个数 (无量纲正整数计数; 年度银行共现网络的连通分量数)
formula: "net_n_components_yr = |{年度银行共现图 G_t 的连通分量}|; G_t 节点=当年被报道的目标银行, 边=两家银行在同一判据窗内被共现提及; 判据变体 {同篇(无后缀)/±1句窗 _win1/严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py (compute_bank_network_centrality) ; news_process/pipeline/panel/export.py (标签)
upstream:
- 13_cooccurrence_filter.parquet
- 40_panel_yearly.parquet
citations:
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
- doi: 10.1111/jofi.13010
  type: journal
  authors: Duarte, F., & Eisenbach, T. M.
  year: 2021
  title: "Fire-sale spillovers and systemic risk"
  venue: The Journal of Finance
  vol: 76
  issue: 3
  pages_or_artno: 1251-1294
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
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
- doi: 10.1103/PhysRevE.69.026113
  type: journal
  authors: Newman, M. E. J., & Girvan, M.
  year: 2004
  title: "Finding and evaluating community structure in networks"
  venue: Physical Review E
  vol: 69
  issue: 2
  pages_or_artno: 026113
- doi: 10.1103/PhysRevE.70.066111
  type: journal
  authors: Clauset, A., Newman, M. E. J., & Moore, C.
  year: 2004
  title: "Finding community structure in very large networks"
  venue: Physical Review E
  vol: 70
  issue: 6
  pages_or_artno: 066111
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1016/0378-8733(83)90028-X
  type: journal
  authors: Seidman, S. B.
  year: 1983
  title: "Network structure and minimum degree"
  venue: Social Networks
  vol: 5
  issue: 3
  pages_or_artno: 269-287
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
new_dois: []
---

## CORE

【构念与来源】
本家族刻画年度银行共现网络的整体连通结构, canonical 列 net_n_components_yr 定义为该网络的连通分量个数 (number of connected components)。构造对象是一张逐年重建的无向图: 在给定日历年内, 节点集合为当年被媒体报道触及的目标银行, 边集合为在同一判据窗口内被共同提及 (co-mention) 的银行对。所谓连通分量, 是指图中彼此可经由若干条边互相到达、而与图中其余节点不相连的极大节点子集; 连通分量个数即把整张网络切分成的这类互不相连团块的数目。直觉上, 该计数是网络碎裂程度 (fragmentation) 的最粗粒度概括: 当某一年里所有被报道银行都通过共现链条串成一张连通大图时, 连通分量数趋近于 1; 当媒体叙事把银行群体割裂成若干互不交叉的话语簇 (例如国有大行簇、区域城商行簇、互联网系银行簇彼此不被同篇报道并置) 时, 连通分量数随之上升。因此该变量与同族的巨分量占比 net_giant_share_yr、模块度 net_modularity_yr、网络直径 net_diameter_yr 共同构成对"整个银行舆论场是一体还是分裂"的互补刻画, 但连通分量数最直接地对应拓扑意义上的分块计数, 不依赖社区发现算法的分辨率参数, 也不依赖对最大分量的挑选。

数据来源上, 边的判定原始物料来自上游 stage 13 共现硬过滤后的文章级语料与银行实体标注。判据原语是 core/text/entity_context 中的 map_bank_sentence_positions 与银行对句窗共现例程, 逐句扫描每篇报道 (标题经 prepend 后作为第 0 句) 中未被排除的银行实体出现位置, 再据判据窗口把落入窗内的银行两两连边。此处的判定主体是"银行与银行"的共现, 与 stage 13 上游"银行与金融科技"的过滤口径是两个正交的概念空间, 二者所用的窗口配置键亦不同: 网络判据窗口取 config/panel.yaml 的 network_criteria.win_radius (默认 1), 而 stage 13 银行金科过滤取 config/filtering.yaml 的 cooccurrence_filter.sentence_radius, 两键互不联动。银行实体识别沿用与 stage 11/13 及三轨物化共享的同一否定与短名排除事实源 (禁裸 Aho-Corasick 匹配, 以防"涉农行业"误触发"农行"一类短名假阳性), 保证网络构造所用的银行边与情感三轨所用的银行判定同源同标准。

【方法学与计算】
计算在 pipeline/panel/network_spillover.py 的 compute_bank_network_centrality 中完成, 使用 networkx 承载图对象。对每个年份 t, 引擎先聚合当年全部报道中满足判据的银行对边 (共现次数可作为边权供加权度量使用, 但连通分量的判定只关心边是否存在, 与权重无关), 构造无向图 G_t, 随后调用连通分量枚举得到分量个数并写入 net_n_components_yr。孤立点 (当年被报道但从未与其他银行共现的银行) 在此语义下各自构成一个大小为 1 的分量, 因此连通分量数天然把边缘银行的孤立状态计入碎裂度, 这与同族部分中心度量对平凡分量的处理不同: 例如特征向量类中心度对小于最小分量门槛 (_CMNT_MIN_COMPONENT_SIZE = 3, 即最小三角) 的孤立点或单边对会被置为缺失, 而连通分量计数不做此类掩码, 忠实反映分块总数。该变量是网络级 (network-level) 广播度量, 即同一年内所有银行取同一个值, 因此在带年份固定效应的面板回归中会被年 FE 吸收而不可单独识别, 其用途主要是刻画时间维度上银行舆论网络整体连通性的演化、作为跨年描述统计与稳健性叙事的组成部分, 以及在不含年 FE 的横截面或时序设定中作为网络结构协变量。该列是 NETWORK_METRIC_BASES 这一 33 个结构指标基名单一事实源中的一员, stata_export 的判据标签机械块与门控测试对该基名单 import 复用以防命名漂移, 镜像 encode 层模型清单的先例。

【文献定位】
连通分量作为图的最基本连通性统计, 其方法学根系可追溯到社会网络分析对结构与连通性的经典刻画。Freeman (1978) 对中心性概念的厘清奠定了以节点在连通结构中位置刻画其重要性的范式, 而连通分量数则是与之互补的整体层面统计, 回答"网络是否被切成多块"而非"某点多重要"。Watts 与 Strogatz (1998) 揭示的小世界现象说明真实网络往往在高聚类的同时保持全局可达, 连通分量数正是检验这一"全局是否一体"性质的门槛量: 单一巨分量是小世界的前提。社区结构文献进一步细化了"块"的概念, Newman 与 Girvan (2004) 以及 Clauset、Newman 与 Moore (2004) 发展的模块度优化与快速社区发现方法刻画的是连通图内部的软性分块, 与连通分量所刻画的硬性 (拓扑不可达) 分块形成层次互补——本家族同族的 net_modularity_yr 正对应前者, net_n_components_yr 对应后者。Newman (2005) 的随机游走介数、Seidman (1983) 的 k-核分解则从中间性与稠密核心两个侧面补足了对同一共现图的结构画像, 与连通分量数共处同一 NETWORK_METRIC_BASES 家族。

在金融与经济学脉络中, 连通结构直接关联系统性风险与同伴效应两条主线。Jackson 与 Pernoud (2021) 对金融网络系统性风险的综述指出, 机构间连通性的拓扑形态决定冲击的传染路径与放大程度, 一体化 (低分量数) 网络在提供风险分散的同时也可能成为传染高速路; Duarte 与 Eisenbach (2021) 对火线抛售溢出的度量同样以机构间的连通与重叠为传染载体。就本项目而言, 银行共现网络虽是媒体话语层面的关联而非资产负债表层面的暴露, 但其连通分量数刻画的正是"银行群体在公共叙事中是否被作为一个相互关联的整体来讨论", 这与舆论驱动的信心传染 (媒体情绪在关联银行间的溢出) 直接呼应。同伴效应识别文献为此提供了计量地基: Manski (1993) 的反射问题指出内生社会效应识别的根本困难, Bramoullé、Djebbari 与 Fortin (2009) 证明网络拓扑的差异 (尤其是非完全连通、存在多分量或不同邻接结构) 可为同伴效应提供识别所需的排除性变异, 其 2020 年综述进一步系统化了这一识别策略。连通分量数作为拓扑异质性的最粗概括, 恰是这类识别赖以成立的网络结构变异的可观测标度。Grieser 等 (2022) 关于网络效应对公司财务政策的证据、Yu、Hu 与 Zhong (2024) 关于网络中心性与信息扩散和资产定价的证据, 以及 Nezami、Chisam 与 Palmatier (2025) 对网络中心性与企业绩效关系的元分析, 共同表明网络位置与连通形态是解释企业与金融机构结果变量的一类稳健协变量, 为将网络结构指标纳入银行面板提供了实证正当性 (该元分析对具体度量如聚类系数持保留态度, 本家族据此仅将连通分量数用作结构描述与稳健性协变量, 不对其单独因果解读)。

【识别策略定位】
本家族在识别上的角色须严格区分两个层次。第一, net_n_components_yr 是纯网络级年度广播量, 在主线银行年面板的带双向固定效应 (银行 FE + 年 FE) 设定下会被年 FE 完全吸收, 因而不可作为主处理变量进入这类回归; 其识别价值体现在不含年 FE 的时序描述、跨年结构演化叙事, 以及作为工具变量族或网络结构控制的构造原料 (同伴效应 IV 与 Bartik 类构造依赖网络拓扑的时变结构, 连通性演化是其合法性诊断的一部分)。第二, 更重要的是本家族三列构成判据敏感性梯子: 同篇 (无后缀 canonical)、±1 句窗 (_win1)、严格同句 (_sent) 三种银行邻接判定各自独立地重建全年网络并各自计算连通分量数。这三条判据轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J——即禁止把三种判据下的同一构念度量当作过度识别工具集塞进单一 Hansen 过度识别检验, 因为它们是对同一潜在网络结构的替代测量而非独立矩条件。该口径与项目全局的三轨文本 (full/ctx/ss)、co-primary 双轨嵌入、词典消融/政治词权重/BERT 阈值等梯子的稳健性并排原则一脉相承。须特别强调: 网络判据后缀 (无后缀/_win1/_sent) 与三轨文本后缀 (_full/_ctx/_ss) 是两个正交概念空间, 前者刻画银行∧银行邻接的空间紧邻度, 后者刻画银行∧金科文本的语境窗口, 二者绝不可混入同一 Hansen J, 亦不可字面拼配。

【与相邻测度的构念区分】
连通分量数须与同族三个易混指标划清边界。其一, net_giant_share_yr (巨分量占比) 度量最大连通分量所含节点占全网节点的比例, 与分量个数负相关但并不冗余: 一年可能既有一个覆盖八成银行的巨分量、又有数个零散小分量, 此时巨分量占比高而分量数亦不低, 两者从"最大块多大"与"共分几块"两个角度描述碎裂。其二, net_modularity_yr (模块度) 度量连通图内部的社区划分优度, 是软性分块, 即便网络只有一个连通分量, 模块度仍可揭示其内部子群结构; 连通分量数则只认拓扑不可达的硬边界。其三, net_density_yr (网络密度) 度量实际边数占最大可能边数之比, 是稠密度而非连通块数, 高密度必然意味着少分量但反之不成立。此外, 连通分量数与节点级度量 (如 bank_degree_cent、bank_clustering) 处于不同分析单元: 后者逐银行取值、可进入带年 FE 的面板作节点异质性刻画, 前者是全网单值。厘清这些区分, 方能避免在稳健性叙事中把"碎裂度上升"误读为"密度下降"或"社区增多"。

【度量的解释含义与经济语义】
须审慎界定连通分量数在本项目语境下的经济解释边界。银行共现网络是媒体话语层面的关联而非资产负债表层面的风险暴露: 一条边表示两家银行被同一 (判据窗内的) 媒体叙事并置提及, 它捕捉的是公众与市场对两家机构"是否被作为相关联的一组"来认知与讨论, 而非它们之间真实存在同业拆借、担保或交叉持股。因此连通分量数下降 (网络趋于一体) 的经济含义是"银行群体在公共叙事中被越来越多地关联讨论", 这可能源于系统性事件 (如行业性监管新规、金融科技冲击、流动性紧张时期) 使得银行被媒体成批并列评述; 反之分量数上升 (网络碎裂) 意味着银行被分门别类地、彼此隔离地报道, 常见于平稳时期各机构各自的常规经营新闻互不交叉。正因如此, 该度量与舆论驱动的信心传染研究呼应: 当银行在叙事上被高度关联 (低分量数) 时, 针对某一机构的负面情绪更易被读者外推至被并置的同类机构, 这与关于社交媒体加速银行挤兑、媒体情绪影响存款稳定与银行系统性风险的近期证据在机制上同源。但须强调, 本项目仅将连通分量数用作结构描述与稳健性协变量, 不对其赋予单独的因果解读——网络中心性与企业绩效关系的元分析亦提示对具体网络度量须持审慎态度, 避免把话语关联的拓扑统计过度解读为因果暴露。使用者在论文中援引本家族时, 宜将其定位为刻画"银行舆论场整体连通性演化"的描述性结构指标, 及同伴效应识别与网络工具变量构造的拓扑诊断量, 而非独立的处理或结果变量。

【与项目全局稳健性架构的对齐】
连通分量数所处的判据敏感性梯子并非孤立设计, 而是项目"以并排替代测量证明主结论不被单一构造选择驱动"这一方法论在网络拓扑维度的落地。项目在情感测度上以三轨文本 (full/ctx/ss) 并排、以 co-primary 双轨嵌入 (Qwen3 无后缀轨与 text-embedding-3-large 的 _lg 轨) 并排、以词典规则消融 (否定翻转/程度副词/转折的全 powerset 变体) 并排、以政治词权重梯子 (0.0/0.5/1.0 三档) 并排、以 BERT 极端负面阈值梯子 (0.80/0.90/0.95) 并排、以 LLM 三家与 BERT 三模型跨厂商并排, 每一条梯子的共同宪法条款都是: 各变体各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J。网络判据三轨 (无后缀/_win1/_sent) 是这一宪法在"银行邻接空间紧邻度"维度的实例。之所以严禁把三判据变体塞进同一 Hansen 过度识别检验, 根本原因在于它们是对同一潜在网络结构的替代测量 (measurement replicates), 彼此高度相关且共享同一构念内核, 不构成相互独立的矩条件; 若强行并入过度识别工具集, Hansen J 的零假设 (全部工具外生) 将因测量冗余而被机械性地无法拒绝或错误拒绝, 使检验丧失诊断意义。正确用法是把三判据轨分别代入各自 just-identified 的设定, 观察系数符号与显著性是否跨判据稳定, 以走势一致性而非联合矩检验来支撑稳健性结论。这与跨模型真 FWER 检验只在根级 rwolf 模板 (针对同构念替代测量 headline) 实现、而 paper_spec 内的跨模型声明仅作文档而无运行时消费者的架构选择, 属同一治理逻辑: 替代测量的多重性用符号稳健性叙事管理, 不滥用为过度识别工具。使用者在撰写论文稳健性章节引用本家族三列时, 须复述该口径, 避免审稿人误以为三判据可联合进入一次 GMM 过度识别。

【已知局限与稳健性梯子】
局限有三。第一, 连通分量数对判据窗口高度敏感: 严格同句 (_sent) 判据最苛刻, 连出的边最少, 因而网络最碎、分量数最高; 同篇 (无后缀) 判据最宽松, 边最多, 网络最连通、分量数最低; ±1 句窗 (_win1) 居中。这一单调关系本身即是三列并排提供的稳健性信息——主结论不应被判据窗口的具体选择驱动。第二, 该度量在小样本年份或试跑面板 (T=2 开发态) 上可能退化: 当某年被报道银行极少或几乎两两共现时, 分量数逼近 1 而近零方差, 此属预期退化而非缺陷, 生产 T=18 全量语料下方能体现其时序变异。第三, 作为年度广播量, 它无法在双向固定效应设定中单独识别, 使用者须在无年 FE 或跨年描述语境中消费。第四, 连通分量数对语料覆盖的选择效应敏感: 若某年某类银行被媒体系统性地少报道, 其节点可能整体缺席网络或退化为孤立点, 从而抬高分量数, 这一测量误差在跨年比较时须以样本框稳定性 (被报道银行集合的年度可比性) 为前提审视, 不可将报道覆盖变动误读为真实结构碎裂。稳健性叙事上, 三判据轨的一致性 (三列随年份的走势是否同向) 是核心检验; 与同族巨分量占比、模块度、直径的联合解读可交叉验证碎裂结论; 因连通分量判定与边权无关, 该度量对共现次数的加权方案、对情感三轨的选择均免疫, 具有相对稳健的构造性质。相较之下, 依赖最短路或谱分解的中间性、特征向量类中心度会随边权与分量掩码门槛 (最小三角 _CMNT_MIN_COMPONENT_SIZE) 产生 BLAS 浮点级非确定漂移, 而纯拓扑的连通分量计数枚举结果确定可复现, 这使其在 golden 逐位复现校验中属零漂移列, 是构造稳健性的又一佐证。须再次锚定项目铁律: 三判据各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J; 该家族属非嵌入的纯拓扑计数, 无 co-primary 的 _lg 孪生列, 亦不参与 full-only 留篇门控口径 (留篇门控只由 llm_verified_full 决定, 与网络构造无关)。

## VAR: net_n_components_yr

【变体差分】
本列是家族 canonical (无判据后缀), 采用同篇共现判据: 只要两家银行在同一篇报道内 (标题 prepend 后与全文正文合并的整篇文本范围内) 各自出现且均未被短名/否定排除规则剔除, 即在当年网络中连一条边, 不要求二者出现在相邻句或同一句。这是三条判据轨中最宽松的邻接标准, 因而所连边最多、网络最连通, 相应地连通分量数在三轨中系统性最低 (碎裂度最小)。它是现行生产口径, 也是 NETWORK_METRIC_BASES 单一事实源登记的基名, 同族其余 32 个结构指标的无后缀列与之共享同一张同篇判据网络。语义上, 该列回答的是"以整篇报道的话语并置为关联标准时, 全年银行舆论场被切分成几个互不相连的团块": 值为 1 表示当年所有被报道银行经由同篇共现链条串成一张连通图, 值越大表示媒体叙事把银行群体割裂成越多互不交叉的话语簇。作为网络级年度广播量, 该列在带年份固定效应的银行年面板中会被年 FE 吸收而不可单独识别, 其消费场景为不含年 FE 的时序结构描述、跨年碎裂度演化叙事, 以及作为网络拓扑控制变量与同伴效应工具变量构造的诊断原料。计算调用 networkx 的连通分量枚举, 孤立银行 (当年被报道但无任何同篇共现伙伴) 各计为一个大小为 1 的分量而不做掩码, 忠实计入碎裂总数——这与本家族部分节点级中心度量对小于最小三角门槛 (_CMNT_MIN_COMPONENT_SIZE = 3) 的平凡分量置缺失的处理刻意不同。须锚定: 本列与其 _win1、_sent 两个判据变体互为稳健性、不分主次, 三者各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 判据后缀 (此处为无后缀) 与三轨文本后缀 (_full/_ctx/_ss) 是两个正交概念空间, 绝不可拼配或混入同一 Hansen J。因判定只依赖边的存在与否, 本列对共现边权、情感轨道选择均免疫, 是家族中构造最稳健的碎裂度基准。就与同族相邻测度的边界而言, 本列须与同为同篇判据无后缀的巨分量占比 net_giant_share_yr、模块度 net_modularity_yr、网络密度 net_density_yr 划清: 巨分量占比问"最大团块占全网多大", 本列问"共分几个团块", 二者负相关却不冗余 (一年可同时存在覆盖多数银行的巨分量与若干零散小分量, 使占比高而分量数亦不低); 模块度刻画的是连通图内部的软性社区划分, 即便全网只有一个连通分量, 模块度仍可揭示其内部子群, 而本列只认拓扑不可达的硬边界; 密度刻画实际边数占最大可能边数之比, 是稠密度而非分块计数。就分析单元而言, 本列是全网单值的年度广播量, 与逐银行取值、可进入带年 FE 面板的节点级度量 (bank_degree_cent、bank_clustering 等) 处于不同层次, 使用者不可将本列与节点级列混入同一自变量集当作同层控制。在稳健性叙事中, 本列作为最宽松判据下的碎裂度下界, 与 _win1 中间值、_sent 上界共同勾勒连通分量数随邻接标准收紧而单调上升的完整轮廓, 三值的同向演化 (而非某一判据的孤立取值) 才是可援引的稳健性证据; 开发态 T=2 面板上本列可能因银行两两同篇共现而逼近 1、近零方差, 属预期退化, 须以生产 T=18 全量语料的时序变异为准。

## VAR: net_n_components_yr_sent

【变体差分】
本列为严格同句判据变体, 邻接标准最苛刻: 只有当两家银行在同一句子内被共同提及 (二者的实体出现位置落在同一句, 标题作为第 0 句同样参与扫描) 时, 才在当年网络中连边; 跨句共现即便同篇也不连。相对 canonical 的同篇判据与 _win1 的 ±1 句窗判据, 严格同句连出的边最少, 因而网络最碎、连通分量数在三轨中系统性最高 (碎裂度最大)。判据原语沿用 map_bank_sentence_positions 逐句定位银行位置后取严格同句共现的银行对, 与 canonical 共享同一套否定/短名排除事实源, 差异仅在邻接窗口收紧至同句。语义上, 本列回答"当把邻接标准提高到必须同句并置时, 全年银行网络被切成几块": 由于同句并置往往对应更紧密、更明确的语义关联 (如两家银行在同一句里被比较、并列或关联评论), 本列刻画的是最保守、最少假阳性的连通结构, 相应分量数偏高反映了大量仅在篇章层面松散并置、却从不同句共现的银行对被判为不相连。本列与 canonical、_win1 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J——三列随年份走势的一致性是核心稳健性检验, 主结论不应被判据窗口的松紧选择驱动。同为网络级年度广播量, 本列在双向固定效应设定下被年 FE 吸收, 适用于无年 FE 的结构描述与稳健性叙事。判据后缀 _sent 与三轨文本后缀 _ss 分属正交概念空间 (前者银行∧银行同句邻接, 后者银行∧金科同句语境窗), 绝不可混淆; 本列亦为纯拓扑计数, 无 _lg 嵌入孪生。开发态 T=2 上, 严格同句判据可能使多数银行无同句共现伙伴而致分量数逼近节点数、近零方差, 属预期退化, 生产 T=18 方显时序变异。

## VAR: net_n_components_yr_win1

【变体差分】
本列为 ±1 句窗判据变体, 邻接标准居于同篇 (canonical) 与严格同句 (_sent) 之间: 当两家银行的实体出现位置落在彼此相距不超过 win_radius 句 (默认取 config/panel.yaml 的 network_criteria.win_radius = 1, 即目标句及其前后各一句构成的滑动窗口) 时连边。相对严格同句放宽了一句的容差以捕捉跨相邻句的紧邻并置 (如上一句点名甲行、下一句评论乙行的连续叙述), 又相对同篇收紧以排除仅在篇章两端遥隔出现的松散并置。因此本列连出的边数、网络连通性与分量数均系统性居于三轨之中: 分量数低于 _sent、高于 canonical。判据原语在 map_bank_sentence_positions 定位后取句窗内银行对, 窗口半径来自 network_criteria.win_radius, 须再次强调该键与 stage 13 银行∧金科过滤所用的 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键、互不联动。本列与 canonical、_sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; ±1 句窗提供的中间松紧度, 使三列共同构成对连通分量数随邻接标准单调变化的完整刻画, 支撑"主结论不被判据窗口选择驱动"的稳健性论证。判据后缀 _win1 与三轨文本后缀分属正交空间, 不可拼配。本列同为网络级年度广播量, 双向固定效应下被年 FE 吸收, 消费于无年 FE 的结构描述与拓扑控制; 亦为纯拓扑计数, 无 _lg 嵌入孪生, 不涉 full-only 留篇门控。计算沿用 networkx 连通分量枚举, 孤立银行计为大小 1 分量不掩码, 与 canonical 处理一致, 保证三判据轨的唯一差异恰为邻接窗口半径而无其它混淆。

<!-- rendered-citations:begin -->
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. Physical Review E, 70(6), 27721. https://doi.org/10.1103/PhysRevE.70.066111
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
<!-- rendered-citations:end -->
