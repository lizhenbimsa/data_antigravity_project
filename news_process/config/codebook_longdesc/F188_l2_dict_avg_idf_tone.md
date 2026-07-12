---
family_id: F188
columns:
- dict_avg_idf_tone_app_ctx
- dict_avg_idf_tone_app_full
- dict_avg_idf_tone_app_ss
- dict_avg_idf_tone_ctx
- dict_avg_idf_tone_ctx_z
- dict_avg_idf_tone_full
- dict_avg_idf_tone_full_z
- dict_avg_idf_tone_hw_ctx
- dict_avg_idf_tone_hw_full
- dict_avg_idf_tone_hw_ss
- dict_avg_idf_tone_mw_ctx
- dict_avg_idf_tone_mw_full
- dict_avg_idf_tone_mw_ss
- dict_avg_idf_tone_ss
- dict_avg_idf_tone_ss_z
- dict_avg_idf_tone_tech_ctx
- dict_avg_idf_tone_tech_full
- dict_avg_idf_tone_tech_ss
- dict_avg_idf_tone_vw_ctx
- dict_avg_idf_tone_vw_full
- dict_avg_idf_tone_vw_ss
unit: 语调得分 (无量纲, 约 [-1,1]; 跨词典行均值后按 bank-year 聚合)
formula: "dict_avg_idf_tone{track} = mean_d({d}_idf_tone{track}), d 遍历六部中文金融情感词典; 其中面板级 {d}_idf_tone{track} = 文章级 {d}_idf_score{track} 的 bank-year 均值, 文章级 {d}_idf_score{track} = (Σ_pos idf_w − Σ_neg idf_w) / (Σ_pos idf_w + Σ_neg idf_w), idf_w 为该情感词的逆文档频率权重"
producer: news_process/pipeline/panel/geography.py::compute_composite_indicators
upstream:
- 22_tone_words.parquet (文章级逐词典 IDF 归一化语调 {d}_idf_score{track}, tone_words.py idf_norm)
- 面板构建阶段 encode.py (由文章级 {d}_idf_score{track} 聚合出 bank-year 级 {d}_idf_tone{track} 及其 _vw/_mw/_hw/_tech/_app 加权与子样本变体)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
citations:
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
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
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
new_dois: []
---

## CORE

【构念与来源】
本家族测度「银行—金融科技新闻的词典法情感倾向, 且情感词按其逆文档频率 (IDF) 加权后跨词典取均值」。它是词典情感三支柱中的 IDF 加权支柱: 与等权重支柱 (dict_avg_tone) 和计数型 MSENT 支柱并列, 共同构成跨词典层的方法学谱系。构念的核心动机来自内容分析中一个长期被验证的经验事实——不同情感词携带的信息量并不相等: 在语料里高频泛滥的褒贬词 (如「增长」「下降」) 其边际区分力低, 而稀有、领域专属的情感词往往承载更高的信号浓度。IDF 加权正是把这一直觉形式化, 使罕见情感词在语调合成时获得更大话语权, 从而压低套话式高频词对语气得分的稀释。数据来源上须区分文章级与面板级两个命名层: 文章级 stage 22 (22_tone_words.parquet, tone_words.py 的 idf_norm) 逐词典落 {d}_idf_score{track} 归一化得分, 六部中文金融情感词典各自独立打分; 进入面板构建阶段 (encode.py) 后, 每部词典的文章级 idf_score 先按 bank-year 取均值形成面板级 {d}_idf_tone{track} 及其 _vw/_mw/_hw/_tech/_app 加权与子样本变体; 本家族再在 stage 40 面板综合步骤 (geography.py::compute_composite_indicators) 对六部词典的同名面板列取行均值, 得到跨词典集成的 IDF 语调落入面板。故文章级列名是 {d}_idf_score{track}, 面板级 {d}_idf_tone{track} 专指其 bank-year 均值, 二者不可混同。跨词典取均值的目的是降低单一词典覆盖偏差与构造主观性带来的测量噪声, 使集成语调比任一单部词典更稳健。

【方法学与计算】
逐词典 IDF 语调的文章级分子为「正情感词 IDF 权重之和减负情感词 IDF 权重之和」, 分母为「二者之和」, 因而落在约 [-1,1] 区间, 正值偏乐观、负值偏悲观; 该文章级归一化列在源码里名为 {d}_idf_score{track} (tone_words.py 的 idf_norm), 面板级同名 idf_tone 是它按 bank-year 取均值的结果。IDF 权重的思想可回溯到信息检索中的词特异性度量 (Spärck Jones 1972), 并在金融文本分析里由 Jegadeesh 与 Wu (2013) 的「词力量 (word power)」框架系统化, 用样本内文档频率反比给情感词赋权, 替代朴素等权计数。本家族把这一逐词典权重方案外推到六部词典的集成层: 先各词典自归一化算文章级 idf_score, 聚合为面板级 idf_tone, 再跨词典行均值 (_safe_mean 对缺列优雅返回 NaN, golden 重生前源列缺失不致崩)。三条文本轨 (full/ctx/ss)、四种文章级聚合权重 (等权、_vw、_mw、_hw)、两类分类子样本 (_tech/_app) 以及横截面标准化 (_z) 在此基础上正交派生, 每一维度都是对同一构念的规格稳健性探针, 而非新构念。

【文献定位】
IDF 加权语调坐落于会计与金融文本情感测量的方法学三角内。词典法的规范地位由 Loughran 与 McDonald (2011) 奠定, 他们证明通用心理学词表在金融语境下系统性误判, 领域专属词典不可或缺; 其后 Loughran 与 McDonald (2016) 的综述进一步把词权重、稀有度加权列为提升词典效度的关键工艺。Jegadeesh 与 Wu (2013, 发表于 Journal of Financial Economics) 是本家族 IDF 支柱最直接的顶刊锚: 他们提出以词的文档频率反比赋权来度量文本语气, 显著改善了语气对市场反应的解释力, 本家族的逐词典 idf_score 正是这一「词力量」思想在中文金融语料上的落地。媒体情感与市场之间的因果关联则由 Tetlock (2007, Journal of Finance) 奠基, 他用媒体悲观语气预测股市回报与成交量, 论证「谁在报道、报道语气如何」本身携带定价信息, 这一发现是本家族 _mw 媒体权威加权与 _hw 报道相关性加权族的思想源头之一。García、Hu 与 Rohrer (2023) 则从「金融词汇的色彩」角度提示情感词的信息价值随语境与稀有度漂移, 支持非等权方案。Frankel、Jennings 与 Lee (2022) 与 Algaba 等 (2020) 论证词典法、机器学习、计数法三者互为稳健、各有偏误, 呼应本项目让 IDF 语调与等权语调、BERT、LLM 投票并排互证的设计。就中文金融词典本身, Du 等 (2022) 与相关本土词典构造工作提供了六部词典的语义基座。⚠ 铁律: 本家族的三轨、四加权、两分类子样本、标准化各自 just-identified 并排, 互为稳健性、不分主次, 严禁把任意两个后缀变体混入同一 over-identified Hansen J 过度识别检验。留篇门控口径与 full-only (2026-06-29) 一致: 一篇报道是否计入银行—金科新闻宇宙只看 full 轨 llm_verified_full, ctx/ss 为 conditional-on-full 的稳健轨。

## VAR: dict_avg_idf_tone_app_ctx

【变体差分】
本列是「应用维度 (_app) 子样本 × ctx 轨」的跨词典 IDF 加权语调。_app 后缀限定分子分母只在被分类为金融科技「应用/业务场景」维度的文章子集上计算 (对照 _tech 的技术维度子样本, 二者由 stage 16 分类维度切分), 因此它刻画的是银行在金科应用叙事上的情感倾向, 而非全体报道。ctx 轨的文本口径为「标题 prepend + 银行实体上下文窗口」, 相对 full 轨剔除了与目标银行无关的段落, 收紧了实体相关性, 但代价是样本文本更短、方差更高。作为 conditional-on-full 稳健轨, ctx 的行宇宙是 full 留篇集的子集, per-track 列照算。该列与家族 canonical (dict_avg_idf_tone_full) 的差别是三重叠加: 子样本 (应用维度)、轨道 (ctx)、以及随之而来的聚合分母口径。它与 _app_full、_app_ss 构成应用维度内的三轨规格稳健梯; 与 _tech_ctx 构成同轨内的分类维度对照。⚠ 铁律: 本列与同族任一变体各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。分类计数列 n_articles_app 缺席时本列优雅退化为 NaN, 不阻断面板生成。
补充地: 本列的逆文档频率权重在样本内估计, 使应用维度里高频泛化的褒贬词被降权、稀有的场景专属情感词被升权, 相对等权计数信号浓度更高; 它与去掉 IDF 的等权重对应列 (dict_avg_tone 同后缀) 互为词层加权稳健, 二者因高度相关不得同入一式。

## VAR: dict_avg_idf_tone_app_full

【变体差分】
本列是「应用维度 (_app) 子样本 × full 轨」的跨词典 IDF 加权语调, 是应用维度分类子样本中信息最完整的旗舰轨。full 轨文本 = 标题 prepend + 全文正文, 是留篇门控的判定轨 (full-only, 2026-06-29), 故 _app_full 的样本框直接建立在被判为银行—金科报道且归入应用维度的全文之上。相对家族 canonical dict_avg_idf_tone_full, 唯一差别是 _app 子样本限定: 分子的 IDF 加权正负情感词和、分母的总权重和都只在应用维度文章上累加, 因此度量的是银行在支付、信贷、财富管理等金科应用场景叙事里的语气, 剥离了纯底层技术 (如算法、区块链基础设施) 报道的情感。它与 _tech_full 构成 full 轨内技术—应用两维度的对照, 是分离「银行讲应用故事」与「银行讲技术故事」情感差异的核心切分。与 _app_ctx、_app_ss 则构成应用维度内的三轨稳健性阵列。IDF 加权保证稀有的应用相关情感词 (相对高频泛化词) 获得更高权重, 提升子样本内语气的信号浓度。⚠ 铁律: 与同族变体各自 just-identified 并排, 禁混同一 over-identified Hansen J; 分类维度、轨道、加权三组后缀互为稳健、不分主次。
补充地: 六部词典的应用维度 idf_tone 由 geography.py 的 _safe_mean 取行均值, 任一词典源列缺失时优雅返回 NaN 而不使阶段崩溃; 本列与其等权重对应列构成词层加权稳健对, 检验应用维度语气是否被 IDF 赋权方案本身驱动。

## VAR: dict_avg_idf_tone_app_ss

【变体差分】
本列是「应用维度 (_app) 子样本 × ss 轨」的跨词典 IDF 加权语调。ss 轨 (same-sentence) 的文本口径最严: 标题 prepend + 银行实体与金融科技词在同一句子 ±N 窗内共现的片段 (config filtering.yaml::context_window.ss_sentence_radius, 默认 1)。ss 轨的回退语义严格镜像 ctx: 当某文章不存在银行∧金科同句共现时, content_ss 退回为全文正文, ss_is_fallback 置 True, 且与 ctx 共享 n_articles 留篇分母。叠加 _app 子样本后, 本列度量的是「在银行与金科应用维度紧邻共现的句子层面」所表达的情感倾向, 是三轨里语义定位最精准、但也最易因窗口过窄而方差偏高、退化为回退全文的一轨。它与 _app_full、_app_ctx 构成应用维度三轨规格稳健梯, 与 _tech_ss 构成同轨内分类维度对照。在开发期 T=2 小样本上, ss 轨常因共现稀疏而大量回退, 属预期退化而非缺陷; 生产期 T=18 全语料上信号更充分。⚠ 铁律: 本列与同族变体各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混进同一 over-identified Hansen J。
补充地: ss 轨叠加应用维度子样本后样本最稀疏, 逆文档频率仍在样本内估计, 稀有的场景专属情感词获高权以提升退化前的信号浓度; 本列与等权重对应列互为词层加权稳健, 且与 _tech_ss 共同支持技术—应用维度的情感分野检验。

## VAR: dict_avg_idf_tone_ctx

【变体差分】
本列是家族在 ctx 轨的等权 (无加权后缀) 跨词典 IDF 加权语调, 即 canonical 度量的上下文轨稳健版本。文本口径为「标题 prepend + 银行实体上下文窗口」, 在 stage 14 ctx_materializer 物化 (content_ctx)。相对 canonical dict_avg_idf_tone_full, 唯一差别是轨道: ctx 只保留围绕目标银行实体的段落, 剔除全文中与该银行无关的内容, 因而对「这篇报道究竟在讲这家银行什么」这一实体相关性更敏感, 是 full 轨的首要文本稳健轨。它不含任何文章级加权 (等权聚合)、不做分类子样本切分、不做横截面标准化, 因此是家族在 ctx 轨上最基线的形态。IDF 加权仍在词层生效: 六部词典各自对稀有情感词赋高权后算文章级 idf_score, 聚合为面板级 idf_tone, 再跨词典取行均值。ctx 作为 conditional-on-full 轨, 行宇宙是 full 留篇集子集。它与 dict_avg_idf_tone_full、dict_avg_idf_tone_ss 构成核心三轨稳健梯, 与 _vw/_mw/_hw 的 ctx 版本构成同轨内加权谱系。⚠ 铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。
补充地: 本列的 IDF 权重在样本内估计, 高频泛化褒贬词降权、稀有领域情感词升权, 相对等权计数对套话式语气更不敏感; 它与 dict_avg_tone_ctx (去 IDF 等权重) 互为词层加权稳健, 二者给出词权重敏感性证据但因高度相关不可同入一式。

## VAR: dict_avg_idf_tone_ctx_z

【变体差分】
本列是 dict_avg_idf_tone_ctx 的横截面标准化 (z-score) 版本: 在合适的分组维度上减均值除标准差, 使量纲归一、均值 0 方差 1, 便于与其它标准化情感测度在同一回归里比较系数量级, 或作为需要单位无关刻度的场合的替代刻度。它与非标准化的 dict_avg_idf_tone_ctx 底层是同一构念、同一 ctx 轨、同一等权聚合, 差别仅是一次单调线性变换 (标准化), 因而与原始列几乎完全共线, 二者绝不可同时进入同一 RHS。_z 变体只在三条基础轨 (full/ctx/ss) 上派生, 不叠加 _vw/_mw/_hw 加权也不叠加 _tech/_app 分类子样本, 故本列是「ctx 轨等权 IDF 语调」的标准化孪生。它的用途是回归可比性与稳健性呈现, 而非引入新信息。⚠ 标准化后仍受 full-only 留篇门控约束, ctx 为 conditional-on-full 稳健轨; 与 full_z、ss_z 构成标准化三轨。铁律: 与同族各变体各自 just-identified 并排、不分主次, 禁混进同一 over-identified Hansen J; 标准化列与其未标准化母列互为刻度稳健, 不得混入同一过度识别检验。
补充地: 标准化只改变刻度不改变构念, 本列底层仍是 ctx 轨等权 IDF 语调, 逆文档频率赋权、六部词典行均值口径一概不变; 它主要用于回归表内与其它已标准化变量的系数量级并列呈现, 而非引入任何新的情感信息。

## VAR: dict_avg_idf_tone_full

【变体差分】
本列是家族 canonical——full 轨、等权聚合、无分类子样本、无标准化的跨词典 IDF 加权语调, 是全部 20 个变体的参照原点。full 轨文本 = 标题 prepend + 全文正文, 是留篇门控的唯一判定轨 (full-only, 2026-06-29): 一篇报道是否计入银行—金科新闻宇宙只看 full 轨 llm_verified_full, 因此本列的样本框最完整、方差最低、最贴近「银行全部相关报道的整体词典情感」。计算上, 六部中文金融情感词典各自在全文上算文章级 IDF 加权语调 {d}_idf_score_full (稀有情感词按逆文档频率赋高权), 聚合为面板级 {d}_idf_tone_full, 再由 geography.py 跨六部词典取行均值, 最后按 bank-year 落面板。它与 dict_avg_tone_full (等权重词典语调) 的差别在于词层加权方案 (IDF vs 等权), 二者互为词权重稳健; 与 dict_avg_idf_tone_ctx、_ss 的差别在文本轨。作为 canonical, 它是媒体情感在诸多主线论文里 full-only 首要测度的词典法对应物。⚠ 铁律: 本列与其余 20 变体各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。
补充地: 作为参照原点, 本列的 IDF 权重在样本内估计, 稀有领域专属情感词较高频泛化词获更大话语权, 压低套话式褒贬词对语气的稀释; 它与 dict_avg_tone_full (去 IDF 等权重) 构成词层加权稳健对, 是判断主结论是否依赖 IDF 赋权方案的核心一腿。

## VAR: dict_avg_idf_tone_full_z

【变体差分】
本列是 canonical dict_avg_idf_tone_full 的横截面标准化 (z-score) 版本, 均值 0、方差 1 的单位无关刻度。它与 dict_avg_idf_tone_full 底层完全同源——同为 full 轨、等权聚合、跨六部词典 IDF 加权语调, 唯一区别是一次标准化线性变换, 用于让本测度在与其它已标准化变量并列的回归表中系数量级可比, 或用于对量纲敏感的稳健性设定。由于标准化是严格单调变换, 本列与母列 dict_avg_idf_tone_full 高度共线, 二者不得同时作为解释变量进入同一 RHS。_z 只在 full/ctx/ss 三条基础轨上派生, 不与 _vw/_mw/_hw 加权或 _tech/_app 分类子样本叠加, 故本列专指「full 轨等权 IDF 语调」的标准化孪生。它承载的信息与非标准化母列等价, 仅刻度不同。⚠ 铁律: 本列仍受 full-only 留篇门控约束; 与 ctx_z、ss_z 构成标准化三轨稳健梯, 各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 标准化列与其母列互为刻度稳健, 不入同一过度识别检验。
补充地: 标准化仅归一刻度, 本列底层与 dict_avg_idf_tone_full 完全同源——full 轨、等权聚合、六部词典 IDF 语调行均值; 它服务于系数量级可比与量纲敏感的稳健性呈现, 承载信息与非标准化母列严格等价, 二者高度共线不得同入一式。
就论文用法而言, 标准化列多用于把词典 IDF 语气与其它已归一的情感或控制变量放进同一系数图或同一多列回归表, 使读者能直接比较不同测度的效应量级, 而原始刻度列则保留其语义可解释性用于点估计报告。

## VAR: dict_avg_idf_tone_hw_ctx

【变体差分】
本列是「_hw 文章级加权 × ctx 轨」的跨词典 IDF 加权语调。_hw 是把文章级 IDF 语调聚合到 bank-year 时采用的一种文章权重方案 (producer 中该加权族的注释归因于 Tetlock (2007) 一系的媒体情感/报道相关性/信息新鲜度加权思路), 区别于等权 (每篇等权)、_vw (体量/覆盖加权) 与 _mw (媒体权威加权)。因此本列与等权版 dict_avg_idf_tone_ctx 的差别不在文本轨 (同为 ctx)、不在词层加权 (同为 IDF)、不在分类子样本, 而在文章级聚合权重: 不同报道在合成 bank-year 语气时被赋予不同权重, 以检验「若按某类报道重要性加权, 银行的集成词典情感是否改变」。它与 dict_avg_idf_tone_hw_full、_hw_ss 构成 _hw 加权族的三轨稳健梯, 与同轨的等权 / _vw / _mw 版本构成加权方案谱系。四种聚合权重共同回答同一鲁棒性问题——集成语气对文章级加权选择是否敏感。⚠ 铁律: 等权、_vw、_mw、_hw 四种加权各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; ctx 为 conditional-on-full 稳健轨。
补充地: _hw 只改变文章级聚合权重, 词层仍是逆文档频率赋权、六部词典行均值; 本列与 dict_avg_tone_hw_ctx (去 IDF 等权重) 互为词层加权稳健, 与同轨等权 / _vw / _mw 版本共同构成加权规格曲线, 回答集成语气对聚合权重与词权重两组选择是否同时稳健。

## VAR: dict_avg_idf_tone_hw_full

【变体差分】
本列是「_hw 文章级加权 × full 轨」的跨词典 IDF 加权语调, 是 _hw 加权族在信息最完整 full 轨上的旗舰。它与 canonical dict_avg_idf_tone_full 的唯一差别是文章级聚合权重: canonical 对每篇报道等权, 本列采用 _hw 权重方案 (producer 注释归因于 Tetlock (2007) 一系的报道相关性/新鲜度加权思路), 使不同报道按该权重贡献于 bank-year 语气合成。文本轨 (full)、词层 IDF 加权、六部词典行均值口径均与 canonical 一致, 因此本列度量的是「按 _hw 权重加权后, 银行全体相关报道的集成词典情感」。它与 dict_avg_idf_tone_hw_ctx、_hw_ss 构成 _hw 族三轨稳健梯, 与 dict_avg_idf_tone_full (等权)、_vw_full、_mw_full 构成 full 轨内四加权方案的规格曲线。加权敏感性检验的意义在于: 若主结论只在等权下成立、_hw 下翻转, 则说明结论被少数高权重报道驱动, 稳健性存疑; 本列正是这一诊断的一条腿。⚠ 铁律: 四加权各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 本列受 full-only 留篇门控。
补充地: 本列的 IDF 权重在样本内估计, 使稀有情感词在按 _hw 加权合成的 full 轨语气里获更大话语权; 它与 dict_avg_tone_hw_full 互为词层加权稳健, 六部词典同名列由 _safe_mean 取行均值, 任一源列缺失优雅返回 NaN 而不阻断面板生成。
就稳健性叙事而言, 若 full 轨等权语气与本 _hw 加权语气给出方向一致、量级相近的估计, 即支持主结论不被文章级加权选择驱动; 反之背离则提示存在少数高权重报道主导的隐忧, 需在稳健性表中明确披露。

## VAR: dict_avg_idf_tone_hw_ss

【变体差分】
本列是「_hw 文章级加权 × ss 轨」的跨词典 IDF 加权语调。ss 轨文本口径最严——标题 prepend + 银行与金科同句 ±N 窗共现片段, 回退语义镜像 ctx (无同句共现则 content_ss 退回全文正文、ss_is_fallback 置 True、共享 n_articles 分母)。叠加 _hw 文章级加权后, 本列度量的是「在银行—金科同句共现的最精准语义定位上, 按 _hw 权重加权得到的集成词典情感」。它与等权版 dict_avg_idf_tone_ss 的差别仅在文章级聚合权重 (_hw vs 等权), 与 _hw_full、_hw_ctx 的差别仅在文本轨。ss 轨在开发期 T=2 上常因同句共现稀疏而大量回退全文、方差偏高, 属预期退化; 生产期 T=18 信号更充分。本列在 _hw 加权族里承担「最严语义窗 × 报道重要性加权」的组合稳健性, 与同族其余变体共同勾画规格曲线。⚠ 铁律: 三轨与四加权各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两个变体混进同一 over-identified Hansen J; ss 为 conditional-on-full 稳健轨。
补充地: ss 轨叠加 _hw 加权后样本较稀疏, 逆文档频率仍在样本内估计以升权稀有情感词; 本列与 dict_avg_tone_hw_ss 互为词层加权稳健, 与 _hw_full、_hw_ctx 只在文本轨不同, 共同在 _hw 加权族里勾画最严语义窗下的规格曲线。
由于 ss 轨在小样本上易退化为回退全文, 本列的 _hw 加权在退化区间会趋近于 full 轨的加权语气, 这一行为是回退语义镜像 ctx 公理的直接后果, 而非度量缺陷, 生产期全语料上同句共现更充分时该趋近减弱。

## VAR: dict_avg_idf_tone_mw_ctx

【变体差分】
本列是「_mw 媒体权威加权 × ctx 轨」的跨词典 IDF 加权语调。_mw (media-authority weighted) 是按报道来源媒体的权威性/影响力给文章赋权的聚合方案, producer 明确将其归因于 Holzman、Miller 与 Twedt (2023, The Accounting Review): 权威媒体的语气对市场纪律作用更强, 故在合成 bank-year 语气时应获更高权重。本列与等权版 dict_avg_idf_tone_ctx 的差别仅在文章级聚合权重 (媒体权威加权 vs 等权), 同为 ctx 轨、同为词层 IDF 加权、同为六部词典行均值。它度量的是「若按媒体权威性加权, 银行在实体上下文窗内的集成词典情感」, 检验主结论是否被低权威、边缘媒体的噪声报道拉动。它与 _mw_full、_mw_ss 构成媒体权威加权族三轨稳健梯, 与同轨等权 / _vw / _hw 版本构成加权谱系。_mw 与 _vw (体量加权)、_hw 各自捕捉不同的报道重要性维度, 互不替代。⚠ 铁律: 四加权各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ctx 为 conditional-on-full 稳健轨。
补充地: _mw 只改变文章级聚合权重, 词层仍是逆文档频率赋权、六部词典行均值; 本列与 dict_avg_tone_mw_ctx (去 IDF 等权重) 互为词层加权稳健, 检验「权威媒体语气」这一结论是否同时对聚合权重与词权重两组方案稳健, 二者因高度相关不可同入一式。该权威加权在实体上下文窗内尤其有意义, 因为窗口已剔除无关段落, 权重差异直接作用于真正谈论目标银行的报道语气。

## VAR: dict_avg_idf_tone_mw_full

【变体差分】
本列是「_mw 媒体权威加权 × full 轨」的跨词典 IDF 加权语调, 是媒体权威加权族在最完整 full 轨上的旗舰, 也在 stage 40 面板导出 (pipeline/panel/export.py) 中带有明确标签 (Dict IDF Tone, Media-Auth Wt, Full)。它与 canonical dict_avg_idf_tone_full 的唯一差别是文章级聚合权重: 本列按来源媒体权威性给报道赋权 (归因 Holzman、Miller 与 Twedt 2023, The Accounting Review), 使权威媒体的语气在 bank-year 合成中占更大份额。文本轨 (full)、词层 IDF 加权、六部词典行均值均与 canonical 一致。构念上它回答「银行相关报道里, 权威媒体所传递的词典情感是否与全体报道等权情感一致」——若二者显著背离, 说明语气结构存在媒体权威异质性。它与 _mw_ctx、_mw_ss 构成媒体权威加权族三轨稳健梯, 与 full 轨的等权 / _vw / _hw 版本构成四加权规格曲线。媒体权威加权与体量加权 (_vw) 捕捉正交的报道重要性维度, 不可互相替代。⚠ 铁律: 四加权各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 本列受 full-only 留篇门控。
补充地: 本列在 stage 40 面板导出 (pipeline/panel/export.py) 中带明确标签, IDF 权重在样本内估计以升权稀有情感词; 它与 dict_avg_tone_mw_full 互为词层加权稳健, 六部词典同名列经 _safe_mean 行均值, 任一源列缺失优雅返回 NaN, golden 重生前源列未落盘亦不阻断面板生成。
就构念判别而言, 本列与体量加权 _vw_full 的对照可分离「谁在说」与「说得多不多」两种报道重要性: 若权威媒体语气与高体量语气背离, 说明银行的媒体情感在权威性与曝光度两个维度上并不同构, 这一异质性本身即有信息价值。

## VAR: dict_avg_idf_tone_mw_ss

【变体差分】
本列是「_mw 媒体权威加权 × ss 轨」的跨词典 IDF 加权语调。ss 轨采用最严语义口径 (标题 prepend + 银行与金科同句 ±N 窗共现片段), 回退语义镜像 ctx (无同句共现则退回全文、ss_is_fallback 置 True、共享 n_articles 分母)。叠加 _mw 媒体权威加权 (归因 Holzman、Miller 与 Twedt 2023, The Accounting Review) 后, 本列度量的是「在银行—金科同句共现的精准语义定位上, 按媒体权威性加权得到的集成词典情感」。它与等权版 dict_avg_idf_tone_ss 的差别仅在文章级聚合权重, 与 _mw_full、_mw_ctx 的差别仅在文本轨。ss 轨在开发期小样本上常大量回退全文、方差偏高, 属预期退化; 生产期全语料信号更充分。本列在媒体权威加权族里承担「最严语义窗 × 媒体权威加权」的组合稳健性。⚠ 铁律: 三轨与四加权各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两个变体混进同一 over-identified Hansen J; ss 为 conditional-on-full 稳健轨。
补充地: ss 轨叠加媒体权威加权后样本较稀疏, 逆文档频率仍在样本内估计; 本列与 dict_avg_tone_mw_ss 互为词层加权稳健, 与 _mw_full、_mw_ctx 只在文本轨不同, 共同支持「权威媒体语气在最严语义窗下是否稳健」这一组合稳健性检验。
在退化区间 (无同句共现回退全文), 本列的媒体权威加权语气会趋近 full 轨的加权语气, 属回退镜像 ctx 公理的后果而非缺陷; 生产期全语料上银行—金科同句共现更充分, 该趋近减弱, 度量恢复其最严语义定位。

## VAR: dict_avg_idf_tone_ss

【变体差分】
本列是家族在 ss 轨的等权 (无加权后缀) 跨词典 IDF 加权语调, 即 canonical 度量的同句共现轨稳健版本。ss (same-sentence) 轨文本口径最严: 标题 prepend + 银行实体与金融科技词在同一句子 ±N 窗内共现的片段 (config filtering.yaml::context_window.ss_sentence_radius, 默认 1), 在 stage 14 物化为 content_ss。其回退语义严格镜像 ctx: 无银行∧金科同句共现时, content_ss 退回全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 留篇分母。相对 canonical dict_avg_idf_tone_full, 差别是轨道 (ss vs full); 相对 dict_avg_idf_tone_ctx, 差别是语义窗更严 (同句 vs 实体窗)。它不含文章级加权、不做分类子样本、不做标准化, 是家族在 ss 轨上最基线的形态。它与 full、ctx 版本构成核心三轨稳健梯。ss 轨语义定位最精准但最易因窗口过窄而退化为回退全文, 开发期 T=2 上尤甚, 属预期。⚠ 铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 稳健轨。
补充地: 本列的 IDF 权重在样本内估计, 稀有领域情感词较高频泛化词升权, 相对等权计数对套话式语气更不敏感; 它与 dict_avg_tone_ss (去 IDF 等权重) 互为词层加权稳健, 二者给出词权重敏感性证据, 但因高度相关不可同时进入同一 RHS。
作为 ss 轨基线形态, 本列在开发期 T=2 上大量回退全文时会与 dict_avg_idf_tone_full 高度趋近, 属回退语义镜像 ctx 的必然结果; 只有在生产期同句共现充分时, ss 轨才真正兑现其「银行与金科紧邻共现句层情感」的最精准语义定位。

## VAR: dict_avg_idf_tone_ss_z

【变体差分】
本列是 dict_avg_idf_tone_ss 的横截面标准化 (z-score) 版本, 均值 0、方差 1 的单位无关刻度。它与 dict_avg_idf_tone_ss 底层完全同源——同为 ss 轨 (标题 prepend + 银行与金科同句共现片段, 回退镜像 ctx)、等权聚合、跨六部词典 IDF 加权语调, 唯一区别是一次标准化线性变换, 用于在与其它已标准化变量并列的回归里系数量级可比, 或用于对量纲敏感的稳健性设定。由于标准化是严格单调变换, 本列与母列 dict_avg_idf_tone_ss 高度共线, 二者不得同时进入同一 RHS。_z 只在 full/ctx/ss 三条基础轨上派生, 不与 _vw/_mw/_hw 加权或 _tech/_app 分类子样本叠加, 故本列专指「ss 轨等权 IDF 语调」的标准化孪生。它承载的信息与非标准化母列等价, 仅刻度不同。ss 轨在开发期常因同句共现稀疏而回退全文, 标准化不改变这一底层退化。⚠ 铁律: 本列受 full-only 留篇门控; 与 full_z、ctx_z 构成标准化三轨稳健梯, 各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 标准化列与母列互为刻度稳健, 不入同一过度识别检验。
补充地: 标准化仅归一刻度, 本列底层与 dict_avg_idf_tone_ss 完全同源——ss 轨、等权聚合、六部词典 IDF 语调行均值, 回退镜像 ctx 的语义不因标准化改变; 它服务于系数量级可比的稳健性呈现, 与非标准化母列严格等价且高度共线, 不得同入一式。

## VAR: dict_avg_idf_tone_tech_ctx

【变体差分】
本列是「技术维度 (_tech) 子样本 × ctx 轨」的跨词典 IDF 加权语调。_tech 后缀限定分子分母只在被分类为金融科技「技术」维度的文章子集上计算 (对照 _app 的应用/业务场景维度, 二者由 stage 16 分类维度切分), 因此它刻画的是银行在底层技术叙事 (如算法、区块链、云计算基础设施) 上的情感倾向, 而非全体报道或应用场景报道。ctx 轨文本 = 标题 prepend + 银行实体上下文窗口, 相对 full 轨剔除无关段落、收紧实体相关性。本列与 canonical dict_avg_idf_tone_full 的差别是三重叠加: 子样本 (技术维度)、轨道 (ctx)、以及随之而来的聚合分母口径。它与 _tech_full、_tech_ss 构成技术维度三轨稳健梯, 与同轨的 _app_ctx 构成技术—应用两维度对照——分离「银行讲技术故事」与「银行讲应用故事」的情感差异, 是本家族分类维度切分的核心价值。分类计数列 n_articles_tech 缺席时本列优雅退化为 NaN。⚠ 铁律: 本列与同族任一变体各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ctx 为 conditional-on-full 稳健轨。
补充地: 本列的 IDF 权重在样本内估计, 使技术维度里稀有的专业情感词较高频泛化词升权, 信号浓度更高; 它与 dict_avg_tone_tech_ctx (去 IDF 等权重) 互为词层加权稳健, 并与 _app_ctx 共同支持「银行讲技术故事 vs 讲应用故事」的情感分野检验。

## VAR: dict_avg_idf_tone_tech_full

【变体差分】
本列是「技术维度 (_tech) 子样本 × full 轨」的跨词典 IDF 加权语调, 是技术维度分类子样本中信息最完整的旗舰轨。full 轨文本 = 标题 prepend + 全文正文, 是留篇门控判定轨 (full-only, 2026-06-29), 故本列样本框建立在被判为银行—金科报道且归入技术维度的全文之上。相对 canonical dict_avg_idf_tone_full, 唯一差别是 _tech 子样本限定: IDF 加权正负情感词和与总权重和只在技术维度文章上累加, 度量的是银行在金科底层技术叙事里的语气, 剥离了纯应用/业务场景报道的情感。它与 _app_full 构成 full 轨内技术—应用两维度对照, 是本家族分离两类金科叙事情感的核心切分; 与 _tech_ctx、_tech_ss 构成技术维度三轨稳健阵列。IDF 加权保证技术维度里稀有的专业情感词获得更高权重, 提升子样本内语气信号浓度。构念上, 技术维度与应用维度语气的系统性差异, 可揭示银行在「炫技」与「讲落地价值」两种传播策略上的情感立场分野。⚠ 铁律: 与同族变体各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 本列受 full-only 留篇门控。
补充地: 六部词典的技术维度 idf_tone 由 _safe_mean 取行均值, 任一源列缺失优雅返回 NaN 不阻断面板生成; 本列与 dict_avg_tone_tech_full 互为词层加权稳健, 技术维度语气与 _app_full 应用维度语气的系统性落差, 揭示银行两类金科传播策略的情感立场分野。

## VAR: dict_avg_idf_tone_tech_ss

【变体差分】
本列是「技术维度 (_tech) 子样本 × ss 轨」的跨词典 IDF 加权语调。ss 轨文本口径最严——标题 prepend + 银行与金科同句 ±N 窗共现片段, 回退语义镜像 ctx (无同句共现则 content_ss 退回全文、ss_is_fallback 置 True、共享 n_articles 分母)。叠加 _tech 技术维度子样本后, 本列度量的是「在银行与金科技术维度紧邻共现的句子层面所表达的情感倾向」, 是技术维度三轨里语义定位最精准、但也最易因窗口过窄而方差偏高、退化为回退全文的一轨。它与 _tech_full、_tech_ctx 构成技术维度三轨稳健梯, 与同轨的 _app_ss 构成技术—应用维度对照。在开发期 T=2 小样本上, ss 轨叠加技术维度子样本后样本极稀疏、常大量回退, 属预期退化而非缺陷; 生产期 T=18 全语料信号更充分。分类计数列 n_articles_tech 缺席时本列优雅退化为 NaN。⚠ 铁律: 本列与同族变体各自 just-identified 并排、互为稳健性不分主次, 三轨与两分类维度严禁混进同一 over-identified Hansen J; ss 为 conditional-on-full 稳健轨。
补充地: ss 轨叠加技术维度子样本后样本极稀疏, 逆文档频率仍在样本内估计以升权稀有专业情感词; 本列与 dict_avg_tone_tech_ss 互为词层加权稳健, 与 _app_ss 构成最严语义窗下的技术—应用维度对照, 共同支撑分类维度情感差异的稳健性叙事。

## VAR: dict_avg_idf_tone_vw_ctx

【变体差分】
本列是「_vw 体量/覆盖加权 × ctx 轨」的跨词典 IDF 加权语调。_vw (volume-weighted) 是按报道体量/覆盖强度给文章赋权的聚合方案, 区别于等权 (每篇等权)、_mw (媒体权威加权) 与 _hw。因此本列与等权版 dict_avg_idf_tone_ctx 的差别仅在文章级聚合权重: 体量更大、覆盖更强的报道在合成 bank-year 语气时贡献更多, 以检验「若按报道体量加权, 银行在实体上下文窗内的集成词典情感是否改变」。同为 ctx 轨、同为词层 IDF 加权、同为六部词典行均值。它与 _vw_full、_vw_ss 构成体量加权族三轨稳健梯, 与同轨等权 / _mw / _hw 版本构成加权谱系。_vw 捕捉的报道重要性维度 (体量) 与 _mw (媒体权威)、_hw 各自正交, 三者互不替代, 共同回答「集成语气对文章级加权选择是否敏感」这一鲁棒性问题。⚠ 铁律: 等权、_vw、_mw、_hw 四种加权各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; ctx 为 conditional-on-full 稳健轨。
补充地: _vw 只改变文章级聚合权重, 词层仍是逆文档频率赋权、六部词典行均值; 本列与 dict_avg_tone_vw_ctx (去 IDF 等权重) 互为词层加权稳健, 与同轨等权 / _mw / _hw 版本共同构成加权规格曲线, 检验集成语气对体量加权与词权重两组选择是否同时稳健。体量加权在实体上下文窗内直接作用于真正谈论目标银行的报道, 使高覆盖报道的语气在窗内合成中占更大份额, 增强对主流叙事的代表性。

## VAR: dict_avg_idf_tone_vw_full

【变体差分】
本列是「_vw 体量/覆盖加权 × full 轨」的跨词典 IDF 加权语调, 是体量加权族在最完整 full 轨上的旗舰。它与 canonical dict_avg_idf_tone_full 的唯一差别是文章级聚合权重: canonical 对每篇报道等权, 本列按报道体量/覆盖强度赋权, 使高体量报道在 bank-year 语气合成中占更大份额。文本轨 (full)、词层 IDF 加权、六部词典行均值均与 canonical 一致。构念上它回答「银行相关报道里, 高体量报道所传递的词典情感是否与全体等权情感一致」——若显著背离, 说明语气被少数大体量报道主导。它与 _vw_ctx、_vw_ss 构成体量加权族三轨稳健梯, 与 full 轨的等权 / _mw / _hw 版本构成四加权规格曲线。体量加权 (_vw) 与媒体权威加权 (_mw) 捕捉正交的报道重要性维度, 不可互相替代: 前者看「说得多不多」, 后者看「谁在说」。加权敏感性检验是判断主结论是否被特定报道子集驱动的关键稳健性腿。⚠ 铁律: 四加权各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 本列受 full-only 留篇门控。
补充地: 本列的 IDF 权重在样本内估计, 使稀有情感词在按体量加权合成的 full 轨语气里获更大话语权; 它与 dict_avg_tone_vw_full 互为词层加权稳健, 六部词典同名列经 _safe_mean 行均值, 任一源列缺失优雅返回 NaN 而不阻断面板生成。

## VAR: dict_avg_idf_tone_vw_ss

【变体差分】
本列是「_vw 体量/覆盖加权 × ss 轨」的跨词典 IDF 加权语调。ss 轨采用最严语义口径 (标题 prepend + 银行与金科同句 ±N 窗共现片段), 回退语义镜像 ctx (无同句共现则退回全文、ss_is_fallback 置 True、共享 n_articles 分母)。叠加 _vw 体量/覆盖加权后, 本列度量的是「在银行—金科同句共现的精准语义定位上, 按报道体量加权得到的集成词典情感」。它与等权版 dict_avg_idf_tone_ss 的差别仅在文章级聚合权重 (体量加权 vs 等权), 与 _vw_full、_vw_ctx 的差别仅在文本轨。ss 轨在开发期小样本上常因同句共现稀疏而大量回退全文、方差偏高, 属预期退化; 生产期全语料信号更充分。本列在体量加权族里承担「最严语义窗 × 报道体量加权」的组合稳健性, 与同族其余变体共同勾画规格曲线。体量加权与媒体权威、_hw 加权捕捉正交的报道重要性维度, 互不替代。⚠ 铁律: 三轨与四加权各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两个变体混进同一 over-identified Hansen J; ss 为 conditional-on-full 稳健轨。
补充地: ss 轨叠加体量加权后样本较稀疏, 逆文档频率仍在样本内估计; 本列与 dict_avg_tone_vw_ss 互为词层加权稳健, 与 _vw_full、_vw_ctx 只在文本轨不同, 共同在体量加权族里勾画最严语义窗下的规格曲线, 回答语气是否被少数大体量报道主导。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
<!-- rendered-citations:end -->
