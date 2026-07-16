---
family_id: F490
columns:
- semantic_highstale_ctx
- semantic_highstale_ctx_lg
- semantic_highstale_full
- semantic_highstale_full_lg
- semantic_highstale_ss
- semantic_highstale_ss_lg
unit: 银行-年占比 (无量纲, 值域 [0,1]; 该行-年内语义高陈旧文章占有效文章的比例)
formula: "文章级 semantic_highstale_{track} = 1[semantic_staleness_{track} > 0.9]; 其中 semantic_staleness = 该文章嵌入向量对过去 7 日窗 [d-7d, d) 内 (严格排除同日) 文章嵌入的最大余弦相似度。银行-年面板列 = 该行-年内 semantic_highstale 的均值 (占比), 分母 = 语义陈旧度非 NaN 的有效文章数。"
producer: news_process/pipeline/text/article_staleness.py::aggregate_to_bank_year (阈值化) ← compute_semantic_staleness (相似度)
upstream:
- 25_article_sbert.parquet (co-primary 双轨嵌入 emb_{full,ctx,ss}(+_lg))
- 26_semantic_staleness.parquet (文章级 semantic_staleness_{track}(+_lg))
- 40_panel_yearly.parquet (面板 merge/导出; bank-year 聚合本身在 stage 26 aggregate_to_bank_year 完成)
citations:
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: You, K.
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
- doi: 10.1145/3701716.3715303
  type: journal
  authors: Kumar, A., Tumre, S., & Patil, S.
  year: 2025
  title: "Benchmarking near-duplicate detection in the era of pay-walled news"
  venue: Companion Proceedings of the ACM Web Conference 2025 (WWW '25 Companion)
  pages_or_artno: 745-748
- doi: 10.18653/v1/2025.naacl-industry.73
  type: journal
  authors: Tumre, S., Patil, S., & Kumar, A.
  year: 2025
  title: "Improved near-duplicate detection for aggregated and paywalled news-feeds"
  venue: "Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Industry Track)"
  pages_or_artno: 979-987
- doi: 10.1038/s41586-024-07421-0
  type: journal
  authors: Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y.
  year: 2024
  title: "Detecting hallucinations in large language models using semantic entropy"
  venue: Nature
  vol: 630
  issue: 8017
  pages_or_artno: 625-630
- doi: 10.18653/v1/2024.starsem-1.22
  type: journal
  authors: Han, G., Tsao, J., & Huang, X.
  year: 2024
  title: "Length-aware multi-kernel transformer for long document classification"
  venue: Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024)
  pages_or_artno: 278-290
- doi: 10.1145/3677136
  type: journal
  authors: Peng, Z., Zhang, Y., & Deng, D.
  year: 2024
  title: "Near-duplicate text alignment with one permutation hashing"
  venue: Proceedings of the ACM on Management of Data
  vol: 2
  issue: 4
  pages_or_artno: Article 222
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.3233/sw-222986
  type: journal
  authors: Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C.
  year: 2022
  title: "Neural entity linking: A survey of models based on deep learning"
  venue: Semantic Web
  vol: 13
  issue: 3
  pages_or_artno: 527-570
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: Tetlock, P. C.
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3982-3992
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
---

## CORE

【构念与来源】
本家族刻画的是"语义高陈旧报道占比"这一新闻信息新鲜度构念。其出发点是: 一篇银行金融科技报道所承载的语义内容, 在多大程度上只是对过去一小段时间内已经出现过的报道的语义重复。若一篇报道的语义与其之前七天内的某篇报道高度雷同, 则它对市场几乎不带来增量信息, 属于"陈旧"内容; 反之, 与近期报道语义相距较远的报道更可能承载新信息。家族列把这一逐篇的连续陈旧度得分在给定阈值上二值化, 再在银行-年层面聚合为占比, 得到"该银行该年度报道中语义高陈旧者所占的份额"。这一构念直接呼应金融学中关于陈旧信息与投资者反应的经典问题: Tetlock (2011) 系统检验了投资者是否会对被媒体重复转载的陈旧信息做出反应, 并以旧文重复程度作为信息新鲜度的度量。本家族把这一思想迁移到中文银行金融科技报道语料, 并以现代句向量嵌入替代早期的词面重叠度量, 从而在"语义"而非"字面"层面捕捉重复。

【构念与来源】(续)
数据来源与生产链路如下。上游 stage 25 (article_sbert) 为每篇报道产出 co-primary 双轨句向量嵌入 emb_{full,ctx,ss} 及其 _lg 孪生; stage 26 (semantic_staleness) 调用 compute_semantic_staleness, 对每篇报道在其嵌入空间内检索过去七天窗口的历史报道并计算最大余弦相似度, 得到逐篇连续得分 semantic_staleness_{track}(+_lg); 二值化与银行-年聚合并不在 stage 40 完成, 而是就在 stage 26 语义陈旧度阶段内 (article_staleness.py 的 main 函数体内) 由 aggregate_to_bank_year 一并产出: 该函数先把连续得分按阈值 0.9 二值化为文章级 semantic_highstale 指示, 再对每个 (target_bank, year) 组取均值, 得到本家族的六个银行-年占比列; stage 40 面板导出阶段仅负责把这些已聚合好的占比列 merge 进 40_panel_yearly 并导出, 不承担二值化或聚合逻辑。生产函数的权威位置是 pipeline/text/article_staleness.py: 相似度计算在 compute_semantic_staleness, 二值化与聚合在同模块 main 调用的 aggregate_to_bank_year (stage 26), 而非 stage 40。嵌入检索由 Faiss (IndexFlatIP) 加速, 内积等价于单位归一向量的余弦, 维度无关 (Qwen 4096 维 / large 3072 维直接流过, 两轨绝不混算)。

【方法学与计算】
逐篇语义陈旧度的计算口径必须精确复述, 因为其中若干设定是可复现性的承重点。第一, 窗口为日粒度的 [d-7d, d), 且严格排除同日行。这一"排除同日"是 2026-06-11 的关键修复 (fix omni-g-embed-01): 流水线会把同一篇报道 (同 docid) 按其匹配到的多家银行复制成多行, 若窗口含同日更早行, 则重复行内部余弦恒为 1.0, 使 semantic staleness 机械等于 1.0, 高陈旧信号几乎纯由该复制副作用驱动 (盘上曾出现 155/155 同日重复行全为 1.0), 且哪一行取到 1.0 依赖任意输入行序。排除同日后, surface 轨与 semantic 轨的窗口与 NaN 口径一致。第二, 窗口为空 (含语料首周、或近邻仅为同日行) 的文章其连续得分为 NaN, 在下游聚合中被 skip, 不计入分母。第三, 排序采用稳定排序 kind='stable' (metric-audit 2026-06-02 定论): 在大量同时间戳并列下, 非稳定 argsort 的并列顺序依赖输入行序, 会使得分随任意输入序漂移 (实测曾达 27% 行受影响), 稳定排序使其确定。第四, 对 NaT 日期采用 np.argsort(datetime64) 而非 pd.Series.argsort (后者对 NaT 返回 -1 致整列错位), NaT 稳定排到末尾、构成合法置换, 与还原原始行序的逆置换自洽。第五, 阈值二值化在 aggregate_to_bank_year 内向量化完成: high 列 = 1[stale > 0.9], 并把 stale 为 NaN 的行的 high 列同置 NaN, 使得均值 (占比) 自动跳过缺失; 随后按 (target_bank, year) 分组取 mean, 即得占比。分母因此是"语义陈旧度非 NaN 的有效文章数", 与面板其余 highstale 列同口径。

【文献定位】
本家族在方法学上立足于句向量嵌入与余弦相似度这一现代语义表示范式。以 Sentence-BERT (Reimers & Gurevych, 2019) 为代表的句向量方法, 通过孪生网络把句子/文档映射到稠密向量空间, 使语义相近的文本在向量空间中距离更近, 从而支持大规模最近邻检索; 本家族的嵌入轨正是这一范式在生产语料上的落地。余弦相似度作为语义接近度的度量并非无懈可击: You (2025) 系统讨论了余弦相似度"能用直到失效"的边界条件, 指出在某些几何/各向异性情形下余弦会给出误导性的语义接近判断; 这为本家族把余弦得分仅作为"重复度代理"而非"语义等价证明"提供了审慎注脚。在语义辨识的方向上, Farquhar et al. (2024) 提出以语义熵检测大模型幻觉, 其核心思想同样是在语义 (而非字面) 层面对内容进行聚类与判别, 与本家族"语义重复"的判据同源。对长文档的语义表示, Han et al. (2024) 提出长度感知的多核 Transformer, 提醒我们文档长度会影响嵌入质量——这与本家族三轨 (full/ctx/ss) 设计中"全文轨天然更长、上下文窗轨更短"的文本长度差异相关。实体链接综述 (Sevgili et al., 2022) 则为本项目"银行/金融科技实体识别→上下文窗抽取"的上游判定提供了方法学背景。在金融学定位上, Tetlock (2011) 的"陈旧新闻是否被反应"是本构念的经济学母题: 本家族把银行层面的语义高陈旧占比作为该银行媒体信息环境"新鲜度稀释"的代理, 服务于新闻情感/关注度对银行行为影响这一研究线中的稳健性与信息质量刻画。

【识别策略定位】
本家族的六列并非六个相互竞争的"更好/更差"测度, 而是沿两个正交维度展开的规格稳健性网格: 文本轨维度 (full/ctx/ss 三轨) 与嵌入轨维度 (canonical/MAIN 无后缀 与 _lg co-primary 双轨)。按 CLAUDE.md 铁律, 三轨与 co-primary 双轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨的列混进同一个 over-identified Hansen J 检验——两个 co-primary 嵌入轨各自 just-identified 并排, 禁混入同一 over-identified Hansen J; 三轨同理。识别上, 语义高陈旧占比可作为银行信息环境的控制变量或机制变量: 当研究媒体情感/关注度对银行融资成本、金融科技投资等结果的影响时, 高陈旧占比刻画了"该银行报道中有多大比例只是旧闻重复", 用以吸收报道量背后信息含量的异质性。其留篇域与面板行宇宙沿用 full-only 门控口径 (2026-06-29): 一篇报道是否被判为"一篇银行金融科技报道"只看 full 轨的 llm_verified_full, ctx/ss 轨降为 conditional-on-full 的测度/稳健性轨, 面板平均域收缩到 verified 面板语料。因此 full 轨占比与 ctx/ss 轨占比在样本框上并非对称: 后两轨是在 full 留篇集子集上按各自轨文本重算的规格稳健性对照。
识别层面还须厘清本家族在因果链条上扮演的角色边界。语义高陈旧占比并非本项目任何一篇主线论文的处理变量 (treatment) 或结果变量 (outcome), 而是刻画银行媒体信息环境"质量维度"的一个可观测代理, 因此它进入回归的正当身份是控制变量或调节 (机制) 变量, 而非被解释的核心变量。作为控制变量时, 其识别价值在于吸收"报道量-信息含量"之间的混淆: 若某银行某年报道量激增但其中大量为通稿转载的语义近似重复, 则单纯以报道条数或篇幅衡量的关注度会系统性高估真实信息投放; 把语义高陈旧占比同时纳入右手边, 相当于对"每单位报道的语义新意"做了显式的观测控制, 从而使情感强度或关注度对结果 (融资成本、金融科技投资等) 的估计更接近"新信息驱动"而非"重复噪声驱动"。这与 Fang & Peress (2009) 关于媒体报道本身在股票横截面定价中并非中性的经典发现相衔接——既然报道的"有无/多寡"已具定价含义, 那么报道的"新旧/是否重复"更需被显式建模, 否则媒体覆盖变量会同时裹挟数量与新鲜度两重异质性。作为调节变量时, 语义高陈旧占比可用于检验信息新鲜度是否削弱媒体情感的传导斜率: 一个先验假设是, 当报道流中充斥语义重复的旧闻时, 边际报道的情感信号对市场的增量说服力下降, 表现为情感×高陈旧占比交互项的显著负号。无论作为控制还是调节, 本家族六列都以"文本三轨 × 嵌入双轨"的规格网格出现, 目的是让这一识别不因文本粒度 (全文/实体窗/同句共现) 或嵌入实现 (Qwen 4096 维 / large 3072 维) 的任意选择而改变结论。须再次强调 CLAUDE.md 铁律的操作后果: 六列虽同源, 但绝不能因"都测语义陈旧"就把它们并入同一个 over-identified 的工具变量 Hansen J 过度识别检验——三轨各自 just-identified 并排、co-primary 双轨各自 just-identified 并排, 混用会人为制造过度识别约束并污染 J 统计量的原意, 这在方法上是错误的。正确用法是把不同轨/不同嵌入的结果作为并排汇报的规格稳健性证据, 各自独立地进入 just-identified 的设定, 再横向比较系数符号与显著性的一致性。

【与相邻测度的构念区分】
本家族须与两个近邻严格区分。其一是 surface staleness / surface_highstale (字面陈旧度): 后者基于 MinHash 字符 shingle 的 Jaccard 相似度, 度量的是"字面/表述"层面的重复, 属非嵌入 carve-out, 因此没有 _lg 孪生, 也不进入本家族。语义轨与字面轨互为补充: 一篇改写了措辞但语义照旧的旧闻, 字面陈旧度低而语义陈旧度高; 二者的低相关正是同时保留两族的理由。生产日志会实测 surface 与 semantic 全文轨的相关系数用以监控二者确实捕捉不同信号。其二是连续得分 semantic_staleness_{track} 本身 (F 家族的另一族): 那是逐篇余弦最大值的银行-年均值 (水平), 而本家族是其在 0.9 阈值上二值化后的占比 (尾部频率)。均值刻画"平均有多旧", 占比刻画"有多大比例特别旧"; 阈值 0.9 是一个刻意保守的高位截断, 使占比聚焦于近乎重复的极端尾部, 对分布中段不敏感。二者是同一底层信号的水平矩与尾部矩, 服务于不同的稳健性叙事, 不应互相替代。

【方法学与计算】(实现细节)
从工程实现角度须再补充几点, 以便复现者精确重建本家族。检索由 Faiss 的 IndexFlatIP (内积平坦索引) 完成: 在单位归一化的嵌入向量假设下, 内积等价于余弦相似度, 因此索引直接返回余弦最大近邻。IndexFlatIP 是精确 (非近似) 检索, 不引入 ANN 的随机性, 与稳定排序共同保证逐篇得分的可复现性。索引按天分桶构建: 对每一目标日 d, 先把 [d-7d, d) 窗口内的历史文章嵌入加入索引 (严格不含 d 当天), 再对 d 当天的每篇文章做一次查询取窗口内最大余弦, 窗口为空时该文章得分置 NaN。维度上, canonical/MAIN 轨嵌入为 4096 维 (Qwen/Qwen3-Embedding-8B), _lg 轨为 3072 维 (text-embedding-3-large); compute_semantic_staleness 的实现维度无关, 由 emb.shape[1] 驱动, 两轨各自建索引、各自查询, 绝不跨维度混算。col_suffix 参数 (''或'_lg') 仅用于日志区分两轨, 不参与任何数值计算。逆置换还原原始行序是承重步骤: 计算前按日期稳定排序得到 _sort_idx, 计算后以 stale[np.argsort(_sort_idx)] 还原, 与 main 的按位置赋值对齐 (这是 metric-audit 2026-06-02 的 P0 修复, 否则整列错位)。二值化阈值 0.9 在 aggregate_to_bank_year 内以向量化布尔运算实现, 并显式把 stale 为 NaN 的行的 high 列回填 NaN, 确保占比分母只计有效行、与连续得分族的均值分母口径完全一致。

【方法学与计算】(三轨文本口径)
本家族的三轨文本来源须与其余家族对齐理解。full 轨 = content_full = 标题 prepend + 全文正文; ctx 轨 = content_ctx = 标题 prepend + 目标实体附近窗口文本; ss 轨 = content_ss = 标题 prepend + 银行与金融科技词同句 (±N 句窗, 由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 共现处文本。三轨文本统一在 stage 14 (ctx_materializer) 物化, 标题以 prepend 方式并入 (v3.8.0 起取消独立 title 轨, 标题改为前置拼接), 原始"内容"列不动。ss 轨的回退语义镜像 ctx: 当某篇报道无银行与金融科技同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 与其余轨共享 n_articles 分母; 若上游金融科技 AC 自动机为 None, 则相关 is_fallback 全置 True 优雅降级。三轨判定采用不对称口径: 银行侧含否定与短名过滤, 金融科技侧用裸 AC 词表匹配。三轨文本各自喂入 stage 25 嵌入与 stage 26 语义陈旧度计算, 因此本家族三轨的语义空间输入天然不同 (全文最长、实体窗次之、同句共现最窄), 这也是三轨占比互为稳健性而非冗余复制的根本原因。须再次强调: 三轨禁混同一 over-identified Hansen J。

【文献定位】(信息新鲜度与市场反应)
在经济金融维度上, 本构念的价值链条可进一步展开。Tetlock (2011) 以"陈旧新闻是否被投资者反应"为题, 发现被重复转载的旧信息仍会引发可测量的市场反应, 并以旧文重复度作为信息新鲜度的操作化度量; 这为"语义高陈旧占比"作为银行媒体信息环境质量代理提供了直接的经济学母题。本家族把该思想从个股旧闻迁移到银行层面的金融科技报道流, 并以现代句向量替代早期词面 (bag-of-words) 重叠, 使"重复"的判定从字面提升到语义。这一提升的方法学基础是 Sentence-BERT (Reimers & Gurevych, 2019) 所奠定的稠密句表示范式: 通过孪生网络学习使语义相近文本在向量空间邻近, 支持工业规模最近邻检索。但须审慎: You (2025) 提醒余弦相似度在特定几何条件下会失效, 高余弦未必等价于语义等同; 本家族以 0.9 高截断和 co-primary 双轨互证两道防线来缓解这一风险。语义层面的辨识思路与 Farquhar et al. (2024) 以语义熵检测幻觉一脉相承——两者都主张在语义聚类而非字面匹配层面判断内容异同。文档长度对嵌入质量的影响 (Han et al., 2024) 则解释了为何本家族坚持三轨并排: 全文、实体窗、同句共现三种文本长度在嵌入质量上各有取舍, 不宜以单一长度轨定论。上游实体判定的方法学背景见实体链接综述 (Sevgili et al., 2022)。综合来看, 本家族处在"金融学信息新鲜度命题"与"自然语言处理语义表示与相似度"两条文献脉络的交汇点: 它借 NLP 的句向量与余弦检索工具, 回答金融学关于陈旧信息的经济学问题, 并以银行-年占比这一计量友好的聚合形式接入面板回归。

【文献定位】(近重复检测与词嵌入的应用方法学)
本家族在计算机科学一侧直接落在"新闻近重复检测 (near-duplicate detection)"这一成熟子领域。近年针对付费墙与聚合新闻源的近重复检测出现了一批工程化研究: Kumar et al. (2025) 系统构建了付费墙时代新闻近重复检测的基准 (benchmark), 揭示在授权转载、聚合改写盛行的现代新闻生态中, "同一条新闻的多份近似副本"是普遍且需专门建模的现象; Tumre et al. (2025) 进一步针对聚合与付费新闻流改进了近重复检测方法, 强调跨源转载副本的召回。这两项工作从工程层面印证了本家族的动机——银行金融科技报道流中充斥通稿转载与近似改写, 若不度量重复, 报道量将系统性高估真实信息投放。在近重复判定的算法基元上, Peng et al. (2024) 提出以单次置换哈希 (one permutation hashing) 做近重复文本对齐, 与本项目字面陈旧族 (surface, 基于 MinHash 字符 shingle) 的哈希-Jaccard 思路同源; 本家族则刻意选择句向量余弦而非哈希 Jaccard, 以在语义层 (而非字面层) 捕捉"改写措辞但语义照旧"的旧闻, 二者构成新鲜度大类下互补的两条技术路线。在把词/句嵌入用于社科与金融文本的应用方法学一侧, Rodriguez & Spirling (2022) 系统评估了词嵌入在应用研究中"何时有效、何时失效、如何辨别", 为本家族以嵌入余弦作重复代理提供了应用层的效度告诫——嵌入并非黑箱可信, 须以任务相关的效度检验与稳健性对照来使用, 这正是本家族坚持 co-primary 双轨互证 (Qwen 4096 维 vs large 3072 维) 与三轨并排的方法学理由。金融文本方向上, Zheng et al. (2024) 用词嵌入方法刻画金融文本情感的时间演化, 表明嵌入表示能够捕捉金融语料中随时间漂移的语义结构; 这与本家族"在七天历史窗内以嵌入检索衡量语义重复"的时序设定相呼应——只是本家族关注的是语义的"重复/不变"而非"演化/漂移", 二者是同一嵌入时序分析的两个互补切面。综上, 近重复检测 (Kumar et al., 2025; Tumre et al., 2025; Peng et al., 2024) 提供了本构念在 CS 侧的问题定义与算法谱系, 应用词嵌入研究 (Rodriguez & Spirling, 2022; Zheng et al., 2024) 则提供了把嵌入用于社科/金融文本时的效度纪律, 二者共同支撑本家族"以句向量余弦在语义层度量新闻重复"的方法选择。

【文献定位】(在本项目测度体系中的位置)
在本项目自身的测度体系内, 语义陈旧族与字面陈旧族 (surface, MinHash) 构成"新鲜度"这一大类下的两个互补分支, 二者又与情感族 (LLM 三家投票 / 词典 / BERT 三模型)、关注度族、以及网络溢出族相互独立、各司其职。语义高陈旧占比刻画的是信息"新不新", 而非信息"好不好 (情感)"或"多不多 (关注度)"; 它回答的问题是同一银行的报道流里有多少只是旧闻的语义翻版。这一维度对识别至关重要: 若不控制新鲜度, 报道量或情感强度的估计可能被"大量低信息含量的重复报道"所污染。本家族因此常作为信息环境质量控制或调节变量进入 P1 (情感→融资成本)、P2 (关注度→金融科技投资) 等主线论文的稳健性与机制分析, 其六列则以文本三轨 × 嵌入双轨的规格网格, 保证该控制/机制不因文本粒度或嵌入实现的任意选择而改变结论。须最后重申贯穿全家族的铁律: 三轨 (full/ctx/ss)、co-primary 双轨 (无后缀/_lg) 各自 just-identified 并排、互为稳健性、不分主次, 任何情况下都禁止把它们混进同一个 over-identified Hansen J 过度识别检验。

须坦陈若干局限。第一, 阈值 0.9 是研究者设定, 其绝对高度带有 model-specific 含义: 不同嵌入模型 (Qwen 4096 维 vs large 3072 维) 的余弦相似度分布尺度不同, 因此 canonical 轨与 _lg 轨的占比水平不宜直接比较绝对高低, 只宜比较标准化后的回归系数与方向一致性——这正是保留 _lg co-primary 孪生作互证的意义: 两轨若给出方向一致、显著性相仿的结论, 则主结论不被单一厂商嵌入空间的几何驱动。第二, 余弦相似度作为语义重复的代理有其失效边界 (You, 2025), 极端各向异性下高余弦未必等于语义等价; 0.9 的高截断在一定程度上缓解了这一风险 (只有非常接近的对才被计为高陈旧)。第三, 同日重复副作用已由"严格排除同日行"修复, 但跨日的多银行复制行仍可能带来轻度机械相关, 属已知残留。第四, 在开发期 T=2、语料极浅时, 窗口空导致大量 NaN, ss 轨在极短面板上可能退化 (与其在 ctx 轨的回退语义一致: 缺列即跳过, 优雅降级), 属预期退化而非缺陷; 生产 T=19 全语料下窗口充分填充, 信号正常。第五, co-primary 双轨遵循 both-or-neither 守卫: 若某轨的 MAIN 嵌入缺失, 则该轨的无后缀与 _lg 两列同置缺席, 不产生单边孤儿。围绕本家族的稳健性梯子因此由文本三轨、嵌入双轨、以及与之正交的连续得分族/字面陈旧族共同构成, 各梯级各自 just-identified 并排, 禁混同一 over-identified Hansen J。

【已知局限与稳健性梯子】(阈值与聚合的补充)
关于阈值 0.9 本身还须补两点。其一, 阈值梯子在本家族未展开为多档 (不像情感权重的 {0.0,0.5,1.0} 或极端负面占比的 {0.80,0.90,0.95}), 而是固定为单一高截断; 若未来需要阈值敏感性, 应沿"多阈值各自 just-identified 并排、禁混同一 over-identified Hansen J"的既有纪律扩展, 而非把不同阈值列塞进同一过度识别检验。其二, 占比这一聚合形式对分母 (有效文章数) 敏感: 在报道极少的银行-年, 分母小使占比方差放大, 单篇高陈旧就能把占比顶到很高; 因此在回归中通常需以报道量或其对数作控制, 或对薄样本银行-年做稳健性剔除。关于分子的二值化, 0.9 的高截断意味着本家族只捕捉近乎重复的极端尾部, 对"中度相似"的旧闻不敏感——这是刻意的构念选择 (聚焦"几乎照搬"而非"主题相近"), 但也意味着它不能替代连续得分族对分布中段的刻画。最后须重申门控纪律: 面板平均域由 _restrict_to_panel_domain 收缩到 verified 面板语料, full 轨的 llm_verified_full 定义留篇, ctx/ss 为 conditional-on-full; 这一 full-only 口径 (2026-06-29) 使 full 轨占比与 ctx/ss 轨占比在样本框上不对称, 解读跨轨差异时必须把这一子集关系纳入考量, 不可误读为纯粹的测度差异。

## VAR: semantic_highstale_full

【变体差分】
本列是家族 canonical 核心列, 也是 full-only 门控口径 (2026-06-29) 下的 headline 轨。其精确语义为: 在 full 全文轨 (content_full = 标题 prepend + 全文正文) 上, 用 canonical/MAIN 嵌入轨 (Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动端点, 无后缀即代表 canonical) 计算的逐篇语义陈旧度, 经阈值 0.9 二值化后, 在银行-年层面取均值得到的语义高陈旧文章占比。文本轨上, full 轨消费的是标题拼接后的整篇正文, 因此文本最长、语义覆盖最全, 是判定"是否一篇银行金融科技报道"的门控轨——面板行宇宙即由 full 轨的 llm_verified_full 定义, 该列的分母 (语义陈旧度非 NaN 的有效文章) 直接落在 verified 留篇集上。嵌入轨上, 本列取 canonical Qwen 4096 维空间的余弦最大值, 是与其 _lg 孪生 (semantic_highstale_full_lg, text-embedding-3-large 3072 维) 严格并排的 co-primary 主测度之一。阈值维度上, 0.9 是家族统一的高位截断, 使本列聚焦近乎重复的极端尾部; 判据维度上, 窗口为日粒度 [d-7d, d) 严格排除同日行, 稳定排序保证确定性。相对家族内其余五列, 本列同时占据"full 文本轨 + canonical 嵌入轨"这一双维原点, 是其余五列 (ctx/ss 文本变体、_lg 嵌入变体) 稳健性对照所环绕的基准。须重申铁律: 本列与其 _lg 孪生各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与 ctx/ss 两轨同理。作为 canonical 列, 它承担与情感/关注度结果变量并列进入基线回归、或作为银行信息环境控制/机制变量的主要角色, 而 ctx/ss 与 _lg 诸列则在规格曲线上提供并排的方向一致性检验。它与同底层的连续得分列 semantic_staleness_full (水平矩) 及字面陈旧族 surface_highstale_full (MinHash 字面轨, 无 _lg) 构念不同, 不可互替。就该列的经济学解读而言, 一个较高的 semantic_highstale_full 意味着该银行当年的金融科技报道流中, 有相当比例的报道在语义上只是过去七天内已有报道的近乎重复——这既可能反映媒体对该行金融科技议题的"跟风转载/通稿复制"式覆盖, 也可能反映该行金融科技信息本身缺乏实质增量。作为控制变量, 它帮助把"报道量大但信息含量低"与"报道量大且信息新鲜"两种情形区分开, 从而净化情感/关注度对结果 (如融资成本、金融科技投资) 的估计。作为机制变量, 它可用于检验信息新鲜度是否调节媒体情感的传导强度。其在开发期 T=2 极浅面板上会因窗口空而出现较多 NaN, 生产 T=19 全语料下窗口充分, 信号趋于稳定, 这一样本深度差异在解读开发期数值时须牢记。就该列的技术根基而言, 其嵌入来自 stage 25 的 canonical Qwen 轨 (无后缀槽), 语义陈旧度由 stage 26 用 Faiss IndexFlatIP 精确检索日粒度七天窗、严格排除同日行、稳定排序、逆置换还原行序后取余弦最大值算得, 二值化与 (target_bank, year) 均值聚合同样在 stage 26 内 (article_staleness.py 的 main 调用 aggregate_to_bank_year) 按 0.9 阈值一并完成, stage 40 面板导出阶段只负责把聚合好的占比列 merge 进面板并导出、不承担阈值化或聚合。整条链路每一步都是确定性的 (精确检索无 ANN 随机、稳定排序无并列漂移), 因此本列在固定嵌入缓存下逐位可复现, 是家族内其余五列比对的基准锚。它服务的核心问题——语义高陈旧占比是否影响、或调节媒体信息对银行行为的传导——正是 Tetlock (2011) 陈旧信息命题在银行金融科技语境下的落地。

## VAR: semantic_highstale_full_lg

【变体差分】
本列是 semantic_highstale_full 的 _lg co-primary 对偶, 与 canonical 列并列构成核心双轨。其唯一的差分维度在嵌入轨: 它在 full 全文轨上、改用 _lg 嵌入套 (text-embedding-3-large, 3072 维, OpenAI/yunwu 端点) 计算逐篇语义陈旧度的余弦最大值, 再经同一 0.9 阈值二值化并在银行-年聚合为占比。除嵌入模型与维度外, 其文本轨 (full = 标题 prepend + 全文正文)、窗口判据 (日粒度 [d-7d, d) 严格排除同日、稳定排序)、阈值 (0.9)、聚合口径 (bank-year 均值、分母为非 NaN 有效文章) 与留篇门控 (full-only, verified 面板域) 均与 canonical 列逐字一致。设立本列的目的是跨厂商、跨嵌入维度的互证: 中文金融科技报道的语义高陈旧信号若在阿里 Qwen 4096 维与 OpenAI large 3072 维两个独立几何空间中同时成立, 则主结论不被任一单一嵌入空间的各向异性或维度选择所驱动 (呼应 You (2025) 关于余弦相似度失效边界的告诫)。须严格遵守 CLAUDE.md 铁律: 本 _lg 列与 canonical 无后缀列是两个各自 just-identified 的 co-primary 主测度, 并排互证、不分主次, 绝对禁止把两轨的语义陈旧列混入同一个 over-identified Hansen J 过度识别检验——这是嵌入双轨最核心的使用约束。降级语义上, 本列受 both-or-neither 守卫约束: 若 full 轨的 _lg 嵌入 (emb_full_lg) 缺失 (例如旧 stage 25/26 parquet 未重跑双轨), 则 semantic_highstale_full 与 semantic_highstale_full_lg 两列一并缺席, 不产生单边孤儿列。同时因阈值 0.9 的语义随嵌入空间尺度变化, 本列与 canonical 列的占比绝对水平不宜直接比高低, 只宜比较标准化回归系数的符号与显著性是否一致。作为 core 列, 它与 canonical full 列共同承担核心双轨互证职责, 其余 ctx/ss 及各自 _lg 列则沿正交的文本轨维度提供进一步的规格稳健性。就实现而言, 本列的 _lg 嵌入来自 text-embedding-3-large 空间, 其缓存键与厂商端点均与 canonical Qwen 轨不同, 但语义陈旧度的算法路径 (Faiss IndexFlatIP 精确检索、日粒度七天窗、严格排除同日、稳定排序、逆置换还原行序、0.9 阈值二值化、bank-year 均值聚合) 与 canonical 列逐步一致——差异被严格限定在"用哪一个嵌入空间做余弦"这一单一自由度上。正因如此, 两列结论若一致即构成强互证: 一个在 4096 维阿里几何、一个在 3072 维 OpenAI 几何, 二者对"某银行某年语义高陈旧占比"的排序若高度吻合, 则该信号被判为不依赖单一嵌入实现的稳健语言学事实, 而非某一模型各向异性的伪影 (You (2025) 所警示的余弦失效边界因此被双轨证伪机制部分对冲)。反之若两轨系统性分歧, 则应回到嵌入质量与文档长度 (Han et al., 2024) 层面排查, 而非贸然采信任一单轨。本列在论文规格曲线中通常与 canonical full 列并列汇报, 作为核心结论的第一道稳健性锚, 再由 ctx/ss 诸轨补齐文本粒度维度的稳健性。须再次强调 both-or-neither 守卫的对称性: full 轨的 MAIN 与 _lg 嵌入任一缺失 (例如 stage 25 旧 parquet 未重跑双轨), 则 semantic_highstale_full 与 semantic_highstale_full_lg 两列一并置缺席, 系统绝不产生单边孤儿列, 从而保证 co-primary 双轨在任何数据状态下都是"要么两列俱在、要么两列俱无"。这一守卫使双轨互证的前提 (两列同时可比) 始终成立, 也避免了下游误把单轨当作全部证据。综上, 本 _lg 核心列的存在意义不在于自身单独定论, 而在于与 canonical 列构成不可分割的互证对, 共同把"语义高陈旧"这一结论从"某模型下成立"提升为"跨两大主流嵌入实现下稳健成立"。

## VAR: semantic_highstale_ctx

【变体差分】
本列是 canonical/MAIN 嵌入轨 (Qwen 4096 维) 在 ctx 上下文窗轨上的语义高陈旧占比。其相对 canonical full 列的唯一差分在文本轨: ctx 轨消费 content_ctx = 标题 prepend + 目标实体窗口文本 (银行/金融科技实体附近的局部窗口, 而非整篇正文), 在 stage 14 (ctx_materializer) 物化。因此它度量的是"围绕银行金融科技实体的局部语义"层面的重复, 文本更短、更聚焦于实体上下文。除文本轨外, 其嵌入轨 (canonical Qwen 4096 维)、窗口判据 (日粒度 [d-7d, d) 严格排除同日、稳定排序)、阈值 (0.9)、聚合与分母口径均与 canonical 列一致。在 full-only 门控口径下 (2026-06-29), ctx 轨属 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 轨 verified 留篇集的子集, 占比按 ctx 轨文本重算。因文本更短, 局部窗内可用于检索的语义信息较少, 在极浅面板上更易出现窗口空/NaN 退化, 属预期行为。本列与其 _lg 孪生 (semantic_highstale_ctx_lg)、以及 full/ss 各轨列, 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。它的价值在于回答"若只看实体上下文而非全文, 语义高陈旧结论是否依然成立", 从而在文本轨维度上为 canonical full 结论提供并排的规格稳健性对照。相较全文轨, ctx 轨剔除了与银行金融科技议题无关的段落, 因此其语义陈旧度更纯粹地反映"实体周边叙述"的重复程度, 对全文中大量样板/背景文字的干扰更不敏感; 但代价是文本更短、可供区分的语义信息更少, 在窗口检索中更易出现高相似的偶合。二者取舍无绝对优劣, 故并排保留。

## VAR: semantic_highstale_ctx_lg

【变体差分】
本列是 semantic_highstale_ctx 的 _lg co-primary 对偶: 同在 ctx 上下文窗轨 (content_ctx = 标题 prepend + 实体窗口文本) 上, 改用 _lg 嵌入套 (text-embedding-3-large, 3072 维) 计算语义陈旧度并经 0.9 阈值二值化聚合为银行-年占比。它同时沿两个维度偏离 canonical full 列: 文本轨 (ctx 而非 full) 与嵌入轨 (_lg 而非 MAIN)。除此之外的窗口判据、阈值、聚合口径与门控域均与家族统一口径一致。设立本列是为在"实体上下文文本 × large 嵌入空间"这一组合下复核语义高陈旧信号, 与 semantic_highstale_ctx (Qwen 空间) 构成 ctx 轨内部的 co-primary 双轨互证。按铁律, 本 _lg 列与其无后缀孪生各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 与 full/ss 各轨列亦然。降级上遵守 both-or-neither: ctx 轨 _lg 嵌入缺失时, semantic_highstale_ctx 与 semantic_highstale_ctx_lg 两列同置缺席。因阈值语义随嵌入空间尺度而变, 本列占比水平不宜与 Qwen 轨或 full 轨直接比高低, 只比较标准化系数方向。作为 standard 列, 它在文本轨与嵌入轨的交叉格点上补齐规格稳健性网格, 服务于"结论不依赖特定文本粒度与特定嵌入厂商"的稳健性叙事, 而非承担独立的核心识别角色。具体而言, 若 canonical full 结论在 ctx 轨的 Qwen 与 large 两个空间中都能重现, 则文本粒度维度与嵌入厂商维度的交叉稳健性同时得到验证, 这比任一单维稳健性更有说服力。反之若唯独本列偏离, 应先排查 ctx 轨 large 嵌入是否因文本过短而质量下降 (Han et al., 2024 关于长度敏感的提示), 而非直接质疑主结论。

## VAR: semantic_highstale_ss

【变体差分】
本列是 canonical/MAIN 嵌入轨 (Qwen 4096 维) 在 ss 同句共现轨上的语义高陈旧占比。其相对 canonical full 列的差分在文本轨: ss 轨消费 content_ss = 标题 prepend + 银行与金融科技词同句 (±N 窗, 由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 共现处的局部文本。它度量的是"银行与金融科技概念真正在同一句语境中共现"这一最严格局部语境下的语义重复, 文本轨最窄、最贴合共现事件。ss 轨的回退语义镜像 ctx: 当某篇报道无银行与金融科技的同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 并与其余轨共享 n_articles 分母。除文本轨与回退语义外, 其嵌入轨 (canonical Qwen 4096 维)、窗口判据 (日粒度 [d-7d, d) 严格排除同日、稳定排序)、阈值 (0.9)、聚合与分母口径均与家族统一口径一致。在 full-only 门控下 (2026-06-29), ss 轨同属 conditional-on-full 稳健性轨, 行宇宙为 full verified 留篇集子集。因文本最窄, 在开发期极浅面板上 ss 轨最易零方差/全 NaN 退化 (属预期, 缺列即跳过、优雅降级); 生产 T=19 全语料下正常。本列与其 _lg 孪生 (semantic_highstale_ss_lg) 及 full/ctx 各轨列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。它回答"若只看银行与金融科技真正同句共现处的语义, 高陈旧结论是否成立", 是文本轨维度上最严格的规格稳健性对照。

## VAR: semantic_highstale_ss_lg

【变体差分】
本列是 semantic_highstale_ss 的 _lg co-primary 对偶: 同在 ss 同句共现轨 (content_ss = 标题 prepend + 银行与金融科技同句共现文本, 回退语义镜像 ctx) 上, 改用 _lg 嵌入套 (text-embedding-3-large, 3072 维) 计算语义陈旧度并经 0.9 阈值二值化聚合为银行-年占比。它沿文本轨 (ss) 与嵌入轨 (_lg) 两个维度同时偏离 canonical full 列, 其余窗口判据、阈值、聚合口径、门控域与家族统一口径一致。设立本列是为在"同句共现文本 × large 嵌入空间"这一最严格文本粒度与另一嵌入厂商的组合下复核语义高陈旧信号, 与 semantic_highstale_ss (Qwen 空间) 构成 ss 轨内部的 co-primary 双轨互证。按铁律, 本 _lg 列与其无后缀孪生各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 与 full/ctx 各轨列亦然。降级遵守 both-or-neither: ss 轨 _lg 嵌入缺失时, semantic_highstale_ss 与 semantic_highstale_ss_lg 两列同置缺席; 且 ss 轨依赖 stage 25 是否为 content_ss 产出对应嵌入, 旧 parquet 未重跑 ss 轨时该轨整族优雅跳过。因阈值语义随嵌入空间尺度变化, 本列占比水平不宜与其他轨直接比高低, 只比较标准化系数方向。作为 standard 列, 它在最窄文本轨与 large 嵌入的交叉格点补齐规格稳健性网格的最后一格, 使"语义高陈旧"结论在文本粒度与嵌入厂商双维上均可被并排检验。因 ss 轨文本最窄且带回退机制, 本列在开发期极浅面板上信噪比最低、退化最明显, 其数值应审慎解读; 在生产 T=19 全语料下同句共现事件充分, 该轨方能提供最贴合"银行与金融科技真正同框叙述"这一最严格语境的语义重复度量。它与 semantic_highstale_ss (Qwen 轨) 的绝对占比水平因嵌入尺度差异不可直接比高低, 只比标准化系数方向, 这与其余 co-primary 双轨的解读纪律完全一致。

<!-- rendered-citations:begin -->
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Kumar, A., Tumre, S., & Patil, S. (2025). Benchmarking near-duplicate detection in the era of pay-walled news. Companion Proceedings of the ACM Web Conference 2025 (WWW '25 Companion), 745-748. https://doi.org/10.1145/3701716.3715303
Tumre, S., Patil, S., & Kumar, A. (2025). Improved near-duplicate detection for aggregated and paywalled news-feeds. Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Industry Track), 979-987. https://doi.org/10.18653/v1/2025.naacl-industry.73
Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature, 630(8017), 625-630. https://doi.org/10.1038/s41586-024-07421-0
Han, G., Tsao, J., & Huang, X. (2024). Length-aware multi-kernel transformer for long document classification. Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024), 278-290. https://doi.org/10.18653/v1/2024.starsem-1.22
Peng, Z., Zhang, Y., & Deng, D. (2024). Near-duplicate text alignment with one permutation hashing. Proceedings of the ACM on Management of Data, 2(4), Article 222. https://doi.org/10.1145/3677136
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C. (2022). Neural entity linking: A survey of models based on deep learning. Semantic Web, 13(3), 527-570. https://doi.org/10.3233/sw-222986
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information?. Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP), 3982-3992. https://doi.org/10.18653/v1/D19-1410
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
<!-- rendered-citations:end -->
