---
family_id: F045
columns:
- avg_hard_char_ctx
- avg_hard_char_full
- avg_hard_char_ss
unit: 无量纲比率 (难字占比 ∈ [0,1] 的 bank-year 均值)
formula: "hard_char_ratio = 难字符数 / 汉字符总数 (逐篇, 难字 = 不在 jieba 0.42.1 冻结词典高频常用字集 _common_char_set 内的汉字); avg_hard_char{track} = mean_over_articles(hard_char_ratio{track}) 按 bank-year 聚合, 'mean' 自动跳过 NaN"
producer: news_process/pipeline/sentiment/lexical_complexity.py::compute_lexical_complexity ; news_process/pipeline/panel/encode.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (hard_char_ratio{track})
citations:
- doi: 10.18653/v1/2023.emnlp-main.863
  type: journal
  authors: Yang, X., Arora, A., Jheng, S.-Y., & Dell, M.
  year: 2023
  title: "Quantifying character similarity with vision transformers"
  venue: Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 13982-13996
- doi: 10.1093/rfs/hhy083
  type: journal
  authors: Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M.
  year: 2019
  title: "Information, trading, and volatility: Evidence from firm-specific news"
  venue: The Review of Financial Studies
  vol: 32
  issue: 3
  pages_or_artno: 992-1033
- doi: 10.2308/accr-52342
  type: journal
  authors: Chen, S., Schuchard, K., & Stomberg, B.
  year: 2019
  title: "Media coverage of corporate taxes"
  venue: The Accounting Review
  vol: 94
  issue: 5
  pages_or_artno: 83-116
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一家银行在给定年度所获媒体报道的"用字难度"平均水平, 核心构念是难字率 (hard character ratio): 一篇报道中不属于常用字集的汉字所占比例。其思想承袭可读性研究中 Dale 与 Chall 的 familiar-word 传统, 即以"读者是否熟识该书写单元"作为难度的基本判据; 由于中文没有音节切分, 无法直接套用英文 Fog 指数中的"多音节复杂词占比", 因而在中文语境下以"是否为常用汉字"替代"是否为多音节复杂词", 使难字率成为 Fog 式"%complex words"维度的中文等价物。这一中文落地口径与丘心颖等 (2016) 在《经济学(季刊)》中对中文年报可读性的处理一脉相承, 都把字符级难度作为文本可读性的一条独立维度, 与句长、词长、类符形符比等指标互补而不重叠。在本项目的披露质量/可读性测度族中, 难字率与低频词率 (rare word)、名词化率、功能词比率、硬信息密度、篇内冗余并列, 各自覆盖可读性的不同侧面: 低频词率度量"术语稀有度", 而难字率度量"书写单元本身的生僻度", 二者构念相邻但不等价, 回归中互为稳健性而非相互替代。

【方法学与计算】
计算在 pipeline/sentiment/lexical_complexity.py 的 compute_lexical_complexity 中完成: 对每篇报道文本先做一次 jieba 0.42.1 的词性标注 pass, 统计其中的汉字字符, 分母为该篇汉字符总数, 分子为其中落在常用字集之外的汉字个数, 相除即得逐篇 hard_char_ratio。常用字集 _common_char_set 并非官方字表, 而是由 jieba 0.42.1 冻结词典的词频派生的可复现代理集, 因此整条链路是零付费 (无 LLM、无新依赖、不触 M0 审批门、不改 Prompt v8) 的确定性测度; 源码注释明确指出官方《通用规范汉字表》一级字 3500 可作为未来的 drop-in 替换, 但当前生产口径以冻结词典派生集为准, 以保证 golden 可复现。逐篇比率随后在 pipeline/panel/encode.py 内按 bank-year 以 'mean' 聚合为面板列 avg_hard_char{track}, 'mean' 会自动跳过 NaN, 使过短或空文本不污染年度均值。整个测度是逐字符统计, 不含任何随机性, 亦不依赖嵌入或 BERT, 因此与换嵌入模型、换情感 LLM 等改动完全正交。

【文献定位】
难字率属于以字符为基本计量单元的中文文本测度, 与近年将汉字字形/视觉特征量化的工作在方法学脉络上相通: Yang 等 (2023) 用视觉 Transformer 量化汉字之间的相似度, 说明汉字层面的细粒度计量已成为中文文本分析的一条独立路径, 本家族则在最朴素的"常用/非常用"二分上做字符级难度统计, 属同一以字符为单元的计量取向的低成本端。将文本可读性/复杂度测度用于金融与媒体研究由来已久: Boudoukh 等 (2019) 表明公司特定新闻的文本信息含量能解释交易与波动, 支持把新闻文本的可测特征纳入实证; Chen 等 (2019) 对企业税务的媒体报道做文本层面的刻画, 印证媒体报道文本的用词特征本身即是有信息的研究对象。本家族把这条思路落到银行金科报道的用字难度上, 作为报道"可读性/专业性"的一个代理, 供下游作为控制变量或稳健性维度使用。

【三轨口径与稳健性】
本家族严格实现 full/ctx/ss 三轨: full = 标题 prepend 后的全文正文, ctx = 标题加实体上下文窗口, ss = 标题加银行与金科同句共现窗口。三轨文本在 stage 14 ctx_materializer 物化, compute_lexical_complexity 本身 track-agnostic, 由调用方 tone_words 对 content_full / content_ctx / content_ss 各调用一次驱动。三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。留篇门控为 full-only (2026-06-29): 一篇是否计入"银行金科报道"只看 full 轨的留篇判定, ctx/ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 列照算。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 与 full 共享 n_articles 分母, 属优雅降级而非静默丢列。

## VAR: avg_hard_char_full

【变体差分】
本列是家族在 full 轨上的实例, 也是三轨中的首要 (primary) 轨。full 轨文本 = 标题 prepend 到全文正文, 因此难字率覆盖整篇报道的全部汉字, 是信息量最完整、样本最全的一轨。按 full-only 门控 (2026-06-29), 一篇报道是否被判为"银行金科报道"仅取决于 full 轨的留篇判定, 因此 avg_hard_char_full 的行宇宙即为该 bank-year 的全部留篇集, 分母 n_articles 与该轨严格对齐; ctx 与 ss 两列则在此留篇集的子集上条件计算。数值上, 由于 full 轨文本最长 (源码披露 full 轨中位约 1553 字), 其难字率对篇幅长尾更稳健, 年度均值的抽样噪声也最小, 故 full 列适合作为主分析中报道用字难度的代理控制变量。本列与同家族 ctx/ss 两列各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 三者刻画的是同一构念在三种文本切分下的读数, 不构成相互替代的工具或分解项。与相邻的 avg_rare_word_full (低频词率) 相比, 本列度量书写单元本身的生僻度而非术语稀有度, 二者构念相邻但不等价, 回归中并列为互补的可读性维度而非同式共线代理。需强调常用字集 _common_char_set 由 jieba 0.42.1 冻结词典词频派生而非官方字表, 属可复现的零付费代理, 因此 full 列的绝对水平只在同一冻结口径内可比, 跨口径 (如未来替换为《通用规范汉字表》一级字) 的水平不可直接比较, 只可比标准化后的效应方向; 这一点在披露文本可读性结果时须如实说明。full 轨作为主轨还意味着它是三轨中 fallback 最少、样本框最稳定的一列, 适合承担描述统计与主回归中的可读性控制角色。

## VAR: avg_hard_char_ctx

【变体差分】
本列是家族在 ctx 轨上的实例。ctx 轨文本 = 标题 prepend 加上实体上下文窗口, 只保留目标银行等实体附近的局部行文, 因此难字率只统计上下文窗口内汉字的生僻度, 剔除了与银行金科主题无关的段落对用字难度的稀释或抬升。相对 full 轨, ctx 轨文本更短 (源码披露 ctx 轨中位约 725 字), 聚焦度更高, 但年度均值的抽样噪声也更大, 因此定位为 full 的稳健性轨而非主轨。按 full-only 门控, 本列是 conditional-on-full 测度: 其行宇宙是 full 留篇集的子集, 仅在 full 轨判定为留篇的报道上再取 ctx 轨文本计算, per-track 列照算。本列与 avg_hard_char_full、avg_hard_char_ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; ctx 与 full 的读数差异首先可能源自文本切分口径 (窗口 vs 全文) 而非构念差异, 解读时应把二者视为同一难字率构念在不同粒度上的并列证据, 而非可加分解。由于窗口截取可能落在实体密集句上, 而这类句子常含机构简称、专有名词与数字缩写, ctx 轨的难字率既可能因剔除铺陈段而下降, 也可能因专有名词集中而上升, 方向取决于语料, 因此 ctx 列的价值在于检验主轨结论是否对"聚焦到实体上下文"这一文本切分选择稳健, 而非提供一个可加或可分解的独立信号。与 avg_rare_word_ctx 一样, 本列在 ctx 轨上度量的仍是字符级书写难度而非术语稀有度, 二者构念相邻不等价, 并列为互补维度; 计算口径与常用字集同 full 轨完全一致, 唯一差别是输入文本由 content_full 换为 content_ctx, 保证三轨差异纯粹来自文本切分而非度量定义。

## VAR: avg_hard_char_ss

【变体差分】
本列是家族在 ss 轨上的实例。ss 轨文本 = 标题 prepend 加上银行与金科同句共现窗口, 是三轨中聚焦度最高的一轨: 只有当某句中银行与金科词同句共现时, 该句 (及其邻近窗口) 才进入 ss 文本, 因此难字率度量的是最贴近"银行金科交汇"语境的用字难度。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 与 full 共享 n_articles 分母, 属优雅降级; 当上游金科自动机为空 (FINTECH_AC=None) 时 ss_is_fallback 全 True。因此 ss 列在共现稀疏的样本上会有相当比例的回退篇, 解读时须结合 fallback 占比。按 full-only 门控, 本列同为 conditional-on-full 测度, 行宇宙是 full 留篇集的子集。本列与 avg_hard_char_full、avg_hard_char_ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 三轨读数是同一难字率构念在全文、实体窗、同句共现窗三种切分下的并列证据, 不作相互替代或合并入同一过度识别检验。ss 轨在样本上的一个实务后果是: 若某 bank-year 内多数报道并无银行与金科同句共现, 则本列大量取回退全文口径, 数值会向 full 轨收敛, 此时 ss 与 full 的读数趋同并不表明两轨等价, 而是共现稀疏导致的回退所致, 稳健性解读须结合该 bank-year 的 ss_is_fallback 占比一并汇报。计算口径 (常用字集、分子分母定义、bank-year 'mean' 聚合、自动跳过 NaN) 与 full/ctx 两轨逐字节一致, 唯一差别是输入文本由 content_ss 提供, 保证三轨差异只来自文本切分而非度量定义, 这也是三轨可被并排为互为稳健性证据的前提。

<!-- rendered-citations:begin -->
Yang, X., Arora, A., Jheng, S.-Y., & Dell, M. (2023). Quantifying character similarity with vision transformers. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 13982-13996. https://doi.org/10.18653/v1/2023.emnlp-main.863
Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. The Review of Financial Studies, 32(3), 992-1033. https://doi.org/10.1093/rfs/hhy083
Chen, S., Schuchard, K., & Stomberg, B. (2019). Media coverage of corporate taxes. The Accounting Review, 94(5), 83-116. https://doi.org/10.2308/accr-52342
<!-- rendered-citations:end -->
