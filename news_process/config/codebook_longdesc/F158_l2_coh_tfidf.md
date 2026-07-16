---
family_id: F158
columns:
- coh_tfidf_w_ctx
- coh_tfidf_w_full
- coh_tfidf_w_ss
unit: 无量纲余弦相似度得分, 取值区间 [0, 1] (相邻两年 bank-year 聚合文档的 TF-IDF 向量夹角余弦; 首年与年份间隙返回 NaN)
formula: "coh_tfidf_w_{trk} = cosine( TFIDF_jieba(doc_{i,t,trk}), TFIDF_jieba(doc_{i,t-1,trk}) ), 定义域限于连续相邻年度 year_t 与 year_{t-1}; doc = 该 bank-year 该轨聚合新闻文本经 jieba 词级切分后的词袋 TF-IDF 表示"
producer: news_process/pipeline/features/strategic_diff.py ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (bank-year 聚合文档)
citations:
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.48550/arXiv.2004.05150
  type: arxiv
  authors: Beltagy, I., Peters, M. E., & Cohan, A.
  year: 2020
  title: "Longformer: The long-document transformer"
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是「相邻期文本连贯性」(temporal text coherence): 同一家银行相邻两个连续年度所对应的媒体新闻文本, 在词汇构成层面上的相似程度。直觉上, 若一家银行在 t 年与 t−1 年被媒体报道的内容高度雷同 (措辞、主题、术语重复), 则连贯性得分高, 表明该银行的媒体叙事在时间上稳定、缺乏更新; 反之, 若相邻两年报道内容发生显著改写与主题迁移, 得分低, 表明媒体感知层面发生了实质性变化。该测度的思想直接承袭金融文本研究中「逐年文本相似度」这一经典范式: Cohen、Malloy 与 Nguyen (2020) 在其被广泛引用的研究中, 以企业年报相邻两期披露文本的相似度作为核心变量, 发现披露文本「懒惰」不变 (相似度高) 的企业, 其后续股价反应存在可预测的滞后, 揭示了文本变化本身携带增量信息。本项目将这一「相邻期相似度」思路从企业自撰的年报披露文本, 迁移到第三方媒体新闻语料上, 因而测量的是「媒体叙事的年际连贯性」而非「企业自我披露的年际连贯性」, 构念内涵已作相应校准, 后文局限部分会明确这一迁移带来的解释边界。生产实现记录于欧阳志刚与胡雯华 (2024) 的方法参照下, 落在 strategic_diff.py 的相邻期连贯性变量块。

【方法学与计算】
计算分三步。第一步是文档聚合: 对每个 bank-year 单元, 将该银行该年度全部入选新闻按对应文本轨拼接为一份聚合文档 (聚合口径见「与三轨的关系」)。第二步是向量化: 对聚合文档做 jieba 词级切分, 构造词袋并计算 TF-IDF 权重, 得到该 bank-year 文档的稀疏词向量; 本家族三列统一采用 jieba 分词的「词级」(word-level) TF-IDF 通道, 以与同一相邻期连贯性块内另一条「字级」(char-level) 通道 coh_tfidf_c 形成分词粒度上的并排稳健性对照 —— 词级切分保留了金融领域复合词与专有名词的语义完整性, 字级切分则对分词错误与未登录词更鲁棒, 二者各自 just-identified 并排、互为稳健性、不分主次, 严禁把词级与字级两个通道混进同一个 over-identified 的 Hansen J 过度识别检验。第三步是相邻期匹配: 取该银行 t 年与 t−1 年两份 TF-IDF 向量的余弦相似度作为 t 年的连贯性得分, 取值落在 [0, 1] 区间。关键的定义域约束是: 连贯性严格定义在「相邻连续年度」上 —— 只有当 year_t 与 year_{t−1} 均存在且相差恰为一年时才计算, 对每家银行的首个观测年、以及样本中出现年份间隙 (跨年缺失) 的年度一律返回 NaN, 这与同一生产模块内 strat_fluidity 流动性变量的缺失处理保持一致, 避免把「跨越多年的一次性跳变」误当作「相邻一年的平滑演化」。留篇口径遵循全项目 full-only 门控 (2026-06-29): 一篇报道是否计入 bank-year 文档由 full 轨的留篇判定决定, ctx/ss 轨在此留篇集合之上按各自文本口径重新物化聚合文本, 因而三轨行宇宙是 full 留篇集的一致子集派生, 而非独立留篇。

【文献定位】
本测度处于「金融文本的时间维度分析」这一线索上。Cohen、Malloy 与 Nguyen (2020) 提供了最直接的方法学母题: 相邻两期披露文本相似度是一个可操作、可复现、且与后续经济结果相关的文本特征, 其价值在于「变化 (或不变化) 本身即信号」。本家族把该母题的载体由披露文本换成媒体报道, 因此更贴近「外部感知连贯性」而非「内部披露连贯性」。在计量落地层面, 连贯性得分作为一个 bank-year 层面的连续解释变量, 其分布形态需谨慎处理, 但须先厘清其性质与「计数变量」的本质区别: 本指标是相邻两期 TF-IDF 向量夹角的余弦相似度, 取值严格封闭在 [0, 1] 单位区间内, 是一个有界的连续测度, 而非非负整数意义上的计数或类计数变量。因此对它套用计数数据的建模框架并不贴切 —— 它既没有零膨胀的整数堆积, 也不服从泊松或负二项的生成机制。Cohn、Liu 与 Wardlaw (2022) 系统讨论了金融研究中计数型与类计数型变量因其离散、非负、右偏的生成结构而带来的建模陷阱; 本家族在此处援引该文并非把连贯性得分归入计数变量, 而是取其更一般的方法学教训 —— 一个测度的机械生成方式 (此处是由词频派生的向量余弦) 会先验地塑造其分布支撑与形态, 提醒研究者不可对派生自文本频次的指标不加辨析地套用现成的线性设定。落到本指标, 需要关注的不是计数变量的零膨胀与右偏, 而是有界支撑 (bounded support) 与单位区间内可能存在的偏态: 当大量 bank-year 的相邻期报道高度雷同, 相似度会在接近 1 的上界处堆积, 使分布左偏并触及边界, 此时朴素 OLS 线性设定同样可能失当, 分数型 (fractional) 或有界响应的处理值得作为稳健性对照。在文本表示的工程约束上, 长文档的处理是本家族与整个 strategic_diff 模块共同面对的问题: 当聚合文档很长时, 简单截断会丢失尾部语义, Beltagy、Peters 与 Cohan (2020) 提出的长文档 Transformer 说明了长文本表示需要专门的分段与注意力机制; 本家族在 TF-IDF 词袋通道上不受序列长度上限约束 (词袋对长度不敏感), 但同一模块内的 embedding 通道则采用 token 分段加均值池化来规避超长截断, 二者构成对长文本敏感性的互补稳健性检验。需要强调的是, TF-IDF 词袋通道天然忽略词序与上下文, 只捕捉词汇层面的重叠, 因而它测量的是「用词是否雷同」这一浅层连贯性, 与 embedding 通道测量的「语义是否接近」这一深层连贯性正交, 二者不可互相替代, 亦不得混入同一过度识别检验。

## VAR: coh_tfidf_w_full

【变体差分】
本列是相邻期文本连贯性 jieba 词级通道的 full 轨实现, 也是本家族三轨中与全项目 full-only 留篇门控直接对齐的主轨。full 轨的聚合文档口径为「标题 prepend + 全文正文」: 每篇入选报道先把标题前置拼接到正文之前, 再把该 bank-year 全部报道拼接为一份长文档, 随后走 jieba 词级切分与 TF-IDF 向量化, 最终取该银行 t 年与 t−1 年两份 full 轨向量的余弦相似度。本列相对家族 canonical 描述的差分维度仅在「文本轨 = full」这一个坐标上: 分词粒度固定为 jieba 词级 (区别于同块的字级 coh_tfidf_c_full), 表示方法固定为 TF-IDF 词袋 (区别于 coh_lda_full 的 LDA 主题分布与 coh_emb_full 的稠密嵌入), 相邻期定义固定为连续年度 year_t 与 year_{t−1}。作为 full 轨, 它承担该家族的门控一致职责: 是否有一篇报道进入 t 年或 t−1 年的聚合文档, 由 full 轨留篇判定单点决定, ctx/ss 两轨在此基础上派生。首年与年份间隙返回 NaN。本列与同家族 _ctx、_ss 两列各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验; 需要注意的机械相似风险是: full 轨中一篇共同提及多家银行的报道会逐字进入每家被提银行的年度聚合文档, 使共同被报道的银行在相邻年也可能因共享语料而抬高连贯性, 该风险已由年内同行重复全文去重部分缓解 (见 _aggregate_bank_year_texts 默认去重开关)。

## VAR: coh_tfidf_w_ctx

【变体差分】
本列是相邻期文本连贯性 jieba 词级通道的 ctx 轨实现, 与 full 轨的唯一差分坐标是文本轨由「全文」收窄为「实体上下文窗口」。ctx 轨的聚合文档口径为 content_ctx: 每篇报道只保留标题 prepend 之后、目标银行实体提及位置附近的上下文窗口文本 (窗口半径由配置控制), 而非整篇正文, 随后同样走 jieba 词级切分、TF-IDF 向量化, 取相邻连续年度两份 ctx 向量的余弦相似度。相对 full 轨, ctx 轨的价值在于剥离与目标银行无关的正文段落, 使连贯性得分更聚焦于「围绕该银行的报道措辞」是否年际稳定, 从而弱化 full 轨中那类由共同提及导致的跨银行逐字机械相似 —— 因为 ctx 文本是 bank-specific 的实体窗口, 不同银行在同一篇报道中的窗口切片天然不同, 跨银行逐字共享被结构性削弱。留篇集合仍由 full 轨门控决定, ctx 轨只是在同一留篇篇集上换用实体窗口文本重新聚合, 因而其行宇宙是 full 留篇集的子集派生, 属 conditional-on-full 的稳健性轨而非独立留篇轨。分词粒度、表示方法、相邻期定义与 NaN 处理均与 full 轨一致, 差分只在文本轨。本列与 _full、_ss 各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J; 与 full 轨的对照读法是: 若 full 高而 ctx 低, 提示年际的雷同主要来自银行无关的背景段落 (如宏观、行业通稿) 而非银行本身的叙事, 这一分解正是设置 ctx 轨的识别意义所在。

## VAR: coh_tfidf_w_ss

【变体差分】
本列是相邻期文本连贯性 jieba 词级通道的 ss 轨实现, 文本轨由「实体上下文窗口」进一步收窄为「银行与金融科技同句共现」的最严口径。ss 轨的聚合文档口径为 content_ss: 只保留目标银行与金融科技词在同一句子内 (含标题句, 句窗半径由 filtering.yaml 的 ss_sentence_radius 控制, 默认 ±1 句) 共现的文本片段, 其回退语义严格镜像 ctx 轨 —— 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文 body 且该篇 ss_is_fallback 置 True, 与 ctx 轨的回退机制一一对应, 二者共享 full 门控确定的 n_articles 分母。收窄文本后同样走 jieba 词级切分、TF-IDF 向量化, 取相邻连续年度两份 ss 向量的余弦相似度。相对 full/ctx 两轨, ss 轨把连贯性锁定在「银行×金融科技」这一交叉叙事上, 回答的是「围绕该银行的金融科技相关报道措辞是否年际稳定」这一更窄但更贴近研究主题的问题。留篇集合仍由 full 门控单点决定, ss 轨在该篇集上换用同句共现文本 (或按上述回退) 重新聚合, 属 conditional-on-full 的稳健性轨。分词粒度、表示方法、相邻期连续年度定义、首年与年份间隙 NaN 处理均与 full 轨一致, 差分只在文本轨收窄口径与回退语义。本列与 _full、_ctx 各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验; 在 T 较小的开发样本上, ss 轨因同句共现片段稀疏, 相邻期均可取到有效向量的 bank-year 格点更少, NaN 比例高于 full/ctx 属预期退化, 生产全样本 (T=19) 下方能充分取值。

<!-- rendered-citations:begin -->
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The long-document transformer. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2004.05150
<!-- rendered-citations:end -->
