---
family_id: F136
novelty_exempt_rationale: "该家族是 bian_2021 词典语调分在 bank-year 层的求和 (sum) 聚合变体, 与 canonical 均值列 bian_2021_tone 共用同一套逐篇打分构造与词典来源, 仅聚合算子由 mean 换为 sum 以刻画外延边际, 属于测度的机械聚合变体而非独立学术构念, 其学术依据已由母族词典文献 (Bian et al. 2021 等) 覆盖, 无需额外追新文献。"
columns:
- bian_2021_tone_sum_ctx
- bian_2021_tone_sum_full
- bian_2021_tone_sum_ss
unit: 语调总和 (无量纲, 单篇净极性分逐篇相加; 近似落于 [-n_articles, n_articles], 无固定上下界)
formula: "bian_2021_tone_sum{track} = Σ_j bian_2021_score_j{track} (对 bank-year 单元内留篇报道 j 求和); 单篇 bian_2021_score = total_score / total_abs_score = Σ_i s_i / Σ_i |s_i|, 对篇内每个命中词 i 求和, s_i 为叠加否定翻转/程度分级/转折规则后的带符号加权分 (正词正、负词负), 分母为同一组 |s_i| 之和 (both-sided 重叠词按 2×|s_i| 计入分母, 使归一化口径偏中性); 分子分母同源、皆含语言学规则加权, 数值近似落于 [-1, 1]"
producer: news_process/pipeline/panel/encode.py (bank-year 'sum' 聚合); 标签 news_process/pipeline/panel/stata_export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (article-level bian_2021_score{track})
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1016/j.jbankfin.2025.107501"
  type: "journal"
  authors: "Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N."
  year: 2025
  title: "Newswire tone-overlay commodity portfolios"
  venue: "Journal of Banking & Finance"
  vol: "178"
  pages_or_artno: "107501"
- doi: "10.1016/j.jbankfin.2025.107542"
  type: "journal"
  authors: "Lehkonen, H., Heimonen, K., & Pukthuanthong, K."
  year: 2025
  title: "Media tone is a priced risk factor in currency markets"
  venue: "Journal of Banking & Finance"
  vol: "180"
  pages_or_artno: "107542"
- doi: "10.1016/j.pacfin.2025.102721"
  type: "journal"
  authors: "Wang, Y., Xiao, J., Wang, L., & Wang, D."
  year: 2025
  title: "News sentiment and the cost of debt"
  venue: "Pacific-Basin Finance Journal"
  vol: "91"
  pages_or_artno: "102721"
- doi: "10.1016/j.chieco.2025.102541"
  type: "journal"
  authors: "Wei, L., Wei, M., Wu, Y., & Jing, Z."
  year: 2025
  title: "Does party organization construction improve chinese banks' stability? Evidence from a new textual index"
  venue: "China Economic Review"
  vol: "94"
  pages_or_artno: "102541"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 bian_2021_tone_sum_full、bian_2021_tone_sum_ctx、bian_2021_tone_sum_ss 度量的是: 在一个银行—年度 (bank-year) 单元内, 以 Bian、Jia、Li 与 Yan (2021) 构建的中文金融情感词典对每篇银行金融科技报道逐篇打出的净极性语调分之总和 (sum), 而非该单元内的均值。该词典是一部面向会计与金融文本的中文情感词表, 以工作论文形式发布于 SSRN (编号 3446388), 其正、负面词表针对中文财经语域重新筛选, 相较于英文场景直译的词表更贴合中文年报、公告与财经新闻的表达习惯, 因此被本项目纳入六部并行的中文金融情感词典之一, 与 Du、Huang、Wermers 与 Wu (2022) 等其余词典构成词典法内部的互为稳健性并排轨。逐篇语调分 bian_2021_score 的构造遵循标准净极性归一化口径: 先在报道文本上以冻结版 jieba 分词切词, 对照 Bian 等 (2021) 的正面词与负面词统计命中, 再叠加三条针对中文的语言学状态机规则——否定翻转、程度副词分级、转折让步——为每个命中词赋一个带符号的加权分 (正面词取正、负面词取负)。单篇分值采用带符号分之和除以其绝对值之和的归一化口径, 即 total_score 除以 total_abs_score, 分子为篇内所有命中词带符号加权分的代数和, 分母为同一组加权分绝对值的总和; 其中同时落入正负两侧的重叠词按其绝对值的两倍计入分母, 从而把归一化结果向中性方向拉动, 因此这是一个近似而非精确的正负差比值, 数值近似落在负一到正一之间。在 bank-year 层, tone_sum 把该单元内所有留篇报道的单篇分值直接相加, 得到一个不设固定上下界的总和量: 其绝对值同时随报道语调的强度与报道篇数上升, 因此刻画的是情感的外延边际 (extensive margin), 与家族 canonical 的均值列 bian_2021_tone 所刻画的内涵边际 (intensive margin) 互补。

【方法学与计算】
tone_sum 列由 pipeline/panel/encode.py 在 bank-year 聚合阶段以 pandas 具名聚合 (源列 bian_2021_score{track}, 聚合算子 sum) 生成, 每个文本轨道独立成列; Stata 变量标签由 pipeline/panel/stata_export.py 机械挂载。上游依赖两级: 一是 14_materialize_ctx.parquet 物化的三条文本列 content_full / content_ctx / content_ss (以及各自的回退旗标), 二是 22_tone_words.parquet 中逐篇算出的 bian_2021_score{track}。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入 bank-year 单元, 只由 full 轨的 LLM 留篇判定 (llm_verified_full 为真) 决定; ctx 与 ss 轨降为在 full 留篇集之上条件计算的测度轨, 其行宇宙是 full 留篇集的子集, 各轨列在该行宇宙上按本轨文本各自求和。三条文本轨的语义严格分层: full 轨为标题 prepend 后的全文正文, ctx 轨为标题加实体上下文窗口, ss 轨为标题加银行与金融科技同句共现窗口; ss 轨在无同句共现时镜像 ctx 的回退语义、退回全文 body 并置 ss_is_fallback 为真, 与 ctx/full 共享 n_articles 分母口径。三轨 tone_sum 属规格稳健性并排: 各自 just-identified 并排、互为稳健性不分主次, 严禁把三轨混进同一个 over-identified 的 Hansen J 过度识别检验。与均值列相比, 求和聚合对留篇篇数敏感, 因而在做跨银行、跨年度比较时通常需与 n_articles 或篇数控制项联用, 或作为均值主轨结论的稳健性佐证而非独立识别源。

【文献定位】
本家族的词典源头是 Bian 等 (2021): 该文的核心贡献是为中文会计与金融文本重建一部本土化的情感词典, 弥补英文词表直译在中文语域上的失配。与之并列的另一部权威中文金融情感词典来自 Du 等 (2022) 发表于 Review of Finance 的研究, 该文系统论证了语言与领域特异性对情感测度的实质影响, 是本项目将多部中文词典并排为互为稳健性轨的直接理据。词典法这一测度范式的方法学根基可追溯至 Loughran 与 McDonald (2011) 发表于 Journal of Finance 的经典工作, 他们指出通用情感词表在金融文本中系统性误判, 从而奠定了领域专用词典的必要性; García、Hu 与 Rohrer (2023) 发表于 Journal of Financial Economics 的研究进一步用大规模标注数据校准了金融词汇的情感色彩, 为词典命中的极性赋权提供了实证依据。在测度效度层面, Frankel、Jennings 与 Lee (2022) 于 Management Science 比较了词典法与机器学习法在披露情感上的表现, 支持将词典法与 LLM、BERT 三角并置作为互为稳健性设计; van Atteveldt、van der Velden 与 Boukes (2021) 则从人工标注、众包、词典与机器学习的对比中系统评估了情感分析的效度边界, 提示词典法总和量在解读时须与人工基准和替代测度交叉验证。 就把逐篇语调按单元求和这一聚合算子而言, Fernandez-Perez、Fuertes、Miffre 与 Zhao (2025) 用新闻通讯社语调叠加构造商品组合信号, 为把逐篇语调聚合成标的-期层面的语调量提供了近期存在性; 惟原文标的为商品期货组合与英文 newswire, 聚合层级是商品-期而非银行-年三轨, 且无 IDF、媒体权威度或羊群衰减加权层, 亦非中文六词典。Lehkonen、Heimonen 与 Pukthuanthong (2025) 以 Refinitiv MarketPsych 指数 (覆盖约 2,000 家全球媒体与 800 家社交站点的约 700 万篇文本) 构造媒体语调, 证明比率型媒体语调 (正负提及净额除以总提及) 是可跨截面定价货币的真实风险因子, 为本家族逐篇 Σ s_i / Σ |s_i| 这一比率型测度形态提供了经济含义论证; 所锚仅止于此: 原文语调取自专有商业 NLP 指数而非自建词表命中计数, 构造细节不可复核, 与本家族公开中文词典自建计数的透明度不可比, 其层级为货币(国别)、DV 为汇率与货币收益, 亦未使用中文分词与否定翻转规则, 更无按极性符号对主体-期篇数分拆的操作。应用同域一侧, Wang、Xiao、Wang 与 Wang (2025) 在中国语境下自新闻报道抽取情感并聚合到企业层面用于债务成本实证, 是中文新闻情感到实体-年测度这一链路的近期实例, 用以锚定本家族的应用语境而非其具体算法 (原文实体为一般上市公司、DV 为债务成本, 无三轨文本范围与本项目的多层加权口径); Wei、Wei、Wu 与 Jing (2025) 构造新的中文文本指数度量中国银行的党组织建设, 并接入银行层面面板检验其对银行稳定性的影响, 为中文文本到银行层面指数再到银行面板回归的整体链路提供了同域范例, 惟该文文本源与指数构造口径未经核实 (据题名保守判读, 极可能为银行自身披露文件的主题或关键词计数), 并非六部情感词典净极性经语言学规则加权后的银行-年求和, 其 DV 亦为银行稳定性, 只可作应用同域参照。
## VAR: bian_2021_tone_sum_full

【变体差分】
本列是 Bian (2021) 词典语调总和在全文轨 (full) 上的实现, 也是本家族三轨中与留篇门控口径完全对齐的主轨。其文本通道为标题 prepend 之后的完整正文: 先把报道标题拼接到正文最前, 再在整篇文本上逐篇计算 bian_2021_score_full, 最后在 bank-year 单元内对所有留篇报道的单篇分值求和。相对于家族其余两轨, full 轨的差分维度在于文本覆盖面最广——它不做任何实体窗口或同句共现的裁剪, 因此单篇分值综合了报道全篇的正负词命中, 求和后的量既反映语调强度也反映留篇篇数。由于 full-only 门控 (2026-06-29) 规定一篇报道是否计入 bank-year 单元仅由 full 轨的 LLM 留篇判定决定, 本列的行宇宙即为留篇全集本身, 而 ctx 与 ss 两轨的行宇宙是本列行宇宙的子集。本列与家族 canonical 的均值列 bian_2021_tone_full 的关键区别在于聚合算子: 前者用 sum、刻画外延边际 (总量随篇数与强度共同变动), 后者用 mean、刻画内涵边际 (单位报道的平均语调)。因此在跨单元比较时本列通常需与篇数控制联用, 或作为均值主轨结论的稳健性佐证而非独立识别源。作为词典法六部并排轨之一, 本列还与其余五部中文金融情感词典的同轨总和列互为稳健性, 用以证明主结论不被任一部词表的词汇取舍所驱动。本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 严禁把三轨混入同一个 over-identified 的 Hansen J。

## VAR: bian_2021_tone_sum_ctx

【变体差分】
本列是 Bian (2021) 词典语调总和在实体上下文窗口轨 (ctx) 上的实现。其文本通道为标题 prepend 加实体上下文窗口: 在标题拼接正文之后, 仅保留银行与金融科技实体命中位置附近的上下文片段作为计分文本, 因此相较 full 轨剔除了与目标实体无关的段落, 使单篇语调分更聚焦于银行金融科技这一具体语境。bank-year 层的求和口径与其余两轨一致——把该单元内所有留篇报道的单篇 bian_2021_score_ctx 直接相加。本列区别于 full 轨的核心差分在文本裁剪范围: ctx 只在实体窗口内取词, 命中词更集中、噪声段落更少, 但也可能因窗口过窄而漏掉全篇层面的语气线索。依 full-only 门控, 本列在 full 留篇集的子集上条件计算: 留篇与否由 full 轨判定, ctx 轨仅在被留下的报道上按本轨文本各自求和; 当某报道缺失有效实体窗口时按回退旗标处理。本列与家族均值列 bian_2021_tone_ctx 的区别同样在于聚合算子由 mean 改为 sum, 因而对篇数敏感, 通常作为均值主轨的稳健性佐证而非独立识别源。作为与 full 轨互补的规格稳健性轨, 本列检验的是当计分文本收窄到实体窗口时总和量结论是否依然定性稳健。本列与 full、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一个 over-identified 的 Hansen J 过度识别检验。

## VAR: bian_2021_tone_sum_ss

【变体差分】
本列是 Bian (2021) 词典语调总和在同句共现窗口轨 (ss) 上的实现, 是三轨中文本约束最严的一轨。其文本通道为标题 prepend 加银行与金融科技同句共现窗口: 仅保留银行实体与金融科技实体落在同一句 (可含前后 N 句半径, 默认半径为一) 的片段作为计分文本, 因此单篇语调分只捕捉两类实体真正同句关联时的情感表达, 语境最纯但覆盖面最窄。bank-year 层仍按求和聚合, 把留篇报道的单篇 bian_2021_score_ss 直接相加。ss 轨的差分要点在其回退语义: 当某报道不存在银行与金融科技同句共现时, 本轨镜像 ctx 的降级逻辑, 退回全文 body 计分并置 ss_is_fallback 为真, 且与 full/ctx 共享同一 n_articles 分母口径, 从而避免因样本框收缩造成的口径漂移。依 full-only 门控, 本列同样在 full 留篇集的子集上条件计算, 留篇由 full 轨判定。本列与家族均值列 bian_2021_tone_ss 的区别在聚合算子由 mean 改为 sum, 刻画外延边际而非平均语调, 对篇数与回退占比均较敏感, 解读时须结合回退旗标, 通常作为均值主轨结论的稳健性佐证而非独立识别源。作为文本约束最严的一轨, 本列检验的是当情感只取自银行与金融科技真正同句关联时总和量结论是否依然成立。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性不分主次, 严禁把三轨混入同一个 over-identified 的 Hansen J。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N. (2025). Newswire tone-overlay commodity portfolios. Journal of Banking & Finance, 178, 107501. https://doi.org/10.1016/j.jbankfin.2025.107501
Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
Wei, L., Wei, M., Wu, Y., & Jing, Z. (2025). Does party organization construction improve chinese banks' stability? Evidence from a new textual index. China Economic Review, 94, 102541. https://doi.org/10.1016/j.chieco.2025.102541
<!-- rendered-citations:end -->
