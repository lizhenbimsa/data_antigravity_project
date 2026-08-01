---
family_id: F244
columns:
- exc_du_2022_score_degonly_ctx
- exc_du_2022_score_degonly_full
- exc_du_2022_score_degonly_ss
unit: 情感倾向分值 (无量纲, 带符号词典打分的银行-年均值)
formula: "exc_du_2022_score_degonly_track(b,y) = mean over articles a in (b,y) with media(a) NOT in ceased_set of du_2022_score_degonly_track(a); 文章级 du_2022_score_degonly = 带符号词典极性加权和, 仅施加程度副词六级加权规则 (否定翻转 OFF, 转折增强 OFF, 政治词权重取 canonical polw05); ceased_set = detect_defacto_cessation 检出的疑似覆盖退出媒体 (confirmed ∪ suspected)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity
upstream:
- 22_tone_words.parquet (du_2022_score_degonly_{full,ctx,ss} 文章级列)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- 40_panel_export_main (detect_defacto_cessation → ceased_set)
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
- doi: 10.1016/j.jbef.2023.100809
  type: journal
  authors: Nițoi, M., Pochea, M.-M., & Radu, Ş.-C.
  year: 2023
  title: "Unveiling the sentiment behind central bank narratives: A novel deep learning index"
  venue: Journal of Behavioral and Experimental Finance
  vol: 38
  pages_or_artno: 100809
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
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
本家族刻画的是一个复合稳健性测度: 在剔除"疑似退出覆盖的媒体"之后, 用 Du 等 (2022) 的中文金融情感词典、并只保留"程度副词加权"这一条语言学规则, 对每篇银行-金融科技报道打出的带符号情感分, 再聚合到银行-年层级的均值。它同时承载两条相互正交的稳健性叙事: 其一是样本选择维度的"停刊/覆盖退出稳健性"(exc 前缀); 其二是打分规则维度的"规则消融梯度"(degonly 后缀)。两条叙事都不是主结果测度, 而是用来证明主结论对"哪些媒体进入样本"以及"施加哪几条语言学规则"这两个研究者选择并不敏感的旁证轨。它绝不进入主回归的解释变量位置, 只在稳健性 battery 里与 canonical 主情感列并排, 供读者判断系数方向与显著性是否被上述两个人为选择所驱动。

【构念与来源】的第一层是词典来源。Du 等 (2022, Review of Finance) 面向中文金融文本构造了一部本土化的情感词典, 系统论证了金融文本情感具有强烈的语言与领域特异性——把英文金融词典或通用中文情感词表直接迁移到中文金融语料会产生系统性失真, 因此需要在中文金融语境下重新界定正负极性词并对情感强度做校准。本项目以 tone_dicts.json 为该词典的单一事实源 (SSOT), 正词赋 +1、负词赋 -1; 对于同时落在正负两类的重叠词, 按用户 2026-06-24 决策予以保留并在两侧各自计数 (占位幅值取绝对值, 符号无意义)。需特别指出的是, Du 等 (2022) 词典体系内含一类"政治正面词", 项目对该类词按 0.5 权重计入正侧并做 {0.0, 0.5, 1.0} 三级政治词权重敏感性检验; 本 degonly 家族在政治词权重维度上取 canonical 的 polw05 口径, 政治词权重梯子与规则消融梯度刻意保持正交、不交叉, 以避免 3×8 的列组合爆炸。

【方法学与计算】文章级 du_2022_score 是词典命中词的带符号加权和, 而 degonly 变体在此基础上只开启"程度副词六级加权"这一条规则: 否定窗口翻转关闭、转折 (adversative) 增强关闭, 因此该变体绝不改变任何命中词的极性符号, 只按"极其/非常/较/略"等程度副词的六级强度调整幅值。它属于 v3.11.1 引入的规则消融梯度 (rule-ablation ladder), 该梯度把状态机三规则 (否定翻转 / 程度加权 / 转折增强) 做 powerset 组合, 物化出 raw、negonly、degonly、advonly、negdeg、negadv、degadv 七个非-full 变体, degonly 是其中"仅程度"这一格 (状态位 negation=False, degree=True, adversative=False), SSOT = tone_words 的 _RULE_ABLATION_VARIANTS。exc 前缀的语义来自 attention_media.detect_defacto_cessation: 该函数在银行-金融科技报道子集上按媒体统计首末出现年份与文章数, 把最后出现年份早于样本末年减去阈值间隔 (threshold_gap 默认 2)、且文章数不低于门槛的媒体标记为"疑似覆盖退出", 并与新闻出版署 (NPPA) 停办名录做交叉验证; 排除集 ceased_all = confirmed ∪ suspected, 即未经证实的 suspected 也全量进入排除集, NPPA 交叉验证仅改报告标签而不收窄排除集。随后 compute_media_heterogeneity 在排除这些媒体的存活样本上, 对每个银行-年格逐轨求 du_2022_score_degonly 的算术均值, 落为 exc_du_2022_score_degonly。诚实披露口径: 该检测度量的是媒体"退出银行-金融科技话题覆盖"(topic exit) 而非经证实的报纸停刊, 媒体可能仍在正常出版; 因而下游 exc_* 只可解读为"疑似退出覆盖媒体"的保守剔除稳健性口径, 不可在论文中表述为严格停刊 (publication cessation) 口径。计数上的零文章格与情感均值格处理不同: n_articles_exc 按"计数 Σ over ∅ = 0"契约填 0, 而 exc_* 情感类列在空集上按契约保持 NaN, 绝不连带零填。

【文献定位】把媒体覆盖退出识别出来并做样本稳健性, 其因果动机在金融经济学文献里有清晰锚点: Heese 等 (2022, Journal of Financial Economics) 证明地方报纸退出本地覆盖会造成监督真空, 进而抬升公司违规, 这正说明以媒体情感为核心解释变量的面板研究必须识别并控制媒体来源消失引入的样本选择偏误——exc 前缀就是对这一识别关切的直接回应。词典法一侧, Du 等 (2022) 提供了本测度的词表来源, 并系统论证了金融文本情感的语言与领域特异性, 这是本项目采用多部中文金融专用词典并做规则消融的方法学依据; Hamilton 等 (2016) 从无标注语料自动归纳领域特定情感词典的工作, 进一步佐证"情感极性是领域依赖的、需专用词表"这一前提。测量与更新层面, Ma 等 (2025) 在中文细粒度投资者情感上构造 CN-FSD 词典、Sun 等 (2025) 探讨把词典知识与中性特征注入预训练语言模型、Nițoi 等 (2023) 用深度学习为央行叙事构造情感指数, 三者共同表明词典法与神经方法互为稳健性、可解释性各有取舍, 支撑本项目"词典法作为可解释、可复现的旁证轨"这一定位。口径铁律: exc 停刊臂与 degonly 规则臂、以及下方三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验; 银行留篇门控遵循 full-only 口径 (2026-06-29), n_articles 之类的行宇宙以 full 轨留篇集为准, ctx/ss 为 conditional-on-full 的稳健性轨。⚠ 非可加分解 (audit MATH-1): 规则消融各相邻级差含否定×程度交互与自归一化分母变更, degonly 只作"主结果对程度规则是否敏感"的定性对照, 不可解读为程度规则的纯贡献。

## VAR: exc_du_2022_score_degonly_ctx

【变体差分】
本列是 ctx 轨的实例。ctx (context) 轨的文本口径 = 标题 prepend 后, 只保留银行别名命中句及其前后各若干句 (context_window.sentence_radius, 默认 ±1 句) 的实体窗口拼接文本, 而非全文正文。因此本列度量的是"围绕目标银行的近场语境"里, Du 等 (2022) 词典在 degonly 规则 (仅程度副词六级加权, 否定翻转与转折增强均关闭) 下打出的带符号情感分, 在剔除疑似覆盖退出媒体后按银行-年求得的均值。它与同族 full 列的唯一差别在文本窗口: full 用整篇正文, ctx 用实体邻域窗口; 与 ss 列的差别则在共现判据的严格程度。ctx 轨相对 full 轨定位为 conditional-on-full 的稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 列照算。政治词权重维度上本列取 canonical polw05, 与政治词权重梯子正交。按口径铁律, ctx 轨与 full/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 同理 exc 停刊臂与 degonly 规则臂与三轨三个维度彼此正交, 不交叉进同一过度识别式。早期试跑 T=2 语料上 ctx 轨可能因窗口收窄而出现零方差退化, 属预期; 生产 T=19 全量语料下正常取值。需强调本列度量对象是 Du 等 (2022) 中文金融词典而非通用情感词表, 领域特异性使其在银行金融科技语境下的极性判定更可靠; 相对 canonical 主情感列 du_2022_tone, 本列既剔除疑似退出覆盖媒体又只保留程度规则, 是"样本×规则"双重扰动下的稳健性对照轨, 唯一目的是佐证主结论方向不被媒体样本框与语言学规则组合所驱动。

## VAR: exc_du_2022_score_degonly_full

【变体差分】
本列是 full 轨的实例, 也是本三轨家族里最贴近"整篇报道情感"的一格。full (full text) 轨的文本口径 = 标题 prepend 后的整篇正文, 不做实体窗口裁剪。因此本列度量的是: 对每篇银行-金融科技报道的全文, 用 Du 等 (2022) 中文金融情感词典、在 degonly 规则 (只施加程度副词六级加权, 否定翻转关闭、转折增强关闭, 极性符号绝不翻转, 政治词权重取 canonical polw05) 下打出的带符号情感分, 在按 detect_defacto_cessation 剔除疑似覆盖退出媒体后, 逐银行-年求得的均值。它与 ctx/ss 列共享完全相同的词典、相同的 degonly 规则组合与相同的 exc 停刊剔除逻辑, 唯一差别是文本窗口取全文。留篇门控为 full-only (2026-06-29): 一篇报道是否算作"一篇银行金融科技报道"只看 full 轨判定, 故 full 轨是行宇宙的锚, ctx/ss 为其子集上的条件测度。口径铁律照旧: full 与 ctx/ss 三轨、exc 与 degonly 两臂各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。相对家族 canonical 主情感列 (无 exc 前缀、full 规则的 du_2022_tone), 本列的双重差分在于既换了样本 (剔停刊媒体) 又换了规则 (仅程度), 因而只作稳健性对照而非主测度。在政治词权重维度上本列固定为 canonical polw05, 政治词权重梯子 {0.0, 0.5, 1.0} 与规则消融梯度刻意正交, 二者不在同一列上交叉; 因此本 full 列可视为"在 full 文本轨、剔除疑似退出媒体、仅施加程度规则、政治词权重 0.5"这一具体设定下的情感读数, 供稳健性 battery 与 canonical 主测度并排比对系数方向与显著性。

## VAR: exc_du_2022_score_degonly_ss

【变体差分】
本列是 ss (same-sentence) 轨的实例。ss 轨的文本口径 = 标题 prepend 后, 只保留"目标银行与金融科技词在同一句内共现"的句子 (同句共现窗, ss_sentence_radius 默认 1), 是三轨里对"银行∧金科同时在场"要求最严的一轨。因此本列度量的是: 在银行与金融科技强同句共现的最窄语境里, Du 等 (2022) 词典在 degonly 规则 (仅程度副词六级加权, 无否定翻转、无转折增强, 政治词权重 canonical polw05) 下的带符号情感分, 在剔除疑似覆盖退出媒体后按银行-年聚合的均值。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True, 与 ctx 的回退公理一致, 并共享 n_articles 分母; 若金融科技 AC 自动机为空则 *_is_fallback 全 True 优雅降级。它与 full/ctx 列的差别只在共现判据的严格程度 (ss 最严、ctx 次之、full 无共现约束), 词典、degonly 规则、exc 停刊剔除三者完全一致。口径铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 稳健性轨。早期试跑 T=2 上因同句共现稀疏, ss 轨可能大量回退或零方差, 属预期退化; 生产 T=19 正常。ss 轨的价值在于把"银行与金融科技真正同句在场"这一最严语义约束加到词典打分之上, 使本列成为三轨里对共现判据最敏感的一格; 它与 ctx 列同享回退语义、只在共现严格度上更进一步, 因此三轨之间构成从无共现约束 (full) 到实体邻域窗 (ctx) 再到严格同句 (ss) 的规格谱, 各自 just-identified 并排, 共同证明主结论对"银行金融科技共现如何界定"这一测量选择不敏感。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Nițoi, M., Pochea, M.-M., & Radu, Ş.-C. (2023). Unveiling the sentiment behind central bank narratives: A novel deep learning index. Journal of Behavioral and Experimental Finance, 38, 100809. https://doi.org/10.1016/j.jbef.2023.100809
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
