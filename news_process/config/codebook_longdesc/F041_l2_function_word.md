---
family_id: F041
columns:
- avg_function_word_ctx
- avg_function_word_full
- avg_function_word_ss
unit: 无量纲比率 (功能词 token 占实词 token 的比例, 值域 [0,1]), bank-year 均值
formula: "function_word_ratio = n_function / n_real; n_function = 词性前缀 ∈ {u,p,c,r,y,e} 的 token 数, n_real = 非标点 token 数; avg_function_word{track} = 该 bank-year 内各文章 function_word_ratio{track} 的算术均值 (mean 自动跳过 NaN)"
producer: news_process/pipeline/sentiment/lexical_complexity.py::compute_lexical_complexity ; news_process/pipeline/panel/encode.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (function_word_ratio{track})
citations:
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1177/0261927X09351676
  type: journal
  authors: Tausczik, Y. R., & Pennebaker, J. W.
  year: 2010
  title: "The psychological meaning of words: LIWC and computerized text analysis methods"
  venue: Journal of Language and Social Psychology
  vol: 29
  issue: 1
  pages_or_artno: 24-54
- doi: 10.1111/j.1540-6261.2008.01362.x
  type: journal
  authors: Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S.
  year: 2008
  title: "More than words: Quantifying language to measure firms' fundamentals"
  venue: The Journal of Finance
  vol: 63
  issue: 3
  pages_or_artno: 1437-1467
- doi: 10.3115/1119250.1119269
  type: journal
  authors: Sproat, R., & Emerson, T.
  year: 2003
  title: "The first international Chinese word segmentation bakeoff"
  venue: Proceedings of the Second SIGHAN Workshop on Chinese Language Processing
  pages_or_artno: 133-143
- doi: "10.1111/1911-3846.12825"
  type: "journal"
  authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W."
  year: 2023
  title: "Textual Analysis in Accounting: What's Next?"
  venue: "Contemporary Accounting Research"
- doi: "10.1080/10888438.2024.2422365"
  type: "journal"
  authors: "Crossley, S. A."
  year: 2024
  title: "Developing Linguistic Constructs of Text Readability Using Natural Language Processing"
  venue: "Scientific Studies of Reading"
- doi: "10.1017/nlp.2024.50"
  type: "journal"
  authors: "Pan, W., Li, X., Chen, X., & Xu, R."
  year: 2024
  title: "Textual form features for text readability assessment"
  venue: "Natural Language Processing"
new_dois:
  - "10.1111/1911-3846.12825"
  - "10.1080/10888438.2024.2422365"
  - "10.1017/nlp.2024.50"
---

## CORE

【构念与来源】
本家族刻画一篇银行金融科技报道的功能词比率 (function word ratio), 并聚合为 bank-year 面板测度 avg_function_word。功能词 (又称虚词) 指承担语法结构而非实质语义的词类: 在中文语境下, 本项目以 jieba 词性标注的六类前缀近似之——助词 (u)、介词 (p)、连词 (c)、代词 (r)、语气词 (y)、叹词 (e)。分子 n_function 为落入这六类前缀的 token 数, 分母 n_real 为剔除标点后的全部 token 数, 二者相除即得单篇功能词比率, 值域为零到一之间的无量纲比例。构念动机来自 LIWC 分析性维度 (Analytic dimension): Tausczik 与 Pennebaker (2010) 系统阐述了功能词在心理语言学中的核心地位, 指出功能词密度高的文本往往结构松散、叙事性强、分析性 (逻辑化、层次化、形式化) 偏低, 而功能词密度低、实词密度高的文本更接近正式的、信息密集的书面披露。因此本家族把功能词比率作为报道文本"低分析性/高叙事性"的一个反向代理: 比率越高, 报道越偏口语化、铺陈化, 越少凝练的硬信息。

【方法学与计算】
计算入口是 lexical_complexity 模块的 compute_lexical_complexity, 对每篇文本做一次 jieba.posseg 词性标注 pass, 在同一次遍历中并行派生功能词比率与该模块的其余互补复杂度测度 (低频词率、难字率、名词化率、硬信息密度、篇内冗余等), 全部 $0 成本 (jieba 0.42.1 冻结词典, 无付费 LLM、不触 M0 门、不动 Prompt v8)。功能词判定原语是词性前缀集合 {u,p,c,r,y,e}, 刻意不含副词 (d): 副词语义偏内容侧, 保守排除以免污染"纯虚词"口径。分母 n_real 取非标点 token 数, 与本模块其余比率测度口径严格一致, 保证同一分母下各比率可横向比较; 当 n_real 为零 (空文本或纯标点) 时返回 NaN, 由下游 mean 聚合自动跳过, 短文本或空文本不污染均值。该函数本身 track-agnostic (输入单一文本, 返回 per-text 字典), 三轨 (full/ctx/ss) 的差异完全由调用方 tone_words 用各轨文本 content_full / content_ctx / content_ss 分别驱动一次实现。面板聚合在 encode 层: agg[avg_function_word{track}] = (function_word_ratio{track}, mean), 即某 bank-year 内所有留篇报道的功能词比率算术均值。

【文献定位】
功能词比率属于文本可读性/披露质量的一支, 与金融文本计量的主流传统相接。Tetlock、Saar-Tsechansky 与 Macskassy (2008) 开创了以词频统计量化媒体语言并连结公司基本面的范式; Jegadeesh 与 Wu (2013) 进一步提出以词权重刻画内容基调, 表明词层面的分布特征本身携带定价相关信息。García、Hu 与 Rohrer (2023) 则揭示金融词汇的情感与语义色彩随语境系统变化, 提示以词类分布度量文本风格须审慎处理语境依赖。Siano (2025) 展示了以 LLM 捕捉词语上下文相较于纯词袋计数的增量, 从反面界定了本家族这类词性计数测度的适用边界: 功能词比率是一个粗粒度、可复现、零成本的结构风格代理, 不宣称等同于语境感知的深度语义度量, 而是作为可读性控制变量与稳健性维度并入分析。中文分词的底层依赖 (jieba 词典与 HMM) 其精度与边界处理可追溯至 Sproat 与 Emerson (2003) 记录的中文分词评测传统, 本项目据此如实披露 jieba 词性标注属"粗近似", 功能词六类前缀映射为工程近似而非语言学权威切分。Bochkay、Brown、Leone 与 Tucker (2023, Contemporary Accounting Research) 的综述系统梳理了会计文本分析领域词频类测度 (含功能词/虚词计数) 的方法学现状与未来方向, 为本家族以词性前缀计数刻画报道文本风格的做法提供了最新的方法论定位。Crossley (2024, Scientific Studies of Reading) 用自然语言处理方法系统构建可读性相关的语言学构念, 含功能词/虚词密度等词类分布特征, 为本家族以词性前缀计数刻画文本可读性风格提供最新方法论参照。Pan、Li、Chen 与 Xu (2024, Natural Language Processing) 提出文本表层形式特征, 含功能词等词类比率, 用于可读性评估, 支持本家族功能词比率作为文本结构风格粗粒度代理的定位。

【口径与稳健性】
三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨同名列混入同一 over-identified 的 Hansen J 过度识别检验。留篇门控为 full-only (2026-06-29): 一篇报道是否计入 bank-year 分母, 只由 full 轨的 llm_verified_full 判定; ctx 与 ss 轨降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 列在该子集上照常聚合。ss 轨的回退语义镜像 ctx 轨: 当某篇无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 full/ctx 共享同一 n_articles 分母。已知局限须如实披露: 功能词比率是词性计数的机械代理, 受分词与词性标注误差影响; 它与本模块其余复杂度测度 (如名词化率、难字率) 度量文本风格的不同侧面, 属互补而非替代, 回归中作为可读性控制变量层叠使用时须注意共线性。

## VAR: avg_function_word_full

【变体差分】
本列是家族的 canonical 轨 (full 轨), 也是留篇门控的判定轨。full 轨文本 = content_full = 标题 prepend 到全文正文后的完整报道体, 在 stage 14 ctx_materializer 物化。该轨对应最完整的文本证据面: 一篇报道的功能词比率在 full 轨上以全文所有非标点 token 为分母、六类虚词前缀 token 为分子计算, 再取某 bank-year 内全部留篇报道的算术均值。之所以 full 轨是 canonical 而非 ctx/ss, 是因为留篇门控为 full-only (2026-06-29): 一篇报道是否被判为"一篇银行金融科技报道"并计入面板行宇宙, 仅由 llm_verified_full 决定; 因此 full 轨的行集是最大集, ctx 与 ss 轨的行集是其子集。在实证上, full 轨功能词比率宜作为该家族的首要测度进入可读性控制向量与描述统计, 而 ctx/ss 轨作为并排的稳健性轨。铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 三轨同名列严禁混入同一 over-identified 的 Hansen J 过度识别检验; full 轨也不与本模块高共线的其它复杂度列 (如名词化、难字率) 无差别地同进一回归式, 须按构念区分层叠或择一。full 轨中位文本较长 (标题加全文正文), 分母 n_real 通常最大, 使得该轨功能词比率的方差相对最稳定, 是三轨中信噪比最高的一支。功能词六类前缀 (助词、介词、连词、代词、语气词、叹词) 在全文尺度下覆盖最充分, 全文行文的连接词与代词回指越密集, 该轨比率越高, 越指示叙事化、铺陈化的报道风格; 反之比率越低越接近信息密集的正式披露体。因此 full 轨读数最适合作为可读性描述统计与控制向量的首选口径。

## VAR: avg_function_word_ctx

【变体差分】
本列是 ctx 轨 (实体窗口轨), 属家族的稳健性轨而非 canonical 轨。ctx 轨文本 = content_ctx = 标题 prepend 加上围绕目标实体 (银行、金科词) 的上下文窗口片段, 在 stage 14 ctx_materializer 物化。相较 full 轨取全文, ctx 轨把文本收窄到实体邻近语境, 意在剔除与银行金科主题无关的段落噪声, 聚焦于报道真正谈论目标实体的局部行文风格。其功能词比率同样以该轨文本的非标点 token 为分母、六类虚词前缀 token 为分子计算, 再取 bank-year 均值。与 full 轨的关键差分在于文本域: ctx 轨中位文本显著短于 full 轨 (实体窗口截取), 因而分母 n_real 较小, 单篇比率的抽样波动相对更大, 在早期试跑 T=2 样本上可能出现更多退化格。留篇门控为 full-only, 故 ctx 轨在 full 留篇集的子集上聚合, 为 conditional-on-full 测度。铁律复述: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨同名列严禁混入同一 over-identified 的 Hansen J。ctx 轨的价值在于提供一个"实体聚焦"口径下的功能词密度对照——若主结论在 full 与 ctx 两个文本域下方向一致, 则说明结论不由取全文还是取实体窗口这一文本切分选择驱动, 从而增强稳健性叙事。由于实体窗口截断可能切断跨句的连接词与代词回指链, ctx 轨功能词比率的绝对水平未必与 full 轨可比, 实证中应比较标准化后的方向与显著性, 而非直接比对两轨的原始比率水平。

## VAR: avg_function_word_ss

【变体差分】
本列是 ss 轨 (同句共现轨), 三轨中文本域最窄的一支, 属家族的稳健性轨。ss 轨文本 = content_ss = 标题 prepend 加上银行与金科词严格同句 (± N 句窗, ss_sentence_radius 默认 1) 共现的句子片段, 在 stage 14 物化。这是最保守的证据面: 只保留银行与金融科技在同一句话内真正共现的行文, 意在最大限度排除银行与金科被分散提及但并非实质关联的报道段落。其功能词比率以该轨文本的非标点 token 为分母、六类虚词前缀 token 为分子计算并取 bank-year 均值。ss 轨的回退语义严格镜像 ctx 轨: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 full/ctx 共享同一 n_articles 分母, 保证三轨分母口径一致、优雅降级不产生单边孤儿。因文本域最窄, ss 轨分母 n_real 通常最小, 抽样波动最大, 在早期试跑样本 (T=2) 上可能出现较多零方差或全 NaN 的退化, 属预期而非缺陷, 生产语料 (T=19) 上恢复正常。留篇门控 full-only 下 ss 轨在 full 留篇集子集上聚合, 为 conditional-on-full 稳健性轨。铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨同名列混入同一 over-identified 的 Hansen J 过度识别检验; ss 轨提供最严判据下的功能词密度对照, 与 full/ctx 共同构成从宽到严的文本域稳健性梯子。

<!-- rendered-citations:begin -->
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Tausczik, Y. R., & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC and computerized text analysis methods. Journal of Language and Social Psychology, 29(1), 24-54. https://doi.org/10.1177/0261927X09351676
Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x
Sproat, R., & Emerson, T. (2003). The first international Chinese word segmentation bakeoff. Proceedings of the Second SIGHAN Workshop on Chinese Language Processing, 133-143. https://doi.org/10.3115/1119250.1119269
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual Analysis in Accounting: What's Next? Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12825
Crossley, S. A. (2024). Developing Linguistic Constructs of Text Readability Using Natural Language Processing. Scientific Studies of Reading. https://doi.org/10.1080/10888438.2024.2422365
Pan, W., Li, X., Chen, X., & Xu, R. (2024). Textual form features for text readability assessment. Natural Language Processing. https://doi.org/10.1017/nlp.2024.50
<!-- rendered-citations:end -->
