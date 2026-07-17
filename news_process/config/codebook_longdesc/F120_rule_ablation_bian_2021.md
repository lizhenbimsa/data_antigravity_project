---
family_id: F120
novelty_exempt_rationale: "rule_ablation_bian_2021 是词典消融变体家族(否定/程度副词/转折三语言学规则全 powerset 物化), 其测度定义依据母族 bian_2021 词典及既有情感词典文献, 非独立新构念, 不需单独追新文献。"
columns:
- bian_2021_advonly_tone_ctx
- bian_2021_advonly_tone_full
- bian_2021_advonly_tone_ss
- bian_2021_degadv_tone_ctx
- bian_2021_degadv_tone_full
- bian_2021_degadv_tone_ss
- bian_2021_degonly_tone_ctx
- bian_2021_degonly_tone_full
- bian_2021_degonly_tone_ss
- bian_2021_negadv_tone_ctx
- bian_2021_negadv_tone_full
- bian_2021_negadv_tone_ss
- bian_2021_negdeg_tone_ctx
- bian_2021_negdeg_tone_full
- bian_2021_negdeg_tone_ss
- bian_2021_negonly_tone_ctx
- bian_2021_negonly_tone_full
- bian_2021_negonly_tone_ss
- bian_2021_raw_tone_ctx
- bian_2021_raw_tone_full
- bian_2021_raw_tone_ss
unit: 语调得分 (连续, 约 [-1,1]; 文章级自归一化, bank-year 留篇均值聚合)
formula: "逐词状态机在指定语言学规则子集下产出带符号强度 final_i; 文章级 tone = Σ final_i / Σ|final_i| ∈ [-1,1]; bank-year 聚合取 full-only 留篇集内均值"
producer: news_process/pipeline/sentiment/tone_words.py (_compute_sentiment_with_rules 逐词状态机 + _analyze_single_article 内 _RULE_ABLATION_VARIANTS 消融物化循环) ; 聚合 pipeline/panel/export.py ; 标签 pipeline/panel/stata_export.py
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
  pages_or_artno: 20
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: "No. 3446388"
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是以 Bian, Jia, Li 与 Yan (2021) 中文金融情感词典为极性词表、在受控语言学规则子集下计算得到的银行年度媒体语调, 并以此构成一条"规则消融梯度"。Bian 等 (2021) 针对中文会计与金融文本构建了一部本土情感词典, 弥补了将英文 Loughran 与 McDonald (2011) 词表直译到中文语境时产生的领域与语言错配。词典法给出情感倾向的可复现、可审计的基线, 但一个长期悬而未决的方法学问题是: 裸词计数之外的语言学修饰规则 (否定翻转、程度副词缩放、转折让步调整) 究竟在多大程度上驱动最终语调测度。本家族把这个问题物化为一条并排的消融阶梯, 让规则集合本身成为一个可稳健性检验的设计维度。

【方法学与计算】
计算入口是 tone_words.py 中的逐词状态机式打分器 _compute_sentiment_with_rules。它逐词扫描分词后的文本, 命中 Bian 词典的极性词即赋予带符号的基础强度, 随后按三条可独立开关的语言学规则调整: 否定翻转 (邻近否定词时翻转极性符号)、程度副词缩放 (程度副词放大或收缩强度)、转折让步 (转折连词后分句重定权重)。文章级语调采用自归一化式 Σ final_i / Σ|final_i|, 值域约束在 [-1,1], 从而消去篇幅差异。三条规则的全部组合由单一事实源 _RULE_ABLATION_VARIANTS 枚举, 消融变体的物化循环位于 _analyze_single_article 内 (对每一旗标三元组各调一次 _compute_sentiment_with_rules): raw 为零规则基线 (三旗全关), negonly / degonly / advonly 各只开一条, negdeg / negadv / degadv 各开两条; 三旗全开的 full-rules 版本即无后缀的 canonical 主列 bian_2021_tone, 刻意不入本谱而单独物化。因此本家族恰为 7 个非-full 变体 × 三轨 (full / ctx / ss) = 21 列。银行年度聚合取该银行当年留篇集内的文章级均值, 分母口径遵循 2026-06-29 起的 full-only 留篇门控: 一篇报道是否计入取决于 llm_verified_full, ctx 与 ss 轨为条件于 full 留篇集的子集测度。三轨文本来源在 stage 14 物化: full = 标题 prepend 全文正文, ctx = 标题加实体窗口, ss = 标题加银行与金科同句共现窗, 且 ss 在无同句共现时优雅回退镜像 ctx 的全文 body。

【文献定位】
本谱与主流金融文本测度文献的方法学关切一脉相承。García, Hu 与 Rohrer (2023) 用市场反应校准情感词的"颜色", 论证词表构造细节对测度有效性的实质影响, 与本谱把规则集合当作设计自由度的立场同源。Frankel, Jennings 与 Lee (2022) 系统比较词典法与机器学习法, 确立"多测度互为稳健性"的范式, 本项目正是以三种情感法 (LLM / 词典 / BERT) 并排、并在词典法内部再展开规则消融来落实这一范式。Du, Huang, Wermers 与 Wu (2022) 的中文金融词典工作提示领域与语言特异性对中文情感测度不可忽略, 支持本谱选用中文本土的 Bian 词典而非英文直译词表。规则层面, Taboada 等 (2011) 系统化了词典法中否定、程度与转折的处理算子, Pröllochs, Feuerriegel 与 Neumann (2016) 与 Punetha 与 Jain (2025) 进一步论证否定作用域检测对新闻驱动情感测度的边际贡献, 三者共同为本谱的否定 / 程度 / 转折三开关提供文献依据。需要强调的方法学纪律: 七个消融变体各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则子集混进同一 over-identified Hansen J; 同理三轨与该消融梯度正交, 亦不得跨轨混入同一过度识别检验。审计口径 (MATH-1) 已注明各变体高度共线 (相关系数近 0.99), 故报告相关性而非并入同一可加分解式, 变体间为"定性不变"的稳健性叙事, 而非声称某一规则子集在测度上更优。 在测量误差的一般层面, Iqbal 与 Pfarrer (2025) 针对多主体文本中的情感归属问题引入共指消解 (coreference resolution), 并以两项研究证明该处理可降低文本分析的测量误差、提升测度的真实性, 佐证了"单一语言学处理选择即可系统性改变文本测度取值、并构成实质性测量误差来源"这一般命题, 与本谱不把任何规则配置默认为真值、而是显式物化其后果的立场相通。其迁移边界须严格限定: 该文所处理的是共指消解 (实体指代还原), 与本谱的否定翻转、程度副词缩放、转折让步三规则并非同一规则, 亦非本谱消融梯度的方法学来源; 该文立场是规范性的, 主张采纳该规则以减少误差 (即存在唯一正确做法), 与本谱令七臂互为稳健性并排、不设主次的取向不同, 故不得据以主张 powerset 规则消融存在同构先例; 其实体归属问题在本项目内对应的是 ctx 与 ss 实体窗口轨而非本消融族; 且原文语料为英文组织管理文本, 单位为文档与组织, 与本谱的中文银行金科新闻及银行年度聚合口径不同。
## VAR: bian_2021_advonly_tone_ctx

【变体差分】
本列为 advonly 变体、ctx 轨。advonly 在 _RULE_ABLATION_VARIANTS 中对应旗标 (False, False, True): 只开转折让步规则, 关闭否定翻转与程度副词缩放。即极性词的基础符号与强度均保持裸值, 唯在遇到转折连词 (如"但""然而""不过") 时按让步逻辑对前后分句重定权重。相对 canonical 的 full-rules 主列, 本列等价于"从全规则中同时抽掉否定与程度两条", 因而隔离出转折规则对 Bian 词典中文语调的单独贡献。ctx 轨的文本载体是 content_ctx, 即标题 prepend 后拼接目标银行实体上下文窗口, 而非整篇正文, 使语调聚焦于与银行实体邻近的表述, 抑制远离主体的无关段落噪声。因转折在中文新闻的让步句式中承载情感反转的关键信息, advonly 单独臂常用于检验"仅靠转折调整能否复现主测度的定性方向"。本列与 negonly、degonly 等其余六个消融臂各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与三轨维度正交, 亦不与 full / ss 轨跨轨混入同一过度识别检验。聚合分母遵循 full-only 留篇门控, ctx 为条件于 full 留篇集的子集测度。

在消融格中, advonly 属 L1 单规则臂 (只叠转折一条), 与 raw 基线之差正好估计转折让步规则在 ctx 轨的单独边际, 与 degadv 之差则估计"在有转折前提下再加程度"的增量。审计 MATH-1 已注明三条单规则臂各自与 raw 的差之和一般不等于全规则主列与 raw 之差, 因规则间存在交互项 (非可加分解), 故本谱不把各臂并入同一可加式, 只两两报告相关。聚合层面, 文章级经 Σ|final_i| 自归一化抵消篇幅后, bank-year 值取该行当年 full 留篇集内文章均值, ctx 缺列时跳轨而不借 full 轨分母。

## VAR: bian_2021_advonly_tone_full

【变体差分】
本列为 advonly 变体、full 轨。规则子集与上一列同为 (False, False, True): 仅启用转折让步、停用否定翻转与程度缩放, 隔离转折规则对 Bian 中文金融语调的边际效应。差别在轨道: full 轨的文本载体是 content_full, 即标题 prepend 后接整篇正文, 是覆盖面最广的文本视角, 也是本项目留篇门控与 canonical 主测度所依托的口径。因此在三轨中, full 轨的 advonly 值最直接对照无后缀主列 bian_2021_tone (full-rules, full 轨), 二者之差纯粹归因于否定与程度两条规则的缺席, 为"转折是否为主要驱动"提供最干净的对照。full 轨样本覆盖全部通过 llm_verified_full 门控的银行金科报道, 是三轨中分母最完整者, ctx 与 ss 轨均为其子集。本列与其余六消融臂、与其他两轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则子集或不同轨混入同一 over-identified Hansen J。变体间高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解, 叙事为定性稳健而非择优。

在消融格里 advonly-full 与 raw-full 之差是转折规则在全文视角下最完整的单独边际估计, 与 negadv-full、degadv-full 联读可从多臂交叉定位转折的贡献稳定性。因全文轨样本分母最大, 本列的均值估计方差最小, 常被选作规格曲线 (specification curve) 里转折维度的代表点。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。转折在长文本中触发的让步反转较实体窗更多, 故 full 轨最能暴露 advonly 与全规则主列的潜在背离。

## VAR: bian_2021_advonly_tone_ss

【变体差分】
本列为 advonly 变体、ss 轨。规则子集仍为 (False, False, True): 只开转折让步。ss 轨文本载体是 content_ss, 即标题 prepend 后拼接银行与金科同句共现窗口 (窗宽由 filtering.yaml 的 ss_sentence_radius 控制, 默认 ±1 句), 是三轨中语义最聚焦、对"银行谈金科"这一具体语境最敏感的视角。关键回退语义: 当某篇报道不存在银行与金科的同句共现时, content_ss 优雅回退镜像 content_ctx 的全文 body, 并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 避免样本坍缩。因此 ss 轨的 advonly 值在有共现篇章上反映"银行金科同句语境下、仅转折调整的语调", 在回退篇章上退化为 ctx 口径。转折让步在这一狭窄语境窗内可能因句内让步结构而作用有限, 故 ss-advonly 更多充当稳健性下界探针。本列与其余消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。聚合遵循 full-only 门控, ss 为条件于 full 留篇集的子集测度。

ss-advonly 处于"最聚焦语境 + 单转折规则"的格点, 其与 ss-raw 之差在有共现篇章上估计转折规则在同句语境的边际, 在回退篇章上则退化为 ctx 口径下的对应差。由于同句窗多为单句或近邻句, 让步转折结构在此稀疏, 本列相对 ss-raw 的偏移通常最小, 从下界方向印证转折规则对聚焦语调的有限作用。聚合层面, 有共现与回退两类篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比, 缺列不借他轨分母。

## VAR: bian_2021_degadv_tone_ctx

【变体差分】
本列为 degadv 变体、ctx 轨。degadv 对应旗标 (False, True, True): 同时启用程度副词缩放与转折让步, 唯独关闭否定翻转。它等价于"从 full-rules 中抽掉否定规则", 因而与无后缀主列之差纯粹归因于否定处理的缺席, 是检验"否定翻转是否为语调主要驱动"的直接对照臂。程度副词缩放使"显著改善""大幅下滑"等表述获得放大或收缩的强度, 转折让步处理让步句的情感反转, 二者叠加但不触碰符号翻转。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 语调聚焦银行实体邻近表述。在中文新闻里否定句式频繁, 故 degadv 相对 negonly 系列往往呈现最能凸显"缺否定"后果的对照。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与三轨正交不跨轨混检。变体间高度共线, 报告相关性而非可加分解, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

degadv 属 L2 双规则臂, 在消融格中恰为"全规则减否定", 与 negdeg (全规则减转折)、negadv (全规则减程度) 三者共同从三个方向逼近全规则主列, 每一臂与主列之差分别隔离被省略的那一条规则。degadv 与主列在 ctx 轨之差即否定翻转的边际估计。审计 MATH-1 提示三条双规则臂之差不可加总还原, 因交互项存在, 故只报告相关不并入同一分解式。聚合遵循 full-only 门控, 自归一化后 bank-year 取当年 full 留篇集内文章均值, ctx 缺列跳轨。

## VAR: bian_2021_degadv_tone_full

【变体差分】
本列为 degadv 变体、full 轨。规则子集同为 (False, True, True): 程度缩放与转折让步并用、独缺否定翻转。轨道为 full, 文本载体 content_full = 标题 prepend 加整篇正文, 是三轨中覆盖最广、样本分母最完整的视角, 也是最直接对照 canonical 主列 (full-rules, full 轨) 的口径。full 轨 degadv 与主列之差干净地隔离否定规则对 Bian 中文语调的边际贡献: 若二者定性方向一致, 说明否定翻转在本语料上非主导驱动; 若显著背离, 则提示否定处理承载关键情感信息, 需在稳健性叙事中披露。程度与转折两条规则在全文视角下对长句、复合句的情感强度重估更充分, 因此 full 轨是评估这两条规则联合效应的最佳载体。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。变体高度共线, 报告相关性, 聚合遵循 full-only 门控。

degadv-full 与全规则主列在 full 轨之差是否定规则在全文视角下最完整的边际估计, 与 negonly-full 相对 raw-full 的差可交叉印证否定贡献的量级一致性。因否定在中文金融新闻中高频触发, 本列相对全规则主列的背离往往在三条双规则臂中最显著, 是评估"缺否定"后果的关键探针。全文轨分母最大使估计最稳, 常作规格曲线中否定维度的代表点。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。

## VAR: bian_2021_degadv_tone_ss

【变体差分】
本列为 degadv 变体、ss 轨。规则子集 (False, True, True): 程度缩放加转折让步、无否定翻转。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 是语义最聚焦于"银行谈金科"语境的视角。无同句共现时 content_ss 优雅回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母, 防样本坍缩。在狭窄的同句窗内, 程度副词对局部情感强度的缩放最直接可辨, 而否定的缺席在短窗中可能影响有限, 故 ss-degadv 兼具"聚焦语境 + 无否定"双重特征, 是最锐利的边际探针之一。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨维度与消融梯度正交, 不跨轨混检。聚合遵循 full-only 留篇门控, ss 为条件于 full 留篇集的子集测度, 变体间高度共线故报告相关性而非并入同一可加分解式。

ss-degadv 位于"最聚焦语境 + 缺否定双规则"的格点, 与 ss 全规则轨之差在同句语境下隔离否定翻转的边际。因同句窗中否定词多紧邻极性词, 缺否定在此语境的后果可能被放大, 使本列成为观察否定误计在聚焦语境影响的敏感探针。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_degonly_tone_ctx

【变体差分】
本列为 degonly 变体、ctx 轨。degonly 对应旗标 (False, True, False): 只开程度副词缩放, 关闭否定翻转与转折让步。它把 Bian 词典的情感测度约化为"裸极性 + 程度强度重估", 隔离出程度副词单条规则的贡献。相较 raw 基线, degonly 仅多一层强度缩放而不改符号, 故二者之差纯粹反映程度副词对语调幅度的调节; 相较 full-rules 主列, 它缺否定与转折两条, 是"仅程度"最小规则臂。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 使度量聚焦银行实体邻近表述, 抑制远端噪声。中文金融新闻中程度副词 (大幅、显著、略微) 密度高, 故 degonly 常呈现相对 raw 可观的幅度重估, 但因不动符号, 其与 raw 的极性方向高度一致。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。变体高度共线, 报告相关性, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

degonly 属 L1 单规则臂, 与 raw 之差正好估计程度副词缩放在 ctx 轨的单独边际, 与 negdeg 之差则估计"在有程度前提下再加否定"的增量。因程度规则只改幅度不动符号, 本列与 raw 的极性方向应逐篇一致, 差异集中在数值大小, 这一性质使 degonly 特别适合检验"幅度重估是否改变语调结论方向"。审计 MATH-1: 单规则臂差不可加总还原, 故报告相关。聚合遵循 full-only 门控, 自归一化后 bank-year 取当年 full 留篇集内均值, ctx 缺列跳轨。

## VAR: bian_2021_degonly_tone_full

【变体差分】
本列为 degonly 变体、full 轨。规则子集 (False, True, False): 仅程度副词缩放。full 轨文本载体 content_full = 标题 prepend 加整篇正文, 覆盖最广、分母最完整。在全文视角下, 程度副词对长文本累计情感强度的重估最充分, 故 full 轨是评估"单靠程度缩放"效应的主载体。本列与 raw-full 之差纯归因于程度规则, 与 canonical 主列 (full-rules) 之差则揭示"缺否定与转折"的后果。由于程度规则不翻转符号, degonly-full 与 raw-full 的极性方向应高度吻合, 主要差异在数值幅度; 若二者定性一致, 说明程度缩放不改变语调结论方向, 支撑主测度对该规则设定的稳健性。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则子集或不同轨混进同一 over-identified Hansen J。变体间高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解, 聚合遵循 2026-06-29 full-only 留篇门控。

degonly-full 与 raw-full 之差是程度规则在全文视角的最完整单独边际, 与 degadv-full、negdeg-full 联读可交叉定位程度贡献。因全文长句多含程度副词, 本列相对 raw 的幅度重估在三轨中最充分, 但因不动符号其极性方向仍与 raw 逐篇一致, 支撑"程度缩放不改变结论方向"的稳健叙事。全文轨分母最大使均值估计最稳, 常作规格曲线中程度维度代表点。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。

## VAR: bian_2021_degonly_tone_ss

【变体差分】
本列为 degonly 变体、ss 轨。规则子集 (False, True, False): 仅程度副词缩放。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 语义最聚焦。无同句共现时回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母。在同句窗内程度副词直接修饰局部极性词, 其强度缩放作用清晰可辨, 而缺否定与转折使本列成为"最小规则 + 最聚焦语境"的组合, 适合作为语调幅度对程度规则敏感性的下界探针。因不动符号, ss-degonly 与 ss-raw 的极性方向应一致, 差异集中于幅度。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三轨与消融梯度正交不跨轨混检。聚合遵循 full-only 门控, ss 为条件于 full 留篇集的子集测度, 变体高度共线故报告相关性而非可加分解。

ss-degonly 位于"最聚焦语境 + 单程度规则"格点, 与 ss-raw 之差在同句语境隔离程度缩放的边际, 因不动符号二者极性方向逐篇一致。同句窗内程度副词直接修饰邻近极性词, 使幅度缩放在此语境清晰可辨, 本列可作语调幅度对程度规则敏感性的下界探针。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借他轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_negadv_tone_ctx

【变体差分】
本列为 negadv 变体、ctx 轨。negadv 对应旗标 (True, False, True): 同时启用否定翻转与转折让步, 唯独关闭程度副词缩放。它等价于"从 full-rules 中抽掉程度规则", 因而与无后缀主列之差纯归因于程度副词缩放的缺席, 是检验"程度强度重估是否驱动语调"的对照臂。否定翻转处理"不""未""难以"等对极性符号的反转, 转折让步处理让步句情感反转, 二者叠加而不触碰强度缩放。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 使度量聚焦银行邻近表述。由于否定与转折均直接关乎极性方向, negadv 系列往往在符号层面最贴近 full-rules, 主要差异来自被省略的幅度缩放。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨正交不跨轨混检。变体高度共线, 报告相关性, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

negadv 属 L2 双规则臂, 在消融格中为"全规则减程度", 与 negdeg、degadv 三臂从三方向逼近全规则主列。negadv 与主列在 ctx 轨之差即程度副词缩放的边际估计。因否定与转折两条极性方向类规则齐备, 本列在符号层面最贴近主列, 差异主要来自被省略的幅度缩放, 故与主列相关通常较高。审计 MATH-1: 三双规则臂差不可加总还原, 交互项使然, 只报告相关。聚合遵循 full-only 门控, 自归一化后 bank-year 取当年 full 留篇集内均值, ctx 缺列跳轨。

## VAR: bian_2021_negadv_tone_full

【变体差分】
本列为 negadv 变体、full 轨。规则子集 (True, False, True): 否定翻转加转折让步、无程度缩放。full 轨文本载体 content_full = 标题 prepend 加整篇正文, 覆盖最广、分母最完整, 最直接对照 canonical 主列。full 轨 negadv 与主列之差干净地隔离程度规则的边际贡献: 若二者定性方向一致, 说明程度副词缩放不改变语调结论方向, 支撑主测度对该规则设定稳健; 若背离, 则提示程度强度信息不可忽略, 需在稳健性叙事披露。因否定与转折两条极性方向类规则齐备, negadv-full 在符号结构上与 full-rules 主列高度一致, 二者常呈现三轨中最高的相关。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁把不同规则子集或不同轨混进同一 over-identified Hansen J。变体高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解, 聚合遵循 full-only 留篇门控。

negadv-full 与全规则主列之差是程度规则在全文视角的最完整边际, 与 degonly-full 相对 raw-full 的差可交叉印证程度贡献量级。因否定与转折齐备, 本列在三轨中通常与主列相关最高, 是消融梯度里符号结构最接近全规则的双规则臂之一。全文轨分母最大使估计最稳, 若本列与主列高度吻合, 即支撑"程度幅度信息对结论方向非主导"的稳健结论。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。

## VAR: bian_2021_negadv_tone_ss

【变体差分】
本列为 negadv 变体、ss 轨。规则子集 (True, False, True): 否定翻转加转折让步、无程度缩放。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 语义最聚焦于"银行谈金科"语境。无同句共现时回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母, 防样本坍缩。在同句窗内, 否定翻转对短句极性符号的反转最关键, 转折让步在句内让步结构下亦有作用, 二者兼备使 ss-negadv 在符号层面最能复现聚焦语境下的语调方向, 仅缺程度幅度重估。本列适合作为"聚焦语境 + 极性方向类规则齐备"的对照臂, 检验程度规则在狭窄语境的边际。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨与消融梯度正交。聚合遵循 full-only 门控, ss 为条件于 full 留篇集子集测度, 变体高度共线故报告相关性。

ss-negadv 位于"最聚焦语境 + 缺程度双规则"格点, 与 ss 全规则轨之差在同句语境隔离程度规则边际。因否定与转折两条方向类规则在短窗内齐备, 本列在符号层面最能复现聚焦语调的方向, 仅缺幅度重估, 适合验证"程度规则在狭窄语境边际有限"。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_negdeg_tone_ctx

【变体差分】
本列为 negdeg 变体、ctx 轨。negdeg 对应旗标 (True, True, False): 同时启用否定翻转与程度副词缩放, 唯独关闭转折让步。它等价于"从 full-rules 中抽掉转折规则", 因而与无后缀主列之差纯归因于转折让步的缺席, 与前述 advonly 系列 (只留转折) 恰构成互补对照, 共同定位转折规则的贡献边界。否定翻转管极性符号反转, 程度缩放管强度幅度, 二者兼备使 negdeg 在符号与幅度两方面都接近 full-rules, 唯独不处理让步句的情感反转。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 聚焦银行邻近表述。由于转折句在正文中相对稀疏而在实体窗内更少, ctx-negdeg 常与 full-rules 主列的对应轨高度吻合。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三轨正交不跨轨混检。变体高度共线, 报告相关性, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

negdeg 属 L2 双规则臂, 为"全规则减转折", 与 advonly (只留转折) 恰成互补: 前者与主列之差自上而下估计转折边际, 后者与 raw 之差自下而上估计转折边际, 两侧夹逼定位转折贡献。因否定与程度两条最常触发的规则齐备, 本列在 ctx 轨与主列相关通常极高。审计 MATH-1: 双规则臂差不可加总还原, 只报告相关。聚合遵循 full-only 门控, 自归一化后 bank-year 取当年 full 留篇集内均值, ctx 缺列跳轨不借他轨分母。

## VAR: bian_2021_negdeg_tone_full

【变体差分】
本列为 negdeg 变体、full 轨。规则子集 (True, True, False): 否定翻转加程度缩放、无转折让步。full 轨文本载体 content_full = 标题 prepend 加整篇正文, 覆盖最广、分母最完整, 最直接对照 canonical 主列。full 轨 negdeg 与无后缀主列之差干净地隔离转折规则的边际贡献: 若二者定性一致, 说明转折让步不改变语调方向, 支撑主测度对该规则稳健; 与 advonly-full (只留转折) 联读则可从两侧夹逼转折规则的作用大小。因否定与程度两条最常触发的规则齐备, negdeg-full 在三轨中通常与 full-rules 主列相关最高, 是消融梯度里最接近全规则的臂之一。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则子集或不同轨混进同一 over-identified Hansen J。变体高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解式, 聚合遵循 2026-06-29 起的 full-only 留篇门控。

negdeg-full 与全规则主列之差是转折规则在全文视角的最完整边际, 与 advonly-full 相对 raw-full 的差从两侧交叉定位转折贡献量级, 二者若一致即印证转折边际估计稳健。因否定与程度齐备, 本列在三轨中与主列相关通常最高, 是消融梯度里最接近全规则的臂。全文轨分母最大使估计最稳, 常作规格曲线中最接近主测度的参照点。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。

## VAR: bian_2021_negdeg_tone_ss

【变体差分】
本列为 negdeg 变体、ss 轨。规则子集 (True, True, False): 否定翻转加程度缩放、无转折让步。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 语义最聚焦。无同句共现时回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母。在同句窗内否定翻转与程度缩放同时作用于局部极性词, 既管符号又管幅度, 使 ss-negdeg 成为聚焦语境下最接近全规则的臂, 仅缺转折让步; 而狭窄窗内转折句本就稀少, 故本列常与 ss 轨全规则测度高度吻合, 适合验证"在最聚焦语境下转折规则近乎无关"。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三轨与消融梯度正交不跨轨混检。聚合遵循 full-only 门控, ss 为条件于 full 留篇集子集测度, 变体高度共线故报告相关性而非可加分解。

ss-negdeg 位于"最聚焦语境 + 缺转折双规则"格点, 与 ss 全规则轨之差在同句语境隔离转折边际。因狭窄同句窗内让步转折结构本就稀少, 本列常与 ss 全规则测度高度吻合, 从下界方向印证"最聚焦语境下转折近乎无关"。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_negonly_tone_ctx

【变体差分】
本列为 negonly 变体、ctx 轨。negonly 对应旗标 (True, False, False): 只开否定翻转, 关闭程度缩放与转折让步。它是消融梯度里最经典的单规则臂, 且与既有手写列 bian_2021_negonly 字节一致 (相同旗标产相同输出, golden-safe, 旧 call site 已折入本谱)。否定翻转处理"不""未""无""难以"等对极性符号的反转, 是中文情感测度中最常被单列讨论的规则; Pröllochs 等 (2016) 与 Punetha 与 Jain (2025) 均论证否定作用域检测对新闻情感的边际贡献。相较 raw 基线, negonly 仅多一层符号翻转, 故二者之差纯反映否定规则单独效应。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 聚焦银行邻近表述。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨正交不跨轨混检。变体高度共线, 报告相关性, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

negonly 属 L1 单规则臂, 与 raw 之差正好估计否定翻转在 ctx 轨的单独边际, 与 negdeg 之差则估计"在有否定前提下再加程度"的增量。否定是中文金融新闻里最频繁触发极性反转的规则, 故本列相对 raw 的符号修正在三条单规则臂中通常最大。审计 MATH-1: 单规则臂差不可加总还原, 交互项使然, 只报告相关。聚合遵循 full-only 门控, 自归一化后 bank-year 取当年 full 留篇集内文章均值, ctx 缺列跳轨不借他轨分母。

## VAR: bian_2021_negonly_tone_full

【变体差分】
本列为 negonly 变体、full 轨。规则子集 (True, False, False): 仅否定翻转。full 轨文本载体 content_full = 标题 prepend 加整篇正文, 覆盖最广、分母最完整。本列同样与既有 bian_2021_negonly_full 字节一致, 是消融梯度中语义最明确的单规则臂, 隔离否定翻转对 Bian 中文语调的单独贡献。相较 raw-full 之差纯归因于否定规则, 相较 canonical 主列 (full-rules) 之差则揭示"仅有否定、缺程度与转折"的后果。否定是中文金融新闻里最频繁触发极性反转的规则, 故 negonly-full 相对 raw-full 常在符号方向上产生可观修正, 是评估"否定翻转是否为语调主要驱动"的核心对照。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁把不同规则子集或不同轨混进同一 over-identified Hansen J。变体间高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解, 聚合遵循 2026-06-29 full-only 留篇门控。

negonly-full 与 raw-full 之差是否定规则在全文视角的最完整单独边际, 是量化"否定误计后果"的核心对照; 与 negdeg-full、negadv-full 联读可交叉印证否定贡献量级。因否定高频, 本列相对 raw 的符号修正在三轨中最显著, 是评估否定是否为语调主要驱动的关键点。全文轨分母最大使估计最稳, 且本列与既有手写列字节一致, golden-safe。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比。

## VAR: bian_2021_negonly_tone_ss

【变体差分】
本列为 negonly 变体、ss 轨。规则子集 (True, False, False): 仅否定翻转。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 语义最聚焦于"银行谈金科"语境。无同句共现时回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母, 防样本坍缩。在同句窗内否定词对短句极性符号的反转最关键, 故 ss-negonly 尽管只开一条规则, 却能在最聚焦语境下捕捉"银行金科同句语调"的符号方向, 是"最小极性方向规则 + 最聚焦语境"的组合。因不动幅度, 其与 ss-raw 的差异集中于符号翻转。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨与消融梯度正交不跨轨混检。聚合遵循 full-only 门控, ss 为条件于 full 留篇集子集测度, 变体高度共线故报告相关性而非可加分解。

ss-negonly 位于"最聚焦语境 + 单否定规则"格点, 与 ss-raw 之差在同句语境隔离否定翻转边际。因同句窗内否定词多紧邻极性词, 否定误计在此语境后果显著, 本列相对 ss-raw 的符号修正可能被放大, 是观察否定作用在聚焦语调影响的敏感探针。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_raw_tone_ctx

【变体差分】
本列为 raw 变体、ctx 轨。raw 对应旗标 (False, False, False): 三条语言学规则全部关闭, 是消融梯度的零规则基线 (L0)。它把 Bian 词典的情感测度约化为最朴素的带符号极性词计数自归一化, 不做否定翻转、不做程度缩放、不做转折让步, 因而是评估任何单条或多条规则边际贡献时的统一参照原点。所有其余六个消融臂与 canonical full-rules 主列都可视为在 raw 之上逐步叠加规则的结果, 故 raw 在解释上具有锚点地位。ctx 轨文本载体 content_ctx 为标题 prepend 加银行实体上下文窗, 使裸极性计数聚焦银行邻近表述, 抑制远端段落噪声。由于不处理否定, raw 会把"不良""未达标"等含否定的负面表述里的正面词误计为正, 因此 raw 与 negonly 系列之差正是否定误计的量级估计。本列与其余六消融臂、与 full / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三轨正交不跨轨混检。变体高度共线, 报告相关性, 聚合遵循 full-only 门控, ctx 为 full 留篇集子集测度。

作为 L0 原点, raw 不与任何规则叠加, 其与 negonly、degonly、advonly 三单规则臂之差分别估计否定、程度、转折的单独边际; 但三差之和一般不等于全规则主列与 raw 之差, 因规则间存在交互项 (审计 MATH-1 非可加分解), 故本谱刻意不把各臂并入同一可加式而只报告两两相关。聚合层面, 文章级经 Σ|final_i| 自归一化抵消篇幅后, bank-year 值取该行当年 full 留篇集内文章均值, ctx 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

## VAR: bian_2021_raw_tone_full

【变体差分】
本列为 raw 变体、full 轨。规则子集 (False, False, False): 零规则基线, 三条语言学规则全关。full 轨文本载体 content_full = 标题 prepend 加整篇正文, 覆盖最广、分母最完整, 是三轨中最直接对照 canonical full-rules 主列的口径。full 轨 raw 与无后缀主列之差, 完整刻画了否定 / 程度 / 转折三条规则叠加的总效应, 是量化"语言学规则整体贡献"的最干净上界对照。作为最朴素的裸极性计数, raw-full 不做任何符号或强度修正, 其与各单规则臂 (negonly / degonly / advonly) 之差分别估计对应单条规则的边际, 与各双规则臂之差则估计缺失那条规则的后果。需注意 raw 因不处理否定而系统性高估含否定负面语句的语调, 故不宜作主测度, 仅充当参照原点。本列与其余消融臂、与 ctx / ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则子集或不同轨混进同一 over-identified Hansen J。变体高度共线 (相关近 0.99), 报告相关性而非并入同一可加分解, 聚合遵循 full-only 留篇门控。

raw-full 在消融格中是所有臂的统一参照原点, 其与全规则主列之差刻画三条规则叠加的总效应上界, 与各单规则臂之差分别给出单条规则边际的下界视角。因不做否定处理, 本列系统性高估含否定负面语句的语调, 故仅作原点而非主测度。全文轨分母最大, 使各基于 raw 的差分估计方差最小, 是规格曲线中零规则端点的代表。聚合遵循 full-only 门控, 分子分母严格同轨, 自归一化保证跨篇可比, 缺列不借他轨分母。

## VAR: bian_2021_raw_tone_ss

【变体差分】
本列为 raw 变体、ss 轨。规则子集 (False, False, False): 零规则基线。ss 轨文本载体 content_ss 为标题 prepend 加银行与金科同句共现窗 (默认 ±1 句), 是三轨中语义最聚焦者。无同句共现时回退镜像 content_ctx 全文 body, 置 ss_is_fallback=True 并共享 ctx 的 n_articles 分母, 防样本坍缩。在最聚焦的同句语境下计算最朴素的裸极性计数, ss-raw 给出"银行金科同句、零规则修正"的语调基线, 与 ss 轨其余消融臂之差即在该聚焦语境下各规则的边际。因短窗内否定往往紧邻极性词, ss-raw 相对 ss-negonly 的偏差可能被放大, 使本列成为观察否定误计在聚焦语境后果的敏感探针。本列与其余六消融臂、与 full / ctx 轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三轨与消融梯度正交不跨轨混检。聚合遵循 full-only 门控, ss 为条件于 full 留篇集子集测度, 变体高度共线故报告相关性而非并入同一可加分解式。

ss-raw 在最聚焦语境给出零规则基线, 与 ss 轨各消融臂之差即各规则在同句语境的边际。因短窗内否定紧邻极性词, 本列相对 ss-negonly 的偏差可能被放大, 使其成为观察否定误计在聚焦语境后果的最敏感探针。聚合层面有共现与回退篇章共享 ctx 的 n_articles 分母, bank-year 取 full 留篇集内文章均值, 自归一化后跨篇可比; ss 缺列跳轨不借 full 轨分母, 保证分子分母严格同轨。

<!-- rendered-citations:begin -->
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), 20. https://doi.org/10.1007/s13278-025-01416-z
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
