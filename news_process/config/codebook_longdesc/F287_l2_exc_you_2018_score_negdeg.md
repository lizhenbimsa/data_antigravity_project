---
family_id: F287
columns:
- exc_you_2018_score_negdeg_ctx
- exc_you_2018_score_negdeg_full
- exc_you_2018_score_negdeg_ss
unit: 情感倾向得分 (无量纲; bank-year 层对文章级 you_2018 词典规则消融得分取均值, 值域随归一化落在 [-1, +1] 附近)
formula: "exc_you_2018_score_negdeg{track} = mean_{i∈alive(b,y,track)} you_2018_score_negdeg_i{track}; alive = 剔除疑似停刊媒体 (_is_ceased_media==0) 后的存活媒体文章子集; you_2018_score_negdeg{track} 是 you_2018 词典在状态机打分时仅启用「否定翻转」与「程度副词六级权重」两条规则、关闭「转折增强」规则后的自归一化文章级得分 (= you_2018_score{track} 全规则版本减去转折规则的消融臂)"
producer: news_process/pipeline/panel/attention_media.py (第 C.4 步「排除停刊后的全方法情感均值 — 动态发现」, exc_{src} 前缀 bank-year 聚合, src 匹配 _SCORE_PATTERNS 动态发现停刊稳健性变量); 上游文章级消融得分由 news_process/pipeline/sentiment/tone_words.py 的 _RULE_ABLATION_VARIANTS 规则消融梯度 (v3.11.1) 在 stage 22 逐篇计算并写入 22_tone_words.parquet
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (you_2018_score_negdeg{track} 文章级规则消融词典得分, _RULE_ABLATION_VARIANTS 谱之一)
- 40_panel_yearly.parquet (attention_media 停刊检测 detect_defacto_cessation 与 C.4 动态聚合)
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是「剔除疑似停刊媒体后、以 you_2018 情感词典在『仅否定翻转+仅程度副词』两条语言学规则下打分得到的银行-年度新闻情感倾向」, 是规则消融梯度 (rule-ablation ladder, v3.11.1) 在停刊稳健性口径上的映射。列名前缀 exc_ 是「exclude 疑似停刊媒体」的缩写: 在把文章级情感聚合成银行-年度面板值之前, 先把被判定为疑似退出报道该话题 (覆盖退出, topic-coverage exit) 的媒体来源整体剔出样本, 再对剩余存活媒体的文章取均值; 该前缀与本仓「停刊稳健性」全族 (F283 等价 exc_you_2018_score 家族) 共享同一构念, 差别仅在词典打分时启用的语言学规则子集。词典部分 you_2018 指以 You、Zhang 与 Zhang (2018) 为学术锚点的中文财经情感词表, 该文研究媒体报道 (「笔杆子的力量」) 如何被市场化与非市场化媒体分别捕获, 为中文财经文本的正负面词汇打分提供了被广泛引用的构念依据。negdeg 后缀标记的是本仓状态机打分器三条语言学规则 (① 否定翻转、② 程度副词六级权重、③ 转折增强) 全 powerset 消融谱中的一级: 仅启用①否定翻转与②程度副词权重, 关闭③转折增强规则, 等价于「全规则版本 (canonical you_2018_score) 减去转折规则」这一条稳健性臂, 而非某种独立构念——它检验的是主口径的结论是否被「遇到『但是/然而』类转折词时对情感值做额外放大」这一条具体规则驱动。

【方法学与计算】
计算分三层。第一层是文章级规则消融打分: stage 22 (tone_words) 的状态机逐词扫描 you_2018 词表命中, 对每个命中词依次尝试应用否定翻转 (检测该词前若干词内是否存在否定词, 命中则将符号翻转)、程度副词加权 (检测紧邻的程度副词, 按六级词表给出 1.0～3.0 区间的乘子) 与转折增强 (检测句内转折连词, 对转折分句后的情感命中给予额外放大); negdeg 变体在扫描时只让①②两条规则参与最终得分计算、③规则被关闭 (对应 `_RULE_ABLATION_VARIANTS` 中 `('negdeg', True, True, False)` 一项), 随后按 Σ|final_score| (加权幅度和) 归一化, 得到自归一化、值域恒有界于 [-1, +1] 的文章级得分 you_2018_score_negdeg{track}, 写入 22_tone_words.parquet。第二层是停刊稳健性聚合: attention_media 先经 detect_defacto_cessation 识别在样本期内疑似停止覆盖该话题的媒体来源 (排除集 = confirmed 与 suspected 并集, 未经 NPPA 证实的 suspected 一律保守纳入排除集), 标记 _is_ceased_media, 再在存活子集 (_is_ceased_media==0) 上按 target_bank、year 分组求相应源列均值。第三层是列的动态发现: 本家族三列并非像 exc_tone_full/ctx/ss 那样在代码里显式写死, 而是由 attention_media.py 第 (C.4) 步遍历存活子集 df_alive 的全部列, 对列名以 _SCORE_PATTERNS 中任一前缀开头 (含 you_2018_score) 且非已加权变体 (不以 _w 结尾、不含 _mw_/_idf_、不以 llm_vote_score_ 开头) 的列逐一聚合并以 exc_{src} 命名——因此每一条规则消融梯度变体 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 都会自动获得对应的 exc_ 前缀停刊稳健性列, 无需在聚合代码里逐一登记。须强调该口径是「话题覆盖退出」的保守代理而非经证实的报纸停刊, 论文表述应称稳健性口径 (survivorship / 幸存者偏差检验), 不可等同严格出版停刊。留篇门控沿用 full-only 口径 (2026-06-29): 一篇报道是否算「银行金科报道」只看 full 轨 llm_verified 判定, ctx/ss 为 conditional-on-full 的稳健轨, 行宇宙是 full 留篇集的子集。三轨含义: full 为标题加全文正文, ctx 为标题加实体窗口, ss 为标题加银行与金科同句共现窗; ss 回退语义镜像 ctx, 无同句共现时 content_ss 回退为全文正文, ss_is_fallback 置真并共享 n_articles 分母。

【文献定位】
情感词典法在财经文本上的效度是本族方法学的支点: van Atteveldt、van der Velden 与 Boukes (2021, *Communication Methods and Measures*) 系统比较人工标注、众包、词典与机器学习, 论证词典法在成本与可解释性上的位置, 并指出规则细节 (否定、强度修饰) 对词典法效度的边际影响不可忽视, 为本族「拆解语言学规则做消融」提供了直接的方法学动机。Taboada、Brooke、Tofiloski、Voll 与 Stede (2011, *Computational Linguistics*) 系统论述基于词典的情感分析方法中否定处理、强度修饰与转折 (contrastive conjunction) 三类语言学规则各自的作用机制与边界, 是本仓状态机打分器三条规则设计、以及本族选择「保留否定+程度、剔除转折」这一具体消融臂的直接方法学依据。Barbaglia 等 (2025, *Economic Inquiry*) 给出经济文本词典构造的近期范式, 支撑以规则化词表打分聚合的做法。Frankel、Jennings 与 Lee (2022, *Management Science*) 比较词典法与机器学习情感, 为「多方法互为稳健性、不分主次」提供先例, 呼应本仓词典/LLM/BERT 三法并排的整体设计。You、Zhang 与 Zhang (2018, *Review of Financial Studies*) 是 you_2018 词表的构念母锚。停刊稳健性的动机在于媒体来源消失会引入幸存者偏差, 使情感指标向存活媒体倾斜并污染基于媒体暴露的工具变量, 故以剔除疑似退出媒体的子集重算作为系数稳定性检验; 规则消融梯度的动机则是把词典打分器内部三条正乘子/翻转规则的贡献拆解为可审计的独立稳健性臂, 而非把它们隐式打包进单一 canonical 得分。三轨 (full/ctx/ss) 与规则消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 本族与政治词权重梯度 (du_2022 独有) 正交, 不交叉。非可加分解须留意: 每个消融变体各自 self-normalize (Σ|final| 分母随启用规则变化), 且否定与程度作用同一词含交互, 相邻级差并非「某规则的纯贡献」, 仅作为 ablation 稳健性对照, 论文表述宜采用「定性不变」而非声称某规则边际效应量化可分解。

## VAR: exc_you_2018_score_negdeg_ctx

【变体差分】
本列为规则消融 negdeg (仅否定翻转+仅程度副词权重, 关闭转折增强)、实体窗 (ctx) 轨的停刊稳健性情感均值。源列 you_2018_score_negdeg_ctx 在标题加实体窗口文本上以 you_2018 词典打分, 打分时只让否定翻转与程度副词权重两条规则参与最终得分, 转折增强规则被关闭; ctx 只取目标银行实体附近的上下文窗口而非全文, 相对 full 轨聚焦银行相关语境、压低无关段落噪声, 也相对 ss 轨保留更宽的上下文 (不要求银行与金科严格同句)。本列检验的是: 在已经聚焦到实体窗口的语境下, 「遇到转折词额外放大情感」这条规则是否驱动结论——与同轨 canonical 全规则得分 (you_2018_score_ctx) 及同轨其余消融臂 (raw/negonly/degonly/advonly/negadv/degadv) 对照, 若系数方向与显著性「定性不变」, 可视为结论不由转折规则这一自由度驱动。停刊维度上, 本列已在聚合前剔除疑似退出媒体 (_is_ceased_media==0 子集): attention_media 用 detect_defacto_cessation 判定某媒体来源在样本期内是否疑似停止覆盖该话题, confirmed 与 suspected 一律并入排除集, 再对存活媒体子集按 target_bank、year 分组求 ctx 轨 negdeg 消融得分均值。ctx 轨在留篇门控上是 conditional-on-full 的稳健轨: 一篇报道是否计入行宇宙, 由 full 轨 llm_verified 判定, ctx 只在该子集内重算测度, 不独立扩样本; ss 回退语义 (缺同句共现回退全文) 与本轨无关。本列与 full/ss 两轨、与同轨其余六个规则消融臂各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_negdeg_full

【变体差分】
本列为规则消融 negdeg、全文 (full) 轨的停刊稳健性情感均值, 是本家族三轨中的规范 (canonical) 参照臂, 亦是留篇门控 full-only 口径 (2026-06-29) 所依据的主轨。源列 you_2018_score_negdeg_full 在标题 prepend 加全文正文上以 you_2018 词典打分, 打分时只让否定翻转与程度副词权重两条规则参与最终得分、转折增强规则被关闭, 覆盖整篇报道从标题到正文尾段的全部正负面词命中, 相对 ctx (仅实体窗口) 与 ss (仅同句共现窗) 保留最完整语境, 因此代价是也纳入了与银行金科关联较弱段落的噪声。本列与同轨 canonical 全规则得分 (you_2018_score_full, 三条规则全开) 相比, 差别恰为「关闭转折增强」这一单一自由度 (= you_2018_score_full 减去转折规则的消融臂); 与 negonly (仅否定)、degonly (仅程度) 等更小子集相比, negdeg 多保留了程度或否定其中一条, 是该消融梯度上信息量介于单规则臂与全规则 canonical 之间的一级。停刊维度上, 本列在聚合前剔除疑似退出 (话题覆盖退出的保守代理) 媒体, 只对存活子集按 target_bank、year 分组取均值, 用于对照全样本 you_2018_score_negdeg_full 情感列检验媒体幸存者偏差是否驱动结论。本列与 ctx/ss 两轨、与同轨其余六个规则消融臂 (raw/negonly/degonly/advonly/negadv/degadv) 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: exc_you_2018_score_negdeg_ss

【变体差分】
本列为规则消融 negdeg、同句共现 (ss) 轨的停刊稳健性情感均值。文本轨 ss 最严格: 只取标题加银行与金科在同一句子共现窗口 (半径由 config filtering ss_sentence_radius 控制, 默认 1) 的文本, 聚焦银行金科强关联语境。源列 you_2018_score_negdeg_ss 打分时只让否定翻转与程度副词权重两条规则参与最终得分, 转折增强规则被关闭。ss 回退语义镜像 ctx: 无银行与金科同句共现时 content_ss 回退为全文正文, ss_is_fallback 置真并共享 n_articles 分母, 保证优雅降级不产孤儿。停刊维度上聚合前剔除疑似退出媒体, 仅对存活子集按 target_bank、year 分组取均值, 与全样本 ss 轨 negdeg 消融情感列互为幸存者偏差稳健性对照。ss 轨在留篇门控上是 conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集; dev T=2 上 ss 轨常因样本稀薄退化 (零方差或缺格), 属预期, 生产 T=18 正常。由于 ss 文本窗口本身就比 full/ctx 更窄, 命中 you_2018 词表的正负面词数在单篇报道内往往更少, 打分器的否定翻转与程度副词加权在小样本命中下对最终自归一化得分的影响相对更敏感, 这是解读本列时应额外留意的一点: 与同轨 canonical 全规则 ss 得分 (you_2018_score_ss) 及其余消融臂 (raw/negonly/degonly/advonly/negadv/degadv) 对照时, 若系数方向定性不变但幅度波动大于 full/ctx 两轨, 不应误读为规则本身失效, 而应归因于 ss 轨样本窗口窄带来的方差放大。本列与 full/ctx 两轨、与同轨其余六个规则消融臂各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
