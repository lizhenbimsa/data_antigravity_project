---
family_id: F413
columns:
- loughran_cater_b_ctx
- loughran_cater_b_full
- loughran_cater_b_ss
unit: 无量纲语调差值 (词典净语调 − BERT 净语调; 值域约 [-2, 2], 零为两测度一致)
formula: "loughran_cater_b{track} = loughran_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track}); 逐轨 (full/ctx/ss) 同域相减"
producer: news_process/pipeline/panel/runner.py (步骤 8d algo_cater 全展开) ; news_process/pipeline/sentiment/tone_words.py (loughran 词典打分)
upstream:
- 22_tone_words.parquet (loughran_tone_{full,ctx,ss})
- 23_tone_berts.parquet (bert_avg_pos_{full,ctx,ss}, bert_avg_neg_{full,ctx,ss})
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
citations:
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
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
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
new_dois: []
---

## CORE

【构念与来源】
本家族测度算法迎合度 (algorithmic catering) 的「Loughran-McDonald 中文主译本词典—BERT」变体, 度量同一篇银行金科报道在固定词表规则式打分与语境敏感深层判别式模型之间净语调的系统性落差。构念直觉与家族兄弟 du_2022_cater_b、jiang_2021_cater_b 等一致: 当一段文本对基于逐词匹配的词典引擎表现得比对语境更敏感的深层模型更为正面, 这种落差往往揭示文本在表层措辞上堆砌了可被机器逐词识别的褒义词, 而深层模型因能捕捉句法否定、程度修饰与语境线索, 不容易被这种表层堆砌迷惑; 落差为正即提示潜在的语调粉饰或对算法读者的迎合式书写。词典侧使用 loughran_mcdonald_zh_2026, 即原始英文 Loughran-McDonald (2011) 10-K 情感词典的中文主译本, 该词典正面词 1,295 个、负面词 3,729 个, 另含五类非极性词 (不确定性、诉讼、约束性、弱势等语言学功能词类, 本家族仅取正负极性两类参与打分)。落地公式为逐轨相减: loughran_cater_b 等于 loughran_tone 减去综合 BERT 净语调, 后者由综合三模型正类概率均值 bert_avg_pos 减负类概率均值 bert_avg_neg 构成。loughran 词典在加载阶段对 positive∩negative 跨类重叠词按「两侧保留」判断消歧 (原 61 词经用户决策 2026-06-24 保留而非剔除的口径, 38 词已归单侧、余 23 词不可约简仍两侧计数), 打分时重叠词以对称正负两票同时计入, 使该词典个体语调净向中性拉平而非武断选边; 这一消歧口径不影响以词典个体列 loughran_tone 为分子的本家族计算。

【方法学与计算】
计算发生在面板构造阶段的算法迎合度全展开步骤 (runner 步骤 8d)。对每条轨道, 引擎先核验词典净语调列 (loughran_tone{track}) 与综合 BERT 正负概率列 (bert_avg_pos{track}/bert_avg_neg{track}) 在面板中同域存在, 再执行同银行同年、同轨道的逐格相减, 得到 loughran_cater_b 的三轨列。「_b」后缀专指以综合 BERT 深层判别式模型作为参照引擎, 与以三家 LLM 多数投票共识为参照的 loughran_cater (无 b 后缀) 是两条并行、构念互补但不可混同的迎合度轨: 前者对照的是概率型判别式深层模型 (finbert_cn/fin_sent_zh/finbert2 三模型综合正负概率), 后者对照的是生成式大模型的多家投票共识。两参照引擎分别捕捉判别式与生成式两类深层模型对语境的不同理解方式, 因而在稳健性叙事中作为「各自 just-identified 并排、互为稳健性、不分主次」的两条轨呈现, 严禁将词典—BERT 迎合度与词典—LLM 迎合度混进同一 over-identified 的 Hansen J 过度识别检验。词典侧的 loughran_tone 经三条语言学规则 (否定翻转、程度副词、转折句式) 增强后自归一化, 用词典打分聚合测度所依赖的是 6 词典固定 union 词典口径下逐篇匹配 (个体词典列 loughran_tone 本身不受 union 聚合口径影响, 但词条本身经跨类重叠消歧); BERT 侧的正负概率为综合三模型的聚合均值, 反映判别式模型对文本整体情感分布的概率判断。两侧测度量纲经各自归一化后落在可比区间, 相减所得落差即为迎合度信号, 正值表示词典比 BERT 更正面 (潜在迎合), 负值表示 BERT 读出了词典未捕捉的正面或负面语境信息。

【文献定位】
迎合度构念的思想源流是 Cao, Jiang, Yang & Zhang (2023) 关于「当机器在聆听时如何说话」的研究, 其核心发现是当披露方预期文本会被算法解析时会策略性调整用词以取悦机器读者; 本家族把这一策略性行为操作化为词典引擎与 BERT 判别式引擎打分的可观测差。词典侧测度的方法论根基直接来自 Loughran 与 McDonald 一系列奠基性工作: When is a liability not a liability? (Loughran & McDonald, 2011, *The Journal of Finance*) 首次系统证明通用词典 (如 Harvard IV-4) 大量误判金融文本中的中性词为负面, 提出面向金融披露的专属词表, 该词表经本土化中文主译本移植后即为本家族词典侧的直接来源; Textual analysis in accounting and finance: A survey (Loughran & McDonald, 2016, *Journal of Accounting Research*) 系统梳理了词典法在会计与金融文本分析中的适用边界与消融敏感性依据, 支撑了本家族「词典对深层模型的落差需要被审计而非默认可信」的方法学立场; Measuring firm complexity (Loughran & McDonald, 2024, *Journal of Financial and Quantitative Analysis*) 是该系列近年将词典文本分析方法扩展到企业复杂度测度的延伸工作, 佐证词典法在与新型深层模型并行使用时依然具有独立的构念价值, 而非被后者完全替代。深层词典构造方法学层面, Ma, Zhang & Zhang (2025) 构建面向中国境内投资者的细粒度中文情感词典 CN-FSD, 与 Sun, Yuan & Xu (2025) 将词典知识与中性特征注入预训练语言模型的做法, 共同呼应了本迎合度测度「词典与深层模型互补而非替代、二者之差恰是可审计信息」的底层假设, 也为词典—BERT 落差的构念效度提供了跨语料佐证。

## VAR: loughran_cater_b_full

【变体差分】
本列为全文轨 (full) 变体, 是本家族在留篇门控口径下的锚定轨。full 轨文本等于标题 prepend 后拼接的完整正文 (content_full), 覆盖报道全文的情感信息。按 full-only 留篇门控 (2026-06-29), 一篇报道是否计入「银行金科报道」宇宙仅由 full 轨的 LLM 判定 (llm_verified_full) 决定, 因而 full 轨的迎合度落差建立在最完整、最权威的留篇集之上, 是本家族对外呈现结果时的首要轨。其数值等于 loughran_tone_full 减去 (bert_avg_pos_full 减 bert_avg_neg_full), 词典侧与 BERT 侧均取全文轨的同域聚合值, 分子分母严格逐轨匹配, 不借用其它轨道的语调或概率。相较 ctx/ss 两条稳健性轨, full 轨因文本最长, 对表层褒义词堆砌与深层语境判别之差的捕捉最为充分: 若迎合式书写散布在正文段落而非仅集中于标题或实体邻域, 唯 full 轨能完整体现这一信号。full 轨与 ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验; 三者只作规格稳健性的并排比较, 不设跨轨 FWER 模板。需强调本列的「_b」参照引擎恒为综合 BERT 判别式模型而非 LLM 投票共识, 因而它专门刻画词典打分相对深层概率型模型的偏离; 若同时希望对照生成式大模型, 应另取 loughran_cater_full (无 b 后缀) 并排检验, 二者互为稳健性、不分主次, 严禁混入同一过度识别检验。full 轨作为家族锚轨, 其正值区间对应「词典比 BERT 更褒义」的迎合方向, 负值则提示深层模型读出了词典未捕捉的语境信息, 数值本身经两侧各自归一化后同域可比。

## VAR: loughran_cater_b_ctx

【变体差分】
本列为实体窗轨 (ctx) 变体, 属 conditional-on-full 的稳健性轨。ctx 轨文本 (content_ctx) 等于标题 prepend 后拼接银行等目标实体邻域窗口内的句子, 而非全文; 它把情感测度聚焦到目标银行被提及的语境附近, 剔除与目标实体无关的段落噪声。因此 ctx 轨的迎合度落差回答的是「在直接谈及目标银行的文字里, 词典引擎是否比 BERT 更正面」这一更聚焦的问题。其数值等于 loughran_tone_ctx 减去 (bert_avg_pos_ctx 减 bert_avg_neg_ctx), 词典侧与 BERT 侧一律取实体窗轨的同域值, 严格逐轨匹配, 不与 full 轨或 ss 轨的语调、概率交叉借用。ctx 轨的行宇宙是 full 留篇集的子集 (conditional-on-full), 但 per-track 的迎合度列照常在该子集上逐格计算。相较 full 轨可能被大量无关正文稀释, ctx 轨对目标实体邻域的迎合式措辞更敏感, 是检验主结论不被文本范围选择驱动的关键稳健轨。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J。ctx 轨的参照引擎同样恒为综合 BERT, 与本家族无 b 后缀的词典—LLM 迎合度轨构念互补而不可混同; 在实体窗聚焦下, 若词典对目标银行邻域文字的褒义堆砌显著高于深层模型的语境判别, 该轨将放大迎合信号, 反之则收敛, 恰好补足 full 轨可能被长正文稀释的盲区。

## VAR: loughran_cater_b_ss

【变体差分】
本列为同句轨 (ss) 变体, 是三轨中判定最严格的稳健性轨。ss 轨文本 (content_ss) 等于标题 prepend 后拼接目标银行与金融科技词在同一句子及其前后 ±N 句窗口内共现的句子 (窗口半径由 filtering 配置的 ss_sentence_radius 控制, 默认 1), 从而把情感测度进一步收窄到银行与金科议题真正同现的最贴近语境。其数值等于 loughran_tone_ss 减去 (bert_avg_pos_ss 减 bert_avg_neg_ss), 词典侧与 BERT 侧均取同句轨的同域值, 严格逐轨匹配, 绝不借用其它轨的分子分母。ss 轨采用镜像 ctx 的回退语义: 当某篇报道不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母, 属优雅降级而非空值。因文本最短且最聚焦, ss 轨在开发期 T=2 小样本上可能出现方差退化 (格子稀疏), 属预期现象, 生产 T=19 语料上应恢复正常。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验。ss 轨的参照引擎与 full、ctx 一致恒为综合 BERT 而非 LLM 投票, 因而它度量的是在银行与金科议题最贴近共现的文字里词典相对深层模型的语调偏离; 这一最严聚焦口径使 ss 轨成为主结论对文本范围最敏感的稳健检验, 若迎合信号在全文轨成立却在同句轨消失, 即提示迎合式措辞可能并不集中于银行金科的核心语境, 此类跨轨对比正是三轨并排设计的价值所在。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
<!-- rendered-citations:end -->
