# 文献理论锚点扩充报告 · 第七补编(前沿银企共现面板 · 共现富集度零模型 + 公司侧效度/控制族 + 面板时点纪律专项 · 2024–2026 最新文献优先 · 5 主题桶 · APA 第 7 版 · Crossref/DataCite DOI→标题回比 + 权威元数据逐条回填全核验)

- **日期**: 2026-07-06
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 143 条)、`LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 102 条)、`LITERATURE_ANCHORS_EXPANSION_2026-06-22.md`(第二补编, 63 条)、`LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md`(第三补编, 108 条)、`LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md`(第四补编, 2 条)、`LITERATURE_ANCHORS_SUPPLEMENT_V_2026-07-01.md`(第五补编, 111 条)、`LITERATURE_ANCHORS_SUPPLEMENT_VI_2026-07-06.md`(第六补编, 85 条)之后的 **第七补编**, 八者**合为一套**。前七份已建成 **612 条已核验锚点 / 592 个唯一 doi.org DOI**(全语料 `audit_dois.py` 实测)。
- **本补编专项**: 补齐**前沿「上市公司×年 银企共现媒体报道面板」(v33 计划)**里, 主锚点体系(前七份)与其自带归档(`COMPANY_BANK_COOC_PANEL_PLAN_ARCHIVE_2026-07-04.md` §10, 150 条/137 DOI)**皆未收**的一批方法/指标/时点纪律的学术出处。分两类:
  1. **在用但主体系未锚的活跃统计量** —— **共现富集度双基准判定**(观测共现相对随机独立下期望共现的超代表性; `cooc_hhi` 三轨 · `frac`/`frac_v` · 富集度**均匀基准**与**边际保持基准**双基准敏感性), 及其背后的 **PMI/lift 偏差校正**与**固定边际/度数保持零模型(configuration model)显著性**。此为**真缺口**: 前七份仅锚共现"计数"(Fang–Peress 谱系)与二部投影 backbone(Neal–Neal), **未锚"共现超代表性统计量本身"**。
  2. **前沿面板即将接入的公司侧效度/控制族与面板时点纪律** —— 对应盘上已到位、供**构念效度对照**的三张辅助表(`config/上市公司十大股东.dta` / `上市公司董监高金融机构背景表.dta` / `上市公司向金融机构借款表.dta`)与股东报告期 (c,t) **年末快照**口径。这批是前沿计划 §9.9 明列"**未入包待议 · 贷款表接入后另立计划**"的方法族: 主体系此前零覆盖(实测: 7 文件对股权集中度/大股东/董监高金融背景**基本零锚**), 本补编为其**前置备料**学术出处(用户 2026-07-06 明确认可此四桶范围)。
- **规模**: 5 主题桶并行动态多智能体工作流发现 → 每候选 Crossref/DataCite DOI→标题自核验 + claim-fit 诚实性检验 → 主控**逐条直连 Crossref/DataCite 回填权威元数据**(作者序/年份/卷期/页码/标题, 69/69 零解析失败) → 全语料去重(剔与前七份+前沿归档重叠, 实测仅 1 条重复 Bochkay et al. 2023 已在前沿归档 §10.15, 已剔) = **净增 69 条唯一锚点**, 其中 **2024–2026 者 31 条**(占 45%), 工作论文 3 条(arXiv)。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编经**三道独立核验 + 一道元数据回填**:
  1. 发现层每候选提名前实时 `GET api.crossref.org/works/{DOI}`(arXiv 走 `api.datacite.org`)读回标题自比对; 各桶智能体额外主动弃掉数条错 DOI(如关系借贷桶弃 2 个错解 DOI: `10.1016/j.jfineco.2017.09.005` 实解析到 Bali/Brown/Tang、`10.1016/j.jfineco.2015.05.001` 实解析到 Fama–French, 均以正确 DOI 替换后重核), 均已在源头剔除;
  2. 主控**逐条直连 Crossref/DataCite 回填权威书目元数据**(作者序/年份/卷期/页码/标题), 据此撰写 APA —— 此步对 69 条**零解析失败、零标题不符、零作者字段错乱**, 并将若干条年份对齐 Crossref 回读年(卷期年优先, 见各条);
  3. 全语料本地核验(决定性闸): `scripts/audit/audit_dois.py`(本补编轮已将前沿归档并入 FILES)直连 Crossref/DataCite, 对全套唯一 DOI 逐条 DOI→标题逐字回比 + 年份核验;
  4. 元数据回填同时**将前沿归档 137 DOI 纳入主机械闸**并全量复核: 归档 doi.org DOI **零新增 flag**(仅既有 3 条 benign 不变)。
- **合计**: 612(前七份)+ **69(本补编净增)** = **681 条**唯一文献锚点; 全语料 `audit_dois.py` 实测唯一 doi.org DOI = **671 个**(前七份 592 + 前沿归档并入净增 10 + 本补编 69)。

---

## 〇、白话导读

**这份补的是什么**: 前七份把项目主线(到 v3.15.0 及 07-06 全部已提交指标)配齐了(612 条)。但项目正在搭一个**新面板**——"哪家上市公司和哪家银行在同一篇新闻里一起出现"的**银企共现面板**。这个面板有两样东西是前面没配学术出处的: ① 一个**统计量**: 两家一起出现的次数"比随机情况下该出现的次数高多少"(富集度), 项目用"均匀"和"保持各自出现总数不变"两把尺子去量——这需要网络科学里"零模型/固定边际随机化/PMI 显著性"那一套出处; ② 一批**配套的公司侧数据**(十大股东、董监高有没有银行背景、向银行借了多少钱)和**打面板时点的纪律**(用"当年年末那一版"的股东名单, 不能把以后才披露的信息塞进当年)——这些是给面板做"真假关系对照"用的, 数据已经到盘上了, 出处得先备好。这份就专门补这两类。

**和"严禁自我生成"的关系**: 每一条**都不是编的**。发现时智能体先查一遍官方接口, 之后主控又**逐条直连 Crossref/DataCite 把作者、年份、卷期、页码、标题原样拉回来**再写 APA(不信智能体的转写)。这次 69 条**一条没查不着、一条标题没对不上、一条作者没乱**(不像第六补编当场抓出 2 条坏的)。最后本地脚本再全量复核一遍——顺便把前沿那份自带的 137 条也第一次拉进这个总闸门, 零新增红灯。每条后面的"回读标题"就是接口实际回读值。

**怎么用**: 写论文/codebook 时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。**勿沿用代码注释里的旧版引用**。

**一句话铁律提醒**: 富集度的两把尺子(均匀基准 vs 边际保持基准)是**互为稳健性、不分主次的敏感性检验**——各自 just-identified 并排, **严禁混进同一 over-identified Hansen J**。这条与代码里的铁律一致, 引用时须在方法节写明。前沿计划的贷款/股东/董监高效度对照仍属"另立计划待议", 本补编只**前置备料出处**, 不代表这些变量已进任何回归。

---

## 一、5 主题桶 × 新增已核验锚点(2024–2026 优先; 〔〕内为回读标题)

### 七补-1. 共现富集度 / 超代表性统计量 / 固定边际零模型 / PMI 显著性 (银企共现 `cooc_hhi` 三轨 · 富集度双基准: 均匀 vs 边际保持)

> 净增 14 条(其中 2024–2026 者 7 条)。**真缺口**: 前七份仅锚共现"计数"(Fang–Peress)与二部 backbone(Neal–Neal), 未锚"共现是否显著超出偶然"这一**统计量本身**。⚠ 铁律: 均匀基准 vs 边际保持基准两把尺子互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

- Tumminello, M., Miccichè, S., Lillo, F., Piilo, J., & Mantegna, R. N. (2011). Statistically validated networks in bipartite complex systems. *PLoS ONE, 6*(3), Article e17994. https://doi.org/10.1371/journal.pone.0017994
  - *锚定* — **边际保持基准的 method-origin**: 对二部(此处=公司-银行)投影每条共现边, 在**固定双侧度数**下用超几何分布算 p 值, 显式区分"系统异质性造成的偶然共现"与"真实超代表关联" —— 正是本项目"边际保持基准判富集度"的原型。注: 原文逐边显著性验证网络, 本项目取其零模型作富集度基准之一, 非同一交付物。
  - 〔Crossref 回读标题: Statistically Validated Networks in Bipartite Complex Systems〕
- Fosdick, B. K., Larremore, D. B., Nishimura, J., & Ugander, J. (2018). Configuring random graph models with fixed degree sequences. *SIAM Review, 60*(2), 315–355. https://doi.org/10.1137/16M1087175
  - *锚定* — **度数保持随机化(configuration model)的权威统一处理**: 系统梳理固定度数序列下的 8 种 stub-matching/vertex-labeled 变体与 double-edge-swap MCMC, 为"随机独立下期望共现"提供严谨零模型基座。注: 一般图零模型理论, 非共现应用, 提供方法基座。
  - 〔Crossref 回读标题: Configuring Random Graph Models with Fixed Degree Sequences〕
- Casiraghi, G., & Nanumyan, V. (2021). Configuration models as an urn problem. *Scientific Reports, 11*(1), Article 13416. https://doi.org/10.1038/s41598-021-92519-y
  - *锚定* — 把 configuration model 重构为 urn/广义超几何抽样, 给出固定边际下**期望共现的闭式**与偏差校正, 直接支撑"观测/期望"富集比的**解析推断**(免纯蒙特卡洛)。注: 通用网络 ensemble, 需迁移到银企二部结构。
  - 〔Crossref 回读标题: Configuration models as an urn problem〕
- Neal, Z. P., Domagalski, R., & Sagan, B. (2021). Comparing alternatives to the fixed degree sequence model for extracting the backbone of bipartite projections. *Scientific Reports, 11*(1), Article 23929. https://doi.org/10.1038/s41598-021-03238-3
  - *锚定* — 直击本项目"边际保持基准"的选型: 系统比较 FDSM(固定度数序列)与四种放松版(fixed-fill/fixed-row/fixed-column/SDSM)对二部共现投影显著性判定的差异, 并给出何时可用解析近似替代置换。注: 面向 backbone 抽取而非富集度报数, 迁移可用。
  - 〔Crossref 回读标题: Comparing alternatives to the fixed degree sequence model for extracting the backbone of bipartite projections〕
- Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022). Meta-validation of bipartite network projections. *Communications Physics, 5*(1), Article 76. https://doi.org/10.1038/s42005-022-00856-9
  - *锚定* — **与本项目"双基准敏感性"高度同构**: 证明不同 configuration-model 形式(约束加在哪一侧/如何加)在同一显著性阈值下结论分叉, 提出 meta-validation 选取"信号最强"的模型专属阈值 —— 恰是"均匀 vs 边际保持两把尺子并报"的方法学正当性。注: 物理网络语境, 迁移到银企二部。
  - 〔Crossref 回读标题: Meta-validation of bipartite network projections〕
- Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. *Science Advances, 8*(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
  - *锚定* — **lift/Jaccard 偏差校正的 method-origin**: 论证传统共现指数(Jaccard/lift)无一致估计目标且受边际(prevalence)污染, 提出关联参数 α 及其**完整零分布**(给定行列和的期望共现)与 MLE。注: 生态/相似度语境, 本项目可借其作 lift 的偏差校正替代。
  - 〔Crossref 回读标题: A better index for analysis of co-occurrence and similarity〕
- Williams, C. K. I. (2022). On suspicious coincidences and pointwise mutual information. *Neural Computation, 34*(10), 2037–2046. https://doi.org/10.1162/neco_a_01533
  - *锚定* — 分析 PMI 作"可疑共现(suspicious coincidence)"检测量的性质, 剖其对边际的敏感性(稀疏事件被抬分)——支撑"为何 PMI 型富集须做低频校正"。注: 概念性质分析, 非给定语料的显著性程序。
  - 〔Crossref 回读标题: On Suspicious Coincidences and Pointwise Mutual Information〕
- 【2024–2026】Czyż, P., Grabowski, F., Vogt, J. E., Beerenwinkel, N., & Marx, A. (2024). On the properties and estimation of pointwise mutual information profiles. *Transactions on Machine Learning Research*. https://doi.org/10.48550/arXiv.2310.10240
  - *锚定* — 研究 PMI *profile*(逐点互信息的分布, 其期望即 MI)的解析性质与蒙特卡洛估计, 为 PMI 类关联量的**统计估计/不确定性**提供理论工具。注: TMLR 录用版(2024), 可解析 DOI 指向 arXiv 存档(DataCite 回读年 2023); 面向 MI 估计器评测, 非共现显著性程序。
  - 〔DataCite 回读标题: On the Properties and Estimation of Pointwise Mutual Information Profiles〕
- 【2024–2026】Mainali, K. P., & Slud, E. (2025). CooccurrenceAffinity: An R package for computing a novel metric of affinity in co-occurrence data that corrects for pervasive errors in traditional indices. *PLOS ONE, 20*(1), Article e0316650. https://doi.org/10.1371/journal.pone.0316650
  - *锚定* — 上条 α 关联指标的**落地实现**与显著性流程(MLE + 置信区间 + 与传统指数对照), 供复现"边际校正的共现关联"。注: 软件/操作层。
  - 〔Crossref 回读标题: CooccurrenceAffinity: An R package for computing a novel metric of affinity in co-occurrence data that corrects for pervasive errors in traditional indices〕
- 【2024–2026】Yassin, A., Cherifi, H., Seba, H., & Togni, O. (2025). Backbone extraction through statistical edge filtering: A comparative study. *PLOS ONE, 20*(1), Article e0316141. https://doi.org/10.1371/journal.pone.0316141
  - *锚定* — **2025 决策证据**: 系统横比 7 种基于零模型的显著边过滤(Disparity/Enhanced Configuration Model/Marginal Likelihood/Noise-Corrected 等)对高权重/高度数边的选择偏好, 为"选哪种边际保持零模型"提供近期依据。注: 一般网络 backboning, 迁移可用。
  - 〔Crossref 回读标题: Backbone extraction through statistical edge filtering: A comparative study〕
- 【2024–2026】Kirkley, A. (2025). Fast nonparametric inference of network backbones for weighted graph sparsification. *Physical Review X, 15*(3), Article 031013. https://doi.org/10.1103/4pg6-mtmt
  - *锚定* — 用最小描述长度(MDL)**非参**推断哪些加权边构成"真信号"骨架, 是显著性阈值/零模型 backboning 的信息论替代, 可作富集判定的**稳健性对照臂**。注: 不走 p 值零模型路线, 供方法多元化对照。
  - 〔Crossref 回读标题: Fast Nonparametric Inference of Network Backbones for Weighted Graph Sparsification〕
- 【2024–2026】Amancio, D. R., Machicao, J., & Quispe, L. V. C. (2025). Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis. *PLOS ONE, 20*(7), Article e0327421. https://doi.org/10.1371/journal.pone.0327421
  - *锚定* — 从文本构造共现网络时用词向量补足"应共现却未共现"的边, 并做统计分析区分**真实关联 vs 稀疏噪声** —— 呼应"从新闻共现区分真实/偶然银企关联"。注: 词-词共现而非企业-银行, 方法可迁移。
  - 〔Crossref 回读标题: Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis〕
- 【2024–2026】McCauley, T., & Pracht, E. B. (2026). Interpreting the statistical significance of pointwise mutual information using probability models of collocation. *Journal of Quantitative Linguistics*. Advance online publication. https://doi.org/10.1080/09296174.2025.2611604
  - *锚定* — **最贴合"PMI 显著性化"子桶**: 在二项/泊松搭配概率模型下推导 PMI 统计量的**可检验 p 值**, 治其对低频共现的过评偏差。注: 语言学搭配语境, 迁移到银企共现即得显著性化 PMI。
  - 〔Crossref 回读标题: Interpreting the Statistical Significance of Pointwise Mutual Information Using Probability Models of Collocation〕
- 【2024–2026】Lotito, Q. F., Vendramini, A., Montresor, A., & Battiston, F. (2026). The microscale organization of directed hypergraphs. *Communications Physics, 9*(1), Article 43. https://doi.org/10.1038/s42005-025-02472-9
  - *锚定* — 用 configuration-model 零模型判定有向超图中 motif/模式是否显著超偶然, 是"固定边际随机化判显著共现"在**高阶(多实体同现)**结构上的最新扩展 —— 若把"多家银行同篇共现"视作高阶超边即直接对接。注: 高阶超图 motif, 非二部富集比。
  - 〔Crossref 回读标题: The microscale organization of directed hypergraphs〕

### 七补-2. 股权集中度 / 大股东监督 / 股权制衡 (前沿面板公司侧效度/控制: `上市公司十大股东.dta`)

> 净增 15 条(其中 2024–2026 者 10 条)。前沿面板"另立计划"备料; 主体系此前对该族**基本零锚**。⚠ 前置备料出处, 不代表已进任何回归。

- Demsetz, H., & Lehn, K. (1985). The structure of corporate ownership: Causes and consequences. *Journal of Political Economy, 93*(6), 1155–1177. https://doi.org/10.1086/261354
  - *锚定* — **股权 Herfindahl / 股权集中度测度的 method-origin**(前 5、前 20 大股东持股平方和), 本项目股权集中度构造直接溯此。注: 奠基, 非近期。
  - 〔Crossref 回读标题: The Structure of Corporate Ownership: Causes and Consequences〕
- Shleifer, A., & Vishny, R. W. (1986). Large shareholders and corporate control. *Journal of Political Economy, 94*(3, Part 1), 461–488. https://doi.org/10.1086/261385
  - *锚定* — **大股东监督(blockholder monitoring)构念的奠基文献**, 支撑"大股东/股权制衡"变量的理论正当性。注: 奠基, 非近期。
  - 〔Crossref 回读标题: Large Shareholders and Corporate Control〕
- Choi, H., Kim, J. H., Suh, J., & Yu, S. (2023). Ownership concentration and financial policy of China's listed firms. *China Economic Review, 79*, Article 101973. https://doi.org/10.1016/j.chieco.2023.101973
  - *锚定* — **最贴合本桶**: 股权集中度→企业融资/负债政策的直接中国 A 股证据。注: DV 为财务政策。
  - 〔Crossref 回读标题: Ownership concentration and financial policy of China's listed firms〕
- Cai, G., Hsu, P.-H., Xu, X., Zhou, T., & Zhu, Y. (2023). The bright and dark sides of minority shareholder protection: Evidence from the separate vote counts disclosure rule in China. *Pacific-Basin Finance Journal, 82*, Article 102185. https://doi.org/10.1016/j.pacfin.2023.102185
  - *锚定* — 中小股东保护/股权制衡与信息披露规则的双面效应(中国制度冲击)。注: 制度冲击视角, 非连续股权集中度量。
  - 〔Crossref 回读标题: The bright and dark sides of minority shareholder protection: Evidence from the separate vote counts disclosure rule in China〕
- Xiao, Q. (2023). State equity participation and financing constraints of private enterprises in China: Based on the competitive pressure perspective. *PLOS ONE, 18*(11), Article e0292817. https://doi.org/10.1371/journal.pone.0292817
  - *锚定* — 中国 A 股**国有 vs 民营股权结构**(国有参股)→民企融资约束, 直击"中国股权结构异质性"控制。注: 处理变量为国有参股。
  - 〔Crossref 回读标题: State equity participation and financing constraints of private enterprises in China: Based on the competitive pressure perspective〕
- 【2024–2026】Ji, J., Sun, H., & Xu, H. (2024). Multiple large shareholders, blockholder trading and stock price crash risk. *European Financial Management, 30*(3), 1344–1384. https://doi.org/10.1111/eufm.12446
  - *锚定* — **multiple large shareholders / blockholders → 信息环境**(崩盘风险)的直接证据, 直击"多个大股东/股权制衡"。注: 结果变量为股价崩盘。
  - 〔Crossref 回读标题: Multiple large shareholders, blockholder trading and stock price crash risk〕
- 【2024–2026】Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. *Accounting & Finance, 64*(S1), 5107–5131. https://doi.org/10.1111/acfi.13328
  - *锚定* — 中国**媒体报道**与企业信息披露口径的关联, 为"公司治理/股权→媒体报道"因变量侧提供语境。注: analogy, 自变量非股权集中度。
  - 〔Crossref 回读标题: Media coverage and disclosure of short-termism tone: Evidence from China〕
- 【2024–2026】Bishwas, P. C., & Hossain, M. S. (2025). Does ownership concentration have an impact on financial performance of firms? *Future Business Journal, 11*(1), Article 86. https://doi.org/10.1186/s43093-025-00491-0
  - *锚定* — 股权集中度→公司绩效的近期实证, 供股权集中度作控制/效度变量的**一般性支撑**。注: analogy, 样本非中国 A 股。
  - 〔Crossref 回读标题: Does ownership concentration have an impact on financial performance of firms?〕
- 【2024–2026】Huang, L., Ying, Q., & Han, M. (2025). Can minority shareholders' online voice restrain controlling shareholders' tunneling? *Corporate Governance: An International Review, 33*(4), 850–872. https://doi.org/10.1111/corg.12628
  - *锚定* — 控股股东掏空(tunneling)与股权制衡/外部监督(散户网络舆论), 契合"大股东监督/股权制衡 + 信息环境"。注: 监督来源为散户舆论。
  - 〔Crossref 回读标题: Can Minority Shareholders' Online Voice Restrain Controlling Shareholders' Tunneling?〕
- 【2024–2026】Xu, J., & Luo, Q. (2025). Controlling shareholder equity pledging, financing constraints, and corporate social responsibility. *Finance Research Letters, 76*, Article 106996. https://doi.org/10.1016/j.frl.2025.106996
  - *锚定* — 控股股东行为→融资约束的中国证据, 契合"控股股东/大股东→公司融资"。注: 处理变量为股权质押。
  - 〔Crossref 回读标题: Controlling shareholder equity pledging, financing constraints, and corporate social responsibility〕
- 【2024–2026】Wang, L., Wang, X., & Xiong, X. (2025). The ultimate controlling shareholder's motivation for equity pledge in China – "financing demands" or "interest encroachment". *Economic Analysis and Policy, 88*, 1131–1164. https://doi.org/10.1016/j.eap.2025.10.019
  - *锚定* — 终极控股股东的融资需求 vs 利益侵占动机, 契合"控股股东监督/掏空 + 融资"。注: 焦点为质押动机机制。
  - 〔Crossref 回读标题: The ultimate controlling shareholder's motivation for equity pledge in China – "financing demands" or "interest encroachment"〕
- 【2024–2026】Zheng, Y. (2025). Ownership concentration and independent director effectiveness: Governance challenges under China's new company law. *China Economic Review, 93*, Article 102474. https://doi.org/10.1016/j.chieco.2025.102474
  - *锚定* — 股权集中度作核心自变量, 度量其对独立董事监督有效性的抑制(中国新公司法语境)。注: 本项目作公司层控制/效度而非结果变量。
  - 〔Crossref 回读标题: Ownership concentration and independent director effectiveness: Governance challenges under China's new company law〕
- 【2024–2026】Hua, S., & Ji, Z. (2025). Ownership structure, power separation and the supervisory effectiveness of independent director system. *China Economic Review, 94*, Article 102560. https://doi.org/10.1016/j.chieco.2025.102560
  - *锚定* — 中国 A 股股权结构与控制权分离的公司治理测度。注: 聚焦独董监督, 不涉媒体/信息环境。
  - 〔Crossref 回读标题: Ownership structure, power separation and the supervisory effectiveness of independent director system〕
- 【2024–2026】Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. *Pacific-Basin Finance Journal, 89*, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
  - *锚定* — 股权集中度→企业信息披露真实性(greenwashing)的多主体视角(中国), 契合"股权集中度→信息披露/信息环境"。注: 结果为 ESG 披露质量。
  - 〔Crossref 回读标题: Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective〕
- 【2024–2026】Wang, Y., Zhang, X., Walker, T., & Liedtke, G. (2026). Institutional ownership and bond pricing: Evidence from China. *Emerging Markets Review, 70*, Article 101396. https://doi.org/10.1016/j.ememar.2025.101396
  - *锚定* — 机构/大股东持股→企业债务定价的中国证据, 呼应"股权结构→企业融资成本"。注: 测度对象为债券市场定价。
  - 〔Crossref 回读标题: Institutional ownership and bond pricing: Evidence from China〕

### 七补-3. 董监高金融机构背景 / 银行家董事 / 董事联结 (前沿面板公司侧效度/控制: `董监高金融机构背景表.dta`)

> 净增 15 条(其中 2024–2026 者 8 条, 含 5 条中国"高管金融背景"直接构念锚 + JF 顶刊董事联结)。前沿面板"另立计划"备料; 主体系此前仅 1 条 Robins–Alexander(2004, 董事联结网络结构)边缘覆盖。

- Kroszner, R. S., & Strahan, P. E. (2001). Bankers on boards: Monitoring, conflicts of interest, and lender liability. *Journal of Financial Economics, 62*(3), 415–452. https://doi.org/10.1016/S0304-405X(01)00082-4
  - *锚定* — **"银行家进入企业董事会"研究的 method-origin**, 界定监督/利益冲突/贷款人责任机制。注: 奠基, 美国样本。
  - 〔Crossref 回读标题: Bankers on boards:(Crossref 截断; 全名含 monitoring, conflicts of interest, and lender liability)〕
- Güner, A. B., Malmendier, U., & Tate, G. (2008). Financial expertise of directors. *Journal of Financial Economics, 88*(2), 323–354. https://doi.org/10.1016/j.jfineco.2007.05.009
  - *锚定* — **金融专家/银行家董事影响企业融资的奠基文献**(银行家董事→更大贷款额, 但仅利于非受约束企业)。注: 经典 method-origin。
  - 〔Crossref 回读标题: Financial expertise of directors〕
- Dittmann, I., Maug, E., & Schneider, C. (2010). Bankers on the boards of German firms: What they do, what they are worth, and why they are (still) there. *Review of Finance, 14*(1), 35–71. https://doi.org/10.1093/rof/rfp007
  - *锚定* — 银行家出任企业董事的角色/价值/关系型借贷的经典跨国证据。注: method-origin, 德国样本; Crossref published 字段读作 2009, 卷 14 期 1 通用引 2010。
  - 〔Crossref 回读标题: Bankers on the Boards of German Firms: What They Do, What They Are Worth, and Why They Are (Still) There〕
- Sisli-Ciamarra, E. (2012). Monitoring by affiliated bankers on board of directors: Evidence from corporate financing outcomes. *Financial Management, 41*(3), 665–702. https://doi.org/10.1111/j.1755-053X.2012.01191.x
  - *锚定* — **关联银行家进入董事会与企业融资结果的经典识别框架**(affiliated vs unaffiliated 口径的方法学锚)。注: 美国样本。
  - 〔Crossref 回读标题: Monitoring by Affiliated Bankers on Board of Directors: Evidence from Corporate Financing Outcomes〕
- Xia, C., Zhang, X., Cao, C., & Xu, N. (2019). Independent director connectedness in China: An examination of the trade credit financing hypothesis. *International Review of Economics & Finance, 63*, 209–225. https://doi.org/10.1016/j.iref.2018.09.010
  - *锚定* — **中国**独立董事网络连结→企业融资可得性, 董事关联资本作融资渠道。注: 融资为商业信用而非银行贷款。
  - 〔Crossref 回读标题: Independent director connectedness in China: An examination of the trade credit financing hypothesis〕
- Haw, I.-M., Song, B. Y., Tan, W., & Wang, W. (2021). Bankruptcy, overlapping directors, and bank loan pricing. *Journal of Corporate Finance, 71*, Article 102097. https://doi.org/10.1016/j.jcorpfin.2021.102097
  - *锚定* — 企业与银行间**重叠董事→银行贷款定价**, 直击董事联结→贷款成本。注: 情境限定破产/困境企业。
  - 〔Crossref 回读标题: Bankruptcy, overlapping directors, and bank loan pricing〕
- Togan Egrican, A. (2021). Overlapping board connections with banker directors and corporate loan terms: Evidence from syndicated loans. *Global Finance Journal, 50*, Article 100672. https://doi.org/10.1016/j.gfj.2021.100672
  - *锚定* — **银行家董事的重叠董事会连结→企业贷款条款**, 与"董事联结连接企业与银行→借贷"几乎逐字契合。注: 银团贷款、非中国。
  - 〔Crossref 回读标题: Overlapping board connections with banker directors and corporate loan terms: Evidence from syndicated loans〕
- 【2024–2026】Even-Tov, O., Li, X., Wang, H., & Williams, C. (2024). The importance of individual-pair lending relationships. *Review of Accounting Studies, 29*(4), 3907–3945. https://doi.org/10.1007/s11142-023-09782-9
  - *锚定* — 借款企业高管个人与信贷员的"人-人"关系降低借款成本(7–13bp)——正是"高管金融关联→关系型借贷"机制。注: 关系载体为高管-信贷员配对而非高管本人银行从业背景。
  - 〔Crossref 回读标题: The importance of individual-pair lending relationships〕
- 【2024–2026】Xie, L., Liu, Y., & Jiang, T. (2024). Executives with business education background and cost of debt financing: Evidence from China. *International Review of Economics & Finance, 90*, 283–296. https://doi.org/10.1016/j.iref.2023.12.002
  - *锚定* — 中国高管背景→债务融资成本的直接证据, 口径可迁移到"董监高金融背景→融资成本"。注: 背景变量为商科教育而非金融机构从业, fit 略弱。
  - 〔Crossref 回读标题: Executives with business education background and cost of debt financing: Evidence from China〕
- 【2024–2026】Barone, G., Schivardi, F., & Sette, E. (2025). Interlocking directorates and competition in banking. *The Journal of Finance, 80*(4), 1963–2016. https://doi.org/10.1111/jofi.13464
  - *锚定* — **顶刊(JF)近证**: interlocking directorates 与银行竞争/贷款利率。注: 焦点为银行间董事联结与竞争, 非"企业-银行"董事联结, 作 interlocking-directorate 主题权威近锚。
  - 〔Crossref 回读标题: Interlocking Directorates and Competition in Banking〕
- 【2024–2026】Wang, J., Li, H., Jia, V., & Wang, H. (2026). Affiliated banker directors and firm mergers and acquisitions. *Applied Economics, 58*(21), 4023–4036. https://doi.org/10.1080/00036846.2025.2491793
  - *锚定* — 直接测度"**关联银行家董事**(affiliated banker directors)"对企业行为的影响, 与"银行家出任企业董事"高度契合。注: 结果变量为并购; 卷 58 期 21 对应 2026 印刷年。
  - 〔Crossref 回读标题: Affiliated banker directors and firm mergers and acquisitions〕
- 【2024–2026】Li, M., & Kong, L. (2024). Executives with financial backgrounds and corporate social responsibility: Evidence from China. *Finance Research Letters, 61*, Article 105054. https://doi.org/10.1016/j.frl.2024.105054
  - *锚定* — **中国"有金融背景高管"构念的直接操作化**, 变量效度锚(董监高金融背景表的直接效度参照)。注: DV 为 CSR。
  - 〔Crossref 回读标题: Executives with financial backgrounds and corporate social responsibility: Evidence from China〕
- 【2024–2026】Sun, T., Xie, Z., Song, Y., & Lu, M. (2025). Executives' financial background, corporate financialization and corporate innovation. *International Review of Financial Analysis, 106*, Article 104580. https://doi.org/10.1016/j.irfa.2025.104580
  - *锚定* — "**高管金融背景**"构念直接用于中国上市公司, 效度/测度锚。注: DV 为金融化与创新, 非银企贷款。
  - 〔Crossref 回读标题: Executives' financial background, corporate financialization and corporate innovation〕
- 【2024–2026】Xu, Y., & Shi, Q. (2026). Executive financial background and corporate digital transformation: Empirical evidence from China. *Applied Economics Letters, 33*(10), 1653–1661. https://doi.org/10.1080/13504851.2024.2449540
  - *锚定* — 同一"**高管金融背景**"构念在中国样本的构造与测度锚。注: DV 为数字化转型; 卷 33 期 10 对应 2026 印刷年(online 2024)。
  - 〔Crossref 回读标题: Executive financial background and corporate digital transformation: empirical evidence from China〕
- 【2024–2026】Xing, J., Wu, Q., Yuan, H., & Xing, Z. (2026). Executive financial background, corporate ESG performance, and carbon performance. *International Review of Financial Analysis, 109*, Article 104821. https://doi.org/10.1016/j.irfa.2025.104821
  - *锚定* — 直接以"**高管金融背景**(executive financial background)"为中国上市公司自变量构念 —— 正是"董监高金融机构背景"变量的效度锚。注: DV 为 ESG/碳绩效, 非银企贷款。
  - 〔Crossref 回读标题: Executive financial background, corporate ESG performance, and carbon performance〕

### 七补-4. 面板时点纪律 / point-in-time / as-of 快照 / 幸存者偏误 (前沿面板股东报告期 (c,t) 年末快照口径)

> 净增 10 条(其中 2024–2026 者 2 条)。构念: 用"当年年末那一版"的时点数据编面板, 严避未来才披露信息混入当期。注: 本桶为**面板数据构造侧**方法学, 与前七份已有的 **LLM 侧前视污染族**(Levy 2026 / Glasserman–Lin 2024 / Benhenda 2026)正交、不重复。

- Banz, R. W., & Breen, W. J. (1986). Sample-dependent results using accounting and market data: Some evidence. *The Journal of Finance, 41*(4), 779–793. https://doi.org/10.1111/j.1540-6261.1986.tb04548.x
  - *锚定* — **最贴近本桶的 method-origin**: 首次系统论证用标准 Compustat 会计数据会引入 look-ahead bias 与 ex-post-selection bias, 并给出缓解方案 —— 正是"as-reported vs restated / 回填前视"命门。注: 年代久远但几乎正中面板会计-市场数据前视口径。
  - 〔Crossref 回读标题: Sample-Dependent Results Using Accounting and Market Data: Some Evidence〕
- Brown, S. J., Goetzmann, W., Ibbotson, R. G., & Ross, S. A. (1992). Survivorship bias in performance studies. *The Review of Financial Studies, 5*(4), 553–580. https://doi.org/10.1093/rfs/5.4.553
  - *锚定* — **幸存偏误的方法奠基之一**: 证明被幸存截断的样本会制造虚假可预测性/波动率-收益关系。注: 业绩研究一般性, 作 method-origin。
  - 〔Crossref 回读标题: Survivorship Bias in Performance Studies〕
- Kothari, S. P., Shanken, J., & Sloan, R. G. (1995). Another look at the cross-section of expected stock returns. *The Journal of Finance, 50*(1), 185–224. https://doi.org/10.1111/j.1540-6261.1995.tb05171.x
  - *锚定* — **Compustat 回填导致幸存偏误的经典证据**: 论证 book-to-market 溢价部分源于事后补录高 BE/ME 幸存困境公司, 警示回填/幸存污染。注: 主题为横截面定价检验。
  - 〔Crossref 回读标题: Another Look at the Cross-Section of Expected Stock Returns〕
- Elton, E. J., Gruber, M. J., & Blake, C. R. (1996). Survivor bias and mutual fund performance. *The Review of Financial Studies, 9*(4), 1097–1120. https://doi.org/10.1093/rfs/9.4.1097
  - *锚定* — 用全样本追踪(含并购退出)量化幸存偏误(约年化 1.4% 上偏), 支撑"须以全样本 as-of 追踪防幸存污染"。注: 基金业绩语境, 原理同构。
  - 〔Crossref 回读标题: Survivor Bias and Mutual Fund Performance〕
- Croushore, D., & Stark, T. (2001). A real-time data set for macroeconomists. *Journal of Econometrics, 105*(1), 111–130. https://doi.org/10.1016/S0304-4076(01)00072-0
  - *锚定* — **vintage / real-time(as-reported vs restated)数据方法奠基**: 按季 vintage 快照记录"当时可得"的数据, 是 point-in-time/时点对齐、避免用修订后数据前视的经典范式 —— 与本项目"股东报告期 (c,t) 年末快照"同理同源。注: 宏观时序而非公司会计面板。
  - 〔Crossref 回读标题: A real-time data set for macroeconomists〕
- Sengupta, P. (2004). Disclosure timing: Determinants of quarterly earnings release dates. *Journal of Accounting and Public Policy, 23*(6), 457–482. https://doi.org/10.1016/j.jaccpubpol.2004.10.001
  - *锚定* — **reporting lag / 披露时点**: 实证季度盈余披露日期的决定因素, 直接支撑"用披露时点而非报告期打面板时间戳"的滞后校准。注: 焦点为披露日决定因素, 面板构造是下游含义。
  - 〔Crossref 回读标题: Disclosure timing: Determinants of quarterly earnings release dates〕
- Linnainmaa, J. T., & Roberts, M. R. (2018). The history of the cross-section of stock returns. *The Review of Financial Studies, 31*(7), 2606–2649. https://doi.org/10.1093/rfs/hhy030
  - *锚定* — 用二十世纪外样本(前推/后推)证明多数会计类异象是 data-snooping 产物, 警示样本内构造的幸存/前视风险。注: 论点为异象稳健性, as-of-date 是其暴露机制之一。
  - 〔Crossref 回读标题: The History of the Cross-Section of Stock Returns〕
- Chen, A. Y., & Zimmermann, T. (2022). Open source cross-sectional asset pricing. *Critical Finance Review, 11*(2), 207–264. https://doi.org/10.1561/104.00000112
  - *锚定* — 可复现的 point-in-time 数据构造纪律: 公开数据/代码复刻 319 个横截面预测变量, 强调用可得时点信息避免 look-ahead。注: 侧重复现性/预测变量库, 时点纪律是其贯穿约束。
  - 〔Crossref 回读标题: Open Source Cross-Sectional Asset Pricing〕
- 【2024–2026】Muhammad, T. (2026). *Temporal coverage bias in financial panel data: A coverage-aware structuring framework with evidence from the Dhaka Stock Exchange* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2603.20237
  - *锚定* — **正面命中**: 形式化定义"时间覆盖偏误"(异质上市/存续区间在日历对齐时被忽略所致的系统性失真), 明确与 survivorship/look-ahead 相区分, 直指面板日历对齐口径。注: arXiv preprint(未评审), 案例为孟加拉股市, 框架可迁移。
  - 〔DataCite 回读标题: Temporal Coverage Bias in Financial Panel Data: A Coverage-Aware Structuring Framework with Evidence from the Dhaka Stock Exchange〕
- 【2024–2026】Zhang, F., Li, Z., Peng, S., & Chen, Y. (2026). *When alpha disappears: A one-switch benchmark for decision-time leakage in financial backtests* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2605.23959
  - *锚定* — 命中"决策时点信息泄漏(decision-time leakage)"(把当期不可得信息混入建模/回测的时点对齐问题), 提供单开关基准量化其虚增 alpha。注: arXiv preprint; 站在回测/信号构造侧而非纯会计面板时间戳, 属邻接。
  - 〔DataCite 回读标题: When Alpha Disappears: A One-Switch Benchmark for Decision-Time Leakage in Financial Backtests〕

### 七补-5. 关系型借贷 / 银企匹配 / 共现作关系代理 (前沿面板 `向金融机构借款表.dta` 效度对照 + 共现→关系效度)

> 净增 15 条(其中 2024–2026 者 4 条; 已剔与前沿归档重叠 1 条 Bochkay et al. 2023)。前沿计划 §9.9 明列"媒体共现 vs 真实借款关系的构念效度对照 · 待议另立计划"; 本桶备料。注: Petersen–Rajan(1994)/Khwaja–Mian(2008)已在前沿归档 §10.9, 此处不重列。

- Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. *The Journal of Business, 68*(3), 351–381. https://doi.org/10.1086/296668
  - *锚定* — **奠基性证据**: 关系时长越长→利率更低、抵押更少, 是"银企关系强度"构念效度的原始锚。注: 美国小企业授信数据。
  - 〔Crossref 回读标题: Relationship Lending and Lines of Credit in Small Firm Finance〕
- Boot, A. W. A. (2000). Relationship banking: What do we know? *Journal of Financial Intermediation, 9*(1), 7–25. https://doi.org/10.1006/jfin.2000.0282
  - *锚定* — **relationship banking 构念的权威综述奠基**。注: 综述、非实证。
  - 〔Crossref 回读标题: Relationship Banking: What Do We Know?〕
- Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms: Aggregating investor perceptions through internet co-searches. *Journal of Financial Economics, 116*(2), 410–431. https://doi.org/10.1016/j.jfineco.2015.02.003
  - *锚定* — **"共现作关系代理"的 method-precedent**: 用"共同出现/共同检索"从非结构化行为数据推断经济关联实体, 并做效度检验(优于 GICS 行业分类)——为"用新闻共现推断银企关系"的构念效度提供直接方法先例。注: 共检索(EDGAR), 对象为同业/关联企业而非银企。
  - 〔Crossref 回读标题: Search-based peer firms: Aggregating investor perceptions through internet co-searches〕
- Bolton, P., Freixas, X., Gambacorta, L., & Mistrulli, P. E. (2016). Relationship and transaction lending in a crisis. *The Review of Financial Studies, 29*(10), 2643–2676. https://doi.org/10.1093/rfs/hhw041
  - *锚定* — 理论+意大利数据, 界定关系 vs 交易借贷的构念边界(关系银行常态收高息、危机时对优质企业续贷更优)。注: 意大利、含理论模型。
  - 〔Crossref 回读标题: Relationship and Transaction Lending in a Crisis〕
- Amiti, M., & Weinstein, D. E. (2018). How much do idiosyncratic bank shocks affect investment? Evidence from matched bank-firm loan data. *Journal of Political Economy, 126*(2), 525–587. https://doi.org/10.1086/696272
  - *锚定* — **matched 银企贷款数据的方法奠基**(分离银行供给 vs 企业需求冲击), 支撑"银企关系数目/主办银行"识别策略。注: 日本、宏观分解口径。
  - 〔Crossref 回读标题: How Much Do Idiosyncratic Bank Shocks Affect Investment? Evidence from Matched Bank-Firm Loan Data〕
- Beck, T., Degryse, H., De Haas, R., & van Horen, N. (2018). When arm's length is too far: Relationship banking over the credit cycle. *Journal of Financial Economics, 127*(1), 174–196. https://doi.org/10.1016/j.jfineco.2017.11.007
  - *锚定* — 21 国证据, 关系型借贷在衰退期缓解信贷约束(尤其小、不透明企业)。注: 跨国、银行 CEO 访谈分类。
  - 〔Crossref 回读标题: When arm's length is too far: Relationship banking over the credit cycle〕
- Huang, J., Matthews, K., & Zhou, P. (2020). What causes Chinese listed firms to switch bank loan provider? Evidence from a survival analysis. *Emerging Markets Review, 43*, Article 100678. https://doi.org/10.1016/j.ememar.2020.100678
  - *锚定* — **直接用中国 A 股企业-银行匹配贷款关系(存续期/切换)做生存分析**, 与"银企关系数目、主办银行、关系稳定性"高度契合(且数据来自年报披露的借款关系, 呼应 `向金融机构借款表`)。注: 生存分析口径。
  - 〔Crossref 回读标题: What causes Chinese listed firms to switch bank loan provider? Evidence from a survival analysis〕
- Banerjee, R. N., Gambacorta, L., & Sette, E. (2021). The real effects of relationship lending. *Journal of Financial Intermediation, 48*, Article 100923. https://doi.org/10.1016/j.jfi.2021.100923
  - *锚定* — 用意大利 matched 银企数据证明关系型借贷在危机中支撑企业投资与就业等实体结果。注: 意大利、信贷登记数据。
  - 〔Crossref 回读标题: The real effects of relationship lending〕
- Ye, Y., Wang, Y., & Yang, X. (2022). Bank loan information and information asymmetry in the stock market: Evidence from China. *Financial Innovation, 8*(1), Article 62. https://doi.org/10.1186/s40854-022-00367-0
  - *锚定* — **用中国上市公司披露的银行贷款信息构造代理**, 证明"有存续贷款→信息不对称更低" —— 直接支撑"披露的向金融机构借款"作银企关系/透明度代理的效度。注: 测度为信息不对称而非关系强度本身。
  - 〔Crossref 回读标题: Bank loan information and information asymmetry in the stock market: evidence from China〕
- Bai, Y., Dang, T. V., He, Q., & Lu, L. (2022). Does lending relationship help or alleviate the transmission of liquidity shocks? Evidence from a liquidity crunch in China. *Journal of Financial Stability, 58*, Article 100889. https://doi.org/10.1016/j.jfs.2021.100889
  - *锚定* — **中国核心证据**: 用 2013 钱荒证明长期银企关系缓冲银行流动性冲击对借款企业投资/估值的负向传导。注: 事件研究口径, 关系用长期借款连续性度量。
  - 〔Crossref 回读标题: Does lending relationship help or alleviate the transmission of liquidity shocks? Evidence from a liquidity crunch in China〕
- Zhao, T., Matthews, K., & Munday, M. (2023). Neither true nor fairweather friend: Relationship banking and SME borrowing under Covid-19. *The European Journal of Finance, 29*(16), 1957–1974. https://doi.org/10.1080/1351847X.2022.2092415
  - *锚定* — 关系银行在 Covid 前显著、Covid 后作用有限, 对"关系代理"给出**边界条件**。注: 英国 SME; 卷 29 期 16 对应 2023 印刷年(online 2022)。
  - 〔Crossref 回读标题: Neither true nor fairweather friend: relationship banking and SME borrowing under Covid-19〕
- 【2024–2026】Wu, L., Zhang, J., & Xu, L. (2024). Compensating balance and loan bargaining power in China. *Accounting & Finance, 64*(2), 1335–1359. https://doi.org/10.1111/acfi.13181
  - *锚定* — 中国上市公司银行存款/贷款关系与银企议价力, 旁证银企关系强度可从披露的存贷结构度量。注: 测度为补偿性存款/议价力; 卷 64 期 2 对应 2024 印刷年(online 2023)。
  - 〔Crossref 回读标题: Compensating balance and loan bargaining power in China〕
- 【2024–2026】Kutzbach, M. J., & Pogach, J. (2024). Financial technology and relationship lending: Complements or substitutes? *Journal of Financial Intermediation, 59*, Article 101101. https://doi.org/10.1016/j.jfi.2024.101101
  - *锚定* — 检验金融科技与传统关系型借贷是互补还是替代, 支持"关系借贷仍具独立信息价值"(呼应本项目银行金科主构念)。注: 美国 PPP 场景。
  - 〔Crossref 回读标题: Financial technology and relationship lending: Complements or substitutes?〕
- 【2024–2026】Berger, A. N., Bouwman, C. H. S., Norden, L., Roman, R. A., Udell, G. F., & Wang, T. (2024). Piercing through opacity: Relationships and credit card lending to consumers and small businesses during normal times and the COVID-19 crisis. *Journal of Political Economy, 132*(2), 484–551. https://doi.org/10.1086/726236
  - *锚定* — **顶刊(JPE)近期证据**: 关系持有人在危机中获更优信贷条件(跨期平滑)。注: 美国信用卡/小企业、非新闻代理。
  - 〔Crossref 回读标题: Piercing through Opacity: Relationships and Credit Card Lending to Consumers and Small Businesses during Normal Times and the COVID-19 Crisis〕
- 【2024–2026】Liu, J., Chen, S., Su, F., & Liu, J. (2025). Digital transformation disclosure and bank loans: An information heterogeneity perspective. *International Journal of Finance & Economics, 30*(4), 4004–4038. https://doi.org/10.1002/ijfe.3105
  - *锚定* — 中国上市公司**披露文本→银行贷款获取**, 支撑"企业披露信息进入银企借贷决策"的机制与效度。注: 测度为数字化转型披露, 非新闻共现。
  - 〔Crossref 回读标题: Digital Transformation Disclosure and Bank Loans: An Information Heterogeneity Perspective〕

---

## 二、核验记录(三道独立核验 + 一道元数据回填)

1. **发现层自核验**: 5 主题桶并行 FIND 智能体, 提名每条前实时 `GET api.crossref.org/works/{DOI}`(arXiv 走 `api.datacite.org`)读回标题自比对; 解析失败/标题不符当场弃。关系借贷桶额外主动弃 2 个错解 DOI(`10.1016/j.jfineco.2017.09.005`→实解析到 Bali/Brown/Tang、`10.1016/j.jfineco.2015.05.001`→实解析到 Fama–French), 均以正确 DOI 替换后重核。
2. **元数据回填(决定性质检)**: 主控**逐条直连 Crossref/DataCite 回填权威书目**(作者序/年份/卷期/页码/标题, 脚本 `backfill.json`), 据此撰写 APA, **不采信智能体转写**。此步对 69 条**零解析失败、零标题不符、零作者字段错乱**(不同于第六补编当场剔 2 条); 并将若干条年份对齐 Crossref 回读年(卷期年优先): Xu & Shi(卷 33(10)→2026)、Wang et al. Applied Economics(卷 58(21)→2026)、Xing et al.(卷 109→2026)、Wang, Y. et al.(卷 70→2026)、McCauley & Pracht(advance online→2026); Dittmann et al. Crossref 字段读作 2009 而卷 14(1) 通用引 2010、Czyż et al. arXiv 存档年 2023 而 TMLR 录用 2024, 二者 |年差|=1 属 audit 容差内, 已在条目注明。
3. **全语料本地核验(决定性闸)**: `scripts/audit/audit_dois.py`(本轮已将前沿归档 `COMPANY_BANK_COOC_PANEL_PLAN_ARCHIVE_2026-07-04.md` 并入 FILES)直连 Crossref/DataCite, 对全套唯一 DOI 逐条 DOI→标题逐字回比 + 年份核验。本补编 **69 条新增 0 flag**(全部 resolved, 0 UNRESOLVED / 0 TITLE_MISMATCH / 0 YEAR_DIFF); 前七份+前沿归档并入后既有 3 条 pre-existing benign(① CNKI DOI 不进 Crossref; ② 老 ACL Anthology deposit `10.18653/v1/N19-1423` 标题字段空缺但 DOI 真实可解析; ③ SSRN 工作论文 `10.2139/ssrn.3446388` 张贴年差 1 年)仍为既有裁定 benign, **前沿归档 137 DOI 零新增 flag**。任何不能解析或解析到另一篇的 DOI 一律不入本文件。
4. **claim-fit 诚实性**: 每条按 method-origin / recent-application / methodological-analogy 分级并写明与所锚指标的确切关系及局限; 七补-1 富集度零模型一律注明"迁移到银企二部结构"; 公司侧效度族(七补-2/3/5)一律注明"前沿计划§9.9 待议另立计划、本补编只前置备料出处、不代表变量已进任何回归"; 面板时点纪律(七补-4)注明"与 LLM 侧前视污染族正交、不重复"。

> **合计**: 612(前七份)+ **69(本补编净增)** = **681 条**唯一文献锚点; 全语料 `audit_dois.py` 实测唯一 doi.org DOI = **671 个**(592 + 前沿归档并入 10 + 本补编 69)。**富集度双基准铁律**(均匀基准 vs 边际保持基准)——两把尺子互为稳健性、不分主次, 各自 just-identified 并排, **禁混同一 over-identified Hansen J** —— 与代码注释及前沿计划 D8b 一致, 引用时须在方法节写明。
