---
family_id: F478
columns:
- pos_symb_count_ctx
- pos_symb_count_full
- pos_symb_count_ss
unit: 篇数/计数 (count, 银行-年层面加总)
formula: 'pos_symb_count{track} = sum(_is_pos_symb{track}), 其中 _is_pos_symb{track} 是文章级布尔指示列: LLM 投票判定该篇银行-金科报道情感极性为正 (llm_vote 多数票=正面) 且实质性分类为「符号性/象征性」而非「实质性」创新叙事 (substantiveness=symbolic)。track ∈ {full, ctx, ss} 三轨并排各自加总, 不跨轨相加。'
producer: pipeline\panel\encode.py ; pipeline\panel\runner.py
upstream:
- llm_vote_tone (文章级 LLM 三家多数投票情感极性)
- innovation_substantiveness (文章级 LLM 实质性/符号性分类, P3 substance 构念下游)
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
- doi: 10.1002/smj.3549
  type: journal
  authors: Su, J., Gao, X., & Tan, J.
  year: 2024
  title: 'Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment'
  venue: Strategic Management Journal
  vol: '45'
  issue: '2'
  pages_or_artno: 333-361
- doi: "10.1016/j.jsis.2026.101971"
  type: "journal"
  authors: "Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E."
  year: 2026
  title: "Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?"
  venue: "The Journal of Strategic Information Systems"
  vol: "35"
  issue: "2"
  pages_or_artno: "101971"
- doi: "10.1108/ara-01-2025-0031"
  type: "journal"
  authors: "Guan, J., & Zhuang, X."
  year: 2025
  title: "Do digital words reflect real innovation? Evidence from post-M&A earnings conference"
  venue: "Asian Review of Accounting"
  pages_or_artno: "1-44"
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
- doi: "10.1016/j.technovation.2023.102880"
  type: "journal"
  authors: "Granados, C., Ayala, Y., & Ramos-Mejia, M."
  year: 2024
  title: "Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation"
  venue: "Technovation"
  vol: "129"
  pages_or_artno: "102880"
new_dois: []
---

## CORE

【构念与来源】
`pos_symb_count` 家族衡量的是银行-年层面「正面情绪但缺乏实质内容」的银行-金科报道篇数, 是本项目「洗稿率」(washing_ratio) 测度族的分子输入之一, 而非独立成品指标 — 它必须与同域分母 (`pos_substvalid_count`) 配对使用才具解释力。构念动机借鉴企业传播文献中「言辞脱耦」(decoupling) 的经典区分: 企业/媒体文本可以在情绪基调上表现积极, 但其内容既不涉及具体产品、合作、投入规模等可验证事实, 也不构成对既往承诺的兑现追踪, 因而属于象征性 (symbolic) 而非实质性 (substantive) 叙事。这一区分直接对应 Bingler et al. (2022, *Finance Research Letters*) 在 ClimateBert 框架下提出的「cheap talk vs. cherry-picking」判据: 企业气候披露中大量文本情绪正面, 却系统性缺乏可核验的量化承诺与后续行动, 作者将这类文本标记为廉价言辞 (cheap talk); 其后续工作 Bingler et al. (2024, *Journal of Banking & Finance*) 进一步把这一判据与企业实际排放数据、声誉风险挂钩, 验证「言辞正面度」与「行动实质性」两个维度确有系统性缺口, 而非同一构念的两种测量误差。本项目把这一判据从企业气候披露迁移到中文银行-金科新闻语境: 一篇报道若被 LLM 判为情感极性正面, 但其叙事内容被同一 LLM 管线 (`innovation_substantiveness` 分类任务) 归入「符号性」桶 (即报道停留在口号式、意向性、无具体量化信息的层面, 例如「某银行积极拥抱金融科技、加快数字化转型」这类无具体项目/金额/时点的泛化措辞), 则该篇文章被标记为 `_is_pos_symb{track}=True`, 计入本家族分子。

【方法学与计算】
产生本家族三列的计算发生在两个阶段: 文章级布尔指示列 `_is_pos_symb{track}` 由 stage 21 LLM 情感投票 (`llm_vote_tone`) 与实质性分类 (`innovation_substantiveness`) 两个独立 LLM 任务的输出联合判定 (逻辑与运算: 情感=正面 AND 实质性=符号性), 该联合判定发生在 `pipeline\panel\encode.py` 银行-年聚合入口之前; `encode.py` 随后按 `for track in ['_full', '_ctx', '_ss']: agg[f'pos_symb_count{track}'] = (f'_is_pos_symb{track}', 'sum')` 逐轨对银行-年分组求和, 得到本家族三列的原始计数值。计数本身是非负整数取值的 double 类型 (篇数), 无归一化、无除以样本规模, 因此其绝对水平会随银行-年内报道量规模而机械增长, 单独解读时须谨慎 — 这也是为什么下游 `pipeline\panel\runner.py` 不直接消费本家族列本身作回归 DV, 而是将其作为分子, 除以同域分母 `pos_substvalid_count{track}` (阳性且实质性已成功测量的篇数) 构造归一化的 `washing_ratio{_sfx}` (`_sfx` 在 full 轨为空字符串, ctx/ss 轨分别为 `_ctx`/`_ss` 后缀; 注意源码明确警示不可写成 `'' if full else '_ctx'` 这种简写, 否则会把 ss 误并入 ctx 命名空间)。`runner.py` 中的 `_svd_denom` 辅助函数还处理了分母同域化的历史修复 (`fix(omni-g-runner-10/g-runner-14, 2026-06-11)`): 早期版本分母误用「全部阳性文章数」而非「阳性且实质性判定成功的文章数」, 导致当 LLM 实质性分类失败率上升时洗稿率被系统性低估 (分子受限于已判定样本, 分母却包含未判定样本, 形成分子分母失配); 修复后分母改用 `{name}_substvalid_count{track}`, 缺该列时回退旧分母并输出告警日志, 以兼容旧 schema。理解本家族三列时应牢记: 它们本身是「洗稿率」这一比率型稳健性测度链条的中间产物, 计数值的银行-年间比较意义有限, 真正承担识别功能的是下游比率列。

【文献定位】
本家族在方法论谱系上继承两条脉络。第一条是文本情绪与文本实质性分离的判据设计, 直接对应 Bingler et al. (2022, *Finance Research Letters*) 关于 cheap talk 的操作化定义, 以及其 2024 年 (*Journal of Banking & Finance*) 后续对该判据外部效度的验证; 本项目的创新点在于把该判据从企业自我披露文本 (10-K/年报/ESG 报告) 迁移到第三方媒体报道文本, 情感极性与实质性两个维度均由独立的 LLM 分类任务而非 Bag-of-Words 词典产生, 判定粒度落在篇章级而非句子级。第二条脉络是组织行为文献中「象征性遵从 vs 实质性遵从」(symbolic vs. substantive conformance) 的一般性区分, 参照 Su, Gao, & Tan (2024, *Strategic Management Journal*) 关于企业如何在竞争压力与制度压力交织的动态复杂环境下, 通过「最优独特性」(optimal distinctiveness) 权衡表面姿态性行为与可验证的实质性行动这一论证: 企业面对外部压力时既可以选择改变实质性经营行为以真正满足利益相关方期待, 也可以选择仅在传播/表态层面做出姿态性回应而不伴随实质投入, 两类回应在外部观察者 (包括媒体) 视角下都可能呈现出「态度积极」的表象, 但其可验证的实质内容截然不同; 该框架为本项目区分「正面且符号性」与「正面且实质性」两类报道提供了组织理论层面的支撑。本家族与其反向配对列 `neg_sub_count` (「反向验证: 负面但被判定为实质性」的镜像计数) 共同体现了这一分离原则 — 洗稿判据不是单一极性下的净值, 而是情感维度与实质性维度的交叉表 (2×2: 正面×实质性、正面×符号性、负面×实质性、负面×符号性), `pos_symb_count` 只是其中一个象限的原始计数。三轨 (full/ctx/ss) 铁律适用于本家族: full/ctx/ss 三条计算路径各自独立 just-identified 并排, 互为稳健性检验而不设主次关系, 严禁在同一 over-identified Hansen J 检验中混用跨轨列; ss 轨在文章无法找到银行∧金科同句共现窗口时镜像 ctx 的回退语义, 退化为使用全文正文 (`content_ss` 回退等于 `content_full` body, 对应 `ss_is_fallback=True`), 三轨共享同一 `n_articles` 分母口径。此外, 留篇门控严格遵循 2026-06-29 起生效的 full-only 口径: 一篇报道是否计入「银行-金科报道」样本, 只取决于 `llm_verified_full == True`, ctx/ss 两轨的 `_is_pos_symb` 计数是在 full 轨留篇集合的子集行宇宙上分轨计算, 而非各轨独立留篇, 这保证了三轨计数在同一样本基础上可比。 近期文献进一步充实了这两条脉络在数字化/科技话语上的落地。Chen、Hajiheydari、Zhang 与 Lin (2026) 基于注意力基础观提出企业数字化转型关注度 (CDTA), 以中国上市公司 2007–2020 年样本在「战略实质承诺 vs 象征性信号」两个对立解释间做检验, 结果支持实质承诺说而未支持象征性信号说, 且话语与创新的一致性在高问责情境下最强; 其对本家族的锚定价值在于确立该二分是当代科技话语研究的主流理论框架, 并证明「话语是否只是象征」属可被实证证伪的经验问题, 因而本列所刻画的「正面×象征性」象限是一个有待检验的量而非预设结论 —— 须注意原文以「话语关注度 vs 实际创新产出」间接推断, 与本项目由 LLM 对单篇报道直接标注实质性/象征性的判定机制不同, 文本源亦为公司自述披露而非第三方新闻, 层级为公司-年而非银行-年三轨。Guan 与 Zhuang (2025) 在中国并购语境下直问「数字化措辞是否对应真实创新」, 以文本测度检验数字化词汇与后续创新产出的对应关系, 与本列在正面科技话语中析出象征性叙事的构念高度同域; 但原文文本源为并购后业绩说明会 (管理层自述), 且以「数字词汇量 vs 实际创新指标」间接推断象征性, 并未提出象征性/实质性的逐篇标注方案, 分析单元为并购事件/公司-年。Huang 与 Ma (2024) 则把「实质性 vs 象征性」二分直接置于金融科技议题下, 检验金融科技发展对企业实质性与象征性绿色创新的差异化影响, 其中文表述与本项目 innovation_substantiveness 的标签直接对应; 迁移边界是原文的实质/象征由专利类型 (发明 vs 实用新型/外观) 客观划分、主体为非金融上市公司且金融科技是解释变量, 本项目则由 LLM 判定新闻文本、主体为银行且金融科技是被报道议题本身, 原文亦未构造任何比率型 washing 指标。构念界定层面, Granados、Ayala 与 Ramos-Mejia (2024) 对「创新剧场」(innovation theater) 的刻画补足了 symbolic 一侧的组织理论内涵 —— 技术创新的象征性展演可与实质性投入脱钩, 恰是本列所计数的报道类型的理论原型; 惟原文属组织行为学层面的构念研究, 未提供文本自动分类算法, 非中国语境、非银行业、无面板计量, 本项目把该构念操作化为逐篇 LLM 标签并按银行-年计数, 操作化层级与数据类型均不同。上述四条文献共同支撑本列构念的正当性与可检验性, 但均不涉及三轨文本设计, 故 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性而不分主次的口径仍由本项目自身的测度设计承担, 不应据这些文献推断任何一轨具有主测度地位。
## VAR: pos_symb_count_ctx

【变体差分】
本列是 `pos_symb_count` 家族在 ctx 轨 (context track) 上的实现, 对应文章级指示列 `_is_pos_symb_ctx`。ctx 轨的文本输入 `content_ctx` 由 stage 14 `ctx_materializer` 物化, 定义为「标题 + 实体窗口」— 即以目标银行/金科实体出现位置为中心截取的局部上下文窗口文本 (而非全文), 标题以 `prepend_title` 方式前置拼接。用于产生本列的两个上游 LLM 判定任务 (情感投票 `llm_vote_tone_ctx` 与实质性分类) 均基于该窗口化文本重新推断, 而非直接复用 full 轨的判定结果做窗口截断, 因此 `pos_symb_count_ctx` 与 `pos_symb_count_full` 之间的差异既可能来自实体窗口截断丢失了判定所需的关键上下文信息 (导致同一篇文章在 ctx 轨下情感或实质性归类发生翻转), 也可能反映窗口聚焦确实降低了无关段落对 LLM 判定的噪声干扰。ctx 轨与 full/ss 两轨各自独立 just-identified 并排, 是「互为稳健性、不分主次」关系中的一环: 若一篇文章在 full 轨被判定为 `pos_symb`、在 ctx 轨未必同样被判定, 这种轨间不一致本身是可解释的稳健性信息而非测量误差, 不应强行调和或取平均。留篇门控本列仍遵循 full-only 铁律, 行宇宙限定在 `llm_verified_full == True` 的报道子集内, ctx 轨在此子集上产出条件性 (conditional-on-full) 测度, 而非另设一套独立的留篇标准。使用本列做稳健性检验时应注意: 由于 ctx 窗口截断可能移除了判断「符号性 vs 实质性」所需的具体细节 (例如具体合作项目名称、投入金额、时间节点往往散落在实体窗口之外的段落), ctx 轨的 `_is_pos_symb` 判定相对 full 轨可能系统性偏向「符号性」一侧 (信息不足时 LLM 更倾向保守判定为缺乏实质内容), 这一方向性偏差本身构成对洗稿判据稳健性的有益压力测试, 而非需要修正的偏误来源。研究者在解读 ctx 轨与 full 轨的差异时, 应将其视为「文本粒度对判据敏感性」的诊断信息, 与 ss 轨的严格同句判据共同构成从宽到窄的三档文本范围梯度。

## VAR: pos_symb_count_full

【变体差分】
本列是 `pos_symb_count` 家族的 full 轨实现, 即无后缀的 canonical 变体 (变量命名遵循 full 不加后缀、ctx 加 `_ctx`、ss 加 `_ss` 的项目约定), 对应文章级指示列 `_is_pos_symb_full`, 其文本输入 `content_full` = 标题前置拼接后的报道全文正文, 是三轨中信息量最完整、覆盖判定上下文最充分的一轨。full 轨同时也是留篇门控的唯一判据来源: 一篇报道是否被计入「银行-金科报道」样本 (`llm_verified_full == True`) 只看 full 轨的 LLM 验证结果, 因此 `pos_symb_count_full` 天然定义在完整样本行宇宙上, 而 ctx/ss 两轨则是在 full 轨留篇集合子集上的条件测度。在下游 `washing_ratio` 比率族的构造中, full 轨对应变量名不加轨道后缀的 `washing_ratio` 本身 (`_sfx = ''`), 是三条洗稿率序列中命名最贴近「主指标」的一条, 但按项目铁律三轨仍严格互为稳健性并排, 不因命名简洁而获得事实上的主测度地位, 三轨结果应在稳健性表中逐一报告而非只报 full 轨。full 轨的实践意义在于它是三轨中样本量最大、判定输入最完整的一条: 由于 full 轨文本未经窗口截断或同句限定, LLM 在情感投票与实质性分类两个任务上均可获得报道全文的完整线索, 理论上判定误差 (无论是情感极性误判还是实质性/符号性误判) 应低于信息受限的 ctx/ss 两轨; 但这也意味着 full 轨文本中可能混入与目标银行-金科关系无直接关联的段落 (例如同一篇报道中提及多家机构或多个不相关事件), 这些段落理论上不应主导情感与实质性判定, 但实践中不能完全排除其对 LLM 整体判定产生噪声干扰的可能, 这正是设置 ctx/ss 两条更聚焦文本轨道作为并排稳健性检验的动机所在。

## VAR: pos_symb_count_ss

【变体差分】
本列是 `pos_symb_count` 家族的 ss 轨 (same-sentence track) 实现, 对应文章级指示列 `_is_pos_symb_ss`, 其文本输入 `content_ss` 定义为「标题 + 银行∧金科词同句共现窗口 (默认 ±1 句半径, `config/filtering.yaml::context_window.ss_sentence_radius`)」的严格同句判据, 是三轨中文本范围最窄、判据最严格的一轨。当一篇文章找不到银行与金科词严格同句共现的句子时, `content_ss` 回退为全文正文 (镜像 ctx 轨回退语义), 该篇文章的 `ss_is_fallback` 标记为 True, 此时其 `_is_pos_symb_ss` 判定实质上退化为基于全文文本做出, 与 full 轨的判定输入趋同 (但仍是独立的 LLM 调用, 结果未必逐位相等)。ss 轨的严格同句判据与 stage 13 硬过滤共现判据 (`config/filtering.yaml::cooccurrence_filter.sentence_radius`) 是两个不同的配置键, 不应混淆: stage 13 的共现判据决定一篇文章是否进入下游任何处理 (丢行), 而本列所用的 ss 窗口判据只决定该篇文章在计算洗稿率相关判定时使用哪一段文本 (不丢行, 只影响文本范围与回退)。留篇门控同样遵循 full-only 铁律, ss 轨是在 full 轨留篇集合子集上、与 full/ctx 两轨严格并排、互为稳健性检验的第三条独立路径, 三轨计数不可相加或加权合并进同一识别方程。由于 ss 判据要求银行词与金科词在同一句内共现, 它天然剔除了「报道整体谈及金融科技、但目标银行只在别处被提及」这类弱关联文章的贡献段落, 使 `pos_symb_count_ss` 相对 ctx/full 两轨更集中反映「银行与金科在同一叙述单元中被直接绑定」时的符号性正面报道量; 当同句共现比例本身在样本中偏低时 (例如开发阶段 T=2 小样本下), 触发回退的文章占比会相应升高, 此时 ss 轨的判定退化为 full 轨的独立重复调用而非严格意义上的窄窗口判定, 这一退化行为是设计内 (by-design) 而非缺陷, 研究者在小样本诊断阶段观察到 ss 轨与 full 轨高度重合是预期现象。
<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E. (2026). Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?. The Journal of Strategic Information Systems, 35(2), 101971. https://doi.org/10.1016/j.jsis.2026.101971
Guan, J., & Zhuang, X. (2025). Do digital words reflect real innovation? Evidence from post-M&A earnings conference. Asian Review of Accounting, 1-44. https://doi.org/10.1108/ara-01-2025-0031
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
Granados, C., Ayala, Y., & Ramos-Mejia, M. (2024). Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation. Technovation, 129, 102880. https://doi.org/10.1016/j.technovation.2023.102880
<!-- rendered-citations:end -->
