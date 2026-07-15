---
family_id: F126
columns:
- bian_2021_idf_tone_app_ctx
- bian_2021_idf_tone_app_full
- bian_2021_idf_tone_app_ss
- bian_2021_idf_tone_ctx
- bian_2021_idf_tone_full
- bian_2021_idf_tone_hw_ctx
- bian_2021_idf_tone_hw_full
- bian_2021_idf_tone_hw_ss
- bian_2021_idf_tone_mw_ctx
- bian_2021_idf_tone_mw_full
- bian_2021_idf_tone_mw_ss
- bian_2021_idf_tone_ss
- bian_2021_idf_tone_std_ctx
- bian_2021_idf_tone_std_full
- bian_2021_idf_tone_std_ss
- bian_2021_idf_tone_tech_ctx
- bian_2021_idf_tone_tech_full
- bian_2021_idf_tone_tech_ss
- bian_2021_idf_tone_vw_ctx
- bian_2021_idf_tone_vw_full
- bian_2021_idf_tone_vw_ss
unit: 语调得分 (无量纲, 归一化, 约 [-1,1]; std 变体为年内离散度非极性均值; 聚合后 bank-year 值)
formula: "article: bian_2021_idf_score = normalize(Σ sign(w)·idf(w)·rule_mult(w)); idf(w) = winsorize(log10(N/(1+df(w)))/mean_raw_idf, P1, P99); panel: bian_2021_idf_tone{track} = mean(idf_score); _std = 年内 std; _vw/_mw/_hw = Σ(idf_score·weight)/Σweight (weight=mention_density / media_authority / herd_decay); _tech/_app = 按 innovation_locus 分组类内均值"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _build_idf_weighted_dict (文章级 bian_2021_idf_score{track}) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (base mean/_std) ; news_process/pipeline/panel/runner.py 步骤 3b/3c/3d (文章级加权列 {d}_idf_score_w/_mw/_hw{track}, 喂 _vw/_mw/_hw 面板聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_idf_score{track}, is_positive_w, media_authority_weight, herd_weight, innovation_locus)
- 22_idf_weights.json (bian_2021 词级 IDF 权重快照)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper (No. 3446388)
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1016/0306-4573(88)90021-0
  type: journal
  authors: Salton, G., & Buckley, C.
  year: 1988
  title: "Term-weighting approaches in automatic text retrieval"
  venue: Information Processing & Management
  vol: 24
  issue: 5
  pages_or_artno: 513-523
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
- doi: "10.1016/j.ememar.2024.101234"
  type: journal
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: "Emerging Markets Review"
- doi: "10.1016/j.eswa.2024.125739"
  type: journal
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: "Expert Systems with Applications"
- doi: "10.1016/j.jempfin.2024.101534"
  type: journal
  authors: "Peng, Y., Shi, L., Shi, X., & Tan, S."
  year: 2024
  title: "Tone or term: Machine-learning text analysis, featured vocabulary extraction, and evidence from bond pricing in China"
  venue: "Journal of Empirical Finance"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1002/isaf.1549"
  - "10.1016/j.ememar.2024.101234"
  - "10.1016/j.eswa.2024.125739"
  - "10.1016/j.jempfin.2024.101534"
---

## CORE

【构念与来源】
本家族测度银行相关新闻在采用 Bian et al. (2021) 中文金融情感词典打分, 且叠加 IDF (逆文档频率) 词级加权之后, 聚合到银行-年层面的语调 (tone)。基础构念与不加 IDF 的原始词频语调 (raw dictionary tone) 同源: 都是把一篇报道切词后, 用情感词典判定每个词的极性 (正面 +1 / 负面 −1), 再叠加否定翻转、程度副词、转折三类语言学规则, 归一化到约 [−1, 1] 的连续分值, 正值表示报道语气偏正面、负值偏负面。本家族与原始词频语调的唯一区别在于: 每个情感词的极性贡献不再是等权的 ±1, 而是先乘上该词的 IDF 权重再累加。IDF 的经济学直觉是"稀有词更具信息量": 一个词在全语料中出现的文章越少 (文档频率 df 越低), 它一旦出现就越能刻画该篇报道的特异语气, 因而被赋予更高权重; 反之像"发展""业务"这类几乎每篇都出现的高频常见词, IDF 权重被压低, 避免其淹没真正带信号的稀有金融术语。词典本体取自 Bian、Jia、Li 与 Yan (2021) 构建并公开的中文金融情感词典 (SSRN 编号 3446388), 该词典专为会计与金融领域中文文本的情感分析设计, 相较通用情感词表能更准确捕捉金融语境下的褒贬用语, 与 Du et al. (2022) 强调的"语言与领域特异性"关切一脉相承。本项目同时物化六部情感词典 (Bian 2021、Jiang 2021、Yao 2021、Du 2022、You 2018、Loughran) 的 IDF 加权语调作为跨词典互为稳健性的一组并排测度, 本家族即其中的 Bian 部。

【方法学与计算】
计算分两层。第一层 (文章级, tone_words.py) 先在含标题的 content_full 语料上统一计算一次 IDF: 对词典中每个情感词 w, 原始权重 raw_idf(w) = log10(N / (1 + df(w))) (smooth IDF, N 为去重后唯一文档数), 再对各词典内部做均值归一化 (使 IDF 加权后的量级与等权版可比、可共享阈值), 最后对归一化权重做 P1–P99 Winsorize 以抑制极端稀有词的杠杆。三轨 (full/ctx/ss) 共享同一份 content_full 语料的 IDF 权重, 以保证 IDF 的文档频率语料与 TF 打分语料同构、标题词的 df 不被低估; 权重快照落盘为 22_idf_weights.json 以满足可复现要求。得到权重后, 把词典 base_score 乘以 IDF 权重构成加权词典 (正面词 +1×idf, 负面词 −1×idf), 再在此加权词典上跑与原始语调完全相同的否定/程度/转折规则打分, 输出 bian_2021_idf_score{track}。IDF 仅缩放极性贡献的幅值、不改变词的极性归属, 跨类重叠词的计数口径与 raw 语调保持一致。第二层 (面板级, encode.py::build_aggregation_dict) 把文章级 IDF 分数聚合到银行-年: 基础列取类内等权均值, 另派生离散度 (_std)、三种加权口径 (_vw/_mw/_hw) 与两种金科创新定位分组 (_tech/_app), 每一变体在 full/ctx/ss 三轨上分别落列, 共 7 变体 × 3 轨 = 21 列。三轨语义遵循全项目统一口径: full = 标题前置 + 全文正文, ctx = 标题 + 银行实体上下文窗口, ss = 标题 + 银行与金科同句共现 ±N 窗; 且自 2026-06-29 起留篇门控为 full-only, 即一篇报道是否计入"银行金科报道"只看 full 轨的 LLM 判定, ctx/ss 降为 conditional-on-full 的稳健性轨, ss 轨在无同句共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True), 与 full 分母共享。

【文献定位】
IDF 加权的思想源头是 Spärck Jones (1972) 关于词项特异性的统计解释与 Salton 与 Buckley (1988) 的词项加权方法, 二者奠定了信息检索中 TF-IDF 的理论基础; Jegadeesh 与 Wu (2013) 首次系统地把词级信息量加权引入金融文本内容分析 ("word power"), 是本家族在金融领域最直接的方法学先例。词典法语调测度的规范框架由 Loughran 与 McDonald (2011) 确立, 中文金融语境的领域特异性词典则由 Bian et al. (2021) 与 Du et al. (2022) 分别提供。作为顶刊锚, Holzman、Miller 与 Twedt (2023, 发表于 The Accounting Review) 论证了媒体情感在盈余公告纪律作用中的经济后果, 并系统采用媒体权威度加权的语调聚合, 正是本家族 _mw 变体的直接方法学依据; Tetlock (2007, Journal of Finance) 关于媒体语气影响市场的经典发现则为语调聚合的构念效度提供了顶刊层面的支撑。Frankel、Jennings 与 Lee (2022) 关于词典法与机器学习法互为稳健的证据, 以及 Barbaglia et al. (2025) 对基于词典的经济文本情感分析的最新评估, 共同支持本项目把 IDF 加权语调与原始词频语调、LLM 投票、BERT 概率并排作为互为稳健性测度的做法。⚠ 口径铁律: 本家族的三轨 (full/ctx/ss)、三种加权 (vw/mw/hw)、两种定位分组 (tech/app) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨/不同加权/不同分组的列混进同一 over-identified 的 Hansen J 过度识别检验。Todd、Bowden 与 Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献 (含词典法与 IDF 等词级加权方法), 为本家族词典法叠加 IDF 加权语调测度提供最新的方法学定位坐标; 徐、华与张 (Xu, Hua, & Zhang, 2025, Emerging Markets Review) 构建中国官方媒体情感指数并证明其预测股市反转与交易行为, 为本家族在中国语境下的媒体语调测度提供最新实证支撑。Ma、Zhang 与 Zhang (2025, Expert Systems with Applications) 构建面向中国境内投资者的细粒度中文情感词典(CN-FSD),证明细粒度情感指标较传统极性/粗粒度词典更能预测中国股市波动与异常现象,为本家族中文金融情感词典叠加词级加权的构念提供最新方法学同源支撑。Peng、Shi、Shi 与 Tan (2024, Journal of Empirical Finance) 用机器学习方法从中国债券定价相关文本中抽取特征词并区分"语调"与"词项"的信息含量,论证词级特征加权(而非等权词频)对中国金融文本信息量提取的增量价值,呼应本家族 IDF 词级加权相对原始等权词频语调的构念动机。

## VAR: bian_2021_idf_tone_full

【变体差分】
本列是家族的 canonical 无后缀基础列在全文轨 (full) 上的实现: 银行-年内所有留篇报道的文章级 Bian IDF 加权语调 (bian_2021_idf_score_full) 的等权算术均值 (聚合算子 = mean), 不做价值加权、媒体权威加权或跟风衰减加权, 也不按金科创新定位分组。full 轨语义为标题前置 + 全文正文, 是本项目自 2026-06-29 起唯一承担留篇门控职责的轨道: 一篇报道是否被判为"银行金科报道"只以 full 轨的 LLM 判定 (llm_verified_full) 为准, 因此本列的行宇宙即银行-年的 full 留篇集, 是家族中样本覆盖最完整、最稳定的一列。与不加 IDF 的 bian_2021_tone_full 的差别仅在于每个情感词的极性贡献先乘以其 IDF 权重: 稀有金融术语被放大、高频常见词被压低, 使语调更聚焦于报道中真正具区分度的语气信号。同时本列也是 IDF 文档频率的计算语料所在轨——IDF 权重恰在含标题的 content_full 上统一算出并被三轨共享, 故 full 轨与 IDF 权重语料严格同构, 不存在标题词 df 被低估的问题。本列与 _std/_vw/_mw/_hw/_tech/_app 各变体互为稳健性、不分主次, 严禁与其他轨或其他加权口径混入同一 over-identified Hansen J。作为词典法的一员, 本列又与 LLM 投票语调、BERT 概率语调在跨方法层面互为稳健。

## VAR: bian_2021_idf_tone_ctx

【变体差分】
本列是 canonical 基础列在实体窗轨 (ctx) 上的实现: 银行-年内文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 的等权均值。ctx 轨的文本为标题 + 围绕银行实体提及的上下文窗口 (entity window), 相比 full 轨剔除了与目标银行语义无关的段落, 使语调更贴近"关于该银行"的局部语气而非整篇报道的整体基调。自 full-only 留篇门控确立后, ctx 轨不再独立决定一篇报道是否留篇, 而是降为 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, per-track 列在此子集上照常计算。IDF 权重仍取自 content_full 语料并与 full/ss 共享, 因此 ctx 轨的 IDF 缩放与 full 轨同源, 二者差异纯粹来自打分文本范围 (整篇 vs 实体窗) 的不同, 而非权重来源不同。本列的经济含义是: 在把常见词压权、稀有金融术语提权之后, 该银行在实体上下文层面被报道的语气偏向。作为 canonical 全文轨的首要稳健性对照, 本列与 full 轨互为稳健性、不分主次; ⚠ 三轨各自 just-identified 并排, 严禁把 ctx 与 full 或 ss 列同时塞进一个过度识别的 Hansen J。本列同样属词典法轨, 与同轨的 LLM、BERT 语调构成跨方法互证。在实证叙事中本列常作为全文轨结论的首要 robustness 报告项, 用以证明主结论不依赖于是否纳入与目标银行语义无关的段落, 即语气信号并非由整篇报道的背景性表述所稀释或反转。

## VAR: bian_2021_idf_tone_ss

【变体差分】
本列是 canonical 基础列在同句共现轨 (ss) 上的实现: 银行-年内文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 的等权均值。ss 轨的文本为标题 + 银行与金融科技词在同一句子内共现的 ±N 句窗 (窗宽由 config 的 ss_sentence_radius 控制, 默认 1), 是三轨中语义最严格、最聚焦"银行×金科"直接叙事的轨道。其回退语义镜像 ctx: 当某篇报道不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文, 并置 ss_is_fallback=True, 与 full 共享 n_articles 分母, 保证不因严格判据而静默丢样本。与 full 轨同样, IDF 权重来自 content_full 语料并三轨共享, 因此 ss 轨的 IDF 缩放与其它两轨同源, 差异只在打分文本范围 (同句窗 vs 整篇)。在留篇门控上, ss 轨与 ctx 轨一样是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集的子集。在开发期 T=2 小样本下, ss 轨因大量回退而可能与 ctx 高度相似甚至退化, 属预期现象, 需在生产期 T=18 全量语料上重新评估其独立信息量。⚠ 铁律: 本列与 full/ctx 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified Hansen J。在生产期全量语料下, 同句轨因判据最严而最能剔除银行与金科偶然共现于同一长文却语义无关的噪声, 因而在稳健性叙事中承担"最保守口径"的角色: 若主结论在 ss 轨仍成立, 则可强力排除语气信号来自泛泛提及而非真实的银行×金科关联叙事。

## VAR: bian_2021_idf_tone_std_full

【变体差分】
本列不是极性均值, 而是全文轨 (full) 内文章级 Bian IDF 加权语调 (bian_2021_idf_score_full) 的银行-年组内标准差 (聚合算子 = std)。它度量的是同一银行同一年不同报道之间语气的离散程度 (tone dispersion / tone volatility), 而非语气的平均高低: 数值越大, 说明该银行当年的新闻语调越分化 (有的报道很正面、有的很负面), 数值接近 0 则说明各篇报道语气高度一致。这一离散度构念与常见的"叙事暴露度"或"语气不确定性"相关: 高覆盖叠加高语气波动往往意味着更强的媒体叙事张力。需强调本列取的是原始 std 聚合, 即在银行-年组内直接对文章级 IDF 加权语调求标准差, 未做任何 z-score 标准化或跨组量纲变换; 它是组内离散度这一实质测度本身, 而非为共享阈值而做的量纲缩放, 二者构念不同, 不要与后续回归中可能对本列再行标准化的做法相混淆。full 轨承担 full-only 留篇门控, 故本列在完整留篇集上计算, 是三轨 std 中样本最稳的一列。⚠ 与家族其余极性均值列 (base/vw/mw/hw/tech/app) 构念不同、量纲不同, 属并排稳健性维度而非可加分解, 严禁与它们混入同一 over-identified Hansen J; 三轨 std (full/ctx/ss) 之间亦各自 just-identified 并排。开发期 T=2 且年内篇数不足时 std 可能为 NaN 或不稳, 属预期退化。在下游回归中本列可作为语气不确定性 / 叙事分歧度的代理变量, 与极性均值列进入各自独立的规格而非同一方程, 因二者构念与量纲皆不可加。

## VAR: bian_2021_idf_tone_std_ctx

【变体差分】
本列是语气离散度 (std) 变体在实体窗轨 (ctx) 上的实现: 银行-年内文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 的组内标准差。与 std_full 的差别仅在打分文本范围——ctx 轨只在银行实体上下文窗口上打分, 因此本列度量的是"关于该银行的局部语气"在不同报道间的分化程度, 相比整篇口径更能剔除无关段落带来的噪声波动。构念上它与 std_full 同为离散度而非极性均值: 高值表示该银行当年实体层面的新闻语气高度分歧, 低值表示各报道对该银行的评价口径趋同。ctx 轨在留篇门控上是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集的子集, 故本列的样本较 std_full 略窄。IDF 权重仍与三轨共享同一 content_full 语料, 缩放来源一致。⚠ 铁律: 本列与 std_full、std_ss 三轨各自 just-identified 并排、互为稳健性, 且与家族内极性均值列量纲不同, 一律不得混入同一 over-identified Hansen J。在开发期 T=2 上, ctx 轨 std 因年内有效篇数少而常呈零方差或 NaN, 属预期退化, 应在生产期 T=18 上评估。本列服务于"语气波动是否稳健于打分文本范围"这一规格稳健性问题: 若实体窗口口径下的离散度与全文口径高度一致, 则可判断语气分歧并非由无关段落的杂音制造, 而是真实反映该银行报道评价的内在分裂。

## VAR: bian_2021_idf_tone_std_ss

【变体差分】
本列是语气离散度 (std) 变体在同句共现轨 (ss) 上的实现: 银行-年内文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 的组内标准差, 度量最严格的"银行×金科同句叙事"口径下各报道语气的分化程度。ss 轨文本为标题 + 银行与金科同句共现 ±N 句窗, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True)。因此本列的离散度在很大程度上受回退比例影响: 回退篇越多, ss 轨越接近 full 轨, 其 std 也越向 full 收敛。构念与 std_full/std_ctx 一致——刻画语气波动而非平均语气, 高值意味着该银行当年金科相关叙事口径高度分裂。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 权重三轨共享 content_full 语料。⚠ 铁律: 本列与 std_full/std_ctx 各自 just-identified 并排、互为稳健性不分主次, 且离散度与极性均值构念/量纲皆不同, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, ss 轨 std 因严格判据下有效篇数极少而几乎全 NaN 或零方差, 属预期退化, 须待生产期全量语料复核其独立信息量。本列在生产期的价值在于刻画最聚焦的银行×金科叙事内部语气是否分裂, 是三轨离散度中口径最窄、最不受泛化背景报道干扰的一列, 与 std_full、std_ctx 共同构成语气分歧度对文本范围敏感性的完整梯子。

## VAR: bian_2021_idf_tone_vw_full

【变体差分】
本列是价值加权 (value-weighted, vw) 变体在全文轨上的实现: 银行-年语调不再对各报道等权平均, 而是以每篇报道的"提及密度 / 显著度权重"作为权重做加权平均, 计算式为 Σ(bian_2021_idf_score_full × weight) / Σweight, 其中分母取 sum_mention_density (0 值替换为 NaN 以防除零)。加权直觉是: 大篇幅、密集提及目标银行的重头报道, 对该银行当年语调的贡献应大于一笔带过的边角报道。这一显著度加权口径借鉴了金融文本测度中按语篇显著性赋权的做法 (与 Hassan et al. (2019) 按提及频次构造企业层风险暴露度量的显著度加权同源思想)。与 canonical base 列 (等权 mean) 相比, 本列在报道篇幅高度不均时能更贴近"读者实际接收到的加权语气", 是回答"结论是否稳健于文章加权方案"的关键并排列。IDF 词级加权与文章级价值加权在此正交叠加: 前者调节词的贡献, 后者调节文章的贡献。full 轨承担 full-only 留篇门控, 本列在完整留篇集上计算。⚠ 铁律: vw 与 base/mw/hw 各自 just-identified 并排、互为稳健性不分主次, 三轨 vw 之间亦并排, 严禁把不同加权口径或不同轨的列混入同一 over-identified Hansen J。若 base 等权口径与 vw 显著度加权口径给出定性一致的语调结论, 即可强化"结论不被少数长篇重头报道的语气单独驱动"的稳健性论证。

## VAR: bian_2021_idf_tone_vw_ctx

【变体差分】
本列是价值加权 (vw) 变体在实体窗轨 (ctx) 上的实现: 以提及密度为权重, 对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 做加权平均, 分母为 sum_mention_density。与 vw_full 的差异仅在打分文本范围——ctx 轨在银行实体上下文窗口上打分, 使显著度加权后的语调更聚焦"关于该银行"的局部语气。加权动机不变: 密集提及目标银行的重头报道贡献更大, 边角提及贡献更小, 从而逼近读者实际接收的加权语气。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权 (稀有词提权) 与文章级价值加权 (显著报道提权) 在本列正交叠加, 二者作用于不同层级、互不干扰。本列的用途是检验"价值加权语调"这一结论是否同时稳健于打分文本范围 (整篇 vs 实体窗) 与文章加权方案两个维度。⚠ 铁律: 本列与 vw_full/vw_ss 三轨各自 just-identified 并排, 与 base/mw/hw 各加权口径亦并排、互为稳健性不分主次, 一律不得混入同一 over-identified Hansen J。开发期小样本下若某银行-年提及密度全为 0, 分母置 NaN 使本列缺失, 属预期安全降级。本列使显著度加权与实体窗口两个维度叠加, 用以确认局部语气结论既不被无关段落污染, 也不被单篇高密度报道所支配。

## VAR: bian_2021_idf_tone_vw_ss

【变体差分】
本列是价值加权 (vw) 变体在同句共现轨 (ss) 上的实现: 以提及密度为权重对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 做加权平均, 分母为 sum_mention_density。ss 轨采用最严格的银行×金科同句共现 ±N 句窗打分, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True), 故本列同时受严格判据与回退比例影响。构念与 vw_full/vw_ctx 一致: 用文章显著度加权逼近读者实际接收的加权语气, 密集提及的重头报道权重更大。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权与文章级价值加权在此正交叠加。本列服务于最严格文本范围下"价值加权语调是否稳健"的检验。⚠ 铁律: 本列与 vw_full/vw_ctx 三轨各自 just-identified 并排, 与 base/mw/hw 加权口径亦并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, ss 轨因严格判据下有效篇数极少、且提及密度可能为 0, 本列常缺失或与 vw 其它轨高度相似, 属预期退化, 须在生产期 T=18 全量语料复核其独立性。本列代表"最严文本口径 + 显著度加权"的双重最保守组合, 若结论在此仍成立则稳健性证据最强, 是价值加权族三轨中判据与权重都最收敛的一列。

## VAR: bian_2021_idf_tone_mw_full

【变体差分】
本列是媒体权威加权 (media-authority weighted, mw) 变体在全文轨上的实现: 银行-年语调以每篇报道来源媒体的权威度权重做加权平均, 计算式为 Σ(bian_2021_idf_score_full × media_authority_weight) / Σmedia_authority_weight, 分母取 sum_media_authority_weight (0 值替换为 NaN)。加权直觉是: 权威主流媒体 (如党报、财经权威刊) 的报道语气比小众或低公信力来源更能影响市场认知与银行声誉, 因此应赋予更高权重。这一口径直接对应 Holzman、Miller 与 Twedt (2023, The Accounting Review) 关于媒体权威度加权情感在盈余公告纪律作用中经济后果的发现, 是本变体的顶刊方法学锚。相较 canonical 等权 base 列与 vw (按文章篇幅显著度加权), mw 换用"来源公信力"这一正交的加权维度, 用以检验语调结论是否被高权威媒体的语气所驱动。IDF 词级加权与媒体权威加权在本列正交叠加: 前者调节词贡献, 后者调节来源贡献。full 轨承担 full-only 留篇门控, 本列在完整留篇集上计算。⚠ 铁律: mw 与 base/vw/hw 各加权口径各自 just-identified 并排、互为稳健性不分主次, 三轨 mw 之间亦并排, 严禁混入同一 over-identified Hansen J。若权威媒体加权与等权口径给出一致语调, 则可排除"结论仅由少数低公信力来源的极端语气所制造"这一替代解释, 增强测度的外部效度。

## VAR: bian_2021_idf_tone_mw_ctx

【变体差分】
本列是媒体权威加权 (mw) 变体在实体窗轨 (ctx) 上的实现: 以来源媒体权威度为权重, 对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 做加权平均, 分母为 sum_media_authority_weight。与 mw_full 的差异仅在打分文本范围——ctx 轨在银行实体上下文窗口上打分, 使权威度加权后的语调更聚焦"关于该银行"的局部语气。加权动机不变: 高公信力主流媒体的语气更能塑造市场认知, 故权重更大。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权 (稀有词提权) 与媒体权威加权 (权威来源提权) 在本列正交叠加。本列用以检验"媒体权威加权语调"是否同时稳健于打分文本范围与来源加权维度。⚠ 铁律: 本列与 mw_full/mw_ss 三轨各自 just-identified 并排, 与 base/vw/hw 加权口径亦并排、互为稳健性不分主次, 一律不得混入同一 over-identified Hansen J。开发期小样本下若某银行-年媒体权威权重合计为 0, 分母置 NaN 使本列缺失, 属预期安全降级; 生产期 T=18 全量语料上媒体来源多样性充分, 本列信息量方能充分体现。本列使权威度加权与实体窗口两个维度叠加, 用以检验局部语气结论既独立于无关段落, 也独立于来源公信力的分布。

## VAR: bian_2021_idf_tone_mw_ss

【变体差分】
本列是媒体权威加权 (mw) 变体在同句共现轨 (ss) 上的实现: 以来源媒体权威度为权重, 对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 做加权平均, 分母为 sum_media_authority_weight。ss 轨采用最严格的银行×金科同句共现 ±N 句窗打分, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True)。构念与 mw_full/mw_ctx 一致: 用来源公信力加权逼近权威媒体主导的语气偏向, 权威主流来源权重更大。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权与媒体权威加权在本列正交叠加, 分别作用于词层与来源层。本列服务于最严格文本范围下"媒体权威加权语调是否稳健"的检验。⚠ 铁律: 本列与 mw_full/mw_ctx 三轨各自 just-identified 并排, 与 base/vw/hw 加权口径亦并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, ss 轨因严格判据下有效篇数极少、且权威权重合计可能为 0, 本列常缺失或与 mw 其它轨高度相似, 属预期退化, 须在生产期全量语料复核其独立信息量。本列代表"最严文本口径 + 来源权威加权"的组合, 用以在最保守设定下检验权威媒体主导的银行×金科语气偏向, 与 mw_full、mw_ctx 共同构成媒体权威加权对文本范围敏感性的完整梯子。

## VAR: bian_2021_idf_tone_hw_full

【变体差分】
本列是跟风衰减加权 (herd-decay weighted, hw) 变体在全文轨上的实现: 银行-年语调以每篇报道的"跟风衰减权重"做加权平均, 计算式为 Σ(bian_2021_idf_score_full × herd_weight) / Σherd_weight, 分母取 sum_herd_weight_full (0 值替换为 NaN, 三轨各用本轨专属分母 sum_herd_weight_{track})。跟风衰减权重由 stage 24 (herd_decay_processor) 生成, 用以抑制媒体"羊群式跟风报道"——当同一事件在短期内被大量媒体重复转载时, 后续跟风报道携带的边际新信息递减, 因而被赋予衰减后的较低权重, 以免高度相关的重复报道人为放大某一时段的语气。这一构念与 Tetlock (2007) 关于媒体语气影响市场、以及媒体信息重复性折价的文献一脉相承。相较 canonical base、vw (篇幅显著度) 与 mw (来源权威), hw 换用"信息新颖性/独立性"这一正交的加权维度, 检验语调结论是否被跟风重复报道所驱动。IDF 词级加权与跟风衰减加权在本列正交叠加。full 轨承担 full-only 留篇门控。⚠ 铁律: hw 与 base/vw/mw 各加权口径各自 just-identified 并排、互为稳健性不分主次, 三轨 hw 之间亦并排, 严禁混入同一 over-identified Hansen J。若跟风衰减加权与等权口径给出一致语调, 则可排除"结论由某一时段的密集转载报道人为放大"这一替代解释, 从而支撑语气信号的信息独立性。

## VAR: bian_2021_idf_tone_hw_ctx

【变体差分】
本列是跟风衰减加权 (hw) 变体在实体窗轨 (ctx) 上的实现: 以跟风衰减权重为权重, 对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 做加权平均, 分母为本轨专属的 sum_herd_weight_ctx (v3.6.0 起三轨分母严格逐轨独立, 修正早期错配)。与 hw_full 的差异仅在打分文本范围——ctx 轨在银行实体上下文窗口上打分, 使衰减加权后的语调更聚焦"关于该银行"的局部语气。加权动机不变: 短期跟风重复报道携带的边际新信息递减, 权重被衰减, 以免重复报道放大某时段语气。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权 (稀有词提权) 与跟风衰减加权 (独立新信息提权) 在本列正交叠加。本列用以检验"跟风衰减加权语调"是否同时稳健于打分文本范围与跟风加权维度。⚠ 铁律: 本列与 hw_full/hw_ss 三轨各自 just-identified 并排, 与 base/vw/mw 加权口径亦并排、互为稳健性不分主次, 一律不得混入同一 over-identified Hansen J。开发期小样本下若某银行-年跟风权重合计为 0, 分母置 NaN 使本列缺失, 属预期安全降级。本列使跟风衰减与实体窗口两维度叠加, 用以确认局部语气结论既不被无关段落污染, 也不被短期跟风重复报道所支配。

## VAR: bian_2021_idf_tone_hw_ss

【变体差分】
本列是跟风衰减加权 (hw) 变体在同句共现轨 (ss) 上的实现: 以跟风衰减权重为权重, 对文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 做加权平均, 分母为本轨专属的 sum_herd_weight_ss; 当 stage 24 未产出同句轨跟风权重时, 该分母缺失使本列优雅退化为 NaN (逐源守卫, 不影响 full/ctx 计算)。ss 轨采用最严格的银行×金科同句共现 ±N 句窗打分, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True)。构念与 hw_full/hw_ctx 一致: 抑制短期跟风重复报道的边际信息折价, 独立新颖报道权重更大。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。IDF 词级加权与跟风衰减加权在本列正交叠加。本列服务于最严格文本范围下"跟风衰减加权语调是否稳健"的检验。⚠ 铁律: 本列与 hw_full/hw_ctx 三轨各自 just-identified 并排, 与 base/vw/mw 加权口径亦并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, ss 轨常因缺同句权重或有效篇数极少而缺失, 属预期退化, 须在生产期全量语料复核。本列代表"最严文本口径 + 跟风衰减加权"的组合, 在最保守设定下检验去重复化之后银行×金科叙事的语气偏向是否依然稳健, 与 hw_full、hw_ctx 共同构成跟风衰减加权对文本范围敏感性的完整梯子。

## VAR: bian_2021_idf_tone_tech_full

【变体差分】
本列是底层技术定位分组 (tech) 变体在全文轨上的实现: 先按创新定位分类 innovation_locus_full 把银行-年内的报道划分为"底层技术"与"应用场景"两类, 再在被判为"底层技术"类的报道子集上取文章级 Bian IDF 加权语调 (bian_2021_idf_score_full) 的类内等权均值。分组依据 Gomber et al. (2018) 关于金融科技创新在"底层技术层 (如区块链、算法、基础设施)"与"应用场景层 (如支付、理财等面向用户的应用)"上的区分, 用以刻画媒体在报道银行金科时聚焦于哪一创新层面, 以及不同层面报道的语气是否系统性不同。本列因此度量的是"该银行当年被报道的底层技术类新闻的语气偏向"。与 canonical base 列 (不分组、全部报道均值) 相比, tech 变体切出的是按创新定位分层的子样本语调, 与 _app 变体 (应用场景层) 构成一对定位对照, 二者之差即家族外的 tone_gap_tech_app 所刻画的技术-应用语气落差 (该 gap 另设最小篇数守卫防组成性混杂)。IDF 词级加权在分组内照常生效。full 轨承担 full-only 留篇门控。⚠ 铁律: tech 与 app 两定位分组、以及三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把不同定位分组或不同轨的列混入同一 over-identified Hansen J。开发期小样本下若某银行-年无"底层技术"类报道, 本列缺失, 属预期。

## VAR: bian_2021_idf_tone_tech_ctx

【变体差分】
本列是底层技术定位分组 (tech) 变体在实体窗轨 (ctx) 上的实现: 在按 innovation_locus 判为"底层技术"类的报道子集上, 取文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 的类内等权均值。与 tech_full 的差异仅在打分文本范围——ctx 轨在银行实体上下文窗口上打分, 使技术类报道的语调更聚焦"关于该银行"的局部语气。分组依据仍为 Gomber et al. (2018) 的底层技术层与应用场景层之分, 本列度量该银行当年底层技术类新闻在实体层面的语气偏向。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。本列与同轨的 app_ctx 构成技术-应用定位对照, 用以检验"技术层新闻语气"是否稳健于打分文本范围。IDF 词级加权在分组子样本内照常生效。⚠ 铁律: 本列与 tech_full/tech_ss 三轨、以及与 app 定位分组各自 just-identified 并排、互为稳健性不分主次, 一律不得混入同一 over-identified Hansen J。开发期 T=2 上, 分组后类内篇数极少, 本列常缺失或方差不稳, 属预期退化, 须在生产期 T=18 全量语料上评估技术层语调的独立信息量。本列与 app_ctx 之差在实体窗口口径下刻画技术层与应用层的语气落差, 用以检验创新定位维度上的语气分野是否稳健于打分文本范围。

## VAR: bian_2021_idf_tone_tech_ss

【变体差分】
本列是底层技术定位分组 (tech) 变体在同句共现轨 (ss) 上的实现: 在按 innovation_locus 判为"底层技术"类的报道子集上, 取文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 的类内等权均值。ss 轨采用最严格的银行×金科同句共现 ±N 句窗打分, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True)。分组依据 Gomber et al. (2018) 的底层技术层与应用场景层之分, 本列度量该银行当年底层技术类新闻在最严格金科叙事口径下的语气偏向。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。本列与同轨的 app_ss 构成技术-应用定位对照。IDF 词级加权在分组子样本内照常生效。⚠ 铁律: 本列与 tech_full/tech_ctx 三轨、以及与 app 定位分组各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, 严格判据叠加定位分组使类内有效篇数几近于零, 本列几乎全缺失, 属预期退化, 须待生产期全量语料方能复核技术层语调在同句轨上的独立性。本列代表"底层技术定位 + 最严同句口径"的组合, 在最保守设定下考察媒体对银行底层技术类金科叙事的语气偏向, 与 app_ss 共同构成同句轨上技术层与应用层的定位对照。

## VAR: bian_2021_idf_tone_app_full

【变体差分】
本列是应用场景定位分组 (app) 变体在全文轨上的实现: 先按创新定位分类 innovation_locus_full 划分底层技术与应用场景两类, 再在被判为"应用场景"类的报道子集上取文章级 Bian IDF 加权语调 (bian_2021_idf_score_full) 的类内等权均值。分组依据 Gomber et al. (2018): 应用场景层指面向终端用户的金融科技应用 (如移动支付、智能理财、消费信贷等), 与底层技术层 (基础设施/算法) 相对。本列度量该银行当年被报道的应用场景类新闻的语气偏向, 与 tech 变体 (底层技术层) 构成一对定位对照, 二者之差即 tone_gap_tech_app。相较 canonical base 列 (不分组全部报道均值), app 变体切出的是应用场景层子样本语调, 用以检验语气结论是否随金科创新层面而异——例如面向用户的应用类报道语气是否系统性比底层技术类更正面或更负面。IDF 词级加权在分组内照常生效。full 轨承担 full-only 留篇门控, 本列在完整留篇集内的应用场景子样本上计算。⚠ 铁律: app 与 tech 两定位分组、以及三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把不同定位分组或不同轨的列混入同一 over-identified Hansen J。开发期小样本下若某银行-年无"应用场景"类报道, 本列缺失, 属预期。

## VAR: bian_2021_idf_tone_app_ctx

【变体差分】
本列是应用场景定位分组 (app) 变体在实体窗轨 (ctx) 上的实现: 在按 innovation_locus 判为"应用场景"类的报道子集上, 取文章级 Bian IDF 加权语调 (bian_2021_idf_score_ctx) 的类内等权均值。与 app_full 的差异仅在打分文本范围——ctx 轨在银行实体上下文窗口上打分, 使应用场景类报道的语调更聚焦"关于该银行"的局部语气。分组依据仍为 Gomber et al. (2018) 的应用场景层与底层技术层之分, 本列度量该银行当年应用场景类新闻在实体层面的语气偏向。ctx 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。本列与同轨的 tech_ctx 构成技术-应用定位对照, 用以检验"应用层新闻语气"是否稳健于打分文本范围。IDF 词级加权在分组子样本内照常生效。⚠ 铁律: 本列与 app_full/app_ss 三轨、以及与 tech 定位分组各自 just-identified 并排、互为稳健性不分主次, 一律不得混入同一 over-identified Hansen J。开发期 T=2 上, 分组后类内篇数极少, 本列常缺失或方差不稳, 属预期退化, 须在生产期 T=18 全量语料上评估应用层语调的独立信息量。本列与 tech_ctx 之差在实体窗口口径下刻画应用层与技术层的语气落差, 用以检验创新定位维度上的语气分野是否稳健于打分文本范围。

## VAR: bian_2021_idf_tone_app_ss

【变体差分】
本列是应用场景定位分组 (app) 变体在同句共现轨 (ss) 上的实现: 在按 innovation_locus 判为"应用场景"类的报道子集上, 取文章级 Bian IDF 加权语调 (bian_2021_idf_score_ss) 的类内等权均值。ss 轨采用最严格的银行×金科同句共现 ±N 句窗打分, 无共现时回退镜像 ctx (content_ss 退化为全文正文, ss_is_fallback=True)。分组依据 Gomber et al. (2018) 的应用场景层与底层技术层之分, 本列度量该银行当年应用场景类新闻在最严格金科叙事口径下的语气偏向。ss 轨为 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集的子集。本列与同轨的 tech_ss 构成技术-应用定位对照, 二者共同刻画在最聚焦口径下技术层与应用层语气的分野。IDF 词级加权在分组子样本内照常生效。⚠ 铁律: 本列与 app_full/app_ctx 三轨、以及与 tech 定位分组各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。开发期 T=2 上, 严格判据叠加定位分组使类内有效篇数几近于零, 本列几乎全缺失, 属预期退化, 须待生产期全量语料方能复核应用层语调在同句轨上的独立性。本列代表"应用场景定位 + 最严同句口径"的组合, 在最保守设定下考察媒体对银行面向用户的金科应用叙事的语气偏向。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper (No. 3446388) [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. Information Processing & Management, 24(5), 513-523. https://doi.org/10.1016/0306-4573(88)90021-0
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
Peng, Y., Shi, L., Shi, X., & Tan, S. (2024). Tone or term: Machine-learning text analysis, featured vocabulary extraction, and evidence from bond pricing in China. Journal of Empirical Finance. https://doi.org/10.1016/j.jempfin.2024.101534
<!-- rendered-citations:end -->
