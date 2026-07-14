---
family_id: F155
columns:
- coh_emb_ctx
- coh_emb_full
- coh_emb_lg_ctx
- coh_emb_lg_full
- coh_emb_lg_ss
- coh_emb_ss
unit: 余弦相似度 (无量纲, 值域 [-1,1]; 首年与年份间隙返回 NaN)
formula: "coh_emb = cos(v_{i,t}, v_{i,t-1}); v_{i,t} = 银行 i 第 t 年聚合文本经预训练嵌入模型分段池化后的句向量; 仅当 (i, t-1) 存在时取值, 否则 NaN"
producer: news_process/pipeline/features/strategic_diff.py::_compute_emb_coherence ; news_process/pipeline/panel/stata_export.py (HEURISTIC_LABELS)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (full-only 留篇门控行宇宙)
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
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L.
  year: 2022
  title: "Text and code embeddings by contrastive pre-training"
  venue: arXiv
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3980-3990
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: Levy, O., Goldberg, Y., & Dagan, I.
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
- doi: "10.18653/v1/2025.emnlp-main.179"
  type: journal
  authors: "Tang, Y., & Yang, Y."
  year: 2025
  title: "FinMTEB: Finance Massive Text Embedding Benchmark"
  venue: "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP)"
- doi: "10.18653/v1/2024.findings-naacl.168"
  title: "Beyond Surface Similarity: Detecting Subtle Semantic Shifts in Financial Narratives"
  authors: "Liu, J., Yang, Y., & Tam, K. Y."
  year: 2024
  venue: "Findings of the Association for Computational Linguistics: NAACL 2024"
  type: "wp"
- doi: "10.3389/frai.2026.1752103"
  title: "FinTextSim: a domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  authors: "Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J."
  year: 2026
  venue: "Frontiers in Artificial Intelligence"
  type: "journal"
new_dois:
  - "10.18653/v1/2025.emnlp-main.179"
  - "10.18653/v1/2024.findings-naacl.168"
  - "10.3389/frai.2026.1752103"
---

## CORE

【构念与来源】
本家族刻画同一家银行在相邻两个年度里"对外沟通语义画像"的稳定程度, 即相邻期文本连贯性 (temporal text coherence) 的稠密语义嵌入实现。构念动机来自央行与机构沟通研究的一条主线: 当一个主体逐年发出的公开文本在语义上高度一致时, 市场理解其意图的偏差更小、信息传导更顺畅、由沟通引发的额外不确定性更低, 这一"沟通一致性降低理解偏差"的逻辑正是把年际语义连贯性作为可观测代理来刻画的动机所在。把该逻辑迁移到银行金融科技叙事上, 我们对每家银行、每个年度先聚合其被媒体报道的文本, 再用预训练语言模型把该年度画像映射到高维语义向量, 最后计算 t 年与 t-1 年两个向量的余弦相似度作为连贯性得分。得分越高, 说明该行今年的语义画像越接近去年, 沟通"叙事"越稳定; 得分越低甚至为负, 说明画像发生显著转向。该测度与情感、注意力等"内容"型测度正交: 它衡量的是画像的年际稳定性而非画像本身的好坏, 因此在收敛效度诊断里与 llm_vote_tone_full 等情感列被要求呈低相关。

【方法学与计算】
计算链路为: 上游 stage 14 物化三轨文本 (content_full / content_ctx / content_ss) → strategic_diff.py 内 _aggregate_bank_year_texts 把每个 (银行, 年份) 单元的文本聚合成一段超级文档 → _compute_emb_coherence 一次性调用统一 API 嵌入引擎, 对全部 (银行, 年份) 超级文档做分段池化 (长文本按 token 切块后池化, 复用 _embed_texts_with_chunk_pooling), 得到逐单元向量 → 对每个单元查找其上一年度 (bank, year-1) 是否存在, 存在则计算两向量余弦相似度并写入。因此本家族在样本首年以及年份出现断档 (间隙年) 时严格返回 NaN, 与 strat_fluidity 的缺失口径一致; "相邻期"严格定义为连续年度。值域方面, 嵌入余弦的数学真值域为 [-1,1] (不同于 TF-IDF/LDA 非负算子轨的 [0,1]); 实现只在落值处 clip 到 [-1,1] 作为浮点容忍 (float32 余弦可达 1+ε, ε 约 1e-7), 合法的负余弦被保留而非地板到 0, 下游 _log_coherence_diagnostics 亦按 [-1,1] 对 coh_emb* 做断言。行宇宙沿用全仓 full-only 留篇门控 (2026-06-29): 一篇报道是否计入银行年度画像取决于 full 轨是否被判为一篇银行金科报道, ctx/ss 轨为 conditional-on-full 的稳健性测度轨。

本家族是四方法连贯性 (TF-IDF char / TF-IDF word / LDA+JSD / Embedding) 中的稠密嵌入方法, 也是唯一能捕获同义替换与上下文语义的方法: TF-IDF 词袋无法识别改写, LDA 落在主题分布层, 而嵌入把文本压进连续语义空间后比对。本家族在两个正交维度上展开为六列: 三条文本轨 (full/ctx/ss) 乘以两条 co-primary 嵌入模型轨。co-primary 双轨遵循全仓铁律: 无后缀 (MAIN) 槽为 Qwen/Qwen3-Embedding-8B (硅基流动, 4096 维), _lg 槽为 text-embedding-3-large (3072 维); 两轨同为主测度、互为稳健性、严格 parity (both-or-neither: 任一嵌入失败则同族两列一并置空, 不留单边孤儿列), 实现里以 `if not coh_emb or not coh_emb_lg` 联锁清零保证。⚠ 三条文本轨与两条模型轨均属规格稳健性并排: 各自 just-identified 并排、互为稳健性不分主次, 严禁把不同轨或不同嵌入模型的列混进同一 over-identified Hansen J。ss 轨回退语义镜像 ctx: 无银行∧金科同句共现时 content_ss 退化为全文正文并标 fallback。

【文献定位】
方法谱系上, 本家族站在把"文本相似度"作为经济计量测度这一日益成熟的传统里。Jha, Liu 与 Manela (2026, Review of Financial Studies) 系统展示了用语言嵌入把金融文本映射到语义空间、再以向量几何量化构念的路径, 与本测度以银行年度画像向量做年际比对同源; 该顶刊文亦是本项目 benefit 家族的嵌入方法锚。Cohen, Malloy 与 Nguyen (2020, Journal of Finance) 的"懒惰价格"研究用相邻年度公司文件的文本相似度度量披露变化并预测收益, 与本家族"相邻期语义连贯性"在构念上高度平行——都把年际文本变动本身当作有信息含量的信号。Zheng, Ng, Zheng 与 Tam (2024, Journal of Management Information Systems) 以词嵌入刻画金融文本情感演化, 印证嵌入空间足以承载金融叙事的时序动态。方法本体上, Reimers 与 Gurevych (2019) 的 Sentence-BERT 奠定了把整段文本压成可比句向量的范式, Levy, Goldberg 与 Dagan (2015) 厘清了分布式相似度与嵌入的关系, 而本项目采用的 Qwen3 嵌入 (Zhang et al. 2025) 与 OpenAI 对比预训练嵌入 (Neelakantan et al. 2022) 分别是 MAIN 与 _lg 两条 co-primary 轨的模型来源。Tang 与 Yang (2025, 2025年经验方法自然语言处理会议 EMNLP) 构建金融领域文本嵌入大规模基准, 系统评估通用与金融专用嵌入模型在语义相似度任务上的表现差异, 为本家族选用通用预训练嵌入模型 (Qwen3/text-embedding-3-large) 计算银行年度画像相邻期余弦连贯性提供了嵌入模型选型与金融文本适配性的方法学参照。⚠ 已知局限: 余弦相似度作为"语义接近"的代理并非无争议——Steck, Ekanadham 与 Kallus (2024) 指出嵌入余弦在特定训练与正则条件下未必如实反映语义相似度, 因此本家族刻意与 TF-IDF/LDA 三条非嵌入连贯性方法并置作收敛效度交叉验证, 而非单点依赖嵌入余弦; 这也是保留 co-primary 双模型互证的动机之一。Liu, Yang 与 Tam (2024, 计算语言学协会发现: NAACL 2024) 提出 Financial-STS 任务, 衡量同一公司不同期财报叙事间的细微语义偏移, 发现通用预训练嵌入模型难以捕获这种年际语义变化, 与本家族用嵌入余弦刻画银行年际语义连贯性的构念直接平行。Jehnen, Villalba-Díez 与 Ordieres-Meré (2026, 人工智能前沿) 针对金融文本套话噪声与专业术语稀释语义重合的问题微调领域专用句向量模型, 显著提升同主题文本的簇内相似度, 为本家族选用通用预训练嵌入而非领域微调模型计算银行年度画像连贯性提供了对照参照。

## VAR: coh_emb_full

【变体差分】
本列是家族的 canonical 连贯性列: MAIN 嵌入模型 (Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动) 在 full 文本轨上算出的相邻期余弦连贯性。full 轨 = 标题 prepend 后拼接全文正文 (content_full), 即最完整的银行年度语义画像, 涵盖报道正文的全部上下文, 因此是三轨中信息量最大、最接近"整体叙事"的口径。full 轨也是全仓留篇门控的判定轨: 一篇报道是否计入某银行的年度画像取决于该报道 full 轨是否被判为一篇银行金科报道, 故 full 连贯性的行宇宙就是留篇总集本身, 而 ctx/ss 两轨是其子集上的 conditional-on-full 稳健性测度轨。stata_export 标签写作 "Temporal Coherence Emb (full) (co-primary: Qwen/Qwen3-Embedding-8B)"; 注意 full 轨在本嵌入族命名上带 _full 后缀 (与 strat_diff_n5_emb 等裸名 full 列的历史命名约定不同, 后者 full 为裸名)。取值口径同家族: 首年与间隙年严格 NaN (相邻期严格定义为连续年度 year_t 与 year_{t-1}), 值域 [-1,1], 合法负余弦保留不删失。作为 canonical 列, 它与 coh_emb_ctx / coh_emb_ss (同模型不同文本轨) 及 coh_emb_lg_full (同文本轨不同嵌入模型) 三者互为稳健性、各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。相较另三条非嵌入连贯性 (coh_tfidf_c_full / coh_tfidf_w_full / coh_lda_full), 本列是唯一能识别同义改写与上下文语义的方法, 是四方法收敛效度矩阵里的稠密语义顶点; 四方法在诊断日志里被要求大致同向, 若四者一致则连贯性结论可信, 而本列与情感列被要求呈低相关以确认其正交性。

## VAR: coh_emb_ctx

【变体差分】
本列与 canonical 的唯一差分在文本轨: 采用 ctx 轨 (content_ctx) 而非 full。ctx 轨 = 标题 prepend 后拼接实体上下文窗口, 即仅保留银行/金科实体附近的文本片段, 剔除与目标实体无关的远端段落, 因此得到的是"聚焦银行金科议题"的年度语义画像, 相较 full 轨的整体叙事更贴近核心议题、噪声更少但覆盖更窄。嵌入模型仍为 MAIN 的 Qwen/Qwen3-Embedding-8B (4096 维), 计算公式、缺失口径 (首年/间隙年 NaN)、值域 [-1,1]、负余弦保留均与 canonical 完全一致。stata_export 标签为 "Temporal Coherence Emb (ctx) (co-primary: Qwen/Qwen3-Embedding-8B)"。ctx 轨是 full-only 留篇门控下的 conditional-on-full 稳健性测度轨: 行宇宙是 full 留篇集的子集, per-track 列照算。本列与 coh_emb_full / coh_emb_ss 三轨互为稳健性、不分主次、各自 just-identified 并排, 禁混同一 over-identified Hansen J。其存在价值在于检验连贯性结论是否受文本窗口选择驱动——若聚焦实体窗口后连贯性排序与 full 轨一致, 说明结论稳健于"整体叙事 vs 议题聚焦"的口径切换。ctx 轨的判定不对称口径继承自 stage 14 物化: 银行侧采用否定加短名过滤, 金科侧采用裸 AC 1506 词匹配, 由此界定"实体上下文窗口"的边界。由于 ctx 剔除了与银行金科议题无关的远端段落, 其年度画像的语义方差通常低于 full 轨, 相邻期余弦可能更高也更稳定; 但当某年报道极少或窗口内文本稀疏时, ctx 画像更易受个别报道主导, 因此 ctx 与 full 的差异本身即是"叙事宽窄"敏感性的诊断量。本列的 co-primary 嵌入对偶是 coh_emb_lg_ctx (换 text-embedding-3-large), 二者严格 parity、both-or-neither 联锁, 亦互为稳健性而非主从。

## VAR: coh_emb_ss

【变体差分】
本列与 canonical 的差分同样在文本轨: 采用 ss 轨 (content_ss), 即最严格的"银行∧金科同句共现"口径。ss 轨 = 标题 prepend 后拼接银行与金融科技实体落在同一句子 (±N 句窗, config filtering.yaml context_window.ss_sentence_radius 默认 1) 内的片段, 是三轨中语义最聚焦、最直接刻画"银行与金科被同句谈论"的画像。关键回退语义 (镜像 ctx): 当某银行年度不存在银行∧金科同句共现时, content_ss 退化为全文正文并置 ss_is_fallback=True, 与 ctx 的 fallback 机制对称, 共享 n_articles 分母。嵌入模型仍为 MAIN 的 Qwen/Qwen3-Embedding-8B (4096 维), 公式与缺失/值域口径同 canonical (首年/间隙年 NaN, [-1,1], 负余弦保留)。标签为 "Temporal Coherence Emb (ss) (co-primary: Qwen/Qwen3-Embedding-8B)"。本列与 coh_emb_full / coh_emb_ctx 三轨互为稳健性、各自 just-identified 并排, 禁混同一 over-identified Hansen J。因 ss 轨在开发期 T=2 短面板上信息更稀疏, 其连贯性可能更多依赖回退全文, 生产 T=18 语料上聚焦效果才充分显现。需强调 ss 的同句共现判据与 stage 13 上游共现硬过滤不是同一口径: stage 13 用 ±1 句窗的 has_bank_fintech_cooccurrence_within_radius 做丢行硬过滤, 而 ss 轨文本用严格同句的 extract_bank_fintech_cooccurrence 物化, 二者禁互相复用。ss 因语义最聚焦, 一旦某年确有充分的银行金科同句报道, 其画像最能剔除泛化叙事噪声、直指"银行与金科被同句谈论"这一核心构念, 相邻期连贯性因而最能反映银行金科叙事本身的年际稳定性; 反之高 fallback 比例年份的 ss 连贯性会向 full 轨收敛。本列的 co-primary 嵌入对偶是 coh_emb_lg_ss, 严格 parity、both-or-neither、互为稳健性不分主次。

## VAR: coh_emb_lg_full

【变体差分】
本列是 canonical (coh_emb_full) 的 co-primary 嵌入对偶: 同为 full 文本轨, 但嵌入模型换成 _lg 槽的 text-embedding-3-large (OpenAI/yunwu, 3072 维) 而非 MAIN 的 Qwen 4096 维。两轨严格 parity、同为主测度、互为稳健性: both-or-neither 联锁保证 coh_emb_full 与 coh_emb_lg_full 任一嵌入失败则同族两列一并置空, 不留单边孤儿。计算逻辑、full 轨文本口径 (标题 prepend + 全文正文)、缺失口径 (首年/间隙年 NaN)、值域 [-1,1] 与负余弦保留均与 MAIN 完全一致, 唯一区别是喂给 _compute_emb_coherence 的 spec 参数指向 _LARGE_SPEC (缓存键 ('text-embedding-3-large','v1-2026-06-27-emb3large'))。stata_export 标签为 "Temporal Coherence Emb (full) (co-primary: Qwen/Qwen3-Embedding-8B)" 家族下的 _lg 派生条目 (由 _lg 派生循环自动生成)。⚠ 铁律: 本列与 coh_emb_full 各自 just-identified 并排, 二者是不同厂商、不同维度的语义空间实现, 属对等互证 (严禁 "robustness check" 单向措辞), 严禁把两条 co-primary 嵌入混进同一 over-identified Hansen J。引擎层面, _compute_emb_coherence 通过 spec 参数复用同一套分段池化与余弦计算逻辑, 维度由 emb.shape[1] 驱动 (维度无关), 因此 4096 维与 3072 维两轨走完全一致的算子, 唯一变量是底层语义空间。both-or-neither parity 在 full 轨内独立成立: 若 text-embedding-3-large 与 Qwen 任一嵌入返回空, 则 coh_emb_full 与 coh_emb_lg_full 一并置空, 杜绝单边孤儿列。text-embedding-3-large 走 OpenAI/yunwu 端点, 其模型谱系可追至 Neelakantan et al. (2022) 的对比预训练嵌入。本列价值在于证明连贯性结论不被单一嵌入厂商/维度驱动: 若 Qwen 与 text-embedding-3-large 两个独立语义空间给出一致的银行连贯性排序, 则该测度对嵌入实现选择稳健, 这正是 co-primary 双轨设计的核心识别目的。

## VAR: coh_emb_lg_ctx

【变体差分】
本列是 coh_emb_ctx 的 co-primary 嵌入对偶, 在两个维度上同时区别于 canonical: 文本轨 = ctx (标题 prepend + 实体上下文窗口, content_ctx), 嵌入模型 = _lg 的 text-embedding-3-large (3072 维)。相对 coh_emb_lg_full 仅文本轨由 full 收窄到实体窗口; 相对 coh_emb_ctx 仅嵌入模型由 Qwen 换成 text-embedding-3-large。both-or-neither parity 在 ctx 轨内独立成立: coh_emb_ctx 与 coh_emb_lg_ctx 任一失败则该轨两列同置空。计算公式、缺失口径 (首年/间隙年 NaN)、值域 [-1,1]、负余弦保留、full-only 门控下 conditional-on-full 的行宇宙口径均与家族一致, spec 指向 _LARGE_SPEC。stata_export 标签为 "Temporal Coherence Emb (ctx)" 的 _lg 派生条目。⚠ 本列与 coh_emb_ctx (同轨不同模型) 及 coh_emb_lg_full / coh_emb_lg_ss (同模型不同轨) 均互为稳健性、各自 just-identified 并排, 禁混同一 over-identified Hansen J。它同时检验连贯性结论对"嵌入厂商"与"文本窗口"两重选择的稳健性, 是六列矩阵里 ctx×_lg 的交叉格。需注意两重差分是正交的: 文本轨 (full/ctx/ss) 决定喂入嵌入模型的文本口径, 嵌入模型轨 (Qwen/_lg) 决定语义空间, 二者不交叉、不合并; 六列因而构成 3×2 的稳健性网格, 每一格都是一个 just-identified 的独立测度。行宇宙沿用 full-only 门控, ctx 轨为 conditional-on-full 子集, 缺失口径 (首年/间隙年 NaN)、值域 [-1,1]、负余弦保留均与家族一致。若 ctx×_lg 与 ctx×Qwen 一致, 说明在实体窗口口径下换嵌入厂商不改结论; 若 ctx×_lg 与 full×_lg 一致, 说明在 text-embedding-3-large 空间下换文本窗口不改结论——两条对照分别锁定一个维度, 是本交叉格的诊断意义所在。

## VAR: coh_emb_lg_ss

【变体差分】
本列是 coh_emb_ss 的 co-primary 嵌入对偶, 也是六列中语义最聚焦且嵌入厂商为 _lg 的交叉格: 文本轨 = ss (银行∧金科同句共现 ±N 句窗, content_ss, 无共现时回退全文正文并置 ss_is_fallback=True, 镜像 ctx 回退语义并共享 n_articles 分母), 嵌入模型 = text-embedding-3-large (3072 维)。相对 coh_emb_lg_full/ctx 文本轨进一步收窄到同句共现; 相对 coh_emb_ss 仅嵌入模型由 Qwen 换成 text-embedding-3-large。both-or-neither parity 在 ss 轨内独立成立: coh_emb_ss 与 coh_emb_lg_ss 任一嵌入失败则同置空。计算公式、缺失口径 (首年/间隙年严格 NaN)、值域 [-1,1] 与负余弦保留均与家族一致, spec 指向 _LARGE_SPEC (缓存键 ('text-embedding-3-large','v1-2026-06-27-emb3large'))。stata_export 标签为 "Temporal Coherence Emb (ss)" 的 _lg 派生条目。⚠ 本列与 coh_emb_ss (同轨不同模型)、coh_emb_lg_full / coh_emb_lg_ctx (同模型不同轨) 互为稳健性、各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。在开发期 T=2 短面板上, ss×_lg 因文本稀疏叠加年际相邻期要求, 取值可能高度依赖回退全文, 生产 T=18 上聚焦口径方充分体现。作为六列稳健性网格里语义最聚焦且嵌入厂商为 OpenAI 系的一格, 本列与 coh_emb_ss (锁 ss 轨换嵌入厂商) 及 coh_emb_lg_full / coh_emb_lg_ctx (锁 _lg 换文本窗口) 构成两条正交对照: 前者检验"同句共现口径下换 Qwen 为 text-embedding-3-large 是否改结论", 后者检验"text-embedding-3-large 空间下窗口从整体收窄到同句是否改结论"。both-or-neither parity 保证若 text-embedding-3-large 在 ss 轨嵌入失败, 则 coh_emb_ss 与 coh_emb_lg_ss 一并置空, 不留单边孤儿。其余口径 (spec 指向 _LARGE_SPEC、相邻期严格连续年度、值域 [-1,1]、负余弦保留、full-only 门控下 conditional-on-full 行宇宙) 均与家族严格一致, 仅在文本轨与嵌入模型两处与 canonical 差分。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 3980-3990. https://doi.org/10.18653/v1/D19-1410
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding Benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP). https://doi.org/10.18653/v1/2025.emnlp-main.179
Liu, J., Yang, Y., & Tam, K. Y. (2024). Beyond Surface Similarity: Detecting Subtle Semantic Shifts in Financial Narratives. Findings of the Association for Computational Linguistics: NAACL 2024 [Working Paper]. https://doi.org/10.18653/v1/2024.findings-naacl.168
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: a domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2026.1752103
<!-- rendered-citations:end -->
