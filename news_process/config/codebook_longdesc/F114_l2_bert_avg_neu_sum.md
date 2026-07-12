---
family_id: F114
columns:
- bert_avg_neu_sum_ctx
- bert_avg_neu_sum_full
- bert_avg_neu_sum_ss
unit: 无量纲概率质量求和 (中性类累积概率总量, extensive/篇数级, 随报道量增长)
formula: "bert_avg_neu_sum{track} = mean_{b in 三分类BERT模型集} ( {b}_neu_sum{track} ); 其中 {b}_neu_sum{track} = Σ_{该 bank-year 落在 track 上的报道} P_b(neutral | 报道); _safe_mean 缺列优雅返回 NaN"
producer: news_process/pipeline/panel/geography.py
upstream:
- 23_tone_berts.parquet ({b}_neu_sum{track} 逐模型中性类求和)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1146/annurev-financial-112923-020503
  type: journal
  authors: Eisfeldt, A. L., & Schubert, G.
  year: 2025
  title: "Generative AI and finance"
  venue: Annual Review of Financial Economics
  vol: 17
  issue: 1
  pages_or_artno: 363-393
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
本家族测度 bert_avg_neu_sum 刻画一家银行在给定年度的媒体报道中, 被 BERT 类金融情感分类器判为"中性" (既非明确利好、亦非明确利空) 的概率质量累积总量, 并在多个三分类 BERT 模型之间取跨模型均值。其构念定位与常见的正/负情感极性测度互补: 正、负两侧刻画情绪方向与强度, 而中性侧刻画的是报道语义的"未表态/含糊/程序化"成分。在银行金融科技这一研究场景里, 中性报道往往对应例行公告、产品罗列、监管流程叙述等不含明确价值判断的文本, 因此中性概率的累积量能够近似衡量一家银行年度报道里"信息含量偏低、口径中立"部分的规模。之所以采用求和 (sum) 而非取均值 (mean) 聚合, 是要保留 extensive (外延、篇数级) 语义: 该列的取值随一家银行当年被判中性的报道数量与中性置信度共同增长, 是一个规模量而非强度量, 与同族的 bert_avg_neu (逐篇中性概率的算术平均, intensive 强度量) 构成"总量—强度"一对孪生。

数据来源链条为: 上游 stage 14 (materialize_ctx) 物化三轨文本 content_full / content_ctx / content_ss; stage 23 (tone_berts) 用若干金融 BERT 模型对每篇报道逐篇打出正/负/中三类概率, 并在 bank-year 层把逐篇中性概率按报道求和得到逐模型的 {b}_neu_sum{track}; 最终在 producer geography.py 的三轨综合指标段, 用 _safe_mean 对"具备中性类的三分类 BERT 模型集"逐模型的中性求和列取跨模型均值, 落为 bert_avg_neu_sum{track}。中性类只对三分类模型有定义 (源码注释 fix(omni-g-geography-06): pos/neg/neu 同域 = 三分类模型), 二分类 (伯努利) 模型没有中性类, 不进入本家族的跨模型均值集合。_safe_mean 对缺列优雅返回 NaN, 因此在 golden 重生前若某逐模型列尚未落盘, 综合列退化为 NaN 而非崩溃。

【方法学与计算】
逐篇打分沿用 BERT 双向 Transformer 编码器的序列分类范式 (Devlin et al., 2019), 在金融文本上以 FinBERT 类专用模型完成三分类 softmax 输出 (Huang et al., 2023)。中性类概率是 softmax 三维输出中对应"中性/不确定"维度的分量, 天然落在 [0,1] 且三维之和为 1。逐篇中性概率在 bank-year 内按报道求和即得 {b}_neu_sum; 该量的量纲是"篇数 × 平均中性概率", 因此与报道体量正相关。跨模型均值这一步遵循项目一贯的多模型互为稳健性口径: 三分类 BERT 各模型的逐模型中性求和列并排、地位对等, 跨模型均值只是把它们汇成一个便于建模的综合信号, 但在识别层, 各模型的 per-model 子测度各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同模型 (或不同轨道) 的中性列混进同一 over-identified 的 Hansen J 过度识别检验。per-model 独立降级: 某个 BERT 模型缺席只掉它自身的中性列, 不连坐其他模型, 也不同于 co-primary 嵌入的 both-or-neither 联动。中性侧作为一个刻意保留的语义维度而非噪声, 与近年把"中性特征"显式纳入金融情感建模的做法一致 (Sun et al., 2025)。

【文献定位】
金融文本情感测度的方法学谱系可归为词典法与机器学习/深度学习法两支。Loughran and McDonald (2011) 确立了面向金融文本的领域词典范式, 并在 Loughran and McDonald (2016) 的综述中系统梳理了文本分析在会计金融中的效度边界; Tetlock (2007) 则较早论证了媒体语气 (尤其悲观/负面成分) 对市场的预测含义, 为"把报道情感聚合成公司—时间面板信号"提供了经典模板。相较词典法, 以 BERT 为代表的预训练语言模型能捕捉否定、程度、语境依赖等词典难以刻画的结构, Frankel et al. (2022) 在顶刊层面直接比较了机器学习与词典法在披露情感度量上的相对优劣, 支持在主测度之外并置深度学习测度作为互为稳健性的一轨。Eisfeldt and Schubert (2025) 从更宏观的视角综述了生成式 AI 与深度文本模型在金融研究中的角色。本家族正是这一谱系中的 BERT 侧中性维度: 它既不是极性方向信号, 也不是词典法产物, 而是三分类 BERT 中性类的跨模型、跨报道累积量, 与项目内的 LLM 三家投票情感、六词典法情感各自独立并排、互为稳健性, 三法之间不分主次、不混同一过度识别检验。

## VAR: bert_avg_neu_sum_full

【变体差分】
本列为 full 轨版本, 是本家族在留篇门控口径下的主锚轨。full 轨文本 = 标题 prepend 到全文正文 (content_full), 即在原始正文前拼接标题后交给三分类 BERT 逐篇打分, 再按 bank-year 求和、跨模型取均值。按 2026-06-29 起生效的 full-only 留篇门控口径, 一篇报道是否被计入"一篇银行金科报道"的留篇集, 只由 llm_verified_full == True 决定; 因此 full 轨的行宇宙 = 全部留篇报道, 是 ctx / ss 两条 conditional-on-full 轨的母集。相应地, full 轨的中性求和分母覆盖面最全, 数值规模在三轨中通常最大, 也最接近"该银行当年全部合格报道中被判中性的总概率质量"这一构念本意。与 ctx / ss 相比, full 轨不做实体窗口或同句共现的文本裁剪, 保留报道的完整叙述, 因而对例行公告、监管流程等长而中性的文本更敏感, 中性累积量更充分地反映了报道体量。full 轨与 ctx 轨、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J; 建模时三轨分别进入各自的规格, 不在同一右手侧并列。作为 extensive 总量列, 本列取值随报道量与中性置信度共同上升, 应与同轨的 bert_avg_neu (逐篇均值、intensive 强度量) 配合解读, 避免把规模效应误读为语气变化。逐模型层面同样遵循 per-model 独立降级: 缺席某个三分类 BERT 模型只影响其自身在 full 轨的中性求和列, 不连坐其余模型, 也不触发 co-primary 嵌入那类 both-or-neither 的联动置空。

## VAR: bert_avg_neu_sum_ctx

【变体差分】
本列为 ctx 轨版本, 文本口径 = 标题 prepend 到"实体上下文窗口" (content_ctx), 即只保留围绕目标银行实体附近的语境片段 (标题 + 实体窗口) 交给三分类 BERT 逐篇打分, 再按 bank-year 求和、跨模型取均值。相对于 full 轨保留全文, ctx 轨把注意力收窄到与目标银行直接相邻的叙述, 剔除了远离实体的背景段落, 因此对"这家银行本身被如何中性化描述"更聚焦, 但也牺牲了对例行长文中性成分的覆盖。按 full-only 门控, ctx 轨是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, per-track 中性求和在该子集上逐轨自算, 分母严格取本轨自身口径, 不借 full 轨分母。full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨中性列混进同一 over-identified 的 Hansen J; ctx 轨在主结论中充当对 full 轨的规格稳健性对照, 用以检验中性总量测度是否稳健于文本窗口的收窄。作为 extensive 总量列, 本列同样随本轨报道量与中性置信度共同增长; 在开发规模 (T 小) 语料上, 窗口收窄可能使部分 bank-year 的中性求和退化为很小甚至零方差, 属预期的规模退化而非缺陷, 需在生产语料上重估。逐模型层面 per-model 独立降级: 缺席某个三分类 BERT 只影响其自身在本轨的中性列, 不连坐其他模型。

## VAR: bert_avg_neu_sum_ss

【变体差分】
本列为 ss 轨版本, 文本口径 = 标题 prepend 到"银行与金融科技同句共现窗口" (content_ss), 即只保留目标银行与金融科技词在同一句 (含 ±N 句半径, 由 filtering.yaml 的 ss_sentence_radius 控制, 默认 1) 共现的片段交给三分类 BERT 逐篇打分, 再按 bank-year 求和、跨模型取均值。ss 轨是三轨中语义最窄的一轨, 专门聚焦"银行 × 金融科技"这一交叉语境下报道的中性成分, 因此最贴近本项目银行金科主题的构念内核, 但覆盖面最小。关键的回退语义 (ss 镜像 ctx): 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文 body, 同时 ss_is_fallback 置 True, 并与其它轨共享 n_articles 分母; 若金融科技词表 (FINTECH_AC) 整体为 None, 则 *_is_fallback 全 True 做优雅降级。因此本列在共现稀疏的样本上会大量回退到全文口径, 其取值在退化区间会趋近 full 轨, 解读时须结合 ss_is_fallback 判断回退比例。按 full-only 门控, ss 轨同为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 中性求和逐轨自算、分母取本轨口径。full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J; ss 轨用作对主题相关性最强口径的规格稳健性检验。作为 extensive 总量列, 本列亦随本轨报道量增长, 在小样本上易出现零方差退化, 属预期。

<!-- rendered-citations:begin -->
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Eisfeldt, A. L., & Schubert, G. (2025). Generative AI and finance. Annual Review of Financial Economics, 17(1), 363-393. https://doi.org/10.1146/annurev-financial-112923-020503
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
<!-- rendered-citations:end -->
