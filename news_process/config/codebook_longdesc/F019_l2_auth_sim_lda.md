---
family_id: F019
columns:
- auth_sim_lda_ctx
- auth_sim_lda_full
- auth_sim_lda_ss
unit: 相似度 (无量纲, 值域 [0,1]; 1=与政策锚点主题分布完全贴合)
formula: "auth_sim_lda = 1 - sqrt(JSD(theta_bank_year, theta_policy_anchor)); theta 为 LDA 主题分布, JSD 为 Jensen-Shannon 散度; 政策锚点取发布年份 <= t 的政策文档拼接 (前视守卫)"
producer: news_process/pipeline/features/policy_similarity.py::_build_lda_jsd_matrix ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_sbert.parquet (银行年度画像聚合上游)
citations:
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: 111823
- doi: 10.3389/frai.2026.1752103
  type: journal
  authors: Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J.
  year: 2026
  title: "FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  venue: Frontiers in Artificial Intelligence
  vol: 9
  pages_or_artno: 1752103
- doi: 10.1145/3657299
  type: journal
  authors: Xia, B., Rawte, V., Gupta, A., & Zaki, M. J.
  year: 2024
  title: "FETILDA: Evaluation framework for effective representations of long financial documents"
  venue: ACM Transactions on Knowledge Discovery from Data
  vol: 18
  issue: 7
  pages_or_artno: 1-27
- doi: 10.18653/v1/2025.emnlp-main.1135
  type: journal
  authors: Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S.
  year: 2025
  title: "Interpretable text embeddings and text similarity explanation: A survey"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 22314-22330
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
- doi: 10.1257/aer.20191823
  type: journal
  authors: Caldara, D., & Iacoviello, M.
  year: 2022
  title: "Measuring geopolitical risk"
  venue: American Economic Review
  vol: 112
  issue: 4
  pages_or_artno: 1194-1225
new_dois: []
---

## CORE

【构念与来源】
本家族度量银行年度战略画像与宏观权威政策锚点在潜在主题空间上的贴合度, 即"权威政策战略响应度"(authoritative policy alignment) 的 LDA 主题分布实现。构念动机是: 一家银行在其新闻文本所折射的年度战略叙事, 究竟在多大程度上收敛于当年及此前监管者所发布的政策议程。相较直接读取政策关键词命中率, 本家族把银行文本与政策文本共同投影到一组潜在主题上, 用主题分布之间的接近程度刻画"议题结构上的对齐", 从而对同义改写、话术差异与词面不一致更为稳健。数据来源有两支: 银行侧文本来自本流水线 stage 14 物化的三轨文本 (content_full / content_ctx / content_ss), 先在银行-年度层面聚合为年度画像 (先聚合后向量化, 以年度汇总消解单篇报道的特质白噪音, 使主题分布反映银行当年的整体战略叙事而非个别报道的措辞波动); 政策侧文本来自监管政策原文语料, 以其为参照锚点, 呼应 Liu、Cao 与 Wen (2024) 在中国情境下以政企文本余弦对齐度量并为其定价的先例, 以及 Caldara 与 Iacoviello (2022) 以文本为基础构造宏观政策/风险测度的范式。

【方法学与计算】
计算入口在 policy_similarity.py 的 ghost-anchor 相似度模块, 由面板构建器 (pipeline/panel/runner.py) 作为 panel 构建步骤之一在面板导出链路 (stage 40 面板导出) 中调用 compute_authoritative_similarity, 而非独立注册阶段; 模块日志中的 authoritative_similarity 标签仅为该步骤的日志前缀, 不对应 DAG 中的编号阶段。方法 C 即 LDA 主题轨: 把银行年度聚合文本与政策锚点文本一并纳入同一 LDA 主题模型, 得到各自的主题分布 theta; 随后计算银行分布与锚点分布之间的 Jensen-Shannon 散度 JSD, 并以 1 - sqrt(JSD) 作为最终相似度, 使值域落在 [0,1] 且方向为"越大越贴合"。选用 JSD 而非 KL 散度, 因其对称、有界且对零概率主题稳健; 取平方根再做 1 减是把散度转成满足度量三角不等式的距离后再翻转为相似度。锚点采取前视守卫的 vintage 口径: 每个年度 t 只拼接发布年份不晚于 t 的政策文档, 杜绝用未来政策解释当期战略的前视偏误; 当某年无可用政策文档时, 该年 auth_sim_lda 置 NaN 而非回填。为与 stage 25 的 LDA K 值稳定性保持一致, 设最低银行门槛为每年 3 家, 不足则该年跳过。本轨为纯 CPU 确定性计算 (同锚点同输入确定性产同值), 不涉付费嵌入, 因此在 golden 复现上属零成本、零网络。此外家族之外并列产出结构完全相同的 auth_sim_lda_allv 稳健孪生 (静态全语料锚点, 含未来政策文本), 作 anchor-robustness 对照, 不属本三列家族。

【文献定位】
方法学谱系上, 以 LDA 主题分布刻画金融披露文本的做法有长期传统, 近期在金融域的专门化上有 Jehnen、Villalba-Díez 与 Ordieres-Meré (2026) 的 FinTextSim 与 Xia、Rawte、Gupta 与 Zaki (2024) 的 FETILDA 长文档表征评估框架为佐证, 二者均指出通用主题/嵌入表征在金融长文本上需领域适配。相似度算子选择上, Steck、Ekanadham 与 Kallus (2024) 与 You (2025) 提醒余弦相似度在特定几何下会失真, Opitz 等 (2025) 系统梳理了文本相似度的可解释性; 本家族刻意采用主题分布上的 JSD 距离而非嵌入余弦, 与嵌入余弦轨 (auth_sim_emb) 并列构成算子层面的稳健性对照。需强调铁律: LDA 主题轨、TF-IDF 字符/词轨与嵌入主轨/_lg 轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J; 三轨文本 (full/ctx/ss) 亦同此律, 各轨各自识别、不得跨轨拼装工具变量集。

## VAR: auth_sim_lda_full

【变体差分】
本列是 LDA 主题相似度的 full 文本轨实现, 也是本家族与留篇门控口径对齐的主轨。full 轨的银行年度画像文本取自 content_full, 即标题 prepend 后拼接全文正文的完整报道; 相较 ctx/ss 两轨只截取实体窗口或同句共现片段, full 轨保留了报道的全部语境, 主题分布覆盖最广、对长尾议题最敏感, 因而最贴近"银行整体战略叙事 vs 政策议程"这一构念的原始意图。与 full-only 留篇门控 (2026-06-29) 一致: 一篇报道是否计入银行年度语料由 llm_verified_full 判定, ctx/ss 轨为 conditional-on-full 的子集测度; 因此 full 轨的行宇宙即留篇集本身, 分母口径最完整。计算上本列走 1 - sqrt(JSD(theta_bank_full, theta_policy)), 政策锚点采前视 vintage 拼接, 最低 3 家银行/年门槛, 无可用政策文档年份置 NaN。本列与同族 ctx/ss 列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 亦与同 stage 的 TF-IDF 字符/词轨、嵌入主轨/_lg 轨分属不同算子, 同律隔离, 不得跨算子拼装同一工具变量集。使用建议以本列为主报测度, ctx/ss 作稳健性旁证。需注意本列虽名为无后缀家族的 full 轨, 但其"最广语境"的代价是主题分布易被报道中与政策议题无关的背景段落稀释, 因此在解释系数时应与 ctx 主题轨对照读: 若两轨方向一致, 说明贴合度信号不依赖语境截取方式而稳健; 若 full 轨显著而 ctx 轨不显著, 则提示对齐可能来自宽泛背景叙事而非银行主体的实质战略回应, 应审慎归因。此外本列在开发 T=2 语料上因政策锚点年份稀疏可能出现较多 NaN, 属前视守卫的预期表现, 生产 T=19 语料下随可用政策文档增多而恢复覆盖, 勿据 T=2 覆盖率评判本轨有效性。

## VAR: auth_sim_lda_ctx

【变体差分】
本列是 LDA 主题相似度的 ctx (实体上下文窗口) 文本轨。ctx 轨的银行年度画像文本取自 content_ctx, 即标题 prepend 后仅保留目标银行实体邻近窗口的片段, 而非全文; 因此其主题分布聚焦于"围绕银行主体展开的局部议题", 剔除了报道中与银行无关的背景段落对主题贴合度的稀释。与 full 轨相比, ctx 轨对"银行确实被置于某政策议题语境中"这一更严格的语义更敏感, 是 full 主轨的 conditional-on-full 稳健性轨: 其行宇宙为 full 留篇集的子集, 分母按本轨自身有效篇数逐轨计算, 不借用 full 分母。计算算子与 full 列同构, 均为 1 - sqrt(JSD(theta_bank_ctx, theta_policy)), 同样采前视 vintage 政策锚点、3 家银行/年最低门槛、无政策文档年份置 NaN。回退语义上 ctx 轨若无可用实体窗口则相应 *_is_fallback 上游标记生效, 优雅降级。本列与 full/ss 两轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J, 亦禁与 TF-IDF/嵌入算子轨跨算子拼装工具变量。在开发 T=2 语料上 ctx 轨可能因窗口稀疏出现更多 NaN, 属预期退化, 生产 T=19 语料下恢复正常。判据口径上须提醒, ctx 轨的"实体上下文窗口"是文本截取层面的三轨维度, 与 stage 13 共现硬过滤的句窗半径、以及网络指标的三判据后缀是彼此独立的键, 不可混用或相互复用其原语。使用上本列相较 full 轨更能排除报道背景噪音, 相较 ss 轨又保留了非严格同句但仍围绕银行主体的邻近语料, 因此在"聚焦度"上居中, 常作为 full 主轨与 ss 严格轨之间的桥接稳健性证据: 三轨系数若单调过渡, 可佐证贴合度信号随语义约束收紧而平滑变化, 而非由某一截取方式的伪影驱动。

## VAR: auth_sim_lda_ss

【变体差分】
本列是 LDA 主题相似度的 ss (银行与金科同句共现窗口) 文本轨, 是三轨中语义约束最强的一支。ss 轨的银行年度画像文本取自 content_ss, 即标题 prepend 后仅保留目标银行与金融科技词在同句 (±N 句窗, 默认半径 1) 共现的片段; 因此其主题分布锁定"银行与金科议题真正同句交汇"处的语料, 对"政策议程 vs 银行金科战略在议题结构上是否对齐"这一最窄构念最敏感。ss 轨的回退语义镜像 ctx: 当某篇报道无银行与金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True (与 n_articles 共享分母口径); 当上游金科 AC 词表为 None 时 *_is_fallback 全 True 优雅降级。计算算子与 full/ctx 同构, 为 1 - sqrt(JSD(theta_bank_ss, theta_policy)), 采前视 vintage 政策锚点、3 家银行/年门槛、无政策文档年份置 NaN。作为 conditional-on-full 稳健性轨, 其行宇宙为 full 留篇集子集, 分母逐轨自算不借 full。本列与 full/ctx 两轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J, 亦与 TF-IDF/嵌入算子轨同律隔离。开发 T=2 语料上 ss 轨因同句共现稀疏而 NaN 比例最高, 属预期退化, 生产语料下方具区分力。须区分两个不同键: ss 轨的同句共现判据 (config filtering context_window ss_sentence_radius, 默认半径 1) 与 stage 13 共现硬过滤的 cooccurrence_filter sentence_radius 是两个独立配置项, 前者服务于 ss 文本物化、后者服务于上游留行硬过滤, 二者原语判据不同 (ss 用严格同句共现的 extract 口径, stage 13 用 within_radius 邻近口径), 禁互相复用。在解释力上, 因 ss 轨语料最纯净、与政策议题最贴近, 其主题分布对"银行金科战略是否真正响应政策议程"最具针对性, 适合作为主结论的最强稳健性锚: 若 full/ctx/ss 三轨随语义约束收紧仍给出方向一致的贴合度信号, 则可较有力地排除对齐仅为宽泛背景叙事产物的替代解释。反之若仅 ss 轨微弱或多 NaN, 应回到 full 主轨审慎报告并披露 ss 轨的样本稀疏局限。

<!-- rendered-citations:begin -->
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, 1752103. https://doi.org/10.3389/frai.2026.1752103
Xia, B., Rawte, V., Gupta, A., & Zaki, M. J. (2024). FETILDA: Evaluation framework for effective representations of long financial documents. ACM Transactions on Knowledge Discovery from Data, 18(7), 1-27. https://doi.org/10.1145/3657299
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Caldara, D., & Iacoviello, M. (2022). Measuring geopolitical risk. American Economic Review, 112(4), 1194-1225. https://doi.org/10.1257/aer.20191823
<!-- rendered-citations:end -->
