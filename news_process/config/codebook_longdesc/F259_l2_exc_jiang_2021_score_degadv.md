---
family_id: F259
columns:
- exc_jiang_2021_score_degadv_ctx
- exc_jiang_2021_score_degadv_full
- exc_jiang_2021_score_degadv_ss
unit: 无量纲情感倾向得分 (bank-year 级均值, 值域约 [-1, 1]; 分母仅计存活媒体报道)
formula: "exc_jiang_2021_score_degadv{track} = mean over articles with _is_ceased_media==0 in (target_bank, year) of jiang_2021_score_degadv{track}; 文章级 jiang_2021_score_degadv = 自归一化词典情感, 施加程度副词(deg)+转折(adv)两条语言学规则, 不施否定翻转(neg)"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性聚合; 文章级源列产自 pipeline/sentiment/tone_words.py 词典消融梯度)
novelty_exempt_rationale: "消融/排除复合变体家族 (exc_ 停刊剔除前缀 × degadv 语言学规则消融梯度), 测度定义依据母族姜富伟(2021)词典及规则消融梯度 SSOT, 非独立新构念, 无需追新文献。"
upstream:
- 22_tone_words.parquet (jiang_2021_score_degadv_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- detect_defacto_cessation (_is_ceased_media 覆盖退出代理标记)
citations:
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
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
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"排除疑似停刊媒体后、以姜富伟等 (2021) 中文财经情感词典按程度副词与转折两条语言学规则加工所得的银行年度媒体情绪均值"。构念落在两个相互独立的坐标上: 一是分母口径, 即把疑似退出报道覆盖的媒体从聚合样本里保守剔除, 得到"存活媒体子样本"上的情绪测度, 用以检验主情绪指标是否被媒体退场引入的幸存者偏差 (survivorship bias) 所驱动; 二是文章级情感的构造口径, 即在词典打分时选择性地开启程度副词加权 (deg) 与转折让步翻转 (adv) 两条规则、而关闭否定翻转 (neg) 规则, 由此得到消融梯度中的 degadv 变体。前者对应 producer 里的 exc_ 前缀语义, 后者对应文章级源列名尾部的 degadv 后缀语义。二者组合起来, 该家族列即"存活媒体样本 × degadv 规则组合"下的姜富伟词典情绪, 是主情绪测度的一条稳健性支路, 而非独立的新构念。

情感词典本身取自姜富伟, 孟令超, 唐国豪 (2021) 为中国媒体文本构造的财经情绪词表, 该词典把词语分为正面与负面两极, 并被作者验证为对 A 股市场股票回报具有样本外预测力。本项目把它作为词典法情绪的六部中文词典之一纳入 stage 22 (tone_words), 与 yao_2021、bian_2021、du_2022、you_2018 以及 L&M 中文主译 loughran 并列, 各词典各自打分、互为稳健性、不分主次。degadv 只是该词典在语言学规则消融梯度上的一个具体组合, 与 raw、negonly、degonly、advonly、negdeg、negadv 等同族兄弟变体处于同一梯子上。

【方法学与计算】
计算链路分两层。文章级第一层在 stage 22 完成: 对每篇报道的目标文本, 先用词典匹配出正负情感词, 再叠加语言学规则修正——degadv 变体只启用程度副词规则 (遇到"很/极其/较为"等修饰时按强度缩放情感权重) 与转折规则 (遇到"但是/然而/尽管"等让步连词时对从句情感做符号或权重调整), 而不启用否定翻转规则 (不对"不/没有"等否定词后的情感词做符号翻转)。各规则消融变体均自归一化, 彼此高度共线 (审计口径下相关系数常接近 0.99), 因此它们只作规格稳健性并排, 属于非可加分解, 严禁把多个变体并进同一 over-identified Hansen J 联合识别; 每条变体各自 just-identified 并排, 互为稳健性、不分主次。文章级 degadv 情绪在 full、ctx、ss 三条文本轨上分别产出。

面板级第二层在 attention_media.py 的停刊稳健性区块完成: 先由 detect_defacto_cessation 依据"某媒体是否停止覆盖目标话题"这一保守代理判定 _is_ceased_media 标记 (须强调这是话题覆盖退出的代理, 并非经证实的报纸停刊), 再取 _is_ceased_media 为零的存活媒体子样本, 按 (target_bank, year) 分组对文章级 jiang_2021_score_degadv{track} 求简单算术均值, 加 exc_ 前缀落为面板列。零文章的银行年度按情感类契约保持缺失 (不做零填), 以区别于计数类列的零填口径。三条文本轨各得一列, 即本家族的三个成员。整个第二层是纯 CPU、零 API、golden-safe 的确定性后处理。

【文献定位】
在方法学谱系上, 词典法情绪与机器学习、大模型情绪构成互补的三条测量路径。Frankel, Jennings, Lee (2022) 系统比较了披露情绪的机器学习法与词典法, 论证两类方法在不同场景下各有偏误、宜互为稳健性对照, 这正是本项目让六部词典、三家 LLM、三个 BERT 各自并排的先例依据。Cao, Jiang, Yang, Zhang (2023) 进一步指出当机器成为文本读者时企业披露语言会内生调整, 提示任何单一文本情绪测度都需要多口径稳健性支撑。中文语境下, Du, Huang, Wermers, Wu (2022) 强调财经情绪词典的语言与领域特异性, 说明直接移植英文词典会失真、须使用本土构造的中文词表——这为本家族选用姜富伟等 (2021) 的中文词典提供了直接理由。至于程度与转折两条规则本身, Taboada 等 (2011) 的词典法情感分析框架给出了系统的效价转移 (valence shifting) 处理, 包括强化词 (intensifier, 对应 deg) 与对比连词 (对应 adv) 的加权与翻转规则, 是 degadv 组合的方法论出处。而把词典情绪用于资产定价预测的传统, 则可上溯至 Jiang, Lee, Martin, Zhou (2019) 对管理层情绪与股票回报关系的证据。停刊剔除这一层的动机, 来自媒体退场引入的样本选择问题: 存活媒体样本上的情绪若与全样本情绪系数一致, 即可缓解对幸存者偏差污染 Bartik 类工具变量的担忧。

## VAR: exc_jiang_2021_score_degadv_full

【变体差分】
本列取 full 文本轨。full 轨的文本口径是"标题 prepend 到正文之前 + 全文正文", 即在 stage 14 物化的 content_full 上跑词典打分, 覆盖整篇报道的全部文字。相对同家族的 ctx 与 ss 两列, full 轨不做任何实体窗口裁剪, 因此纳入打分的情感词最多、分母文本最长, 通常是三轨中信噪比最稳、缺失最少的一条。在本项目的留篇门控口径下 (2026-06-29 full-only), 一篇报道是否被判为"一篇银行金科报道"仅取决于其 full 轨的 LLM 判定, 故 full 轨对应的存活样本行宇宙即留篇集本身, ctx/ss 两轨是其 conditional-on-full 的子集测度。就本列而言, 它是"存活媒体 × degadv 规则 × full 轨"的姜富伟词典情绪银行年度均值: 分母是该银行当年被判存活媒体所发的报道, 每篇按 degadv 规则 (开程度副词与转折、关否定翻转) 自归一化打分后取算术平均。它与 ctx_、ss_ 两列构成三轨规格稳健性并排, 三轨各自 just-identified、互为稳健性、不分主次, 严禁把三轨列混进同一 over-identified Hansen J 联合识别。与同轨的其它规则消融变体 (如 full 上的 negadv、negdeg) 相比, 本列的唯一区别是关闭了否定翻转规则, 因此对含大量否定句式的负面报道, 其打分符号可能与开否定的变体系统性不同, 这正是该变体存在的敏感性检验价值。

## VAR: exc_jiang_2021_score_degadv_ctx

【变体差分】
本列取 ctx 文本轨。ctx 轨的文本口径是"标题 prepend + 实体上下文窗口", 即只保留围绕目标银行等实体邻近若干句的正文片段 (content_ctx), 而非整篇全文。相较 full 轨, ctx 轨主动裁掉了与目标实体无关的段落, 意在减少跑题文字对情绪测度的稀释, 代价是纳入的情感词更少、极端情形下可能出现零匹配而回退。就本列而言, 它是"存活媒体 × degadv 规则 × ctx 轨"的姜富伟词典情绪银行年度均值: 分母同为该银行当年存活媒体报道, 但每篇的打分文本被收窄到实体上下文窗口, 再按 degadv 规则 (程度副词加权 + 转折翻转、不做否定翻转) 自归一化后组内取均值。本列相对 full 列的差异纯在文本轨口径, 相对 ss 列的差异在窗口判据 (实体上下文窗口 vs 银行金科严格同句共现), 相对同轨其它消融变体的差异在语言学规则组合。在留篇门控 full-only 口径下, ctx 轨是 conditional-on-full 的稳健性测度轨, 行宇宙为 full 存活留篇集的子集。三轨互为稳健性、不分主次、各自 just-identified 并排, 严禁三轨列同入一个 over-identified Hansen J。在 T=2 的开发盘面上, ctx 轨聚合常因窗口内样本稀薄而更易缺失或退化, 属预期现象, 生产 T=19 语料下方可充分显形。

## VAR: exc_jiang_2021_score_degadv_ss

【变体差分】
本列取 ss 文本轨。ss 轨的文本口径是"标题 prepend + 银行与金融科技词在同一句子及其正负 N 句窗口内共现的片段" (content_ss, 默认句半径由 filtering.yaml 的 ss_sentence_radius 控制, 默认 1)。这是三轨中判据最严的一条: 只有当目标银行与金科词真正同句 (或紧邻句) 共现时, 对应片段才进入打分文本; 若全篇不存在此类共现, 则 ss 轨镜像 ctx 的回退语义、退化为使用全文正文并置 ss_is_fallback 为真, 且与 ctx 共享 n_articles 分母。就本列而言, 它是"存活媒体 × degadv 规则 × ss 轨"的姜富伟词典情绪银行年度均值: 分母为该银行当年存活媒体报道, 每篇的打分文本取银行金科同句共现窗口, 再按 degadv 规则 (仅程度副词与转折规则, 关否定翻转) 自归一化后取组内均值。本列与 full/ctx 两列的唯一系统差异是文本轨判据 (严格同句共现 vs 全文 vs 实体窗口), 与同轨其它消融变体的差异在语言学规则组合。三轨列各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。因判据最严, ss 轨在开发盘面上最易触发回退或零方差退化, 生产全量语料下才能体现其"最贴近银行金科语义共现"的测量价值。需要强调的是, ss 轨的回退并非静默丢列, 而是优雅降级为全文正文并显式打上回退标记, 使下游能够区分"真同句共现"与"无共现回退"两种来源, 避免把回退样本误当作严格共现证据。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
