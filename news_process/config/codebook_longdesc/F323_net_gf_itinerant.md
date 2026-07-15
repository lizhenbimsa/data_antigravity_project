---
family_id: F323
columns:
- gf_itinerant
- gf_itinerant_sent
- gf_itinerant_win1
unit: 非负整数 2-path 计数 (float64 落盘, 无量纲; 缺分组时 NaN)
formula: "gf_itinerant(i) = #{ {a,c} ⊆ N(i) : (a,c) ∉ E, g(a) = g(c) ≠ g(i) } — 年度银行共现无向图 (networkx) 上, 端点不直连且端点同群、经纪人异群的 2-path 唯一计数 (Gould-Fernandez 1989 巡回经纪角色, 无向坍缩口径); 判据变体 {同篇 canonical 无后缀 / ±1 句窗 _win1 / 严格同句 _sent}"
producer: news_process/pipeline/panel/network_spillover.py::_gould_fernandez_roles (经 compute_bank_network_centrality 逐年调用; 判据落列于 runner 步骤 7g/7g_win1/7g_sent)
upstream:
- "df_exploded 篇章级展开帧 (docid × target_bank, both-verified; 面板构建期内存对象, 源自 stage 21 留篇门控后的文章-银行展开)"
- "build_adjacency_matrix 年度邻接矩阵 (criterion ∈ {article, win1, sent})"
- "pipeline/panel/iv_did.py::load_bank_group_maps (银行所有制类型分组 SSOT)"
- "config/panel.yaml::network_criteria.win_radius (仅 _win1 判据消费, 默认 1)"
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: "10.1007/s10490-026-10116-x"
  type: "journal"
  authors: "Wang, Y., & Wei, F."
  year: 2026
  title: "Agentic, powerful, but unethical: New ventures' ethical practices as the outcome of entrepreneurs' networking behaviors and structural holes"
  venue: "Asia Pacific Journal of Management"
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
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: "Network centrality, information diffusion and asset pricing"
  venue: International Review of Financial Analysis
  vol: 93
  pages_or_artno: "103223"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1371/journal.pone.0274475
  type: journal
  authors: Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S.
  year: 2022
  title: "A weighted and normalized Gould-Fernandez brokerage measure"
  venue: PLOS ONE
  vol: 17
  issue: 9
  pages_or_artno: e0274475
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1017/S0022109021000788
  type: journal
  authors: Gao, H., Ru, H., & Yang, X.
  year: 2022
  title: "The informational role of ownership networks in bank lending"
  venue: Journal of Financial and Quantitative Analysis
  vol: 57
  issue: 8
  pages_or_artno: 2993-3017
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
- doi: 10.1038/s41467-020-16535-8
  type: journal
  authors: Wang, Y., Zhang, Q., & Yang, X.
  year: 2020
  title: "Evolution of the Chinese guarantee network under financial crisis and stimulus program"
  venue: Nature Communications
  vol: 11
  pages_or_artno: "2693"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1086/421787
  type: journal
  authors: Burt, R. S.
  year: 2004
  title: "Structural holes and good ideas"
  venue: American Journal of Sociology
  vol: 110
  issue: 2
  pages_or_artno: 349-399
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.2307/270949
  type: journal
  authors: Gould, R. V., & Fernandez, R. M.
  year: 1989
  title: "Structures of mediation: A formal approach to brokerage in transaction networks"
  venue: Sociological Methodology
  vol: 19
  pages_or_artno: 89-126
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: "10.1111/acfi.13091"
  title: "How do co-shareholding networks affect negative media coverage? Evidence from China"
  authors: "Wang, L., Hou, W., & Liu, Y."
  year: 2023
  venue: "Accounting & Finance"
  type: "journal"
- doi: "10.1287/mnsc.2023.4891"
  title: "Analyst Coverage Networks and Corporate Financial Policies"
  authors: "Gomes, A. R., Gopalan, R., Leary, M. T., & Marcet, F."
  year: 2024
  venue: "Management Science"
  type: "journal"
- doi: "10.1016/j.irfa.2023.102701"
  title: "Brokers in beneficial ownership: A network approach"
  authors: "Kostaris, K., & Andrikopoulos, A."
  year: 2023
  venue: "International Review of Financial Analysis"
  type: "journal"
new_dois:
- "10.3390/bdcc9100263"
- "10.1007/s10490-026-10116-x"
- "10.1111/acfi.13091"
- "10.1287/mnsc.2023.4891"
- "10.1016/j.irfa.2023.102701"
---

## CORE

该文研究新创企业创业者的网络拓展/加深行为与结构洞位置如何共同影响企业伦理实践, 为经纪/结构洞构念在企业行为结果上的应用提供了2026年最新实证证据。

【构念与来源】
本家族测量目标银行在年度银行新闻共现网络中扮演的巡回经纪 (itinerant brokerage) 角色强度, 构念直接取自 Gould & Fernandez (1989) 在交易网络上提出的形式化经纪角色分解框架。该框架的核心洞见是: 经纪不是一个同质的结构位置, 而应按经纪人与被中介双方的群归属关系细分为若干在社会学含义上截然不同的角色。给定一条二步路径, 即甲方经由中间人到达丙方且甲丙之间没有直接连边, 按甲方、中间人、丙方三者所属群体的异同组合, 原始有向框架区分出协调人、巡回经纪人、守门人、代表人、联络人五种角色。其中巡回经纪人 (itinerant broker) 的定义是: 被中介的两端属于同一群体, 而中间人自己属于另一个群体, 即中间人以外部人身份中介了某个群体的内部交往。Gould & Fernandez (1989) 用行商与巡回法官作类比, 强调这类经纪的独特张力在于经纪人不享有被中介群体的成员身份, 其中介地位既可能来自专业化优势, 也可能来自该群体内部关系的结构性断裂。在本项目语境下, 群体按银行所有制类型划分 (国有大行、股份制、城商、农商农信、民营、外资及其他), 巡回经纪计数高的银行意味着: 在中文财经媒体的报道叙事中, 它频繁地与两家同类型但彼此不直接共现的其他类型银行同时出现, 换句话说, 媒体在讲述某一类银行的故事时反复把这家异类银行放在中间位置。白话版: 想象两家城商行从不同时出现在同一批新闻里, 但它们各自都经常与某家股份制银行一起被报道, 那么这家股份制银行就在这两家城商行之间充当了信息意义上的巡回经纪人; 本变量数的就是一家银行在一年里充当这种中间人的次数。这一构念之所以值得单独测量, 是因为大量文献表明经纪位置承载着与单纯中心度不同的信息与资源含义: Burt (2004) 证明跨越结构洞的经纪位置与好想法的产生系统相关; Han, Kim & Nanda (2024) 在机构经纪网络中发现经纪结构影响流动性供给; Nezami, Chisam & Palmatier (2025) 的元分析确认网络中心地位与企业绩效存在稳定但异质的关联, 并强调不同中心度构念不可互相替代。媒体共现网络作为这些构念的文本代理, 其效度前提由 Li et al. (2026) 一类基于文本披露还原金融网络结构的研究提供: 文本共提及网络能够恢复真实金融关联的关键拓扑特征。中国场景下, You, Zhang & Zhang (2018) 证明中文媒体报道的强度与倾向受制度性力量塑造, Fang et al. (2024) 进一步证明媒体情绪经由存款稳定性通道影响中国银行系统性风险, 这两点共同意味着中国银行间的媒体共现结构既有信息含量、又非随机噪声, 适合作为银行在公共信息空间中结构位置的测度基底。

【方法学与计算】
计算分三层: 建网、分组、数角色。第一层建网: 生产函数 compute_bank_network_centrality (pipeline/panel/network_spillover.py) 逐年调用 build_adjacency_matrix, 在篇章级展开帧 df_exploded 上按 docid 聚合, 取每篇文章内全部通过验证的目标银行集合, 对集合内每个无序银行对在对称邻接矩阵上各加一, 得到该年度的加权无向共现图; 这一 docid 聚合口径是 2026 年 6 月审计修复后的统一口径, 消除了旧实现中同篇文章双行重复计数与幻影边 (验证未通过的银行经 co_mentioned_banks 字段混入) 两类污染, 保证入网节点全部是 both-verified 银行。留篇的上游宇宙与 full-only 留篇门控口径 (2026-06-29) 一致: 是否算一篇银行金科报道只看 full 轨验证结果, 展开帧即在该门控之后生成。第二层分组: 巡回经纪的判定需要每个节点的群标签, 生产代码复用既有 SSOT 加载器 load_bank_group_maps (pipeline/panel/iv_did.py) 的银行类型映射, 将银行归入国有、股份、城商、农商、民营、外资、其他等所有制类型群; 分组是年不变的银行属性, 加载失败时全部 gf 列优雅置 NaN 而非报错。第三层数角色: 叶函数 _gould_fernandez_roles 对图中每个有分组的节点 i, 以确定性的字典序枚举其邻居中的无序对 {a, c}, 先执行经典 GF 铁律筛选, 即仅统计端点不直连的对 (a 与 c 之间无边, 甲方必须真的需要经过 i 才能到达丙方); 随后按三者群标签归类: 三者同群计入协调人, 两端同群且异于 i 计入巡回经纪人 (本家族), 两端中恰有一端与 i 同群计入守门人代表人合并类, 三群互异计入联络人; 任一端点分组缺失的对整对跳过。四个角色计数之和等于 gf_total, 该守恒关系由单元测试锁定。两处口径细节须特别说明。其一, 无向坍缩: Gould & Fernandez (1989) 的原始框架定义在有向网络上, 有五种角色, 但银行共现图严格无向, 每条二步路径与其逆向路径不可区分, 导致守门人 (信息流入群) 与代表人 (信息流出群) 两角色机械共线, 生产口径将其合并为 gf_gatekeeper_rep, 全家族落地为四个可区分角色加总计数五列; 巡回经纪角色本身在正逆两个方向上定义对称, 无向化不改变其语义, 这是本家族相对守门人族在口径上更干净的一点。其二, 端点不直连筛选的团投影鲁棒性: 新闻共现网络由文章级团投影生成, 一篇提及多家银行的文章会在这些银行间生成完全子图, 若不加筛选, 团内任意三元组都会被误计为经纪; 经典 GF 定义天然免疫这一膨胀, 因为团内所有端点对均直接相邻, 经纪计数恒为零, 只有跨文章拼接出的真实结构洞才产生非零计数。缺失值语义刻意区分两类: 节点自身分组缺失时置 NaN (不可计算), 节点有分组但无可用二步路径 (孤立点、邻居全部直连、邻居全部缺分组) 时置零 (真实零经纪), 下游回归须区分零经纪与未知, 该约定与 bank_constraint 等列一致。计算为纯整数计数, 无随机数、无谱分解、无浮点迭代, 逐位确定可复现, 不在面板九列 BLAS 浮点漂移排除集之内。判据维度上, 本家族随全部三十三个网络结构指标 (SSOT 为 network_spillover.NETWORK_METRIC_BASES 元组) 按银行与银行共现判据分三轨落列: 无后缀列为同篇判据 (canonical, 现行口径, 同一篇文章共同幸存即成边), _win1 列为正负一句窗判据, _sent 列为严格同句判据; 后两者在 docid 组内做句级文本重扫 (标题经 prepend_title 作为第零句参与扫描, 镜像 stage 13 的 match_in_title 口径), 节点全集与同篇判据一致, 仅边集依次收紧。判据原语复用 core/text/entity_context 的银行句位映射与句窗配对函数, 银行识别与 stage 11/13 共用同一否定与短名排除事实源, 禁用裸 AC 自动机以防涉农行业误匹配农行一类假阳性。窗宽读取 config/panel.yaml 下 network_criteria.win_radius (默认一), 与 config/filtering.yaml 下 cooccurrence_filter.sentence_radius (stage 13 银行与金科共现的过滤半径) 是两个互不联动的配置键, 不可混淆。判据后缀与三轨文本后缀 (_full/_ctx/_ss, 银行与金融科技共现口径) 属于两个正交的概念空间: 前者改变的是银行间成边的判据, 后者改变的是情感测度所依据的文本切片, 两者不交叉组合。

【文献定位】
本家族在文献坐标系中位于三条脉络的交点。第一条是结构社会学的经纪与结构洞传统: Freeman (1978) 厘清了中心度族系的概念边界并确立中介性作为独立构念, Burt (2004) 将结构洞位置与信息优势和创新产出连接, Gould & Fernandez (1989) 则贡献了本家族直接实现的角色分解代数; 方法论上的现代延伸如 Zádor et al. (2022) 提出加权归一化的 GF 测度, 说明原始计数口径的规模依赖问题已被方法文献正视, 本项目以原始计数落列并把规模调整留给回归规格 (年内标准化、控制度中心度), 与该文献的处理精神一致。第二条是金融网络与银行体系脉络: Jackson & Pernoud (2021) 综述了金融网络中系统性风险的结构决定因素, 强调网络位置异质性对传染与保险的双重作用; Wang, Zhang & Yang (2020) 刻画了中国担保网络在危机与刺激周期中的结构演化, Gao, Ru & Yang (2022) 证明所有权网络在中国银行信贷决策中承载真实信息; 这些研究共同确立了在中国银行体系内, 网络结构位置 (而非仅仅规模) 是风险与信息分析的一级变量。第三条是媒体网络与信息扩散脉络: Xu (2024) 证明财经记者社交网络的结构塑造新闻偏差, Yu, Hu & Zhong (2024) 证明网络中心度经由信息扩散通道影响资产定价, Han, Kim & Nanda (2024) 在机构经纪场景下识别出经纪网络对流动性供给的因果贡献。本家族把这三条脉络接到同一个可复现的面板测度上: 用媒体共现文本还原银行间信息网络 (脉络三的测量基底), 在其上计算社会学口径的经纪角色 (脉络一的构念), 服务于中国银行金融科技研究的结构异质性分析 (脉络二的应用场景)。同期中国场景的证据同样支持把网络结构位置而非仅中心度水平作为媒体信息环境的自变量: Wang, Hou & Liu (2023, Accounting & Finance) 证明企业共股东网络中的结构洞位置通过信息控制机制降低负面媒体报道, 说明结构位置本身承载独立于中心度的媒体信息含量, 为本家族按群构型细分经纪角色 (而非仅报告一个笼统的中心度水平) 的构念取向提供了同期中国场景的实证支持。分析师覆盖网络中的经纪中介地位通过信息中介机制传导同伴效应, 驱动企业融资政策的趋同, 为本家族用媒体共现网络刻画银行经纪角色的构念提供了方法论近邻证据 (Gomes, Gopalan, Leary, & Marcet, 2024, Management Science); 实益所有权网络中的经纪节点连接彼此不直接相连的股东与目标公司群体, 其结构位置显著影响被并购概率, 印证经纪角色测度对公司金融事件具有独立解释力 (Kostaris & Andrikopoulos, 2023, International Review of Financial Analysis)。

【识别策略定位】
本家族在计量框架中的定位是结构位置控制变量与异质性调节变量, 不是因果处理变量, 也不是工具变量。网络计量的根本困难自 Manski (1993) 的反射问题起就已明确: 同伴结果、同伴特征与共同冲击在线性均值模型中不可分, 而 Bramoullé, Djebbari & Fortin (2009) 证明网络结构本身 (非重叠邻域) 可以打破这一不可识别性, Bramoullé, Djebbari & Fortin (2020) 与 Boucher et al. (2024) 进一步系统化了网络内生性与效应异质性下的识别条件。这些结果对本家族的含义是双向的: 一方面, 共现网络的拓扑非平凡性 (巡回经纪计数非零恰恰要求存在非重叠邻域结构) 是网络工具策略的前提, 项目内 brokerage_network 论文规格以二阶同伴情感作为一阶同伴效应的工具, 正是 Bramoullé 式识别的应用, 本家族列在该规格中的角色是刻画哪些银行位于适合该识别策略的结构位置; 另一方面, 媒体共现网络是内生生成的, 媒体选择报道谁与谁同框本身可能被不可观测的银行质量或事件驱动 (Grieser et al. 2022 对公司金融网络效应中此类内生性的处理提供了参照), 故本家族列进入回归时应以银行固定效应吸收慢变结构位置、以年固定效应吸收网络整体规模漂移, 系数解释为年内相对经纪地位变动的条件关联, 不宜作因果读数。节点级计数逐银行逐年变动, 与年固定效应相容 (这一点与年内恒定、会被年固定效应吸收的 net 级列如 net_density_yr 不同)。判据梯子的计量纪律遵循全仓铁律: 同篇、句窗、同句三个判据变体各自 just-identified 并排进入各自的回归, 三者互为稳健性、不分主次, 禁止把多个判据变体混进同一个 over-identified 的 Hansen J 检验; 该铁律同样约束三轨文本 (full/ctx/ss)、co-primary 双轨嵌入及各类梯子, 因为这些变体测量的是同一构念的替代口径, 联合过度识别检验会把口径差异误读为工具无效。判据族属于规格稳健性并排 (镜像政治词权重与词典消融先例), 不设跨判据的 FWER 模板, 因为跨模型 rwolf 先例仅覆盖同构念替代 headline 测量的情形。

【与相邻测度的构念区分】
先看同家族近邻: gf_coordinator 数的是三者同群的内部协调 (例如一家国有大行中介两家互不共现的国有大行), gf_gatekeeper_rep 数的是恰有一端与经纪人同群的跨群把关, gf_liaison 数的是三群互异的纯外部联络, gf_total 是四者之和; 巡回经纪与它们的判别性差异在于群构型 (两端同群且异于经纪人), 这是唯一一种经纪人以完全外部人身份介入某群内部断裂的构型, 社会学预测其地位最不稳固、最依赖持续的专业化价值供给。与路径类中介性的区分: bank_between_cent 与 bank_cfbetween_cent 度量节点落在最短路径或电流路径上的总强度, 完全不使用群归属信息, 一家银行可以中介性极高而巡回经纪为零 (它中介的全是异群对或同群于己的对); GF 角色分解正是对无差别中介性的群构型细化。与 Burt 自我网络族的区分: bank_constraint、bank_ci、bank_effective_size、bank_ego_density 从自我网络冗余度刻画结构洞的丰裕程度, 同样不区分群归属, 且它们是比率或密度型连续量, 而本家族是二步路径的整数计数。与声望类中心度的区分: 项目内 brokerage 侧的特征向量中心度族度量的是邻居质量加权的声望, GF 族度量的是真经纪 (跨群桥接), 二者构念互补, 生产注释明确要求勿混。与二分图族的区分: brok_bip 前缀列建立在媒体与银行的二分图上, 节点集合与本家族的银行投影图不同。与溢出测度族的区分: peer_tone 族与 industry_neg_shock 族是把网络当作权重矩阵去传播情感冲击的 W 轨测度, 本家族则是网络自身的拓扑属性; 前者随三轨文本与 W 轨分列, 本家族只随银行与银行判据分列, 两个分列维度不可混淆。

【已知局限与稳健性梯子】
第一, 群粒度局限: 所有制类型是粗粒度分组, 群内异质性 (同为城商行但规模与区域悬殊) 会稀释角色构念; 分组映射缺失的银行整行 NaN, 缺失非随机 (小型或新设银行更易缺), 下游须检查缺失模式。第二, 规模依赖: 原始计数与节点度近似平方相关, 大行机械占优; Zádor et al. (2022) 的加权归一化方案是文献认可的修正方向, 当前生产口径以原始计数落列, 回归侧应年内标准化或同时控制度中心度, 跨年比较水平值不可取。第三, 无向坍缩的信息损失: 守门与代表的方向语义在共现图上不可恢复, 这是数据生成过程 (共现天然无向) 的约束而非实现缺陷, 但意味着与有向网络文献对表时只能在四角色口径下进行。第四, 团投影膨胀虽被端点不直连铁律阻断于经纪计数本身, 但上游边集仍由文章团投影生成, 多银行大稿会同时加密邻居集与端点邻接, 对计数的净效应方向不定, 判据梯子 (收紧成边条件) 正是针对这一测量不确定性的规格稳健性设计: 同篇判据容忍远距离共提, 句窗判据要求近邻叙事, 同句判据要求同一句法单元内共现, 三者对报道体裁差异 (盘点式罗列对深度关联报道) 的敏感度依次递减。第五, 开发环境退化: 本机 T=2 两年开发面板上网络稀疏, 巡回经纪计数大面积为零或 NaN 属预期退化, 生产推断以 T=18 全量语料为准, 全量口径下年度共现网络的节点与边规模足以支撑非平凡的角色分布。第六, 媒体基底的解释边界: 共现网络反映的是公共信息空间中的叙事结构而非真实业务往来, You, Zhang & Zhang (2018) 与 Xu (2024) 提示的媒体生产过程偏差会传导到网络拓扑, 论文写作时应把本家族解释为媒体中介的信息网络位置, 与 Gao, Ru & Yang (2022) 式的真实所有权网络位置明确区分。稳健性梯子汇总: 三判据并排 (本家族三列)、同族四角色对照 (构念内部效度)、与无群构念的中介性列对照 (增量信息含量), 全部遵循各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J 的口径纪律。

## VAR: gf_itinerant

【变体差分】
本列是家族 canonical 列, tier=core, 采用同篇共现判据 (criterion='article', 无后缀, 现行生产口径): 只要两家银行在同一篇 both-verified 文章的幸存银行集合中共同出现, 即在该年度共现图上成边, 无论二者在文中相距多少句。在此边集上, 本列取值为目标银行 i 在该年图中满足以下全部条件的邻居无序对 {a, c} 的个数: a 与 c 之间无直接连边 (经典 GF 端点不直连铁律, 团投影鲁棒性的来源), 且 a 与 c 的所有制类型群相同而与 i 的群不同 (巡回经纪构型)。它是家族三列中边集最宽、计数期望最高的一列, 作为主口径进入回归与描述统计; _win1 与 _sent 两列是其判据收紧方向的稳健性臂。选择同篇判据为 canonical 的理由与全部三十三个网络指标一致: 它是项目自始的历史口径, 与共现图其余消费者 (溢出 W 矩阵、brokerage 论文规格) 的建图口径同源, 保证网络族内部的可比性; 列名无后缀是历史命名产物, 不含主次含义, 三判据互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。取值语义上须严格区分两类非正值: 零表示该银行有分组且入网, 但当年不存在任何满足巡回经纪构型的二步路径 (孤立、邻居全直连、或群构型不匹配), 是真实的零经纪; NaN 表示该银行的所有制分组在 load_bank_group_maps 中缺键, 角色不可计算, 或该银行当年未入网 (面板左连接后缺失)。回归样本构造时若将 NaN 简单填零, 会把测量缺失误标为结构位置边缘, 属口径错误。本列为 core 列的依据 (columns.json core_rationale): 网络结构指标家族的 canonical 判据列, 基名收录于 NETWORK_METRIC_BASES 单一事实源, 于 2026-07-10 类别六扩围签核。计算全程为确定性整数计数, 无随机数无谱分解, 不在 BLAS 浮点漂移排除集内, golden 对比无需豁免; 面板落列走节点级结果按银行乘年份左连接, 未入网银行年格因此为缺失而非零, 与上文缺失语义呼应。使用建议分三层。第一层, 量纲处理: 原始计数随节点度近似平方增长, 大型银行因媒体曝光基数机械占优, 进入回归前宜做年内标准化, 或以 gf_total 为分母构造巡回经纪占比 (刻画该银行经纪组合的构型倾向而非总量), 或同时控制 bank_degree_cent 以剥离纯规模通道, 三种处理刻画的构念侧面不同, 应按假设选择并在稳健性中互查。第二层, 固定效应相容性: 本列逐银行逐年变动, 与年固定效应相容 (不同于年内恒定会被吸收的 net 级列); 银行固定效应会吸收慢变的结构位置水平, 剩余变异来自年际经纪地位的相对起落, 系数应按此解释。第三层, 与判据臂的联合披露: 报告主结果时以本列为主口径, _win1 与 _sent 两臂并排复核, 三者各自单独进回归而非同时入 RHS, 亦不混入同一联合过度识别检验。构念解释上, 巡回经纪构型在中国银行业语境下有具体对应: 例如某股份制银行频繁与两家彼此从不同框的城商行分别同框 (数字化转型标杆报道中作为对照系), 或某外资银行在两家国有大行的国际业务报道中反复居间出现; 计数高意味着媒体叙事习惯性地把该银行放在其他类型银行群体的内部比较框架中, 这既可能反映真实的业务桥接地位, 也可能只是媒体的修辞惯例, 因果解释须谨慎。白话版: 这一列数的是, 一年之内, 有多少对同类型但互不同框的银行, 是靠这家异类型银行在新闻里被串在一起的; 数字越大, 这家银行越像是别人圈子故事里的固定中间人。

## VAR: gf_itinerant_sent

【变体差分】
本列是严格同句判据臂 (criterion='sent', 后缀 _sent), 与 canonical 列的唯一差分是银行与银行的成边条件从同篇收紧到同一句: 两家银行必须在同一篇文章的同一个句子内共同出现 (经否定与短名排除防线确认的真实提及) 才成边。实现上走 docid 组内句级重扫路径: 以 core/text/entity_context 的银行句位映射原语在 prepend_title 拼接文本 (标题作为第零句参与扫描, 镜像 stage 13 的 match_in_title 口径) 上定位每家幸存银行的句位置, 仅当两银行句位置相同才计边; 节点全集与 canonical 列一致 (同为该年幸存银行), 仅边集为其子集。同句共现是判据梯子中语义最强的一档, 近似要求媒体在单一句法单元内并置两家银行 (直接比较、并列列举或同一事件的共同主体), 对盘点式长文的远距离弱关联免疫最彻底; 代价是边集稀疏化, 在低报道密度年份或 T=2 开发面板上, 图可能碎裂为微小分量, 巡回经纪计数大面积为零属预期退化。须注意边集收紧对本列的影响并非单调: 删边既会缩小邻居集 (压低计数), 也会解除某些端点对的直接邻接从而使原本被端点不直连铁律排除的二步路径重新计入 (推高计数), 故本列与 canonical 列的差值方向逐银行不定, 这正是把它作为独立稳健性臂而非机械缩尾版本的原因。判据后缀 _sent 属于银行与银行共现判据空间, 与三轨文本后缀 _ss (银行与金科同句, 情感文本切片) 是两个正交概念, 拼写相近但语义无关, 勿混。口径纪律: 本列与无后缀、_win1 两列互为稳健性、不分主次, 各自 just-identified 并排进入各自回归, 禁混同一 over-identified Hansen J。

## VAR: gf_itinerant_win1

【变体差分】
本列是句窗判据臂 (criterion='win1', 后缀 _win1), 与 canonical 列的唯一差分是银行与银行的成边条件从同篇收紧到正负 win_radius 句的滑动窗口: 两家银行的句位置之差不超过窗宽即成边, 窗宽读取 config/panel.yaml 下 network_criteria.win_radius, 默认为一, 即相邻句或同句共现成边。该配置键与 config/filtering.yaml 下 cooccurrence_filter.sentence_radius (stage 13 银行与金融科技共现硬过滤的句窗) 是两个互不联动的独立键, 改动任一方不影响另一方, 这是生产注释显式标注的防混淆点。实现路径与 _sent 列共用同一 docid 组内句级重扫机制与同一否定短名排除事实源 (禁裸 AC 自动机, 防涉农行业匹配到农行一类假阳性), 标题经 prepend_title 作为第零句参与扫描; 节点全集与 canonical 一致, 边集严格介于同篇与同句之间 (同句成边必然句窗成边, 句窗成边必然同篇成边), 构成判据梯子的中间档。语义上, 正负一句窗口捕捉的是段落级邻近叙事: 两家银行虽不在同一句, 但出现在紧邻的行文位置, 通常对应同一论述单元内的承接或对照, 强于同篇远距离共提、弱于同句并置。与 _sent 列同理, 边集收紧对巡回经纪计数的影响双向 (缩邻居集与解除端点邻接两力相抵), 本列相对两端的差值方向逐银行逐年不定, 三列联合报告即构成对成边判据这一研究者自由度的规格稳健性披露。口径纪律与家族一致: 无后缀、_win1、_sent 三判据各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 判据后缀与三轨文本后缀 (_full/_ctx/_ss) 正交, 不交叉组合。开发环境 T=2 下本列同样呈稀疏退化, 生产推断以 T=18 全量为准。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Wang, Y., & Wei, F. (2026). Agentic, powerful, but unethical: New ventures' ethical practices as the outcome of entrepreneurs' networking behaviors and structural holes. Asia Pacific Journal of Management. https://doi.org/10.1007/s10490-026-10116-x
Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79-104. https://doi.org/10.1007/s11747-024-01043-8
Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould-Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. Journal of Financial and Quantitative Analysis, 57(8), 2993-3017. https://doi.org/10.1017/S0022109021000788
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. Nature Communications, 11, 2693. https://doi.org/10.1038/s41467-020-16535-8
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Burt, R. S. (2004). Structural holes and good ideas. American Journal of Sociology, 110(2), 349-399. https://doi.org/10.1086/421787
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. Sociological Methodology, 19, 89-126. https://doi.org/10.2307/270949
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Wang, L., Hou, W., & Liu, Y. (2023). How do co-shareholding networks affect negative media coverage? Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13091
Gomes, A. R., Gopalan, R., Leary, M. T., & Marcet, F. (2024). Analyst Coverage Networks and Corporate Financial Policies. Management Science. https://doi.org/10.1287/mnsc.2023.4891
Kostaris, K., & Andrikopoulos, A. (2023). Brokers in beneficial ownership: A network approach. International Review of Financial Analysis. https://doi.org/10.1016/j.irfa.2023.102701
<!-- rendered-citations:end -->
