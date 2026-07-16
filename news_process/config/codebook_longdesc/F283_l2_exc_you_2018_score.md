---
family_id: F283
columns:
- exc_you_2018_score_ctx
- exc_you_2018_score_full
- exc_you_2018_score_hw_ctx
- exc_you_2018_score_hw_full
- exc_you_2018_score_hw_ss
- exc_you_2018_score_ss
- exc_you_2018_score_w_ctx
- exc_you_2018_score_w_full
- exc_you_2018_score_w_ss
unit: 情感倾向得分 (无量纲; bank-year 层对文章级 you_2018 词典得分取均值)
formula: "exc_you_2018_score{track} = mean_{i∈alive(b,y,track)} you_2018_score_i{track}; alive = 剔除疑似停刊媒体 (_is_ceased_media==0) 后的存活媒体文章子集; _hw 变体源列先乘羊群衰减权重 herd_weight{track}, _w 变体源列先乘提及密度 mention_density"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性块, exc_ 前缀 bank-year 聚合; 加权源列在 news_process/pipeline/panel/runner.py 步骤 3b/3d 预计算)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (you_2018_score{track} 文章级词典得分)
- 24_herd_decay_processor.parquet (herd_weight{track}; 供 _hw 变体)
- （无独立落盘文件；attention_media.py 的 compute_attention_treatments/detect_defacto_cessation 以内存中构建中的 panel DataFrame 为参数, 由 40_panel_export_main 编排流程在写出 40_panel_yearly.parquet 之前的子步骤内调用, 本家族列即该编排过程的产出而非对已落盘 40_panel_yearly.parquet 的消费）
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
- doi: "10.1111/1475-679x.12560"
  title: "News Bias in Financial Journalists' Social Networks"
  authors: "Xu, G."
  year: 2024
  venue: "Journal of Accounting Research"
  type: "journal"
- doi: "10.1111/jfir.70039"
  title: "Social media sentiment, investor herding and informational efficiency"
  authors: "Yang, N., Fernandez-Perez, A., & Indriawan, I."
  year: 2026
  venue: "Journal of Financial Research"
  type: "journal"
new_dois:
  - "10.1111/1475-679x.12560"
  - "10.1111/jfir.70039"
---

## CORE

【构念与来源】
本家族度量的是"剔除疑似停刊媒体后、以 you_2018 情感词典打分得到的银行-年度新闻情感倾向"。列名前缀 exc_ 是"exclude 疑似停刊媒体"的缩写: 在把文章级情感聚合成银行-年度面板值之前, 先把被判定为疑似退出报道该话题 (覆盖退出, topic-coverage exit) 的媒体来源整体剔出样本, 再对剩余存活媒体的文章取均值。词典部分 you_2018 指以 You、Zhang 与 Zhang (2018) 为学术锚点的中文财经情感词表: 该文研究媒体报道 (笔杆子的力量) 如何被市场化与非市场化媒体分别捕获, 为中文财经文本的正负面词汇打分提供了被广泛引用的构念依据。本家族即以该词表对每篇银行金科报道计正负面词命中, 归一化为文章级情感分, 再在存活媒体子集上聚合。

【方法学与计算】
计算分三层。第一层是文章级词典打分: 在 stage 22 (tone_words) 上, 对每篇报道用 you_2018 词表统计正负面词命中并归一化, 得到 you_2018_score{track} (取值区间随归一化落在正负之间, 正值偏正面、负值偏负面)。第二层是加权变体的预乘: 在 runner 步骤 3b 用提及密度 mention_density 作价值加权 (value-weighted exposure) 得到 _w 源列, 在步骤 3d 用 stage 24 的羊群衰减权重 herd_weight{track} 作注意力加权得到 _hw 源列; 无后缀的 score 变体则不预乘、保留等权文章。第三层是停刊稳健性聚合: attention_media 先经 detect_defacto_cessation 识别在样本期内疑似停止覆盖的媒体 (排除集 = confirmed 与 suspected 并集, 未经 NPPA 证实的 suspected 一律保守纳入排除集), 标记 _is_ceased_media, 再在存活子集 (_is_ceased_media==0) 上按 target_bank、year 分组对相应源列取均值, 输出 exc_ 前缀的三种权重 × 三轨共九列。须强调该口径是"话题覆盖退出"的保守代理而非经证实的报纸停刊, 论文表述应称稳健性口径 (survivorship / 幸存者偏差检验), 不可等同严格出版停刊。留篇门控沿用 full-only 口径 (2026-06-29): 一篇是否算"银行金科报道"只看 full 轨 llm_verified 判定, ctx/ss 为 conditional-on-full 的稳健轨, 行宇宙是 full 留篇集的子集。三轨含义: full 为标题加全文正文, ctx 为标题加实体窗口, ss 为标题加银行与金科同句共现窗; ss 回退语义镜像 ctx, 无同句共现时回退全文。

【文献定位】
情感词典法在财经文本上的效度是本族方法学的支点: van Atteveldt、van der Velden 与 Boukes (2021) 系统比较人工标注、众包、词典与机器学习, 论证词典法在成本与可解释性上的位置; Barbaglia 等 (2025) 与 Ma 等 (2025) 分别给出经济文本与中文投资者细粒度词典的近期构造范式, 支撑以词表打分聚合的做法。Frankel、Jennings 与 Lee (2022) 比较词典法与机器学习情感, 为"多方法互为稳健性、不分主次"提供先例。You、Zhang 与 Zhang (2018) 是 you_2018 词表的构念母锚, Hwang 与 Kim (2017) 则从写作质量与市场反应角度补足"笔杆子"文本信号的经济后果证据。停刊稳健性的动机在于媒体来源消失会引入幸存者偏差, 使情感指标向存活媒体倾斜并污染基于媒体暴露的工具变量, 故以剔除疑似退出媒体的子集重算作为系数稳定性检验。三轨 (full/ctx/ss) 与三种权重 (等权/羊群加权/提及密度加权) 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 本族与规则消融梯度、政治词权重梯度正交, 不交叉。发现与公司管理层有社交网络联系的财经记者在报道中会引入系统性媒体偏向, 为本家族剔除疑似退出媒体的停刊稳健性口径提供媒体来源异质性的文献支点, 引自 Xu (2024, Journal of Accounting Research)。证明情感驱动的投资者羊群行为会降低市场信息效率, 为本家族 _hw 羊群衰减加权变体的构念动机 (校正报道潮聚集期彼此高度相似文章的机械放大) 提供近期实证依据, 引自 Yang、Fernandez-Perez 与 Indriawan (2026, Journal of Financial Research)。

## VAR: exc_you_2018_score_ctx

【变体差分】
本列为等权、实体窗 (ctx) 轨的停刊稳健性情感均值。源列 you_2018_score_ctx 在标题加实体窗口文本上打分: ctx 只取目标银行实体附近的上下文窗口而非全文, 相对 full 轨聚焦银行相关语境、压低无关段落噪声, 也相对 ss 轨保留更宽的上下文 (不要求银行与金科严格同句)。等权指聚合时不乘任何权重, 每篇存活媒体文章权重相同, 与 _hw (羊群衰减加权) 、_w (提及密度价值加权) 构成同族的三种加权稳健性臂; 三者度量的都是"存活媒体子集上的 ctx 轨情感", 差别仅在权重来源, 互为稳健性、不分主次。停刊维度上, 本列已在聚合前剔除疑似退出媒体 (_is_ceased_media==0 子集): attention_media 用 detect_defacto_cessation 判定某媒体来源在样本期内是否疑似停止覆盖该话题, confirmed 与 suspected 一律并入排除集 (保守处理, 未经 NPPA 证实的 suspected 也不予保留), 再对存活媒体子集按 target_bank、year 分组求 ctx 轨情感均值。与不带 exc_ 前缀的全样本 you_2018_score_ctx 情感列对照, 若二者系数方向与显著性接近, 可视为该结论不受媒体幸存者偏差驱动。ctx 轨在留篇门控上是 conditional-on-full 的稳健轨: 一篇报道是否计入行宇宙, 由 full 轨 llm_verified 判定, ctx 只在该子集内重算测度, 不独立扩样本; ss 回退语义 (缺同句共现回退全文) 与本轨无关。本列与 full/ss 两轨、与同轨 _hw/_w 两加权变体各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_full

【变体差分】
本列为等权、全文 (full) 轨的停刊稳健性情感均值, 是本家族三轨中的规范 (canonical) 参照臂。源列 you_2018_score_full 在标题 prepend 加全文正文上以 you_2018 词典打分, 覆盖整篇报道从标题到正文尾段的全部正负面词命中, 相对 ctx (仅实体窗口) 与 ss (仅同句共现窗) 保留最完整语境, 因此代价是也纳入了与银行金科关联较弱段落的噪声, 这是三轨互为稳健性设计要检验的具体张力。等权聚合不乘羊群衰减或提及密度权重, 每篇存活媒体文章等权计入均值; 与 _hw (羊群加权)、_w (提及密度加权) 两种加权臂互为稳健性、不分主次, 三者共享同一 full 文本轨、仅权重来源不同。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出的保守代理) 媒体, 只对存活子集按 target_bank、year 分组取均值, 用于对照全样本 you_2018_score_full 情感列检验媒体幸存者偏差是否驱动结论: 若剔除疑似停刊媒体后系数方向与幅度不发生实质性反转, 则原结论对媒体样本流失具有稳健性。留篇门控采用 full-only 口径 (2026-06-29), 本轨即门控判定所依据的主轨——一篇报道是否算"银行金科报道"只看 full 轨 llm_verified 结果, ctx/ss 是该行宇宙内的 conditional-on-full 稳健轨。本列与 ctx/ss 两轨、与 _hw/_w 两加权臂各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_hw_ctx

【变体差分】
本列为羊群衰减加权 (_hw) 、实体窗 (ctx) 轨的停刊稳健性情感均值。与等权 ctx 列的差别在于源列 you_2018_score_hw_ctx 在文章级已由等权 you_2018_score_ctx 乘以 stage 24 (herd_decay_processor) 输出的羊群衰减权重 herd_weight_ctx: 该权重刻画注意力羊群随报道时间聚集程度衰减的强度, 使处于报道潮密集聚集期、彼此高度相似的文章在聚合时相对被降权, 而相对孤立、信息增量更大的文章相对被升权, 度量的是"注意力羊群调整后"的情感暴露而非简单等权情感。文本轨仍为 ctx, 只取标题加银行实体窗口上下文, 未纳入全文或同句约束。停刊维度上, 本列同样先剔除疑似退出 (话题覆盖退出代理) 媒体, 只对 _is_ceased_media==0 的存活子集按银行-年度分组取均值, 与不带 exc_ 前缀的全样本 you_2018_score_hw_ctx 情感列互为幸存者偏差稳健性对照。羊群加权臂与等权臂、提及密度加权 (_w) 臂构成同一 ctx 轨下的三种加权稳健性口径, 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。ctx 轨在留篇门控上是 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集。本列与其 full/ss 两个同权重孪生列构成三轨并排、与同轨不同权重列均为互为稳健性关系, 不设主次。

## VAR: exc_you_2018_score_hw_full

【变体差分】
本列为羊群衰减加权 (_hw) 、全文 (full) 轨的停刊稳健性情感均值。源列 you_2018_score_hw_full 在文章级由等权 you_2018_score_full 乘以 stage 24 (herd_decay_processor) 输出的羊群衰减权重 herd_weight_full 得到, 反映注意力羊群衰减调整后的情感暴露: 度量意图是让某一时点集中爆发、彼此相似度极高的报道潮不至于像分散、独立报道那样等权地贡献情感信号, 从而部分校正"媒体扎堆报道"对面板情感均值的机械放大。文本轨为 full, 覆盖标题加全文正文, 是三轨中语境最完整者, 也是留篇门控 full-only 口径 (2026-06-29) 所依据的主轨——一篇报道是否计入行宇宙由 full 轨 llm_verified 判定。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出代理) 媒体, 仅对 _is_ceased_media==0 的存活媒体子集按 target_bank、year 分组取均值, 与不带 exc_ 前缀的全样本 you_2018_score_hw_full 羊群加权情感列互为幸存者偏差稳健性对照: 若剔除疑似停刊媒体后结论方向不变, 说明羊群加权口径下的结果同样不受媒体样本流失驱动。本列与等权 full 列、提及密度加权 full 列 (_w) 构成同一 full 轨下的三种加权臂, 与 ctx/ss 两个同权重列构成三轨, 全部各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用时应把本列理解为"注意力羊群调整后的 full 轨情感均值", 与等权、提及密度加权两臂在同一回归表内并排报告, 而非彼此替代或加权合并为单一列。

## VAR: exc_you_2018_score_hw_ss

【变体差分】
本列为羊群衰减加权 (_hw) 、同句共现 (ss) 轨的停刊稳健性情感均值。文本轨 ss 在三轨中约束最严: 只取标题加银行与金科在同一句子共现窗口 (半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 的文本, 聚焦银行金科强关联语境, 排除仅在同一篇文章内出现但语境上并不直接相关的段落, 因此对"银行与金融科技具体互动"这一构念的测度纯度高于 ctx、更高于 full, 代价是可用样本量最小。源列 you_2018_score_hw_ss 在文章级由等权 you_2018_score_ss 乘以 stage 24 羊群衰减权重 herd_weight_ss 得到 (若该权重列缺失, 则优雅回退使用 full 轨权重, 不产生孤儿), 度量的是同句共现语境下经注意力羊群调整的情感暴露。ss 回退语义严格镜像 ctx: 当一篇文章内不存在银行与金科的同句共现时, content_ss 整体回退为全文正文, ss_is_fallback 置真, 并与其他轨共享同一 n_articles 分母, 不因回退而产生单边孤儿或分母不一致。停刊维度上, 本列在聚合前同样剔除疑似退出媒体, 仅对存活子集取均值。ss 轨在留篇门控上是 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集; dev T=2 (本机 110 家银行 × 2 年) 上 ss 轨因样本稀薄常出现零方差或缺格退化, 属预期, 生产 T=19 语料上样本量充足后应恢复正常方差。本列与 full/ctx 两个同权重孪生列、与同轨等权及提及密度加权列各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_ss

【变体差分】
本列为等权、同句共现 (ss) 轨的停刊稳健性情感均值。源列 you_2018_score_ss 在标题加银行与金科同句共现窗文本 (窗口半径由 ss_sentence_radius 控制, 默认 1) 上以 you_2018 词典打分, 是三轨中语境最窄、银行与金融科技关联最强的度量: 只统计明确在同一句子内谈及银行与金科交互的段落, 排除文章其余部分的正负面词干扰, 因此对"该银行与金融科技具体互动的情感倾向"这一构念的测度更纯粹, 但可用样本较 full/ctx 更少。等权聚合不乘羊群衰减或提及密度权重, 每篇存活媒体文章等权计入均值; 与 _hw (羊群加权)、_w (提及密度加权) 两加权臂构成同一 ss 轨下的三种加权稳健性口径, 三者仅权重来源不同, 互为稳健性不分主次。ss 回退语义严格镜像 ctx: 当文章内不存在银行与金科同句共现时, content_ss 整体回退为全文正文, ss_is_fallback 置真, 与其余轨共享同一 n_articles 分母, 保证优雅降级不产生单边孤儿。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出代理) 媒体, 仅对 _is_ceased_media==0 的存活子集按银行-年度取均值, 与不带 exc_ 前缀的全样本 ss 情感列互为幸存者偏差稳健性对照。ss 轨为 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集, dev T=2 上样本稀薄易出现零方差或缺格退化属预期, 生产 T=19 语料上应恢复正常。本列与 full/ctx 两轨、与同轨 _hw/_w 加权臂各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_w_ctx

【变体差分】
本列为提及密度价值加权 (_w) 、实体窗 (ctx) 轨的停刊稳健性情感均值。与等权 ctx 列的差别在于源列 you_2018_score_w_ctx 在文章级已由等权 you_2018_score_ctx 乘以提及密度 mention_density: 该权重按目标银行在文中被提及的密度构造价值加权暴露 (value-weighted exposure), 使某篇报道内目标银行被反复、密集提及时对应的情感相对贡献更大权重, 而仅被顺带一提的报道贡献更小权重, 度量的是"以关注强度加权"的情感而非简单等权情感。文本轨仍为 ctx, 取标题加银行实体窗口上下文, 不涉及全文或同句约束。停刊维度上, 本列同样在聚合前剔除疑似退出 (话题覆盖退出代理) 媒体, 仅对 _is_ceased_media==0 的存活子集按银行-年度取均值, 与不带 exc_ 前缀的全样本 you_2018_score_w_ctx 情感列互为幸存者偏差稳健性对照。提及密度加权臂与等权臂、羊群加权 (_hw) 臂构成同一 ctx 轨下的三种加权稳健性口径, 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。ctx 轨在留篇门控上是 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集。本列与其 full/ss 两个同权重孪生列构成三轨并排、与同轨不同权重列均为互为稳健性关系。分析时若发现 ctx 轨系数与 full 轨明显背离, 应优先怀疑实体窗口截断是否切掉了关键语境, 而非直接判定某一轨"更正确"。

## VAR: exc_you_2018_score_w_full

【变体差分】
本列为提及密度价值加权 (_w) 、全文 (full) 轨的停刊稳健性情感均值。源列 you_2018_score_w_full 在文章级由等权 you_2018_score_full 乘以提及密度 mention_density 得到, 反映价值加权暴露: 度量意图是让高频提及目标银行的报道相对分散一带而过、只顺带提及一次的报道贡献更大情感信号, 从而更贴近"该报道究竟在多大程度上聚焦于该银行"的经济含义。文本轨为 full, 覆盖标题加全文正文, 语境最完整, 亦为留篇门控 full-only 口径 (2026-06-29) 所依据的主轨——一篇报道是否计入行宇宙由 full 轨 llm_verified 判定, 与本列的加权方式无关。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出代理) 媒体, 仅对 _is_ceased_media==0 的存活媒体子集按 target_bank、year 分组取均值, 与不带 exc_ 前缀的全样本提及密度加权情感列互为幸存者偏差稳健性对照, 用以排除结论是被少数疑似停刊媒体的极端提及密度所驱动的可能。本列与等权 full 列、羊群加权 full 列 (_hw) 构成同一 full 轨下的三种加权臂, 与 ctx/ss 两个同权重列构成三轨, 全部各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列适合用作"报道聚焦度加权"的稳健性检验, 与羊群加权臂 (处理报道时间聚集) 分属不同的度量动机, 二者不应被简单相加或平均为单一合成权重。

## VAR: exc_you_2018_score_w_ss

【变体差分】
本列为提及密度价值加权 (_w) 、同句共现 (ss) 轨的停刊稳健性情感均值。文本轨 ss 在三轨中约束最严: 只取标题加银行与金科在同一句子共现窗口 (半径由 ss_sentence_radius 控制, 默认 1) 的文本, 聚焦银行金科强关联语境, 因此本列同时叠加了"语境最窄"与"以提及密度加权"两重收紧, 是本家族九列中构念最集中于"银行金科具体互动强度"的一列。源列 you_2018_score_w_ss 在文章级已由等权 you_2018_score_ss 乘以提及密度 mention_density 得到, 度量的是价值加权暴露而非等权情感, 使密集提及目标银行的同句共现片段相对贡献更大权重。ss 回退语义严格镜像 ctx: 当文章内不存在银行与金科同句共现时, content_ss 整体回退为全文正文, ss_is_fallback 置真, 与其余轨共享同一 n_articles 分母, 不因回退产生单边孤儿。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出代理) 媒体, 仅对存活子集取均值, 与不带 exc_ 前缀的全样本提及密度加权 ss 情感列互为幸存者偏差稳健性对照。ss 轨为 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集, dev T=2 上因样本稀薄易出现零方差或缺格退化, 属预期, 生产 T=19 语料上应恢复正常方差。本列与 full/ctx 两个同权重孪生列、与同轨等权及羊群加权列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Xu, G. (2024). News Bias in Financial Journalists' Social Networks. Journal of Accounting Research. https://doi.org/10.1111/1475-679x.12560
Yang, N., Fernandez-Perez, A., & Indriawan, I. (2026). Social media sentiment, investor herding and informational efficiency. Journal of Financial Research. https://doi.org/10.1111/jfir.70039
<!-- rendered-citations:end -->
