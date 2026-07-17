---
family_id: F219
columns:
- du_2022_neg_count_ctx
- du_2022_neg_count_full
- du_2022_neg_count_ss
unit: 篇数 (bank-year 内被判为负面的报道计数, 非负整数)
formula: "du_2022_neg_count{track} = Σ_articles 1[du_2022_score{track} < 0]; 逐 bank-year 对该银行该年全部留篇求和 (du_2022_score 正侧含 political_positive 以 0.5 权重计入, 负侧不加权)"
producer: news_process/pipeline/panel/runner.py (物化 _is_du_2022_negative{track}) ; news_process/pipeline/panel/encode.py (聚合 sum)
upstream:
- 22_tone_words.parquet (du_2022_score{full,ctx,ss})
- 21_tone_llms.parquet (full-only 留篇门控 llm_verified_full)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
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
本家族测度 du_2022_neg_count 是"负面报道计数"这一构念在 Du et al. (2022) 中文金融情感词典下的实现: 对某银行某年度的全部留篇, 逐篇判定该词典给出的归一化语调分数是否为负, 再把判为负的篇数逐 bank-year 求和。它与家族 du_2022_tone (词典语调均值) 出自同一部词典、同一批分词与打分, 但落点不同: tone 度量极性的方向与强度均值, neg_count 度量负面语气报道在数量上的绝对累积。之所以把正负两侧分开计数、而不是只保留净语调, 是要避免同一 bank-year 内正负报道相互对冲, 把真实存在的负面信息量掩蔽为零——负面报道的绝对篇数本身携带净语调所丢失的信息量。Du et al. (2022) 的词典是本项目六部并列中文情感词典之一, 其独特之处在于除普通正面 (2,235 词) 与负面 (2,986 词) 外, 另含一类 political_positive 政治正面词 (1,434 词), 以 0.5 权重计入正侧; 该政治词权重仅作用于正侧的加权, 不改变负面词的识别与计数, 因此 du_2022_neg_count 落在词典的负面侧, 与政治词权重敏感性梯子在构念上正交、不交叉。Du2022 与 loughran(中文主译)、jiang_2021、yao_2021、bian_2021、you_2018 构成互为稳健性、不分主次的词典消融面, 各自 just-identified 并排、禁混进同一 over-identified Hansen J。

【方法学与计算】
计算链路分两层。篇章层在 stage 22 tone_words 完成: 对每篇报道的分词序列, 以状态机顺序扫描, 遇否定词设置翻转窗口、遇程度副词设置倍率、遇转折连词激活从句级加权、遇句末标点重置全部句法状态, 命中 Du et al. (2022) 词典的情感词按 base×degree×negation×adversative 累加得篇章语调 du_2022_score{track}; 政治正面词命中时以 0.5 权重计入正侧加权和, 负面词则以单位权重计入负侧; 该分数经加权绝对值之和归一化后恒落在 [-1, +1]。面板层在 runner.py 把 du_2022_score{track} < 0 物化为篇章级二值指示 _is_du_2022_negative{track} (严格小于零方判负, 零分即中性不计入), encode.py 再以 groupby-sum 聚合到 bank-year, 得到本家族三列。单位是篇数、非负整数, 语义是"该行该年被 Du2022 词典判为负面语气的报道有多少篇", 而非负面词的词频总数; 一篇报道无论正文出现多少负面词, 只要归一化后的语调分数小于零就恰记一篇。留篇宇宙统一遵循 2026-06-29 起的 full-only 门控: 一篇报道是否进入银行金科语料只由 llm_verified_full 决定, ctx/ss 轨在此留篇集之上做 conditional-on-full 的逐轨重算, 三轨分母各自独立、不交叉借用。作为计数型中间量, neg_count 主要服务下游: 一是喂入词级/篇级的分歧 (disagreement) 指标, 二是与 n_articles_llm_valid{track} 作分母构成行业负面冲击 industry_neg_shock 及其滞后轨的分子。

【文献定位】
把 neg_count 建成一个显式的计数列, 直接呼应金融文本研究中计数型变量须与连续得分区别对待的方法论关切: 这类变量在分布形态 (零膨胀、右偏) 与恰当估计上不同于连续均值, 应以计数身份披露, 本家族刻意与 du_2022_tone 的连续语调分开落列, 正是为此提供计数原语。词典本身的效度与适用性由 Du et al. (2022) 在 Review of Finance 提供: 该文以语言与领域专用性为核心, 论证通用或跨语迁移的情感词表在中文金融语料上存在系统性偏差, 需从中文财经文本本土归纳专用词典, 并特别刻画了政治正面词信号弱于普通正面词的现象——这正是本项目对其 political_positive 类赋 0.5 权重并做敏感性检验的直接依据。方法学上, 负面语气识别的核心难点在否定处理, Pröllochs, Feuerriegel, & Neumann (2016) 论证了否定范围检测对新闻驱动交易情感测度准确性的实质影响, 本项目状态机的否定窗口与句末重置即是对该关切的工程回应。Todd, Bowden, & Moshfeghi (2024) 对金融文本情感分析文献的综述, 说明词典法在可解释性与领域适配上仍是与机器学习法并存的一支, 支持本项目以多词典并列作稳健性面的设计。Ma, Zhang, & Zhang (2025) 新近构建的中文细粒度投资者情感词典进一步印证: 中文金融语料的情感测度高度依赖领域专用词表, 通用词典存在系统性偏差, 这也是本家族保留 Du2022 等多部中文词典的现实理由。就构念指向的负面信息而言, Piotroski, Wong, & Zhang (2015) 关于中国上市公司负面信息被政治性压制的证据提示: 在中国制度语境下, 媒体负面报道的可见性本身受抑制, 因而对负面报道数量做绝对计数、而非仅看相对占比, 具有独立的信息价值, 也与 Du2022 词典专门为政治色彩词单列并降权的设计动机相互印证。 就以银行为主体归集媒体情感这一做法本身, Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 提供了同域前沿佐证: 该文构造针对特定银行的媒体情感测度, 并检验其与监管行为的关联, 说明把新闻情感按银行主体归集、再进入银行层面实证, 是当前被顶级金融稳定期刊接受的做法, 为本家族在 bank-year 单元上累积负面篇数提供了外部合法性。迁移边界须诚实标注: 原文处于美国银行监管语境 (以监管评级与监管行动为 DV), 本项目为中国商业银行×金融科技报道语境且 DV 另定; 原文情感测度的构造细节与本项目六部中文词典并列、逐篇归一化后再作篇级二值判负的口径不同, 亦未涉及三轨文本或 LLM 投票口径, 更无实质性/象征性的话语分类维度。故它只锚定「以银行为主体的媒体情感计数/极性测度」这一同域应用形态, 不锚定本家族的词典选择与判负阈值。
## VAR: du_2022_neg_count_full

【变体差分】
本列是家族的 canonical 主轨, 采用 full 全文轨: 篇章文本 = 标题 prepend 到正文 (stage 14 ctx_materializer 把原始标题拼接到 content_full 首部, 原始正文内容列不改动), 覆盖报道全篇。判负口径为 du_2022_score_full < 0 的篇数逐 bank-year 求和。它是三轨中承载留篇门控语义的一轨——full-only 门控 (2026-06-29) 下, 一篇报道是否算入银行金科语料只看 llm_verified_full, 因此 full 轨的分母 n_articles_llm_valid 即该行该年的留篇总数, ctx/ss 两轨的行宇宙是它的子集重算。在下游行业负面冲击 industry_neg_shock 的构造里, 无后缀 canonical 分子恒取 neg_count_full、分母取 n_articles_llm_valid, 是主轨口径。full 轨相对 ctx/ss 的差异在于文本范围最宽: 它把整篇报道的负面措辞都纳入 Du2022 词典打分, 因而对同一篇报道更可能因正文任一处的负面表述而被判负, 计数水平系统性高于两条窄轨。须强调本列计的是"被判负的篇数"而非负面词的词频: 一篇报道无论正文出现多少负面词, 只要其归一化后的 du_2022_score_full 小于零就恰记一篇, 等于零 (正负抵消或无匹配) 则记为中性不计入; 这里的正侧含以 0.5 权重计入的政治正面词, 因而与不降权的口径相比, 政治词降权会让净语调略偏负、边际上略增被判负的篇数, 但这一影响仅通过正侧加权间接作用, 负面词的识别本身不受政治权重影响。这一篇级二值化口径使 neg_count_full 天然是非负整数计数, 与 du_2022_tone 的连续均值互补而非冗余。它与 ctx/ss 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified Hansen J。

## VAR: du_2022_neg_count_ctx

【变体差分】
本列采用 ctx 实体窗轨, 是相对 full 主轨的稳健性并排轨。其篇章文本 content_ctx = 标题 prepend 加上以目标实体为中心的上下文窗口 (银行与金科词邻域截取), 而非全篇正文; 判负口径同为 du_2022_score_ctx < 0 的篇数逐 bank-year 求和, 分母则用该轨自身的 n_articles_llm_valid_ctx, 不借 full 轨分母。与 full 的核心差异在文本范围收窄: ctx 只把与目标实体邻近的语句交给 Du2022 词典打分, 剔除了报道中远离银行/金科主题的段落, 因而更贴近"针对该银行的负面语气"而非"整篇报道任意处的负面语气"。这一收窄使 ctx 轨的负面计数水平通常低于 full 轨, 但对主题相关性更纯净, 作为主轨的稳健性检验存在。判负仍是篇级二值化: 对每篇报道只以其 ctx 轨的 du_2022_score_ctx 是否小于零记一篇或零篇, 与 full 轨同为非负整数计数, 差异纯粹来自喂给词典的文本片段不同——full 是全篇、ctx 是实体邻域窗; 政治正面词的 0.5 权重口径在两轨完全一致, 只作用于正侧加权和, 不改变负面词计数。因此 full 与 ctx 之间的计数落差, 直接刻画了"报道整体负面语气"与"针对该银行主题的负面语气"之间的口径差, 这正是把两轨并列而非二选一的价值所在。它与 full/ss 互为稳健性、不分主次, 各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J。留篇集仍是 full-only 门控产出的 conditional-on-full 子集, 逐轨分母独立计算, 不与其它轨交叉借用, 避免用 full 轨分母去除 ctx 轨分子造成的口径混淆。

## VAR: du_2022_neg_count_ss

【变体差分】
本列采用 ss 同句轨, 是三轨中文本口径最严的稳健性并排轨。其篇章文本 content_ss = 标题 prepend 加上银行与金科词在同一句 (±ss_sentence_radius 窗, 默认半径 1) 共现的语句, 判负口径为 du_2022_score_ss < 0 的篇数逐 bank-year 求和, 分母用本轨自身的 n_articles_llm_valid_ss。相对 ctx 更进一步: ss 要求银行与金科概念在句级真正同现, 只把此类高相关语句交给词典打分, 因而定位到"银行与金科同句语境下的负面语气"这一最窄构念。ss 轨遵循镜像 ctx 的回退语义: 当某篇报道不存在银行与金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback=True, 与 ctx 的回退机制对称; 若上游金科 AC 自动机为空则整轨 fallback 全 True 优雅降级。因文本最窄, ss 轨负面计数水平通常最低, 且在浅面板 (T 很小) 上可能出现零方差退化, 属预期而非缺陷。此处须区分 ss 同句轨的口径与 stage 13 共现硬过滤: stage 13 用 ±1 句窗的邻近共现判据决定报道是否留篇, 而 ss 轨用严格同句共现判据物化 content_ss 文本, 二者是不同口径的原语, 不可互相复用。判负口径与另两轨一致, 仍是篇级 du_2022_score_ss 小于零则记一篇的非负整数计数, 政治正面词的 0.5 权重同样只作用于正侧、不改变负面词识别, 只是打分文本被限定在银行与金科真正同句的最高相关语句上, 因而定位的负面语气构念最纯、噪声最小, 代价是可用文本量最少、统计不确定性最大。三轨由宽到窄 (full→ctx→ss) 构成一条口径梯子, 让研究者观察结论对文本相关性阈值的敏感度。它与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 三轨严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
<!-- rendered-citations:end -->
