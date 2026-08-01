---
family_id: F009
columns:
- article_sim_std
- article_sim_std_ctx
- article_sim_std_lg
- article_sim_std_lg_ctx
- article_sim_std_lg_ss
- article_sim_std_ss
unit: 余弦相似度的组内样本标准差 (无量纲, 定义域 [0, ~0.7])
formula: "article_sim_std{track,emb} = std_{i in (bank,year)}(policy_cosine_sim_i); 分子=文章级政策对齐余弦相似度, 组=同一 (target_bank, year), 聚合域=LLM-verified 篇集 (semi-join 24_herd_decay)"
producer: news_process/pipeline/panel/runner.py (bank-year 聚合) ; news_process/pipeline/panel/export.py (列命名/标签)
upstream:
- "16_article_alignment.parquet (16_article_policy_alignment.py: 文章级 policy_cosine_sim + _lg + 三轨)"
- 24_herd_decay.parquet (LLM-verified (docid, target_bank) 聚合域)
- 40_panel_yearly.parquet
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
- doi: 10.1016/j.frl.2025.107111
  type: journal
  authors: Fan, S., Wu, Y., & Yang, R.
  year: 2025
  title: "Measuring firm-level supply chain risk using a generative large language model"
  venue: Finance Research Letters
  vol: 77
  pages_or_artno: Article 107111
- doi: 10.1016/j.econlet.2025.112602
  type: journal
  authors: Didisheim, A., Fraschini, M., & Somoza, L.
  year: 2025
  title: "AI's predictable memory in financial analysis"
  venue: Economics Letters
  vol: 256
  pages_or_artno: Article 112602
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
本家族刻画的是"银行-年"层面政策语义对齐度的离散程度 (dispersion), 而非其中心水平。其原子测度是文章级政策对齐余弦相似度 policy_cosine_sim: 在 stage 16 (16_article_policy_alignment.py, 落盘 16_article_alignment.parquet) 中, 每一篇经实体判定的银行金科报道被嵌入向量化, 并与冻结政策语料 (监管口径文本) 的嵌入质心求余弦相似度, 得到该篇报道"贴近官方政策话语"的连续强度。此原子量产出源与 stage 15 (fintech_intensity, TF-IDF 技术重度) 是两个独立 stage, 不可混指。伴生家族 article_sim_mean 把同一 (target_bank, year) 组内所有文章的余弦相似度取均值, 度量该行当年报道整体上离政策话语多近; 本家族 article_sim_std 则取同组的样本标准差, 度量的是"同一行当年不同报道在政策贴近度上的分散/异质程度"。二者是同一原子量的一阶矩与二阶矩, 构念正交: 一行可以整体均值很高但内部很散 (部分报道高度贴合、部分完全偏离), 也可以均值中等而高度同质。std 因此承载了均值无法表达的信息——报道政策话语的内部一致性, 可作为"叙事协调度""口径统一度"或"信息环境噪声"的代理变量。数据链条: 原始新闻语料经 stage 00 预处理、stage 11/12 银行与金科实体识别、stage 13 共现硬过滤、stage 14 三轨文本物化后, 在 stage 16 计算文章级 policy_cosine_sim (三轨 × 双嵌入), 再由面板 runner 聚合到银行-年。

【方法学与计算】
聚合公式为组内样本标准差 std_{i∈(bank,year)}(policy_cosine_sim_i), 分母口径遵循 pandas 默认 ddof=1 (无偏样本方差), 单篇组或全 NaN 组自然产出 NaN 而非零 (dispersion 在单点上无定义)。一个承重口径是聚合域: runner 的 _filter_to_verified_universe 把包括 article_sim_* 在内的整个 7h-token 族输入, 用 (docid, target_bank) 键 semi-join 到 stage 24 (herd_decay) 的 LLM-verified 篇集。此举纠正了历史缺陷——stage 16 的文章级输出建立在 stage 13/14 规则预筛候选集 (含未通过 LLM 语义精筛的文章) 之上, 若直接聚合会让约四分之一的假阳性文章污染 bank-year 统计并制造 phantom bank-year。因此本家族的方差是在"确证为真银行金科报道"的子集上计算的, 与面板其余全部文本测度聚合域严格一致。留篇门控采 full-only 口径 (2026-06-29): 一篇是否计入行宇宙只看 full 轨的 llm_verified 判定, ctx/ss 轨降为 conditional-on-full 的稳健性测度, 其 per-track 方差在 full 留篇子集上照算。嵌入引擎为纯 API 双轨: 无后缀轨 = 硅基流动 Qwen3-Embedding-8B (4096 维), _lg 轨 = text-embedding-3-large (3072 维), 二者维度无关 (由 emb.shape[1] 驱动)、严格 parity、both-or-neither 降级。

【文献定位】
以文本嵌入余弦相似度度量"文档与目标语料的语义贴近度"是近年金融文本经济学的主流范式。Liu, Cao, and Wen (2024) 直接以中国政企文本的余弦对齐度量并为其定价, 是本家族政策贴近构念最贴近的先例; Chen, Granville, and Matousek (2026) 用大模型解码央行沟通、Jehnen, Villalba-Díez, and Ordieres-Meré (2026) 训练金融领域句向量模型抽取潜在主题, 均确立了"领域嵌入 + 相似度"作为政策/披露语义测度的方法论基础。Fan, Wu, and Yang (2025) 与 Didisheim, Fraschini, and Somoza (2025) 进一步提示了生成式与嵌入式表征在金融文本中的可复现性与记忆性边界, 为本家族选择冻结、确定性可复现的嵌入锚点提供了动机。以嵌入/文本相似度刻画实体间语义差异并将其组内离散度作为经济构念的做法, 在战略管理文献中已有先例: Arts, Cassiman, and Hou (2025) 以专利文本相似度构造企业间技术差异度并将其与产品市场竞争及并购决策相联系, 印证了"相似度及其分散程度可作为可信实证测度"这一方法论前提, 支撑本家族把组内相似度标准差当作叙事异质度代理的合法性。方差作为离散度指标本身的方法论审慎见 Mainali, Slud, Singer, and Fagan (2022) 对相似度/共现指标的可比性讨论; 而标准差在回归输入中的标准化角色见 Gelman (2008)。需强调: 三轨 (full/ctx/ss) 与 co-primary 双嵌入 (Qwen 无后缀 / text-embedding-3-large 的 _lg) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 或三条轨道混进同一条 over-identified 的 Hansen J 过度识别检验; ss 轨回退语义镜像 ctx (无银行金科同句共现时 content_ss 降级为全文正文并置 fallback 标志, 共享 n_articles 分母)。

## VAR: article_sim_std

【变体差分】
本列是家族 canonical 无后缀槽: 无后缀嵌入轨 = 硅基流动 Qwen3-Embedding-8B (4096 维) 这一 co-primary 主测度, full 文本轨 = 标题 prepend 加全文正文。它度量的是每一"银行-年"内, 各篇 (Qwen 嵌入、full 文本) 政策对齐余弦相似度的组内样本标准差, 即该行当年报道在政策话语贴近度上的分散程度。相对于伴生的 article_sim_mean (同组均值, 中心水平), 本列取的是二阶矩 (离散水平), 二者构念正交、可同时进入回归而不共线。聚合域为 LLM-verified 篇集 (semi-join stage 24), 留篇门控 full-only。与三条 ctx/ss 轨及三条 _lg 轨相比, 本列是"Qwen × full"这一格; 它与 article_sim_std_lg (换 text-embedding-3-large 嵌入、同 full 轨) 构成 co-primary 对偶, 二者互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。生产口径上无后缀不代表"更主", 只是历史命名产物; 数值上, 单篇银行-年组产出 NaN (标准差在单点无定义), 这是设计契约而非缺失 bug。作为二阶矩测度, 它对组内篇数极其敏感: 组内篇数越少方差估计越不稳, 因此本列在实证上更适合作银行当年报道量充足者的信息一致性代理, 稀疏样本行须谨慎解读或以篇数加权。经济含义上, 高 std 表示该行当年一部分报道高度贴合政策话语、另一部分则明显偏离, 反映口径分裂或多元叙事; 低 std (且非零) 表示报道政策贴近度高度同质, 口径协调。与均值联合使用时, "高均值低方差"刻画统一的高政策贴合叙事, "高均值高方差"则提示表面贴合下潜藏异质。早期试跑 T=2 语料下多数行仅一两篇报道, 故本列大量为 NaN, 生产 T=19 语料上方有意义方差; 聚合遵循 pandas ddof=1 无偏样本方差口径。

## VAR: article_sim_std_ctx

【变体差分】
本列相对 canonical article_sim_std 的唯一差分是文本轨: 由 full 轨换为 ctx (context) 轨。ctx 轨文本 = 标题 prepend 加实体窗口 (仅保留目标银行实体上下文窗口内的句子, 剔除与银行金科无关的段落), 在 stage 14 (ctx_materializer) 物化为 content_ctx。因此本列度量的是"仅看银行相关语境时", 各篇政策对齐余弦相似度的组内离散程度, 剥离了报道中与目标银行无关的政策叙事对相似度的稀释。嵌入仍为无后缀 Qwen3-Embedding-8B 这条 co-primary 主轨。ctx 轨在 full-only 门控下降为 conditional-on-full 的稳健性/条件测度: 行宇宙是 full 留篇集的子集, per-track 方差在该子集上照算。它与 full 轨 (article_sim_std) 及 ss 轨 (article_sim_std_ss) 构成三轨规格稳健性并排, 三轨各自 just-identified、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本列又与其 _lg 对偶 article_sim_std_lg_ctx 构成 both-or-neither 的 co-primary 双射, 任一嵌入为空则两列同置 NaN, 无单边孤儿。方法论上, ctx 轨相对 full 轨的价值在于降低"稀释偏误": full 轨把整篇报道 (含大量与目标银行无关的政策背景铺陈) 一并嵌入, 会使不同银行的报道趋同、压低方差; ctx 轨仅保留银行实体窗口句子, 使余弦相似度更贴近该行自身的政策语境, 组内离散度因而更能反映银行特异的叙事异质而非公共背景噪声。三轨方差水平不可直接跨轨比较 (文本域不同, 尺度不同), 只可在各自轨内比较或标准化后并排入回归。ctx 文本在 stage 14 由 prepend_title 内嵌标题后物化, 原始内容列不动。早期试跑 T=2 上 ctx 轨常因组内篇数不足或零方差而退化为 NaN 或 0, 属预期退化, 生产 T=19 方具判别力。

## VAR: article_sim_std_lg

【变体差分】
本列相对 canonical article_sim_std 的唯一差分是嵌入引擎: 由无后缀 Qwen3-Embedding-8B (4096 维) 换为 _lg 槽的 text-embedding-3-large (3072 维), 文本轨仍为 full (标题 prepend 加全文正文)。它是 canonical 列的 co-primary 对偶——两条嵌入轨同为主测度、互为稳健性、严格 parity, 列名 both-or-neither 双射: 任一 embed 返回 None 则同族两列同置 NaN, 不产生单边孤儿。度量语义与 canonical 完全相同 (银行-年内文章级政策对齐余弦的组内样本标准差), 只是把语义空间从阿里 Qwen 换成 OpenAI text-embedding-3-large, 用以验证 dispersion 结论不被单一嵌入厂商/维度驱动。铁律: 两条 co-primary 各自 just-identified 并排, 严禁把 article_sim_std 与 article_sim_std_lg 混进同一条 over-identified 的 Hansen J 过度识别检验 (维度 4096 vs 3072、语义空间不同, 混合会破坏 just-identification 结构)。_lg 后缀在本家族命名中置于 std 与 track 之间 (article_sim_std_lg, article_sim_std_lg_ctx, article_sim_std_lg_ss), 与 CLAUDE.md "_lg 中置" 口径一致。聚合域同为 LLM-verified 篇集 (semi-join stage 24), 留篇门控 full-only, 组内样本标准差 ddof=1。方法论动机上, 保留两条独立厂商、独立维度的嵌入轨并要求结论在两轨上同号同显著, 是对"嵌入表征可复现性与记忆性"担忧 (Didisheim, Fraschini, and Somoza, 2025) 的直接回应: 若某个 dispersion 结论只在 Qwen 空间成立而在 text-embedding-3-large 空间消失, 则该结论可能是特定嵌入几何的伪影而非稳健的经济信号。换嵌入模型时须同步散落的硬编码默认回退并先删盘上跨嵌入空间的冻结阈值 sidecar, 否则守卫 fail-loud。本列数值同样在单篇组上为 NaN, 早期试跑 T=2 稀疏, 生产 T=19 有意义。

## VAR: article_sim_std_lg_ctx

【变体差分】
本列是双维差分格: 嵌入轨 = _lg (text-embedding-3-large, 3072 维), 文本轨 = ctx (实体窗口, content_ctx)。它度量的是"仅看银行相关语境、且用 OpenAI text-embedding-3-large 语义空间时", 银行-年内各篇政策对齐余弦相似度的组内标准差。它同时坐落在两条正交的稳健性维度上: 沿文本轨维度, 它与 article_sim_std_lg (full) 和 article_sim_std_lg_ss (ss) 构成 _lg 内部三轨并排; 沿嵌入维度, 它与 article_sim_std_ctx (Qwen × ctx) 构成 co-primary 对偶, both-or-neither 双射同置 NaN。所有这些并排关系均遵循同一铁律: 各自 just-identified、互为稳健性、不分主次, 严禁三轨或两条 co-primary 混进同一 over-identified Hansen J。ctx 轨在 full-only 门控下为 conditional-on-full 测度, 行宇宙为 full 留篇子集。text-embedding-3-large 的嵌入缓存键与 Qwen 轨不同 (('text-embedding-3-large', 版本戳)), 换嵌入时须先删盘上冻结阈值 sidecar 以免跨嵌入空间守卫 fail-loud。作为四条稳健性网格 (2 嵌入 × 三轨中的 ctx) 中的一格, 本列的实证角色是双重交叉验证: 只有当核心 dispersion 结论在 full/ctx/ss 三轨、且在 Qwen/text-embedding-3-large 两嵌入上都稳健时, 才可宣称该银行-年政策叙事异质度的效应不被文本域选择与嵌入几何选择联合驱动。但铁律要求这些交叉验证以并排规格呈现, 而非并入单一过度识别方程: 每一格各自 just-identified, 混入同一 Hansen J 会因维度与文本域异质而虚增自由度、破坏识别结构。早期试跑 T=2 下该格常退化为 NaN, 生产 T=19 有意义。

## VAR: article_sim_std_lg_ss

【变体差分】
本列是双维差分格: 嵌入轨 = _lg (text-embedding-3-large, 3072 维), 文本轨 = ss (sentence-scope 同句轨)。ss 轨文本 = 标题 prepend 加"银行与金科在同一句 (±ss_sentence_radius 窗, 默认 1) 共现"的句子集; 度量的是最严格语境下——报道中银行与金科真正同句绑定之处——各篇政策对齐余弦相似度在银行-年内的组内标准差。ss 轨的回退语义严格镜像 ctx: 若某篇无银行金科同句共现, 则 content_ss 降级为全文正文、ss_is_fallback 置 True, 并共享 n_articles 分母; 若 FINTECH_AC 为空则整轨优雅降级 fallback 全 True。它沿 _lg 嵌入维度与 article_sim_std_lg / article_sim_std_lg_ctx 构成三轨并排, 沿嵌入维度与 article_sim_std_ss (Qwen × ss) 构成 co-primary both-or-neither 对偶。三轨/两 co-primary 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。ss 是三轨中语境最窄、样本最稀的一轨, 在早期试跑 T=2 上几乎恒为 NaN 或零方差, 属预期退化, 需生产语料方有充分组内篇数支撑二阶矩估计。相对 ctx 轨 (实体窗口, 可能跨句), ss 轨要求银行与金科在同一句内绑定, 语义精度最高但召回最低, 大量文章落入 fallback (退回全文正文) 从而与 full 轨趋同; 故本列在实证上是最保守、也最易退化的一格, 其非 fallback 部分承载的是"银行金科强绑定叙事"的政策贴近离散度, 一旦有值则信号最纯。判定不对称口径沿用全仓约定: 银行侧含否定与短名过滤, 金科侧为裸 AC 词表匹配。本列与 Qwen 内部 full/ctx 两轨及 _lg 内部三轨并排, 均遵循各自 just-identified、互为稳健性、不分主次、禁混同一 over-identified Hansen J 的铁律。聚合 ddof=1, 留篇门控 full-only, 行宇宙为 full 留篇子集。

## VAR: article_sim_std_ss

【变体差分】
本列相对 canonical article_sim_std 的唯一差分是文本轨: 由 full 换为 ss (同句轨), 嵌入仍为无后缀 Qwen3-Embedding-8B 这条 co-primary 主轨。ss 轨只保留报道中银行与金科同句 (±1 句窗) 共现的句子, 是三轨中语境最严格者; 本列因此度量的是"银行金科真正同句绑定处"的政策对齐余弦在银行-年内的组内离散程度, 剔除了泛泛提及的政策叙事对方差的贡献。回退语义镜像 ctx: 无同句共现的文章其 content_ss 降为全文正文、置 ss_is_fallback、共享 n_articles 分母, 保证不静默清空。本列与 full 轨 (article_sim_std) 及 ctx 轨 (article_sim_std_ctx) 构成 Qwen 内部三轨规格稳健性并排, 又与其 _lg 对偶 article_sim_std_lg_ss 构成 co-primary both-or-neither 双射。铁律同前: 三轨与两条 co-primary 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。留篇门控 full-only, ss 行宇宙为 full 留篇子集。经济含义上, 本列度量的是"银行金科真正同句捆绑处"报道政策贴近度的内部分歧: 当一行当年既有同句语境高度贴合政策的报道、又有明显偏离的报道时本列走高, 反映其金科相关叙事在官方话语框架下的口径不一。相较 full 与 ctx, ss 剔除了泛政策背景的稀释, 使方差更聚焦银行金科议题本身; 但代价是样本最稀、fallback 最多、二阶矩估计最不稳。ss 回退严格镜像 ctx (无同句共现降为全文正文、置 ss_is_fallback、共享 n_articles 分母, 绝不静默清空); FINTECH_AC 为空时整轨优雅降级。早期试跑 T=2 语料下本列因同句共现稀疏而大量为 NaN, 生产 T=19 上方具判别力; 聚合 ddof=1。

<!-- rendered-citations:begin -->
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, Article 102325. https://doi.org/10.1016/j.intfin.2026.102325
Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer for extracting predictive latent topics from financial disclosures. Frontiers in Artificial Intelligence, 9, Article 1752103. https://doi.org/10.3389/frai.2026.1752103
Fan, S., Wu, Y., & Yang, R. (2025). Measuring firm-level supply chain risk using a generative large language model. Finance Research Letters, 77, Article 107111. https://doi.org/10.1016/j.frl.2025.107111
Didisheim, A., Fraschini, M., & Somoza, L. (2025). AI's predictable memory in financial analysis. Economics Letters, 256, Article 112602. https://doi.org/10.1016/j.econlet.2025.112602
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine, 27(15), 2865-2873. https://doi.org/10.1002/sim.3107
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
<!-- rendered-citations:end -->
