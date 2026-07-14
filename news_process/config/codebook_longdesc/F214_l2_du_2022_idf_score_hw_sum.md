---
family_id: F214
columns:
- du_2022_idf_score_hw_sum_ctx
- du_2022_idf_score_hw_sum_full
- du_2022_idf_score_hw_sum_ss
unit: 无量纲加权和 (banks-year 内对 herd-decay 权重 × IDF 缩放的 du_2022 词典净语调求和; 非归一化, 作为 herd-weighted 均值语调的分子)
formula: "du_2022_idf_score_hw_sum{track} = Σ_{i ∈ bank-year} ( du_2022_idf_score{track}_i × herd_weight{track}_i ); 其中 du_2022_idf_score = 逐篇 IDF 加权归一化净语调 (round 4), herd_weight 来自 stage 24 跟风衰减; 下游 du_2022_idf_tone_hw{track} = 本列 / Σ herd_weight{track}"
producer: news_process/pipeline/sentiment/tone_words.py (逐篇 du_2022_idf_score) ; news_process/pipeline/panel/runner.py (herd-decay 加权列 du_2022_idf_score_hw) ; news_process/pipeline/panel/encode.py (bank-year hw_sum 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_idf_score{track})
- 24_herd_decay_processor.parquet (herd_weight{track})
- config/tone_dicts.json (du_2022 正/负/政治正面词表 + IDF 权重)
citations:
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
- doi: 10.1016/j.jcorpfin.2025.102813
  type: journal
  authors: Campbell, J. L., Zheng, X., & Zhou, D.
  year: 2025
  title: "Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?"
  venue: Journal of Corporate Finance
  vol: 94
  pages_or_artno: 102813
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1017/CBO9780511809071
  type: book
  authors: Manning, C. D., Raghavan, P., & Schütze, H.
  year: 2008
  title: "Introduction to information retrieval"
  venue: Cambridge University Press
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个 banks-year (银行-年) 层面的加权情感聚合量: 把每篇涉银行金融科技报道用 du_2022 中文金融情感词典打出的、经 IDF (逆文档频率) 缩放的归一化净语调, 乘以 stage 24 跟风衰减 (herd-decay) 权重后, 在该银行当年的报道集合内求和。它不是一个归一化的语调均值, 而是均值的分子 —— 下游 du_2022_idf_tone_hw{track} 正是把本列除以同轨的 herd-decay 权重之和得到。之所以把分子单独物化为面板列, 是为了让 Stata 端能自选分母口径 (物理篇数 / 有效篇数 / 权重和) 复算加权均值, 并作为 rwolf、bootstrap 等稳健性程序可直接消费的原料。构念的三层来源: 情感极性来自 du_2022 词典, 词级重要性权重来自 IDF, 报道级重要性权重来自跟风衰减。三者相乘再求和, 意在回答"这家银行今年被媒体以何种情感基调、以多大的语义分量报道"这一问题, 而非简单的正负词计数。

du_2022 词典本身取自 Du 等 (2022) 在 Review of Finance 发表的中文金融情感词典工作。该词典针对中文金融语料的领域特异性构建, 含正面词约 2,235 个、负面词约 2,986 个, 另有 1,434 个政治正面词以降低的 0.5 权重计入正侧 (政治词权重敏感性属另一正交梯子, 本家族不涉及, 三权重变体在别处并排)。本家族只使用 du_2022 的常规正负极性与政治词的 canonical 0.5 权重, 不展开权重梯子。词典加载时对 positive∩negative 的跨类重叠词按用户 2026-06-24 决策"两侧保留并各计一票"处理, IDF 缩放只改幅值不改极性归属, 两侧计数取绝对值, 故与原始词典口径同源。

【方法学与计算】
逐篇计算分三步。第一步, stage 22 (tone_words) 用同一次分词的 token 序列, 对 du_2022 的 IDF 版词典施加语言学规则 (否定翻转 / 程度副词 / 转折) 后计算归一化净语调 idf_norm, 落为 du_2022_idf_score{track} (保留四位小数)。IDF 加权的思想源自信息检索: 一个情感词在语料中越罕见, 越具区分度, 其对文本情感的边际信息量越高, 因而应获得更大的权重; 这与词频-逆文档频率在文本内容分析中的经典用法 (Manning 等, 2008) 以及"词力"式的内容分析 (Jegadeesh & Wu, 2013) 一脉相承。第二步, stage 24 (herd_decay_processor) 对每篇报道估计一个跟风衰减权重 herd_weight{track}: 当同一事件在短时间内被大量高度相似的报道复述 (媒体跟风), 后续冗余报道被下调权重, 以避免情感信号被"回声"人为放大。runner 步骤 3d 把 du_2022_idf_score{track} 与 herd_weight{track} 逐元素相乘, 得篇级 du_2022_idf_score_hw{track}。第三步, encode 在 banks-year 分组上对该列做 sum 聚合, 得本家族的三条轨道列。空文本或无匹配词时逐篇分退化为 0 (与 ratio 契约对称), 不产生虚假极性。

留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算作"银行金融科技报道"只由 full 轨的 LLM 判定决定; ctx / ss 轨降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但每轨的 hw_sum 仍按各自轨道的篇级数值独立累加, n_articles 分母共享 full 口径。

【文献定位】
在中文金融文本计量谱系里, 本家族属于"词典 × 词级 IDF 权重 × 报道级衰减权重"三重加权的聚合测度。它与纯计数式情感 (MSENT)、未加 IDF 的等权均值语调互为稳健性: 前者对高频泛化情感词敏感, 本测度则通过 IDF 压低泛词、放大稀有判别词的贡献, 呼应 Jegadeesh & Wu (2013) 用词的判别力而非简单频次刻画内容的思路, 以及 Hwang & Kim (2017) 关于文本表达质量本身携带定价相关信息的证据。词典选择上, du_2022 (Du 等, 2022) 是面向中文金融的领域特化词典, 与近年的细粒度中文投资者情感词典 (Ma 等, 2025) 及融合词典知识的预训练情感模型 (Sun 等, 2025) 构成方法学光谱的两端 —— 前者可解释、可复现、零训练成本, 后者数据驱动、上下文敏感。领域特异性词典的构建逻辑亦与从无标注语料归纳领域情感词库的做法 (Hamilton 等, 2016) 相通。此外, 把定量披露的信息含量单列度量 (Campbell 等, 2025) 提示: 情感之外的文本"分量"维度同样值得作为并排稳健性轨, 而本家族的 IDF 与 herd 双权重正是对"报道分量"的两种操作化。三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J 检验。

## VAR: du_2022_idf_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体上下文窗) 轨。其篇级文本 content_ctx = 标题 prepend 后, 仅保留目标银行实体命中位置附近窗口内的句子 (窗口半径见 filtering.yaml 的 context_window 配置), 而非全文正文。相较 full 轨, ctx 轨把 IDF 缩放的 du_2022 净语调只在"围绕该银行的局部语境"上计算, 意在剥离报道中与目标银行无关的段落所携带的情感噪声, 使聚合出的加权和更聚焦于针对该银行主体的基调。计算链路与家族一致: du_2022_idf_score_ctx × herd_weight_ctx 逐篇相乘后在 banks-year 内求和。权重侧, ctx 轨消费 stage 24 的 herd_weight_ctx (跟风衰减在 ctx 文本上独立估计), 若该轨权重缺列则优雅回退 full 轨权重并记 WARN。口径归属上, ctx 轨在 full-only 门控下是 conditional-on-full 的测度/稳健性轨: 是否留篇由 full 轨 LLM 判定, ctx 轨只在留篇集子集上按自身文本重算数值。它与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J。当 ctx 文本因实体窗为空而退化为全文回退时, 其数值向 full 轨靠拢, 属预期行为而非缺陷; 在 T=2 开发样本上 ctx 轨可能出现低方差退化, 生产 T=18 语料下恢复正常辨识度。需强调本列是加权和 (分子) 而非归一化均值, 直接跨银行比较其绝对水平会混入报道量差异, 使用时须先按同轨的 herd-decay 权重之和 (或 n_articles) 归一, 或在回归中以银行、年份固定效应吸收规模项; 这一点对 ctx 轨尤其关键, 因其文本裁剪后单篇可匹配情感词更少, 篇级 idf_score 的量纲与 full 轨不完全可比。

## VAR: du_2022_idf_score_hw_sum_full

【变体差分】
本列是 full (全文) 轨, 也是三轨中承担留篇门控职责的主轨。其篇级文本 content_full = 标题 prepend 后拼接完整正文, 覆盖报道全篇的所有 du_2022 情感词, 因而在三轨中匹配到的情感词最多、IDF 缩放后的净语调统计上最稳定。计算链路: du_2022_idf_score_full × herd_weight_full 逐篇相乘, 再在 banks-year 内求和; 权重取 stage 24 的 herd_weight_full。full 轨的特殊地位在于 full-only 门控 (2026-06-29): 一篇报道是否被判为"银行金融科技报道"完全由 full 轨的 LLM 判定决定, 因此 full 轨的行宇宙即整个留篇集, 而 ctx / ss 两轨只在这一集合的子集上取值。作为加权均值 du_2022_idf_tone_hw_full 的分子, 本列除以 full 轨 herd-decay 权重之和即得该银行当年的 herd-weighted IDF 语调。full 轨相较 ctx / ss 更全面但也更易混入与目标银行无关段落的情感, 正因如此三轨才需并排: full 提供覆盖广度, ctx / ss 提供针对性, 三者各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J。全文轨对报道分量的刻画同时叠加了 IDF (词级) 与 herd (报道级) 两重权重, 与等权计数式情感形成方法学对照。作为家族中唯一承担留篇判定的轨道, full 轨列的取值直接决定了 ctx / ss 两轨的行是否存在: 若某银行-年在 full 轨下无留篇, 则三轨该格全空; 反之三轨该格都按各自文本取值。因此在稳健性叙事中, full 轨通常充当主设定, ctx / ss 轨作为收窄语境的替代测量, 三者数值差异本身即是对"情感信号是否被无关段落污染"的诊断。使用者若需 herd-weighted 均值语调而非加权和, 应取下游 du_2022_idf_tone_hw_full 而非直接使用本列。

## VAR: du_2022_idf_score_hw_sum_ss

【变体差分】
本列是 ss (银行 ∧ 金融科技同句) 轨, 三轨中语境最窄。其篇级文本 content_ss 只保留目标银行与金融科技词在同一句 (±N 句窗, ss_sentence_radius 默认 1) 共现的句子, 因而 IDF 缩放的 du_2022 净语调被约束在"该银行与金融科技被同时提及"的最贴近语境上, 最大程度剥离泛化背景情感, 聚焦银行的金融科技叙事基调。计算链路与家族一致: du_2022_idf_score_ss × herd_weight_ss 逐篇相乘后在 banks-year 内求和; 权重取 stage 24 镜像 ctx 产出的 herd_weight_ss, 缺列时优雅回退 full 轨权重。ss 轨的回退语义严格镜像 ctx: 当某篇无银行 ∧ 金融科技同句共现时, content_ss 退化为全文 body 且 ss_is_fallback=True (共享 n_articles 分母); 当 FINTECH_AC 词表为 None 时 ss_is_fallback 全 True 优雅降级。口径上, ss 轨同样是 full-only 门控下的 conditional-on-full 稳健性轨, 留篇由 full 轨 LLM 决定, ss 只在子集上按同句文本重算。它与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J。因语境最窄, ss 轨在 T=2 开发样本上极易出现零方差退化 (同句共现稀少), 生产 T=18 语料下方能提供有效的针对性稳健性信号; 这一退化属预期, 不应被误判为管道缺陷。正因语境最贴近银行的金融科技叙事, ss 轨在三轨中最能回答"针对该银行金融科技活动本身的媒体基调如何", 但代价是样本稀疏、方差不稳, 故它只作稳健性轨而非主设定。与 full、ctx 一样, 本列是加权和 (分子), 跨银行比较绝对水平前须先按同轨权重和归一或以固定效应吸收规模; 三轨列名满足 both-or-neither 之外的独立降级语义 (ss 缺同句共现仅回退自身文本, 不连坐 full/ctx)。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Campbell, J. L., Zheng, X., & Zhou, D. (2025). Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?. Journal of Corporate Finance, 94, 102813. https://doi.org/10.1016/j.jcorpfin.2025.102813
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
<!-- rendered-citations:end -->
