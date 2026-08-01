---
family_id: F264
novelty_exempt_rationale: "exc_ 前缀的疑似退出覆盖稳健性剔除变体家族, 是对 jiang_2021 词典情绪母族施加媒体构成稳健性检验的技术变体 (与 bal_ 互为姊妹稳健轨), 非独立新构念, 测度定义的学术依据已在母族词典原始文献 (姜富伟等 2021) 及既有 5 篇方法学引文中给出, 不需追新文献。"
columns:
- exc_jiang_2021_score_raw_ctx
- exc_jiang_2021_score_raw_full
- exc_jiang_2021_score_raw_ss
unit: 情感倾向分值 (无量纲, 自归一化于 [-1, 1])
formula: "exc_jiang_2021_score_raw_{track} = mean_{i in bank-year, outlet 未停刊}( jiang_2021_score_raw article-level ); raw = (pos - neg)/(pos + neg), 不施加否定翻转/程度副词/转折三类语言学规则 (自归一化, 非可加分解)"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_score_raw_{track} 文章级)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
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
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
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
本家族度量的是"疑似退出覆盖稳健性"口径下、以姜富伟等 (2021) 中文媒体情绪词典计算的银行-年度报道情绪倾向。构念的落点不是新增一套情绪测量, 而是对既有 jiang_2021 词典情绪聚合施加一层媒体构成 (media composition) 的稳健性检验: 生产函数 detect_defacto_cessation 检测的是媒体在样本期内"退出银行-fintech 话题覆盖" (topic exit), 而非经证实的报纸停刊 (publication cessation) —— 该媒体本身完全可能仍在正常出版, 只是不再报道银行-fintech 这一话题子集。因此排除集是"疑似退出话题覆盖"的 confirmed(经 NPPA 等外部登记交叉验证)∪suspected(仅凭情绪列前缀清单探测到无有效记录、未经外部证实)两部分之并集: 只要某一媒体来源在某年已无任何情绪分值列 (覆盖 LLM 投票、各大 LLM、词典法与 BERT 前缀, 含 jiang_2021_score_) 命中记录, 无论是否经过 NPPA 交叉验证, 均全量计入排除集, 从聚合分母中剔除, 只在"仍在覆盖"的媒体子集上重算银行-年度情绪均值。NPPA 等外部证据交叉验证只改变该来源被标记为 confirmed 还是 suspected 的标签, 并不收窄排除集本身 —— confirmed 与 suspected 一律同等剔除。前缀 exc_ (exclude) 标记的正是这一"疑似退出话题覆盖"的保守剔除子样本口径, 下游必须解读为疑似退出覆盖媒体稳健性口径 (保守剔除), 不可表述为严格停刊口径; 它与同一生产函数下的平衡媒体口径 bal_ (仅保留在样本期各年均有报道的媒体, 构成媒体维度的平衡面板) 互为姊妹稳健性轨。构念动机在于: 若主结论由少数在样本尾部退出话题覆盖的媒体所驱动 (幸存者偏差、构成漂移, 无论其退出的真实原因是停刊、改版还是单纯不再报道该话题), 则以这一保守代理剔除后结论应保持稳定; exc_ 轨提供的正是这一"媒体构成不驱动结论"的证据, 而非对停刊事实本身的确证测量。

【方法学与计算】
文章级底料是 jiang_2021_score_raw 的三轨分值。其中 jiang_2021 指姜富伟等 (2021) 发表于经济学(季刊)的中文财经媒体情绪词典, 该文以人工标注与机器学习方法从中文财经新闻语料中提炼正负情绪词表, 并证明由此构造的媒体情绪对 A 股横截面与时序回报具有预测力, 是本项目六部中文情绪词典之一。后缀 raw 指规则消融梯度中的"零规则"变体: 情绪分按 (pos - neg)/(pos + neg) 自归一化, 不施加否定翻转、程度副词加权、转折让步三类语言学规则中的任何一类; 它是消融 powerset 的下界基点, 与 negonly/degonly/advonly/negdeg/negadv/degadv 等六个带规则变体互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J (各变体高度共线, 相关系数近 0.99, 报相关而非并入同式)。银行-年度聚合是在剔除疑似退出话题覆盖的媒体来源 (confirmed∪suspected) 后, 对该银行该年"仍在覆盖"子集的报道逐篇分值取均值, 三轨各自独立聚合。整个 exc_ 家族属纯 CPU、零 API 成本的面板后处理, 不触发任何 LLM 或嵌入调用, golden 可复现。

【文献定位】
本家族站在词典法情绪测量与其稳健性检验两支文献的交叉处。词典源头姜富伟等 (2021) 属中文场景的媒体情绪词典构造与资产定价应用; 其英文对应的方法学传统可上溯 Jiang, Lee, Martin & Zhou (2019) 在 Journal of Financial Economics 上以文本情绪 (manager sentiment) 预测股票回报的经典工作, 后者系统论证了从公司披露文本抽取的情绪指数具有稳健的横截面定价含义, 为本项目将媒体情绪聚合为银行-年度面板变量提供了方法学正当性与顶刊锚。中文财经文本的领域特异性由 Du, Huang, Wermers & Wu (2022, Review of Finance) 系统刻画, 他们证明通用情绪词典在中文财经语境下会系统性失准, 支持本项目并置多部中文专用词典 (jiang/yao/bian/du/you/loughran) 互为稳健的设计。词典法与机器学习法孰优的争论由 Frankel, Jennings & Lee (2022, Management Science) 给出细致对照, 支撑本项目"三方法 (LLM/词典/BERT) 互为稳健、不分主次"的总体架构。测量效度层面, van Atteveldt, van der Velden & Boukes (2021) 与 Barbaglia 等 (2025) 分别从人工标注对照与经济文本词典法的角度论证了词典情绪的适用边界与效度前提, 提示 raw 零规则变体在缺失否定与转折处理时可能低估语义反转, 这正是消融梯度并置带规则变体的意义所在。 至于 exc_ 前缀所刻画的「剔除疑似退出覆盖媒体后再做银行-年度聚合」一环, 其现实动机可锚 Cziraki 与 Gider (2024): 该工作论文以报纸停刊为冲击, 实证报道供给的退出会改变本地股票的交易行为, 说明媒体退出并非无关紧要的样本损耗, 而是真实且有经济后果的样本组成变化, 因而值得单列一条剔除后重算的子样本臂。边界须如实写明: 原文的停刊判定取自外部事件数据、DV 为本地股票交易活动, 且停刊被用作识别冲击; 而本族 ceased_set 是由 detect_defacto_cessation 自语料内部推断的「疑似退出覆盖」保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 用途仅限稳健性子样本而不承担识别功能; 该文为工作论文, 未经同行评审。
## VAR: exc_jiang_2021_score_raw_ctx

【变体差分】
本列为 ctx (上下文窗) 轨: 文章级底料取自 content_ctx, 即标题 prepend 到实体上下文窗口 (目标银行实体命中位置附近的窗口文本) 之上, 再由 jiang_2021 词典按 raw 零规则口径打分, 在剔除疑似退出话题覆盖媒体来源 (confirmed∪suspected, 保守代理而非确证停刊) 的子样本上聚合为银行-年度均值。相较 full 轨用整篇正文, ctx 轨只截取围绕银行实体的邻近文本, 意在剥离与目标银行无关的段落噪声, 使情绪更聚焦于涉行语境; 它是 full 主轨的规格稳健性轨。三轨 (full/ctx/ss) 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨同列混入同一 over-identified Hansen J。需强调留篇门控为 full-only (2026-06-29 口径): 一篇报道是否计入某银行该年的报道宇宙, 只由 full 轨的 LLM 判定决定, ctx 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 ctx 的分值与聚合按 ctx 自身文本独立计算。本列同时叠加 exc_ 的疑似退出话题覆盖剔除口径, 因此它回答的是"在只看涉行上下文、且保守剔除疑似退出覆盖的媒体后, 情绪结论是否仍稳健" —— 被剔除的来源未必已实际停刊, 也可能只是不再报道银行-fintech 话题。需注意 ctx 轨的实体窗口截取会使正负情绪词的可及范围收窄, raw 零规则又不做否定与转折修正, 两者叠加时对语义反转 (如"并非利好""风险可控") 的捕捉能力最弱, 因此本列的解读应始终与 full 主轨及带规则消融变体并置对读, 而非单列作因果推断的唯一测度。ctx 与 ss 两轨的分母口径一致 (共享 n_articles), 差异只在文本窗的宽窄; exc_ 前缀的疑似退出覆盖剔除只改变纳入聚合的媒体来源集合, 不改变逐篇打分口径。本列的价值在于以最窄涉行语境 × 最严媒体构成的双重收紧, 验证主结论对文本范围与样本构成两个自由度的联合不敏感性。

## VAR: exc_jiang_2021_score_raw_full

【变体差分】
本列为 full (全文) 轨, 是三轨中的 canonical 主轨: 文章级底料取自 content_full, 即标题 prepend 到完整正文之上, 由 jiang_2021 词典按 raw 零规则口径逐篇打分, 在剔除疑似退出话题覆盖媒体来源 (confirmed∪suspected) 的子样本上聚合为银行-年度情绪均值。full 轨承担留篇门控职责——一篇报道是否被判为"一篇银行金科报道"并计入报道宇宙, 只看 full 轨的 LLM 判定 (llm_verified_full == True); ctx 与 ss 两轨在此意义上都是 conditional-on-full 的稳健性轨。因此在 exc_ 家族内, full 轨给出的是最完整文本证据下的疑似退出覆盖稳健性情绪基准, ctx/ss 是围绕它的规格变动。三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。raw 后缀标明本列不施加否定/程度/转折任一语言学规则, 与带规则消融变体亦为并排稳健关系而非主从; exc_ 前缀标明聚合分母已剔除疑似退出话题覆盖的媒体来源 (topic exit 的保守代理, 该来源可能仍在正常出版, 不可解读为确证停刊), 与平衡媒体 bal_ 口径互为媒体构成维度的姊妹稳健轨。作为 canonical 主轨, 本列在实证中通常充当疑似退出覆盖稳健性检验的基准列: 若无后缀主口径 (全媒体) 的情绪系数在剔除疑似退出覆盖来源后于 full 轨上保持符号与量级稳定, 即构成"结论不由幸存者偏差或媒体构成漂移驱动"的直接证据; 该检验本身不依赖、也不构成对任何来源确已停刊的事实性判定。full 轨保留完整正文, 相较 ctx/ss 两轨捕捉到最多的情绪词, 分母亦最厚实, 因而在早期试跑 T=2 样本上退化最少、在生产 T=19 全量语料上估计最稳。本列与 exc_jiang_2021_score_raw 的 ctx、ss 两列构成同一疑似退出覆盖口径下的三轨规格谱系, 三者只应作互为稳健性的并排读法。

## VAR: exc_jiang_2021_score_raw_ss

【变体差分】
本列为 ss (同句共现) 轨: 文章级底料取自 content_ss, 即标题 prepend 到"目标银行与金融科技词同句共现 ±N 句窗"文本之上 (窗半径由 config/filtering.yaml 的 ss_sentence_radius 配置, 默认 1), 再由 jiang_2021 词典按 raw 零规则口径打分, 在剔除疑似退出话题覆盖媒体来源 (confirmed∪suspected 的保守代理) 的子样本上聚合。ss 轨是三轨中语境最窄者, 只保留银行与金科议题真正同句交汇的片段, 情绪由此最贴近"银行涉金科"这一核心构念。其回退语义镜像 ctx: 当某篇无银行∧金科同句共现时, content_ss 退回全文正文并置 ss_is_fallback=True (与 ctx 共享 n_articles 分母); 若 FINTECH_AC 为空则 ss_is_fallback 全 True 优雅降级。ss 轨同样是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集子集, 留篇门控仍为 full-only。三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混入同一 over-identified Hansen J。叠加 exc_ 口径后, 本列回答"仅看银行金科同句语境、且保守剔除疑似退出话题覆盖的媒体后情绪是否稳健" —— 被剔除的媒体来源未必已确证停刊, 可能只是不再覆盖银行-fintech 话题, 表述上不可等同于严格停刊。由于 ss 语境最窄, 在早期试跑 T=2 短面板上极易出现该银行该年无任何同句共现从而大面积回退到全文的情形, 使 ss 轨在小样本上与 ctx 轨趋同、方差偏低属预期退化, 需在生产 T=19 全量语料上方能充分体现其涉金科语境的辨识力。本列与 full、ctx 两轨互为稳健性, 与 raw 之外的带规则消融变体亦为并排关系; exc_ 疑似退出覆盖剔除与 bal_ 平衡媒体则是媒体构成维度上的两条姊妹稳健轨。任何跨轨、跨消融变体、跨媒体构成口径的比较都只作稳健性对读, 绝不并入同一 over-identified 的 Hansen J 过度识别检验。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
