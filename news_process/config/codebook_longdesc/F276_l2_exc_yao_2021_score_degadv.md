---
family_id: F276
columns:
- exc_yao_2021_score_degadv_ctx
- exc_yao_2021_score_degadv_full
- exc_yao_2021_score_degadv_ss
unit: 无量纲情感倾向得分 (bank-year 均值; 剔疑似停刊媒体子样本; 值域约 [-1, 1])
formula: "exc_yao_2021_score_degadv{track} = mean_文章 i 所属媒体的 _is_ceased_media_i 取 0 (即非疑似退出媒体) yao_2021_score_degadv{track}_i;  其中 yao_2021_score_degadv = (Σ pos − Σ neg) / (Σ pos + Σ neg), 计算时启用程度副词缩放与转折(adversative)规则、关闭否定翻转规则; yao_2021 词典正负两侧无政治正面词类, 故无 du_2022 式 0.5 政治词权重"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (停刊稳健性区段动态发现循环, exc_{src} = df_alive 上的 bank-year 均值; 文章层 score 由 pipeline/sentiment/tone_words.py 在 stage 22 产出)
upstream:
- "22_tone_words.parquet (article: yao_2021_score_degadv_full / _ctx / _ss)"
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- attention_media.detect_defacto_cessation (_is_ceased_media 停刊代理标记)
citations:
- doi: 10.1111/jofi.13498
  type: journal
  authors: Derrien, F., Krüger, P., Landier, A., & Yao, T.
  year: 2025
  title: "ESG news, future cash flows, and firm value"
  venue: The Journal of Finance
  vol: 80
  issue: 6
  pages_or_artno: 3499-3554
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.48550/arXiv.2411.13958
  type: arxiv
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2024
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: arXiv
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.1093/llc/fqae013"
  type: "journal"
  authors: "Venglařová, K., & Matlach, V."
  year: 2024
  title: "Beyond content: discriminatory power of function words in text type classification"
  venue: "Digital Scholarship in the Humanities"
  vol: "39"
  issue: "2"
  pages_or_artno: "765-789"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是"剔除疑似停刊媒体后、以 Yao 等 (2021) 金融领域中文情绪词典在程度加转折规则组合下计得的银行—年度词典情感倾向"。它把三个正交的设计维度叠在同一条列名上: 词典底料取自 Yao 等 (2021) 的金融领域中文情绪词典 (代码键 yao_2021), 该词典由年报语料与社交媒体语料两支合成, 正面词为年报正面∪社媒正面去重后约 3,844 词、负面词约 2,074 词, 与姜富伟等 (2021)、Bian 等 (2021)、Du 等 (2022)、You 等 (2018) 及 Loughran-McDonald 中文主译本并列为本项目六部固定情感词典之一; 语言学规则取 degadv 消融组合, 即启用程度副词缩放与转折 (adversative) 规则、关闭否定翻转规则; 样本口径取 exc 停刊稳健性子样本, 即在被停刊代理标记为疑似退出话题覆盖的媒体来源剔除之后的报道集合上聚合。三个维度共同回答一个稳健性问题: 当我们既不让否定翻转规则参与打分、又把疑似停刊媒体的报道排除在样本外时, 银行层面的词典情感均值是否仍与主口径给出定性一致的结论。它并不是一个新的构念, 而是主情感构念在"规则消融梯子 × 停刊样本梯子"这两条稳健性轴交叉处的一个并排臂。需强调 yao_2021 词典两侧不含政治正面词类, 因此本家族不涉及 du_2022 特有的 0.5 政治词权重取舍, 这也是与 exc_du_2022 同结构家族在打分口径上的唯一实质差异。

【方法学与计算】
计算分两层。文章层由 pipeline/sentiment/tone_words.py 在 stage 22 完成: 对每篇报道的三轨文本 (content_full 标题加正文、content_ctx 标题加实体窗、content_ss 标题加银行与金科同句窗) 分别扫描 yao_2021 词典命中词, 得到正词与负词的计数, 再按 degadv 规则打分——遇程度副词按 HowNet 六级强度体系缩放邻近情感词幅度、遇转折连词按 ADVERSATIVE_BOOST 提升转折后分句权重, 但不执行否定词翻转 (故 degadv 恰等于全规则口径减去否定这一条规则)。文章得分自归一化为 (Σ正 − Σ负)/(Σ正 + Σ负), 落在约 [-1, 1] 区间。面板层由 pipeline/panel/attention_media.py 的 compute_media_heterogeneity 在停刊稳健性区段完成: 先由 detect_defacto_cessation 依覆盖退出信号 (媒体在银行金科话题上的首末出现年跨度) 给每条报道打 _is_ceased_media 标记, 再在 _is_ceased_media 等于 0 的存活子样本 df_alive 上按 (target_bank, year) 对文章层 yao_2021_score_degadv{track} 取算术均值, 前缀 exc_ 写出 bank-year 列。停刊比例本身另存为 ceased_media_frac、剔停后文章数另存为 n_articles_exc; 本情感列按契约在零文章格保持缺失而不零填。由于每个消融变体各自 self-normalize (分母随启用规则集变化), 相邻消融级差并非某条规则的纯边际贡献, 只作 ablation 稳健性对照; 披露时应报各级相关系数与逐级变号占比, 论文表述落在"定性不变", 而非声称某一消融组合更优。

【文献定位】
词典法的方法学定位可放在近年金融文本测度的两条线索上。一是词典底料的持续演进: Ma 等 (2025) 构建面向中国国内投资者的细粒度中文情感词典 CN-FSD, 代表中文金融词典法在细粒度与领域特异方向的最新进展, 佐证"专门词典优于英文词典直译"这一路线在中文金融文本上的持续有效性; Barbaglia 等 (2024) 的经济文本词典法工作则在跨语种层面重申词典命中加规则修正这一透明、可复现路线的价值。二是测量效度的独立评估: van Atteveldt 等 (2021) 系统比较人工标注、众包、词典法与机器学习在情感分析上的效度, 指出不同方法在难例上存在系统差异, 这正是本项目坚持"词典法 × 大模型法 × BERT 法三法互为稳健性"的实证依据, 也支持用规则消融梯子检验结论对具体规则取舍的敏感性。顶刊锚方面, Derrien 等 (2025) 发表于 The Journal of Finance 的研究以 ESG 新闻的文本情感度量为核心, 论证从新闻文本抽取的情感信号确能预测未来现金流并进入公司估值, 为"以词典法从媒体文本构造银行情感面板"这一测量策略提供了顶刊层面的构念与识别参照; Du 等 (2022) 发表于 Review of Finance 的中文金融情感词典工作则从语言与领域特异性角度论证中文金融文本需专门词典, 是本项目六部词典整体设计 (含 yao_2021) 的方法学共同底座, 尽管其政治正面词加权设计仅对 du_2022 生效、对本家族的 yao_2021 底料不适用。 就本族三个设计维度而言, 近期文献分别提供了可锚的支点。规则维度上, Naldi 与 Petroni (2023) 以人工构造测试集专门评估词典法情感工具的否定检测与处理表现, 实证各工具差异显著, 佐证否定是词典法内部一个可被单独测量、单独失效的模块, 从而使 degadv 这条「全规则口径减去否定」的臂具备独立解读价值; 惟该文语料为英文通用领域, 所度量者为否定检测准确率, 本族并不评测准确率, 只把否定的开与关物化为并排稳健性臂。转折通道方面, Venglařová 与 Matlach (2024) 实证功能词 (含连词一类的非内容词) 在文本类型判别上具有独立于内容词的信息量, 支持把转折结构视为一个值得单独计量的语言维度; 但其任务是文本类型分类, 并不区分转折连词与其它功能词类, 语料亦非中文金融新闻、不涉及银行—年度聚合, 故只在构念层与本族的 adversative 规则相通, 不构成 ADVERSATIVE_BOOST 取值的依据。样本口径方面, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 为 exc_ 前缀「剔除疑似退出覆盖媒体后再作 bank-year 聚合」这一环节提供现实动机; 该文为工作论文尚未经同行评审, 其停刊判定来自外部事件数据所记录的真实停刊事件, 而本项目的 ceased_set 是由 detect_defacto_cessation 自语料内部推断的疑似退出覆盖保守代理, 并非严格停刊事实, 且仅作稳健性子样本, 不用于识别冲击。
## VAR: exc_yao_2021_score_degadv_ctx

【变体差分】
本列取 ctx 轨。ctx 轨文本为标题 prepend 后的实体上下文窗 (content_ctx): 在正文中围绕目标银行实体的邻近窗口截取, 相较 full 轨全文更聚焦于与银行直接相关的语句, 削弱全文中与本行无关段落对词典命中的稀释。三轨 (full/ctx/ss) 就本家族而言各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J; ctx 轨在此作为 full 轨的稳健性对照, 检验"把打分文本从整篇收窄到实体窗"是否改变剔停后 degadv 口径下的银行情感定性结论。词典 (yao_2021)、规则组合 (degadv: 程度加转折、无否定)、样本口径 (剔疑似停刊媒体的存活子样本 df_alive 上按 bank-year 取均值) 三项与家族其余两列完全一致, 唯一区别是文章层打分所用文本轨为 content_ctx。分母口径为该 bank-year 内存活且 ctx 轨可打分的报道数; 无实体窗共现的报道其 ctx 文本按三轨回退语义处理, 详见文章层三轨物化契约。degadv 消融组合在 ctx 轨上的语义与 full 轨完全同构: 关闭否定翻转意味着句中出现"不""未""没有"等否定词时不再对邻近情感词做符号反转, 仅保留程度副词缩放与转折规则, 因此本列相对启用全规则的主口径差在否定这一条规则的取舍, 相对启用否定的 negadv/negdeg 等兄弟消融变体差在文本轨与规则集的双重选择。把这一差分放在实体窗轨上并叠加剔停样本, 目的是检验"否定规则关停对情感均值的扰动"是否会因文本聚焦程度或样本存活性而放大或衰减; 若三轨在此均给出与主口径高度相关、变号占比低的结果, 则可在论文稳健性叙事中如实陈述结论对否定规则与媒体存活口径均不敏感。

## VAR: exc_yao_2021_score_degadv_full

【变体差分】
本列取 full 轨, 是本家族在文本轨维度上的基准轨。full 轨文本为标题 prepend 后的全文正文 (content_full): 标题加整篇报道正文, 词典命中扫描覆盖面最广, 与主口径留篇门控 (full-only, 2026-06-29) 所依据的文本轨一致——即一篇报道是否算作银行金科报道由 full 轨判定, ctx/ss 为 conditional-on-full 的稳健轨。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。相较家族内 ctx/ss 两列, 本列唯一差别是文章层 yao_2021_score_degadv 在 content_full 上计算; 词典底料 (yao_2021)、degadv 规则组合 (启用程度副词缩放与转折、关闭否定翻转)、以及在 _is_ceased_media 等于 0 的存活子样本上按 (target_bank, year) 取算术均值这一停刊稳健性口径, 均与家族其余两列同构。它回答的稳健性问题是: 在最广的全文文本轨上, 既关掉否定翻转规则、又剔掉疑似停刊媒体, 银行情感均值是否仍与主口径一致。作为家族内的基准文本轨, 本列在实证使用中通常与剔停前的全样本 degadv full 列、以及启用否定的 full 轨消融变体成对比较: 前者隔离出"剔停"这一样本口径的净效应, 后者隔离出"关否定"这一规则口径的净效应, 二者叠加即本列的联合稳健性含义。由于 degadv 各变体自归一化、否定与程度作用于同一批含交互的词, 相邻消融级差不可解读为某规则的可加边际贡献, 只能作为 ablation 对照; 本列在披露时应与家族其余消融臂一并报相关系数矩阵与逐级变号占比, 论文表述以"定性结论不变"为落点。

## VAR: exc_yao_2021_score_degadv_ss

【变体差分】
本列取 ss 轨 (同句共现轨)。ss 轨文本为标题 prepend 后、银行实体与金融科技词在同一句子正负 N 句窗内共现的语句 (content_ss), 是三轨中最严格、最聚焦银行金科直接关联的文本口径。其回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置真, 与 ctx 轨的回退结构一致 (以 CLAUDE.md 三轨回退口径为准)。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J; ss 轨作为最严口径的稳健性并排臂, 检验"把打分文本收到银行金科同句窗"是否改变剔停后 degadv 口径下的定性结论。词典 (yao_2021)、规则组合 (degadv: 程度加转折、无否定)、以及剔疑似停刊媒体后在存活子样本上按 bank-year 取均值的停刊稳健性口径, 均与家族其余两列一致, 唯一区别为文章层打分文本轨取 content_ss。在早期试跑盘上 T=2 样本上, 同句共现较稀疏时 ss 轨可能出现较多回退, 属预期退化, 生产 T=19 语料上恢复正常密度。ss 轨与 ctx 轨的核心区别在于共现判据的严格度: ctx 只要求银行实体落入邻近窗, ss 进一步要求银行与金科词落入同一句正负 N 句窗, 故 ss 文本更短、更纯, 词典命中密度更高但样本回退风险也更大。把 degadv 规则组合 (关否定、留程度与转折) 与剔停样本口径叠加在这条最严文本轨上, 是三轨稳健性梯子的一端: 若 full、ctx、ss 三列在剔停子样本上对 degadv 口径给出一致的银行情感排序与相近的均值水平, 则可论证主结论既不依赖具体文本聚焦口径, 也不依赖否定规则是否启用, 更不依赖疑似停刊媒体是否在样本内。因此本列的价值不在于单独进入某个回归的右手边, 而在于与家族其余两轨、以及规则消融与停刊两条梯子上的相邻臂并排, 共同支撑"测量选择不驱动结论"的稳健性叙事。

<!-- rendered-citations:begin -->
Derrien, F., Krüger, P., Landier, A., & Yao, T. (2025). ESG news, future cash flows, and firm value. The Journal of Finance, 80(6), 3499-3554. https://doi.org/10.1111/jofi.13498
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2024). Sentiment analysis of economic text: A lexicon-based approach. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2411.13958
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
