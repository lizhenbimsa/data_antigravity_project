---
family_id: F546
columns:
- surface_highstale_ctx
- surface_highstale_full
- surface_highstale_ss
unit: 银行-年占比 (无量纲, 值域 [0,1]; 该行-年内字面高陈旧文章占有效文章的比例)
formula: "文章级 surface_highstale_{track} = 1[surface_staleness_{track} > 0.9]; 其中 surface_staleness = 该文章字符级 3-gram shingle 的 MinHash (num_perm=128) 对过去 7 日窗 [d-7d, d) 内 (严格排除同日) 文章经 MinHashLSHForest 检索得到的最大近似 Jaccard 相似度。银行-年面板列 = 该行-年内 surface_highstale 的均值 (占比), 分母 = 字面陈旧度非 NaN 的有效文章数。"
producer: news_process/pipeline/text/article_staleness.py::aggregate_to_bank_year (阈值化) ← compute_surface_staleness (相似度)
upstream:
- 14_news_with_ctx.parquet (三轨文本 content_{full,ctx,ss})
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: The Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1016/j.jacceco.2020.101344
  type: journal
  authors: Blankespoor, E., deHaan, E., & Marinovic, I.
  year: 2020
  title: "Disclosure processing costs, investors' information choice, and equity market outcomes: A review"
  venue: Journal of Accounting and Economics
  vol: 70
  issue: 2-3
  pages_or_artno: 101344
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1016/j.jacceco.2017.07.002
  type: journal
  authors: Dyer, T., Lang, M., & Stice-Lawrence, L.
  year: 2017
  title: "The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation"
  venue: Journal of Accounting and Economics
  vol: 64
  issue: 2-3
  pages_or_artno: 221-245
- doi: 10.2308/acch-51240
  type: journal
  authors: Cazier, R. A., & Pfeiffer, R. J.
  year: 2016
  title: "Why are 10-K filings so long?"
  venue: Accounting Horizons
  vol: 30
  issue: 1
  pages_or_artno: 1-21
- doi: 10.1016/j.jacceco.2015.09.002
  type: journal
  authors: Lang, M., & Stice-Lawrence, L.
  year: 2015
  title: "Textual analysis and international financial reporting: Large sample evidence"
  venue: Journal of Accounting and Economics
  vol: 60
  issue: 2-3
  pages_or_artno: 110-135
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: Tetlock, P. C.
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: The Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.ememar.2025.101309"
  type: journal
  authors: "Huang, R., Chen, X., & Wu, C."
  year: 2025
  title: "The textual similarity of news content and stock return synchronicity"
  venue: "Emerging Markets Review"
- doi: "10.1016/j.jeconbus.2025.106258"
  type: journal
  authors: "Wang, Y., Chen, R., Gao, X., & Qi, W."
  year: 2025
  title: "Text similarity in analyst reports and stock price synchronization"
  venue: "Journal of Economics and Business"
- doi: "10.1016/j.irfa.2024.103579"
  type: journal
  authors: "Duan, J., Kou, F., Wang, Z., & Wei, Y."
  year: 2024
  title: "When echoes surpass voices: Market reaction to forwarded news"
  venue: "International Review of Financial Analysis"
- doi: "10.2308/tar-2023-0191"
  type: journal
  authors: "Merkley, K. J., Pacelli, J., Sun, F., & Twedt, B. J."
  year: 2024
  title: "Common Media Holding Companies and the Uniqueness of Business Press Content"
  venue: "The Accounting Review"
new_dois:
  - "10.1016/j.ememar.2025.101309"
  - "10.1016/j.jeconbus.2025.106258"
  - "10.1016/j.irfa.2024.103579"
  - "10.2308/tar-2023-0191"
---

## CORE

【构念与来源】
本家族刻画的是"字面高陈旧报道占比"这一新闻信息新鲜度构念。其出发点是: 一篇银行金融科技报道在措辞与字面表述层面, 有多大程度只是对过去一小段时间内已经出现过的报道的机械重复。若一篇报道的字面内容 (字符组合、成句方式) 与其发表前七天内的某篇旧报道高度雷同, 则它对市场几乎不带来增量信息, 属于"炒冷饭"式的旧闻重印; 反之, 与近期报道字面相距较远的报道更可能承载新信息。家族列把这一逐篇的连续字面陈旧度得分在给定高阈值上二值化, 再在银行-年层面聚合为占比, 得到"该银行该年度报道中字面高陈旧者所占的份额"。这一构念直接呼应金融学中关于陈旧信息与投资者反应的经典问题: Tetlock (2011) 系统检验了投资者是否会对被媒体重复转载的陈旧信息做出反应, 并以旧文的词面重复程度作为信息新鲜度的操作化度量。本家族把这一思想迁移到中文银行金融科技报道语料, 并刻意坚守"字面"这一层面——它捕捉的是通稿转载、同稿多发、模板化写作所留下的表述指纹, 与其语义孪生家族 (F490 semantic_highstale) 在向量空间捕捉的"意思重复"互为补充而非替代。

数据来源与生产链路如下。上游 stage 14 (ctx_materializer) 为每篇报道物化三轨文本 content_{full,ctx,ss} (标题以 prepend 方式并入); stage 26 (article_staleness) 调用 compute_surface_staleness, 对每篇报道在其字符指纹空间内检索过去七天窗口的历史报道并计算最大近似 Jaccard 相似度, 得到逐篇连续得分 surface_staleness_{track}; 最终在银行-年聚合阶段, aggregate_to_bank_year 先把连续得分按阈值 0.9 二值化为文章级 surface_highstale 指示, 再对每个 (target_bank, year) 组取均值, 得到本家族的三个银行-年占比列 surface_highstale_{full,ctx,ss}。生产函数的权威位置是 pipeline/text/article_staleness.py: 相似度计算在 compute_surface_staleness, 二值化与聚合在 aggregate_to_bank_year。须特别强调一个与语义家族的根本差异: 字面轨完全不依赖任何句向量嵌入, 它是 MinHash 字符 shingle 的纯 CPU 计算, 因此没有 co-primary 双轨嵌入的 _lg 孪生——这是刻意的 carve-out, 字面重复与嵌入几何无关, 不存在"换嵌入厂商互证"的概念。

【方法学与计算】
逐篇字面陈旧度的计算口径必须精确复述, 因为其中若干设定是可复现性与效度的承重点。第一, 指纹构造采用字符级 3-gram shingle (_char_shingles): 直接在字符序列上滑动取三字窗口, 对中文友好且不依赖分词, 从而规避了 jieba 切词歧义对相似度的扰动; shingle 集合再经 MinHash (num_perm=128 个置换哈希) 压缩为定长签名, 两篇文章 MinHash 签名的相符比例是其 shingle 集合真实 Jaccard 相似度的无偏近似。第二, 近邻检索用 MinHashLSHForest (局部敏感哈希森林): 若对全语料两两比对, 40 万篇 × 7 天窗口约 5000 个候选将产生约 20 亿次比较不可行, LSH 森林把该复杂度降到约 7N, 使工业规模的重复检测可行。第三, 窗口为日粒度的 [d-7d, d), 且严格排除同日行: 流水线会把同一篇报道 (同 docid) 按其匹配到的多家银行复制成多行, 若窗口含同日更早行, 则重复行内部相似度恒为 1.0, 使字面陈旧度机械等于 1.0, 高陈旧信号几乎纯由该复制副作用驱动, 且哪一行取到 1.0 依赖任意输入行序; 排除同日后, 字面轨与语义轨的窗口与 NaN 口径一致。第四, 窗口为空 (含语料首周、或近邻仅为同日行) 的文章其连续得分为 NaN, 在下游聚合中被 skip, 不计入分母; 有窗口但 LSH 查询无任何命中的文章得分为 0.0 (确有窗口而无相似旧闻, 属真实的"零陈旧"而非缺失)。第五, 计算前按日期稳定排序 (kind='stable'), 计算后以逆置换 stale[np.argsort(sort_idx)] 还原原始行序, 与按位置赋值对齐——这是防整列错位的 P0 承重步骤, 在大量同时间戳并列下非稳定排序会使得分随输入序漂移。第六, 阈值二值化在 aggregate_to_bank_year 内向量化完成: high 列 = 1[stale > 0.9], 并把 stale 为 NaN 的行的 high 列同置 NaN, 使得均值 (占比) 自动跳过缺失; 随后按 (target_bank, year) 分组取 mean, 即得占比。分母因此是"字面陈旧度非 NaN 的有效文章数", 与面板其余 highstale 列同口径。

【文献定位】
本家族在方法学上立足于金融文本分析这一成熟范式。Gentzkow, Kelly & Taddy (2019) 的"文本作为数据"系统梳理了把非结构化文本转为可计量特征的方法谱系, 为本家族把报道流转为"字面重复度"这一定量特征提供了总纲。在金融文本的具体度量上, Loughran & McDonald (2020) 综述了词典法与相似度法在金融领域的应用与陷阱, 提示文本度量须谨慎对待领域特异性。与本家族最贴近的实证锚点是 Cohen, Malloy & Nguyen (2020) 的"惰性价格": 他们以公司年报相邻年度之间的文本相似度作为"是否改动了披露"的度量, 发现文本高度雷同 (即字面陈旧) 的公司蕴含可预测的负向市场信息——这与本家族"字面重复度越高、增量信息越少"的经济学直觉同构, 只是把度量域从年报相邻年迁移到银行报道流的七天滚动窗。Dyer, Lang & Stice-Lawrence (2017)、Lang & Stice-Lawrence (2015) 以大样本刻画了披露文本的模板化与套话膨胀趋势, Cazier & Pfeiffer (2016) 与 Li (2008) 则从可读性与文本长度角度补充了"文本冗余不等于信息"的证据; 这些工作共同支撑了"字面重复是信息含量的负向代理"这一判断。信息中介与处理成本维度上, Blankespoor, deHaan & Marinovic (2020) 综述了披露处理成本如何塑造投资者信息选择与市场结果, 并明确把媒体等信息中介的再传播、再加工纳入决定处理成本的环节——旧闻重印恰恰是提高处理成本、稀释信息环境的一种机制, 通稿转载即是媒体中介过程在报道流上留下的字面指纹。而 Cao et al. (2023) 关于"机器在听时如何说话"的研究则提醒: 当披露/报道日益被算法消费, 文本的模板化与重复本身成为策略性行为的产物, 使字面陈旧度的度量在当代更具意义。在金融学母题上, Tetlock (2011) 的"陈旧新闻是否被反应"与 Tetlock (2007) 的"媒体赋予投资者情绪内容"共同构成本构念的经济学根基: 本家族把银行层面的字面高陈旧占比作为该银行媒体信息环境"新鲜度稀释"的代理, 服务于新闻情感/关注度对银行行为影响这一研究线中的稳健性与信息质量刻画。近年文献进一步在文本相似度与股价同步性这一具体渠道上提供了支持: Huang, Chen & Wu (2025, Emerging Markets Review) 以新闻报道文本相似度度量信息重复程度并检验其与股价同步性的关系, 与本家族用字面相似度刻画报道陈旧、重复的思路直接同构; Wang, Chen, Gao & Qi (2025, Journal of Economics and Business) 发现文本相似度越高的分析师报告对应的信息含量越低、股价同步性越高, 支持本家族以字面重复度作为信息新鲜度负向代理的经济学逻辑。Duan, Kou, Wang & Wei (2024, International Review of Financial Analysis) 研究转发/重复传播的新闻相较原创新闻引发更强的市场反应, 与本家族字面重复度捕捉旧闻重印信息含量的思路相呼应。Merkley, Pacelli, Sun & Twedt (2024, The Accounting Review) 发现同一媒体控股公司旗下媒体报道趋同、字面与语气相似度更高, 并阻碍价格形成, 支持以文本相似度衡量报道重复对信息环境的稀释效应。

【识别策略定位】
本家族的三列并非三个相互竞争的"更好/更差"测度, 而是沿文本轨这一单一维度展开的规格稳健性网格: full/ctx/ss 三轨。按 CLAUDE.md 铁律, 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨的列混进同一个 over-identified Hansen J 过度识别检验。与语义家族不同, 字面家族没有 co-primary 双轨嵌入维度 (MinHash 无 _lg 孪生), 因此其稳健性网格只有文本轨一维, 更为简洁。识别上, 字面高陈旧占比可作为银行信息环境的控制变量或机制变量: 当研究媒体情感/关注度对银行融资成本、金融科技投资等结果的影响时, 高陈旧占比刻画了"该银行报道中有多大比例只是旧闻的字面重印", 用以吸收报道量背后信息含量的异质性。其留篇域与面板行宇宙沿用 full-only 门控口径 (2026-06-29): 一篇报道是否被判为"一篇银行金融科技报道"只看 full 轨的 llm_verified_full, ctx/ss 轨降为 conditional-on-full 的测度/稳健性轨, 面板平均域收缩到 verified 面板语料。因此 full 轨占比与 ctx/ss 轨占比在样本框上并非对称: 后两轨是在 full 留篇集子集上按各自轨文本重算的规格稳健性对照。须再次强调聚合域的双口径: 计算逐篇陈旧度的"参照窗口" (过去七天信息环境基准) 用 stage 13 预筛全集以保证背景完整, 而 bank-year"平均域"则收缩到 verified 面板语料 (与 tone/herd/intensity 兄弟列聚合口径一致), 二者刻意不同。

【与相邻测度的构念区分】
本家族须与三个近邻严格区分。其一是语义陈旧族 semantic_staleness / semantic_highstale (F490 及其连续得分族): 后者基于句向量嵌入的余弦相似度, 度量"语义/含义"层面的重复, 属嵌入派生, 因此有 co-primary 双轨 (canonical Qwen 4096 维 + _lg large 3072 维) 及互证需求。语义轨与字面轨互为补充: 一篇改写了措辞但意思照旧的旧闻, 字面陈旧度低而语义陈旧度高; 一篇字面雷同但被系统替换少数关键词的通稿, 字面陈旧度高而语义或有微降。二者的低相关正是同时保留两族的理由——生产日志会实测 surface 与 semantic 全文轨的相关系数 (设计期望落在 0.3 至 0.7 的互补区间) 用以监控二者确实捕捉不同信号。须切记: 字面族绝无 _lg 孪生, 若在稳健性表中误给字面列配 _lg 列即为口径错误。其二是连续得分 surface_staleness_{track} 本身 (F547): 那是逐篇最大近似 Jaccard 的银行-年均值 (水平矩), 而本家族是其在 0.9 阈值上二值化后的占比 (尾部矩)。均值刻画"平均有多旧", 占比刻画"有多大比例特别旧"; 阈值 0.9 是刻意保守的高位截断, 使占比聚焦于近乎逐字重印的极端尾部, 对分布中段不敏感。二者是同一底层信号的水平矩与尾部矩, 不应互相替代。其三是套话比率 boilerplate (F031): 后者度量单篇内部的模板化程度 (与语料公共套话的重合), 是"这一篇有多少是废话套话"; 而本家族度量的是"这一篇与近期某篇旧闻有多雷同", 是跨文档的重复而非文档内的模板密度, 二者构念不同、不可互替。

【已知局限与稳健性梯子】
须坦陈若干局限。第一, 匹配域与 Tetlock (2011) 原度量有刻意偏离, 论文/codebook 引用时须如实披露: Tetlock 原文按同一公司过去 72 小时内最近若干篇旧故事匹配, 本实现是 corpus-level (全银行混池) 七天日粒度窗口, 度量的是"银行业信息环境"层面的字面陈旧, 而非严格的同公司旧闻重印率——银行 A 的报道与上周关于银行 B 的行业通稿字面雷同亦计为陈旧。第二, MinHash 与 LSH 森林都是近似算法: MinHash 签名的相符比例是真实 Jaccard 的无偏但有方差的估计 (num_perm=128 决定其精度), LSH 森林的召回也非精确, 因此逐篇得分带轻度估计噪声; 0.9 的高截断在一定程度上缓解了这一影响 (只有非常接近逐字重印的对才被计为高陈旧)。第三, 阈值 0.9 是研究者设定的地板性保守值, 其绝对高度是 Jaccard 尺度上的选择; 占比水平对该阈值敏感, 稳健性检验中可考察阈值扰动下结论方向是否稳定。第四, 同日重复副作用已由"严格排除同日行"修复, 但跨日的多银行复制行仍可能带来轻度机械相关, 属已知残留。第五, 在开发期 T=2、语料极浅时, 窗口空导致大量 NaN, ss 轨在极短面板上最易零方差/全 NaN 退化 (与其在 ctx 轨的回退语义一致, 缺列即跳过、优雅降级), 属预期退化而非缺陷; 生产 T=19 全语料下窗口充分填充, 信号正常。围绕本家族的稳健性梯子因此由文本三轨、以及与之正交的连续得分族 (F547 水平矩)、语义陈旧族 (F490 意义重复) 共同构成, 各梯级各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

【方法学与计算】(工程实现细节)
从工程实现角度须再补充若干点, 以便复现者精确重建本家族。第一, 字符 shingle 的选择是中文语料下的关键设计: 相较于词级 n-gram, 字符级 3-gram 不经过分词, 因此不受 jieba 冻结词典版本 (0.42.1) 变动或分词歧义的影响, 使字面相似度在跨版本、跨语料下更稳定可复现; 同时字符级窗口对同义改写、语序微调较为敏感——真正的通稿转载即便零星替换标点或连接词, 其字符 3-gram 集合仍高度重合, 从而被稳定捕获。第二, MinHash 的 num_perm=128 是签名长度: 它决定了 Jaccard 估计的标准误 (约与 1/根号(num_perm) 同阶), 128 在精度与计算成本之间取得平衡; 逐篇得分带此固有估计方差, 是 0.9 高截断而非中段阈值的又一理由。第三, LSH 森林按 unique-day 分组滚动重建: 对每一个出现的"天", 重建一次覆盖其前七天窗口的森林, 该窗口严格为半开区间 [d-7d, d) 且不含当天, 再对当天的每篇文章做一次近邻查询取窗内最大相似度。滚动重建的成本与窗口内文档数近似线性, 整体把原 O(N²) 降到约 O(7N), 这是十万至千万量级语料可行的前提。第四, 本阶段自身完全不调用任何外部 API、零金钱成本 (纯 CPU 的 MinHash 与 LSH), 这与依赖付费嵌入的语义轨形成鲜明对比, 也是字面轨在生产上更轻量、可无门槛全量重跑的原因。第五, 外部依赖为 datasketch (提供 MinHash 与 MinHashLSHForest); 在 always-on 口径下缺包会真崩 (ImportError raise) 而非静默跳过, 以防悄然丢列。

【文献定位】(信息新鲜度与市场反应)
在经济金融维度上, 本构念的价值链条可进一步展开。Tetlock (2011) 以"陈旧新闻是否被投资者反应"为题, 发现被重复转载的旧信息仍会引发可测量的市场反应, 并以旧文的词面重复度作为信息新鲜度的操作化度量; 这为"字面高陈旧占比"作为银行媒体信息环境质量代理提供了直接的经济学母题, 且其原始度量本身就是词面重叠——与本家族的 MinHash Jaccard 轨属同一构念家族, 使字面轨相较语义轨更贴近 Tetlock 原范式。Tetlock (2007) 进一步论证媒体内容如何赋予投资者情绪以可交易的信息含量, 提示媒体报道流的信息结构 (含其中的重复与新鲜成分) 对资产定价具有实质影响。Cohen, Malloy & Nguyen (2020) 的"惰性价格"把文本相似度提升为可预测收益的信号: 当公司在相邻年度几乎不改动披露文本时 (字面高陈旧), 其背后往往隐藏未被及时消化的负面变化——这一"少改动即坏消息"的逻辑, 迁移到银行报道流即为"高比例旧闻重印意味着该银行信息环境的新鲜度被稀释"。Blankespoor, deHaan & Marinovic (2020) 从投资者处理成本视角综述了披露如何影响信息选择与市场结果, 旧闻重印正是抬高处理成本、降低有效信息密度的一种机制, 而该综述亦把媒体作为信息中介的传播与再加工纳入处理成本的来源, 通稿转载恰是这一中介过程留下的字面指纹。Lang & Stice-Lawrence (2015)、Dyer, Lang & Stice-Lawrence (2017)、Cazier & Pfeiffer (2016)、Li (2008) 从文本模板化、套话膨胀与可读性角度提供了"文本冗余不等于信息"的大样本证据, 支撑把字面重复作为信息含量负向代理的合法性。Cao et al. (2023) 与 Loughran & McDonald (2020) 则从当代 (机器消费文本、算法化披露) 与方法学 (金融文本分析的陷阱与边界) 两端界定了该度量的适用条件与审慎注脚。Gentzkow, Kelly & Taddy (2019) 的"文本作为数据"为整套从报道流到定量重复度的转换提供了统一方法学框架。

【方法学与计算】(三轨文本口径)
本家族的三轨文本来源须与其余家族对齐理解。full 轨 = content_full = 标题 prepend + 全文正文; ctx 轨 = content_ctx = 标题 prepend + 目标实体附近窗口文本; ss 轨 = content_ss = 标题 prepend + 银行与金融科技词同句 (±N 句窗, 由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 共现处文本。三轨文本统一在 stage 14 (ctx_materializer) 物化, 标题以 prepend 方式并入 (v3.8.0 起取消独立 title 轨, 标题改为前置拼接), 原始"内容"列不动。ss 轨的回退语义镜像 ctx: 当某篇报道无银行与金融科技同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 与其余轨共享 n_articles 分母; 若上游金融科技 AC 自动机为 None, 则相关 is_fallback 全置 True 优雅降级。三轨判定采用不对称口径: 银行侧含否定与短名过滤, 金融科技侧用裸 AC 词表匹配。三轨文本各自独立喂入 compute_surface_staleness 计算字面陈旧度, 因此本家族三轨的字符指纹输入天然不同 (全文最长、实体窗次之、同句共现最窄), 这也是三轨占比互为稳健性而非冗余复制的根本原因。须再次强调: 三轨禁混同一 over-identified Hansen J; 且三轨皆为 MinHash carve-out, 无一具备 _lg 孪生。

## VAR: surface_highstale_full

【变体差分】
本列是家族 canonical 核心列, 也是 full-only 门控口径 (2026-06-29) 下的 headline 轨。其精确语义为: 在 full 全文轨 (content_full = 标题 prepend + 全文正文) 上, 用字符级 3-gram shingle 的 MinHash (num_perm=128) 经 MinHashLSHForest 检索过去七日窗 [d-7d, d) (严格排除同日) 得到的逐篇最大近似 Jaccard 相似度, 经阈值 0.9 二值化后, 在银行-年层面取均值得到的字面高陈旧文章占比。文本轨上, full 轨消费的是标题拼接后的整篇正文, 因此字符指纹覆盖最全、最能捕捉整篇通稿级的逐字重印, 是判定"是否一篇银行金融科技报道"的门控轨——面板行宇宙即由 full 轨的 llm_verified_full 定义, 该列的分母 (字面陈旧度非 NaN 的有效文章) 直接落在 verified 留篇集上。须特别强调 carve-out 铁律: 本列是 MinHash 字符 shingle 派生, 属非嵌入度量, 因此没有 _lg co-primary 孪生, 也不存在跨嵌入厂商互证的概念——若在任何稳健性表中给本列配一个 surface_highstale_full_lg 列即为口径错误 (该列在设计上不存在)。相对家族内其余两列, 本列占据"full 文本轨"这一基准原点, 是 ctx/ss 两轨稳健性对照所环绕的基准; 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。阈值维度上, 0.9 是家族统一的高位截断, 使本列聚焦近乎逐字重印的极端尾部; 判据维度上, 窗口为日粒度 [d-7d, d) 严格排除同日行, 稳定排序保证确定性, LSH 无命中记 0.0、窗口空记 NaN。作为 canonical 列, 它承担与情感/关注度结果变量并列进入基线回归、或作为银行信息环境控制/机制变量的主要角色, 呼应 Cohen, Malloy & Nguyen (2020) 以文本相似度作为信息含量负向代理的思路。它与同底层的连续得分列 surface_staleness_full (水平矩)、语义孪生族 semantic_highstale_full (嵌入轨, 有 _lg)、以及套话比率 boilerplate_full (文档内模板密度) 构念各异, 均不可互替。就构造判据再作精确复述: 本列的逐篇分子来自 compute_surface_staleness, 其对 full 轨文本 (content_full) 先取字符级 3-gram shingle, 经 num_perm=128 的 MinHash 压缩为定长签名, 再以 MinHashLSHForest 在按天滚动的七日窗口内检索最相似旧文, 取其近似 Jaccard 相似度的最大值; 当窗口为空 (语料首周或近邻仅同日行) 时该值为 NaN 并在聚合时被跳过, 当窗口非空但 LSH 无任何命中时该值为 0.0 (真实零陈旧); 逐篇稳定排序与逆置换还原行序是防整列错位的承重步骤。随后在 aggregate_to_bank_year 内向量化二值化: 文章级 surface_highstale = 1[surface_staleness_full > 0.9], 并把连续得分为 NaN 的行的指示回填 NaN, 使 (target_bank, year) 分组均值 (即本列) 的分母恰为字面陈旧度非 NaN 的有效文章数。此分母口径与面板其余 highstale 兄弟列 (语义高陈旧、以及各占比类度量) 完全一致, 保证跨度量的可比性。须谨记本列的经济含义: 占比越高, 说明该银行该年度的报道中越大比例只是近七日内某篇旧闻的字面重印, 信息环境的新鲜度被稀释得越严重——这与 Cohen, Malloy & Nguyen (2020)"文本高度雷同蕴含未被消化信息"、以及 Blankespoor et al. (2020)"重复抬高处理成本"的逻辑一致。在实际使用中, 本列既可作为解释变量刻画信息环境质量, 也可作为控制变量吸收报道量背后信息含量的异质性, 但因其与连续得分列高度共线 (同一底层信号的水平矩与尾部矩), 二者不应同时并入同一回归的右手端, 更不应连同 ctx/ss 两轨一并塞入同一 over-identified Hansen J——三轨与水平/尾部两矩均为各自 just-identified 并排的规格稳健性梯级。最后须就本列的匹配域局限对使用者作一层提醒: 与 Tetlock (2011) 按同一公司过去数十小时旧闻匹配的原度量不同, 本列的七日窗口是 corpus-level 全银行混池的字面陈旧, 因此本列高值既可能来自针对该银行自身报道的逐字重印, 也可能来自与近期他行行业通稿的字面雷同——在把本列解读为"该银行专属信息新鲜度稀释"时须谨慎, 论文引用须如实披露这一 corpus-level 口径。就其与语义孪生 semantic_highstale_full 的分工再作一句厘清: 本列捕获措辞层面的逐字重印指纹, 语义列捕获改写措辞后意思照旧的重复, 二者低相关、互为补充, 生产日志会实测全文轨 surface 与 semantic 的相关以监控二者确捕不同信号; 但因语义列属嵌入派生而带 co-primary 双轨 (canonical Qwen 4096 维与 _lg large 3072 维), 本列作为 MinHash carve-out 绝无 _lg 孪生, 二族在稳健性表中须分列陈放、切忌张冠李戴。

## VAR: surface_highstale_ctx

【变体差分】
本列是字面高陈旧占比在 ctx 上下文窗轨上的规格稳健性对照。其相对 canonical full 列的唯一差分在文本轨: ctx 轨消费 content_ctx = 标题 prepend + 目标实体窗口文本 (银行/金融科技实体附近的局部窗口, 而非整篇正文), 在 stage 14 (ctx_materializer) 物化。因此本列的 MinHash 字符指纹只覆盖实体上下文局部文本, 度量的是"围绕银行金融科技实体的局部表述"层面的字面重复, 文本更短、更聚焦于实体窗。除文本轨外, 其指纹构造 (字符 3-gram shingle, num_perm=128)、检索器 (MinHashLSHForest)、窗口判据 (日粒度 [d-7d, d) 严格排除同日、稳定排序、无命中记 0.0、空窗记 NaN)、阈值 (0.9)、聚合与分母口径均与 canonical 列一致。同为 MinHash carve-out, 本列亦无 _lg 孪生。在 full-only 门控口径下 (2026-06-29), ctx 轨属 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 轨 verified 留篇集的子集, 占比按 ctx 轨文本重算。因文本更短, 局部窗内可用于比对的字符指纹较少, 在极浅面板上更易出现窗口空/NaN 退化, 属预期行为。本列与 full/ss 各轨列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。它的价值在于回答"若只看实体上下文而非全文, 字面高陈旧结论是否依然成立", 从而在文本轨维度上为 canonical full 结论提供并排的规格稳健性对照。

## VAR: surface_highstale_ss

【变体差分】
本列是字面高陈旧占比在 ss 同句共现轨上的规格稳健性对照, 是文本轨维度上最严格的一格。其相对 canonical full 列的差分在文本轨: ss 轨消费 content_ss = 标题 prepend + 银行与金融科技词同句 (±N 句窗, 由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 共现处的局部文本。因此本列的 MinHash 字符指纹只覆盖"银行与金融科技概念真正在同一句语境中共现"处的最窄文本, 度量的是这一最严格局部语境下的字面重复。ss 轨的回退语义镜像 ctx: 当某篇报道无银行与金融科技的同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 并与其余轨共享 n_articles 分母; 若上游金融科技 AC 自动机为 None, 则相关 is_fallback 全置 True 优雅降级。除文本轨与回退语义外, 其指纹构造 (字符 3-gram shingle, num_perm=128)、检索器 (MinHashLSHForest)、窗口判据 (日粒度 [d-7d, d) 严格排除同日、稳定排序、无命中记 0.0、空窗记 NaN)、阈值 (0.9)、聚合与分母口径均与家族统一口径一致。同为 MinHash carve-out, 本列亦无 _lg 孪生。在 full-only 门控下 (2026-06-29), ss 轨同属 conditional-on-full 稳健性轨, 行宇宙为 full verified 留篇集子集。因文本最窄, 在开发期极浅面板上 ss 轨最易零方差/全 NaN 退化 (属预期, 缺列即跳过、优雅降级); 生产 T=19 全语料下正常。本列与 full/ctx 各轨列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。它回答"若只看银行与金融科技真正同句共现处的字面表述, 高陈旧结论是否成立", 是三轨中最严格的规格稳健性对照。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Blankespoor, E., deHaan, E., & Marinovic, I. (2020). Disclosure processing costs, investors' information choice, and equity market outcomes: A review. Journal of Accounting and Economics, 70(2-3), 101344. https://doi.org/10.1016/j.jacceco.2020.101344
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal of Accounting and Economics, 64(2-3), 221-245. https://doi.org/10.1016/j.jacceco.2017.07.002
Cazier, R. A., & Pfeiffer, R. J. (2016). Why are 10-K filings so long? Accounting Horizons, 30(1), 1-21. https://doi.org/10.2308/acch-51240
Lang, M., & Stice-Lawrence, L. (2015). Textual analysis and international financial reporting: Large sample evidence. Journal of Accounting and Economics, 60(2-3), 110-135. https://doi.org/10.1016/j.jacceco.2015.09.002
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information? The Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Huang, R., Chen, X., & Wu, C. (2025). The textual similarity of news content and stock return synchronicity. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2025.101309
Wang, Y., Chen, R., Gao, X., & Qi, W. (2025). Text similarity in analyst reports and stock price synchronization. Journal of Economics and Business. https://doi.org/10.1016/j.jeconbus.2025.106258
Duan, J., Kou, F., Wang, Z., & Wei, Y. (2024). When echoes surpass voices: Market reaction to forwarded news. International Review of Financial Analysis. https://doi.org/10.1016/j.irfa.2024.103579
Merkley, K. J., Pacelli, J., Sun, F., & Twedt, B. J. (2024). Common Media Holding Companies and the Uniqueness of Business Press Content. The Accounting Review. https://doi.org/10.2308/tar-2023-0191
<!-- rendered-citations:end -->
