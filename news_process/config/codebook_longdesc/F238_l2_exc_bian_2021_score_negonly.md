---
family_id: F238
columns:
- exc_bian_2021_score_negonly_ctx
- exc_bian_2021_score_negonly_full
- exc_bian_2021_score_negonly_ss
unit: 情感倾向分值 (无量纲, self-normalized 落 [-1, 1]), 银行-年层按篇取均值
formula: "exc_bian_2021_score_negonly_track = mean_{a ∈ 非停刊媒体 ∧ target_bank ∧ year}( bian_2021_score_negonly_track(a) ); 篇级 bian_2021_score_negonly = total_score / total_abs_score, 打分时 apply_negation=True、apply_degree=False、apply_adversative=False (仅否定规则), 词典 = Bian et al. (2021) 中文金融情感词典"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (exc_ 均值聚合, 动态发现 score 列对 _is_ceased_media==0 活跃子集按 target_bank/year 取 mean); 停刊标记 _is_ceased_media 由同文件 detect_defacto_cessation 置; 篇级分值来自 news_process/pipeline/sentiment/tone_words.py::_compute_sentiment_with_rules (negonly 变体 apply_negation=True/apply_degree=False/apply_adversative=False, 见 _RULE_ABLATION_VARIANTS)
upstream:
- 22_tone_words.parquet (bian_2021_score_negonly_{full,ctx,ss} 篇级列)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
- attention_media 阶段 (_is_ceased_media 停刊媒体标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
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
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
- doi: "10.1016/j.pacfin.2025.102854"
  title: "The colour of finance words in Chinese"
  authors: "Yao, K., Zheng, Z., & Liu, C."
  year: 2025
  venue: "Pacific-Basin Finance Journal"
  type: "journal"
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
new_dois:
  - "10.1016/j.pacfin.2025.102854"
  - "10.1002/isaf.1549"
---

## CORE

【构念与来源】
本家族度量的是"排除疑似退出覆盖媒体后、以 Bian et al. (2021) 中文金融情感词典的仅否定规则消融变体计算的银行-年层报道语调均值"。它由两层构念叠加而成: 外层是 exc_ 前缀所标记的停刊稳健性口径 (exclusivity / ceased-media robustness), 内层是 bian_2021_score_negonly 所标记的词典法语调测度及其规则消融梯度中的"仅否定"臂。两层各自服务于不同的稳健性目的, 合成后得到一个既排除样本选择偏误、又剥离程度副词与转折规则数值效应的保守语调估计。

外层的 exc_ 口径源于对媒体覆盖退出的诚实处理。以媒体情感为核心自变量的面板研究面临一个内生的样本选择问题: 若某些媒体在样本期内停止对银行-金融科技话题的覆盖, 则依赖全样本媒体计算的语调均值会掺入"覆盖结构随时间漂移"的成分, 而非纯粹的语调变化。detect_defacto_cessation 以"话题覆盖退出"为报纸停刊的保守代理, 对每家媒体计算其在银行-金融科技子集内的 first_year、last_year 与报道量, 将 last_year 明显早于样本末年 (threshold_gap) 的媒体标记为疑似退出, 并可选地与 NPPA 出版许可信息交叉验证 (confirmed / suspected / nppa_only / active 四态仅改报告标签、不收窄排除集)。凡被判入 ceased_all = confirmed ∪ suspected 的媒体, 其报道行在计算 exc_ 系列均值时被整体剔除, 只保留判定为持续活跃媒体的报道。因此 exc_bian_2021_score_negonly 应解读为"若仅信赖持续覆盖该话题的媒体, 语调均值会是多少"的对照量, 而非严格的停刊口径; 它与不排除任何媒体的对应主列互为稳健性、不分主次, 二者各自 just-identified 并排, 禁混进同一 over-identified Hansen J 检验。

内层的 negonly 变体来自词典法规则消融梯度 (rule-ablation ladder)。词典法完整打分时叠加三条语言学规则: 否定翻转 (遇否定词在窗口内翻转情感极性)、程度副词加权 (程度词按倍率放大后续情感强度)、转折加权 (转折连词之后的情感按 boost 系数放大)。仅否定臂在打分函数中令 apply_negation=True、apply_degree=False、apply_adversative=False, 即只保留否定翻转的数值效应, 而把程度倍率锁为 1.0、转折不放大。关键铁律是: 关闭程度与转折并不删除对相应 token 的识别与从句边界重置骨架, 仅锁其数值效应为中性, 从而与全规则共享完全一致的 scoping (否定窗口的有效到达距离不被副作用改变)。篇级分值取 self-normalized 形式 total_score / total_abs_score, 恒落在 [-1, 1], 无匹配词时返回 0.0 中性, 使其尺度与 LLM 投票、BERT 概率等其它情感轨可比。

【方法学与计算】
计算分两步。第一步在 22_tone_words 阶段对每篇报道的三轨文本 (content_full / content_ctx / content_ss) 分词后调用 _compute_sentiment_with_rules, 传入 Bian et al. (2021) 词典与仅否定 flag 组合 (apply_negation=True、apply_degree=False、apply_adversative=False), 得到篇级 bian_2021_score_negonly_{full,ctx,ss}。第二步在 attention_media 阶段, 先由 detect_defacto_cessation 标记 _is_ceased_media, 再由 compute_media_heterogeneity 对 _is_ceased_media == 0 的活跃媒体子集 (df_alive) 动态发现 score 列后按 (target_bank, year) 分组、对篇级分值取算术均值, 前缀 exc_ 后落为面板列。detect_defacto_cessation 本身只做停刊检测与标记、不做聚合, exc_ 均值聚合逻辑在 compute_media_heterogeneity 内。均值分母是该银行-年内活跃媒体的报道篇数, 对语调类 exc_* 列在零篇时按契约保持 NaN (不做计数式零填, 与 n_articles_exc 这类计数列的零填契约区分)。留篇门控沿用 full-only 口径 (2026-06-29): 一篇是否算"银行金融科技报道"只看 full 轨的 LLM 判定, ctx 与 ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。

negonly 与全规则主列 (bian_2021_score) 的差 (full − negonly) 反映程度与转折规则对最终归一化语调的联合净效应, 但因两者各自 self-normalize (Σ|final| 分母随倍率变化), 且否定与程度作用于同一词时倍率乘的是翻转后幅度、含 negation×degree 交互, 该差非可加分解、不可解读为程度或转折的纯因果贡献。审计实测 corr(full, negonly) 高度共线 (接近 1), 判读为"主结果对去掉程度/转折规则不敏感"即越稳健, 而非声称某变体更优。

【文献定位】
词典法情感测度的方法论传统由 Frankel, Jennings, & Lee (2022) 系统对照: 在披露语调场景下, 词典法与机器学习法各有偏差来源, 二者应互为稳健性而非相互替代, 这正是本项目让词典、LLM、BERT 三法并排的先例。中文金融文本的领域特异性由 Du, Huang, Wermers, & Wu (2022) 论证——通用词典移植到中文金融语料会系统性失准, 需构建领域词典; Bian et al. (2021) 与 Ma, Zhang, & Zhang (2025) 分别提供了面向会计金融文本与面向国内投资者的中文细粒度情感词典, 为本家族的词典选择提供了效度支撑。lexicon-based 打分的一般框架及其在经济文本上的表现见 Barbaglia et al. (2025)。否定处理作为词典法最关键的语言学规则, 其范围检测对新闻驱动交易信号的影响由 Pröllochs, Feuerriegel, & Neumann (2016) 专门论证, 直接支撑本变体单独保留否定规则、关闭程度与转折的设计动机。Yao, Zheng, & Liu (2025, Pacific-Basin Finance Journal) 将 robust-MNIR 情感词典构建法首次扩展到非英语语境, 用中国上市公司 MD&A 文本构造中文情感词典, 发现负面词典对收益的预测力显著优于人工构造词典, 与本家族基于人工规则词典 (Bian et al. 2021) 及其否定规则消融变体的方法论议题直接相关。Todd, Bowden, & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献, 专门讨论词典法中否定处理的两类主流策略 (极性反转/固定量位移) 及其局限, 为本家族仅保留否定规则 (negonly) 的消融设计提供最新方法论综述支撑。

## VAR: exc_bian_2021_score_negonly_full

【变体差分】
本列是 full 轨: 篇级文本 = 标题 prepend 到全文正文 (content_full), 覆盖整篇报道内容。在三轨中 full 轨是留篇门控的判定轨 (full-only 口径, 2026-06-29), 即"是否算一篇银行金融科技报道"只由 full 轨的 LLM 判定决定, 因此 full 轨的行宇宙最完整、样本量最大, ctx 与 ss 两轨都是在 full 留篇集内进一步收窄的子集。本列在此基础上再叠加 exc_ 停刊稳健性口径: 仅对判定为持续覆盖银行-金融科技话题的活跃媒体报道取均值, 排除疑似退出覆盖的媒体, 从而剔除因媒体覆盖结构随时间漂移带来的样本选择成分。规则层面, 本列采用仅否定臂 (apply_negation=True、apply_degree=False、apply_adversative=False), 只保留否定翻转的数值效应, 程度倍率锁 1.0、转折不放大, 但保留对程度/转折 token 的识别与从句边界重置以维持一致 scoping。因 full 轨样本最全, 本列在停刊稳健性检验中通常提供最高统计功效, 是 exc_ 系列语调稳健性的主参照轨。均值分母是该银行-年内活跃媒体的报道篇数, 语调类列在零活跃篇时按契约保持 NaN, 不做计数式零填, 与 n_articles_exc 计数列的零填契约严格区分, 避免把"无活跃报道"误记为"语调中性"。它与不排除媒体的对应主列 (bian_2021_score_negonly_full)、与全规则的 exc_bian_2021_score_full、以及 ctx/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 三轨与规则消融梯度均禁混进同一 over-identified Hansen J。仅否定臂之所以有意义, 是因为它把语调对程度副词与转折规则设定的敏感性隔离出来: 若本列与全规则列在回归中给出定性一致的系数, 即证明主结论不被这两条语言学规则的取舍所驱动。

## VAR: exc_bian_2021_score_negonly_ctx

【变体差分】
本列是 ctx 轨: 篇级文本 = 标题 prepend 到实体上下文窗口 (content_ctx), 即围绕目标实体 (银行、金融科技词) 出现位置截取的邻近句窗, 而非整篇正文。相较 full 轨覆盖全文, ctx 轨聚焦于与目标实体直接相关的文本片段, 意在剥离报道中与银行-金融科技无关段落对语调的稀释, 是 full 轨的 conditional-on-full 稳健性测度轨——其行宇宙是 full 留篇集的子集, 语调仅在实体上下文窗内计算。本列同样叠加 exc_ 停刊稳健性口径 (仅对活跃媒体报道取银行-年均值、排除疑似退出覆盖媒体) 与仅否定规则臂 (只保留否定翻转数值效应, 程度锁 1.0、转折不放大, scoping 骨架完整保留)。相较 full 轨, ctx 轨因只在实体上下文窗内取词, 报道内无关段落被剥离, 通常降低无关噪声但也可能因窗口过窄而丢失部分修饰语境, 因此它与 full 轨提供的是同一构念在不同文本范围下的两个估计。均值同样只在活跃媒体子集上计算, 零活跃篇时保持 NaN 不做零填。本列与 full/ss 两轨、与全规则的 exc_bian_2021_score_ctx、与不排除媒体的 bian_2021_score_negonly_ctx 互为稳健性、不分主次, 各自 just-identified 并排, 三轨与规则梯度均禁混进同一 over-identified Hansen J。作为 conditional-on-full 测度轨, 其判定基准始终由 full 轨的留篇门控给出, ctx 轨自身不重新判定一篇是否入样, 只对已入样的报道在更窄文本范围内重算语调。

## VAR: exc_bian_2021_score_negonly_ss

【变体差分】
本列是 ss 轨 (same-sentence 共现轨): 篇级文本 = 标题 prepend 到银行与金融科技词同句共现的句窗 (content_ss, 由 config 的 ss_sentence_radius 控制半径, 默认 ±1 句), 是三轨中判据最严的一轨, 只保留银行∧金融科技在同一句 (及邻近窗) 共现的文本, 意在把语调锚定到明确讨论"该银行的金融科技"的语境上。其回退语义镜像 ctx 轨: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 与 ctx 轨共享 n_articles 分母; 当金融科技 AC 自动机为 None 时 *_is_fallback 全 True 优雅降级。本列同样叠加 exc_ 停刊稳健性口径 (仅活跃媒体报道取均值、排除疑似退出覆盖媒体) 与仅否定规则臂 (保留否定翻转、锁程度倍率 1.0、转折不放大、scoping 骨架完整)。作为 conditional-on-full 轨, 其行宇宙是 full 留篇集的子集。由于同句共现判据最严, ss 轨在语义上最贴近"该银行的金融科技"这一精确语境, 但也最易触发回退、样本最易稀薄, 因此它提供的是三轨中构念最纯、但统计功效通常最低的语调估计。均值只在活跃媒体子集上计算, 零活跃篇时保持 NaN、不做计数式零填。本列与 full/ctx 两轨、与全规则的 exc_bian_2021_score_ss、与不排除媒体的 bian_2021_score_negonly_ss 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。三轨口径的这一严格性排序 (full 最全、ctx 居中、ss 最严) 使研究者可沿文本范围维度做规格稳健性检验, 而 exc_ 停刊剔除与 negonly 规则消融则分别沿样本选择维度与语言学规则维度提供正交的稳健性梯子。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Yao, K., Zheng, Z., & Liu, C. (2025). The colour of finance words in Chinese. Pacific-Basin Finance Journal. https://doi.org/10.1016/j.pacfin.2025.102854
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
