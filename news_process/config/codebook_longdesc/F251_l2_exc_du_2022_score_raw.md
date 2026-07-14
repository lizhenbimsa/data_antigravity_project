---
family_id: F251
columns:
- exc_du_2022_score_raw_ctx
- exc_du_2022_score_raw_full
- exc_du_2022_score_raw_ss
unit: 情感倾向分值 (无量纲, 词典法自归一化, 幅度口径 Σ|base| 归一化差, 非计数口径)
formula: "exc_du_2022_score_raw_track = mean_媒体 a 不属于 ceased_set 覆盖退出集合 du_2022_score_raw_track(a); 逐 (target_bank, year) 分组均值, ceased_set = detect_defacto_cessation(疑似退出覆盖媒体) 的 confirmed ∪ suspected 并集; du_2022_score_raw = Du(2022) 中文金融情感词典在关闭全部语言学规则(否定翻转/程度副词/转折)下的裸极性得分"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性 C.4 动态发现循环, 经 detect_defacto_cessation)
upstream:
- 22_tone_words.parquet (article-level du_2022_score_raw_{full,ctx,ss})
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
- 40_panel_export_main (bank-year 聚合宿主)
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
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
本家族三列度量的是「剔除疑似退出覆盖媒体后、以 Du et al. (2022) 中文金融情感词典裸口径 (raw) 计得的银行-年度情感均值」。名字里三段前缀各承载一层语义: exc 段标记停刊稳健性 (cessation robustness) 口径, 即分子样本只保留仍在持续覆盖银行-金科话题的媒体、把疑似退出覆盖的来源整体剔出; du_2022 段标记情感测度所依据的词典, 即 Du、Huang、Wermers 与 Wu (2022) 发表于 Review of Finance 的中文金融情感词典; raw 段标记该词典七条规则消融梯度中的裸变体, 即在既不做否定翻转、也不做程度副词加权、更不做转折让步调整的最朴素配置下、以词典基础极性得分 (base score, 而非命中词计数) 的绝对值之和 Σ|base| 做自归一化而得的幅度口径得分, 且仍沿用政治正面词降权 (0.5) 相对普通正负极性词 (1.0) 的差异化加权, 与「命中词计数之差」的纯词频口径 (即家族内的 msent_score 计数口径零规则变体) 并非同一测度、不可混淆。三者叠加, 构成一条同时对「样本框选择偏误」与「语言学规则依赖」两个方向都做敏感性剥离的情感稳健性轨。

【方法学与计算】
计算分两阶段。第一阶段在文章级完成: 词典引擎在 stage 22 (tone_words) 对每篇报道的三轨文本 (content_full 标题加正文全文、content_ctx 标题加实体窗、content_ss 标题加银行与金科同句共现窗) 分别匹配 Du (2022) 词典的正负极性词, 在关闭全部语言学规则的 raw 配置下, 以命中词的词典基础极性得分 (base score, 而非命中词个数) 之绝对值总和 Σ|base| 做自归一化, 得到幅度口径的文章级 du_2022_score_raw_{full,ctx,ss} (该归一化仍保留政治正面词 0.5 权重相对普通极性词 1.0 权重的差异化加权; 与之口径不同的纯计数零规则变体是家族内的 msent_score, 二者同为零规则但归一化基准不同, 不可等同)。第二阶段在面板级完成: attention_media 模块先经 detect_defacto_cessation 识别疑似退出覆盖的媒体集合 ceased_set (数据驱动判据为「末次覆盖年早于样本末年减去阈值间隔且累计报道数不少于十篇」, 与国家新闻出版署注销/停办/休刊名录做交叉验证, 但未经名录证实的 suspected 亦保守并入排除集), 随后在停刊稳健性动态发现循环中, 仅对来自非停刊媒体 (_is_ceased_media == 0) 的存活文章、按 target_bank 与 year 分组求 du_2022_score_raw 各轨均值, 生成 exc_ 前缀列。因此该列与不剔除媒体的同名基准列之间的差, 精确隔离了「疑似退出覆盖媒体」这一样本框对情感测度的贡献。比例类与情感类的 exc_ 列在零文章银行-年度按契约保留 NaN、不做零填 (只有计数类 n_articles_exc 走计数零填契约), 以免把「无存活报道」误记为「情感中性」。

【文献定位】
情感测度的词典本体锚定 Du et al. (2022) 发表于 Review of Finance 的工作: 该文论证通用情感词典迁移到中文金融文本时的领域特异性缺口, 并据以构造专门的中文金融情感词典, 是本家族 du_2022 前缀的唯一出处与权重依据。词典法在中文投资者文本上的持续演进由 Ma et al. (2025) 的细粒度投资者情感词典与 Sun et al. (2025) 融合词典知识与中性特征的预训练情感分析所印证, 二者共同支撑了「以规则消融梯度剥离语言学规则依赖」的稳健性动机。领域特异极性词表的自动归纳方法可追溯至 Hamilton et al. (2016) 从无标注语料诱导领域情感词典的框架, 为 raw 裸口径提供了方法学参照。而 exc_ 前缀所隐含的样本框剥离动机, 则直接根植于 Heese et al. (2022) 关于地方报纸退出导致监督真空、进而系统性改变可观测文本供给的发现: 在以媒体情感为核心解释变量的面板中, 媒体来源消失会引入幸存者偏误, 必须以剔除退出媒体的替代口径检验系数稳定性。需强调停刊稳健性轨、三轨文本轨与规则消融梯度三者是并排的规格稳健性设计: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同口径混进同一 over-identified Hansen J 过度识别检验。

## VAR: exc_du_2022_score_raw_ctx

【变体差分】
本列取三轨文本中的 ctx 轨, 即上游文章级情感在 content_ctx (标题 prepend 后加实体上下文窗口) 上计得的 du_2022_score_raw_ctx, 再经停刊稳健性剔除后按银行-年度求均值。相对 full 轨, ctx 轨把参与词典匹配的文本收窄为围绕目标实体的上下文窗, 从而抑制远离银行-金科语境的无关段落对极性计数的稀释; 相对 ss 轨, ctx 轨的窗口口径以实体窗为界、并非严格要求银行与金科同句共现, 因而覆盖面居于 full 与 ss 之间。三轨在留篇门控上一致遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨判定, ctx 轨降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的 ctx 情感列照常逐轨独立计算。本列同时叠加 exc_ 的停刊剥离, 因此它检验的是「同时收窄到实体上下文、又剔除疑似退出媒体」这一双重保守口径下, du_2022 裸情感的稳健性。ctx 轨与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。需注意在盘上 T=2 开发语料上 ctx 轨可能因样本稀薄出现零方差退化, 属预期现象, 生产 T=18 全量语料下方恢复正常识别力。就使用建议而言, 本列适合作为主结果的规格稳健性并排臂, 用以证明主情感系数不被「全文口径纳入无关段落」与「疑似退出媒体的样本框」两个方向同时驱动, 而非作为独立的主测度进入单一回归右手边。

## VAR: exc_du_2022_score_raw_full

【变体差分】
本列取三轨文本中的 full 轨, 即上游文章级情感在 content_full (标题 prepend 后加全文正文) 上计得的 du_2022_score_raw_full, 再经停刊稳健性剔除后按银行-年度求均值。full 轨是三轨中唯一承担留篇门控职责的轨道: 依 full-only 口径 (2026-06-29), 一篇报道是否被判为一篇银行金科报道、进而计入 n_articles 分母, 只看 full 轨的判定; ctx 与 ss 两轨在此意义上皆是 conditional-on-full 的从属轨。因此在三轨中, full 轨对应的样本框最完整、覆盖面最广, 其极性计数吸纳了报道全文而非仅上下文窗或同句共现窗, 代价是可能纳入更多远离银行-金科语境的段落。本列在 full 全文口径之上再叠加 exc_ 停刊剥离, 度量的是「保留全文、但剔除疑似退出覆盖媒体」下 du_2022 裸情感的稳健性, 是本家族三列中最接近基准情感、仅在样本框上做保守收缩的一支。与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。raw 裸口径意味着本列不做否定翻转、程度副词与转折调整, 与规则消融梯度的其余变体正交并排, 亦不得与任何规则变体合并进同一过度识别式。作为家族中样本框收缩最温和的一支, 本列常被用作停刊稳健性检验的首要参照: 若它与不剔除媒体的基准情感列在符号与显著性上一致, 即为「媒体退出未系统性驱动主结论」提供证据。

## VAR: exc_du_2022_score_raw_ss

【变体差分】
本列取三轨文本中的 ss 轨, 即上游文章级情感在 content_ss (标题 prepend 后加银行与金科同句共现的正负 N 句窗) 上计得的 du_2022_score_raw_ss, 再经停刊稳健性剔除后按银行-年度求均值。ss 轨是三轨中口径最严的一支: 只有当银行与金科词在同一句子及其邻近窗内共现时, 对应句段才进入词典匹配, 因而它最精准地锁定「银行确实在谈论金融科技」的文本, 但也最易因共现稀缺而退化。ss 轨遵循镜像 ctx 的回退语义: 当一篇报道不存在银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母; 当金科自动机为空时, is_fallback 全真、优雅降级。留篇门控上 ss 轨同样服从 full-only 口径, 是 conditional-on-full 的测度与稳健性轨, 行宇宙为 full 留篇集子集, per-track 的 ss 情感列逐轨独立计算。本列再叠加 exc_ 停刊剥离, 检验「严格同句共现、又剔除疑似退出媒体」双重最保守口径下 du_2022 裸情感的稳健性。ss 轨与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 在盘上 T=2 开发语料上 ss 轨因共现稀薄而近零方差属预期退化, 生产 T=18 语料下恢复识别力。因口径最严, 本列在三轨中方差通常最小、缺失最多, 解读时须结合同句共现回退比例, 避免把大量回退到全文的样本误当作真实同句情感; 它最适合作为「银行确实在谈金融科技」这一最狭窄语境下的稳健性佐证轨。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
