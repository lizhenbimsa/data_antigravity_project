---
family_id: F161
columns:
- complexity_frac_ctx
- complexity_frac_full
- complexity_frac_ss
unit: 词频占比 (proportion, 无量纲, 理论域 [0,1]; 空文本时为 NaN)
formula: "文章级 complexity_frac = n_complexity / n_tokens; n_complexity = 命中 L&M 复杂度子词典的 token 计数, n_tokens = 排除纯标点/纯数字/下划线后的 jieba 词数; bank-year 面板列 = 该行留篇集内文章级 frac 的均值 (逐轨)"
producer: news_process/pipeline/sentiment/lm_non_sentiment.py::_compute_lm_non_sentiment_for_text ; news_process/pipeline/panel/codebook.py (provenance 注入)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (_dual_analyze 三轨调用)
citations:
- doi: 10.2308/tar-2023-0716
  type: journal
  authors: Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S.
  year: 2026
  title: "Using GPT to measure business complexity"
  venue: The Accounting Review
  vol: 101
  issue: 3
  pages_or_artno: 67-102
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting—A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: 843
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
- doi: 10.1016/j.jcae.2023.100395
  type: journal
  authors: Yu, W., & Zhao, G.
  year: 2024
  title: "Textual disclosure complexity and analysts' weighting of information"
  venue: Journal of Contemporary Accounting & Economics
  vol: 20
  issue: 1
  pages_or_artno: 100395
- doi: 10.1111/1475-679X.12179
  type: journal
  authors: Bushee, B. J., Gow, I. D., & Taylor, D. J.
  year: 2018
  title: "Linguistic complexity in firm disclosures: Obfuscation or information?"
  venue: Journal of Accounting Research
  vol: 56
  issue: 1
  pages_or_artno: 85-121
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是"银行金融科技相关新闻文本的语言复杂度密度", 即在一篇报道的有效词流中, 落入 Loughran-McDonald 复杂度 (complexity) 子词典的词所占的比例, 再在 bank-year 层面对该行当年留存报道求均值。构念承袭财务文本分析里的一个成熟主张: 披露文本并非透明的信息管道, 其用词的抽象度、专业度与句法负荷会影响读者的信息处理成本, 从而在信息含量与"混淆" (obfuscation) 之间产生张力。复杂度词属于 Loughran & McDonald (2011) 在解析 10-K 报告时界定的六类非情感子词典之一 (uncertainty / litigious / constraining / strong_modal / weak_modal / complexity), 它们不表达褒贬极性, 而是刻画文本的认知负荷维度。在本项目中, 复杂度子集连同其余五类由手工 stub 全面替换为经审计的中文主译全本 loughran_mcdonald_zh_2026, 复杂度类别收词 129 个 (六子集合计 1717 词)。数据源与替换过程记录于 pipeline/sentiment/lm_non_sentiment.py 模块 docstring: 原 314 词 stub (v0.1.5, 待审计) 已按用户指令用 loughran 主译全本对应非极性类别彻底替代并从 tone_dicts.json 删除, 因此这是一次有意的测度变更而非行为保持, 对应 18 个 frac 面板列 (六子集 × full/ctx/ss) 数值随词表扩张而改变, golden 须受控重生 (M0 门)。

【方法学与计算】
文章级计算入口 _compute_lm_non_sentiment_for_text 对单篇文本先用 jieba 分词, 再按 Loughran & McDonald (2011) 的占比口径确定分母: 分母 n_tokens 只数含字母或汉字的"真词" token, 用正则剔除纯标点、纯数字与下划线串 (否则约 19% 的标点/数字 token 会把词数分母系统性做大、把复杂度占比压低)。分子 n_complexity 是逐 token 在复杂度 frozenset 上做 O(1) 命中计数; complexity_frac = n_complexity / n_tokens, 当 n_tokens 为 0 (空文本或全被剔除) 时取 NaN。该函数本身是 track-agnostic 的: 上游 tone_words 的 _dual_analyze 分别以 content_full、content_ctx、content_ss 三种文本各调用一次, 于是同一算法在三条文本轨上生成三列文章级 frac, 再聚合到 bank-year 面板得到 complexity_frac_full / _ctx / _ss。三条文本轨在 stage 14 (ctx_materializer) 物化, 标题一律 prepend 进正文; full 轨=标题+全文正文, ctx 轨=标题+实体上下文窗口, ss 轨=标题+银行与金融科技同句共现窗口。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某行某年的分母, 只看 full 轨的 LLM 判定, ctx/ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 逐轨列照算但分母口径统一。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技同句共现时, content_ss 退化为全文正文, 相应 fallback 标记置真。关键口径铁律: 三条文本轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 full/ctx/ss 三列混进同一条 over-identified 的 Hansen J 过度识别检验。

【文献定位】
复杂度作为文本测度有清晰的会计与金融文献谱系。You & Zhang (2009) 以 10-K 文件长度刻画财务报告复杂度, 发现投资者对复杂披露信息反应不足; Loughran & McDonald (2011) 则给出可复用的复杂度词表, 使"复杂度"从篇幅代理走向词典化的、可跨文本比较的密度测度。Bushee, Gow & Taylor (2018) 进一步把语言复杂度分解为"信息"成分与"混淆"成分, 指出复杂度既可能承载真实信息也可能是遮蔽, 这正是本家族测度需要在稳健性叙事中审慎解读的核心张力。近期研究把该构念推向新方法与新场景: Loughran & McDonald (2024) 系统讨论如何测量公司复杂度并给出多维度基准; Yu & Zhao (2024) 检验文本披露复杂度如何影响分析师对信息的加权; Lesmy, Muchnik & Mugerman (2025) 做跨国比较, 记录财务报告复杂度的增长趋势; Bernard, Blankespoor, de Kok & Toynbee (2026) 则用 GPT 直接测量业务复杂度, 提示词典法与生成式测度之间的互补与校验空间。本家族沿用词典法路线, 与上述文献在构念上同源、在实现上以中文主译全本落地。

## VAR: complexity_frac_full

【变体差分】
本列是复杂度密度的 full 文本轨。full 轨的输入文本 content_full = 标题 prepend + 全文正文, 是三条轨中信息最完整、覆盖最广的一条, 因而也是留篇门控 (full-only, 2026-06-29) 的判定所依据的轨: 一篇报道是否计入某行某年 bank-year 分母, 只看该篇 full 轨的 LLM 判定, 故 complexity_frac_full 的行宇宙即该行当年的完整留篇集本身, 而非其子集。文章级 frac 的计算与家族 CORE 完全一致 (分子=复杂度词命中数, 分母=剔除纯标点/纯数字/下划线后的 jieba 真词数), bank-year 列取该留篇集内各篇 frac 的均值。相对于 ctx/ss 两条较窄的轨, full 轨最不易因窗口截断而丢失复杂度用词, 因此在噪声与稳定性上通常是三轨中方差较小、可比性最强的参照; 但它也最容易把与银行金融科技主题无关的背景段落纳入分母, 从而在专题针对性上弱于 ctx/ss。三条文本轨各自 just-identified 并排、互为稳健性且不分主次, 本列绝不与 complexity_frac_ctx/_ss 混入同一条 over-identified 的 Hansen J 检验。full 轨无同句共现回退问题 (回退仅出现在 ss 轨), 故本列的 fallback 标记恒不触发, 分母即完整留篇集, 是三列中口径最直接、最无歧义的一条。在实证使用上, 若需要一个刻画"该行当年报道整体语言复杂度"的稳定基准, 通常以本列为首选参照, 而把 ctx/ss 两列作为收敛到银行主体语境后的针对性稳健性对照; 三者之间的差异本身也可用于诊断复杂度用词是集中于银行金融科技核心语段还是弥散于全文背景, 但该诊断只作为并行测量的解读线索, 不构成主从排序。

## VAR: complexity_frac_ctx

【变体差分】
本列是复杂度密度的 ctx (context) 文本轨。ctx 轨的输入文本 content_ctx = 标题 prepend + 实体上下文窗口, 只截取围绕目标银行实体的邻近上下文而非全文, 意在把复杂度密度收敛到与银行主体直接相关的语段, 降低无关背景段落对占比的稀释。文章级算法与家族 CORE 一致, bank-year 列取均值。相对 full 轨, ctx 轨在专题针对性上更强, 但代价是窗口截断可能丢失分散在正文他处的复杂度用词, 使 frac 的取值与方差相对 full 轨发生偏移; 二者不存在主从关系, 而是对同一构念在不同文本切片上的并行测量。留篇门控采用 full-only 口径, 故本列是 conditional-on-full 的测度轨: 其行宇宙是 full 留篇集的子集, 分母口径与 full 统一, 逐轨 frac 照算。三条文本轨各自 just-identified 并排、互为稳健性、不分主次, complexity_frac_ctx 严禁与 _full/_ss 混进同一条 over-identified 的 Hansen J。ctx 轨本身不涉及同句共现回退 (回退语义专属 ss 轨, 且 ss 回退正是镜像 ctx 的全文退化)。需要强调的是, ctx 与 ss 的区别在于窗口的界定原语不同: ctx 以目标银行实体为中心取上下文窗口, 而 ss 要求银行与金融科技在同一句内共现, 因此 ctx 轨的语料通常比 ss 轨宽、比 full 轨窄, 在专题针对性与词覆盖之间取折中。就复杂度这一构念而言, 收敛到银行实体上下文有助于剥离与银行主体无关的宏观背景描述, 使复杂度密度更贴近"关于该银行的叙述"本身, 这也是把本列与 full 轨并列作为互稳健对照的意义所在。

## VAR: complexity_frac_ss

【变体差分】
本列是复杂度密度的 ss (same-sentence) 文本轨, 三轨中最窄。ss 轨的输入文本 content_ss = 标题 prepend + 银行与金融科技同句共现窗口 (窗口半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 ±1 句), 只保留银行主体与金融科技主题在同一句 (及邻近窗口) 共现的语段, 因而复杂度密度被约束在最贴合"银行谈金融科技"这一核心语境的文本上。文章级算法与家族 CORE 一致, bank-year 列取均值。ss 轨的独有语义是回退: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 优雅退化为全文正文 (ss_is_fallback 置真), 此退化行为严格镜像 ctx 轨的语义, 与 full 轨共享同一 n_articles 分母口径; 这意味着在共现稀疏的样本上, ss 列会与 full 列趋同, 解读时须结合 fallback 标记。留篇门控为 full-only, 故本列同为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集。三条文本轨各自 just-identified 并排、互为稳健性、不分主次, complexity_frac_ss 绝不与 _full/_ctx 混入同一条 over-identified 的 Hansen J 过度识别检验。由于 ss 轨语料最窄, 其文章级 n_tokens 分母通常最小, 复杂度占比对个别复杂词的命中最为敏感, 方差相对 full/ctx 更大, 在共现稀疏的样本上还会因回退而与 full 轨趋同; 因此本列在解读时最需结合样本共现密度与 fallback 比例, 作为"银行谈金融科技这一核心语境下的复杂度密度"的针对性稳健性测量, 而非独立于其余两轨的主测度。

<!-- rendered-citations:begin -->
Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S. (2026). Using GPT to measure business complexity. The Accounting Review, 101(3), 67-102. https://doi.org/10.2308/tar-2023-0716
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting—A comparative study. Humanities and Social Sciences Communications, 12, 843. https://doi.org/10.1057/s41599-025-06094-y
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Yu, W., & Zhao, G. (2024). Textual disclosure complexity and analysts' weighting of information. Journal of Contemporary Accounting & Economics, 20(1), 100395. https://doi.org/10.1016/j.jcae.2023.100395
Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in firm disclosures: Obfuscation or information?. Journal of Accounting Research, 56(1), 85-121. https://doi.org/10.1111/1475-679X.12179
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
<!-- rendered-citations:end -->
