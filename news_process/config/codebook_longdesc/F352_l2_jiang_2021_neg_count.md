---
family_id: F352
columns:
- jiang_2021_neg_count_ctx
- jiang_2021_neg_count_full
- jiang_2021_neg_count_ss
unit: 篇数 (bank-year 内被判为负面的报道计数, 非负整数)
formula: "jiang_2021_neg_count{track} = Σ_articles 1[jiang_2021_score{track} < 0]; 逐 bank-year 对该银行该年全部留篇求和"
producer: news_process/pipeline/panel/runner.py (物化 _is_jiang_2021_negative{track}) ; news_process/pipeline/panel/encode.py (聚合 sum, 零填契约见 L2450-L2459 的 `_count_pat` 正则)
upstream:
- 22_tone_words.parquet (jiang_2021_score{full,ctx,ss})
- 21_tone_llms.parquet (full-only 留篇门控 llm_verified_full)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
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
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
  - "10.1016/j.ememar.2024.101234"
  - "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
本家族测度 jiang_2021_neg_count 是"负面报道计数"这一构念在姜富伟、孟令超、唐国豪 (2021) 中文财经情绪词典下的实现: 对某银行某年度全部留篇, 逐篇判定该词典给出的语调分数是否为负, 再把判为负的篇数逐 bank-year 求和, 得到一个非负整数计数列。它与家族 jiang_2021_tone (同词典的篇章语调连续均值) 出自同一部词典、同一批分词与打分流水线, 但落点不同: tone 度量的是极性方向与强度的均值水平, neg_count 度量的是负面语气报道在数量上的绝对累积。之所以把负面一侧单独计数, 而不是只靠净语调均值代表全部信息, 遵循情感研究中把正负两极分列的通行做法——同一 bank-year 内如果只报净语调, 大量正面报道与少量但持续存在的负面报道可能相互对冲, 把真实存在的负面信息掩蔽为接近零的均值, 而计数列能把"有多少篇报道被判为负面"这一独立事实显式暴露出来。姜富伟等 (2021) 的词典由中国学者基于财经媒体文本情绪与股票回报预测的研究构建, 专门针对中文财经语料的措辞习惯与领域术语校准, 与本项目并列使用的 bian_2021、loughran(中文主译)、yao_2021、du_2022、you_2018 等词典构成互为稳健性、不分主次的中文情感词典消融面: 六部词典各自独立打分、各自 just-identified 并排产出 canonical 及消融梯度列, 严禁把不同词典的分数或计数混入同一 over-identified Hansen J 检验, 也不以任一词典为"真值"裁决其余词典。jiang_2021 词典的独特定位在于其构建语境是媒体文本对股票回报的预测力, 因而在情绪词的筛选与打分上天然偏向"市场相关"的措辞, 与 bian_2021 面向会计与金融文本、du_2022 显式区分政治词权重等词典各有侧重, 六词典并列恰好覆盖了中文财经文本情感测度在构建语境与词表来源上的多样性。

【方法学与计算】
计算链路分两层。篇章层在 stage 22 tone_words 完成: 对每篇报道的分词序列, 以状态机顺序扫描, 遇否定词设置翻转窗口、遇程度副词设置倍率、遇转折连词激活从句级加权、遇句末标点重置全部句法状态, 命中 jiang_2021 词典的情感词按 base×degree×negation×adversative 累加得篇章语调 jiang_2021_score{track}, 该分数经加权绝对值之和归一化后恒落在 [-1, +1] 区间, 且可按词典消融梯度 (`{dict}_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}`) 拆出仅含否定/仅含程度副词/仅含转折等子规则变体, 但本家族三列固定消费全语言学规则版本 jiang_2021_score{track} (未经消融拆分)。面板层在 runner.py 把 jiang_2021_score{track} < 0 物化为篇章级二值指示 _is_jiang_2021_negative{track} (严格小于零方判负, 恰为零即中性、不计入负面计数), encode.py 再以 groupby-sum 聚合到 bank-year, 得到本家族三列。聚合层还须满足零填契约: 一个银行某年若没有任何留篇, 该行的计数类和流量类列应显式填 0 而非残留 NaN, 这在 encode.py 中由正则 `_count_pat = re.compile(r'_count(_vw)?_(full|ctx|ss|title)$')` 匹配 jiang_2021_neg_count_full/_ctx/_ss 等带轨道后缀的计数列名实现 (该正则历经多轮修复才覆盖到逐词典/逐模型计数列, 早期版本仅锚定裸 pos_count/neg_count 会遗漏本家族这类带词典前缀的计数列, 现已改为后缀匹配保证覆盖); 零填不适用于均值/比例类列 (以 avg_/mean_ 前缀排除), 因其空 bank-year 语义是"无观测"而非"观测值为零"。留篇宇宙统一遵循 2026-06-29 起的 full-only 门控: 一篇报道是否进入银行金科语料只由 llm_verified_full 决定, ctx/ss 两轨在此留篇集之上做 conditional-on-full 的逐轨重算, 三轨分母各自独立计算、不交叉借用。作为计数型中间量, neg_count 是负面信息累积程度的直接原语, 供下游需要"负面报道数量"而非"负面语气强度均值"的场景消费, 例如行业负面冲击构造中作分子成分之一。

【文献定位】
把 neg_count 建成一个显式的、非负整数的计数列, 呼应了金融文本研究中把计数类信息与连续得分区分处理的做法——本家族刻意与 jiang_2021_tone 的连续语调分开落列, 为下游提供计数原语而非仅依赖均值代表全部信息。词典本身的构建依据是姜富伟、孟令超、唐国豪 (2021) 发表于《经济学(季刊)》的媒体文本情绪与股票回报预测研究, 该文从中国财经媒体语料出发构建情绪词表并验证其对股票回报的预测力, 是本项目采用它判定负面语气的直接依据; 该词典与 Bian, Jia, Li, & Yan (2021) 针对会计与金融文本构建的中文情感词典并列, 后者的方法论——从大规模中文财经语料归纳构建领域专用词表——为 jiang_2021 词典的构建逻辑提供了同类参照。方法学上, 负面语气识别的核心难点在否定处理, Pröllochs, Feuerriegel, & Neumann (2016) 论证了否定范围检测对新闻驱动交易情感测度准确性的实质影响, 本项目状态机的否定窗口与句末重置机制即是对该关切的工程回应, 也是 jiang_2021 词典打分流程与 bian_2021 等其余词典共用同一套语言学规则引擎的原因。Todd, Bowden, & Moshfeghi (2024) 对金融文本情感分析文献的系统综述指出, 词典法在可解释性与领域适配性上仍是与机器学习/大语言模型法并存的重要一支, 支持本项目以多部中文词典并列作稳健性面而非单一"最优"词典的设计取向。就构念指向的负面信息本身而言, Piotroski, Wong, & Zhang (2015) 发表于《Journal of Accounting Research》的研究提供了关键的制度背景: 该文以中国上市公司为样本证明负面信息在政治激励下系统性地被压制、可见度更低, 这意味着在中国语境下媒体负面报道的绝对数量本身承载着独立于比例指标的信息价值, 也是本家族选择对负面报道做绝对计数、而非仅报负面占比的现实依据。Ma, Zhang, & Zhang (2025) 新近构建的中文细粒度投资者情感词典进一步印证中文金融文本情感测度对领域专用词表的高度依赖, 支持本项目保留 jiang_2021 等多部中文词典而非仅采用英文舶来词典翻译版的设计选择。Xu, Hua, & Zhang (2025, Emerging Markets Review) 该文构建官方媒体负面情绪指数(NegGovOp)并证明其对中国股市回报反转与散户悲观抛售行为的预测力, 为本家族按负面报道数量单独计数(而非仅报净语调)的设计取向提供了新近实证支持。Chuang, He, & Hu (2025, Big Data and Cognitive Computing) 该文系统比较词嵌入与大语言模型在中文财经新闻情感分类与股价预测中的表现, 印证了词典法与机器学习/LLM法在中文财经文本情感测度上并存互补的方法论定位。

## VAR: jiang_2021_neg_count_full

【变体差分】
本列是家族的 canonical 主轨, 采用 full 全文轨: 篇章文本 = 标题 prepend 到正文 (stage 14 ctx_materializer 把原始标题拼接到 content_full 首部, 原始正文内容列不改动), 覆盖报道全篇。判负口径为 jiang_2021_score_full < 0 的篇数逐 bank-year 求和, 分母 (若下游需要占比化) 取该轨自身的 n_articles_llm_valid_full。它是三轨中承载留篇门控语义的一轨——full-only 门控 (2026-06-29) 下, 一篇报道是否算入银行金科语料只看 llm_verified_full, 因此 full 轨的分母即该行该年的留篇总数, ctx/ss 两轨的行宇宙是它的子集重算, 不可反过来把 ctx/ss 轨的分母替换为 full 轨。full 轨相对 ctx/ss 的差异在于喂给词典打分的文本范围最宽: 它把整篇报道的负面措辞都纳入 jiang_2021 词典扫描, 因而对同一篇报道更可能因正文任一处出现负面表述而被判负, 计数水平系统性高于两条窄轨。需强调本列计的是"被判负的篇数"而非负面词的词频总数: 一篇报道无论正文出现多少个 jiang_2021 词典中的负面词, 只要其归一化后的 jiang_2021_score_full 小于零就恰记一篇, 等于零 (正负抵消或无匹配命中) 则记为中性、不计入。这一篇级二值化口径使 neg_count_full 天然是非负整数计数, 与 jiang_2021_tone_full 的连续均值互补而非冗余。它与 ctx/ss 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified Hansen J。

## VAR: jiang_2021_neg_count_ctx

【变体差分】
本列采用 ctx 实体窗轨, 是相对 full 主轨的稳健性并排轨。其篇章文本 content_ctx = 标题 prepend 加上以目标实体为中心的上下文窗口 (银行与金科词邻域截取), 而非全篇正文; 判负口径同为 jiang_2021_score_ctx < 0 的篇数逐 bank-year 求和, 分母用该轨自身的 n_articles_llm_valid_ctx, 不借 full 轨分母。与 full 的核心差异在文本范围收窄: ctx 只把与目标实体邻近的语句交给 jiang_2021 词典打分, 剔除了报道中远离银行/金科主题的段落, 因而更贴近"针对该银行的负面语气"而非"整篇报道任意处的负面语气"。这一收窄使 ctx 轨的负面计数水平通常低于 full 轨, 但对主题相关性更纯净, 作为主轨的稳健性检验存在。判负仍是篇级二值化: 对每篇报道只以其 ctx 轨的 jiang_2021_score_ctx 是否小于零记一篇或零篇, 与 full 轨同为非负整数计数, 差异纯粹来自喂给 jiang_2021 词典的文本片段不同——full 是全篇、ctx 是实体邻域窗。因此 full 与 ctx 之间的计数落差, 直接刻画了"报道整体负面语气"与"针对该银行主题的负面语气"之间的口径差, 这正是把两轨并列而非二选一的价值所在。它与 full/ss 互为稳健性、不分主次, 各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J。留篇集仍是 full-only 门控产出的 conditional-on-full 子集, 逐轨分母独立计算, 不与其它轨交叉借用, 避免用 full 轨分母去除 ctx 轨分子造成的口径混淆。

## VAR: jiang_2021_neg_count_ss

【变体差分】
本列采用 ss 同句轨, 是三轨中文本口径最严的稳健性并排轨。其篇章文本 content_ss = 标题 prepend 加上银行与金科词在同一句 (±ss_sentence_radius 窗, 默认半径 1) 共现的语句, 判负口径为 jiang_2021_score_ss < 0 的篇数逐 bank-year 求和, 分母用本轨自身的 n_articles_llm_valid_ss。相对 ctx 更进一步: ss 要求银行与金科概念在句级真正同现, 只把此类高相关语句交给 jiang_2021 词典打分, 因而定位到"银行与金科同句语境下的负面语气"这一最窄构念。ss 轨遵循镜像 ctx 的回退语义: 当某篇报道不存在银行与金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback=True, 与 ctx 的回退机制对称、共享 n_articles 分母口径; 若上游金科 AC 自动机为空 (FINTECH_AC=None) 则整轨 *_is_fallback 全 True 优雅降级。因文本最窄, ss 轨负面计数水平通常最低, 且在浅面板 (T 很小的开发样本) 上可能出现零方差退化, 属预期而非缺陷。此处须区分 ss 同句轨的判负口径与 stage 13 共现硬过滤: stage 13 用 ±1 句窗的邻近共现判据 (`has_bank_fintech_cooccurrence_within_radius`) 决定报道是否留篇, 而 ss 轨用严格同句共现原语 (`extract_bank_fintech_cooccurrence`) 物化 content_ss 文本, 二者是不同口径的原语, 不可互相复用。判负口径与另两轨一致, 仍是篇级 jiang_2021_score_ss 小于零则记一篇的非负整数计数, 只是打分文本被限定在银行与金科真正同句的最高相关语句上, 因而定位的负面语气构念最纯、噪声最小, 代价是可用文本量最少、统计不确定性最大。三轨由宽到窄 (full→ctx→ss) 构成一条口径梯子, 让研究者观察结论对文本相关性阈值的敏感度。它与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 三轨严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
