---
family_id: F125
columns:
- bian_2021_idf_score_w_sum_ctx
- bian_2021_idf_score_w_sum_full
- bian_2021_idf_score_w_sum_ss
unit: 无量纲加权得分之和 (VW 分子求和; 篇章级 idf 语调分 × 提及密度, 在 bank-year × 轨内累加)
formula: "bian_2021_idf_score_w_sum{track} = Σ_{a ∈ bank-year, track} ( bian_2021_idf_score_a{track} × mention_density_a ); 其中 bian_2021_idf_score = 在 IDF 重加权 Bian2021 词典上经语言学规则调整后归一化的篇章语调分, 权重 w = mention_density (Hassan 2019 QJE value-weighted exposure)"
producer: pipeline\panel\runner.py (步骤 3b 生成篇章级 {d}_idf_score_w) ; pipeline\panel\encode.py::build_aggregation_dict (F2 块 sum 聚合) ; pipeline\sentiment\tone_words.py::build_idf_weights / _build_idf_weighted_dict (IDF 权重)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 22_tone_words.parquet (bian_2021_idf_score{track} 篇章级 IDF 语调分, 22_idf_weights.json)
- 11_news_bank.parquet (mention_density 提及密度权重)
citations:
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
  venue: SSRN Working Paper
  pages_or_artno: "No. 3446388"
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: "10.1111/1911-3846.12825"
  type: journal
  authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W."
  year: 2023
  title: "Textual Analysis in Accounting: What's Next?"
  venue: "Contemporary Accounting Research"
- doi: "10.1093/rfs/hhag049"
  type: "journal"
  authors: "Harford, J., He, Q., & Qiu, B."
  year: 2026
  title: "Firm-Level Labor Shortage Exposure"
  venue: "The Review of Financial Studies"
  pages_or_artno: "hhag049"
new_dois:
  - "10.1111/1911-3846.12825"
---

## CORE

【构念与来源】
本家族刻画的是"以 Bian et al. (2021) 中文金融情感词典为底、经 IDF 词级加权后, 再按报道对目标银行的提及密度做价值加权、并在 bank-year × 文本轨内累加"所得的语调分子求和。它不是一个可直接读取的语调均值, 而是"价值加权语调均值"(idf_tone_vw) 的分子件: 分母是同 bank-year 内提及密度之和 (Σ mention_density), 两者相除才还原为一个落在语调量纲上的加权平均。之所以把分子单独物化落列, 是为了让下游 Stata 侧既能取现成的 vw 比值, 也能自行更换分母口径 (如改用有效票数、改用媒体权威权重) 而无需回到篇章级重算。构念上它服务于同一个问题: 当一家银行在某年被多篇金融科技相关报道覆盖时, 覆盖越密集、目标银行被提及越频繁的报道, 越应在年度语调聚合中占更大话语权——这正是 Hassan et al. (2019) 价值加权暴露 (value-weighted exposure) 思想在词典语调上的落地。底层词典取自 Bian et al. (2021) 面向会计与金融文本分析构建的中文金融情感词典 (SSRN 3446388), 该词典相较通用中文情感词表更贴合财经语域, 正面词计 +1、负面词计 −1 的基分, 再乘以词级 IDF 权重形成加权词典。

【方法学与计算】
计算分三层。第一层是词级 IDF 加权: 在 tone_words.build_idf_weights 中, 对全语料 (document-frequency 统计以 content_full 去重篇为文档单位) 求 raw_idf(w)=log₁₀(N/(1+df(w))), 再除以全词均值做归一化, 末以 P1/P99 Winsorize 截尾, 得到落在 22_idf_weights.json 的词级权重; _build_idf_weighted_dict 将 Bian2021 每个词的 ±1 基分乘以该词 IDF 权重, 生成 IDF 加权词典。第二层是篇章语调: _compute_sentiment_with_rules 在 IDF 加权词典上逐篇扫描, 施加否定翻转/程度副词/转折三条语言学规则并做归一化, 落为 bian_2021_idf_score{track}。第三层是价值加权与聚合: runner.py 步骤 3b 取提及密度 w=mention_density (缺失填 0), 逐篇算出 bian_2021_idf_score_w{track}=bian_2021_idf_score{track}×w; encode.py 的 build_aggregation_dict F2 块再在 bank-year × 轨内对该列做 'sum' 聚合, 得本家族三列。三条文本轨 (full/ctx/ss) 各自独立走完这条链路, 分子分母严格逐轨匹配, 不跨轨借用。IDF 的引入使高信息量的稀有情感词权重上升、遍布全语料的常见词权重下降, 呼应 text-as-data 中 tf-idf 词加权的方法学传统。

【文献定位】
方法学锚点有三条谱系。其一是词典法本身的效度与定位: Frankel, Jennings and Lee (2022) 在 Management Science 上系统比较了机器学习与词典法在披露情感度量上的表现, 论证了词典法在可解释、可复现与跨样本稳定上的价值, 为本项目并置 LLM/词典/BERT 三法互为稳健性提供了先例。其二是中文金融语域的专用词典: Bian et al. (2021) 是本家族底层词典的直接出处, 而 Du et al. (2022) 在 Review of Finance 上进一步论证了语言与领域专用性对中文金融情感度量的关键作用, 二者共同支撑"必须用财经语域词典而非通用词表"的选择。其三是词级加权的理论根据: Jegadeesh and Wu (2013) 在 Journal of Financial Economics 提出的 word power 思想说明不同词对文档语调的贡献并不均等, 而 Spärck Jones (1972) 关于词项特异性的经典统计解释则是 IDF 加权的原始出处。需强调的是, 三条文本轨 (full/ctx/ss) 在本族属规格稳健性并排: 各自 just-identified、互为稳健性不分主次, 严禁把不同轨的加权分子混进同一 over-identified 的 Hansen J 检验。留篇门控口径遵循 full-only (2026-06-29): 一篇报道是否被判为"银行金融科技报道"只看 full 轨的 llm_verified_full, ctx/ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。此外, Bochkay, Brown, Leone and Tucker (2023, Contemporary Accounting Research) 系统综述了会计文本分析方法(含词典法情感度量及其权重设计)的现状与未来方向, 为本家族 IDF 加权词典与提及密度价值加权并置的方法学选择提供了近期综述性文献支撑。 提及型暴露度权重这一谱系的近期构造范例见 Harford、He 与 Qiu (2026): 该文自财报电话会文本提取公司层面「劳动力短缺暴露」测度, 并在州、行业与公司三个层级做效度验证, 再检验其对 CAR、未来收益与经营绩效的预测力, 为本族价值加权分子所用的文本提及型 firm-level exposure 权重 (mention_density) 提供了近期的构造与效度验证参照。迁移边界须写明: 原文语料为英文财报电话会, 度量的是劳动力短缺暴露而非情感极性; 且原文把暴露度直接作为自变量进入回归, 并未将其作为乘性权重乘到词典情感分上 (本族为 w = mention_density 与篇章 IDF 语调分相乘后再在 bank-year × 轨内求和), 亦无银行-年三轨聚合。
## VAR: bian_2021_idf_score_w_sum_ctx

【变体差分】
本列是三轨中的实体窗轨 (ctx) 变体。文本载体为 content_ctx——即"标题 prepend + 目标银行实体上下文窗口"物化文本 (stage 14 ctx_materializer 产出), 而非全文正文。相对 full 轨, ctx 轨把语调扫描收缩到实体附近的语境窗内, 目的是降低全文中与目标银行无关段落对语调的稀释; 相对 ss 轨, ctx 轨的窗判据是"实体窗"而非"银行∧金科严格同句", 覆盖面更宽。计算上, 本列的篇章分子 bian_2021_idf_score_w_ctx = bian_2021_idf_score_ctx × mention_density, 再在 bank-year 内求和; IDF 词权重与提及密度权重两者的口径与其余两轨完全一致, 唯一差别在语调分所扫描的文本轨。回退语义: 当实体未在正文命中、content_ctx 退化为等于 content_full 时, ctx_is_fallback=True, 此时本轨语调实质等价于 full 轨 (frac_ctx_fallback 高值即提示两轨退化同源); 与之配套的 n_articles_for_ctx_independence 记录真正 full≠ctx 的独立篇数, 用以避免按比例过滤时的银行规模偏差。需特别厘清: 本列的 ctx 后缀标示的是"语调所扫描的文本轨", 与 stage 13 共现硬过滤中 sentence_radius 那类"判据窗口"后缀不是同一维度, 二者不可相互替代或复用。IDF 词权重仍来自以 content_full 为文档基底统计的同一份 22_idf_weights.json, 故本轨与 full/ss 共享词级权重, 差异纯粹落在语调扫描范围。在识别上本列与 full/ss 两轨各自 just-identified、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。作为 conditional-on-full 轨, 其行集是 full 留篇集的子集, 单独进入自身的稳健性回归而不与 full 轨同列作 RHS。

## VAR: bian_2021_idf_score_w_sum_full

【变体差分】
本列是三轨中的全文轨 (full) 变体, 也是本族在 full-only 留篇门控 (2026-06-29) 下的首要轨。文本载体为 content_full——"标题 prepend + 完整正文 body", 是留篇判定 (llm_verified_full) 所依据的同一文本域。计算上, 篇章分子 bian_2021_idf_score_w_full = bian_2021_idf_score_full × mention_density, 再在 bank-year 内求和成本列; 其中 IDF 的 document-frequency 统计正是以 content_full 去重篇为文档单位 (tone_words 里 _idf_text_col 优先取 content_full), 因此 full 轨在 IDF 词权重的语料基底上与其余两轨共享同一份 22_idf_weights.json, 差别仅在语调扫描所覆盖的文本范围最大。相较 ctx/ss 两轨, full 轨不做实体窗或同句窗收缩, 覆盖全文, 因而对目标银行以外语境的语调信息也纳入, 稳健性上作为"信息面最全"的一端。作为首要轨, 它承载 n_articles 等留篇计数的口径; ctx/ss 为其 conditional-on-full 的稳健性伴随轨。要提醒的是, 尽管本族无"裸无后缀"列 (面板中只存在 full/ctx/ss 三列), full 轨在 full-only 门控下扮演事实上的 canonical 角色, 但这一"首要"并不意味着 ctx/ss 是次级派生量——三轨在计量效度上并置、不分主次, 仅在留篇判定的门控职责上由 full 承担。本列作为 VW 分子求和, 其数值随 bank-year 内报道篇数与各篇提及密度共同放大, 因此绝对量级不可跨银行/跨年直接横比水平, 须先除以同域 Σ mention_density 还原为 bian_2021_idf_tone_vw 语调均值后再作比较。三轨各自 just-identified、互为稳健性不分主次, 严禁把 full 与 ctx/ss 的加权分子混进同一 over-identified Hansen J。

## VAR: bian_2021_idf_score_w_sum_ss

【变体差分】
本列是三轨中的同句轨 (ss) 变体, 判据最严。文本载体为 content_ss——"标题 prepend + 目标银行与金融科技词在同一句 ±N 窗内共现"所截取的超文本 (stage 14 物化, N 由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。相对 ctx 轨的"实体窗"判据, ss 轨要求银行与金科词严格同句共现, 因而只保留语义关联最紧的语境, 用以检验主结论是否被"银行与金科同句强共现"这一最保守口径所支撑。计算链路与其余两轨对称: 篇章分子 bian_2021_idf_score_w_ss = bian_2021_idf_score_ss × mention_density, bank-year 内求和成列; IDF 与提及密度权重口径不变, 仅语调扫描的文本轨最窄。回退语义镜像 ctx: 当某篇不存在银行∧金科同句共现时, content_ss 回退为全文 body, ss_is_fallback=True, 与 ctx 回退公理同构 (frac_ss_fallback 高值提示同句信号弱、该轨退化为全文轨)。在开发期 T=2 短面板上, ss 轨可能因样本稀薄而出现方差退化, 属预期而非缺陷。还需与另一同名概念区分: ss 轨的"同句"判据 (extract_bank_fintech_cooccurrence, 银行∧金科严格同句) 与 stage 13 共现硬过滤所用的 has_bank_fintech_cooccurrence_within_radius (±1 句窗) 是两套不同口径的原语, 项目铁律禁止互相复用; 本列所依赖的是前者物化出的 content_ss 文本, 而非后者的过滤判据。IDF 词权重与提及密度权重的口径同 full/ctx 完全一致, ss 轨仅在语调扫描文本上最窄, 从而给出最保守的一端稳健性证据: 若主结论在 ss 轨仍成立, 则不能被"银行与金科仅泛泛同篇而非同句"的弱共现所解释。三轨各自 just-identified、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 作为 conditional-on-full 轨, 行集是 full 留篇集的子集。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual Analysis in Accounting: What's Next? Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12825
Harford, J., He, Q., & Qiu, B. (2026). Firm-Level Labor Shortage Exposure. The Review of Financial Studies, hhag049. https://doi.org/10.1093/rfs/hhag049
<!-- rendered-citations:end -->
