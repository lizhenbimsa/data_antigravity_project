---
family_id: F088
columns:
- bank_degree_cent
- bank_degree_cent_sent
- bank_degree_cent_win1
unit: 度中心度 (无量纲, 归一化到 [0, 1])
formula: "bank_degree_cent = degree(i) / (n - 1); degree(i) = 银行 i 在年度共现图中相邻的不同银行数 (纯拓扑, 不计边权); 判据变体 {同篇 (无后缀) / ±1 句窗 _win1 / 严格同句 _sent}"
producer: pipeline\panel\network_spillover.py::compute_bank_network_centrality (build_adjacency_matrix + networkx.degree_centrality); 落列 pipeline\panel\runner.py 步骤 7h-cent; codebook 元数据 pipeline\panel\codebook.py
upstream:
- 11_news_bank.parquet (docid, target_bank, 内容, 标题, year — 篇章级共现来源)
- 21_tone_llms.parquet (both-verified 幸存银行 = full-only 留篇门控节点全集)
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
- doi: 10.1016/j.najef.2024.102163
  type: journal
  authors: Xu, Y., & Zhao, X.
  year: 2024
  title: "How does node centrality in a financial network affect asset price prediction?"
  venue: The North American Journal of Economics and Finance
  vol: 73
  pages_or_artno: 102163
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: Review of Financial Studies
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
  pages_or_artno: 76
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
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
- doi: 10.1103/PhysRevE.71.056103
  type: journal
  authors: Estrada, E., & Rodríguez-Velázquez, J. A.
  year: 2005
  title: "Subgraph centrality in complex networks"
  venue: Physical Review E
  vol: 71
  issue: 5
  pages_or_artno: 056103
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
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: 1170-1182
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
bank_degree_cent 是 F088 家族的 canonical 列, 度量一家银行在年度"媒体共现网络"中的度中心度 (degree centrality)。构念根植于社会网络分析对"中心性"的经典界定: 一个节点越是与网络中众多其他节点直接相连, 它在信息、资源与影响力流动中所占据的位置就越居中、越关键 (Freeman, 1978)。本项目把这一构念移植到中国银行业的新闻文本语境: 网络的节点是银行, 网络的边是"两家银行在同一年的媒体报道里被共同提及"这一可观测事件。当一家银行在一年之内频繁地与许多不同的同业一起出现在金融科技相关的新闻叙事中, 它在公众注意力与市场话语的结构里就占据了一个更中心的位置——这既可能反映它作为行业标杆被媒体反复援引的显著地位, 也可能反映它深嵌于一个更密集的同业竞争与合作话语场之中。度中心度回答的问题非常朴素: 这家银行今年在新闻里"认识"多少家不同的同业。它是整个网络指标家族里最直观、最不依赖任何谱分解或路径计算的一个, 因而被选作家族的 headline 列与 SSOT 锚点。需要强调, 这里的"共现网络"在图论上是一种由二模关系 (银行—文章的隶属关系) 投影而来的一模网络 (Faust, 1997): 底层可观测的是"哪家银行出现在哪篇文章里"这层隶属结构, 度中心度所度量的连接广度, 是该隶属结构经投影后在银行—银行一模图上的显现, 因此对投影方式与文章规模分布敏感, 这一性质会在下文的构念区分与局限讨论中反复回到。

数据来源与生成链路: 该列不是某个独立 stage 的直接产物, 而是在面板构建 (panel building, 历史模块名 46_network_spillovers, 现行落位 Stage 40 的 pipeline/panel/network_spillover.py) 内部, 由 compute_bank_network_centrality 消费上游篇章级展开帧 df_exploded (article × bank 的长表) 计算而得, 落列发生在 runner 的 7h-cent 步骤。上游 df_exploded 来自 11_news_bank 阶段: 每篇文章解析出它所提及的目标银行 (target_bank) 与共同提及的银行集合, 并携带全局文档标识 docid、发布年份 year、标题与正文文本。关键的边权口径校正 (omni-g-net-spill-01, 2026-06-11) 在于: 邻接矩阵不再直接消费 stage-11 遗留的 co_mentioned_banks token 串——该串在 stage 21 verification 过滤之后仍会列出已被判定为"非真提及"而剔除的银行, 若逐行双向计数会把这些已拒绝的银行也拉进网络, 制造出 phantom 边 (幽灵边), 并因同一文章的两条 twin 行是否各自幸存而在 1x/2x 之间任意混合边权; 而现行主路径按 docid 聚合"该篇文章中所有通过 verification 的 target_bank 幸存集合", 对集合内每一个无序银行对恰好在对称邻接矩阵上各加一次权重 (每篇每对 +1, 对称写入 [i,j] 与 [j,i])。由此, 只有真正通过判定的银行才成为网络节点、只有真正共同幸存于同一文档的银行对才成为边。co_mentioned_banks 逐行计数仅在缺 docid 的旧 schema 或合成帧下作为降级兜底路径保留, 并伴随 loud WARNING 显式标注该年退化为遗留口径。

进入网络的节点全集, 是经过留篇门控筛选后的 both-verified 幸存银行——这与 2026-06-29 起生效的 full-only 留篇口径严格一致: 一篇报道是否算作"银行金科报道"只看 llm_verified_full 是否为真, ctx 轨与 ss 轨已降为 conditional-on-full 的测度/稳健性轨。因此媒体共现网络的节点宇宙与面板 n_articles 的 full-only 分母共享同一事实源, 不会因 ctx/ss 轨口径差异而漂移。这一点对网络指标的可解释性至关重要: 网络的边和度都建立在"留篇集"这一确定的样本框之上, 使得 bank_degree_cent 与同面板其他 full-only 口径的注意力、情感变量在样本层面可比。若把不同留篇口径的节点集混入同一张年度图, 会破坏度中心度的可比基线; full-only 的单一事实源正是为消除这一自由度而设。

【方法学与计算】
计算严格遵循 Freeman (1978) 的度中心度定义并采用其规范化形式: 对含 n 个节点的图, 节点 i 的度中心度等于它的度数 (直接相邻的不同节点数) 除以理论最大可能度数 n 减 1, 即 degree(i)/(n-1), 取值域理论上落在 0 到 1 的闭区间内, 无量纲。实现层面, 引擎先调用 build_adjacency_matrix 构建年度对称加权邻接矩阵 (稀疏 lil_matrix 承载, 再转 CSR): 该年出现的全部银行按名称排序确定节点索引, 每篇文章对其幸存银行集合内的每一对贡献一次计数; 随后用 networkx 建立无向图 G, 只要某两银行的邻接权重大于 0 即在其间建一条边 (边权保留为共现次数), 并把当年出现却未与任何同业共现的银行作为孤立节点补入图中, 以保证节点全集完整无遗漏。度中心度调用 networkx 的 degree_centrality(G): 该函数在计数节点度数时只看"两点间是否存在边"这一纯拓扑事实, 完全不看边权大小, 因此 bank_degree_cent 是一个纯拓扑量——它回答"这家银行今年与多少家不同的同业一起上过新闻", 而绝不问"一起上了多少次"。共现强度 (加权度) 这一维度由家族外的姊妹列 bank_strength_cent 单独承载 (加权度构念, Opsahl et al., 2010, 并在本项目内做年内 max 归一), 两者刻意分工、构念不混, 以免把"广度"与"频度"两种不同的中心含义压进同一个数字。孤立节点通过 degree_centrality 天然取 0, 与全部其他银行都相连的极端中心节点取 1, 中间取连续值。

三个判据变体共享同一套计算原语但走不同的边生成路径。同篇 (article) 口径是主路径, 直接按 docid 聚合幸存银行集合成团, 无须触碰句级文本, 因而计算最省。±1 句窗 (win1) 与严格同句 (sent) 两个更严口径走"docid 组内文本重扫"的分轨路径: 引擎先加载与 stage 11/13/ctx/ss 共用的同一事实源 (银行别名字典、否定词 AC、短名排除表、句窗半径 win_radius), 再逐 docid 组把该组幸存银行的别名字典喂给 core/text/entity_context 的 map_bank_sentence_positions, 定位每家银行在"标题 prepend 后正文"里出现的句号位置 (标题自成第 0 句, 镜像 stage 13 的 match_in_title 口径); 随后 bank_pairs_within_sentence_window 在给定句窗半径内 (win1 取 win_radius=1, sent 取 radius=0) 枚举满足邻近条件的银行对成边。三条路径的节点全集完全一致 (都是当年幸存 target_bank), 仅边集因判据松紧不同而逐级变稀。审计脚本与生产调用共用这同一套原语 (审计==生产), 保证判据敏感性检验与主口径可比。分轨路径刻意拒绝裸 AC 匹配并启用短名排除, 以防"涉农行业"误命中"农行"这类假阳性——这条防线在所有涉银行实体识别的阶段是统一的; 若某 docid 组内正文文本不一致 (F0.18 实测应为 0), 引擎取组首行并 loud WARN, 而非让单条脏数据崩掉整个 stage。

从二模到一模的投影视角看, 同篇口径本质是把每篇文章视作一个"隶属团"(clique)、对其内部所有银行对等权连边——这正是二模隶属网络投影为一模网络的标准操作 (Borgatti & Everett, 1997; Faust, 1997)。这一视角解释了为什么引擎保留了 hyperedge_normalize 这一预留开关: 一篇同时提及 N 家银行的文章会以等权投影贡献 C(N,2) 条边, 大-N 文章可凭边数膨胀主导网络; hyperedge_normalize=True 时改按 Newman (2001 PRE) 的 degree-preserving 归一, 每对贡献 1/(N-1) 使单篇总度贡献守恒。但该参数目前仍是尚未接线到 config/runner 的预留开关 (两个生产调用方及外层签名均不透传, True 分支在生产流水线不可达), 生产口径仍为等权 +1 (golden-safe); 且分轨路径 (win1/sent) 对该参数直接 raise 以防三判据轨无警告分叉口径。引擎在每年检测到大-N 文章 (>10 家银行) 时会 info 日志披露其数量与最大规模, 以便事后审计投影污染的严重程度。

确定性说明: 因为度中心度是纯拓扑计数, 不涉及特征分解、幂迭代或最短路径的浮点运算, 它不受 BLAS 浮点漂移影响, 跨次重建可逐位复现。这与同一计算函数产出的 bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 形成鲜明对照——后三者 (连同它们各自的 _win1/_sent 判据分轨变体, 共九列) 属于已登记在案的 BLAS 浮点非确定列, golden 校验验零漂移时须按全名剔除; 而 bank_degree_cent 及其两个判据变体不在该豁免清单内, 属于严格确定的锚列, 因此它天然适合承担家族 canonical 与确定性锚的双重角色。这一确定性也是把它选作若干下游派生指标 (bank_is_hub 枢纽哑变量、net_degree_gini_yr 度基尼) 原料的实务前提: 派生列的可复现性以本列的逐位确定性为地基。

【文献定位】
度中心度是社会网络分析中历史最悠久、被引最广的中心性度量。Freeman (1978) 在其对中心性构念的系统澄清中区分了度 (degree)、中介 (betweenness) 与接近 (closeness) 三大类, 并明确指出度中心度捕捉的是"活动性/可及性"这一维度: 高度节点直接触达的邻居最多。Bonacich (1987) 进一步把度中心度置于一个更大的"中心性度量家族"中, 说明当把邻居的重要性也纳入加权时, 度中心度是特征向量中心度等一族测度在权重参数取零阶时的退化特例——这为本项目在同一网络上并置度、特征向量 (bank_eigen_cent)、Katz、子图 (Estrada & Rodríguez-Velázquez, 2005)、当前流中介 (Newman, 2005) 等多种中心度提供了统一的谱系依据。Opsahl et al. (2010) 则给出了度中心度向加权网络推广的规范框架, 说明为何本项目要把"广度"(度) 与"频度"(强度) 拆成两列分别度量。Boldi 与 Vigna (2014) 从公理化角度比较了各类中心性对节点增删、边加密等操作的响应性质, 为审慎解释"度中心度上升意味着什么"提供了理论边界。由于本项目的共现图是二模隶属网络的一模投影, Faust (1997) 关于隶属网络中心性的专门讨论尤为切题: 她指出隶属网络投影后的中心度会系统性地被"事件规模" (此处即文章提及的银行数) 塑形, 这为本项目审慎解读度中心度水平、以及保留 hyperedge_normalize 归一选项提供了直接的方法学依据。

在金融与银行网络的应用脉络里, 中心性与结果变量的关系有大量近期证据。Nezami et al. (2025) 的元分析系统汇总了网络中心度与企业绩效之间的关联, 表明中心性对绩效的效应在方向与强度上依中心性类型、网络类型与情境而异——这提示 bank_degree_cent 作为单一测度不宜被过度解读为"越中心越好", 而应放在多测度、多判据的稳健性矩阵中审视。Yu et al. (2024) 与 Xu 和 Zhao (2024) 分别在信息扩散/资产定价与资产价格预测的框架下论证了节点在金融网络中的中心位置具有信息含量; Sadeghi 与 Feinstein (2024) 则从统计验证角度讨论金融网络中传染性中心度的可靠性。这些工作共同支撑了本项目的核心设想: 银行在媒体共现网络中的度中心度, 是其在信息生态中结构位置的一个可观测代理。

在更贴近本项目对象的金融中介与网络效应文献中, Grieser et al. (2022) 记录了公司财务政策沿网络传导的显著网络效应, 说明一个机构在同业网络中的结构位置会实质影响其决策与结果; Han et al. (2024) 对机构经纪网络如何促成流动性提供的研究, 则从中介/经纪的角度补充了"位置即资源"的机制叙事——这两条脉络共同提示: 度中心度所刻画的连接广度只是网络位置的一个侧面, 桥梁地位、经纪角色与结构洞是与之互补而非替代的维度 (故本项目在同一网络上并置了 gf_ 系列 Gould-Fernandez 经纪角色与 constraint/effective_size 等结构洞测度)。文本网络方面, Hoberg 和 Phillips (2016) 用文本相似度构建企业间"产品市场邻近"网络的思路, 直接启发了本项目 W-轨嵌入相似度网络的构造, 但也正因如此需要与共现网络严格区分: 前者的边是语义相似, 后者的边是被媒体共同提及, 两族基底图不同、不可混用。

【识别策略定位】
把网络中心度用于因果识别, 无法回避 Manski (1993) 提出并被 Bramoullé et al. (2009) 形式化的反射问题 (reflection problem): 一个节点的行为既受其邻居影响, 又同时影响其邻居, 内生同伴效应、外生情境效应与相关效应三者难以分离。Manski (1993) 的原始论证针对线性均值模型, 说明在最基本的线性设定下, 由于节点期望结果既作为原因又作为结果出现, 反射会使内生与外生社会效应的系数不可分离识别。Bramoullé et al. (2009) 证明当网络存在"朋友的朋友并非自己的朋友"这类结构 (即图的邻接矩阵、其平方与三次方线性无关) 时, 可利用间接连接构造工具、使参数获得识别; Boucher et al. (2024) 进一步给出同伴效应的更一般理论, 放松了线性—均值假设并容纳更丰富的社会互动形式。这一整套识别文献对本项目的直接含义是: 网络中心度本身既可能是同伴影响的载体, 又可能是被同伴塑形的结果, 因此把它当作外生处理变量单列进回归会先天带有反射污染。

本项目对此的立场是保守而透明的: bank_degree_cent 主要作为描述性结构控制变量与稳健性维度进入分析, 而非作为需要外生工具的内生处理变量单列 (与之相邻的 brokerage_network 论文体系里, 结构位置的因果解释另有专门的 IV 扩展与识别叙事, 参见 Grieser et al., 2022 对公司财务政策网络效应的识别处理)。在需要外生变异时, 项目侧的 IV 扩展 (同组 leave-one-out 均值、广义 Bartik、媒体来源 house-style 暴露) 提供了与网络位置正交的移位份额型工具, 而不直接用中心度本身充当工具——这与直接把中心度当工具相比, 更能回避"工具与被解释误差经由网络本身相关"的弱外生性风险。还须提示一层更基础的测量—识别耦合: 本项目的连边并非直接观测到的业务往来, 而是由媒体共现推断而来, 因此连边本身携带测量不确定性; 近期方法学工作 (de Paula et al., 2024) 专门讨论了如何从面板数据中识别网络连边这一对象、以及连边识别的误差如何向下游网络统计量传导, 这提醒我们在解读度中心度的水平与变化时, 须把"边是被推断出来的"这一测量事实纳入不确定性预算, 而非当作无误差的观测。综上, 本家族在识别上的定位是: 度中心度是刻画结构位置的描述性坐标与稳健性维度, 因果解释一律外包给配备了显式外生变异与识别叙事的论文侧模型, 而不在 codebook 层对单列中心度作因果承诺。

【与相邻测度的构念区分】
度中心度必须与家族内外若干相邻测度小心区分, 否则极易在解释与计量上混淆。其一, 与加权度 bank_strength_cent 的区分: 度只数"认识几家", 强度数"认识得多深"(共现次数之和), 两者在共现分布高度偏斜时可以大相径庭 (Opsahl et al., 2010); 一家只与两三家同业但反复被并列报道的银行可以度低而强度高, 反之一家在一份大榜单里与几十家银行各共现一次的银行可以度高而单次强度低。其二, 与特征向量类中心度 (bank_eigen_cent、bank_katz_cent、bank_subgraph_cent) 的区分: 度只看一阶邻居数量, 特征向量类看"邻居本身是否重要"这种递归的高阶信号 (Bonacich, 1987; Estrada & Rodríguez-Velázquez, 2005), 因此一家只与几个超级中心银行相连的机构可以度低而特征向量高。其三, 与路径/桥梁类中心度 (bank_between_cent、bank_cfbetween_cent、bank_harmonic_cent、bank_closeness_cent) 的区分: 后者度量"多少最短路径/信息流必须经过它"的中介与可达地位 (Freeman, 1978; Newman, 2005), 与度所刻画的"局部连接广度"是正交的结构维度, 一个度不高却卡在两个稠密社群之间的银行可以中介极高而度平平。其四, 与结构洞类测度 (bank_constraint、bank_effective_size、bank_ego_density) 的区分: 度高不等于经纪地位好, 一个度高但邻居彼此都认识的节点其实被约束在一个封闭团里 (Burt 的结构洞逻辑), 其经纪价值可能远低于一个度中等但连接了多个互不相识群体的节点。其五, 与 k-核/核度 (bank_coreness) 的区分: 度是纯粹的一阶邻居计数, 而核度刻画的是节点所嵌入的最稠密子结构层级 (Seidman, 1983 的最小度分解), 一个节点可以度很高却位于外围松散区、也可以度中等却深嵌于一个高度互连的核心团, 两者度量的是"连接多少"与"嵌入多深"两种不同的结构含义。其六, 与 W-轨嵌入相似度网络 (bank_emb_sim_mean、emb_peer_tone_diag) 的根本区分: 那一族的"边"是由 content 超级文档的语义余弦相似度定义的 (Hoberg & Phillips, 2016 的文本网络思路), 边的语义是"话语相似", 而 bank_degree_cent 的边是"被媒体共同提及"这一离散事件——两族网络的基底图完全不同, 禁止把它们的中心度并入同一 over-identified Hansen J 检验。还须与二模隶属结构本身区分: 度中心度是隶属网络投影后的一模量 (Faust, 1997; Borgatti & Everett, 1997), 它已丢失"通过哪些文章相连"的二模信息, 因此不能反过来当作隶属强度或文章共享数的直接代理。

【已知局限与稳健性梯子】
已知局限有四。第一, 大-N 文章的团投影污染: 一篇同时提及大量银行的榜单式或批量监管通报会以等权团投影贡献 C(N,2) 条等权边, 可能凭边数膨胀主导网络, 使得平均度与中心度水平被少数超大文章驱动; 引擎为此保留了 Newman (2001) degree-preserving 归一的 hyperedge_normalize 选项 (每对贡献 1/(N-1) 使单篇总度贡献守恒), 但该参数目前仍是尚未接线到 config/runner 的预留开关, 生产口径仍为等权 +1 (golden-safe), 未来若接线须产出第二套 *_hn 列并受控重生 golden。这一局限在方法学上早有系统刻画: 二模隶属网络投影到一模会人为制造团结构、抬高聚类与度, 且投影统计量的显著性须相对于恰当的零模型校准 (Cimini et al., 2022; Faust, 1997), 因此本项目在解读度中心度时刻意不把"高度"直接读作"关系密集", 而把大-N 文章数量与最大规模的年度诊断日志作为投影污染的监测信号。第二, 度中心度的年相对性质有限但仍需注意: 归一化除以 n-1 使其在同年内可比, 但跨年可比性依赖节点集规模的稳定性, 在样本框逐年扩张时应审慎解释水平变化; 派生的枢纽哑变量 bank_is_hub 尤其如此——它按年内度分布取第 top10_count 名的度为 cutoff (占比约 10%), 所有度不低于该 cutoff 的银行判为枢纽 (并列同判, 避免旧实现按字典序硬切前 N 家在边界任意判定), 但"~10%"是年内绝对阈值, 跨年 N 变化下仍会漂移, 故 bank_is_hub 宜作年内相对指示而非跨年水平变量; 且引擎设有退化守卫, 当某年全孤立 (cutoff≤0) 或度分布退化为单一值 (正则图) 时, 把全部银行判为枢纽会使该列沦为零方差常数并违背构念, 此时统一置 0 (该年无明确枢纽)。第三, 媒体共现的代理距离: 一起被报道不等于业务上真有往来, 度中心度度量的是"媒体话语里的结构位置"而非实际业务关联网络, 把它当作后者代理时必须明确这层测量距离, 且连边是被推断而非直接观测的 (de Paula et al., 2024), 携带识别误差。第四, T=2 开发切片上网络极易退化 (全孤立年 / 正则图), 此时度分布可能塌缩为常数导致零方差, 属预期退化, 生产 T=18 全量语料下不成立; 引擎对零方差中心度列有专门的诊断日志, 会显式标注哪些列因样本退化被回归的固定效应吸收, 便于把退化格与真实结构变异区分开来。

针对构造选择的稳健性梯子是本家族的核心设计: 同一 33 指标 (含 bank_degree_cent) 按"银行∧银行共现判据"分三轨并排计算——同篇 (无后缀 canonical) / ±1 句窗 (_win1) / 严格同句 (_sent), 判据越来越严, 边集越来越稀。三个判据变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把三者混进同一个 over-identified Hansen J 检验 (这一铁律与本项目三轨文本、co-primary 双轨嵌入、政治词权重梯子、词典消融梯度、per-model 稳健性等所有并排稳健性梯子完全同构)。必须强调: 这里的判据后缀 (无后缀 / _win1 / _sent) 与三轨文本后缀 (_full / _ctx / _ss) 是两个正交的概念空间——判据后缀刻画的是"两家银行算不算共现"的邻近度门槛 (判据主体是银行∧银行), 而三轨文本后缀刻画的是"用哪段文本判定银行金科关联"(判据主体是银行∧金科), 二者不可互相替代, 也禁止混入同一 Hansen J。判据分轨的口径细节 (match_in_title 恒真、prepend_title 后标题自成第 0 句参与判定、win_radius 取 config/panel.yaml::network_criteria.win_radius, 且该键与 filtering.yaml::cooccurrence_filter.sentence_radius 是互不联动的两个不同键) 见下方各 VAR 节。除判据梯子外, hyperedge_normalize 等权 vs Newman 归一构成另一条正交的构造敏感性维度 (当前预留未接线), 未来接线后同样应作为并排稳健性对照、而非叠加进同一识别式。

用大白话说, 这个家族做的事是: 把一年里的新闻当成一张"谁和谁一起被报道"的关系网, 银行是网上的点, 两家银行一起上过新闻就在它们之间画一条线; 度中心度就是数一家银行连出去多少条线——它今年在新闻里"认识"多少家不同的同业。同篇、相邻一句、同一句这三种越来越严的"算认识"标准, 就像分别问"同一天上过同一份报""被写进相邻的两句话""被塞进同一句话", 三种口径各画一张疏密不同的网、各算一遍度, 互相印证结论稳不稳, 但不能把三张网的度硬塞进同一道检验里当成三个独立证据。解读时要记住三条: 一是度只数"认识几家"不数"熟不熟"(熟不熟由强度列管); 二是一篇同时点名几十家银行的大榜单会一下子连出很多条线, 可能把整张网的形状带偏, 所以看"度高"别急着当成"关系铁"; 三是媒体报道里一起出现不等于业务上真有往来, 度中心度度量的是"媒体话语里的结构位置", 而且这些线是我们从新闻里"推断"出来的、不是直接看到的账目往来, 把它当作真实业务网络的代理时必须明确这层测量距离。这也是为什么本项目在同一批语料上还并置了嵌入相似度网络、经纪角色、结构洞、核度等多族测度, 让不同构念相互制衡, 避免单凭度中心度过度推断。

## VAR: bank_degree_cent

【变体差分】
本列是 F088 家族的 canonical 无后缀列, 也是 tier=core 的 headline 列。它采用"同篇 (article)"共现判据: 只要两家 both-verified 幸存银行出现在同一篇文档 (同一 docid) 中, 就在它们之间建一条边, 无论两者在文中相距多远 (可以一个在标题、一个在文末)。这是三个判据变体里最宽松的一档, 因而在同一年内产出的边最密、节点平均度最高、网络最不易断连。对应 build_adjacency_matrix 的主路径: 按 docid 聚合该篇幸存 target_bank 集合, 集合内每一无序对 +1 (对称写入), 完全不做句级重扫, 也因此不依赖 内容/标题 文本的分句——这使得同篇口径既是计算上最省的路径, 也是语义上"共同进入同一则新闻叙事"这一最基础的共现定义。正因门槛最低, 它对文本分句质量、句边界识别误差最不敏感, 因而被选作 canonical 主口径; 而更严的两个判据变体则以牺牲一部分对分句质量的稳健性为代价, 换取更强的"实质共现"语义, 二者形成互补的松紧梯度。同篇口径本质上是把每篇文章当作一个隶属团、对团内银行两两连边的二模到一模投影 (Faust, 1997; Borgatti & Everett, 1997), 因此它也是三判据里最直接暴露于"大-N 文章团投影污染"的一档——一篇提及 N 家银行的榜单会一次性贡献 C(N,2) 条等权边, 这正是引擎在同篇主路径 (而非分轨路径) 上保留 hyperedge_normalize 预留开关、并对 >10 家银行的大文章逐年 info 诊断的原因。

canonical 的取值语义: bank_degree_cent = degree(i)/(n-1), 其中 degree(i) 是银行 i 在该年同篇共现图中相邻的不同银行数, n 是该年进入网络的银行总数。它是纯拓扑量, 不计边权 (共现次数由 bank_strength_cent 单独承载), 因此一家银行只要与某同业在同一年任一篇报道里共现过一次, 就为其度数贡献 1, 再多次共现也不增加度 (只增加强度)。孤立银行 (当年出现却无任何同业共现) 取 0, 与全部其他银行都共现的极端中心银行取 1; 现实媒体共现网络高度偏斜, 少数标杆银行度极高、长尾大量银行度很低。作为纯拓扑计数, 本列不受 BLAS 浮点漂移影响、跨次重建逐位可复现, 是家族确定性锚——与同函数产出的 clustering/cfbetween/harmonic 三列 (BLAS 非确定) 形成对照, 后者验零漂移须按全名剔除而本列无须。

本列还是若干下游派生指标的原料, 因此其口径的稳定性具有外溢意义。其一, bank_is_hub (Top ~10% 枢纽哑变量) 由本列的度分布经阈值法生成: 取该年第 top10_count 名 (top10_count = max(1, ⌊N×0.10⌋)) 的度中心度为 cutoff, 所有度不低于该 cutoff 的银行判为枢纽 (并列同判, 避免旧实现按字典序硬切前 N 家在边界并列处任意判定的问题); 并设退化守卫: 当 cutoff≤0 (全孤立年) 或度分布退化为单一值 (正则图) 时, 统一置 0 以免"人人皆枢纽"的零方差常数列。其二, 网络级的度基尼系数 net_degree_gini_yr 直接以各银行的无权度序列度量"连接数不平等"(注意是连接数 Gini、非加权强度 Gini)。因此若本列口径变动, 会连带影响枢纽认定与度不平等度量, 这也是把它选作家族 SSOT 锚的实务理由之一。

在分析定位上, 本列作为描述性结构控制与稳健性维度进入 brokerage_network 相关论文体系 (Freeman, 1978; Bonacich, 1987; Nezami et al., 2025), 度量银行在媒体注意力网络中的连接广度。它与两个判据变体 _win1、_sent 构成"构造判据敏感性"的最宽松一端: 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。使用时应牢记同篇口径可能把"仅因同属一份榜单而被并列"的弱关联也计为边, 因此在需要更强"实质共现"语义时, 应以 _win1 / _sent 作为逐级收紧的稳健性参照, 而非把三者当作可以叠加进同一识别式的独立信息源。判据后缀 (无后缀) 与三轨文本后缀 (_full/_ctx/_ss) 属两个正交空间, 本列的"无后缀"仅指同篇判据, 与文本轨无关; 同理, 它主要作描述性坐标与稳健性维度, 因果解释外包给论文侧配备外生变异的模型 (Manski, 1993; Bramoullé et al., 2009)。

## VAR: bank_degree_cent_sent

【变体差分】
本列是"严格同句 (sent)"判据变体, 是三个判据里最严的一档。它只在两家 both-verified 幸存银行出现在同一句话之内时才建边——对应 build_adjacency_matrix 的分轨路径, criterion='sent' 时把句窗半径 radius 设为 0, 逐 docid 组内对 内容 正文 (prepend_title 后标题自成第 0 句) 重新分句, 用 map_bank_sentence_positions 定位每家银行出现的句号, 再由 bank_pairs_within_sentence_window 在半径 0 (即同一句) 内取银行对成边。因判据最严, 该口径产出的边最稀、平均度最低、网络最易断连, 度中心度水平系统性低于同篇 canonical, 也因此在偏斜语料上更易出现大量零度孤立节点。其语义是最保守的"实质共现": 两家银行不只是同处一文, 而是被记者写进了同一个句子, 通常意味着更直接的并列、比较或关联关系, 例如"工商银行与建设银行同时上线数字人民币试点"这类同句并置。

判据主体是银行∧银行, 扫描时启用与 stage 11/13/ctx/ss 共用的同一否定/短名排除事实源 (禁裸 AC 匹配, 防"涉农行业"误命中"农行"这类假阳性), 且 match_in_title 恒真, 故标题第 0 句亦参与同句判定。相较同篇口径, 严格同句因依赖分句边界的正确识别, 对分句质量更敏感, 这是它换取更强"实质共现"语义所付的代价; 与 _win1 相比, 它进一步剔除了跨相邻句才共现的对, 只保留最紧的同句关系。必须强调: _sent 判据后缀与三轨文本后缀 _ss 语义完全不同、绝不可混淆——_ss 是"银行∧金科同句"的文本轨 (判定哪段文本算银行金科报道, 且其回退语义镜像 ctx), 而 _sent 是"银行∧银行同句"的网络构造判据 (判定两家银行算不算共现); 两者判据主体不同、所在概念空间正交, 混用即口径错误。本列与 canonical、_win1 各自 just-identified 并排、互为稳健性、不分主次, 三者禁混同一 over-identified Hansen J。它同样是纯拓扑量, 不计边权、不受 BLAS 漂移影响、跨次逐位可复现。一个可供事后审计利用的数学不变量是: 三判据的节点全集恒同 (都是当年 both-verified 幸存银行), 而边集严格嵌套——同句成对必然落入 ±1 句窗、落入句窗必然同处一文, 故任一银行任一年份必有 bank_degree_cent_sent 不大于 bank_degree_cent_win1 不大于 bank_degree_cent; 若诊断中发现该单调性被破坏, 即指示分句或实体扫描环节存在口径漂移, 应视为数据缺陷而非结构信号。在 T=2 开发切片上, 严格同句口径极易退化为零方差 (几乎无同句共现对), 度中心度可能全为常数进而被固定效应吸收, 属预期现象, 生产 T=18 全量语料下方有实质变异。

## VAR: bank_degree_cent_win1

【变体差分】
本列是"±1 句窗 (win1)"判据变体, 严格程度介于同篇 canonical 与严格同句 _sent 之间。它在两家 both-verified 幸存银行出现在相邻句窗内 (默认句窗半径 win_radius=1, 即同句或相邻一句) 时建边——对应 build_adjacency_matrix 分轨路径, criterion='win1' 时 radius 取 config/panel.yaml::network_criteria.win_radius (默认 1), 逐 docid 组内对 内容 正文 (prepend_title 后标题为第 0 句) 重扫分句, 用 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 在半径 1 内取对成边。相较同篇口径, 它剔除了"相隔很远才各自出现"的弱共现; 相较严格同句, 它又放宽到允许跨相邻一句的邻近关系。因此其网络密度与平均度居于三判据之中, 度中心度水平介于 canonical 与 _sent 之间, 在稳健性梯子上恰好充当"中间松紧档"。

win_radius 取自 config/panel.yaml::network_criteria.win_radius, 该键与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科保留判据) 是两个不同的键、互不联动——前者判据主体是银行∧银行的网络构造, 后者是银行∧金科的留篇硬过滤, 语义正交, 改动其一不影响其二。match_in_title 恒为真 (镜像 stage 13 标题盲区修复), 故标题参与同句判定与句距计算, 一家银行出现在标题、另一家出现在正文首句时, 二者按第 0 句与第 1 句相邻、落入 ±1 句窗而成边。判据主体是银行∧银行, 同样启用共用的否定/短名排除事实源防假阳性。判据后缀 _win1 与三轨文本后缀 _ctx (银行∧金科实体窗) 语义不同, 前者是银行对的句距门槛、后者是判定银行金科关联的文本范围, 不可混淆。本列与 canonical、_sent 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。它是纯拓扑量, 不计边权、不受 BLAS 漂移影响、逐位可复现; 与分轨路径的另一档 _sent 一样, win1 路径对 hyperedge_normalize=True 直接 raise, 以防三判据轨在归一口径上无警告分叉。T=2 切片上句窗口径亦可能退化为零方差, 属预期, 生产 T=18 方有实质变异。选取相邻一句为中间档并非任意: 中文新闻写作中, 对多家机构的实质性并列陈述常以"上句点名、下句展开"的相邻句结构呈现, 半径 1 恰好把这类跨句衔接的实质关联收进边集, 同时排除仅因导语与结尾遥相呼应而共处一文的弱关联; 且本列继承三判据的边集嵌套不变量 (同句边是句窗边的子集、句窗边是同篇边的子集), 逐行度数介于 _sent 与 canonical 之间的单调排序可作免费的构造正确性诊断。

<!-- rendered-citations:begin -->
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage networks: Facilitating liquidity provision. Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 23619. https://doi.org/10.1103/PhysRevE.71.056103
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
<!-- rendered-citations:end -->
