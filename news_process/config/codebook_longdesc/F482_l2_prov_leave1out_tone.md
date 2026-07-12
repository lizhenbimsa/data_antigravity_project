---
family_id: F482
columns:
- prov_leave1out_tone_ctx
- prov_leave1out_tone_full
- prov_leave1out_tone_ss
unit: 语调工具变量得分 (连续, 无量纲, 与底层 llm_vote_tone 同标度约 [-1,1]; bank-year 层级)
formula: "prov_leave1out_tone{track}_{i,t} = (Σ_{j≠i, j∈G(i)} llm_vote_tone{track}_{j,t} − llm_vote_tone{track}_{i,t}) / (N_{G,t} − 1); G(i)=银行 i 所在省份 (bank_province), N_{G,t}=该省该年有非缺情感的银行数, N_{G,t}=1 时置 NaN"
producer: news_process/pipeline/panel/geography.py::compute_leave_one_out_sentiment (步骤 7d); 变量标签 news_process/pipeline/falsification/controls.py::STATA_LABELS_41
upstream:
- 40_panel_yearly.parquet (llm_vote_tone_full / llm_vote_tone_ctx / llm_vote_tone_ss)
- 40_panel_yearly.parquet (bank_province — 步骤 7c merge_bank_geography 注入)
citations:
- doi: 10.1111/jofi.70034
  type: journal
  authors: Drechsler, I., Savov, A., Schnabl, P., & Wang, O.
  year: 2026
  title: "Deposit franchise runs"
  venue: The Journal of Finance
  vol: 81
  issue: 3
  pages_or_artno: 1573-1617
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: 104218
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: 112803
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: 241
  issue: 1
  pages_or_artno: 105727
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: 103870
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: Emerging Markets Review
  vol: 64
  pages_or_artno: 101234
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1093/rof/rfac052
  type: journal
  authors: Goldstein, I.
  year: 2023
  title: "Information in financial markets and its real effects"
  venue: Review of Finance
  vol: 27
  issue: 1
  pages_or_artno: 1-32
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是一组省级 leave-one-out (留一法) 地理平均语调工具变量: 对面板中每一个银行-年度观测, 取该银行注册地所在省份内其余所有银行当年的平均新闻语调, 严格剔除该银行自身, 用作估计"媒体语调对银行结果变量"因果效应时的外生工具变量 (instrumental variable)。构念的直觉是: 一家银行所处的本地媒体生态 (省级报纸的选题偏好、地方宣传口径、区域性金融叙事的冷热) 会同时笼罩同省的一整片银行, 因而"同省其他银行当年被报道的语调"承载了与本银行语调相关的共同外生成分; 但邻居银行的报道语调不太可能由本银行自身当年的经营决策直接决定, 于是"除我之外的本地平均舆论"就构成了一股既相关又相对外生的推力。之所以必须把自身从组均值中剔除, 是因为一旦工具里混入了被解释银行自己的语调, 内生性会原路返回, 工具随即失效——这正是 leave-one-out 构造相对朴素"组均值"的关键改进。底层被聚合的语调是 stage 21 情感 LLM 的三家多数投票共识列 llm_vote_tone{track} (gpt54nano / gemini31 / deepseekv4 三家投票), 已在 bank-year 面板层预先按 full-only 留篇门控聚合成型, 本步骤不再触碰文章级信息, 只在面板上做省份分组的算术再聚合。需要强调工具"外生性"的来源结构: 被解释银行 i 当年的经营基本面、被报道的负面事件、乃至其管理层的公关策略, 都可能同时驱动"本银行被报道的语调"与"本银行的融资成本"等结果变量, 这正是直接用本银行语调做回归会内生的根源。而同省其他银行 j 的语调之所以能充当外生推力, 逻辑在于: 省级媒体的选题风格、地方宣传节律、区域金融叙事的整体冷暖是一种笼罩全省银行的共同外生环境, 它把相关性注入邻居语调与本银行语调之间; 与此同时, 邻居 j 被怎样报道, 一般并不由本银行 i 当年的具体决策所决定 (排他性的直觉), 于是"邻居语调"相对本银行结果就近似只经"本银行语调"这一唯一通道起作用。工具的说服力因此高度依赖"本地媒体生态的共同冲击"这一实体机制是否成立, 而非纯统计构造——这也是为何本家族的文献定位必须同时锚在"媒体语调如何产生共同变异"与"这一变异为何不直接进入结果方程"两侧。省份标识 bank_province 由步骤 7c 的 merge_bank_geography 从银行注册地字典注入, 代表银行总部所在省, 而非报道来源地; 因此本工具刻画的是"注册地同省同业的舆论溢出", 与基于"报道来源地"的媒体关注度工具在变异来源上正交。

【方法学与计算】
计算实现于 pipeline/panel/geography.py 的 compute_leave_one_out_sentiment (编号步骤 7d), 采用 O(N) 的向量化留一公式: 先对 (省份, 年度) 分组用 groupby.transform 求组内语调总和 group_sum 与有效计数 group_cnt, 再对每一行取 leave1out_i = (group_sum − tone_i) / (group_cnt − 1)。这一构造的经济学含义值得展开: 分子 group_sum − tone_i 恰是"把本银行自己的语调从省级总和里扣掉"后剩余的邻居语调之和, 分母 group_cnt − 1 是扣掉本银行后的邻居数, 二者相除即省内其余银行当年语调的算术平均。之所以坚持用留一均值而非直接用含自身的省级组均值, 是因为组均值里始终残留 1/N 权重的本银行语调, 当 N 较小 (中国许多省份上市/发债银行不过数家) 时这一残留占比可观, 足以让"工具"与"处理"机械共动而伪造出第一阶段相关性并破坏排他性; 留一构造把这一污染项精确清零, 是弱识别情形下必需而非可选的净化步骤。这一写法在一次分组广播里同时完成对每家银行的"减去自身、除以邻居数", 避免逐行循环。有效子集的筛选有两道闸: 其一要求银行有非空省份标识 (排除注册地未匹配的银行), 其二要求银行当年有非缺失的情感得分 (排除零新闻的银行-年度)。边界处理是方法论上刻意为之的: 当某省某年只有一家银行有有效语调时, 留一分母 N−1 归零, 该观测的工具值置为 NaN——因为无法从一个孤立样本推断其所处的本地媒体生态, 强行赋值等于凭空捏造外生变异。代码在赋值前设有三道 -O 存活的显式 raise 守卫 (原裸 assert 在 python 优化模式下会被剥离, 已改为显式抛错): 分别校验参与计算的语调无空值、组频数无 NaN、以及分母 N−1 严格为正; 这三道守卫保护的正是工具变量分母非零这一命门, 比一般的建图断言更需在优化模式下存活。计算须排在 balance_panel (步骤 6) 与 merge_bank_geography (步骤 7c) 之后运行, 因为留一公式假设每家银行在 (地理, 年度) 单元内唯一出现, 这由面板平衡保证; 而省份列须由地理合并先行落地。本家族在生产口径上共产出双层 (省级 prov / 城市级 city) × 三轨 (full / ctx / ss) = 六个变量, 本 F482 家族专收省级三轨这一支; 城市级三轨归属相邻家族。命名上使用 _GEO_SHORT 映射把 bank_province 缩写为 prov (而非 replace 派生的冗长 province_ 前缀), 以确保面板列名、Stata 模板占位符与 STATA_LABELS_41 变量标签三处严格一致, 列名长度均 ≤32 字符满足下游约束。三轨的 tone_col 通过循环 f'llm_vote_tone{track}' 逐轨取列, 当某轨 (典型是 ss) 因上游未落盘而缺列时, 代码以 if tone_col not in panel.columns: continue 优雅跳过该轨而不报错, 保证部分轨缺失时其余轨照常产出, 这是逐轨独立降级而非家族级 both-or-neither 连坐。诊断日志会对每轨记录有效工具值数 n_valid 与因单银行组退化置 NaN 的观测数 n_singleton, 供事后核查覆盖率; 这些计数在开发浅面板上会显示大量 singleton, 在生产深面板上则显著回落, 是判断工具在特定语料上是否具有足够第一阶段力度的第一手证据。整个步骤不产生任何文章级中间列, 只在既有 bank-year 面板上追加六个双精度浮点列, 因而它是纯面板后处理, 计算成本极低且与 LLM/嵌入 API 完全无关——换情感模型或换嵌入模型时本家族零改动, 只要底层 llm_vote_tone{track} 列名不变。

【文献定位】
本家族坐落在三条文献脉络的交汇处。第一条是媒体语调的资产定价与实体后果传统: Tetlock (2007) 奠定了媒体语调 (悲观语调) 系统性预测收益与成交的经典证据, 其后大量文献把语调作为影响投资者信念与真实决策的信息载体。中文语境下这一传统由 Xu 等 (2025) 关于官方媒体语调对股市的作用、以及 Fang 等 (2024) 关于银行级媒体情感与存款稳定性、系统性风险的证据延续; 银行融资条件层面的语调移动测量则见 Marchetti 等 (2025) 对意大利银行融资环境的应用; 语调持续性对可预测性的含义见 Aksoy-Yurdagul 等 (2026)。第二条脉络是信息的真实效应与银行负债侧脆弱性: Goldstein (2023) 综述了金融市场信息如何反作用于实体, Chen 等 (2022) 直接刻画银行透明度与存款流动的关系, Drechsler 等 (2026)、Cookson 等 (2026) 与 Cookson 等 (2024) 则从存款特许权挤兑、社交媒体作为挤兑催化剂、以及社交信号的角度揭示舆论如何转化为负债侧的实际冲击——这些工作为本工具下游结果变量 (银行融资成本、存款稳定性等) 的经济学意义提供了因果链条的理论锚点, 解释了"为何语调不只是噪声、值得费力做因果识别"。第三条脉络是语调测量方法学与识别推断纪律: 底层语调的度量横跨词典法 (Du 等 2022 的中文金融情感词典) 与机器学习法 (Huang 等 2023 的 FinBERT), 本项目以三家 LLM 投票共识作主测度并以词典/BERT 互为稳健性; 识别侧则借鉴 Goldsmith-Pinkham 等 (2020) 对移动份额工具的诊断框架、Wang & Zhang (2024) 的弱工具野自助推断、以及 Romano & Wolf (2005) 的逐步多重检验以控制族错误率。本工具作为"同省同业语调溢出"IV 的具体形态, 是把上述媒体语调因果识别的一般思路落到中国银行-金融科技面板上的一个操作化实现。

【识别策略定位】
本家族是所属论文 bank_fintech_tone 识别策略的核心工具变量来源: paper_spec 的 identification.iv 把 prov_leave1out_tone_full 收作主工具, 典型二阶段设定为 ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) X, absorb(target_bank year) cluster(target_bank), 即以省级留一语调工具化本银行的内生语调, 估计语调对下游结果 (如融资成本) 的因果效应。识别的合法性建立在两条约束上: 相关性 (第一阶段) 依赖同省银行共享本地媒体生态而语调正相关, 排他性 (exclusion) 则要求同省邻居的语调只通过"影响本银行语调"这一唯一通道作用于本银行的结果变量。本工具与面板中另一族地理工具 ft_attn_prov / ft_attn_city (媒体来源地金融科技关注度, 沿 Da 等与 Fang & Peress 2009 传统) 在变异来源上不同: 后者捕获"媒体关注度"维度, 前者捕获"情感溢出"维度, 二者从不同角度提供外生推力, 因而可并联进入过度识别检验 (Hansen J) 以检验排他性约束是否同时成立。除留一语调工具外, 论文的识别工具箱还配有广义 Bartik 移动份额工具与媒体来源 house-style 暴露工具 (pipeline/panel/iv_extensions.py), 供 shift-share 式识别与稳健性交叉; Bartik 类工具的识别机理与诊断可参 Goldsmith-Pinkham 等 (2020) 的系统梳理。关于工具变量在弱工具且聚类数少情形下的推断, 本项目稳健性 battery 采用 Wang & Zhang (2024) 的弱工具野自助 (wild bootstrap) 推断以及 MacKinnon-Webb 传统的聚类野自助, 避免在少省份聚类下依赖渐近正态的过度自信。须把识别的三个技术支点逐一说清。第一是聚类层级的选择: 二阶段的标准误在 target_bank 层聚类, 而工具的构造却是省级分组, 二者层级不同并不矛盾——省级留一均值是"生成外生变异的机制层级", 银行是"观测与残差相关性的最细层级"; 若担心同省残差相关 (省级共同冲击残留在结果方程扰动项中), 可把聚类层级抬到省级做稳健性, 但省份数偏少时聚类渐近失效, 此时正是 Wang & Zhang (2024) 弱工具野自助与 MacKinnon-Webb 少聚类野自助的用武之地。第二是第一阶段力度的报告纪律: 主表须报以 target_bank 聚类为准的有效 F (effective F, Montiel Olea-Pflueger 意义), 而非仅报非稳健的 Cragg-Donald F, 因为在聚类与异方差下后者会系统性高估工具力度; 当有效 F 落在弱工具阈值附近时, 二阶段系数须以弱工具稳健置信区间 (Anderson-Rubin 或其野自助版本) 而非 Wald 型区间报告。第三是 LATE 的解读: 在异质处理效应下, 本工具识别的是"其语调对省内本地媒体生态共同冲击有响应"那部分银行 (complier) 的局部平均处理效应, 而非全样本 ATE; 单调性假设 (同省舆论转暖不会使任一银行自身语调反向变冷) 是 LATE 解读的前提, 生产口径认为在媒体生态共同冲击下该假设大体温和成立, 但手稿须点明这一局部性, 不可把 IV 系数直接当作全样本因果效应外推。此外, 本工具与广义 Bartik 移动份额工具的识别哲学存在互补: Bartik 类工具把识别力寄托在"份额外生"或"冲击外生"二者之一 (Goldsmith-Pinkham 等 2020 的分解), 而留一语调工具把识别力寄托在"同省邻居语调只经本银行语调唯一通道起作用"这一排他性; 二者变异来源不同, 因此并联进入过度识别检验时, Hansen J 不拒绝可被读作对两套排他性同时成立的联合支持, 但 J 检验低功效的固有局限也须一并披露, 不可把"J 不拒绝"当成排他性的证明。

【与相邻测度的构念区分】
须严格区分本家族与三类相邻测度。其一, 与底层 llm_vote_tone{track} 的区分: 后者是本银行自身被报道的语调 (潜在内生的处理变量), 前者是同省他行语调的留一均值 (外生工具), 二者标度同源但角色相反, 严禁在同一回归中把工具当处理或反之。其二, 与城市级同名工具 city_leave1out_tone{track} 的区分: 分组粒度不同 (省 vs 市), 省级组更大、邻居更多、留一均值更平滑但地理相关性更弱, 市级组更小、更贴近本地媒体但更易触发单银行退化置 NaN; 两粒度是并列的替代工具而非嵌套。其三, 与媒体关注度工具 ft_attn_prov/city 的区分已如上述, 一为情感溢出、一为关注强度。此外须澄清: 本工具的地理是"银行注册地省份", 不是"报道发生地省份", 故它度量的是同注册地同业的舆论共振, 与媒体来源地暴露正交。其四, 与"同组 leave-one-out peer 均值" (leave_one_out_peer_*_iv, iv_extensions.py) 的区分: 后者的分组维度可以是行业/规模等非地理同类组, 前者严格以省份为分组维度, 二者虽同属留一均值构造范式但组定义不同, 承载的共同外生冲击也不同 (行业性冲击 vs 地方媒体生态冲击), 属并列而非重复的工具, 严禁把不同分组维度的留一工具当同一工具复用。其五, 与情感的其他聚合变体 (词典消融梯度、政治词权重梯度、BERT 分布形状族) 的区分: 那些是对"语调如何测量"的稳健性梯子, 作用在底层测度层; 本工具是对"语调如何被外生化"的识别构造, 作用在面板聚合层, 两层正交, 不可混谈——一个回答"这个语调数字可信吗", 一个回答"这个语调数字能不能当因果处理"。须再强调本家族与底层处理变量共享标度这一点极易被误用: 因为 prov_leave1out_tone{track} 与 llm_vote_tone{track} 都落在约 [-1,1] 且量纲相同, 描述统计里二者均值、方差看上去近似, 使用者极易在建模时误把工具列直接当作又一个情感控制变量塞进结果方程的右手边——这会同时破坏排他性 (工具进了结果方程) 并使二阶段失去识别, 属最严重的误用, 必须以变量标签与本节明文双重防范。最后须区分本工具与"银行自身滞后语调"这一时间维度工具: 本家族是同期横截面的省内他行均值 (空间溢出), 与用 llm_vote_tone{track} 的一阶滞后做工具 (时间外生性) 是两条不同的识别路径, 前者依赖地理共同冲击、后者依赖预定性 (predeterminedness), 变异来源与失效条件都不同, 不可互相替代。

【已知局限与稳健性梯子】
最核心的局限是反射问题 (reflection problem)。Manski (1993) 证明在线性均值模型下, 同期组均值 (本留一 IV 正属此类) 与个体结果不可分离识别; Bramoullé 等 (2009) 给出的网络识别条件要求组内存在非传递三元组, 而同省/同城分组是完全图 (组内两两相连), 恰不满足该条件。因此这两文对本工具而言是识别威胁与限定条件, 而非支撑性引用——项目日志与手稿必须如实披露此点: 决不能反向援引 Manski (1993) 或 Bramoullé 等 (2009) 为本工具背书, 因为二者恰恰指出同期完全图组均值的识别困难。本工具的排他性辩护只能建立在一条制度性 (而非统计可证) 的实体机制论证之上: 省级媒体生态 (地方报纸选题偏好、宣传口径、区域金融叙事的冷热) 是一股独立于本银行经营基本面、笼罩全省同业的共同外生环境, 它把相关性注入邻居语调与本银行语调之间, 而邻居银行被如何报道一般并不由本银行当年的具体决策所决定——只有当这一"媒体生态独立于共同基本面地驱动语调"的实体判断在制度层面站得住, 排他性才近似成立。此论证是研究者对本地媒体制度的实质性判断, 不依赖任何单篇文献背书, 也无法由第一阶段相关性显著来证明; 手稿须把它作为一条需要明确辩护并接受质疑的假设如实陈述, 而非当作已被引用文献确证的结论 (代码注释与生产日志已按此勘误, 剔除了将此辩护挂靠于经核验注册表之外文献的旧表述)。第二类局限是弱工具风险: 当省内银行数偏少或本地媒体生态异质性高时第一阶段偏弱, 须以有效 F 统计量诊断并配合弱工具稳健推断 (Wang & Zhang 2024)。第三类是退化: 在开发期 T=2 的浅面板上, 许多省-年单元仅一家银行有效, 工具大面积置 NaN 属预期; 生产 T=18 深面板上覆盖显著改善。稳健性梯子横跨三个维度且各自并排、互为稳健性、不分主次: ① 三轨 full / ctx / ss——留一均值分别在三条文本轨的底层语调上重算, 各轨各自 just-identified 并排, 严禁把不同轨的工具混进同一 over-identified Hansen J; ② 地理粒度 省 / 市 两层同理并列; ③ 与关注度工具 ft_attn 的过度识别交叉检验则是刻意设计的 over-id, 用来检验排他性而非堆工具冲显著性。留篇门控与底层语调一致采用 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科语料只看 llm_verified_full, ctx/ss 轨降为 conditional-on-full 的条件测度, 故三轨的样本宇宙存在包含关系而非独立子样本, 解读工具时须记住 ss 轨行宇宙是 full 留篇集的子集。须补充第四类实践层面的局限与相应处置。其一是地理匹配的时点问题: 银行注册地省份取自静态字典, 若样本期内银行迁址或重组, 静态省份会引入错分, 生产口径以主要样本期的稳定注册地为准, 迁址稀有故影响有限, 但在解读极少数迁址银行时须留意。其二是省份边界与媒体市场边界并不完全重合: 省级行政区未必等同于媒体覆盖的自然边界, 跨省的全国性财经媒体与省内地方媒体混合作用, 使"省级本地媒体生态"是一个近似; 城市级工具在这一点上更贴合本地媒体市场, 故省/市两粒度并列本身即是对"何为恰当地理聚合尺度"这一不确定性的稳健性检验。其三是零新闻银行的选择性: 当年无任何新闻的银行 tone 为 NaN, 既不进入邻居分组也自身无工具值, 若"是否被报道"本身与银行特征系统相关, 则有效子样本存在选择, 须在稳健性中检查零覆盖指示变量 (zero_coverage) 与主结果的关系。其四是与面板其他情感度量的正交性维护: 本工具族与词典消融梯度、政治词权重梯度、BERT 分布形状族等在构念上正交, 各梯子间不交叉, 严禁把不同族的变体混进同一过度识别式冲显著性——这与三轨、双层地理粒度、以及与关注度工具交叉的纪律是同一条铁律的不同侧面: 凡并排的稳健性轨各自 just-identified, 只有变异来源确实正交、旨在检验排他性的工具组合才允许进入刻意的 over-identified Hansen J。其五是"同省共同基本面冲击"这一排他性最尖锐的威胁: 若同省银行不仅共享媒体生态、还共享地方经济基本面 (本地经济景气、地方政府隐性担保、区域房地产周期), 那么同省邻居语调之所以与本银行结果相关, 可能并非只经"本银行语调"通道, 而是直接经"共同基本面"这条旁路——这会直接违反排他性。处置上必须在结果方程尽力吸收共同基本面: 生产设定以 year 固定效应吸收全国性年度冲击、以 target_bank 固定效应吸收银行时不变异质性, 稳健性上可加省×年固定效应或省级时变经济控制 (地区 GDP 增速、地方财政等财务面板到位后接入) 以尽量清洗掉基本面旁路, 但须诚实承认固定效应无法吸收"省内时变且与语调正交于基本面之外"的残余, 故排他性始终是一个需要制度性论证 (媒体生态确实独立于基本面地驱动语调) 而非纯统计可证的假设。其六是聚合尺度的内生边界: 用省而非市或城市群作为"本地媒体生态"的操作化边界本身是一个建模选择, 若真实的媒体市场边界与行政省界系统性错位, 则工具会系统性地测量偏误 (attenuation), 省/市两粒度并列正是对这一尺度不确定性的直接稳健性检验, 但两粒度都错位的可能性无法被并列检验排除。其七是三轨样本宇宙的包含关系对稳健性解读的约束: 因 ctx/ss 是 full 的 conditional-on-full 子集 (2026-06-29 full-only 门控), 三轨结果的一致并不能等同于三个独立样本的一致——ss 轨的"稳健"部分继承自它是 full 子集这一事实, 故三轨一致是"同一留篇宇宙下不同文本视野的一致", 而非"不同样本的独立复现", 手稿在把三轨并列呈现为稳健性时须准确交代这层嵌套, 避免夸大为独立重复检验。综合以上, 本工具的可信度是一个需要机制论证、诊断报告与稳健性梯子三者共同支撑的整体, 单看第一阶段相关性显著远不足以宣称因果, 排他性的实体辩护 (本地媒体生态独立驱动语调) 才是识别的真正承重墙。

语调测量本身的效度另有独立文献支撑: 媒体语调影响资产定价的传统由 Tetlock (2007) 奠基, 中文语境下官方媒体语调的市场相关性见 Xu 等 (2025) 与 Fang 等 (2024, 银行级), 银行融资条件的语调移动可参 Marchetti 等 (2025); 语调对存款侧稳定性与银行脆弱性的实际后果 (信息的真实效应) 则由 Goldstein (2023)、Chen 等 (2022)、Drechsler 等 (2026)、Cookson 等 (2026) 一线刻画, 为本工具下游结果变量的经济学意义提供锚点。底层语调的测量方法学 (词典与机器学习) 分别由 Du 等 (2022, 中文金融词典)、Huang 等 (2023, FinBERT) 与 Cookson 等 (2024) 代表; 多重检验的族错误率控制采用 Romano & Wolf (2005) 的逐步法, 以防在三轨、双层地理粒度与多结果变量的组合下因反复检验而虚增显著性。综上, 本家族既是所属论文因果识别的承重工具, 也是一组结构清晰、退化处理严谨、稳健性梯子交代完备、且与相邻测度构念边界分明的省级情感溢出工具变量家族。

## VAR: prov_leave1out_tone_full

【变体差分】
本列是家族 canonical 与所属论文 bank_fintech_tone 识别策略的主工具变量 (tier=core), 底层聚合的是 full 轨语调 llm_vote_tone_full——即"标题 prepend + 全文正文"文本轨上三家 LLM (gpt54nano / gemini31 / deepseekv4) 的多数投票共识语调。相对家族其余两列, 本列的差分维度是文本轨=full: full 轨对应最宽的报道文本视野, 亦是 2026-06-29 起 full-only 留篇门控的判定轨——一篇报道是否被计为"一篇银行金科报道"只看 llm_verified_full, 因此 full 轨的银行-年度语调覆盖是三轨中最完整的, 省内有效邻居数最多、留一均值最稳, 单银行退化置 NaN 的比例最低。这也是它被 paper_spec identification.iv 选作主工具 (primary) 而非 fallback 的技术原因: 覆盖最全、第一阶段相关性最强, 在浅面板上单银行省-年退化置 NaN 的比例最低, 故有效工具观测数在三轨中最多, 第一阶段有效 F 通常也最高。之所以由"三家 LLM 多数投票共识"而非单一模型或词典分数作底层, 是因为共识对单模型的系统偏误更稳健, 相当于对语调测量本身做了一层跨厂商的降噪, 这一点承接了 Huang 等 (2023) 关于机器学习优于词典法抽取金融文本信息、以及项目内 LLM/词典/BERT 三法互为稳健性的整体设计。生产二阶段的规范设定为 ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) X, absorb(target_bank year) cluster(target_bank), 即用它工具化本银行 full 轨内生语调。使用铁律: 本列与同族的 prov_leave1out_tone_ctx / prov_leave1out_tone_ss 是三条并排、互为稳健性、不分主次的工具轨, 各自 just-identified 单独进第一阶段, 严禁把三轨工具塞进同一 over-identified Hansen J 制造虚假过度识别; 与之相对, 本列可与"媒体关注度"族工具 ft_attn_prov (变异来源正交) 并联做刻意的 over-id, 用以检验排他性约束。同时须区分本列 (外生工具) 与被它工具化的 llm_vote_tone_full (潜在内生处理变量): 二者同标度但角色相反, 不可混用。省级粒度意味着邻居集大而平滑, 与城市级 city_leave1out_tone_full 构成并列 (非嵌套) 的替代地理工具; 省级组邻居更多故留一均值方差更小、对个别极端邻居更不敏感, 但地理相关性 (本地媒体生态的共享强度) 往往弱于同城, 因此省级与城市级两个粒度在第一阶段力度与排他性可信度上各有取舍, 属并列稳健性检验而非孰优孰劣。取值在生产 T=18 深面板上覆盖良好, 而在开发 T=2 浅面板上因单银行省-年退化而大面积 NaN, 属预期而非缺陷。作为主工具, 本列在手稿披露中必须如实交代反射问题这一识别限定: 同省组是完全图, 其组均值型工具落在 Manski (1993) 不可识别的情形内, 决不能反向援引 Manski/Bramoullé 为工具背书; 本列排他性的辩护只能建立在一条制度性实体机制论证上——省级媒体生态独立于本银行基本面地共同驱动同省同业语调, 而邻居语调不经由本银行决策产生——这是研究者对媒体制度的实质判断、须作为受质疑的假设如实陈述, 不依赖任何单篇文献背书; 弱工具与少聚类下的推断则以有效 F 诊断并配合 Wang & Zhang (2024) 的弱工具野自助。本列亦是与 ft_attn_prov 做 Hansen 过度识别交叉检验时的一支——二者变异来源正交 (情感溢出 vs 关注强度), 该 over-id 的目的在检验排他性约束是否同时成立, 而非用堆工具的方式去冲高显著性。作为主工具, 本列的报告规范是: 先报第一阶段有效 F 与工具系数符号 (应与"本地媒体生态共同冲击"预期一致为正相关), 再报二阶段结构系数, 最后以 ctx/ss 两轨与城市级同名工具作并排稳健性、以 ft_attn 交叉作过度识别诊断, 全程配弱工具稳健推断。

## VAR: prov_leave1out_tone_ctx

【变体差分】
本列 (tier=standard) 与 canonical 的唯一差分维度是文本轨=ctx: 底层聚合的是 llm_vote_tone_ctx, 即"标题 prepend + 实体上下文窗口"文本轨上三家 LLM 多数投票共识语调; 留一构造、省级分组、剔除自身、单银行置 NaN 的算法与 full 列逐字节相同, 只是被聚合的底层语调换成 ctx 轨。ctx 轨把报道正文裁剪到银行/金科实体附近的上下文窗口, 相对 full 轨更聚焦于与银行金科直接相关的语句, 剥离了全文中与主体无关的段落噪声, 因而它是 full 轨的一条并排稳健性工具轨——若主结果只在 full 轨成立而在 ctx 轨崩塌, 说明识别可能被无关文本的语调污染。在 full-only 留篇门控 (2026-06-29) 下, ctx 轨是 conditional-on-full 的条件测度: 其行宇宙是 full 留篇集的子集, per-track 语调照算但只在被 full 判定留篇的银行-年度上取值, 故 ctx 工具的省内有效邻居数通常略少于 full, 单银行退化置 NaN 的比例略高。使用铁律与家族一致: 本列与 prov_leave1out_tone_full / prov_leave1out_tone_ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 与城市级同轨工具 city_leave1out_tone_ctx 构成并列替代粒度。同样须区分本列 (外生工具) 与 llm_vote_tone_ctx (潜在内生处理变量) 的相反角色, 不可互换。ctx 轨在识别上的价值在于它提供了一条"排除全文无关文本污染"的稳健性: full 轨的语调可能被报道中与银行金科主体无关的段落 (如宏观时评、其他机构消息) 的情绪带偏, 若这种带偏在同省银行间同向, 会同时进入工具与潜在处理而威胁排他性; ctx 轨把文本收窄到实体上下文窗口后, 这类无关污染被显著削弱, 因而"主结果在 full 轨成立且在 ctx 轨依然成立"比"仅 full 轨成立"是更强的证据。反过来, 若 ctx 轨工具的第一阶段力度明显弱于 full 轨, 通常是覆盖收缩 (条件测度子样本更小) 所致, 须结合 n_valid 与 singleton 计数判读而非直接判定工具失效。

## VAR: prov_leave1out_tone_ss

【变体差分】
本列 (tier=standard) 与 canonical 的差分维度是文本轨=ss: 底层聚合的是 llm_vote_tone_ss, 即"标题 prepend + 银行∧金科同句 ±N 窗"文本轨 (窗半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 上三家 LLM 多数投票共识语调; 留一算法、省级分组、剔除自身、单银行置 NaN 与 full/ctx 完全一致, 差异只在底层语调轨。ss 轨是三轨中最严格的语义轨: 只保留银行实体与金科词落在同一句 (或相邻窗) 内的共现语境, 因而它捕获的是"银行与金融科技被直接并置论述"时的语调, 剥离了银行与金科各自零散出现但并未同框的段落。回退语义须按 CLAUDE.md 口径记牢: ss 轨镜像 ctx——当某报道无银行∧金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback=True (与 n_articles 共享分母); 当 FINTECH_AC=None 时 *_is_fallback 全 True 优雅降级。在 full-only 门控下 ss 轨同为 conditional-on-full 条件测度, 行宇宙是 full 留篇集的子集, 故 ss 工具的省内有效邻居通常最稀疏, 单银行退化置 NaN 比例在三轨中往往最高, 在开发期 T=2 浅面板上尤易大面积缺失。使用铁律不变: 本列与 prov_leave1out_tone_full / prov_leave1out_tone_ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 与 city_leave1out_tone_ss 并列为替代粒度; 本列 (外生工具) 与 llm_vote_tone_ss (潜在内生处理变量) 角色相反不可混用。ss 轨在识别上是三轨中语义最纯的稳健性臂: 它只在银行与金融科技被直接并置论述的语境下取语调, 因而最贴近论文关切的"银行金科叙事"这一构念本身, 若主结果在如此严格的语义轨上仍然成立, 对"效应确由银行金科相关舆论驱动、而非泛泛的银行报道情绪"这一因果解释是最有力的支撑。代价是覆盖最稀疏、退化置 NaN 最多, 故 ss 轨工具在浅面板上第一阶段常偏弱, 解读须格外谨慎、优先以其作为方向一致性的佐证而非独立主识别。须再次记牢回退口径与 full-only 门控: ss 无同句共现时回退全文 body 并标记 ss_is_fallback, 门控判定仍只看 full 轨, ss 行宇宙是 full 留篇集子集; 三轨工具各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Drechsler, I., Savov, A., Schnabl, P., & Wang, O. (2026). Deposit franchise runs. The Journal of Finance, 81(3), 1573-1617. https://doi.org/10.1111/jofi.70034
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, 112803. https://doi.org/10.1016/j.econlet.2025.112803
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review, 64, 101234. https://doi.org/10.1016/j.ememar.2024.101234
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Goldstein, I. (2023). Information in financial markets and its real effects. Review of Finance, 27(1), 1-32. https://doi.org/10.1093/rof/rfac052
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
<!-- rendered-citations:end -->
