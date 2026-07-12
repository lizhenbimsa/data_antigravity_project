---
family_id: F462
columns:
- net_diameter_yr
- net_diameter_yr_sent
- net_diameter_yr_win1
unit: 无量纲整数 (最长最短路的跳数/边数; 巨片内节点对间最短路径的步数上确界)
formula: "net_diameter_yr = max_{v∈LCC} eccentricity(v) = LCC 内无权 BFS 意义下最长的最短路; 当 |LCC 节点| ≥ 2 时取值, 否则 NaN。判据变体 {同篇 (无后缀) / ±1 句窗 (_win1) / 严格同句 (_sent)} 只改银行∧银行成边判据, 直径算法本身不变"
producer: news_process/pipeline/panel/network_spillover.py::_net_level_extra_metrics (经 compute_bank_network_centrality 落列; 标签在 pipeline/panel/export.py)
upstream:
- 13_cooccurrence_filter.parquet (docid, target_bank, 内容, 标题 → 银行∧银行共现邻接)
- 40_panel_yearly.parquet (bank-year 行骨架)
citations:
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
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1103/PhysRevE.70.066111
  type: journal
  authors: Clauset, A., Newman, M. E. J., & Moore, C.
  year: 2004
  title: "Finding community structure in very large networks"
  venue: Physical Review E
  vol: 70
  issue: 6
  pages_or_artno: 066111
- doi: 10.1103/PhysRevE.69.026113
  type: journal
  authors: Newman, M. E. J., & Girvan, M.
  year: 2004
  title: "Finding and evaluating community structure in networks"
  venue: Physical Review E
  vol: 69
  issue: 2
  pages_or_artno: 026113
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
本家族刻画银行共现网络的年度直径 (annual co-mention network diameter), 是一个网络级 (network-level) 结构指标: 对每一自然年, 把当年新闻语料中被同时提及的银行两两连边, 得到一张年度无向共现图, 再在其最大连通分量 (largest connected component, LCC) 上度量"两家最遥远银行之间的最短路径长度"。直径回答的问题是: 在这张由媒体共同提及所织成的关系网里, 信息或情绪要从网络一端传到另一端, 最坏情况下需要经过多少次"中转"。它与本项目其余 32 个共现网络指标同源, 共享唯一事实源 network_spillover.NETWORK_METRIC_BASES (33 基名元组), 由 compute_bank_network_centrality 统一产出, 标签在 export.py 机械落列, 保证审计脚本、stata_export 判据标签块与 gate 测试三处 import 复用、口径不漂移。数据来源上游是经 stage 13 银行∧金科共现硬过滤后的文章级展开帧 (docid × target_bank, 携 内容/标题), 与 bank-year 面板骨架合并后按年建图。

直径的语义根植于社会网络分析的经典构念谱系。Freeman (1978) 奠定了中心性的概念澄清: 度、介数、接近度分别对应"活动量""中介控制""可达效率"三种直觉; 直径不是节点级中心性, 而是整张图的一个全局尺度量, 描述网络的"跨度"或"直径宽度"。它与接近度 (closeness) 互补——接近度问单个节点到其余所有节点的平均距离, 直径问全网所有节点对里最坏的那一对距离。Watts 与 Strogatz (1998) 的小世界模型把"特征路径长度"提到网络科学的中心位置: 稀疏但高聚类的真实网络往往具有出人意料的短路径, 少数长程连边即可把直径从线性尺度压缩到对数尺度。银行共现网络若呈小世界特征, 其直径会远小于节点数, 意味着任意两家银行都能通过很少几步媒体共现相连; 直径若随年份收缩, 通常提示网络因媒体叙事聚焦而更加"抱团"、跨行溢出的结构距离在缩短。

【方法学与计算】
落地算法在 _net_level_extra_metrics 内: 复用已构建的年度图 G 与其最大连通分量 G_lcc, 当 LCC 节点数 ≥ 2 时, 取 G_lcc 上所有节点偏心率 (eccentricity) 的最大值即为直径, 亦即 max_{v} eccentricity(v); 偏心率本身是该节点到 LCC 内其余任一节点最短路径长度的最大值, 因此"偏心率的最大值"恰是最长的最短路。计算严格采用无权 (unweighted) BFS 口径: 边权 (共现频次) 只用于建图判定是否有边, 不参与最短路的距离累加, 每条边一律记作 1 跳。这一点在源码注释里被特别标注为"复用 G_lcc 对象、非 G_inv_lcc 加权 ecc", 是刻意的口径选择——直径度量的是拓扑意义上的"结构距离/中转次数", 而非加权意义上的"共现强度累积成本"。当 LCC 退化 (孤立点、单节点、空图, 即有效节点不足 2) 时优雅置 NaN, 不抛异常; networkx 在不连通图上直接求直径会 raise NetworkXError, 因此代码只在 LCC 上求 ecc 并以 try 捕获, 属 fail-soft 设计。

一个对确定性至关重要的性质: 直径是整数值, 由 BFS 逐跳计数产生, 全程无浮点累加、无特征分解、无随机初始化, 因此 net_diameter_yr 是完全确定性、golden-safe 的列。本项目已知的 BLAS 浮点非确定网络列共 9 个 (bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 各自的无后缀/_win1/_sent 三判据变体), net_diameter_yr 及其判据孪生均不在其中——重生 golden 快照时无须把本家族任何列纳入 _KNOWN_BLAS_RE 排除清单, 逐位可复现。在 T=2 开发语料 (约 220 行, 110 家银行 × 2 年) 上, 巨片规模常较小、直径取值域窄, 属规模退化的预期表现; 生产 T=18 (2007–2024, 1700 万条报道) 语料下年度图节点数与巨片跨度显著放大, 直径分布方有充分的年际变异, 才能作为溢出结构演化的稳健叙事变量使用。也正因为直径在小图上取值域窄、在大图上方见变异, 解读时严禁把开发语料上的退化取值外推为生产结论——本列的经济含义只在生产规模的年度网络上才真正稳定成立, 这一规模依赖性是网络级结构量的共性而非本列独有缺陷。

【数据构造细节】
年度图的建边过程决定了直径的一切统计性质, 须交代清楚。同篇主路径 (criterion='article') 直接以文章级展开帧的 target_bank 共现关系建对称邻接: 同一 docid 内每一对存活目标银行连一条边、每篇每对权重累加一。判据分轨路径 (_win1/_sent) 则对每个含两家及以上银行的 docid 组重扫正文与标题, 先用 map_bank_sentence_positions 把各银行别名定位到具体句序号 (标题作为第 0 句前置, 镜像 stage 13 的 match_in_title 口径), 再由 bank_pairs_within_sentence_window 按句距阈值判定成对。这一路径刻意复用与 stage 11/13/ctx/ss 同一份否定 AC 自动机与短名排除事实源, 严禁裸 Aho-Corasick 匹配, 以堵住"涉农行业"被误判为"农行"这类短名假阳性——若假阳性泄漏进邻接, 会凭空制造桥接边、系统性压低直径。源码另设两道 fail-soft 防线: 同一 docid 组内正文不一致时 loud WARN 并取组首行 (镜像 FINTECH_AC=None 优雅降级先例, 该分支仅在同一 docid 携多份不一致正文时触发, 属极少见的上游脏数据情形); 缺 docid 或"内容"列时该年判据邻接置全零 (节点保留、无边), 而非崩整个 stage。这些设计保证直径在脏数据面前退化为保守值 (更碎、更短或 NaN) 而非抛异常中断。值得单列的是, hyperedge_normalize (Newman 1/(N-1) 超边归一) 是 article 主路径独有的预留参数且在判据分轨路径被显式 raise 禁用, 以防三判据轨在无警告下口径分叉——但该参数对无权直径本就无影响, 此守卫是对整个网络指标族的统一防线而非直径特有。

【文献定位】
直径这一构念在图论上还有一层"最坏情形保证"的意味, 对本项目的经济解读尤为贴切。若把年度共现网想象成情绪或叙事在银行之间传播的潜在通道, 那么平均路径长度描述的是"一条消息平均要走多远", 直径描述的是"一条消息在最不利的起点—终点组合下最多要走多远"。当媒体把某几家银行密集地并列报道时, 这几家银行会形成紧密子团、彼此距离为一, 但若这些子团之间缺少桥接性报道, 整张网的直径就会被"团与团之间的空隙"撑大。因此直径对网络的宏观形态高度敏感: 一个由若干紧密小团经少数长程边串起来的链状结构, 其直径远大于一个各处均匀相连的稠密图。银行共现网若逐年直径收缩, 通常对应两种情形之一——要么媒体叙事更趋同 (更多银行被写进同一篇金融科技报道、桥接边增多), 要么某些原本孤立的银行被拉入主叙事巨片; 二者都意味着"跨行结构距离"在缩短、潜在溢出更易跨越整张网。这一解读与本项目把共现网视为情绪溢出载体的核心假设一脉相承, 也解释了为何直径与巨片占比、连通分量数被归入同一组 net_* 网络级结构控制、须联读。

在实证金融的语境里, 网络级结构尺度已被反复证明与信息扩散、系统性风险和公司决策相关。Jackson 与 Pernoud (2021) 系统综述金融网络中的系统性风险, 强调网络拓扑 (连通度、路径长度、集中度) 决定冲击如何跨机构传导; 直径作为"最坏可达距离"是刻画传导链条最大跨度的自然量。Yu, Hu 与 Zhong (2024) 与 Xu, Zhao (2024) 分别从信息扩散—资产定价和节点中心性—价格预测两条线, 提供了"金融网络结构承载定价相关信息"的近年证据; Nezami, Chisam 与 Palmatier (2025) 以元分析汇总了中心性与企业绩效的关系, 提示网络位置的经济后果具有跨情境稳健性 (但其注册表注明确不背书具体某个中心性算法的因果解读, 本项目沿用此谨慎口径, 将网络结构变量定位为描述性/控制性协变量而非因果处理)。社区结构文献 (Newman & Girvan 2004; Clauset, Newman & Moore 2004) 与直径互为补充: 直径刻画全网跨度, 模块度刻画分块紧密度, 二者共同勾勒共现网的"松散/抱团"形态, 在本项目中并列为 net_* 网络级结构控制族。银行业媒体—网络的中国制度语境可参照 Zhang 与 Li (2026) 对金融科技驱动网点网络扩张的研究, 为"银行间关系网年际重构"提供了机构层面的现实背景。Grieser 等 (2022) 则以公司财务政策的网络效应示范了把同伴网络结构接入财务面板的完整实证范式, 是本项目把共现网直径等结构量与银行财务哨兵列对接的方法论参照; 其强调网络结构变量须与恰当的固定效应结构配合、避免把网络级广播量误当截面处理, 恰是本家族反复申明的识别边界。整体而言, 本家族在文献坐标上处于三条脉络的交汇处: 社会网络分析的结构度量传统 (Freeman 1978; Watts & Strogatz 1998), 同伴效应识别的计量经济学 (Manski 1993; Bramoullé, Djebbari & Fortin 2009; Bramoullé 等 2020; Boucher 等 2024), 以及金融网络与系统性风险的实证前沿 (Jackson & Pernoud 2021; Yu, Hu & Zhong 2024; Xu & Zhao 2024)。直径在这一坐标里是最粗粒度、最直观的全网跨度标尺, 与更精细的模块度、度分布、中心性分布并列, 共同为"银行共现网如何随媒体金融科技叙事演化、又如何承载跨行情绪溢出"这一核心问题提供结构侧的描述与诊断。

【识别策略定位】
必须清醒界定本家族在识别链条中的角色: 它是网络级 (年度广播) 变量, 对全体银行在给定年份取同一值, 因此在含年份固定效应 (year FE) 的规格中会被完全吸收, 不可作为主处理变量进入以银行—年为观测的双固定效应回归。这与源码注释对相邻 net_modularity_yr / net_assortativity_yr 标注的"year-FE absorbed"是同一道理。其正当用途有三: 其一, 作为纯时间序列的网络演化描述量 (逐年直径轨迹), 服务数据附录与机制叙事; 其二, 在放开年份 FE、以更粗时间维度 (如子样本或跨期) 比较的稳健性表中, 作为刻画网络结构状态的协变量; 其三, 作为构造节点级溢出权重矩阵 W 的结构诊断——直径、巨片占比、连通分量数共同判断"网络是否连通到足以让 peer 效应有意义"。同伴效应识别的经典难题即 Manski (1993) 的反射问题: 内生社会效应、外生情境效应与相关效应在线性均值模型中不可分。Bramoullé, Djebbari 与 Fortin (2009) 证明当网络存在"有间隔的间接连接" (即直径 ≥ 2、非完全图) 时, 邻居的邻居可作为工具, 令内生同伴效应重获识别; Bramoullé 等 (2020) 与 Boucher 等 (2024) 分别以综述和一般理论深化了这一识别基础。这正是本项目关心网络直径的深层动机: 直径 > 2 是"网络结构可用于识别"的必要拓扑前提, 直径退化为 1 (完全图) 则反射问题无解。Grieser 等 (2022) 进一步示范了如何用网络效应刻画公司财务政策的相互影响, 为把银行共现网结构接入财务面板提供了实证范式。

【与相邻测度的构念区分】
直径极易与三个相邻量混淆, 须逐一厘清。其一, 与 net_avg_path_yr (年度平均最短路径长度): 平均路径是巨片内所有节点对最短路的均值, 反映"典型"结构距离; 直径是同一分布的最大值, 对少数偏远节点极其敏感, 因此直径是网络跨度的上界刻画而非中心趋势刻画, 二者并列可揭示分布的偏斜。其二, 与 net_giant_share_yr (巨片占比) 和 net_n_components_yr (连通分量数): 后两者刻画网络的碎裂程度, 直径只在巨片内部度量, 当网络高度碎裂 (巨片很小) 时直径可能因巨片过小而人为偏低, 故解读直径必须与巨片占比联读, 避免把"碎裂导致的短直径"误读为"紧密导致的短直径"。其三, 与节点级偏心率/接近度: 直径是偏心率在全网取最大, 是一个标量而非逐银行列, 不携带"哪家银行处于边缘"的信息。此外, 直径采用无权 BFS, 与本项目加权中心性族 (bank_strength_cent 等 Opsahl 2010 口径) 在距离定义上正交, 不可互相替代。

【已知局限与稳健性梯子】
这里再补充直径与工具变量构造的具体接口, 以厘清本家族的方法论价值。本项目的溢出识别依赖以共现网邻接构造的空间权重矩阵 W (同组 leave-one-out 均值、广义 Bartik、媒体来源 house-style 暴露三引擎, 见 iv_extensions), 而 W 是否携带可用的识别力, 直接取决于底层网络的拓扑连通性: 若网络退化为完全图 (直径为一, 任意两银行皆直接相邻), 则"邻居的邻居"与"邻居"重合, Bramoullé, Djebbari 与 Fortin (2009) 型工具失效、反射问题重新无解; 若网络过度碎裂 (巨片极小、直径无从定义), 则大多数银行落在孤立分量、W 近似对角、溢出无从传导。直径连同巨片占比因此充当 W 有效性的"体检指标": 只有在直径 ≥ 2 且巨片覆盖足够多银行的年份, 网络型工具与二阶溢出列 (peer_tone_2nd_lag1_*) 才具备实质识别内容。Boucher 等 (2024) 的一般同伴效应理论进一步说明, 网络结构的异质性 (而非仅平均连接度) 是分离内生效应与情境效应的关键, 直径作为结构异质性的一个粗粒度标尺, 与模块度、度分布基尼等并列进入结构诊断集合。需要强调的是, 本项目全程把网络结构变量定位为描述性/诊断性协变量而非因果处理——Nezami, Chisam 与 Palmatier (2025) 的元分析虽确认中心性与绩效相关, 但其注册表明确不背书任一具体算法的因果解读, 本家族沿用此谨慎立场。

局限有四。其一, 直径对单条长程边极敏感: 一年内一篇把两家原本疏离银行并列提及的报道, 就可能把两个子团桥接、使直径骤变, 因此单年直径含噪, 宜看多年平滑趋势。其二, 整数取值域窄, 在小图上区分度低 (T=2 开发语料尤甚), 生产规模方稳定。其三, 网络级广播属性使其在主回归中被年份 FE 吸收 (见上), 非处理变量。其四, 建图依赖 stage 13 共现硬过滤的口径, 判据变动会改边集。正因单年直径含噪, 实证使用时宜取多年移动平均或趋势斜率而非逐年水平值作叙事变量, 把偶发长程桥接边引入的年际抖动平滑掉, 只保留结构演化的低频信号; 这一处理与本项目对其余网络级结构量 (巨片占比、模块度) 的多年平滑口径一致, 避免单篇报道的偶然并列驱动结论。针对建图判据这一自由度, 本家族提供三判据稳健性梯子: net_diameter_yr (同篇共现, canonical 无后缀)、net_diameter_yr_win1 (±1 句窗共现)、net_diameter_yr_sent (严格同句共现)。三者只改银行∧银行成边判据、直径算法本身逐字不变, 构成对"边定义宽严"的规格稳健性并排。铁律: 三判据变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混进同一 over-identified Hansen J 过度识别检验 (镜像本项目三轨 full/ctx/ss、co-primary 双轨嵌入、政治词权重梯子的同一口径); 该规格族属稳健性并排, 刻意不设 rwolf FWER 模板 (跨模型 FWER 先例仅覆盖同构念替代 headline 测量, 判据敏感性本族不适用)。另须强调: 判据后缀 (_win1/_sent) 与三轨文本后缀 (_full/_ctx/_ss) 是两个正交概念空间——前者是银行∧银行成边的句距判据, 后者是银行∧金科的情感文本轨道, 二者亦禁混同一 Hansen J; 且判据分轨路径的 win_radius 取自 config/panel.yaml::network_criteria.win_radius, 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键、互不联动。n_articles 与留篇口径遵循全项目 full-only 门控 (2026-06-29): 一篇是否计入建图语料以 full 轨留篇判定为准, 与本家族直径算法无关但共享同一上游行宇宙。

## VAR: net_diameter_yr

【变体差分】
本列是家族 canonical, 无判据后缀, 采用同篇 (article) 共现判据: 只要两家银行在同一篇报道 (同一 docid) 内被共同提及 (经 stage 13 银行∧金科硬过滤且经否定/短名排除后仍存活的目标银行), 即在当年图上连一条边、每篇每对权重 +1。这是三判据里最宽松的边定义——不要求两家银行出现在邻近句子, 只要同文即可, 因此它产生的年度图边最密、巨片最大、直径通常最小 (节点更易通过密边短路相连)。它是现行生产口径, 也是 NETWORK_METRIC_BASES 中登记的 net_diameter_yr 基名本体, 其余两列均在此基础上收紧成边判据派生。计算路径走 compute_bank_network_centrality 的 article 主路径 (suffix=''), 由 _net_level_extra_metrics 在最大连通分量上取偏心率最大值; 主路径独有 hyperedge_normalize 预留参数 (Newman 1/(N-1) 超边归一), 但该参数与直径无关且在判据分轨路径尚未接线。

作为 canonical, 本列承担家族对外的主叙事: 逐年直径轨迹刻画银行共现网的"结构跨度"如何随媒体金融科技叙事的聚焦或发散而演化。它是完全确定性的整数列 (无权 BFS 逐跳计数, 无 BLAS 浮点、无特征分解、无 RNG), 不在 9 个 BLAS 非确定网络列之列, golden 重生时逐位可复现、无须纳入排除清单。取值语义: 直径 = k 表示巨片内最遥远的两家银行需经 k 步媒体共现中转相连; 直径随年收缩通常提示网络更抱团、跨行结构距离缩短, 但须与 net_giant_share_yr 联读以排除"巨片碎裂导致的伪短直径"。识别层面, 本列是网络级年度广播变量, 在含年份 FE 的主回归中被完全吸收, 定位为网络结构演化的描述量与构造溢出权重 W 的连通性诊断 (直径 ≥ 2 是 Bramoullé, Djebbari 与 Fortin (2009) 意义下"邻居的邻居可作工具、反射问题可解"的必要拓扑前提), 而非因果处理变量。与家族内 net_avg_path_yr 的均值口径互补——本列取最大值、对偏远节点敏感, 刻画跨度上界而非中心趋势。

作为家族的现行生产口径, 本列的同篇判据在三判据里最宽松: 只要两家银行落在同一 docid 即成边, 不要求句距邻近, 因而边集最密、巨片最大、直径通常最小且最稳定, 这正是把它设为 canonical (无后缀基名) 的理由——它给出网络跨度的下界基准, 而 _win1/_sent 通过逐级收紧成边判据探测该基准对"边定义宽严"的敏感度。在与财务面板接续时, 本列的正当接口是: 逐年直径序列进入数据附录刻画共现网结构演化; 在放开年份 FE 的跨期/子样本稳健性表中作结构状态协变量; 以及作为 W 权重矩阵连通性的体检量 (直径 ≥ 2 时网络型工具方有识别内容)。须再次界定其边界: 本列对全体银行在给定年取同一值, 属网络级年度广播变量, 在以银行—年为观测、含年份固定效应的双固定效应主回归中被完全吸收 (与相邻 net_modularity_yr / net_assortativity_yr 的 year-FE absorbed 同理), 因此绝不可硬编码为主处理变量; 误把它塞进含年份 FE 的 RHS 会得到共线丢弃或系统性零系数, 属规格错误而非发现。与本列的两个判据孪生 net_diameter_yr_win1 / net_diameter_yr_sent 各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混入同一 over-identified Hansen J (镜像三轨 full/ctx/ss、co-primary 双轨嵌入、政治词权重梯子的统一铁律), 该判据族属规格稳健性并排、刻意不设 rwolf FWER 模板。

## VAR: net_diameter_yr_win1

【变体差分】
本列是同篇 canonical 的收紧判据变体, 采用 ±1 句窗 (win1) 共现判据: 两家银行仅当出现在彼此相距不超过 win_radius 句的窗口内 (win_radius 默认取 config/panel.yaml::network_criteria.win_radius=1) 才连边, 而非只要同文即可。计算走 compute_bank_network_centrality 的判据分轨路径 (criterion='win1', suffix='_win1'): 对每个多银行 docid 组重扫正文, 用 core/text/entity_context.map_bank_sentence_positions 定位各银行别名的句位置, 再由 bank_pairs_within_sentence_window 以 win_radius=1 判定成对邻近, 每对每篇对称 +1; 该路径复用与 stage 11/13 同一否定 AC 与短名排除事实源 (禁裸 AC, 防"涉农行业"→"农行"假阳性)。由于成边判据比同篇更严, win1 图边更稀、巨片更小、连边更"局部", 直径分布相对 canonical 通常上移或更易退化。它相对 canonical 的唯一差异就是边定义的句距阈值, 直径算法 (LCC 上无权 BFS 偏心率最大值) 逐字相同。判据后缀 _win1 与三轨文本后缀 _ctx 是正交概念——前者是银行∧银行句距, 后者是银行∧金科情感文本轨, 禁混同一 Hansen J; win_radius 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键、互不联动。相对同篇 canonical, win1 剔除了"同文但相隔多句"的松散并列, 保留的是"叙事上邻近"的共现, 因此它对共现关系的语义要求更高、对偶发的跨段并列更稳健, 是介于同篇 (最宽) 与同句 (最严) 之间的中间刚性档位。解读时须留意: win1 图边更稀会推高碎裂、缩小巨片, 直径既可能因巨片变小而人为偏低, 也可能因桥接边被剔除而升高, 方向不定, 故本列须与 net_giant_share_yr_win1 联读判别。本列与 canonical、_sent 三判据各自 just-identified 并排、互为稳健性、不分主次, 属对"成边句距宽严"的规格稳健性并排, 严禁混进同一 over-identified Hansen J, 且本族刻意不设 rwolf FWER 模板。

## VAR: net_diameter_yr_sent

【变体差分】
本列是三判据里最严的严格同句 (sent) 变体: 两家银行仅当在同一句内共同出现才连边, 对应判据分轨路径以 win_radius=0 调用 (criterion='sent', suffix='_sent') —— 源码内 radius = 0 if criterion=='sent' else win_radius, 即把句窗收缩到零、只认同句共现。计算同样走 map_bank_sentence_positions + bank_pairs_within_sentence_window (radius=0), 复用同一否定/短名排除事实源。严格同句是三判据中边集最稀疏的: 只有真正被写在同一句里的银行对才成边, 排除了跨句、跨段的松散并列, 因此 sent 图往往高度碎裂、巨片小、连通分量多, 直径在小巨片上取值域最窄、退化风险最高 (T=2 开发语料上尤为明显)。它相对 canonical 的唯一差异是把成边判据从"同文"收紧到"同句", 直径算法本身 (LCC 无权 BFS 偏心率最大值、|LCC|<2 置 NaN 的 fail-soft 守卫) 完全一致。解读本列须与其 net_giant_share_yr_sent / net_n_components_yr_sent 判据孪生联读, 严格区分"同句判据导致的网络碎裂"与"直径本身的短小"。判据后缀 _sent 与三轨文本后缀 _ss 是正交概念空间 (前者银行∧银行同句成边、后者银行∧金科同句情感轨), 禁混同一 Hansen J。本列与 canonical、_win1 三判据各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J (镜像三轨/co-primary 双轨嵌入/政治词权重梯子的统一铁律), 该族属规格稳健性并排、刻意不设 FWER 模板。

<!-- rendered-citations:begin -->
Zhang, X., & Li, Z. (2026). FinTech and branch network expansion: Evidence from China's banking industry. Applied Economics, 58(12), 2321-2336. https://doi.org/10.1080/00036846.2025.2476213
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. Physical Review E, 70(6), 27721. https://doi.org/10.1103/PhysRevE.70.066111
Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. Physical Review E, 69(2), 11339. https://doi.org/10.1103/PhysRevE.69.026113
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
<!-- rendered-citations:end -->
