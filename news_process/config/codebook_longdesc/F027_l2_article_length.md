---
family_id: F027
columns:
- avg_article_length
- avg_article_length_z
unit: ln(1+平均字符数) (avg_article_length, 无量纲对数长度); 年内标准差单位 (avg_article_length_z, 无量纲)
formula: "avg_article_length = ln(1 + avg_doc_length); avg_doc_length = bank-year mean of doc_length; doc_length = len(str(内容)) = Unicode 字符数。avg_article_length_z = 年度截面 z-score = (avg_article_length − μ_year) / σ_year, 仅在 n_articles>0 行、年内有效观测 ≥3 且 σ≥1e-10 时赋值, 否则 NaN"
producer: pipeline\panel\geography.py (compute_geography_features 文章平均长度段 + standardize_panel_variables) ; pipeline\panel\codebook.py (VariableMetadata 注册)
upstream:
- 11_news_bank.parquet (doc_length = len(str(内容)) Unicode 字符数)
- 40_panel_export_main (avg_doc_length = bank-year mean(doc_length); n_articles 门控)
citations:
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: Article 102325
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: Article 112803
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: Article 101126
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: Emerging Markets Review
  vol: 64
  pages_or_artno: Article 101234
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: Article 113917
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行—年度层面新闻报道的平均篇幅长度, 是文本信息量的一阶代理。构念根植于财经文本"披露长度/冗长度"(disclosure length / verbosity)传统: 一篇报道越长, 通常承载越多的事实描述、背景铺陈与细节, 但过长也可能意味着模板化铺陈或信息稀释。将篇幅作为文档级属性纳入银行—年度面板, 目的有二: 其一作为独立的报道信息量刻画; 其二作为回归中的长度控制变量, 隔离其它文本测度(如情感、套话比率、冗余度、罕见词占比)与篇幅之间的机械相关。数据来源为原始报道正文字段: 上游 stage 11 (news_bank) 对每篇报道计算 doc_length = len(str(内容)), 即报道正文的 Unicode 字符数; 该篇级长度经 stage 40 面板导出在银行—年度层面取均值得到 avg_doc_length, 再由 geography 段做对数压缩生成 avg_article_length。分母口径与留篇门控一致: 只有被判为"银行金科报道"(full-only 留篇门控, 2026-06-29 口径, 即 llm_verified_full 为真的报道)进入银行—年度聚合, 零新闻行保持缺失, 不以零篇幅冒充。

【方法学与计算】
计算链路分三步。第一步篇级长度: doc_length = len(str(内容)), 为 Unicode 字符数, 而非分词后的词数——这一点在 2026-06-05 做过明确的单位勘误。早期注释曾把该量标为 MLENGTH(文章词数)并援引词数口径文献, 属单位误标; 在中文语料下, 由于一个词往往由多个汉字构成, 字符数通常明显多于分词后的词数, 二者虽高度相关却分属不同量纲, 本家族严格锁定为字符口径, 不援引任何具体换算比率作为经验常数。字符口径的优点是完全独立于分词器的切分策略与词表版本, 不因分词工具或词典更迭而漂移, 从而使长度度量在跨版本、跨语料重处理时保持字节级可复现的确定性; 词口径 ln_word_count 与汉字口径 ln_han_count 则分别把切分单位换成 jieba 分词词与 CJK 汉字, 作为并排的长度稳健轨与字符口径互证。第二步银行—年度聚合: avg_doc_length 为该银行该年所有留篇报道 doc_length 的算术均值。第三步对数压缩: avg_article_length = ln(1 + avg_doc_length), 采用 log1p 而非裸对数, 使零值安全并压缩右偏长尾, 让长度进入线性回归时近似满足同方差与正态残差假设。该对数长度是无量纲量, 取值区间 [0, +∞)。avg_article_length_z 则是在此基础上做的年度截面标准化(Fama–MacBeth 传统): 逐年在有新闻覆盖的银行子样本内, 把 avg_article_length 减去当年截面均值再除以当年截面标准差, 使系数可直接读作"1 个年内标准差的篇幅变化对应因变量若干单位变动"; 有效性守卫要求该年截面有效观测不少于 3 且标准差不低于 1e-10, 否则该年该列置 NaN, 零新闻行始终为 NaN。

【文献定位】
篇幅长度是财经文本量化研究的基础文档属性。在财经披露的经典文本分析框架中(Loughran & McDonald, 2011), 文档长度(以文件规模刻画)本身即被视为一项与语调、可读性并列的文本测度, 且与其它文本属性存在系统性机械相关, 需作为规模维度加以隔离——这正是本家族把篇幅同时作为独立信息量代理与长度控制项纳入面板的直接文献依据。在以中文官方媒体与财经新闻为语料的资本市场研究中(Xu, Hua & Zhang, 2025; Xu, Li, Hua & Ren, 2024), 报道文本被系统抽取为情感、语调与信息量指标, 而文本长度是这些指标不可回避的规模维度与控制项。以新闻标题与正文差异刻画情绪分歧的研究(Garcia, 2025)进一步说明, 标题与全文的篇幅结构本身携带信息, 长度不是中性的背景噪声。在以大语言模型解码央行沟通与新闻文本的前沿工作中(Chen, Granville & Matousek, 2026), 文本冗长度与信息密度同样是刻画沟通策略的一维。就时序含义而言, 新闻情感与文本属性具有跨期持续性(Aksoy-Yurdagul, Buchner & Zareei, 2026), 这为把长度纳入面板并做年度截面标准化提供了方法学动机——年内标准化剥离逐年媒体环境的系统性漂移, 使跨年可比。需强调本家族的长度稳健梯子纪律: avg_article_length 为字符口径, 与同源的词口径 ln_word_count、汉字口径 ln_han_count 互为长度稳健的并排轨, 三口径各自 just-identified 并排、互为稳健性、不分主次, 严禁把三口径长度混进同一 over-identified Hansen J 过度识别检验; 它们回答的是"长度用哪种计量单位度量都不改变结论"这一稳健性问题, 而非相互提供额外工具变量。

## VAR: avg_article_length

【变体差分】
本列为家族 canonical, 是字符口径的对数篇幅长度, 即 avg_article_length = ln(1 + avg_doc_length), 其中 avg_doc_length 为银行—年度内所有留篇报道 Unicode 字符数(doc_length = len(str(内容)))的均值。它保留原始的对数长度水平, 是可跨银行、跨年直接比较绝对篇幅的量, 单位为无量纲对数字符数, 取值 [0, +∞)。与家族内其它长度口径的精确区分: 相对词口径 ln_word_count(以 jieba 分词词数为底)与汉字口径 ln_han_count(仅计 CJK 汉字、剔除数字标点拉丁字符), 本列不做分词、不剔非汉字符号, 因此包含数字、标点与拉丁字母在内的全部字符, 是最"原始"的字符规模口径。三口径互为长度稳健、各自 just-identified 并排、不分主次, 禁混进同一 over-identified Hansen J。相对下方的标准化孪生列 avg_article_length_z, 本列是未标准化的水平量: 它不做年度截面去均值除标准差, 因而保留了逐年媒体篇幅整体漂移的信息, 适合需要绝对篇幅水平或自行控制年份固定效应的设定; 而 z 列适合需要"1 年内标准差"可比刻度的 Fama–MacBeth 型截面设定。本列是 track-agnostic 的标量长度度量, 不随 full/ctx/ss 三轨分裂(篇幅在留篇门控口径下按 full 轨聚合), 因此不带轨道后缀。零新闻的银行—年度行保持 NaN, 不以零篇幅充数。

## VAR: avg_article_length_z

【变体差分】
本列是 canonical 列 avg_article_length 的年度截面标准化(z-score)孪生, 由 standardize_panel_variables 在面板导出步骤 7b 生成, 方法学锚点为 Fama–MacBeth 截面标准化传统。差分语义完全在"标准化"这一变换上: 逐个年度截面, 在有新闻覆盖(n_articles>0)的银行子样本内, 取 avg_article_length 减去当年截面均值再除以当年截面标准差, 得到均值 0、单位方差的 z 值; 原始列 avg_article_length 保持不变并列存在。有效性守卫: 某年截面有效观测数不足 3、或该年截面标准差低于 1e-10(近似零方差)时, 该年该列不赋值而置 NaN; 零新闻行(n_articles 不大于 0)始终 NaN。该变换的作用是让回归系数可直接解读为"篇幅每变动 1 个年内标准差, 因变量变动 β 个单位", 并剥离逐年媒体环境导致的截面均值与离散度漂移, 使跨年系数可比——这与新闻文本属性存在跨期持续性、需在年内做可比化的方法学考量一致。与本列区分的是 canonical 水平列: 水平列保留绝对对数篇幅、可跨年比较原始长度, z 列则牺牲绝对水平换取年内可比刻度, 二者是同一构念的两种呈现, 通常不应同时作为解释变量进入同一回归右端(标准化仅是线性再缩放, 二者高度共线)。本列同为 track-agnostic 标量, 不带 full/ctx/ss 轨道后缀。

<!-- rendered-citations:begin -->
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, Article 102325. https://doi.org/10.1016/j.intfin.2026.102325
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, Article 112803. https://doi.org/10.1016/j.econlet.2025.112803
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review, 64, Article 101234. https://doi.org/10.1016/j.ememar.2024.101234
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, Article 113917. https://doi.org/10.1016/j.enpol.2023.113917
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66, 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
