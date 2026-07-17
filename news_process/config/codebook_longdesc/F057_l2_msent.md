---
family_id: F057
columns:
- avg_msent_ctx
- avg_msent_ctx_z
- avg_msent_full
- avg_msent_full_z
- avg_msent_ss
- avg_msent_ss_z
- avg_msent_std_ctx
- avg_msent_std_full
- avg_msent_std_ss
unit: 无量纲计数型极性得分 (msent 逐篇取值域约 [-1,1], 越大越负面); avg 与 std 沿用同量纲; _z 为年度截面标准差单位
formula: "msent_score{t} = (neg_count - pos_count) / (pos_count + neg_count) [固定 6 词典 union 词表, 零语言学规则]; avg_msent{t} = mean_{bank-year}(msent_score{t}); avg_msent_std{t} = std_{bank-year}(msent_score{t}); avg_msent{t}_z = 年度截面内对 avg_msent{t} 做 (x-μ_year)/σ_year"
producer: news_process/pipeline/sentiment/tone_words.py (msent_score 逐篇) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (avg/std bank-year 聚合) ; news_process/pipeline/panel/geography.py::standardize_panel_variables (_z 年度截面标准化)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 22_tone_words.parquet (msent_score_full / msent_score_ctx / msent_score_ss)
- 40_panel_yearly.parquet (bank-year 聚合与 _z 标准化落地)
citations:
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1086/260061
  type: journal
  authors: Fama, E. F., & MacBeth, J. D.
  year: 1973
  title: "Risk, return, and equilibrium: Empirical tests"
  venue: Journal of Political Economy
  vol: 81
  issue: 3
  pages_or_artno: 607-636
- doi: "10.1016/j.jbankfin.2025.107542"
  type: "journal"
  authors: "Lehkonen, H., Heimonen, K., & Pukthuanthong, K."
  year: 2025
  title: "Media tone is a priced risk factor in currency markets"
  venue: "Journal of Banking & Finance"
  vol: "180"
  pages_or_artno: "107542"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
- doi: "10.1016/j.iref.2024.103745"
  type: "journal"
  authors: "Bai, C., Duan, Y., & Goodell, J. W."
  year: 2025
  title: "Multi-media sentiment to systemic risk: Evidence from COVID-19"
  venue: "International Review of Economics & Finance"
  vol: "97"
  pages_or_artno: "103745"
- doi: "10.1111/acfi.13353"
  type: "journal"
  authors: "Kanagaretnam, K., Li, W., Shi, G., & Zhou, Z."
  year: 2025
  title: "Ambiguity of tone in annual reports and bank risk taking"
  venue: "Accounting & Finance"
  vol: "65"
  issue: "1"
  pages_or_artno: "935-970"
new_dois:
- 10.1016/j.jeconom.2020.07.053
- 10.1086/260061
---

## CORE

【构念与来源】
本家族刻画的是同一个底层构念在银行—年度面板上的三种呈现: 计数型媒体情感极性 (msent, machine sentiment 的缩写) 的年内均值、年内离散度, 以及年度截面标准化值。msent 是词典法情感测度里最朴素、最贴近经典文本经济学原型的一档: 它只数一篇报道里落入正面词集与负面词集的词条个数, 用差与和之比构造一个介于约负一到正一之间的极性标量, 完全不施加否定、程度副词、转折连词等任何语言学规则。其定义为 msent = (负面词数 − 正面词数) / (正面词数 + 负面词数), 因此取值越大代表整篇报道越偏负面, 方向与日常直觉相反, 这一符号约定在下游一切消费该列的回归模板与图表里都必须显式说明, 以免误读系数正负。之所以保留这样一档"零规则"的纯词频测度, 是要在项目已有的全规则词典得分 (施加否定翻转、六级程度权重、转折增强的 dict_avg_tone) 与仅否定档 (negonly) 之外, 补齐 ablation 谱系最朴素的一端, 使得整条"零规则计数 → 仅否定 → 全规则"的三点谱可以完整地对情感测度做稳健性对照。

【方法学与计算】
计数基采用固定的六词典 union 词表, 而非"逐篇匹配数最多的词典"。历史上旧实现按每篇报道挑选命中词条最多的那部词典来数正负面词, 这会让测量工具本身随观测漂移, 违反经典文本情感测度对固定词表的要求。现行口径在加载期把 jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran (即 Loughran and McDonald 2011 中文主译) 六部词典并集成一部固定 union 词典, 对跨类重叠词以正一负一的平衡双票喂入, 使极性 margin 守恒、union 词典逐位不变, 再在这部固定词表上数每篇报道的正负面词。空文本按缺失语义处理, msent 记为缺失值而非零, 与项目内可读性、清晰度、前瞻性语句等测度的空文本契约对称。逐篇 msent 落在 22_tone_words 阶段产出; 面板层在 encode 的聚合字典里对每个银行—年度单元取该单元内所有留篇报道 msent 的等权均值得到 avg_msent, 取其样本标准差得到 avg_msent_std; 年度截面标准化则在 geography 步骤对 avg_msent 逐年度把截面归一到零均值单位方差, 生成 _z 列并保留原始列不变。均值聚合自动跳过缺失值, 短文本或空文本不污染分母。

该家族严格沿用项目的三轨文本架构 (full / ctx / ss) 与 full-only 留篇门控口径 (2026-06-29)。full 轨文本为标题前置加全文正文; ctx 轨为标题加实体窗口; ss 轨为标题加银行与金融科技同句共现的窄窗, 且 ss 的回退语义镜像 ctx——当某篇报道不存在银行与金融科技的同句共现时, ss 文本退回全文正文并标记回退。行宇宙由 full 轨留篇集唯一确定, 一篇报道是否算作"银行金融科技报道"只看 full 轨 LLM 判定, ctx 与 ss 是 conditional-on-full 的测度轨与稳健性轨, 其 msent 列在 full 留篇集的子集上逐轨计算。需要厘清的是, 面板均值聚合并非以全局 n_articles 为固定分母, 而是对每个银行—年度单元内该轨 msent 非缺失的报道逐轨取等权均值 (encode 层 mean 聚合自动跳过缺失值), 因此 per-track 分母等于该轨实际有值的篇数, 未必严格等于由 full-only 留篇门控计得的 n_articles: n_articles 是 full 轨留篇集的篇数, 当某篇报道在 ctx 或 ss 轨因回退标记、空窗或空文本而缺失 msent 时, 该篇不进入本轨分母。CLAUDE.md 中"共享 n_articles 分母"一语专指 ss 回退语义下 ss 与 ctx 镜像同一留篇报道基这一层含义, 并不意味着三轨聚合分母逐位相等——三轨分母只在无任何轨内缺失的理想单元才恰好一致。三轨之间是各自 just-identified 并排、互为稳健性、不分主次的关系, 严禁把 full、ctx、ss 三轨的 msent 混进同一个 over-identified 的 Hansen J 过度识别检验; 这与项目内 co-primary 双轨嵌入、政治词权重梯度、规则消融梯度所遵循的同款铁律一致。计数口径 msent 刻意不进入规则消融梯度: 程度副词与转折连词在计数口径下是严格正的乘子、永不翻号, 对 (负面减正面) 除以 (正负面之和) 的比值零影响, 会使各规则消融变体全部退化, 因此 msent 口径仅由零规则的 msent_score 与仅否定的 msent_negonly 两档完整覆盖, 不再新增任何 msent 消融列。

【文献定位】
计数型词频情感测度的方法学原型可追溯到媒体文本与资产市场关系的经典研究。Tetlock (2007) 在顶级金融学期刊上用固定词表统计财经专栏中的悲观词频, 证明媒体语调对市场收益与成交量具有可度量的预测含量, 为本家族"数正负面词、构造极性标量"的做法提供了直接构念锚, 且其固定词表、不做复杂语言学处理的朴素做法恰是 msent 零规则口径要复刻的原型。测量层面, Shapiro, Sudhof and Wilson (2022) 系统讨论了新闻情感的测量误差如何通过衰减偏误 (attenuation bias) 把回归系数拉向零, 这为本家族同时保留 avg_msent 与其年内离散度 avg_msent_std、并对 avg_msent 做年度截面标准化提供了识别层面的依据: 离散度是测量噪声的直接刻画, 标准化则使系数可比。年度截面标准化本身的方法学出处是 Fama and MacBeth (1973) 的两阶段截面回归框架, 逐年度把核心回归变量归一到单位方差, 使斜率系数可直接解读为"一个标准差的情感变化对应因变量若干单位的变动"。三篇文献共同界定了 msent 从逐篇构造、到面板聚合、再到截面标准化的完整方法学链条。 在这三条经典锚点之外, 近期同域研究进一步印证了本家族的构造形态与应用场景。Lehkonen、Heimonen 与 Pukthuanthong (2025) 以覆盖全球逾两千家媒体与八百家社交站点的约七百万篇文本构造媒体语调, 证明以正负提及净额除以总提及构成的比率型语调是可跨截面定价货币的真实风险因子, 为 msent 所用「极性差除以极性和」这一比率形态提供了近期顶刊级的经济含义论证; 须同时写明其语调取自 Refinitiv MarketPsych 专有商业指数而非自建词表命中计数, 构造细节不可复核, 且其层级为货币-国别聚合、语料为英文国际财经新闻、因变量为汇率与货币收益的因子定价, 与本项目公开中文词典自建计数、银行×年聚合的口径在透明度与聚合结构上均不可直接比附。Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 表明把新闻情感按银行主体归集、进而进入银行层面实证, 是当前被顶级金融稳定期刊接受的做法, 锚定的正是本家族「逐篇 msent → 银行—年度均值」这一聚合环; 其语境为美国银行监管 (以监管评级与监管行动为因变量), 情感测度的构造细节与本项目六词典 union 及 (负面减正面) 除以 (正负面之和) 的归一化口径不同, 亦不涉及本项目的三轨文本与 LLM 投票设计。Bai、Duan 与 Goodell (2025) 用 2020 年二至四月来自官方新闻媒体、新浪微博与微信的约八百八十万条中文文本构造日度情感指数, 发现媒体情感上升经缓解存款人挤兑而降低系统性风险, 且渠道间情感分歧扩大会加剧系统性风险, 提供了「中文媒体情感测度进入银行体系风险实证」的近期同域证据; 但其情感指数是否为词表命中计数在可得材料中未见披露, 测度单元为日度指数而非按银行—年度对篇数取均值, 且其所谓「多源」指媒体渠道, 与本项目多词典 union、三文本轨的并排不是同一维度, 因此不可据以为本家族的词典并集或三轨并排设计背书。Kanagaretnam、Li、Shi 与 Zhou (2025) 以银行 10-K 文本的语调模糊度 (由分离混淆成分与信息成分的语调模型残差估计) 进入银行风险承担面板回归, 佐证银行文本的词表型语调测度可作为银行层面实证的解释变量; 其测度为残差化的模糊度指标, 并非本家族的比率式极性口径, 且每银行—年度仅一份年报文档, 与本家族逐篇计数后再取均值的分母结构不同, 因而亦不可把 avg_msent_std 的年内离散度构念等同于其模糊度指标。
## VAR: avg_msent_full

【变体差分】
本列是家族在 full 轨上的均值档, 也是 msent 家族在主线回归中最常用的 canonical 呈现。full 轨文本为标题前置加全文正文, 覆盖整篇报道的全部正负面词, 因而其分子分母的词条基数最大、单篇 msent 的采样噪声相对最低。取值为该银行—年度单元内所有 full 轨留篇报道 msent_score_full 的等权均值, 量纲与逐篇 msent 相同, 落在约负一到正一之间, 越大代表该银行当年的媒体报道整体越偏负面。作为 full 轨列, 它直接服务于 full-only 留篇门控下的行宇宙, 是 ctx 与 ss 两轨对应列的稳健性参照基准。与同家族 avg_msent_ctx / avg_msent_ss 相比, 三者唯一差异在文本轨道: 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨 msent 均值混入同一 over-identified Hansen J。与 avg_msent_full_z 相比, 本列是未标准化的原始均值, 保留了跨年度可比的绝对水平信息; 与 avg_msent_std_full 相比, 本列刻画的是中心趋势而非年内离散度。与全规则 dict_avg_tone 及仅否定 negonly 档相比, 本列是零语言学规则的纯计数极性, 构成三点 ablation 谱最朴素的一端, 且方向约定为越大越负面, 与 tone 类越大越正面的列符号相反。在实证使用上, 本列既可作为语调水平的主测度直接进入基线回归, 也可作为词典法内部的稳健性对照, 用以检验施加复杂语言学规则是否实质改变了媒体语调对因变量的解释力; 由于其计数口径最贴近 Tetlock (2007) 的固定词表原型, 它在方法学披露中承担"最保守、最少研究者自由度"的基准角色。

## VAR: avg_msent_ctx

【变体差分】
本列是家族在 ctx 轨上的均值档。ctx 轨文本为标题前置加实体窗口, 只保留目标银行实体附近的上下文, 而非整篇正文, 因此其正负面词基数窄于 full 轨, 单篇 msent 的采样噪声相对更高、在稀疏报道年份更易出现退化。取值为该银行—年度单元内所有留篇报道 ctx 轨 msent_score_ctx 的等权均值, 量纲与方向与 full 轨一致 (越大越负面)。它是 conditional-on-full 的测度轨: 行宇宙仍由 full 轨留篇集唯一确定, ctx 列只在这一子集上逐轨计算; 均值聚合以该单元内 ctx 轨 msent 非缺失的报道篇数为分母 (encode 层 mean 逐轨跳过缺失值), 因而本轨 per-track 分母是 ctx 轨实际有值的篇数, 未必严格等于 full-only 留篇门控计得的 n_articles——后者是 full 轨留篇集篇数, 当某篇在 ctx 轨因回退或空窗而缺失 msent 时不计入本轨分母。CLAUDE.md 里"共享 n_articles 分母"是 ss 回退语义下 ss 镜像 ctx 同一留篇报道基的措辞, 并非断言逐轨聚合分母逐位相等。与 avg_msent_full 的唯一区别是文本轨道由 full 收窄为实体窗口, 二者各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。与 avg_msent_ss 相比, ctx 用实体窗口而 ss 用银行与金融科技同句共现窄窗, 且 ss 回退语义正是镜像 ctx。相对 avg_msent_ctx_z, 本列是未标准化原始均值; 相对 avg_msent_std_ctx, 本列是中心趋势而非离散度。ctx 轨的价值在于把语调测度聚焦到与银行实体紧邻的语境, 剔除整篇报道中与该行无关段落的语调噪声, 作为 full 轨的规格稳健性对照。当一篇报道同时涉及多家银行或大段与目标行无关的行业综述时, full 轨会把这些段落的语调一并计入, 而 ctx 轨通过实体窗口只保留目标行紧邻文本, 从而更纯净地度量"针对这家银行"的媒体语调; 二者水平差异本身即可作为语境敏感性的诊断信号。

## VAR: avg_msent_ss

【变体差分】
本列是家族在 ss 轨 (sentence-scoped, 银行与金融科技同句共现轨) 上的均值档, 是三轨中语境最窄、判据最严的一档。ss 轨文本为标题前置加银行与金融科技处于同一句内共现的窄窗 (窗口半径由配置项 ss_sentence_radius 控制, 默认为一句), 目的是把情感测度锁定到"这家银行确实在谈金融科技"的语境, 剔除银行与金融科技各自出现但语义无关的段落。其回退语义严格镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 退回全文正文并将回退标记置真, 与 ctx 轨遵循同一条回退公理。取值为该银行—年度单元内所有留篇报道 ss 轨 msent_score_ss 的等权均值, 量纲与方向与 full 轨一致 (越大越负面)。作为 conditional-on-full 的稳健性轨, 其行宇宙由 full 留篇集唯一确定, 在稀疏语料或短面板 (如 T=2 开发态) 上 ss 轨极易出现零方差或大面积缺失的预期退化, 均值聚合按缺失跳过, 不污染分母。与 avg_msent_full / avg_msent_ctx 相比, 唯一差异是文本轨道判据最严, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。相对 avg_msent_ss_z 为未标准化原始均值, 相对 avg_msent_std_ss 为中心趋势而非离散度。ss 轨的方法学价值在于把"银行是否被媒体与金融科技一并讨论"这一处理相关的构念与语调测度绑定在同一句语境内, 因而当主结论在 full 轨成立、在 ss 最窄语境仍不反号时, 可为语调渠道提供最强的规格稳健性支撑。

## VAR: avg_msent_full_z

【变体差分】
本列是 avg_msent_full 的年度截面标准化版本, 后缀 _z 表示在每个年度截面内把该变量归一到零均值、单位方差。标准化仅对有新闻覆盖的银行—年度行 (n_articles 大于零) 执行, 逐年度分组后减去当年截面均值再除以当年截面标准差, 零新闻行保持缺失; 白名单守卫要求当年有效观测不少于阈值方才生成, 否则该轨判入跳过。生成时保留原始 avg_msent_full 列不动, _z 为并列新增列。它区别于家族其余列的核心在于施加了 Fama and MacBeth (1973) 式的年内截面标准化: 标准化后系数可直接解读为"该银行媒体负面语调相对当年同业高出一个标准差, 对应因变量若干单位的变动", 消除了不同年份 msent 绝对水平漂移 (例如宏观事件年份整体语调偏负) 对跨年度可比性的干扰。量纲由 msent 的极性单位转为标准差单位, 方向仍为越大越负面。与 avg_msent_full 相比, 本列牺牲了绝对水平信息换取截面可比性; 与 avg_msent_ctx_z / avg_msent_ss_z 相比, 三者仅文本轨道不同, 同样各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。注意标准化白名单只覆盖 avg_msent 的三轨均值列, 并不对 avg_msent_std 生成 _z 孪生列。因此在需要跨年度可比语调水平的两阶段截面回归或多年份合并样本中, 本列往往比未标准化的 avg_msent_full 更适合直接进入右手边, 而绝对水平研究则应回用未标准化列。

## VAR: avg_msent_ctx_z

【变体差分】
本列是 avg_msent_ctx 的年度截面标准化版本, 标准化机制与 avg_msent_full_z 完全一致——在每个年度截面内对有新闻覆盖行做零均值单位方差归一, 逐年度减截面均值除截面标准差, 零新闻行保持缺失, 原始 avg_msent_ctx 列保留不动。它与 avg_msent_full_z 的唯一区别是被标准化的底层均值来自 ctx 轨 (标题加实体窗口) 而非 full 轨: 因此本列先继承了 ctx 轨"聚焦银行实体紧邻语境、剔除无关段落语调"的窄窗特性, 再叠加 Fama and MacBeth (1973) 式截面标准化带来的跨年度可比性。量纲为标准差单位, 方向越大越负面。由于 ctx 轨词条基数窄于 full, 在稀疏年份其年内截面标准差可能偏小甚至退化, 标准化守卫的有效观测阈值 (不少于十) 会把观测不足的年份轨判入跳过, 属预期行为而非缺陷。与 avg_msent_ctx 相比, 本列以绝对水平换取截面可比; 与 avg_msent_full_z / avg_msent_ss_z 相比仅文本轨道不同, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列亦不派生离散度孪生列, avg_msent_std_ctx 与本列分别刻画离散度与标准化中心趋势, 两者不可互代。实务上本列常作为 avg_msent_full_z 的语境收窄稳健性对照: 若主结论在 full 标准化轨成立而在 ctx 标准化轨方向一致, 则说明结果并非由与目标行无关的整篇报道语调驱动, 而是来自紧邻银行实体的语境。

## VAR: avg_msent_ss_z

【变体差分】
本列是 avg_msent_ss 的年度截面标准化版本, 标准化机制与其余两条 _z 列一致: 逐年度对有新闻覆盖行归一到零均值单位方差, 零新闻行保持缺失, 保留原始 avg_msent_ss 列。它与 avg_msent_full_z / avg_msent_ctx_z 的唯一区别是底层均值取自 ss 轨 (银行与金融科技同句共现窄窗, 回退语义镜像 ctx), 因此本列同时继承了三轨中判据最严、语境最窄的特性与截面标准化带来的可比性。量纲为标准差单位, 方向越大越负面。ss 轨在稀疏语料上最易出现零方差或大面积缺失: 一旦某年度截面有效观测不足阈值, 标准化守卫会把该轨该年判入跳过 (在 T=2 开发态尤为常见), 这是 conditional-on-full 稳健性轨的预期退化, 不影响 full 与 ctx 轨的标准化。作为 Fama and MacBeth (1973) 框架下最严判据轨的标准化呈现, 本列主要用于检验主结论在"确证银行谈金融科技"的最窄语境下是否稳健。与 avg_msent_ss 相比以绝对水平换截面可比; 与另两条 _z 列仅文本轨道不同, 三者各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。由于 ss 轨在开发态短面板上年内截面标准差常不足以支撑标准化, 本列的有效覆盖通常远稀于 full 与 ctx 的 _z 列, 因而它更适合在生产态长面板上作为语调渠道在最严语境下的最终稳健性锚, 而非基线主回归的常规右手边变量; 与 avg_msent_std_ss 相比, 本列刻画的是标准化后的中心趋势而非语调离散度, 二者构念正交、不可互代。

## VAR: avg_msent_std_full

【变体差分】
本列是 full 轨 msent 的年内离散度档, 取该银行—年度单元内所有 full 轨留篇报道 msent_score_full 的样本标准差, 而非均值。它刻画的不是该行当年语调偏正还是偏负, 而是当年围绕该行的媒体报道在语调上的分歧程度或波动程度: 标准差越大, 说明该行当年既有明显偏正也有明显偏负的报道并存, 语调越不一致。这一离散度在识别层面有直接用途——按 Shapiro, Sudhof and Wilson (2022) 的论证, 情感测度的年内离散度是测量噪声与语调异质性的直接刻画, 可用于诊断均值型语调变量的衰减偏误强度, 或作为语调分歧的构念本身进入异质性分析。量纲与 msent 相同 (标准差以极性单位计)。与 avg_msent_full 相比, 二者共享同一底层逐篇 msent 序列, 但一取中心趋势一取二阶矩, 刻画的构念正交, 回归中可并列进入而不互代。与 avg_msent_std_ctx / avg_msent_std_ss 相比, 三者仅文本轨道不同, 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。需注意标准化白名单不覆盖离散度列, 故本列没有 _z 孪生列; 在单元内报道数为一时样本标准差未定义, 记为缺失。作为 full 轨的离散度呈现, 本列词条基数最大、逐篇 msent 采样噪声最低, 因而在三条离散度列中最稳定、最少退化, 通常作为语调分歧构念的主测度, 其余两轨离散度列作为语境收窄的稳健性对照。

## VAR: avg_msent_std_ctx

【变体差分】
本列是 ctx 轨 msent 的年内离散度档, 取该银行—年度单元内所有留篇报道 ctx 轨 msent_score_ctx 的样本标准差。与 avg_msent_std_full 的唯一区别是底层逐篇序列取自 ctx 轨 (标题加实体窗口) 而非 full 轨: 因此本列刻画的是"聚焦银行实体紧邻语境后"的语调分歧程度。由于 ctx 轨词条基数窄于 full, 单篇 msent 采样噪声更高, 其年内标准差在稀疏报道单元更易偏大或因单篇/空缺而退化为缺失。量纲与 msent 相同, 语义为语调离散度而非水平。作为 conditional-on-full 的测度轨, 行宇宙由 full 留篇集唯一确定, ctx 离散度只在该子集上逐轨计算。与 avg_msent_ctx 相比, 二者共享同一底层逐篇序列但分取二阶矩与一阶矩, 构念正交, 可并列进入回归; 与 avg_msent_std_full / avg_msent_std_ss 相比仅文本轨道不同, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列同样没有 _z 孪生列 (标准化白名单只含 avg_msent 三轨均值), 且单元内报道数为一时标准差未定义、记缺失; 这些退化在短面板开发态属预期, 不视为缺陷。相较 avg_msent_std_full, 本列以更纯净的实体语境换取更高的采样噪声与更强的退化倾向, 二者共同界定了"整篇 vs 实体窗口"两种语调分歧口径的稳健性区间。

## VAR: avg_msent_std_ss

【变体差分】
本列是 ss 轨 msent 的年内离散度档, 取该银行—年度单元内所有留篇报道 ss 轨 msent_score_ss 的样本标准差, 是三条离散度列中判据最严、最易退化的一条。ss 轨文本为标题加银行与金融科技同句共现窄窗, 回退语义镜像 ctx; 其逐篇 msent 序列本已语境最窄、样本最稀, 再取二阶矩使得本列在稀疏语料或短面板 (如 T=2 开发态) 上极易因单元内有效报道不足两篇而无法定义标准差、记为缺失, 或呈零方差退化。这属于 conditional-on-full 最严判据轨的预期行为, 不影响 full 与 ctx 轨的离散度。语义上, 本列刻画的是"确证银行谈金融科技"这一最窄语境内媒体语调的分歧程度, 量纲与 msent 相同。与 avg_msent_ss 相比, 二者共享同一底层逐篇序列而分取离散度与中心趋势, 构念正交可并列进入回归; 与 avg_msent_std_full / avg_msent_std_ctx 相比仅文本轨道不同, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列亦无 _z 孪生列, 且标准差在单元报道数不足两篇时未定义, 与家族其余离散度列的缺失契约一致。因此本列主要用于在生产态长面板上检验"确证银行谈金融科技"最窄语境内的语调分歧是否与全篇口径一致, 在短面板开发态则常大面积缺失, 属预期退化而非数据缺陷。

<!-- rendered-citations:begin -->
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fama, E. F., & MacBeth, J. D. (1973). Risk, return, and equilibrium: Empirical tests. Journal of Political Economy, 81(3), 607-636. https://doi.org/10.1086/260061
Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
Bai, C., Duan, Y., & Goodell, J. W. (2025). Multi-media sentiment to systemic risk: Evidence from COVID-19. International Review of Economics & Finance, 97, 103745. https://doi.org/10.1016/j.iref.2024.103745
Kanagaretnam, K., Li, W., Shi, G., & Zhou, Z. (2025). Ambiguity of tone in annual reports and bank risk taking. Accounting & Finance, 65(1), 935-970. https://doi.org/10.1111/acfi.13353
<!-- rendered-citations:end -->
