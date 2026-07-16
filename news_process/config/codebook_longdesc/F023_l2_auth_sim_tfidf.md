---
family_id: F023
columns:
- auth_sim_tfidf_w_ctx
- auth_sim_tfidf_w_full
- auth_sim_tfidf_w_ss
unit: 余弦相似度 (无量纲, 取值域 [0,1])
formula: "auth_sim_tfidf_w = cosine( TFIDF_word(bank_year_text), TFIDF_word(vintage_policy_anchor) ); TF-IDF 参数 jieba 词级分词 · max_features=5000 · min_df=1 · max_df=0.95 · sublinear_tf=True; vintage 锚点 = 发布年份 ≤ t 的政策文档拼接; 幽灵锚点作 (N+1) 元素取对称矩阵末列"
producer: news_process/pipeline/features/policy_similarity.py::compute_authoritative_similarity ; news_process/pipeline/features/strategic_diff.py::_build_tfidf_sim_matrix (mode='word')
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- config 政策语料库 (权威政策文档 + 发布年份 vintage 切分)
- 40_panel_yearly.parquet (target_bank × year 骨架)
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
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: Levy, O., Goldberg, Y., & Dagan, I.
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
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
- doi: "10.1016/j.econmod.2025.107121"
  title: "Monetary policy analysis using natural language processing: Evaluating the People's Bank of China's minutes and report summary with the Taylor Rule"
  authors: "Su, S., Ahmad, A. H., Wood, J., & Jia, S."
  year: 2025
  venue: "Economic Modelling, 149, 107121"
  type: "journal"
new_dois:
  - "10.1016/j.econmod.2025.107121"
---

## CORE

【构念与来源】
本家族测度一家目标银行在给定年度的新闻文本, 与国家权威金融科技政策文本之间的词级 TF-IDF 余弦贴合度, 命名前缀 auth_sim_tfidf_w, 意为 authoritative-similarity, TF-IDF, word-level。构念的经济学含义是"战略响应度": 分数越高, 说明这家银行当年被媒体报道所刻画的战略方向与叙事重心, 与截至当年已发布的宏观政策口径越同步。该构念承接文本化宏观暴露度的研究范式, 把碎片化的企业年度披露先聚合成一份"银行年度总结", 再把权威政策文本注入同一个特征空间, 度量微观画像与宏观基准的收敛程度; 这一"先聚合后向量化"的思路与政企文本对齐的既有实证一脉相承。Liu, Cao, Wen (2024) 在中国情境下直接构造企业与政府文本的余弦相似度并证明其对资产定价有解释力, 是本家族最贴近的先例; 本家族把该思路从企业年报迁移到银行的媒体报道语料, 并以幽灵锚点法保证银行侧与政策侧走完全同构的向量化流程。

【方法学与计算】
计算分四步。第一步文本聚合: 把目标银行一整年的全部相关新闻碎片按轨道拼接成一份长文档, 消除文章级的特质性白噪音, 得到 Firm-Year 级的结构化画像。第二步锚点构造: 把权威政策语料按发布年份 (vintage) 切分, 年度 t 的"标准答案"只拼接发布年份 ≤ t 的政策文件, 这一前视守卫消除"用尚未出台的政策当标答"的构造偏误; 无 ≤ t 政策文档的早年份 (前视守卫年份) 该指标置 NaN。第三步幽灵锚点比对: 把政策标答文本当作第 (N+1) 个虚拟"幽灵银行"挂到银行文本列表末尾, 送入与战略差异模块绝对同构的 TF-IDF 矩阵提取器, 取对称余弦矩阵最后一列即各银行相对该锚点的相似度。第四步汇总挂载至 target_bank × year 面板。本家族专指其中的词级 (word) 变体: 向量化器采用 jieba 词级分词器 (token_pattern=None, 领域复合词如"金融科技""区块链"整词保留), 参数 max_features=5000 控制词表规模, min_df=1 保留所有出现过的词以防小样本清空词表, max_df=0.95 排除出现在 95% 以上文档的超高频停用性词 (词表被清空时降级为 max_df=1.0 不过滤), sublinear_tf=True 以 log(1+tf) 抑制词频极端值, 最终取 TF-IDF 向量的余弦相似度, 取值域 [0,1]。词级 TF-IDF 属稀疏词袋测度, 依赖分词质量但语义粒度高于字符 n-gram; 它与同模块的字符级 auth_sim_tfidf_c (char_wb 2-4 gram, 不依赖分词)、主题级 auth_sim_lda (LDA-JSD)、以及 co-primary 嵌入级 auth_sim_emb / auth_sim_emb_lg 是四条并行的相似度测度轨, 各自捕捉不同的语义层次, 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。此外家族在 vintage 主轨之外并列产出全年份静态锚点的 _allv 稳健孪生 (含未来政策文本, 仅作 anchor-robustness 对照, 绝不替换 vintage 主轨), 三个 _w 主列不带 _allv 后缀。

【文献定位】
词级 TF-IDF 余弦是分布式语义假设的稀疏经典实现, 其有效性根植于以词共现刻画语义相近的思想; Levy, Goldberg, Dagan (2015) 系统比较词袋加权与稠密嵌入后指出, 恰当的加权与归一化 (与本家族 sublinear_tf、余弦归一同源) 能让计数型表示逼近嵌入的相似度判别力, 为本家族保留 TF-IDF 稀疏轨提供了方法论辩护。相似度测度本身存在几何陷阱: Steck, Ekanadham, Kallus (2024) 与 You (2025) 分别从嵌入的正则化不变性与角度语义漂移两个角度警示, 余弦相似度的数值在某些表示空间下会脱离"语义相近"的直觉; 本家族以词级 TF-IDF、字符级 TF-IDF、LDA、嵌入四轨并行, 正是把这一警示转化为多测度交叉验证的设计原则, 而非依赖任一单轨。在测度设计层面, Mainali et al. (2022) 论证共现型相似度指数须校正样本规模与边际频率的机械成分, 提醒读者本家族的年度聚合语料长度差异可能带来水平不可比、须以标准化系数而非原始相似度水平作跨行比较。相似度估计的可扩展性有其算法史: Charikar (2002) 的 SimHash 舍入技术奠定了从随机投影角度逼近余弦相似度的经典路径, 是理解相似度测度计算复杂度权衡的基石; 而 Opitz et al. (2025) 的可解释文本相似度综述则勾勒了从稀疏词袋到可解释嵌入的方法谱系, 为本家族在四轨中定位词级 TF-IDF 的可解释性优势 (每一维直接对应可读词项) 提供了坐标。最后, 三轨与四测度构成的规格空间须以规格曲线的纪律呈现: Simonsohn, Simmons, Nelson (2020) 主张把合理的分析自由度全部物化并联合报告, 本家族的三轨 × 四测度 × vintage/_allv 锚点的并排即遵循这一披露原则, 避免择优汇报。该文以词向量余弦相似度量化中国人民银行政策文本随时间的语义贴合与演变, 为本家族的 vintage 政策锚点余弦相似度构造提供了中国央行语境下的方法论近邻, 引用格式 Su, Ahmad, Wood, & Jia (2025, Economic Modelling)。

## VAR: auth_sim_tfidf_w_full

【变体差分】
本列是词级权威政策相似度的 full 轨变体, 轨道后缀 _full 指聚合语料取自 content_full, 即标题 prepend 后拼接全文正文的完整文本。full 轨是三轨中的基准轨: 依据 2026-06-29 的 full-only 留篇门控口径, 一篇报道是否被判为"银行金科报道"仅由 full 轨的 LLM 判定决定, 因此 full 轨聚合的是留篇集内每家银行当年全部报道正文, 语料覆盖最完整、词表最厚、相似度水平的统计功效最高。相对同家族 ctx 与 ss 两轨, 本列不做实体窗口或同句共现的文本裁剪, 因而更能刻画银行整体叙事与政策口径的宏观贴合度, 但也最易被与金融科技无关的高频行业套话稀释信号。在计算上本列与 ctx/ss 走完全一致的 jieba 词级 TF-IDF 流程 (max_features=5000, min_df=1, max_df=0.95, sublinear_tf=True) 与同一 vintage 幽灵锚点, 唯一差别是输入文本轨道。full/ctx/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 本列作为最完整语料轨通常承担首要测度角色, ctx/ss 作 conditional-on-full 的稳健性对照。生产 T=19 语料下三轨均正常出值; 开发 T=2 语料因样本单薄, 词级词表稀疏、相似度水平不宜作实质解读。使用本列时须注意两点口径: 一是 full 轨语料最厚, 其相似度水平天然高于 ctx/ss 两轨, 跨轨比较应比标准化系数而非原始相似度水平; 二是本列与同轨的字符级 auth_sim_tfidf_c_full、主题级 auth_sim_lda_full、嵌入级 auth_sim_emb_full 是四条并行测度, 本列的词级优势在于每一 TF-IDF 维直接对应一个可读词项, 可解释性高于稠密嵌入轨, 便于事后审计哪些政策关键词驱动了贴合度。

## VAR: auth_sim_tfidf_w_ctx

【变体差分】
本列是词级权威政策相似度的 ctx 轨变体, 轨道后缀 _ctx 指聚合语料取自 content_ctx, 即标题 prepend 后仅保留实体上下文窗口的文本 (银行/金科实体附近的句子窗, 剔除远离实体的段落)。相对 full 轨, ctx 轨通过实体窗口裁剪剥离与目标实体无关的行业套话与背景叙事, 使 TF-IDF 词表更聚焦于银行在具体金融科技语境中的用词, 因而理论上能降低无关高频词对余弦相似度的稀释, 是 full 轨的语义聚焦型稳健性轨。计算流程与 full/ss 逐字节同构: 同一 jieba 词级分词、同一 max_features=5000 / min_df=1 / max_df=0.95 / sublinear_tf=True 参数、同一 vintage 幽灵锚点法, 唯一差别是输入文本的轨道来源。ctx 轨在留篇门控上降为 conditional-on-full 测度, 其行宇宙是 full 轨留篇集的子集, 但 per-track 的 ctx 相似度列照常逐轨独立计算, 分母与聚合口径严格取 ctx 轨自身语料, 绝不借用 full 轨分母。full/ctx/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。开发 T=2 语料上实体窗口裁剪后文本更短, 词表进一步稀疏, 该轨相似度水平退化属预期, 生产 T=19 正常。须强调 _ctx 轨道后缀刻画的是文本裁剪口径, 与 vintage/_allv 锚点后缀 (锚点时间构造) 属正交维度: 本列是 vintage 主轨的 ctx 变体, 家族另有全年份静态锚点的 auth_sim_tfidf_w_allv_ctx 稳健孪生并列, 二者仅锚点不同、下游构造完全一致。ctx 轨的设计意图是回答"当只看银行与实体紧邻的语境时, 政策贴合度是否稳健", 因此它承担 full 轨的语义聚焦型稳健性角色, 而非独立的处理变量。

## VAR: auth_sim_tfidf_w_ss

【变体差分】
本列是词级权威政策相似度的 ss 轨变体, 轨道后缀 _ss 指聚合语料取自 content_ss, 即标题 prepend 后仅保留"银行与金融科技词同句共现窗 ±N 句"的最窄文本 (N 由 filtering 配置的 ss_sentence_radius 决定, 默认 1)。ss 轨是三轨中语义最严苛的一轨: 只有目标银行与金融科技概念在同一句 (及邻近窗) 内共现的片段才进入聚合语料, 因而最贴近"银行确实在谈金融科技"的核心叙事, 相似度信号最纯、但语料最稀疏。关键的回退语义须与 CLAUDE.md 口径严格一致: ss 轨镜像 ctx 轨的降级行为, 当某银行某年无银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True 并与其它轨共享 n_articles 分母; 当上游金科 AC 自动机为空导致无法判定共现时优雅全回退。计算上本列与 full/ctx 走完全同构的 jieba 词级 TF-IDF 流程与同一 vintage 幽灵锚点, 唯输入轨道不同; content_ss 整体缺失时该模块退回 full/ctx 两路, 不产 _ss 指标列。full/ctx/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。开发 T=2 语料上同句共现片段极少, ss 轨大量回退、相似度水平几乎不可实质解读, 生产 T=19 语料正常。使用本列须特别警惕回退比例: 当 ss_is_fallback 大面积为真时, ss 轨语料实际退化为 full 轨全文, 此时 auth_sim_tfidf_w_ss 会趋近 auth_sim_tfidf_w_full 而丧失区分度, 因此实证中应结合回退标记评估该轨的有效样本, 而非直接以其相似度水平下结论。作为语义最严苛的一轨, ss 轨在信号纯度与样本损耗之间取最激进的权衡, 与 full (最完整)、ctx (居中聚焦) 构成一条从宽到窄的语义收窄梯子, 三轨联合报告即可展现主结论对文本裁剪口径的稳健性。

<!-- rendered-citations:begin -->
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), eabj9204. https://doi.org/10.1126/sciadv.abj9204
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
Charikar, M. S. (2002). Similarity estimation techniques from rounding algorithms. Proceedings of the Thirty-Fourth Annual ACM Symposium on Theory of Computing (STOC '02), 380-388. https://doi.org/10.1145/509907.509965
Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. Nature Human Behaviour, 4(11), 1208-1214. https://doi.org/10.1038/s41562-020-0912-z
Su, S., Ahmad, A. H., Wood, J., & Jia, S. (2025). Monetary policy analysis using natural language processing: Evaluating the People's Bank of China's minutes and report summary with the Taylor Rule. Economic Modelling, 149, 107121. https://doi.org/10.1016/j.econmod.2025.107121
<!-- rendered-citations:end -->
