---
family_id: F018
columns:
- auth_sim_lda_allv_ctx
- auth_sim_lda_allv_full
- auth_sim_lda_allv_ss
unit: 主题分布相似度 (无量纲, [0,1])
formula: "auth_sim_lda_allv = 1 - JSdist(theta_bank, theta_anchor); theta = LDA 主题分布, JSdist = Jensen-Shannon 距离 = sqrt(Jensen-Shannon 散度) (scipy jensenshannon, base=2); anchor = 全年份 (all-vintage) 静态政策锚点 (非 vintage ≤t 主轨)"
producer: news_process/pipeline/features/policy_similarity.py::compute_authoritative_similarity
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 政策语料 (config policy corpus; load_policy_corpus_docs 全年份静态锚点)
citations:
- doi: 10.3389/frai.2026.1752103
  type: journal
  authors: Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J.
  year: 2026
  title: "FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  venue: Frontiers in Artificial Intelligence
  vol: 9
  pages_or_artno: Article 1752103
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
  pages_or_artno: Article 111823
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1145/3657299
  type: journal
  authors: Xia, B., Rawte, V., Gupta, A., & Zaki, M. J.
  year: 2024
  title: "FETILDA: Evaluation framework for effective representations of long financial documents"
  venue: ACM Transactions on Knowledge Discovery from Data
  vol: 18
  issue: 7
  pages_or_artno: 1-27
- doi: 10.1126/sciadv.abj9204
  type: journal
  authors: Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F.
  year: 2022
  title: "A better index for analysis of co-occurrence and similarity"
  venue: Science Advances
  vol: 8
  issue: 4
  pages_or_artno: Article eabj9204
- doi: 10.1038/s41562-020-0912-z
  type: journal
  authors: Simonsohn, U., Simmons, J. P., & Nelson, L. D.
  year: 2020
  title: "Specification curve analysis"
  venue: Nature Human Behaviour
  vol: 4
  issue: 11
  pages_or_artno: 1208-1214
new_dois: []
---

## CORE

【构念与来源】
本家族三列 auth_sim_lda_allv_{full,ctx,ss} 测度的构念是「银行年度战略画像与国家金融科技宏观政策在潜在主题空间上的收敛度」, 也就是一家银行在某一年份, 其被媒体报道所刻画的战略议题分布, 与国家权威政策文本所强调的主题分布究竟有多贴合。测度沿用文本金融学中「先聚合、后向量化」(Pool-then-Vectorize) 的范式: 先把某银行某年度散落在众多新闻碎片里的表述拼成一份长篇「银行年度战略总结」, 以此消除单篇文章级的特质性白噪音, 再把这份总结投射进一个与政策文本同构的主题空间, 计算两者的分布距离。这一范式在企业战略文本定位与宏观政策暴露度测量两条线索上都有稳固先例: 一方面, 把宏观政策文本注入与微观主体共享的向量空间、以主体向量对宏观锚向量的贴合度来刻画暴露度, 是 Hassan 等人测度企业层面政治风险时确立的概念动因; 另一方面, 把企业年度文本聚合成画像再做高维相似度定位, 是 Hoberg 与 Phillips 文本网络产业方法论的核心。近年来, Liu、Cao 与 Wen (2024) 直接在中国情境下把企业文本与政府文本做相似度对齐并考察其定价含义, 与本家族「银行对权威政策的战略响应度」构念最为贴近, 构成本测度在中国政企文本语境下的直接先例。

【方法学与计算】
计算分四步。第一步聚合: 对每个 (target_bank, year) 单元, 把该年该行的全部报道文本拼成一份超长文档 (聚合原语 _aggregate_bank_year_texts, 与战略差异模块共用)。第二步构造锚点: 把国家权威政策语料拼成一份「标准答案」文本, 当作一个虚拟的「幽灵银行」挂到真实银行文本列表末尾, 送入与主测度绝对同构的主题抽取器, 取对称相似度矩阵最后一列即得各真实银行相对锚点的相似度 (幽灵锚点 O(1) 提取, 保证幽灵行与真实行走完全相同的字典与主题模型)。第三步主题相似度: LDA 通道把每份文档表示为潜在主题上的概率分布 theta, 计算银行分布与锚点分布之间的 Jensen-Shannon 距离 (scipy jensenshannon, base=2, 返回值是 Jensen-Shannon 散度的平方根, 而非散度本身), 再以 auth_sim_lda = 1 − Jensen-Shannon 距离折算为相似度, 取值落在 [0,1], 越接近 1 表示两份文档的主题构成越一致。须精确区分: 引擎 sqrt(JSD) 得到的是有界 [0,1] 的 JS 距离 (一个满足度量三角不等式的真距离), 直接以 1 减散度会得到数值不同、且不保证 [0,1] 的量, 故本测度的口径是 1 减 JS 距离而非 1 减散度。第四步汇总挂载: 逐单元逐轨记录后按 (target_bank, year) 合并回面板。本家族是其中的 LDA 主题通道, 与同模块并行的 TF-IDF 字符级 / TF-IDF 词级 / 语义嵌入 (Qwen 主轨与 text-embedding-3-large 的 _lg co-primary 孪生) 各通道是并列的方法学变体, 分别刻画字面重合、词面重合与语义/主题层面的贴合。

【文献定位】
本家族的关键定语是 _allv (all-vintage, 全年份锚点)。生产主轨采用 vintage-aware 口径: 年度 t 的政策锚点只拼接发布年份 ≤ t 的政策文件, 以消除「拿尚未出台的政策当标准答案」的前视 (look-ahead) 构造偏差。而 _allv 孪生刻意反其道: 用「所有年份政策文档」(含发布晚于 t 的未来文本) 拼成一个不随年份变化的静态锚点, 再用完全同构的 LDA-JSD 流程并列算一套 auth_sim_lda_allv 指标。因此 _allv 与 vintage 主轨是「锚点稳健性」(anchor-robustness) 的一对并排臂: 二者唯一差异是锚点文本口径 (静态全年份 vs 逐年 ≤t), 下游主题抽取、聚合、幽灵挂载完全一致。这种以锚点选择做稳健性梯子的做法, 呼应 Simonsohn、Simmons 与 Nelson (2020) 规格曲线分析的精神——把一个本质上属于研究者自由度的构造选择显式物化为并排规格, 用以证明主结论不被单一锚点口径驱动。方法学层面, 主题相似度与近年财务文本主题建模 (Jehnen 等 2026 的 FinTextSim、Xia 等 2024 的 FETILDA 对长财务文档表征的评估) 属同一脉络; 而相似度度量本身的可解释性与陷阱, 由 Opitz 等 (2025) 的相似度解释综述、Steck 等 (2024) 与 You (2025) 对余弦相似度何时失效的辨析、以及 Mainali 等 (2022) 对共现/相似度指数的改进共同界定——这些工作提醒: 相似度数值的可比性依赖于底层表征空间, 故本家族只在同一 LDA 主题空间内、同一锚点口径下横向比较, 不跨通道混用绝对水平。口径铁律: _allv 稳健臂与 vintage 主轨、以及下述 full/ctx/ss 三轨, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同锚点口径或不同文本轨的相似度列混进同一 over-identified Hansen J 过度识别检验。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的战略画像, 由 full 轨的留篇判定决定, ctx/ss 轨为 conditional-on-full 的测度/稳健性轨。ss 轨的回退语义镜像 ctx: 当某银行某年无「银行与金科同句共现」文本时, content_ss 优雅回退为全文正文。已知局限: LDA 主题数与随机种子会影响 JSD 绝对水平, 故本测度只作序内可比、跨规格并排稳健, 不宜跨主题模型超参直接比水平。

## VAR: auth_sim_lda_allv_ctx

【变体差分】
本列是 auth_sim_lda_allv 家族的 ctx 轨实例。它与家族 canonical 语义完全共享【构念与来源】【方法学与计算】所述的「全年份静态锚点 × LDA 主题分布 × Jensen-Shannon 距离 (sqrt(JSD), base=2) 折算相似度」链路, 唯一区别在于输入文本轨: ctx 轨消费 content_ctx, 即「标题 prepend + 实体上下文窗口」文本——只截取围绕目标银行实体附近窗口的正文, 而非全文。因此本列刻画的是「在银行被点名的上下文语境里, 银行战略议题与权威政策主题的贴合度」, 相对 full 轨更聚焦、噪音更低, 但也可能因窗口截断而丢失全文层面的战略语境。按 full-only 门控口径 (2026-06-29), 本 ctx 列是 conditional-on-full 的测度/稳健性轨: 行宇宙是 full 轨留篇集的子集, per-track 相似度照单元计算。本列与同家族 full、ss 两轨, 以及 vintage 主轨对应的 auth_sim_lda_ctx, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混进同一 over-identified Hansen J 过度识别检验。当某单元 ctx 文本缺失或全为回退时, 本列按优雅降级置 NaN, 不借用 full 轨分母。就锚点维度而言, 本列固定采用全年份静态锚点 (_allv), 与之对应的 vintage 逐年锚点臂为 auth_sim_lda_ctx: 两者唯一差异是锚点是否含发布晚于当年的未来政策文本, 构成锚点稳健性的一对并排规格。因此本列在解读上兼具两重非主属性——文本轨取上下文窗、锚点口径取全年份静态——两处都属稳健性对照臂而非生产主轨, 主结论应以 full 轨 vintage 锚点为准, 本列用于验证结论不被上下文窗截取与全年份锚点这两项构造选择所驱动。使用时只在同一 LDA 主题空间、同一锚点口径内做序内比较, 不与 TF-IDF 或嵌入通道横向比绝对水平。

## VAR: auth_sim_lda_allv_full

【变体差分】
本列是 auth_sim_lda_allv 家族的 full 轨实例, 也是本家族的基准文本轨。它消费 content_full, 即「标题 prepend + 全文正文」, 把某银行某年全部报道的完整文本聚合为战略画像, 再与全年份静态政策锚点在 LDA 主题空间上算 1 − Jensen-Shannon 距离 (即 1 − sqrt(JSD), base=2) 相似度。相对 ctx / ss 两轨只取窗口或同句片段, full 轨保留最完整的战略语境, 因而是留篇门控的判定轨: 依 full-only 口径 (2026-06-29), 一篇报道是否计入某银行某年的战略画像由 full 轨留篇判定决定, ctx / ss 轨的行宇宙是 full 留篇集的子集。需要区分的是: 本列的 full 指文本轨 (全文 vs 上下文窗 vs 同句), 而列名中的 _allv 指锚点口径 (全年份静态锚点 vs vintage ≤t 逐年锚点)——两个后缀维度正交, 本列是「全文轨 × 全年份锚点」的组合, 其 vintage 对应臂为 auth_sim_lda_full。本列与家族内 ctx、ss 两轨, 以及 vintage 主轨的 auth_sim_lda_full, 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 过度识别检验。当锚点文本因前视守卫不可用或聚合文本为空时, 本列优雅置 NaN。需强调本列虽以全文轨为文本基准, 但在锚点维度上仍属稳健性对照臂: 它采用全年份静态锚点 (含未来政策文本), 刻意违背 vintage 前视守卫, 用以检验主结论是否对「用后见之明政策当标答」这一构造敏感。真正进入主回归的生产主轨是 vintage 锚点的 auth_sim_lda_full, 本 _allv 列与之并排、互为稳健性、不分主次。解读时应把本列视为「全文轨下, 放松逐年前视约束后」的战略贴合度, 其与 vintage 主轨的一致性越高, 越说明主题相似度的信号不被政策文本的时序切分方式左右; 二者若出现系统性背离, 则提示某些年份的贴合度实由晚出政策文本驱动, 须谨慎解读。

## VAR: auth_sim_lda_allv_ss

【变体差分】
本列是 auth_sim_lda_allv 家族的 ss 轨实例。它与家族 canonical 共享全部计算链路, 唯一区别是输入文本轨: ss 轨消费 content_ss, 即「标题 prepend + 银行与金科同句共现窗 (±N 句, 默认半径 1)」文本——只保留目标银行与金融科技词在同一句 (或极小句窗) 内共现的片段, 是三轨中最严格、最聚焦的语境轨。因此本列刻画的是「在银行与金科被同句提及的最贴近语境里, 银行战略议题与权威政策主题的贴合度」。ss 轨的回退语义严格镜像 ctx: 当某银行某年不存在银行与金科同句共现时, content_ss 优雅回退为全文正文, 对应 ss_is_fallback 置 True 并共享 n_articles 分母; 当整条金科词典不可用时优雅全回退。按 full-only 门控口径 (2026-06-29), 本 ss 列是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集。本列与家族内 full、ctx 两轨, 以及 vintage 主轨的 auth_sim_lda_ss, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混进同一 over-identified Hansen J 过度识别检验。当 content_ss 文本缺失时本列优雅置 NaN, 逐轨独立降级, 不借 full 轨分母。在锚点维度上, 本列同样固定采用全年份静态锚点 (_allv), 其 vintage 逐年锚点对应臂为 auth_sim_lda_ss: 因此本列在文本轨与锚点口径两处都取非主生产口径 (最严格的同句共现窗 × 含未来文本的全年份锚点), 属双重稳健性对照, 解读须格外审慎——同句共现的样本量在开发期短面板上往往稀薄, 叠加静态锚点后其绝对水平的可比性进一步依赖底层主题空间, 故本列仅在同轨同锚点口径内做序内比较, 不与 full/ctx 轨或其他相似度通道横向比水平。它的价值在于: 若最聚焦语境下、放松前视约束后, 银行战略与政策的主题贴合度仍与 full 轨 vintage 主轨方向一致, 则主结论的稳健性得到三轨与锚点两个维度的交叉支持。

<!-- rendered-citations:begin -->
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, Article 1752103. https://doi.org/10.3389/frai.2026.1752103
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Xia, B., Rawte, V., Gupta, A., & Zaki, M. J. (2024). FETILDA: Evaluation framework for effective representations of long financial documents. ACM Transactions on Knowledge Discovery from Data, 18(7), 1-27. https://doi.org/10.1145/3657299
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. Nature Human Behaviour, 4(11), 1208-1214. https://doi.org/10.1038/s41562-020-0912-z
<!-- rendered-citations:end -->
