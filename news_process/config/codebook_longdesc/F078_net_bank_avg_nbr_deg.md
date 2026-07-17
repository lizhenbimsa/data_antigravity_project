---
family_id: F078
columns:
- bank_avg_nbr_deg
- bank_avg_nbr_deg_sent
- bank_avg_nbr_deg_win1
unit: 无量纲 (加权平均最近邻度 ANND; 正实数, 有边节点下界为 1; 孤立节点 degree=0 置 NaN)
formula: "bank_avg_nbr_deg = k_nn,i^w = (1/s_i) · Σ_{j∈N(i)} w_ij · k_j, 其中 s_i = Σ_{j∈N(i)} w_ij 为节点 i 的加权度 (强度), k_j 为邻居 j 的无权度; 实现 = nx.average_neighbor_degree(G, weight='weight'), G.degree(i)=0 → NaN。判据变体 {同篇 (无后缀 canonical) / ±1 句窗 _win1 / 严格同句 _sent} 仅改边集, 不改节点集"
producer: news_process/pipeline/panel/network_spillover.py::compute_bank_network_centrality (Part B 指标 17 Average Neighbor Degree); 判据后缀标签推断 news_process/pipeline/panel/codebook.py::_strip_criteria_suffix
upstream:
- "24_herd_decay.parquet (article×bank 级 df_exploded: docid / target_bank / year / 内容 / 标题 — 共现网络节点与边的原语输入)"
- "bank-year 面板骨架 (runner 内存对象: pipeline/panel/runner.py 在面板构建流程内调用 compute_bank_network_centrality 并入指标列, 随后才导出为 40_panel_yearly.parquet — 该 parquet 是下游产物而非输入)"
- "config/bank_names.json (CONFIG['paths']['bank_names_file'], 见 config/paths.yaml: _win1/_sent 判据句级重扫所需银行别名字典) + config/bank_name_exclusions.json (load_exclusion_patterns: 否定 AC + 短名排除)"
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: 79-104
- doi: 10.1103/4pg6-mtmt
  type: journal
  authors: Kirkley, A.
  year: 2025
  title: "Fast nonparametric inference of network backbones for weighted graph sparsification"
  venue: Physical Review X
  vol: 15
  issue: 3
  pages_or_artno: "031013"
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
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1038/s42005-022-00856-9
  type: journal
  authors: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A.
  year: 2022
  title: "Meta-validation of bipartite network projections"
  venue: Communications Physics
  vol: 5
  issue: 1
  pages_or_artno: "76"
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
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
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A.
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: 3747-3752
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: 440-442
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: 157-191
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: 243-269
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
- doi: "10.1287/mnsc.2023.00475"
  type: journal
  authors: "Li, H., Xu, T., Qi, J., & Chen, Y.-J."
  year: 2026
  title: "Analyzing Network Formation Using Big Data Analytics: A Study of Degree Distribution, Clustering Coefficient, Diameter, and Assortativity"
  venue: "Management Science"
- doi: "10.1287/mnsc.2024.04492"
  title: "SPAC IPOs and Sponsor Network Centrality"
  authors: "Lin, C., Lu, F., Michaely, R., & Qin, S."
  year: 2026
  venue: "Management Science, 72(4), 3309-3331"
  type: "journal"
  one_sentence_zh: "该文以赞助人网络中心度研究 SPAC IPO 的资源整合与治理机制,为把网络位置结构指标用于金融实体关系分析提供近期方法学参照。"
new_dois:
- "10.1016/j.procs.2023.08.056"
- "10.1287/mnsc.2023.00475"
- "10.1287/mnsc.2024.04492"
---

## CORE

该文基于新闻文本构造中国金融企业共现网络并用 Louvain 社群检测揭示同行业企业连接更密的结构特征,为把新闻共现图上的节点/邻域结构指标用于金融实体关系分析提供了同期实证参照。

【构念与来源】
本家族刻画的是目标银行在年度新闻共现网络中的加权平均最近邻度 (weighted average nearest-neighbor degree, ANND), 即一家银行在被媒体同篇提及的伙伴银行群体中, 这些邻居本身在整张网络里连接得有多广。它回答的不是这家银行自己被多少家同行共同提及 (那是度中心度的问题), 而是与它共同出现的那些银行是不是也各自身处高连接位置。构念上, 平均最近邻度是度序关联 (degree-degree correlation) 在节点层的原子度量: 若一家银行的邻居普遍高度连接, 其 ANND 高, 反映它嵌在网络核心的稠密簇中; 若其邻居多为边缘的低度节点, 其 ANND 低, 反映它虽有连接却停在网络外围。数据来源是同一套新闻语料驱动的银行共现图, 节点为在给定年份幸存于面板的目标银行, 边为两家银行在同一媒体载体内的共同出现, 边权为共同出现的篇数。构念根系可追至度中心度的经典厘清 (Freeman, 1978): 度是网络位置最基础的操作化, 而平均最近邻度把注意力从自身度移到邻居度, 度量的是位置的位置。加权口径直接采自复杂加权网的结构刻画 (Barrat et al., 2004): 该文提出以节点强度为归一分母、以边权乘邻居度求和的加权 ANND, 用于揭示强度与度关联的层级结构, 本项目的实现 (networkx 的加权 average_neighbor_degree) 即此定义的落地, 面板导出标签亦明确标注 Barrat 2004 为构念来源。把这一社会网络与统计物理的度关联工具移植到银行媒体共现图上, 目的是给面板提供一个不看自身曝光量、只看所处邻域结构层级的节点级结构变量。在银行媒体研究的语境下这一层级信息有实质意义: 与高连接枢纽银行反复同篇出现的银行往往处于系统性话题的中心, 其经营与风险叙事更易与同业联动; 而邻居度低的银行多停在孤立的地方性报道里, ANND 因此给出一个衡量银行在媒体注意力结构中所处层级的连续代理, 而非仅仅重复曝光量已经承载的信息。

【方法学与计算】
计算链路分三步。第一步构造年度邻接矩阵: 取该年篇章级 (article×bank) 展开帧, 节点全集为该年出现过的全部目标银行, 逐篇把同一篇内共同出现的银行两两配对, 每篇每对无序对给对应邻接元素加一, 对称累加, 得到以共同出现篇数为权的对称邻接矩阵。第二步据邻接矩阵建原始加权图 G (边权 = 共现篇数, 孤立银行以孤立节点入图), 并另建倒数权图供路径型指标使用 (本家族不用倒数图)。第三步在 G 上调用加权平均最近邻度: 对节点 i, k_nn,i 等于其各邻居无权度按边权加权的平均, 即先对每个邻居 j 取边权 w_ij 乘 j 的无权度 k_j, 求和后除以 i 的加权度 (强度) s_i。因每个邻居 j 至少与 i 相连, k_j 恒大于等于一, 故有边节点的 ANND 有下界一; 度为零的孤立银行没有邻居, 平均无从定义, 显式置 NaN (这与该指标同批的 effective_size 等原始图指标一致的空值口径)。三步计算全为闭式算术聚合, 不含特征值迭代或最短路数值求解, 因而 bank_avg_nbr_deg 不在本项目枚举的 BLAS 浮点求和序非确定网络列之列 (那一组仅含 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 各自的三判据变体), 在钉死随机种子与线程数的确定性协议下可逐位复现。共现网存在一处结构性口径披露: 一篇同时点名 N 家银行的稿件 (榜单稿、批量监管通报) 会贡献 N 取二条等权边, 大 N 稿可凭边数膨胀主导网络结构; 生产默认按每对加一 (golden-safe), 预留的 Newman 度守恒归一 (hyperedge_normalize) 仅在同篇 article 主路径可选且当前未接线, 判据分轨路径遇该参数为真会显式抛错以防三轨口径无声分叉。行宇宙遵循 2026-06-29 的 full-only 留篇门控: 进入共现网的文章是 full 轨判定为银行金科报道的留篇集, 与面板 n_articles 分母的 full 口径对齐, 使网络节点与边的样本框同面板的报道计数同源。实现细节上, networkx 的 average_neighbor_degree 在无向图上把 source 与 target 邻域坍缩为同一邻居集, 权重参数指定即取加权分子与强度分母、未指定则退化为无权 ANND, 本项目显式传 weight 为边权取加权版。网络逐年独立重建、逐年独立计算, 本家族是当年快照的截面结构变量, 不含跨年滞后 — 这与共现溢出族里显式带 lag1 的列不同, 后者刻意引入时间前定性以缓解同期反射, 本家族则不做滞后, 属同期结构描述。数值量级的读法: ANND 等于一表示邻居全是仅与本行相连的叶节点 (邻居度均为一), 数值随邻居连接广度单调上升, 上界受当年网络规模约束; 因分母为强度而非邻居数, 高权边 (与某同行反复同篇出现) 的邻居对 ANND 的贡献被放大, 使本列对重复共现的强关联比单次共现的弱关联更敏感, 这正是采加权而非无权口径的信息动机。

【文献定位】
在网络测量谱系里, 本家族处于度层结构变量与全局关联系数之间的节点级度关联层。加权定义的方法学锚是 Barrat et al. (2004): 该文以航空网与科学合作网证明, 只看无权度会丢失强度信息, 加权 ANND 能揭示高强度节点是否优先连向高度节点这一层级结构, 本项目沿用其强度归一口径。分母所用的节点强度概念承自加权网中心度的推广 (Opsahl, 2010): 把度推广到强度 (边权之和) 是加权网络的基本操作, ANND 的加权版正是以强度替代计数作分母。度作为网络位置最基础操作化的合法性来自中心度的概念厘清 (Freeman, 1978), 而以最小度刻画网络内聚子结构的传统 (Seidman, 1983) 与小世界网中局部邻域连通性的洞见 (Watts & Strogatz, 1998) 共同说明: 邻居的连接结构本身携带超出自身度的信息, 这正是把节点级 ANND 单列为一个测度的理由。在金融应用侧, 近年一批研究支持网络中心度对资产定价与预测的信息增量: 中心度与信息扩散、资产定价的联系 (Yu et al., 2024), 金融网络中节点中心度对资产价格预测的作用 (Xu & Zhao, 2024), 金融网络传染中心度的统计效度检验 (Sadeghi & Feinstein, 2024), 以及中心度与企业绩效关系的元分析证据 (Nezami et al., 2025) 共同确立结构位置是可解释经济结局的变量族。与本项目共现图构造最贴近的是文本驱动网络这一支: 从文本相似度构造企业网络的范式 (Hoberg & Phillips, 2016) 与从文本风险披露反演金融网络结构与连通性的近作 (Li et al., 2026) 都证明, 由文本共现或相似度构造的网络虽非真实合约暴露, 却能作为潜在关联结构的可复现代理, 为把新闻共现网上的结构指标当作银行间媒体关联的代理提供外部效度。具体到每条锚点的相关性可再收束: Barrat et al. (2004) 提供加权 ANND 的定义与强度归一口径, 是本列算法的直接来源; Opsahl (2010) 界定分母所用的强度概念并把度推广到加权网; Freeman (1978) 奠定度作为网络位置操作化的合法性; Seidman (1983) 与 Watts & Strogatz (1998) 分别从最小度内聚与局部邻域连通性说明邻居结构携带超出自身度的信息; 金融侧四文 (Yu et al., 2024; Xu & Zhao, 2024; Sadeghi & Feinstein, 2024; Nezami et al., 2025) 从资产定价、价格预测、传染中心度效度与绩效元分析四个方向支持结构位置的经济含量; 文本网络两文 (Hoberg & Phillips, 2016; Li et al., 2026) 为由文本共现或相似度构造网络并在其上读结构指标提供方法学与效度先例。此外, Li, Xu, Qi & Chen (2026, Management Science) 用大数据方法系统刻画网络的度分布、聚类系数与度关联 (assortativity) 等结构统计量, 为本家族以邻居度加权均值刻画节点邻域层级位置的构念提供了同期方法论参照。同期, Lin, Lu, Michaely & Qin (2026, Management Science) 以赞助人网络中心度研究 SPAC IPO 的资源整合与治理机制, 为把网络位置结构指标用于金融实体关系分析提供近期方法学参照。

【识别策略定位】
本家族在识别策略上的定位须分三层澄清。第一层是判据梯子的性质: 同一 ANND 构念按银行与银行的共现判据分三轨物化 — 同篇 (无后缀, 现行 canonical)、正负一句窗 (_win1)、严格同句 (_sent), 三者互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。这一梯子是规格稳健性并排, 镜像政治词权重梯度与词典消融梯度的先例, 刻意不设 FWER 模板: 跨模型 rwolf 先例仅覆盖同构念替代 headline 测量, 而判据梯子是同一测度在不同边定义下的重算, 不适用族级家族错误率校正。第二层是判据后缀与三轨文本后缀的正交性铁律: 判据后缀 (_win1 / _sent) 度量的是银行与银行的边如何界定, 三轨文本后缀 (_full / _ctx / _ss) 度量的是银行与金科文本如何物化, 两者是两个正交的概念空间, 全仓无既有列以 _win1 或 _sent 结尾, 严禁把判据轨与文本轨混进同一 Hansen J, 也严禁把 _sent 的同句判据与 _ss 文本轨的银行金科同句共现混为一谈 (前者银行与银行, 后者银行与金科, 判据原语不同, 禁互相复用)。第三层是 ANND 作为邻域暴露统计量在计量识别上的双刃性质: 平均最近邻度本质是邻居特征 (邻居度) 的加权均值, 与社会网络同群效应识别中的邻居协变量暴露同形 (Bramoullé et al., 2009), 因此它天然携带反射问题的内生性风险 — 一家银行的邻居度与其自身在网络中的位置由同一共现过程生成, 把 ANND 直接作回归右手侧解释共同结局时, 估计的可能是共同的媒体覆盖结构而非因果的邻域溢出。企业金融政策中的网络效应研究 (Grieser et al., 2022) 提示, 网络生成的解释变量须以外生的网络工具或结构假设识别, 本家族在面板中的定位因而以结构描述与稳健性佐证为主, 升为因果 RHS 须另配识别策略并披露反射问题。实践上, 判据梯子的正确用法是把三判据轨各自放进独立的 just-identified 规格、并排报告结果一致性, 而非把三列作为三个工具塞进同一过度识别系统做 Hansen J 检验 — 后者会因三列源自同一共现过程、测量误差结构同源, 使检验的拒绝无法区分工具无效与列间机械相关, 这正是本项目对全部规格稳健性梯子 (判据 / 三轨文本 / co-primary 嵌入 / 政治词权重 / 词典消融) 统一施加禁混同一 over-identified Hansen J 铁律的计量根据。第四层须补足共现网的投影本源对识别的独立含义: 银行共现图并非直接观测到的银行间关系, 而是文章 × 银行二模隶属 (affiliation/incidence) 网络向银行单模的投影 (Faust, 1997; Borgatti & Everett, 1997)。二模投影不是信息守恒的变换 — 两家银行因同列一篇榜单稿而相连, 与两家银行因一篇专题深度报道被并置讨论, 在投影后得到形态相同的边, 边权因而内生地编码了稿件的团规模 (hyperedge size) 结构而非纯粹的关系亲近度。这意味着 ANND 携带的测量误差是非经典的: 其量级与每家银行暴露于大 N 榜单稿的程度共变, 一个邻居的高度可能反映它与本行同受一批宽榜单稿覆盖, 而非真实的关系邻近。这一投影伪迹叠加在反射问题之上 — 邻居度与本行位置既同源于共现过程, 又同源于同一批宽稿的团投影, 使把 ANND 直接作因果右手侧时的混淆源比标准反射问题更复杂。二模投影的元验证工作 (Cimini et al., 2022) 表明, 须以零模型 (null model) 过滤才能把信号边与投影伪迹边分离, 而生产的每对加一团投影不作任何此类过滤, 故因果解读须把投影伪迹当作反射问题之外的额外混淆一并披露。回到同群效应识别的经典结果 (Bramoullé et al., 2009): 其识别依赖网络中的非传递三元组 (朋友的朋友并非自己的朋友), 而 ANND 作为邻居之邻居的度矩恰是该策略所倚重的二阶网络矩; 但同一文献亦告诫, 当网络由不可观测的共同因子生成 (此处即共同的编辑议程与同批宽稿覆盖) 时, 排除约束失效 — 这与投影本源的分析同向, 共同把本家族在因果层的定位收束为结构描述与稳健性佐证, 而非现成的因果解释变量。

【与相邻测度的构念区分】
本家族须与同批网络指标逐一区分。与 bank_degree_cent 的区分最关键: 度中心度是节点自身的 (归一) 邻居数, 度量这家银行被多少家同行共同提及; ANND 是这些邻居各自的度的均值, 度量邻居们连得多广, 一家只被两家同行提及但这两家都是网络枢纽的银行, 度中心度低而 ANND 可以很高, 二者分居自身位置与邻域位置两个层级。与 bank_strength_cent 的区分: 强度中心度是自身加权度 (再按年内最大值归一, 属年相对度量), 是 ANND 分母中出现的量, 但 ANND 把它当归一常数、真正测量的是分子里的邻居度, 二者不可互替。与 bank_clustering 的区分: 聚类系数看的是一家银行的邻居之间是否互相成边 (三元闭合), ANND 看的是邻居对更广网络的连接, 一个测邻域内部致密度、一个测邻域外部延展度, 且聚类系数属 BLAS 浮点非确定列而 ANND 确定, 两者构念与数值稳定性均异。与 net_assortativity_yr 的区分尤须点明: 后者是整张年度网络的度关联皮尔逊系数, 是网络级全局标量, 而 bank_avg_nbr_deg 是其节点级构成单元 — 全局关联系数正是 k_nn(k) 随度变化趋势的浓缩, 节点级 ANND 保留了每家银行的邻域层级信息而不被全局平均抹平。与 bank_coreness (k 核数, Seidman 1983 谱系) 的区分: 核数是节点所属最深 k 核的整数拓扑标签, ANND 是加权连续度关联, 核数问它嵌得多深、ANND 问它邻居连得多广。与 Burt 结构洞族 (bank_constraint / bank_effective_size / bank_ego_density) 的区分: 结构洞族度量邻域的冗余与桥接机会, 与邻居的全局度无关, 一家 ANND 高的银行其邻居可能高度冗余互连而结构洞少, 两族正交。与谱型中心度族 (bank_eigen_cent / bank_katz_cent / bank_subgraph_cent) 的区分: 谱型中心度以递归方式把邻居的中心度 (而非邻居的度) 反馈进自身得分, 是无穷阶邻域的加权汇总, 而 ANND 只看一阶邻居的度、不递归, 是局部一跳的度关联; 且谱型指标含特征值迭代、属 BLAS 敏感谱系, ANND 为闭式确定量, 数值稳定性亦异。与 bank_between_cent / bank_closeness_cent 等路径型指标的区分: 路径型走倒数权重图、度量的是全局可达性与中介位置, ANND 走原始权重图、只问一阶邻域的度层级, 图基底 (倒数图对原始图) 与语义均不同。此外须与二模隶属网络的中心度概念划清界限: 因单模共现图本身是文章 × 银行隶属网络的投影, 其无权度已把同篇共同隶属重复计数 (一篇点名 N 家的稿件把每家的度一次性抬高 N 减一), ANND 是建在这张已投影图上的二阶统计量, 与直接在文章 × 银行二模关联矩阵上计算的双模中心度 (Faust, 1997; Borgatti & Everett, 1997) 不是同一构念, 后者本项目并不计算 — 读 ANND 时须记得它继承的是投影后的度结构而非原始隶属结构。与 bank_cfbetween_cent 的进一步区分亦可借此点明其算法本源: cfbetween 是基于随机游走的电流介数 (current-flow betweenness, Newman, 2005), 度量信息在整张网络里以随机游走方式流经该节点的期望频次, 属全局路径型量; ANND 只看一阶邻居的度、不含任何游走或路径积分, 是局部一跳的度关联, 两者在图论阶数 (全局无穷阶随机游走对一阶邻域) 与数值稳定性 (cfbetween 属 BLAS 敏感列、ANND 闭式确定) 上双重相异。

【已知局限与稳健性梯子】
第一, 空值语义: 孤立银行 (当年无任何共现) ANND 置 NaN, 报道稀少的小银行与早年份系统性缺失, 缺失机制与共现活跃度相关而非随机, 解释时须视为条件于有邻域的银行的度量。第二, 大 N 稿膨胀: 榜单与批量通报稿以等权团投影贡献大量边, 未接线的度守恒归一使当前口径对大 N 稿敏感, 一年中若干超大团稿可抬高团内银行的邻居度, 从而系统性拉高其 ANND, 面板层暂无 hn 归一对照臂 (预留但未接线, 属受控重生事项)。第三, 加权与无权口径: 生产用加权 ANND (Barrat 2004 强度归一), 未同时物化无权 ANND 对照臂, 因此加权方案本身的贡献尚无梯内对照, 换算法即换测度。第四, 判据梯子的开发盘退化: 本机两年短窗试跑下, 严格同句 (_sent) 与句窗 (_win1) 判据的边集稀疏, 部分银行邻域为空使 ANND 大面积 NaN 或退化, 生产十九年窗方可谈稳定的判据间比较; 跨判据比较应侧重方向与显著性而非水平值。第五, 判据扫描依赖: _win1 与 _sent 走 docid 组内文本重扫, 依赖银行别名字典、否定自动机与短名排除 (与共现硬过滤同一事实源, 防涉农行业误命中农行之类假阳性), 别名字典或否定表更新即改边集, 属换测度。第六, 代理性质: 共现网是媒体关联的文本代理而非真实同业暴露, ANND 高只说明该行常与网络枢纽银行被同篇提及, 不等于存在合约或风险敞口关联, 因果解读须谨慎 (Li et al., 2026 的文本反演网络同属此代理层)。稳健性梯子结构: 三判据轨 (同篇 / _win1 / _sent) 构成本家族的规格稳健性梯子, 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 该梯子与三轨文本后缀、co-primary 双轨嵌入的稳健性梯子彼此正交、不交叉, 严禁跨概念空间拼进同一过度识别系统。第七, 年相对与跨年可比性: 网络逐年重建、节点集逐年变动, 邻居度的绝对量级随当年入网银行数与媒体报道密度浮动, 跨年比较 ANND 水平须辅以年固定效应或网络规模控制, 单看原始水平易把年度报道量波动误读为结构变化。第八, 判据轨的确定性一致: 三判据轨均为闭式算术, 全部不在 BLAS 非确定网络列之列, 受控环境下逐位可复现, 故判据梯子的稳健性对照不受浮点非确定性污染, 这一点与 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 等须在验零漂移时按全名剔除的列不同。第九, 关于大 N 团投影的原则性补救须再展开一层: 对无归一团投影导致的边膨胀, 文献给出的规范做法有二 — 一是保留的度守恒零模型归一 (hyperedge_normalize, Newman 式, 使一篇点名 N 家的稿件贡献的总度守恒), 二是统计骨架抽取 (network backbone extraction), 即仅保留能通过零模型显著性检验的边、剔除随机投影即可解释的边 (Kirkley, 2025; 投影零模型的效度检验见 Cimini et al., 2022)。两种补救本项目当前均未接线进面板: 度守恒归一是保留但未接线的参数 (判据分轨路径遇之显式抛错), 骨架抽取更无实现, 故本家族目前不提供骨架过滤对照臂, 属受控重生事项。这意味着现行 ANND 是在稠密的每对加一投影图上计算的、对大 N 稿最敏感的一版; 一个骨架过滤对照臂若接线, 会把 ANND 的邻域限定在统计显著的强关联上, 预期系统性压低受大 N 团稿抬升的银行的邻居度, 是本家族最值得优先补齐的稳健性轨。

## VAR: bank_avg_nbr_deg

【变体差分】
无后缀 canonical 列, 采同篇 (article) 共现判据。两家银行只要在同一篇报道 (同一 docid) 内被共同提及即成边, 边权为共同出现的篇数, 这是本项目共现网现行的生产口径, 也是判据梯子的基准轨。取边路径走 both-verified 主路径: 在同一 docid 分组内, 对该组幸存的目标银行集合逐无序对加一, 每篇每对恰计一次; 非幸存银行不入参、不可能成边 (幽灵边防线)。相对两个更严的判据轨, 本列的边定义最宽 — 只要同篇即算共现, 不要求两家银行出现在邻近句子或同一句子, 因此其邻接矩阵最稠密、邻域最大, 对应节点的加权度与邻居度均倾向最高, ANND 的有效样本 (有邻域的银行数) 最多, NaN 最少, 在开发短窗下也最不易退化。这一宽判据的代价是最易受大 N 团稿主导: 一篇点名众多银行的榜单稿在同篇口径下把全部被点名银行两两连成等权团, 显著抬高团内银行的邻居度, 是本列相对 _win1 / _sent 更须警惕大 N 膨胀的原因; 预留的 Newman 度守恒归一仅在本 article 主路径可选 (判据分轨路径遇之抛错), 但当前未接线, 故本列亦按每对加一。须强调无后缀不等于唯一主测度, 而是判据梯子中现行 canonical 口径的承载列: 它与 _win1、_sent 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。判据后缀空缺仅表示同篇口径, 与三轨文本后缀 (_full / _ctx / _ss) 分属正交概念空间, 严禁把本列与任一文本轨列混进同一 Hansen J。空值、加权定义 (强度归一的 Barrat 2004 加权 ANND)、确定性 (闭式算术, 不在 BLAS 非确定网络列之列)、full-only 留篇行宇宙等口径与 CORE 所述一致: 孤立银行置 NaN, 有边节点下界为一, 度量的是与本行同篇被提及的银行群在整张年度共现网中的连接广度。取边路径的降级口径须一并说明: both-verified 主路径依赖 docid 分组, 当篇章级帧缺 docid 列时退回按 co_mentioned_banks 的旧口径连边 (每篇把该篇共同提及银行列表两两连边), 语义近似但不经 docid 去重, 属兼容降级而非首选。节点全集口径: 无论走主路径还是判据分轨, 节点集恒为该年出现过的全部目标银行, 与 _win1 / _sent 完全一致, 三判据只改边不改点, 这保证三轨 ANND 定义在同一节点宇宙上、差异纯粹来自边界定, 使判据梯子的稳健性对照干净可解释。为何以同篇为 canonical: 同篇共现是最贴近媒体议程共同性的关联定义 — 被写进同一篇报道即意味着编辑视角下的话题共现, 不苛求物理相邻, 契合以新闻共现代理银行间媒体关联的构念初衷; 更严的句窗与同句判据则作为收紧关联门槛的稳健性轨存在。使用规范: 新增下游模板若要引用同篇口径应显式书写无后缀名, 并把三判据列视为同一构念的三个稳健性并排臂而非三个独立测度, 严禁把无后缀列与 _win1 / _sent 同时作为不同工具塞进同一过度识别回归, 与三轨文本后缀列的混用同样被正交性铁律禁止。综上, 本列是判据梯子的基准轨与现行生产口径, 另两轨 (_win1 与 _sent) 均以它为宽判据参照系, 读的是把银行间关联门槛逐级收紧后邻域度层级是否稳健。

## VAR: bank_avg_nbr_deg_sent

【变体差分】
严格同句 (sent) 共现判据轨, 判据梯子中边定义最严的一轨。两家银行只有在同一句话内被同时提及 (句窗半径取零) 才成边, 走 docid 组内文本重扫: 对多银行同篇稿以 map_bank_sentence_positions 定位各银行的逐句出现位置, 再以零半径的句窗配对原语取同句共现对, 标题按 prepend_title 计为第零句 (镜像共现硬过滤的标题匹配口径)。相对无后缀的同篇口径与 _win1 的句窗口径, 严格同句大幅收窄边集: 只有真正被写在同一句里的银行对才算关联, 剔除了同篇但分散在不同段落、仅因同属一篇榜单而被连边的弱关联。因此本轨邻接最稀疏, 有邻域的银行最少, ANND 的 NaN 比例结构性最高, 在开发两年短窗下邻域大面积为空、退化最重, 生产十九年窗方有足够同句共现支撑稳定估计。判据原语 (银行与银行同句) 与三轨文本后缀里 _ss 的银行金科同句共现是两个不同口径, 严禁互相复用, 也严禁把本列与 _ss 文本轨混进同一 Hansen J。本列与无后缀 canonical、_win1 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J: 它提供的是最保守的邻域界定下 ANND 是否稳健的证据 — 若结论在只认同句关联的最严判据下仍成立, 则邻域层级信号不依赖宽松的同篇连边约定。加权定义、强度归一、孤立节点置 NaN、确定性等口径与 CORE 一致, 差异仅在边如何界定。

## VAR: bank_avg_nbr_deg_win1

【变体差分】
正负一句窗 (win1) 共现判据轨, 严格程度介于同篇与严格同句之间。两家银行在正负 win_radius 句窗内被提及即成边, 句窗半径取自 config/panel.yaml 的 network_criteria.win_radius (默认一), 走与 _sent 相同的 docid 组内文本重扫路径, 差别仅在配对原语的窗半径取一而非零, 标题同样按 prepend_title 计为第零句。相对无后缀的同篇口径, _win1 要求两家银行出现在邻近句子而非仅同篇, 因而剔除了同篇但相隔很远的弱关联, 边集比同篇稀疏; 相对 _sent 的严格同句, 它放宽到正负一句邻域, 边集比同句稠密, 捕捉的是跨相邻句子表述的银行对关联。这一居中判据在稠密度与保守度之间取平衡, 有邻域银行数与 NaN 比例介于另两轨之间, 开发短窗下的退化程度亦居中。须点明一处易混的配置键: 本轨的 network_criteria.win_radius 与共现硬过滤 (stage 13, 银行与金科) 的 cooccurrence_filter.sentence_radius 是两个不同键、互不联动, 前者定义银行与银行的边窗, 后者定义银行与金科的留篇窗, 判据后缀与三轨文本后缀分属正交概念空间。本列与无后缀 canonical、_sent 互为稳健性、不分主次, 三判据各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 它是同篇与同句之间的中间稳健性轨, 用于检验 ANND 结论对边界定宽严的敏感性。加权定义、强度归一、孤立节点置 NaN、确定性等口径与 CORE 一致, 差异仅在边窗半径。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Kirkley, A. (2025). Fast nonparametric inference of network backbones for weighted graph sparsification. Physical Review X, 15(3), 031013. https://doi.org/10.1103/4pg6-mtmt
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Li, H., Xu, T., Qi, J., & Chen, Y.-J. (2026). Analyzing Network Formation Using Big Data Analytics: A Study of Degree Distribution, Clustering Coefficient, Diameter, and Assortativity. Management Science. https://doi.org/10.1287/mnsc.2023.00475
Lin, C., Lu, F., Michaely, R., & Qin, S. (2026). SPAC IPOs and Sponsor Network Centrality. Management Science, 72(4), 3309-3331. https://doi.org/10.1287/mnsc.2024.04492
<!-- rendered-citations:end -->
