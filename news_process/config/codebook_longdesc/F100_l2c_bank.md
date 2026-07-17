---
family_id: F100
columns:
- bank_type
- bank_zone
unit: 分类标签 (字符串枚举, 无量纲; bank_type 七值/bank_zone 十一值, 含 'other' 兜底)
formula: "bank_type = NFRA_TO_SHORT[bank_addresses.json[target_bank].nfra_type] ∈ {soe, joint, city, rural, private, foreign, other}; bank_zone = PROVINCE_TO_ZONE[bank_province] ∈ {京津冀, 长三角, 珠三角, 成渝, 东北, 中部, 西北, 西南, 东南, 环渤海, other}"
producer: news_process/pipeline/panel/iv_did.py::load_bank_group_maps + compute_bartik_iv (bank_type, runner 步骤 7e) ; news_process/pipeline/panel/iv_did.py::compute_zone_leave1out (bank_zone, runner 步骤 7f) ; 消费端 news_process/pipeline/panel/iv_extensions.py::compute_peer_loo_iv (group_col 默认 bank_type)
upstream:
- config/bank_addresses.json (nfra_type 官方机构分类 + enterprise_scale)
- config/bank_list.yaml (province → 面板 bank_province)
- 40_panel_yearly.parquet (target_bank / bank_province / year 面板骨架)
citations:
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: "10.1016/j.procs.2023.08.056"
  type: "journal"
  authors: "Yang, X., Liu, Z., Li, J., & Xie, Q."
  year: 2023
  title: "Communities of co-occurrence network of financial firms in news"
  venue: "Procedia Computer Science"
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.1093/qje/qjac038
  type: journal
  authors: Abadie, A., Athey, S., Imbens, G. W., & Wooldridge, J. M.
  year: 2023
  title: "When should you adjust standard errors for clustering?"
  venue: Quarterly Journal of Economics
  vol: 138
  issue: 1
  pages_or_artno: 1-35
- doi: 10.1016/j.jeconom.2022.04.001
  type: journal
  authors: MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D.
  year: 2023
  title: "Cluster-robust inference: A guide to empirical practice"
  venue: Journal of Econometrics
  vol: 232
  issue: 2
  pages_or_artno: 272-299
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.2308/JFR-2021-003
  type: journal
  authors: Breuer, M.
  year: 2022
  title: "Bartik instruments: An applied introduction"
  venue: Journal of Financial Reporting
  vol: 7
  issue: 1
  pages_or_artno: 49-67
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: W.E. Upjohn Institute
- doi: 10.1068/a231025
  type: journal
  authors: Fotheringham, A. S., & Wong, D. W. S.
  year: 1991
  title: "The modifiable areal unit problem in multivariate statistical analysis"
  venue: "Environment and Planning A: Economy and Space"
  vol: 23
  issue: 7
  pages_or_artno: 1025-1044
- doi: 10.1016/0022-5193(66)90013-0
  type: journal
  authors: Pielou, E. C.
  year: 1966
  title: "The measurement of diversity in different types of biological collections"
  venue: Journal of Theoretical Biology
  vol: 13
  pages_or_artno: 131-144
- doi: "10.1016/j.pacfin.2024.102324"
  type: journal
  authors: "Chen, X., He, G., & Li, Q."
  year: 2024
  title: "Can Fintech development improve the financial inclusion of village and township banks? Evidence from China"
  venue: "Pacific-Basin Finance Journal"
- doi: "10.1016/j.econmod.2024.106777"
  type: journal
  authors: "Lu, Y., Li, L., Zhan, H., & Zhan, M."
  year: 2024
  title: "Fintech, information heterogeneity, and the regional distribution effects of corporate financing constraints"
  venue: "Economic Modelling"
- doi: "10.1002/jae.70045"
  title: "Count Data Models With Heterogeneous Peer Effects Under Rational Expectations"
  authors: "Houndetoungan, A."
  year: 2026
  venue: "Journal of Applied Econometrics"
  type: "journal"
- doi: "10.1057/s41599-025-04373-2"
  title: "Commercial banks performance, ownership types and operations efficiency decomposition in China: a comparative analysis"
  authors: "Zhu, C., & Wang, R."
  year: 2025
  venue: "Humanities and Social Sciences Communications"
  type: "journal"
new_dois:
  - "10.1016/j.procs.2023.08.056"
  - "10.1016/j.pacfin.2024.102324"
  - "10.1016/j.econmod.2024.106777"
  - "10.1002/jae.70045"
  - "10.1057/s41599-025-04373-2"
---

## CORE

【构念与来源】
本家族的两列 bank_type 与 bank_zone 不是任何情感、注意力或文本测度本身, 而是整条识别链的分组基础设施, 即回答一个前置于一切工具变量与异质性分析的问题: 对样本中的每一家银行, 它的同业参照组是谁。bank_type 承载的是中国银行业的官方监管分类构念: 国家金融监督管理总局 (及其前身银保监会) 对法人银行机构维护一套权威机构类别口径, 项目将其压缩为六个英文短码, 分别对应国有大型商业银行、股份制商业银行、城市商业银行、农村商业银行、民营银行与外资法人银行, 未落入上述六类的机构统一落入兜底类 other。这一分类不是研究者的主观聚类, 而是监管当局基于产权结构、设立法源、业务范围与审慎监管强度作出的制度性划分, 因而在银行金融科技研究语境下天然携带丰富的经济含义: 国有大行与股份制银行在隐性担保、融资成本、科技投入能力与媒体曝光基线上系统性不同于城商行与农商行, 民营银行与外资行又各自处于牌照稀缺与市场准入的特殊制度位置。bank_zone 承载的则是空间经济学意义上的区域经济圈构念: 将银行总部所在省份映射到十个经济圈标签, 包括京津冀、长三角、珠三角、成渝、东北、中部、西北、西南、东南与环渤海, 未纳入映射表的省份落入 other。经济圈的构念动机是刻画区域共同冲击的作用边界, 即宏观区域层面的信贷周期、地方政府行为、区域产业结构变迁与地方媒体生态, 其传导范围往往跨越省界但又远小于全国, 经济圈恰好是介于省与全国之间的中观分组粒度。两列的数据来源均为项目冻结的配置资产而非任何付费或抓取管道: bank_type 逐行读取 config 下的银行地址主档中的官方分类字段, bank_zone 由面板既有的总部省份列经模块内硬编码的省份到经济圈字典映射得到, 因此两列对全部下游测度而言是严格前定的、与新闻语料实现值完全无关的外生标识符。就制度内涵而言, 六类银行的差异远不止名称: 国有大行由中央财政直接或间接控股, 承担准政策职能且处于系统重要性监管的最高档; 股份制银行为全国展业的混合所有制机构, 市场化程度与科技投入弹性最高; 城市商业银行与农村商业银行受经营地域限制约束, 其金融科技策略高度依赖与外部科技公司的合作而非自研; 民营银行自设立之初即以互联网展业为主要牌照定位, 是金融科技构念上的天然处理强度高组; 外资法人银行则受母行全球战略与跨境合规约束, 行为逻辑独立于境内同业。正因各类型在科技采纳动机、约束与新闻可见度上的系统性分化, 以类型定义同业参照组才具有经济学意义, 而不是任意的统计分块。地址主档本身与银行主名录配置同源维护, 同一条目还携带机构代码、上市状态与总部省份等字段, 本家族仅消费其中的官方分类与省份两条信息, 其余字段服务于相邻家族, 数据血缘由此保持单一事实源。

【方法学与计算】
bank_type 的计算链路是一个两步纯查表过程。第一步在分组映射加载函数中完成: 逐家银行读取地址主档的官方分类字段, 经固定字典压缩为六短码, 查不到或字段为空的银行落入 other; 同一函数同时产出规模映射, 供平行的规模维度分组使用但不属于本家族。第二步在通用 Bartik 引擎的第一步内完成: 以面板的银行名列映射该字典并以 other 填充缺失, 直接把标签写为面板列, 生成时点在 runner 步骤 7e, 即 Bartik 工具变量族构建的最前端。bank_zone 的计算链路在经济圈留一法函数的第一步完成, 生成时点为 runner 步骤 7f: 面板的总部省份列经省份到经济圈字典映射, 映射失败填 other, 结果同时打到面板与文章级展开表两侧, 后者通过目标银行名回连面板标签, 保证文章级聚合与面板级标签同源。两列生成后由三大消费族接手。其一是 Bartik 移测份额工具变量族: bank_type 定义暴露维度, 基期各类型份额经由文章级共同提及银行列计算跨组暴露而得, 即以每家银行基期报道中共同被提及银行落入各类型的相对频次为该行对各类型冲击的暴露权重, 随后被冻结为逐类型份额列并与逐年类型层面冲击相乘汇总成工具变量, 三条文本轨各得一列; 面板年份早于基期末年的行被前视掩码置为缺失, 全程以双精度浮点算术执行以防整型分组降型回绕, 引擎日志逐轨披露工具覆盖率与区分度, 并把地址主档的读取路径、银行家数及落入真实类型组而非兜底组的家数写入溯源日志, 使份额外生性论证的实证根可审计。其二是同组留一均值工具变量族: 通用留一引擎默认以 bank_type 为分组列, 对任一内生面板变量计算同类型同年剔除自身后的组均值, 剔除自身后组内有效同业数低于最小同业阈值 (默认为二) 的格点置缺失, 分组标签为 other 或缺失的银行被伪组拒绝直接置缺失; 引擎默认同时产出滞后一期变体, 以规避同期反射问题, 面板首年自然缺失。经济圈留一法与之同构但分组换为 bank_zone, 组内最小规模阈值默认为三, other 伪经济圈的文章不进入圈层聚合、其银行的圈层留一输出缺失, 该口径与 Bartik 引擎排除 other 的处理镜像一致。其三是异质性与调节分析族: 国有大行哑变量直接由 bank_type 等于 soe 派生; 数字化前沿哑变量按基年内 bank_type 分组的覆盖量中位数一次性切分且组员资格跨年冻结; 多篇论文的验证轨模板将 bank_type 作为分样本与交互项维度进入异质性正文表。需要特别写明口径的一点是: 两列本身为轨道无关的元数据标签, 不带 full、ctx、ss 后缀, 属于双轨铁律中唯一豁免的 track-agnostic 类; 三轨纪律作用于其下游, 即以它们为分组键产出的每一族工具变量都严格逐轨成列, full、ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; ss 轨消费的同句共现打分列缺失时该轨优雅置缺失 (镜像 ctx 轨), 而 ss 文本本身的回退语义遵循全仓口径, 即无银行与金科同句共现时回退全文并以回退指示列标记。留篇门控与 full-only 口径 (二〇二六年六月二十九日起) 在上游文章级已经固化, 本家族两列作为面板级标签不改动也不绕过该门控, 其下游分轨工具变量消费的正是门控后逐轨打分列。

【文献定位】
本家族在方法论文献中的锚点由其两大消费场景决定。份额视角的现代 Bartik 文献是第一支柱, 其谱系可以完整追至源头: Bartik (1991) 在州与地方经济发展政策评估中首创以基期产业构成份额乘以全国性行业增量合成地方劳动力需求冲击的做法, 这一「基期份额乘外生增量」的构造范式正是本项目类型维度移测份额工具的方法源头, 区别仅在于本项目把产业份额换成了基期报道共同提及网络中各银行类型的相对暴露份额。Goldsmith-Pinkham et al. (2020) 系统阐明移测份额工具变量的识别内容等价于以基期暴露份额为工具, 排他性约束的实质是基期份额相对结果残差的外生性, 并给出份额层面的诊断议程, 包括 Rotemberg 权重分解各份额对工具变量估计量的贡献、检查负权重与权重集中度。与之互补的第二条识别路径由 Borusyak et al. (2022) 正式化: 当冲击 (shift) 层面可以论证为准随机分派时, 即便份额内生, 移测份额工具仍可经等价的冲击层面回归获得识别; Borusyak et al. (2025) 进一步给出实操核对清单, 帮助研究者判定自己的设计属于「少份额且份额外生」还是「多冲击且冲击外生」路径并匹配对应诊断。本项目的类型 Bartik 属于前一路径, 类型数少而份额在基期冻结, 因而论文披露以份额外生论证与 Rotemberg 权重表为主轴, 这也是 bank_type 生成于 Bartik 引擎最前端的设计原因。推断层面, Adão et al. (2019) 证明当不同单元的暴露份额相关时, 常规按单元聚类的标准误会严重低估移测份额设计的抽样不确定性, 并给出暴露稳健推断程序, 该警告对本家族尤其切身, 因为同类型银行的份额向量天然高度相似。面向财务与银行实证读者的落地参照是 Breuer (2022), 其以会计与金融面板为语境演示了在单元乘时间固定效应设计中构造差异暴露 Bartik 工具的完整流程, 为本项目把该方法移植到银行年度面板提供领域内先例。项目对该框架的落实直接体现在 bank_type 的用法上: 类型份额在基期一次性冻结、绝不逐年更新, 面板年份早于基期的格点被前视掩码清空, 数字化前沿等派生分组同样执行基年一次切分且跨年冻结的前定公理, 相关修复在源码中显式引注该文并留有修复台账。同群效应识别文献是第二支柱: Manski (1993) 提出的反射问题指出, 当个体结果依赖于组内均值结果时, 同期组均值回归无法分离内生社会效应、外生情境效应与相关效应。留一均值工具变量族的两个设计细节直接回应这一批评: 其一, 留一构造从组均值中剔除银行自身贡献, 切断机械自相关; 其二, 引擎默认加产滞后一期变体, 以时间错位规避同期反射, 源码文档字符串明示这一动机。Bramoullé et al. (2009) 把这一识别问题从完全组结构推广到一般网络结构, 证明只要参照组之间存在部分重叠而非完全重合, 朋友的朋友的特征即可充当排他工具, 线性均值模型便可点识别; 该结果反过来照亮了本家族分组设计的一个结构性事实, 即 bank_type 与 bank_zone 定义的是互斥划分而非重叠网络, 组内完全参照恰是 Manski 批评最尖锐的情形, 因此本项目不依赖组结构本身供给排他变异, 而是靠留一剔除、时间滞后与跨组暴露份额三重机制外挂识别力, 这一定位在论文识别小节须如实陈述。以类型分组为视角的近期实证亦印证该分类的经济含义: Chen, He, & Li (2024, Pacific-Basin Finance Journal) 以村镇银行为代表的银行类型分组视角检验金融科技对普惠金融的异质性影响, 印证 bank_type 官方机构分类维度在中国银行业金融科技研究中携带的经济含义; 而 Lu, Li, Zhan, & Zhan (2024, Economic Modelling) 利用中国银企关系数据揭示金融科技对企业融资约束的区域分布效应因地区标准化信息可得性而异, 支持 bank_zone 以跨省经济圈刻画区域共同冲击边界的构念动机。Houndetoungan (2026, Journal of Applied Econometrics) 提出理性预期下考虑组内异质同群效应的计数数据模型估计方法, 为本家族留一均值同群效应工具变量族提供更细粒度的异质性同群效应识别参照。Zhu & Wang (2025, Humanities and Social Sciences Communications) 以两阶段网络DEA分解中国商业银行按所有制类型 (内资/外资等) 划分的经营效率差异, 印证 bank_type 官方机构分类维度在银行绩效异质性研究中的经济含义。第三支柱是分组结构本身的测量学: 一个分类体系对识别的贡献不仅取决于类别定义是否外生, 还取决于单元在类别间分布的均匀程度, Pielou (1966) 对按类型归类的集合提出的多样性与均匀度测量, 为刻画本家族分组的组规模不均问题提供了经典参照, 即国有大行组组员极少而城商行组组员众多这类高度不均的类别分布, 会使不同类型的留一工具在有效同业数与一阶段强度上系统性不对称, 这正是最小同业阈值与组规模阈值这两道守卫存在的原因。

【识别策略定位】
在整个项目的识别版图中, 本家族处于工具变量与调节维度的坐标原点位置。第一, 它定义了排他性约束的讨论单位: 类型层面或圈层层面的共同冲击影响个体银行结果的通道, 被假定完全经由同组其他银行的可观测新闻测度, 而基期类型份额与总部省份的经济圈归属均在样本期前或样本期外决定, 与逐年新闻实现值无关, 这是两族工具第一阶段相关性与排他性论证的共同前提。第二, 它组织了粒度阶梯: 同一留一引擎的分组列可替换为 bank_type、bank_zone 或省份列, 形成类型、经济圈、省份三层粒度的平行工具族, 省级组粒度细但组内银行数易不足, 经济圈跨省聚合样本更充足且捕捉区域共同冲击, 类型组则捕捉制度同质性冲击; 三层分组产出的工具各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 这与三轨、co-primary 双轨嵌入、词典消融与政治词权重梯子共用同一条全仓铁律。第三, 它约束了时间结构: 滞后一期变体与基期冻结份额共同保证工具的信息集先于结果实现, 面板首年与基期前行的缺失是设计性缺失而非数据质量问题。第四, 它是异质性推断的分层键: 类型维度的分样本回归与交互项检验回答的是效应在制度位置不同的银行间是否同质, 这一用途使 bank_type 成为多个验证轨模板正文表的调节主变量, 也是其被列为 core 列的直接依据。第五, 模板层面的落地形态是守卫式多类别分样本: 验证轨模板对 bank_type 逐类别枚举取值、每类别以最小行数守卫过阈才跑该类别的分样本回归 (吸收银行与年份双固定效应、按银行聚类), 列缺失或类别过小时显式跳过并留日志, 保证异质性表在开发窗口与生产窗口都不因某一类别退化而整表崩溃; 这一守卫设计本身就是对前述组规模不均局限的工程化回应。第六, 在识别路径谱系上须明确站位: 按 Borusyak et al. (2025) 的核对清单, 本项目的类型 Bartik 属于份额外生路径而非冲击外生路径, 因为类型层面冲击由样本内新闻测度逐年聚合而来、并不天然满足准随机分派, 识别重量全部压在基期份额的前定性上; 相应地, 论文披露侧重 Rotemberg 权重与基期前安慰剂, 而非冲击层面等价回归。若审稿人质疑某一类型份额的排他性, 备用路径是 Apfel (2024) 提出的放松排他约束方案, 即允许一部分份额违反排他性而以其余份额识别, 该方案在类型数有限的本设计中对应「逐一剔除单个类型份额重估」的敏感性检验, 已列入稳健性菜单而非主规格。第七, 本家族与工具变量族之间存在严格的单向依赖: 标签列先于一切工具生成、且生成过程不读取任何情感或注意力测度, 这一时序与信息集隔离是全部下游排他性论证的公共前提, 任何把标签生成挪到测度之后或让映射表依赖语料实现值的改动都属识别层面的破坏性变更, 须整族重审。

【与相邻测度的构念区分】
bank_type 须与若干形近邻居严格区分。与 bank_scale 的区别是维度正交: 后者来自地址主档的企业规模字段, 取大中小微四档短码加 other, 定义的是规模维度的平行 Bartik 分组, 是类型维度的稳健性臂而非替代; 两者对同一家银行可以给出完全独立的信息, 例如同为城商行可以横跨大中小档。与国有大行哑变量的区别是派生关系: 该哑变量仅由 bank_type 是否等于 soe 塌缩而来, 丢弃了其余五类间的全部区分度, 只服务于单一交互项场景。与隐性担保层级的区别是构念不同源: 后者是项目按太大不能倒逻辑对类型与政策地位的再编码, 属研究者构造的序数变量, 而 bank_type 保持监管原始类别的名义尺度不作排序。bank_zone 须与 bank_province 区分: 省份是行政区划粒度, 经济圈是跨省经济功能粒度, 两者构成留一工具的两层平行分组而非同义替换; 也须与文章侧的地理测度族区分, 后者刻画报道内容的地理指向, 而 bank_zone 只刻画银行总部的静态区位归属。最后是 other 兜底语义的家族内不对称: 在 bank_type 侧, other 表示官方分类缺失或不属六类, 留一引擎与 Bartik 份额均将其作伪组拒绝; 在 bank_zone 侧, other 表示总部省份未纳入十圈映射, 圈层聚合将其文章整体剔除且其留一输出缺失。两列的 other 都绝不构成可用的同业参照组, 任何把 other 当真实类别读入回归的用法都是误用。

【已知局限与稳健性梯子】
第一, 分类为静态快照: 两列均由冻结配置一次性映射, 不随年份变动, 无法反映样本期内的机构改制, 例如农信社改制为农商行或城商行跨区域合并重组, 类型标签按主档登记口径固定; 这在识别上反而是优点 (前定性), 但在描述统计上须避免把标签解释为逐年状态。第二, 组规模高度不均: 官方分类下各类型的机构数量差异悬殊, 少数类别组员极少, 留一后有效同业数可能低于阈值而整组置缺失, 均匀度意义上的类别分布偏斜 (Pielou 1966 意义下的低均匀度) 使各类型工具的强度天然不对称, 论文须逐工具报告一阶段有效样本量与弱工具统计量。第三, 经济圈划分含研究者选择: 十圈映射对边界省份的归属 (例如安徽入长三角、山东归环渤海、福建与海南合为东南) 是可辩护但非唯一的划法, 属于可修改区域单元问题的一个实例 — Fotheringham & Wong (1991) 系统证明多变量统计推断对空间聚合单元的尺度选择与分区方案双重敏感, 系数大小甚至符号都可能随聚合方式改变, 因此对圈层工具的稳健性检验应换用省级留一与类型留一互证, 即在尺度维度上同时报告省与圈两级、在分区维度上以类型这一非空间划分作外部参照, 三者并排而非择优合并。第四, 兜底类淹没信息: other 银行在两族工具中系统性缺失, 若其在样本中占比不可忽略, 相关工具变量回归的有效样本相对主回归收缩, 须在附表披露收缩幅度。第五, 短面板退化: 开发窗口的短面板下滞后一期变体仅后段年份有值、基期份额易呈退化分布, 均属预期的设计性现象, 全量语料长面板下自然恢复, 不构成对生成逻辑的反例。第六, 分组键与被聚合测度之间存在潜在的组内相关聚类问题: 以类型或经济圈为组构造的工具在推断时应至少按银行聚类标准误。这里的聚类层级选择须按 Abadie et al. (2023) 的设计视角论证而非机械套用惯例: 聚类调整的正当性来自抽样设计或处理分派在某一层级上的成组性, 本家族的工具变量恰恰在类型与经济圈层级上人为制造了组内共同成分, 属于「分派在组层级相关」的典型情形, 因此按分组键聚类不是过度保守而是设计使然; 但类型仅七组、经济圈仅十一组, 远低于常规聚类渐近所需组数, 按 MacKinnon et al. (2023) 的实证操作指引, 少组数场景应放弃常规聚类稳健标准误, 改用野聚类自助或聚类刀切法并报告对聚类层级选择的敏感性; 对移测份额工具还须叠加 Adão et al. (2019) 的暴露稳健推断, 因为份额相关引致的横截面依赖并不沿行政或制度分组边界排列, 常规聚类无法吸收。实务折衷是主表按银行聚类、附表报告双向聚类与野聚类自助置信区间, 三套推断口径并排披露。稳健性梯子的总纪律与全仓一致: 类型、经济圈、省份三层分组工具, 连同其下游的三轨版本与滞后变体, 一律各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 梯子之间正交不交叉, 不做分组粒度与文本轨道的笛卡尔积展开。

## VAR: bank_type

【变体差分】
本列是家族的 canonical 分组键与唯一 core 列, 字符串枚举取值为 soe、joint、city、rural、private、foreign 六短码加 other 兜底, 分别对应国有大型商业银行、股份制商业银行、城市商业银行、农村商业银行、民营银行与外资法人银行的官方监管分类。区别于家族内另一列 bank_zone 的精确语义有四点。第一, 信息源不同: 本列读取的是银行地址主档中的官方机构分类字段, 是监管当局的制度性划分, 不含任何地理信息; bank_zone 则纯由总部省份派生, 不含任何制度类型信息, 两列对同一家银行给出两个正交维度的组归属。第二, 生成位点不同: 本列在 runner 步骤 7e 由通用 Bartik 引擎第一步写入面板, 先于经济圈标签一步生成, 并且是全仓分组映射加载函数的第一返回值, 与规模映射同批加载但独立成列。第三, 下游消费面更宽: 本列同时服务三大消费族, 即类型维度 Bartik 份额与工具变量三轨族 (基期份额冻结、前视掩码、逐轨成列)、同组留一均值工具变量族的默认分组列 (最小同业阈值为二, 滞后一期变体规避 Manski 1993 的同期反射, other 与缺失伪组拒绝)、以及异质性族 (国有大行哑变量由本列等于 soe 直接派生, 数字化前沿哑变量按本列分组做基年中位数一次性切分且组员资格跨年冻结, 遵循 Goldsmith-Pinkham et al. 2020 的前定公理); 而 bank_zone 的主消费面仅为经济圈留一族与留一引擎的可选分组替换臂。第四, 推断角色不同: 本列是多个验证轨回归模板异质性正文表的调节主变量, 承担分样本与交互项推断的正文角色, 这是其 tier 定为 core 的直接依据; bank_zone 在论文正文中主要以工具变量构造中介的身份出现, 不直接作调节主变量。模板层面的具体消费方式是守卫式多类别分样本: 验证轨模板对本列逐类别枚举实际出现的取值, 每类别以最小行数守卫过阈才跑分样本回归, 吸收银行与年份双固定效应并按银行聚类, 类别过小或列缺失时显式跳过并留日志, 因此正文异质性表报告的类别集合是数据驱动的, 开发窗口与生产窗口可不同, 读表时应以表注列出的类别为准而非假定六类齐全。导出层面本列在数据字典与变量标签中显式标注其官方分类来源, 盘上以字符串枚举存储而非整数编码, 与主名录中的整数类型编号字段是两套并存口径, 后者服务实体匹配与守卫, 本列服务回归分组, 两者不可互相顶替。使用注意: 本列为轨道无关元数据, 无 full、ctx、ss 后缀, 属双轨铁律的 track-agnostic 豁免类; 由本列派生的每一族工具在三轨与分组粒度两个方向都必须各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; other 取值是伪组拒绝哨兵而非真实类别, 进入固定效应或交互项前应显式处理; 标签为静态快照, 不随年份变动, 分析中作前定变量使用, 报告异质性结果时应同时披露各类别的银行家数与观测数, 避免读者把小类别的不显著误读为效应缺席。推断口径上, 以本列为分组键的工具变量回归属于组层级共同成分被人为注入的场景, 按 Abadie et al. (2023) 的设计视角应考虑按本列聚类的敏感性, 但七个取值远低于聚类渐近所需组数, 须配合野聚类自助类小组数修正 (MacKinnon et al. 2023); 由本列基期份额构造的 Bartik 工具另须按 Adão et al. (2019) 报告暴露稳健标准误。识别谱系上本列是份额外生路径 (Goldsmith-Pinkham et al. 2020) 的份额载体, 与 Borusyak et al. (2022) 的冲击外生路径相区别; 逐一剔除单类型份额重估的敏感性检验对应 Apfel (2024) 的放松排他约束思路。这些推断与识别义务全部由本列的分组角色派生, bank_zone 侧仅镜像其中的少组数与暴露相关两条。

## VAR: bank_zone

【变体差分】
本列是家族的区域维度伴生标签, 字符串枚举取值为京津冀、长三角、珠三角、成渝、东北、中部、西北、西南、东南、环渤海十个经济圈加 other 兜底, 由面板的总部省份列经模块内硬编码的省份到经济圈字典一次性映射生成, 生成位点为 runner 步骤 7f 的经济圈留一函数第一步, 晚于 bank_type 一步。区别于 canonical 列 bank_type 的精确语义: 分组依据是空间经济功能区而非监管制度类别, 捕捉的是跨省而小于全国的区域共同冲击边界; 粒度介于省级与全国之间, 与省级留一构成粗细互补的两层平行分组, 省级粒度细但组内银行数易不足, 圈层聚合样本更充足。本列的直接下游是经济圈留一情感均值三轨列 (full、ctx、ss 逐轨成列, ss 消费同句共现打分列、缺列时该轨优雅置缺失、镜像 ctx), 并可作为通用留一引擎的替换分组列构成分组粒度梯子的一级。口径守卫: other 伪经济圈不构成真实区域共同冲击组, 其文章不进入圈层聚合、其银行的圈层留一输出缺失, 与 Bartik 引擎排除 other 的口径镜像一致; 圈层组内最小规模阈值默认为三, 高于类型留一的默认阈值二。十圈划分对边界省份的归属属研究者选择, 是可修改区域单元问题在尺度与分区两个维度上的实例 (Fotheringham & Wong 1991), 稳健性上与类型留一、省级留一并排互证: 省级换尺度、类型换分区逻辑, 三层分组各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。十一个取值的少组数问题与 bank_type 侧同理, 按圈层聚类的推断须配合小组数修正 (MacKinnon et al. 2023)。本列同为轨道无关元数据, 无三轨后缀, 静态快照不随年变, 不反映样本期内银行总部迁址这一罕见事件, 按主档登记口径固定。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Yang, X., Liu, Z., Li, J., & Xie, Q. (2023). Communities of co-occurrence network of financial firms in news. Procedia Computer Science. https://doi.org/10.1016/j.procs.2023.08.056
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Abadie, A., Athey, S., Imbens, G. W., & Wooldridge, J. M. (2023). When should you adjust standard errors for clustering? Quarterly Journal of Economics, 138(1), 1-35. https://doi.org/10.1093/qje/qjac038
MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. (2023). Cluster-robust inference: A guide to empirical practice. Journal of Econometrics, 232(2), 272-299. https://doi.org/10.1016/j.jeconom.2022.04.001
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Breuer, M. (2022). Bartik instruments: An applied introduction. Journal of Financial Reporting, 7(1), 49-67. https://doi.org/10.2308/JFR-2021-003
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bartik, T. J. (1991). Who benefits from state and local economic development policies? W.E. Upjohn Institute. https://doi.org/10.17848/9780585223940
Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit problem in multivariate statistical analysis. Environment and Planning A: Economy and Space, 23(7), 1025-1044. https://doi.org/10.1068/a231025
Pielou, E. C. (1966). The measurement of diversity in different types of biological collections. Journal of Theoretical Biology, 13, 131-144. https://doi.org/10.1016/0022-5193(66)90013-0
Chen, X., He, G., & Li, Q. (2024). Can Fintech development improve the financial inclusion of village and township banks? Evidence from China. Pacific-Basin Finance Journal. https://doi.org/10.1016/j.pacfin.2024.102324
Lu, Y., Li, L., Zhan, H., & Zhan, M. (2024). Fintech, information heterogeneity, and the regional distribution effects of corporate financing constraints. Economic Modelling. https://doi.org/10.1016/j.econmod.2024.106777
Houndetoungan, A. (2026). Count Data Models With Heterogeneous Peer Effects Under Rational Expectations. Journal of Applied Econometrics. https://doi.org/10.1002/jae.70045
Zhu, C., & Wang, R. (2025). Commercial banks performance, ownership types and operations efficiency decomposition in China: a comparative analysis. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-025-04373-2
<!-- rendered-citations:end -->
