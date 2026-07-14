---
family_id: F419
columns:
- loughran_idf_tone_sum_ctx
- loughran_idf_tone_sum_full
- loughran_idf_tone_sum_ss
unit: 语调得分之和 (bank-year 内逐篇 IDF 加权语调分的算术求和; 单篇取值区间约 [-1,1], 求和后随该 bank-year 报道量线性放大, 无固定上下界)
formula: 'bank-year 聚合: loughran_idf_tone_sum{track} = Σ_articles loughran_idf_score{track}; 其中 loughran_idf_score{track} 由状态机规则 (否定翻转/程度副词/转折连词) 作用于 loughran 词典的 IDF 加权版本后, 对逐词加权极性求和并按文本口径归一化得到 (与 loughran_score{track} 共享同一状态机 _compute_sentiment_with_rules, 唯一差异是词权重矩阵从 0/1 二值替换为 IDF 权重)。'
producer: pipeline\sentiment\tone_words.py (build_idf_weights / _build_idf_weighted_dict / _compute_sentiment_with_rules 生成逐篇 loughran_idf_score{track}) ; pipeline\panel\encode.py (agg[f'{d}_idf_tone_sum{track}'] = (f'{d}_idf_score{track}', 'sum') 聚合为 bank-year 求和列)
upstream: []
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T.; McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N.; Wu, D.
  year: 2013
  title: 'Word power: A new approach for content analysis'
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R.; Jennings, J.; Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M.; Brooke, J.; Tofiloski, M.; Voll, K.; Stede, M.
  year: 2011
  title: Lexicon-based methods for sentiment analysis
  venue: Computational Linguistics
  vol: '37'
  issue: '2'
  pages_or_artno: 267-307
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R.; Miller, B. P.; Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
new_dois: []
---

## CORE

【构念与来源】
本家族 loughran_idf_tone_sum 三列, 度量的是银行-年度 (bank-year) 面板单元内, 基于 Loughran & McDonald (2011) 中文本土化译本词典、经逐词 IDF (inverse document frequency) 权重放大后的语调得分, 在该 bank-year 观测涵盖的全部报道篇目上直接求和的结果。它属于本管道词典法情感测度体系 (stage 22, 词典打分产出层) 中 "词典 × IDF 稳健性检验 × 聚合方式" 三维交叉网格里的一个具体单元格: 词典维取值固定为 loughran (Loughran & McDonald 2011 JF 原始英文金融文本词典的中文主译本, 正面词 1,295 / 负面词 3,729, 另含五类非极性专门词类, 列前缀别名沿用 loughran); IDF 维取值固定为 idf (相对于等权基线 loughran_score/loughran_tone 的加权稳健性对照臂); 聚合方式维取值固定为 sum (相对于均值 loughran_idf_tone 与标准差 loughran_idf_tone_std 的求和口径)。三者叠加, 唯一自由维度是文本轨道 (full/ctx/ss), 这正是本家族三列的差分来源。
词典本身的合法性与用途已在 tone_words.py 模块头注中以表格形式固定: loughran_mcdonald_zh_2026 是 Loughran & McDonald (2011, Journal of Finance) 词典的中文主译本, 与管道内另外五部词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018) 并列构成六词典矩阵, 六者互为跨词典稳健性对照, 不设单一"主词典"。loughran 词典原始版本存在 61 个跨类重叠词 (同一词条同时出现在正面集与负面集), 经 2026-06-24 用户决策"两侧保留"消歧后, 38 词已归单侧, 余下 23 词按管道统一约定"两侧保留" (登记入 _BOTH_SIDED_BY_DICT, 打分时对该词典个体分数同时计入正负两侧, 净效果是把该词条的贡献拉向中性而非武断选边)。这一消歧口径对 IDF 加权臂同样适用 (IDF 仅缩放词条权重幅值, 不改变词典层面的极性归属与重叠词处理规则)。
【方法学与计算】
loughran_idf_score{track} 的计算分两步。第一步是 IDF 权重矩阵的构建: build_idf_weights 函数在 stage 22 运行时, 以该次运行涉及的全部文章 (按 content_full 文本口径去重计数, N = 唯一文本数) 为语料库, 对 loughran 词典中的每个词条 w 统计其文档频率 df(w) (出现该词的文章数), 计算原始 IDF raw_idf(w) = log₁₀(N / (1 + df(w))), 再做均值归一化 normalized_idf(w) = raw_idf(w) / mean(raw_idf), 最后按 [P1, P99] 分位数做 Winsorize 截尾, 得到 _build_idf_weighted_dict 产出的 词 word 的 capped_normalized_idf 值 权重字典。这一构造思路与 Jegadeesh & Wu (2013, Journal of Financial Economics) 提出的按语料库相对信息量对情感词加权的 "word power" 方法同源: 高频泛用词 (低 IDF) 被系统性降权, 低频专有词 (高 IDF) 被系统性加权, 目的是让语调得分更多由文本判别力强的词条驱动, 而非被通用高频词的重复出现主导。
第二步是逐篇打分: 对每篇文章 (每个文本轨道 track ∈ {full, ctx, ss} 各自独立), 复用与等权基线打分完全相同的状态机函数 _compute_sentiment_with_rules, 唯一区别是传入的词典从原始二值极性字典 (词条权重恒为 ±1) 替换为上一步构建的 IDF 加权字典 (词条权重为 ±capped_normalized_idf)。状态机依次施加三条语言学规则: 否定翻转 (词条前出现否定词时极性反号)、程度副词加权 (词条前出现程度副词时按六级强度表调整幅值)、转折连词降权 (转折连词后的从句语调权重按规则调低)。三规则共同作用后得到逐篇归一化的 idf_norm 值, 四舍五入到小数点后 4 位写入 result[f'{dict_name}_idf_score{track}'], 若词典为空或该轨道文本缺失, 则回退为 0.0 / NaN 并标记中性标签 (与等权基线在缺失语义上对称)。
第三步是 bank-year 面板聚合: pipeline/panel/encode.py 在构建 loughran_idf_tone_sum{track} 时, 以 pandas groupby-agg 对同一 bank-year 单元内全部文章的 loughran_idf_score{track} 直接取 sum (而非 mean 或 std), 得到本家族三列的最终数值。sum 聚合方式与同一网格内的 mean 聚合 (loughran_idf_tone{track}, 篇均语调) 及 std 聚合 (loughran_idf_tone_std{track}, 语调分散度) 三者并列, 各自捕捉不同的分布矩: sum 天然会随该 bank-year 观测到的报道篇数增多而放大, 因此它同时承载了"语调方向"与"报道体量"两重信息, 在解释上须与 n_articles 类分母列联合审视, 不宜脱离样本规模单独解读为纯粹的语调强度指标; 若研究设计需要剥离规模效应而只保留语调水平信息, 应转用 mean 口径的 loughran_idf_tone{track} 而非本家族。
【文献定位】
本家族的方法学谱系交汇于两条独立文献线。第一条是词典构造与验证线: Loughran & McDonald (2011, The Journal of Finance) 首次系统证明通用情感词典 (如 Harvard-IV) 在金融文本上大量误判 (把行业中性词误判为负面), 提出须构造领域专用金融词典, 该文是本管道六词典矩阵的方法论起点, 也是本家族列名前缀 loughran 的直接出处。第二条是词权重构造线: Jegadeesh & Wu (2013, Journal of Financial Economics) 提出用词条在语料库中的相对信息量 (而非简单二值出现/不出现) 对情感词加权的 "word power" 方法, 与本家族 IDF 加权臂在"让判别力强的词主导得分"这一构造哲学上同源, 是 loughran_idf_tone_sum 相对于等权基线 loughran_tone_sum 的直接文献支撑。IDF 加权与等权两臂在本管道中被明确设计为互为稳健性检验、不分主次的并列臂, 而非互相替代的"改进版"关系: 若两臂在下游回归中给出定性一致的结论, 说明语调测度结果不依赖于是否对词条做语料库层面的判别力加权, 这一稳健性论证思路呼应 Frankel, Jennings & Lee (2022, Management Science) 关于不同文本情感测量方法 (词典法内部不同权重方案、以及词典法与机器学习法之间) 应互为交叉验证而非线性替代的方法论主张。Taboada et al. (2011, Computational Linguistics) 对词典法情感分析中语言学规则 (否定/程度/转折) 的系统综述, 为本家族共享的状态机规则层 (与等权基线完全一致的三规则叠加) 提供了通用方法学依据。Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体语调加权测量在会计与金融文本中如何影响下游经济结果解释力的讨论, 佐证了在银行-金融科技报道语境下对语调测度做加权稳健性检验 (而不满足于单一等权基线) 的实证价值。
需特别澄清本家族与管道内另一条正交梯子——政治词权重敏感性 (du_2022 词典特有, political_positive 类词以 {0.0, 0.5, 1.0} 三档权重敏感性检验) ——之间的边界: 二者虽同属"加权"范畴, 但加权对象、加权依据与适用词典完全不同 (本家族对 loughran 词典的全部词条按语料库 IDF 加权; du_2022 权重梯子只对该词典内 political_positive 一个专门词类按研究者设定的固定权重加权), 属于互不重叠、可分别独立解释的两套稳健性设计, 不应混为一谈或混入同一识别方程。同理, 本家族与词典规则消融梯度 (raw/negonly/degonly/advonly 等 rule-ablation 变体) 也是正交关系: 消融梯度控制的是否定/程度/转折三条语言学规则的开关组合, 本家族三列则固定使用全规则 (full) 状态机, 仅在词权重矩阵上做 IDF 替换, 两个维度互不交叉, 各自的组内变体各自 just-identified 并排, 不应混入同一个 over-identified 的 Hansen J 过度识别检验。

## VAR: loughran_idf_tone_sum_ctx

【变体差分】
本列文本口径为 ctx 轨: 标题 + 目标银行实体窗口文本 (content_ctx, 由 stage 14 materialize_ctx 在标题前缀化后物化), 与全文轨 (full) 相比只保留围绕目标银行实体出现位置的窗口片段, 意在剔除文章中与目标银行无直接关联的段落对语调打分的稀释或污染。当某篇文章不存在可识别的银行实体窗口时, ctx_is_fallback 标记为 True, content_ctx 退化为与 full 轨相同的全文 body, 此时该篇对 loughran_idf_tone_sum_ctx 的贡献与它对 full 轨的贡献在数值上重合, 但仍计入 ctx 轨的分母/分子统计 (共享 n_articles 口径), 不做单独剔除。
IDF 权重矩阵与词典消歧规则 (23 个跨类重叠词两侧保留)、状态机三规则 (否定/程度/转折) 均与 full/ss 轨完全共享同一套参数, ctx 与其余两轨之间的唯一差异是喂入 _compute_sentiment_with_rules 的分词文本来源不同。由于 build_idf_weights 的 IDF 统计口径固定以 content_full 文本去重计数为 N (代码内 _idf_text_col = 'content_full'), 三轨共享同一份 IDF 权重字典, 即 ctx 轨并不会因文本片段变短而重新估计一套"ctx 专属"IDF, 这保证了三轨之间的语调分数在词权重维度上严格可比, 差异只来自文本片段本身。
按管道口径铁律, ctx 轨与 full、ss 两轨是互为稳健性检验的并列测度, 不设主次之分, 三者各自 just-identified, 严禁在同一 over-identified 的 Hansen J 或类似过度识别检验中把三轨混合作为同一构念的多重工具变量使用。留篇门控 (2026-06-29 起) 采用 full-only 口径, 即某篇文章是否被认定为"一篇有效的银行-金融科技报道"只看 llm_verified_full 是否为真; ctx 轨 (与 ss 轨一样) 相对于这一留篇集合是条件性 (conditional-on-full) 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 但该子集之上的 loughran_idf_score_ctx 打分与 sum 聚合仍按 ctx 轨自身文本独立计算, 不借用 full 轨的分数。

## VAR: loughran_idf_tone_sum_full

【变体差分】
本列文本口径为 full 轨: 标题 + 全文正文 (content_full, prepend_title 前缀化后的完整文章文本), 是三轨中信息量最完整、也是留篇门控 (2026-06-29 起) 唯一依据的口径 —— 一篇文章是否被判定为有效的银行-金融科技报道, 只看该篇在 full 轨上的 llm_verified_full 标记, ctx 与 ss 两轨的留篇集合都是 full 轨留篇集合的子集。因此 loughran_idf_tone_sum_full 天然对应"报道体量最大"的分母口径, 三列中其求和绝对值通常最大 (覆盖篇目最多), 但这并非本列在构念上比 ctx/ss 更"优先"或更"正确"——本管道的一致口径是三轨互为稳健性并列测度, 不分主次, full 轨只是留篇判定的锚点, 不是语调测量本身的权威版本。
IDF 权重字典的构建口径 (build_idf_weights 内 _idf_text_col = 'content_full') 恰好与本列的文本口径一致, 即本列是三轨中 IDF 权重估计样本与打分样本同源的那一个; ctx/ss 轨复用同一份权重字典对各自的窗口/同句文本打分, 属于跨口径复用而非各轨独立重估。这一实现细节不改变三轨"互为稳健性、并列不分主次"的解释原则, 只是提示读者: 若要严格审视 IDF 权重估计样本与打分样本是否同源, full 轨是唯一无跨口径迁移的版本。
本列与家族内均值口径 loughran_idf_tone_full、标准差口径 loughran_idf_tone_std_full 共享同一批逐篇 loughran_idf_score_full 输入, 三者是同一原始信号在 bank-year 聚合层面的三种不同矩统计, 互相补充而非互相替代: sum 反映"语调方向 × 报道体量"的复合信号, mean 反映剥离体量效应后的篇均语调水平, std 反映该 bank-year 内部报道语调的分散/极化程度。

## VAR: loughran_idf_tone_sum_ss

【变体差分】
本列文本口径为 ss 轨 (same-sentence): 标题 + 目标银行与金融科技词汇在同一句子内共现的窗口文本 (content_ss), 判据比 ctx 轨的实体窗口更严格——要求银行实体与金融科技相关词汇严格同句共现 (受 config/filtering.yaml::context_window.ss_sentence_radius 控制, 生产口径半径默认为 1, 即允许 ±1 句的窗口容差; 该键与 stage 13 共现硬过滤所用的 cooccurrence_filter.sentence_radius 是两个独立配置键, 不可混用)。ss 轨的回退语义镜像 ctx 轨: 当某篇文章内不存在满足条件的银行∧金融科技同句共现片段时, ss_is_fallback 标记为 True, content_ss 退化为与 full 轨相同的全文 body, 该篇对 loughran_idf_tone_sum_ss 的贡献仍计入统计、共享 n_articles 分母, 不做单独剔除, 这一优雅降级设计与 FINTECH_AC (金融科技自动机) 为 None 时全体 *_is_fallback 置 True 的降级路径在语义上一致。
词典 (loughran, 含 23 个两侧保留重叠词的消歧规则)、IDF 权重字典 (以 content_full 口径估计, 三轨共享)、状态机三规则 (否定/程度/转折) 均与 full/ctx 两轨完全一致, ss 轨与其余两轨的差异同样只体现在喂入打分函数的文本片段上。由于 ss 轨判据比 ctx 轨更严格 (同句而非实体窗口), 在存在共现的文章中 ss 轨文本片段通常比 ctx 轨更短、更聚焦, 相应地该篇 loughran_idf_score_ss 的打分样本 (词条数) 也更少, 这是解读 ss 轨求和值时需要注意的机械性特征, 不代表语调方向本身的系统性偏移。
与 ctx、full 两轨同理, ss 轨在管道口径下是与另外两轨互为稳健性检验的并列测度, 各自 just-identified, 严禁三轨混入同一 over-identified 的 Hansen J 或类似过度识别检验框架。留篇门控口径下, ss 轨的行宇宙同样是 full 轨留篇集合的子集 (conditional-on-full), 但 loughran_idf_score_ss 的逐篇打分与本列的 bank-year sum 聚合完全基于 ss 轨自身文本独立计算完成。

<!-- rendered-citations:begin -->
Loughran, T.; McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Jegadeesh, N.; Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Frankel, R.; Jennings, J.; Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M.; Brooke, J.; Tofiloski, M.; Voll, K.; Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Holzman, E. R.; Miller, B. P.; Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
<!-- rendered-citations:end -->
