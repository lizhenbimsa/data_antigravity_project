---
family_id: F156
columns:
- coh_lda_ctx
- coh_lda_full
- coh_lda_ss
unit: 无量纲连贯性得分, 值域 [0,1]; 高值 = 相邻两年主题分布接近 = 沟通连贯
formula: "coh_lda_{track} = 1 - JSD_distance(theta_{i,t}, theta_{i,t-1}); theta = LDA 主题分布 (K = max(10, n_total // 30)); JSD_distance = scipy.spatial.distance.jensenshannon(base=2) = sqrt(JSD) in [0,1]; 首年与年份间隙 -> NaN"
producer: news_process/pipeline/features/strategic_diff.py::_compute_lda_coherence ; news_process/pipeline/panel/export.py (列标签)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1145/3657299
  type: journal
  authors: Xia, B., Rawte, V., Gupta, A., & Zaki, M. J.
  year: 2024
  title: "FETILDA: Evaluation framework for effective representations of long financial documents"
  venue: ACM Transactions on Knowledge Discovery from Data
  vol: 18
  issue: 7
  pages_or_artno: 1-27
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: "10.1007/s11142-026-09952-5"
  type: "journal"
  authors: "Dai, L., Gong, P., Jackson, A. B., & Peng, Z."
  year: 2026
  title: "Controlling the narrative: managers’ topic-shifting behavior in conference calls"
  venue: "Review of Accounting Studies"
  vol: "31"
  issue: "2"
  pages_or_artno: "1165-1206"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 coh_lda_full / coh_lda_ctx / coh_lda_ss 度量的是同一家银行相邻两个年度媒体文本的"主题连贯性"(temporal text coherence): 把某银行在 year_t 的全部相关报道聚合成一份年度文本画像, 再与其 year_{t-1} 的年度文本画像作比较, 若两年谈论的主题结构接近则连贯性高, 反之则低。构念直觉来自公司披露文本的年际相似度研究传统 —— Cohen, Malloy 与 Nguyen (2020) 在其对公司年报年际措辞变动的研究中指出, 企业沟通文本在时间维度上的稳定与变化本身携带信息; 本项目把这一"自我披露年际相似"的思路平移到第三方媒体语料, 因此本家族测量的严格来说是"媒体感知的年际连贯"而非企业自撰披露的年际连贯, 两者构念不可等同 (详见已知局限)。项目内部把连贯性作为战略差异化 (strategic differentiation) 测度体系的时间维配套指标, 与横截面的同行差异度 (strat_diff / centroid_diff) 互补: 前者答"这家银行今年与去年像不像", 后者答"这家银行今年与同行像不像"。

【方法学与计算】
计算链路为 jieba 分词 → 词频计数 (CountVectorizer, max_features=5000, min_df=1, max_df=0.95, 词表清空时降级 max_df=1.0) → 潜在狄利克雷分配主题模型 (LatentDirichletAllocation) 抽取每份年度文档的主题分布向量 theta → 用 Jensen-Shannon 散度度量相邻两年 theta 的差异。主题数按 K = max(10, n_total // 30) 取定, 其中 n_total 是 year_t 与 year_{t-1} 两年文档合并后的池规模。⚠ 此处原载"两年合并池规模远不足 300 篇文档, 故 K 恒被 max(10, ·) 兜底为常数 10, 属'伪自适应'"—— 该结论沿袭自 2026-06-11 的源码披露 (omni-g-strategic-06), 其成立前提是早期小样本; 在生产 T=19 全量语料 (2007-2025, 每年有效 bank-year 文档数由 2007 年 29 家增至 2022 年 584 家) 上**已被实测证伪, 2026-07-28 订正**: 相邻两年池 n_total 在 2013 年即突破 300 (197+155=352), 至 2022 年达 1,147, 对应 K = max(10, n_total//30) 取值集为 {10, 11, 14, 18, 21, 26, 30, 31, 34, 36, 37, 38}, 最大 38 —— K 是**真自适应**而非常数。与之相应, 原载"仅因同被兜底为 10 而暂时数值一致, 只有当两年池文档数超过 300 时两处口径随之分叉"所预告的分叉**已经发生**: 横截面 _build_lda_jsd_matrix 用单年 n_banks 为基数, 生产上 K ∈ {10, 11, 14, 15, 18, 19} (最大 19, 与 stage 40 生产日志三轨各 37 次 LDA fit 逐条核对一致), 而本列用两年池 n_total 为基数, K 最大 38; 两者在 2007-2025 的 18 个可比年份中有 **13 年取值不同**。因此在解读时, 本列 (相邻期连贯性) 与横截面同行相似度族的主题空间粒度并不相同, 不可假定二者共享同一主题分辨率。散度计算调用 scipy.spatial.distance.jensenshannon(theta_t, theta_{t-1}, base=2), 该函数返回的是 √JSD (JSD 距离而非散度本身), base=2 使其上界恰为 1; 因此最终 coh_lda = 1 − √JSD ∈ [0,1], 高值表示两年主题分布接近即连贯 (Jensen-Shannon 散度是 Kullback-Leibler 散度的对称化平滑版本, 有界且对称, 其平方根满足度量公理即三角不等式, 因而适合作为两年主题分布间的距离度量)。首年 (无 t−1) 与年份间隙 (t−1 缺席) 一律返回 NaN, 严格定义"相邻期"为连续年度, 与产品市场流动性 strat_fluidity 的缺失口径一致。确定性由 random_state=42 + max_iter=50 + learning_method='online' + n_jobs=1 共同保证: 源码披露 (omni-g-strategic-16) 记录了 n_jobs=-1 时 sklearn 在线 LDA 的 E-step 会按有效核数切片累加充分统计量, 切片序跨机器不同导致 theta 逐位漂移 (实测 max|Δθ|≈0.99), 故必须钉死单线程才能逐位可复现。

【文献定位】
LDA+JSD 路径在本项目定位为 TF-IDF 主路径之外的稳健性检验测度: 三列均标注"稳健性检验", 与同族的 TF-IDF char/word 连贯性 (coh_tfidf_c / coh_tfidf_w) 及嵌入连贯性 (coh_emb) 互为稳健性、不分主次; 各测度各自 just-identified 并排, 严禁把不同方法的连贯列混进同一 over-identified Hansen J 检验。就构念本身的文献坐标而言, 与本家族"年际文本连贯"最贴近的顶刊参照是 Cohen, Malloy 与 Nguyen (2020) 发表于《Journal of Finance》的年报年际措辞变动研究: 他们以年报相邻期文本的相似与变动为核心, 证明沟通文本在时间维度上的稳定或改动本身即携带可定价信息, 这与本家族"相邻两年主题分布接近即连贯"的度量逻辑同源, 是本测度构念合法性的直接文献锚 (差别仅在于本项目把该思路从企业自撰披露平移到第三方媒体聚合语料, 详见【构念与来源】与已知局限)。方法学上另需一处诚实的口径说明: 本家族 LDA 的输入是 jieba 词频计数矩阵 (DTM), 而金融实证中"计数与类计数数据"的计量处理已由 Cohn, Liu 与 Wardlaw (2022, 《Journal of Financial Economics》) 系统梳理; 但须明确其讨论对象是回归中作为因变量的计数型结果变量 (Poisson / 负二项等), 与本家族把词频计数仅作为主题模型输入特征的用法并不等同, 此处援引仅为提示"以计数为底的数据在分布特征上需审慎"这一一般性方法学意识, 不构成对 LDA 文本主题建模本身的直接背书。文本表示层面, 长金融文档的有效表征评估框架由 Xia 等 (2024) 系统化提出, 其对"如何把冗长金融文本压缩为可比向量"的讨论与本项目将年度聚合文本压缩为 K 维主题分布的做法同源, 为本家族"用低维主题向量表征年度长文本再逐年比较"的表示选择提供了文本表征评估框架层面的参照。需要说明的是, LDA 主题建模面对第三方媒体聚合语料时存在若干未做披露的敏感性缺口 —— 例如未做 perplexity / held-out 数据驱动的选 K, 亦无 K ∈ {5,15,20} 的敏感性列 (类文本论文的标准披露项), 这是本测度作为稳健性配套而非主结论驱动变量的定位所允许的取舍。 在表征空间层面另有一处近期顶刊佐证可以补入: Dai、Gong、Jackson 与 Peng (2026) 发表于《Review of Accounting Studies》, 以 2002-2017 年电话会议样本用主题分析度量管理层回答偏离分析师提问主题的程度 (managerial topic-shifting), 发现业绩较好、CEO 权力较强、信息环境较弱的公司管理层转移更多, 且该转移行为向资本市场传递增量信息、促进盈余信息融入股价。该文对本家族的价值在于确立了两个主题分布之间的距离本身即为有实质经济含义的沟通行为测度而非建模噪声, 支持本族把主题分布距离作为标量测度落盘的做法。迁移边界须诚实交代: 原文的位移发生在同一场电话会议内的问答之间 (话轮层面, 以分析师提问主题为参照系), 本族则是同一银行相邻两年自身主题分布的距离 (年度层面, 以自身上期为参照系), 时间尺度与参照系均不同; 原文未使用 Jensen-Shannon 距离, 语料为英文管理层发言而非中文第三方报道; 且其构念是管理层回避而非战略差异化, 全文无任何同业或行业质心参照物, 故该锚点仅止于本族的年际自比构念, 不外推至横截面的质心偏离测度。此外该锚点属构念合法性层面的佐证, 不改变本族三条 LDA 连贯列相对 TF-IDF 与嵌入连贯列的定位 —— 各测度仍各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。
## VAR: coh_lda_full

【变体差分】
本列为 full 轨: 底层年度聚合文本取自 content_full, 即"标题 prepend + 全文正文"的三轨中信息量最全的一轨 —— 每篇相关报道的完整正文 (前置标题句) 逐篇进入该银行当年的年度聚合文档, 再走 jieba → CountVectorizer → LDA → JSD 链路算得相邻期连贯性。与 ctx/ss 两轨相比, full 轨捕捉的是银行被媒体报道的整体语义画像的年际稳定性, 不限定于金融科技实体窗口, 因此主题覆盖最宽、噪声也最高。full 轨须警惕共提及机械相似问题: 一篇同时提及 n 家银行的报道会逐字进入每家被提银行的年度聚合文档 (源码披露 omni-g-strategic-01/09), 这在横截面同行相似度上会制造与战略无关的机械相似, 在时间维连贯性上则可能因跨年共享语料而人为抬高连贯; 缓解手段包括同行年内重复全文的 content 去重 (默认开) 与稳健开关 co_mention_downweight。留篇门控采用 full-only 口径 (2026-06-29): 某篇是否计入某银行某年语料由 full 轨的 llm_verified_full 判定, 因此 full 轨的年度文档集是三轨中的母集, coh_lda_full 是本家族的锚定轨。本轨与 coh_lda_ctx / coh_lda_ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。首年与年份间隙返回 NaN, 与家族口径一致。就方法参数而言, full 轨与另两轨完全共享同一套 LDA 超参 (K=max(10, 两年池 n_total//30) — 生产 T=19 上实取 10-38, **非**旧载的常数 10, 详见上文 2026-07-28 订正、max_iter=50、learning_method='online'、random_state=42、n_jobs=1) 与同一 JSD base=2 距离口径, 三轨之间唯一的差分来自底层聚合文本的来源 (content_full 对全文正文), 而非任何模型、阈值或滞后设定的差异; 换言之三列在算法层完全同构, 只在语义粒度上分层, 这正是"互为稳健性"定位的技术前提。

## VAR: coh_lda_ctx

【变体差分】
本列为 ctx 轨: 底层年度聚合文本取自 content_ctx, 即"标题 + 实体窗口"文本 —— 只保留报道中目标银行实体附近的上下文窗口而非全文正文, 因此年度聚合文档聚焦于银行被提及处的语境, 剔除了与该银行无关的段落噪声。相对 full 轨, ctx 轨的主题分布更集中于银行相关议题, 其年际连贯性度量的是"银行相关语境"这一较窄语义子空间的年度稳定性。ctx 轨还有一项结构性优势: 由于其文本是 bank-specific 实体窗口, 跨银行逐字共享天然更弱, 因此前述共提及机械相似问题在 ctx 轨上显著轻于 full 轨 (源码披露 omni-g-strategic-09 明列此为缓解通道之一)。在 full-only 留篇门控下 (2026-06-29), ctx 轨为 conditional-on-full 的稳健性/测度轨: 行宇宙是 full 留篇集的子集, 但 ctx 轨的主题连贯列在其自身文档集上照常计算。本轨与 coh_lda_full / coh_lda_ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。ctx 轨在 T=2 开发盘上可能出现零方差退化 (窗口文本稀疏), 属预期, 生产 T=19 语料下正常; 首年与年份间隙同样返回 NaN。需强调 ctx 轨与 full 轨在 LDA 建模流程与 JSD 距离口径上逐参数一致, 唯一区别是喂入模型的年度聚合文本来源不同 (content_ctx 为实体窗口而非全文), 因此本列不引入任何新的模型、阈值或滞后维度, 纯粹是语义范围的收窄; 这一收窄使 ctx 轨在测度上更接近"银行相关议题"的年际稳定, 可作为 full 轨宽语义连贯的稳健性对照。

## VAR: coh_lda_ss

【变体差分】
本列为 ss 轨: 底层年度聚合文本取自 content_ss, 即"标题 + 银行∧金科同句共现窗 ±N"文本 (窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) —— 是三轨中语义最窄、判定最严的一轨, 只保留银行实体与金融科技词在同一句子邻近共现的文本片段。因此 coh_lda_ss 度量的是"银行×金融科技同句语境"这一最聚焦子空间的年际主题连贯性, 最贴近本项目银行金融科技叙事的核心构念, 但也最易受语料稀疏影响。ss 轨的回退语义严格镜像 ctx 轨: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True (与 ctx 共享 n_articles 分母口径); 当金融科技 AC 自动机为 None 时 *_is_fallback 全 True 优雅降级。在 full-only 留篇门控下 (2026-06-29) ss 轨同为 conditional-on-full 的稳健性/测度轨, 行宇宙是 full 留篇集子集。本轨与 coh_lda_full / coh_lda_ctx 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。ss 轨在 T=2 开发盘上因同句共现文本极稀疏而常见零方差或大面积 NaN 退化, 属预期, 生产 T=19 语料下方能充分取值; 首年与年份间隙返回 NaN。与 full / ctx 两轨一致, ss 轨的 LDA 超参与 JSD 距离口径逐参数相同, 唯一差分来自底层文本来源 content_ss 的同句共现窗口口径 (由 ss_sentence_radius 控制); 需特别注意该窗口半径键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 不可混用。因语义最窄, ss 轨的连贯性对语料密度最敏感, 定位为三轨中最贴近核心构念、也最需生产规模语料支撑的稳健性轨。

<!-- rendered-citations:begin -->
Xia, B., Rawte, V., Gupta, A., & Zaki, M. J. (2024). FETILDA: Evaluation framework for effective representations of long financial documents. ACM Transactions on Knowledge Discovery from Data, 18(7), 1-27. https://doi.org/10.1145/3657299
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Dai, L., Gong, P., Jackson, A. B., & Peng, Z. (2026). Controlling the narrative: managers’ topic-shifting behavior in conference calls. Review of Accounting Studies, 31(2), 1165-1206. https://doi.org/10.1007/s11142-026-09952-5
<!-- rendered-citations:end -->
