---
family_id: F017
columns:
- auth_sim_emb_ctx
- auth_sim_emb_full
- auth_sim_emb_lg_ctx
- auth_sim_emb_lg_full
- auth_sim_emb_lg_ss
- auth_sim_emb_ss
unit: 余弦相似度 (无量纲, 理论域 [-1,1]; 权威政策语境近似落于 [0,1])
formula: "auth_sim_emb{track} = cos( E(银行年度聚合文本_track), E(权威政策 vintage 锚点文本) ); E = 嵌入编码器 (MAIN=Qwen/Qwen3-Embedding-8B 4096 维; _lg=text-embedding-3-large 3072 维); ghost-anchor 提取 = 对称相似度矩阵末列 sim[:-1,-1]"
producer: news_process/pipeline/features/policy_similarity.py::compute_authoritative_similarity (_ghost_anchor_metrics 助手) ; news_process/pipeline/panel/stata_export.py (HEURISTIC_LABELS)
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - config/authoritative_corpus.txt (权威政策语料, 按 vintage 年份切分)
  - 25_article_sbert.parquet (co-primary 嵌入引擎共享口径)
citations:
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.48550/arXiv.2401.00368
  type: arxiv
  authors: Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F.
  year: 2024
  title: "Improving text embeddings with large language models"
  venue: arXiv
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: The Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
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
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L.
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
new_dois: []
---

## CORE

【构念与来源】
本家族测度「银行年度战略画像与国家权威政策基准的语义收敛度」, 即在同一语义向量空间内, 微观银行画像文本相对宏观政策锚点的余弦贴近程度。构念动因是: 银行在金融科技转型中对国家政策的响应并非齐步走, 有的银行叙事高度贴合监管与产业政策导向 (高值), 有的则各自为政 (低值)。该家族由权威政策战略响应度模块 (policy_similarity.py::compute_authoritative_similarity) 产出, 该模块在 panel runner 步骤 7h (policy 子步) 内被调用, 隶属 stage 40 面板导出流程 (并非 stage 26; stage 26 是 article_staleness/semantic_staleness 冷启动模块, 与本家族不同源)。它是该模块 TF-IDF 字符级/词级、LDA 主题空间、语义嵌入四类方法学中的「语义嵌入」一支; 本家族六列专指嵌入支, 不含 tfidf/lda 支。数据来源为 stage 14 物化的三轨聚合文本 (content_full/content_ctx/content_ss) 与磁盘上的权威政策语料 config/authoritative_corpus.txt, 后者按发布年份 (vintage) 切分。

【方法学与计算】
计算采用「幽灵锚点 (ghost-anchor)」范式: 把当年权威政策锚点文本作为第 (N+1) 个元素挂载至该年 N 家银行文本列表末尾, 送入与 stage 25 article_sbert 绝对同构的嵌入矩阵提取器, 得到 (N+1)×(N+1) 对称余弦相似度矩阵, 取末列去尾 sim[:-1, -1] 即各银行相对政策锚点的相似度 (O(1) 同构提取, 与 banks 两两相似度共享同一编码调用, 保证口径一致)。锚点采用 vintage 口径: 年度 t 的锚点只含发布年份 ≤t 的政策文档, 前视守卫 (锚点不可用年份) 置 NaN, 杜绝用未来政策解释过去响应度的信息泄漏。嵌入编码纯走 API, 维度由 emb.shape[1] 驱动, 与具体维度无关。余弦相似度作为语义贴近算子已是文本向量对齐的标准操作化 (Liu, Cao, & Wen, 2024; Jha, Liu, & Manela, 2026), 但其可解释性对嵌入几何与频率结构敏感, 高维余弦未必等同人类语义直觉 (Steck, Ekanadham, & Kallus, 2024; You, 2025), 故本模块将其定位为对锚响应度的一致性代理而非绝对语义度量。

【文献定位】
嵌入本身承接对比预训练与大模型嵌入两条技术脉络: MAIN 轨 Qwen/Qwen3-Embedding-8B 属基础模型驱动的高维中文友好嵌入 (Zhang et al., 2025), 其大模型化训练思路与 Wang et al. (2024) 一脉; _lg 轨 text-embedding-3-large 承 OpenAI 对比预训练系 (Neelakantan et al., 2022)。两轨在通用与金融文本基准上的可比性由 MTEB 类评测框架背书 (Muennighoff, Tazi, Magne, & Reimers, 2023)。将宏观政策文本与微观主体画像嵌入同一空间做余弦对锚, 与中国政企文本相似度定价 (Liu, Cao, & Wen, 2024) 及金融文本嵌入的社会价值测度 (Jha, Liu, & Manela, 2026) 属同一测量家族。

【三轨与 co-primary 双轨口径】
本家族同时跨两个正交的规格维度。其一是三轨文本: full (标题 prepend + 全文正文)、ctx (标题 + 实体窗口)、ss (标题 + 银行∧金科同句±N 窗); ss 无同句共现时回退镜像 ctx 语义 (content_ss 退化为全文 body, 共享 n_articles 分母)。留篇门控为 full-only 口径 (2026-06-29): 是否判为一篇银行金科报道只看 full 轨, ctx/ss 为 conditional-on-full 的稳健性轨。其二是 co-primary 嵌入双轨: 无后缀 MAIN 轨 = Qwen/Qwen3-Embedding-8B (4096 维), _lg 轨 = text-embedding-3-large (3072 维); 两轨同为主测度、互为稳健性、严格 both-or-neither parity — 任一嵌入返回 None 则同族两列同置 NaN, 无单边孤儿列。铁律: 三轨之间、co-primary 两轨之间各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨或不同嵌入模型的列混进同一 over-identified Hansen J 过度识别检验。本家族嵌入支属真嵌入, 与 tfidf/lda 支不同源, 后者无 _lg 孪生。

## VAR: auth_sim_emb_full

【变体差分】
本列为 MAIN 嵌入轨 (Qwen/Qwen3-Embedding-8B, 4096 维) 在 full 文本轨上的权威政策余弦响应度, 是本家族的语义锚定基准列, 也是 tfidf/lda 三兄弟方法学中语义嵌入一支的无后缀主轨。full 轨聚合文本 = 标题 prepend + 全文正文, 对应 stage 14 物化的 content_full; 由于留篇门控为 full-only 口径 (2026-06-29), full 轨的行宇宙即当年被判为银行金科报道的全体留篇集, 是 ctx/ss 两轨的母集, 因此本列在样本覆盖上最完整, 缺失最少。取值为银行年度聚合文本嵌入与 vintage 政策锚点嵌入的余弦, vintage 口径只纳入发布年份 ≤t 的政策文档以杜绝前视泄漏, 前视守卫年份 (锚点尚不可用) 置 NaN。数值越高表示该银行当年叙事在语义上越贴合国家政策步调, 可作为战略响应度的连续代理进入回归。相对 _lg 孪生列 auth_sim_emb_lg_full, 本列走无后缀 MAIN 编码器 (4096 维), 二者严格 both-or-neither parity、互为稳健性、不分主次, 换厂商换维度互证; 相对 ctx/ss 两轨, 本列文本覆盖面最全、信息量最高, 但也最易被与政策无关的正文噪声稀释, 故 ctx/ss 提供收敛焦点后的稳健性对照。余弦作为语义贴近算子的可解释性对嵌入几何敏感 (Steck, Ekanadham, & Kallus, 2024), 故本列宜与 tfidf/lda 支交叉互证而非单点解读。铁律: 本列与 _lg 孪生及 ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: auth_sim_emb_ctx

【变体差分】
本列为 MAIN 嵌入轨 (Qwen/Qwen3-Embedding-8B, 4096 维) 在 ctx 文本轨上的权威政策余弦响应度。ctx 轨聚合文本 = 标题 prepend + 实体窗口 (content_ctx), 相对 full 轨剔除远离目标实体的正文段落, 把语义焦点收敛到银行/金科实体邻近语境, 从而降低与政策无关正文对余弦的稀释, 提供对 full 基准的稳健性对照。这一收敛设计的假设是: 银行对政策的真实响应更集中体现在直接谈及该银行金科动作的语句里, 剔除背景段落可提升信噪比。作为 conditional-on-full 轨, 其行宇宙是 full 留篇集的子集 (是否留篇仍只看 full 轨判定), per-track 列照算, 因此本列缺失率略高于 full。取值口径与 full 完全一致 (vintage 幽灵锚点余弦, 只纳发布年份 ≤t 政策文档, 前视守卫置 NaN), 唯一差分是输入文本从全文收窄至实体窗口。相对 _lg 孪生 auth_sim_emb_lg_ctx, 本列走无后缀 MAIN 编码器 (4096 维), 二者严格 both-or-neither parity, 任一嵌入 None 同置 NaN。ctx 与 full 是两条并排稳健性规格, 依据双轨即互为稳健性口径, 不以彼此余弦相关性高低决定取舍, 也不因某轨方差退化 (dev T=2 上短文本轨可能近零方差) 而废弃。本列亦有 tfidf/lda 同轨兄弟 (auth_sim_tfidf_c_ctx 等), 可交叉互证嵌入余弦是否被高维几何伪影驱动 (Steck, Ekanadham, & Kallus, 2024; You, 2025)。铁律: full/ctx/ss 三轨与 MAIN/_lg 双轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: auth_sim_emb_ss

【变体差分】
本列为 MAIN 嵌入轨 (Qwen/Qwen3-Embedding-8B, 4096 维) 在 ss 文本轨上的权威政策余弦响应度。ss (same-sentence) 轨聚合文本 = 标题 prepend + 银行∧金科同句±N 窗 (content_ss, 窗半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义最聚焦、判据最严格的一轨, 只保留银行与金科实体真正同句 (含 ±1 句邻域) 共现的语境, 意在把响应度测量锁定在最贴近银行金科主题的核心语句上。回退语义严格镜像 ctx: 当某银行年度无银行∧金科同句共现时, content_ss 优雅退化为全文 body、ss_is_fallback 置 True 并共享 n_articles 分母, 保证不产生空洞行、不无声清空。这一回退口径与 CLAUDE.md 中 ss 镜像 ctx 的语义一致, 写错即 P0。作为 conditional-on-full 轨, 是否留篇仍只看 full 轨, 行宇宙为 full 留篇集子集, 缺失率通常三轨中最高。取值口径同 full/ctx (vintage 幽灵锚点余弦, 只纳发布年份 ≤t 政策文档, 前视守卫置 NaN), 唯一差分是输入文本收窄至同句窗。相对 _lg 孪生 auth_sim_emb_lg_ss 走无后缀 MAIN 编码器 (4096 维), 严格 both-or-neither parity, 任一嵌入 None 同置 NaN。由于 ss 判据最严又叠加短文本, 本列在浅面板 (dev T=2) 上易出现近零方差或大量回退, 属预期退化而非缺陷, 生产 T=19 长面板方能充分展开其与政策核心语句的贴近信号。本列与 auth_sim_emb_full/ctx 三轨并排解读时须记住三者语义焦点递进 (全文→实体窗→同句窗), 焦点越窄越贴近银行金科主题但样本越薄。铁律: 三轨与双轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: auth_sim_emb_lg_full

【变体差分】
本列为 _lg co-primary 嵌入轨 (text-embedding-3-large, 3072 维) 在 full 文本轨上的权威政策余弦响应度, 是 auth_sim_emb_full 的严格孪生。差分仅在编码器: 本列走 OpenAI 系对比预训练嵌入谱系 (Neelakantan et al., 2022) 而非 MAIN 的 Qwen3 基础模型嵌入 (Zhang et al., 2025), 输出维度 3072 而非 4096, 由 emb.shape[1] 维度无关地驱动整条计算链, 无任何硬编码维度假设。文本轨 (标题 prepend + 全文正文, content_full)、vintage 锚点口径 (只纳发布年份 ≤t 政策文档)、幽灵锚点末列提取、前视守卫置 NaN 全部与 MAIN full 列逐字一致。二者构成 co-primary 双轨: 同为主测度、互为稳健性、不分主次, 严格 both-or-neither parity — 任一嵌入返回 None 则本列与 auth_sim_emb_full 同置 NaN, 杜绝单边孤儿列, parity 测试会捕获任何单边缺失。设立本轨的意义是把结论对嵌入厂商与向量维度的敏感性显性化: 若权威政策响应度的实证结论在 Qwen (4096 维, 阿里) 与 text-embedding-3-large (3072 维, OpenAI) 两个异构语义空间下同向, 则可排除单一嵌入几何驱动结果的疑虑, 呼应嵌入基准可比性文献 (Muennighoff, Tazi, Magne, & Reimers, 2023) 与大模型嵌入方法 (Wang et al., 2024)。本列取值越高表示银行叙事在 OpenAI 语义空间下越贴合国家政策, 与 MAIN full 列并排即构成对同一构念的双厂商测量, 是本家族最主要的一对稳健性互证。铁律: MAIN/_lg 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: auth_sim_emb_lg_ctx

【变体差分】
本列为 _lg co-primary 嵌入轨 (text-embedding-3-large, 3072 维) 在 ctx 文本轨上的权威政策余弦响应度, 是 auth_sim_emb_ctx 的严格孪生。相对 MAIN ctx 列, 唯一差分是编码器由 Qwen/Qwen3-Embedding-8B (4096 维) 换为 text-embedding-3-large (3072 维); ctx 轨聚合文本 (标题 prepend + 实体窗口, content_ctx)、vintage 锚点口径 (只纳发布年份 ≤t 政策文档)、幽灵锚点末列提取余弦、前视守卫置 NaN 与 MAIN ctx 列完全一致。本列同时承载两个正交的规格差分维度: 文本轨维度 (ctx 相对 full 收敛到实体邻近语境, 提升与政策相关的信噪比) 与嵌入轨维度 (_lg 相对 MAIN 换厂商换向量维度)。这两个维度彼此正交、不交叉, 各自作为独立稳健性梯子并排存在, 不会因组合而产生列爆炸或交叉污染。ctx 收敛焦点的信噪比提升假设在 OpenAI 空间下同样成立, 故本列与 MAIN ctx 一起验证「实体窗聚焦是否跨嵌入厂商稳定地改善政策响应度信号」。与 auth_sim_emb_ctx 构成 co-primary 双轨, 严格 both-or-neither parity, 任一嵌入 None 则本列与 MAIN 孪生同置 NaN。作为 conditional-on-full 轨, 是否留篇只看 full 轨, 行宇宙为 full 留篇集子集, 缺失率介于 full 与 ss 之间。本列与 MAIN ctx 孪生并排, 可检验 ctx 焦点下政策响应度结论是否跨嵌入厂商稳健; 与 _lg full/ss 并排, 可检验同一 OpenAI 空间下文本焦点变化的敏感性。铁律: 三轨与 co-primary 双轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 依据双轨即互为稳健性口径, 不以余弦相关性高低决定并排取舍。

## VAR: auth_sim_emb_lg_ss

【变体差分】
本列为 _lg co-primary 嵌入轨 (text-embedding-3-large, 3072 维) 在 ss 文本轨上的权威政策余弦响应度, 是 auth_sim_emb_ss 的严格孪生, 也是本家族六列中文本轨最严格、且换用 OpenAI 异构嵌入空间的一列。相对 MAIN ss 列, 唯一差分是编码器由 Qwen/Qwen3-Embedding-8B (4096 维) 换为 text-embedding-3-large (3072 维); ss 轨聚合文本 (标题 prepend + 银行∧金科同句±N 窗, content_ss)、回退语义 (无同句共现时严格镜像 ctx 退化为全文 body、ss_is_fallback=True、共享 n_articles 分母、绝不无声清空)、vintage 幽灵锚点末列余弦 (只纳发布年份 ≤t 政策文档) 与前视守卫置 NaN 口径均与 MAIN ss 列逐字一致。本列同时承载两个正交差分: ss 文本轨 (最严格同句聚焦) 与 _lg 嵌入轨 (换厂商换向量维度)。与 auth_sim_emb_ss 构成 co-primary 双轨, 严格 both-or-neither parity, 任一嵌入 None 则本列与 MAIN 孪生同置 NaN, 无单边孤儿列。作为 conditional-on-full 轨, 是否留篇只看 full 轨, 行宇宙为 full 留篇集子集, 加之 ss 判据最严, 本列缺失率通常六列中最高; dev T=2 上短聚焦文本可能出现近零方差退化属预期, 不构成废弃理由, 生产 T=19 长面板方能充分展开。本列的价值在于以最严格同句焦点叠加 OpenAI 异构嵌入空间, 提供本家族最保守的一条稳健性臂: 若权威政策响应度结论在此最窄焦点、最异构嵌入下仍同向, 则构念的稳健性最有说服力。本列与 MAIN ss 孪生跨厂商互证, 与 _lg full/ctx 跨焦点互证, 两条互证路径正交。铁律: 三轨与双轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Improving text embeddings with large language models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2401.00368
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics, 2014-2037. https://doi.org/10.18653/v1/2023.eacl-main.148
<!-- rendered-citations:end -->
