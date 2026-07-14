---
family_id: F202
columns:
- disag_finbert2_ctx
- disag_finbert2_full
- disag_finbert2_ss
unit: 无量纲离散度指数, 取值区间 [0, 1]
formula: "disag_finbert2 = sqrt(1 - ((P - N) / (P + N))^2); P = finbert2 逐篇正类概率在该单元的均值 (finbert2_pos), N = finbert2 逐篇负类概率在该单元的均值 (finbert2_neg); 逐轨 (full/ctx/ss) 各自用同轨概率均值, P + N = 0 时置 NaN"
producer: pipeline\panel\runner.py (step 8b disag, 单 BERT 概率均值输入 finbert2_pos/finbert2_neg); 上游 finbert2_pos/finbert2_neg 由 pipeline\panel\encode.py 对 stage 23 逐篇正/负类概率取 mean 聚合 (非 argmax 计数)
upstream:
- 23_tone_berts.parquet (finbert2 逐篇正/负类概率)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 24_herd_decay.parquet (df_exploded, article×bank 级 verified 集)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1145/3711896.3737219
  type: wp
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
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: "10.1016/j.jfineco.2024.103816"
  type: journal
  authors: "Goldman, E., Gupta, N., & Israelsen, R. D."
  year: 2024
  title: "Political polarization in financial news"
  venue: "Journal of Financial Economics"
new_dois:
  - "10.1016/j.jfineco.2024.103816"
---

## CORE

【构念与来源】
本家族刻画的是某家银行在某一年内, 媒体报道情感在正负两极之间的分歧程度 (disagreement), 由第三家 BERT 情感模型 finbert2 的逐篇分类结果聚合而成。构念动机来自金融学关于意见分歧的长期讨论: 当一家主体被市场解读为好坏参半、多空并存时, 关于它的信息呈现出高度分歧, 而这种分歧本身携带定价与行为含义。Hong 与 Stein (2007) 在其分歧综述中系统论证了异质信念如何进入资产价格; Carlin、Longstaff 与 Matoba (2014) 用债券市场数据实证了分歧水平与价格、成交与波动的关联; Cen、Wei 与 Yang (2017) 进一步刻画了分歧如何引致反应不足与后续可预测的收益。与"平均情绪高不高"是两个正交的问题: 一家银行的报道可以整体偏正面但内部高度撕裂, 也可以整体温和且众口一词。本家族测度捕捉的正是后一维度——报道口径的内部离散度, 而非其位置 (均值)。

【方法学与计算】
计算入口在 pipeline\panel\runner.py 的步骤 8b (disag 段, 单 BERT 概率均值支路)。这里须先厘清一个关键口径, 以免与"逐篇分类计数"混淆: finbert2 的 disag 输入不是 argmax 判正、判负的篇数, 而是逐篇正类概率、负类概率各自在该单元上的均值。具体地, stage 23 对每篇报道给出 finbert2 的正类概率与负类概率, encode 层 (pipeline\panel\encode.py) 把它们各自按 mean 聚合到银行-年-轨道单元, 得到两个平均概率 P (finbert2_pos, 该单元正类概率均值) 与 N (finbert2_neg, 该单元负类概率均值)。本仓库刻意不用 argmax 判正篇数一类的计数量作分歧输入: 以语调 argmax 为条件挑篇会引入以情感为条件的内生样本选择, encode 层对此有明令禁用。取到 P 与 N 后代入离散度闭式: disag = 根号下 (1 减去 ((P 减 N) 除以 (P 加 N)) 的平方)。该式是一个规范到 [0, 1] 的极化指标: 当平均概率完全一边倒 (P 或 N 之一趋近于零) 时, 括号内比值趋近正负一, 平方趋近一, 整体趋近零, 表示零分歧; 当平均正、负概率恰好持平 (P 等于 N) 时, 比值为零, 整体取一, 表示最大分歧。分母 P 加 N 为零 (该单元无任何 finbert2 概率可聚合) 时置 NaN, 而非零, 以免把"没有可判读报道"误当成"完全一致"。需特别指出, finbert2 是二分类 (Bernoulli) 模型, 无独立中性类, 逐篇正、负类概率互补相加约等于一, 故对 finbert2 而言 P 加 N 约等于一 (是概率量而非篇数, 分母不等于该单元的文章篇数); 在这一近似下 disag 化简为 2 乘以根号下 (P 乘以 (1 减 P)), 其中 P 为平均正类概率——即以平均概率为参数的伯努利标准差的两倍, 是平均正类概率围绕 0.5 的对称山形函数。这一化简是 finbert2 相对三分类模型的构念特殊性: 它的 disag 与平均正类概率逐单调对应, 读数应作二分类极化解读, 不宜与三分类模型的同名列比较水平, 只比标准化后的回归系数。

【文献定位】
在测量层面, 本家族属于机器学习情感度量而非词典度量。Huang、Wang 与 Yang (2023) 论证了微调 BERT 在金融文本情感抽取上相对词典法的增益与边界; Frankel、Jennings 与 Lee (2022) 在顶刊 Management Science 上系统比较了机器学习情感与词典情感, 指出两类方法在不同任务上各有优劣、宜互为稳健性并置而非彼此替代——这正是本仓库把 finbert2 与另两家 BERT、与词典法、与 LLM 投票法平行保留的方法学依据。finbert2 模型本身取自 Xu 等 (2025) 的领域专用双向编码器工作。在构念层面, 以新闻文本的正负分歧作为主体级别信号已有实证先例: Li 与 Luan (2025) 直接用新闻构造投资者分歧并检验其对股票收益的解释力, Cookson 与 Niessner (2020) 则从投资者社会网络出发刻画分歧的来源与后果。本家族把这一构念下沉到银行-年面板, 作为媒体报道口径撕裂程度的稳健性测度轨。Goldman、Gupta 与 Israelsen (2024, Journal of Financial Economics) 直接度量不同新闻源对同一公司财经报道的分歧程度, 并证明这种报道分歧本身能预测异常交易量, 为本家族用新闻文本聚合出的银行层面分歧指数提供了同期实证先例。

## VAR: disag_finbert2_full

【变体差分】
本列是三轨中的 full 轨: 分子分母 P 与 N 均为 full 轨文本 (标题 prepend 加全文正文, content_full) 上 finbert2 逐篇正类、负类概率在该单元的均值 (finbert2_pos_full / finbert2_neg_full), 非 argmax 判正、判负的篇数。full 轨是留篇门控的判定轨——一篇报道是否计入某银行-年的报道宇宙, 由 stage 21 的 full 轨 verified 结果决定 (2026-06-29 full-only 门控口径), 因此 full 轨的 disag 建立在最完整的留篇集之上, 是本家族三轨中信息量最饱满、样本最稳的一轨, 通常用作首要读数。与同家族 ctx、ss 两轨的关系是: 三轨各自用同轨概率均值独立算出、各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨的 disag 列混进同一个 over-identified 的 Hansen J 过度识别检验 (三轨铁律)。full 轨读数解读时须记住 finbert2 是二分类模型, 其 disag 等于平均正类概率伯努利离散度的两倍, 水平不可跨模型直接比较, 只比标准化系数。分母 P 加 N 为零 (full 轨无可判读报道) 时该单元置 NaN。从构念上看, full 轨的分歧读数回答的问题是: 综合一家银行全年被媒体书写的完整文本, 正负两极的报道情感是否势均力敌。它对"报道整体撕裂"这一情形最敏感——即使全年报道均值温和, 只要平均正、负类概率接近持平, full 轨 disag 就会拉高, 从而把"温和的一致"与"温和的撕裂"区分开。这一点是本列相对家族内均值型情感列 (如 finbert2 的净情感均值) 的正交价值所在, 也是把它单列为稳健性轨而非并入均值列的原因。在识别口径上, full 轨作为留篇门控轨, 其样本宇宙最完整, 故其 disag 的年际方差最稳、最不易被单篇噪声左右, 适合作分歧维度的主读数; ctx 与 ss 两轨则在此基础上分别检验读数是否被"聚焦实体上下文"或"锁定同句共现"这两种文本裁剪口径所驱动。

## VAR: disag_finbert2_ctx

【变体差分】
本列是三轨中的 ctx 轨: P 与 N 为 ctx 轨文本 (标题 prepend 加实体上下文窗口, content_ctx) 上 finbert2 逐篇正类、负类概率在该单元的均值 (finbert2_pos_ctx / finbert2_neg_ctx), 非 argmax 判正、判负的篇数。ctx 轨把正文裁剪到目标银行实体附近的上下文窗口, 剔除与该银行无关的段落噪声, 使情感判读更聚焦于"关于这家银行"的表述, 但代价是可判读文本变短、部分报道退化为回退全文。相对 full 轨, ctx 轨是 conditional-on-full 的测度轨与稳健性轨 (行宇宙是 full 留篇集的子集, 但 per-track 概率均值照该轨自身文本重算), 用以检验分歧读数是否被"是否聚焦实体上下文"这一文本口径驱动。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。同 full 轨, finbert2 二分类性质使本列读数为平均正类概率离散度的两倍, 只比标准化系数、不比跨模型水平; ctx 轨无可判读报道时该单元置 NaN, 分歧不因文本裁短而虚高。ctx 轨的构念取舍值得展开: 把文本裁到实体上下文窗口后, 一篇原本兼含正负两方面表述的长报道, 可能只在银行实体附近保留了其中一极的措辞, 于是同一篇报道在 full 轨与 ctx 轨可能被 finbert2 给出不同的正负概率。因此 ctx 轨的 disag 与 full 轨的差异, 本身携带"报道的正负色彩在多大程度上集中于该银行实体近旁 vs 散落于无关段落"的信息。若两轨 disag 高度一致, 说明分歧读数对文本聚焦口径稳健; 若显著分化, 则提示报道的极化更多来自实体外围叙述, 这是稳健性叙事中值得披露的一层。正因为如此, 本仓库刻意不以两轨相关性高低决定去留, 而是让二者各进各自的回归、互为稳健性并置。

## VAR: disag_finbert2_ss

【变体差分】
本列是三轨中的 ss (same-sentence) 轨: P 与 N 为 ss 轨文本 (标题 prepend 加银行与金融科技同句共现正负 N 句窗, content_ss) 上 finbert2 逐篇正类、负类概率在该单元的均值 (finbert2_pos_ss / finbert2_neg_ss), 非 argmax 判正、判负的篇数。ss 轨是三轨中口径最严的一轨, 只保留目标银行与金融科技词在同句 (正负一句窗) 共现的语境, 意在把情感判读锁定到"这家银行的金融科技相关表述"上。其回退语义镜像 ctx 轨: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母; 当整体 FINTECH_AC 为空时全部标记优雅降级。因此 ss 轨的 disag 在开发期极短面板 (T 很小) 上可能因有效样本稀疏而退化, 属预期现象。ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。finbert2 二分类性质同样使本列等于平均正类概率伯努利离散度的两倍, 水平不可跨模型比较, 只比标准化系数; ss 轨无同句共现且回退后仍无可判读报道时该单元置 NaN。ss 轨的构念定位是三轨中最"就事论事"的一轨: 它试图回答, 当媒体把这家银行与金融科技放在同一句话里谈论时, 这些高度贴题的表述在正负两极上是否撕裂。相对 ctx 轨的实体窗口, ss 轨的同句共现约束更强, 因而更贴合本项目"银行金融科技报道"的核心构念, 但也更容易因共现稀疏而落入回退全文的情形——一旦大量报道回退, ss 轨在语义上就趋近于 full 轨、其增量信息随之衰减, 这一退化在开发期短面板上尤为明显, 应视为样本稀疏的预期表现而非缺陷。解读 ss 轨 disag 时须同时参考 ss_is_fallback 的占比: 回退比例越低, ss 轨越能反映纯粹同句语境下的分歧; 回退比例越高, 其读数越向 full 轨收敛。ss 与 full、ctx 三轨严格并置、互为稳健性, 不分主次, 不得混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Goldman, E., Gupta, N., & Israelsen, R. D. (2024). Political polarization in financial news. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2024.103816
<!-- rendered-citations:end -->
