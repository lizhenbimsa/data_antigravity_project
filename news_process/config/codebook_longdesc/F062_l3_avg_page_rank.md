---
family_id: F062
columns:
- avg_page_rank
unit: 版位序数 (rank ∪ NaN, 越小越显著)
formula: "avg_page_rank = bank-year mean of page_rank; page_rank = 叠字母序 × 100 + 页码 (越小越靠前显著)"
producer: news_process/pipeline/filtering/news_salience.py ; news_process/pipeline/panel/codebook.py
upstream:
- 11_news_bank.parquet (page_rank article 级列)
- 40_panel_yearly.parquet (encode bank-year 聚合)
citations:
- doi: 10.1111/jofi.13287
  type: journal
  authors: Fedyk, A.
  year: 2024
  title: "Front-page news: The effect of news positioning on financial markets"
  venue: Journal of Finance
  vol: 79
  issue: 1
  pages_or_artno: 5-33
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/j.1540-6261.2004.00662.x
  type: journal
  authors: Antweiler, W., & Frank, M. Z.
  year: 2004
  title: "Is all that talk just noise? The information content of internet stock message boards"
  venue: The Journal of Finance
  vol: 59
  issue: 3
  pages_or_artno: 1259-1294
new_dois: []
---

## CORE

【构念与来源】
avg_page_rank 属新闻体裁显著性 (news-genre salience) 测度族, 刻画目标银行在报纸物理版位上的平均显著程度。构念的直觉是: 报纸的版面与页码不是中性的排版细节, 而是编辑对一条报道重要性的显性排序, 也是读者注意力的物理代理 —— 登在头版或 A 叠前几页的报道被更多读者看到、被赋予更高的权威暗示, 而被埋在后叠、深页的报道则大概率被略过。据此本列把"目标银行今年被报道时, 平均落在多靠前的版位"编码为一个可回归的连续变量。数据来源是原始新闻语料本就现成、却在本项目此前仅用于广告过滤而从未派生为特征的版面与页号字段: 在 stage 11 (news_salience) 用纯字符串与正则解析物化为 article 级列 page_rank, 再经 encode 在 stage 40 聚合到 bank-year 面板。整族属 $0 测度 (无 LLM、无嵌入、无新依赖, 只做确定性文本解析), 因此不涉及付费缓存与留篇门控的在线成本。

【方法学与计算】
article 级原语 page_rank 的构造式为"叠字母序 × 100 + 页码": 先把版面代码里的叠区字母 (A 叠、B 叠…) 映射为以零为起点的序号 (A→0、B→1、C→2…, 源码取 ord(letter) − ord('A'), 属 0-based 而非从一计数) 并乘以 100 作为高位, 再加上该叠内的页码作为低位, 从而得到一个"越小越靠前、越显著"的单调序数。据此口径, A 叠第 3 页的 page_rank = 0×100 + 3 = 3, B 叠第 5 页 = 1×100 + 5 = 105, F 叠第 20 页 = 5×100 + 20 = 520, 头版 A 叠总落在最小的低百位区间, 后叠深页则被推向更大的序数, 与"越小越显著"的方向语义一致; 须特别提醒论文写作与制表勿把该映射误记为从一起算 (A→1), 否则会把每篇报道的 page_rank 整体高估一个百位、令头版与内页的量级对比失真。bank-year 层面的 avg_page_rank 即对该银行当年全部命中报道的 page_rank 取算术均值 (mean)。取值域为 rank ∪ NaN: 当某篇报道的版面与页号两者皆缺失时, 该篇 page_rank 记为 NaN, 均值聚合自动跳过 NaN 而非以零或哨兵值污染分母 —— 这一"字段不适用 (如网络源天然无版面概念) 不等同于未上头版"的缺失语义, 是 fix(omni-g-entity-13, 2026-06-11) 刻意做出的区分。本列为 track-agnostic 单轨测度: 版位是报道的元数据属性, 与文本内容的 full/ctx/ss 三轨切分正交, 故不派生 _full/_ctx/_ss 分轨, 也没有 co-primary 嵌入的 _lg 孪生列 (与 surface_staleness 同属非嵌入 carve-out)。诚实限定须写入论文披露: 不同报纸的 A/B 叠语义并不一致, 本版以 (叠字母序 × 100 + 页码) 作单一近似规范化, 全量多报源下宜先构建各报源的叠语义映射; 多字母叠号 (如 'AII06') 按首个 [字母]?数字 序列解析, 可能被误析为后续单字母叠而使 page_rank 偏大, 同属单一近似的披露范围。就构念区分而言, 版位显著性刻画的是投入端 (报道被放在哪) 的编辑排序, 与媒体级的 media_authority (谁在报道)、产出端的 herd_decay (报道被重复了多少) 相互正交, 三者度量的是新闻生产链条上不同环节的信息, 不应互相替代。

【文献定位】
版位作为注意力代理的因果证据由 Fedyk (2024) 系统建立: 该研究利用报纸头版定位的准随机变异, 证明同一条新闻被放上头版 (相对被放在内页) 会显著放大其对金融市场的影响, 从而把"版位不只是相关、而是有独立因果效力的注意力放大器"这一命题坐实, 直接支撑本列以版位序数刻画显著性的构念合法性。更早的 Antweiler and Frank (2004) 从信息内容角度论证了新闻类文本 (message board 帖子) 承载可被市场吸收的增量信息、而非纯噪声, 为"报道显著性差异应当被编码为特征而非丢弃"提供了信息论依据。在测度方法论层面, 本族坚持纯解析 ($0 字典/正则) 而非机器学习的路线选择, 呼应 Frankel, Jennings, and Lee (2022) 对字典法与机器学习法在披露情感测度上互为稳健、各有适用边界的比较 —— 版位解析的透明性、可复现性与零成本, 正是把它作为注意力测度基线而非黑箱替代的理由。上述三条锚点分别从因果识别、信息含量与方法透明三个侧面, 共同界定了 avg_page_rank 在文献谱系中的位置。

## VAR: avg_page_rank

【变体差分】
avg_page_rank 是本单列家族的唯一列, 也是版位显著性族中"连续序数"一支的 canonical 度量, 与同族的二值频率列 frac_front_page (是否登上头版/要闻或 A 叠首页的比例) 和 frac_front_section (版面是否含头版/要闻/头条关键词的比例) 构成互补而非替代: 后两者只回答"是否够靠前"的二分问题, 本列则保留了版位的完整梯度信息 —— 一篇 A 叠第 3 页与一篇 F 叠第 20 页在二值指标下可能同判为"非头版", 但在 avg_page_rank 下相差一个数量级。这一梯度保留正是选择连续序数而非阈值化二值的核心差分理由。方向语义上须格外注意: 本列越小代表越显著 (越靠前), 与同族多数"越大越显著"的比例列方向相反, 回归解读与系数符号预期须据此反向对齐, 制表时其标签明确写作 "Avg Page Prominence (lower=front)" 以防误读。轨道与判据维度上, 本列为 track-agnostic 单轨, 不含 full/ctx/ss 分轨、不含 _lg 嵌入孪生、不含阈值或判据梯子, 因此不存在"多轨/多梯子并排、禁混同一 over-identified Hansen J"的稳健性配置问题 —— 它是一条独立的元数据显著性信号。聚合口径为 bank-year 算术均值, 缺失 (版面页号皆缺) 逐篇置 NaN 并在均值中跳过, 保证"字段不适用"的报道不被误计为"未上头版"。其构念与 media_authority (媒体级权威)、herd_decay (产出端重复度) 严格正交, 三者不可互相回归替代, 使用时应作为刻画报道物理显著性的独立控制或处理变量纳入模型。

<!-- rendered-citations:begin -->
Fedyk, A. (2024). Front-page news: The effect of news positioning on financial markets. Journal of Finance, 79(1), 5-33. https://doi.org/10.1111/jofi.13287
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. The Journal of Finance, 59(3), 1259-1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x
<!-- rendered-citations:end -->
