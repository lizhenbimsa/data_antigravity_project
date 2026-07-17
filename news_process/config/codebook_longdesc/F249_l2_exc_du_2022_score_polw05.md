---
family_id: F249
columns:
- exc_du_2022_score_polw05_ctx
- exc_du_2022_score_polw05_full
- exc_du_2022_score_polw05_ss
unit: 情感倾向分值 (无量纲, 归一化至 [-1, 1]); bank-year 级排除停刊媒体后的文章均值
formula: "exc_du_2022_score_polw05{track} = mean_over_surviving_articles( du_2022_score_polw05{track} ), 其中 surviving = 非 de-facto 停刊媒体的文章; du_2022_score_polw05 (逐词) final_score_i = base_score_i * degree_multiplier_i * negation_i (base_score 对政治正面词按 0.5 折算, 其余正负词按 1.0 计), du_2022_score_polw05 = sum(final_score_i) / sum(abs(final_score_i))"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性 exc_* 动态发现块, C.4)
upstream:
- 22_tone_words.parquet (du_2022_score_polw05_full / _ctx / _ss, 文章级词典分)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- attention_media.detect_defacto_cessation (媒体 de-facto 停刊集合 _is_ceased_media)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: "10.1007/s10479-025-06558-z"
  type: "journal"
  authors: "Nguyen, V. D., & Gigliarano, C."
  year: 2025
  title: "Sensitivity-based weighting method for composite indicators"
  venue: "Annals of Operations Research"
- doi: "10.1016/j.jempfin.2024.101517"
  type: "journal"
  authors: "Soebhag, A., Van Vliet, B., & Verwijmeren, P."
  year: 2024
  title: "Non-standard errors in asset pricing: Mind your sorts"
  venue: "Journal of Empirical Finance"
  vol: "78"
  pages_or_artno: "101517"
- doi: "10.1007/s10842-024-00426-5"
  type: "journal"
  authors: "Merkus, E."
  year: 2024
  title: "Gravity Models in International Trade: A Specification Curve Analysis"
  venue: "Journal of Industry, Competition and Trade"
  vol: "24"
  issue: "1"
  pages_or_artno: "17"
- doi: "10.1017/s175577392610054x"
  type: "journal"
  authors: "Beltran, A., Guariso, D., & Guerrero, O. A."
  year: 2026
  title: "Paying the piper: government advertising and media bias"
  venue: "European Political Science Review"
  pages_or_artno: "1-20"
- doi: "10.1080/13504851.2026.2701294"
  type: "journal"
  authors: "Cha, Y., & Wang, T.-X."
  year: 2026
  title: "Can firms offset information asymmetry shocks? Evidence from local newspaper closures"
  venue: "Applied Economics Letters"
  pages_or_artno: "1-7"
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"排除停刊媒体后, 银行-年层面的 Du et al. (2022) 中文金融情感词典倾向", 属情感测度的幸存者偏差 (survivorship bias) 稳健性轨。构念分两层叠加。底层是文章级词典情感分 du_2022_score_polw05: 对每篇报道, 用 Du et al. (2022) 构建并公开的中文金融情感词典对分词后的正文匹配正面词、负面词, 施加否定翻转、程度副词、转折三条中文语言学规则后, 归一化为落在 [-1, 1] 的分值; 其中该词典特有的政治正面词 (political_positive, 约 1,434 词) 以 0.5 的权重计入正侧 (polw05)。上层是本家族真正物化的 exc 聚合: 在 bank-year 内, 仅对来自"未 de-facto 停刊"媒体来源的文章求算术平均, 从而剔除因媒体退出而向存活媒体倾斜的情感均值。之所以需要这一层, 是因为样本期内部分媒体来源在中途停止发稿 (隐性停刊), 若不加处理, 全样本情感均值会掺入幸存者偏差, 并进一步污染以媒体来源暴露构造的 Bartik 类工具变量。数据来源为已过共现硬过滤、已物化三轨文本 (content_full / content_ctx / content_ss) 并经 stage 22 词典打分的文章表, 停刊集合由 attention_media 的 detect_defacto_cessation 依据发稿时间序列的 de-facto 中断检测得到。

【方法学与计算】
计算链路为: stage 22 逐词计算 final_score = base_score * degree_multiplier * negation (base_score 对政治正面词按 0.5 折算即 polw05, 其余正负词按 1.0 计, degree_multiplier 与 negation 分别对应程度副词与否定翻转两条规则, 转折规则作用于分句权重), 再以 sum(final_score) / sum(abs(final_score)) 归一化, 逐篇产出 du_2022_score_polw05_{full,ctx,ss} 三个文章级列 (polw05 权重固化于词典变体构造, 与词典其余正负词共用同一套语言学规则); attention_media 先调用 detect_defacto_cessation 标注每篇文章的 _is_ceased_media, 再在停刊稳健性块 (C.4 动态发现) 中, 对匹配 _SCORE_PATTERNS 的所有文章级情感列 (含本词典分) 逐列在 df_alive = df[_is_ceased_media == 0] 上做 groupby(target_bank, year).mean(), 加 exc_ 前缀写回面板, 得到 exc_du_2022_score_polw05_{track}。契约上, exc_*tone* 情感类列在零文章 bank-year 保持 NaN (不做计数式零填, 与兄弟计数列 n_articles_exc=0 语义区分)。polw05 的 0.5 是研究者选择, 并配套敏感性梯子: 政治词权重 ∈ {0.0, 0.5, 1.0} 三臂 (polw00 / polw05 / polw10) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三臂混进同一 over-identified Hansen J; 该梯子与规则消融梯度正交、不交叉 (三权重均在全语言学规则下计算)。三轨 full/ctx/ss 同理各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J; 留篇门控为 full-only 口径 (2026-06-29): 是否算作一篇银行金科报道只看 full 轨的 LLM 判定, ctx/ss 为 conditional-on-full 的测度/稳健性轨, ss 回退语义镜像 ctx (无银行与金科同句共现时 content_ss 退回全文)。

【文献定位】
词典底座直接采自 Du et al. (2022, Review of Finance) 的中文金融情感词典, 该文既提供词表, 也给出政治正面词信号弱于普通正面词的证据, 是 polw05 折中权重与三权重敏感性检验的依据。词典法情感测度的方法学规范可上溯 Loughran & McDonald (2011, Journal of Finance) 对领域专用金融词典优于通用词表的论证; Ma, Zhang & Zhang (2025) 的中文投资者细粒度情感词典进一步佐证中文金融文本需要本土化、领域化词表, 为本家族选用中文金融专用词典而非通用译词提供当代支撑。exc 这一层的动机与做法则对齐 Heese, Pérez-Cavazos & Peter (2022, Journal of Financial Economics) 对地方报纸停刊 (local newspaper closures) 效应的实证发现: 媒体来源退出报道会系统性改变被覆盖主体后续可观测的信息环境与情感画像, 故须以排除停刊来源的替代测度检验主系数稳定性; ceased_media_frac (停刊媒体文章占比) 与本家族共享同一套 detect_defacto_cessation 停刊判定, 是该文献动机在本项目内的直接映射。 晚近文献在权重取值、停刊排除与应用域三处进一步补强本家族的定位。polw05 的 0.5 属研究者选择, 而复合指标分量权重的设定本身即公认的方法学问题: Nguyen 与 Gigliarano (2025) 指出复合指标聚合中分量权重的取值争议众多而少有彻底解法, 并提出一种由输入对输出方差的贡献比例反推权重的统计方法。此处须诚实声明该文的取径是为权重导出单一有原则的解, 并未主张枚举离散权重阶梯做稳健性, 与本家族三点权重 (0.0 / 0.5 / 1.0) 并排、不分主次的做法取径不同, 故仅作「分量权重不可随手指定」这一问题存在性的方法学邻域参照, 不作本家族做法的依据; 其场景为一般性社会经济复合指标, 不涉情感词典与新闻文本, 亦无中国语境、银行层级与 bank-year 聚合。三臂并排这一做法的直接依据来自 Soebhag 与 Verwijmeren (2024): 该文在资产定价因子模型上枚举断点选择、是否剔除 microcaps、行业调整与再平衡频率等构造路径, 实证记录这些可自由取值的设计选择带来的结果离散 (non-standard error 与 standard error 之比平均超过 1), 主张研究者须清楚交代并论证这些选择而非独断取一; 边界在于其自由度维度为投资组合排序等资产定价构造选项而非情感词典权重, 且原文以枚举上百条路径估计 NSE, 本家族仅枚举三个权重取值, 不构成 NSE 的完整估计。同源地, Merkus (2024) 把规格曲线分析用于国际贸易引力模型, 系统枚举设定选择并展示估计量在整条曲线上的分布, 以判断结论是否被某一设定驱动, 正是本家族「证明主结论不被 0.5 这一取值驱动」的方法原型; 但其枚举维度是控制变量与固定效应设定、规模达上百设定且层级为国家对, 与本家族三点权重阶梯规模不可比。政治正面词何以值得折权, 可由 Beltran、Guariso 与 Guerrero (2026) 提供一条独立的机制性旁证: 该文以墨西哥八家主要报纸逾 20 万篇意见专栏为语料, 以政府广告投放的过度倾斜度量媒体俘获, 发现被俘获媒体对现任总统的负面程度更低、对其主要政治对手的负面程度更高, 提示媒体的政治性正面表述可能反映资助/俘获关系而非基本面信息; 惟原文未构造词典权重、未做任何词类降权, 语境为墨西哥单一国家而非中国, 其偏向以专栏负面语调与广告投放倾斜度量而非词级 political_positive 计数, 且不涉及媒体停刊, 故不作 exc_ 层的依据。exc_ 层则在 Heese et al. (2022) 之外再添一条近期实证: Cha 与 Wang (2026) 以地方报纸停刊作为信息环境冲击, 证实媒体停刊会真实改变可观测的报道集合与信息含量, 支撑「停刊媒体值得单独处理」; 其边界是把停刊当作外生冲击做因果识别、DV 为公司层面信息不对称指标、层级为公司-年且语境为英文地方报业, 而本家族只把停刊媒体作为样本排除条件做并排稳健性, 不做因果。应用域上, Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度并将其用于银行融资条件这一银行层级实证问题, 与本家族「文章级词典语调 → bank-year 均值」的链条同域; 其国别为意大利、语调测度未使用 du_2022 词典亦无 political_positive 词类概念, 且无三轨文本切分与停刊媒体排除, 故只作前沿存在性参照。
## VAR: exc_du_2022_score_polw05_full

【变体差分】
本列为 full 轨: 文章级底分 du_2022_score_polw05_full 取自"标题 prepend + 全文正文"的完整文本 (content_full), 是三轨中信息量最全、也是留篇门控唯一裁定轨的轨道。相对家族内 ctx / ss 两列, 差异仅在底层文本范围: full 用整篇正文, 不做实体窗口或同句裁剪。相对同轨其余政治权重臂 (exc_du_2022_score_polw00_full / _polw10_full), 本列固定 polw05 即政治正面词以 0.5 权重计入正侧, 是 Du et al. (2022) 弱信号折中臂, 亦即历史命名下与无后缀 canonical 字节一致的那一臂 (无后缀为历史命名产物, 非"主")。相对家族外的非-exc 兄弟列 du_2022_polw05_tone_full, 本列多一层停刊排除: 仅对来自未 de-facto 停刊媒体的文章求 bank-year 均值, 因而是幸存者偏差稳健性轨。三轨各自 just-identified 并排、互为稳健性不分主次, 政治权重三臂同样各自 just-identified 并排, 二者均禁混进同一 over-identified Hansen J; 本列在零存活文章的 bank-year 按契约保持 NaN 而非零填。作为 full 轨的 exc 稳健列, 本列在实证中通常与非-exc 兄弟 du_2022_polw05_tone_full 高度相关, 二者系数与显著性的一致性正是稳健性论证的目标: 若排除停刊媒体后主结论不变, 则可排除媒体退出驱动的幸存者偏差解释。分母口径上, 本列的 bank-year 均值以该格内来自存活媒体的文章数为隐含权数, 与 n_articles_exc 计数列同源但语义不同 (前者是情感均值, 后者是留存篇数)。因此在阅读该列时须与 ceased_media_frac (停刊媒体文章占比) 并看: 停刊占比越高的 bank-year, exc 均值相对全样本均值的偏移越具诊断意义。

## VAR: exc_du_2022_score_polw05_ctx

【变体差分】
本列为 ctx 轨: 文章级底分 du_2022_score_polw05_ctx 取自"标题 prepend + 实体上下文窗口"文本 (content_ctx), 即仅保留目标银行与金科实体邻近窗口内的正文, 相对 full 轨剔除了远离实体的段落, 用以检验情感信号是否被无关正文稀释或污染。相对家族内 full 列, 差异纯在底层文本范围 (实体窗口 vs 全文); 相对 ss 列, ctx 采用实体上下文窗口而非银行与金科严格同句共现窗口。政治权重固定为 polw05 (政治正面词 0.5 权重), 停刊排除逻辑与 full 列一致 (仅对未停刊媒体文章求 bank-year 均值), 故本列是"实体窗口 + 幸存者偏差稳健"的双重稳健性轨。按 full-only 门控口径, ctx 轨为 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集, per-track 列照算。三轨各自 just-identified 并排、互为稳健性不分主次, 政治权重三臂各自 just-identified 并排, 二者均严禁混进同一 over-identified Hansen J; 零存活文章 bank-year 保持 NaN。ctx 轨的价值在于回答"情感是否来自与银行金科事件真正相关的正文": 若 full 与 ctx 的 exc 稳健系数一致, 则说明主信号并非由报道中与该银行无关的宏观或行业段落堆砌而成。相对政治权重 polw00 (完全剔除政治正面词) 与 polw10 (政治正面词全权计入) 两臂, 本列取 0.5 的折中权重, 既不因政治宣传式正面词过度抬高情感, 也不将其视作全无信号; 三臂在实体窗口文本上并排, 用以证明政治词权重取值不驱动结论。零存活文章 bank-year 保持 NaN 而非零填, 以免把"无存活媒体覆盖"误读为"情感中性"。

## VAR: exc_du_2022_score_polw05_ss

【变体差分】
本列为 ss 轨: 文章级底分 du_2022_score_polw05_ss 取自"标题 prepend + 银行与金科同句共现窗口 (±N 句)"文本 (content_ss), 是三轨中最严格的语义裁剪轨, 只保留银行实体与金科实体在同一句 (或指定同句半径) 共现的正文, 用以逼近"确与该银行金科事件相关"的情感信号。相对 full 全文与 ctx 实体窗口, ss 的文本范围最窄; 其回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 退回全文 body 且 ss_is_fallback=True (与 ctx 共享 n_articles 分母口径)。政治权重固定 polw05 (政治正面词 0.5 权重), 停刊排除逻辑与其余两轨一致, 故本列是"严格同句 + 幸存者偏差稳健"的双重稳健性轨。按 full-only 门控, ss 为 conditional-on-full 测度轨。三轨各自 just-identified 并排、互为稳健性不分主次, 政治权重三臂各自 just-identified 并排, 二者均禁混进同一 over-identified Hansen J; 零存活文章 bank-year 按契约保持 NaN, 不做计数式零填。ss 轨是三轨中语义最保守的轨道, 其代价是可用文章数最少、在浅面板 (T=2 开发样本) 上易退化为高缺失或零方差, 但在生产 T=19 全量语料上提供"确与银行金科同句相关"的最干净情感切片。将 full / ctx / ss 三轨的 exc 稳健系数并排, 可从"全文—实体窗口—严格同句"三个收窄尺度上检验情感信号的稳健性: 若信号随文本收窄而消失, 则提示原始信号可能来自与该银行金科无关的段落。回退语义须谨记镜像 ctx: 无同句共现的文章其 content_ss 退回全文, 故 ss 与 ctx 在无共现篇上会趋同, 这是设计使然而非缺陷。政治权重 polw05 与另两臂并排, 仍受禁混同一 over-identified Hansen J 的铁律约束。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Nguyen, V. D., & Gigliarano, C. (2025). Sensitivity-based weighting method for composite indicators. Annals of Operations Research. https://doi.org/10.1007/s10479-025-06558-z
Soebhag, A., Van Vliet, B., & Verwijmeren, P. (2024). Non-standard errors in asset pricing: Mind your sorts. Journal of Empirical Finance, 78, 101517. https://doi.org/10.1016/j.jempfin.2024.101517
Merkus, E. (2024). Gravity Models in International Trade: A Specification Curve Analysis. Journal of Industry, Competition and Trade, 24(1), 17. https://doi.org/10.1007/s10842-024-00426-5
Beltran, A., Guariso, D., & Guerrero, O. A. (2026). Paying the piper: government advertising and media bias. European Political Science Review, 1-20. https://doi.org/10.1017/s175577392610054x
Cha, Y., & Wang, T.-X. (2026). Can firms offset information asymmetry shocks? Evidence from local newspaper closures. Applied Economics Letters, 1-7. https://doi.org/10.1080/13504851.2026.2701294
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
