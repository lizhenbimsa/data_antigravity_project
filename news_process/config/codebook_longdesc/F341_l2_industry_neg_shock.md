---
family_id: F341
columns:
- industry_neg_shock
- industry_neg_shock_ctx
- industry_neg_shock_lag1
- industry_neg_shock_lag1_ctx
- industry_neg_shock_lag1_ss
- industry_neg_shock_ss
unit: 同行银行负面报道占比的留一均值 (无量纲比例, 取值域 [0,1])
formula: "neg_ratio_{trk,i,t} = neg_count_{trk,i,t} / n_articles_llm_valid_{trk,i,t} (有效篇数 >= min_count=5 守门, 分子分母严格逐轨; trk ∈ {full=无后缀, ctx, ss}); industry_neg_shock{sfx}_{i,t} = mean_{j≠i}(neg_ratio_{trk,j,t}) = (Σ_j ratio_{j,t} − ratio_{i,t}) / (N_t − 1); industry_neg_shock_lag1{sfx}_{i,t} = industry_neg_shock{sfx}_{i,t−1} (按 target_bank 组内 shift(1))"
producer: news_process/pipeline/panel/network_brokerage.py::compute_industry_neg_shock (40_panel_export_main 步骤 7h-neg)
upstream:
- 41_panel_encode_aggregate (neg_count_{full,ctx,ss}, n_articles_llm_valid{,_ctx,_ss})
- 21_tone_llms.parquet (三家 LLM 投票负面判定, full-only 留篇门控)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: "10.1016/j.econlet.2023.111170"
  type: "journal"
  authors: "Dosumu, O. E., Sakariyahu, R., Oyekola, O., & Lawal, R."
  year: 2023
  title: "Panic bank runs, global market contagion and the financial consequences of social media"
  venue: "Economics Letters"
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: "Diamond cuts diamond: News co-mention momentum spillover prevails in China"
  venue: Journal of Banking & Finance
  vol: 171
  pages_or_artno: "Article 107356"
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: Han, M., Kim, S. H., & Nanda, V.
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: 132
  issue: 7
  pages_or_artno: 2274-2303
- doi: 10.48550/arXiv.2404.14337
  type: arxiv
  authors: Sadeghi, A., & Feinstein, Z.
  year: 2024
  title: "Statistical validation of contagion centrality in financial networks"
  venue: arXiv
- doi: 10.3982/ECTA19367
  type: journal
  authors: Borusyak, K., & Hull, P.
  year: 2023
  title: "Nonrandom exposure to exogenous shocks"
  venue: Econometrica
  vol: 91
  issue: 6
  pages_or_artno: 2155-2185
- doi: 10.1016/j.jfs.2021.100889
  type: journal
  authors: Bai, Y., Dang, T. V., He, Q., & Lu, L.
  year: 2022
  title: "Does lending relationship help or alleviate the transmission of liquidity shocks? Evidence from a liquidity crunch in China"
  venue: Journal of Financial Stability
  vol: 58
  pages_or_artno: "Article 100889"
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  pages_or_artno: 171-202
- doi: 10.1111/jofi.13010
  type: journal
  authors: Duarte, F., & Eisenbach, T. M.
  year: 2021
  title: "Fire-sale spillovers and systemic risk"
  venue: The Journal of Finance
  vol: 76
  issue: 3
  pages_or_artno: 1251-1294
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1257/pol.20160005
  type: journal
  authors: Greenstone, M., Mas, A., & Nguyen, H.-L.
  year: 2020
  title: "Do credit market shocks affect the real economy? Quasi-experimental evidence from the Great Recession and 'normal' economic times"
  venue: "American Economic Journal: Economic Policy"
  vol: 12
  issue: 1
  pages_or_artno: 200-225
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: 11
  pages_or_artno: 727-753
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1086/696272
  type: journal
  authors: Amiti, M., & Weinstein, D. E.
  year: 2018
  title: "How much do idiosyncratic bank shocks affect investment? Evidence from matched bank-firm loan data"
  venue: Journal of Political Economy
  vol: 126
  issue: 2
  pages_or_artno: 525-587
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.3982/ECTA6248
  type: journal
  authors: Bloom, N.
  year: 2009
  title: "The impact of uncertainty shocks"
  venue: Econometrica
  vol: 77
  issue: 3
  pages_or_artno: 623-685
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1257/aer.98.4.1413
  type: journal
  authors: Khwaja, A. I., & Mian, A.
  year: 2008
  title: "Tracing the impact of bank liquidity shocks: Evidence from an emerging market"
  venue: American Economic Review
  vol: 98
  issue: 4
  pages_or_artno: 1413-1442
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1016/j.najef.2025.102444"
  title: "From collapse to contagion: How bank failures influence stock markets"
  authors: "Brož, V., & Teplý, P."
  year: 2025
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
- doi: "10.1016/j.gfj.2024.101044"
  title: "Bank scandal contagion: Evidence from the Wells Fargo cross-selling scandal"
  authors: "Noel, M. D., & Osman, S. M. I."
  year: 2024
  venue: "Global Finance Journal"
  type: "journal"
- doi: "10.1016/j.frl.2023.104696"
  title: "The spillover effect of bank distress: Evidence from the takeover of Baoshang Bank in China"
  authors: "Xu, Y., Liu, Z., & Zhang, L."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
new_dois:
- "10.1016/j.econlet.2023.111170"
- "10.1016/j.najef.2025.102444"
- "10.1016/j.gfj.2024.101044"
- "10.1016/j.frl.2023.104696"
---

## CORE

利用2023年美国银行业动荡的推特数据发现社交媒体负面情绪跨94国市场传染,为行业层面银行负面舆论冲击的跨主体外溢机制提供了独立的实证证据。

【构念与来源】
本家族测度的构念是"行业负面舆论压力" (industry-level negative media pressure): 银行 i 在年份 t 所处的银行业整体负面媒体环境的强度, 操作化为同年除自身之外全部同行银行的负面报道占比的等权均值 (Leave-One-Out, 下称 LOO)。构念的经济学动机来自三条相互交织的文献脉络。第一条是媒体情绪与银行稳定文献: 媒体对银行业的负面报道并非中性的信息记录, 而是能够实质性地改变储户与投资者行为的传导渠道。Fang 等 (2024) 用中国数据证明媒体情绪显著影响存款稳定性并放大银行系统性风险; Cookson 等 (2026) 进一步表明, 在社交媒体时代负面叙事的扩散速度足以成为银行挤兑的直接催化剂。这意味着"全行业被负面报道笼罩"本身构成一种可测量的外部压力状态, 与单家银行自身被负面报道是两个不同层次的构念。第二条是中国媒体制度背景文献: You、Zhang 与 Zhang (2018) 揭示了中国市场化媒体与官方媒体在"笔杆子权力"上的分化, 媒体负面报道对公司治理与市场定价有真实约束力; Xu (2024) 则提醒财经记者的社交网络会系统性地塑造新闻偏向, 因此行业层面聚合 (跨媒体、跨银行取均值) 相比单篇报道信号更能平滑单个记者或单家媒体的特异性偏差。Ge、Li 与 Zheng (2025) 用中国新闻共现数据证明新闻信号在关联主体之间存在可检验的动量溢出, 为"以新闻测度行业间传染压力"的效度提供了中国语境下的直接证据。第三条是银行冲击传导文献: Khwaja 与 Mian (2008) 及 Amiti 与 Weinstein (2018) 确立了银行层面特异性冲击向实体经济传导的识别范式, Greenstone、Mas 与 Nguyen (2020) 度量了信贷市场冲击的宏观后果, Bai 等 (2022) 专门考察了中国流动性紧缩期冲击沿借贷关系的传导。本测度把这一"冲击暴露"思想移植到舆论维度: 银行的经营结果 (融资成本、存款流动、金融科技投入等) 不仅取决于自身的媒体形象, 也取决于其所处行业在当年承受的舆论冲击总量。数据来源上, 分子 neg_count_{trk} 来自 stage 21 三家大模型 (gpt54nano、gemini31、deepseekv4) 独立打分后多数投票判定为负面的文章篇数, 经 41_panel_encode_aggregate 聚合到银行-年格; 分母 n_articles_llm_valid_{trk} 是同一聚合阶段产出的该轨 LLM 有效判定篇数。留篇门控遵循 2026-06-29 起的 full-only 口径: 一篇文章是否计入"银行金融科技报道宇宙"只由 full 轨的 llm_verified_full 判定, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 各轨情感列在该子集上逐轨计算。

【方法学与计算】
计算由 pipeline/panel/network_brokerage.py 的 compute_industry_neg_shock 函数在主管线 40_panel_export_main 的步骤 7h-neg 完成, 位于 46_network_spillovers 之后执行。第一步构造银行-年负面比率: neg_ratio 等于该轨负面篇数除以该轨 LLM 有效篇数, 分母先经除零保护 (零篇数置缺失), 再经最小篇数守门 — 有效篇数低于 min_count (默认取五篇) 的银行-年格其比率整体置缺失。守门的动机是等权 mean-of-ratios 设计下, 单篇银行的比率只能取零或一两个极值, 若不设门槛, 一家只被报道过一篇的小银行就可能独家拉动全行业指数水平; 五篇门槛对齐项目内 attention 与 encode 系列的最小篇数惯例。第二步执行逐年 LOO 内核: 对每个年份, 先求全体有效银行比率之和与有效银行数, 银行 i 的冲击值等于总和减去自身比率后除以有效银行数减一, 即严格排除自身的同行等权均值。三条边界规则: 其一, 自身比率缺失但同年存在至少一家有效同行时, 冲击值取全体有效同行的均值 — 求和本就不含自身, 天然满足 leave-out, 行业级变量不与自身覆盖状态绑定; 其二, 单银行年份 (有效银行数不超过一) 无法做 LOO, 置缺失; 其三, 缺失值在求和中被自动忽略, 不污染均值。第三步产出滞后变体: 面板按银行与年份排序后组内后移一期, 各银行首个观测年为缺失。三轨实现严格遵循"分子分母逐轨对齐"纪律: 无后缀 canonical 轨用 neg_count_full 配 n_articles_llm_valid (仅当旧面板缺该列时回退物理篇数 n_articles, 此回退仅限 canonical 轨的历史兼容); ctx 轨用 neg_count_ctx 配 n_articles_llm_valid_ctx, ss 轨用 neg_count_ss 配 n_articles_llm_valid_ss, 两轨均无回退, 缺任一原料列即整轨跳过并发出警告, 绝不借用 full 轨或物理分母 — 这一纪律是为防止分子分母来自不同文本轨造成的口径撕裂。全部计算是确定性的 pandas 分组运算, 不涉及 BLAS 浮点归约, 不在面板九个已知非确定网络列之列。产出六列全部取值于零到一的闭区间, 缺失表示该格无法计算。下游的火灾甩卖交乘项 brokerage_fire_sale 刻意只消费 canonical 同期列 (滞后一期的经纪中心度乘以同期冲击), 不做轨派生。

【识别策略定位】
本测度的识别属性需要放在 Manski (1993) 反射问题的框架下逐层澄清, 这也是六列中同期与滞后变体分工的根本原因。第一层, LOO 解决的且仅解决的是机械性自相关: 若直接使用含自身的行业均值, 银行自身的负面新闻会同时出现在方程两侧, 造成构造性相关; 排除自身消除了这一污染。第二层, 同期 LOO 不解决 Manski 意义上的反射与同时性问题 — 同年所有银行的负面比率仍由共同的行业冲击联合决定, 同期项作为处理变量不满足排他性; 这一点在 2026-06-10 的识别更正中被明确写入 producer 文档, 与 Bramoullé、Djebbari 与 Fortin (2009) 的经典结论一致: 线性均值模型中同期同伴效应的识别需要网络结构提供的非重叠变异 (朋友的朋友不是我的朋友), 而全行业等权 LOO 恰恰是网络完全重叠的极端情形, 内生与外生同伴效应无法分离。Bramoullé 等 (2020) 的综述与 Boucher 等 (2024) 的一般化理论进一步说明, 缺乏结构排除约束时, 同伴效应参数的点识别系统性地失败。第三层是本家族最尖锐的技术警示, 即年固定效应下的精确共线: 同期 LOO 均值可写成组内常数减自身的仿射变换 — 冲击值等于年总和除以银行数减一, 再减去自身比率除以银行数减一。含年固定效应的回归中, 第一项被年效应完全吸收, 剩余识别变异恰好是自身负面比率的负向重标度, 与自身比率 within-year 相关系数恒为负一。换言之, 在项目 paper_spec 默认的银行加年份双固定效应规格下, 同期冲击项的系数根本不是行业冲击效应, 而是自身比率效应的符号翻转; 任何含年固定效应的规格必须改用 lag1 变体, 后者在年固定效应下保留跨期识别变异。这一披露自 2026-06-11 起同时写入 producer 源码、Stata 变量标签 (同期三列标签均带 year-FE collinear 警示, 滞后三列标注 year-FE-safe) 与本长文。第四层, 若要把行业冲击用作因果处理或工具变量, 应参照冲击暴露设计文献的当代标准: Borusyak 与 Hull (2023) 论证了非随机暴露于聚合冲击时需要重新中心化以消除暴露内生性; Borusyak、Hull 与 Jaravel (2025) 给出了 shift-share 类工具的实操清单; Gabaix 与 Koijen (2024) 的颗粒工具变量思想 (以大单元的特异性冲击构造聚合工具) 与本测度的 LOO 结构同源。项目 IV 扩展族中的 leave_one_out_peer_*_iv 系列即沿此路线构造, 其弱工具诊断遵循 Andrews、Stock 与 Sun (2019) 的实践标准。本家族六列自身定位为描述性暴露测度与稳健性梯子, 不主张同期因果识别。

【与相邻测度的构念区分】
面板中存在多个表面相近但构念与代数结构均不同的邻居, 使用者须严格区分。其一, 与 emb_peer_tone_lag1 族 (W-轨嵌入加权同行语调) 的区别: 后者以银行间嵌入余弦相似度为连续权重对同行语调加权, 权重矩阵刻画"认知邻近"的异质结构; 本家族是等权全行业均值, 权重结构退化为常数, 二者分别回答"与我相似的银行怎么样"与"整个行业怎么样"两个不同问题。其二, 与 leave_one_out_peer_*_iv 族的区别: 该族虽同用 LOO 代数, 但均值对象是注意力、实质性份额等非情感测度, 且组定义是同类型银行组而非全行业, 用途是 2SLS 第一阶段工具而非右侧暴露变量。其三, 与 brokerage_fire_sale 的区别: 后者是滞后经纪中心度与同期冲击的交乘项, 检验信息枢纽地位对行业冲击的放大机制 (构念原型是 Duarte 与 Eisenbach (2021) 的火灾甩卖溢出), 本家族提供其中的冲击分量。其四, 与 net_*_yr 年度网络结构指标的区别: 那些是年内常数, 在年固定效应下被整体吸收; 本家族同期列虽逐行变动, 但如上所述其 within-year 变异与自身比率精确共线, 两类列在双固定效应规格下都不可作同期解释变量, 但机理不同 (整体吸收对精确共线)。其五, 与银行自身负面比率的区别: 自身比率是银行级测度, 本家族是排除自身的行业级测度, 二者在无年固定效应规格中可同时入回归以分离自身与行业分量。其六, 后缀空间的区分: 本家族的 _ctx 与 _ss 是三轨文本后缀 (情感原料来自哪一段文本), 与网络结构指标族的 _win1 与 _sent 判据后缀 (银行与银行共现的接近度判据) 是两个互不相通的后缀空间, 本家族不存在判据后缀变体, 因为其输入是情感聚合列而非共现边。

【已知局限与稳健性梯子】
第一, 三轨梯子。full (无后缀)、_ctx、_ss 三轨互为稳健性、不分主次: 无后缀是历史命名产物而非"主测度" (镜像词典族政治词权重 polw05 等价于无后缀 canonical 的先例); full 轨取标题加全文, ctx 轨取标题加目标银行实体窗口文本, ss 轨取标题加银行与金融科技词同句共现的窗口句。ss 轨回退语义镜像 ctx: 当文章不存在银行与金融科技词同句共现时, content_ss 回退为全文并置 ss_is_fallback 为真, 与 full 共享篇数分母口径。三轨各自 just-identified 并排进入各自的回归, 禁止混入同一个 over-identified Hansen J 检验 — 三轨是同一构念的替代测量而非满足排他性的独立工具, 强行合并做过度识别检验在统计上无效, 这是项目级铁律。第二, 滞后梯子。同期与 lag1 构成两级动态规格: 无年固定效应的描述性规格可用同期列, 任何含年固定效应的规格必须用 lag1 列; 滞后同时缓解 (但不根除) 同时性问题, 与 Leary 与 Roberts (2014)、Grieser 等 (2022) 在公司金融同伴效应研究中普遍采用的滞后暴露惯例一致。第三, min_count 阈值是研究者选择, 默认五篇; 其效果是牺牲小银行覆盖率换取比率的方差稳定, 阈值附近的敏感性属于可报告的稳健性维度, 但项目刻意未将其物化为阈值梯子列族, 避免与三轨乘积产生列爆炸。第四, 等权 mean-of-ratios 聚合把每家有效银行视为一票, 大银行与小银行对行业指数贡献相同; 备择的篇数加权 ratio-of-sums 聚合会让报道量大的银行主导指数, 二者构念不同 (行业内银行的平均处境对行业报道总量的负面强度), 本家族固定前者。第五, 覆盖退化。早期试跑盘面仅两个年份, ctx 轨常因唯一负例格的分母不足五篇被守门、ss 轨常因零负例而零方差, 两轨同期列退化为常数属预期现象而非缺陷, 数值验证推迟到生产语料 (真实全量为一千八百一十九万条、十九个年份) 上复核; lag1 列在早期两年试跑面板上仅第二年有值, 生产面板上首年缺失占比会自然摊薄。第六, 分母口径继承 full-only 留篇门控的数值副作用: 门控口径的任何变更会同时移动分子与分母, 本家族对门控翻转不具有向后可比性, 跨版本比较须核对留篇口径一致。第七, 系统性风险文献的告诫同样适用于舆论网络: Jackson 与 Pernoud (2021) 强调传染测度对网络拓扑设定高度敏感, Sadeghi 与 Feinstein (2024) 表明传染中心性类指标需要统计显著性验证而非直接当作点估计使用; 本家族的全行业等权设定是最保守的拓扑假设, 其代价是无法刻画分层传染路径。

【白话理解与使用速查】
用大白话概括: 这一族变量回答的问题是"这一年, 除了我之外的整个银行业, 在媒体上被骂得有多凶"。做法是先给每家银行算一个"被骂比例" — 当年被大模型判定为负面的报道篇数, 除以当年被大模型有效判定过的报道总篇数; 报道太少的银行 (不足五篇) 不算数, 因为一两篇报道算出来的比例不是零就是一, 太极端, 会把全行业的数带偏。然后对每家银行, 把同一年其他所有算得出比例的银行的比例加起来取平均, 唯独不算它自己 — 不算自己是为了避免"自己骂自己再解释自己"的循环。为什么还要一套滞后一年的版本: 因为在最常用的"银行固定效应加年份固定效应"回归里, 同年版本有一个致命的代数陷阱 — 年份固定效应把"全行业当年的总水平"吸干净之后, 这个变量剩下的信息恰好就是"自己的被骂比例乘以负号", 回归跑出来的系数看着是行业效应, 实际上是自己效应换了个符号, 完全不是想要的东西; 滞后一年的版本没有这个陷阱, 因为"去年的行业水平"不会被"今年的年份效应"吸走。所以速查规则只有一条: 回归里带年份固定效应, 就只能用带 lag1 的三列; 不带年份固定效应的描述性回归, 才可以用同期三列。三个文本轨道的直觉: full 是"整篇文章怎么写", ctx 是"提到这家银行的那几句怎么写", ss 是"银行和金融科技出现在同一句话里的那几句怎么写", 从宽到窄, 越窄越贴金融科技主题但覆盖越少; 三个轨道地位平等, 分别跑回归互相印证, 不允许打包塞进同一个过度识别检验。

【文献定位】
在文献坐标系中, 本家族处于三个研究传统的交点。方法论上, 它属于以文本测度经济暴露的度量传统 — Hassan 等 (2019) 用电话会议文本构造企业级政治风险暴露的范式确立了"文本份额比率作为暴露测度"的合法性, 本家族把该思想应用于中文银行新闻的负面份额; Bloom (2009) 则提供了"不确定性冲击具有实质宏观后果"的基准证据, 支撑负面舆论冲击作为解释变量的经济意义。识别论上, 它继承 Manski (1993) 反射问题与 Bramoullé 等 (2009, 2020)、Boucher 等 (2024) 的网络同伴效应识别理论, 并按 Borusyak 与 Hull (2023) 及 Borusyak 等 (2025) 的当代冲击暴露设计标准披露自身的识别边界。应用上, 它服务于媒体与银行稳定文献 (Fang 等 2024; Cookson 等 2026; You 等 2018) 与银行冲击传导文献 (Khwaja 与 Mian 2008; Amiti 与 Weinstein 2018; Bai 等 2022; Greenstone 等 2020) 的交叉议题, 并作为 Han 等 (2024) 式信息经纪网络分析 (本模块另产出媒体-银行二分图中心度) 中"冲击放大机制"检验的暴露分量。六列的完整梯子设计 (三轨乘以同期与滞后) 使研究者能在披露识别局限的前提下, 系统展示结论对文本轨道与动态时序选择的不敏感性。此外, Brož 与 Teplý (2025, The North American Journal of Economics and Finance) 实证检验单家银行倒闭事件如何通过股票市场溢出为行业层面的负面冲击, 为本家族行业负面舆论压力构念中个体负面事件外溢至同业的经济机制提供了2025年的最新证据。以富国银行交叉销售丑闻为准实验, 证明单一银行负面事件会通过声誉渠道向同业传染负面情绪, 为本家族行业负面舆论压力构念提供丑闻传染机制的实证支持, 见 Noel 与 Osman (2024, Global Finance Journal)。利用包商银行被接管这一中国准自然实验, 证明单家银行的困境事件会显著提高同业银行贷款组合风险, 为行业级负面冲击的同业传导提供中国场景的直接证据, 见 Xu、Liu 与 Zhang (2024, Finance Research Letters)。

## VAR: industry_neg_shock

【变体差分】
本列是家族 canonical 列 (tier=core, 类别六网络溢出 headline), 无后缀即 full 轨同期版: 分子取 neg_count_full (三家大模型多数投票判负的 full 轨篇数), 分母取 n_articles_llm_valid (full 轨 LLM 有效判定篇数; 仅当旧版面板缺该列时回退物理篇数 n_articles, 此历史兼容回退是六列中唯一的回退通道, ctx 与 ss 轨严格无回退), 比率经五篇最小有效篇数守门后, 对同年除自身外全部有效银行取等权均值。须再次强调无后缀不等于"主测度": 三轨互为稳健性、不分主次, 无后缀只是历史命名产物 (镜像 du_2022 词典族 polw05 等价于无后缀 canonical 的项目先例), full 轨的实际优先性仅来自 2026-06-29 起的留篇门控口径 — 文章是否进入银行金融科技报道宇宙由 llm_verified_full 单独判定, 因此 full 轨的分子分母覆盖是三轨中最完整的, ctx 与 ss 是 conditional-on-full 的子集轨。本列的核心使用警示是年固定效应精确共线: 同期 LOO 均值等于年总和项减去自身比率项的仿射变换, 年总和项被年固定效应吸收后, 残余变异与银行自身负面比率 within-year 相关系数恒为负一, 故本列绝不可进入含年固定效应的规格 — 项目 paper_spec 默认的银行加年份双固定效应下, 本列系数是自身比率效应的符号翻转重标度而非行业冲击效应, Stata 变量标签为此显式携带 year-FE collinear 警示。合法用法有三: 无年固定效应的描述性或截面规格中作行业暴露变量; 作 brokerage_fire_sale 交乘项的冲击分量 (该交乘刻意 canonical-only, 不派生轨变体); 以及与自身负面比率同时入无年固定效应回归以分离自身与行业分量。含年固定效应的一切规格请改用同族 industry_neg_shock_lag1。LOO 设计消除的是机械性自相关 (Manski 1993 意义上的构造性污染), 不构成同时性问题的解决, 同期列作处理变量不满足排他性 — 这一识别边界连同年固定效应警示一起, 构成本列区别于滞后变体的全部差分语义。取值域为零到一闭区间, 单银行年份与全年无有效同行时缺失。三条缺失路径的语义各不相同, 使用者做样本筛选时须区分: 第一种, 自身比率有效但同年不存在第二家有效银行, 无法留一, 置缺失 — 这是小样本年份的机械缺口; 第二种, 自身比率因分母不足五篇被守门置缺失, 但同年存在至少一家有效同行, 此时本列仍取全体有效同行的均值 — 求和本就不含自身, 天然满足留一语义, 这一设计 (2026-06-11 修正) 确保行业级暴露变量不与银行自身的报道覆盖状态绑定, 避免"报道少的银行连行业环境都观测不到"的选择性缺失; 第三种, 全年无任何有效银行, 整年缺失。等权 mean-of-ratios 的聚合含义也须写明: 每家过守门线的银行对行业指数贡献一票, 与其报道总量无关, 度量的是"行业内银行的平均舆论处境"; 若研究问题关心"行业报道流的总体负面强度", 应自行按篇数加权重构, 本列不承担该构念。作为类别六网络溢出的 headline 列, 本列还是 brokerage_fire_sale 交乘机制检验的冲击分量输入 — 该交乘检验的是信息枢纽银行 (滞后经纪中心度高) 在行业负面冲击到来时是否承受放大效应, 交乘规格因不含年固定效应而合法使用同期冲击, 这是本列在项目内最主要的下游消费场景。

## VAR: industry_neg_shock_ctx

【变体差分】
本列是 canonical 列的 ctx 轨同期变体, 差分维度仅在文本轨道: 分子取 neg_count_ctx, 分母取 n_articles_llm_valid_ctx, 分子分母严格逐轨对齐, 缺任一原料列时整轨跳过, 绝不借用 full 轨或物理分母 — 这是 2026-07-03 三轨扩展时为防轨道不对称口径撕裂而立的硬纪律。ctx 轨文本为标题加目标银行实体窗口 (prepend_title 后围绕银行实体提及的邻域句), 其构念指向"与目标银行直接相关的文本片段所表达的负面性", 相比 full 轨剔除了同篇文章中与该银行无关段落的情感噪声, 是归因更严格的测量臂。行宇宙遵循 full-only 留篇门控: ctx 轨是 conditional-on-full 的测度轨, 其覆盖是 full 留篇集的子集, 且逐格须独立满足五篇最小有效篇数守门, 故本列的有效覆盖系统性地不超过 canonical 列。早期试跑盘面上 ctx 轨曾因唯一负例格分母不足守门而整轨零方差, 属预期退化而非缺陷, 生产语料上应恢复正常方差。本列与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排进入各自回归, 禁混同一 over-identified Hansen J — 三轨是同一构念的替代测量, 不是相互独立的工具变量。年固定效应精确共线警示对本列同样成立 (共线代数与轨道无关, 只依赖 LOO 仿射结构), 含年固定效应规格请改用 industry_neg_shock_lag1_ctx。

## VAR: industry_neg_shock_lag1

【变体差分】
本列是 canonical 列的一阶滞后变体, 差分维度仅在动态时序: 面板按 target_bank 与 year 排序后组内后移一期, 银行 i 在年份 t 的取值等于其 t 减一年的 industry_neg_shock, 各银行样本内首个观测年为缺失, 滞后约定与 compute_fire_sale_interaction 的经纪中心度滞后一致。本列存在的根本理由是解除同期列的年固定效应死锁: 同期 LOO 均值的年公共项被年固定效应吸收后与自身比率精确共线, 而滞后一期后, t 减一年的行业冲击相对 t 年的年固定效应保留了真实的跨期识别变异, Stata 标签为此标注 year-FE-safe。因此本列是项目 paper_spec 默认双固定效应规格下本家族唯一可用的 full 轨解释变量形态, 也是 producer 文档明示的"含年固定效应规格请改用"指向列。滞后同时具有识别改进含义: 按同伴效应文献惯例 (Leary 与 Roberts 2014 的公司金融应用与 Bramoullé 等 2020 综述的时序论证), 滞后暴露削弱同期共同冲击驱动的同时性, 让系数更接近前定暴露的解释 — 但须诚实披露滞后并非根治, 行业舆论冲击存在跨年持续性时, 滞后项仍携带序列相关的共同因子, 严格因果主张仍需工具化路线。分子分母口径、五篇守门、LOO 边界规则全部继承 canonical 列, 无任何独立自由度。早期试跑盘面两年深度下本列仅第二年有值, 属机械性首年缺失; 生产十九年面板上损失可忽略。与 lag1_ctx、lag1_ss 互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: industry_neg_shock_lag1_ctx

【变体差分】
本列在家族梯子上同时携带两个差分维度: ctx 文本轨道与一阶滞后。计算顺序是先轨后滞 — 先按 ctx 轨严格逐轨口径 (neg_count_ctx 除以 n_articles_llm_valid_ctx, 五篇守门, 无回退) 算出同期 industry_neg_shock_ctx, 再按 target_bank 组内后移一期, 首年缺失。因此本列同时继承两条使用语义: 从 ctx 轨继承"银行实体窗口文本的归因严格性"与 conditional-on-full 的子集覆盖 (有效格须 ctx 轨分母独立过五篇门槛, 覆盖不超过 lag1 无后缀列); 从滞后维度继承 year-FE-safe 属性 — 本列是含年固定效应规格下 ctx 轨的唯一合法形态, 同期 ctx 列在双固定效应下与自身 ctx 比率精确共线的问题在此解除。典型用法是作 industry_neg_shock_lag1 的稳健性平行臂: 在同一含年固定效应的模型骨架下, 分别以 lag1 (full)、lag1_ctx、lag1_ss 三列各跑一支回归, 展示行业舆论冲击的滞后效应不依赖文本轨道选择。铁律照旧: 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁把三支滞后轨塞进同一个 over-identified Hansen J — 它们是同一构念的替代测量而非独立工具。早期试跑盘面上本列因上游同期 ctx 列零方差退化叠加两年深度首年缺失而近乎全缺, 属双重预期退化; 生产语料上两个退化源都会消解。滞后不根治同时性的披露对本列同样适用。

## VAR: industry_neg_shock_lag1_ss

【变体差分】
本列携带 ss 文本轨道与一阶滞后两个差分维度, 是家族梯子中归因口径最窄的滞后臂。ss 轨同期原料为 neg_count_ss 除以 n_articles_llm_valid_ss (严格逐轨, 五篇守门, 无回退), 文本为标题加银行与金融科技词同句共现的窗口句 (半径由 config 的 ss_sentence_radius 控制, 默认一句), 构念指向"银行与金融科技在最紧密语境中被共同提及时的负面性", 是三轨中信噪比最高但覆盖最窄的测量臂。须完整继承 ss 轨回退语义: 文章无银行与金融科技同句共现时 content_ss 回退为全文并置 ss_is_fallback 为真, 与 full 共享篇数分母口径, 镜像 ctx 的回退设计; 因此 ss 轨的负面判定在回退占比高的银行-年格上会向 full 轨收敛, 解读时须意识到该列不是纯窗口句测度而是"窗口句优先、全文兜底"的混合测度。滞后维度语义与其余 lag1 列完全一致: 组内后移一期, 首年缺失, year-FE-safe, 是含年固定效应规格下 ss 轨的唯一合法形态。典型用法是滞后三轨稳健性三联的第三臂, 与 lag1、lag1_ctx 并排各自 just-identified 回归, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。早期试跑盘面上 ss 轨同期列因零负例而零方差, 叠加首年缺失后本列近乎全缺, 属预期退化; 生产语料上负例充足, 该列应有正常变异。若三滞后臂系数符号一致而幅度沿 full、ctx、ss 递变, 该梯度本身携带信息: 冲击效应集中于金融科技语境的程度可由窄轨相对宽轨的幅度比刻画。

## VAR: industry_neg_shock_ss

【变体差分】
本列是 canonical 列的 ss 轨同期变体, 差分维度仅在文本轨道, 且是三条同期轨中语境口径最严格的一条: 分子 neg_count_ss 只统计在"银行与金融科技词同句共现窗口句" (标题按 prepend_title 约定计入第零句) 文本上被三家大模型投票判负的篇数, 分母 n_articles_llm_valid_ss 为同轨有效判定篇数, 分子分母严格逐轨、缺列整轨跳过、绝不借 full 分母。ss 轨回退语义必须如实纳入解读: 无同句共现的文章其 content_ss 回退为全文 (ss_is_fallback 为真, 镜像 ctx 回退设计, 与 full 共享篇数分母), 极端情形下若金融科技自动机不可用则全体回退并优雅降级, 因此本列在回退率高的格上向 full 轨测量收敛。行宇宙为 full-only 留篇门控下的 conditional-on-full 子集, 叠加逐格五篇守门后本列覆盖是三条同期轨中最窄的。年固定效应精确共线警示不因轨道而豁免: LOO 仿射共线结构与文本轨无关, 本列同样禁止进入含年固定效应的规格, 该场景请改用 industry_neg_shock_lag1_ss。早期试跑盘面上本列因两年语料零 ss 轨负例而恒为零方差, producer 日志将其标记为预期退化, 生产十九年语料上应恢复变异。与 full、ctx 同期轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。本列的独特价值在于其构念纯度: 当研究问题是"银行的金融科技活动所引致的行业负面舆论" 而非"银行的一般负面舆论"时, ss 轨的窄语境口径提供了最贴合的行业冲击测量。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Dosumu, O. E., Sakariyahu, R., Oyekola, O., & Lawal, R. (2023). Panic bank runs, global market contagion and the financial consequences of social media. Economics Letters. https://doi.org/10.1016/j.econlet.2023.111170
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. Journal of Banking & Finance, 171, Article 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage networks: Facilitating liquidity provision. Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.14337
Borusyak, K., & Hull, P. (2023). Nonrandom exposure to exogenous shocks. Econometrica, 91(6), 2155-2185. https://doi.org/10.3982/ECTA19367
Bai, Y., Dang, T. V., He, Q., & Lu, L. (2022). Does lending relationship help or alleviate the transmission of liquidity shocks? Evidence from a liquidity crunch in China. Journal of Financial Stability, 58, Article 100889. https://doi.org/10.1016/j.jfs.2021.100889
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Duarte, F., & Eisenbach, T. M. (2021). Fire-sale spillovers and systemic risk. The Journal of Finance, 76(3), 1251-1294. https://doi.org/10.1111/jofi.13010
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Greenstone, M., Mas, A., & Nguyen, H.-L. (2020). Do credit market shocks affect the real economy? Quasi-experimental evidence from the Great Recession and 'normal' economic times. American Economic Journal: Economic Policy, 12(1), 200-225. https://doi.org/10.1257/pol.20160005
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Amiti, M., & Weinstein, D. E. (2018). How much do idiosyncratic bank shocks affect investment? Evidence from matched bank-firm loan data. Journal of Political Economy, 126(2), 525-587. https://doi.org/10.1086/696272
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bloom, N. (2009). The impact of uncertainty shocks. Econometrica, 77(3), 623-685. https://doi.org/10.3982/ECTA6248
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Khwaja, A. I., & Mian, A. (2008). Tracing the impact of bank liquidity shocks: Evidence from an emerging market. American Economic Review, 98(4), 1413-1442. https://doi.org/10.1257/aer.98.4.1413
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Brož, V., & Teplý, P. (2025). From collapse to contagion: How bank failures influence stock markets. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2025.102444
Noel, M. D., & Osman, S. M. I. (2024). Bank scandal contagion: Evidence from the Wells Fargo cross-selling scandal. Global Finance Journal. https://doi.org/10.1016/j.gfj.2024.101044
Xu, Y., Liu, Z., & Zhang, L. (2024). The spillover effect of bank distress: Evidence from the takeover of Baoshang Bank in China. Finance Research Letters. https://doi.org/10.1016/j.frl.2023.104696
<!-- rendered-citations:end -->
