---
family_id: F636
columns:
- yao_2021_tone_sum_ctx
- yao_2021_tone_sum_full
- yao_2021_tone_sum_ss
unit: 无量纲词典极性得分和 (等权分子, 未归一; bank-year × 轨道)
formula: "yao_2021_tone_sum{track} = Σ_{a ∈ bank-year} yao_2021_score{track}(a); 其中 yao_2021_score{track}(a) 是 stage 22 tone_words 对报道 a 用 Yao et al. (2021) 词典逐篇算出的未加权净极性分 (正负词命中经否定翻转/程度副词/转折三条语言学规则后相减得净分); encode.py 等权 (equal-weight) 聚合段在银行-年-轨道内对 yao_2021_score{track} 直接求和得本列; 下游等权语调 yao_2021_tone{track} = yao_2021_tone_sum{track} / n_articles_llm_valid{track}(该银行-年-轨道留篇报道数)"
producer: news_process/pipeline/panel/encode.py (等权 E 段 agg[f'{d}_tone_sum{track}'] = (f'{d}_score{track}', 'sum')) ; news_process/pipeline/panel/stata_export.py (标签导出)
upstream:
- 22_tone_words.parquet (逐篇未加权 yao_2021_score_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
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
本家族三列 yao_2021_tone_sum{full,ctx,ss} 是 Yao et al. (2021) 中文金融情感词典在银行-年层面的「等权得分和」, 即最基础的等权 (equal-weight, EW) 语调聚合的未归一分子。它要回答的问题是: 在一个银行-年-轨道单元内, 把每篇留篇报道各自算出的 Yao 词典净极性分不加任何权重地直接累加, 结果的方向与体量是多少。之所以要把这个求和结果单独存档为一列, 而不是只保留除法之后的归一化语调, 是因为分子本身携带了「净极性方向」与「报道体量」两层信息, 在核对聚合口径、判定零新闻年份退化、以及与其它加权口径 (提及密度加权 vw、媒体权威加权 mw、跟风衰减加权 hw) 的分子并置比较时, 未归一的和更透明、更便于溯源。当某银行-年-轨道内没有任何留篇报道时, 该和是空集求和, 按 Σ over ∅ = 0 的契约落 0, 而不是缺失值, 这一契约与同族其它「_sum」聚合列 (词性计数和、声调和等) 保持一致, 避免面板与 .dta 导出中零新闻行残留为点号。

【方法学与计算】
计算须分清两个阶段的分工。第一步在情感词典阶段 (stage 22 tone_words) 完成: 对每篇留篇报道, 先用 Yao et al. (2021) 词典匹配正负情感词, 并应用与其余五部中文金融情感词典共享的三条语言学规则 (否定翻转、程度副词加权、转折句式调整) 后相减求得逐篇净极性分 yao_2021_score{track}; 这一逐篇分是无量纲的, 且不含任何面板层面的权重。第二步在面板聚合阶段 (encode.py 等权 E 段) 完成: 对同一银行-年-轨道内所有留篇报道的 yao_2021_score{track} 直接求和 (equal weight, 即权重恒为 1), 得到 yao_2021_tone_sum{track}。这与另一族 score_w_sum (value-weighted, 由 panel runner 步骤 3b 先乘以来自 stage 11 news_salience 的提及密度权重再求和) 是两条并行但不同的加权路径: 前者 (本家族) 是纯等权累加, 后者是提及密度加权累加, 二者互为稳健性并排、不分主次, 也不应混同求和口径。随后 encode.py 同段以该银行-年-轨道的留篇报道数 n_articles_llm_valid{track} 为分母作除法, 派生出归一化的等权语调 yao_2021_tone{track}, 故本家族三列在数学上正是这一 canonical 等权语调的分子。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入银行-年宇宙, 由 full 轨的 LLM 判定 (llm_verified_full == True) 决定; ctx 与 ss 两轨的行集合是 full 轨留篇集的严格子集, 三轨各自在该子集上逐轨求和, ctx/ss 不借用 full 轨的分子或分母。单位为无量纲得分和: 逐篇净极性分本身无固定区间, 求和后的量纲随报道条数伸缩, 因而本列只可在同一银行、同一轨道、跨年份或跨银行的相对体量意义上比较, 不能直接当作 [-1,1] 区间的归一化语调数值使用 (那是下游 yao_2021_tone{track} 的职责)。

【文献定位】
词典来源 Yao et al. (2021) 是本家族极性分的唯一词典依据, 与同仓另外五部中文金融情感词典 (Jiang 2021、Bian 2021、Du 2022、You 2018、Loughran & McDonald 中译) 并列构成词典轨内部的跨词典稳健性梯队。方法论定位上, van Atteveldt, van der Velden & Boukes (2021) 系统比较人工标注、众包、词典法与机器学习四类情感测度路径, 指出词典法的偏差来源与适用边界, 是本仓把词典轨、LLM 三家投票轨、BERT 三模型轨并置为「三方法互为稳健、不分主次」设计的方法学依据; Frankel, Jennings & Lee (2022) 在 Management Science 上以真实披露文本直接对比机器学习情感与词典法情感, 为词典法在金融文本场景下与更复杂方法并列存证提供了顶刊层面的直接先例。就中文金融语域的词典专用性而言, Du et al. (2022) 在 Review of Finance 论证语言与领域专用性对中文金融情感测度的必要性, 说明为何本仓不满足于通用情感词典而要引入 Yao 等多部中文金融专用词典; Ma, Zhang & Zhang (2025) 面向中国境内投资者构建细粒度中文情感词典 (CN-FSD), 代表这一谱系向更细颗粒度演进的近期进展, 与 Yao 词典同属为中文金融文本定制的情感资源家族。铁律须再述: 六部词典各自 just-identified 并排, 词典轨内部的等权/提及密度加权/媒体权威加权/跟风衰减加权四种聚合口径同样各自 just-identified 并排, 与三轨 full/ctx/ss 一并均为「互为稳健性、不分主次」, 禁混进同一 over-identified Hansen J; 词典轨与 LLM 轨、BERT 轨之间同理只作互为稳健性对照, 不合并识别。 就本家族「逐篇语调→单元级求和」这一聚合形态本身, 近期文献亦有可援引的先例。Fernandez-Perez、Fuertes、Miffre 与 Zhao (2025) 以新闻通讯社 (newswire) 语调叠加构造商品组合信号, 其做法正是把逐篇通讯社报道的语调按标的聚合成单元级语调量再进入下游分析, 与本家族把逐篇 yao_2021_score{track} 在银行-年-轨道内累加为未归一分子的口径同构; 迁移边界须写实: 该文聚合单元是商品-期而非银行-年三轨, 语料为英文 newswire, 且不含 IDF、提及密度、媒体权威、跟风衰减任何一层加权, 故只锚求和聚合口径的存在性。Lehkonen、Heimonen 与 Pukthuanthong (2025) 以 Refinitiv MarketPsych 指数构造媒体语调, 证明比率型媒体语调 (正负提及净额除以总提及) 是可跨截面定价货币的真实风险因子, 为本家族分子在下游除以 n_articles_llm_valid{track} 后形成的比率型语调这一测度形态提供了经济含义层面的近期论证; 惟其语调取自专有商业 NLP 指数而非自建词表命中计数, 构造细节不可复核, 与本仓公开中文词典自建计数的透明度不可比, 且其层级为货币 (国别)、DV 为汇率收益的因子定价, 亦无中文分词与否定翻转规则, 该文不得被援引为任何词级或聚合层加权口径的依据。在应用同域上, Wang、Xiao、Wang 与 Wang (2025) 在中国语境下从新闻报道抽取情感并聚合到企业层面用于债务成本实证, 与本家族「中文新闻情感 → 实体-年测度」的链路形态一致, 可作为该链路的近期实例; 惟其实体为一般上市公司、DV 为债务成本, 且不区分等权与加权两种聚合口径, 无三轨文本范围, 故只锚应用语境而非本家族的具体求和算法。Wei、Wei、Wu 与 Jing (2025) 构造新的中文文本指数度量中国银行的党组织建设, 并接入银行层面面板检验其对银行稳定性的影响, 为「中文文本→银行层面指数→银行面板回归」这一整体链路提供了应用同域 (中国银行×中文文本计量) 的近期范例; 该条须按降级口径引用: 其文本源与指数构造口径未经核实, 极可能为银行自身披露文件的主题/关键词计数, 而非情感词典净极性经三条语言学规则后的银行-年求和, 其 DV 为银行稳定性, 亦无三轨与四层加权, 因此仅锚链路存在性, 不构成对本家族计分或聚合公式的任何支持。
## VAR: yao_2021_tone_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨的 Yao 词典等权得分和。相对于家族 canonical 的 full 轨, 差分仅在参与词典命中统计的文本域: ctx 轨逐篇文本 content_ctx 由 stage 14 ctx_materializer 物化, 是标题 (prepend_title 前置) 加上以目标银行/金融科技实体为中心的上下文窗口, 而非全文正文。因此逐篇净极性分 yao_2021_score_ctx 只在该实体邻近窗口内统计 Yao 词典命中, 三条语言学规则 (否定/程度/转折) 同样只作用于窗口内文本, 随后在银行-年内不加权直接求和即得本列。语义上它衡量「把注意力收窄到实体上下文后, 该银行当年报道的等权词典净极性体量」, 与 full 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。留篇宇宙受 full-only 门控约束: 行集是 full 轨留篇集的子集, ctx 轨逐轨自算分子, 分母 n_articles_llm_valid_ctx 同样是该子集内的条件计数而非借用 full 轨分母。当某银行-年缺 content_ctx 源列或该轨聚合结果为空集时, 按 Σ over ∅ = 0 落 0, 不产生单边孤儿。与归一化的 yao_2021_tone_ctx 相比, 本列保留未除分母的和, 便于核对窗口口径下的极性方向与体量; 收窄到实体窗口的代价是当窗口过小时可能丢失有效极性词, 收益是滤掉与目标银行无关段落的噪声, 两者只作互为稳健性并排, 不以相关性高低择一为主。在早期试跑 T=2 极小样本上 ctx 轨可能因命中稀疏呈现较大波动, 属预期退化, 生产期 T=19 语料下恢复正常。

## VAR: yao_2021_tone_sum_full

【变体差分】
本列是 full (全文) 轨, 为家族的 canonical 等权得分和列。其底层文本域 content_full 由标题 prepend 后拼接全文正文构成, 且是留篇门控 (2026-06-29 full-only) 的判定轨: 一篇报道是否计入银行-年宇宙, 唯独由 full 轨的 LLM 判定 (llm_verified_full == True) 决定, ctx/ss 两轨的留篇集是其严格子集。逐篇净极性分 yao_2021_score_full 在整篇正文范围内统计 Yao 词典命中并应用三条语言学规则, 在银行-年内等权 (权重恒为 1) 求和即得本列; 随后除以该轨的留篇报道数 n_articles_llm_valid_full 得到归一化等权语调 yao_2021_tone_full。作为 canonical, 它给出「覆盖整篇正文、不加权」的词典净极性体量, 是等权词典轨的主口径分子, 也是三轨中样本框最完整的一轨 (因为它本身即为留篇判定所依据的那一轨)。相对于同族 ctx/ss, 差分仅在文本域覆盖范围, 三轨各自 just-identified 并排、互为稳健性、不分主次; 相对于同轨的 score_w_sum (提及密度加权和), 差分在是否引入 stage 11 news_salience 的提及密度权重, 二者同样互为稳健性并排、不合并识别。零新闻银行-年按 Σ over ∅ = 0 落 0。使用者须注意本列是未归一分子, 数值随当年留篇报道条数同向伸缩, 跨银行-年比较时应改用下游 yao_2021_tone_full, 本列的价值在于以「和」的形态保留可溯源、可与其他加权口径分子并置核对的原始聚合结果。

## VAR: yao_2021_tone_sum_ss

【变体差分】
本列是 ss (同句) 轨的 Yao 词典等权得分和, 三轨中文本域最窄。ss 轨逐篇文本 content_ss 取标题 prepend 后, 只保留银行与金融科技词在同一句子及其 ±N 句窗内共现的片段 (窗半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1); 逐篇净极性分 yao_2021_score_ss 只在该严格共现语境内统计 Yao 词典命中, 三条语言学规则同样只作用于该片段, 再在银行-年内等权求和即得本列。回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body 且该篇标记 ss_is_fallback=True, 与 ctx 共享 n_articles 分母口径; 若上游金融科技 AC 词典未加载 (FINTECH_AC=None), 则 ss_is_fallback 对全部行记为 True, 优雅降级为等同 full 覆盖但仍逐轨独立求和。语义上本列衡量「把注意力收窄到银行与金科严格同句共现语境后, 该银行当年报道的等权词典净极性体量」, 与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 留篇宇宙同为 full-only 门控下 full 留篇集的子集, ss 轨逐轨自算, 缺源列或空集时按 Σ over ∅ = 0 落 0, 不借邻轨分子分母。与 ctx 轨相比, 差别在于共现判据的严格程度: ctx 只要求实体落入邻近窗口, ss 要求银行与金融科技词严格同句 (或同句 ±N 窗) 共现, 是三轨中信号最聚焦、也最易触发回退的一轨, 与 full/ctx 构成由宽到窄的规格阶梯。需强调回退不是缺失: 回退篇仍以全文 body 参与词典命中统计, 只是 ss_is_fallback 标记其非真同句共现, 供下游按需剔除或作为敏感性检验的过滤条件。在早期试跑 T=2 上 ss 轨常因同句共现稀疏而大面积回退甚至呈现零方差, 属预期退化, 生产期 T=19 语料下恢复正常, 不影响本列作为等权词典和分子的口径定义。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N. (2025). Newswire tone-overlay commodity portfolios. Journal of Banking & Finance, 178, 107501. https://doi.org/10.1016/j.jbankfin.2025.107501
Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
Wei, L., Wei, M., Wu, Y., & Jing, Z. (2025). Does party organization construction improve chinese banks' stability? Evidence from a new textual index. China Economic Review, 94, 102541. https://doi.org/10.1016/j.chieco.2025.102541
<!-- rendered-citations:end -->
