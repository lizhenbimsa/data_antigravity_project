---
family_id: F460
columns:
- net_degree_gini_yr
- net_degree_gini_yr_sent
- net_degree_gini_yr_win1
unit: 无量纲不平等指数 (取值区间 [0, 1); 0=各行连接数完全均等, 越大越集中)
formula: "net_degree_gini_yr = Gini({deg_i}); deg_i = 年度银行共现无向图 G 中银行 i 的无权度 (邻居家数); Gini(x) = 2·Σ(i·x_(i)) / (n·Σx) − (n+1)/n, x 升序排列"
producer: news_process/pipeline/panel/network_spillover.py::_gini (调用点 compute_bank_network_centrality; 判据分轨 _build_year_adjacency) ; news_process/pipeline/panel/export.py (英文标签)
upstream:
- 40_article_bank_level.parquet (target_bank, year, docid, 内容, 标题)
- config/panel.yaml::network_criteria (win_radius, 默认 1)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: 104218
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
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
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
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
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
- doi: "10.1007/s11846-023-00689-y"
  type: journal
  authors: "Sánchez García, J., & Cruz Rambaud, S."
  year: 2023
  title: "The network econometrics of financial concentration"
  venue: "Review of Managerial Science"
- doi: "10.3390/jrfm17080325"
  type: journal
  authors: "Metelski, D., & Sobieraj, J."
  year: 2024
  title: "Trading Volume Concentration across S&P 500 Index Constituents—A Gini-Based Analysis and Concentration-Driven (Daily Rebalanced) Portfolio Performance Evaluation: Is Chasing Concentration Profitable?"
  venue: "Journal of Risk and Financial Management"
- doi: "10.1016/j.intfin.2025.102237"
  type: journal
  authors: "Mao, Y.-R., Shi, H.-L., Chen, H., & Wan, Y.-L."
  year: 2025
  title: "Detecting cross-firm momentum effects via shared analyst coverage: The role of leaders"
  venue: "Journal of International Financial Markets, Institutions and Money"
new_dois:
  - "10.1016/j.procs.2023.08.056"
  - "10.1007/s11846-023-00689-y"
  - "10.3390/jrfm17080325"
  - "10.1016/j.intfin.2025.102237"
---

## CORE

【构念与来源】
本家族刻画的是"银行共现网络的度分布不平等度", 即在给定年份内, 由媒体报道共同提及所连结成的银行网络中, 各家银行拥有的连接数量 (度) 分布得有多集中。核心列 net_degree_gini_yr 是一个网络级 (year-level) 结构指标: 它不属于任何单家银行的节点属性, 而是描述整张年度网络拓扑形态的一个标量, 在面板中按年份广播 (broadcast) 到当年全部银行行上, 使每家银行在同一年取到相同的取值。构念上它回答的问题是: 这一年的银行舆论关注是"雨露均沾"地分散到许多银行身上, 还是"赢者通吃"地集中于少数几家枢纽银行。取值越接近 0, 表示各行被共同提及的连接数越均等, 网络越扁平; 取值越大 (上界趋近 1), 表示少数节点垄断了绝大多数连接, 网络越呈星型集中形态。这一集中度视角与系统性风险文献里对"网络集中招致脆弱"的关切一脉相承 (Jackson & Pernoud, 2021), 也与金融网络中心性影响资产定价与信息扩散的证据相呼应 (Yu, Hu & Zhong, 2024; Xu & Zhao, 2024)。之所以选用度分布的不平等度而非简单的边数或平均度作为集中度刻画, 是因为不平等度是尺度不变量: 它剔除了网络规模 (节点数、总边数) 的直接影响, 只保留"连接如何在节点间分配"的形状信息, 从而使不同年份、不同规模的年度网络之间可比。这一性质对本项目尤为关键——媒体报道量逐年增长, 若用绝对边数或平均度, 年度间的比较会被"报道总量膨胀"这一与网络形态无关的趋势污染; 而度分布 Gini 对整体缩放不敏感, 只对"是否向少数枢纽集中"敏感, 恰好隔离出研究者真正关心的结构变化。换言之, 本列试图捕捉的是"关注结构的形状", 而非"关注总量的大小", 后者由 net_density_yr、报道计数等其他变量承载。

数据来源上, 边的定义来自新闻共现: 上游 40_article_bank_level 层提供每篇报道 (docid) 命中的目标银行 (target_bank) 与其年份、标题、正文。凡在同一判据下被判为"邻近共现"的两家银行之间即连一条无向边, 边权按篇累加但度 (degree) 的计算刻意采用无权口径, 即只数一家银行有多少个不同的邻居, 不看共现了多少次。判据 (criterion) 决定"邻近"如何界定, 这正是本家族三列的分野: canonical 列 net_degree_gini_yr 用"同篇"判据 (两家银行只要出现在同一篇报道即成边), _win1 用"±1 句窗"判据 (须落在相邻一句的窗口内), _sent 用"严格同句"判据 (须落在同一句内)。三判据来自同一执行计划 (NETWORK_TRITRACK_AND_CRITERIA_EXECUTION_PLAN_2026-07-02), 由 core/text/entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window 两个原语在生产与审计路径共用实现, 保证审计口径等同生产口径。须特别澄清: 这里的判据后缀 (无后缀 / _win1 / _sent) 与三轨文本后缀 (_full / _ctx / _ss) 是两个正交的概念空间——判据后缀刻画"银行∧银行"的邻接构造严格程度, 三轨文本后缀刻画"银行∧金科"的情感文本切片; 二者互不联动, 也绝不允许混进同一 over-identified Hansen J 检验。

【方法学与计算】
计算分两步。第一步构造年度邻接矩阵。对 canonical "同篇"判据, 生产主路径在同一 docid 下把当年幸存的 target_bank 行集合内的每一个无序对各加一条边 (每篇每对恰计一次), 由此得到对称邻接矩阵。对 _win1 / _sent 两个分轨判据, 走的是"docid 组内句级重扫"路径: 仅对同一 docid 下有至少两家幸存银行的组重新扫描正文与标题, 用 map_bank_sentence_positions 定位每家银行别名出现的句号, 再用 bank_pairs_within_sentence_window 以 win_radius 判定共现——_sent 令 radius=0 (严格同句), _win1 令 radius 取 config/panel.yaml::network_criteria.win_radius (默认 1, 即±1句)。分轨路径复用与 stage 11/13/ctx/ss 同一份否定与短名排除事实源, 禁用裸 AC 匹配, 以拦截"涉农行业→农行"这类短名假阳性; 且只把幸存银行的别名字典喂入扫描, 从源头杜绝 phantom 边。第二步在邻接图上算无权度序列并求其 Gini。度定义为 deg_i = G.degree(i), 即节点 i 的邻居家数 (不计边权)。Gini 采用离散排序闭式: 将度序列升序排为 x_(1)≤…≤x_(n), 则 Gini = 2·Σ_i(i·x_(i))/(n·Σx) − (n+1)/n。当年内不足两家银行、度序列全零 (无任何边) 或和为零时置 NaN, 属早期年份或稀疏判据下的预期退化。须强调一处口径披露 (network-metrics-audit N-04): 此处度是无权度 (连接数), 因此本指标衡量的是"连接数不平等"而非"加权共现强度不平等"; 后者需以 weight='weight' 走加权度 (strength) 口径, 与 bank_strength_cent 一致但与本列刻意不同——这是有意为之的拓扑集中度选择, 阅读时切勿把本列误读作强度分布集中度 (Opsahl, Agneessens & Skvoretz, 2010 对无权度与加权度的区分)。该指标确定性可复现, 无 RNG 与谱分解, 属 golden-safe, 不扩 BLAS-FP 非确定列排除集。关于 Gini 闭式的数学性质须补充两点。其一, 该离散排序式等价于 Gini 系数的"相对平均绝对差之半"定义, 但避开了 O(n²) 的两两差分, 以一次排序加一次带序号加权求和在 O(n·log n) 内完成, 数值稳定且无浮点非结合性引入的漂移。其二, 该式在有限样本下取值区间为 [0, (n−1)/n), 严格上界随节点数增大而趋近 1 而非恰达 1; 当且仅当度序列完全均等 (所有银行邻居家数相同, 含全零非退化情形外) Gini=0, 当单一节点垄断全部连接、其余为零时 Gini 趋近上界。本项目未做小样本 (n−1)/n 上界校正, 因生产 T=19 全量语料下年度节点数足够大, 校正影响可忽略; 但在开发切片这类 n 极小的年份, 读者须知本列的上界被有限 n 压低, 跨年比较时应与节点数联合解读。此外, 度序列的输入采用 bank_list 全序 (含孤立点, 度为 0), 而非仅计入有边节点——这意味着一年内被提及但从未与他行共列的"孤立银行"会以零度进入 Gini 计算, 系统性抬高不平等度; 这是有意的口径 (孤立本身即一种极端的连接稀缺, 应计入集中度), 与只在最大连通分量上计算的路径类指标 (net_avg_path_yr、net_diameter_yr) 的节点集不同, 勿混。

【文献定位】
把银行共现网络的度不平等作为一个结构变量, 立足于三条文献脉络。其一是社会网络的中心化与中心性测量传统: Freeman (1978) 系统厘清了度、介数、接近三类中心性并提出"网络中心化"(网络层面对个体中心性离散度的汇总) 概念, 度分布 Gini 正是同族的一个尺度不变、对网络规模稳健的集中度汇总。其二是金融网络与系统性风险: Jackson 与 Pernoud (2021) 综述指出网络的连接集中度是传染放大与脆弱性的关键结构特征, 度不平等高意味着少数枢纽节点一旦受冲击更易外溢; Li 等 (2026) 从文本风险披露中抽取金融网络结构与关联度, 与本项目"从新闻文本构造银行网络"的思路同源; Yu 等 (2024) 与 Xu、Zhao (2024) 进一步给出网络中心性影响信息扩散与资产价格的经验证据。其三是媒体—银行的情境文献: Fang 等 (2024) 以中国样本证明媒体情绪经由存款稳定性传导至银行系统性风险, Cookson 等 (2026) 展示社交媒体如何成为银行挤兑的催化器——二者共同支持"媒体共同提及本身即一种可度量、可能承载风险传染的连结"这一底层假设。Nezami 等 (2025) 对中心性—绩效关系的元分析则提示: 网络位置的经济后果异质且依赖情境, 因而必须以结构变量入模、辅以稳健性梯子, 而非单点断言。此外, Sánchez García 与 Cruz Rambaud (2023, Review of Managerial Science) 以网络计量方法刻画金融体系的连接集中度, 与本家族用度分布 Gini 汇总银行共现网络集中形态的思路直接呼应。须补充说明本指标在方法学谱系上的定位: 度分布 Gini 属于"网络级汇总统计量" (network-level summary), 与个体节点的中心性测量 (Freeman, 1978; Opsahl et al., 2010) 是聚合关系而非替代关系——它把 n 维的节点度向量压缩为一个描述其离散度的标量, 因而不可避免地丢失了"谁中心" 的身份信息, 只保留"有多集中" 的形状信息。这种压缩在计量上有明确用途: 当研究问题是"整体网络环境如何演变"而非"某家银行处于何位置"时, 汇总统计量避免了把 n 个高度共线的节点中心性同时塞入回归的多重共线与自由度浪费。与从文本直接抽取网络连接度的近期工作 (Li et al., 2026) 相比, 本项目的边来自"共同被提及"这一可观测事件, 语义上更接近"公众/媒体认知中的关联"而非资产负债表上的敞口关联, 因而本列刻画的是舆论关注结构的集中度, 其经济含义须在"媒体关注—银行行为/风险"的传导框架内解读 (Fang et al., 2024; Cookson et al., 2026), 不应直接等同于同业拆借或担保网络的结构集中度。

【识别策略定位】
在识别层面, net_degree_gini_yr 及其判据变体主要以年度结构控制变量 / 网络环境刻画量的身份进入模型, 而非因果处理变量。须清醒认识两点局限。第一, 作为年度广播量, 本列在同一年内对所有银行取同值, 因此在含年份固定效应 (year FE) 的规格中会被完全吸收而不可识别; 它的用武之地在于跨年比较、交互项 (与银行级变量交乘)、或不含 year FE 的描述性与机制刻画。第二, 网络位置的内生性与"反射问题"(Manski, 1993) 如影随形: 共现网络既可能塑造银行行为, 也可能由银行行为塑造, 且同群成员的结果相互决定使得线性均值模型的内生、外生同群效应难以分离。Bramoullé、Djebbari 与 Fortin (2009) 证明当网络存在"朋友的朋友非自身朋友"的可及性变异 (intransitivity) 时, 社会互动效应可借网络结构获得识别; 其后续综述 (Bramoullé, Djebbari & Fortin, 2020) 与 Grieser 等 (2022) 在公司金融政策情境下给出网络效应识别的可操作路径。本项目在使用这些结构量做溢出/同群分析时, 遵循上述文献的识别前提 (网络非完全传递、外生冲击或工具变量辅助), 并把度不平等这类"网络形状"控制量与"同群情感"这类"网络内容"变量分层处理, 避免把结构与内容混为一谈。第三, 共现网络本身由媒体报道行为生成, 报道量与报道偏好随时间、随监管周期波动, 因而本列的年度变异既含真实的银行关联结构演变, 也含媒体覆盖模式变迁; 在不含 year FE 的规格中须以报道总量、媒体来源数等控制量吸收后者, 否则易把"媒体扩张"误读为"网络集中度变化"。第四, 因本列是全网汇总而非个体位置, 它不适合承载"某家银行网络位置的因果效应"这类命题, 那类命题应改用节点级中心性并配合个体层面的识别策略。

【与相邻测度的构念区分】
本列须与家族及相邻家族的多个测度严格区分。与节点级中心性 (bank_degree_cent 等 18 个节点指标) 的区分: 后者是每家银行各自的网络位置 (个体属性, 年内跨行有别), 本列是整张网络的形状汇总 (年度标量, 年内跨行同值); 前者回答"这家银行有多中心", 本列回答"这一年的中心性有多集中"。与其他 9 个网络级指标的区分: net_density_yr 衡量边的填充比例 (整体稠密度), net_giant_share_yr 衡量最大连通分量占比 (连通集中), net_modularity_yr / net_assortativity_yr 衡量社群与同配结构, 而度分布 Gini 专注度序列的离散不平等——高密度未必高不平等 (完全图密度最高但 Gini=0), 二者正交。与加权强度口径的区分已如前述: 本列数邻居家数, 不数共现次数。特别地, 因本列是纯拓扑、确定性量, 它与家族外的三个 BLAS-FP 非确定网络列 (bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 及其判据变体) 在 golden 可复现性上分属两类——本列逐位可复现, 无须纳入零漂移验证的 drop 排除清单。

【已知局限与稳健性梯子】
已知局限包括: 早期稀疏年份 (早期试跑盘上 T=2 开发切片) 上判据越严, 边越少, Gini 越易退化为 NaN 或零方差, 属预期而非缺陷, 生产 T=19 全量语料上判据分轨方有充分方差; 超边规模效应 (一篇提及 N 家银行的榜单/批量通报天然贡献 C(N,2) 条等权边) 会抬高被反复共列银行的度, 主路径默认 +1 计边 (golden-safe), 预留的 hyperedge_normalize (Newman 度守恒归一) 尚未接线, 分轨路径显式禁用之以防口径无警告分叉。稳健性梯子的核心是三判据: net_degree_gini_yr (同篇) / net_degree_gini_yr_win1 (±1句) / net_degree_gini_yr_sent (同句) 三者是"网络构造判据敏感性"的并排稳健性设计, 各自 just-identified 并排、互为稳健性、不分主次, 用以证明主结论不被"共现邻近如何界定"这一研究者取值驱动; 铁律是三判据各自 just-identified 并排, 严禁把三判据混进同一 over-identified Hansen J (镜像政治词权重梯度、词典消融梯度、co-primary 嵌入双轨、三轨文本的同一铁律)。判据梯子与三轨文本梯子、co-primary 嵌入梯子彼此正交、互不交叉, 不设跨判据的 FWER 模板 (跨模型 rwolf 先例仅覆盖同构念替代 headline 测量, 本族属规格稳健性并排, 不适用); 若确需多重比较校正, 仍走根级 FWER 模板并遵循 Romano 与 Wolf (2005) 的逐步下降检验框架, 而非在判据轨内自造 over-identification。

进一步的稳健性叙事须澄清判据梯子与其它梯子的分工。判据梯子回答的是"共现邻近如何界定"这一测量取值敏感性, 与之正交的三轨文本梯子 (_full/_ctx/_ss) 回答"银行∧金科情感文本如何切片", co-primary 嵌入双轨回答"用哪一族嵌入度量语义", 政治词权重梯度回答"政治正面词赋多大权重", 词典消融梯度回答"启用哪些语言学规则"——五套梯子各自刻画一个独立的研究者自由度, 彼此正交、不交叉、不做笛卡尔积展开 (避免列数指数爆炸), 且每套梯子内部的各臂都遵循同一条铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把同一梯子的多臂混进同一 over-identified Hansen J 检验。就本家族而言, 这意味着三个判据列应各自单独进入 just-identified 规格并列报, 用系数的方向与显著性一致性证明主结论稳健, 而不是把三列同时作为过度识别工具或同一 J 检验的多个矩条件。另一条稳健性维度是超边规模的处理: 因媒体常有"榜单式""批量监管通报式"报道 (一篇同列大量银行), 这类大-N 文章会以 C(N,2) 条等权边显著抬高被反复共列银行的度, 从而压低 (更均等) 或抬高 (若集中于少数常客) 度不平等, 具体方向依数据而定。本项目主路径默认按每对 +1 计边以保持 golden 可复现, 并预留 Newman (2001) 度守恒归一选项 (hyperedge_normalize, 每对贡献 1/(N−1) 使单篇总度贡献守恒) 作为未来的稳健性臂; 该选项当前尚未接线到 config 与 runner, 且在判据分轨路径上被显式禁用 (raise), 以防三判据轨在未接线状态下出现无警告的口径分叉。读者在解读跨年趋势时, 须警惕榜单类报道占比的年度变化可能对本列造成的机械影响, 必要时应以剔除超大-N 文章后的稳健性重算佐证。最后, 关于缺失值语义: 本列在不足两家银行、度序列全零或和为零时置 NaN, 这在开发切片 (早期试跑 T=2、约 220 行) 上判据越严越常见, 属预期退化而非管道故障; 面板下游对 NaN 的处理 (整行剔除或保留) 由具体规格决定, 使用者须在样本量报告中明示因判据严格度导致的有效观测损失, 避免把稀疏判据下的样本缩减误读为选择性样本。

## VAR: net_degree_gini_yr

【变体差分】
本列是本家族的 canonical 列 (tier=core), 采用"同篇"共现判据 (criterion='article', 无后缀), 即两家银行只要在同一篇报道 (同一 docid) 中被共同提及即连一条无向边, 不要求二者出现在相邻句或同一句内。这是三判据中最宽松、边最稠密的构造口径, 也是 NETWORK_METRIC_BASES SSOT 中 net_degree_gini_yr 的注册基名。它由生产主路径 (both-verified 同 docid 幸存 target_bank 逐无序对 +1) 构图, 度取无权度 (邻居家数), Gini 取升序离散闭式; 英文标签在 export.py 中为 "Annual Degree Distribution Gini"。与两个判据变体的精确差分在于"邻近"的空间粒度: 本列不施加句级邻近约束, 因此把"同篇但相隔甚远"的银行对也算作连接——这会系统性地产生比 _win1 / _sent 更多的边、更大的度、通常更平缓 (更小) 的 Gini, 因为宽判据倾向把关注摊薄到更多银行对上。作为 canonical, 本列是主报告口径; 它在含年份固定效应的规格下不可识别 (年度广播量被 year FE 吸收), 主要用于跨年结构刻画、交互项与机制分析。它与 net_degree_gini_yr_win1、net_degree_gini_yr_sent 构成判据敏感性三元组, 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J; 该判据轨与三轨文本 (_full/_ctx/_ss)、co-primary 嵌入双轨彼此正交, 不交叉、不设跨判据 FWER 模板。须重申无权度口径: 本列衡量连接数 (拓扑连接) 的不平等, 而非加权共现强度的不平等, 阅读时不得与 bank_strength_cent 的加权口径混读。取值区间 [0,1), 越大表示当年少数枢纽银行垄断越多共同提及连接、网络越呈星型集中形态; 不足两家银行或度序列全零/和为零时置 NaN, 属稀疏年份预期退化。作为家族核心列, 本列的语义须与两类易混淆量再作切分。其一, 与 net_density_yr (年度网络密度) 的区分: 密度衡量实际边数占最大可能边数的比例, 是"网络有多满", 而本列衡量度在节点间的分配是否均等, 是"网络有多偏"; 完全图 (每对银行都共现) 密度为 1 但 Gini 为 0 (人人满度、完全均等), 星型图 (一家银行与所有人共现、其余互不共现) 密度很低但 Gini 很高——两者正交, 高密度绝不蕴含高集中。其二, 与节点级 bank_degree_cent (共现度中心性) 的区分: 后者是每家银行各自的度 (经规模归一的个体属性, 同年跨行有别), 本列是这些度的全网不平等汇总 (年度标量, 同年跨行同值); 若把全年所有银行的 bank_degree_cent 取出算其 Gini, 在同判据下即近似还原本列的构念 (差别仅在归一常数)。选用"同篇"作为 canonical 判据的理由是: 它对句级切分误差 (分句算法在中文长句、无标点段落上的不稳健) 最不敏感, 边的构造最稳健、最可复现, 适合充当主报告口径与判据梯子的锚; 更严的 _win1 / _sent 则作为并排稳健性轨, 检验主结论是否对"邻近如何界定"稳健。使用建议: 因本列为年度广播量, 在含 year FE 的双向固定效应面板中会被完全吸收而不可识别, 应仅在不含 year FE 的描述性回归、跨年时序刻画、或与银行级变量的交互项中使用; 与"网络内容"变量 (如同群情感溢出) 联用时须分层, 把本列这类"网络形状"控制量与情感内容变量置于不同解释角色, 避免结构与内容混淆。三判据 (本列/_win1/_sent) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 判据轨与三轨文本、co-primary 嵌入双轨正交不交叉。

## VAR: net_degree_gini_yr_sent

【变体差分】
本列 (tier=standard) 是 canonical net_degree_gini_yr 的"严格同句"判据变体 (criterion='sent', 后缀 _sent), 唯一差分在于邻接构造的邻近约束最严: 两家银行须在同一句 (win_radius=0) 内被共同提及方连边, 走 docid 组内句级重扫路径, 由 map_bank_sentence_positions 定位银行别名所在句号、bank_pairs_within_sentence_window 以 radius=0 判邻接。相对同篇判据, 同句判据剔除了"同篇但不同句"的松散共现, 只保留语义上最紧密、最可能表征真实关联叙事 (如"A 行与 B 行联合放贷""A 行收购 B 行") 的银行对, 因而边最稀、度最小, 在稀疏年份 (开发切片早期试跑 T=2) 上极易退化为零方差或 NaN, 属预期而非缺陷, 生产 T=19 全量语料上方有充分方差。除判据粒度外, 其余口径与 canonical 完全一致: 无权度、升序离散 Gini 闭式、年度广播、含 year FE 时不可识别、确定性 golden-safe。它与 canonical (同篇) 及 _win1 (±1句) 构成判据敏感性三元组, 三者各自 just-identified 并排、互为稳健性、不分主次, 用以证明主结论不被"共现邻近如何界定"驱动; 铁律是严禁把 _sent 与另两判据混进同一 over-identified Hansen J。判据后缀 _sent 属"银行∧银行"邻接构造概念空间, 与"银行∧金科"三轨文本后缀 _ss 是两个正交概念, 切勿因字面相近而混淆——_ss 是同句情感文本切片且有回退语义 (无银行∧金科同句共现时镜像 ctx 回退为全文 body、置 fallback 标志), _sent 是同句邻接判据且无任何文本回退 (同句无第二家银行即不成边、直接体现在度序列上), 二者不可互相复用。须进一步说明同句判据的语义价值与代价: 其语义价值在于把边约束到"同一句内并列提及"这一最强关联信号上, 从而最大限度排除"同篇但语境无关"的偶合共现 (如一篇宏观综述里前段提 A 行、后段提 B 行却毫无业务关联), 使成边更接近真实的银行间叙事关联 (联合放贷、并购、担保、同业往来); 其代价是句级切分对中文长句、无标点段落、以及别名跨句断裂 (银行全称被逗号或换行切开) 敏感, 可能漏判本应同句的共现, 因而 _sent 是三判据中"精确率高、召回率低"的一端。正因如此, 本项目不以 _sent 作 canonical, 而以最宽松、对切分误差最不敏感的同篇判据作主报告口径锚, 令 _sent 与 _win1 作并排稳健性轨检验主结论是否对"邻近如何界定"稳健。扫描文本口径与 canonical 一致: 复用与 stage 11/13/ctx/ss 同一份否定与短名排除事实源、禁裸 AC 匹配 (拦截"涉农行业→农行"类短名假阳性)、仅以幸存银行别名字典入参以杜绝 phantom 边, 且标题以 prepend_title 内嵌为第 0 句参与句级定位 (镜像 stage 13 match_in_title)。开发切片早期试跑 T=2 上 _sent 边最稀、极易零方差或 NaN, 属预期退化, 使用时须与另两判据并排列报, 三者各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: net_degree_gini_yr_win1

【变体差分】
本列 (tier=standard) 是 canonical net_degree_gini_yr 的"±1 句窗"判据变体 (criterion='win1', 后缀 _win1), 邻近严格程度介于同篇 (最宽) 与同句 (最严) 之间: 两家银行须落在相隔不超过 win_radius 句的窗口内方连边, win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1, 即±1句), 同走 docid 组内句级重扫路径。相对同句判据, ±1句窗容纳了"上下相邻句" 的共现叙事 (如一句写 A 行、紧邻一句写 B 行的并列报道), 因而边比 _sent 稍稠、度略大、Gini 通常介于同篇与同句之间; 相对同篇判据, 它又排除了"同篇远隔"的松散共现, 保留了一定的句级邻近语义。须特别澄清 win_radius 的键归属: 它取自 panel.yaml::network_criteria.win_radius, 与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科硬过滤所用) 是两个不同的配置键, 互不联动——改一个不会牵动另一个。除判据窗口外, 其余口径与 canonical 完全一致: 无权度、升序离散 Gini 闭式、年度广播、含 year FE 时不可识别、确定性 golden-safe, 幸存银行别名字典入参以防 phantom 边。它与 canonical (同篇) 及 _sent (同句) 构成判据敏感性三元组, 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J; 该判据轨与三轨文本、co-primary 嵌入双轨正交不交叉。判据后缀 _win1 属"银行∧银行"邻接构造概念空间, 与三轨文本后缀是正交概念, 勿混。在三判据的严格度谱系上, _win1 恰居中位, 因而它常被用作检验"同篇 vs 同句"两端结论是否单调、连续的中间锚: 若 canonical (同篇) 与 _sent (同句) 给出一致方向而 _win1 落在两者之间, 即为主结论对判据取值稳健的强证据。开发切片早期试跑 T=2 上 _win1 的边数虽多于 _sent, 但仍可能因语料稀疏而出现零方差或 NaN, 属预期退化, 生产 T=19 全量语料方有充分方差; 使用时须与另两判据列并排列报, 三者各自 just-identified、互为稳健性、不分主次。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Sánchez García, J., & Cruz Rambaud, S. (2023). The network econometrics of financial concentration. Review of Managerial Science. https://doi.org/10.1007/s11846-023-00689-y
Metelski, D., & Sobieraj, J. (2024). Trading Volume Concentration across S&P 500 Index Constituents—A Gini-Based Analysis and Concentration-Driven (Daily Rebalanced) Portfolio Performance Evaluation: Is Chasing Concentration Profitable? Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm17080325
Mao, Y.-R., Shi, H.-L., Chen, H., & Wan, Y.-L. (2025). Detecting cross-firm momentum effects via shared analyst coverage: The role of leaders. Journal of International Financial Markets, Institutions and Money. https://doi.org/10.1016/j.intfin.2025.102237
<!-- rendered-citations:end -->
