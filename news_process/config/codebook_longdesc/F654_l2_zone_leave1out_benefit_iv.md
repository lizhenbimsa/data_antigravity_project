---
family_id: F654
columns:
- zone_leave1out_benefit_iv
- zone_leave1out_benefit_iv_ctx
- zone_leave1out_benefit_iv_ss
unit: 工具变量 (无量纲, 与被工具化的内生变量 benefit_mean 同量纲, 取值域为经营效益态度均值的连续实数)
formula: "zone_leave1out_benefit_iv_{i,t} = ( Σ_{j∈zone(i), 有效} benefit_mean_{j,t} − benefit_mean_{i,t}·1[i 有效] ) / ( n_{zone(i),t}^{有效} − 1[i 有效] ); 分组列 = bank_zone; 剩余有效同经济圈同业数 < 2 或 zone∈{other,NaN} → NaN; 无 _lag1 (add_lag1=False)"
producer: news_process/pipeline/panel/iv_extensions.py::compute_peer_loo_iv (runner 步骤 8z, compute_iv_extensions 编排) ; 标签经 news_process/pipeline/panel/stata_export.py::HEURISTIC_LABELS 注入 .dta
upstream:
- 40_panel_yearly.parquet (benefit_mean_full / benefit_mean_ctx / benefit_mean_ss, bank_zone)
- benefit_society 维度测度 (dimension_analysis 产 benefit_mean 系列)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.1080/07350015.2026.2618311
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2026
  title: "Gradient wild bootstrap for instrumental variable quantile regressions with weak and few clusters"
  venue: Journal of Business & Economic Statistics
  pages_or_artno: 1-12
- doi: 10.48550/arXiv.2504.05658
  type: arxiv
  authors: Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y.
  year: 2025
  title: "Identification and estimation of causal peer effects using instrumental variables"
  venue: arXiv
- doi: 10.48550/arXiv.2509.12538
  type: arxiv
  authors: Nibbering, D., & Oosterveen, M.
  year: 2025
  title: "Policy-relevant causal effect estimation using instrumental variables with interference"
  venue: arXiv
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: 241
  issue: 1
  pages_or_artno: 105727
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: 132
  issue: 7
  pages_or_artno: 2274-2303
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: Journal of the Royal Statistical Society Series A
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.48550/arXiv.2308.04276
  type: arxiv
  authors: Hoshino, T.
  year: 2023
  title: "Causal interpretation of linear social interaction models with endogenous networks"
  venue: arXiv
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1177/1536867X20953572
  type: journal
  authors: Dippel, C., Ferrara, A., & Heblich, S.
  year: 2020
  title: "Causal mediation analysis in instrumental-variables regressions"
  venue: The Stata Journal
  vol: 20
  issue: 3
  pages_or_artno: 613-626
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: 11
  pages_or_artno: 727-753
- doi: 10.3368/jhr.50.2.317
  type: journal
  authors: Cameron, A. C., & Miller, D. L.
  year: 2015
  title: "A practitioner's guide to cluster-robust inference"
  venue: Journal of Human Resources
  vol: 50
  issue: 2
  pages_or_artno: 317-372
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1017/CBO9780511614491.006
  type: book
  authors: Stock, J. H., & Yogo, M.
  year: 2005
  title: "Testing for weak instruments in linear IV regression"
  venue: "Identification and inference for econometric models: Essays in honor of Thomas Rothenberg"
  pages_or_artno: 80-108
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (zone_leave1out_benefit_iv 及其 _ctx / _ss 孪生) 是 benefit_society 论文识别策略的核心工具变量, 用于工具化银行层面的内生解释变量「经营效益态度」(benefit_mean, 即媒体报道中对该银行是否服务实体、造福社会的语义倾向均值)。被工具化的内生变量 benefit_mean 本身取自 Jha, Liu & Manela (2026) 在 Review of Financial Studies 提出的语言嵌入 (language embedding) 测度谱系: 以文本与「金融是否造福社会」这一构念方向向量的语义相似度刻画每篇报道的效益态度, 再在 bank-year 层面聚合为 benefit_mean_full / benefit_mean_ctx / benefit_mean_ss 三轨。由于一家银行当年获得的效益态度报道既可能是其真实经营行为的结果, 也可能反向承载了记者选择性报道、地方媒体立场、以及与银行财务表现同期共动的遗漏变量, 故 benefit_mean 与 benefit_society 的结果变量 (如 roa) 之间存在典型的双向因果与遗漏变量内生性。本家族提供一个「同经济圈留一 (leave-one-out) 均值」外生位移工具, 借同经济圈内其它银行的平均效益态度为焦点银行的效益态度提供一个仅经由同业模仿 / 区域舆论共振渠道、而非经由焦点银行自身财务后果渠道传导的外生变异。

【构念与来源】
「经济圈 (bank_zone) 分组」是本工具区别于同族其它 LOO 工具 (leave_one_out_peer_benefit_iv 以 bank_type 银行类型分组) 的关键设计。bank_zone 把全国银行按其注册 / 主要经营地所属的经济区域 (如东部沿海、中部、西部、东北等宏观经济带) 划分, 使「同组同业」在地理与制度环境上邻近但在具体经营决策上相互独立。这一分组由上游步骤 7f 物化到面板列 bank_zone; 若该列缺失 (7f 未运行), 生产函数 compute_iv_extensions 会把本家族三列整体优雅置 NaN 并打 WARNING, 绝不静默产出错误工具。分组取值为 'other' 或 NaN 的银行 (无法归入任何真经济圈的伪组) 被 compute_peer_loo_iv 明确拒绝置 NaN, 与 iv_did 模块的 compute_zone_leave1out 保持同一伪组拒绝口径, 避免把语义上不构成「同业外溢」的杂项银行掺进分子分母污染工具。

【方法学与计算】
计算引擎是通用的同组×年留一均值算子 compute_peer_loo_iv (iv_extensions.py), 对焦点银行 i、年份 t: 先在 (zone(i), t) 单元内对所有有效同业 (benefit_mean 非缺失且分组非伪组) 求和 Σ benefit_mean_{j,t} 与计数 n; 再从中减去焦点银行自身的贡献 (若其自身有效), 得剩余同业均值 (Σ − benefit_mean_{i,t}) / (n − 1)。留一构造确保工具在机械上不含焦点银行自身的信息, 是「反射问题 (reflection problem)」的标准一阶规避 (Manski, 1993): 若直接用含自身的组均值, 焦点银行既在左手边又在右手边, 内生 - 外生分量不可识别。剩余有效同业数低于 min_peers=2 时置 NaN——单个残余同业的均值噪声过大、且在小组内极易与焦点银行共享同一地方冲击, 不足以构成可信位移。全部数值以 float64 强制, 规避 masked Int8 groupby 的降型回绕 (与 iv_did g-ivdid-07 同型防护)。

【方法学与计算】
本家族三列刻意不产 _lag1 滞后变体 (add_lag1=False), 与同族的 leave_one_out_peer_*_iv (默认 add_lag1=True, 额外产 _lag1 以规避同期反射) 形成对照。原因是 bank_zone 分组下的同业集合远大于 bank_type 分组、且经济圈内成员经营决策的同期相关性主要来自区域宏观环境而非直接的银行间即时模仿, 故同期 zone-LOO 的反射污染在结构上已被跨经济圈、跨具体银行的双重距离稀释; 论文识别使用同期 zone-LOO 作 just-identified 主工具, 而把「同类型银行滞后一期 LOO」作为一个独立的、机制不同的备选 / 稳健工具并列, 二者刻意不合并进同一 over-identified 设定。这样的设计使 zone-LOO 工具在 T 较短的面板 (本机 T=2 试跑) 上不因首年滞后缺失而进一步损失样本, 也让「地理外溢」与「类型外溢」两条识别通道各自独立可检。

【文献定位】
本工具属于「同群 (peer-group) 留一均值工具」这一在公司金融与劳动经济学中成熟的识别族。Leary & Roberts (2014) 用同业公司特征的外生分量 (如同业股票的特质收益冲击) 工具化焦点公司所处的同群平均政策, 证明同群公司确实影响焦点公司的资本结构决策; 其识别逻辑——同群的某维度对焦点主体只经由「社会互动 / 模仿」渠道、而非经由焦点主体自身基本面渠道影响结果——正是本 zone-LOO 工具的方法学母板。Manski (1993) 的反射问题奠定了「不能用含自身的组均值识别内生社会效应」这一底层约束, 留一构造是对其最直接的回应。近年计量文献进一步收紧了 peer-effect IV 的有效性条件: Hoshino (2023) 讨论了当同群网络本身内生 (银行的经济圈归属并非随机) 时线性社会互动模型的因果解释边界; Luo et al. (2025) 系统给出用工具变量识别因果同群效应的识别与估计条件; Nibbering & Oosterveen (2025) 则专门处理「个体间相互干扰 (interference)」下 IV 估计的政策相关效应——这三支 2023-2025 的前沿共同提示: zone-LOO 工具的排他性依赖于「同经济圈其它银行的效益态度不经由焦点银行自身财务后果之外的其它渠道 (如共同的区域政策冲击直接作用于焦点银行 roa) 影响结果」, 该假设需以经济圈×年固定效应等设定加以捍卫。

【识别策略定位】
在 benefit_society 论文的 paper_spec.yaml::identification.iv 中, zone_leave1out_benefit_iv 被登记为 primary/fallback 全收的主识别工具, 故其 tier 判为 core (类别 3: 识别策略主 IV)。运行时它经 runner 步骤 8z 的 compute_iv_extensions 统一编排产出, 与其它十篇论文的 IV 列族 (leave_one_out_peer_* / bartik_* / outlet_* 等) 并排落盘, 并在 paper_spec 的 2SLS 模板中作为第一阶段回归的外生工具进入。识别所依赖的两条 Stock-Yogo (2005) 意义上的检验——弱工具第一阶段 F 与 (在过度识别设定下的) Hansen J——在本项目里遵循一条铁律: zone-LOO (地理外溢) 与 peer-type-LOO (类型外溢)、以及本工具的 full / ctx / ss 三轨版本, 各自构成 just-identified 的独立设定并排陈列, 互为稳健性、不分主次; 严禁把其中任意两者拼进同一 over-identified 的 Hansen J。原因在于过度识别检验 (overidentifying restrictions test) 只有当各工具经由「实质不同的外生渠道」传导时才有诊断功效, 而 full / ctx / ss 三轨源自同一篇报道的三个剪裁窗口 (full=标题+全文 / ctx=标题+实体窗口 / ss=标题+银行金科同句窗口), 同受 bank_type×year 共同冲击逐字污染, 拼成 overid 的 Hansen J 零功效——会给出误导性的「工具外生」通过判据。

【识别策略定位】
弱工具方面, 本工具在小簇 (few clusters) 与弱识别下的推断遵循 Andrews, Stock & Sun (2019) 的实践指引, 优先报告对弱工具稳健的置信集; 在 benefit_society 的稳健性 battery 中并配合近年针对「弱且少簇」情形的 wild bootstrap 推断 (Wang & Zhang, 2024) 与其分位数回归推广 (Wang & Zhang, 2026), 以及 Cameron & Miller (2015) 的簇稳健推断实践。当把工具用于中介分析 (效益态度 → 中介 → 结果) 时, 采用 Dippel, Ferrara & Heblich (2020) 的 IV 中介框架以在单一外生工具下同时识别直接与间接效应。这些 2019-2026 的方法学锚点共同构成本工具的推断护栏, 使 zone-LOO 识别在 T 短、簇少的银行面板上仍可给出诚实的不确定性度量。

【识别策略定位】
把本工具放进近年 IV 方法学的坐标系还需强调其与 shift-share (Bartik) 识别范式的分工。Goldsmith-Pinkham, Sorkin & Swift (2020) 揭示 Bartik 工具的识别力等价于以初始份额为工具的 GMM, 其外生性实质要求初始份额外生; Borusyak, Hull & Jaravel (2025) 则给出「份额不完整 / 重归一化选择」等实操陷阱的检查表; Apfel (2024) 进一步探讨在部分份额内生时如何松弛排他性; Gabaix & Koijen (2024) 从颗粒 (granular) 视角把个体层面的特质冲击聚合为宏观工具。本项目在 benefit_society 之外的多篇论文 (如注意力、实质性、协同模式) 确实并行产出 bartik_*_iv 列族作为 shift-share 通道的识别; 而 zone-LOO 与 peer-type-LOO 走的是「留一组均值」这条与 shift-share 机制正交的通道——前者的外生性挂在「同群冲击不直接作用于焦点结果」, 后者挂在「初始份额外生」。正因两条通道的排他性失效模式互不重叠, 它们互为强有力的稳健性交叉验证; 但也正因其失效模式不同, 绝不能把 zone-LOO 与 Bartik 拼进同一 over-identified Hansen J 当作「工具外生」的联合检验——那样的 Hansen J 通过与否都无法归因到具体哪条通道, 诊断价值为零。

【与相邻测度的构念区分】
本工具须与三类相邻测度严格区分。其一, 与同族 leave_one_out_peer_benefit_iv 的区别纯在分组维度: 后者按 bank_type 分组捕捉「同类型银行的态度外溢」, 前者按 bank_zone 分组捕捉「同经济圈银行的态度外溢」; 二者是两条独立的识别通道 (类型邻近 vs 地理邻近), 各自 just-identified 并排, 不并入同一 overid。其二, 与 Bartik / shift-share 类工具 (bartik_*_iv, 见 Goldsmith-Pinkham, Sorkin & Swift 2020; Borusyak, Hull & Jaravel 2025 的实操检查表; Apfel 2024 对排他性约束的松弛; Gabaix & Koijen 2024 的颗粒工具视角) 的区别在于位移的构造原理: Bartik 工具用「份额×共同冲击」的交互构造暴露, 而 zone-LOO 用「留一组均值」直接借同业实测值作位移, 二者的排他性失效模式不同 (Bartik 依赖份额外生, LOO 依赖同业冲击不直接作用于焦点结果), 故在稳健性上互补而不可混同进一个 Hansen J。其三, 与被工具化的内生变量 benefit_mean 本身的区别是「留一」——工具在机械上剔除了焦点银行自身贡献, 使其不再是内生量的平滑版本而是纯外生位移候选。

【方法学与计算】
须澄清「效益态度」这一被工具化内生变量与相邻情感 / 属性测度的边界, 以正确理解本工具的位移含义。benefit_mean 不是普通的正负情感极性 (那由 stage 21 三家 LLM 投票的 tone 测度承担), 而是专门刻画「该银行的行为 / 报道是否体现服务实体经济、造福社会」这一规范维度的语义倾向, 属 Jha, Liu & Manela (2026) 的规范嵌入构念族。因此 zone-LOO 工具借的是「同经济圈其它银行在公众舆论中被塑造的效益形象」这一区域性软环境, 而非同业的普通媒体情绪水平; 二者虽都源自媒体文本, 但构念方向不同, 工具的排他性论证也据此展开——地方公众对「金融是否造福社会」的整体氛围既塑造圈内所有银行的效益态度报道, 又不必然经由焦点银行自身效益行为之外的渠道直接改变其结果变量。这一构念定位是本工具区别于其它 peer-LOO 工具 (如注意力、实质性、技术定位、协同模式各自的 peer-LOO) 的语义根基。

【方法学与计算】
关于分子分母的边界情形, 引擎有若干明确约定值得复述以避免误用。其一, 焦点银行自身若在当年 benefit_mean 缺失 (无有效报道), 则它本就不进入组内有效计数, 留一时也无需再减自身 (own_valid=0), 分子分母自然只含其它有效同业——这保证「留一」在焦点自身缺测时不会错误地多减一。其二, 组内有效同业全部缺失或经济圈只有焦点一家银行时, 剩余计数为 0 或负, 经 min_peers=2 门槛统一置 NaN, 不会产出除零或单点均值。其三, 全流程 float64 强制与 remain_cnt.replace(0.0, np.nan) 的除零保护共同确保不产 inf。这些机械约定与 iv_did 模块的 compute_zone_leave1out 保持逐条一致, 使「经济圈留一」在本项目内跨模块口径统一 (面板 IV 扩展轨与 DID 识别轨同源)。

【文献定位】
被工具化的内生构念本身的文献母锚是 Jha, Liu & Manela (2026): 该文以语言嵌入方法把「金融是否造福社会」这一抽象规范构念操作化为文本与构念方向向量的语义相似度, 突破了传统词典法只能计数关键词、无法捕捉语义整体倾向的局限。本项目的 benefit_mean 系列直接承接这一测度谱系, 并在中文银行金科报道语料上以 co-primary 双轨嵌入 (canonical Qwen3-Embedding-8B 4096 维 / _lg text-embedding-3-large 3072 维) 实现——两轨同为主测度、互为稳健性、严格 parity。需强调的是: 本 IV 家族三列 (full / ctx / ss) 是「文本剪裁轨」的稳健性梯子, 而 benefit_mean 的 co-primary 嵌入双轨是「嵌入模型轨」的另一条正交稳健性梯子, 二者是两个不同维度; 与三轨同理, 两条 co-primary 嵌入各自 just-identified 并排、互为稳健性、不分主次, 严禁把两轨嵌入混进同一 over-identified Hansen J。本工具位于「文本测度 + peer-group IV」的交叉地带, 上承 Leary & Roberts (2014) 的同群工具识别范式, 下接近年对同群效应 IV 有效性条件日趋精细的收紧 (Hoshino 2023; Luo et al. 2025; Nibbering & Oosterveen 2025)。

【已知局限与稳健性梯子】
已知局限有四。第一, 排他性 (exclusion restriction) 是不可直接检验的实质假设: 若某经济圈遭遇的区域性政策 / 经济冲击既抬高了圈内其它银行的效益态度报道、又直接 (不经由焦点银行自身效益行为) 改变了焦点银行的结果变量, 则工具失效——论文以经济圈×年、银行类型×年等高维固定效应吸收共同冲击层, 并把 zone-LOO 与机制不同的 type-LOO 并排作为交叉验证。近年 shift-share 文献 (Apfel 2024) 提示: 即便份额 / 组均值构造在机械上剔除了自身, 只要位移与结果存在未被固定效应吸收的共同因子, 排他性仍可能被松动, 故本工具的识别断言须以可观测的区域冲击代理做安慰剂检验加以佐证, 而非仅凭构造的机械外生性。第二, 弱识别风险: 在 T=2 的本机试跑下, 经济圈×年单元内剩余有效同业数常低于 min_peers=2 的门槛, 本家族三列因而大面积退化为 NaN, 这是预期的样本稀薄退化 (模块头已披露), 全量 T=19 / 生产语料下工具有效率自然恢复; 使用者在小样本下应以 Andrews, Stock & Sun (2019) 与 wild bootstrap 推断护栏 (Wang & Zhang 2024, 2026) 诚实报告弱工具区间, 不得在少簇下依赖渐近正态。第三, 三轨稳健性梯子: full / ctx / ss 三轨各配同轨内生变量 (benefit_mean_full / _ctx / _ss) 的同轨 zone-LOO 工具, 表达对「文本剪裁窗口选择」的稳健性——三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把任意两轨的 zone-LOO 拼成一对工具跑 over-identified Hansen J (同一篇文章三窗共同污染, Hansen J 零功效)。ss 轨回退语义镜像 ctx: 当某篇报道无「银行∧金科同句共现」时, 其 ss 底层文本回退为全文, 对应的 benefit_mean_ss 与本 _ss 工具在该单元退化为 full 轨镜像, 这是优雅降级而非缺陷。第四, 分组粒度权衡: bank_zone 经济圈划分较粗, 使同组同业集合较大、位移较平滑但地理外生性较强; 若改用更细的省级分组 (bank_province) 则外生性可能更弱 (省内银行更易共享同一地方政策冲击) 而组内样本更薄——生产口径选择经济圈粒度是外生性与样本量的折中, 论文以省级分组作为稳健性备选并列, 与经济圈 zone-LOO 各自 just-identified、不并入同一 overid。

【已知局限与稳健性梯子】
在使用层面还须注意: 本工具与结果变量的对接依赖 benefit_society 论文的结果变量定义 (如 roa 或外部财务哨兵列), 财务面板接入时构造; 在财务数据尚未完整落位的当前阶段, 本工具的第一阶段 (工具 → 内生 benefit_mean) 已可独立诊断识别强度, 而完整两阶段的因果估计须俟结果变量到位。中介机制分析可采用 Dippel, Ferrara & Heblich (2020) 在单一外生工具下同时识别直接与间接效应的 IV 中介框架。全部标签经 stata_export.py 的 HEURISTIC_LABELS 注入 .dta; full 轨标签为中文「经济区留一效益态度(LOO,工具变量IV)」, ctx / ss 孪生在同一主干后机械追加中文轨别尾注 (分别为「,实体窗轨」「,同句轨」), 三条标签均为面向 Stata 使用者的简体中文短描述, 保证复现包模板可直接按列名引用其人类可读含义。最后须提醒: 本家族三列在生产落盘前是「真新面板列」, 其加入曾要求重跑 stage 45/46 并受控重生 golden 快照; 本机因语料为 T=2 试跑、data/raw 为空且付费 LLM 不可逆, golden 重生被 DEFER 到生产语料机, 故当前盘上若见本三列为 NaN 或缺席, 属预期的开发态状态而非缺陷, 使用者应在生产全量语料上评估其真实识别强度。

## VAR: zone_leave1out_benefit_iv

【变体差分】
本列是家族 canonical 列, 也是 benefit_society 论文的主识别工具 (tier=core)。其被工具化的内生变量是 full 轨的经营效益态度 benefit_mean_full, 即「标题 prepend + 全文正文」文本经语言嵌入测度得到的效益态度在 bank-year 层面的均值。full 轨与项目的「留篇门控 = full-only」(2026-06-29) 口径一致: 一篇报道是否算作「一篇银行金科报道」只看其 full 轨 LLM 判定, 故 full 轨的行宇宙即留篇集本身, benefit_mean_full 在最完整、门控最权威的样本上聚合, 是三轨中信息量最大、退化最少的一轨, 亦因此被选为主工具的内生源。本列的分组维度是 bank_zone (经济圈), 而非同族 leave_one_out_peer_benefit_iv 的 bank_type (银行类型)——这是本列与该 peer-type 工具的唯一差分: 二者捕捉两条独立外溢通道 (地理邻近 vs 类型邻近), 各自 just-identified 并排、互为稳健性、不分主次, 严禁并入同一 over-identified Hansen J。

【变体差分】
计算上, 本列对焦点银行 i、年份 t 取其所属经济圈 zone(i) 内、当年、剔除 i 自身后的其它有效银行的 benefit_mean_full 均值; 经济圈归属为 'other' 或缺失的银行按伪组拒绝置 NaN; 剔除自身后剩余有效同业数低于 2 时置 NaN。本列刻意不带 _lag1 滞后 (add_lag1=False), 使用同期 zone-LOO 作 just-identified 主工具——bank_zone 分组下的跨具体银行、跨地理距离双重稀释使同期反射污染在结构上被压低, 论文另以「同类型银行滞后一期 LOO」作为机制不同的独立备选工具并列, 二者不合并。本列的语义是: 为焦点银行的 full 轨效益态度提供一个仅经由同经济圈舆论共振 / 同业模仿渠道传导、不经由焦点银行自身财务后果渠道传导的外生位移。其排他性依赖「同经济圈其它银行的效益态度不直接作用于焦点银行结果」这一实质假设, 由经济圈×年等高维固定效应捍卫。在 T=2 本机试跑下, 经济圈×年单元有效同业数常不足门槛, 本列因而大面积 NaN, 属预期样本稀薄退化, 全量 T=19 恢复。使用本列作第一阶段工具时须以弱工具稳健推断 (Andrews, Stock & Sun 2019; wild bootstrap Wang & Zhang 2024) 诚实报告识别强度, 并遵守本工具与 peer-type-LOO、Bartik、ctx / ss 三轨版本各自 just-identified 并排、禁混同一 Hansen J 的铁律。

【变体差分】
作为主工具, 本列在 paper_spec.yaml::identification.iv 中被登记为 primary/fallback 全收, 是 tier=core 的判据来源 (类别 3: 识别策略主 IV)。它经 runner 步骤 8z 的 compute_iv_extensions 统一编排, 与十篇论文的其它 IV 列族并排落盘, 并在 benefit_society 的 2SLS 模板中作为第一阶段外生工具进入。相对于同族的其它变体, 本 canonical 列承担「主识别」角色而非仅稳健性轨: 其内生源 benefit_mean_full 处于 full-only 留篇门控 (2026-06-29) 的完整行宇宙上, 分母 n_articles 与门控口径严格一致, 是三轨中样本最全、退化最少、门控最权威的一轨, 故被选为主工具的内生变量。本列不带 _lag1 的设计使其在短面板上不因首年滞后缺失而额外损失样本——这一点相对于同族带 _lag1 的 peer-type LOO 工具是一个刻意的样本保全取舍。须再次强调本列与三类相邻工具的边界: 与 peer-type-LOO 差在分组维度 (经济圈 vs 类型), 与 Bartik 工具差在位移构造原理 (留一组均值 vs 份额×冲击交互), 与 ctx / ss 孪生差在内生源的文本剪裁轨——四者各自 just-identified 并排、互为稳健性、不分主次, 任意两者严禁并入同一 over-identified Hansen J, 因其外生渠道或文本窗口的共同污染会使过度识别检验丧失功效。

## VAR: zone_leave1out_benefit_iv_ctx

【变体差分】
本列 (tier=standard) 是 canonical 列的 ctx 轨孪生, 唯一差分在于其被工具化的内生变量改为 ctx 轨的 benefit_mean_ctx——即以「标题 prepend + 实体窗口 (银行 / 金科实体附近的文本窗口)」剪裁文本计算的效益态度均值, 而非 canonical 的 full 全文。ctx 轨归因把语义信号限定在实体邻近上下文, 属实体邻近上下文 (entity-proximity window) 的剪裁口径, 相对 full 轨更聚焦、噪声更低但样本更薄。本列由 2026-06-13 的四 agent 对抗终审落地, 与 full 轨 zone-LOO 一一镜像: 同以 bank_zone 分组、同期 (无 _lag1)、同 min_peers=2 门槛与伪组拒绝口径, 仅把内生源从 _full 换为 _ctx。其识别语义是: 为焦点银行的 ctx 轨效益态度提供同经济圈同轨留一均值位移。本列与 full 轨 zone-LOO、ss 轨 zone-LOO 三者各自 just-identified 并排、互为稳健性、不分主次, 表达对「文本剪裁窗口选择」的稳健性; 严禁把三轨中任意两轨的 zone-LOO 拼成一对工具跑 over-identified Hansen J——三轨源自同一篇报道的三个剪裁窗口, 同受 bank_type×year 共同冲击逐字污染, Hansen J 零功效。benefit_mean_ctx 缺列时 compute_peer_loo_iv 内置守卫将本列优雅置 NaN。本列是真新面板列, 落盘须重跑 stage 45/46 并受控重生 golden (本机不可安全 regen)。相对 canonical full 轨主工具, 本 ctx 轨列的定位是「文本窗口稳健性轨」而非主识别: 它回答「若把效益态度信号限定在实体邻近上下文而非全文, 主结论是否稳健」这一稳健性问题。ctx 轨样本较 full 更薄、退化更早, 在 T=2 试跑下有效率通常低于 canonical 列, 全量语料下恢复。使用本列须与 full / ss 轨 zone-LOO 各自独立跑 just-identified 2SLS 后并排比较系数, 绝不把两轨工具合成 overid。

## VAR: zone_leave1out_benefit_iv_ss

【变体差分】
本列 (tier=standard) 是 canonical 列的 ss 轨孪生, 唯一差分在于其被工具化的内生变量改为 ss 轨的 benefit_mean_ss——即以「标题 prepend + 银行∧金科同句共现窗口 (同一句内同时出现目标银行与金科词的句子 ±N 句窗)」剪裁文本计算的效益态度均值。ss 轨是三轨中语义最严格、共现要求最高的一轨, 其剪裁口径属「媒体共提及 (co-mention) 计量」谱系 (只保留银行与金科词在同一句内共现的最紧凑窗口), 与 ctx 的实体邻近窗口口径并列。ss 轨的回退语义镜像 ctx: 当某篇报道无「银行∧金科同句共现」时, 其 ss 底层文本回退为全文 body, 对应的 benefit_mean_ss 在该单元退化为 full 轨镜像——这是优雅降级而非缺陷。本列由 2026-06-14 的三轨平价补全落地, 与 full / ctx 轨 zone-LOO 一一镜像: 同以 bank_zone 分组、同期 (无 _lag1)、同 min_peers=2 门槛与伪组拒绝口径, 仅把内生源换为 _ss。其识别语义是为焦点银行的 ss 轨效益态度提供同经济圈同轨留一均值位移。本列与 full / ctx 轨 zone-LOO 三者各自 just-identified 并排、互为稳健性、不分主次; 严禁把任意两轨 zone-LOO 合成 over-identified Hansen J (同篇三窗共同污染, Hansen J 零功效)。benefit_mean_ss 缺列时守卫优雅置 NaN。本列亦是真新面板列, 落盘须重跑 stage 45/46 并受控重生 golden。相对 canonical full 轨主工具, 本 ss 轨列是三轨稳健性梯子中语义最严格的一端: 它回答「若只用银行与金科同句共现的最紧凑窗口计算效益态度, 主结论是否稳健」。由于同句共现要求极高, ss 轨在 T=2 试跑下退化最甚 (大量单元回退全文镜像或直接 NaN), 全量 T=19 恢复。使用本列须与 full / ctx 轨 zone-LOO 各自独立跑 just-identified 2SLS 后并排, 表达对文本剪裁窗口选择的稳健性, 严禁两轨合成 over-identified Hansen J。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Wang, W., & Zhang, Y. (2026). Gradient wild bootstrap for instrumental variable quantile regressions with weak and few clusters. Journal of Business & Economic Statistics, 1-12. https://doi.org/10.1080/07350015.2026.2618311
Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.05658
Nibbering, D., & Oosterveen, M. (2025). Policy-relevant causal effect estimation using instrumental variables with interference. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.12538
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Hoshino, T. (2023). Causal interpretation of linear social interaction models with endogenous networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2308.04276
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Dippel, C., Ferrara, A., & Heblich, S. (2020). Causal mediation analysis in instrumental-variables regressions. The Stata Journal, 20(3), 613-626. https://doi.org/10.1177/1536867X20953572
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. Journal of Human Resources, 50(2), 317-372. https://doi.org/10.3368/jhr.50.2.317
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. Identification and inference for econometric models: Essays in honor of Thomas Rothenberg. https://doi.org/10.1017/CBO9780511614491.006
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
<!-- rendered-citations:end -->
