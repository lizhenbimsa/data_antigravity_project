---
family_id: F243
columns:
- exc_du_2022_score_degadv_ctx
- exc_du_2022_score_degadv_full
- exc_du_2022_score_degadv_ss
unit: 无量纲情感倾向得分 (bank-year 均值; 剔疑似停刊媒体子样本; 值域约 [-1, 1])
formula: "exc_du_2022_score_degadv{track} = mean_文章 i 所属媒体的 _is_ceased_media_i 取 0 (即非疑似退出媒体) du_2022_score_degadv{track}_i;  其中 du_2022_score_degadv = (Σ pos_weighted − Σ neg) / (Σ pos_weighted + Σ neg), 计算时启用程度副词缩放与转折(adversative)规则、关闭否定翻转规则; pos_weighted = pos_ordinary + 0.5 * pos_political (du_2022 生产口径政治词权重)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (停刊稳健性 (C.4) 动态发现循环, exc_{src} = df_alive 上的 bank-year 均值)
upstream:
- "22_tone_words.parquet (article: du_2022_score_degadv_full / _ctx / _ss)"
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- attention_media.detect_defacto_cessation (_is_ceased_media 停刊代理标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
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
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是"剔除疑似停刊媒体后、以 Du et al. (2022) 中文金融情感词典在程度加转折规则组合下计得的银行—年度词典情感倾向"。它把三个正交的设计维度叠在一条列名上: 词典底料取自 Du et al. (2022) 的中文金融情感词典 (du_2022); 语言学规则取 degadv 消融组合 (启用程度副词缩放与转折规则、关闭否定翻转); 样本口径取 exc 停刊稳健性子样本 (剔除被停刊代理标记为疑似退出覆盖的媒体来源后的报道集合)。三个维度共同回答一个稳健性问题: 当我们既不让否定翻转规则参与打分、又把疑似停刊媒体的报道排除在外时, 银行层面的词典情感均值是否与主口径给出一致的定性结论。它不是一个新的构念, 而是主情感构念在"规则消融梯子 × 停刊样本梯子"两条稳健性轴交叉处的一个并排臂。

【方法学与计算】
计算分两层。文章层由 pipeline/sentiment/tone_words.py 在 stage 22 完成: 对每篇报道的三轨文本 (content_full 标题加正文、content_ctx 标题加实体窗、content_ss 标题加银行与金科同句窗) 分别扫描 du_2022 词典命中词, 得到正词与负词的加权计数, 其中政治正面词以 0.5 权重并入正侧 (du_2022 生产口径), 再按 degadv 规则打分: 遇程度副词按其强度缩放邻近情感词幅度、遇转折连词按转折规则调整前后分句权重, 但不执行否定词翻转 (故 degadv 恰等于全规则口径减去否定这一条规则)。文章得分归一化为 (加权正 − 负)/(加权正 + 负), 落在约 [-1, 1] 区间。面板层由 pipeline/panel/attention_media.py 的 compute_media_heterogeneity 在停刊稳健性区段完成: 先由 detect_defacto_cessation 依覆盖退出信号给每条报道打 _is_ceased_media 标记, 再在 _is_ceased_media 等于 0 的存活子样本 df_alive 上按 (target_bank, year) 对文章层 du_2022_score_degadv{track} 取算术均值, 前缀 exc_ 写出 bank-year 列。停刊比例本身另存为 ceased_media_frac、剔停后文章数另存为 n_articles_exc; 本情感列按契约在零文章格保持缺失而不零填。因每个消融变体各自 self-normalize (分母随启用规则集变化), 相邻消融级差并非某条规则的纯边际贡献, 只作 ablation 稳健性对照, 披露时报各级相关系数与逐级变号占比、论文表述"定性不变"。

【文献定位】
词典底料的权威锚点是 Du et al. (2022) 发表于 Review of Finance 的中文金融情感词典, 该文以语言与领域特异性为核心论证中文金融文本需要专门词典而非英文词典直译, 并单列政治正面词一类、指出其情感信号弱于普通正面词——这正是本口径对政治正面词赋 0.5 权重的依据。词典构造方法学上, Ma et al. (2025) 的 CN-FSD 细粒度中文投资者情感词典与 Sun et al. (2025) 融合词典知识与中性特征的金融情感分析工作, 代表了中文金融词典法的近期演进方向, 佐证词典命中加规则修正这一路线的持续有效性; Hamilton et al. (2016) 从无标注语料诱导领域情感词典的方法则为"领域特异词典优于通用词典"提供了跨语种的方法学支撑。停刊剔除这一样本设计的因果动机取自 Heese et al. (2022) 发表于 Journal of Financial Economics 的研究: 地方报纸关停会造成地方监督真空、放大企业不当行为, 故媒体来源退出覆盖会给情感面板引入幸存者偏差、污染以媒体为基础的工具变量; 把疑似退出媒体保守剔出样本、再验主结论稳定性, 正是对这一偏差的直接防御。 这一防御的现实必要性另有近期实证佐证: Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 发现报道供给退出会改变本地股票的交易行为, 表明媒体退出是携带经济后果的真实样本组成变化, 而非可当作随机缺失处理的噪声; 惟其停刊判定取自外部事件数据、被解释变量为交易活动, 本项目的排除集则是自语料内部推断的疑似覆盖退出代理, 仅作稳健性子样本之用, 且该文为未经同行评审的工作论文。就本口径刻意关停的否定翻转规则而言, Naldi 与 Petroni (2023) 以人工构造测试集专门评估词典法情感工具的否定检测与处理能力, 实证各工具表现差异显著, 支持把否定视为词典法内部可被单独测量、单独失效的模块, 因而值得单列为一条可独立开关的消融臂; 其语境为英文通用领域的工具准确率评测, 本项目则不作否定检测准确率评估, 只把否定开关作为中文金融新闻银行-年度测度的一条并排稳健性臂。本口径保留的转折规则可参照 Venglařová 与 Matlach (2024): 该文实证功能词 (含连词一类非内容词) 在文本类型判别上具有独立信息量, 佐证转折连词并非可忽略的虚词, 值得在计分内核中单独建模; 惟原文任务为文本类型分类、并不区分转折连词与其他功能词类, 语料亦非中文金融新闻, 故其支撑仅止于「转折类功能词自带独立信息」这一构念层面, 不涉及规则级消融设计本身。上述三条锚点分别落在样本口径轴与规则轴上, 与本列 degadv 组合的其余并排臂一样只作定性对照, 各自 just-identified 并排, 不进入同一 over-identified Hansen J。
## VAR: exc_du_2022_score_degadv_ctx

【变体差分】
本列取 ctx 轨。ctx 轨文本为标题 prepend 后的实体上下文窗 (content_ctx): 在正文中围绕目标银行实体的邻近窗口截取, 相较 full 轨全文更聚焦于与银行直接相关的语句, 削弱全文中与本行无关段落对词典命中的稀释。三轨 (full/ctx/ss) 就本家族而言各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J; ctx 轨在此作为 full 轨的稳健性对照, 检验"把打分文本从整篇收窄到实体窗"是否改变剔停后 degadv 口径下的银行情感定性结论。词典 (du_2022)、规则组合 (degadv: 程度加转折、无否定)、样本口径 (剔疑似停刊媒体的存活子样本 df_alive 上按 bank-year 取均值)、政治词 0.5 权重四项与家族其余两列完全一致, 唯一区别是文章层打分所用文本轨为 content_ctx。分母口径为该 bank-year 内存活且 ctx 轨可打分的报道数; 无实体窗共现的报道其 ctx 文本按三轨回退语义处理, 详见文章层三轨物化契约。需要强调的是, degadv 消融组合在 ctx 轨上的语义与 full 轨完全同构: 关闭否定翻转意味着句中出现"不""未""没有"等否定词时不再对邻近情感词做符号反转, 仅保留程度副词缩放与转折规则的作用, 因此本列相对启用全规则的主口径, 差在否定这一条规则的取舍, 相对启用否定的 negadv/negdeg 等兄弟消融变体, 差在文本轨与规则集的双重选择。把这一差分放在实体窗轨上并叠加剔停样本, 目的是检验"否定规则关停对情感均值的扰动"是否会因文本聚焦程度或样本存活性而放大或衰减; 若三轨在此均给出与主口径高度相关、变号占比低的结果, 则可在论文稳健性叙事中如实陈述结论对否定规则与媒体存活口径均不敏感。

## VAR: exc_du_2022_score_degadv_full

【变体差分】
本列取 full 轨, 是本家族在文本轨维度上的基准轨。full 轨文本为标题 prepend 后的全文正文 (content_full): 标题加整篇报道正文, 词典命中扫描覆盖面最广, 与主口径留篇门控 (full-only, 2026-06-29) 所依据的文本轨一致——即一篇报道是否算作银行金科报道由 full 轨判定, ctx/ss 为 conditional-on-full 的稳健轨。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。相较家族内 ctx/ss 两列, 本列唯一差别是文章层 du_2022_score_degadv 在 content_full 上计算; 词典底料、degadv 规则组合 (启用程度副词缩放与转折、关闭否定翻转)、政治正面词 0.5 权重、以及在 _is_ceased_media 等于 0 的存活子样本上按 (target_bank, year) 取算术均值这一停刊稳健性口径, 均与家族其余两列同构。它回答的稳健性问题是: 在最广的全文文本轨上, 既关掉否定翻转规则、又剔掉疑似停刊媒体, 银行情感均值是否仍与主口径一致。作为家族内的基准文本轨, 本列在实证使用中通常与剔停前的全样本 degadv full 列、以及启用否定的 full 轨消融变体成对比较: 前者隔离出"剔停"这一样本口径的净效应, 后者隔离出"关否定"这一规则口径的净效应, 二者叠加即本列的联合稳健性含义。由于 degadv 各变体自归一化、否定与程度作用于同一批含交互的词, 相邻消融级差不可解读为某规则的可加边际贡献, 只能作为 ablation 对照; 本列在披露时应与家族其余消融臂一并报相关系数矩阵与逐级变号占比, 论文表述以"定性结论不变"为落点, 而非声称某一消融组合更优。

## VAR: exc_du_2022_score_degadv_ss

【变体差分】
本列取 ss 轨 (同句共现轨)。ss 轨文本为标题 prepend 后、银行实体与金融科技词在同一句子正负 N 句窗内共现的语句 (content_ss), 是三轨中最严格、最聚焦银行金科直接关联的文本口径。其回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置真, 与 ctx 轨的回退结构一致 (以 CLAUDE.md 三轨回退口径为准)。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J; ss 轨作为最严口径的稳健性并排臂, 检验"把打分文本收到银行金科同句窗"是否改变剔停后 degadv 口径下的定性结论。词典 (du_2022)、规则组合 (degadv)、政治词 0.5 权重、以及剔疑似停刊媒体后在存活子样本上按 bank-year 取均值的停刊稳健性口径, 均与家族其余两列一致, 唯一区别为文章层打分文本轨取 content_ss。在盘上 T=2 开发样本上, 同句共现较稀疏时 ss 轨可能出现较多回退, 属预期退化, 生产 T=19 语料上恢复正常密度。ss 轨与 ctx 轨的核心区别在于共现判据的严格度: ctx 只要求银行实体落入邻近窗, ss 进一步要求银行与金科词落入同一句正负 N 句窗, 故 ss 文本更短、更纯, 词典命中密度更高但样本回退风险也更大。把 degadv 规则组合 (关否定、留程度与转折) 与剔停样本口径叠加在这条最严文本轨上, 是三轨稳健性梯子的一端: 若 full、ctx、ss 三列在剔停子样本上对 degadv 口径给出一致的银行情感排序与相近的均值水平, 则可论证主结论既不依赖具体文本聚焦口径, 也不依赖否定规则是否启用, 更不依赖疑似停刊媒体是否在样本内。因此本列的价值不在于单独进入某个回归的右手边, 而在于与家族其余两轨、以及规则消融与停刊两条梯子上的相邻臂并排, 共同支撑"测量选择不驱动结论"的稳健性叙事。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
<!-- rendered-citations:end -->
