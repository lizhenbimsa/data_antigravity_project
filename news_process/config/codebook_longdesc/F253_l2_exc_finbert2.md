---
family_id: F253
novelty_exempt_rationale: "exc_ 前缀家族为停刊/退出覆盖媒体稳健性剔除变体, 测度定义 (FinBERT2 正面概率及三轨三加权) 依据母族 finbert2 情感测度与其原始文献, 本身非独立新构念, 无需单独追新文献。"
columns:
- exc_finbert2_正面_ctx
- exc_finbert2_正面_full
- exc_finbert2_正面_hw_ctx
- exc_finbert2_正面_hw_full
- exc_finbert2_正面_hw_ss
- exc_finbert2_正面_ss
- exc_finbert2_正面_w_ctx
- exc_finbert2_正面_w_full
- exc_finbert2_正面_w_ss
unit: 无量纲概率均值 (∈ [0,1]; 加权变体为 权重×概率 的组内均值, 非重归一化概率)
formula: "exc_finbert2_正面{wt}{track} = mean_{i ∈ alive-media(bank,year)} finbert2_正面{wt}{track,i}; finbert2_正面 = FinBERT2 二分类 P(正面); wt ∈ {∅, _w (×mention_density, VW), _hw (×herd_weight, HW)}; alive-media = 剔除疑似退出覆盖媒体 (_is_ceased_media==0) 后的文章子集"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (步骤 6c「媒体信息中介异质性」函数体内嵌 exc_ 停刊稳健性块 C.1-C.4; 逐篇 finbert2 概率来自 stage 23 tone_berts, 加权变体在 encode.py 物化)
upstream:
  - 23_bert_tone.parquet (finbert2_正面_{full,ctx,ss} 及其 _w/_hw 加权文章列)
  - 24_herd_decay.parquet (herd_weight_{full,ctx,ss}, HW 权重源)
  - 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
citations:
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2
  pages_or_artno: 5117-5128
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是「剔除疑似退出覆盖的媒体之后, 由 FinBERT2 判给银行—金融科技报道的正面情感概率」的银行—年度聚合值。列名结构 exc_finbert2_正面_{加权}{轨道} 拆成三段读: exc_ 是停刊稳健性前缀 (excluded-media, 表示样本已剔除疑似退出覆盖的媒体来源); finbert2_正面 是 stage 23 的第三个金融领域 BERT 模型 FinBERT2 对单篇报道给出的「正面」类概率; 尾部的加权与轨道后缀指明该概率在文章层如何加权、以及取自哪一条三轨文本。构念的落点不是「银行这一年被报道得多正面」的主测度本身, 而是「把疑似退出覆盖的媒体从样本里拿掉之后, 这个正面度是否还站得住」的稳健性对照。它服务于识别环节的一个具体威胁: 媒体来源在样本期内消失 (报纸停办、休刊, 或仅仅停止覆盖银行—金科话题) 会引入幸存者偏差, 使情感指标向仍在出版的媒体倾斜, 进而污染以媒体情感为核心解释变量的面板回归与 Bartik 型工具变量。exc_ 族的做法是保守地把疑似退出覆盖媒体整体剔出, 在存活媒体 (alive-media) 子集上重算同一测度, 供 Stata 端做系数稳定性检验。

数据来源链条为: 上游 stage 23 (tone_berts) 用 FinBERT2 对每篇报道的三轨文本 (content_full / content_ctx / content_ss) 分别推断, 按各自 tokenizer 分窗、argmax 分类并以置信度加权池化, 产出文章层的 finbert2_正面{轨道} 概率列; stage 24 (herd_decay) 产出 herd_weight{轨道} 从众衰减权重; encode 层据此物化 finbert2_正面_w{轨道} (提及密度加权, VW) 与 finbert2_正面_hw{轨道} (从众衰减加权, HW) 两组加权文章列。随后 attention_media 模块的停刊检测 detect_defacto_cessation 依据每家媒体在银行—金科子集中的首末出现年份与文章量, 结合 NPPA (国家新闻出版署) 名录交叉验证, 标出 confirmed ∪ suspected 的疑似退出集; 在 _is_ceased_media==0 的存活子集上, 对上述九个文章层概率列按 (target_bank, year) 取组内均值, 得到本家族九列。

【方法学与计算】
计算分三步。第一步, 文章层概率: FinBERT2 是一个二分类金融情感编码器, 只输出「正面 / 负面」两类 (中性列在 encode 层补 NaN, 与三分类模型严格区分), 因此 finbert2_正面 是伯努利意义下的 P(正面), 与 finbert2_负面 互补而非独立第三维。第二步, 文章层加权: 无后缀列为等权原始概率; _w 变体把概率乘以该篇的提及密度 (mention_density) 得到成交量加权 (VW) 分子, 强调被密集提及的报道; _hw 变体把概率乘以从众衰减权重 (herd_weight) 得到从众加权 (HW) 分子, 压低同题重复、相互跟风的冗余报道。第三步, 样本剔除与聚合: 在剔除疑似退出覆盖媒体后的存活子集上, 对每个 (银行, 年份) 单元取上述文章列的算术均值。需注意 exc_ 聚合取的是「加权后概率列」的均值, 而非「加权分子和 ÷ 权重和」的重归一化比率, 故 _w/_hw 变体是 权重×概率 的组内平均, 尺度随权重量纲平移, 水平值不可与无后缀列直接并列比大小, 只可各自标准化后比较系数。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算入银行—金科报道宇宙只看 full 轨的 LLM 判定, ctx/ss 轨为 conditional-on-full 的子集测度; 因此三轨 exc_ 列的行宇宙同源, 差别只在文本窗口。

【文献定位】
方法学上本家族坐落在金融文本情感测量从词典法转向机器学习/深度学习的谱系中。Loughran 与 McDonald (2011) 奠定了金融领域专用词典的必要性, 其 2016 年综述 (Loughran & McDonald, 2016) 系统梳理了文本分析在会计金融中的测量陷阱; Frankel、Jennings 与 Lee (2022) 在顶刊 Management Science 上直接比较了机器学习与词典法在披露情感上的表现, 论证了监督式模型相对词表的增量信息, 为本项目并置 BERT 与词典两族测度提供了方法学依据。FinBERT (Huang, Wang & Yang, 2023) 把 BERT 架构引入金融文本抽取, FinBERT2 (Xu et al., 2025) 进一步做金融领域专用的双向编码器部署优化, 即本家族所用模型。情感与媒体的经济后果一线由 Tetlock (2007) 关于媒体语气对股市的作用确立; 而 exc_ 前缀所针对的幸存者偏差与样本选择问题, 直接呼应 Fang 与 Peress (2009) 对媒体覆盖与截面收益的识别关切——媒体覆盖的进入与退出本身携带信息, 若不加处理会偏误估计。本项目把 FinBERT2 与另两个 BERT 模型 (finbert_cn / fin_sent_zh) 并置为「互为稳健性、不分主次」的三模型轨, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 同理三轨 (full/ctx/ss) 与三加权 (无/VW/HW) 亦为规格稳健性并排, 不得在单一过度识别检验里混用。

## VAR: exc_finbert2_正面_ctx

【变体差分】
本列 = FinBERT2 正面概率, 等权 (无加权后缀), 取自 ctx 轨文本, 在剔除疑似退出覆盖媒体后的存活子集上按银行—年度取均值。相对家族参照列 exc_finbert2_正面_full, 唯一差别是文本轨道: ctx 轨的文章文本为「标题 prepend + 实体上下文窗口」, 即只保留目标银行实体附近的上下文, 而非全文正文。因此本列反映的是「在银行实体近旁的局部语境里, FinBERT2 读到的正面倾向」在存活媒体子集上的平均, 相对 full 轨滤除了与银行无关的段落噪声, 是 full 轨的稳健性对照轨而非独立构念。加权维度为等权, 即每篇报道的正面概率不乘提及密度也不乘从众权重, 直接进入组内算术平均。ctx 轨与 full/ss 两轨遵循 full-only 留篇门控: 行宇宙同为 full 轨判定的银行—金科报道集, ctx 列在该子集上 per-track 计算。本列与同族 _full、_ss 及各加权变体属「互为稳健性、不分主次」的三轨规格并排, 各自 just-identified, 禁混进同一 over-identified Hansen J。ss 轨在无银行∧金科同句共现时回退至全文 body (镜像 ctx 的回退语义), 但 ctx 轨自身以实体窗口为准, 不共享该回退分母。使用上, 本列适合作为 exc_finbert2_正面_full 主轨系数的稳健性对照: 若把样本从全文轨换到实体窗口轨后, 存活媒体子集上的正面度对结果论断无实质改变, 则可佐证结论不由与银行无关的段落噪声驱动。开发期 T=2 小样本上, ctx 轨与 full 轨可能高度相关甚至近乎重合, 这属预期退化, 三轨的真实分离要到生产期 T=19 全量语料才充分显现, 因此对本列在开发数据上的方差不足不应作为构念冗余的证据。

## VAR: exc_finbert2_正面_full

【变体差分】
本列是本家族的参照列: FinBERT2 正面概率, 等权, 取自 full 轨, 在存活媒体子集上按银行—年度取均值。full 轨文本 = 标题 prepend + 全文正文, 是信息最完整、也是 full-only 留篇门控的判定轨——一篇报道是否算入银行—金科报道宇宙只看 full 轨的 LLM 判定, 故 full 轨的行宇宙即为整个留篇集。相对同族其余八列, 本列同时取「等权 + full 轨」两个基线维度, 是解读加权效应 (对照 _w/_hw) 与轨道效应 (对照 _ctx/_ss) 的公共基准。其数值语义为: 把疑似退出覆盖的媒体整体剔出后, 该银行当年被存活媒体报道的全文经 FinBERT2 判为正面的平均概率。由于 FinBERT2 为二分类模型, 该概率与 finbert2_负面_full 互补, 不含中性维度, 与三分类的 finbert_cn/fin_sent_zh 在水平上不可直接比较 (伯努利概率与三类 softmax 概率量纲不同), 只可各自标准化后比系数。本列与 exc_finbert2_正面_ctx/_ss 及三加权变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。作为停刊稳健性口径, 本列应解读为「疑似退出覆盖媒体」保守剔除下的对照, 不可在论文中表述为严格出版停刊口径。典型用法是与不剔除媒体的同构主测度 (finbert2 正面度的 full 轨聚合) 并置, 检验核心系数在剔除退出媒体前后是否稳定; 若两者符号一致、幅度接近, 则可缓解幸存者偏差与样本选择对识别的威胁。需再次强调 exc_ 剔除集是 confirmed ∪ suspected 的并集, 未经 NPPA 证实的 suspected 亦整体进入排除集, 故本列偏保守, 倾向于剔多而非剔少, 这一取向在披露样本选择稳健性时应如实说明。

## VAR: exc_finbert2_正面_hw_ctx

【变体差分】
本列 = FinBERT2 正面概率的从众衰减加权 (HW) 变体, ctx 轨, 存活媒体子集组内均值。相对 exc_finbert2_正面_ctx, 差别在加权: 文章层概率先乘以 stage 24 herd_decay 产出的 herd_weight_ctx 从众衰减权重, 再取组内均值。herd_weight 依据同题材、时间邻近报道的 TF-IDF 相似度构造, 相似冗余越高权重越低, 目的是压低相互跟风、批量转载的从众报道对情感聚合的支配, 使测度更贴近独立信息。相对 full 轨的 HW 变体 (exc_finbert2_正面_hw_full), 本列在 ctx 轨上计算, 权重亦取 ctx 轨自身的 herd_weight_ctx (非借 full 轨权重), 属逐轨严格加权。需强调本列是 权重×概率 的组内均值 (exc_ 聚合取列均值而非分子和÷权重和), 故其水平值受 herd_weight 量纲平移, 不可与等权 _ctx 列直接比大小, 只可各自标准化后比较回归系数。本列与等权轨 (_ctx)、提及密度加权轨 (_w_ctx) 及其余轨道/加权组合属规格稳健性并排, 三加权 (无/VW/HW) × 三轨 (full/ctx/ss) 各自 just-identified, 禁混进同一 over-identified Hansen J。full-only 留篇门控下, ctx 为 conditional-on-full 子集轨。用途上, 本列适合与等权 ctx 列 (exc_finbert2_正面_ctx) 对照, 检验对同题冗余稿件降权是否改变实体窗口语境下存活媒体子集的正面度估计; 若 HW 加权后系数方向不变, 说明结论不由批量转载、跟风报道的舆论潮支配。在 T=2 开发数据上 herd_weight 的区分度有限、加权列可能与等权列近乎共线, 属预期退化, 生产期 T=19 语料密度更高时从众衰减方能有效识别冗余稿件。

## VAR: exc_finbert2_正面_hw_full

【变体差分】
本列 = FinBERT2 正面概率的从众衰减加权 (HW) 变体, full 轨, 存活媒体子集组内均值。相对家族参照列 exc_finbert2_正面_full, 差别只在加权维度: 文章层概率乘以 herd_weight_full 后再聚合。从众衰减加权的动机是: 银行相关新闻常出现大量同源转载与跟风报道, 若等权聚合会让高度重复的稿件反复计入、放大一时的舆论潮; herd_weight 依据相邻期同题文本的 TF-IDF 相似度对冗余稿件降权, 从而更接近「独立信息量」加权下的正面度。本列在三个加权基线中对应 HW, 与 VW (提及密度加权, _w_full) 各自刻画不同的加权哲学: VW 强调「被提得多」的报道, HW 强调「独立、非跟风」的报道, 两者不是同一构念的替代而是并列的稳健性视角。本列取 full 轨, 权重取 full 轨的 herd_weight_full, 逐轨严格。数值为 权重×概率 的组内均值 (非重归一化), 水平不可与等权列直接比较, 只可标准化后比系数。本列与 exc_finbert2_正面_full (等权)、exc_finbert2_正面_w_full (VW) 互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。作为 exc_ 族成员, 解读须限于疑似退出覆盖媒体的保守剔除口径。在实证叙事中, 本列与 exc_finbert2_正面_full、exc_finbert2_正面_w_full 三者构成「等权—提及强度加权—从众衰减加权」的加权稳健性梯子: 若核心系数在三种加权下均保持一致, 则可论证结论既不被顺带一提的边缘报道稀释、也不被批量跟风稿件放大, 加权选择本身不驱动结论, 这正是把三加权并列而非择一报告的意义所在。

## VAR: exc_finbert2_正面_hw_ss

【变体差分】
本列 = FinBERT2 正面概率的从众衰减加权 (HW) 变体, ss 轨, 存活媒体子集组内均值。相对 exc_finbert2_正面_hw_full, 差别在轨道: ss 轨文本 = 标题 prepend + 「银行∧金融科技同句共现 ±N 窗」句子拼接 (窗口半径由 config filtering.yaml 的 ss_sentence_radius 控制, 默认 1)。ss 轨是三轨中语境最窄、共现约束最强的一轨, 只保留银行与金科词在同一句附近同现的文本, 因此本列刻画的是「在银行与金融科技被同句谈及的最紧语境里, 经从众衰减降权后, 存活媒体所呈现的正面度」。加权维度为 HW, 权重取 ss 轨自身的 herd_weight_ss。ss 轨的关键语义是回退: 当某篇报道没有银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback=True (镜像 ctx 的回退语义, 共享 n_articles 分母); 在开发期 T=2 小样本上 ss 轨可能大面积回退乃至零方差, 属预期退化, 生产期 T=19 全量语料下方显真三轨差异。本列为 权重×概率 的组内均值, 水平不可与等权 _ss 或其他轨直接比大小, 只可标准化后比系数。与同族各轨/各加权互为稳健性、不分主次, 各自 just-identified, 禁混同一 over-identified Hansen J。作为三轨中语境最窄的一轨叠加从众衰减加权, 本列是识别设计中约束最强的对照之一: 若结论在「银行—金科同句 + 剔除冗余稿件 + 剔除退出媒体」的三重收窄下仍稳定, 则对构念效度是有力佐证。反之, 由于 ss 轨在开发期回退率高, 本列在 T=2 上大量取自回退全文, 与 hw_full 近乎重合亦属预期, 不应据此判定 ss 轨无独立信息。

## VAR: exc_finbert2_正面_ss

【变体差分】
本列 = FinBERT2 正面概率, 等权 (无加权), ss 轨, 存活媒体子集组内均值。相对家族参照列 exc_finbert2_正面_full, 差别在文本轨道: 取 ss 轨即银行∧金科同句共现窗口文本, 是三轨中共现约束最强的窄语境轨。相对 exc_finbert2_正面_ctx (实体窗口), ss 轨进一步要求银行与金融科技在同句附近同现, 语境更聚焦于「银行做金科」这一议题本身, 滤除仅泛提银行或仅泛提金科的段落。加权维度为等权, 每篇概率直接进入组内均值不乘任何权重。ss 轨遵循回退语义: 无同句共现时 content_ss 回退全文 body、ss_is_fallback=True, 与 ctx 回退镜像并共享 n_articles 分母; 若 FINTECH_AC=None 则 *_is_fallback 全 True 优雅降级。full-only 门控下, ss 为 conditional-on-full 的子集轨, 行宇宙同源于 full 轨留篇集。数值语义: 剔除疑似退出覆盖媒体后, 在银行—金科同句语境里 FinBERT2 判正面的平均概率。本列作为二分类概率与三分类 BERT 不可直接比水平。本列与 exc_finbert2_正面_full/_ctx 及三加权变体属三轨/三加权规格稳健性并排, 各自 just-identified, 禁混同一 over-identified Hansen J。用途上本列刻画最聚焦「银行做金科」议题的正面度对照, 适合检验主结论是否由该议题本身的报道驱动而非泛泛的银行新闻; 在生产期 T=19 语料下, ss 轨与 full/ctx 轨的分离最能揭示情感信号究竟锚定于哪一层文本语境, 从而为构念的语境敏感性提供证据。

## VAR: exc_finbert2_正面_w_ctx

【变体差分】
本列 = FinBERT2 正面概率的提及密度加权 (VW, volume-weighted) 变体, ctx 轨, 存活媒体子集组内均值。相对 exc_finbert2_正面_ctx, 差别在加权: 文章层概率先乘以提及密度 (mention_density) 得到 VW 分子, 再取组内均值。提及密度衡量目标银行在报道中被提及的强度, VW 加权因此把「被密集提及」的报道抬高权重, 强调那些真正聚焦于该银行的稿件, 弱化只是顺带一提的边缘报道。相对 full 轨的 VW 变体 (exc_finbert2_正面_w_full), 本列在 ctx 轨上计算。VW 与 HW 是两种正交的加权哲学: VW 关注「提得多」, HW 关注「不跟风」, 两者并列而非替代。本列为 权重×概率 的组内均值 (exc_ 取列均值而非分子和÷提及密度和), 故水平受提及密度量纲平移, 不可与等权 _ctx 或 HW 变体直接比大小, 只可各自标准化后比系数。full-only 门控下, ctx 为 conditional-on-full 子集轨。本列与等权轨、HW 轨及其余轨道组合属三加权×三轨规格稳健性并排, 各自 just-identified, 禁混进同一 over-identified Hansen J。作为 exc_ 族成员, 数值应限于疑似退出覆盖媒体保守剔除口径解读。使用上本列适合与等权 ctx 列 (exc_finbert2_正面_ctx) 对照, 检验按提及强度加权是否改变实体窗口语境下存活媒体子集的正面度; 若 VW 加权后系数方向不变, 说明结论不由仅顺带提及银行的边缘稿件稀释。在 T=2 开发数据上提及密度的区分度有限, 加权列可能与等权列近乎共线, 属预期退化, 生产期 T=19 语料方能有效区分聚焦度不同的报道。

## VAR: exc_finbert2_正面_w_full

【变体差分】
本列 = FinBERT2 正面概率的提及密度加权 (VW) 变体, full 轨, 存活媒体子集组内均值。相对家族参照列 exc_finbert2_正面_full, 差别只在加权维度: 文章层概率乘以提及密度后再聚合。VW 加权的动机是: 一篇长篇深度报道若反复聚焦某银行, 其情感信号应比一篇仅顺带提及该银行的稿件更有分量; 提及密度正是对这种「聚焦强度」的度量。本列在三个加权基线中对应 VW, 取 full 轨完整文本, 权重取 full 轨提及密度, 逐轨严格。与从众衰减加权 (HW, exc_finbert2_正面_hw_full) 相比, VW 不惩罚跟风冗余而奖励高提及强度, 二者刻画的加权取向不同, 属并列的稳健性视角而非同一构念的替代。数值为 权重×概率 的组内均值, 非重归一化比率, 水平随提及密度量纲平移, 不可与等权 _full 或 HW 变体直接比大小, 只可标准化后比较回归系数。本列与 exc_finbert2_正面_full (等权)、exc_finbert2_正面_hw_full (HW) 互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。FinBERT2 二分类概率与三分类 BERT 不可直接比水平。在实证叙事中, 本列与等权 full 列、HW full 列共同构成加权稳健性梯子: 三种加权若给出一致的核心系数, 即可论证加权取向 (等权 / 提及强度 / 独立信息) 不驱动结论。需注意提及密度加权在 exc_ 聚合下取的是 提及密度×概率 的列均值而非成交量加权平均比率, 故本列水平与等权列不在同一尺度, 报告时应各自标准化, 避免读者误将两列水平差解读为加权效应本身。

## VAR: exc_finbert2_正面_w_ss

【变体差分】
本列 = FinBERT2 正面概率的提及密度加权 (VW) 变体, ss 轨, 存活媒体子集组内均值。相对 exc_finbert2_正面_w_full, 差别在轨道: 取 ss 轨即银行∧金融科技同句共现窗口文本 (标题 prepend + 同句 ±N 窗句子拼接), 语境最窄、共现约束最强。相对同轨等权列 exc_finbert2_正面_ss, 差别在加权: 概率乘以 ss 轨提及密度后聚合, 抬高对该银行提及强度高的稿件。本列因此刻画「在银行—金科最紧同句语境里、按提及强度加权后, 存活媒体所呈现的正面度」。ss 轨遵循回退语义: 无银行∧金科同句共现时 content_ss 回退全文 body、ss_is_fallback=True (镜像 ctx 回退, 共享 n_articles 分母); 开发期 T=2 上 ss 轨可能大面积回退、方差退化, 生产期 T=19 方显真三轨分离, 属预期。数值为 权重×概率 的组内均值, 水平受提及密度量纲平移, 不可与等权 _ss 或 HW 变体直接比大小, 只可各自标准化后比系数。本列与同族各轨/各加权 (等权、HW, 及 full/ctx 轨) 属三加权×三轨规格稳健性并排, 各自 just-identified, 禁混同一 over-identified Hansen J。作为 exc_ 族, 解读限于疑似退出覆盖媒体保守剔除口径, 不可表述为严格出版停刊。本列是三轨 × 三加权组合中约束最强的 VW 成员 (最窄语境 + 提及强度加权 + 剔除退出媒体), 适合作为主结论的极端稳健性对照: 若正面度系数在如此收窄的规格下仍稳定, 则对构念与识别都是有力佐证; 而其在 T=2 开发期因回退率高而与 w_full 近乎重合, 属预期退化, 真三轨分离须待生产期 T=19 语料。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2, 5117-5128. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
