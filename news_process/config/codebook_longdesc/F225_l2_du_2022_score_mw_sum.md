---
family_id: F225
columns:
- du_2022_score_mw_sum_ctx
- du_2022_score_mw_sum_full
- du_2022_score_mw_sum_ss
unit: 无量纲加权净极性得分的银行-年求和 (媒体权威加权后按银行-年累加, 非比率非归一化)
formula: "du_2022_score_mw{track} = du_2022_score{track} × media_authority_weight; du_2022_score_mw_sum{track} = Σ_{i∈(bank,year)} du_2022_score_mw{track}; media_authority_weight = raw_media_weight / mean(raw_media_weight); du_2022_score = 语言学规则增强后的 du_2022 词典净极性 (pos_weighted − neg, 政治正面词以 0.5 权重计入正侧)"
producer: news_process/pipeline/panel/runner.py (步骤3c 逐篇 media_authority 加权) ; news_process/pipeline/panel/encode.py (build_aggregation_dict 银行-年求和) ; news_process/pipeline/sentiment/tone_words.py (du_2022_score 词典底分)
upstream:
- 22_tone_words.parquet (du_2022_score{track} 词典底分)
- 40 面板聚合 (media_authority_weight 逐篇加权 + 银行-年 sum)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.18653/v1/d16-1057
  type: wp
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: "10.1016/j.jcorpfin.2025.102835"
  type: "journal"
  authors: "Schweizer, D., Wang, X., Wu, G., & Zhang, A."
  year: 2025
  title: "Political connections and media bias: Evidence from China"
  venue: "Journal of Corporate Finance"
  vol: "94"
  pages_or_artno: "102835"
- doi: "10.1016/j.pacfin.2024.102499"
  type: "journal"
  authors: "Nguyen, M., Samarasinghe, A., & Skully, M."
  year: 2024
  title: "Watchdogs or Petdogs: The role of media freedom on banking system stability"
  venue: "Pacific-Basin Finance Journal"
  vol: "87"
  pages_or_artno: "102499"
- doi: "10.1287/orsc.2022.17237"
  type: "journal"
  authors: "Dewan, Y., Simons, T., & Wernicke, G."
  year: 2024
  title: "The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms"
  venue: "Organization Science"
  vol: "35"
  issue: "5"
  pages_or_artno: "1930-1955"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是 du_2022 中文金融情感词典在单篇报道上的净极性底分, 经媒体权威权重 (media authority weight, 简称 MW) 逐篇放缩后, 再在银行-年层面按篇累加而得的加权求和量。其底层词典来自 Du, Huang, Wermers 与 Wu (2022) 发表于 Review of Finance 的中文金融情感词典工作: 该词典针对中文金融语境的语言特异性与领域特异性重建极性词表, 正面词 2,235 个、负面词 2,986 个, 另含政治正面词 1,434 个。本项目在 tone_words 阶段对每篇报道用该词表计算净极性底分 du_2022_score, 其中政治正面词依 Du 等 (2022) 关于政治正面词信号弱于普通正面词的发现, 以 0.5 权重计入正侧 (canonical 口径 polw05); 语言学规则 (否定翻转、程度副词、转折) 在底分构造时一并施加。本家族在此底分之上叠加媒体来源的权威放缩, 目的是让来自权威、原创性更强媒体的报道在银行-年累加中获得更大话语权, 与等权累加互为稳健性对照。

【方法学与计算】
计算分三层。第一层在阶段 22 由 tone_words 产出逐篇词典底分 du_2022_score{track} (track ∈ full/ctx/ss)。第二层在面板 runner 步骤 3c 逐篇计算 media_authority_weight: 先按报道所属媒体名称 (精确匹配优先, 去括号模糊匹配兜底, 未命中落默认权重) 查得原始媒体权重, 再对全样本做均值归一化 (raw_series 除以其均值), 使权重均值锚定为 1.0、量纲无关; 随后令 du_2022_score_mw{track} = du_2022_score{track} × media_authority_weight。第三层在 encode 的聚合字典中把逐篇加权底分按银行-年求和, 得 du_2022_score_mw_sum{track}。需强调本家族是加权比率 du_2022_tone_mw 的分子累加量, 本身不是归一化语调: 它除以同银行-年的媒体权威权重之和 (sum_media_authority_weight) 才得到最终的加权净语调。因此它是一个中间累加量, 数值随报道篇数、媒体权威分布与词典命中强度共同变动, 单独解读时须结合分母口径。均值归一化保证了 MW 与等权累加 (score_sum) 在无媒体差异极限下退化一致, 也保证跨样本可比。

【文献定位】
媒体权威加权属于文本度量的话语权分层稳健性检验, 与以词频密度加权 (VW) 或羊群/产出端加权 (HW) 并列, 三者是同一构念的不同加权基, 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。词典侧的方法学谱系上, Du 等 (2022) 的中文金融词典是本家族的直接底分来源, 强调领域与语言特异性对情感抽取效度的决定性影响; Hamilton 等 (2016) 从无标注语料归纳领域特异极性词表的思路, 为这类领域词典的构造合法性提供方法学背书。近年中文金融情感词典的持续演进 (Ma 等, 2025 构建面向国内投资者的细粒度词典 CN-FSD; Sun 等, 2025 将词典知识与中性特征融入预训练语言模型) 表明词典法在中文金融文本上仍是效度可控、可复现的主力测度, 也说明以多部词典并排 (本项目并列六部词典) 做测量稳健性的必要性。本家族的媒体权威加权正是在既定词典底分上追加一层来源可信度分层, 使银行-年情感累加不被大量低权威通稿稀释。 媒体权威加权这一层的前提与限度须分别锚定, 不可含混。Schweizer、Wang、Wu 与 Zhang (2025) 以中国非国有上市公司新闻报道大样本实证发现, 有政治关联的企业获得显著更正面的媒体报道, 并借 Rule 18 反腐规定强制政治关联董事辞职这一监管冲击做 DiD 确证该因果链, 丑闻期政治关联企业面临更软化的媒体审视; 该文锚定的是「中国的媒体报道语调并非中性的信息镜像, 而可被系统性因素预测地偏移」这一同域前提。须显式声明其限度: 其异质性维度是被报道企业的政治关联属性, 而非媒体来源之间的异质性, 故不可据以主张「来源不同质故须按来源赋权」; 该文未构造任何权重函数, 亦未做权重乘词典分再求和, 样本为上市公司而非银行—年三轨。Nguyen、Samarasinghe 与 Skully (2024) 以跨国样本实证媒体自由度与银行稳定性在银行层与系统层均呈正相关, 并识别出存款人纪律渠道 —— 更高的媒体自由度向存款人扩散更多关于金融中介的信息、激励其约束银行的高风险行为, 且媒体的国有产权会削弱这一正向关系; 本家族仅据此作同域动机性引用, 说明媒体环境对银行侧结果具有系统性影响、媒体自身属性会调节其信息功能, 因而报道不宜被当作与来源无关的同质噪声处理。其边界较宽须如实写明: 该文的媒体维度是国别层面的媒体自由度指数, 与本家族逐篇的 media_authority_weight 既非同一层级也非同一构念, 不可据以声称 outlet 级权威性加权已获前沿支持; 其样本跨国、结果变量为银行体系稳定性, 且不涉及词典情感分与任何乘性加权求和层。outlet 级异质性的直接依据另引 Dewan、Simons 与 Wernicke (2024): 该文考察企业 CSR 行为如何影响新闻媒体对该企业的报道及报道倾向, 并表明该映射受媒体自身意识形态调节, 即不同来源对同一事实的呈现存在系统性差异, 恰是本家族按媒体名逐篇赋权的前提; 但该文语境为美国媒体与美国企业 CSR, 报道量与倾向是结果变量而非加权基, 不构造任何权重函数, 故只锚定「媒体报道非中性、来源有别」, 不锚定 raw_weight 除以均值的具体归一化公式。上述三条锚点与等权累加 (score_sum)、VW、HW 诸加权基之间仍适用同一纪律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。
## VAR: du_2022_score_mw_sum_ctx

【变体差分】
本列为实体上下文窗轨 (ctx) 的媒体权威加权净极性银行-年求和。与家族三列的唯一差分在文本轨道: ctx 轨的词典底分 du_2022_score_ctx 来自 content_ctx, 即在阶段 14 ctx_materializer 物化的"标题 prepend + 目标实体命中窗口"文本, 而非全文正文。其余计算链路 (政治正面词 0.5 权重、语言学规则、media_authority_weight 均值归一化逐篇相乘、银行-年累加) 与 full/ss 两列完全一致。ctx 轨聚焦于目标银行实体邻近的语义窗口, 意在剔除全文中与该银行无关的段落对情感底分的稀释, 因而在留篇门控为 full-only 口径 (2026-06-29) 下, ctx 属 conditional-on-full 的测度/稳健性轨: 行宇宙是 full 留篇集的子集, per-track 列照算。三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J。ctx 与 full 的差异越大, 说明全文中围绕该银行的情感语境越集中于局部窗口; 当实体未命中而 content_ctx 回退等于全文时, 本列数值将与 full 列趋同, 该退化由 frac_ctx_fallback 独立记录。作为加权求和的分子累加量, 本列须与同轨分母 sum_media_authority_weight 配对方能还原 ctx 轨的加权语调 du_2022_tone_mw_ctx。需注意 ctx 轨在实体命中率高的语料上比 full 轨更能抑制无关段落对情感底分的稀释, 因而在真实全量 T=19 生产语料上, ctx 与 full 的差异会承载额外的语义信息; 而在开发期窗口稀疏时该差异被回退退化压缩。本列与家族内政治词权重梯子、词典消融梯度等正交梯子互不交叉, 各梯子只在本轨的媒体权威加权维度内提供稳健性对照, 不与其它加权基或轨道混入同一识别方程。

## VAR: du_2022_score_mw_sum_full

【变体差分】
本列为全文轨 (full) 的媒体权威加权净极性银行-年求和, 是家族三列中的基准轨。其词典底分 du_2022_score_full 取自 content_full, 即标题 prepend 后的完整正文, 覆盖报道全部文本, 不做实体窗口裁剪。与 ctx/ss 两列的唯一差分同样只在文本轨道: full 轨吃全文, 因而词典命中面最广、单篇底分绝对量通常最大, 相应地在银行-年累加中样本信息最完整。留篇门控采用 full-only 口径 (2026-06-29), 即一篇报道是否算作"银行金科报道"只看 full 轨的 verified 判定, 故 full 轨的行宇宙就是本家族三轨共享的留篇总集, ctx/ss 是其 conditional-on-full 子集。计算上, full 底分先经政治正面词 0.5 权重 (canonical polw05) 与三条语言学规则增强, 再逐篇乘以均值归一化后的 media_authority_weight, 最后按银行-年求和。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。作为加权比率的分子累加量, 本列除以同银行-年的 sum_media_authority_weight 才得到 full 轨的媒体权威加权语调; 它与等权累加 du_2022_score_sum_full 的差异, 恰反映了权威媒体与低权威通稿在情感话语权上的再分配幅度, 是媒体来源可信度稳健性检验的核心输入。由于 full 轨命中面最广, 其加权累加对媒体权威分布的敏感度也最高: 若某银行某年的报道大量来自低权威通稿转载, full 轨的等权累加会被这些通稿主导, 而媒体权威加权则把话语权重新拉向署名深度稿与权威来源, 二者之差正是本列相对等权基准的信息增量。该增量在真实全量 T=19 语料上方能充分体现, 开发期 T=2 因媒体覆盖稀薄而受限。

## VAR: du_2022_score_mw_sum_ss

【变体差分】
本列为银行∧金科同句共现轨 (ss) 的媒体权威加权净极性银行-年求和。差分同样只在文本轨道: ss 轨的词典底分 du_2022_score_ss 来自 content_ss, 即标题 prepend 后仅保留"目标银行与金融科技词在同一句 ±N 窗共现"的文本 (ss_sentence_radius 默认 1)。ss 是三轨中语义最严的窗口, 聚焦银行与金科真正同句相邻的语境, 意在捕捉与金融科技直接相关的情感信号, 剔除银行泛报道的噪声。ss 的回退语义镜像 ctx: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 并与 ctx 一样共享 n_articles 物理篇数分母 (不另设 n_articles_ss); 当金科 AC 自动机为空时 *_is_fallback 全 True 优雅降级。因此在开发期 T=2 等窗口稀疏语料上, ss 列常与 full 列趋同, 该退化由 frac_ss_fallback 独立记录。其余计算 (政治正面词 0.5 权重、语言学规则、media_authority_weight 均值归一化逐篇相乘、银行-年累加) 与 full/ctx 完全一致。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J。本列作为分子累加量, 须与同轨分母配对还原 ss 轨的加权语调 du_2022_tone_mw_ss。ss 轨的构念定位与 ctx 略有分工: ctx 以实体窗口界定语境, ss 以银行与金科同句相邻这一更严判据界定语境, 因而 ss 底分命中最稀、单篇绝对量最小, 对媒体权威加权的响应也更依赖于同句共现是否发生。当共现频繁时, 本列刻画的是与金融科技直接相关的、经来源可信度再加权的情感累加; 当共现稀疏而大面积回退时, 本列退化为与 full 相近的全文加权累加。该轨与政治词权重、词典消融等正交梯子互不交叉, 仅在 ss 文本轨的媒体权威加权维度内充当稳健性一臂。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing No. 595-605 [Working Paper]. https://doi.org/10.18653/v1/d16-1057
Schweizer, D., Wang, X., Wu, G., & Zhang, A. (2025). Political connections and media bias: Evidence from China. Journal of Corporate Finance, 94, 102835. https://doi.org/10.1016/j.jcorpfin.2025.102835
Nguyen, M., Samarasinghe, A., & Skully, M. (2024). Watchdogs or Petdogs: The role of media freedom on banking system stability. Pacific-Basin Finance Journal, 87, 102499. https://doi.org/10.1016/j.pacfin.2024.102499
Dewan, Y., Simons, T., & Wernicke, G. (2024). The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms. Organization Science, 35(5), 1930-1955. https://doi.org/10.1287/orsc.2022.17237
<!-- rendered-citations:end -->
