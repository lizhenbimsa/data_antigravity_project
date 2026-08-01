---
family_id: F257
novelty_exempt_rationale: "停刊代理剔除(exc_)×语言学规则消融(advonly)双重变体家族, 测度定义依据姜富伟(2021)母族词典与规则消融方法论(Taboada et al. 2011), 非独立新构念, 无需追加2023+新颖引文。"
columns:
- exc_jiang_2021_score_advonly_ctx
- exc_jiang_2021_score_advonly_full
- exc_jiang_2021_score_advonly_ss
unit: 情感倾向分值 (无量纲, 词典法自归一化), 银行-年聚合均值
formula: "exc_jiang_2021_score_advonly{track} = mean_{a ∈ 非停刊代理媒体, 该 bank-year} jiang_2021_score_advonly{track}(a); 文章级分子 jiang_2021_score_advonly = 仅启用转折(adversative)语言学规则的姜富伟(2021)词典 tone 得分"
producer: news_process/pipeline/panel/attention_media.py (C.4 动态发现块; 文章级分子 = news_process/pipeline/sentiment/tone_words.py)
upstream:
- 22_tone_words.parquet (jiang_2021_score_advonly_{full,ctx,ss})
- 40_panel_export_main (停刊代理检测 _is_ceased_media)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, & 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
- doi: "10.1093/llc/fqae013"
  type: "journal"
  authors: "Venglařová, K., & Matlach, V."
  year: 2024
  title: "Beyond content: discriminatory power of function words in text type classification"
  venue: "Digital Scholarship in the Humanities"
  vol: "39"
  issue: "2"
  pages_or_artno: "765-789"
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
本家族度量的是"剔除疑似停刊媒体后、以姜富伟(2021)中文金融情感词典的转折规则消融变体计算的银行-年报道情绪均值"。三层构念叠加缺一不可。第一层是停刊代理稳健性口径, 即前缀 exc_ 的语义: 生产函数在 attention_media.py 中先对每家媒体做覆盖退出检测, 把某银行话题上不再产出报道、疑似退出覆盖的媒体标记为 _is_ceased_media, 随后仅在"仍在覆盖"的存活媒体子样本上重算情绪均值。需要强调的是, 本实现以"话题覆盖退出"作为报纸停刊的保守代理(proxy), 而非经证实的出版停刊, 媒体可能仍在正常出版只是不再覆盖该银行话题; 因此下游 exc_ 列只可解读为"疑似退出覆盖媒体"的保守剔除稳健性口径, 不可在论文中表述为严格的出版停刊(publication cessation)口径。第二层是词典来源: jiang_2021 指姜富伟、孟令超、唐国豪(2021)在《经济学(季刊)》发表的中文媒体文本情绪词典, 该词典面向中文财经媒体文本构建正负情绪词表, 是本项目六部并列词典之一。第三层是语言学规则消融维度: 后缀 advonly 表示在计分时只启用三条语言学规则中的转折(adversative)一条, 关闭否定翻转与程度副词两条。文章级分子 jiang_2021_score_advonly 是词典法自归一化、值域有界的情感倾向分, 再由面板层在 bank-year 粒度、存活媒体子集上取算术均值聚合为本列。

【方法学与计算】
计算链路分两段。文章级段在 tone_words.py 中完成: 对每篇报道用姜富伟(2021)词表统计正负词命中, 并把三条语言学规则以幂集方式物化为八个消融变体 raw、negonly、degonly、advonly、negdeg、negadv、degadv 与全规则版, 每个变体各自归一化、非可加分解; advonly 变体只让转折连词(如"但是""然而")触发的语义反转规则生效, 其余两条规则一律不施加, 以此隔离转折规则单独的边际贡献。面板层段在 attention_media.py 的 C.4 动态发现块完成: 先由 _is_ceased_media == 0 筛出存活媒体子样本 df_alive, 再对匹配情绪前缀模式的文章级列按 target_bank 与 year 分组取均值, 前缀加 exc_ 后左连接进面板。三条轨道 full/ctx/ss 各自独立走这条链路: full 轨用标题 prepend 加全文正文, ctx 轨用标题加实体窗口文本, ss 轨用标题加银行与金科同句共现窗文本; 缺列时守卫优雅跳过。留篇门控遵循 full-only 口径(2026-06-29), 一篇报道是否计入银行金科报道宇宙只看 full 轨的 llm_verified_full, ctx/ss 为 conditional-on-full 的稳健性轨。ss 轨回退语义镜像 ctx: 无银行金科同句共现时以全文正文回退。停刊媒体对应的 exc_ 情感列按契约保持 NaN, 绝不连带零填。

【文献定位】
词典法与机器学习法在披露情绪测量上的相对表现由 Frankel、Jennings 与 Lee (2022) 在 Management Science 系统比较, 其结论支持把词典法与其它方法并列为互为稳健性的测度而非唯一真相, 这正是本项目把六部词典、三家 LLM、三个 BERT 并排的方法学依据。姜富伟等 (2021) 提供本家族词表的原始出处与中文财经语料的构建思路。Du、Huang、Wermers 与 Wu (2022) 在 Review of Finance 强调中文金融情感词典的语言与领域专属性, 论证了不能照搬英文 Loughran-McDonald 词表而须用本土词典的必要性。van Atteveldt、van der Velden 与 Boukes (2021) 通过与人工标注对比量化了词典法的效度边界。Taboada 等 (2011) 系统阐述基于词典的情感分析中否定、程度与转折等语境价移(contextual valence shifting)规则, 是本家族 advonly 转折规则消融的方法学根基; Barbaglia 等 (2025) 在经济文本上给出词典法的近期应用范式。Bian 等 (2021) 提供另一部可比较的中文金融情感词典。Jiang、Lee、Martin 与 Zhou (2019) 在 Journal of Financial Economics 论证经理层情绪对股票回报的预测力, 为文本情绪测度的经济含义提供支撑。方法学口径上, 词典消融梯度(raw 至全规则八变体)属规格稳健性并排: 各消融变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同变体混进同一 over-identified Hansen J; 同理三轨 full/ctx/ss 亦各自 just-identified 并排、禁混同一 over-identified Hansen J。词典消融梯度与停刊代理口径正交, 不交叉物化以避免列爆炸。 就本家族两个构造环节, 尚可各补前沿依据。停刊剔除一侧, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 为本家族「剔除疑似退出覆盖媒体后再作银行—年度聚合」提供现实动机: 媒体退出是真实且有经济后果的样本组成变化。迁移边界在于, 原文的停刊判定取自外部事件数据、DV 为本地股票交易活动, 而本项目的 ceased_set 是自语料内部推断的保守代理 (confirmed 与 suspected 之并), 并非严格停刊事实, 用途亦仅限稳健性子样本而非识别冲击; 该文为工作论文, 未经同行评审。转折规则一侧, Venglařová 与 Matlach (2024) 实证显示功能词 (含连词一类非内容词) 在文本类型判别上具有独立于内容词的信息量, 支持本家族把转折/逆接连词视为一个与词项极性无关的独立语言维度, 值得单列为一条可独立开关的规则臂; 惟原文任务为文本类型分类, 并不区分转折连词与其他功能词类, 语料亦非中文金融新闻、不涉及银行—年度聚合, 故其仅在「转折连词自带独立信息」这一构念层面与 advonly 臂相通。Iqbal 与 Pfarrer (2025) 则以共指消解为例, 证明一项具体的语言学处理选择会系统性改变文本测度取值、并构成实质的测量误差来源, 与本项目不对语言学规则作默认采纳、而把其后果显式物化为消融臂的立场同向; 但须强调该文所处理的是实体指代还原 (在本项目中对应 ctx/ss 实体窗口轨而非规则消融族), 与否定/程度/转折三规则非同一规则, 且其取向是规范性的——主张采纳该规则以减少误差, 而本项目令七臂互为稳健性并排、不设主次, 故不得以之作为 powerset 规则消融设计的同构先例。
## VAR: exc_jiang_2021_score_advonly_ctx

【变体差分】
本列是三轨中的 ctx 轨。轨道语义: ctx 轨的文章级底层文本是"标题 prepend + 实体窗口"(content_ctx), 即在标题之后拼接围绕目标银行实体前后若干句的上下文窗口, 而非全文。相对家族的 full 轨(canonical 主轨), ctx 轨把计分文本收窄到银行实体邻近语境, 目的是削弱与银行无关的段落对情绪信号的稀释, 因此它是主轨的稳健性并排轨而非替代。在留篇门控上, 本列遵循 full-only 口径: 一篇报道是否被计入银行金科报道宇宙只由 full 轨的 llm_verified_full 决定, ctx 轨是 conditional-on-full 的测度, 其行宇宙是 full 留篇集的子集, per-track 情绪列在该子集上照算。其余三层构念与家族一致: exc_ 前缀表示仅在非停刊代理(存活覆盖)媒体子样本上聚合, advonly 表示词典计分时只启用转折规则而关闭否定翻转与程度副词, jiang_2021 表示采用姜富伟(2021)中文金融情感词典。本列与 full 轨、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混入同一 over-identified Hansen J 检验。dev 语料早期试跑 T=2 下 ctx 轨可能出现零方差退化属预期, 生产 T=19 语料上恢复正常方差。与家族内其它规则消融变体(如 raw、negonly、degonly)的区别在于计分规则集: 本列固定为仅转折规则一条, 其数值差异完全归因于转折连词触发的语义反转在实体窗口文本上的边际作用; 相对于同轨的全规则版本, 若两者系数接近, 则说明否定与程度副词规则在 ctx 轨上的增量信息有限, 反之则提示需保留完整规则栈。停刊媒体对应值按契约保持 NaN, 绝不连带零填。

## VAR: exc_jiang_2021_score_advonly_full

【变体差分】
本列是三轨中的 full 轨, 也是家族的 canonical 主轨。轨道语义: full 轨的文章级底层文本是"标题 prepend + 全文正文"(content_full), 即以完整报道正文参与词典计分, 覆盖面最广、信号最完整。full 轨在本项目中承担留篇门控的唯一裁决角色: 一篇报道是否被判为银行金科报道、是否进入 n_articles 分母与银行金科报道宇宙, 只看 full 轨的 llm_verified_full == True(full-only 口径, 2026-06-29); 因此 full 轨的行宇宙是三轨中的全集, ctx 与 ss 两轨的行宇宙都是它的子集。其余三层构念与家族一致: exc_ 前缀表示先剔除疑似停刊(覆盖退出代理)媒体、只在存活媒体子样本上按 target_bank 与 year 分组取情绪均值, advonly 表示在姜富伟(2021)词典计分时只启用转折(adversative)一条语言学规则、关闭否定翻转与程度副词两条, 以隔离转折规则的单独边际贡献。本列与 ctx 轨、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混入同一 over-identified Hansen J 检验。作为家族 canonical 主轨, 本列在做词典消融梯度稳健性叙事时通常充当基准臂: 把本列(advonly, full)与同轨的全规则版、其它单规则或组合规则消融变体逐一对照, 可以在最完整的正文语境下分离出转折规则单独的贡献, 从而判断姜富伟(2021)词典在中文财经报道上是否高度依赖转折结构。停刊媒体对应值按契约保持 NaN, 绝不连带零填, 以免把"该银行-年无存活媒体报道"误读为情绪中性。

## VAR: exc_jiang_2021_score_advonly_ss

【变体差分】
本列是三轨中的 ss 轨(sentence-level 银行金科同句共现轨)。轨道语义: ss 轨的文章级底层文本是"标题 prepend + 银行与金科同句共现窗"(content_ss), 即只保留目标银行与金融科技词在同一句子及其前后 N 句窗内共现的文本片段(窗口半径由 config 的 ss_sentence_radius 控制, 默认为 1)参与词典计分, 是三轨中语境最紧、最聚焦于银行金科交叉议题的轨道。ss 轨的关键契约是回退语义镜像 ctx: 当某报道不存在银行与金科的同句共现时, content_ss 回退为全文正文, 并置 ss_is_fallback 为真, 与 ctx 轨共享 n_articles 分母; 当金科 AC 自动机为空时该轨优雅降级、is_fallback 全真。留篇门控同样遵循 full-only 口径, ss 轨为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集。其余三层构念与家族一致: exc_ 仅在非停刊代理媒体子样本聚合, advonly 只启用转折规则, jiang_2021 采用姜富伟(2021)词典。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。早期试跑 T=2 下 ss 轨易零方差退化属预期, 因同句共现样本在短面板上极稀。相对 full 与 ctx 两轨, ss 轨把情绪信号锁定在"银行与金融科技在同句共现"的最窄语境, 因此它对银行金科交叉议题的情绪最敏感、对无关段落的稀释最不敏感; 但代价是回退比例可能偏高, 使用时须结合 ss_is_fallback 判断有效样本占比。与同家族其它消融变体一致, 本列固定仅转折规则, 数值差异归因于转折连词在同句共现窗上的语义反转作用。停刊媒体对应值按契约保持 NaN, 绝不零填。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
