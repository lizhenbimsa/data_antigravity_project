---
family_id: F221
columns:
- du_2022_pos_count_ctx
- du_2022_pos_count_full
- du_2022_pos_count_ss
unit: 篇数/计数 (count, 非负整数; 空 bank-year 填 0)
formula: "du_2022_pos_count{track} = Σ_{i ∈ bank-year} 1[du_2022_score{track}_i > 0]; 其中 du_2022_score = 规则增强净语调 (canonical polw05, 政治正面词以 0.5 权重计入正侧)"
producer: news_process/pipeline/panel/runner.py (article 级指示列 _is_du_2022_positive{track}) ; news_process/pipeline/panel/encode.py (bank-year 求和聚合) ; news_process/pipeline/sentiment/tone_words.py (du_2022_score 上游打分)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_score_full / _ctx / _ss)
- 40_panel_yearly.parquet (聚合宿主)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
- doi: "10.1016/j.jaccpubpol.2024.107181"
  type: "journal"
  authors: "Cheng, C. A., Jiang, L., & Song, W.-L."
  year: 2024
  title: "Media coverage and debt financing choice"
  venue: "Journal of Accounting and Public Policy"
  vol: "44"
  pages_or_artno: "107181"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个 bank-year 单元内, 被 du_2022 金融情感词典判定为「净正面语调」的报道篇数, 按三条文本轨 (full / ctx / ss) 各出一列。它不是一个连续的语调强度分, 而是一个可加的计数: 先在文章层逐篇算出该篇在 du_2022 词典下的规则增强净语调 du_2022_score, 若该值严格大于零则该篇记为一次正面命中, 再把同一 bank-year 内的命中次数相加。因此它回答的是「这一年关于这家银行, 词典口径下有多少篇报道整体偏正面」这一体量问题, 与偏度、占比、均值等口径互补。分母语义留在同族的 neg_count 与 n_articles 等列, 本列只承担分子中的正侧计数, 从而让下游可以自由构造正负差、正面占比、极性净额等派生指标而不被预先归一化锁死。

du_2022 词典来自 Du, Huang, Wermers 与 Wu (2022) 在 Review of Finance 发表的中文金融情感词典。该词典的构念立足于「语言特异性与领域特异性」这一核心主张: 直接把英文 Loughran 与 McDonald 词表机械翻译到中文会丢失中文金融语域里的表达习惯与政治话语色彩, 因此需要一部在中文语料上重新归纳、并显式区分普通正面词与政治正面词的本土词典。落到本流水线, du_2022 提供普通 positive 约 2,235 词、negative 约 2,986 词, 另有 political_positive 约 1,434 词以 0.5 的降权计入正侧。这一 0.5 权重是 du_2022 这一部词典独有的构造, 依据是该文发现政治性正面措辞的信号强度弱于普通正面词; 项目据此把政治词权重取为 0.5 作为 canonical, 并把 {0.0, 0.5, 1.0} 三档设为互为稳健性、不分主次的权重梯子。本计数家族消费的正是 canonical 净语调 (polw05), 即政治词半权口径下的 du_2022_score。

【方法学与计算】
计算分三层。第一层在 stage 22 (tone_words) 逐篇打分: 对分词后的 token 序列在 du_2022 词典上做匹配, 命中正面词记正、命中负面词记负, 再叠加三条中文语言学规则 (否定翻转、程度副词缩放、转折让步降权), 得到每篇的加权净分 total_score, 归一化分则另存, 本家族只用 total_score 的符号。跨类重叠词按用户 2026-06-24 决策「保留并两侧计数」, 同一 token 同时进正负两侧, 对净分贡献零、对分母贡献两倍幅值, 从而把该词语调拉向中性而非武断选边; 这一处理对本计数列的影响是: 一篇净分恰好被重叠词拉回零的报道不计入正面命中。第二层在 panel runner 构造文章级二值指示 _is_du_2022_positive{track} = 1[du_2022_score{track} > 0], 严格用严格不等号, 净分为零 (中性) 的报道不计入。第三层在 encode 的 groupby 聚合中对该指示列按 (bank, year) 求和, 得到本列; 对当年无任何报道的 bank-year, 计数类列在导出前统一填 0 而非 NaN, 以符合「计数无覆盖即为零」的契约。

三条文本轨 full / ctx / ss 各自独立走上述三层, 得到三列并排的计数。三轨是各自 just-identified 并排、互为稳健性、不分主次的关系, 严禁把三轨列混进同一 over-identified Hansen J。留篇门控采用 2026-06-29 的 full-only 口径: 一篇是否算「一篇银行金科报道」只看 full 轨的 LLM 判定, ctx 与 ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但每条轨的 per-track 计数照各自的文本内容独立计算。ss 轨的回退语义镜像 ctx: 当某篇没有银行与金科的同句共现时, 其 content_ss 回退为全文正文, 相应 fallback 标记置真, 分母与 ctx 共享 n_articles。

【文献定位】
在中文金融文本测度谱系里, du_2022 (Du, Huang, Wermers & Wu, 2022) 是与本项目并用的六部词典之一, 也是唯一显式携带政治正面词分层的词典, 其在 Review of Finance 的方法学地位使其成为政治词权重敏感性检验的锚。相邻的 Bian, Jia, Li 与 Yan (2021) 同样是 Loughran 与 McDonald 框架的中文本土化扩充, 但不区分政治词, 因而与 du_2022 构成同一构念下的替代词典稳健性。更晚近的 Ma, Zhang 与 Zhang (2025) 提出面向中国境内投资者的细粒度情感词典 CN-FSD, 代表词典细粒度化的方法学前沿, 说明「计数一部固定词典的正面命中」这一朴素测度在多词典并置下仍有稳健性价值。Todd, Bowden 与 Moshfeghi (2024) 对金融文本情感分析文献的综述则勾勒了词典法与机器学习法的分野, 佐证本项目把词典计数、LLM 投票、BERT 概率三法并置为互为稳健性轨的做法。Fang, Wang, Wang 与 Yuan (2024) 在中国银行层面用媒体情感解释存款稳定与系统性风险, 是本计数列在银行研究场景下的典型下游应用范式。 同域前沿方面, Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 表明把新闻情感按银行主体归集、再进入银行层面实证, 是当前金融稳定研究接受的做法, 可为本列「逐篇判定极性再按 bank-year 归集」的层级设定提供同域背书; 其边界在于该文语境为美国银行监管 (以监管评级与监管行动为 DV), 本项目为中国商业银行金融科技报道语境且 DV 另定, 原文情感测度的构造细节与本项目六词典并置、逐篇净分符号判正的口径不同, 亦不涉及三轨文本或 LLM 投票, 更无实质性/象征性维度。聚合形态上, Cheng、Jiang 与 Song (2024) 以 RavenPack 把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量与新闻情感并解释债务融资方式选择, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率, 为「文章级极性判定 → 按主体-年对极性指示求和」这一聚合范式提供了前沿实证用例。援引须严格限定: 该文极性来自 RavenPack 专有事件情感分析 (ESS), 既非公开情感词典亦非人工编码, 故此处只锚定其聚合形态, 不锚定极性来源; 且其主体为美国上市公司而非银行, 亦无提及密度加权变体。
## VAR: du_2022_pos_count_ctx

【变体差分】
本列是 du_2022 正面命中计数的实体窗 (ctx) 轨。它与家族其余两列的唯一区别在文本轨: ctx 轨消费的是 stage 14 物化的 content_ctx, 即标题 prepend 后再取目标银行实体上下文窗口的文本, 而非整篇正文。因此同一篇报道在 ctx 轨下的 du_2022_score 只统计落在银行实体邻近窗口内的情感词, 一篇整体偏正、但正面措辞集中在与目标银行无关段落的报道, 在 ctx 轨可能不再被判为正面命中, 从而与 full 轨的计数产生系统性差异。这一差异正是 ctx 轨作为稳健性轨的价值: 它把「关于这家银行本身的正面语调」与「文章大环境的正面语调」分离开。

需要复述的口径铁律: ctx 轨与 full、ss 两轨各自 just-identified 并排, 三者互为稳健性、不分主次, 严禁把三轨列混进同一 over-identified Hansen J。留篇门控为 full-only, 故 ctx 轨的行宇宙是 full 留篇集的子集, 属 conditional-on-full 测度轨, 但计数本身按 content_ctx 独立计算, 分母与 ss 共享 n_articles。当某 bank-year 无任何留篇时该列填 0。政治词权重沿用 canonical 的 0.5 (polw05), 与权重梯子的 polw00、polw10 两臂互为稳健性、不分主次, 三档权重同样严禁混进同一 over-identified Hansen J。本列净分判正采用严格不等号, 中性 (净分为零) 报道不计入; 跨类重叠词平衡双票的处理在 ctx 轨同样生效。

## VAR: du_2022_pos_count_full

【变体差分】
本列是 du_2022 正面命中计数的全文 (full) 轨, 是家族内与留篇门控口径最直接对齐的一列。full 轨消费 stage 14 物化的 content_full, 即标题 prepend 后的整篇正文, 因此它统计一篇报道全文范围内 du_2022 词典的净正面判定。由于 2026-06-29 起留篇门控采用 full-only 口径, full 轨的行宇宙即留篇集本身 (不是子集), 这使 full 轨计数在数值上最贴近「这家银行这一年有多少篇整体偏正面的报道」的朴素直觉, 也使其常被选作首要读数、而把 ctx 与 ss 轨作为稳健性对照。

与家族其余两列的区别仅在文本轨: full 轨看整篇, ctx 轨看实体窗, ss 轨看银行与金科同句窗。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。本列的净分判正同样用严格不等号, 净分为零的中性报道不计入正面命中; 政治词权重为 canonical polw05 (0.5 半权), 与 polw00、polw10 两臂构成不分主次的权重梯子, 三档权重亦禁混进同一 over-identified Hansen J。跨类重叠词按「保留并两侧计数」处理, 一篇被重叠词拉回零净分的报道不计入。空 bank-year 计数填 0。相对 ctx 与 ss, full 轨因文本最长, 命中概率与计数量级通常最高, 这是文本覆盖面差异的机械后果而非偏误。

## VAR: du_2022_pos_count_ss

【变体差分】
本列是 du_2022 正面命中计数的同句 (ss) 轨, 三轨中口径最严。ss 轨消费 stage 14 物化的 content_ss, 即标题 prepend 后仅取目标银行与金融科技实体落在同一句 (可带 ±N 句半径, 由 config 的 ss_sentence_radius 控制, 默认 1) 的共现文本。因此 ss 轨统计的是「银行与金科被同句提及」这一最狭窄语境下的 du_2022 净正面判定, 意在剔除银行与金科各自出现但语义不相关的噪声, 逼近真正谈论该银行金科关系的正面语调。这是三轨中信息面最窄、计数量级通常最低的一列, 在开发期 T=2 的小样本上尤易退化, 属预期现象而非缺陷。

ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文, 相应 ss_is_fallback 标记置真, 并与 ctx 共享 n_articles 作为分母 (不另设 n_articles_ss); 若金科 AC 词表为空则该轨 fallback 全真, 整体降级为等价 full 的读数。需要复述的铁律: ss 轨与 full、ctx 各自 just-identified 并排, 三轨互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 留篇门控为 full-only, ss 轨行宇宙是 full 留篇集子集, 属 conditional-on-full 测度轨。净分判正用严格不等号, 中性报道不计入; 政治词权重为 canonical polw05 (0.5), 与 polw00、polw10 权重梯子不分主次、禁混同一 over-identified Hansen J; 跨类重叠词双侧平衡计数照常生效; 空 bank-year 计数填 0。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision?. Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
<!-- rendered-citations:end -->
