---
family_id: F166
columns:
- dcep_ddd_digfront
- dcep_lag0
- dcep_lag1
- dcep_lag2
- dcep_lag3
- dcep_lag4plus
- dcep_lead2
- dcep_lead3
- dcep_lead4plus
- dcep_post
- dcep_rel_year
- dcep_treat_year
- dcep_treated
unit: 0/1 指示变量与事件时相对年 (无量纲; dcep_rel_year 为相对年整数, 以 double 存储以容纳缺失)
formula: "dcep_rel_year = 日历年 - dcep_treat_year (事件时 k); dcep_treated = 1{银行曾进入 DCEP 试点}; dcep_post = 1{k >= 0}; dcep_lag{h} = 1{k = h} (h=0..3), dcep_lag4plus = 1{k >= 4}; dcep_lead{h} = 1{k = -h} (h=2,3), dcep_lead4plus = 1{k <= -4}; k = -1 为省略基期; dcep_ddd_digfront = dcep_treated x post x digfront (三重差分交互)"
producer: pipeline\panel\export.py (列装配与标签); pipeline\audit\stata_audit.py (0/1 值域与哑变量合规审计)
upstream:
- 40_panel_yearly.parquet (bank-year 骨架 + 日历年轴)
- DCEP 试点名册 (dcep_treat_year 处理队列来源)
citations:
- doi: 10.1093/restud/rdae007
  type: journal
  authors: Borusyak, K., Jaravel, X., & Spiess, J.
  year: 2024
  title: "Revisiting event-study designs: Robust and efficient estimation"
  venue: Review of Economic Studies
  vol: 91
  issue: 6
  pages_or_artno: 3253-3285
- doi: 10.1093/restud/rdad018
  type: journal
  authors: Rambachan, A., & Roth, J.
  year: 2023
  title: "A more credible approach to parallel trends"
  venue: Review of Economic Studies
  vol: 90
  issue: 5
  pages_or_artno: 2555-2591
- doi: 10.1016/j.jeconom.2023.03.008
  type: journal
  authors: Roth, J., Sant'Anna, P. H. C., Bilinski, A., & Poe, J.
  year: 2023
  title: "What's trending in difference-in-differences? A synthesis of the recent econometrics literature"
  venue: Journal of Econometrics
  vol: 235
  issue: 2
  pages_or_artno: 2218-2244
- doi: 10.1016/j.jfineco.2022.01.004
  type: journal
  authors: Baker, A. C., Larcker, D. F., & Wang, C. C. Y.
  year: 2022
  title: "How much should we trust staggered difference-in-differences estimates?"
  venue: Journal of Financial Economics
  vol: 144
  issue: 2
  pages_or_artno: 370-395
- doi: 10.1257/aeri.20210236
  type: journal
  authors: Roth, J.
  year: 2022
  title: "Pretest with caution: Event-study estimates after testing for parallel trends"
  venue: "American Economic Review: Insights"
  vol: 4
  issue: 3
  pages_or_artno: 305-322
- doi: 10.1016/j.jeconom.2020.12.001
  type: journal
  authors: Callaway, B., & Sant'Anna, P. H. C.
  year: 2021
  title: "Difference-in-differences with multiple time periods"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 200-230
- doi: 10.1016/j.jeconom.2020.09.006
  type: journal
  authors: Sun, L., & Abraham, S.
  year: 2021
  title: "Estimating dynamic treatment effects in event studies with heterogeneous treatment effects"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 175-199
- doi: 10.1016/j.jeconom.2021.03.014
  type: journal
  authors: Goodman-Bacon, A.
  year: 2021
  title: "Difference-in-differences with variation in treatment timing"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 254-277
- doi: 10.1257/aer.20181169
  type: journal
  authors: de Chaisemartin, C., & D'Haultfœuille, X.
  year: 2020
  title: "Two-way fixed effects estimators with heterogeneous treatment effects"
  venue: American Economic Review
  vol: 110
  issue: 9
  pages_or_artno: 2964-2996
new_dois: []
---

## CORE

【构念与来源】
本家族刻画数字人民币试点 (DCEP, Digital Currency Electronic Payment; 央行数字货币的中国落地形态) 作为一次错时推行的政策冲击, 在银行-年面板上所需要的全套双重差分与事件研究设计变量。与本仓库绝大多数家族不同, 这一族列不是从新闻文本抽取的情感、注意力或嵌入测度, 而是识别策略本身的骨架: 它把"哪些银行、在哪一年、被这项政策处理"这一事实编码为一组指示变量与事件时相对年, 供下游回归模板估计政策效应。构念的原始来源是 DCEP 试点的分批推行名册——数字人民币自试点城市与场景分批扩围, 不同银行因其所在地、业务条线与试点参与身份而在不同年份进入处理状态, 由此天然形成错时 (staggered) 采纳结构。家族把这一名册映射到面板上: 每家银行有一个首次处理年 dcep_treat_year (从未处理者取缺省), 由它与日历年轴相减得到事件时相对年 dcep_rel_year, 再以相对年为轴把动态效应切成一组以基期为参照的哑变量。这样, 一族列同时承载了三种角色: 处理组身份 (dcep_treated)、处理期开关 (dcep_post) 与逐期动态分解 (leads / lags), 外加一个三重差分交互项 (dcep_ddd_digfront) 用于剥离与数字前沿禀赋相关的混淆。

【方法学与计算】
计算链路以处理队列为起点: 先在名册中确定每家银行的首次处理年 dcep_treat_year, 再令 dcep_rel_year = 日历年 − dcep_treat_year 得到事件时 k。dcep_treated 是时不变的处理组指示 (曾进入试点即恒为 1), dcep_post 是随时间开合的处理期指示 (k ≥ 0 记 1), 两者相乘即经典 2×2 双重差分的交互项。事件研究部分把 k 离散成一组互斥的哑变量: dcep_lag0 (k=0, 处理当年)、dcep_lag1/2/3 (k=+1/+2/+3)、dcep_lag4plus (k≥4 的右端归并箱)、dcep_lead2/3 (k=−2/−3) 与 dcep_lead4plus (k≤−4 的左端归并箱)。此处刻意不设 dcep_lead1: 相对年 k=−1 是被省略的参照期 (baseline), 所有事件时系数都相对它读数, 这是现代事件研究的规范做法, 也是为何这一族没有 k=−1 列而不是遗漏。右/左两端采用归并箱 (bin-and-truncate) 而非无限延伸的单期哑变量, 是为了在样本两翼观测稀薄处避免估计爆炸并吸收长期趋势, 符合 Borusyak, Jaravel & Spiess (2024) 对端点处理的建议口径。dcep_ddd_digfront 则在双重差分之上叠加第三重差分: 以数字前沿 (digital frontier) 禀赋维度 digfront 与处理×处理期交互, 目的是把"恰好处于数字化前沿的银行本就会走的轨迹"从政策效应中差分掉。所有列的取值合规性由 pipeline\audit\stata_audit.py 强制审计——该审计把凡以 dcep_ 前缀命名者纳入哑变量检查, 仅豁免 dcep_treat_year 与 dcep_rel_year 两列 (前者是年份码、后者是可正可负的相对年), 其余列若出现 0/1 以外取值即判 FAIL; 处理期与处理组指示还与 n_articles 非负、情感列值域等一并进入面板落盘前的机械闸。列的英文标签与最终装配在 pipeline\panel\export.py 完成, 该文件把 dcep_treated/post/treat_year 归入"DID 政策冲击"块、把 rel_year 与 leads/lags 归入"Event Study 动态效应"块; 该块在 export.py 源码中以一行代码注释标注了 Callaway & Sant'Anna (2021) 的方法出处 (注释位于标签装配块上方, 标签字符串本身并不含该引注)。

【文献定位】
本家族的方法学根基是 2020 年以来那场关于错时双重差分的计量革命。传统做法把处理组×处理期交互项塞进双向固定效应 (TWFE) 回归读取一个平均效应, 但 Goodman-Bacon (2021) 的分解证明: 在错时采纳下, TWFE 估计量其实是所有可能的 2×2 比较的加权和, 且当处理效应随时间演化时会出现"以已处理单位充当对照"的坏比较, 携带负权重, 从而使总估计量偏离任何有意义的加权平均。de Chaisemartin & D'Haultfœuille (2020, AER) 在异质处理效应框架下独立给出同一诊断并提出稳健估计量。正因如此, 本家族刻意提供逐期动态分解而非单一 post 交互, 使下游可采用 Callaway & Sant'Anna (2021) 的多期分组估计量、Sun & Abraham (2021) 的交互加权事件研究等对队列异质性稳健的方法, 而不必依赖有偏的朴素 TWFE。Baker, Larcker & Wang (2022) 在金融学语境下系统检验了这些偏误对已发表实证结论的影响, 强调金融面板研究应默认采用稳健估计量, 这正是本家族在设计上留出 leads/lags 与 treat_year 队列信息的动机。事件研究的 leads (dcep_lead*) 承担平行趋势诊断: 处理前各期系数应统计不可区分于零。但 Roth (2022) 警示, 简单地"目视 leads 是否为零"作为预检验会引入选择偏误并扭曲后续推断; Rambachan & Roth (2023) 进而提出以对预趋势违背幅度设界的方式做更可信的敏感性分析。Roth, Sant'Anna, Bilinski & Poe (2023) 对这一整条文献做了权威综述, 是理解本家族各列如何协同服务于识别的入口。需要强调的是, 这一族 leads/lags 是同一事件研究设定内互斥的时间分箱, 属于对单一动态路径的分解, 并非本仓库其它家族中"互为稳健性、不分主次、禁混进同一 over-identified Hansen J"意义上的并排稳健性梯子——它们本就应当同时进入同一回归的右手边共同刻画动态效应, 这一点与三轨或 co-primary 双轨的正交并排口径不同, 使用时不可混淆。

## VAR: dcep_treated

【变体差分】
本列是家族中的处理组身份指示, 时不变: 一家银行只要在样本期内曾进入 DCEP 试点, 该列即在其所有年份恒取 1, 从未进入者恒取 0。它对应 export.py 中"DCEP Pilot (0/1)"标签, 是双重差分中截面维度的处理组划分, 单独进入回归时被银行固定效应吸收, 真正的识别力来自它与处理期或事件时哑变量的交互。与 dcep_post 的区别在于时间维度: dcep_treated 不随年份变化 (回答"是不是处理组"), dcep_post 随年份开合 (回答"是不是处理期"), 二者相乘才得到经典 2×2 DID 的处理×处理期项。与 dcep_treat_year 的区别在于信息粒度: treated 只保留 0/1 的组别, treat_year 保留具体队列年份, 后者是错时 DID 估计量 (如 Callaway & Sant'Anna 分组 ATT) 所必需而前者不足以支撑。该列受 stata_audit.py 哑变量闸约束, 取值越出 {0,1} 即判 FAIL, 保证下游交互项语义干净。它是理解本家族的截面锚点, 一切事件时分解都建立在"谁属于处理组"这一判定之上。需要特别说明的是, 由于本列时不变, 在含银行固定效应的面板回归中它的主效应无法单独识别 (被完全吸收), 因此它几乎从不作为独立解释变量出现, 而总是以交互形式贡献识别信息; 这也解释了为何家族同时保留 treated 与 post 两个看似冗余的指示: 前者定组、后者定期, 二者的乘积才是双重差分真正估计的对象。在稳健性检验中, 研究者常以 treated 定义处理与对照两个子样本, 再在其上分别验证平行趋势或做安慰剂检验, 因此它也是样本切分的天然依据。使用时须核对从未处理组是否被正确编码为 0 而非缺失, 以免在构造交互项时引入意外的缺失传播。

## VAR: dcep_post

【变体差分】
本列是处理期开关, 随日历年开合: 当某观测的事件时 k ≥ 0 (即该银行已进入或越过其首次处理年) 时取 1, 否则取 0; 对应 export.py 的"Post DCEP Pilot (0/1)"标签。它与 dcep_treated 的乘积构成标准双重差分的处理×处理期交互, 读取一个跨所有处理后期的平均政策效应。columns.json 将本列标记为 needs_review, 提示写手核对其精确口径: 生产实现中 post 是相对处理事件的时间指示而非固定日历断点, 因此对不同队列的银行, 同一日历年可能一为 post 一为 pre——这正是错时设计区别于单一断点 DID 之处, 也是为何朴素 TWFE 在此会产生 Goodman-Bacon (2021) 所述坏比较的根源。与 leads/lags 各列的区别在于聚合层次: dcep_post 把所有 k ≥ 0 期压成一个开关读取平均效应, 而 dcep_lag0/1/2/3/4plus 把同一处理后区间逐期展开读取动态路径, 二者服务于不同的估计目标 (平均 vs 动态), 通常不在同一设定中同时充当处理项。本列同样受哑变量审计闸约束, 仅取 0/1。在实践中, dcep_treated 与 dcep_post 的乘积给出的是跨全部处理后期的一个平均处理效应, 简洁但掩盖了效应的时间形状; 当研究者更关心政策效应是即时到位还是逐年累积时, 应转向 leads/lags 分解而非依赖单一 post 交互。同时须警惕, 在错时采纳下把 treated×post 直接塞进 TWFE 读取的系数并非任何有意义的加权平均, 这一点已由 Goodman-Bacon (2021) 与 de Chaisemartin & D'Haultfœuille (2020) 严格证明, 因此本列的双重差分读数应被视为描述性起点, 正式识别应交由对异质效应稳健的现代估计量完成。核对口径时还须确认 post 对从未处理组的取值约定 (通常恒为 0), 避免其被误纳入处理后计数。

## VAR: dcep_treat_year

【变体差分】
本列记录每家银行的首次处理年 (处理队列 / cohort), 是错时双重差分估计量的核心输入; 对应"DCEP First Treatment Year"标签, 以整数年份存储, 从未处理者取约定缺省值。它与家族中所有 0/1 指示列的根本区别在于: treat_year 不是哑变量而是队列标签, 因此 stata_audit.py 的哑变量闸显式豁免本列 (与 dcep_rel_year、sandbox_treat_year 并列在豁免清单中), 否则其多取值的年份码会被误判为非法。dcep_rel_year 正是由本列与日历年相减派生, 因此 treat_year 是整条事件研究时间轴的原点。相对于 dcep_treated 只保留 0/1 组别, 本列保留的队列信息使下游可实现 Callaway & Sant'Anna (2021) 的分组-时期 ATT、Sun & Abraham (2021) 的交互加权估计等以队列为单位、对异质处理效应稳健的方法; 没有它, 面板只能退回可能有偏的朴素 TWFE。队列信息还是判定错时结构本身的依据: 通过统计不同 treat_year 上的银行数, 可以直接看出处理是集中于少数几批还是高度分散, 前者接近分块的准断点设计、后者才是真正意义上的错时采纳, 二者对估计量选择的含义不同。Baker, Larcker & Wang (2022) 在金融面板语境下强调, 报告处理队列的时间分布是错时 DID 研究应当披露的基本信息, 因为坏比较偏误的严重程度直接取决于队列的错开程度与效应异质性的大小。使用时需注意从未处理组在本列的缺省编码约定, 以免在构造 rel_year 或分组时把缺省值误当真实队列年份, 这类编码错误会静默地把从未处理组污染进某个虚假队列, 从而扭曲整条事件时轴。

## VAR: dcep_rel_year

【变体差分】
本列是事件时相对年 k = 日历年 − dcep_treat_year, 即距首次处理的年数, 可正可负; 对应"DCEP Relative Year to Treatment"标签。它是家族中唯一以 double 存储的列 (其余为整数 0/1 指示), 以此容纳负值与从未处理组的缺失, 也因此被 stata_audit.py 的哑变量闸显式豁免——它本就不是 0/1 变量。dcep_rel_year 是把政策冲击对齐到统一事件时钟的关键: 不同队列的银行在各自的处理年被对齐到 k=0, 使得跨队列的动态路径可比。家族中的一整组 leads/lags 哑变量都是本列的离散化产物: dcep_lag{h} 标记 k=h, dcep_lead{h} 标记 k=−h, 两端 4plus 箱标记 |k|≥4 的归并区。与这些哑变量相比, dcep_rel_year 保留连续 (整数) 事件时信息, 既可用于构造上述分箱, 也可直接用于以相对年为横轴绘制事件研究图或做参数化趋势设定。需注意 k=−1 在下游被约定为省略基期, 因此虽然 rel_year 本身取得到 −1, 但对应的 lead1 哑变量刻意不物化, 以免与基期共线。作为连续事件时的载体, 本列也是各种敏感性检验的接口: 例如可用它构造处理前的线性趋势项来检验预趋势, 或据 Rambachan & Roth (2023) 的框架在 rel_year 上设定对预趋势违背幅度的约束再评估处理后系数的稳健区间。对从未处理组, 本列因无 treat_year 而取缺失, 使用时须确保这些观测在事件研究样本中被恰当处理 (作为纯对照或按估计量要求纳入), 而非因缺失被机械剔除导致对照信息流失。相对省略基期的读数约定意味着, 解释任何 rel_year 派生系数时都要牢记零点锚定在 k=−1 而非绝对水平。

## VAR: dcep_ddd_digfront

【变体差分】
本列是家族中唯一的三重差分 (DDD, difference-in-differences-in-differences) 交互项: 在处理组×处理期的双重差分之上, 再叠加数字前沿维度 digfront (刻画银行既有数字化禀赋是否处于前沿) 作为第三重差分。其构念目的是把"恰好处于数字化前沿的银行本就会经历的轨迹"从 DCEP 政策效应中差分掉, 从而缓解处理组分配可能与数字禀赋相关所带来的混淆——若数字前沿银行既更可能早进试点、又本就沿更陡的数字化路径演化, 单纯的 DID 会把后者误记为政策效应, 而 DDD 通过在前沿/非前沿两层各做一次 DID 再相减来净化这一部分。与 dcep_treated×dcep_post 构成的双重差分项相比, 本列多出 digfront 这一层交互, 因此识别所依赖的平行趋势假设从"处理与对照两组趋势平行"放宽为"前沿与非前沿间的处理-对照差异趋势平行", 这是一个通常更可信但也更依赖 digfront 维度测度质量的设定。该列受哑变量审计闸约束取 0/1 (作为三向交互指示)。它是本家族识别策略的稳健性支柱: 当读者担心 DCEP 处理分配的内生性时, DDD 提供了一个剥离数字禀赋混淆的对照读数, 与主 DID 设定互相印证。需要澄清的是, 本列与家族其余 leads/lags 分箱不构成"互为稳健性、不分主次"的并排梯子: DDD 是在识别假设层面对主 DID 的加强 (放宽平行趋势为差分后的平行), 而非同一构念的替代测度, 因此二者通常作为主设定与稳健性设定分别呈现, 不宜简单合并进同一 over-identified 检验框架。实证中本列常与主 DID 的处理×处理期系数并列报告, 若两者符号一致、量级相近, 则说明数字前沿禀赋并非驱动主结果的主要混淆; 若 DDD 读数显著收缩, 则提示原 DID 效应中相当部分实为前沿银行本身的数字化轨迹。digfront 维度的测度口径 (以何指标、何阈值划定"前沿") 直接决定本列的解释力, 使用时须核对其定义与稳健性。

## VAR: dcep_lag0

【变体差分】
本列是事件研究处理当年 (k=0) 的哑变量: 当某观测的 dcep_rel_year 恰为 0 (即该银行处于其首次处理年) 时取 1, 否则取 0; 对应"DCEP Treatment Year (k=0)"标签。它是处理后动态路径的起点, 读取政策生效当年即时效应。与 dcep_post 的区别在于: post 把所有 k≥0 期压成单一平均开关, 而 lag0 只挑出 k=0 这一期, 与 lag1/2/3/4plus 一道把处理后区间逐期展开, 使下游得以观察效应是当年跳升还是逐年累积。与各 lead 列的区别在于时序方向: lead 落在处理前 (k<0) 服务于平行趋势诊断, lag 落在处理后 (k≥0) 承载真实的政策动态效应。所有 lag/lead 哑变量都相对省略基期 k=−1 读数, 因此 dcep_lag0 的系数应理解为处理当年相对处理前一年的效应差。本列受哑变量审计闸约束, 仅取 0/1, 保证事件研究设定中各期分箱互斥且干净。在 DCEP 这类涉及支付与结算基础设施的政策中, 处理当年的即时效应往往受实施节奏影响: 若试点在年内较晚落地, k=0 系数会低估稳态效应, 使动态路径呈现先低后高的形态; 反之若市场存在提前反应, 部分效应可能已泄漏到 lead 期。因此 dcep_lag0 通常与其后的 lag1/lag2 系数联读, 而非孤立解释。需强调本列虽名为 lag0, 语义上是"处理当期"而非滞后一期, 命名沿用事件研究惯例中以 lag 统称处理后各期、以 lead 统称处理前各期的约定, 阅读时不应把 lag0 误解为滞后算子作用后的结果。

## VAR: dcep_lag1

【变体差分】
本列标记事件时 k=+1, 即首次处理后第一年 (dcep_rel_year 为 1 时取 1); 对应"DCEP Lag 1 Period (k=+1)"标签。它与 dcep_lag0 的差别仅在事件时相差一期, 二者连同 lag2/3/4plus 共同刻画政策效应在处理后逐年的演化形状——效应是当年到位后维持、继续放大还是衰减, 正由这一组相邻 lag 系数的相对大小揭示。相对 dcep_post 的单一平均读数, 本列提供的是处理后第一年这一特定期的边际信息, 这在评估政策效应是否随时间累积 (dynamic build-up) 时尤为关键, 也是 Sun & Abraham (2021)、Callaway & Sant'Anna (2021) 等动态估计量所要还原的对象。系数相对省略基期 k=−1 读数。本列受哑变量审计闸约束仅取 0/1, 与家族其它事件时分箱互斥。处理后第一年常是判断政策效应性质的关键节点: 若 k=+1 系数显著大于 k=0, 提示效应存在滞后累积, 符合金融机构与市场对新支付基础设施逐步适应的先验; 若 k=+1 与 k=0 相当, 则提示效应近似一次性跳升。在错时结构下, 用朴素 TWFE 读取的动态系数会因坏比较而失真, Sun & Abraham (2021) 的交互加权估计正是为还原本列这类逐期系数的无偏读数而设计, 因此实证中应优先以其还原 k=+1 效应而非直接对 dummy 做 OLS。使用时须与相邻 lag/lead 列一并纳入同一设定, 单独抽取会破坏分解完整性与基期参照。

## VAR: dcep_lag2

【变体差分】
本列标记事件时 k=+2, 即首次处理后第二年 (dcep_rel_year 为 2 时取 1); 对应"DCEP Lag 2 Periods (k=+2)"标签。它在处理后动态序列中承接 lag1、领先 lag3, 用以刻画政策效应进入第二年后的水平。与家族其它 lag 列同为处理后逐期分箱, 差别仅在事件时取值; 与 lead 列的差别在于落于处理后区间, 承载真实效应而非预趋势诊断。在 DCEP 这类涉及支付习惯与银行业务条线渐进调整的政策中, 中期 (k=+2) 系数往往比即时 (k=0) 系数更能反映稳态效应, 因为机构与市场的适应需要时间; 这正是本家族逐期展开而非仅用单一 post 开关的价值所在。系数相对省略基期 k=−1 读数, 受哑变量审计闸约束仅取 0/1。在有限 T 的银行-年面板上, k=+2 已属较远期, 能同时观测到该期的队列数会随事件时增大而减少, 因此本列系数的估计精度通常低于近期 lag, 置信区间更宽; 解释其量级时须结合样本量与标准误, 避免把因样本稀薄导致的波动误读为效应衰减。它应与其余 lag/lead 列共同进入同一事件研究回归, 以保持动态路径分解的互斥与完整; 若研究者关心的是政策的中期稳态效应, 本列往往比 lag0 更具政策解读价值, 但代价是识别所依赖的可观测队列更少、外推性更受限。

## VAR: dcep_lag3

【变体差分】
本列标记事件时 k=+3, 即首次处理后第三年 (dcep_rel_year 为 3 时取 1); 对应"DCEP Lag 3 Periods (k=+3)"标签。它是处理后逐期分箱中最后一个单期哑变量, 其后即由归并箱 dcep_lag4plus 吸收更远期。在 T 有限的银行-年面板上, k=+3 常已接近多数队列的可观测右端, 因此本列系数对判断政策效应是否在中长期趋于稳定或衰减具有指示意义。与 dcep_lag4plus 的关键区别在于粒度: lag3 是精确的单期 (k=3), 而 lag4plus 把 k≥4 的所有远期压成一箱以避免样本稀薄处的估计爆炸。与 lead 列的区别在于时序方向 (处理后 vs 处理前)。系数相对省略基期 k=−1 读数, 受哑变量审计闸约束仅取 0/1。作为最后一个精确单期的处理后哑变量, 本列在设计上承担着"归并前的最后一档": 它与其后的 dcep_lag4plus 一起决定了动态路径在何处从逐期刻画切换为聚合刻画, 这一切换点的选择 (此处为 k=3 与 k≥4 之间) 是研究者在分辨率与估计稳定性之间的权衡, 应与样本的时间跨度相匹配。在 DCEP 面板中, 若多数队列的可观测右端不超过 k=3, 则本列已接近能提供单期信息的极限, 更远期只能靠归并箱把握趋势。本列须与家族其它事件时分箱一并纳入同一设定共同刻画动态路径, 单独抽取会破坏分解的完整性与基期参照的可解释性, 也会使 lag4plus 的归并语义失去参照。

## VAR: dcep_lag4plus

【变体差分】
本列是处理后右端归并箱: 当事件时 k≥4 (dcep_rel_year 大于等于 4) 时取 1; 对应"DCEP Lag 4+ Periods (k>=+4)"标签。它与 dcep_lag0/1/2/3 的单期哑变量不同——不是精确某一期, 而是把处理后第四年及以后的所有远期合并为一箱。这一 bin-and-truncate 设计是现代事件研究的规范做法: 在样本两翼观测稀薄、单期估计易爆炸的区域, 用归并箱吸收长期效应既稳定估计又保留"远期是否持续"的信息, 与 Borusyak, Jaravel & Spiess (2024) 关于端点处理的建议一致。与左端对称箱 dcep_lead4plus 的区别在于时序方向: 本列聚合处理后远期承载持续效应, lead4plus 聚合处理前远期服务于长期预趋势诊断。系数相对省略基期 k=−1 读数, 受哑变量审计闸约束仅取 0/1。归并箱的存在是事件研究在有限面板上的必要妥协: 若为 k≥4 的每一期都单设哑变量, 越远期能观测到的队列越少, 单期系数会因样本极稀而剧烈波动甚至不可估, Borusyak, Jaravel & Spiess (2024) 讨论的稳健高效估计正是针对这类端点问题。把远期合并成一箱既稳住估计, 又保留了"政策效应在长期是否持续存在"这一关键信息——本列系数显著为正即提示效应长期不消退。使用时应意识到本列系数是一个跨多期的加权平均而非单期读数, 其对应的银行-年集合随队列的可观测长度而变, 因此解释其量级时须与单期 lag 列区别对待, 也不宜与近期系数直接做斜率比较来推断衰减速率。

## VAR: dcep_lead2

【变体差分】
本列标记事件时 k=−2, 即首次处理前第二年 (dcep_rel_year 为 −2 时取 1); 对应"DCEP Lead 2 Periods (k=-2)"标签。作为处理前分箱, 它不承载政策效应而服务于平行趋势诊断: 在无预期效应且识别假设成立时, 本列系数应统计不可区分于零。与各 lag 列的根本区别正在于此——lead 落于处理前, 其系数是否为零是判断处理组与对照组处理前趋势是否平行的直接证据。家族刻意不物化 dcep_lead1 (k=−1), 因为 k=−1 被约定为省略基期, 所有 lead/lag 系数都相对它读数; 因此本列 dcep_lead2 是最靠近基期的可估处理前系数, 对预趋势诊断信息量最高。需注意 Roth (2022) 的告诫: 不应把 lead 系数是否显著为零作简单的预检验后再决定设定, 这会引入偏误——因为在预检验通过的条件下继续估计处理效应, 相当于以数据依赖的方式筛选样本, 会扭曲后续系数的抽样分布; 更稳妥的做法是配合 Rambachan & Roth (2023) 的敏感性框架, 对预趋势违背的幅度设界并直接给出处理后效应的稳健区间, 而非二元地"通过/否决"某个设定。在 DCEP 语境下, 本列若显著非零尤其值得警惕: 它可能提示试点城市或参与银行在政策前已沿更强的数字化轨迹演化, 这正是 dcep_ddd_digfront 三重差分想要剥离的混淆来源, 两列因此在识别上互为补充。本列受哑变量审计闸约束仅取 0/1, 与其余事件时分箱互斥。

## VAR: dcep_lead3

【变体差分】
本列标记事件时 k=−3, 即首次处理前第三年 (dcep_rel_year 为 −3 时取 1); 对应"DCEP Lead 3 Periods (k=-3)"标签。它与 dcep_lead2 同为处理前分箱、同服务于平行趋势诊断, 差别仅在离基期更远一期。多个 lead 系数 (lead2、lead3、lead4plus) 联合构成处理前的动态路径, 其整体形状比单个系数更能反映是否存在渐进的预趋势或预期效应: 若 lead 系数随距处理时点临近而系统性偏离零, 则提示处理组在政策前已沿不同轨迹演化, 威胁识别。相对 lag 列的处理后效应, 本列是纯粹的证伪性检验变量——理想情形下其系数应为零。系数相对省略基期 k=−1 读数, 受哑变量审计闸约束仅取 0/1。在实证叙事中, lead2 与 lead3 的联合读数常以事件研究图处理前段是否平坦来呈现: 若这两期系数都统计不可区分于零且无明显趋势, 则为平行趋势假设提供直观支持; 若 lead3 到 lead2 呈现单调靠近零的形态, 则提示存在渐进的预期效应或预趋势, 威胁识别。但正如 Roth (2022) 所强调, 这种目视判断不能替代正式的敏感性分析。本列相比 lead2 离基期更远一期, 因而受更早期样本稀薄的影响更大, 其估计精度通常略低; 解释时应结合标准误而非仅看点估计。本列须与其余 lead/lag 分箱一并纳入同一事件研究设定, 单独抽取会破坏处理前趋势诊断的完整性与基期参照的一致性。

## VAR: dcep_lead4plus

【变体差分】
本列是处理前左端归并箱: 当事件时 k≤−4 (dcep_rel_year 小于等于 −4) 时取 1; 对应"DCEP Lead 4+ Periods (k<=-4)"标签。它与 dcep_lead2/3 的单期哑变量不同, 把首次处理前第四年及更早的所有远期合并为一箱, 与右端箱 dcep_lag4plus 对称。这一左端归并同样出于 bin-and-truncate 的考量: 处理前远期观测稀薄, 单期估计不稳, 归并成箱既稳定估计又吸收长期趋势基线, 使处理时点附近的 lead 系数更清晰地承担平行趋势诊断。与 dcep_lag4plus 的区别在于时序方向 (处理前 vs 处理后): 本列聚合的是政策生效前的远期, 其系数偏离零主要提示长期结构性差异或选择效应而非政策效应。系数相对省略基期 k=−1 读数, 受哑变量审计闸约束仅取 0/1。作为处理前最远的归并区间, 本列在事件研究中扮演双重角色: 一方面它吸收处理组与对照组在政策前很久就存在的水平差异, 使临近处理时点的 lead2/lead3 系数更聚焦于近端预趋势; 另一方面它自身的系数也是一种长期平行性检验——若其显著非零, 说明两组在远期已不可比, 单靠固定效应难以完全吸收, 此时应更审慎地依赖 dcep_ddd_digfront 等剥离禀赋混淆的设定。解释本列时须记住它是跨多个处理前远期的加权平均, 对应的银行-年集合随各队列可回溯的长度而变, 量级不可与单期 lead 直接比较; 它常被设为事件研究图最左端的参照区间, 与右端 lag4plus 对称收束整条动态路径。

<!-- rendered-citations:begin -->
Borusyak, K., Jaravel, X., & Spiess, J. (2024). Revisiting event-study designs: Robust and efficient estimation. Review of Economic Studies, 91(6), 3253-3285. https://doi.org/10.1093/restud/rdae007
Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. Review of Economic Studies, 90(5), 2555-2591. https://doi.org/10.1093/restud/rdad018
Roth, J., Sant'Anna, P. H. C., Bilinski, A., & Poe, J. (2023). What's trending in difference-in-differences? A synthesis of the recent econometrics literature. Journal of Econometrics, 235(2), 2218-2244. https://doi.org/10.1016/j.jeconom.2023.03.008
Baker, A. C., Larcker, D. F., & Wang, C. C. Y. (2022). How much should we trust staggered difference-in-differences estimates?. Journal of Financial Economics, 144(2), 370-395. https://doi.org/10.1016/j.jfineco.2022.01.004
Roth, J. (2022). Pretest with caution: Event-study estimates after testing for parallel trends. American Economic Review: Insights, 4(3), 305-322. https://doi.org/10.1257/aeri.20210236
Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics, 225(2), 200-230. https://doi.org/10.1016/j.jeconom.2020.12.001
Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics, 225(2), 175-199. https://doi.org/10.1016/j.jeconom.2020.09.006
Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. Journal of Econometrics, 225(2), 254-277. https://doi.org/10.1016/j.jeconom.2021.03.014
de Chaisemartin, C., & D'Haultfœuille, X. (2020). Two-way fixed effects estimators with heterogeneous treatment effects. American Economic Review, 110(9), 2964-2996. https://doi.org/10.1257/aer.20181169
<!-- rendered-citations:end -->
