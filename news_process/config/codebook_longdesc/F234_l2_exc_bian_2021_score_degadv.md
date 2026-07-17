---
family_id: F234
novelty_exempt_rationale: "该家族是 exc_(停刊稳健性排除样本) × degadv(程度+转折规则消融臂) 双重变体家族, 基于 Bian et al. (2021) 词典的技术性稳健性检验, 测度定义依据母族词典与规则消融梯度既有文献, 非独立新构念, 无需追新文献。"
columns:
- exc_bian_2021_score_degadv_ctx
- exc_bian_2021_score_degadv_full
- exc_bian_2021_score_degadv_ss
unit: 无量纲情感得分, 值域 [-1, 1] (银行-年内非停刊代理媒体报道的篇均情感均值)
formula: "exc_bian_2021_score_degadv{track} = mean_{i ∈ 非停刊代理媒体} bian_2021_score_degadv{track}_i; 其中 bian_2021_score_degadv = Σ(base_valence · degree_weight · adversative_boost) / Σ|base_valence · degree_weight · adversative_boost| (否定翻转规则关闭, 程度副词与转折规则开启), 值域 [-1,1]"
producer: news_process/pipeline/panel/attention_media.py (exc_* 停刊稳健性再聚合, 动态发现 _SCORE_PATTERNS); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::_dual_analyze (rule-ablation ladder, _RULE_ABLATION_VARIANTS 中的 degadv 变体)
upstream:
- 22_tone_words.parquet (文章级 bian_2021_score_degadv{track})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_export_main (停刊代理检测 detect_defacto_cessation → _is_ceased_media)
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
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1145/1341531.1341561
  type: journal
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)
  pages_or_artno: 231-240
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
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
本家族度量的是银行-年层面、基于 Bian et al. (2021) 中文金融情感词典计算的报道情感得分, 且限定在两个交叉口径上: 其一为"停刊稳健性"子样本 (变量名前缀 exc_, 即 exclusion), 其二为"程度+转折"规则消融臂 (后缀 degadv)。Bian et al. (2021) 是一部面向会计与金融文本分析的中文金融情感词典, 通过对中文财经语料的人工标注与词表扩展, 给出正面词与负面词的极性清单; 相较于将英文 Loughran-McDonald 词典机械翻译的做法, 它在中文金融语境下具备更贴合的领域特异性。本项目在 tone_words 阶段以该词典为极性来源, 对每篇报道分词后逐词匹配, 得到词级基础极性 (base valence), 再叠加语言学规则得到篇章得分。degadv 是规则消融梯度 (rule-ablation ladder) 的一个具体臂: 关闭否定翻转规则 (negation 关), 同时开启程度副词加权 (degree 开) 与转折/让步重配权 (adversative 开)。从组合上看它恰等于"完整规则减去否定" (full − negation), 因而与 negonly、degonly、advonly、raw 等其它消融臂并列, 共同构成"主结论对每一条语言学规则是否敏感"的稳健性证据链, 而非声称某一臂在测量上更优。

【方法学与计算】
计算分两级。文章级: 对报道文本 (按三轨物化) 分词后, 用 Bian et al. (2021) 词表逐词赋极性, 得到每个匹配词的基础极性 base_valence; 在 degadv 臂下, 程度副词按六级强度对相邻情感词的极性进行缩放, 转折连词 (如"但""然而") 对分句极性进行 boost 重配权, 而否定词不触发极性翻转。篇章得分取带符号极性之和除以其绝对值之和, 即 Σ(final_valence) / Σ|final_valence|, 自归一化到 [-1, 1], 与家族 canonical 的无后缀 bian_2021_score 采用同一归一化口径, 唯一差别是所启用的规则子集。面板级: 在 attention_media 阶段, 系统先以"话题覆盖退出"为停刊的保守代理 (cessation proxy) 检测疑似退出媒体, 将 confirmed 与 suspected 合集标记为 _is_ceased_media, 未经 NPPA 交叉验证证实的 suspected 亦保守计入排除集; 随后仅在非停刊代理媒体的报道子集 (df_alive) 上, 按银行-年分组对文章级 degadv 得分取算术平均, 落为 exc_bian_2021_score_degadv{track}。零文章的银行-年在情感类列上按契约保持 NaN (不做零填, 与计数类 n_articles_exc 的零填契约相区别)。需要强调: exc_ 口径应解读为"疑似退出覆盖媒体"的保守剔除稳健性检验, 用于缓解媒体消失带来的幸存者偏差 (survivorship bias) 对情感测度与 Bartik 类工具变量的污染, 不可在论文中表述为严格的出版停刊口径。

【文献定位】
词典法情感测量的方法学谱系是本家族的核心参照。Bian et al. (2021) 提供了极性词表这一原料; 而 degadv 臂所叠加的程度副词加权与转折重配权, 属于 valence-shifter (情感转移语) 谱系, Taboada et al. (2011) 系统论证了程度词、否定词与转折结构对情感极性的调节作用, Ding et al. (2008) 亦在整体式词典法中处理了转折等语境反转; 本项目正是把这些规则拆成可开关的消融臂以做敏感性检验。词典法与机器学习法孰优的争论上, Frankel et al. (2022, Management Science) 比较了披露情感的机器学习与词典两类测度, 支持将不同方法并列互证的做法, 这与本项目情感三法 (LLM 三家 / 词典 / BERT 三模型) 互为稳健性的设计一脉相承。van Atteveldt et al. (2021) 则从人工标注、众包、词典与机器学习的横向对照出发, 提醒词典法在效度上的边界。中文金融领域的领域特异性上, Du et al. (2022, Review of Finance) 记录了将通用或英文词典迁移到中文金融文本的失配, 强调领域自建词典的必要性; Ma et al. (2025) 进一步构建面向中国投资者的细粒度情感词典。这些文献共同支撑本项目为何同时并行多部中文金融词典、并对每部词典做规则消融梯度的方法论选择。凡涉三轨与消融梯子的度量, 各臂各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified 的 Hansen J 检验。 就 degadv 臂关闭否定翻转、仅保留程度与转折两规则这一设定, Naldi 与 Petroni (2023) 以人工构造测试集评估多款词典法情感工具的否定检测与处理能力, 发现各工具表现差异显著, 说明否定是词典法内部可被单独测量、亦可单独失效的模块, 因而把它开/关成一条独立可报告的臂是有据的; 边界在于该文为英文通用领域的工具评测、度量的是否定检测准确率, 而本族不做准确率评测, 只把否定关闭后的自归一化得分作为面板测度的一条并排稳健臂。就剔停刊这一样本口径, Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 说明媒体退出是有经济后果的样本组成变化, 锚定本族先剔除疑似退出覆盖媒体再做银行-年度聚合的动机; 迁移边界为该文停刊判定取自外部事件数据并用作识别冲击, 而本族 ceased_set 系自语料内部推断的保守代理 (confirmed ∪ suspected), 仅作稳健性子样本, 且该文为工作论文尚未经同行评审。
## VAR: exc_bian_2021_score_degadv_ctx

【变体差分】
本列是 degadv 规则消融臂在 ctx (实体上下文窗) 轨、且限定于非停刊代理媒体子样本上的银行-年篇均情感得分。相对于家族三列, 其唯一差分维度是文本轨道: ctx 轨的输入文本为 content_ctx, 即标题 prepend 后再取目标实体 (银行) 出现处的上下文窗口, 而非全文正文。因此本列衡量的是"当报道聚焦于银行相关语境片段、且仅在存活媒体上、且启用程度+转折但关闭否定翻转规则时"的情感倾向。相对于家族 canonical 参照 (无后缀 bian_2021_score, 全规则、全样本), 本列在三个维度上偏移: 规则子集 (degadv = 关否定 / 开程度 / 开转折)、样本口径 (exc = 剔疑似退出覆盖媒体)、文本轨 (ctx)。ctx 轨与 full、ss 两轨互为稳健性、不分主次、各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J。留篇门控采用 full-only 口径 (2026-06-29), ctx 轨为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, per-track 得分照算。在盘上 T=2 开发样本中, 因实体窗共现与停刊剔除双重收窄, ctx 轨可能出现较多零文章银行-年而按契约留 NaN, 属预期退化, 生产 T=19 语料下方能正常取值。需注意 ctx 轨与家族无后缀的 exc_bian_2021_score_ctx (全规则版) 的差别只在规则子集: 后者叠加否定翻转, 本列关闭否定; 两者相减可近似读出否定翻转规则在实体窗语境下对情感极性的净贡献, 用于论证主语调结论不被"是否处理否定"这一建模选择所驱动。该差分与样本口径 (exc)、文本轨 (ctx) 相互正交, 不应交叉解读为单一维度效应。

## VAR: exc_bian_2021_score_degadv_full

【变体差分】
本列是 degadv 规则消融臂在 full (标题+全文正文) 轨、限定于非停刊代理媒体子样本上的银行-年篇均情感得分。其文本输入为 content_full, 即标题 prepend 后拼接完整正文, 覆盖面最广, 是三轨中信息量最全的一轨。相对家族 canonical (无后缀 bian_2021_score, 全规则、全样本、全轨), 本列的差分在于: 规则子集为 degadv (否定翻转关闭, 程度副词与转折规则开启, 组合上等于 full 规则减去否定这一条), 样本口径为 exc (仅保留非停刊代理媒体, 剔除疑似退出覆盖的报纸以缓解幸存者偏差)。full 轨在项目中通常承担 canonical headline 与留篇门控角色 (留篇判定只看 full 轨的 llm_verified_full), 但就本 exc/degadv 稳健性列而言, full 轨与 ctx、ss 两轨互为稳健性、不分主次、各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J。将本列与家族内其它消融臂 (raw / negonly / degonly / advonly / negdeg / negadv) 的 full 轨版本对照, 可读出主语调结论对"是否施加否定翻转"这一条规则的敏感性: 若剔除否定后得分与全规则得分高度共线且系数方向不变, 即支持"定性不变"的稳健性叙事。此处须警惕: 规则消融各臂之间高度共线 (audit MATH-1 记录全规则与仅否定臂的相关系数常在 0.998 以上), 因而是"非可加分解", 应逐臂并列报告相关性而非将多臂并入同一线性式; 计数口径的零规则档亦刻意不入本谱, 以避免口径混淆。full 轨作为信息量最全的一轨, 其 degadv 值在存活媒体子样本上的稳定性, 是评估媒体退出是否系统性地扭曲了否定相关表述频率的直接证据。

## VAR: exc_bian_2021_score_degadv_ss

【变体差分】
本列是 degadv 规则消融臂在 ss (银行与金科同句共现窗) 轨、限定于非停刊代理媒体子样本上的银行-年篇均情感得分。其文本输入为 content_ss, 即标题 prepend 后取目标银行与金融科技词在同一句子内共现 (±N 句窗, 默认半径 1) 的最窄语境片段; 若某报道不存在银行与金科的同句共现, 则 ss_is_fallback 置 True 并镜像 ctx 的回退语义降级为全文 body, 与 CLAUDE.md 三轨回退口径一致。因此本列衡量的是"当报道把银行与金融科技拉到同句、且仅在存活媒体上、且启用程度+转折但关闭否定翻转时"的情感倾向, 是三轨中语境最聚焦、最贴近"银行金科关系"构念的一轨。相对家族 canonical, 本列在规则子集 (degadv)、样本口径 (exc)、文本轨 (ss) 三维度同时偏移。ss 轨与 full、ctx 互为稳健性、不分主次、各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J; 同样受 full-only 留篇门控约束, 为 conditional-on-full 测度轨。在 T=2 开发样本上, 同句共现叠加停刊剔除会令本轨极度稀疏乃至零方差, 属预期退化, 需在生产 T=19 语料下评估其有效取值分布。由于 ss 轨把语境窄化到银行与金科同句这一最严判据, 它对停刊剔除尤其敏感: 一旦某地方性报纸退出覆盖, 其贡献的同句共现片段整体消失, 从而使 exc 口径下的 ss 得分与全样本 ss 得分的落差, 直接反映了退出媒体在"银行金科关系"这一最核心构念上的覆盖倾向。degadv 规则子集在 ss 轨上的意义与其它两轨一致: 关闭否定翻转、保留程度与转折调节, 用以检验最聚焦语境下的情感结论是否依赖否定建模。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08), 231-240. https://doi.org/10.1145/1341531.1341561
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
