---
family_id: F007
columns:
- article_sim_mean
- article_sim_mean_ctx
- article_sim_mean_lg
- article_sim_mean_lg_ctx
- article_sim_mean_lg_ss
- article_sim_mean_ss
unit: 余弦相似度均值 (无量纲, 理论域 [-1,1], 实证多落 [0,1])
formula: "article_sim_mean = mean_over_articles(policy_cosine_sim) within (target_bank, year); policy_cosine_sim = cos(emb_article, emb_policy_anchor)"
producer: news_process/pipeline/panel/runner.py ; news_process/pipeline/panel/export.py
upstream:
- 16_article_alignment.parquet (policy_cosine_sim / policy_cosine_sim_ctx / policy_cosine_sim_ss 及 _lg 孪生, Stage 16 article_policy_alignment 产出)
- 24_herd_decay_processor.parquet (df_exploded, verified 聚合域 semi-join)
- 40_panel_yearly.parquet
citations:
- doi: 10.3389/frai.2026.1752103
  type: journal
  authors: Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J.
  year: 2026
  title: "FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  venue: Frontiers in Artificial Intelligence
  vol: 9
  pages_or_artno: Article 1752103
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: Article 102325
- doi: 10.1016/j.frl.2025.107111
  type: journal
  authors: Fan, S., Wu, Y., & Yang, R.
  year: 2025
  title: "Measuring firm-level supply chain risk using a generative large language model"
  venue: Finance Research Letters
  vol: 77
  pages_or_artno: Article 107111
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: Article 111823
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: Article 113917
- doi: 10.1126/sciadv.abj9204
  type: journal
  authors: Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F.
  year: 2022
  title: "A better index for analysis of co-occurrence and similarity"
  venue: Science Advances
  vol: 8
  issue: 4
  pages_or_artno: Article eabj9204
- doi: 10.1002/sim.3107
  type: journal
  authors: Gelman, A.
  year: 2008
  title: "Scaling regression inputs by dividing by two standard deviations"
  venue: Statistics in Medicine
  vol: 27
  issue: 15
  pages_or_artno: 2865-2873
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"银行涉金融科技报道与权威政策话语的语义对齐度"。其文章级原语是 Stage 16 (article_policy_alignment) 产出的 policy_cosine_sim: 对每篇经留篇门控保留的银行金科报道, 先用嵌入引擎把报道文本编码为稠密向量, 再把一组权威政策锚文本 (监管口径的金融科技政策表述) 编码为锚向量, 两者取余弦相似度, 得到该篇报道在语义空间中"贴近政策话语"的程度。本家族六列均是把这一文章级相似度按 (target_bank, year) 分组求算术平均, 得到银行年度面板上的平均政策对齐度。数据链路上游是原始媒体语料经预处理、银行实体识别、金科词识别、Stage 13 共现硬过滤、Stage 14 三轨文本物化后, 在 Stage 16 (16_article_policy_alignment.py, 逻辑归 pipeline/filtering/policy_alignment.py) 逐篇算出的 policy_cosine_sim 系列列; 面板聚合发生在 pipeline/panel/runner.py 的连续聚合块 (groupby 求 mean), 变量标签在 pipeline/panel/export.py 声明 (Avg Article-Policy Cosine Sim), 最终落在 40_panel_yearly.parquet。语义上它回答的是: 一家银行某年被媒体报道时, 这些报道整体上多大程度地复述、呼应或对齐了官方金融科技政策的话语框架。

【方法学与计算】
计算分两层。文章级 (Stage 16, article_policy_alignment): policy_cosine_sim = cos(报道向量, 政策锚向量), 余弦相似度理论域为 [-1,1], 在高维文本嵌入空间中实证取值通常落在正区间 [0,1]。面板级 (runner.py): 对同一 (target_bank, year) 内所有留篇报道的 policy_cosine_sim 取均值 (pandas groupby.agg 的 'mean'), 即得 article_sim_mean。选择连续均值而非离散化阈值分类, 依据连续变量在回归中信息损失更小、任意阈值切分会牺牲组内变异并可能人为制造非线性伪断点的方法学立场, 与本家族并列的象限离散分类 (token/hidden/subst adoption) 分工互补: 前者供主回归, 后者供机制检验。聚合域经过 semi-join 收敛: runner.py 用 _filter_to_verified_universe 把聚合样本收缩到 df_exploded (24_herd_decay) 的 verified 子集, 使本家族与全仓其余面板测度共享同一 verified 聚合域, 避免在含未通过 LLM 验证文章的规则预筛全集上聚合导致的孪生对取值系统性偏移与 phantom bank-year。留篇门控口径与全仓一致, 采用 full-only (2026-06-29): 一篇报道是否计入银行金科报道宇宙只看其 full 轨 LLM 验证是否通过, ctx/ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。相应的 std 孪生 (article_sim_std) 对单篇 bank-year 保持 NaN 而非强填 0, 因为 ddof=1 的样本标准差在单观测下数学未定义, 保留 NaN 与"无数据即未测量"契约一致。

【文献定位】
把机构文本与政策/政府话语的语义贴近度作为可度量的经济变量, 是近年文本金融的活跃方向。Liu, Cao & Wen (2024) 直接以中国情境下"企业文本与政府文本的余弦相似度"作为测度并考察其定价含义, 是本家族最贴近的方法学先例。Chen, Granville & Matousek (2026) 用大语言模型解码央行沟通、Xu 等 (2024) 度量政府控制媒体语调对资本市场的价值, 共同说明"官方话语—市场文本对齐"这一构念的经济意义。在嵌入表征侧, Jehnen 等 (2026) 的 FinTextSim 证明领域专用句向量能从金融披露中抽取更具预测力的潜在语义, 支持以稠密嵌入余弦而非词袋重叠来度量对齐; Fan, Wu & Yang (2025) 展示生成式大模型可从企业文本抽取结构化风险信号, 印证嵌入/生成范式在金融文本测度上的可用性。把文本/技术相似度构造为刻画主体间差异化程度的可度量变量并用于识别经济后果, Arts, Cassiman & Hou (2025) 在企业技术差异化与并购的研究中提供了顶刊层面的方法学范例, 佐证以嵌入余弦这类连续相似度作为主体对齐/差异测度进入回归的正当性。相似度指标本身的统计性质由 Mainali 等 (2022) 系统讨论。回归输入的标准化取舍可参照 Gelman (2008)。需强调, 本家族的三轨 (full/ctx/ss) 与 co-primary 双轨嵌入 (Qwen canonical 无后缀 / text-embedding-3-large 的 _lg) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨或不同嵌入空间的列混进同一 over-identified Hansen J 过度识别检验。

## VAR: article_sim_mean

【变体差分】
本列是家族 canonical (无任何后缀): full 轨叠加 Qwen canonical 嵌入。full 轨文本等于标题 prepend 后的标题加全文正文 (content_full), 是本家族里最完整、信息量最大的报道语料通道, 覆盖整篇报道而非局部语段; 嵌入引擎走 canonical 无后缀槽 Qwen/Qwen3-Embedding-8B (硅基流动, 4096 维)。文章级原语为无后缀的 policy_cosine_sim, 面板聚合处 runner.py 以均值方式把它汇总为本列。它是主回归默认采用的政策对齐测度, 也是本家族其余五列的比较基准: ctx 与 ss 列相对它替换文本轨道, 三个 _lg 列相对它替换底层嵌入模型, 因此读懂本列的口径就等于读懂了全家族的公共骨架。在留篇门控 full-only 之下, 计入本列均值的报道数直接等于该银行当年 full 轨情感大模型验证通过的报道篇数, 与面板留篇篇数口径完全一致, 无需向 ctx 或 ss 轨借用分母, 也不会出现分母错配。作为 canonical 文本轨与 canonical 嵌入的交点, 本列必须与三轨其余两轨、与三个 _lg 对偶各自独立地并排进入模型, 三者互为稳健性、不分主次, 严禁把本列与它们混入同一 over-identified Hansen J 过度识别检验。配套的离散度孪生 article_sim_std 在只有单篇报道的银行年度上保持 NaN 而非被强填为零, 因为样本标准差在单观测时数学上未定义, 保留缺失才如实表达"离散度不可估计", 而非把"无从判断"伪装成"零分歧"。

## VAR: article_sim_mean_ctx

【变体差分】
本列相对 canonical 只改文本轨道一个维度: 从 full 轨换成 ctx (实体上下文窗) 轨, 底层嵌入模型仍是 Qwen canonical, 其余一切口径不变。ctx 轨文本等于标题 prepend 后的标题加围绕目标银行实体的邻近窗口 (content_ctx), 在 Stage 14 的上下文物化阶段生成, 只保留紧贴目标银行实体的那段上下文而不是整篇正文。这样做的用意在于把政策对齐度收敛到"确与该银行相关"的语段上, 削弱全文中大量与该银行无关的段落对余弦相似度的稀释, 使测度更贴近该银行本身被媒体如何放在政策话语里叙述。文章级原语为 policy_cosine_sim_ctx, 面板聚合处 runner.py 在该列存在时才追加以均值方式汇总, 若旧 schema 或该轨未上线导致缺列则优雅跳过, 绝不报错。在 full-only 门控下, ctx 轨被明确降为 conditional-on-full 的测度兼稳健性轨: 它的行宇宙是 full 留篇集的一个子集, 计入均值的分母严格逐轨统计、绝不向 full 轨借分母, 从而保证每一轨的均值都建立在自身对应的报道集合上。ctx 与 full、ss 三轨各自独立地并排进入模型, 三者互为稳健性、不分主次, 严禁把三轨混入同一 over-identified Hansen J 过度识别检验。ctx 相对 full 的差异, 本质上反映的是"把语料从整篇全文收缩到实体上下文窗"这一口径选择对政策对齐测度的敏感性, 属于规格层面的稳健性并排, 而非谁主谁次的替代关系。

## VAR: article_sim_mean_lg

【变体差分】
本列相对 canonical 只改底层嵌入模型一个维度: 文本轨仍是最完整的 full 轨, 但把编码报道与政策锚的嵌入从 Qwen canonical 换成 co-primary 的 _lg 槽, 即 text-embedding-3-large (OpenAI 或 yunwu 代理, 3072 维)。它是 canonical 列 article_sim_mean 的 co-primary 对偶: 两轨同为主测度、互为稳健性、严格 parity, 表现为列名双射 both-or-neither——只要一条轨存在另一条必须存在, 任一嵌入调用返回 None 则同族的这两列一并置 NaN, 绝不留下单边孤儿。文章级原语为 policy_cosine_sim 的 _lg 孪生 policy_cosine_sim_lg, 在面板层沿 full/ctx/ss 三轨对称聚合。之所以要并列两套独立嵌入, 根本原因在于余弦相似度的绝对水平强烈依赖具体嵌入空间的几何性质, 包括维度、训练语料分布与向量各向异性, 同一段文本在不同嵌入空间里算出的相似度并不可直接比较水平; 因此用两个不同厂商、不同维度的模型分别度量同一政策对齐构念, 才能检验主结论并非由单一嵌入空间的表征伪影所驱动, 而是稳健地存在于两套几何之下。铁律: 两条 co-primary 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 canonical 与 _lg 两列混进同一 over-identified Hansen J 过度识别检验。还须强调, 本列所换的是嵌入模型, 与 Stage 21 情感大模型的三家投票没有任何关系, 换嵌入时对全部情感列零误改。

## VAR: article_sim_mean_lg_ctx

【变体差分】
本列同时切换两个维度: 文本轨换成 ctx (实体上下文窗), 嵌入换成 _lg 的 text-embedding-3-large。它既是 article_sim_mean_ctx (Qwen 嵌入的 ctx 轨) 的 co-primary 对偶, 又是 article_sim_mean_lg (lg 嵌入的 full 轨) 在 ctx 轨上的投影, 处于"ctx 文本轨与 _lg 嵌入空间"的交点位置。文章级原语为 policy_cosine_sim_lg 的 ctx 孪生, 面板聚合处 runner.py 在对应列存在时逐轨以均值汇总, 缺列优雅跳过。相对 canonical, 本列在两条彼此正交的稳健性维度上同时偏离: 一方面把语料从整篇全文收缩到实体上下文窗, 另一方面把嵌入空间从 Qwen 换到 text-embedding-3-large, 因此它检验的是"文本口径与嵌入几何两者同时改变时结论是否依旧成立"。both-or-neither 的 parity 守卫在 _lg 双轨上严格成立: 一旦 _lg 嵌入调用缺失, 本列与其同族其余 _lg 列会被一并置为 NaN, 不留单边孤儿。在 full-only 门控之下, 本列是 conditional-on-full 的测度兼稳健性轨, 其行宇宙是 full 留篇集的子集, 计入均值的分母严格逐轨统计、绝不借用 full 轨分母。正因为它在文本口径与嵌入几何两条正交维度上同时偏离 canonical, 读者不应把本列与 canonical 的水平差异归因于单一原因, 而应把它理解为两种规格选择叠加后的联合稳健性证据。铁律照旧且必须复述: full/ctx/ss 三轨之间、Qwen 与 _lg 双轨之间, 都是各自 just-identified 并排、互为稳健性、不分主次, 严禁把本列与任一相邻轨或任一对偶混入同一 over-identified Hansen J 过度识别检验。

## VAR: article_sim_mean_lg_ss

【变体差分】
本列文本轨换成 ss (银行金科同句窗), 嵌入换成 _lg 的 text-embedding-3-large, 是全家族里语料最严格、嵌入又非 canonical 的一列。ss 轨文本等于标题 prepend 后, 取目标银行与金融科技词在同一句子内共现的语段再加上下 N 句窗 (content_ss, 窗半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认为 1 句)。ss 把政策对齐度进一步收敛到"银行与金科确实在同一句里共现"的证据段, 是三轨中对相关性要求最高的一轨。关键的回退语义必须写清: ss 镜像 ctx——当某篇报道并不存在银行与金科的同句共现时, content_ss 回退为全文正文, 同时 ss_is_fallback 标志置 True, 并与全文轨共享同一 n_articles 分母; 而当金融科技 AC 词表整体为空时, 所有 *_is_fallback 全部置 True, 作整体的优雅降级, 绝不静默产生空值。文章级原语为 policy_cosine_sim_lg 的 ss 孪生, 其面板标签由 export.py 的第三轨机械派生循环自动补全, 无需手列。本列是 article_sim_mean_ss (Qwen 嵌入的 ss 轨) 的 co-primary 对偶, both-or-neither 的 parity 守卫在两者间严格成立: 只要其中一列存在另一列必然存在, 缺失时两列一并置 NaN。由于本列同时落在最严语料轨与非 canonical 嵌入空间, 它是全家族里对"相关性证据最强、且换用第二套嵌入几何"这一双重约束最敏感的取值, 适合用来检验在最保守语料口径下结论是否仍由两套嵌入共同支撑。铁律: ss 与 full、ctx 三轨之间, Qwen 与 _lg 双轨之间, 均各自 just-identified 并排、互为稳健性、不分主次, 严禁把本列与任一相邻轨或对偶混入同一 over-identified Hansen J 过度识别检验。

## VAR: article_sim_mean_ss

【变体差分】
本列相对 canonical 只改文本轨道一个维度: full 换成 ss (银行金科同句窗), 底层嵌入仍是 Qwen canonical。它是三轨中语料最严格的一轨在 canonical 嵌入下的取值, 与 article_sim_mean_lg_ss 互为 co-primary 对偶。ss 轨文本等于标题 prepend 后, 取目标银行与金融科技词在同一句子内共现的语段再加上下句窗 (content_ss); 其判定口径是不对称的——银行侧要经过否定语境剔除与短名过滤, 金科侧则用裸 AC 词表直接匹配, 二者口径刻意不同。回退语义镜像 ctx: 当报道无同句共现时 content_ss 回退为全文正文, ss_is_fallback 标志置 True, 并与全文轨共享同一 n_articles 分母, 保证不会因 ss 语料收缩而产生空分母或系统性丢样。文章级原语为 policy_cosine_sim_ss, 面板聚合处 runner.py 在该列存在时以均值追加汇总, 缺列则优雅跳过以兼容旧 schema。在 full-only 门控下, ss 轨被降为 conditional-on-full 的测度兼稳健性轨: 其行宇宙是 full 留篇集的子集, 计入均值的分母严格逐轨统计、绝不借用 full 轨分母。ss 相对 full 与 ctx 的差异, 反映的是把语料进一步收敛到"最强的银行金科同句共现证据段"这一口径选择对政策对齐测度的敏感性。铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨连同 Qwen 与 _lg 双轨混入同一 over-identified Hansen J 过度识别检验。

<!-- rendered-citations:begin -->
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, Article 1752103. https://doi.org/10.3389/frai.2026.1752103
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, Article 102325. https://doi.org/10.1016/j.intfin.2026.102325
Fan, S., Wu, Y., & Yang, R. (2025). Measuring firm-level supply chain risk using a generative large language model. Finance Research Letters, 77, Article 107111. https://doi.org/10.1016/j.frl.2025.107111
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, Article 113917. https://doi.org/10.1016/j.enpol.2023.113917
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine, 27(15), 2865-2873. https://doi.org/10.1002/sim.3107
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
<!-- rendered-citations:end -->
