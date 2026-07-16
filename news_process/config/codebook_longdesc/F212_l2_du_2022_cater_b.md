---
family_id: F212
columns:
- du_2022_cater_b_ctx
- du_2022_cater_b_full
- du_2022_cater_b_ss
unit: 无量纲语调差值 (词典净语调 − BERT 净语调; 值域约 [-2, 2], 零为两测度一致)
formula: "du_2022_cater_b{track} = du_2022_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track}); 逐轨 (full/ctx/ss) 同域相减"
producer: news_process/pipeline/panel/runner.py (步骤 8d algo_cater 全展开) ; news_process/pipeline/panel/stata_export.py (Stata 标签)
upstream:
- 22_tone_words.parquet (du_2022_tone_{full,ctx,ss})
- 23_tone_berts.parquet (bert_avg_pos_{full,ctx,ss}, bert_avg_neg_{full,ctx,ss})
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
citations:
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.jbef.2023.100809
  type: journal
  authors: Nițoi, M., Pochea, M.-M., & Radu, Ş.-C.
  year: 2023
  title: "Unveiling the sentiment behind central bank narratives: A novel deep learning index"
  venue: Journal of Behavioral and Experimental Finance
  vol: 38
  pages_or_artno: 100809
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
new_dois: []
---

## CORE

【构念与来源】
本家族测度算法迎合度 (algorithmic catering) 的「词典—BERT」变体, 度量同一篇银行金科报道在两套异构情感引擎下净语调的系统性落差。构念的直觉是: 当一段文本对基于固定词表的规则式情感打分表现得比对语境敏感的深层神经模型更为正面时, 这种落差往往揭示文本在措辞层面对可被机器逐词读取的褒义词的堆砌, 而深层模型因能捕捉句法否定、转折与语境线索而不被表层褒义词面所迷惑。落差为正即提示潜在的语调粉饰或对算法读者的迎合式书写。落地公式为逐轨相减: du_2022_cater_b 等于 du_2022 词典净语调减去综合 BERT 的净语调, 其中 BERT 净语调由综合正类概率均值 bert_avg_pos 减综合负类概率均值 bert_avg_neg 构成。词典侧的 du_2022_tone 来自 Du et al. (2022) 构建的中文金融本土化情感词典, 该词典在通用正负极性词之外另含一批政治正面词, 生产口径以 0.5 权重计入正侧 (权重敏感性梯子 polw00/polw05/polw10 属另一正交家族, 本家族固定采用 canonical 的 du_2022_tone)。

【方法学与计算】
计算发生在面板构造阶段的算法迎合度全展开步骤 (runner 步骤 8d)。对每条轨道, 引擎先核验词典净语调列与 BERT 正负概率列在面板中同域存在, 再执行同银行同年、同轨道的逐格相减, 得到 du_2022_cater_b 的三轨列。这里的「_b」后缀专指以 BERT 深层模型作为参照引擎, 与以 LLM 三家投票共识为参照的 du_2022_cater (无 b) 是两条并行、构念互补但不可混同的迎合度轨: 前者对照的是概率型判别式深层模型, 后者对照的是生成式大模型的多数投票。两参照引擎各自捕捉不同层面的语境理解能力, 因而在稳健性叙事中作为「各自 just-identified 并排、互为稳健性、不分主次」的两条轨呈现, 严禁将词典—BERT 迎合度与词典—LLM 迎合度混进同一 over-identified 的 Hansen J 过度识别检验。词典侧的净语调经语言学规则 (否定翻转、程度副词、转折) 增强后自归一化; BERT 侧的正负概率为综合三模型的聚合均值, 反映判别式模型对文本整体情感分布的概率判断。两侧测度量纲经各自归一化后落在可比区间, 相减所得落差即为迎合度信号。

【文献定位】
迎合度构念的思想源流是 Cao 等 (2023) 关于「当机器在聆听时如何说话」的研究, 其核心发现是当披露方预期文本会被算法解析时, 会策略性地调整用词以取悦机器读者; 本家族正是把这一策略性行为操作化为词典引擎与深层引擎打分的可观测差。词典侧测度依托 Du et al. (2022) 发表于 Review of Finance 的中文金融情感词典, 该文系统论证了语言与领域特异性对情感词表构建的关键作用, 指出直接移植英文 Loughran-McDonald 词表到中文金融语境会产生系统性偏差, 因而需要本土化扩充——这正是选用 du_2022 而非通用词典作为迎合度词典侧锚的方法学依据。深层引擎一侧的合理性可由 Nițoi et al. (2023) 佐证, 其构建的深度学习情感指数表明神经模型能捕捉词典方法遗漏的语境情感信号, 从而使词典与深层模型之差具有实质的构念内涵而非纯噪声。词典构造方法学层面, Hamilton et al. (2016) 提出的从无标注语料诱导领域特异情感词表的框架, 与 Ma et al. (2025) 构建的面向中国境内投资者的细粒度中文情感词典 (CN-FSD), 共同刻画了金融情感词典在覆盖度与领域适配上的演进; Sun et al. (2025) 进一步将词典知识与中性特征注入预训练语言模型, 呼应了本迎合度测度「词典与深层模型互补而非替代」的底层假设——二者的差恰是可被审计的信息。

## VAR: du_2022_cater_b_full

【变体差分】
本列为全文轨 (full) 变体, 是本家族在留篇门控口径下的锚定轨。full 轨文本等于标题 prepend 后拼接的完整正文 (content_full), 覆盖报道全文的情感信息。按 full-only 留篇门控 (2026-06-29), 一篇报道是否计入「银行金科报道」宇宙仅由 full 轨的 LLM 判定 (llm_verified_full) 决定, 因而 full 轨的迎合度落差建立在最完整、最权威的留篇集之上, 是本家族对外呈现结果时的首要轨。其数值等于 du_2022_tone_full 减去 (bert_avg_pos_full 减 bert_avg_neg_full), 词典侧与 BERT 侧均取全文轨的同域聚合值, 分子分母严格逐轨匹配, 不借用其它轨道的语调或概率。相较 ctx/ss 两条稳健性轨, full 轨因文本最长而对表层褒义词堆砌与深层语境判别之差的捕捉最为充分, 迎合式书写若存在于正文段落而非仅标题或实体邻域, 唯 full 轨能完整体现。full 轨与 ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验; 三者只作规格稳健性的并排比较, 不设跨轨 FWER 模板。需强调本列的「_b」参照引擎恒为综合 BERT 判别式模型, 而非 LLM 投票共识, 因而它专门刻画词典打分相对深层概率型模型的偏离; 若同时希望对照生成式大模型, 应另取 du_2022_cater_full (无 b 后缀) 并排检验, 二者互为稳健性、不分主次, 严禁混入同一过度识别检验。full 轨作为家族锚轨, 其正值区间对应「词典比 BERT 更褒义」的迎合方向, 负值则提示深层模型读出了词典未捕捉的正面语境, 数值本身经两侧各自归一化后同域可比。

## VAR: du_2022_cater_b_ctx

【变体差分】
本列为实体窗轨 (ctx) 变体, 属 conditional-on-full 的稳健性轨。ctx 轨文本 (content_ctx) 等于标题 prepend 后拼接银行等目标实体邻域窗口内的句子, 而非全文; 它把情感测度聚焦到目标银行被提及的语境附近, 剔除与目标实体无关的段落噪声。因此 ctx 轨的迎合度落差回答的是「在直接谈及目标银行的文字里, 词典引擎是否比深层引擎更正面」这一更聚焦的问题。其数值等于 du_2022_tone_ctx 减去 (bert_avg_pos_ctx 减 bert_avg_neg_ctx), 词典侧与 BERT 侧一律取实体窗轨的同域值, 严格逐轨匹配, 不与 full 轨或 ss 轨的语调、概率交叉借用。ctx 轨的行宇宙是 full 留篇集的子集 (conditional-on-full), 但 per-track 的迎合度列照常在该子集上逐格计算。相较 full 轨可能被大量无关正文稀释, ctx 轨对目标实体邻域的迎合式措辞更敏感, 是检验主结论不被文本范围选择驱动的关键稳健轨。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J。ctx 轨的参照引擎同样恒为综合 BERT, 与本家族无 b 后缀的词典—LLM 迎合度轨构念互补而不可混同; 在实体窗聚焦下, 若词典对目标银行邻域文字的褒义堆砌显著高于深层模型的语境判别, 该轨将放大迎合信号, 反之则收敛。因窗口只取实体邻近句, ctx 轨对标题与首段的迎合式措辞尤为敏感, 恰好补足 full 轨可能被长正文稀释的盲区, 使读者能判断迎合是否集中在与目标银行直接相关的语境。

## VAR: du_2022_cater_b_ss

【变体差分】
本列为同句轨 (ss) 变体, 是三轨中判定最严格的稳健性轨。ss 轨文本 (content_ss) 等于标题 prepend 后拼接目标银行与金融科技词在同一句子及其前后 ±N 句窗口内共现的句子 (窗口半径由 filtering 配置的 ss_sentence_radius 控制, 默认 1), 从而把情感测度进一步收窄到银行与金科议题真正同现的最贴近语境。其数值等于 du_2022_tone_ss 减去 (bert_avg_pos_ss 减 bert_avg_neg_ss), 词典侧与 BERT 侧均取同句轨的同域值, 严格逐轨匹配, 绝不借用其它轨的分子分母。ss 轨采用镜像 ctx 的回退语义: 当某篇报道不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母, 属优雅降级而非空值。因文本最短且最聚焦, ss 轨在开发期 T=2 小样本上可能出现方差退化 (格子稀疏), 属预期现象, 生产 T=19 语料上恢复正常。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验。ss 轨的参照引擎与 full、ctx 一致恒为综合 BERT, 而非 LLM 投票, 因而它度量的是在银行与金科议题最贴近共现的文字里词典相对深层模型的语调偏离; 这一最严聚焦口径使 ss 轨成为主结论对文本范围最敏感的稳健检验, 若迎合信号在全文轨成立却在同句轨消失, 即提示迎合式措辞可能并不集中于银行金科的核心语境, 此类跨轨对比正是三轨并排设计的价值所在。

<!-- rendered-citations:begin -->
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Nițoi, M., Pochea, M.-M., & Radu, Ş.-C. (2023). Unveiling the sentiment behind central bank narratives: A novel deep learning index. Journal of Behavioral and Experimental Finance, 38, 100809. https://doi.org/10.1016/j.jbef.2023.100809
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
