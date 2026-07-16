---
family_id: F152
columns:
- city_leave1out_bert_avg_pos_ctx
- city_leave1out_bert_avg_pos_full
- city_leave1out_bert_avg_pos_ss
unit: 无量纲概率均值 (BERT 正面类概率 ∈ [0,1] 的同城 leave-one-out 组年均值)
formula: "city_leave1out_bert_avg_pos_i,t = (Σ_{j∈city(i)} bert_avg_pos_j,t − bert_avg_pos_i,t) / (N_{city,t} − 1); 其中 bert_avg_pos = mean_{b∈THREE_CLASS_MODELS}(b_pos), 逐轨 track ∈ {_full,_ctx,_ss}"
producer: news_process/pipeline/panel/geography.py::compute_leave_one_out_sentiment
upstream:
- 23_tone_berts.parquet (finbert_cn / fin_sent_zh 三分类正面概率, 逐轨)
- 40_panel_yearly.parquet (bert_avg_pos{track} 由 geography.py::compute_composite_indicators 三分类聚合)
- config/银行面板2007-2025年.xlsx (bank_city 注册地城市, merge_bank_geography 合并)
citations:
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
- doi: "10.1016/j.econlet.2025.112306"
  type: journal
  authors: "Zhang, M., & Chen, J."
  year: 2025
  title: "Spatial spillovers of media sentiment divergence in the stock market: A dynamic spatial Durbin approach"
  venue: "Economics Letters"
  one_sentence_zh: "该文用动态空间杜宾模型证明媒体情感分歧存在显著的地理空间溢出效应, 为本家族「同城同业情感外溢作为工具变量」的外生性主张提供了最新的实证支撑。"
new_dois:
  - "10.1016/j.econlet.2025.112306"
---

## CORE

【构念与来源】
本家族刻画的是「同城其他银行的年度平均正面舆论」这一外生推力度量, 用作银行自身情感的工具变量 (instrumental variable)。对面板中每一个「银行 i × 年份 t」观测, 本度量取银行 i 注册地所在城市 (bank_city) 内、同一年度、除银行 i 之外其余所有银行的 BERT 正面类概率的均值, 即所谓 leave-one-out (排除自身) 的地理组均值。构念动机很直白: 一家银行当年被媒体正面报道的程度, 可能与它自身的经营基本面、财务表现或不可观测的地方冲击同时相关, 从而在回归里内生; 而「同城邻居银行的平均语调」在很大程度上由本地媒体生态、地方舆论环境、区域性金融科技叙事氛围所驱动, 不太可能反过来由银行 i 自己的单家行为所决定, 因此可以作为对银行 i 自身情感的外生推力。用大白话说: 我想知道「一家银行被夸得多不多」会不会影响它后续的融资成本或行为, 但「被夸」本身可能是结果不是原因; 于是我退一步, 用「它同城的左邻右舍平均被夸多少」来当替身——邻居的舆论氛围会外溢到它头上, 却基本不由它一家说了算。数据来源上, 分子分母都来自面板级的 bert_avg_pos 列: 该列是文章级 BERT 情感 (stage 23, 23_tone_berts.parquet) 先聚合到银行-年, 再在地理组内做 leave-one-out。银行注册地城市 bank_city 由 merge_bank_geography 从银行标识面板 (config 银行面板 xlsx) 合并而来, 是纯标识符, 不含财务信息。

【方法学与计算】
计算分两层。第一层是构造被平均的原料 bert_avg_pos: 在 geography.py::compute_composite_indicators 中, 对每条轨道 track, bert_avg_pos{track} = 三分类 BERT 模型 (THREE_CLASS_MODELS, 即 finbert_cn 与 fin_sent_zh, 刻意排除二分类 finbert2) 的正面类概率的等权均值。之所以只在三分类模型上平均, 是因为二分类 finbert2 把中性概率质量重新归一进正负两类 (pos+neg 恒等于 1), 其正面概率与三分类模型处于不同的类空间、系统性上偏, 直接混入会破坏 bert_avg_pos / bert_avg_neu / bert_avg_neg 三者近似构成概率单纯形的恒等式; finbert2 的逐模型列作为二分类稳健轨单独保留。第二层是 leave-one-out 组均值: 在 compute_leave_one_out_sentiment 中, 按 (bank_city, year) 分组, 用向量化的 O(N) 公式 leave1out_i = (组内求和 − 自身值) / (组内有效银行数 − 1) 求得; 分组内某年仅有一家银行有有效情感数据时, 分母为零, 结果按方法论正确的方式置 NaN (无法从自身推断本地媒体生态)。该 leave-one-out 度量与省级 (prov) 层同构并列, 也与词典法综合 (dict_tone) 和 LLM 投票 (llm_vote_tone) 的 leave-one-out 工具变量并列, 三种情感测度的地理工具变量共同支撑 Stata 中的过度识别检验 (Hansen J): 典型用法为 ivreghdfe 把银行自身 full 轨情感作为内生变量, 用同一轨道的 prov/city 情感、词典、BERT 三类 leave-one-out 工具变量识别, 再跑 estat overid。三轨 (full/ctx/ss)、三测度 (LLM/词典/BERT)、两地理层 (省/市) 之间的关系遵循项目铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把同一测度的 full/ctx/ss 三轨混进同一个 over-identified 的 Hansen J (跨轨混入会人为制造工具变量数量并污染过度识别检验); G-08 里刻意做过度识别的那一组, 用的是同一轨道 (通常 full) 下 LLM/词典/BERT 三种异质测度, 而非跨轨。全部计算在面板级完成, 不触及付费 LLM 缓存, 因此换嵌入模型或重跑情感阶段时本家族随上游 bert_avg_pos 变化而变化, 自身无独立随机源。留篇门控与全局口径一致 (full-only, 2026-06-29): 一篇报道是否计入「银行金科报道」由 full 轨判定, ctx/ss 轨为 conditional-on-full 的子集测度; ss 轨的回退语义镜像 ctx (无银行∧金科同句共现时 content_ss 退化为全文正文)。

【文献定位】
本家族坐落在三条文献脉络的交叉处。其一是金融文本情感的机器度量: 情感原料由中文金融领域微调的 BERT 产生, Huang, Wang, & Yang (2023) 系统论证了在金融文本上用大型语言模型抽取信息相较传统词典法的增量效度, 是 bert_avg_pos 选用 BERT 而非仅靠词典的直接依据; Li, Mai, Shen, & Yan (2021) 则展示了以机器学习从非结构化文本中构造企业层面构念 (企业文化) 的范式, 为「把文章级概率聚合成银行-年度构念」提供了方法学模板; Devlin, Chang, Lee, & Toutanova (2019) 是 BERT 架构本身的来源。其二是多测度并置与稳健性: Du, Huang, Wermers, & Wu (2022) 构造的中文金融情感词典是本项目词典法综合 (dict_tone) leave-one-out 工具变量的来源之一, 与 BERT 测度在 G-08 过度识别检验里互为异质测度、互为稳健性佐证。其三是识别策略与其经济学根据: leave-one-out 同城组均值属于「同期组均值」类工具变量, 其外生性主张与 Goldsmith-Pinkham, Sorkin, & Swift (2020) 关于 shift-share / Bartik 类工具变量在何时、为何、如何有效的诊断框架一脉相承——两者都依赖「暴露份额或组归属外生于个体特质冲动」这一识别核心; 而作为待识别对象的银行舆论, 其经济后果 (存款流动、透明度) 由 Chen, Goldstein, Huang, & Vashishtha (2022) 就银行信息披露与存款流动的因果链条给出, 为「为什么值得费力识别银行情感的外生变异」提供了结果侧的理论支点。需要如实披露的识别威胁是反射问题 (reflection problem): 地理完全组 (同省/同城全连接) 不满足非传递三元组条件, 因此本工具变量并不主张点识别, 只作为稳健性并排轨提供外生变异的一个来源, 其援用属限定条件披露而非无保留背书。Zhang & Chen (2025, Economics Letters) 用动态空间杜宾模型证明媒体情感分歧存在显著的地理空间溢出效应, 为本家族「同城同业情感外溢作为工具变量」的外生性主张提供了最新的实证支撑。

## VAR: city_leave1out_bert_avg_pos_full

【变体差分】
本列是 city_leave1out_bert_avg_pos 家族的 full 轨成员, 也是三轨中的主轨。它与同家族 _ctx、_ss 两列的唯一区别在于底层文本轨道: full 轨的文本单元 = 标题 prepend 之后的「标题 + 全文正文」, 即报道的完整篇幅。因此本列平均的 bert_avg_pos_full 是在完整报道正文上跑出来的三分类 BERT 正面概率, 再经银行-年聚合与同城 leave-one-out 求得。相较 ctx/ss 轨只截取实体窗口或银行金科同句窗, full 轨保留了最大的语境信息量, 也承担了全项目的留篇门控职责: 一篇报道是否被判为「银行金科报道」严格只看 full 轨 (full-only 口径, 2026-06-29), 故 full 轨的行宇宙即留篇集本身, ctx/ss 轨则是其 conditional-on-full 的子集测度。在识别用途上, city_leave1out_bert_avg_pos_full 与同轨的 prov 层、与同轨的词典 leave-one-out (city_leave1out_dict_tone_full) 和 LLM 投票 leave-one-out (city_leave1out_tone_full) 构成 full 轨上的多测度工具变量集合, 是 G-08 过度识别 Hansen J 检验的规范载体; 本列可与这些同轨异测度工具变量同置于一个 over-identified 方程, 但严禁与本家族的 _ctx / _ss 列跨轨混入同一 Hansen J——那会人为夸大工具变量数量并污染过度识别统计量。三轨各自 just-identified 并排、互为稳健性、不分主次, 主轨地位只体现在门控口径, 不代表数值上更「真」。需要提醒的是, 本列的城市级 leave-one-out 相较省级同轨列 (prov_leave1out_bert_avg_pos_full) 组更小、地方媒体生态的同质性更强, 因而外生推力更贴近本地舆论氛围, 但也更容易在小城市当年只有一两家银行时触发 leave-one-out 分母为零而置 NaN; 城市层与省级层之间同样是互为稳健性的并排关系, 使用者应结合样本覆盖在两层之间做效度权衡, 而非默认更细的城市层一定更优。

## VAR: city_leave1out_bert_avg_pos_ctx

【变体差分】
本列是 city_leave1out_bert_avg_pos 家族的 ctx 轨成员。它与主轨 _full 的唯一差别在底层文本轨道: ctx 轨的文本单元 = 标题 prepend 之后的「标题 + 实体上下文窗口」, 即只截取银行实体附近的语境片段而非整篇正文, 由 stage 14 ctx_materializer 物化的 content_ctx 派生。因此本列平均的 bert_avg_pos_ctx 是在实体窗口文本上跑出的三分类 BERT 正面概率经银行-年聚合、再做同城 leave-one-out 的结果。相较 full 轨, ctx 轨滤除了与目标银行关系较远的语料噪声, 代价是牺牲了篇章级语境, 因此它是主轨的稳健性并排轨而非替代: 若结论在 full 与 ctx 两轨上一致, 说明结果不被「取全文还是取实体窗」这一测量选择所驱动。口径上 ctx 轨为 conditional-on-full 子集测度 (留篇仍由 full 轨判定, 2026-06-29 full-only 门控), 分子分母严格逐轨——ctx 轨缺列或某地理组该年无 ctx 有效值时按 leave-one-out 边界规则置 NaN, 绝不借用 full 轨分母。识别上, city_leave1out_bert_avg_pos_ctx 只与同为 ctx 轨的 prov 层及 ctx 轨词典 / LLM leave-one-out 工具变量并列组队, 与本家族 _full / _ss 列各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。实务上, ctx 轨在实体窗口内更少纳入与目标银行无关的宏观或行业背景描写, 因此当 full 轨结果可能受「同篇报道顺带提及其他银行」的语料污染质疑时, ctx 轨给出一个更聚焦目标实体的对照读数; 若 full 与 ctx 两轨的一阶段相关强度与二阶段系数方向一致, 即可对该质疑给出稳健性回应, 这正是保留 ctx 轨而非仅报 full 轨的价值所在。

## VAR: city_leave1out_bert_avg_pos_ss

【变体差分】
本列是 city_leave1out_bert_avg_pos 家族的 ss 轨成员, 三轨中语境最窄。它与主轨 _full 的差别在底层文本轨道: ss 轨的文本单元 = 标题 prepend 之后的「标题 + 银行∧金融科技同句共现窗口 (±N 句)」, 即只保留银行与金科概念在同一句 (及邻近窗) 共现的片段, 由 stage 14 物化的 content_ss 派生。因此本列平均的 bert_avg_pos_ss 聚焦于「银行确实在谈金融科技」的最强针对性语料, 再经银行-年聚合与同城 leave-one-out 求得。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行∧金科的同句共现时, content_ss 优雅降级为全文正文、ss_is_fallback 置真, 与 ctx 轨共享 n_articles 分母。相较 full / ctx, ss 轨在 T=2 开发面板上因样本稀薄可能出现零方差或大量 NaN 退化, 属预期现象, 生产 T=19 语料下方能充分取值; 它作为最窄语境的稳健性并排轨, 检验结论是否对「是否强制银行与金科同句」这一测量口径稳健。口径上 ss 轨同为 conditional-on-full 子集测度 (留篇由 full 轨判定), 分子分母严格逐轨、缺列时按 leave-one-out 边界规则置 NaN 不借 full 分母。识别上, city_leave1out_bert_avg_pos_ss 只与同为 ss 轨的工具变量并列, 与本家族 _full / _ctx 列各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。ss 轨的意义在于把「银行的正面舆论」收窄到确实围绕金融科技议题展开的语料上, 从而排除银行因与金科无关的普通经营新闻而被正面报道所带来的干扰; 当研究关切明确指向金科相关舆论溢出时, ss 轨提供了针对性最强的外生推力读数, 而在样本稀薄时其退化行为也提示使用者需谨慎评估该层工具变量的弱识别风险。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
Zhang, M., & Chen, J. (2025). Spatial spillovers of media sentiment divergence in the stock market: A dynamic spatial Durbin approach. Economics Letters. https://doi.org/10.1016/j.econlet.2025.112306
<!-- rendered-citations:end -->
