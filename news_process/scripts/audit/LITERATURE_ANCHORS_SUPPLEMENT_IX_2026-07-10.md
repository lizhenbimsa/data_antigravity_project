# 文献理论锚点扩充报告 · 第九补编(三文件夹功能专项: 银企共现权重源两管线补遗 + LLM 金融科技词典 LLMs_for_FinTech_dic 全量 · 2024–2026 最新文献优先 · 6 主题桶 · APA 第 7 版 · Crossref/DataCite DOI→标题回比 + 权威元数据逐条回填全核验)

- **日期**: 2026-07-10
- **定位**: 本文件是前八份锚点文件之后的 **第九补编**, 十者**合为一套**。前八份 = **760 条 / 750 唯一 doi.org DOI**(第八补编头部口径; 第八补编为同日并行会话产出的 company_tax_bank 税调专项 79 条, 本补编与其**已全量去重**, 重叠 27 条已剔)。
- **本补编专项**: 为三个文件夹的功能补齐主锚点体系(含第八补编)仍未覆盖的学术出处 —— ① `company_listed_bank/` 与 `company_tax_bank/`(银企共现面板两管线: **网点权重补遗、税调/行政数据补遗、实体解析/名称匹配补遗** —— 经典主干已由第八补编收录, 本补编收其余缺口与 2024–2026 前沿); ② `LLMs_for_FinTech_dic/`(**8 个异构 LLM 三阶段构建 1,506 词金融科技词典**: 零样本并发生成→子串包容规约→交叉盲审多数投票, Fleiss κ=0.5017 词项级截断 —— 该文件夹的 **LLM-as-a-judge / 多模型集成 / 多评估者一致性 / 词典效度**四主题在既有全池零或近零覆盖, 为本补编主体)。
- **规模**: 6 主题桶并行动态多智能体工作流发现(每候选提名前实时 GET api.crossref.org / api.datacite.org 读回标题自比对) → 主控**逐条直连 Crossref/DataCite 回填权威书目元数据**(作者序/年份/卷期/页码/标题, 106/106 零解析失败、零标题不符) → APA 由回填元数据**程序化机械拼装**(非人工转写) → 三重去重(对既有池 671 DOI + 第八补编 79 DOI + LLMs_for_FinTech_dic 自有 43 条有效引文; 候选间跨桶重复另剔 8 条) = **净增 79 条唯一锚点**, 其中 **2024–2026 者 33 条(42%)**, 工作论文(NBER/SSRN/arXiv) 若干条均以真实可解析 DOI 收录。
- **同期修复**(与本补编同一轮, 详见 §二): `LLMs_for_FinTech_dic/` 两份文档自带 82 条引文经机械审计, 72 个唯一 DOI 中 **29 个标红**; 判定为 5 提取伪影(实际正确) / **18 错 DOI 已找回真 DOI 并双重核验替换** / **5 论文不存在(疑似生成幻觉)已删除或以真实文献替换** / 1 条 LDA 原典 DOI 属 Crossref 已删除 DOI(改官方 JMLR 链接)。修复后两份 md 已并入 `audit_dois.py::FILES` 机械闸永久覆盖。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编经**发现层自核验 + 主控独立回填 + 全语料机械闸 + 对抗性 claim-fit 评审**四道核验; 全语料本地决定性闸 = `scripts/audit/audit_dois.py`。
- **合计**: 760(前八份) + **79(本补编净增)** = **839 条**唯一文献锚点(唯一 doi.org DOI 数以 audit_dois.py 实测为准)。

---

## 〇、白话导读

**这份补的是什么**: 项目新添了三摊活: 两条"哪家企业和哪家银行一起上新闻"的面板生产线(一条对上市公司, 一条对 4.5 万家税调企业), 和一个"让 8 个大模型投票编金融科技词典"的工具。同日并行的第八补编已把税调管线的主干文献(网点=信贷通道的经典链、税调数据顶刊先例、记录联结方法学)配齐; 本第九补编补两块: ① 两管线主干之外的**剩余缺口与最新前沿**(如 2024-26 网点关闭新作、中国税调数据 2024-26 新应用、匹配误差对回归的偏误); ② **大模型词典工具的全套出处**——8 个模型投票筛词这件事, 2023-2026 年恰好爆发了一整支文献: 大模型能不能替代人工标注(能, 且多篇顶刊已验证)、让多个模型投票能不能压住单个模型的幻觉(能, "评审团优于单一裁判"有直接证据)、大模型当裁判有什么系统性偏差(位置偏差/自我偏爱, 须知情披露)、模型标的数据进回归要不要纠偏(要, 已有专门计量框架)、以及 Fleiss Kappa 这类"多个评委意见有多一致"的统计量怎么用才规范(含 κ 悖论: 基线一致率高时 κ 被压低——本项目 P_e=0.518 正中此议题, 引用时须披露)。

**顺手抓出的问题**: 检查时发现词典文件夹自带的参考文献表**有将近三分之一的 DOI 是坏的**——有的链接指向完全无关的论文, 有的论文压根不存在(典型的 AI 生成幻觉, 如一篇声称发在 JCF 的 "AI in corporate governance" 和一篇 MS 的 "ML models in portfolio optimization", 多路检索均无此文)。这次全部逐条查实: 能修的修(18 条找回了真链接), 修不了的删(5 条假文献), 每一步都有 Crossref 官方接口的回读证据, 台账见 §二。

**怎么用**: 写论文/codebook 时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。每条的〔回读标题〕就是官方接口实际返回值。工作论文条目引用时须标注 working paper 状态。

**一句话铁律提醒**: 税调管线的**三权重**(共现报道权/城市网点权/县域网点权)与上市管线的**七替代权**均为"互为稳健性、不分主次"——各自 just-identified 并排, **严禁混进同一 over-identified Hansen J**; LLM 词典的 8 模型亦同理: 各模型判定互为稳健性, 投票共识是唯一 headline, **不得把多模型判定混作多工具变量**(与代码 codebook 铁律一致, 引用时须在方法节写明)。

---

## 一、6 主题桶 × 新增已核验锚点(2024–2026 优先; 〔〕内为回读标题; 与第八补编重叠者已剔)

### 九补-1. 银行网点网络作为暴露/权重 (company_tax_bank 城市/县域网点权 · company_listed_bank 七替代权之 branch 权)

> 净增 6 条(其中 2024–2026 者 3 条)。

- Beck, T., Demirguc-Kunt, A., & Martinez Peria, M. S. (2007). Reaching out: Access to and use of banking services across countries. *Journal of Financial Economics*, *85*(1), 234-266. https://doi.org/10.1016/j.jfineco.2006.07.002
  - *锚定* — 网点密度作为金融可达性测度的 method-origin: 首创以每单位人口/面积银行网点数(branch penetration)刻画银行服务可及性, 直接锚定 company_tax_bank 管线 03 用《银行业金融机构基本信息表》构造的银行×地区网点密度权重。迁移边界: 原文为跨国宏观截面口径, 本项目下沉到中国城市/县域×单家银行层级, 密度定义(除以人口/面积 vs 原始网点数占比)需在文中说明。
  - 〔Crossref 回读标题: Reaching out: Access to and use of banking services across countries〕
- Benmelech, E., Yang, J., & Zator, M. (2023). Bank Branch Density and Bank Runs (NBER Working Paper No. 31462). National Bureau of Economic Research. https://doi.org/10.3386/w31462
  - *锚定* — 网点密度(branch density)作为银行层特征测度的最新代表作: 以每单位存款/地理面积网点数刻画银行经营模式并解释挤兑脆弱性差异, 与本项目'银行×地区网点密度权'同一测度族, 证明该统计量在 2020s 仍是活跃研究对象。迁移边界: 其密度是银行总体特征而非银行×地区双下标权重; 且 DV 是挤兑而非银企关联, 属测度同源、问题不同。
  - 〔Crossref 回读标题: Bank Branch Density and Bank Runs〕
- Sun, R., Zhou, N., & Zhang, B. (2023). Can bank branch establishment help SMEs survive? Evidence from China. *International Review of Financial Analysis*, *88*, 102694. https://doi.org/10.1016/j.irfa.2023.102694
  - *锚定* — 中国语境直接锚点: 用中国银行网点区位微观数据 (SME 周边给定半径内网点数, 1,800 万+ 家 SME, 与本项目《银行业金融机构基本信息表》同一测度族) 考察网点设立对中小企业存续的因果效应, 证明中国网点微观数据可支撑企业级识别。迁移边界: 其单位是网点设立事件×企业存续, 本项目是网点存量密度×新闻共现加权, 口径不同; 其数据源是否即银保监金融许可证系统未据正文核实, 不作同源断言。
  - 〔Crossref 回读标题: Can bank branch establishment help SMEs survive? Evidence from China〕
- 【2024–2026】Wang, Y., & Wu, S. (2024). Impact of mobile banking on small business lending after bank branch closures. *Journal of Corporate Finance*, *87*, 102593. https://doi.org/10.1016/j.jcorpfin.2024.102593
  - *锚定* — 2024 年 branch closure 新作 (JCF): 银行**自有移动 app** (bank-level app presence, matched bank-county 设计) 可部分缓解 (约 18.8%) 网点关闭对小企业信贷的负效应, 但原文同时强调**物理网点对本地信贷仍不可或缺** (开设新网点时 app 无显著效应)——引作 fintech 部分替代网点渠道的机制动机时, 须一并披露『替代是部分的、网点仍重要』这一反向半句 (恰支撑本项目网点权在样本期内仍有效力)。迁移边界: 美国县级数据; 引作机制动机, 非识别模板。
  - 〔Crossref 回读标题: Impact of mobile banking on small business lending after bank branch closures〕
- 【2024–2026】Chen, M., Sun, Y., & Zhang, W. (2025). Bank branch closure and entrepreneurship in China. *SSRN*. https://doi.org/10.2139/ssrn.5232569
  - *锚定* — 2025 年中国网点关闭工作论文: 以中国网点退出考察对创业活动的影响, 是'中国+网点关闭+实体后果'三要素齐备的最新前沿, 补齐桶内 2024-26 中国分支。迁移边界: SSRN 工作论文未经同行评审, 引用须标注 working paper 状态; DV 为创业而非银企信贷关系。
  - 〔Crossref 回读标题: Bank branch closure and entrepreneurship in China〕
- 【2024–2026】Kladakis, G., & Skouralis, A. (2025). The dark side of bank branch closures. *SSRN*. https://doi.org/10.2139/ssrn.5841042
  - *锚定* — 2025 年网点关闭负外部性前沿工作论文, 代表 branch closure 文献的最新一波, 用于文献综述中标注该议题在 2024-26 仍活跃、网点存在性测度未过时。迁移边界: SSRN 未评审工作论文, 具体样本国别与结论以引用时核对全文为准, 仅作前沿存在性引用。
  - 〔Crossref 回读标题: The dark side of bank branch closures〕

### 九补-2. 税收调查/行政企业微观数据 (company_tax_bank 44,771 家税调企业样本框 · usci×year merge 键)

> 净增 13 条(其中 2024–2026 者 5 条)。

- 【2024–2026】Xing, J., Bilicka, K., Hou, X., & Raei, S. (2024). How distortive are turnover taxes? Evidence from China. *Journal of Development Economics*, *171*, 103332. https://doi.org/10.1016/j.jdeveco.2024.103332
  - *锚定* — 税调数据 2024 年国际期刊新应用 (JDE): 用中国全国税收调查数据研究流转税扭曲, 证明该数据在 2024-26 前沿仍是活跃研究基础设施, 样本年窗与本项目 2011–2020 面板窗**重叠** (营改增政策期 2012–2016 为其核心窗口, 是否覆盖全窗须核对原文数据节)。边界: 主题为税制扭曲, 与银企媒体共现构念无关, 仅锚定数据源。
  - 〔Crossref 回读标题: How distortive are turnover taxes? Evidence from China〕
- 【2024–2026】Niu, Q., Yuan, J., Kang, F., & Wen, L. (2025). VAT credit refund policy and corporate risk-taking: Evidence from China. *Finance Research Letters*, *81*, 107478. https://doi.org/10.1016/j.frl.2025.107478
  - *锚定* — 2025 年最新发表: 中国增值税留抵退税政策与企业风险承担, 锚定税收政策×企业金融行为 (与本项目银企关系构念最近邻) 的 2024-26 前沿文献带。边界: FRL 短文, 数据为上市公司而非税调全样本的可能性存在, 引用时按'税收政策-企业金融'谱系而非税调数据谱系归位。
  - 〔Crossref 回读标题: VAT credit refund policy and corporate risk-taking: Evidence from China〕
- 【2024–2026】Wang, B., Wang, X., & Qin, C. (2025). Can Tax Incentives Promote Corporate Digital Transformation? Evidence from China’s Accelerated Depreciation of Fixed Assets Policy. *China Finance and Economic Review*, *14*(2), 108-128. https://doi.org/10.1515/cfer-2025-0012
  - *锚定* — 2025 年加速折旧政策×企业数字化转型实证, 锚定任务点①中'固定资产加速折旧'政策评估的 2024-26 延续文献, 且数字化转型构念与本项目金融科技语境相邻。边界: 非顶刊; 据 Crossref 摘要其样本为 A 股上市公司 2012–2022 (交错 DiD), **非**税调数据——引作加速折旧政策评估谱系的延续文献而非税调数据源先例; 作为前沿补充锚而非承重锚。
  - 〔Crossref 回读标题: Can Tax Incentives Promote Corporate Digital Transformation? Evidence from China’s Accelerated Depreciation of Fixed Assets Policy〕
- 【2024–2026】Yang, X., Wan, P., & Yang, M. (2026). How polluting enterprises respond to Pigovian tax: Evidence from China's environmental protection tax law. *China Economic Review*, *98*, 102723. https://doi.org/10.1016/j.chieco.2026.102723
  - *锚定* — 2026 年最新: 中国企业对环保税 (庇古税) 的微观响应, 锚定中国税制改革×企业微观行为面板的当下前沿。边界: 环境税语境, 数据源是否全国税收调查需正文核对; 仅作'中国税收微观实证仍活跃'的时效性锚, 不承重。
  - 〔Crossref 回读标题: How polluting enterprises respond to Pigovian tax: Evidence from China's environmental protection tax law〕
- Pomeranz, D. (2015). No Taxation without Information: Deterrence and Self-Enforcement in the Value Added Tax. *American Economic Review*, *105*(8), 2539-2569. https://doi.org/10.1257/aer.20130393
  - *锚定* — 任务点② method-origin: 智利税务局全量行政增值税数据+随机实验的经典范式, 锚定'税务行政数据做企业微观实证'的国际方法论谱系, 佐证本项目以税调行政数据为样本框的做法处于成熟传统之内。边界: 智利语境+实验设计, 需迁移; 本项目为观察性面板。
  - 〔Crossref 回读标题: No Taxation without Information: Deterrence and Self-Enforcement in the Value Added Tax〕
- Zwick, E., & Mahon, J. (2017). Tax Policy and Heterogeneous Investment Behavior. *American Economic Review*, *107*(1), 217-248. https://doi.org/10.1257/aer.20140855
  - *锚定* — 行政报税数据做企业投资响应识别的标杆 (AER 2017): 基于 IRS 行政报税数据的 12 万+ 企业大样本面板 (数十万 firm-year 观测), 锚定『税务行政数据→企业面板→因果识别』的国际黄金标准路线, 与本项目税调样本框同族。边界: 美国折旧政策语境, 仅作数据基础设施先例。
  - 〔Crossref 回读标题: Tax Policy and Heterogeneous Investment Behavior〕
- Kleven, H. J., Knudsen, M. B., Kreiner, C. T., Pedersen, S., & Saez, E. (2011). Unwilling or unable to cheat? Evidence from a tax audit experiment in Denmark. *Econometrica*, *79*(3), 651-692. https://doi.org/10.3982/ecta9113
  - *锚定* — 任务点② method-origin: 丹麦全民税务行政记录+审计实验的奠基之作, 锚定'税务行政数据=近乎零测量误差的微观面板'这一方法论主张, 用于论证税调行政数据相对商业数据库的质量优势。边界: 丹麦个人所得税语境, 迁移到中国企业税调需明示制度差异; Crossref 回读无作者字段, 作者名单已据原刊补全 (Crossref 该 DOI 作者字段缺失, 属元数据登记缺陷)。
  - 〔Crossref 回读标题: Unwilling or Unable to Cheat? Evidence From a Tax Audit Experiment in Denmark〕
- Pomeranz, D., & Vila-Belda, J. (2019). Taking State-Capacity Research to the Field: Insights from Collaborations with Tax Authorities. *Annual Review of Economics*, *11*(1), 755-781. https://doi.org/10.1146/annurev-economics-080218-030312
  - *锚定* — 任务点②方法论综述: 系统总结与各国税务机关合作使用行政税务数据的经验、代表性与偏差问题, 是讨论税调数据代表性 (44,771 家样本框是否有选择性) 时的规范引用。边界: 综述覆盖发展中国家税务合作, 未专论中国税调。
  - 〔Crossref 回读标题: Taking State-Capacity Research to the Field: Insights from Collaborations with Tax Authorities〕
- Bustos, S., Pomeranz, D., Suárez Serrato, J. C., Vila-Belda, J., & Zucman, G. (2022). The Race Between Tax Enforcement and Tax Planning: Evidence From a Natural Experiment in Chile (NBER Working Paper No. 30114). National Bureau of Economic Research. https://doi.org/10.3386/w30114
  - *锚定* — 任务点②优秀工作论文: 智利全量企业税务行政数据 (含跨境关联交易记录) 的准实验研究, 锚定 2020s 行政税务大数据做企业面板的国际前沿实践。边界: 智利转让定价语境, 需迁移; NBER WP 版本, 引用时可注明后续期刊版本待查。
  - 〔Crossref 回读标题: The Race Between Tax Enforcement and Tax Planning: Evidence From a Natural Experiment in Chile〕
- Cui, W. (2022). *The Administrative Foundations of the Chinese Fiscal State*. Cambridge University Press. https://doi.org/10.1017/9781108868648
  - *锚定* — 任务点②③交叉: 系统论述中国税收征管体系的制度基础与数据生成过程 (论述中国税收征管体系与数据生成过程), 是解释税调数据'如何产生、覆盖谁、有何行政偏差'的权威专著级引用。边界: 法学/政治经济学专著, 非计量实证; 用于数据生成过程 (DGP) 制度背景段。
  - 〔Crossref 回读标题: The Administrative Foundations of the Chinese Fiscal State〕
- Brandt, L., Van Biesebroeck, J., & Zhang, Y. (2014). Challenges of working with the Chinese NBS firm-level data. *China Economic Review*, *30*, 339-352. https://doi.org/10.1016/j.chieco.2014.04.008
  - *锚定* — 任务点③指名文献: 对中国国家统计局工企数据库质量问题 (变量断档、口径漂移、匹配失败) 的系统批评, 是论证'为何改用税调数据+统一社会信用代码精确 merge'的直接对照锚。边界: 批评对象是 NBS 工企库而非税调, 引用逻辑为反衬。
  - 〔Crossref 回读标题: Challenges of working with the Chinese NBS firm-level data〕
- Chen, S., Schuchard, K., & Stomberg, B. (2019). Media Coverage of Corporate Taxes. *The Accounting Review*, *94*(5), 83-116. https://doi.org/10.2308/accr-52342
  - *锚定* — 任务点④: 将媒体新闻文本与企业税务属性合并构造'企业×媒体报道'数据的顶级会计学先例, 与本项目'税调企业×银企共现媒体报道面板'在数据结构上同型。边界: 美国上市公司+英文媒体语境, 报道对象是税收议题本身而非银企关系, 需迁移。
  - 〔Crossref 回读标题: Media Coverage of Corporate Taxes〕
- 【2024–2026】Li, K., Lu, L. Y., & Wang, K. (2025). From Firms to Faces: How Journalist–Manager Relationships Shape Corporate Media Coverage. *SSRN*. https://doi.org/10.2139/ssrn.5648287
  - *锚定* — 任务点④近期实践 (2025 工作论文): 微观关系数据×企业媒体报道面板的最新 merge 实践, 锚定'企业级媒体覆盖由可观测微观联结驱动'这一与银企共现报道面板同构的识别关切 (报道生成非随机)。边界: SSRN 未发表工作论文, 记者-高管关系语境, 需迁移且不承重。
  - 〔Crossref 回读标题: From Firms to Faces: How Journalist–Manager Relationships Shape Corporate Media Coverage〕

### 九补-3. 实体解析/记录联结/公司名称匹配 (两管线 01 registry 名称变体 AC 匹配 + 裁剪负清单)

> 净增 10 条(其中 2024–2026 者 3 条)。

- Price, J., Buckles, K., Van Leeuwen, J., & Riley, I. (2021). Combining family history and machine learning to link historical records: The Census Tree data set. *Explorations in Economic History*, *80*, 101391. https://doi.org/10.1016/j.eeh.2021.101391
  - *锚定* — 用外部辅助信息 (家谱树) 扩充联结训练集的大规模记录联结实践, 类比本项目用 iFind 曾用名/简称/括注等 64,337 个名称变体作为外部先验字典扩充匹配召回。迁移边界: 其 ML 监督联结与本项目无监督字典匹配路线不同, 仅锚定'外部结构化先验提升联结覆盖'这一层。
  - 〔Crossref 回读标题: Combining family history and machine learning to link historical records: The Census Tree data set〕
- Kim, G., & Chambers, R. (2015). Unbiased regression estimation under correlated linkage errors. *Stat*, *4*(1), 32-45. https://doi.org/10.1002/sta4.76
  - *锚定* — 把联结误差偏误分析扩展到误差相关场景的二次分析文献, 锚定本项目同一歧义短名在多篇报道中系统性误匹配 (误差非独立、按名称聚簇) 时对面板估计的相关性误差风险。迁移边界: 抽样调查联结语境, 其无偏估计量在项目场景不可实施, 引用限于误差相关性的定性风险刻画。
  - 〔Crossref 回读标题: Unbiased regression estimation under correlated linkage errors〕
- Thoma, G., Torrisi, S., Gambardella, A., Guellec, D., Hall, B., & Harhoff, D. (2010). Harmonizing and Combining Large Datasets - An Application to Firm-Level Patent and Accounting Data (NBER Working Paper No. 15851). National Bureau of Economic Research. https://doi.org/10.3386/w15851
  - *锚定* — 公司名称标准化 (harmonization) 与跨库企业匹配的经典工作论文, 锚定项目把 5,528/44,771 家企业的官方名/曾用名/简称统一成匹配字典的名称规范化环节。迁移边界: 专利-财务数据匹配语境且为 2010 年规则法, 不能佐证匹配精度数值, 只锚定名称标准化的方法必要性。
  - 〔Crossref 回读标题: Harmonizing and Combining Large Datasets - An Application to Firm-Level Patent and Accounting Data〕
- 【2024–2026】Libgober, B., & Jerzak, C. T. (2025). Linking datasets on organizations using half a billion open-collaborated records. *Political Science Research and Methods*, *13*(4), 923-942. https://doi.org/10.1017/psrm.2024.55
  - *锚定* — 最新的组织/机构级 (非个人级) 记录联结方法 (LinkOrgs), 用众包别名网络解决机构名称变体问题, 与项目用 iFind 名称变体字典解决同一问题同构, 是机构名联结的 2024 年方法前沿锚点。迁移边界: 其别名图谱基于 LinkedIn 英文记录, 中文企业变体需自建 (项目已自建), 引用限于方法论同构性。
  - 〔Crossref 回读标题: Linking datasets on organizations using half a billion open-collaborated records〕
- Yang, X., Arora, A., Jheng, S.-Y., & Dell, M. (2023). Quantifying Character Similarity with Vision Transformers. *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, 13982-13996. https://doi.org/10.18653/v1/2023.emnlp-main.863
  - *锚定* — CJK 文字记录联结的对照文献 (EMNLP 2023): 该文指出统一代价的现成字符串匹配与手工替换代价清单在 CJK 等低资源文字场景缺失/表现不佳, 提出视觉 Transformer homoglyph 相似度作为 Levenshtein 编辑距离的替换代价、实现 CJK **模糊**匹配 (日本企业记录联结验证, 面向 OCR 错字场景)。**引用方向**: 本项目新闻文本无 OCR 噪声、名称变体已由 iFind 字典枚举, 故走变体字典+精确 AC 匹配而**未采用**其模糊路线——本文作为『为何不走模糊匹配』的对照与动机引注, 非精确路线的支撑文献。
  - 〔Crossref 回读标题: Quantifying Character Similarity with Vision Transformers〕
- Li, Y., Li, J., Suhara, Y., Doan, A., & Tan, W.-C. (2020). Deep entity matching with pre-trained language models. *Proceedings of the VLDB Endowment*, *14*(1), 50-60. https://doi.org/10.14778/3421424.3421431
  - *锚定* — 预训练语言模型实体匹配的标杆方法 (Ditto), 是数据库界实体匹配从规则/字典转向 PLM 的分水岭文献, 为项目匹配方案的方法谱系定位提供 NLP 侧锚点。迁移边界: 需带标注训练对做二分类微调, 项目零标注、字典驱动, 仅作方法谱系对照。
  - 〔Crossref 回读标题: Deep entity matching with pre-trained language models〕
- 【2024–2026】Huang, Z. (2024). Disambiguate Entity Matching using Large Language Models through Relation Discovery. *Proceedings of the Conference on Governance, Understanding and Integration of Data for Effective and Responsible AI*, 36-39. https://doi.org/10.1145/3665601.3669844
  - *锚定* — LLM 用于实体匹配歧义场景的前沿动向示例 (2024 workshop 短文): 以 LLM 发现记录间关系以消解『相关但非同一实体』的记录对歧义。迁移边界: 其歧义类型 (记录对间关系) 与本项目负清单所防的**提及级同形词歧义** (公司短名与地名/常用词同形) 不是同一构念, 仅作 LLM+实体匹配方向的存在性引用, 不承重。
  - 〔Crossref 回读标题: Disambiguate Entity Matching using Large Language Models through Relation Discovery〕
- 【2024–2026】Çeliktuğ, M. F., & Kantarcıoğlu, M. (2024). Power of Sentence Transformers in Record Linkage. *2024 IEEE International Conference on Big Data (BigData)*, 6944-6955. https://doi.org/10.1109/bigdata62323.2024.10825999
  - *锚定* — 2024 年句向量嵌入用于记录联结的系统评测, 与项目双轨嵌入基础设施 (Qwen3/text-embedding-3-large) 天然衔接, 锚定'嵌入相似度可作 AC 精确匹配的召回审计轨'这一潜在稳健性检验设计。迁移边界: 项目现行匹配不用嵌入, 引用为方法可行性佐证而非已实施功能。
  - 〔Crossref 回读标题: Power of Sentence Transformers in Record Linkage〕
- Schwenkler, G., & Zheng, H. (2019). The Network of Firms Implied by the News. *SSRN*. https://doi.org/10.2139/ssrn.3320859 (注: 2020 年有更新修订版 ssrn.3664879/ssrn.3723464, 无期刊版)
  - *锚定* — 金融学中从新闻文本识别公司实体并构建公司网络的直接同域先例: 其流水线同样始于新闻-公司实体识别与别名消歧, 终于公司共现网络, 与项目'企业×银行新闻共现面板+网络溢出指标'高度同构, 是⑤类 news-firm entity linking 的核心锚点。迁移边界: 英文财经新闻+美国上市公司语境; SSRN 工作论文版本, 引用时注明未刊状态。
  - 〔Crossref 回读标题: The Network of Firms Implied by the News〕
- Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C. (2022). Neural entity linking: A survey of models based on deep learning. *Semantic Web*, *13*(3), 527-570. https://doi.org/10.3233/sw-222986
  - *锚定* — 神经实体链接 (candidate generation→消歧) 的系统综述, 锚定项目'变体字典生成候选+负清单消歧'两阶段结构与 NLP 实体链接标准架构的对应关系, 并为 alias resolution 术语提供规范出处。迁移边界: 综述面向知识库链接 (链到 Wikidata 等), 项目链到自建企业 registry, 无知识库嵌入环节。
  - 〔Crossref 回读标题: Neural entity linking: A survey of models based on deep learning〕

### 九补-4. LLM 群体标注/LLM-as-a-Judge/多模型集成投票 (LLMs_for_FinTech_dic 三阶段词典构建)

> 净增 18 条(其中 2024–2026 者 13 条)。

- 【2024–2026】Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. *Proceedings of the National Academy of Sciences*, *121*(34), Article e2308950121. https://doi.org/10.1073/pnas.2308950121
  - *锚定* — GPT 多语言心理文本分析的基准验证 (PNAS 2024): **以人工标注为评判基准**, GPT (相关系数 r=0.59–0.77) 大幅优于英文词典法 (r=0.20–0.30), 接近乃至偶超微调 ML 模型, 且跨 12 种语言稳健——锚定 LLM 判定优于词典基线、且多语言 (含非英语) 可用的证据。迁移边界: 心理构念 (情绪/道德化) 非金融术语判定; 人工标注在该设计中是 ground truth, 不存在『超过人工』的比较。
  - 〔Crossref 回读标题: GPT is an effective tool for multilingual psychological text analysis〕
- 【2024–2026】Heseltine, M., & Clemm von Hohenberg, B. (2024). Large language models as a substitute for human experts in annotating political text. *Research & Politics*, *11*(1), Article 20531680241236239. https://doi.org/10.1177/20531680241236239
  - *锚定* — LLM 替代人工专家标注的直接证据 (2024): GPT-4 对政治文本的编码与人类专家编码高度一致 (短文本准确率最高达 95%), 并提出多次 GPT-4 运行分歧交由专家仲裁的 hybrid 方案——锚定本项目 8 模型交叉盲审替代人工筛词的可行性。迁移边界: 美/智/德/意四国政治文本 (非英语仅轻微降级), 非金融中文语境; 该文比较对象是人类专家而非众包工人 (『优于众包工人』是 Gilardi et al. 2023 PNAS 的结论, 勿混引)。
  - 〔Crossref 回读标题: Large language models as a substitute for human experts in annotating political text〕
- Pangakis, N., Wolken, S., & Fasching, N. (2023). Automated Annotation with Generative AI Requires Validation. *arXiv*. https://doi.org/10.48550/arxiv.2306.00176
  - *锚定* — 锚定「LLM 标注可靠性须逐任务验证」: 用 27 个标注任务证明 LLM 标注质量任务间方差大、不可先验假定, 为本项目三阶段流程中把 8 模型交叉盲审(而非单模型直出)作为内建验证环节提供方法论依据。迁移边界: 预印本且基于英文社科语料; 其推荐的『对照人工金标验证』环节本项目以模型间多数投票近似, 属于替代而非等价实现, 须诚实披露。
  - 〔DataCite 回读标题: Automated Annotation with Generative AI Requires Validation〕
- 【2024–2026】Ollion, É., Shen, R., Macanovic, A., & Chatelain, A. (2024). The dangers of using proprietary LLMs for research. *Nature Machine Intelligence*, *6*(1), 4-5. https://doi.org/10.1038/s42256-023-00783-6
  - *锚定* — 锚定「闭源 LLM 标注的可复现性风险」: 指出专有模型版本漂移、不可审计对研究可复现性的威胁, 正当化本项目的缓解设计——8 个异构厂商模型互为稳健性 + T=0 固定 prompt + 缓存冻结复现锚。迁移边界: 这是 2 页评论文章(comment)而非实证研究, 只能作立场/风险披露引用, 不能当作实证效应证据。
  - 〔Crossref 回读标题: The dangers of using proprietary LLMs for research〕
- Törnberg, P. (2023). How to use LLMs for Text Analysis. *arXiv*. https://doi.org/10.48550/arxiv.2307.13106
  - *锚定* — 锚定「LLM 文本分析操作规范」: 给出零样本标注的 prompt 设计、温度设置与验证步骤的实操指引, 对应本项目生成阶段(默认温度探索)与盲审阶段(T=0 + 固定 prompt)的两段式温度策略。迁移边界: 教程型预印本, 面向政治学英文文本示例; 引作流程设计出处而非效度证据。
  - 〔DataCite 回读标题: How to use LLMs for Text Analysis〕
- 【2024–2026】Gu, J., Jiang, X., Shi, Z., Tan, H., Zhai, X., Xu, C., Li, W., Shen, Y., Ma, S., Liu, H., Wang, S., Zhang, K., Wang, Y., Gao, W., Ni, L., & Guo, J. (2024). A Survey on LLM-as-a-Judge. *arXiv*. https://doi.org/10.48550/arxiv.2411.15594
  - *锚定* — 锚定「LLM-as-a-judge 范式总览」: 系统梳理用 LLM 做评审的方法、偏差类型与缓解策略(含多评审聚合), 为本项目 8 模型交叉盲审(每模型充当 judge 输出二元判定+20 字理由)提供范式定位与偏差缓解清单。迁移边界: 综述对象多为『评价生成质量』场景, 本项目是『词条领域归属判定』, judge 任务结构更简单, 偏差谱系需选择性迁移。
  - 〔DataCite 回读标题: A Survey on LLM-as-a-Judge〕
- 【2024–2026】Panickssery, A., Bowman, S. R., & Feng, S. (2024). LLM Evaluators Recognize and Favor Their Own Generations. *arXiv*. https://doi.org/10.48550/arxiv.2404.13076
  - *锚定* — 锚定「self-preference 偏差」: 证明 LLM 评审系统性偏爱自家生成内容, 直接正当化本项目『8 模型交叉盲审』设计——候选词由多模型生成后打乱、由包括生成者在内的全部 8 模型盲评, 用异构多数投票稀释单模型自我偏好。迁移边界: 原文场景是摘要/生成质量对比评审, 本项目是词条二元判定, 自我识别通道(风格指纹)在单词条上弱得多, 偏差幅度不可直接外推。
  - 〔DataCite 回读标题: LLM Evaluators Recognize and Favor Their Own Generations〕
- 【2024–2026】Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2024). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. *arXiv*. https://doi.org/10.48550/arxiv.2406.07791
  - *锚定* — 锚定「position bias」: 系统量化 LLM 评审的位置偏差及其模型间异质性。本项目盲审为单词条独立判定(非成对比较), 位置偏差主要体现为词表呈现顺序效应, 引用时说明二元单项判定天然规避成对位置偏差是设计优点。迁移边界: 原文基于成对比较基准(MTBench/DevBench), 与本项目任务结构不同, 只能作『已知偏差已被设计规避』的支撑。
  - 〔DataCite 回读标题: Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge〕
- 【2024–2026】Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Kong, L., Liu, Q., Liu, T., & Sui, Z. (2024). Large Language Models are not Fair Evaluators. *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 9440-9450. https://doi.org/10.18653/v1/2024.acl-long.511
  - *锚定* — 锚定「LLM 评审不公平性与校准」: 证明评审顺序可操纵评价结论并提出多证据校准(含多次采样+人机协同), 支撑本项目为盲审加 CoT 理由(20 字)与固定 T=0 的『可审计判定』设计。迁移边界: 针对开放生成质量对比场景; 本项目二元领域判定的可操纵面更窄, 引用限于『LLM 评审存在系统性偏差、须结构化缓解』这一层。
  - 〔Crossref 回读标题: Large Language Models are not Fair Evaluators〕
- Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2022). Self-Consistency Improves Chain of Thought Reasoning in Language Models. *arXiv*. https://doi.org/10.48550/arxiv.2203.11171
  - *锚定* — 锚定「多数投票聚合的 method-origin」: self-consistency 证明对多条推理路径做多数表决可显著降低单次采样误差, 是本项目 total_score>=5 简单多数投票截断的方法学始祖。迁移边界: 原文是同一模型多次采样内部聚合, 本项目是 8 个异构模型跨厂商聚合(错误相关性更低, 理论上更优), 属机制外推而非同构复现。
  - 〔DataCite 回读标题: Self-Consistency Improves Chain of Thought Reasoning in Language Models〕
- 【2024–2026】Li, J., Zhang, Q., Yu, Y., Fu, Q., & Ye, D. (2024). More Agents Is All You Need. *arXiv*. https://doi.org/10.48550/arxiv.2402.05120
  - *锚定* — 多模型/多次采样投票的规模化增益 (2024): 实验表明 LLM 集成性能随投票规模 (采样-投票集成数) 提升, 增益幅度与任务难度相关——为本项目 8 模型多数投票的规模选择提供经验参照。迁移边界: 其主实验为同模型多实例采样-投票 (仅分层扩展涉及 GPT-3.5→GPT-4 两级), 非 8 异构厂商面板; 增益无单调保证, 8 之外的边际收益曲线未知。
  - 〔DataCite 回读标题: More Agents Is All You Need〕
- 【2024–2026】Verga, P., Hofstatter, S., Althammer, S., Su, Y., Piktus, A., Arkhangorodsky, A., Xu, M., White, N., & Lewis, P. (2024). Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models. *arXiv*. https://doi.org/10.48550/arxiv.2404.18796
  - *锚定* — 锚定「异构模型陪审团 (PoLL)」: 证明多个异构小模型组成的评审团比单一大模型 judge 偏差更小、成本更低, 是与本项目『8 异构 LLM 交叉盲审多数投票』最同构的先例。迁移边界: 其评审对象是 QA 生成质量且陪审团规模为 3 家, 本项目为词条判定+8 家; 结论方向可迁移, 具体偏差缩减幅度不可照搬。
  - 〔DataCite 回读标题: Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models〕
- 【2024–2026】Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large Language Models: An Applied Econometric Framework. *Annual Review of Economics*. https://doi.org/10.1146/annurev-economics-120925-105620
  - *锚定* — LLM 输出进计量的适格条件框架 (Annual Review of Economics): **预测用途须防训练数据泄漏; 估计/测量用途须配合小规模人工验证金标样本方能做一致的下游推断**。本项目词典构建属估计/测量用途——按该框架, 其适格条件是配备人工验证样本, 而项目现无人工金标 (与本桶 Egami et al. DSL 条目披露的缺口一致), 引用时须明示这是**待补的适格条件**而非已满足; 词频外部效度检验不能替代金标验证。
  - 〔Crossref 回读标题: Large Language Models: An Applied Econometric Framework〕
- Egami, N., Hinck, M., Stewart, B., & Wei, H. (2023). Using Imperfect Surrogates for Downstream Inference: Design-based Supervised Learning for Social Science Applications of Large Language Models. *Advances in Neural Information Processing Systems 36*, 68589-68601. https://doi.org/10.52202/075280-3000
  - *锚定* — 锚定「LLM 代理标签的下游偏误校正 (DSL)」: 证明直接把 LLM 标注当真值进回归会产生系统偏误, 给出 design-based 校正估计量。本项目 LLM 词典命中率进面板回归属同类『代理测量』, 引用以披露测量误差风险并指出 DSL 式校正为可行扩展。迁移边界: DSL 需要一个随机抽样的专家金标子集, 本项目现无人工金标, 该校正是 roadmap 而非已实施。
  - 〔Crossref 回读标题: Using Imperfect Surrogates for Downstream Inference: Design-based Supervised Learning for Social Science Applications of Large Language Models〕
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2023). Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting. *arXiv*. https://doi.org/10.48550/arxiv.2310.11324
  - *锚定* — 锚定「prompt 格式敏感性」: 证明仅改 prompt 格式(空格/分隔符)即可造成任务性能最多数十点波动, 正当化本项目对盲审 prompt 做字节级冻结(与主 pipeline Prompt v8 冻结同一逻辑)并对 8 模型使用统一模板。迁移边界: 测于英文分类基准与开源模型; 中文金融判定任务的敏感度未直接测量, 引用支撑『冻结 prompt 是必要防御』而非量化本项目波动幅度。
  - 〔DataCite 回读标题: Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting〕
- 【2024–2026】Atil, B., Aykent, S., Chittams, A., Fu, L., Passonneau, R. J., Radcliffe, E., Rajagopal, G. R., Sloan, A., Tudrej, T., Ture, F., Wu, Z., Xu, L., & Baldwin, B. (2024). Non-Determinism of "Deterministic" LLM Settings. *arXiv*. https://doi.org/10.48550/arxiv.2408.04667
  - *锚定* — 锚定「T=0 不等于逐位可复现」: 实证 temperature=0/固定种子下商用 LLM 输出仍存在跨调用漂移, 诚实限定本项目『盲审 T=0』的可复现性声明——T=0 降低但不消除随机性, 真正的复现锚是响应缓存冻结而非温度设置。迁移边界: 漂移幅度随厂商/推理栈变化, 本项目 8 家模型各自的非确定率未逐一实测, 引用作风险披露。
  - 〔DataCite 回读标题: Non-Determinism of "Deterministic" LLM Settings〕
- 【2024–2026】Renze, M. (2024). The Effect of Sampling Temperature on Problem Solving in Large Language Models. *Findings of the Association for Computational Linguistics: EMNLP 2024*, 7346-7356. https://doi.org/10.18653/v1/2024.findings-emnlp.432
  - *锚定* — 锚定「温度选择的实证依据」: 系统测量温度 0.0–1.0 对任务表现的影响, 发现问题求解准确率对温度不敏感——支撑本项目两段温度策略(生成阶段默认温度换多样性、判定阶段 T=0 换稳定)不至于牺牲判定质量。迁移边界: 测于英文选择题型基准, 『温度不敏感』结论对开放式词条生成的多样性收益一侧并无直接证据。
  - 〔Crossref 回读标题: The Effect of Sampling Temperature on Problem Solving in Large Language Models〕
- 【2024–2026】Kim, A. G., Muhn, M., & Nikolaev, V. V. (2024). Financial Statement Analysis with Large Language Models. *SSRN*. https://doi.org/10.2139/ssrn.4835311
  - *锚定* — LLM 在专业金融判断上的能力上限证据 (2024 工作论文): GPT-4 仅凭标准化财务报表在盈余变动方向预测上**优于**人类分析师中位数——支撑『LLM 具备金融领域专业判断力』这一本项目盲审机制的前提。迁移边界: SSRN 工作论文未经同行评审; 任务为盈余预测而非词汇判定, 属能力域旁证。
  - 〔Crossref 回读标题: Financial Statement Analysis with Large Language Models〕

### 九补-5. 多评估者一致性统计与机器评审可靠性 (Fleiss' κ=0.5017 · 词项级 P_i 截断 · 多数投票聚合)

> 净增 15 条(其中 2024–2026 者 5 条)。

- Fleiss, J. L., Nee, J. C., & Landis, J. R. (1979). Large sample variance of kappa in the case of different sets of raters. *Psychological Bulletin*, *86*(5), 974-977. https://doi.org/10.1037/0033-2909.86.5.974
  - *锚定* — 直接锚定 LLMs_for_FinTech_dic 对 Fleiss' Kappa (N=2814, n=8, k=2, κ=0.5017) 做 Z 检验拒绝随机共识所用的大样本方差公式的统计原典 (Fleiss 1971 原文已在池, 本条补方差/显著性检验推导)。经典 method-origin 文献; 原语境为多组评估者的临床评级, 迁移到 8 个 LLM 词典评审属固定评估者集合, 严格说 Fleiss 设定假设评估者可随机更换, 需在方法节披露该差异。
  - 〔Crossref 回读标题: Large sample variance of kappa in the case of different sets of raters〕
- Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low Kappa: I. the problems of two paradoxes. *Journal of Clinical Epidemiology*, *43*(6), 543-549. https://doi.org/10.1016/0895-4356(90)90158-l
  - *锚定* — kappa 悖论的 method-origin (规范性引注): 高原始一致率可伴随低 kappa, 解读任何 kappa 须同时报告边际分布与两类悖论。**对本项目的诚实定位**: 实测 P_e=0.5176 仅比二分类理论下限 0.5 高 0.018 (词条收录基率约 59%/41%, 接近均衡), 悖论效应约 1.8 个百分点、可忽略——引用本文是为规范披露口径, **不是**为『解释 κ=0.5017 偏低』; 本项目不处于 kappa 悖论区。
  - 〔Crossref 回读标题: High agreement but low Kappa: I. the problems of two paradoxes〕
- Gwet, K. L. (2008). Computing inter‐rater reliability and its variance in the presence of high agreement. *British Journal of Mathematical and Statistical Psychology*, *61*(1), 29-48. https://doi.org/10.1348/000711006x126600
  - *锚定* — Gwet AC1 作为不同机会校正模型下的敏感性替代系数 (method-origin): 与 Fleiss κ 的机会模型不同, 可作稳健性检查并列报告。迁移边界: AC1 的比较优势场景是高一致+机会基线接近 1 的悖论区, 本项目 P_o=0.7596/P_e=0.5176 两者均不满足, 预期 AC1 与 κ 差异有限; AC1 自身的机会模型假设亦有争议, 只作敏感性臂不作 headline。
  - 〔Crossref 回读标题: Computing inter‐rater reliability and its variance in the presence of high agreement〕
- Dawid, A. P., & Skene, A. M. (1979). Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm. *Applied Statistics*, *28*(1), 20-28. https://doi.org/10.2307/2346806
  - *锚定* — 标注聚合模型原典 (Dawid-Skene EM): 为项目'多数投票 + P_i 词项级一致度截断'提供统计上更精细的替代基准 — 估计每个 LLM 评审者的混淆矩阵而非等权投票。经典临床观察者误差语境, 迁移到 LLM 评审者聚合已是 crowdsourcing/LLM 标注文献的标准做法; 项目未实际实现 DS 模型, 只能作为'等权多数票是 DS 的对称误差特例'的引注, 不可夸大为已做。
  - 〔Crossref 回读标题: Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm〕
- List, C., & Goodin, R. E. (2001). Epistemic Democracy: Generalizing the Condorcet Jury Theorem. *Journal of Political Philosophy*, *9*(3), 277-306. https://doi.org/10.1111/1467-9760.00128
  - *锚定* — Condorcet 陪审团定理的现代多选项推广 (plurality 规则下的认识论性质), 锚定主项目 stage 21 三家 LLM 多数投票 (llm_vote_tone) 与词典项目 8 评审者多数准入的理论依据: 个体正确率>随机时多数票胜过单一评审。政治哲学语境, 迁移需注明定理假设评审者独立同质 — 三家 LLM 共享训练语料相关性会削弱定理保证, 须诚实披露。
  - 〔Crossref 回读标题: Epistemic Democracy: Generalizing the Condorcet Jury Theorem〕
- Passonneau, R. J., & Carpenter, B. (2014). The Benefits of a Model of Annotation. *Transactions of the Association for Computational Linguistics*, *2*, 311-326. https://doi.org/10.1162/tacl_a_00185
  - *锚定* — NLP 标注可靠性方法学关键文献: 论证一致性系数 (kappa/alpha) 高不必然意味标签正确, 主张用 Dawid-Skene 类概率模型替代阈值化一致性。锚定项目用 κ+P_i 截断做词项准入的方法学局限披露 — 承认一致性≠效度, 与人工盲标验证 (llms_human 双文件协议) 互补。语境同为文本标注, 迁移边界小。
  - 〔Crossref 回读标题: The Benefits of a Model of Annotation〕
- Delgado, R., & Tibau, X.-A. (2019). Why Cohen’s Kappa should be avoided as performance measure in classification. *PLOS ONE*, *14*(9), e0222916. https://doi.org/10.1371/journal.pone.0222916
  - *锚定* — kappa 对类别分布敏感的机制性证据: 该文语境是**分类器对 ground truth 的性能评估** (Cohen kappa vs MCC, 类不平衡场景), 与本项目**无金标的评审者间一致性**是不同统计对象 (classifier-vs-gold ≠ rater-vs-rater)——迁移仅借『kappa 数值受类分布影响, 跨数据集/跨设定不可直接比较水平』这一机制, 引用时须明示语境差异。
  - 〔Crossref 回读标题: Why Cohen’s Kappa should be avoided as performance measure in classification〕
- Gwet, K. L. (2021). Large-Sample Variance of Fleiss Generalized Kappa. *Educational and Psychological Measurement*, *81*(4), 781-790. https://doi.org/10.1177/0013164420973080
  - *锚定* — Fleiss κ 方差估计的边界披露引注 (2021): 该文证明 Fleiss-Nee-Landis (1979) 大样本方差**仅在原假设 (κ=0) 条件下有效, 不能用作 κ 的精度度量或构造置信区间**——本项目 Z 检验用 1979 null-conditional 方差检验 H0 是正当的, 但**不得**据此报告 κ 的置信区间; 若需 CI 须改用本文的通用方差估计。与 Fleiss et al. (1979) 原典成对引用, 方向为『限定其适用域』。
  - 〔Crossref 回读标题: Large-Sample Variance of Fleiss Generalized Kappa〕
- van Oest, R., & Girard, J. M. (2021). Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement. *Psychological Methods*. Advance online publication. https://doi.org/10.1037/met0000412
  - *锚定* — 机会校正一致性系数的广义贝叶斯统一框架 (涵盖 kappa/alpha/AC1 等作为特例, 处理不完整数据与权重方案), 锚定项目同时报告 Fleiss kappa、Krippendorff alpha、Cohen kappa 三种系数时'各系数是同一族不同机会模型'的统一叙述。心理测量方法语境, 迁移到 LLM 评审者一致性需注明该框架针对人类评估者的机会评级行为假设。
  - 〔Crossref 回读标题: Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement〕
- 【2024–2026】Almehrizi, R. S. (2026). Coefficient Lambda for Interrater Agreement Among Multiple Raters: Correction for Category Prevalence. *Educational and Psychological Measurement*, *86*(2), 287-319. https://doi.org/10.1177/00131644251380540
  - *锚定* — prevalence-adjusted 一致性系数族谱的最新延续 (纸版 2026, online-first 2025), 显式校正类别患病率不均衡对一致性系数的扭曲——供敏感性脚注引用。迁移边界: 本项目类别分布约 59%/41% 接近均衡, 预期患病率校正幅度很小; 项目未实际计算该 lambda 系数, 引用仅为方法族谱定位, 不可声称已做。
  - 〔Crossref 回读标题: Coefficient Lambda for Interrater Agreement Among Multiple Raters: Correction for Category Prevalence〕
- 【2024–2026】Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. *Science Advances*, *10*(45), Article eadp1528. https://doi.org/10.1126/sciadv.adp1528
  - *锚定* — 12 个 LLM 组成的'硅基群体'中位数聚合达到人类群体预测精度的实证, 锚定项目三家 LLM 投票共识 (llm_vote_tone) 与 8-LLM 词典评审团的'LLM 群体智慧'经验依据。语境为概率预测锦标赛而非文本标注, 聚合对象是连续概率非离散标签, 迁移边界需明示: 仅支持'多模型聚合优于单模型'的一般论断。
  - 〔Crossref 回读标题: Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy〕
- Plank, B. (2022). The 'Problem' of Human Label Variation: On Ground Truth in Data, Modeling and Evaluation. *arXiv*. https://doi.org/10.48550/arxiv.2211.02570
  - *锚定* — 论证标注分歧不全是噪声、部分是合理的标签变异 (perspectivism), 锚定项目对未达 P_i 准入截断词项的处理叙述: 被截断词项可能反映真实语义边界模糊而非评审失败, 支持项目保留一致度连续值而非只报二值准入。NLP 标注语境, 迁移到 LLM 评审者间分歧需注明该文核心讨论对象是人类标注者。
  - 〔DataCite 回读标题: The 'Problem' of Human Label Variation: On Ground Truth in Data, Modeling and Evaluation〕
- 【2024–2026】Calderon, N., Reichart, R., & Dror, R. (2025). The Alternative Annotator Test for LLM-as-a-Judge: How to Statistically Justify Replacing Human Annotators with LLMs. *arXiv*. https://doi.org/10.48550/arxiv.2501.10970
  - *锚定* — 2025 年提出替代标注者检验 (alt-test): 用统计假设检验框架正当化'以 LLM 替代人类标注者'的决策, 正中项目用 Z 检验拒随机共识来正当化 LLM 评审准入的方法论诉求, 也衔接主项目人工盲标 pilot 门 (机器 vs 人类一致性对比)。方法直接面向 LLM 标注者, 迁移边界小; 项目未实现该检验本身, 引作'更严格的正当化程序存在'的披露。
  - 〔DataCite 回读标题: The Alternative Annotator Test for LLM-as-a-Judge: How to Statistically Justify Replacing Human Annotators with LLMs〕
- 【2024–2026】Tan, Z., Li, D., Wang, S., Beigi, A., Jiang, B., Bhattacharjee, A., Karami, M., Li, J., Cheng, L., & Liu, H. (2024). Large Language Models for Data Annotation and Synthesis: A Survey. *arXiv*. https://doi.org/10.48550/arxiv.2402.13446
  - *锚定* — LLM 数据标注/合成的系统综述 (含标注质量评估、多标注聚合、与人类标注对比的度量), 为项目'LLM 评审者 + 一致性统计 + 多数票聚合'整条流水线提供 2024 年领域定位引注。综述性质, 不锚定具体统计量; 引用时限于方法归类, 不作实证支撑。
  - 〔DataCite 回读标题: Large Language Models for Data Annotation and Synthesis: A Survey〕
- 【2024–2026】Pavlovic, M., & Poesio, M. (2024). The Effectiveness of LLMs as Annotators: A Comparative Overview and Empirical Analysis of Direct Representation. *arXiv*. https://doi.org/10.48550/arxiv.2405.01299
  - *锚定* — 对'LLM 作为标注者'的比较综观与实证 (含 LLM 与人类标签分布的一致性度量、对主观任务标签分歧的处理), 锚定项目跨模型 Krippendorff alpha/Cohen kappa 一致性度量在 LLM 标注者上的适用性讨论。语境为主观 NLP 标注任务, 与项目金融文本情感/词典判断的主观性相当, 迁移边界小; 该文提醒 LLM 标签分布偏移问题, 应与项目 verified 门控一并披露。
  - 〔DataCite 回读标题: The Effectiveness of LLMs as Annotators: A Comparative Overview and Empirical Analysis of Direct Representation〕

### 九补-6. 词典法金融科技测度/中国银行金融科技指数/词典效度 (1,506 词 FinTech 词典下游应用)

> 净增 17 条(其中 2024–2026 者 4 条)。

- Wang, R., Liu, J., & Luo, H. (2021). Fintech development and bank risk taking in China. *The European Journal of Finance*, *27*(4-5), 397-418. https://doi.org/10.1080/1351847x.2020.1805782
  - *锚定* — 新闻文本→fintech 计量路线的同源先例 (EJF 2021): 以媒体对 FinTech 相关信息的关注度构建**行业/宏观层面** FinTech 发展指数 (据摘要口径; 具体计数机制以原文方法节为准), 接入中国银行风险回归 (银行侧为被解释面板)。迁移边界: 其 fintech 测度是全行业时序而非 per-bank 词频; 本项目银行级词典强度是更细粒度测度, 二者仅在『新闻文本→fintech 计量』路线上同源。
  - 〔Crossref 回读标题: Fintech development and bank risk taking in China〕
- Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China’s banking industry. *International Review of Economics & Finance*, *74*, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
  - *锚定* — 中国 fintech 发展→银行效率的代表性实证 (IREF 2021): 其 fintech 指数基于金融科技**企业层面数据**构建的行业发展指数 (整体+信贷/支付/投资管理/市场支持四子行业, 2003–2017), 银行效率用 stochastic metafrontier 估计。**引用定位**: 该指数是行业层面企业数据指数而**非文本词频测度**, 与本项目词典词频路线是不同测度族——引作『fintech→银行绩效』文献定位与测度谱系对照, 不作方法先例。
  - 〔Crossref 回读标题: Does fintech innovation improve bank efficiency? Evidence from China’s banking industry〕
- Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. *Economic Modelling*, *127*, 106445. https://doi.org/10.1016/j.econmod.2023.106445
  - *锚定* — 中国银行 fintech 指数的新闻语料词典路线升级版 (Economic Modelling 2023): 基于**新闻语料**的 **155 个关键词** (战略构建/基础设施/业务应用三维度) + 词向量训练 + 因子分析构建银行 fintech 指数, 属 Cheng-Qu (2020) 新闻计数路线的方法学升级——与本项目 (新闻语料+词典词频) 高度同构, 是测度构建段落的直接参照。迁移边界: 155 词 vs 本项目 1,506 词的覆盖度差异须量化讨论; 其因子合成与本项目原始词频强度口径不同。
  - 〔Crossref 回读标题: Bank fintech, liquidity creation, and risk-taking: Evidence from China〕
- 【2024–2026】Liu, S., Wang, B., & Zhang, Q. (2024). Fintech regulation and bank liquidity creation: Evidence from China. *Pacific-Basin Finance Journal*, *84*, 102276. https://doi.org/10.1016/j.pacfin.2024.102276
  - *锚定* — 2024 年 PBFJ 中国银行 fintech 监管冲击实证 (与 Cheng-Qu 2020 同刊): 研究 fintech 监管对银行流动性创造的影响, 其银行 fintech/监管强度测度部分可作本项目测度构建段落的近期参照。迁移边界: 核心变量围绕监管事件而非连续文本词频强度, 是否属文本测度路线未经核实, 不作『同路线』断言。
  - 〔Crossref 回读标题: Fintech regulation and bank liquidity creation: Evidence from China〕
- 【2024–2026】Liu, H., & Hu, J. (2025). Bank Fintech and firm leverage adjustment speed: Evidence from China. *Research in International Business and Finance*, *73*, 102613. https://doi.org/10.1016/j.ribaf.2024.102613
  - *锚定* — ① 2025 年 bank fintech 词频指数外溢到企业侧结果的最新实证, 锚定本项目银行金融科技测度可延伸到银企配对下游 (与主仓 company×bank 共现面板呼应)。迁移边界: 结果变量为企业杠杆调整速度, 与本项目银行侧 DV 不同, 仅引其测度构建与银企传导逻辑。
  - 〔Crossref 回读标题: Bank Fintech and firm leverage adjustment speed: Evidence from China〕
- Allen, F., Gu, X., & Jagtiani, J. (2021). A Survey of Fintech Research and Policy Discussion. *Review of Corporate Finance*, *1*(3-4), 259-339. https://doi.org/10.1561/114.00000007
  - *锚定* — ④ FinTech 研究权威综述 (Allen-Gu-Jagtiani), 锚定词典 1,506 词的领域切分 (支付/信贷/区块链/AI 等子域) 与文献定位段落, 证明词典类目覆盖与学界公认的 fintech 疆界一致。迁移边界: 综述以美欧市场为主, 中国银行系 fintech 语境需另配中国实证。
  - 〔Crossref 回读标题: A Survey of Fintech Research and Policy Discussion〕
- Grimmer, J., & Stewart, B. M. (2013). Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts. *Political Analysis*, *21*(3), 267-297. https://doi.org/10.1093/pan/mps028
  - *锚定* — ② 文本测度效度检验的 method-origin: 'validate, validate, validate' 原则, 直接锚定 1,506 词词典必须做人工标注对照/收敛效度/区分效度三件套的规范依据。迁移边界: 政治文本语境, 金融领域词典需补充领域特异性论证 (与 Loughran-McDonald 路线衔接)。
  - 〔Crossref 回读标题: Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts〕
- van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. *Communication Methods and Measures*, *15*(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
  - *锚定* — ② 词典法 vs 人工标注 vs 机器学习的系统效度比较 (荷兰语新闻), 锚定本项目词典测度须与 LLM/BERT/人工盲标 (llms_human 协议) 做同题多法对照的设计规范, 及'词典法效度通常最弱须报告'的诚实披露义务。迁移边界: 传播学新闻情感语境, 非 fintech 主题词典; 情感词典结论向主题词典迁移时只引方法框架。
  - 〔Crossref 回读标题: The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms〕
- Ying, L., Montgomery, J. M., & Stewart, B. M. (2022). Topics, Concepts, and Measurement: A Crowdsourced Procedure for Validating Topics as Measures. *Political Analysis*, *30*(4), 570-589. https://doi.org/10.1017/pan.2021.33
  - *锚定* — ② 2020 后文本测度构念效度的可操作检验程序 (众包式标签入侵/词入侵检验), 锚定 1,506 词词典可做'词入侵'式人工审核以证明词条-构念对应。迁移边界: 原文针对主题模型输出而非人工词典, 迁移时把 topic-word 检验改造为 dictionary-word 检验须显式说明。
  - 〔Crossref 回读标题: Topics, Concepts, and Measurement: A Crowdsourced Procedure for Validating Topics as Measures〕
- 【2024–2026】Birkenmaier, L., Lechner, C. M., & Wagner, C. (2024). The Search for Solid Ground in Text as Data: A Systematic Review of Validation Practices and Practical Recommendations for Validation. *Communication Methods and Measures*, *18*(3), 249-277. https://doi.org/10.1080/19312458.2023.2285765
  - *锚定* — ② 2024 年 (online-first 2023) 文本测度验证实践的系统综述 (Grimmer-Stewart 后最新验证框架), 锚定本项目词典效度检验章节的清单式设计 (内容效度/收敛效度/基准对照全覆盖)。迁移边界: 通用 text-as-data 综述, 无金融词典专例, 用作规范框架引用。
  - 〔Crossref 回读标题: The Search for Solid Ground in Text as Data: A Systematic Review of Validation Practices and Practical Recommendations for Validation〕
- Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora. *Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing*, 595-605. https://doi.org/10.18653/v1/d16-1057
  - *锚定* — ③ 种子词+词嵌入图传播自动扩展领域词典的 method-origin (SentProp), 锚定本项目'种子词典+word2vec 扩展'对照路线的技术出处与领域特异性论证。迁移边界: 情感极性词典的英文语料方法, 向中文 fintech 主题词典迁移需换嵌入空间并人工复核。
  - 〔Crossref 回读标题: Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora〕
- King, G., Lam, P., & Roberts, M. E. (2017). Computer‐Assisted Keyword and Document Set Discovery from Unstructured Text. *American Journal of Political Science*, *61*(4), 971-988. https://doi.org/10.1111/ajps.12291
  - *锚定* — ③ 计算机辅助关键词发现的 method-origin: 证明纯人工选词不可靠且不同研究者选词几乎不重叠, 锚定本项目 1,506 词采用'算法候选+人工裁决'混合流程的必要性论证。迁移边界: 政治文本检索语境, 引用限于选词方法论而非其具体算法实现。
  - 〔Crossref 回读标题: Computer‐Assisted Keyword and Document Set Discovery from Unstructured Text〕
- Garg, N., Schiebinger, L., Jurafsky, D., & Zou, J. (2018). Word embeddings quantify 100 years of gender and ethnic stereotypes. *Proceedings of the National Academy of Sciences*, *115*(16). https://doi.org/10.1073/pnas.1720347115
  - *锚定* — ③ 词嵌入承载语料系统性偏差的经典证据, 锚定本项目对 word2vec 扩展词典路线的局限性讨论: 嵌入扩展会继承新闻语料的时代与来源偏差, 故 1,506 词最终版需人工审核冻结。迁移边界: 社会刻板印象语境, 仅引'嵌入继承语料偏差'这一机制。
  - 〔Crossref 回读标题: Word embeddings quantify 100 years of gender and ethnic stereotypes〕
- Rodriguez, P. L., & Spirling, A. (2022). Word Embeddings: What Works, What Doesn’t, and How to Tell the Difference for Applied Research. *The Journal of Politics*, *84*(1), 101-115. https://doi.org/10.1086/715162
  - *锚定* — ③ 应用研究中词嵌入选型与验证的 2022 规范 (预训练 vs 自训练、超参敏感性、人工评审基准), 锚定本项目词典扩展阶段嵌入模型选择及'嵌入近邻须过人工闸'的操作标准。迁移边界: 政治学英文语料结论, 中文金融语料的超参结论不直接搬用, 只引验证框架。
  - 〔Crossref 回读标题: Word Embeddings: What Works, What Doesn’t, and How to Tell the Difference for Applied Research〕
- Lu, D., Wu, H., Liang, J., Xu, Y., He, Q., Geng, Y., Han, M., Xin, Y., & Xiao, Y. (2023). BBT-Fin: Comprehensive Construction of Chinese Financial Domain Pre-trained Language Model, Corpus and Benchmark. *arXiv*. https://doi.org/10.48550/arxiv.2302.09432
  - *锚定* — ⑤ 中文金融领域预训练语言模型+语料+基准的系统构建, 锚定本项目中文金融 NLP 资源生态定位: 1,506 词词典与领域 PLM/基准互补, 词典法在可解释性与零训练成本上的比较优势。迁移边界: 预印本未经同行评审; 其对象是 PLM 而非词典, 引用限于中文金融语料资源综观。
  - 〔DataCite 回读标题: BBT-Fin: Comprehensive Construction of Chinese Financial Domain Pre-trained Language Model, Corpus and Benchmark〕
- Guo, X., Xia, H., Liu, Z., Cao, H., Yang, Z., Liu, Z., Wang, S., Niu, J., Wang, C., Wang, Y., Liang, X., Huang, X., Zhu, B., Wei, Z., Chen, Y., Shen, W., & Zhang, L. (2023). FinEval: A Chinese Financial Domain Knowledge Evaluation Benchmark for Large Language Models. *arXiv*. https://doi.org/10.48550/arxiv.2308.09975
  - *锚定* — ⑤ 中文金融领域知识评测基准, 锚定本项目用 LLM 参与词典生成/审核时对模型中文金融领域能力的选型依据 (与主仓 stage 21 三家 LLM 路由的领域胜任度论证同源)。迁移边界: 预印本; 评测对象是 LLM 知识问答而非词典质量, 仅作模型领域能力佐证。
  - 〔DataCite 回读标题: FinEval: A Chinese Financial Domain Knowledge Evaluation Benchmark for Large Language Models〕
- 【2024–2026】Bail, C. A. (2024). Can Generative AI improve social science?. *Proceedings of the National Academy of Sciences*, *121*(21), Article e2314021121. https://doi.org/10.1073/pnas.2314021121
  - *锚定* — ⑥ 2024 年生成式 AI 用于社科测量的机遇与风险总评 (含 LLM 辅助编码/词表生成的偏差、可复现性与验证义务), 锚定本项目 LLM 参与 1,506 词词典构建时的披露与人工终审闸设计。迁移边界: 观点性综述而非实证, 引用限于规范性论证。
  - 〔Crossref 回读标题: Can Generative AI improve social science?〕

---

## 二、LLMs_for_FinTech_dic 自带引文修复台账 (2026-07-10 机械审计 + 双重核验)

审计口径: `FinTech_Dictionary_LLMs_Paper_Final.md`(原 67 条) + `FinTech_Dictionary_Fleiss_Kappa_Methodology.md`(15 条) 全部 doi.org 链接逐条 GET Crossref/DataCite 回读标题比对。72 唯一 DOI: 43 OK / 29 标红。29 条判定与处置:

| 类别 | 条数 | 处置 |
|---|---|---|
| 提取伪影(DOI 独占一行, 实际正确) | 5 | 不动 (Cheng-Qu 2020 / Gilardi 2023 / L&M 2016 survey / Krippendorff 2004 / Landis-Koch 1977) |
| 错 DOI(解析到无关论文/404) | 18 | 17 条找回真 DOI 并经主控独立二次 GET 回读确认后替换; 1 条 (Jiang-Kelly-Xiu) 复核题名不符改判删除, 见下 |
| 论文不存在(多路检索无此标题, 疑似生成幻觉) | 5 | 从参考文献表删除; 其中 Chen & Wang (2022) 在正文有引用, 以已核验真实文献 Cheng & Qu (2020) 替换 |
| Crossref 已删除 DOI (Blei et al. 2003 LDA) | 1 | 去除失效 DOI, 改 JMLR 官方页链接 |

不存在的 5 条(留档防复发): Chen & Wang (2022) "AI in corporate governance" JCF 102263[该 DOI 实为 Right-to-Work laws 论文]; Jiang & Wei (2019) "Word power" JAR[实为 Made in the U.S.A. 论文]; Dzielinski et al. (2023) ARFE[DOI 未注册且多路检索无此文]; Lee & Tang (2022) "ML models in portfolio optimization" MS[实为 Sunk Costs 房价论文]; Flynn & Gandhi (2023) SSRN 4419814[实为驾驶教育量表论文]。另: 原引 "Jiang, Kelly & Xiu (2023) (Re-)Imagining Data Science in Finance" 标题不存在, 作者们的真实论文为 *(Re‑)Imag(in)ing Price Trends* (JF 2023, 10.1111/jofi.13268), 因正文未引用、构念不符, 从参考文献表删除。

**连带修正**(按 Crossref 权威元数据): Cao et al. "Man vs. Machine" 实为 **JFE 2024, 160, 103910**(原引 2021 卷期页均误); "Using GPT to measure business complexity" 实际作者序为 **Bernard, Blankespoor, de Kok, & Toynbee (2026, TAR 101(3), 67-102)**(正文引注同步改 Bernard et al.); Didisheim et al. 合著者实为 **Malamud**(非 Maliar); Zheng et al. MT-Bench 实为 **NeurIPS 2023**(正文 5 处 2024→2023); Hojati-Nault 与 Shan-Qiu 均已见刊 **ISR 37(2), 2026**(正文年份同步); Ye et al. LOLA 以 **SSRN 2024** 版收录(所引 Marketing Science 卷期 DOI 不存在); 悬空正文引注三处均以已核验真实文献落实并补入参考文献表: Liu et al. (2023) = **G-Eval (arXiv:2303.16634)**; Wang et al. (2024, 多路检索不存在) → **García, Hu & Rohrer (2023, JFE 147(3), The colour of finance words)**; Peng et al. (2025, 专名 Semantic-to-Causal 检索零命中, 疑似臆造) → **Kıcıman et al. (2023, arXiv:2305.00050, Causal reasoning and LLMs)**; Landis & Koch (1977) 原正文多处引用但漏列参考文献表, 已补。修复后参考文献表 **66 条**(67 − 6 删 + 5 增), 全表按字母序重排重编号。

**实验数字已实证核定**(据盘上产物 data_processed/bank_keywords_20260302_011050.xlsx 判别 sheet 实读: total_score 分布 {8票:870, 7票:247, 6票:248, 5票:141, ≥5 合计 1,506, N=2,814}, 模型面板 8 家与表1 一致、无 DeepSeek): 结论 "836 枚完全一致词"→**870**; §3.1 智能体 m∈{1…11}→**{1…8}**; 表3 "11满贯"→**8票满贯**; Kappa 文档两处 DeepSeek 表述改为 Doubao/Kimi。另: κ=0.5017 的分级表述全文统一为 Landis-Koch "中度一致 (Moderate)"(0.41–0.60 区间不含 Substantial, 原 "中度至实质"属夸大; McHugh 2012 更严格口径已如实并列注明)。

---

## 三、审计闸与复核记录

- 发现层: 6 桶智能体每候选实时 Crossref/DataCite 自核验后才提名。去重流水账: 发现 114 候选 → 候选间跨桶重复 −8 → 主控回填 106/106 (零解析失败、标题重叠全部 ≥0.6) → 对第八补编重叠 −27 (对既有池 671 DOI 与词典自有 43 条的重叠均为 0) = **净增 79**。
- 修复层: 18 个替换 DOI 主控独立二次核验 17 PASS + 1 改判删除(见 §二)。
- 口径说明: 头部 **839** 为九份锚点文件的锚点条目数; 下行 **874** 为机械闸全部注册文件 (另含 COOC 计划归档 137 DOI 与两份词典 md 引文等非锚点文件) 去重后的唯一 doi.org DOI 数 — 两口径统计对象不同, 皆以 audit_dois.py 实测为准。
- 全语料闸 (2026-07-10 实测): `python scripts/audit/audit_dois.py`(含第八/第九补编 + 两份修复后 md) = **874 唯一 doi.org DOI / 871 OK / 0 新增红旗**; 仅余 3 条既有 benign (CNKI 预期 404 / Devlin NAACL DOI Crossref 未收录 [10.18653/v1/n19-1423, 见主编 2026-06-13] / Bian et al. SSRN 3446388 修订版年差), 均先于本补编存在。
- 对抗评审 (第一轮, 8 智能体): claim-fit / APA / 方向性 / 修复复核 / 悬空引注侦探 — 3 P0 + 7 P1 + 若干 P2/NIT 全部整改 (含 Ludwig 两条件框架方向、Heseltine 张冠李戴、kappa 悖论三条数学口径、图文矛盾等)。
- 终审 (第二轮, 6 智能体 + 主控亲算): 20 条重写锚定逐条与原文对勘 (Ludwig 框架/κ 全链数字/Kleven 五人作者序/18.8%/155 词/12 万+ 等全部确证), 抓出并整改 2 P1 (More Agents 「趋于饱和」为文外之言 / Yang EMNLP 动机句归属失准) + 论文稿 3 处图文矛盾 (图1 P_i>0.5 残迹会数学性剔除全部 141 个 5 票词 / 图2 「降温采样」与正文默认温度矛盾 / Gomber-Cheng&Qu 方法归属) + Kappa 文档 3 P1 (Krippendorff 立场反转 / 「实质性一致」自相矛盾 / P_e 成对概率解释错误) 等共 28 处; Fleiss κ 全链 (p=59.37%/40.63%, P_e=0.5176, P̄=0.7596, κ=0.5017, ≥5 票=1,506) 由主控据盘上票数分布独立复算逐位吻合。
- 第三轮终验 (5 智能体全新通读 + 干净机械闸): 前两轮整改的事实内核全部确证 (P_e 成对 51.76% / 全体一致约 1.6% 亲算复核; Krippendorff α≥0.800/0.667 阈值与原文相符; More Agents 与 Yang EMNLP 改写与 arXiv/ACL 原文吻合); 再清剿 20 处残留 (两处"只改一处未清同伴"型矛盾: 论文 P_i 引导语仍称"决定截断" / Kappa 条目3 首句仍称"绝佳的背书"; 提示词2 "50 个词汇"与代码 JUDGE_BATCH_SIZE=100 不符按代码实证改 100; ⌈n/2⌉+1 取整泛化错误改 ⌊n/2⌋+1; 图2 "反事实辩伪"图示夸大; 摘要/结论补 McHugh 双口径; 参考文献表按语如实披露含延伸阅读书目; CFER 条目数据源按 Crossref 摘要直陈非税调; 等)。
