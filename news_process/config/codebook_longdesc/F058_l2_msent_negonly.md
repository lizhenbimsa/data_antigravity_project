---
family_id: F058
columns:
- avg_msent_negonly_ctx
- avg_msent_negonly_full
- avg_msent_negonly_ss
unit: 无量纲计数型情感指标 (取值区间 [-1, +1]; 银行-年均值)
formula: "article: msent_negonly = (n_neg' - n_pos') / (n_pos' + n_neg'), 其中 n_pos'/n_neg' 为并集词典正/负面词计数, 仅施加否定翻转规则 (程度副词与转折连词规则关闭); panel: avg_msent_negonly_{track} = mean_over_retained_articles(msent_negonly_{track})"
producer: news_process/pipeline/sentiment/tone_words.py (article-level msent_negonly) ; news_process/pipeline/panel/encode.py (bank-year aggregation)
upstream:
- 21_tone_llms.parquet (content_full / content_ctx / content_ss, full-only 留篇门控后的银行金科报道)
- 22_tone_words.parquet (msent_negonly_{full,ctx,ss})
citations:
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: "Pröllochs, N., Feuerriegel, S., & Neumann, D."
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.jbankfin.2025.107542"
  type: "journal"
  authors: "Lehkonen, H., Heimonen, K., & Pukthuanthong, K."
  year: 2025
  title: "Media tone is a priced risk factor in currency markets"
  venue: "Journal of Banking & Finance"
  vol: "180"
  pages_or_artno: "107542"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"仅否定规则计数型情感指标"(msent 的 negonly 消融变体)在银行-年层面的均值。它属于 stage 22 词典情感 (tone_words) 产出的 $0 纯 CPU 测度族, 与 stage 21 的 LLM 三家投票情感、stage 23 的 BERT 三模型情感构成互为稳健性、不分主次的三法并列证据链。计数型情感指标 msent 的原点是 Tetlock (2007) 在《Journal of Finance》确立的媒体词频情感范式: 把一篇文本的情绪倾向压缩成正、负面词计数的相对差, 以透明、可复现、逐词可审计的方式度量语气。本家族的 negonly 变体在此基础上做一次受控简化——只保留否定翻转这一条中文语法修正, 关闭程度副词缩放与转折连词加权两条规则, 用来回答"主结果是否过度依赖那两条修饰规则"这一稳健性问题。

【方法学与计算】
文章级 msent_negonly 的算法链路是: 先由 build_union_dictionary 把六部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026, 末者即 Loughran & McDonald 2011 的中文主译本) 合并为一部并集词典, 重叠词按极性多数票消解、平票剔除; 再用冻结版 jieba (0.42.1) 分词, 逐 token 走状态机 _compute_sentiment_with_rules。negonly 档的参数设定是 apply_negation=True、apply_degree=False、apply_adversative=False, 即遇到否定词 (如"不""未""无") 时在 NEGATION_WINDOW=2 个分词单元的窗口内翻转后续词的极性 (不乐观计入负面), 但不做"非常"类程度副词的六级权重缩放, 也不做"但是/然而"类转折连词后半句的加权提升。据此得到经否定修正的正、负面词计数 n_pos'、n_neg', 计数型指标取 msent_negonly = (n_neg' - n_pos') / (n_pos' + n_neg'), 取值落在 [-1, +1], 数值越高代表负面语气越重 (符号朝向负面, 与部分正向定义的语气分相反, 使用时须注意方向)。它是计数口径而非自归一 Σ|final| 口径, 因此与同族 rule-ablation 的 {dict}_score_negonly (自归一化得分) 刻意分开, 不混入同一分解式。银行-年聚合在 encode.py 完成: avg_msent_negonly_{track} 取该银行该年全部留篇文章 msent_negonly_{track} 的算术平均; 它与零规则原始极性计数的 avg_msent 配对, 二者之差 (avg_msent_negonly − avg_msent) 即纯否定规则的边际贡献, 用作透明的规则敏感性诊断。据 producer 说明, negonly 档与全规则档在文章级实测高度共线 (相关系数约 0.998–0.999), 印证它是稳健性对照而非独立新信号。

【文献定位】
本家族的方法学锚点有三。其一是 Tetlock (2007), 它奠定了以正、负面词计数相对差度量媒体语气、并将其接入资产定价回归的经典范式, 是 msent 计数口径的构念原点。其二是 Loughran & McDonald (2011) 在《Journal of Finance》的工作, 它论证了通用情感词典 (如 Harvard IV) 在金融文本上的系统性误分类, 主张改用领域专用词表并以词频而非复杂加权来度量语气——这正是本管道并集词典 (含其中文主译本) 与计数口径的直接依据。其三是 Pröllochs, Feuerriegel & Neumann (2016), 它系统研究了否定作用域检测对新闻驱动情感度量的价值, 为 negonly 档"只保留否定翻转"这一受控消融提供了直接的方法学正当性: 否定处理是词典情感中信息增益最确定、争议最小的一条语法规则, 因此被单独保留作为最小规则基线。凡涉三轨 (full/ctx/ss) 与规则消融梯子的证据, 本管道一律遵循"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"的铁律; negonly 与 full 规则档、程度/转折各消融档均属规格稳健性并排, 不设 FWER 模板, 彼此正交不交叉。 在近期同域文献中, 本家族所依托的比率型计数形态与银行层面应用亦获得进一步印证。Lehkonen、Heimonen 与 Pukthuanthong (2025) 用覆盖全球逾两千家媒体与八百家社交站点的约七百万篇文本构造媒体语调, 证明以正负提及净额除以总提及构成的比率型语调是可跨截面定价的真实风险因子, 为本家族 (n_neg' − n_pos') / (n_pos' + n_neg') 这一比率形态提供了近期顶刊级的经济含义支撑; 但其语调取自 Refinitiv MarketPsych 专有商业指数而非自建词表命中计数, 构造细节不可复核, 亦不含任何否定作用域处理, 故不能据以为 negonly 这一「只保留否定翻转」的规则档设定本身背书, 其层级为货币-国别、语料为英文财经新闻, 与本管道的银行-年、中文报纸口径不同。Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 说明按银行主体归集新闻情感并接入银行层面实证已为顶级金融稳定期刊接受, 锚定的是本家族「逐篇计数极性 → 银行-年均值」这一聚合环; 其语境为美国银行监管 (监管评级与监管行动为因变量), 情感测度构造与本管道六词典并集的计数口径不同, 更未涉及中文否定翻转等语法规则层与 full/ctx/ss 三轨文本设计, 因此对本族只锚定聚合形态, 不锚定极性来源与规则消融梯子。
## VAR: avg_msent_negonly_ctx

【变体差分】
本列是 ctx 轨 (context, 实体窗口轨) 下的仅否定计数型情感银行-年均值。ctx 轨的文本 content_ctx 由 stage 14 ctx_materializer 物化, 内容 = 标题 prepend + 银行实体上下文窗口 (围绕目标银行提及的邻近片段), 而非全文正文。因此本列度量的是"银行相关段落"这一收窄语境内、只施加否定翻转规则的语气计数差。它与同家族 avg_msent_negonly_full、avg_msent_negonly_ss 是同一 negonly 计数口径在三条不同文本轨上的并排实现, 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。分子分母严格逐轨: n_pos'、n_neg' 均在 content_ctx 上计数, 不借用 full 轨语料。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道行宇宙, 只看 llm_verified_full 是否为真, ctx 轨在留篇集子集上按本轨语料照算, 属 conditional-on-full 的测度/稳健性轨。若某银行某年无任何 content_ctx 有效计数, 该格按逐轨口径退化 (缺列跳轨不借 full 分母), 在早期试跑 T=2 样本上出现零方差或 NaN 属预期退化, 生产 T=19 语料下正常取值。方向朝向负面 (值越高负面越重), 与 avg_msent (零规则) 配对可分解 ctx 轨上否定规则的纯边际贡献。需要强调的是, ctx 轨的实体窗口比 full 轨窄、比 ss 轨宽, 处于三轨语境粒度谱系的中段, 因此本列在解释上介于"全篇泛化语气"与"银行金科同句聚焦语气"之间, 常被用作 full 主轨的首要稳健性对照: 若银行相关段落内的否定计数语气与全篇一致, 则可排除"语气信号来自与银行无关的文本噪声"这一竞争性解释。计数口径与自归一 rule-ablation 得分列刻意分离, 不并入同一分解式; jieba 分词与并集词典均为冻结确定性组件, 保证跨 run 可复现。

## VAR: avg_msent_negonly_full

【变体差分】
本列是 full 轨 (标题 prepend + 全文正文) 下的仅否定计数型情感银行-年均值, 是本家族三轨中的 canonical 主轨。full 轨文本 content_full 覆盖整篇报道的全文, 由 stage 14 物化 (原始"内容"列不动, 标题以 prepend 方式并入而非独立 title 轨——v3.8.0 已删除独立标题轨)。因此本列度量的是全篇范围内、只保留否定翻转规则的正负面词计数差。它是 full-only 留篇门控的直接落点: 留篇判定 (llm_verified_full == True) 与本轨语料同源, 使 full 轨成为三轨中样本最完整、分母最稳的一轨; avg_msent_negonly_full 与全规则的 full 档 avg_msent、及 ctx/ss 两轨的同名列一并构成规格稳健性并排, 各自 just-identified、互为稳健性不分主次、禁混进同一 over-identified Hansen J。计数口径而非自归一口径, 与同族 rule-ablation 的自归一得分列刻意分开。它与零规则 avg_msent_full 配对, 其差 (avg_msent_negonly_full − avg_msent_full) 度量全文范围内否定规则的纯边际贡献, 是判断主结果是否被否定处理这一条规则驱动的透明诊断量; 据 producer 实测, 该差在文章级极小 (两档相关系数约 0.998–0.999), 支持"结论对规则设定稳健"的叙事。方向朝向负面, 使用时须与正向定义的语气分区分符号。作为家族 canonical 主轨, 本列在下游回归中通常充当词典法计数型情感的代表口径, 与 LLM 三家投票情感、BERT 三模型情感并列构成三法互证; 三法各自 just-identified 并排、互为稳健性不分主次, 严禁在同一 over-identified Hansen J 中混用。它同时与全规则 full 档、程度消融档、转折消融档等 rule-ablation 变体形成规格稳健性梯子, 各消融档正交不交叉、不设 FWER 模板。full 轨的完整分母也使本列成为三轨中噪声-信号比最优的一轨, 适合作为敏感性检验的基准起点。

## VAR: avg_msent_negonly_ss

【变体差分】
本列是 ss 轨 (same-sentence, 银行∧金科同句窗轨) 下的仅否定计数型情感银行-年均值。ss 轨文本 content_ss 覆盖目标银行与金融科技词在同一句子 ±N 窗 (config filtering.yaml 的 context_window.ss_sentence_radius, 默认 1) 内共现的片段, 是三轨中语境最收窄、最贴近"银行确在谈金融科技"这一构念的一轨。其回退语义镜像 ctx: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置真, 并与全家族共享 n_articles 分母; 若 FINTECH_AC 为空则 *_is_fallback 全真优雅降级。因此本列度量的是银行金科同句语境内、只施加否定翻转规则的语气计数差。它与 avg_msent_negonly_full、avg_msent_negonly_ctx 同为 negonly 计数口径的逐轨实现, 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。分子分母严格逐轨在 content_ss 上计数, 不借 full 分母; 留篇仍遵 full-only 门控, ss 轨在留篇子集上按本轨语料照算, 属 conditional-on-full 稳健性轨。在早期试跑 T=2 样本上, ss 轨因同句共现稀疏常出现零方差或 NaN 属预期退化, 生产 T=19 下正常; 方向朝向负面, 与 avg_msent 配对可分解 ss 语境内否定规则的边际贡献。ss 轨是三轨中构念纯度最高、语境最严的一轨, 因为它要求银行与金融科技词真正落在同一句 (或 ±1 句窗) 内共现, 从而最大程度剔除"银行与金科各自出现在文中不同段落、实则无关"的伪共现噪声; 其代价是样本更稀疏、回退比例更高, 故常与 full/ctx 两轨并读——若三轨否定计数语气方向一致, 则结论对语境粒度稳健, 反之则提示信号对语境收窄敏感, 需进一步审视。它与家族其余两列同为 negonly 计数口径的规格稳健性并排, 不得混入同一 Hansen J; 回退语义严格镜像 ctx, 冻结 jieba 与并集词典保证确定性。

<!-- rendered-citations:begin -->
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
<!-- rendered-citations:end -->
