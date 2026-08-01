---
family_id: F267
novelty_exempt_rationale: "exc_loughran_score_degadv 是'停刊代理媒体剔除'(exc_) 与'L&M词典语言学规则消融'(degadv) 两重衍生变体家族, 测度定义完全依据母族 loughran/L&M 词典原始文献与项目规则消融 SSOT (rule ablation powerset), 非独立新构念, 无需追加新颖文献。"
columns:
- exc_loughran_score_degadv_ctx
- exc_loughran_score_degadv_full
- exc_loughran_score_degadv_ss
unit: 情感倾向分值 (无量纲, 自归一化; 停刊代理剔除子样本上的 bank-year 均值)
formula: "exc_loughran_score_degadv{track} = mean over articles a of loughran_score_degadv{track}(a), for a in media outlets with _is_ceased_media==0, grouped by (target_bank, year); article-level loughran_score_degadv = 词典逐词计分, 仅启用程度副词 (deg) 与转折 (adv) 两条语言学规则、关闭否定翻转 (neg)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_robustness (C.4 动态发现块)
upstream:
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- 22_tone_words.parquet (loughran_score_degadv_full/_ctx/_ss 文章级)
- 40_panel_export_main (attention_media 停刊代理检测 detect_defacto_cessation)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个双层复合测度: 底层是 Loughran & McDonald 词典 (以下简称 L&M 词典) 在单篇报道上的情感原始得分 (loughran_score), 且专取"程度副词 + 转折"这一条语言学规则消融变体 (后缀 degadv); 上层则把该文章级得分按 bank-year 聚合, 但只在"疑似停刊媒体剔除后"的稳健性子样本上求均值 (前缀 exc)。因此每个数值回答的问题是: 在剔除疑似退出覆盖的媒体来源之后, 某银行某年被报道文本用 L&M 中文主译词典 (loughran 别名, 第六部词典) 在启用程度副词放缩与转折翻转、但关闭否定翻转的规则组合下所测得的整体情感基调是偏正还是偏负。构念既承载"情感极性测量", 又承载两重稳健性设计 (语言学规则的消融梯度、媒体存活的样本敏感性)。

词典来源方面, L&M 词典源自 Loughran & McDonald (2011) 在 Journal of Finance 上提出的金融文本情感词表——他们发现通用 Harvard-IV 心理学词表把大量金融语境中中性的词误判为负面, 遂从 10-K 语料重建了金融专用的正面/负面词类, 这一词表成为会计与金融文本分析领域的事实标准。本项目使用其中文主译本, 在 tone_words 的词典别名体系里登记为 loughran, 权威列前缀由 DICT_COLUMN_ALIAS 与 encode.DICT_NAMES 双向锁定。它与项目内另外五部中文金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018) 并列, 六部词典各自独立计分、互为稳健性, 共享完全相同的动态发现路径与后缀结构, 故 exc_loughran_* 的后缀结构与 exc_jiang_2021_* 全等。

【方法学与计算】
计算分两阶段。阶段一在 stage 22 (tone_words) 完成文章级词典计分: 对三轨文本各自逐词匹配 L&M 词典的正负词类, 再叠加三条可开关的语言学规则——否定翻转 (neg, 命中否定词则翻转其后情感词极性)、程度副词放缩 (deg, 命中程度副词则放大邻近情感词权重)、转折翻转 (adv, 命中转折连词则处理前后分句极性)。项目把这三条规则的全部幂集物化为消融变体 (raw/negonly/degonly/advonly/negdeg/negadv/degadv 共七个非-full 变体), degadv 即"程度副词 + 转折两条规则同时启用、否定翻转关闭"这一格。各变体自归一化、非可加分解——审计已确认这些变体两两高度共线 (相关系数约 0.99), 故只报告相关系数而绝不把不同规则变体并入同一回归式。degadv 与其余六个规则变体各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验。

阶段二在 stage 40 的 attention_media 模块完成 bank-year 聚合。detect_defacto_cessation 先以"话题覆盖退出"为停刊的保守代理 (proxy), 把疑似不再覆盖目标话题的媒体来源标记为 _is_ceased_media==1; 随后 C.4 动态发现块遍历所有匹配 _SCORE_PATTERNS 前缀的文章级列, 在存活媒体子样本 (df_alive, _is_ceased_media==0) 上按 (target_bank, year) 求均值, 生成 exc_ 前缀列。此聚合排除了已加权变体 (_w 结尾、含 _mw_ 或 _idf_ 的列) 以及在 C.3 单独处理的 llm_vote_score, 但保留 degadv 这类规则消融列。需强调下游文档口径: ceased_media_frac / exc_* / n_articles_exc 应解读为"疑似退出覆盖媒体"的保守稳健性口径, 不可在论文中表述为严格的报纸停刊 (publication cessation)。零文章 bank-year 的 exc_*tone* 按契约保持 NaN, 绝不连带零填 (只有 n_articles_exc 这类计数列的空集求和才填 0)。

三轨口径遵循项目铁律: full=标题 prepend + 全文正文, ctx=标题 + 实体窗口, ss=标题 + 银行与金科同句共现窗; ss 轨在无共现时镜像 ctx 的回退语义 (content_ss 退化为全文 body)。三轨 exc_loughran_score_degadv 各自 just-identified 并排, 互为稳健性, 禁混同一 over-identified Hansen J。留篇门控为 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙只看 full 轨的 llm_verified 结果, ctx/ss 降为 conditional-on-full 的子集测度。

【文献定位】
词典法情感测量的方法学正当性有稳固文献支撑。Loughran & McDonald (2011) 是本测度词表的直接源头; Loughran & McDonald (2016) 的综述系统论证了在会计金融领域使用领域专用词典而非通用词表的必要性, 并讨论了词典法相对机器学习法的可复现、透明与低成本优势, 正是本项目保留六词典梯度的依据。Taboada et al. (2011) 详述了词典法中程度副词放缩与转折处理等语言学规则的实现, 与本家族 degadv 变体的规则设计一一对应。Du et al. (2022) 与本项目使用的中文金融词典家族同源, 论证了词典的语言与领域特异性。van Atteveldt et al. (2021) 与 Frankel et al. (2022) 分别从传播学与管理学视角比较了人工标注、词典法与机器学习的效度差异, 支撑本项目将词典法与 LLM 法、BERT 法并列为互为稳健性三法的设计。Barbaglia et al. (2025) 与 Loughran & McDonald (2024) 是本领域近年的方法学延续, 前者提供了经济文本词典法的最新实证基准, 后者展示了 L&M 词表族在复杂度等新构念上的持续生命力。

## VAR: exc_loughran_score_degadv_ctx

【变体差分】
本列为 ctx 轨变体。文本通道取 content_ctx——标题 prepend 后叠加围绕目标实体 (银行、金科词) 的上下文窗口, 而非全文。相对家族的 full 轨基准, ctx 轨刻意收窄了计分文本的语义范围, 只保留实体近邻的句子, 以此检验情感信号是否集中于直接谈及银行与金融科技的语段。词典、规则组合 (degadv=程度副词 + 转折、关闭否定翻转)、停刊剔除聚合口径三者与家族其余两列完全一致, 唯一差别是底层文章级列取 loughran_score_degadv_ctx。在 full-only 留篇门控下, ctx 轨是 conditional-on-full 的稳健性测度: 行宇宙是 full 轨留篇集的子集, per-track 均值照算但不重新定义样本。ctx 与 full、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。早期试跑 T=2 上 ctx/ss 轨在部分 bank-year 可能零方差或缺列, 此时 attention_media 的 if src in df_alive.columns 守卫优雅跳过, 属预期退化而非缺陷; 生产 T=19 语料下三轨均正常出值。需注意 ctx 轨的实体窗口口径 (config context_window) 与 stage 13 共现硬过滤的 sentence_radius 是两个不同的配置键, 不可混用。就 degadv 规则格而言, ctx 轨与其余六个规则消融变体 (raw、negonly、degonly、advonly、negdeg、negadv) 在 ctx 通道上高度共线, 各自 just-identified 并排、互为稳健性、不分主次, 报告相关系数而绝不并入同一回归式, 亦禁混进同一 over-identified Hansen J。此外, exc_ 前缀所依赖的停刊代理剔除只作用于聚合分母 (存活媒体子样本), 不改变 ctx 轨文本切分本身, 因此本列同时承载"文本轨收窄"与"媒体样本剔除"两重稳健性设计, 二者正交叠加。

## VAR: exc_loughran_score_degadv_full

【变体差分】
本列为 full 轨变体, 是家族的规范 (canonical) 轨。文本通道取 content_full——标题 prepend 后接完整正文 body, 计分覆盖整篇报道的全部文字, 语义范围最宽。这是留篇门控的判定轨: 依 2026-06-29 full-only 口径, 一篇报道是否计入某银行某年的报道宇宙, 只看 full 轨的验证结果; ctx 与 ss 轨的同名列都是在 full 留篇集之上的子集测度。词典 (L&M 中文主译, loughran 别名)、规则消融组合 (degadv: 启用程度副词放缩与转折翻转、关闭否定翻转) 与停刊代理剔除聚合口径与家族其余两列一致, 唯一差别是底层取 loughran_score_degadv_full。作为最宽文本轨, full 通常信噪比与覆盖率最高, 在生产规模下最稳定; 但它也最易被与银行金科主题弱相关的段落稀释, 故需 ctx/ss 两轨作为收窄语义范围的稳健性对照。degadv 这一规则格与同词典的其余六个规则变体 (raw、negonly 等) 高度共线 (相关系数约 0.99), 各自 just-identified 并排、互为稳健性, 报告相关系数而绝不并入同一回归式, 亦禁混进同一 over-identified Hansen J。full 与 ctx、ss 三轨同理各自并排, 禁混同一 Hansen J。就聚合层而言, exc_ 前缀依赖的停刊代理剔除是保守的"话题覆盖退出"代理, 而非严格报纸停刊口径, 故本列在 full 轨上给出的是"疑似退出覆盖媒体剔除后"的银行金科情感均值, 供 Stata 端与未剔除口径的兄弟列作系数稳定性对照。零文章 bank-year 按契约保持 NaN 而非零填, 以免与计数列 n_articles_exc=0 产生"有均值却无文章"的矛盾。

## VAR: exc_loughran_score_degadv_ss

【变体差分】
本列为 ss 轨变体。文本通道取 content_ss——标题 prepend 后取"银行与金融科技词同句共现"窗口 (config filtering 的 context_window.ss_sentence_radius, 默认 ±1 句), 是三轨中语义约束最严的一轨, 只保留银行与金科在同一或邻近句子中共同出现的语段。相对 full 与 ctx, ss 轨检验的是情感信号在"银行确实与金融科技同句相关"的最狭窄语境下是否依然稳健。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行与金科的同句共现时, content_ss 优雅降级为全文 body 且 ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则 is_fallback 全 True 整体降级。词典、degadv 规则组合与停刊代理剔除聚合口径与家族其余两列一致, 唯一差别是底层取 loughran_score_degadv_ss。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。早期试跑 T=2 上 ss 轨因共现约束严格, 满足条件的样本极少, 常出现零方差或全 NaN, 属预期退化; 生产 T=19 全量语料下方能充分出值。ss 轨的同句共现判据 (extract_bank_fintech_cooccurrence) 与 stage 13 的邻近共现硬过滤判据是两套不同口径, 禁互相复用。与家族其余两轨一样, ss 轨的 degadv 规则格与同词典其余六个规则消融变体高度共线, 各自 just-identified 并排、互为稳健性, 报告相关系数而不并入同一回归式, 亦禁混同一 over-identified Hansen J。本列同时叠加最严的文本约束 (银行金科同句) 与停刊代理媒体剔除, 是三轨中语义与样本双重最保守的稳健性臂, 主要价值在于验证情感信号在最窄语境与最保守样本下是否依然与 full 轨同号。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
