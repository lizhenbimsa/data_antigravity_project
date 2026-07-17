---
family_id: F265
columns:
- exc_loughran_score_advonly_ctx
- exc_loughran_score_advonly_full
- exc_loughran_score_advonly_ss
unit: 无量纲情感得分 (自归一化, 值域约 [-1, 1])
novelty_exempt_rationale: "exc_(疑似退出覆盖媒体剔除)×advonly(转折规则单开)双重消融/排除变体家族, 测度定义依据母族 Loughran&McDonald 词典与规则消融梯度设计, 已有文献锚点覆盖, 非独立新构念, 无需追加新引文。"
formula: "exc_loughran_score_advonly = 剔除疑似退出覆盖媒体 (confirmed ∪ suspected, 保守话题层面代理, 非严格停刊口径) 子集上, 仅启用转折(adversative)语言学规则的 loughran (L&M 2011 JF 中文主译) 词典打分聚合; 单篇 score = (pos_adv − neg_adv) / (pos_adv + neg_adv), 分子分母仅计入转折规则调整后的正/负情感词命中, 否定翻转与程度副词加权两条规则均关闭"
producer: pipeline/panel/attention_media.py::detect_defacto_cessation (疑似退出覆盖媒体剔除 exc_ 子集聚合, 保守稳健性口径而非严格停刊判定; 上游单篇词典打分 pipeline/sentiment/tone_words.py::compute_dict_scores 的 advonly 消融变体)
upstream:
- 22_tone_words.parquet
- 14_materialize_ctx.parquet
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
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
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: "10.1057/s41267-025-00798-8"
  type: "journal"
  authors: "Pinto, J., & Siano, F."
  year: 2025
  title: "Beyond words: the challenge of measuring financial text across borders"
  venue: "Journal of International Business Studies"
  vol: "56"
  issue: "7"
  pages_or_artno: "921-936"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「以 Loughran 与 McDonald 金融情感词典 (中文主译版, 列前缀 loughran) 对目标银行金科报道打出的语调得分」在两重稳健性切面下的取值: 一是媒体构成切面的 exc_ 变体, 即从聚合样本中剔除样本期内疑似退出银行-金科话题覆盖的媒体来源后重算的语调——按源码 detect_defacto_cessation 的显式披露, 该判定测的是媒体「退出话题覆盖 (topic exit)」而非经证实的报纸停刊, 排除集 = confirmed ∪ suspected 两类, 其中 suspected 未经权威机构 (如 NPPA) 证实即整体计入排除, 属保守的稳健性代理口径, 不可表述为严格意义的 publication cessation; 二是语言学规则消融切面的 advonly 变体, 即在词典打分时只保留转折 (adversative, 转折连词如"但是/然而/不过") 一条语言学规则, 而把否定翻转 (negation) 与程度副词加权 (degree adverb) 两条规则关闭。两个切面叠加, 使该家族成为主语调测度旁的一条纯稳健性轨: 它回答的问题不是"银行金科报道到底多正面", 而是"当我们剔除疑似退出该话题覆盖的媒体、并只让转折规则起作用时, 语调结论是否依然成立"。构念根源是文本情感的词典法测量传统, 权威出处为 Loughran 与 McDonald (2011), 该文在金融语境下重建情感词表、指出通用词典 (如 Harvard IV) 因领域错配而系统性误判 10-K 语调, 奠定了"领域专用金融词典 + 逐词计数归一"的范式; 本项目第 6 部词典即该文词表的中文主译 (权威以 tone_words.DICT_COLUMN_ALIAS / encode.DICT_NAMES 为准)。

【方法学与计算】
单篇打分链路为: 先在 22_tone_words 阶段对每篇报道逐词匹配 loughran 正、负情感词, 得到基础命中计数; 消融梯度把否定翻转、程度副词、转折三条语言学规则视作可独立开关的算子, 对全部 2 的 3 次方幂集物化为消融变体 raw / negonly / degonly / advonly / negdeg / negadv / degadv (7 个非-full 规则变体), advonly 即"仅转折规则激活"这一格。转折规则的作用是: 遇到转折连词时, 依据 Taboada 等 (2011) 的情境价移 (contextual valence shifting) 思想, 对连词后从句的情感权重做重加权 (转折后为叙述重心), 从而校正"虽然……但是……"式句子里被前半句稀释的真实语调。单篇得分自归一化为 score = (pos_adv − neg_adv)/(pos_adv + neg_adv), 因而每个消融变体各自成一套内部一致的标度, 变体之间高度共线 (审计 MATH-1: corr≈0.99), 属非可加分解, 报告相关系数而非并入同一线性式。面板聚合在 pipeline/panel/attention_media.py::detect_defacto_cessation 完成, 该模块动态发现全部情感列前缀 (含 loughran_score_), 对疑似退出话题覆盖的媒体子集 (confirmed ∪ suspected) 做剔除后按篇平均得到 exc_ 家族的银行-年取值——三点诚实披露之(c) 明确要求 ceased_media_frac / exc_* / n_articles_exc 一律解读为「疑似退出覆盖媒体」稳健性口径 (保守剔除), 不得在论文或本文档中表述为严格停刊 (publication cessation) 口径, 因为 first/last_year 度量的是媒体退出该话题覆盖而非经证实的报纸停刊, 媒体本身可能仍在正常出版只是不再报道银行-金科话题; 留篇总体口径与全项目一致 (full-only 门控, 2026-06-29): 一篇报道是否算入银行金科报道宇宙, 仅由 full 轨的 LLM 验证结果决定, ctx/ss 为 conditional-on-full 的子集测度。

【文献定位】
方法学上本家族坐落于金融文本分析的词典法一支。Loughran 与 McDonald (2011) 是构念的直接锚, 其后 Loughran 与 McDonald (2016) 的综述系统梳理了词典构造、加权、否定处理等设计自由度, 正是本项目把语言学规则做成幂集消融梯度的依据——综述反复强调这些看似技术性的选择会实质影响语调估计, 因此稳健性检验须显式呈现。Frankel、Jennings 与 Lee (2022) 在 Management Science 上直接比较词典法与机器学习法的语调测量, 论证不同方法互为稳健、不应偏废, 为本项目"词典/LLM/BERT 三法并排、各自 just-identified"的架构提供了先例。转折规则的语言学基础见 Taboada 等 (2011), 其情境价移框架是 advonly 变体的理论来源; Barbaglia 等 (2025) 则在经济文本上验证词典法的持续有效性。方法上须复述本项目铁律: 规则消融的各变体 (raw/advonly/…) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同消融变体混进同一 over-identified 的 Hansen J 过度识别检验; 同理三轨 (full/ctx/ss) 亦各自成轨、禁混同一 Hansen J。exc_ 与 bal_ (平衡媒体) 是两条正交的媒体构成稳健性轨, 与规则消融、与三轨彼此独立不交叉。需要注入生成期实测统计处见【动态统计】段, 写手不手填任何面板数字。 就词表移出本国语境后的可比性这一维度而言, Pinto 与 Siano (2025) 以 85 个国家、200,960 份财报电话会记录 (文本本身即英文) 为语料, 把美国基准词表直接套用其上, 发现情感与收益的关联在非美国公司弱约 30%, 且定谳主因是文化距离而非语言 (语言特征仅作文化价值的工具变量); 换言之, L&M 式美国基准词表一旦移出美国语境, 即使文本仍是英文, 信号强度亦系统性衰减, 那么本家族 loughran 词典系 L&M (2011) 英文原表中文主译这一动作既跨文化、又另加中文翻译, 风险只会更大, 这也是本项目不依赖单一词表、而并排多部本土中文词典与多条规则臂的又一动机。须注明该文全文无词表翻译、亦无非英语语料, 语料为财报电话会记录而非中文金融新闻, 且并未涉及否定/程度/转折规则子集的消融设计, 亦无银行-年度聚合层级, 故仅作词表跨语境可比性的背景依据, 不构成 advonly 单规则臂的直接方法学出处。
## VAR: exc_loughran_score_advonly_ctx

【变体差分】
本列是 exc_loughran_score_advonly 家族的 ctx (context / 实体窗口) 轨。与 full 轨相比, 其唯一差别在打分所用的文本载体: ctx 轨的输入是 content_ctx, 即在 stage 14 ctx_materializer 阶段以"标题 prepend + 目标银行实体上下文窗口"物化的文本, 而非全文正文——只保留银行实体命中位置附近的窗口句, 剔除与银行无关的段落, 从而聚焦银行相关叙述的语调而非整篇报道的泛语调。词典、消融规则 (仅转折 advonly)、疑似退出覆盖媒体剔除 (exc_)、自归一化公式与 full 轨完全一致, 差异纯粹来自文本范围。按 full-only 门控口径, 本列的行宇宙是 full 轨留篇集的子集: 一篇报道是否算作银行金科报道由 full 轨 LLM 验证决定, ctx 轨在此子集上按其自身文本重算语调, 属 conditional-on-full 的测度轨。三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J 过度识别检验。ctx 轨的价值在于检验:当把语调测量收窄到银行实体上下文时, advonly 消融下的疑似退出覆盖媒体剔除语调是否与全文口径同向, 是主结论对"文本聚焦度"这一自由度的稳健性证据。dev T=2 盘面上该 exc_ 排除子集可能为空 (两年样本内尚未触发 detect_defacto_cessation 的疑似退出判定) 故暂不显值, 生产 T=19 全量正常。需强调 ctx 轨与 exc_ 前缀是两条正交的自由度:前者控制文本聚焦范围, 后者控制媒体样本构成, 两者叠加不改变 advonly 消融本身的语言学口径。再次重申源码三点诚实披露之(c): exc_ 前缀标注的是保守话题层面「疑似退出覆盖」代理, 而非经证实的媒体停刊, 本列不得被解读为"驱动语调结论的是媒体是否停刊"这一强因果表述。因此本列既服务于"聚焦度稳健性", 又服务于"疑似退出覆盖媒体构成稳健性", 两重切面同向才构成对主语调结论的有力交叉验证。

## VAR: exc_loughran_score_advonly_full

【变体差分】
本列是 exc_loughran_score_advonly 家族的 full (全文) 轨, 也是三轨中的门控基准轨。其文本载体为 content_full, 即"标题 prepend + 完整正文", 覆盖报道全篇而非实体窗口或同句共现。full 轨在本项目具有特殊地位: 留篇门控 (2026-06-29) 判定"一篇报道是否算作银行金科报道"只看 full 轨的 LLM 验证结果 (llm_verified_full == True), 因此 full 轨定义了 ctx/ss 两轨共享的行宇宙, ctx/ss 均为 conditional-on-full 子集。除文本范围外, 本列与家族其余两轨共享同一 loughran 词典、同一 advonly 消融 (仅转折规则激活、否定翻转与程度副词加权关闭)、同一 exc_ 疑似退出覆盖媒体剔除口径与同一自归一化公式 score = (pos_adv − neg_adv)/(pos_adv + neg_adv)。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。作为消融梯度中的 advonly 格, 本列相对 raw 格 (三规则全开) 与其余消融格 (negonly/degonly/negdeg/…) 亦是各自 just-identified 的并排稳健性轨, 彼此高度共线 (corr≈0.99) 属非可加分解, 报告相关系数而非并入同一式。exc_ 前缀标明这是剔除疑似退出银行-金科话题覆盖媒体 (detect_defacto_cessation 判定, confirmed ∪ suspected, 保守代理口径) 后重算的媒体构成稳健性变体, 按源码诚实披露不得表述为严格停刊剔除, 与 bal_ (平衡媒体)、与无前缀主轨正交。作为门控基准轨, full 轨的取值同时被三轨口径与消融梯度双重引用:当研究者要检验"疑似退出覆盖媒体是否驱动语调结论"(而非严格停刊) 时, full 轨给出全文口径下 advonly 消融的排除后语调, 是最直接可比的一格。它与 ctx/ss 两轨同向、与 raw 及其余消融格同向, 层层印证主语调测度不被单一自由度驱动。

## VAR: exc_loughran_score_advonly_ss

【变体差分】
本列是 exc_loughran_score_advonly 家族的 ss (same-sentence / 同句共现) 轨, 三轨中文本范围最窄的一轨。其输入为 content_ss, 即在 stage 14 物化的"标题 prepend + 银行与金融科技词同句 (±N 句窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 共现片段"。ss 轨把语调测量进一步收窄到"银行与金科同时出现"的句子邻域, 相对 ctx 轨的实体窗口更严格地锁定银行金科交叉叙述。回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body, 且 ss_is_fallback 置 True (与 ctx 的回退口径对称, 共享 n_articles 分母)。除文本载体与回退规则外, 本列与家族 full/ctx 两轨共享同一 loughran 词典、同一 advonly 消融 (仅转折规则)、同一 exc_ 疑似退出覆盖媒体剔除口径与同一自归一化公式。按 full-only 门控, ss 轨行宇宙为 full 留篇集子集, 属 conditional-on-full 测度。三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J。ss 轨检验的是最保守的聚焦口径下 advonly 消融、疑似退出覆盖媒体剔除后语调的稳健性 (再次强调: 此为保守话题层面代理, 非经证实的媒体停刊); dev T=2 上因 exc_ 排除子集叠加同句共现约束, 该列可能全空或零方差, 属预期退化, 生产 T=19 正常出值。ss 轨与 ctx 轨的关键区分在判定不对称口径:ctx 以银行实体窗口为界, ss 则要求银行与金科在同句 (±N 句窗) 真实共现, 判定更严, 回退触发也更频繁。两轨叠加 exc_ 疑似退出覆盖媒体剔除与 advonly 转折消融后, 共同构成语调测度在"最保守聚焦口径 + 媒体构成稳健"下的下界检验, 是主结论稳健性叙事中最严苛的一环。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Pinto, J., & Siano, F. (2025). Beyond words: the challenge of measuring financial text across borders. Journal of International Business Studies, 56(7), 921-936. https://doi.org/10.1057/s41267-025-00798-8
<!-- rendered-citations:end -->
