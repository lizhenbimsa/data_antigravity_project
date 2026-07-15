---
family_id: F093
columns:
- bank_emb_sim_mean_lag1
- bank_emb_sim_mean_lag1_ctx
- bank_emb_sim_mean_lag1_lg
- bank_emb_sim_mean_lag1_lg_ctx
- bank_emb_sim_mean_lag1_lg_ss
- bank_emb_sim_mean_lag1_ss
unit: "无量纲嵌入余弦相似度均值 (真实 cosine 域闭区间 -1 到 1; 归一化嵌入在真实语料上实践取值通常为正, 极少落入负区)"
formula: "bank_emb_sim_mean_lag1{model}{_wtrk}_{i,t} = mean_{j != i} cosine( E_i(t-1), E_j(t-1) ); E_i(t-1) = 银行 i 在滞后年 t-1 全部报道聚合的超级文档经嵌入引擎编码所得向量; full/canonical 轨超级文档 = (标题 + 空格 + 正文) 逐篇拼接 (原始 内容/标题 列, docid 升序确定性排序), ctx/ss 轨超级文档 = content_{ctx,ss} 逐篇原样拼接 (剔 *_is_fallback==True 行、禁 title 通道); 嵌入模型: 无后缀 = {Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动}, _lg = {text-embedding-3-large, 3072 维, yunwu}, 超长超级文档分块 + 逐块 L2 归一 token 加权 mean pooling; cosine 基于未 clip 的真实嵌入 (负值 clip 仅用于 W_emb 行随机化, 绝不进入 sim_mean), 对角经 np.delete 排除后取行均值; 值域闭区间 -1 到 1; 滞后年无数据 / 当年有效银行 < 2 家 → 该格 NaN; 空超级文档剔除仅存在于 ctx/ss diag 支路 (剔空后有效银行不足 2 家同样 NaN), full 轨聚合不做空文本剔除"
producer: "news_process/pipeline/panel/network_spillover.py::compute_embedding_peer_network (Stage 40 面板派生, 步骤 7h-emb; 主/协主轨经 _compute_embedding_peer_network_pass, ctx/ss diag W-轨经 _merge_diag_w_track_units, 行级 both-or-neither 经 _enforce_row_parity) ; news_process/pipeline/panel/stata_export.py (Stata 变量标签)"
upstream:
- 篇章级展开帧 df_exploded (原始 标题 / 内容 列 + target_bank + year + docid; full 轨超级文档源, 提供滞后年 t-1 文本)
- 14_materialize_ctx.parquet (content_ctx / content_ss + ctx_is_fallback / ss_is_fallback; ctx / ss 两条 diag W-轨超级文档源)
- 21_tone_llms 留篇集 (full-only 门控行宇宙, 2026-06-29; sim 本身 track-agnostic, 但参与聚合的文章集由 llm_verified_full 判定)
- "41_panel_encode_aggregate (bank-year 面板骨架: target_bank × year 键, 供嵌入相似度均值 merge 落列)"
- data/processed/_llm_cache.db (嵌入 API 结果缓存; 命中即 $0 离线复现, 离线 miss 触发 RuntimeError)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: "Jha, M., Liu, H., & Manela, A."
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: The Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.2139/ssrn.6507162
  type: wp
  authors: "Tan, L., Wang, C., Sun, J., & Qian, Y."
  year: 2026
  title: "Measuring corporate risk using large language model embeddings: Evidence on corporate climate risk and supply chain restructuring"
  venue: SSRN Electronic Journal
  pages_or_artno: "SSRN:6507162"
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: "Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J."
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
  pages_or_artno: "arXiv:2506.05176"
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: "You, K."
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
  pages_or_artno: "arXiv:2504.16318"
- doi: 10.18653/v1/2025.emnlp-main.1135
  type: journal
  authors: "Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S."
  year: 2025
  title: "Interpretable text embeddings and text similarity explanation: A survey"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 22314-22330
- doi: 10.18653/v1/2025.emnlp-main.179
  type: journal
  authors: "Tang, Y., & Yang, Y."
  year: 2025
  title: "FinMTEB: Finance Massive Text Embedding Benchmark"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 3620-3638
- doi: 10.3386/w33651
  type: wp
  authors: "Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M."
  year: 2025
  title: "Asset embeddings"
  venue: NBER Working Paper No. 33651
  pages_or_artno: "w33651"
- doi: 10.1002/smj.3687
  type: journal
  authors: "Arts, S., Cassiman, B., & Hou, J."
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.1145/3589335.3651526
  type: journal
  authors: "Steck, H., Ekanadham, C., & Kallus, N."
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: "Liu, Y., Cao, Z., & Wen, F."
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: "111823"
- doi: 10.18653/v1/2023.eacl-main.148
  type: journal
  authors: "Muennighoff, N., Tazi, N., Magne, L., & Reimers, N."
  year: 2023
  title: "MTEB: Massive text embedding benchmark"
  venue: Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics
  pages_or_artno: 2014-2037
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: "Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L."
  year: 2022
  title: "Text and code embeddings by contrastive pre-training"
  venue: arXiv
  pages_or_artno: "arXiv:2201.10005"
- doi: 10.1086/715162
  type: journal
  authors: "Rodriguez, P. L., & Spirling, A."
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: "Reimers, N., & Gurevych, I."
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3980-3990
- doi: 10.1086/688176
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: "Levy, O., Goldberg, Y., & Dagan, I."
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
- doi: 10.2307/2298123
  type: journal
  authors: "Manski, C. F."
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
new_dois:
- 10.1086/688176
- 10.2307/2298123
---

## CORE

【构念与来源】
本家族刻画的是"银行间语义邻近度" (semantic proximity), 即两家银行在某一年被媒体报道的整体话语在深层语义空间中彼此接近的程度, 并以此为每家银行给出它与全行业其余各行的平均语义相似度。构念的直接理论源头是 Hoberg 与 Phillips (2016) 提出的文本网络产业思想: 他们用企业产品描述文本的两两相似度构建随时间变动的同行网络, 用文本邻近替代静态的行业分类码, 从而捕捉企业间真实的竞争与差异化关系。本项目把这套"以文本相似度构建动态同行网络"的方法迁移到中国银行业的新闻话语场域, 并把 Hoberg 与 Phillips 原文所用的 TF-IDF 稀疏词频余弦, 升级为句向量嵌入 (sentence embedding) 的稠密余弦——嵌入向量能把词面不同但语义相近的表述映射到相邻位置, 从而捕获比表层词频更深层的语义邻近度。具体操作是: 对每一家目标银行, 把它在某一年内被媒体报道的全部文本聚合成一份"超级文档", 用统一嵌入引擎把超级文档编码为一个高维向量, 再计算任意两家银行向量之间的余弦相似度, 最后对每家银行取它与当年其余所有银行相似度的均值, 得到该行的嵌入语义相似度均值。得分高意味着这家银行的新闻语义与行业整体高度趋同, 处于语义同质、信息环境高度重叠的区域; 得分低意味着这家银行在语义空间中相对独特, 呈现话语差异化。这里"超级文档"是本测度的关键中间产物: 把一家银行在一年内被媒体报道的所有篇章拼成一份长文档, 目的是让相似度度量的粒度落在银行-年这一面板单元上, 而不是逐篇文章——因为面板计量关心的是银行的年度信息画像, 逐篇相似度既无法直接进入 bank-year 面板, 也会被单篇噪声主导。还须点明本家族与同行情感溢出 emb_peer_tone 的产出关系: 相似度均值与 emb_peer_tone 由同一遍 pass 产出, 相似度均值是这一遍里 track-agnostic 的结构副产品, 而 emb_peer_tone 是把同一相似度方阵行随机化后乘以同行情感的有向溢出——二者共享超级文档与嵌入, 但相似度均值不加载任何情感, 只刻画语义邻近的强度。数据来源上, full 轨超级文档取自篇章级展开帧的原始标题与正文, ctx 与 ss 两轨取自 stage 14 物化的 content_ctx 与 content_ss; 银行-年面板骨架来自 41_panel_encode_aggregate, 相似度均值以 target_bank 与 year 为键 merge 落列; 参与聚合的文章集遵循 2026-06-29 起的 full-only 留篇口径, 即一篇是否算作银行金科报道由 llm_verified_full 判定, ctx 与 ss 只是该留篇集的条件子集 (行宇宙为 full 留篇集的子集)。

【方法学与计算】
计算严格逐年独立、且带一期滞后, 这两点同时决定了本测度的口径。滞后指的是: 银行 i 在面板年 t 上的相似度均值, 完全由滞后年 t-1 的超级文档算出——源码在列名中显式写入 lag1 后缀正是为此披露 (修复 omni-g-net-spill-03), 目的是让本测度可作为滞后同行溢出网络的构造基元, 并规避 Manski (1993) 反射问题带来的同期内生性。具体链路如下。第一步, 取滞后年数据: 面板年 t 对应读取 df_exploded 中 year 等于 t-1 的全部文章; 若滞后年无数据则当年该格跳过。第二步, 确定性排序与聚合: 把滞后年文章按 docid (缺则日期、标题) 稳定升序排序后, 按目标银行聚合成超级文档——full 轨把每篇的原始标题与正文用空格拼接再整体串接 (修复 omni-g-net-spill-02 移除了旧的 8000 字符前缀截断, 因为前缀截断只保留行序最先的若干篇, 属非代表性样本), ctx 与 ss 轨则把 content_ctx 或 content_ss 逐篇原样拼接、并刻意剔除 *_is_fallback 为真的行、禁用标题通道 (因 stage 14 的 prepend_title 已把标题内嵌, 再拼即双标题污染付费嵌入缓存)。第三步, 有效银行守卫: 若当年通过聚合 (且 ctx/ss 轨剔 fallback、剔空超级文档) 后的有效银行不足 2 家, 则当年全部置 NaN, 因为余弦相似度至少需要一对主体才有定义。第四步, 嵌入编码: 调用统一引擎 embed_texts, 无后缀 canonical 轨用 MAIN spec (Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动), _lg 协主轨用 large spec (text-embedding-3-large, 3072 维, yunwu); 超长超级文档由引擎内部按 token 切块, 逐块 L2 归一后做 token 加权 mean pooling 汇成单一向量, 因此嵌入维度无关、绝不跨模型混算余弦。第五步, 余弦方阵与相似度均值: 在嵌入矩阵上计算两两余弦相似度得到方阵, 把对角线置零以排除自身, 然后按索引 (np.delete) 剔除对角项后对每一行取均值, 得到该行与当年其余所有银行的平均余弦相似度。此处有两个必须精确区分的口径。其一, 相似度均值 sim_mean 建立在未经 clip 的真实余弦之上, 因此其值域是真实 cosine 域闭区间 -1 到 1, 而非 0 到 1——源码把范围断言从旧的 0 到 1 明确改成 -1 到 1 (修复 omni-g-net-spill-04), 并把旧的 sim_row 大于 0 符号筛选 (它把"排除对角"与"按符号筛选"混同, 会静默剔除负余弦同行、又使 0 下界断言结构性不可触发) 改成按索引去对角。其二, 对负余弦做 clip 为 0 的操作只发生在构造行随机化权重矩阵 W_emb 的支路 (供同行情感溢出 emb_peer_tone 使用, 因为对含负项的行做行和归一会破坏加权均值语义), 这一 clip 绝不进入 sim_mean 的计算。全过程唯一的付费点是嵌入 API 在线 miss; 命中 _llm_cache.db 即零成本, 离线模式下 miss 会 raise RuntimeError 而绝不静默调网。

最后须交代嵌入引擎与缓存的确定性与降级机制, 因为它们直接决定本测度能否 golden 复现、以及缺嵌入时如何优雅退化。嵌入引擎 embed_texts 是纯 API 调用, 向量维度完全由返回矩阵的 emb.shape[1] 驱动 (Qwen 4096 维 / text-embedding-3-large 3072 维), 对超过单次 token 上限的超级文档按 cl100k 分词切块、逐块编码后再做 token 加权 mean pooling 汇成单一向量; 每一次编码都经统一 LLMCache 穿透同一份 _llm_cache.db (缓存路径与历史实现一致), 命中即零成本且逐字节可复现, 未命中时在线才付费。离线守卫 NEWS_PROCESS_LLM_OFFLINE=1 下, 任一 miss 会 raise RuntimeError 而绝不静默调网——这与情感 stage 21 的 LLMCacheMissError 对称 (异常类型不同但语义一致), 保证三轨全命中时可离线零 miss 字节级复现。降级机制分两层: pass 级 both-or-neither 是"整遍 pass 返空则该 spec 该轨列对称置 NaN" (main_ok = bool(emb_results)); 行级 both-or-neither (审计 F3, _enforce_row_parity) 则在 canonical 与 _lg 覆盖的 (银行, 年) 键集因单侧 per-year miss 而不一致时, 逐键强制任一 NaN 即两列同置 NaN, 杜绝单边孤儿。此外, 轨级嵌入 miss 或失败的年份会被显式计数并以一条 loud WARN 汇总回声 (未播种或离线 miss 导致该年该轨列 NaN, 播种后应为 0), 避免吞异常路径静默丢列。确定性上, 滞后年文章按 docid 升序稳定排序、超级文档拼接顺序固定, 加之分块与 pooling 确定, 使同一超级文档的缓存键稳定, 本测度得以跨 run 复现——但须在受控环境钉死 PYTHONHASHSEED 与全部 BLAS 线程为 1, 因为部分网络中心度列存在 BLAS 浮点非确定漂移。

【文献定位】
本测度处在三条文献脉络的交汇处。其一是文本网络与同行效应脉络。构念的方法学祖本是 Hoberg 与 Phillips (2016) 的文本网络产业, 用产品文本相似度构建动态同行网络; Arts, Cassiman 与 Hou (2025) 沿这一思路用文本刻画技术差异化与产品市场竞争并接入并购分析, 是把文本相似度网络用于企业战略与交易的近期范例。而一旦要在这类网络上做因果识别, 就绕不开 Manski (1993) 的反射问题——同期的同行行为与个体行为互为因果、难以分离, 本项目正是以严格滞后一期 (Lag Y-1) 规避这一难题, 因此把嵌入相似度均值定义在 t-1 文本之上。其二是嵌入与余弦相似度方法脉络。canonical 轨所用 Qwen3 嵌入模型的技术细节见 Zhang 等 (2025); _lg 协主轨所用 text-embedding-3-large 属 OpenAI 对比学习嵌入谱系, 其方法源头见 Neelakantan 等 (2022); 句向量相似度的经典范式见 Reimers 与 Gurevych (2019) 的 Sentence-BERT (也是源码为本地降级方案标注的学术依据); 嵌入质量的横向评测框架见 Muennighoff 等 (2023) 的 MTEB 与 Tang 与 Yang (2025) 面向金融文本的 FinMTEB。方法论上余弦相似度并非无懈可击: Steck 等 (2024) 指出在学习到的稠密嵌入空间中, 余弦相似度未必真的度量语义相似; You (2025) 进一步刻画余弦"在某些情形有效、直到失效"的边界; Opitz 等 (2025) 对可解释文本嵌入与相似度解释做了系统综述。更早的经验教训同样成立: Levy, Goldberg 与 Dagan (2015) 系统证明词向量方法之间的表观性能差距很大程度上由超参数与预处理选择驱动而非算法本身, 这一发现平移到句向量场景就是"嵌入模型与池化方案的选择本身是一个研究者自由度", 必须以多模型并置来约束; Rodriguez 与 Spirling (2022) 则专门面向应用社会科学研究者给出嵌入选型的效度评估框架, 强调在把嵌入产物当作实证变量之前须先回答"它在本领域语料上度量的是什么、如何验证"。这些告诫共同界定了把嵌入余弦当作构念代理时必须保持的审慎, 也正是本家族保留 TF-IDF 认知邻近度 (bank_cogn_mean, 表层可解释) 与嵌入相似度 (深层语义) 并置、互为效度参照的原因。其三是金融领域的嵌入应用脉络。Jha, Liu 与 Manela (2026) 在顶级金融期刊上以语言嵌入方法度量金融是否惠及社会, Gabaix 等 (2025) 提出资产嵌入, Tan 等 (2026) 用大模型嵌入度量企业风险, Liu, Cao 与 Wen (2024) 在中国情境下以企业与政府文本余弦对齐度量并接入定价——这四项工作共同确立了"把文本嵌入相似度作为经济与金融面板变量"的合法性与现实相关性, 为把银行新闻的语义趋同纳入银行面板提供了外部相关性依据。综观三条脉络可见本测度的坐标: 它在方法源头上是 Hoberg 与 Phillips 文本网络的嵌入升级版, 在技术实现上依托 Qwen3 与 OpenAI 对比学习嵌入并受余弦方法学告诫约束, 在应用定位上属金融文本嵌入这一新兴变量族; 三者交叉决定了它既非纯 NLP 度量、也非纯计量控制, 而是把语义邻近编码为可进入银行面板的结构变量, 其效度须同时对 NLP 侧 (嵌入质量、余弦是否失真) 与计量侧 (识别位置、反射问题) 负责。

【识别策略定位】
必须厘清本家族在识别框架中的角色: 它是嵌入同业网络控制变量的一环, 服务于内生性净化, 而非承担因果识别的处理变量。嵌入相似度均值 sim_mean 本身是"文本相似度均值", 是 track-agnostic 的结构量 (不加载任何情感符号), 它的直接用途有二: 一是作为同期信息环境同质性的控制, 吸收"语义高度重叠的银行可能共享未观测冲击"这一混淆; 二是作为同一支路副产的行随机化权重矩阵 W_emb 的构造基元, 而 W_emb 与滞后一期同行情感相乘得到 emb_peer_tone 这一有向溢出处理度量。滞后一期是本支路识别设计的核心: 用 t-1 文本构造相似度与权重、再乘 t-1 同行情感, 是为规避 Manski (1993) 反射问题与同期反向因果, 这也是列名显式带 lag1 的原因。源码 (network_spillover.py 第 1793 行附近) 特意警示不要把本家族的滞后口径与同期的 TF-IDF 认知邻近度 bank_cogn_mean (当年文本) 混淆——两者一为 t-1、一为 t, 一为嵌入、一为 TF-IDF, 服务于不同的识别位置。样本层面须再次提示本机开发样本 (T=2, 2017-2018) 的严重局限: 一期滞后本身就吃掉一年样本, 在如此浅的面板上, 去除伪零后的一阶同行网络覆盖极稀、经纪类 2SLS 在银行与年份双固定效应吸收下不足以识别, 论文不得在开发样本上宣称因果, 须待生产样本扩到 T 大于等于 3 并接入结局变量后重估。也就是说, 本测度不承担识别因果, 而是净化因果识别环境的辅助变量, 其水平的经济解读同样要等生产语料才稳。须再区分本测度在识别链上的两种身份粒度: sim_mean 是把整行两两余弦相似度塌缩为单一标量的 monadic (节点级) 网络嵌入度摘要, 而真正进入空间滞后识别的 dyadic 对象是完整的行随机化权重矩阵 W_emb——sim_mean 概括一家银行在语义网络中的整体嵌入强度、可作诊断量与同质性控制, 但它本身不是空间权重, 不能替代 W_emb 承担同行溢出的加权传播, 二者是同一遍 pass 里由同一余弦方阵派生的两个不同粒度产物。就反射问题的机制而言, Manski (1993) 所刻画的困境是同期同行结局与个体结局互为因果、内生同行均值与外生同行特征在线性均值模型中难以分离; 本支路以 t-1 文本构造 W_emb 与相似度、再乘 t-1 同行情感, 只是把同期联立打断为前定 (predetermined) 结构, 是识别的必要条件而非充分条件——在银行与年份双固定效应吸收之后, 一阶同行网络在浅面板上仍可能弱识别, 完整的同行效应识别还须叠加面板 IV 扩展的三引擎 (同组 leave-one-out 均值 / 广义 Bartik / 媒体来源 house-style 暴露) 所提供的外生变异, 本测度只承担其中的网络结构编码与信息环境同质性控制这一环, 绝不单独宣称已解决同行效应的内生性。

【与相邻测度的构念区分】
嵌入相似度均值与面板中若干近邻测度形态相近而口径迥异, 须逐一切割以免下游误用。相对 TF-IDF 认知邻近度 bank_cogn_mean 族: 那是同期 (当年文本) 的表层字符 n-gram 词频余弦, 值域良态落在 0 到 1, 属非嵌入 carve-out 因而没有 _lg 孪生; 本家族是滞后一期 (t-1 文本) 的稠密语义嵌入余弦, 值域为真实 cosine 域 -1 到 1, 且是嵌入测度因而带 co-primary 的 _lg 协主孪生。两者刻意并置、互为效度参照——表层词频与深层语义各有盲区 (前者对同义改写不敏感, 后者受 Steck 等 2024、You 2025 所述稠密空间余弦失真影响)。相对同行情感网络压力 emb_peer_tone 族: 那是 W_emb 行随机化权重矩阵乘以同行情感的有向、带符号溢出, 加载了情感极性与方向; 本家族是纯结构的语义相似度均值, 不加载任何情感、也无方向, 是 emb_peer_tone 的构造上游而非其本身。相对战略差异化族 strat_diff 与 strat_sim: 那些度量的是一家银行与其最相似的前 N 个同行 (或行业质心) 之间的距离或最大相似度, 落点在"与最近邻的差距"; 本家族取的是与全部其余银行相似度的均值, 刻画整个语义空间的整体趋同, 而非局部最近邻关系。相对表层陈旧度 surface_staleness: 那是 MinHash 近似去重信号、非嵌入且无 _lg 孪生, 与本家族的稠密嵌入余弦分属两个测度族。还须与三类形态相近却机制不同的度量切割。其一是网络拓扑中心度族 (bank_clustering、bank_cfbetween_cent、bank_harmonic_cent 及其判据分轨变体): 那些在银行共现邻接图上计算聚类系数、流介数、调和中心度, 刻画一家银行在共现图中的结构位置, 属图论拓扑量、且存在 BLAS 浮点非确定漂移 (验零漂移须按全名剔除相应列); 本家族是语义嵌入空间中的余弦相似度均值, 只要嵌入缓存全命中即确定可复现, 一为图结构、一为语义邻近, 不可混为一谈。其二是时间一致性 coh_emb 族: 那度量同一家银行跨年自身嵌入的时序一致性 (陈旧度 / 稳定度信号), 是 within-bank、across-year 的自相似; 本家族是 cross-bank、same-year 的他相似, 轴向正交。其三是政策余弦对齐 policy_cosine_sim 与 auth_sim_emb: 那是把银行文本与外部政策或权威文本作余弦对齐 (银行对外部锚点), 本家族是银行对银行的两两对齐 (无外部锚点), 参照系不同。最后须点明本家族内部的两条正交轴: 嵌入模型轴 (canonical Qwen 与 _lg text-embedding-3-large, co-primary 双轨) 与 W-轨轴 (full / ctx / ss 三条文本来源轨), 二者正交交叉出六列, 但两轴绝不交叉进同一个过度识别检验。

【已知局限与稳健性梯子】
第一层稳健性梯子是 co-primary 双轨嵌入。无后缀 canonical 列用 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动), _lg 协主列用 text-embedding-3-large (3072 维, yunwu); 两轨同为主测度、互为稳健性、严格 parity, 并遵守 both-or-neither——任一 spec 嵌入失败则同族两列同时置 NaN, 无单边孤儿; full 族更有行级 both-or-neither 补强 (审计 F3, _enforce_row_parity), 逐 (银行, 年) 键上任一 NaN 即两列同置 NaN。铁律: 两条 co-primary 各自 just-identified 并排, 严禁把 Qwen 与 emb3large 两轨混进同一个 over-identified 的 Hansen J 检验。第二层稳健性梯子是三条 W-轨 (full / ctx / ss)。full 为历史 canonical 口径 (原始标题加正文, 含标题通道), ctx 与 ss 是 2026-07-03 扩展加入的 diag W-轨 (超级文档改用 content_ctx / content_ss 逐篇原样拼接、剔 *_is_fallback 行、禁标题通道), 三轨列名后缀语义 = W (文本来源) 轨。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J; 三轨属规格稳健性并排 (镜像政治词权重梯度、词典消融梯度先例), 本族刻意不设跨轨 FWER 模板。第三层是 per-W-轨独立降级 (D8): 每条 W-轨 (ctx / ss) 是独立降级单元, 单元内 canonical 与 _lg 严格 both-or-neither, 单元间及与 full 族互不连坐——ctx 或 ss 未播种、离线 miss 绝不抹掉 full 族既有产出。第四层是余弦方法学告诫: 稠密嵌入空间中的余弦读数未必等同真实语义相似 (Steck 等 2024; You 2025; Opitz 等 2025), 且嵌入表征本身对训练超参与预处理选择高度敏感 (Levy 等 2015)、其应用效度须按领域专门验证 (Rodriguez 与 Spirling 2022), 本读数应与 TF-IDF 认知邻近度互为效度对照, 不宜单独当作语义邻近的定论。第五层是逐年独立与跨年不可比: 相似度在各年内部可比, 但不同年份间水平值不宜直接横比。第六层是短文本与浅面板退化: 滞后年无数据、当年有效银行不足 2 家、ctx/ss 轨剔 fallback 后空超级文档均会落 NaN, 在 T=2 开发样本上退化更明显 (一期滞后又吃掉一年)。第七层是播种状态披露: ctx/ss/diag 嵌入 (canonical 加 _lg) 在 T=2 已本机在线播种、可在 NEWS_PROCESS_LLM_OFFLINE=1 下离线零 miss 字节级复现, 生产 T=18 的全量播种按生产语料实测费用另行评估、当前 DEFERRED; 换嵌入模型属受控全量重生范畴, 须先过 M0 审批门, 并在手稿披露厂商与维度变更 (Google 转阿里 Qwen) 及 full-only 门控的数值副作用。第八层是确定性与 golden 复现的边界: 本家族的相似度均值依赖嵌入 API 返回值, 只要三轨在 _llm_cache.db 全命中即可离线零成本字节级复现, 但一旦换嵌入模型或做测度类改动即须受控全量重生 (钉死 PYTHONHASHSEED 与全部 BLAS 线程为 1), 且须注意本网络支路的若干中心度列存在 BLAS 浮点非确定漂移, 验零漂移时需按全名剔除相应列; 手稿须把厂商维度变更与 full-only 门控引发的分母收缩 (如 n_articles、fintech_share 的口径变化) 明确披露为口径调整而非缺陷。第九层是构念效度的根本前提: 嵌入余弦度量的是"新闻语义邻近", 它是否等同于两家银行真实的业务或战略邻近, 仍需外部业务相似度基准 (如技术邻近度、业务重叠度) 的效度检验才能坐实, 本档把这一前提写明以约束下游解读, 避免把语义层面的趋同直接读作业务结构层面的趋同。第十层是 monadic 塌缩的信息损失: sim_mean 把一整行 dyadic 相似度平均成单一标量, 会抹掉相似度的分布形状——一家与少数银行极近、与多数银行较远的银行, 可能与另一家和所有银行都中等接近的银行取到相同的均值; 需要完整网络结构的下游分析应直接使用 W_emb 或 emb_peer_tone, 不能以 sim_mean 代偿这一信息损失。第十一层是经验取值的正区间事实: 尽管余弦域为闭区间 -1 到 1, 归一化嵌入在真实语料上两两余弦极少落入负区, 因而实测 sim_mean 几乎恒为正; -1 下界是防负余弦被静默剔除的正确性守卫 (源码把值域断言从旧的 0 到 1 改为 -1 到 1、并容差 1e-6 适配浮点舍入, 正为此), 而非一个预期常见的取值区间, 解读时不应把理论负值当作常态。第十二层须澄清与 emb_peer_tone 支路的降级边界: emb_peer_tone 对缺 tone 同行改用仅 observed-tone 加权均值并按观测权重和重归一 (避免伪零向 0 衰减), 这一 fillna 口径修复只作用于 emb_peer_tone 的加权传播, 与 sim_mean 的行均值计算无关——sim_mean 只对有效银行 (n≥2) 的真实余弦取均值, 全程不涉及 tone 的缺失填充, 故本家族不继承该修复的落盘待重跑状态。

## VAR: bank_emb_sim_mean_lag1

【变体差分】
本列是整个家族的 canonical 无后缀列, 也是嵌入同业网络相似度在网络溢出族中的 headline (tier 为 core), Stata 变量标签为"银行嵌入相似度均值(滞后1)(对等轨Qwen3-8B)" (2026-07-10 WP3 标签中文化后的现行口径, 尾注中的 Qwen3-8B 指代 MAIN 槽 co-primary 嵌入模型)。它在两条正交轴上都取基准取值: 在嵌入模型轴上取 canonical 主轨, 即用 MAIN spec (Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动) 独立嵌入超级文档; 在 W-轨轴上取 full 轨, 即超级文档由滞后年每篇报道的原始标题与正文用空格拼接、再按 docid 升序确定性串接而成, 显式开启标题通道、使用未经三轨物化的原始文本列——这正是它与 ctx、ss 两条 diag 轨的本质口径区别 (那两轨读 stage 14 已 prepend_title 的 content_ctx / content_ss 且禁标题通道)。其余计算与家族 CORE 所述完全一致: 逐年独立、滞后一期 (面板年 t 由 t-1 超级文档算出, 列名 lag1 显式披露), 超长超级文档经引擎分块加 token 加权 mean pooling 编码, 余弦方阵对角置零后按 np.delete 去对角取行均值, sim_mean 建立在未经 clip 的真实余弦上因而值域为真实 cosine 域闭区间 -1 到 1 (源码显式 raise 校验, 容差 1e-6 适配浮点舍入; 对负余弦的 clip 为 0 只发生在 W_emb 支路、绝不进入本列)。滞后年无数据、当年有效银行不足 2 家会落 NaN。口径定位上, 本列是 track-agnostic 的结构相似度均值 (不加载任何情感符号), 承担同期信息环境同质性控制并作为 W_emb 权重矩阵的构造基元, 服务于以滞后规避 Manski (1993) 反射问题的识别设计; 它与同期的 TF-IDF 认知邻近度 bank_cogn_mean 口径不可混淆 (源码第 1793 行附近的显式警示), 也不同于战略差异化族的最近邻距离与 emb_peer_tone 的有向情感溢出。作为 co-primary 双轨的主轨, 本列与 _lg 协主孪生 bank_emb_sim_mean_lag1_lg 严格 both-or-neither (并有行级 parity 补强)、各自 just-identified 并排、互为稳健性、不分主次, 严禁把 Qwen 与 emb3large 两轨混进同一个 over-identified 的 Hansen J; 作为 W-轨轴的 full 基准, 它又与 ctx、ss 两轨各自 just-identified 并排、同样严禁三轨混进同一 over-identified 的 Hansen J。解读时须记住: 高值指向该行新闻语义与行业整体趋同的信息环境重叠, 低值指向语义空间的话语差异化, 而稠密嵌入余弦读数是否等同真实语义邻近仍受方法学告诫 (Steck 等 2024; You 2025) 约束, 应与表层 TF-IDF 认知邻近度互为效度对照。

须补充本列作为 W_emb 构造基元的下游用途, 以澄清相似度均值与其副产权重矩阵的分工。本列所依据的余弦方阵, 在同一遍 pass 里还被用来构造行随机化权重矩阵 W_emb: 具体是先把方阵对角置零 (自身不算同行), 再把负余弦 clip 为 0 (因为对含负项的行做行和归一会破坏加权均值语义、甚至令行和分母被负项侵蚀至非正而静默产生 NaN 或符号翻转), 然后行随机化标准化 (每行归一到行和为 1), 得到 W_emb; W_emb 再与滞后一期同行情感相乘得到 emb_peer_tone 有向溢出。关键在于: 这条负值 clip 与行随机化只作用于 W_emb 支路, 本列 bank_emb_sim_mean_lag1 取的是未经 clip 的真实余弦行均值, 因此本列可含 (理论上的) 负值、值域为 -1 到 1, 而 W_emb 用的相似度非负——二者绝不混淆。行宇宙层面, 本列参与聚合的文章集遵循 2026-06-29 起的 full-only 留篇口径 (由 llm_verified_full 判定一篇是否算银行金科报道), 因此本列的银行-年覆盖与 full 留篇集一致; 在 T=2 开发样本上, 一期滞后又吃掉一年, 去伪零后一阶网络覆盖极稀, 本列水平的经济解读须待生产 T=18 语料才稳。作为整个网络溢出族的 headline 与 tier=core 列, 本列在论文主表中承担同期信息环境同质性控制的角色, 其读数的最终效度绑定于嵌入质量 (Zhang 等 2025 的 Qwen3、Muennighoff 等 2023 的 MTEB 评测) 与余弦是否失真 (Steck 等 2024) 两个前提。确定性与复现层面还有一处只属于本列口径的细节值得写明: full 轨超级文档的拼接顺序由 docid 升序 (缺 docid 时退化为日期、标题) 稳定排序钉死, 这不仅是工程洁癖——超级文档的字节序列即嵌入缓存键的输入, 拼接顺序一旦漂移, 同一批文章会产生不同缓存键, 既造成缓存 miss 白白付费, 也破坏跨 run 字节级复现; 因此本列可在 _llm_cache.db 全命中前提下于 NEWS_PROCESS_LLM_OFFLINE=1 离线零成本重算, 且逐字节等值。另须提示嵌入表征效度的应用侧告诫: 嵌入模型选择本身构成研究者自由度 (Levy 等 2015 关于超参驱动表观差异的教训; Rodriguez 与 Spirling 2022 的应用效度框架), 本列以 co-primary 双轨与三 W-轨的并排稳健性设计正面回应这一自由度, 而非假装它不存在。

## VAR: bank_emb_sim_mean_lag1_ctx

【变体差分】
本列是嵌入相似度均值的 ctx (实体上下文窗口) diag W-轨, tier 为 standard, Stata 变量标签为"银行嵌入相似度均值(W=实体窗,滞后1)(对等轨Qwen3-8B)" (2026-07-10 WP3 标签中文化后的现行口径)。它在嵌入模型轴上仍取 canonical 主轨 (Qwen/Qwen3-Embedding-8B, 4096 维), 与 full canonical 列的差分只在 W (文本来源) 轨: 本列不读原始标题与内容, 而是把滞后年每篇报道的 content_ctx——即以"标题前置拼接目标实体窗口"方式在 stage 14 物化的上下文文本——逐篇原样拼接成超级文档。两处刻意设计必须复述准确: 其一, 剔除 ctx_is_fallback 为真的行, 只保留纯 ctx 轨文本参与嵌入; 其二, 禁用标题通道, 因为 content_ctx 已由 prepend_title 内嵌标题, 再拼一次即双标题污染付费嵌入缓存; 剔 fallback、剔空超级文档后有效银行不足 2 家则整轨该年 NaN, 缺 content_ctx 列时整轨跳过不产。其余计算与家族一致: 逐年独立、滞后一期, 分块 token 加权 mean pooling 编码, 余弦对角置零后去对角取行均值, 值域真实 cosine 域 -1 到 1。列名后缀 ctx 的语义是 W 来源轨 (不是情感轨), 这一点与 emb_peer_tone_lag1_ctx 语义为 W_full 乘 tone_ctx 截然不同——本列的 W 与相似度都真正来自 ctx 文本 (对角 diag 语义)。构念意图上, ctx 轨把语义相似度收窄到实体上下文邻域, 检验 canonical 的语义趋同结论是否被报道中与目标银行无关的外围段落所驱动。口径铁律: 本列与 full、ss 两 W-轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J; 作为 ctx 这一独立降级单元 (D8), 本列与其 _lg 孪生 bank_emb_sim_mean_lag1_lg_ctx 单元内严格 both-or-neither, 与 full 族及 ss 单元互不连坐。本机 T=2 开发样本上, ctx 轨因文本更短更易触发有效银行不足或空超级文档而退化, 属预期现象, 该列只作规格稳健性对照, 不单独承重。

## VAR: bank_emb_sim_mean_lag1_lg

【变体差分】
本列是家族 canonical 列的 _lg co-primary 协主孪生 (tier 为 core), Stata 变量标签为"银行嵌入相似度均值(滞后1)(对等轨emb-3-large)" (由 canonical 标签机械派生: 尾注 Qwen3-8B 替换为 emb-3-large, 同属 2026-07-10 WP3 中文化口径)。它与无后缀 canonical 列 bank_emb_sim_mean_lag1 的唯一差分在嵌入模型轴: canonical 用 MAIN spec (Qwen/Qwen3-Embedding-8B, 4096 维, 硅基流动), 本列用 large spec (text-embedding-3-large, 3072 维, yunwu), 且是用各自独立的 spec 嵌入各自的文本、绝不混用不同模型的向量。在 W-轨轴上本列同取 full 基准 (原始标题加正文超级文档, 含标题通道, docid 升序确定性排序), 在滞后与聚合口径上与 canonical 列逐字节一致: 逐年独立、滞后一期 (面板年 t 由 t-1 超级文档算出), 超长超级文档分块加 token 加权 mean pooling, 余弦对角置零后去对角取行均值, sim_mean 建立在未经 clip 的真实余弦上、值域真实 cosine 域闭区间 -1 到 1 (对负余弦的 clip 为 0 只发生在 W_emb 支路、绝不进入本列)。须强调余弦的维度无关性: Qwen 是 4096 维、text-embedding-3-large 是 3072 维, 余弦相似度对向量维度无关, 但两模型的向量绝不跨模型混算——这是嵌入引擎以 emb.shape[1] 驱动、逐 spec 独立编码的设计保证。口径铁律: 本列与 canonical 主轨 bank_emb_sim_mean_lag1 是 co-primary 双轨, 两轨同为主测度、互为稳健性、严格 parity, both-or-neither 且有行级 parity 补强 (审计 F3)——任一 spec 嵌入失败或某 (银行, 年) 键单侧 miss, 两列同时置 NaN, 绝无单边孤儿。最关键的铁律: 两条 co-primary 各自 just-identified 并排, 严禁把 canonical Qwen 与本 _lg emb3large 两轨混进同一个 over-identified 的 Hansen J 检验——它们必须各自单独进入 just-identified 的规格, 作为互为稳健性的两把独立标尺, 而非在一个过度识别检验里被当成两个不同工具变量并联。作为协主而非从属轨, 本列在论文中与 canonical 列地位对等、不分主次; 无后缀并不代表 canonical 更"主", 只是历史命名产物。解读同 canonical: 高值指向语义趋同、低值指向话语差异化, 且同受稠密余弦方法学告诫约束, 应与表层 TF-IDF 认知邻近度互为效度对照。

须进一步说明 co-primary 双轨设计的经济与方法学动机, 以及本列在换嵌入与播种流程中的位置。为何要用两家不同厂商、不同维度的嵌入模型并置为协主, 而不是只用一家? 因为任何单一嵌入模型都带有自己的训练语料偏置与几何结构 (Steck 等 2024 指出稠密嵌入空间的余弦可能失真, 且失真方式与具体模型相关), 若主结论只依赖一家模型的相似度, 就无法排除"结论是这家模型几何构造的产物"这一质疑; 用 Qwen3 (Zhang 等 2025) 与 OpenAI 对比学习嵌入 (Neelakantan 等 2022) 两把独立标尺各自算一遍、并要求主结论在两轨下同号同显著, 才是对嵌入选择稳健性的实质检验——这正是"互为稳健性"的含义, 也是为什么两轨必须各自 just-identified 单独进规格、而绝不能被塞进同一个 over-identified Hansen J (那会把两把独立标尺误当成两个过度识别工具变量并联, 混淆稳健性检验与工具变量识别两件事)。播种与复现层面: canonical 与 _lg 两轨在 T=2 已本机在线播种、可离线零 miss 字节级复现, 生产 T=18 全量播种 DEFERRED、按生产语料实测费用另评; 若未来更换 canonical 嵌入模型 (如已发生的 Google 转阿里 Qwen), 属受控全量重生范畴, 须先过 M0 审批门, 并在手稿披露厂商与维度变更以及 full-only 门控引发的数值副作用 (如相关分母收缩) 均非 bug 而是口径调整。本列与 canonical 列的 both-or-neither 契约保证了两轨列名双射 (both-or-neither, 无单边孤儿列), 使 codebook 与下游模板可安全地成对处理这对协主列。基础设施层面本列与 canonical 列还有两处运行时差异须知悉: 其一, 两轨走不同 API 端点与密钥 (canonical 走硅基流动, 本列走 yunwu 侧端点), 因此两轨的可用性故障是独立事件——恰恰因为可能单侧故障, 行级 both-or-neither 补强才有必要, 否则单侧 per-year miss 会留下不对称覆盖、使"两轨对照"在缺失机制上失去可比性; 其二, 两轨嵌入结果共享同一份 _llm_cache.db 缓存 (缓存键含模型标识故互不冲撞), 离线守卫对两轨同样生效, 任一轨 miss 即 raise 而绝不静默调网。应用效度层面, Rodriguez 与 Spirling (2022) 强调嵌入选型须以领域内效度检验落定, 本列存在的意义正是把这一检验制度化: 若下游结论在 Qwen 轨成立而在本列翻转, 该分歧本身即是须报告的实质发现, 而非可静默丢弃的噪声。

## VAR: bank_emb_sim_mean_lag1_lg_ctx

【变体差分】
本列是 ctx diag W-轨的 _lg co-primary 协主孪生, tier 为 standard, 是 bank_emb_sim_mean_lag1_ctx 在嵌入模型轴上的 _lg 对偶。它同时携带两条轴的非基准取值: 在嵌入模型轴上取 large spec (text-embedding-3-large, 3072 维, yunwu) 而非 canonical 的 Qwen; 在 W-轨轴上取 ctx 而非 full。因此它的超级文档与 bank_emb_sim_mean_lag1_ctx 完全同源——把滞后年每篇报道的 content_ctx (stage 14 以标题前置拼接目标实体窗口物化的上下文文本) 逐篇原样拼接, 剔除 ctx_is_fallback 为真的行、禁用标题通道 (标题已内嵌, 再拼即双标题污染)、剔空超级文档、有效银行不足 2 家或缺 content_ctx 列则该轨跳过——差分只在改用 text-embedding-3-large 独立嵌入这批同源文本。其余计算与家族一致: 逐年独立、滞后一期, 分块 token 加权 mean pooling, 余弦对角置零后去对角取行均值, 值域真实 cosine 域 -1 到 1。列名后缀顺序须记准: _lg 插在 lag1 与 W-轨后缀之间, 即 bank_emb_sim_mean_lag1_lg_ctx, 后缀 ctx 的语义是 W 来源轨。口径铁律: 作为 ctx 这一独立降级单元 (D8) 内的 _lg 侧, 本列与 canonical 侧 bank_emb_sim_mean_lag1_ctx 单元内严格 both-or-neither, 与 full 族及 ss 单元互不连坐; 两条 co-primary (canonical 与 _lg) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J; 三条 W-轨 (full/ctx/ss) 亦各自 just-identified 并排、严禁混进同一 over-identified 的 Hansen J。构念意图上, 本列检验的是"把语义窗口收窄到实体上下文、同时换用另一家厂商的嵌入模型"这一双重扰动下, canonical headline 的语义趋同结论是否稳健。本机 T=2 开发样本上, ctx 轨与 _lg 轨叠加更易触发退化落 NaN, 属预期现象, 该列只作规格稳健性对照, 不单独承重。

## VAR: bank_emb_sim_mean_lag1_lg_ss

【变体差分】
本列是 ss diag W-轨的 _lg co-primary 协主孪生, tier 为 standard, 是 bank_emb_sim_mean_lag1_ss 在嵌入模型轴上的 _lg 对偶。它同时携带两条轴的非基准取值: 在嵌入模型轴上取 large spec (text-embedding-3-large, 3072 维, yunwu); 在 W-轨轴上取 ss (银行与金融科技同句共现窗口) 而非 full。它的超级文档与 bank_emb_sim_mean_lag1_ss 完全同源——把滞后年每篇报道的 content_ss (stage 14 以标题前置拼接"银行与金融科技词在同一句共现的句子及其前后若干句窗口"物化的靶向文本) 逐篇原样拼接, 剔除 ss_is_fallback 为真的行、禁用标题通道、剔空超级文档、有效银行不足 2 家或缺 content_ss 列则该轨跳过——差分只在改用 text-embedding-3-large 独立嵌入这批同源文本。ss 回退语义须与全仓契约一字不差: ss 镜像 ctx, 当一篇报道不存在银行与金融科技同句共现时 content_ss 回退为全文正文且 ss_is_fallback 置真, 而本列构建 ss 轨超级文档时正是剔除这些 fallback 行、只保留真正含同句共现的靶向文本参与嵌入。其余计算与家族一致: 逐年独立、滞后一期, 分块 token 加权 mean pooling, 余弦对角置零后去对角取行均值, 值域真实 cosine 域 -1 到 1; 列名后缀顺序为 _lg 插在 lag1 与 ss 之间。口径铁律: 作为 ss 这一独立降级单元 (D8) 内的 _lg 侧, 本列与 canonical 侧 bank_emb_sim_mean_lag1_ss 单元内严格 both-or-neither, 与 full 族及 ctx 单元互不连坐; 两条 co-primary 各自 just-identified 并排、互为稳健性、不分主次, 三条 W-轨亦各自 just-identified 并排, 二者皆严禁混进同一 over-identified 的 Hansen J。构念意图上, ss 是三轨中语义靶向最强也最短的文本轨, 本列检验的是"把语义窗口收到银行与金科真正同句出现的核心邻域、同时换用另一家厂商嵌入模型"这一双重扰动下结论的稳健性。本机 T=2 开发样本上, ss 文本最短、叠加 _lg 轨, 退化判 NaN 的概率在六列中最高, 该列只作 conditional-on-full 的规格稳健性对照, 不单独承重。

## VAR: bank_emb_sim_mean_lag1_ss

【变体差分】
本列是嵌入相似度均值的 ss (银行与金融科技同句共现窗口) diag W-轨, tier 为 standard, Stata 变量标签为"银行嵌入相似度均值(W=同句,滞后1)(对等轨Qwen3-8B)" (2026-07-10 WP3 标签中文化后的现行口径)。它在嵌入模型轴上仍取 canonical 主轨 (Qwen/Qwen3-Embedding-8B, 4096 维), 与 full canonical 列的差分只在 W (文本来源) 轨: 本列把滞后年每篇报道的 content_ss——即以"标题前置拼接银行与金融科技词同句共现的句子及其前后若干句窗口"方式在 stage 14 物化的靶向文本——逐篇原样拼接成超级文档。两处刻意设计与 ctx 轨同型: 剔除 ss_is_fallback 为真的行、只保留纯 ss 轨文本; 禁用标题通道 (content_ss 已由 prepend_title 内嵌标题, 再拼即双标题污染)。ss 回退语义须与全仓契约一字不差: ss 镜像 ctx, 无银行与金融科技同句共现时 content_ss 回退为全文正文且 ss_is_fallback 置真——本列在构建超级文档时正是剔除这些 fallback 行, 只保留真正含同句共现的靶向文本参与嵌入相似度计算; 剔 fallback、剔空超级文档后有效银行不足 2 家或缺 content_ss 列则整轨该年跳过。其余计算与家族一致: 逐年独立、滞后一期, 分块 token 加权 mean pooling 编码, 余弦对角置零后去对角取行均值, 值域真实 cosine 域 -1 到 1。列名后缀 ss 的语义是 W 来源轨 (不是情感轨), 与 emb_peer_tone_lag1_ss 语义为 W_full 乘 tone_ss 截然不同——本列的 W 与相似度都真正来自 ss 文本 (对角 diag 语义)。构念意图上, ss 是三轨中语义靶向最强也最短的文本轨, 把相似度收窄到"银行与金科真正同句出现"的核心论述邻域, 检验结论是否被外围话语驱动。口径铁律: 本列与 full、ctx 两 W-轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J; 作为 ss 这一独立降级单元 (D8), 本列与其 _lg 孪生 bank_emb_sim_mean_lag1_lg_ss 单元内严格 both-or-neither, 与 full 族及 ctx 单元互不连坐。解读注意: ss 文本最短, 在 T=2 开发样本上退化判 NaN 的概率三轨最高, 该列只作 conditional-on-full 的规格稳健性对照, 不单独承重。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. The Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Tan, L., Wang, C., Sun, J., & Qian, Y. (2026). Measuring corporate risk using large language model embeddings: Evidence on corporate climate risk and supply chain restructuring. SSRN Electronic Journal No. SSRN:6507162 [Working Paper]. https://doi.org/10.2139/ssrn.6507162
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding Benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 3620-3638. https://doi.org/10.18653/v1/2025.emnlp-main.179
Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M. (2025). Asset embeddings. NBER Working Paper No. 33651 No. w33651 [Working Paper]. https://doi.org/10.3386/w33651
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics, 2014-2037. https://doi.org/10.18653/v1/2023.eacl-main.148
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 3980-3990. https://doi.org/10.18653/v1/D19-1410
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
<!-- rendered-citations:end -->
