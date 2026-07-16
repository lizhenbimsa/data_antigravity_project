---
family_id: F547
columns:
- surface_staleness_ctx
- surface_staleness_full
- surface_staleness_ss
unit: 词面相似度陈旧度分值 (无量纲, [0,1] 区间)
formula: "surface_staleness_track = 该文与其参照邻域内先前报道的 MinHash 近似 Jaccard 相似度 (char-shingle 3-gram); 越高越陈旧 (越接近既往报道), track ∈ {full, ctx, ss}"
producer: news_process/pipeline/text/article_staleness.py (stage 26 article_staleness; surface 支路 _compute_surface)
upstream:
- 14_news_with_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_embeddings.parquet (仅 semantic 支路依赖嵌入; surface 支路不依赖)
citations:
- doi: 10.48550/arXiv.2511.01211
  type: arxiv
  authors: Wu, C.
  year: 2025
  title: "Novelty and impact of economics papers"
  venue: arXiv
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.2139/ssrn.4425527
  type: wp
  authors: Kim, A. G., Muhn, M., & Nikolaev, V. V.
  year: 2023
  title: "Bloated disclosures: Can ChatGPT help investors process information?"
  venue: SSRN Working Paper No. 4425527
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
- doi: 10.1111/1475-679X.12179
  type: journal
  authors: Bushee, B. J., Gow, I. D., & Taylor, D. J.
  year: 2018
  title: "Linguistic complexity in firm disclosures: Obfuscation or information?"
  venue: Journal of Accounting Research
  vol: 56
  issue: 1
  pages_or_artno: 85-121
- doi: 10.1016/j.jacceco.2017.07.002
  type: journal
  authors: Dyer, T., Lang, M., & Stice-Lawrence, L.
  year: 2017
  title: "The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation"
  venue: Journal of Accounting and Economics
  vol: 64
  issue: 2-3
  pages_or_artno: 221-245
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
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
  venue: Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: "10.2139/ssrn.4555832"
  type: wp
  authors: "Glasserman, P., Mamaysky, H., & Qin, J."
  year: 2023
  title: "New News is Bad News"
  venue: "SSRN Electronic Journal (Working Paper No. 4555832)"
- doi: "10.1145/3701716.3715303"
  title: "Benchmarking Near-Duplicate Detection in the era of Pay-walled News"
  authors: "Kumar, A., Tumre, S., & Patil, S."
  year: 2025
  venue: "Companion Proceedings of the ACM on Web Conference 2025 (WWW '25 Companion)"
  type: "wp"
- doi: "10.1007/s11142-025-09897-1"
  title: "News-based investor disagreement and stock returns"
  authors: "Li, S. Z., & Luan, Z."
  year: 2025
  venue: "Review of Accounting Studies"
  type: "journal"
new_dois:
- 10.1016/j.jacceco.2017.07.002
- 10.1016/j.jacceco.2015.09.002
- "10.2139/ssrn.4555832"
- "10.1145/3701716.3715303"
- "10.1007/s11142-025-09897-1"
---

## CORE

【构念与来源】
本家族度量一篇银行金融科技报道在词面层的陈旧度 (surface staleness): 该文的字面表述相对于此前已经出现过的报道有多大程度的重复。构念直觉是, 新闻的信息价值随其新颖性递减 —— 若一篇报道在措辞、句式、片段上与既往报道高度雷同, 那么它多半是旧信息的转载、改写或例行通稿, 对市场几乎不携带增量信息; 反之, 词面上与历史报道相去甚远的报道更可能承载新事件、新表述与新信号。surface_staleness 把这一直觉物化为一个连续的相似度分值, 取值落在 0 到 1 的闭区间: 越接近 1 表示该文与其参照邻域内的先前报道越相似 (越陈旧), 越接近 0 表示越新颖。该分值由 stage 26 (article_staleness) 的 surface 支路产出, 计算完全基于文本本身, 不依赖任何嵌入模型或外部资源, 因此是一条零边际成本、可离线字节级复现的度量。构念的学术锚点是 Tetlock (2011): 该文以美联社与道琼斯新闻的词面重叠度界定 "stale" 信息, 实证发现投资者对陈旧信息存在初始过度反应并随后反转 (return reversal), 从而把 "新闻的词面新颖性" 确立为一个具有资产定价含义的一等度量。需要准确说明 Tetlock 原文的度量形态: Tetlock (2011) 的 staleness 本身即是一个连续量 —— 它把每篇报道中与其之前若干天既往报道相重叠的内容占比 (记为 Old, 即旧文重叠比率, 取值落在 0 到 1 的闭区间) 作为陈旧度, 并在实证中直接以这一连续比率进入回归, 而非仅给出一个 "是否陈旧" 的二元标签。因此本项目并非把 Tetlock 的布尔判定 "升级" 为连续分值 —— 它原本就是连续的; 本项目所做的是直接承袭其 "旧文重叠比率" 这一连续操作化思路, 换用对中文分词误差更鲁棒的字符 shingle 上的 MinHash 近似 Jaccard 来实现同一族连续重叠度, 并把度量对象从英文财经新闻迁移到中文银行金科报道语料, 概念同源、落地本土化。之所以坚持保留连续分值、而非只留一个 "是否近重复" 的布尔标记, 是相对本项目自身 dedup 模块 (在 0.80 相似度阈值处做二元切割以删近重复行) 而言的: 布尔阈值会丢失大量中间信息 —— 一篇与旧报道相似度 0.55 的报道和一篇相似度 0.95 的报道在信息陈旧程度上差异巨大, 二元切割把二者压成同一类别; 连续分值则让回归可以刻画陈旧度的边际效应, 也便于做分位数分组、稳健性梯度与工具变量构造。这与 Tetlock 连续 Old 比率的原始形态一脉相承, 并非对被引文献方法学的改写。在银行金科这一具体语境里, 词面陈旧尤为常见: 监管新规、产品发布、战略合作等事件常以高度模板化的通稿形式经多家媒体同步转载, 同一事件的多篇报道措辞高度雷同; surface_staleness 正是要把这类 "同事件转载" 与 "真正携带新事实的原创报道" 在词面层区分开, 为后续把媒体报道用作银行行为、市场反应或政策传导的解释变量时提供一个信息含量的调节维度。

【方法学与计算】
surface_staleness 的核心算法是字符 shingle 上的 MinHash 近似 Jaccard 相似度。具体链路为: 先把每篇报道的文本切成字符层的 3-gram (char-shingle, 即以 3 个连续汉字为一个片段的滑窗集合), 一篇文档由此表示为一个 shingle 集合; 两篇文档的词面相似度定义为其 shingle 集合的 Jaccard 相似系数 (交集大小除以并集大小)。选择字符 3-gram 而非分词后词级 n-gram, 是因为中文新闻在分词边界上高度依赖分词器且专有名词与机构简称切分不稳, 字符层滑窗对分词误差鲁棒、对局部改写敏感, 且不引入 jieba 词典的外部依赖, 更利于确定性复现。由于逐对精确 Jaccard 在大样本上是平方级开销, 实现采用 datasketch 的 MinHash 把每个 shingle 集合压缩为固定长度的最小哈希签名, 用签名的碰撞比无偏估计真实 Jaccard, 并借助 LSHForest (局部敏感哈希森林) 做近邻检索, 只对可能高相似的候选对求值, 从而把复杂度从平方级降到近线性, 使其在千万级语料上仍可产。每篇报道的 surface_staleness 取其相对参照邻域内先前报道的最高 (或近邻聚合) 相似度: 邻域里存在与本文措辞高度雷同的旧报道时分值高 (陈旧), 找不到相近旧文时分值低 (新颖)。分值域为 0 到 1 的闭区间, 无量纲, 可直接跨时间跨银行比较。该度量与项目既有的去重模块 (dedup.py 的 jaccard_similarity_threshold=0.80 布尔判据) 严格同源 —— 二者用同一族 Jaccard 相似度, 区别仅在于 dedup 输出 "是否近重复" 的布尔决策 (在 0.80 阈值上做二元切割以删除近重复行), 而 surface_staleness 保留连续 score 供回归使用, 是同一测度机制的两种输出粒度: 前者服务于样本清洗, 后者服务于陈旧度信号的连续刻画。这一同源性也意味着 surface_staleness 的分布形态与去重阈值经验一致, 读者可据 0.80 这一近重复经验阈值大致定位 "高陈旧" 的量级。

确定性上, MinHash 的排列种子固定、shingle 切分与 Jaccard 估计均无随机浮点路径, 分值经定点舍入, 因此不依赖 PYTHONHASHSEED, 可在 NEWS_PROCESS_LLM_OFFLINE 离线态零漂移复现; 这也是它作为 golden 锚点安全列的原因之一 —— 与那些受 BLAS 浮点非确定性影响的网络中心性列不同, surface_staleness 是逐位可复现的。安全降级上, 参照邻域为空 (无可比先前报道) 或文本退化 (空文、哨兵、实字数不足以构成一个 3-gram) 时分值置 NaN 并伴 loud WARNING, 绝不静默填零 —— 这一 fail-loud 约定镜像全项目对 FINTECH_AC=None 等边界的处理, 确保退化不会被误读为 "极度新颖 (分值 0)"; 换言之, NaN 与 0 在本家族里语义严格不同, 前者表示 "无法判定陈旧度", 后者表示 "判定为完全新颖", 使用者在下游聚合与回归时须区别对待, 不得把 NaN 静默填 0。需要强调, surface_staleness 的产出完全在 stage 26 的 surface 支路内闭环, 不触碰任何 LLM 或嵌入 API, 因此对生产的边际成本为零, 三轨 (full/ctx/ss) 全部只依赖 stage 14 物化的三份文本列 (content_full/content_ctx/content_ss), 是本项目最经济的一类文本度量。

【文献定位】
panel 级另有一个配套统计量 staleness_corr, 记录 surface 与 semantic 两支路陈旧度在整个语料上的相关性, 它不属于本家族的逐文列, 但为读者评估 "词面陈旧" 与 "语义陈旧" 的重叠度提供全局参照, 与本家族 surface 三列配合解读。

本家族在文献谱系上处于三条线索的交汇处。第一条是新闻陈旧度与资产定价: Tetlock (2011) 奠定 "词面重叠即陈旧" 的操作化并给出 return reversal 证据, Wu (2025) 则从更一般的 "文本新颖性" 视角讨论新颖度与影响力的关系, 为 "新颖 (低陈旧) 报道更具信息价值" 的假设提供跨领域佐证; Fang & Peress (2009) 关于媒体报道与股票横截面收益的经典证据, 则从 "报道即信息" 的方向说明媒体覆盖本身携带定价相关信号, 而陈旧度正是把这类覆盖按信息新颖性再切分的调节维度。第二条是会计与披露文本学: Lang & Stice-Lawrence (2015) 与 Dyer, Lang & Stice-Lawrence (2017) 把 "套话/公式化措辞占比" 与 "披露文本随时间的演化" 作为文本质量与信息含量的代理, 与本项目 boilerplate 家族同源, 也间接支撑 "高度重复的词面表述携带较少增量信息" 这一 surface_staleness 的构念前提; Bushee, Gow & Taylor (2018) 关于语言复杂度究竟是混淆还是信息的辨析, 以及 Kim, Muhn & Nikolaev (2023) 对 "膨胀披露 (bloated disclosure)" 稀释增量信息的量化, 都从不同侧面印证 "文本冗余度与其信息含量负相关" 的方向, 与本家族 "越陈旧越少增量信息" 的假设同调。Blankespoor, deHaan & Marinovic (2020) 对披露处理成本与投资者信息选择的综述进一步提示, 陈旧/冗余文本会抬高信息处理成本、压低有效信息获取, 使陈旧度成为一个具有市场后果的文本质量维度。第三条是文本相似度的度量与定价: Liu, Cao & Wen (2024) 直接把 "企业与政府文本的相似度" 操作化为可度量、可进入资产定价的连续变量, 与本家族把 "整篇 vs 历史报道的相似度" 物化为连续陈旧度分值的思路方法学同构, 为 "文本相似度是一个一等的、有定价含义的度量" 提供了最贴近的近期支撑; 而 Loughran & McDonald (2016, 2020) 两篇文本分析权威综述则确立了本家族所处的方法学范式 —— 在财经文本上以可复现、可审计的量化度量刻画文本属性, 是本项目所有文本度量列 (含 surface_staleness) 共同遵循的方法学底座。中文语境上, 姜富伟、孟令超、唐国豪 (2021) 对中文媒体文本情绪与股票回报预测的研究, 说明中文财经媒体文本本身即携带可被量化并进入定价的信号, 为本家族把词面陈旧度从英文语料迁移到中文银行金科报道语料提供了本土可行性佐证。Glasserman, Mamaysky & Qin (2023, SSRN Electronic Journal) 以新闻文本分布随时间变化的新颖度 (熵测度) 预测股票市场收益与宏观经济下行, 与本家族用词面重叠度刻画陈旧度构成同一新闻新颖性—市场后果研究线索的最新实证支撑。本家族与 boilerplate 家族出自同一执行计划下的非极性文本维度组, 但测度对象不同: boilerplate 度量的是 "篇内命中语料级高频套话短语的比率" (单篇 vs 语料级套话集), surface_staleness 度量的是 "整篇 vs 具体历史报道的相似度" (两篇之间的 Jaccard), 二者正交、各自成列, 不得互相替代。把这两条文本学线索接到银行金科研究上, 陈旧度可作为一个新闻质量/信息含量的控制变量或识别工具: 在研究媒体报道对银行行为、市场反应或政策传导的影响时, 剔除或调节高陈旧 (旧闻转载) 报道有助于把真实的增量新闻信号从例行通稿的噪声中分离出来。Tetlock (2011) 的 return reversal 结果进一步提示, 陈旧信息可能诱发短期误定价并随后反转, 因此陈旧度不仅是数据清洗维度, 本身也可能是一个具有行为金融含义的解释变量。Wu (2025) 关于新颖性与影响力关系的讨论则从产出端佐证: 更新颖的文本 (低陈旧) 往往对应更高的后续影响力, 与本家族 "低陈旧报道携带更多增量信息" 的假设方向一致。Kumar, Tumre & Patil (2025, WWW '25 Companion) 在付费墙新闻场景下对 MinHash-LSH、SimHash 与句向量方法做近重复检测基准评测, 发现哈希类方法准确率显著低于神经方法, 为本家族选用的 MinHash 近似 Jaccard 词面相似度方法提供了最新的方法学效度边界参照。Li & Luan (2025, Review of Accounting Studies) 以新闻文本构造投资者分歧度量并检验其对股票收益的预测力, 与本家族把新闻词面重复/陈旧度作为信息含量调节变量的思路同属最新的新闻文本—资产定价实证支撑。

【识别策略定位】
在计量识别上, surface_staleness 家族是一条纯词面 (lexical/surface) 的信息新颖性测度轨, 与 semantic_staleness 家族构成一对刻意区分的互补支路: 前者捕捉字面重复, 后者 (由 stage 26 semantic 支路以 Faiss 余弦嵌入计算) 捕捉 "措辞不同但语义近似" 的深层重复。二者共同刻画陈旧度的两个正交侧面, panel 级另产 staleness_corr 记录二者的相关性以便读者评估二者的重叠度。关键的口径铁律是: surface_staleness 是嵌入派生度量的 carve-out —— 由于它基于 MinHash 字符 n-gram 而非任何 API 嵌入, 它没有 co-primary 双轨嵌入体系下的 `_lg` 孪生列; 与之对照的 semantic_staleness 才各算两遍 (Qwen 主轨无后缀 + text-embedding-3-large 的 `_lg` 孪生, 两轨维度不同 4096/3072, 余弦维度无关绝不混算, 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J)。因此在任何涉及 `_lg` 的批量列操作或 both-or-neither 平价守卫里, surface_staleness 三列都应被显式排除, 不能被误当作缺失孪生的孤儿列。作为工具变量或稳健性对照使用时, surface 轨与 semantic 轨应各自单独进入识别式, 不应把两条不同测度机制的陈旧度硬塞进同一超辨识 Hansen J 的过度识别检验。同理, full/ctx/ss 三条文本轨的 surface_staleness 属规格稳健性并排 (镜像本项目政治词权重梯度、词典消融梯度、共现判据敏感性等先例的口径): 三轨各自 just-identified 单独进入回归、互为稳健性、不分主次, 证明主结论不被文本口径选择所驱动, 而不应把三轨并入同一过度识别工具集。这一 "各自 just-identified 并排、禁混同一 over-identified Hansen J" 的铁律贯穿本项目所有三轨/co-primary 双轨/梯子/per-model 度量族, surface_staleness 家族在其中的定位是: 三轨 (文本口径梯子) 与 semantic 轨 (词面 vs 语义机制对照, 且 semantic 侧另含 `_lg` co-primary 双轨) 共同构成陈旧度构念的多重稳健性对照矩阵, 但每一维都需分别进入识别式。

【与相邻测度的构念区分】
需要与三个相邻测度严格区分。其一是 dedup.py 的近重复布尔标记: 二者同源于 Jaccard 但粒度不同, 近重复标记在 0.80 阈值上做二元切割用于删行去重, surface_staleness 保留连续分值供回归, 二者不可互换填充。其二是 within_doc_redundancy (篇内自重复): 那是一篇报道内部段落/句子的自相似, 与本家族的 "跨报道相似" 是不同的重复轴 —— 一篇内部啰嗦重复但内容首发的报道会有高篇内自重复却低 surface_staleness, 一篇简洁但整篇抄自旧报道的报道则相反, 二者刻画的重复方向正交, 不可互推。其三是 boilerplate_phrase_ratio (套话比率): 如前所述, 它命中的是语料级高频套话短语集, 是 "单篇 vs 集合" 的命中率, 而非 "单篇 vs 单篇" 的相似度; 二者在真实语料上虽可能相关, 但构念与算法都不同, 且 boilerplate 同为非嵌入 carve-out (无 `_lg`), 与本家族并列。二者的一个关键差异在时间维度: boilerplate 的套话集是在整个语料上一次性统计出来的高频短语集合, 是一个 "跨全语料的静态基线"; 而 surface_staleness 的参照系是每篇报道之前出现的具体历史报道, 是一个 "随时间推进的动态邻域"。因此一篇报道即便套话比率不高, 只要它与某几篇具体旧报道逐句雷同, 其 surface_staleness 依然会很高; 反之一篇满是行业通用套语但内容确属首发的报道, boilerplate 比率高而 surface_staleness 未必高。这一时间性差异是二者不可互相替代的根本原因, 使用者不应用其一去填补另一的缺失。此外 surface_staleness 与 semantic_staleness 的区别已如上述, 一为词面一为语义, staleness_corr 就是为量化这一区别而设 —— 若二者相关性极高, 说明本语料上词面重复与语义重复高度同步 (洗稿罕见), 词面轨已足够代理陈旧度; 若相关性中等, 则说明存在大量 "换词不换意" 的语义陈旧, semantic 轨提供不可被 surface 轨替代的增量信号。第四个易混点是本家族与新闻显著性 (news_salience) 等注意力类度量: 陈旧度刻画的是 "信息是否重复", 注意力度量刻画的是 "报道是否被密集覆盖", 一篇被密集转载的通稿可能同时高陈旧且高注意力, 二者构念正交, 不可互推。

【已知局限与稳健性梯子】
本家族的已知局限有三。第一, 参照邻域的界定依赖时间顺序与可比样本量: 语料早期或稀薄时段可比先前报道少, 分值偏低或缺失属预期退化 (dev 小样本 T=2 上尤其明显), 生产全量 T=19 语料上邻域充分方为正常口径。第二, 中文语料上字符 3-gram 对同义改写不敏感 —— 换词不换意的洗稿会被判为低陈旧, 这正是 semantic_staleness 存在的理由, 二者互补而非替代。第三, MinHash 是 Jaccard 的近似估计, 签名长度决定估计方差; 实现选用与去重模块一致的参数以保证两处口径同源, 使 surface_staleness 的连续分值可与 0.80 近重复经验阈值直接对齐解读, 避免在两处对同一族相似度采用不一致的哈希参数而产生口径漂移。稳健性梯子由三条文本轨构成 (full/ctx/ss), 三轨各自在自身参照邻域上独立计算 surface_staleness, 互为稳健性、不分主次、各自 just-identified 并排、禁混进同一 over-identified Hansen J; 与 semantic 轨 (含其 `_lg` 孪生) 又构成词面 vs 语义的第二重稳健性对照。三轨的文本口径遵循全项目统一约定: full 轨为标题 prepend + 全文正文, ctx 轨为标题 + 实体上下文窗口, ss 轨为标题 + 银行与金科同句共现 ±N 窗; 留篇门控口径以 full-only 为准 (2026-06-29), 即一篇报道是否被判为一篇银行金科报道只看 full 轨的留篇结果, ctx/ss 轨降为 conditional-on-full 的条件测度轨 (行宇宙为 full 留篇集的子集), 各轨的 surface_staleness 在各自留篇行宇宙上按各自参照邻域独立计算。ss 轨在无银行∧金科同句共现时其文本回退镜像 ctx/full (ss_is_fallback 置真), 但陈旧度层因参照窗口邻居不同于 full 而仍带独立信号, 非纯冗余 —— 这是 ss 轨即便文本回退也保留为独立稳健性轨的根本理由。

第四条局限关乎参照邻域的时间方向与可比性口径。陈旧度隐含 "相对于先前报道" 的时间不对称: 一篇报道的陈旧度只应由其之前 (而非之后) 出现的报道决定, 否则会引入前视偏误。实现按语料时间顺序约束参照邻域的检索方向, 但在同日/同批次报道的次序界定上存在实现依赖, 使用者在把 surface_staleness 用作严格的因果识别工具时应额外核查其时间边界口径是否满足研究设计。第五条局限关乎中文语料特性: 银行金科报道大量使用机构全称、监管套语与固定披露句式 (如 "根据某某管理办法")、这些高频公式化表述会抬高整体陈旧度基线, 与 boilerplate 家族捕捉的对象部分重叠; 二者虽算法不同 (相似度 vs 套话命中率), 但在解读高陈旧报道时宜结合 boilerplate 比率交叉印证, 避免把 "行业通用套语多" 误读为 "旧闻转载"。第六, MinHash 是无偏但有方差的估计, 极端稀疏或极短文本上的 shingle 集合小、估计方差大, 实测口径以生产全量语料为准, dev 小样本 (T=2) 上的分值分布不具代表性, 不应据此下测度效度结论。综合而言, surface_staleness 家族是一条经济、确定、可离线复现的词面陈旧度主测度, 其稳健性由三条文本轨与一条语义机制对照 (semantic_staleness 及其 `_lg` co-primary 孪生) 共同承托, 各维分别 just-identified 并排、禁混同一 over-identified Hansen J, 构成对陈旧度构念的多角度三角验证, 也为把陈旧度用作银行金科研究中的信息含量控制或工具变量提供了可审计、可复现的度量基座。

## VAR: surface_staleness_full

【变体差分】
本列是家族的 canonical 核心列, 也是 tier=core 列, 对应 full 文本轨 —— 即标题 prepend 到全文正文后的完整报道文本。它的参照邻域与相似度计算都建立在 full 轨文本上: 把每篇报道的 "标题+全文" 切成字符 3-gram shingle 集合, 用 MinHash 签名近似 Jaccard, 借 LSHForest 检索其在 full 轨语料里的近邻先前报道, 取近邻相似度作为该文的词面陈旧度分值。相对家族其余两轨, full 轨的区别在于它使用信息最完整的文本 —— 全文语料意味着 shingle 集合最大、可捕捉的重复片段最全, 因此 full 轨的 surface_staleness 通常被视为最贴近 "整篇报道是否为旧闻转载" 这一构念的主测度。它也是留篇门控 (full-only, 2026-06-29) 所锚定的那一轨: 一篇报道是否被判为一篇银行金科报道只看 full 轨的 LLM 留篇结果 (llm_verified_full 为真), 因此 full 轨的行宇宙即面板的基准行集合, ctx/ss 轨是其条件子集。这一门控口径意味着 surface_staleness_full 与面板上其它 full 轨主变量共享同一样本框, 用作控制或分组时无需额外做样本对齐, 是它相对 ctx/ss 轨在实操上的又一便利。本列作为 core 列还承担 carve-out 的显式声明职责: 尽管 stage 26 的 semantic_staleness 有 co-primary 双轨嵌入的 `_lg` 孪生, surface_staleness_full 因基于 MinHash 字符 n-gram 而非任何 API 嵌入, 没有 `_lg` 孪生, 属非嵌入派生的 carve-out; 在所有涉及 both-or-neither 嵌入平价守卫、`_lg` 列双射核验、跨厂商维度对照的批量操作里, 本列必须被显式排除, 绝不能被当作 "缺失 `_lg` 孪生的孤儿列" 触发平价告警。识别用途上, full 轨的 surface_staleness 与同轨的 semantic_staleness (及其 `_lg` 孪生) 构成词面 vs 语义的稳健性对照, 与 ctx/ss 两轨又构成文本口径的稳健性梯子; 无论哪一重, 各测度都应各自 just-identified 单独进入识别式, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。从测度效度看, full 轨之所以被选为 canonical, 有三重理由: 其一, 它使用信息最完整的全文文本, shingle 集合覆盖面最广, 对 "整篇是否旧闻转载" 的判定最全面, 与 Tetlock (2011) 原始构念 (整篇报道级别的词面重叠) 最贴合; 其二, 它锚定 full-only 留篇门控的行宇宙, 是面板的基准行集合, 因此以 full 轨陈旧度作主测度可保证与其它 full 轨主变量 (如 llm_vote_tone_full) 的样本口径一致; 其三, full 轨无需实体窗口或同句共现的额外裁剪逻辑, 口径最简、最少歧义, 复现路径最短。作为主测度, surface_staleness_full 的典型用法是作为新闻信息含量的连续控制变量或稳健性维度: 在研究媒体报道对银行融资成本、金科投资或市场反应的影响时, 控制或分组本列可把旧闻转载的稀释效应从真实增量新闻中剥离。使用时须与同轨 semantic_staleness_full (及其 `_lg` 孪生) 交叉解读 —— 若 surface 低而 semantic 高, 提示存在换词不换意的洗稿式陈旧; 二者相关性由 panel 级 staleness_corr 汇报。识别铁律再次强调: 词面轨、语义轨、`_lg` 孪生、以及 ctx/ss 文本轨, 每一维都应各自 just-identified 单独进入识别式, 互为稳健性、不分主次, 各证主结论不被单一口径驱动, 禁混进同一 over-identified Hansen J。确定性上本列无 HASHSEED 依赖, 分值定点舍入, 是 golden 逐位可复现的安全列 (不受 BLAS 浮点非确定性影响), 参照邻域为空或文本退化时置 NaN 伴 loud WARNING, 可在 NEWS_PROCESS_LLM_OFFLINE 离线态零漂移复现。

## VAR: surface_staleness_ctx

【变体差分】
本列对应 ctx 文本轨, tier=standard, 是 full 轨的第一条稳健性对照。它与 canonical full 列的唯一区别在于所用文本口径: ctx 轨文本 = 标题 prepend + 实体上下文窗口 (围绕目标银行与金科实体的邻近上下文片段), 而非全文正文。因此 ctx 轨的 shingle 集合建立在更聚焦、更短的实体上下文文本上: 它剔除了与银行金科主题无关的段落, 只在实体相关的措辞上比较词面重复。这一口径差异带来的直接后果是, ctx 轨的 surface_staleness 捕捉的是 "围绕银行金科实体的表述有多陈旧", 对无关背景段落的雷同不敏感 —— 若两篇报道正文主体不同但实体上下文措辞雷同 (例如同一套 "某银行推出金科产品" 的通稿式表述), ctx 轨会给出更高的陈旧度。ctx 轨在参照邻域检索上同样独立于 full 轨: 它在 ctx 轨自身的文本语料上建 MinHash 索引与近邻检索, 不借用 full 轨的邻域或分母。作为稳健性轨, ctx 与 full/ss 各自 just-identified 并排、互为稳健性、不分主次、禁混进同一 over-identified Hansen J; ctx 轨的价值在于检验主结论是否对 "把陈旧度限定在实体相关语境" 这一口径选择稳健。本列同为非嵌入 carve-out, 无 `_lg` 孪生, 在涉 `_lg` 的批量列操作与 both-or-neither 平价守卫里须被显式排除。确定性、NaN 降级 (参照邻域空或文本退化置 NaN 伴 loud WARNING) 口径与 full 列一致, 离线态零漂移可复现。

## VAR: surface_staleness_ss

【变体差分】
本列对应 ss 文本轨 (银行与金科同句共现窗口轨), tier=standard, 是家族的第二条稳健性对照, 2026-06-21 随 ss 全平价上线。它与 canonical full 列的区别在于文本口径: ss 轨文本 = 标题 prepend + 银行∧金科同句共现 ±N 窗 (config filtering.yaml 的 context_window.ss_sentence_radius, 默认 1), 即只保留银行与金科词在同一句子内共现的最窄上下文。因此 ss 轨的 shingle 集合最聚焦, 度量的是 "银行金科紧密共现语境下的措辞有多陈旧"。ss 轨的 surface_staleness 完全依赖 content_ss 文本的 MinHash, 与 surface_full/ctx 同源、零边际成本, 不依赖任何嵌入 (这一点与 semantic_staleness_ss 不同, 后者依赖 stage 25 为 content_ss 产出的 SBERT 嵌入 emb_ss)。回退语义上须注意: 当某文无银行∧金科同句共现时, content_ss 回退镜像 ctx/full 文本 (ss_is_fallback=True), 但即便文本回退到与 full 一致, ss 轨的陈旧度层因参照窗口邻居不同于 full 而 surface_staleness_ss 仍不等于 surface_staleness_full —— 参照邻域是在 ss 轨语料上独立构建的, 故非纯冗余, 仍携带独立信号。作为稳健性轨, ss 与 full/ctx 各自 just-identified 并排、互为稳健性、不分主次、禁混进同一 over-identified Hansen J; ss 轨检验主结论是否对 "把陈旧度限定在银行金科最紧密共现语境" 这一最窄口径稳健。本列同为非嵌入 carve-out, 无 `_lg` 孪生, 在涉 `_lg` 的批量列操作与 both-or-neither 平价守卫里须被显式排除 (这一点与依赖嵌入的 semantic_staleness_ss 恰相反, 后者才有 `_lg` 孪生并受 NEWS_PROCESS_LLM_OFFLINE 嵌入守卫)。确定性与 NaN 降级口径 (参照邻域空或文本退化置 NaN 伴 loud WARNING) 同 full 列, 零边际成本、离线态零漂移可复现。

<!-- rendered-citations:begin -->
Wu, C. (2025). Novelty and impact of economics papers. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.01211
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Kim, A. G., Muhn, M., & Nikolaev, V. V. (2023). Bloated disclosures: Can ChatGPT help investors process information?. SSRN Working Paper No. 4425527 [Working Paper]. https://doi.org/10.2139/ssrn.4425527
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Blankespoor, E., deHaan, E., & Marinovic, I. (2020). Disclosure processing costs, investors' information choice, and equity market outcomes: A review. Journal of Accounting and Economics, 70(2-3), 101344. https://doi.org/10.1016/j.jacceco.2020.101344
Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in firm disclosures: Obfuscation or information?. Journal of Accounting Research, 56(1), 85-121. https://doi.org/10.1111/1475-679X.12179
Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal of Accounting and Economics, 64(2-3), 221-245. https://doi.org/10.1016/j.jacceco.2017.07.002
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Lang, M., & Stice-Lawrence, L. (2015). Textual analysis and international financial reporting: Large sample evidence. Journal of Accounting and Economics, 60(2-3), 110-135. https://doi.org/10.1016/j.jacceco.2015.09.002
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information?. Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Glasserman, P., Mamaysky, H., & Qin, J. (2023). New News is Bad News. SSRN Electronic Journal (Working Paper No. 4555832) [Working Paper]. https://doi.org/10.2139/ssrn.4555832
Kumar, A., Tumre, S., & Patil, S. (2025). Benchmarking Near-Duplicate Detection in the era of Pay-walled News. Companion Proceedings of the ACM on Web Conference 2025 (WWW '25 Companion) [Working Paper]. https://doi.org/10.1145/3701716.3715303
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies. https://doi.org/10.1007/s11142-025-09897-1
<!-- rendered-citations:end -->
