---
family_id: F289
columns:
- exc_you_2018_score_raw_ctx
- exc_you_2018_score_raw_full
- exc_you_2018_score_raw_ss
unit: 情感倾向得分 (无量纲; bank-year 层对文章级 you_2018 词典 L0 零规则基线得分取均值)
formula: "exc_you_2018_score_raw{track} = mean_{i∈alive(b,y,track)} you_2018_score_raw_i{track}; you_2018_score_raw = 仅按 you_2018 词表统计正负面词命中并归一化, 不启用否定翻转/程度副词/转折三条语言学规则 (apply_negation=False, apply_degree=False, apply_adversative=False, 规则消融梯度 L0 基线); alive = 剔除疑似停刊/覆盖退出媒体 (_is_ceased_media==0) 后的存活媒体文章子集"
producer: news_process/pipeline/sentiment/tone_words.py (_RULE_ABLATION_VARIANTS 消融谱物化 you_2018_score_raw{track} 文章级列); news_process/pipeline/panel/attention_media.py (停刊稳健性块, exc_ 前缀 bank-year 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (you_2018_score_raw{track} 文章级词典 L0 基线得分)
- 40_panel_yearly.parquet (attention_media 停刊检测与聚合)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.1371/journal.pone.0305148"
  title: "News source bias and sentiment on social media"
  authors: "Knutson, B., Hsu, T. W., Ko, M., & Tsai, J. L."
  year: 2024
  venue: "PLOS ONE"
  type: "journal"
- doi: "10.1016/j.frl.2023.104865"
  title: "Media sentiment and management earnings forecasts: Evidence from China"
  authors: "Chen, T., Chiu, P.-C., & Wang, Y."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
new_dois:
  - "10.1371/journal.pone.0305148"
  - "10.1016/j.frl.2023.104865"
---

## CORE

【构念与来源】
本家族度量的是"剔除疑似停刊媒体后、以 you_2018 情感词典 L0 零规则基线打分得到的银行-年度新闻情感倾向"。列名结构自外而内三层: exc_ 是"exclude 疑似停刊媒体"的缩写, 表示在把文章级情感聚合成银行-年度面板值之前先剔出被判定为疑似退出该话题报道 (覆盖退出, topic-coverage exit) 的媒体来源, 只对剩余存活媒体文章取均值; you_2018 指以 You、Zhang 与 Zhang (2018) 为学术锚点构造的中文财经情感词表, 该文研究媒体报道 (笔杆子的力量) 如何被市场化与非市场化媒体分别捕获, 为中文财经文本的正负面词汇打分提供了被广泛引用的构念依据; score_raw 中的 raw 后缀标识本列取自词典规则消融梯度 (rule-ablation ladder, v3.11.1 引入) 的 L0 零规则基线, 即仅做正负面词命中计数与归一化, 不启用否定翻转、程度副词、转折三条语言学规则中的任何一条。本家族因此回答一个具体的方法学问题: 剥离掉全部句法修饰规则、只看最朴素的关键词命中打分, 银行-年度情感面板值会不会实质性偏离 (在存活媒体子集上) 引入语言学规则后的规范口径。

【方法学与计算】
计算分三层。第一层是文章级词典打分的规则消融: 在 stage 22 (tone_words) 上, `_RULE_ABLATION_VARIANTS` 谱系统一物化词典打分在三条语言学规则 (否定翻转 apply_negation、程度副词 apply_degree、转折 apply_adversative) 全 powerset 组合下的变体, 每个组合各产一个后缀; raw 对应 (False, False, False), 即三条规则全部关闭的零规则基线, 是该消融谱系中"最原始"的一端, 全启用的对照臂是不带消融后缀的规范列 `you_2018_score{track}` (不在本谱内, 单独物化)。you_2018_score_raw{track} 即在该基线设定下对每篇银行金科报道统计 you_2018 词表正负面词命中并归一化得到的文章级得分。第二层是覆盖退出识别: attention_media 用 detect_defacto_cessation 识别样本期内疑似停止覆盖该话题的媒体, 排除集取 confirmed 与 suspected 的并集 (未经权威证实的 suspected 一律保守纳入排除集, 而非等待证实才剔除), 标记 `_is_ceased_media`。第三层是存活子集聚合: 在 `_is_ceased_media==0` 的存活媒体子集上, 按 target_bank、year 分组对 you_2018_score_raw{track} 取均值, 得到 exc_you_2018_score_raw{track} 三轨列。留篇门控沿用 full-only 口径 (2026-06-29): 一篇报道是否计入"银行金科报道"行宇宙只看 full 轨的 llm_verified 判定, ctx/ss 是 conditional-on-full 的稳健测量轨, 行宇宙是 full 留篇集的子集, per-track 情感值仍照各自文本轨分别计算。三轨含义: full 为标题 prepend 加全文正文, ctx 为标题加目标银行实体窗口, ss 为标题加银行与金科在同一句子共现的窗口 (半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1); ss 回退语义镜像 ctx, 缺银行∧金科同句共现时 content_ss 回退为全文正文, `ss_is_fallback` 置真并共享 `n_articles` 分母, 保证优雅降级不产生单边孤儿。

【文献定位】
本族方法学立足两条独立支点。其一是消融本身的方法论正当性: 词典法情感测量对具体语言学规则的选择带有研究者自由度, van Atteveldt、van der Velden 与 Boukes (2021, *Communication Methods and Measures*) 系统比较人工标注、众包、词典与机器学习四类方法, 指出词典法在成本与可解释性上的相对位置及其构念效度边界, 为对词典内部规则做敏感性检验 (而非只信一种规则设定) 提供了必要性依据; Taboada、Brooke、Tofiloski、Voll 与 Stede (2011, *Computational Linguistics*) 系统论述基于词表的情感分析方法, 明确否定处理、强化词/程度副词与转折结构是词典法打分中最核心的三类语言学修饰规则, 为本族选取这三条规则做消融、以 raw 为其零假设基线的设计提供了方法论对应。其二是词表本身的构念来源与并行方法证据: You、Zhang 与 Zhang (2018, *Review of Financial Studies*) 是 you_2018 词表的学术母锚; Barbaglia、Consoli、Manzan、Tiozzo Pezzoli 与 Tosetti (2025, *Economic Inquiry*) 给出经济文本词典法情感分析的近期系统范式; Frankel、Jennings 与 Lee (2022, *Management Science*) 比较词典法与机器学习情感测度, 为"多方法互为稳健性、不分主次"提供先例, 呼应本族与 stage 21 三家 LLM 投票、stage 23 三模型 BERT 之间的并行不分主次关系。停刊稳健性的动机在于媒体来源在样本期内消失会引入幸存者偏差, 使基于媒体暴露的情感指标与工具变量向存活媒体系统性倾斜, 故以剔除疑似退出媒体的子集重算作为系数稳定性检验。规则消融的七个非-full 组合 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 高度共线 (相邻级差 corr 常 ≈0.99), 论文表述须报相关系数与逐级变号占比, 定性为"定性不变"而非声称某规则组合更优; 消融梯度与三轨、与停刊剔除维度正交, 不交叉相乘出爆炸列数。三轨 (full/ctx/ss) 与规则消融梯度各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 本族与政治词权重梯度亦正交、不交叉。此外, 该文分析社交媒体上不同新闻来源的偏向性与情感差异, 为按媒体来源子集 (如剔除疑似退出媒体) 重新聚合情感测度提供了媒体来源异质性的方法学支撑, 引 Knutson、Hsu、Ko 与 Tsai (2024, PLOS ONE); 该文以中国媒体情感度量管理层盈余预测行为, 提供了中文财经语境下词典法媒体情感测度与幸存者偏差敏感性检验并行的近期实证先例, 引 Chen、Chiu 与 Wang (2024, Finance Research Letters)。

## VAR: exc_you_2018_score_raw_ctx

【变体差分】
本列为规则消融 L0 零规则基线、实体窗 (ctx) 轨的停刊稳健性情感均值。源列 you_2018_score_raw_ctx 在标题加目标银行实体窗口文本上打分, 且否定翻转、程度副词、转折三条语言学规则全部关闭, 只做正负面词命中的朴素归一化: ctx 只取目标银行实体附近的上下文窗口而非全文, 相对 full 轨聚焦银行相关语境、压低无关段落噪声; raw 基线则相对规范列 (全规则启用) 剥离掉全部句法修饰, 是消融谱系的零假设端。停刊维度上, 本列已在聚合前剔除疑似退出媒体 (`_is_ceased_media==0` 子集), 与不带 exc_ 前缀的全样本 you_2018_score_raw_ctx 情感列互为幸存者偏差稳健性对照。ctx 轨在留篇门控上是 conditional-on-full 的稳健轨, 行宇宙为 full 留篇集的子集; ss 回退语义与本轨无关。

从解读角度看, 本列衡量的是"剔除疑似退出话题报道的媒体后, 仅在银行实体近邻语境、且不做任何否定/程度/转折修饰下, you_2018 词典打分反映的银行-年度情感均值"。当研究者比较本列与规范全规则列 `exc_you_2018_score_ctx` 时, 二者差异刻画的是三条语言学规则在 ctx 语境下对情感极性判定的边际贡献: 若否定句 (如"未出现风险")、程度副词 (如"严重亏损")、转折结构 (如"虽有增长但…")在样本中出现频率不高, 两列相关系数会很高、级差很小; 反之差异越大说明规则修正在该文本轨上越重要。由于 ctx 窗口本身已经比 full 窄, 规则修饰触发的语句片段可能被窗口边界切断, 使 ctx 轨的规则消融效应与 full 轨不完全对应, 这是三轨与消融梯度须分别评估、不能相互替代的原因之一。本列与 full/ss 两轨、与同轨其余六个非-full 消融变体 (negonly/degonly/advonly/negdeg/negadv/degadv) 及规范全规则列各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_raw_full

【变体差分】
本列为规则消融 L0 零规则基线、全文 (full) 轨的停刊稳健性情感均值, 是本家族在文本轨维度上的规范 (canonical) 参照臂 (亦是留篇门控 full-only 口径所依据的主轨)。源列 you_2018_score_raw_full 在标题 prepend 加全文正文上打分, 覆盖整篇报道的正负面词命中, 相对 ctx/ss 保留最完整语境; 但在规则维度上, raw 关闭否定翻转、程度副词、转折全部三条规则, 只做最朴素的关键词命中计数, 与规范全规则列 `exc_you_2018_score_full`、以及 negonly/degonly/advonly/negdeg/negadv/degadv 六个部分启用变体构成八点式消融梯度的一端。停刊维度上, 本列在聚合前剔除疑似退出 (覆盖退出代理) 媒体, 只对存活子集取银行-年度均值, 用于对照全样本 raw 情感列检验媒体幸存者偏差是否驱动结论。

作为 full 轨且规则全关的组合, 本列同时承担两条稳健性检验的交汇点: 一是文本轨维度上, 它是留篇门控的行宇宙依据, ctx/ss 两轨行宇宙均是其子集, 因此本列样本量在三轨中通常最大、覆盖最完整; 二是规则维度上, 它是消融梯度的零假设端, 全文语境下否定/程度/转折三条规则触发频率通常高于 ctx/ss (因全文含更多完整句式), 故 full 轨上 raw 与规范全规则列之间的级差理论上比 ctx/ss 更具代表性, 论文披露规则消融的定性稳健性结论时应以本列与规范 full 列的相关系数及变号占比为主要证据。本列与 ctx/ss 两轨、与同轨七个其余消融变体各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_raw_ss

【变体差分】
本列为规则消融 L0 零规则基线、同句共现 (ss) 轨的停刊稳健性情感均值。文本轨 ss 最严格: 只取标题加银行与金科在同一句子共现窗口内的文本 (半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1), 聚焦银行金科强关联语境。源列 you_2018_score_raw_ss 在该窗口文本上打分, 且三条语言学规则全部关闭, 只做朴素关键词命中计数。ss 回退语义镜像 ctx: 无银行与金科同句共现时 content_ss 回退为全文正文, `ss_is_fallback` 置真并共享 `n_articles` 分母, 保证优雅降级不产生单边孤儿。停刊维度上, 本列在聚合前剔除疑似退出 (覆盖退出代理) 媒体, 仅对存活子集按银行-年度取均值, 与全样本 raw ss 情感列互为幸存者偏差稳健性对照。ss 轨为 conditional-on-full 稳健轨, 早期试跑 T=2 上常因样本稀薄呈零方差或缺格, 属预期退化, 生产 T=19 正常。

由于 ss 窗口通常只覆盖一到两句话, 否定/程度/转折三条规则在如此短的窗口内触发的绝对次数本就稀少, raw 基线与规范全规则列 `exc_you_2018_score_ss` 之间的数值差异预期比 full/ctx 两轨更小, 这是解读本列时须特别注意的一点: ss 轨上规则消融的"定性不变"结论更容易成立, 但样本方差本身也更小, 二者不应混为一谈——前者是规则敏感性问题, 后者是窗口稀薄度问题。本列与 full/ctx 两轨、与同轨七个其余消融变体各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Knutson, B., Hsu, T. W., Ko, M., & Tsai, J. L. (2024). News source bias and sentiment on social media. PLOS ONE. https://doi.org/10.1371/journal.pone.0305148
Chen, T., Chiu, P.-C., & Wang, Y. (2024). Media sentiment and management earnings forecasts: Evidence from China. Finance Research Letters. https://doi.org/10.1016/j.frl.2023.104865
<!-- rendered-citations:end -->
