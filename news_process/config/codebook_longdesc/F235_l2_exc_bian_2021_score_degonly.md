---
family_id: F235
novelty_exempt_rationale: "exc_ 停刊剔除臂 × degonly 规则消融臂的双重稳健性变体家族, 测度定义依据母族 Bian et al. (2021) 词典与规则消融梯度/媒体覆盖退出检测方法, 非独立新构念, 不需追加新文献。"
columns:
- exc_bian_2021_score_degonly_ctx
- exc_bian_2021_score_degonly_full
- exc_bian_2021_score_degonly_ss
unit: 情感倾向分值 (无量纲, 带符号词典打分的银行-年均值)
formula: "exc_bian_2021_score_degonly_track(b,y) = mean over articles a in (b,y) with media(a) NOT in ceased_set of bian_2021_score_degonly_track(a); 文章级 bian_2021_score_degonly = 带符号词典极性加权和, 仅施加程度副词六级加权规则 (否定翻转 OFF, 转折增强 OFF); ceased_set = detect_defacto_cessation 检出的疑似覆盖退出媒体 (confirmed ∪ suspected)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity
upstream:
- 22_tone_words.parquet (bian_2021_score_degonly_{full,ctx,ss} 文章级列)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- 40_panel_export_main (detect_defacto_cessation → ceased_set)
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
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
本家族刻画的是一个复合稳健性测度: 在剔除"疑似退出覆盖的媒体"之后, 用 Bian 等 (2021) 的中文金融情感词典、并只保留"程度副词加权"这一条语言学规则, 对每篇银行-金融科技报道打出的带符号情感分, 再聚合到银行-年层级的均值。它同时承载两条相互正交的稳健性叙事: 其一是样本选择维度的"停刊/覆盖退出稳健性"(exc 前缀); 其二是打分规则维度的"规则消融梯度"(degonly 后缀)。两条叙事都不是主结果测度, 而是用来证明主结论对"哪些媒体进入样本"以及"施加哪几条语言学规则"这两个研究者选择并不敏感的旁证轨。

【构念与来源】的第一层是词典来源。Bian 等 (2021) 在 Loughran 与 McDonald 英文金融词典的框架上做中文本土化扩充, 给出正负极性词表; 本项目以 tone_dicts.json 为该词典的单一事实源, 正词赋 +1、负词赋 -1, 跨正负两类重叠的词按用户 2026-06-24 决策保留并两侧计数 (占位幅值取绝对值, 符号无意义)。文章级 bian_2021_score 是词典命中词的带符号加权和, 而 degonly 变体在此基础上只开启"程度副词六级加权"这一条规则: 否定窗口翻转关闭、转折 (adversative) 增强关闭, 因此该变体绝不改变任何命中词的极性符号, 只按"极其/非常/较/略"等程度副词的六级强度调整幅值。它属于 v3.11.1 引入的规则消融梯度 (rule-ablation ladder), 该梯度把状态机三规则 (否定翻转 / 程度加权 / 转折增强) 做 powerset 组合, 物化出 raw、negonly、degonly、advonly、negdeg、negadv、degadv 七个非-full 变体, degonly 是其中"仅程度"这一格。

【方法学与计算】exc 前缀的语义来自 attention_media.detect_defacto_cessation: 该函数在银行-金融科技报道子集上按媒体统计首末出现年份与文章数, 把最后出现年份早于样本末年减去阈值间隔、且文章数不低于门槛的媒体标记为"疑似覆盖退出", 并与新闻出版署 (NPPA) 停办名录做交叉验证, 未经证实的 suspected 全量进入排除集 (confirmed ∪ suspected), 交叉验证仅改报告标签而不收窄排除集。随后在排除这些媒体的存活样本上, 对每个银行-年格逐轨求 bian_2021_score_degonly 的算术均值, 落为 exc_bian_2021_score_degonly。诚实披露口径: 该检测度量的是媒体"退出银行-金融科技话题覆盖"(topic exit) 而非经证实的报纸停刊, 媒体可能仍在正常出版; 因而下游 exc_* 只可解读为"疑似退出覆盖媒体"的保守剔除稳健性口径, 不可在论文中表述为严格停刊 (publication cessation) 口径。计数上的零文章格与情感均值格处理不同: n_articles_exc 按"计数 Σ over ∅ = 0"契约填 0, 而 exc_* 情感类列在空集上按契约保持 NaN, 绝不连带零填。

【文献定位】把媒体覆盖退出识别出来并做样本稳健性, 其因果动机在金融经济学文献里有清晰锚点: 报纸退出地方覆盖会造成监督真空, 进而抬升公司违规与公共财政成本, 因此以媒体情感为核心解释变量的面板研究必须识别并控制媒体来源消失引入的样本选择偏误。词典法一侧, Bian 等 (2021) 提供了本测度的词表来源, 而 Du 等 (2022, Review of Finance) 系统论证了金融文本情感的语言与领域特异性——通用词典跨领域迁移会系统性失真, 这正是本项目采用多部中文金融专用词典并做规则消融的依据。degonly 只保留程度副词加权, 呼应 Taboada 等 (2011) 在词典法中对强化词 (intensifier) 与程度处理的强调; 而"词典法与机器学习是否给出一致结论"这一互为稳健性框架, Frankel 等 (2022, Management Science) 已作先例。测量效度层面, van Atteveldt 等 (2021) 对人工标注、众包、词典、机器学习四类方法做系统比对, Barbaglia 等 (2025) 与 Ma 等 (2025) 则分别在经济文本与中文细粒度投资者情感上更新了词典法的证据, 三者共同支撑"词典法作为可解释、可复现的旁证轨"这一定位。口径铁律: exc 停刊臂与 degonly 规则臂、以及下方三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验; 银行留篇门控遵循 full-only 口径 (2026-06-29), n_articles 之类的行宇宙以 full 轨留篇集为准, ctx/ss 为 conditional-on-full 的稳健性轨。⚠ 非可加分解 (audit MATH-1): 规则消融各相邻级差含否定×程度交互与自归一化分母变更, degonly 只作"主结果对程度规则是否敏感"的定性对照, 不可解读为程度规则的纯贡献。

## VAR: exc_bian_2021_score_degonly_ctx

【变体差分】
本列是 ctx 轨的实例。ctx (context) 轨的文本口径 = 标题 prepend 后, 只保留银行别名命中句及其前后各若干句 (context_window.sentence_radius, 默认 ±1 句) 的实体窗口拼接文本, 而非全文正文。因此本列度量的是"围绕目标银行的近场语境"里, Bian 等 (2021) 词典在 degonly 规则 (仅程度副词六级加权, 否定翻转与转折增强均关闭) 下打出的带符号情感分, 在剔除疑似覆盖退出媒体后按银行-年求得的均值。它与同族 full 列的唯一差别在文本窗口: full 用整篇正文, ctx 用实体邻域窗口; 与 ss 列的差别则在共现判据的严格程度。ctx 轨相对 full 轨定位为 conditional-on-full 的稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 列照算。按口径铁律, ctx 轨与 full/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 同理 exc 停刊臂与 degonly 规则臂与三轨三个维度彼此正交, 不交叉进同一过度识别式。早期试跑 T=2 语料上 ctx 轨可能因窗口收窄而出现零方差退化, 属预期; 生产 T=19 全量语料下正常取值。与家族 canonical 主情感列 (无 exc 前缀、full 规则的 bian_2021_tone) 相比, 本列在样本 (剔停刊媒体)、规则 (仅程度) 与文本窗口 (实体邻域) 三处同时偏移, 因此绝不作为主测度, 只在稳健性表里与主列并排比对系数符号与显著性是否稳定。ctx 窗口的实体命中经否定前缀与短名排除守卫过滤 (has_unexcluded_occurrence), 命中句前后各 radius 句扩窗后做区间合并再拼接, 无命中则回退全文正文, 与 ss 的回退公理同源但共现判据口径不同 (ctx 是银行别名命中即扩窗, ss 要求银行与金科同句共现), 两者不可互相复用判定原语。

## VAR: exc_bian_2021_score_degonly_full

【变体差分】
本列是 full 轨的实例, 也是本三轨家族里最贴近"整篇报道情感"的一格。full (full text) 轨的文本口径 = 标题 prepend 后的整篇正文, 不做实体窗口裁剪。因此本列度量的是: 对每篇银行-金融科技报道的全文, 用 Bian 等 (2021) 中文金融情感词典、在 degonly 规则 (只施加程度副词六级加权, 否定翻转关闭、转折增强关闭, 极性符号绝不翻转) 下打出的带符号情感分, 在按 detect_defacto_cessation 剔除疑似覆盖退出媒体后, 逐银行-年求得的均值。它与 ctx/ss 列共享完全相同的词典、相同的 degonly 规则组合与相同的 exc 停刊剔除逻辑, 唯一差别是文本窗口取全文。留篇门控为 full-only (2026-06-29): 一篇报道是否算作"一篇银行金融科技报道"只看 full 轨判定, 故 full 轨是行宇宙的锚, ctx/ss 为其子集上的条件测度。口径铁律照旧: full 与 ctx/ss 三轨、exc 与 degonly 两臂各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。相对家族 canonical 主情感列 (无 exc 前缀、full 规则的 bian_2021_tone), 本列的双重差分在于既换了样本 (剔停刊媒体) 又换了规则 (仅程度), 因而只作稳健性对照而非主测度。degonly 规则的经济含义是: 承认"极其糟糕/略有改善"这类程度副词会调节情感强度, 但刻意关闭否定翻转与转折增强, 从而检验主结论是否只由程度加权这一条规则支撑; 若主列与本列系数方向一致, 即说明程度规则的取舍不驱动结论。相对同族 ctx/ss 列, full 轨保留整篇正文信息量最大、样本回退最少, 因此在早期试跑 T=2 语料上通常也最少出现零方差退化, 是三轨里数值最稳的一格; 生产 T=19 全量下三轨均正常取值, 差异体现为语境窗口宽窄导致的情感均值系统性偏移而非缺陷。

## VAR: exc_bian_2021_score_degonly_ss

【变体差分】
本列是 ss (same-sentence) 轨的实例。ss 轨的文本口径 = 标题 prepend 后, 只保留"目标银行与金融科技词在同一句内共现"的句子 (同句共现窗, ss_sentence_radius 默认 1), 是三轨里对"银行∧金科同时在场"要求最严的一轨。因此本列度量的是: 在银行与金融科技强同句共现的最窄语境里, Bian 等 (2021) 词典在 degonly 规则 (仅程度副词六级加权, 无否定翻转、无转折增强) 下的带符号情感分, 在剔除疑似覆盖退出媒体后按银行-年聚合的均值。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True, 与 ctx 的回退公理一致, 并共享 n_articles 分母; 若金融科技 AC 自动机为空则 *_is_fallback 全 True 优雅降级。它与 full/ctx 列的差别只在共现判据的严格程度 (ss 最严、ctx 次之、full 无共现约束), 词典、degonly 规则、exc 停刊剔除三者完全一致。口径铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 稳健性轨。早期试跑 T=2 上因同句共现稀疏, ss 轨可能大量回退或零方差, 属预期退化; 生产 T=19 正常。相对家族 canonical 主情感列, 本列在样本 (剔停刊)、规则 (仅程度)、文本窗口 (最严同句共现) 三处叠加偏移, 定位为最保守的稳健性对照。ss 的同句共现判据原语与 stage 13 上游共现硬过滤同源思路但口径独立: stage 13 用 ±句窗邻近共现做丢行硬过滤, 而 ss 轨要求银行与金科严格落在同一句 (extract_bank_fintech_cooccurrence), 二者禁互相复用。判定不对称口径沿用全项目约定: 银行侧带否定与短名过滤, 金科侧用裸 AC 自动机词表。当共现为空回退全文时, 本列数值会向 full 轨靠拢, 这正是回退语义镜像 ctx 的直接后果, 需在解读 ss 列时结合 ss_is_fallback 比例一并判断其代表性。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
