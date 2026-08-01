---
family_id: F248
columns:
- exc_du_2022_score_polw00_ctx
- exc_du_2022_score_polw00_full
- exc_du_2022_score_polw00_ss
unit: 情感倾向分值 (无量纲, 归一化于 [-1, +1]), bank-year 级排除停刊媒体后的算术均值
formula: "exc_du_2022_score_polw00{track} = mean_over_articles{ i : media(i) ∉ ceased_set } ( du_2022_score_polw00{track}_i ); 其中 du_2022_score_polw00 = Σ(final_score) / Σ|final_score| ∈ [-1,+1], pos_weighted = pos_ordinary + 0.0 * pos_political (政治正面词权重 w_pol=0.0, 即完全剔除)"
producer: news_process/pipeline/panel/attention_media.py (exc_* 停刊排除聚合, C.4 动态发现块) ← 上游文章级 news_process/pipeline/sentiment/tone_words.py::classify_batch → _analyze_single_article → _compute_sentiment_with_rules (polw 变体经 _political_variant_dict 生成)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_score_polw00_{full,ctx,ss})
- 40_panel 停刊媒体检测 (detect_defacto_cessation → ceased_set)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
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
- doi: "10.1111/acfi.13230"
  type: "journal"
  authors: "Yan, L., Ma, Y., Li, C., & Tang, G."
  year: 2024
  title: "Media abnormal tone and cross section of stock returns: Evidence from China"
  venue: "Accounting & Finance"
  vol: "64"
  issue: "3"
  pages_or_artno: "2671-2698"
new_dois: []
novelty_exempt_rationale: "exc_ 前缀的停刊媒体排除稳健性变体家族, 叠加于已是消融臂的 du_2022_score_polw00 (政治词零权重), 其测度定义 (词典/归一化公式/三条语言学规则) 依据母族与词典原始文献 Du et al. (2022), 停刊排除逻辑本身是聚合层稳健性设计而非独立学术构念, 无需追加新文献。"
---

## CORE

【构念与来源】
本家族是「排除停刊媒体后的 du_2022 词典情感均值」在政治词零权重臂 (polw00) 上的三轨落地。构念可拆为三层。最内层是文章级情感测度 du_2022_score: 采用 Du、Huang、Wermers 与 Wu (2022) 为中文财经文本构建的领域专用情感词典对每篇报道打分, 对匹配到的每个情感词施加否定翻转、程度副词乘子与转折增强三条语言学规则后, 取加权得分的归一化比值 Σ(final) / Σ|final|, 值域严格落在 [-1, +1], 正号表示报道语调偏正面、负号偏负面、零表示中性或无匹配。中间层是政治词权重臂: Du et al. (2022) 的词典把正面词进一步分为普通正面词与政治正面词 (political_positive, 约 1,434 词), 并给出政治正面词的市场信号弱于普通正面词的实证发现。生产口径对政治正面词赋 0.5 权重计入正侧, 而 polw00 臂把该权重设为 0.0, 即把政治正面词从正侧完全剔除、只保留普通正面词与全部负面词参与打分。最外层是面板聚合与停刊排除: 在 bank-year 面板构建阶段, 先由 de-facto 停刊检测程序识别出在样本期内事实上停止发稿的媒体来源集合 (ceased_set), 再对每个银行-年份, 仅在「非停刊媒体」发布的报道子集上对文章级 du_2022_score_polw00 取算术均值, 得到本列。前缀 exc 即 exclude-ceased 之意。

【方法学与计算】
计算链路分两段。文章级一段由 tone_words.py 的 classify_batch 逐篇分派至 _analyze_single_article、再落到 _compute_sentiment_with_rules 承担: 对三轨文本 (content_full / content_ctx / content_ss) 分别做分词与词典匹配, 逐词判定基准极性、施加三条规则得到 final_score, 累加得净得分与加权幅度和, 归一化得 du_2022_score_polw00_{track}; polw00 臂通过 _political_variant_dict 在装载词典时令政治正面词的贡献乘以 0.0。面板级一段由 attention_media.py 的停刊稳健性块承担: detect_defacto_cessation 依据发稿间断等信号给出 ceased_set, 随后在 df_alive = 剔除停刊媒体后的文章集上按 target_bank × year 分组对每一个符合 _SCORE_PATTERNS 前缀 (含 du_2022_score_) 且非加权变体 (排除 _w / _mw_ / _idf_) 的文章列取均值, 加 exc_ 前缀写回面板, 故本列的分母是「该银行该年非停刊媒体报道篇数」而非全部报道篇数。这是一条幸存者偏差稳健性轨: 若停刊媒体系统性地偏正面或偏负面, 全样本均值会被存活媒体的语调结构污染, 排除停刊媒体后重算可检验主结论是否被媒体退出所驱动, 呼应 Fang 与 Peress (2009) 关于媒体覆盖结构影响横截面测度的关切。留篇口径与全项目 full-only 门控 (2026-06-29) 一致: 是否判为一篇银行金科报道只看 full 轨的 LLM 判定, ctx/ss 为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。

【文献定位】
本测度立足三支文献。其一是中文财经情感词典本身: Du et al. (2022, Review of Finance) 是本家族词典与政治词权重设定的直接来源, 其核心贡献是论证情感词典必须兼顾语言特异性与领域特异性, 并揭示政治正面词的信号强度弱于普通正面词——这正是政治词权重梯子存在的理论依据。其二是词典法情感度量的方法学传统: Loughran 与 McDonald (2011, Journal of Finance) 确立了以领域词典而非通用词典度量金融文本语调的范式, Loughran 与 McDonald (2016, Journal of Accounting Research) 的综述进一步梳理了词典法相对机器学习法的可解释性与可复现性优势, 二者共同支撑本家族以透明、可审计的加权计数取代黑箱打分。其三是媒体语调的资产定价含义与媒体结构稳健性: Tetlock (2007, Journal of Finance) 奠定了媒体语调预测市场的经验基础, 而 Fang 与 Peress (2009, Journal of Finance) 提示媒体覆盖的横截面结构本身是一个需要控制的维度, 二者共同论证了「排除停刊媒体重算」这一稳健性设计的必要性。方法学铁律: 政治词权重三臂 (polw00 / polw05 / polw10) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 检验; 三轨 (full / ctx / ss) 同理各自 just-identified 并排, 亦禁混同一 over-identified Hansen J; 政治词权重梯子与规则消融梯度刻意正交、不交叉 (三权重均在全语言学规则下计算, 避免列数组合爆炸)。 晚近文献在本家族的三个环节上各自补强。政治词零权重臂的机制依据可由 Beltran、Guariso 与 Guerrero (2026) 旁证: 该文以墨西哥八家主要报纸逾 20 万篇意见专栏为语料, 以政府广告投放的过度倾斜度量媒体俘获, 发现被俘获媒体对现任总统的负面程度更低、对其主要政治对手的负面程度更高, 并有黑名单的质性证据佐证, 提示媒体的政治性正面表述可能反映资助关系而非基本面信息。须注意其边界: 原文未构造任何词典权重、亦未做词类降权, 语境为墨西哥单一国家 (与中国党媒-市场化媒体的制度结构不同), 其偏向以专栏负面语调与广告投放倾斜度量而非词级 political_positive 计数, 故只作 w_pol<1 乃至 polw00 完全剔除这一取值区间的机制性旁证, 且原文不涉及媒体停刊, 不作 exc_ 停刊排除的依据。停刊排除这一层的近期实证依据是 Cha 与 Wang (2026): 该文以地方报纸停刊作为信息环境冲击做实证, 证实媒体停刊是会真实改变可观测报道集合与信息含量的事件, 从而支撑「停刊媒体值得单独处理」; 边界在于原文把停刊当作外生冲击做因果识别、DV 为公司层面的信息不对称指标、层级为公司-年且语境为英文地方报业, 本家族只把停刊媒体作为样本排除条件做并排稳健性, 既不做因果推断, 其 ceased_set 亦是中文媒体源的疑似/确证停刊判定。三权重并排这一设计的方法学依据是 Soebhag 与 Verwijmeren (2024): 该文在资产定价因子模型上枚举断点选择、是否剔除 microcaps、行业调整与再平衡频率等构造路径, 实证记录研究者自由度带来的结果离散 (non-standard error 与 standard error 之比平均超过 1), 主张研究者须清楚交代并论证这些选择而非独断取一; 其自由度维度是投资组合排序而非情感词典权重, 且原文以枚举上百条构造路径来估计 NSE, 本家族仅枚举三个权重取值, 不构成 NSE 的完整估计。与之互补, Merkus (2024) 把规格曲线分析用于国际贸易引力模型, 系统枚举设定选择并展示估计量在整条曲线上的分布, 以判断结论是否被某一设定驱动, 与本家族「证明主结论不被 0.5 这一取值驱动」的敏感性设计同源; 但原文枚举的是控制变量与固定效应设定、规模达上百设定且层级为国家对, 本家族只有三点权重阶梯, 二者规模不可比。中文语料侧, Yan、Ma、Li 与 Tang (2024) 在中国语境下以中文媒体报道构造语调测度并做横截面实证, 是与本家族同语言、同媒体类型的近期语调计量实践; 其口径为相对预期的「异常语调」残差、层级为上市公司股票横截面、DV 为股票收益, 与本家族的幅度归一化 Σ(final)/Σ|final|、bank-year 面板聚合及停刊排除均不同, 且未做政治词子类折权, 故只作同域前沿参照。
## VAR: exc_du_2022_score_polw00_ctx

【变体差分】
本列是 polw00 臂在 ctx 轨上的排除停刊聚合值。ctx 轨的文本来源是 content_ctx, 即标题 prepend 后拼接「银行实体上下文窗口」内的文本 (实体窗口口径, 判定不对称: 银行侧走否定+短名过滤, 金科侧走裸 AC 词表), 相对 full 轨聚焦于目标银行邻近语境而剔除远端无关正文, 故其词典匹配集更窄、噪声更低但覆盖更少。政治词权重维度上, 本列与 full/ss 三轨完全一致地取 w_pol=0.0, 即政治正面词被完全剔除、只有普通正面词与负面词进入归一化打分。聚合维度上, 本列同样在非停刊媒体子集上取 bank-year 均值, 分母是该银行该年非停刊媒体的 ctx 轨有效报道篇数。相对家族 canonical (无 exc 前缀、w_pol=0.5 的 du_2022_score_ctx), 本列在两个正交维度上偏移: 一是聚合样本剔除停刊媒体 (幸存者偏差稳健性), 二是政治词权重降为零 (政治词敏感性下界臂)。需强调 ctx 轨的实体窗口截断只改变进入词典匹配的文本子集, 不改变归一化公式与三条语言学规则本身, 故本列与 full 轨列的差异纯粹来自语境范围而非打分口径。作为 conditional-on-full 稳健性轨, 本列的行宇宙是 full 留篇集与非停刊媒体的交集; 因早期试跑 T=2 样本上 ctx 轨匹配稀疏, 该列可能出现较多缺失或近零方差, 属预期退化, 生产 T=19 样本下方能充分识别。本列与 full 轨列各自 just-identified 并排、互为稳健性、不分主次, 严禁与 full/ss 轨、与 polw05/polw10 臂混入同一 over-identified Hansen J。

## VAR: exc_du_2022_score_polw00_full

【变体差分】
本列是 polw00 臂在 full 轨上的排除停刊聚合值, 是本家族三列中语义最完整、覆盖最广的一条。full 轨文本来源是 content_full, 即标题 prepend 后拼接完整正文, 词典匹配作用于整篇报道, 故相对 ctx/ss 轨匹配词数最多、语调估计方差最小。政治词权重维度上取 w_pol=0.0, 即在计算 du_2022_score 时政治正面词贡献乘以 0.0、被完全排除, 只保留普通正面词与全部负面词; 这是政治词权重梯子的下界臂, 用以检验「若认为政治正面词毫无情感信号」时家族主结论是否稳健。聚合维度上, 本列在剔除 de-facto 停刊媒体后的报道子集上对文章级 du_2022_score_polw00_full 取 bank-year 算术均值, 分母是该银行该年非停刊媒体的 full 轨报道篇数。因全项目采用 full-only 留篇门控, full 轨定义了银行金科报道的行宇宙, 本列的样本框是该宇宙再交非停刊媒体。相对 canonical du_2022_score_full (无 exc、w_pol=0.5), 本列同时施加停刊排除与政治词零权重两重偏移。作为政治词权重梯子的下界端点, 本列与 polw05 (生产口径 0.5)、polw10 (满权重 1.0) 构成三点敏感性: 若家族主结论在政治正面词毫无信号 (polw00) 至满信号 (polw10) 的整个区间内符号与显著性不变, 则可判定结论不被政治词这一研究者选择所驱动。full 轨在三轨中匹配最密、方差最小, 因而是三点敏感性检验中信噪比最高的参照轨; 停刊排除进一步保证该参照不被样本期内退出发稿的媒体语调结构污染, 与 Fang 与 Peress (2009) 关于媒体覆盖横截面结构的关切相呼应。需强调停刊排除只收窄聚合样本、政治词零权重只改动词典装载, 二者均不触碰归一化公式 Σ(final)/Σ|final| 与三条语言学规则, 故本列与 canonical 的差异是可精确归因的两维偏移而非口径混淆。铁律: 本列与 ctx/ss 轨、与 polw05/polw10 臂均各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。

## VAR: exc_du_2022_score_polw00_ss

【变体差分】
本列是 polw00 臂在 ss 轨上的排除停刊聚合值。ss 轨 (same-sentence) 文本来源是 content_ss, 即标题 prepend 后取「目标银行与金融科技词在同一句、正负 N 句窗内共现」的文本 (config/filtering.yaml 的 ss_sentence_radius, 默认 1)。ss 轨口径最严: 只有银行与金科同句共现的片段才进入打分, 故匹配词数最少、最易退化。其回退语义镜像 ctx 轨: 若某篇无银行∧金科同句共现, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若金科 AC 词表为 None 则 ss 全轨优雅降级。政治词权重维度取 w_pol=0.0, 与 full/ctx 三轨一致地完全剔除政治正面词。聚合维度上, 本列在非停刊媒体子集上取 bank-year 均值, 分母是该银行该年非停刊媒体的 ss 轨有效报道篇数。在早期试跑 T=2 样本上 ss 轨常因同句共现稀疏而近零方差, 属预期退化, 生产 T=19 样本正常。相对 canonical du_2022_score_ss (无 exc、w_pol=0.5), 本列叠加停刊排除与政治词零权重两重偏移。需注意 ss 轨的回退设计使其在无同句共现时退化为 full 正文打分, 故本列并非全部行都真正反映「银行金科同句语境」, 使用时应结合 ss_is_fallback 指示列判断有效性; 这一回退与 ctx 轨共享分母的口径确保三轨在缺共现时优雅降级而非产生单边孤儿列。铁律: 本列作为 conditional-on-full 稳健性轨, 与 full/ctx 轨、与 polw05/polw10 臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Beltran, A., Guariso, D., & Guerrero, O. A. (2026). Paying the piper: government advertising and media bias. European Political Science Review, 1-20. https://doi.org/10.1017/s175577392610054x
Cha, Y., & Wang, T.-X. (2026). Can firms offset information asymmetry shocks? Evidence from local newspaper closures. Applied Economics Letters, 1-7. https://doi.org/10.1080/13504851.2026.2701294
Soebhag, A., Van Vliet, B., & Verwijmeren, P. (2024). Non-standard errors in asset pricing: Mind your sorts. Journal of Empirical Finance, 78, 101517. https://doi.org/10.1016/j.jempfin.2024.101517
Merkus, E. (2024). Gravity Models in International Trade: A Specification Curve Analysis. Journal of Industry, Competition and Trade, 24(1), 17. https://doi.org/10.1007/s10842-024-00426-5
Yan, L., Ma, Y., Li, C., & Tang, G. (2024). Media abnormal tone and cross section of stock returns: Evidence from China. Accounting & Finance, 64(3), 2671-2698. https://doi.org/10.1111/acfi.13230
<!-- rendered-citations:end -->
