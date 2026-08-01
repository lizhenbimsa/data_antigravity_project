---
family_id: F116
columns:
- bert_pos_count_ctx
- bert_pos_count_full
- bert_pos_count_ss
unit: 篇数 (bank-year 内被判正面的报道计数, 非负整数)
formula: "bert_pos_count{track} = Σ_{a ∈ 银行年内报道} _is_bert_positive{track}(a); _is_bert_positive = 1{逐 BERT 模型 argmax 极性中投正面的模型占比 > 0.5 (模型间多数票)}"
producer: news_process/pipeline/panel/runner.py (washing_cols; 由 stage23 原始 {b}_正面{track} 概率列现算 _bert_avg=投正面模型占比、多数票 > 0.5 → _is_bert_positive{track} 指示列, 属落盘前 drop 的文章级中间列) ; news_process/pipeline/panel/encode.py (聚合 K-block, 对该指示列 'sum' 归约为银行年篇数)
upstream:
- 23_tone_berts.parquet ({b}_正面 / _负面 / _中性{track} 逐模型 BERT 分类概率列; 注意 _is_bert_positive{track} 非本 parquet 直出的指示列, 而由下游 runner.py 现算)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  issue: null
  pages_or_artno: 102776
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2018
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
  vol: null
  issue: null
  pages_or_artno: arXiv:1810.04805
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
  vol: null
  issue: null
  pages_or_artno: null
- doi: "10.3390/ijfs13020075"
  title: "Financial Sentiment Analysis and Classification: A Comparative Study of Fine-Tuned Deep Learning Models"
  authors: "Nasiopoulos, D. K., Roumeliotis, K. I., Sakas, D. P., Toudas, K., & Reklitis, P."
  year: 2025
  venue: "International Journal of Financial Studies"
  type: "journal"
- doi: "10.18653/v1/2023.emnlp-main.956"
  title: "FinEntity: Entity-level Sentiment Classification for Financial Texts"
  authors: "Tang, Y., Yang, Y., Huang, A., Tam, A., & Tang, J."
  year: 2023
  venue: "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)"
  type: "wp"
new_dois:
  - "10.1002/isaf.1549"
  - "10.3390/ijfs13020075"
  - "10.18653/v1/2023.emnlp-main.956"
---

## CORE

【构念与来源】
本家族三列 bert_pos_count_full / _ctx / _ss 记录的是同一个底层构念在三条文本轨上的银行年计数: 在某家银行某一年内被保留的银行金科报道中, 经 BERT 情感模型判定为正面情感的报道篇数。它不是一个连续的情感强度度量, 而是一个非负整数计数, 是下游 "洗稿率" (washing ratio, 实质性对象征性口径缺口) 系列指标 E 路 (BERT 均值) 的分母基元。构念上它回答的是一个前置的量化问题: 在这家银行这一年的金科相关媒体叙事里, 到底有多少篇被机器读出正面基调? 有了这个正面篇数的分母, 才能进一步在其上叠加象征性证据密度分子, 构造出 washing_ratio_bert 这一类披露实质性缺口测度。

【方法学与计算】
文章级底层信号需厘清生产者链条: stage 23 (tone_berts) 落盘的是每个 BERT 模型对每篇报道的原始分类概率列 ({b}_正面 / _负面 / _中性{track}), 而 _is_bert_positive{track} 这一二值指示列并非该 parquet 的直出列, 它是在 stage 40 面板阶段由 runner.py 的 washing_cols 构造块现算的文章级中间列, 且在落盘前被统一 drop, 绝不进入文章级 parquet。指示列的判定机制是逐模型 argmax 极性的模型间多数票, 而非概率集成或概率平均: 先对每个 BERT 模型各自取 argmax 得到该篇的离散极性 (3-class 模型如 finbert_cn / fin_sent_zh 在正面 / 中性 / 负面三类间取极大; 2-class Bernoulli 模型 finbert2 只在正面 / 负面二类间以 P(正面) > 0.5 判定, 与 softmax 和为一时的 argmax 逐位等价), 再统计投正面 (argmax 结果为正面) 的模型占比 _bert_avg, 该占比严格大于 0.5 (即多数模型投正面) 时把 _is_bert_positive{track} 置一, 否则置零。此处方法 E 的历史标签 "BERT 均值" 中的 "均值" 作用于逐模型的正面 argmax 标签指示 (取占比后过 0.5 阈值), 不是对裸概率取平均后再二值化 —— 后者是 2026-06-11 修复 (omni-g-runner-01) 明确弃用的旧实现 (跨 2-class 与 3-class 的裸概率尺度不可比, 均值会被 finbert2 的 2-class 尺度主导)。方法 E (集成多数票) 与逐模型的 E2 路 (finbert_cn / fin_sent_zh / finbert2 各自的 pos_count) 并列而非替代。计数在 stage 40 由 encode.py 的聚合块 (K block) 完成: 对每家银行每年内的全部报道, 把上述 _is_bert_positive{track} 指示做 sum 归约, 落成 bert_pos_count{track}。因此本列在语义上等价于 "该银行年、该文本轨下经 BERT 多数票判正面的报道数", 单位是篇, 取值为非负整数, 无量纲归一化。

留篇口径遵循全仓 full-only 门控 (2026-06-29): 是否算作一篇进入银行金科报道宇宙的报道, 只由 full 轨的 LLM 留篇判定 (llm_verified_full) 决定; ctx 与 ss 轨是条件在 full 留篇集之上的子测度轨, 其行宇宙是 full 留篇集的子集, 但每条轨各自按本轨文本重新判定正面并各自计数。分母口径由此在三轨间保持一致的行集来源, 而分子的正面判定则逐轨独立。当某轨文本对某篇不可得或回退时, 该篇在该轨的 _is_bert_positive 依 stage 23 的降级语义处理; ss 轨的回退镜像 ctx 轨语义 (无银行金科同句共现时 content_ss 退化为全文正文)。

【文献定位】
以 BERT 类预训练语言模型抽取金融文本情感, 方法学锚在 Devlin et al. (2018) 提出的双向 Transformer 预训练范式, 以及 Huang et al. (2023) 面向金融文本信息抽取的 FinBERT 大模型工作, 后者论证了领域微调后的 BERT 在金融叙事情感判别上相较通用模型与词典法的增量。Frankel et al. (2022) 系统对比了机器学习与词典法在披露情感测量上的一致与背离, 支撑本项目为何要在词典轨之外并列一条 BERT 轨作为互为稳健性的测度来源。Loughran and McDonald (2016) 对会计与金融文本分析的综述则确立了正负面篇数分离统计 (而非直接极性对冲) 的计量传统, 使得像本家族这样先算正面篇数再叠加象征性密度的两步构造具有方法学合法性。正面篇数作为分母基元最终服务于 Bingler et al. (2022) 意义上的 "廉价空话与摘樱桃" 识别: 只有先框定正面叙事的规模, 才能检验其中有多少是有实质证据支撑、有多少只是象征性表态。需强调三条文本轨 (full / ctx / ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨计数混进同一条 over-identified 的 Hansen J 过度识别检验。Todd, Bowden, and Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述了基于文本(含BERT类模型)的金融情感分析文献并展望未来方向, 为本家族以BERT多数票判正面篇数的方法学定位提供了最新综述锚点。Nasiopoulos, Roumeliotis, Sakas, Toudas, & Reklitis (2025, International Journal of Financial Studies) 比较微调 BERT/FinBERT/GPT-4o 等深度学习模型在金融文本情感分类上的表现, 为多模型集成判正面情感提供最新方法学参照。Tang, Yang, Huang, Tam, & Tang (2023, Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing) 构建实体级金融文本情感分类基准数据集并测评 BERT/FinBERT/ChatGPT, 支撑本家族以 BERT 多数票判定报道正面情感的实体级情感抽取传统。

## VAR: bert_pos_count_full

【变体差分】
本列是 full 文本轨的正面报道篇数: 对每篇报道取 content_full (标题 prepend 后拼接全文正文) 作为 BERT 情感判别的输入文本, 极性为正面则计入, 银行年内求和即得。full 轨在全仓口径里具有特殊地位 —— 留篇门控本身就是 full-only 的, 即 "一篇银行金科报道" 的成立与否只看 full 轨的 LLM 留篇判定, 因此 bert_pos_count_full 的行宇宙就是该银行年被判定为银行金科报道的全部留篇, 分母不被任何轨条件化裁剪, 是三轨中口径最完整、最贴近 "全文语料下正面叙事规模" 的一支。与同家族的 ctx / ss 两列相比, 本列差异仅在输入文本轨: 它读全文, 不做实体窗口或同句窗口截断, 因而通常正面篇数最大、方差最稳。它是三轨中作为首要报告轨的一支, 与 ctx / ss 各自 just-identified 并排、互为稳健性、不分主次, 三者禁混进同一条 over-identified 的 Hansen J。下游 washing_ratio_bert 的 full 变体正是以本列为分母基元。需注意本列采集的是方法 E 的集成正面判定, 其机制是逐模型 argmax 极性的模型间多数票 (投正面模型占比 > 0.5), 并非对裸概率取平均后二值化; 它与逐个 BERT 模型各自的正面篇数 (方法 E2, 如 finbert_cn / fin_sent_zh 二三分类、finbert2 二分类 Bernoulli 各自的 pos_count) 属并列关系: 各模型独立降级, 缺席某模型只掉自身族而不连坐集成轨。作为计数而非情感强度, 本列对稀疏银行年不产生连续插值, 零值表示该银行年 full 轨下无任何一篇被判正面, 与缺失有本质区别, 建模时须区分结构零与缺失; 生产语料 (T=19) 下本列在多数银行年取正整数, 试跑语料 (早期试跑 T=2) 下则可能出现大量结构零属预期退化。

## VAR: bert_pos_count_ctx

【变体差分】
本列是 ctx (实体上下文窗口) 文本轨的正面报道篇数: 输入文本改为 content_ctx, 即标题加上银行与金科实体附近的上下文窗口, 而非整篇全文正文; 在此截断文本上由 BERT 判正面则计入, 银行年内求和。与 full 列相比, 本列的唯一差分维度是文本轨: ctx 只保留实体邻近的语义片段, 剔除与银行金科主题无关的背景段落, 目的在于让情感判定更聚焦于目标实体所处的局部语境, 削弱长文中无关正面表述带来的稀释与噪声。因 ctx 轨是条件在 full 留篇集之上的子测度轨, 其行宇宙是 full 留篇集的子集, 每篇是否正面按 ctx 文本重新判定, 故 bert_pos_count_ctx 通常不等于也不大于对应的 full 计数, 而是提供一条口径更窄、对实体局部语境更敏感的稳健性对照。本列与 full / ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混进同一条 over-identified 的 Hansen J。当某篇 ctx 文本回退 (无有效实体窗口) 时, 其正面判定依 stage 23 降级语义处理, 不向 full 借分母。与 full 列相同, 本列同样采集的是方法 E 的集成正面判定 (逐模型 argmax 极性的模型间多数票, 投正面占比 > 0.5, 非概率平均), 与逐模型 E2 路并列; 作为非负整数计数, ctx 轨因文本更窄, 情感信号密度更高但样本可判性略降, 其正面篇数相对 full 的收缩幅度可作为 "全文无关正面语料稀释程度" 的一个侧写。

## VAR: bert_pos_count_ss

【变体差分】
本列是 ss (银行金科同句共现窗口) 文本轨的正面报道篇数: 输入文本为 content_ss, 即标题加上银行与金科词在同一句子及其前后各 N 句窗口内共现的最严片段 (窗宽由 filtering.yaml 的 ss_sentence_radius 控制, 默认 1); 在此最窄语义片段上由 BERT 判正面则计入, 银行年内求和。与 full / ctx 两列相比, 本列差分维度同样只是文本轨, 但截断口径最严: 它要求银行与金科在同句邻域内真正共现, 只保留最贴近 "银行做金科" 语义焦点的文本, 从而给出对目标构念最保守、最抗无关正面语料污染的正面篇数。ss 轨的回退语义镜像 ctx 轨: 当某篇不存在银行与金科的同句共现时, content_ss 优雅退化为全文正文 (ss_is_fallback 置真), 该篇的正面判定与 full 轨共享分母口径下的处理, 避免静默丢篇。因 ss 轨条件在 full 留篇集之上, 本列行宇宙是 full 留篇集的子集, 计数通常最小、对稀疏银行年退化最明显 (窗口内可能零共现)。本列与 full / ctx 各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混进同一条 over-identified 的 Hansen J。作为最严口径的正面篇数, 本列在下游 washing_ratio_bert 的 ss 变体中充当最保守的分母基元, 其正面判定仍取方法 E 的集成结果 (逐模型 argmax 极性的模型间多数票, 投正面占比 > 0.5, 非概率平均; 其中 finbert2 为二分类 Bernoulli, finbert_cn / fin_sent_zh 为三分类), 与逐模型 E2 路并列。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Nasiopoulos, D. K., Roumeliotis, K. I., Sakas, D. P., Toudas, K., & Reklitis, P. (2025). Financial Sentiment Analysis and Classification: A Comparative Study of Fine-Tuned Deep Learning Models. International Journal of Financial Studies. https://doi.org/10.3390/ijfs13020075
Tang, Y., Yang, Y., Huang, A., Tam, A., & Tang, J. (2023). FinEntity: Entity-level Sentiment Classification for Financial Texts. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP) [Working Paper]. https://doi.org/10.18653/v1/2023.emnlp-main.956
<!-- rendered-citations:end -->
