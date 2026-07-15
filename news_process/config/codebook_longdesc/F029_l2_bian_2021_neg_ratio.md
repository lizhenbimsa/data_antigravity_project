---
family_id: F029
columns:
- avg_bian_2021_neg_ratio_ctx
- avg_bian_2021_neg_ratio_full
- avg_bian_2021_neg_ratio_ss
unit: 比率 (proportion, 无量纲, 理论值域 [0,1]; 文章级负面词 word-token 占比的银行-年等权均值)
formula: "文章级 bian_2021_neg_ratio{trk} = neg_count_final / n_word_tokens (trk ∈ {_full,_ctx,_ss}; 分子 = 经语言学规则后 final 极性 < 0 的 bian_2021 词典命中 token 数, 极性翻转仅由否定规则驱动; 分母 = 剔除纯标点/纯数字 token 后的 word-token 数, round 6; 空文本或零 word-token → NaN); 面板级 avg_bian_2021_neg_ratio{trk} = mean(bian_2021_neg_ratio{trk}) over 该银行-年留篇集内文章 (等权, skipna)"
producer: pipeline/panel/encode.py::build_aggregation_dict (面板聚合注册) ; pipeline/sentiment/tone_words.py::_analyze_single_article + _compute_sentiment_with_rules (文章级分子分母)
upstream:
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本 + *_is_fallback)
- 21_tone_llms.parquet (llm_verified_full 留篇门控, full-only 口径 2026-06-29)
- 22_words_tone.parquet (bian_2021_neg_ratio_{full,ctx,ss} 文章级中间列)
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
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality"
  venue: Journal of Economics and Development
  vol: 27
  issue: 4
  pages_or_artno: 309-321
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
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
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
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
- doi: "10.1186/s40854-025-00887-5"
  title: "Exploring the relationship between bank liquidity risk and the media sentiment index via big data technology: a study during the COVID-19 pandemic and the Russia–Ukraine conflict"
  authors: "Ullah, M., Sohag, K., & Hassan, M. K."
  year: 2026
  venue: "Financial Innovation"
  type: "journal"
- doi: "10.3390/risks12110171"
  title: "News Sentiment and Liquidity Risk Forecasting: Insights from Iranian Banks"
  authors: "Mirashk, H., Albadvi, A., Kargari, M., & Rastegar, M. A."
  year: 2024
  venue: "Risks"
  type: "journal"
new_dois:
- "10.3390/bdcc9100263"
- 10.1111/jofi.12027
- 10.1111/j.1540-6261.2010.01625.x
- "10.1186/s40854-025-00887-5"
- "10.3390/risks12110171"
---

## CORE

【构念与来源】
本家族测量的构念是「负面词密度」(negative word density): 以 Bian et al. (2021) 构建并公开的中文金融情感词典 (Chinese Financial Sentiment Dictionary, CFSD) 的负面词表为量尺, 统计一篇银行金融科技报道中负面词命中数占该篇有效词数的比例, 再把这一篇章级比率在银行-年单元内取等权算术平均, 得到面板变量 avg_bian_2021_neg_ratio。它回答的问题是: 在给定年份, 媒体谈论某家银行及其金融科技活动的文本里, 负面措辞出现得有多密。与净语调 (net tone) 类测度刻意不同, 本家族只取负面一侧, 属于「正负分离」的单侧密度测度。这一取向有两层学理依据。其一是测量方法上的: Garcia (2013) 证明将正、负面词汇分离为两个独立协变量, 能避免净情感指标里正负两侧相互对冲导致的信息掩蔽——一篇既有大量正面词又有大量负面词的争议性报道, 其净语调可能接近零, 但正、负两侧密度都很高, 分离口径才能保留这一「高强度双向」信息。其二是金融文本的经验事实: Loughran 与 McDonald (2011) 在 10-K 披露文本语境下确立了「负面词表是词典法中信息含量最高的一侧」, 正面词在金融披露里常被管理层用于粉饰、信噪比偏低, 而负面词与后续市场反应的相关最稳健, 其后大量金融文本研究都以负面词占比为首要词典变量。

在中国媒体环境下, 单侧负面口径还有额外的信息经济学理由。Piotroski et al. (2015) 与 Piotroski et al. (2017) 的证据表明, 中国上市主体与媒体之间存在系统性抑制负面信息的激励与渠道: 地方政府与国有股东有动机压制辖内主体的负面报道, 使负面新闻相对稀缺。因而一旦负面措辞出现, 其边际信息含量更高——负面词密度作为解释变量的信号价值, 正建立在这种发布端的不对称之上。这与应用文献的发现相互印证: Anastasiou et al. (2026) 用银行文本的负面信号预测股价崩盘风险, Pham et al. (2025) 证明新闻负面度在有限理性框架下塑造企业困境动态, 两者都说明「银行新闻负面密度」在银行风险研究中有直接可检验的后果。

词典本体方面, CFSD 由 Bian、Jia、Li 与 Yan 四位作者构建并公开, 项目内的单一权威来源是 config/tone_dicts.json 的 bian_2021 条目 (凡使用该词典一律以 tone_dicts.json 为准, 不读上游 xlsx 源料): 原始词表含 2,595 个词条, 每词标注二值极性 (1 为正面、负 1 为负面), 清洗去重后为 2,595 个唯一词汇, 其中正面词 1,107 个、负面词 1,488 个; 正负两类之和恰好等于唯一词数, 说明该词典不存在跨极性重叠词。谱系上它是 Loughran-McDonald 2011 英文金融词典范式的中文本土化平行努力, 与项目内另外五部词典 (jiang_2021、yao_2021、du_2022、you_2018、loughran 中文主译本) 并列为六部互为稳健性的词典量尺。选择「密度」而非「计数」作为篇章级原语, 出于两点测量考虑。第一, 原始负面词计数与篇幅机械正相关, 长文天然计数更高, 以有效词数为分母的比率把篇幅异质性从测度中剥离, 使长短报道在银行-年均值中携带可比信息。第二, 编辑在有限版面内反复选用负面词汇本身是一种强度信号, 密度口径恰好捕捉「单位篇幅内的负面浓度」。命名口径需要一处披露: 项目内部键名 bian_2021 锚定的是 SSRN 编号 3446388 工作论文 2021 年 6 月版本; 该词典更早的流通版本以 2019 年命名 (数据仓库路径即以 2019 标注), 引用与复现时应以本 codebook 与 tone_dicts.json 登记的 2021 年版次为准, 避免年份口径漂移。

【方法学与计算】
计算链条分文章级与面板级两层, 全程零 LLM、零联网、零成本, 确定性由冻结的 jieba 0.42.1 分词器与词典文件共同保证。上游链路: stage 14 (ctx_materializer) 先把每篇文章物化为三条文本轨 content_full、content_ctx、content_ss (均为标题 prepend 后拼接, 原始「内容」列不动); stage 21 完成 LLM 语义精筛并给出 llm_verified_full 留篇标记; stage 22 (tone_words) 再对每条轨计分。文章级实现在 pipeline/sentiment/tone_words.py 的 _analyze_single_article: 它先用一个独立的 tone tokenizer 对文本分词 (领域词注入只作用于这个私有分词器, 不污染全局 jieba 状态, 保证与其它阶段的分词互不干扰), 然后对每部词典调用语言学规则状态机 _compute_sentiment_with_rules。该状态机逐 token 维护三个状态: 否定窗口 (命中否定词后, 其后 NEGATION_WINDOW 等于 2 个分词单元内的情感词极性翻转)、程度副词倍率 (多档权重, 极强档如「极其」乘 3.0、减弱档如「有些」乘小于 1.0, 命中情感词时消费并重置为 1.0)、转折激活标志 (转折连词后的情感词幅度乘 ADVERSATIVE_BOOST 默认 1.5, 句末标点重置全部状态, 即规则作用域限定在从句层级)。

对本家族至关重要的一点是分子的归类口径: 一个 token 记入负面计数 neg_count, 当且仅当其经全部规则处理后的最终得分 final_score 严格小于零。三条规则里只有否定翻转会改变符号 (base_score 取负号), 程度与转折都是严格正乘子, 只缩放幅度、永不改变极性。因此否定规则对本测度有实质影响——词典里的正面词被否定后其 final_score 转负、计入负面分子, 负面词被否定后转正、移出负面分子——这正是 Pröllochs et al. (2016) 所论证的否定作用域处理对新闻驱动决策的价值所在; 而程度与转折规则对分子计数完全中性 (它们不改符号, 故永不改变某 token 是否被计入 neg_count, 只会改变净语调 tone 的幅度)。bian_2021 词典不含跨极性重叠词 (正负两类词数之和恰等于唯一词数), 故状态机里针对「两侧计数」的消歧分支对本词典是空集、从不触发。分母是 word-token 数: 分词结果中剔除纯标点与纯数字 token 后的词数, 与 Loughran-McDonald 谱系「占词数之比」的分母口径对齐 (盘上实测纯标点与数字 token 占比逐篇波动明显且非常数, 若不剔除会引入非经典测量误差式的稀释)。比率经四舍五入保留六位小数; 空文本、纯符号文本或零 word-token 情形返回 NaN 缺测, 词典整体缺失时同样返回 NaN 而非零——「测不到」与「没有负面词」在数据里被刻意区分为两种状态。

面板级实现在 pipeline/panel/encode.py 的 build_aggregation_dict (Section M): 对六部词典乘三条文本轨各注册一条 mean 聚合规则, avg_bian_2021_neg_ratio 及其 _ctx、_ss 轨后缀变体等于该银行-年留篇集内全部文章篇章级比率的等权算术平均 (pandas mean 自动跳过 NaN 篇), 每篇一票、不按篇幅或词数加权。需注意: 只有 union 口径的 avg_neg_ratio 另配了 _std 组内离散度孪生列, 单词典的 avg_bian_2021_neg_ratio 只做 mean 聚合、无 _std 孪生。行宇宙口径遵循 2026-06-29 的 full-only 留篇门控: 一篇文章是否计入「银行金融科技报道」只看 llm_verified_full 是否为真, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。下游消费: 本族与镜像列 avg_bian_2021_pos_ratio 一起, 作为词级情感分歧指数 disag_bian_2021 (三轨) 的直接输入。分歧指数采用经典的看涨-看跌一致性指数 (agreement/disagreement index) 构造, 由正、负两侧占比按「1 减去 (正占比减负占比) 除以 (正占比加负占比) 之商的平方, 再开平方」合成, 取值落在 0 与 1 之间, 正负相等时分歧最大、单极 (全正或全负) 时分歧为零, 分母为零时返回 NaN。这也是 encode 层把单词典正负比率分离聚合的首要设计动机。值得强调的是, 本族的确定性不依赖任何缓存或联网: 与 LLM 情感轨须命中盘上 _llm_cache.db 才能离线复现不同, 词典法完全由冻结的分词器版本与词典文件决定, 无论是否设置离线守卫环境变量, 同一份文本必然得到逐字节相同的负面密度。这一性质使本族成为整条情感测度链上审稿人最易独立验证的一环: 只要拿到原始文本、tone_dicts.json 与固定版本的 jieba, 任何第三方都能在无成本、无外部依赖的条件下重算并逐值核对本列, 因此它在稳健性表里承担的正是「零自由度、零成本的机械对照」角色。

【文献定位】
本家族在文献谱系上位于三条线索的交汇处。第一条是金融文本词典法的经典脉络: 自 Loughran 与 McDonald (2011) 确立领域专用词表与负面侧优先的范式以来, 词典法因其完全透明、可审计、任何人重跑结果逐字节一致的特性, 一直是金融文本测度的基准方法; Hansen et al. (2018) 在央行沟通研究中同样强调计算语言学测度的可复现性是其进入经济学识别链条的前提。Garcia (2013) 则在此谱系内补上「正负分离优于净值」这一测量论断, 直接为本家族只取负面一侧的设计背书。第二条是中文金融词典的本土化竞争。通用中文情感词典在金融语境下误判严重, Du et al. (2022) 系统论证了语言与领域双重特异性的必要性, 并构建了含政治正面词的中文金融词典; Bian et al. (2021) 的 CFSD 是同期平行努力之一; Ma et al. (2025) 的 CN-FSD 进一步做细粒度分级, 把情感强度从二值扩展到多档; Sun et al. (2025) 则展示词典知识可以注入预训练语言模型形成词典-神经混合方法。本项目同时装载六部词典而非择一, 正是对「词典选择本身构成研究者自由度」这一批评的制度化回应: 六部词典的同名负面密度列并排, 使读者能直接读出主结论对词典选择的敏感性。第三条是方法效度与负面信号的应用文献。van Atteveldt et al. (2021) 的系统比较表明, 词典法的效度普遍低于人工标注与有监督机器学习, 这一结果构成本项目「词典法只作 LLM 主测度的旁证轨、绝不单独承重」的方法论依据; Punetha 与 Jain (2025) 说明否定处理仍是词典式情感分析的活跃改进方向, 支持本管道在纯词频之上叠加否定状态机的选择; 应用端, Anastasiou et al. (2026) 与 Pham et al. (2025) 分别在崩盘风险与困境动态两个后果变量上验证了新闻负面度的预测力, 说明本家族测量的构念在银行风险实证中确有落点。

【识别策略定位】
在识别链条中, 本家族是处理变量侧的稳健性测度, 而非任何一篇论文的 canonical 处理变量。项目主线的 canonical 情感测度是 LLM 三家投票的 llm_vote_tone_full; 词典法六部词典 (含 bian_2021) 与 BERT 三模型构成两条平行的替代方法族, 三方法互为三角验证: 若 LLM 测得的银行情感效应在词典负面密度上重现同号显著, 则主结论不由 LLM 这一具体测量工具驱动。要把「测量稳健性」与「规格稳健性」两个层次分清, 因为本族同时横跨两者。相对于 canonical 的 LLM 语调, 用 bian_2021 负面密度替换处理变量、其余回归骨架 (固定效应、控制变量、样本、工具变量) 一律不动, 检验系数符号与显著性是否重现——这是测量工具替换意义上的稳健性, 针对的正是审稿人最常见的顾虑: LLM 判定可能被提示词、模型版本或厂商特异性驱动, 而一台完全机械、零自由度、逐字节可复现的词典扫描若能给出同号结论, 这一顾虑即被直接消解。在本族内部, 六部词典乘三条文本轨乘正负两侧构成的密度阵列则属于规格稳健性: 它们不是对同一潜构念换用不同仪器, 而是对「用哪部词表、扫哪段文本、取哪一侧」这些研究者自由度做穷举并排, 每个变体各自独立入模。bian_2021 负面密度在替代方法角色中有两点比较优势: 其一是完全确定性与零成本, 不依赖付费 API 与缓存, 审稿人可在任何机器上逐字节复现; 其二是构念上最接近 Loughran-McDonald 传统, 与英文文献的负面词占比变量可直接对话。

本族在识别上还有一处常被忽略却要害的性质: 因行宇宙遵循 full-only 留篇门控 (2026-06-29), 本列与 canonical 的 llm_vote_tone_full 建立在同一份留篇样本上——两者的银行-年观测集合逐行一致。这意味着用本列替换 LLM 语调做稳健性时, 估计样本的构成完全不变, 从而把「测量工具差异」与「样本选择差异」两个混淆源干净剥离: 若结论仍稳健, 可确证效应源自被测情感的实质, 而非某种测量工具与样本构成的交互。ctx 与 ss 是该留篇集上的 conditional-on-full 收窄轨, 其行宇宙是 full 留篇集的子集, 因而三轨之间的比较同样是在受控样本上进行的窗口敏感性读数, 而非跨样本的混合比较。

使用时须严守项目的口径铁律。三条文本轨 full、ctx、ss 各自 just-identified 并排、互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 检验; 六部词典之间、正负两侧比率之间同理, 每个变体各进各的回归规格, 不得把多个变体同时塞进一个过度识别的矩条件集合。词典族属于「规格稳健性并排」性质: 跨模型 FWER 校正模板 (rwolf) 只覆盖同构念替代 headline 测量的场景, 词典乘轨道的密度族不进入该矩阵, 报告时以逐规格并排表呈现即可, 不设专门的 family-wise 校正模板。另须注意水平不可比问题。六部词典负面词表规模差异可达数倍 (bian_2021 负面词 1,488 个在六部中属最精简一档), 密度水平天然不同, 跨词典比较只看标准化系数与符号方向, 不比原始水平; 同理三轨分母长度悬殊 (full 覆盖全文、ctx 收窄到实体窗、ss 收窄到共现句邻域), 轨间也只比方向与显著性形态, 不比密度绝对值。正因如此, 本族在稳健性表里的规范呈现方式是「符号-显著性一致性矩阵」而非系数量级横比: 读者据此判断主效应是否在词表选择、文本窗口、极性侧三个自由度的全部组合下保持定性稳定, 而不被任何单一测量约定驱动。

【与相邻测度的构念区分】
本家族与若干形近列的边界必须逐一划清, 否则极易在建模与解读时张冠李戴。

与 bian_2021_tone (三轨) 的区别是分子分母双重的: tone 是净语调, 分子为全部命中词 final 得分之代数和、分母为加权幅度绝对值之和, 自归一化到负 1 与正 1 之间, 度量「已命中词内部的净极性强度」, 属集约边际 (intensive margin); neg_ratio 的分母是全篇 word-token 数, 度量「负面词相对全文长度的覆盖密度」, 属广延边际 (extensive margin)。一篇通篇平淡、只在结尾出现两个负面词的长文, 其 tone 可能极负而 neg_ratio 接近零; 反之一篇负面词密集但正面词同样密集的争议报道, neg_ratio 很高而 tone 因正负对冲可能接近零。两者相关但绝非同构念, 同表并置时须分别标注为集约边际净极性与广延边际密度。

与 bian_2021_negonly_tone 的区别尤须点明, 因为二者同时含「bian_2021」与「neg」两个字符, 极易误认。negonly_tone 是规则消融梯度里「仅保留否定规则」档的净语调, 仍是带符号、自归一化到正负 1 之间的强度测度; neg_ratio 是全语言学规则下负面命中词的计数密度。前者回答「在只开否定规则时净极性有多强」, 后者回答「负面词占全文多大比例」, 分子口径 (代数和 vs 计数)、分母口径 (加权幅度和 vs word-token 数)、值域 (正负 1 vs 0 到 1) 三者皆异, 不可互相代入。

与无词典前缀的 avg_neg_ratio 的区别在分子词表: 后者的计数基是六词典固定 union 词典 (并集加重叠词极性多数票消解、平票剔除), 是全样本统一的固定词表, 兑现固定词表情感构念 (Garcia 2013 谱系, 全样本单一词表的经典设计); 本列只用 bian_2021 单一词表, 是 union 口径的单词典分解臂; 二者聚合层也有差异, union 的 avg_neg_ratio 另有 _std 组内离散度孪生, 单词典本列无。

与镜像列 avg_bian_2021_pos_ratio 的关系需澄清一个常见误解: 二者共享同一 word-token 分母、极性侧相反, 但并非简单互补 (两侧之和不恒等于命中密度, 更不等于 1)——否定规则会把被否定的正面词从正侧计数移入负侧、把被否定的负面词反向移出, 故正负两侧的计数并非仅由裸词频决定; 加之中性词与未命中词大量存在, 两侧之和远小于全文长度。二者是下游 disag_bian_2021 词级分歧指数的成对输入, 本列是其负侧输入, 而非分歧指数本身, 引用时勿把 neg_ratio 与 disag 混为一谈。

与 msent_score 族的区别在规则口径: msent 按原始词典极性 (base 字段) 计数、零语言学规则, 而本列分子按 final 极性、经否定翻转; 两者对「不良贷款没有恶化」这类含否定的句子分类相反。与 LLM/BERT 侧的 neg_count、xneg_frac 族的区别在计数单位: 那些是篇章级分类计数 (多少篇被判负面), 本列是词级密度 (一篇之内负面词有多密), 聚合后构念不同。与 industry_neg_shock 的区别在主体: 后者是同业其他银行负面篇占比的 leave-one-out 均值, 度量同业冲击暴露, 与本列的自身密度构念正交。最后, 规则消融梯度 (raw、negonly 等七变体) 与政治词权重梯度只对 score 族物化, 比率族不设这些消融变体——本列只在全规则口径下存在, 引用时勿虚构 bian_2021_neg_ratio_negonly 之类不存在的列名; 面板层本族亦只有 mean 聚合的 avg_bian_2021_neg_ratio 三轨列, 无 sum 或 _std 孪生列。

【已知局限与稳健性梯子】
第一, 词表覆盖有限: bian_2021 负面词 1,488 个, 在六部词典中属于最精简的一档, 覆盖不足会造成密度系统性偏低与漏报; 对策是六词典并排, 同一回归换用其余五部词典的同名密度列, 检验符号与显著性是否稳定。第二, 分词依赖: 词典命中要求 jieba 切分粒度与词条一致, 切分漂移会直接改变分子; 管道以 jieba 0.42.1 版本冻结加独立 tone tokenizer 隔离来锁死这一自由度, 复现时不得升级分词器。须补充的是, 领域词注入只作用于计分用的私有 tokenizer、不污染全局 jieba 状态, 这既保证与其它阶段分词互不干扰, 也意味着注入词表本身构成一处隐性自由度: 若未来调整领域词表, 分词边界改变会连带改变词典命中, 故领域词表与分词器版本须同步冻结、一并披露, 不可只声明 jieba 版本而略过注入词表。

第三, 二值极性: CFSD 词条只有正、负 1 两档, 无强度分级, 「亏损」与「破产」同权; 这是词典本体属性, 由 LLM 与 BERT 的连续得分轨在方法族层面补偿, 也正是 Ma et al. (2025) 细粒度词典与 Sun et al. (2025) 词典-神经混合方法所针对的局限。第四, 语域迁移误差: CFSD 构建于会计与金融文本语料, 而本管道扫描的是媒体新闻语料, 两种语域在措辞习惯、行话密度与修辞方式上存在差异, 词表在新闻语域下的命中精度未必等同于其在原始建构语域的表现, 这一语域-构念错配是所有词典法移植使用的共性风险 (van Atteveldt et al. 2021), 只能靠与 LLM、BERT 方法族的三角一致性来约束, 不能靠词典法自证。

第五, 等权篇均的小样本噪声: 报道量极少的银行-年, 单篇极端值即可主导均值 (本族不设最小篇数守门, 与 industry_neg_shock 默认按最小有效篇数守门的口径不同), 且密度测度对极短文本尤其敏感——一篇仅数个 word-token 的短文若恰含一个负面词, 其比率会出现尖峰, 在等权平均下被过度加权; 回归中应控制报道量、或对低篇数单元做敏感性剔除、或在文章级做缩尾。第六, 回退语义带来的轨间收敛: ss 轨镜像 ctx 的回退设计, 无银行与金科同句共现的文章其 content_ss 回退为全文 body 并打 fallback 标记, 这类行上 ss 密度与 full 密度机械趋同, 属设计内语义而非泄漏, 严格窗口子样本分析应按 fallback 标记切分。第七, 语用盲区: 否定窗口仅两个分词单元, 长程否定、反讽、引述他人负面言论等均超出词典法能力 (Punetha 与 Jain 2025), 故本列结论只在与 LLM、BERT 轨一致时才可承重。第八, 命名年份口径: 项目键名 bian_2021 锚定 SSRN 3446388 的 2021 年 6 月版本, 而该词典早期以 2019 年在数据仓库流通, 复现与引用须统一以本 codebook 登记的版次为准, 避免年份漂移导致误取不同词表快照。近期应用文献进一步印证了负面词密度对银行风险的预警效度: Ullah, Sohag, & Hassan (2026, Financial Innovation) 用大数据技术构建媒体正负情感指数, 发现负面情感指数与银行流动性风险显著正相关, 支持负面词密度作为银行风险预警信号的效度; Mirashk, Albadvi, Kargari, & Rastegar (2024, Risks) 以伊朗银行海量经济新闻为语料, 验证新闻情感 (含负面测度) 对银行流动性覆盖率方向性预测的增量信息含量。

稳健性梯子汇总: 词典维度六臂、文本轨道三臂、极性侧两臂 (与 pos_ratio 镜像)、方法族三臂 (词典、LLM、BERT), 各梯子正交不交叉、各臂各自 just-identified 并排、互为稳健性不分主次, 一律禁混进同一 over-identified Hansen J——尤其禁止把六词典或三轨的密度列同时纳入一个过度识别的 GMM 矩条件集合。开发盘 T 等于 2 的试跑环境下轨间零方差或整列缺测属预期退化, 生产口径以 T 等于 18 全量语料为准。

## VAR: avg_bian_2021_neg_ratio_ctx

【变体差分】
本列是家族的实体窗口轨 (ctx) 变体, tier 为 standard。与 canonical 的 full 轨唯一差分在被扫描文本: 分词与计分对象是 content_ctx, 即标题 prepend 后拼接的目标银行实体窗口文本——只保留报道中围绕目标银行实体出现位置的邻近窗口, 剔除同篇中与该银行无关的段落。测量意图是归因收紧: 一篇报道可能同时评论多家机构或穿插宏观叙事, full 轨会把针对他行或行业整体的负面措辞计入本行密度, ctx 轨把分子分母同时限制在银行邻域, 降低这类归因噪声。需要注意两点非直觉性质。其一, ctx 密度不是 full 密度的单调子集——分母随窗口收窄大幅缩小, 若负面词恰好集中在银行邻域, ctx 密度可以高于 full。其二, 无法定位实体窗口的文章按回退语义以全文替代并打 fallback 标记, 这些行上 ctx 与 full 机械相等, 严格窗口分析须按标记切分。行宇宙是 conditional-on-full: 留篇与否由 llm_verified_full 单独决定, 本列只改变已留篇文章的测度口径, 不改变哪些文章入样。口径铁律照适用: ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 本列同时是 disag_bian_2021_ctx 的负侧输入, 亦是六词典 ctx 轨负面密度族的 bian 分解臂。

## VAR: avg_bian_2021_neg_ratio_full

【变体差分】
本列是家族的 canonical 列与唯一 core 列 (签核口径: 类别 6 扩围①, 词典 bian_2021 负面成分占比的 canonical full 轨, Loughran-McDonald 谱系的分解成分)。差分语义: 被扫描文本为 content_full, 即标题 prepend 后的完整正文——三轨中覆盖最宽的口径, 度量整篇报道的总体负面词密度, 包括与目标银行不直接相关的段落与背景叙述。选择 full 轨作 canonical 有三层理由。第一是与门控口径的自洽: 2026-06-29 起留篇门控为 full-only, 一篇文章是否算「银行金融科技报道」只看 llm_verified_full, 因此 full 轨测度的行宇宙与门控判据同轨, 分母定义最干净; ctx 与 ss 是该留篇集上的 conditional-on-full 收窄轨, 其行宇宙是 full 留篇集的子集。第二是与文献的可比性: 英文文献的负面词占比变量 (Loughran 与 McDonald 2011 谱系, 及 Garcia 2013 的正负分离设计) 均以全文为分母, full 轨与其构念对齐, 便于系数量级对话; 项目主线 P1 的处理变量 llm_vote_tone_full 亦为 full 轨, 本列作其词典法稳健臂时两者口径同轨、不引入轨道混淆。第三是回退中性: full 轨不存在回退语义, 每篇文章的取值都来自真实全文, 无 fallback 行与非 fallback 行的异质混合, 这使 full 轨成为三轨中唯一没有机械趋同污染的口径。使用建议: 作为 P1 语调效应的词典法负侧稳健臂时, 与镜像列 avg_bian_2021_pos_ratio_full 分别进入两条独立回归规格 (正负分离、不合成净值, 兑现 Garcia 2013 的分离设计), 或经 disag_bian_2021_full 以分歧构念入模; 跨词典横比时只比标准化系数, 因 bian_2021 负面词表规模在六部词典中最精简 (负面词 1,488 个), 密度水平系统性偏低、不可直接比水平; 与 bian_2021_tone_full 同表呈现时应注明两者分别是广延边际密度与集约边际净极性, 相关但不同构念。进一步说明本轨作为 core 列的测量含义: 全文口径把一篇报道视为对该银行整体舆论环境的一次快照, 既包含直接点名银行的负面评价, 也包含行业背景、监管风向、宏观形势等间接施压于该银行的负面语境; 在银行声誉与风险传染研究里, 这种「广谱负面暴露」往往比仅锁定实体邻域的窄口径更贴近投资者实际接收到的信息总量, 因为读者读的是整篇而非只读银行段落。正因如此, 本列在与收窄轨并排时通常承担「上界暴露」的角色: 若某效应在最宽的 full 轨上显著、在逐步收窄的 ctx 与 ss 轨上衰减, 可读作负面语境的作用主要来自泛化背景而非银行专属叙述; 反之若效应在收窄轨上反而增强, 则提示负面信号高度聚焦于银行与金融科技议题的直接交汇处。这种「随窗口收窄的单调性读数」只在三轨并排、各自独立入模时才成立, 严禁把三轨塞进同一过度识别方程后再解读其相对大小。就小样本行为而言, 全文口径的分母通常最大, 单篇比率的方差相对最小, 因而在报道量偏低的银行-年上, full 轨的等权篇均比 ctx 与 ss 轨更稳定、更少被极短文本的零一跳变主导; 但这不改变本族不设最小篇数守门的事实, 低报道量单元仍应在回归层面以报道量控制或子样本剔除处理。缺失语义在面板层还有一处契约须写明: 零报道的银行-年行在面板补全时, 计数族列 (n_articles 前缀全族) 按契约填 0, 而本列属于比例与情感类, 按同一契约保持 NaN 不填 0——「该年没有报道」与「该年报道的负面密度为零」是两种不同状态, 建模时不可把本列的缺测当零处理, 也不可用零填充制造虚假的低负面观测; 需要区分两者时应以同行的 n_articles 计数列为条件变量。下游消费还有一条链路值得点名: 面板层的 disag_bian_2021_full 分歧指数即以本列与镜像正侧列为成对输入, 按看涨-看跌一致性公式合成, 其分母为正负两侧密度之和、和为零时返回 NaN, 因此本列的缺失与零值会沿该链路传导, 解读分歧指数的缺测时应回溯到本列这一侧的输入状态。铁律复述: 本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 与其余五部词典的同名 full 列亦然, 一律禁混进同一 over-identified Hansen J; 词典族属规格稳健性并排, 不进入跨模型 rwolf 的 FWER 矩阵。

## VAR: avg_bian_2021_neg_ratio_ss

【变体差分】
本列是家族的同句轨 (ss) 变体, tier 为 standard, 是三轨中归因口径最严的一档。差分语义: 被扫描文本为 content_ss, 即标题 prepend 后拼接「目标银行与金融科技词在同一句共现」的句子及其正负一句邻域 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。测量意图是把负面词密度锚定到银行与金融科技议题直接交汇的最小语篇单元: 只有出现在共现句邻域内的负面措辞才进入分子分母, 最大限度排除同篇中他行评论、宏观背景与无关板块的污染。回退语义镜像 ctx 且必须原样陈述: 全篇不存在银行与金科同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback 为真, 与主轨共享 n_articles 分母; 这些回退行上 ss 密度与全文密度机械趋同, 属设计内优雅降级而非数据错误, 严格同句子样本分析应剔除 fallback 行。两处易混口径须区分: 其一, 本轨的同句判据与 stage 13 共现硬过滤的 sentence_radius 是两个不同的 config 键、两套不同原语 (前者对应严格同句的 extract_bank_fintech_cooccurrence, 后者对应邻近窗口的 has_bank_fintech_cooccurrence_within_radius), 禁互相复用解读; 其二, ss 后缀是文本轨后缀, 与网络指标族的 _sent 判据后缀无关。行宇宙同为 conditional-on-full 子集。铁律照适用: ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 开发盘 T 等于 2 环境下 ss 轨可能整列退化为缺测或零方差, 属预期现象, 生产推断以 T 等于 18 为准。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Ullah, M., Sohag, K., & Hassan, M. K. (2026). Exploring the relationship between bank liquidity risk and the media sentiment index via big data technology: a study during the COVID-19 pandemic and the Russia–Ukraine conflict. Financial Innovation. https://doi.org/10.1186/s40854-025-00887-5
Mirashk, H., Albadvi, A., Kargari, M., & Rastegar, M. A. (2024). News Sentiment and Liquidity Risk Forecasting: Insights from Iranian Banks. Risks. https://doi.org/10.3390/risks12110171
<!-- rendered-citations:end -->
