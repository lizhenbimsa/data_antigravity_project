# 文献理论锚点扩充报告 · 第二补编(代码内具名引用 / Wave-1 网络 / 空间 / 战略差异 / 中文可读性 · APA 第 7 版 · DOI 全核验)

- **日期**: 2026-06-22
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 12 族 / 143 条)与 `LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 10 族 / 102 条, 合计 22 族 / 245 条)的 **第二补编**, 三者**合为一套**。前两份从"方法学族"自上而下覆盖; 本第二补编从**代码内具名引用**自下而上反向核查, 补齐两类此前未锚的缺口:
  - **缺口 A(结构性)**: 2026-06-21 落地的 **Wave-1 网络指标**(`_gould_fernandez_roles` / `_net_level_extra_metrics` / `_bipartite_bank_metrics`)在补编族 20 写定**之后**新增, 其算法出处(Gould-Fernandez 经纪角色 / 模块度 / 度相关性 / 两模二分图中心度)族 20 **未覆盖**。
  - **缺口 B(审计盲区)**: 前四轮"完整性审计"按**方法学族**核查, 未对**代码注释/docstring 内已具名的引用**逐条核对是否进了参考表。本次反向核查发现 **~65 条**项目**自己代码里点名**的文献(空间滞后 LeSage-Pace、认知邻近 Boschma、niche distance Guzman-Li、fluidity Hoberg-Phillips-Prabhala、JS 散度 Lin、LDA Blei、数字密度 Davis-Tama-Sweet、可读性 Dale-Chall、valence-shifter Kennedy-Inkpen/Taboada、脱耦 Westphal-Zajac、rare-events logit King-Zeng、LLM 校准 Guo/Carlson-Burbano、**stage 12 金科词典 胡俊等 2024** 等)**不在** 245 条之列。它们是**项目作者写进代码的真实引用**(非本次自我生成), 本补编逐条在权威源核验后补入。
- **规模**: **两批 / 10 个子族(23–32 续号, 接主编+补编的 1–22) / 65 条 code-named 引用 → 63 条已核验 + 2 条未核验 flagged**。
  - 第一批(§二, 28 条): 子族 23 网络 Wave-1 算法出处(10)+ 24 空间-地理(4)+ 25 战略差异(6)+ 26 可读性-词法(8); 27 confirmed(含 2 中文 丘心颖2016/徐巍2021)+ 1 flagged(谢佳松2025)。
  - 第二批(§六, 37 条, 完整性批判发现): 子族 27 情感语言学规则(6)+ 28 LLM 方法/校准/标注效度(11)+ 29 媒体类型构成(7)+ 30 组织理论脱耦(6)+ 31 计量/IR/网络方法(5)+ 32 中文(2); 36 confirmed + 1 flagged(欧阳志刚2024)。
  - **2024–2026 新近条目密集**: Han-Kim-Nanda 2024 RFS / Carlson-Burbano 2026 SMJ / Chiu-Hung 2025 PBFJ / Gilardi 2023 PNAS / Heese 2022 JFE / Holzman 2023 TAR / Tornberg 2024 / 胡俊等 2024 / 欧阳志刚2024 等; 另 §三 附经核验的 2024–2026 近期同法应用。
- **核验铁律(沿用主编/补编)**: "查不实=不存在"。本批 **26 条非中文文献的 DOI/落地页由主控(main loop)在 2026-06-22 当场逐条 Crossref/出版社/JMLR/JSTOR 实时抓取、DOI→标题逐字回比**(防"错位 DOI 解析到另一篇真论文"); 另经独立多智能体工作流(`wf_5cac45b0-969`)二次对抗复核。**主控核验中实测捕获 2 处真 DOI 前缀错误**(见 §四), 印证"DOI→标题回比"不可省。3 条中文文献(CNKI 索引, 不进 Crossref)按"查实-或-标注 pending"处理, **绝不臆造**。
- **生产方式**: 主控主循环逐条 Crossref/arXiv/JMLR/JSTOR DOI→标题回比(28/28 非中文条目 + 3 中文 verify-or-flag) + 多智能体工作流(28 条 find→对抗-verify 双阶段 + 高风险既有 245 条抽样独立复核 + 代码注释完整性批判)。

---

## 〇、白话导读

**为什么还要再补一份**: 前两份文档把"项目用了哪些方法、各配什么文献"梳理得很全了。但有两件事它们没做: ① 昨天(06-21)新加的一批**网络指标**(银行经纪角色、网络模块度、二分图中心度)是在文献表写完**之后**才落代码的, 等于"先发文献表、后加指标", 这批指标的算法出处漏了; ② 前四轮审计都是"按方法找文献", 没人反过来把**代码注释里项目自己写的引用**(比如代码里明明写着"LeSage-Pace 2009""Boschma 2005""Guzman-Li 2023")拿去和文献表逐条对账——一对账发现有 ~28 条**代码点了名、文献表却没收**。这份文档就专门补这两个缺口。

**和"严禁自我生成"的关系**: 这 28 条**不是我编的**, 是**项目作者写在代码里的真实引用**。我的工作是把它们逐条拿到 Crossref/JSTOR 等权威源去**核实存在 + 抓准 DOL/卷期页**, 查不实的(尤其 3 条中文)就如实标"待核验", 决不假装查到。核验中我还真抓到 2 个 DOI 写错的(下面 §四), 所以"DOI→标题回比"这步一步都不能省。

**怎么用**: 写论文时, 这 28 条按 §二的子族归类直接引用; 参考文献表抄 §五。注意 3 条中文文献(谢佳松等 2025、丘心颖等 2016、徐巍等 2021)在投稿前须经 CNKI 最终确认。

---

## 一、核验协议

1. **DOI→标题回比(防伪主轴)**: 每条非中文文献, 主控亲自 `GET https://api.crossref.org/works/{DOI}`(或 arXiv/JMLR/JSTOR/出版社页), 读回**真实解析标题**与所引论文逐字比对。DOI 解析到**另一篇真论文** = FAIL。
2. **铁律**: 无法在权威源确认存在者一律不主张(中文 CNKI 文献若 US 检索不可达, 标 "pending CNKI 核验", 不计入"已核验"。)
3. **年份规则**: 期刊按卷期所属刊年(Cazier-Pfeiffer 标 2016 / You-Zhang 标 2009, 在线首发早一年)。
4. **claim-fit**: 每条锚定声明须与**具体代码位置 + 指标列**绑定, 诚实区分"直接算法出处"与"构念/经济学锚点"。

---

## 二、四个子族 × 锚点清单(代码内具名 + Wave-1 算法出处; 其余六个子族 27–32 见 §六)

### 子族 23. Wave-1 网络指标算法出处(补编族 20 扩展; 2026-06-21 新增指标)

项目做法(白话): 2026-06-21 在银行共现网络与媒体-银行二分图上新增三组指标——① 五种 Gould-Fernandez 经纪角色(gf_*); ② 六个网络级结构控制(模块度/度相关性/传递性/直径/巨片占比/分量数, net_*_yr); ③ 五个二分图银行端中心度(brok_bip_*)。补编族 20 在这批指标落地前写定, 故其算法出处未收。本子族补齐。

- Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. *Sociological Methodology, 19*, 89–126. https://doi.org/10.2307/270949
  - *锚定*: `pipeline/panel/network_spillover.py::_gould_fernandez_roles` 的五经纪角色计数(coordinator/itinerant/gatekeeper_rep/liaison/total)直接实现 Gould-Fernandez(1989)的"中介结构"形式化框架——按 broker 与两无序非邻接端点的群归属三元组归类, 是 WS-C `gf_*` 角色测度的**直接算法奠基出处**。
- Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. *Physical Review E, 70*(6), 066111. https://doi.org/10.1103/PhysRevE.70.066111
  - *锚定*: `_net_level_extra_metrics` 用 `nx.community.greedy_modularity_communities` 做社区检测, 代码注释具名 CNM(2004)greedy 算法, 是 `net_modularity_yr` 社区划分的**直接算法出处**。
- Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. *Physical Review E, 69*(2), 026113. https://doi.org/10.1103/PhysRevE.69.026113
  - *锚定*: `net_modularity_yr` 的模块度 Q 打分(`nx.community.modularity`)源自 Newman-Girvan(2004)提出的模块度 Q 函数, 是该**统计量的原始定义出处**(与 CNM 2004 的检测算法互补)。
- Newman, M. E. J. (2002). Assortative mixing in networks. *Physical Review Letters, 89*(20), 208701. https://doi.org/10.1103/PhysRevLett.89.208701
  - *锚定*: `net_assortativity_yr`(`nx.degree_assortativity_coefficient`)的度相关性(assortative mixing)系数**原始出处**。
- Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review, 45*(2), 167–256. https://doi.org/10.1137/S003614450342480
  - *锚定*: `net_transitivity_yr`(全局传递性)、`net_giant_share_yr`(巨片占比)、`net_n_components_yr`(连通分量数)、`net_diameter_yr`(直径)这组复杂网络结构测度的权威综述出处(三角传递性、巨片/渗流、连通分量、最短路直径)。
- Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. *Social Networks, 19*(3), 243–269. https://doi.org/10.1016/S0378-8733(96)00301-2
  - *锚定*: `pipeline/panel/network_brokerage.py::_bipartite_bank_metrics` 的二分图(两模)度/介数中心度(`nx.bipartite.degree_centrality`/`betweenness_centrality`)的**方法奠基出处**。
- Faust, K. (1997). Centrality in affiliation networks. *Social Networks, 19*(2), 157–191. https://doi.org/10.1016/S0378-8733(96)00300-0
  - *锚定*: 隶属(affiliation/两模)网络中心度的**方法出处**, 与 Borgatti-Everett(1997)共同构成 `brok_bip_degree_cent`/`brok_bip_between_cent`/`brok_bip_closeness_cent` 的两模中心度方法学参照。
- Robins, G., & Alexander, M. (2004). Small worlds among interlocking directors: Network structure and distance in bipartite graphs. *Computational & Mathematical Organization Theory, 10*(1), 69–94. https://doi.org/10.1023/B:CMOT.0000032580.12184.c0
  - *锚定*: `brok_bip_clustering_ra`(`nx.bipartite.clustering`, `mode='dot'`)的二分图聚类系数出处——代码注释**具名 Robins-Alexander 2004**。
- Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. *Social Networks, 30*(1), 31–48. https://doi.org/10.1016/j.socnet.2007.04.006
  - *锚定*: `brok_bip_node_redundancy`(`nx.bipartite.node_redundancy`)的大型两模网络节点冗余测度**方法出处**。
- Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. *The Review of Financial Studies, 37*(9), 2903–2935. https://doi.org/10.1093/rfs/hhae026
  - *锚定(构念锚, 非算法)*: 金融"机构经纪网络"构念的最新顶刊(RFS 2024)实证出处, 为项目把媒体-银行二分图介数 `brok_bip_between_cent` 解读为"真经纪"位置(区别于 `brokerage_eigen_cent` 的声望)提供金融语境的**经济学构念锚点**。⚠ 二分图介数的**算法出处**是 Borgatti-Everett/Faust; 本文锚定的是经纪网络的经济学构念与解读, **非算法**(代码 `network_brokerage.py:24` 具名 Han 2024 系此意)。

### 子族 24. 空间滞后 / 地理邻近 / 截面标准化(代码具名)

项目做法(白话): ① `peer_tone_2nd` = W²·tone 的行随机化"空间滞后"(二阶同业语调加权均值, 作 brokerage IV 工具); ② 50/100/150/200km 地理缓冲的本地媒体接近度; ③ 逐年截面 z-score 标准化。这三处代码均已具名引用, 但文献表未收。

- LeSage, J., & Pace, R. K. (2009). *Introduction to spatial econometrics*. Chapman and Hall/CRC. https://doi.org/10.1201/9781420064254
  - *锚定*: `network_spillover.py:223/336/391` 注释具名; `W2 = W_arr @ W_arr` 行随机化空间滞后(`peer_tone_2nd`)直接对应空间计量的**空间滞后算子 W·y**, 是该构造的方法学出处。补编族 14(Manski 1993 反射问题 / Bramoullé 2009 网络识别)锚定 peer-effects **识别**, 本条补齐**空间滞后估计原语**本身。
- Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local equity preference in domestic portfolios. *The Journal of Finance, 54*(6), 2045–2073. https://doi.org/10.1111/0022-1082.00181
  - *锚定*: `geography.py::compute_geo_proximity_buffers` 的 50/100/150/200km 本地媒体接近度(geography.py docstring 具名), 其"地理距离→本地偏好/信息优势"机制的金融学奠基出处(与既有 Gurun-Butler 2012 本地媒体倾向互补)。
- Fama, E. F., & MacBeth, J. D. (1973). Risk, return, and equilibrium: Empirical tests. *Journal of Political Economy, 81*(3), 607–636. https://doi.org/10.1086/260061
  - *锚定*: `geography.py::standardize_panel_variables` 的逐年截面 z-score 标准化(docstring 具名)直接对应 Fama-MacBeth 年度截面程序。补编族 13 的 Petersen(2009)引此作 SE 对比, 本条补齐**截面标准化原典**本身。
- Boschma, R. (2005). Proximity and innovation: A critical assessment. *Regional Studies, 39*(1), 61–74. https://doi.org/10.1080/0034340052000320887
  - *锚定*: `network_spillover.py:32` 注释具名; `bank_cogn_mean`(对全体其他银行的平均余弦相似度)操作化 Boschma(2005)的**认知邻近(cognitive proximity)**构念。

### 子族 25. 战略差异 / 文本距离 / 主题模型(代码具名)

项目做法(白话): `strategic_diff.py` 用四轨方法(TF-IDF char/word + LDA + 嵌入)给每家银行的金科新闻建主题向量, 算两类差异度: ① N-最近邻 niche distance(到 N 个最像同行的平均距离); ② 行业质心余弦距离; 主题分布间用 Jensen-Shannon 散度; 还有 fluidity、文本创新等。代码均已具名。

- Guzman, J., & Li, A. (2023). Measuring founding strategy. *Management Science, 69*(1), 101–118. https://doi.org/10.1287/mnsc.2022.4369
  - *锚定*: `strategic_diff.py:12` 注释具名(§3); N-最近邻 niche distance(Ŝ_i = mean(到 N 个最近同行的文本距离))直接对应 Guzman & Li(2023)的创始战略差异测度。
- Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. *The Journal of Finance, 69*(1), 293–324. https://doi.org/10.1111/jofi.12050
  - *锚定*: `strategic_diff.py:54` 注释具名(Eq.2); 产品市场 fluidity(流动性)测度的**直接出处**(与既有 Hoberg-Phillips 2016 TNIC 互补, 后者已在主编)。
- Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. *Management Science, 67*(7), 4004–4031. https://doi.org/10.1287/mnsc.2020.3682
  - *锚定*: `strategic_diff.py:57` 注释具名; 文本法企业创新测度的顶刊出处, 为项目以新闻文本测度银行"创新边界"提供方法先例。
- Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory, 37*(1), 145–151. https://doi.org/10.1109/18.61115
  - *锚定*: `strategic_diff.py:62` 用 `scipy.spatial.distance.jensenshannon` 计算 LDA 主题分布间的 **Jensen-Shannon 散度**, Lin(1991)是 JS 散度的方法出处。
- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. *Journal of Machine Learning Research, 3*, 993–1022. https://www.jmlr.org/papers/v3/blei03a.html
  - *锚定*: `strategic_diff.py:74` 注释具名; LDA 主题向量(`*_lda` 轨 / `coh_lda` 主题一致性)的**算法奠基出处**。补编族 19 收 TF-IDF/MinHash/Aho-Corasick 但无 LDA, 本条补齐(JMLR 无 DOI, 用官方稳定页)。
- 谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界. *经济研究*, (11). 〔**待 CNKI 最终核验** — 代码 `strategic_diff.py:1004` docstring 具名引用; CNKI 索引文献, 未进 Crossref, US 检索不可达; **不作"已核验"主张**, 投稿前须经 CNKI/知网最终确认或改引可及替代〕
  - *锚定(代码内来源, 待核验)*: `_compute_centroid_scores` 的行业质心余弦差异(1 − cos(v_i, leave-one-out 行业质心))在代码 docstring 中标注迁移自该文的 BERTopic 余弦相似度方法。**核验状态见 §四**。

### 子族 26. 中文/基础可读性与词法测度(代码具名)

项目做法(白话): `lexical_complexity.py` / `numerical_intensity.py` 的难字率、类符-形符比、数字密度、转折/对照词频等测度, 代码注释具名了一批基础与中文文献(Dale-Chall 可读性、MATTR、Davis-Tama-Sweet 数字密度等), 文献表未收。

- Dale, E., & Chall, J. S. (1948). A formula for predicting readability. *Educational Research Bulletin, 27*(1), 11–20, 28. https://www.jstor.org/stable/1473669
  - *锚定*: `lexical_complexity.py:14` 注释具名; familiar-word 可读性公式的**奠基出处**(项目 `hard_char_ratio` 中文难字率为其"难词比例"思想的中文移植)。〔JSTOR 收录; Crossref **未注册** DOI(10.2307/1473669 解析 404), 故用 JSTOR 稳定链接而非臆造 DOI; 该文分两部分刊出: 27(1):11–20 与"Instructions"27(2):37–54〕
- Cazier, R. A., & Pfeiffer, R. J. (2016). Why are 10-K filings so long? *Accounting Horizons, 30*(1), 1–21. https://doi.org/10.2308/acch-51240
  - *锚定*: `lexical_complexity.py:23` 注释具名; 文档内冗余/篇幅测度的会计学出处, 锚定 `within_doc_redundancy`(字符 3-gram 冗余)。
- Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A. *Contemporary Accounting Research, 29*(3), 804–837. https://doi.org/10.1111/j.1911-3846.2011.01125.x
  - *锚定*: `numerical_intensity.py:5` 注释具名; 披露语言中"硬信息"/数字使用的测度出处, 锚定 `num_intensity`/`num_intensity_word`(数字密度)。
- You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. *Review of Accounting Studies, 14*(4), 559–586. https://doi.org/10.1007/s11142-008-9083-2
  - *锚定*: `lexical_complexity.py:12` 注释具名; 财报复杂度与投资者反应不足的出处, 锚定 `rare_word_ratio`/复杂度族的经济含义。
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100. https://doi.org/10.1080/09296171003643098
  - *锚定*: `lexical_complexity.py:35` 注释具名; MATTR(移动平均类符-形符比)处理 TTR 长度依赖的方法出处。补编族 22 收 Tweedie-Baayen(1998)TTR, 本条补齐 **MATTR 长度校正**的具名出处。
- Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. In *Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)* (pp. 231–240). ACM. https://doi.org/10.1145/1341531.1341561
  - *锚定*: `lexical_complexity.py:141` 注释具名; 词典法意见挖掘中**转折/对照词(adversative)处理**的方法出处, 锚定项目转折连词频率测度。
- 丘心颖, 郑小翠, & 邓可斌. (2016). 分析师能有效发挥专业解读信息的作用吗？——基于汉字年报复杂性指标的研究. *经济学(季刊), 15*(4), 1483–1506. 〔**多智能体已核验** — PDF 页眉"第15卷第4期 2016年7月 经济学(季刊) China Economic Quarterly Vol.15, No.4"+ 页码 1483-1506 + 三作者独立核实〕
  - *锚定*: `lexical_complexity.py:15` 注释具名(15(4):1483-1506 逐字); 其"次常用字密度"(基于《现代汉语次常用字表》的生僻/次常用字密度)正是项目 `hard_char_ratio`(jieba 高频常用字之外的字符占比)所移植的汉字稀有度可读性思路, 是 Dale-Chall"难词比例"的**中文字符级对应**。
- 徐巍, 姚振晔, & 陈冬华. (2021). 中文年报可读性：衡量与检验. *会计研究*, (3), 28–44. 〔**多智能体已核验** — 经中国会计学会官方 TOC(asc.net.cn 2021/issue=3)+ cntext 文档独立核实〕
  - *锚定*: `lexical_complexity.py:141` 注释具名(会计研究 2021(3):28-44, 副词连词占比); 其可读性 readability2(每句副词+连词占比)是项目转折连词频率测度的**母构念**, 项目仅取其中"转折/对照连词"的**严格子集**(忠实保守)。

---

## 三、近期(2024–2026)同法应用增补(多智能体提出 + 独立 DOI→标题复核)

> 本节每条均经工作流 stage-2 独立 `companion_check`(再次 Crossref 解析 DOI→标题)核验; 仅收真正同法的近期应用。**本第二补编的"大量 2024–2026 新近性"主要由 §二/§六的缺口锚点本身承载**(Han-Kim-Nanda 2024 RFS、Carlson-Burbano 2026 SMJ、Chiu-Hung 2025 PBFJ、Gilardi 2023 PNAS、Heese 2022 JFE、Holzman 2023 TAR、Tornberg 2024 等), 本节为补充。

- **网络模块度的金融应用**: Jiang, J., Jiang, X., Yan, Y., Xie, S., & Yao, J. (2025). Alliance-based modeling of interbank lending networks: Insights into risk contagion dynamics. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0324981 — 把社区检测/模块度用于银行间借贷网络风险传染, 是 `net_modularity_yr` 的近期金融应用。
- **数字披露密度的近期应用**: Taraj, I., & Wahlström, R. R. (2026). Narratives contextualizing numeric disclosures: Insights from earnings calls. *Journal of Business Finance & Accounting, 53*(3), 1263–1286. https://doi.org/10.1111/jbfa.70056 — 数字披露的叙事语境, 呼应 `num_intensity`。
- **文本复杂度的近期应用**: (a) Yu, ?, & Zhao, ? (2024). Textual disclosure complexity and analysts' weighting of information. *Journal of Contemporary Accounting & Economics*. https://doi.org/10.1016/j.jcae.2023.100395; (b) Lesmy, Muchnik & Mugerman (2025). Lost in the fog: Growing complexity in financial reporting—A comparative study. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-025-06094-y — 呼应 `rare_word_ratio`/复杂度族(You-Zhang 2009 母锚)。
- **MATTR 的近期评估**: Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. *Research Methods in Applied Linguistics, 4*(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168 — 呼应 `type_token_ratio`(Covington-McFall 2010 出处)。

> 注: 上述各条作者名/年份若标 "?" 系 companion_check 仅回比了 DOI→标题(已 MATCH), 完整作者串投稿前应以 Crossref 全字段复填; 其 DOI 均已独立解析无误。

---

## 四、核验记录与 DOI 防伪实测(2026-06-22)

**主控主循环 DOI→标题回比(28/28 非中文条目)**: 26 条经 Crossref 实时解析 + Blei(JMLR 稳定页)+ Dale-Chall(JSTOR 稳定页, Crossref 未注册)逐条确认解析标题=所引论文。

**实测捕获 2 处真 DOI 前缀错误(印证回比不可省)**:
1. **Gould-Fernandez(1989)**: 初查 DOI `10.1086/229068` 解析到 **Sampson & Groves(1989)"Community Structure and Crime"(AJS)**——完全另一篇论文 → 已纠正为 `10.2307/270949`(Sociological Methodology 19:89–126, 解析标题精确匹配)。
2. **Borgatti-Everett(1997)**: 初查 `10.1016/S0378-8733(97)00008-0` 解析 **404** → 实为 `10.1016/S0378-8733(96)00301-2`(前缀是 (96) 非 (97); Social Networks 19(3):243–269)。

**3 条中文 CNKI 文献状态(多智能体独立核验后)**:
- ✅ **丘心颖, 郑小翠, 邓可斌 (2016)** — **已确认**(独立智能体抓到 ResearchGate 自存 PDF 页眉"第15卷第4期 2016年7月 经济学(季刊) Vol.15, No.4" + 页码 1483-1506 + 三作者; 代码 `lexical_complexity.py:15` 逐字匹配)。
- ✅ **徐巍, 姚振晔, 陈冬华 (2021)** — **已确认**(独立智能体经中国会计学会官方 TOC `asc.net.cn 2021/issue=3` + cntext 文档核实题名"中文年报可读性：衡量与检验", 会计研究 2021(3):28-44)。
- ⚠ **谢佳松, 樊嘉诚, 林建浩 (2025) 经济研究** — **未能核验, 保持 flagged**。独立智能体三条检索路径 + 经济研究 2025 第 10/11 期目录逐条比对**均未找到**该题名(林建浩系中山大学岭南学院真实文本计量学者且确在经济研究发文, 故引用"看似可信"但具体文章不可证实)。**裁决: 不作已核验主张, 论文中标"待 CNKI 核实/代码内部引用"**; 该质心差异度量已由 Hoberg-Phillips (2016, 已在主编)+ Guzman-Li (2023, §二子族 25) 充分锚定, 移除此条不影响指标可锚定性。

**多智能体工作流复核(`wf_5cac45b0-969`, 65 智能体, ~440 万 token, 657 次联网核验)**:
- **28 条新增 find→对抗-verify 双阶段: 26 条 CONFIRM, 2 条中文确认(qiu/xu), 1 条中文(xie)正确 flagged**。对抗层独立 DOI→标题回比, 全部 `title_match=true`(中文 flagged 项除外), `claim_fit_honest=true`; 仅 1 处 claim-fit 措辞微调(LDA 列名 `coh_lda`→实为 `strat_diff_n5_lda`, 非引用错)。**0 FIX、0 REJECT**(中文 xie 的 "flag 而非 assert" 经对抗层独立坐实为正确处置)。
- **既有 245 条高风险抽样独立复核(6 桶, 含 2024-2026 WP / 中文 / 复姓 / 形近刊名 / 跨命名空间 DOI 陷阱)**: 绝大多数 `any_problem=false`; **发现 2 处工作论文状态漂移(非主编错误)**——
  1. **Chen, Kelly & Xiu (2026)**: 主编用 `ssrn.com/abstract=4416687` 链接(**可访问, 正确**); 但其 DOI 形式 `10.2139/ssrn.4416687` 在 Crossref/doi.org **均 404**(SSRN 该 ID 未注册 Crossref DOI)→ 启示: 引用此文用 SSRN 链接, **勿**用 DOI 形式。另该文 SSRN 起源年份(2022/2023)使"2026"标注偏新。
  2. **Gao, Jiang & Yan (2026)**: SSRN DOI `10.2139/ssrn.5985277` 解析仍为 "A Test of Lookahead Bias..."(与主编一致); 但其 **arXiv 2512.23847 v2(2026-06-12 改)题名已改为 "Detecting Lookahead Bias in LLM Forecasts"**——同文同 ID, arXiv 题名漂移, 投稿前复查。
  - 其余高风险条(含 LM-2014 跨命名空间 `jofi.12162`、Sautner 双胞胎分刊、复姓 Santos Silva/Montiel Olea/Nguyen、CNKI 姜富伟/You/Du/Bian)**全部 confirmed 无误**。
- **完整性批判(3 智能体, 分扫 sentiment/text、panel/features、validation/filtering/core)**: 发现**代码注释内另有约 35-40 条具名引用未进 245 主编/补编**(前四轮审计按方法学族核查, 未对代码注释逐条对账)→ 已据此启动**第二批验证(`wf_9c571baf-482`)**, 结果见 §六。另发现一批"指标有构念锚但**操作化为项目自定义**(无单一方法出处)"项, 如实记录于 §七。**在代码内已被标注为勘误/弃用的引用**(Hales-Kuang-Venkataraman 2011 误标 / Platt 1999 标 NOT USED / Dahlke 2024 disclaimed / Berger-2022-JFI removed / Jiang-2019-PLS 改 Janis-Fadner)**一律不收**。

---

## 五、合并参考文献总表(第二补编 28 条, APA 第 7 版, 按第一作者姓氏字母序)

> 〔与主编 143 + 补编 102 = 245 条互补不重叠; 本表 3 条中文中仅 1 条(谢佳松等 2025)待 CNKI 核验, 以〔待核验〕标注; 另 2 条(丘心颖 2016 / 徐巍 2021)已核验〕

- Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. *Management Science, 67*(7), 4004–4031. https://doi.org/10.1287/mnsc.2020.3682
- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. *Journal of Machine Learning Research, 3*, 993–1022. https://www.jmlr.org/papers/v3/blei03a.html
- Borgatti, S. P., & Everett, M. G. (1997). Network analysis of 2-mode data. *Social Networks, 19*(3), 243–269. https://doi.org/10.1016/S0378-8733(96)00301-2
- Boschma, R. (2005). Proximity and innovation: A critical assessment. *Regional Studies, 39*(1), 61–74. https://doi.org/10.1080/0034340052000320887
- Cazier, R. A., & Pfeiffer, R. J. (2016). Why are 10-K filings so long? *Accounting Horizons, 30*(1), 1–21. https://doi.org/10.2308/acch-51240
- Clauset, A., Newman, M. E. J., & Moore, C. (2004). Finding community structure in very large networks. *Physical Review E, 70*(6), 066111. https://doi.org/10.1103/PhysRevE.70.066111
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100. https://doi.org/10.1080/09296171003643098
- Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local equity preference in domestic portfolios. *The Journal of Finance, 54*(6), 2045–2073. https://doi.org/10.1111/0022-1082.00181
- Dale, E., & Chall, J. S. (1948). A formula for predicting readability. *Educational Research Bulletin, 27*(1), 11–20, 28. https://www.jstor.org/stable/1473669
- Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A. *Contemporary Accounting Research, 29*(3), 804–837. https://doi.org/10.1111/j.1911-3846.2011.01125.x
- Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. In *Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)* (pp. 231–240). ACM. https://doi.org/10.1145/1341531.1341561
- Fama, E. F., & MacBeth, J. D. (1973). Risk, return, and equilibrium: Empirical tests. *Journal of Political Economy, 81*(3), 607–636. https://doi.org/10.1086/260061
- Faust, K. (1997). Centrality in affiliation networks. *Social Networks, 19*(2), 157–191. https://doi.org/10.1016/S0378-8733(96)00300-0
- Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. *Sociological Methodology, 19*, 89–126. https://doi.org/10.2307/270949
- Guzman, J., & Li, A. (2023). Measuring founding strategy. *Management Science, 69*(1), 101–118. https://doi.org/10.1287/mnsc.2022.4369
- Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. *The Review of Financial Studies, 37*(9), 2903–2935. https://doi.org/10.1093/rfs/hhae026
- Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. *The Journal of Finance, 69*(1), 293–324. https://doi.org/10.1111/jofi.12050
- Latapy, M., Magnien, C., & Del Vecchio, N. (2008). Basic notions for the analysis of large two-mode networks. *Social Networks, 30*(1), 31–48. https://doi.org/10.1016/j.socnet.2007.04.006
- LeSage, J., & Pace, R. K. (2009). *Introduction to spatial econometrics*. Chapman and Hall/CRC. https://doi.org/10.1201/9781420064254
- Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory, 37*(1), 145–151. https://doi.org/10.1109/18.61115
- Newman, M. E. J. (2002). Assortative mixing in networks. *Physical Review Letters, 89*(20), 208701. https://doi.org/10.1103/PhysRevLett.89.208701
- Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review, 45*(2), 167–256. https://doi.org/10.1137/S003614450342480
- Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure in networks. *Physical Review E, 69*(2), 026113. https://doi.org/10.1103/PhysRevE.69.026113
- Robins, G., & Alexander, M. (2004). Small worlds among interlocking directors: Network structure and distance in bipartite graphs. *Computational & Mathematical Organization Theory, 10*(1), 69–94. https://doi.org/10.1023/B:CMOT.0000032580.12184.c0
- You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. *Review of Accounting Studies, 14*(4), 559–586. https://doi.org/10.1007/s11142-008-9083-2
- 丘心颖, 郑小翠, & 邓可斌. (2016). 分析师能有效发挥专业解读信息的作用吗？——基于汉字年报复杂性指标的研究. *经济学(季刊), 15*(4), 1483–1506.
- 徐巍, 姚振晔, & 陈冬华. (2021). 中文年报可读性：衡量与检验. *会计研究*, (3), 28–44.
- 〔**待 CNKI 核实, 未确认, 不作已核验主张**〕 谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界. *经济研究*, (11). 〔代码 `strategic_diff.py:1004` 内部引用; 多智能体逐目录核验未找到; 论文写作请改引 Hoberg-Phillips (2016) / Guzman-Li (2023)〕

---

## 六、完整性批判补遗(第二批 · 37 条代码内具名引用, 由完整性批判 `wf_5cac45b0-969` 发现 + `wf_9c571baf-482` 验证)

> 完整性批判逐文件扫描代码注释/docstring, 发现 §二 的 28 条之外**另有约 37 条具名引用**未进 245 主编/补编(同一审计盲区: 按方法学族审, 未对代码注释逐条对账)。本批 **36 条经多智能体 find→对抗-verify 双阶段核验为真**(其中 4 条对抗判 FIX, 但**FIX 全指向代码注释缺陷(DOI 笔误/置放/误归/刊名标签), 引用本身 APA 正确**, 详见 §七), **1 条中文(欧阳志刚-胡雯华 2024)未能核验 → flagged 不主张**。

### 子族 27. 情感语言学规则(`tone_words.py` msent: 否定/程度/转折)

项目做法(白话): 词典情感分 `msent` 不是裸数正负词, 而是带规则——否定词翻号、程度副词乘子、转折连词动态增强。这些规则各有方法学出处, 代码均具名。

- Kennedy, A., & Inkpen, D. (2006). Sentiment classification of movie reviews using contextual valence shifters. *Computational Intelligence, 22*(2), 110–125. https://doi.org/10.1111/j.1467-8640.2006.00277.x
  - *锚定*: contextual valence shifters 三类(negation 翻号 / intensifier 增强 / diminisher 减弱)正是 `tone_words.py:189,1296` 的 msent 否定翻号 + 程度乘子(0.3–3.0)的**直接方法出处**。
- Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. *Computational Linguistics, 37*(2), 267–307. https://doi.org/10.1162/COLI_a_00049
  - *锚定*: SO-CAL 词典法(强化词 + 否定处理)是 `tone_words.py:1297` 词典情感 valence-shifter 谱系的权威出处(ACL 2021 Test-of-Time)。
- Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. *Foundations and Trends in Information Retrieval, 2*(1–2), 1–135. https://doi.org/10.1561/1500000011
  - *锚定*: 意见挖掘/词典法情感的奠基综述, 锚定 `tone_words.py:179` 词典法极性打分的整体方法谱系。⚠ 代码 `tone_words.py:181` 的 DOI 写成 `10.1561/1500000001`(解析到另一篇 Prager 2007 问答综述)——**真 DOL 笔误**, 正确为 `…0011`(详见 §七)。
- Liu, B. (2012). Sentiment analysis and opinion mining. *Synthesis Lectures on Human Language Technologies, 5*(1), 1–167. Morgan & Claypool. https://doi.org/10.2200/S00416ED1V01Y201204HLT016
  - *锚定*: 意见词典/程度词权威专著, 锚定 `tone_words.py:208` 程度副词三级线性近似(代码自定义权重矩阵, 思想同源于本书 + HowNet)。
- Jia, L., Yu, C., & Meng, W. (2009). The effect of negation on sentiment analysis and retrieval effectiveness. In *Proceedings of the 18th ACM Conference on Information and Knowledge Management (CIKM '09)* (pp. 1827–1830). ACM. https://doi.org/10.1145/1645953.1646241
  - *锚定*: 专研否定对情感的影响, 锚定 `tone_words.py:176` msent 否定辖域规则。
- Li, F., Huang, M., & Zhu, X. (2010). Sentiment analysis with global topics and local dependency. *Proceedings of the AAAI Conference on Artificial Intelligence, 24*(1), 1371–1376. https://doi.org/10.1609/aaai.v24i1.7523
  - *锚定*: Sentiment-LDA 的"局部依赖"= 连词("and"/"but")驱动的情感转移, 对应 msent **转折连词动态增强**。⚠ 代码 `tone_words.py:184` 误置于"程度副词权重"块, 更契合"转折连词"块(本文主建模连词驱动的局部依赖而非程度副词强化; Kennedy-Inkpen 2006 才是该块正确的程度/强化锚, 仍应留; 详见 §七)。

### 子族 28. LLM 方法 / 概率校准 / 标注效度(`tone_llms.py` / `validation/`)

项目做法(白话): LLM 投票打分要把"模型自报置信"映射成连续分、要校准概率、要证明 LLM 标注可信、要防"调参挑结果"。这些方法步骤代码均具名。

- Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. *Journal of Econometrics, 228*(2), 221–243. https://doi.org/10.1016/j.jeconom.2020.07.053
  - *锚定*: 新闻情感的连续测度与衰减偏误校正, 锚定 `tone_llms.py:1174`/`encode.py` 的情感分构造与"≥2/3 共识"聚合。
- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences, 120*(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
  - *锚定*: LLM 文本标注效度(vs 人工/众包)的顶刊证据, 锚定 `codebook.py:1331` LLM-vs-规则交叉验证(κ/一致性)。
- Törnberg, P. (2024). Best practices for text annotation with large language models. *Sociologica, 18*(2), 67–85. https://doi.org/10.6092/issn.1971-8853/19461
  - *锚定*: LLM 标注最佳实践(避免 web UI、多模型可复现), 锚定 `tone_llms.py:495` LLM 标注规程与稳健性。
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning (ICML)* (PMLR 70, pp. 1321–1330). https://proceedings.mlr.press/v70/guo17a.html
  - *锚定*: Expected Calibration Error(ECE)与可靠性分箱的出处, 锚定 `validation/tone_validation.py` 的 10 箱 ECE 校准。
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In *Proceedings of the 22nd International Conference on Machine Learning (ICML)* (pp. 625–632). ACM. https://doi.org/10.1145/1102351.1102430
  - *锚定*: 可靠性图(reliability diagram)的出处, 与 Guo et al. (2017) 配套锚定 `validation/tone_validation.py` 校准诊断。
- Cover, T. M., & Thomas, J. A. (2006). *Elements of information theory* (2nd ed.). Wiley-Interscience. https://doi.org/10.1002/047174882X
  - *锚定*: 二元/Shannon 熵的标准教材出处, 锚定 `tone_llms.py:1170`/`codebook.py:728` 的 `compute_prob_score_binary` 与属性熵。
- Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal, 47*(3), 699–725. https://doi.org/10.1002/smj.70023
  - *锚定*: 管理学 LLM 标注的基础指南与告警(误分类系统偏置诊断、prompt 敏感性方差), 锚定 `validation/llms_evaluation.py`/`prompt_sensitivity.py` 与 `tone_llms.py:193` 版本感知缓存可复现性。
- Chiu, I.-C., & Hung, M.-W. (2025). Finance-specific large language models: Advancing sentiment analysis and return prediction with LLaMA 2. *Pacific-Basin Finance Journal, 90*, 102632. https://doi.org/10.1016/j.pacfin.2024.102632
  - *锚定(主题锚)*: 金融领域专用 LLM(LLaMA-2 微调)情感分析与收益预测的近期金融应用, 为 LLM 情感轨提供金融 LLM 主题锚。⚠ 代码 `validation/tone_validation.py:39/51` **误把** Dirichlet 类别偏置诊断(χ² + JS)归于此文(该文无 Dirichlet/χ²/JS)——此为代码误归, 该诊断的真出处应另引(如 Malinin & Gales 2018 Prior Networks; 详见 §七)。
- Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science, 22*(11), 1359–1366. https://doi.org/10.1177/0956797611417632
  - *锚定*: researcher degrees-of-freedom 的出处, 锚定 `validation/decay_sensitivity.py` "固定 3 种衰减形式、不做超参搜索"的研究者自由度纪律。
- Manski, C. F., & Lerman, S. R. (1977). The estimation of choice probabilities from choice based samples. *Econometrica, 45*(8), 1977–1988. https://doi.org/10.2307/1914121
  - *锚定*: choice-based sampling 加权校正的出处, 锚定 `validation/llms_evaluation.py` 分层过采样下的准确率总体重加权。
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
  - *锚定*: Wilson 二项置信区间的出处, 锚定 `validation/dict_coverage.py`/`llms_evaluation.py` 覆盖率/查准率比例 CI(n=1000 样本量论证)。

### 子族 29. 媒体类型构成 / 分歧 / 显著性(`attention_media.py` / `codebook.py`)

项目做法(白话): 媒体不是铁板一块——官方 vs 市场化、深度 vs 转载、报道相关性高低。项目据此构造 `official_media_frac`/`deepdive_media_frac`/`news_salience`/媒体退出稳健性等; 代码均具名。

- Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. *Journal of Financial Economics, 145*(2), 445–463. https://doi.org/10.1016/j.jfineco.2021.08.015
  - *锚定*: 本地报纸退出→公司不端的因果证据, 锚定 `attention_media.py:67` 媒体退出/停刊稳健性(`exc_*`)。
- Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. *Journal of Financial Economics, 135*(2), 445–467. https://doi.org/10.1016/j.jfineco.2019.06.003
  - *锚定*: 报纸关停×公共财政监督, 锚定 `attention_media.py:67` 媒体监督的背景引用。
- Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. *Journal of Accounting Research, 53*(2), 405–459. https://doi.org/10.1111/1475-679X.12071
  - *锚定*: 中国情境官方媒体压制负面信息的政治激励, 锚定 `attention_media.py:1116` `official_media_frac`/`market_media_frac` 官方-市场化对立构念。
- Guest, N. M. (2021). The information role of the media in earnings news. *Journal of Accounting Research, 59*(3), 1021–1076. https://doi.org/10.1111/1475-679X.12349
  - *锚定*: 证明高差异度(深度原创)新闻更长/更可读/更具体/转载更少, 锚定 `attention_media.py:1189` `deepdive_media_frac`(深度分析型媒体原创性)。
- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x
  - *锚定*: bullishness/分歧的信息含量, 锚定 `codebook.py:476` 情感分歧与 subject-relevance 阈值。
- Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. *The Review of Financial Studies, 32*(3), 992–1033. https://doi.org/10.1093/rfs/hhy083
  - *锚定*: 公司特定新闻的相关性/显著性识别, 锚定 `pipeline/filtering/news_salience.py`/`codebook.py:1206` `news_salience`。
- Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. *The Accounting Review, 98*(7), 315–345. https://doi.org/10.2308/TAR-2020-0104
  - *锚定*: 媒体情感与盈余公告的纪律作用, 锚定 `encode.py:267` 媒体权威性加权 MW Tone 的背景构念(媒体情感的可被基本面校正性)。

### 子族 30. 组织理论构念: 实质-象征脱耦 / locus / 协同(`codebook.py` / `encode.py`)

项目做法(白话): P3(实质 vs 象征)、P4(底层 vs 应用 locus)、P5(自研 vs 外部协同)的理论根, 代码均具名了管理学经典。

- Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. *Administrative Science Quarterly, 39*(3), 367–390. https://doi.org/10.2307/2393295
  - *锚定*: **实质 vs 象征脱耦(decoupling)的奠基理论**(采纳≠实施), 是项目 P3 substance/`sub_frac`-`symb_frac` 二元的**核心理论出处**。
- Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. *Administrative Science Quarterly, 43*(1), 127–153. https://doi.org/10.2307/2393593
  - *锚定*: 象征性管理(symbolic management)的延伸出处, 锚定项目象征性叙事产生市场反应的机制。
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. *Academy of Management Journal, 49*(6), 1173–1193. https://doi.org/10.5465/amj.2006.23478255
  - *锚定*: 框架(framing)+脱耦(decoupling)的象征性战略变革管理, 锚定 `codebook.py:827` 象征-实质 `sub_frac` 维度。⚠ 代码注释把本文刊名误标 **ASQ**, 实为 **AMJ**(Fiss-Zajac 确有一篇 ASQ 2004 但是另一文; 详见 §七)。
- Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. *Strategic Management Journal, 31*(3), 306–333. https://doi.org/10.1002/smj.821
  - *锚定*: 创新生态/技术相互依赖, 锚定 `codebook.py:686` `tone_gap_tech_app`(底层 vs 应用 locus)的生态视角。
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. *Strategic Management Journal, 27*(2), 131–150. https://doi.org/10.1002/smj.507
  - *锚定*: 开放式创新 breadth(外部搜索广度), 锚定 `codebook.py:786`/`encode.py:1616` P5 `collab_mode` 外部协同(与既有 Chesbrough 2003 互补)。
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy, 31*(4), 477–492. https://doi.org/10.1016/S0048-7333(01)00120-2
  - *锚定*: 企业间 R&D 合作伙伴的分类学, 锚定 `codebook.py:1301` `collab_mode` partnership 分类。

### 子族 31. 计量 / 信息检索 / 网络方法(`codebook.py` / `fintech_intensity.py` / `network_spillover.py`)

- King, G., & Zeng, L. (2001). Logistic regression in rare events data. *Political Analysis, 9*(2), 137–163. https://doi.org/10.1093/oxfordjournals.pan.a004868
  - *锚定*: rare-events logit(类别失衡校正), 锚定 `codebook.py:535` 稀有事件 DV 的 logit 偏误校正。
- Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization. In *Proceedings of the 19th Annual International ACM SIGIR Conference* (pp. 21–29). ACM. https://doi.org/10.1145/243199.243206
  - *锚定*: pivoted 文档长度归一化, 锚定 `pipeline/filtering/fintech_intensity.py` 强度分的篇幅偏差校正。
- Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. *Social Networks, 32*(3), 245–251. https://doi.org/10.1016/j.socnet.2010.03.006
  - *锚定*: 加权网络节点中心度(广义度/最短路), 锚定 `network_spillover.py:740` `bank_strength_cent`(加权强度中心度)。
- Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. *Proceedings of the National Academy of Sciences, 101*(11), 3747–3752. https://doi.org/10.1073/pnas.0400087101
  - *锚定*: 加权网络架构(含加权聚类/强度), 锚定 `bank_avg_nbr_deg`(加权平均邻居度)。
- Seidman, S. B. (1983). Network structure and minimum degree. *Social Networks, 5*(3), 269–287. https://doi.org/10.1016/0378-8733(83)90028-X
  - *锚定*: k-core/coreness 的出处, 锚定 `bank_coreness`(k-核)。

### 子族 32. 中文锚点(CNKI; 查实-或-标注)

- 胡俊, 李强, 戴嘉诚, & 曾勇. (2024). 基于文本分析的商业银行金融科技测度及赋能效果检验. *中国管理科学, 32*(1), 31–41.
  - *锚定(关键)*: **驱动 stage 12 的 1506 词金融科技关键词词典本身**的学术出处——`pipeline/filtering/news_fintech.py` 的 Aho-Corasick 金科分类词典即源于该文的"基于文本分析的商业银行金融科技测度"。〔多智能体经期刊页 + 英文题名"Textual Analysis-based Measurement of Fintech and Tests of Enabling Effect for Commercial Banks"+ 卷期页 32(1):31-41 核实〕
- 〔**待 CNKI 核实, 未确认, 不作已核验主张**〕 欧阳志刚, & 胡雯华. (2024). 央行沟通公告有助于提升政策利率的传导效率吗？*数量经济技术经济研究, 41*(10), 69–88. 〔代码 `strategic_diff.py:54` 具名此题, 但其 DOI `10.13653/j.cnki.jqte.2024.10.004` 在 doi.org/Crossref **404**、chndoi 报"DOI 号没有注册", 该题名亦零目录命中 → **未能核验**〕
  - 代码 `strategic_diff.py:1142` 内部引用作"相邻期文本连贯性"(`coh_*`)依据; 独立智能体实测其候选 DOI `10.13653/…2024.10.004` 在 doi.org/Crossref **404**、chndoi.org 报"DOI 号没有注册", 候选题名零目录命中 → **未能核验, 保持 flagged**; 论文写作请改引可及替代或如实标代码来源。

---

## 七、操作化透明声明与代码勘误(诚实披露, 非引用缺口)

**(A) 代码注释勘误(本次核验实测, 引用本身正确, 仅代码注释需修)**:
1. `tone_words.py:181` — Pang & Lee (2008) 的 DOI 写成 `10.1561/1500000001`, 解析到**另一篇** Prager (2007) 问答综述; 正确 DOI = `10.1561/1500000011`(差一个尾"1", 典型错位 DOI)。
2. `tone_words.py:184` — Li, Huang & Zhu (2010) 被置于"程度副词权重"块, 但该文主建模 Sentiment-LDA **连词驱动**的局部依赖而非程度副词强化, 更契合"转折连词"块(Kennedy-Inkpen 2006 才是该块正确的程度/强化锚, 仍应留)。
3. `validation/tone_validation.py:39/51` — Chiu & Hung (2025) 被误归为 Dirichlet 类别偏置诊断(χ²+JS)的出处; 该文是金融 LLM 情感/收益预测, **无** Dirichlet/χ²/JS; 该诊断真出处应另引(如 Malinin & Gales 2018 Prior Networks, **本文未将其登记为已核验项, 仅作建议**)。
4. `codebook.py:827` — Fiss & Zajac (2006) 刊名误标 **ASQ**, 实为 **AMJ 49(6):1173-1193**(Fiss-Zajac 另有一篇 ASQ 2004 论文是别篇)。

**(B) 已在代码内被标注为勘误/弃用的引用(一律不收, 如实记录)**: Hales-Kuang-Venkataraman (2011)(numerical_intensity 误标, 已改 Davis-Tama-Sweet 2012) / Platt (1999)(标 NOT USED) / Dahlke (2024)(cognitive proximity disclaimed) / Berger (2022, JFI)(removed) / Jiang (2019) PLS(改 Janis-Fadner)。

**(C) "有构念锚但操作化为项目自定义"项(透明声明, 非缺引用)**: 下列指标的**构念**已被锚定, 但其**具体公式/参数为项目自定义**, 无单一方法出处——论文方法部分应**如实声明为本项目操作化**, 不可硬挂某文献:
- `function_word_ratio`(LIWC Analytic 中文近似)/ `rare_word_ratio` 的 20 分位 jieba 频率切分 / `hard_char_ratio` 的 0.995 常用字覆盖切分(构念锚 Dale-Chall 1948 + 丘心颖等 2016)。
- `num_intensity` = n_numeric / n_sentences 与 `num_intensity_word` 词级分母(构念锚 Davis-Tama-Sweet 2012; 公式自定义)。
- `within_doc_redundancy`(字符 3-gram 自重复)/ `boilerplate_phrase_ratio`(char_wb (4,6)-gram + DF≥0.10 阈值)(构念锚 Dyer-Lang-Stice-Lawrence 2017 / Cazier-Pfeiffer 2016 / Lang-Stice-Lawrence 2015; n-gram 与阈值自定义)。
- `cogn_mean`(TF-IDF char-ngram 余弦均值)(构念锚 Boschma 2005; **TF-IDF 余弦操作化为自定义**, 代码已自我披露)。
- `_RULE_ABLATION` 7 变体 powerset(否定+程度+转折)/ BERT 滑窗置信加权 logit 池化 / cn2arab 中文数字转换 / `cross_media_alpha` 事件窗阈值 — 均为项目自定义算法, 仅构念/部件有锚。

**(D) 未能核验、保持 flagged 的 code-named 引用(决不臆造)**: ① 谢佳松, 樊嘉诚, 林建浩 (2025, 经济研究) — 见 §四; ② 欧阳志刚, 胡雯华 (2024, 数量经济技术经济研究) — 见 §六子族 32。两者论文写作中均应改引可及替代或标"代码内部引用, 待核验"。

---

## 八、合并参考文献总表 · 第二批(36 条已核验, APA 第 7 版, 按第一作者姓氏字母序)

> 与 §五(第一批 28 条)+ 主编 143 + 补编 102 互补不重叠; ouyang_hu (2024) 因未核验**不入此表**。

- Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. *Strategic Management Journal, 31*(3), 306–333. https://doi.org/10.1002/smj.821
- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x
- Barrat, A., Barthélemy, M., Pastor-Satorras, R., & Vespignani, A. (2004). The architecture of complex weighted networks. *Proceedings of the National Academy of Sciences, 101*(11), 3747–3752. https://doi.org/10.1073/pnas.0400087101
- Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. *The Review of Financial Studies, 32*(3), 992–1033. https://doi.org/10.1093/rfs/hhy083
- Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal, 47*(3), 699–725. https://doi.org/10.1002/smj.70023
- Chiu, I.-C., & Hung, M.-W. (2025). Finance-specific large language models: Advancing sentiment analysis and return prediction with LLaMA 2. *Pacific-Basin Finance Journal, 90*, 102632. https://doi.org/10.1016/j.pacfin.2024.102632
- Cover, T. M., & Thomas, J. A. (2006). *Elements of information theory* (2nd ed.). Wiley-Interscience. https://doi.org/10.1002/047174882X
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. *Academy of Management Journal, 49*(6), 1173–1193. https://doi.org/10.5465/amj.2006.23478255
- Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. *Journal of Financial Economics, 135*(2), 445–467. https://doi.org/10.1016/j.jfineco.2019.06.003
- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences, 120*(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
- Guest, N. M. (2021). The information role of the media in earnings news. *Journal of Accounting Research, 59*(3), 1021–1076. https://doi.org/10.1111/1475-679X.12349
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning (ICML)* (PMLR 70, pp. 1321–1330). https://proceedings.mlr.press/v70/guo17a.html
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy, 31*(4), 477–492. https://doi.org/10.1016/S0048-7333(01)00120-2
- Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. *Journal of Financial Economics, 145*(2), 445–463. https://doi.org/10.1016/j.jfineco.2021.08.015
- Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. *The Accounting Review, 98*(7), 315–345. https://doi.org/10.2308/TAR-2020-0104
- Jia, L., Yu, C., & Meng, W. (2009). The effect of negation on sentiment analysis and retrieval effectiveness. In *Proceedings of the 18th ACM Conference on Information and Knowledge Management (CIKM '09)* (pp. 1827–1830). ACM. https://doi.org/10.1145/1645953.1646241
- Kennedy, A., & Inkpen, D. (2006). Sentiment classification of movie reviews using contextual valence shifters. *Computational Intelligence, 22*(2), 110–125. https://doi.org/10.1111/j.1467-8640.2006.00277.x
- King, G., & Zeng, L. (2001). Logistic regression in rare events data. *Political Analysis, 9*(2), 137–163. https://doi.org/10.1093/oxfordjournals.pan.a004868
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. *Strategic Management Journal, 27*(2), 131–150. https://doi.org/10.1002/smj.507
- Li, F., Huang, M., & Zhu, X. (2010). Sentiment analysis with global topics and local dependency. *Proceedings of the AAAI Conference on Artificial Intelligence, 24*(1), 1371–1376. https://doi.org/10.1609/aaai.v24i1.7523
- Liu, B. (2012). Sentiment analysis and opinion mining. *Synthesis Lectures on Human Language Technologies, 5*(1), 1–167. Morgan & Claypool. https://doi.org/10.2200/S00416ED1V01Y201204HLT016
- Manski, C. F., & Lerman, S. R. (1977). The estimation of choice probabilities from choice based samples. *Econometrica, 45*(8), 1977–1988. https://doi.org/10.2307/1914121
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In *Proceedings of the 22nd International Conference on Machine Learning (ICML)* (pp. 625–632). ACM. https://doi.org/10.1145/1102351.1102430
- Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). Node centrality in weighted networks: Generalizing degree and shortest paths. *Social Networks, 32*(3), 245–251. https://doi.org/10.1016/j.socnet.2010.03.006
- Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. *Foundations and Trends in Information Retrieval, 2*(1–2), 1–135. https://doi.org/10.1561/1500000011
- Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. *Journal of Accounting Research, 53*(2), 405–459. https://doi.org/10.1111/1475-679X.12071
- Seidman, S. B. (1983). Network structure and minimum degree. *Social Networks, 5*(3), 269–287. https://doi.org/10.1016/0378-8733(83)90028-X
- Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. *Journal of Econometrics, 228*(2), 221–243. https://doi.org/10.1016/j.jeconom.2020.07.053
- Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science, 22*(11), 1359–1366. https://doi.org/10.1177/0956797611417632
- Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization. In *Proceedings of the 19th Annual International ACM SIGIR Conference* (pp. 21–29). ACM. https://doi.org/10.1145/243199.243206
- Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. *Computational Linguistics, 37*(2), 267–307. https://doi.org/10.1162/COLI_a_00049
- Törnberg, P. (2024). Best practices for text annotation with large language models. *Sociologica, 18*(2), 67–85. https://doi.org/10.6092/issn.1971-8853/19461
- Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. *Administrative Science Quarterly, 39*(3), 367–390. https://doi.org/10.2307/2393295
- Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. *Administrative Science Quarterly, 43*(1), 127–153. https://doi.org/10.2307/2393593
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
- 胡俊, 李强, 戴嘉诚, & 曾勇. (2024). 基于文本分析的商业银行金融科技测度及赋能效果检验. *中国管理科学, 32*(1), 31–41.

---

## 九、使用注意

1. **代码注释旧引用**: 本补编以权威源核验值为准; 代码注释里的卷期/页/DOI 若与本表不符, 以本表为准(尤见 §七 四处代码勘误)。
2. **构念 vs 算法**: Han-Kim-Nanda(2024)锚定金融经纪**构念**, 二分图介数**算法**出处为 Borgatti-Everett/Faust; Chiu-Hung(2025)是金融 LLM 情感**主题锚**, 非 Dirichlet 诊断出处——引用时勿混。
3. **中文文献**: 已核验 3 条(丘心颖等 2016 / 徐巍等 2021 / 胡俊等 2024)可直接引; 未核验 2 条(谢佳松等 2025 / 欧阳志刚-胡雯华 2024)投稿前须 CNKI 最终确认或改引可及替代。
4. **JMLR/JSTOR/PMLR 无 DOI**: Blei(2003)/Dale-Chall(1948)/Guo et al.(2017)用官方稳定页, 非臆造 DOI。
5. **操作化自定义**: §七(C) 所列指标方法部分应**如实声明为本项目操作化**, 不可硬挂单一文献。

---

**全文合计**: 主编 143 + 补编 102 + 本第二补编 **63 条已核验**(第一批 27 + 第二批 36) = **308 条唯一文献锚点**, 覆盖 news_process 管线全部指标计算从"文本→测度→面板→识别→推断→效度验证→网络→空间→战略差异→中文构念"的学术谱系。另 2 条 code-named 中文引用(谢佳松等 2025 / 欧阳志刚-胡雯华 2024)未能核验, 如实 flagged。
