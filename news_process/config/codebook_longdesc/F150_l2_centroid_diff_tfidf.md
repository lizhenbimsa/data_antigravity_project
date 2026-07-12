---
family_id: F150
columns:
- centroid_diff_tfidf_w
- centroid_diff_tfidf_w_ctx
- centroid_diff_tfidf_w_ss
unit: 文本向量到全行业质心的距离 (无量纲, 归一化非负)
formula: "centroid_diff_tfidf_w = 1 - cos(v_i, c_{-i}); v_i = 银行 i 报道聚合的 jieba 词级 TF-IDF 向量; c_{-i} = (n·c − v_i)/(n−1) = 同期剔除银行 i 自身后的 leave-one-out 行业质心 (n<2 则无定义置 NaN); 三轨 full/ctx/ss 各自独立构造质心与距离"
producer: news_process/pipeline/features/strategic_diff.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: "Measuring founding strategy"
  venue: Management Science
  vol: 69
  issue: 1
  pages_or_artno: 101-118
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: 40
  issue: 1
  pages_or_artno: 3-27
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是单家银行在给定年度被第三方媒体报道所勾勒出的"战略画像", 相对于同期整个银行业"平均画像"的偏离程度, 也就是所谓的全行业质心距离 (industry centroid distance)。构念的直觉很朴素: 若把每家银行当年的全部新闻文本压缩成一个高维词频向量, 再把全行业所有银行的向量取平均得到一个"行业质心", 那么某家银行离质心越远, 就说明媒体笔下的它在业务重心、话题结构、叙事用词上越偏离行业主流, 越具有差异化 (distinctiveness) 或战略独特性; 反之贴近质心则意味着其媒体形象与同业高度同质、缺乏辨识度。本家族的三列 centroid_diff_tfidf_w、centroid_diff_tfidf_w_ctx、centroid_diff_tfidf_w_ss 分别在 full、ctx、ss 三条文本轨道上独立计算这一距离, 采用的向量化口径是 jieba 词级 (word-level) 的 TF-IDF 表示, 后缀 "_w" 即 word 之意, 与同一生产函数产出的字符级 (char-level, char_wb, 对应 "_c" 后缀) 轨道构成成对的稳健性检验。用大白话说, 这组变量回答的是"这家银行在新闻里被写得跟别家有多不一样", 数值越大越不一样。

需要强调本项目与差异化文献原始设定的一个根本差别: Hoberg 与 Phillips (2016) 一系的文本网络差异化测度使用的是企业自有的 10-K 披露文本, 测的是"企业自我披露差异"; 本项目的语料是第三方媒体报道 (中文银行/金融科技新闻), 因此测度的是"媒体感知差异 (media-perceived differentiation)"而非自我披露差异。这一口径转换是本家族解读时的第一性前提, 任何将其等同于企业主动战略选择的推断都必须先经过"媒体是否忠实反映战略"这一中介环节的论证。此外, 本项目银行样本每年约数十家, 远小于 TNIC 数据集数千家企业的规模, 因此质心的估计更易受个别报道量异常银行的牵引, 小样本下的质心稳定性是已知局限。

【方法学与计算】
计算链路分四步。其一, 文本聚合: 对每个银行-年单元, 把该单元下的全部报道文本按对应轨道拼接 (full 轨为标题 prepend 后的全文正文; ctx 与 ss 轨为窗口化超级文档), 得到该单元的文档串。其二, 向量化: 在同期全行业语料上拟合一个 jieba 词级 TF-IDF 向量器, 该分词器自 2026-06-21 起注入 1506 个金融科技领域词 (金融科技、区块链等复合词整词保留), 使领域复合词不被切碎, 与字符轨、嵌入轨的领域感知口径一致; 每个银行-年单元被映射为一个非负 TF-IDF 稀疏向量 v_i。其三, 质心构造: 对每家银行 i 取"剔除其自身后"的同期行业 leave-one-out 质心 c_{-i} = (n·c − v_i)/(n−1), 其中 n 为该同期单元数、c 为含自身的全体均值; 此 leave-one-out 口径自 fix(omni-g-strategic-10, 2026-06-11) 起替换了原先含自身的全体均值 mean, 因为把待测银行自身向量也计入质心会引入约 1/n 量级的机械自相关 (对与行业越正交的银行抬升越大, 系统性压缩 centroid_diff 右尾), leave-one-out 消除了这一偏差, 并与模块内 N-最近邻路径 fill_diagonal 置 NaN、fluidity 排除自身的既有惯例对齐; 当同期单元数 n<2 时 leave-one-out 质心无定义, 该单元距离置 NaN。其四, 距离度量: 以 1 减去 v_i 与 c_{-i} 的余弦相似度作为距离。因 TF-IDF 向量分量非负, 余弦相似度落在 [0,1], 故本家族距离亦被约束在归一化的非负区间 (与 Embedding 轨余弦真值域 [-1,1]、距离域 [0,2] 不同, 后者刻意不做地板裁剪以保留负余弦信息; 本 TF-IDF 家族因非负天然无此问题)。三条轨道各自独立拟合向量器、独立构造质心、独立算距离, 互不借用分母或词表。

关于三轨与稳健性口径的铁律必须复述: full、ctx、ss 三条轨道是"各自 just-identified 并排、互为稳健性、不分主次"的设计, 严禁把三轨的同名距离列混进同一个 over-identified 的 Hansen J 过度识别检验; 同理, word 级 (_w) 与 char 级 (_c)、TF-IDF 与 LDA、TF-IDF 与 Embedding 各方法轨亦是并排的稳健性替代, 而非可叠加进一个联合矩条件的多重工具。留篇口径遵循 full-only 门控 (2026-06-29): 一个银行-年单元是否计入"银行金科报道"样本, 由 full 轨的 llm_verified_full 判定, ctx/ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的质心与距离仍在各自轨道上独立照算。

【文献定位】
本家族的方法学谱系落在"用文本相似度刻画企业间战略/竞争差异"这一近十余年快速成长的实证传统。Hoberg 与 Phillips (2016) 在 Journal of Political Economy 上奠定了以企业披露文本的向量余弦构造内生产品市场网络与差异化测度的范式, 是本家族"文本向量 + 余弦距离"内核的直接思想来源。Guzman 与 Li (2023) 在 Management Science 上提出以最近邻文本距离度量创业公司的"创始战略", 论证了文本距离作为战略差异化代理的可行性与效度, 本项目的 N-最近邻族与本质心族互为并排稳健度量即取法于此。战略管理文献进一步厘清了"差异化"这一构念的经济含义与情境依赖: Haans (2019, Strategic Management Journal) 讨论了在同质与异质品类中"与众不同"的价值差异, 提醒差异化的绩效含义并非单调; Miller 与 Wang (2024, Strategic Management Journal) 以图书出版业为例研究了数字化如何驱动差异化战略变迁; Arts、Cassiman 与 Hou (2025, Strategic Management Journal) 则将技术差异化与产品市场竞争、并购交易联系起来, 为本家族在金融科技情境下的解读提供了外部效度参照。方法层面, Rodriguez 与 Spirling (2022) 系统比较了不同文本表示 (词嵌入 vs 计数型 TF-IDF) 在应用研究中的适用边界, 支持本项目并置 TF-IDF、LDA、Embedding 多轨互证而非单押一种表示的稳健性策略。

## VAR: centroid_diff_tfidf_w

【变体差分】
本列是家族的 canonical 列, 对应 full 轨 (无轨道后缀), jieba 词级 TF-IDF 全行业质心距离。其文本口径为标题 prepend 后的完整正文 (content_full): 把该银行-年单元下每篇报道的标题拼接到正文之前, 再将该单元所有报道串接成一份文档, 在同期全行业语料上拟合词级 TF-IDF 向量器并取剔除本行自身后的 leave-one-out 行业质心 c_{-i}=(n·c − v_i)/(n−1) 为参照 (含自身均值会引入约 1/n 机械自相关, 故 fix(omni-g-strategic-10) 起改用 leave-one-out; n<2 置 NaN), 以 1 减余弦相似度得距离。它区别于同族 _ctx / _ss 两列的唯一维度是文本轨道: 本列用的是覆盖面最广、信息量最全的全文轨, 因而质心与距离都建立在最完整的媒体叙事之上, 通常作为该测度的首要报告轨。它区别于生产函数内 centroid_diff_tfidf_c (未纳入本家族) 的维度是分词粒度: 本列 "_w" 为 jieba 词级, char 级 "_c" 为字符窗口, 二者对同一文本给出并排的稳健性度量, 词级对领域复合词 (金融科技、区块链等因注入 1506 金科词而整词保留) 更敏感, 字符级则对未登录词与切分歧义更鲁棒。它区别于 centroid_diff_lda / centroid_diff_emb 的维度是向量表示法: 本列是稀疏计数型 TF-IDF, 后两者分别是 LDA 主题分布 (配 JSD 距离) 与稠密语义嵌入, 三法互为稳健性替代而非可合并的联合矩。铁律: 本 full 轨列与 _ctx / _ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨同名列混进同一 over-identified Hansen J。

## VAR: centroid_diff_tfidf_w_ctx

【变体差分】
本列是 canonical 列的 ctx 轨孪生, 计算方法与 full 轨完全一致 (jieba 词级 TF-IDF、剔除本行自身的 leave-one-out 行业质心 c_{-i}=(n·c − v_i)/(n−1)、1 减余弦距离), 唯一差分维度是文本轨道: 本列消费的是 ctx 上下文窗口超级文档 (content_ctx), 即以标题 prepend 后仅保留实体 (目标银行) 邻近窗口的截断文本, 而非全文。其含义是把质心距离限定在"银行被提及的语境局部"这一更聚焦的叙事片段上度量差异化, 剔除了与目标银行无关的背景段落对向量的稀释, 因而对"围绕该行的具体话题"更灵敏, 但也牺牲了全文的语境完整性。它是 full 轨 canonical 测度的稳健性轨: 若主结论在全文轨成立而在实体窗口轨消失或反号, 即提示该差异化信号可能由报道中与银行无关的行业背景文本驱动, 而非银行本身的差异化叙事。留篇口径为 conditional-on-full: 本列只在通过 full 轨 llm_verified_full 门控的留篇单元上取值, 行宇宙是 full 留篇集的子集, 但 ctx 轨的向量器、质心、距离均在 ctx 文本上独立构造, 不借用 full 轨的任何中间量。在开发期 T=2 的极小样本上, 实体窗口截断可能使个别单元的向量高度稀疏甚至退化, 此时本轨距离对文本清洗与分词的敏感度高于全文轨, 生产期 T=18 语料下窗口截断的稳定性方可充分体现, 解读开发期数值须留意此退化风险。铁律复述: full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨同名距离列混入同一 over-identified Hansen J 过度识别检验。

## VAR: centroid_diff_tfidf_w_ss

【变体差分】
本列是 canonical 列的 ss 轨孪生, 度量口径 (jieba 词级 TF-IDF、剔除本行自身的 leave-one-out 行业质心 c_{-i}=(n·c − v_i)/(n−1)、1 减余弦距离) 与 full / ctx 完全一致, 唯一差分维度是文本轨道: 本列消费的是 ss 同句共现超级文档 (content_ss), 即以标题 prepend 后, 仅保留"目标银行与金融科技词在同一句子及其前后 ±N 句窗口内共现"的最严格文本片段 (窗口半径由 config 的 ss_sentence_radius 控制, 默认 1)。因此本列度量的是"在银行与金融科技被并置言说的最紧密语境里"该行相对全行业的差异化, 是三轨中语境最窄、信噪比取向最激进的一条, 用于检验主结论是否稳健于极端聚焦的银行×金科共现叙事。回退语义严格镜像 ctx 轨: 当某单元不存在银行与金融科技的同句共现时, content_ss 优雅回退为全文 body, 同时 ss_is_fallback 置为 True 以标记该单元走了回退路径, 与 ctx 轨共享 n_articles 分母; 若上游金科词 AC 自动机为 None, 则相关 _is_fallback 标志整体置 True 做优雅降级, 不会静默清空。留篇口径同为 conditional-on-full, 行宇宙是 full 留篇集子集, ss 轨向量器与质心在 ss 文本上独立构造。需注意本 ss 轨的同句共现判据与 stage 13 共现硬过滤所用的邻近共现判据虽同源于实体上下文原语, 但口径不同 (ss 为严格同句 ±N 窗、stage 13 为句级邻近), 二者不可互相复用; 回退比例较高时本列的有效方差主要来自回退的全文样本, 解读须结合 ss_is_fallback 占比一并审视。铁律复述: full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨同名列混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
<!-- rendered-citations:end -->
