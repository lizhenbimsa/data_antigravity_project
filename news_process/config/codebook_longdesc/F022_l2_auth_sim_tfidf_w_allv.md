---
family_id: F022
columns:
- auth_sim_tfidf_w_allv_ctx
- auth_sim_tfidf_w_allv_full
- auth_sim_tfidf_w_allv_ss
unit: 余弦相似度 (无量纲, 取值域 [0,1])
formula: "auth_sim_tfidf_w_allv{track} = cosine( TFIDF_word(银行年度聚合文本), TFIDF_word(全年份静态政策锚点) ); 词级 TF-IDF 采用 jieba 分词, max_features=5000, min_df=1, max_df=0.95, sublinear_tf=True; 锚点=全部年份政策文档拼接 (静态, 非 vintage)"
producer: news_process/pipeline/features/policy_similarity.py::_ghost_anchor_metrics
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (target_bank, year 聚合骨架)
citations:
- doi: 10.18653/v1/2025.emnlp-main.1135
  type: journal
  authors: Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S.
  year: 2025
  title: "Interpretable text embeddings and text similarity explanation: A survey"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 22314-22330
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: You, K.
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv [Preprint]
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.1145/509907.509965
  type: journal
  authors: Charikar, M. S.
  year: 2002
  title: "Similarity estimation techniques from rounding algorithms"
  venue: Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02)
  pages_or_artno: 380-388
- doi: 10.1145/324133.324140
  type: journal
  authors: Kleinberg, J. M.
  year: 1999
  title: "Authoritative sources in a hyperlinked environment"
  venue: Journal of the ACM
  vol: 46
  issue: 5
  pages_or_artno: 604-632
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: Levy, O., Goldberg, Y., & Dagan, I.
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
new_dois: []
---

## CORE

【构念与来源】
本家族测度一家银行在给定年份, 其被媒体所呈现的战略叙事与国家金融科技宏观政策之间的词面贴合程度, 学术上称为权威政策战略响应度 (authoritative policy strategic responsiveness)。构念的直觉是: 若一家银行当年的新闻语料在具体用词层面与国家权威政策文本高度重合, 则说明该行的战略步调与国家政策导向跟得更紧。本家族聚焦于其中的词级 TF-IDF 通道, 并且是该通道的全年份静态锚点稳健孪生轨 (后缀 `_allv`)。数据来源有二: 一是银行侧的年度聚合新闻文本, 由上游 stage 14 物化的三轨文本列 (content_full / content_ctx / content_ss) 按 (target_bank, year) 聚合而成, 相当于把一家银行一整年碎片化的新闻拼成一份长篇的年度战略画像; 二是宏观侧的权威政策语料, 由 policy_alignment 模块加载并做对称归一化 (与新闻侧同规则, 领导人姓名等做简繁体现而非删除), 保证微观画像与宏观基准落在同构的特征空间内。

【方法学与计算】
计算范式严格遵循先聚合后向量化 (Pool-then-Vectorize): 先把单家银行一年的全部新闻碎片汇总, 消除文章级的特质性白噪音, 再送入向量化器。核心算法采用幽灵锚点 (Ghost Anchor) 技巧: 将政策锚点文本作为第 (N+1) 个元素挂载到当年 N 家银行文本列表末尾, 一并送入与战略差异化模块 (strategic_diff) 绝对同构的 TF-IDF 矩阵提取器, 取对称相似度矩阵最后一列即得各银行相对该锚点的余弦相似度。这保证政策文本被当成一个虚拟的幽灵银行, 与所有真实银行走一模一样的字典、同样的分词、同样的加权规则, 比对绝对公平。本家族的词级 (word) 通道使用 jieba 分词器切词, 与字符级 (char_wb 二至四元 n-gram) 通道形成两种粒度的稳健性对照; 向量化参数为 max_features=5000、min_df=1、max_df=0.95、sublinear_tf=True (对数化词频压制极端高频), 当 max_df 过滤后词表清空时优雅降级为 max_df=1.0。最终度量为两向量的余弦相似度, 取值落在 [0,1], 越高代表词面步调越贴合。

【锚点口径与 allv 语义】
主轨采用 vintage-aware 锚点: 年度 t 的标准答案只拼接发布年份 ≤ t 的政策文档, 消除拿尚未发布的政策当标答的前视构造问题。本家族的 `_allv` 后缀则是全年份静态锚点稳健孪生: 在 vintage 主轨之外, 再用全部年份 (含晚于 t 的未来政策) 拼成的静态标答并列算一套完全同结构的指标, 作为锚点稳健性对照 (anchor-robustness), 绝不替换 vintage 主轨。当某年 vintage 锚点恰好已含全部政策文档 (晚年语料) 或 vintage 退化时, allv 与主轨字节等价, 引擎会短路复用主轨副本免重算, 保持确定性与 golden 安全。因此 `_allv` 与无后缀的 vintage 主轨互为稳健性、不分主次, 二者各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

【文献定位】
本测度承接文本相似度度量文献的方法学脉络。词级 TF-IDF 余弦是稀疏词袋相似度的经典范式, 相似度估计与向量近似的算法基础见 Charikar (2002)。词级 TF-IDF 稀疏词袋作为分布式相似度度量的基线, 其超参数选择 (词频加权、上下文口径、归一化) 对相似度读数的系统性影响已由 Levy, Goldberg 与 Dagan (2015) 系统刻画, 他们证明这类分布式相似度度量的表现高度依赖于设计选择而非仅取决于模型族, 直接支撑本家族对 sublinear_tf、max_df、词表规模等参数做同构冻结以保证跨轨可比。将文本相似度用于刻画企业与政府之间的对齐并进而定价, 在中国情境的最贴近先例是 Liu, Cao 与 Wen (2024), 他们以企业与政府文本的余弦对齐构造度量并检验其资产定价含义, 与本家族政策贴合度的经济学动机同源。近年文献同时对余弦相似度的可解释性与适用边界提出警示: Steck, Ekanadham 与 Kallus (2024) 指出嵌入余弦并不总等价于人类语义相似, You (2025) 进一步刻画余弦在何种几何条件下失效, Opitz 等 (2025) 则系统综述了文本相似度的可解释表示。这些工作提醒: 本家族的词级 TF-IDF 通道刻意保留在稀疏词面层, 与嵌入通道 (auth_sim_emb 及其 co-primary `_lg` 孪生) 构成互补的多测度稳健性梯子, 而非彼此替代。此外, authoritative 一词在信息检索中指向权威性排序 (Kleinberg, 1999), 本处借其权威锚点之意刻画国家政策文本作为战略基准的地位。

## VAR: auth_sim_tfidf_w_allv_full

【变体差分】
本列是词级 TF-IDF 权威政策相似度全年份静态锚点稳健孪生的 full 轨。full 轨的银行年度聚合文本来源于 content_full, 即标题 prepend 后拼接全文正文, 是三轨中信息量最完整、语料覆盖最广的一轨, 因而也是本家族在下游回归中最常作为首要读数的轨道。与家族其他两轨相比, full 轨不施加任何实体窗口或同句共现的裁剪, 银行一整年所有被判定为相关的报道全文均参与聚合与向量化, 分母口径与留篇门控保持 full-only 一致 (2026-06-29 口径: 是否判为一篇银行金科报道只看 full 轨的 LLM 留篇结果, ctx/ss 降为 conditional-on-full 的稳健性轨)。该列与无后缀 vintage 主轨的唯一差别在于锚点: 本列用全部年份政策文档拼成的静态标答 (含未来政策), 主轨用发布年份 ≤ t 的 vintage 锚点。两者各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。full 轨与 ctx、ss 两轨亦属规格稳健性并排, 同样禁混同一 over-identified Hansen J。当 max_df=0.95 过滤后词表清空时, 向量化器优雅降级为 max_df=1.0, 该列仍照常出值。就构念区分而言, full 轨的词级 TF-IDF 与同轨的字符级 (auth_sim_tfidf_c_allv_full)、LDA 主题 (auth_sim_lda_allv_full)、嵌入 (auth_sim_emb_allv_full 及其 co-primary `_lg` 孪生) 通道刻意各自成列, 分别刻画词面重合、字面重合、主题分布贴合与语义空间贴合四个正交侧面, 互为稳健性梯子而非可加分解, 同样禁混进同一 over-identified Hansen J。读该列时越高代表该行当年新闻在词面用语上与国家政策 (全年份静态锚点口径) 步调越紧密。

## VAR: auth_sim_tfidf_w_allv_ctx

【变体差分】
本列是词级 TF-IDF 权威政策相似度全年份静态锚点稳健孪生的 ctx 轨。ctx 轨的银行年度聚合文本来源于 content_ctx, 即标题 prepend 后拼接实体上下文窗口内的文本 (银行实体邻近窗口), 相较 full 轨更聚焦于与目标银行直接相关的片段, 剔除了远离实体的背景叙述, 因而在语料噪音与主题集中度上与 full 轨形成互补。作为 conditional-on-full 的稳健性轨, ctx 轨的行宇宙是 full 留篇集的子集, 其 per-track 相似度列在该子集上独立计算。本列与无后缀 vintage 主轨的差别同样只在锚点 (全年份静态 vs 发布年份 ≤ t 的 vintage), 二者各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; ctx 与 full、ss 三轨亦属规格稳健性并排, 禁混同一 over-identified Hansen J。词级向量化参数 (jieba 分词、max_features=5000、min_df=1、max_df=0.95、sublinear_tf=True) 与家族其余轨完全同构, 唯输入文本轨道不同。ctx 轨在开发期 T=2 小样本上可能出现零方差退化, 属预期现象, 生产 T=19 语料下恢复正常判别力。相较 full 轨, ctx 轨把语料收窄到银行实体邻近窗口, 因而当报道大段背景与目标银行战略无直接关联时, ctx 读数更能反映银行自身叙事的政策贴合度, 而 full 读数会被背景语料稀释, 二者的差值本身即承载信息。ctx 轨与同轨的字符级、LDA、嵌入通道亦各自成列、互为稳健性、禁混同一 over-identified Hansen J。该列的全年份静态锚点身份意味着其对政策语料时序切分不敏感, 与 vintage 主轨对读可诊断前视构造对相似度读数的影响幅度。

## VAR: auth_sim_tfidf_w_allv_ss

【变体差分】
本列是词级 TF-IDF 权威政策相似度全年份静态锚点稳健孪生的 ss 轨。ss 轨的银行年度聚合文本来源于 content_ss, 即标题 prepend 后拼接银行与金融科技词同句共现窗口 (±N 句, 默认半径 1) 内的文本, 是三轨中裁剪最严、语义定位最精确的一轨, 只保留银行与金科概念真正同句邻近出现的语料。其回退语义严格镜像 ctx: 当某银行某年不存在银行∧金科同句共现时, content_ss 回退为全文 body, 并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; 若上游金科 AC 自动机为空则优雅降级。作为 conditional-on-full 的稳健性轨, ss 轨行宇宙同为 full 留篇集子集。本列与无后缀 vintage 主轨仅锚点不同 (全年份静态 vs vintage ≤ t), 二者各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; ss 与 full、ctx 三轨属规格稳健性并排, 禁混同一 over-identified Hansen J。当上游 content_ss 缺失时, 引擎退回 full/ctx 两路而不产 `_ss` 指标列, 属优雅跳过。ss 轨在开发期 T=2 上易出现零方差退化, 属预期, 生产语料下正常。ss 轨的同句共现裁剪口径 (银行侧否定加短名过滤, 金科侧裸自动机匹配) 与 stage 13 上游共现硬过滤属两个不同键、不同判据, 不可互相复用。作为三轨中定位最精确的一轨, ss 读数最能排除银行与金科概念仅在同一篇报道遥远段落各自出现的伪共现, 因而在刻画战略层面真实的政策贴合时噪音最低, 但代价是回退比例较高时样本有效信息缩水。ss 轨与同轨的字符级、LDA、嵌入通道各自成列、互为稳健性、禁混同一 over-identified Hansen J, 全年份静态锚点身份同样使其可与 vintage 主轨对读诊断前视构造的敏感性。

<!-- rendered-citations:begin -->
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint] [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Charikar, M. S. (2002). Similarity estimation techniques from rounding algorithms. Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02), 380-388. https://doi.org/10.1145/509907.509965
Kleinberg, J. M. (1999). Authoritative sources in a hyperlinked environment. Journal of the ACM, 46(5), 604-632. https://doi.org/10.1145/324133.324140
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
<!-- rendered-citations:end -->
