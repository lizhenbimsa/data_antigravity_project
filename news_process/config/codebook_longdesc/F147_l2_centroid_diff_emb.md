---
family_id: F147
columns:
- centroid_diff_emb
- centroid_diff_emb_ctx
- centroid_diff_emb_lg
- centroid_diff_emb_lg_ctx
- centroid_diff_emb_lg_ss
- centroid_diff_emb_ss
unit: 语义质心距离 (无量纲余弦距离, 值域 [0, 2])
formula: "centroid_diff_emb = 1 - cos(c_i, c_{-i}); c_i = mean_a( emb(doc_a) for a in bank_i-year 文档集 ); c_{-i} = leave-one-out 行业质心 = (n·c − c_i)/(n−1) (排除银行 i 自身后的同年样本质心均值); n<2 → NaN; emb = 嵌入引擎句向量 (full 轨 Qwen3-Embedding-8B / _lg 轨 text-embedding-3-large)"
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_sbert.parquet (co-primary 双轨句向量 emb_full/_lg)
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
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: 40
  issue: 1
  pages_or_artno: 3-27
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: Levy, O., Goldberg, Y., & Dagan, I.
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of EMNLP-IJCNLP 2019
  pages_or_artno: 3980-3990
- doi: "10.1016/j.jfineco.2025.104007"
  type: journal
  authors: "Breitung, C., & Müller, S."
  year: 2025
  title: "Global Business Networks"
  venue: "Journal of Financial Economics"
- doi: "10.1016/j.iref.2025.104785"
  type: journal
  authors: "Fu, R., Gao, F., & Ma, C."
  year: 2025
  title: "Do peer narrative disclosures support or disrupt efficient investment?"
  venue: "International Review of Economics & Finance"
- doi: "10.2139/ssrn.6725723"
  type: "wp"
  authors: "de Bodt, E., & Eckbo, B. E."
  year: 2026
  title: "An improved text-based industry peer-firm identification algorithm"
  venue: "SSRN Working Paper"
new_dois:
- "10.1016/j.jfineco.2025.104007"
- "10.1016/j.iref.2025.104785"
- "10.2139/ssrn.6725723"
---

## CORE

【构念与来源】
本家族度量银行在媒体叙事语义空间中相对于全行业平均的偏离程度, 即一种基于稠密语义嵌入的战略差异化 (strategic differentiation) 测度。构念的直觉是: 若一家银行当年的新闻报道文本在向量空间中的重心 (质心) 距离全行业所有银行当年报道的共同重心越远, 则该行的叙事定位越独特、越偏离行业主流话语; 反之, 质心贴近行业中心意味着该行的媒体形象与同业高度趋同、缺乏辨识度。这一"与众不同"的构念承袭管理学差异化文献: Haans (2019) 在同质与异质品类下考察独特性对绩效的非线性作用, 指出差异化的价值取决于其所处品类的拥挤度, 为把"偏离行业中心的距离"作为可解释的战略变量提供了理论根基。方法学血统上, 本模块迁移自计量文本研究中的全行业向量法实证范式: 该范式先把每家机构当年的文本投影为向量, 再以其与全行业向量重心的距离刻画战略偏离, 本项目将其由基于离散主题分布 (如 BERTopic 主题相似度) 的口径改造为直接落在稠密语义嵌入上的"行业质心距离", 从而保留细粒度语义信息而非退化到少数主题维度。这一以嵌入几何刻画机构立场偏离的做法, 与金融文本计量前沿把海量文本投影到稠密向量空间再以向量几何度量机构变量的思路一脉相承 (Jha, Liu 与 Manela, 2026)。

【方法学与计算】
计算分三步。第一步, 对每篇报道用嵌入引擎生成一条句向量 emb(doc); 全轨 (无 _lg 后缀) 使用 canonical 主测度 Qwen3-Embedding-8B (硅基流动, 4096 维), _lg 轨使用跨厂商对偶 text-embedding-3-large (3072 维)。第二步, 把某银行-年内所有报道的句向量取算术平均, 得到该银行的文档质心 c_i; 再构造该银行的 leave-one-out 行业质心 c_{-i}, 即把全行业同年样本的银行质心均值在排除银行 i 自身后重算——闭式为 c_{-i} = (n·c − c_i)/(n−1), 其中 c 为含全部 n 家银行的总质心。之所以排除自身而非直接用含自身的行业均值, 是因为后者会使 cos(c_i, c) 混入约 1/n_t 量级的机械自相关, 且对与行业越正交的银行抬升越多, 从而系统性压缩 centroid_diff 的右尾 (此为生产口径明确弃用的行为, 与模块内 N-最近邻路径对角置 NaN、流动性度量排除自身的既有惯例一致)。当某银行-年样本内有效银行数 n<2 时, leave-one-out 行业质心无定义, 该格返回 NaN 而非强行取值。第三步, 计算 c_i 与 c_{-i} 的余弦距离 centroid_diff = 1 − cos(c_i, c_{-i})。因余弦相似度真值域为 [−1, 1], 对应距离列真值域为 [0, 2]; 生产口径已修正历史上把嵌入轨统一 clip 到 [0, 1] 的值域删失问题——负余弦不再被地板到 0, 而是如实映射到 (1, 2] 区间。需要强调, 余弦几何本身并非无争议: Steck 等 (2024) 指出正则化训练下嵌入的余弦相似度未必对应语义相似度的直觉尺度, 因此本度量在解释上只做行内跨行的相对比较 (哪家更偏离中心), 不对距离绝对水平赋予语义, 也不跨嵌入空间比较距离水平。嵌入引擎为纯 API 调用, 维度由返回矩阵形状驱动、与维度无关; 句向量表征的可行性由 Sentence-BERT (Reimers & Gurevych, 2019) 奠基, 而分布式表征"距离即语义差异"的合法性可追溯到 Levy 等 (2015) 对分布相似度的系统检讨。

【文献定位】
在金融文本计量脉络中, 以语言嵌入构造机构级经济变量已成方法学前沿。Jha, Liu 与 Manela (2026) 在《Review of Financial Studies》提出语言嵌入方法度量金融是否惠及社会, 系统论证了把海量文本投影到稠密向量空间、再以向量几何刻画机构立场的可行性与识别价值, 是本家族"以质心距离刻画银行叙事定位"的最直接顶刊参照。嵌入底座方面, 主轨 Qwen3-Embedding-8B 的技术规格见 Zhang 等 (2025), 对偶轨 text-embedding-3-large 的对比预训练底座见 Neelakantan 等 (2022); 二者分属阿里与 OpenAI 两个独立厂商与维度, 构成 co-primary 双轨。方法学铁律: 全轨与 _lg 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 距离列混入同一 over-identified Hansen J; 同理三条文本轨 (full/ctx/ss) 亦各自 just-identified 并排、禁混同一 Hansen J。差异化构念的绩效含义与非线性则由 Haans (2019) 提供解释框架。同一方法学脉络还可见于 Breitung 与 Müller (2025, Journal of Financial Economics), 该文用文本嵌入向量的余弦相似度矩阵刻画企业间业务联系并构建全球商业网络, 与本家族用嵌入余弦距离刻画银行相对行业质心的语义偏离度同属以嵌入几何度量机构级经济关系的方法学脉络。用同业 MD&A 叙事文本相似度度量同业信息趋同度, 发现同业叙事相似度越低、行业专属信息越丰富、投资效率越高, 为本家族以质心距离刻画机构叙事偏离度的构念提供最新同业文本相似度实证参照, 见 Fu, Gao 与 Ma (2025, International Review of Economics & Finance)。提出概率加权余弦相似度评分, 将向量嵌入文本网络方法与传统同业特征识别相结合以构建行业同业组, 为本家族嵌入余弦几何刻画机构行业偏离度的方法学谱系补充最新同业识别文献, 见 de Bodt 与 Eckbo (2026, SSRN Working Paper)。

## VAR: centroid_diff_emb

【变体差分】
本列为家族 canonical 度量, 采用 full 文本轨与主测度嵌入 Qwen3-Embedding-8B (无 _lg 后缀)。full 轨文本 = content_full, 即标题 prepend 后拼接全文正文 (原始正文列不改动), 是信息最全的轨道, 承载银行当年媒体叙事的完整语义。命名上遵循 producer 列约定: n5_emb / sim_max_emb / centroid_diff_emb 这三族的 full 轨取裸名 (无 _full 后缀), 而其余族的 full 轨带 _full——因此本列虽无后缀却确为 full 轨, 不可误读为"轨道无关"的元数据列。质心由该银行-年 full 轨全部报道句向量平均得到; 与之比较的行业质心取 leave-one-out 口径, 即把全行业同年 full 轨样本的银行质心均值在排除本行自身后重算 (c_{-i} = (n·c − c_i)/(n−1)), 距离 = 1 − 余弦相似度, 真值域 [0, 2]。排除自身是为避免含自身的行业均值把约 1/n_t 量级的机械自相关灌进 cos 值、系统性压缩偏离度右尾; 当同年有效银行数 n<2 时 leave-one-out 质心无定义, 该格置 NaN。作为 canonical, 本列是家族内其余五个变体的比较基准: 各变体只在文本轨或嵌入厂商上与本列相异, 计算链路完全一致。本列与 _lg 对偶列 centroid_diff_emb_lg 构成 co-primary 双轨, 二者 both-or-neither 降级 (任一嵌入缺失则两列同置 NaN, 无单边孤儿), 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。留篇门控口径遵循 full-only (2026-06-29): 是否判为一篇银行金科报道只看 full 轨的留篇集, 本列作为 full 轨 canonical 直接落在这一留篇宇宙之上, 分母口径与全项目 full-only 口径一致, 不因 ctx/ss 轨的条件化而收缩。实证解读上, 本列取值越大表示该行当年媒体叙事在稠密语义空间中越偏离全行业重心、辨识度越高; 取值贴近 0 表示叙事高度趋同同业。因余弦几何在正则化嵌入下的绝对水平缺乏统一语义尺度 (参见方法学段对 Steck 等 2024 的讨论), 本列只用于行内跨行的相对排序与偏离度比较, 不对距离绝对值赋予跨样本的语义解释, 亦不与其余五个变体做跨轨/跨厂商的距离水平直接相减。

## VAR: centroid_diff_emb_ctx

【变体差分】
本列相对 canonical 的唯一差分在文本轨: 由 full 轨切换为 ctx (上下文实体窗口) 轨, 嵌入仍为主测度 Qwen3-Embedding-8B (无 _lg 后缀)。ctx 轨文本 = content_ctx, 即标题 prepend 后只保留银行/金科实体命中处附近的上下文窗口, 剔除与目标实体无关的段落, 使质心更聚焦于"围绕本行的报道语境"而非全文泛化叙事。因此本列度量的是银行在实体聚焦语境下的叙事偏离度, 与 full 轨的全文偏离度互为稳健性, 二者各自 just-identified 并排、不分主次, 严禁混入同一 over-identified Hansen J。计算链路 (银行-年 ctx 轨句向量平均得质心、leave-one-out 排除本行后取全行业同年 ctx 轨质心均值得行业质心 c_{-i}=(n·c−c_i)/(n−1)、余弦距离 1 − cos、值域 [0, 2]、n<2 置 NaN) 与 canonical 完全一致, 仅输入文本轨不同。ctx 轨在 stage 14 ctx_materializer 物化 (prepend_title, 原始正文列不动), 保留 ctx_is_fallback 标记以标注无实体命中而回退全文的样本; 回退发生时该样本 content_ctx 退化为全文正文, 语义上等同 full 轨输入, 因此高回退比例的年份 ctx 与 full 两轨会趋同, 属预期而非缺陷。作为 conditional-on-full 的稳健性轨, 本列的行宇宙是 full 轨留篇集的子集, per-track 质心与距离照常逐轨计算, 但留篇判定不由 ctx 轨自身决定。本列与 _lg 对偶列 centroid_diff_emb_lg_ctx 构成 co-primary 双轨, both-or-neither 降级, 严禁混入同一 Hansen J; 与同厂商 full/ss 两轨构成三轨稳健性并排, 亦各自 just-identified、不分主次。实证解读与 canonical 一致: 取值大表示实体聚焦语境下叙事偏离行业中心, 仅作行内跨行相对比较。

## VAR: centroid_diff_emb_lg

【变体差分】
本列相对 canonical 的唯一差分在嵌入厂商: 文本轨仍为 full, 但嵌入由主测度 Qwen3-Embedding-8B (4096 维, 硅基流动) 切换为跨厂商对偶 text-embedding-3-large (3072 维, OpenAI 系, _lg 后缀)。这是 co-primary 双轨中的第二条主测度, 而非"稳健性检验的次轨"——两条轨对等互证, 严禁在标签或文档中使用 robust/robustness check 措辞暗示主次。_lg 轨的对比预训练底座见 Neelakantan 等 (2022), 其向量维度与训练语料、几何空间均与 Qwen 主轨不同, 因此两列的距离绝对水平不可跨空间比较, 只能在各自空间内做行内跨行的相对排序。本列与 canonical centroid_diff_emb 构成 both-or-neither 双轨: 任一嵌入 API 返回缺失则两列同置 NaN, 不产生单边孤儿列; 二者各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。计算链路 (银行质心、leave-one-out 排除本行后的全行业同年质心均值 c_{-i}=(n·c−c_i)/(n−1)、余弦距离、值域 [0, 2]、n<2 置 NaN) 与 canonical 一致, 仅嵌入引擎不同。维度差异由引擎按返回矩阵形状自动驱动, 度量本身维度无关, 3072 维与 4096 维在各自空间内独立成立。此双轨设计的目的在于证明"银行叙事偏离行业中心"这一结论不被单一嵌入厂商或单一向量几何所驱动: 若两条 co-primary 轨在回归中给出方向一致的系数, 则测量层面的稳健性得到跨厂商佐证。text-embedding-3-large 的对比预训练范式使其向量在语义检索任务上表现优异 (Neelakantan 等 2022), 与 Qwen3 主轨形成互证而非替代。留篇门控同样遵循 full-only, 本列作为 full 轨 _lg 对偶落在 full 留篇宇宙之上, 分母口径与 canonical 对称。

## VAR: centroid_diff_emb_lg_ctx

【变体差分】
本列是 _lg 对偶轨与 ctx 文本轨的组合: 嵌入为 text-embedding-3-large (_lg, OpenAI 系, 3072 维), 文本轨为 ctx (实体上下文窗口, content_ctx)。它同时在两个维度上偏离 canonical centroid_diff_emb——嵌入厂商 (Qwen→text-embedding-3-large) 与文本轨 (full→ctx)——因而在 co-primary 双轨与三文本轨两套稳健性网格的交叉格点上取值。语义上, 本列度量银行在实体聚焦语境下、经 OpenAI 嵌入空间投影后的叙事偏离度, 与 centroid_diff_emb_ctx (Qwen 主轨同 ctx) 构成 co-primary 双轨、both-or-neither 降级, 又与 centroid_diff_emb_lg (同厂商 full 轨) 构成三轨稳健性并排。所有并排关系均遵循同一铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 或三条文本轨混入同一 over-identified Hansen J。计算链路 (银行-年 ctx 轨句向量平均得质心、leave-one-out 排除本行后取全行业同年 ctx 轨质心均值得行业质心 c_{-i}=(n·c−c_i)/(n−1)、余弦距离 1 − cos、值域 [0, 2]、n<2 置 NaN) 与 canonical 一致, 仅嵌入引擎与输入文本轨相异。作为交叉格点列, 本列在 co-primary 双轨网格与三文本轨网格的交点上取值, 但两套网格刻意保持正交、不交叉相乘进同一 over-identified 设定: 任何一次 IV 或 GMM 只取网格中的单一格点作 just-identified 使用。ctx 轨回退语义与主轨 ctx 完全一致 (无实体命中则 content_ctx 退化全文正文、ctx_is_fallback=True), 因此本列高回退年份会与 centroid_diff_emb_lg (同厂商 full 轨) 趋同, 属预期退化。留篇门控遵循 full-only, 本列行宇宙为 full 留篇集子集, per-track 逐轨计算距离而不自定留篇。

## VAR: centroid_diff_emb_lg_ss

【变体差分】
本列是 _lg 对偶轨与 ss 文本轨的组合: 嵌入为 text-embedding-3-large (_lg, 3072 维), 文本轨为 ss (银行∧金科同句共现窗口, content_ss)。ss 轨文本 = 标题 prepend 后只保留银行与金融科技词在同一句子及其 ±N 句半径 (config 键 ss_sentence_radius, 默认 1) 内共现的片段, 是三轨中语境最严格、最聚焦"银行谈金科"主题的轨道。回退语义镜像 ctx: 当某样本无银行∧金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 优雅降级。本列度量银行在"银行谈金科"最严格语境下、经 OpenAI 嵌入空间投影后的叙事偏离度。它与 centroid_diff_emb_ss (Qwen 主轨同 ss) 构成 co-primary 双轨、both-or-neither 降级, 与同厂商 full/ctx 轨构成三轨稳健性并排; 一律各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。计算链路与 canonical 一致 (银行-年 ss 轨句向量平均得质心、leave-one-out 排除本行后取全行业同年 ss 轨质心均值得行业质心 c_{-i}=(n·c−c_i)/(n−1)、余弦距离 1 − cos、值域 [0, 2]、n<2 置 NaN), 仅嵌入引擎与文本轨相异。需特别注意 ss 轨是三轨中最严格的语境, 在开发期 T=2 的小样本上, 同句共现片段稀少可能导致质心由极少数句向量平均而成、方差偏高甚至退化, 属预期的小样本行为; 生产期 T=19 全量语料下该轨可正常识别。作为 conditional-on-full 的稳健性轨, 本列行宇宙为 full 留篇集子集, 留篇判定不由 ss 轨自身作出。实证解读: 取值大表示在"银行谈金科"最严格语境、经 OpenAI 嵌入空间投影后叙事偏离行业中心, 仅作行内跨行相对排序。

## VAR: centroid_diff_emb_ss

【变体差分】
本列相对 canonical 的唯一差分在文本轨: 由 full 切换为 ss (银行∧金科同句共现窗口), 嵌入仍为主测度 Qwen3-Embedding-8B (无 _lg 后缀)。ss 轨文本 = content_ss, 保留标题 prepend 后银行与金融科技词在同句及 ±N 句半径内共现的片段, 是三轨中主题最聚焦的轨道, 使质心刻画"本行金科叙事"而非泛化媒体形象。回退语义镜像 ctx: 无同句共现的样本 content_ss 回退全文正文、ss_is_fallback=True, 共享 n_articles 分母; 留篇门控口径遵循 full-only (2026-06-29)——是否判为一篇银行金科报道只看 full 轨留篇集, ctx/ss 为 conditional-on-full 的测度/稳健性轨, 行宇宙为 full 留篇集的子集。本列与 full/ctx 轨互为稳健性、各自 just-identified 并排、不分主次, 严禁混入同一 over-identified Hansen J; 与 _lg 对偶列 centroid_diff_emb_lg_ss 构成 co-primary 双轨、both-or-neither 降级。计算链路 (质心平均、leave-one-out 排除本行后的全行业同年质心均值 c_{-i}=(n·c−c_i)/(n−1)、余弦距离、值域 [0, 2]、n<2 置 NaN) 与 canonical 完全一致, 仅输入文本轨不同。语义上本列刻画的是"本行金科叙事"相对全行业金科话语中心的偏离度: 相比 full 轨的全文泛化偏离、ctx 轨的实体聚焦偏离, ss 轨把语境收窄到银行与金融科技词同句共现的片段, 因而对"该行如何被媒体描述其金科动作"这一主题最敏感。作为主测度 Qwen 轨的 ss 变体, 本列与 full/ctx 两轨互为稳健性、各自 just-identified 并排, 用以检验战略差异化结论是否稳健于语境窗口的宽窄选择。开发期 ss 轨小样本退化 (同句共现稀少导致质心方差偏高) 属预期, 生产期全量语料正常。本列只用于行内跨行相对比较, 不对距离绝对水平赋予跨样本语义。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., & Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of EMNLP-IJCNLP 2019, 3980-3990. https://doi.org/10.18653/v1/D19-1410
Breitung, C., & Müller, S. (2025). Global Business Networks. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2025.104007
Fu, R., Gao, F., & Ma, C. (2025). Do peer narrative disclosures support or disrupt efficient investment?. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2025.104785
de Bodt, E., & Eckbo, B. E. (2026). An improved text-based industry peer-firm identification algorithm. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.6725723
<!-- rendered-citations:end -->
