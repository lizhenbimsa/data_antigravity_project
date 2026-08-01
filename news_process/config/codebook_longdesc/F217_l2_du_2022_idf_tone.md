---
family_id: F217
columns:
- du_2022_idf_tone_app_ctx
- du_2022_idf_tone_app_full
- du_2022_idf_tone_app_ss
- du_2022_idf_tone_ctx
- du_2022_idf_tone_full
- du_2022_idf_tone_hw_ctx
- du_2022_idf_tone_hw_full
- du_2022_idf_tone_hw_ss
- du_2022_idf_tone_mw_ctx
- du_2022_idf_tone_mw_full
- du_2022_idf_tone_mw_ss
- du_2022_idf_tone_ss
- du_2022_idf_tone_std_ctx
- du_2022_idf_tone_std_full
- du_2022_idf_tone_std_ss
- du_2022_idf_tone_tech_ctx
- du_2022_idf_tone_tech_full
- du_2022_idf_tone_tech_ss
- du_2022_idf_tone_vw_ctx
- du_2022_idf_tone_vw_full
- du_2022_idf_tone_vw_ss
unit: 语调得分 (无量纲, 均值口径约 [-1,1]; std 口径为组内标准差 ≥0; 聚合为 bank-year 面板值)
formula: "article: du_2022_idf_score = Σ_w [base_score(w) × idf_weight(w) × rule_multiplier(w)] / n_words; idf_weight(w) = Winsorize_{P1,P99}( log10(N/(1+df(w))) / mean_idf ); panel(mean/std/vw/mw/hw): 见各 VAR 节"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _build_idf_weighted_dict ; news_process/pipeline/panel/encode.py (bank-year 聚合) ; news_process/pipeline/panel/geography.py (跨词典均值)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_idf_score 三轨)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
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
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
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
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: Tetlock, P. C.
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: "10.1016/j.jfineco.2022.11.006"
  title: "The colour of finance words"
  authors: "García, D., Hu, X., & Rohrer, M."
  year: 2023
  venue: "Journal of Financial Economics"
  type: "journal"
- doi: "10.1016/j.pacfin.2025.102854"
  title: "The colour of finance words in Chinese"
  authors: "Yao, K., Zheng, Z., & Liu, C."
  year: 2025
  venue: "Pacific-Basin Finance Journal"
  type: "journal"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1016/j.jfineco.2022.11.006"
  - "10.1016/j.pacfin.2025.102854"
---

## CORE

【构念与来源】
本家族刻画的是「以词级信息量重新加权后的 du_2022 词典语调」这一构念。基础语调家族对一篇报道内出现的每个情感词按相等权重累加极性分, 而本家族在累加之前先给每个情感词乘上一枚 IDF (inverse document frequency, 逆文档频率) 权重, 使得像「发展」「提高」这类几乎每篇金融新闻都会出现、信息量稀薄的高频词被压低, 而像「违约」「挤兑」「处罚」这类只在少数报道中出现、一旦出现便高度说明问题的稀有词被放大。构念上, 它回答的问题不是「这篇报道整体上偏正面还是偏负面」, 而是「在剔除样板套话、只看真正携带辨识度信息的词之后, 这篇报道对目标银行涉金融科技议题的语调是正是负、强度几何」。底层情感极性词典采用 Du、Huang、Wermers 与 Wu (2022) 构建的中文金融情感词典 du_2022 (正面 2,235 词 / 负面 2,986 词, 另含政治正面词 1,434 词以 0.5 权重计入正侧, 即生产口径 polw05), 该词典针对中文金融文本领域特异性做了本土化扩充, 相较于由英文 Loughran 与 McDonald (2011) 词典机械翻译而来的版本更贴合中文语料。词级信息量加权的思想源自 Spärck Jones (1972) 的术语特异性统计解释, 并在金融文本分析中由 Jegadeesh 与 Wu (2013) 的「词力量 (Word Power)」框架系统化为对情感词按其区分度赋权的做法。

【方法学与计算】
计算分两阶段。第一阶段在文章级 (stage 22, tone_words.py) 完成: 对全语料按唯一文档去重后统计每个情感词的文档频率 df(w) 与总文档数 N, 以平滑公式 raw_idf(w)=log10(N/(1+df(w))) 得到原始 IDF, 再做两步稳定化处理 —— 均值归一化 (normalized_idf=raw_idf/mean_idf, 使加权后得分量级与等权版相当, 可共享阈值) 与 P1/P99 Winsorization (削平最极端 1% 权重, 防止某个超稀有词一词定乾坤)。归一化后的权重乘入词典 base_score, 再叠加与之正交的语言学规则乘子 (否定翻转、程度副词、转折), 逐篇归一得到 du_2022_idf_score。⚠ 一个承重口径: IDF 权重在含标题的 content_full 语料上统一计算一次, full/ctx/ss 三轨共享同一份权重 (绝不按轨分语料重算), 只有分子的词频匹配按各轨文本进行。第二阶段在面板级 (stage 40, encode.py) 把文章级 idf_score 聚合到 bank-year, 衍生出等权均值 (无后缀 canonical)、组内标准差 (std)、以及三种加权聚合 (vw 提及密度加权 / mw 媒体权威加权 / hw 跟风衰减加权), 并对技术类 (tech) 与应用类 (app) 两个金融科技分类子集分别再算等权均值。这 7 种聚合口径各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同聚合口径混进同一 over-identified Hansen J 过度识别检验。留篇与行宇宙口径遵循全项目 full-only 门控 (2026-06-29): 一篇报道是否计入 bank-year 由 full 轨留篇判定, ctx/ss 轨是 conditional-on-full 的稳健性测度; ss 轨在无「银行∧金科同句共现」时回退为全文正文, 镜像 ctx 的回退公理。三轨各自 just-identified 并排, 同样禁混同一 Hansen J。

【文献定位】
方法学上, 本家族坐落在金融文本情感测量的词典法一支。Loughran 与 McDonald (2011) 奠定了「用领域特定词典而非通用心理学词典读财务文本」的范式, Du 等 (2022) 将其精神迁移到中文金融语境并给出 du_2022 词典。等权词典法的一个已知弱点是把高频功能词与稀有信息词同等对待, Spärck Jones (1972) 的 IDF 与 Jegadeesh 与 Wu (2013) 的词力量框架正是对此的修正 —— 后者证明按词的区分度赋权能显著提升情感度量对未来收益的预测力。在聚合层面, Tetlock (2007) 开创了把媒体语调先分后合聚合为市场级情绪指标的做法, 是本家族 vw 提及密度加权臂的直接锚点; Holzman、Miller 与 Twedt (2023) 论证按媒体权威性加权能凸显更具定价含义的语调信号, 是 mw 媒体权威加权臂的直接锚点; Tetlock (2011) 论证陈旧信息 (含对同一事件的重复转载) 相对首发原创报道的信息含量系统性递减、投资者对陈旧信息的反应也随之减弱, 为 hw 跟风衰减加权臂 (对同一事件的重复、跟风报道逐步衰减其权重) 提供直接锚点。Garcia (2013) 则展示词典语调在不同宏观状态下具有异质的信息含量, 提示加权聚合口径的结论仍需在不同市场状态下检验其稳健性。Frankel、Jennings 与 Lee (2022) 系统比较了词典法与机器学习情感度量, 为本项目「词典 / LLM / BERT 三法互为稳健」的整体设计提供了方法论对照: IDF 加权词典轨正是词典法内部的一条稳健性支路, 与规则消融梯度、政治词权重梯度正交并列, 共同支撑主结论不被任一测量选择驱动的论证。García、Hu 与 Rohrer (2023, Journal of Financial Economics) 系统度量金融文本中哪些词真正携带定价相关信息、哪些是信息量稀薄的套话词, 为本家族按词级信息量 (IDF) 重新加权情感词典的做法提供了2023年的直接方法学支撑。Yao、Zheng 与 Liu (2025, Pacific-Basin Finance Journal) 将"金融词语颜色"(词的信息含量差异化) 框架迁移到中文语境, 与本家族在中文金融新闻上做 IDF 词级信息量加权的构念直接对应。

## VAR: du_2022_idf_tone_app_ctx

【变体差分】
本列是「应用类 (app) 金融科技报道子集 × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调等权均值。相较家族 canonical (du_2022_idf_tone_full, 全篇全轨等权均值), 它在两个维度上收窄: 其一, 分类子集限定为被判为「应用导向」的金融科技报道 (侧重具体金融科技产品、场景与业务落地, 与技术导向的 tech 子集互补), 分母只计入该 bank-year 内 app 类报道篇数; 其二, 文本轨为 ctx 实体窗 —— 只在目标银行实体上下文窗口内匹配情感词, 剔除与该银行无关的段落干扰。IDF 权重仍取自 content_full 全语料统一计算的那一份 (三轨共享), 只是词频匹配落在 ctx 文本上。该列作为分类维度上的稳健性子测度存在, 与 tech 子集、与全篇口径各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 app 子集与 tech 子集或全篇口径混进同一 over-identified Hansen J。ctx 轨为 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束, 未在 full 轨留篇的报道不进入本列聚合。在实证使用中, 本列通常作为分类维度稳健性面板的一员进入回归, 用来回答主效应是否由某一类金融科技叙事单独驱动的问题。研究者在解读该列时应牢记其分母是分类子集的报道篇数, 样本规模天然小于全篇口径, 故点估计的标准误往往更大, 弱识别风险更高, 这是分类子集稳健性检验固有的代价而非缺陷。把它与全篇口径同时用来解释同一结果时, 只能择一进入方程, 或分别估计后并列汇报系数, 绝不允许二者在同一工具变量集下过度识别。此外实体窗口径进一步剔除了与目标银行无关段落的语调噪声, 使得本列相对全篇口径更纯净地反映围绕该银行的应用类金科叙事情感。

## VAR: du_2022_idf_tone_app_full

【变体差分】
本列是「应用类 (app) 金融科技报道子集 × 全文 (full) 轨」的 IDF 加权 du_2022 语调等权均值。与 canonical 的差别在于分类子集: 只对被判为应用导向的金融科技报道求 IDF 加权语调的 bank-year 等权均值, 分母为该 bank-year 内 app 类报道篇数, 而非全部留篇报道。文本轨为 full (标题 prepend + 全文正文), 与 canonical 同轨, 故本列与 canonical 的唯一区分就是「是否限定 app 子集」这一分类判据。它衡量的是「银行在金融科技应用落地类叙事中获得的加权语调」, 与 tech 子集 (技术导向叙事的加权语调) 构成金融科技报道内部的两个正交侧面。app 子集口径与 tech 子集口径、与不分类的全篇口径各自 just-identified 并排, 互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J。IDF 权重仍来自 content_full 全语料统一计算的共享权重, 词频匹配落在被判 app 的报道 full 文本上。作为 full 轨列, 其行宇宙即 full-only 留篇集, 是分类维度稳健性的存档轨。在实证使用中, 本列作为分类维度稳健性存档轨进入面板, 用于检验主效应是否由应用落地导向的这一类金融科技叙事单独驱动。因分母限定为该类报道篇数, 样本规模小于全篇口径, 点估计标准误偏大、弱识别风险偏高, 属分类稳健性检验的固有代价而非缺陷。与全篇口径共同解释同一结果时只能择一进入方程, 或分别估计后并列汇报系数, 绝不允许二者在同一工具变量集下过度识别。全文轨保留标题与正文的全部语境, 相对实体窗与同句轨样本更充裕, 故本列常被视作该应用类子集下最稳健的基准存档口径, 供与技术类子集对照阅读。

## VAR: du_2022_idf_tone_app_ss

【变体差分】
本列是「应用类 (app) 金融科技报道子集 × 同句 (ss) 轨」的 IDF 加权 du_2022 语调等权均值。相对 canonical, 它同时收窄分类子集 (仅 app 类报道) 与文本轨 (ss 同句共现轨)。ss 轨只在「目标银行与金融科技词同处一句 (±N 句窗, 默认半径 1)」的最严格上下文内匹配情感词, 是三轨中语境最紧的一条; 当某报道不存在银行∧金科同句共现时, ss 文本回退为全文正文, 镜像 ctx 的回退公理, 并与 ctx 共享 n_articles 分母。IDF 权重依旧取自 content_full 全语料统一计算的共享权重, 仅词频匹配落在 ss 文本。该列把「最严格语境 × 应用导向子集」两重收窄叠加, 用作双重收窄下的稳健性对照。它与 app_full、app_ctx 三轨各自 just-identified 并排, 也与 tech 子集、与全篇口径并排, 互为稳健性、不分主次, 严禁把不同轨或不同分类子集混进同一 over-identified Hansen J。ss 轨为 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列是应用类子集与最严语境轨的双重收窄组合, 通常放在稳健性附表而非主表, 用来确认结论在最挑剔口径下依然成立。由于同句共现本就稀疏、再叠加应用类分类过滤, 该列样本规模在三轨中最小, 缺失与弱识别的风险也最高, 研究者解读时应结合有效观测数一并披露, 避免对少数格点的点估计过度外推。它与全文轨和实体窗轨的应用类孪生共同构成语境收窄的梯子, 三者只能并列汇报或规格曲线切换, 绝不允许混入同一过度识别方程。试跑语料上本列大量置空属预期退化, 生产规模下恢复正常。

## VAR: du_2022_idf_tone_ctx

【变体差分】
本列是家族 canonical 的实体窗 (ctx) 轨孪生: 全部留篇报道 (不分 tech/app 子集)、等权均值聚合、IDF 加权 du_2022 语调, 但文本轨为 ctx 而非 full。ctx 轨只在目标银行实体的上下文窗口内匹配情感词, 剔除同篇中与该银行无关段落的语调噪声, 语境紧于 full 而松于 ss。它与 du_2022_idf_tone_full (canonical 全文轨) 构成互为稳健性的一对: full 轨捕捉整篇报道对银行的加权语调, ctx 轨检验该语调是否稳健于「只看银行相关段落」的更严口径。IDF 权重仍是 content_full 全语料统一计算的共享权重, 仅词频匹配落在 ctx 文本。作为 conditional-on-full 测度, ctx 轨行宇宙是 full-only 留篇集的子集 (逐 bank-year 照算)。三轨 full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J 过度识别检验; 它们也不与 vw/mw/hw 加权口径或 tech/app 子集口径交叉进同一识别方程。在实证使用中, 本列作为语境稳健性梯子的中间一档进入回归, 位于全文轨与同句轨之间, 用来检验加权语调是否随语境收紧而系统性改变。若全文轨与实体窗轨的系数方向一致、量级相近, 则说明主结论不依赖于是否剔除银行无关段落这一测量选择, 稳健性得到支持; 若二者背离, 则提示语调信号可能来自与目标银行无关的报道内容, 需谨慎解读。三轨只能并列汇报或规格曲线逐一切换, 绝不允许同时塞进同一过度识别方程以人为制造工具变量。相较全文轨, 实体窗轨牺牲部分语境完整性以换取更强的实体相关性, 二者的取舍正是这一稳健性对照的价值所在。

## VAR: du_2022_idf_tone_full

【变体差分】
本列是本家族的 canonical (无聚合后缀、无分类后缀、full 轨): 对该 bank-year 内全部 full 轨留篇报道的文章级 du_2022_idf_score 求等权算术均值。它是家族的基准头条口径 —— IDF 词级加权 (压低高频套话词、放大稀有信息词) 后的 du_2022 词典语调, 在全篇 (标题 prepend + 全文正文) 文本上匹配、以每篇报道等权重的方式聚合到银行-年。所有其它 20 列都是相对本列在「文本轨 (ctx/ss)」「聚合权重 (std/vw/mw/hw)」或「分类子集 (tech/app)」某一维度上的变体。作为 full 轨列, 其行宇宙即 full-only 留篇集 (2026-06-29 门控): 一篇报道是否计入由 full 轨留篇判定, 这也是其它轨行宇宙的上界。IDF 权重在 content_full 全语料上统一计算一次, 由三轨共享 (绝不按轨重算)。本列与其 ctx/ss 孪生三轨各自 just-identified 并排, 与 vw/mw/hw 加权聚合各自并排, 与 tech/app 子集各自并排, 互为稳健性、不分主次, 严禁把任意两个口径混进同一 over-identified Hansen J。它同时是 geography.py 跨词典均值 dict_avg_idf_tone_full 的六词典成员之一。在实证使用中, 本列是本家族进入主表的默认头条口径, 其余二十列围绕它在文本轨、聚合权重与分类子集三个维度上展开稳健性检验。研究者引用本家族时应以本列作为主效应载体, 把三轨、四种加权与两类子集分别作为并列的稳健性支路汇报, 而非择优呈现。需要强调的是, 词级信息量加权本身就是相对无加权词典语调的一条稳健性支路, 用以证明主结论不被高频套话词主导; 因此本列与无信息量加权的等权词典语调之间也是互为稳健、不分主次的关系, 同样不得合并进同一过度识别方程。它同时是跨六部情感词典均值口径的成员之一, 供跨词典稳健性对照使用。

## VAR: du_2022_idf_tone_hw_ctx

【变体差分】
本列是「跟风衰减加权 (hw) × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调。相对 canonical 的等权均值, hw 聚合按跟风衰减权重给每篇报道赋权 (承 Tetlock (2011) 关于陈旧/重复转载新闻信息含量递减的发现): 对同一事件的跟风、重复报道逐步衰减其权重, 从而抑制「一条消息被大量转载放大」造成的语调虚增, 突出原发、非冗余的信息。计算上为加权和除以权重和, 分子 = Σ(du_2022_idf_score × herd_weight_ctx), 分母 = sum_herd_weight_ctx (按 ctx 轨独立取分母, 遵循 measurement-treatment matching, 不借 full 轨分母)。文本轨为 ctx 实体窗。IDF 权重仍取自 content_full 全语料统一计算的共享权重。本列衡量的是「剔除跟风冗余后、实体窗内的加权语调」, 与 vw (提及密度加权)、mw (媒体权威加权)、canonical (等权) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同聚合权重混进同一 over-identified Hansen J。作为 ctx 轨列, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列作为聚合权重维度的一条稳健性支路进入回归, 用以检验主效应是否稳健于剔除跟风冗余的加权方案。等权、提及密度、媒体权威与跟风衰减四种权重各自刻画不同的信息含量假设, 研究者应分别估计后并列汇报, 或在规格曲线中逐一切换, 而不得把它们塞进同一过度识别方程。需留意跟风衰减权重依赖于对事件转载链的识别, 当同一事件的重复报道难以判定时, 该权重会向等权收敛, 此时本列与无后缀口径的数值差异缩小, 应结合权重覆盖情况一并披露。实体窗轨进一步剔除银行无关段落, 使本列在跟风加权基础上更聚焦于围绕该银行的原发语调。

## VAR: du_2022_idf_tone_hw_full

【变体差分】
本列是「跟风衰减加权 (hw) × 全文 (full) 轨」的 IDF 加权 du_2022 语调, 与 canonical 同轨、同分类范围 (全部留篇报道), 唯一差别是聚合权重从等权换成跟风衰减权重 (承 Tetlock (2011) 关于陈旧/重复转载新闻信息含量递减的发现)。其经济含义是: 新闻语调对市场的信息含量并非每篇等值 —— 首发报道携带增量信息, 而随后的跟风转载多是冗余噪声, 应当衰减。分子 = Σ(du_2022_idf_score × herd_weight_full), 分母 = sum_herd_weight_full。它把「词级 IDF 信息量加权」(文章内) 与「篇级跟风衰减加权」(bank-year 内) 两层信息量修正叠加, 是本家族在聚合维度上最贴近「只保留原发信息语调」构念的一条支路。本列与 hw_ctx、hw_ss 三轨各自 just-identified 并排, 与 vw_full、mw_full、canonical 各自并排, 互为稳健性、不分主次, 严禁把不同聚合权重或不同轨混进同一 over-identified Hansen J。作为 full 轨列, 行宇宙即 full-only 留篇集。在实证使用中, 本列把文章内的词级信息量加权与银行年内的篇级跟风衰减加权两层修正叠加, 是本家族最贴近只保留原发信息语调这一构念的支路。它与等权、提及密度、媒体权威三种聚合口径并列, 用来证明主效应不由报道数量的机械堆叠或热点事件的集中转载驱动。四种权重只能并列汇报或规格曲线切换, 绝不允许合并进同一过度识别方程。当语料中跟风链条稀疏、权重趋于均匀时, 本列会退化为接近等权口径, 这属预期而非异常, 需结合语料的转载结构一并解读。汇报本列时宜同时给出跟风权重的覆盖与离散情况, 以便读者判断加权结论的稳健区间。

## VAR: du_2022_idf_tone_hw_ss

【变体差分】
本列是「跟风衰减加权 (hw) × 同句 (ss) 轨」的 IDF 加权 du_2022 语调, 把最严格语境轨 (ss) 与跟风衰减聚合叠加。ss 轨只在银行∧金科同句共现处匹配情感词, 无共现时回退全文正文 (镜像 ctx 回退公理); hw 聚合按跟风衰减权重赋权 (承 Tetlock (2011) 关于陈旧/重复转载新闻信息含量递减的发现), 分子 = Σ(du_2022_idf_score × herd_weight_ss), 分母 = sum_herd_weight_ss (按 ss 轨独立取分母; 若 stage 24 未产同句轨权重则分母退化为 NaN, 本列随之优雅置 NaN, 不连坐 full/ctx)。IDF 权重仍是 content_full 全语料共享权重。该列是「最严语境 × 剔除跟风冗余」的双重收窄稳健性对照。它与 hw_full、hw_ctx 三轨各自 just-identified 并排, 与 vw_ss、mw_ss、canonical_ss 各自并排, 互为稳健性、不分主次, 严禁把不同轨或不同聚合权重混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列是跟风衰减加权与最严语境轨的双重收窄组合, 通常置于稳健性附表, 用来确认剔除冗余转载后、在银行与金科同句范围内语调结论依然成立。由于同句共现稀疏叠加跟风权重可能缺失, 该列在三轨中最易出现缺失值, 尤其在试跑语料上大量置空属预期退化, 生产规模下恢复正常。研究者应结合有效观测数披露, 避免对少数格点过度外推。它与全文轨、实体窗轨的跟风加权孪生并列, 只能分别估计或规格曲线切换, 绝不混入同一过度识别方程, 亦不与提及密度、媒体权威口径交叉进同一识别方程。

## VAR: du_2022_idf_tone_mw_ctx

【变体差分】
本列是「媒体权威加权 (mw) × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调。相对 canonical 的等权均值, mw 聚合按 Holzman、Miller 与 Twedt (2023) 的媒体权威性给每篇报道赋权: 来自权威性更高媒体来源的报道获得更大权重, 使 bank-year 语调更贴近具备定价含义的信号。权重取自 media_weights.json (媒体来源→权威权重映射, 未命中来源落默认权重)。计算为加权和除以权重和, 分子 = Σ(du_2022_idf_score × media_authority_weight), 分母 = sum_media_authority_weight。文本轨为 ctx 实体窗, IDF 权重仍取自 content_full 全语料共享权重。本列衡量「按媒体权威加权后、实体窗内的语调」, 与 vw (提及密度加权)、hw (跟风衰减加权)、canonical (等权) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同聚合权重混进同一 over-identified Hansen J。作为 ctx 轨列, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列作为聚合权重维度的一条稳健性支路进入回归, 用以检验主效应是否稳健于让权威媒体主导的加权方案。等权、提及密度、媒体权威与跟风衰减四种权重各刻画不同的信息含量假设, 研究者应分别估计后并列汇报, 或在规格曲线中逐一切换, 而不得把它们塞进同一过度识别方程。需要留意媒体权威权重取自外部媒体权重字典, 当大量报道来源未命中而落默认权重时, 加权聚合会向等权收敛, 此时本列与无后缀口径差异缩小, 应结合权重覆盖率一并披露。实体窗轨进一步剔除银行无关段落, 使本列在权威加权基础上更聚焦于围绕该银行的语调信号。

## VAR: du_2022_idf_tone_mw_full

【变体差分】
本列是「媒体权威加权 (mw) × 全文 (full) 轨」的 IDF 加权 du_2022 语调, 与 canonical 同轨同分类范围, 唯聚合权重换成 Holzman 等 (2023) 媒体权威权重。其构念前提是: 并非所有媒体对市场同等重要, 权威主流媒体的语调更能预测投资者反应与定价, 应赋更大权重。分子 = Σ(du_2022_idf_score × media_authority_weight), 分母 = sum_media_authority_weight; 当多数来源落默认权重时, mw 语调退化为接近等权 (可通过补充 media_weights.json 缓解)。本列把词级 IDF 信息量加权 (文章内) 与篇级媒体权威加权 (bank-year 内) 叠加, 是「让权威媒体的加权语调主导」构念的直接落地。它与 mw_ctx、mw_ss 三轨各自 just-identified 并排, 与 vw_full、hw_full、canonical 各自并排, 互为稳健性、不分主次, 严禁把不同聚合权重或不同轨混进同一 over-identified Hansen J。作为 full 轨列, 行宇宙即 full-only 留篇集。在实证使用中, 本列把文章内的词级信息量加权与银行年内的篇级媒体权威加权两层修正叠加, 用来证明主效应是否由权威主流媒体的语调而非边缘来源的噪声驱动。它与等权、提及密度、跟风衰减三种口径并列, 只能分别估计或规格曲线切换, 绝不允许合并进同一过度识别方程。媒体权威权重的有效性取决于媒体权重字典的覆盖广度, 覆盖不足时本列会向等权退化; 因此在汇报本列时应同时说明权重字典的命中率, 以便读者判断加权结论的可信区间。作为全文轨列, 本列保留标题与正文的完整语境, 相对实体窗与同句轨样本更充裕, 常作为媒体权威加权族的基准存档口径。

## VAR: du_2022_idf_tone_mw_ss

【变体差分】
本列是「媒体权威加权 (mw) × 同句 (ss) 轨」的 IDF 加权 du_2022 语调, 把最严格语境轨与媒体权威加权聚合叠加。ss 轨只在银行∧金科同句共现处匹配情感词, 无共现时回退全文正文 (镜像 ctx 回退公理)。mw 聚合按 Holzman 等 (2023) 媒体权威权重赋权, 分子 = Σ(du_2022_idf_score × media_authority_weight), 分母 = sum_media_authority_weight。IDF 权重仍是 content_full 全语料共享权重。该列是「最严语境 × 权威媒体主导」的双重收窄稳健性对照, 用于检验主结论是否稳健于「只看银行相关同句、且让权威媒体加权」这一最挑剔的组合口径。它与 mw_full、mw_ctx 三轨各自 just-identified 并排, 与 vw_ss、hw_ss、canonical_ss 各自并排, 互为稳健性、不分主次, 严禁把不同轨或不同聚合权重混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列是媒体权威加权与最严语境轨的双重收窄组合, 通常置于稳健性附表, 用来确认在权威媒体主导且仅看银行与金科同句的最挑剔口径下语调结论仍成立。由于同句共现稀疏叠加权重可能落默认值, 该列样本规模小、缺失较多, 试跑语料上尤甚, 属预期退化。研究者应结合有效观测数与权重覆盖率一并披露, 避免过度外推。它与全文轨、实体窗轨的媒体权威加权孪生并列, 只能分别估计或规格曲线切换, 绝不混入同一过度识别方程, 亦不与提及密度、跟风衰减口径交叉进同一识别方程。

## VAR: du_2022_idf_tone_ss

【变体差分】
本列是家族 canonical 的同句 (ss) 轨孪生: 全部留篇报道、等权均值聚合、IDF 加权 du_2022 语调, 文本轨为三轨中语境最严的 ss。ss 轨只在「目标银行与金融科技词同处一句 (±N 句窗, 默认半径 1)」的范围内匹配情感词; 当某报道无此同句共现时, ss 文本回退为全文正文, 镜像 ctx 的回退公理, 并与 ctx 共享 n_articles 分母。它与 du_2022_idf_tone_full (canonical 全文轨)、du_2022_idf_tone_ctx (实体窗轨) 构成三轨互为稳健性: full 看整篇、ctx 看银行相关段、ss 看银行与金科同句, 三者依次收窄语境, 用于检验加权语调是否稳健于语境口径。IDF 权重仍是 content_full 全语料统一计算的共享权重, 仅词频匹配落在 ss 文本。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙是 full-only 留篇集的子集。早期试跑 T=2 语料上 ss 轨可能因同句共现稀疏而退化, 属预期现象, 生产 T=19 恢复正常。在实证使用中, 本列是语境稳健性梯子中收窄最深的一档, 通常置于稳健性附表, 用来确认加权语调在只看银行与金科同句的最紧口径下依然稳健。它与全文轨、实体窗轨构成语境依次收窄的三档梯子: 若三档系数方向一致、量级递进平滑, 则说明结论对语境口径不敏感; 若同句轨显著背离, 则提示语调信号可能来自银行与金科并未真正同句关联的段落。三轨只能并列汇报或规格曲线切换, 绝不允许同时进入同一过度识别方程以人为制造工具变量。同句共现的严格性使本列在三轨中信噪取舍最为极端, 语境最纯但样本最少, 解读时须权衡。

## VAR: du_2022_idf_tone_std_ctx

【变体差分】
本列是「组内标准差 (std) × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调离散度。它与 canonical 的关键差别在于聚合算子: canonical 取该 bank-year 内文章级 du_2022_idf_score 的均值, 本列取同一批分数的样本标准差 (pandas std, 默认 ddof=1)。因此它衡量的不是语调的水平, 而是语调在报道之间的分歧程度 —— 一个银行在某年若既有高度正面又有高度负面的加权报道, std 会偏大; 若众口一词, std 偏小。单位上它是非负量 (≥0), 与均值列的 [-1,1] 量纲口径不同, 不可与均值列直接相加或比较水平。文本轨为 ctx 实体窗, IDF 权重取自 content_full 全语料共享权重。std 口径与均值口径 (canonical) 各自刻画不同的一阶/二阶矩, 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 std 与均值混进同一 over-identified Hansen J。作为 ctx 轨列, 行宇宙受 full-only 留篇门控约束; 当某 bank-year 仅 1 篇报道时 std 为 NaN (ddof=1 无自由度)。在实证使用中, 本列作为语调离散度而非水平进入模型, 常用作媒体意见分歧或语调不确定性的代理变量。它与均值口径互补而非替代: 同一银行年若均值接近中性但离散度很高, 说明媒体对该银行涉金科议题存在明显分歧, 这一信息是任何均值口径都无法捕捉的。研究者应把离散度列与均值列作为刻画不同矩的两个变量分别使用, 绝不允许把二者当作同一构念的替代而合并进同一过度识别方程。需注意单篇报道的银行年因缺乏自由度而取空值, 汇报时应说明有效样本规模; 实体窗轨进一步剔除银行无关段落, 使本列反映的分歧更聚焦于围绕该银行的报道语调。

## VAR: du_2022_idf_tone_std_full

【变体差分】
本列是「组内标准差 (std) × 全文 (full) 轨」的 IDF 加权 du_2022 语调离散度, 与 canonical 同轨、同分类范围, 唯聚合算子从均值换成样本标准差 (ddof=1)。它捕捉的是某 bank-year 内各篇报道加权语调的分散程度, 是对「媒体对该银行涉金科议题看法是否一致」的二阶矩刻画, 可作为语调不确定性 / 意见分歧的代理变量。与均值列 (du_2022_idf_tone_full) 是一阶/二阶矩的互补关系, 而非同一构念的替代: 均值答「平均多正/多负」, std 答「有多大分歧」。单位为非负离散度, 量纲口径与均值列不同, 禁止直接跨列相加比较水平。文本轨为 full (标题 prepend + 全文正文), IDF 权重取自 content_full 全语料共享权重。std_full 与 std_ctx、std_ss 三轨各自 just-identified 并排, 与均值 / vw / mw / hw 各口径各自并排, 互为稳健性、不分主次, 严禁把 std 与其它口径混进同一 over-identified Hansen J。作为 full 轨列, 行宇宙即 full-only 留篇集; 单篇 bank-year 时值为 NaN。在实证使用中, 本列是全文轨下的语调离散度, 是本家族刻画媒体意见分歧最直接的口径, 常作为语调不确定性的代理进入异质性或机制分析。它与均值口径回答的问题正交: 均值答平均语调偏正还是偏负, 离散度答各篇看法是否一致。二者作为一阶矩与二阶矩的互补变量分别使用, 绝不合并进同一过度识别方程。离散度对报道数量较敏感, 报道极少的银行年离散度估计噪声较大, 单篇时取空值; 因此汇报本列时应同时给出银行年的平均报道篇数, 以便读者判断离散度估计的稳定性。作为全文轨列, 其行宇宙即全篇留篇集, 是离散度族进入主分析的基准口径。

## VAR: du_2022_idf_tone_std_ss

【变体差分】
本列是「组内标准差 (std) × 同句 (ss) 轨」的 IDF 加权 du_2022 语调离散度, 把最严格语境轨与二阶矩聚合叠加。ss 轨只在银行∧金科同句共现处匹配情感词, 无共现时回退全文正文 (镜像 ctx 回退公理, 共享 n_articles 分母)。聚合算子为样本标准差 (ddof=1), 衡量最严语境下该 bank-year 内各篇加权语调的分歧程度。单位为非负离散度, 与均值列量纲口径不同, 禁止跨列相加比较水平。IDF 权重仍是 content_full 全语料共享权重, 仅词频匹配落在 ss 文本。该列是「最严语境 × 语调离散度」的组合稳健性测度, 与 std_full、std_ctx 三轨各自 just-identified 并排, 与均值及各加权口径各自并排, 互为稳健性、不分主次, 严禁把 std 与其它口径或不同轨混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束; 单篇 bank-year 或 ss 共现稀疏时值为 NaN, 早期试跑 T=2 上尤其常见, 属预期退化, 生产 T=19 恢复。在实证使用中, 本列是最严语境轨下的语调离散度, 是离散度族中收窄最深的一档, 通常置于稳健性附表, 用来确认意见分歧结论在只看银行与金科同句的口径下依然成立。由于同句共现稀疏, 该列有效样本最少, 单篇或零共现时取空值, 试跑语料上大量缺失属预期退化。它与全文轨、实体窗轨的离散度孪生并列, 只能分别估计或规格曲线切换, 绝不混入同一过度识别方程。研究者引用本列时应牢记其单位为非负离散度, 与均值列量纲口径不同, 严禁跨列相加或直接比较水平, 亦不得与均值口径当作同一构念替代。

## VAR: du_2022_idf_tone_tech_ctx

【变体差分】
本列是「技术类 (tech) 金融科技报道子集 × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调等权均值。相对 canonical, 它在分类子集 (仅 tech 类报道) 与文本轨 (ctx 实体窗) 两维上收窄。tech 子集限定为被判为「技术导向」的金融科技报道 (侧重底层技术、系统、算法能力, 与应用落地导向的 app 子集互补), 分母只计入该 bank-year 内 tech 类报道篇数。文本轨为 ctx, 只在目标银行实体上下文窗口内匹配情感词。IDF 权重取自 content_full 全语料共享权重, 词频匹配落在 tech 类报道的 ctx 文本上。该列衡量「银行在技术导向金科叙事中、实体窗内的加权语调」, 与 app 子集、与不分类全篇口径各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 tech 与 app 或全篇口径混进同一 over-identified Hansen J。作为 ctx 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列作为分类维度稳健性面板的一员进入回归, 用来检验主效应是否由技术导向的这一类金融科技叙事单独驱动。因分母限定为技术类报道篇数, 样本规模小于全篇口径, 点估计标准误偏大、弱识别风险偏高, 属分类稳健性检验的固有代价。与应用类子集及全篇口径共同解释同一结果时只能择一进入方程, 或分别估计后并列汇报, 绝不允许在同一工具变量集下过度识别。实体窗进一步剔除了与目标银行无关段落的语调噪声, 使本列更纯净地反映围绕该银行的技术类金科叙事情感, 供与应用类子集对照阅读。

## VAR: du_2022_idf_tone_tech_full

【变体差分】
本列是「技术类 (tech) 金融科技报道子集 × 全文 (full) 轨」的 IDF 加权 du_2022 语调等权均值。与 canonical 的唯一区分是分类子集: 只对被判技术导向的金融科技报道求 IDF 加权语调的 bank-year 等权均值, 分母为该 bank-year 内 tech 类报道篇数。文本轨为 full, 与 canonical 同轨。它衡量「银行在技术导向 (底层技术/系统/算法能力) 金科叙事中获得的加权语调」, 与 app 子集 (应用落地导向叙事的加权语调) 构成金融科技报道内部的两个正交侧面, 用以检验主结论是否由某一类金科叙事驱动。tech 子集口径、app 子集口径与不分类全篇口径各自 just-identified 并排, 互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J。IDF 权重取自 content_full 全语料共享权重, 词频匹配落在被判 tech 的报道 full 文本上。作为 full 轨列, 行宇宙即 full-only 留篇集, 是分类维度稳健性的存档轨。在实证使用中, 本列是技术类子集在全文轨下的分类稳健性存档口径, 与应用类子集对照使用, 用来判断主效应究竟来自底层技术能力叙事还是应用落地叙事, 这一区分对机制解读有直接价值。因分母为技术类报道篇数, 样本小于全篇口径, 标准误偏大。它与应用类子集、全篇口径三者只能并列汇报或分别估计, 绝不允许在同一工具变量集下过度识别。全文轨保留标题与正文全部语境, 样本相对充裕, 故本列常作为技术类子集下最稳健的基准存档口径, 供稳健性附表引用与跨子集对照。

## VAR: du_2022_idf_tone_tech_ss

【变体差分】
本列是「技术类 (tech) 金融科技报道子集 × 同句 (ss) 轨」的 IDF 加权 du_2022 语调等权均值, 同时收窄分类子集 (仅 tech 类) 与文本轨 (ss 同句共现轨)。ss 轨只在银行∧金科同句共现处匹配情感词, 无共现时回退全文正文 (镜像 ctx 回退公理)。分母只计入该 bank-year 内 tech 类报道篇数。IDF 权重取自 content_full 全语料共享权重, 词频匹配落在 tech 类报道的 ss 文本。该列把「最严语境 × 技术导向子集」两重收窄叠加, 用作双重收窄下的稳健性对照。它与 tech_full、tech_ctx 三轨各自 just-identified 并排, 也与 app 子集、与全篇口径并排, 互为稳健性、不分主次, 严禁把不同轨或不同分类子集混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束; 早期试跑 T=2 上 tech 子集与 ss 共现叠加后样本极稀, 可能大量 NaN, 属预期退化, 生产 T=19 恢复。在实证使用中, 本列是技术类子集与最严语境轨的双重收窄组合, 通常置于稳健性附表, 用来确认技术类叙事的语调结论在只看银行与金科同句的最挑剔口径下依然成立。由于技术类过滤叠加同句共现稀疏, 该列样本在全族中最小, 试跑语料上可能大量缺失, 属预期退化, 生产规模下恢复。研究者应结合有效观测数披露, 避免对少数格点过度外推。它与全文轨、实体窗轨的技术类孪生并列, 只能分别估计或规格曲线切换, 绝不混入同一过度识别方程, 亦不与应用类子集交叉进同一识别方程。

## VAR: du_2022_idf_tone_vw_ctx

【变体差分】
本列是「提及密度加权 (vw, value-weighted) × 实体窗 (ctx) 轨」的 IDF 加权 du_2022 语调。相对 canonical 的等权均值, vw 聚合按每篇报道对目标银行的提及密度赋权 (Tetlock 2007/2008 先分后合范式下的篇级权重), 使深度聚焦该银行的报道获得更大权重, 顺带提及的报道权重较小。计算为加权和除以权重和, 分子 = Σ(du_2022_idf_score × mention_density), 分母 = sum_mention_density。文本轨为 ctx 实体窗, IDF 权重取自 content_full 全语料共享权重。本列衡量「按银行提及密度加权后、实体窗内的语调」, 让真正围绕该银行展开的报道主导 bank-year 语调。它与 mw (媒体权威加权)、hw (跟风衰减加权)、canonical (等权) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同聚合权重混进同一 over-identified Hansen J。作为 ctx 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列作为聚合权重维度的一条稳健性支路进入回归, 用以检验主效应是否稳健于按提及密度加权的方案。等权、提及密度、媒体权威与跟风衰减四种权重各刻画不同的信息含量假设, 研究者应分别估计后并列汇报, 或在规格曲线中逐一切换, 而不得把它们塞进同一过度识别方程。提及密度加权让深度聚焦目标银行的报道主导语调, 顺带一提的报道权重较小; 当报道普遍只轻度提及该银行时, 该权重趋于均匀, 本列与无后缀口径差异缩小, 应结合提及密度分布一并披露。实体窗轨进一步剔除银行无关段落, 使本列在密度加权基础上更聚焦于围绕该银行的语调信号。

## VAR: du_2022_idf_tone_vw_full

【变体差分】
本列是「提及密度加权 (vw, value-weighted) × 全文 (full) 轨」的 IDF 加权 du_2022 语调, 与 canonical 同轨、同分类范围, 唯聚合权重从等权换成提及密度权重。其构念前提是: 一篇深度报道某银行的文章与一篇仅顺带一提的文章, 对该银行 bank-year 语调的贡献不应等同, 应按对该银行的提及密度加权 (Tetlock 2007 先分后合范式)。分子 = Σ(du_2022_idf_score × mention_density), 分母 = sum_mention_density。本列把词级 IDF 信息量加权 (文章内) 与篇级提及密度加权 (bank-year 内) 叠加, 是「让聚焦该银行的加权语调主导」构念的直接落地。它与 vw_ctx、vw_ss 三轨各自 just-identified 并排, 与 mw_full、hw_full、canonical 各自并排, 互为稳健性、不分主次, 严禁把不同聚合权重或不同轨混进同一 over-identified Hansen J。作为 full 轨列, 行宇宙即 full-only 留篇集。在实证使用中, 本列把文章内的词级信息量加权与银行年内的篇级提及密度加权两层修正叠加, 用来证明主效应是否由真正围绕该银行展开的深度报道而非顺带提及的边缘报道驱动。它与等权、媒体权威、跟风衰减三种口径并列, 只能分别估计或规格曲线切换, 绝不允许合并进同一过度识别方程。提及密度加权的效力取决于报道对目标银行聚焦程度的分布, 分布均匀时本列会向等权退化; 汇报本列时宜同时说明提及密度的离散情况, 以便读者判断加权结论的稳健区间。作为全文轨列, 本列保留完整语境, 是提及密度加权族进入主分析的基准存档口径。

## VAR: du_2022_idf_tone_vw_ss

【变体差分】
本列是「提及密度加权 (vw, value-weighted) × 同句 (ss) 轨」的 IDF 加权 du_2022 语调, 把最严格语境轨与提及密度加权聚合叠加。ss 轨只在银行∧金科同句共现处匹配情感词, 无共现时回退全文正文 (镜像 ctx 回退公理, 共享 n_articles 分母)。vw 聚合按篇级对目标银行的提及密度赋权, 分子 = Σ(du_2022_idf_score × mention_density), 分母 = sum_mention_density。IDF 权重仍是 content_full 全语料共享权重, 仅词频匹配落在 ss 文本。该列是「最严语境 × 提及密度主导」的双重收窄稳健性对照, 用于检验主结论是否稳健于「只看银行与金科同句、且让聚焦该银行的报道加权」这一组合口径。它与 vw_full、vw_ctx 三轨各自 just-identified 并排, 与 mw_ss、hw_ss、canonical_ss 各自并排, 互为稳健性、不分主次, 严禁把不同轨或不同聚合权重混进同一 over-identified Hansen J。作为 ss 轨 conditional-on-full 测度, 行宇宙受 full-only 留篇门控约束。在实证使用中, 本列是提及密度加权与最严语境轨的双重收窄组合, 通常置于稳健性附表, 用来确认在聚焦该银行的报道主导且仅看银行与金科同句的最挑剔口径下语调结论仍成立。由于同句共现稀疏叠加提及密度权重, 该列样本规模小、缺失较多, 试跑语料上尤甚, 属预期退化。研究者应结合有效观测数与提及密度分布一并披露, 避免过度外推。它与全文轨、实体窗轨的提及密度加权孪生并列, 只能分别估计或规格曲线切换, 绝不混入同一过度识别方程, 亦不与媒体权威、跟风衰减口径交叉进同一识别方程。

<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information? Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2022.11.006
Yao, K., Zheng, Z., & Liu, C. (2025). The colour of finance words in Chinese. Pacific-Basin Finance Journal. https://doi.org/10.1016/j.pacfin.2025.102854
<!-- rendered-citations:end -->
