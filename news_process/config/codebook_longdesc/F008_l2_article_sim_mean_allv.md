---
family_id: F008
columns:
- article_sim_mean_allv
- article_sim_mean_allv_ctx
- article_sim_mean_allv_ss
- article_sim_mean_lg_allv
- article_sim_mean_lg_allv_ctx
- article_sim_mean_lg_allv_ss
unit: 余弦相似度均值 (无量纲, 理论值域 [-1,1], 实务多落 [0,1])
formula: "article_sim_mean_allv{track} = mean_{文章 i ∈ (target_bank, year)} policy_cosine_sim_allv{track}_i; policy_cosine_sim_allv{track} = cos(emb(article_i,{track}), emb(全语料静态政策锚点)); {track} ∈ {(full 无后缀), _ctx, _ss}, 嵌入轨 ∈ {MAIN Qwen 4096 维 (无 _lg), _lg text-embedding-3-large 3072 维}"
producer: news_process/pipeline/panel/runner.py (bank-year 聚合); 上游文章级 news_process/pipeline/filtering/policy_alignment.py::compute_article_policy_alignment
upstream:
- 16_article_policy_alignment.parquet (policy_cosine_sim_allv{track} · policy_cosine_sim_lg_allv{track})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (bank-year 面板承载列)
citations:
- doi: 10.3389/frai.2026.1752103
  type: journal
  authors: Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J.
  year: 2026
  title: "FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  venue: Frontiers in Artificial Intelligence
  vol: 9
  pages_or_artno: 1752103
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: 102325
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
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
本家族刻画的构念是「银行年度媒体叙事与权威宏观政策文本的语义贴合度」在全语料静态锚点口径下的年度均值。其原子度量出自文章级阶段 16 (article_policy_alignment): 对每一篇目标银行相关报道, 先取该篇的三轨文本表示, 再与一枚由权威政策文档拼接并做均值池化、L2 归一化后的宏观锚向量算余弦相似度, 得到 policy_cosine_sim。该操作化把"这篇报道在讲的东西离国家金融科技政策导向有多近"落成一个连续标量, 理论值域为余弦的 [-1,1], 实务中银行金科报道与政策锚点极少反向, 故绝大多数落在 [0,1]。面板层 (pipeline/panel/runner.py) 再按 (target_bank, year) 分组对文章级值取算术均值, 得到本家族的 bank-year 列 article_sim_mean_allv 及其两条轨道后缀与两条嵌入孪生。行宇宙沿用 full-only 留篇门控 (2026-06-29): 一篇报道是否计入银行年度, 由 llm_verified_full 判定; 均值分母为该银行该年的留篇集, ctx/ss 轨为 conditional-on-full 的测度轨, 不另立留篇宇宙。均值聚合刻意采用连续变量而非离散化分箱, 以避免人为阈值切割损失信息 (Gelman (2008) 强调连续输入的标准化处理优于武断二分)。与均值并列的还有一枚同源 *_std 离散度列 (归属 std 家族, 不在本册); 单篇 bank-year 的样本标准差在 ddof=1 下数学未定义, 生产刻意保留 NaN 而非强填 0, 以免把"离散度不可估计"伪装成"零分歧"。

【方法学与计算】
后缀 _allv (all-vintage, 全年份/全语料静态锚点) 是本家族区别于同名 vintage 主轨的核心。主轨 policy_cosine_sim 默认走 vintage-aware 前视守卫: 年度 t 的文章只与发布年份 ≤ t 的政策文档段拼成锚点算余弦, 以消除"2017 年报道却与 2022 年才出台的政策贴近"这一前视构造。_allv 孪生则用所有年份政策文档拼成的静态全语料锚点 (即 vintage 关闭时的旧行为) 对同一批文章、以完全一致的下游构造 (同嵌入、同池化、同余弦、同聚合) 再算一遍。二者唯一差异在锚点文本集合, 因此 _allv 天然含有 t 期尚不可知的未来政策文本, 系 ex-post / 全语料口径, 仅作 anchor-robustness 稳健性对照, 绝不替换 vintage 主轨。当年份不可解析或 vintage 关闭而退化为静态锚点时, _allv 与主轨 byte-identical (诚实退化, 生产复用同一副本免重算)。嵌入侧为 co-primary 双轨零本地模型架构: MAIN 无 _lg 后缀槽 = Qwen3-Embedding-8B (硅基流动 API, 4096 维), _lg 槽 = text-embedding-3-large (3072 维)。两轨同为主测度、互为稳健性、严格 both-or-neither parity: 任一族嵌入失败则两族同置 NaN, 无单边孤儿列。三轨文本在阶段 14 物化: full = 标题 prepend + 全文正文, ctx = 标题 + 实体上下文窗口, ss = 标题 + 银行与金科同句 ±N 窗; ss 无同句共现时镜像 ctx 的回退语义降级为全文 body。

【文献定位】
把文本相似度作为经济计量变量、并以外部权威文本为锚点算余弦, 是近年文本金融的成熟范式。Liu, Cao & Wen (2024) 在中国情境下直接度量企业披露与政府文本的余弦相似度并检验其定价含义, 是本家族"银行叙事 vs 政策锚点"操作化最贴近的先例。Chen, Granville & Matousek (2026) 用大模型解码央行沟通, 印证宏观权威政策/沟通文本可被嵌入向量化并支撑下游经济分析, 支持本家族把国家金科政策拼成静态锚点的做法。Jehnen, Villalba-Díez & Ordieres-Meré (2026) 的领域专用句向量模型说明金融文本嵌入对潜在主题的判别力, 为本家族选择 co-primary 句向量轨提供方法学背书。Mainali, Slud, Singer & Fagan (2022) 对共现与相似度指标的系统比较提醒相似度构造对锚点与归一化选择敏感, 正是本家族并列 vintage 与 _allv 双锚点作稳健性对照的动机。Arts, Cassiman & Hou (2025) 在顶刊 Strategic Management Journal 上把企业间文本 (专利文本) 的余弦相似度构造为技术差异化的计量变量并检验其对 M&A 交易的解释力, 为本家族"把文本余弦相似度当作一枚连续经济计量变量"这一核心操作化提供了顶刊层级的方法学背书, 印证以嵌入余弦度量文本语义贴合、再纳入回归的做法在一线实证研究中已成规范。需强调的铁律: 三轨 (full/ctx/ss)、co-primary 双嵌入 (MAIN/_lg)、以及 vintage 主轨与 _allv 静态锚点三组维度均为「各自 just-identified 并排、互为稳健性、不分主次」的规格稳健性轨, 严禁把任意两条混进同一 over-identified Hansen J 检验。

## VAR: article_sim_mean_allv

【变体差分】
本列是家族在 _allv 口径下的 canonical 起点: 全语料静态政策锚点 × full 轨文本 × MAIN (Qwen, 4096 维) 嵌入, 按 (target_bank, year) 对文章级 policy_cosine_sim_allv 取均值。它与同名 vintage 主轨 article_sim_mean 唯一差异是锚点集合 —— 本列锚点纳入全部年份 (含 t 期之后发布) 的政策文档, 是 ex-post/全语料口径, 故只能作 anchor-robustness 稳健性对照, 绝不替换前视守卫的 vintage 主轨。之所以并列这条含未来信息的锚点, 是因为 vintage 前视守卫在早年 (如 2014) 可用政策文档稀少、锚点池不稳, 全语料静态锚点则提供一枚跨年恒定的参照系, 二者相关性越高越说明相似度构造对锚点选择不敏感。full 轨含义为标题 prepend 后叠加全文正文, 相较 ctx/ss 覆盖信息最全但可能稀释银行与金科的局部共现信号。嵌入取无 _lg 后缀的 MAIN 槽, 与 article_sim_mean_lg_allv 构成 co-primary 双轨, both-or-neither parity 保证二者要么并存要么同置 NaN。均值分母为该银行该年 full 留篇集大小 (full-only 门控, 2026-06-29), 单篇 bank-year 的均值即该单篇值本身、其配套 std 保持 NaN。使用时须记: 本列与其 vintage 孪生、与 ctx/ss 轨、与 _lg 孪生分属三组正交稳健性维度, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J 当作多个独立工具。当年份不可解析或 vintage 关闭退化时, 本列与 vintage 主轨数值 byte-identical, 属诚实退化而非缺陷, 生产复用同一副本免二次嵌入调用。

## VAR: article_sim_mean_allv_ctx

【变体差分】
本列在 article_sim_mean_allv 基础上把文本轨从 full 切到 ctx: 文章级源列改为 policy_cosine_sim_allv_ctx, 嵌入仍为无后缀的 MAIN (Qwen) 轨, 锚点仍为全语料静态 _allv 口径。ctx 轨 = 标题 prepend + 实体上下文窗口, 即只截取目标银行实体附近的文本窗后再与政策锚点算余弦, 相较 full 轨剔除了远离实体的段落, 使相似度更聚焦银行相关叙事、减少全文背景噪声的稀释。构念上 ctx 回答的是"围绕这家银行的那段话有多贴近政策", 而 full 回答"整篇报道有多贴近政策", 二者刻意保留为不分主次的并行测量而非替代。本列是 conditional-on-full 的测度轨: 行宇宙仍为 full-only 留篇集的子集, 不另立留篇门控; 文章级 policy_cosine_sim_allv_ctx 缺列 (旧 schema 或 ss/ctx 未上线) 时聚合按存在性优雅跳过, 分母严格取 ctx 自身有效篇数、不借 full 分母。与 full 轨 article_sim_mean_allv、ss 轨 article_sim_mean_allv_ss 三者为「互为稳健性、不分主次」的三轨并排, 各自 just-identified, 严禁三轨混进同一 over-identified Hansen J。同时本列与其 _lg 孪生 article_sim_mean_lg_allv_ctx 构成 co-primary 双轨, parity 双射 both-or-neither; 与 vintage 口径的 ctx 孪生构成锚点稳健性对照。实证使用时, 若发现 ctx 轨系数与 full 轨方向一致而幅度更大, 通常说明政策贴合信号确实集中在银行实体附近文本、被全文背景稀释; 反之若两轨背离则提示相似度可能受全文无关段落驱动, 需谨慎解读。dev T=2 小样本上 ctx 轨因窗口截断后有效文本变少, 可能出现零方差退化, 属预期而非 bug, 生产 T=18 恢复正常。

## VAR: article_sim_mean_allv_ss

【变体差分】
本列是 _allv 口径下最严的文本轨: 文章级源列为 policy_cosine_sim_allv_ss, 嵌入取无后缀 MAIN (Qwen), 锚点为全语料静态口径。ss (same-sentence) 轨 = 标题 prepend + 银行与金科同句 ±N 窗 (窗口半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1; 该键与 stage 13 cooccurrence_filter.sentence_radius 是两个不同键, 不可混用), 只保留银行实体与金科词在同一句及邻窗共现的最小文本单元, 是三轨中信号最聚焦、噪声最低但也最易稀疏的一轨。构念上 ss 逼近"银行与金融科技被同句谈及的那句话有多贴近政策", 剔除了报道中银行与金科各自独立出现却不相关的段落。回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 退化为全文 body 且 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; FINTECH_AC 为空时 *_is_fallback 全 True 优雅降级, 绝不静默清空。本列同为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集, 分母取 ss 自身有效篇数。它与 full/ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与 _lg 孪生 article_sim_mean_lg_allv_ss 构成 co-primary 双轨严格 both-or-neither parity。作为信号最纯的一轨, ss 在生产大样本下最能剥离"银行与金科各自出现却互不相关"的报道噪声, 是三轨中对政策贴合构念效度最高、但样本损耗也最大的取舍; 研究者应把它视作 full/ctx 的边界稳健性验证而非替代主测度。dev T=2 上 ss 轨因同句共现稀疏更易全 NaN 或零方差, 属预期退化, 生产 T=18 语料下恢复常态。

## VAR: article_sim_mean_lg_allv

【变体差分】
本列是 article_sim_mean_allv 的 co-primary _lg 孪生: 全语料静态锚点 × full 轨 × 第二嵌入 text-embedding-3-large (3072 维, 走 OpenAI/yunwu 端点), 其余聚合口径与 MAIN 完全对称。_lg 与 MAIN (Qwen, 4096 维) 并非主辅关系而是对等 co-primary 双轨, 分处阿里与 OpenAI 两个厂商的嵌入空间, 用于跨厂商互证语义相似度构造不被单一模型的向量几何驱动; 二者严格 both-or-neither parity, 生产层按同名约定把 raw policy_cosine_sim_lg_allv 聚合后 rename 为 article_sim_mean_lg_allv, 以保证面板层 MAIN=article_sim_mean_allv 与 _lg 列名双射不破 (code-review P1-1 裁决)。缺源列时优雅跳过, 但一旦 MAIN 或 _lg 任一族嵌入失败则两族同时置 NaN, 不留单边孤儿列。使用铁律: MAIN 与 _lg 各自 just-identified 并排、互为稳健性、不分主次, 严禁把 article_sim_mean_allv 与本列同时塞进同一 over-identified Hansen J 当作两个独立工具; 二者应作并行规格分别报告。本列同时叠加 _allv 全语料静态锚点口径, 故相对 vintage 的 _lg 孪生仍是 anchor-robustness 对照, 含 t 期之后的未来政策文本, 系 ex-post 口径, 不作前视守卫指标, 论文须明确披露。实证价值在于: 若把 MAIN 与 _lg 两枚不同厂商嵌入下的同一 full×allv 相似度并排跑主回归, 系数符号与显著性一致即构成对"结论不被单一嵌入几何驱动"的有力佐证; 这正是本项目零本地模型、co-primary 双轨设计的核心目的, 与三轨、锚点口径共同织成规格稳健性网。当 _lg 端点因限流或密钥缺失而嵌入失败时, both-or-neither 守卫会连带把 MAIN 对偶一起置 NaN, 使面板层不出现只有一半嵌入证据的误导性观测。

## VAR: article_sim_mean_lg_allv_ctx

【变体差分】
本列是 _lg 嵌入 × ctx 文本轨 × _allv 静态锚点的三重组合: 文章级源列 policy_cosine_sim_lg_allv_ctx 按 (target_bank, year) 取均值。相对 article_sim_mean_allv_ctx (MAIN) 唯一差异是嵌入模型换为 text-embedding-3-large (3072 维), 与之构成 co-primary 双轨严格 both-or-neither parity; 相对 article_sim_mean_lg_allv (full) 差异是文本轨收窄到实体上下文窗, 只保留目标银行实体附近文本再与政策锚点算余弦, 剔除远离银行实体的段落, 使相似度更聚焦银行相关叙事而非全文背景。本列同时承载三条正交稳健性维度: 三轨 (与 lg_allv full/ss 并排)、co-primary 双嵌入 (与 MAIN 的 allv_ctx 并排)、锚点口径 (与 vintage 的 lg ctx 孪生对照)。三组维度各自 just-identified、互为稳健性、不分主次, 严禁任意两条混进同一 over-identified Hansen J 当作独立工具堆叠。本列为 conditional-on-full 测度轨, 行宇宙为 full 留篇集子集, 文章级源列缺失时聚合优雅跳过、分母严格取 ctx 自身有效篇数不借 full 分母。both-or-neither 守卫下, 若 _lg 或 MAIN 任一嵌入族失败, 本列与其 MAIN 对偶 article_sim_mean_allv_ctx 同置 NaN。作为 _lg × ctx 交叉的中间聚合列, 本列在实证中通常与 MAIN 的 allv_ctx 高度相关, 二者背离即提示 ctx 窗口下政策贴合估计对嵌入模型敏感, 属值得报告的稳健性信号。同理本列与 lg_allv 的 full 轨对照可揭示文本粒度效应, 与 vintage 的 lg ctx 孪生对照可揭示锚点口径效应, 三组对照互不交叉、各自独立读数。dev T=2 上 ctx 轨因窗口截断有效文本减少而零方差退化属预期, 生产 T=18 恢复。

## VAR: article_sim_mean_lg_allv_ss

【变体差分】
本列是家族中约束最叠满的一列: _lg 嵌入 (text-embedding-3-large, 3072 维) × ss 同句轨 × _allv 全语料静态锚点, 文章级源列 policy_cosine_sim_lg_allv_ss 按 bank-year 取均值。相对 article_sim_mean_allv_ss (MAIN, Qwen 4096 维) 差异仅在嵌入模型, 二者构成 co-primary 双轨严格 both-or-neither parity 双射; 相对 article_sim_mean_lg_allv_ctx 差异在文本轨进一步收窄到银行与金科同句 ±N 窗 (窗口半径 config filtering.yaml context_window.ss_sentence_radius, 默认 1), 只保留银行与金融科技被同句谈及的最小文本单元。ss 回退语义镜像 ctx: 无同句共现时 content_ss 退化为全文 body 且 ss_is_fallback=True, 共享 n_articles 分母, 绝不静默清空。本列为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集, 分母取 ss 自身有效篇数。它与 lg_allv 的 full/ctx 两轨、与 MAIN 的 allv_ss 对偶、与 vintage 的 lg ss 孪生分属三组正交稳健性维度, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两条混进同一 over-identified Hansen J。both-or-neither 守卫下本列与 MAIN 对偶 article_sim_mean_allv_ss 同存亡, 任一嵌入族失败即两列同置 NaN; dev T=2 上因 ss 同句共现稀疏叠加 _lg 可用性双重约束, 本列最易出现全 NaN 或零方差, 属预期退化而非缺陷, 生产 T=18 语料下恢复常态。作为家族里文本粒度最细、嵌入厂商为第二轨、锚点为全语料静态口径三者叠加的极端组合, 本列在实证中主要充当"即便把测量收到最纯的同句信号、换到另一家嵌入模型、并用最宽松的静态锚点, 政策贴合结论是否依旧成立"的边界稳健性检验; 其读数与 canonical article_sim_mean_allv 一致即最大限度地排除了轨道、模型、锚点三重设定共同驱动结果的疑虑, 是本家族稳健性网络最外圈的一个节点。

<!-- rendered-citations:begin -->
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, 1752103. https://doi.org/10.3389/frai.2026.1752103
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, 102325. https://doi.org/10.1016/j.intfin.2026.102325
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), eabj9204. https://doi.org/10.1126/sciadv.abj9204
Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine, 27(15), 2865-2873. https://doi.org/10.1002/sim.3107
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
<!-- rendered-citations:end -->
