---
family_id: F250
novelty_exempt_rationale: "exc_ 前缀家族是 du_2022 词典情感主测度叠加停刊媒体排除约束与政治词权重梯子(polw10)的消融/稳健性变体, 测度定义的学术依据已在母族 Du et al. (2022) 词典文献及既有引文池中给出, 非独立新构念, 无需追加 2023+ 新引文。"
columns:
- exc_du_2022_score_polw10_ctx
- exc_du_2022_score_polw10_full
- exc_du_2022_score_polw10_ss
unit: 情感倾向分值 (无量纲, 自归一化 ∈ [-1, +1]; 排除疑似停刊媒体后的银行-年均值)
formula: "exc_du_2022_score_polw10{track} = mean_{i ∈ alive-media articles}( du_2022_score_polw10{track}_i ); 其中 du_2022_score_polw10 = (pos_weighted - neg) / (pos_weighted + neg), pos_weighted = pos_ordinary + 1.0 * pos_political; alive = 未被判定为疑似/确证停刊媒体的文章 (_is_ceased_media == 0)"
producer: news_process/pipeline/panel/attention_media.py::process (子步骤 C — 停刊稳健性; 动态发现 _SCORE_PATTERNS 前缀 du_2022_score_ 后加 exc_ 前缀)
upstream:
- 22_tone_words.parquet (du_2022_score_polw10_full/_ctx/_ss 文章级词典分)
- 42_cessation_report (detect_defacto_cessation → _is_ceased_media 停刊标记)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
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
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1080/13504851.2026.2701294"
  type: "journal"
  authors: "Cha, Y., & Wang, T.-X."
  year: 2026
  title: "Can firms offset information asymmetry shocks? Evidence from local newspaper closures"
  venue: "Applied Economics Letters"
  pages_or_artno: "1-7"
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
本家族测度记为 exc_du_2022_score_polw10, 是"停刊媒体稳健性"口径下、以政治词全权计入 (w_pol=1.0) 的 Du 等 (2022) 中文金融情感词典净极性得分, 在银行-年层面按存活媒体子样本聚合而成的稳健性变量。它服务于一个明确的构念问题: 当同一银行在同一年份的媒体报道语调受制于"哪些媒体在发声"时, 若把后来被判定为疑似或确证停刊 (注销/停办/休刊) 的媒体来源的报道全部剔除, 银行金科报道的整体情感倾向是否依然稳定。这一构念定位把两条独立的度量链条焊接在一起: 一条是文章级词典情感的构造 (Du 等 2022 词典 × 政治词权重梯子), 另一条是媒体来源存活性的判定 (de-facto cessation 检测)。前者决定"每篇报道有多正/多负", 后者决定"哪些报道进入均值分母"。因此 exc_ 前缀不是一个新的语义维度, 而是对既有 du_2022_score 主测度施加的样本约束: 分子分母同步限制在存活媒体文章上。

数据来源上, 文章级底层列 du_2022_score_polw10 由 22_tone_words 阶段的 compute_dict_scores 产出, 以 jieba (冻结版本 0.42.1) 分词后, 对每篇报道在 Du 等 (2022) 词典的三类词表 (普通正面 2,235 词 / 负面 2,986 词 / 政治正面 1,434 词) 上计数。存活性标记 _is_ceased_media 由 attention_media 模块的 detect_defacto_cessation 依据数据内媒体活跃度并交叉核验新闻出版署 (NPPA) 出版状态得到; 其保守口径是: 未经 NPPA 证实的"疑似退出"媒体亦全量纳入排除集 (ceased_all = confirmed ∪ suspected)。正因如此, 本列与兄弟列 ceased_media_frac / n_articles_exc 一样, 应解读为"疑似退出覆盖媒体"的稳健性口径, 不可在论文中表述为严格停刊 (publication cessation) 口径。

【方法学与计算】
计算分两步。第一步文章级: du_2022_score_polw10 = (pos_weighted − neg) / (pos_weighted + neg), 其中 pos_weighted = pos_ordinary + 1.0 × pos_political。这是一个自归一化净极性, 值域 [−1, +1], 越大越正面; 分母为加权正负词总量, 天然对文本长度免疫, 无需外部标准化。政治词以权重 1.0 计入正侧, 即把 Du 等 (2022) 识别出的 1,434 个政治性正面词与普通正面词等量齐观。第二步聚合级: 在剔除 _is_ceased_media == 1 的文章后, 对每个 (target_bank, year) 单元取该文章级分数的算术均值, 得到 exc_du_2022_score_polw10。跨类重叠词 (positive ∩ negative) 按用户 2026-06-24 决策保留并两侧各计一次, 使净分子对该类词守恒为 0、拉向中性。缺失契约上, 情感类 exc_*tone*/exc_*score* 列在单元内无存活媒体文章时保持 NaN (不做零填, 与计数类 n_articles_exc 的零填契约相反), 以免把"无观测"误读为"中性 0"。

政治词权重 w_pol=1.0 是三点权重梯子 {0.0, 0.5, 1.0} 的上端臂。依据 Du 等 (2022) 的发现——政治正面词的信号强度弱于普通正面词——生产口径 canonical 取 0.5 (polw05, 亦即无后缀历史命名的 du_2022_score); 0.0 与 1.0 两臂做敏感性检验。三权重各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同权重臂混入同一 over-identified Hansen J 的过度识别检验; 该梯子与规则消融梯度 (否定/程度/转折) 正交、不交叉, 三权重均在全语言学规则下计算以避免列数爆炸。同理, 本家族的三条文本轨 full/ctx/ss 亦为互为稳健性的并排轨, 禁混同一 Hansen J。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否算作"银行金科报道"仅由 full 轨的 LLM 判定决定, ctx/ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。

【文献定位】
本测度处在中文金融文本情感度量与媒体环境识别两支文献的交叉点。词典侧的直接锚点是 Du 等 (2022) 发表于 Review of Finance 的中文金融情感词典, 其核心贡献是论证情感度量的语言与领域特异性, 并首次系统区分政治性正面词与普通正面词的信号差异——这正是政治词权重梯子的理论根据。方法学上, 词典法与机器学习/大模型情感抽取的相对优劣是持续争论: Loughran 与 McDonald (2011) 奠定了领域特定词典相对通用词典的必要性, Frankel 等 (2022) 则系统比较词典法与机器学习在披露情感上的表现, 提示词典法的透明性与可复现性优势。Ma 等 (2025) 构建的细粒度中文投资者情感词典 CN-FSD 代表了该支文献 2024 年后的最新推进。媒体环境侧, exc_ 口径回应了媒体来源构成的内生性: Heese 等 (2022) 证明地方报纸退出会实质改变企业行为的曝光概率, 说明"哪些媒体在发声"本身携带信息; Qin 等 (2018) 与 Piotroski 等 (2015) 则揭示中国语境下媒体偏向与政治性信息压制的结构, 后者尤其与政治词权重的敏感性检验形成呼应——若政治性正面语调部分源于对负面信息的压制, 则调低其权重 (polw00) 与调高其权重 (polw10) 的对照能界定主结论对该机制的稳健区间。 晚近文献在停刊排除、权重梯子与应用域三处补入近期锚点。exc_ 口径在 Heese 等 (2022) 之外再得一条新证: Cha 与 Wang (2026) 以地方报纸停刊作为信息环境冲击做实证, 直接证实媒体停刊是会改变可观测报道集合与信息含量的真实事件, 支撑「将退出发声的媒体来源值得单独处理」这一设计前提; 其边界须写明: 原文把停刊当作外生冲击做因果识别、DV 为公司层面的信息不对称指标、层级为公司-年且语境为英文地方报业, 而本家族只把 _is_ceased_media == 1 的报道作为样本排除条件做并排稳健性, 不做因果推断, 且本项目的排除集采保守口径 (confirmed 与 suspected 并入), 应表述为「疑似退出覆盖媒体」而非严格停刊。三点权重梯子作为研究设计的方法学依据来自 Soebhag 与 Verwijmeren (2024): 该文在资产定价因子模型上自行枚举断点选择、是否剔除 microcaps、行业调整与再平衡频率等构造路径, 实证记录这些研究者自由度带来的结果离散 (non-standard error 与 standard error 之比平均超过 1), 主张研究者须清楚交代并论证这些选择而非独断取一, 本家族在词典政治词权重这一自由度上并排 polw00 / polw05 / polw10 即该主张的落地; 边界在于其自由度维度为投资组合排序等资产定价构造选项而非情感词典权重, 且原文以枚举上百条路径估计 NSE, 本家族仅三个权重取值, 不构成 NSE 的完整估计, 国别与数据层级亦不同。与之互补的是 Merkus (2024) 把规格曲线分析用于国际贸易引力模型, 系统枚举设定选择并展示估计量在整条曲线上的分布, 以判断结论是否被某一设定驱动, 与本家族以 polw10 上端臂对照 polw00 下端臂、界定主结论稳健区间的思路同源; 惟原文枚举的是控制变量与固定效应设定、规模达上百设定且层级为国家对, 与本家族三点阶梯规模不可比, 亦不涉文本测度。应用域上, Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度并把它用于银行融资条件这一银行层级实证问题, 为本家族「文章级词典净极性 → 银行-年聚合」的链条提供近期同域实践; 其国别为意大利、语调测度未使用 Du 等 (2022) 词典亦无政治正面词类概念, 且无 full/ctx/ss 三轨切分与停刊媒体排除, 故仅作前沿存在性参照, 不作本家族任一构造细节的依据。
## VAR: exc_du_2022_score_polw10_full

【变体差分】
本列是 exc_du_2022_score_polw10 家族的 full 轨。full 轨的文本单元 = 标题 prepend 后的全文正文 (content_full), 即在 14_materialize_ctx 阶段把报道标题前置拼接到正文之前再整体计分, 覆盖整篇报道的全部词汇。相对家族内的 ctx/ss 两条轨, full 轨信息面最宽、词频基数最大, 因而词典分子分母的样本量最充分, 在早期试跑盘面 T=2 的开发样本上方差也最不易退化。full 轨在本项目中承担 canonical 首要轨的角色: 留篇门控 (是否算一篇银行金科报道) 完全由 full 轨的 LLM 判定决定 (full-only 口径, 2026-06-29), ctx/ss 的行宇宙是 full 留篇集的子集。就本列而言, 差分维度落在两处: 其一是政治词权重固定为 1.0 (polw10 上端臂, 政治正面词与普通正面词等量计入正侧), 区别于 canonical 的 polw05 与下端臂 polw00; 其二是 exc_ 样本约束——分子分母同步剔除疑似/确证停刊媒体的报道 (_is_ceased_media == 1), 使本列与不加约束的全样本 du_2022_score_polw10_full 形成停刊稳健性对照。三权重臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; full/ctx/ss 三轨亦同此铁律。就解读而言, 本列与全样本 du_2022_score_polw10_full 之差, 度量的是"疑似停刊媒体报道对该银行当年语调的边际贡献"; 若两者接近, 说明主测度不被少数将退出的媒体来源驱动。政治词以全权计入意味着本列对含政治性正面表述 (如政策支持、监管肯定) 的报道给予最大正向读数, 因而它是权重梯子中对官方语调最敏感的一臂。单元内无存活媒体文章时本列保持 NaN, 不做零填。

## VAR: exc_du_2022_score_polw10_ctx

【变体差分】
本列是 exc_du_2022_score_polw10 家族的 ctx 轨。ctx 轨的文本单元 = 标题 prepend 后的实体上下文窗口 (content_ctx), 即只保留目标银行实体命中位置周边的窗口文本参与计分, 而非整篇正文。相对 full 轨, ctx 轨把词典计数聚焦到与目标银行直接相关的语段, 削减了与银行无关的背景性词汇对情感均值的稀释, 因而更贴近"关于这家银行的语调"这一构念, 但代价是词频基数更小、在早期试跑 T=2 盘面样本上更易出现方差收缩甚至零方差退化 (生产 T=19 正常展开)。ctx 轨在项目定位上为 conditional-on-full 的稳健性/测度轨: 其留篇宇宙是 full 留篇集的子集, per-track 列照常计算但不参与留篇门控。本列的差分维度与 full 列一致落在两处——政治词权重固定为 1.0 (polw10 上端臂) 且施加 exc_ 停刊媒体排除约束 (仅存活媒体文章进入银行-年均值), 唯一区别是文本轨从全文正文换为实体上下文窗口。ctx 与 full/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 三权重梯子同此铁律。把文本轨收窄到实体窗口后再叠加停刊媒体排除, 本列刻画的是"仅就直接谈及该银行的语段、且只保留存活媒体来源时"的政治词全权情感读数, 因而它同时对样本选择 (媒体存活) 与语义聚焦 (实体窗口) 两个维度施加约束, 是家族内比 full 轨更保守的稳健性切片。单元内无存活媒体文章时保持 NaN, 不做零填。

## VAR: exc_du_2022_score_polw10_ss

【变体差分】
本列是 exc_du_2022_score_polw10 家族的 ss 轨。ss 轨的文本单元 = 标题 prepend 后、银行与金科同句共现窗口 (content_ss): 只保留目标银行与金融科技词在同一句 (可含 ±N 句半径, 由 config 的 ss_sentence_radius 控制, 默认 1) 共现的语段参与计分, 是三轨中语义约束最严、文本面最窄的一轨。其回退语义镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback=True (与 n_articles 共享分母); 当金科词表 FINTECH_AC 为空时 *_is_fallback 全 True 优雅降级。正因约束最严, ss 轨在早期试跑 T=2 盘面上退化最明显 (常见零方差), 但在生产 T=19 上它提供了"银行与金科被同句提及时的语调"这一最精确的构念切片。本列差分维度与家族其余两列一致: 政治词权重固定为 1.0 (polw10 上端臂) 且施加 exc_ 停刊媒体排除约束, 差异仅在文本轨为同句共现窗口。ss 属 conditional-on-full 测度轨, 留篇宇宙为 full 留篇集子集。ss 与 full/ctx 三轨、以及三权重臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。作为三轨中约束最严的一轨叠加 exc_ 停刊排除与 polw10 政治词全权三重设定, 本列是整个家族里样本最窄、语义最聚焦的稳健性变量, 主要用途是检验主结论在最严苛切片下是否仍然成立; 其读数在盘面早期试跑样本上易退化, 解读须以生产 T=19 全量为准, 不宜据 T=2 的零方差表现下判断。单元内无存活媒体文章时保持 NaN, 不做零填。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Cha, Y., & Wang, T.-X. (2026). Can firms offset information asymmetry shocks? Evidence from local newspaper closures. Applied Economics Letters, 1-7. https://doi.org/10.1080/13504851.2026.2701294
Soebhag, A., Van Vliet, B., & Verwijmeren, P. (2024). Non-standard errors in asset pricing: Mind your sorts. Journal of Empirical Finance, 78, 101517. https://doi.org/10.1016/j.jempfin.2024.101517
Merkus, E. (2024). Gravity Models in International Trade: A Specification Curve Analysis. Journal of Industry, Competition and Trade, 24(1), 17. https://doi.org/10.1007/s10842-024-00426-5
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
