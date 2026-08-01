---
family_id: F246
columns:
- exc_du_2022_score_negdeg_ctx
- exc_du_2022_score_negdeg_full
- exc_du_2022_score_negdeg_ss
unit: 无量纲情感倾向得分 (词典法, 自归一化区间 [-1, 1])
formula: "exc_du_2022_score_negdeg{track} = mean_over(article ∈ bank-year, media ∉ ceased_set) du_2022_score_negdeg{track}; 其中 du_2022_score_negdeg = (Σ pos_final - Σ neg_final)/(Σ|pos_final|+Σ|neg_final|), 规则集 = 否定翻转 ON + 程度副词 ON + 转折 OFF"
producer: news_process/pipeline/panel/attention_media.py (exc_* 动态发现聚合; 上游文章列 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores)
upstream:
- 22_tone_words.parquet (du_2022_score_negdeg_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- detect_defacto_cessation (ceased_set = confirmed ∪ suspected 停刊代理集)
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"剔除疑似退出覆盖媒体后、以 Du et al. (2022) 中文金融情感词典的否定+程度消融变体所度量的银行-金科报道语气"这一 bank-year 面板测度。三列 exc_du_2022_score_negdeg_full / _ctx / _ss 是同一构念在三条文本轨上的并排实现: 分子分母都由词典法逐篇打分, 再在银行-年格内对"存活媒体"子样本取算术均值。测度落在自归一化区间 [-1, 1], 正值表示存活媒体对该银行金科议题的报道语气偏正面, 负值偏负面, 零附近表示褒贬相抵或语料稀薄。它同时承担两重身份: 一是把 du_2022 词典的规则消融梯度 (rule-ablation ladder) 延伸到面板端, 二是把"媒体退出覆盖"这一样本选择维度物化为一条保守稳健性轴, 供 Stata 端做系数稳定性对照。

【方法学与计算】
计算分三层。第一层是文章级词典打分, 由 tone_words.py::compute_dict_scores 完成: 对每篇报道分别在 full/ctx/ss 三轨文本上跑 Du et al. (2022) 词典的正负词匹配, 得到 du_2022_score_negdeg{track}。这里的 negdeg 是消融梯度里的 L2 组合, 即语言学三规则中"否定翻转"与"程度副词"两条开启、"转折"一条关闭 (等价于完整规则集减去转折规则)。每个消融变体各自 self-normalize, 分母 Σ|final| 随所启用规则变动, 因此相邻级差并非某条规则的纯边际贡献, 只能作 ablation 稳健性对照, 论文披露须报四级相关系数与逐级变号占比、口径表述为"定性不变"。第二层是停刊代理检测: detect_defacto_cessation 以"话题覆盖退出"作为报纸停刊的保守代理, 对每家媒体在银行-金科子样本内统计首末覆盖年与报道数, 把末覆盖年早于样本末年减阈值 (默认 gap=2) 且累计报道数不少于十篇者标记为疑似退出, 再与 NPPA 出版状态注销/停办/休刊名单交叉验证得 confirmed 与 suspected; 排除集 ceased_set = confirmed ∪ suspected, 即未经 NPPA 证实的疑似退出也一并保守剔除。第三层是面板聚合: attention_media.py 的 exc_* 动态发现循环对 _is_ceased_media==0 的存活子样本按 target_bank×year 分组, 对 du_2022_score_negdeg{track} 取均值, 写出 exc_ 前缀列 (加权变体、_mw_/_idf_ 变体与已单列处理的 llm_vote_score 在该循环内被显式跳过, 故本族只含无 idf/无 mw 的纯计数消融口径)。缺列或空子样本时该轨优雅跳过, 情感类 exc_* 列按契约保持 NaN 而非零填 (零填只适用于 n_articles_exc 等计数列)。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算作银行金科报道只看 full 轨 LLM 判定, ctx/ss 轨为 conditional-on-full 的稳健性测度, 行宇宙是 full 留篇集的子集。

【文献定位】
词典本体源自 Du et al. (2022, Review of Finance) 构建的领域特定中文金融情感词典, 该文证明通用词典迁移到中文金融文本会显著失真、领域与语言特异性词表能实质提升情感抽取效度, 是本族打分器的方法学与词表来源。词典法在中文金融文本上的持续演进可参 Ma et al. (2025) 面向国内投资者的细粒度情感词典与 Sun et al. (2025) 把词典知识与中性特征注入预训练语言模型的融合路线, 两者都印证"领域词表 + 规则修饰"相较纯计数的增量价值, 为本族保留否定/程度/转折规则消融梯度提供支撑; 情感词表的无监督归纳方法学则可追溯至 Hamilton et al. (2016)。剔除退出媒体这一稳健性设计的因果依据来自 Heese et al. (2022, Journal of Financial Economics): 地方报纸关停会造成企业监督真空、公司违规上升, 因此以媒体情感为核心变量的面板必须识别并保守剔除因媒体来源消失引入的样本选择偏误——这正是 exc_ 前缀存在的理由。须强调本族三轨与整个消融梯度各自 just-identified 并排、互为稳健性不分主次, 严禁把不同轨或不同消融变体混进同一 over-identified Hansen J 过度识别检验。 近期文献可从两个环节进一步锚定本族。否定通道方面, Naldi 与 Petroni (2023) 以人工构造测试集提出一套专门评估词典法情感工具否定检测与处理能力的方法, 实证发现各工具在否定处理上的表现差异显著, 说明否定是词典法内部可被单独测量、单独失效的模块, 为 negdeg 变体保留否定翻转、并把该规则的开/关单列一档提供了最贴近的方法学参照; 迁移边界在于该文是英文通用领域 (非金融) 的工具准确率评测, 本族并不评测否定检测准确率, 而是把规则开关作为面板测度的一条并排稳健性臂, 且 negdeg 同时启用的程度副词一条在该文中并无对应。ceased_set 剔除环节则可由 Cziraki 与 Gider (2024) 补充现实动机: 该工作论文以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 表明媒体退出覆盖是真实且有经济后果的样本组成变化。须诚实指出其停刊判定来自美国本地报纸的外部真实停刊事件数据、DV 为本地股票交易活动, 而本族 ceased_set 是 detect_defacto_cessation 自语料内部推断的「疑似退出覆盖」保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 用途亦仅限稳健性子样本而非识别冲击; 该文为未经同行评审的工作论文, 只作动机性佐证。
## VAR: exc_du_2022_score_negdeg_ctx

【变体差分】
本列是 negdeg 消融变体在 ctx (context) 轨上、剔除疑似退出媒体后的银行-年均值。ctx 轨文本 = 标题 prepend 后拼接"目标银行实体上下文窗口", 即只保留围绕银行实体命中位置的局部窗口而非整篇正文, 因此相较 full 轨语气打分聚焦于银行被点名处的措辞, 抑制了整篇长文中与银行无关段落的语气噪声。与家族内 full/ss 两轨相比, 本列的唯一差分维度是文本轨 (ctx), 消融规则集 (否定 ON + 程度 ON + 转折 OFF)、词典 (du_2022)、聚合口径 (存活媒体子样本均值) 与滞后 (无) 全部相同。三轨互为稳健性、不分主次: ctx 轨在门控上是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集; 当某银行-年在存活媒体子样本内无 ctx 命中时该格保持 NaN 而非零填。铁律: ctx 轨严禁与 full/ss 轨或任何其他消融变体混入同一 over-identified Hansen J。ctx 轨与 full 轨的经济含义差异在于, 一篇既谈银行又展开大量宏观背景或行业综述的长报道, 在 full 轨会把全篇语气纳入均值, 而在 ctx 轨只截取银行实体命中窗口, 因此当整篇基调与银行段落基调背离时两轨会给出不同符号, 这正是把 ctx 作为独立稳健性轨的价值所在; 研究者应把两轨系数并排展示、以定性一致性而非相关系数高低判定稳健。在早期试跑 T=2 语料上 ctx 轨可能出现零方差退化, 属预期现象, 生产 T=19 语料下正常。

## VAR: exc_du_2022_score_negdeg_full

【变体差分】
本列是 negdeg 消融变体在 full 轨上、剔除疑似退出媒体后的银行-年均值, 是本家族在留篇门控意义上的基准轨。full 轨文本 = 标题 prepend + 完整正文, 因此打分覆盖整篇报道的全部褒贬用词, 是三轨中信息量最全、也最易混入与银行无关段落语气的一轨。按 full-only 门控 (2026-06-29), 一篇报道是否算作银行金科报道只由 full 轨 LLM 判定裁决, 故 full 轨的留篇集是 ctx/ss 两轨行宇宙的上界。与家族内 ctx/ss 两列相比, 本列唯一差分是文本轨 (full); 消融规则集 (否定 ON + 程度 ON + 转折 OFF, 即完整规则减转折)、词典 (du_2022)、存活媒体子样本聚合、无滞后全部一致。相对同轨的完整规则 canonical (du_2022_score{track}), 本列关闭了转折规则, 属规则消融梯度的一级对照, 用于验证转折处理对结论的定性影响; 相对未剔除媒体的全样本口径, 本列剔除了 ceased_set 中疑似退出覆盖的媒体, 属样本选择稳健性对照。三轨与各消融级各自 just-identified 并排, 禁混同一 over-identified Hansen J。full 轨的另一层作用是充当同轨完整规则口径与其余消融变体之间的锚: 由于只有 full 轨承担留篇判定, 论文正表通常以 full 轨报主结果、以 ctx/ss 轨与其余消融级作附表稳健性对照, 若剔除退出媒体后 full 轨系数符号与显著性维持不变, 即可主张媒体退出选择偏误未驱动结论。需再次提醒读者本列口径为"疑似退出覆盖"的保守剔除, 不可在论文中表述为严格停刊, 且情感类 exc_* 列在空子样本格按契约保持 NaN 而非零填, 与兄弟计数列 n_articles_exc 的零填口径刻意区分。空子样本格按契约保持 NaN。

## VAR: exc_du_2022_score_negdeg_ss

【变体差分】
本列是 negdeg 消融变体在 ss (same-sentence) 轨上、剔除疑似退出媒体后的银行-年均值。ss 轨文本 = 标题 prepend + "目标银行与金融科技词同句共现 ±N 窗" (N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义最严、最贴近"银行∧金科"共现语境的一轨, 因此语气打分只反映银行与金科议题真正同句讨论处的措辞。ss 轨采用镜像 ctx 的回退语义: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 共享 n_articles 分母; 若 FINTECH_AC 缺失则 *_is_fallback 全 True 优雅降级。与家族内 full/ctx 两列相比, 本列唯一差分是文本轨 (ss) 及其同句判据与回退规则, 消融规则集、词典、存活媒体子样本聚合、无滞后全部相同。三轨互为稳健性、不分主次, 门控上 ss 为 conditional-on-full 的稳健性测度轨, 行宇宙是 full 留篇集的子集; 空存活子样本格保持 NaN。铁律: ss 轨严禁与 full/ctx 轨或其他消融变体混入同一 over-identified Hansen J。ss 轨相较 ctx 轨进一步收紧了语境: ctx 只要求落在银行实体窗口, ss 则额外要求银行与金融科技词在同一句 (或 ±N 句窗) 共现, 因此 ss 轨最能排除"文章仅顺带提及银行、金科议题另起段落"这类弱相关噪声, 但代价是命中篇数最少、方差最大、回退频率最高, 研究者解读 ss 轨系数时须一并汇报回退占比与有效篇数。在早期试跑 T=2 上 ss 轨可能零方差退化属预期, 生产 T=19 正常。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
