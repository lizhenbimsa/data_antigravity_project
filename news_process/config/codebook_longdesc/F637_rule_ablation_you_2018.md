---
family_id: F637
novelty_exempt_rationale: "消融变体家族(rule_ablation_you_2018): 21列是对you_2018词典在neg/deg/adv三条语言学规则维度上的非全集组合穷举,测度定义依据已在母族You et al.(2018)词典文献与Taboada et al.(2011)语境价化转移理论中给出,本家族仅是方法学稳健性梯度,非独立新构念,无需追加2023+文献。"
columns:
- you_2018_advonly_tone_ctx
- you_2018_advonly_tone_full
- you_2018_advonly_tone_ss
- you_2018_degadv_tone_ctx
- you_2018_degadv_tone_full
- you_2018_degadv_tone_ss
- you_2018_degonly_tone_ctx
- you_2018_degonly_tone_full
- you_2018_degonly_tone_ss
- you_2018_negadv_tone_ctx
- you_2018_negadv_tone_full
- you_2018_negadv_tone_ss
- you_2018_negdeg_tone_ctx
- you_2018_negdeg_tone_full
- you_2018_negdeg_tone_ss
- you_2018_negonly_tone_ctx
- you_2018_negonly_tone_full
- you_2018_negonly_tone_ss
- you_2018_raw_tone_ctx
- you_2018_raw_tone_full
- you_2018_raw_tone_ss
unit: 语调得分 (连续, 理论域约 [-1,1]; 文章级自归一化后聚合为 bank-year 均值)
formula: 状态机扫词命中 you_2018 词典 (positive 1,425 / negative 1,583 词) → 对每条命中施加指定语言学规则子集 (否定翻转 neg / 程度副词 deg / 转折 adv 三规则的 7 种非全集组合, 另设不加规则的 raw 基线) → Σ|final| 自归一化 → 文章级 you_2018_{variant}_score_{track} → bank-year 聚合为面板列 you_2018_{variant}_tone_{track}
producer: news_process/pipeline/sentiment/tone_words.py ; news_process/pipeline/panel/export.py
upstream: []
citations:
- {doi: "10.1093/rfs/hhx055", type: journal, authors: "You, J., Zhang, B., & Zhang, L.", year: 2018, title: "Who Captures the Power of the Pen?", venue: "The Review of Financial Studies", vol: "31", issue: "1", pages_or_artno: "43-96"}
- {doi: "10.1162/COLI_a_00049", type: journal, authors: "Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.", year: 2011, title: "Lexicon-based methods for sentiment analysis", venue: "Computational Linguistics", vol: "37", issue: "2", pages_or_artno: "267-307"}
- {doi: "10.1287/mnsc.2021.4156", type: journal, authors: "Frankel, R., Jennings, J., & Lee, J.", year: 2022, title: "Disclosure sentiment: Machine learning vs. dictionary methods", venue: "Management Science", vol: "68", issue: "7", pages_or_artno: "5514-5532"}
- {doi: "10.1016/j.dss.2016.05.009", type: journal, authors: "Pröllochs, N., Feuerriegel, S., & Neumann, D.", year: 2016, title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading", venue: "Decision Support Systems", vol: "88", pages_or_artno: "67-75"}
- {doi: "10.1093/rof/rfab036", type: journal, authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W.", year: 2022, title: "Language and domain specificity: A Chinese financial sentiment dictionary", venue: "Review of Finance", vol: "26", issue: "3", pages_or_artno: "673-719"}
- doi: "10.1609/icwsm.v18i1.31443"
  type: "journal"
  authors: "Oh, N."
  year: 2024
  title: "Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries"
  venue: "Proceedings of the International AAAI Conference on Web and Social Media"
  vol: "18"
  pages_or_artno: "2003-2013"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"银行—金融科技新闻的词典式语调"在语言学规则维度上的消融梯度: 给定 You et al. (2018, Review of Financial Studies)《Who Captures the Power of the Pen?》所构建的中文金融情感词典 (positive 1,425 词 / negative 1,583 词; 该词典由该文用于度量中国官方媒体与市场化媒体报道语调对信贷配置的差异化影响, 是词典法金融文本情感测度在中国语境下的代表性锚点), 家族逐一拆解否定翻转 (neg)、程度副词加权 (deg)、转折结构降权 (adv) 三条语言学规则各自及其两两组合对最终语调分的边际贡献。You et al. (2018) 原文本身即以简单词频计数构造语调指标, 未内生这三条规则; 本家族的规则叠加是本项目在其词典基础上的方法学扩展, 用以检验"语言学规则精细化"这一测度选择本身是否驱动下游结果, 呼应 Taboada et al. (2011, Computational Linguistics)《Lexicon-based methods for sentiment analysis》对词典法情感分析中否定、强化词、转折等语言学修饰规则系统性作用的经典论证, 以及 Frankel, Jennings & Lee (2022, Management Science)《Disclosure sentiment: Machine learning vs. dictionary methods》关于词典法本身内部设计选择 (而非词典法与机器学习法之间) 亦可显著改变测度结果的发现。

【方法学与计算】
计算管道位于 pipeline/sentiment/tone_words.py: 阶段 22 词典情感分析引擎对每篇文章的三条文本轨道 (full/ctx/ss) 分别执行一个状态机扫词过程, 命中 you_2018 词典的正/负词条后, 根据当前变体 (variant) 所启用的规则子集对命中词的极性符号与幅度做条件变换——neg 规则检测命中词前是否存在否定词, 若存在则翻转符号 (正转负、负转正); deg 规则检测命中词前是否存在程度副词 (如"极其""略微"), 若存在则按副词强度对该词权重做放大或缩小; adv 规则检测命中词是否处于转折从句中 (如"但是""然而"引导的分句), 若存在则对其贡献做降权处理, 因转折句式中的情感词往往被后半句语气反转或弱化。本家族固定于 you_2018 一部词典之上系统性穷举这三条规则的非全集组合 (即排除三规则全启用的 canonical 全量变体, 该变体属家族外的 canonical 列, 不在本 21 列清单内)——具体 7 种非-full 变体依次为: raw (三规则全不启用的裸计数基线) / negonly (仅 neg) / degonly (仅 deg) / advonly (仅 adv) / negdeg (neg+deg) / negadv (neg+adv) / degadv (deg+adv)。每个变体对每条命中词计算出 final 符号与幅度后, 逐词求和得到该变体在该篇文章该轨道下的原始得分, 再除以 Σ|final| (即所有命中词最终幅度绝对值之和) 做自归一化, 使得分域收敛到约 [-1,1] 区间且不受文章长度或命中词数量的线性膨胀影响。文章级得分 you_2018_{variant}_score_{track} 经 pipeline/panel/export.py 在 bank-year 层面按同一 bank 同一年份下全部合格文章取算术均值, 产出本家族面板列 you_2018_{variant}_tone_{track}。三轨道 full (标题+正文全文) / ctx (标题+银行∧金科实体窗口) / ss (标题+银行∧金科同句±N窗口) 各自独立走完整状态机与归一化流程, 三轨互为规格稳健性并排、各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; ss 轨在无银行∧金科同句共现时镜像 ctx 的回退语义——回退为全文 body 且置位 ss_is_fallback=True, 与 ctx 共享同一 n_articles 分母。留篇门控 (是否判定某篇文章为"一篇银行金科报道"从而进入 bank-year 聚合分母) 采用 full-only 口径 (2026-06-29 起): 只看该文章在 full 轨的 LLM 验证结果 llm_verified_full 是否为真, ctx/ss 两轨在此意义上是 conditional-on-full 的测度轨、行宇宙是 full 留篇集的子集, 各轨照算但不反过来扩张或收缩留篇集合。

【文献定位】
You, Zhang & Zhang (2018, Review of Financial Studies) 是本词典的直接方法学来源, 该文利用词典语调差异识别中国官方控制媒体与市场化媒体报道倾向对企业融资的因果效应, 本家族继承其词典表, 但把规则维度作为独立于词典选择的正交稳健性轴。Taboada et al. (2011, Computational Linguistics) 系统论证了否定、强化/弱化程度词与转折结构是词典法情感分析中最主要的三类"语境价化转移" (contextual valence shifters) 来源, 是本家族三规则 (neg/deg/adv) 拆分设计的方法学依据。Frankel, Jennings & Lee (2022, Management Science) 在披露语调测度语境下比较词典法与机器学习法, 发现词典法内部的具体实现选择本身已能造成不容忽视的测度差异, 支持本家族"在同一词典上做规则消融、逐一验证结果对规则选择的敏感性"这一设计动机。Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 专门研究否定辖域检测对新闻驱动交易语境下情感测度准确性的影响, 是 negonly/negdeg/negadv 三个含 neg 规则臂的直接文献支撑。Du et al. (2022, Review of Finance) 虽以其自建 du_2022 词典的政治词权重敏感性检验为主体 (三权重 {0.0, 0.5, 1.0} 互为稳健性, 详见项目铁律与 F634 等姊妹家族), 但其"以显式敏感性梯度证明主结论不被单一测度选择驱动"的方法论范式与本家族的规则消融梯度同构, 二者互为方法学参照。

本家族 21 列穷举 7 种规则子集变体 (advonly/degadv/degonly/negadv/negdeg/negonly/raw) × 3 条文本轨道 (ctx/full/ss)。铁律重申: 各变体、各轨道均各自 just-identified 并排、互为稳健性、不分主次, 任何回归设定禁止将本家族多个变体或多个轨道同时作为工具变量塞入同一个 over-identified Hansen J 检验; 三规则消融梯度与政治词权重梯度 (du_2022 专属) 正交不交叉, 二者均在"全语言学规则"或"全权重取值"各自独立维度上变动, 不做笛卡尔积展开以避免列数爆炸。留篇门控与 n_articles 分母口径与项目 full-only 铁律 (2026-06-29) 完全一致, ss 轨回退语义严格镜像 ctx 轨。 Oh (2024) 构建 sentibank, 把 15 部原始情感词典与 43 部预处理词典统一整合入库 (覆盖 7 类体裁与 6 个领域), 其问题意识是词典资源的碎片化与验证缺失, 同时明确背书依赖专家词表的规则法在可解释性上的透明性——这为本家族在三家 LLM 与三个 BERT 两支之外继续保留 you_2018 词典状态机语调轨提供了当代前沿参照, 也佐证同一情感构念下并存大量异源词典乃该领域常态, 与本项目并排六部中文词典的设计同构。边界须写明: 该文覆盖英文社交媒体等体裁, 不含 you_2018 等中文金融词典, 未实现否定/程度/转折三规则状态机, 亦未做任何跨词典整合或均值运算, 故只锚定“词典轨值得保留且异源并存”这一层, 对本家族 7 个规则消融变体的具体拆分设计不构成依据。
## VAR: you_2018_advonly_tone_ctx

【变体差分】
本列在 you_2018 词典基础上仅启用 adv (转折降权) 一条语言学规则, 不启用 neg (否定翻转) 与 deg (程度副词加权); 文本轨道为 ctx (标题+银行∧金科实体窗口)。计算上, 状态机对每个命中词只检测其是否处于转折从句语境, 若处于转折从句 (如"虽然……但是……"结构后半句反转前) 则对该词最终贡献幅度做降权, 否则按原始词典极性与固定权重计入; 不做否定符号翻转、不做程度副词幅度调整。该变体单独度量"仅剔除转折污染"对语调分的边际贡献, 与其余含 adv 的变体 (negadv/degadv) 相比缺少 neg 或 deg 的叠加效应, 是理解 adv 规则独立解释力的基准臂。转折结构在中文财经报道中相当常见 (如"业绩虽有下滑, 但整体经营稳健"), 若不加处理, 词典法容易把转折前半句的负面词与转折后半句的正面词同等计入, 造成语调方向被稀释甚至误判; adv 规则的设计动机正是针对这一常见句法陷阱, 呼应 Taboada et al. (2011, Computational Linguistics) 对"contrastive conjunction"作为语境价化转移来源的系统论证。ctx 轨相对 full/ss 轨的差异在于文本窗口范围仅覆盖标题与银行∧金科实体邻近区域, 命中词样本更聚焦于目标实体相关语境, 但样本量 (命中词数) 通常小于 full 轨, 自归一化后对单一命中词的敏感度相对更高, 与 you_2018_advonly_tone_full / you_2018_advonly_tone_ss 互为规格稳健性并排、各自 just-identified, 三者禁止混入同一 over-identified Hansen J 设定。

## VAR: you_2018_advonly_tone_full

【变体差分】
本列在 you_2018 词典基础上仅启用 adv (转折降权) 规则, 文本轨道为 full (标题+正文全文)。与 you_2018_advonly_tone_ctx 共享完全相同的规则子集 (仅 adv), 差异只在文本轨道: full 轨扫描整篇正文而非局限于实体邻近窗口, 因而命中词样本量通常最大、覆盖面最广, 是 P1 (`bank_fintech_tone`) 论文留篇门控所依赖的 full-only 主轨在本消融族中的对应臂——留篇门控 (是否判定某篇文章为一篇银行金科报道) 仅看该文章 full 轨的 LLM 验证结果 llm_verified_full, 与本列共享同一行宇宙 (full-only 口径, 2026-06-29 起)。作为家族内样本量最充分的 adv-only 变体, 该列在稳健性检验中通常统计功效最高, 但其代价是可能纳入与目标银行∧金科关系较弱的段落语境 (例如整篇报道虽提及目标银行但主体段落讨论其他业务), 从而混入与银行金科关系较弱的转折句式噪声。与 ctx/ss 两轨互为规格稳健性并排、不分主次, 三者均各自 just-identified, 不得同时作为工具变量塞入同一个 over-identified Hansen J 检验。该列与 you_2018_degonly_tone_full / you_2018_negonly_tone_full 共同构成 full 轨上的单规则三元组, 用以在样本量最充分的条件下比较 adv/deg/neg 三条语言学规则各自独立作用于语调分的边际大小, 三者互为稳健性、不设优先级, 任何一条规则若在此三元组比较中系统性偏离另外两条较远, 应披露为测度选择敏感性而非据此推翻规则设计本身。

## VAR: you_2018_advonly_tone_ss

【变体差分】
本列在 you_2018 词典基础上仅启用 adv (转折降权) 规则, 文本轨道为 ss (标题+银行∧金科同句±N窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)。相较 ctx 轨, ss 轨判定更严格——要求银行实体与金科词在同一句 (或±1句窗) 内共现才纳入该句, 是三轨中语境最紧凑、噪声最小但样本量通常最小的一支; 判定原语为 core/text/entity_context.py 中与 stage 13 共现硬过滤不同口径的严格同句抽取函数。当某篇文章不存在银行∧金科同句共现时, 该列回退为镜像 ctx 轨语义: content_ss 退化为全文 body, 对应 ss_is_fallback 置为 True, 且与 ctx 轨共享同一 n_articles 分母, 不产生单边孤儿样本。该列与 you_2018_advonly_tone_ctx / you_2018_advonly_tone_full 在规则维度上完全一致 (仅 adv), 差异纯粹来自文本轨道判据, 三者互为稳健性并排; 在样本量充分的情形下, ss 轨因语境最紧凑, 通常能最直接地捕捉"银行与金科紧邻同句出现且带转折句式"这一特定叙事模式对语调分的边际影响, 但代价是样本量收缩带来的估计方差上升。该列与 you_2018_advonly_tone_ctx / you_2018_advonly_tone_full 构成三轨完整组, 三者估计方向与幅度的一致性是"adv 规则是否稳健于文本窗口宽窄"这一具体稳健性命题的直接经验依据, 供稳健性附表并排披露, 不因样本量差异择一为准; 生产 T=19 全量语料上该列样本量将随文章总数扩大而相应扩大, 届时与 ctx/full 两轨的分化程度才具备充分统计意义。

## VAR: you_2018_degadv_tone_ctx

【变体差分】
本列同时启用 deg (程度副词加权) 与 adv (转折降权) 两条规则, 不启用 neg (否定翻转); 文本轨道为 ctx。状态机对每个命中词先检测其前是否有程度副词并据此放大/缩小幅度 (如"大幅提升"较"提升"幅度更大, "略有下降"较"下降"幅度更小), 再检测其是否处于转折从句语境并据此降权, 但不检测否定词、不做符号翻转——即该变体刻意保留"未否定处理"的原始极性方向, 只在幅度层面叠加两种修饰效应, 是三个两两规则组合臂中唯一不涉及符号翻转、只做幅度调制的一支。degadv 与 negadv (deg 替换为 neg)、negdeg (adv 替换为 neg) 构成三个两两组合臂, 三者两两互补 (每一对恰好共享一条规则、缺另一条), 用于识别 deg×adv 交互相对其余两两组合的相对贡献差异, 从而在不叠加否定翻转这一相对"激进"的语义反转操作的前提下, 单独考察幅度类规则 (deg) 与结构降权类规则 (adv) 的联合效应。ctx 轨窗口设定同 you_2018_advonly_tone_ctx 条目所述, 与 you_2018_degadv_tone_full / you_2018_degadv_tone_ss 互为规格稳健性并排、各自 just-identified, 禁止混入同一 over-identified Hansen J 设定。在实体邻近窗口下, deg×adv 交互效应聚焦于目标银行金科相关叙事本身的强弱与转折修辞, 相较 full 轨更能剥离与目标实体无关段落的规则效应噪声, 是本组合臂在细粒度语境下的代表性观测点; 与含 neg 的两个两两组合臂 (negadv_tone_ctx/negdeg_tone_ctx) 相比, 本列保留原始极性方向, 结果解读上应聚焦幅度差异而非方向差异。

## VAR: you_2018_degadv_tone_full

【变体差分】
本列同时启用 deg 与 adv 两条规则 (不含 neg), 文本轨道为 full。与 you_2018_degadv_tone_ctx 规则子集完全相同, 差异仅在文本覆盖范围: full 轨对整篇正文逐句扫描程度副词与转折结构, 因样本量更大, 在检验 deg×adv 交互效应的统计显著性时通常提供更高功效, 是本变体在三轨中的主力稳健性臂, 也是留篇门控 full-only 口径 (2026-06-29) 所对应的行宇宙主轨。该列与 negadv_tone_full / negdeg_tone_full 共同构成"两两组合×full轨"三元组, 三者在同一最大样本量文本覆盖范围下比较不同规则对组合效应的相对贡献, 互为稳健性、不分主次。deg 与 adv 两条规则分别作用于幅度层面的放缩与降权, 二者组合刻画的是"程度用语被转折句式部分抵消"这一常见修辞模式 (如"业绩大幅改善, 但仍低于预期"), 在官方媒体与市场化媒体报道中该修辞模式出现频率可能存在系统性差异, 呼应 You, Zhang & Zhang (2018) 对不同媒体属性下报道语调构造方式的核心关切, 是本列在文献定位上区别于其余两两组合臂的独特分析价值所在。full 轨样本量最充分, 使该列相较 ctx/ss 两轨在检验 deg×adv 交互效应统计显著性时通常提供最高功效, 常在正文结果表中作为该两两组合臂的主展示对象, 但依据家族铁律, 该列不构成相对其余两轨或其余两两组合臂的"优选"测度, 仅是规格稳健性梯度中的一个并排观测点。

## VAR: you_2018_degadv_tone_ss

【变体差分】
本列同时启用 deg 与 adv 两条规则 (不含 neg), 文本轨道为 ss (银行∧金科同句±1句窗, 无共现时回退全文并镜像 ctx 语义、共享 n_articles 分母, 详见家族 CORE 节回退语义说明)。该列在三轨×两规则组合矩阵中提供最紧凑语境下的 deg×adv 交互度量, 语境判据要求银行与金科词同句共现, 因而命中词样本天然集中于目标实体紧邻叙事, 程度副词与转折结构的联合调制在此窗口下更贴近"针对该银行金科业务的具体措辞"而非泛泛报道背景。与 ctx/full 两轨互为稳健性并排, 各自 just-identified, 不得混入同一 over-identified Hansen J 设定。该列与 degadv_tone_ctx / degadv_tone_full 构成三轨完整组, 三者的一致性程度是"deg×adv 交互效应是否稳健于文本窗口宽窄选择"这一具体稳健性命题的直接经验依据, 供稳健性附表并排披露而非取平均或择一为准; dev T=2 小样本下 ss 轨受回退语义影响, 与 ctx 轨数值可能高度接近, 生产 T=19 全量语料上二者分化程度才具备实证意义。该列的规则子集 (deg+adv, 不含 neg) 保留了命中词原始极性方向, 仅调制其幅度, 在解释上相较含 neg 的两两组合臂更接近"语调强弱"而非"语调方向"的稳健性检验, 这一区分在解读家族内三个两两组合臂 (degadv/negadv/negdeg) 的实证结果时应予明确, 避免将幅度层面的规则效应与符号层面的规则效应混为一谈。ss 轨最紧凑语境判据下, 该列命中词样本量在 T=2 开发样本上通常有限, 使用者应结合命中词数诊断解读该列的置信区间; 生产 T=19 全量语料上样本规模扩大, 该列与 ctx/full 两轨在数值上的一致性检验才具备充分统计意义, 是本组合臂稳健性主张的最终经验落点。

## VAR: you_2018_degonly_tone_ctx

【变体差分】
本列仅启用 deg (程度副词加权) 一条规则, 不启用 neg 与 adv; 文本轨道为 ctx。状态机只对命中词前是否存在程度副词做幅度调整 (如"非常好"较"好"幅度更大, "略微下滑"较"下滑"幅度更小), 不做否定翻转、不做转折降权, 是理解程度副词规则独立边际贡献的基准臂。与 you_2018_advonly_tone_ctx (仅 adv) 及 you_2018_negonly_tone_ctx (仅 neg) 构成三个单规则基准臂中的一支, 三者共同定位各条规则在孤立状态下 (不与其余规则交互) 对语调分的独立贡献大小——即在保持其余两条规则均关闭的前提下, 单独打开某一条规则相较 raw 裸计数基线所产生的数值位移, 是分解"总规则叠加效应"为三个可加性分量 (在语言学假设下近似线性可加, 但状态机实现层面并非严格线性分解, 需以实证相关系数披露, 参见家族 CORE 节 MATH-1 相关口径) 的第一步。ctx 轨窗口设定与 you_2018_advonly_tone_ctx 一致, 与 you_2018_degonly_tone_full / you_2018_degonly_tone_ss 互为规格稳健性并排、各自 just-identified。程度副词规则对语调分幅度而非方向产生影响, 其效应大小很大程度上取决于中文财经报道中程度副词的使用密度与强度分布, 在实体邻近窗口 (ctx) 下, 由于命中词更聚焦于目标银行金科相关叙事, 该列比 full 轨更能反映"记者在具体评价该银行金科业务时使用的措辞强度", 是理解媒体报道语气强弱而非单纯正负判断的细粒度测度。

## VAR: you_2018_degonly_tone_full

【变体差分】
本列仅启用 deg 规则, 文本轨道为 full。与 you_2018_degonly_tone_ctx 规则子集一致, 仅文本覆盖范围不同 (整篇正文 vs 实体邻近窗口), 是 deg-only 臂在三轨消融矩阵中样本量最大、统计功效通常最高的对应列, 也是 full-only 留篇门控口径下的主轨对应列。程度副词在中文财经报道中出现频率较高 (如"大幅""明显""略微""基本"等修饰语常见于业绩描述), 因而该列相较 advonly/negonly 的 full 轨对应列, 通常拥有更多命中词参与幅度调制, 是三个单规则基准臂中样本利用率相对充分的一支。该列与 you_2018_degonly_tone_ctx / you_2018_degonly_tone_ss 共同构成 deg-only 三轨稳健性组, 三者刻意不设主次: full 轨样本最充分但语境最泛化, ctx 轨语境聚焦银行∧金科实体窗口, ss 轨语境最紧凑但样本量最小, 三者的估计一致性本身即是"程度副词规则对语调分方向性影响是否稳健于文本窗口选择"这一稳健性问题的直接检验对象, 在规格曲线式的稳健性附表中通常并排列出、不取加权平均或择一为准。该列与 advonly_tone_full / negonly_tone_full 构成 full 轨单规则三元组的一员, 三者共同回答"三条语言学规则中哪一条对语调分数值的边际影响最大"这一问题, 但答案本身仅作稳健性梯度披露, 不构成对任一规则子集"更优"的方法学判定, 项目铁律明确各变体互为稳健性、不分主次。

## VAR: you_2018_degonly_tone_ss

【变体差分】
本列仅启用 deg 规则, 文本轨道为 ss (银行∧金科同句±1句窗, 回退语义镜像 ctx)。是 deg-only 臂在最紧凑语境判据下的对应列, 与 ctx/full 两轨互为稳健性并排、不分主次, 各自 just-identified, 不得混入同一 over-identified Hansen J 设定。当银行与金科词并未同句共现时, 该列回退为全文 body 并置位 ss_is_fallback=True, 与 ctx 轨共享同一 n_articles 分母, 不产生单边孤儿样本, 确保三轨在聚合层面的分母口径一致可比。dev T=2 小样本 (110 银行 × 2 年) 上 ss 轨往往因同句共现要求过严导致大比例回退为全文, 该列在生产 T=19 全量语料上才会展现出与 ctx/full 两轨在数值上更充分的分化, 使用者在小样本诊断阶段观察到 ss 轨与 ctx/full 高度接近时不应误判为规则设计有误, 而应理解为回退语义本身的预期表现。该列刻画在最贴近目标实体叙事窗口内单独的程度副词幅度调制效应, 与 degonly_tone_ctx / degonly_tone_full 构成完整三轨组, 三者一致的方向性 (若语调整体偏正或偏负的判断不随文本窗口宽窄反转) 是本家族向下游论文披露"测度结论不依赖文本窗口选择"这一稳健性主张的关键实证支撑之一。作为单规则、最紧凑语境的交叉单元, 该列在信息密度上兼具语义精确与样本量偏小两面, 应与家族其余单规则×三轨的其余 5 列联合观察, 才能完整勾勒规则维度与轨道维度各自独立且互不干扰的边际影响全貌。

## VAR: you_2018_negadv_tone_ctx

【变体差分】
本列同时启用 neg (否定翻转) 与 adv (转折降权) 两条规则, 不启用 deg (程度副词加权); 文本轨道为 ctx。状态机先检测命中词前是否存在否定词, 若存在则翻转该词符号 (正变负、负变正), 再检测该词是否处于转折从句语境并据此降权, 但不做程度副词幅度放缩。Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems)《Negation scope detection in sentiment analysis: Decision support for news-driven trading》对否定辖域检测在新闻驱动情感测度中重要性的论证, 是本变体及其余含 neg 规则臂 (negonly/negdeg/negadv) 的直接方法学支撑——该变体额外叠加转折降权, 用于检验"否定+转折"两种句法反转/弱化机制联合作用下语调分的稳健性。两条规则分别作用于符号层面 (neg) 与幅度层面 (adv), 理论上互不冲突, 但当同一命中词同时落入否定辖域与转折从句时 (如"虽然并非不看好"), 状态机按固定执行顺序先翻转后降权, 该执行顺序本身是实现细节而非语言学必然, 是本组合臂相较单规则臂额外引入的一层测度选择。ctx 轨窗口与 you_2018_advonly_tone_ctx 一致, 与 you_2018_negadv_tone_full / you_2018_negadv_tone_ss 互为规格稳健性并排、各自 just-identified。该列与 degadv_tone_ctx (deg+adv, 不含 neg)、negdeg_tone_ctx (neg+deg, 不含 adv) 构成三个两两组合臂中含 neg 规则的两支之一, 二者相较不含 neg 的 degadv 臂多出符号反转这一相对激进的语义操作, 在实证上通常表现出比 degadv 更大的数值波动, 是判断"否定处理是否是驱动规则组合效应的主要来源"这一具体诊断问题的直接对照对象。

## VAR: you_2018_negadv_tone_full

【变体差分】
本列同时启用 neg 与 adv 两条规则 (不含 deg), 文本轨道为 full。与 you_2018_negadv_tone_ctx 规则子集一致, 差异仅在文本覆盖范围, 是该组合规则在样本量最充分的 full 轨上的对应列, 通常在稳健性表格中作为该规则组合的主力展示臂, 也是 full-only 留篇门控口径下与 P1 (`bank_fintech_tone`) 主轨行宇宙一致的对应列。该列与 negdeg_tone_full / degadv_tone_full 共同构成三个两两组合臂在 full 轨上的完整三元组, 三者互为稳健性、不分主次, 用于展示不同规则两两叠加时对语调分数值与显著性的相对影响。由于该列同时叠加否定符号翻转与转折降权两种反转/弱化机制, 相较单规则臂 (negonly_tone_full/advonly_tone_full) 数值上更接近对语言学修饰全量敏感的极端, 但仍缺少 deg 幅度调制, 三者 (negonly/advonly/negadv 各自的 full 轨) 联合观察可勾勒出规则叠加对语调分的边际递增或递减模式, 是判断规则维度是否驱动主结论的关键诊断组之一。full 轨样本覆盖最广, 使该列成为家族内该两两组合臂中统计功效最高、最适合在正文正式结果表中作为主展示对象的一支, 但依据项目铁律, 该列本身不构成相对 ctx/ss 两轨或相对其余两两组合臂的"优选测度", 仅作规格稳健性梯度上的一个并排观测点。

## VAR: you_2018_negadv_tone_ss

【变体差分】
本列同时启用 neg 与 adv 两条规则 (不含 deg), 文本轨道为 ss (银行∧金科同句±1句窗, 无共现回退全文并镜像 ctx、共享 n_articles 分母)。是该规则组合在最紧凑语境判据下的对应列, 语境要求银行与金科词同句共现, 因而否定与转折的联合修饰效应在此窗口下更贴近针对目标实体本身的具体措辞判断, 而非泛化的整篇报道基调。与 ctx/full 两轨互为稳健性并排、各自 just-identified, 不得混入同一 over-identified Hansen J 设定。ss 轨严格同句判据 (核心原语 core/text/entity_context.py 的严格同句抽取函数, 与 stage 13 共现硬过滤的 ±1句窗判据是两个不同口径, 禁互相复用) 使该列在捕捉"银行与金科在同一句中被否定或转折式表述"这一细粒度叙事时具备较高的语义精确度, 但代价是命中词样本量偏小, 在小样本 (如单一银行单一年份) 下方差可能偏大, 解读该列估计值时应结合样本量诊断。该列与 negadv_tone_ctx / negadv_tone_full 构成三轨完整组, 三者一致的方向性是"否定+转折联合效应是否稳健于文本窗口选择"这一命题的直接证据; 三轨互为规格稳健性并排、各自 just-identified, 禁止在同一 IV 设定中混用作为过度识别工具。

## VAR: you_2018_negdeg_tone_ctx

【变体差分】
本列同时启用 neg (否定翻转) 与 deg (程度副词加权) 两条规则, 不启用 adv (转折降权); 文本轨道为 ctx。状态机先做否定符号翻转, 再对翻转后 (或未翻转) 的词施加程度副词幅度调整, 但不检测转折从句、不做降权处理。该变体用于检验"否定+程度"两种规则联合、且不涉及句式转折修饰时的语调分表现——即在否定翻转确定符号方向后, 程度副词进一步调制该 (可能已翻转) 极性的幅度大小 (如"并非略微下滑"经否定翻转后转为正向, 再叠加"略微"的幅度弱化), 与 negadv (neg+adv, 不含 deg)、degadv (deg+adv, 不含 neg) 构成互补的两两组合三元组, 三个组合恰好穷举"三选二"的规则子集空间, 每一对共享恰好一条规则。ctx 轨窗口设定与家族其余 ctx 列一致, 与 you_2018_negdeg_tone_full / you_2018_negdeg_tone_ss 互为规格稳健性并排、各自 just-identified, 三者禁止混入同一 over-identified Hansen J 设定。相较 negadv_tone_ctx (neg+adv, 不含 deg), 本列以幅度调制 (deg) 替代结构降权 (adv) 与否定翻转联合, 二者的差异反映"程度副词幅度调制"与"转折句式降权"这两种不同机制在与否定规则叠加时对语调分产生的不同边际影响, 是理解 neg 规则与另外两条规则各自交互模式差异的关键对照列。

## VAR: you_2018_negdeg_tone_full

【变体差分】
本列同时启用 neg 与 deg 两条规则 (不含 adv), 文本轨道为 full。与 you_2018_negdeg_tone_ctx 规则子集一致, 差异仅在文本覆盖范围 (整篇正文 vs 实体邻近窗口); 是该规则组合样本量最大的对应列, 也是 full-only 留篇门控口径下与主线论文行宇宙一致的对应列。该列在实证上通常是"否定+程度"组合效应统计功效最高的一支, 因整篇正文覆盖了更多可能同时触发否定与程度修饰的句子。与 negadv_tone_full (neg+adv, 不含 deg)、degadv_tone_full (deg+adv, 不含 neg) 并列, 三者互补覆盖三条规则两两组合的全部情形, 在 full 轨样本量最充分的条件下比较三种组合效应的相对大小, 是判断"哪一条规则在与其余规则交互时贡献最大边际差异"的关键诊断列, 结果仅作稳健性披露、不作为择优选择单一规则子集的依据。该列同时执行符号翻转 (neg) 与幅度调制 (deg), 是三个两两组合臂中较为直观地对应"传统词典法否定处理+强化词处理"这一常见英文金融文本情感分析惯例的组合, 但由于中文语法结构与英文存在系统性差异 (否定词位置、程度副词修饰范围等), 该组合在中文语境下的具体行为特征仍需以家族内部逐轨对照结果作为经验依据, 不应径直套用英文文献结论。

## VAR: you_2018_negdeg_tone_ss

【变体差分】
本列同时启用 neg 与 deg 两条规则 (不含 adv), 文本轨道为 ss (银行∧金科同句±1句窗, 回退语义镜像 ctx)。是该规则组合在最紧凑语境判据下的对应列, 与 ctx/full 两轨互为稳健性并排、各自 just-identified, 不得混入同一 over-identified Hansen J 设定。当银行与金科词未同句共现时回退为全文并置位 ss_is_fallback=True, 与 ctx 轨共享同一 n_articles 分母。该列刻画在最贴近目标实体叙事语境下, 否定翻转与程度幅度调制联合作用的语调分表现, 与 negdeg_tone_ctx / negdeg_tone_full 构成三轨完整组; 在生产 T=19 全量语料上, ss 轨样本量随文章总量扩大而相应扩大, 届时该列相较 T=2 开发样本将展现出更充分的统计功效与更稳定的估计。三轨之间 (ctx/full/ss) 与规则组合维度 (三个两两组合臂) 构成二维正交的规格空间, 本列位于该空间中"最紧凑语境×否定+程度组合"这一特定单元格, 其数值应被解读为该单元格下的稳健性观测点, 而非相对家族内其余单元格的优选或劣选测度。该列与家族内另外两个含 neg 的组合臂 (negadv_tone_ss) 相比, 差异在于叠加规则不同 (deg 而非 adv), 二者共同揭示 neg 规则在与幅度类 (deg) 或结构类 (adv) 规则各自交互时是否表现出不同的方向性或幅度特征, 是判断否定处理规则本身是否为家族内规则效应的主要驱动来源的关键辅助证据之一。

## VAR: you_2018_negonly_tone_ctx

【变体差分】
本列仅启用 neg (否定翻转) 一条规则, 不启用 deg 与 adv; 文本轨道为 ctx。状态机只对命中词前是否存在否定词做符号翻转判定, 不做程度副词幅度调整、不做转折降权, 是三条单规则基准臂中最贴近传统词典法"否定处理"惯例的一支——多数经典英文金融词典法研究 (如 Loughran & McDonald 系列) 在最简版本中也常仅处理否定这一种语境修饰, Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 亦专门论证否定辖域检测在新闻情感测度中的独立重要性, 是本列方法学定位的直接依据。该列与 you_2018_degonly_tone_ctx / you_2018_advonly_tone_ctx 共同定位 neg 规则独立于 deg、adv 时的边际贡献, 三者构成三个单规则基准臂中的一支, 各自 just-identified 并排, ctx 轨窗口设定与家族其余 ctx 列一致。否定处理规则在中文句法中通常表现为情感词前的否定副词 (如"不""没有""未""无""难以"等), 状态机须在扫词状态机中维护否定词的检测辖域范围 (向前若干词的窗口), 该辖域设定本身即是词典法情感测度中的一处方法学选择, 与 Pröllochs, Feuerriegel & Neumann (2016) 所论证的否定辖域检测挑战直接对应; 本列作为单独隔离该规则效应的基准臂, 是评估该辖域设定选择本身对最终语调分影响大小的起点。

## VAR: you_2018_negonly_tone_full

【变体差分】
本列仅启用 neg 规则, 文本轨道为 full。与 you_2018_negonly_tone_ctx 规则子集一致, 文本覆盖范围为整篇正文, 是 neg-only 臂样本量最充分的对应列, 也是 full-only 留篇门控口径下与主线论文行宇宙一致的对应列。否定词在中文财经报道中的出现频率与句法位置较程度副词更为规则化 (常紧邻情感词之前), 使得该列在三个单规则臂中通常具有相对稳定的检测精度, 与 degonly_tone_full / advonly_tone_full 共同构成 full 轨上的单规则三元组, 互为稳健性、不分主次。该三元组连同 raw_tone_full 基线共同构成"零规则 + 三个单规则"的四点比较组, 是本家族用以逐一分解各条语言学规则独立边际贡献 (相对裸计数基线的位移量) 的核心比较单元, 在稳健性附表中通常以 raw 为参照列并排展示三个单规则臂的偏离方向与幅度。该四点比较组是本家族向下游论文交付"语言学规则精细化对语调分是否产生实质性数值位移"这一核心稳健性主张的最小充分观测集: 若三个单规则臂相对 raw 的位移方向一致且幅度接近, 说明语调分对规则选择相对不敏感; 若出现方向分歧或幅度悬殊, 则须在论文正文明确披露该敏感性, 而非默认采用某一规则子集作为唯一口径。

## VAR: you_2018_negonly_tone_ss

【变体差分】
本列仅启用 neg 规则, 文本轨道为 ss (银行∧金科同句±1句窗, 回退语义镜像 ctx)。是 neg-only 臂在最紧凑语境判据下的对应列, 与 ctx/full 两轨互为稳健性并排、不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定。当银行与金科词未同句共现时该列回退为全文 body 并置位 ss_is_fallback=True, 与 ctx 轨共享同一 n_articles 分母, 不产生单边孤儿样本。该列在最贴近目标实体的语境窗口内单独捕捉否定翻转规则的效应, 与 negonly_tone_ctx / negonly_tone_full 构成完整三轨组, 三者的一致性程度可作为"否定处理规则对语调分方向性影响是否稳健于文本窗口宽窄"这一具体稳健性命题的直接实证依据, 供稳健性附表并排披露。作为家族内规则维度最简单 (单规则) 与轨道维度最紧凑 (ss) 的交叉单元, 该列在信息密度上代价与收益并存: 语义精确度最高但样本方差也可能最大, 使用者在生产 T=19 全量语料上应结合样本量诊断 (如命中词数分布) 判断该列估计值的可信区间宽窄, 不宜脱离样本规模孤立解读点估计。该列与家族内 raw_tone_ss 基线相比多出否定翻转这一符号层面的规则调制, 二者差值即为 neg 规则在最紧凑语境下相对裸计数基线产生的边际数值位移, 是本家族"规则叠加是否显著改变语调分布"这一核心稳健性问题在最细粒度语境判据下的直接观测点。

## VAR: you_2018_raw_tone_ctx

【变体差分】
本列不启用 neg、deg、adv 任何一条语言学规则, 是三条规则维度上的裸计数基线——状态机对每个命中词只按 you_2018 词典原始极性 (positive/negative) 与固定权重 (幅度恒为 1, 不做否定翻转、不做程度放缩、不做转折降权) 计入求和, 再做 Σ|final| 自归一化; 文本轨道为 ctx。该列是本家族 7 个非-full 变体中方法学上最简单的一支, 用作衡量"叠加任一或任几条语言学规则相较裸词频计数带来多大边际改进/差异"的锚点参照, 对应 You, Zhang & Zhang (2018, Review of Financial Studies) 原文所采用的简单词频法精神 (该文本身未内生 neg/deg/adv 规则, 仅按词典正负词计数构造语调指标)。作为家族内规则维度上的"零点"参照, raw 系列三列 (ctx/full/ss) 与其余 7 个规则子集变体在同一词典、同一文本轨道条件下逐一比较, 可分解出各条规则乃至规则组合相较裸计数的边际数值位移, 是本家族消融设计的锚点起点。ctx 轨窗口设定与家族其余 ctx 列一致, 与 you_2018_raw_tone_full / you_2018_raw_tone_ss 互为规格稳健性并排、各自 just-identified。由于该列是家族内规则维度上的零点, 其数值全部由 you_2018 词典本身的正负词命中构成, 不受任何语言学修饰规则调制, 是评估词典本身极性覆盖质量 (而非规则设计质量) 的天然观测窗口——若该列在 ctx 轨的数值分布出现系统性异常 (如极端集中于零附近), 应首先排查词典命中率或实体窗口物化是否存在上游数据问题, 而非误判为规则消融设计本身的缺陷。

## VAR: you_2018_raw_tone_full

【变体差分】
本列为裸计数基线 (不启用任何语言学规则), 文本轨道为 full (标题+正文全文)。是家族 21 列中方法学上最简单且样本覆盖面最广的一列, 常被用作 P1 (`bank_fintech_tone`) 及相关论文稳健性附表中与规则增强变体 (raw vs negonly/degonly/advonly/…) 对比的基准起点, 用以直观展示语言学规则精细化对语调分数值大小与统计推断结论的影响幅度; 也是 full-only 留篇门控口径 (2026-06-29) 下与主线论文行宇宙完全一致的对应列, 三轨中样本覆盖最广、统计功效通常最高。由于 raw 变体不做任何符号或幅度修饰, 该列数值波动主要来自命中词本身的极性构成与数量, 是理解本家族"规则叠加是否显著改变语调分布"这一稳健性问题的天然基准。该列在方法学谱系上最贴近 You, Zhang & Zhang (2018) 原文简单词频计数法的精神, 也是家族内与规则增强变体做直接数值对比时最常被引用的参照列; 若该列与其余 6 个非-full full 轨变体 (advonly/degonly/negonly/negdeg/negadv/degadv 各自的 full 轨) 高度相关, 说明语言学规则精细化对本家族语调分的边际改进有限, 该结论本身是稳健性附表应披露的信息, 不构成对规则设计价值的否定。

## VAR: you_2018_raw_tone_ss

【变体差分】
本列为裸计数基线 (不启用任何语言学规则), 文本轨道为 ss (银行∧金科同句±1句窗, 无共现时回退全文并镜像 ctx 语义、共享 n_articles 分母)。是裸计数基线在三轨中语境最紧凑的对应列, 与 ctx/full 两轨互为稳健性并排、各自 just-identified, 不得混入同一 over-identified Hansen J 设定。ss 轨判据要求银行与金科词在同一句 (或±1句窗) 共现方纳入该窗口文本, 该判据与本列的规则维度选择 (raw, 无语言学规则) 正交——即 ss 轨的紧凑语境判据决定"用哪些句子参与计数", 而 raw 规则子集决定"命中词如何计入总和", 二者互不干扰、可独立组合, 与家族内其余变体×轨道的正交设计一致。该列是家族 21 列中语境最紧凑且规则维度最简单的交叉单元, 是理解"文本窗口收窄"与"语言学规则关闭"两个独立维度各自及联合对语调分产生何种边际影响的基准参照点; 与 raw_tone_ctx / raw_tone_full 构成完整三轨组, 三者的相对差异应主要归因于窗口宽窄而非规则选择 (因规则维度在三者间保持恒定为零)。该列也是家族内 7 个非-full 规则子集变体各自 ss 轨 (advonly/degadv/degonly/negadv/negdeg/negonly/raw 共 7 列) 中方法学上最简单的一支, 在稳健性附表中通常与 raw_tone_ctx / raw_tone_full 并列作为 ss 轨规则效应分解的零点参照, 供研究者逐一核对规则叠加在最紧凑语境判据下是否依旧保持与 ctx/full 两轨一致的方向性结论。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Oh, N. (2024). Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries. Proceedings of the International AAAI Conference on Web and Social Media, 18, 2003-2013. https://doi.org/10.1609/icwsm.v18i1.31443
<!-- rendered-citations:end -->
