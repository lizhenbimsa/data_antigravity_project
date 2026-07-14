---
family_id: F218
columns:
- du_2022_idf_tone_sum_ctx
- du_2022_idf_tone_sum_full
- du_2022_idf_tone_sum_ss
unit: 语调得分总和 (无量纲; bank-year 内逐篇 IDF 加权净语调的求和, 随该行报道篇数放大)
formula: "du_2022_idf_tone_sum{track} = Σ_{i∈bank-year} du_2022_idf_score_i{track}; 其中逐篇 du_2022_idf_score = (Σ_pos w_idf·s − Σ_neg w_idf·s) / (Σ_pos w_idf·s + Σ_neg w_idf·s), w_idf(word) = Winsor_{P1,P99}( log10(N/(1+df(word))) / mean(log10(N/(1+df))) )"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _analyze_single_article ; 聚合 news_process/pipeline/panel/encode.py::_build_valid_agg_map (sum)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_idf_score_full / _ctx / _ss)
- 40_panel_yearly.parquet
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
- doi: 10.1111/jofi.12027
  type: journal
  authors: Garcia, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: The Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是以 Du et al. (2022) 中文金融情感词典 (下称 du_2022 词典) 打分、并经逆文档频率 (IDF) 加权后, 在银行—年 (bank-year) 单元内对该单元全部相关报道逐篇净语调的求和值。构念上它回答的问题是: 在一个银行的某一年里, 以"稀有词更能说明问题"的加权口径衡量, 全部涉该行的金融科技报道在情感极性上累积贡献了多大的正负净量。之所以取求和 (sum) 而非均值, 是因为求和保留了报道数量维度: 一个被媒体密集关注、且负面调性词反复出现的银行—年, 其累积语调总量会显著偏离零, 而一个只有寥寥数篇中性报道的单元则总量趋近于零。因此该测度天然是"外延量" (extensive), 同时编码了语气方向与媒体注意力强度两重信息, 与家族内均值口径 du_2022_idf_tone (内涵量, 已剔除篇数) 形成互补。

du_2022 词典本身取自 Du et al. (2022) 发表于 Review of Finance 的中文金融情感词典工作, 该词典针对中文金融文本的领域特异性与语言特异性重建了极性词表, 含正面词 2,235 条、负面词 2,986 条, 另设政治正面词 1,434 条。生产口径遵循 CLAUDE.md 铁律: 政治正面词以 0.5 权重计入正侧 (依据 Du et al. 政治正面词信号弱于普通正面词的发现), 且该 0.5 为研究者选择并另有 {0.0, 0.5, 1.0} 三权重的敏感性梯子; 但本 idf 家族固定采用生产口径 (含政治词 0.5 权重), 政治词权重梯子在别处物化, 两者正交不交叉, 本家族不再展开。跨类重叠词 (positive∩negative) 遵循 2026-06-24"保留并两侧计数"决策, 登记到两侧同时计票, 使个体词典净语调对重叠词拉向中性而不武断选边; IDF 仅缩放词的幅值、不改其极性归属, 故重叠词在 IDF 轨与 raw 轨的处理完全同口径。

【方法学与计算】
计算分两级。第一级为逐篇文章级 IDF 加权打分 (阶段 22, tone_words.py)。IDF 权重在与词频打分完全同一语料上估计: 对每个情感词 word, 先算原始权重 raw_idf(word) = log10(N / (1 + df(word))), 其中 N 为去重后唯一文档数、df(word) 为包含该词的文档数; 再对全体情感词做均值归一化 normalized_idf = raw_idf / mean(raw_idf), 使 IDF 加权后整体量级与等权版可比; 最后按 P1/P99 做 Winsorization 抑制极端权重。该三步 (平滑 IDF + 均值归一化 + 缩尾) 直接落地信息检索与文本计量中经典的逆文档频率 (稀有词加权) 思想: 像"发展""提高"这类几乎每篇都出现的高频词信息量低而被压权, 像"违约""挤兑"这类罕见词一出现即高度诊断性而被抬权。权重估计文本为含标题的 content_full (标题以 prepend 方式并入正文), 以保证 IDF 语料与 TF 打分语料严格一致, 避免标题词的 df 被系统性低估。逐篇 du_2022_idf_score 即以 IDF 加权后的 du_2022 词典重算净语调, 净语调本身经否定翻转、程度副词、转折三条语言学规则增强 (与 raw 轨同规则), 再对绝对幅值自归一化落到约 [−1, 1]。第二级为面板聚合 (阶段 40, encode.py): 对 bank-year 单元内全部留篇报道的 du_2022_idf_score 逐篇求和, 得本家族列。

留篇门控遵循 full-only 口径 (2026-06-29): 某篇是否计入"一篇银行金科报道"仅由 llm_verified_full 判定, ctx/ss 轨为 conditional-on-full 测度, 其行宇宙是 full 留篇集的子集, 但 per-track 列各自照算。求和聚合对缺失源列由 valid_agg 按存在性自动过滤: 若某轨源列 (如 du_2022_idf_score_ss) 未产出则该轨优雅跳过而不借用他轨分母。

【文献定位】
本测度处在金融文本情感的词典法测量传统内。词典法的现代规范由 Loughran 和 McDonald (2011) 在《Journal of Finance》确立: 通用情感词表在金融语境中系统性误判 (如"liability"), 须构建领域词典, 这一诊断正是 du_2022 面向中文金融文本重建词表的直接动因。Garcia (2013) 将词频计数式的媒体语气引入资产定价, 证明报纸情感在衰退期对收益的预测边际最大, 为"对全部报道语气求和以捕捉累积媒体调性"提供了外延量口径的先例。IDF 加权则将信息检索与文本计量中经典的逆文档频率 (稀有词信息量) 思想嫁接到词典法上, 使少数高诊断性词主导语气, 而非被海量套话稀释。Barbaglia et al. (2025) 系统比较了经济文本的词典法路线, 论证在可解释性与跨语料稳定性上词典法相对黑箱模型的独立价值, 支持本项目以词典轨与 LLM 轨、BERT 轨并列互证的设计。Frankel, Jennings 和 Lee (2022) 直接比较词典法与机器学习法的披露情感, 结论是两法各有系统性偏差、宜互为稳健性对照而非彼此替代——这正是本项目将 du_2022 的 IDF 加权轨作为词频加权稳健性检验轨、与主 tone 轨并排的方法学依据。就三轨 (full/ctx/ss) 而言, 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 检验。

## VAR: du_2022_idf_tone_sum_full

【变体差分】
本列为 full 轨 IDF 加权 du_2022 净语调在 bank-year 内的求和。full 轨的打分文本 = 标题 prepend 后的全文正文 (content_full), 即完整报道内容, 是三轨中信息最完整、也是本项目留篇门控与主口径所锚定的轨道。与家族内均值列 du_2022_idf_tone_full 的区别在聚合算子: 本列用 sum, 保留 bank-year 内报道篇数维度, 因而同时编码语气方向与媒体注意力强度, 是外延量; 均值列除以篇数、剔除强度, 为内涵量。与非 IDF 的 du_2022_tone_sum_full 的区别在词权重: 本列各情感词按 log10(N/(1+df)) 归一缩尾后的 IDF 权重加权, 罕见高诊断词 (如"挤兑""违约") 主导语气, 高频套话词被压权, 从而作为词频加权口径的稳健性检验轨; 后者为等权口径。留篇门控为 full-only, 故本 full 轨列的行宇宙即银行金科报道留篇全集。IDF 权重在含标题的 content_full 上估计, 与 full 轨打分语料严格同源, 无标题词 df 低估问题。政治正面词按生产口径以 0.5 权重计入正侧。在解读上, 本列取值随 bank-year 报道篇数放大: 一个被密集负面报道的银行—年会累积出较大负的语调总量, 而报道寥寥或调性中性的单元趋近零, 故本列不应与均值列直接比较水平, 而应在同一聚合口径 (sum) 内跨轨、跨词典或跨 IDF/等权对照解读。作为词频加权稳健性轨, 本列与 raw tone 轨、ctx/ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

## VAR: du_2022_idf_tone_sum_ctx

【变体差分】
本列为 ctx 轨 (实体窗轨) IDF 加权 du_2022 净语调在 bank-year 内的求和。ctx 轨的打分文本 = 标题 prepend 后的"标题 + 实体窗口"文本 (content_ctx), 即仅保留目标银行实体附近上下文窗口的内容, 相较 full 轨滤除了与目标行无关的段落, 用以检验语气信号是否被无关文本稀释或污染。与 full 轨同名列的唯一差别即在此文本轨道: 词典、IDF 权重表、政治词 0.5 权重、语言学规则、sum 聚合算子全部一致, 只是逐篇打分所扫描的文本范围收窄到实体窗口。留篇门控仍为 full-only, 故 ctx 轨为 conditional-on-full 测度: 其行宇宙是 full 留篇集的子集 (仅在 full 判为留篇的报道上计算 ctx 得分), per-track 求和列照算。若 ctx 源列缺失则该轨聚合优雅跳过, 不借用 full 轨分母。作为窗口收窄的稳健性轨, 本列与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J。需注意在浅面板 (T 极小) 上 ctx 轨可能因窗口内情感词稀疏而方差退化, 属预期现象而非缺陷。就构念区分而言, ctx 轨相对 full 轨的价值在于诊断"语气信号是否来自与目标行真正相关的段落": 若 full 与 ctx 求和列在回归中给出一致符号与量级, 说明主结论不由无关文本的调性驱动; 反之则提示 full 轨可能掺入了与该行金融科技无关的报道情绪, 从而为读者提供稳健性证据。IDF 权重表在全语料 content_full 上估计, ctx 轨打分沿用同一权重表, 不因窗口收窄而重估 IDF, 以保证跨轨权重口径一致、可比。

## VAR: du_2022_idf_tone_sum_ss

【变体差分】
本列为 ss 轨 (同句共现轨) IDF 加权 du_2022 净语调在 bank-year 内的求和。ss 轨的打分文本 = 标题 prepend 后的"标题 + 银行与金融科技词同句 (±N 句窗) 共现内容" (content_ss), 是三轨中过滤最严的一轨, 仅保留目标银行与金融科技概念在同一句 (含小窗) 内共现的文本段, 用以隔离出真正谈及"该行金融科技"而非泛泛提及该行的语气信号。回退语义镜像 ctx 轨: 当某篇不存在银行与金科词的同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True 并共享 n_articles 分母; 当 FINTECH_AC 为空时全部 *_is_fallback 优雅置 True 降级。与 full/ctx 同名列的唯一差别即在文本轨道口径 (最严的同句共现过滤), 其余词典、IDF 权重、政治词 0.5 权重、语言学规则、sum 聚合完全一致。留篇门控为 full-only, 故 ss 轨同为 conditional-on-full 测度, 行宇宙是 full 留篇集的子集; ss 源列缺失时该轨聚合优雅跳过而不借他轨分母。作为最严过滤的稳健性轨, 本列与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。在浅面板上 ss 轨常因共现样本稀少而近零方差, 属预期退化, 在生产规模的深面板上方可正常出值。就构念区分而言, ss 轨是三轨中对"该行金融科技"这一具体议题最贴近的语气度量: full 轨可能计入仅顺带提及该行的报道, ctx 轨放宽到实体窗口, 而 ss 轨要求银行与金科概念严格同句共现, 因而信噪比最高但样本最稀。IDF 权重表同样沿用全语料 content_full 估计值, ss 轨打分不重估 IDF, 保证跨三轨的词权重口径完全一致、可比。三轨 sum 列共同构成从宽到严的文本过滤稳健性梯子, 供读者评估语气—结果关系对文本界定口径的敏感度。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
