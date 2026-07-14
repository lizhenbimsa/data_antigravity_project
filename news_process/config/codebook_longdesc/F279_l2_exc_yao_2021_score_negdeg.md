---
family_id: F279
columns:
- exc_yao_2021_score_negdeg_ctx
- exc_yao_2021_score_negdeg_full
- exc_yao_2021_score_negdeg_ss
unit: 无量纲情感倾向得分 (词典法, 自归一化区间 [-1, 1])
novelty_exempt_rationale: "该家族是 yao_2021 词典规则消融梯度 (negdeg, 否定+程度) 叠加 exc_ 停刊媒体排除的技术变体, 非独立新构念, 其测度定义的学术依据已在母族词典文献 (Du et al. 2022 Review of Finance 等) 中给出, 无需单独追新 2023+ 文献。"
formula: "exc_yao_2021_score_negdeg{track} = mean_over(article ∈ bank-year, media ∉ ceased_set) yao_2021_score_negdeg{track}; 其中 yao_2021_score_negdeg = (Σ pos_final - Σ neg_final)/(Σ|pos_final|+Σ|neg_final|), 规则集 = 否定翻转 ON + 程度副词 ON + 转折 OFF"
producer: news_process/pipeline/panel/attention_media.py (exc_* 动态发现聚合; 上游文章列 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores)
upstream:
- 22_tone_words.parquet (yao_2021_score_negdeg_full / _ctx / _ss)
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: China Journal of Accounting Studies
  vol: 7
  issue: 3
  pages_or_artno: 407-437
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
本家族刻画的是"剔除疑似退出覆盖媒体后、以姚加权等 (2021) 金融领域中文情绪词典 (yao_2021) 的否定加程度消融变体所度量的银行-金科报道语气"这一 bank-year 面板测度。三列 exc_yao_2021_score_negdeg_full / _ctx / _ss 是同一构念在三条文本轨上的并排实现: 分子分母都由词典法逐篇打分, 再在银行-年格内对"存活媒体"子样本取算术均值。测度落在自归一化区间 [-1, 1], 正值表示存活媒体对该银行金科议题的报道语气偏正面, 负值偏负面, 零附近表示褒贬相抵或语料稀薄。它同时承担两重身份: 一是把 yao_2021 词典的规则消融梯度 (rule-ablation ladder) 延伸到面板端, 二是把"媒体退出覆盖"这一样本选择维度物化为一条保守稳健性轴, 供 Stata 端做系数稳定性对照。之所以选用姚加权等 (2021) 而非其它词典, 是因为项目刻意并排六部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran), 让最终结论不被任一单一词表的构念选择驱动; yao_2021 是其中一部, 与其余五部各自 just-identified 并排, 互为稳健性、不分主次。

【方法学与计算】
计算分三层。第一层是文章级词典打分, 由 tone_words.py::compute_dict_scores 完成: 对每篇报道分别在 full/ctx/ss 三轨文本上跑 yao_2021 词典的正负词匹配, 得到 yao_2021_score_negdeg{track}。这里的 negdeg 是消融梯度里的一个二规则组合, 即语言学三规则中"否定翻转"与"程度副词"两条开启、"转折"一条关闭 (等价于完整规则集减去转折规则)。每个消融变体各自 self-normalize, 分母 Σ|final| 随所启用规则变动, 因此相邻级差并非某条规则的纯边际贡献, 与完整规则口径高度共线 (盘上实证相关系数约 0.99), 只能作 ablation 稳健性对照, 论文披露须报四级相关系数与逐级变号占比、口径表述为"定性不变", 严禁把两级差解读为该规则的可加分解。第二层是停刊代理检测: detect_defacto_cessation 以"话题覆盖退出"作为报纸停刊的保守代理, 对每家媒体在银行-金科子样本内统计首末覆盖年与报道数, 把末覆盖年早于样本末年减阈值 (默认间隔为二年) 且累计报道数不少于十篇者标记为疑似退出, 再与出版监管部门的注销、停办、休刊名单交叉验证得 confirmed 与 suspected; 排除集 ceased_set = confirmed ∪ suspected, 即未经监管名单证实的疑似退出也一并保守剔除, 故列名前缀 exc 意为 excluding ceased media。第三层是面板聚合: attention_media.py 的 exc_* 动态发现循环对未被标记为退出媒体的存活子样本按 target_bank×year 分组, 对 yao_2021_score_negdeg{track} 取均值, 写出 exc_ 前缀列 (加权变体、mw 变体与 idf 变体, 以及已单列处理的 llm_vote_score, 在该循环内被显式跳过, 故本族只含无 idf、无 mw 的纯计数消融口径)。缺列或空子样本时该轨优雅跳过, 情感类 exc_* 列按契约保持 NaN 而非零填 (零填只适用于 n_articles_exc 等计数列)。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算作银行金科报道只看 full 轨 LLM 判定, ctx/ss 轨为 conditional-on-full 的稳健性测度, 行宇宙是 full 留篇集的子集。

【文献定位】
词典本体源自姚加权等 (2021) 构建的金融领域中文情绪词典, 其思路与 Du et al. (2022, Review of Finance) 一脉相承: 后者系统证明通用词典迁移到中文金融文本会显著失真、领域与语言特异性词表能实质提升情感抽取效度, 是整套中文金融词典法 (含 yao_2021) 的方法学依据与顶刊锚; 中文会计文本可读性度量的相关方法学证据另见 Xu, Yao and Chen (2019), 二者共同勾勒出"中文金融文本领域特异性测度需专门构建规则或词表"这一更宽泛的方法学取向, 但该文作者与本族词典作者并非同一人, 此处仅作方法学脉络参照, 不作同一作者归属主张。词典法在中文金融文本上的持续演进可参 Ma et al. (2025) 面向国内投资者的细粒度情感词典与 Sun et al. (2025) 把词典知识与中性特征注入预训练语言模型的融合路线, 两者都印证"领域词表加规则修饰"相较纯计数的增量价值, 为本族保留否定、程度、转折规则消融梯度提供支撑; 情感词表的无监督归纳方法学则可追溯至 Hamilton et al. (2016)。词典法与机器学习、人工标注三条测量路线之间的效度权衡由 van Atteveldt et al. (2021) 与 Frankel et al. (2022, Management Science) 系统评估, 后者确立了三方法互为稳健性的先例, 直接支撑本项目把词典、LLM、BERT 三法及词典内各消融梯度并排为稳健性轴而非唯一真值的设计。须强调本族三轨与整个消融梯度各自 just-identified 并排、互为稳健性不分主次, 严禁把不同轨或不同消融变体混进同一 over-identified Hansen J 过度识别检验。

## VAR: exc_yao_2021_score_negdeg_ctx

【变体差分】
本列是 yao_2021 词典 negdeg 消融变体在 ctx (context) 轨上、剔除疑似退出媒体后的银行-年均值。ctx 轨文本 = 标题 prepend 后拼接"目标银行实体上下文窗口", 即只保留围绕银行实体命中位置的局部窗口而非整篇正文, 因此相较 full 轨语气打分聚焦于银行被点名处的措辞, 抑制了整篇长文中与银行无关段落的语气噪声。与家族内 full/ss 两轨相比, 本列的唯一差分维度是文本轨 (ctx), 消融规则集 (否定翻转 ON + 程度副词 ON + 转折 OFF)、词典 (yao_2021)、聚合口径 (存活媒体子样本均值) 与滞后 (无) 全部相同。三轨互为稳健性、不分主次: ctx 轨在门控上是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集; 当某银行-年在存活媒体子样本内无 ctx 命中时该格保持 NaN 而非零填。铁律: ctx 轨严禁与 full/ss 轨或任何其他消融变体混入同一 over-identified Hansen J。ctx 轨与 full 轨的经济含义差异在于, 一篇既谈银行又展开大量宏观背景或行业综述的长报道, 在 full 轨会把全篇语气纳入均值, 而在 ctx 轨只截取银行实体命中窗口, 因此当整篇基调与银行段落基调背离时两轨会给出不同符号, 这正是把 ctx 作为独立稳健性轨的价值所在; 研究者应把两轨系数并排展示、以定性一致性而非相关系数高低判定稳健。在 T=2 试跑语料上 ctx 轨可能出现零方差退化, 属预期现象, 生产 T=18 语料下正常。

## VAR: exc_yao_2021_score_negdeg_full

【变体差分】
本列是 yao_2021 词典 negdeg 消融变体在 full 轨上、剔除疑似退出媒体后的银行-年均值, 是本家族在留篇门控意义上的基准轨。full 轨文本 = 标题 prepend + 完整正文, 因此打分覆盖整篇报道的全部褒贬用词, 是三轨中信息量最全、也最易混入与银行无关段落语气的一轨。按 full-only 门控 (2026-06-29), 一篇报道是否算作银行金科报道只由 full 轨 LLM 判定裁决, 故 full 轨的留篇集是 ctx/ss 两轨行宇宙的上界。与家族内 ctx/ss 两列相比, 本列唯一差分是文本轨 (full); 消融规则集 (否定翻转 ON + 程度副词 ON + 转折 OFF, 即完整规则减转折)、词典 (yao_2021)、存活媒体子样本聚合、无滞后全部一致。相对同轨的完整规则 canonical (yao_2021_score{track}), 本列关闭了转折规则, 属规则消融梯度的一级对照, 用于验证转折处理对结论的定性影响; 相对未剔除媒体的全样本口径, 本列剔除了 ceased_set 中疑似退出覆盖的媒体, 属样本选择稳健性对照。三轨与各消融级各自 just-identified 并排, 禁混同一 over-identified Hansen J。full 轨的另一层作用是充当同轨完整规则口径与其余消融变体之间的锚: 由于只有 full 轨承担留篇判定, 论文正表通常以 full 轨报主结果、以 ctx/ss 轨与其余消融级作附表稳健性对照, 若剔除退出媒体后 full 轨系数符号与显著性维持不变, 即可主张媒体退出选择偏误未驱动结论。需再次提醒读者本列口径为"疑似退出覆盖"的保守剔除, 不可在论文中表述为严格停刊, 且情感类 exc_* 列在空子样本格按契约保持 NaN 而非零填, 与兄弟计数列 n_articles_exc 的零填口径刻意区分。

## VAR: exc_yao_2021_score_negdeg_ss

【变体差分】
本列是 yao_2021 词典 negdeg 消融变体在 ss (same-sentence) 轨上、剔除疑似退出媒体后的银行-年均值。ss 轨文本 = 标题 prepend + "目标银行与金融科技词同句共现 ±N 窗" (N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义最严、最贴近"银行∧金科"共现语境的一轨, 因此语气打分只反映银行与金科议题真正同句讨论处的措辞。ss 轨采用镜像 ctx 的回退语义: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 共享 n_articles 分母; 若 FINTECH_AC 缺失则 *_is_fallback 全 True 优雅降级。与家族内 full/ctx 两列相比, 本列唯一差分是文本轨 (ss) 及其同句判据与回退规则, 消融规则集 (否定翻转 ON + 程度副词 ON + 转折 OFF)、词典 (yao_2021)、存活媒体子样本聚合、无滞后全部相同。三轨互为稳健性、不分主次, 门控上 ss 为 conditional-on-full 的稳健性测度轨, 行宇宙是 full 留篇集的子集; 空存活子样本格保持 NaN。铁律: ss 轨严禁与 full/ctx 轨或其他消融变体混入同一 over-identified Hansen J。ss 轨相较 ctx 轨进一步收紧了语境: ctx 只要求落在银行实体窗口, ss 则额外要求银行与金融科技词在同一句 (或 ±N 句窗) 共现, 因此 ss 轨最能排除"文章仅顺带提及银行、金科议题另起段落"这类弱相关噪声, 但代价是命中篇数最少、方差最大、回退频率最高, 研究者解读 ss 轨系数时须一并汇报回退占比与有效篇数。在 T=2 试跑上 ss 轨可能零方差退化属预期, 生产 T=18 正常。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
