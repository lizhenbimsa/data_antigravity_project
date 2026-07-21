---
family_id: F577
columns:
- tone_gap_indep_collab_cm_ctx
- tone_gap_indep_collab_cm_ss
unit: 语调差值 (连续, 理论域 [-2,2], 经验上多落在 [-1,1]; bank-year 面板列, 上游为篇章级三家 LLM 多数投票语调再按合作模式二分聚合)
formula: 'tone_gap_indep_collab_cm_{trk} = llm_vote_tone_indep_cm_{trk} − llm_vote_tone_collab_cm_{trk}, 其中 {trk}∈{ctx,ss}; 两个子项分别是「自主研发」「外部协同」两个 innovation_collab_mode_{trk} 类目下 llm_vote_tone_{trk} 的对角线聚合均值 (_aggregate_ctx_diagonal); 双侧最小样本门槛 n_articles_indep_cm_{trk}>=5 且 n_articles_collab_cm_{trk}>=5 同时满足才出值, 否则整格 NaN'
producer: pipeline\panel\encode.py
upstream:
- innovation_collab_mode_ctx
- innovation_collab_mode_ss
- llm_vote_tone_ctx
- llm_vote_tone_ss
- n_articles_llm_valid_ctx
- n_articles_llm_valid_ss
citations:
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: '41'
  issue: '4'
  pages_or_artno: 793–815
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: FinTech credit and entrepreneurial growth
  venue: The Journal of Finance
  vol: '79'
  issue: '5'
  pages_or_artno: 3309–3359
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315–345
- doi: 10.1016/j.frl.2023.104779
  type: journal
  authors: Kueschnig, M., & Schertler, A.
  year: 2024
  title: 'Fusing futures: Financial institutions'' stock price response to fintech acquisitions'
  venue: Finance Research Letters
  vol: '59'
  pages_or_artno: '104779'
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: 'Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms'
  venue: Strategic Management Journal
  vol: '27'
  issue: '2'
  pages_or_artno: 131–150
- doi: "10.1108/ijoem-01-2026-0159"
  type: "journal"
  authors: "Ferilli, G. B., Palmieri, E., & Cicchiello, A. F."
  year: 2026
  title: "Bank–FinTech cooperation: what the empirical evidence reveals in Asia–Pacific countries"
  venue: "International Journal of Emerging Markets"
  pages_or_artno: "1-26"
- doi: "10.1108/ijbm-09-2023-0525"
  type: "journal"
  authors: "Le, T., Ngo, T., Nguyen, D. T., & Do, T. T."
  year: 2024
  title: "Fintech and banking: friends or foes? Evidence from bank–fintech cooperation"
  venue: "International Journal of Bank Marketing"
  vol: "42"
  issue: "7"
  pages_or_artno: "1513-1535"
- doi: "10.1007/s10668-025-07107-1"
  type: "journal"
  authors: "Sun, Z., Sun, Y., Qiao, Q., & Zhang, P."
  year: 2025
  title: "Independent innovation and collaborative innovation: exploring the impact of digital technology transfer on green innovation from the perspective of innovation element flow"
  venue: "Environment, Development and Sustainability"
- doi: "10.2139/ssrn.5265813"
  type: "wp"
  authors: "Jamshed, A., Oberoi, J. S., & Lawal, T. O."
  year: 2025
  title: "Speaking with One Voice? The Joint Information Content of Tone in MD&A and Risk Factor Disclosures"
  venue: "SSRN"
  pages_or_artno: "5265813"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画同一银行同一年度内, 媒体报道把该行金科合作行为定性为「自主研发」与定性为「外部协同」两类子样本之间的媒体语调落差, 是 Chesbrough (2003) 开放式创新框架 (自主研发内向型 vs. 外部协同开放型) 与银行金科报道语调测度的交叉产物。变量名 cm 取自 collab_mode (合作模式) 缩写, indep/collab 分别对应「自主研发」「外部协同」两个互斥类目。构念动机: 若媒体对银行「自主研发」路线的报道语调系统性高于 (或低于) 「外部协同」路线, 该差值即捕捉了市场/媒体叙事对两种创新战略选择的相对评价倾向, 可作为战略选择的媒体反馈信号, 呼应 Laursen & Salter (2006) 关于开放度与创新绩效关系的经典发现——媒体语调落差本质上是对"开放"与"封闭"两条路径孰优孰劣这一命题的舆论侧量化。分类原语来自 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票产出的 innovation_collab_mode 文章级标签 (自主研发/外部协同二分类, 与 F3/F4/F5 系列 locus/collab 分类维度同源), 语调原语是 llm_vote_tone (三家 LLM 多数投票共识语调, headline canonical 测度), 两者在 encode.py 面板构建阶段做对角线聚合 (`_aggregate_ctx_diagonal`) 后相减得到本家族。

【方法学与计算】
计算分两步。第一步, 对每个 (bank, year) 单元, 按 innovation_collab_mode 标签把该单元内的文章切成「自主研发」与「外部协同」两个互斥子集, 分别对该子集内文章的 llm_vote_tone 取均值, 得到 llm_vote_tone_indep_cm 与 llm_vote_tone_collab_cm 两个子指标 (同时副产 n_articles_indep_cm / n_articles_collab_cm 计数列以及分母配比 indep_frac_cm / collab_frac_cm——后两者不属本家族但共享同一次聚合调用, 分子分母同轨匹配以避免轨道不对称导致占比 >1 的已知缺陷, 见源码 2026-06-02 metric-audit 注记)。第二步, 两子指标相减: tone_gap = llm_vote_tone_indep_cm − llm_vote_tone_collab_cm。正值表示该行在「自主研发」叙事下的媒体语调更正面, 负值反之, 零表示两条战略路线的媒体评价无差异。最小样本门槛是本家族的关键质量控制: 只有当自主研发子集与外部协同子集各自的文章数都不少于 5 篇时才输出差值, 否则置 NaN, 目的是避免单篇甚至个位数样本的极端语调值伪装成有统计意义的战略路线差距 (源码注记明确标注为"补齐第 6 个 tone_gap 缺失的 min-n>=5 守门, 对齐其余 5 个同类 tone_gap 家族")。分类判定本身不对称: 银行侧类目判定走否定词+短名过滤口径, 金科侧走裸 AC (Aho-Corasick) 607 词表, 该口径不对称性由上游 innovation_collab_mode 分类器决定, 与本家族计算逻辑无关但影响子集划分的准入边界。

【文献定位】
本家族测度的理论根基是 Chesbrough (2003) 提出的开放式创新二分框架, 区分企业依赖内部研发资源 (closed/indep) 还是引入外部合作伙伴资源 (open/collab) 完成创新, 该框架在金融科技合作情境下被 Zhang et al. (2024, *Journal of Product Innovation Management*) 的近 20 年元分析进一步验证——开放式创新的绩效前因后果具有相当异质性, 媒体叙事很可能对不同开放度路线赋予不同的评价基调, 这正是本家族试图捕捉的信号。将媒体语调差异作为战略路线评价代理变量的做法, 呼应 Holzman, Miller & Twedt (2023, *The Accounting Review*) 关于媒体情感对企业行为具有约束/纪律作用的发现, 以及 Kueschnig & Schertler (2024, *Finance Research Letters*) 对金融机构金科并购 (外部协同的典型子类) 引发的股价语调反应的直接考察。就银行业金科战略而言, Hau et al. (2024, *The Journal of Finance*) 记录了金科信贷对企业成长的实证效应, 为「合作/自主」两条路径在产业层面的经济后果提供了背景, 本家族在媒体语调层面提供了对应的舆论侧微观测度, 与财务后果指标互补而非替代。 就本家族两条轨道所依赖的类目划分与合作侧构念, 近期文献可作补充锚定。Ferilli、Palmieri 与 Cicchiello (2026) 对 2015–2024 年 204 篇同行评议文献作结构化整合综述 (含定性内容编码与共被引/关键词文献计量), 识别出银行–金融科技合作研究的三大簇 (合作对银行绩效、效率与风险承担的影响; 监管套利与影子银行; 组织转型与商业模式重构), 并指出中国是「金科整合如何影响在位银行盈利、信贷配置与系统性风险」的主要经验基础, 从而为本家族 collab 类目在中国银行业的构念存在性与经济重要性提供综述级依据; 该文是文献综述而非实证研究, 分析单位是论文而非银行, 既不测量媒体语调亦无银行层合作变量, 与本家族按 innovation_collab_mode_ctx / innovation_collab_mode_ss 类目作对角线聚合再相减的测度构造无直接对应。Le、Ngo、Nguyen 与 Do (2024) 用越南银行 2007–2019 年样本 (系统 GMM) 自建跨七个金科细分领域的合作多样性指数, 发现合作多样性总体提升银行风险调整后收益, 但效应依金科细分领域与所有制而异 (比较型领域为正、支付与移动钱包领域为负, 国有大型与上市银行的正效应更明显), 说明 collab 一侧在银行层确属可测且对经营有实质后果的构念; 须注意其标题的 'friends or foes' 仅为修辞设问, 实证只含合作侧指标而未检验「合作 vs 竞争」二分, 且该文的「竞争」与本家族的 indep (自主研发) 不是同一构念, 不能据以主张「两种模式对银行含义不同」已有直接证据; 其单一国别 (越南) 样本、以风险调整后收益为 DV、由公司间合作事件构造合作变量, 与本家族的中国银行-年新闻语调差值、LLM 篇章分类口径均不同。Sun、Sun、Qiao 与 Zhang (2025) 以「自主创新 vs 协同创新」为并列的两条创新路径作对照分析, 佐证该二分在中国创新研究中是标准且可测的划分, 可作为 indep/collab 类目在中文语境下的近期构念参照; 但该文用专利与技术转移数据识别路径、对象是区域与企业的绿色创新、产出为创新绩效而非语调, 与本家族的银行主体与语调落差输出差距较大, 仅供构念对照。就「同一主体内两个来源的语调分开计算再作对照」这一构造思路, Jamshed、Oberoi 与 Lawal (2025) 的 SSRN 工作论文以同一份年报的 MD&A 与风险因素两节语调设问 'Speaking with One Voice?', 可作为该方向属活跃前沿的存在性提示; 惟该文尚未发表, 摘要在 Crossref/OpenAlex 均不可得且 Semantic Scholar 未收录, 无从证实其是否以「两者之差」为测度 ('joint information content' 亦可指联合或交互而非差分), 故本文档不主张其与本家族「两类目均值相减并加双侧 n≥5 门槛」的构造同型, 亦不作为已发表定论援引。
## VAR: tone_gap_indep_collab_cm_ctx

【变体差分】
本列使用 ctx 轨 (标题+实体窗口文本) 上的 innovation_collab_mode_ctx 分类标签与 llm_vote_tone_ctx 语调值计算差值, 是本家族的时间序上先落地的轨道 (源码 L2036–L2069, `_aggregate_ctx_diagonal` 默认 track 参数即 ctx)。子指标 n_articles_indep_cm_ctx / n_articles_collab_cm_ctx 的最小样本门槛 (各 ≥5 篇) 在 ctx 轨上独立核算, 分母来自 n_articles_llm_valid_ctx (ctx 轨留篇有效篇数), 分子分母同轨匹配, 避免与 full 轨或 ss 轨混用导致的占比失真。按项目「留篇门控=full-only」铁律 (2026-06-29), ctx 轨的行宇宙是 full 轨留篇集的子集 (`llm_verified_full==True` 决定"是否算一篇银行金科报道", ctx/ss 仅在此子集上补测), 因而 ctx 轨的 n_articles_llm_valid_ctx 与 min-n 门槛均建立在这一收缩后的样本上。ctx 与 ss 两轨之间, 以及与家族外的 full 轨同类测度之间, 均为各自 just-identified 并排的互为稳健性关系, 不分主次, 严禁在同一 over-identified Hansen J 检验中混用同一构念的多轨版本。使用者若只报告 ctx 轨结果, 应在稳健性附表中并列 ss 轨 (以及若存在的 full 轨同名列) 作为交叉验证, 而非把 ctx 轨当作凌驾于其余轨道之上的首选口径; 三轨之间的数值差异本身即含信息量——差异越小说明该行"自主研发 vs 外部协同"语调落差这一构念对文本窗口宽窄不敏感, 差异越大则提示窗口选择对结论有实质影响, 应在稳健性讨论中如实披露而非择优呈现。此外, ctx 轨的 min-n≥5 门槛与 innovation_collab_mode_ctx 标签质量共同决定缺失模式: 若某银行某年金科报道总量偏少, 即便报道全部命中分类, 也可能因单侧子集不足 5 篇而整格置 NaN, 这一缺失并非随机 (missing not at random), 使用者在做面板回归前应检视缺失是否与银行规模、金科业务活跃度等协变量相关, 必要时报告缺失敏感性检验。

## VAR: tone_gap_indep_collab_cm_ss

【变体差分】
本列使用 ss 轨 (标题+银行∧金科同句±N窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 上的 innovation_collab_mode_ss 与 llm_vote_tone_ss 计算差值, 源码位置紧随 ctx 轨块之后 (L2070 起, 注记明确写作"_ss 轨对角线追加, 镜像 ctx _cm 块, 三轨 full/ctx/ss"), 计算逻辑与 ctx 轨完全对称: 同样的 `_aggregate_ctx_diagonal` 调用 (显式传入 `track='_ss'`)、同样的 indep/collab 二分、同样的分子分母同轨匹配 (分母为 n_articles_llm_valid_ss)、同样的 min-n≥5 双侧门槛。ss 轨相对 ctx 轨的核心差异在于共现判据更严格: ctx 轨采用"银行实体窗口内"的宽松邻近口径, ss 轨要求银行与金科词汇同句共现, 因而 ss 轨样本天然更稀疏, min-n≥5 门槛在此轨上更容易触发 NaN 置空, 这是稀疏性与测量精度之间的权衡而非缺陷。ss 轨的回退语义镜像 ctx 轨: 若某单元内无银行∧金科同句共现的文章, 该文章的 content_ss 退化为全文 body 且 ss_is_fallback 标记为真, 分母 n_articles 与 ctx 轨共享同一套核算口径。ss 轨与 ctx 轨、以及族外 full 轨同构念版本三者互为稳健性并排, 各自 just-identified, 不设主次排序, 亦不得混入同一 over-identified Hansen J 检验。由于同句共现判据比 ctx 轨的实体窗口判据更保守, ss 轨样本量系统性小于 ctx 轨, 二者的缺失模式并不重合: 存在 ctx 轨可出值而 ss 轨因样本不足置 NaN 的单元, 反之则极少 (ss 轨判据是 ctx 轨判据的严格子集, 理论上 ss 轨样本恒 ≤ ctx 轨样本)。这意味着 ss 轨天然是"高精度小样本"版本, 适合作精确度优先的稳健性核验, 而 ctx 轨适合作覆盖率优先的主力测度; 二者搭配使用能同时兼顾统计功效与测量噪声控制。使用者在解释 ss 轨结果时应留意: 当某单元 ss 轨可出值而 ctx 轨恰好因分类边界差异未通过门槛 (理论上少见但不排除, 因两轨分类标签虽同名 innovation_collab_mode 但基于不同文本窗口独立由 LLM 判定, 并非同一次判定的简单子集), 该单元的 ss 轨结果应被视为独立观测而非 ctx 轨的补充插补, 不应做任何跨轨插值或平均处理。

<!-- rendered-citations:begin -->
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793–815. https://doi.org/10.1111/jpim.12710
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309–3359. https://doi.org/10.1111/jofi.13384
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315–345. https://doi.org/10.2308/TAR-2020-0104
Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. Finance Research Letters, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131–150. https://doi.org/10.1002/smj.507
Ferilli, G. B., Palmieri, E., & Cicchiello, A. F. (2026). Bank–FinTech cooperation: what the empirical evidence reveals in Asia–Pacific countries. International Journal of Emerging Markets, 1-26. https://doi.org/10.1108/ijoem-01-2026-0159
Le, T., Ngo, T., Nguyen, D. T., & Do, T. T. (2024). Fintech and banking: friends or foes? Evidence from bank–fintech cooperation. International Journal of Bank Marketing, 42(7), 1513-1535. https://doi.org/10.1108/ijbm-09-2023-0525
Sun, Z., Sun, Y., Qiao, Q., & Zhang, P. (2025). Independent innovation and collaborative innovation: exploring the impact of digital technology transfer on green innovation from the perspective of innovation element flow. Environment, Development and Sustainability. https://doi.org/10.1007/s10668-025-07107-1
Jamshed, A., Oberoi, J. S., & Lawal, T. O. (2025). Speaking with One Voice? The Joint Information Content of Tone in MD&A and Risk Factor Disclosures. SSRN No. 5265813 [Working Paper]. https://doi.org/10.2139/ssrn.5265813
<!-- rendered-citations:end -->
