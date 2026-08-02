---
family_id: F016
columns:
- auth_sim_emb_allv_ctx
- auth_sim_emb_allv_full
- auth_sim_emb_allv_ss
- auth_sim_emb_lg_allv_ctx
- auth_sim_emb_lg_allv_full
- auth_sim_emb_lg_allv_ss
unit: 余弦相似度 (无量纲, 值域 [0,1])
formula: "auth_sim_emb_allv{track} = cos(v_bank_year, v_anchor_allv); v_bank_year = 该银行该年聚合文本的嵌入向量, v_anchor_allv = 全年份权威政策语料静态锚点的嵌入向量 (幽灵锚点法, 取同构相似度矩阵末列 sim[:-1,-1]); emb 轨用 Qwen3-Embedding-8B, emb_lg 轨用 text-embedding-3-large"
producer: news_process/pipeline/features/policy_similarity.py::_ghost_anchor_metrics
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 权威政策语料 (policy_alignment.load_policy_corpus_docs, 全年份静态锚点)
- 25_article_sbert.parquet (co-primary 嵌入引擎 emb / emb_lg)
citations:
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: You, K.
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., ... Weng, L.
  year: 2022
  title: "Text and code embeddings by contrastive pre-training"
  venue: arXiv
- doi: 10.18653/v1/2023.eacl-main.148
  type: journal
  authors: Muennighoff, N., Tazi, N., Magne, L., & Reimers, N.
  year: 2023
  title: "MTEB: Massive text embedding benchmark"
  venue: Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics
  pages_or_artno: 2014-2037
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: The Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
new_dois: []
---

## CORE

【构念与来源】
本家族测度一家银行在某一年份, 其战略叙事与国家金融科技权威政策之间的语义贴合度, 属权威政策战略响应度特征 (policy_similarity) 的嵌入维度、全年份锚点稳健孪生子族; 须澄清 policy_similarity 是 panel runner 子步骤 7h(policy) 内运行的 feature 模块 (由 _ghost_anchor_metrics 产出), 并非 OUTPUT_REGISTRY 里的独立 pipeline stage, 更不等同于产出 semantic_staleness 系列的 stage 26 (语义陈旧度), 部分源码 docstring 沿用的旧编号 26 是仓库内部的编号碰撞, 以权威口径为准本子族不占用 stage 26。构念根植于文本经济学的宏微观收敛思想: 把碎片化的银行年度披露聚合为一份"企业年度战略画像", 再把国家重磅政策文件汇成"标准答案", 二者投入同构特征空间后测其收敛程度, 分数越高表示该行的战略步调与国家政策跟得越紧。方法学谱系上, 聚合后向量化的思路承自 Hoberg 与 Phillips (2016) 的文本网络产品空间与 Hassan 等 (2019) 把宏观政策文本注入企业级同构空间的政治风险测度; 在中国政企文本对齐的经验先例上, 最贴近的是 Liu、Cao 与 Wen (2024) 以余弦相似度度量企业与政府文本靠拢并考察其定价含义的工作。本子族与 finance-benefit-society 一系的语言嵌入方法 (Jha、Liu 与 Manela, 2026) 共享"用连续嵌入而非离散词典刻画抽象经济构念"的取向, 但落点是政策贴合而非社会效益, 构念不可互换。

【方法学与计算】
计算走幽灵锚点法 (ghost anchor): 把权威政策锚点文本当作第 (N+1) 个"虚拟银行"挂在该年真实银行文本列表末尾, 送入与 stage 25 战略画像绝对同构的嵌入矩阵提取器, 取对称相似度矩阵最后一列 sim[:-1, -1], 即得各行相对该锚点的余弦相似度。超长的银行年度聚合文本走 token 分段加均值池化 (非旧注释所称固定字数截断), 嵌入引擎纯 API、维度由返回张量驱动。本子族的锚点是全年份静态锚点 (_allv): 不做 vintage 前视切分, 用所有年份 (含发布年份晚于 t 的) 政策文档拼成一份不随年份变化的标准答案。它与家族内的 vintage 主轨 (锚点只含发布年份 ≤ t 的政策, 消除"拿还没出生的政策当标答"的前视构造) 结构完全一致、唯锚点不同, 因此 _allv 系严格定位为锚点稳健性对照 (anchor-robustness), 绝不替换 vintage 主轨。当某年 vintage 锚点恰等于全年份静态锚点 (晚年政策已含全部文档) 时, 源码短路复用 vin 副本, 两轨逐字节相同, 属确定性 golden-safe 行为。留篇口径与全仓一致: 银行年度文本的聚合宇宙以 full-only 留篇门控 (2026-06-29) 的留篇集为准, ctx/ss 为 conditional-on-full 的子集测度; content_ss 缺失时该行 ss 轨优雅回退 (镜像 ctx: 无银行与金科同句共现即退回全文正文), 不产孤儿列。

【文献定位】
本子族横跨三条正交的规格维度, 每一维都遵循全仓铁律: 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性不分主次, co-primary 双嵌入 (Qwen 主轨与 text-embedding-3-large 的 _lg 轨) both-or-neither 严格 parity、亦互为稳健性, 全年份锚点 _allv 与 vintage 主轨互为锚点稳健性; 三者禁混进同一 over-identified Hansen J, 只能各自并列做过度识别外的稳健性阵列。嵌入模型选择上, 主轨 Qwen3-Embedding-8B 的能力见 Zhang 等 (2025), _lg 轨的 OpenAI 对比预训练嵌入见 Neelakantan 等 (2022), 两族在通用嵌入基准上的横向定位见 Muennighoff 等 (2023) 的 MTEB。度量层用余弦相似度须留意其已知陷阱: Steck、Ekanadham 与 Kallus (2024) 指出正则化线性模型学到的嵌入其余弦可能与语义相似度并不对应, You (2025) 进一步刻画余弦在何种几何条件下失效; 本子族以双嵌入并排、锚点双轨互证来缓释单一余弦度量的脆弱性。将嵌入用于社会科学的效度与可复现性方法论则以 Rodriguez 与 Spirling (2022) 为纲。

## VAR: auth_sim_emb_allv_ctx

【变体差分】
本列是全年份锚点嵌入子族的 ctx 轨、canonical Qwen 主嵌入变体。银行年度聚合文本取自 content_ctx (标题 prepend 加实体上下文窗口, stage 14 物化), 相对全年份静态政策锚点求余弦相似度。相对家族 canonical (full 轨) 的精确差分只在文本轨道: ctx 只纳入围绕银行实体的邻近窗口而非整篇正文, 因此度量的是"银行相关段落的战略语义"与政策的贴合, 剔除了与银行无关的通稿噪音, 但也可能因窗口过窄而漏掉散落全文的战略信号。它与 full、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 三轨禁混进同一 over-identified Hansen J。嵌入模型为 Qwen3-Embedding-8B (无 _lg 后缀即 canonical 主轨), 与同名 _lg 列 both-or-neither 严格 parity、互为稳健性。锚点为全年份静态锚点 (含未来政策), 相对同轨 vintage 主轨 (auth_sim_emb_ctx) 仅换锚点、构造全同, 定位为锚点稳健性对照, 绝不替换 vintage 主轨。ctx 轨的留篇宇宙是 full-only 门控留篇集的 conditional-on-full 子集。使用建议上, 若研究者担心 full 轨的整篇正文掺入与银行战略无关的行业背景稀释了政策贴合信号, 则本 ctx 列提供一个更聚焦于银行实体上下文的对照读数; 反之若窗口过窄导致 ctx 与 full 系统性背离, 该背离本身就是可披露的规格敏感性证据, 而非须择一取舍的噪音。在早期试跑 T=2 开发面板上, 权威政策相似度的前视守卫年份可能因有效样本不足 (n_valid < 3) 而暂无阈值判读, 属预期退化; 生产 T=19 语料下各年锚点真实不同, ctx 轨与全年份 _allv 锚点方能给出稳定的锚点稳健性对比。

## VAR: auth_sim_emb_allv_full

【变体差分】
本列是全年份锚点嵌入子族的 full 轨、canonical Qwen 主嵌入变体, 亦为本子族最贴近 canonical 的列。银行年度聚合文本取自 content_full (标题 prepend 加完整正文, stage 14 物化), 纳入该行当年全部留篇报道的整篇文本, 相对全年份静态政策锚点求余弦相似度。相对 ctx / ss 两轨的差分在文本轨道: full 轨保留整篇正文, 度量的是最完整的战略语义画像, 信号量最大但也最易掺入与银行战略无关的背景叙述。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。留篇门控本身即 full-only 口径 (2026-06-29): 一篇报道是否计入该行年度文本以其 full 轨 LLM 留篇判定为准, 故 full 轨的行宇宙是三轨的母集、ctx/ss 是其子集。嵌入为 Qwen3-Embedding-8B 主轨, 与 auth_sim_emb_lg_allv_full both-or-neither 严格 parity。锚点为全年份静态锚点, 相对同轨 vintage 主轨 auth_sim_emb_full 仅换锚点、构造全同, 为锚点稳健性对照。作为最贴近 canonical 的列, 本列在多数分析中充当嵌入维度的默认读数; 当它与其 vintage 主轨 auth_sim_emb_full 显著背离时, 说明该行的政策贴合度对"是否允许锚点纳入未来政策"这一构造选择敏感, 通常指向后发年份政策对早年画像的回溯性拉高, 这一差值本身即前视构造稳健性的可披露证据。须提醒的是全年份锚点含发布年份晚于 t 的政策文本, 存在轻度前视, 故本列仅作稳健性对照绝不作主结论测度; 主结论一律以同轨 vintage 列为准。当某年 vintage 锚点恰等于全年份静态锚点时源码短路复用, 本列与 vintage 列逐字节相同, 属确定性 golden-safe 行为而非缺陷。

## VAR: auth_sim_emb_allv_ss

【变体差分】
本列是全年份锚点嵌入子族的 ss 轨、canonical Qwen 主嵌入变体。银行年度聚合文本取自 content_ss (标题 prepend 加银行与金科同句共现窗, stage 14 物化), 相对全年份静态政策锚点求余弦相似度。相对 full / ctx 的差分在文本轨道: ss 轨只纳入银行实体与金融科技词在同一句 (含 ±N 句半径) 共现的最窄语境, 度量的是"银行明确谈及金科处"的战略语义与政策的贴合, 是三轨中最聚焦、信噪比最高但覆盖最窄的一轨。回退语义严格镜像 ctx: 某行某年无任何银行与金科同句共现时, content_ss 优雅退回全文正文、标记 fallback; content_ss 整体缺失时该行 ss 轨优雅跳过而不产孤儿列。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; ss 轨为 full-only 门控留篇集的 conditional-on-full 子集。嵌入为 Qwen3-Embedding-8B 主轨, 与 auth_sim_emb_lg_allv_ss both-or-neither 严格 parity。锚点为全年份静态锚点, 相对同轨 vintage 主轨 auth_sim_emb_ss 仅换锚点, 为锚点稳健性对照。因 ss 轨窗口最窄, 当某行当年谈及金科的同句共现极少时, 大量样本会走 fallback 退回全文正文, 此时 ss 列在数值上会向 full 列靠拢, 属回退语义的预期表现而非污染; 研究者若要严格利用 ss 的聚焦性, 应结合 ss_is_fallback 标记筛出真正含同句共现的样本再作解读。在早期试跑 T=2 开发面板上 ss 轨常因样本稀薄而给出接近零方差的退化读数, 生产 T=19 语料下方能体现其信噪比优势。本列同样仅作锚点稳健性对照, 主结论以同轨 vintage 列为准。

## VAR: auth_sim_emb_lg_allv_ctx

【变体差分】
本列是全年份锚点嵌入子族的 ctx 轨、_lg co-primary 嵌入变体。构造与 auth_sim_emb_allv_ctx 完全一致 (content_ctx 银行年度文本对全年份静态政策锚点求余弦), 唯一差分是嵌入引擎: 本列用 text-embedding-3-large (OpenAI/OpenLux, 3072 维), 而非主轨 Qwen3-Embedding-8B (4096 维)。二者是 co-primary 双轨: 同为主测度、互为稳健性、严格 parity, 列名 both-or-neither 双射 — 任一嵌入返回缺失即同族两列同置 NaN, 无单边孤儿。_lg 与主轨各自 just-identified 并排, 铁律禁混进同一 over-identified Hansen J。换嵌入厂商 (Google 系旧轨已退, 现主轨为阿里 Qwen、稳健轨为 OpenAI large) 会带来维度与数值的系统性差异, 正是并排双轨要暴露而非隐藏的稳健性来源。锚点为全年份静态锚点 (含未来政策), 相对同轨 vintage 主轨 auth_sim_emb_lg_ctx 仅换锚点、构造全同, 为锚点稳健性对照。轨道维度上仍是 ctx (实体上下文窗口), 与 _lg 的 full/ss 三轨各自 just-identified 并排、互为稳健性。须强调本列同时承载两条正交的稳健性: 一是相对 Qwen 主轨的换嵌入模型稳健性 (co-primary 双轨), 二是相对同轨 vintage 列的换锚点稳健性 (全年份对 vintage), 二者不可折叠进同一过度识别方程, 只能各自并列比对系数与显著性。当本列与主轨 auth_sim_emb_allv_ctx 的系数方向一致仅幅度不同时, 说明政策贴合的结论不被单一嵌入厂商的几何特性驱动; 若方向翻转则须回到余弦度量本身的效度讨论 (Steck 等 2024; You 2025)。生产实践中 _lg 轨的 3072 维与主轨 4096 维在同一余弦标度下不可直接比水平, 跨模型比较一律须先标准化系数。

## VAR: auth_sim_emb_lg_allv_full

【变体差分】
本列是全年份锚点嵌入子族的 full 轨、_lg co-primary 嵌入变体。构造与 auth_sim_emb_allv_full 完全一致 (content_full 整篇正文的银行年度聚合文本对全年份静态政策锚点求余弦), 唯一差分是嵌入引擎换为 text-embedding-3-large (3072 维), 而非主轨 Qwen3-Embedding-8B (4096 维)。本列与 auth_sim_emb_allv_full 构成 co-primary 双轨: 同为主测度、互为稳健性、严格 parity, both-or-neither 双射, 任一嵌入 None 即两列同置 NaN。_lg 与 Qwen 主轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。full 轨保留整篇正文、信号量最大, 且其留篇门控本身即 full-only 口径 (2026-06-29), 行宇宙为三轨母集。锚点为全年份静态锚点, 相对同轨 vintage 主轨 auth_sim_emb_lg_full 仅换锚点、构造全同, 为锚点稳健性对照, 绝不替换 vintage 主轨。轨道维度为 full (完整正文), 与 _lg 的 ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次。text-embedding-3-large 的对比预训练渊源见 Neelakantan 等 (2022), 与主轨 Qwen3 (Zhang 等 2025) 分属不同厂商与训练范式, 正因如此二者并排能暴露而非隐藏嵌入空间选择带来的系统性差异。本列在实务中是对 auth_sim_emb_allv_full 主轨最直接的换模型稳健性对照读数: 若两列在同一回归设定下给出方向一致的政策贴合效应, 则该效应稳健于嵌入厂商与维度的具体取值; 双轨严格 parity 保证任一嵌入返回缺失时两列同置 NaN, 不会出现单边孤儿造成的样本不对称。本列锚点含未来政策存在轻度前视, 只作稳健性对照, 主结论以同轨 vintage 列 auth_sim_emb_lg_full 为准。

## VAR: auth_sim_emb_lg_allv_ss

【变体差分】
本列是全年份锚点嵌入子族的 ss 轨、_lg co-primary 嵌入变体。构造与 auth_sim_emb_allv_ss 完全一致 (content_ss 银行与金科同句共现窗的银行年度文本对全年份静态政策锚点求余弦), 唯一差分是嵌入引擎换为 text-embedding-3-large (3072 维), 而非主轨 Qwen3-Embedding-8B (4096 维)。本列与 auth_sim_emb_allv_ss 为 co-primary 双轨: 同为主测度、互为稳健性、严格 parity, both-or-neither 双射, 任一嵌入 None 即两列同置 NaN, 无单边孤儿。_lg 与主轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。ss 轨回退语义严格镜像 ctx: 无银行与金科同句共现时 content_ss 退回全文正文并标记 fallback, content_ss 缺失时该行 ss 轨优雅跳过。ss 是三轨中最聚焦、覆盖最窄的一轨, 为 full-only 门控留篇集的 conditional-on-full 子集。锚点为全年份静态锚点, 相对同轨 vintage 主轨 auth_sim_emb_lg_ss 仅换锚点、构造全同, 为锚点稳健性对照。轨道维度为 ss (同句共现窗), 与 _lg 的 full/ctx 三轨各自 just-identified 并排、互为稳健性不分主次。本列在整个子族中定位最细: 它同时叠加了三重规格选择 (ss 最窄轨道 + _lg 换嵌入模型 + 全年份换锚点), 因而既是覆盖最窄、退化最易触发的一列, 也是检验主结论是否稳健于最严苛构造组合的极端对照。实务解读须结合 ss_is_fallback 标记, 剔除退回全文的样本后方能利用其"银行明确谈及金科处"的聚焦语义; 在早期试跑 T=2 面板上本列常近零方差, 属预期退化。与其 vintage 孪生 auth_sim_emb_lg_ss 的差值反映锚点前视敏感性, 与 canonical Qwen 的 auth_sim_emb_allv_ss 的差值反映嵌入厂商敏感性, 两条稳健性正交、禁折叠进同一过度识别 Hansen J。跨模型比较一律先标准化系数, 不比余弦水平。

<!-- rendered-citations:begin -->
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., ... Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics, 2014-2037. https://doi.org/10.18653/v1/2023.eacl-main.148
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
<!-- rendered-citations:end -->
