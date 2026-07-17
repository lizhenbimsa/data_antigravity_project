---
family_id: F020
columns:
- auth_sim_tfidf_c_allv_ctx
- auth_sim_tfidf_c_allv_full
- auth_sim_tfidf_c_allv_ss
unit: 余弦相似度 (无量纲, 取值域 [0,1])
formula: "auth_sim_tfidf_c_allv{track} = cosine( TFIDF_charwb(2,4)(银行年度聚合文本_i), TFIDF_charwb(2,4)(全年份静态政策锚点) ); 幽灵锚点取对称相似度矩阵末列 sim[:-1,-1]"
producer: news_process/pipeline/features/policy_similarity.py::_ghost_anchor_metrics
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 政策权威语料库 (load_policy_corpus_docs, 全年份静态锚点)
citations:
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.18653/v1/2025.emnlp-main.1135
  type: journal
  authors: Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S.
  year: 2025
  title: "Interpretable text embeddings and text similarity explanation: A survey"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 22314-22330
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: You, K.
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
- doi: 10.1145/509907.509965
  type: journal
  authors: Charikar, M. S.
  year: 2002
  title: "Similarity estimation techniques from rounding algorithms"
  venue: Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02)
  pages_or_artno: 380-388
- doi: 10.1038/s41562-020-0912-z
  type: journal
  authors: Simonsohn, U., Simmons, J. P., & Nelson, L. D.
  year: 2020
  title: "Specification curve analysis"
  venue: Nature Human Behaviour
  vol: 4
  issue: 11
  pages_or_artno: 1208-1214
- doi: 10.1371/journal.pcbi.1003285
  type: journal
  authors: Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E.
  year: 2013
  title: "Ten simple rules for reproducible computational research"
  venue: PLoS Computational Biology
  vol: 9
  issue: 10
  pages_or_artno: e1003285
new_dois: []
---

## CORE

【构念与来源】
本家族测度一家银行在给定年份的战略话语与国家金融科技权威政策文本之间的字符级词形贴合度, 是"银行战略步调—国家政策基准"收敛性构念在字符 TF-IDF 空间中的具体落地。构念动机源自政企文本对齐这一新兴测量传统: Liu, Y., Cao, Z., & Wen, F. (2024) 在中国情境下以企业披露与政府文件之间的文本余弦相似度刻画二者话语趋同, 并证明该对齐度具有资产定价含义; 本家族沿用同一"把宏观权威文本注入与微观主体同构的向量空间再测收敛"的思路, 但把测量对象换成银行年度新闻画像相对国家金融科技政策的贴合。所谓权威政策相似度, 直觉上回答的是"这家银行这一年在公开话语层面, 与截至该年国家已表态的金融科技政策方向, 措辞和主题跟得有多紧"。分数越高, 表示银行战略叙事与政策基准的字面重合越强。

【方法学与计算】
计算分四步。第一步文本聚合: 把单家银行一年内的全部新闻碎片拼成一份长篇的"银行年度战略画像", 以消除文章级特质白噪音, 使测度落在 firm-year 粒度。第二步锚点构造: 把国家重磅政策文件构成权威语料库, 拼成"标准答案"锚点。第三步幽灵锚点比对: 将锚点文本作为第 N+1 个元素挂到当年银行文本列表末尾, 送入与战略趋同模块 (strategic_diff) 绝对同构的 TF-IDF 矩阵提取器, 取对称相似度矩阵的最后一列 sim[:-1, -1], 即得各银行相对该锚点的相似度, 保证幽灵银行与真实银行走完全一致的字典、分段与池化标准, 杜绝口径不公。第四步余弦度量: 本家族的 tfidf_c 分支采用字符级 char_wb 二到四元 n-gram 向量器 (analyzer='char_wb', ngram_range=(2,4)), 对拼接文本抽取字符 n-gram 权重向量后取余弦。字符级向量器不依赖分词质量, 对未登录金融科技新词、领域复合词与错分词稳健, 这与词级 tfidf_w 稳健性轨形成刻意的方法学互补 (词级依赖 jieba 分词, 领域复合词整体保留)。Charikar, M. S. (2002) 关于基于舍入的相似度估计的经典工作阐明了此类高维稀疏 TF-IDF 表示上余弦相似度的几何与可估计性基础, 为在字符 n-gram 权重向量上以余弦度量银行文本与政策锚点的贴合度提供了估计学依据。需澄清本家族的权威性并非来自任何图结构或链接分析意义上的权威节点算法, 而纯粹是构造意义上的: 政策锚点被当作外生给定的国家权威文本基准, 银行年度画像相对该固定锚点的余弦即贴合度, 权威锚点由政策语料库直接指定而非从结构中提取, 这一点须与超链接权威度一类结构性算法明确区分, 避免概念混淆。

【文献定位】
本家族在相似度测量的方法学谱系中处于"字符级词形对齐"一端。近期文献反复提示余弦相似度并非在所有表示上都等价于语义相似: Steck, H., Ekanadham, C., & Kallus, N. (2024) 指出嵌入余弦可能受正则化与自由度影响而与真实相似度脱钩, You, K. (2025) 进一步刻画了余弦相似度"可用直到失效"的边界, Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025) 系统综述了可解释文本相似度的方法与陷阱。本家族对这些警示的回应是: 字符 TF-IDF 余弦是可解释、可复现的词形对齐测度, 语义解释力弱于嵌入但透明度高, 因而定位为与 LDA 主题轨、Qwen/large 嵌入轨互为稳健性、不分主次的并排测度, 而非唯一权威测度。整个 auth_sim 指标族 (tfidf_c / tfidf_w / lda / emb / emb_lg) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同方法轨或不同文本轨的相似度混进同一 over-identified Hansen J 过度识别检验。方法学复现性遵循 Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013) 的可复现计算研究规范: 同锚点、同输入在确定性向量器下产同值, 是本模块 golden 安全的前提。

本家族三列全部带 _allv 后缀, 即全年份静态锚点孪生。生产主轨 auth_sim_tfidf_c (无 _allv) 采用 vintage-aware 锚点: 年度 t 的标准答案只拼接发布年份 ≤ t 的政策文件, 消除"拿尚未出台的政策当标答"的前视构造。本家族的 _allv 孪生则用全部年份 (含未来年份) 政策文档拼成的静态锚点再算一遍完全同结构的相似度, 作为锚点选择的稳健性对照。二者的关系是: vintage 主轨规避前视偏误、是因果推断的首选; _allv 孪生检验主结论是否对"是否纳入未来政策文本"这一锚点构造选择敏感。当晚年份 vintage 锚点已含全部政策文档、或 vintage 退化时, _allv 与主轨字节等同, 引擎短路复用副本免重算 (golden 安全)。_allv 与 vintage 是锚点稳健性的两条并排轨, 各自 just-identified, 同样禁混进同一 over-identified Hansen J。Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020) 的规格曲线分析框架正是本类锚点/方法/文本轨并排稳健性梯子的方法论依据: 主结论应在合理的构造选择集合上稳健, 而非由单一锚点驱动。

【三轨与留篇口径】
本家族三列对应 full / ctx / ss 三条文本轨。三轨聚合的原始文本分别来自 stage 14 物化的 content_full (标题 prepend + 全文正文)、content_ctx (标题 + 银行实体上下文窗口)、content_ss (标题 + 银行与金科同句共现窗)。ss 轨在无银行∧金科同句共现时优雅回退为全文正文, 镜像 ctx 轨的回退语义; content_ss 整体缺失时该模块退回 full/ctx 两路、不产 _ss 指标列。三轨同为规格稳健性并排轨、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道由 full 轨判定, ctx/ss 为 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集。

## VAR: auth_sim_tfidf_c_allv_ctx

【变体差分】
本列是全年份静态锚点 (_allv) 孪生在 ctx 文本轨上的字符级 TF-IDF 权威政策相似度。相对家族 canonical 的 vintage 主轨 auth_sim_tfidf_c (无 _allv、full 轨), 本列在两个维度上差分: 其一是锚点维度, 采用全年份 (含发布年份 > t 的未来政策文本) 静态锚点, 而非只用 ≤ t 政策的 vintage 锚点, 因此本列刻意允许前视信息进入锚点, 定位为锚点选择的稳健性对照轨, 绝不替换规避前视偏误的 vintage 主轨。其二是文本轨维度, 聚合文本取 content_ctx (标题 prepend + 银行实体上下文窗口), 相较 full 轨的全文正文, ctx 轨聚焦银行实体邻近语境、剔除远离实体的无关段落, 是 conditional-on-full 的稳健性轨。方法内核仍是字符级 char_wb 二到四元 n-gram 向量器上的余弦, 与词级 tfidf_w、LDA、嵌入轨互为稳健性、不分主次。锚点轨 (_allv vs vintage)、文本轨 (full/ctx/ss)、方法轨三个维度各自 just-identified 并排, 本列与它们中任意一条均严禁混进同一 over-identified Hansen J 过度识别检验。取值域 [0,1], 越高表示 ctx 语境下银行战略话语与全年份政策锚点的字形贴合越强。使用本列的典型场景是: 在以 vintage 主轨 full 列为基准得到主结论后, 把本列作为"锚点换成全年份且文本轨换成实体窗"的双重稳健性替代进入并排规格, 若系数方向与显著性稳定, 则说明主结论既不被前视政策锚点驱动、也不被全文噪声段落驱动。反之, 若本列结果与 vintage full 列显著背离, 应视为对锚点构造或语境窗选择敏感的信号, 需在稳健性叙事中如实披露而非择优汇报。需强调本列相对 vintage 主轨仅在稳健性维度提供信息, 不参与因果识别的首选设定。

## VAR: auth_sim_tfidf_c_allv_full

【变体差分】
本列是全年份静态锚点 (_allv) 孪生在 full 文本轨上的字符级 TF-IDF 权威政策相似度, 是本 _allv 家族中最贴近家族 canonical 语义的一列。它与 vintage 主轨 auth_sim_tfidf_c (full 轨) 唯一的差分在锚点维度: 本列用全部年份政策文档 (含未来年份) 拼成的静态锚点, vintage 主轨则只用发布年份 ≤ t 的政策文档。因此本列的经济含义是"若把尚未出台的政策也纳入标准答案, 银行 full 轨战略话语的贴合度会怎样", 用于检验主结论是否对是否引入前视政策文本这一锚点构造选择敏感。当某年 vintage 锚点已含全部政策文档 (晚年份) 或 vintage 机制退化时, 本列与 vintage 主轨字节等同, 引擎短路复用免重算, 属预期确定性行为而非缺陷。文本轨为 content_full (标题 prepend + 全文正文), 是留篇门控 (full-only, 2026-06-29) 与整个三轨体系的基准轨; 本列的行宇宙即 full 留篇集。方法内核为字符级 char_wb 二到四元 n-gram 余弦, 对分词质量与领域新词稳健, 与词级、LDA、嵌入轨互为稳健性、不分主次。_allv 与 vintage 两锚点轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。取值域 [0,1]。由于本列与 vintage full 主轨仅在锚点纳入年份上不同、文本轨完全相同, 它是隔离"前视政策文本"这一单一构造选择影响的最干净对照: 二者之差纯粹归因于锚点是否包含年份 > t 的未来政策, 而不掺杂文本轨切换的混淆。研究者可据此判断相似度水平在多大程度上依赖于回溯纳入后续政策文本; 若晚年份因锚点已收敛而两列趋同, 恰印证 vintage 与全年份口径在样本尾端自然弥合。本列在整个 auth_sim 指标族中是 full 轨、字符方法、全年份锚点三者的交叉点, 应与词级、LDA、Qwen 与 large 嵌入的对应 full 列并读, 以判断字形贴合与语义贴合是否给出一致的政策收敛画像。

## VAR: auth_sim_tfidf_c_allv_ss

【变体差分】
本列是全年份静态锚点 (_allv) 孪生在 ss 文本轨上的字符级 TF-IDF 权威政策相似度。相对家族 canonical, 本列在锚点与文本轨两维差分。锚点维度同 _allv 家族其余列: 采用含未来年份的全年份静态锚点, 是 vintage 主轨的锚点稳健性对照, 不替换主轨。文本轨维度取 content_ss (标题 prepend + 银行与金融科技同句共现窗口 ±N 句), 是三轨中语境最窄、信噪比要求最高的一轨: 只有银行与金科词在同一句邻近共现时才纳入该句上下文。ss 轨采用镜像 ctx 的回退语义 —— 当某银行年内不存在银行∧金科同句共现时, content_ss 优雅回退为全文正文 (ss_is_fallback=True), 与 ctx 共享留篇分母; 若 content_ss 轨整体不可用, 该模块退回 full/ctx 两路、不产本列。因此本列在 T 较小的开发样本上可能因同句共现稀疏而大面积走回退或退化, 属预期行为, 生产全样本 (T=19) 下方能充分体现 ss 轨对紧邻政策语境的聚焦。方法内核为字符级 char_wb 二到四元 n-gram 余弦。ss 轨与 full/ctx 轨、_allv 与 vintage 锚点轨、字符与词级/LDA/嵌入方法轨均各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。取值域 [0,1]。本列的独特价值在于把权威政策相似度收窄到银行与金融科技概念真正同句共现的最紧邻语境: 若一家银行仅在泛泛的整篇报道层面与政策文本贴合、却在银行与金科同句共现的核心句上贴合度骤降, 本列相对 full 与 ctx 列的落差即揭示这种"表层贴合、核心疏离"的结构。因此在稳健性叙事中, ss 轨常被用作最保守的语境界定, 检验主结论是否在最严格的共现口径下依然成立。使用时须结合 ss_is_fallback 比例判读: 回退占比过高时本列实质退化为 full 轨全文口径, 其对紧邻语境的判别力相应减弱, 此时应主要依赖生产全样本而非开发子样本的结果。

<!-- rendered-citations:begin -->
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Charikar, M. S. (2002). Similarity estimation techniques from rounding algorithms. Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02), 380-388. https://doi.org/10.1145/509907.509965
Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. Nature Human Behaviour, 4(11), 1208-1214. https://doi.org/10.1038/s41562-020-0912-z
Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for reproducible computational research. PLoS Computational Biology, 9(10), e1003285. https://doi.org/10.1371/journal.pcbi.1003285
<!-- rendered-citations:end -->
