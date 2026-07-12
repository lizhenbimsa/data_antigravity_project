---
family_id: F071
columns:
- avg_within_doc_redund_ctx
- avg_within_doc_redund_full
- avg_within_doc_redund_ss
unit: 篇内字符3-gram自重复比 (无量纲 ratio, 定义域 [0,1] ∪ NaN)
formula: "avg_within_doc_redund_{track} = bank-year mean over articles of within_doc_redundancy; within_doc_redundancy = 1 − (唯一字符3-gram 数 / 全部字符3-gram 数), 逐篇在对应轨文本 content_{full,ctx,ss} 上计算"
producer: pipeline\sentiment\lexical_complexity.py::compute_lexical_complexity ; pipeline\panel\encode.py (bank-year mean 聚合, avg_within_doc_redund{track})
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - 22_tone_words.parquet
  - 40_panel_yearly.parquet
citations:
  - doi: 10.1093/restud/rdz061
    type: journal
    authors: Cagé, J., Hervé, N., & Viaud, M.-L.
    year: 2020
    title: "The production of information in an online world"
    venue: Review of Economic Studies
    vol: 87
    issue: 5
    pages_or_artno: 2126-2164
  - doi: 10.1093/qje/qjx045
    type: journal
    authors: Hansen, S., McMahon, M., & Prat, A.
    year: 2018
    title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
    venue: Quarterly Journal of Economics
    vol: 133
    issue: 2
    pages_or_artno: 801-870
  - doi: 10.1145/3657299
    type: journal
    authors: Xia, B., Rawte, V., Gupta, A., & Zaki, M. J.
    year: 2024
    title: "FETILDA: Evaluation framework for effective representations of long financial documents"
    venue: ACM Transactions on Knowledge Discovery from Data
    vol: 18
    issue: 7
    pages_or_artno: 1-27
  - doi: 10.1108/eb026526
    type: journal
    authors: Spärck Jones, K.
    year: 1972
    title: "A statistical interpretation of term specificity and its application in retrieval"
    venue: Journal of Documentation
    vol: 28
    issue: 1
    pages_or_artno: 11-21
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
本家族度量的是"篇内冗余"(within-document redundancy), 即单篇新闻在自身内部的字面自重复程度: 一篇报道中相同的字符片段被反复出现的比例越高, 该篇的行文越冗余、信息密度越低。构念上它衡量的是文本自身的重复性质, 而非跨篇章之间的相似性——这与本项目 staleness (整篇相似度) 和 herd (跨文章重复报道) 族刻意正交: staleness/herd 关注的是"篇间"重复 (这篇像不像别的报道), 篇内冗余关注的是"篇内"复读 (这篇自己有多啰嗦)。构念的会计学与金融文本学渊源为 Dyer-Lang-Stice-Lawrence (2017) 与 Cazier & Pfeiffer (2016) 关于 10-K 年报文本冗余与披露质量的研究: 冗余越高的披露往往对应更弱的信息含量与更差的可读性。本家族将该英文年报构念做中文新闻的落地操作化, 因原文的 operationalization 面向英文长文本, 汉字新闻篇幅更短、常无段落标记, 故本项目采用字符级 n-gram 自重复比作为可复现的 $0 代理。

【方法学与计算】
逐篇计算在 pipeline\sentiment\lexical_complexity.py::compute_lexical_complexity 内完成: 对单篇文本切出全部相邻字符 3-gram, 令分母为全部 3-gram 出现总数、分子为其中"唯一" (去重后) 3-gram 数, 则 within_doc_redundancy = 1 − 唯一3-gram/全部3-gram, 取值落于 [0,1], 越大越冗余。该实现是词形-词例比 (type-token ratio, TTR) 族的字符级变体, 全部依赖 jieba 0.42.1 冻结分词生态与纯字符串解析, 不触付费 LLM、不引新依赖、不触 M0 审批门。文章级度量本身 track-agnostic (输入单一文本返回单一 dict), 三轨 (full/ctx/ss) 的差异完全由调用方 tone_words 用各轨物化文本 content_full/content_ctx/content_ss 各调用一次驱动; 三轨文本在 stage 14 ctx_materializer 物化, prepend_title 已把标题拼入正文首句。面板聚合在 stage 40 完成: avg_within_doc_redund_{track} = 该 bank-year 内所有留篇文章 within_doc_redundancy 的算术均值。留篇门控为 full-only (2026-06-29 口径): 是否判为一篇银行金科报道只看 full 轨判定, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙为 full 留篇集的子集。三轨互为稳健性、不分主次、各自 just-identified 并排, 铁律禁止把三轨混进同一 over-identified Hansen J。ss 轨回退语义镜像 ctx: 当篇内无银行与金科的同句共现时 content_ss 回退为全文 body, ss_is_fallback=True, 与 ctx 共享分母口径。

【文献定位】
篇内冗余属于计算语言学与文本经济学交叉的可读性/披露质量测度谱系。Hansen, McMahon, & Prat (2018) 在 FOMC 讨论纪要上用计算语言学方法刻画沟通文本的信息与重复结构, 为"以词频/n-gram 结构量化文本沟通质量"提供了顶刊范式; 本家族的 3-gram 自重复正是这一范式在中文新闻上的轻量落地。Cagé, Hervé, & Viaud (2020) 在在线新闻生产的研究中系统度量了新闻内容的原创性与复制/复读, 是"以字面片段重复刻画信息生产"最贴近的顶刊参照——他们关注的复制是跨稿件的, 而篇内冗余把同一思路收缩到单篇之内。字符/词片段 n-gram 作为文本特征的统计基础可追溯至 Spärck Jones (1972) 对词项特异性 (term specificity) 的统计解释, 这是 n-gram 去重与信息量权衡的经典源头。Xia et al. (2024) 与 Beltagy, Peters, & Cohan (2020) 则从长金融文档表示与长文本建模角度提示: 文本冗余与长度高度耦合, 任何 TTR 族测度都存在机械长度依赖。据此本家族披露一项已知局限: within_doc_redundancy 存在强机械长度依赖 (与 Covington & McFall 2010 的 TTR 长度效应同构), 文档越长常见 3-gram 重复概率机械上升, 盘上实测冗余与长度呈正相关且长度分位组均值严格单调; 故回归中必须同时控制长度 (配套输出 redundancy_log_length = ln 去空白字符数)。此外存在汉字口径孪生 within_doc_redundancy_han (先抽纯汉字子序列再切 3-gram), 但实测其与字符版相关约 0.99, 属"字符口径对非汉字符号扰动的敏感性诊断"而非独立第二构念, 论文报告须披露该近完美共线且不与字符版同进一回归。构念解释还须诚实限定: 中文新闻篇幅中位约数百字、常无段落标记, 篇内信号弱于 10-K, 全量下宜另出 bank-year pooled 版互为稳健 (本模块仅篇级)。

## VAR: avg_within_doc_redund_full

【变体差分】
本列是家族的 full 轨, 计算文本为 content_full——标题经 prepend 拼入后的完整正文, 是三轨中的 canonical 轨, 也是留篇门控 (full-only, 2026-06-29 口径) 直接作用的轨。一篇报道是否被判为"银行金科报道"并计入某 bank-year 的留篇集只由 full 轨判定 (llm_verified_full == True), 因此 avg_within_doc_redund_full 参与均值的文章集就是该 bank-year 的完整留篇宇宙, 三轨中它的样本覆盖最全、代表性最强, 作为家族 canonical 应在主回归中优先使用。相对 ctx/ss 两个子窗轨, full 轨保留整篇正文因而文本最长, 其篇内冗余水平通常也最高: 篇内冗余的强机械长度依赖决定了 full 轨中位篇幅显著大于 ctx/ss 子窗, 更长的文本能被切出更多 3-gram、常见片段被反复命中的概率机械上升, 故轨间冗余差异首先应被理解为长度伪差异, 而非行文精炼度或风格的真实轨间差别; 使用本列做轨间对照 (例如 full 减 ctx) 时必须同时把配套的 redundancy_log_length (= ln 去空白字符数) 纳入控制, 否则轨间系数会被长度混淆。此外解读本列绝对水平时须记得它是 TTR 族字符级变体, 与汉字口径孪生 within_doc_redundancy_han 近完美共线 (实测相关约 0.99), 两者不得同进一回归。full 轨作为 canonical 与 ctx/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 铁律禁止把 full 与 ctx/ss 混入同一 over-identified Hansen J。本列非嵌入族, 属非嵌入 carve-out, 无 co-primary 的 _lg 孪生。

## VAR: avg_within_doc_redund_ctx

【变体差分】
本列是家族的 ctx 轨, 计算文本为 content_ctx——标题 prepend 后再加上银行等目标实体的上下文窗口, 相对 full 轨把语料收缩到实体邻近段落, 是 conditional-on-full 的稳健性/测度轨而非独立留篇门控轨: 它不参与"是否留篇"的判定, 其行宇宙是 full 留篇集的子集 (只对 full 已判为留篇的文章再算 ctx 轨冗余)。由于 ctx 子窗只截取实体上下文, 篇幅显著短于整篇 full (盘上 ctx 轨中位字数约为 full 轨的一半), 篇内冗余的机械长度依赖使本列的冗余水平通常系统性低于 full 轨: 更短的文本能被切出的字符 3-gram 更少, 去重后唯一 3-gram 占比相对更高, 因而自重复比 (1 − 唯一/全部) 相应下降。因此 avg_within_doc_redund_ctx 低于 full 轨这一事实不能直接读作"实体上下文段落更精炼、更少复读", 首先应归因于子窗带来的长度差异; 任何以本列与 full 轨作对照的分析都须同时控制 redundancy_log_length。ctx 轨的定位价值在于: 当研究者担心 full 轨冗余被大量与银行金科无关的背景段落稀释或污染时, ctx 轨提供了"聚焦实体语境"的稳健对照读数。ctx 轨与 full/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。本列非嵌入族, 无 _lg 孪生; 值得一提的是 ss 轨在无银行金科同句共现时正是回退镜像本 ctx 轨的语义。

## VAR: avg_within_doc_redund_ss

【变体差分】
本列是家族的 ss 轨, 计算文本为 content_ss (标题 prepend + 银行与金科在同句共现的 ±N 句窗, N 由 config filtering ss_sentence_radius 决定, 默认 1)。ss 是三轨中最窄的子窗, 只保留银行与金融科技在同一句附近共现的语境, 因此它的篇内冗余度量的是"银行金科共现语境内部"的字面自重复。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 优雅回退为全文 body、ss_is_fallback=True, 并与 ctx 共享 n_articles 分母口径; 若 FINTECH_AC 为 None 则全部 ss_is_fallback=True 优雅降级。因窗口最窄, 未回退时 ss 文本篇幅通常最短, 篇内冗余水平在三轨中一般最低 (同样源于篇内冗余的机械长度依赖: 极短文本切出的 3-gram 少、去重后唯一占比高、自重复比低), 而在大量回退到全文 body 的样本上, ss 文本实际等同 full 正文, 冗余水平又会向 full 轨靠拢。这一双态特征使本列的分布对回退比例高度敏感: 一个 bank-year 的 avg_within_doc_redund_ss 究竟落在"窄窗低冗余"还是"回退高冗余"区间, 取决于该 bank-year 内多少篇触发了 ss 回退, 因此解读本列绝不能脱离 ss_is_fallback 占比——回退占比高的 bank-year 其 ss 冗余本质上是 full 冗余的重述, 而非同句共现语境的真实冗余信号。正因如此 ss 轨最适合作为对 full/ctx 结论的稳健性旁证, 而非独立的主测度。ss 轨与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 铁律禁混同一 over-identified Hansen J; 作为 conditional-on-full 轨其行宇宙是 full 留篇集子集。本列非嵌入族, 属非嵌入 carve-out, 无 _lg 孪生。

<!-- rendered-citations:begin -->
Cagé, J., Hervé, N., & Viaud, M.-L. (2020). The production of information in an online world. Review of Economic Studies, 87(5), 2126-2164. https://doi.org/10.1093/restud/rdz061
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Xia, B., Rawte, V., Gupta, A., & Zaki, M. J. (2024). FETILDA: Evaluation framework for effective representations of long financial documents. ACM Transactions on Knowledge Discovery from Data, 18(7), 1-27. https://doi.org/10.1145/3657299
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The long-document transformer. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2004.05150
<!-- rendered-citations:end -->
