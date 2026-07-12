---
family_id: F021
columns:
- auth_sim_tfidf_c_ctx
- auth_sim_tfidf_c_full
- auth_sim_tfidf_c_ss
unit: 余弦相似度 (无量纲, 取值区间 [0,1])
formula: "auth_sim_tfidf_c_track = cosine( v_bank_year , v_policy_anchor ); v = TF-IDF(analyzer=char_wb, ngram=(2,4), max_features=5000, min_df=1, max_df=0.95, sublinear_tf=True); v_policy_anchor = vintage ghost-anchor (发布年份 <= t 的权威金科政策语料拼接文本, 挂银行文本列表末列取 sim 末列)"
producer: news_process/pipeline/features/policy_similarity.py::_ghost_anchor_metrics (历史脚本名 26_authoritative_similarity.py, 现无独立 shim, 由 panel runner 调用; 该编号 26 为遗留脚本号, 非 core/dag.py 当前 stage 26 = semantic_staleness) ; 标签兜底 news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (full-only 留篇门控行宇宙)
- 权威金科政策语料 (policy_alignment.load_policy_corpus_docs, vintage 切分)
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
  venue: arXiv
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1126/sciadv.abj9204
  type: journal
  authors: Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F.
  year: 2022
  title: "A better index for analysis of co-occurrence and similarity"
  venue: Science Advances
  vol: 8
  issue: 4
  pages_or_artno: eabj9204
- doi: 10.1002/sim.3107
  type: journal
  authors: Gelman, A.
  year: 2008
  title: "Scaling regression inputs by dividing by two standard deviations"
  venue: Statistics in Medicine
  vol: 27
  issue: 15
  pages_or_artno: 2865-2873
- doi: 10.1145/509907.509965
  type: journal
  authors: Charikar, M. S.
  year: 2002
  title: "Similarity estimation techniques from rounding algorithms"
  venue: Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02)
  pages_or_artno: 380-388
new_dois: []
---

## CORE

【构念与来源】
本家族测度一家银行在给定年度其新闻文本与国家权威金融科技政策语料在字符层面的贴合程度, 即"银行年度战略画像是否与宏观政策基调同频"。构念根植于文本战略定位文献的"先聚合后向量化"范式: 把某银行某年度的全部碎片化报道拼成一份长篇"银行年度总结", 消除文章级的特质性白噪音, 再把它投射到一个可与外部宏观基准直接比对的向量空间。宏观基准来自权威金科政策文本 (由 policy_alignment 语料加载器统一读入、按发布年份切分)。做法上采用"幽灵锚点"技巧: 将政策拼接文本作为第 N+1 个元素挂到当年银行文本列表末尾, 送入与战略差异化 stage 完全同构的 TF-IDF 提取器, 取对称相似度矩阵最后一列即得各银行相对该政策锚点的余弦相似度。这样政策"标准答案"与所有真实银行走一模一样的字典、同样的归一化与同样的 n-gram 切分, 保证比对的绝对公平。分数越高, 说明该银行 (截至当年已发布的) 政策步调贴得越紧。

【方法学与计算】
向量化器为字符级 TF-IDF: analyzer=char_wb, ngram_range=(2,4), max_features=5000, min_df=1, max_df=0.95, sublinear_tf=True。字符 n-gram (char_wb) 的关键优点是不依赖中文分词质量, 对未登录词、缩写、领域复合词天然稳健, 与词级 (jieba tokenizer) 轨互为方法学对照。sublinear_tf 用 log(1+tf) 压制极端词频, max_df=0.95 剔除近乎无差别的超高频片段, min_df=1 则保留所有出现过的片段以防小样本或高差异文本把词表清空。相似度为标准余弦, 取值落在 [0,1]。前视守卫是本测度的构造命门: 年度 t 的政策锚点只拼接发布年份小于等于 t 的政策文档, 严禁"拿还没出生的政策当标准答案"造成的前视污染; 若某年不存在发布年份小于等于 t 的政策文档, 该年主轨锚点为空, 对应值置 NaN。在 vintage 主轨之外还并列产出全年份静态锚点的 auth_sim_tfidf_c_allv 孪生 (含未来政策文本), 仅作 anchor-robustness 对照, 绝不替换 vintage 主轨。行宇宙锚定 full-only 留篇门控 (2026-06-29): 是否算作一家银行金科报道只看 full 轨留篇判定, ctx 与 ss 轨为 conditional-on-full 的稳健性测度。

【文献定位】
以文本相似度刻画"微观主体与宏观基准的收敛性"在金融与会计文本计量中已成熟。Liu, Cao 与 Wen (2024) 直接以企业与政府文本的余弦相似度构造并为其定价, 是与本测度最贴近的中国政企文本对齐先例, 佐证"政策贴合度"可用向量夹角量化并具经济含义。在战略管理主流刊上, Arts, Cassiman 与 Hou (2025) 以企业专利文本的相似度构造"技术差异化"并将其与产品市场竞争、并购交易关联, 顶刊实证印证了 TF-IDF 式文本相似度作为企业战略定位测度的效度与经济后果, 为本家族"以文本相似度刻画银行战略画像"提供直接的构念背书。方法学上须正视余弦相似度并非无条件反映语义相似: Steck, Ekanadham 与 Kallus (2024) 指出嵌入余弦可能被表示的自由度扭曲, You (2025) 进一步刻画"余弦有效直到失效"的边界条件, Opitz 等 (2025) 综述了文本相似度的可解释性视角。字符 n-gram 稀疏向量的余弦相对嵌入余弦更透明 (每一维对应显式字符片段), 在一定程度上规避了上述嵌入特有的病态, 但仍受词表构造与频次加权影响, 故本项目将其与词级、LDA 主题、跨厂商嵌入等多种测度并置为互为稳健性的度量族。Mainali 等 (2022) 关于共现与相似性指数改良、Charikar (2002) 关于相似度估计的经典结果, 为跨测度稳健性叙事提供更广的方法学背景; 回归接入时按 Gelman (2008) 对连续解释变量作标准化以利系数可比。铁律: 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨或不同测度 (tfidf_c/tfidf_w/lda/emb) 混进同一 over-identified 的 Hansen J 过度识别检验。

## VAR: auth_sim_tfidf_c_full

【变体差分】
本列为家族 canonical 轨。full 轨的银行年度总结取自 content_full, 即标题 prepend 后的全文正文聚合 (标题句作为第 0 句并入). 因行宇宙锚定 full-only 留篇门控 (2026-06-29), full 轨的留篇判定同时也是整族三轨的行集依据: 是否算作一家银行金科报道只看 full 轨, ctx 与 ss 轨是 conditional-on-full 的子集测度。本列与另两轨的唯一差别在于喂入 TF-IDF 幽灵锚点比对的文本范围最宽 (全文), 因而字符 n-gram 词表覆盖最完整, 对政策语料中任一措辞片段的召回最高, 相似度水平通常也最高、方差最稳。字符级 char_wb (2,4) 的选择使该值不受中文分词误差影响, 对政策文本特有的机构名、专有缩写、四字政策术语天然稳健。vintage 前视守卫在本轨同样生效: 年度 t 只用发布年份小于等于 t 的政策锚点, 无可用锚点则置 NaN; 全年份静态锚点的稳健孪生落在 _allv 后缀列, 不属本列。铁律: 本轨与 ctx/ss 轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。作为 canonical 轨, 本列是主回归中优先采用的政策贴合度度量, 另两轨提供文本窗口敏感性的稳健性检验。由于全文轨保留了最完整的语料信息, 本列在解释银行战略与政策同步性时信噪比最高, 也最接近文本战略定位文献所强调的"企业年度画像"整体口径; 在与词级、主题级、嵌入级测度并置作跨方法稳健性叙事时, 本列充当字符级度量族的主锚。

## VAR: auth_sim_tfidf_c_ctx

【变体差分】
本列为 ctx 轨稳健性变体。ctx 轨的银行年度总结取自 content_ctx, 即标题 prepend 后仅保留银行实体上下文窗口的文本聚合 — 相对 full 轨剔除了与目标银行无关的段落, 把 TF-IDF 幽灵锚点比对聚焦到银行邻近语境。因此本列相对 canonical full 轨的差别纯在文本范围 (实体窗口 vs 全文): 词表更集中于银行相关措辞, 对政策贴合的度量更"就近"、噪声段落更少, 但覆盖面窄于 full, 在极短上下文时更易出现零方差或稀疏退化。计算内核 (char_wb 2-4 gram、sublinear_tf、max_features=5000、min_df=1、max_df=0.95、vintage 前视守卫、幽灵锚点取末列) 与 full 轨逐字节同构, 唯输入文本轨不同。ctx 为 conditional-on-full 测度: 行宇宙仍由 full 轨留篇门控决定, 本轨只在留篇集内按 ctx 文本另算一遍。若 content_ctx 缺失则本轨优雅跳过、不产列。铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把本列与 full 或 ss 轨混进同一 over-identified Hansen J 过度识别检验; 本列定位为文本窗口敏感性的稳健性轨, 不作主轨替换。其经济解读是: 若把度量收窄到银行实体邻近语境后政策贴合度的结论依然成立, 则主结论不被无关段落的表述所驱动, 从而提高了对全文轨潜在稀释效应的稳健性说服力。生产态多年样本下本轨方差与均值均恢复正常, 与 full 轨呈高相关但非冗余。

## VAR: auth_sim_tfidf_c_ss

【变体差分】
本列为 ss 轨稳健性变体, 是三轨中文本窗口最窄的一路。ss 轨的银行年度总结取自 content_ss, 即银行与金融科技词在同一句 (同句共现窗, 半径由 filtering.yaml 的 ss_sentence_radius 控制) 邻近出现的文本聚合, 把政策贴合度的度量收紧到"银行确实在谈金科"的句子上, 语义针对性最强、无关噪声最低。回退语义严格镜像 ctx: 当某银行某年无银行与金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 与 ctx 的回退口径一致 — 这一点须与 CLAUDE.md 口径完全对齐, 写错即为 P0。因窗口最窄, 本轨在样本浅或共现稀疏时最易出现零方差退化 (开发态 T=2 上尤为常见), 生产态 T=18 恢复正常。计算内核 (char_wb 2-4 gram、sublinear_tf、幽灵锚点、vintage 前视守卫) 与 full/ctx 逐字节同构, 唯输入文本轨为 content_ss。ss 同为 conditional-on-full 测度, 行宇宙由 full 轨留篇门控决定; content_ss 缺失时本轨优雅跳过、不产列。铁律: 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 本列作最严判据下的窗口敏感性稳健轨, 不替换 canonical full 主轨。其价值在于提供三轨中语义针对性最强的一端: 若在"银行确实在同句谈金科"的最严文本判据下政策贴合度结论仍稳健, 则可排除报道中泛泛政策背景句对度量的机械抬升。回退到全文的行须借助 ss_is_fallback 标记与 ctx 共享同一分母口径, 分析时可据该标记评估回退比例对本轨解释力的影响。

<!-- rendered-citations:begin -->
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), eabj9204. https://doi.org/10.1126/sciadv.abj9204
Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine, 27(15), 2865-2873. https://doi.org/10.1002/sim.3107
Charikar, M. S. (2002). Similarity estimation techniques from rounding algorithms. Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02), 380-388. https://doi.org/10.1145/509907.509965
<!-- rendered-citations:end -->
