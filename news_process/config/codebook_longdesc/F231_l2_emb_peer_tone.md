---
family_id: F231
columns:
- emb_peer_tone_lag1_ctx
- emb_peer_tone_lag1_full
- emb_peer_tone_lag1_lg_ctx
- emb_peer_tone_lag1_lg_full
- emb_peer_tone_lag1_lg_ss
- emb_peer_tone_lag1_ss
unit: 语调得分 (连续, 有界于 [-1,1]; bank-year 面板列, 相似度加权同行均值)
formula: "emb_peer_tone_lag1{_lg}{_trk}(i,t) = Σ_j W_emb(i,j; t-1)·1{tone_j 观测}·llm_vote_tone_{trk}(j,t-1) / Σ_j W_emb(i,j; t-1)·1{tone_j 观测}; 其中 W_emb = row_stochastic_normalize(clip(cosine(E_i, E_j), 0, ·)), 对角线置零; E_i = 银行 i 在 t-1 年新闻超级文档 (标题+正文, docid 升序确定性拼接) 的嵌入向量 (MAIN=Qwen3-Embedding-8B 4096 维 / _lg=text-embedding-3-large 3072 维, 分块 token 加权 mean pooling); 分母=0 (无观测 tone 同行) → NaN"
producer: news_process/pipeline/panel/network_spillover.py::compute_embedding_peer_network (单遍内核 = _compute_embedding_peer_network_pass, w_track='full'; Stata 标签见 pipeline/panel/stata_export.py::HEURISTIC_LABELS)
upstream:
- "40_article_bank_level (df_exploded 文章级展开帧: target_bank/year/标题/内容)"
- 21_tone_llms → panel 列 llm_vote_tone_{full,ctx,ss} (三家 LLM 多数投票共识, t-1 年取值)
- data/processed/_llm_cache.db (嵌入 API 缓存; NEWS_PROCESS_LLM_OFFLINE=1 下 miss→raise)
- config/features.yaml::embedding_api (MAIN spec) 与 embedding_large (_lg spec)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: The Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: Article 112803
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.18653/v1/2025.emnlp-main.179
  type: journal
  authors: Tang, Y., & Yang, Y.
  year: 2025
  title: "FinMTEB: Finance Massive Text Embedding Benchmark"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 3620-3638
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1371/journal.pone.0327421
  type: journal
  authors: Amancio, D. R., Machicao, J., & Quispe, L. V. C.
  year: 2025
  title: "Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis"
  venue: PLOS ONE
  vol: 20
  issue: 7
  pages_or_artno: Article e0327421
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.3982/ECTA21048
  type: journal
  authors: Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y.
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: 132
  issue: 7
  pages_or_artno: 2274-2303
- doi: 10.48550/arXiv.2401.00368
  type: arxiv
  authors: Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F.
  year: 2024
  title: "Improving text embeddings with large language models"
  venue: arXiv
- doi: 10.18653/v1/2023.eacl-main.148
  type: journal
  authors: Muennighoff, N., Tazi, N., Magne, L., & Reimers, N.
  year: 2023
  title: "MTEB: Massive text embedding benchmark"
  venue: Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics
  pages_or_artno: 2014-2037
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoulle, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., ... Weng, L.
  year: 2022
  title: "Text and code embeddings by contrastive pre-training"
  venue: arXiv
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3980-3990
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoulle, Y., Djebbari, H., & Fortin, B.
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
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1186/s40854-024-00675-7"
  title: "Investor sentiment networks: mapping connectedness in DJIA stocks"
  authors: "Nyakurukwa, K., & Seetharam, Y."
  year: 2025
  venue: "Financial Innovation"
  type: "journal"
- doi: "10.1145/3604237.3626862"
  title: "Modeling Momentum Spillover with Economic Links Discovered from Financial Documents"
  authors: "Chung, A., & Tanaka-Ishii, K."
  year: 2023
  venue: "Proceedings of the 4th ACM International Conference on AI in Finance (ICAIF '23)"
  type: "wp"
new_dois:
- 10.1086/688176
- "10.1186/s40854-024-00675-7"
- "10.1145/3604237.3626862"
---

## CORE

【构念与来源】
本家族六列共享同一个构念: 基于嵌入向量文本相似度网络加权的滞后同业媒体语调 (embedding-weighted lagged peer tone), 直观含义是"与银行 i 在新闻文本空间中最相近的其他银行, 在上一年被媒体报道时的平均情感语调"。用大白话说: 每家银行每年被媒体报道的内容, 拼成一份该行当年的新闻大文档; 两家银行的大文档在语义上越相似, 说明它们被媒体谈论的业务话题、经营处境越接近, 就越应被视作彼此的"文本同业"; 本测度把这种相似度当作权重, 对上一年各文本同业的媒体语调做加权平均, 得到银行 i 面对的滞后同业情感环境。构念动机来自公司金融的同伴效应文献: Leary 与 Roberts (2014) 证明企业融资政策显著响应同伴企业的行为而非仅响应自身基本面; Grieser 等 (2022) 进一步在网络计量框架下识别出公司财务政策沿经济网络的溢出效应; Fang 等 (2024) 则以中国银行业为对象, 证明媒体情感通过存款稳定性渠道影响银行系统性风险, 且该渠道存在跨行传染。因此在以银行媒体语调为核心处理变量的回归中, 若不控制同业情感环境, 银行自身语调的系数会混入行业性情绪波动与同业模仿的成分; 本家族即为此目的构建的网络溢出控制变量, 其中 emb_peer_tone_lag1_full 被列为类别6 网络溢出的 headline 列, emb_peer_tone_lag1_lg_full 为其 co-primary 对偶 (2026-07-10 签核扩围为 core)。网络的定义方式承袭 Hoberg 与 Phillips (2016) 的开创性做法: 该文用上市公司产品描述文本的相似度构建随时间演化的产品市场网络, 证明文本网络比 SIC/NAICS 等固定行业分类更能刻画真实的竞争邻近关系。本模块将其中的 TF-IDF 词袋余弦升级为深度嵌入向量余弦: 句向量表示的谱系起自 Reimers 与 Gurevych (2019) 的 Sentence-BERT, 其后以对比学习训练的大模型嵌入在 MTEB 基准 (Muennighoff 等, 2023) 与金融专域基准 FinMTEB (Tang 与 Yang, 2025) 上系统性超越词袋与早期句向量; 本仓生产口径的 canonical 嵌入模型即 Qwen3-Embedding (Zhang 等, 2025)。以嵌入测度经济构念的路线在金融学已获顶刊背书: Jha、Liu 与 Manela (2026) 用语言嵌入测度"金融是否有益社会"的话语立场, Zheng 等 (2024) 用词嵌入刻画金融文本中的情感演化并证明其增量预测力。语调侧的输入为本仓 stage 21 的三家 LLM 多数投票共识 llm_vote_tone, 取值有界于 [-1,1]; 由于权重行随机且非负、并按观测同行重归一, 本家族输出同样有界于 [-1,1], 单位为无量纲语调得分。取值解读: 越接近 1 表示该行的文本近邻同业在上一年被媒体以正面语调报道为主, 越接近 -1 表示近邻同业上年处在负面舆论环境中, 0 附近表示近邻同业语调正负相抵或整体中性; 由于加权对象是同业各自的年度均值语调而非逐篇打分, 本列的截面方差通常小于银行自身语调列 — 加权平均天然压缩极端值, 这是构造使然而非信息缺失。家族六列沿两条正交维度展开: 嵌入模型维 (无 _lg 中缀 = canonical Qwen 轨, 有 _lg = text-embedding-3-large 协主轨) 与语调轨道维 (_full/_ctx/_ss 三轨), 二乘三恰为六列; 家族键 l2_emb_peer_tone 中的 l2 标记其面板层级 (滞后网络控制), 全部六列由同一单遍内核在 w_track='full' 下产出, 与 diag 对角族 (w_track='ctx'/'ss') 分属不同家族。

【方法学与计算】
计算在 pipeline/panel/network_spillover.py 的步骤 7h-emb 完成, 单遍内核为 _compute_embedding_peer_network_pass, 本家族六列全部出自 w_track='full' 的两遍 (MAIN 与 _lg 各一遍)。流程分五步。第一步, 对每个观测年 t, 取滞后年 t-1 的文章级展开帧 df_exploded, 按 target_bank 分组, 把该行该年全部报道的标题与正文 (原始"标题"+"内容"列, 非 stage 14 物化文本) 以 docid 升序确定性排序后拼接成一份 bank-year 超级文档; 排序键缺 docid 时退用日期/标题, 保证拼接顺序不随上游行序漂移。第二步, 完整超级文档交统一嵌入引擎编码: 引擎按 cl100k 词表以 8191 token 上限切块, 逐块嵌入后做逐块 L2 归一的 token 加权 mean pooling; 这里刻意移除了历史实现的 8000 字符前缀截断 (fix omni-g-net-spill-02), 因为前缀截断只保留行序最先若干篇文章, 是非代表性样本。第三步, 每个嵌入 spec 用自己的模型独立编码自己的文本: MAIN spec 为 Qwen/Qwen3-Embedding-8B (硅基流动, 4096 维), _lg spec 为 text-embedding-3-large (yunwu, 3072 维); 余弦相似度维度无关, 两轨向量绝不混算, 维度由返回矩阵形状驱动。第四步, 对同年全部 n 家有文本银行的嵌入矩阵计算两两余弦相似度, 对角线置零 (自身不算同行); 再把负余弦 clip 为 0 (fix omni-g-net-spill-04) 后做行随机归一得到权重矩阵 W_emb — 若不 clip, 含负项的行做行和归一会产生负"权重", 加权均值语义被破坏, 行和分母甚至可被负项侵蚀至非正而静默产出 NaN 或符号翻转; clip 发生时留 loud 告警披露。第五步, 令滞后同业语调等于 W_emb(t-1) 与 tone(t-1) 的矩阵乘积, tone 取面板滞后年的 llm_vote_tone 列。此处有一个承重的缺失值口径 (fix NSP-1): 对缺 tone 的同行不做 fillna(0), 而是把它们同时从分子与分母中剔除 — 分母改为观测 tone 同行的权重和, 并据此重归一; 分母为 0 (该行无任何观测 tone 的同行) 时置 NaN。旧 fillna(0) 口径会把伪零注入分子而权重仍留在行和为 1 的分母里, 在生产 T=19 全量下 (缺 tone 同行也有真实新闻与权重) 使加权均值系统性向 0 衰减。滞后年无数据、当年有文本银行不足 2 家、或该年嵌入 miss/失败时整年跳过 (该年该列 NaN), miss 年份数在轨级汇总 loud 告警。嵌入调用经 data/processed/_llm_cache.db 缓存穿透, 缓存命中即零成本; NEWS_PROCESS_LLM_OFFLINE=1 时 miss 直接 raise 而非调 API, 保证离线可复现。语调输入侧须与全仓留篇门控口径一致: 自 2026-06-29 起, 一篇文章是否计为"银行金科报道"只看 llm_verified_full, ctx/ss 是 conditional-on-full 的测度轨, 其行宇宙为 full 留篇集的子集; 因此本家族 ctx/ss 后缀列的语调分量继承该门控。降级语义分两层: 嵌入模型层, MAIN 与 _lg 在 full-W 单元内 both-or-neither — 任一 spec 缺结果则本单元两族列同置 NaN, 不留单边孤儿列; W-轨单元层, full 单元失败不连坐 diag 单元 (per-W-轨独立降级, D8), 各单元独立尝试。补充两点承重细节。其一, 行随机归一的经济含义: 每行权重和为 1, 使输出是同行语调的凸组合而非规模量, 银行被多少家同业"包围"不改变量纲, 改变的只是权重在同行间的分配 — 报道话题越独特的银行, 其权重分布越均匀 (近邻不突出), 话题越同质的银行权重越向少数高相似同业集中。其二, 与 sim_mean 伴生列的关系: 同一遍计算顺手产出 bank_emb_sim_mean_lag1 (未 clip 真实余弦的去对角均值), 二者共享 sim_matrix 但语义正交 — sim_mean 是"我有多典型" (网络密度/位置), 本家族是"我的近邻在说什么" (加权语调水平); 回归中二者可同时进入, 分别吸收位置效应与环境效应。成本与播种口径: 每个 bank-year 超级文档 × 每个 spec 是一次付费嵌入调用 (超长文档分块则多次), 全部经缓存穿透, 生产 T=19 的播种费用按生产语料实测重估 (播种状态为 DEFERRED); 开发盘 T=2 下仅 2018 年存在滞后年 2017, 本家族有效值天然只覆盖单一年份截面, 属预期而非缺陷。

【文献定位】
本测度处在三支文献的交汇处。其一是文本网络文献: Hoberg 与 Phillips (2016) 确立了"以文本相似度内生定义同业网络"的范式, 本模块的贡献性替换是以大模型嵌入余弦取代 TF-IDF 余弦, 以捕获同义替换、话题级邻近等词面不重叠的深层语义关系; Rodriguez 与 Spirling (2022) 对嵌入方法在应用研究中"何时有效、何时失效"的系统评估为这一替换提供方法论边界, Amancio 等 (2025) 的近作亦证明嵌入可在统计意义上增强共现网络的结构信号。其二是同伴效应与网络计量文献: Manski (1993) 的反射问题指出同期同伴均值回归无法区分内生效应、外生 (情境) 效应与相关效应; Bramoulle、Djebbari 与 Fortin (2009) 证明在网络非完全传递 (存在朋友的朋友非朋友) 时可借网络结构识别内生同伴效应, Bramoulle 等 (2020) 与 Boucher 等 (2024) 分别给出该识别路线的综述与一般化理论。本测度显式采用 Manski (1993) 的滞后规避策略: W 与 tone 双双取 t-1, 使同期反射在构造层即被切断 — 注意是双滞后而非仅语调滞后, 网络本身也随文本年度重建, 避免"用未来的相似度加权过去的语调"这类时间口径错配; 代价是网络与语调共享同一滞后年信息集, 相关效应问题依旧 (见识别策略定位段)。其三是金融文本情感文献: Zheng 等 (2024) 证明嵌入空间中的情感演化信号对市场结果有预测内容, Aksoy-Yurdagul 等 (2026) 证明新闻情感存在跨期持续性 — 这正是滞后一期的同业语调仍具信息量、值得作为控制变量纳入的经验前提; Fang 等 (2024) 提供中国银行业媒体情感溢出的直接场景证据。嵌入模型侧的两条技术谱系恰好对应本家族的两条 co-primary 轨: canonical 轨的 Qwen3-Embedding (Zhang 等, 2025) 属"以大语言模型为底座训练嵌入"的路线, 其方法论前身见 Wang 等 (2024) 以大模型合成数据改进文本嵌入的工作; _lg 轨的 text-embedding-3-large 属对比预训练路线, 谱系起自 Neelakantan 等 (2022) 的文本与代码对比嵌入。两轨在训练数据、目标函数、参数规模与厂商上全面异质, 这正是把它们并置为互检双轨的价值所在。基准评估侧, Muennighoff 等 (2023) 的 MTEB 提供通用排名, Tang 与 Yang (2025) 的 FinMTEB 证明金融专域表现与通用排名并不完全同序 — 这一发现直接支持本仓"不押注单一模型、双轨并行"的设计。Steck 等 (2024) 对"嵌入余弦是否真的度量相似"的批判性分析则构成本测度已知局限的一部分, 见下文。Nyakurukwa 与 Seetharam (2025, Financial Innovation) 构建投资者情感网络刻画道琼斯成分股间的情感连通性与非对称传染, 为本家族"文本相似度加权同业情感溢出"构念提供情感网络方法论的最新期刊佐证。Chung 与 Tanaka-Ishii (2023, Proceedings of the 4th ACM International Conference on AI in Finance) 从财务文档 (年报/电话会议记录) 挖掘公司间经济联系网络并用图注意力网络建模动量溢出, 证明文档衍生网络优于传统行业分类, 呼应本家族以嵌入相似度替代固定行业分类构建同业网络的设计动机。

【识别策略定位】
本家族在识别链条中的角色定位是控制变量而非工具变量: 它吸收"同业情感环境"这一潜在混杂通道, 使银行自身语调 (或其他处理变量) 的系数不再搭载行业性情绪波动的便车。按 Manski (1993) 的经典三分, 同伴关联可来自内生效应 (同业语调直接影响本行结果)、情境效应 (同业特征影响本行结果) 与相关效应 (共同环境使彼此相似); 作为控制变量使用时无须区分三者 — 只要该列吸收了三种来源共同张成的混杂空间, 主处理变量的系数即得净化, 这也是它比"识别因果同伴效应"这一更强目标对假设要求宽松得多的原因。构造层的滞后一期只切断同期反射, 并不能排除相关效应 — 共同冲击若有持续性, 仍会同时驱动 t-1 年同业语调与 t 年结果; 因此使用建议是与年份固定效应 (吸收全行业共同冲击) 及银行固定效应联用, 并把本列与同族 industry_neg_shock_lag1 等等权 LOO 测度并列为规格稳健性。若研究目标是识别因果性同伴效应本身而非仅控制, 应转用本仓 IV 扩展族: 同组 leave-one-out 均值工具、广义 Bartik/shift-share 工具 (设计与诊断见 Borusyak、Hull 与 Jaravel, 2025) 与媒体来源 house-style 暴露工具是独立的列族与 2SLS 模板; granular IV (Gabaix 与 Koijen, 2024) 与网络结构识别 (Bramoulle 等, 2009) 是进一步的可选路线。口径铁律必须复述: 本家族横跨两条正交的稳健性维度 — 情感三轨 (full/ctx/ss) 与 co-primary 双轨嵌入 (canonical Qwen 与 _lg text-embedding-3-large), 两维度上的各变体均为互为稳健性、不分主次的并排测度, 每列各自进 just-identified 规格并排报告, 严禁把三轨或双轨嵌入变体混进同一个 over-identified 的 Hansen J 检验 — 它们是同一构念的替代测量而非满足排除约束的独立工具, 混用会把测量误差的相关性伪装成过度识别信息。同理, 本家族与 diag W-轨、与三判据网络指标之间也只做规格并排, 不做交叉合并。

【与相邻测度的构念区分】
第一, 与 emb_peer_tone_diag_lag1_{ctx,ss} (diag 对角轨, 另族): 本家族六列的 W 来源恒为 full 超级文档 (原始标题+正文拼接), ctx/ss 后缀只标记语调分量的轨道, 语义是 W_full × tone_trk; diag 列则让 W 的文本来源轨与 tone 同轨 (逐篇 content_ctx/content_ss 剔 fallback 行原样拼接、禁 title 通道), 是"网络定义本身也换轨"的更彻底敏感性。两族刻意不做 3×3 交叉 (W 轨 × tone 轨), 遵循梯子间正交不交叉先例。第二, 与 bank_emb_sim_mean_lag1: 出自同一 sim_matrix, 但取的是未 clip 真实余弦的去对角均值, 不乘 tone, 是 track-agnostic 的文本网络密度/嵌入位置测度, 与本家族"密度加权的语调水平"构念不同。第三, 与 bank_cogn_mean 三轨: 后者是当年文本的 TF-IDF 余弦认知邻近度, 非嵌入 (无 co-primary 标注、无 _lg 孪生), 且无滞后; 它是本家族嵌入相似度的词袋参照臂。第四, 与 industry_neg_shock{_lag1} 三轨: 后者是等权 leave-one-out 的同业负面报道占比, 分子分母严格逐轨, 不含相似度加权; 本家族则以文本邻近度对同业差异加权, 二者分别回答"全行业环境"与"我的文本近邻环境"。第五, 与 leave_one_out_peer_*_iv 及 bartik_*_iv: 那些是工具变量列族, 服务 2SLS; 本家族是 OLS/FE 规格里的控制变量, 角色不可互换。第六, 与共提及网络 (co-mention) 的 33 项结构指标: 那些刻画银行∧银行在报道中的共现拓扑 (含三判据后缀), 网络定义依据是共同出现而非语义相似。

【已知局限与稳健性梯子】
局限一, 嵌入余弦的语义解释边界: Steck 等 (2024) 证明在某些训练目标与正则化设定下, 嵌入余弦可以产生任意的甚至无意义的"相似度", 其绝对水平不宜过度解读; 本测度只以余弦的相对大小构造行内权重 (行随机归一后仅行内相对序承重), 部分缓释该批评, 且以 TF-IDF 参照臂 (bank_cogn_mean) 与双 co-primary 模型互检作为梯子。局限二, 负余弦 clip: W 构造前把负余弦截为 0 丢弃了"语义对立"的信息; 该选择是加权均值语义完整性所必需, 且 clip 发生时有 loud 告警披露, 未 clip 真值仍保全在 sim_mean 列中。局限三, 滞后不等于外生: 相关效应与持续性共同冲击不被滞后消除 (见识别策略定位段), 本列不可单独当因果同伴效应读。局限四, 文本构成内生: 超级文档随媒体覆盖量与选题构成变化, 报道稀少银行的向量噪声更大; W 行随机归一使权重相对化, 但小样本行的权重分布更不稳定。局限五, 数据与播种状态: 嵌入依赖付费 API 缓存, 未播种/离线 miss 的年份整年置 NaN 并 loud 告警; 开发盘 T=2 下仅一个年份存在滞后年, 本家族有效值稀疏属预期退化, 生产 T=19 播种后正常。局限六, 样本进入退出: 某行在 t-1 年无任何报道则该年不在节点集内, 其同行的 W 行会重新归一 — 网络成员随媒体覆盖进出, 面板不平衡时同行集合逐年变动, 解释系数时须意识到"同业"的外延是年度滚动的。稳健性梯子的完整结构: 嵌入模型维 (canonical Qwen 对 _lg large, 严格 parity)、情感轨维 (full/ctx/ss, full-only 留篇门控下 ctx/ss 为 conditional-on-full)、W-轨维 (full 族对 diag 族)、加权方式维 (相似度加权对等权 LOO)、词袋对嵌入维 (cogn 对 emb) — 五个维度全部遵循各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J 的口径, 且维度之间正交不交叉 — 不做 W 轨 × tone 轨的 3×3 全交叉, 也不做嵌入模型 × 语言学规则之类的跨梯子组合, 以免列空间组合爆炸稀释每条梯子的可读性。最后一点披露义务: 嵌入模型属外部 API 依赖, 厂商侧的模型迭代或下线会改变缓存外的新增取值; 本仓以冻结缓存 (命中即复现) 与双轨互检对冲该风险, 手稿中须按仓库口径披露嵌入厂商维度与 full-only 门控带来的数值副作用。

## VAR: emb_peer_tone_lag1_full

【变体差分】
本列是家族 canonical headline (tier=core, 类别6 网络溢出 headline), 家族公式中所有默认取值的交点: 嵌入模型取 MAIN spec 即 Qwen/Qwen3-Embedding-8B (硅基流动 API, 4096 维, 列名无 _lg 中缀), 语调轨取 full 轨即 llm_vote_tone_full, W 来源取 full 超级文档, 滞后取一期。逐项展开其精确语义: 权重侧, t-1 年每家银行的全部报道以原始"标题"+"内容"列按 docid 升序确定性拼接为超级文档, 经 Qwen 嵌入引擎分块编码 (无前缀截断, token 加权 mean pooling), 两两余弦→对角置零→负值 clip→行随机归一得 W_emb; 语调侧, llm_vote_tone_full 是 stage 21 三家 LLM (gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash) 对 full 轨文本 (标题 prepend + 全文正文) 的多数投票共识, 也是 P1 论文 treatment 的 primary 列; full 轨同时承担全仓留篇门控职能 — 一篇文章是否计为银行金科报道只看 llm_verified_full, 故本列的语调分量建立在门控后的留篇集上, 无 conditional-on-full 的额外截尾。缺失语义: 缺 tone 同行同时剔出分子分母并按观测权重和重归一, 无观测 tone 同行或该年嵌入 miss 时为 NaN, 绝不以 fillna(0) 伪零稀释。取值有界于 [-1,1], 正值表示文本近邻同业上年被媒体正面报道为主。用法定位: 作为网络溢出控制变量进入以银行自身语调为处理变量的主规格, 与年份/银行固定效应联用; 由于本列本身是滞后量, 与被解释变量之间不存在同期联立, 但它与滞后被解释变量可能相关, 动态面板规格下须按弱外生处理。它与 _lg 孪生列构成 co-primary 双轨, 与 ctx/ss 后缀列构成三轨梯子, 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 作为家族 headline, 附表中其余五列的系数均以本列为参照系报告。与近邻列的边界: 它不是 emb_peer_tone_diag_lag1 系 (本列 W 恒 full, diag 族无 full 对角列 — full 轨的对角即本列自身), 不是 bank_emb_sim_mean_lag1 (同矩阵但不乘 tone), 也不是 industry_neg_shock_lag1 (等权 LOO 负面占比, 无相似度加权)。解读示例: 本列取值 0.3 读作"该行文本近邻同业上一年的媒体语调加权平均为温和偏正", 系数为正读作"同业舆论环境越正面, 本行结果变量越高 (在控制自身语调与双固定效应后)"; 由于是凸组合, 本列一个标准差的变动量级通常明显小于自身语调列, 跨列比较效应大小须用标准化系数。加权算术的一个直观性质值得记录: 若某行的全部观测同行语调同为常数 c, 则无论权重如何分配本列取值恒为 c — 权重只在同行语调有截面差异时才承重, 这意味着行业语调高度同质的年份里, 本列与等权 LOO 均值 (industry 系列) 几乎重合, 二者的分歧本身就是"文本近邻结构是否有额外信息"的诊断。构造链上游的两处修复对本列数值有历史影响, 复现旧结果时须注意: 其一, 超级文档去 8000 字符前缀截断 (2026-06-11) 改变了长文档银行的向量, 属缓存键级变更; 其二, 缺 tone 同行从 fillna(0) 改为观测重归一 (NSP-1), 在 T=19 全量下方向性地抬升缺失密集年份的绝对水平, 盘上 T=2 近似 no-op。确定性口径: 拼接顺序 docid 升序钉死, 嵌入经 _llm_cache.db 缓存, 离线 0 miss 时字节级可复现; 本列不在 BLAS-FP 非确定网络列清单 (9 列, 均为图结构中心性/聚类类) 内, golden 验零漂移时无须豁免; 唯一的跨 run 漂移来源是嵌入缓存外的新增 API 调用, 播种完备后即消失。

## VAR: emb_peer_tone_lag1_ctx

【变体差分】
本列与 canonical (emb_peer_tone_lag1_full) 的唯一差分在语调分量的轨道: tone 取 llm_vote_tone_ctx (t-1), 即三家 LLM 对 ctx 轨文本 (标题 prepend + 目标银行实体窗口文本, stage 14 物化的 content_ctx) 的多数投票共识; 权重矩阵 W_emb 与 canonical 完全同一 — 来源恒为 full 超级文档、同一 Qwen 嵌入、同一年份的同一矩阵, 故本列语义是 W_full × tone_ctx, 这一点已在 Stata 标签中显式写明 (W=full, tone=ctx)。它回答的问题是: 若把同业语调的测量从全文收窄到银行实体邻域 (剔除同篇中与该行无关段落的情感噪声), 网络溢出控制的取值是否稳健。须与 emb_peer_tone_diag_lag1_ctx 严格区分: 后者连 W 的文本来源也换成 content_ctx (剔 fallback 行、禁 title 通道), 是另一族列; 本列只换 tone 轨不换 W 轨。留篇门控口径: ctx 轨自 2026-06-29 起为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 本列语调分量继承该门控。缺列守卫: 面板缺 llm_vote_tone_ctx 时本轨跳过不借 full 分母, 本列整列缺席或 NaN。解读上, 本列与 canonical 的差值刻画"同业的全文语调与实体邻域语调的分歧经网络加权后的净额": 若同业报道普遍在与银行无关的段落夹带情绪 (如宏观评论), 本列会系统性偏离 canonical, 差异本身有诊断价值。用法与 canonical 相同 (网络溢出控制, 配双固定效应), 与 full/ss 变体各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 报告时在附表与 canonical 主规格并排呈现即可, 不进入同一方程的右侧。

## VAR: emb_peer_tone_lag1_lg_ctx

【变体差分】
本列是 emb_peer_tone_lag1_ctx 的 _lg co-primary 对偶: 语调分量同取 llm_vote_tone_ctx (t-1, conditional-on-full 门控), 差分在嵌入模型 — W_emb 出自 text-embedding-3-large (OpenAI 模型经 yunwu 网关, 3072 维) 对同一批 t-1 年 full 超级文档的独立编码, 与 canonical 的 Qwen 4096 维向量绝不混算 (余弦维度无关, 由返回矩阵形状驱动)。列名构造须注意 _lg 中缀插在轨道后缀之前 (lag1_lg_ctx 而非 lag1_ctx_lg), 这是全仓嵌入族的统一命名口径。降级语义: 在 full-W 单元内 MAIN 与 _lg both-or-neither — 任一 spec 该单元失败, 本列与 canonical 族同置 NaN, 无单边孤儿; 这与 BERT/LLM per-model 独立降级不同, 是嵌入 co-primary 的更强 parity 约束。用法: 与 emb_peer_tone_lag1_ctx 构成双轨并排, 检验"ctx 轨语调的同业溢出控制"不被单一嵌入厂商的表示空间驱动; 两列各自 just-identified 并排、同为主测度互为稳健性不分主次, 禁混同一 over-identified Hansen J。缓存键含模型标识, _lg 轨 miss 独立于 canonical 轨计数与告警。与家族内其余列的定位关系: 本列同时偏离 canonical 两个刻度 (嵌入空间与语调轨), 但两个偏离维度正交且各自可单独回溯 — 与 lg_full 比较隔离出语调轨差异, 与无 _lg 的 ctx 列比较隔离出嵌入空间差异; 面板缺 llm_vote_tone_ctx 时本列与非 _lg 的 ctx 列同步缺席, 不产生跨模型的单边孤儿。开发盘 T=2 下与家族其余列同受"仅单一滞后年"约束, 有效值稀疏属预期; 生产 T=19 播种后本列随 _lg 轨整体补全。

## VAR: emb_peer_tone_lag1_lg_full

【变体差分】
本列是家族 headline (emb_peer_tone_lag1_full) 的 _lg co-primary 对偶, tier=core (2026-07-10 签核扩围): 语调分量与 canonical 完全同一 (llm_vote_tone_full, t-1, full-only 留篇门控), 唯一差分在权重矩阵的嵌入表示空间 — W_emb 出自 text-embedding-3-large (3072 维, yunwu 网关) 对同一批 t-1 年 full 超级文档 (同一 docid 升序拼接文本) 的独立编码, 再走与 canonical 逐字相同的余弦→去对角→负值 clip→行随机归一→观测重归一链路。它存在的构念理由: 嵌入相似度权重是本家族唯一无法用词面规则审计的黑箱环节, 单一模型的各向异性、训练目标偏置 (Steck 等, 2024 的批评) 可能系统性扭曲"谁是谁的文本近邻"; 换一个训练数据、目标函数、参数量、厂商全都不同的第二嵌入空间重建 W, 若加权后的同业语调仍给出同号同量级的系数, 则结论对表示空间选择稳健。注意本列的差分只作用于权重侧: 语调向量、观测掩码、重归一算术与 canonical 逐元素相同, 两列取值的任何差异都可完全归因于 W 矩阵的分歧, 这使双轨比较成为对"近邻结构假设"的定向检验而非笼统的换模检验。这正是全仓 co-primary 双轨设计的意图: 两轨同为主测度、互为稳健性、严格 parity — 列名双射 both-or-neither, 任一 spec 在 full-W 单元失败则本列与 canonical 族同置 NaN, 无单边孤儿列; 本列绝不是 canonical 的"附属稳健列", 扩围为 core 即确认其与无后缀列不分主次的地位。使用铁律: 与 emb_peer_tone_lag1_full 各自进 just-identified 规格并排报告, 严禁把两列混进同一 over-identified Hansen J — 它们是同一构念在两个表示空间下的替代测量, 测量误差高度相关, 不满足过度识别检验的独立性前提; 系数比较只做定性同号同量级判断, 若做跨列显著性汇总须走 FWER 校正路线而非 J 检验。与近邻列边界: 区别于 emb_peer_tone_lag1_lg_ctx/lg_ss (语调换轨), 区别于 bank_emb_sim_mean_lag1_lg (同 _lg 矩阵但不乘 tone), 区别于 diag 族 _lg 列 (W 换轨)。缺失与确定性口径均与 canonical 逐条对称: 观测重归一、无观测同行→NaN、嵌入缓存穿透、离线 miss→raise、docid 升序确定性拼接; _lg 轨的缓存键含自身模型标识, 与 canonical 轨互不串键, 两轨的 miss 年份独立计数、独立告警。技术谱系上本列与 canonical 的异质性是实质而非名义: text-embedding-3-large 出自对比预训练路线 (Neelakantan 等, 2022), Qwen3-Embedding 出自大模型底座蒸馏路线 (Zhang 等, 2025; 方法论前身 Wang 等, 2024), FinMTEB (Tang 与 Yang, 2025) 的评估显示两类模型在金融文本上的强弱项不同序 — 若两个如此异质的表示空间给出一致的同业语调加权结果, 表示空间选择这一研究者自由度即被实质排除。历史沿革: 本仓曾有 text2vec 与 bge-m3 两条本地嵌入稳健轨, v3.14.0 整体移除后 _lg 升格为唯一且无条件计算的协主轨 (仅当 _lg spec 配置为空时才不产列), 本列因此从"多轨之一"变为与 canonical 严格对偶的双轨之一。维度差异 (3072 对 4096) 不影响任何下游语义, 余弦与行随机归一均维度无关; 两轨的 W 矩阵取值不同但同为行随机, 输出量纲完全可比, 差异只反映"谁被认作近邻"的表示空间分歧; 实证上两列的截面相关系数是双轨一致性的一线诊断, 相关越高说明结论对嵌入选择越不敏感, 相关偏低时应逐年检视两个 W 矩阵的近邻排序分歧再下结论。

## VAR: emb_peer_tone_lag1_lg_ss

【变体差分】
本列是 emb_peer_tone_lag1_ss 的 _lg co-primary 对偶: 语调分量取 llm_vote_tone_ss (t-1), 权重矩阵出自 text-embedding-3-large (3072 维) 对 full 超级文档的独立编码, 语义为 W_full(_lg) × tone_ss。ss 轨语调测量的是最严格的文本口径: 标题 prepend + 银行与金科词严格同句 (±1 句窗) 共现的句子集; 无共现的文章按全仓回退语义取全文 body 且 ss_is_fallback=True (镜像 ctx 的回退设计, 共享 n_articles 分母), 该轨自 2026-06-29 起为 conditional-on-full 测度轨。本列把"最窄语调口径"与"第二嵌入空间"两个差分维度同时打开, 但两维度正交: 换 tone 轨不改 W, 换嵌入 spec 不改文本与链路, 故本列仍是单一差分链上可追溯的组合而非新构念。降级语义: full-W 单元内与 canonical 族 both-or-neither; 面板缺 llm_vote_tone_ss 时本列不追加。开发盘 T=2 下 ss 轨常因样本稀疏而近乎全 NaN, 属预期退化。与 emb_peer_tone_lag1_ss 及 lg_full/lg_ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 diag 族的 emb_peer_tone_diag_lag1_lg_ss (W 亦换 ss 轨) 是不同列, 勿混。定位关系与 lg_ctx 对称: 与 lg_full 比较隔离语调轨差异, 与无 _lg 的 ss 列比较隔离嵌入空间差异; 由于 ss 轨语调本身回退比例较高 (无同句共现文章按全文 body 计), 本列对回退语义的敏感性与非 _lg 的 ss 列完全同源, 嵌入空间的更换不改变回退行为; 换言之, 本列相对 lg_full 的差异全部来自语调口径收窄, 与嵌入厂商无关, 解读时两个刻度不可混同归因。

## VAR: emb_peer_tone_lag1_ss

【变体差分】
本列与 canonical 的唯一差分在语调轨道: tone 取 llm_vote_tone_ss (t-1), 即三家 LLM 对 ss 轨文本的多数投票共识; W_emb 与 canonical 同一 (full 超级文档, Qwen 4096 维), 语义为 W_full × tone_ss, Stata 标签显式标注 (W=full, tone=ss)。ss 轨是三轨中信噪比取向最激进的口径: 只保留目标银行与金科词在同句 (±1 句窗, config 键 ss_sentence_radius) 共现的句子, 把语调测量收窄到"银行×金融科技"关系被直接陈述的文本邻域; 无共现文章按回退语义取全文 body 并置 ss_is_fallback=True (镜像 ctx 回退, 共享 n_articles 分母), FINTECH_AC 缺席时全 fallback 优雅降级。本列回答: 同业情感环境若只按"与金科直接相关的语调"计量, 网络溢出控制是否稳健。门控口径: ss 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集。缺列守卫: 面板缺 llm_vote_tone_ss 时本轨跳过, 不借 full 分母。开发盘 T=2 下本列近乎全 NaN 属预期退化, 生产 T=19 正常。须与 emb_peer_tone_diag_lag1_ss 区分 (后者 W 亦换 ss 文本, 另族)。解读上, 本列与 canonical 的差值经网络加权后度量"同业语调中与金科议题无直接关联的部分": 二者高度一致说明同业的媒体语调本就由金科议题主导, 显著分歧则提示全文口径混入了大量非金科情绪。与 full/ctx 变体各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 报告位置在稳健性附表, 与主规格并排不同方程。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, Article 112803. https://doi.org/10.1016/j.econlet.2025.112803
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding Benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 3620-3638. https://doi.org/10.18653/v1/2025.emnlp-main.179
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Amancio, D. R., Machicao, J., & Quispe, L. V. C. (2025). Leveraging word embeddings to enhance co-occurrence networks: A statistical analysis. PLOS ONE, 20(7), Article e0327421. https://doi.org/10.1371/journal.pone.0327421
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Improving text embeddings with large language models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2401.00368
Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics, 2014-2037. https://doi.org/10.18653/v1/2023.eacl-main.148
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Bramoulle, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., ... Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 3980-3990. https://doi.org/10.18653/v1/D19-1410
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoulle, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Nyakurukwa, K., & Seetharam, Y. (2025). Investor sentiment networks: mapping connectedness in DJIA stocks. Financial Innovation. https://doi.org/10.1186/s40854-024-00675-7
Chung, A., & Tanaka-Ishii, K. (2023). Modeling Momentum Spillover with Economic Links Discovered from Financial Documents. Proceedings of the 4th ACM International Conference on AI in Finance (ICAIF '23) [Working Paper]. https://doi.org/10.1145/3604237.3626862
<!-- rendered-citations:end -->
