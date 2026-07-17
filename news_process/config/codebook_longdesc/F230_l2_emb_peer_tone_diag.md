---
family_id: F230
columns:
- emb_peer_tone_diag_lag1_ctx
- emb_peer_tone_diag_lag1_lg_ctx
- emb_peer_tone_diag_lag1_lg_ss
- emb_peer_tone_diag_lag1_ss
novelty_exempt_rationale: "该家族是 emb_peer_tone_lag1 同行语调外溢测度的 diag(对角轨)技术变体——仅改变权重矩阵 W 与语调的同轨对齐方式(W_ctx×tone_ctx / W_ss×tone_ss 替代历史 W_full 混合轨), 并非独立新构念, 其经济逻辑与测度定义已在母族(同行效应/嵌入相似度文献)及正文引文中给出依据, 无需为变体本身追加独立新颖文献。"
unit: 语调得分 (连续, 约 [-1,1]; 银行-年层面的嵌入加权同行滞后语调)
formula: "emb_peer_tone_diag_lag1_{trk} = Σ_j W_emb^{trk}(t-1)_{ij} · tone_j^{trk}(t-1); W_emb 由同轨超级文档嵌入的 cosine similarity 构造, 对角线置零 → 负值 clip 至 0 → row-stochastic 行归一化; trk ∈ {ctx, ss}, 嵌入模型 ∈ {Qwen3-Embedding-8B (MAIN), text-embedding-3-large (_lg)}"
producer: news_process/pipeline/panel/network_spillover.py ; news_process/pipeline/panel/stata_export.py
upstream:
- 14_materialize_ctx.parquet (content_ctx, content_ss, ss_is_fallback)
- 21_tone_llms.parquet (三家投票 tone 逐轨)
- 40_panel_yearly.parquet (bank-year tone 面板输入)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.18653/v1/D19-1410
  type: arxiv
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: EMNLP-IJCNLP
  pages_or_artno: 3980-3990
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"语义邻近同行的滞后语调外溢"(embedding-weighted peer tone spillover)的对角轨变体。其经济含义是: 一家银行在 t 年所处的舆论语义空间里, 与它文本描述最相似的一批同行银行, 在 t-1 年被媒体赋予的情感语调, 会通过语义邻近这一渠道对本行产生同行溢出。构造逻辑分两层: 第一层是把"谁是同行"从传统的行业代码或规模分组, 替换为由文本嵌入余弦相似度动态刻画的语义邻近矩阵 W_emb; 第二层是用这张权重矩阵去加权同行的历史语调, 得到本行所暴露的同行语调环境。数据来源是 stage 21 三家 LLM 投票得到的银行-文章级语调, 按银行×年份聚合后作为节点属性; 权重矩阵的原料则是 stage 14 物化的三轨超级文档文本 (content_ctx / content_ss), 经统一嵌入引擎编码而来。构念上它属于金融网络与同行效应文献中"内生网络 × 节点属性外溢"的一支, 与用产品描述文本构造动态同行网络的思路一脉相承, 只是把 TF-IDF 余弦换成了更深层的稠密嵌入相似度。

【方法学与计算】
计算链路见 network_spillover.py: 先按银行×年份把当年归属该行的报道文本 (docid 升序确定性拼接) 汇成超级文档, 超长文档由 embedding_engine 分块并做 token 加权 mean pooling (旧的 8000 字符前缀截断已废弃, 因为它只保留行序最先若干篇, 非代表性样本); 再调用统一引擎 embed_texts 得到每行的年度语义向量; 对同一年内各行向量两两算 cosine_similarity, 将对角线置零 (剔除自相似)、把负相似度 clip 到 0、再做 row-stochastic 行随机归一化, 得到当年的语义同行权重矩阵 W_emb(t); 最后取滞后一期做外溢乘积 emb_peer_tone = W_emb(t-1) × tone(t-1)。滞后一期是刻意的识别设计: 依据 Manski (1993) 的反射问题, 同期同行结果与本行结果互为因果、无法与情境效应分离, 用 t-1 的同行语调作暴露量可切断同期反射。本家族的"diag 对角轨"关键区别在于: 历史列 emb_peer_tone_lag1_{ctx,ss} 的权重矩阵恒取 full 轨文本 (W_full × tone_trk, 是 W 与 tone 异轨的混合), 而 diag 轨令权重矩阵与被加权语调严格同轨 (W_ctx × tone_ctx 或 W_ss × tone_ss), 即语义邻近判定与语调测量落在同一文本口径上, 消除了 W 来源与语调来源的轨道错配。ctx/ss 超级文档由 content_ctx / content_ss 原样拼接, 剔除 *_is_fallback 行且禁走 title 通道 (prepend_title 已内嵌标题, 再拼即双标题污染付费缓存)。嵌入采用 co-primary 双轨零本地模型架构: 无 _lg 后缀列走 canonical 主轨 Qwen3-Embedding-8B (硅基流动, 4096 维), _lg 列走 text-embedding-3-large (yunwu, 3072 维); 两轨同为主测度、互为稳健性、严格 parity, 余弦相似度维度无关 (由 emb.shape[1] 驱动, 4096 与 3072 绝不混算)。按 CLAUDE.md 铁律, 三轨 (full/ctx/ss)、co-primary 双轨嵌入、diag 与 legacy W-轨, 均为各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; per-W-轨独立降级 (D8, 单元内 both-or-neither, 单元间不连坐)。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算作银行金科报道只看 full 轨 LLM 判定, ctx/ss 为 conditional-on-full 的行宇宙子集, 逐轨语调在此子集上聚合。ss 轨的回退语义镜像 ctx: 当银行与金科无同句共现时 content_ss 退回全文 body 并置 ss_is_fallback=True, 拼接超级文档时这些回退行被剔除以免污染语义空间。

【文献定位】
本家族在方法上锚定三支文献。其一是嵌入驱动的文本金融测度: Jha, Liu 与 Manela (2026) 在 Review of Financial Studies 用语言嵌入方法度量金融对社会的贡献, 论证了稠密嵌入相较词袋能捕获更深层语义, 为以嵌入余弦替代 TF-IDF 构造银行语义邻近提供了顶刊层面的方法学背书; Zheng 等 (2024) 在 Journal of Management Information Systems 用词嵌入刻画金融文本情感的演化, 印证了嵌入空间承载可量化的情感邻近结构; Reimers 与 Gurevych (2019) 的 Sentence-BERT 确立了以句级/文档级稠密向量编码并以余弦相似度度量语义邻近的方法范式, 为本家族用嵌入余弦构造银行语义同行矩阵提供了工程与方法学基石 (本项目采用零本地模型的 co-primary 双轨 API 嵌入架构, 该文提供的是稠密向量相似度这一测度范式的学术依据, 而非本地模型部署路径)。其二是同行效应识别: Manski (1993) 界定的反射问题是本家族采用滞后暴露量的直接理由; Bramoullé, Djebbari 与 Fortin (2009) 证明了通过社会网络的拓扑结构 (存在未直接相连的二阶邻居) 可识别内生同行效应, 其 2020 年综述进一步系统化了网络同行效应的识别条件; Boucher 等 (2024) 在 Econometrica 提出的一般化同行效应理论, 为把语义邻近矩阵当作社会互动权重的做法给出了理论边界。其三是企业金融的同行网络外溢: Leary 与 Roberts (2014) 证明同行企业确实影响本企业财务政策, Grieser 等 (2022) 在 Journal of Financial Economics 进一步用空间计量刻画公司财务政策的网络外溢, 二者共同支撑"以同行语调环境作为解释变量"的经济逻辑。

## VAR: emb_peer_tone_diag_lag1_ctx

【变体差分】
本列是 diag 对角轨在 canonical 主嵌入 (Qwen3-Embedding-8B, 硅基流动, 4096 维)、ctx 文本轨下的实现。相对家族语义, 它锁定三处坐标: 轨道 = ctx (标题 prepend + 银行/金科实体上下文窗口文本), 嵌入模型 = MAIN 无后缀主轨, 权重-语调同轨性 = diag (W_ctx × tone_ctx)。它与历史列 emb_peer_tone_lag1_ctx 的本质差别不在语调轨 (两者语调均取 ctx), 而在权重矩阵来源: 历史列的 W 恒由 full 轨全文超级文档嵌入构造, 是 W_full × tone_ctx 的异轨混合; 本 diag 列则令语义邻近矩阵也由 ctx 超级文档构造, 使"谁是语义同行"与"同行语调如何"落在同一 ctx 文本口径, 消除轨道错配, 语义纯度更高。ctx 超级文档由 content_ctx 原样拼接、剔 *_is_fallback 行、禁 title 通道 (标题已 prepend, 再拼即双标题污染缓存)。滞后一期同样为规避 Manski (1993) 反射问题, 使本行 t 年结果对同行 t-1 年语调的回归不被同期反射污染。ctx 轨的经济定位介于 full 与 ss 之间: 它比 full 更聚焦银行/金科实体上下文、剔除无关正文噪声, 又比 ss 保留更宽的语境, 因而在语义邻近判定上兼顾覆盖与精度, 常被用作 diag 家族的首要稳健性轨。语义同行矩阵在 ctx 口径下构造意味着"相似"的判据是两行报道在实体上下文层面的表述接近, 而非全文层面的泛泛相似, 更契合银行金科议题的同行界定。本列与 _ss 轨及 _lg 孪生互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与历史 W=full 轨的关系亦为规格稳健性并排而非替代 (跨模型 rwolf 先例仅覆盖同构念替代 headline 测量, 本 W-轨族不适用, 不设 FWER 模板)。dev T=2 语料上 ctx 语调常呈零方差退化, 该列可能近似退化为常数, 属预期 (生产 T=19 正常)。

## VAR: emb_peer_tone_diag_lag1_lg_ctx

【变体差分】
本列是 emb_peer_tone_diag_lag1_ctx 的 _lg co-primary 对偶: 三处坐标中轨道 (ctx) 与权重-语调同轨性 (diag, W_ctx × tone_ctx) 完全一致, 唯一差别是嵌入模型换为 text-embedding-3-large (yunwu, 3072 维)。它并非主列的稳健性附庸, 而是与无后缀主轨严格 parity、地位对等的第二主测度: 两轨列名 both-or-neither 双射, 任一 embed 返回 None 则同族两列同置 NaN, 无单边孤儿。余弦相似度维度无关, 4096 维 Qwen 与 3072 维 large 各自在自身向量空间内构造权重矩阵, 绝不跨空间混算。经济含义与主列相同, 提供的是"换一家嵌入厂商 (阿里 Qwen ↔ OpenAI text-embedding-3-large)、语义邻近结论是否稳健"这一维度的敏感性检验。按 co-primary 铁律, 本 _lg 列与无后缀主列各自 just-identified 并排、互为稳健性、不分主次, 两 co-primary 严禁混进同一 over-identified Hansen J。per-W-轨独立降级 (D8): 若 ctx 轨嵌入不可得, 仅 ctx 单元的主/lg 两列同置 NaN, 不连坐 ss 单元。留篇门控与回退语义同 full-only 口径 (2026-06-29): 一篇报道是否算银行金科报道只看 full 轨 LLM 判定, ctx 为 conditional-on-full 的行宇宙子集, 本列语调在此子集上按 ctx 轨聚合。之所以保留 _lg 双轨而非只留一家嵌入, 是因为不同厂商的嵌入几何存在系统差异 (维度、各向异性、训练语料分布), 单一嵌入空间可能把这种模型特异性伪装成实证结论; co-primary 并列正是要证明语义邻近同行外溢的方向与显著性不被嵌入厂商选择所驱动。text-embedding-3-large 缓存键固定为 ('text-embedding-3-large', 'v1-2026-06-27-emb3large'), 与主轨缓存严格隔离。dev T=2 上的退化行为与主列同因同步。

## VAR: emb_peer_tone_diag_lag1_lg_ss

【变体差分】
本列是 diag 对角轨在 _lg 嵌入 (text-embedding-3-large, 3072 维)、ss 文本轨下的实现。三处坐标: 轨道 = ss (标题 prepend + 银行∧金科同句共现 ±N 句窗, 最严格的语义定位), 嵌入模型 = _lg co-primary, 权重-语调同轨性 = diag (W_ss × tone_ss)。它是 emb_peer_tone_diag_lag1_ss 的 _lg 对偶, 也是 emb_peer_tone_diag_lag1_lg_ctx 的 ss 轨姊妹。ss 轨的关键性质是其回退语义镜像 ctx: 当某行在某年无银行与金科同句共现时, content_ss 退回全文 body 且 ss_is_fallback=True; 构造 ss 超级文档时这些回退行被剔除, 使权重矩阵只由真正含同句共现语义的文本张成, 语义定位最窄但信噪比设计上最高。若 FINTECH_AC=None, ss 全轨优雅降级。与 ctx 轨相比, ss 牺牲文本覆盖换取语义精确, 二者互为稳健性、不分主次。与 ctx 轨相比, ss 牺牲文本覆盖换取语义精确, 二者互为稳健性、不分主次, 各自 just-identified 并排。本 _lg ss 列同时承载两个正交的稳健性维度: 相对 ss 主列它是"换嵌入厂商"的敏感性检验, 相对 lg_ctx 它是"收窄语义定位窗口"的敏感性检验; 两维度不交叉, 各自独立回答一个规格选择是否驱动结论。text-embedding-3-large (3072 维) 在自身向量空间内构造 ss 语义邻近矩阵, 与 4096 维 Qwen 空间绝不混算余弦。本列与无后缀 ss 主列 both-or-neither 双射、严格 parity, 两 co-primary 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; per-W-轨独立降级 (D8), ss 单元不可得时不连坐 ctx 单元。dev T=2 上 ss 语调普遍零方差退化, 本列多为 NaN 或常数, 属预期 (生产 T=19 恢复正常方差)。

## VAR: emb_peer_tone_diag_lag1_ss

【变体差分】
本列是 diag 对角轨在 canonical 主嵌入 (Qwen3-Embedding-8B, 4096 维)、ss 文本轨下的实现, 是全家族语义定位最窄的主测度。三处坐标: 轨道 = ss (标题 prepend + 银行∧金科严格同句共现窗), 嵌入模型 = MAIN 无后缀主轨, 权重-语调同轨性 = diag (W_ss × tone_ss)。相对家族其它列, 它同时把权重矩阵与被加权语调都压到 ss 口径: 语义同行的判定只依据银行与金科同句共现语境下的文本嵌入, 语调也只取 ss 轨聚合值, 因而刻画的是"在最贴近银行-金科议题的窄语境里, 语义邻近同行的历史语调外溢"。与历史列 emb_peer_tone_lag1_ss (W=full × tone_ss 异轨混合) 的差别正在于此: 本列的 W 亦为 ss 轨构造, 语义纯度最高但对文本量最敏感。ss 超级文档剔除 *_is_fallback 回退行、禁 title 通道; 回退语义镜像 ctx。滞后一期规避 Manski (1993) 反射问题。这一设计的代价是对文本量最敏感: 当某行某年含同句共现的报道稀少时, ss 超级文档可能过短, 权重矩阵易受个别文本主导, 稳健性弱于 ctx 轨, 故 ss 在 diag 家族中定位为最窄、最纯但最脆的稳健性轨, 与 ctx 主轨形成"精度-覆盖"权衡的两端。本列与 ctx 主列、_lg 孪生 (emb_peer_tone_diag_lag1_lg_ss) 及历史 W=full 轨, 均为各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; per-W-轨独立降级 (D8), ss 单元不可得时主/lg 两列同置 NaN 且不连坐 ctx。留篇门控遵循 full-only 口径, ss 为 conditional-on-full 子集且回退语义镜像 ctx。dev T=2 上因 ss 语调零方差, 本列常退化为 NaN 或常数, 属预期退化 (生产 T=19 正常)。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. EMNLP-IJCNLP [Preprint]. https://doi.org/10.18653/v1/D19-1410
<!-- rendered-citations:end -->
