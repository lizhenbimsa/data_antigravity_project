---
family_id: F359
columns:
- jiang_2021_tone_app_ctx
- jiang_2021_tone_app_full
- jiang_2021_tone_app_ss
- jiang_2021_tone_ctx
- jiang_2021_tone_full
- jiang_2021_tone_hw_ctx
- jiang_2021_tone_hw_full
- jiang_2021_tone_hw_ss
- jiang_2021_tone_mw_ctx
- jiang_2021_tone_mw_full
- jiang_2021_tone_mw_ss
- jiang_2021_tone_ss
- jiang_2021_tone_std_ctx
- jiang_2021_tone_std_full
- jiang_2021_tone_std_ss
- jiang_2021_tone_tech_ctx
- jiang_2021_tone_tech_full
- jiang_2021_tone_tech_ss
- jiang_2021_tone_vw_ctx
- jiang_2021_tone_vw_full
- jiang_2021_tone_vw_ss
unit: 语调得分 (无量纲, 连续, 约 [-1,1]; bank-year 聚合后为文章级得分的均值或加权均值; _std 变体为 bank-year 标准差)
formula: "jiang_2021_score{track} = (Σ pos_final − Σ neg_final) / (Σ |final|), 经否定翻转/程度副词/转折三规则后自归一化 ∈ [−1,1]; jiang_2021_tone{track} = mean_over_articles(jiang_2021_score{track}); 加权变体 _vw/_mw/_hw = Σ(score·w)/Σw (w 分别取 mention_density / media_authority_weight / herd_weight); _std = bank-year SD; _tech/_app = 仅在 locus 分类为底层技术/应用场景子集上求均值"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (canonical/_std/_vw/_mw/_hw 聚合 + _tech/_app locus 分类聚合块, tech/app 子集由 innovation_locus_full 单轨标签切分); 文章级得分源 news_process/pipeline/sentiment/tone_words.py::classify_batch (stage 22)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_score{track}, jiang_2021_score_w{track})
- 24_herd_decay_processor.parquet (herd_weight_full / herd_weight_ctx / herd_weight_ss, 供 _hw 变体)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: "10.1016/j.iref.2024.01.067"
  type: "journal"
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, & 唐国豪
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
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.irfa.2023.102610"
  title: "The annual report tone and return Comovement—Evidence from China's stock market"
  authors: "Liu, C., Wang, F., & Xue, W."
  year: 2023
  venue: "International Review of Financial Analysis"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
- "10.1016/j.iref.2024.01.067"
- "10.1016/j.irfa.2023.102610"
- "10.1016/j.ememar.2024.101234"
---

## CORE

该文用文本分析方法构建中国银行层面媒体情绪指数,发现负面媒体情绪通过挤兑存款、迫使银行提高同业拆借依赖等渠道显著推高银行系统性风险。

【构念与来源】
本家族测度的是"以姜富伟等 (2021) 中文财经情绪词典对银行金融科技相关新闻文本打分、再聚合到银行-年层面的语调倾向"。构念上, 它属于媒体语调 (media tone) 家族: 把一篇报道对目标银行金融科技活动的褒贬态度压缩成一个约在 [−1,1] 区间的连续标量, 正值表示叙事偏乐观、负值表示偏悲观、接近零表示中性或褒贬相抵。之所以专门保留这一部词典的一整族列, 是因为中文财经文本的情感极性高度依赖领域词与本土表达习惯, 单一词典的选择本身就是一个需要经受住稳健性检验的研究者自由度; 姜富伟等 (2021) 词典是国内财经文本情绪研究广泛使用的一部中文金融情感词表, 与 you et al. (2018)、bian et al. (2021)、du et al. (2022)、yao et al. (2021) 及中文主译版 loughran and mcdonald (2011) 六部词典并排, 构成一个"跨词典互为稳健性"的证据梯子。

数据来源链条清晰。原始语料是经预处理、银行实体识别、金融科技词识别与共现硬过滤 (stage 13) 之后保留下来的"目标银行与至少一个金融科技词邻近共现"的报道; stage 14 (ctx_materializer) 把每篇报道物化成三条并行文本 (content_full = 标题 prepend 全文正文; content_ctx = 标题加实体上下文窗口; content_ss = 标题加银行与金融科技同句共现的正负若干句窗口); stage 22 (tone_words) 用姜富伟等 (2021) 词典对三条文本各自独立扫描打分, 产出文章级 jiang_2021_score{track}; 最后在 stage 40 的面板聚合环节 (encode.aggregate_panel) 把文章级得分按银行-年分组聚合成本家族的各列。canonical 无后缀列 jiang_2021_tone_full 就是"该银行该年全部留篇报道的 full 轨得分算术平均"。

需要强调的是, 本家族的原始信号并非直接来自任意中文新闻, 而是来自共现硬过滤后聚焦"银行 × 金融科技"的语料池, 因此这里的"语调"始终是有条件的: 它度量的是"在媒体谈及某银行金融科技相关活动时所流露的褒贬态度", 而非该银行的一般性媒体形象。这一条件性使得本家族与项目其它更宽口径的情感变量在语义上不可互替, 使用时必须记住其分母是"留篇报道数"而非"全部提及该银行的报道数"。姜富伟等 (2021) 词典之所以被纳入六部并排词典, 一方面因为它面向中文财经文本、对本土表达与领域术语的覆盖优于通用中文情感词表, 另一方面因为在跨词典稳健性设计里, 每多一部独立构建、来源与构造逻辑不同的词典, 就多一条能证伪"结论由单一词表人为驱动"的证据线; 六部词典彼此的构造语料、极性判定方法与更新年代各异, 恰好提供了这种异质性。

【方法学与计算】
文章级打分遵循基于状态机的三条语言学规则, 而非朴素的正负词计数。分词后逐词匹配词典, 命中正面词记基分 +1、命中负面词记基分 −1; 在此之上叠加: 否定规则 (前置否定词翻转其后情感词极性)、程度副词规则 (根据程度副词的强弱等级放大或缩小该情感词幅度)、转折规则 (转折连词后的从句权重上调, 体现"话锋一转"承载的真实态度)。所有规则作用完毕后, 文章得分 = (正向最终值之和 − 负向最终值之和) / (最终值绝对值之和), 从而自归一化到约 [−1,1], 与文本长度解耦。这一"幅度归一化"口径不同于纯词频计数口径 (后者对应 avg_msent 一类零规则测度)。

三条语言学规则的引入是为了逼近人类读者对财经文本态度的真实理解, 而非机械计数。否定规则处理"并未改善""不容乐观"这类结构, 若不翻转极性, 纯计数会把"未见好转"误判为正面; 程度副词规则区分"略有回暖"与"大幅回暖", 前者幅度小、后者幅度大, 使同一情感词在不同修饰下贡献不同权重; 转折规则处理"虽然……但是……"这类句式, 把话锋转折之后的从句视为承载真实态度的主句而上调权重, 避免被前半句的表面基调误导。这三条规则与 loughran and mcdonald (2011) 强调"金融文本的情感必须结合上下文与否定" 的精神一致, 也与 barbaglia et al. (2025) 在经济文本上强调规则处理对词典法效力至关重要的发现相呼应。需要指出的是, 规则的叠加使得得分并非各词贡献的简单可加分解, 相邻规则组合之间高度共线, 因此项目在别处专门物化了规则消融梯度 (rule-ablation) 供审计, 而本家族一律采用全规则口径 (full 规则), 即三条规则全部启用后的归一化得分, 与消融变体正交、不交叉。此外, 分词依赖冻结版 jieba (0.42.1), 词典本身也字节级冻结, 保证同一文本在不同运行下打分完全可复现, 这是本家族相对语义模型测度的一大工程优势。

聚合层面, 本家族在 canonical 均值之外系统地物化了若干正交的聚合变体, 每一个都对应一条独立的稳健性维度。三轨 (full/ctx/ss) 是文本粒度维度; _std 是同一银行-年内文章间语调离散度 (bank-year 标准差); _vw 是以报道内目标银行提及密度 (mention_density) 为权重的加权均值, 借鉴 hassan et al. (2019) 与相关文献中"按相关性加权"的思想, 让更聚焦于该银行的报道贡献更多; _mw 是以媒体权威性权重 (media_authority_weight) 加权的均值, 呼应 holzman et al. (2023) 关于权威媒体语调更具定价与纪律含义的证据; _hw 是以羊群衰减权重 (herd_weight, stage 24 产出) 加权的均值, 用于抑制短时间内高度同质化的跟风报道对语调的重复计入; _tech 与 _app 则是 P4 金融科技定位 (locus) 二元分类下, 分别在"底层技术"与"应用场景"报道子集上求得的语调均值。所有加权变体的实现都是"先在文章级预乘权重得到分子列、聚合时对分子求和再除以权重和", 而非直接对已归一化得分做二次加权, 以避免 Jensen 不等式带来的口径偏差。

之所以要区分"文章级预乘 + 聚合求和相除"与"聚合后再加权"两种口径, 是因为 jiang_2021_score 已经是一个自归一化到 [−1,1] 的比值, 对比值直接再乘权重求平均, 会把权重错误地作用在"已被各篇自身分母标准化过"的量上, 与"以权重定义的加权平均"这一目标不符; 正确做法是把权重理解为对每篇报道"贡献份额"的定义, 即分子为 Σ(score·w)、分母为 Σw, 这样当所有权重相等时自动退化为等权算术均值, 与 canonical 完全一致, 保证了加权变体与 canonical 之间的可比性与连续性。三种权重来源在语义上彼此正交: mention_density 刻画篇内对该银行的聚焦程度 (篇内维度), media_authority_weight 刻画报道所在媒体的权威等级 (媒体维度), herd_weight 刻画报道在时间上相对同题跟风稿的独立性 (时间维度)。三者不是同一权重的不同刻度, 而是三个不同的加权理由, 因此论文在同时呈现它们时须明确各自的经济学含义, 以防被质疑为无意义的变量堆砌 (variable farming)。此外, tech/app 子集依赖 locus 分类器对每篇报道的二元标注, 该标注本身来自 P4 内容定位链路, 与语调打分相互独立, 因此 tech/app 语调是"在给定内容类型条件下的语调", 而非对语调本身的再切分。须特别指出: 在 encode.aggregate_panel 的 locus 分类聚合块里, tech 与 app 子集的成员资格一律由 full 轨的 locus 标签 (innovation_locus_full == 底层技术/应用场景) 决定, 三轨 (full/ctx/ss) 的 tech/app 列只是把三轨各自的语调源列在同一个 full-locus 子集内分别求均值; 换言之, 随轨变化的只是被聚合的语调源列, 子集的行成员恒由 full-locus 标签锁定, ctx/ss 并不各自重新按轨内 locus 重切子集。这与 codebook 侧另有的 _tech_lc_ctx 一类"对角轨"命名 (轨与 locus 同轨) 属不同口径, 本家族的 _tech/_app 后缀恒指 full-locus 单轨子集, 二者不可混淆。

【文献定位】
本家族坐落于财经文本情感度量的方法学谱系中。tetlock (2007) 奠定了"媒体语调进入资产定价"的实证范式, loughran and mcdonald (2011) 指出通用情感词典在金融文本上系统性误分类、必须使用领域词典, loughran and mcdonald (2016) 系统综述了会计金融文本分析方法。中文场景下, you et al. (2018) 刻画了中国媒体"笔杆子的权力"及其信息含量, du et al. (2022)、bian et al. (2021) 与姜富伟等 (2021) 分别构建了面向中文财经文本的情感词典; ma et al. (2025) 进一步构建了面向中国国内投资者的细粒度中文情感词典 CN-FSD, 说明"中文财经词典"本身仍是活跃的方法学前沿。barbaglia et al. (2025) 与 zheng et al. (2024) 表明基于词典与基于词嵌入的情感度量在经济金融文本上各有优劣; algaba et al. (2020) 与 van atteveldt et al. (2021) 分别从计量方法与效度比较角度指出, 任何单一情感度量都应与替代方法交叉验证; frankel et al. (2022) 直接比较了机器学习与词典法, 强调二者互为稳健。本家族正是把"词典选择"这一自由度显性化为可审计的稳健性梯子。

从测量效度角度看, van atteveldt et al. (2021) 系统比较了人工标注、众包、词典法与机器学习四类情感度量, 指出词典法在成本与可复现性上占优、在细粒度语义上不及监督学习, 这为本项目"词典 + LLM + BERT 三法并行、互相印证"的架构提供了直接的方法论依据; barbaglia et al. (2025) 在经济文本上的应用则说明, 只要词典构建得当、规则处理到位, 基于词典的情感度量在解释宏观与市场变量时仍具竞争力, 而非仅是机器学习的落后替代。姜富伟等 (2021) 词典正是这样一部经过财经语料校准的中文词典, 其在国内研究中的广泛使用本身构成了外部效度的一种间接证据。把它与更晚近的 du et al. (2022)、ma et al. (2025) 并置, 还能检验"结论是否随词典的构建年代与语料时代而漂移", 这在金融科技这一术语快速演化的领域尤为重要。总之, 本家族在文献谱系中的定位是"可复现、领域校准、且作为跨方法三角验证一角的中文词典法语调测度"。相邻的中文股市语调研究也提供了旁证: Liu, Wang, & Xue (2023, International Review of Financial Analysis) 发现中国A股年报语调显著提高股票收益共动性, 该效应在机构持股低、民营及市场份额低的股票中更强, 并在经济扩张期与投资者情绪高涨时更为突出; Xu, Hua, & Zhang (2025, Emerging Markets Review) 构建基于文本分析与BERT的官方媒体情绪指数(NegGovOp), 发现其能预测中国股市收益反转, 主要通过影响散户交易行为、成交量与波动率发挥作用。

【识别策略定位】
在下游因果识别中, 姜富伟等 (2021) 词典语调主要充当处理变量 (treatment) 的稳健性替代测度, 而非主线主测度。项目主线 P1 (bank_fintech_tone) 的注册主处理变量是 LLM 三家投票共识语调 llm_vote_tone_full (full-only 留篇门控口径, 2026-06-29), 词典法语调 (含本家族) 作为"不依赖大模型的可复现替代测量"进入稳健性表格。铁律在此适用: 六部词典各自 just-identified 并排, 各自作为主测度的独立替代, 互为稳健性、不分主次; 严禁把姜富伟等 (2021) 与其它词典的语调列混进同一个 over-identified 的 Hansen J 过度识别检验中当作多个工具变量, 因为它们度量的是同一构念的高度共线替代 (跨词典语调相关系数通常很高), 混入会人为制造虚假的过度识别信息。同理, 三轨 (full/ctx/ss)、三种加权 (vw/mw/hw)、以及 tech/app 二分, 都是规格稳健性的并排臂, 各自 just-identified, 不得跨臂拼进同一过度识别方程。

这一纪律的经济学理由值得展开: 过度识别检验 (如 Hansen J) 的效力建立在"多个工具携带部分独立的识别信息"这一前提上; 而本家族的诸多列度量的是同一潜在构念 (媒体对银行金融科技的语调) 的高度共线替代, 跨词典语调之间、跨轨之间、跨权重之间的相关系数通常都很高。若把它们并列塞进一个 over-identified 的工具集, J 统计量会因这些工具几乎携带相同信息而失去检验力, 甚至制造出"看似通过过度识别"的假象, 反而掩盖了真正的识别问题。正确的用法是: 选定一列 (通常是 canonical full 轨 LLM 共识, 词典法作替代) 作为主规格, 其余列逐一替换主测度、各自跑一个 just-identified 或标准回归, 报告系数与显著性在替换后的稳定性; 稳健性来自"换了测量、结论不变", 而不是"把所有测量一起当工具"。这正是本项目把词典、三轨、三权重、tech/app 都物化成显式列而非合并成单一指数的根本原因 —— 让每一个测量自由度都可被独立审计与替换。

进一步区分本家族在识别链条中充当处理变量替代与充当被解释变量两种角色。主线 P1 把语调放在解释变量一侧, 关心的是"媒体对银行金融科技的语调"如何影响下游银行财务后果 (如融资成本), 此时姜富伟等 (2021) 词典语调是处理变量 llm_vote_tone_full 的可复现替代, 换测量重跑即得稳健性表; 但在方法学论文 (如 llm_peer) 或以语调本身为结果的规格里, 本家族语调也可能被放在被解释变量一侧, 用外生冲击或工具 (如媒体来源 house-style 暴露 outlet IV、同组留一均值 leave-one-out peer IV、广义 Bartik 暴露) 去解释语调的形成。无论居于方程哪一侧, "六部词典各自 just-identified 并排、禁混同一 over-identified Hansen J"的纪律都不变: 工具的过度识别信息必须来自工具间的真实独立性, 而不是来自把同一构念的高度共线替代硬凑成多个工具。就本项目而言, 真正承担跨测量族多重检验校正的是根级 rwolf/FWER 模板 (如 27_tableA12 跨模型 FWER), 它对同构念不同测量的替代做的是"族内多重假设的显著性校正", 而非"把它们当多工具做过度识别"; 二者在统计目标上截然不同, 混用会同时误用两种方法。因此凡在稿件里同时呈现本家族多列, 都应在方法脚注里点明: 这是规格稳健性的并排展示, 不是工具集扩容。

【与相邻测度的构念区分】
本家族须与三类相邻测度明确区分。其一, 与其它五部词典的同名语调列 (yao_2021_tone、bian_2021_tone、du_2022_tone、you_2018_tone、loughran_tone) 区分: 差异仅在底层词表与规则参数 (例如 du_2022 独有政治正面词半权口径), 聚合口径完全一致, 因此它们是跨词典稳健性的平行臂。其二, 与 LLM 语调 (llm_vote_tone、各家 per-model 语调) 及 BERT 语调 (finbert_cn 等) 区分: 后二者是"读语义"的机器学习测度, 本家族是"查词表 + 规则"的词典测度, 三法互为稳健性但计算机理迥异。其三, 与 IDF 加权版 jiang_2021_idf_tone 区分: 后者对词典词施加语料级 IDF 权重 (稀有词升权、高频词降权), 属另一条稳健性支线, 不在本家族。此外, _std 度量的是语调离散度 (不确定性/分歧) 而非语调水平, 在构念上更接近"叙事一致性", 使用时须避免与语调水平混淆。

其四, 与 tech/app 语调差 (tone_gap) 区分: 本家族只提供 tech 侧与 app 侧各自的语调水平, 而 P4 (locus) 的主 DV 是二者之差, 在别处专列度量; 差值与水平构念不同, 差值捕捉"媒体在谈底层技术与谈应用场景时的语调偏向", 而本家族的 _tech/_app 列只是构成该差值的两个分量之一, 单独使用时不应被解读为定位偏向。其五, 与加权变体各自的权重列本身区分: sum_media_authority_weight、avg_herd_weight 等是权重的聚合量, 与"以权重加权后的语调"是两回事, 前者刻画报道的媒体权威或跟风结构, 后者才是被加权的态度; 论文若同时使用须避免把权重结构误当作语调。总之, 本家族在构念地图上占据的是"词典法 × 有条件语境 × 银行-年语调水平/离散度"这一格, 与语义模型测度、IDF 加权支线、语调差 DV、以及权重结构量都保持清晰边界。

再补两组易混淆的相邻测度以彻底划界。其六, 与注意力/曝光量家族 (P2 attention 侧, 如 n_articles、fintech_share、attention_pct、ln_coverage) 区分: 那一族度量的是"媒体谈了多少、谈得多密"的数量维度, 与本家族"谈得多褒或多贬"的态度维度正交; 一家银行可以被大量报道却语调中性, 也可以只被少数报道却语调极端, 因此曝光量与语调是两条独立信号, 论文常把二者交互 (如 ln_coverage × tone) 构造复合暴露, 但绝不能互相替代, 更不能因语调列缺失就用曝光量列顶替。其七, 与羊群衰减权重列本身及金融科技强度 (fintech_intensity, stage 15) 区分: herd_weight 是本家族 _hw 变体的输入权重, 度量报道相对同题跟风稿的独立性, 属"信息新鲜度"维度而非态度; fintech_intensity 是报道中金融科技语义浓度的连续测度, 属"主题相关度"维度; 二者都可能与语调相关, 但构念上分属信息结构与主题结构, 不是语调的组成部分。厘清这两组边界后, 本家族与项目内数量、独立性、主题浓度三类非态度测度之间就不存在语义重叠, 使用时可放心把它们作为控制变量或交互项与语调联用, 而不必担心同义反复。

【已知局限与稳健性梯子】
已知局限有四。第一, 词典法对反讽、隐喻、复杂条件句的处理弱于语义模型, 这正是需要 LLM/BERT 三法交叉的原因。第二, 姜富伟等 (2021) 词典的覆盖与时代性有限, 对新兴金融科技术语可能欠收录, 故须与更新的中文词典 (如 du 2022、ma 2025) 并排。第三, 在早期试跑盘面 T=2 的开发数据上, ss 轨与 tech/app 子集常因样本稀薄而出现大量 NaN 或零方差, 属预期退化, 结论一律以全量约 1,819 万条语料 / T=19 (2007–2025) 为准。第四, 加权变体的解释力依赖权重来源列的质量 (mention_density、media_authority_weight、herd_weight), 权重缺失时相应变体优雅回退或置 NaN。稳健性梯子的完整叙事是: 以 canonical full 轨为锚, 沿文本粒度 (三轨)、聚合权重 (vw/mw/hw)、内容子集 (tech/app)、离散度 (std) 与跨词典 (六部) 五个正交维度展开, 每一维都是并排的 just-identified 臂, 共同支撑"主结论不被任一测量自由度驱动"的论断。

还须补充两点操作性局限。第一, 加权变体在盘面小样本上可能因权重来源列的稀疏 (例如 herd_weight 需要 stage 24 跟风衰减计算充分、media_authority_weight 需要媒体来源被权威分级表覆盖) 而部分退化, 此时相应 _vw/_mw/_hw 列可能等于或接近 canonical 均值, 不应据此推断"加权无影响", 而应在全量 T=19 上重新评估; 反过来, 当权重来源充分时, 若加权与等权结论显著背离, 才是值得关注的稳健性信号, 提示语调可能被特定密度、特定媒体或特定跟风结构驱动。第二, tech/app 子集依赖 locus 分类器标注的质量, 分类器在盘面小样本上标注稀薄、甚至整类缺席属预期; 使用 tech/app 语调时须先核查对应 n_articles_tech / n_articles_app 的非零覆盖, 覆盖过低时子集均值的抽样误差极大, 不宜进入主结论, 只作探索性对照。综上, 本家族的正确使用姿势是: 以 jiang_2021_tone_full 为词典法主替代, 其余各列按其明确的测量维度作并排稳健性臂, 逐一替换主测度检验结论稳定性, 而非把它们合并或塞进同一过度识别方程; 一切回归级数值结论以全量约 1,819 万条语料 / T=19 (2007–2025) 的实测为准, 早期试跑盘面 T=2 仅验证管道正确性与 schema 完整性。

最后把稳健性梯子放进项目"词典 + LLM + BERT 三法交叉"的更大三角里给出使用序。第一步, 在词典法族内先做跨词典替换 (六部词典逐一顶替 canonical), 证明结论不被姜富伟等 (2021) 这一部词表的构建选择驱动; 这是 frankel et al. (2022) 与 van atteveldt et al. (2021) 反复强调的"任何单一情感测量都须与替代方法交叉验证"的最低要求。第二步, 跨方法交叉: 用 LLM 三家投票语调与 BERT 三模型语调重跑同一规格, 检验"词典法 vs 语义模型"这一更根本的方法学分野是否改变结论, 呼应 barbaglia et al. (2025)、zheng et al. (2024) 关于词典法与词嵌入法各有优劣的发现。第三步, 在选定的主测量上沿本家族的三轨、三权重、tech/app、std 五个正交维度做规格稳健性展开。三步各自回答不同层级的稳健性问题 —— 词表选择、方法范式、规格自由度 —— 层层收敛却互不替代, 共同支撑"主结论不被任一测量自由度驱动"这一论断。需再次强调: 上述所有替换臂都是并排的 just-identified 或标准规格, 稳健性来自"换测量、结论稳", 多重假设的显著性风险由根级 FWER 模板统一校正, 任何环节都不得把这些高度共线的替代测量拼进同一 over-identified Hansen J 冒充过度识别信息; ss 轨与 tech/app 子集在早期试跑盘面 T=2 上的整体缺失或零方差是样本稀薄导致的预期退化 (ss 回退语义镜像 ctx: 无同句共现即回退全文并置 fallback 标志、共享 n_articles 分母), 绝非缺陷, 一切阈值化的定量结论须待全量 T=19 语料上线后方可下笔。

## VAR: jiang_2021_tone_full

【变体差分】
本列是家族 canonical 核心列, tier=core。它是姜富伟等 (2021) 词典语调在 full 文本轨、无聚合加权、算术均值口径下的银行-年测度, 是家族一切其它变体的参照基准。full 轨的文本是 content_full, 即在报道正文前 prepend 标题后的完整全文; 相较 ctx/ss 两轨, full 轨最大化保留上下文信息, 因此被选作 canonical, 与项目"留篇门控 = full-only" (2026-06-29) 的口径一致 —— 一篇报道是否计入某银行某年的语调分母, 只看 full 轨口径, ctx/ss 是 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集的子集。

计算上, 先由 stage 22 对每篇 full 文本用姜富伟等 (2021) 词典 + 否定/程度/转折三规则打出文章级 jiang_2021_score_full ∈ 约 [−1,1], 再在 stage 40 按 (target_bank, year) 分组取算术平均得到本列, 分母是该银行该年 full 轨全部留篇报道数, 零报道的银行-年为 NaN (刻意不填零, 以防回归口径污染)。本列在下游作为 P1 处理变量 llm_vote_tone_full 的"非大模型可复现替代测量"进入稳健性表, 度量同一"媒体对银行金融科技的语调"构念。作为跨词典稳健性梯子的一员, 本列与 yao_2021_tone_full、bian_2021_tone_full、du_2022_tone_full、you_2018_tone_full、loughran_tone_full 六者各自 just-identified 并排、互为稳健性、不分主次; 严禁把它们混进同一个 over-identified Hansen J 过度识别检验, 因为跨词典语调是同一构念的高度共线替代。同理, 本 full 轨与 ctx/ss 轨、与 std/vw/mw/hw/tech/app 各聚合变体, 均为规格稳健性并排臂, 不得跨臂拼入同一过度识别方程。相对家族内其它列, 本列的唯一识别特征是: 三轨中的 full 轨 + 无权重 (等权) + 均值 (非 SD) + 全样本 (非 tech/app 子集)。

进一步说明本列作为家族基准的地位。家族里其余二十列都可以理解为在本列的四个坐标 (轨道 = full、权重 = 等权、算子 = 均值、样本 = 全样本) 上各改动一维得到的变体: 换轨得到 _ctx/_ss, 换算子得到 _std, 换权重得到 _vw/_mw/_hw, 换样本子集得到 _tech/_app。因此解释任何其它列时, 都以本列为参照系, 只需说明它相对本列改了哪一维即可。选择 full 轨 + 等权 + 均值作为基准, 是与项目整体口径一致的刻意设计: full 轨最大化上下文信息且是留篇门控的唯一裁决轨 (full-only, 2026-06-29), 等权是最少假设的聚合方式 (不引入任何权重来源列的额外依赖与噪声), 算术均值是最直接的"银行该年平均语调"估计。

在与主线 P1 的关系上, 本列是 llm_vote_tone_full 的词典法可复现替代: 当审稿人质疑"结论是否依赖大模型这一黑箱"时, 用本列重跑主回归可给出一个完全不调用任何 LLM、仅靠公开词典与确定性规则即可复现的替代证据; 二者度量同一"媒体对银行金融科技的语调"构念, 但一为语义模型的三家投票共识、一为词典 + 规则打分, 计算机理正交, 故互为稳健性而非冗余。同时, 本列自身又是跨词典梯子的锚: 把它替换为 yao_2021_tone_full、bian_2021_tone_full、du_2022_tone_full、you_2018_tone_full、loughran_tone_full 逐一重跑, 即得跨词典稳健性表。所有这些替换都遵循 just-identified 并排、逐一替换主测度的纪律, 六部词典语调互为稳健性、不分主次, 严禁一起塞进同一 over-identified Hansen J; 同理本 full 轨与 ctx/ss 轨、与各聚合变体也不得跨臂合并。使用时须记住本列分母是该银行该年 full 轨留篇报道数, 零报道行为 NaN 而非 0, 回归中不可将 NaN 误填为中性 0, 否则会把"无媒体覆盖"错误编码为"语调中性", 污染系数估计。

补充本列在计算与解释上的三条操作细则。其一, 打分口径继承家族全规则约定: 每篇 full 文本经冻结版 jieba (0.42.1) 分词后, 用字节级冻结的姜富伟等 (2021) 词典逐词匹配, 再叠加否定翻转、程度副词缩放、转折上调三条语言学规则, 最后按 (正向最终值和 − 负向最终值和) / 最终值绝对值和 自归一化到约 [−1,1]; 冻结分词与冻结词典共同保证本列在同一文本上跨运行逐位可复现, 这是它相对 LLM/BERT 语义测度的核心工程优势, 也是它能充当"确定性可复现替代"的前提。其二, 本列度量的是有条件语调而非一般媒体形象: 原始语料已经过 stage 13 共现硬过滤, 只保留"目标银行与至少一个金融科技词邻近共现"的报道, 因此本列回答的是"当媒体谈及该银行金融科技活动时的平均褒贬", 其分母是留篇报道数而非全部提及该银行的报道数, 与更宽口径的一般银行语调在语义上不可互替。其三, 与家族内加权变体的关系: 本列是等权基准, 当它与 _vw/_mw/_hw 加权变体在全量样本上显著背离时, 提示银行该年语调分别被高聚焦报道、权威媒体或跟风重复所主导, 此时应把等权与加权臂并排呈现并讨论差异来源, 而非简单认定某一口径"更对"; 三种权重来源 (mention_density、media_authority_weight、herd_weight) 语义正交, 与本列一道构成聚合权重维度的并排稳健性臂, 同样禁止合并进同一 over-identified Hansen J。

## VAR: jiang_2021_tone_ctx

【变体差分】
本列相对 canonical jiang_2021_tone_full 的唯一差分是文本轨: 由 full 轨换成 ctx 轨。ctx 文本是 content_ctx, 即标题 prepend 之后, 仅保留围绕目标银行实体提及的上下文窗口 (实体窗), 剔除与该银行无关的段落。其构念意图是: 只让"确实在谈论这家银行"的语句进入语调打分, 减少全文中无关噪声段落的稀释, 因此 ctx 轨语调通常比 full 轨更聚焦、方差特征也不同。词典、三规则、聚合均值口径与 canonical 完全一致, 差异纯粹来自被打分的文本范围。

在项目留篇门控 full-only 口径下, ctx 轨是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, 语调 per-track 独立计算。本列与 full 轨、ss 轨互为文本粒度维度上的稳健性并排臂, 各自 just-identified, 严禁三轨混入同一 over-identified Hansen J。作为词典法测度, 它与其它五部词典的 _ctx 列构成跨词典稳健性平行臂, 同样禁止拼入同一过度识别方程。使用建议: 当担心 full 轨因长文中大量与银行无关内容而语调被摊平时, 以本 ctx 轨作为"聚焦口径"的稳健性对照; 但在早期试跑盘面 T=2 上 ctx 轨可能样本稀薄, 数值结论以全量 T=19 为准。相对家族其它列, 本列识别特征是 ctx 轨 + 等权 + 均值 + 全样本。在实践中当本列与 full 轨语调出现方向性背离时, 往往提示全文中存在大量与该银行无关的背景段落把 full 轨语调摊平, 此时 ctx 轨更贴近针对该银行的真实态度, 值得在稳健性表中并排呈现并加以讨论。

## VAR: jiang_2021_tone_ss

【变体差分】
本列相对 canonical 的唯一差分是文本轨换成 ss (same-sentence) 轨。ss 文本是 content_ss, 即标题 prepend 之后, 仅保留"目标银行与金融科技词出现在同一句 (含正负若干句窗, 窗口半径由 config filtering ss_sentence_radius 控制, 默认 1)"的语句。其构念意图是最严格地锁定"银行 × 金融科技"共现语境下的语调, 排除银行在与金融科技无关段落中被提及时的态度。ss 轨的回退语义镜像 ctx 轨: 当某报道不存在银行与金融科技的同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback=True (与 ctx 共享 n_articles 分母口径), 当金融科技 AC 自动机为空时 ss_is_fallback 全 True 优雅降级。

词典、三规则、聚合均值口径与 canonical 完全一致, 仅文本范围最窄。本列与 full/ctx 轨互为文本粒度稳健性并排臂, 各自 just-identified, 严禁三轨混入同一 over-identified Hansen J; 与其它五部词典的 _ss 列构成跨词典平行臂。特别提示: ss 轨是三轨中最依赖付费 LLM 缓存播种与共现命中的一轨, 在早期试跑盘面 T=2 数据上 ss 相关列常整体缺失或零方差属预期 (REQUIRED_PANEL_COLUMNS 刻意不含 _ss, 不阻塞导出), 全量 T=19 上线后方为非退化, 一切数值结论以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 等权 + 均值 + 全样本。作为三轨中语境最严格的一条, 本列与 full 轨语调若在全量样本上出现系统性差异, 可用于论证"银行金融科技叙事本身的褒贬与报道整体基调存在分层", 是三轨梯子中最贴近核心构念的稳健性对照。

## VAR: jiang_2021_tone_std_full

【变体差分】
本列相对 canonical jiang_2021_tone_full 的差分在聚合算子: 由算术均值换成同一银行-年内文章级 jiang_2021_score_full 的标准差 (bank-year SD), 文本轨仍为 full。因此本列度量的构念不是语调水平, 而是"该银行该年 full 轨报道之间语调的离散程度", 可解读为媒体叙事的分歧度或不确定性 —— 高 std 表示同期报道褒贬并存、叙事不一致, 低 std 表示口径高度一致。这一离散度在下游可用于构造"金融科技叙事暴露"复合指标 (如 fintech_exposure = ln_coverage × tone_std), 也可单独作为叙事分歧的代理。

计算上取 pandas groupby 的 std (样本标准差, ddof=1), 分母为该银行-年 full 轨报道数减一; 当报道数为 1 时 SD 为 NaN, 当零报道时同样 NaN。须严格区分本列与语调水平列: 二者构念不同, 不可互替, 论文中若同时使用须明确说明一为水平、一为分歧。本列与 std_ctx、std_ss 构成三轨离散度并排臂, 各自 just-identified, 禁混同一 over-identified Hansen J; 与其它五部词典的 _tone_std_full 列构成跨词典离散度平行臂。相对家族其它列, 本列识别特征是 full 轨 + 等权 + 标准差算子 (非均值) + 全样本。作为离散度族在最完整文本轨上的锚, 本列可与语调水平列 jiang_2021_tone_full 配对使用, 前者答"分歧有多大", 后者答"平均偏向哪边", 二者联用能刻画媒体叙事的水平与不确定性两个维度。早期试跑盘面 T=2 上因每格报道极少, SD 常为 NaN, 结论以全量 T=19 为准。

## VAR: jiang_2021_tone_std_ctx

【变体差分】
本列是 jiang_2021_tone_std_full 的 ctx 轨孪生: 聚合算子同为 bank-year 标准差, 但对象换成 ctx 轨的文章级得分 jiang_2021_score_ctx。它度量的是"在仅保留银行实体上下文窗口的聚焦文本口径下, 该银行该年报道之间语调的离散度"。相比 std_full, 本列剔除了全文中与银行无关段落对语调分布的影响, 因此其离散度更纯粹地反映了针对该银行的叙事分歧, 而非全文话题多样性带来的伪离散。

在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 本列的样本宇宙是 full 留篇集子集。计算口径 (ddof=1 样本标准差, 单篇为 NaN, 零篇为 NaN) 与 std_full 一致。本列与 std_full、std_ss 构成三轨离散度稳健性并排臂, 各自 just-identified, 严禁三轨混入同一 over-identified Hansen J; 与其它五部词典的 _tone_std_ctx 列构成跨词典离散度平行臂, 同样禁止拼入同一过度识别方程。使用时须与语调水平列区分, 本列度量分歧而非水平。相对家族其它列, 本列识别特征是 ctx 轨 + 等权 + 标准差算子 + 全样本。相比 std_full, 本列的离散度更纯粹地反映针对该银行报道之间的态度分歧, 剔除了全文话题多样性带来的伪离散, 因此在检验"叙事分歧假说"时是 std_full 的更聚焦对照臂。早期试跑盘面 T=2 上 ctx 轨样本稀薄, 本列多为 NaN 或零方差, 属预期退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_std_ss

【变体差分】
本列是语调离散度族的 ss 轨成员: 聚合算子为 bank-year 标准差, 对象为 ss 轨文章级得分 jiang_2021_score_ss。它度量"在银行与金融科技严格同句共现的最窄文本口径下, 该银行该年报道之间语调的离散度", 是三条离散度轨中语境最聚焦的一条 —— 只有确实在同句谈论银行金融科技活动的语句才进入 SD 计算, 因此本列反映的是金融科技叙事本身的褒贬分歧, 而非报道整体基调的分散。

ss 轨回退语义镜像 ctx: 无同句共现时 content_ss 回退全文并置 ss_is_fallback=True。计算口径 (样本标准差 ddof=1, 单篇/零篇为 NaN) 与其它离散度列一致。本列与 std_full、std_ctx 构成三轨离散度并排臂, 各自 just-identified, 严禁三轨混入同一 over-identified Hansen J; 与其它五部词典的 _tone_std_ss 列构成跨词典离散度平行臂。须注意 ss 轨是最依赖付费缓存播种与共现命中的一轨, 早期试跑盘面 T=2 上本列几乎必然整体缺失或零方差, 属预期; 全量 T=19 上线后方为有效离散度测度, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 等权 + 标准差算子 + 全样本。它是三条离散度轨中语境最聚焦者, 度量的是银行金融科技同句共现语境下媒体态度的分歧程度, 在全量样本上可用于识别"金融科技叙事本身是否存在褒贬两极分化"。使用时须与语调水平列区分, 本列度量分歧而非水平。

## VAR: jiang_2021_tone_vw_full

【变体差分】
本列相对 canonical jiang_2021_tone_full 的差分在聚合权重: 由等权算术均值换成以报道内目标银行提及密度 (mention_density) 为权重的加权均值, 文本轨仍为 full。构念意图是让"更聚焦于该银行"的报道在语调聚合中承载更大权重, 借鉴 hassan et al. (2019) 等文献中按相关性/暴露度加权的思想 —— 一篇通篇围绕该银行金融科技的报道, 其语调应比一篇仅顺带提及该银行的报道更能代表媒体对该银行的态度。vw 即 value/density-weighted。

实现上遵循"先在文章级预乘权重、聚合时分子求和再除以权重和"的口径 (jiang_2021_tone_vw = Σ(score·w)/Σw, w = mention_density), 而非对已归一化得分做二次加权, 以规避 Jensen 不等式偏差。当密度权重来源列缺失时本列优雅回退或置 NaN。本列与 vw_ctx、vw_ss 构成三轨密度加权并排臂; 与等权 canonical、媒体权 _mw、羊群权 _hw 构成"聚合权重维度"的并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_vw_full 列构成跨词典平行臂。相对家族其它列, 本列识别特征是 full 轨 + 密度权 (mention_density) + 加权均值 + 全样本。当本列与等权 canonical 显著背离时, 提示银行该年语调被少数高聚焦度报道主导, 是检验"语调是否由深度报道而非顺带提及驱动"的直接稳健性证据。

## VAR: jiang_2021_tone_vw_ctx

【变体差分】
本列是密度加权语调族的 ctx 轨成员: 权重为 mention_density, 对象为 ctx 轨文章级得分。它度量"在仅保留银行实体上下文窗口的聚焦文本口径下, 以银行提及密度加权后的银行-年语调"。相比 vw_full, 本列先在文本层剔除与银行无关段落 (ctx 轨), 再在聚合层按密度加权, 是"文本聚焦 × 聚合聚焦"的双重聚焦口径, 用于检验主结论是否对"给更相关报道更大权重"这一自由度稳健。

计算口径为 Σ(score_ctx·mention_density)/Σ(mention_density), 与 vw_full 同构, 仅文本轨不同; 权重缺失时优雅回退或置 NaN。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 样本宇宙是 full 留篇集子集。本列与 vw_full、vw_ss 构成三轨密度加权并排臂; 与 canonical 等权、_mw 媒体权、_hw 羊群权构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重/不同轨变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_vw_ctx 列构成跨词典平行臂。相对家族其它列, 本列识别特征是 ctx 轨 + 密度权 + 加权均值 + 全样本。它把文本聚焦 (ctx 轨剔除无关段落) 与聚合聚焦 (按银行提及密度加权) 叠加, 是"双重聚焦"稳健性臂, 用于检验主结论在最严格相关性口径下是否依然成立。早期试跑盘面 T=2 上 ctx 轨样本稀薄, 本列多退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_vw_ss

【变体差分】
本列是密度加权语调族的 ss 轨成员: 权重为 mention_density, 对象为 ss (银行与金融科技同句共现) 轨文章级得分。它度量"在最窄的同句共现文本口径下, 以银行提及密度加权后的银行-年语调", 是三条密度加权轨中语境最聚焦者, 兼具"文本最聚焦"与"聚合按相关性加权"两重收敛。构念上, 它最贴近"媒体对这家银行的金融科技活动本身的加权态度"。

计算口径为 Σ(score_ss·mention_density)/Σ(mention_density), 与 vw_full/vw_ctx 同构; ss 轨回退语义镜像 ctx (无同句共现时回退全文并置 ss_is_fallback=True), 权重缺失时优雅回退或置 NaN。本列与 vw_full、vw_ctx 构成三轨密度加权并排臂; 与 canonical 等权、_mw、_hw 构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与其它五部词典的 _tone_vw_ss 列构成跨词典平行臂。特别提示: ss 轨最依赖付费缓存播种与共现命中, 早期试跑盘面 T=2 上本列几乎必然缺失或零方差, 属预期退化, 全量 T=19 上线后方有效, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 密度权 + 加权均值 + 全样本。它是密度加权族里语境最窄的一条, 兼具同句共现的文本聚焦与按银行提及密度的聚合聚焦, 在全量样本上最贴近"媒体对该银行金融科技活动本身的加权态度"。

## VAR: jiang_2021_tone_mw_full

【变体差分】
本列相对 canonical 的差分在聚合权重: 换成以媒体权威性权重 (media_authority_weight) 加权的均值, 文本轨为 full。构念意图是让权威媒体的报道语调承载更大权重 —— holzman et al. (2023) 等证据表明权威媒体的语调更具信息含量与市场纪律作用, 因此以媒体权威性加权可检验"主结论是否由权威媒体而非边缘自媒体驱动"。mw 即 media-authority-weighted。权重来源列 media_authority_weight 在 stage 40 前由 compute_media_authority_weights 依据媒体来源的权威分级计算 (另有 media_authority_weight_tier 三级并行列作 Table A8 敏感性)。

实现遵循"文章级预乘权重、聚合时分子求和再除权重和"口径 (Σ(score·media_authority_weight)/Σ(media_authority_weight)), 规避 Jensen 偏差; 权重缺失时以 1.0 兜底或优雅置 NaN。本列与 mw_ctx、mw_ss 构成三轨媒体加权并排臂; 与 canonical 等权、_vw 密度权、_hw 羊群权构成聚合权重维度并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_mw_full 列构成跨词典平行臂。媒体权威加权与密度加权正交 (前者按媒体级权威、后者按篇内银行聚焦度), 论文须明写以防 variable-farm 质疑。相对家族其它列, 本列识别特征是 full 轨 + 媒体权 + 加权均值 + 全样本。当本列与等权 canonical 背离时, 提示银行该年语调被权威媒体或边缘自媒体的某一侧主导, 是检验"语调结论是否由权威信源驱动"的直接稳健性证据。

## VAR: jiang_2021_tone_mw_ctx

【变体差分】
本列是媒体权威加权语调族的 ctx 轨成员: 权重为 media_authority_weight, 对象为 ctx 轨文章级得分。它度量"在银行实体上下文窗口的聚焦文本口径下, 以媒体权威性加权后的银行-年语调"。相比 mw_full, 本列先在文本层剔除与银行无关段落 (ctx 轨), 再按媒体权威加权, 检验主结论对"文本聚焦 + 权威媒体加权"联合口径的稳健性。

计算口径 Σ(score_ctx·media_authority_weight)/Σ(media_authority_weight) 与 mw_full 同构, 仅文本轨不同; 权重缺失以 1.0 兜底或优雅置 NaN。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 样本宇宙是 full 留篇集子集。本列与 mw_full、mw_ss 构成三轨媒体加权并排臂; 与 canonical 等权、_vw、_hw 构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重/不同轨变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_mw_ctx 列构成跨词典平行臂。媒体权威加权与密度加权正交, 使用时须明确区分。相对家族其它列, 本列识别特征是 ctx 轨 + 媒体权 + 加权均值 + 全样本。它把文本聚焦与权威媒体优先叠加, 是"文本聚焦 × 媒体权威"双重口径稳健性臂, 用于检验主结论在既剔除无关段落又给权威媒体更大权重时的稳定性。早期试跑盘面 T=2 上 ctx 轨样本稀薄, 本列多退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_mw_ss

【变体差分】
本列是媒体权威加权语调族的 ss 轨成员: 权重为 media_authority_weight, 对象为 ss (银行与金融科技同句共现) 轨文章级得分。它度量"在最窄同句共现文本口径下, 以媒体权威性加权后的银行-年语调", 是三条媒体加权轨中语境最聚焦者, 兼具"文本最聚焦"与"权威媒体优先"两重口径, 最贴近"权威媒体对这家银行金融科技活动本身的态度"。

计算口径 Σ(score_ss·media_authority_weight)/Σ(media_authority_weight) 与 mw_full/mw_ctx 同构; ss 轨回退语义镜像 ctx (无同句共现时回退全文并置 ss_is_fallback=True), 权重缺失以 1.0 兜底或优雅置 NaN。本列与 mw_full、mw_ctx 构成三轨媒体加权并排臂; 与 canonical 等权、_vw、_hw 构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与其它五部词典的 _tone_mw_ss 列构成跨词典平行臂。特别提示: ss 轨最依赖付费缓存播种与共现命中, 早期试跑盘面 T=2 上本列几乎必然缺失或零方差, 属预期退化, 全量 T=19 上线后方有效, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 媒体权 + 加权均值 + 全样本。它是媒体加权族里语境最窄的一条, 兼具同句共现的文本聚焦与权威媒体优先, 在全量样本上最贴近"权威媒体对该银行金融科技活动本身的态度"。

## VAR: jiang_2021_tone_hw_full

【变体差分】
本列相对 canonical 的差分在聚合权重: 换成以羊群衰减权重 (herd_weight) 加权的均值, 文本轨为 full。构念意图是抑制短时间内高度同质化的跟风报道对语调的重复计入 —— 当同一事件被大量媒体近乎复制式转载时, 朴素等权会让该事件语调被过度计入; 羊群衰减权重则对这类跟风报道降权, 使聚合语调更接近独立信息的加权。hw 即 herd-weighted。权重来源列 herd_weight 由 stage 24 (herd_decay_processor) 产出, 且为三轨独立 (herd_weight_full/ctx/ss); 本列使用 full 轨对应的 herd_weight_full。

实现遵循"文章级预乘权重、聚合时分子求和再除权重和"口径 (Σ(score·herd_weight_full)/Σ(herd_weight_full)), 规避 Jensen 偏差; 若仅存在 v3.5.0 legacy 单列 herd_weight 则三轨退化为同一权重并记 WARN, 权重缺失以 1.0 兜底。本列与 hw_ctx、hw_ss 构成三轨羊群加权并排臂; 与 canonical 等权、_vw 密度权、_mw 媒体权构成聚合权重维度并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_hw_full 列构成跨词典平行臂。羊群衰减与媒体权威、密度加权三者正交 (分别针对跟风重复、媒体权威、篇内聚焦), 论文须明写区分。相对家族其它列, 本列识别特征是 full 轨 + 羊群权 (herd_weight_full) + 加权均值 + 全样本。当本列与等权 canonical 背离时, 提示银行该年语调被短时间内高度同质的跟风转载重复计入, 是检验"语调结论是否由独立信息而非跟风重复驱动"的直接稳健性证据。

## VAR: jiang_2021_tone_hw_ctx

【变体差分】
本列是羊群加权语调族的 ctx 轨成员: 权重为 herd_weight_ctx (stage 24 三轨独立产出的 ctx 轨羊群衰减权重), 对象为 ctx 轨文章级得分。它度量"在银行实体上下文窗口的聚焦文本口径下, 对跟风报道降权后的银行-年语调"。相比 hw_full, 本列先在文本层剔除与银行无关段落 (ctx 轨), 再按羊群衰减降权, 检验主结论对"文本聚焦 + 抑制跟风重复"联合口径的稳健性。

计算口径 Σ(score_ctx·herd_weight_ctx)/Σ(herd_weight_ctx) 与 hw_full 同构, 仅文本轨与对应权重轨不同; legacy 单列时退化并记 WARN, 权重缺失以 1.0 兜底。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 样本宇宙是 full 留篇集子集。本列与 hw_full、hw_ss 构成三轨羊群加权并排臂; 与 canonical 等权、_vw、_mw 构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同权重/不同轨变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_hw_ctx 列构成跨词典平行臂。羊群衰减与媒体权威、密度加权正交。相对家族其它列, 本列识别特征是 ctx 轨 + 羊群权 + 加权均值 + 全样本。它把文本聚焦与抑制跟风重复叠加, 是"文本聚焦 × 独立信息"双重口径稳健性臂, 用于检验主结论在既剔除无关段落又对跟风稿降权时的稳定性。早期试跑盘面 T=2 上 ctx 轨样本稀薄, 本列多退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_hw_ss

【变体差分】
本列是羊群加权语调族的 ss 轨成员: 权重为 herd_weight_ss (stage 24 镜像 ctx 产出的同句轨羊群衰减权重; 缺列时优雅回退 herd_weight_full), 对象为 ss (银行与金融科技同句共现) 轨文章级得分。它度量"在最窄同句共现文本口径下, 对跟风报道降权后的银行-年语调", 是三条羊群加权轨中语境最聚焦者, 兼具"文本最聚焦"与"抑制跟风重复"两重口径。

计算口径 Σ(score_ss·herd_weight_ss)/Σ(herd_weight_ss) 与 hw_full/hw_ctx 同构; ss 轨回退语义镜像 ctx (无同句共现时 content_ss 回退全文并置 ss_is_fallback=True); herd_weight_ss 缺列时回退 herd_weight_full (与 legacy 单轨退化同口径), 权重缺失以 1.0 兜底。本列与 hw_full、hw_ctx 构成三轨羊群加权并排臂; 与 canonical 等权、_vw、_mw 构成聚合权重维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与其它五部词典的 _tone_hw_ss 列构成跨词典平行臂。特别提示: ss 轨最依赖付费缓存播种与共现命中, 早期试跑盘面 T=2 上本列几乎必然缺失或零方差, 属预期退化, 全量 T=19 上线后方有效, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 羊群权 + 加权均值 + 全样本。它是羊群加权族里语境最窄的一条, 兼具同句共现的文本聚焦与对跟风稿的降权, 在全量样本上最贴近"剔除跟风重复后媒体对该银行金融科技的独立态度"。

## VAR: jiang_2021_tone_tech_full

【变体差分】
本列相对 canonical 的差分在样本子集: 由全样本收窄到"金融科技定位 (locus) 二元分类为底层技术 (tech) 的报道子集", 文本轨为 full, 等权均值。构念意图对接主线 P4 (locus) —— 把银行金融科技报道按其谈论对象是"底层技术研发"还是"应用场景落地"二分, 本列只在被判为底层技术的报道子集上求姜富伟等 (2021) 词典语调均值, 从而回答"当媒体谈论银行的底层金融科技时, 语调如何"。tech 子集由 locus 分类器标注 (成员资格由 full 轨标签 innovation_locus_full 决定), 计数列为 n_articles_tech, 本列在 encode.aggregate_panel 的 locus 分类聚合块中生成, 仅当该子集非空时物化。

计算口径与 canonical 一致 (full 轨、等权、算术均值), 仅样本被限定在 tech 子集。本列与 tech_ctx、tech_ss 构成三轨底层技术子集并排臂; 与应用场景子集 _app、以及全样本 canonical 构成"内容子集维度"的并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁 tech/app/全样本不同子集变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_tech_full 列构成跨词典平行臂。须注意 tech 与 app 子集互斥, 二者语调之差 (tone_gap) 在别处专列度量 (P4 主 DV), 本列只提供 tech 侧的水平。相对家族其它列, 本列识别特征是 full 轨 + 等权 + 均值 + 底层技术子集。早期试跑盘面 T=2 上 locus 标注可能稀薄, 本列常大量 NaN, 结论以全量 T=19 为准。

## VAR: jiang_2021_tone_tech_ctx

【变体差分】
本列是底层技术子集语调族的 ctx 轨成员: 样本限定在 locus 分类为底层技术的报道, 对象为 ctx 轨文章级得分, 等权均值。它度量"在银行实体上下文窗口的聚焦文本口径下, 媒体谈论银行底层金融科技时的语调"。相比 tech_full, 本列先在文本层剔除与银行无关段落 (ctx 轨), 再限定 tech 子集, 是"文本聚焦 × 内容子集"双重收窄口径。

计算口径与 tech_full 同构 (ctx 轨、等权、均值), 仅被聚合的语调源列换成 ctx 轨得分; 由 encode.aggregate_panel 的 locus 分类聚合块生成。须强调子集成员资格由 full 轨 locus 标签 (innovation_locus_full == 底层技术) 锁定, 本 ctx 轨列只是在该 full-locus 子集内改取 ctx 轨语调源, 并非按 ctx 轨自身重切 tech 子集; 依赖该 full-locus tech 子集非空。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 样本宇宙是 full 留篇集子集。本列与 tech_full、tech_ss 构成三轨底层技术子集并排臂; 与 _app 子集、全样本 canonical 构成内容子集维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同子集/不同轨变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_tech_ctx 列构成跨词典平行臂。tech 与 app 子集互斥, 本列只提供 tech 侧 ctx 轨水平。相对家族其它列, 本列识别特征是 ctx 轨 + 等权 + 均值 + 底层技术子集。它把文本聚焦与内容限定叠加, 在全量样本上度量"仅在谈论该银行底层金融科技的聚焦文本里"媒体的语调, 是 tech_full 的更聚焦对照臂。早期试跑盘面 T=2 上 ctx 轨与 locus 标注双重稀薄, 本列几乎必然大量退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_tech_ss

【变体差分】
本列是底层技术子集语调族的 ss 轨成员: 样本限定在 locus 分类为底层技术的报道, 对象为 ss (银行与金融科技同句共现) 轨文章级得分, 等权均值。它度量"在最窄同句共现文本口径下, 媒体谈论银行底层金融科技时的语调", 是三条底层技术子集轨中语境最聚焦者, 兼具"文本最聚焦"与"内容限定底层技术"两重收窄。

计算口径与 tech_full/tech_ctx 同构 (ss 轨、等权、均值); ss 轨回退语义镜像 ctx (无同句共现时 content_ss 回退全文并置 ss_is_fallback=True); 由 encode.aggregate_panel 的 locus 分类聚合块生成。子集成员资格同样由 full 轨 locus 标签 (innovation_locus_full == 底层技术) 锁定, 本 ss 轨列只是在该 full-locus 子集内改取 ss 轨语调源, 而非按 ss 轨自身重切 tech 子集; 依赖该 full-locus tech 子集非空。本列与 tech_full、tech_ctx 构成三轨底层技术子集并排臂; 与 _app 子集、全样本 canonical 构成内容子集维度并排臂, 各自 just-identified, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与其它五部词典的 _tone_tech_ss 列构成跨词典平行臂。特别提示: ss 轨最依赖付费缓存播种与共现命中, 叠加 locus 标注稀薄, 早期试跑盘面 T=2 上本列几乎必然整体缺失或零方差, 属预期退化, 全量 T=19 上线后方有效, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 等权 + 均值 + 底层技术子集。它是底层技术子集族里语境最窄的一条, 兼具同句共现的文本聚焦与内容限定底层技术, 在全量样本上最贴近"媒体在同句谈论该银行底层金融科技时的态度"。

## VAR: jiang_2021_tone_app_ctx

【变体差分】
本列是应用场景子集语调族的 ctx 轨成员: 样本限定在 locus 分类为应用场景 (app) 的报道, 对象为 ctx 轨文章级得分, 等权均值。它与 tech 侧互补, 度量"在银行实体上下文窗口的聚焦文本口径下, 媒体谈论银行金融科技应用场景落地时的语调"。app 与 tech 子集互斥, 二者共同覆盖被 locus 分类器标注的报道; 本列只提供 app 侧 ctx 轨水平, 二者之差 (tone_gap) 在别处专列度量作 P4 主 DV。

计算口径与 canonical 同构 (等权、算术均值), 仅被聚合的语调源列换成 ctx 轨得分且样本限定 app 子集; 由 encode.aggregate_panel 的 locus 分类聚合块生成。子集成员资格由 full 轨 locus 标签 (innovation_locus_full == 应用场景) 锁定, 本 ctx 轨列只是在该 full-locus 子集内改取 ctx 轨语调源, 而非按 ctx 轨自身重切 app 子集; 依赖该 full-locus app 子集非空。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 稳健性轨, 样本宇宙是 full 留篇集子集。本列与 app_full、app_ss 构成三轨应用场景子集并排臂; 与底层技术子集 _tech、全样本 canonical 构成内容子集维度并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁不同子集/不同轨变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_app_ctx 列构成跨词典平行臂。相对家族其它列, 本列识别特征是 ctx 轨 + 等权 + 均值 + 应用场景子集。它把文本聚焦与内容限定叠加, 在全量样本上度量"仅在谈论该银行金融科技应用场景的聚焦文本里"媒体的语调, 是 app_full 的更聚焦对照臂。早期试跑盘面 T=2 上 ctx 轨与 locus 标注双重稀薄, 本列几乎必然大量退化, 数值结论以全量 T=19 为准。

## VAR: jiang_2021_tone_app_full

【变体差分】
本列是应用场景子集语调族的 full 轨成员: 样本限定在 locus 分类为应用场景 (app) 的报道, 对象为 full 轨文章级得分, 等权均值。它度量"当媒体谈论银行金融科技的应用场景落地时, 姜富伟等 (2021) 词典语调如何", 是 app 侧内容子集在最完整文本轨上的水平, 与同轨的底层技术子集 tech_full 互补 (二者互斥, 共同覆盖被 locus 标注的报道)。

计算口径与 canonical jiang_2021_tone_full 完全一致 (full 轨、等权、算术均值), 唯一差分是样本被限定在 app 子集 (成员资格由 full 轨标签 innovation_locus_full == 应用场景 决定); 由 encode.aggregate_panel 的 locus 分类聚合块生成, 依赖该 full-locus app 子集非空。tech 与 app 语调之差在别处专列度量作 P4 (locus) 主 DV, 本列只提供 app 侧水平, 不可与该差值混淆。本列与 app_ctx、app_ss 构成三轨应用场景子集并排臂; 与底层技术子集 _tech、全样本 canonical 构成内容子集维度并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁 tech/app/全样本不同子集变体混进同一 over-identified Hansen J; 与其它五部词典的 _tone_app_full 列构成跨词典平行臂。相对家族其它列, 本列识别特征是 full 轨 + 等权 + 均值 + 应用场景子集。它与同轨底层技术子集 tech_full 构成 P4 定位二分的两个语调分量, 单独度量应用场景侧的语调水平, 而二者之差 (定位偏向) 由别处专列承担, 使用时不可混淆水平与差值。早期试跑盘面 T=2 上 locus 标注可能稀薄, 本列常大量 NaN, 结论以全量 T=19 为准。

## VAR: jiang_2021_tone_app_ss

【变体差分】
本列是应用场景子集语调族的 ss 轨成员: 样本限定在 locus 分类为应用场景 (app) 的报道, 对象为 ss (银行与金融科技同句共现) 轨文章级得分, 等权均值。它度量"在最窄同句共现文本口径下, 媒体谈论银行金融科技应用场景时的语调", 是三条应用场景子集轨中语境最聚焦者, 兼具"文本最聚焦"与"内容限定应用场景"两重收窄, 与同轨底层技术子集 tech_ss 互补互斥。

计算口径与 app_full/app_ctx 同构 (ss 轨、等权、均值); ss 轨回退语义镜像 ctx (无同句共现时 content_ss 回退全文并置 ss_is_fallback=True); 由 encode.aggregate_panel 的 locus 分类聚合块生成。子集成员资格由 full 轨 locus 标签 (innovation_locus_full == 应用场景) 锁定, 本 ss 轨列只是在该 full-locus 子集内改取 ss 轨语调源, 而非按 ss 轨自身重切 app 子集; 依赖该 full-locus app 子集非空。本列与 app_full、app_ctx 构成三轨应用场景子集并排臂; 与底层技术子集 _tech、全样本 canonical 构成内容子集维度并排稳健性臂, 各自 just-identified, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与其它五部词典的 _tone_app_ss 列构成跨词典平行臂。特别提示: ss 轨最依赖付费缓存播种与共现命中, 叠加 locus 标注稀薄, 早期试跑盘面 T=2 上本列几乎必然整体缺失或零方差, 属预期退化, 全量 T=19 上线后方有效, 结论一律以全量为准。相对家族其它列, 本列识别特征是 ss 轨 + 等权 + 均值 + 应用场景子集。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Liu, C., Wang, F., & Xue, W. (2023). The annual report tone and return Comovement—Evidence from China's stock market. International Review of Financial Analysis. https://doi.org/10.1016/j.irfa.2023.102610
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
