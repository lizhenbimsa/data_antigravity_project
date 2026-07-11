---
family_id: F055
columns:
- avg_loughran_neg_ratio_ctx
- avg_loughran_neg_ratio_full
- avg_loughran_neg_ratio_ss
unit: 占比 (proportion, 无量纲; 文章级取值 [0,1], 面板列为其银行-年算术均值)
formula: "avg_loughran_neg_ratio_trk = mean_i(loughran_neg_ratio_trk_i), trk ∈ (full, ctx, ss); 文章级 loughran_neg_ratio_i = neg_count_i / n_word_tokens_i, 其中 neg_count = 以 loughran_mcdonald_zh_2026 词典扫描、经否定/程度/转折全语言学规则后最终极性为负的命中 token 数 (跨类重叠 23 词两侧同计), n_word_tokens = 剔除纯标点/纯数字 token 后的词 token 数; 空文本或零 word-token → NaN"
producer: pipeline/sentiment/tone_words.py::_analyze_single_article (文章级 loughran_neg_ratio, 经 _compute_sentiment_with_rules 计数) → pipeline/panel/encode.py::build_aggregation_dict §M (bank-year 逐篇等权 mean); Stata 标签见 pipeline/panel/stata_export.py
upstream:
- 14_news_with_ctx.parquet (content_full / content_ctx / content_ss 及 *_is_fallback)
- 22_words_tone.parquet (文章级 loughran_neg_ratio_full/_ctx/_ss)
- config/tone_dicts.json (loughran_mcdonald_zh_2026 词表, 列前缀别名 loughran)
- 21_tone_llms.parquet (llm_verified_full 留篇门控, 决定聚合行宇宙)
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality"
  venue: Journal of Economics and Development
  vol: 27
  issue: 4
  pages_or_artno: 309-321
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: Wu, M., Shen, L., Wu, T., & Shao, Y.
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
  pages_or_artno: Advance online publication
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
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
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: The Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: "Political bias in corporate news: The role of conglomeration reform in China"
  venue: The Journal of Law and Economics
  vol: 60
  issue: 1
  pages_or_artno: 173-207
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】本家族三列测量的构念是银行-年层面新闻文本的负面语言强度, 即目标银行当年全部留存报道中, 按 Loughran-McDonald 金融情感词典中文主译本识别出的负面词汇在全文词量中所占的比重, 再对该银行该年全部文章取算术均值。它是一个单极 (unipolar) 测度: 只刻画负面词汇的浓度, 不与正面词汇轧差, 因而与净语调类指标在构念上严格分离。单极分离的方法学动机在于规避净情感指标的极性对冲掩蔽问题, 即一篇同时高密度使用正面与负面词汇的报道, 其净语调可能与一篇几乎不含情感词的中性报道数值相同, 但两者所承载的信息环境截然不同; 生产源码在文章级正负分离处明确援引 Garcia (2013) 的正负面词汇分离原则作为设计依据, 将正、负两个方向各自作为独立协变量物化, 供下游媒体分歧族指标消费。词表来源是本管道六部中文情感词典中的第六部 loughran_mcdonald_zh_2026, 即 Loughran 与 McDonald (2011) 在金融文本分析领域的奠基词典之中文主译本, 面板列前缀取别名 loughran; 该译本含正面词 1,295 个、负面词 3,729 个, 另附弱模态、强模态、复杂度、不确定与诉讼等非极性词类供同源姊妹列使用。Loughran 与 McDonald (2011) 的核心发现是: 通用心理学词表 (如 Harvard General Inquirer) 中被标为负面的英文词, 约四分之三在财务语境中并不承载负面含义, 因而金融文本研究必须使用领域专用词表, 且其中负面词表 (Fin-Neg) 的信息含量在实证上最为突出——负面词在披露文本中相对稀缺、区分度高, 且不像正面词那样易被管理层策略性堆砌, 这正是本家族以负面占比而非正面占比作为 core 列的谱系学理由。语料侧, 输入为本项目千万级中文媒体银行报道语料经共现硬过滤与验证门控后的留篇集; 文本域按三轨物化 (标题拼接全文、标题拼接实体窗口、标题拼接银行与金融科技词同句邻域), 三列一一对应三轨, 各轨在同一留篇集上按各自文本域独立扫描, 互为稳健性、不分主次。

【方法学与计算】计算链路分三段。第一段, stage 14 (ctx_materializer) 物化三轨文本列: content_full 为标题 prepend 加全文正文, content_ctx 为标题加目标银行实体上下文窗口, content_ss 为标题加银行与金融科技词同句共现句的正负一句邻域; ctx 与 ss 各带 is_fallback 指示列, 无相应窗口时回退为全文 body, 标题以首句身份参与分词与规则扫描而原始内容列不被改写。第二段, stage 22 (tone_words) 的 _analyze_single_article 对每篇文章、每条轨道独立执行词典扫描: 分词采用冻结版本 jieba 的独立 tone tokenizer (与领域词注入隔离, 保证跨期确定性), 随后由 _compute_sentiment_with_rules 的状态机遍历 token 序列——否定词开启定长翻转窗口, 程度副词设置倍率, 转折连词按 Ding 等 (2008) 的从句级作用域激活增强, 句末标点重置全部句法状态。负面计数 neg_count 取的是经全部规则处理后最终得分为负的命中 token 数, 因此一个被否定词翻转的正面词 (如"不乐观"中的"乐观") 会被计入负面侧, 这一口径与仅按词典原始极性计数的 msent 族刻意不同。该词典原有 61 个正负跨类重叠词, 经 2026-06-24 人工消歧后 38 个归入单侧, 其余 23 个不可约简者按"两侧保留"决策同时计入正负两个计数 (源码经 both_sided_words 形参实现), 使这些词的贡献对称地拉向中性而非武断选边。分母 n_word_tokens 为剔除纯标点与纯数字 token 之后的词 token 数, 对应 Loughran 与 McDonald (2011) 及后续文献以"占词数之比" (fraction of words) 定义占比的规范口径; 源码记录纯标点与纯数字 token 在开发盘上约占全部 token 两成、逐篇在一到三成之间波动, 若不剔除会造成非常数稀释而污染跨篇可比性。文章级值 = neg_count 除以 n_word_tokens, 保留六位小数; 空文本、纯符号文本或词典整体缺失时取 NaN 缺失语义, 而非回填零值伪中性, 以免在均值聚合中人为压低负面强度。第三段, stage 40 面板聚合: encode 模块 build_aggregation_dict 的 §M 单词典占比聚合段对六部词典乘三轨统一注册逐篇等权算术均值, 得到 avg_loughran_neg_ratio 三列; 聚合行宇宙遵循 2026-06-29 起的 full-only 留篇门控口径, 即一篇文章是否计入某银行-年, 只看全文轨 LLM 验证 llm_verified_full 是否为真, ctx 与 ss 轨列在同一行宇宙上按各自文本域计算, 属 conditional-on-full 的条件测度。整条链路不调用任何付费 API, 是零成本、字节级可复现的确定性测度。此处有一个值得写明的口径细节: 状态机中的程度副词倍率与转折增强只缩放命中词的得分幅度, 不改变其符号, 唯一能改变符号的规则是否定翻转; 因此对本占比列而言, 分子的有效构成等于"词典原判为负且未被否定翻转的词"加上"词典原判为正但被否定翻转的词", 程度与转折规则对计数本身没有影响, 只影响同源的 score 族。换言之, 占比列天然只对否定规则敏感, 这也是为什么规则消融梯度只需要在 score 族上物化——占比列的"消融版本"在数学上只有有否定与无否定两档, 而无否定档的信息已由原始极性口径的 msent 族承载。另一细节是轨道后缀的追加机制: 文章级函数返回无后缀键, 由三轨调度器对各轨结果统一追加 full、ctx、ss 后缀, 保证三轨获得完全同构的键集合, 包括空文本与回退场景下的 NaN 键, 从而三列在任何边界条件下都保持逐篇可比。

【文献定位】本家族站在金融文本词典法的正统谱系之上。奠基文献 Loughran 与 McDonald (2011) 确立了领域专用词典与词频占比口径两大范式, 其研究计划延续至今, Loughran 与 McDonald (2024) 仍以词表与文本计量方法构造企业复杂度测度, 显示词典法在大模型时代依然是金融文本计量的基准工具而非被完全取代的遗产方法。中文语境下, 直接翻译英文词典存在语言与领域双重特异性损失: Du, Huang, Wermers 与 Wu (2022) 系统论证了中文金融文本需要本土化构建的情感词典, 并给出监督式词典构建流程, 该文亦是本管道第四部词典的出处; Ma, Zhang 与 Zhang (2025) 面向中国本土投资者构建细粒度中文金融情感词典 CN-FSD, 说明中文金融词典的构建与校准仍是活跃前沿。本列采用中文主译本而非本土构建词典, 恰好与同管道内 Du 系、姜系等本土词典列形成"译制词表对本土词表"的互证结构, 二者的系统性偏离本身即是一种可测量的信息。方法效度层面, van Atteveldt, van der Velden 与 Boukes (2021) 对人工标注、众包、词典法与机器学习算法的系统比较表明, 词典法效度存在天花板但具备完全透明与零边际成本的独特优势, 这正是本管道坚持词典、LLM、BERT 三方法并行互稳的文献依据; Sun, Yuan 与 Xu (2025) 则展示词典知识可注入预训练语言模型提升金融情感判别, 说明词典信号与深度模型信号互补而非替代。否定处理是词典法负面计数的关键自由度: Pröllochs, Feuerriegel 与 Neumann (2016) 证明否定作用域检测显著改变新闻驱动交易中的情感测量, Punetha 与 Jain (2025) 进一步给出无监督数学框架处理否定难题, 本列分子采用否定翻转后的最终极性正是对这一文献脉络的落实, 而同管道的 negonly 消融臂 (在 score 族上) 则把规则贡献单独暴露供审计。文本即数据的宏观方法论传统由 Hansen, McMahon 与 Prat (2018) 在央行沟通研究中确立, 其以词频与计算语言学方法量化审议内容, 为本管道以词典占比刻画媒体语言强度提供了范式先例。应用侧, 负面新闻语言的预测价值有多重证据: Pham, Huynh, Nguyen 与 Luu (2025) 发现新闻衍生的投资者负面情绪塑造企业财务困境动态, Anastasiou, Katsafados 与 Tzomakas (2026) 以银行文本负面信号预测股价崩盘风险, Li, Yuan, Zhu, Emrouznejad, Hao 与 Jin (2026) 从文本风险披露中还原金融网络关联结构; 就本面板的银行乘金融科技语境而言, Wu, Shen, Wu 与 Shao (2025) 关于中国银行与金融科技公司战略合作影响银行风险承担的证据, 说明媒体对银行金科议题的负面报道强度是有实质经济含义的信息变量。中文媒体语料的供给侧特性亦须纳入解读: Piotroski, Wong 与 Zhang (2017) 证明中国公司新闻存在系统性政治偏差, 负面报道的发生与强度部分受媒体管制结构调节, 这提示本列水平值的跨期比较应控制媒体环境变迁。

【识别策略定位】在多论文组合的识别设计中, 本家族扮演三重角色。其一, 作为词典法负面强度的代表性测度, 它是 LLM 三家投票共识语调 (P1 主处理变量 llm_vote_tone_full) 的确定性稳健性伴测: LLM 测度依赖付费推理与缓存冻结, 词典测度零成本、全透明、可逐词审计, 二者在"银行金科报道的负面性"这一构念上互为校验, 属方法梯子上的并排臂。管道内情感三方法 (LLM、词典、BERT) 互为稳健性、不分主次, 每一方法各自进入 just-identified 的独立规格并排呈现, 铁律是禁止把多方法测度混入同一 over-identified 的 Hansen J 检验——它们测量同一构念, 混入同一矩条件组会制造伪过度识别。其二, 作为下游媒体分歧 (disagreement) 族指标的词级输入: 单词典正负占比是分歧公式的原材料, 本列的测量质量直接传导至分歧测度。其三, 作为负面信息环境的直接代理进入辅助规格: 由于占比水平受文体、题材构成驱动, 推荐用法是置于银行与年份双固定效应之内识别组内变异, 而非跨行比较水平值; 面板深度生产环境为 2007 至 2024 共十八年, 开发盘上仅两年, 年内趋势类推断须以生产语料为准。行宇宙与分母口径上须与 full-only 留篇门控保持一致: n_articles 分母、留篇判定均由全文轨验证结果单独决定, 三轨共享同一篇章集合, 不存在各轨自选样本的选择性偏差通道。从计量性质看, 本列作为解释变量使用时的测量误差结构相对友好: 词典口径的误差来源 (分词、词表覆盖、否定窗口) 均与银行的经济基本面正交, 属经典测量误差, 在线性规格中的后果是系数向零衰减而非方向翻转, 因此用它复现 LLM 主测度的定性结论是保守检验——若衰减后仍显著同号, 结论更稳; 若不显著, 也不能反推主结论失效, 只能说明词典口径信噪比不足, 这一非对称解读须在论文稳健性叙事中写明。另一个识别层面的用法是作调节变量或异质性切割: 按银行-年负面词占比的样本内分位切分高负面与低负面信息环境子样本, 考察主效应的环境依赖性; 由于本列零成本且对全样本近乎无缺失 (仅空文本篇 NaN), 它比依赖缓存命中的 LLM 置信度类变量更适合承担切割角色。与工具变量族的关系上, 本列不充当工具——负面报道强度与银行不可观测冲击直接相关, 不满足排他约束; 管道内的媒体来源风格暴露类工具 (outlet 族) 在构造上刻意绕开了报道内容本身, 二者分工明确, 不可互换。识别接线上还有三处须写明。其一, 跨方法比较的族错误率 (FWER) 控制并非靠本列与 LLM、BERT 测度共入同一矩条件实现, 而由根级 romano-wolf 步降模板专门承担: 情感三方法各自 just-identified 并排产出后, 真正的多重假设校正在跨模型 rwolf 模板里统一处理, paper_spec 内的跨模型声明是声明式文档、运行时无消费者。把词典与 LLM 负面测度塞进同一 over-identified 的 Hansen J 会制造伪过度识别——二者测的是同一构念的不同实现, 矩条件高度相关, 混入后 J 统计量的原假设分布不再有效。其二, full-only 留篇门控 (2026-06-29) 给本列的测量误差结构带来一层意外的洁净: 一篇报道是否计入某银行-年只取决于全文轨 LLM 验证 llm_verified_full, 与词典对该篇的负面词计数无关, 留篇决定与本列取值之间不存在选择性通道, 高负面篇不会因其负面而被系统性纳入或排除, 因而本列在样本内近似随机缺失, 其测量误差可按经典误差处理、后果是系数向零衰减而非方向翻转。其三, 稳健性梯子的完整结构是方法 (LLM / 词典 / BERT) 乘轨道 (full / ctx / ss) 乘词典 (六部) 的笛卡尔积, 本列只是其中一格 (词典法 × 三轨 × loughran); 每一格各自 just-identified 单独进入独立回归, 格与格之间互为稳健性、不分主次, 任意两格严禁并入同一 over-identified 的 Hansen J, 缘由正是它们系同一构念在不同实现下的高度相关矩条件, 混入后过度识别检验的原假设分布失效, 而分歧本身 (方法间、轨道间、词典间) 不是噪声而是由分歧族指标单独测量的信息。

【与相邻测度的构念区分】同前缀与同源列密集, 使用时须严格区分。与 loughran_tone 系 (loughran_tone_full 等) 的区别: 后者是幅度加权自归一化的净语调, 分子为全部命中词最终得分之和、分母为其绝对值之和, 值域负一到正一, 正负相互抵消; 本列是单极占比, 分母为全文词量, 不发生对冲。与 loughran_negonly_tone 系的区别: 后者仍是净语调, 只是把语言学规则消融到仅保留否定翻转的稳健臂; 本家族占比列不进入规则消融梯度——梯度只物化 score 族, 占比列恒在全规则口径下计算一次。与 avg_loughran_pos_ratio 的区别: 严格正极对偶, 同分母同规则, 二者可同时进入一个规格实现正负分离, 但不应相加解读为总情感词密度 (跨类重叠 23 词会被双计)。与 avg_neg_ratio (无词典前缀) 的区别: 后者的计数基是六词典并集经极性多数票消解的固定 union 词典, 兑现 Tetlock (2007)、Garcia (2013)、Henry (2008) 的固定词表构念; 本列则是单一 L&M 译本词表, 二者构成"单词典对并集词典"的稳健性对照。与 avg_msent 的区别: msent 采用词典原始极性的纯计数口径且分母为正负命中数之和, 不含否定翻转; 本列含全语言学规则且分母为全文词量。与 loughran_neg_count 的区别: 该列是银行-年内按篇级词典标签判负的文章计数 (整数, 篇为单位), 本列是词级占比的均值 (连续, 词为单位), 分子分母口径完全不同。与 modal_weak_frac、complexity_frac 的区别: 同一词典的非极性词类占比, 测量语言风格而非情感。与 BERT 族极端负面占比 (xneg_frac 系) 的区别: 后者基于模型概率阈值判篇, 构念是极端负面文章占比而非负面词汇密度。此外本列非 du_2022 词典, 不存在政治词权重梯度变体。再补三组更精细的对照, 它们最易在实证中被误用为同一测度。其一, 与固定 union 词典的正负占比列 (avg_pos_ratio / avg_neg_ratio, 无词典前缀) 的重叠词处理机制根本不同: union 列在构建阶段以极性多数票消解跨类重叠、平票词直接剔除, 使重叠词的极性 margin 守恒、union 逐位不受"保留并两侧计数"改动影响; 本列则对 loughran 词典自身的 23 个不可约简重叠词行两侧计数, 同一词同时进 pos_count 与 neg_count。因此 union 的 neg_ratio 与本列的 loughran_neg_ratio 即便落在同一篇上也非简单的词表子集关系, 而是两套重叠词规约策略 (多数票消解 对 对称双计) 的产物, 二者恰构成"并集固定词表 对 单一译制词表"的稳健性对照。其二, 与其余五部单词典的同名 neg_ratio 列 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 的 neg_ratio 三轨) 的区别只在词表来源、计算口径逐项相同: jiang 与 bian 是 L&M 英文词典的中文本土化翻译扩充, yao 融合年报与社交媒体两域语料, du 含以 0.5 权重计入正侧的政治正面词, you 另带清晰度定/歧义子集; 本列的译制主译本与这些本土构建或扩充词典之间的系统性偏离, 本身由下游分歧族指标测量, 属信息而非噪声。其三, 与本列的正极对偶 avg_loughran_pos_ratio 联立时须记得 23 个双侧词对两个占比列的分子各贡献一次, 同一 token 在分母只计一次, 故两列并非严格互补、其和亦非纯粹的总情感词密度; 正负分离的本意是让二者作为两个独立回归元进入同一规格 (Garcia 2013 意义上的极性解耦), 而非相减合成净指标——净指标已由 loughran_tone 以更规范的自归一化口径承载。

【已知局限与稳健性梯子】第一, 跨语言效度: 译制词表继承英文原典的领域判断, 但中文金融语用与英文并不同构, 某些译词在中文新闻语体中的负面强度可能偏移; 对策是与本土构建的姜系、Du 系、姚系词典占比列并排互证。第二, 分词依赖: jieba 切分粒度与词典词条粒度失配会造成漏配, 版本已冻结以锁死这一测量误差的实现, 使其跨期恒定而非随环境漂移。第三, 否定窗口为定长启发式, 无法覆盖长距离否定与反讽; negonly 与规则梯度臂 (在 score 族上) 提供了规则敏感性的直接证据。第四, 静态词表的时变性: 词典冻结于单一时点, 无法捕捉 2007 至 2024 年间负面用语的语义漂移, 解读长期趋势时应与时变的 LLM、嵌入类测度对照。第五, 聚合为逐篇等权均值, 长文与短文同权, 与按词量加权的替代口径存在构念差异; 篇内占比已除以自身词量, 等权聚合的含义是"平均每篇报道的负面浓度"。第六, 23 个双侧保留词对分子分母的对称贡献轻微抬升占比水平但不引入方向偏误。第七, 开发盘 T 等于 2, 年内与跨年动态在开发环境呈预期退化, 一切分布陈述以生产语料重跑为准, 文档不预填实测数字。稳健性梯子的完整结构是: 三轨 (full、ctx、ss) 乘六词典乘正负两极, 外加 union 固定词表列与三方法梯子; 所有臂互为稳健性、不分主次, 各自 just-identified 并排进入规格, 严禁把任意两臂混入同一 over-identified 的 Hansen J; 轨道间、词典间、方法间的分歧不是噪声而是信息, 由分歧族指标单独测量。第八, 语料供给侧的结构性约束: 输入语料在预处理阶段按媒体类型只保留报纸报道, 通讯社、杂志、政府与网页来源按行剔除, 因此本列测量的是报纸生态内的负面用语强度, 向全媒体环境外推时须谨慎; 同时中国媒体的报道尺度存在政策周期性, 负面词占比的时间序列变异中混有管制松紧的成分, 这与 Piotroski, Wong 与 Zhang (2017) 记录的政治偏差机制同源, 年份固定效应能吸收全行业共同的管制冲击, 但吸收不了管制对不同所有制银行的差异化作用, 后者需要所有制乘年份交互或分组回归来处理。第九, 占比是有界变量, 分布右偏且贴近零值, 极端规格下可考虑对数或分位变换的敏感性检验, 但任何变换臂同样遵循并排铁律, 不与原始占比臂混入同一过度识别检验。第十, 译制词表的规模非对称须纳入解读: loughran 主译本负面词 3,729 个、正面词仅 1,295 个, 这一悬殊比例继承 Loughran 与 McDonald (2011) 关于金融负面词汇更丰富、区分度更高的原始发现, 但庞大的译制负面清单也抬高了中文假阳性风险——某些在英文财务语境判负的词, 直译入中文新闻语体后语义可能中性甚至转正; 对策仍是与本土构建的姜系、姚系、Bian 系负面占比列并排互证, 用词表间的系统性偏离标记潜在的跨语言误配区。第十一, 占比是文体敏感的水平量: 社论、深度报道与快讯的负面词密度基线本就不同, 银行-年内媒体来源构成的漂移会平移本列水平值, 跨来源比较须辅以来源固定效应或媒体来源风格控制, 这与前述语料只保留报纸报道、以及 Piotroski, Wong 与 Zhang (2017) 记录的政治周期性同属供给侧结构约束, 因而水平值的时间序列变异中混有报道尺度松紧的成分, 应优先识别银行与年份双固定效应内的组内变异。第十二, 本列只对否定规则敏感这一数学性质既是简洁性也是局限: 状态机中程度副词与转折连词只等比缩放命中词的得分幅度、不改变其符号, 唯一改变符号的规则是否定翻转, 故本占比列的规则消融在数学上仅有否定与无否定两档, 无否定档的信息已由原始极性口径的 msent 族承载; 这意味着本列无法反映程度强化 (如"严重亏损"相对"亏损") 或转折弱化带来的负面强度层级差异, 若研究关心负面强度的连续变化而非发生密度, 应改用同源的 loughran_tone 幅度加权自归一化净语调, 而规则消融梯度也因此只需在 score 族上物化、无须在本占比族上重复。

## VAR: avg_loughran_neg_ratio_ctx

【变体差分】实体窗轨变体, tier 为 standard。与家族 canonical (全文轨) 的唯一差分在测量文本域: 本列的文章级输入在 content_ctx 上扫描, 即标题 prepend 加目标银行实体的上下文窗口文本, 而非全文正文。构念含义相应收窄为"目标银行实体邻域内的负面词汇密度": 一篇报道可能在与目标银行无关的段落大量使用负面词 (如概述宏观风险、报道他行事件), 全文轨会把这些负面词计入该银行名下, 实体窗轨则通过截取实体邻近文本实现归因降噪, 代价是窗口截断可能丢失照应上下文并缩短分母词量, 使占比方差增大。回退语义: 文章无可用实体窗口时 content_ctx 回退为全文 body 并置 ctx_is_fallback 指示, 回退篇上本列与全文轨仅差标题拼接口径。行宇宙与全文轨完全一致——留篇门控为 full-only, 本列是 conditional-on-full 的条件测度, 不因 ctx 轨自身状况增删任何文章, 分母 n_articles 与全文轨共享, 故两列之差纯粹反映文本域差异而无样本构成差异, 解读时可直接把 ctx 与 full 之差归因于归因窗口而非样本选择。词典、分词器、语言学规则、双侧计数、NaN 契约、六位小数、逐篇等权均值等全部口径与 canonical 逐项相同。用法铁律: 本列与 full、ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排进入独立规格, 禁止混入同一 over-identified 的 Hansen J; 亦不应以三轨相关性高低裁定主次, 相关性高只说明构念稳健, 不改变各轨作为独立稳健性臂的地位。

## VAR: avg_loughran_neg_ratio_full

【变体差分】全文轨列, tier 为 core, 系本家族 canonical 与 headline: 2026-07-10 签核扩围 (类别六扩围第一批) 将其纳入 core 清单, 理据是 L&M 词典负面成分占比是词典法情感测度中谱系最正、信息含量证据最强的分解成分, 而全文轨是三轨中与留篇门控同域的规范轨。测量文本域为 content_full, 即标题 prepend 加全文正文——标题以首句身份参与分词与规则扫描 (标题中的否定、转折同样作用于状态机), 原始内容列不被改写。选择全文轨为 canonical 有三层理由: 其一, 口径一致性——留篇门控本身是 full-only (一篇文章计入面板与否只看 llm_verified_full), 全文轨列的测量域与门控判定域完全重合, 是三轨中唯一无跨轨条件化解读负担的列; 其二, 分母充分性——全文词量最大, 占比估计的篇内抽样噪声最小, 且不受窗口截断与回退混合的影响 (本轨无回退概念, 每篇都有全文); 其三, 与文献口径可比——Loughran 与 McDonald (2011) 及其后继研究的负面词占比均在整篇文档上计算, 全文轨结果可直接与英文文献的量级与效应方向对话。本列的典型用途: 在 P1 语调主线中作 LLM 共识语调的词典法稳健性伴测; 作为媒体分歧族指标的词级输入; 在负面信息环境相关的辅助规格中作直接代理, 建议置于银行与年份双固定效应内使用。与家族内两个姊妹列的关系是并排而非上下位: ctx 轨提供实体归因降噪的稳健版本, ss 轨提供银行金科共现语境的最窄版本, 三者互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified 的 Hansen J。与同为 core 谱系的净语调列 (loughran_tone_full) 的分工: 净语调回答"报道整体偏正还是偏负", 本列回答"负面语言用得有多密", 二者在极性对冲场景下会系统性分离, 联立呈现时应分属不同规格。Stata 侧标签由 stata_export 的 curated 标签映射直接给出而非泛型推断, 保证 dta 层与 codebook 层的口径一致。使用建议再补三点。其一, 与正极对偶列 avg_loughran_pos_ratio_full 联立时应作为两个独立回归元进入同一线性规格 (这正是正负分离设计的本意, 即 Garcia 2013 意义上的极性解耦), 而不要相减合成净指标——净指标已由 loughran_tone_full 以更规范的自归一化口径承载, 手工相减会同时丢失分母口径与规则口径的一致性。其二, 跨方法比较效应量时须先做样本内标准化: 本列的原始方差量级由词典命中率决定, 与 LLM 三分类共识、BERT 概率类测度的方差量级不可比, 直接比较未标准化系数会得出无意义的排序。其三, 门控口径的数值副作用须在论文中如实披露: full-only 留篇门控 (2026-06-29) 使行宇宙相对旧双轨门控收缩, n_articles 及一切按篇均值列的样本构成随之变化, 这是刻意的口径统一而非数据缺陷; 本列在该口径下的准确解读是"通过全文轨验证的银行金科报道中, 平均每篇的 L&M 负面词浓度", 而非"该银行全部媒体曝光的负面性"。补充一点谱系学定位: 本 core 列之所以选负极占比而非正极占比作代表, 直接呼应 Loughran 与 McDonald (2011) 关于金融负面词表信息含量最强的实证结论——正面词易被管理层与公关文本策略性堆砌、信噪比低, 负面词相对稀缺且区分度高, 因此在银行金科议题的媒体审视中, 负面语言密度是更贴近"市场真正在意什么"的信号, 这一点在 Anastasiou, Katsafados 与 Tzomakas (2026) 以银行文本负面信号预测崩盘风险、以及 Pham, Huynh, Nguyen 与 Luu (2025) 以新闻负面情绪刻画财务困境动态的应用中得到独立印证。

## VAR: avg_loughran_neg_ratio_ss

【变体差分】同句轨变体, tier 为 standard, 三轨中文本域最窄的一臂。文章级输入在 content_ss 上扫描: 标题 prepend 加"目标银行与金融科技词出现在同一句"的共现句及其正负一句邻域 (句半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认为一, 与 stage 13 共现硬过滤的 sentence_radius 是两个不同配置键)。构念含义是"银行与金融科技议题直接交汇语境中的负面词汇密度", 即把测量聚焦到报道中真正把目标银行与金科议题绑在同一句谈论的文本片段, 是三轨中对"银行金科关联报道负面性"归因最强、也最激进的口径。回退语义镜像 ctx 轨: 当文章不存在银行与金科词的同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback 为真, 该篇仍留在行宇宙内 (共享 full-only 门控下的 n_articles 分母), 其本列取值退化为近似全文轨口径; 因此本列在篇间是"严格同句邻域"与"回退全文"两种文本域的混合, 解读时可配合 ss_is_fallback 占比评估混合程度。金融科技侧判定为裸 AC 自动机词表匹配, 银行侧含否定与短名过滤, 两侧判定口径刻意不对称。极窄窗口使分母词量急剧缩小, 占比的篇内方差放大, 开发盘小样本上与全文轨差异可能退化, 生产十八年语料上方有稳定推断价值。其余全部计算口径 (词典、规则、双侧计数、NaN 契约、六位小数、逐篇等权聚合) 与 canonical 逐项相同。用法铁律同前: 与 full、ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified 的 Hansen J。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics, Advance online publication. https://doi.org/10.1080/00036846.2025.2536881
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
