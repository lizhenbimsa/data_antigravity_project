---
family_id: F211
columns:
- du_2022_advonly_tone_ctx
- du_2022_advonly_tone_full
- du_2022_advonly_tone_ss
- du_2022_degadv_tone_ctx
- du_2022_degadv_tone_full
- du_2022_degadv_tone_ss
- du_2022_degonly_tone_ctx
- du_2022_degonly_tone_full
- du_2022_degonly_tone_ss
- du_2022_negadv_tone_ctx
- du_2022_negadv_tone_full
- du_2022_negadv_tone_ss
- du_2022_negdeg_tone_ctx
- du_2022_negdeg_tone_full
- du_2022_negdeg_tone_ss
- du_2022_negonly_tone_ctx
- du_2022_negonly_tone_full
- du_2022_negonly_tone_ss
- du_2022_raw_tone_ctx
- du_2022_raw_tone_full
- du_2022_raw_tone_ss
unit: 语调得分 (连续, 约 [-1,1]; 文章级 Σ|final| 自归一化, 聚合后为 bank-year 均值)
formula: "du_2022_{variant}_tone = Σ(final_signed) / Σ|final| ; final 由 Du(2022) 词典命中词的极性经指定语言学规则子集 (否定翻转/程度副词/转折) 修饰后得到; variant ∈ {raw, negonly, degonly, advonly, negdeg, negadv, degadv} 为三规则的 powerset 真子集 (不含三规则全开的 full 口径)"
producer: news_process/pipeline/sentiment/tone_words.py ; news_process/pipeline/panel/stata_export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet
citations:
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: "Article 20"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  issue: null
  pages_or_artno: 67-75
- doi: 10.1111/jofi.12027
  type: journal
  authors: Garcia, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: The Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是同一部中文金融情感词典 du_2022 在打分阶段所依附的三条语言学规则被系统性开关后, 得到的语调测度阵列。底层词典为 Du et al. (2022) 提出的含政治正面词扩充的中文金融情感词典 (positive 2,235 词 / negative 2,986 词, 另含 political_positive 1,434 词以 0.5 权重计入正侧), 该词典的构念定位是: 相对英文 Loughran & McDonald (2011) 词典直接翻译的做法, 它在中文金融语境内本土化重构了极性词表, 使得词典在中国资本市场文本上的信噪比更高。本家族并不改变词典本身, 而是改变把逐词极性汇总为篇章语调时所施加的语言学修饰规则, 从而回答一个测量学问题: 主结论对"语调计算引擎里加了哪几条规则"这一研究者选择是否稳健。

【方法学与计算】
打分引擎是一台状态机 (producer = pipeline/sentiment/tone_words.py, 阶段 22 tone_words), 它逐句扫描分词后的文本, 对每个命中 du_2022 极性词表的词赋一个带符号的初始极性 (正词 +1, 负词 −1, 政治正面词 +0.5), 然后按启用的规则对该极性做局部修饰得到 final_signed 值。三条规则分别是: 否定翻转 (neg, 命中词落在否定词的作用域内则符号取反)、程度副词 (deg, 前置程度副词按强弱缩放极性幅度)、转折 (adv, 在"但是/然而"等转折连词后调整从句极性权重)。篇章语调 = Σ(final_signed) / Σ|final_signed|, 即以命中词绝对贡献之和自归一化, 取值近似落在 [−1, 1]。本家族的 7 个变体 raw / negonly / degonly / advonly / negdeg / negadv / degadv 恰是这三条规则的 powerset 真子集: raw 三规则全关 (裸词典计数), 三个 only 变体各只开一条, 三个双字母变体各开两条; 三规则全开的口径即 canonical du_2022_tone, 归属另一家族 (F211 刻意不含全开臂, 避免与 canonical 列重复)。每个变体经文章级计算后, 在阶段 40 面板导出时按 bank-year 取报道均值聚合 (stata_export.py), 分母口径与 full-only 留篇门控 (2026-06-29) 一致: 一篇是否计为"银行金科报道"只由 full 轨 llm_verified_full 判定, ctx/ss 轨为 conditional-on-full 的子集测度。审计 MATH-1 已确认这些消融变体彼此高度共线 (corr≈0.99), 属于同一构念在不同规则集下的近平行位移, 引擎因此报告变体间相关性而不将其并入同一可加分解式。

【文献定位】
词典法与规则修饰的方法学谱系可上溯至 Loughran & McDonald (2011) 对金融文本专用词典必要性的奠基论证, 以及 Garcia (2013) 在《Journal of Finance》上用词典语调刻画媒体情绪并检验其对市场收益预测力的经典应用——后者是"词典语调作为可复现测度进入资产定价实证"的顶刊范本, 本家族的自归一化语调正是该传统的中文本土化延续。规则层面, Taboada et al. (2011) 系统论证了否定、程度强化与转折三类语境价移 (contextual valence shifting) 对词典法语调准确度的贡献, 是本家族三规则消融的直接方法学依据; Pröllochs et al. (2016) 进一步针对新闻驱动交易场景专门研究否定作用域检测, 支撑了 negonly 一臂的独立价值; Punetha & Jain (2025) 则以无监督数学方法重新审视否定处理这一长期难题, 说明该规则选择至今仍是活跃且未被完全定论的研究前沿, 因而值得以消融梯子做敏感性检验。Frankel et al. (2022) 在《Management Science》上对比机器学习与词典法披露语调, 佐证了"同一构念在不同测量引擎下并排互证"的稳健性检验范式。Du et al. (2022) 作为词典本身的出处, 界定了 political_positive 的降权处理与中文金融语境的领域特异性。就识别口径而言, 7 个规则变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同规则集的变体混进同一 over-identified Hansen J 检验; 该梯子与政治词权重梯度、三轨、co-primary 双轨嵌入等其它稳健性梯子彼此正交, 各自独立评估, 不交叉进同一识别式。

## VAR: du_2022_advonly_tone_ctx

【变体差分】
本列 = advonly 规则子集 × ctx 轨。规则维: 仅启用转折规则 (adv), 否定翻转与程度副词两条规则关闭; 命中 du_2022 极性词后, 引擎只在"但是/然而/不过"等转折连词界定的从句内调整极性权重, 而对否定作用域和程度副词一律不作修饰, 因此该臂近似回答"若语调引擎只理解转折、不理解否定与强度, 语调如何"。由于正式财经报道中转折结构相对稀疏, advonly 相对 raw 基线的净位移通常较小, 但在含"业绩下滑但转型见效"这类逆折叙事的报道里差异会被放大。轨道维: ctx = 实体窗轨, 文本来源为 content_ctx (标题 prepend + 目标银行实体上下文窗口), 仅取围绕银行实体的局部片段而非全文, 相对 full 轨剔除了与目标银行无关的段落噪声, 使语调更贴合"关于该银行本身"的情绪。本列相对家族参照 (三规则全开的 canonical) 的差分是"只留转折一条规则"; 相对同规则的 full/ss 兄弟列的差分是文本作用域收窄到实体窗。聚合上, 本列文章级得分先算, 再按 bank-year 均值进入面板, 分母沿用 full-only 门控下的留篇集。ctx 轨为 conditional-on-full 的稳健性测度, 与 advonly_full / advonly_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_advonly_tone_full

【变体差分】
本列 = advonly 规则子集 × full 轨。规则维同 advonly 家族说明: 仅启用转折规则, 否定与程度副词关闭, 语调只对转折连词后的从句极性权重作调整; 用途是隔离转折规则单独的边际贡献——把本列与 raw_full (零规则基线) 相减, 即得转折规则在全文轨上相对无规则的净效应。轨道维: full = 全文轨, 文本来源为 content_full (标题 prepend + 全文正文), 是三轨中信息量最全、也是唯一承担留篇门控 (full-only, 2026-06-29) 的轨——一篇报道是否计入 bank-year 分母只由 full 轨判定, 故 full 轨样本宇宙为最大集, ctx/ss 为其子集。因保留全部正文命中词参与自归一化, 本列的分母 Σ|final| 在三轨中最大, 语调读数通常也最平滑稳定。本列相对 advonly_ctx / advonly_ss 差分在于不作任何实体窗或同句裁剪; 相对三规则全开 canonical 的差分是"关掉否定与程度、只留转折"。经文章级计算后按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J, 与政治词权重、双轨嵌入等其它稳健性梯子彼此正交独立。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_advonly_tone_ss

【变体差分】
本列 = advonly 规则子集 × ss 轨。规则维: 仅转折规则启用, 否定翻转与程度副词关闭, 与 advonly 家族一致, 只对转折从句调整极性权重。轨道维: ss = 同句轨, 文本来源为 content_ss (标题 prepend + 银行∧金科同句±N 窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)。ss 轨是三轨中最严格的作用域: 只保留目标银行与金融科技词在同一句 (含 ±N 句窗) 共现的片段, 因而对"银行—金科"共现语境的语调最敏感, 也是三轨中命中词最少、方差可能最大的一轨。回退语义镜像 ctx: 当某篇不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True, 共享 n_articles 分母; 若 FINTECH_AC=None 则该篇 ss_is_fallback 全 True 优雅降级。因作用域窄且转折在窄窗内更少出现, advonly_ss 相对 raw_ss 的净位移通常最小。本列相对 advonly_full / advonly_ctx 的差分即文本作用域进一步收窄到同句共现窗。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则的 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degadv_tone_ctx

【变体差分】
本列 = degadv 规则子集 × ctx 轨。规则维: 同时启用程度副词 (deg) 与转折 (adv) 两条规则, 唯独关闭否定翻转 (neg); 引擎会按前置程度副词缩放极性幅度、并在转折从句内调整权重, 但对否定词作用域内的命中词不翻转符号, 故该臂近似回答"若引擎理解强度与转折、却对否定盲视, 语调如何"——这与 negonly 恰成互补对照, 二者并读可交叉界定否定规则的边际。因缺否定, 凡"未能盈利""并非利好"这类被否定的正词在本臂仍记正值, 语调会系统性偏正。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 文本作用域限于目标银行邻近片段, 剔除无关段落噪声。本列相对 degadv_full / degadv_ss 兄弟列差分在轨道 (实体窗); 相对三规则全开 canonical 差分在"缺否定这一条规则"。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 degadv_full / degadv_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degadv_tone_full

【变体差分】
本列 = degadv 规则子集 × full 轨。规则维: 程度副词与转折两条规则启用, 否定翻转关闭, 与 degadv 家族说明一致——语调对强度缩放与转折从句敏感, 但不对否定作用域翻转符号, 因而对被否定的极性词有系统性偏差 (被否定的正词仍记正)。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙为最大集, 分母 Σ|final| 在三轨中最大。本列代表在"缺否定"这一规则残缺下、基于最完整文本证据的语调, 相对 degadv_ctx / degadv_ss 差分在于不作实体窗或同句裁剪。与 negonly_full 并读可分离出否定规则单独的边际——二者互为该规则消融梯子的对照臂 (一个只缺否定、一个只有否定), 但仍各自 just-identified、并排评估。相对三规则全开 canonical 差分为"关掉否定"; 由于否定在中文金融新闻里是三规则中影响最大的一条, 本列与 canonical 的落差通常在三个双规则臂中最显著。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degadv_tone_ss

【变体差分】
本列 = degadv 规则子集 × ss 轨。规则维: 程度副词与转折启用, 否定翻转关闭 (同 degadv 家族), 对被否定的极性词有系统性偏正。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少、方差最大; 回退语义镜像 ctx——无同句共现时 content_ss 回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列相对 degadv_full / degadv_ctx 的差分是文本作用域进一步收窄到同句共现窗, 对"银行—金科"共现语境下的强度与转折修饰最敏感, 但对否定盲视。在 T=2 开发语料上, 因同句共现片段稀疏, 本列可能出现较多回退与近零方差, 属预期退化, 生产 T=18 语料下方能充分体现该臂差异。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 亦不与其它梯子交叉进同一识别式。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degonly_tone_ctx

【变体差分】
本列 = degonly 规则子集 × ctx 轨。规则维: 仅启用程度副词 (deg), 否定翻转与转折关闭; 引擎只按前置程度副词的强弱缩放命中词极性幅度 (如"大幅""显著"放大权重、"略微""小幅"收窄权重), 而不翻转否定符号、不作转折调整, 故该臂隔离出强度修饰单条规则的效应。因程度副词只改变幅度不改变符号, degonly 相对 raw 基线的差异主要体现在语调绝对值的伸缩而非方向翻转。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 作用域限于目标银行邻近片段, 剔除无关段落噪声。本列相对 degonly_full / degonly_ss 差分在轨道; 相对三规则全开 canonical 差分在"只留程度副词一条规则"。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 degonly_full / degonly_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degonly_tone_full

【变体差分】
本列 = degonly 规则子集 × full 轨。规则维: 仅程度副词启用, 否定与转折关闭 (同 degonly 家族), 语调只对强度副词缩放极性幅度、不改变符号方向。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙最大, 分母 Σ|final| 最大。本列代表"引擎只理解强度"这一最小规则集下、基于最完整文本的语调, 相对 degonly_ctx / degonly_ss 差分在于不作实体窗或同句裁剪。与 raw_full 并读即可分离出程度副词规则单独的边际贡献 (raw 为零规则基线, degonly 在其上仅加一条 deg), 是量化"强度修饰是否值得加进语调引擎"的直接对照。因程度副词不翻转符号, 本列与 raw_full 高度相关 (共线性尤强), 符合审计 MATH-1 对消融变体 corr≈0.99 的观察。相对三规则全开 canonical 差分为"关掉否定与转折"。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J, 与政治词权重、双轨嵌入等梯子正交独立。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_degonly_tone_ss

【变体差分】
本列 = degonly 规则子集 × ss 轨。规则维: 仅程度副词启用, 否定翻转与转折关闭 (同 degonly 家族), 只缩放极性幅度不改符号。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少; 回退语义镜像 ctx——无同句共现时回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列相对 degonly_full / degonly_ctx 差分是作用域进一步收窄到同句共现窗, 对共现语境下的强度修饰最敏感, 但对否定与转折盲视。因作用域窄且程度副词在短窗内出现频率低, 本列相对 raw_ss 的净位移通常很小, 在 T=2 开发语料上可能近乎重合。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negadv_tone_ctx

【变体差分】
本列 = negadv 规则子集 × ctx 轨。规则维: 同时启用否定翻转 (neg) 与转折 (adv), 关闭程度副词 (deg); 引擎在否定作用域内翻转命中词符号、并在转折从句内调整权重, 但不按程度副词缩放极性幅度, 故该臂近似回答"若引擎理解否定与转折、却对强度盲视, 语调如何"。由于含否定这一影响最大的规则, negadv 相对 raw 基线的位移通常较大, 尤其在含"未达预期""并未改善"等被否定正词的报道里。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 作用域限于目标银行邻近片段, 剔除无关段落噪声。本列相对 negadv_full / negadv_ss 差分在轨道; 相对三规则全开 canonical 差分在"缺程度副词一条规则"。与 degadv (缺否定) 对照可交叉分离规则边际, 但各臂仍各自 just-identified。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 negadv_full / negadv_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negadv_tone_full

【变体差分】
本列 = negadv 规则子集 × full 轨。规则维: 否定翻转与转折启用, 程度副词关闭 (同 negadv 家族), 语调对否定作用域翻转符号、对转折从句调权, 但不作强度缩放。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙最大, 分母 Σ|final| 最大。本列代表"缺程度副词"规则残缺下、基于最完整文本的语调, 相对 negadv_ctx / negadv_ss 差分在于不作实体窗或同句裁剪。与 negonly_full 并读可分离出转折规则的边际 (negonly 只留否定, negadv 在其上再加转折); 与 advonly_full 并读可分离否定规则的边际——本列因此是规则消融交叉分解中承上启下的一臂。相对三规则全开 canonical 差分为"关掉程度副词"; 由于程度副词只缩放幅度不改符号, 本列与 canonical 的落差在三个双规则臂中通常最小。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negadv_tone_ss

【变体差分】
本列 = negadv 规则子集 × ss 轨。规则维: 否定翻转与转折启用, 程度副词关闭 (同 negadv 家族)。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少、方差最大; 回退语义镜像 ctx——无同句共现时回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列相对 negadv_full / negadv_ctx 差分是作用域进一步收窄到同句共现窗, 对共现语境下的否定与转折修饰最敏感, 但对强度盲视。因含否定规则, 本列在共现窗内一旦命中被否定的极性词, 符号翻转会显著改变窄窗语调, 故相对同句轨的 raw_ss 位移在含否定报道里可观。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 亦不与其它稳健性梯子交叉进同一识别式。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negdeg_tone_ctx

【变体差分】
本列 = negdeg 规则子集 × ctx 轨。规则维: 同时启用否定翻转 (neg) 与程度副词 (deg), 关闭转折 (adv); 引擎在否定作用域内翻转符号、按程度副词缩放极性幅度, 但不作转折从句调权, 故该臂近似回答"若引擎理解否定与强度、却对转折盲视, 语调如何"。negdeg 组合了三规则中影响最大 (否定) 与只改幅度 (程度) 两条, 独缺在正式财经文本中相对稀疏的转折。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 作用域限于目标银行邻近片段, 剔除无关段落噪声。本列相对 negdeg_full / negdeg_ss 差分在轨道; 相对三规则全开 canonical 差分在"缺转折一条规则"; 因转折稀疏, 本列通常是三个双规则臂中与 canonical 最接近者。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 negdeg_full / negdeg_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negdeg_tone_full

【变体差分】
本列 = negdeg 规则子集 × full 轨。规则维: 否定翻转与程度副词启用, 转折关闭 (同 negdeg 家族), 语调对否定翻转符号、对强度缩放幅度, 但不作转折调权。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙最大, 分母 Σ|final| 最大。本列代表"缺转折"规则残缺下、基于最完整文本的语调, 是三个双规则臂中在中文金融新闻里通常最接近三规则全开 canonical 的一臂 (转折结构在正式财经报道中相对稀疏, 关掉它损失的信息最少), 相对 negdeg_ctx / negdeg_ss 差分在于不作实体窗或同句裁剪。与 negonly_full / degonly_full 并读可交叉分离否定与程度两条规则的边际, 构成规则消融的核心对照三角。相对 canonical 差分为"关掉转折"。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negdeg_tone_ss

【变体差分】
本列 = negdeg 规则子集 × ss 轨。规则维: 否定翻转与程度副词启用, 转折关闭 (同 negdeg 家族)。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少; 回退语义镜像 ctx——无同句共现时回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列相对 negdeg_full / negdeg_ctx 差分是作用域进一步收窄到同句共现窗, 对共现语境下的否定与强度修饰最敏感, 但对转折盲视。因转折在短窗内几乎不出现, negdeg_ss 与三规则全开在同句轨上的读数通常近乎一致, 是同句轨里信息损失最小的消融臂。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negonly_tone_ctx

【变体差分】
本列 = negonly 规则子集 × ctx 轨。规则维: 仅启用否定翻转 (neg), 程度副词与转折关闭; 引擎只对落在否定词作用域内的命中词翻转符号, 不作强度缩放、不作转折调权, 故该臂隔离出否定规则单条效应——这也是词典法语调最经典、最常被单独讨论的一条规则 (见 Pröllochs et al. 2016 对新闻交易场景否定作用域检测的专门研究, 以及 Punetha & Jain 2025 对否定处理数学化的最新推进)。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 作用域限于目标银行邻近片段, 剔除无关段落噪声。本列相对 negonly_full / negonly_ss 差分在轨道; 相对三规则全开 canonical 差分在"只留否定一条规则"。与 raw_ctx 并读即得否定规则在实体窗轨上相对无规则基线的净边际。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 negonly_full / negonly_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negonly_tone_full

【变体差分】
本列 = negonly 规则子集 × full 轨。规则维: 仅否定翻转启用, 程度副词与转折关闭 (同 negonly 家族), 语调只对否定作用域翻转符号。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙最大, 分母 Σ|final| 最大。值得注意的是 negonly × 三轨在 stata_export.py 中拥有 curated 中文标签 ("Du2022词典语调(仅否定规则,全文/实体窗/同句轨)"), 是本消融家族里唯一被显式命名标签的一臂 (与其余 5 部情感词典的 negonly 对称补全), 反映否定规则在文献与实践中的特殊地位。本列代表"引擎只理解否定"最小规则集下、基于最完整文本的语调, 相对 negonly_ctx / negonly_ss 差分在于不作实体窗或同句裁剪; 与 raw_full 并读即可分离出否定规则单独的边际 (raw 为零规则基线), 是量化"否定修饰对中文金融语调值不值得加"的最直接对照。相对 canonical 差分为"关掉程度副词与转折"。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_negonly_tone_ss

【变体差分】
本列 = negonly 规则子集 × ss 轨。规则维: 仅否定翻转启用, 程度副词与转折关闭 (同 negonly 家族)。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少、方差最大; 回退语义镜像 ctx——无同句共现时回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列同样拥有 curated 中文标签 ("Du2022词典语调(仅否定规则,同句轨)")。相对 negonly_full / negonly_ctx 差分是作用域进一步收窄到同句共现窗, 对"银行—金科"共现语境下的否定修饰最敏感——当共现窗内命中被否定的极性词时, 符号翻转对窄窗语调的影响尤为显著。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_raw_tone_ctx

【变体差分】
本列 = raw 规则子集 × ctx 轨。规则维: 三条语言学规则全部关闭 (neg/deg/adv 均不启用), 语调退化为最纯粹的裸词典极性计数自归一化——命中正词记 +1、负词记 −1、政治正面词 +0.5, 不作任何否定翻转、强度缩放或转折调权。raw 是整个消融梯子的零规则基线, 其余六个变体都可视作在 raw 之上叠加规则子集; 与任一含规则臂并读即可测得那些规则相对无规则基线的净边际, 因此 raw 是解释所有其它臂的算术锚点。轨道维: ctx = 实体窗轨 (content_ctx, 标题 prepend + 银行实体上下文窗口), 作用域限于目标银行邻近片段, 剔除与目标银行无关的段落噪声。本列相对 raw_full / raw_ss 差分在轨道; 相对三规则全开 canonical 差分在"三规则全关"。文章级得分按 bank-year 均值聚合进面板, 分母沿用 full-only 留篇集。ctx 轨为 conditional-on-full 稳健性测度, 与 raw_full / raw_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_raw_tone_full

【变体差分】
本列 = raw 规则子集 × full 轨, 是本家族的解释锚点。规则维: 三条规则全关, 语调 = 裸 du_2022 词典命中词的带符号极性之和除以绝对贡献之和, 不作否定翻转、强度缩放、转折调权中的任何一项; 该臂对应"只用词典、不用任何语言学后处理"的最朴素文本情感测度, 常被文献 (如 Loughran & McDonald 2011 与 Garcia 2013) 作为词典法的默认起点。轨道维: full = 全文轨 (content_full, 标题 prepend + 全文正文), 承担 full-only 留篇门控, 样本宇宙最大, 分母 Σ|final| 在三轨中最大。本列既是全家族的零规则基线, 又落在信息量最全的全文轨, 因而是把"规则修饰"与"文本作用域"两个消融维度都归零的双重参照系: 任何含规则臂减去本列即该规则集在 full 轨上的净贡献, 任何 raw_ctx/raw_ss 减去本列即作用域收窄的净贡献, 两个方向的边际都以本列为原点度量。相对三规则全开 canonical 差分为"三规则全关"。文章级得分按 bank-year 均值聚合进面板。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨混入同一 over-identified Hansen J, 与政治词权重梯度、词典消融、co-primary 双轨嵌入等其它稳健性梯子彼此正交独立。 作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

## VAR: du_2022_raw_tone_ss

【变体差分】
本列 = raw 规则子集 × ss 轨。规则维: 三条语言学规则全部关闭, 语调为裸词典极性计数自归一化 (同 raw 家族), 是零规则基线, 不作否定翻转、强度缩放、转折调权。轨道维: ss = 同句轨 (content_ss, 标题 prepend + 银行∧金科同句±N 窗), 三轨中作用域最严格, 只保留银行与金科同句共现片段, 命中词最少、方差最大; 回退语义镜像 ctx——无同句共现时回退全文 body 且 ss_is_fallback=True 共享 n_articles 分母, FINTECH_AC=None 时全篇优雅降级。本列把"规则归零"与"作用域收窄到同句共现窗"两个方向叠加, 是本家族最保守的语调读数, 对"银行—金科"共现语境下最朴素的词典极性最敏感, 也是同句轨里其余六臂的算术锚点。相对 raw_full / raw_ctx 差分是文本作用域进一步收窄。在 T=2 开发语料上因同句共现稀疏可能出现较多回退与近零方差, 属预期退化, 生产 T=18 方能充分体现。文章级得分按 bank-year 均值聚合进面板。ss 轨为 conditional-on-full 稳健性测度, 与同规则 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

作为规则消融梯子的一员, 本列与三规则全开 canonical 及本家族其余六个变体高度共线 (审计 MATH-1 观察消融变体间 corr≈0.99), 引擎因此只报告变体间相关性而不将其并入同一可加分解式, 也不据相关性高低取舍主次。在 jieba 0.42.1 分词与阶段 22 打分状态机逻辑冻结的前提下, 本列文章级得分逐位可复现, 构成规格曲线 (specification curve) 稳健性检验中的一个独立坐标点, 用以证明主结论不被'语调引擎装了哪几条语言学规则、文本取哪一轨'这一研究者自由度所驱动。

<!-- rendered-citations:begin -->
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
