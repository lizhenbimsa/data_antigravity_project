---
family_id: F364
columns:
- leave_one_out_peer_attention_iv
- leave_one_out_peer_attention_iv_lag1
- leave_one_out_peer_benefit_iv
- leave_one_out_peer_benefit_iv_lag1
- leave_one_out_peer_collab_iv
- leave_one_out_peer_collab_iv_lag1
- leave_one_out_peer_locus_iv
- leave_one_out_peer_locus_iv_lag1
- leave_one_out_peer_subst_iv
- leave_one_out_peer_subst_iv_lag1
unit: 工具变量 (与被工具化内生变量同量纲; 各列分别与 attention_index_full / sub_frac / tech_frac / collab_frac / benefit_mean_full 同量纲)
formula: "LOO(i,t) = (sum_{j in g(i), t, valid} x(j,t) - x(i,t)*1[x(i,t) valid]) / (n_valid(g(i),t) - 1[x(i,t) valid]); 组 g = bank_type x year; 剩余有效同业数 < min_peers(=2) 或组别为 other/缺失 -> NaN; _lag1 = 同银行 LOO(i,t-1) (merge-based 滞后)"
producer: news_process/pipeline/panel/iv_extensions.py::compute_peer_loo_iv (编排入口 compute_iv_extensions, runner 步骤 8z; Stata 标签在 pipeline/panel/export.py)
upstream:
- 40_panel_yearly.parquet (内生列 attention_index_full / sub_frac / tech_frac / collab_frac / benefit_mean_full + 分组列 bank_type / target_bank / year)
citations:
- doi: 10.1016/j.techfore.2026.124581
  type: journal
  authors: Dehghani, M. A., Brauneis, A., & Karavidas, D.
  year: 2026
  title: "Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions"
  venue: Technological Forecasting and Social Change
  vol: 226
  pages_or_artno: "124581"
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
- doi: 10.1016/j.jcorpfin.2025.102772
  type: journal
  authors: Schwenkler, G., & Zheng, H.
  year: 2025
  title: "News-driven peer co-movement in crypto markets"
  venue: Journal of Corporate Finance
  vol: 93
  pages_or_artno: "Article 102772"
- doi: 10.1093/qje/qjaf002
  type: journal
  authors: Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A.
  year: 2025
  title: "The diffusion of new technologies"
  venue: The Quarterly Journal of Economics
  vol: 140
  issue: 2
  pages_or_artno: 1299-1365
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: "Article 103870"
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: 241
  issue: 1
  pages_or_artno: "105727"
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: "FinTech credit and entrepreneurial growth"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3309-3359
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: The Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the Fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: "In search of attention"
  venue: The Journal of Finance
  vol: 66
  issue: 5
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1017/CBO9780511614491.006
  type: book
  authors: Stock, J. H., & Yogo, M.
  year: 2005
  title: "Testing for weak instruments in linear IV regression"
  venue: "Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (Cambridge University Press)"
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
new_dois:
- 10.1111/jofi.12094
---

## CORE

【构念与来源】
本家族是 news_process 面板的同组 leave-one-out (以下简称 LOO) 同业均值工具变量族, 属于 IV 扩展引擎三类构造中的第一类 (另两类为广义 Bartik 移位份额与媒体来源 house-style 暴露, 分属其它列族)。所要解决的核心识别问题是: 银行层面由新闻文本构造的处理变量 (媒体注意力强度、创新报道的实质性占比、技术底层性占比、外部协同占比、经营效益态度) 都是内生的 — 银行自身的经营状况、战略选择与未观测冲击既决定媒体如何报道它, 也直接影响融资成本、金融科技投入、专利产出等结果变量, 直接把处理变量放进结果方程会混入反向因果与遗漏变量偏误。本族的构造思路来自公司金融同行效应文献的经典范式: 用同一分组内其它银行在同一年度该指标的平均值 (剔除焦点银行自身) 作为焦点银行处理变量的工具。直觉上, 同类型同业的媒体曝光与战略叙事会通过模仿、竞争压力与行业风向传导, 推动焦点银行的对应指标同向变动 (相关性, 一阶段), 但同业的取值本身并不直接进入焦点银行的结果方程 (排他性, 需假设并披露)。这一范式的实证源头是 Leary 与 Roberts (2014) 对同行企业财务政策相互影响的研究, 其把同行均值作为工具并系统讨论了该策略的排他性局限; 理论根基则是 Manski (1993) 提出的内生社会效应反射问题 — 同组个体同期互为因果时, 组均值与个体取值在线性模型中不可分离, 任何同行均值工具都必须直面这一批评。构念上, 本族十列覆盖五个内生处理变量, 分别服务五篇论文的识别策略: 注意力 (P2 bank_fintech_attention, 测度谱系承 Hassan 等 (2019) 的公司层文本暴露范式与 Da 等 (2011)、Fang 与 Peress (2009) 的注意力与媒体覆盖文献)、实质性 (P3 bank_fintech_substance)、技术底座 (P4 bank_fintech_locus, 维度框架承 Gomber 等 (2018) 的金融科技创新分类)、外部协同 (P5 bank_fintech_collab, 开放式创新谱系见 Zhang 等 (2024) 的元分析与 Dehghani 等 (2026) 对金融机构开放创新与专利策略的考察)、经营效益态度 (benefit_society 论文)。十列中六列被各论文 paper_spec 的 identification.iv 字段直接收录为主工具或后备工具, 属识别策略承重列。

【方法学与计算】
计算引擎是 iv_extensions.py 中的 compute_peer_loo_iv 通用函数, 输入为银行-年面板 (每个 bank-year 一行), 逐列独立调用。分组维度统一取 bank_type (银行类型: 国有大行、股份制、城商、农商等监管口径分类), 时间维度取自然年, 即同组被定义为「同类型银行 x 同年」。对每个焦点银行 i 在年份 t, 先在组内对内生变量 x 做有效观测聚合: 只有 x 非缺失且组别有效的行进入分子分母; 然后从组总和中减去焦点银行自身的取值 (若自身有效), 从组有效计数中减去一 (若自身有效), 得到剔除自身后的组均值。这一「先聚合再扣自身」的实现与逐组循环在数学上等价, 但对全体银行一次性向量化完成, 且全程强制 float64 算术, 避免可空整型在 groupby 中降型回绕的既知陷阱。缺失语义遵循全仓 IV 族统一口径, 有五条硬规则: 第一, 组别为 other 或缺失的银行不构成真实同业组, 输出 NaN 而非伪零; 第二, 剔除自身后组内剩余有效同业数少于 min_peers (默认 2) 时输出 NaN, 因为单一同业的取值不构成有统计意义的组均值, 且会造成两家银行互为对方工具的镜像对称; 第三, 内生变量自身缺失时该行不进入任何同业的分子分母, 但只要组内其它有效同业足额, 焦点银行自己仍可获得 LOO 值 (自身有效性只影响扣减项); 第四, 输出列与被工具化的内生变量同量纲, 不做任何标准化或缩尾, 量纲变换留给下游回归模板; 第五, 滞后变体 _lag1 通过按银行-年键合并上一年 LOO 值实现 (merge-based, 不依赖面板行序), 面板首年自然缺失。工具变量列名与 paper_spec 的 identification.iv 声明一字不差对应, Stata 导出层为每列配英文标签 (如 Peer LOO Attention IV (type-year)), 下游 2SLS 模板统一按 Stock 与 Yogo (2005) 临界值与 Kleibergen-Paap 秩检验诊断弱工具, 弱工具情形自动追加 Anderson-Rubin 稳健置信区间; 当聚类数少或工具弱时, Wang 与 Zhang (2024) 的 wild bootstrap 弱工具稳健推断是模板层的补充参照。

【计算链路与复现口径】
本族在管线中的落位是 40_panel_export_main 阶段的步骤 8z, 时点在全部面板 merge 完成之后、导出之前, 由编排函数 compute_iv_extensions 按论文逐一调用底层引擎; 引擎属零成本纯后处理 — 只消费面板上既有的聚合列, 不发起任何新的 LLM 或嵌入 API 调用, 因此重跑本族不受离线缓存守卫与付费审批门约束, 也不影响 golden 快照中任何上游列。可复现性口径: 引擎内部只有确定性的 pandas groupby 与向量化算术, 无随机数、无浮点归约顺序依赖 (聚合按组键排序后进行), 在同一上游面板字节下输出逐位可复现; 上游内生列若因 BLAS 浮点或缓存播种差异漂移, 本族随之等量漂移, 属传导而非自身非确定性。运行日志在 8z 步骤开头打出 METHOD banner, 声明本族的方法学口径与三轨禁混约束, 并对每列打出「有效行数 / 面板总行数」的覆盖统计, 审计时以日志为准核对 NaN 结构是否符合上述五条缺失语义。列的消费端有三处: 各论文 paper_spec 的 identification.iv 字段按列名一字不差引用 (机器可读契约, 拼写漂移会被 spec 一致性测试打红); 根级与论文级 2SLS Stata 模板把本族列填入一阶段右侧; codebook 与 Stata 变量标签层从 export.py 的标签字典读取英文短标签。列名语义的一处历史包袱须显式记录: 家族主名不带轨道后缀 (leave_one_out_peer_attention_iv 而非带 _full 后缀), 这与「主名无轨后缀即 full 轨」的全仓约定一致, 是历史命名产物, 不构成 full 轨在方法学上的优先地位 — full 与 ctx/ss 三轨互为稳健性、不分主次。

【识别策略定位】
本族在 11 篇论文识别体系中的定位是「同业维度的外生变异源」, 与其它三条 IV 谱系并列而不重叠: 广义 Bartik 族 (bartik_*_iv) 用基期共现份额乘以组年 LOO 移位, 识别依赖 Goldsmith-Pinkham 等 (2020) 的基期份额外生性视角, 与 Borusyak 等 (2022) 的冲击外生性视角刻意区分 (本仓明确只主张前者); 媒体来源构成族 (outlet_*_iv) 用基期媒体组合乘以媒体 house-style; 地理族 (zone_leave1out_*) 用经济圈分组替代银行类型分组。本族则是最直接的 Manski (1993) - Bramoullé 等 (2009) 谱系: Bramoullé 等 (2009) 证明当网络结构使得「同伴的同伴」不完全重合于「同伴」时, 内生效应与外生效应可分离, 排除性工具可由网络二阶邻居构造; 本仓的银行类型分组是完全组结构 (组内全连接), 恰恰是 Bramoullé 等 (2009) 意义下识别最弱的拓扑, 因此本族从不宣称点识别同行效应本身, 而是退一步只把 LOO 均值当作处理变量的相关外生移位来源, 并强制在论文中披露反射问题与共同冲击风险。近年方法论进展进一步细化了这一定位: Luo 等 (2025) 给出了用工具变量识别与估计因果同行效应的一般框架, Nibbering 与 Oosterveen (2025) 讨论了存在干扰 (interference) 时工具变量估计的政策含义, 两者共同提示 LOO 型工具的估计对象是特定暴露映射下的局部平均处理效应, 论文解释系数时须与之对齐。排他性威胁最实质的一条是共同冲击: 行业层面的监管政策、技术浪潮 (Kalyani 等 (2025) 记录的新技术扩散动态) 或宏观新闻周期会同时抬升同组所有银行的文本指标并直接作用于结果变量, 使工具与误差项相关。缓解手段有三: 回归模板统一吸收年份固定效应 (吸掉全行业共同年冲击, 残余威胁只剩「类型 x 年」层的组内共同冲击); _lag1 滞后变体规避同期反射 (同期组均值与个体同期取值互为因果, 滞后一年打断同期联立); 与 Bartik 族、outlet 族跨谱系互证 (不同外生性来源的工具给出方向一致的估计, 提升可信度)。Grieser 等 (2022) 对公司金融政策网络效应的估计与 Schwenkler 与 Zheng (2025) 对新闻驱动的同伴联动的证据, 都支持「同业新闻暴露传导」这一一阶段机制在经济上是真实存在的。

【与相邻测度的构念区分】
第一, 本族与 lpeer_ 前缀的 ctx/ss 轨镜像列 (lpeer_attention_iv_ctx 等, 属另一家族) 的关系: 本族十列全部基于 full 轨内生变量 (attention_index_full、benefit_mean_full 显式带后缀; sub_frac、tech_frac、collab_frac 无后缀即 full 轨, 属历史命名产物而非「主轨特权」)。ctx 轨 (标题加实体窗口) 与 ss 轨 (银行与金科词同句窗口) 的同名 LOO 工具以紧凑前缀 lpeer_ 另行物化, 三轨互为稳健性、不分主次, 各自 just-identified 并排进各自的 2SLS; 铁律是严禁把 full/ctx/ss 任意两轨的 LOO 工具拼进同一个 over-identified 方程做 Hansen J — 三轨源自同一批文章的三种文本窗口, 共同冲击同源同污染, 过度识别检验在此设定下零功效, 通过了也不构成排他性证据。第二, 与 zone_leave1out_benefit_iv 的区分: 后者同引擎但分组维度换成 bank_zone (经济圈), 是分组判据敏感性臂, 与本族 bank_type 分组各自 just-identified 并排, 同样禁混 Hansen J。第三, 与 bartik_*_iv 的区分: Bartik 族的移位部分虽然也是组年 LOO 均值, 但乘上了基期冻结份额, 识别论证依赖份额外生性而非同业均值排他性, 两族是不同识别假设下的独立工具, 跨族互证是设计意图, 但合并进同一方程做过度识别检验时必须逐篇论证两套排他性假设可同时成立。第四, 与 llm_peer_tone_iv、emb_peer_tone 系 W 矩阵溢出列的区分: 那些列的「同行」由 LLM 识别的竞争对手集合或嵌入相似度矩阵定义, 是连续加权网络; 本族的同行是离散监管类型分组, 构念上一个是「市场感知的竞争邻居」, 一个是「监管同类」, 不可互换解释。第五, 内生变量自身的口径约束向上传导: 五个内生列全部继承 stage 21 的 full-only 留篇门控 (2026-06-29 口径, 一篇文章是否计入银行金科报道宇宙只看 full 轨 LLM 验证), 因此本族工具的有效样本结构也随 full 轨门控收缩, 这是设计内行为而非缺陷。

【已知局限与稳健性梯子】
局限一, 排他性不可检验且先天承压: 同业均值工具的排他性在 Leary 与 Roberts (2014) 原文中已被作者本人明确标注为局限, 本仓所有消费论文必须如实披露「同业指标可能经由共同需求冲击直接进入结果方程」的风险, 勿过度宣称。局限二, 完全组结构下反射问题无法根除: 年份固定效应加滞后只是缓解, 不是 Bramoullé 等 (2009) 意义的拓扑识别; 若审稿人要求, 跨谱系工具 (Bartik、outlet) 是指定的替代识别路径。局限三, 弱工具风险随组规模波动: 类型分组组数少 (约六类), 组内银行数不均, 小组年格上剩余同业可能刚过 min_peers 门槛, 一阶段 F 值须逐表报告, 低于 Stock 与 Yogo (2005) 临界值时切换 Anderson-Rubin 推断或 Wang 与 Zhang (2024) 型 bootstrap。局限四, T=2 开发样本退化: 当前磁盘面板仅 2017-2018 两年, _lag1 变体只有 2018 年有值, 组年格稀薄导致 NaN 占比偏高, 这是试跑窗口的机械后果, 全量语料 (2007-2024, T=18) 下自然恢复, 审计时禁用 T=2 表现推断生产行为。局限五, 测量误差传导: 内生变量本身是 LLM 分类或嵌入投影的文本测度 (Gentzkow 等 (2019) 意义下的 text-as-data 生成变量), 其测量误差会同时进入工具 (同业均值) 与处理变量, 经典衰减偏误的方向分析在生成回归变量设定下更复杂, 论文须在稳健性节讨论。稳健性梯子的完整形态: 轨道维度 full/lpeer_ctx/lpeer_ss 三臂, 分组判据维度 bank_type/bank_zone 两臂, 时点维度当期/滞后一期两臂, 工具谱系维度 LOO/Bartik/outlet 三族 — 全部遵循「各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J」的全仓铁律; 运行日志在 8z 步骤打出的 METHOD banner 亦复述此约束。局限六, 组构成随年份漂移: 样本银行的进入退出与类型归属调整会改变各组年格的同业集合, LOO 均值的年际变动因此混入组构成效应与真实叙事变动两种来源; 由于分组判据是缓慢变动的监管分类, 该问题在本设定下二阶, 但涉及城商行农商行合并重组密集年份时论文须做剔除重组银行的敏感性。局限七, 留篇门控的样本选择传导: 内生变量的分母随 full-only 门控收缩, 若门控通过率与银行类型相关 (大行报道更易通过验证), 则组均值的测量精度在类型间不均, 属异方差性质的测量问题而非偏误来源, 聚类稳健推断可覆盖, 但报告一阶段时宜按类型分组披露有效观测的分布。局限八, 分组维度与固定效应的共线约束须预分析确认: 本族分组维度 bank_type 与回归常配的类型固定效应在组间水平上完全共线, 一旦模型纳入类型固定效应, 工具的识别变异被压缩到「类型 x 年」交互层, 组间的长期水平差异被固定效应吸收殆尽, 剩余的一阶段解释力全部来自同组内跨年的相对波动。这一约束在两年开发窗口上尤为致命 (T=2 时类型 x 年格几乎无跨年变异可用), 生产 T=18 语料下每个类型有十八年的组年序列, 交互层变异才充分。因此论文预分析阶段必须报告纳入与不纳入类型固定效应两种设定下的一阶段偏 R 方与 Kleibergen-Paap F, 若类型固定效应下工具塌陷, 则须显式声明识别依赖组间水平差异这一较强假设, 或改以年份固定效应加类型层聚类的较弱设定, 并在稳健性节交代两种设定的系数异同。

【文献定位】
本族的文献坐标系由三层构成。方法层: Manski (1993) 反射问题奠定同行效应识别的批评基准; Bramoullé 等 (2009) 给出网络拓扑识别条件; Leary 与 Roberts (2014) 是同行均值工具在公司金融的落地范式与排他性诚实披露的先例; Goldsmith-Pinkham 等 (2020) 与 Borusyak 等 (2022) 界定了相邻 Bartik 族的两种外生性视角, 本族借其框架厘清自身不同的识别依赖; Stock 与 Yogo (2005) 与 Wang 与 Zhang (2024) 提供弱工具诊断与稳健推断工具箱; Luo 等 (2025) 与 Nibbering 与 Oosterveen (2025) 代表同行效应 IV 识别的前沿刻画。测度层: Hassan 等 (2019) 确立公司层文本暴露测度范式, Da 等 (2011) 与 Fang 与 Peress (2009) 确立注意力与媒体覆盖对金融结果的实证意义, Cookson 等 (2024) 把媒体信号的信息含量推进到社交媒体时代, Qin 等 (2018) 提供中国媒体市场结构与报道偏差的制度背景 — 这对以中文银行新闻为语料的本仓尤为关键, 因为中国媒体的党媒/市场化分层意味着「同类型银行被报道的方式」有系统性的媒体端成分, 恰是同业暴露传导的现实通道。应用层: Chen 等 (2019) 与 Hau 等 (2024) 代表金融科技创新价值与信贷增长的因果证据谱系, Gomber 等 (2018) 提供 locus 维度的概念框架, Zhang 等 (2024) 与 Dehghani 等 (2026) 支撑 collab 维度的开放式创新构念, Kalyani 等 (2025) 的技术扩散测度与 Grieser 等 (2022)、Schwenkler 与 Zheng (2025) 的同伴联动证据共同支撑「同业文本指标存在真实传导」的一阶段经济机制。本族十列即处在这三层文献的交点上: 用方法层的工具化策略, 处理测度层生成的文本变量, 服务应用层的因果问题。

## VAR: leave_one_out_peer_attention_iv

【变体差分】
本列是家族 canonical 形态在注意力维度的实例, tier=core, 被 P2 论文 bank_fintech_attention 的 paper_spec identification.iv 收录为识别策略主工具。被工具化的内生变量是 attention_index_full — full 轨 (标题 prepend 加全文正文) 口径下的银行金融科技媒体注意力指数, 谱系上承 Hassan 等 (2019) 的公司层文本暴露测度与 Da 等 (2011) 的投资者注意力文献。构造为: 对焦点银行 i 在年份 t, 取同一 bank_type 类型内其它银行同年 attention_index_full 的算术均值 (剔除 i 自身), 剩余有效同业数不足 2 或类型为 other/缺失时置 NaN。Stata 标签 Peer LOO Attention IV (type-year) 中的 type-year 明示分组粒度。一阶段逻辑: 同类型同业被金融科技议题高强度报道时, 媒体议程与行业叙事会外溢到焦点银行 (Fang 与 Peress (2009) 与 Cookson 等 (2024) 意义下的媒体覆盖与信号传导), 且同类型银行面对相似的监管叙事窗口 (Qin 等 (2018) 的中国媒体结构背景), 故同业注意力对焦点银行注意力有正向预测力; 排他性主张: 同业被报道的强度不直接进入焦点银行的金融科技投资方程, 只经由焦点银行自身的注意力暴露渠道起作用 — 这一主张承 Leary 与 Roberts (2014) 的同行均值范式, 其共同冲击风险 (行业性金科政策同时驱动同业报道与焦点银行投资) 由年份固定效应与滞后变体缓解, 并须在论文中如实披露。与家族内其它列的差分: 维度上属注意力构念 (强度型连续指标, 与占比型的 subst/locus/collab 和态度型的 benefit 量纲性质不同); 时点上是当期值, 与 _lag1 滞后臂并排互为稳健性。与族外近邻的差分: 同论文的 bartik_attention_iv 用基期共现份额乘组年 LOO 金科强度, 识别依赖不同 (份额外生性 vs 同业均值排他性), 两者是 P2 的 primary/fallback 双工具, 各自 just-identified 进各自 2SLS, 合并做过度识别检验须双假设联合论证; ctx/ss 轨镜像 lpeer_attention_iv_ctx/_ss 属另一家族, 三轨并排禁混同一 Hansen J。本列在 T=2 开发面板上有效率受组年格稀薄限制, 生产 T=18 下恢复; 弱工具诊断按 Stock 与 Yogo (2005) 临界值执行。使用注意事项有三。其一, 内生变量 attention_index_full 的分母结构继承 full-only 留篇门控, 一篇报道是否计入注意力宇宙由 full 轨验证决定, 因此本工具的组均值也定义在该门控后的报道集上, 与门控前口径的任何注意力代理 (如原始报道计数) 不可直接换算。其二, 注意力是强度型指标, 组内分布右偏 — 头部银行的曝光量远超同组中位数, LOO 均值对是否剔除自身高度敏感, 这正是必须用 LOO 而非裸组均值的原因: 焦点银行自身的极端取值若留在均值内会机械制造相关性, 使一阶段虚高而工具实质内生。其三, 论文使用本列时年份固定效应是底线配置, 建议同时报告类型固定效应下的组内变异是否仍足以支撑一阶段 — 类型与工具的组维度重合, 类型固定效应会吸掉组间水平差异, 工具的识别变异只剩组年交互部分, 这一点在预分析时须用一阶段偏 R 方确认。补充一点计量口径: 本列作为 P2 主工具进入 2SLS 时, 一阶段被工具化的是焦点银行的 attention_index_full, 结果方程的 outcome 为 ln_fintech_investment 类真实投入哨兵列, 故本列的经济解释是「由同类型同业媒体注意力外生驱动的那部分焦点银行注意力」对金融科技投入的因果弹性, 而非注意力与投入的总相关; 报告时须并列 OLS 与 2SLS 系数以观察内生性偏误的方向与量级, 并按 Da 等 (2011) 的注意力度量传统披露注意力代理构造的敏感性, 按 Fang 与 Peress (2009) 的媒体覆盖传统披露覆盖度量口径的替代。

## VAR: leave_one_out_peer_attention_iv_lag1

【变体差分】
本列 tier=standard, 是 leave_one_out_peer_attention_iv 的滞后一期派生臂: 取同一银行上一年度的 LOO 同业注意力均值, 即 LOO(i,t-1)。实现为 merge-based 滞后 — 把 LOO 列按银行-年键整体前移一年后合并回面板, 不依赖行序, 面板首年自然 NaN。设立动机是缓解 Manski (1993) 同期反射: 当期组均值与焦点银行当期取值在线性模型中互为因果不可分离, 而 t-1 年的同业注意力在时间上先于焦点银行 t 年的取值, 打断了同期联立; 代价是引入「同业指标序列相关时滞后值仍携带共同冲击」的残余风险, 以及一阶段强度通常弱于当期臂 (注意力的年际持续性决定滞后相关性), 故弱工具诊断在本臂上更须严格执行。与当期臂的关系是互为稳健性、不分主次: 两臂各自 just-identified 进各自的 2SLS 规格并排报告, 禁把当期与滞后工具拼进同一 over-identified 方程做 Hansen J — 两者共享同一同业分组与同一文本测度来源, 共同冲击同源, 过度识别检验无实质功效。T=2 开发面板上本列仅 2018 年有值 (2017 为面板首年无滞后源), 全量 T=18 语料下自然恢复; 该退化是滞后构造的机械后果, 不是缺陷。补一点使用口径: 因本列继承当期臂的同业分组与 full 轨测度, 其排他性威胁与当期臂同源, 论文把它当独立稳健性规格并排报告即可, 无需为它单列一套排他性论证; 但一阶段 F 必须单独报告, 不可沿用当期臂数值, 因为滞后自相关会使两臂的工具强度显著不同。

## VAR: leave_one_out_peer_benefit_iv

【变体差分】
本列 tier=core, 是 benefit_society 论文 paper_spec identification.iv 收录的识别策略主工具。被工具化的内生变量是 benefit_mean_full — full 轨口径下银行新闻的经营效益态度均值, 由嵌入投影维度分析产出 (文章文本向经营效益构念方向向量投影后按银行-年聚合), 属 Gentzkow 等 (2019) 意义下的生成型文本变量。构造与家族 canonical 完全一致: bank_type x year 组内剔除自身的算术均值, min_peers=2, 伪组与不足额组置 NaN, Stata 标签 Peer LOO Benefit-Attitude IV。一阶段逻辑: 同类型同业在媒体叙事中被赋予的经营效益态度反映了该类型银行群体面对的共同舆论气候与商业模式评价基调, 会传导为焦点银行被报道时的态度基线; 排他性主张: 同业的被报道态度不直接影响焦点银行的经营绩效结果 (该论文 outcome 为 roa 类财务哨兵列), 只经焦点银行自身的媒体态度渠道作用。本列的差分要点有三。其一, 它是家族内唯一拥有「分组判据敏感性孪生」的维度: 同一内生变量 benefit_mean_full 另配 zone_leave1out_benefit_iv (bank_zone 经济圈分组, 无滞后变体), 类型分组与地理分组两臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 Hansen J — 类型分组捕捉监管同类的叙事传导, 地理分组捕捉区域媒体市场的叙事传导, 两者排他性威胁的来源不同 (行业政策 vs 区域经济冲击), 并排一致才构成强证据。其二, 内生变量是嵌入投影测度, 其上游嵌入列遵循 co-primary 双轨口径 (canonical Qwen 槽与 _lg 槽严格 parity), 但本 IV 列只消费聚合后的 canonical 面板列, 不存在 _lg 孪生, 这是设计内行为 — IV 引擎消费的是面板级聚合值而非嵌入原始列。其三, 与同论文的 zone 族及其它维度 LOO 列一样, 态度型指标的组均值对组内极端报道敏感, 小组年格上单篇极端文章可经同业均值传入工具, 论文稳健性节须报告缩尾敏感性。共同冲击披露义务同族 (Leary 与 Roberts (2014) 先例), 弱工具诊断同族 (Stock 与 Yogo (2005))。另有两点使用注意。第一, 态度均值是有向连续指标而非占比, 取值可正可负, 组均值的符号本身携带信息 (该类型银行群体当年被媒体正面还是负面评价), 解释一阶段系数时应同时报告工具的组间与组内分布, 避免把水平差异误读为传导强度。第二, benefit 维度的结果变量是财务绩效哨兵列, 在财务面板接入前该论文的 2SLS 只能在模板层演练, 本工具列的实证承重要到外部财务数据合入后才真正兑现; 这不影响列本身的定义与生产 — 引擎不依赖结果变量, 面板每次重跑都会物化本列, 复现包中模板与列同时就位, 属「先备好识别策略、后接结果数据」的设计意图。加之态度测度经嵌入投影生成, 上游嵌入的任何受控换模都会传导为本列数值漂移, 换模后须整体重估一阶段强度而不能沿用旧 F 值。末一点须强调本列在分组判据敏感性中的枢纽地位: benefit 维度是家族内唯一同时铺开 bank_type 与 bank_zone 两套分组的维度, 因此它承担了检验「同业传导究竟沿监管同类还是沿区域市场发生」这一识别机制归因的实证责任; 若两套分组给出方向相反或量级悬殊的一阶段, 则提示存在未被年份固定效应吸收的分组特异共同冲击, 论文须回到构念层重新论证排他性, 而非机械并排两个系数了事。

## VAR: leave_one_out_peer_benefit_iv_lag1

【变体差分】
本列 tier=standard, 是 leave_one_out_peer_benefit_iv 的滞后一期派生臂, 取同银行上一年的类型组 LOO 经营效益态度均值, merge-based 构造, 面板首年 NaN。动机与家族其它滞后臂一致: 打断 Manski (1993) 同期反射, 让工具在时间上先于处理变量。对态度型指标而言滞后臂另有一层含义 — 媒体态度气候的年际持续性弱于注意力强度的持续性 (态度随新闻周期与政策叙事快速翻转), 因此本臂的一阶段强度对语料年份覆盖更敏感, 弱工具情形下模板自动追加 Anderson-Rubin 稳健区间, 少聚类设定可参照 Wang 与 Zhang (2024) 的 bootstrap 推断。注意本列与 zone_leave1out_benefit_iv 没有滞后对应 (zone 族刻意不产 _lag1), 因此「分组判据 x 时点」矩阵在 benefit 维度是不满秩的三臂而非四臂, 属设计内取舍。补充口径: 态度均值的滞后传导在经济上对应「上一年度同类型银行群体的舆论评价气候塑造本年焦点银行被报道时的态度基线」这一慢变量渠道; 由于 benefit 维度的结果变量是 roa 类财务哨兵列, 本滞后臂在财务面板接入前只能在模板层演练, 与当期臂一样属「先备好识别策略、后接结果数据」的设计, 引擎不依赖结果变量, 面板每次重跑都会物化本列。上游嵌入受控换模会传导为本列数值漂移, 换模后须整体重估一阶段强度, 不可沿用旧 F 值。与当期臂互为稳健性、不分主次, 各自 just-identified 并排, 禁与当期臂或任何同源轨道工具拼进同一 over-identified Hansen J。T=2 面板上仅 2018 年有值, 生产 T=18 恢复。

## VAR: leave_one_out_peer_collab_iv

【变体差分】
本列 tier=core, 是 P5 论文 bank_fintech_collab 的 paper_spec identification.iv 主工具。被工具化的内生变量是 collab_frac — 无后缀即 full 轨 (历史命名产物, 非主轨特权) 的外部协同占比: 焦点银行当年被 LLM 判为「外部协同」的金融科技创新报道占其有效分类报道的比例, 维度框架承 Chesbrough 开放式创新谱系, 其构念效度由 Zhang 等 (2024) 的开放式创新二十年元分析与 Dehghani 等 (2026) 对金融机构开放创新实践的考察支撑。分类共识列继承 stage 21 的 verified 门控与 full-only 留篇口径 (2026-06-29), 分母为验证通过的分类报道数。构造为 bank_type x year 组内剔除自身的 collab_frac 均值, Stata 标签 Peer LOO Collab IV。一阶段逻辑: 开放式创新具有显著的同业示范效应 — 同类型银行密集开展外部合作 (与金科公司联合、投资、共建) 并被媒体报道时, 焦点银行面临跟进压力且媒体也更倾向以协同框架报道该类型银行 (Grieser 等 (2022) 意义下的网络效应传导), 故同业协同叙事占比预测焦点银行的协同占比; 排他性主张: 同业的协同报道占比不直接进入焦点银行的并购结果方程 (P5 outcome 为 m_and_a_fintech 哨兵列), 只经焦点银行自身的协同叙事渠道作用, 共同冲击风险 (行业性开放合作政策同时驱动两端) 照例披露并由年份固定效应与滞后臂缓解。差分要点: 其一, 占比型内生变量取值域在零一之间, LOO 均值同域, 系数解释为「同业协同占比每上升一个百分点经由焦点银行协同占比传导的效应」; 其二, LLM 分类的测量误差在本维度经 per-model 稳健性梯子另行处理 (三厂商各自的 collab_frac 子测度属 LLM 分类 per-model 族, 与本 IV 列正交, IV 引擎只消费共识列), 分类维度的跨厂商稳健与本族的同业工具化是两条不交叉的梯子; 其三, 同论文另有 bartik_collab_iv_full/_ctx 双轨 Bartik 工具作 fallback, 跨谱系互证, 各自 just-identified, 禁混 Hansen J。与 lpeer_collab_iv_ctx/_ss (ctx 轨消费 collab_frac_cm, ss 轨消费 collab_frac_cm_ss) 的三轨并排关系同族铁律。弱工具与 T=2 退化披露同族。补充数点使本列可独立审阅。其一, 计量落位: 本列作为 P5 主工具进入 2SLS, 一阶段被工具化 collab_frac, 结果方程 outcome 为 m_and_a_fintech 类并购哨兵列, 故系数解释为「由同类型同业协同叙事外生驱动的那部分焦点银行协同占比」对金融科技并购的因果效应, 报告须并列 OLS 与 2SLS 以显内生性偏误方向。其二, 占比型工具的边界行为: collab_frac 定义在有效分类报道分母上, 当焦点银行某年金科分类报道极少 (分母小) 时占比方差机械放大, 但经同业均值传入本工具后噪声被稀释 (LOO 是同业跨行平均, 对焦点银行自身小分母噪声不敏感), 这是用同业工具而非焦点银行滞后自值的一层额外好处。其三, 与开放式创新构念的对齐: Zhang 等 (2024) 的元分析界定了开放式创新的前因与后果测度谱系, Dehghani 等 (2026) 记录了金融机构以专利与开放合作并举的实践, 本列的一阶段机制 (同业协同示范推动焦点银行协同叙事) 正落在该谱系「外部知识搜寻的同业扩散」一支上。其四, 三轨与跨谱系的并排矩阵: 本列 (full) 与 lpeer_collab_iv_ctx、lpeer_collab_iv_ss 构成轨道三臂, 与 bartik_collab_iv_full、bartik_collab_iv_ctx 构成谱系互证, 与 _lag1 构成时点双臂, 全部各自 just-identified 并排, 禁任意两者拼进同一 over-identified Hansen J — 三轨同源文本窗口、双时点同源分组, 过度识别检验在这些设定下零功效, 通过与否都不携带排他性信息。

## VAR: leave_one_out_peer_collab_iv_lag1

【变体差分】
本列 tier=standard, 是 leave_one_out_peer_collab_iv 的滞后一期派生臂: 同银行上一年的类型组 LOO 外部协同占比, merge-based 滞后, 面板首年 NaN。反射缓解逻辑同族 (Manski (1993)); 对协同维度而言滞后臂还有一层经济含义 — 开放式创新的同业示范到跟进存在天然时滞 (观察同业合作成效、谈判、落地均需时间), 因此 t-1 年同业协同叙事对焦点银行 t 年协同行为的传导在机制上比当期臂更贴近「示范-模仿」的时间结构, 部分论文规格把滞后臂作为机制一致性检查而非单纯稳健臂使用; 但代价同样是序列相关的共同冲击残余与一阶段强度衰减, Stock 与 Yogo (2005) 诊断照例执行。与当期臂互为稳健性、不分主次, 各自 just-identified 并排, 禁拼同一 over-identified Hansen J (同源同业分组、同源文本测度, 过度识别零功效)。T=2 面板仅 2018 年有值, 生产 T=18 恢复; 占比型指标在小组年格上的 LOO 均值方差偏大, 滞后臂继承该噪声。补充口径: 因开放式创新的示范到跟进存在观察成效、谈判、落地的天然时滞, 本滞后臂在部分 P5 规格中被当作机制一致性检查而非单纯稳健臂 — 若「t-1 年同业协同叙事 → t 年焦点银行协同行为」的传导显著, 则正面支持示范-模仿的时间结构假设。但这一用法不改变它与当期臂互为稳健性、不分主次的定位: 两臂各自 just-identified 并排, 禁与当期臂或 Bartik 族拼进同一 over-identified Hansen J; 一阶段 F 须单独报告, 不可沿用当期臂数值。

## VAR: leave_one_out_peer_locus_iv

【变体差分】
本列 tier=core, 是 P4 论文 bank_fintech_locus 的 paper_spec identification.iv 主工具。被工具化的内生变量是 tech_frac — 无后缀即 full 轨的技术底座占比: 焦点银行当年被 LLM 判为「底层技术」(区别于「应用场景」) 的金融科技创新报道占其有效分类报道的比例, 维度框架承 Gomber 等 (2018) 对金融科技创新力量的分类学 — 底层技术 (基础设施、算法、数据能力) 与应用场景 (渠道、产品、获客) 是创新位阶 (locus) 的两极, 其经济后果差异是 P4 的核心问题 (outcome 为 citation_weighted_patent 哨兵列, 底层技术叙事应更强预测高质量专利产出, 谱系上呼应 Chen 等 (2019) 对金融科技创新价值的度量与 Kalyani 等 (2025) 对新技术扩散的公司层证据)。构造为 bank_type x year 组内剔除自身的 tech_frac 均值, min_peers=2, Stata 标签 Peer LOO Locus(Tech) IV。一阶段逻辑: 技术路线选择有强烈的同业锚定 — 同类型银行集体转向底层技术叙事 (如大行群体投入分布式核心、隐私计算) 时, 焦点银行的技术议程与媒体对其的报道框架都会被带动, 类型内共享的科技监管窗口 (监管沙盒、信创要求) 放大了这一传导; 排他性主张: 同业的技术叙事占比不直接进入焦点银行的专利产出方程, 只经焦点银行自身技术叙事渠道作用。本列的特殊差分在于: P4 是家族内唯一把当期臂与滞后臂同时收进 identification.iv 主口径的论文 (leave_one_out_peer_locus_iv_lag1 亦为 tier=core), 因为专利产出这一 outcome 从研发决策到申请授权的滞后结构长, 当期工具与滞后工具对应结果方程的两种时间对齐假设, spec 层面 primary/fallback 全收以保证复现包完整 — 但两臂仍各自 just-identified 并排, 禁混同一 Hansen J。其余差分同族: 与 lpeer_locus_iv_ctx (消费 tech_frac_lc) 与 lpeer_locus_iv_ss (消费 tech_frac_ls) 三轨并排; 分类共识列继承 verified 门控与 full-only 留篇口径; LLM per-model 梯子 (三厂商 tech_frac 子测度) 与本族正交不交叉; 弱工具诊断与 T=2 退化披露同族。注意 P4 没有对应的 Bartik 工具 (编排注释明示 locus 维度只配 LOO 族), 跨谱系互证在本维度不可用, 论文稳健性叙事须改以三轨与双时点臂支撑。补充数点。其一, 计量落位: 本列作为 P4 主工具, 一阶段工具化 tech_frac, 结果方程 outcome 为 citation_weighted_patent 引用加权专利哨兵列, 系数解释为「由同类型同业技术底座叙事外生驱动的那部分焦点银行技术占比」对高质量专利产出的因果效应; 因专利产出滞后长, P4 特意把当期与滞后两臂同收主口径 (见下一列)。其二, locus 二分的构念根基: Gomber 等 (2018) 把金融科技创新按创新位阶分为底层技术与应用场景两极, 本列工具化的正是这一位阶的底层技术端占比, 其经济后果假设 (底层技术叙事更强预测可专利化的技术积累) 呼应 Chen 等 (2019) 对金科创新价值的度量与 Kalyani 等 (2025) 对公司层新技术扩散的证据。其三, 本维度无 Bartik 孪生: 编排明示 locus 只配 LOO 族而不产 bartik_locus_iv, 故稳健性叙事的替代识别路径退回三轨 (full 与 lpeer_locus_iv_ctx、lpeer_locus_iv_ss) 与双时点 (当期与滞后) 两个维度并排, 全部各自 just-identified, 禁混同一 over-identified Hansen J。其四, 占比型小组年格噪声与弱工具诊断 (Stock 与 Yogo (2005)、必要时 Anderson-Rubin 与 Wang 与 Zhang (2024) 型 bootstrap) 与 T=2 退化披露同族。其五, 内生变量 tech_frac 的分类维度另有 per-model 稳健性梯子 (三厂商各自的 tech_frac 子测度), 与本 IV 列正交不交叉, IV 引擎只消费共识清票后的技术占比, 不消费任何单厂商裸测度, 两条梯子互不干扰。

## VAR: leave_one_out_peer_locus_iv_lag1

【变体差分】
本列 tier=core — 家族四个滞后臂中唯一的 core 列, 因为 P4 论文的 paper_spec identification.iv 把它与当期臂一并收录为主口径工具 (primary/fallback 全收), 而非仅作稳健性附件。构造上与其它滞后臂完全同构: 取同银行上一年的 bank_type 组 LOO 技术底座占比, 即 LOO(i,t-1), merge-based 按银行-年键合并, 不依赖行序, 面板首年自然 NaN。它在 P4 识别策略中被抬升为主口径的原因在于 outcome 的时间结构: 引用加权专利产出 (citation_weighted_patent 哨兵列) 从技术决策、研发投入到专利申请与授权存在一到数年的滞后, 用 t-1 年的同业技术叙事工具化焦点银行的技术叙事、再看 t 年及之后的专利结果, 在时间序上比当期工具更贴合「同业示范先行、焦点银行跟进、产出滞后显现」的机制链条; 同时滞后一期也正面回应 Manski (1993) 同期反射 — t-1 年的同业组均值不可能由焦点银行 t 年的取值反向决定, 联立性在构造层面被打断。方法论上仍须诚实披露两条残余威胁: 其一, 技术叙事具有年际持续性, 若类型层共同冲击 (如信创政策) 本身序列相关, 滞后工具仍携带该冲击, 年份固定效应只能吸收全行业共同部分, 类型 x 年层的残余须依赖跨轨与跨判据并排互证; 其二, 滞后臂的一阶段强度系于 tech_frac 的自相关与同业传导时滞, 弱于当期臂时须报告 Kleibergen-Paap F 并按 Stock 与 Yogo (2005) 临界值判定, 不足则切换 Anderson-Rubin 推断。与当期臂 leave_one_out_peer_locus_iv 的关系是互为稳健性、不分主次的双时点并排: 两臂各自 just-identified 进各自 2SLS 规格, 铁律禁止把当期与滞后工具拼进同一 over-identified 方程做 Hansen J — 两者共享同一分组、同一文本测度与同源共同冲击, 过度识别检验通过与否都不携带排他性信息。T=2 开发面板上本列仅 2018 年一格有值, 组年格稀薄时 NaN 占比高, 属滞后构造在两年窗口上的机械退化, 全量 T=18 语料自然恢复; 论文报告时须给出本臂的一阶段有效 N。与 lpeer_ 前缀 ctx/ss 轨的滞后镜像 (lpeer_locus_iv_ctx_lag1 等) 三轨并排、禁混 Hansen J 的口径同族铁律。补充数点使本列与当期臂的分工可独立审阅。其一, 主口径抬升的复现含义: 因本列被 paper_spec identification.iv 明列为主口径工具而非稳健性附件, 复现包在 instantiate 阶段会为其单独生成 2SLS 模板槽位, spec 一致性测试按列名一字不差核对, 拼写漂移即打红。其二, 时间对齐的方法论权衡: 用 t-1 年同业技术叙事工具化焦点银行 t 年技术叙事, 再观察 t 及之后的专利结果, 与引用加权专利的长滞后产出结构对齐, 但也意味着有效样本进一步收缩 (需 t-1 组年格与 t 焦点行同时有值), 一阶段有效 N 通常小于当期臂, 报告时须并列两臂的 N 与 F。其三, 残余共同冲击: 信创、监管沙盒等类型层技术政策若序列相关, t-1 工具仍携带该冲击, 年份固定效应只吸全行业共同部分, 类型 x 年残余靠跨轨 (full/ctx/ss) 与跨时点并排互证。其四, 与当期臂互为稳健性不分主次, 全部各自 just-identified, 禁混同一 over-identified Hansen J。其五, 本列虽为滞后派生, 但因被 spec 主口径收录, codebook 与 Stata 标签层须与当期臂平级维护, 不得当作次级附属列省略标签或从复现清单剔除, 这是 P4 唯一把滞后臂提到主口径的设计后果。

## VAR: leave_one_out_peer_subst_iv

【变体差分】
本列 tier=core, 是 P3 论文 bank_fintech_substance 的 paper_spec identification.iv 主工具。被工具化的内生变量是 sub_frac — 无后缀即 full 轨的实质性占比: 焦点银行当年被 LLM 判为「实质性」(区别于「象征性」) 的金融科技创新报道占其有效分类报道的比例, 构念承创新管理文献中实质性创新与象征性创新 (贴标签、蹭热点、政策迎合) 的二分, P3 检验实质性叙事对成本收入比变化 (cost_income_ratio_change_3yr 哨兵列) 的因果效应 — 真金白银的技术投入应在中期改善经营效率, 而象征性叙事不应。构造为 bank_type x year 组内剔除自身的 sub_frac 均值, min_peers=2, 伪组置 NaN, Stata 标签 Peer LOO Substantive IV。一阶段逻辑: 实质性与象征性的叙事基调在类型内传染 — 当同类型同业普遍以实打实的系统上线、专利、投产被报道时, 行业评价标准水涨船高, 焦点银行的象征性动作更难获得媒体背书, 其报道结构被推向实质性一端; 反之在概念炒作周期 (Chen 等 (2019) 记录的金科创新估值热潮背景) 同业的象征性叙事也会拉低焦点银行叙事的实质性含量。排他性主张: 同业报道的实质性占比不直接进入焦点银行的成本效率方程, 只经焦点银行自身叙事渠道作用; 共同冲击风险 (行业性技术投资周期同时驱动同业叙事与焦点银行效率) 照例披露, 由年份固定效应、滞后臂与跨谱系 Bartik 工具 (bartik_subst_iv_full/_ctx, 以实质性等于一、象征性等于零的映射构造移位) 三重缓解。差分要点: 其一, sub_frac 的分类分母继承 verified 门控与 full-only 留篇口径, 且实质性判定是 LLM 输出经共识清票后的结果, 非裸多数票; 其二, per-model 梯子 (三厂商各自 sub_frac 子测度) 与本族正交, IV 引擎只消费共识列; 其三, 与 lpeer_subst_iv_ctx (消费 sub_frac_sc) 与 lpeer_subst_iv_ss (消费 sub_frac_ss) 三轨并排, 与 Bartik 族跨谱系并证, 全部各自 just-identified, 禁混同一 Hansen J。占比型指标的小组年格噪声、弱工具诊断 (Stock 与 Yogo (2005)) 与 T=2 退化披露同族。补充数点。其一, 计量落位: 本列作为 P3 主工具, 一阶段工具化 sub_frac, 结果方程 outcome 为 cost_income_ratio_change_3yr 三年成本收入比变化哨兵列, 系数解释为「由同类型同业实质性叙事外生驱动的那部分焦点银行实质性占比」对中期经营效率改善的因果效应; 真金白银的技术投入应在中期压降成本收入比, 象征性叙事不应, 这一非对称是 P3 的识别落点。其二, 实质性与象征性二分的构念根基: 该二分承创新管理文献对实质性创新与象征性 (贴标签、蹭热点、政策迎合) 创新的区分, LLM 判定经共识清票而非裸多数票, 分母为 verified 门控通过的有效分类报道数, 继承 full-only 留篇口径。其三, 三重缓解的完整形态: 共同冲击 (行业技术投资周期同时驱动同业叙事与焦点银行效率) 由年份固定效应、滞后臂 (打断同期反射) 与跨谱系 Bartik 工具 (bartik_subst_iv_full、bartik_subst_iv_ctx, 以实质性映射为一、象征性为零构造移位) 三路并行缓解。其四, 三轨与跨谱系并排矩阵: 本列 (full) 与 lpeer_subst_iv_ctx (消费 sub_frac_sc)、lpeer_subst_iv_ss (消费 sub_frac_ss) 三轨, 与 Bartik 族跨谱系, 与 _lag1 双时点, 全部各自 just-identified 并排, 禁任意两者拼进同一 over-identified Hansen J。其五, sub_frac 的分类维度同样另配 per-model 稳健性梯子 (三厂商各自的 sub_frac 子测度), 与本 IV 列正交, IV 引擎只消费共识列, 分类跨厂商稳健与同业工具化是两条不交叉的梯子。

## VAR: leave_one_out_peer_subst_iv_lag1

【变体差分】
本列 tier=standard, 是 leave_one_out_peer_subst_iv 的滞后一期派生臂: 同银行上一年的类型组 LOO 实质性占比, merge-based 滞后, 面板首年 NaN。反射缓解与时间先序逻辑同族 (Manski (1993)); 对实质性维度而言, 滞后臂与 P3 outcome 的三年变化窗口 (cost_income_ratio_change_3yr) 天然形成「t-1 年同业叙事、t 年焦点银行叙事、t 到 t+3 年效率变化」的时间梯队, 比当期臂更不易受结果窗口内共同冲击的同期污染, 这是它在 P3 稳健性规格中的主要价值。代价同族: 叙事基调的年际翻转 (炒作周期切换) 会削弱滞后相关性, 一阶段 F 须逐表报告, 弱工具时按 Stock 与 Yogo (2005) 与 Anderson-Rubin 流程处理, 少聚类补充 Wang 与 Zhang (2024) 型推断。与当期臂互为稳健性、不分主次, 各自 just-identified 并排, 禁与当期臂或 Bartik 族拼进同一 over-identified Hansen J (LOO 双时点同源; 与 Bartik 合并则须双排他性假设联合论证, 默认不做)。补充口径: 本滞后臂与 P3 的三年成本收入比变化窗口天然错位对齐, 形成「t-1 年同业实质性叙事 → t 年焦点银行叙事 → t 到 t+3 年效率变化」的时间梯队, 比当期臂更不易被结果窗口内的同期共同冲击污染, 这是它在 P3 稳健性规格中的主要价值而非冗余重复。代价是炒作周期切换削弱叙事基调的年际持续性, 从而削弱滞后相关性, 一阶段 F 须逐表单独报告, 弱工具时按 Stock 与 Yogo (2005) 与 Anderson-Rubin 流程处理, 少聚类补充 Wang 与 Zhang (2024) 型 bootstrap。T=2 面板仅 2018 年有值, 生产 T=18 恢复。

<!-- rendered-citations:begin -->
Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.05658
Nibbering, D., & Oosterveen, M. (2025). Policy-relevant causal effect estimation using instrumental variables with interference. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.12538
Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. Journal of Corporate Finance, 93, Article 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. The Quarterly Journal of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, Article 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation?. The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the Fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (Cambridge University Press). https://doi.org/10.1017/CBO9780511614491.006
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
<!-- rendered-citations:end -->
