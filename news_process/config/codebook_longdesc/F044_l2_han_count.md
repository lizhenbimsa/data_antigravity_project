---
family_id: F044
columns:
- avg_han_count_ctx
- avg_han_count_full
- avg_han_count_ss
unit: 汉字数 (CJK 基本区字符个数, bank-year 篇均, 无量纲计数)
formula: "avg_han_count_{track} = mean_{i in bank-year 留篇集} n_han_real_i(track); n_han_real = sum_ch is_cjk(ch), is_cjk = (U+4E00 <= ch <= U+9FFF); track in {full, ctx, ss}"
producer: news_process/core/text/cn_text_utils.py::is_cjk / cn_han_count (计数原语) ; encode H2 段 (文章级 n_han_real 的 bank-year 篇均) ; news_process/pipeline/panel/geography.py (下游消费生成 ln_han_count)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (full-only 留篇门控)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting — A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: "Article 06094"
- doi: 10.1016/j.jcae.2023.100395
  type: journal
  authors: Yu, Y., & Zhao, R.
  year: 2024
  title: "Textual disclosure complexity and analysts' weighting of information"
  venue: Journal of Contemporary Accounting & Economics
  vol: 20
  issue: 1
  pages_or_artno: "Article 100395"
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: Hope, O.-K., Hu, D., & Lu, H.
  year: 2016
  title: "The benefits of specific risk-factor disclosures"
  venue: Review of Accounting Studies
  vol: 21
  issue: 4
  pages_or_artno: 1005-1045
- doi: 10.2308/accr-50725
  type: journal
  authors: Lundholm, R. J., Rogo, R., & Zhang, J. L.
  year: 2014
  title: "Restoring the Tower of Babel: How foreign firms communicate with U.S. investors"
  venue: The Accounting Review
  vol: 89
  issue: 4
  pages_or_artno: 1453-1485
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1002/j.1538-7305.1948.tb01338.x
  type: journal
  authors: Shannon, C. E.
  year: 1948
  title: "A mathematical theory of communication"
  venue: Bell System Technical Journal
  vol: 27
  issue: 3
  pages_or_artno: 379-423
- doi: "10.1017/s0022109023000716"
  title: "Measuring Firm Complexity"
  authors: "Loughran, T., & McDonald, B."
  year: 2023
  venue: "Journal of Financial and Quantitative Analysis"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
- doi: "10.1108/ijaim-09-2025-0294"
  title: "Firm complexity and non-GAAP earnings disclosure"
  authors: "Chen, L., & Sun, L."
  year: 2026
  venue: "International Journal of Accounting & Information Management"
  type: "journal"
new_dois:
  - "10.1017/s0022109023000716"
  - "10.3390/bdcc9100263"
  - "10.1108/ijaim-09-2025-0294"
---

## CORE

【构念与来源】
本家族三列 avg_han_count_full / avg_han_count_ctx / avg_han_count_ss 度量的是"一家银行在某一年被报道的文章, 平均含有多少个汉字"这一篇均文本长度。它属于文本篇幅代理族, 与"文章平均字符数"(avg_article_length, 字符口径, 含数字标点拉丁字母) 及"文章平均词数"(ln_word_count, jieba 分词后的词口径) 并列, 构成同一底层构念"报道长度"的三把不同尺子。三把尺子互为长度稳健性: 字符口径受数字、标点、英文缩写影响, 词口径受分词切分粒度影响, 而汉字口径剔除一切非汉字符号、且不依赖分词, 因而对语料中夹带的表格数字、股票代码、英文机构名等噪声最不敏感, 是三者中最"纯粹"的中文正文体量刻画。白话说, 就是把每篇报道里方方正正的中国字数一数, 再对全年报道取平均: 字数多通常意味着报道更详尽、信息更铺陈, 字数少则往往是简讯式、通稿式的短消息。

数据来源链条如下。文章级底层量是 n_han_real, 即单篇正文中 CJK 汉字的个数; 它由计数原语 is_cjk 逐字符判定后求和得到。计数口径的单一事实源在 core/text/cn_text_utils.py: is_cjk(ch) 判定字符是否落在 CJK 统一表意文字基本区 U+4E00 至 U+9FFF (即 '一' 到 '鿿'), cn_han_count(text) 则是对全文施加该谓词的规范计数 helper。项目刻意把"汉字口径"收敛到这一个定义点, 避免各模块各自硬编码字符区间或裸用 len() 造成计数口径漂移 —— 历史上曾出过把"字符数"误标为"词数"的单位乌龙 (avg_article_length 早期注释误称 MLENGTH 词数), 正是这类口径分裂的教训催生了本 SSOT。需要强调, 项目另有 preprocess/filter.py 使用更窄的区间 U+9FA5 ('龥') 做标题清洗正则, 那是"此处有无中文字符"的清洗判定而非计数口径, 与本族在 U+9FA6 至 U+9FFF 这 90 个汉字上分歧但用途不同, 不互相污染。文章级 n_han_real 与难字率 hard_char_ratio 分子分母中的 n_han 同源同口径, 保证"分子是汉字、分母也是汉字"时两端一致。

【方法学与计算】
从文章级到面板级的聚合发生在 encode 的 H2 段: 对某 bank-year 单元内的留篇集, 逐篇取 n_han_real, 再取算术平均, 得到 avg_han_count_{track}。随后 pipeline/panel/geography.py 消费该列, 施加 ln(1 + x) 变换生成 ln_han_count_{track} 作为回归中更常用的对数长度控制变量 (缓解右偏、便于弹性解读); 本族三列是那一步的直接输入, 保留原始篇均计数以便描述统计与稳健性对照。三条轨道 full / ctx / ss 对应三种被计数的正文文本: full = 标题 prepend 后的全文正文; ctx = 标题加实体上下文窗口; ss = 标题加"银行与金融科技词同句共现"的窄窗片段。三轨文本本身在 stage 14 ctx_materializer 物化 (content_full / content_ctx / content_ss), 计数只是对不同轨道文本各自套用同一 is_cjk 原语, 因此三列语义完全平行、只在"数哪段字"上不同。

留篇门控遵循 full-only 口径 (2026-06-29): 某篇报道是否算作"一篇银行金融科技报道"、从而进入 bank-year 分母, 仅由 full 轨的 llm_verified_full 判定; ctx 与 ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的篇均汉字数仍按各自轨道文本逐列计算。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技词的同句共现时, content_ss 优雅回退为全文 body (ss_is_fallback=True), 与 full 共享 n_articles 分母, 保证 ss 列不因窄窗为空而塌缩为缺失。三轨严格是规格稳健性并排关系: 各自 just-identified, 互为稳健性、不分主次, 禁止把 full / ctx / ss 三列混进同一个 over-identified 的 Hansen J 过度识别检验 (这是全项目三轨、co-primary 双轨嵌入、各类梯子共守的铁律)。本族为纯计数, 不涉及嵌入, 故无 co-primary 的 _lg 孪生列。

【文献定位】
文本篇幅与复杂度作为信息含量代理, 有稳固的实证会计与金融文献传统。You and Zhang (2009) 以 10-K 文件长度刻画报告复杂度, 发现文件越长, 投资者对信息的反应越不充分、事后漂移越大, 奠定了"篇幅即处理成本"的基本逻辑。Lundholm, Rogo, and Zhang (2014) 进一步表明, 需要与投资者跨越语言与制度距离沟通的公司会系统性调整其披露文本的长度与用词, 说明篇幅是一个受策略调节的可观测沟通选择, 而非纯技术噪声。Hope, Hu, and Lu (2016) 从风险因素披露的具体性角度补充: 更长、更具体的文本承载更多决策相关信息, 对定价有增量贡献, 支持把长度作为信息量的一阶代理。近期研究延续并细化了这一脉络: Yu and Zhao (2024) 检验文本披露复杂度如何影响分析师对信息的加权, Lesmy, Muchnik, and Mugerman (2025) 则以跨国比较记录了财务报告复杂度的持续增长及其可比性代价。方法学的更上游锚点是 Shannon (1948) 的信息论: 符号序列的长度与信息量在信息编码意义上直接关联, 为"数字数"这一朴素计数提供了理论合法性。本族把这些以英文 10-K/年报为对象的长度—信息量关系, 迁移到中文银行新闻语料, 并以汉字口径 (而非字符或词) 实现最抗噪的中文篇幅刻画。需要清醒认识局限: 篇均长度只是信息量的粗糙一阶代理, 它无法区分"长而空洞的通稿"与"长而信息密集的深度报道", 这类质量维度须由难字率、套话比率、冗余度等测度分工承担; 本族与那些测度构念正交, 彼此互补而非替代。近期方法学文献进一步把"篇幅即复杂度"的逻辑推向更直接的构造: Loughran and McDonald (2023, Journal of Financial and Quantitative Analysis) 以 10-K 文件体量 (文件大小与篇幅) 为核心构造企业复杂度的文本代理测度, 为本族以篇幅 (汉字计数) 作为报道信息量与复杂度代理提供了最新的方法学锚点。该文比较多种词嵌入与语言模型对中文财经新闻做情感分类与股价预测,文本长度等篇幅特征是其特征工程的一部分,为本族以中文新闻篇幅刻画报道信息量提供了同源语料方法学参照,引用格式为 Chuang, He, and Hu (2025, Big Data and Cognitive Computing)。该文发现企业复杂度与非公认会计准则盈余披露倾向显著正相关,延续了以复杂度—披露关系为核心的实证脉络,支持本族把文本篇幅作为报道信息量与复杂度代理的构念定位,引用格式为 Chen and Sun (2026, International Journal of Accounting & Information Management)。

## VAR: avg_han_count_full

【变体差分】
本列是 full 轨变体, 亦是本族的 canonical 长度尺子。它对 content_full 计数, content_full = 标题 prepend 到全文正文后的完整文本 (原始"内容"列不改动, 标题以 prepend 方式并入)。因此 avg_han_count_full 度量的是整篇报道的中文正文体量, 涵盖导语、主体与结尾各段, 是三轨中信息覆盖最广、也最贴近读者实际阅读篇幅的口径。在留篇门控上它享有特殊地位: full 轨的 llm_verified_full 正是判定该 bank-year 单元有哪些篇进入分母的唯一门控依据 (full-only 口径, 2026-06-29), 因此 avg_han_count_full 的分母 (留篇集) 与后续所有情感、注意力面板列的 n_articles 分母严格一致, 是跨列可比的锚点轨。它是 geography.py 生成 ln_han_count_full 的直接输入, 而 ln_han_count_full 常作为对数篇幅控制变量进入主回归。与 ctx / ss 两轨的关系是: 三者各自 just-identified, 互为长度稳健性、不分主次, full 覆盖全文而 ctx/ss 聚焦局部, 禁止把三列混入同一 over-identified Hansen J 过度识别检验。相对同族的字符口径 avg_article_length 与词口径 ln_word_count, 本列剔除数字、标点、拉丁字母, 不依赖 jieba 分词, 对语料中夹带的股票代码、财务数字、英文机构名最不敏感, 是最纯粹的中文正文长度。因此在同一 bank-year 内, 若全文轨与字符轨、词轨给出方向不一致的长度信号, 通常是数字或英文密度异常所致, 本列可作为诊断参照。作为纯汉字计数, 本列无嵌入, 因而没有 co-primary 的 _lg 孪生列。

## VAR: avg_han_count_ctx

【变体差分】
本列是 ctx 轨变体, 对 content_ctx 计数。content_ctx = 标题 prepend 加上"实体上下文窗口"文本, 即围绕目标银行实体提及位置截取的邻近句子窗口, 而非整篇正文。因此 avg_han_count_ctx 度量的是"与银行实体直接相关的那部分文本"的篇均汉字体量, 系统性地短于或等于 full 轨: 当一篇长报道只在局部段落提及目标银行时, ctx 会剔除与该银行无关的大段内容, 使篇均汉字数明显收缩; 当整篇都围绕该银行展开时, ctx 会趋近 full。这一收缩正是 ctx 轨的构念价值 —— 它把长度的注意力聚焦到"银行相关语境"而非全文泛长度, 从而对"报道对该银行着墨多少"更敏感。留篇门控上, ctx 是 conditional-on-full 测度轨: 其行宇宙为 full 留篇集的子集, 是否入样由 full 轨 llm_verified_full 决定, 但篇均汉字数按 content_ctx 自身文本逐列计算, 不借 full 分子。与 full / ss 的关系恪守三轨铁律: 三者各自 just-identified, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列同样是纯汉字计数、无嵌入, 故无 _lg 孪生列。在 T=2 开发语料上 ctx 可能因窗口稀疏而方差偏低, 属预期退化, 生产 T=18 语料下恢复正常。实证上 avg_han_count_ctx 与 avg_han_count_full 高度相关但非重合, 二者之差近似刻画报道中"非银行语境冗余篇幅", 是与全文轨互补的局部聚焦信号。

## VAR: avg_han_count_ss

【变体差分】
本列是 ss 轨变体, 对 content_ss 计数。content_ss = 标题 prepend 加上"银行与金融科技词严格同句共现"的窄窗片段 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语境最窄、聚焦度最高的口径 —— 它只保留银行与金融科技概念在同一句 (或 ±N 句窄窗) 内同时出现的文本。因此 avg_han_count_ss 度量的是"银行与金融科技交汇语境"的篇均汉字体量, 直接刻画报道对"银行做金融科技"这一交叉主题的正文投入量。关键差分在其回退语义: ss 严格镜像 ctx 的降级逻辑, 当某篇不存在银行与金融科技词的同句共现时, content_ss 优雅回退为全文 body, ss_is_fallback 置 True, 并与 full 共享 n_articles 分母, 保证本列不因窄窗为空而塌缩为缺失。留篇门控同为 full-only、conditional-on-full: 入样由 full 轨 llm_verified_full 决定, 篇均汉字数按 content_ss (含回退) 逐列计算。与 full / ctx 的关系守三轨铁律: 三者各自 just-identified, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列为纯汉字计数、无嵌入, 无 _lg 孪生列。在 T=2 开发语料上, 若同句共现稀疏, ss 大量回退至全文, 数值会趋近 full 轨, 属预期退化; 生产 T=18 语料下同句共现样本充足时, ss 与 full/ctx 的分离度恢复。使用者须注意 ss_is_fallback 指示列: 回退占比高的 bank-year 单元, 其 ss 篇均汉字数已被全文长度稀释, 解读交叉主题体量时应结合该指示列共同判断, 避免把回退噪声误读为交汇语境的真实篇幅。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting — A comparative study. Humanities and Social Sciences Communications, 12, Article 06094. https://doi.org/10.1057/s41599-025-06094-y
Yu, Y., & Zhao, R. (2024). Textual disclosure complexity and analysts' weighting of information. Journal of Contemporary Accounting & Economics, 20(1), Article 100395. https://doi.org/10.1016/j.jcae.2023.100395
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
Lundholm, R. J., Rogo, R., & Zhang, J. L. (2014). Restoring the Tower of Babel: How foreign firms communicate with U.S. investors. The Accounting Review, 89(4), 1453-1485. https://doi.org/10.2308/accr-50725
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
Loughran, T., & McDonald, B. (2023). Measuring Firm Complexity. Journal of Financial and Quantitative Analysis. https://doi.org/10.1017/s0022109023000716
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Chen, L., & Sun, L. (2026). Firm complexity and non-GAAP earnings disclosure. International Journal of Accounting & Information Management. https://doi.org/10.1108/ijaim-09-2025-0294
<!-- rendered-citations:end -->
