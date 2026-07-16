---
family_id: F096
columns:
- bank_katz_cent
- bank_katz_cent_sent
- bank_katz_cent_win1
unit: 网络结构指标 (无量纲; networkx katz_centrality 默认 L2 归一化分值)
formula: "bank_katz_cent = Katz 中心度 x_i, 满足 x = alpha * A^T x + beta*1 (beta=1), 即 x_i = sum_k sum_j alpha^k (A^k)_{ji} + 常数基线; alpha = 0.9 / lambda_max(A) (lambda_max<=0 时回退 0.01); A = 年度银行共现加权邻接矩阵 (build_adjacency_matrix, 每篇 docid 每对 both-verified 银行 +1, 对称); 判据变体 = {同篇 article 无后缀 canonical / ±1 句窗 _win1 / 严格同句 _sent}"
producer: pipeline/panel/network_spillover.py::compute_bank_network_centrality (经 build_adjacency_matrix 建图; stage 46_network_spillovers 函数库, panel runner 网络步骤调用) ; pipeline/panel/export.py (dta 变量标签)
upstream:
- 21_tone_llms.parquet (docid + target_bank, both-verified 篇章级留篇集; 留篇门控 full-only)
- 40_panel_yearly.parquet (bank-year 面板合并宿主)
- config/panel.yaml::network_criteria.win_radius (_win1 判据句窗半径, 默认 1)
- config/bank_list.yaml + bank_name_exclusions.json (银行别名 + 否定/短名排除事实源, _win1/_sent 重扫共用)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.1002/csr.70661"
  type: "journal"
  authors: "Huangfu, X."
  year: 2026
  title: "Board Networks and Corporate Transparency: How Independent Director Centrality Drives ESG Disclosure Quality"
  venue: "Corporate Social Responsibility and Environmental Management"
- doi: 10.1016/j.jeconom.2025.106130
  type: journal
  authors: Hughes, D. W.
  year: 2026
  title: "A jackknife bias correction for nonlinear network data models with fixed effects"
  venue: Journal of Econometrics
  vol: 253
  pages_or_artno: "106130"
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: 10.1007/s11747-024-01043-8
  type: journal
  authors: Nezami, M., Chisam, N., & Palmatier, R. W.
  year: 2025
  title: "Network centrality and firm performance: A meta-analysis"
  venue: Journal of the Academy of Marketing Science
  vol: 53
  issue: 1
  pages_or_artno: "79-104"
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: "181-204"
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
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: "110"
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: "1145-1182"
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: "543-565"
- doi: 10.1093/restud/rdae088
  type: journal
  authors: de Paula, A., Rasul, I., & Souza, P. C. L.
  year: 2024
  title: "Identifying network ties from panel data: Theory and an application to tax competition"
  venue: The Review of Economic Studies
  vol: 92
  issue: 4
  pages_or_artno: "2691-2729"
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: 132
  issue: 7
  pages_or_artno: "2274-2303"
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
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: "603-629"
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: "2693"
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: 11
  pages_or_artno: "727-753"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: "43-96"
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: "1423-1465"
- doi: 10.3368/jhr.50.2.317
  type: journal
  authors: Cameron, A. C., & Miller, D. L.
  year: 2015
  title: "A practitioner's guide to cluster-robust inference"
  venue: Journal of Human Resources
  vol: 50
  issue: 2
  pages_or_artno: "317-372"
- doi: 10.1080/15427951.2013.865686
  type: journal
  authors: Boldi, P., & Vigna, S.
  year: 2014
  title: "Axioms for centrality"
  venue: Internet Mathematics
  vol: 10
  issue: 3-4
  pages_or_artno: "222-262"
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: "139-178"
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
- doi: 10.1016/j.socnet.2004.11.009
  type: journal
  authors: Newman, M. E. J.
  year: 2005
  title: "A measure of betweenness centrality based on random walks"
  venue: Social Networks
  vol: 27
  issue: 1
  pages_or_artno: "39-54"
- doi: 10.1103/PhysRevE.71.056103
  type: journal
  authors: Estrada, E., & Rodríguez-Velázquez, J. A.
  year: 2005
  title: "Subgraph centrality in complex networks"
  venue: Physical Review E
  vol: 71
  issue: 5
  pages_or_artno: "056103"
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: "1237-1282"
- doi: 10.1073/pnas.0400087101
  type: journal
  authors: Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A.
  year: 2004
  title: "The architecture of complex weighted networks"
  venue: Proceedings of the National Academy of Sciences
  vol: 101
  issue: 11
  pages_or_artno: "3747-3752"
- doi: 10.1038/30918
  type: journal
  authors: Watts, D. J., & Strogatz, S. H.
  year: 1998
  title: "Collective dynamics of 'small-world' networks"
  venue: Nature
  vol: 393
  issue: 6684
  pages_or_artno: "440-442"
- doi: 10.1016/S0378-8733(96)00300-0
  type: journal
  authors: Faust, K.
  year: 1997
  title: "Centrality in affiliation networks"
  venue: Social Networks
  vol: 19
  issue: 2
  pages_or_artno: "157-191"
- doi: 10.1016/S0378-8733(96)00301-2
  type: journal
  authors: Borgatti, S. P., & Everett, M. G.
  year: 1997
  title: "Network analysis of 2-mode data"
  venue: Social Networks
  vol: 19
  issue: 3
  pages_or_artno: "243-269"
- doi: 10.1016/j.socnet.2007.04.006
  type: journal
  authors: Latapy, M., Magnien, C., & Del Vecchio, N.
  year: 2008
  title: "Basic notions for the analysis of large two-mode networks"
  venue: Social Networks
  vol: 30
  issue: 1
  pages_or_artno: "31-48"
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: "531-542"
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
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: Bonacich, P.
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: "113-120"
- doi: "10.1093/rfs/hhae025"
  title: "News Diffusion in Social Networks and Stock Market Reactions"
  authors: "Hirshleifer, D., Peng, L., & Wang, Q."
  year: 2024
  venue: "The Review of Financial Studies"
  type: "journal"
- doi: "10.1287/mnsc.2023.4891"
  title: "Analyst Coverage Networks and Corporate Financial Policies"
  authors: "Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F."
  year: 2024
  venue: "Management Science"
  type: "journal"
- doi: "10.1016/j.iref.2025.104355"
  title: "Measuring systemic risk from textual Analysis: Evidence from Chinese Banks"
  authors: "Fang, Y., Lin, H., & Lu, L."
  year: 2025
  venue: "International Review of Economics & Finance"
  type: "journal"
- doi: "10.1016/j.najef.2025.102577"
  title: "Bank systemic risk prediction based on text mining and explainable machine learning"
  authors: "Wang, P., & Borjigin, S."
  year: 2026
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
new_dois:
- "10.1002/csr.70661"
- "10.1093/rfs/hhae025"
- "10.1287/mnsc.2023.4891"
- "10.1016/j.iref.2025.104355"
- "10.1016/j.najef.2025.102577"
---

## CORE

该文用S&P 500公司面板证明独立董事网络中心度提升ESG披露质量、且效应在媒体关注度更高时增强, 为网络中心度测度与媒体关注交互影响公司信息环境提供了2026年的实证参照, 可与本家族媒体共现网络中心度构念互为对照。

【构念与来源】
本家族测度的构念是银行在年度媒体共现网络中的 Katz 中心度, 回答的问题是: 在中文财经媒体的报道生态里, 一家银行不仅自己被频繁地与其他银行同篇提及, 而且它的共现邻居本身又与更多银行相连时, 它在整个报道网络中占据的全局性显要位置有多突出。用大白话讲: 度中心度数的是这家银行认识多少邻居, 而 Katz 中心度还进一步追问这些邻居各自又认识谁、邻居的邻居又认识谁, 把所有长度的间接关联链条全部纳入, 只是链条越长打的折扣越重。这一构念的思想源头是 Katz 在二十世纪五十年代提出的地位指数, 后经 Bonacich (1987) 系统化为带衰减参数与基线项的幂中心度家族, 与 Bonacich (1972) 的特征向量中心度构成同一谱系: 当衰减参数趋近于邻接矩阵主特征值的倒数时, Katz 中心度收敛到特征向量中心度; 当衰减参数趋近于零时, 它退化为度中心度的仿射变换。因此 Katz 中心度可以理解为在局部连接数与全局声望之间连续插值的测度, 项目在 dta 导出标签中以宏观经济学网络文献的惯用引法标注这一测度族, 呼应生产网络冲击传导研究中 Katz-Bonacich 向量作为影响力向量的经典地位。数据来源是本项目 2007 至 2025 年中文银行金融科技新闻语料: 上游 stage 21 产出的篇章级留篇集给出每篇文章 (docid) 与其中通过双重验证 (both-verified) 的目标银行集合, 由此把每一年份的所有文章折叠成一张银行与银行之间的加权无向共现网络, 节点是当年至少出现在一篇留存文章中的银行, 边权是两家银行被同一篇文章共同提及的文章篇数。留篇门控遵循 2026-06-29 的 full-only 口径: 一篇文章是否算作银行金融科技报道, 只看 full 轨的 llm_verified_full 判定, 因此共现网络的文章宇宙与面板 n_articles 分母同源, 不存在 ctx 或 ss 轨单独扩充或收缩网络样本的通道。以媒体文本构造经济主体间网络的做法在文献中已有坚实先例: Hoberg 与 Phillips (2016) 用产品描述文本相似度构造企业竞争网络并证明文本网络能捕捉传统行业分类遗漏的经济关联, Li 等 (2026) 从风险披露文本中恢复金融机构间的关联结构, 而 You 等 (2018) 与 Fang 等 (2024) 则分别证明中国媒体报道的立场与情感对资本市场和银行系统性风险具有真实的信息含量, Xu (2024) 进一步说明财经记者自身的社会网络会系统性地塑造报道的联结结构。这些工作共同支撑本家族的前提假设: 媒体共现不是噪声, 而是承载银行间业务关联、事件关联与公众认知关联的可测信号。Fang, Lin & Lu (2025, International Review of Economics & Finance) 该文用中文银行媒体文本共现构建网络并以负面新闻指数衡量系统性风险, 直接支持本家族以媒体共现网络刻画银行结构位置的构念前提。Wang & Borjigin (2026, The North American Journal of Economics and Finance) 该文以银行相关文本挖掘特征结合可解释机器学习预测系统性风险, 呼应本家族媒体文本网络位置作为银行系统性风险代理的应用语境。

【方法学与计算】
计算分建图与求解两步, 生产实现位于 pipeline/panel/network_spillover.py, 该模块是 stage 46_network_spillovers 的函数库 (无独立 main, 由 panel runner 的网络步骤调用, 日志写 46_network_spillovers.log)。第一步建图由 build_adjacency_matrix 完成: 对目标年份的篇章级数据按 docid 分组, 每篇文章内的每一对不同的 both-verified 银行为对应邻接矩阵元素对称地加一, 得到以共现篇数为边权的无向加权图。这里有一个承重的历史修正: 主路径刻意改为按 docid 聚合而不再消费 stage 11 遗留的 co_mentioned_banks 字段, 因为后者在 stage 21 验证过滤之后仍会列出已被否决的银行, 是幽灵边的来源; 旧字段仅在缺 docid 的旧 schema 下作降级兜底。canonical 判据是同篇共现 (criterion 为 article, 列名无后缀): 两家银行只要出现在同一篇留存文章中即记一次共现。第二步求解 Katz 中心度: 先用 networkx 把当年图转成稠密邻接矩阵, 以 numpy 特征值分解取谱半径 lambda_max, 令衰减参数 alpha 等于 0.9 除以 lambda_max (谱半径非正时回退到 0.01 的保守常数), 再调用 networkx 的 katz_centrality 以边权参与迭代求解, 基线项 beta 取默认值 1, 解向量按 L2 范数归一化。alpha 严格小于谱半径倒数是 Katz 级数收敛的充要条件, 取 0.9 倍是在收敛安全边际与"尽量吸收长链信息"之间的研究者选择: alpha 越接近上界, 测度越接近特征向量中心度的全局声望语义; 系数 0.9 使测度保留明显的全局成分同时对退化图保持数值稳定。求解被 try/except 包裹: 任何异常 (如极端图形态导致的线性代数错误) 触发该年份全部银行的 bank_katz_cent 置 NaN 并写警告日志, 属 fail-loud 而非静默填零; 与之相区别, 求解成功但某银行不在解字典中时以 0.0 兜底, 两种缺失语义不同, 使用者做缺失值分析时应注意区分。与路径类指标 (closeness, harmonic, betweenness) 需要把"共现越多等于关系越近"翻译成倒数边权不同, Katz 中心度直接在原始权重图上工作, 共现篇数越大对邻居分值的传递越强, 语义上更贴近"关联强度加权的影响力"。判据敏感性分轨 (2026-07-03) 为同一基名派生三个判据臂: 无后缀同篇臂之外, _win1 臂要求两家银行的提及落在正负 win_radius 句 (config/panel.yaml 下 network_criteria.win_radius, 默认 1) 的窗口内, _sent 臂要求严格同句; 两个严格臂对每个多银行 docid 走组内文本重扫, 判据原语是 core/text/entity_context 的 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 扫描文本按 prepend_title 口径把标题当作第 0 句 (镜像 stage 13 的 match_in_title), 银行识别复用与 stage 11 和 13 相同的否定过滤与短名排除事实源 (防止"涉农行业"误命中"农行"一类假阳性), 禁用裸 AC 自动机。三判据臂的节点全集与同篇臂一致 (同一年度幸存银行), 仅边集依次收紧, 因此跨臂差异干净地归因于共现判据的严格程度而非样本构成。计算完成后逐年合并回 bank-year 面板, 由 stage 46 的 stata 导出为其挂英文变量标签。

【文献定位】
Katz 中心度在方法学谱系中的坐标由三条线索确定。第一条是社会网络分析的测度公理化传统: Freeman (1978) 厘清了度、接近、中介三类中心度概念各自回答的问题, Bonacich (1972, 1987) 建立了以特征结构为核心的声望测度家族, Boldi 与 Vigna (2014) 给出中心度的公理体系并证明 Katz 型测度在尺寸公理与密度公理上的良好性质 (调和中心度是其公理筛选的另一幸存者, 本项目同族的 bank_harmonic_cent 与之呼应), Opsahl 等 (2010) 则把度与最短路两类测度推广到加权网络, 为本家族在共现计数权重图上直接求解的做法提供依据。第二条是金融网络与系统性风险文献: Jackson 与 Pernoud (2021) 综述了金融网络中冲击传导与网络位置的理论关系, 指出特征向量型与 Katz-Bonacich 型中心度刻画的正是机构在传染动力学中的放大角色; Sadeghi 与 Feinstein (2024) 对金融网络传染中心度做统计显著性验证, 强调中心度排序须区分真实结构与抽样噪声; Wang 等 (2020) 刻画了中国担保网络在金融危机与刺激计划下的演化, Gao 等 (2022) 证明股权网络位置影响银行信贷决策的信息渠道, 两者共同说明在中国制度背景下机构间网络位置具有实质经济含量。第三条是资产定价与绩效的实证应用: Yu 等 (2024) 发现网络中心度通过信息扩散渠道进入资产定价, Xu 与 Zhao (2024) 系统比较了不同节点中心度对金融资产价格预测的边际贡献, Nezami 等 (2025) 的元分析汇总了跨学科数百个效应量, 确认网络中心度与企业绩效之间存在稳健正相关但效应大小高度依赖测度选择与网络类型。媒体驱动的银行网络这一具体语境则由 Cookson 等 (2026) 与 Khan 等 (2024) 补足: 前者证明社交媒体信息流可以成为银行挤兑的催化剂, 后者展示硅谷银行事件经由媒体网络产生跨机构多米诺效应, 两者共同说明"报道网络中的居中位置"在压力时期可能同时是信息优势与传染暴露的代理, 这正是本家族测度在下游回归中承担的双重解释角色。Hirshleifer, Peng & Wang (2024, The Review of Financial Studies) 证明社交网络中较高中心度的地理社群会加速新闻向价格的传导并放大交易量反应, 为本家族报道网络中心度承载真实信息含量的前提假设提供了资产定价侧的最新实证支持。

【识别策略定位】
在计量识别层面, bank_katz_cent 家族在本项目的角色是网络位置的截面与时序刻画变量, 主要用作三类右手边角色: 一是作为控制变量吸收"报道显要度"对情感处理变量与结果变量的共同驱动, 二是作为异质性调节变量检验主效应是否随网络位置分层, 三是在网络溢出族回归 (industry_neg_shock 与 emb_peer_tone 等 W-轨测度) 中作为结构性补充刻画。凡把网络位置或其派生的同伴均值放上右手边, 就绕不开 Manski (1993) 的反射问题与 Bramoullé 等 (2009, 2020) 给出的图结构识别条件: 内生同伴效应、外生情境效应与相关效应在线性期望模型中一般不可分, 而非传递性三元组 (朋友的朋友不是朋友) 提供的排除约束正是 Katz 型长链结构可以识别同伴效应的数学根源; Boucher 等 (2024) 进一步把这一识别框架推广到一般偏好基础上。共现网络本身是内生对象: Grieser 等 (2022) 证明企业网络中财务政策的溢出估计对网络形成的内生性高度敏感, de Paula 等 (2024) 则给出从面板数据反推网络连边的识别理论, 提醒使用者媒体共现边可能部分由结果变量的共同冲击生成。本项目的缓解设计有三层: 其一, 项目 IV 扩展族提供同组 leave-one-out 均值与广义 Bartik 型工具, 其构造逻辑遵循 Borusyak 等 (2025) 对份额型工具有效性条件的刻画, 供网络暴露类回归做工具变量法稳健性; 其二, 网络级年度指标 (net_ 前缀族) 在年份固定效应下不可识别、仅节点级指标携带组内变异, 这一分工在导出标签中明示, 避免把年度广播量误当识别来源; 其三, 短面板网络模型的关联偏差可循 Hughes (2026) 的 jackknife 思路做偏差校正敏感性。在结构解释层面还有一个更深的对应关系值得写明: 在线性二次效用的网络博弈里, 纳什均衡的行动向量恰好等于以行动互补强度为衰减参数的 Katz-Bonacich 向量, 这意味着把 bank_katz_cent 放上右手边并不只是描述性的"位置控制", 它同时是同伴互动结构模型的约化形式统计量 — 系数显著既可能反映位置本身的回报, 也可能反映未建模的均衡放大机制, 两种解读的区分须依赖外生变异而非网络统计量本身。因此工具变量臂的诊断规范须一并写死: 采用 leave-one-out 或 Bartik 型工具时, 弱工具诊断按 Andrews 等 (2019) 的实践指引报告有效 F 统计量与弱工具稳健置信集, 不以传统一阶段 F 大于十的经验法则代替; 若报道覆盖高度集中于头部银行, Gabaix 与 Koijen (2024) 的颗粒工具变量思路提供了另一条可行路径 — 利用大型机构特异冲击在加总暴露中的不可忽略份额构造工具, 这与媒体共现网络右偏的度分布形态天然契合。识别之外的推断口径同样承重: 网络位置变量在截面上天然相关 (同一年度图上所有节点的分值由同一次特征值求解联动生成), 残差的截面依赖不可当作独立观测处理, 聚类标准误的选择按 Cameron 与 Miller (2015) 的实务指引以银行维度聚类为底线、以银行与年份双向聚类为稳健性上限, 且须警惕短面板下聚类数不足导致的过度拒绝。同伴效应文献中的另一条识别路线 — Leary 与 Roberts (2014) 以同伴企业特异股票收益冲击作为同伴行为的工具 — 提示了本家族的一个对照设计: 网络溢出族中以同组特异情感冲击替代结构位置作外生变异来源, 与 Katz 位置控制互为补充而非替代。Gomes, Gopalan, Leary & Marcet (2024, Management Science) 以分析师覆盖网络中的朋友的朋友结构分离内生同伴效应与情境效应, 为本家族在识别策略定位一节讨论的网络内生性与同伴效应识别问题提供了另一同期方法论参照。推断口径上须强调: 三个判据臂属于规格稳健性并排, 按项目铁律各自 just-identified 进入各自的回归、互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J; 判据臂也刻意不设 FWER 模板, 因为项目真正的族错误率控制走 Romano 与 Wolf (2005) 的逐步降压程序 (根级 rwolf 模板), 其先例仅覆盖同一构念的替代 headline 测量 (跨厂商情感模型), 而判据臂检验的是构造口径敏感性而非多假设族, 把口径敏感性伪装成多重检验校正反而会稀释两类证据各自的解释力。

【与相邻测度的构念区分】
本家族与同一 33 指标 SSOT (NETWORK_METRIC_BASES) 中的相邻中心度测度构念边界如下。与 bank_degree_cent 和 bank_strength_cent 相比: 度与强度 (Freeman 1978; Opsahl 等 2010) 只看直接邻居的个数或权重和, 是纯局部测度; Katz 把全部长度的游走纳入几何衰减求和, 两家直接连接数相同的银行若邻居质量不同则 Katz 分值分化, 因此 Katz 对"二阶及以上的结构优势"敏感而度中心度按构造不敏感。与 bank_eigen_cent 相比: 特征向量中心度 (Bonacich 1972) 是 Katz 在 alpha 趋近谱半径倒数且无基线项时的极限, 但它在断连图与低连通图上退化, 生产实现须按连通分量分别计算并把小于三个节点的微小分量置 NaN; Katz 因带常数基线项 beta 对每个节点注入保底分值, 在同样的稀疏年度网络上对孤立点与小分量给出有限且可比的分值, 这正是共现网络这种天然碎片化图形态下 Katz 相对特征向量的工程优势, 也是两列缺失模式系统性不同的原因。与 bank_subgraph_cent 相比: 子图中心度 (Estrada 与 Rodríguez-Velázquez 2005) 对闭合游走 (从自己出发回到自己) 按阶乘衰减求和, 度量的是节点参与网络内闭环冗余结构的深度, 而 Katz 对从他人到达自己的开放游走按几何衰减求和, 度量的是可达性意义上的声望; 前者阶乘衰减压制长链, 后者几何衰减保留长链, 构念与数值行为均不同。与 bank_between_cent 和 bank_cfbetween_cent 相比: 中介与电流中介 (Newman 2005) 度量的是节点作为他人之间通道的桥梁地位, 与 Katz 的声望语义正交, 一个占据结构洞的经纪节点可以中介很高而 Katz 平平。与 bank_closeness_cent 和 bank_harmonic_cent 相比: 距离类测度在倒数权重图上工作 (共现越多距离越短), 语义是到达全网的效率; Katz 在原始权重图上工作, 语义是被到达的强度, 两者对边权的使用方向相反, 禁止把它们的分值直接横向比较。与 bank_kcore 相比: k-核分解 (Seidman 1983) 给出的是节点所处凝聚子结构的最大深度, 是一个中观尺度的离散台阶量, 度量"嵌入在多稠密的核心圈层里", 而 Katz 是连续的个体声望量, 核数相同的两家银行 Katz 可以差一个数量级, 反之高 Katz 的桥接节点可能只处在浅核, 两者联合使用可分离"圈层归属"与"个体可达性"。与 bank_clustering 相比: 聚类系数 (Watts 与 Strogatz 1998) 度量的是自我网络的闭合程度 — 我的邻居之间是否也互相认识, 高聚类意味着冗余的本地闭环; Katz 恰恰对"邻居们各自通向不同远方"的开放结构给高分, 两者在结构洞理论意义上接近互补, 且加权图上聚类系数的推广形式本身存在多个互不等价的定义 (Barrat 等 2004), 而 Katz 的加权推广是唯一自然的 (权重直接进入游走求和), 这也是本项目把聚类列而非 Katz 列列入 BLAS 浮点非确定观察清单的间接原因之一。还有一层更基础的结构区分须写明: 媒体共现网络本质上是"文章乘银行"二部隶属网络的单模投影, 隶属网络的中心度理论 (Faust 1997; Borgatti 与 Everett 1997) 与大规模二部图分析框架 (Latapy 等 2008) 都指出, 投影会把每篇多银行文章机械地变成投影图上的完全子图, 使投影图的稠密度与聚类水平系统性高于同规模随机图, 因此在投影图上解读任何中心度都必须意识到"团块是构造的产物"这一底色; 本家族在投影图而非二部图上求解 Katz 是刻意选择 — 研究对象是银行间的间接可达性而非银行与文章的隶属强度 — 但使用者引用跨家族网络统计量时应记得这一共同的投影基因。最后, 判据后缀与三轨文本后缀是两个正交概念空间: _win1 与 _sent 是银行与银行共现判据的严格化, 而 _full、_ctx、_ss 是银行与金融科技共现语境的文本轨道, 本家族列名中不出现文本轨后缀, 任何把判据臂与文本轨臂混同的解读都是口径错误。

【已知局限与稳健性梯子】
第一, 构造效度局限: 媒体共现是银行间关联的噪声代理, 它混合了业务关联 (同业、银团、并购)、事件关联 (同受一项监管冲击) 与纯粹的报道惯例 (盘点式新闻罗列多家银行), 后者会制造与经济关联无关的稠密团。判据梯子正是针对这一局限设计的敏感性工具: 同篇臂容忍盘点式共现, 同句臂几乎只保留强绑定表述, 若下游结论仅在同篇臂成立而在严格臂下消失, 应怀疑结果被罗列式报道驱动。第二, 参数选择局限: alpha 取 0.9 倍谱半径倒数是研究者选择, 无自然单位; 由于逐年谱半径不同, alpha 逐年变化, 跨年分值的可比性依赖归一化而非 alpha 恒定, 使用者应优先在年份固定效应内解读组内变异, 谨慎解读跨年水平差。第三, 数值再现性: 谱半径经由稠密特征值分解获得, 属 BLAS 浮点运算; 项目在册的非确定网络列清单 (bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 各三判据臂共九列) 不含 katz 族, 但跨机器验证零漂移时仍建议对特征值分解路径保持警惕。第四, 失败语义不对称: 全年求解异常置 NaN 与个别银行缺席解字典置 0.0 并存, 极端小年份网络下 0.0 可能被误读为"真实低中心度"。第五, 小样本退化: 开发环境短面板下年度网络稀薄, 判据严格臂的边集可能接近空图, Katz 分值坍缩到基线项主导的近常数, 属预期退化而非缺陷, 生产全量语料下不适用该借口。第六, 分轨路径的边界守卫: 判据臂不支持超边归一化选项 (显式抛错而非静默分叉), 保证三臂建图逻辑除判据外严格同构。稳健性梯子的完整叙事是: 三判据臂 (本家族) 与测度族内的相邻中心度 (度、强度、特征向量、子图、中介) 构成双向三角互证, 判据臂检验共现口径敏感性, 相邻测度检验构念操作化敏感性; 全部并排臂遵守同一铁律 — 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 该口径与三轨文本、co-primary 双轨嵌入、词典消融与政治词权重梯子完全一致。第七, 投影边的统计效度: 承接上节的二部投影底色, 投影图中的一条边未必对应统计上显著的关联 — 两家被媒体高频报道的大型银行即使在随机配对下也会大量同篇出现, Cimini 等 (2022) 对二部投影的元验证研究系统比较了各种投影边显著性过滤方法并指出未经验证的投影会高估网络的真实结构, Sadeghi 与 Feinstein (2024) 在金融传染语境下同样主张对中心度排序做统计显著性检验; 本家族现行实现不做投影边过滤 (保留全部共现计数作边权), 这是一个已知且刻意记录的局限 — 判据梯子从文本口径侧收紧边集, 是对同一问题的替代性缓解, 而基于零模型的边显著性过滤是文档在案的可选升级路径, 未实现前使用者应把宽松臂的稠密结构视为上界而非真值。第八, 覆盖选择性: 进入网络的银行以当年被留存报道提及为前提, 媒体对大型机构的系统性偏好意味着小银行的节点缺席本身携带信息, 把本族分值当作全体银行的无条件网络位置解读会引入选择偏差; 严谨用法是明示样本宇宙为"当年有留存报道的银行", 并在稳健性中报告以银行固定效应吸收持续性覆盖差异后的组内估计。

## VAR: bank_katz_cent

【变体差分】
本列是家族 canonical 列, 采用同篇共现判据 (criterion 为 article), 列名无后缀即现行生产口径, 在 33 指标基名 SSOT (network_spillover.NETWORK_METRIC_BASES) 中注册, dta 导出携带 Co-mention Katz Centrality 英文标签。精确语义: 对每个年份, 把该年全部 full-only 留篇文章按 docid 折叠, 同一篇文章内每一对 both-verified 银行贡献一条权重加一的对称边, 无论两家银行在文中相距多远、是否出现在同一句甚至同一段, 只要同篇即计; 在此加权图上以 alpha 等于 0.9 除以当年谱半径 (谱半径非正时回退 0.01)、基线 beta 等于 1、边权参与迭代的设定求解 Katz 中心度, 解向量 L2 归一化后按银行合并回 bank-year 面板。同篇判据是三臂中最宽松的口径, 边集是 _win1 与 _sent 两个严格臂的超集, 因此本列的网络最稠密、连通性最好、Katz 级数吸收的长链信息最多; 相应的代价是对盘点式报道 (一篇新闻罗列十家银行的年报盘点) 最不设防, 此类文章会在当年图上制造完全子图, 系统性抬高被频繁纳入盘点名单的大型银行的分值。选择同篇作 canonical 的理由有三: 其一, 它与项目其他篇级共现口径 (如 stage 13 银行与金融科技的留篇过滤以篇为单位) 的观测粒度一致, 便于分母对齐; 其二, 宽松判据下年度网络的连通分量更大更稳定, Katz 求解的数值条件最好, 全年置 NaN 的失败概率最低; 其三, 它是 2026-07-03 判据分轨之前的既有生产口径, 无后缀命名是历史连续性的产物而非"更优"的宣示 — 与政治词权重梯子中 polw05 等价于无后缀列的先例同构, canonical 地位来自延续性与工程稳健性, 不来自构念优先级。缺失语义须注意双通道: 当年 Katz 求解整体异常时本列该年全部银行为 NaN (fail-loud), 求解成功但个别银行未出现在解字典时为 0.0 兜底, 二者不可混同。使用建议: 作为控制或调节变量时与年份固定效应搭配, 解读组内变异; 与 _win1、_sent 两个严格臂的关系是互为稳健性、不分主次, 三臂各自 just-identified 进入各自回归, 禁混进同一 over-identified Hansen J; 与特征向量列 bank_eigen_cent 的核心差分在断连图行为 (本列对小分量给出有限分值, 后者置 NaN), 两列联合使用可以分离"全局声望"与"分量内声望"两层构念。进一步的实用口径有四点。其一, 量纲与横向比较: 分值经 L2 归一化且 alpha 逐年随谱半径变化, 跨年与跨规格比较系数时应先做 z-score 标准化再比较标准化 beta, 直接比较原始系数没有意义, 这与项目跨模型情感测度须标准化后再比较的口径同构。其二, 时序用法: 若担心当期网络位置与当期结果变量同受报道冲击驱动, 可自行取滞后一期进入回归, 网络溢出族的 emb 系测度已内置滞后先例可循。其三, 与二值指示列 bank_is_hub (度排名前一成) 的分工: 后者是粗粒度的枢纽哑变量, 适合做异质性切样, 本列是连续测度, 适合做梯度解释, 两者共用同一张年度图, 联合呈现能同时给出"是否枢纽"与"居中程度"两个层次。其四, 报告规范: 论文呈现本列结果时应同时脚注判据梯子两个严格臂的方向与显著性形态, 三臂完整披露是家族设计的初衷, 只报单臂等于放弃判据敏感性证据。

## VAR: bank_katz_cent_sent

【变体差分】
本列是严格同句判据臂 (criterion 为 sent, 内部实现为句窗半径取 0), 是三判据梯子中口径最严的一臂。精确差分: 与 canonical 同篇臂不同, 两家银行仅当其提及位置落在同一个句子内才贡献一条边; 对每个包含至少两家 both-verified 银行的 docid, 走组内文本重扫, 以 map_bank_sentence_positions 定位各银行在标题加正文中的句级位置 (prepend_title 口径, 标题记为第 0 句, 镜像 stage 13 的 match_in_title), 再由 bank_pairs_within_sentence_window 以半径 0 枚举同句银行对。银行识别与 stage 11 和 13 共用同一否定过滤与短名排除事实源, 禁裸 AC 自动机, 防"涉农行业"命中"农行"一类假阳性。节点全集与 canonical 臂完全一致 (同年幸存银行), 仅边集收紧, 因此本列与无后缀列的差异干净地归因于判据严格度。构念上, 同句共现近似要求记者在一个句法单元内把两家银行绑定表述 (对比、并购、合作、名单式列举), 是媒体感知中"强关联"的代理; 代价是边集大幅稀疏、连通分量碎裂, Katz 分值更多由基线项主导, 短面板开发环境下接近退化属预期而非缺陷。注意本列判据后缀 _sent 与三轨文本后缀 _ss (银行与金融科技同句) 是两个正交概念空间, 前者绑定的是银行与银行, 严禁混同; 判据原语与 _ss 轨的 extract_bank_fintech_cooccurrence 也是不同口径的两套原语, 生产代码禁互相复用。使用口径: 本臂与无后缀臂、_win1 臂互为稳健性、不分主次, 各自 just-identified 并排进入各自回归, 禁混进同一 over-identified Hansen J; 若结论仅在宽松臂成立而在本臂消失, 应报告并解释为共现口径敏感而非直接删臂。

## VAR: bank_katz_cent_win1

【变体差分】
本列是句窗判据臂 (criterion 为 win1), 严格度介于同篇 canonical 臂与同句 _sent 臂之间。精确差分: 两家银行的提及须落在正负 win_radius 句的窗口内才贡献一条边, 窗口半径读取 config/panel.yaml 下 network_criteria.win_radius, 默认 1, 即允许相邻句的跨句绑定; 该配置键与 stage 13 银行金融科技共现过滤的 filtering.yaml 下 cooccurrence_filter.sentence_radius 是两个不同的键, 互不联动, 排查口径时勿混。实现路径与 _sent 臂共用同一组内文本重扫机制: 按 docid 分组, map_bank_sentence_positions 定位句级位置 (标题为第 0 句, prepend_title 口径), bank_pairs_within_sentence_window 以半径 1 枚举窗口内银行对, 每篇每对加一与 canonical 臂同权; 银行识别同样复用否定过滤与短名排除事实源。构念定位: 中文财经报道常以相邻两句完成一组银行间的对照或承接叙述 (前句述甲行动作, 后句以"同样"或"相比之下"引出乙行), 严格同句判据会漏掉这类跨句强关联, 而同篇判据又会放进大量弱关联, 半径 1 的句窗正是针对这一叙事结构的折中口径, 与 ss 文本轨在银行金融科技侧采用句窗半径的设计动机同构但绑定对象不同 (本列绑定银行与银行)。判据后缀 _win1 与三轨文本后缀是正交概念空间, 本列不携带任何文本轨语义。使用口径与家族铁律一致: 本臂与无后缀臂、_sent 臂互为稳健性、不分主次, 三臂各自 just-identified 并排进入各自回归, 禁混进同一 over-identified Hansen J; 三臂系数沿严格度单调衰减或稳定不变都是可解释的形态, 应完整报告而非择优。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Huangfu, X. (2026). Board Networks and Corporate Transparency: How Independent Director Centrality Drives ESG Disclosure Quality. Corporate Social Responsibility and Environmental Management. https://doi.org/10.1002/csr.70661
Hughes, D. W. (2026). A jackknife bias correction for nonlinear network data models with fixed effects. Journal of Econometrics, 253, 106130. https://doi.org/10.1016/j.jeconom.2025.106130
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction?. The North American Journal of Economics and Finance, 73, 102163. https://doi.org/10.1016/j.najef.2024.102163
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691-2729. https://doi.org/10.1093/restud/rdae088
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. Communications Physics, 5(1), 76. https://doi.org/10.1038/s42005-022-00856-9
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. Journal of Human Resources, 50(2), 317-372. https://doi.org/10.3368/jhr.50.2.317
Boldi, P., & Vigna, S. (2014). Axioms for centrality. Internet Mathematics, 10(3-4), 222-262. https://doi.org/10.1080/15427951.2013.865686
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. Social Networks, 32(3), 245-251. https://doi.org/10.1016/j.socnet.2010.03.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Newman, M. E. J. (2005). A measure of betweenness centrality based on random walks. Social Networks, 27(1), 39-54. https://doi.org/10.1016/j.socnet.2004.11.009
Estrada, E., & Rodríguez-Velázquez, J. A. (2005). Subgraph centrality in complex networks. Physical Review E, 71(5), 056103. https://doi.org/10.1103/PhysRevE.71.056103
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. Proceedings of the National Academy of Sciences, 101(11), 3747-3752. https://doi.org/10.1073/pnas.0400087101
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Faust, K. (1997). Centrality in affiliation networks. Social Networks, 19(2), 157-191. https://doi.org/10.1016/S0378-8733(96)00300-0
Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. Social Networks, 19(3), 243-269. https://doi.org/10.1016/S0378-8733(96)00301-2
Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. Social Networks, 30(1), 31-48. https://doi.org/10.1016/j.socnet.2007.04.006
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287. https://doi.org/10.1016/0378-8733(83)90028-X
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Hirshleifer, D., Peng, L., & Wang, Q. (2024). News Diffusion in Social Networks and Stock Market Reactions. The Review of Financial Studies. https://doi.org/10.1093/rfs/hhae025
Gomes, A., Gopalan, R., Leary, M. T., & Marcet, F. (2024). Analyst Coverage Networks and Corporate Financial Policies. Management Science. https://doi.org/10.1287/mnsc.2023.4891
Fang, Y., Lin, H., & Lu, L. (2025). Measuring systemic risk from textual Analysis: Evidence from Chinese Banks. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2025.104355
Wang, P., & Borjigin, S. (2026). Bank systemic risk prediction based on text mining and explainable machine learning. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2025.102577
<!-- rendered-citations:end -->
