---
family_id: F072
columns:
- avg_within_doc_redund_han_ctx
- avg_within_doc_redund_han_full
- avg_within_doc_redund_han_ss
unit: 比率 (无量纲), 取值域 [0,1] ∪ NaN
formula: "avg_within_doc_redund_han = bank-year mean of (1 − 唯一汉字3-gram数 / 全部汉字3-gram数); 分子分母同为篇内汉字 3-gram, 剔数字/标点/拉丁字符"
producer: pipeline\sentiment\lexical_complexity.py (Stage 22 文章级篇内冗余, _han_trigram_redundancy 计算, within_doc_redundancy_han 落列) ; pipeline\panel\encode.py (Stage 40 bank-year mean 聚合, agg[within_doc_redundancy_han{track}]='mean') ; 标签登记于 pipeline\panel\export.py + pipeline\panel\codebook.py
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - 22_tone_words.parquet (Stage 22 lexical_complexity 文章级篇内冗余)
  - 40_panel_yearly.parquet (Stage 40 bank-year 聚合)
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting — A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: "1-15"
- doi: 10.48550/arXiv.2411.04257
  type: arxiv
  authors: Khan, A., Underwood, R., Siebenschuh, C., Babuji, Y., Ajith, A., Hippe, K., Gokdemir, O., Brace, A., Chard, K., & Foster, I.
  year: 2024
  title: "LSHBloom: Memory-efficient, extreme-scale document deduplication"
  venue: arXiv
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: The Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1002/j.1538-7305.1948.tb01338.x
  type: journal
  authors: Shannon, C. E.
  year: 1948
  title: "A mathematical theory of communication"
  venue: Bell System Technical Journal
  vol: 27
  issue: 3
  pages_or_artno: 379-423
- doi: "10.1111/lang.12630"
  type: "journal"
  authors: "Bestgen, Y."
  year: 2024
  title: "Measuring Lexical Diversity in Texts: The Twofold Length Problem"
  venue: "Language Learning"
  vol: "74"
  issue: "3"
  pages_or_artno: "638-671"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一篇媒体报道内部的自我重复程度, 即篇内冗余 (within-document redundancy), 并聚合到银行-年层面。构念直觉是: 一篇文章若把同一批表述反复堆叠, 其真正携带的增量信息就低; 反之, 若行文推进而少见字面回环, 单位篇幅承载的信息就高。冗余度因此是文本信息含量的逆向代理, 与可读性复杂度、罕见词率、名词化率等文本测度共同构成报道语言学画像的一个正交侧面。本家族采用汉字口径 (Han-char), 即在计算前先把文本收缩为纯汉字序列, 剔除阿拉伯数字、标点符号与拉丁字母, 使分子分母同为汉字, 从而与并存的字符口径孪生列 avg_within_doc_redund 构成双口径 (hanzi-char-dual)。汉字口径是把源自英文披露文本的做法在中文语料上的本地化落地, 避免数字串与英文缩写在字符 3-gram 里造成的口径污染, 让"重复"更贴近中文表意单元本身的复现。

数据来源上, 文本取自新闻语料经预处理、银行实体识别、金科词识别与共现硬过滤后的留篇集; 三条并存文本轨 (content_full / content_ctx / content_ss) 在 Stage 14 物化, 标题以 prepend 方式并入正文。篇内冗余在 Stage 22 的词法复杂度环节按文章逐篇计算, 再在 Stage 40 以银行-年为单位取算术均值, 得到本家族三列。留篇与否的门控为 full-only 口径 (2026-06-29): 一篇报道是否计入某银行某年的分母, 只看其 full 轨是否被判为一篇银行金科报道; ctx 与 ss 轨降为 conditional-on-full 的测度轨与稳健性轨, 行宇宙是 full 留篇集的子集, 各轨在其自身可用篇上分别计列。

【方法学与计算】
文章级计算遵循经典的 n-gram 唯一性比率思路: 先把文本收缩为汉字序列, 滑窗生成全部汉字 3-gram, 令冗余 = 1 − (去重后唯一 3-gram 数 / 全部 3-gram 数)。当一篇文章的字面表述高度重复时, 大量 3-gram 相互重合, 唯一比率下降, 冗余趋近上界; 当行文几乎不重复时, 唯一比率接近 1, 冗余趋近 0。因此本测度值域为 [0,1], 篇幅过短无法构成有效 3-gram 或整轨文本缺失时以 NaN 表达并沿 NaN 传播, 不以 0 冒充"零冗余"。银行-年层面取文章级冗余在该银行该年留篇上的简单均值, 记为 avg_ 前缀。冗余对文本长度存在机械相关 (长文更易复现片段), 家族刻意并存配对长度控制列 avg_redund_han_log_length (篇内 ln 汉字数的 bank-year 均值, mean-of-ln 口径), 供回归时与冗余同域配对使用; 该长度控制与 geography 侧 ln-of-mean 的 ln_han_count 是两种不同聚合口径, 刻意并存不可混用。

需要强调的一处口径边界: 篇内冗余度量的是同一篇文章内部的字面自重复, 与跨篇、跨期的陈旧度 (staleness) 及年际文本变化 (lazy Jaccard) 构念正交 — 前者问"这一篇是否啰嗦地自我重复", 后者问"今年这篇相对去年那篇是否照抄"。二者不可互相替代。此外, 汉字口径冗余与字符口径冗余在文章级相关极高 (源码标注文章级 corr 约 0.99), 故本家族三列是字符口径的敏感性诊断轨而非独立构念, 属 hanzi-char-dual 稳健性对照; 二者禁同进一回归式, 以免共线且构念重复计数 (实测相关的确切数值待生产 T=19 语料回填)。

【文献定位】
篇内冗余作为文本信息含量逆代理, 其思想根植于信息论: Shannon (1948) 把冗余定义为符号序列可预测部分的占比, 高冗余意味着单位符号承载的信息熵低, 这为"重复越多、增量信息越少"提供了原始理论锚。在会计与财务披露文本研究中, You & Zhang (2009) 论证披露复杂度会削弱投资者对信息的即时吸收, 引发对复杂文本的反应不足, 而重复冗长正是复杂度的一个可操作侧面; Lesmy, Muchnik 与 Mugerman (2025) 在跨制度比较中记录了财务报告复杂度随时间攀升的趋势, 呼应了以文本结构量化信息可及性的研究路线。方法层面, Hansen, McMahon 与 Prat (2018) 以计算语言学手段量化央行审议文本的信息与重复结构, 示范了如何把机械的文本统计量映射为具经济含义的沟通测度, 是本家族"机械文本比率→经济语义代理"路径的方法学范本。工程侧, Khan 等 (2024) 提出的大规模文档去重方法从相反方向印证了 n-gram 重叠作为冗余/重复识别原语的可扩展性与稳健性。本家族即在中文媒体语料上把上述篇内冗余思路以汉字 3-gram 唯一比率落地, 并保留字符/汉字双口径与配对长度控制以支撑稳健性诊断。 就本测度已知的长度偏倚, Bestgen (2024) 给出了最直接的方法学依据: 该文在三个英语学习者文本数据集上系统批判常用词汇多样性指数, 指出『双重长度问题』——第一重是 type-token 比率类指数本身随文本长度系统漂移; 第二重是即便以概率或算法方法把所有文本削减至等长从而解决了第一重, 这些指数仍对『决定该等长长度的参数取值』高度敏感, 无一幸免。本家族的 1 − 唯一汉字 3-gram / 全部汉字 3-gram 在数学上正是 (1 减) 一个 type-token 比率, 上述双重长度问题原样适用, 这也正是本家族必须与 avg_redund_han_log_length 等配对长度列并置解读、而非单独解读其水平高低的测度学理由。迁移边界须明示: 该文在字母语言学习者语料上做词级 type-token 分析, 与本项目的中文汉字 3-gram 阶在语言与 n-gram 阶数上均不同; 原文未研究金融或新闻文本, 也未提出本项目采用的 mean-of-ln 长度聚合; 其给出的等长削减类校正本项目并未实施——引用它是为诚实披露长度依赖并提示本项目未做校正, 不是主张该问题在本家族已被解决。
## VAR: avg_within_doc_redund_han_ctx

【变体差分】
本列是家族汉字口径篇内冗余在 ctx 轨上的银行-年均值。ctx 轨的文本是 content_ctx: 标题 prepend 后, 正文收缩到目标银行等实体的邻近上下文窗口 (实体窗口拼接), 而非整篇全文。相对 full 轨, ctx 轨聚焦在银行实体周边的表述, 剔除了与目标实体距离较远的段落, 因此其篇内冗余刻画的是"围绕该银行的局部叙述是否自我重复", 口径比 full 更窄、更聚焦于实体语境。在 full-only 门控下, 本列属 conditional-on-full 的测度轨: 行宇宙是 full 轨留篇集的子集, 仅在该银行该年 ctx 文本可用的篇上计算并取均值; 若某篇 ctx 上下文为空或过短无法构成有效汉字 3-gram, 则该篇以 NaN 表达并沿 NaN 传播, 不借用 full 分母凑数。

轨道口径之外, 本列的汉字口径 (剔数字/标点/拉丁)、3-gram 唯一比率公式、以及与字符口径孪生列的高相关诊断地位, 均与家族 CORE 所述一致。三轨 (full/ctx/ss) 之间是各自 just-identified 并排、互为稳健性、不分主次的关系: 三轨分别进入各自的自回归或设定, 用以证明主结论不被"取哪条文本轨"这一选择所驱动; 铁律是三轨禁混进同一 over-identified 的 Hansen J 过度识别检验, 也禁与字符口径冗余同进一回归式 (hanzi-char-dual 高共线)。在开发期 T=2 的浅面板上, ctx 轨因窗口更窄、有效篇更少, 可能出现方差退化, 属预期现象; 生产期 T=19 语料上该轨恢复正常刻画力。

## VAR: avg_within_doc_redund_han_full

【变体差分】
本列是家族汉字口径篇内冗余在 full 轨上的银行-年均值, 也是三轨中承担留篇门控职责的 canonical 文本轨。full 轨文本为 content_full: 标题以 prepend 方式并入完整正文, 覆盖全篇而非实体窗口。因此本列刻画的是整篇报道层面的字面自重复程度, 是家族最直接、覆盖面最全的篇内冗余度量。按 full-only 门控 (2026-06-29), 一篇报道是否计入某银行某年的分母, 正是以其 full 轨判定为准; 本列的行宇宙即该留篇集本身, ctx 与 ss 两轨的行宇宙都是它的子集。

计算上, 本列与家族 CORE 完全一致: 文本收缩为纯汉字序列后取全部汉字 3-gram, 冗余 = 1 − 唯一 3-gram / 全部 3-gram, 银行-年取留篇算术均值, 有效 3-gram 不可构成时以 NaN 表达并传播。需要与相邻列区分的两点: 其一, 本列是汉字口径, 与字符口径 avg_within_doc_redund_full 构成 hanzi-char-dual 双口径, 二者文章级相关极高 (约 0.99), 是敏感性诊断关系而非独立构念, 禁同进一回归; 其二, 篇内冗余与跨篇陈旧度、年际 lazy Jaccard 构念正交, 分别回答"篇内是否自我重复"与"跨期是否照抄"。作为主轨, 回归中若使用本列, 应配对使用同轨、同域的长度控制列 avg_redund_han_log_length_full 以吸收冗余与篇幅的机械相关。三轨各自 just-identified 并排、互为稳健性、禁混同一 over-identified Hansen J 的铁律同样适用于本列。

## VAR: avg_within_doc_redund_han_ss

【变体差分】
本列是家族汉字口径篇内冗余在 ss 轨上的银行-年均值。ss 轨文本为 content_ss: 标题 prepend 后, 正文收缩到"目标银行与金科词严格同句共现"的句子及其上下 N 句窗口 (句半径由 filtering.yaml 的 ss_sentence_radius 控制, 默认 1), 是三轨中最聚焦、口径最窄的一轨, 专门刻画银行与金融科技在同一叙述语境下的表述。其篇内冗余因此度量的是"银行金科同句语境的局部行文是否自我重复"。ss 轨采用镜像 ctx 的优雅回退语义: 当一篇报道内不存在银行与金科的同句共现时, content_ss 回退为全文正文, 该篇的 ss_is_fallback 置为 True, 并与 ctx 共享 n_articles 分母口径; 若金科 AC 自动机为空导致无法判定, 则相关 *_is_fallback 全部置 True 作整体降级。这一回退保证本列在稀疏共现下不静默清空, 而是可解释地退回全篇口径。

在 full-only 门控下, 本列同为 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集, 仅在该银行该年 ss 文本 (含回退后的全文) 可用的篇上计算并取均值, 无有效汉字 3-gram 时以 NaN 表达并传播。汉字口径、3-gram 唯一比率公式、以及与字符口径孪生列的高相关诊断地位与家族 CORE 一致。三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 铁律是三轨禁混进同一 over-identified 的 Hansen J, 也禁与字符口径冗余同进一回归式。开发期 T=2 上, ss 轨因同句共现约束最紧、有效篇最少, 可能出现零方差或近似退化, 属预期现象; 生产期 T=19 语料上恢复正常刻画力。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting — A comparative study. Humanities and Social Sciences Communications, 12, 1-15. https://doi.org/10.1057/s41599-025-06094-y
Khan, A., Underwood, R., Siebenschuh, C., Babuji, Y., Ajith, A., Hippe, K., Gokdemir, O., Brace, A., Chard, K., & Foster, I. (2024). LSHBloom: Memory-efficient, extreme-scale document deduplication. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2411.04257
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
Bestgen, Y. (2024). Measuring Lexical Diversity in Texts: The Twofold Length Problem. Language Learning, 74(3), 638-671. https://doi.org/10.1111/lang.12630
<!-- rendered-citations:end -->
