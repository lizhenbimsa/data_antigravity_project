---
family_id: F489
columns:
- sandbox_ddd_digfront
- sandbox_lag0
- sandbox_lag1
- sandbox_lag2
- sandbox_lag3
- sandbox_lag4plus
- sandbox_lead2
- sandbox_lead3
- sandbox_lead4plus
- sandbox_post
- sandbox_rel_year
- sandbox_treat_year
- sandbox_treated
unit: 处理组哑变量/相对期序数 (0-1 哑变量族 + 整数年份 + 相对期序数; 无量纲)
formula: 'sandbox_treat_year = 银行总部所在城市/省份首次被纳入监管沙盒试点的年份 (按 config/policy_shocks.json::fintech_sandbox 三阶段分组匹配, 未覆盖为 0); sandbox_treated = 1[sandbox_treat_year > 0]; sandbox_post = 1[year >= sandbox_treat_year] (仅处理组银行, 否则 0); sandbox_rel_year = year − sandbox_treat_year (仅处理组, 控制组为 NaN); sandbox_lag{0..3}/lead{2,3} = 1[sandbox_rel_year == k] (k=-1 为基期省略); sandbox_lag4plus = 1[sandbox_rel_year >= 4 且处理组]; sandbox_ddd_digfront = sandbox_treated × sandbox_post × digital_frontier'
producer: pipeline\panel\iv_did.py (核心构造, DiD 处理分配 + event-study lead/lag) ; pipeline\panel\runner.py (DDD 三重差分交互项) ; config\policy_shocks.json (政策冲击原始配置) ; pipeline\panel\export.py (Stata 标签映射) ; pipeline\audit\stata_audit.py (值域/哑变量审计)
upstream:
- bank_city
- bank_province
- year
- digital_frontier
citations:
- doi: 10.1016/j.jeconom.2020.12.001
  type: journal
  authors: Callaway, B., & Sant'Anna, P. H. C.
  year: 2021
  title: Difference-in-differences with multiple time periods
  venue: Journal of Econometrics
  vol: '225'
  issue: '2'
  pages_or_artno: 200-230
- doi: 10.1016/j.jeconom.2020.09.006
  type: journal
  authors: Sun, L., & Abraham, S.
  year: 2021
  title: Estimating dynamic treatment effects in event studies with heterogeneous treatment effects
  venue: Journal of Econometrics
  vol: '225'
  issue: '2'
  pages_or_artno: 175-199
- doi: 10.1257/aeri.20210236
  type: journal
  authors: Roth, J.
  year: 2022
  title: "Pretest with caution: Event-study estimates after testing for parallel trends"
  venue: "American Economic Review: Insights"
  vol: 4
  issue: 3
  pages_or_artno: 305-322
- doi: "10.1080/1540496x.2026.2698629"
  type: "journal"
  authors: "Zheng, Y., Li, R., Ren, S., & He, F."
  year: 2026
  title: "The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience"
  venue: "Emerging Markets Finance and Trade"
  pages_or_artno: "1-17"
- doi: "10.1016/j.jeconom.2025.106059"
  type: "journal"
  authors: "Aguilar-Loyo, J."
  year: 2025
  title: "A comparative analysis of two-way fixed effects estimators in staggered treatment designs"
  venue: "Journal of Econometrics"
  vol: "251"
  pages_or_artno: "106059"
- doi: "10.1080/07350015.2024.2308121"
  type: "journal"
  authors: "Dette, H., & Schumann, M."
  year: 2024
  title: "Testing for Equivalence of Pre-Trends in Difference-in-Differences Estimation"
  venue: "Journal of Business & Economic Statistics"
  vol: "42"
  issue: "4"
  pages_or_artno: "1289-1301"
new_dois: []
---

## CORE

【构念与来源】
本家族 13 列共同承载一个交错双重差分 (staggered DiD) 处理变量族: 中国人民银行 (央行) 主导的"金融科技创新监管试点"(俗称"监管沙盒", regulatory sandbox for fintech innovation) 政策冲击, 在样本银行层面的处理分配、处理后哑变量、以及配套的事件研究 (event study) 动态效应窗口。原始政策信息不来自新闻语料或 LLM/词典/BERT 情感管道, 而来自 config/policy_shocks.json 中人工整理的政策冲击台账 (数据来源标注为央行总行及各省级分行公开文件、gov.cn/people.com.cn/ce.cn/gdjr.gov.cn/mpaypass.com.cn 等), 因此本家族在测度论上属于外生政策冲击构造变量, 而非文本测度; 它与家族内其余"情感/态度/网络"测度族是互补关系 — 后者提供结果变量 (outcome) 或调节变量, 本家族提供处理分配 (treatment assignment) 的外生时间戳与窗口结构, 供交错 DiD/事件研究设计使用。
中国监管沙盒试点分三阶段展开: 第一阶段 (2020 年) 由央行总行直接批复北京、上海、深圳、重庆、雄安 (行政上属保定市, 故保定同时纳入以确保匹配)、杭州、苏州、成都、广州共 9 个核心城市/新区; 第二阶段 (2021 年) 策略提级为"省级统筹", 新增 11 个全新省份 (山东、湖北、甘肃、贵州、新疆、辽宁、山西、广西、安徽、福建、河南) 并将此前的城市试点 (深圳/广州→广东、苏州→江苏、杭州→浙江) 提级为全省覆盖; 第三阶段 (2022 年) 继续向中西部/东北/海南纵深, 新增 8 个全新省份 (陕西、天津、黑龙江、江西、湖南、吉林、云南、海南) 并将四川由成都市试点提级为全省统筹。未被上述任一阶段覆盖的省份 (如河北仅雄安/保定获批、宁夏、内蒙古、西藏、青海) 构成 never-treated 控制组。匹配规则遵循"先入为主": 已由城市级匹配确定处理年份的银行 (如总部在深圳), 不因后续省级扩围 (广东提级) 而被覆盖为更晚的年份, 从而保证每家银行只有唯一的首次处理年份 sandbox_treat_year。
【方法学与计算】
sandbox_treat_year 的赋值发生在 pipeline/panel/iv_did.py 的政策冲击合并子步骤: 先将 bank_city 去除"市"字尾并与 config/policy_shocks.json::fintech_sandbox 各阶段的 cities/full_province 列表逐一匹配 (城市级匹配优先于省级匹配, 且仅在该银行尚未被更早年份匹配到时才写入, 实现"先入为主"), 匹配不到任何阶段的银行 sandbox_treat_year 保持 0。由此派生 sandbox_treated = 1[sandbox_treat_year > 0] (是否曾进入试点, 时不变哑变量) 与 sandbox_post = 1[year >= sandbox_treat_year] (仅对处理组银行随年份翻转, 控制组恒为 0) — 二者的乘积构成经典交错 DiD 的核心回归量 sandbox_treated × sandbox_post。sandbox_rel_year = year − sandbox_treat_year 仅对处理组定义 (控制组记为缺失, 在 Stata 回归中自动被排除), 是事件研究设计的相对期序数, 用于检验处理前趋势平行性 (relative_year < 0 应不显著) 与处理后动态效应演化 (relative_year >= 0 的系数轨迹)。基于 sandbox_rel_year, 逐期虚拟变量 sandbox_lag{0,1,2,3} 与 sandbox_lead{2,3} 分别标记 k=0 (处理当年) 至 k=+3、以及 k=-2、k=-3 (处理前 2、3 期), k=-1 按惯例设为省略基期不生成对应列, 以避免完全共线性; 窗口端点做了合并处理 (endpoint binning): sandbox_lag4plus 合并全部 k>=4 (处理后第 4 期及以上), sandbox_lead4plus 合并全部 k<=-4 (处理前第 4 期及以上), 避免深尾稀疏期单独估计导致方差爆炸。sandbox_ddd_digfront 则在 pipeline/panel/runner.py 的异质性分析子步骤中构造, 是三重差分 (triple-difference, DDD) 交互项 sandbox_treated × sandbox_post × digital_frontier, 用于检验监管沙盒试点的处理效应是否在"数字前沿"银行 (digital_frontier, 另一家族的数字化前沿分组哑变量) 中存在异质性放大或衰减; Wooldridge (2010) §10.4 强调三重差分设计要求全部低阶交互项 (双重交互与主效应) 同时进入回归, Stata 的 `##` 因子变量语法可自动满足此要求。
本家族的处理分配遵循 HQ-based (总部所在地) 匹配假设: 银行的试点归属由其总部注册城市/省份决定, 而非其实际业务网点覆盖或分支机构暴露。这一假设对全国性银行 (国有大行/股份制银行) 尤其敏感 — 其总部所在地 (多为北京/上海等一线城市) 往往是第一阶段试点城市, 导致其 sandbox_treat_year 系统性偏向最早批次, 而其真实业务暴露 (分支网络遍布全国) 与"总部城市试点"这一处理定义之间存在错配。管道日志对此显式披露警告, 并建议以剔除国有行/股份制银行 (或仅对城商行/农商行等地方性银行定义处理组) 作为稳健性检验。此外, 由于早期试跑 T=2 (2017-2018) 开发面板样本年份区间早于监管沙盒试点最早批次 (2020 年), ⚠ 2026-08-01 订正: 在早期试跑 T=2 帧 (2017-2018) 上, 本家族在 sandbox_post/sandbox_lag/sandbox_lead 等派生列结构性恒为 0 (post 恒 0 意味着 DiD/事件研究在当前样本上不可识别), 管道对此发出"DiD 不可识别"告警; 该退化是样本年份覆盖不足导致的预期行为, 在覆盖 2007-2025 (T=19) 的生产语料上, 面板年份将跨越试点冲击年, sandbox_post 及其后续事件研究窗口列将自然恢复非零取值与可识别性。
【文献定位】
本家族的估计范式属于交错采纳双重差分 (staggered adoption DiD), 直接对应 Callaway & Sant'Anna (2021) 提出的多期处理时点框架——该文强调传统双向固定效应估计量在处理时点存在异质性时会产生"负权重"偏误, 应改用 group-time 平均处理效应 (ATT(g,t)) 估计量, 这正是管道日志中建议改用 csdid 命令 (`csdid Y X, ivar(bank_id) time(year) gvar(sandbox_treat_year)`) 的方法学依据; sandbox_lag/lead 逐期虚拟变量族则直接服务 Sun & Abraham (2021) 提出的交互加权事件研究估计量, 用以规避标准两阶段事件研究设计在异质处理效应下的估计偏误。sandbox_ddd_digfront 三重差分设计的方法学依据是 Wooldridge (2010) 关于交互项优于中介回归、避免"坏控制变量"问题的论述, 要求把三个主效应与三个两两交互项全部作为低阶项同时纳入回归, 只放入三重交互项本身而遗漏低阶项会使系数丧失"处理效应的组间差异"这一因果解释。需注意本家族与另一压力期交互列族 (tone_x_stress{track}, 基于 STRESS_YEARS={2015, 2018, 2020} 独立构造的年份哑变量与情感测度的交互项) 在构造上完全独立: tone_x_stress{track} 不依赖 sandbox_treated/sandbox_post/sandbox_treat_year 中的任何一列, 二者仅在概念上同属"事件窗口交互设计"这一大类, 不应误读为本家族的处理时点驱动了压力期情感非对称效应的构造。事件研究前置平行趋势预检验的潜在陷阱另有 Roth (2022, American Economic Review: Insights) 的顶刊支撑: 该文论证在正式估计前先做平行趋势预检验并据此筛选样本或调整设定, 会系统性扭曲后续事件研究估计量的统计推断, 提示本家族在报告 sandbox 试点前后动态效应时应避免依据预检验结果择优呈现设定, 而应完整披露所有 leads/lags 系数。 就本家族所锚定的政策冲击本身, Zheng、Li、Ren 与 He (2026) 以中国金融科技创新监管试点 (即监管沙盒) 为准自然实验, 检验其对银行金融科技发展与风险韧性的影响, 与 sandbox_treat_year 按银行总部所在城市/省份首次纳入试点年份分配处理的逻辑同属一个政策、同落在银行层面, 是本家族设计在前沿实证中的存在性证明; 但该文 DV 为银行金融科技发展指数与风险韧性指标, 本家族哑变量族服务的是媒体语调/关注度类 DV, 且其试点分期与本项目 config/policy_shocks.json 中 fintech_sandbox 的三阶段分组是否逐城逐年一致并未经过核对, 引用时不得声称口径等同。交错采纳设计下的估计量取舍另有近期方法学比较可援引: Aguilar-Loyo (2025) 系统比较了交错处理设计下各类双向固定效应估计量 (重点为 extended TWFE), 推导其与 DiD 估计量的等价分解, 并论证估计量选择取决于目标参数与应用特征、不存在单一最优, 恰可与前述 Callaway & Sant'Anna (2021)、Sun & Abraham (2021) 的路径并读; 惟该文为纯计量方法学 (含理论推导与示例), 不针对任何具体经验场景, 既不背书本家族的处理分配规则, 也未针对本项目 T=19 (2007-2025) 的面板深度作出任何设定。前期系数的检验与解释则可进一步援引 Dette 与 Schumann (2024) 提出的平行趋势等价性检验 (equivalence testing): 该文直接针对事件研究中 lead 系数「未拒绝零」不等于「平行趋势成立」这一推断缺陷给出检验程序, 与本家族以 k=-1 为省略基期、构造 sandbox_lead2/sandbox_lead3 的设定直接相关, 与上文 Roth (2022) 关于预检验扭曲后续推断的警示互为补充; 需说明该文提供的仅是检验程序本身, 不涉及金融科技监管沙盒或银行业数据, 本家族的 lead 系数是否已按该程序实施属本项目自身的实施选择, 原文不构成对既有做法的背书。
## VAR: sandbox_ddd_digfront

【变体差分】
本列是家族内唯一的三重交互项 (triple interaction), 与其余 12 列在测度层级上根本不同: 其余列刻画"是否处理/何时处理/相对处理期多少"的一维处理分配结构, 而本列是 sandbox_treated × sandbox_post × digital_frontier 三者的逐行乘积, 用于三重差分 (DDD) 设计, 检验监管沙盒试点效应是否在"数字前沿"银行子样本中存在异质性放大或衰减 (即"处理效应的处理效应")。构造发生在 pipeline/panel/runner.py 步骤 7g-het (异质性分析交互项预计算子步骤), 而非 iv_did.py 主体的 DiD 派生逻辑; 二者在管道中是先后两次独立的赋值, sandbox_ddd_digfront 的生成严格依赖上游 iv_did.py 已先写入 sandbox_treated/sandbox_post 两列, 前提条件是这两列以及 digital_frontier 三列均已存在于面板 DataFrame 中, 缺任一列该列的 DDD 生成即被跳过 (管道以 `logger.info` 显式记录"DDD 交互项跳过 (DID 变量或 digital_frontier 不存在)", 而非静默产出全零列或缺失列, 便于下游区分"结构性跳过"与"真实全零")。
构造循环同时覆盖 dcep (数字人民币试点) 与 sandbox (监管沙盒) 两个政策前缀, 二者共享同一段构造代码 (`for prefix in ['dcep', 'sandbox']`), 但产出各自独立命名的列 (dcep_ddd_digfront 属另一家族), 互不覆盖、互不借用彼此的处理年份或后验窗口。回归解释上, 依 Wooldridge (2010) §10.4 关于交互项模型的建议, 三重差分设计要求把全部低阶交互项 (sandbox_treated、sandbox_post、digital_frontier 三个主效应, 以及 sandbox_treated×sandbox_post、sandbox_treated×digital_frontier、sandbox_post×digital_frontier 三个两两交互) 同时纳入回归, 只放入本列而遗漏低阶项 (所谓"坏控制"或"遗漏交互"问题) 会使三重差分系数不再具有"处理效应的组间差异"这一因果解释, 系数会与主效应混淆。Stata 中用因子变量语法 `i.sandbox_treated##i.sandbox_post##i.digital_frontier` 可自动补全全部低阶项, 是比手动计算并单独纳入 sandbox_ddd_digfront 更稳妥的写法; 若仅使用预算好的 sandbox_ddd_digfront 单列 (例如在不支持因子变量语法的下游工具中), 使用者须自行手工补齐六个低阶项, 否则估计有偏。因样本早期试跑 T=2 面板年份早于监管沙盒试点最早批次, sandbox_post 恒为 0 导致本列在早期试跑盘上数据中曾亦结构性恒为 0, 在生产 T=19 语料上随 sandbox_post 恢复非零取值而自然启用。

## VAR: sandbox_lag0

【变体差分】
本列是事件研究窗口中 k=0 (处理当年, sandbox_rel_year == 0) 的逐期虚拟变量, 标记银行进入监管沙盒试点覆盖范围的当年观测。构造上 `panel[col_name] = np.where(panel['sandbox_rel_year'] == k, 1, 0).astype(int)`, 对 k=0 逐行判断, 控制组因 sandbox_rel_year 恒为 NaN 而 `== 0` 判断恒假, 自然落在 0 侧, 无需额外的控制组屏蔽逻辑。它与 sandbox_post (处理组自处理年起持续为 1 的"开关式"哑变量) 不同: sandbox_lag0 只在恰好等于处理当年的单一年份取 1, 其余年份 (包括处理组自身的其他年份及全部控制组) 均为 0, 用于在 reghdfe/csdid 等事件研究回归框架中单独估计处理当期效应系数, 而非笼统估计处理后全部期数的平均效应 (ATT)。
基期设定为 k=-1 (省略, 不生成对应列, 即 sandbox_lead1 不存在), 是事件研究设计中防止虚拟变量矩阵完全共线的标准做法 (逐期虚拟变量族若不省略任一期, 加上银行固定效应与年份固定效应会构成完全共线的设计矩阵)。因此 sandbox_lag0 的系数解释为"处理当年相对处理前一年 (基期) 的效应变化", 而非相对整体均值或相对未处理状态的效应。sandbox_lag0 是逐期序列 (lag0/lag1/lag2/lag3/lag4plus) 中效应显现最早的一期, 若处理效应存在实施滞后 (银行需要一定时间调整业务或市场需要时间对沙盒试点信息作出反应), sandbox_lag0 的系数可能不显著而后续期系数逐渐显现, 这是判断处理效应动态演化路径的重要参照点。在与 lead 侧逐期列联合绘制事件研究图时, sandbox_lag0 是横轴 k=0 处曲线的起点。

## VAR: sandbox_lag1

【变体差分】
本列标记 sandbox_rel_year == 1 (处理后第 1 期) 的逐期虚拟变量, 是事件研究动态效应窗口中紧邻处理当年 (sandbox_lag0) 之后的一期。与 sandbox_lag0/lag2/lag3 共同构成处理后 0~3 期的完整逐期序列, 由同一段 `for k in range(-3, 4)` 循环批量生成, 命名规则为非负 k 值映射为 `sandbox_lag{k}`、负 k 值映射为 `sandbox_lead{abs(k)}`, sandbox_lag1 对应 k=1 分支。用于观察处理效应随时间的演化轨迹: 系数序列 (lag0→lag1→lag2→lag3) 若单调递增 (绝对值), 提示处理效应随时间累积增强 (例如银行逐步适应监管沙盒环境、加大金融科技合作/创新投入); 若先增后减, 提示效应存在峰值后衰减; 若各期系数大致持平, 提示处理效应在处理当年即已充分显现且保持稳定。
基期仍为 k=-1 (省略), 故 sandbox_lag1 的系数解释为"处理后第 1 期相对处理前一年 (基期) 的效应变化", 与 sandbox_lag0 的差值 (lag1 系数 − lag0 系数) 反映的是处理当年到次年的边际动态, 在需要检验"处理效应是否随时间显著变化"的联合假设检验 (如 F 检验 lag0=lag1=lag2=lag3) 中, sandbox_lag1 是构成该假设检验的必要分量之一, 单独使用该列而不搭配同族其余逐期列, 无法完整刻画动态效应曲线的形状信息。因该列同样受样本年份覆盖限制, 在早期试跑 T=2 面板上恒为 0, 生产语料上须待处理组银行进入试点满一年后才可能取到非零观测。

## VAR: sandbox_lag2

【变体差分】
本列标记 sandbox_rel_year == 2 (处理后第 2 期) 的逐期虚拟变量, 由 `range(-3, 4)` 循环中 k=2 分支生成, 判定条件为 `panel['sandbox_rel_year'] == 2`。在事件研究图 (event study plot) 中, sandbox_lag0 至 sandbox_lag3 的系数序列通常联合绘制以展示处理效应的动态演化曲线; sandbox_lag2 处于该曲线的中段, 是处理后 4 期窗口 (k=0..3) 中承上启下的一期, 用于判断效应是否具有累积或滞后放大特征 (例如银行需要一定时间调整业务模式、组建金融科技合作团队或调整风险管理框架以响应沙盒试点带来的合规/竞争环境变化, 这类结构性调整往往不会在处理当年立即完成)。
sandbox_lag2 与 sandbox_lag1 之间的系数变化幅度是判断"效应加速期"的关键窗口; 若二者系数接近但均显著小于 sandbox_lag3, 提示处理效应在样本观察窗口内仍处于爬坡阶段而非已达到稳态。由于本列窗口设计固定为 ±3 期加端点合并 (而非更长的逐期展开), 若研究者需要更细粒度地观察第 2 期附近的效应, 只能借助 sandbox_rel_year 原始连续列重新分箱构造, sandbox_lag2 本身不可再细分。与 sandbox_lag0/lag1/lag3 一样, 该列在早期试跑 T=2 面板 (2017-2018) 上因监管沙盒试点最早批次晚于面板末年而结构性恒为 0, 生产语料上随处理组进入第 2 期观测窗口而恢复非零取值。

## VAR: sandbox_lag3

【变体差分】
本列标记 sandbox_rel_year == 3 (处理后第 3 期) 的逐期虚拟变量, 是逐期窗口 (k=0..3) 中的最后一期; 超过该期的观测 (k>=4) 不再单独估计, 而是合并计入 sandbox_lag4plus (端点合并, endpoint binning), 以避免深尾稀疏期样本量过小导致系数方差爆炸、估计不稳定 (交错采纳设计下, 越晚被处理的银行观测到的相对期越靠近 0, 越早被处理的银行才能观测到更大的 k 值, 深尾期样本天然稀疏, 逐期单独估计会使标准误急剧膨胀甚至无法估计)。sandbox_lag3 与 sandbox_lag4plus 的分界 (k=3 vs k>=4) 是管道固定设计选择, 对应 pipeline/panel/iv_did.py 中 `range(-3, 4)` 的窗口范围设定, 覆盖处理前 3 期到处理后 3 期共 7 个逐期取值 (基期 k=-1 省略后实际生成 6 个逐期列) 加上两个端点合并列, 合计 8 个非处理年份哑变量列 (加上 sandbox_treated/post/rel_year 共 11 列构成事件研究核心族, 另有 sandbox_treat_year 与 sandbox_ddd_digfront 补足全家族 13 列)。
在长期效应检验中, sandbox_lag3 的系数是判断"处理效应在观察窗口末端是否仍具统计显著性"的最后一个精确期证据, 若 sandbox_lag3 与 sandbox_lag4plus 系数量级相近, 提示处理效应已进入稳态平台; 若二者差异悬殊, 则提示效应仍在演变, 端点合并可能掩盖了更细致的长期动态, 此时应审慎解释 sandbox_lag4plus 的汇总系数。

## VAR: sandbox_lag4plus

【变体差分】
本列是处理后第 4 期及以上全部观测的端点合并 (endpoint-binned) 虚拟变量: 构造为 `np.where(panel['sandbox_rel_year'].fillna(0) >= 4, (panel['sandbox_treat_year'] > 0).astype(int), 0)`, 即对处理组银行, 当 sandbox_rel_year >= 4 时取 1, 其余 (包括控制组与处理组尚未到达第 4 期的观测) 取 0; 构造上先对 sandbox_rel_year 的缺失值 (控制组恒为 NaN) 填 0 再判断阈值, 单独看 `fillna(0) >= 4` 这一步骤本身不会区分控制组与处理组早期观测, 但取值逻辑的第二层 `(sandbox_treat_year > 0).astype(int)` 显式要求该银行确曾进入试点 (treat_year>0) 才可能被赋 1, 因此控制组银行 (treat_year 恒为 0) 不会被误判为该列取 1, 这一"填 0 判阈值 + 处理组门槛"两步走的写法与 sandbox_lead4plus 完全对称 (仅方向相反)。
与逐期列 sandbox_lag0~lag3 (精确单期示性函数) 不同, 本列刻画的是"处理后期数已进入远期平台"的粗粒度长期效应, 用于在事件研究图右端呈现一个汇总系数而非继续单独估计每一深尾期; 该系数的样本构成会随处理组银行进入试点的年份分布而系统性变化——越早进入试点 (如 2020 年第一阶段城市) 的银行, 越有可能在样本晚期年份贡献 k>=4 的观测, 而越晚进入试点 (如 2022 年第三阶段省份) 的银行几乎不会进入该窗口, 因此 sandbox_lag4plus 的估计样本本质上是"早期批次处理组的远期子样本", 解释时应留意这一构成偏斜, 不宜直接类比为"全体处理组的第 4 期效应"。在生产 T=19 语料上, 该列才具备真正的估计力度; 在早期试跑盘上 T=2 面板中因 sandbox_post 结构性恒为 0, 本列同样恒为 0。

## VAR: sandbox_lead2

【变体差分】
本列标记 sandbox_rel_year == -2 (处理前第 2 期) 的逐期虚拟变量, 由 `range(-3, 4)` 循环中 k=-2 分支生成 (命名规则: 负 k 值映射为 `sandbox_lead{abs(k)}`, 故 k=-2 → sandbox_lead2), 属于事件研究窗口的"前置期"(pre-treatment lead) 一侧, 用于平行趋势检验 (parallel trends test): 若处理前各期系数 (sandbox_lead2/lead3/lead4plus, 及被省略的基期 k=-1) 均不显著异于零, 支持处理组与控制组在处理发生前具有平行的结果变量趋势, 是交错 DiD/事件研究因果识别有效性的关键证据; 反之若 sandbox_lead2 系数显著非零, 提示处理前趋势已在分化, 处理效应的因果解释需要更审慎地排除"预期效应"(anticipation effect, 银行可能在正式获批监管沙盒试点前已从政策信号中调整行为) 或"选择性处理"(政策制定者可能优先选择趋势本就领先/落后的城市/省份试点) 两类混淆解释。
基期为 k=-1 (省略, 不生成对应列), 故 sandbox_lead2 的系数解释为"处理前第 2 期相对处理前一年 (基期) 的差异", 而非相对整体控制组均值的差异; 这一相对基期设计是标准事件研究设计的通用惯例 (与 Callaway & Sant'Anna 2021 提出的 group-time ATT 框架中以处理前一期为参照的做法一致)。sandbox_lead2 与其对称的 sandbox_lag2 (处理后第 2 期) 虽同为"距处理年 2 期"的观测, 但二者分别承担"识别检验"(lead) 与"效应估计"(lag) 两种截然不同的角色, 不应混同解释。

## VAR: sandbox_lead3

【变体差分】
本列标记 sandbox_rel_year == -3 (处理前第 3 期) 的逐期虚拟变量, 由 k=-3 分支生成, 是前置期窗口 (k=-3..-2, 基期 k=-1 省略) 中最早的单独估计期; 早于该期的观测 (k<=-4) 端点合并进 sandbox_lead4plus, 不再逐期展开。与 sandbox_lead2 共同用于平行趋势的逐期可视化检验, 两者系数若呈现明显趋势性 (而非围绕零波动无序分布), 提示处理前趋势不平行, 交错 DiD 的可信度受损, 应转向更稳健的估计量 (如 Callaway & Sant'Anna 2021 的 doubly-robust ATT(g,t) 估计量、或改用 not-yet-treated 而非 never-treated 作比较基准) 或探讨潜在的处理前预期效应 (anticipation effects, 例如监管沙盒试点审批公示与正式落地之间存在时滞, 银行可能在正式纳入前已从公开征求意见等信号中提前调整行为)。
sandbox_lead2 与 sandbox_lead3 联合构成的前置期检验窗口仅覆盖 k=-3 至 k=-2 两期 (加被省略的基期 k=-1), 比处理后窗口 (k=0..3 共 4 期) 短一期, 这是设计上的固定选择而非数据驱动, 与 dcep 前缀家族的对称窗口设计完全一致 (镜像同一段 `range(-3, 4)` 循环代码, 仅前缀不同)。研究者若需要更长的前置期窗口 (例如检验 k=-5、k=-6 是否仍平行), 须基于 sandbox_rel_year 原始连续列重新构造, 当前逐期列族不覆盖该范围。sandbox_lead3 在早期试跑 T=2 面板上同样恒为 0 (监管沙盒试点最早批次晚于面板末年, 结构性不可识别), 生产语料上须待处理组银行进入试点前 3 年即已在面板中出现观测才会取非零值, 面板起点越靠近处理年份 (如某银行仅在 2019 年才进入面板, 而其处理年份为 2020 年), 该列的可观测样本亦相应受限。

## VAR: sandbox_lead4plus

【变体差分】
本列是处理前第 4 期及以上全部观测的端点合并虚拟变量: 构造为 `np.where(panel['sandbox_rel_year'].fillna(0) <= -4, (panel['sandbox_treat_year'] > 0).astype(int), 0)`, 即当 sandbox_rel_year <= -4 且该银行确曾进入试点 (treat_year>0) 时取 1, 否则 (包括控制组以及处理组尚未到达 k<=-4 的观测) 取 0。与 sandbox_lag4plus 对称构造 (同一"先 fillna(0) 再阈值判断, 再叠加 treat_year>0 门槛"逻辑, 仅比较方向相反: lag4plus 判 `>=4`, lead4plus 判 `<=-4`), 用于在事件研究图左端呈现一个汇总的远期前置系数, 避免深远前置期样本稀疏导致的估计不稳定, 同时仍保留对"是否存在长期预期效应"的粗粒度检验能力。
样本构成上, sandbox_lead4plus 的非零观测同样偏向较晚进入试点批次的银行 (需要面板起点更早于其处理年份 4 期以上才能观测到 k<=-4), 与 sandbox_lag4plus 偏向较早批次银行的构成方向相反, 这一不对称性是交错采纳设计下"日历时间固定但处理时点异质"所天然导致的样本结构, 论文披露识别策略时应一并说明。若 sandbox_lead4plus 系数显著异于零而 sandbox_lead2/lead3 不显著, 提示远期 (而非近期) 前置趋势存在差异, 可能反映政策预告/申报周期较长导致的提前反应, 而非近端的处理前扰动。与家族内其余端点合并列一致, sandbox_lead4plus 在早期试跑 T=2 面板上恒为 0, 生产 T=19 语料覆盖更长时间跨度后才具备真实估计力度。

## VAR: sandbox_post

【变体差分】
本列是处理组银行自其处理年份 (含) 起持续为 1 的"开关式"处理后哑变量, 构造为 `np.where(panel['sandbox_treat_year'] > 0, (panel['year'] >= panel['sandbox_treat_year']).astype(int), 0)`: 仅在处理组银行 (sandbox_treat_year > 0) 上按年份翻转, 控制组银行 (从未进入试点, sandbox_treat_year 恒为 0) 恒为 0, 不因 `year >= 0` 恒真而被误判为 1 — 外层的 `panel['sandbox_treat_year'] > 0` 判断先行短路, 保证控制组始终落在 else 分支。它是构成经典 (静态) 交错 DiD 回归量 sandbox_treated × sandbox_post 的两个因子之一, 也是 sandbox_ddd_digfront 三重差分交互项的第二个因子。
与逐期事件研究虚拟变量族 (sandbox_lag0~lag4plus/lead2~lead4plus) 的关系是: sandbox_post 在数学上等价于全部非负相对期虚拟变量之并集 (即 lag0∪lag1∪lag2∪lag3∪lag4plus 的逻辑或, 因 sandbox_rel_year>=0 当且仅当处理组银行已进入处理后阶段), 提供的是处理后平均效应 (ATT, average treatment effect on the treated) 的单一系数估计, 是把处理后各期效应粗暴地压缩为一个常数; 而事件研究族保留了处理后各期效应可能不同的动态曲线信息。两者在回归设计中通常二选一: 静态 DiD 设计 (`reghdfe y sandbox_treated##sandbox_post, absorb(bank_id year)`) 用 sandbox_post, 动态事件研究设计用逐期 lag/lead 列, 不应同时作为独立回归量混入同一设计矩阵 (会产生完全共线, 因逐期列之和恒等于 sandbox_post)。管道对早期试跑 T=2 面板 (2017-2018, 早于监管沙盒试点最早批次 2020 年) 显式披露"sandbox_post 恒为 0, DiD 结构性不可识别"的告警日志, 提醒下游不应在此退化样本上估计 ATT; 该告警逻辑是通用的 (对 dcep_post 亦一体适用), 检测条件为该列在全样本上是否存在至少一个 1 值。

## VAR: sandbox_rel_year

【变体差分】
本列是唯一的连续 (整数值域, 但因含控制组缺失值而以 double/float 类型落盘) 相对处理期变量, 定义为 year − sandbox_treat_year (仅处理组银行定义, 控制组记为 NaN, 在 Stata 回归中自动排除, 与其余列中控制组多以数值 0 表示的约定不同——这一区别是刻意设计: 若控制组也记 0, 会与处理组恰好在处理当年的观测 (rel_year==0) 混淆, NaN 是唯一能保证控制组与处理当年被严格区分的取值)。它是全部逐期事件研究虚拟变量 (sandbox_lag0~lag4plus/lead2~lead4plus) 的生成源头——后者均是对 sandbox_rel_year 取特定整数值 (或阈值区间) 的示性函数, 逐期生成循环 `for k in range(-3, 4)` 逐一比较 `panel['sandbox_rel_year'] == k`, 但 sandbox_rel_year 本身保留了完整的连续相对期信息 (不受 ±3 期窗口截断), 既可直接用于 csdid/did_imputation 等专用交错 DiD 命令的 gvar/相对期参数 (这类命令通常直接消费 group 变量与 time 变量自行计算相对期, 但部分手工实现的估计量或图形命令需要显式的相对期列作输入), 也可在需要更细粒度窗口切分 (超出当前 ±3 期设计, 例如生产 T=19 语料上可能希望观察 k=-6..+6 的更长窗口) 时作为重新分箱的基础列, 不受当前 k=-3..+3 窗口设计的限制。
需特别注意: sandbox_rel_year 的符号约定与直觉一致 (处理前为负、处理后为非负), 但列命名中的 lag/lead 术语在事件研究文献中易与"滞后/领先"的时间序列惯例混淆——本家族的 sandbox_lag{k} 对应 rel_year=+k (处理后, 即处理已发生 k 期), sandbox_lead{k} 对应 rel_year=-k (处理前, 即距处理还有 k 期), 这一命名映射在跨家族比较 (如与网络滞后族 leave1out_lag1 等纯时间序列滞后概念对照) 时应予明确区分, 避免误读符号方向。

## VAR: sandbox_treat_year

【变体差分】
本列是本家族的根节点变量: 银行总部所在城市 (优先) 或省份 (其次) 首次被纳入监管沙盒试点覆盖范围的年份, 取值集合为 {0, 2020, 2021, 2022}, 未被任何阶段覆盖的银行取 0 (而非缺失), 这与 sandbox_rel_year 的"控制组记 NaN"约定不同——sandbox_treat_year 的 0 值同时承担"未处理"标记与"用于比较判断的哨兵值"两重角色 (下游 sandbox_treated = 1[sandbox_treat_year > 0] 依赖此约定, 若误将 0 当作真实处理年份代入 sandbox_rel_year = year − sandbox_treat_year 计算, 会得到荒谬地巨大的正数, 因此下游所有派生列均先判断 treat_year>0 再计算相对期, 严禁绕过该列直接对未处理银行计算相对期)。
三阶段 (2020/2021/2022) 匹配遵循"先入为主"原则: 城市级匹配优先于省级匹配 (代码执行顺序为先遍历各阶段的 cities 列表、再遍历 full_province 列表), 且仅对尚未匹配到更早年份的银行生效 (`mask = (panel_city == alias) & (panel['sandbox_treat_year'] == 0)`), 因此本列在跨阶段扩围 (如广东省 2021 年提级覆盖此前已由深圳市 2020 年匹配的银行, 或四川省 2022 年提级覆盖此前已由成都市 2020 年匹配的银行) 时不会覆盖已确定的更早年份, 保证每家银行的 sandbox_treat_year 恒为其最早可能的处理年份。城市名匹配前先去除"市"字尾并处理雄安—保定的行政区划别名映射 (雄安新区行政上属保定市, 二者同时纳入以确保匹配)。该列的匹配基于总部注册地 (HQ-based), 而非银行实际业务网点分布, 全国性银行 (国有大行/股份制银行) 的总部多集中在北京/上海/深圳等第一阶段 (2020 年) 试点城市, 其处理年份因此系统性偏向最早批次, 而其真实业务暴露 (分支网络遍布全国, 未必集中于总部城市) 与"总部城市试点"这一处理定义之间存在错配; 论文使用时须结合 bank_type (国有/股份制 vs 城商/农商) 披露此识别假设, 并提供剔除全国性银行 (或仅对地方性银行定义处理组) 的稳健性口径。

## VAR: sandbox_treated

【变体差分】
本列是时不变 (time-invariant) 的处理组哑变量, sandbox_treated = 1[sandbox_treat_year > 0], 对同一家银行在全部样本年份取值恒定, 区别于同族其余随年份变化的列 (sandbox_post/rel_year/lag*/lead*)。它单独使用时仅刻画"该银行总部所在地是否曾 (在样本窗口内的任意年份) 被纳入监管沙盒试点", 不含时间信息, 更准确地说是一个"最终是否进入试点"的静态分组标签, 与经典 DiD 教学范式中"实验组 vs 对照组"的分组变量角色完全对应。必须与 sandbox_post 相乘 (sandbox_treated × sandbox_post) 才构成有处理时点含义的标准 DiD 交互项, 也是 sandbox_ddd_digfront 三重差分交互项的第一个因子; 单独的 sandbox_treated 与 sandbox_post 相乘之外, 也常单独用作交错 DiD 样本描述统计的分组变量 (如报告处理组/控制组银行数量、处理组银行的地理省份/城市分布等描述性表格), 或作为倾向得分匹配/协变量平衡检验中的处理指示变量。
若在包含银行固定效应的面板回归模型中单独纳入 sandbox_treated (未与 post 交互), 因其时不变特征 (对同一银行 id 在全部年份恒定) 会被银行固定效应 (bank fixed effects) 完全吸收共线, Stata 会自动将其从设计矩阵中剔除或报告完全共线警告, 不产生可识别的系数, 这是面板固定效应模型的标准性质而非本列的构造缺陷; 因此 sandbox_treated 只在不含银行固定效应的截面/混合回归设计中才可能单独估计出有意义的系数 (刻画"是否处于试点地区"这一时不变特征与结果变量的静态相关性), 在标准的交错 DiD 面板设计中, 它的作用被限定为构造交互项的原料而非独立回归量。

<!-- rendered-citations:begin -->
Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics, 225(2), 200-230. https://doi.org/10.1016/j.jeconom.2020.12.001
Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics, 225(2), 175-199. https://doi.org/10.1016/j.jeconom.2020.09.006
Roth, J. (2022). Pretest with caution: Event-study estimates after testing for parallel trends. American Economic Review: Insights, 4(3), 305-322. https://doi.org/10.1257/aeri.20210236
Zheng, Y., Li, R., Ren, S., & He, F. (2026). The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience. Emerging Markets Finance and Trade, 1-17. https://doi.org/10.1080/1540496x.2026.2698629
Aguilar-Loyo, J. (2025). A comparative analysis of two-way fixed effects estimators in staggered treatment designs. Journal of Econometrics, 251, 106059. https://doi.org/10.1016/j.jeconom.2025.106059
Dette, H., & Schumann, M. (2024). Testing for Equivalence of Pre-Trends in Difference-in-Differences Estimation. Journal of Business & Economic Statistics, 42(4), 1289-1301. https://doi.org/10.1080/07350015.2024.2308121
<!-- rendered-citations:end -->
