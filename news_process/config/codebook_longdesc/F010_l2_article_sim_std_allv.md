---
family_id: F010
columns:
- article_sim_std_allv
- article_sim_std_allv_ctx
- article_sim_std_allv_ss
- article_sim_std_lg_allv
- article_sim_std_lg_allv_ctx
- article_sim_std_lg_allv_ss
unit: 余弦相似度的组内样本标准差 (无量纲, 底层相似度 ∈ [0,1], 标准差 ≥ 0)
formula: "article_sim_std_allv = sample_std_{i ∈ (target_bank, year)}(policy_cosine_sim_allv_i), ddof=1; 单篇 bank-year → NaN (不填 0); policy_cosine_sim_allv = cos(E(文章), E(政策锚点_全语料静态)); 后缀 _ctx/_ss 为文本轨, _lg 为 text-embedding-3-large co-primary 对偶轨"
producer: news_process/pipeline/panel/runner.py (连续聚合块 groupby[target_bank, year].agg std)
upstream:
- 16_article_policy_alignment.parquet (policy_cosine_sim_allv{,_ctx,_ss}, policy_cosine_sim_lg_allv{,_ctx,_ss})
- 14_materialize_ctx.parquet (content_ctx / content_ss 三轨文本)
- 15_fintech_intensity.parquet (co-primary 双轨嵌入向量)
citations:
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: Article 102325
- doi: 10.3389/frai.2026.1752103
  type: journal
  authors: Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J.
  year: 2026
  title: "FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures"
  venue: Frontiers in Artificial Intelligence
  vol: 9
  pages_or_artno: Article 1752103
- doi: 10.1007/s11205-026-03831-x
  type: journal
  authors: Muñoz, J. F., Pavía, J. M., & Álvarez-Verdejo, E.
  year: 2026
  title: "A practical guide to proper estimation and inference of the Gini index by avoiding often encountered methodological pitfalls"
  venue: Social Indicators Research
  vol: 183
  issue: 1
  pages_or_artno: Article 2
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: Article 111823
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
本家族刻画的是"某家目标银行在某一年度内, 其相关报道与政策文本语义对齐程度的年内离散度", 即把文章级的政策余弦相似度 policy_cosine_sim_allv 按 (target_bank, year) 聚合后取样本标准差得到的 bank-year 面板列。底层的文章级测度 policy_cosine_sim 由 stage 16 article_policy_alignment 产出: 先在 stage 15 fintech_intensity 用嵌入引擎把每篇报道正文与预置的政策语料锚点各自映射成稠密向量, 再取二者的余弦相似度, 落在 [0,1] 区间, 越高表示该篇报道在语义上越贴近政策话语。本家族与"均值"族 article_sim_mean_allv 同源但取二阶矩: 均值刻画年内平均对齐水平, 标准差刻画年内对齐的分散或异质程度 —— 一个银行若这一年的报道在政策语义上时而高度贴合、时而完全脱离, 其标准差就大, 反之若全年报道对齐度整齐划一则标准差小。这一"年内语义离散度"作为构念, 既可作为衡量报道口径一致性的自变量, 也可作为均值测度的稳健性伴随列。本家族的 _allv 后缀是关键身份标记: 它不是主轨的 policy_cosine_sim, 而是"全年份锚点稳健孪生"(2026-06-21 引入)。主轨政策锚点可能随年份取值, 而 _allv 使用在全语料范围内一次性冻结的静态政策锚点 (全语料静态锚点), 消除锚点随年漂移带来的机械共动。因此主轨相似度族与 _allv 静态锚点族构成一条锚点选择稳健性阶梯: 二者各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验 [CLAUDE.md 铁律]。

【方法学与计算】
计算发生在 pipeline/panel/runner.py 的"连续聚合"块内: 对已过滤到 verified 留篇宇宙的文章级 DataFrame 按 (target_bank, year) 分组, 用 pandas 的 std 聚合器 (ddof=1, 样本标准差) 对 policy_cosine_sim_allv 求组内标准差, 生成 article_sim_std_allv, 与均值列 article_sim_mean_allv 成对合并回面板。一个刻意的裁决 (omni-group-std-singleobs, 2026-06-11) 是: 单篇文章的 bank-year 其 ddof=1 标准差数学上未定义, 引擎保持 NaN 而不强填 0.0 —— 强填 0 会把"离散度不可估计"伪装成"零分歧"的假观测, 与本项目"无数据即未测量"的缺失语义冲突。因此使用本列做回归时须注意: NaN 行是单篇年度而非零方差年度, 计量上应作缺失处理而非零值处理。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入 bank-year 宇宙只看其 full 轨是否 verified, ctx/ss 轨降为 conditional-on-full 的测度轨, 各 per-track 列在该 full 留篇子集上照算, 分母语义与 n_articles 保持一致。三条文本轨 full/ctx/ss 与 co-primary 双轨嵌入 (无后缀 Qwen 主轨 vs _lg 的 text-embedding-3-large) 均在此块以 both-or-neither 列名双射的方式并列聚合: 有主轨列必有 _lg 孪生列, 缺源列时整对优雅跳过而非留单边孤儿。ss 轨的回退语义镜像 ctx: 当某篇缺银行∧金科同句共现时 ss 文本回退为全文正文并置 is_fallback 标记。

【文献定位】
以余弦相似度度量文本与政策/官方语料的贴近程度已成为中国情境下的成熟做法, Liu, Cao 和 Wen (2024) 直接构造企业与政府文本的余弦相似度并研究其定价含义, 是本家族 policy_cosine_sim 最贴近的方法学先例。以领域专用句向量提升金融文本语义表征质量的路线由 Jehnen, Villalba-Díez 和 Ordieres-Meré (2026) 的 FinTextSim 系统化论证, 支持本项目以嵌入余弦而非词频重叠作为对齐测度的选择; Chen, Granville 和 Matousek (2026) 用大语言模型解码央行政策沟通, 印证了政策文本可被嵌入空间稳定表征, 为静态政策锚点的构造提供依据。相似性指数本身的度量学问题由 Mainali, Slud, Singer 和 Fagan (2022) 系统讨论, 提示不同相似指数在偏差与可比性上的差异, 支持本家族以固定锚点、固定余弦口径来保证跨年可比。以文本/向量间的语义相似度来量化经济主体之间的贴近或差异, 并进一步以其分散度作为构念, 亦有一线管理学证据支撑: Arts, Cassiman 和 Hou (2025) 在 Strategic Management Journal 上以专利技术描述的文本相似度度量企业间技术差异化, 并将该相似度结构作为解释产品市场竞争与并购行为的自变量, 印证了"以相似度及其离散度作为可回归构念"这一测量路径的合法性, 与本家族把年内政策余弦相似度的样本标准差用作报道口径异质度自变量的做法同构。就"标准差作为组内离散度"这一二阶矩测度而言, Gelman (2008) 关于以两倍标准差缩放回归输入的讨论说明标准差在回归语境中兼具尺度与离散双重含义, 而 Muñoz, Pavía 和 Álvarez-Verdejo (2026) 关于离散/不平等指数在小样本下估计与推断陷阱的指南, 恰与本家族对单篇年度不可估计而置 NaN 的处理相呼应。

## VAR: article_sim_std_allv

【变体差分】
本列是家族的 canonical 锚点: co-primary 主轨嵌入 (无后缀, 即硅基流动 Qwen/Qwen3-Embedding-8B, 4096 维), full 文本轨 (标题 prepend + 全文正文), 全语料静态政策锚点 (_allv)。它对文章级 policy_cosine_sim_allv 按 (target_bank, year) 取 ddof=1 样本标准差, 度量该银行该年内报道-政策语义对齐的分散程度。与家族其余五列相比, 本列在三个身份维度上都取"主"取值: 文本轨=full (非 ctx/ss)、嵌入轨=Qwen 主轨 (非 _lg)、故不带任何 _ctx/_ss/_lg 中缀。full-only 留篇门控意味着本列的分组宇宙即整个 verified 报道集, 是六列中样本最完整、统计最稳的一列, 通常作为主回归所用的年内离散度测度, 其余五列为其稳健性伴随。需强调 _allv 相对于非 _allv 主轨相似度的差别: 本列使用冻结于全语料的静态政策锚点, 而非可能随年份变动的锚点, 从而剥离锚点年漂移导致的机械共动。锚点静态族与主轨族互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。单篇年度置 NaN (不填 0) 的语义在本列同样成立: NaN 表示离散度不可估计而非零分歧, 回归中须按缺失处理。就消费口径而言, 本列既可作为报道口径一致性的直接自变量, 也常作为均值列 article_sim_mean_allv 的稳健性伴随: 若某银行某年的政策对齐既高又整齐, 均值高而本列标准差低; 若对齐水平在年内剧烈摆动, 则均值中等但本列取值放大。使用时须与非 _allv 主轨的同名标准差列并读, 二者仅锚点选择 (静态全语料锚点 vs 主轨锚点) 不同, 属锚点选择稳健性阶梯的两臂; 主结论若在两臂下一致, 即证明不被锚点年漂移所驱动。本列不带 _ctx/_ss/_lg 任何中缀, 是三条正交稳健性阶梯 (文本粒度、嵌入厂商、锚点选择) 上均取"主"值的唯一交汇列。

## VAR: article_sim_std_allv_ctx

【变体差分】
本列在 canonical article_sim_std_allv 基础上仅切换文本轨: 由 full 换为 ctx (标题+实体窗口), 嵌入轨仍为 Qwen 主轨、锚点仍为全语料静态 _allv。ctx 轨的底层文本 content_ctx 由 stage 14 ctx_materializer 物化, 只保留标题与命中实体周围的上下文窗口, 相比 full 全文更聚焦于银行/金科实体邻近语境, 因而其政策余弦相似度捕捉的是"实体语境层面"的政策对齐, 本列即该层面对齐度的年内标准差。在 full-only 门控下 ctx 轨为 conditional-on-full 的测度/稳健性轨: 分组宇宙仍是 full 判定的 verified 留篇集, 本列只在该子集上换用 ctx 文本重算相似度再取标准差, 不独立扩张或收缩样本。三条文本轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。ctx 与主轨 full 的差异是"上下文窗口 vs 全文"这一测量口径, 而非锚点或嵌入模型的差异, 因此本列与 article_sim_std_allv 应被读作同一构念在不同文本粒度下的两个测度。单篇年度 NaN、不填 0 的离散度语义与家族一致; 缺 policy_cosine_sim_allv_ctx 源列时本列优雅缺席。实务上 ctx 轨相比 full 轨剔除了与实体无关的段落噪声, 因此当一篇报道大段泛谈行业却仅一句提及目标银行时, ctx 相似度更贴近该银行真实的政策语境, 本列由此度量的离散度也更聚焦于实体层面的口径异质而非全文主题漂移。ctx 与 full 的取值差异本身即可作为诊断: 若两轨的年内标准差系统性背离, 提示报道中银行实体语境与全文语境的政策对齐不一致。本列的嵌入轨与锚点均与 canonical 相同 (Qwen 主轨 + 全语料静态 _allv), 唯文本粒度不同, 因此与 article_sim_std_allv 应被读作同一构念在实体窗口与全文两个粒度下的互证测度。

## VAR: article_sim_std_allv_ss

【变体差分】
本列相对 canonical 仅切换文本轨至 ss (银行∧金科同句±N 窗, 窗半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 嵌入轨仍为 Qwen 主轨、锚点仍为全语料静态 _allv。ss 是三轨中最严格的语境轨: 底层文本 content_ss 只保留银行与金科词在同一句 (及相邻 ±N 句) 共现的片段, 因此本列度量的是"银行-金科强共现语境"下报道与政策语义对齐的年内离散度, 语义定位最窄、噪声最低但也最易在稀疏年度退化。关键的回退语义镜像 ctx: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文正文, ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 当 FINTECH_AC 为空时 is_fallback 全 True 优雅降级。在 full-only 门控下 ss 同为 conditional-on-full 的稳健性轨, 分组宇宙即 full verified 留篇集。三轨各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。在开发期 T 较小、共现稀疏时本列可能大面积 NaN (单篇年度不可估标准差), 属预期退化而非缺陷; 生产期长面板下方恢复正常离散度取值。缺源列时本列优雅缺席。相比 ctx 轨, ss 轨进一步把语境收窄到银行与金科词同句共现的片段, 因此本列度量的是最"纯"的银行-金科强关联语境下报道-政策对齐的年内离散度, 语义信噪比最高但样本代表性受回退比例影响: 当大量报道触发全文回退时, 本列实际退化为接近 full 轨的口径, 须结合 ss_is_fallback 占比一并解读。本列与 ctx/full 轨仅文本粒度不同 (嵌入轨、锚点均同 canonical), 三者互为稳健性、不分主次; ss 轨给出的窄语境结论若与 full/ctx 一致, 即证明政策对齐的年内异质不依赖于语境窗口的宽窄选择。

## VAR: article_sim_std_lg_allv

【变体差分】
本列是 canonical article_sim_std_allv 的 co-primary 对偶: full 文本轨、全语料静态 _allv 锚点均与 canonical 相同, 唯一差别是嵌入轨由无后缀的 Qwen 主轨换为 _lg 轨, 即 OpenAI 系 text-embedding-3-large (3072 维), 经不同厂商、不同维度的嵌入空间重算政策余弦相似度后取年内标准差。两条 co-primary 嵌入轨同为主测度、互为稳健性、严格 parity: 引擎在聚合时以 both-or-neither 保证列名双射 —— 有 Qwen 主轨的 article_sim_std_allv 处必有本 _lg 孪生列, 任一嵌入为 None 则同族两列同置 NaN, 不留单边孤儿; 且 _lg 聚合结果须 rename 为 article_sim_*_lg 的 MAIN 同名约定以维持面板层列名对称。本列的价值在于跨厂商互证: 若年内语义离散度的结论在 Qwen 与 large 两套独立嵌入下一致, 则结论不被单一嵌入模型驱动。铁律: 两条 co-primary 轨各自 just-identified 并排, 严禁把无后缀与 _lg 两列混进同一个 over-identified Hansen J。单篇年度 NaN、不填 0 的离散度语义与家族一致。需强调 Qwen 与 large 两套嵌入维度不同 (4096 vs 3072)、训练厂商不同, 余弦相似度的绝对水平在两空间不可直接比较, 因此本列与 canonical 的比较应在标准化 (如各自 z-score) 后进行, 关注结论方向而非离散度水平的逐点相等。本列的 both-or-neither 降级不同于 per-model BERT 的独立降级: 一旦主轨或本 _lg 轨任一嵌入缺失, 同族两列成对置 NaN, 不容单边孤儿存在, 这是 co-primary 严格 parity 的刚性约束。文本轨 (full) 与锚点 (全语料静态 _allv) 均与 canonical 相同, 唯嵌入厂商轴切换, 故本列专用于验证年内语义离散度结论对嵌入模型选择的稳健性。

## VAR: article_sim_std_lg_allv_ctx

【变体差分】
本列在两个维度上同时偏离 canonical: 嵌入轨为 _lg (text-embedding-3-large, 3072 维), 文本轨为 ctx (标题+实体窗口), 锚点仍为全语料静态 _allv。它是 article_sim_std_allv_ctx 的 co-primary 对偶列, 也是 article_sim_std_lg_allv 的 ctx 文本轨姐妹列, 度量的是"large 嵌入空间下、实体上下文窗口层面"报道与政策语义对齐的年内标准差。作为 co-primary 双轨的一员, 本列与其 Qwen 主轨同名列 article_sim_std_allv_ctx 严格 parity、both-or-neither 双射: 二者同为主测度、互为稳健性, 任一嵌入缺失则成对置 NaN。同时它归属 ctx 文本轨, 与 full/ss 三轨互为稳健性、不分主次。因此本列同时坐落在两条正交的稳健性阶梯上 (嵌入厂商轴 × 文本粒度轴), 但铁律不变: 无论沿哪条轴, 各变体各自 just-identified 并排, 严禁把本列与其 Qwen 对偶、或与 full/ss 轨混进同一 over-identified Hansen J。ctx 底层文本 content_ctx 由 stage 14 物化, 只含标题与实体邻近窗口。在 full-only 门控下本列为 conditional-on-full 稳健性轨, 分组宇宙即 full verified 留篇集。单篇年度 NaN、不填 0; 缺源列优雅缺席。由于本列同处两条正交稳健性阶梯的中间格 (large 嵌入 × ctx 文本), 其取值既受嵌入厂商差异影响也受文本粒度差异影响, 解读时须与 article_sim_std_allv (双主)、article_sim_std_allv_ctx (仅换文本轨)、article_sim_std_lg_allv (仅换嵌入轨) 三列联读, 通过差分定位究竟是嵌入空间还是语境窗口驱动了离散度的变化。与 canonical 一样, 两空间余弦水平不可直接比较, 应先标准化再比方向。

## VAR: article_sim_std_lg_allv_ss

【变体差分】
本列是家族中定位最窄的一列: 嵌入轨为 _lg (text-embedding-3-large, 3072 维), 文本轨为 ss (银行∧金科同句±N 窗, 默认半径 1), 锚点为全语料静态 _allv。它同时是 article_sim_std_allv_ss 的 co-primary 对偶列与 article_sim_std_lg_allv 的 ss 文本轨姐妹列, 度量"large 嵌入空间下、银行-金科强共现同句语境"中报道-政策语义对齐的年内标准差。作为 co-primary 双轨成员, 本列与 Qwen 主轨同名列 article_sim_std_allv_ss 严格 parity、both-or-neither 双射, 二者互为稳健性、同为主测度, 任一嵌入缺失成对置 NaN。ss 轨的回退语义镜像 ctx: 无银行∧金科同句共现时底层 content_ss 回退全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母; FINTECH_AC 为空时 is_fallback 全 True 优雅降级。本列坐落于嵌入厂商轴与文本粒度轴两条正交稳健性阶梯的交汇最窄端, 铁律不变: 各变体各自 just-identified 并排, 严禁本列与其 Qwen 对偶或与 full/ctx 轨混进同一 over-identified Hansen J。在早期试跑期短面板、共现稀疏时本列易大面积 NaN (单篇年度不可估标准差, 不填 0), 属预期退化; 生产长面板下恢复正常。缺源列优雅缺席。本列是家族六列中约束最强、语义最窄的一格: 它同时要求 large 嵌入可算、ss 同句共现命中 (否则回退)、且该 bank-year 有多于一篇 verified 报道, 三重条件叠加使其在短面板下最易缺失, 但也因此在样本充足时提供信噪比最高、跨厂商互证的年内离散度测度。使用时须与其 Qwen 对偶 article_sim_std_allv_ss 及 large 系的 full/ctx 姐妹列联读, 差分嵌入厂商与文本粒度两轴的贡献; 且因两嵌入空间余弦水平不可比, 一律先标准化再比结论方向。

<!-- rendered-citations:begin -->
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, Article 102325. https://doi.org/10.1016/j.intfin.2026.102325
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, Article 1752103. https://doi.org/10.3389/frai.2026.1752103
Muñoz, J. F., Pavía, J. M., & Álvarez-Verdejo, E. (2026). A practical guide to proper estimation and inference of the Gini index by avoiding often encountered methodological pitfalls. Social Indicators Research, 183(1), Article 2. https://doi.org/10.1007/s11205-026-03831-x
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine, 27(15), 2865-2873. https://doi.org/10.1002/sim.3107
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
<!-- rendered-citations:end -->
