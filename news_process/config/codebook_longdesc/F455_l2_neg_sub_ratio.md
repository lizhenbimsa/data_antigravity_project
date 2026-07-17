---
family_id: F455
columns:
- neg_sub_ratio_ctx
- neg_sub_ratio_full
- neg_sub_ratio_ss
unit: 比率 (proportion, [0,1]; 分子分母均为篇数, 无量纲)
formula: 'neg_sub_ratio{track} = neg_sub_count{track} / max(neg_substvalid_count{track}, neg_count{track}) (`_svd_denom` 优先取实质性/象征性双裁定合法的子样本计数 neg_substvalid_count{track} 作分母; 若该列缺失或全空则退化为分母=neg_count{track} 全部负面篇数; 分子 neg_sub_count{track}=负面且被裁定为「实质性」议题的篇数)'
producer: pipeline\panel\runner.py (方法 B「反向验证」, L2220-2234, `neg_sub_count{track}` 赋值见 L2222-2227; `_safe_ratio`/`_svd_denom` 内部函数); 标签写入 pipeline\panel\export.py
upstream:
- 21_tone_llms (llm_vote_tone{track} 三家 LLM 投票情感, 提供 neg_count 基底)
- l2_cater_* 系列 (三 LLM 逐家情感裁定, 供多数投票聚合)
- substantive/symbolic 二分类裁定 (locus/substance 维 LLM 分类, 供 sub/symb 子样本划分)
citations:
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: 'Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
- doi: 10.1016/j.jfineco.2021.09.012
  type: journal
  authors: Hirshleifer, D., & Sheng, J.
  year: 2022
  title: 'Macro news and micro news: Complements or substitutes?'
  venue: Journal of Financial Economics
  vol: '145'
  issue: '3'
  pages_or_artno: 1006-1024
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: 'Transparency and deliberation within the FOMC: a computational linguistics approach'
  venue: The Quarterly Journal of Economics
  vol: '133'
  issue: '2'
  pages_or_artno: 801-870
- doi: "10.1007/s10614-026-11328-5"
  title: "DeepGreen: Effective LLM-Driven Greenwashing Monitoring System Designed for Empirical Testing — Evidence from China"
  authors: "Xu, C., Liu, J., Li, Z., & Lin, C."
  year: 2026
  venue: "Computational Economics"
  type: "journal"
- doi: "10.1016/j.jenvman.2023.118950"
  title: "Symbol or substance? Environmental regulations and corporate environmental actions decoupling"
  authors: "Tang, P., Wang, C., Jiang, Q., Liu, X., & Wang, J."
  year: 2023
  venue: "Journal of Environmental Management"
  type: "journal"
new_dois:
  - "10.1007/s10614-026-11328-5"
  - "10.1016/j.jenvman.2023.118950"
---

## CORE

【构念与来源】
`neg_sub_ratio` 是 washing 洗稿测度族 (F455 所属家族群) 中「方法 B: 反向验证」输出的负面议题实质性占比: 在被 LLM 三家投票判定为负面 (`neg_count`) 的银行-金科报道子集中, 有多大比例同时被判定为围绕实质性 (substantive) 议题展开, 而非纯象征性 (symbolic) 措辞。构念直接对接组织行为与公司治理文献中经典的 substantive-symbolic 行动二分类学: 前者指组织真实采取的具体行动 (如产品上线、合作签约、监管处罚整改), 后者指仅停留在姿态性/公关性表述而无可核验的具体内容变更。本家族把这一二分类学移植到银行-金科新闻文本层面, 用 LLM 逐篇裁定报道所述事项是「实质性」还是「象征性」, 再按情感极性 (正面/负面) 交叉分层, 形成 washing 诊断矩阵的四个象限之一。`neg_sub_ratio` 对应负面-实质象限的密度, 是判断"负面报道是否言之有物"的核心统计量: 若该比率高, 说明负面报道多聚焦具体事件(如违规处罚、项目失败), 可信度与信息含量较高; 若该比率低, 说明负面报道多为泛泛而谈的负面情绪渲染, 缺乏具体事实支撑, 更接近舆论噪音而非基本面信号。

`neg_sub_ratio` 与家族内正向对应量 `washing_ratio` (方法 A, LLM 投票极化条件法, 衡量正面报道中"象征性"占比, 即 washing 程度) 构成一对镜像测度: `washing_ratio` 高 = 正面报道空心化 (自我吹嘘、无实质内容); `neg_sub_ratio` 低 = 负面报道空心化 (情绪化指责、无实质内容)。二者共同刻画同一枚硬币的两面: 银行-金科报道中「言辞」与「实质」的脱钩程度 (decoupling), 呼应企业传播与制度理论文献中 greenwashing/decoupling 概念的操作化 (Kim & Lyon, 2015, *Organization Science*, 对企业可持续披露中"言过其实/过度谦虚"两类脱钩的经典区分)。运行时另派生 `washing_asymmetry{track} = neg_sub_ratio{track} - (1 - washing_ratio{track})`, 直接检验正负面报道的实质性基准是否对称 (若报道生产机制对正负面一视同仁, 二者应互补且非对称量应趋近零)。

【方法学与计算】
计算流程分两步。第一步 (stage 21 `tone_llms` + substance 维 LLM 分类) 对每篇留篇报道产出两组独立裁定: (a) 情感极性投票 `llm_vote_tone{track}`, 三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 多数表决, 据此把报道计入 `neg_count{track}` (负面篇数); (b) substantive/symbolic 议题分类 (对接 P3 substance 维 `sub_frac`/`symb_frac` 面板测度所依赖的同一底层裁定), 据此判断该篇是否落入"实质性"范畴。第二步 (`pipeline/panel/runner.py` L2220-L2234, 方法 B) 在面板聚合层做交叉计数: `neg_sub_count{track}` = 负面∧实质性的篇数; 分母经 `_svd_denom` 择优 — 优先取「负面且情感/实质性双裁定均有效 (substvalid)」的子样本计数 `neg_substvalid_count{track}` (剔除因分类置信不足/解析失败而无法定性的边缘篇目, 使比率仅在双重可靠标注的样本上计算), 该列缺失时退化为分母 = 全部负面篇数 `neg_count{track}` (即把无法确认实质性归类的负面篇目当作分母口径内但不计入分子)。`_safe_ratio` 对零分母 (该 track 该轨该期无负面报道) 返回 NaN, 不做 0/0 强填, 与家族其余比率类测度 (`washing_ratio` 等) 共享同一护栏函数, 保证极端稀疏格 (小样本银行-年) 不会产出虚假精确的比率。

三轨 (full/ctx/ss) 分别以各自独立的文本窗口重复上述全部裁定与聚合: `_full`=标题+正文全文, `_ctx`=标题+银行/金科实体窗口, `_ss`=标题+银行∧金科同句±N窗口 (`ss_sentence_radius` 默认1); 三者互不借用彼此的分子分母, 严格逐轨独立计算。`_ss` 轨在无银行∧金科同句共现时按标准回退语义退化为 `content_full` (镜像 `_ctx` 回退, `ss_is_fallback=True`), 该回退发生在文本物化层 (stage 14), `neg_sub_ratio_ss` 本身不因此单独失真, 但其样本构成会包含较高比例的回退篇目, 解读跨行比较时须留意。三轨在识别策略上各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨同名系数混入同一 over-identified 的 Hansen J 过度识别检验; full 轨对应 2026-06-29 之后确立的 full-only 留篇门控 canonical (`llm_verified_full==True` 决定"是否算一篇银行-金科报道"), ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集, 三轨列仍各自照算不借用彼此分母。

【文献定位】
substantive/symbolic 二分类学的方法论根源是组织行为与公司治理文献对改革"言行不一"现象的经典区分, 本测度族将其迁移到新闻文本自动化裁定场景, 并与企业传播/漂绿(greenwashing)文献中的 decoupling 概念对齐: Kim & Lyon (2015, *Organization Science*) 系统区分了企业披露中的"过度渲染 (greenwash)"与"过度谦虚 (brownwash)"两类言行脱钩, `washing_ratio`/`neg_sub_ratio` 一正一负两个方向的实质性占比正是这一 decoupling 逻辑在情感极性分层下的操作化。文本/披露的"廉价谈话 (cheap talk)"识别方法直接借鉴气候披露文本分析文献: Bingler, Kraus, Leippold & Webersinke (2022, *Finance Research Letters*; 2024, *Journal of Banking & Finance*) 用 ClimateBert 及后续模型区分企业气候披露中"言辞"与"可核实行动"的脱钩程度, 是本测度计算管线中已直接沿用的"洗稿率(washing ratio)"概念与命名的直接方法学出处 (见 `pipeline/panel/export.py` 内嵌注释)。用 LLM 对海量新闻文本做结构化裁定 (议题实质性/情感极性) 这一自动化文本分析路径, 承袭计算语言学在宏观/公司新闻文本挖掘中的应用范式 (Hansen, McMahon & Prat, 2018, *The Quarterly Journal of Economics*, 计算语言学方法解构 FOMC 会议记录的透明度效应, 是文本自动裁定用于制度/政策分析的代表性先例)。新闻内容的宏观-微观信息互补/替代关系 (Hirshleifer & Sheng, 2022, *Journal of Financial Economics*) 为解读"哪类报道承载增量信息、哪类只是重复噪音"提供了理论参照: `neg_sub_ratio` 低意味着该期负面新闻更接近对既有负面预期的重复渲染而非新增实质信息, 与该文对宏观/微观新闻信息含量区分的框架相呼应。近年 LLM 驱动的文本裁定方法进一步扩展了这一脉络: Xu, Liu, Li & Lin (2026, Computational Economics) 提出双阶段 LLM 驱动的漂绿监测系统 DeepGreen, 在中国 A 股年报文本上区分实质性绿色改进与象征性表述, 与本测度用 LLM 裁定报道「实质性 vs 象征性」的方法学高度对应; Tang, Wang, Jiang, Liu & Wang (2023, Journal of Environmental Management) 以中国上市公司为样本考察环境规制强度如何加剧披露言辞与实际环境行动之间的脱钩(言过其实、行动不足), 为本测度「言辞-实质脱钩」的构念提供直接经验对照。

## VAR: neg_sub_ratio_full

【变体差分】
`_full` 轨: 文本窗口 = 标题 + 正文全文 (`content_full`, prepend_title), 是三轨中的 canonical/主轨, 对应 2026-06-29 起确立的 full-only 留篇门控 — 是否计入"一篇银行-金科报道"完全由 `llm_verified_full==True` 决定, 该门控同时决定了本列分子 `neg_sub_count_full` 与分母 `neg_substvalid_count_full`/`neg_count_full` 的行宇宙。`_full` 无独立后缀 (帕累托意义上的裸列名 `neg_sub_ratio` 落在方法 B 中即为 full 轨, `_full` 显式后缀由本 codebook 家族命名约定统一补全)。与 `_ctx`/`_ss` 相比, `_full` 轨样本量最大 (不受实体窗口/同句窗口约束丢词), 但也最可能纳入与银行-金科议题无关的背景段落, 使"实质性"裁定基于更宽的上下文, 在解读为主测度时应配合 `_ctx`/`_ss` 互为稳健性核验, 三轨并排 just-identified, 不构成单一 over-identified 检验的联合矩。

分子分母的行宇宙口径均落在 `_full` 上: 分母优先取 `neg_substvalid_count_full` (负面且实质性/情感双裁定均有效的子样本篇数), 缺失时退化为 `neg_count_full` 全部负面篇数; 分子 `neg_sub_count_full` 是该子样本中被判为实质性议题的篇数。由于 `_full` 是留篇门控的口径来源, 该列在跨阶段一致性上最稳定 (不受 ctx/ss 特有的实体窗口截断或同句回退语义影响), 适合用作论文正文 Table 1 描述统计与主回归的默认轨; ctx/ss 两支作为并列稳健性检验出现于稳健性附表, 三者数值差异反映的是"裁定所依赖上下文宽窄"这一测量维度的敏感性, 不代表其中一支"更对"。使用者在跨银行-年比较 `neg_sub_ratio_full` 时, 应同时核对该格对应的负面篇数分母是否过小 (`neg_count_full` 极低时比率对单篇裁定高度敏感, 建议配合样本量列做加权或截断处理)。

## VAR: neg_sub_ratio_ctx

【变体差分】
`_ctx` 轨: 文本窗口 = 标题 + 银行/金科实体窗口 (`content_ctx`, 围绕目标实体的局部上下文截取, 而非全文), 是 full-only 门控确立后的 conditional-on-full 稳健性轨 — 行宇宙是 full 轨留篇集的子集, 但情感/实质性裁定与分子分母聚合仍在 `_ctx` 自身文本上逐轨独立完成, 不借用 `_full` 的计数。相较 `_full`, `_ctx` 轨把裁定视野收窄到实体近邻文本, 更贴近"报道究竟围绕这家银行/这家金科公司说了什么", 理论上能过滤掉全文中与目标实体无关的负面段落对分类的干扰, 但窗口截断也可能丢失判断"是否实质性"所需的上下文线索 (如具体金额、时间、监管条款可能出现在窗口外)。作为稳健性轨与 `_full`/`_ss` 互为并排验证, 不分主次, 禁止混入同一 Hansen J。

分子分母同样逐轨独立: `neg_sub_count_ctx`/`neg_substvalid_count_ctx`(或退化分母 `neg_count_ctx`) 均在 `_ctx` 自身的情感/实质性裁定基础上重新统计, 不与 `_full` 共享任何中间计数。行宇宙受 full-only 门控约束为 full 留篇集的子集 (即某篇若未通过 `llm_verified_full==True` 判定, 即便其 ctx 窗口文本存在, 也不进入 `_ctx` 轨的任何计数), 这保证了跨轨比较时分母定义域一致、不会因为 ctx 单独放宽或收紧留篇标准而制造伪差异。当某银行-年格内负面篇数本就稀少时, `_ctx` 轨因窗口截断可能进一步丢失少量可判定样本, 导致该格 `neg_sub_ratio_ctx` 缺失或方差偏大于 `_full`, 属预期的窗口收缩效应而非数据质量问题, 解读时建议与 `_full`/`_ss` 并列查看而非单独下结论。

## VAR: neg_sub_ratio_ss

【变体差分】
`_ss` 轨: 文本窗口 = 标题 + 银行∧金科同句 (strict same-sentence) ±N 句窗口 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认 N=1), 是三轨中判据最严格的一支, 只在银行实体与金科词汇真正同句/近邻共现的局部文本上做情感与实质性裁定, 因而信噪比理论上最高但样本收缩最明显。当某篇报道中银行与金科词汇从未在同句(±N)共现时, 该篇的 `content_ss` 按标准回退语义退化为 `content_full` 全文 (`ss_is_fallback=True`, 镜像 `_ctx` 缺同句证据时的回退处理, 分母 `n_articles` 与主口径共享), 使 `_ss` 轨在这类篇目上的实质性裁定实质等同于 `_full` 轨结果; 因此 `neg_sub_ratio_ss` 应理解为"严格同句证据可得时用严格窗口、证据不可得时优雅退化为全文"的混合口径, 而非在任何情形下都严格局部。作为三轨之一与 `_full`/`_ctx` 互为稳健性并排, 不分主次, 各自 just-identified, 严禁混入同一 over-identified Hansen J 联合检验。

分子分母仍逐轨独立聚合: `neg_sub_count_ss`/`neg_substvalid_count_ss`(或退化分母 `neg_count_ss`) 完全基于 `content_ss` 文本上的裁定重新统计, 不借用 `_full`/`_ctx` 的中间列。回退发生的判据是"该篇是否存在银行实体与金科词汇的同句 (±N 句) 共现", 由 stage 14 文本物化阶段一次性决定并写入 `ss_is_fallback` 标记列, 该标记与 `n_articles` 分母口径共享, 使跨行的回退比例可被审计。由于严格同句判据比 `_ctx` 的实体窗口更苛刻, `_ss` 轨在多数银行-金科议题密度低的期数会有较高比例回退为全文口径, 此时 `neg_sub_ratio_ss` 与 `neg_sub_ratio_full` 在这些行上数值高度重合属预期而非重复冗余; 真正体现 `_ss` 轨增量信息的是那些确有同句共现证据的行, 此时该列反映的是"银行与金科议题被同一句话直接绑定讨论"时报道的实质性密度, 是三轨中构念最贴近"同一事件描述"的测度, 适合用于对报道紧密程度敏感的稳健性检验设计。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Hirshleifer, D., & Sheng, J. (2022). Macro news and micro news: Complements or substitutes? Journal of Financial Economics, 145(3), 1006-1024. https://doi.org/10.1016/j.jfineco.2021.09.012
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: a computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Xu, C., Liu, J., Li, Z., & Lin, C. (2026). DeepGreen: Effective LLM-Driven Greenwashing Monitoring System Designed for Empirical Testing — Evidence from China. Computational Economics. https://doi.org/10.1007/s10614-026-11328-5
Tang, P., Wang, C., Jiang, Q., Liu, X., & Wang, J. (2023). Symbol or substance? Environmental regulations and corporate environmental actions decoupling. Journal of Environmental Management. https://doi.org/10.1016/j.jenvman.2023.118950
<!-- rendered-citations:end -->
