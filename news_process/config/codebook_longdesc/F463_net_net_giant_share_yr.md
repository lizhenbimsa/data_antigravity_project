---
family_id: F463
columns:
- net_giant_share_yr
- net_giant_share_yr_sent
- net_giant_share_yr_win1
unit: 比率/占比 (proportion, 无量纲, 取值域 [0,1]; 巨片节点数占年度网络节点总数之比)
formula: "net_giant_share_yr = |V(LCC_t)| / |V_t|; LCC_t = 年度银行共现网络 G_t 的最大连通分量, V_t = 年度出现的银行节点全集; 判据变体 {同篇(无后缀)/±1句窗(_win1)/严格同句(_sent)} 决定 G_t 的建边口径"
producer: news_process/pipeline/panel/network_spillover.py::_net_level_extra_metrics (私有助手, 第 911-912 行 len(lcc_nodes)/n_nodes; 经公开入口 compute_bank_network_centrality 分判据物化); news_process/pipeline/panel/export.py (Stata 标签)
upstream:
- 13_cooccurrence_filter.parquet (banks∧banks 共现文章集, 建边原料)
- 14_materialize_ctx.parquet (content_full, prepend_title 后的判据扫描文本)
- 40_panel_yearly.parquet (bank-year 面板骨架)
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
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: 103223
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: 2693
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
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
  title: "Collective dynamics of small-world networks"
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
- doi: "10.1016/j.isci.2024.110474"
  title: "Assessing interconnectedness and systemic importance of Chinese financial institutions"
  authors: "Liu, Z., Wang, L., Huang, C., & Yang, B."
  year: 2024
  venue: "iScience"
  type: "journal"
  one_sentence_zh: "该文以中国金融机构为样本构建关联网络并评估其系统重要性,与本家族用银行共现网络巨片占比刻画中国银行业连通结构的思路直接呼应,为中国语境下的网络连通度测度提供最新经验参照。"
- doi: "10.1007/s10479-024-06163-6"
  title: "Corporate ESG performance and systemic risk: a network perspective"
  authors: "Wang, G.-J., Lin, X., Zhu, Y., Xie, C., & Uddin, G. S."
  year: 2024
  venue: "Annals of Operations Research"
  type: "journal"
  one_sentence_zh: "该文以网络视角刻画企业ESG表现与系统性风险的关联结构,与本家族用共现网络连通拓扑刻画银行业系统性舆情外溢的方法论同源,为网络连通度指标的经济含义提供最新经验支撑。"
new_dois:
  - "10.1016/j.procs.2023.08.056"
  - "10.1016/j.isci.2024.110474"
  - "10.1007/s10479-024-06163-6"
---

## CORE

【构念与来源】
本家族刻画的是每一年度银行共现网络的巨片占比 (annual giant component share), 即在把所有银行按"是否在新闻报道中被邻近共同提及"连成的年度无向图 G_t 上, 落入最大连通分量 (largest connected component, 简称 LCC 或巨片) 的银行节点数占该年出现过的银行节点总数的比例。它是一个网络级 (network-level)、逐年广播 (year-broadcast) 的标量: 同一年内所有银行共享同一个数值, 用来概括"这一年媒体话语把中国银行业整合成一张多大的连通拼图"。当巨片占比接近 1 时, 绝大多数银行都被同一条媒体叙事链条串在一起, 任一家银行的负面舆情原则上都有话语路径蔓延到其余大多数同业; 当巨片占比偏低时, 银行业在媒体话语层面呈碎片化, 分裂成若干互不连通的小簇, 舆情外溢被结构性地隔断在局部。构念来源上, 巨片占比是渗流理论 (percolation) 与随机图连通性研究中最基础的宏观序参量之一: Watts 与 Strogatz (1998) 在小世界网络的经典工作中即以巨片的涌现刻画系统从局域耦合走向全局连通的相变, 而 Clauset、Newman 与 Moore (2004) 在超大规模网络的社区探测中同样把连通分量结构作为拆解网络的第一层骨架。本项目把这一物理与社会网络的成熟测度移植到"银行—银行媒体共现网络", 用以为银行业系统性舆情连通度提供一个可跨年比较的单一维度。

【方法学与计算】
计算链路分三步。第一步是建边: 对给定年度 t, 遍历该年通过 stage 13 共现硬过滤的报道, 把在同一篇报道 (或按更严判据在同一句窗 / 同一句) 内被同时提及的每一对银行连上一条无向边。银行的识别沿用与 stage 11/13 同一套否定 + 短名排除事实源 (禁裸 Aho-Corasick 匹配, 例如防"涉农行业"误触发"农行"), 判据原语为 core/text/entity_context.map_bank_sentence_positions 与 bank_pairs_within_sentence_window, 扫描文本是 prepend_title 后的 content_full (标题占第 0 句), 审计脚本与生产共用同一原语以保证审计即生产。第二步是构图: 以该年出现的银行为节点集 V_t, 上述银行对为边集, 用 networkx 建成年度无向图 G_t。第三步是取巨片: 枚举 G_t 的全部连通分量, 取节点数最大者为 LCC, 巨片占比 = |V(LCC_t)| / |V_t| (源码 out['net_giant_share_yr'] = len(lcc_nodes) / n_nodes; n_nodes 为零时置 NaN)。取值域严格落在 [0,1], 单调地随共现网络的连通程度上升。需要强调的是, 巨片占比只数节点、不计边权, 因此它对"谁和谁被一起报道过至少一次"敏感, 而对共现频次的强弱不敏感 — 这与同族的加权中心度指标 (如 bank_strength_cent) 形成互补: 后者刻画连接强度, 前者刻画连通拓扑的整体轮廓。与巨片占比配套产出的 net_n_components_yr (连通分量数) 复用同一枚举结果, 二者共同描述"网络碎成了几块、最大一块有多大"。计算的确定性与稳定性也值得交代: 巨片占比只涉及整数计数 (节点数、分量大小) 与一次整数除法, 不经过任何迭代求解器或 BLAS 浮点线性代数, 因此它是一个逐位可复现的量, 不像同族的 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 那样受浮点非确定性影响 — 本族三条巨片占比列均不在已知 BLAS 非确定网络列清单 (那 9 列 = 上述 3 基名 × 三判据) 之内, 故 golden 复现无需对本族任何一列做 drop 排除。边的建立不计重: 无论两家银行在一年内被同框多少次, 在无权图 G_t 上都只体现为存在一条边 (0/1), 这使巨片占比对共现频次强度完全不敏感, 而只对"是否至少共现过一次"敏感 — 这一二值化恰是它与加权强度类指标分工的技术根源。用大白话说: 巨片占比回答的是"把所有银行按'有没有被一起报道过'牵手连成一片, 最大的那一片圈住了几成银行", 它不管牵手牵得多紧, 只管有没有牵上。

【数据来源与上游依赖】
建边原料来自 stage 13 共现硬过滤后的报道集 (13_cooccurrence_filter.parquet), 判据扫描的文本是 stage 14 物化的 content_full (标题 prepend 后, 标题占第 0 句), 银行节点的宇宙与年份骨架来自 40_panel_yearly.parquet 的 bank-year 面板。须特别澄清与留篇门控的关系: 本项目自 2026-06-29 起统一为 full-only 门控 — 一篇报道是否被判为"银行金科报道"、是否计入 n_articles, 只看 llm_verified_full == True; ctx / ss 降为 conditional-on-full 的测度轨。但巨片占比的建边判据 (article / win1 / sent) 属于银行∧银行共现的网络构造判据敏感性空间, 与银行∧金科情感文本的 full/ctx/ss 三轨是两套正交概念空间: 前者调"两家银行邻近到什么尺度才算共现", 后者调"情感取材于全文还是实体窗还是同句"。二者不共享后缀语义、不联动、更严禁混入同一 over-identified Hansen J。这一正交性是理解本家族三个判据变体的前提, 也是全篇反复申明的口径铁律。

【文献定位】
在文献谱系上, 巨片占比属于"以网络结构度量刻画金融系统连通性与传染风险"的一支。Jackson 与 Pernoud (2021) 对金融网络系统性风险的综述指出, 机构间的连通拓扑是决定冲击能否从局部放大为系统性事件的一阶结构条件, 而巨片的规模正是这一连通性最粗粒度的概括量。Duarte 与 Eisenbach (2021) 在火线抛售外溢的研究中同样表明, 溢出的广度取决于资产负债关联网络的连通结构。Wang、Zhang 与 Yang (2020) 对中国担保网络在金融危机与刺激计划下演化的研究尤具参照价值: 他们直接以巨片的形成、膨胀与瓦解刻画中国式关联网络在宏观冲击下的相变, 与本家族"以媒体共现巨片刻画银行业话语连通度"在方法论上同源。相较之下, 本项目的网络不是真实的资产负债或担保敞口网络, 而是媒体话语的共现投影 — 这一区别对识别与解释都至关重要 (详见识别策略定位)。Li 等 (2026) 从文本风险披露中提取金融网络结构与连通性的工作, 与本项目"从新闻文本重建银行网络"共享同一测量哲学: 网络关系并非直接观测, 而是从非结构化文本的共现信号中重建。就"网络结构度量是否携带经济含义"这一元问题, Nezami、Chisam 与 Palmatier (2025) 对网络中心度与企业绩效关系的元分析提供了跨领域的效应量证据, Yu、Hu 与 Zhong (2024) 则在资产定价语境下论证网络中心度经由信息扩散影响价格, Gao、Ru 与 Yang (2022) 揭示了银行贷款中所有权网络的信息角色 — 三者共同支撑"银行业连通拓扑是有定价与信息含义的经济对象", 从而为巨片占比作为一个宏观连通性控制变量或稳健性维度提供构念合法性。就"从文本共现重建的网络与真实关联网络的关系"这一测量效度问题, 需要与真实敞口网络的研究并置理解: Wang、Zhang 与 Yang (2020) 观测的是有真实法律效力的担保合约网络, Gao、Ru 与 Yang (2022) 观测的是股权所有权网络, 而本项目的银行共现网络是媒体话语的共现投影, 二者在语义上并不等同 — 媒体共现巨片的膨胀既可能反映真实业务关联的加深, 也可能只是新闻生产把多家银行编织进同一叙事的产物。因此在解释巨片占比的年际变动时, 必须把"话语连通"与"实质连通"审慎区分, 不能简单地把媒体巨片占比读作系统性风险敞口的连通度。这一测量效度的诚实边界, 正是本家族区别于以真实敞口建网的系统性风险文献的关键处, 也是它只能作为描述 / 稳健性维度、而非因果处理项使用的深层理由之一。Liu、Wang、Huang 与 Yang (2024, iScience) 以中国金融机构为样本构建关联网络并评估其系统重要性, 与本家族用银行共现网络巨片占比刻画中国银行业连通结构的思路直接呼应, 为中国语境下的网络连通度测度提供最新经验参照。Wang、Lin、Zhu、Xie 与 Uddin (2024, Annals of Operations Research) 以网络视角刻画企业ESG表现与系统性风险的关联结构, 与本家族用共现网络连通拓扑刻画银行业系统性舆情外溢的方法论同源, 为网络连通度指标的经济含义提供最新经验支撑。
【识别策略定位】
巨片占比在本项目中的计量地位必须诚实界定为网络级、逐年广播的描述性 / 稳健性维度, 而非可在双向固定效应下识别的处理变量。因为它对全年所有银行取同一数值, 在包含年度固定效应 (year FE) 的回归中它与年份哑变量完全共线, 会被吸收 — 这与同族的 net_modularity_yr、net_assortativity_yr 的"year-FE absorbed"处境完全一致 (见 export.py Stata 标签)。因此它的正确用法是: 进入不含年 FE 的时间序列 / 跨年描述, 或作为刻画"网络年度厚度"的宏观协变量, 而绝不能被误当作银行层面的内生处理项塞进带年 FE 的面板回归充数。更深一层, 即便在可识别的设定里使用由共现网络导出的同业效应, 也必须正视 Manski 式反射问题与网络内生性: Bramoullé、Djebbari 与 Fortin (2009) 证明了在社会网络中借助网络拓扑 (尤其是二阶及以上邻居) 分离内生同群效应与外生情境效应的条件, 其 2020 年的综述 (Bramoullé, Djebbari, & Fortin, 2020) 进一步系统化了网络同群识别的前提与陷阱; Grieser、Hadlock、LeSage 与 Zekhnini (2022) 则在公司金融政策的网络效应中示范了空间自回归式的识别处理。本项目引用这些工作意在申明: 巨片占比作为一个纯拓扑描述量本身不承担因果识别, 一旦下游要把网络连通性用于同业外溢的因果推断, 反射问题、同时性与网络构造内生性都需另行处理, 不能因为有了一张网络就默认识别成立。

【与相邻测度的构念区分】
巨片占比须与家族外若干形近测度严格区分, 避免语义混淆。其一, 它与节点级中心度 (bank_degree_cent、bank_eigen_cent 等, 见 Freeman 1978 的中心度概念澄清) 不同层级: 中心度刻画单家银行在网络中的相对地位, 逐银行取值; 巨片占比刻画整张网络的宏观连通轮廓, 逐年取值。其二, 它与 net_density_yr (网络密度 = 实际边数 / 可能边数) 不同构念: 密度衡量连边的稠密程度, 一张密度很低的网络仍可能因存在一条贯穿全局的稀疏骨架而拥有很高的巨片占比; 反之高密度的若干孤立小团也可能巨片占比不高。其三, 它与 net_n_components_yr 是同一枚举结果的两个侧面, 但一个只数"最大块多大", 一个只数"共分几块", 二者并非彼此的单调变换 (例如两块各占一半 vs 一大块 + 众多孤立点, 分量数可相同而巨片占比迥异), 故并列而非替代。最关键的口径区分在于判据后缀 ≠ 三轨文本后缀: 巨片占比的三个判据变体 (无后缀 / _win1 / _sent) 调的是"银行∧银行共现"的邻近尺度, 属网络构造判据敏感性的正交概念空间; 而项目主线的 full/ctx/ss 三轨调的是"银行∧金科"情感文本的取材范围, 两者是两套互不联动的概念空间 (win_radius 取 config/panel.yaml::network_criteria.win_radius, 与 filtering.yaml::cooccurrence_filter.sentence_radius 是不同键)。二者禁止混入同一 over-identified Hansen J。

【已知局限与稳健性梯子】
巨片占比的首要局限来自媒体共现网络本身的测量性质: 它是"被一起报道"的投影, 会受媒体注意力周期、大事件同框报道 (如监管新政点名多家银行) 的机械抬升影响, 因而巨片占比的年际波动可能反映的是新闻生产而非真实业务关联 — 这一点在把它当宏观连通度解读时须保守。其次, 在本机 T=2 的开发语料上, 网络年度极浅, 巨片占比的方差被压缩, 稳健性梯子的判据分轨在如此小样本上可能退化 (甚至趋同), 属预期现象; 生产 T=18 规模下判据敏感性才充分展开。稳健性梯子的组织原则是: 无后缀 (同篇)、_win1 (±1 句窗)、_sent (严格同句) 三个判据变体各自 just-identified 并排, 互为稳健性、不分主次, 检验主结论不被"邻近共现定义得多宽"这一取值驱动。判据由宽到严, 建边越来越苛刻, 网络越来越稀疏, 巨片占比通常单调收缩: 同篇口径把一篇长报道里所有被提及银行两两连边, 最宽松; 严格同句口径只承认真正落在同一句话里的银行对, 最保守, 更接近"实质关联"而非"版面同框"。铁律: 三判据严禁混进同一 over-identified Hansen J (镜像三轨 / co-primary 嵌入 / 政治词权重 / 词典消融梯度的同一并排口径)。此外须注意本族三条巨片占比列不在已知 BLAS 浮点非确定网络列清单内 (那 9 列为 bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的三判据变体), 故 golden 复现无需对本族做 drop 排除。

【指标的经济读法与用途边界】
就巨片占比在实证中怎么用、能用来说明什么, 有必要给出白话与术语并陈的边界。白话版: 巨片占比像是给"这一年银行业在新闻里彼此挨得有多近"拍了一张全景照, 数字越接近满格 (1), 说明媒体几乎把所有银行编进了同一张关系图, 任何一家出事都更容易在话语上牵连一大片; 数字越低, 说明银行们在新闻叙事里各过各的, 舆情更被隔在小圈子里。术语版: 它是一个宏观连通度序参量, 适合刻画银行业媒体网络的"年度厚度", 可作横截面之上叠加的时间趋势变量, 或在异质性分析中用来切分"高连通年 vs 低连通年"的子样本。但用途有硬边界: 其一, 由于逐年广播、与年 FE 共线, 它绝不能进入含年固定效应的银行层面回归当处理项 (会被吸收, 塞进去等于什么都没加还制造共线); 其二, 它是无权二值拓扑量, 不承载连接强度信息, 若研究关心的是关联的紧密而非可达, 应改用加权指标; 其三, 它是媒体共现投影而非真实敞口, 因果解读须格外克制。就"网络结构度量的经济含义是否可信"这一背景问题, Yu、Hu 与 Zhong (2024) 与 Nezami、Chisam 与 Palmatier (2025) 提供了跨市场、跨领域的证据, 说明网络位置确实经由信息扩散渠道进入定价与绩效, 但这些证据针对的是节点级中心度而非网络级巨片占比, 移植到本指标时须留意层级差异 — 这也是本家族在文献定位与构念区分两节反复强调"层级不可混淆"的原因。

巨片占比的另一层用途在于为下游的同业外溢分析提供网络厚度的背景刻度。当研究者用共现网络导出的权重矩阵 W 构造同业情感外溢 (peer tone spillover) 时, 一个几乎不连通、巨片占比很低的年份意味着 W 高度稀疏、外溢路径稀少, 此时同业效应的估计天然更噪、更局部; 反之高巨片占比的年份 W 稠密, 外溢渠道通畅。因此巨片占比可作为解读同业外溢估计稳定性的旁证维度。但须再次强调 Bramoullé、Djebbari 与 Fortin (2009, 2020) 与 Grieser、Hadlock、LeSage 与 Zekhnini (2022) 的告诫: 有网络不等于识别成立, 反射问题、同时性与网络构造内生性都需在外溢回归里另行处理, 巨片占比本身只描述连通厚度, 不为任何因果主张背书。归纳而言, 本指标是一个语义清晰、计算确定、可跨年比较的宏观拓扑序参量: 它以最粗的粒度回答"这一年媒体话语把银行业整合成多大一张连通拼图", 在方法论上直承渗流与随机图连通性的经典传统 (Watts 与 Strogatz 1998; Clauset、Newman 与 Moore 2004), 在金融应用上呼应以连通结构刻画系统性风险与关联演化的文献 (Jackson 与 Pernoud 2021; Wang、Zhang 与 Yang 2020; Li 等 2026), 但其媒体共现投影的测量性质与逐年广播的统计性质共同界定了它只能作描述与稳健性维度、不可充作识别处理项的用途边界。三判据变体则把"邻近共现定义得多宽"这一研究者选择显式暴露为并排的稳健性梯子, 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: net_giant_share_yr

【变体差分】
本列是家族 canonical (无判据后缀), tier=core, 也是 NETWORK_METRIC_BASES 这一 33 结构指标基名 SSOT 中巨片占比的唯一无后缀成员, 采用现行生产口径的"同篇 (article) 判据": 只要两家银行在同一篇经 stage 13 共现硬过滤保留的报道内被共同提及 (银行∧银行, 走否定 + 短名排除事实源, 扫描 prepend_title 后的 content_full), 即在该年度无向图 G_t 上连一条边; 随后取最大连通分量节点数除以该年出现的银行节点总数 (源码 len(lcc_nodes) / n_nodes, n_nodes 为零置 NaN), 得到落在 [0,1] 的巨片占比。之所以以同篇为无后缀 canonical, 是因为它是本项目历史现行口径 (与 stage 13 硬过滤的 match_in_title 全篇匹配语义衔接), 而非因为它在方法学上比 _win1 / _sent 更"主" — 三判据在识别地位上完全对等, 无后缀只是历史命名产物。作为一个逐年广播标量, 本列同一年内所有银行取值相同, 在含年 FE 的回归中与年份哑变量共线而被吸收 (与 net_modularity_yr / net_assortativity_yr 同处境), 故其正当用法是不含年 FE 的跨年描述或作为刻画"该年媒体共现网络把银行业整合成多大一张连通拼图"的宏观协变量, 严禁当作银行层面处理项塞进带年 FE 的面板充数。相对两个更严判据的稳健性臂, 本列因建边最宽松, 巨片占比通常取三者中最高值: 同篇口径把一篇报道里同框出现的所有银行一律两两连边, 因而更容易把散落的小簇经由若干"多家银行同框"的枢纽报道缝合进同一个巨片。这一敏感性正是它区别于 _win1 / _sent 的核心: 三者仅在"邻近共现定义得多宽"上分岔, 其余计算 (取 LCC、除以节点总数、NaN 守卫、年广播语义) 逐字节一致。它与无后缀同篇判据下的 net_n_components_yr 共享同一次连通分量枚举, 二者一个数"最大块多大"、一个数"共几块", 并列而非替代。进一步就本列的解读须提醒三点。其一, 它对共现频次强度不敏感: 无论一对银行在一年内被同框报道一次还是上百次, 在无权图 G_t 上都只是一条边 (0/1), 因此本列衡量的是连通拓扑的可达性而非关联的紧密程度, 与加权强度类指标 (bank_strength_cent) 分工互补, 不可相互替代。其二, 它是逐位可复现的确定性量: 只涉及整数计数与一次整数除法, 不经迭代求解器或 BLAS 浮点线性代数, 故不落入本项目已知 BLAS 非确定网络列清单 (bank_clustering / bank_cfbetween_cent / bank_harmonic_cent 的三判据变体那 9 列), golden 复现无需对本列 drop 排除。其三, 用大白话说, 本列同篇口径下回答的是"这一年只要两家银行在同一篇新闻里被一起点过名就算它们牵手, 那么牵成的最大一片圈住了全部银行的几成"; 因为牵手门槛最低 (整篇同框即可), 它比句窗、同句两个更严的臂更容易把零散小簇经由"多家银行同框"的枢纽报道缝合进同一巨片, 所以读数通常也最高。它与无后缀同篇判据下的 net_n_components_yr 共享同一次连通分量枚举: 一个报告最大块的相对大小, 一个报告总共碎成几块, 二者非彼此的单调变换, 故并列产出而非择一。铁律: 本列与其 _win1 / _sent 变体各自 just-identified 并排、互为稳健性不分主次, 严禁三判据混进同一 over-identified Hansen J。就本列作为 canonical 在下游被消费的方式再作一层界定: 因它是 NETWORK_METRIC_BASES 中巨片占比唯一的无后缀成员, stata_export.py 的机械标签块会以本列为基名派生出 Stata 变量注释, 三判据变体的标签由同一模板套印后缀, 故本列的语义定义即三变体共享的语义骨架 — 这也是把"同篇"选为无后缀基名的工程理由 (历史现行口径优先), 与方法学上何者更"主"无关。作为宏观连通度序参量, 本列在解读上最容易被误用之处有二: 一是把它逐年广播的高读数误读为"某家银行连通性强", 实则它不含任何银行截面信息, 只描述整张年度网络的连通拓扑轮廓; 二是把同篇口径下偏高的巨片占比读作真实业务关联的紧密, 实则同篇建边最宽松, 一篇点名多家银行的监管综述即可把大量本无实质关联的银行缝进同一巨片, 故本列的高读数更应理解为"版面同框的连通可达"而非"实质关联的连通"。两个更严判据 (_win1 / _sent) 正是为剥离这层版面同框噪声而并排设置的稳健性臂, 若三判据读数一致方可判定主结论不由邻近共现的宽窄定义驱动。

## VAR: net_giant_share_yr_sent

【变体差分】
本列 tier=standard, 是巨片占比的严格同句 (_sent) 判据变体: 与 canonical 唯一的差别在于建边口径最为苛刻 — 只有当两家银行真正落在同一个句子之内被共同提及时才连边, 版面同框但分属不同句子的银行对一律不连。其余计算流程 (以 networkx 建年度无向图、枚举连通分量取最大者、巨片占比 = LCC 节点数 / 该年银行节点总数、n_nodes 为零置 NaN、逐年广播因而在含年 FE 回归中被吸收) 与 canonical 逐字节一致, 判据切换经 compute_bank_network_centrality 的 criterion='sent' 分轨物化, 判据原语为 map_bank_sentence_positions 与 bank_pairs_within_sentence_window, win_radius 参数在同句口径下收紧到 0。因为建边最严, 本列的网络最稀疏, 巨片占比在三判据中通常取最低值, 也最接近"实质关联"而非"报道同框"的语义: 落在同一句话里的两家银行, 更可能是被记者放在同一断言下真实并置 (如"工行与建行同步下调利率"), 而非仅仅在一篇综述里先后被点名。因此本列是检验"主结论是否被把共现定义放宽到全篇所致"这一稳健性问题最保守的一臂。判据后缀 _sent 调的是银行∧银行的邻近尺度, 与项目主线 full/ctx/ss 三轨 (银行∧金科的情感文本取材) 是两个正交概念空间, 互不联动, 不可混淆。铁律: 本列与 canonical (同篇) 及 _win1 (句窗) 各自 just-identified 并排、互为稳健性不分主次, 严禁三判据混进同一 over-identified Hansen J。在本机 T=2 开发语料上, 严格同句判据把已经很浅的网络进一步稀疏化, 本列方差可能极度压缩甚至趋于退化, 属预期现象, 生产 T=18 规模下才充分展开。

## VAR: net_giant_share_yr_win1

【变体差分】
本列 tier=standard, 是巨片占比的 ±1 句窗 (_win1) 判据变体, 邻近尺度居于 canonical (同篇) 与 _sent (严格同句) 之间: 当两家银行落在彼此 ±1 句的窗口内 (即同句或相邻一句) 被共同提及时连边, 比严格同句宽松 (允许跨相邻句的并置), 又比全篇同框苛刻 (排除长报道里相隔多句的银行对)。其余计算流程 (networkx 建年度无向图、取最大连通分量、巨片占比 = LCC 节点数 / 该年银行节点总数、NaN 守卫、逐年广播因而在含年 FE 回归中被吸收) 与 canonical 逐字节一致, 判据切换经 compute_bank_network_centrality 的 criterion='win1' 物化, win_radius 取 config/panel.yaml::network_criteria.win_radius (默认 1) — 须再次强调该键与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科口径) 是不同键, 互不联动, 改一个不牵动另一个。作为中间尺度, 本列的巨片占比通常介于同篇与严格同句两个端点之间, 其价值在于提供一条"局部邻近但不必严格同句"的连通度读数, 检验主结论是否对邻近窗口的具体取值稳健 — 若同篇、±1 句窗、严格同句三个读数下结论一致, 则可判定结果不由"共现定义得多宽"这一研究者选择驱动。判据后缀 _win1 属网络构造判据敏感性空间, 与 full/ctx/ss 三轨文本后缀是正交的两套概念, 禁止混为一谈。铁律: 本列与 canonical 及 _sent 各自 just-identified 并排、互为稳健性不分主次, 严禁三判据混进同一 over-identified Hansen J。同 canonical 与 _sent, 本列在含年固定效应设定中与年份哑变量共线被吸收, 正确用法为不含年 FE 的跨年描述或宏观连通度协变量, 不得充作银行层面处理项。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. Physical Review E, 70(6), 27721. https://doi.org/10.1103/PhysRevE.70.066111
Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of small-world networks. Nature, 393(6684), 440-442. https://doi.org/10.1038/30918
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Liu, Z., Wang, L., Huang, C., & Yang, B. (2024). Assessing interconnectedness and systemic importance of Chinese financial institutions. iScience. https://doi.org/10.1016/j.isci.2024.110474
Wang, G.-J., Lin, X., Zhu, Y., Xie, C., & Uddin, G. S. (2024). Corporate ESG performance and systemic risk: a network perspective. Annals of Operations Research. https://doi.org/10.1007/s10479-024-06163-6
<!-- rendered-citations:end -->
