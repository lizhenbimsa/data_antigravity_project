---
family_id: F282
columns:
- exc_you_2018_score_advonly_ctx
- exc_you_2018_score_advonly_full
- exc_you_2018_score_advonly_ss
unit: 情感倾向得分 (无量纲; 值域约 [-1, 1], 正为褒、负为贬)
formula: "exc_you_2018_score_advonly{track} = mean_{article ∈ 非停刊媒体} you_2018_score_advonly{track}; 文章级 you_2018_score_advonly = (pos_score - neg_score) / (pos_score + neg_score), 经规则状态机后仅启用转折规则 (adversative ×ADVERSATIVE_BOOST), 否定翻转与程度副词加权两条规则关闭"
producer: news_process/pipeline/panel/attention_media.py (exc_ 停刊稳健性聚合); 文章级底料 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (打分内核 _compute_sentiment_with_rules, rule-ablation advonly 变体)
upstream:
- 22_tone_words.parquet (you_2018_score_advonly_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- "config/tone_dicts.json (you_2018 词典: positive 1,425 / negative 1,583; positive∩negative 跨类重叠词两侧计数)"
- _is_ceased_media (attention_media 内 detect_defacto_cessation 派生的隐性停刊标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
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
本家族刻画的是「剔除隐性停刊媒体之后、以 you_2018 中文金融情感词典在仅转折语言学规则下重算」的银行–年度情感倾向。列名由三段语义叠合而成: 前缀 exc_ 是 excluding-ceased-media 的缩写, 与词典本身无关, 而是一道幸存者偏差 (survivorship bias) 稳健性处理; 中段 you_2018_score 指向底层词典与打分口径; 后缀 advonly 标记规则消融梯度里「仅转折」这一臂。exc_ 的动机是: 面板构建阶段先由 detect_defacto_cessation 判定哪些媒体来源在样本期内事实上停止发稿 (de-facto cessation, 隐性停刊而非正式注销), 再仅对来自「仍存活媒体」的文章聚合情感, 以检验主情感测度是否被存活媒体的选择性构成所污染。底层词典 you_2018 是本项目并置的六部中文金融情感词典之一, 正面词 1,425 个、负面词 1,583 个, 词表命名锚定 You、Zhang 与 Zhang (2018) 在 Review of Financial Studies 关于媒体「笔杆之力」如何被捕获的研究脉络, 用以在中文财经语料上抽取褒贬倾向。与 du_2022 词典不同, you_2018 口径不含政治正面词降权机制, 故本家族不涉及政治词权重梯度, 打分只由词典命中与语言学规则状态机共同决定。

【方法学与计算】
文章级底料由 tone_words.py 的 compute_dict_scores 经打分内核 _compute_sentiment_with_rules 产出。分词冻结在 jieba 0.42.1, 纯 CPU、无 LLM、无网络、零成本, 确定性完全来自 jieba 版本与词典文件的字节冻结。得分定义为 (pos_score − neg_score) / (pos_score + neg_score), 其中 pos_score、neg_score 是经规则状态机处理后落在正、负两侧的加权词次之和。规则状态机维护三个滚动状态: 否定窗口剩余 token 数、当前程度副词倍率、是否处于转折后从句区域; 遇句末标点重置三者 (从句级作用域, 遵循 Ding、Liu 与 Yu 2008 的转折效应限定), 遇转折词激活转折并重置否定与程度, 遇否定词开窗, 遇程度副词设倍率, 遇情感词则以 base × degree × negation × adversative 计分。advonly 变体在扫描时把 apply_negation 与 apply_degree 置 False、apply_adversative 置 True: 遇否定词仍识别否定 token 并维持窗口递减骨架但不翻转极性, 遇程度副词把倍率锁定为 1.0 但仍 continue 保留否定窗口 passthrough, 唯独在遇到转折词后的从句区域内对情感词施加 ×ADVERSATIVE_BOOST 放大。这条「只锁数值效应、不动 scoping」的铁律 (即关闭规则时仍保留该规则 token 的识别、continue 与窗口递减骨架, 不整段删检测) 保证 advonly 与其余六个消融变体逐字节可比, 否则删除检测会让被关规则的 token 落入末尾 else 分支触发窗口递减, 副作用缩短否定有效到达距离、污染语义。银行–年度聚合在 attention_media.py 完成: 先剔除 _is_ceased_media 为真的文章得到存活子集, 再按 target_bank×year 对文章级 you_2018_score_advonly{track} 取算术均值, 落列 exc_you_2018_score_advonly{track}; 停刊过滤只作用于聚合口径, 不改词典与规则本身, 零文章 bank-year 按契约保持 NaN 不做计数零填。

【文献定位】
词典命名脉络锚定 You、Zhang 与 Zhang (2018): 该文在 Review of Financial Studies 上研究媒体报道的信息含量如何被不同主体「捕获」, 是本项目 you_2018 词表所承接的媒体–情感研究传统的直接来源, 也是本家族在顶刊层面的方法学锚。转折规则的语言学基础可追溯至 Taboada 等 (2011) 的词典法情感分析框架, 该文系统处理了否定 (negation)、程度强化 (intensifier) 与转折 (contrastive/adversative) 结构如何调制词典极性, advonly 变体正是在该框架内单独激活转折通道、关闭否定与程度两通道的一次消融。Ma 等 (2025) 构建面向中国境内投资者的细粒度中文情感词典, 印证了在中文金融语境下持续精化领域词典与语言学规则的必要性, 为本项目多词典并置提供同期对照。Frankel 等 (2022) 在 Management Science 对比机器学习与词典法披露情感抽取, 论证两类方法各有偏误、宜互为稳健, 为本项目「词典 / LLM / BERT 三法并置」以及词典内部规则消融梯度并排读法提供方法学先例。需强调, 规则消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 各变体自归一化、高度共线且非可加分解 (audit MATH-1), 它们各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J 检验; 同理三轨 full/ctx/ss 亦各自 just-identified 并排、禁混同一 Hansen J。留篇门控口径与全项目一致, 采用 full-only (2026-06-29): 是否判为一篇银行金科报道只看 full 轨留篇集, ctx/ss 为 conditional-on-full 的稳健性轨, 行宇宙是 full 轨留篇集的子集。 就 advonly 所单独激活的转折通道而言, Venglařová 与 Matlach (2024) 实证功能词 (含连词一类的非内容词) 在文本类型判别上携带独立于内容词的信息量, 佐证转折/逆接结构作为一个与词典极性无关的语言维度值得被单独计量, 构成本臂「只留转折、关否定与程度」的构念前提; 惟原文任务为文本类型分类, 并不区分转折连词与其它功能词类, 语料非中文金融新闻, 亦不涉及银行—年度聚合, 故只在构念层与本族相通, 不构成 ADVERSATIVE_BOOST 具体取值的依据。样本口径一侧, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 为 exc_ 前缀先剔除隐性停刊媒体再聚合这一步提供现实动机; 该文系未经同行评审的工作论文, 其停刊判定取自外部事件数据认定的真实停刊, 而本项目的 ceased_set 是 detect_defacto_cessation 自语料内部推断的疑似退出覆盖保守代理, 仅作稳健性子样本而非识别冲击。方法论环境上, Oh (2024) 在整合 15 部原始情感词典与 43 部预处理词典构建 sentibank 时明确指出, 依赖专家词表的规则法能提供透明性, 而其应用困境在于资源碎片化与验证缺失; 这一背书支持本项目保留词典状态机语调轨并以六部中文词典并置的总体设计。须限定的是, 该资源覆盖英文社交媒体等体裁, 不含 you_2018 一类中文金融词典, 亦未实现否定/程度/转折三规则状态机, 与本族的规则消融稳健性检验无直接关系, 仅作构念层背景。
## VAR: exc_you_2018_score_advonly_ctx

【变体差分】
本列为 ctx 轨: 文章文本取标题 prepend 后的「实体窗口」上下文 content_ctx, 即在标题加银行实体命中位置附近窗口内截取的语段, 而非整篇正文。相对家族 full 轨参照口径, 差分维度是文本轨道而非规则或词典: 词典仍是 you_2018、规则仍是 advonly (仅转折)、聚合仍先剔除隐性停刊媒体。ctx 轨用以检验情感信号是否稳健于「只看银行邻近语境」的收窄视野, 缓解整篇正文里与目标银行无关段落带来的稀释: ctx 窗口只截取银行实体邻近语段, 因此对整篇里远离目标银行的段落所携带的褒贬噪声天然不敏感, 这是本轨相对 full 轨的核心识别价值。按 full-only 门控, ctx 轨为 conditional-on-full 测度, 行宇宙是 full 轨留篇集的子集, per-track 列照常在该子集上计算。本列与 exc_you_2018_score_advonly_full、exc_you_2018_score_advonly_ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁三轨混入同一 over-identified Hansen J。早期试跑 T=2 语料上 ctx 轨可能出现零方差退化属预期, 生产 T=19 正常。须区分本列与两类相邻测度: 一是同为 you_2018、同为 ctx 轨但不带 exc_ 前缀的全样本聚合列, 二者仅差在是否剔除隐性停刊媒体, 本列是前者的幸存者偏差稳健对照; 二是同轨的其它规则消融列 (如 negonly、negadv 的 exc_ 孪生), 它们与本列共用词典与文本轨、仅规则激活组合不同, 高度共线且非可加, 只能并排读作稳健性梯子而不可相加分解为各规则的边际贡献。

## VAR: exc_you_2018_score_advonly_full

【变体差分】
本列为 full 轨, 是家族内文本覆盖最广的口径: 文章文本取标题 prepend 加整篇正文 content_full。它承担留篇门控的 canonical 角色 (full-only, 2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨判定, ctx 与 ss 轨的行宇宙均为本轨留篇集的子集。词典为 you_2018, 规则为 advonly——仅激活转折 ×ADVERSATIVE_BOOST 放大、关闭否定翻转与程度副词加权, 用以隔离「转折结构单独贡献」在整篇文本上的净情感效应: full 轨承载最完整的正文信息, 因而是三轨中信噪结构最丰富、也最易被无关段落稀释的一轨, advonly 在此轨上只放大转折从句后的情感、不动否定与程度, 使转折结构对整篇净情感的单独贡献得以被隔离测量, 便于与 negadv (否定加转折) 等含转折的组合臂对照, 判断转折效应是否与否定效应存在交互。与家族其余列一致, 本列并非对全部文章聚合, 而是先剔除 _is_ceased_media 为真的隐性停刊媒体文章、再对存活子集按 target_bank×year 取均值, 因此它是主情感测度的幸存者偏差稳健对照, 用于验证结论不被存活媒体的选择性构成驱动; 本列与其非-exc_ 全样本孪生列系数的接近程度即是主结论不受媒体退出污染的直接证据。本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混入同一 over-identified Hansen J; 与规则消融梯度其余六臂 (raw/negonly/degonly/negdeg/negadv/degadv) 亦为并排稳健关系而非可加分解。

## VAR: exc_you_2018_score_advonly_ss

【变体差分】
本列为 ss 轨 (same-sentence 同句共现轨): 文章文本取标题 prepend 后、银行与金科词在同一句子内共现的 ±N 句窗 content_ss (句半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。相对 full/ctx, 差分维度是文本轨道——ss 轨最严格, 只保留银行与金融科技真正在同句同现的语境, 用以检验情感信号是否稳健于最窄的主题相关性判据。回退语义镜像 ctx 轨: 当文章无银行∧金科同句共现时, content_ss 优雅退化为整篇正文 body、ss_is_fallback 置真并与 full 轨共享 n_articles 分母; 若金科 AC 自动机为 None 则 *_is_fallback 全真、整体优雅降级。词典 you_2018 与 advonly 仅转折规则均与家族其余列一致; 聚合仍先剔除隐性停刊媒体再取 bank-year 均值。按 full-only 门控, ss 轨为 conditional-on-full 稳健性轨, 行宇宙是 full 轨留篇集的子集。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混同一 over-identified Hansen J。早期试跑 T=2 语料上 ss 轨常呈零方差退化属预期, 生产 T=19 恢复正常。相对 ctx 轨, ss 轨的判据更严: ctx 只要求银行实体命中即取邻近窗, ss 则要求银行与金融科技词在同一句子内共现, 因此在主题相关性上比 ctx 更保守, 也更易触发回退到全文的降级路径。这一层严格判据使本列成为「即便把相关性门槛拉到最紧、且剔除停刊媒体后」情感信号是否仍然成立的极端稳健检验; 若本列与 full/ctx 轨的 advonly 系数方向一致, 则可排除信号由弱相关篇章或存活媒体选择所驱动。本列与其非-exc_ 同句孪生列仅差停刊过滤, 与同轨其余规则消融列仅差规则激活组合, 三类差分互不交叉、各自作为正交的稳健性维度并排, 不得合并进同一 over-identified 估计。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
Oh, N. (2024). Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries. Proceedings of the International AAAI Conference on Web and Social Media, 18, 2003-2013. https://doi.org/10.1609/icwsm.v18i1.31443
<!-- rendered-citations:end -->
