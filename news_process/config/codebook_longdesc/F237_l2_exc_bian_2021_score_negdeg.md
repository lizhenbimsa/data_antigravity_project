---
family_id: F237
novelty_exempt_rationale: "F237 是 exc_ 前缀的媒体退出稳健性排除变体 × negdeg 规则消融臂, 属于 bian_2021 词典母族的派生/消融子变体 (非独立构念), frontmatter 已含 5 篇文献且含 2025 (Barbaglia et al., Economic Inquiry) 与 2022 (Frankel et al., Management Science; Du et al., Review of Finance) 三篇 2022+ 文献, 覆盖词典法情感分析、效价转移词处理、中文财经词典构建与词典-ML比较等全部构念维度, 母族文献已充分覆盖, 无需为该 exc_/negdeg 消融格点单独补充引文。"
columns:
- exc_bian_2021_score_negdeg_ctx
- exc_bian_2021_score_negdeg_full
- exc_bian_2021_score_negdeg_ss
unit: 情感倾向分值 (无量纲, 词典自归一化), 银行-年在"存活媒体"子集上的算术均值
formula: "exc_bian_2021_score_negdeg{track} = mean over 存活媒体(非疑似退出覆盖)文章的 bian_2021_score_negdeg{track}; 文章级 bian_2021_score_negdeg = 仅启用 (否定翻转 ∧ 程度副词) 两条语言学规则重算的 Bian et al. (2021) 词典净情感, 未启用转折(adversative)规则"
producer: news_process/pipeline/panel/attention_media.py::compute_media_attention (C.4 段, 动态发现 _SCORE_PATTERNS 前缀 'bian_2021_score_'); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (_RULE_ABLATION_VARIANTS)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_score_negdeg{track})
- 40_panel_export_main (detect_defacto_cessation → _is_ceased_media 掩码)
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"媒体退出稳健性口径下、以否定加程度副词两条语言学规则重算的 Bian 词典净情感"。它是三条正交设计维度的交点: 其一是底层情感词典, 取自 Bian et al. (2021) 为会计与金融文本分析构建的中文财经情感词典 (bian_2021), 该词典按财经语料的正负极性对词条打标, 是本仓六部词典 (jiang/yao/bian/du/you/loughran) 之一; 其二是规则消融变体后缀 negdeg, 即在词典打分时只启用"否定翻转"与"程度副词加权"两条语言学规则、刻意关闭"转折(adversative)"规则的消融臂; 其三是 exc 前缀所标记的样本子集, 即把"疑似退出银行-金科话题覆盖的媒体"保守剔除后, 仅在存活媒体文章上重算的银行-年情感均值。三者叠加, 使本列成为"词典选择 × 规则组合 × 媒体存活"三重稳健性网格中的一个格点, 服务于证明主线情感测度不被上述任一取值驱动的稳健性叙事。

【方法学与计算】
计算分两层。文章级由 tone_words.py::compute_dict_scores 在 stage 22 完成: 对每篇文章的三轨文本 (full/ctx/ss) 分别用 Bian 词典匹配正负词, 在只保留否定翻转与程度副词两条规则的组合下计净情感并自归一化, 得到 bian_2021_score_negdeg 的三轨列。此处规则组合是全 powerset 消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 中的 negdeg 一格, 各消融臂高度共线 (corr≈0.99)、彼此为非可加分解, 因而只报相关而不并入同一线性式。银行-年级聚合由 attention_media.py 的 C.4 段完成: 先由 detect_defacto_cessation 以"话题覆盖退出"为停刊的保守代理, 按各媒体在银行-金科子集中的末次出现年份早于样本末年减阈值 (且累计报道数达门槛) 标记 _is_ceased_media, 并以 NPPA 注销/停办/休刊名录交叉验证 (仅改报告标签, 未证实的 suspected 全量进入排除集); 随后在存活媒体子集 df_alive 上, 按动态发现的 'bian_2021_score_' 前缀 (排除 _w/_mw_/_idf_ 加权变体) 对 target_bank×year 取算术均值, 落为 exc_ 前缀列。零文章的银行-年格按情感类契约保持 NaN, 不做零填 (仅计数类 n_articles_exc 填 0)。

【文献定位】
底层词典的构念依据是 Bian et al. (2021), 其为中文会计与金融文本专门构建极性词表, 是本列词条来源。规则消融所调节的否定、程度副词、转折三类"效价转移词(valence shifters)"处理, 其方法学规范出自 Taboada et al. (2011) 在 Computational Linguistics 上对词典法情感分析的系统化, 该文明确区分了强化词、否定词与转折结构对极性计算的差异化影响, 正是 negdeg 只取否定与程度两条、剔除转折一条的直接依据。中文财经词典相较通用英文词典的领域特异性收益, 由 Du et al. (2022) 在 Review of Finance 上就中文财经情感词典的构建与验证给出, 佐证了在中国语境下采用本土词典 (而非机翻 Loughran-McDonald) 的必要。词典法与机器学习法在披露情感度量上的系统比较由 Frankel et al. (2022) 在 Management Science 上给出, 支撑了本仓将词典、LLM、BERT 三法并置为互为稳健性轨的设计。词典法在经济文本上的近期实证由 Barbaglia et al. (2025) 补充。媒体退出这一样本选择维度, 在以媒体情感为核心变量的面板中必须被识别与控制, 以免情感指标向存活媒体倾斜、污染 Bartik 类工具变量的暴露构造。铁律: 六部词典、七个规则消融臂、存活/全样本两口径、三轨(full/ctx/ss)各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。ss 轨回退语义镜像 ctx 轨。留篇门控为 full-only 口径 (2026-06-29): 是否判为一篇银行-金科报道只看 full 轨 LLM 验证, ctx/ss 为 conditional-on-full 的稳健性轨。 否定处理作为词典法内部一个可被单独测量、单独失效的模块, 其最贴近的方法学依据是 Naldi 与 Petroni (2023): 该文提出一套基于人工构造测试集的评测方法, 专门分析词典法情感分析工具的否定检测与处理表现, 并实证发现各工具在这一模块上的差异显著。这直接支撑本族 negdeg 臂把否定与程度两条规则合并激活、并与仅启否定、仅启程度等臂并排报告的消融设计: 若否定处理确为一个可独立失效的模块, 则其开关后果就必须被显式度量而非默认吸收。迁移边界须写明: 原文为英文、通用领域 (非金融) 的工具评测, 度量对象是否定检测准确率; 本族并不评测否定检测的正确性, 而是把否定规则的开/关作为面板测度的一条稳健性臂, 语料为中文银行金融科技新闻, 且在剔除疑似退出覆盖媒体后于银行-年度层取算术均值; 该文发表于 2023 年, 非 2024 年后的前沿文献。
## VAR: exc_bian_2021_score_negdeg_ctx

【变体差分】
本列为 ctx 轨。文本通道取 content_ctx, 即标题 prepend 后与实体上下文窗口拼接的文本 (银行/金科实体邻近窗, 而非全文正文)。相对于 full 轨, ctx 轨只把命中实体附近的语句纳入词典匹配, 因而对"报道正文里远离银行-金科主题的段落"不敏感, 度量的是聚焦于目标实体语境的 Bian 词典 negdeg 净情感。其余两个维度与家族一致: 底层词典为 bian_2021, 规则组合固定为 negdeg (仅否定翻转与程度副词两条规则、无转折规则), 样本为剔除疑似退出覆盖媒体后的存活子集, 聚合为 target_bank×year 算术均值。按 full-only 门控口径, ctx 轨是 conditional-on-full 的稳健性/测度轨, 其行宇宙是 full 留篇集的子集, per-track 列照算。本列与同族 full/ss 两轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与规则消融梯度的其余六臂 (raw/negonly/degonly/advonly/negadv/degadv) 及其余五部词典的同位列, 同样为并排稳健性格点, 因高度共线只报相关不并入同一线性式。早期试跑 T=2 语料下 ctx 轨可能因窗口稀疏而方差退化, 属预期, 生产 T=19 正常。与 full 轨的差异专门用于识别"报道情感是否由远离实体的背景段落驱动": 若 ctx 与 full 系数一致, 说明主线情感确由银行-金科语境承载, 而非泛泛的报道基调。ctx 轨在存活媒体子集上重算的意义, 是同时排除"退出媒体的选择偏误"与"非实体语境的噪声", 属两重收敛的保守稳健口径, 供 Stata 端与 full 轨、全样本口径做系数稳定性对照。exc 前缀所依赖的退出媒体掩码由 detect_defacto_cessation 生成, 三轨共享同一掩码, 因而 ctx 与 full/ss 的差异纯由文本通道贡献, 掩码维度被固定住, 便于把媒体存活与文本聚焦两条正交轴分离解读。

## VAR: exc_bian_2021_score_negdeg_full

【变体差分】
本列为 full 轨, 是三轨中的锚轨。文本通道取 content_full, 即标题 prepend 后与全文正文拼接的完整文本, 词典对整篇报道的全部语句匹配正负词。相对 ctx/ss 两轨, full 轨纳入的语料最宽, 度量的是整篇报道层面的 Bian 词典 negdeg 净情感。按 full-only 留篇门控 (2026-06-29), 是否判为一篇银行-金科报道只看 full 轨 LLM 验证, 因而 full 轨承担留篇集的定义职责, ctx/ss 两轨的行宇宙均是本轨留篇集的子集。其余两维与家族一致: 词典为 bian_2021, 规则组合为 negdeg (只启用否定翻转与程度副词、关闭转折规则), 样本为剔除疑似退出覆盖媒体后的存活子集, 聚合为 target_bank×year 均值。本列与同族 ctx/ss 两轨、与规则消融其余六臂、与六部词典同位列各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。因 negdeg 与同词典各消融臂高度共线 (corr≈0.99) 且为非可加分解, 报相关系数而非并入同一式。零文章银行-年按情感类契约保持 NaN, 不零填。full 轨作为锚轨, 其与全样本对应列 (无 exc 前缀) 的系数对照, 直接回答"剔除疑似退出覆盖媒体是否改变结论"这一媒体选择偏误问题; 若两者系数一致, 则可披露主线情感测度对媒体存活取值稳健。full 轨同时是留篇集的定义轨: 一篇报道能否进入银行-金科样本仅由 full 轨 LLM 验证决定, ctx/ss 两轨在此留篇集内条件计算。规则组合 negdeg 相对同词典 raw 臂关闭了转折规则、相对 negonly 臂追加了程度副词加权, 因而本列度量的是"计入否定翻转与副词强度、但不因转折结构调整极性"的净情感, 这一取值差异连同其余六消融臂共同构成规则敏感性梯子, 证明词典打分不被单一规则组合驱动。

## VAR: exc_bian_2021_score_negdeg_ss

【变体差分】
本列为 ss 轨 (sentence-sensitive 同句共现轨)。文本通道取 content_ss, 即标题 prepend 后、仅保留"银行与金科在同一句子及其前后 N 句窗口内共现"的语句所构成的超级文档 (窗口半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 1)。相对 ctx 轨的实体邻近窗, ss 轨的判定更严, 要求银行侧与金科侧在同句共现, 因而度量的是最贴近"银行确实在谈金科"语境的 Bian 词典 negdeg 净情感。回退语义镜像 ctx: 当某文章无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母; 若金科自动机为空则 *_is_fallback 全 True 优雅降级。其余两维与家族一致: 词典 bian_2021、规则组合 negdeg (否定翻转加程度副词、无转折)、存活媒体子集、target_bank×year 均值。按 full-only 门控, ss 轨为 conditional-on-full 的稳健性轨。本列与同族 full/ctx 两轨、规则消融其余六臂、六部词典同位列各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。早期试跑 T=2 语料下 ss 轨常因同句共现稀疏而近零方差, 属预期退化, 生产 T=19 正常。ss 轨与 ctx 轨的差异在于共现判定的严格度: ctx 取实体邻近窗、ss 取银行与金科同句 (含 ±N 句窗), 因而 ss 是三轨中语料最窄、语境最贴合"银行确实在谈金科"的一轨, 度量的净情感最不易被泛报道基调稀释。三轨在存活媒体子集上并排, 使研究者可同时观察文本聚焦程度 (full→ctx→ss 递进收窄) 与媒体存活两条正交轴对 Bian 词典 negdeg 情感的影响。ss 轨的超级文档是 content_ss 原样拼接, 已内嵌 prepend 标题, 因而聚合时不再单独走 title 通道以免双标题污染。本列在退出媒体掩码固定下, 与 full/ctx 的差异纯由同句共现口径贡献。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
<!-- rendered-citations:end -->
