# 文献理论锚点扩充报告 · 第八补编(税调企业×银行共现面板专项: 税调数据源效度 + 银行网点地理暴露双层权 + 实体匹配 merge 键 · 2024–2026 最新文献优先 · 6 主题桶 · APA 第 7 版 · Crossref/DataCite DOI→标题回比 + 权威元数据逐条回填全核验)

- **日期**: 2026-07-10
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 143 条)、`LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 102 条)、`LITERATURE_ANCHORS_EXPANSION_2026-06-22.md`(第二补编, 63 条)、`LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md`(第三补编, 108 条)、`LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md`(第四补编, 2 条)、`LITERATURE_ANCHORS_SUPPLEMENT_V_2026-07-01.md`(第五补编, 111 条)、`LITERATURE_ANCHORS_SUPPLEMENT_VI_2026-07-06.md`(第六补编, 85 条)、`LITERATURE_ANCHORS_SUPPLEMENT_VII_2026-07-06.md`(第七补编, 69 条)之后的 **第八补编**, 九者与前沿归档 `COMPANY_BANK_COOC_PANEL_PLAN_ARCHIVE_2026-07-04.md` **合为一套**。前八份文件已建成 **681 条已核验锚点 / 671 个唯一 doi.org DOI**(全语料 `audit_dois.py` 实测)。
- **本补编专项**: 补齐 **2026-07-08 新落地的 `company_tax_bank/` 税调企业×银行共现面板派生流水线**(main=a871b44f, v7 年窗=1891e48c)的学术出处。该管线是第七补编收口(2026-07-06)**之后**才提交的全新指标面, 主体系此前零覆盖其税调侧构件:
  1. **样本框换轨**: 上市公司(5,528 家)→ **全国税收调查企业(44,771 家, 2011–2020 年窗)**, merge 主键 = **usci**(18 位统一社会信用代码)——需要"税调数据作为企业微观数据源"的效度/代表性/口径出处(桶①), 及非上市中小企业银企关系的差异化文献(桶④);
  2. **替代权重换轨**: 姊妹管线的权重效度对照(股东/董监高/借款表)在税调侧不可得, 改用**银行分支机构城市/县域两级网点权**(源=银保监金融许可证口径的银行业金融机构基本信息表)与报道共现权**三权互稳**——需要"branch presence = 在地信贷供给暴露"的经典与最新出处(桶②), 与"城市 vs 县域双层级金融地理"的先例(桶③), 以及"份额型暴露权重构造+替代权重规格稳健性"的计量出处(桶⑥);
  3. **实体匹配面**: 44,771 家企业名称 variant × 银行 AC 自动机匹配 + usci 全填全唯一主键——需要 record linkage / 模糊匹配偏误 / 标识符 merge 键的方法出处(桶⑤)。
- **规模**: 6 主题桶并行动态多智能体工作流发现(每候选提名前实时 `GET api.crossref.org/works/{DOI}`, arXiv 走 `api.datacite.org`, 读回标题自比对) → 主控**逐条直连 Crossref/DataCite 回填权威书目元数据**(标题/年份/第一作者/期刊/卷期/页码两道机械回比, 89 候选零解析失败) → 全语料查重(剔与前八份+前沿归档重叠 11 条、批内重复 4 条) = 初稿 74 条 → **8 路对抗评审 (R1)** 后修复 1 P0 + 7 P1 + 10 P2 + 若干 NIT, 并按完备性评审补入 5 条真缺口锚 (related lending own-bank 剔除 ×2 / MAUP ×1 / 撤县设区 ×2) = **净增 79 条唯一锚点**, 其中 **2024–2026 者 33 条**(占 42%), 工作论文 2 条(arXiv)。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编经**三道独立核验 + 两道元数据回比 + 一轮对抗评审**:
  1. 发现层每候选提名前实时查 Crossref/DataCite 读回标题自比对, 核验不过当场弃;
  2. 主控逐条直连回填权威元数据: 第一道 DOI→标题回比(74/74 过, 3 条初判不符经 HTML 实体/`<scp>` 标签归一化后全数复核为假阳性), 第二道卷期/页码/第一作者/期刊名回比(9 条初判疑点全部为 `&amp;` 反转义/U+2010 连字符/期刊副标题等编码假阳性, **零真书目错乱**); R1 补入的 5 条同样经主控逐条直连 Crossref 回填 (标题/年份/第一作者/期刊/卷期/页码) 并全数通过;
  3. 全语料本地决定性闸: `scripts/audit/audit_dois.py`(本补编已加入 FILES)直连 Crossref/DataCite, 对全套唯一 DOI 逐条 DOI→标题逐字回比 + 年份核验 (R1 前 745 DOI 轮实测: 742 OK + 仅 3 条既有 benign 零新增 flag; R1 补入 5 条后复跑同样零新增 flag);
  4. **8 路对抗评审 (R1)**: 6 桶各一名对抗审稿人逐条查文献真实摘要比对锚定句诚实性 + 1 名格式/口径一致性审 + 1 名完备性批评者。抓获并修复: **1 P0**(Cui-Hicks-Xing 2022 数据源错配 — 该文用某省行政税表**非**税调数据, 锚定句已改写并显式划界)、**7 P1**(Yu-Qi NTSD 未证实点名/Wang-Dong-Ge 网点级数据夸大+银保监年代错置/Greenstone-Mas-Nguyen 否定性结论未披露/Xu 2019 上市公司样本+选择性引用/Ward 2023 race 成分吞并+构念滑移/Li-Shao 设计细节投射/Schwenkler-Zheng 判据与语境边界缺失)、**10 P2**(含 3 处年份-卷期口径统一为卷期年优先、方法迁移锚逐条补国别/构念边界)与格式 NIT(en-dash 统一/Article 前缀/Fišar 斜体/回读标题空白归一/同姓作者消歧)。修复方向逐条对照评审证据自验 (镜像"评审 agent 修法也要验方向"教训)。
- **合计**: 681(前八份)+ **79(本补编净增)** = **760 条**唯一文献锚点; 全语料 `audit_dois.py` 实测唯一 doi.org DOI = **750 个**(671 + 79)。

---

## 〇、白话导读

**这份补的是什么**: 前八份把主管道(v3.15.0)和上市公司×银行共现面板的学术出处都配齐了(681 条)。但 7 月 8 日项目又落地了一条**新管线**: 把"上市公司"换成"**全国税收调查里的 44,771 家企业**"(绝大多数是非上市的中小企业), 照样数"哪家企业和哪家银行在同一篇新闻里一起出现"。因为税调企业没有股东名单、董监高这类公开对照数据, 项目改用了另一个思路做交叉验证: **数一数每家银行在这家企业所在的城市/县里开了多少网点**——网点多, 说明这家银行在当地信贷供给强, 企业和它发生关系的可能性就大。于是"报道共现权 + 城市网点权 + 县域网点权"三把尺子互相印证。这份补编补的就是这条新管线的四类出处: ① 税调数据本身靠不靠谱(顶刊用过没有、覆盖谁、口径如何); ② "网点=在地信贷供给"这件事的经典与最新证据; ③ 城市和县两个层级分别量金融可及性的先例; ④ 用 18 位社会信用代码和企业名字做数据匹配时, 怎么防错配、错配会带来什么偏误。

**和"严禁自我生成"的关系**: 每一条**都不是编的**。发现时智能体先查官方接口, 之后主控又**逐条直连 Crossref/DataCite 把标题、年份、第一作者、期刊、卷期、页码原样拉回来**做两道机械回比(不信智能体的转写)。这次 79 条**一条没查不着、一条真书目没错乱**(初判的 12 处疑点均出自初稿 74 条轮, 复核后全部是 HTML 转义符和特殊连字符造成的假阳性; 评审后补入的 5 条同样逐条回填核验)。之后又请 8 个对抗评审员逐条去查每篇文献**实际写了什么**, 抓出 1 条把"某省行政税表"错说成"税调数据"的硬伤和一批夸大/漏注边界的措辞, 全部改写修正; 评审还指出 3 个真缺口(为什么要剔"银行自家企业"的共现、城/县两个口径对不上怎么办、县改区了怎么办), 补了 5 条对应出处。最后本地脚本再对全套 750 个 DOI 全量复核一遍。每条后面的"回读标题"就是接口实际回读值。

**怎么用**: 写论文/codebook 时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。**勿沿用代码注释里的旧版引用**。

**一句话铁律提醒**: 报道共现权、城市网点权、县域网点权**三权互为稳健性、不分主次**——各自 just-identified 并排, **严禁混进同一 over-identified Hansen J**(与代码 `company_tax_bank/` 及 CLAUDE.md 铁律一致, 引用时须在方法节写明)。各桶方法迁移锚(原文语境≠银企共现)的"锚定"句均已注明国别/构念/结论方向边界(R1 评审逐条把关), 引用时勿夸大。

**评审遗留的两项 DEFERRED 挂靠动作**(不新增锚点, 生产机重生 codebook 时落地): ① codebook §7-L1 单一企业占比告警段显式挂靠八补-5 Bailey et al. (2020) + Abramitzky et al. (2021), 声明阈值为研究者选择的诊断哨兵; ② codebook L2 批次快照铺零段显式引用七补-4 幸存者偏误/as-of 条目 + 八补-1 Chen, He, Liu, Suárez Serrato & Xu (2021, *Tax Policy and the Economy*, NTSD 口径描述件)。

---

## 一、6 主题桶 × 新增已核验锚点(2024–2026 优先; 〔〕内为回读标题)

### 八补-1. 全国税收调查数据 (NTSD) 数据源效度 / 中国企业行政微观数据 (税调面板样本框 44,771 家 · 2011–2020 年窗 · usci 主键)

> 净增 14 条(其中 2024–2026 者 7 条)。

- Brandt, L., Van Biesebroeck, J., & Zhang, Y. (2012). Creative accounting or creative destruction? Firm-level productivity growth in Chinese manufacturing. *Journal of Development Economics, 97*(2), 339–351. https://doi.org/10.1016/j.jdeveco.2011.02.002
  - *锚定* — 中国企业微观行政数据 (工业企业数据库) 跨年匹配、清洗与效度处理的奠基经典, 锚定本管线税调面板跨年主键 (usci) 匹配与数据质量协议 (通用效度条目)。
  - 〔Crossref 回读标题: Creative accounting or creative destruction? Firm-level productivity growth in Chinese manufacturing〕
- Liu, Y., & Mao, J. (2019). How do tax incentives affect investment and productivity? Firm-level evidence from China. *American Economic Journal: Economic Policy, 11*(3), 261–291. https://doi.org/10.1257/pol.20170478
  - *锚定* — 以中国企业微观数据评估 2004–2009 分步增值税转型 (2004 东北试点→2007 中部扩围→2009 全国推开) 对企业投资与生产率的因果效应 (投资 +38.4%/生产率 +8.9%), 学界通引为全国税收调查数据的顶刊奠基用例 (数据源细节见其数据节)。
  - 〔Crossref 回读标题: How Do Tax Incentives Affect Investment and Productivity? Firm-Level Evidence from China〕
- Chen, Z., He, Y., Liu, Z., Suárez Serrato, J. C., & Xu, D. Y. (2021). The structure of business taxation in China. *Tax Policy and the Economy, 35*, 131–177. https://doi.org/10.1086/713495
  - *锚定* — 系统刻画中国企业税制结构并描述全国税收调查数据库 (NTSD) 的覆盖、抽样与口径, 是本管线税调样本 (2011–2020, usci主键) 代表性讨论的核心锚点。
  - 〔Crossref 回读标题: The Structure of Business Taxation in China〕
- Chen, Z., Liu, Z., Suárez Serrato, J. C., & Xu, D. Y. (2021). Notching R&D investment with corporate income tax cuts in China. *American Economic Review, 111*(7), 2065–2100. https://doi.org/10.1257/aer.20191758
  - *锚定* — 基于中国企业所得税行政申报数据研究税收notch下的研发投入操纵与真实反应, 支撑税调类行政税务数据可用于识别企业申报行为的口径讨论。
  - 〔Crossref 回读标题: Notching R&D Investment with Corporate Income Tax Cuts in China〕
- Cui, W., Hicks, J., & Xing, J. (2022). Cash on the table? Imperfect take-up of tax incentives and firm investment behavior. *Journal of Public Economics, 208*, Article 104632. https://doi.org/10.1016/j.jpubeco.2022.104632
  - *锚定* — 用某大省企业所得税行政申报+财务报表微观数据度量加速折旧优惠的不完全领取 (80%以上合格投资未申领) 及其投资含义, 支撑中国税务行政微观数据 (广义) 可识别企业申报与投资行为。⚠ 注: 该文数据**非**全国税收调查 (数据=某大省保密企业所得税申报+财务报表, 见其数据节), 引用时勿写成税调用例。
  - 〔Crossref 回读标题: Cash on the table? Imperfect take-up of tax incentives and firm investment behavior〕
- Yu, J., & Qi, Y. (2022). BT-to-VAT reform and firm productivity: Evidence from a quasi-experiment in China. *China Economic Review, 71*, Article 101740. https://doi.org/10.1016/j.chieco.2021.101740
  - *锚定* — 使用中国企业层行政微观面板 2011–2017 (窗口与本管线税调面板高度重合) 以 DiD 研究营改增对企业生产率的准实验效应; 正效应在融资约束紧的企业中更强 (异质性, 非机制)。注: 摘要仅称 administrative firm-level dataset 未点名 NTSD, 数据源以正文为准。
  - 〔Crossref 回读标题: BT-to-VAT reform and firm productivity: Evidence from a quasi-experiment in China〕
- Chen, Z., Jiang, X., Liu, Z., Suárez Serrato, J. C., & Xu, D. Y. (2023). Tax policy and lumpy investment behaviour: Evidence from China's VAT reform. *The Review of Economic Studies, 90*(2), 634–674. https://doi.org/10.1093/restud/rdac027
  - *锚定* — 用中国税务行政微观数据识别VAT改革下企业粗投资 (lumpy investment) 行为, 锚定本管线税调企业行政数据用于因果识别的可信度。
  - 〔Crossref 回读标题: Tax Policy and Lumpy Investment Behaviour: Evidence from China’s VAT Reform〕
- 【2024–2026】Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. *Tax Policy and the Economy, 38*, 101–122. https://doi.org/10.1086/730053
  - *锚定* — 评估金税工程电子化增值税发票对征管与企业行为的动态效应, 锚定税调数据所处的征管技术环境与中国税务行政数据质量讨论。
  - 〔Crossref 回读标题: Technological Adoption and Taxation: The Case of China’s Golden Tax Reform〕
- 【2024–2026】Liu, L., Cao, L., Cao, Y., Lu, M., & Shan, Y. (2024). VAT credit refunds and firm productivity: Evidence from China's VAT reform. *International Review of Financial Analysis, 93*, Article 103171. https://doi.org/10.1016/j.irfa.2024.103171
  - *锚定* — 以增值税留抵退税政策为外生冲击研究企业生产率, 提供税调窗口内VAT政策通过现金流/融资渠道影响企业的最新证据 (不宣称其使用税调数据)。
  - 〔Crossref 回读标题: VAT credit refunds and firm productivity: Evidence from China's VAT reform〕
- 【2024–2026】Xiao, R., Xu, P., & Huang, B. (2024). Tax incentives and firm social insurance contributions: Evidence from China. *China Economic Review, 86*, Article 102210. https://doi.org/10.1016/j.chieco.2024.102210
  - *锚定* — 以中国企业微观数据估计税收优惠对企业社保缴费的正向效应, 支撑税调企业税负/优惠变量对企业行为的解释力。
  - 〔Crossref 回读标题: Tax incentives and firm social insurance contributions: Evidence from China〕
- 【2024–2026】Yu, C., & Li, Y. (2025). Digitalization of tax collection and enterprises' social security compliance. *International Tax and Public Finance, 32*(4), 1213–1252. (卷期年优先; online-first 2024) https://doi.org/10.1007/s10797-024-09867-4
  - *锚定* — 研究税收征管数字化 (金税三期) 对企业社保合规的影响, 支撑本管线税调窗口内征管环境变迁作为企业申报数据口径背景。
  - 〔Crossref 回读标题: Digitalization of tax collection and enterprises’ social security compliance〕
- 【2024–2026】Cao, J., Ma, G., Mao, J., & Yin, H. (2026). Who benefits from investment tax incentives? Evidence from China's VAT reform. *Journal of Economic Behavior & Organization, 245*, Article 107532. https://doi.org/10.1016/j.jebo.2026.107532
  - *锚定* — 基于2007–2015中国企业层数据估计VAT投资优惠在雇员/价格/利润间的归宿, 为税调企业样本上税收激励分配效应提供2026年最新锚点。
  - 〔Crossref 回读标题: Who benefits from investment tax incentives? Evidence from China’s VAT reform〕
- 【2024–2026】Fu, J., Liu, Z., Wang, S., & Zhao, X. (2026). Tax incentives and firm compliance: Evidence from China. *China Economic Review, 99*, Article 102747. https://doi.org/10.1016/j.chieco.2026.102747
  - *锚定* — 提供税收优惠与中国企业申报合规行为的最新 (2026) 证据, 支撑本管线税调企业申报口径可信度讨论 (数据源细节以正文为准, 不夸大) (Crossref 存在性已核; 刊发过新, 摘要未入公开索引, 内容待正文核)。
  - 〔Crossref 回读标题: Tax incentives and firm compliance: Evidence from China〕
- 【2024–2026】Zhang, Z., Lu, Y., Tao, D., & Tian, B. (2026). Spillover effect of tax enforcement: Evidence from China. *Journal of Asian Economics, 103*, Article 102126. https://doi.org/10.1016/j.asieco.2026.102126
  - *锚定* — 使用全国税收调查企业数据识别税收稽查在道路级邻近区域的空间外溢, 直接示范税调微观数据支持地理邻近结构分析 (呼应本管线城市/县域网点权的空间构造)。
  - 〔Crossref 回读标题: Spillover effect of tax enforcement: Evidence from China〕

### 八补-2. 银行分支机构网点数据与在地信贷暴露 (branch_cityw / branch_countyw 双层网点权源: 金融许可证口径)

> 净增 15 条(其中 2024–2026 者 7 条)。

- Jayaratne, J., & Strahan, P. E. (1996). The finance-growth nexus: Evidence from bank branch deregulation. *The Quarterly Journal of Economics, 111*(3), 639–670. https://doi.org/10.2307/2946668
  - *锚定* — 经典锚点: 以美国跨州分支管制放开作为银行在地存在的准外生变异并识别其增长效应, 是把分支网络扩张当作信贷供给冲击/工具变量策略的奠基文献。注: 原文识别=州内分支管制放开时点的 DiD (非 IV), '工具变量用法'是后续文献的追溯性发展
  - 〔Crossref 回读标题: The Finance-Growth Nexus: Evidence from Bank Branch Deregulation〕
- Petersen, M. A., & Rajan, R. G. (2002). Does distance still matter? The information revolution in small business lending. *The Journal of Finance, 57*(6), 2533–2570. https://doi.org/10.1111/1540-6261.00505
  - *锚定* — 经典锚点: 记录小企业借贷中借贷距离随信息技术演化但软信息借贷仍依赖在地存在, 为城市层与县域层两档地理粒度并行 (粗/细互稳) 提供距离-信息机制依据。
  - 〔Crossref 回读标题: Does Distance Still Matter? The Information Revolution in Small Business Lending〕
- Degryse, H., & Ongena, S. (2005). Distance, lending relationships, and competition. *The Journal of Finance, 60*(1), 231–266. https://doi.org/10.1111/j.1540-6261.2005.00729.x
  - *锚定* — 经典锚点: 借款企业与放贷网点的物理距离显著影响贷款利率 (空间价格歧视), 支撑以企业所在城/县内银行网点密度刻画企业-银行关联强度的做法。
  - 〔Crossref 回读标题: Distance, Lending Relationships, and Competition〕
- Nguyen, H.-L. Q. (2019). Are credit markets still local? Evidence from bank branch closings. *American Economic Journal: Applied Economics, 11*(1), 1–32. https://doi.org/10.1257/app.20170543
  - *锚定* — 经典锚点: 网点关闭导致本地小企业信贷持续下降且效应在6英里内消散, 支撑本管线用城市/县层网点权度量企业对银行的在地信贷暴露 (branch presence = 本地信贷供给)。
  - 〔Crossref 回读标题: Are Credit Markets Still Local? Evidence from Bank Branch Closings〕
- Bonfim, D., Nogueira, G., & Ongena, S. (2021). "Sorry, we're closed": Bank branch closures, loan pricing, and information asymmetries. *Review of Finance, 25*(4), 1211–1259. https://doi.org/10.1093/rof/rfaa036
  - *锚定* — 网点关闭后原关系企业转投他行时贷款定价与信息不对称恶化, 支撑网点权作为企业-银行软信息关系强度代理 (而非仅物理可达性)。
  - 〔Crossref 回读标题: “Sorry, We're Closed” Bank Branch Closures, Loan Pricing, and Information Asymmetries〕
- Granja, J., Leuz, C., & Rajan, R. G. (2022). Going the extra mile: Distant lending and credit cycles. *The Journal of Finance, 77*(2), 1259–1324. https://doi.org/10.1111/jofi.13114
  - *锚定* — 银行-借款人距离随信贷周期扩张且远距贷款质量更差, 佐证在地网点暴露 (近距离) 与远程/媒体渠道暴露是不同质的关联测度, 支撑三权互为稳健性设计。
  - 〔Crossref 回读标题: Going the Extra Mile: Distant Lending and Credit Cycles〕
- Ji, Y., Teng, S., & Townsend, R. M. (2023). Dynamic bank expansion: Spatial growth, financial access, and inequality. *Journal of Political Economy, 131*(8), 2209–2275. https://doi.org/10.1086/724112
  - *锚定* — 以到最近网点距离刻画金融可及成本并结构估计分支网络空间扩张的实际效应, 为县域层网点权的空间摩擦解释提供顶刊结构模型锚点 (原文场景为泰国分支网络扩张的结构估计, 此处为空间摩擦机制的方法迁移锚)
  - 〔Crossref 回读标题: Dynamic Bank Expansion: Spatial Growth, Financial Access, and Inequality〕
- Wang, C., Dong, Y., & Ge, R. (2023). Bank branching deregulation and the credit risk of the regional banking sector: Evidence from city commercial banks in China. *Emerging Markets Review, 55*, Article 100969. https://doi.org/10.1016/j.ememar.2022.100969
  - *锚定* — 利用中国城商行跨城分支准入放开 (2006–2011, 银监会口径) 的准实验、以 286 个地级市城市层数据研究分支扩张对区域银行业信用风险的影响 (竞争加剧→信用风险上升), 锚定中国分支管制变异作为在地银行存在准外生来源的研究先例。注: 城市层聚合数据, 非网点级许可证明细。
  - 〔Crossref 回读标题: Bank branching deregulation and the credit risk of the regional banking sector: Evidence from city commercial banks in China〕
- 【2024–2026】Cardamone, P., & Trivieri, F. (2024). Out of sight, out of mind! Bank branch closures and new firm creation in Italy. *Regional Studies, Regional Science, 11*(1), 122–152. https://doi.org/10.1080/21681376.2024.2315187
  - *锚定* — 意大利省级证据显示网点关闭抑制新企业创立, 支撑县/市层网点密度作为企业层融资环境暴露变量的外部效度。
  - 〔Crossref 回读标题: Out of sight, out of mind! Bank branch closures and new firm creation in Italy〕
- 【2024–2026】Fonseca, J., & Matray, A. (2024). Financial inclusion, economic development, and inequality: Evidence from Brazil. *Journal of Financial Economics, 156*, Article 103854. https://doi.org/10.1016/j.jfineco.2024.103854
  - *锚定* — 以政策驱动的银行网点进入 (banking deserts 填补) 识别在地银行存在对创业/就业/工资的因果效应, 为县域网点权作为信贷供给暴露的政策外生变异提供最新 JFE 锚点。
  - 〔Crossref 回读标题: Financial inclusion, economic development, and inequality: Evidence from Brazil〕
- 【2024–2026】Keil, J., & Ongena, S. (2024). The demise of branch banking – Technology, consolidation, bank fragility. *Journal of Banking & Finance, 158*, Article 107038. https://doi.org/10.1016/j.jbankfin.2023.107038
  - *锚定* — 记录技术与并购驱动的分支网络收缩长期趋势及其与银行脆弱性的关联, 提醒本管线网点权在样本期 (2011–2020) 内的时变性须以年度网点面板而非截面刻画。
  - 〔Crossref 回读标题: The demise of branch banking – Technology, consolidation, bank fragility〕
- 【2024–2026】Tian, Z., Shen, Y., & Chen, Z. (2024). How does bank branch expansion affect ESG: Evidence from Chinese commercial banks. *Economic Analysis and Policy, 82*, 502–514. https://doi.org/10.1016/j.eap.2024.03.025
  - *锚定* — 以中国商业银行分支扩张 (分支扩张测度) 为处理变量研究银行行为后果, 提供中国网点级数据构造银行在地存在测度的 2024 年实证先例。
  - 〔Crossref 回读标题: How does bank branch expansion affect ESG: Evidence from Chinese commercial banks〕
- 【2024–2026】Wang, S., Zeng, S., & Xie, W. (2025). City commercial banks' expansion and firm innovation: Evidence from China. *Economic Analysis and Policy, 87*, 2658–2673. https://doi.org/10.1016/j.eap.2025.08.020
  - *锚定* — 城商行跨区网点进入通过缓解融资约束提升企业研发/创新, 直接锚定'企业所在地银行网点进入 → 企业层结果'的识别链条 (与本管线企业-银行网点权同构)。
  - 〔Crossref 回读标题: City commercial banks’ expansion and firm innovation: Evidence from China〕
- 【2024–2026】Du, Y., Li, W., & Wang, X. (2026). The impact of foreign bank deregulation on firm performance: Evidence from China. *Economica, 93*(370), 677–704. https://doi.org/10.1111/ecca.70032
  - *锚定* — 以中国外资银行准入放开 (分支设立管制) 的城市×时间变异识别银行在地进入对企业绩效的影响, 为网点权的准自然实验解释提供 2026 年最新锚点。
  - 〔Crossref 回读标题: The impact of foreign bank deregulation on firm performance: evidence from China〕
- 【2024–2026】Zhang, X., & Li, Z. (2026). FinTech and branch network expansion: Evidence from China's banking industry. *Applied Economics, 58*(12), 2321–2336. (卷期年优先; online-first 2025) https://doi.org/10.1080/00036846.2025.2476213
  - *锚定* — 用约 27 万条中国银行网点数据研究金融科技对分支网络扩张的影响, 与本项目银行×金科主题直接交叉, 且示范中国网点大样本数据 (许可证口径) 的学术使用。
  - 〔Crossref 回读标题: FinTech and branch network expansion: evidence from China’s banking industry〕

### 八补-3. 县域/城市两级金融地理 / 聚合层级敏感性 (MAUP) / 区划变更 (城市权 vs 县域权双层级并排 · city×county ρ=0.899 · 县改区错位披露)

> 净增 16 条(其中 2024–2026 者 7 条)。⚠ 铁律: 城市权 vs 县域权双层级互为稳健性、不分主次, 禁混同一 over-identified Hansen J。MAUP/撤县设区 3 条为 R1 完备性评审补入。

- Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit problem in multivariate statistical analysis. *Environment and Planning A: Economy and Space, 23*(7), 1025–1044. https://doi.org/10.1068/a231025
  - *锚定* — **MAUP (可变面积单元问题) 奠基**: 多变量统计推断对空间聚合单元的尺度 (scale) 与分区 (zoning) 选择敏感 — 锚定本管线城市/县域两级网点权并排报告 + 跨粒度秩相关 (city×county Spearman ρ=0.899) 作为聚合层级敏感性检验的方法学动机。注: 通用空间统计方法件, 非金融应用。
  - 〔Crossref 回读标题: The Modifiable Areal Unit Problem in Multivariate Statistical Analysis〕
- Guiso, L., Sapienza, P., & Zingales, L. (2004). Does local financial development matter? *The Quarterly Journal of Economics, 119*(3), 929–969. https://doi.org/10.1162/0033553041502162
  - *锚定* — 奠基经典: 在一体化金融市场内构造次国家 (意大利地区) 层级金融发展指标并证明其影响企业进入与成长, 锚定本管线以城市/县域层级度量企业金融可及性的合法性。
  - 〔Crossref 回读标题: Does Local Financial Development Matter?〕
- Burgess, R., & Pande, R. (2005). Do rural banks matter? Evidence from the Indian social banking experiment. *American Economic Review, 95*(3), 780–795. https://doi.org/10.1257/0002828054201242
  - *锚定* — 奠基经典: 以印度农村银行网点扩张的准实验证明地方网点开设改变实体结果, 锚定本管线用县域银行分支机构存在作为企业-银行关联权重的思路。
  - 〔Crossref 回读标题: Do Rural Banks Matter? Evidence from the Indian Social Banking Experiment〕
- Chen, Z., Poncet, S., & Xiong, R. (2020). Local financial development and constraints on domestic private-firm exports: Evidence from city commercial banks in China. *Journal of Comparative Economics, 48*(1), 56–75. https://doi.org/10.1016/j.jce.2019.09.005
  - *锚定* — 以中国城商行网点的城市层级存在度量地方金融发展并识别其对民营企业出口约束的缓解, 锚定本管线城市层网点权 (②) 的中国证据基础。
  - 〔Crossref 回读标题: Local financial development and constraints on domestic private-firm exports: Evidence from city commercial banks in China〕
- Greenstone, M., Mas, A., & Nguyen, H.-L. (2020). Do credit market shocks affect the real economy? Quasi-experimental evidence from the Great Recession and "normal" economic times. *American Economic Journal: Economic Policy, 12*(1), 200–225. https://doi.org/10.1257/pol.20160005
  - *锚定* — 以'银行本地市场份额 × 银行信贷供给移动'构造 county 级信贷供给暴露 (shift-share), 是本管线网点份额型地理暴露构造的方法先例。⚠ 注: 该文实证结论为县域小企业信贷冲击对实体经济活动影响有限 (尤其正常时期), 此处仅取其暴露构造方法, 不引其结论方向。
  - 〔Crossref 回读标题: Do Credit Market Shocks Affect the Real Economy? Quasi-experimental Evidence from the Great Recession and “Normal” Economic Times〕
- Zhao, B., & Xi, X. (2022). Economic effects of conversion from county (or county-level city) to municipal district in China. *PLOS ONE, 17*(9), Article e0272267. https://doi.org/10.1371/journal.pone.0272267
  - *锚定* — 撤县设区 (county-to-district conversion) 经济效应的中国实证 — 佐证县改区是真实且系统性的区划变更事件而非登记噪声, 锚定本管线县域键快照精确匹配下'县改区错位→披露不修补 + county_key_ok 机器可读标识'的保守处置 (题名级核验, 效应方向以正文为准)。
  - 〔Crossref 回读标题: Economic effects of conversion from county (or county-level city) to municipal district in China〕
- Herpfer, C., Mjøs, A., & Schmidt, C. (2023). The causal impact of distance on bank lending. *Management Science, 69*(2), 723–740. https://doi.org/10.1287/mnsc.2022.4346
  - *锚定* — 用道路基建带来的企业-银行通行距离外生变化识别距离对放贷的因果效应, 为本管线以网点地理邻近 (城市/县域) 作为企业-银行关联强度代理提供因果依据 (挪威场景; 该文另发现既有关系中银行会部分攫取通行成本节约, 邻近并非一律利于企业)
  - 〔Crossref 回读标题: The Causal Impact of Distance on Bank Lending〕
- Lai, S., Chen, L., Wang, Q. S., & Anderson, H. D. (2023). Bank competition and corporate employment: Evidence from the geographic distribution of bank branches in China. *Journal of Banking & Finance, 154*, Article 106964. https://doi.org/10.1016/j.jbankfin.2023.106964
  - *锚定* — 用中国 21.9 万家银行分支机构地理分布度量企业周边银行竞争并联到企业雇佣, 是本管线'企业所在地银行网点计数权'在中国场景的直接先例。
  - 〔Crossref 回读标题: Bank competition and corporate employment: Evidence from the geographic distribution of bank branches in China〕
- Wang, E.-Z., & Lee, C.-C. (2023). The impact of commercial bank branch expansion on energy efficiency: Micro evidence from China. *China Economic Review, 80*, Article 102019. https://doi.org/10.1016/j.chieco.2023.102019
  - *锚定* — 用中国制造业企业与银行网点经纬度做微观地理匹配 (阈值半径内网点数) 构造企业级融资可得变量, 是本管线企业-网点地理匹配构造的中国微观先例。
  - 〔Crossref 回读标题: The impact of commercial bank branch expansion on energy efficiency: Micro evidence from China〕
- 【2024–2026】Gama, P. M., Sol Murta, F., & Vieira, E. S. (2024). Local banking development and SME conservative financing policy. Does bank branch density matter? *Small Business Economics, 63*(4), 1747–1765. https://doi.org/10.1007/s11187-024-00910-6
  - *锚定* — 以市镇层级银行网点密度度量地方银行业环境并联到中小企业融资行为 (葡萄牙场景); 结论方向为高密度地区中小企业融资更保守 (债务使用负相关, 合作银行网点方向相反)。此处仅取'次国家层级网点密度作为地方银行环境测度'的构造先例, 不取方向性结论。
  - 〔Crossref 回读标题: Local banking development and SME conservative financing policy. Does bank branch density matter?〕
- 【2024–2026】Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C. (2024). Does improved credit access promote pollution reduction? The role of bank proximity. *Economic Analysis and Policy, 84*, 78–97. https://doi.org/10.1016/j.eap.2024.08.019
  - *锚定* — 以企业与银行网点的地理邻近度量信贷可得改善并联到企业行为, 锚定本管线'网点邻近=企业-银行关联强度'这一权重构造假设的近期证据。
  - 〔Crossref 回读标题: Does improved credit access promote pollution reduction? The role of bank proximity〕
- 【2024–2026】Shen, H., Qin, M., Li, T., Zhang, X., & Zhao, Y. (2024). Digital finance and industrial structure upgrading: Evidence from Chinese counties. *International Review of Financial Analysis, 95*, Article 103442. https://doi.org/10.1016/j.irfa.2024.103442
  - *锚定* — 以中国县域为分析单元度量金融 (数字金融) 发展并联到县域产业结构升级, 且在传统金融发展较弱县效应更强, 锚定本管线以县为金融暴露度量单元的口径 注: 构念为数字渠道 (≠网点在地存在), 仅取县级暴露单元口径先例。
  - 〔Crossref 回读标题: Digital finance and industrial structure upgrading: Evidence from Chinese counties〕
- 【2024–2026】Yu, W., Wang, L., Liu, X., Xie, W., & Zhang, M. (2024). Can digital inclusive finance promote high-quality rural entrepreneurship? A county-level analysis from China. *Finance Research Letters, 67*, Article 105820. https://doi.org/10.1016/j.frl.2024.105820
  - *锚定* — 以中国县域面板 (1,649 县, 2014–2019) 度量**数字**普惠金融可及性并发现其与结果的倒 U 形关系。注: 构念为数字渠道 (文献中常视作实体网点的替代), 非网点在地存在; 此处仅取'县为金融暴露单元的年度面板'结构先例。
  - 〔Crossref 回读标题: Can digital inclusive finance promote high-quality rural entrepreneurship? A county-level analysis from China〕
- 【2024–2026】Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition. *American Economic Review, 115*(6), 1818–1856. https://doi.org/10.1257/aer.20200374
  - *锚定* — 以银行分支网络结构模型刻画地方信贷市场分割与跨地区资金流动, 锚定本管线'银行×地点网点矩阵决定地方信贷可得'的分支网络视角。
  - 〔Crossref 回读标题: The Geographic Flow of Bank Funding and Access to Credit: Branch Networks, Synergies, and Local Competition〕
- 【2024–2026】Qiao, L., Guo, D., Wu, C., & Wang, H. (2025). Exploring common prosperity in China's counties: From the perspective of bank branch expansion. *Cities, 158*, Article 105724. https://doi.org/10.1016/j.cities.2025.105724
  - *锚定* — 直接以中国县域银行分支机构扩张为解释变量研究县域经济结果, 锚定本管线县域层网点权 (③, 金融许可证口径网点计数) 的构造与county-level中国证据。
  - 〔Crossref 回读标题: Exploring common prosperity in China's counties: From the perspective of bank branch expansion〕
- 【2024–2026】Tan, P., & Wang, R. (2026). Local drivers of municipal consolidation: County-to-district conversion in China. *Land, 15*(4), Article 672. https://doi.org/10.3390/land15040672
  - *锚定* — 县改区行政区划合并的地方驱动因素 (2026 最新) — 区划变更具选择性 (非随机) 的证据, 支撑本管线不建历史区划别名表、以缺键标识如实披露而非静默回填的决策 (题名级核验, 机制以正文为准)。
  - 〔Crossref 回读标题: Local Drivers of Municipal Consolidation: County-to-District Conversion in China〕

### 八补-4. 私营/非上市/中小企业银企关系 + 关联贷款 own-bank 剔除 (税调企业绝大多数为非上市中小企业 · D4 五通道 bank_company_map)

> 净增 14 条(其中 2024–2026 者 4 条)。own-bank 剔除 2 条 (La Porta et al. 2003 / Khwaja & Mian 2005) 为 R1 完备性评审补入。

- La Porta, R., Lopez-de-Silanes, F., & Zamarripa, G. (2003). Related lending. *The Quarterly Journal of Economics, 118*(1), 231–268. https://doi.org/10.1162/00335530360535199
  - *锚定* — **own-bank 剔除 (D4 五通道) 的构念出处**: 关联贷款 (银行对其控制人/关联企业放贷) 条件更优、违约率更高、回收率更低 (墨西哥全银行样本), 证明关联借贷与臂长银企信贷关系不同质 — 锚定本管线把银行系企业与自家银行的共现剔出银企关系计数 (280 家 bank_company_map, is_bank_company 标记保留供分析端裁样) 的经济学依据。
  - 〔Crossref 回读标题: Related Lending〕
- Khwaja, A. I., & Mian, A. (2005). Do lenders favor politically connected firms? Rent provision in an emerging financial market. *The Quarterly Journal of Economics, 120*(4), 1371–1411. https://doi.org/10.1162/003355305775097524
  - *锚定* — 政治关联企业从政府银行获得优惠信贷且违约率更高 (巴基斯坦全量信贷登记), 与 La Porta et al. (2003) 同为'关联≠臂长借贷'的核心证据 — 支撑 own-bank/关联共现须与一般银企媒体关联区分处理的决策。
  - 〔Crossref 回读标题: Do Lenders Favor Politically Connected Firms? Rent Provision in an Emerging Financial Market〕
- Ayyagari, M., Demirgüç-Kunt, A., & Maksimovic, V. (2010). Formal versus informal finance: Evidence from China. *Review of Financial Studies, 23*(8), 3048–3097. https://doi.org/10.1093/rfs/hhq030
  - *锚定* — 用中国非上市私营企业调查样本证明正规银行融资(相对非正规融资)与更快企业增长相关, 锚定以非上市企业样本研究银行信贷与企业绩效的奠基证据。
  - 〔Crossref 回读标题: Formal versus Informal Finance: Evidence from China〕
- Chong, T. T.-L., Lu, L., & Ongena, S. (2013). Does banking competition alleviate or worsen credit constraints faced by small- and medium-sized enterprises? Evidence from China. *Journal of Banking & Finance, 37*(9), 3412–3424. https://doi.org/10.1016/j.jbankfin.2013.05.006
  - *锚定* — 将中国中小企业融资调查与银行分支网点明细结合, 用地方银行市场网点结构解释中小企业信贷约束, 直接锚定本管线②③以城市/县域网点分布构造企业-银行接入权的核心决策。
  - 〔Crossref 回读标题: Does banking competition alleviate or worsen credit constraints faced by small- and medium-sized enterprises? Evidence from China〕
- Cull, R., Li, W., Sun, B., & Xu, L. C. (2015). Government connections and financial constraints: Evidence from a large representative sample of Chinese firms. *Journal of Corporate Finance, 32*, 271–294. https://doi.org/10.1016/j.jcorpfin.2014.10.012
  - *锚定* — 用大规模代表性中国企业(含非上市)调查数据研究融资约束与投资, 锚定以全国性企业调查微观数据(同税调样本框范式)研究非上市企业信贷约束的方法先例。
  - 〔Crossref 回读标题: Government connections and financial constraints: Evidence from a large representative sample of Chinese firms〕
- Xu, B. (2019). Permissible collateral and access to finance: Evidence from a quasi-natural experiment. *China Economic Review, 54*, 237–255. https://doi.org/10.1016/j.chieco.2018.11.006
  - *锚定* — 以中国 2007 物权法扩大可担保财产范围为准实验 (DiD, 2001–2011) 提供抵押品渠道提升信贷可得性与期限的证据。⚠ 注: 样本为**上市公司**, 与本桶非上市税调样本框存在边界; 且该文同时发现改革未改善信贷配置效率 (低质量企业债务扩张最多)、信贷扩张未带来更好绩效, 引用勿只取正向半句。
  - 〔Crossref 回读标题: Permissible collateral and access to finance: Evidence from a quasi-natural experiment〕
- Wang, Y., Zhang, Q., & Yang, X. (2020). Evolution of the Chinese guarantee network under financial crisis and stimulus program. *Nature Communications, 11*, Article 2693. https://doi.org/10.1038/s41467-020-16535-8
  - *锚定* — 刻画中国**企业间** (firm-to-firm) 贷款担保网络的结构演化与脆弱性 (危机收缩/刺激计划催生互保脆弱结构), 作为中国信贷语境下企业网络结构度量的间接类比锚。注: 网络主体为企业-企业而非企业-银行, 迁移到本管线银企共现须注明构念差异。
  - 〔Crossref 回读标题: Evolution of the Chinese guarantee network under financial crisis and stimulus program〕
- Gao, H., Ru, H., & Yang, X. (2022). The informational role of ownership networks in bank lending. *Journal of Financial and Quantitative Analysis, 57*(8), 2993–3017. https://doi.org/10.1017/S0022109021000788
  - *锚定* — 证明企业间**股权网络**传导的软信息可帮助银行内部评级更准预测违约 (对中小企业信息传导尤为重要), 作为网络化关联承载信贷信息渠道的**机制类比锚**。注: 原语境=股权网络, 本管线媒体共现权系构念迁移而非同一测度。
  - 〔Crossref 回读标题: The Informational Role of Ownership Networks in Bank Lending〕
- Lu, Z., Wu, J., Li, H., & Nguyen, D. K. (2022). Local bank, digital financial inclusion and SME financing constraints: Empirical evidence from China. *Emerging Markets Finance and Trade, 58*(6), 1712–1725. https://doi.org/10.1080/1540496X.2021.1923477
  - *锚定* — 发现本地银行网点占比越高中国中小企业融资约束越低, 直接锚定本管线②城市层银行网点权作为企业信贷可得性代理的构造决策。
  - 〔Crossref 回读标题: Local Bank, Digital Financial Inclusion and SME Financing Constraints: Empirical Evidence from China〕
- Gambacorta, L., Huang, Y., Li, Z., Qiu, H., & Chen, S. (2023). Data versus collateral. *Review of Finance, 27*(2), 369–398. https://doi.org/10.1093/rof/rfac022
  - *锚定* — 用中国小微企业信贷数据对比信息型(数据)与抵押型信贷技术, 锚定本管线『信息渠道(媒体共现)与实体接入渠道(网点)并列互稳』的多权重设计逻辑。
  - 〔Crossref 回读标题: Data versus Collateral〕
- 【2024–2026】Liang, Y., Zhou, B., & Zhao, S. (2024). Risking or de-risking? The effect of banking competition on large state-owned banks and small and medium-sized enterprise lending: Evidence from China. *International Review of Financial Analysis, 94*, Article 103258. https://doi.org/10.1016/j.irfa.2024.103258
  - *锚定* — 研究中国银行业竞争如何改变大型国有银行的中小企业贷款供给, 锚定本管线 110 家银行异质性(国有大行 vs 其他)在企业-银行权重解读中的意义。
  - 〔Crossref 回读标题: Risking or de-risking? The effect of banking competition on large state-owned banks and small and medium-sized enterprise lending: Evidence from China〕
- 【2024–2026】Liu, Y., Fujiwara, K., & Jinushi, T. (2024). Peer-to-peer lending for individual and MSME finance: Evidence from an original survey in China. *International Review of Economics & Finance, 93*, 38–51. https://doi.org/10.1016/j.iref.2024.02.038
  - *锚定* — 以原创调查刻画中国个体与小微企业在正规银行渠道之外的融资行为, 锚定税调非上市企业银行信贷约束讨论中的替代融资渠道基线。
  - 〔Crossref 回读标题: Peer-to-peer lending for individual and MSME finance: Evidence from an original survey in China〕
- 【2024–2026】Li, D., & Sun, Y. (2025). The impact of inclusive lending support on the performance of small and micro enterprises: Evidence from China. *Economic Analysis and Policy, 85*, 353–370. https://doi.org/10.1016/j.eap.2024.12.009
  - *锚定* — 用 2013–2022 中国数据估计普惠贷款支持对小微企业绩效的影响, 锚定本管线『银企信贷关联影响非上市小微企业绩效』的核心因果链 ⚠ 注: 样本为新三板挂牌中小企业 (有公开披露的公众公司), 外推到税调无披露非上市样本框须谨慎。
  - 〔Crossref 回读标题: The impact of inclusive lending support on the performance of small and micro enterprises: Evidence from China〕
- 【2024–2026】Ming, L., Wu, Y., Yang, S., & Yang, X. (2025). Fintech and large banks for SME financing: Evidence from China. *Accounting & Finance, 65*(2), 2106–2134. https://doi.org/10.1111/acfi.13395
  - *锚定* — 分析金融科技与大银行协作缓解中国中小企业融资难, 锚定本管线所处的银行×金融科技×中小企业交叉研究背景 (案例+fsQCA 混合方法研究, 作背景引用而非大样本因果证据)
  - 〔Crossref 回读标题: Fintech and large banks for SME financing: Evidence from China〕

### 八补-5. 企业实体匹配 / record linkage / 标识符 merge 键 (usci 统一社会信用代码 × 名称 variant AC 自动机匹配)

> 净增 14 条(其中 2024–2026 者 5 条)。

- Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. *Journal of the American Statistical Association, 64*(328), 1183–1210. https://doi.org/10.1080/01621459.1969.10501049
  - *锚定* — 概率记录链接的奠基理论 (错链/漏链权衡的最优判定规则), 为企业名×银行名匹配中精确匹配 vs 模糊匹配的取舍提供经典框架。
  - 〔Crossref 回读标题: A Theory for Record Linkage〕
- Lahiri, P., & Larsen, M. D. (2005). Regression analysis with linked data. *Journal of the American Statistical Association, 100*(469), 222–230. https://doi.org/10.1198/016214504000001277
  - *锚定* — 推导链接误差 (错配) 使链接后回归系数产生衰减偏误并给出无偏校正估计量, 锚定本管线披露共现权/网点权面板中匹配误差对下游估计的影响。
  - 〔Crossref 回读标题: Regression Analysis With Linked Data〕
- Wasi, N., & Flaaen, A. (2015). Record linkage using Stata: Preprocessing, linking, and reviewing utilities. *The Stata Journal, 15*(3), 672–697. https://doi.org/10.1177/1536867X1501500304
  - *锚定* — 提供公司名称解析标准化 (stnd_compname) 与概率链接 (reclink2) 的 Stata 实务工具, 直接锚定本管线 44,771 家企业 64,337 个名称变体的清洗与标准化步骤。
  - 〔Crossref 回读标题: Record Linkage Using Stata: Preprocessing, Linking, and Reviewing Utilities〕
- Enamorado, T., Fifield, B., & Imai, K. (2019). Using a probabilistic model to assist merging of large-scale administrative records. *American Political Science Review, 113*(2), 353–371. https://doi.org/10.1017/S0003055418000783
  - *锚定* — 可扩展到百万级行政记录的概率链接 (fastLink) 并把合并不确定性带入合并后分析, 锚定税调企业与新闻/网点行政数据的大规模合并方法选型。
  - 〔Crossref 回读标题: Using a Probabilistic Model to Assist Merging of Large-Scale Administrative Records〕
- Bailey, M. J., Cole, C., Henderson, M., & Massey, C. (2020). How well do automated linking methods perform? Lessons from US historical data. *Journal of Economic Literature, 58*(4), 997–1044. https://doi.org/10.1257/jel.20191526
  - *锚定* — 实证发现常用自动链接算法 15–37% 的链接被人工复核判为错误且假链接与样本特征系统相关, 锚定本管线对 fuzzy matching 偏误的警惕与优先精确标识符 (usci) 匹配的决策。
  - 〔Crossref 回读标题: How Well Do Automated Linking Methods Perform? Lessons from US Historical Data〕
- Abramitzky, R., Boustan, L., Eriksson, K., Feigenbaum, J., & Pérez, S. (2021). Automated linking of historical data. *Journal of Economic Literature, 59*(3), 865–918. https://doi.org/10.1257/jel.20201599
  - *锚定* — JEL 综述比较多种自动记录链接方法并显示保守设定可将假阳性率压到 5% 以下, 锚定本管线名称匹配采用保守全称+受控变体字典 (宁漏勿错) 的口径。
  - 〔Crossref 回读标题: Automated Linking of Historical Data〕
- Arora, A., Belenzon, S., & Sheer, L. (2021). Matching patents to Compustat firms, 1980–2015: Dynamic reassignment, name changes, and ownership structures. *Research Policy, 50*(5), Article 104217. https://doi.org/10.1016/j.respol.2021.104217
  - *锚定* — 构建专利-上市公司名称匹配时显式处理企业更名/曾用名与所有权结构的动态重指派并显示匹配改进改变回归估计, 锚定本管线把曾用名/括注变体纳入企业匹配字典的构造决策。
  - 〔Crossref 回读标题: Matching patents to compustat firms, 1980–2015: Dynamic reassignment, name changes, and ownership structures〕
- Binette, O., & Steorts, R. C. (2022). (Almost) all of entity resolution. *Science Advances, 8*(12), Article eabi8021. https://doi.org/10.1126/sciadv.abi8021
  - *锚定* — 实体消解 (记录链接/去重) 概率与贝叶斯方法的权威总览, 锚定本管线把同一企业的多名称变体归并到 usci 主键这一实体消解任务的方法学定位。
  - 〔Crossref 回读标题: (Almost) all of entity resolution〕
- Ward, Z. (2023). Intergenerational mobility in American history: Accounting for race and measurement error. *American Economic Review, 113*(12), 3213–3248. https://doi.org/10.1257/aer.20200292
  - *锚定* — 显示历史链接样本中对 race 与父辈职业地位测量误差的**联合**校正可使代际持久性估计翻倍 (测量误差使估计偏向更高流动性), 作为 (广义) 误差校正影响下游估计量级的警示锚。⚠ 注: 其测量误差为职业地位单次观测误差而非记录链接错配误差本身, 与本管线匹配误差的对接是量级警示而非同一构念。
  - 〔Crossref 回读标题: Intergenerational Mobility in American History: Accounting for Race and Measurement Error〕
- 【2024–2026】Arora, A., & Dell, M. (2024). LinkTransformer: A unified package for record linkage with transformer language models. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations)* (pp. 221–231). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.acl-demos.21
  - *锚定* — 面向社科的 transformer 记录链接软件包, 支持多语言 (含中文) 噪声字段与跨语言企业名链接, 锚定本管线企业名语义匹配作为字符串规则匹配之上的可选稳健性升级路径 注: 本条第一作者为 Abhishek Arora, 与本桶 DISCERN 条 (Matching patents to Compustat) 的 Ashish Arora 非同一人。
  - 〔Crossref 回读标题: LinkTransformer: A Unified Package for Record Linkage with Transformer Language Models〕
- 【2024–2026】Binette, O., Baek, Y., Engineer, S., Jones, C., Dasylva, A., & Reiter, J. P. (2024). How to evaluate entity resolution systems: An entity-centric framework with application to inventor name disambiguation. arXiv. https://doi.org/10.48550/arXiv.2404.05622
  - *锚定* — 提出实体中心 (而非记录对层面) 的实体消解系统评估框架并应用于发明人名称消歧, 锚定本管线企业匹配质量评估 (实体层 precision/recall 抽检) 的指标设计 (arXiv preprint, 未同行评审)
  - 〔DataCite 回读标题: How to Evaluate Entity Resolution Systems: An Entity-Centric Framework with Application to Inventor Name Disambiguation〕
- 【2024–2026】Steiner, A., Peeters, R., & Bizer, C. (2025). Fine-tuning large language models for entity matching. In *2025 IEEE 41st International Conference on Data Engineering Workshops (ICDEW)* (pp. 9–17). IEEE. https://doi.org/10.1109/ICDEW67478.2025.00006
  - *锚定* — 实验评估微调 LLM 做实体匹配的效果与泛化, 锚定本管线未来以 LLM 辅助企业名-新闻提及匹配作稳健性交叉验证的前沿参照。
  - 〔Crossref 回读标题: Fine-Tuning Large Language Models for Entity Matching〕
- 【2024–2026】Tam, S.-M., Wang, M., Rambaldi, A., & Tao, D. (2025). On linkage bias-correction for estimators using iterated bootstraps. arXiv. https://doi.org/10.48550/arXiv.2511.05004
  - *锚定* — 用迭代 bootstrap 构造链接数据集上模型参数的链接偏误校正估计量, 锚定共现权重面板中匹配误差偏误校正的敏感性检验方案。
  - 〔DataCite 回读标题: On linkage bias-correction for estimators using iterated bootstraps〕
- 【2024–2026】Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. *Statistical Science, 41*(1). https://doi.org/10.1214/24-STS939
  - *锚定* — 把记录链接视为缺失数据问题, 系统梳理链接误差下的三类下游推断校正方法 (似然/贝叶斯、插补、加权), 锚定本管线链接后分析阶段对错链/漏链误差的处置框架。
  - 〔Crossref 回读标题: Analysis of Linked Files: A Missing Data Perspective〕

### 八补-6. 暴露度权重构造与替代权重规格稳健性 (报道共现权 + 城/县网点权三权互稳 · 各自 just-identified 并排)

> 净增 6 条(其中 2024–2026 者 3 条)。⚠ 铁律: 报道共现权 + 城市网点权 + 县域网点权三权互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。本桶净增少 (6 条) 系 shift-share 核心件 (Goldsmith-Pinkham/Borusyak/Adão 等) 已在前编收录, 查重剔除所致。

- Gilje, E. P., Loutskina, E., & Strahan, P. E. (2016). Exporting liquidity: Branch banking and financial integration. *The Journal of Finance, 71*(3), 1159–1184. https://doi.org/10.1111/jofi.12387
  - *锚定* — 奠基经典: 以银行分支网点的地理布局界定流动性冲击向异地信贷市场的传导暴露, 是网点层地理暴露设计 (branch-network exposure) 的代表性范式, 锚定本管线城市/县域网点权的设计谱系。
  - 〔Crossref 回读标题: Exporting Liquidity: Branch Banking and Financial Integration〕
- Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021). The influence of hidden researcher decisions in applied microeconomics. *Economic Inquiry, 59*(3), 944–960. https://doi.org/10.1111/ecin.12992
  - *锚定* — 多团队复现同一应用微观问题时隐性数据构造决策 (样本、变量定义) 导致估计显著分歧, 锚定本管线把共现计权与网点计权等数据构造决策显式化并做替代规格披露。
  - 〔Crossref 回读标题: The influence of hidden researcher decisions in applied microeconomics〕
- Borusyak, K., & Hull, P. (2023). Nonrandom exposure to exogenous shocks. *Econometrica, 91*(6), 2155–2185. https://doi.org/10.3982/ECTA19367
  - *锚定* — 公式化组合多源变异的暴露变量在暴露非随机时产生遗漏变量偏差, 给出 recentering 修正 (应用=中国高铁扩张冲击)。⚠ 注: 该修正以暴露含 (条件) 外生 shock 成分为前提; 本管线网点权/共现权现阶段为描述性暴露测度, 引用应定位为'若未来将其用作 shift-share 式处理或工具'时的偏差诊断与修正参照, 非现行构造的直接依据。
  - 〔Crossref 回读标题: Nonrandom Exposure to Exogenous Shocks〕
- 【2024–2026】Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration. (2024). Reproducibility in Management Science. *Management Science, 70*(3), 1343–1356. https://doi.org/10.1287/mnsc.2023.03556
  - *锚定* — 对近 500 篇 Management Science 论文做大规模计算可复现性评估, 锚定本管线派生面板全链路确定性复现 (registry 哈希/字节等价) 工程规范的期刊侧依据。
  - 〔Crossref 回读标题: Reproducibility in Management Science〕
- 【2024–2026】Li, X., Shao, X., Shen, G., & Zou, J. (2025). Bank competition and formation of zombie firms: Evidence from banking deregulation in China. *Journal of Banking & Finance, 172*, Article 107390. https://doi.org/10.1016/j.jbankfin.2025.107390
  - *锚定* — 利用中国 2009 年中小银行分支市场准入放开的准实验研究地方银行竞争对企业僵尸化的两阶段效应, 为本管线在地银行竞争/网点进入暴露的中国场景提供准实验先例。注: 其竞争度量构造细节 (是否用既有网点布局/许可证口径) 摘要级不可核, 引用时以其正文为准。
  - 〔Crossref 回读标题: Bank competition and formation of zombie firms: Evidence from banking deregulation in China〕
- 【2024–2026】Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. *Journal of Corporate Finance, 93*, Article 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
  - *锚定* — 以同句共提及 + NLP 关系分类从财经新闻构建加密资产 peer 网络, 发现 peer 间由投资者过度反应驱动的条件反向共动 (数周内修正的错误定价), 为新闻共提及可提取经济关系网络提供方法先例。⚠ 注: 其 peer 判据 (同句+竞争关系分类) 与市场语境 (加密资产投机市场) 均与本管线银企共现权不同, 头条结论是媒体驱动 mispricing 而非共现网络效度验证, 引用须注明边界。
  - 〔Crossref 回读标题: News-driven peer co-movement in crypto markets〕

---

## 二、核验记录 (决定性闸 + 评审轮)

- **机械闸三轮** (`scripts/audit/audit_dois.py`, 直连 Crossref/DataCite, 100% 覆盖非抽样): R1 前 745 唯一 DOI 轮与 R1 补入后 750 唯一 DOI 两轮、终稿字节态再一轮 — 三轮均 **747 OK + 仅 3 条既有 benign** (CNKI 10.13821 目录 404 / ACL BERT 10.18653 目录 404 / SSRN 3446388 年差), **零新增 flag**。
- **R1 8 路对抗评审**: 6 桶逐条真实摘要比对 + 格式/口径一致性 + 完备性批评者; 1 P0 + 7 P1 + 10 P2 + NIT 全数修复, 完备性补 5 条真缺口锚。
- **R2 双路复核**: 修复方向逐条对照原文验证 + 终稿格式全查; 抓获并修复"字典键被批内重复记录覆盖致 2 处 R1 修复未落地"。
- **终审双路 (max 标准, 独立抽验)**: 6 桶各抽 3 条 + 全部 2026 年条目逐条 Crossref 确证 (7 条 2026 全部真实存在、零幻觉, 其中 Zhang et al. 2026 JAE 的"税调数据+道路级邻近"宣称经原文摘要逐点确证); 双路判定 **ok_to_ship、零 P0/P1**, 残余 NIT (Economica 期号/en-dash 残留/sentence case/卷期年短注/指称消歧/本节补齐) 已全部落实于本版。
