---
family_id: F151
columns:
- citation_weighted_patent
- cost_income_ratio_change_3yr
- funding_cost
- ln_fintech_investment
- m_and_a_fintech
- roa
- tobin_q
- z_score
unit: 依列而异 — 财务比率 / 对数金额 / 引用加权计数 / 稳定性指数 (外部财务面板哨兵, 面板不实存)
formula: "无统一闭式 — 本家族为八列论文级结果变量 (outcome/DV) 哨兵占位, 各列语义与量纲依所属论文而异 (见各 VAR 节); 面板尚未实存, 由复现包 01_data_prep 以 capture confirm 自校验拼装, 缺列时优雅降级"
producer: papers\_common\derivative_replication.py (PAPER_DEFAULTS 的 MAIN_DV 槽) ; papers\bank_fintech_attention\tables.py (Table 1 NaN 占位行)
upstream: []
citations:
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: 102306
- doi: 10.1016/j.jfineco.2024.103950
  type: journal
  authors: Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T.
  year: 2025
  title: "Customer data access and fintech entry: Early evidence from open banking"
  venue: Journal of Financial Economics
  vol: 169
  pages_or_artno: 103950
- doi: 10.1016/j.intfin.2024.102002
  type: journal
  authors: Koranteng, B., & You, K.
  year: 2024
  title: "Fintech and financial stability: Evidence from spatial analysis for 25 countries"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 93
  pages_or_artno: 102002
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
- doi: 10.1016/j.respol.2021.104217
  type: journal
  authors: Arora, A., Belenzon, S., & Sheer, L.
  year: 2021
  title: "Matching patents to Compustat firms, 1980-2015: Dynamic reassignment, name changes, and ownership structures"
  venue: Research Policy
  vol: 50
  issue: 5
  pages_or_artno: 104217
- doi: 10.1016/j.jfi.2019.100833
  type: journal
  authors: Thakor, A. V.
  year: 2020
  title: "Fintech and banking: What do we know?"
  venue: Journal of Financial Intermediation
  vol: 41
  pages_or_artno: 100833
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: "Annual report readability, tone ambiguity, and the cost of borrowing"
  venue: Journal of Financial and Quantitative Analysis
  vol: 52
  issue: 2
  pages_or_artno: 811-836
- doi: 10.1093/rfs/hhn053
  type: journal
  authors: Petersen, M. A.
  year: 2009
  title: "Estimating standard errors in finance panel data sets: Comparing approaches"
  venue: Review of Financial Studies
  vol: 22
  issue: 1
  pages_or_artno: 435-480
- doi: "10.3390/fintech5010014"
  title: "Fintech Adoption and Bank Risk, Efficiency and Stability: Evidence from Panel Data of Selected Asian Economies"
  authors: "Uddin, H., & Barai, M. K."
  year: 2026
  venue: "FinTech"
  type: "journal"
- doi: "10.5089/9798400265167.001"
  title: "Does FinTech Increase Bank Risk Taking?"
  authors: "Elekdag, S. A., Emrullahu, D., & Ben Naceur, S."
  year: 2024
  venue: "IMF Working Papers"
  type: "wp"
new_dois:
  - "10.3390/fintech5010014"
  - "10.5089/9798400265167.001"
---

## CORE

【构念与来源】
本家族聚合八个论文级结果变量 (outcome/dependent variable) 的哨兵占位列: citation_weighted_patent、cost_income_ratio_change_3yr、funding_cost、ln_fintech_investment、m_and_a_fintech、roa、tobin_q、z_score。它们的共同身份不是同一测度的变体, 而是本仓十一篇论文各自的主结果变量 (DV) —— 处理变量 (treatment) 与结果变量 (outcome) 在本项目是两套截然分开的对象: 各论文主轨 treatment 多为管道内部构造的 full 轨情感或属性列 (如 P1 的 llm_vote_tone_full、P2 的 attention_index_full、P3 的 sub_frac), 而结果变量另行定义, 绝大多数是外部银行财务面板的哨兵列, 待财务面板接入时才构造。因此本家族 tier 统一标为 pending: 这些列在当前盘上的 bank-year 面板 (T=2 开发切片, 生产 T=19) 中并不实存, 是复现包与论文表格里以名称先行占位、数据后补的空槽。用户已明确财务数据后续会补, 故本家族定位为"结构先行、数值待填"的接口契约, 而非已落盘的测度。

【方法学与计算】
本家族无统一闭式公式, 因为八列量纲各异: citation_weighted_patent 是引用加权的专利计数, ln_fintech_investment 是金科投资额的自然对数, cost_income_ratio_change_3yr 是三年前向的成本收入比变化 (差分), funding_cost 与 roa、tobin_q、z_score 分别是融资成本、资产收益率、托宾 Q、银行稳定性 Z 分数等标准财务比率或指数, m_and_a_fintech 是金科并购的计数或指示。生产侧的唯一挂载点是复现包工厂 papers/_common/derivative_replication.py 里的 PAPER_DEFAULTS 映射: 每篇论文的 MAIN_DV 槽登记其结果变量名 (例如 bank_fintech_attention 的 MAIN_DV = ln_fintech_investment、bank_fintech_substance 的 MAIN_DV = cost_income_ratio_change_3yr、bank_fintech_locus 的 MAIN_DV = citation_weighted_patent), 这些名称经模板替换写入根级与 paper 级 .do 模板。运行期由 01_data_prep 以 Stata 的 capture confirm variable 机制自校验拼装: 列存在则纳入回归, 缺列则优雅降级而不报错崩溃, 这也是它们被称为"哨兵"的原因。bank_fintech_attention/tables.py 的 Table 1 描述统计表则通过 build_summary_table(strict=False) 为这些尚未落盘的结果列保留可见的 NaN 占位行, 使表结构在数据补入前即定型。由此可见本家族的"计算"实为一套装配契约: 名称冻结在先, 财务面板补入在后, 补入后各列即从 pending 升为 core 结果变量。

【文献定位】
八列的构念出处分散在各自论文的对标文献中。金科投资强度作为银行创新的外部结果, 与 Alfhaili、Bakoush 与 Wolfe (2026) 关于银行投资金科股权与创新产出的证据、以及 Thakor (2020) 对金科与银行关系的综述一脉相承; 开放银行下的金科进入与客户数据可得性对银行绩效的冲击见 Babina 等 (2025)。成本收入比变化作为效率试金石, 呼应 Wernerfelt 与 Zajac 传统下"实质性采纳应改善效率、象征性宣告应无效"的解耦逻辑。融资成本作为语气传导的下游结果, 直接对标 Ertugrul、Lei、Qiu 与 Wan (2017) 关于年报可读性、语气模糊度与借贷成本的发现。引用加权专利承 Kogan 谱系并以 Arora、Belenzon 与 Sheer (2021) 的专利—公司匹配方法为构造规范。战略差异化对市场估值 (托宾 Q) 的映射见 Miller 与 Wang (2024) 关于产品数字化与差异化战略变迁的研究。银行稳定性 Z 分数作为系统性风险结果对标 Koranteng 与 You (2024) 的金科与金融稳定证据。凡涉外部财务面板与内部文本测度的合并, 面板标准误须遵循 Petersen (2009) 的双向聚类建议。需强调: 各论文的结果变量各自 just-identified 并排、互为不同构念不分主次, 严禁把不同论文的异质结果变量混进同一 over-identified Hansen J 过度识别检验。

## VAR: citation_weighted_patent

【变体差分】
本列是论文 bank_fintech_locus (P4, Gomber 技术定位轨) 的主结果变量, 区别于家族内其余七列之处在于它是唯一以技术产出 (专利) 而非财务比率或投资额为量纲的结果变量。语义为银行 (或上市行扩展样本) 年度专利产出按前向引用次数加权后的计数, 承 Kogan (2017 QJE) 专利价值谱系, 度量金科技术定位在底层技术轨上的直接产出: 引用加权而非裸计数的用意, 是让高影响力专利获得更大权重, 逼近专利的经济价值而非单纯的申请数量。2026-06-13 的 outcome 重定位记录明确说明了它的历史选择依据: 原设想的事件窗 CAR (累计异常收益) 需要日频股价数据, 而本项目面板是年频 (T=2 开发切片, 生产 T=19), 日频事件研究在年度约束下无法实施, 故 CAR 降级为上市行扩展样本的稳健性检验, 主结果改用引用加权专利这一年频可得、且与底层技术轨直接对应的技术产出测度。构造规范依 Arora、Belenzon 与 Sheer (2021) 的专利—公司动态匹配方法, 妥善处理公司更名、专利重分配与所有权结构变化, 以免匹配噪声污染年度计数。在 derivative_replication.py 中本列登记为 bank_fintech_locus 的 MAIN_DV, 而该论文的回归实际用 primary_pair = (locus_layer_full, locus_scenario_full) 作处理变量, 15_locus_main 模板直接硬编码该 pair, MAIN_TREAT 仅留 locus_layer_full 作单处理占位 fallback 供 16_mechanism 等使用单处理的 paper 级模板消费。本列当前 tier=pending 不实存, 待专利面板接入后升 core。

## VAR: cost_income_ratio_change_3yr

【变体差分】
本列是论文 bank_fintech_substance (P3, Wernerfelt & Zajac 实质—象征解耦轨) 的主结果变量, 区别于家族内水平型财务比率之处在于它是一个三年前向的变化量 (差分) 而非某一年的存量水平。语义为银行成本收入比 (cost-income ratio) 从当期到未来三年的变化, 作为金科采纳的效率试金石: 依 W&Z 实质—象征解耦逻辑, 金科的实质性采纳 (真正嵌入业务流程) 应改善成本收入比 (即降低该比率、提高效率), 而象征性宣告 (只作对外声明而不改变实际运营) 应对效率无实质影响。用三年前向变化而非同期水平, 是为了捕捉采纳到效率兑现之间的滞后, 并缓解反向因果 (当期效率影响当期采纳) 的内生性担忧。2026-06-13 的 outcome 重定位将其升为主结果, 同时把 long_run_roa_change_3yr 降级为 secondary 结果。与之配套的处理变量在同次修订中从原先的文章级列 innovation_substantiveness_full (该列是 stage 21 article-level 产物, 永不在 bank-year 面板出现, 会导致 01_data_prep 因 capture confirm 失败而死于 exit 198) 改为面板真实聚合列 sub_frac (实质性文章占比, 连续测度), 与 spec.treatment.primary 同步修订。控制变量集为 ln_assets、leverage、capital_ratio、npl_ratio、deposit_growth (M5 已去掉 gdp_growth/m2_growth 两个宏观列, 以保 M1→M6 渐进设计里 M5 相对 M4 是真增量而非被 reghdfe 静默 omit 的重复 regressor), 聚类于 bank_id, 异质性维度为 is_soe。本列当前 tier=pending 不实存, 财务面板接入后升 core。

## VAR: funding_cost

【变体差分】
本列是论文 bank_fintech_tone (P1, 情感语气轨) 的主结果变量, 区别于家族内产出型结果 (专利/投资/并购) 之处在于它是一个成本型财务比率, 方向上负面语气抬高该值。语义为银行的融资成本 (funding cost) / 借贷成本, 作为新闻语气这一处理变量的下游财务结果: 更负面的媒体语气经声誉渠道与信息不对称渠道推高投资者与债权人的要求回报, 从而抬高银行的融资成本。这一构念直接对标 Ertugrul、Lei、Qiu 与 Wan (2017) 关于年报可读性、语气模糊度与借贷成本的 JFQA 证据, 后者正是将文本可读性/语气度量映射到融资成本这一财务结果的经典范式。P1 的处理变量主轨已切至 full 轨共识语气列 llm_vote_tone_full (三家 LLM 多数投票的共识 headline), 该列与 llm_peer 方法学篇刻意共享 (记入 SHARED_CONTROLS 白名单, 镜像 z_score 跨篇共享先例)。留篇门控遵循 2026-06-29 的 full-only 口径: 是否判为一篇银行金科报道只看 llm_verified_full == True, ctx/ss 降为 conditional-on-full 的测度/稳健性轨, 行宇宙为 full 留篇集的子集; 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列的源码归属须与家族内衍生篇诸列区分: bank_fintech_tone 是本仓主线论文 (P1), 其复现包由 stata_runner.build_replication_package 这一主线专用入口生成, 刻意不经 derivative_replication.py —— 后者是非主线论文的 replication 生成器, 模块 docstring 与 _DERIVATIVE_PAPER_IDS 白名单 (benefit_society / brokerage_network / strategic_diff / llm_peer / bank_fintech_attention / substance / locus 共七个非主线 id) 明确把主线 bank_fintech_tone 排除在外, 故 funding_cost 不在该模块的 MAIN_DV 槽登记。funding_cost 的权威源是 papers/bank_fintech_tone/paper_spec.yaml 的 outcome.primary 字段, 语义注为利息支出与计息负债年均余额之比 (年度全样本口径)。它成为 P1 主结果是 2026-06-13 outcome 重定位的产物: 项目统一为年频 bank-year 面板后, 原设想的事件窗 CAR (需日频收益) 不再作 primary, 改用储户纪律范式下的资金成本 —— 媒体语气经储户与债权人的风险感知传导到计息负债定价, 年度全样本 (含非上市行) 可用, 优于仅覆盖上市行的 CAR。运行期由复现包的 01_data_prep 以 Stata capture confirm variable 机制自校验拼装, 缺列时优雅降级而不使复现流程崩溃, 这也是其哨兵身份的由来。当前 tier=pending 不实存, 待银行融资成本 (债券利差/存款成本/加权平均资金成本等) 面板接入后升 core。

## VAR: ln_fintech_investment

【变体差分】
本列是论文 bank_fintech_attention (P2, Fang & Peress 覆盖加权曝光轨) 的主结果变量, 区别于家族内比率型结果之处在于它是金额的对数变换 (ln), 对数化用于压缩投资额的右偏分布并让系数读作半弹性。语义为银行金科投资额的自然对数, 度量媒体注意力强度对实际金科投入的 extensive margin (是否投、投多少) 效应。P2 的处理变量 attention_index 是 Fang 与 Peress (2009 JF) 式的 extensive 覆盖加权曝光度量 (对标仅限归一化度量与 ctx 轨 proximity 归因参照 Hassan 等 2019 QJE), 三轨 (full/ctx/ss) 平价并列: attention_index_ss 为银行与金科同句共现轨曝光强度, 配同句 IV lpeer_attention_iv_ss, 与 full/ctx 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨合成 over-identified Hansen J。机制链路为 attention → ln_fintech_mdna_length → ln_fintech_investment (Table 3 中介)。基线为横截面强度 DiD 的 TWFE 实现 (非旧称交错 staggered DiD, csdid 仅在 T≥3 时作稳健性), 控制变量集同 P3 的 bank-level 五列, 异质性维度为 bank_type (四类银行) 叠加金科浪潮。金科投资作为银行创新产出的下游结果, 对标见 Alfhaili 等 (2026) 与 Thakor (2020)。对数化的另一好处是让因变量近似正态、缓解异方差, 使 TWFE 估计的推断更稳健。本列在 tables.py 的 Table 1 以 build_summary_table(strict=False) 的 NaN 占位行保留可见, 使描述统计表结构在数据落盘前即定型; 当前 tier=pending 不实存, 待金科投资额 (自建/合资/股权投资口径) 面板接入后升 core, 届时对 ln_fintech_investment 取对数前须先处理零投资年份的截断问题。

## VAR: m_and_a_fintech

【变体差分】
本列是论文 bank_fintech_collab (P5, Chesbrough 开放式创新轨, provisional) 的主结果变量, 区别于家族内连续型财务结果之处在于它是一个事件计数/指示型结果, 刻画的是离散的整合决策而非连续的比率变化。语义为银行发起的金科并购 (mergers & acquisitions) 事件的计数或指示变量, 度量银行—金科协作在极端整合端 (股权收购/并购) 的实现: 协作光谱从松散的联合声明、合作协议一直延伸到最深度的所有权整合, 并购处于该光谱的极端, 承 Chesbrough 开放式创新框架下"外部技术内部化"的逻辑, 即银行通过收购把外部金科能力纳入自身边界。开放银行与客户数据可得性如何重塑金科进入与在位银行的整合决策, 见 Babina 等 (2025) 的 JFE 证据。P5 目前为 provisional 篇 (analysis/figures/tables 三件套齐备, 但主结果哨兵待外部并购事件面板接入), 处理变量主轨为面板聚合的协作占比 collab_frac (协作类文章占比, 连续测度)。本列在 derivative_replication.py 登记为 bank_fintech_collab 的 MAIN_DV, 当前 tier=pending 不实存, 并购事件面板接入后升 core。作为 provisional 篇的哨兵, 其名称先行冻结以定型该篇复现包的回归模板与描述统计表结构, 使数据补入即可复现。由于并购是稀疏计数结果, 接入后的基线设定可能采用计数模型 (泊松/负二项) 或线性概率的整合指示, 具体口径待并购事件数据到位后依零膨胀程度决定。

## VAR: roa

【变体差分】
本列是三篇论文共享的主结果变量, 区别于家族内单篇专属结果之处在于它被 benefit_society (社会效益轨)、brokerage_network (券商网络轨) 与 llm_peer (方法学篇) 三篇同时征用为主 outcome/DV, 是家族内复用度最高的哨兵。语义为银行资产收益率 (return on assets, 净利润与总资产之比), 是银行盈利能力最标准、跨文献最可比的财务测度。三篇共用同一外部财务哨兵列, 但各自的处理变量与识别设计截然不同: benefit_society 用社会效益维度作处理、brokerage_network 用同业/券商网络暴露作处理、llm_peer 则以 LLM 同侪工具变量 (peer tone IV) 作识别。因此虽共享 roa 这一 DV 名称, 三篇的结果变量在各自模型中各自 just-identified 并排、互为不同识别策略下的独立估计, 属规格并排的稳健性证据而非可合并的矩条件, 严禁跨篇把三套识别混进同一 over-identified Hansen J 过度识别检验。之所以三篇共用一个名字而非各起别名, 是因为 roa 是外部财务面板里的同一物理列, 共享名称保证接入时一次构造、三篇共用。银行盈利能力作为金科冲击下游结果的对标见 Thakor (2020) 综述与 Alfhaili 等 (2026)。本列当前 tier=pending 不实存, 财务面板接入后升 core; 涉及外部财务面板与内部文本测度合并时, 面板标准误遵循 Petersen (2009) 的双向聚类建议。

## VAR: tobin_q

【变体差分】
本列是论文 strategic_diff (战略差异化轨) 的主结果变量, 区别于家族内会计口径结果 (roa/funding_cost/cost_income_ratio) 之处在于它是一个市场口径的估值指标, 直接读入投资者对企业前景的定价而非历史盈利。语义为托宾 Q (Tobin's Q, 企业市场价值与资产重置成本之比), 度量战略差异化程度对银行市场估值的映射: 当银行在战略空间中占据更差异化、更难被模仿的定位时, 市场理应给予更高的估值溢价, 表现为更高的托宾 Q。构念对标 Miller 与 Wang (2024) 关于产品数字化如何驱动差异化战略变迁的 SMJ 研究: 数字化转型改变企业在战略空间中的相对定位, 进而反映到市场估值这一前瞻性结果上。strategic_diff 的处理变量为文本挖掘构造的战略差异化 top-k 指标族 (N ∈ {10,20,30,40,50} × 多方法 × 三轨), 结果变量另定为 tobin_q 这一外部市场估值哨兵, 处理与结果分属内部文本测度与外部市场数据两套。本列在 derivative_replication.py 登记为 strategic_diff 的 MAIN_DV, 当前 tier=pending 不实存 —— 需接入上市行的市场价值与资产重置成本数据后构造, 接入后升 core。作为外部财务哨兵, 其名称先行冻结以定型该篇复现包的回归模板与描述统计表结构, 保证数据补入即可一键复现。

## VAR: z_score

【变体差分】
本列是两篇 provisional 论文共享的主结果变量, 区别于家族内盈利/估值型结果之处在于它是一个风险/稳定性口径的复合指数, 度量的是银行离破产有多远而非赚了多少。语义为标准的银行稳定性 Z-score (通常定义为资产收益率均值加资本资产比之和、除以资产收益率的标准差), 值越高表示破产距离越远、稳定性越强, 是银行风险文献里最常用的破产风险逆向测度, 对标 Koranteng 与 You (2024) 关于金科与金融稳定的空间计量证据。bank_media_disagreement (媒体分歧轨) 与 bank_news_clarity (新闻清晰度轨) 两篇均以 z_score 为主 outcome/DV: 媒体分歧或新闻清晰度经不确定性与信息质量渠道影响银行的破产风险。需特别注意一条铁律: 依 CLAUDE.md, provisional .do 模板里的 z_score (以及 NPL、RWA) 是占位变量名, 刻意保留待外部财务面板接入后填实, 绝不得误删。两篇虽共享 z_score 这一 DV 名称, 但处理变量不同 (媒体分歧度 vs 新闻清晰度), 两套结果各自 just-identified 并排、互为不同构念不分主次, 严禁混进同一 over-identified Hansen J。本列当前 tier=pending 不实存, 稳定性面板接入后升 core; 与 roa 的跨篇共享同理, 共享名称保证外部面板一次构造两篇共用。用9个亚洲国家85家银行2014-2024年面板数据, 以Z-score与稳定性比率度量金科采纳对银行风险、效率与稳定性的影响, 为z_score列的构念提供最新跨国证据 (Uddin & Barai, 2026, FinTech)。用覆盖逾万家金融机构的全球金科活动数据库检验金科渗透与金融机构风险承担的关系, 发现支持竞争—脆弱性假说的稳健证据, 为z_score/roa等银行风险稳定性哨兵列提供识别参照 (Elekdag, Emrullahu, & Ben Naceur, 2024, IMF Working Papers)。

<!-- rendered-citations:begin -->
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T. (2025). Customer data access and fintech entry: Early evidence from open banking. Journal of Financial Economics, 169, 103950. https://doi.org/10.1016/j.jfineco.2024.103950
Koranteng, B., & You, K. (2024). Fintech and financial stability: Evidence from spatial analysis for 25 countries. Journal of International Financial Markets, Institutions and Money, 93, 102002. https://doi.org/10.1016/j.intfin.2024.102002
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Arora, A., Belenzon, S., & Sheer, L. (2021). Matching patents to Compustat firms, 1980-2015: Dynamic reassignment, name changes, and ownership structures. Research Policy, 50(5), 104217. https://doi.org/10.1016/j.respol.2021.104217
Thakor, A. V. (2020). Fintech and banking: What do we know? Journal of Financial Intermediation, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833
Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. Journal of Financial and Quantitative Analysis, 52(2), 811-836. https://doi.org/10.1017/S0022109017000187
Petersen, M. A. (2009). Estimating standard errors in finance panel data sets: Comparing approaches. Review of Financial Studies, 22(1), 435-480. https://doi.org/10.1093/rfs/hhn053
Uddin, H., & Barai, M. K. (2026). Fintech Adoption and Bank Risk, Efficiency and Stability: Evidence from Panel Data of Selected Asian Economies. FinTech. https://doi.org/10.3390/fintech5010014
Elekdag, S. A., Emrullahu, D., & Ben Naceur, S. (2024). Does FinTech Increase Bank Risk Taking? IMF Working Papers [Working Paper]. https://doi.org/10.5089/9798400265167.001
<!-- rendered-citations:end -->
