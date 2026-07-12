---
family_id: F187
columns:
- dict_avg_advonly_tone_ctx
- dict_avg_advonly_tone_full
- dict_avg_advonly_tone_ss
- dict_avg_degadv_tone_ctx
- dict_avg_degadv_tone_full
- dict_avg_degadv_tone_ss
- dict_avg_degonly_tone_ctx
- dict_avg_degonly_tone_full
- dict_avg_degonly_tone_ss
- dict_avg_negadv_tone_ctx
- dict_avg_negadv_tone_full
- dict_avg_negadv_tone_ss
- dict_avg_negdeg_tone_ctx
- dict_avg_negdeg_tone_full
- dict_avg_negdeg_tone_ss
- dict_avg_negonly_tone_ctx
- dict_avg_negonly_tone_full
- dict_avg_negonly_tone_ss
- dict_avg_raw_tone_ctx
- dict_avg_raw_tone_full
- dict_avg_raw_tone_ss
unit: 语调得分 (连续无量纲, 约 [-1,1]; 文章级自归一化后聚合为 bank-year 均值)
formula: "dict_avg_{sfx}_tone{track} = mean_over_dicts( {d}_{sfx}_tone{track} ); 其中 {d}_{sfx}_tone = 状态机在语言学规则子集 sfx 下的 Σfinal / Σ|final| 自归一化词典语调, d 遍历 6 部词典 (DICT_NAMES)"
producer: news_process/pipeline/panel/geography.py (跨词典均值聚合) ; news_process/pipeline/sentiment/tone_words.py (per-dict 消融变体) ; news_process/pipeline/panel/codebook.py (元数据发射)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet ({d}_{sfx}_tone{track} 逐词典消融列)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  issue: ""
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是词典法银行金科语调在语言学规则消融梯度上的跨词典均值, 即把银行相关新闻文本经六部金融情感词典打分, 再对得分施加不同子集的语言学修正规则后, 跨六部词典取算术平均, 最终聚合为 bank-year 面板列。构念内核仍是媒体语调 (media tone) 这一经典文本测度: 正面词与负面词的相对配比映射市场对某银行金融科技活动的情绪倾向。词典法之所以在会计与金融文本分析中长期占据方法学基座, 在于它透明、可复现、无需训练标注, 且系数不随语料漂移, Loughran 与 McDonald (2016) 的综述把这一取向确立为财务文本情感度量的规范起点。本家族的特殊性在于, 它不只报告单一"全规则"语调, 而是把三条中文语言学修正规则展开为完整幂集, 逐一物化为可并排检验的消融臂, 从而把"语言学规则是否驱动主结论"这一稳健性问题变成可直接读取的面板证据。

【方法学与计算】
底层三条语言学修正规则为: 否定翻转 (neg, 当情感词前一定窗口内出现否定词时翻转其极性)、程度副词调节 (deg, 程度副词按其强度缩放邻接情感词的贡献)、转折重加权 (adv, 转折连词后的分句权重上调、之前分句权重下调)。七个消融后缀对应这三条规则的非全集子集: raw 关闭全部三规则 (退化为纯词袋计数), negonly / degonly / advonly 各只开一条, negdeg / negadv / degadv 各开两条; 三规则全开的"全规则"变体即家族之外的 canonical 无后缀 dict_avg_tone, 不属本家族。逐词典打分在状态机内完成, 对每篇文章按 Σfinal / Σ|final| 做自归一化, 使单篇语调落在约 [-1,1] 且与文章长度无关; 随后 geography.py 对六部词典的同名消融变体取跨词典算术平均得到 dict_avg_{sfx}_tone{track}, 缺列由 _safe_mean 优雅返回 NaN 而不崩。三条文本轨 full / ctx / ss 各自独立走完整条链: full 为标题 prepend 加全文正文, ctx 为标题加实体上下文窗口, ss 为标题加银行与金科同句共现窗口, 且 ss 在无共现时镜像 ctx 的回退公理退化为全文正文并置 ss_is_fallback 为真。留篇门控采用 full-only 口径, 一篇是否计入银行金科报道只看 full 轨判定, ctx 与 ss 为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集。跨词典均值族属六部词典体系, 其数值随词典集合由五部扩为六部而回溯微变, 属有意的测度改善而非缺陷。

【文献定位】
消融梯度的方法论正当性直接锚于两支文献。其一是词典法内部的语言学规则争议: Taboada 等 (2011) 系统论证了否定、程度强化与转折等价性转移 (valence shifters) 对基于词典的情感判定至关重要, 忽略它们会系统性错判分句极性; Pröllochs、Feuerriegel 与 Neumann (2016) 进一步在新闻驱动交易情境下量化了否定范围检测对情感信号质量的边际贡献。本家族把这些规则逐条开关物化, 正是对上述争议提供可审计的稳健性回应。其二是跨方法与跨规格的稳健性规范: Frankel、Jennings 与 Lee (2022) 把词典法与机器学习法并置为互为稳健性的测量臂, 为本项目"多规格并排、不分主次"的做法提供先例。García、Hu 与 Rohrer (2023) 强调金融词语情感权重的语料依赖性, 提示任何单一规则配置都不应被当作唯一真值。Du 等 (2022) 与 Tetlock (2007) 则分别奠定中文金融情感词典与媒体语调影响资产定价的实证基础。铁律层面, 七个消融臂各自 just-identified 并排、互为稳健性不分主次, 严禁把不同消融臂混进同一 over-identified 的 Hansen J 检验; 三条文本轨亦同此律, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_advonly_tone_ctx

【变体差分】
本列为 advonly 消融臂在 ctx 轨的跨词典均值。该列在文章级先由状态机逐篇计 Σfinal / Σ|final| 自归一化得单篇语调, 再在六部词典间取算术平均, 最后按 bank-year 聚合为面板均值; 因只保留转折规则, 本列与同轨 raw 之差可读出转折规则单独相对纯词袋的增量, 与全规则 canonical 之差则暴露否定与程度合并的缺失。六部词典体系由五扩六后本列数值回溯微变, 属有意测度改善而非缺陷。advonly 只开启转折重加权 (adv) 一条规则, 关闭否定翻转与程度副词调节: 状态机识别转折连词 (如"但""然而""不过"), 对转折之后的分句上调权重、之前分句下调权重, 但不对否定词做极性翻转、亦不按程度副词强度缩放贡献。ctx 轨的文本载体是 content_ctx, 即标题 prepend 后加实体上下文窗口, 只保留银行实体邻近的语句而非全文正文, 因此本列度量的是银行实体上下文范围内、仅经转折规则修正的六词典平均语调。相对家族 canonical (三规则全开的 dict_avg_tone), 本列刻意剥离否定与程度两条规则, 用以隔离转折规则单独的边际贡献。ctx 轨在项目内为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集, 留篇判定仍由 full 轨门控。本列与家族其余消融臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_advonly_tone_full

【变体差分】
本列为 advonly 消融臂在 full 轨的跨词典均值, 是本消融臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; 因 full 轨覆盖标题与全文正文, 转折连词在长文中出现更充分, 本列相对同臂 ctx/ss 轨对转折规则的敏感度通常更高, 是评估转折规则单独效应的最信息密集轨。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。advonly 仅启用转折重加权规则, 否定翻转与程度副词调节均关闭, 故其与全规则 canonical 的差异精确等于"否定加程度两规则合并的边际效应缺失"。full 轨文本载体为 content_full, 即标题 prepend 后拼接全文正文, 覆盖面最广, 也是项目留篇门控 (2026-06-29 full-only 口径) 的唯一判定轨: 一篇是否计为银行金科报道只看 full 轨 llm_verified_full, 因此 full 轨的行宇宙即银行金科留篇全集, 而 ctx 与 ss 轨为其子集。本列在跨词典层对六部词典的 advonly 变体取算术平均, 缺列以 NaN 优雅降级。作为消融梯度的一臂, 本列与 raw、negonly、degonly、negadv、negdeg、degadv 六臂以及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨亦同此律。

## VAR: dict_avg_advonly_tone_ss

【变体差分】
本列为 advonly 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段极短且转折连词稀疏, 本列在共现片段内的转折修正力度往往弱于 full/ctx, 但正因语义聚焦, 它度量的是银行金科同句语境下转折规则的净贡献。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。advonly 只保留转折重加权规则, 关闭否定与程度两条规则。ss 轨文本载体为 content_ss, 即标题 prepend 后加银行与金科同句共现窗口 (±N 句, 默认半径 1), 是三轨中语义最聚焦的一轨, 只截取银行实体与金融科技词在同一句子邻域共现的片段。其回退语义严格镜像 ctx: 当文章内不存在银行与金科同句共现时, content_ss 退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 若金科 AC 自动机为空则 ss_is_fallback 全域为真, 优雅降级。因此本列度量的是银行金科共现语境内、仅经转折规则修正的六词典平均语调。ss 轨为 conditional-on-full 稳健性轨, 留篇判定仍归 full 轨。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_degadv_tone_ctx

【变体差分】
本列为 degadv 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 因同时保留程度与转折两规则、独缺否定, 本列可与同轨 negonly、negadv 等臂交叉对照, 从多侧夹逼否定翻转规则在银行实体上下文内的边际重要性。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degadv 同时开启程度副词调节 (deg) 与转折重加权 (adv) 两条规则, 唯独关闭否定翻转 (neg): 状态机既按程度副词强度缩放邻接情感词贡献, 又对转折分句做非对称重加权, 但不因否定词翻转极性。相对全规则 canonical, 本列差异精确等于"否定翻转规则单独缺失"的效应, 因而可与 negonly 等臂对照, 从两侧夹逼出否定规则的边际重要性。ctx 轨载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量范围限于银行实体邻近语句。本列在跨词典层对六部词典的 degadv 变体取算术平均, 缺列以 NaN 优雅降级。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六个消融臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_degadv_tone_full

【变体差分】
本列为 degadv 消融臂在 full 轨的跨词典均值, 是该消融臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使否定词与其被翻转对象的搭配样本最充分, 故本列与全规则 canonical 之差是估计否定翻转规则单独贡献的首选口径, 亦为该臂三轨中信息量最大者。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degadv 启用程度副词调节与转折重加权两规则、关闭否定翻转, 故与全规则 canonical 的差异恰为否定规则单独的边际贡献, 是评估否定翻转是否驱动主结论的关键对照臂。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是项目 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 degadv 变体取跨词典算术平均, 逐词典打分经 Σfinal / Σ|final| 自归一化后再平均, 缺列以 NaN 优雅降级不崩。作为消融梯度七臂之一, 本列与 raw、三个单规则臂、其余两个双规则臂以及全规则 canonical 并置为完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨同律。

## VAR: dict_avg_degadv_tone_ss

【变体差分】
本列为 degadv 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段聚焦银行金科同句共现, 否定词与情感词的搭配窗口被截短, 本列相对 full 轨对否定规则的隔离更保守, 却提供了共现语境下的独立稳健性读数。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degadv 开启程度副词调节与转折重加权、关闭否定翻转, 因此与全规则 canonical 之差精确刻画否定规则的单独效应。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 语义最聚焦, 只覆盖银行实体与金融科技词同句共现片段。其回退公理镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退优雅降级。故本列度量的是银行金科共现语境内、仅缺否定翻转规则的六词典平均语调。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_degonly_tone_ctx

【变体差分】
本列为 degonly 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 因只保留程度副词一条规则, 本列与同轨 raw 之差直接量化程度强化在银行实体上下文内相对纯词袋的净增益, 与 negdeg 对照则可分离否定成分。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degonly 只开启程度副词调节 (deg) 一条规则, 关闭否定翻转与转折重加权: 状态机仅按程度副词强度缩放邻接情感词的贡献, 例如"显著改善"较"改善"贡献更大, 但不翻转否定极性、不对转折分句重加权。相对全规则 canonical, 本列刻意剥离否定与转折两规则, 用以隔离程度副词规则单独的边际贡献。ctx 轨文本载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量限于银行实体邻近语句。本列在跨词典层对六部词典的 degonly 变体取算术平均, 缺列以 NaN 优雅降级。ctx 为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_degonly_tone_full

【变体差分】
本列为 degonly 消融臂在 full 轨的跨词典均值, 是该臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使程度副词与其修饰情感词的搭配样本最充分, 本列因而是估计程度副词规则单独增量的首选口径, 亦为该臂三轨中信息量最大者, 在生产语料上其对程度强化的敏感度显著高于同臂 ss 轨。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degonly 仅启用程度副词调节, 关闭否定翻转与转折重加权, 故其与三规则全开 canonical 的差异等于"否定加转折两规则合并缺失"的效应; 与 raw 相比则可读出程度副词规则单独相对纯词袋的增量。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 degonly 变体取跨词典算术平均, 逐词典自归一化后平均, 缺列以 NaN 优雅降级。作为消融梯度七臂之一, 本列与其余六臂及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨亦同此律。

## VAR: dict_avg_degonly_tone_ss

【变体差分】
本列为 degonly 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段短、程度副词稀疏, 本列的程度修正力度弱于 full/ctx, 但作为银行金科同句语境下的独立读数, 它与另两轨互为稳健性校验。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。degonly 只保留程度副词调节规则, 关闭否定与转折两规则, 故其相对全规则 canonical 的差异刻画的是否定与转折合并的缺失效应。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 是三轨中语义最聚焦者, 只覆盖银行实体与金融科技词同句共现片段。回退语义严格镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退。因此本列度量的是银行金科共现语境内、仅经程度副词规则修正的六词典平均语调。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negadv_tone_ctx

【变体差分】
本列为 negadv 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 因保留否定与转折两规则、独缺程度, 本列可与同轨 degonly、degadv 交叉对照, 从多侧夹逼程度副词规则在银行实体上下文内的边际重要性。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negadv 同时开启否定翻转 (neg) 与转折重加权 (adv) 两规则、唯独关闭程度副词调节 (deg): 状态机既在否定词窗口内翻转情感词极性, 又对转折分句非对称重加权, 但不按程度副词强度缩放贡献。相对全规则 canonical, 本列差异精确等于"程度副词规则单独缺失"的效应, 可与 degonly 等臂对照夹逼出程度规则的边际重要性。ctx 轨文本载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量限于银行实体邻近语句。本列在跨词典层对六部词典的 negadv 变体取算术平均, 缺列以 NaN 优雅降级。ctx 为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negadv_tone_full

【变体差分】
本列为 negadv 消融臂在 full 轨的跨词典均值, 是该臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使程度副词的样本最充分, 本列与全规则 canonical 之差因而是估计程度副词规则单独贡献的首选口径, 亦为该臂三轨中信息量最大者。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negadv 启用否定翻转与转折重加权两规则、关闭程度副词调节, 故与三规则全开 canonical 的差异恰为程度副词规则单独的边际贡献, 是检验程度规则是否驱动主结论的关键对照臂。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 negadv 变体取跨词典算术平均, 逐词典经 Σfinal / Σ|final| 自归一化后再平均, 缺列以 NaN 优雅降级不崩。作为消融梯度七臂之一, 本列与 raw、三个单规则臂、其余两个双规则臂及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨同律。

## VAR: dict_avg_negadv_tone_ss

【变体差分】
本列为 negadv 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段聚焦银行金科同句共现且程度副词稀疏, 本列相对 full 轨对程度规则的隔离更保守, 却提供共现语境下的独立稳健性读数。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negadv 开启否定翻转与转折重加权、关闭程度副词调节, 故与全规则 canonical 之差精确刻画程度副词规则的单独效应。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 语义最聚焦, 只覆盖银行实体与金融科技词同句共现片段。回退公理镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退优雅降级。因此本列度量的是银行金科共现语境内、仅缺程度副词规则的六词典平均语调, 其在开发期短面板上因程度副词稀疏而方差偏小属预期退化。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negdeg_tone_ctx

【变体差分】
本列为 negdeg 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 因保留否定与程度两规则、独缺转折, 本列可与同轨 advonly、degadv 交叉对照, 从多侧夹逼转折重加权规则在银行实体上下文内的边际重要性。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negdeg 同时开启否定翻转 (neg) 与程度副词调节 (deg) 两规则、唯独关闭转折重加权 (adv): 状态机既翻转否定词后情感词极性, 又按程度副词强度缩放贡献, 但对转折分句不做非对称重加权。相对全规则 canonical, 本列差异精确等于"转折规则单独缺失"的效应, 可与 advonly 等臂对照夹逼出转折规则的边际重要性。ctx 轨文本载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量限于银行实体邻近语句。本列在跨词典层对六部词典的 negdeg 变体取算术平均, 缺列以 NaN 优雅降级。ctx 为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negdeg_tone_full

【变体差分】
本列为 negdeg 消融臂在 full 轨的跨词典均值, 是该臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使转折连词的样本最充分, 本列与全规则 canonical 之差因而是估计转折规则单独贡献的首选口径, 亦为该臂三轨中信息量最大者, 在生产语料上对转折连词的覆盖显著优于同臂 ss 轨。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negdeg 启用否定翻转与程度副词调节两规则、关闭转折重加权, 故与三规则全开 canonical 的差异恰为转折规则单独的边际贡献, 是检验转折规则是否驱动主结论的关键对照臂。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 negdeg 变体取跨词典算术平均, 逐词典自归一化后再平均, 缺列以 NaN 优雅降级不崩。作为消融梯度七臂之一, 本列与 raw、三个单规则臂、其余两个双规则臂及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨同律。

## VAR: dict_avg_negdeg_tone_ss

【变体差分】
本列为 negdeg 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段短、转折连词稀疏, 本列的转折修正力度弱于 full/ctx, 但作为银行金科同句语境下的独立读数, 它与另两轨互为稳健性校验。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negdeg 开启否定翻转与程度副词调节、关闭转折重加权, 故与全规则 canonical 之差精确刻画转折规则的单独效应。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 语义最聚焦, 只覆盖银行实体与金融科技词同句共现片段。回退公理镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退优雅降级。因此本列度量的是银行金科共现语境内、仅缺转折规则的六词典平均语调, 其在开发期短面板上因转折连词稀疏而方差偏小属预期退化, 生产长面板可正常识别。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negonly_tone_ctx

【变体差分】
本列为 negonly 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 作为三点谱的中间锚, 本列在银行实体上下文内隔离否定翻转一条规则, 与 raw、全规则 canonical 三点并读即构成最简的规则增益诊断链。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negonly 只开启否定翻转 (neg) 一条规则, 关闭程度副词调节与转折重加权: 状态机仅在否定词窗口内翻转邻接情感词极性 (如"未见改善"翻为负向), 但不按程度强度缩放、不对转折分句重加权。negonly 在项目内具特殊地位, 它与全规则 dict_avg_tone (三点谱高端) 及零规则的纯计数 avg_msent (三点谱低端) 共同构成最早落地的跨词典三点消融谱, 后经全幂集扩展为本家族。ctx 轨文本载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量限于银行实体邻近语句。本列对六部词典的 negonly 变体取跨词典算术平均, 缺列以 NaN 优雅降级。ctx 为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_negonly_tone_full

【变体差分】
本列为 negonly 消融臂在 full 轨的跨词典均值, 是该臂的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使否定词与被翻转对象的搭配样本最充分, 本列因而是最早落地三点消融谱的高信息端, 亦为评估否定翻转规则单独增量的首选口径。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negonly 仅启用否定翻转规则, 关闭程度副词与转折两规则, 故与三规则全开 canonical 之差等于"程度加转折两规则合并缺失"的效应; 与 raw 相比则可读出否定翻转规则单独相对纯词袋的增量, 呼应 Pröllochs 等 (2016) 对否定范围处理边际价值的量化。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 negonly 变体取跨词典算术平均, 逐词典自归一化后再平均, 缺列以 NaN 优雅降级。作为消融梯度七臂之一, 本列与其余六臂及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨同律。

## VAR: dict_avg_negonly_tone_ss

【变体差分】
本列为 negonly 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段聚焦银行金科同句共现, 否定词与情感词的搭配窗口被截短, 本列相对 full 轨对否定规则的隔离更保守, 却提供共现语境下的独立稳健性读数。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。negonly 只保留否定翻转规则, 关闭程度副词与转折两规则, 故其相对全规则 canonical 的差异刻画程度与转折合并的缺失效应。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 是三轨中语义最聚焦者, 只覆盖银行实体与金融科技词同句共现片段。回退语义严格镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退优雅降级。因此本列度量的是银行金科共现语境内、仅经否定翻转规则修正的六词典平均语调。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_raw_tone_ctx

【变体差分】
本列为 raw 消融臂在 ctx 轨的跨词典均值。该列在文章级逐篇计 Σfinal / Σ|final| 自归一化后于六部词典间取均值再按 bank-year 聚合; 作为零规则基线, 本列在银行实体上下文内提供纯词袋参照, 任何单规则或双规则同轨臂减去本列即得对应规则组合的净增量, 是整条消融梯度的对照原点。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。raw 关闭全部三条语言学修正规则 (否定翻转、程度副词调节、转折重加权), 退化为最朴素的词袋式词典计数: 只统计正面词与负面词的原始出现, 不做任何极性翻转、强度缩放或分句重加权。raw 是消融梯度的最低端参照臂, 与全规则 canonical (三点谱高端) 相比, 二者之差即三条规则合并施加的总修正量; 与各单规则臂相比则可逐条读出规则的边际增量。ctx 轨文本载体为 content_ctx, 标题 prepend 加实体上下文窗口, 度量限于银行实体邻近语句。本列对六部词典的 raw 变体取跨词典算术平均, 逐词典 Σfinal / Σ|final| 自归一化后再平均, 缺列以 NaN 优雅降级。ctx 为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 留篇门控归 full 轨。本列与家族其余六臂、与另两条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把任意两臂或两轨混进同一 over-identified 的 Hansen J 检验。

## VAR: dict_avg_raw_tone_full

【变体差分】
本列为 raw 消融臂在 full 轨的跨词典均值, 是消融梯度最低端 (零规则) 的门控主轨。该列在文章级逐篇自归一化后于六部词典间取均值再按 bank-year 聚合; full 轨全文覆盖使词频统计最充分, 本列因而是全库规模上评估任何语言学规则相对朴素计数是否带来增益的首选基线, 亦为整条梯度诊断的参照原点。raw 关闭全部三条语言学修正规则, 退化为纯词袋词典计数, 因此它是评估"任何语言学规则相对朴素计数是否带来增益"的基线参照: 全规则 canonical 减去本列即三规则合并总修正量, 各单规则臂减去本列即各规则单独增量。full 轨文本载体为 content_full, 标题 prepend 加全文正文, 是 full-only 留篇门控的唯一判定轨, 行宇宙为银行金科留篇全集。本列对六部词典的 raw 变体取跨词典算术平均, 逐词典自归一化后再平均, 缺列以 NaN 优雅降级不崩; 作为跨词典均值族, 其数值随词典集合五扩六而回溯微变, 属有意测度改善。作为消融梯度七臂之一, 本列与其余六臂及全规则 canonical 构成完整幂集谱, 各臂各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两臂混进同一 over-identified 的 Hansen J 检验, 三文本轨同律。

## VAR: dict_avg_raw_tone_ss

【变体差分】
本列为 raw 消融臂在 ss 轨的跨词典均值。该列在文章级逐篇自归一化后于六部词典间取均值再聚合为 bank-year; 因 ss 片段聚焦银行金科同句共现, 本列提供该聚焦语境下的纯词袋基线, 同轨任一带规则臂减去本列即得共现语境内对应规则组合的净增量。六部词典体系由五扩六后本列回溯微变, 属有意测度改善而非缺陷。raw 关闭全部三条语言学修正规则, 退化为纯词袋词典计数, 是消融梯度最低端参照臂。ss 轨文本载体为 content_ss, 标题 prepend 加银行与金科同句共现窗口 (默认半径 1 句), 是三轨中语义最聚焦者, 只覆盖银行实体与金融科技词同句共现片段。回退语义严格镜像 ctx: 无同句共现时退化为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 金科 AC 为空时全域回退优雅降级。因此本列度量的是银行金科共现语境内、未经任何语言学规则修正的六词典平均原始计数语调, 可作为该语境下评估规则增益的基线。ss 为 conditional-on-full 稳健性轨, 留篇门控归 full 轨, 行宇宙为 full 留篇集子集。本列与家族其余消融臂、与 full/ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
