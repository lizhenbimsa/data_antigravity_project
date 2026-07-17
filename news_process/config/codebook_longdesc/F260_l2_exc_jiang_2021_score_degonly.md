---
family_id: F260
novelty_exempt_rationale: "exc_/degonly 双重消融衍生变体家族(停刊稳健性剔除子集×规则消融臂), 测度定义依据母族词典(姜富伟等2021)及规则消融梯度设计, 非独立新构念, 无需追新文献。"
columns:
- exc_jiang_2021_score_degonly_ctx
- exc_jiang_2021_score_degonly_full
- exc_jiang_2021_score_degonly_ss
unit: 情感倾向分值 (无量纲, 自归一化 ∈ [−1, 1]; bank-year 级为该 bank-year 存活媒体子集内文章级得分的算术均值)
formula: "exc_jiang_2021_score_degonly_{trk} = mean_媒体 a 的 _is_ceased_media(a) 取 0 (即非疑似退出媒体) jiang_2021_score_degonly_{trk}(a); 文章级 jiang_2021_score_degonly = norm_score, 由 _compute_sentiment_with_rules(tokens, jiang_2021_dict, apply_negation=False, apply_degree=True, apply_adversative=False) 得, norm_score = Σ_signed / Σ|base| ∈ [−1,1]; trk ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性聚合 C.4; 文章级得分源自 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores 的 _RULE_ABLATION_VARIANTS)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_score_degonly_{full,ctx,ss})
- 40_panel_export_main (attention_media 停刊代理检测产 _is_ceased_media 掩码)
citations:
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
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
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
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
本家族测度一条"双重稳健性"复合语调指标: 在姜富伟等 (2021) 中文财经媒体情绪词典 (jiang_2021, 本流水线六部词典之一) 基础上, 一方面剥离否定与转折两条语言学规则、仅保留程度副词加权 (degonly 消融变体), 另一方面把 bank-year 聚合的样本框收缩到"疑似退出覆盖" (停刊代理) 媒体之外的存活媒体子集 (exc 前缀)。三个列 exc_jiang_2021_score_degonly_{full, ctx, ss} 分别对应三条文本轨。词典本身来自姜富伟等 (2021) 发表于经济学(季刊)的工作: 该文用机器学习从中文财经媒体文本抽取带情感极性的词表, 并证明媒体文本情绪对股票横截面回报有预测力, 与英文语境下 Jiang 等 (2019) 关于经理人情绪 (manager sentiment) 可预测股票回报的证据一脉相承, 为把媒体语调作为定价相关信息提供了构念合法性。

【方法学与计算】
文章级得分在 stage 22 (tone_words) 计算。分词后调用 _compute_sentiment_with_rules, 对命中 jiang_2021 词表的极性词逐一累加带符号强度, 再以其绝对值之和归一化, 得 norm_score = Σ_signed / Σ|base| ∈ [−1, 1], 属幅度口径 (amplitude) 而非纯词频计数口径。degonly 变体锁定规则开关 (apply_negation=False, apply_degree=True, apply_adversative=False), 即只施加程度副词的六级强度加权、不做否定翻转、不做转折 boost, 是规则消融梯度 _RULE_ABLATION_VARIANTS 中 (raw, negonly, degonly, advonly, negdeg, negadv, degadv) 七个非-full 组合之一; 全语言学规则叠加后的 full 组合另行物化为主列 jiang_2021_score, 不落本家族。valence-shifter 谱系的方法学依据见 Taboada 等 (2011) 与其后续文献: 程度副词、否定、转折被视为改变基础极性强度或方向的三类独立算子, 逐一开关即构成对语调测度稳健性的消融检验。bank-year 聚合在 stage 40 的 attention_media 停刊稳健性块 (C.4) 完成: 先由 detect_defacto_cessation 以"话题覆盖退出"为停刊的保守代理产 _is_ceased_media 掩码 (须强调这是疑似退出覆盖而非经证实的报纸停刊), 再对 _is_ceased_media==0 的存活媒体文章按 (target_bank, year) 分组求文章级得分均值, 冠以 exc_ 前缀。停刊稳健性口径的经济动机是幸存者偏差 (survivorship bias): 若覆盖某话题的媒体陆续退出, 语调指标会向存活媒体倾斜并可能污染下游 Bartik 类工具变量, 故构造剔除疑似退出媒体后的替代指标, 供 Stata 端做系数稳定性对照。exc_* 情感类列在零文章 bank-year 按契约保持 NaN, 不做计数式零填。

【文献定位】
词典法语调测度的效度须放在与人工标注、机器学习法的三方比较中理解: van Atteveldt 等 (2021) 系统比较人工标注、众包、词典与机器学习, 指出词典法在细粒度极性上弱于监督学习但具备完全可复现、零训练成本与跨样本词表固定的优点, 正是本流水线保留多部词典并逐条做规则消融的理由。Du 等 (2022) 构建中文财经情感词典并讨论语言与领域特异性, 与 jiang_2021 同属中文财经语料的词表工程谱系, 二者互为构念替代。Cao 等 (2023) 关于"机器在听时如何说话"的证据提示: 当文本同时被算法读取时, 披露语调本身会被策略性调整, 这为把媒体 (第三方) 语调而非公司自述语调作为信号来源提供了额外辩护。方法学定位上, degonly 与同家族其余六个规则消融臂各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同规则臂混入同一 over-identified Hansen J; 三条文本轨 (full/ctx/ss) 同理各自 just-identified 并排、禁混同一 over-identified Hansen J。留篇门控采 full-only 口径 (2026-06-29): 是否算作一篇银行金科报道只看 full 轨的 llm_verified 判定, ctx/ss 为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。 就本臂刻意关闭否定翻转、仅保留程度副词规则这一设定, Naldi 与 Petroni (2023) 提出以人工构造测试集评估词典法情感工具的否定检测与处理能力, 并实证发现各工具在否定处理上表现差异显著, 印证否定是词典法内部可被单独测量、单独失效的模块, 从而使 degonly 这一臂具备明确的方法学意涵; 惟其评测语料为英文通用领域、度量对象是否定检测准确率, 本项目并不评测准确率, 只把规则开关的后果并排呈现为互为稳健性的臂。样本层面, Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 为本族在剔除 _is_ceased_media 标记媒体后重算存活子样本均值提供了现实动机; 但其停刊判定来自外部事件数据、被解释变量为本地股票交易活动, 而本族的标记只是自语料内部推断的疑似退出覆盖保守代理, 用途限于稳健性子样本而非识别冲击, 且该文为未经同行评审的工作论文。
## VAR: exc_jiang_2021_score_degonly_ctx

【变体差分】
本列取三轨中的 ctx (context) 轨: 文章级 jiang_2021_score_degonly 在 content_ctx 上计算, 该文本 = 标题 prepend + 实体上下文窗口 (目标银行实体前后若干句的截取), 由 stage 14 ctx_materializer 物化。相较 full 轨, ctx 只保留银行实体邻域的句子, 目的是把语调测量聚焦到与目标银行直接相关的语境、削弱全文其余无关段落的稀释。规则口径与家族一致: 仅程度副词加权 (degonly), 不做否定翻转、不做转折 boost。样本框口径亦一致: bank-year 聚合仅纳入 _is_ceased_media==0 的存活媒体文章 (exc 停刊稳健性), 对疑似退出覆盖的媒体保守剔除。定位上, ctx 轨与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。按 full-only 留篇门控 (2026-06-29), 本 ctx 列是 conditional-on-full 的稳健性轨, 其行宇宙为 full 留篇集的子集; 若某 bank-year 存活媒体文章的 content_ctx 全部退化为空或该轨缺列, 则按守卫优雅跳过, 该 bank-year 的本列保持 NaN 而不连带零填。ctx 与 ss 的差异在于窗口判据: ctx 取实体上下文窗口, ss 取银行∧金科同句共现窗口, 二者判据不同, 不可互相复用。就与家族 canonical 的差分而言, 本列同时在两个维度上偏离主列 jiang_2021_score: 其一是文本轨从 full 收窄为 ctx, 其二是聚合样本框从全样本收窄为存活媒体子集; 前者影响的是"读哪些句子", 后者影响的是"聚合哪些文章", 两条收窄相互正交, 不可混谈。degonly 相对 full 规则组合的差异则是"不翻否定、不加转折、只留程度加权", 因此当一段银行邻域文本含较多否定式表述时, 本列与 full 规则臂会出现方向或强度差异, 这正是消融梯度用以检验主语调稳健性的信息来源。

## VAR: exc_jiang_2021_score_degonly_full

【变体差分】
本列取三轨中的 full 轨, 是家族内文本覆盖最完整的一轨: 文章级 jiang_2021_score_degonly 在 content_full 上计算, 该文本 = 标题 prepend + 全文正文 (原始内容列不动, 标题以 prepend_title 方式并入)。相较 ctx/ss 两轨, full 不做任何句级截取, 因此语调测量覆盖整篇报道的全部极性词, 是本家族的基准文本轨。规则口径为 degonly: 仅施加程度副词六级加权, 不做否定翻转、不做转折 boost, 与同家族其余规则消融臂正交并列。样本框为 exc 停刊稳健性: bank-year 聚合仅纳入 _is_ceased_media==0 的存活媒体文章, 剔除疑似退出覆盖的媒体以防幸存者偏差污染。须特别指出留篇门控的非对称性 (2026-06-29 full-only 口径): 一篇报道是否被计入"银行金科报道"由 full 轨的 llm_verified 判定唯一决定, 因此 full 轨的行宇宙即本家族三轨行宇宙的上界, ctx/ss 两列均是在 full 留篇集之上再按各自窗口条件化的子集测度。定位上, full 轨与 ctx、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; 同理 degonly 与家族外六个规则臂亦各自 just-identified 并排、禁混同一 over-identified Hansen J。exc_* 情感类列在零文章 bank-year 保持 NaN, 不做计数式零填。相对家族 canonical 主列 jiang_2021_score, 本 full 列的唯一系统性偏离在聚合样本框 (exc 停刊稳健性子集) 与规则口径 (degonly 消融) 两处, 文本轨则同为 full; 因此在解读时, 本列与主列的差异应归因于"是否剔除疑似退出媒体"叠加"是否保留否定与转折规则"两条效应, 而非文本覆盖范围的变化。这一分层使得研究者可把停刊稳健性与规则消融两条稳健性轴解耦考察。

## VAR: exc_jiang_2021_score_degonly_ss

【变体差分】
本列取三轨中的 ss (same-sentence) 轨, 是家族内文本判据最严格的一轨: 文章级 jiang_2021_score_degonly 在 content_ss 上计算, 该文本 = 标题 prepend + 银行∧金科同句共现窗口 (目标银行与金融科技词在同一句、并按配置的句半径 ss_sentence_radius 取邻域, 默认 ±1 句), 由 stage 14 物化。相较 ctx 轨取实体上下文窗口, ss 要求银行与金科在同句共现, 判据更紧, 目的是把语调测量锁定在银行与金融科技直接相关联的语境。ss 轨的回退语义镜像 ctx: 当某文章无银行∧金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True (与 ctx 共享 n_articles 分母); 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 优雅降级。规则口径与家族一致为 degonly (仅程度副词加权, 无否定、无转折)。样本框亦为 exc 停刊稳健性: bank-year 聚合仅纳入 _is_ceased_media==0 的存活媒体文章。定位上, ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。按 full-only 留篇门控 (2026-06-29), 本 ss 列为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集; 在 T=2 开发盘上 ss 轨可能出现较多回退或零方差, 属预期退化, 生产 T=19 语料下恢复正常。若该轨缺列或存活媒体子集为空, 本列按守卫优雅跳过并保持 NaN, 不连带零填。相对家族 canonical, 本列在三个维度上同时偏离: 文本轨为最严格的 ss 同句共现判据、规则口径为 degonly 消融、聚合样本框为 exc 停刊稳健性子集; 三者相互正交, 分别刻画"读哪些同句片段""保留哪些语言学规则""聚合哪些存活媒体文章"。正因判据最严, ss 轨在噪声较大或共现稀疏的报道上更易触发全文回退, 因此本列在稳健性梯子中承担"最保守语境"角色, 与 full/ctx 两轨形成由宽到严的语境谱, 供论文论证主结论对语境收窄不敏感。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
